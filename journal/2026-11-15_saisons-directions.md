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

(à compléter après l'exécution)
