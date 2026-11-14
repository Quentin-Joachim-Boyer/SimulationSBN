"""simsbn — réseaux booléens à signe (SBN), pluripotence et simulations évolutives.

Conventions, identiques dans tout le paquet :

- ``W[i, j]`` est le poids de l'arc ``i -> j`` ; la fonction du nœud ``j`` ne dépend
  que de la colonne ``j`` ;
- un état est un entier dont le bit ``i`` vaut la valeur du nœud ``i`` (nœuds numérotés
  à partir de 0, le nœud 0 étant le bit de poids faible) ;
- une table de vérité est un entier dont le bit ``s`` vaut ``f(s)`` ;
- une dynamique est le tuple ``(f_0, ..., f_{d-1})`` des tables de vérité de ses nœuds.
"""

from simsbn.core import attractors, column_table, dynamics, transition
from simsbn.pluripotence import (
    control_nodes,
    count_psbn,
    decomposition,
    is_control_node,
    is_psbn,
)
from simsbn.sbf import WEIGHT_BOUND, sbf_tables, weight_bound

__all__ = [
    "WEIGHT_BOUND",
    "attractors",
    "column_table",
    "control_nodes",
    "count_psbn",
    "decomposition",
    "dynamics",
    "is_control_node",
    "is_psbn",
    "sbf_tables",
    "transition",
    "weight_bound",
]
