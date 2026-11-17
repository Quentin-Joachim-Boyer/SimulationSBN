# Flux d'énergie du milieu : recyclage, conservation, diffusion, cadavres

Écrit avant de lancer l'expérience ; « Résultat » est rempli après.

## Pourquoi

Quentin (17 novembre) demande si l'on peut changer la façon dont l'énergie circule dans
le milieu, la simulation n'étant pas à énergie constante. Elle ne l'est pas : c'est un
système ouvert.

- **Entrée** : en été, environ 200 unités de nourriture par pas, tirées sur des cases au
  hasard ; une case garde 5 unités au plus, ce qui arrive sur une case pleine est perdu.
- **Circulation** : une unité mangée donne 4 d'énergie (`gain`) ; à la division, l'énergie
  est partagée entre parent et enfant (conservée).
- **Sorties** : l'entretien (1), chaque tentative d'ingérer (1), chaque moteur de direction
  allumé (1), le poison (4) quittent l'agent et disparaissent ; un agent meurt à énergie
  nulle et ne laisse rien. Le déchet ne porte pas d'énergie : c'est un poison, qui
  disparaît à 5 % par pas.

Claude a proposé quatre variantes ; Quentin les juge toutes pertinentes et demande de
développer sur des simulations courtes.

## Bilan d'énergie (ajouté au code)

