# Fondateur unique et taux de mutation

Écrit avant de lancer l'expérience ; « Résultat » est rempli après.

## Pourquoi

En regardant la simulation « directions » (artefact, mode « Lignée »), Quentin constate
que tous les agents de la fin ont la même couleur : la population de 194 agents descend
d'un seul des 300 ancêtres du pas 0. Deux conséquences :

1. Une fixation sur un ancêtre n'est pas en soi une preuve de sélection : la dérive
   seule, dans une population de taille finie, finit par ne laisser qu'un lignage. Sans
   comparaison au modèle nul, on ne peut pas dire si la sélection l'a accéléré.
2. Chaque population est surtout la descendance d'un ancêtre plus les mutations
   survenues depuis. La variété sur laquelle la sélection agit vient donc, après le tri
   initial, de la seule mutation (0,1 par naissance, un poids tiré au hasard prend une
   autre valeur de [-3, 3] : `mutate`). Elle est faible.

Quentin propose (a) de faire varier le taux de mutation, (b) de partir d'un **génotype
unique** pour que toute la variété vienne des mutations et qu'on n'attende pas le tri de
la variété de départ, (c) d'un fondateur unique pour toutes les populations (la viabilité
ne se vérifie qu'une fois).

## Protocole

Monde et agent : ceux de `journal/2026-11-15_directions-absolues.md`, inchangés (monde à
déchet 32 × 32, division à 20, sans saisons, cinq moteurs « ingérer / nord / sud / est /
ouest », k = 2, cerveau de 3 nœuds, poids dans [-3, 3]). Départ : 300 **clones** du
fondateur (génotype identique ; l'état du cerveau, les moteurs et la case de départ sont
tirés au hasard par agent, comme avant). Durée : 20 000 pas, 24 populations par
condition, graine 0.

**Choix du fondateur** (fait une fois, avant tout le reste ; ce critère est écrit ici) :
génotypes tirés au hasard (loi uniforme, flux de nombres aléatoires `[0, 7, 0]`) ; on garde
le premier dont une population de 300 clones, **sans mutation** (mu = 0), dans le monde
de ce régime (« directions », nourriture dépendant des positions) pendant 3 000 pas :
(i) ne s'éteint pas ; (ii) a un effectif moyen d'au moins 100 sur les 500 derniers pas
(repère : des génotypes aléatoires tous différents donnaient 158 à 178 dans le contrôle de
la journal `directions-absolues`). On note combien de candidats ont été essayés. Une seule
valeur de fondateur : limite assumée (la conclusion dépend de ce génotype ; un deuxième
fondateur serait un contrôle de plus, pas fait ici).

**Conditions** : taux de mutation mu ∈ {0 ; 0,1 ; 0,3 ; 1,0} par naissance (mu = 1 : chaque
naissance porte une mutation ; c'est le maximum de ce paramètre) × régime
{directions, neutre}. Le régime **neutre** (nourriture tirée au sort entre les vivants,
mêmes cinq moteurs, même fondateur, même mu) est le modèle nul à chaque taux : un taux
plus élevé change aussi la dérive, donc la comparaison à mu = 0,1 ne suffit pas. mu = 0
est le contrôle « sans variété » : tous les agents restent des clones, la sélection entre
génotypes est impossible.

Mesures (une valeur par population : moyenne de la seconde moitié, relevés tous les
100 pas) : celles de `directions` (effectif, naissances, dépendance, persistance,
fréquence des parties contrôle internes et des PTBN dans la population) plus quatre
mesures de variété :

- `lignees` : nombre d'ancêtres du pas 0 (parmi les 300 clones) qui ont encore des
  descendants vivants. Mesure la dérive ou la sélection de lignages, indépendamment du
  génotype (ici tous les ancêtres ont le même, la distinction vient des hasards de vie).
- `genotypes` : nombre de génotypes distincts vivants (sur les poids qui évoluent).
- `distance_fondateur` : nombre moyen de poids qui diffèrent du fondateur.
- `distance_paires` : nombre moyen de poids qui diffèrent entre deux agents tirés au
  hasard (1 000 paires par relevé).

Tests : permutation des populations (20 000, bilatéral, p < 0,01), directions contre
neutre à chaque mu, et directions à chaque mu > 0 contre directions à mu = 0 pour la
dépendance et la persistance. Beaucoup de tests, non corrigés : limite assumée.

## Hypothèses (Claude)

1. **Contrôle mu = 0.** Il n'y a qu'un seul génotype vivant à tout moment et la distance
   au fondateur est nulle (vérifié par la mesure). Les comportements restent ceux du
   fondateur (aucune adaptation possible) : dépendance et persistance de la seconde moitié
   égales, à la dispersion près, à celles du début. Si ce n'était pas vrai, la mesure de
   variété ou de comportement serait fausse.
2. **Variété.** Les génotypes distincts et la distance au fondateur augmentent avec mu,
   dans les deux régimes. Réfutation : pas de monotonie.
3. **Sélection contre dérive de lignages.** À mu = 0,1 et 0,3, le nombre de lignées
   vivantes à la fin est plus faible dans directions que dans neutre (la sélection
   accélère la fixation). Je ne suis pas sûr de la direction : la sélection peut aussi
   maintenir plusieurs lignages en parallèle (bandes de nourriture séparées). Résultat
   rapporté dans les deux cas.
4. **Comportement.** À mu = 0,3 (assez de variété pour que la sélection agisse), la
   dépendance au capteur et la persistance de directions diffèrent de celles de neutre et
   de directions à mu = 0 (p < 0,01). À mu = 1,0, l'effet est plus faible ou inversé
   (charge mutationnelle). Réfutation : l'effet de la sélection ne change pas avec mu.
5. **Structure.** Pas d'enrichissement des parties contrôle internes ni des PTBN par
   rapport à neutre, comme dans tous les mondes testés jusqu'ici (attendu : résultat
   négatif).

