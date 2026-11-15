# Quatre directions absolues : un cerveau qui doit retenir un cap

Écrit avant de lancer l'expérience ; « Résultat » est rempli après.

## Pourquoi

Quentin propose (15 novembre) d'augmenter le nombre de moteurs : un par direction. Avec
le moteur « bouger », qui envoie l'agent sur une case voisine au hasard, le comportement
tient en un bit (bouger ou rester). Quatre moteurs absolus (nord, sud, est, ouest) dont
les effets s'additionnent permettent de garder un cap.

Le point qui rend l'expérience intéressante pour la question de recherche : l'agent n'a
pas de cap dans son corps. Pour tenir une direction avec un capteur d'un seul bit, le
cerveau doit la porter dans son état. Cela demande de la mémoire interne, et un nœud de
contrôle (qui garde sa valeur) en est une forme naturelle. Ce monde pourrait donc favoriser
des parties contrôle (PC) internes, ce que les expériences précédentes n'ont jamais fait.
C'est une hypothèse de Claude, pas un résultat. (Des moteurs « avancer / tourner » avec un
cap dans le corps externaliseraient cette mémoire ; ils ne sont pas testés ici.)

## Ce qui change dans le code

- Nouvelle mesure **persistance** : cosinus entre deux déplacements successifs d'un même
  agent, compté quand il se déplace aux deux pas (effets additionnés, donc diagonales
  possibles ; nord et sud allumés ensemble s'annulent et ne comptent pas comme un
  déplacement). Une marche au hasard donne 0 en moyenne ; un cap constant donne 1.
  Testé sur un agent à direction constante.
- Pas d'autre changement du code du monde.

## Question

Quand l'agent peut choisir des directions absolues et que seul son cerveau peut retenir un
cap, l'évolution (1) produit-elle des déplacements persistants, (2) enrichit-elle les
parties contrôle internes ?

## Protocole

Monde à déchet 2D, paramètres, durée et nombre de populations **inchangés** (32 × 32,
division à 20, sans saisons, 20 000 pas, 300 agents au départ, mutation 0,1 par
naissance, graine 0, 24 populations par régime). Aucun nouveau calibrage.

Agent : capteur de bien-être (1 bit, comme avant), cerveau de 3 nœuds sans étiquette, cinq
moteurs lisant chacun les trois nœuds du cerveau (15 poids dans [-3, 3]) : « ingérer »,
« nord », « sud », « est », « ouest ». Lecture retardée, **k = 2** pas d'agent par pas du
milieu. Chaque moteur allumé coûte 1 d'énergie (règle existante) : un agent tiré au hasard
paie donc plus que dans le régime à deux moteurs.

Régimes :

- **directions** : le monde à déchet avec ces cinq moteurs ;
- **neutre** : même démographie, nourriture tirée au sort entre les vivants, mêmes cinq
  moteurs ; modèle nul de la structure et de la persistance (un moteur allumé en
  permanence donne déjà une persistance sans sélection).

Repère : le régime `k = 2` de `2026-11-15_rythme-agent.md` (deux moteurs, « bouger » au
hasard), non relancé ; comparé aux mêmes mesures pour la dépendance et la structure.

Mesures : celles de `rythme`, plus la persistance. Test : permutation des populations
(20 000 permutations, bilatéral), p < 0,01. Une valeur par population (moyenne de la
seconde moitié). Beaucoup de tests, non corrigés : limite assumée.

## Contrôle démographique permis

Une population de génotypes uniformes, 2 000 pas, régime directions : aucune extinction,
158 à 178 agents sur les 100 derniers pas (71 à 78 après 20 pas : le départ est coûteux).
Paramètres laissés tels quels.

## Hypothèses

1. **Persistance.** La persistance du régime directions est supérieure à celle du neutre
   (p < 0,01). Réfutation : pas de différence. Je n'en suis pas sûr : la sélection doit
   trouver un cerveau qui garde un cap en plus de survivre.
2. **Structure.** L'une au moins des PC lues sur les poids (1/2 ou 2/1) est enrichie par
   rapport au neutre (p < 0,01). Réfutation : aucune des deux. Je lui donne peu de
   chances (environ une sur quatre) : les trois expériences précédentes n'ont rien
   donné, et un cap peut aussi se retenir sans nœud de contrôle. Quentin s'attend plutôt
   à un résultat négatif avec trois nœuds.
