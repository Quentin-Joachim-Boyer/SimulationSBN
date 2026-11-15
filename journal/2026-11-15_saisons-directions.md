# Saisons cachées avec les cinq moteurs, départ aléatoire, mutation 0,5

Écrit avant de lancer l'expérience ; « Résultat » est rempli après.

## Pourquoi

Quentin (15 novembre), après avoir regardé les populations à fondateur unique : le
comportement viable du fondateur semble s'imposer (minimum local) ; maintenant que la
simulation ressemble davantage à ce qu'il imaginait (cerveau sans étiquette, cinq moteurs,
agents qui suivent une ligne), il propose de remettre les saisons. Il choisit le départ
de 300 génotypes aléatoires et un taux de mutation de 0,5 par naissance.

Raison de s'y intéresser pour la question de recherche : en hiver la nourriture n'arrive
plus et le capteur reste à 0 ; un agent qui change de ligne quand il n'est pas nourri se
dépense pour rien. Répondre à l'hiver (« pas nourri depuis plusieurs pas : j'arrête »)
demande de la mémoire interne, donc peut-être une partie contrôle. Les deux essais de
saisons précédents (lecture directe, moteur « bouger » au hasard, mutation 0,1) ont été
négatifs : saison ignorée, aucune PC favorisée.

## Protocole

Monde : celui de `2026-11-15_saisons-reserve.md` (32 × 32, division à 40, été 80 pas,
hiver 20 pas ; en hiver aucune nourriture n'arrive et l'agent ne perçoit pas la saison).
Agent : capteur de bien-être d'un bit, cerveau de 3 nœuds, cinq moteurs lecteurs
(ingérer, nord, sud, est, ouest), lecture retardée, k = 2. Départ : 300 génotypes
uniformes. Mutation : 0,5 par naissance. 200 années (20 000 pas), 24 populations par
régime, graine 0.

Régimes : **saisons** ; **sans saisons** (même monde, nourriture toute l'année) ;
**neutre à saisons** (nourriture tirée au sort entre vivants, en été seulement).

Mesures, une valeur par année (80 pas puis 20 pas, donc jamais de fenêtre alignée sur une
seule saison), puis une valeur par population (moyenne des 100 dernières années) :
effectif en fin d'été et en fin d'hiver, perte hivernale, économie d'hiver
(P(ingérer, été) − P(ingérer, hiver)), déplacement hiver moins été, dépendance au capteur,
persistance, PC de 1 et de 2 nœuds lues sur les poids, PTBN. Test par permutation
(20 000, bilatéral, p < 0,01), saisons contre sans saisons et contre neutre. Non corrigé.

Rappel de la limite constatée au résultat 14 : le neutre est le nul de la dérive et de la
structure, pas un nul propre du comportement. Pour le comportement, on regarde aussi
l'écart à 0 et l'évolution depuis les 10 premières années.

## Contrôle démographique (le seul permis)

Une population, régime saisons, 20 années : pas d'extinction, 45 à 73 agents en fin d'été,
36 à 57 en fin d'hiver. La perte hivernale y est faible (environ 10 %) : la population
de départ est très en dessous de ce que le monde peut nourrir, les stocks des cases
durent tout l'hiver. Paramètres laissés tels quels (pas de calibrage) ; si la perte reste
faible, l'expérience sera non informative sur la réponse à l'hiver, et ce sera rapporté.

## Hypothèses (Claude)

1. **L'hiver compte** : perte hivernale d'au moins 30 % en seconde moitié dans le régime
   saisons (seuil du résultat 11). Vu le contrôle, je n'en suis pas sûr : elle devrait
   monter si l'effectif monte avec l'adaptation.
2. **La saison reste en grande partie ignorée** : économie d'hiver inférieure à 10 points.
   Réfutation (résultat positif) : économie d'au moins 10 points et supérieure au neutre.
3. **Déplacement** : les agents bougent autant ou plus en hiver qu'en été (écart ≥ 0),
   comme au résultat 11. Réfutation : ils bougent nettement moins en hiver (écart
   inférieur à −10 points).
4. **Structure** : aucune PC lue sur les poids ni PTBN enrichie dans saisons, ni contre
   sans saisons ni contre neutre. Réfutation : un enrichissement à p < 0,01 contre les
   deux.

## Résultat

Exécuté le 15 novembre (`experiments/saisons_directions/run.py`, graine 0, 24 populations
par régime, 200 années, aucune extinction). Moyenne ± écart-type entre populations, 100
dernières années ; entre crochets, moyenne des 10 premières années.

| mesure | saisons | sans saisons | neutre à saisons |
|---|---|---|---|
| effectif fin d'été | 175 ± 10 [89] | 182 ± 6 [113] | 408 |
| effectif fin d'hiver | 122 ± 6 [75] | 182 ± 6 [114] | 145 |
| perte hivernale (%) | 29,6 ± 5,2 [13,6] | −0,4 | 64,5 |
| ingérer, été / hiver (%) | 98,5 / 98,0 | 98,9 / — | 30,7 / 25,2 |
| économie d'hiver (points) | 0,5 ± 0,6 [−3,6] | — | 5,5 ± 2,3 |
| bouger, été / hiver (%) | 60,4 / 66,2 [93,6 / 96,7] | — | 66,7 / 54,7 |
| bouger hiver − été (points) | +5,9 ± 2,5 | — | −12,0 ± 3,4 |
| dépendance au capteur (points) | 46,9 ± 24,6 [−3,9] | 51,4 ± 21,0 [−3,9] | −18,7 |
| persistance | 0,66 ± 0,14 [0,92] | 0,62 ± 0,15 [0,90] | 0,92 |
| PC de 1 nœud, poids (%) | 5,6 ± 11,3 | 1,0 ± 2,4 | 7,0 ± 6,4 |
| PC de 2 nœuds, poids (%) | 4,6 ± 16,0 | 1,5 ± 2,9 | 5,5 ± 3,2 |
| PTBN (%) | 6,1 ± 9,6 | 4,6 ± 13,8 | 7,3 ± 2,9 |

1. **L'hiver compte : à la limite.** Perte hivernale 29,6 %, juste sous le seuil de 30 %
   écrit à l'avance (13,6 % les dix premières années : elle monte avec l'effectif, comme
   prévu). L'hiver retire près d'un tiers de la population chaque année ; le seuil n'est
   pas atteint au sens strict.
