from dataclasses import replace

import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import EAT, IMMOBILE, MARCHEUR, MOVE, REACTIF, Monde, Vie, handmade

CLEAN = Monde(height=1, width=8, inflow=0.0, tox=np.inf)  # ni apport ni poison


def lone(genotype, monde, cell, food, brain=(1, 0, 0), seed=0):
    """Un agent seul sur ``cell``, la nourriture de chaque case étant imposée."""
    vie = Vie(genotype[None], monde, np.random.default_rng(seed))
    vie.brain[:] = brain
    vie.cell[:] = cell
    vie.food[:] = food
    return vie


def test_melange_keeps_the_totals():
    monde = Monde(height=4, width=8, food_cap=5, tox=10.0)
    mixed = monde.melange()
    assert mixed.cells == 1
    assert mixed.food_cap == 5 * 32 and mixed.tox == 10.0 * 32
    assert mixed.inflow == monde.inflow


def test_reactive_agent_stays_while_fed_and_leaves_when_unfed():
    vie = lone(REACTIF, CLEAN, cell=3, food=[0, 0, 0, 3, 0, 0, 0, 0])
    cells, energies = [], []
    for _ in range(5):
        vie.step()
        cells.append(int(vie.cell[0]))
        energies.append(int(vie.energy[0]))
    # Trois repas sur place (+4 - 2), un échec (-2), puis départ vers une case voisine.
    assert cells[:4] == [3, 3, 3, 3] and cells[4] in (2, 4)
    assert energies == [12, 14, 16, 14, 11]
    assert vie.food[3] == 0 and vie.waste[3] == 3  # une unité de déchet par unité ingérée


def test_walker_moves_one_cell_at_a_time_on_the_torus():
    monde = replace(CLEAN, height=5, width=7, gain=10)
    vie = Vie(np.stack([MARCHEUR] * 30), monde, np.random.default_rng(1), mutation_rate=0.0)
    vie.brain[:] = (1, 1, 0)
    for _ in range(20):
        ident, cell = vie.ident.copy(), vie.cell.copy()
        vie.step()
        before = dict(zip(ident.tolist(), cell.tolist(), strict=True))
        for i, c in zip(vie.ident.tolist(), vie.cell.tolist(), strict=True):
            if i in before:
                dr = abs(c // 7 - before[i] // 7)
                dc = abs(c % 7 - before[i] % 7)
                assert sorted((min(dr, 5 - dr), min(dc, 7 - dc))) == [0, 1]


def test_nobody_moves_in_a_one_cell_world_but_moving_still_costs():
    monde = replace(CLEAN, height=1, width=1)
    vie = lone(MARCHEUR, monde, cell=0, food=[0], brain=(1, 1, 0))
    vie.step()
    assert vie.cell[0] == 0 and vie.energy[0] == 10 - 3


def test_a_cell_never_serves_more_than_its_stock():
    vie = Vie(np.stack([IMMOBILE] * 12), CLEAN, np.random.default_rng(2))
    vie.brain[:] = (1, 0, 0)
    vie.cell[:] = 0
    vie.food[:] = [5, 0, 0, 0, 0, 0, 0, 0]
    vie.step()
    assert sorted(vie.energy.tolist()) == [8] * 7 + [12] * 5
    assert vie.food[0] == 0 and vie.waste[0] == 5
    assert vie.sensor.sum() == 5  # le capteur suit la hausse d'énergie


def test_waste_poisons_those_who_ingest_and_decays():
    monde = replace(CLEAN, tox=10.0, decay=0.0)
    vie = Vie(np.stack([IMMOBILE] * 400), monde, np.random.default_rng(3))
    vie.brain[:200] = (1, 0, 0)
    vie.brain[200:] = (0, 0, 1)  # ceux-là n'ingèrent pas : aucun poison
    vie.cell[:] = 0
    vie.food[:] = 0
    vie.waste[0] = 5  # une chance sur deux
    vie.step()
    poisoned = vie.energy == 10 - 2 - 4
    assert 70 <= poisoned[:200].sum() <= 130
    assert (vie.energy[200:] == 9).all()
    faster = Vie(IMMOBILE[None], replace(monde, decay=0.5), np.random.default_rng(4))
    faster.waste[:] = 1000
    faster.step()
    assert 400 * 8 <= faster.waste.sum() <= 600 * 8


def test_food_and_waste_bookkeeping_over_a_long_run():
    monde = Monde(height=8, width=8, inflow=20.0, decay=0.0, tox=np.inf)
    vie = Vie(np.stack([MARCHEUR] * 40), monde, np.random.default_rng(5), mutation_rate=0.0)
    for _ in range(300):
        vie.step()
        assert vie.food.min() >= 0 and vie.food.max() <= monde.food_cap
    assert vie.waste.sum() == vie.counts["served"]  # sans disparition, tout déchet reste
    assert len(vie) > 0 and vie.counts["births"] > 0
    assert len(set(vie.ident.tolist())) == len(vie)
    assert set(vie.lineage.tolist()) <= set(range(40))


def test_inert_agents_starve():
    vie = Vie(np.stack([handmade()] * 5), Monde(), np.random.default_rng(6))
    vie.brain[:] = 0
    for _ in range(9):
        vie.step()
    assert len(vie) == 5
    vie.step()
    assert len(vie) == 0 and vie.counts["deaths"] == 5


def test_neutral_regime_ignores_behaviour_and_position():
    # 200 unités tirées au sort, +4 chacune, 2 de dépense par pas : équilibre vers 400.
    monde = Monde(neutral=True)
    for genotype in (IMMOBILE, MARCHEUR, handmade()):
        vie = Vie(np.stack([genotype] * 100), monde, np.random.default_rng(7), 0.0)
        for _ in range(1500):
            vie.step()
        assert 320 <= len(vie) <= 480
        assert vie.waste.sum() == 0 and (vie.food == monde.food_cap).all()


def test_stats_split_actions_by_sensor_and_reset():
    vie = lone(REACTIF, CLEAN, cell=3, food=[0, 0, 0, 3, 0, 0, 0, 0])
    for _ in range(8):
        vie.step()
    stats = vie.stats()
    assert stats["manger_0"] == 1 and stats["manger_1"] == 1
    assert stats["bouger_1"] == 0 and stats["bouger_0"] > 0.5
    assert stats["dependance"] == stats["bouger_0"]
    assert vie.counts["steps"] == 0


def test_run_is_reproducible_and_mutates_only_evolving_weights():
    start = ARCH.random(np.random.default_rng(8), 150, 3)

    def run():
        vie = Vie(start, Monde(height=8, width=8, inflow=40.0), np.random.default_rng(9))
        for _ in range(300):
            vie.step()
        return vie

    a, b = run(), run()
    assert np.array_equal(a.population, b.population) and np.array_equal(a.cell, b.cell)
    assert (np.abs(a.population) <= 3).all()
    assert (a.population[:, ~ARCH.mask()] == start[0][~ARCH.mask()]).all()
    assert EAT == 0 and MOVE == 1
