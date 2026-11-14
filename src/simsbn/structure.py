"""Mesures de structure d'agents à un capteur (``simsbn.milieu.ARCH``).

Quatre mesures par agent, dans l'ordre de ``KINDS`` :

- ``controle_cerveau`` : le cerveau seul (face « capteur = 0 ») a un nœud de contrôle ;
- ``psbn_cerveau`` : le cerveau seul est un PSBN ;
- ``scission_sbn`` : la face « capteur = 1 » de la dynamique complète est un SBN ;
- ``controle_interne`` : la décomposition PTBN la plus fine a plus de 2 feuilles.
"""

from __future__ import annotations

from itertools import product

import numpy as np

from simsbn.core import batch_dynamics, state_bits
from simsbn.milieu import ARCH
from simsbn.pluripotence import control_nodes, decomposition, is_psbn, split_is_sbn
from simsbn.sbf import restrict

KINDS = ["controle_cerveau", "psbn_cerveau", "scission_sbn", "controle_interne"]
SENSOR = ARCH.inputs[0]


class Classifier:
    """Mesures de structure d'une population, mémorisées par dynamique."""

    def __init__(self):
        self.kinds: dict[tuple[int, ...], tuple[bool, ...]] = {}

    def flags(self, population) -> np.ndarray:
        """Tableau booléen ``(N, 4)`` : une ligne par agent, une colonne par mesure."""
        out = []
        for f in map(tuple, batch_dynamics(population).tolist()):
            if f not in self.kinds:
                brain = tuple(restrict(f[j], ARCH.d, SENSOR, 0) for j in ARCH.brain)
                self.kinds[f] = (
                    bool(control_nodes(brain)),
                    is_psbn(brain),
                    split_is_sbn(f, SENSOR),
                    sum(decomposition(f, "tbn")) > 2,
                )
            out.append(self.kinds[f])
        return np.array(out, dtype=bool).reshape(len(out), len(KINDS))

    def __call__(self, population) -> np.ndarray:
        """Part de la population qui a chaque propriété."""
        return self.flags(population).mean(axis=0)


def exact_brain_law(bound: int, d: int = 3) -> tuple[float, float]:
    """Parts exactes de cerveaux à nœud de contrôle et de PSBN, poids uniformes.

    Les poids sont uniformes dans ``[-bound, bound]`` ; avec la borne ``B_d`` on
    retrouve :func:`simsbn.evolution.null_distribution`.
    """
    cols = np.array(list(product(range(-bound, bound + 1), repeat=d)))
    tables = (cols @ state_bits(d).T > 0) @ (1 << np.arange(1 << d))
    values, counts = np.unique(tables, return_counts=True)
    control = psbn = 0
    for f in product(range(len(values)), repeat=d):
        dyn = tuple(int(values[k]) for k in f)
        weight = int(np.prod(counts[list(f)]))
        control += weight * bool(control_nodes(dyn))
        psbn += weight * is_psbn(dyn)
    total = len(cols) ** d
    return control / total, psbn / total
