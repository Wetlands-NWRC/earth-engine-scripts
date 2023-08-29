import os

import matplotlib.pyplot as plt
import pandas as pd


def plot_predictors(
    samples: pd.DataFrame, label_col: str, ranks: pd.DataFrame, out_dir: str = None
):
    out_dir = "./data/plots/" if out_dir is None else out_dir

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for _, row in ranks.iterrows():
        # isolate the data series we want to use
        label = samples[samples[label_col] == row["label"]][row["predictor"]]
        versus = samples[samples[label_col] == row["versus"]][row["predictor"]]

        # create the plot objects
        title = (
            f"{row['label']} vs {row['versus']} {row['predictor']} rank {row['rank']}"
        )

        # Plot histogram
        plt.hist(label, bins=100, alpha=0.5, label=row["label"])
        plt.hist(versus, bins=100, alpha=0.5, label=row["versus"])

        # set axis labels and title
        plt.legend(loc="upper right")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title(title)

        plt.savefig(os.path.join(out_dir, f"{'_'.join(title.split(' '))}.png"))
        plt.clf()
    plt.close()
    return None
