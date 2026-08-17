# PROJECT AUDIT - FLY-IN

Date: 2026-08-16
Workspace: fly_in_v2

## 1. Resume global

Ce projet presente une base solide (architecture MVC, parser structure, moteur de simulation fonctionnel, interface Pygame), mais il n'est pas conforme integralement au sujet sur des points centraux:

- format de sortie de simulation non conforme au format obligatoire;
- gestion des zones `restricted` incorrecte dans la simulation (cout de transit applique a 1 au lieu de 2);
- logique de priorisation des zones `priority` absente dans le pathfinding;
- suite de tests en etat incoherent avec l'API actuelle;
- lint et mypy non conformes.

Conclusion: projet prometteur, mais non pret pour une validation stricte du sujet sans corrections majeures sur la logique metier et la qualite outillage.

## 2. Conformite au sujet

Important: le fichier racine `# Fly-in.txt` n'est pas present dans ce workspace. L'audit a donc ete aligne strictement sur la specification disponible dans `docs/subject_fr_v3.md` (version 1.6) qui correspond au sujet fourni.

### Synthese conformite

- Conformite globale estimee: PARTIAL
- Blocages majeurs: VII.3, VII.5, VII.1 (priority), III.1 (flake8/mypy)

### Matrice de conformite

| Exigence | Statut | Commentaire |
|---|---|---|
| VII.1 Pathfinding adaptable et efficace | PARTIAL | Dijkstra implemente, reroute local present, mais pas de strategie multi-chemins explicite ni preference `priority` |
| VII.2 Regles d'occupation | PARTIAL | Capacites zones/liens gerees globalement, mais robustesse de concurrence tour-a-tour discutable |
| VII.3 Mecanismes de deplacement/couts | FAIL | `restricted` applique en transit a cout 1 dans la simulation (au lieu de 2) |
| VII.4 Contraintes parser | PARTIAL | Parser robuste sur base, mais certains cas limites/contraintes nominales non enforcees strictement |
| VII.5 Format de sortie | FAIL | Format affiche non conforme (`D_1 start -> x`) au lieu de `D1-x` |
| VII.6 Score/tours | PASS | Compteur de tours fonctionnel |
| VII.7 Benchmarks | PARTIAL | Bon sur easy/medium/hard, mais challenger au-dessus des cibles |
| III.2 Makefile | PASS | Cibles principales presentes |
| VIII README | PARTIAL | Structure bonne mais incoherences factuelles importantes |
| V Contraintes (typesafe/flake8/mypy/OOP) | PARTIAL | OOP oui, mais mypy/flake8 et type safety incomplete |

## 3. Analyse du parseur

Fichiers examines:
- `src/parser/parser.py`
- `src/parser/validator.py`

### Points forts

- Lecture nettoyee des commentaires/lignes vides.
- Verification de la premiere ligne `nb_drones`.
- Validation de base des metadonnees (`zone`, `capacity`, `capacity`).
- Validation de coherence:
  - unicite des noms de hubs,
  - endpoints de connexions existants,
  - connexions dupliquees (a-b / b-a).

### Ecarts et risques

1. Validation incomplte des noms de hubs
- Le sujet interdit tirets et espaces dans les noms de zones.
- Le parser n'applique pas explicitement cette regle au nom du hub.

2. Typage faible dans `MapValidator`
- Methodes non typees (`__init__`, `validate`, etc.), contraire a l'objectif fully typesafe.

3. Reset d'etat parser
- Le parser reutilise ses attributs d'instance (`hub_zones`, `conections`) sans reset explicite dans `parse()`. En usage standard c'est OK (une carte/un parser), mais fragile si reutilisation de la meme instance.

4. Orthographe de `conections`
- Faute de nommage interne (`conections`) source potentielle d'erreurs de maintenance.

## 4. Analyse du moteur de simulation

Fichier principal: `src/model/simulation.py`

### Fonctionnement observe

- Boucle de simulation tour par tour via `simulate_turn()` puis `simulate()`.
- Gestion du transit via etat `in_transit`, `transit_turns`, `transit_cost`.
- Capacites verifiees avant deplacer (`_zone_has_capacity`, `_connection_has_capacity`).
- Reroutage opportuniste si destination courante bloquee.

### Defauts majeurs

1. COUT `restricted` faux dans la simulation
- Dans `_move_drone`, la branche `destination.zone_type == "restricted"` lance:
  - `drone.begin_transit(..., cost=1, ...)`
- Le sujet exige un cout de 2 tours.

