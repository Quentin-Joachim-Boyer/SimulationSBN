# Classes de pluripotence du cerveau : PTBN, PSBN, deux nœuds de contrôle

Écrit avant de relancer les expériences ; « Résultat » est rempli après.

## Pourquoi

Quentin demande de mesurer la part de cerveaux pluripotents au sens TBN et au sens SBN,
et la part de cerveaux pluripotents au sens « deux nœuds de contrôle, un nœud opératif ».

## Définitions

Toutes portent sur le cerveau seul (3 nœuds, capteur à 0), donc sur un SBN.

- **PTBN** : le cerveau a au moins un nœud de contrôle. Pour un SBN c'est la même chose
  qu'être décomposable en réseaux à seuil : vérifié sur les 32 768 dynamiques de
  dimension 3. C'est la mesure déjà suivie sous le nom « nœud de contrôle (cerveau seul) ».
- **PSBN** : il existe un nœud de contrôle dont les deux faces sont des SBN. Déjà suivie.
- **2 contrôle / 1 opératif** (sens TBN) : exactement deux nœuds gardent toujours leur
  valeur ; le troisième a l'une de quatre dynamiques selon la valeur des deux premiers.
- **2 contrôle / 1 opératif, sens SBN** : en plus, sur chacune des quatre faces, la
  fonction du nœud opératif est une SBF (il reste éteint, ou il garde sa valeur).

Choix de Claude, à confirmer avec la définition du stage : les nœuds de contrôle sont
ceux de l'hypercube entier. La variante emboîtée (un second nœud de contrôle propre à
chaque face) donne presque la même classe : 0,269 % contre 0,250 % sous la loi uniforme.

## Loi uniforme (calcul exact, poids dans [-3, 3])

| Classe | Part |
|---|---|
| Aucun nœud de contrôle | 91,51 % |
| PTBN (au moins un) | 8,49 % |
| PSBN | 2,49 % |
| Exactement un nœud de contrôle | 8,24 % |
| 2 contrôle / 1 opératif, sens TBN | 0,248 % |
| 2 contrôle / 1 opératif, sens SBN | 0,076 % |
| Trois nœuds de contrôle (tout figé) | 0,0025 % |

La classe demandée est donc rare : un cerveau sur 400 au sens TBN, un sur 1 300 au sens SBN.

## Protocole

Aucune nouvelle simulation : les deux expériences du monde à déchet
(`experiments/monde_dechet/run.py`, lecture directe) et des moteurs lecteurs
(`experiments/moteurs_lecteurs/run.py`) sont relancées telles quelles, avec les mêmes
graines, donc les mêmes populations. Le classificateur reçoit deux mesures de plus. Les
anciennes lignes doivent ressortir identiques ; c'est vérifié.

Comme avant : 24 populations par régime, moyenne de la seconde moitié, test par
permutation contre le régime neutre, seuil p < 0,01.

## Hypothèses

1. **2 contrôle / 1 opératif, sens TBN.** Enrichie en régime mélangé à lecture directe.
   Raison : le nœud d'ingestion doit rester allumé et le nœud de déplacement éteint ; deux
   nœuds figés sur trois, cela donne souvent deux nœuds de contrôle, sans que rien dépende
   du contexte. Réfutation : pas de différence avec le régime neutre (p ≥ 0,01).
2. **Même classe, régime espace** (toutes lectures) : pas d'enrichissement, puisque le
   déplacement doit y changer d'état. Réfutation : part supérieure au neutre avec p < 0,01.