`Vie.energie_totale()` = énergie des agents + 4 × nourriture des cases + réserve (la
réserve n'existe qu'avec la conservation). `Vie.bilan` cumule `entree` (énergie qui entre
dans le système : apport gardé, recyclage gardé, nourriture du neutre), `sortie` (énergie
qui en sort : dépenses, énergie d'un mort, restes et débordements) et `depense` (ce que les
agents ont payé, sorti ou rendu au milieu ; un mourant ne paie que ce qu'il a). Test :
pour chaque variante et pour le neutre, la variation de l'énergie totale à **chaque pas**
est exactement `entree − sortie` (`tests/test_energie.py`, 400 pas, 9 configurations dont
une qui combine conservation, diffusion et cadavres). Le monde par défaut tire les mêmes
nombres aléatoires qu'avant : la page « directions » rejoue toujours la population mesurée
à l'identique.

## Variantes (paramètres fixés par raisonnement)

Agent et monde témoin : ceux du régime « sans saisons » de
`2026-11-15_saisons-directions.md` (32 × 32, apport 200 par pas, plafond 5, toxicité 20,
disparition du déchet 5 %, division à 40 ; capteur de bien-être d'un bit, cerveau de
3 nœuds, cinq moteurs lecteurs retardés, k = 2), 300 génotypes uniformes au départ,
mutation 0,5 par naissance. Une seule chose change par régime :

- **témoin** : inchangé.
- **recyclage** (`recyclage = 0,5`) : la moitié du déchet qui disparaît redevient
  nourriture sur sa case (plafond 5, le surplus n'entre pas). Une case où l'on a mangé est
  toxique, puis redevient riche. Raison du 1/2 : avec un recyclage complet, le cycle
  nourriture → déchet → nourriture ne perdrait que les débordements et l'apport effectif
  pourrait être multiplié plusieurs fois ; avec 1/2, un repas rend au plus une demi-unité,
  qui en rend un quart, etc. : l'apport effectif est au plus doublé.
- **conservation** : rien n'entre de l'extérieur (l'apport est ignoré). Toute énergie
  perdue (dépenses, débordements) va dans une réserve, rendue au pas suivant en nourriture
  (une unité pour 4 d'énergie) sur des cases tirées au hasard ; ce qui tombe sur une case
  pleine retourne à la réserve. Énergie totale : celle du départ du témoin, 300 agents × 20
  + 1 024 cases × 5 unités × 4 = **26 480**, constante. Le retour remplace le soleil : on
  choisit seulement où et quand il arrive (ici, au hasard, comme l'apport du témoin ; le
  flux est égal à la dépense des agents).
- **diffusion** (`diffusion = 0,2`) : à chaque pas, chaque unité de nourriture part vers
  une des quatre cases voisines avec la probabilité 0,2 ; une unité qui irait sur une case
  pleine reste où elle est (la diffusion conserve exactement la nourriture). Raison : une
  unité qui attend une dizaine de pas fait environ deux sauts, les écarts de nourriture
  s'étalent sur quelques cases, l'échelle que verrait un capteur par direction.
- **accidents** (`accident = 0,005`) : chaque agent meurt avec la probabilité 0,005 par
  pas, quelle que soit son énergie, et son énergie est perdue. Raison : dans le témoin, il
  naît et meurt environ 1,8 agent par pas pour 175 agents (contrôle ci-dessous, 3 000 pas) ;
  0,005 × 175 ≈ 0,9 : les accidents feraient environ la moitié des morts. C'est le témoin
  des cadavres.
- **cadavres** : mêmes accidents ; l'énergie du mort devient nourriture sur sa case
  (une unité par 4 d'énergie, plafond 5 ; le reste d'une unité et le surplus sont perdus).
  Un agent mort de faim n'a plus d'énergie et ne laisse rien.
- **neutre** : inchangé (nourriture tirée au sort entre les vivants, mêmes moteurs, même
  mutation). C'est le nul de la dérive et de la structure, pour tous les régimes ; il n'est
  pas un nul propre du comportement (constat du résultat 14). Pour le comportement, chaque
  variante se compare au **témoin**. La loi uniforme exacte est aussi donnée.

## Développement et contrôle démographique (le seul permis)

Une population par régime, 3 000 pas, moyenne de la seconde moitié : aucune extinction ;
effectif 175 (témoin), 210 (recyclage), 244 (conservation), 146 (accidents), 140
(cadavres), 399 (neutre). Énergie totale de la conservation : 26 480 à tous les relevés.

**Défaut trouvé et corrigé pendant ce contrôle** : la première diffusion écrêtait au
plafond la nourriture arrivée sur une case pleine, ce qui la détruisait. Il entrait 647
d'énergie par pas, les agents n'en dépensaient que 356 : la diffusion était aussi une
perte, ce qui n'est pas son intention. Corrigée (une unité bloquée reste sur sa case,
test ajouté) : 176 agents, entrée 600 et dépense 602 par pas.

## Protocole

24 populations par régime, 20 000 pas (la durée de référence des résultats précédents ;
pas de prolongation), graine 0, relevés par fenêtres de 100 pas, une valeur par population
(moyenne de la seconde moitié). Mesures : effectif, nourriture et déchet par case, énergie
entrée et dépensée par pas, énergie totale, naissances, morts, accidents, ingestion et
déplacement selon le capteur, dépendance au capteur, persistance, empoisonnement, PC de
1 et de 2 nœuds lues sur les poids, PTBN, PSBN. Tests par permutation (20 000, bilatéral,
p < 0,01) : chaque variante contre le témoin (comportement et structure), chaque régime
contre le neutre (structure). Beaucoup de tests, non corrigés.

## Hypothèses (Claude)

1. **Bilan.** Aucune extinction ; l'énergie totale de la conservation vaut 26 480 à tous
   les relevés des 24 populations. Sinon le code est faux.
2. **Recyclage : le comportement change.** La nourriture revient là où l'on a mangé, une
   vingtaine de pas plus tard en moyenne : rester dans la zone ou y revenir paie davantage
   qu'aller tout droit. Je prédis une persistance plus basse que dans le témoin
   (p < 0,01) ; peu confiant sur le sens, je rapporte toute différence de comportement.
   Réfutation : persistance et dépendance indistinguables du témoin.
3. **Conservation : seule la démographie change.** Le retour tombe au hasard, comme
   l'apport du témoin ; seul le flux diffère. Dépendance et persistance indistinguables du
   témoin (p ≥ 0,01). Réfutation : une différence de comportement à p < 0,01.
4. **Diffusion : pas d'effet sur le comportement.** Le capteur d'un bit ne perçoit pas les
   gradients. Dépendance et persistance indistinguables du témoin (p ≥ 0,01). Elle
   prépare le capteur gradué ; un effet ici serait inattendu.
5. **Cadavres contre accidents : pas d'effet.** Environ 0,7 accident par pas ; un mort de
   20 d'énergie laisse 5 unités (9 au plus, plafond 5 par case) : environ 3,5 unités par
   pas, contre 200 d'apport, moins de 2 % de la nourriture.
   Résultat négatif attendu ; la variante est gardée parce qu'elle a été demandée, et
   pour la mesurer.
6. **Structure : aucune PC ni PTBN enrichie**, dans aucune variante, ni contre le neutre
   ni contre le témoin. Réfutation : un enrichissement à p < 0,01 contre les deux. Dans
   le témoin à 20 000 pas, l'appauvrissement vu à 100 000 pas peut ne pas être encore net.

## Résultat

Exécuté le 17 novembre (`experiments/energie/run.py`, graine 0, 24 populations par
régime, 20 000 pas, 16 minutes ; aucune extinction). Moyenne ± écart-type entre
populations, seconde moitié. Figure : `experiments/energie/out/energie.png`.

| mesure | témoin | recyclage | conservation | diffusion | accidents | cadavres | neutre |
|---|---|---|---|---|---|---|---|
| effectif | 183 ± 5 | 253 ± 4 | 349 ± 7 | 201 ± 6 | 158 ± 6 | 162 ± 6 | 400 |
| nourriture par case | 2,72 | 3,07 | 3,93 | 2,66 | 3,09 | 3,07 | 5 |
| déchet par case | 2,86 | 4,12 | 6,25 | 3,22 | 2,53 | 2,60 | 0 |
| énergie dépensée par pas | 585 | 844 | 1 279 | 660 | 501 | 514 | 800 |
| empoisonnés (% des repas tentés) | 13,9 | 21,9 | 32,2 | 17,3 | 13,5 | 14,3 | 0 |
| bouger, capteur à 0 / à 1 (%) | 95 / 52 | 95 / 24 | 94 / 9 | 94 / 46 | 94 / 52 | 94 / 47 | 60 / 77 |
| dépendance au capteur (points) | 43 ± 31 | 72 ± 19 | 85 ± 15 | 49 ± 16 | 42 ± 27 | 48 ± 20 | −17 |
| persistance | 0,64 ± 0,21 | 0,56 ± 0,08 | 0,48 ± 0,10 | 0,61 ± 0,11 | 0,64 ± 0,14 | 0,64 ± 0,11 | 0,90 |
| PC de 1 nœud, poids (%) | 4,2 | 3,2 | 5,9 | 2,5 | 2,7 | 1,7 | 6,4 |
| PC de 2 nœuds, poids (%) | 2,9 | 5,9 | 3,0 | 4,3 | 3,4 | 1,4 | 4,8 |
| PTBN (%) | 9,7 | 6,4 | 6,9 | 6,4 | 7,8 | 3,9 | 8,9 |

Tests contre le témoin (p bilatéral) : recyclage, déplacement à capteur 1 p = 0,0005,
dépendance p = 0,0006, persistance p = 0,105 ; conservation, déplacement à capteur 1 et
dépendance p < 0,0001, persistance p = 0,0018 ; diffusion, accidents, cadavres :
p ≥ 0,29 sur tout le comportement ; structure : p ≥ 0,08 pour toutes les variantes.
L'effectif diffère du témoin dans toutes (p < 0,0001).

1. **Bilan : tenu.** Aucune extinction ; l'énergie totale de la conservation vaut 26 480
   aux 4 800 relevés (24 populations × 200 fenêtres).
2. **Recyclage : le comportement change, mais pas comme prévu.** La persistance baisse un
   peu (0,56 contre 0,64) sans être significative (p = 0,105) : la prédiction écrite n'est
   pas confirmée. Ce qui change, c'est que les agents nourris restent : ils ne bougent plus
   que 24 % du temps quand le capteur vaut 1, contre 52 % (p = 0,0005), et la dépendance
   monte à 72 points (p = 0,0006). La clause de réfutation n'est pas remplie.
3. **Conservation : hypothèse réfutée.** J'avais prédit que seule la démographie
   changerait. Le comportement change le plus de toutes les variantes : agents nourris
   immobiles à 91 % (9 % de déplacement à capteur 1), dépendance 85 points, persistance
   0,48 (p < 0,0001 ; 0,0018). Mon raisonnement oubliait que, sans perte au plafond, le
   flux de nourriture est bien plus fort : il arrive environ 320 unités par pas (la
   dépense, 1 279, divisée par 4) contre environ 146 gardées dans le témoin, et les cases
   restent plus pleines (3,9 contre 2,7).
4. **Diffusion : tenue.** Aucune différence de comportement (p ≥ 0,40) ; seul l'effectif
   monte un peu (201 contre 183).
5. **Cadavres contre accidents : tenue (résultat négatif).** Test calculé après coup, comme
   prévu par l'hypothèse : effectif 162 contre 158 (p = 0,019), comportement et structure
   indistincts (p ≥ 0,12). Les accidents seuls ne changent rien non plus au comportement
   du témoin (p ≥ 0,38).
6. **Structure : tenue, aucune PC ni PTBN enrichie.** Contre le témoin, p ≥ 0,08 partout.
   Contre le neutre, les seules différences à p < 0,01 sont des **appauvrissements**, tous
   dans le régime cadavres : PC de 1 nœud 1,7 % contre 6,4 % (p < 0,0001), PC de 2 nœuds
   1,4 % contre 4,8 % (p = 0,0001), PTBN 3,9 % contre 8,9 % (p = 0,0075). Comme les
   cadavres ne se distinguent pas des accidents (p ≥ 0,12), je ne l'attribue pas aux
   cadavres. Le témoin ne se distingue pas encore du neutre à 20 000 pas (p ≥ 0,22),
   comme anticipé.

Sans prédiction, lecture après coup (non testée, 6 régimes seulement) : la dépendance au
capteur suit la richesse du monde. Classés par nourriture par case et énergie dépensée par
pas, les régimes vont du témoin, des accidents et de la diffusion (dépendance 42 à 49) au
recyclage (72) puis à la conservation (85). Une lecture possible : quand les cases restent
riches, rester sur place tant qu'on mange paie, malgré un empoisonnement plus fréquent
(22 % et 32 % des repas). Ce que les variantes changent d'abord, c'est donc la quantité de
nourriture, pas sa disposition. Pour séparer les deux, il faudrait comparer chaque
variante à un témoin d'apport égal.

## Limites

Une graine ; la dépendance monte encore en seconde moitié dans tous les régimes sélectifs
(de 3 à 14 points par 10 000 pas) ; les variantes changent le flux de nourriture en même
temps que sa disposition (voir ci-dessus) ; un seul neutre pour toutes les variantes ;
dispersion énorme de la structure entre populations ; beaucoup de tests non corrigés ;
l'hypothèse 5 a été testée par un calcul ajouté après l'exécution (prévu dans
l'hypothèse, absent du script).
