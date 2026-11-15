# Saisons cachées : un monde où le capteur ne dit pas tout

Écrit avant de lancer l'expérience ; « Contrôle démographique » et « Résultat » après.

## Pourquoi

Dans le monde à déchet, aucune partie contrôle (PC) interne n'émerge : le contexte vient
déjà du capteur. Quentin et Claude conviennent d'essayer un monde où l'information de
l'agent est locale et partielle, comme dans une évolution naturelle. Quentin ne s'attend
pas forcément à un résultat positif : un cerveau de 3 nœuds est peut-être trop peu
expressif. C'est un point de départ.

Deux décisions de Quentin sur la méthode :

- pas de calibrage sur « le meilleur agent construit à la main ». La question est de
  savoir si les PC/PO sont favorisées ; ce que l'évolution atteint dépend du voisinage
  mutationnel, pas seulement de l'optimum ;
- pas d'indice fabriqué (la « pluie » proposée par Claude était forcée). Le seul signal
  est la nourriture, perçue en essayant de manger.

## Question

Quand le bon comportement dépend d'un état du monde que le capteur ne montre pas, les
décompositions 1/2 et 2/1 du cerveau sont-elles favorisées ?

## Protocole

Monde à déchet en 2D, lecture directe, capteur de bien-être inchangé, mêmes paramètres.
Un seul ajout : des **saisons**. La nourriture n'arrive qu'en été. L'agent ne perçoit
pas la saison ; en hiver son capteur reste à 0, comme sur une case vide en été.

- **Durées, fixées par raisonnement et non par essai** : un agent a au plus 19 d'énergie
  (division à 20), environ 10 en moyenne. En hiver, un agent en veille dépense 1 par pas,
  un agent qui ingère et bouge 3. L'hiver dure **8 pas** : plus que ce que tient un agent
  actif moyen (3 à 4 pas), moins que ce que tient un agent en veille moyen (10 pas).
  L'été dure **40 pas**, de quoi reconstituer la population.
  Correction : Claude avait proposé à Quentin « deux fois la réserve d'énergie » ; c'était
  une erreur, l'entretien seul tuerait alors tout le monde.
- **Régimes**, 24 populations chacun, 20 000 pas, graine 0 :
  - **saisons** ;
  - **sans saisons** : le monde à déchet tel quel (témoin) ;
  - **neutre à saisons** : nourriture tirée au sort en été, rien en hiver, où chacun ne
    paie que l'entretien (comme en veille). Il subit les mêmes goulots que le régime
    saisons, donc la même dérive.
- **Mesures** : celles d'avant, plus la part des pas avec ingestion et avec déplacement
  en été et en hiver. **Économie d'hiver** = P(ingérer, été) − P(ingérer, hiver).
- **Test** : permutation des populations, seuil p < 0,01.

## Contrôle démographique permis

Une seule population de génotypes uniformes, régime saisons, 2 000 pas, en ne regardant
que l'effectif. Si elle s'éteint, l'hiver est raccourci de 2 pas, et ainsi de suite.
Rien d'autre n'est réglé.

## Hypothèses

1. **Comportement** : en régime saisons, l'économie d'hiver est positive et supérieure à
   celle du régime neutre. Réfutation : pas de différence (p ≥ 0,01).
   Je n'en suis pas sûr : sortir de la veille demande de sonder sans signal, et 8 pas
   d'hiver sur 48 ne pèsent peut-être pas assez.
2. **Structure** : ni la 1/2 ni la 2/1 lues sur les poids ne sont enrichies en régime
   saisons par rapport au neutre à saisons. C'est aussi le pronostic de Quentin.
   Réfutation : l'une des deux supérieure au neutre avec p < 0,01.
3. Sans prédiction : PTBN, PSBN, et la comparaison avec le régime sans saisons.

## Contrôle démographique

Une population de génotypes uniformes, 2 000 pas : aucune extinction. Sur les six
dernières années, 142 à 179 agents en fin d'été et 119 à 157 en fin d'hiver. L'hiver ne
retire donc que 10 à 15 % de la population, moins que je ne pensais : il reste sans doute
de la nourriture sur les cases. Paramètres laissés tels quels, comme prévu.

## Résultat

`python experiments/saisons/run.py`, graine 0, 24 populations par régime, 20 000 pas,
moyennes de la seconde moitié ± écart-type entre populations. Aucune extinction.

|                              | Saisons       | Sans saisons  | Neutre à saisons |
|------------------------------|---------------|---------------|------------------|
| Effectif                     | 146           | 173           | 363              |
| P(ingérer), été              | 99,1 %        | 99,4 %        | 39,0 %           |
| P(ingérer), hiver            | 99,0 %        |               | 33,3 %           |
| **Économie d'hiver**         | +0,1 ± 0,4    |               | +5,7 ± 3,8       |
| P(bouger), été / hiver       | 59,8 / 62,4 % | 58,5 %        | 41,7 / 36,4 %    |
| Dépendance au capteur        | +50,8 ± 12,8  | +54,7 ± 2,6   | -8,6 ± 6,9       |
| 1/2 sur les poids            | 4,9 ± 7,7 %   | 2,9 ± 4,3 %   | 4,7 ± 4,0 %      |
| 2/1 sur les poids            | 7,2 ± 11,0 %  | 3,0 ± 4,9 %   | 4,0 ± 3,9 %      |
| PTBN (cerveau seul)          | 14,1 ± 12,9 % | 8,8 ± 9,2 %   | 9,3 ± 7,8 %      |
| PSBN (cerveau seul)          | 1,2 ± 3,2 %   | 0,04 ± 0,06 % | 3,0 ± 3,4 %      |

- **Hypothèse 1 : réfutée.** Les agents ne font aucune économie d'hiver : ils tentent
  d'ingérer 99 % du temps, été comme hiver, et bougent autant. Leur comportement est
  celui du monde sans saisons (dépendance au capteur +50,8 contre +54,7, p = 0,20). La
  saison est ignorée. (L'écart avec le neutre est significatif mais dans l'autre sens :
  un cerveau tiré au hasard s'active un peu moins quand son capteur reste à 0.)
- **Hypothèse 2 : confirmée.** Ni la 1/2 (4,9 % contre 4,7 %, p = 0,90) ni la 2/1 (7,2 %
  contre 4,0 %, p = 0,21) lues sur les poids ne sont enrichies.
- **Sans prédiction.** PTBN 14,1 % contre 9,3 % (p = 0,13). Aucune mesure ne passe le
  seuil dans le sens d'un enrichissement.

**Pourquoi la saison est ignorée, à mon avis.** L'hiver ne pèse pas assez. Le contrôle
démographique le laissait voir (10 à 15 % de pertes) et l'effectif le confirme (146
contre 173 sans saisons). Tel que je l'ai réglé, l'hiver ne peut pas être beaucoup plus
dur : au-delà d'une dizaine de pas, l'entretien seul tue même un agent en veille. Le
monde ne laisse donc presque aucune marge entre « l'hiver ne compte pas » et « l'hiver
tue tout le monde ». C'est un défaut de conception, pas un résultat sur les PC/PO.

### Limites

- Une graine, un seul couple de durées (été 40, hiver 8), non réglé comme convenu.
- L'expérience ne dit rien de ce qui se passerait si la saison comptait.

## Suites possibles

- Donner de la marge à la veille : un entretien plus faible que le coût des actions
  (par exemple 1 pour 4), ou une réserve plus grande (division à 40), pour qu'un hiver
  long soit survivable en veille et mortel en activité.
- Un cerveau de 4 nœuds, si le comportement de veille et de sonde s'avère hors de portée.