3. Sans prédiction : la même classe en régime mélangé avec des lecteurs, et le sens SBN
   partout (classe trop rare pour que j'ose un pronostic).

PTBN et PSBN ne changent pas : ce sont les lignes déjà publiées.

## Résultat

Les deux scripts relancés redonnent à l'identique toutes les lignes déjà publiées
(effectifs, comportement, quatre mesures de structure et leurs valeurs p contre le
régime neutre). Seules les valeurs p des sections placées après les nouveaux tests
bougent à la troisième décimale, parce que le tirage des permutations est décalé.

Parts en %, seconde moitié, moyenne ± écart-type entre 24 populations.

| Lecture directe          | Mélangé       | Espace        | Neutre        | Loi uniforme |
|--------------------------|---------------|---------------|---------------|--------------|
| PTBN (cerveau seul)      | 17,60 ± 8,23  | 8,99 ± 9,93   | 9,45 ± 8,46   | 8,494        |
| PSBN (cerveau seul)      | 7,83 ± 4,76   | 1,03 ± 3,23   | 3,05 ± 3,19   | 2,491        |
| 2 contrôle / 1 opératif  | 0,82 ± 1,26   | 0,29 ± 1,02   | 0,38 ± 0,64   | 0,248        |
| idem, sens SBN           | 0,28 ± 0,50   | 0,00 ± 0,00   | 0,11 ± 0,28   | 0,076        |

| Moteurs lecteurs         | Mélangé retardé | Mélangé immédiat | Espace retardé | Espace immédiat | Neutre      |
|--------------------------|-----------------|------------------|----------------|-----------------|-------------|
| PTBN (cerveau seul)      | 14,92 ± 10,15   | 18,00 ± 15,20    | 8,66 ± 12,62   | 12,98 ± 16,29   | 7,88 ± 7,73 |
| PSBN (cerveau seul)      | 4,34 ± 5,15     | 4,47 ± 4,60      | 1,43 ± 2,98    | 4,41 ± 6,02     | 2,81 ± 3,96 |
| 2 contrôle / 1 opératif  | 0,75 ± 2,49     | 0,34 ± 0,53      | 0,31 ± 1,29    | 0,05 ± 0,11     | 0,13 ± 0,24 |
| idem, sens SBN           | 0,19 ± 0,53     | 0,16 ± 0,46      | 0,26 ± 1,27    | 0,01 ± 0,02     | 0,00 ± 0,01 |

Valeurs p contre le régime neutre de la même expérience :

|                          | Mélangé direct | Espace direct | Mélangé retardé | Mélangé immédiat | Espace retardé | Espace immédiat |
|--------------------------|----------------|---------------|-----------------|------------------|----------------|-----------------|
| 2 contrôle / 1 opératif  | 0,15           | 0,78          | 0,14            | 0,073            | 0,91           | 0,19            |
| idem, sens SBN           | 0,17           | 0,0008        | 0,0044          | 0,019            | 0,93           | 0,55            |

- **Hypothèse 1 : réfutée.** En régime mélangé à lecture directe, la classe « 2 contrôle /
  1 opératif » est à 0,82 % contre 0,38 % en neutre : le sens attendu, mais p = 0,15.
- **Hypothèse 2 : confirmée.** Aucun régime espace n'enrichit cette classe (p ≥ 0,19).
- **Sens SBN, régime espace à lecture directe** : la classe est absente des 24 populations
  (maximum 0,01 %), nettement sous le régime neutre (p = 0,0008). Explication probable :
  le nœud d'ingestion, qui reste allumé, y active le déplacement (poids ingérer → bouger
  positif chez 91,6 % des agents finaux, contre 46,4 % en neutre et 7,7 % en mélangé). Or
  un nœud de contrôle qui active un autre nœud interdit la décomposition en SBN : c'est
  la même contrainte que pour la scission. Le PSBN du cerveau seul y baisse aussi (1,03 %).
- **Sens SBN, régime mélangé retardé** : 0,19 % contre 0,00 % en neutre, p = 0,0044. Je ne
  m'y fie pas : deux populations sur 24 portent l'écart, et ce régime neutre est tombé à
  0,00 % alors que la loi exacte donne 0,076 % et que l'autre régime neutre donne 0,11 %.

**Ce que valent ces mesures.**

- PTBN et PSBN du cerveau seul restent les deux mesures utilisables. PTBN n'ajoute rien à
  « au moins un nœud de contrôle » : c'est la même chose.
- La classe « 2 contrôle / 1 opératif » est trop rare en dimension 3 pour ces populations.
  Sous la loi uniforme on en attend moins d'un agent par population (0,25 % de 170 à 400
  agents). Les parts observées sont presque toujours nulles, avec de rares bouffées quand
  une lignée qui la porte se répand (jusqu'à 12,5 % dans une population). Vingt-quatre
  populations ne suffisent pas à distinguer un doublement.
- Avec trois nœuds, deux nœuds figés ne laissent qu'un nœud pour calculer. La classe
  aurait plus de sens avec un cerveau plus grand.

### Limites

- Une graine ; les mêmes populations que les deux expériences précédentes.
- Douze tests de plus, sans correction ; le seuil de 0,01 valait pour les hypothèses 1 et 2.
- Nœuds de contrôle de l'hypercube entier, sur le cerveau à capteur éteint seulement.

## Suites possibles

- Un cerveau de 4 ou 5 nœuds, où « 2 contrôle / n opératifs » laisse de quoi calculer.
- Les mêmes classes sur le cerveau à capteur allumé (un réseau à seuil), pour voir si le
  contexte change la classe du cerveau.
- Davantage de populations, ou une mesure cumulée sur toute la durée, si la classe rare
  reste d'intérêt en dimension 3.
