# Décompositions partie contrôle / partie opérative du cerveau

Écrit avant de relancer les expériences ; « Résultat » est rempli après.

## Pourquoi

Précision de Quentin (15 novembre) : « deux nœuds de contrôle, un nœud opératif » ne
désigne pas deux nœuds fixes, mais une **partie contrôle** (PC) de deux nœuds, un cerveau
dans le cerveau, et une **partie opérative** (PO). La PC peut avoir n'importe quelle
dynamique, cycles compris. Les arcs PC → PO sont libres, les arcs PO → PC interdits.
On mesure d'abord les décompositions possibles d'un cerveau de 3 nœuds, 1/2 et 2/1
(0/3 et 3/0 ne sont qu'un SBN quelconque). Plus tard : décompositions emboîtées, où
la PC ou la PO est elle-même de la forme PC/PO.

La classe « deux nœuds fixes » de `2026-11-15_classes-de-pluripotence.md` en est le cas
particulier où la PC est l'identité ; elle reste mesurée mais n'est plus la définition.

## Définitions

Sur le cerveau seul (capteur éteint), comme les autres mesures.

- **Arc** lu sur la dynamique, choix de Claude : le nœud j lit le nœud i si changer i
  change parfois la valeur suivante de j. Un poids non nul sans effet ne compte pas,
  comme pour les nœuds de contrôle.
- **1/2** : un nœud ne lit aucun des deux autres. Pour un SBN, il est alors soit un nœud
  de contrôle (il garde sa valeur), soit **mort** (toujours éteint après un pas).
  La 1/2 vivante est donc exactement le PTBN, déjà mesuré.
- **2/1** : deux nœuds ne lisent pas le troisième. **2/1 vivante** : la PC n'est pas
  constamment éteinte.

## Loi uniforme (calcul exact, poids dans [-3, 3])

| Décomposition | Part |
|---|---|
| 1/2, toutes | 51,764 % |
| 1/2 vivante (= PTBN) | 8,494 % |
| 1/2 seulement par un nœud mort | 43,270 % |
| 2/1, toutes | 28,850 % |
| 2/1 vivante | 22,688 % |
| 1/2 et 2/1 à la fois | 24,978 % |
| Au moins une des deux | 55,635 % |

## Protocole

Comme pour les classes de pluripotence : les deux expériences du monde à déchet et des
moteurs lecteurs relancées telles quelles, mêmes graines, trois mesures de plus
(1/2 toutes, 2/1 toutes, 2/1 vivante). Les anciennes lignes doivent ressortir
identiques. Test par permutation contre le régime neutre, seuil p < 0,01.

## Hypothèses

1. **2/1 vivante, régime mélangé (lecture directe)** : enrichie. Raison : l'ingestion y
   est un nœud de contrôle et le déplacement y est éteint ; s'il est mort, ces deux
   nœuds forment une PC vivante. Réfutation : p ≥ 0,01 ou part inférieure au neutre.
2. **1/2 toutes, régime espace (lecture directe)** : appauvrie. Raison : le déplacement y
   reste allumé quand le capteur vaut 0, il ne peut donc pas être mort, et moins de
   nœuds morts veut dire moins de 1/2. Réfutation : p ≥ 0,01 ou part supérieure au neutre.
3. Sans prédiction : 2/1 vivante en régime espace, et tous les régimes à moteurs lecteurs.

Réserve connue d'avance : un nœud que seul le capteur allume paraît mort quand on
regarde le cerveau à capteur éteint.

## Résultat

À remplir.