2. **La saison est ignorée (hypothèse tenue, résultat négatif).** Économie d'hiver
   0,5 point : les agents tentent d'ingérer 98 % du temps en hiver comme en été.
3. **Ils bougent plus en hiver (hypothèse tenue).** +5,9 points (neutre −12,0,
   p < 0,0001) : capteur à 0, donc déplacement, pour rien.
4. **Structure : aucune PC ni PTBN enrichie (hypothèse tenue, résultat négatif).**
   Saisons contre sans saisons : p = 0,07 (PC de 1 nœud), 0,59, 0,71 ; contre neutre :
   p ≥ 0,56. Dispersion énorme entre populations (écarts-types de 10 à 16 points).

Sans prédiction :

- Le régime saisons ne se distingue du régime sans saisons que par la démographie :
  dépendance (p = 0,52) et persistance (p = 0,47) indistinguables.
- Avec le départ aléatoire et mu = 0,5, la dépendance au capteur atteint 47 à 51 points et
  les agents ne bougent plus que 60 % du temps en été : le comportement « rester quand on
  est nourri, bouger sinon » réapparaît avec cinq moteurs. Au résultat 13 (mu = 0,1,
  division à 20) la dépendance n'était que de 18 points et montait encore. La mutation
  plus forte, la réserve doublée ou les deux peuvent l'expliquer : non séparé ici.
- Dans sans saisons, les PC lues sur les poids sont plus rares que la loi uniforme
  (1,0 % et 1,5 % contre 6,0 %), comme au résultat 9 : cerveaux plus intégrés que le
  hasard. Non testé contre un neutre sans saisons (il n'y en a pas dans cette expérience).

## Limites

Une graine ; seuil de l'hypothèse 1 manqué de peu ; pas de neutre sans saisons ; mu et
division changent tous deux par rapport au résultat 13 ; tests non corrigés ; la mesure
« bouger » est le déplacement net (nord et sud allumés ensemble ne comptent pas).

## Lecture

Troisième essai de saisons, troisième résultat négatif, cette fois dans la configuration
voulue (cerveau sans étiquette, cinq moteurs, k = 2) et avec beaucoup de variété
(mu = 0,5). Avec un capteur d'un bit qui dit seulement « mon énergie a monté », un
cerveau de 3 nœuds ne trouve pas de réponse à l'hiver. Pistes inchangées : un capteur
plus riche (capteur gradué de nourriture : une case vide en hiver ne se distingue pas
aujourd'hui d'un repas disputé ou empoisonné), un cerveau de 4 ou 5 nœuds.

## Prolongation à 100 000 pas (écrit avant de lancer)

Quentin demande de faire durer la simulation plus longtemps. Mêmes régimes, mêmes graines
(les 200 premières années sont donc celles ci-dessus), 1 000 années au lieu de 200 :
`run.py --years 1000`. Une valeur par population : moyenne des 500 dernières années.

Hypothèses (Claude) :

1. La saison reste ignorée : économie d'hiver inférieure à 10 points. Réfutation :
   au moins 10 points et supérieure au neutre.
2. Les agents ne bougent pas moins en hiver (écart hiver − été ≥ −10 points).
3. Aucune PC lue sur les poids ni PTBN enrichie contre sans saisons et contre neutre.
4. La dépendance au capteur ne monte plus : moyenne des années 500 à 1 000 à moins de
   10 points de celle des années 100 à 200 (46,9). Je n'en suis pas sûr, elle montait
   encore dans d'autres expériences.

### Résultat de la prolongation

(à compléter)
