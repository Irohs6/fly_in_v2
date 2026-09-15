# Audit de conformité au sujet PDF — 14 septembre 2026

## Référence et portée

Référence : PDF anglais `en.subject.pdf`, version 1.6, fourni par l’utilisateur, transcrit dans [subject.md](subject.md). Empreinte SHA-256 du PDF : `5609bfe3058fc2db9abd7460281f70eec19500f3283a86ab480599cf70a9e9f2`. Les anciennes transcriptions ne servent plus de référence. Les pages indiquées ci-dessous sont les numéros imprimés du PDF.

Relecture de tous les fichiers Python de `src/`, de `main.py`, du README, du Makefile, de la configuration et des tests utiles à chaque exigence. Exécution de la suite existante, du lint, du typage strict, des 11 cartes présentes et de cas ciblés temporaires. Cet audit ne modifie ni le code applicatif ni les cartes dans `assets/maps` ; il ajoute ce rapport et une carte de reproduction dans `docs/audit_cases`.

**Conclusion : le projet possède les composants obligatoires et passe ses tests courants, mais je ne le qualifierais pas encore de complètement conforme.** Les corrections prioritaires sont détaillées ci-dessous. Des tests réussis ne prouvent pas la conformité sur toutes les cartes d’évaluation.

## Résultats des vérifications

| Vérification | Résultat |
|---|---|
| Suite existante | **166 tests réussis** |
| `make lint` | Réussi : flake8 et mypy avec les options obligatoires |
| `poetry run mypy . --strict --exclude .venv` | Un échec dans un test, décrit plus bas ; strict est optionnel |
| 11 cartes actuellement présentes | Toutes terminent |
| Carte valide avec 201 drones | Rejetée par le plafond applicatif |
| Première ligne `drones: 1` ou `nb_drone: 1` | Acceptée, alors que le sujet demande `nb_drones` |
| Carte sans déclaration d’arrivée | Erreur claire, mais sans numéro de ligne ni position de fin de fichier |
| Pilote vidéo indisponible | Exception Pygame non interceptée et traceback |
| Nettoyage après échec d’ouverture graphique | `pygame.quit()` non appelé |
| Ordonnancement sur un graphe temporaire | Attente évitable reproduite au tour 7 avec six drones |
| Recherche complémentaire de blocages | 2 000 candidats aléatoires déterministes, cartes invalides écartées, au plus 150 tours par carte ; aucun blocage stationnaire détecté par ce contrôle. Ce n’est pas une preuve générale |

## Écarts confirmés et corrections proposées

### 1. Priorité haute — plafond obligatoire de 200 drones

**Exigence :** VII.4, page 13 : le programme doit gérer n’importe quel nombre de drones.

**Code :** [validator.py](../src/parser/validator.py:14), contrôle dans `_validate_nb_drones()` autour de la ligne 61 ; README lignes 174–176.

Une carte valide contenant `nb_drones: 201` échoue avant simulation avec :

```text
nb_drones: 201 drones requested, allowed limit: 200.
```

Cette limite avait été demandée pour les performances, mais elle contredit explicitement le sujet. **Correction proposée : retirer le rejet inconditionnel.** Une limite volontaire d’exécution peut être une option utilisateur, pas une restriction du format obligatoire. Adapter également le README et les tests qui exigent actuellement ce rejet.

### 2. Corrigé — erreurs graphiques non gérées

**Mise à jour après correction :** `PygameView.display()` intercepte uniquement les erreurs Pygame attendues et les convertit en `DisplayError`, une exception indépendante de Pygame que `main()` affiche proprement. Un `finally` garantit `pygame.quit()` à la fermeture normale, à l’échec d’initialisation ou de rendu, et à l’interruption. Les exceptions inattendues restent propagées après nettoyage. Le mode terminal n’importe toujours pas Pygame.

Validation : **178 tests réussis**, `make lint` réussi. Douze nouveaux cas couvrent trois points d’échec, les exceptions attendues et inattendues, l’interruption, la fermeture normale et les deux modes avec pilote vidéo indisponible. Le constat ci-dessous décrit l’état avant correction.


**Exigence :** III.1, page 5 : éviter les crashes dus aux exceptions non gérées et nettoyer les ressources.

