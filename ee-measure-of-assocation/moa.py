from itertools import combinations
import os
import matplotlib.pyplot as plt
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


class MoaPlot:
    def __init__(self, title, x_label, y_label):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.fig, self.ax = plt.subplots()

    def add_histogram(
        self,
        data,
        label=None,
        bin=100,
        alpha=0.5,
    ):
        self.ax.hist(data, bins=bin, alpha=alpha, label=label)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_title(self.title)
        self.ax.legend()

    def show(self):
        plt.show()

    def save(self, path):
        self.fig.savefig(path)


def moa_scores(df, label_col, colums_to_skip: list[str] = None):
    cols_2_skip = ["system:index", "isTraining", ".geo"]

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
