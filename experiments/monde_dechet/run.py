"""Ressource et déchet toxique : monde bien mélangé, monde en 2D, régime neutre.

    python experiments/monde_dechet/run.py    # écrit out/monde_dechet.png

Protocole et hypothèses : journal/2026-11-14_monde-dechet.md.
"""

from __future__ import annotations

import argparse
import csv
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from commun import BOUND, ESPACE, REGIMES, naissance

from simsbn.milieu import ARCH
from simsbn.stats import format_p, permutation_test
from simsbn.structure import KINDS, Classifier, exact_brain_law
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

COLORS = {"mélangé": BLUE, "espace": ORANGE, "neutre": MUTED}
ACTIVITY = [
    "naissances", "manger_0", "manger_1", "bouger_0", "bouger_1", "dependance", "capteur",
    "servies", "empoisonnees",
]  # fmt: skip
MEASURES = ["effectif", *ACTIVITY, "dechet", *KINDS]
TESTED = ["dependance", "scission_sbn", "controle_cerveau", "psbn_cerveau", "controle_interne"]
PANELS = [  # (mesure, titre, unité, indice du modèle nul uniforme ou None)
    ("effectif", "Effectif", "agents vivants", None),
    ("dependance", "Dépendance au contexte : P(bouger | 0) - P(bouger | 1)", "points de %", None),
    ("empoisonnees", "Part des ingestions empoisonnées", "%", None),
    ("controle_cerveau", "Cerveau seul : part à nœud de contrôle", "%", 0),
    ("scission_sbn", "Part dont la face « capteur = 1 » est un SBN", "%", 2),
    ("controle_interne", "Part à contrôle interne (plus de 2 feuilles PTBN)", "%", 3),
]
_classify = Classifier()  # un par processus


