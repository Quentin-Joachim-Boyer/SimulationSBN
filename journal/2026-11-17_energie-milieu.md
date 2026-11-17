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

(à compléter après l'exécution)