**Code :** [main.py](../main.py:23), [pygame_view.py](../src/view/pygame_view.py:34) et fin de `display()` ligne 158.

Le point d’entrée intercepte `OSError` et `ParseError`, mais pas `pygame.error`. Une carte valide avec un pilote vidéo indisponible termine avec un traceback. Reproduction sur une carte temporaire valide, via un sous-processus ayant `SDL_VIDEODRIVER=flyin_nonexistent_driver` : code de sortie 1, traceback présent, erreur Pygame confirmée. Ce problème peut aussi survenir lors d’un échec réel d’initialisation de l’affichage.

Un second contrôle, simulant uniquement l’échec de `pygame.display.set_mode()`, confirme que `pygame.quit()` n’est pas appelé.

**Correction proposée :** intercepter les erreurs attendues dans la couche graphique, retourner un message propre au point d’entrée et garantir `pygame.quit()` par `finally`. Ne pas importer Pygame dans le mode terminal uniquement pour pouvoir intercepter son exception. Ne pas masquer indistinctement toutes les exceptions internes.

### 3. Priorité moyenne — le parser accepte des en-têtes hors du format demandé

**Exigence :** VII.4, page 13 : première ligne `nb_drones: <positive_integer>`.

**Code :** [parser.py](../src/parser/parser.py:328) et branche de traitement autour de la ligne 344.

Les alias `drones` et `nb_drone` sont acceptés. Deux cartes temporaires ont confirmé cette acceptation. Le test existant sur les mots-clés ne couvre pas ces deux variantes.

**Correction proposée :** accepter uniquement `nb_drones` pour le format du sujet, ou isoler explicitement une extension de compatibilité si elle est réellement voulue. Pour une évaluation stricte, les fautes de mot-clé doivent être rejetées.

Les noms internes `Hub.capacity` et `Connection.capacity` ne sont, eux, **pas un défaut** : la correspondance depuis `max_drones` et `max_link_capacity` fonctionne. L’alias externe `capacity` est une extension de compatibilité, pas le nom officiel du PDF ; son statut doit être clairement documenté.

### 4. Priorité moyenne — un drone peut manquer une place libérée dans le même tour

**Exigences :** VII.1 et VII.3, pages 11–13 : éviter les délais inutiles et prendre en compte les places libérées par les départs du tour courant.

**Code :** boucle de [simulation.py](../src/model/simulation.py:238), `_try_drone_move()` et son retour après `drone.wait()`.

Le moteur traite les drones une seule fois, dans l’ordre de leur estimation de chemin restant. Cet ordre n’assure pas toujours que le drone qui libère une zone passe avant celui qui veut y entrer. Le drone en attente n’est pas réexaminé après un départ plus tardif.

**Preuve :** [same_turn_release.txt](audit_cases/same_turn_release.txt), carte valide de six drones qui passe le parser et le BFS. Au début du tour 7 :

| Drone | Position | Chemin restant | Traitement au tour 7 |
|---|---|---|---|
| D5 | h2 | h8, end | Commence son transit vers h8 et libère h2 |
| D6 | h5 | h7, h4, end | Attend car h7 est encore occupé |
| D4 | h7 | h2, h8, end | Commence son transit vers h2 et libère h7 |

En fin de tour, h7 est libre et la connexion h5–h7 a encore de la capacité, mais D6 n’a pas bougé. Un ordre D5, D4, D6 permettrait ces trois mouvements dans le même tour. Les drones déjà livrés sont omis du tableau.

**Correction proposée :** planifier les départs et arrivées du tour, ou réexaminer les drones en attente après les départs, en garantissant au plus un déplacement par drone et sans faire avancer deux fois un transit. Un simple tri supplémentaire ne suffit pas à démontrer la correction générale.

Ce cas établit un délai évitable, **pas une collision ni un blocage infini**. Aucun dépassement de capacité n’a été observé sur ce cas.

### 5. Priorité moyenne — erreurs de déclaration manquante sans localisation

**Exigence :** VII.4, page 13 : une erreur de parsing indique la ligne et la cause.

**Code :** [parser.py](../src/parser/parser.py:280), contrôles des déclarations obligatoires après lecture.

