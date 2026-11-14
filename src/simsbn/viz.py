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
