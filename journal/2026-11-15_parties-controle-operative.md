# Décompositions partie contrôle / partie opérative du cerveau

Écrit avant de relancer les expériences ; « Résultat » est rempli après.

## Pourquoi

Précision de Quentin (15 novembre) : « deux nœuds de contrôle, un nœud opératif » ne
désigne pas deux nœuds fixes, mais une **partie contrôle** (PC) de deux nœuds, un cerveau
dans le cerveau, et une **partie opérative** (PO). La PC peut avoir n'importe quelle
dynamique, cycles compris. Les arcs PC → PO sont libres, les arcs PO → PC interdits.
On mesure d'abord les décompositions possibles d'un cerveau de 3 nœuds, 1/2 et 2/1
(0/3 et 3/0 ne sont qu'un SBN quelconque). Plus tard : décompositions emboîtées, où
la PC ou la PO est elle-même de la forme PC/PO.

La classe « deux nœuds fixes » de `2026-11-15_classes-de-pluripotence.md` en est le cas
particulier où la PC est l'identité ; elle reste mesurée mais n'est plus la définition.

## Définitions

Sur le cerveau seul (capteur éteint), comme les autres mesures.

- **Arc** lu sur la dynamique, choix de Claude : le nœud j lit le nœud i si changer i
  change parfois la valeur suivante de j. Un poids non nul sans effet ne compte pas,
  comme pour les nœuds de contrôle.
- **1/2** : un nœud ne lit aucun des deux autres. Pour un SBN, il est alors soit un nœud
  de contrôle (il garde sa valeur), soit **mort** (toujours éteint après un pas).
  La 1/2 vivante est donc exactement le PTBN, déjà mesuré.
- **2/1** : deux nœuds ne lisent pas le troisième. **2/1 vivante** : la PC n'est pas
  constamment éteinte.

## Loi uniforme (calcul exact, poids dans [-3, 3])

| Décomposition | Part |
|---|---|
| 1/2, toutes | 51,764 % |
| 1/2 vivante (= PTBN) | 8,494 % |
| 1/2 seulement par un nœud mort | 43,270 % |
| 2/1, toutes | 28,850 % |
| 2/1 vivante | 22,688 % |
| 1/2 et 2/1 à la fois | 24,978 % |
| Au moins une des deux | 55,635 % |

## Protocole

Comme pour les classes de pluripotence : les deux expériences du monde à déchet et des
moteurs lecteurs relancées telles quelles, mêmes graines, trois mesures de plus
(1/2 toutes, 2/1 toutes, 2/1 vivante). Les anciennes lignes doivent ressortir
identiques. Test par permutation contre le régime neutre, seuil p < 0,01.

## Hypothèses

1. **2/1 vivante, régime mélangé (lecture directe)** : enrichie. Raison : l'ingestion y
   est un nœud de contrôle et le déplacement y est éteint ; s'il est mort, ces deux
   nœuds forment une PC vivante. Réfutation : p ≥ 0,01 ou part inférieure au neutre.
2. **1/2 toutes, régime espace (lecture directe)** : appauvrie. Raison : le déplacement y
   reste allumé quand le capteur vaut 0, il ne peut donc pas être mort, et moins de
   nœuds morts veut dire moins de 1/2. Réfutation : p ≥ 0,01 ou part supérieure au neutre.
3. Sans prédiction : 2/1 vivante en régime espace, et tous les régimes à moteurs lecteurs.

Réserve connue d'avance : un nœud que seul le capteur allume paraît mort quand on
regarde le cerveau à capteur éteint.

## Résultat

Les deux expériences relancées redonnent à l'identique toutes les lignes déjà publiées.
Parts en %, seconde moitié, moyenne ± écart-type entre 24 populations.

| Lecture directe   | Mélangé       | Espace        | Neutre        | Loi uniforme |
|-------------------|---------------|---------------|---------------|--------------|
| 1/2, toutes       | 62,86 ± 14,63 | 24,35 ± 19,07 | 52,87 ± 12,14 | 51,764       |
| 1/2 vivante (PTBN)| 17,60 ± 8,23  | 8,99 ± 9,93   | 9,45 ± 8,46   | 8,494        |
| 2/1, toutes       | 36,49 ± 15,06 | 10,82 ± 12,27 | 31,41 ± 12,23 | 28,850       |
| 2/1 vivante       | 30,31 ± 12,74 | 10,81 ± 12,26 | 26,20 ± 11,74 | 22,688       |

Valeurs p contre le neutre : mélangé 0,014 (1/2), 0,21 (2/1), 0,26 (2/1 vivante) ;
espace < 0,0001 (1/2), < 0,0001 (2/1), 0,0002 (2/1 vivante).

| Moteurs lecteurs  | Mélangé retardé | Mélangé immédiat | Espace retardé | Espace immédiat | Neutre        |
|-------------------|-----------------|------------------|----------------|-----------------|---------------|
| 1/2, toutes       | 49,30 ± 16,26   | 50,72 ± 20,99    | 45,80 ± 30,26  | 65,32 ± 33,21   | 55,85 ± 12,98 |
| 2/1, toutes       | 30,38 ± 17,27   | 28,53 ± 14,58    | 19,40 ± 21,79  | 47,99 ± 28,68   | 31,09 ± 13,83 |
| 2/1 vivante       | 28,42 ± 17,18   | 25,71 ± 13,10    | 17,03 ± 20,18  | 36,87 ± 23,78   | 23,81 ± 11,39 |

Valeurs p contre le neutre : toutes ≥ 0,0138 (la plus basse : 2/1 en espace immédiat,
dans le sens d'un enrichissement ; 0,035 en espace retardé, dans l'autre sens).

- **Hypothèse 1 : réfutée.** En régime mélangé, la 2/1 vivante n'est pas enrichie (30,3 %
  contre 26,2 %, p = 0,26).
