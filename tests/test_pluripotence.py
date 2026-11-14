from collections import Counter
from itertools import product

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from simsbn import (
    control_nodes,
    count_psbn,
    decomposition,
    dynamics,
    is_control_node,
    is_psbn,
    sbf_tables,
)
from simsbn.sbf import restrict


@pytest.fixture(scope="module")
def all_dynamics_3():
    return list(product(sbf_tables(3), repeat=3))


@given(st.integers(1, 5).flatmap(lambda d: arrays(np.int64, (d, d), elements=st.integers(-5, 5))))
def test_weights_and_dynamics_agree_on_control_nodes(W):
    d = W.shape[0]
    assert [c for c in range(d) if is_control_node(W, c)] == control_nodes(dynamics(W))


# Les nombres qui suivent viennent du rapport de stage (section « Quel paysage des
# réseaux explore-t-on ? » et tableau des échelles).


def test_dynamics_with_a_control_node_dimension_3(all_dynamics_3):
    assert sum(bool(control_nodes(f)) for f in all_dynamics_3) == 2_977


def test_psbn_dimension_3(all_dynamics_3):
    assert sum(is_psbn(f) for f in all_dynamics_3) == 658


def test_last_node_as_control_dimension_3(all_dynamics_3):
    sub = sbf_tables(2)
    n = sum(
        2 in control_nodes(f) and all(restrict(f[j], 3, 2, 1) in sub for j in (0, 1))
        for f in all_dynamics_3
    )
    assert n == 225


@pytest.mark.parametrize(("d", "expected"), [(1, 1), (2, 5), (3, 658), (4, 11_923_831)])
def test_count_psbn(d, expected):
    assert count_psbn(d) == expected


@pytest.mark.slow
def test_count_psbn_dimension_5():
    assert count_psbn(5) == 475_605_031_121_746  # 4,76e14 dans le rapport


# Histogrammes des vecteurs de décomposition les plus fins en dimension 3, identiques
# à ceux de MCSBN/src/python/decompose.py (PluripotentSBN, commit 0e4640b).
HISTOGRAM_3 = {
    "sbn": {
        (1, 0, 0, 0): 32_110,
        (0, 2, 0, 0): 519,
        (0, 1, 2, 0): 66,
        (0, 1, 1, 2): 36,
        (0, 1, 0, 4): 21,
        (0, 0, 4, 0): 3,
        (0, 0, 3, 2): 3,
        (0, 0, 2, 4): 6,
        (0, 0, 1, 6): 3,
        (0, 0, 0, 8): 1,
    },
    "tbn": {
        (1, 0, 0, 0): 29_791,
        (0, 2, 0, 0): 2_028,
        (0, 1, 2, 0): 516,
        (0, 1, 1, 2): 264,
        (0, 1, 0, 4): 51,
        (0, 0, 4, 0): 48,
        (0, 0, 3, 2): 30,
        (0, 0, 2, 4): 30,
        (0, 0, 1, 6): 9,
        (0, 0, 0, 8): 1,
    },
}


@pytest.mark.parametrize("mode", ["sbn", "tbn"])
def test_decomposition_histogram_dimension_3(all_dynamics_3, mode):
    assert Counter(decomposition(f, mode) for f in all_dynamics_3) == HISTOGRAM_3[mode]


def test_decomposition_is_trivial_exactly_when_not_psbn(all_dynamics_3):
    trivial = (1, 0, 0, 0)
    for f in all_dynamics_3:
        assert (decomposition(f, "sbn") != trivial) == is_psbn(f)


def test_identity_decomposes_into_fixed_points():
    identity = np.eye(3, dtype=np.int64)
    assert decomposition(dynamics(identity)) == (0, 0, 0, 8)
