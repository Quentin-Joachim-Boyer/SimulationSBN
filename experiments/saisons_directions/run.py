"""Saisons cachées avec cinq moteurs (directions absolues), k = 2, mutation 0,5.

    python experiments/saisons_directions/run.py    # écrit out/saisons_directions.png

Protocole et hypothèses : journal/2026-11-15_saisons-directions.md.
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
from simsbn.suivi import ACTIVITY, brains
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

HERE = Path(__file__).parent
BOUND = 3
SUMMER, WINTER = 80, 20
YEAR = SUMMER + WINTER
ESPACE = Monde(divide_at=40)  # monde à déchet, réserve doublée (comme saisons_reserve)
SAISONS = replace(ESPACE, summer=SUMMER, winter=WINTER)
CORPS = Corps(("ingérer", "nord", "sud", "est", "ouest"), ticks=2)
REGIMES = {  # nom : (monde, couleur)
    "saisons": (SAISONS, ORANGE),
    "sans saisons": (ESPACE, BLUE),
    "neutre à saisons": (replace(SAISONS, neutral=True), MUTED),
}
EXTRA = ["effectif_ete", "effectif_hiver", "perte_hiver", "bouger_hiver_moins_ete"]
NAMES = [*EXTRA, *ACTIVITY, *KINDS]
SHOWN = ["effectif_ete", "effectif_hiver", "perte_hiver", "manger_ete", "manger_hiver",
         "economie_hiver", "bouger_ete", "bouger_hiver", "bouger_hiver_moins_ete", "dependance",
         "persistance", "pc1_po2_poids", "pc2_po1_poids", "controle_cerveau",
         "psbn_cerveau"]  # fmt: skip
TESTED = ["perte_hiver", "economie_hiver", "bouger_hiver_moins_ete", "dependance", "persistance",
          "pc1_po2_poids", "pc2_po1_poids", "controle_cerveau"]  # fmt: skip
PANELS = [  # (mesure, titre, unité, loi uniforme ou None)
    ("effectif_hiver", "Effectif en fin d'hiver", "agents vivants", None),
    ("economie_hiver", "Économie d'hiver", "points", None),
    ("bouger_hiver_moins_ete", "Déplacement : hiver moins été", "points", None),
    ("pc1_po2_poids", "PC de 1 nœud (poids)", "%", "pc1_po2_poids"),
    ("pc2_po1_poids", "PC de 2 nœuds (poids)", "%", "pc2_po1_poids"),
    ("controle_cerveau", "PTBN (nœud de contrôle)", "%", "controle_cerveau"),
]
_classify = Classifier()  # un par processus


def one_population(task):
    """Une valeur de chaque mesure par année (80 pas puis 20 pas, avec ou sans saisons)."""
    regime, r, pop, years, mu, seed = task
    rng = np.random.default_rng([seed, r, list(REGIMES).index(regime), 8])
    vie = Vie(CORPS.arch.random(rng, pop, BOUND), REGIMES[regime][0], rng, mu, BOUND, CORPS)
    series = np.full((len(NAMES), years), np.nan)
    for y in range(years):
        sizes = []
        for length in (SUMMER, WINTER):
            for _ in range(length):
                if len(vie):
                    vie.step()
            sizes.append(len(vie))
        if not len(vie):
            break
        stats = vie.stats()
        if stats["bouger_hiver"] != stats["bouger_hiver"]:  # monde sans saisons : par le pas
            stats["bouger_hiver"] = stats["bouger_ete"] = np.nan
        loss = 1 - sizes[1] / sizes[0] if sizes[0] else np.nan
        series[: len(EXTRA), y] = [*sizes, loss, stats["bouger_hiver"] - stats["bouger_ete"]]
        series[len(EXTRA) : len(EXTRA) + len(ACTIVITY), y] = [stats[name] for name in ACTIVITY]
        series[-len(KINDS) :, y] = _classify(brains(vie.population))
    return regime, r, series, len(vie)


def figure(results, null, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    for ax, (measure, title, unit, law) in zip(axes.flat, PANELS, strict=True):
        m = NAMES.index(measure)
        scale = 1 if unit == "agents vivants" else 100
        for regime, (_, color) in REGIMES.items():
            data = scale * results[regime][m]
            if np.isnan(data).all():
                continue  # sans objet : pas d'hiver dans ce régime
            t = YEAR * np.arange(1, data.shape[1] + 1)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                low, high = np.nanpercentile(data, [25, 75], axis=0)
                mean = np.nanmean(data, axis=0)
            ax.fill_between(t, low, high, color=color, alpha=0.1, linewidth=0)
            ax.plot(t, mean, color=color, linewidth=1.6, label=f"régime {regime}")
        if law is not None:
            ax.axhline(100 * null[law], color=INK, linewidth=1, linestyle=(0, (1, 2)),
                       label="loi uniforme")  # fmt: skip
        if unit == "points":
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
    parser.add_argument("--years", type=int, default=200, help="années de 100 pas")
    parser.add_argument("--rep", type=int, default=24)
    parser.add_argument("--mu", type=float, default=0.5, help="mutations par naissance")
    parser.add_argument("--jobs", type=int, default=2, help="processus en parallèle")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    null = exact_brain_kinds(BOUND) | exact_structural_parts(BOUND)
    tasks = [
        (regime, r, args.pop, args.years, args.mu, args.seed)
        for regime in REGIMES
        for r in range(args.rep)
    ]
    results = {regime: np.full((len(NAMES), args.rep, args.years), np.nan) for regime in REGIMES}
    alive = {regime: np.zeros(args.rep, dtype=bool) for regime in REGIMES}
    with Pool(args.jobs) as pool:
        for regime, r, series, size in pool.imap_unordered(one_population, tasks):
            results[regime][:, r] = series
            alive[regime][r] = size > 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        per_pop = {k: np.nanmean(v[:, :, args.years // 2 :], axis=2) for k, v in results.items()}
        first = {k: np.nanmean(v[:, :, :10], axis=(1, 2)) for k, v in results.items()}

    print("seconde moitié, moyenne ± écart-type entre populations (en % ou points, sauf")
    print("effectifs et persistance) ; entre crochets : moyenne des 10 premières années")
    print(f"{'':24}" + "".join(f"{regime:>28}" for regime in REGIMES) + f"{'uniforme':>10}")
    for name in SHOWN:
        m = NAMES.index(name)
        scale = 1 if name.startswith("effectif") or name == "persistance" else 100
        cells = []
        for regime in REGIMES:
            v = scale * per_pop[regime][m]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                cells.append(f"{np.nanmean(v):8.2f} ± {np.nanstd(v):<6.2f}"
                             f"[{scale * first[regime][m]:7.2f}]")  # fmt: skip
        uniform = f"{100 * null[name]:10.3f}" if name in null else ""
        print(f"{name:24}" + "".join(c.rjust(28) for c in cells) + uniform)
    for regime in REGIMES:
        print(f"extinctions, régime {regime} : {(~alive[regime]).sum()}/{args.rep}")

    rng = np.random.default_rng([args.seed, 8, 555])
    print("\ntest par permutation (valeur p bilatérale) : saisons contre chaque autre régime")
    for name in TESTED:
        m = NAMES.index(name)
        ps = []
        for other in ("sans saisons", "neutre à saisons"):
            a, b = per_pop["saisons"][m], per_pop[other][m]
            ps.append("sans objet" if np.isnan(b).all() else format_p(permutation_test(a, b, rng)))
        print(f"   {name:24}{ps[0]:>14}{ps[1]:>14}")

    np.savez_compressed(out / "par_population.npz", mesures=NAMES, **per_pop)
    with open(out / "saisons_directions.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "year", *NAMES])
        for regime, series in results.items():
            for r in range(args.rep):
                for y in range(args.years):
                    writer.writerow([regime, r, y, *series[:, r, y].round(5)])
    suptitle = (
        f"Saisons cachées, cinq moteurs, mutation {args.mu:g} — {args.rep} populations par "
        "régime : moyenne par année, et bande entre quartiles"
    )
    figure(results, null, out / "saisons_directions.png", suptitle)
    print(f"\nfigure : {out / 'saisons_directions.png'}")


if __name__ == "__main__":
    main()
