"""Fondateur unique : toute la variété vient des mutations, à plusieurs taux.

    python experiments/fondateur/fondateur.py    # une fois : choisit le fondateur
    python experiments/fondateur/run.py          # écrit out/fondateur_unique.png

Protocole et hypothèses : journal/2026-11-15_fondateur-unique.md.
"""

from __future__ import annotations

import argparse
import csv
import warnings
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from fondateur import BOUND, CORPS, MONDE

from simsbn.monde import Vie
from simsbn.stats import format_p, permutation_test
from simsbn.structure import KINDS, Classifier
from simsbn.suivi import MEASURES, VARIETE, brains, par_population, suivre, variete
from simsbn.viz import INK, MUTED, ORANGE, apply_style

HERE = Path(__file__).parent
RATES = (0.0, 0.1, 0.3, 1.0)  # mutations par naissance
REGIMES = {"directions": MONDE, "neutre": replace(MONDE, neutral=True)}
NAMES = [*MEASURES, *VARIETE]
SHOWN = ["effectif", "naissances", "dependance", "persistance", *VARIETE,
         "pc1_po2_poids", "pc2_po1_poids", "controle_cerveau"]  # fmt: skip
TESTED = ["dependance", "persistance", *VARIETE, "pc1_po2_poids", "pc2_po1_poids",
          "controle_cerveau"]  # fmt: skip
PANELS = [  # (mesure, titre, unité)
    ("effectif", "Effectif", "agents vivants"),
    ("lignees", "Lignées vivantes (ancêtres du pas 0)", "lignées"),
    ("genotypes", "Génotypes distincts vivants", "génotypes"),
    ("distance_fondateur", "Distance au fondateur", "poids différents"),
    ("persistance", "Persistance du déplacement", "cosinus"),
    ("dependance", "Dépendance au capteur", "points"),
]
_classify = Classifier()  # un par processus


