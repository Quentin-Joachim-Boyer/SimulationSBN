# Moteurs lecteurs : les actions lues par des nœuds sans retour

Écrit avant de lancer l'expérience ; « Résultat » est rempli après.

## Pourquoi

Dans le monde à déchet (`2026-11-14_monde-dechet.md`), les actions étaient lues
directement sur deux nœuds du cerveau. Quentin propose de les faire porter par des nœuds
uniquement lecteurs : ils lisent le cerveau et rien ne revient d'eux. On peut alors
ajouter des actions sans changer la dynamique du cerveau.

Décisions de Quentin (15 novembre) :

1. un moteur lit le cerveau seul, pas le capteur ;
2. un moteur est un nœud SBN ordinaire, mis à jour au même rythme que le milieu : il a
   donc un pas de retard sur le cerveau, et l'agent réagit en deux pas au lieu d'un.
   Plus tard, on essaiera plusieurs pas d'agent pour un pas du milieu ;
3. quand des moteurs se contredisent (nord et sud), leurs effets s'additionnent, donc
   s'annulent. Chaque moteur allumé coûte quand même.

## Question

1. Avec des lecteurs, « toujours ingérer » n'oblige plus un nœud du cerveau à rester
   allumé : il suffit que le cerveau ne soit jamais éteint. L'enrichissement en nœuds de
   contrôle du régime mélangé disparaît-il ?
2. Avec une réaction en deux pas, la survie sélectionne-t-elle encore un comportement
   qui dépend du contexte ?

## Protocole

Le monde, ses paramètres, la durée, les mesures de structure et le test sont ceux du
monde à déchet, sans aucun changement ni nouveau calibrage. Seule la lecture des actions
change.

- **Agent** : `Architecture(1, 3, 2)`. Le cerveau garde ses 12 poids ; deux moteurs,
  « ingérer » et « bouger », lisent chacun les trois nœuds du cerveau (6 poids de plus,
  dans [-3, 3]). Un moteur est allumé si la somme pondérée de ce qu'il lit est positive.
- **Deux lectures** :
  - **retardée** (le choix de Quentin) : au pas t, le moteur vaut ce que donnait le
    cerveau du pas t - 1 ;
  - **immédiate** (témoin ajouté par Claude) : le moteur suit le cerveau du pas même.
    Avec des poids « un nœud, un moteur », elle redonne exactement la lecture directe ;
    c'est testé. Ce témoin sépare l'effet des lecteurs de celui du délai.
- **Régimes** : mélangé et espace pour chaque lecture, plus un régime neutre.
  24 populations par régime, 20 000 pas, graine 0, mutation 0,1 par naissance. Comme le
  génotype passe de 12 à 18 poids, le cerveau reçoit deux mutations sur trois.
- **Dépendance au contexte** : P(bouger | capteur 0) - P(bouger | capteur 1), le capteur
  étant celui auquel l'action a pu réagir : celui du pas précédent en lecture immédiate,
  celui d'il y a deux pas en lecture retardée.
- **Mesures de structure** : les quatre mêmes, sur le capteur et le cerveau. Les moteurs
  n'y entrent pas, puisque rien ne revient d'eux.
- **Motif de déplacement** (prévu cette fois) : part des agents finaux dont le moteur
  « bouger » reste allumé quand le capteur vaut 0 et oscille quand il vaut 1, en partant
  des états du cerveau qui allument le moteur « ingérer ».
- **Références** : le régime neutre de cette expérience, et les populations du monde à
  déchet en lecture directe (`experiments/monde_dechet/out/par_population.npz`).
- **Test** : permutation des populations, bilatéral, seuil p < 0,01.

Les moteurs de direction (nord, sud, est, ouest, effets additionnés) sont codés et
testés, mais pas utilisés ici : sans capteur qui indique une direction, ils n'ont rien
à lire. C'est l'étape suivante.

## Hypothèses

1. **Régime mélangé, nœud de contrôle du cerveau seul.** Avec des lecteurs (retardés ou
   immédiats), la part ne se distingue plus de celle du régime neutre, alors qu'elle la
   dépassait en lecture directe (17,6 % contre 9,5 %). Réfutation : part supérieure au
   régime neutre avec p < 0,01. Je ne suis pas sûr de moi : un nœud qui s'entretient seul
   reste la façon la plus simple de ne jamais s'éteindre.
2. **Régime espace, lecture immédiate.** Le comportement est celui de la lecture directe :
   dépendance au contexte d'au moins +40 points, et motif « allumé, oscille » majoritaire
   dans plus de la moitié des populations. Réfutation : dépendance inférieure à +40 points.
