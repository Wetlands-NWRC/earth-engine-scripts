import os

import matplotlib.pyplot as plt
import pandas as pd


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


class MOAPlotGenerator:
    def __init__(self, samples: pd.DataFrame, scores: pd.DataFrame):
        self.samples = samples
        self.scores = scores
        self.plotter = MoaPlot

    def generate_plots(self, out_dir: str = None, ranks: int = 3):
        for _, rows in self.scores.iterrows():
            input_scores = None
            label = rows["label"]
            versus = rows["versus"]
            predictor = rows["predictor"]
            rank = rows["rank"]
            if rank > ranks:
                continue
            dfc1 = self.samples[self.samples["label"] == label][predictor]
            dfc2 = self.samples[self.samples["label"] == versus][predictor]
            title = f"{label} vs {versus} {predictor} rank {rank}"
            plot = self.plotter(title, predictor, "frequency")
            plot.add_histogram(dfc1, label=label)
            plot.add_histogram(dfc2, label=versus)
            if out_dir is not None:
                plot.save(os.path.join(out_dir, f"{title}.png"))
            else:
                plot.show()
