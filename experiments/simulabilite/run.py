"""Table de simulabilité : quelles paires de cibles un cerveau de dimension 3 simule-t-il ?

    python experiments/simulabilite/run.py   # écrit experiments/simulabilite/out/

Calcul exhaustif sur les 370^3 dynamiques composites, pondérées par leur nombre de
génotypes. Définitions et prédictions : journal/2026-11-14_simulabilite.md.
"""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from simsbn import sbf_counts, sbf_tables
from simsbn.sbf import restrict
from simsbn.simulability import simulated_target, target_code
from simsbn.viz import GRID, INK, MUTED, SURFACE, apply_style

N, P = 3, 2  # nœuds du cerveau, dont visibles
NAMES = {0b0000: "0", 0b1010: "a", 0b1100: "b", 0b1110: "a∨b", 0b0010: "a∧¬b", 0b0100: "b∧¬a"}


def column_types():
    """Types de colonnes du composite : paire (fonction en A, fonction en B) et effectif."""
    counts = sbf_counts(N + 1)
    tts = np.array(list(counts))
    in_a = np.array([restrict(t, N + 1, 0, 0) for t in tts.tolist()])
    in_b = np.array([restrict(t, N + 1, 0, 1) for t in tts.tolist()])
    return in_a, in_b, np.array([counts[t] for t in tts.tolist()], dtype=np.float64)


def target_of_triples(functions):
    """Cible simulée par chaque triplet de fonctions : tableau ``(K, K, K)``."""
    k = len(functions)
    triples = np.array(list(product(functions.tolist(), repeat=N)))
    return simulated_target(triples, N, P).reshape(k, k, k)


def independent_of_hidden(tt):
    """Vrai si la fonction (table sur 8 états) ne dépend pas du nœud caché."""
    return (tt & 0b1111) == (tt >> 4)


def main():
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    in_a, in_b, weight = column_types()
    fa, ia = np.unique(in_a, return_inverse=True)
    fb, ib = np.unique(in_b, return_inverse=True)
    target_a, target_b = target_of_triples(fa), target_of_triples(fb)

    sbf3 = set(sbf_tables(N))
    is_sbf_in_b = np.array([t in sbf3 for t in in_b.tolist()])
    strict = independent_of_hidden(in_a) & independent_of_hidden(in_b)

    targets = [(a, b) for a in NAMES for b in NAMES]  # les 36 cibles SBN, f_1 puis f_2
    index = {target_code(t): i for i, t in enumerate(targets)}
    lookup = np.full(257, -1)
    for code, i in index.items():
        lookup[code] = i

    total = np.zeros((36, 36))
    psbn = np.zeros((36, 36))
    strict_total = np.zeros((36, 36))
    all_pairs: set[tuple[int, int]] = set()  # toutes cibles confondues, SBN ou non
    summary = dict.fromkeys(["tous", "incohérents", "cible B non SBN", "paire de cibles SBN"], 0.0)
    for c1 in range(len(weight)):  # un nœud visible fixé, les deux autres par diffusion
        ta = target_a[ia[c1]][np.ix_(ia, ia)]
        tb = target_b[ib[c1]][np.ix_(ib, ib)]
        w = weight[c1] * np.outer(weight, weight)
        a, b = lookup[ta], lookup[tb]  # -1 : incohérent ou cible hors SBN
        ok = (a >= 0) & (b >= 0)
        coherent = (ta >= 0) & (tb >= 0)
        all_pairs |= set(zip(ta[coherent].tolist(), tb[coherent].tolist(), strict=True))
        summary["tous"] += w.sum()
        summary["incohérents"] += w[(ta < 0) | (tb < 0)].sum()
        summary["cible B non SBN"] += w[(ta >= 0) & (tb >= 0) & (b < 0)].sum()
        summary["paire de cibles SBN"] += w[ok].sum()
        key = (a * 36 + b)[ok]
        total += np.bincount(key, w[ok], 36 * 36).reshape(36, 36)
        all_sbf = is_sbf_in_b[c1] & np.logical_and.outer(is_sbf_in_b, is_sbf_in_b)
        psbn += np.bincount(key, (w * all_sbf)[ok], 36 * 36).reshape(36, 36)
        # strict : les deux nœuds visibles (c1 et le suivant) ignorent le nœud caché
        visible_strict = strict[c1] & np.broadcast_to(strict[:, None], w.shape)
        strict_total += np.bincount(key, (w * visible_strict)[ok], 36 * 36).reshape(36, 36)

    labels = [f"{NAMES[a]} , {NAMES[b]}" for a, b in targets]
    with open(out / "simulabilite.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cible_A", "cible_B", "genotypes", "part_psbn", "part_stricte"])
        for i, j in product(range(36), repeat=2):
            n = total[i, j]
            shares = [psbn[i, j] / n, strict_total[i, j] / n] if n else ["", ""]
            writer.writerow([labels[i], labels[j], int(n), *shares])

    plot(total, psbn, labels, out / "simulabilite.png")

    possible = total > 0
    print(f"génotypes composites           : {summary['tous']:.4g}")
    for key in ("incohérents", "cible B non SBN", "paire de cibles SBN"):
        print(f"  {key:28} : {100 * summary[key] / summary['tous']:.2f} %")
    print(f"paires simulables              : {possible.sum()} sur {possible.size}")
    print(f"  dont sans aucune solution PSBN   : {(possible & (psbn == 0)).sum()}")
    print(f"  dont sans aucune solution stricte: {(possible & (strict_total == 0)).sum()}")
    print(f"part PSBN des solutions        : {100 * psbn.sum() / total.sum():.2f} %")
    print(f"part stricte des solutions     : {100 * strict_total.sum() / total.sum():.2f} %")
    off = ~np.eye(36, dtype=bool)
    print(f"paires A ≠ B simulables        : {(possible & off).sum()} sur {off.sum()}")
    print(f"  part PSBN (A ≠ B)            : {100 * psbn[off].sum() / total[off].sum():.2f} %")
    print(
        f"  part stricte (A ≠ B)         : {100 * strict_total[off].sum() / total[off].sum():.2f} %"
    )
    # Un nœud visible, vu seul : paires (fonction en A, fonction en B) rencontrées,
    # comparées à celles d'une SBF de dimension 3 dont une entrée serait le contexte.
    per_node = {(node_function(a, 0), node_function(b, 0)) for a, b in all_pairs}
    direct = {(restrict(t, 3, 0, 0), restrict(t, 3, 0, 1)) for t in sbf_tables(3)}
    product_size = len(per_node) ** 2
    print(f"paires simulables, toutes cibles : {len(all_pairs)}")
    print(f"  paires par nœud visible        : {len(per_node)} (produit : {product_size})")
    print(f"  identiques à celles d'un nœud sans nœud caché : {per_node == direct}")
    print(f"figure : {out / 'simulabilite.png'}")


