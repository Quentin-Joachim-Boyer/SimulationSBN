"""Régimes et populations de départ de l'expérience « monde à déchet ».

Partagé par ``run.py`` (l'expérience) et ``voir.py`` (la visualisation), pour que la
population montrée soit exactement l'une de celles qui ont été mesurées.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import Monde, Vie

BOUND = 3
ESPACE = Monde()  # paramètres figés dans journal/2026-11-14_monde-dechet.md
REGIMES = {
    "mélangé": ESPACE.melange(),
    "espace": ESPACE,
    "neutre": replace(ESPACE, neutral=True),
}


def naissance(regime: str, replicate: int, seed: int = 0, pop: int = 300, mu: float = 0.1) -> Vie:
    """Population numéro ``replicate`` du régime, à son pas 0."""
    rng = np.random.default_rng([seed, replicate, list(REGIMES).index(regime)])
    return Vie(ARCH.random(rng, pop, BOUND), REGIMES[regime], rng, mu, BOUND)
