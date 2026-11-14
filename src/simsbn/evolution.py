"""Évolution d'une population de SBN : mutations, modèle de Wright-Fisher, modèle nul."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator
from itertools import product
from math import prod

import numpy as np

from simsbn.sbf import sbf_counts, weight_bound


def mutate(W: np.ndarray, rng: np.random.Generator, bound: int | None = None) -> np.ndarray:
    """Copie de ``W`` dont un poids, tiré au hasard, prend une autre valeur de ``[-B, B]``.

    C'est la règle de mutation du rapport de stage ; ``bound`` vaut ``B_d`` par défaut.
    """
    d = W.shape[0]
    b = weight_bound(d) if bound is None else bound
    i, j = rng.integers(d, size=2)
    new = rng.integers(-b, b)  # 2B valeurs, décalées pour éviter la valeur actuelle
    out = W.copy()
    out[i, j] = new + (new >= W[i, j])
    return out


def wright_fisher(
    population: np.ndarray,
    generations: int,
    rng: np.random.Generator,
    mutation_rate: float = 0.1,
    fitness: Callable[[np.ndarray], np.ndarray] | None = None,
    bound: int | None = None,
) -> Iterator[tuple[int, np.ndarray, np.ndarray | None]]:
    """Fait évoluer une population ``(N, d, d)`` à effectif constant.

    À chaque génération, chaque individu choisit son parent dans la génération
    précédente, uniformément (évolution neutre, ``fitness=None``) ou avec une
    probabilité proportionnelle à ``fitness(population)``, puis subit une mutation
    avec la probabilité ``mutation_rate``.

    Produit ``(génération, population, parents)``, où ``parents[k]`` est l'indice du
    parent de l'individu ``k`` (``None`` pour la population initiale). La suite des
    ``parents`` suffit à reconstruire les lignées.
    """
    population = np.array(population, dtype=np.int64)
    n = population.shape[0]
    yield 0, population, None
    for generation in range(1, generations + 1):
        p = None
        if fitness is not None:
            w = np.asarray(fitness(population), dtype=float)
            p = w / w.sum()
        parents = rng.choice(n, size=n, p=p)
        population = population[parents]
        for k in np.flatnonzero(rng.random(n) < mutation_rate):
            population[k] = mutate(population[k], rng, bound)
        yield generation, population, parents


def null_distribution(d: int, classify: Callable[[tuple[int, ...]], Hashable]) -> dict:
    """Loi exacte de ``classify(dynamique)`` pour une matrice de poids uniforme.

    C'est la loi stationnaire d'un individu sous évolution neutre, puisque la mutation
    est symétrique : le modèle nul auquel comparer toute simulation. Énumère toutes
    les dynamiques, donc réservé à ``d <= 3``.
    """
    if d > 3:
        raise ValueError("null_distribution énumère les dynamiques : d <= 3")
    counts = sbf_counts(d)
    total = sum(counts.values()) ** d
    law: dict = {}
    for f in product(counts, repeat=d):
        key = classify(f)
        law[key] = law.get(key, 0) + prod(counts[t] for t in f)
    return {key: value / total for key, value in law.items()}
