"""Moteurs lecteurs : les actions lues par des nœuds sans retour, avec ou sans délai.

    python experiments/moteurs_lecteurs/run.py    # écrit out/moteurs_lecteurs.png

Même monde que experiments/monde_dechet ; seule la lecture des actions change.
Protocole et hypothèses : journal/2026-11-15_moteurs-lecteurs.md.
"""

from __future__ import annotations

import argparse
import csv
import warnings
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simsbn.milieu import step_brains
from simsbn.monde import Corps, Monde, Vie, read_motors
from simsbn.stats import format_p, permutation_test
from simsbn.structure import KINDS, Classifier, exact_brain_kinds, exact_structural_parts
from simsbn.suivi import MEASURES, brains, par_population, suivre
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

HERE = Path(__file__).parent
BOUND = 3
ESPACE = Monde()  # paramètres figés dans journal/2026-11-14_monde-dechet.md
MOTORS = ("ingérer", "bouger")
REGIMES = {  # nom : (monde, corps, couleur, trait)
    "mélangé retardé": (ESPACE.melange(), Corps(MOTORS, delay=True), BLUE, "-"),
    "espace retardé": (ESPACE, Corps(MOTORS, delay=True), ORANGE, "-"),
    "mélangé immédiat": (ESPACE.melange(), Corps(MOTORS, delay=False), BLUE, (0, (4, 2))),
    "espace immédiat": (ESPACE, Corps(MOTORS, delay=False), ORANGE, (0, (4, 2))),
    "neutre": (replace(ESPACE, neutral=True), Corps(MOTORS, delay=True), MUTED, "-"),
}
SHOWN = ["effectif", "naissances", "bouger_0", "bouger_1", "dependance", "manger_0",
         "manger_1", "servies", "empoisonnees", *KINDS]  # fmt: skip
PANELS = [  # (mesure, titre, unité, indice du modèle nul uniforme ou None)
    ("effectif", "Effectif", "agents vivants", None),
    ("dependance", "Dépendance au contexte : P(bouger | 0) - P(bouger | 1)", "points de %", None),
    ("bouger_1", "P(bouger) quand le capteur valait 1", "%", None),
    ("controle_cerveau", "Cerveau seul : part à nœud de contrôle", "%", 0),
    ("psbn_cerveau", "Cerveau seul : part de PSBN", "%", 1),
    ("scission_sbn", "Part dont la face « capteur = 1 » est un SBN", "%", 2),
]
TARGET = ("allumé", "oscille")  # motif de déplacement : capteur 0, capteur 1
_classify = Classifier()  # un par processus


def one_population(task):
    regime, r, pop, steps, mu, every, seed = task
    monde, corps = REGIMES[regime][:2]
    rng = np.random.default_rng([seed, r, list(REGIMES).index(regime), 2])
    vie = Vie(corps.arch.random(rng, pop, BOUND), monde, rng, mu, BOUND, corps)
    return regime, r, suivre(vie, steps, every, _classify, ESPACE.cells), vie.population


def motif(W: np.ndarray, sensor: int) -> str:
    """Valeur du moteur « bouger » sur les attracteurs du cerveau, capteur tenu.

    On part des états du cerveau qui allument le moteur « ingérer ». « variable » : la
    réponse dépend de l'état de départ ; « sans ingestion » : aucun état ne l'allume.
    """
    eat, move = MOTORS.index("ingérer"), MOTORS.index("bouger")
    kinds = set()
    for start in range(8):
        brain = np.array([[(start >> i) & 1 for i in range(3)]])
        if not read_motors(W[None], brain)[0, eat]:
            continue
        seen = []
        while tuple(brain[0]) not in seen:
            seen.append(tuple(brain[0]))
            brain = step_brains(W[None], np.array([sensor]), brain)
        cycle = seen[seen.index(tuple(brain[0])) :]
        moves = {int(read_motors(W[None], np.array([state]))[0, move]) for state in cycle}
        kinds.add("oscille" if len(moves) == 2 else ("allumé" if moves == {1} else "éteint"))
    if not kinds:
        return "sans ingestion"
    return kinds.pop() if len(kinds) == 1 else "variable"


