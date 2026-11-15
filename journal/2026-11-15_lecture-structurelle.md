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
| 1/2 | 6,04 % | 51,76 % |
| 2/1 | 6,04 % | 28,85 % |

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

À remplir.
