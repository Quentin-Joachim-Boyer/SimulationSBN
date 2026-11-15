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
  opératif est une SBF ;
- ``pc1_po2`` : un nœud ne lit aucun des deux autres (partie contrôle de 1 nœud) ;
- ``pc2_po1`` : deux nœuds ne lisent pas le troisième (partie contrôle de 2 nœuds) ;
- ``pc2_po1_vivante`` : idem, avec une partie contrôle qui n'est pas toujours éteinte ;
- ``pc1_po2_poids``, ``pc2_po1_poids`` : les mêmes décompositions lues sur les poids.

Pour les trois premières, « lire » est pris sur la dynamique : j lit i si changer i
change parfois la valeur suivante de j. Pour les deux dernières, qui font la définition
(décision du 15 novembre), j lit i si le poids i → j est non nul. Dans les deux cas,
les arcs partie contrôle → partie opérative sont libres, et le capteur est hors mesure.
"""

from __future__ import annotations

from itertools import combinations, product

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
    "pc1_po2",
    "pc2_po1",
    "pc2_po1_vivante",
    "pc1_po2_poids",
    "pc2_po1_poids",
]
STRUCTURAL_KINDS = ["pc1_po2_poids", "pc2_po1_poids"]
BRAIN_KINDS = [
    "controle_cerveau",
    "psbn_cerveau",
    "deux_controles",
    "deux_controles_sbn",
    "pc1_po2",
    "pc2_po1",
    "pc2_po1_vivante",
]
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
                control, psbn, two, two_sbn, pc1, pc2, pc2_living = brain_kinds(brain)
                self.kinds[f] = (
                    control,
                    psbn,
                    split_is_sbn(f, SENSOR),
                    sum(decomposition(f, "tbn")) > 2,
                    two,
                    two_sbn,
                    pc1,
                    pc2,
                    pc2_living,
                )
            out.append(self.kinds[f])
        dynamic = np.array(out, dtype=bool).reshape(len(out), len(KINDS) - len(STRUCTURAL_KINDS))
        return np.concatenate([dynamic, structural_parts(population)], axis=1)

    def __call__(self, population) -> np.ndarray:
        """Part de la population qui a chaque propriété."""
        return self.flags(population).mean(axis=0)


def reads(table: int, i: int, d: int) -> bool:
    """Vrai si la fonction de table ``table`` (dimension ``d``) dépend du nœud ``i``."""
    return any(((table >> s) & 1) != ((table >> (s ^ (1 << i))) & 1) for s in range(1 << d))


def control_parts(f) -> list[tuple[int, ...]]:
    """Parties contrôle possibles d'une dynamique : ensembles non vides et stricts de
    nœuds dont aucun ne lit un nœud extérieur."""
    d = len(f)
    lit = [[reads(f[j], i, d) for i in range(d)] for j in range(d)]
    return [
        pc
        for size in range(1, d)
        for pc in combinations(range(d), size)
        if not any(lit[j][i] for j in pc for i in range(d) if i not in pc)
    ]


def structural_parts(population) -> np.ndarray:
    """Décompositions 1/2 et 2/1 lues sur les poids du cerveau : tableau ``(N, 2)``.

    ``population`` est ``(N, d, d)`` avec le capteur en tête ; seule la matrice
    cerveau → cerveau compte. Un nœud forme une partie contrôle de 1 nœud si ses deux
    poids entrants venant des autres nœuds sont nuls ; il est la partie opérative d'une
    décomposition 2/1 si ses deux poids sortants vers les autres nœuds sont nuls.
    """
    W = np.asarray(population)[:, ARCH.n_in : ARCH.d, ARCH.n_in : ARCH.d]
    off = ~np.eye(ARCH.n_brain, dtype=bool)
    nonzero = (W != 0) & off
    reads_nobody = ~nonzero.any(axis=1)  # [n, i] : i ne lit aucun autre nœud
    read_by_nobody = ~nonzero.any(axis=2)  # [n, i] : aucun autre nœud ne lit i
    return np.stack([reads_nobody.any(axis=1), read_by_nobody.any(axis=1)], axis=1)


def exact_structural_parts(bound: int) -> dict[str, float]:
    """Part de ``STRUCTURAL_KINDS`` sous la loi uniforme : deux poids nuls par nœud,
    sur des poids distincts d'un nœud à l'autre."""
    one = 1 / (2 * bound + 1) ** 2
    share = 1 - (1 - one) ** ARCH.n_brain
    return dict.fromkeys(STRUCTURAL_KINDS, share)


def brain_kinds(brain) -> tuple[bool, ...]:
    """Classes d'un cerveau seul de 3 nœuds, dans l'ordre de ``BRAIN_KINDS``."""
    control = control_nodes(brain)
    two = len(control) == 2
    # Sens SBN : la décomposition en SBN descend jusqu'au nœud opératif sur chaque face,
    # donc ne laisse aucune feuille de dimension supérieure à 1.
    two_sbn = two and not any(decomposition(brain, "sbn")[: len(brain) - 1])
    parts = control_parts(brain)
    pc1 = any(len(pc) == 1 for pc in parts)
    pairs = [pc for pc in parts if len(pc) == 2]
    pc2_living = any(any(brain[j] for j in pc) for pc in pairs)
    return bool(control), is_psbn(brain), two, two_sbn, pc1, bool(pairs), pc2_living


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
