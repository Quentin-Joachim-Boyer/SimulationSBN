"""Milieu partagé : survie sans cible, en régime constant, à saisons, ou neutre.

    python experiments/milieu_partage/run.py    # écrit out/milieu_partage.png

Protocole et hypothèses : journal/2026-11-14_milieu-partage.md.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from simsbn.milieu import ARCH, Milieu, live, solitary_viable
from simsbn.structure import KINDS, Classifier, exact_brain_law
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

BOUND = 3
REGIMES = {
    "constant": (Milieu(season=None), BLUE),
    "saisons": (Milieu(season=50), ORANGE),
    "neutre": (Milieu(neutral=True), MUTED),
}
MEASURES = ["effectif", *KINDS, "action_x", "action_y", "servies"]
PANELS = [  # (mesure, titre, indice du modèle nul uniforme ou None)
    ("effectif", "Effectif", None),
    ("servies", "Part des demandes servies", None),
    ("action_x", "Part des pas avec action X", None),
    ("controle_cerveau", "Cerveau seul : part à nœud de contrôle", 0),
    ("scission_sbn", "Part dont la face « capteur = 1 » est un SBN", 2),
    ("controle_interne", "Part à contrôle interne (plus de 2 feuilles PTBN)", 3),
]


def simulate(milieu, classify, pop, steps, replicates, mutation_rate, every, seed, tag):
    series = np.full((len(MEASURES), replicates, steps // every + 1), np.nan)
    finals = []
    for r in range(replicates):
        rng = np.random.default_rng([seed, r, tag])
        start = ARCH.random(rng, pop, BOUND)
        for snap in live(start, milieu, steps, rng, mutation_rate, BOUND, every):
            k = -(-snap.t // every)  # un relevé d'extinction tombe sur le relevé suivant
            n = len(snap.population)
            series[0, r, k] = n
            if n:
                series[1:5, r, k] = classify(snap.population)
                series[5:7, r, k] = snap.act
                series[7, r, k] = snap.served
        finals.append(snap.population)
    return series, finals


def figure(results, null, every, path, suptitle):
    import matplotlib.pyplot as plt

    apply_style()
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), layout="constrained", sharex=True)
    for ax, (measure, title, null_index) in zip(axes.flat, PANELS, strict=True):
        m = MEASURES.index(measure)
        scale = 1 if measure == "effectif" else 100
        for regime, (_, color) in REGIMES.items():
            if regime == "neutre" and measure in ("servies", "action_x"):
                continue  # sans objet : le comportement n'y a aucun effet
            data = scale * results[regime][m]
            t = every * np.arange(data.shape[1])
            for row in data:
                ax.plot(t, row, color=color, linewidth=0.6, alpha=0.15)
            with np.errstate(all="ignore"):
                mean = np.nanmean(data, axis=0)
            ax.plot(t, mean, color=color, linewidth=2, label=f"régime {regime}")
        if null_index is not None:
            ax.axhline(
                100 * null[null_index], color=INK, linewidth=1, linestyle=(0, (4, 3)),
                label="loi uniforme",
            )  # fmt: skip
        ax.set_ylabel("agents vivants" if measure == "effectif" else "%")
        ax.set_ylim(bottom=0)
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
    parser.add_argument("--rep", type=int, default=12)
    parser.add_argument("--mu", type=float, default=0.1, help="mutations par naissance")
    parser.add_argument("--every", type=int, default=100, help="pas entre deux relevés")
    parser.add_argument("--null", type=int, default=20_000, help="taille de l'échantillon nul")
    parser.add_argument("--solitary", type=int, default=200_000, help="génotypes testés seuls")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    classify = Classifier()

    # Modèles nuls : loi uniforme, exacte pour le cerveau seul, estimée pour le reste.
    sample = ARCH.random(np.random.default_rng([args.seed, 999]), args.null, BOUND)
    null = classify(sample)
    exact = exact_brain_law(BOUND)
    null[:2] = exact

    def row(label, v, extra=""):
        print(f"{label:34}" + "".join(f"{100 * x:9.2f}%" for x in v) + extra)

    print(f"{'':34}{'contrôle':>10}{'PSBN':>10}{'scission':>10}{'interne':>10}")
    row("loi uniforme", null)

    # Viabilité en solitaire, sans compétition.
    genotypes = ARCH.random(np.random.default_rng([args.seed, 998]), args.solitary, BOUND)
    for regime in ("constant", "saisons"):
        viable = solitary_viable(genotypes, REGIMES[regime][0])
        label = f"viables seuls, {regime}"
        if viable.any():
            row(label, classify(genotypes[viable]), f"   ({100 * viable.mean():.3f} % viables)")
        else:
            print(f"{label:34} aucun génotype viable sur {args.solitary}")

    results, finals = {}, {}
    for tag, (regime, (milieu, _)) in enumerate(REGIMES.items()):
        results[regime], finals[regime] = simulate(
            milieu, classify, args.pop, args.steps, args.rep, args.mu, args.every, args.seed, tag
        )

    half = args.steps // args.every // 2 + 1
    print()
    print(f"{'seconde moitié, moyenne ± é.-t.':34}" + "".join(f"{m:>18}" for m in MEASURES))
    for regime, series in results.items():
        extinct = int((series[0, :, -1] == 0).sum() + np.isnan(series[0, :, -1]).sum())
        with np.errstate(all="ignore"):
            per_rep = np.nanmean(series[:, :, half:], axis=2)
        mean, sd = np.nanmean(per_rep, axis=1), np.nanstd(per_rep, axis=1)
        cells = [f"{mean[0]:10.0f} ± {sd[0]:<5.0f}"]
        cells += [
            f"{100 * a:9.2f} ± {100 * b:<5.2f}%" for a, b in zip(mean[1:], sd[1:], strict=True)
        ]
        print(
            f"{'régime ' + regime:34}" + "".join(cells) + f"   extinctions : {extinct}/{args.rep}"
        )

    np.savez_compressed(
        out / "populations_finales.npz",
        **{f"{regime}_{r}": p for regime, pops in finals.items() for r, p in enumerate(pops)},
    )
    with open(out / "milieu_partage.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["regime", "replicate", "step", *MEASURES])
        for regime, series in results.items():
            for r in range(args.rep):
                for k in range(series.shape[2]):
                    writer.writerow([regime, r, k * args.every, *series[:, r, k].round(5)])
    suptitle = (
        f"Milieu partagé — {args.rep} populations par régime, moyenne en trait épais ; "
        "aucune cible, la survie seule sélectionne"
    )
    figure(results, null, args.every, out / "milieu_partage.png", suptitle)
    print(f"figure : {out / 'milieu_partage.png'}")


if __name__ == "__main__":
    main()
