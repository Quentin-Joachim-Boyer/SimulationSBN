# Saisons cachées, deuxième essai : une réserve doublée et un hiver de 20 pas

Écrit avant de lancer l'expérience ; « Contrôle démographique » et « Résultat » après.

## Pourquoi

Premier essai (`2026-11-15_saisons-cachees.md`) : résultat négatif, mais non informatif.
Les agents ignorent la saison, parce que l'hiver (8 pas) ne retire que 10 à 15 % de la
population. Avec une réserve de 20, un agent en veille tient environ 10 pas et un agent
qui ingère et bouge 3 à 4 : il n'y a presque pas de marge entre « l'hiver ne compte pas »
et « l'hiver tue tout le monde ». Quentin demande de relancer avec une réserve doublée.

## Question

Même question qu'au premier essai : quand le bon comportement dépend d'un état du monde
que le capteur ne montre pas, les décompositions PC/PO 1/2 et 2/1 sont-elles favorisées ?
Plus une condition préalable : l'hiver compte-t-il enfin pour la survie ?

## Protocole

Monde du premier essai, avec deux changements, fixés ici par raisonnement et non par essai :

- **Réserve doublée** : division à **40** d'énergie (au lieu de 20). Un agent en veille
  tient alors environ 20 pas en hiver, un agent qui ingère et bouge environ 7.
- **Hiver de 20 pas.** Le rapport des deux survies (veille contre activité) reste celui
  d'avant, mais l'hiver passe de 0,8 fois à 1 fois la durée de survie moyenne d'un agent
  en veille : les agents en veille les moins bien dotés meurent, les agents actifs
  presque tous. Ce que j'en attends n'est qu'un ordre de grandeur ; c'est le contrôle
  démographique ci-dessous qui dit si l'hiver est survivable.
- **Été de 80 pas**, soit le double de l'été d'avant, comme la réserve : reconstituer une
  réserve de 40 demande deux fois plus de temps qu'une réserve de 20. L'année fait donc
  100 pas.
- **Relevés tous les 20 pas** au lieu de 100. Une année de 100 pas relevée tous les
  100 pas verrait toujours la même saison, et le premier essai avait déjà montré des
  oscillations d'effectif dues au rythme des relevés.
- Tout le reste est inchangé : monde à déchet 2D, lecture directe, capteur de bien-être,
  3 nœuds de cerveau, mutation 0,1 par naissance, 300 agents au départ, 24 populations
  par régime, 20 000 pas, graine 0.
- **Régimes**, ceux d'avant, tous avec la réserve de 40 :
  - **saisons** (été 80, hiver 20) ;
  - **sans saisons** : témoin, relancé car la réserve change aussi lui ;
  - **neutre à saisons** : nourriture tirée au sort en été, rien en hiver, chacun ne paie
    que l'entretien ; modèle nul.
- **Mesures** : celles d'avant. Économie d'hiver = P(ingérer, été) − P(ingérer, hiver).
  Perte hivernale = 1 − effectif en fin d'hiver / effectif en fin d'été, relevée à
  partir des relevés des pas 80 et 100 de chaque année, moyennée sur la seconde moitié.
- **Test** : permutation des populations (20 000 permutations, bilatéral), seuil
  p < 0,01. Beaucoup de tests, non corrigés : limite assumée.
- Affichage : les titres des panneaux sont raccourcis (celui du troisième était coupé) ;
  les formules des mesures sont rappelées ici.

## Contrôle démographique permis

Une seule population de génotypes uniformes, régime saisons, 2 000 pas, en ne regardant
que l'effectif. Si elle s'éteint, l'hiver est raccourci de 2 pas, et ainsi de suite.
Rien d'autre n'est réglé. Je prévois qu'elle survit.

## Hypothèses

0. **L'hiver compte.** En régime saisons, la perte hivernale moyenne est d'au moins
   **30 %**. Si elle est plus faible, l'expérience est de nouveau non informative sur
   les PC/PO et je le dis ainsi, sans régler à nouveau les durées dans ce journal.
1. **Comportement** : l'économie d'hiver du régime saisons est supérieure à celle du
   régime neutre (p < 0,01). Réfutation : pas de différence. Je n'en suis pas sûr :
   l'agent ne perçoit pas la saison, et moins ingérer en hiver suppose de se mettre au
   repos sans autre signal que l'absence de nourriture, qui existe aussi en été.
2. **Structure** : ni la 1/2 ni la 2/1 lues sur les poids ne sont enrichies en régime
   saisons par rapport au neutre à saisons. C'est le pronostic de Quentin (cerveau de
   3 nœuds peut-être trop peu expressif). Réfutation : l'une des deux supérieure au
   neutre avec p < 0,01.
3. Sans prédiction : PTBN, PSBN, la comparaison avec le régime sans saisons, et l'effectif.

## Durée limite et critère d'abandon

Une exécution, environ 20 000 pas × 72 populations. Si plus de la moitié des populations
d'un régime s'éteignent, le résultat est rapporté tel quel et rien n'est relancé sans
l'accord de Quentin.

## Suites possibles

Un entretien plus faible que les actions, un cerveau de 4 nœuds, ou un capteur local
supplémentaire, si l'hiver compte mais que rien ne se passe.
