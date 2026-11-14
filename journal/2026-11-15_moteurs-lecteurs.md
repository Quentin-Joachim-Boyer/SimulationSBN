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

## Résultat

À remplir.
