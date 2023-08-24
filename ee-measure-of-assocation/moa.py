from itertools import combinations


import pandas as pd


class MOATable:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @property
    def table(self) -> pd.DataFrame:
        """returns the table"""
        return self.df

    @property
    def labels(self) -> list:
        """returns the labels"""
        return list(set(self.df["label"]))

    @property
    def predictors(self) -> list:
        """returns the predictors"""
        return list(set(self.df["predictor"]))

    def __repr__(self):
        return self.df.__repr__()

    def __str__(self):
        return self.df.__str__()

    def get_by_rank(self, rank: int) -> pd.DataFrame:
        """returns the table by rank"""
        return self.df[self.df["rank"] == rank]

    def get_by_label(self, label: str) -> pd.DataFrame:
        """returns the table by label"""
        return self.df[self.df["label"] == label]

    def get_by_predictor(self, predictor: str) -> pd.DataFrame:
        """returns the table by predictor"""
        return self.df[self.df["predictor"] == predictor]

    def get_by_rank_range(self, lower: int, upper: int) -> pd.DataFrame:
        """returns the table by rank range"""
        return self.df[(self.df["rank"] >= lower) & (self.df["rank"] <= upper)]


# Steps
# 1. Create a table
# 2. Clean the column names
# 3.


def create_table(df, label_col):
    cols_2_keep = [
        i
        for i in df.columns
        if i not in [".geo", "system:index", "isTraining", "class_name"]
    ]
    cols_2_keep.insert(0, "class_name")

    df = df[cols_2_keep]

    labels = df[label_col].unique().tolist()

    data_frames = []
    for combo in combinations(labels, 2):
        dfin = df.copy()
        data = {"label": [], "predictor": [], "score": []}
        for col in dfin.columns:
            dfin = df[(df["class_name"] == combo[0]) | (df["class_name"] == combo[1])]
            if col == "class_name":
                continue
            dfc1 = dfin[dfin["class_name"] == combo[0]][col]
            dfc2 = dfin[dfin["class_name"] == combo[1]][col]
            c1_mean = dfc1.mean()
            c2_mean = dfc2.mean()
            cat = pd.concat([dfc1, dfc2])
            std = cat.std()
            score = abs(c1_mean - c2_mean) / std
            data["label"].append(f"{combo[0]}:{combo[1]}")
            data["predictor"].append(col)
            data["score"].append(score)
        df_out = pd.DataFrame(data)
        df_out = df_out.sort_values(by="score", ascending=False).reset_index(drop=True)
        df_out["rank"] = list(range(1, len(df_out) + 1))
        data_frames.append(df_out)

    df_out = pd.concat(data_frames)
    return MOATable(df_out)
