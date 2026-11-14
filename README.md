# SimulationSBN

Simulation d'agents modélisés par des réseaux booléens à signe (SBN) dans un cadre
évolutif, sous l'angle de la pluripotence.

La question : la pluripotence est rare parmi les dynamiques tirées au hasard (2 % en
dimension 3, 0,06 % en dimension 4, 0,0003 % en dimension 5). Dans quelles conditions
l'évolution en enrichit-elle les populations, bien au-delà de cette fréquence de base ?

Ce dépôt prolonge un stage dont le travail (énumération, statistiques, métagraphes) est
dans [PluripotentSBN](https://github.com/Quentin-Joachim-Boyer/PluripotentSBN). Il n'en
dépend pas : les notions utiles sont réécrites ici, et validées contre ses résultats.

## Installation

    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    pytest                 # ajouter -m "not slow" pour sauter la dimension 5
    ruff check .

## Ce qui existe

Le paquet `simsbn` (dans `src/`), implémentation de référence en NumPy :

| Module | Contenu |
|---|---|
| `core` | dynamique et fonction de transition d'une matrice de poids, attracteurs |
| `sbf` | énumération des fonctions à seuil signées par dimension, borne des poids |
| `pluripotence` | nœuds de contrôle (sur les poids ou sur la dynamique), décomposition PSBN et PTBN, comptage exact des dynamiques décomposables |

    >>> import numpy as np
    >>> from simsbn import dynamics, decomposition, is_control_node
    >>> W = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]])   # W[i, j] : arc i -> j
    >>> is_control_node(W, 0)
    True
    >>> decomposition(dynamics(W))                          # (v_3, v_2, v_1, v_0)
    (0, 2, 0, 0)

Les tests retrouvent les nombres du rapport de stage (32 et 370 SBF, 2 977 dynamiques à
nœud de contrôle et 658 PSBN en dimension 3, 1,19e7 en dimension 4) et les vecteurs de
décomposition de PluripotentSBN sur les 32 768 dynamiques de dimension 3.

## Feuille de route

1. **Noyau et mesures de pluripotence** — fait.
2. **Évolution neutre** : mutations d'un poids, population, lignées. Les fréquences des
   dynamiques doivent retrouver leur nombre de génotypes : c'est le modèle nul.
3. **Environnement alterné contre environnement fixe** : agents à nœuds capteurs,
   internes et moteurs, et mesure de l'enrichissement en réseaux pluripotents.
4. **Mesures graduées** : décompositions partielles, contrôle à plusieurs nœuds.
5. **Mutations qui changent la dimension** : duplication et suppression de nœuds.
6. **Organismes à plusieurs cellules** partageant un même SBN.

Le noyau rapide (JAX, populations entières sur GPU) viendra à l'étape 3, et sera testé
contre l'implémentation de référence.

## Règles du dépôt

- Une hypothèse écrite dans `journal/` avant chaque expérience.
- Aucun résultat ni binaire dans git : une commande par figure, dans `experiments/`.
- Toute version rapide d'un calcul est testée contre sa version de référence.
