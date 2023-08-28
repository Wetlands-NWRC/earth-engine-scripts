from itertools import combinations
import pandas as pd


class MOACalculator:
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


class MOATable:
    def __init__(self, data: dict):
        self.table = pd.DataFrame(data)

    def rank(self):
        self.table["rank"] = self.table.groupby(["label", "versus"])["score"].rank(
            ascending=False
        )
        return self


def moa_scores(df, label_col, colums_to_skip: list[str] = None):
    cols_2_skip = ["system:index", "isTraining", ".geo", label_col]

    if colums_to_skip is not None:
        cols_2_skip.extend(colums_to_skip)

    # get labels
    labels = df[label_col].unique().tolist()

    # get all combinations of labels
    combos = combinations(labels, 2)

    moa_tables = []

    for combo in combos:
        dfc = df.copy()
        dfc = dfc[(dfc[label_col] == combo[0]) | (dfc[label_col] == combo[1])]
        table_data = {"label": [], "versus": [], "predictor": [], "score": []}
        for col in dfc.columns:
            if col in cols_2_skip:
                continue
            dfc1 = dfc[dfc[label_col] == combo[0]][col]
            dfc2 = dfc[dfc[label_col] == combo[1]][col]

            moa = MOACalculator(dfc1, dfc2)

            table_data["label"].append(combo[0])
            table_data["versus"].append(combo[1])
            table_data["predictor"].append(col)
            table_data["score"].append(moa.calculate())

        moa_table = MOATable(table_data)
        moa_table.rank()
        moa_tables.append(moa_table.table)

    return pd.concat(moa_tables)
