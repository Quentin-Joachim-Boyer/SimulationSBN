import numpy as np

from simsbn.milieu import ARCH, Milieu, live, solitary_viable


def agent(**arcs):
    """Génotype dont les seuls poids non nuls sont donnés, par exemple ``x_x=1``.

    Noms des nœuds : ``s`` (capteur), ``x``, ``y`` (actions), ``h`` (caché).
    """
    index = {"s": 0, "x": 1, "y": 2, "h": 3}
    W = np.zeros((ARCH.d, ARCH.d), dtype=np.int64)
    W[0, 0] = 1
    for name, weight in arcs.items():
        source, target = name.split("_")
        W[index[source], index[target]] = weight
    return W


SPECIALIST = agent(x_x=1, s_x=1)  # ingère X pour toujours, une fois lancé
INERT = agent()


def run(population, milieu, steps, seed=0, **kwargs):
    return list(live(population, milieu, steps, np.random.default_rng(seed), **kwargs))


def test_supply_alternates_with_the_seasons():
    milieu = Milieu(inflow=200, season=50)
    assert milieu.supply(0).tolist() == [200, 0]
    assert milieu.supply(49).tolist() == [200, 0]
    assert milieu.supply(50).tolist() == [0, 200]
    assert milieu.supply(100).tolist() == [200, 0]
    assert Milieu(inflow=200, season=None).supply(7).tolist() == [100, 100]


def test_inert_agents_starve_when_their_reserve_runs_out():
    # Sans poids, le cerveau s'éteint après le premier pas : -1 par pas, mort au pas 10,
    # ou un peu plus tard pour ceux qu'un état de départ allumé a nourris une fois.
    snaps = run(np.stack([INERT] * 5), Milieu(), 20, record_every=1)
    sizes = {s.t: len(s.population) for s in snaps}
    assert sizes[9] == 5 and sizes[10] < 5
    assert len(snaps[-1].population) == 0 and snaps[-1].t <= 14  # arrêt à l'extinction


def test_specialists_fill_a_constant_milieu_up_to_what_it_feeds():
    # 100 unités de X par pas, 3 d'énergie l'unité, 2 de dépense par pas : 150 agents.
    milieu = Milieu(inflow=200, season=None)
    snaps = run(np.stack([SPECIALIST] * 20), milieu, 600, mutation_rate=0.0)
    sizes = [len(s.population) for s in snaps[-3:]]
    assert all(120 <= n <= 180 for n in sizes)
    assert snaps[-1].act[1] == 0  # personne n'ingère Y
    assert snaps[-1].stock[1] == milieu.cap  # Y reste plein, X est vidé
    assert snaps[-1].stock[0] == 0


def test_specialists_die_out_in_the_off_season():
    snaps = run(np.stack([SPECIALIST] * 20), Milieu(season=50), 400, mutation_rate=0.0)
    assert len(snaps[-1].population) == 0


def test_neutral_demography_ignores_behaviour():
    # 200 unités tirées au sort, 2 de dépense par pas : équilibre vers 300 agents.
    milieu = Milieu(neutral=True)
    for genotype in (SPECIALIST, INERT):
        snaps = run(np.stack([genotype] * 100), milieu, 800, mutation_rate=0.0)
        assert 240 <= len(snaps[-1].population) <= 360


def test_live_is_reproducible_and_mutates_only_evolving_weights():
    start = ARCH.random(np.random.default_rng(1), 200, 3)
    a = run(start, Milieu(neutral=True), 300, seed=5)
    b = run(start, Milieu(neutral=True), 300, seed=5)
    assert all(np.array_equal(s.population, u.population) for s, u in zip(a, b, strict=True))
    final = a[-1].population
    assert (np.abs(final) <= 3).all()
    assert (final[:, ~ARCH.mask()] == start[0][~ARCH.mask()]).all()


def test_solitary_viability_on_hand_built_agents():
    population = np.stack([SPECIALIST, INERT])
    assert solitary_viable(population, Milieu(season=None)).tolist() == [True, False]
    assert solitary_viable(population, Milieu(season=50)).tolist() == [False, False]