3. **Sans prédiction** : dépendance au capteur, PTBN, PSBN, effectif ; et la comparaison
   avec le régime à deux moteurs.

## Durée limite et critère d'abandon

Une exécution. Si plus de la moitié des populations d'un régime s'éteignent, je rapporte
sans relancer.

## Résultat

`python experiments/directions/run.py`, graine 0, 24 populations par régime, 20 000 pas,
moyennes de la seconde moitié ± écart-type entre populations. Aucune extinction.

|                            | Directions    | Neutre        | Repère 2 moteurs (k = 2) |
|----------------------------|---------------|---------------|--------------------------|
| Effectif                   | 173           | 400           | 161                      |
| **Persistance**            | 0,68 ± 0,19   | 0,91 ± 0,06   |                          |
| Dépendance au capteur      | +18,3 ± 25,4  | -17,6 ± 17,4  | +45,4                    |
| P(bouger), capteur 0 / 1   | 98,8 / 80,5 % | 58,6 / 76,2 % |                          |
| 1/2 sur les poids          | 4,3 ± 12,2 %  | 3,1 ± 4,2 %   | 4,0 %                    |
| 2/1 sur les poids          | 1,7 ± 2,9 %   | 5,1 ± 8,0 %   | 4,1 %                    |
| PTBN (cerveau seul)        | 6,3 ± 16,6 %  | 10,0 ± 11,0 % | 13,9 %                   |

- **Hypothèse 1 : réfutée.** La persistance du régime directions (0,68) est **inférieure**
  à celle du neutre (0,91 ; p < 0,0001). Les cerveaux tirés au hasard gardent déjà un cap :
  un moteur allumé en permanence donne une direction constante. La sélection défait ce
  cap au lieu de l'installer : sur la figure, la persistance part de 0,93 et baisse
  régulièrement jusqu'à 0,63, et elle baisse encore à 20 000 pas.
- **Hypothèse 2 : réfutée.** Aucune PC lue sur les poids n'est enrichie : 1/2 4,3 % contre
  3,1 % (p = 0,84), 2/1 1,7 % contre 5,1 % (p = 0,036, sous le neutre, non retenu au
  seuil). Même constat que pour tous les mondes précédents. La mémoire d'un cap n'a donc
  pas produit de nœud de contrôle : l'évolution n'a pas gardé de cap.
- **Sans prédiction.** La dépendance au capteur est plus faible qu'avec deux moteurs
  (+18,3 contre +45,4, p = 0,0015), et elle monte encore à 20 000 pas (de −30 à +24).
  Les agents bougent presque toujours quand le capteur vaut 0 (98,8 %) et un peu moins
  quand il vaut 1 (80,5 %). La face « capteur = 1 » SBN est plus rare qu'au neutre
  (1,1 % contre 11,2 %, p < 0,0001), comme à k = 2 et 4 avec deux moteurs : des poids
  positifs du capteur vers le cerveau.

### Lecture

L'agent n'a pas de raison de tenir un cap dans ce monde : il ne perçoit rien de la
direction de la nourriture, et le déchet qui gêne se trouve sur sa propre case, qu'un
déplacement dans n'importe quelle direction suffit à quitter. Une marche qui change de
direction à chaque pas fait l'affaire. Les cinq moteurs lus par trois nœuds ne rendent pas
le cap rentable. Ce que ce monde rend utile, le capteur à un bit le donne déjà. Une
mesure plus riche de l'environnement (nourriture sur la case, par direction) serait
nécessaire pour qu'un cap serve à quelque chose ; c'est la prochaine étape prévue.

### Limites

- Une graine ; beaucoup de tests, non corrigés.
- La persistance se mesure seulement quand l'agent bouge aux deux pas. Elle ne dit rien de
  la qualité du cap (un cosinus de 0,68 peut cacher des virages réguliers).
- Dispersion entre populations grande (écart-type de 25 points sur la dépendance).
- Départ coûteux : cinq moteurs au hasard coûtent de l'énergie, l'effectif tombe à 71
  après 20 pas avant de remonter. Les mesures portent sur la seconde moitié.

## Suites possibles

Un capteur de nourriture sur la case, normalisé sur 7 niveaux (0 à 6), puis des capteurs
par direction pour que l'agent puisse viser ; moteurs « avancer / tourner » avec un cap
dans le corps ; un rythme `k` mutable et coûteux.
