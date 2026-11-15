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

À remplir.
