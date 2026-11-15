"""Calculs et figure complémentaires, depuis out/saisons.csv (après run.py).

Les fenêtres de relevé (20 pas) sont alignées sur les saisons : chaque fenêtre est soit
d'été, soit d'hiver, donc l'économie d'hiver (définie au journal) ne se calcule pas par
fenêtre mais par année : moyenne des fenêtres d'été moins fenêtre d'hiver.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from simsbn.stats import format_p, permutation_test
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

OUT = Path(__file__).parent / "out"
YEAR, SUMMER = 100, 80
COLORS = {"saisons": ORANGE, "sans saisons": BLUE, "neutre à saisons": MUTED}


def main():
    d = pd.read_csv(OUT / "saisons.csv")
    d["year"] = (d.step - 1) // YEAR  # une fenêtre porte le numéro de son dernier pas
    d["winter"] = d.step % YEAR == 0
    second = d[d.step >= d.step.max() // 2]
    per_pop = {}
    for regime in ("saisons", "neutre à saisons"):
        g = second[(second.regime == regime) & (second.step > 0)]
        m = g.groupby(["replicate", "winter"])[["manger_0", "bouger_0"]].mean()
        eat = g.groupby(["replicate", "winter"])["manger_ete"].mean().unstack()
        winter_eat = g.groupby(["replicate", "winter"])["manger_hiver"].mean().unstack()
        move = g.groupby(["replicate", "winter"])["bouger_ete"].mean().unstack()
        move_w = g.groupby(["replicate", "winter"])["bouger_hiver"].mean().unstack()
        per_pop[regime] = (
            (eat[False] - winter_eat[True]).to_numpy(),
            (move_w[True] - move[False]).to_numpy(),
        )
        del m
        print(
            f"{regime:18} économie d'hiver {100 * per_pop[regime][0].mean():6.2f} ± "
            f"{100 * per_pop[regime][0].std():.2f} points ; "
            f"bouger hiver - été {100 * per_pop[regime][1].mean():6.2f} ± "
            f"{100 * per_pop[regime][1].std():.2f} points"
        )
    rng = np.random.default_rng([0, 556])
    for i, name in enumerate(("économie d'hiver", "bouger hiver - été")):
        p = permutation_test(per_pop["saisons"][i], per_pop["neutre à saisons"][i], rng)
        print(f"{name} : saisons contre neutre, p = {format_p(p)}")

    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    for regime, color in COLORS.items():
        g = d[(d.regime == regime) & (d.step > 0)]
        end_summer = g[g.step % YEAR == SUMMER].groupby("step").effectif.mean()
        end_winter = g[g.step % YEAR == 0].groupby("step").effectif.mean()
        axes[0].plot(end_summer.index, end_summer, color=color, linewidth=2, label=regime)
        axes[0].plot(end_winter.index, end_winter, color=color, linewidth=1, linestyle="--")
    axes[0].set_title("Effectif en fin d'été (plein) et en fin d'hiver (tirets)")
    axes[0].set_ylabel("agents vivants")
    axes[0].set_xlabel("pas")
    for regime in ("saisons", "neutre à saisons"):
        g = d[(d.regime == regime) & (d.step > 0)]
        a = g[~g.winter].groupby(["replicate", "year"]).manger_ete.mean()
        b = g[g.winter].groupby(["replicate", "year"]).manger_hiver.mean()
        econ = (100 * (a - b)).groupby("year").mean().dropna()
        axes[1].plot(econ.index * YEAR, econ, color=COLORS[regime], linewidth=2, label=regime)
    axes[1].axhline(0, color=INK, linewidth=0.8)
    axes[1].set_title("Économie d'hiver : P(ingérer, été) - P(ingérer, hiver)")
    axes[1].set_ylabel("points")
    axes[1].set_xlabel("pas")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="outside lower center", ncol=3)
    fig.savefig(OUT / "saisons_complement.png", dpi=160)


if __name__ == "__main__":
    main()
