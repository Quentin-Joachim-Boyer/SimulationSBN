"""Pluripotence : nœuds de contrôle et décomposition d'un SBN.

Deux niveaux de lecture, à ne pas confondre :

- sur les **poids** (génotype) : :func:`is_control_node`, critère du rapport de
  Danwen Wu, en ``O(d)`` et donc utilisable en toute dimension ;
- sur la **dynamique** (phénotype) : :func:`control_nodes`, :func:`is_psbn`,
  :func:`decomposition`, qui parcourent les ``2^d`` états.

Pour un nœud de contrôle de l'hypercube entier, les deux lectures coïncident.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np

from simsbn.sbf import projection, restrict, sbf_tables

Dynamics = tuple[int, ...]


def is_control_node(W, c: int) -> bool:
    """Vrai si ``c`` garde toujours sa valeur, lu sur les poids.

    Aucun autre nœud ne peut l'allumer (arcs entrants inhibiteurs ou absents) ni
    l'éteindre (sa boucle l'emporte sur toutes les inhibitions réunies).
    """
    W = np.asarray(W)
    others = np.delete(W[:, c], c)
    return bool(np.maximum(others, 0).sum() <= 0 and W[c, c] + np.minimum(others, 0).sum() > 0)


def control_nodes(f: Dynamics) -> list[int]:
    """Nœuds de contrôle d'une dynamique : ceux dont la fonction est ``x -> x_c``."""
    d = len(f)
    return [c for c in range(d) if f[c] == projection(d, c)]


def is_psbn(f: Dynamics) -> bool:
    """Vrai si la dynamique se décompose en SBN selon au moins un nœud de contrôle.

    Il faut un nœud de contrôle ``c`` tel que, sur la face ``x_c = 1``, la fonction
    de chaque autre nœud soit encore une SBF (la face ``x_c = 0`` en est toujours un).
    """
    d = len(f)
    sub = sbf_tables(d - 1)
    return any(
        all(restrict(f[j], d, c, 1) in sub for j in range(d) if j != c) for c in control_nodes(f)
    )


def count_psbn(d: int) -> int:
    """Nombre exact de dynamiques de dimension ``d`` décomposables en SBN.

    Les colonnes étant indépendantes, on compte sans énumérer les dynamiques, par
    inclusion-exclusion sur l'ensemble ``S`` des nœuds de contrôle imposés.
    """
    tables = sbf_tables(d)
    sub = sbf_tables(d - 1)
    # ok[c] : SBF dont la restriction à la face x_c = 1 est encore une SBF.
    ok = [{tt for tt in tables if restrict(tt, d, c, 1) in sub} for c in range(d)]
    total = 0
    for size in range(1, d + 1):
        for S in combinations(range(d), size):
            compatible = len(set.intersection(*(ok[c] for c in S)))
            total += (-1) ** (size + 1) * compatible ** (d - size)
    return total


def decomposition(f: Dynamics, mode: str = "sbn") -> tuple[int, ...]:
    """Vecteur de décomposition le plus fin ``(v_d, ..., v_0)`` d'une dynamique.

    ``v_k`` est le nombre de feuilles de dimension ``k`` de l'arbre dont chaque nœud
    interne coupe une face selon un nœud de contrôle (invariant sur cette face).

    - ``mode="sbn"`` (PSBN) : une face n'entre dans l'arbre que si la fonction
      restreinte de chacun de ses nœuds libres est une SBF ;
    - ``mode="tbn"`` (PTBN) : toute face est admise, car fixer des entrées ne fait
      qu'ajouter un seuil.

    Le plus fin maximise le nombre de feuilles, puis les feuilles de basse dimension.
    """
    if mode not in ("sbn", "tbn"):
        raise ValueError("mode doit valoir 'sbn' ou 'tbn'")
    d = len(f)
    memo: dict[tuple[int, int], tuple[int, ...] | None] = {}

    def face_tables(fixed: int, values: int) -> tuple[list[int], list[int]]:
        free = [i for i in range(d) if not (fixed >> i) & 1]
        states = []
        for t in range(1 << len(free)):
            s = values
            for k, i in enumerate(free):
                s |= ((t >> k) & 1) << i
            states.append(s)
        return free, states

    def rec(fixed: int, values: int) -> tuple[int, ...] | None:
        key = (fixed, values)
        if key in memo:
            return memo[key]
        free, states = face_tables(fixed, values)
        k = len(free)
        if mode == "sbn":
            sub = sbf_tables(k)
            for j in free:
                tt = sum(((f[j] >> s) & 1) << t for t, s in enumerate(states))
                if tt not in sub:
                    memo[key] = None
                    return None
        best = tuple(1 if dim == k else 0 for dim in range(d, -1, -1))
        for c in free:
            if any(((f[c] >> s) & 1) != ((s >> c) & 1) for s in states):
                continue
            d0 = rec(fixed | (1 << c), values)
            d1 = rec(fixed | (1 << c), values | (1 << c))
            if d0 is None or d1 is None:
                continue
            cand = tuple(a + b for a, b in zip(d0, d1, strict=True))
            if _finer(cand, best):
                best = cand
        memo[key] = best
        return best

    result = rec(0, 0)
    assert result is not None  # l'hypercube entier est toujours un SBN
    return result


def _finer(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    if sum(a) != sum(b):
        return sum(a) > sum(b)
    return a[::-1] > b[::-1]  # davantage de feuilles de basse dimension
