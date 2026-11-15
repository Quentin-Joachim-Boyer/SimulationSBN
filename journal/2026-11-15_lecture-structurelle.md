# Parties contrôle / opérative lues sur les poids

Écrit avant de relancer les expériences ; « Résultat » est rempli après.

## Pourquoi

Dans `2026-11-15_parties-controle-operative.md`, Claude lisait les arcs sur la dynamique
(j lit i si changer i change parfois j). Quentin remarque que « lire » est d'abord une
notion structurelle : une PC est une contrainte d'architecture. Dans un SBN, un poids non
nul peut être sans effet (exemple : [3·x_j − x_i > 0] ne dépend pas de x_i), donc les deux
lectures diffèrent. Décision : la **lecture structurelle devient la définition**, la
lecture dynamique est gardée à côté.

Décision de Quentin, même jour : le capteur reste **hors** de la mesure. Il modélise un
contrôle par l'environnement, de nature différente d'une PC interne au cerveau, qui
permet un contrôle interne du comportement et peut émerger ou non par l'évolution.
La façon de modéliser le capteur pourra changer plus tard.

## Définitions

Sur les poids du cerveau seul (matrice 3 × 3, capteur exclu, boucles sans importance).

- j **lit** i (structurellement) si le poids i → j est non nul.
- **1/2 structurelle** : un nœud dont les deux poids entrants venant des autres nœuds sont nuls.
- **2/1 structurelle** : un nœud dont les deux poids sortants vers les autres nœuds sont nuls.

Les mesures dynamiques (`pc1_po2`, `pc2_po1`, `pc2_po1_vivante`) restent inchangées.

## Loi uniforme (poids dans [-3, 3], indépendants)

Chaque condition demande deux poids nuls précis (probabilité 1/49), sur des poids
distincts pour les trois nœuds, d'où 1 − (48/49)³ :

| Décomposition | Structurelle | Dynamique (rappel) |
|---|---|---|
| 1/2 | 6,00 % | 51,76 % |
| 2/1 | 6,00 % | 28,85 % |

Correction avant le lancement : une première version de ce journal donnait 6,04 %, une
erreur de calcul à la main ; 1 − (48/49)³ = 6,00 %, confirmé sur 200 000 tirages.

La mutation tire une nouvelle valeur uniforme parmi les six autres : sous dérive neutre,
un poids est nul avec la probabilité 1/7, comme sous la loi uniforme.

## Protocole

Les deux expériences (monde à déchet, moteurs lecteurs) relancées telles quelles, mêmes
graines, deux mesures de plus. Anciennes lignes identiques, vérifié. Test par
permutation contre le régime neutre, seuil p < 0,01.

## Hypothèses

1. **Régime espace, lecture directe** : 2/1 structurelle appauvrie par rapport au neutre,
   comme la 2/1 dynamique. Le déplacement y lit les deux autres nœuds chez 88 à 92 % des
   agents, donc avec des poids non nuls. Réfutation : p ≥ 0,01 ou part supérieure.
2. **Régime mélangé, lecture directe** : 1/2 structurelle **non** enrichie, contrairement
   à la 1/2 dynamique (62,9 %) : cet excès venait de nœuds morts, qui sont morts à cause
   de poids négatifs, pas de poids nuls. Réfutation : part supérieure au neutre, p < 0,01.
3. Sans prédiction : les régimes à moteurs lecteurs. Avec si peu de cas attendus
   (6 %, soit une dizaine à une vingtaine d'agents par population), un écart modeste
   passera inaperçu.

## Résultat

Les deux expériences relancées redonnent à l'identique toutes les lignes déjà publiées.
Parts en %, seconde moitié, moyenne ± écart-type entre 24 populations ; loi uniforme 6,00 %.

| Lecture directe      | Mélangé      | Espace       | Neutre       |
|----------------------|--------------|--------------|--------------|
| 1/2 sur les poids    | 5,83 ± 9,71  | 2,44 ± 3,57  | 5,97 ± 5,21  |
| 2/1 sur les poids    | 5,74 ± 7,99  | 2,68 ± 2,81  | 8,80 ± 7,98  |
| 1/2 dynamique (rappel) | 62,86      | 24,35        | 52,87        |
| 2/1 dynamique (rappel) | 36,49      | 10,82        | 31,41        |

Valeurs p contre le neutre : espace 0,0092 (1/2) et 0,0005 (2/1) ; mélangé 0,96 et 0,20.

| Moteurs lecteurs  | Mélangé retardé | Mélangé immédiat | Espace retardé | Espace immédiat | Neutre      |
|-------------------|-----------------|------------------|----------------|-----------------|-------------|
| 1/2 sur les poids | 6,17 ± 5,80     | 8,68 ± 11,01     | 8,01 ± 18,97   | 9,29 ± 13,01    | 5,24 ± 5,80 |
| 2/1 sur les poids | 7,08 ± 8,52     | 7,74 ± 6,91      | 5,64 ± 8,20    | 12,41 ± 16,95   | 6,25 ± 6,41 |

Valeurs p contre le neutre : toutes ≥ 0,11.

- **Hypothèse 1 : confirmée.** En régime espace à lecture directe, la 2/1 sur les poids
  tombe à 2,7 % contre 8,8 % en neutre (p = 0,0005). La 1/2 aussi (2,4 % contre 6,0 %,
  p = 0,0092). Les deux lectures disent la même chose : le cerveau y est intégré.
- **Hypothèse 2 : confirmée.** En régime mélangé, la 1/2 sur les poids n'est pas enrichie
  (5,8 % contre 6,0 %, p = 0,96). L'excès de la 1/2 dynamique venait bien de nœuds morts
  par des poids négatifs, pas d'une architecture autonome.
- **Moteurs lecteurs** : rien de significatif.

**Lecture d'ensemble.** Aucune partie contrôle interne n'émerge, quelle que soit la
lecture. Là où le comportement dépend du contexte, l'évolution produit au contraire des
cerveaux plus intégrés que le hasard. Le contexte vient du capteur, qui est déjà une
partie contrôle externe : dans ce monde, rien ne demande d'en construire une interne.

Le régime neutre de la lecture directe est un peu au-dessus de la loi uniforme pour la
2/1 sur les poids (8,8 % contre 6,0 %, environ 1,7 erreur standard) : dérive, à surveiller.

### Limites

- Une graine, les mêmes populations ; quatorze tests de plus sur cette série, sans correction.
- Classe rare (6 %) : une dizaine à une vingtaine d'agents par population.

## Suites possibles

- Un monde où un contexte interne paie : un capteur qui ne dit pas tout (par exemple un
  signal bref qu'il faut retenir), pour qu'une mémoire de contexte, donc une PC interne,
  ait une raison d'émerger.
- Décompositions emboîtées ; cerveau de 4 ou 5 nœuds.
