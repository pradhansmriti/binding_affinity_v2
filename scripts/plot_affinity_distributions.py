#!/usr/bin/env python3
"""Plot saved RF-Score predictions without changing the frozen evaluation."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path("runs/rfscore-fixed-100-3"))
    parser.add_argument("--output", type=Path, default=Path("outputs/affinity-distributions.png"))
    args = parser.parse_args()
    cohorts = []
    for name in ("train", "val", "test"):
        frames = [pd.read_csv(args.run / f"{name}-seed-{seed}.csv") for seed in range(3)]
        reference = frames[0]
        for frame in frames[1:]:
            if not reference[["id", "label_p_affinity"]].equals(frame[["id", "label_p_affinity"]]):
                raise ValueError(f"Inconsistent identifiers or labels in {name}")
        cohorts.append((name, reference["label_p_affinity"].to_numpy(),
                        np.stack([f["prediction_p_affinity"].to_numpy() for f in frames])))

    values = np.concatenate([np.concatenate((y, p.ravel())) for _, y, p in cohorts])
    lo, hi = np.floor(values.min()), np.ceil(values.max())
    grid = np.linspace(lo, hi, 600)
    bandwidth = 0.3  # p-affinity units, fixed across cohorts and seeds

    def density(data):
        return gaussian_kde(data, bw_method=bandwidth / np.std(data, ddof=1))(grid)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5), constrained_layout=True)
    for column, (name, labels, predictions) in enumerate(cohorts):
        ax = axes[0, column]
        ax.fill_between(grid, density(labels), color="#b9c4d1", alpha=0.65, label="Measured label")
        for seed, color in enumerate(("#126782", "#db7d28", "#8b5ca6")):
            ax.plot(grid, density(predictions[seed]), linewidth=1.5, color=color,
                    label=f"Prediction: seed {seed}")
        ax.set_title(f"{ {'train': 'Train', 'val': 'Validation', 'test': 'Test'}[name] } (n={len(labels):,})")
        ax.set(xlim=(lo, hi), xlabel="p-affinity", ylabel="Density")
        ax.grid(axis="y", alpha=0.2)
        if column == 0:
            ax.legend(fontsize=8, frameon=False)
        ax = axes[1, column]
        mean_prediction = predictions.mean(axis=0)
        ax.scatter(labels, mean_prediction, s=8, alpha=0.18, color="#126782", rasterized=True)
        ax.plot([lo, hi], [lo, hi], color="#bd562e", linestyle="--", linewidth=1.2)
        ax.set(xlim=(lo, hi), ylim=(lo, hi), xlabel="Measured label (p-affinity)",
               ylabel="Mean predicted p-affinity")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.2)
    fig.suptitle("RF-Score affinity predictions across internal cohorts", fontsize=16, fontweight="bold")
    fig.text(0.5, -0.01, "Top: Gaussian kernel density estimates (bandwidth 0.3 p-affinity). Bottom: mean of three seeds per complex; dashed line = perfect prediction.",
             ha="center", fontsize=9)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
