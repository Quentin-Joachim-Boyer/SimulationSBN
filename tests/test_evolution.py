from itertools import product

import numpy as np
import pytest

from simsbn import (
    batch_dynamics,
    dynamics,
    is_psbn,
    mutate,
    null_distribution,
    sbf_counts,
    weight_bound,
    wright_fisher,
)


def test_mutation_changes_exactly_one_weight_within_bounds():
    rng = np.random.default_rng(0)
    W = rng.integers(-2, 3, size=(3, 3))
    seen = set()
    for _ in range(2000):
        M = mutate(W, rng)
        assert (M != W).sum() == 1
        assert np.abs(M).max() <= 2
        (i,), (j,) = np.nonzero(M != W)
        seen.add((int(i), int(j), int(M[i, j])))
    assert len(seen) == 9 * 4  # K = 2 B_d d^2 mutants, tous atteints


def test_batch_dynamics_matches_reference():
    rng = np.random.default_rng(1)
    for d in (1, 2, 3, 4, 5):
        b = weight_bound(d)
        population = rng.integers(-b, b + 1, size=(20, d, d))
        expected = [list(dynamics(W)) for W in population]
        assert batch_dynamics(population).tolist() == expected


@pytest.mark.parametrize("d", [1, 2, 3, 4])
def test_sbf_counts_cover_all_columns(d):
    assert sum(sbf_counts(d).values()) == (2 * weight_bound(d) + 1) ** d


def test_null_distribution_matches_brute_force_dimension_2():
    matrices = [np.array(w).reshape(2, 2) for w in product((-1, 0, 1), repeat=4)]
    brute = sum(is_psbn(dynamics(W)) for W in matrices) / len(matrices)
    law = null_distribution(2, is_psbn)
    assert law[True] == pytest.approx(brute)
    assert sum(law.values()) == pytest.approx(1)


def test_null_psbn_frequency_dimension_3():
    assert null_distribution(3, is_psbn)[True] == pytest.approx(0.029898752)


def test_wright_fisher_is_reproducible_and_records_parents():
    def run():
        rng = np.random.default_rng(7)
        start = np.zeros((30, 3, 3), dtype=np.int64)
        return list(wright_fisher(start, 20, rng, mutation_rate=0.5))

    a, b = run(), run()
    assert a[0][2] is None
    for (g, pop, parents), (_, pop_b, _) in zip(a, b, strict=True):
        assert np.array_equal(pop, pop_b)
        assert pop.shape == (30, 3, 3)
        if g:
            assert parents.shape == (30,) and parents.min() >= 0 and parents.max() < 30


def test_selection_favours_the_fitter_genotype():
    rng = np.random.default_rng(3)
    start = np.zeros((100, 2, 2), dtype=np.int64)
    start[:10, 0, 0] = 1  # dix porteurs d'une boucle sur le nœud 0

    def fitness(population):
        return 1.0 + 4.0 * (population[:, 0, 0] == 1)

    *_, (_, final, _) = wright_fisher(start, 30, rng, mutation_rate=0.0, fitness=fitness)
    assert (final[:, 0, 0] == 1).mean() > 0.9
