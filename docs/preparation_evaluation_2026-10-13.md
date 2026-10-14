# Préparation de l’évaluation Fly-in — 13 octobre 2026

État examiné : commit `7a373db`, avec la grille d’évaluation ajoutée localement dans `docs`.

Suivi après l’audit : le README et les positions d’erreur de fin de fichier ont été corrigés. L’historique a ensuite été unifié dans `TurnState` : hubs, réservations, connexions, drones et chemins sont enregistrés pour les deux vues. Le visuel affiche les réservations et l’usage des connexions ; les couleurs manquantes de Spaghetti ont été ajoutées. Les mesures initiales ci-dessous précèdent cette refonte.

Références : [grille d’évaluation fournie](Intra%20Projects%20Fly-in%20Edit%20%281%29_261013_204613%20%281%29.pdf) et [sujet officiel retranscrit, version 1.6](subject.md). Les pages indiquées ci-dessous sont celles du PDF d’évaluation, qui comporte huit pages.

## Avis avant soutenance

Le moteur passe les vérifications exécutées et atteint les cibles des deux bonus sur les cartes du dépôt. Il n’est pas nécessaire de refaire son architecture pour préparer la validation.

Il reste cependant des écarts à corriger ou à traiter avant le rendu : la limite de 200 drones et le contenu du dépôt remis. Il faut également savoir réaliser l’exercice `--capacity-info` en direct. Les bonus ne sont évalués qu’après validation des exigences obligatoires.

Ce bilan ne constitue pas une validation officielle ni une note : la grille fournie ne donne pas de pondération numérique, et la présence, l’explication du code, le rendu officiel et le live coding restent à vérifier pendant la soutenance.

## Vérifications exécutées

| Contrôle | Résultat |
|---|---|
| `poetry run pytest -q` | **178 tests réussis**, 1,66 s |
| `make lint` | Flake8 et les options Mypy obligatoires passent |
| `poetry run mypy .` | Aucun problème dans 34 fichiers |
| Onze cartes du dépôt, effectifs d’origine | Tous les drones arrivent ; résultats détaillés ci-dessous |
| Contrôles après chaque traitement de drone sur ces cartes | Occupations, réservations et capacités cohérentes ; transitions entre hubs et connexions valides |
| Onze cartes avec 200 drones en mémoire | Toutes terminent ; aucune carte n’a été modifiée |
| Grand graphe temporaire | 602 hubs, 2 970 connexions, 50 drones : 63 tours, environ 1,61 s pour le chargement des drones et la simulation |
| Entrées invalides via le programme principal | Rejets propres, code 1, sans traceback sur les cas testés |
| Très grandes capacités positives | Une carte avec des capacités de `10^30` est acceptée et termine |
| Rendu Pygame avec le pilote SDL `dummy` | **197 frames** des onze cartes rendues sans exception ; ressources libérées |

Les contrôles d’occupation recomptent les drones réellement présents dans chaque hub et les destinations réservées par les drones en transit. Ils comparent ces valeurs aux compteurs du moteur et vérifient les plafonds des hubs et connexions. Les transitions vérifient également l’existence des arêtes et le transit lors de l’entrée dans un hub restreint.

Les tests CLI supplémentaires couvrent : nombre de drones absent ou mal formé, type de zone invalide, départ ou arrivée manquants, capacité de hub nulle, capacité de connexion négative, doublons de hubs et d’arêtes inversées, extrémité inconnue et graphe déconnecté. Tous produisent un message lisible sans traceback. Une carte valide de 201 drones est toutefois rejetée par la limite applicative.

Le rendu `dummy` vérifie l’exécution du code graphique, pas la lisibilité sur l’écran de soutenance ni l’interaction avec une vraie fenêtre. L’absence d’erreur dans ces essais ne prouve pas l’absence de tout crash ou blocage sur un autre graphe.

## Lecture de la grille