3. **Régime espace, lecture retardée.** La dépendance au contexte est nettement plus
   faible qu'en lecture immédiate. Raison : l'agent qui vient de bien manger a déjà décidé
   son pas suivant ; quand il s'arrête enfin, il est une case plus loin. Réagir tard ne
   paie plus, et je m'attends à un rythme aveugle. Réfutation : pas de différence
   significative entre lecture retardée et lecture immédiate.
4. **Régime espace, structure.** Aucune des quatre mesures n'est enrichie par rapport au
   régime neutre, quelle que soit la lecture, comme dans le monde à déchet.
   Réfutation : une mesure supérieure au régime neutre avec p < 0,01.
5. Sans prédiction : la persistance des populations en lecture retardée, et les effectifs.

## Durée limite et critère d'abandon

Une séance. Aucun réglage du monde. Une extinction est notée telle quelle.

## Prolongation (décidée après le premier lancement, écrite avant de la lancer)

Vu à la fin du premier lancement, avant toute autre analyse : en régime espace à lecture
retardée, la dépendance au contexte monte encore au pas 20 000 (moyenne vers +25 points,
populations étalées de -18 à +50). Le régime n'est pas à l'équilibre, donc la moyenne de
la seconde moitié ne dit pas si le délai réduit la dépendance ou s'il ralentit seulement
son évolution.

`python experiments/moteurs_lecteurs/prolongation.py` : les mêmes 24 populations du régime
espace retardé (même graine, donc mêmes 20 000 premiers pas), poursuivies jusqu'à
100 000 pas. Mesure : dépendance moyenne sur les 10 000 derniers pas.

**Hypothèse 6.** Le délai ralentit sans empêcher : sur les 10 000 derniers pas, la
dépendance moyenne dépasse +40 points, et au moins 18 populations sur 24 dépassent +40.
Réfutation : moyenne inférieure à +40, ou moins de 18 populations. Les trois populations
à -18 peuvent être coincées dans un rythme aveugle ; je n'en sais rien.

## Résultat

`python experiments/moteurs_lecteurs/run.py`, graine 0, 24 populations par régime,
20 000 pas, moyennes de la seconde moitié ± écart-type entre populations. Aucune extinction.

|                             | Mélangé retardé | Mélangé immédiat | Espace retardé | Espace immédiat | Neutre        |
|-----------------------------|-----------------|------------------|----------------|-----------------|---------------|
| Effectif                    | 294             | 294              | 160            | 173             | 400           |
| P(bouger, capteur 0)        | 0,2 %           | 0,2 %            | 77,1 ± 20,7 %  | 98,3 ± 0,5 %    | 30,6 ± 14,2 % |
| P(bouger, capteur 1)        | 0,2 %           | 0,2 %            | 54,5 ± 4,5 %   | 43,0 ± 1,7 %    | 39,3 ± 15,5 % |
| **Dépendance au contexte**  | 0,0             | 0,0              | +22,6 ± 22,2   | +55,3 ± 2,0     | -8,7 ± 7,7    |
| Nœud de contrôle (cerveau)  | 14,9 ± 10,2 %   | 18,0 ± 15,2 %    | 8,7 ± 12,6 %   | 13,0 ± 16,3 %   | 7,9 ± 7,7 %   |
| PSBN (cerveau)              | 4,3 ± 5,2 %     | 4,5 ± 4,6 %      | 1,4 ± 3,0 %    | 4,4 ± 6,0 %     | 2,8 ± 4,0 %   |
| Scission SBN                | 11,3 ± 14,2 %   | 9,1 ± 8,5 %      | 16,2 ± 23,0 %  | 5,4 ± 16,3 %    | 10,9 ± 7,2 %  |
| Contrôle interne            | 16,1 ± 10,5 %   | 19,1 ± 14,8 %    | 10,2 ± 13,4 %  | 15,1 ± 16,0 %   | 9,1 ± 7,7 %   |

Valeurs p contre le régime neutre :

|                        | Mélangé retardé | Mélangé immédiat | Espace retardé | Espace immédiat |
|------------------------|-----------------|------------------|----------------|-----------------|
| Dépendance au contexte | < 0,0001        | < 0,0001         | < 0,0001       | < 0,0001        |
| Nœud de contrôle       | 0,0115          | 0,0053           | 0,81           | 0,19            |
| PSBN                   | 0,27            | 0,20             | 0,19           | 0,30            |
| Scission SBN           | 0,90            | 0,44             | 0,29           | 0,16            |
| Contrôle interne       | 0,013           | 0,0047           | 0,73           | 0,12            |

