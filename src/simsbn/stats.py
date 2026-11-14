"""Tests statistiques simples, une population étant l'unité d'observation."""

from __future__ import annotations

import numpy as np


def permutation_test(a, b, rng: np.random.Generator, n: int = 20_000) -> float:
    """Valeur p bilatérale de la différence des moyennes de ``a`` et ``b``.

    Les étiquettes des deux groupes sont permutées ``n`` fois ; la valeur p est la part
    des permutations dont l'écart est au moins aussi grand que l'écart observé (avec la
    correction ``+1`` qui empêche une valeur nulle). Les ``nan`` sont écartés.
    """
    a, b = (np.asarray(x, dtype=float) for x in (a, b))
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    pooled = np.concatenate([a, b])
    observed = abs(a.mean() - b.mean())
    shuffled = rng.permuted(np.broadcast_to(pooled, (n, len(pooled))), axis=1)
    gaps = np.abs(shuffled[:, : len(a)].mean(axis=1) - shuffled[:, len(a) :].mean(axis=1))
    return float((1 + (gaps >= observed - 1e-12).sum()) / (n + 1))
