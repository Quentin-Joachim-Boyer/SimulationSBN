import numpy as np

from simsbn.milieu import ARCH
from simsbn.monde import Corps, Monde, Vie
from simsbn.structure import KINDS, Classifier
from simsbn.suivi import MEASURES, brains, par_population, suivre


def test_suivre_records_every_measure_and_stops_at_extinction():
    monde = Monde(height=8, width=8, inflow=40.0)
    corps = Corps(("ingérer", "bouger"))
    start = corps.arch.random(np.random.default_rng(0), 120, 3)
    vie = Vie(start, monde, np.random.default_rng(1), corps=corps)
    series = suivre(vie, 400, 100, Classifier(), monde.cells)
    assert series.shape == (len(MEASURES), 5)
    assert series[0, 0] == 120 and series[0, -1] == len(vie) > 0
    assert not np.isnan(series[:, 1:]).any()
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
    assert len(KINDS) == 9
