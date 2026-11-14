import pytest

from simsbn import column_table, sbf_tables
from simsbn.sbf import projection, restrict

# Rapport de stage, tableau des échelles.
SBF_COUNT = {1: 2, 2: 6, 3: 32, 4: 370}


@pytest.mark.parametrize("d", SBF_COUNT)
def test_sbf_count(d):
    assert len(sbf_tables(d)) == SBF_COUNT[d]


@pytest.mark.slow
def test_sbf_count_dimension_5():
    assert len(sbf_tables(5)) == 11_292


@pytest.mark.parametrize("d", [1, 2, 3, 4])
def test_each_realisation_gives_its_table(d):
    for tt, col in sbf_tables(d).items():
        assert column_table(col) == tt


def test_restriction_of_a_projection():
    # x -> x_2 restreinte à la face x_0 = 1 devient x -> x_1 en dimension 2.
    assert restrict(projection(3, 2), 3, 0, 1) == projection(2, 1)
    # ... et restreinte à sa propre face x_2 = 1, la constante 1.
    assert restrict(projection(3, 2), 3, 2, 1) == 0b1111
