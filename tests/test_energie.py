"""Variantes du flux d'énergie dans le monde à déchet (journal/2026-11-17_energie-milieu.md)."""

from dataclasses import replace

import numpy as np
import pytest

from simsbn.monde import Corps, Monde, Vie, handmade

SMALL = Monde(height=6, width=8, inflow=30.0, divide_at=40)
CORPS = Corps(("ingérer", "nord", "sud", "est", "ouest"), ticks=2)
VARIANTS = {
    "témoin": SMALL,
    "recyclage": replace(SMALL, recyclage=0.5),
    "conservation": replace(SMALL, conservation=True),
    "diffusion": replace(SMALL, diffusion=0.2),
    "diffusion, plafond bas": replace(SMALL, diffusion=0.6, food_cap=2),
    "accidents": replace(SMALL, accident=0.005),
    "cadavres": replace(SMALL, accident=0.005, cadavres=True),
    "conservation, diffusion, cadavres": replace(
        SMALL, conservation=True, diffusion=0.2, accident=0.005, cadavres=True
    ),
    "neutre": replace(SMALL, neutral=True),
}


@pytest.mark.parametrize("name", list(VARIANTS))
def test_energy_balance_is_exact_at_every_step(name):
    monde = VARIANTS[name]
    rng = np.random.default_rng(11)
    vie = Vie(CORPS.arch.random(rng, 60, 3), monde, rng, 0.5, 3, CORPS)
    total = vie.energie_totale()
    flows = dict(vie.bilan)
    for _ in range(400):
        vie.step()
        now = vie.energie_totale()
        delta = {key: vie.bilan[key] - flows[key] for key in flows}
        assert now - total == delta["entree"] - delta["sortie"]
        assert 0 <= vie.food.min() and vie.food.max() <= monde.food_cap
        assert vie.pool >= 0 and (vie.pool == 0 or monde.conservation)
        total, flows = now, dict(vie.bilan)
    if monde.conservation:
        assert vie.bilan["entree"] == vie.bilan["sortie"] == 0
        assert vie.bilan["depense"] > 0  # les dépenses ont bien circulé
    assert len(vie) > 0


def test_conservation_keeps_the_starting_total_and_returns_spending_as_food():
    monde = replace(SMALL, conservation=True)
    rng = np.random.default_rng(12)
    vie = Vie(CORPS.arch.random(rng, 60, 3), monde, rng, 0.5, 3, CORPS)
    start = vie.energie_totale()
    assert start == 60 * 20 + monde.gain * monde.food_cap * monde.cells  # aucune réserve
    for _ in range(300):
        vie.step()
    assert vie.energie_totale() == start
    # La réserve ne garde que ce qui n'a pas encore été rendu : la dépense de ce pas, le
    # reste d'une unité, et ce qui a débordé de cases pleines.
    assert vie.pool < monde.gain + vie.bilan["depense"]


def test_recycled_waste_becomes_food_on_its_own_cell():
    monde = Monde(height=1, width=8, inflow=0.0, tox=np.inf, decay=1.0, recyclage=1.0)
    vie = Vie(handmade()[None], monde, np.random.default_rng(13))
    vie.brain[:] = 0
    vie.food[:] = 0
    vie.waste[:] = [0, 0, 0, 3, 0, 0, 9, 0]
    vie.step()
    assert vie.waste.sum() == 0
    assert vie.food.tolist() == [0, 0, 0, 3, 0, 0, monde.food_cap, 0]  # 4 unités débordent
    half = Vie(handmade()[None], replace(monde, recyclage=0.5), np.random.default_rng(14))
    half.food[:] = 0
    half.waste[:] = 4000
    half.step()
    assert half.waste.sum() == 0 and (half.food == monde.food_cap).all()  # plafond atteint
    few = Vie(
        handmade()[None], replace(monde, recyclage=0.5, food_cap=10**6), np.random.default_rng(15)
    )
    few.food[:] = 0
    few.waste[:] = 1000
    few.step()
    assert 3600 <= few.food.sum() <= 4400  # la moitié de 8 000


def test_diffusion_moves_food_to_the_four_neighbours_only():
    monde = Monde(height=5, width=5, inflow=0.0, tox=np.inf, diffusion=1.0)
    vie = Vie(handmade()[None], monde, np.random.default_rng(16))
    vie.brain[:] = 0
    vie.cell[:] = 0
    vie.food[:] = 0
    vie.food[12] = 4  # case centrale (2, 2)
    vie.step()
    neighbours = [7, 17, 11, 13]  # nord, sud, ouest, est
    assert vie.food[12] == 0 and vie.food[neighbours].sum() == 4
    assert vie.food.sum() == 4
    torus = Vie(handmade()[None], monde, np.random.default_rng(17))
    torus.brain[:] = 0
    torus.food[:] = 0
    torus.food[0] = 4  # coin : les voisins sont de l'autre côté du tore
    torus.step()
    assert torus.food[[20, 5, 4, 1]].sum() == 4


def test_diffusion_neither_creates_nor_destroys_food_and_respects_the_cap():
    monde = Monde(height=6, width=7, inflow=0.0, tox=np.inf, diffusion=0.7, food_cap=3)
    vie = Vie(handmade()[None], monde, np.random.default_rng(20))
    vie.brain[:] = 0
    full = Vie(handmade()[None], monde, np.random.default_rng(21))
    full.brain[:] = 0
    rng = np.random.default_rng(22)
    vie.food[:] = rng.integers(0, 4, size=monde.cells)
    start = vie.food.copy()
    total = vie.food.sum()
    for _ in range(50):
        vie.step()
        full.step()
        assert vie.food.sum() == total and vie.food.max() <= monde.food_cap
    assert (full.food == monde.food_cap).all()  # tout est plein : rien ne bouge
    assert not np.array_equal(vie.food, start)  # la nourriture a bien bougé


def test_accidental_deaths_leave_their_energy_as_food_when_corpses_are_on():
    monde = Monde(height=1, width=8, inflow=0.0, tox=np.inf, accident=1.0, cadavres=True)
    vie = Vie(np.stack([handmade()] * 4), monde, np.random.default_rng(18))
    vie.brain[:] = 0  # n'ingère pas, ne bouge pas : il paie l'entretien, 10 - 1 = 9
    vie.cell[:] = [0, 0, 0, 5]
    vie.food[:] = 0
    vie.step()
    assert len(vie) == 0 and vie.counts["accidents"] == 4 and vie.counts["deaths"] == 4
    # 9 // 4 = 2 unités chacun ; la case 0 en reçoit 6, plafonnées à 5 (1 unité perdue)
    assert vie.food.tolist() == [5, 0, 0, 0, 0, 2, 0, 0]
    assert vie.bilan["sortie"] == 4 * 1 + 4 * 1 + 1 * 4  # entretien, restes, débordement
    plain = Vie(handmade()[None], replace(monde, cadavres=False), np.random.default_rng(19))
    plain.brain[:] = 0
    plain.food[:] = 0
    plain.step()
    assert len(plain) == 0 and plain.food.sum() == 0 and plain.bilan["sortie"] == 10


def test_impossible_combinations_are_refused():
    with pytest.raises(ValueError):
        Monde(neutral=True, recyclage=0.5)
    with pytest.raises(ValueError):
        Monde(conservation=True, recyclage=0.5)
    with pytest.raises(ValueError):
        Monde(cadavres=True)
    with pytest.raises(ValueError):
        Monde(diffusion=1.5)
