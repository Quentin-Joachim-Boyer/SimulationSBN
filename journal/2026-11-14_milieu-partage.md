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
  - loi uniforme : exacte pour le cerveau seul, estimée sur 20 000 tirages pour les deux
    autres mesures. Correction faite avant le premier lancement : les 2,99 % de PSBN et
    9,30 % de nœuds de contrôle connus valent pour des poids dans [-2, 2] ; ici les
    poids sont dans [-3, 3], et le script recalcule les valeurs exactes ;
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

`python experiments/milieu_partage/run.py`, graine 0, 12 populations par régime, moyennes
sur la seconde moitié, ± écart-type entre populations.

|                              | Contrôle (cerveau) | PSBN (cerveau) | Scission SBN | Contrôle interne | Effectif |
|------------------------------|--------------------|----------------|--------------|------------------|----------|
| Loi uniforme                 | 8,49 % (exact)     | 2,49 % (exact) | 11,96 %      | 9,75 %           |          |
| Viables seuls, constant (76 % des génotypes) | 9,50 % | 2,54 %     | 7,60 %       | 11,11 %          |          |
| Viables seuls, saisons (20 % des génotypes)  | 11,67 % | 2,01 %    | 3,21 %       | 14,11 %          |          |
| Simulation, régime neutre    | 5,9 ± 3,6 %        | 1,8 ± 2,4 %    | 7,6 ± 7,5 %  | 6,6 ± 3,7 %      | 300      |
| Simulation, régime constant  | 12,2 ± 15,4 %      | 1,5 ± 4,0 %    | 4,6 ± 10,2 % | 15,4 ± 17,3 %    | 202      |
| Simulation, régime saisons   | 13,1 ± 9,1 %       | 0,8 ± 1,8 %    | 4,5 ± 5,6 %  | 15,0 ± 9,9 %     | 200      |

Aucune extinction (0 sur 12 dans chaque régime).

**Le résultat principal n'était pas prévu : dans les deux régimes, les survivants
ingèrent X et Y à tous les pas** (actions allumées plus de 99,5 % du temps, 50 % des
demandes servies). Le capteur ne sert à rien et aucun comportement ne dépend du contexte.

- J'avais écrit que tout ingérer « rapporte au mieux 0 », en y voyant un handicap. C'est
  une erreur de raisonnement : un bilan nul est exactement la condition d'équilibre. Les
  agents qui demandent tout font baisser les stocks jusqu'au point où ils se maintiennent
  tout juste (une demande sur deux servie), et où un spécialiste, qui a besoin de deux
  demandes servies sur trois, meurt de faim. C'est la règle classique d'exclusion par
  celui qui tolère la ressource la plus rare.
- **Hypothèse 1 : non confirmée.** 12 % de cerveaux à nœud de contrôle en régime
  constant contre 6 % en régime neutre, mais l'écart-type entre populations est de 15
  points. Et le mécanisme supposé (des spécialistes) est faux.
- **Hypothèse 2 : réfutée.** La part n'est pas plus basse en régime saisons (13 % contre
  12 %), puisque la stratégie est la même dans les deux régimes.
- **Hypothèse 3 : confirmée.** Aucun enrichissement en scission SBN (4,6 % et 4,5 %,
  contre 7,6 % en régime neutre et 12 % sous la loi uniforme).
- **Point 4** : la population persiste, mais sans résoudre le problème posé : elle le
  contourne.

**Défaut du protocole, régime saisons.** Après un goulot (23 agents en moyenne au pas
100), la population se fige : 200 agents, 200 unités par pas, chacun servi à chaque pas,
bilan exactement nul. Plus aucune mort ni naissance après le pas 400 au plus tard. Les
chiffres de ce régime décrivent donc les survivants d'un tri initial, pas le produit
d'une évolution. En régime constant, le tirage au sort des servis entretient le
renouvellement.

**Régime neutre.** Il oscille lentement autour de la loi uniforme, et sa moyenne sur la
seconde moitié est en dessous pour trois mesures (de 2 à 3 erreurs standard). En théorie
il n'a aucun biais (démographie indépendante du génotype, mutation symétrique) ; la
dérive est lente et 12 populations ne suffisent pas à trancher. À vérifier avec plus de
populations avant de s'en servir comme référence fine.

**Viabilité en solitaire.** 76 % des génotypes uniformes sont viables seuls en régime
constant et 20 % en régime saisons : survivre sans compétition est facile, ce qui
explique qu'aucune population ne s'éteigne. Parmi les viables en saisons, la scission
SBN tombe à 3,2 % (loi uniforme : 12 %) : comme dans l'expérience 1/3/1, le capteur
sert de source d'activation.

Limites : une graine, un seul jeu de paramètres, pas de test statistique ; mesures très
dispersées entre populations, dominées par quelques lignées.

## Suites possibles

Aucune n'a été essayée : le protocole interdisait de régler les paramètres après coup.

- Rendre les deux actions incompatibles (un agent qui demande X et Y n'obtient rien),
  ou les faire coûter plus cher ensemble. C'est une règle du milieu de plus, à assumer.
- Dépense aléatoire ou mortalité de fond, pour qu'une population ne puisse pas se figer.
- Une ressource et un déchet toxique produit par l'ingestion, au lieu de deux ressources :
  le contexte serait alors fabriqué par les agents eux-mêmes.
- Davantage de populations, et un régime neutre plus long, pour réduire la dispersion.
