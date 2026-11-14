"""Style commun des figures (matplotlib, installé par l'extra ``viz``)."""

from __future__ import annotations

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"


def apply_style() -> None:
    """Règle matplotlib : fond clair, axes et grille discrets."""
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.size": 10,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": GRID,
            "axes.labelcolor": MUTED,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "xtick.minor.size": 0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlelocation": "left",
            "axes.titleweight": "bold",
            "axes.titlecolor": INK,
            "legend.frameon": False,
            "legend.labelcolor": MUTED,
        }
    )


def regime_panels(results, titles, null, path, suptitle, colors=None) -> None:
    """Figure à quatre panneaux comparant des régimes au cours des générations.

    ``results[régime]`` est un tableau ``(4, réplicats, générations)``. Les deux
    premières mesures sont des parts de la population, comparées à ``null`` (deux
    valeurs entre 0 et 1) ; les deux dernières sont des scores entre 0 et 1.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    apply_style()
    colors = colors or dict(zip(results, (BLUE, ORANGE), strict=False))
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), layout="constrained", sharex=True)
    for k, (ax, title) in enumerate(zip(axes.flat, titles, strict=True)):
        scale = 100 if k < 2 else 1
        for regime, color in colors.items():
            data = scale * results[regime][k]
            generations = np.arange(data.shape[1])
            for row in data:
                ax.plot(generations, row, color=color, linewidth=0.6, alpha=0.15)
            ax.plot(generations, data.mean(axis=0), color=color, linewidth=2, label=regime)
        if k < 2:
            ax.axhline(
                100 * null[k], color=INK, linewidth=1, linestyle=(0, (4, 3)), label="modèle nul"
            )
            ax.set_ylabel("% de la population")
            ax.set_ylim(bottom=0)
        else:
            ax.set_ylim(0, 1.02)
            ax.set_xlabel("génération")
        ax.set_title(title)
    axes[0, 0].legend(loc="upper right", ncols=3)
    fig.suptitle(suptitle, x=0.01, ha="left", color=INK, fontsize=12)
    fig.savefig(path, dpi=160)
    plt.close(fig)
