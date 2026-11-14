"""Agents entrée / cerveau / moteur 1/3/1, en environnement fixe ou alterné.

    python experiments/cerveau_131/run.py    # écrit experiments/cerveau_131/out/cerveau_131.png

Protocole et hypothèses : journal/2026-11-14_cerveau-131.md.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from simsbn import batch_dynamics, decomposition, split_is_sbn, wright_fisher
from simsbn.agents import Architecture
from simsbn.tasks import Context, score
from simsbn.viz import BLUE, ORANGE, regime_panels

ARCH = Architecture(n_in=1, n_brain=3, n_out=1)
MOTOR = ARCH.outputs[0]
BOUND = 3
STEPS = range(3, 9)
START_A = ARCH.state(inputs=0, brain=0b001)
START_B = ARCH.state(inputs=1, brain=0b001)
# Contexte A : oscillation de période 2, dans l'une ou l'autre phase.
OSCILLATIONS = [Context(START_A, {t: (t + phase) % 2 for t in STEPS}) for phase in (0, 1)]
STEADY = Context(START_B, dict.fromkeys(STEPS, 1))  # contexte B : moteur allumé
REGIMES = {"alterné": BLUE, "fixe": ORANGE}
MEASURES = ["scission_sbn", "controle_interne", "score_A", "score_B"]
TITLES = [
    "Part d'agents dont la face « entrée = 1 » est un SBN",
    "Part d'agents à contrôle interne (plus de 2 feuilles PTBN)",
    "Score moyen dans le contexte A (moteur oscillant)",
    "Score moyen dans le contexte B (moteur allumé)",
]


def score_a(population):
    return np.maximum(*(score(population, c, MOTOR) for c in OSCILLATIONS))


def score_b(population):
    return score(population, STEADY, MOTOR)


class Classifier:
    """Mesures de pluripotence d'une population, mémorisées par dynamique."""

    def __init__(self):
        self.kinds: dict[tuple[int, ...], tuple[bool, bool]] = {}

    def __call__(self, population) -> np.ndarray:
        flags = []
        for f in map(tuple, batch_dynamics(population).tolist()):
            if f not in self.kinds:
                internal = sum(decomposition(f, "tbn")) > 2
                self.kinds[f] = (split_is_sbn(f, ARCH.inputs[0]), internal)
            flags.append(self.kinds[f])
        return np.mean(flags, axis=0)


def simulate(regime, classify, pop_size, generations, replicates, mutation_rate, strength,
             period, seed):  # fmt: skip
    series = np.zeros((len(MEASURES), replicates, generations + 1))
    finals = []

    def fitness(population, generation):
        in_b = regime == "alterné" and (generation // period) % 2 == 1
        return np.exp(strength * (score_b if in_b else score_a)(population))

    for r in range(replicates):
        rng = np.random.default_rng([seed, r, regime == "fixe"])
        start = ARCH.random(rng, pop_size, BOUND)
        runs = wright_fisher(
            start, generations, rng, mutation_rate, fitness, bound=BOUND, mask=ARCH.mask()
        )
        for g, population, _ in runs:
            series[:2, r, g] = classify(population)
            series[2, r, g] = score_a(population).mean()
            series[3, r, g] = score_b(population).mean()
        finals.append(population)
    return series, np.concatenate(finals)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pop", type=int, default=300)
    parser.add_argument("--gen", type=int, default=600)
    parser.add_argument("--rep", type=int, default=12)
    parser.add_argument("--mu", type=float, default=0.1, help="mutations par individu")
    parser.add_argument("--strength", type=float, default=5.0, help="fitness = exp(s × score)")
    parser.add_argument("--period", type=int, default=5, help="générations par contexte")
    parser.add_argument("--null", type=int, default=20_000, help="taille de l'échantillon nul")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    classify = Classifier()
    results, finals = {}, {}
    for regime in REGIMES:
        results[regime], finals[regime] = simulate(
            regime, classify, args.pop, args.gen, args.rep, args.mu, args.strength,
            args.period, args.seed,
        )  # fmt: skip
    sample = ARCH.random(np.random.default_rng([args.seed, 999]), args.null, BOUND)
    null = classify(sample)
    np.savez_compressed(out / "populations_finales.npz", **finals)
    with open(out / "cerveau_131.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "generation", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for g in range(args.gen + 1):
                    writer.writerow([regime, r, g, *series[:, r, g].round(5)])
    suptitle = (
        f"Agents 1/3/1 — {args.rep} populations de {args.pop} individus par régime, "
        "moyenne en trait épais"
    )
    regime_panels(results, TITLES, null, out / "cerveau_131.png", suptitle, REGIMES)

    half = args.gen // 2 + 1
    print(f"{'':28}{'scission':>9}{'interne':>9}{'score A':>9}{'score B':>9}")
    print(
        f"{'modèle nul (échantillon)':28}{100 * null[0]:8.2f}%{100 * null[1]:8.2f}%"
        f"{score_a(sample).mean():9.2f}{score_b(sample).mean():9.2f}"
    )
    for regime, series in results.items():
        m = series[:, :, half:].mean(axis=(1, 2))
        label = f"simulation, régime {regime}"
        print(f"{label:28}{100 * m[0]:8.2f}%{100 * m[1]:8.2f}%{m[2]:9.2f}{m[3]:9.2f}")
    print(f"figure : {out / 'cerveau_131.png'}")


if __name__ == "__main__":
    main()
