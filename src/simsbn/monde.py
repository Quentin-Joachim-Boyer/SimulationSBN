"""Monde en grille : une ressource, un déchet toxique, des agents qui se déplacent.

Chaque case d'une grille torique porte un stock de nourriture et un stock de déchet.
Un agent est un capteur et un cerveau SBN de trois nœuds (``ARCH``, le même génotype
que dans :mod:`simsbn.milieu`) :

- nœud ``EAT`` du cerveau : « ingérer » ; nœud ``MOVE`` : « se déplacer » ; le
  troisième est caché ;
- le capteur « bien-être » vaut 1 si l'énergie de l'agent a augmenté au pas précédent.

Ingérer, c'est absorber le milieu de sa case : une unité de nourriture s'il en reste,
et le déchet présent, qui empoisonne. Chaque unité ingérée laisse une unité de déchet.
Les agents ne s'influencent donc qu'à travers les cases qu'ils vident et polluent.

Une grille 1 × 1 est un milieu bien mélangé : :meth:`Monde.melange` la construit avec
les mêmes totaux. Protocole : ``journal/2026-11-14_monde-dechet.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from simsbn.evolution import mutate
from simsbn.milieu import ARCH, step_brains

EAT, MOVE = 0, 1  # nœuds d'action, parmi les trois nœuds du cerveau
STEPS = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]])  # déplacements (ligne, colonne)


@dataclass(frozen=True)
class Monde:
    """Règles du monde. Les stocks et le seuil ``tox`` sont donnés par case.

    Avec ``neutral=True``, la nourriture est tirée au sort entre les vivants et chacun
    paie ``upkeep + eat_cost`` : ni la position ni le comportement n'ont d'effet.
    """

    height: int = 32
    width: int = 32
    inflow: float = 200.0  # unités de nourriture par pas, sur tout le monde
    food_cap: int = 5  # nourriture maximale d'une case
    tox: float = 20.0  # stock de déchet d'une case où l'empoisonnement est certain
    decay: float = 0.05  # part du déchet qui disparaît à chaque pas
    gain: int = 4
    upkeep: int = 1
    eat_cost: int = 1
    move_cost: int = 1
    poison: int = 4
    divide_at: int = 20
    neutral: bool = False

    @property
    def cells(self) -> int:
        return self.height * self.width

    def melange(self) -> Monde:
        """Le même monde réduit à une seule case, à totaux égaux."""
        return replace(
            self, height=1, width=1, food_cap=self.food_cap * self.cells, tox=self.tox * self.cells
        )


class Vie:
    """Une population vivant dans un monde ; :meth:`step` avance d'un pas.

    Attributs, un élément par agent vivant : ``population`` (génotypes ``(N, 4, 4)``),
    ``brain`` ``(N, 3)``, ``sensor``, ``energy``, ``cell`` (indice ``ligne * largeur +
    colonne``), ``ident`` (numéro unique) et ``lineage`` (numéro de l'ancêtre de départ).
    ``fed`` et ``poisoned`` disent ce qui est arrivé à l'agent au dernier pas (faux pour
    un nouveau-né). ``food`` et ``waste`` ont un élément par case.
    """

    def __init__(
        self,
        population: np.ndarray,
        monde: Monde,
        rng: np.random.Generator,
        mutation_rate: float = 0.1,
        bound: int = 3,
    ):
        self.monde, self.rng = monde, rng
        self.mutation_rate, self.bound = mutation_rate, bound
        self.population = np.array(population, dtype=np.int64)
        n = len(self.population)
        self.brain = rng.integers(0, 2, size=(n, ARCH.n_brain))
        self.sensor = np.ones(n, dtype=np.int64)
        self.energy = np.full(n, monde.divide_at // 2, dtype=np.int64)
        self.cell = rng.integers(0, monde.cells, size=n)
        self.ident = np.arange(n)
        self.lineage = np.arange(n)
        self.next_ident = n
        self.fed = np.zeros(n, dtype=bool)
        self.poisoned = np.zeros(n, dtype=bool)
        self.food = np.full(monde.cells, monde.food_cap, dtype=np.int64)
        self.waste = np.zeros(monde.cells, dtype=np.int64)
        self.t = 0
        self._reset_counts()

    def __len__(self) -> int:
        return len(self.population)

    def _reset_counts(self) -> None:
        # Les trois premiers sont ventilés selon la valeur du capteur (0 ou 1).
        self.counts = {key: np.zeros(2) for key in ("agents", "eat", "move")}
        self.counts |= dict.fromkeys(("served", "poisoned", "births", "deaths", "steps"), 0)

    def stats(self) -> dict[str, float]:
        """Activité depuis le dernier appel, puis remise à zéro des compteurs."""
        c = self.counts
        with np.errstate(invalid="ignore", divide="ignore"):
            eat, move = c["eat"] / c["agents"], c["move"] / c["agents"]
            out = {
                "manger_0": eat[0],
                "manger_1": eat[1],
                "bouger_0": move[0],
                "bouger_1": move[1],
                "dependance": move[0] - move[1],
                "capteur": c["agents"][1] / c["agents"].sum(),
                "servies": c["served"] / c["eat"].sum() if c["eat"].sum() else np.nan,
                "empoisonnees": c["poisoned"] / c["eat"].sum() if c["eat"].sum() else np.nan,
                "naissances": c["births"] / max(c["steps"], 1),
            }
        self._reset_counts()
        return {key: float(value) for key, value in out.items()}

    def step(self) -> None:
        w, rng = self.monde, self.rng
        n = len(self)
        eat = self.brain[:, EAT].astype(bool)
        move = self.brain[:, MOVE].astype(bool)
        for key, flags in (("agents", np.ones(n)), ("eat", eat), ("move", move)):
            self.counts[key] += np.bincount(self.sensor, weights=flags, minlength=2)

        # 1. Le milieu : arrivée de nourriture, disparition de déchet.
        if not w.neutral:
            arrivals = rng.poisson(w.inflow / w.cells, size=w.cells)
            self.food = np.minimum(self.food + arrivals, w.food_cap)
            self.waste = rng.binomial(self.waste, 1 - w.decay)

        # 2. Déplacement vers une case voisine tirée au sort (tore).
        movers = np.flatnonzero(move)
        if len(movers):
            delta = STEPS[rng.integers(0, len(STEPS), size=len(movers))]
            row = (self.cell[movers] // w.width + delta[:, 0]) % w.height
            col = (self.cell[movers] % w.width + delta[:, 1]) % w.width
            self.cell[movers] = row * w.width + col

        # 3. Ingestion : nourriture tirée au sort par case, poison selon le déchet présent.
        units = np.zeros(n, dtype=np.int64)
        poisoned = np.zeros(n, dtype=bool)
        if w.neutral:
            units[rng.permutation(n)[: rng.poisson(w.inflow)]] = 1
            cost = np.full(n, w.upkeep + w.eat_cost)
        else:
            askers = np.flatnonzero(eat)
            if len(askers):
                where = self.cell[askers]
                poisoned[askers] = rng.random(len(askers)) < self.waste[where] / w.tox
                order = np.lexsort((rng.random(len(askers)), where))  # par case, puis au hasard
                sorted_cells = where[order]
                position = np.arange(len(order))
                first = np.r_[True, sorted_cells[1:] != sorted_cells[:-1]]
                rank = position - np.maximum.accumulate(np.where(first, position, 0))
                winners = askers[order[rank < self.food[sorted_cells]]]
                units[winners] = 1
                np.subtract.at(self.food, self.cell[winners], 1)
                np.add.at(self.waste, self.cell[winners], 1)
            cost = w.upkeep + w.eat_cost * eat + w.move_cost * move + w.poison * poisoned
        self.counts["served"] += int(units.sum())
        self.counts["poisoned"] += int(poisoned.sum())

        # 4. Énergie, capteur, cerveau.
        energy = self.energy + w.gain * units - cost
        self.sensor = (energy > self.energy).astype(np.int64)
        self.energy = energy
        self.fed, self.poisoned = units > 0, poisoned
        self.brain = step_brains(self.population, self.sensor, self.brain)

        # 5. Morts, puis divisions sur la case du parent.
        alive = self.energy > 0
        self.counts["deaths"] += int(n - alive.sum())
        names = ("population", "brain", "sensor", "energy", "cell", "ident", "lineage")
        for name in (*names, "fed", "poisoned"):
            setattr(self, name, getattr(self, name)[alive])
        parents = np.flatnonzero(self.energy >= w.divide_at)
        if len(parents):
            share = self.energy[parents] // 2
            self.energy[parents] -= share
            children = self.population[parents].copy()
            mask = ARCH.mask()
            for k in np.flatnonzero(rng.random(len(parents)) < self.mutation_rate):
                children[k] = mutate(children[k], rng, self.bound, mask)
            idents = self.next_ident + np.arange(len(parents))
            self.next_ident += len(parents)
            self.population = np.concatenate([self.population, children])
            self.energy = np.concatenate([self.energy, share])
            self.ident = np.concatenate([self.ident, idents])
            for name in ("fed", "poisoned"):
                born = np.zeros(len(parents), dtype=bool)
                setattr(self, name, np.concatenate([getattr(self, name), born]))
            for name in ("brain", "sensor", "cell", "lineage"):
                values = getattr(self, name)
                setattr(self, name, np.concatenate([values, values[parents]]))
            self.counts["births"] += len(parents)
        self.counts["steps"] += 1
        self.t += 1


def handmade(**arcs: int) -> np.ndarray:
    """Génotype dont les seuls poids non nuls sont donnés, par exemple ``e_e=1``.

    Noms des nœuds : ``s`` (capteur), ``e`` (ingérer), ``m`` (se déplacer), ``h`` (caché).
    """
    index = {"s": 0, "e": 1, "m": 2, "h": 3}
    W = np.zeros((ARCH.d, ARCH.d), dtype=np.int64)
    W[0, 0] = 1
    for name, weight in arcs.items():
        source, target = name.split("_")
        W[index[source], index[target]] = weight
    return W


# Agents de référence, construits à la main. Le poids capteur -> ingérer ne sert qu'à
# lancer l'ingestion au départ ; elle s'entretient ensuite seule.
IMMOBILE = handmade(s_e=1, e_e=1)  # ingère toujours, ne bouge jamais
MARCHEUR = handmade(s_e=1, e_e=1, e_m=1)  # ingère et bouge toujours
REACTIF = handmade(s_e=1, e_e=1, e_m=1, s_m=-3)  # bouge seulement quand le capteur vaut 0
# Bouge toujours quand le capteur vaut 0, un pas sur deux quand il vaut 1 (ajouté après
# l'expérience : c'est le comportement que l'évolution a trouvé en régime espace).
ALTERNANT = handmade(s_e=1, e_e=1, e_m=2, m_m=-1, s_m=-1)
