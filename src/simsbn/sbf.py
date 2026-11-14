"""Fonctions booléennes à seuil signées (SBF) : énumération par dimension."""

from __future__ import annotations

from functools import cache
from itertools import product

import numpy as np

from simsbn.core import state_bits

# Plus petit entier B_d tel que toute SBF de dimension d se réalise avec des poids
# dans [-B_d, B_d] (rapport de stage, tableau des échelles).
WEIGHT_BOUND = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 9}


def weight_bound(d: int) -> int:
    """Borne des poids ``B_d``."""
    try:
        return WEIGHT_BOUND[d]
    except KeyError:
        raise ValueError(f"borne des poids inconnue en dimension {d}") from None


@cache
def sbf_tables(d: int) -> dict[int, tuple[int, ...]]:
    """Toutes les SBF de dimension ``d``.

    Retourne un dictionnaire ``table de vérité -> une réalisation`` (la première
    colonne de poids rencontrée, dans ``[-B_d, B_d]``). L'énumération parcourt les
    ``(2 B_d + 1)^d`` colonnes : immédiate jusqu'à ``d = 4``, quelques secondes en
    ``d = 5``, hors de portée au-delà.
    """
    if d > 5:
        raise ValueError("énumération directe des SBF limitée à d <= 5")
    if d == 0:
        return {0: ()}  # un seul état, aucune entrée : la constante 0
    b = weight_bound(d)
    cols = np.array(list(product(range(-b, b + 1), repeat=d)), dtype=np.int64)
    active = cols @ state_bits(d).T > 0  # (colonnes, états)
    tts = active.astype(np.uint64) @ (np.uint64(1) << np.arange(1 << d, dtype=np.uint64))
    tables: dict[int, tuple[int, ...]] = {}
    for tt, col in zip(tts.tolist(), cols.tolist(), strict=True):
        tables.setdefault(int(tt), tuple(col))
    return tables


@cache
def sbf_counts(d: int) -> dict[int, int]:
    """Nombre de colonnes de poids de ``[-B_d, B_d]^d`` qui réalisent chaque SBF."""
    if d == 0:
        return {0: 1}
    b = weight_bound(d)
    cols = np.array(list(product(range(-b, b + 1), repeat=d)), dtype=np.int64)
    active = cols @ state_bits(d).T > 0
    tts = active.astype(np.uint64) @ (np.uint64(1) << np.arange(1 << d, dtype=np.uint64))
    values, counts = np.unique(tts, return_counts=True)
    return dict(zip(values.tolist(), counts.tolist(), strict=True))


def projection(d: int, c: int) -> int:
    """Table de vérité de ``x -> x_c``, la fonction d'un nœud de contrôle."""
    return sum(1 << s for s in range(1 << d) if (s >> c) & 1)


def restrict(tt: int, d: int, c: int, value: int) -> int:
    """Restriction d'une table de dimension ``d`` à la face ``x_c = value``.

    Le résultat est une table de dimension ``d - 1`` sur les nœuds restants, qui
    gardent leur ordre.
    """
    low = (1 << c) - 1
    out = 0
    for t in range(1 << (d - 1)):
        s = (t & low) | (value << c) | ((t & ~low) << 1)
        out |= ((tt >> s) & 1) << t
    return out