def node_function(code, node):
    """Table de vérité (sur les 4 états visibles) d'un nœud d'une cible codée."""
    return sum(((code >> (P * v + node)) & 1) << v for v in range(1 << P))


def plot(total, psbn, labels, path):
    apply_style()
    plt.rcParams["axes.grid"] = False
    blues = LinearSegmentedColormap.from_list("blues", ["#dbe9f9", "#2a78d6", "#0d2f5c"])
    blues.set_bad(SURFACE)
    fig, axes = plt.subplots(1, 2, figsize=(15, 8.2), layout="constrained", sharey=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        panels = [
            (np.where(total > 0, np.log10(total), np.nan),
             "Nombre de génotypes qui simulent la paire", "log₁₀ du nombre de génotypes"),
            (np.where(total > 0, 100 * psbn / total, np.nan),
             "Part de ces génotypes qui sont des PSBN", "% des solutions"),
        ]  # fmt: skip
    for ax, (data, title, legend) in zip(axes, panels, strict=True):
        image = ax.imshow(np.ma.masked_invalid(data), cmap=blues)
        ax.set_title(title)
        ax.set_xticks(range(36), labels, rotation=90, fontsize=7)
        ax.set_yticks(range(36), labels, fontsize=7)
        ax.set_xlabel("cible du contexte B (f₁ , f₂)")
        ax.set_xticks(np.arange(-0.5, 36), minor=True)
        ax.set_yticks(np.arange(-0.5, 36), minor=True)
        ax.grid(which="minor", color=SURFACE, linewidth=1)
        ax.tick_params(which="minor", length=0)
        for side in ax.spines.values():
            side.set_visible(False)
        bar = fig.colorbar(image, ax=ax, shrink=0.6, pad=0.02)
        bar.set_label(legend, color=MUTED)
        bar.outline.set_edgecolor(GRID)
    axes[0].set_ylabel("cible du contexte A (f₁ , f₂)")
    fig.suptitle(
        "Paires de cibles simulées par un cerveau de dimension 3 — case vide : aucune solution",
        x=0.01, ha="left", color=INK, fontsize=12,
    )  # fmt: skip
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
