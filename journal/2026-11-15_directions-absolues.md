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

## Suites possibles

Un capteur de nourriture sur la case, normalisé sur 7 niveaux (0 à 6), puis des capteurs
par direction pour que l'agent puisse viser ; moteurs « avancer / tourner » avec un cap
dans le corps ; un rythme `k` mutable et coûteux.
