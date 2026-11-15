"""Mesures de structure d'agents à un capteur (``simsbn.milieu.ARCH``).

Six mesures par agent, dans l'ordre de ``KINDS`` :

- ``controle_cerveau`` : le cerveau seul (face « capteur = 0 ») a un nœud de contrôle.
  Pour un SBN, c'est exactement être un PTBN ;
- ``psbn_cerveau`` : le cerveau seul est un PSBN ;
- ``scission_sbn`` : la face « capteur = 1 » de la dynamique complète est un SBN ;
- ``controle_interne`` : la décomposition PTBN la plus fine a plus de 2 feuilles ;
- ``deux_controles`` : le cerveau seul a exactement deux nœuds de contrôle, le troisième
  étant le nœud opératif ;
- ``deux_controles_sbn`` : de plus, sur chacune des quatre faces, la fonction du nœud
  opératif est une SBF.
"""

from __future__ import annotations

from itertools import product

import numpy as np

from simsbn.core import batch_dynamics, state_bits
from simsbn.milieu import ARCH
from simsbn.pluripotence import control_nodes, decomposition, is_psbn, split_is_sbn
from simsbn.sbf import restrict

KINDS = [
    "controle_cerveau",
    "psbn_cerveau",
    "scission_sbn",
    "controle_interne",
    "deux_controles",
    "deux_controles_sbn",
]
BRAIN_KINDS = ["controle_cerveau", "psbn_cerveau", "deux_controles", "deux_controles_sbn"]
SENSOR = ARCH.inputs[0]


class Classifier:
    """Mesures de structure d'une population, mémorisées par dynamique."""

    def __init__(self):
        self.kinds: dict[tuple[int, ...], tuple[bool, ...]] = {}

    def flags(self, population) -> np.ndarray:
        """Tableau booléen : une ligne par agent, une colonne par mesure de ``KINDS``."""
        out = []
        for f in map(tuple, batch_dynamics(population).tolist()):
            if f not in self.kinds:
                brain = tuple(restrict(f[j], ARCH.d, SENSOR, 0) for j in ARCH.brain)
                control, psbn, two, two_sbn = brain_kinds(brain)
                self.kinds[f] = (
                    control,
                    psbn,
                    split_is_sbn(f, SENSOR),
                    sum(decomposition(f, "tbn")) > 2,
                    two,
                    two_sbn,
                )
            out.append(self.kinds[f])
        return np.array(out, dtype=bool).reshape(len(out), len(KINDS))

    def __call__(self, population) -> np.ndarray:
        """Part de la population qui a chaque propriété."""
        return self.flags(population).mean(axis=0)


def brain_kinds(brain) -> tuple[bool, bool, bool, bool]:
    """Classes de pluripotence d'un cerveau seul, dans l'ordre de ``BRAIN_KINDS``."""
    control = control_nodes(brain)
    two = len(control) == 2
    # Sens SBN : la décomposition en SBN descend jusqu'au nœud opératif sur chaque face,
    # donc ne laisse aucune feuille de dimension supérieure à 1.
    two_sbn = two and not any(decomposition(brain, "sbn")[: len(brain) - 1])
    return bool(control), is_psbn(brain), two, two_sbn


def exact_brain_kinds(bound: int, d: int = 3) -> dict[str, float]:
    """Part exacte de chaque classe de ``BRAIN_KINDS``, poids uniformes dans ``[-bound, bound]``.

    Avec la borne ``B_d``, les deux premières redonnent
    :func:`simsbn.evolution.null_distribution`.
    """
    cols = np.array(list(product(range(-bound, bound + 1), repeat=d)))
    tables = (cols @ state_bits(d).T > 0) @ (1 << np.arange(1 << d))
    values, counts = np.unique(tables, return_counts=True)
    totals = np.zeros(len(BRAIN_KINDS), dtype=object)
    for f in product(range(len(values)), repeat=d):
        dyn = tuple(int(values[k]) for k in f)
        weight = int(np.prod(counts[list(f)]))
        totals += [weight * flag for flag in brain_kinds(dyn)]
    return {kind: int(t) / len(cols) ** d for kind, t in zip(BRAIN_KINDS, totals, strict=True)}


def exact_brain_law(bound: int, d: int = 3) -> tuple[float, float]:
    """Parts exactes de cerveaux à nœud de contrôle et de PSBN, poids uniformes."""
    shares = exact_brain_kinds(bound, d)
    return shares["controle_cerveau"], shares["psbn_cerveau"]
