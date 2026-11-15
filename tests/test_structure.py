import numpy as np

from simsbn import control_nodes, dynamics, is_psbn, null_distribution
from simsbn.milieu import ARCH
from simsbn.monde import IMMOBILE, REACTIF
from simsbn.pluripotence import decomposition
from simsbn.sbf import sbf_tables
from simsbn.structure import (
    BRAIN_KINDS,
    KINDS,
    Classifier,
    brain_kinds,
    exact_brain_kinds,
    exact_brain_law,
)


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


def test_a_brain_is_a_ptbn_exactly_when_it_has_a_control_node():
    # Sur les 32 768 dynamiques SBN de dimension 3, sans exception.
    tables = sorted(sbf_tables(3))
    count = 0
    for f in ((a, b, c) for a in tables for b in tables for c in tables):
        control, psbn, two, two_sbn = brain_kinds(f)
        assert control == (sum(decomposition(f, "tbn")) > 1)
        assert psbn == (sum(decomposition(f, "sbn")) > 1)
        assert two == (len(control_nodes(f)) == 2)
        assert not two_sbn or (two and psbn)
        count += 1
    assert count == 32_768


def test_two_control_one_operative_on_hand_built_brains():
    def brain(**arcs):
        index = {"a": 0, "b": 1, "c": 2}
        W = np.zeros((3, 3), dtype=np.int64)
        for name, weight in arcs.items():
            W[index[name[0]], index[name[2]]] = weight
        return dynamics(W)

    names = BRAIN_KINDS
    # a et b gardent leur valeur ; c garde la sienne, sauf si a est allumé : il s'éteint.
    reset = dict(zip(names, brain_kinds(brain(a_a=1, b_b=1, c_c=1, a_c=-1)), strict=True))
    assert reset["deux_controles"] and reset["deux_controles_sbn"] and reset["psbn_cerveau"]
    # Ici a allume c : sur la face a = 1, c n'est plus une SBF. Sens TBN seulement.
    forced = dict(zip(names, brain_kinds(brain(a_a=1, b_b=1, a_c=1)), strict=True))
    assert forced["deux_controles"] and not forced["deux_controles_sbn"]
    # Un seul nœud de contrôle, puis trois : aucun des deux n'est dans la classe.
    assert not brain_kinds(brain(a_a=1, a_b=1, b_c=1))[2]
    assert not brain_kinds(brain(a_a=1, b_b=1, c_c=1))[2]


def test_exact_shares_of_the_brain_classes():
    shares = exact_brain_kinds(bound=3)
    assert list(shares) == BRAIN_KINDS
    assert [round(100 * shares[k], 3) for k in BRAIN_KINDS] == [8.494, 2.491, 0.248, 0.076]
