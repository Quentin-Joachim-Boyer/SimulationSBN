from dataclasses import replace

import numpy as np
import pytest

from simsbn import transition
from simsbn.milieu import ARCH, step_brains
from simsbn.monde import REACTIF, Corps, Monde, Vie, read_motors

CLEAN = Monde(height=1, width=8, inflow=0.0, tox=np.inf)  # ni apport ni poison
PAIR = ("ingérer", "bouger")


def test_one_hot_immediate_readers_reproduce_direct_reading_exactly():
    corps = Corps(PAIR, delay=False)
    genotypes = ARCH.random(np.random.default_rng(0), 120, 3)
    monde = Monde(height=8, width=8, inflow=40.0)
    direct = Vie(genotypes, monde, np.random.default_rng(1), mutation_rate=0.0)
    carried = np.stack([corps.one_hot(g) for g in genotypes])
    readers = Vie(carried, monde, np.random.default_rng(1), mutation_rate=0.0, corps=corps)
    for _ in range(400):
        direct.step()
        readers.step()
        for name in ("cell", "energy", "ident", "brain", "sensor"):
            assert np.array_equal(getattr(direct, name), getattr(readers, name))
    assert len(direct) > 0 and np.array_equal(direct.waste, readers.waste)
    a, b = direct.stats(), readers.stats()
    assert a.keys() == b.keys()
    assert all(a[k] == b[k] or (np.isnan(a[k]) and np.isnan(b[k])) for k in a)


def test_brain_and_delayed_motors_are_one_synchronous_sbn():
    # Référence : la fonction de transition du réseau complet (capteur, cerveau, moteurs).
    arch = Corps(PAIR).arch
    population = arch.random(np.random.default_rng(2), 40, 3)
    for W in population:
        F = transition(W)
        for state in range(1 << arch.d):
            bits = np.array([(state >> i) & 1 for i in range(arch.d)])
            sensor, brain = bits[:1], bits[None, 1:4]
            after = [(int(F[state]) >> i) & 1 for i in range(arch.d)]
            assert after[0] == sensor[0]  # l'entrée garde sa valeur
            assert step_brains(W[None], sensor, brain)[0].tolist() == after[1:4]
            assert read_motors(W[None], brain)[0].tolist() == after[4:]


def test_motors_read_the_brain_only_and_nothing_comes_back():
    arch = Corps(PAIR).arch
    population = arch.random(np.random.default_rng(3), 200, 3)
    silent = population.copy()
    silent[:, :, ARCH.d :] = 0  # mêmes cerveaux, moteurs débranchés
    rng = np.random.default_rng(4)
    sensor, brain = rng.integers(0, 2, 200), rng.integers(0, 2, (200, 3))
    assert np.array_equal(
        step_brains(population, sensor, brain), step_brains(silent, sensor, brain)
    )
    vie = Vie(population, Monde(height=8, width=8, inflow=40.0), rng, corps=Corps(PAIR))
    for _ in range(300):
        vie.step()
    assert vie.counts["births"] > 0
    assert (vie.population[:, ARCH.d :, :] == 0).all()  # rien ne part des moteurs
    assert (vie.population[:, 0, ARCH.d :] == 0).all()  # le capteur n'atteint pas les moteurs
    assert (np.abs(vie.population) <= 3).all()


def lone(corps, food):
    vie = Vie(corps.one_hot(REACTIF)[None], CLEAN, np.random.default_rng(5), corps=corps)
    vie.brain[:] = (1, 0, 0)
    vie.motor[:] = (1, 0)
    vie.cell[:] = 3
    vie.food[:] = food
    return vie


def test_delayed_reactive_agent_leaves_one_step_later():
    food = [0, 0, 0, 3, 0, 0, 0, 0]
    cells, energies = {}, {}
    for delay in (False, True):
        vie = lone(Corps(PAIR, delay=delay), food)
        cells[delay], energies[delay] = [], []
        for _ in range(6):
            vie.step()
            cells[delay].append(int(vie.cell[0]))
            energies[delay].append(int(vie.energy[0]))
    # Le monde n'a qu'une ligne : un pas vers le nord ou le sud laisse sur place, et
    # c'est l'énergie (-3 au lieu de -2) qui prouve le déplacement.
    # Lecture immédiate : trois repas, un échec, départ au pas 5, comme en lecture directe.
    assert cells[False][:4] == [3, 3, 3, 3] and cells[False][4] in (2, 3, 4)
    assert energies[False][:5] == [12, 14, 16, 14, 11]
    # Lecture retardée : un échec de plus sur place avant de partir, au pas 6.
    assert cells[True][:5] == [3, 3, 3, 3, 3] and cells[True][5] in (2, 3, 4)
    assert energies[True] == [12, 14, 16, 14, 12, 9]


@pytest.mark.parametrize("delay", [False, True])
def test_context_is_the_sensor_the_action_could_react_to(delay):
    corps = Corps(PAIR, delay=delay)
    monde = Monde(height=8, width=8, inflow=60.0)
    start = np.stack([corps.one_hot(REACTIF)] * 80)
    vie = Vie(start, monde, np.random.default_rng(6), mutation_rate=0.0, corps=corps)
    vie.brain[:] = (1, 0, 0)
    vie.motor[:] = (1, 0)
    for _ in range(3):
        vie.step()
    vie.stats()
    for _ in range(300):
        vie.step()
    stats = vie.stats()
    assert len(vie) > 0
    assert stats["bouger_0"] == 1 and stats["bouger_1"] == 0  # exactement, sans mélange


def test_direction_motors_add_up_and_each_one_costs():
    corps = Corps(("ingérer", "nord", "sud", "est"))
    monde = replace(CLEAN, height=5, width=7)
    start = np.zeros((4, corps.arch.d, corps.arch.d), dtype=np.int64)
    vie = Vie(start, monde, np.random.default_rng(7), corps=corps)
    vie.cell[:] = 6  # ligne 0, colonne 6 : le coin, pour passer par les bords du tore
    vie.motor[:] = [(0, 1, 1, 0), (0, 1, 0, 1), (0, 1, 0, 0), (0, 0, 0, 0)]
    vie.step()
    assert vie.cell.tolist() == [6, 4 * 7 + 0, 4 * 7 + 6, 6]  # annulation, diagonale, nord, rien
    assert vie.energy.tolist() == [10 - 1 - 2, 10 - 1 - 2, 10 - 1 - 1, 10 - 1]


def test_corps_rejects_unknown_roles_and_wrong_genotypes():
    with pytest.raises(ValueError):
        Corps(("ingérer", "voler"))
    with pytest.raises(ValueError):
        Corps(("nord", "nord"))
    with pytest.raises(ValueError):
        Vie(
            ARCH.random(np.random.default_rng(8), 3, 3),
            Monde(),
            np.random.default_rng(8),
            corps=Corps(PAIR),
        )
    assert Corps().arch == ARCH and not Corps().lagged and Corps(PAIR).lagged
