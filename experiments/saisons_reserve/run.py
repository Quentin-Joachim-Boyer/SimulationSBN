"""Saisons cachées, deuxième essai : réserve doublée (division à 40), été 80, hiver 20.

    python experiments/saisons_reserve/run.py    # écrit out/saisons.png

Protocole et hypothèses : journal/2026-11-15_saisons-reserve.md.
"""

from __future__ import annotations

import argparse
import csv
import warnings
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import Monde, Vie
from simsbn.stats import format_p, permutation_test
from simsbn.structure import KINDS, Classifier, exact_brain_kinds, exact_structural_parts
from simsbn.suivi import MEASURES, brains, par_population, suivre
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

BOUND = 3
ESPACE = Monde(divide_at=40)  # monde de journal/2026-11-14_monde-dechet.md, réserve doublée
SAISONS = replace(ESPACE, summer=80, winter=20)
REGIMES = {  # nom : (monde, couleur)
    "saisons": (SAISONS, ORANGE),
    "sans saisons": (ESPACE, BLUE),
    "neutre à saisons": (replace(SAISONS, neutral=True), MUTED),
}
SHOWN = ["effectif", "naissances", "manger_ete", "manger_hiver", "economie_hiver", "bouger_ete",
         "bouger_hiver", "dependance", *KINDS]  # fmt: skip
TESTED = ["economie_hiver", "dependance", *KINDS]
PANELS = [  # (mesure, titre, unité, nom de la loi uniforme ou None)
    ("effectif", "Effectif", "agents vivants", None),
    ("economie_hiver", "Économie d'hiver", "points", None),
    ("dependance", "Dépendance au capteur", "points", None),
    ("pc1_po2_poids", "PC de 1 nœud (poids)", "%", "pc1_po2_poids"),
    ("pc2_po1_poids", "PC de 2 nœuds (poids)", "%", "pc2_po1_poids"),
    ("controle_cerveau", "PTBN (nœud de contrôle)", "%", "controle_cerveau"),
]
_classify = Classifier()  # un par processus


def one_population(task):
    regime, r, pop, steps, mu, every, seed = task
    rng = np.random.default_rng([seed, r, list(REGIMES).index(regime), 4])
    vie = Vie(ARCH.random(rng, pop, BOUND), REGIMES[regime][0], rng, mu, BOUND)
    return regime, r, suivre(vie, steps, every, _classify, ESPACE.cells), vie.population


def figure(results, null, every, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    for ax, (measure, title, unit, law) in zip(axes.flat, PANELS, strict=True):
        m = MEASURES.index(measure)
        scale = 1 if measure == "effectif" else 100
        for regime, (_, color) in REGIMES.items():
            data = scale * results[regime][m][:, 1:]
            if np.isnan(data).all():
                continue  # sans objet : pas d'hiver dans ce régime
            t = every * np.arange(1, data.shape[1] + 1)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                low, high = np.nanpercentile(data, [25, 75], axis=0)
                mean = np.nanmean(data, axis=0)
            ax.fill_between(t, low, high, color=color, alpha=0.1, linewidth=0)
            ax.plot(t, mean, color=color, linewidth=2, label=f"régime {regime}")
        if law is not None:
            ax.axhline(100 * null[KINDS.index(law)], color=INK, linewidth=1,
                       linestyle=(0, (1, 2)), label="loi uniforme")  # fmt: skip
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
    parser.add_argument("--steps", type=int, default=20_000)
    parser.add_argument("--rep", type=int, default=24)
    parser.add_argument("--mu", type=float, default=0.1, help="mutations par naissance")
    parser.add_argument("--every", type=int, default=20, help="pas entre deux relevés")
    parser.add_argument("--null", type=int, default=20_000, help="taille de l'échantillon nul")
    parser.add_argument("--jobs", type=int, default=2, help="processus en parallèle")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    sample = ARCH.random(np.random.default_rng([args.seed, 999]), args.null, BOUND)
    null = _classify(brains(sample))
    for kind, share in (exact_brain_kinds(BOUND) | exact_structural_parts(BOUND)).items():
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
    print(f"{'':20}" + "".join(f"{regime:>20}" for regime in REGIMES) + f"{'uniforme':>10}")
    for name in SHOWN:
        m = MEASURES.index(name)
        scale = 1 if name in ("effectif", "naissances") else 100
        cells = []
        for regime in REGIMES:
            v = scale * per_pop[regime][m]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                cells.append(f"{np.nanmean(v):12.2f} ± {np.nanstd(v):<5.2f}")
        uniform = f"{100 * null[KINDS.index(name)]:10.3f}" if name in KINDS else ""
        print(f"{name:20}" + "".join(cells) + uniform)
    for regime in REGIMES:
        extinct = sum(len(p) == 0 for p in finals[regime])
        print(f"extinctions, régime {regime} : {extinct}/{args.rep}")

    year = SAISONS.summer + SAISONS.winter
    if year % args.every == 0 and SAISONS.summer % args.every == 0:
        print("\nperte hivernale = 1 - effectif fin d'hiver / effectif fin d'été (seconde moitié)")
        loss_by_regime = {}
        for regime in ("saisons", "neutre à saisons"):
            eff = results[regime][0]  # (populations, relevés)
            ks = np.arange(eff.shape[1]) * args.every
            years = [y for y in range(args.steps // year) if y * year >= args.steps // 2]
            fall = [list(ks).index(y * year + SAISONS.summer) for y in years]
            rise = [list(ks).index((y + 1) * year) for y in years]
            with np.errstate(divide="ignore", invalid="ignore"):
                loss = np.nanmean(1 - eff[:, rise] / eff[:, fall], axis=1)
            loss_by_regime[regime] = loss
            print(f"{regime:20}{100 * np.nanmean(loss):6.1f} % ± {100 * np.nanstd(loss):.1f}")

    rng = np.random.default_rng([args.seed, 555])
    pairs = (("saisons", "neutre à saisons"), ("saisons", "sans saisons"))
    print("\ntest par permutation des populations (valeur p bilatérale)")
    print(f"{'':20}" + "".join(f"{a + ' / ' + b.split()[0]:>24}" for a, b in pairs))
    for name in TESTED:
        m = MEASURES.index(name)
        p = [permutation_test(per_pop[a][m], per_pop[b][m], rng) for a, b in pairs]
        print(f"{name:20}" + "".join(f"{format_p(x):>24}" for x in p))

    np.savez_compressed(
        out / "populations_finales.npz",
        **{f"{regime}_{r}": p for regime, pops in finals.items() for r, p in enumerate(pops)},
    )
    np.savez_compressed(out / "par_population.npz", mesures=MEASURES, **per_pop)
    with open(out / "saisons.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "step", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for k in range(series.shape[2]):
                    writer.writerow([regime, r, k * args.every, *series[:, r, k].round(5)])
    suptitle = (
        f"Saisons cachées, réserve doublée — {args.rep} populations par régime : "
        "moyenne, et bande entre quartiles"
    )
    figure(results, null, args.every, out / "saisons.png", suptitle)
    print(f"\nfigure : {out / 'saisons.png'}")


if __name__ == "__main__":
    main()