Une carte privée de `end_hub` produit seulement `missing end_hub.`. Le comportement reste le même avec des commentaires et lignes blanches en tête. Le programme ne plante pas, mais la localisation demandée manque.

**Correction proposée :** indiquer la fin du fichier et une ligne physique appropriée pour une déclaration absente. Conserver les numéros réels pour toutes les autres erreurs ; ne pas inventer systématiquement « Line 1 ».

### 6. README — sections présentes, contenu à mettre à jour

Le chapitre VIII, page 20, exige la première ligne en italique, Description, Instructions, Resources, les choix algorithmiques, l’usage de l’IA, la visualisation et un exemple entrée/sortie.

| Exigence | État réel |
|---|---|
| Première ligne en italique avec le login | Présente et conforme dans sa forme |
| Description | Présente |
| Instructions d’installation et d’exécution | Présentes |
| Resources et références | Présentes |
| Choix algorithmiques et stratégie | Présents ; expliquer aussi les limites de l’ordonnancement et de la mémoire serait utile |
| Fonctionnalités de visualisation | Présentes : contrôles, occupations et transits |
| Exemple d’entrée et sortie attendue | Présent |
| README anglais | Oui |
| Usage de l’IA | Section présente, mais devenue incomplète et périmée |

Corrections concrètes :

- **Ligne 119 :** `controller.run(gui=False)` ne correspond plus à la signature actuelle, qui utilise `is_view=False`. L’exemple doit être exécutable.
- **Lignes 165, 169 et 184 :** présenter `max_drones` pour les hubs et `max_link_capacity` pour les connexions comme dans le PDF. Expliquer séparément l’éventuel alias `capacity`.
- **Lignes 174–176 :** retirer ou revoir la limite de 200 selon la correction retenue.
- **Lignes 68–82 — mesure revérifiée :** les 48 tours provenaient d’une modification volontaire pour un test. Après remise en état normal signalée par l’utilisateur, la carte Impossible Dream a été relancée : 25 drones, 43 tours, tous livrés. Cette nouvelle mesure remplace celle du fichier de test ; aucune carte n’a été modifiée par cet audit.
- **Lignes 288–294 :** l’usage de l’IA mentionne seulement Copilot / Claude et un ancien `drone_animator.py`. La session actuelle comprend aussi assistance Codex sur robustesse, refactorisation, docstrings, tests et documentation. Décrire les interventions réellement effectuées et les parties réellement relues ; ne pas conserver une déclaration générale de compréhension complète que l’audit ne peut pas vérifier.

**Il ne manque donc pas une série de sections obligatoires. Il faut surtout corriger des informations et rendre la déclaration d’usage de l’IA fidèle.**

## Points secondaires et limites d’interprétation

### Typage strict optionnel

`make lint` passe. Le contrôle strict supplémentaire échoue dans [test_model_entities.py](../tests/test_model_entities.py:189) : mypy conserve le rétrécissement de type de la position vers `Connection`, puis considère la comparaison avec un `Hub` impossible après une méthode qui modifie cet attribut. Le test réussit à l’exécution. Adapter le test pour exprimer correctement cette mutation. Cela ne doit pas être présenté comme un échec du contrôle obligatoire.

### Docstrings et annotations

Les classes et fonctions applicatives disposent de docstrings anglaises. Plusieurs docstrings longues n’isolent pas encore la phrase de résumé par une ligne blanche, comme le recommande PEP 257. Certains constructeurs ont des paramètres annotés mais pas de `-> None` explicite ; mypy les accepte. Compléter ces annotations et le format des docstrings est une finition raisonnable, sans prétendre que tous les contrats doivent devenir de longues notices.

### Commentaires en fin de ligne

La lecture ignore les lignes dont le premier caractère utile est `#`, mais `nb_drones: 1 # fleet` est rejeté. Le chapitre VI dit que les commentaires commencent par `#` et sont ignorés, sans préciser explicitement s’ils sont autorisés après une déclaration. C’est un point à clarifier ou à tester de manière conservatrice, **pas un défaut certain affirmé sans réserve**. Attention : un découpage aveugle sur `#` pourrait interagir avec les noms de hubs autorisés.

### Couleurs

