from itertools import combinations
import pandas as pd


class MoaCalculator:
    def __init__(self, label_series: pd.Series, versus_series: pd.Series):
        self.label_series = label_series
        self.versus_series = versus_series

    def calculate(self):
        """Calculates the MOA score"""
        label_mean = self.label_series.mean()
        versus_mean = self.versus_series.mean()
        cat = pd.concat([self.label_series, self.versus_series])
        std = cat.std()
        score = abs(label_mean - versus_mean) / std
        return score


class MoaTable:
    def __init__(self, data: dict):
        self.table = pd.DataFrame(data)

    def rank(self):
        self.table["rank"] = self.table.groupby(["label", "versus"])["score"].rank(
            ascending=False
        )
        return self


class MoaScores:
    def __init__(self, table):
        self.table = self._sort_data_frame(table, ["rank", "label", "versus"])

    @staticmethod
    def _sort_data_frame(df: pd.DataFrame, col: list[str]):
        return df.sort_values(by=col, ascending=True).reset_index(drop=True)

    def get_by_rank(self, rank: int):
        return self.table[self.table["rank"] == rank]

    def get_by_ranks(self, lower: int, upper: int) -> pd.DataFrame:
        """returns the table by rank range"""
        return self.table[(self.table["rank"] >= lower) & (self.table["rank"] <= upper)]

    def to_csv(self, path: str) -> None:
        self.table.to_csv(path, index=False)
        return None


class MoaScoreGenerator:
    def __init__(self, sampled_data: pd.DataFrame, label_col: str):
        self.sampled_data = sampled_data
        self.label_col = label_col
        self._cols_2_skip = ["system:index", "isTraining", ".geo", self.label_col]

    @property
    def cols_2_skip(self):
        return self._cols_2_skip

    def add_cols_2_skip(self, cols: list[str]):
        self._cols_2_skip.extend(cols)
        return None

    def generate_scores(self) -> MoaScores:
        labels = self.sampled_data[self.label_col].unique().tolist()
        combos = combinations(labels, 2)

        moa_tables = []

        for combo in combos:
            dfc = self.sampled_data.copy()
            dfc = dfc[
                (dfc[self.label_col] == combo[0]) | (dfc[self.label_col] == combo[1])
            ]
            table_data = {"label": [], "versus": [], "predictor": [], "score": []}
            for col in dfc.columns:
                if col in self.cols_2_skip:
                    continue
                dfc1 = dfc[dfc[self.label_col] == combo[0]][col]
                dfc2 = dfc[dfc[self.label_col] == combo[1]][col]

                moa = MoaCalculator(dfc1, dfc2)

                table_data["label"].append(combo[0])
                table_data["versus"].append(combo[1])
                table_data["predictor"].append(col)
                table_data["score"].append(moa.calculate())

            moa_table = MoaTable(table_data)
            moa_table.rank()
            moa_tables.append(moa_table.table)

        return MoaScores(pd.concat(moa_tables))
