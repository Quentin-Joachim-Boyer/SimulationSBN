# Ressource et déchet toxique : monde bien mélangé contre monde en 2D

Écrit avant de lancer l'expérience ; « Calibrage » et « Résultat » sont remplis après.

## Pourquoi

Dans le milieu partagé à deux ressources (`2026-11-14_milieu-partage.md`), les agents
ingéraient tout en permanence et ignoraient leur capteur. Quentin choisit la variante
« une ressource et un déchet toxique produit par l'ingestion », où le contexte est
fabriqué par les agents eux-mêmes, et demande une simulation d'agents qui se déplacent
dans un milieu en 2D, plus visuelle et observable.

Les deux demandes sont réunies dans un seul modèle : un monde en grille, dont le cas
1 × 1 est le milieu bien mélangé. Mêmes agents, mêmes règles, seule la géométrie change.

## Question

1. Quand le contexte que perçoit l'agent est produit localement par les agents (cases
   vidées et polluées), la survie seule sélectionne-t-elle un comportement qui dépend du
   contexte ? Et pas quand le monde est bien mélangé ?
2. Si oui, cette dépendance fonctionnelle s'accompagne-t-elle d'une structure
   pluripotente (scission SBN, nœuds de contrôle) plus fréquente que sous le modèle nul ?

## Protocole

- **Monde** : grille torique de cases. Chaque case porte un stock de nourriture (entier,
  plafonné) et un stock de déchet (entier).
  - régime **espace** : 32 × 32 cases ;
  - régime **mélangé** : 1 × 1 case, avec le même apport total, la même capacité totale
    et le même seuil de toxicité total (les valeurs par case sont multipliées par 1 024).
- **Agent** : même génotype que dans l'expérience précédente, `Architecture(1, 3, 0)`,
  12 poids dans [-3, 3]. Les rôles changent :
  - nœud 0 du cerveau : action « ingérer » ; nœud 1 : action « se déplacer » ; nœud 2 : caché ;
  - capteur « bien-être » : vaut 1 si l'énergie de l'agent a augmenté au pas précédent.
    Il ne distingue pas la faim du poison. C'est un choix de Claude, à discuter : avec
    un capteur de toxine seul, un agent posé sur une case propre et vide n'a aucun
    signal pour partir.
- **Un pas**, dans cet ordre :
  1. la nourriture arrive (loi de Poisson, même espérance sur chaque case) ; chaque
     unité de déchet disparaît avec une probabilité fixe ;
  2. les agents dont le nœud de déplacement est allumé passent sur une des 4 cases
     voisines, tirée au sort (dans le monde 1 × 1, ils restent sur place et paient quand même) ;
  3. les agents dont le nœud d'ingestion est allumé absorbent le milieu de leur case :
     une unité de nourriture s'il en reste (tirage au sort entre demandeurs de la case),
     et le déchet présent, qui les empoisonne avec une probabilité proportionnelle au
     stock de déchet de la case. Chaque unité ingérée laisse une unité de déchet sur la case ;
  4. bilan d'énergie, mort à 0 ou moins, division au seuil (l'enfant naît sur la case du
     parent, avec la moitié de l'énergie, l'état du cerveau et du capteur du parent, et
     une mutation d'un poids avec la probabilité 0,1) ;
  5. le capteur est mis à jour, puis le cerveau calcule son état suivant.
- **Valeurs de départ des paramètres**, avant calibrage : apport 200 unités par pas ;
  plafond 5 unités de nourriture par case ; empoisonnement certain à 10 unités de déchet
  par case ; 5 % du déchet disparaît par pas ; +4 par unité ingérée ; -1 par pas, -1 par
  ingestion tentée, -1 par déplacement, -4 par empoisonnement ; division à 20.
- **Départ** : 300 génotypes uniformes placés au hasard, états du cerveau au hasard,
  capteur à 1, énergie 10, nourriture au plafond, aucun déchet.
- **Durée** : 20 000 pas, 24 populations par régime, graine 0. Mesures tous les 100 pas ;
  une valeur par population, moyennée sur la seconde moitié.
- **Mesures** :
  - démographie : effectif, naissances par pas, extinctions ;
  - comportement : part des pas avec ingestion et avec déplacement, selon que le capteur
    vaut 0 ou 1. **Dépendance au contexte** = P(déplacement | capteur 0) -
    P(déplacement | capteur 1) ;
  - structure : les quatre mesures de l'expérience précédente (nœud de contrôle et PSBN
    du cerveau seul, scission SBN, contrôle interne).
- **Modèles nuls** :
  - loi uniforme sur les génotypes, la même que dans l'expérience précédente ;
  - régime **neutre** : même énergie par unité et même seuil de division, mais la
    nourriture est tirée au sort entre les vivants, chacun paie un coût fixe, et ni la
    position ni le comportement n'ont d'effet. Les comparaisons se font avec ce régime,
    qui subit le même bruit d'échantillonnage que les deux autres.
- **Test** : par permutation des populations entre deux régimes, sur la différence des
  moyennes (20 000 permutations, bilatéral). Seuil : p < 0,01.

## Calibrage permis avant l'expérience

La première version s'est figée faute d'avoir été essayée. Cette fois, les paramètres du
monde peuvent être ajustés avant l'expérience, à trois conditions :