Le parser accepte les couleurs sans liste fermée, conformément au sujet. La vue remplace cependant les couleurs absentes de sa petite palette par du gris ; des noms connus comme `teal`, `lightblue` ou `beige` perdent leur distinction. Le retour visuel obligatoire existe, mais la fidélité aux couleurs peut être améliorée. Ne pas transformer cette limitation graphique en rejet de parsing.

### Drones livrés et mémoire

Les drones livrés sont bien omis des mouvements suivants. Ils restent néanmoins dans la collection triée et dans les frames du recorder. Ce n’est pas une violation démontrée du format terminal, mais c’est du travail et du stockage superflus par rapport à l’objectif de ne plus les suivre. Le journal de mouvements reste également intégralement conservé en mode sans replay. La limite de 200 ne doit pas remplacer une gestion adaptée de ces coûts.

### Portée des tests et optimisation

Les tests couvrent les 11 cartes présentes, des transits restreints, le reroutage, les capacités, les coordonnées très grandes et les erreurs courantes. Ils ne prouvent ni l’optimalité globale, ni l’absence universelle de blocage. La recherche aléatoire bornée de cet audit n’a pas trouvé de blocage stationnaire, mais le moteur n’a pas de détection générale des états sans progrès.

La priorité aux hubs `priority` à durée égale est cohérente avec le coût d’un tour et la préférence demandés. Le sujet ne justifie pas de remplacer ce coût par une durée inférieure à un tour.

## Revue fichier par fichier

| Fichier | Vérification et conclusion |
|---|---|
| `main.py` | Arguments, mode terminal, messages sur stderr et codes de retour ; erreur graphique non gérée à corriger |
| `src/controller/controller.py` | Construction sans simulation, chargement puis exécution, import graphique différé ; signature à refléter dans le README |
| `src/controller/__init__.py` | Fichier de package vide ; aucun comportement à auditer |
| `src/parser/parser.py` | Syntaxe, entiers signés, métadonnées, noms officiels de capacités, doublons, décodage, réutilisation ; alias d’en-tête et localisation des déclarations absentes à corriger |
| `src/parser/validator.py` | Types de zones, capacités, unicité, extrémités précédemment déclarées, doublons bidirectionnels, BFS sans blocked ; plafond 200 non conforme |
| `src/model/graph.py` | Construction depuis des données validées et index bidirectionnel ; pas de bibliothèque de graphe interdite |
| `src/model/hub.py` | Occupants et réservations, capacité, coût normal/priority/restricted/blocked ; pas de défaut supplémentaire confirmé |
| `src/model/connection.py` | Capacité partagée entre les deux sens et extrémité opposée ; pas de défaut supplémentaire confirmé |
| `src/model/drone.py` | Position Hub ou Connection, départ, arrivée, consommation du chemin ; cycle restreint cohérent avec le tour suivant |
| `src/model/pathfinder.py` | Dijkstra écrit avec heapq, coûts positifs, exclusions, préférence priority ; aucune bibliothèque interdite |
| `src/model/simulation.py` | Capacités et réservations conservées ; attente évitable confirmée ; mémoire et suivi des livrés à améliorer |
| `src/model/recorder.py` | Snapshots indépendants, directions et progression des transits ; conserve tous les drones livrés |
| `src/model/replay.py` | Structures de données typées ; positions et capacités présentes |
| `src/model/errors.py` | Exceptions métier distinctes ; pas de défaut supplémentaire confirmé dans leur définition |
| `src/view/__init__.py` | Suppression de la bannière Pygame pour préserver le format terminal |
| `src/view/terminal.py` | Une ligne par tour et format des hubs/connexions ; les drones immobiles sont absents du journal fourni |
| `src/view/pygame_view.py` | Fenêtre et commandes ; garantir la fermeture et gérer les échecs graphiques |
| `src/view/graph_renderer.py` | Réseau, hubs, noms, capacités et couleurs ; palette limitée mais pas de rejet des cartes |
| `src/view/replay_player.py` | Navigation, interpolation et représentants par hub ; visualisation du transit présente |
| `src/view/utils/camera.py` | Zoom et translation ; aucune non-conformité supplémentaire confirmée |
| `src/view/utils/coordinate_system.py` | Entiers géants convertis sans débordement, proportions préservées ; tests de rendu réussis |
| `Makefile` | Règles install, run, debug, clean et lint présentes ; lint obligatoire passe. lint-strict est optionnel |
| `pyproject.toml` | Python >=3.10, Pygame, outils de qualité ; pas de dépendance de graphe interdite |
| `.gitignore` | Exclut bytecode, environnement virtuel et caches de tests/mypy |
| `README.md` | Toutes les rubriques obligatoires présentes ; corrections de contenu listées plus haut |
| `tests/conftest.py` | Configuration du chemin d’import des tests |
| `tests/test_model_entities.py` | Objets et transit ; assertion à adapter pour le typage strict |
| `tests/test_parser_robustness.py` | Nombreux cas de syntaxe ; les tests du plafond 200 devront changer |
| `tests/test_parser_validator_subject.py` | Unicité, connexions et accessibilité ; ajouter les cas de localisation manquante |
| `tests/test_input_errors.py` | Fichiers absents, permissions, décodage et sortie propre ; compléter pour l’échec graphique |
| `tests/test_terminal.py` | Sorties normales/restreintes et sens des connexions |
| `tests/test_execution_modes.py` | Mode sans Pygame, réexécution et enregistrement optionnel |
| `tests/test_robustness.py` | Attente, reroutage et pipeline ; compléter avec la carte de cet audit |
| `tests/test_submission_regressions.py` | Coûts et préférences priority, livraison ; suite réussie |
| `tests/test_large_coordinates.py` | Limites d’entiers C, entiers gigantesques, translation et proportions ; suite réussie |
| `tests/test_all_maps_terminal.py` | Outil d’export et d’exécution des cartes ; ses résultats dépendent des fichiers actuels |
| `docs/subject.md` et figures | Référence issue du PDF fourni ; ne pas l’adapter au comportement du code |
| Anciens rapports d’audit | Historiques, déjà signalés comme fondés sur une transcription incorrecte ; ne pas les considérer comme certification actuelle |