| Critère | Page | État et justification |
|---|---:|---|
| Présence du candidat | 2 | À vérifier en soutenance. |
| Contenu du dépôt remis | 2 | À préparer : le dépôt de développement contient notamment les tests suivis par Git ; voir le point sur le rendu ci-dessous. L’identité et le clone du dépôt officiel ne sont pas vérifiés ici. |
| README | 2 | Rubriques présentes et contenu actualisé après l’audit : commandes, capacités, algorithme, historique complet, affichage et usage de l’IA. |
| OOP | 2–3 | Architecture organisée en classes : parser, validateur, graphe, entités, simulation, recherche de chemin et vues. Aucune hiérarchie d’héritage artificielle n’est nécessaire. |
| Typage | 3 | `mypy .` et les options obligatoires passent. |
| Graphe personnalisé | 3 | Listes d’adjacence et index des connexions développés dans `Graph`, sans bibliothèque de graphes interdite. |
| Formats d’entrée | 3 | Préfixes officiels, valeurs par défaut, `max_drones`, `max_link_capacity` et commentaires de ligne pris en charge. |
| Erreurs du parser | 3 | Les cinq familles d’erreurs demandées sont couvertes par les tests et les essais CLI. |
| Capacité des zones | 3–4 | Vérifiée, avec réservations des destinations restreintes et capacité illimitée au départ et à l’arrivée. |
| Coûts de déplacement | 4 | Normal/priority : un tour ; restricted : deux ; blocked : inaccessible. Tests de préférence des hubs priority à durée égale. |
| Capacité des connexions | 4 | Limites et usages simultanés couverts ; pas de dépassement dans les contrôles sur les onze cartes. |
| Représentation visuelle | 4 | Replay fondé sur l’historique complet, avec réservations et usage des connexions. Les quatre couleurs de Spaghetti ont été ajoutées après l’audit. Contrôle interactif sur la machine de soutenance restant à faire. |
| Scénarios simples et format terminal | 4 | Tests du parcours linéaire, des chemins alternatifs et du format par tour réussis ; drones en attente omis. |
| Fin de simulation | 4–5 | Tous les drones arrivent sur les onze cartes et aucun tour supplémentaire n’est ajouté après leur arrivée. |
| Chemins valides | 5 | Dijkstra fonctionne sur les cartes testées, les types de zones et le grand graphe temporaire. |
| Résolution des conflits | 5 | Capacités et réservations respectées dans les cas testés. Une attente évitable liée à l’ordre de traitement reste reproductible. |
| Efficacité | 5 | Résultats satisfaisants aux effectifs d’origine et à 200 drones ; critère explicitement non éliminatoire dans la grille. |
| Explication de l’algorithme | 5 | À démontrer oralement : Dijkstra, capacités, réservations, reroutage et limites de l’heuristique. |
| Benchmark Easy | 6 | **4 tours de moyenne**, inférieur à 10. |
| Benchmark Medium | 6 | **10 tours de moyenne**, dans l’intervalle 10–30. |
| Benchmark Hard | 6 | **18,33 tours de moyenne**, inférieur à 60. |
| Cas limites | 6 | Drone seul, goulots, graphes déconnectés, connexions invalides et capacités nulles ou très élevées couverts. |
| Messages d’erreur | 6–7 | Clairs et contrôlés sur les cas demandés. Correction après l’audit : les hubs de départ ou d’arrivée manquants indiquent désormais la dernière ligne physique et la fin du fichier. |
| Qualité du code | 7 | Classes séparées, docstrings présentes et lint réussi. Critère de qualité, explicitement non éliminatoire. |
| Live coding | 7 | À réaliser par le candidat : flag `--capacity-info` et démonstration en dix minutes maximum. Ce n’est pas une fonctionnalité obligatoire à préimplémenter. |
| Bonus performances | 7–8 | Toutes les cibles individuelles Easy/Medium/Hard sont atteintes. Sous réserve de validation de la partie obligatoire. |
| Bonus Challenger | 8 | Impossible Dream : **43 tours**, strictement inférieur au record de 45. Même réserve. |

## Performances mesurées

| Carte | Drones d’origine | Tours | Cible individuelle | Tours avec 200 drones | Temps avec 200 drones |
|---|---:|---:|---:|---:|---:|
| Easy — Linear path | 2 | 4 | ≤ 6 | 202 | 86 ms |
| Easy — Simple fork | 4 | 4 | ≤ 8 | 102 | 55 ms |
| Easy — Basic capacity | 4 | 4 | ≤ 6 | 102 | 47 ms |
| Medium — Dead end trap | 5 | 8 | ≤ 12 | 203 | 72 ms |
| Medium — Circular loop | 6 | 15 | ≤ 15 | 403 | 157 ms |
| Medium — Priority puzzle | 5 | 7 | ≤ 12 | 137 | 186 ms |
| Hard — Maze nightmare | 8 | 13 | ≤ 30 | 205 | 188 ms |
| Hard — Capacity hell | 12 | 16 | ≤ 35 | 204 | 865 ms |
| Hard — Ultimate challenge | 15 | 26 | ≤ 45 | 211 | 1 071 ms |
| Challenger — Impossible Dream | 25 | **43** | **< 45** | 218 | 256 ms |
| Challenger — Spaghetti | 42 | 46 | Aucune dans cette grille | 121 | 269 ms |