- **Hypothèse 1 : réfutée.** En régime mélangé, les nœuds de contrôle restent enrichis
  avec des lecteurs : 18,0 % en lecture immédiate contre 7,9 % en neutre (p = 0,0053),
  14,9 % en lecture retardée (p = 0,0115, même sens, juste au-dessus du seuil). Ni l'une
  ni l'autre ne se distingue de la lecture directe (17,6 % ; p = 0,91 et p = 0,33). Mon
  soupçon était faux : l'enrichissement ne vient pas de ce que les actions logeaient
  dans le cerveau. Le contrôle interne suit (p = 0,0047 et p = 0,013).
  En revanche l'enrichissement en PSBN n'est pas retrouvé : 4,3 % et 4,5 % contre 2,8 %
  en neutre (p = 0,27 et p = 0,20), au lieu de 7,8 % en lecture directe. L'écart avec la
  lecture directe est à p = 0,023 et p = 0,019, au-dessus du seuil : indécis.
- **Hypothèse 2 : confirmée pour la dépendance, pas pour le motif.** En lecture
  immédiate, la dépendance est de +55,3 points (+50,6 en lecture directe, p = 0,028),
  avec les mêmes fréquences de déplacement (98 % et 43 %). Le motif « allumé, oscille »
  est porté par 46,3 % des agents finaux (0,6 % en neutre, p < 0,0001), mais il n'est
  majoritaire que dans 11 populations sur 24, et non dans plus de la moitié.
- **Hypothèse 3 : confirmée telle qu'écrite, mais mon raisonnement était trop simple.**
  En lecture retardée, la dépendance (+22,6) est bien plus faible qu'en lecture immédiate
  (p < 0,0001). Elle reste pourtant très au-dessus du régime neutre : réagir tard paie
  encore. Voir la prolongation.
- **Hypothèse 4 : confirmée.** En régime espace, aucune mesure de structure n'est enrichie
  (p ≥ 0,12), quelle que soit la lecture.
- **Sans prédiction.** Aucune extinction. Le délai coûte environ 7 % d'effectif en régime
  espace (160 contre 173).

Le régime neutre est compatible avec la loi uniforme (8,49 %, 2,49 %, 12,14 %, 9,79 %).

### Prolongation

`python experiments/moteurs_lecteurs/prolongation.py`, mêmes 24 populations jusqu'à
100 000 pas. Sur les pas 10 001 à 20 000 on retrouve +22,6 ± 22,2 : ce sont bien les
mêmes populations.

- **Hypothèse 6 : réfutée.** Sur les 10 000 derniers pas, la dépendance moyenne est de
  +34,2 ± 17,7 points, et 13 populations sur 24 dépassent +40 (il en fallait 18).
- Ce que montre la figure, et que je n'avais pas prévu : chaque population bascule,
  dans les deux sens et à plusieurs reprises, entre deux états, l'un vers +50 points et
  l'autre vers -18. Les effectifs sont les mêmes dans les deux états (160 contre 160).
- Au pas 20 000, les populations du premier état portent surtout le motif « allumé,
  oscille » (56 % à 92 % des agents). Celles du second bougent 38 % du temps après un
  capteur à 0 et environ 50 % après un capteur à 1. C'est compatible avec un rythme
  aveugle d'un pas sur deux, dont la phase suffirait à expliquer l'écart négatif, mais
  je ne l'ai pas établi : leur motif dominant est « variable », il dépend de l'état de
  départ du cerveau.
- Lecture : avec une réaction en deux pas, la stratégie qui dépend du contexte n'a plus
  d'avantage net sur l'autre état. Le délai ne fait pas que ralentir son évolution.

### Limites

- Une graine. Quarante tests, le seuil de 0,01 ne valait que pour les hypothèses.
- La prolongation a été décidée après avoir vu la première figure ; son hypothèse a été
  écrite avant de la lancer.
- Le second état du régime retardé n'est pas identifié : ni son génotype type, ni ce
  qui le rend aussi viable que la stratégie sensible au contexte.
- Les mesures de structure sont très dispersées entre populations (écarts-types de 8 à
  23 points) : un effet modeste passerait inaperçu.
- Avec 18 poids au lieu de 12, le cerveau reçoit moins de mutations qu'en lecture directe.

## Suites possibles

- Plusieurs pas d'agent pour un pas du milieu (prévu par Quentin) : la réaction en deux
  pas du réseau tiendrait alors dans un pas du monde. Prédiction à poser : on retrouve
  le comportement de la lecture immédiate.
- Moteurs de direction et capteurs qui indiquent une direction ; le code des directions
  additionnées existe et est testé.
- Régime mélangé : chercher quels nœuds du cerveau deviennent nœuds de contrôle, puisque
  ce ne sont pas des nœuds d'action.
