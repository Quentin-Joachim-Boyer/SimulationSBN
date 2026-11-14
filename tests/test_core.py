import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from simsbn import attractors, column_table, dynamics, transition


def weights(max_d=5, bound=5):
    return st.integers(1, max_d).flatmap(
        lambda d: arrays(np.int64, (d, d), elements=st.integers(-bound, bound))
    )


def test_column_table_dimension_2():
    # bit s = f(s), états 00, 01, 10, 11 (nœud 0 à droite)
    assert column_table([1, 1]) == 0b1110  # OU
    assert column_table([1, -1]) == 0b0010  # x0 et non x1
    assert column_table([-1, 0]) == 0b0000  # constante 0


def test_swap_network():
    # Les nœuds 0 et 1 échangent leurs valeurs.
    F = transition([[0, 1], [1, 0]])
    assert F.tolist() == [0, 2, 1, 3]
    assert attractors(F) == [(0,), (1, 2), (3,)]


@given(weights())
def test_zero_state_is_fixed(W):
    assert transition(W)[0] == 0


@given(weights())
def test_transition_agrees_with_dynamics(W):
    d = W.shape[0]
    f = dynamics(W)
    for s, nxt in enumerate(transition(W).tolist()):
        assert nxt == sum(((f[j] >> s) & 1) << j for j in range(d))


@given(weights())
def test_attractors_are_cycles(W):
    F = transition(W).tolist()
    cycles = attractors(F)
    assert cycles
    for cycle in cycles:
        assert all(F[a] == b for a, b in zip(cycle, cycle[1:] + cycle[:1], strict=True))


@given(weights(max_d=4))
def test_padding_with_an_absent_node_changes_nothing(W):
    # Un nœud sans arc (ligne et colonne nulles) reste éteint et n'influence personne :
    # c'est ce qui autorisera des populations de dimensions variables dans un tableau fixe.
    d = W.shape[0]
    padded = np.zeros((d + 1, d + 1), dtype=np.int64)
    padded[:d, :d] = W
    assert transition(padded)[: 1 << d].tolist() == transition(W).tolist()
