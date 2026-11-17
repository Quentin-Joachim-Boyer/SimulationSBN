"""Flux d'énergie du milieu : recyclage, conservation, diffusion, accidents et cadavres.

    python experiments/energie/run.py    # écrit out/energie.png et out/energie.csv

Protocole et hypothèses : journal/2026-11-17_energie-milieu.md. Agent : capteur de
bien-être, cerveau de 3 nœuds sans étiquette, cinq moteurs lecteurs retardés, k = 2.
"""

from __future__ import annotations

import argparse
import csv
import warnings
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simsbn.monde import Corps, Monde, Vie
from simsbn.stats import format_p, permutation_test
from simsbn.structure import KINDS, Classifier, exact_brain_kinds, exact_structural_parts
from simsbn.suivi import brains
from simsbn.viz import BLUE, INK, MUTED, apply_style

HERE = Path(__file__).parent
BOUND = 3
TEMOIN = Monde(divide_at=40)  # le régime « sans saisons » de saisons_directions
ACCIDENT = 0.005  # mort accidentelle par pas : fixé dans le journal avant l'expérience
REGIMES = {
    "témoin": TEMOIN,
    "recyclage": replace(TEMOIN, recyclage=0.5),
    "conservation": replace(TEMOIN, conservation=True),
    "diffusion": replace(TEMOIN, diffusion=0.2),
    "accidents": replace(TEMOIN, accident=ACCIDENT),
    "cadavres": replace(TEMOIN, accident=ACCIDENT, cadavres=True),
    "neutre": replace(TEMOIN, neutral=True),
}
REFERENCES = ("témoin", "neutre")
CORPS = Corps(("ingérer", "nord", "sud", "est", "ouest"), ticks=2)
ACTIVITY = ["naissances", "morts", "accidents", "manger_0", "manger_1", "bouger_0",
            "bouger_1", "dependance", "persistance", "servies", "empoisonnees"]  # fmt: skip
EXTRA = ["effectif", "nourriture", "dechet", "entree", "depense", "energie"]
NAMES = [*EXTRA, *ACTIVITY, *KINDS]
PERCENT = {"manger_0", "manger_1", "bouger_0", "bouger_1", "dependance", "servies",
           "empoisonnees", *KINDS}  # fmt: skip
SHOWN = ["effectif", "nourriture", "dechet", "entree", "depense", "energie", "naissances",
         "morts", "accidents", "manger_0", "manger_1", "bouger_0", "bouger_1", "dependance",
         "persistance", "empoisonnees", "pc1_po2_poids", "pc2_po1_poids", "controle_cerveau",
         "psbn_cerveau"]  # fmt: skip
BEHAVIOUR = ["effectif", "bouger_0", "bouger_1", "dependance", "persistance"]
STRUCTURE = ["pc1_po2_poids", "pc2_po1_poids", "controle_cerveau", "psbn_cerveau"]
PANELS = [  # (mesure, titre, unité, loi uniforme ou None)
    ("effectif", "Effectif", "agents vivants", None),
    ("dependance", "Dépendance au capteur", "points", None),
    ("persistance", "Persistance du déplacement", "cosinus", None),
    ("pc1_po2_poids", "PC de 1 nœud (poids)", "%", "pc1_po2_poids"),
    ("pc2_po1_poids", "PC de 2 nœuds (poids)", "%", "pc2_po1_poids"),
    ("controle_cerveau", "PTBN (nœud de contrôle)", "%", "controle_cerveau"),
]
_classify = Classifier()  # un par processus