def one_population(task):
    regime, r, pop, steps, mu, every, seed = task
    vie = naissance(regime, r, seed, pop, mu)
    series = np.full((len(MEASURES), steps // every + 1), np.nan)
    series[0, 0] = len(vie)
    series[-len(KINDS) :, 0] = _classify(vie.population)
    for k in range(1, steps // every + 1):
        for _ in range(every):
            vie.step()
            if not len(vie):
                break
        series[0, k] = len(vie)
        if not len(vie):
            break
        stats = vie.stats()
        series[1 : 1 + len(ACTIVITY), k] = [stats[name] for name in ACTIVITY]
        if vie.monde.neutral:  # sans objet : la nourriture n'y dépend pas des demandes
            series[MEASURES.index("servies"), k] = np.nan
        series[MEASURES.index("dechet"), k] = vie.waste.sum() / ESPACE.cells
        series[-len(KINDS) :, k] = _classify(vie.population)
    return regime, r, series, vie.population


def sensor_signs(populations) -> np.ndarray:
    """Part de poids capteur -> nœud négatifs, nuls, positifs : ``(3 nœuds, 3 signes)``.

    Moyenne des populations non éteintes, chacune comptant pour une.
    """
    rows = []
    for p in populations:
        if len(p):
            signs = np.sign(p[:, 0, 1:])  # (agents, nœuds du cerveau)
            rows.append([[(signs[:, j] == v).mean() for v in (-1, 0, 1)] for j in range(3)])
    return np.mean(rows, axis=0)


def figure(results, null, every, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    for ax, (measure, title, unit, null_index) in zip(axes.flat, PANELS, strict=True):
        m = MEASURES.index(measure)
        scale = 1 if measure == "effectif" else 100
        for regime, color in COLORS.items():
            if regime == "neutre" and measure == "empoisonnees":
                continue  # sans objet : pas de poison en régime neutre
            data = scale * results[regime][m]
            t = every * np.arange(data.shape[1])
            for row in data:
                ax.plot(t, row, color=color, linewidth=0.6, alpha=0.12)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)  # relevé sans aucune valeur
                mean = np.nanmean(data, axis=0)
            ax.plot(t, mean, color=color, linewidth=2, label=f"régime {regime}")
        if null_index is not None:
            ax.axhline(
                100 * null[null_index], color=INK, linewidth=1, linestyle=(0, (4, 3)),
                label="loi uniforme",
            )  # fmt: skip
        if measure == "dependance":
            ax.axhline(0, color=INK, linewidth=0.8)
        else:
            ax.set_ylim(bottom=0)
        ax.set_ylabel(unit)
        ax.set_title(title)
    for ax in axes[1]:
        ax.set_xlabel("pas")
    axes[1, 0].legend(loc="upper right")
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

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    null = _classify(ARCH.random(np.random.default_rng([args.seed, 999]), args.null, BOUND))
    null[:2] = exact_brain_law(BOUND)

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

    # Une valeur par population : moyenne des relevés de la seconde moitié.
    half = args.steps // args.every // 2 + 1
    per_pop = {}
    for regime, series in results.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            per_pop[regime] = np.nanmean(series[:, :, half:], axis=2)
        extinct = np.array([len(p) == 0 for p in finals[regime]])
        per_pop[regime][1:, extinct] = np.nan  # une population éteinte ne compte pas

    shown = ["effectif", "naissances", "bouger_0", "bouger_1", "dependance", "manger_0",
             "manger_1", "servies", "empoisonnees", *KINDS]  # fmt: skip
    print("seconde moitié, moyenne ± écart-type entre populations (en %, sauf les deux premières)")
    print(f"{'':18}" + "".join(f"{regime:>20}" for regime in REGIMES) + f"{'loi uniforme':>14}")
    for name in shown:
        m = MEASURES.index(name)
        scale = 1 if name in ("effectif", "naissances") else 100
        cells = []
        for regime in REGIMES:
            v = scale * per_pop[regime][m]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                cells.append(f"{np.nanmean(v):12.2f} ± {np.nanstd(v):<5.2f}")
        uniform = f"{100 * null[KINDS.index(name)]:14.2f}" if name in KINDS else ""
        print(f"{name:18}" + "".join(cells) + uniform)
    for regime in REGIMES:
        extinct = sum(len(p) == 0 for p in finals[regime])
        print(f"extinctions, régime {regime} : {extinct}/{args.rep}")

    print("\ntest par permutation des populations (valeur p bilatérale)")
    print(f"{'':18}{'espace/neutre':>16}{'mélangé/neutre':>16}{'espace/mélangé':>16}")
    rng = np.random.default_rng([args.seed, 555])
    for name in TESTED:
        m = MEASURES.index(name)
        pairs = (("espace", "neutre"), ("mélangé", "neutre"), ("espace", "mélangé"))
        p = [permutation_test(per_pop[a][m], per_pop[b][m], rng) for a, b in pairs]
        print(f"{name:18}" + "".join(f"{format_p(x):>16}" for x in p))

    print("\npoids du capteur dans les populations finales : part de négatifs / nuls / positifs")
    for regime in REGIMES:
        signs = 100 * sensor_signs(finals[regime])
        cells = [
            f"{label} {a:3.0f} / {b:3.0f} / {c:3.0f}"
            for label, (a, b, c) in zip(("ingérer", "bouger", "caché"), signs, strict=True)
        ]
        print(f"{regime:10}" + "   ".join(cells))

    np.savez_compressed(
        out / "populations_finales.npz",
        **{f"{regime}_{r}": p for regime, pops in finals.items() for r, p in enumerate(pops)},
    )
    np.savez_compressed(out / "par_population.npz", mesures=MEASURES, **per_pop)
    with open(out / "monde_dechet.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "step", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for k in range(series.shape[2]):
                    writer.writerow([regime, r, k * args.every, *series[:, r, k].round(5)])
    suptitle = (
        f"Ressource et déchet toxique — {args.rep} populations par régime, moyenne en trait "
        "épais ; la survie seule sélectionne"
    )
    figure(results, null, args.every, out / "monde_dechet.png", suptitle)
    print(f"\nfigure : {out / 'monde_dechet.png'}")


if __name__ == "__main__":
    main()
