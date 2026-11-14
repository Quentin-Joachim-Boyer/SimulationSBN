# Environnement alterné contre environnement fixe (dimension 3)

Écrit avant de lancer l'expérience ; la partie « Résultat » est remplie après.

## Question

Un environnement qui change de contexte enrichit-il les populations en réseaux
pluripotents, par rapport au modèle nul et par rapport à un environnement fixe ?

## Protocole

- Agent : SBN de dimension 3. Le nœud 0 reçoit le contexte, le nœud 1 un stimulus, le
  nœud 2 est le moteur. Le contexte n'est donné qu'à l'état initial : rien n'est
  maintenu de l'extérieur, c'est au réseau de s'en souvenir.
- Contexte A : départ en 010 (stimulus seul), le moteur doit être allumé aux pas 2 à 6.
- Contexte B : départ en 011 (stimulus et contexte), le moteur doit être éteint aux pas 2 à 6.
- Score d'un individu dans un contexte : part des pas où le moteur est correct.
  Fitness : exp(5 × score).
- Régime fixe : contexte A à chaque génération. Régime alterné : le contexte change
  toutes les 5 générations.
- 12 populations de 300 individus par régime, 600 générations, 0,1 mutation par
  individu, départ uniforme sur les matrices (donc au modèle nul).
- Mesures : part de PSBN (modèle nul : 2,99 %), part de dynamiques à nœud de contrôle
  (modèle nul : 9,30 %), score moyen dans chaque contexte. Moyennes sur la seconde moitié.
- En complément, un compte exact : parmi toutes les matrices parfaites dans les deux
  contextes, quelle part est pluripotente ?

## Hypothèse

Le régime alterné enrichit la population en PSBN, au-dessus du modèle nul et du régime
fixe, parce que se souvenir du contexte demande un nœud qui garde sa valeur.

Réfutée si la part de PSBN en régime alterné n'excède pas celle du régime fixe, ou si
les solutions parfaites se passent majoritairement de nœud de contrôle (le moteur peut
décider au premier pas puis s'entretenir seul).

## Durée limite

Une séance. Abandon si aucune population n'atteint un score moyen de 0,9 dans les deux
contextes.

## Résultat

Hypothèse réfutée pour moitié (`python experiments/alterne/run.py`, graine 0, moyennes
sur la seconde moitié des simulations).

|                              | PSBN   | Nœud de contrôle | Score A | Score B |
|------------------------------|--------|------------------|---------|---------|
| Modèle nul exact             | 2,99 % | 9,30 %           |         |         |
| Simulation, régime alterné   | 2,68 % | 9,09 %           | 0,95    | 0,96    |
| Simulation, régime fixe      | 0,90 % | 7,62 %           | 0,98    | 0,12    |
| Génotypes parfaits en A      | 0,71 % | 7,33 %           |         |         |
| Génotypes parfaits en A et B | 2,14 % | 9,47 %           |         |         |

Les deux dernières lignes sont des comptes exacts (405 808 génotypes parfaits en A,
dont 52 611 le sont aussi en B).

- La tâche est apprise : le régime alterné atteint 0,95 dans les deux contextes, le
  régime fixe ignore le contexte B.
- Le régime alterné porte trois fois plus de PSBN que le régime fixe, mais ne dépasse
  pas le modèle nul. Il n'y a donc pas d'enrichissement : c'est l'environnement fixe
  qui appauvrit.
- Le compte exact l'explique sans simulation : parmi les matrices parfaites dans les
  deux contextes, 2,14 % seulement sont des PSBN. La plupart des solutions se passent
  de nœud de contrôle, comme le prévoyait la clause de réfutation.

Limites : une seule tâche, une seule graine, dimension 3, pas de test statistique. Le
pic de PSBN des premières générations en régime alterné (moyenne vers 6 %) n'est pas
expliqué.

## Suites possibles

- Une tâche où le comportement demandé dans chaque contexte est lui-même une dynamique
  (un cycle dans l'un, un point fixe dans l'autre), plus proche de « simuler deux
  systèmes ».
- La dimension 4, où il y a assez de nœuds pour séparer mémoire du contexte et calcul.
- Une mesure graduée de pluripotence : la définition stricte ne voit pas les solutions
  qui gardent le contexte ailleurs que dans un nœud de contrôle.