def one_population(task):
    """Une valeur de chaque mesure par fenêtre de ``every`` pas."""
    regime, r, pop, steps, every, mu, seed = task
    rng = np.random.default_rng([seed, r, list(REGIMES).index(regime), 9])
    monde = REGIMES[regime]
    vie = Vie(CORPS.arch.random(rng, pop, BOUND), monde, rng, mu, BOUND, CORPS)
    series = np.full((len(NAMES), steps // every), np.nan)
    for k in range(steps // every):
        flows = dict(vie.bilan)
        for _ in range(every):
            if len(vie):
                vie.step()
        if not len(vie):
            series[0, k:] = 0
            break
        stats = vie.stats()
        series[: len(EXTRA), k] = [
            len(vie),
            vie.food.mean(),
            vie.waste.mean(),
            (vie.bilan["entree"] - flows["entree"]) / every,
            (vie.bilan["depense"] - flows["depense"]) / every,
            vie.energie_totale(),
        ]
        series[len(EXTRA) : len(EXTRA) + len(ACTIVITY), k] = [stats[n] for n in ACTIVITY]
        series[-len(KINDS) :, k] = _classify(brains(vie.population))
    return regime, r, series, len(vie)


def scale(name):
    return 100 if name in PERCENT else 1


def figure(per_pop, null, path, suptitle):
    """Une valeur par population (seconde moitié) et par régime ; trait : la moyenne."""
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.6), layout="constrained")
    names = list(REGIMES)
    jitter = np.random.default_rng(0).uniform(-0.18, 0.18, size=200)
    for ax, (measure, title, unit, law) in zip(axes.flat, PANELS, strict=True):
        m = NAMES.index(measure)
        for i, regime in enumerate(names):
            values = scale(measure) * per_pop[regime][m]
            values = values[~np.isnan(values)]
            color = MUTED if regime in REFERENCES else BLUE
            ax.scatter(i + jitter[: len(values)], values, s=16, color=color, alpha=0.55,
                       linewidths=0)  # fmt: skip
            if len(values):
                ax.plot([i - 0.3, i + 0.3], [values.mean()] * 2, color=INK, linewidth=2)
        if law is not None:
            ax.axhline(100 * null[law], color=INK, linewidth=1, linestyle=(0, (1, 2)))
            ax.text(len(names) - 0.5, 100 * null[law], " loi uniforme", color=MUTED,
                    fontsize=8, va="bottom", ha="right")  # fmt: skip
        if unit == "points":
            ax.axhline(0, color=INK, linewidth=0.8)
        elif unit != "cosinus":
            ax.set_ylim(bottom=0)
        ax.set_xticks(range(len(names)), names, rotation=30, ha="right")
        ax.set_ylabel(unit)
        ax.set_title(title)
    fig.suptitle(suptitle, x=0.01, ha="left", color=INK, fontsize=12)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pop", type=int, default=300, help="effectif de départ")
    parser.add_argument("--steps", type=int, default=20_000)
    parser.add_argument("--every", type=int, default=100, help="pas par fenêtre de relevé")
    parser.add_argument("--rep", type=int, default=24)
    parser.add_argument("--mu", type=float, default=0.5, help="mutations par naissance")
    parser.add_argument("--regimes", nargs="*", default=list(REGIMES), choices=list(REGIMES))
    parser.add_argument("--jobs", type=int, default=2, help="processus en parallèle")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    null = exact_brain_kinds(BOUND) | exact_structural_parts(BOUND)
    windows = args.steps // args.every
    tasks = [
        (regime, r, args.pop, args.steps, args.every, args.mu, args.seed)
        for regime in args.regimes
        for r in range(args.rep)
    ]
    results = {g: np.full((len(NAMES), args.rep, windows), np.nan) for g in args.regimes}
    alive = {g: np.zeros(args.rep, dtype=bool) for g in args.regimes}
    with Pool(args.jobs) as pool:
        for regime, r, series, size in pool.imap_unordered(one_population, tasks):
            results[regime][:, r] = series
            alive[regime][r] = size > 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        per_pop = {g: np.nanmean(v[:, :, windows // 2 :], axis=2) for g, v in results.items()}
        first = {g: np.nanmean(v[:, :, :5], axis=(1, 2)) for g, v in results.items()}

    print("seconde moitié, moyenne ± écart-type entre populations (en % ou points pour les")
    print("fréquences) ; entre crochets : moyenne des 5 premières fenêtres")
    print(f"{'':16}" + "".join(f"{g:>26}" for g in args.regimes) + f"{'uniforme':>10}")
    for name in SHOWN:
        m = NAMES.index(name)
        cells = []
        for g in args.regimes:
            v = scale(name) * per_pop[g][m]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                cells.append(f"{np.nanmean(v):8.2f}±{np.nanstd(v):<6.2f}"
                             f"[{scale(name) * first[g][m]:8.2f}]")  # fmt: skip
        uniform = f"{100 * null[name]:10.3f}" if name in null else ""
        print(f"{name:16}" + "".join(c.rjust(26) for c in cells) + uniform)
    for g in args.regimes:
        print(f"extinctions, {g} : {(~alive[g]).sum()}/{args.rep}")

    rng = np.random.default_rng([args.seed, 9, 555])
    for reference, names in (("témoin", BEHAVIOUR + STRUCTURE), ("neutre", STRUCTURE)):
        if reference not in per_pop:
            continue
        others = [g for g in args.regimes if g not in REFERENCES]
        if reference == "neutre" and "témoin" in per_pop:
            others = ["témoin", *others]
        print(f"\ntest par permutation (valeur p bilatérale) : chaque régime contre {reference}")
        print(f"{'':20}" + "".join(f"{g:>14}" for g in others))
        for name in names:
            m = NAMES.index(name)
            ps = [format_p(permutation_test(per_pop[g][m], per_pop[reference][m], rng))
                  for g in others]  # fmt: skip
            print(f"   {name:17}" + "".join(p.rjust(14) for p in ps))

    np.savez_compressed(out / "par_population.npz", mesures=NAMES, **per_pop)
    with open(out / "energie.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "window_end", *NAMES])
        for g, series in results.items():
            for r in range(args.rep):
                for k in range(windows):
                    writer.writerow([g, r, (k + 1) * args.every, *series[:, r, k].round(5)])
    if set(args.regimes) == set(REGIMES):
        suptitle = (
            f"Flux d'énergie du milieu, {args.rep} populations par régime, {args.steps} pas : "
            "un point par population (seconde moitié), trait : moyenne"
        )
        figure(per_pop, null, out / "energie.png", suptitle)
        print(f"\nfigure : {out / 'energie.png'}")


if __name__ == "__main__":
    main()
