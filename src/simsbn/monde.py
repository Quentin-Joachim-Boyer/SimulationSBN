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

from simsbn.agents import Architecture
from simsbn.evolution import mutate
from simsbn.milieu import ARCH, step_brains

EAT, MOVE = 0, 1  # nœuds d'action, parmi les trois nœuds du cerveau
STEPS = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]])  # déplacements (ligne, colonne)
DIRECTIONS = {"nord": (-1, 0), "sud": (1, 0), "ouest": (0, -1), "est": (0, 1)}
ROLES = ("ingérer", "bouger", *DIRECTIONS)  # « bouger » : une case voisine au hasard


@dataclass(frozen=True)
class Corps:
    """Comment les actions d'un agent se lisent sur son réseau.

    Sans moteur (le défaut), elles se lisent directement sur les nœuds ``EAT`` et
    ``MOVE`` du cerveau. Sinon chaque moteur est un nœud lecteur, rangé après le cerveau
    dans la matrice : il lit le cerveau seul, et rien ne revient de lui.

    - ``delay=True`` : le moteur est un nœud SBN ordinaire, mis à jour en même temps que
      le cerveau ; il a donc un pas de retard sur lui, et l'agent réagit en deux pas ;
    - ``delay=False`` : le moteur suit le cerveau du pas même.

    Les effets des moteurs de déplacement s'additionnent : nord et sud s'annulent, nord
    et est donnent une diagonale. Chaque moteur allumé coûte.

    ``ticks`` est le nombre de pas d'agent par pas du milieu : le capteur est tenu
    pendant ces pas, le cerveau et les moteurs se mettent à jour ``ticks`` fois, et
    l'action est lue à la fin. Avec ``ticks=1``, rien ne change. Ces pas ne coûtent
    rien de plus : le coût d'un rythme rapide est une question laissée ouverte.
    """

    motors: tuple[str, ...] = ()
    delay: bool = True
    ticks: int = 1

    def __post_init__(self):
        if self.ticks < 1:
            raise ValueError(f"ticks doit valoir au moins 1, pas {self.ticks}")
        unknown = set(self.motors) - set(ROLES)
        if unknown or len(set(self.motors)) != len(self.motors):
            raise ValueError(f"moteurs inconnus ou répétés : {self.motors}")

    @property
    def arch(self) -> Architecture:
        return Architecture(ARCH.n_in, ARCH.n_brain, len(self.motors))

    @property
    def lagged(self) -> bool:
        """Vrai si les actions ont un pas de retard sur le cerveau."""
        return bool(self.motors) and self.delay

    def one_hot(self, genotype: np.ndarray) -> np.ndarray:
        """Génotype à lecture directe, porté dans ce corps : un nœud, un moteur.

        ``genotype`` est une matrice ``(4, 4)`` de :mod:`simsbn.milieu`. Le moteur
        « ingérer » lit le seul nœud ``EAT`` et « bouger » le seul nœud ``MOVE``, avec
        un poids 1 ; les autres moteurs ne lisent rien.
        """
        W = np.zeros((self.arch.d, self.arch.d), dtype=np.int64)
        W[: ARCH.d, : ARCH.d] = genotype
        for j, role in enumerate(self.motors):
            node = {"ingérer": EAT, "bouger": MOVE}.get(role)
            if node is not None:
                W[ARCH.n_in + node, ARCH.d + j] = 1
        return W


def read_motors(population, brain) -> np.ndarray:
    """Valeur des moteurs ``(N, k)`` lue sur des cerveaux ``(N, 3)``."""
    weights = population[:, ARCH.n_in : ARCH.d, ARCH.d :]
    return (np.einsum("ni,nij->nj", brain, weights) > 0).astype(np.int64)


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
    summer: int | None = None  # durée d'un été en pas ; None : pas de saisons
    winter: int = 0  # durée d'un hiver ; la nourriture n'arrive qu'en été

    @property
    def cells(self) -> int:
        return self.height * self.width

    def is_summer(self, t: int) -> bool:
        """Vrai si la nourriture arrive au pas ``t``. L'année commence par l'été.

        Les agents ne perçoivent pas la saison. En régime neutre, l'hiver ne coûte que
        l'entretien, comme à un agent en veille.
        """
        return self.summer is None or t % (self.summer + self.winter) < self.summer

    def melange(self) -> Monde:
        """Le même monde réduit à une seule case, à totaux égaux."""
        return replace(
            self, height=1, width=1, food_cap=self.food_cap * self.cells, tox=self.tox * self.cells
        )