Les temps à 200 drones ont été mesurés avant la refonte du recorder, sur un seul passage de `simulate()`, sans replay, sans impression terminal et sans les contrôles d’invariants supplémentaires. Ils excluent le parsing et le chargement initial des drones ; ils donnent un ordre de grandeur sur cette machine, pas un benchmark statistique. Après refonte, Hard 03 avec 200 drones termine en 211 tours et conserve 212 états complets ; un passage avec chargement des drones et enregistrement a pris environ 1,21 s. Les périmètres de chronométrage diffèrent.

Les critères et les bonus sont comparés aux **effectifs d’origine**. Les 48 tours relevés dans un ancien essai d’Impossible Dream provenaient d’une modification de carte pour test : la carte actuelle donne bien 43 tours.

## Points à régler avant le rendu

### 1. Limite de 200 drones : écart explicite au sujet

Dans [le validateur](../src/parser/validator.py:14), `MAX_DRONES = 200` entraîne le rejet d’une carte de 201 drones, même sur un trajet élémentaire.

Le sujet, VII.4, demande de gérer tout nombre de drones. La grille n’a pas de case consacrée à cette limite, mais cela reste un écart au sujet. Retirer le plafond de validité est préférable ; conserver l’exigence d’un entier strictement positif. Il faudra adapter les tests qui imposent actuellement le rejet à partir de 201 et le paragraphe du README. Le moteur ne doit pas être présenté comme garantissant des ressources illimitées.

### 2. Couleurs de cartes — corrigé après l’audit

[HubRenderer](../src/view/graph_renderer.py) utilisait la couleur de secours `(200, 200, 200)` pour les couleurs suivantes de Spaghetti, désormais ajoutées à la palette :

| Couleur | Hubs concernés |
|---|---|
| `lightbrown` | `here_we_go_again` |
| `lightblue` | `normal_road_north`, `normal_road_join`, `normal_road_south` |
| `teal` | `choose_wisely`, `where_are_we_going`, `far_far_away` |
| `beige` | `is_there_a_way` |

Les noms inconnus conservent une couleur de secours. Le visuel lit la couleur enregistrée dans le hub du tour sélectionné.

### 3. README — actualisé après l’audit

Le [README](../README.md) utilise désormais `is_view=False`, `max_drones` et `max_link_capacity`, détaille l’algorithme, sa complexité, l’historique complet, les limites actuelles et les contributions récentes de Codex. Les exemples d’entrée/sortie ont été vérifiés. Le plafond de 200 drones reste documenté tant qu’il existe dans le code.

### 4. Préparer le contenu du dépôt de rendu

La grille, page 2, demande de ne remettre que les fichiers attendus et prévoit l’arrêt de l’évaluation sinon. Le sujet, III.3, précise que les programmes de test ne sont pas soumis ou notés. Or `tests/` est actuellement suivi par Git.

Il faut préparer le contenu remis en conservant une copie de développement avec les tests et les audits. Vérifier également la nécessité des anciens audits, de `.vscode/` et des documents de travail dans le dépôt officiel. La grille ne donne pas une liste exhaustive de fichiers autorisés : ce point ne justifie pas de supprimer automatiquement les sources, les cartes, les dépendances ou la documentation nécessaire.

Ajouter une entrée à `.gitignore` ne retire pas un fichier déjà suivi. Aucun fichier n’a été supprimé et aucune préparation de commit ou de dépôt officiel n’a été effectuée pendant cet audit.

### 5. Réserves secondaires à connaître

- **Corrigé après l’audit :** [le parser](../src/parser/parser.py) indique désormais la dernière ligne physique et la fin du fichier pour `missing start_hub` et `missing end_hub`, par exemple `Line 5: missing end_hub at end of file.` Les lignes vides et les commentaires finaux sont comptés. Les essais CLI couvrent les deux hubs absents, avec et sans saut de ligne final, ainsi que les lignes ignorées ; la réutilisation du parser après lecture d’un fichier plus long a aussi été vérifiée. Les 178 tests et `make lint` passent après correction.
- Le parser accepte `drones:` et `nb_drone:` en plus de `nb_drones:`. Il s’agit d’extensions du format ; le sujet demande un format précis. Décider explicitement si ces alias doivent rester, sans confondre cela avec un échec des entrées officielles.
- Le cas [same_turn_release.txt](audit_cases/same_turn_release.txt) confirme encore une attente évitable au tour 7 : D6 attend en `h5` devant `h7`, puis D4 quitte `h7` plus tard dans le même tour. D6 n’est pas réexaminé, alors que le hub et la connexion deviennent disponibles. La carte termine en 11 tours, sans dépassement de capacité. C’est une limite d’ordonnancement, pas un blocage infini démontré.
- Le BFS du validateur garantit une accessibilité statique. Il ne constitue pas une preuve que toute interaction entre drones terminera. Aucun blocage infini n’a été observé dans les essais de cette séance ; le moteur ne possède pas de détection générale de blocage.