## Mesures sur les fichiers de cartes actuels

Aucun fichier de `assets/maps` n’a été modifié pour cet audit. Les effectifs sont ceux des fichiers, pas 200.

| Carte | Drones | Tours observés |
|---|---:|---:|
| easy/01_linear_path | 2 | 4 |
| easy/02_simple_fork | 4 | 4 |
| easy/03_basic_capacity | 4 | 4 |
| medium/01_dead_end_trap | 5 | 8 |
| medium/02_circular_loop | 6 | 15 |
| medium/03_priority_puzzle | 5 | 7 |
| hard/01_maze_nightmare | 8 | 13 |
| hard/02_capacity_hell | 12 | 16 |
| hard/03_ultimate_challenge | 15 | 26 |
| challenger/01_the_impossible_dream — remise en état normal par l’utilisateur | 25 | 43 |
| challenger/42_spaghetti | 42 | 46 |

Les seuils faciles, moyens et difficiles du PDF sont atteints numériquement sur ces fichiers. La comparaison au benchmark officiel reste conditionnée à l’identité des cartes : un fichier modifié ne permet pas de déduire la réussite ou l’échec d’un bonus sur l’original. Spaghetti n’a pas de seuil spécifique dans ce PDF. Le bonus challenger demande de battre 45 tours sur The Impossible Dream original, et n’affecte pas la validation de la partie obligatoire.

## Ordre de correction conseillé

1. Supprimer le plafond obligatoire de 200 et adapter ses tests.
2. Gérer les échecs graphiques et garantir le nettoyage.
3. Corriger les en-têtes acceptés et la localisation des erreurs manquantes.
4. Corriger l’ordonnancement du tour avec la carte de reproduction.
5. Actualiser le README : noms officiels, API, usage réel de l’IA et provenance des résultats.
6. Terminer le typage strict optionnel et la présentation PEP 257, puis décider des améliorations de couleurs et de mémoire.

Il n’est pas nécessaire de réécrire tout le projet : les responsabilités des classes, le routage de base, les capacités et le replay existent déjà. Les corrections doivent rester ciblées et être vérifiées avec le PDF comme référence.
