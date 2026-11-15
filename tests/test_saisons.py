from dataclasses import replace

import numpy as np

from simsbn.monde import IMMOBILE, Monde, Vie, handmade

YEAR = Monde(height=4, width=4, inflow=32.0, summer=5, winter=3)


def test_summer_comes_first_and_seasons_repeat():
    assert [YEAR.is_summer(t) for t in range(10)] == [True] * 5 + [False] * 3 + [True] * 2
    assert all(Monde().is_summer(t) for t in range(100))


def test_food_arrives_only_in_summer():
    vie = Vie(np.stack([handmade()] * 3), YEAR, np.random.default_rng(0))
    vie.brain[:] = 0
    vie.food[:] = 0
    totals = []
    for _ in range(8):
        vie.step()
        totals.append(int(vie.food.sum()))
    assert all(b > a for a, b in zip([0, *totals[:4]], totals[:5], strict=True))  # été
    assert totals[5:] == [totals[4]] * 3  # hiver : plus rien n'arrive


def test_activity_is_counted_by_season():
    vie = Vie(np.stack([IMMOBILE] * 40), replace(YEAR, gain=10), np.random.default_rng(1), 0.0)
    vie.brain[:] = (1, 0, 0)
    for _ in range(8):
        vie.step()
    stats = vie.stats()
    assert stats["manger_ete"] == 1 and stats["manger_hiver"] == 1
    assert stats["bouger_ete"] == 0 and stats["economie_hiver"] == 0


def test_neutral_winter_costs_upkeep_only():
    monde = replace(YEAR, neutral=True, inflow=0.0)
    vie = Vie(np.stack([handmade()] * 4), monde, np.random.default_rng(2))
    energies = []
    for _ in range(8):
        vie.step()
        energies.append(int(vie.energy[0]) if len(vie) else 0)
    assert energies == [8, 6, 4, 2, 0, 0, 0, 0]  # été sans nourriture : 2 par pas
    vie = Vie(
        np.stack([handmade()] * 4), replace(monde, summer=1, winter=7), np.random.default_rng(3)
    )
    for _ in range(8):
        vie.step()
    assert vie.energy.tolist() == [10 - 2 - 7] * 4


def test_worlds_without_seasons_have_no_winter_stats():
    vie = Vie(np.stack([IMMOBILE] * 5), Monde(height=4, width=4), np.random.default_rng(4))
    vie.step()
    assert np.isnan(vie.stats()["manger_hiver"])