class Vie:
    """Une population vivant dans un monde ; :meth:`step` avance d'un pas.

    Attributs, un élément par agent vivant : ``population`` (génotypes ``(N, d, d)``,
    ``d = 4`` sans moteur), ``brain`` ``(N, 3)``, ``motor`` ``(N, k)``, ``sensor``,
    ``energy``, ``cell`` (indice ``ligne * largeur + colonne``), ``ident`` (numéro
    unique) et ``lineage`` (numéro de l'ancêtre de départ). ``sensor_prev`` est le capteur
    du pas d'avant. ``fed`` et ``poisoned`` disent ce qui est arrivé à l'agent au dernier
    pas (faux pour un nouveau-né). ``food`` et ``waste`` ont un élément par case.
    """

    def __init__(
        self,
        population: np.ndarray,
        monde: Monde,
        rng: np.random.Generator,
        mutation_rate: float = 0.1,
        bound: int = 3,
        corps: Corps | None = None,
    ):
        self.monde, self.rng = monde, rng
        self.mutation_rate, self.bound = mutation_rate, bound
        self.corps = corps or Corps()
        self.population = np.array(population, dtype=np.int64)
        n, d = len(self.population), self.corps.arch.d
        if self.population.shape[1:] != (d, d):
            raise ValueError(f"génotypes de forme {self.population.shape[1:]}, attendu {(d, d)}")
        self.brain = rng.integers(0, 2, size=(n, ARCH.n_brain))
        self.sensor = np.ones(n, dtype=np.int64)
        self.energy = np.full(n, monde.divide_at // 2, dtype=np.int64)
        self.cell = rng.integers(0, monde.cells, size=n)
        self.ident = np.arange(n)
        self.lineage = np.arange(n)
        self.next_ident = n
        self.fed = np.zeros(n, dtype=bool)
        self.poisoned = np.zeros(n, dtype=bool)
        self.sensor_prev = np.ones(n, dtype=np.int64)
        self.last_delta = np.zeros((n, 2), dtype=np.int64)  # dernier déplacement de chaque agent
        if self.corps.lagged:  # un nœud ordinaire part d'un état quelconque
            self.motor = rng.integers(0, 2, size=(n, len(self.corps.motors)))
        else:
            self.motor = read_motors(self.population, self.brain)
        self.food = np.full(monde.cells, monde.food_cap, dtype=np.int64)
        self.waste = np.zeros(monde.cells, dtype=np.int64)
        self.t = 0
        self._reset_counts()

    def __len__(self) -> int:
        return len(self.population)

    def _reset_counts(self) -> None:
        # Les trois premiers sont ventilés selon la valeur du capteur (0 ou 1) à laquelle
        # l'action a pu réagir : celui du pas d'avant, ou d'il y a deux pas avec retard.
        # Les trois suivants selon la saison (0 : hiver, 1 : été).
        names = ("agents", "eat", "move", "agents_season", "eat_season", "move_season")
        self.counts = {key: np.zeros(2) for key in names}
        self.counts |= dict.fromkeys(
            ("served", "poisoned", "births", "deaths", "steps", "persist_sum", "persist_n"), 0
        )

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
                "persistance": c["persist_sum"] / c["persist_n"] if c["persist_n"] else np.nan,
            }
            eat, move = c["eat_season"] / c["agents_season"], c["move_season"] / c["agents_season"]
            out |= {
                "manger_hiver": eat[0],
                "manger_ete": eat[1],
                "bouger_hiver": move[0],
                "bouger_ete": move[1],
                "economie_hiver": eat[1] - eat[0],
            }
        self._reset_counts()
        return {key: float(value) for key, value in out.items()}

    def step(self) -> None:
        w, rng = self.monde, self.rng
        n = len(self)
        # Actions du pas : ingérer, bouger au hasard, et poussées des moteurs de direction.
        wander = np.zeros(n, dtype=bool)
        pushes = []
        if not self.corps.motors:
            eat = self.brain[:, EAT].astype(bool)
            wander = self.brain[:, MOVE].astype(bool)
        else:
            eat = np.zeros(n, dtype=bool)
            for j, role in enumerate(self.corps.motors):
                on = self.motor[:, j].astype(bool)
                if role == "ingérer":
                    eat = on
                elif role == "bouger":
                    wander = on
                else:
                    pushes.append((on, DIRECTIONS[role]))
        moves = wander.astype(np.int64)  # nombre de moteurs de déplacement allumés
        for on, _ in pushes:
            moves += on
        # Capteur auquel l'action a pu réagir : avec un seul pas d'agent et des moteurs
        # retardés, celui d'il y a deux pas ; sinon, le dernier connu.
        reacts_late = self.corps.lagged and self.corps.ticks == 1
        context = self.sensor_prev if reacts_late else self.sensor
        for key, flags in (("agents", np.ones(n)), ("eat", eat), ("move", moves > 0)):
            self.counts[key] += np.bincount(context, weights=flags, minlength=2)
            self.counts[key + "_season"][int(w.is_summer(self.t))] += flags.sum()
        summer = w.is_summer(self.t)

        # 1. Le milieu : arrivée de nourriture, disparition de déchet.
        if not w.neutral:
            arrivals = rng.poisson(w.inflow / w.cells if summer else 0.0, size=w.cells)
            self.food = np.minimum(self.food + arrivals, w.food_cap)
            self.waste = rng.binomial(self.waste, 1 - w.decay)

        # 2. Déplacement sur le tore : une case voisine au hasard pour « bouger », plus la
        #    somme des poussées des moteurs de direction.
        delta = np.zeros((n, 2), dtype=np.int64)
        movers = np.flatnonzero(wander)
        if len(movers):
            delta[movers] = STEPS[rng.integers(0, len(STEPS), size=len(movers))]
        for on, vector in pushes:
            delta[on] += vector
        # Persistance : cosinus entre deux déplacements successifs d'un même agent, compté
        # quand il se déplace aux deux pas. Une marche au hasard donne 0 en moyenne.
        both = (delta != 0).any(axis=1) & (self.last_delta != 0).any(axis=1)
        if both.any():
            a, b = delta[both].astype(float), self.last_delta[both].astype(float)
            cos = (a * b).sum(axis=1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1))
            self.counts["persist_sum"] += float(cos.sum())
            self.counts["persist_n"] += int(both.sum())
        self.last_delta = delta
        row = (self.cell // w.width + delta[:, 0]) % w.height
        col = (self.cell % w.width + delta[:, 1]) % w.width
        self.cell = row * w.width + col

        # 3. Ingestion : nourriture tirée au sort par case, poison selon le déchet présent.
        units = np.zeros(n, dtype=np.int64)
        poisoned = np.zeros(n, dtype=bool)
        if w.neutral:
            units[rng.permutation(n)[: rng.poisson(w.inflow if summer else 0.0)]] = 1
            cost = np.full(n, w.upkeep + (w.eat_cost if summer else 0))
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
            cost = w.upkeep + w.eat_cost * eat + w.move_cost * moves + w.poison * poisoned
        self.counts["served"] += int(units.sum())
        self.counts["poisoned"] += int(poisoned.sum())

        # 4. Énergie, capteur, puis cerveau et moteurs. Un moteur retardé lit le cerveau
        #    d'avant la mise à jour, comme tout nœud d'un SBN synchrone.
        energy = self.energy + w.gain * units - cost
        self.sensor_prev = self.sensor
        self.sensor = (energy > self.energy).astype(np.int64)
        self.energy = energy
        self.fed, self.poisoned = units > 0, poisoned
        for _ in range(self.corps.ticks):
            previous = self.brain
            self.brain = step_brains(self.population, self.sensor, previous)
            self.motor = read_motors(self.population, previous if self.corps.delay else self.brain)

        # 5. Morts, puis divisions sur la case du parent.
        alive = self.energy > 0
        self.counts["deaths"] += int(n - alive.sum())
        names = ("population", "brain", "sensor", "energy", "cell", "ident", "lineage")
        for name in (*names, "fed", "poisoned", "motor", "sensor_prev", "last_delta"):
            setattr(self, name, getattr(self, name)[alive])
        parents = np.flatnonzero(self.energy >= w.divide_at)
        if len(parents):
            share = self.energy[parents] // 2
            self.energy[parents] -= share
            children = self.population[parents].copy()
            mask = self.corps.arch.mask()
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
            for name in ("brain", "sensor", "cell", "lineage", "motor", "sensor_prev"):
                values = getattr(self, name)
                setattr(self, name, np.concatenate([values, values[parents]]))
            self.last_delta = np.concatenate([self.last_delta, np.zeros((len(parents), 2), int)])
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
