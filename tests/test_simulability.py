import numpy as np

from simsbn import dynamics, sbf_tables, transition
from simsbn.agents import Architecture
from simsbn.sbf import restrict
from simsbn.simulability import simulated_target, target_code

ARCH = Architecture(n_in=1, n_brain=3, n_out=0)


def brute_force(W, e):
    """Cible simulée par le composite ``W`` dans le contexte ``e``, par simple suivi."""
    F = transition(W)
    rule = {}
    for v in range(4):
        s = e | (v << 1)
        for _ in range(20):
            nxt = int(F[s])
            visible, target = (s >> 1) & 3, (nxt >> 1) & 3
            if rule.setdefault(visible, target) != target:
                return -1
            s = nxt
    return sum(rule[v] << (2 * v) for v in range(4))


def test_matches_brute_force_on_random_composites():
    rng = np.random.default_rng(0)
    population = ARCH.random(rng, 400, bound=3)
    found = set()
    for W in population:
        f = dynamics(W)
        for e in (0, 1):
            tables = np.array([[restrict(f[j], 4, 0, e) for j in (1, 2, 3)]])
            got = int(simulated_target(tables, n=3, p=2)[0])
            assert got == brute_force(W, e)
            found.add(got >= 0)
    assert found == {True, False}  # les deux cas sont bien couverts


def test_a_late_hidden_node_breaks_the_rule():
    # Contexte A : les nœuds visibles échangent leurs valeurs. Contexte B : le nœud
    # caché, allumé par l'environnement, les éteint.
    W = np.zeros((4, 4), dtype=np.int64)
    W[0, 0] = 1
    W[1, 2] = W[2, 1] = 1  # échange
    W[0, 3] = 1  # l'environnement allume le nœud caché
    W[3, 1] = W[3, 2] = -1  # qui inhibe les nœuds visibles
    f = dynamics(W)
    swap = target_code((0b1100, 0b1010))  # chaque nœud prend la valeur de l'autre
    in_a = np.array([[restrict(f[j], 4, 0, 0) for j in (1, 2, 3)]])
    in_b = np.array([[restrict(f[j], 4, 0, 1) for j in (1, 2, 3)]])
    assert simulated_target(in_a, 3, 2)[0] == swap
    # En B, le premier pas est encore un échange, puis tout s'éteint : pas de règle fixe.
    assert simulated_target(in_b, 3, 2)[0] == -1


def test_targets_of_sbn_brains_without_context_are_sbn():
    tables = list(sbf_tables(3))
    rng = np.random.default_rng(1)
    triples = rng.choice(tables, size=(2000, 3))
    codes = simulated_target(triples, 3, 2)
    sbn_targets = {target_code((a, b)) for a in sbf_tables(2) for b in sbf_tables(2)}
    assert set(codes[codes >= 0].tolist()) <= sbn_targets
