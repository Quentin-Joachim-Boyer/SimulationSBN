import numpy as np

from simsbn.stats import format_p, permutation_test


def test_permutation_test_separates_distinct_groups_only():
    rng = np.random.default_rng(0)
    low, high = rng.normal(0, 1, 24), rng.normal(3, 1, 24)
    assert permutation_test(low, high, rng) < 0.001
    assert permutation_test(low, rng.normal(0, 1, 24), rng) > 0.05


def test_permutation_test_is_exact_on_a_tiny_case():
    # 3 contre 3, groupes disjoints : 2 des 20 partages donnent un écart aussi grand.
    p = permutation_test([1, 2, 3], [7, 8, 9], np.random.default_rng(1), n=50_000)
    assert abs(p - 0.1) < 0.01


def test_permutation_test_ignores_missing_populations():
    rng = np.random.default_rng(2)
    assert permutation_test([1.0, np.nan, 2.0], [1.5, 1.4, np.nan], rng) > 0.05
    assert np.isnan(permutation_test([np.nan], [1.0], rng))


def test_format_p_never_prints_a_misleading_zero():
    assert format_p(1 / 20001) == "< 0,0001"
    assert format_p(0.0024) == "0,0024" and format_p(0.0024, sign=True) == "= 0,0024"
    assert format_p(float("nan")) == "n.d."