2. Sortie terminale non conforme au sujet
- `_print_turn` imprime des tableaux decoratifs et des formats type:
  - `D_1 start -> loop_a`
- Le sujet impose une ligne par tour, uniquement mouvements, format `D<ID>-<zone>` ou `D<ID>-<connection>`.

3. Detection de stagnation sans action
- Si aucune progression, un message debug peut etre affiche, mais la simulation continue jusqu'au `max_turns`.
- Pas de strategy anti-deadlock active ni de sortie explicite dediee.

4. Couplage fort a l'affichage
- La simulation imprime systematiquement les tours; cela pollue les benchmarks et rend l'integration CI moins propre.

## 5. Analyse des algorithmes de pathfinding

Fichier: `src/model/pathfinder.py`

### Etat actuel

- Dijkstra avec `heapq` correctement structure.
- Support `blocked_zones` et `saturated_conns` present dans la signature.
- Poids de deplacement derives de `Hub.move_cost()`.

### Ecarts

1. Priorite des zones `priority` non implemente
- `move_cost()` retourne 1.0 pour `normal` et `priority`.
- Aucune heuristique de preference `priority` dans Dijkstra.

2. Recalcul frequent
- Reroutage au cas par cas peut entrainer de nombreux recalculs de plus court chemin.
- Impact performance visible surtout sur grandes cartes/challenger.

## 6. Analyse des regles de capacite et de mouvement

Fichiers:
- `src/model/simulation.py`
- `src/model/hub.py`
- `src/model/connection.py`

### Conforme en grande partie

- Capacite zone via `nb_drone < capacity` (sauf start/end).
- Capacite connection via `nb_drones < capacity`.
- `start_hub` et `end_hub` configures en capacite infinie au parsing.

### Limites

- L'ordre de traitement des drones peut influencer les decisions d'occupation (effet de priorite implicite par ordre de liste).
- Pas de mecanisme de reservation global du tour pour arbitrage optimal multi-drone avant commit des mouvements.

## 7. Analyse de la gestion des zones restricted / priority

### restricted

- Partiellement gere dans le design (transit, connection occupee, arrivee differree).
- Non conforme en pratique a cause de `transit_cost=1` applique dans la simulation.

### priority

- Gere seulement comme zone non bloquee a cout standard.
- Exigence "doit etre prioritaire dans la recherche de chemin" non satisfaite.

## 8. Analyse de la gestion des conflits et deadlocks

### Ce qui existe

- Verifications de capacites avant entree zone/lien.
- Reroutage local d'un drone si sa destination immediate est bloquee.

### Ce qui manque

- Detection/traitement formel de deadlock global.
- Politique de resolution de conflits multi-agent (priorites par urgence, criticite de chemin, etc.).
- Strategie proactive (allocation initiale de chemins disjoints, fenetres temporelles, reservation table).

## 9. Analyse de la representation visuelle

Fichiers:
- `src/view/pygame_view.py`
- `src/view/graph_renderer.py`
- `src/view/drone_animator.py`

### Points forts

- Interface Pygame complete: zoom, pan, replay, overlay.
- Reconstitution des etats de tours via `replay_frames`.
- Affichage lisible des hubs et drones.

### Points d'attention

- `src/view/terminal.py` est vide (pas de mode terminal colore dedie).
- Coherence type-checking vue: mismatch de typage `dict_values` vs `list` dans `CoordinateSystem.compute`.

## 10. Analyse de l'architecture OOP

### Globalement bonne

- Separation claire des responsabilites (Parser/Validator/Model/Simulation/View/Controller).
- Entites metier distinctes (`Hub`, `Connection`, `Drone`, `Graph`).

### Points ameliorables

- `Controller.__init__` declenche directement la simulation complete via `_initialize()`, ce qui rend le cycle de vie moins flexible/testable.
- Nommages parfois heterogenes (`zone` vs `hub`, `conections`).
- Certaines classes Vue referencent des types non existants (`src.model.zone`).

## 11. Analyse du typage (mypy)

Commande executee: `make lint` (inclut mypy)

Resultat: FAIL

Problemes releves:
- Fonctions sans annotations dans `src/parser/validator.py`.
- Incompatibilite de type dans `src/model/graph.py` (`str | int` passe a `Hub(name=...)` attendu `str`).
- Incompatibilite de retour dans `src/model/pathfinder.py` (cle de connexion).

Conclusion: projet non typesafe au sens strict de l'enonce.

## 12. Analyse du style (flake8)

