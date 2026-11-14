"""Évolution neutre : la simulation retrouve-t-elle le modèle nul exact ?

    python experiments/neutre/run.py            # écrit experiments/neutre/out/neutre.png

Des populations clonales (matrice nulle) évoluent sans sélection. La part d'individus
pluripotents doit converger vers la fréquence exacte des génotypes PSBN, et les
vecteurs de décomposition vers leur loi exacte.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from simsbn import batch_dynamics, decomposition, null_distribution, wright_fisher

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"


def simulate(d, pop_size, generations, replicates, mutation_rate, seed):
    """Retourne la part pluripotente, la diversité et les vecteurs de décomposition."""
    classes: dict[tuple[int, ...], tuple[int, ...]] = {}
    trivial = (1,) + (0,) * d
    pluripotent = np.zeros((replicates, generations + 1))
    diversity = np.zeros((replicates, generations + 1))
    late = Counter()  # vecteurs observés dans la seconde moitié des simulations
    for r in range(replicates):
        rng = np.random.default_rng([seed, r])
        start = np.zeros((pop_size, d, d), dtype=np.int64)
        for g, population, _ in wright_fisher(start, generations, rng, mutation_rate):
            dyn = [tuple(row) for row in batch_dynamics(population).tolist()]
            vectors = [classes[f] if f in classes else _classify(classes, f) for f in dyn]
            pluripotent[r, g] = sum(v != trivial for v in vectors) / pop_size
            diversity[r, g] = len(set(dyn))
            if g > generations // 2:
                late.update(vectors)
    return pluripotent, diversity, late


def _classify(classes, f):
    classes[f] = decomposition(f)
    return classes[f]


def plot(pluripotent, diversity, late, null, d, pop_size, path):
    trivial = (1,) + (0,) * d
    null_pluripotent = 1 - null[trivial]
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.edgecolor": GRID,
            "axes.labelcolor": MUTED,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    fig = plt.figure(figsize=(11, 7.6), facecolor=SURFACE, layout="constrained")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.25, 1])
    ax_p, ax_d, ax_v = (
        fig.add_subplot(grid[0, 0]),
        fig.add_subplot(grid[1, 0]),
        fig.add_subplot(grid[:, 1]),
    )
    generations = np.arange(pluripotent.shape[1])
    for ax in (ax_p, ax_d, ax_v):
        ax.set_facecolor(SURFACE)
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)

    for row in pluripotent:
        ax_p.plot(generations, 100 * row, color=BLUE, linewidth=0.7, alpha=0.25)
    ax_p.plot(generations, 100 * pluripotent.mean(axis=0), color=BLUE, linewidth=2)
    ax_p.axhline(100 * null_pluripotent, color=INK, linewidth=1, linestyle=(0, (4, 3)))
    ax_p.annotate(
        f"modèle nul exact : {100 * null_pluripotent:.2f} %".replace(".", ","),
        (generations[-1], 100 * null_pluripotent),
        xytext=(0, 60),
        textcoords="offset points",
        ha="right",
        color=INK,
        arrowprops={"arrowstyle": "-", "color": INK, "linewidth": 0.8},
        bbox={"facecolor": SURFACE, "edgecolor": "none", "pad": 2},
    )
    ax_p.set_title("Part d'individus pluripotents (PSBN)", loc="left", color=INK, fontweight="bold")
    ax_p.set_ylabel("% de la population")
    ax_p.set_ylim(bottom=0)

    for row in diversity:
        ax_d.plot(generations, row, color=BLUE, linewidth=0.7, alpha=0.25)
    ax_d.plot(generations, diversity.mean(axis=0), color=BLUE, linewidth=2)
    ax_d.set_title(
        "Dynamiques distinctes dans la population", loc="left", color=INK, fontweight="bold"
    )
    ax_d.set_xlabel("génération")
    ax_d.set_ylabel(f"nombre (sur {pop_size} individus)")
    ax_d.set_ylim(bottom=0)

    vectors = sorted((v for v in null if v != trivial), key=lambda v: null[v])
    total = sum(late.values())
    y = np.arange(len(vectors))
    exact = [100 * null[v] for v in vectors]
    seen = [100 * late[v] / total for v in vectors]
    for yi, a, b in zip(y, exact, seen, strict=True):
        if b > 0:
            ax_v.plot([a, b], [yi, yi], color=GRID, linewidth=2, zorder=1)
    ax_v.scatter(
        exact,
        y,
        s=70,
        facecolor=SURFACE,
        edgecolor=INK,
        linewidth=1.5,
        zorder=2,
        label="modèle nul exact",
    )
    shown = [(b, yi) for b, yi in zip(seen, y, strict=True) if b > 0]
    ax_v.scatter(
        *zip(*shown, strict=True), s=28, color=ORANGE, zorder=3, label="simulation (seconde moitié)"
    )
    ax_v.set_xscale("log")
    ax_v.set_yticks(y, ["⟨" + ", ".join(map(str, v)) + "⟩" for v in vectors])
    ax_v.set_xlabel("% des individus (échelle logarithmique)")
    ax_v.set_title("Vecteurs de décomposition", loc="left", color=INK, fontweight="bold")
    ax_v.legend(loc="upper left", frameon=False, labelcolor=MUTED)

    replicates = pluripotent.shape[0]
    fig.suptitle(
        f"Évolution neutre en dimension {d} — {replicates} populations de {pop_size} "
        "individus, moyenne en trait épais",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=12,
    )
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--d", type=int, default=3)
    parser.add_argument("--pop", type=int, default=300)
    parser.add_argument("--gen", type=int, default=600)
    parser.add_argument("--rep", type=int, default=12)
    parser.add_argument("--mu", type=float, default=0.3, help="mutations par individu")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    pluripotent, diversity, late = simulate(
        args.d, args.pop, args.gen, args.rep, args.mu, args.seed
    )
    null = null_distribution(args.d, decomposition)
    with open(out / "neutre.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["replicate", "generation", "pluripotent_fraction", "distinct_dynamics"])
        for r in range(args.rep):
            for g in range(args.gen + 1):
                writer.writerow([r, g, pluripotent[r, g], int(diversity[r, g])])
    plot(pluripotent, diversity, late, null, args.d, args.pop, out / "neutre.png")
    trivial = (1,) + (0,) * args.d
    half = args.gen // 2
    print(f"modèle nul exact : {100 * (1 - null[trivial]):.2f} % de pluripotents")
    print(f"simulation       : {100 * pluripotent[:, half + 1 :].mean():.2f} %")
    print(f"figure : {out / 'neutre.png'}")


if __name__ == "__main__":
    main()
