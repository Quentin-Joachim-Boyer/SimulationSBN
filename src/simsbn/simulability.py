"""Simulation d'une cible par un cerveau : quelle dynamique les nœuds visibles suivent-ils ?

Le cerveau a ``n`` nœuds, dont les ``p`` premiers sont visibles. Il simule une cible
``T`` (une application sur les ``2^p`` états visibles) si, depuis chaque état visible
avec les nœuds cachés éteints, les nœuds visibles suivent pour toujours la trajectoire
de ``T``.
"""

from __future__ import annotations

import numpy as np


def brain_transition(tables: np.ndarray, n: int) -> np.ndarray:
    """Transitions ``(N, 2^n)`` à partir des tables de vérité ``(N, n)`` des nœuds."""
    tables = np.asarray(tables, dtype=np.int64)
    states = np.arange(1 << n)
    bits = (tables[:, :, None] >> states[None, None, :]) & 1  # (N, nœud, état)
    return np.einsum("njs,j->ns", bits, 1 << np.arange(n))


def simulated_target(tables: np.ndarray, n: int, p: int) -> np.ndarray:
    """Cible simulée par chaque cerveau, ou ``-1`` s'il n'en simule aucune.

    La cible est codée par l'entier ``sum(T(v) << (p * v))``. Elle est donnée par le
    premier pas depuis les états visibles ; le cerveau la simule si tous les états
    atteints ensuite respectent la même règle.
    """
    F = brain_transition(tables, n)
    count = F.shape[0]
    visible_mask = (1 << p) - 1
    rows = np.arange(count)
    starts = np.arange(1 << p)
    rule = F[:, starts] & visible_mask  # (N, 2^p) : T(v)
    reached = np.zeros((count, 1 << n), dtype=bool)
    reached[:, starts] = True
    for _ in range(1 << n):  # fermeture de l'ensemble des états atteints
        nxt = np.zeros_like(reached)
        for s in range(1 << n):
            nxt[rows, F[:, s]] |= reached[:, s]
        grown = reached | nxt
        if (grown == reached).all():
            break
        reached = grown
    states = np.arange(1 << n)
    expected = rule[:, states & visible_mask]  # T(partie visible de s)
    consistent = ((F & visible_mask) == expected) | ~reached
    code = (rule << (p * starts)).sum(axis=1)
    return np.where(consistent.all(axis=1), code, -1)


def target_code(target_tables: tuple[int, ...]) -> int:
    """Code d'une cible donnée comme dynamique ``(t_0, ..., t_{p-1})`` sur ``p`` nœuds."""
    p = len(target_tables)
    code = 0
    for v in range(1 << p):
        nxt = sum(((t >> v) & 1) << j for j, t in enumerate(target_tables))
        code |= nxt << (p * v)
    return code