## Fondateur retenu (écrit avant l'expérience complète)

`experiments/fondateur/fondateur.py` : les six premiers candidats se sont éteints, le
septième (effectif moyen 117,7 sur les 500 derniers pas des 3 000) est retenu (journal
des essais dans `experiments/fondateur/out/fondateur.txt`). Un essai rapide (2 populations,
600 pas, non retenu comme résultat) montre que ce fondateur **marche déjà en ligne droite**
(persistance proche de 1, dépendance au capteur proche de 0). Le filtre de viabilité a donc
sélectionné, au moins ici, un génotype qui a déjà un cap : l'expérience ne peut pas
demander « la sélection produit-elle des déplacements persistants ? » à partir de ce
fondateur. Elle demande si, avec de la variété, la sélection **conserve** ce cap mieux que
la dérive (neutre).

Hypothèse 4 précisée en conséquence : à mu = 0,3 et mu = 1,0, la persistance de directions
reste plus proche de celle du fondateur (≈ 1) que celle de neutre (où elle s'érode par
dérive) ; la dépendance au capteur n'est pas attendue différente de 0 dans directions.
Réfutation : persistance de directions et de neutre indistinguables à ces taux.

## Limites prévues

Un seul fondateur ; un seul monde ; les populations de directions ont un effectif réduit
(quelques centaines d'agents), la dérive reste forte ; les mesures de variété comptent les
poids qui évoluent (les 3 × 3 + 3 + 15 du cerveau et des moteurs, pas ceux du capteur
d'entrée vers lui-même).

## Résultat

Exécuté le 15 novembre (`experiments/fondateur/run.py`, graine 0, 24 populations par
condition, 20 000 pas, aucune extinction). Valeurs : moyenne ± écart-type entre
populations, seconde moitié. Figure : `experiments/fondateur/out/fondateur_unique.png`.

| mesure | dir. mu 0 | dir. 0,1 | dir. 0,3 | dir. 1 | neutre 0 | neutre 0,1 | neutre 0,3 | neutre 1 |
|---|---|---|---|---|---|---|---|---|
| effectif | 122 ± 14 | 148 ± 22 | 169 ± 8 | 161 ± 2 | 400 | 399 | 400 | 400 |
| lignées vivantes | 21,8 ± 2,5 | 12,8 ± 7,6 | 3,0 ± 3,4 | 1,02 ± 0,09 | 1,7 ± 0,6 | 1,8 ± 0,5 | 1,7 ± 0,6 | 1,8 ± 0,6 |
| génotypes distincts | 1 | 39 ± 6 | 74 ± 5 | 160 ± 2 | 1 | 99 ± 1 | 200 ± 1 | 399 ± 1 |
| distance au fondateur (sur 27) | 0 | 13,5 ± 1,6 | 20,2 ± 1,3 | 22,8 ± 0,7 | 0 | 16,6 ± 1,1 | 22,6 ± 0,7 | 23,1 ± 0,2 |
| distance entre paires | 0 | 11,3 ± 4,3 | 11,4 ± 2,8 | 16,4 ± 0,8 | 0 | 14,2 ± 1,1 | 19,3 ± 0,5 | 21,9 ± 0,1 |
| persistance | 1,00 | 0,90 ± 0,10 | 0,75 ± 0,12 | 0,82 ± 0,02 | 0,65 ± 0,12 | 0,89 ± 0,06 | 0,89 ± 0,02 | 0,90 ± 0,01 |
| dépendance (points) | 0,0 | 0,4 ± 6,5 | 26,3 ± 31,8 | 7,5 ± 7,5 | 26,7 ± 8,7 | −11,1 ± 8,5 | −19,1 ± 4,3 | −17,4 ± 2,6 |
| PC de 1 nœud (%) | 0 | 8,2 ± 13,8 | 6,8 ± 9,0 | 4,2 ± 1,9 | 0 | 7,3 ± 12,5 | 4,4 ± 3,1 | 6,3 ± 2,1 |
| PC de 2 nœuds (%) | 0 | 4,4 ± 10,4 | 9,3 ± 18,4 | 4,6 ± 2,8 | 0 | 6,7 ± 8,0 | 5,7 ± 4,4 | 6,4 ± 2,1 |
| PTBN (%) | 0 | 13,5 ± 17,4 | 11,0 ± 12,5 | 8,5 ± 5,7 | 0 | 8,8 ± 10,7 | 6,5 ± 3,6 | 8,9 ± 2,1 |

Hypothèse par hypothèse :

1. **Contrôle mu = 0 : tenu.** Un seul génotype à tout relevé, distance nulle ;
   dépendance −0,03 puis 0,00 point, persistance 0,998 puis 1,00.
2. **Variété : tenue.** Génotypes distincts et distances croissent avec mu dans les deux
   régimes. Mais le nombre de génotypes suit surtout l'effectif (≈ 26 % des agents à
   mu = 0,1, tous distincts à mu = 1, dans les deux régimes) : il ne compare pas les
   régimes. Les distances sont grandes : à mu = 0,1 déjà, la moitié des 27 poids diffère du
   fondateur et deux agents diffèrent de 11 poids. Un génotype aléatoire différerait de
   27 × 6/7 = 23,1 poids : à mu = 1 les deux régimes y sont (directions 22,8 contre
   neutre 23,1, p = 0,02, non retenu). **La variété ne manquait donc pas à 0,1 sur
   20 000 pas** : la prémisse de l'expérience (« peu de variété ») est fausse dans la
   seconde moitié. Directions reste plus proche du fondateur que neutre à 0,1 et 0,3
   (p < 0,0001), mais les effectifs diffèrent (150 contre 400), ce qui suffit peut-être.
3. **Lignées : réfutée dans le sens écrit, et le résultat est plus intéressant.** Sans
   mutation, directions **conserve** ses lignées : 22 des 300 ancêtres ont encore des
   descendants en seconde moitié, et la courbe est plate après l'effondrement initial
   (300 → ≈ 25 dans les premiers pas, effectif 300 → 125). Neutre tombe à 1,7 (dérive).
   Avec mutation, directions perd ses lignées d'autant plus vite que mu est grand :
   12,8 (plus que neutre, p < 0,0001), 3,0 (p = 0,07), 1,02 (moins que neutre,
   p < 0,0001). Lecture proposée, non testée : des clones qui marchent droit ne se
   remplacent pas entre eux (chaque lignée garde sa bande), et ce sont les mutants
   avantageux qui balaient les autres lignées.
4. **Comportement : hypothèse précisée réfutée.** La persistance de directions ne reste
   pas à 1 : 0,90, 0,75, 0,82 (chacune différente de mu = 0, p < 0,0001), et elle est
   plus **basse** que celle de neutre à mu = 0,3 et 1 (p < 0,0001), pas plus haute. Dans
   le même temps l'effectif monte (122 → 148, 169, 161 ; p < 0,0001 contre mu = 0) : la
   sélection s'éloigne de la ligne droite pure du fondateur et la population y gagne. La
   dépendance au capteur apparaît à mu = 0,3 (26 points, très dispersée entre populations,
   encore en hausse à 20 000 pas : 37 points à la fin) et à mu = 1 (7,5), pas à 0,1.
   À mu = 1 l'effectif atteint vite un plateau (≈ 160) plus bas que la fin de la courbe à
   mu = 0,3 (≈ 175, encore en hausse) : compatible avec une charge mutationnelle, non testé
   directement.
5. **Structure : résultat négatif, comme attendu.** Aucun enrichissement des parties
   contrôle internes ni des PTBN par rapport à neutre. À mu = 1, les PC de 1 nœud sont
   moins fréquentes dans directions (4,2 % contre 6,3 %, p = 0,0007 ; loi uniforme 6,0 %).

## Limites constatées

- **Le régime neutre n'est pas un nul propre pour le comportement.** Le même génotype,
  sans mutation, a une persistance de 1,00 et une dépendance de 0 dans directions, mais
  0,65 et 27 points dans neutre : la persistance et la dépendance dépendent de ce que le
  capteur reçoit, donc du monde. Neutre reste le nul de la dérive (lignées, distances,
  structure). Pour le comportement, la comparaison propre ici est directions à mu > 0
  contre directions à mu = 0. Cette limite vaut aussi pour les comparaisons de
  dépendance « régime contre neutre » des expériences précédentes.
- Un seul fondateur, retenu par un filtre de viabilité qui a éliminé les six premiers
  candidats ; il marchait déjà droit. Rien ne dit qu'un autre fondateur donnerait les
  mêmes courbes.
- La dépendance (mu = 0,3) et l'effectif (mu = 0,1 et 0,3) montent encore à 20 000 pas.
- mu est borné à 1 (une mutation par naissance au plus).
- Beaucoup de tests non corrigés.

## Suites possibles

- Un deuxième et un troisième fondateur, pour savoir ce qui tient au génotype de départ.
- Tester la lecture « les clones gardent chacun leur bande » : mu = 0 dans le monde
  mélangé (sans espace) devrait perdre ses lignées comme neutre.
- Durée plus longue à mu = 0,3 (rien n'est stabilisé).
