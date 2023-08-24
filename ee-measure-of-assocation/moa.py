from itertools import combinations
import os
import matplotlib.pyplot as plt
import pandas as pd


class MOATable(pd.DataFrame):
    @classmethod
    def from_csv(cls, path: str, **kwargs):
        """Creates a MOATable from a csv file"""
        return cls(pd.read_csv(path, **kwargs))

    def __init__(self, df: pd.DataFrame):
        super().__init__(df)

    @property
    def labels(self) -> list:
        """returns the labels"""
        return list(set(self["label"]))

    @property
    def predictors(self) -> list:
        """returns the predictors"""
        return list(set(self["predictor"]))

    def get_by_rank(self, rank: int) -> pd.DataFrame:
        """returns the table by rank"""
        return self[self["rank"] == rank]

    def get_by_label(self, label: str) -> pd.DataFrame:
        """returns the table by label"""
        return self[self["label"] == label]

    def get_by_predictor(self, predictor: str) -> pd.DataFrame:
        """returns the table by predictor"""
        return self[self["predictor"] == predictor]

    def get_by_ranks(self, lower: int, upper: int) -> pd.DataFrame:
        """returns the table by rank range"""
        return self[(self["rank"] >= lower) & (self["rank"] <= upper)]


class MOAPlotter:
    def __init__(self, tabel: MOATable, rank: int = 3):
        self.table = tabel
        self.rank = rank

    def plot(self, out_dir: str = None):
        out_dir = out_dir or "moa_plots" if out_dir is None else out_dir

        ranked = self.table.get_by_rank(self.rank)
        pass


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
        data = {"label": [], "versus": [], "predictor": [], "score": []}
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
            data["label"].append(combo[0])
            data["versus"].append(combo[1])
            data["predictor"].append(col)
            data["score"].append(score)
        df_out = pd.DataFrame(data)
        df_out = df_out.sort_values(by="score", ascending=False).reset_index(drop=True)
        df_out["rank"] = list(range(1, len(df_out) + 1))
        data_frames.append(df_out)

    df_out = pd.concat(data_frames)
    return MOATable(df_out)


def plot_scores(
    sample: pd.DataFrame, moa_table: MOATable, out_dir: str = None, ranks: int = 3
) -> None:
    out_dir = "data/plots" if out_dir is None else out_dir
    df = sample.copy()
    ranked = moa_table.get_by_ranks(1, ranks)

    for _, row in ranked.iterrows():
        # print(row)
        # Sample data for two classes
        label = df[(df["class_name"] == row["label"])][row["predictor"]]
        versus = df[(df["class_name"] == row["versus"])][row["predictor"]]

        # Plot histogram
        plt.hist(label, bins=100, alpha=0.5, label=row["label"])
        plt.hist(versus, bins=100, alpha=0.5, label=row["versus"])
        plt.legend(loc="upper right")

        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title(f'{row["predictor"]} for {row["label"]} vs {row["versus"]}')

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        filename = f'{row["label"]}-vs-{row["versus"]}-{row["predictor"]}.png'
        plt.savefig(os.path.join(out_dir, filename))

        plt.clf()

    return None
