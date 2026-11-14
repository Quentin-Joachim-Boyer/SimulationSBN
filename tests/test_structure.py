import numpy as np

from simsbn import control_nodes, dynamics, is_psbn, null_distribution
from simsbn.milieu import ARCH
from simsbn.monde import IMMOBILE, REACTIF
from simsbn.structure import KINDS, Classifier, exact_brain_law


def test_exact_brain_law_matches_the_null_distribution_at_the_usual_bound():
    control, psbn = exact_brain_law(bound=2)
    assert abs(psbn - null_distribution(3, is_psbn)[True]) < 1e-12
    assert abs(control - null_distribution(3, lambda f: bool(control_nodes(f)))[True]) < 1e-12
    assert round(100 * psbn, 2) == 2.99 and round(100 * control, 2) == 9.30


def test_exact_brain_law_agrees_with_sampling_at_bound_three():
    control, psbn = exact_brain_law(bound=3)
    sample = ARCH.random(np.random.default_rng(0), 20_000, 3)
    shares = Classifier()(sample)
    assert abs(shares[0] - control) < 0.01 and abs(shares[1] - psbn) < 0.005


def test_classifier_on_hand_built_agents():
    flags = dict(zip(KINDS, Classifier().flags(np.stack([IMMOBILE, REACTIF])).T, strict=True))
    # Ingestion qui s'entretient seule : nœud de contrôle du cerveau dans les deux cas.
    assert flags["controle_cerveau"].tolist() == [True, True]
    # Le capteur allume l'ingestion (poids +1) : la face « capteur = 1 » n'est pas un SBN.
    assert flags["scission_sbn"].tolist() == [False, False]
    brain = dynamics(REACTIF[1:, 1:])
    assert control_nodes(brain) == [0]
