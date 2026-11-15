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
    pip install -e ".[dev,viz]"
    pytest                 # ajouter -m "not slow" pour sauter la dimension 5
    ruff check .

## Ce qui existe

Le paquet `simsbn` (dans `src/`), implémentation de référence en NumPy :

| Module | Contenu |
|---|---|
| `core` | dynamique et fonction de transition d'une matrice de poids, attracteurs |
| `sbf` | énumération des fonctions à seuil signées par dimension, borne des poids |
| `evolution` | mutation d'un poids, population de Wright-Fisher avec lignées, modèle nul exact |
| `agents` | architecture entrée / cerveau / moteur, comme SBN à topologie contrainte |
| `simulability` | cible simulée par un cerveau sur ses nœuds visibles |
| `milieu` | milieu partagé à deux ressources : énergie, mort, division, viabilité en solitaire |
| `monde` | monde en grille (2D, ou 1 × 1 pour un milieu bien mélangé) : nourriture, déchet toxique, déplacement, capteur de bien-être ; actions lues sur le cerveau ou par des moteurs lecteurs (`Corps`) |
| `suivi` | relevés d'une population qui vit dans un monde : démographie, comportement, structure |
| `structure` | mesures de structure d'un agent à un capteur (PTBN, PSBN, scission, contrôle interne, deux nœuds de contrôle), loi uniforme exacte du cerveau seul |
| `stats` | test par permutation, une population étant l'unité |
| `tasks` | contextes, trajectoires et score d'un agent |
| `viz` | style commun des figures |
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

## Visualiser une simulation

    python experiments/neutre/run.py        # options : --d --pop --gen --rep --mu --seed

Des populations clonales évoluent sans sélection, et la figure
`experiments/neutre/out/neutre.png` compare la simulation au modèle nul exact : part
d'individus pluripotents au cours des générations, diversité des dynamiques, fréquence
de chaque vecteur de décomposition. Les séries sont aussi écrites dans `neutre.csv`.

    python experiments/alterne/run.py

Des agents doivent allumer ou éteindre un nœud moteur selon un contexte donné à l'état
initial, en environnement fixe ou alterné. Protocole, hypothèse et résultat :
`journal/2026-11-14_environnement-alterne.md`.

    python experiments/cerveau_131/run.py     # environ 2 minutes

Même comparaison avec des agents à rôles séparés : 1 nœud d'entrée maintenu par le
contexte, 3 nœuds de cerveau, 1 nœud moteur sans retour vers le cerveau. Journal :
`journal/2026-11-14_cerveau-131.md`.

    python experiments/simulabilite/run.py    # calcul exact, quelques secondes

Table de simulabilité : pour chaque paire de cibles de dimension 2, combien de cerveaux
de dimension 3 simulent l'une sans contexte et l'autre sous contexte, et quelle part
est un PSBN. Journal : `journal/2026-11-14_simulabilite.md`.

    python experiments/milieu_partage/run.py  # environ 4 minutes

Milieu partagé, sans cible ni fitness : les agents ingèrent deux ressources, meurent
d'épuisement ou se divisent, en régime constant, à saisons ou neutre. Journal :
`journal/2026-11-14_milieu-partage.md`.

    python experiments/monde_dechet/calibrage.py  # agents construits à la main
    python experiments/monde_dechet/run.py        # environ 4 minutes sur 2 cœurs
    python experiments/monde_dechet/motifs.py     # analyse des populations finales
    python experiments/monde_dechet/voir.py       # écrit out/monde_2d.html

Une ressource et un déchet toxique produit par l'ingestion, dans un monde bien mélangé,
dans un monde en 2D où les agents se déplacent, et en régime neutre. `voir.py` rejoue une
des populations mesurées dans une page à ouvrir dans un navigateur : on y suit un agent,
son cerveau et son activité pas à pas. Journal : `journal/2026-11-14_monde-dechet.md`.

    python experiments/moteurs_lecteurs/run.py           # environ 5 minutes sur 2 cœurs
    python experiments/moteurs_lecteurs/prolongation.py  # environ 6 minutes

Même monde, mais les actions sont portées par des nœuds lecteurs : ils lisent le cerveau
et rien ne revient d'eux. Lecture retardée (nœud SBN ordinaire, réaction en deux pas) ou
immédiate. Journal : `journal/2026-11-15_moteurs-lecteurs.md`.

## Feuille de route

1. **Noyau et mesures de pluripotence** — fait.
2. **Évolution neutre** — fait : en dimension 3, la part de pluripotents converge vers
   les 2,99 % du modèle nul (fréquence des génotypes, et non des dynamiques). Reste à
   tracer les lignées dans le métagraphe.
3. **Environnement alterné contre environnement fixe** — première expérience faite, en
   dimension 3 : l'alternance ne dépasse pas le modèle nul, c'est l'environnement fixe
   qui appauvrit en PSBN. Avec des agents 1/3/1 et une dynamique demandée par contexte,
   l'alternance éloigne du sens PSBN (l'entrée devient activatrice) tout en restant
   PTBN. Le calcul exact de simulabilité montre qu'entre cibles SBN, le contexte ne
   peut que relever des seuils (225 paires simulables sur 1 296) et que le nœud caché
   n'ajoute aucune paire. Reste à faire évoluer des populations sur des paires choisies
   dans cette table. Dans un milieu partagé où la survie seule sélectionne, les agents
   ingèrent tout en permanence et ignorent leur capteur : aucun comportement ne dépend
   du contexte, et le régime à saisons se fige. Résultat négatif, protocole à revoir.
   Avec une ressource, un déchet toxique et un monde en 2D, la survie seule sélectionne
   un comportement qui dépend du contexte (toujours bouger quand ça va mal, un pas sur
   deux quand ça va bien), mais aucune mesure de structure n'est enrichie ; elles le
   sont dans le monde bien mélangé, où rien ne dépend du contexte. Avec des moteurs
   lecteurs, la lecture immédiate redonne ce comportement ; avec un pas de retard, la
   stratégie sensible au contexte perd son avantage net et les populations basculent
   entre elle et un autre état. Les nœuds de contrôle restent enrichis en monde mélangé.
4. **Mesures graduées** : décompositions partielles, contrôle à plusieurs nœuds.
5. **Mutations qui changent la dimension** : duplication et suppression de nœuds.
6. **Organismes à plusieurs cellules** partageant un même SBN.

Le noyau rapide (JAX, populations entières sur GPU) viendra quand la dimension l'exigera, et sera testé
contre l'implémentation de référence.

## Règles du dépôt

- Une hypothèse écrite dans `journal/` avant chaque expérience.
- Aucun résultat ni binaire dans git : une commande par figure, dans `experiments/`.
- Toute version rapide d'un calcul est testée contre sa version de référence.