1. seulement avec des **agents construits à la main**, mutation coupée : un *immobile*
   (ingère toujours, ne bouge jamais), un *marcheur* (ingère et bouge toujours) et un
   *réactif* (ingère toujours, bouge quand le capteur vaut 0) ;
2. seulement sur des **critères démographiques** : la population persiste, se renouvelle
   (naissances à chaque centaine de pas), et en régime espace le réactif l'emporte sur
   les deux autres quand on les mélange. Sans ce dernier point, le monde ne récompense
   pas la sensibilité au contexte et la question 2 n'a pas d'objet ;
3. une population de génotypes uniformes peut être lancée 500 pas pour vérifier qu'elle
   ne s'éteint pas, en ne regardant que l'effectif.

Aucune mesure de structure n'est regardée sur une population évoluée avant que les
paramètres soient figés ci-dessous. Calibrer ainsi revient à construire un monde où la
sensibilité au contexte paie : l'hypothèse 1 en devient presque acquise en régime espace,
et ce sont les hypothèses 2 et 3 qui portent le risque.

## Hypothèses

1. **Comportement.** En régime espace, la dépendance au contexte est positive et
   supérieure à celle du régime neutre. En régime mélangé, elle ne diffère pas du régime
   neutre et le déplacement disparaît (il coûte sans rien rapporter).
   Réfutation : pas de différence significative entre espace et neutre.
2. **Scission SBN.** En régime espace, la part d'agents dont la face « capteur = 1 » est
   un SBN est supérieure à celle du régime neutre. Raison : ici le capteur sert surtout à
   inhiber (se sentir bien arrête le déplacement), et inhiber ne fait que relever des
   seuils, ce qui reste dans le cadre SBN. Ce serait le premier enrichissement observé.
   Réfutation : part inférieure ou égale à celle du régime neutre.
   En régime mélangé : pas d'enrichissement, comme dans l'expérience précédente.
3. **Nœud de contrôle du cerveau seul.** Supérieur au régime neutre dans les deux mondes :
   un SBN ne s'allume pas seul, donc l'ingestion doit s'entretenir elle-même, et un nœud
   qui s'entretient est souvent un nœud de contrôle. Réfutation : pas de différence
   significative avec le régime neutre.
4. Sans prédiction : PSBN du cerveau seul et contrôle interne.

## Durée limite et critère d'abandon

Une séance. Une fois les paramètres figés, plus aucun réglage ; une extinction ou un
résultat dégénéré est noté tel quel.

## Calibrage

`python experiments/monde_dechet/calibrage.py`, agents construits à la main, mutation
coupée. Sept jeux de paramètres essayés ; seuls l'effectif, les naissances, les parts
servies et empoisonnées et l'issue du mélange des trois types ont été regardés.

- **Valeurs de départ** : en régime espace le marcheur élimine le réactif (6 mélanges
  sur 6). La nourriture n'y est pas limitante (95 % des demandes servies) : c'est le
  poison qui limite la population, et rester sur place revient à manger dans son propre
  déchet. La sensibilité au contexte n'y paie pas.
- **Déplacement à 2 d'énergie** (trois essais) : les trois types s'éteignent en régime
  espace. Manger en se déplaçant donne alors un bilan nul, le capteur ne passe jamais à 1
  et le réactif ne s'arrête plus. Écarté.
- **Seuil de toxicité à 20, 30 ou 40** (déplacement à 1) : le réactif élimine les deux
  autres en régime espace, l'immobile gagne en régime mélangé, les populations se
  renouvellent. Plus le seuil est haut, moins le déchet compte (17 %, 12 %, 10 % des
  ingestions empoisonnées pour le réactif).

Je retiens le seuil à 20, le plus bas qui remplit les critères, donc celui où le déchet
pèse le plus. C'est le seul paramètre changé.

| Seuil 20, monoculture | Effectif | Naissances par pas | Demandes servies | Ingestions empoisonnées |
|---|---|---|---|---|
| Espace, immobile | 0 | | | |
| Espace, marcheur | 145 | 3,3 | 88 % | 14 % |
| Espace, réactif | 157 | 4,7 | 74 % | 17 % |
| Mélangé, immobile | 293 | 8,0 | 68 % | 18 % |
| Mélangé, marcheur | 214 | 3,4 | 93 % | 18 % |
| Mélangé, réactif | 262 | 7,8 | 76 % | 18 % |

Mélange des trois types (6 populations, 4 000 pas) : réactif 100 % en régime espace,
immobile 100 % en régime mélangé. Génotypes uniformes sur 500 pas : effectif entre 149 et
176 en régime espace, entre 286 et 311 en régime mélangé.

À noter pour la lecture des résultats : les effectifs diffèrent d'un régime à l'autre
(environ 150, 290 et 400 en neutre), donc la dérive aussi.

## Paramètres figés

Ceux du protocole, avec un seul changement : **empoisonnement certain à 20 unités de
déchet par case** (au lieu de 10). Figés avant le premier lancement de
`experiments/monde_dechet/run.py`.

Ajout décidé avant le lancement : dans les populations finales, la part d'agents dont
le poids capteur → déplacement est négatif, nul ou positif (de même pour l'ingestion),
pour voir si le mécanisme supposé par l'hypothèse 2 est le bon.

## Résultat

À remplir.
