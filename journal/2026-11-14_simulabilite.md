# Table de simulabilité : un cerveau de dimension 3 peut-il simuler deux cibles ?

Écrit avant le calcul ; la partie « Résultat » est remplie après.

## Question

La pluripotence fonctionnelle (se comporter comme une cible A ou une cible B selon le
contexte) entraîne-t-elle la pluripotence structurelle ? Calcul exhaustif, sans
simulation évolutive.

## Définitions

- Réseau composite de dimension 4 : un nœud d'environnement `e`, maintenu (boucle seule),
  et un cerveau de 3 nœuds. Les 12 poids (3 de couplage, 9 du cerveau) sont dans [-3, 3].
  Contexte A : `e = 0`, le cerveau est un SBN. Contexte B : `e = 1`, le couplage ajoute
  un biais constant, le cerveau est un TBN.
- Les nœuds 1 et 2 du cerveau sont visibles, le nœud 3 est caché.
- Cible : une dynamique sur 2 nœuds. Le cerveau **simule** la cible T dans un contexte
  si, depuis chacun des 4 états visibles (nœud caché éteint), les nœuds visibles
  suivent pour toujours la trajectoire de T. Le nœud caché est libre : il peut servir
  de mémoire ou de relais.
- Un composite simule donc au plus une paire (T_A, T_B) ; sinon il est dit incohérent
  (le nœud caché fait dévier les nœuds visibles d'une règle fixe).
- Mesures structurelles sur les solutions :
  - PSBN : le cerveau du contexte B est encore un SBN ;
  - strict : dans les deux contextes, les nœuds visibles ne dépendent pas du nœud caché
    (la cible se lit directement comme sous-réseau).
- Tout est pondéré par le nombre de génotypes, grâce à l'indépendance des colonnes.

## Prédictions

1. La plupart des 36 × 36 paires de cibles SBN sont simulables.
2. Les solutions PSBN sont minoritaires, et certaines paires ne sont simulables que
   hors du cadre PSBN : ce serait de la pluripotence fonctionnelle sans la structurelle.

## Résultat

Les deux prédictions sont réfutées (`python experiments/simulabilite/run.py`, calcul
exact sur les 7^12 ≈ 1,38e10 génotypes composites, en 5 secondes).

| Génotypes composites                         | Part    |
|----------------------------------------------|---------|
| Incohérents (pas de règle fixe)              | 54,91 % |
| Simulent une paire dont la cible B n'est pas un SBN | 31,47 % |
| Simulent une paire de cibles SBN             | 13,62 % |

1. Seules 225 des 1 296 paires de cibles SBN sont simulables (189 des 1 260 paires où
   A ≠ B). La prédiction « la plupart » est fausse.
2. Aucune paire simulable n'est privée de solution PSBN, et les PSBN font 52 % des
   solutions (44 % quand A ≠ B). Les solutions strictes, où le nœud caché est ignoré,
   en font 23 % (15 % quand A ≠ B). À cette taille, la pluripotence fonctionnelle ne va
   donc jamais sans la structurelle.

Ce que le calcul montre en plus :

- La simulabilité se factorise par nœud visible : 225 = 15², chaque nœud ayant 15
  paires (fonction en A, fonction en B) permises sur 36. Ce sont celles où la fonction
  en B s'obtient en relevant le seuil de la fonction en A. Entre cibles SBN, le
  contexte ne peut donc qu'éteindre : a∨b peut devenir a, b ou 0, jamais l'inverse.
- Toutes cibles B confondues (TBN compris), il y a 1 024 = 32² paires simulables, soit
  32 paires par nœud visible. Ce sont exactement les 32 SBF de dimension 3 lues comme
  paires, le contexte étant la troisième entrée. Le nœud caché n'ajoute donc aucune
  paire : il change le nombre de solutions, pas ce qui est simulable.

Limites : cerveau de dimension 3 avec 2 nœuds visibles, un seul nœud d'environnement
maintenu, cibles de dimension 2. La définition de « simuler » exige une règle fixe
depuis un nœud caché éteint ; une définition plus lâche (sur les attracteurs
seulement) donnerait peut-être un rôle au nœud caché.

## Suites possibles

- Deux nœuds cachés, ou comparaison sur les attracteurs : le nœud caché devient-il utile ?
- Environnement en cycle (deux nœuds), où le biais varie dans le temps.
- Simulation évolutive sur quelques paires choisies dans la table : une paire à
  nombreuses solutions, une paire rare, et la part de PSBN obtenue contre les 44 % attendus.
