"""Tâches : ce qu'un environnement demande à un agent piloté par un SBN.

Un contexte fixe l'état initial du réseau (c'est par là que l'environnement parle à
l'agent) et le comportement attendu d'un nœud moteur. Rien n'est maintenu de
l'extérieur après le départ.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from simsbn.core import batch_dynamics


@dataclass(frozen=True)
class Context:
    """Un contexte : état initial, et valeur attendue du moteur à certains pas."""

    start: int
    target: dict[int, int]  # pas (à partir de 1) -> valeur attendue du moteur


def trajectories(population, start: int, steps: int) -> np.ndarray:
    """États visités aux pas ``1..steps`` depuis ``start`` : tableau ``(N, steps)``."""
    tables = batch_dynamics(population)  # (N, d)
    n, d = tables.shape
    shifts = np.arange(d, dtype=np.uint64)
    state = np.full(n, start, dtype=np.uint64)
    out = np.empty((n, steps), dtype=np.int64)
    for t in range(steps):
        bits = (tables >> state[:, None]) & np.uint64(1)
        state = (bits << shifts).sum(axis=1, dtype=np.uint64)
        out[:, t] = state
    return out


def score(population, context: Context, motor: int) -> np.ndarray:
    """Part des pas évalués où le moteur a la valeur attendue, par individu."""
    steps = sorted(context.target)
    states = trajectories(population, context.start, steps[-1])
    values = (states[:, [t - 1 for t in steps]] >> motor) & 1
    return (values == np.array([context.target[t] for t in steps])).mean(axis=1)
