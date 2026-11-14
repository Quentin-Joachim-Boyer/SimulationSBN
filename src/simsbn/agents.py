"""Agents : SBN dont les nœuds ont un rôle (entrée, cerveau, moteur).

Un agent reste un SBN ordinaire, de dimension ``n_in + n_brain + n_out``, dont la
topologie est contrainte :

- une **entrée** n'a qu'une boucle de poids 1 : elle garde la valeur que le contexte
  lui donne au départ, c'est un nœud de contrôle par construction ;
- le **cerveau** reçoit les entrées et le cerveau ;
- un **moteur** lit le cerveau, sans boucle ni retour vers le cerveau.

Les nœuds sont rangés dans cet ordre : entrées, cerveau, moteurs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Architecture:
    n_in: int
    n_brain: int
    n_out: int

    @property
    def d(self) -> int:
        return self.n_in + self.n_brain + self.n_out

    @property
    def inputs(self) -> range:
        return range(self.n_in)

    @property
    def brain(self) -> range:
        return range(self.n_in, self.n_in + self.n_brain)

    @property
    def outputs(self) -> range:
        return range(self.n_in + self.n_brain, self.d)

    def mask(self) -> np.ndarray:
        """Matrice booléenne des poids qui évoluent (``mask[i, j]`` : arc ``i -> j``)."""
        m = np.zeros((self.d, self.d), dtype=bool)
        b, o = list(self.brain), list(self.outputs)
        m[np.ix_(list(self.inputs) + b, b)] = True
        m[np.ix_(b, o)] = True
        return m

    def random(self, rng: np.random.Generator, n: int, bound: int) -> np.ndarray:
        """Population de ``n`` agents aux poids uniformes dans ``[-bound, bound]``."""
        population = np.zeros((n, self.d, self.d), dtype=np.int64)
        mask = self.mask()
        population[:, mask] = rng.integers(-bound, bound + 1, size=(n, int(mask.sum())))
        for i in self.inputs:
            population[:, i, i] = 1
        return population

    def state(self, inputs: int = 0, brain: int = 0) -> int:
        """État du réseau à partir de l'état des entrées et de celui du cerveau."""
        return inputs | (brain << self.n_in)