La correction des erreurs graphiques demandée auparavant est bien présente : `PygameView.display()` traduit les `pygame.error` en `DisplayError`, `main()` affiche une erreur propre et `finally` appelle `pygame.quit()`. Les tests couvrent l’initialisation, la création de fenêtre, le rendu, la fermeture normale et l’exécution terminal avec un pilote vidéo invalide. Les exceptions internes inattendues ne sont pas masquées.

## Préparer l’exercice `--capacity-info`

La page 7 demande d’ajouter le flag pendant la soutenance et de montrer, à chaque tour, l’occupation des zones et l’usage des connexions, en complément des mouvements normaux. Le travail et sa démonstration doivent tenir en dix minutes.

Les endroits à savoir retrouver :

| Fichier | Rôle dans la modification |
|---|---|
| [main.py](../main.py) | Déclaration du flag avec `argparse` et transmission de sa valeur. |
| [controller.py](../src/controller/controller.py) | Transmission de l’option de la CLI à la vue terminal. |
| [state.py](../src/model/state.py) | Structure des données déjà enregistrées pour chaque tour. |
| [terminal.py](../src/view/terminal.py) | Formatage et affichage des informations supplémentaires. |

L’enregistrement complet existe maintenant indépendamment du flag. Il n’est plus nécessaire d’ajouter un journal ni de changer le recorder pour cet exercice. Le terminal reçoit les mêmes `TurnState` que le replay graphique.

- Lire `frame.hubs` pour afficher `nb_drones`, `reserved` et `capacity`.
- Lire `frame.connections` pour afficher `used_capacity`, `in_transit` et `capacity`.
- `used_capacity` est l’usage pendant le tour ; `in_transit` compte seulement les drones encore sur la connexion à la fin. Ces valeurs diffèrent notamment au tour d’arrivée d’un transit restreint.
- Ignorer le tour initial zéro dans la sortie par tour, comme le fait déjà `TerminalView`.

Il reste à déclarer l’option CLI, la transmettre à la vue et ajouter le formatage conditionnel des données existantes. Le mode sans option doit conserver exactement sa sortie habituelle.

S’entraîner sur une petite carte comprenant un hub de capacité 2, une connexion de capacité 2 et une zone restreinte permet de montrer l’occupation simultanée, les réservations et le transit. L’exercice n’a pas été implémenté pendant cet audit.

## Ce qu’il faut pouvoir expliquer oralement

- Pourquoi le graphe stocke l’adjacence et un index des paires de hubs ; pourquoi une connexion est bidirectionnelle.
- Pourquoi BFS suffit au contrôle d’accessibilité, tandis que Dijkstra choisit un chemin selon les coûts.
- Comment les priorités départagent des chemins de même durée sans favoriser un chemin plus lent.
- Pourquoi une destination restreinte est réservée et pourquoi la connexion reste occupée pendant le transit.
- Comment les exclusions évoluent pendant un reroutage, et pourquoi un drone attend quand aucune alternative n’est disponible.
- Pourquoi cette méthode est une heuristique pour plusieurs drones : les choix individuels et l’ordre de traitement ne garantissent pas un optimum global.
- Une recherche de Dijkstra coûte classiquement `O((V + E) log V)` sur ce graphe simple avec tas. La simulation ajoute le tri des drones à chaque tour, le calcul de leurs durées restantes, les reroutages et l’enregistrement complet. Sa complexité totale ne se réduit donc pas à celle d’un unique Dijkstra.
- Pourquoi le mode terminal n’importe pas Pygame et comment les ressources graphiques sont libérées en cas d’erreur.

## Périmètre de l’audit initial

Le code, les cartes, le README et les tests n’ont pas été modifiés. Les cartes de diagnostic ont été créées dans un répertoire temporaire automatiquement nettoyé ; les essais à 200 drones utilisent des objets en mémoire. Seul ce rapport est ajouté. La grille PDF est présente localement mais n’était pas suivie par Git au début de la vérification.

Les corrections et la refonte décrites dans les notes de suivi sont postérieures à cet audit initial. La comparaison avec le commit `7a373db` confirme des sorties terminal strictement identiques sur les onze cartes après la refonte du recorder.
