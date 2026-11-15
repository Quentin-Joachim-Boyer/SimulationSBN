"""Dessine des agents de l'expérience rythme comme des graphes : capteur, cerveau, moteurs.

    python experiments/rythme/graphes.py [--regime "k = 2"]    # écrit out/graphes.png

Pour chaque population finale, on prend le génotype le plus répandu. Rangée du haut : les
populations de plus forte, médiane et plus faible dépendance au capteur. Rangée du bas :
génotypes dominants qui ont une décomposition partie contrôle / partie opérative lue
sur les poids (nœud du cerveau qui ne lit aucun autre nœud, ou que nul autre ne lit).
Pas un résultat : un moyen de regarder ce que l'évolution a fabriqué.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

from simsbn.structure import structural_parts
from simsbn.suivi import MEASURES
from simsbn.viz import BLUE, INK, MUTED, ORANGE, apply_style

HERE = Path(__file__).parent / "out"
MOTORS = ("ingérer", "bouger")
POS = {  # nœud -> (x, y) : capteur à gauche, cerveau au centre, moteurs à droite
    0: (0.0, 1.0),
    1: (2.0, 2.1), 2: (2.0, -0.1), 3: (3.7, 1.0),
    4: (5.6, 1.7), 5: (5.6, 0.3),
}  # fmt: skip
GREEN = "#2a9d6f"
RED = "#c0392b"


def dominant(population: np.ndarray) -> tuple[np.ndarray, float]:
    """Génotype le plus répandu et sa part."""
    flat = population.reshape(len(population), -1)
    genotypes, counts = np.unique(flat, axis=0, return_counts=True)
    top = counts.argmax()
    return genotypes[top].reshape(population.shape[1:]), counts[top] / len(population)


def draw(ax, W: np.ndarray, title: str) -> None:
    n_in, d = 1, W.shape[0]
    ax.set_xlim(-0.8, 6.9)
    ax.set_ylim(-0.8, 3.2)
    ax.set_aspect("equal")
    ax.axis("off")
    parts = structural_parts(W[None])[0]  # (PC de 1 nœud, PO de 1 nœud)
    off = ~np.eye(3, dtype=bool)
    nonzero = (W[1:4, 1:4] != 0) & off
    # nonzero[i, j] : arc i -> j. Partie contrôle : aucun arc entrant venant des autres
    # nœuds (colonne nulle). Partie opérative : aucun arc sortant vers eux (ligne nulle).
    pc = [i for i in range(3) if not nonzero[:, i].any()] if parts[0] else []
    po = [i for i in range(3) if not nonzero[i].any()] if parts[1] else []
    for x0, x1, name in ((-0.6, 0.6, "capteur"), (1.2, 4.5, "cerveau"), (5.1, 6.6, "moteurs")):
        ax.text((x0 + x1) / 2, 2.85, name, ha="center", va="bottom", color=MUTED, fontsize=10)
        ax.plot([x0, x1], [2.8, 2.8], color=MUTED, linewidth=0.8)
    arcs = [(i, j) for i in range(n_in) for j in range(n_in, d - len(MOTORS))]
    arcs += [(i, j) for i in range(n_in, d - len(MOTORS)) for j in range(n_in, d)]
    for i, j in arcs:
        w = int(W[i, j])
        if w == 0:
            continue
        color, style = (GREEN, "-") if w > 0 else (RED, (0, (4, 2)))
        (x0, y0), (x1, y1) = POS[i], POS[j]
        if i == j:
            ax.add_patch(Circle((x0, y0 + 0.5), 0.2, fill=False, color=color, linestyle=style,
                                linewidth=0.8 + 0.7 * abs(w)))  # fmt: skip
            ax.text(x0, y0 + 0.66, f"{w:+d}", ha="center", va="bottom", color=color, fontsize=9)
            continue
        arrow = FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11, color=color,
            linestyle=style, linewidth=0.8 + 0.7 * abs(w), shrinkA=15, shrinkB=15,
            connectionstyle="arc3,rad=0.3", zorder=2,
        )  # fmt: skip
        ax.add_patch(arrow)
        # milieu de la courbe d'arc3 : milieu du segment + moitié du décalage du point de contrôle
        mx = (x0 + x1) / 2 + 0.5 * 0.3 * (y1 - y0)
        my = (y0 + y1) / 2 - 0.5 * 0.3 * (x1 - x0)
        box = {"facecolor": "white", "edgecolor": "none", "pad": 0.6, "alpha": 0.85}
        ax.text(mx, my, f"{w:+d}", color=color, fontsize=9, ha="center", va="center",
                zorder=5, bbox=box)  # fmt: skip
    for k, (x, y) in POS.items():
        if k == 0:
            face, label = MUTED, ""
            ax.text(x, y - 0.5, "capteur", ha="center", va="top", color=INK, fontsize=10)
        elif k <= 3:
            face, label = BLUE, f"c{k}"
        else:
            face, label = ORANGE, MOTORS[k - 4]
        ring = INK if (k - 1 in pc or k - 1 in po) and 1 <= k <= 3 else "white"
        ax.add_patch(Circle((x, y), 0.3, facecolor=face, edgecolor=ring, linewidth=2.2, zorder=3))
        ax.text(x, y, label if k < 4 else "", ha="center", va="center", color="white",
                fontsize=9, zorder=4)  # fmt: skip
        if k >= 4:
            ax.text(x + 0.45, y, label, ha="left", va="center", color=INK, fontsize=10)
    notes = []
    if pc:
        notes.append("partie contrôle de 1 nœud : " + ", ".join(f"c{i + 1}" for i in pc))
    if po:
        notes.append("partie opérative de 1 nœud : " + ", ".join(f"c{i + 1}" for i in po))
    ax.set_title(title + ("\n" + " ; ".join(notes) if notes else ""), fontsize=10, color=INK, pad=8)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--regime", default="k = 2")
    args = parser.parse_args()
    reps = [int(k.rsplit("_", 1)[1]) for k in np.load(HERE / "populations_finales.npz").files
            if k.rsplit("_", 1)[0] == args.regime]  # fmt: skip
    finals = np.load(HERE / "populations_finales.npz")
    per_pop = np.load(HERE / "par_population.npz", allow_pickle=True)
    dep = per_pop[args.regime][MEASURES.index("dependance")]
    order = np.argsort(dep)
    top = [int(order[-1]), int(order[len(order) // 2]), int(order[0])]
    panels = []
    for r in top:
        p = finals[f"{args.regime}_{r}"]
        W, share = dominant(p)
        panels.append((W, f"population {r} : dépendance {100 * dep[r]:+.0f} points, "
                          f"génotype à {100 * share:.0f} %"))  # fmt: skip
    for r in reps:
        if len(panels) >= 6:
            break
        p = finals[f"{args.regime}_{r}"]
        W, share = dominant(p)
        if structural_parts(W[None])[0].any() and r not in top:
            panels.append((W, f"population {r} : génotype à {100 * share:.0f} %"))

    import matplotlib.pyplot as plt

    apply_style()
    rows = 2 if len(panels) > 3 else 1
    fig, axes = plt.subplots(
        rows, 3, figsize=(16, 4.4 * rows + 0.5), layout="constrained", squeeze=False
    )
    for ax in axes.flat:
        ax.axis("off")
    for ax, (W, title) in zip(axes.flat, panels, strict=False):
        draw(ax, W, title)
    fig.suptitle(
        f"Agents du régime {args.regime} : poids vert plein > 0, rouge pointillé < 0 ; "
        "contour noir : nœud d'une décomposition partie contrôle / partie opérative",
        x=0.01, ha="left", color=INK, fontsize=11,
    )  # fmt: skip
    path = HERE / "graphes.png"
    fig.savefig(path, dpi=140)
    print(f"{len(panels)} agents dessinés : {path}")


if __name__ == "__main__":
    main()
