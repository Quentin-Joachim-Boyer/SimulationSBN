"""Quatre directions absolues et « ingérer » : un cerveau qui doit retenir un cap.

    python experiments/directions/run.py    # écrit out/directions.png

Même monde que experiments/monde_dechet. Protocole et hypothèses :
journal/2026-11-15_directions-absolues.md.
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
from simsbn.suivi import MEASURES, brains, par_population, suivre
from simsbn.viz import INK, MUTED, ORANGE, apply_style

HERE = Path(__file__).parent
BOUND = 3
ESPACE = Monde()  # paramètres figés dans journal/2026-11-14_monde-dechet.md
MOTORS = ("ingérer", "nord", "sud", "est", "ouest")
CORPS = Corps(MOTORS, ticks=2)
REGIMES = {  # nom : (monde, couleur)
    "directions": (ESPACE, ORANGE),
    "neutre": (replace(ESPACE, neutral=True), MUTED),
}
SHOWN = ["effectif", "naissances", "bouger_0", "bouger_1", "dependance", "persistance",
         "manger_0", "manger_1", "servies", "empoisonnees", *KINDS]  # fmt: skip
TESTED = ["dependance", "persistance", *KINDS]
PANELS = [  # (mesure, titre, unité, nom de la loi uniforme ou None)
    ("effectif", "Effectif", "agents vivants", None),
    ("persistance", "Persistance du déplacement", "cosinus", None),
    ("dependance", "Dépendance au capteur", "points", None),
    ("pc1_po2_poids", "PC de 1 nœud (poids)", "%", "pc1_po2_poids"),
    ("pc2_po1_poids", "PC de 2 nœuds (poids)", "%", "pc2_po1_poids"),
    ("controle_cerveau", "PTBN (nœud de contrôle)", "%", "controle_cerveau"),
]
_classify = Classifier()  # un par processus


def one_population(task):
    regime, r, pop, steps, mu, every, seed = task
    monde = REGIMES[regime][0]
    rng = np.random.default_rng([seed, r, list(REGIMES).index(regime), 6])
    vie = Vie(CORPS.arch.random(rng, pop, BOUND), monde, rng, mu, BOUND, CORPS)
    return regime, r, suivre(vie, steps, every, _classify, ESPACE.cells), vie.population


def figure(results, null, every, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    for ax, (measure, title, unit, law) in zip(axes.flat, PANELS, strict=True):
        m = MEASURES.index(measure)
        scale = 100 if unit in ("%", "points") else 1
        for regime, (_, color) in REGIMES.items():
            data = scale * results[regime][m]
            t = every * np.arange(data.shape[1])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                mean = np.nanmean(data, axis=0)
                low, high = np.nanpercentile(data, [25, 75], axis=0)
            ax.fill_between(t, low, high, color=color, alpha=0.08, linewidth=0)
            ax.plot(t, mean, color=color, linewidth=2, label=f"régime {regime}")
        if law is not None:
            ax.axhline(100 * null[KINDS.index(law)], color=INK, linewidth=1,
                       linestyle=(0, (1, 2)), label="loi uniforme")  # fmt: skip
        if measure in ("dependance", "persistance"):
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
    sample = CORPS.arch.random(np.random.default_rng([args.seed, 999]), args.null, BOUND)
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

    print("seconde moitié, moyenne ± écart-type entre populations (en %, sauf effectif,")
    print("naissances et persistance, qui est un cosinus)")
    print(f"{'':18}" + "".join(f"{regime:>19}" for regime in REGIMES) + f"{'uniforme':>10}")
    for name in SHOWN:
        m = MEASURES.index(name)
        scale = 1 if name in ("effectif", "naissances", "persistance") else 100
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
    print("\ntest par permutation, directions contre neutre (valeur p bilatérale)")
    for name in TESTED:
        m = MEASURES.index(name)
        p = permutation_test(per_pop["directions"][m], per_pop["neutre"][m], rng)
        print(f"   {name:18}{format_p(p):>10}")

    reference = HERE.parent / "rythme" / "out" / "par_population.npz"
    if reference.exists():
        print("\ndirections contre le régime à deux moteurs « bouger » (rythme, k = 2)")
        ref = np.load(reference, allow_pickle=True)
        names = list(ref["mesures"])
        for name in TESTED:
            if name not in names:
                continue  # la persistance n'existait pas encore
            before = ref["k = 2"][names.index(name)]
            p = permutation_test(per_pop["directions"][MEASURES.index(name)], before, rng)
            print(f"   {name:18}{100 * np.nanmean(before):8.1f} % avant   p {format_p(p, True)}")
    else:
        print("\n(repère à deux moteurs non comparé : lancer d'abord experiments/rythme/run.py)")

    np.savez_compressed(
        out / "populations_finales.npz",
        **{f"{regime}_{r}": p for regime, pops in finals.items() for r, p in enumerate(pops)},
    )
    np.savez_compressed(out / "par_population.npz", mesures=MEASURES, **per_pop)
    with open(out / "directions.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "step", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for k in range(series.shape[2]):
                    writer.writerow([regime, r, k * args.every, *series[:, r, k].round(5)])
    suptitle = (
        f"Quatre directions absolues — {args.rep} populations par régime : "
        "moyenne, et bande entre quartiles"
    )
    figure(results, null, args.every, out / "directions.png", suptitle)
    print(f"\nfigure : {out / 'directions.png'}")


if __name__ == "__main__":
    main()
