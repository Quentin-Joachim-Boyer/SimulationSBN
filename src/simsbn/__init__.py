"""simsbn — réseaux booléens à signe (SBN), pluripotence et simulations évolutives.

Conventions, identiques dans tout le paquet :

- ``W[i, j]`` est le poids de l'arc ``i -> j`` ; la fonction du nœud ``j`` ne dépend
  que de la colonne ``j`` ;
- un état est un entier dont le bit ``i`` vaut la valeur du nœud ``i`` (nœuds numérotés
  à partir de 0, le nœud 0 étant le bit de poids faible) ;
- une table de vérité est un entier dont le bit ``s`` vaut ``f(s)`` ;
- une dynamique est le tuple ``(f_0, ..., f_{d-1})`` des tables de vérité de ses nœuds.
"""

from simsbn.core import attractors, batch_dynamics, column_table, dynamics, transition
from simsbn.evolution import mutate, null_distribution, wright_fisher
from simsbn.pluripotence import (
    control_nodes,
    count_psbn,
    decomposition,
    is_control_node,
    is_psbn,
    split_is_sbn,
)
from simsbn.sbf import WEIGHT_BOUND, sbf_counts, sbf_tables, weight_bound

__all__ = [
    "WEIGHT_BOUND",
    "attractors",
    "batch_dynamics",
    "column_table",
    "control_nodes",
    "count_psbn",
    "decomposition",
    "dynamics",
    "is_control_node",
    "is_psbn",
    "mutate",
    "null_distribution",
    "sbf_counts",
    "sbf_tables",
    "split_is_sbn",
    "transition",
    "weight_bound",
    "wright_fisher",
]
