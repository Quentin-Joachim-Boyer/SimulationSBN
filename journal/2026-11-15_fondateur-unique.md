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

## Limites prévues

Un seul fondateur ; un seul monde ; les populations de directions ont un effectif réduit
(quelques centaines d'agents), la dérive reste forte ; les mesures de variété comptent les
poids qui évoluent (les 3 × 3 + 3 + 15 du cerveau et des moteurs, pas ceux du capteur
d'entrée vers lui-même).

## Résultat

(à compléter après l'exécution)
