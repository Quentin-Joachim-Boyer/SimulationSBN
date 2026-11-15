# Plusieurs pas d'agent par pas du milieu : le monde à déchet à lecture retardée

Écrit avant de lancer l'expérience ; « Contrôle démographique » et « Résultat » après.

## Pourquoi

Quentin n'aime pas la lecture directe, où deux nœuds du cerveau sont aussi les actions
(`2026-11-14_monde-dechet.md`). Ses raisons (15 novembre) :

1. les nœuds du cerveau ne doivent pas être étiquetés : ils sont lus par des nœuds
   moteurs, qui voient donc tout le cerveau ;
2. si les moteurs sont de vrais nœuds, la lecture ne peut pas être instantanée. Il
   préfère accepter le retard, quitte à laisser s'écouler plusieurs pas d'agent par pas
   du milieu.

Ce que cela ouvre plus tard (idée de Quentin) : faire de ce nombre de pas un trait de
l'agent, une sorte d'horloge biologique qui pourrait muter, avec l'idée qu'un rythme
rapide coûte nécessairement plus d'énergie. Ce n'est pas dans cette expérience : ici le
rythme `k` est le même pour tous et ne coûte rien de plus.

## Ce qui change dans le code

`Corps.ticks` (`k`) : le capteur est tenu pendant `k` pas d'agent ; le cerveau et les
moteurs se mettent à jour `k` fois ; l'action est lue sur les moteurs à la fin. Les
moteurs lisent les trois nœuds du cerveau (6 poids dans [-3, 3]), jamais le capteur. Avec
`k = 1`, le comportement est exactement celui du régime « retardé » de
`2026-11-15_moteurs-lecteurs.md` (testé : 102 tests). Les coûts d'énergie restent par
pas du milieu.

La dépendance au capteur est mesurée avec le capteur auquel l'action a pu réagir :
celui d'il y a deux pas pour `k = 1` (comme avant), le dernier connu pour `k ≥ 2`, où la
réaction tient dans un pas du milieu.

## Question

1. Avec `k = 2` ou `k = 4`, le comportement qui dépend du contexte, retrouvé en lecture
   directe (+51 points) puis réduit par le retard à `k = 1` (+22,6 ± 22,2), revient-il ?
2. Une partie contrôle (PC) interne apparaît-elle quand le cerveau n'a plus de nœud
   étiqueté ?

## Protocole

Monde à déchet 2D, paramètres et durée **inchangés** (32 × 32, division à 20, sans
saisons, 20 000 pas, 300 agents au départ, mutation 0,1 par naissance, graine 0,
24 populations par régime). Aucun nouveau calibrage.

Régimes, tous à moteurs « ingérer » et « bouger » lisant tout le cerveau, lecture
retardée :

- **k = 1** : repère, qui refait le régime « espace retardé » avec ce code ;
- **k = 2** : la réaction du capteur à l'action tient dans un pas du milieu ;
- **k = 4** : le cerveau a de la marge pour un nœud caché ou un cycle ;
- **neutre** (k = 2) : même démographie, nourriture tirée au sort entre les vivants ;
  modèle nul de la structure.

Mesures : celles de `moteurs_lecteurs`. Test : permutation des populations (20 000
permutations, bilatéral), seuil p < 0,01 ; beaucoup de tests non corrigés, limite
assumée. Une valeur par population (moyenne de la seconde moitié). Relevés tous les
100 pas.

Je ne reprends pas l'analyse du motif « allumé, oscille » : elle suppose un pas d'agent
par pas du milieu et n'a pas de sens direct pour `k > 1`.

Comparaisons : chaque régime contre le neutre ; `k = 2` et `k = 4` contre `k = 1` ;
`k = 4` contre `k = 2` ; et contre les populations en lecture directe de
`monde_dechet` si elles existent.

## Contrôle démographique permis

Une population de génotypes uniformes, `k = 4`, 2 000 pas, en ne regardant que
l'effectif. Si elle s'éteint, je le dis et je décide avec Quentin, sans régler.

## Contrôle démographique, fait

Une population de génotypes uniformes, `k = 4`, 2 000 pas : aucune extinction, 116 à 158
agents sur les 100 derniers pas. Paramètres laissés tels quels.

## Hypothèses

1. **Comportement.** La dépendance au capteur est plus forte à `k = 2` qu'à `k = 1`
   (p < 0,01), et à `k = 4` au moins aussi forte qu'à `k = 2`. Raison : la réaction
   tient dans un pas du milieu et l'information arrive à temps. Réfutation : `k = 2` pas
   supérieur à `k = 1`. Je n'en suis pas sûr : le résultat 7 a montré que l'évolution
   bascule entre deux états, et la sélection peut ne pas trancher.
2. **Structure.** Ni la 1/2 ni la 2/1 lues sur les poids ne sont enrichies par rapport
   au neutre, à aucun `k` ; c'est ce que j'attends, comme pour les expériences
   précédentes. Réfutation : l'une des deux supérieure au neutre avec p < 0,01.
3. **Sans prédiction** : PTBN, PSBN, scission, effectif, et la comparaison avec la
   lecture directe.

## Durée limite et critère d'abandon

Une exécution. Si plus de la moitié des populations d'un régime s'éteignent, je rapporte
sans relancer.

## Suites possibles

Un rythme `k` par agent, mutable, avec un coût d'énergie croissant ; les saisons dans
cette configuration ; un cerveau de 4 nœuds.