def motifs(populations) -> list[dict[tuple[str, str], float]]:
    """Pour chaque population, la part de ses agents qui porte chaque motif."""
    tallies = []
    for p in populations:
        tally: dict[tuple[str, str], float] = {}
        if len(p):
            genotypes, counts = np.unique(p.reshape(len(p), -1), axis=0, return_counts=True)
            for g, n in zip(genotypes, counts, strict=True):
                W = g.reshape(p.shape[1:])
                key = (motif(W, 0), motif(W, 1))
                tally[key] = tally.get(key, 0) + n / len(p)
        tallies.append(tally)
    return tallies


def figure(results, null, every, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    for ax, (measure, title, unit, null_index) in zip(axes.flat, PANELS, strict=True):
        m = MEASURES.index(measure)
        scale = 1 if measure == "effectif" else 100
        for regime, (_, _, color, dash) in REGIMES.items():
            data = scale * results[regime][m]
            t = every * np.arange(data.shape[1])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)  # relevé sans aucune valeur
                mean = np.nanmean(data, axis=0)
                low, high = np.nanpercentile(data, [25, 75], axis=0)
            ax.fill_between(t, low, high, color=color, alpha=0.08, linewidth=0)
            ax.plot(t, mean, color=color, linewidth=2, linestyle=dash, label=f"régime {regime}")
        if null_index is not None:
            ax.axhline(100 * null[null_index], color=INK, linewidth=1, linestyle=(0, (1, 2)),
                       label="loi uniforme")  # fmt: skip
        if measure == "dependance":
            ax.axhline(0, color=INK, linewidth=0.8)
        else:
            ax.set_ylim(bottom=0)
        ax.set_ylabel(unit)
        ax.set_title(title)
    for ax in axes[1]:
        ax.set_xlabel("pas")
    handles, labels = axes[1, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=len(labels))
    fig.suptitle(suptitle, x=0.01, ha="left", color=INK, fontsize=12)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pop", type=int, default=300, help="effectif de départ")
    parser.add_argument("--steps", type=int, default=20_000)
    parser.add_argument("--rep", type=int, default=24)
    parser.add_argument("--mu", type=float, default=0.1, help="mutations par naissance")
    parser.add_argument("--every", type=int, default=100, help="pas entre deux relevés")
    parser.add_argument("--null", type=int, default=20_000, help="taille de l'échantillon nul")
    parser.add_argument("--jobs", type=int, default=2, help="processus en parallèle")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    arch = Corps(MOTORS).arch
    sample = arch.random(np.random.default_rng([args.seed, 999]), args.null, BOUND)
    null = _classify(brains(sample))
    exact = exact_brain_kinds(BOUND) | exact_structural_parts(BOUND)
    for kind, share in exact.items():
        null[KINDS.index(kind)] = share

    tasks = [
        (regime, r, args.pop, args.steps, args.mu, args.every, args.seed)
        for regime in REGIMES
        for r in range(args.rep)
    ]
    shape = (len(MEASURES), args.rep, args.steps // args.every + 1)
    results = {regime: np.full(shape, np.nan) for regime in REGIMES}
    finals = {regime: [None] * args.rep for regime in REGIMES}
    with Pool(args.jobs) as pool:
        for regime, r, series, population in pool.imap_unordered(one_population, tasks):
            results[regime][:, r] = series
            finals[regime][r] = population
    per_pop = {
        regime: par_population(series, [len(p) == 0 for p in finals[regime]])
        for regime, series in results.items()
    }

    print("seconde moitié, moyenne ± écart-type entre populations (en %, sauf les deux premières)")
    print(f"{'':18}" + "".join(f"{regime:>19}" for regime in REGIMES) + f"{'uniforme':>10}")
    for name in SHOWN:
        m = MEASURES.index(name)
        scale = 1 if name in ("effectif", "naissances") else 100
        cells = []
        for regime in REGIMES:
            v = scale * per_pop[regime][m]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                cells.append(f"{np.nanmean(v):11.2f} ± {np.nanstd(v):<5.2f}")
        uniform = f"{100 * null[KINDS.index(name)]:10.3f}" if name in KINDS else ""
        print(f"{name:18}" + "".join(cells) + uniform)
    for regime in REGIMES:
        extinct = sum(len(p) == 0 for p in finals[regime])
        print(f"extinctions, régime {regime} : {extinct}/{args.rep}")

    rng = np.random.default_rng([args.seed, 555])
    tested = ["dependance", *KINDS]
    print("\ntest par permutation contre le régime neutre (valeur p bilatérale)")
    print(f"{'':18}" + "".join(f"{regime:>19}" for regime in list(REGIMES)[:-1]))
    for name in tested:
        m = MEASURES.index(name)
        p = [permutation_test(per_pop[r][m], per_pop["neutre"][m], rng) for r in list(REGIMES)[:-1]]
        print(f"{name:18}" + "".join(f"{format_p(x):>19}" for x in p))

    print("\nlecture retardée contre lecture immédiate")
    for world in ("mélangé", "espace"):
        cells = []
        for name in tested:
            m = MEASURES.index(name)
            p = permutation_test(
                per_pop[f"{world} retardé"][m], per_pop[f"{world} immédiat"][m], rng
            )
            cells.append(f"{name} {format_p(p)}")
        print(f"   {world:8} " + "   ".join(cells))

    direct = HERE.parent / "monde_dechet" / "out" / "par_population.npz"
    if direct.exists():
        print("\nlecteurs contre lecture directe (populations du monde à déchet)")
        reference = np.load(direct, allow_pickle=True)
        names = list(reference["mesures"])
        for regime in list(REGIMES)[:-1]:
            world = regime.split()[0]
            cells = []
            for name in tested:
                before = reference[world][names.index(name)]
                p = permutation_test(per_pop[regime][MEASURES.index(name)], before, rng)
                cells.append(
                    f"{name} {100 * np.nanmean(before):.1f} % en direct, p {format_p(p, True)}"
                )
            print(f"   {regime:17} " + "   ".join(cells))
    else:
        print("\n(lecture directe non comparée : lancer d'abord experiments/monde_dechet/run.py)")

    print("\nmotif du moteur « bouger » (capteur 0, capteur 1) dans les populations finales")
    target = {}
    for regime in REGIMES:
        tallies = motifs(finals[regime])
        keys = {k for t in tallies for k in t}
        mean = {k: np.mean([t.get(k, 0) for t in tallies]) for k in keys}
        target[regime] = np.array([t.get(TARGET, 0) for t in tallies])
        print(f"   régime {regime}")
        for k in sorted(keys, key=lambda k: -mean[k])[:4]:
            major = sum(t.get(k, 0) > 0.5 for t in tallies)
            share = f"{100 * mean[k]:5.1f} %"
            print(f"      {k[0]:14} {k[1]:14} {share}   majoritaire dans {major}/{args.rep}")
    for regime in list(REGIMES)[:-1]:
        p = permutation_test(target[regime], target["neutre"], rng)
        here, there = 100 * target[regime].mean(), 100 * target["neutre"].mean()
        print(
            f"   motif « {TARGET[0]}, {TARGET[1]} », {regime} : {here:.1f} % "
            f"contre {there:.1f} % en neutre, p {format_p(p, True)}"
        )

    np.savez_compressed(
        out / "populations_finales.npz",
        **{f"{regime}_{r}": p for regime, pops in finals.items() for r, p in enumerate(pops)},
    )
    np.savez_compressed(out / "par_population.npz", mesures=MEASURES, **per_pop)
    with open(out / "moteurs_lecteurs.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "step", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for k in range(series.shape[2]):
                    writer.writerow([regime, r, k * args.every, *series[:, r, k].round(5)])
    suptitle = (
        f"Moteurs lecteurs — {args.rep} populations par régime : moyenne, et bande entre "
        "quartiles ; tirets : lecture immédiate"
    )
    figure(results, null, args.every, out / "moteurs_lecteurs.png", suptitle)
    print(f"\nfigure : {out / 'moteurs_lecteurs.png'}")


if __name__ == "__main__":
    main()
