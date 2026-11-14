"""Structure et dynamique d'un SBN (implémentation de référence, NumPy)."""

from __future__ import annotations

import numpy as np


def state_bits(d: int) -> np.ndarray:
    """Matrice ``(2^d, d)`` dont la ligne ``s`` contient les bits de l'état ``s``."""
    s = np.arange(1 << d)[:, None]
    return (s >> np.arange(d)[None, :]) & 1


def column_table(col) -> int:
    """Table de vérité de la fonction à seuil de poids entrants ``col``.

    ``f(x) = 1`` si et seulement si la somme des poids des nœuds actifs est
    strictement positive.
    """
    col = np.asarray(col)
    active = state_bits(len(col)) @ col > 0
    return sum(1 << s for s in np.flatnonzero(active).tolist())


def dynamics(W) -> tuple[int, ...]:
    """Dynamique ``(f_0, ..., f_{d-1})`` du réseau de matrice de poids ``W``."""
    W = _square(W)
    return tuple(column_table(W[:, j]) for j in range(W.shape[0]))


def batch_dynamics(population) -> np.ndarray:
    """Dynamiques d'une population ``(N, d, d)`` : tableau ``(N, d)`` de tables de vérité.

    Version vectorisée de :func:`dynamics`, limitée à ``d <= 5`` (tables sur 64 bits).
    """
    population = np.asarray(population)
    d = population.shape[-1]
    if d > 5:
        raise ValueError("batch_dynamics est limité à d <= 5")
    active = np.einsum("si,nij->njs", state_bits(d), population) > 0  # (N, nœud, état)
    return active.astype(np.uint64) @ (np.uint64(1) << np.arange(1 << d, dtype=np.uint64))


def transition(W) -> np.ndarray:
    """Fonction de transition : tableau ``F`` de taille ``2^d`` où ``F[s]`` suit ``s``."""
    W = _square(W)
    d = W.shape[0]
    nxt = (state_bits(d) @ W > 0).astype(np.int64)
    return nxt @ (1 << np.arange(d))


def attractors(F) -> list[tuple[int, ...]]:
    """Attracteurs d'une fonction de transition, chacun comme cycle d'états.

    Chaque cycle commence par son plus petit état, et les cycles sont triés.
    """
    F = [int(v) for v in F]
    seen: dict[int, int] = {}  # état -> numéro de la trajectoire qui l'a visité
    cycles = []
    for start in range(len(F)):
        s = start
        while s not in seen:
            seen[s] = start
            s = F[s]
        if seen[s] == start:  # la trajectoire s'est refermée sur elle-même
            cycle = [s]
            t = F[s]
            while t != s:
                cycle.append(t)
                t = F[t]
            k = cycle.index(min(cycle))
            cycles.append(tuple(cycle[k:] + cycle[:k]))
    return sorted(cycles)


def _square(W) -> np.ndarray:
    W = np.asarray(W)
    if W.ndim != 2 or W.shape[0] != W.shape[1]:
        raise ValueError(f"matrice de poids carrée attendue, reçu {W.shape}")
    return W
