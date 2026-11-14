import numpy as np

from simsbn import transition
from simsbn.tasks import Context, score, trajectories


def test_trajectories_match_reference():
    rng = np.random.default_rng(0)
    population = rng.integers(-2, 3, size=(40, 3, 3))
    for W, row in zip(population, trajectories(population, 0b010, 6), strict=True):
        F, s, expected = transition(W), 0b010, []
        for _ in range(6):
            s = int(F[s])
            expected.append(s)
        assert row.tolist() == expected


def test_score_of_a_handmade_agent():
    # Nœud 0 : contexte, gardé par sa boucle. Nœud 1 : stimulus entretenu.
    # Nœud 2 : moteur, allumé par le stimulus sauf si le contexte l'inhibe.
    W = np.array([[1, 0, -2], [0, 1, 1], [0, 0, 0]])[None]
    on = Context(start=0b010, target=dict.fromkeys(range(2, 7), 1))
    off = Context(start=0b011, target=dict.fromkeys(range(2, 7), 0))
    assert score(W, on, motor=2).tolist() == [1.0]
    assert score(W, off, motor=2).tolist() == [1.0]
    assert score(W, off, motor=1).tolist() == [0.0]  # le stimulus, lui, reste allumé
