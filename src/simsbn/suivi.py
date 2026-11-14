"""Relevés d'une population qui vit dans un monde : démographie, comportement, structure."""

from __future__ import annotations

import warnings

import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import Vie
from simsbn.structure import KINDS, Classifier

ACTIVITY = [
    "naissances", "manger_0", "manger_1", "bouger_0", "bouger_1", "dependance", "capteur",
    "servies", "empoisonnees",
]  # fmt: skip
MEASURES = ["effectif", *ACTIVITY, "dechet", *KINDS]


def brains(population: np.ndarray) -> np.ndarray:
    """Capteur et cerveau de chaque agent, sans ses éventuels moteurs : ``(N, 4, 4)``."""
    return population[:, : ARCH.d, : ARCH.d]


def suivre(vie: Vie, steps: int, every: int, classify: Classifier, cells: int) -> np.ndarray:
    """Fait vivre ``vie`` pendant ``steps`` pas et relève ``MEASURES`` tous les ``every`` pas.

    Renvoie un tableau ``(len(MEASURES), steps // every + 1)`` ; après une extinction,
    seul l'effectif (nul) est noté. Le déchet est rapporté à ``cells`` cases, pour
    comparer un monde réduit à une case au monde dont il garde les totaux.
    """
    series = np.full((len(MEASURES), steps // every + 1), np.nan)
    series[0, 0] = len(vie)
    series[-len(KINDS) :, 0] = classify(brains(vie.population))
    for k in range(1, steps // every + 1):
        for _ in range(every):
            vie.step()
            if not len(vie):
                break
        series[0, k] = len(vie)
        if not len(vie):
            break
        stats = vie.stats()
        series[1 : 1 + len(ACTIVITY), k] = [stats[name] for name in ACTIVITY]
        if vie.monde.neutral:  # sans objet : la nourriture n'y dépend pas des demandes
            series[MEASURES.index("servies"), k] = np.nan
        series[MEASURES.index("dechet"), k] = vie.waste.sum() / cells
        series[-len(KINDS) :, k] = classify(brains(vie.population))
    return series


def par_population(series: np.ndarray, extinct) -> np.ndarray:
    """Une valeur par mesure et par population : moyenne des relevés de la seconde moitié.

    ``series`` est ``(mesures, populations, relevés)``. Une population éteinte ne garde
    que son effectif.
    """
    half = (series.shape[2] - 1) // 2 + 1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # relevés sans aucune valeur
        out = np.nanmean(series[:, :, half:], axis=2)
    out[1:, np.asarray(extinct, dtype=bool)] = np.nan
    return out
