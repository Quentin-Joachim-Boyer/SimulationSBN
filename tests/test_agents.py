import numpy as np

from simsbn import control_nodes, dynamics, is_control_node, mutate
from simsbn.agents import Architecture
from simsbn.tasks import trajectories

ARCH = Architecture(n_in=1, n_brain=3, n_out=1)


def test_mask_counts_the_evolving_weights():
    mask = ARCH.mask()
    assert mask.sum() == 3 + 9 + 3
    assert not mask[:, 0].any()  # rien n'entre dans l'entrée
    assert not mask[4].any()  # rien ne sort du moteur
    assert not mask[0, 4]  # l'entrée n'atteint pas le moteur directement


def test_input_is_a_control_node_and_motor_never_is():
    rng = np.random.default_rng(0)
    for W in ARCH.random(rng, 50, bound=3):
        assert is_control_node(W, 0)
        assert 0 in control_nodes(dynamics(W))
        assert not is_control_node(W, 4)


def test_input_keeps_its_value_and_motor_does_not_feed_back():
    rng = np.random.default_rng(1)
    population = ARCH.random(rng, 50, bound=3)
    for value in (0, 1):
        states = trajectories(population, ARCH.state(inputs=value, brain=0b001), 8)
        assert ((states & 1) == value).all()
    # Allumer le moteur au départ ne change rien à la suite du cerveau.
    a = trajectories(population, ARCH.state(inputs=1, brain=0b101), 8)
    b = trajectories(population, ARCH.state(inputs=1, brain=0b101) | (1 << 4), 8)
    assert np.array_equal(a, b)


def test_masked_mutation_respects_the_architecture():
    rng = np.random.default_rng(2)
    mask = ARCH.mask()
    W = ARCH.random(rng, 1, bound=3)[0]
    for _ in range(500):
        M = mutate(W, rng, bound=3, mask=mask)
        (i,), (j,) = np.nonzero(M != W)
        assert mask[i, j] and abs(M[i, j]) <= 3
