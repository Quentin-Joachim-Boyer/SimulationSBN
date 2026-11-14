# Milieu partagé : survivre ou mourir, sans cible (cerveau de 3 nœuds)

Écrit avant de lancer l'expérience ; la partie « Résultat » est remplie après.

## Pourquoi

Les expériences précédentes sélectionnaient sur la ressemblance à une cible (score du
moteur, trajectoire à simuler). Quentin propose une simulation de plus haut niveau : des
agents dans un milieu, qui survivent ou meurent, et qui modifient ce milieu. Leur
comportement agit donc sur les autres et sur eux-mêmes, mais seulement à travers lui.
Il n'y a plus ni cible, ni distance, ni formule de fitness.

## Question

Dans un milieu partagé, la sélection par la seule survie enrichit-elle les cerveaux en
nœuds de contrôle et en PSBN, et cela dépend-il de ce que le milieu varie ou non ?

## Protocole

Tous les paramètres ci-dessous sont fixés ici, avant le premier lancement.

- **Milieu** : bien mélangé (pas d'espace), deux ressources X et Y en stocks entiers,
  plafonnés à 1 000 unités chacun. Il reçoit 200 unités par pas.
  - régime **constant** : 100 unités de X et 100 de Y à chaque pas ;
  - régime **saisons** : 200 unités de X pendant 50 pas, puis 200 de Y pendant 50 pas.
- **Agent** : un capteur et un cerveau SBN de 3 nœuds (`Architecture(1, 3, 0)`).
  - nœud 0 du cerveau : action « ingérer X » ; nœud 1 : « ingérer Y » ; nœud 2 : caché ;
  - capteur « nourri » : vaut 1 si l'agent a obtenu au moins une unité au pas précédent.
    Le milieu l'impose à chaque pas ; le cerveau ne perçoit rien d'autre ;
  - 12 poids évoluent (3 capteur-cerveau, 9 cerveau-cerveau) dans [-3, 3].
- **Un pas** : le milieu reçoit son apport ; chaque agent dont un nœud d'action est allumé
  demande une unité de la ressource ; si le stock ne suffit pas, les servis sont tirés au
  sort ; le capteur est mis à jour, puis le cerveau calcule son état suivant.
- **Énergie** : +3 par unité obtenue, -1 par pas (entretien), -1 par nœud d'action allumé.
  Mort à 0 ou moins. À 20 ou plus, division : le parent et l'enfant gardent chacun la
  moitié, l'enfant hérite de l'état du cerveau et du capteur, et subit une mutation (un
  poids) avec la probabilité 0,1. Ingérer X et Y à la fois rapporte donc au mieux 0.
- **Départ** : 300 génotypes uniformes, états du cerveau au hasard, capteur à 1, énergie
  10, stocks pleins.
- **Durée** : 20 000 pas, 12 populations par régime, graine 0. Mesures tous les 100 pas,
  moyennées sur la seconde moitié.
- **Mesures**, sur les agents vivants :
  - effectif, extinctions, part des pas avec action X, Y, part des demandes servies ;
  - cerveau seul (matrice 3 × 3) : part de PSBN, part de nœuds de contrôle ;
  - dynamique complète avec le capteur : scission SBN (la face « capteur = 1 » est-elle
    un SBN) et contrôle interne (plus de 2 feuilles PTBN), comme dans l'expérience 1/3/1.
- **Modèles nuls** :
  - loi uniforme : exacte pour le cerveau seul (2,99 % de PSBN, 9,30 % avec nœud de
    contrôle), estimée sur 20 000 tirages pour les deux autres mesures ;
  - régime **neutre** : même démographie, mais les 200 unités sont tirées au sort entre
    les vivants et chacun paie une action, quel que soit son comportement. Il doit
    rester sur la loi uniforme ; sinon c'est la démographie qui biaise, pas la sélection.
- **Viabilité en solitaire** (calcul déterministe, 200 000 génotypes uniformes) : un
  agent seul, toujours servi quand il demande la ressource de la saison, survit-il à
  4 cycles de saisons depuis au moins un état de départ ? Donne la part de génotypes
  viables dans chaque régime et les mêmes mesures parmi eux, sans compétition.

## Hypothèses

1. **Régime constant** : les survivants sont des spécialistes dont le nœud d'action
   s'entretient seul. La part de cerveaux à nœud de contrôle dépasse le modèle nul.
   Réfutation : part inférieure ou égale à celle du régime neutre.
2. **Régime saisons** : une action figée y est mortelle (50 pas sans apport, contre 20 pas
   de réserve au plus). Si la population persiste, la part de nœuds de contrôle dans le
   cerveau seul est plus basse qu'en régime constant. Réfutation : part égale ou supérieure.
3. **Scission SBN** : dans les deux régimes, pas d'enrichissement au-dessus du modèle nul,
   comme dans les résultats 2 et 3. Réfutation : part nettement supérieure au régime neutre.
4. Sans prédiction : la persistance même en régime saisons. « Rester si nourri, changer
   sinon » est un multiplexeur, qu'un seul nœud à seuil ne calcule pas ; je ne sais pas si
   trois nœuds suffisent à une approximation viable. L'extinction serait un résultat.

« Nettement » : écart supérieur à deux écarts-types entre populations.

## Durée limite et critère d'abandon

Une séance. Pas de réglage des paramètres après coup : si le régime saisons s'éteint
dans la majorité des populations, c'est noté tel quel et les variantes vont dans les suites.

## Résultat

À remplir.