def one_population(task):
    regime, mu, r, pop, steps, every, seed, founder = task
    rng = np.random.default_rng([seed, 7, 2, list(REGIMES).index(regime), RATES.index(mu), r])
    vie = Vie(np.repeat(founder[None], pop, axis=0), REGIMES[regime], rng, mu, BOUND, CORPS)
    mask = CORPS.arch.mask()
    watch = np.random.default_rng([seed, 7, 3, r])
    series = np.full((len(NAMES), steps // every + 1), np.nan)
    series[0, 0] = len(vie)
    series[len(MEASURES) :, 0] = variete(vie.population, vie.lineage, founder, mask, watch)
    series[-len(KINDS) - len(VARIETE) : -len(VARIETE), 0] = _classify(brains(vie.population))
    for k in range(1, steps // every + 1):
        if not len(vie):
            series[0, k] = 0
            continue
        block = suivre(vie, every, every, _classify, MONDE.cells)
        series[: len(MEASURES), k] = block[:, 1]
        if len(vie):
            series[len(MEASURES) :, k] = variete(vie.population, vie.lineage, founder, mask, watch)
    return regime, mu, r, series, len(vie)


def figure(results, every, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    shades = {"directions": ["#f7c7b0", "#f4a07a", ORANGE, "#a93c14"],
              "neutre": ["#d0cfcb", "#a8a7a3", MUTED, INK]}  # fmt: skip
    for ax, (measure, title, unit) in zip(axes.flat, PANELS, strict=True):
        m = NAMES.index(measure)
        scale = 100 if unit == "points" else 1
        for regime in REGIMES:
            for i, mu in enumerate(RATES):
                data = scale * results[(regime, mu)][m]
                t = every * np.arange(data.shape[1])
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    mean = np.nanmean(data, axis=0)
                ax.plot(t, mean, color=shades[regime][i], linewidth=1.8,
                        linestyle="-" if regime == "directions" else (0, (3, 2)),
                        label=f"{regime}, mu = {mu:g}")  # fmt: skip
        if measure in ("dependance", "persistance"):
            ax.axhline(0, color=INK, linewidth=0.8)
        else:
            ax.set_ylim(bottom=0)
        ax.set_ylabel(unit)
        ax.set_title(title)
    for ax in axes[1]:
        ax.set_xlabel("pas")
    handles, labels = axes[1, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=4)
    fig.suptitle(suptitle, x=0.01, ha="left", color=INK, fontsize=12)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pop", type=int, default=300, help="clones au départ")
    parser.add_argument("--steps", type=int, default=20_000)
    parser.add_argument("--rep", type=int, default=24)
    parser.add_argument("--every", type=int, default=100, help="pas entre deux relevés")
    parser.add_argument("--jobs", type=int, default=2, help="processus en parallèle")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = HERE / "out"
    founder_path = out / "fondateur.npy"
    if not founder_path.exists():
        raise SystemExit("lancer d'abord experiments/fondateur/fondateur.py")
    founder = np.load(founder_path)

    tasks = [
        (regime, mu, r, args.pop, args.steps, args.every, args.seed, founder)
        for regime in REGIMES
        for mu in RATES
        for r in range(args.rep)
    ]
    shape = (len(NAMES), args.rep, args.steps // args.every + 1)
    results = {(regime, mu): np.full(shape, np.nan) for regime in REGIMES for mu in RATES}
    alive = {key: np.zeros(args.rep, dtype=bool) for key in results}
    with Pool(args.jobs) as pool:
        for regime, mu, r, series, size in pool.imap_unordered(one_population, tasks):
            results[(regime, mu)][:, r] = series
            alive[(regime, mu)][r] = size > 0
    per_pop = {key: par_population(s, ~alive[key]) for key, s in results.items()}

    keys = list(results)
    print("seconde moitié, moyenne ± écart-type entre populations (dépendance en points)")
    print(f"{'':20}" + "".join(f"{regime[:4]} {mu:g}".rjust(15) for regime, mu in keys))
    for name in SHOWN:
        m = NAMES.index(name)
        scale = 100 if name in (*KINDS, "dependance") else 1
        cells = []
        for key in keys:
            v = scale * per_pop[key][m]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                cells.append(f"{np.nanmean(v):8.2f}±{np.nanstd(v):<5.2f}")
        print(f"{name:20}" + "".join(c.rjust(15) for c in cells))
    for key in keys:
        print(f"extinctions {key[0]} mu = {key[1]:g} : {(~alive[key]).sum()}/{args.rep}")

    zero = results[("directions", 0.0)]
    print("\ncontrôle mu = 0 (directions) : génotypes distincts min/max, distance max")
    g, d = NAMES.index("genotypes"), NAMES.index("distance_fondateur")
    print(f"   {np.nanmin(zero[g])} / {np.nanmax(zero[g])} ; distance {np.nanmax(zero[d])}")
    early = np.nanmean(
        zero[[NAMES.index("dependance"), NAMES.index("persistance")], :, 1:6], axis=2
    )
    late = per_pop[("directions", 0.0)][[NAMES.index("dependance"), NAMES.index("persistance")]]
    first, second = np.nanmean(early, axis=1).round(3), np.nanmean(late, axis=1).round(3)
    print(f"   dépendance, persistance : 500 premiers pas {first} ; seconde moitié {second}")

    rng = np.random.default_rng([args.seed, 7, 555])
    print("\ntest par permutation, directions contre neutre (valeur p bilatérale)")
    print(f"{'':20}" + "".join(f"mu = {mu:g}".rjust(12) for mu in RATES))
    for name in TESTED:
        m = NAMES.index(name)
        ps = [permutation_test(per_pop[("directions", mu)][m], per_pop[("neutre", mu)][m], rng)
              for mu in RATES]  # fmt: skip
        print(f"   {name:17}" + "".join(format_p(p).rjust(12) for p in ps))
    print("\ntest par permutation, directions à mu contre directions à mu = 0")
    print(f"{'':20}" + "".join(f"mu = {mu:g}".rjust(12) for mu in RATES[1:]))
    for name in ("dependance", "persistance", "effectif"):
        m = NAMES.index(name)
        ps = [permutation_test(per_pop[("directions", mu)][m], per_pop[("directions", 0.0)][m], rng)
              for mu in RATES[1:]]  # fmt: skip
        print(f"   {name:17}" + "".join(format_p(p).rjust(12) for p in ps))

    np.savez_compressed(
        out / "par_population.npz",
        mesures=NAMES,
        **{f"{regime}_{mu:g}": v for (regime, mu), v in per_pop.items()},
    )
    with open(out / "fondateur_unique.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "mu", "replicate", "step", *NAMES])
        for (regime, mu), series in results.items():
            for r in range(args.rep):
                for k in range(series.shape[2]):
                    writer.writerow([regime, mu, r, k * args.every, *series[:, r, k].round(5)])
    suptitle = (
        f"Fondateur unique, {args.rep} populations par condition : "
        "moyenne (plein : directions, tirets : neutre)"
    )
    figure(results, args.every, out / "fondateur_unique.png", suptitle)
    print(f"\nfigure : {out / 'fondateur_unique.png'}")


if __name__ == "__main__":
    main()