- **Hypothèse 2 : confirmée.** En régime espace à lecture directe, la 1/2 tombe à 24,4 %
  contre 52,9 % en neutre (p < 0,0001).
- **Sans prédiction, et plus net que je ne pensais** : en régime espace à lecture directe,
  la 2/1 est aussi appauvrie (10,8 % contre 31,4 %, p < 0,0001). Les cerveaux y sont plus
  densément couplés.

### Analyse après coup (non prévue) : qui lit qui

Part des agents finaux (cerveau à capteur éteint) dont un nœud lit un autre, ou est mort.

| Lecture directe | Nœud mort | Le déplacement lit l'ingestion | Le déplacement lit le caché | L'ingestion lit le caché |
|-----------------|-----------|--------------------------------|-----------------------------|--------------------------|
| Mélangé         | déplacement 40 %, caché 20 % | 40 % | 48 % | 71 % |
| Espace          | déplacement 0 %, caché 17 %  | 92 % | 88 % | 85 % |
| Neutre          | 16 à 23 % selon le nœud      | 64 % | 58 % | 68 % |

En régime espace, le déplacement n'est jamais mort et lit presque toujours les deux
autres nœuds, qui se lisent eux-mêmes beaucoup. Une PC autonome y est donc rare. En régime
mélangé, l'excès de 1/2 vient surtout du nœud de déplacement mort (40 %), donc d'une PC
morte : c'est le cas dégénéré.

**Lecture.** Là où le comportement dépend du contexte (régime espace, lecture directe), le
cerveau ne se décompose pas en PC/PO : il est intégré. Avec des moteurs lecteurs, ce
lien disparaît (espace immédiat : 2/1 à 48 %, sens inverse, p = 0,014). Les actions
n'étant plus dans le cerveau, rien n'oblige le nœud qui porte le comportement à lire
les autres.

### Limites

- Une graine, les mêmes populations ; neuf tests de plus, sans correction.
- « Lire » est pris sur la dynamique ; un poids sans effet ne compte pas.
- Cerveau à capteur éteint seulement : un nœud que seul le capteur allume paraît mort.

## Suites possibles

- Compter le capteur dans la décomposition : il est par construction une PC externe.
  Une PC interne qui lit le capteur sans être lue en retour serait une autre classe.
- Décompositions emboîtées (la PC ou la PO elle-même PC/PO), prévues par Quentin.
- Type d'attracteurs de la PC (plusieurs points fixes, cycle, un seul point fixe).
- Exclure les PC mortes de la 1/2 et de la 2/1 dans les tableaux, puisqu'elles dominent.