Commande executee: `make lint` (inclut flake8)

Resultat: FAIL

Problemes releves:
- Import inutilise dans `main.py` (`format_parsing_result`).
- Ligne vide avec whitespace dans `src/controller/controller.py`.
- Ligne trop longue dans `src/model/graph.py`.

Conclusion: non conforme flake8 en l'etat.

## 13. Analyse du Makefile

Fichier: `Makefile`

### Conformite

- Cibles presentes: `install`, `run`, `debug`, `clean`, `lint`, `lint-strict`.
- Cible `test` supplementaire utile.
- `lint` utilise bien les flags mypy demandes dans le sujet.

### Remarques

- `fclean` supprime tous les environnements Poetry, operation potentiellement destructive mais acceptable localement.

Bilan Makefile: globalement conforme.

## 14. Analyse du README

Fichier: `README.md`

### Points conformes

- Premiere ligne en italique conforme a l'esprit de la consigne.
- Sections presentes: Description, Instructions, Resources.
- Description de l'algorithme et de la visualisation presentes.
- Exemples d'entree/sortie presents.

### Non-conformites / incoherences

1. Incoherence de nommage de classe/fichier
- README mentionne `src/model/zone.py` alors que le code utilise `src/model/hub.py`.

2. Sortie "Expected output" non alignee avec le comportement reel
- README montre format `D1-waypoint1`, alors que le code imprime `D_1 start -> waypoint1`.

3. Affirmation `priority` preferred
- Decrite comme implementee, mais non verifiee dans le pathfinding effectif.

4. Resultats performance potentiellement optimistes
- Les chiffres annonces ne couvrent pas correctement la situation challenger actuelle:
  - impossible_dream: 46 tours (cible 45)
  - spaghetti: 62 tours (au-dessus de 45)

Bilan README: bon document de presentation, mais pas totalement fidele a l'etat reel du code.

## 15. Cas limites non geres et plan d'amelioration

### Cas limites non geres

- Noms de zones invalides (tirets/espaces) pas strictement refuses.
- Simulation sans mecanisme de sortie explicite sur deadlock autre que garde-fou `max_turns`.
- Tests de robustesse desynchronises de l'API publique actuelle.
- Sortie obligatoire du sujet non produite.

### Plan d'amelioration priorise

1. Critique - conformite metier
- Corriger le cout `restricted` a 2 tours dans la simulation.
- Refaire la sortie de simulation au format strict du sujet (`D<ID>-<zone>`).
- Harmoniser l'identifiant drone (`D1` au lieu de `D_1`).

2. Critique - qualite
- Reparer la suite de tests (`simulate()` vs anciennes methodes).
- Faire passer `make lint` integralement (flake8 + mypy).

3. Important - algorithme
- Introduire une vraie priorisation des zones `priority`.
- Ajouter une strategie de repartition multi-chemins des drones.

4. Important - robustesse
- Ajouter detection active de deadlock + politique de resolution.
- Ajouter tests de non-regression sur: restricted, capacity, output format, duplicate edges, blocked hubs.

5. Important - documentation
- Aligner README sur la realite du code (noms de fichiers/classes, format output, performances).

---

## Annexes d'execution

### A. Lint / Tests

- `make lint`: FAIL
- `make test`: FAIL (5 echecs, 1 succes)

### B. Benchmark de tours observe (simulation sans Pygame)

| Carte | Tours observes | Cible sujet |
|---|---:|---:|
| assets/maps/easy/01_linear_path.txt | 4 | <= 6 |
| assets/maps/easy/02_simple_fork.txt | 4 | <= 8 |
| assets/maps/easy/03_basic_capacity.txt | 4 | <= 6 |
| assets/maps/medium/01_dead_end_trap.txt | 8 | <= 12 |
| assets/maps/medium/02_circular_loop.txt | 15 | <= 15 |
| assets/maps/medium/03_priority_puzzle.txt | 8 | <= 12 |
| assets/maps/hard/01_maze_nightmare.txt | 10 | <= 30 |
| assets/maps/hard/02_capacity_hell.txt | 11 | <= 35 |
| assets/maps/hard/03_ultimate_challenge.txt | 27 | <= 45 |
| assets/maps/challenger/01_the_impossible_dream.txt | 46 | 45 (record) |
| assets/maps/challenger/42_spaghetti.txt | 62 | 45 (record) |

Interpretation:
- Easy/Medium/Hard: objectifs atteints ou depasses.
- Challenger: objectif record non atteint.

---

Audit termine.
