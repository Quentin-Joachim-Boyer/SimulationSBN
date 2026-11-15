import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import Corps, Monde, Vie
from simsbn.structure import KINDS, Classifier
from simsbn.suivi import MEASURES, VARIETE, brains, par_population, suivre, variete


def test_suivre_records_every_measure_and_stops_at_extinction():
    monde = Monde(height=8, width=8, inflow=40.0)
    corps = Corps(("ingérer", "bouger"))
    start = corps.arch.random(np.random.default_rng(0), 120, 3)
    vie = Vie(start, monde, np.random.default_rng(1), corps=corps)
    series = suivre(vie, 400, 100, Classifier(), monde.cells)
    assert series.shape == (len(MEASURES), 5)
    assert series[0, 0] == 120 and series[0, -1] == len(vie) > 0
    winter = [MEASURES.index(m) for m in ("manger_hiver", "bouger_hiver", "economie_hiver")]
    assert np.isnan(series[winter, 1:]).all()  # monde sans saisons
    assert not np.isnan(np.delete(series, winter, axis=0)[:, 1:]).any()
    assert brains(vie.population).shape[1:] == (ARCH.d, ARCH.d)

    doomed = Vie(np.zeros((5, 4, 4), dtype=np.int64), monde, np.random.default_rng(2))
    series = suivre(doomed, 400, 100, Classifier(), monde.cells)
    assert series[0, :2].tolist() == [5, 0] and np.isnan(series[0, 2:]).all()


def test_par_population_averages_the_second_half_and_blanks_extinct_populations():
    series = np.zeros((len(MEASURES), 2, 5))
    series[:, 0] = [0, 0, 0, 10, 20]  # relevés 3 et 4 : seconde moitié
    series[:, 1] = [9, 9, 9, 9, 9]
    out = par_population(series, extinct=[False, True])
    assert (out[:, 0] == 15).all()
    assert out[0, 1] == 9 and np.isnan(out[1:, 1]).all()
    assert len(KINDS) == 11


def test_variete_counts_lineages_genotypes_and_differing_weights():
    corps = Corps(("ingérer", "bouger"))
    mask = corps.arch.mask()
    founder = corps.arch.random(np.random.default_rng(0), 1, 3)[0]
    clones = np.repeat(founder[None], 40, axis=0)
    rng = np.random.default_rng(1)
    clones_only = variete(clones, np.arange(40) % 4, founder, mask, rng)
    assert dict(zip(VARIETE, clones_only, strict=True)) == {
        "lignees": 4.0, "genotypes": 1.0, "distance_fondateur": 0.0, "distance_paires": 0.0,
    }  # fmt: skip

    mutant = founder.copy()
    i, j = np.argwhere(mask)[0]
    mutant[i, j] += 1  # un seul poids change
    mixed = np.concatenate([clones[:20], np.repeat(mutant[None], 20, axis=0)])
    out = dict(
        zip(VARIETE, variete(mixed, np.zeros(40, int), founder, mask, rng, 4000), strict=True)
    )
    assert out["lignees"] == 1 and out["genotypes"] == 2
    assert out["distance_fondateur"] == 0.5  # la moitié des agents diffère d'un poids
    assert abs(out["distance_paires"] - 0.5) < 0.05  # une paire sur deux est mixte
    # un poids hors du masque (capteur vers lui-même) ne compte pas
    outside = founder.copy()
    outside[0, 0] += 5
    assert variete(outside[None], np.zeros(1, int), founder, mask, rng)[2] == 0.0
