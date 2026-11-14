"""Prolongation du régime espace à lecture retardée jusqu'à 100 000 pas.

    python experiments/moteurs_lecteurs/prolongation.py    # écrit out/prolongation.png

Mêmes populations que run.py (même graine, donc mêmes 20 000 premiers pas).
Hypothèse 6 : journal/2026-11-15_moteurs-lecteurs.md.
"""

from __future__ import annotations

import argparse
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from run import REGIMES, TARGET, motifs, one_population

from simsbn.suivi import MEASURES
from simsbn.viz import INK, apply_style

REGIME = "espace retardé"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--steps", type=int, default=100_000)
    parser.add_argument("--rep", type=int, default=24)
    parser.add_argument("--every", type=int, default=500, help="pas entre deux relevés")
    parser.add_argument("--last", type=int, default=10_000, help="fenêtre finale de la mesure")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    tasks = [(REGIME, r, 300, args.steps, 0.1, args.every, args.seed) for r in range(args.rep)]
    series = np.full((len(MEASURES), args.rep, args.steps // args.every + 1), np.nan)
    finals = [None] * args.rep
    with Pool(args.jobs) as pool:
        for _, r, one, population in pool.imap_unordered(one_population, tasks):
            series[:, r] = one
            finals[r] = population

    dep = 100 * series[MEASURES.index("dependance")]
    size = series[MEASURES.index("effectif")]
    t = args.every * np.arange(dep.shape[1])
    window = t > args.steps - args.last
    last = np.nanmean(dep[:, window], axis=1)
    at_20k = np.nanmean(dep[:, (t > 10_000) & (t <= 20_000)], axis=1)
    print(f"dépendance, pas 10 001 à 20 000 : {at_20k.mean():.1f} ± {at_20k.std():.1f} points")
    print(
        f"dépendance, {args.last} derniers pas : {last.mean():.1f} ± {last.std():.1f} points ; "
        f"{int((last > 40).sum())}/{args.rep} populations au-dessus de +40"
    )
    print("par population :", np.round(np.sort(last)).astype(int).tolist())
    for label, lo, hi in (
        ("pas 10 001 à 20 000", 10_000, 20_000),
        ("fin", args.steps - args.last, args.steps),
    ):
        n = np.nanmean(size[:, (t > lo) & (t <= hi)], axis=1)
        print(f"effectif, {label} : {n.mean():.1f} ± {n.std():.1f}")
    print(f"extinctions : {sum(len(p) == 0 for p in finals)}/{args.rep}")
    tallies = motifs(finals)
    share = np.array([tally.get(TARGET, 0) for tally in tallies])
    major = int((share > 0.5).sum())
    print(
        f"motif « {TARGET[0]}, {TARGET[1]} » à la fin : {100 * share.mean():.1f} % des agents, "
        f"majoritaire dans {major}/{args.rep} populations"
    )

    import matplotlib.pyplot as plt

    apply_style()
    color = REGIMES[REGIME][2]
    fig, ax = plt.subplots(figsize=(9, 4.6), layout="constrained")
    for row in dep:
        ax.plot(t, row, color=color, linewidth=0.7, alpha=0.3)
    mean = np.nanmean(dep[:, 1:], axis=0)  # le relevé du pas 0 n'a pas de comportement
    ax.plot(t[1:], mean, color=color, linewidth=2.2, label="moyenne des 24 populations")
    ax.axhline(0, color=INK, linewidth=0.8)
    ax.axvline(
        20_000, color=INK, linewidth=1, linestyle=(0, (4, 3)), label="fin du premier lancement"
    )
    ax.set_xlabel("pas")
    ax.set_ylabel("points de %")
    ax.set_title(
        "Lecture retardée, régime espace : dépendance au contexte, une ligne par population"
    )
    ax.legend(loc="lower right")
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "prolongation.png", dpi=160)
    np.savez_compressed(out / "prolongation.npz", pas=t, dependance=dep, effectif=size)
    print(f"figure : {out / 'prolongation.png'}")


if __name__ == "__main__":
    main()
