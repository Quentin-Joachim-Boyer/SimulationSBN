"""Milieu partagé : des agents y survivent ou y meurent, sans cible ni fitness explicite.

Le milieu est bien mélangé et contient deux ressources, X et Y, en stocks entiers. Un
agent est un capteur et un cerveau SBN de trois nœuds (``ARCH``) :

- nœud 0 du cerveau : action « ingérer X » ; nœud 1 : « ingérer Y » ; nœud 2 : caché ;
- le capteur vaut 1 si l'agent a obtenu au moins une unité au pas précédent. C'est le
  milieu qui l'impose : la boucle de poids 1 de l'architecture n'est pas utilisée ici.

Les agents modifient le milieu en vidant les stocks, et ne s'influencent que par là.
Protocole et hypothèses : ``journal/2026-11-14_milieu-partage.md``.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from simsbn.agents import Architecture
from simsbn.core import state_bits
from simsbn.evolution import mutate

ARCH = Architecture(n_in=1, n_brain=3, n_out=0)
N_ACTIONS = 2  # les deux premiers nœuds du cerveau


@dataclass(frozen=True)
class Milieu:
    """Règles du milieu. ``season=None`` : apport constant, partagé entre X et Y.

    Avec ``neutral=True``, l'apport est tiré au sort entre les vivants et chacun paie
    une action, quel que soit son comportement : même démographie, aucune sélection.
    """

    inflow: int = 200
    season: int | None = 50
    cap: int = 1000
    gain: int = 3
    upkeep: int = 1
    action_cost: int = 1
    divide_at: int = 20
    neutral: bool = False

    def supply(self, t: int) -> np.ndarray:
        """Unités de X et de Y apportées au pas ``t``."""
        if self.season is None:
            return np.array([self.inflow // 2, self.inflow - self.inflow // 2])
        out = np.zeros(N_ACTIONS, dtype=np.int64)
        out[(t // self.season) % N_ACTIONS] = self.inflow
        return out


@dataclass(frozen=True)
class Snapshot:
    """État d'une population au pas ``t``, et activité depuis le relevé précédent."""

    t: int
    population: np.ndarray  # (N, 4, 4), génotypes des vivants
    energy: np.ndarray
    stock: np.ndarray
    act: np.ndarray  # part des pas-agents avec action X, avec action Y
    served: float  # part des demandes servies


def step_brains(population, sensor, brain) -> np.ndarray:
    """État suivant des cerveaux ``(N, 3)``, le capteur ``(N,)`` étant imposé.

    Seuls le capteur et le cerveau sont lus : d'éventuels nœuds moteurs, rangés après
    eux dans la matrice, n'ont aucun effet.
    """
    inputs = np.concatenate([sensor[:, None], brain], axis=1)
    weights = population[:, : ARCH.d, 1 : ARCH.d]
    return (np.einsum("ni,nij->nj", inputs, weights) > 0).astype(np.int64)


def live(
    population: np.ndarray,
    milieu: Milieu,
    steps: int,
    rng: np.random.Generator,
    mutation_rate: float = 0.1,
    bound: int = 3,
    record_every: int = 100,
) -> Iterator[Snapshot]:
    """Fait vivre une population ``(N, 4, 4)`` dans le milieu pendant ``steps`` pas.

    Produit un relevé au départ puis tous les ``record_every`` pas ; s'arrête après le
    relevé qui constate l'extinction.
    """
    population = np.array(population, dtype=np.int64)
    n = len(population)
    mask = ARCH.mask()
    brain = rng.integers(0, 2, size=(n, ARCH.n_brain))
    sensor = np.ones(n, dtype=np.int64)
    energy = np.full(n, milieu.divide_at // 2, dtype=np.int64)
    stock = np.full(N_ACTIONS, milieu.cap, dtype=np.int64)
    acted = np.zeros(N_ACTIONS)
    agent_steps = requests = units_served = 0
    yield Snapshot(0, population, energy, stock.copy(), acted.copy(), 0.0)

    for t in range(steps):
        n = len(population)
        act = brain[:, :N_ACTIONS]
        units = np.zeros(n, dtype=np.int64)
        if milieu.neutral:
            units[rng.permutation(n)[: milieu.inflow]] = 1
            cost = np.full(n, milieu.upkeep + milieu.action_cost)
        else:
            stock = np.minimum(stock + milieu.supply(t), milieu.cap)
            for r in range(N_ACTIONS):
                askers = np.flatnonzero(act[:, r])
                winners = rng.permutation(askers)[: stock[r]]
                units[winners] += 1
                stock[r] -= len(winners)
            cost = milieu.upkeep + milieu.action_cost * act.sum(axis=1)
            requests += int(act.sum())
            units_served += int(units.sum())
        acted += act.sum(axis=0)
        agent_steps += n
        energy = energy + milieu.gain * units - cost
        sensor = (units > 0).astype(np.int64)
        brain = step_brains(population, sensor, brain)

        alive = energy > 0
        population, brain, sensor, energy = (a[alive] for a in (population, brain, sensor, energy))
        parents = np.flatnonzero(energy >= milieu.divide_at)
        if len(parents):
            share = energy[parents] // 2
            energy[parents] -= share
            children = population[parents].copy()
            for k in np.flatnonzero(rng.random(len(parents)) < mutation_rate):
                children[k] = mutate(children[k], rng, bound, mask)
            population = np.concatenate([population, children])
            brain = np.concatenate([brain, brain[parents]])
            sensor = np.concatenate([sensor, sensor[parents]])
            energy = np.concatenate([energy, share])

        if (t + 1) % record_every == 0 or len(population) == 0:
            yield Snapshot(
                t + 1,
                population,
                energy,
                stock.copy(),
                acted / max(agent_steps, 1),
                units_served / requests if requests else 0.0,
            )
            acted = np.zeros(N_ACTIONS)
            agent_steps = requests = units_served = 0
        if len(population) == 0:
            return


def solitary_viable(population: np.ndarray, milieu: Milieu, cycles: int = 4) -> np.ndarray:
    """Viabilité de chaque génotype seul dans le milieu, sans compétition (déterministe).

    L'agent est servi dès qu'il demande une ressource apportée à ce pas. Il part au
    début d'une saison X, capteur à 1, énergie ``divide_at // 2`` ; à ``divide_at`` il
    se divise et l'on suit l'une des deux moitiés. Un génotype est viable s'il survit à
    ``cycles`` cycles de saisons depuis au moins un des 8 états de départ du cerveau.
    """
    population = np.asarray(population)
    g = len(population)
    starts = state_bits(ARCH.n_brain)  # (8, 3)
    brain = np.broadcast_to(starts, (g, *starts.shape)).copy()
    sensor = np.ones((g, len(starts)), dtype=np.int64)
    energy = np.full((g, len(starts)), milieu.divide_at // 2, dtype=np.int64)
    alive = np.ones((g, len(starts)), dtype=bool)
    weights = population[:, :, 1:]
    period = 2 * milieu.season if milieu.season else 100
    for t in range(cycles * period):
        act = brain[:, :, :N_ACTIONS]
        units = (act * (milieu.supply(t) > 0)).sum(axis=2)
        energy = energy + milieu.gain * units - milieu.upkeep - milieu.action_cost * act.sum(axis=2)
        alive &= energy > 0
        energy = np.where(energy >= milieu.divide_at, energy - energy // 2, energy)
        sensor = (units > 0).astype(np.int64)
        inputs = np.concatenate([sensor[:, :, None], brain], axis=2)
        brain = (np.einsum("gsi,gij->gsj", inputs, weights) > 0).astype(np.int64)
    return alive.any(axis=1)
