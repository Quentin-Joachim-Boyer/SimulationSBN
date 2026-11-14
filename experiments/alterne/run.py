"""Environnement alterné contre environnement fixe : qui devient pluripotent ?

    python experiments/alterne/run.py        # écrit experiments/alterne/out/alterne.png

Protocole et hypothèse : journal/2026-11-14_environnement-alterne.md.
"""

from __future__ import annotations

import argparse
import csv
from itertools import product
from math import prod
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from simsbn import (
    batch_dynamics,
    control_nodes,
    is_psbn,
    null_distribution,
    sbf_counts,
    sbf_tables,
    weight_bound,
    wright_fisher,
)
from simsbn.tasks import Context, score
from simsbn.viz import BLUE, INK, ORANGE, apply_style

D, MOTOR = 3, 2
STEPS = range(2, 7)
CONTEXT_A = Context(start=0b010, target=dict.fromkeys(STEPS, 1))  # stimulus seul
CONTEXT_B = Context(start=0b011, target=dict.fromkeys(STEPS, 0))  # stimulus et contexte
REGIMES = {"alterné": BLUE, "fixe": ORANGE}
MEASURES = ["psbn", "controle", "score_A", "score_B"]


def simulate(regime, pop_size, generations, replicates, mutation_rate, strength, period, seed):
    """Séries ``(mesure, réplicat, génération)`` pour un régime."""
    kinds: dict[tuple[int, ...], tuple[bool, bool]] = {}
    series = np.zeros((len(MEASURES), replicates, generations + 1))
    bound = weight_bound(D)

    def fitness(population, generation):
        in_b = regime == "alterné" and (generation // period) % 2 == 1
        return np.exp(strength * score(population, CONTEXT_B if in_b else CONTEXT_A, MOTOR))

    for r in range(replicates):
        rng = np.random.default_rng([seed, r, regime == "fixe"])
        start = rng.integers(-bound, bound + 1, size=(pop_size, D, D))
        runs = wright_fisher(start, generations, rng, mutation_rate, fitness)
        for g, population, _ in runs:
            flags = []
            for f in map(tuple, batch_dynamics(population).tolist()):
                if f not in kinds:
                    kinds[f] = (is_psbn(f), bool(control_nodes(f)))
                flags.append(kinds[f])
            series[0, r, g], series[1, r, g] = np.mean(flags, axis=0)
            series[2, r, g] = score(population, CONTEXT_A, MOTOR).mean()
            series[3, r, g] = score(population, CONTEXT_B, MOTOR).mean()
    return series


def exact_counts():
    """Parts exactes de génotypes pluripotents parmi les solutions parfaites."""
    counts, tables = sbf_counts(D), sbf_tables(D)
    rows = {"A seul": [0, 0, 0], "A et B": [0, 0, 0]}  # génotypes, PSBN, nœud de contrôle
    for f in product(counts, repeat=D):
        W = np.array([tables[t] for t in f]).T[None]
        if score(W, CONTEXT_A, MOTOR)[0] < 1:
            continue
        genotypes = prod(counts[t] for t in f)
        keys = ["A seul"] + (["A et B"] if score(W, CONTEXT_B, MOTOR)[0] == 1 else [])
        for key in keys:
            rows[key][0] += genotypes
            rows[key][1] += genotypes * is_psbn(f)
            rows[key][2] += genotypes * bool(control_nodes(f))
    return rows


def plot(results, null, path, pop_size, replicates):
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), layout="constrained", sharex=True)
    titles = [
        "Part de PSBN",
        "Part de dynamiques à nœud de contrôle",
        "Score moyen dans le contexte A (moteur allumé)",
        "Score moyen dans le contexte B (moteur éteint)",
    ]
    for k, (ax, title) in enumerate(zip(axes.flat, titles, strict=True)):
        scale = 100 if k < 2 else 1
        for regime, color in REGIMES.items():
            data = scale * results[regime][k]
            generations = np.arange(data.shape[1])
            for row in data:
                ax.plot(generations, row, color=color, linewidth=0.6, alpha=0.15)
            ax.plot(generations, data.mean(axis=0), color=color, linewidth=2, label=regime)
        if k < 2:
            ax.axhline(
                100 * null[k],
                color=INK,
                linewidth=1,
                linestyle=(0, (4, 3)),
                label="modèle nul exact",
            )
            ax.set_ylabel("% de la population")
            ax.set_ylim(bottom=0)
        else:
            ax.set_ylim(0, 1.02)
            ax.set_xlabel("génération")
        ax.set_title(title)
    axes[0, 0].legend(loc="upper right", ncols=3)
    fig.suptitle(
        f"Dimension {D} — {replicates} populations de {pop_size} individus par régime, "
        "moyenne en trait épais",
        x=0.01, ha="left", color=INK, fontsize=12,
    )  # fmt: skip
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pop", type=int, default=300)
    parser.add_argument("--gen", type=int, default=600)
    parser.add_argument("--rep", type=int, default=12)
    parser.add_argument("--mu", type=float, default=0.1, help="mutations par individu")
    parser.add_argument("--strength", type=float, default=5.0, help="fitness = exp(s × score)")
    parser.add_argument("--period", type=int, default=5, help="générations par contexte")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    results = {
        regime: simulate(regime, args.pop, args.gen, args.rep, args.mu, args.strength,
                         args.period, args.seed)
        for regime in REGIMES
    }  # fmt: skip
    null = (
        null_distribution(D, is_psbn)[True],
        null_distribution(D, lambda f: bool(control_nodes(f)))[True],
    )
    with open(out / "alterne.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "generation", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for g in range(args.gen + 1):
                    writer.writerow([regime, r, g, *series[:, r, g].round(5)])
    plot(results, null, out / "alterne.png", args.pop, args.rep)

    half = args.gen // 2 + 1
    print(f"{'':28}{'PSBN':>8}{'contrôle':>10}{'score A':>9}{'score B':>9}")
    print(f"{'modèle nul exact':28}{100 * null[0]:7.2f}%{100 * null[1]:9.2f}%")
    for regime, series in results.items():
        m = series[:, :, half:].mean(axis=(1, 2))
        label = f"simulation, régime {regime}"
        print(f"{label:28}{100 * m[0]:7.2f}%{100 * m[1]:9.2f}%{m[2]:9.2f}{m[3]:9.2f}")
    for key, (genotypes, psbn, control) in exact_counts().items():
        label = f"génotypes parfaits, {key}"
        print(f"{label:28}{100 * psbn / genotypes:7.2f}%{100 * control / genotypes:9.2f}%"
              f"   ({genotypes} génotypes)")  # fmt: skip
    print(f"figure : {out / 'alterne.png'}")


if __name__ == "__main__":
    main()
