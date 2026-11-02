# Fly-in — Audit intégral, méthode par méthode (test-main)

**Branche de travail :** `test-main`. Base historique : commit `4c1eeddfc1bda589d62c77bf7b5689f6def5c8fe`. Les corrections auditées sont développées sur `test-main`. Le passage à `argparse` a d’abord été poussé par erreur sur `main` (`3246d28131dfdc44dbb5b9aea162af50edc3fb28`), puis reporté sur `test-main` avec la prise en charge de `ValidatorError`. Depuis cette décision, toutes les nouvelles modifications restent sur `test-main` jusqu’à la fusion finale.

**Inventaire vérifié : 83 méthodes et fonctions explicites dans 17 fichiers applicatifs.** Chaque définition `def` a été comparée à l’index ci-dessous : aucune ne manque. L’audit inclut aussi les dataclasses, erreurs et branches rarement exécutées.

## 1. Chemin réel des appels depuis main

```text
main.main
 └ Controller.__init__ ; Controller.run
    └ Parser.__init__ ; Parser.parse
       └ Parser.read_file (pour chaque ligne)
          └ Parser.parse_line
             ├ Parser._parse_integer (nb_drones)
             ├ Parser.parse_hub -> _parse_integer (x,y,capacité)
             │                   -> parse_metadata
             └ Parser.parse_connection -> parse_metadata -> _parse_integer
       └ MapValidator.__init__ ; MapValidator.validate
          ├ _check_zone_types
          ├ _check_unique_hub_names
          ├ _check_connection_endpoints
          ├ _check_duplicate_connections
          └ _check_reachable_end (BFS)
    └ Graph.__init__
       ├ Hub.__init__ (toutes les zones)
       ├ Graph._build_connections -> Connection.__init__
       └ Graph._index_connection
    └ Simulation.__init__ -> Dijkstra.__init__ ; Recorder.__init__
       ├ Simulation.load_drones
       │  ├ Dijkstra.shortest_path -> shortest_distances
       │  │  └ Graph.get_connections -> Connection.get_other_hub
       │  │                           -> Hub.move_cost -> transit_duration
       │  ├ Drone.__init__ -> Drone.set_path
       │  ├ Hub.add_drone -> is_available
       │  └ Recorder.record
       └ Simulation.simulate (boucle de tours)
          ├ _all_drones_delivered
          ├ _prepare_connections_for_turn -> Connection.use_capacity
          ├ Drone.path_turns (tri)
          ├ _advance_drone
          │  ├ _move_or_wait -> Graph.get_connection
          │  │  ├ Hub.is_available ; Connection.is_available
          │  │  ├ move_drone -> Hub.remove_drone
          │  │  │              -> Drone.move_to_zone OU begin_transit
          │  │  │              -> Hub.add_drone OU reserve
          │  │  │              -> Connection.use_capacity
          │  │  ├ _reroute_drone -> Dijkstra.shortest_path
          │  │  └ Drone.wait
          │  ├ Drone.advance_transit -> Connection.get_other_hub
          │  │                         -> Hub.release_reservation -> add_drone
          │  └ Drone.deliver
          └ Recorder.record
    └ TerminalView.display
    └ [vue active] PygameView.__init__ -> display -> _display_replay
       ├ Camera.__init__
       ├ CoordinateSystem.__init__ -> compute
       ├ GraphRenderer.__init__ -> HubRenderer.__init__
       │                          -> ConnectionRenderer.__init__
       ├ ReplayPlayer.__init__
       └ boucle écran : handle_event / Camera ; GraphRenderer.draw
                       ReplayPlayer.draw ; ReplayPlayer.draw_overlay
```

Les appels répétés dans les boucles ne sont montrés qu’une fois. Les méthodes uniquement utilisées dans les événements, diagnostics ou tests figurent également dans l’inventaire.

## 2. Inventaire exhaustif et décision par méthode

Pour chaque entrée : **signature effective du fichier**, paramètres, rôle/évaluation et décision. Les liens pointent vers les fichiers de la branche test-main.

### `main.py` (1 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`main`](https://github.com/Irohs6/fly_in_v2/blob/test-main/main.py#L10) — `def main() -> int:` | `argparse` lit un unique `map_path` facultatif (carte par défaut), refuse les options inconnues et les cartes supplémentaires, gère `-h/--help` et `--no-view`. Lance le contrôleur et intercepte `ValidatorError`, `ParseError`, les erreurs d'affichage/lecture et `KeyboardInterrupt`. | **MODIFIÉ** |

### `src/controller/controller.py` (2 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Controller.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/controller/controller.py#L11) — `def __init__(self, map_path: str) -> None:` | Ne fait que mémoriser map_path:str ; aucun accès disque et aucun Path superflu. | **CONSERVER** |
| [`Controller.run`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/controller/controller.py#L15) — `def run(self, *, view_active: bool = True) -> None:` | Orchestre parsing, graphe, chargement des drones, simulation et sorties ; respecte la séparation modèle/vue/contrôleur. | **CONSERVER** |

### `src/parser/parser.py` (8 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Parser.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L42) — `def __init__(self, map_path: str):` | Initialise le chemin, les deux listes d’entrées avec lignes physiques et les déclarations facultatives avant lecture. | **CONSERVER** |
| [`Parser.read_file`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L55) — `def read_file(self) -> None:` | Lit UTF-8 ligne par ligne, ignore vide et commentaires seuls, mémorise le numéro, appelle parse_line ; encapsule erreurs de lecture. | **CONSERVER** |
| [`Parser.parse_hub`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L81) — `def parse_hub( self, hub_type: str, raw: str, line_number: int, ) -> None:` | Lit type, nom, x/y et métadonnées ; vérifie unicité des terminaux ; capacités start/end illimitées ; noms de variables homogénéisés. | **MODIFIÉ** |
| [`Parser.parse_connection`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L153) — `def parse_connection(self, raw: str, line_number: int) -> None:` | Lit paire de zones, refuse tirets en trop et espaces, contrôle capacité ; nom capacity_raw homogénéisé. | **MODIFIÉ** |
| [`Parser.parse_metadata`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L203) — `def parse_metadata( raw: str, line_number: int, allowed_keys: set[str], ) -> dict[str, str]:` | Méthode statique pour format [clé=valeur], clés permises, valeurs non vides, répétitions et parenthèses carrées. | **CONSERVER** |
| [`Parser._parse_integer`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L246) — `def _parse_integer( raw: str, line_number: int, field: str, *, positive: bool = False, ) -> int:` | Méthode statique pour entiers signés ou strictement positifs, message contextualisé ; conserver le catch ValueError (entiers trop longs). | **CONSERVER** |
| [`Parser.parse`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L269) — `def parse(self) -> ParsedMap:` | Réinitialise l’état pour réutilisation, lit, vérifie déclarations, délègue au validateur, construit ParsedMap ; laisse ValidatorError remonter. | **MODIFIÉ** |
| [`Parser.parse_line`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L322) — `def parse_line(self, line: str, line_number: int) -> None:` | Exige exactement un caractère :, extrait keyword et raw puis distribue à la méthode spécialisée ; erreurs de syntaxe dans ParseError. | **CONSERVER** |

### `src/parser/validator.py` (7 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`MapValidator.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L18) — `def __init__( self, start_hub: HubDict, end_hub: HubDict, hub_entries: list[tuple[HubDict, int]], connection_entries: list[tuple[ConnectionDict, int]], ) -> None:` | Conserve les définitions et leurs lignes source ; pas de validation anticipée. | **CONSERVER** |
| [`MapValidator.validate`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L35) — `def validate(self) -> None:` | Enchaîne les cinq contrôles statiques ; les exceptions sont de type ValidatorError. | **MODIFIÉ** |
| [`MapValidator._check_zone_types`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L43) — `def _check_zone_types(self) -> None:` | Refuse tout type différent de normal/blocked/restricted/priority. | **MODIFIÉ** |
| [`MapValidator._check_unique_hub_names`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L53) — `def _check_unique_hub_names(self) -> None:` | Détecte doublons de nom parmi toutes les zones, y compris start/end. | **MODIFIÉ** |
| [`MapValidator._check_connection_endpoints`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L66) — `def _check_connection_endpoints(self) -> None:` | Vérifie existence des zones reliées et ordre de définition avant une connexion. | **MODIFIÉ** |
| [`MapValidator._check_duplicate_connections`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L86) — `def _check_duplicate_connections(self) -> None:` | Normalise le couple de noms pour détecter une duplication dans les deux sens. | **MODIFIÉ** |
| [`MapValidator._check_reachable_end`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L112) — `def _check_reachable_end(self) -> None:` | Parcours BFS depuis start en excluant blocked ; garantit une route statique, non la fin de toute congestion. | **MODIFIÉ** |

### `src/model/graph.py` (5 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Graph.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L9) — `def __init__(self, data: ParsedMap) -> None:` | Construit les Hub et Connection, adjacency et connection_map ; expression de docstring sans effet corrigée. | **MODIFIÉ** |
| [`Graph._build_connections`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L36) — `def _build_connections( self, raw_connections: list[ConnectionDict], ) -> list[Connection]:` | Instancie chaque connexion depuis les noms validés, sans dépendance à une bibliothèque de graphes. | **CONSERVER** |
| [`Graph._index_connection`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L51) — `def _index_connection( self, connection: Connection, ) -> None:` | Insère le même objet Connection dans deux listes d’adjacence et deux clés directionnelles. | **CONSERVER** |
| [`Graph.get_connections`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L70) — `def get_connections(self, hub: Hub) -> list[Connection]:` | Retourne les connexions incidentes ou une liste vide ; utilisé par Dijkstra. | **CONSERVER** |
| [`Graph.get_connection`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L74) — `def get_connection(self, source: Hub, target: Hub) -> Connection \| None:` | Trouve le lien direct entre deux Hub en temps moyen constant ; utilisé par le mouvement. | **CONSERVER** |

### `src/model/hub.py` (10 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Hub.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L6) — `def __init__(self, name: str, color: str = "white", zone_type: str = "normal", capacity: int \| float = 1, x: int = 0, y: int = 0) -> None:` | Stocke type, coordonnées, capacité, occupation et réservations ; paramètres cohérents avec HubDict. | **CONSERVER** |
| [`Hub.add_drone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L20) — `def add_drone(self) -> None:` | Incrémente seulement si place réellement disponible ; délègue la règle à is_available. | **CONSERVER** |
| [`Hub.remove_drone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L26) — `def remove_drone(self) -> None:` | Libère une occupation et refuse de décrémenter en dessous de zéro. | **CONSERVER** |
| [`Hub.is_available`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L32) — `def is_available(self) -> bool:` | Inclut les places réservées dans la capacité ; prévient la collision à l’arrivée restricted. | **CONSERVER** |
| [`Hub.reserve`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L36) — `def reserve(self) -> None:` | Bloque une place à destination avant le transit sur une connexion. | **CONSERVER** |
| [`Hub.release_reservation`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L47) — `def release_reservation(self) -> None:` | Annule une place réservée juste avant l’entrée dans le Hub. | **CONSERVER** |
| [`Hub.move_cost`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L56) — `def move_cost(self) -> float:` | Renvoie l’infini pour blocked et une durée sous forme flottante pour les autres types. | **CONSERVER** |
| [`Hub.transit_duration`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L62) — `def transit_duration(self) -> int:` | Renvoie 2 pour restricted, 1 sinon ; paramètre central du calcul de chemin. | **CONSERVER** |
| [`Hub.__str__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L71) — `def __str__(self) -> str:` | Fournit une représentation descriptive pour debug avec nombre de drones. | **CONSERVER** |
| [`Hub.__repr__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L79) — `def __repr__(self) -> str:` | Réutilise __str__ ; utile en inspection interactive, même si pas appelée pendant l’exécution normale. | **CONSERVER** |

### `src/model/connection.py` (5 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Connection.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L7) — `def __init__(self, source: Hub, target: Hub, capacity: int \| float):` | Conserve deux Hub, capacité maximale et consommation du tour. | **CONSERVER** |
| [`Connection.use_capacity`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L15) — `def use_capacity(self) -> None:` | Consomme une unité après vérification ; erreur métier si dépassement. | **CONSERVER** |
| [`Connection.is_available`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L25) — `def is_available(self) -> bool:` | Contrôle used_capacity < capacity, capacité partagée par les deux directions. | **CONSERVER** |
| [`Connection.get_other_hub`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L29) — `def get_other_hub(self, hub: Hub) -> Hub:` | Récupère le voisin opposé ou déclenche ConnectionError si Hub étranger au lien. | **CONSERVER** |
| [`Connection.__repr__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L43) — `def __repr__(self) -> str:` | Affiche les noms extrémités, capacité et usage ; diagnostic non nominal. | **CONSERVER** |

### `src/model/drone.py` (8 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Drone.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L9) — `def __init__( self, drone_id: int, current_position: Hub ) -> None:` | Initialise ID, Hub courant, précédente zone, chemin vide et état idle. | **CONSERVER** |
| [`Drone.move_to_zone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L23) — `def move_to_zone( self, zone: Hub, ) -> None:` | Déplace en un tour, retient l’origine, consomme le prochain Hub du chemin et marque moving. | **CONSERVER** |
| [`Drone.begin_transit`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L42) — `def begin_transit( self, connection: Connection, ) -> None:` | Met le drone sur Connection, conserve l’origine et marque in_transit. | **CONSERVER** |
| [`Drone.advance_transit`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L59) — `def advance_transit(self) -> Hub \| None:` | Au tour suivant, va sur le Hub opposé au départ, consomme une étape et retourne la destination. | **CONSERVER** |
| [`Drone.wait`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L81) — `def wait(self) -> None:` | Marque waiting sans toucher au chemin ni à la position. | **CONSERVER** |
| [`Drone.deliver`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L85) — `def deliver(self) -> None:` | Marque delivered après arrivée à end. | **CONSERVER** |
| [`Drone.path_turns`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L89) — `def path_turns(self) -> int:` | Somme durées des Hub restants ; utilisé au tri, sans ajustement du transit en cours. | **CONSERVER** |
| [`Drone.set_path`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L98) — `def set_path(self, path: list[Hub]) -> None:` | Copie une liste de Hub reçue pour éviter de partager la même liste entre drones. | **CONSERVER** |

### `src/model/pathfinder.py` (4 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Dijkstra.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/pathfinder.py#L10) — `def __init__(self, graph: Graph):` | Stocke l’instance de Graph ; ne recherche rien lors de l’initialisation. | **CONSERVER** |
| [`Dijkstra.shortest_distances`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/pathfinder.py#L14) — `def shortest_distances( self, source: Hub, blocked_hubs: set[Hub] \| None = None, saturated_connections: set[tuple[Hub, Hub]] \| None = None, ) -> tuple[dict[Hub, float], dict[Hub, Hub \| None]]:` | Dijkstra à tas, filtrage hubs blocked/occupés et connexions saturées, préférence priority à coût égal. | **CONSERVER** |
| [`Dijkstra.shortest_path`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/pathfinder.py#L96) — `def shortest_path( self, source: Hub \| None = None, blocked_hubs: set[Hub] \| None = None, saturated_connections: set[tuple[Hub, Hub]] \| None = None, ) -> list[Hub]:` | Reconstruit depuis predecessors jusqu’à end ; chemin vide si end inaccessible. | **CONSERVER** |

### `src/model/simulation.py` (9 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Simulation.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L13) — `def __init__( self, graph: Graph, pathfinder: Dijkstra \| None = None, ) -> None:` | Stocke graphe, drones, compteur de tours, Dijkstra injecté ou créé, Recorder. | **CONSERVER** |
| [`Simulation.load_drones`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L32) — `def load_drones(self, nb_drones: int) -> None:` | Détermine chemin initial unique, crée N drones, compte occupation à start et prend la frame zéro. | **CONSERVER** |
| [`Simulation.move_drone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L54) — `def move_drone( self, drone: Drone, connection: Connection, target_hub: Hub, ) -> None:` | Libère la zone quittée, gère entrée immédiate ou réservation restricted, consomme capacité du lien. | **CONSERVER** |
| [`Simulation._reroute_drone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L85) — `def _reroute_drone( self, drone: Drone, blocked_hubs: set[Hub], saturated_connections: set[ tuple[Hub, Hub] ], ) -> bool:` | Calcule depuis la position actuelle avec contraintes temporaires ; remplace le chemin si possible. | **CONSERVER** |
| [`Simulation._move_or_wait`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L116) — `def _move_or_wait( self, drone: Drone, ) -> bool:` | Essaie le pas suivant, puis alternatives ; conserve chemin initial et attend si détour > coût initial +2 ; exclusion previous_zone conservée. | **RISQUE À SURVEILLER** |
| [`Simulation._all_drones_delivered`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L181) — `def _all_drones_delivered(self) -> bool:` | Stoppe uniquement lorsque chaque drone a atteint le Hub final. | **CONSERVER** |
| [`Simulation._advance_drone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L188) — `def _advance_drone( self, drone: Drone, ) -> bool:` | Avance un drone une seule fois par tour : transit, déplacement ou état livré. | **CONSERVER** |
| [`Simulation._prepare_connections_for_turn`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L210) — `def _prepare_connections_for_turn(self) -> None:` | Réinitialise les usages de liens puis réserve ceux encore occupés par les transits. | **CONSERVER** |
| [`Simulation.simulate`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L218) — `def simulate(self) -> list[TurnState]:` | Boucle tours, trie par path_turns, ordonne déplacements et enregistre frames ; pas de garde de deadlock prouvée. | **RISQUE À SURVEILLER** |

### `src/model/recorder.py` (2 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`Recorder.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/recorder.py#L12) — `def __init__(self) -> None:` | Initialise la liste des TurnState du replay. | **CONSERVER** |
| [`Recorder.record`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/recorder.py#L16) — `def record( self, turn: int, graph: Graph, drones: list[Drone], moved_drones: tuple[int, ...] = (), ) -> None:` | Copie tous les états (drones, Hub, Connection) pour figer le tour indépendamment du modèle vivant. | **CONSERVER** |

### `src/model/errors.py` (0 méthode explicite)

Les classes `ConnectionError` et `HubError` héritent directement d'`Exception`. Tous leurs appels dans l'application fournissent un message explicite. Les constructeurs personnalisés ont donc été supprimés ; les exceptions métier restent utilisées par `Connection` et `Hub`. **MODIFIÉ**

### `src/view/terminal.py` (1 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`TerminalView.display`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/terminal.py#L9) — `def display(self, turns: Iterable[TurnState]) -> None:` | Convertit chaque TurnState en ligne des seuls mouvements, en ignorant tour 0 ; aucun texte parasite. | **CONSERVER** |

### `src/view/pygame_view.py` (3 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`PygameView.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/pygame_view.py#L18) — `def __init__( self, replay_frames: list[TurnState], ) -> None:` | Conserve replay_frames, sans ouvrir de fenêtre dans le constructeur. | **CONSERVER** |
| [`PygameView.display`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/pygame_view.py#L25) — `def display(self) -> None:` | Lance l’écran, transforme pygame.error en DisplayError et assure pygame.quit en finally. | **CONSERVER** |
| [`PygameView._display_replay`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/pygame_view.py#L40) — `def _display_replay(self) -> None:` | Crée une fenêtre redimensionnable et ajuste automatiquement le graphe à l’écran, sans zoom ni pan. | **À VÉRIFIER SUR ÉCRAN** |

### `src/view/graph_renderer.py` (7 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`HubRenderer.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L41) — `def __init__(self, font: pygame.font.Font) -> None:` | Conserve la police de texte des Hub. | **CONSERVER** |
| [`HubRenderer.radius`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L45) — `def radius(self, zone: HubState) -> int:` | Calcule un rayon borné selon la capacité, sans zoom. | **CONSERVER** |
| [`HubRenderer.draw`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L51) — `def draw( self, screen: pygame.Surface, zone: HubState, position: tuple[int, int], is_terminal: bool = False, ) -> None:` | Dessine le hub, son contour et ses labels ; le mode `rainbow` utilise sept cercles colorés concentriques. | **LIMITE VISUELLE** |
| [`ConnectionRenderer.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L91) — `def __init__(self, font: pygame.font.Font) -> None:` | Conserve la police des étiquettes de connexions. | **CONSERVER** |
| [`ConnectionRenderer.draw`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L95) — `def draw( self, screen: pygame.Surface, source_position: tuple[int, int], target_position: tuple[int, int], state: ConnectionState, ) -> None:` | Affiche liens et compteurs used/capacity et in_transit. | **CONSERVER** |
| [`GraphRenderer.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L136) — `def __init__(self, screen: pygame.Surface, font: pygame.font.Font) -> None:` | Assemble HubRenderer et ConnectionRenderer autour de l’écran Pygame. | **CONSERVER** |
| [`GraphRenderer.draw`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L142) — `def draw( self, frame: TurnState, positions: dict[str, tuple[int, int]], ) -> None:` | Dessine les connexions et les hubs aux positions écran fournies par PygameView. | **CONSERVER** |

### `src/view/replay_player.py` (10 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`ReplayPlayer.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L19) — `def __init__( self, frames: list[TurnState], ) -> None:` | Conserve frames et place current_index sur le tour zéro. | **CONSERVER** |
| [`ReplayPlayer._drone_color`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L28) — `def _drone_color( self, drone_id: int, ) -> tuple[int, int, int]:` | Attribue une couleur stable par ID, modulo la taille de la palette. | **CONSERVER** |
| [`ReplayPlayer.handle_event`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L40) — `def handle_event(self, event: pygame.event.Event) -> None:` | Route flèche droite/gauche et R vers navigation ; ignore autres touches. | **CONSERVER** |
| [`ReplayPlayer.next_turn`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L54) — `def next_turn(self) -> None:` | Incrémente l’index en respectant la dernière frame. | **CONSERVER** |
| [`ReplayPlayer.previous_turn`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L61) — `def previous_turn(self) -> None:` | Décrémente sans aller avant le tour zéro. | **CONSERVER** |
| [`ReplayPlayer.restart`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L68) — `def restart(self) -> None:` | Replace l’index sur zéro. | **CONSERVER** |
| [`ReplayPlayer._state_position`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L72) — `def _state_position( self, state: DroneState, hub_positions: dict[str, tuple[float, float]], ) -> tuple[float, float]:` | Pour un Hub retourne sa position, pour un transit retourne milieu des deux extrémités. | **CONSERVER** |
| [`ReplayPlayer.draw`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L86) — `def draw( self, screen: pygame.Surface, font: pygame.font.Font, hub_positions: Mapping[str, tuple[float, float]], ) -> None:` | Dessine un représentant de chaque hub et tous les transits aux positions écran partagées. | **CONSERVER** |
| [`ReplayPlayer._draw_drone`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L140) — `def _draw_drone( self, screen: pygame.Surface, position: tuple[int, int], drone_id: int, font: pygame.font.Font, ) -> None:` | Dessine triangle, contour et ID du drone. | **CONSERVER** |
| [`ReplayPlayer.draw_overlay`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L185) — `def draw_overlay( self, screen: pygame.Surface, font: pygame.font.Font, ) -> None:` | Affiche numéro de tour, durée totale et commandes du replay. | **CONSERVER** |

### `src/view/utils/coordinate_system.py` (2 méthodes)

| Méthode et paramètres | Rôle, analyse | Décision |
|---|---|---|
| [`CoordinateSystem.__init__`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/utils/coordinate_system.py#L14) — `def __init__( self, cell_size: int = 400, ) -> None:` | Conserve cell_size pour la projection du graphe. | **CONSERVER** |
| [`CoordinateSystem.compute`](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/utils/coordinate_system.py#L21) — `def compute( self, hubs: Iterable["Hub \| HubState"], ) -> dict[str, tuple[float, float]]:` | Centre les Hub et met à l’échelle les grands graphes sans rendre les coordonnées impraticables. | **CONSERVER** |

## 3. Structures de données et classes sans méthode explicite

- `HubDict`, `ConnectionDict`, `ParsedMap` : `TypedDict` du parser, typent l’interface avant création du Graph ; pas de code exécuté dans ces classes.
- `ParseError` : erreur syntaxique, fichier, métadonnées, nombre ; levée par Parser.
- `ValidatorError` : erreur de structure et de route (doublons, zone invalide, lien inconnu, non-accessibilité) ; levée par MapValidator, **non transformée par Parser.parse**.
- `src/model/state.py` : `DroneState`, `HubState`, `ConnectionState`, `TurnState` sont quatre dataclasses `frozen=True` utilisées par Recorder et les vues. Elles n’ont pas de méthode définie explicitement ; `__init__` et `__repr__` sont générées par Python. Toutes conservées.
- `DisplayError` : exception de couche présentation, reportée à main.
- `src/view/__init__.py` : `PYGAME_HIDE_SUPPORT_PROMPT=1` est un effet volontaire de l’import pour protéger la sortie terminale.
- `if __name__ == "__main__"` : transmet correctement le retour de `main()` à `SystemExit`.

## 4. Modifications appliquées sur test-main

1. `ValidationError` renommée `ValidatorError` dans le validateur et dans les tests.
2. `Parser.parse` ne rattrape plus `ValidatorError` pour la convertir en `ParseError`. La classe valide seule ; `main.main` intercepte les deux exceptions.
3. Les variables `marker` deviennent `bracket` dans parse_hub/parse_connection ; `cap_raw` devient `capacity_raw` ; adaptation Flake8.
4. `Graph.__init__` : retrait d’une expression chaîne sans effet et repositionnement de la docstring.
5. `Makefile` : deux commandes distinctes dans `lint-strict`, afin qu’un échec de Flake8 ne soit pas masqué.
6. Tests de validateur adaptés ; fichier `tests/test_review_regressions.py` pour remontée d’erreur au CLI et seuil +2 sur le reroutage.
7. Suppression de la méthode inutilisée `Dijkstra.distance_to` et de son assertion dans le test de priorité, sans affecter les autres contrôles de ce test.
8. Workflow de contrôle sur la branche : `.github/workflows/test-main-audit.yml`.
10. `rainbow` est rendu par sept disques concentriques colorés dans `HubRenderer.draw`.
11. Module `Camera` et ses huit méthodes supprimés ; retrait des commandes de zoom/pan et des paramètres `camera`/`zoom` des renderers. La vue calcule désormais le cadrage automatique. Tests de rendu mis à jour.
12. Suppression des deux constructeurs `ConnectionError.__init__` et `HubError.__init__`. Les deux classes restent des sous-classes d'`Exception`; les appels existants fournissent toujours leurs messages.
9. `main.py` : parsing artisanal remplacé par `argparse` ; suppression de la liste `map_paths`, une seule map positionnelle, option `--no-view` sans alias, et conservation de `ValidatorError` dans les exceptions interceptées.

## 5. Limites et défauts possibles non changés sans preuve

- **Ordonnancement** : les drones se déplacent dans un ordre trié par `path_turns()`, mais une zone libérée plus tard dans le tour ne fait pas automatiquement retraiter un drone déjà passé. Effet d’optimisation, à documenter ; cas de diagnostic `docs/audit_cases/same_turn_release.txt`.
- **Terminaison** : `Simulation.simulate()` ne possède pas de détection générale d’état sans progrès. Le validateur garantit une route statique, pas un comportement sans blocage. Je ne présente pas cela comme un échec effectivement observé sur la branche.
- **Heuristique** : la décision `nouveau coût > coût initial + 2` est une approximation, pas un calcul optimal de temps d’attente. L’exclusion de `previous_zone` limite certaines possibilités de recul. Non modifiés sans test.
- **Mémoire** : Recorder mémorise tous les graphes/états à chaque tour y compris sans interface graphique ; coût non négligeable sur grandes cartes.
- **Fenêtre** : dimension initiale 0×0 utilisée avec `pygame.RESIZABLE` ; comportement SDL dépendant de la plateforme ; pas de modification aveugle.
- **Couleurs** : les noms de couleur hors palette choisie sont affichés en couleur de repli, non fidèlement.
- **Dépendance circulaire contrôlée** : `validator.py` importe les TypedDict du parser ; l’import de `MapValidator` est donc volontairement local à `Parser.parse`. Le déplacer sans extraire les types casserait le chargement.
- **Suppression de `Dijkstra.distance_to`** : aucune utilisation par l'application. L'unique assertion dédiée a été supprimée de `tests/test_submission_regressions.py` sans remplacer sa vérification. Les contrôles du choix de chemin et de la durée des simulations dans ce test sont maintenus.

## 6. Vérification et critères

Les tests ciblés et la suite complète sont lancés via le workflow GitHub Actions de `test-main` : `poetry run pytest -q`, `poetry run flake8 . --exclude=.venv`, puis `poetry run mypy` avec les drapeaux obligatoires. Les étapes doivent être vérifiées dans le run avant d’annoncer leur succès. Le terminal local de cette conversation ne peut pas résoudre github.com.

Cet audit documente le contenu de `test-main`. Exception historique : le changement `argparse` avait déjà été poussé sur `main` avant notre décision de travailler uniquement sur `test-main`. Il est maintenant aussi présent sur `test-main`, avec `ValidatorError` conservée. La mise à jour actuelle ne modifie pas `main`.

## 7. Résultats d’exécution confirmés sur GitHub Actions

Après l'intégration d’`argparse`, le [workflow d’audit réussi](https://github.com/Irohs6/fly_in_v2/actions/runs/41422135161) a exécuté `test-main` sur Python 3.13 (commit `fa548614b976c7a4ba871918c0d688e42b0297d7`) :

- **205 tests pytest réussis** (2,01 s pour la phase pytest).
- **11 cartes du dépôt terminées** sans Pygame, et toutes les sorties enregistrées sans erreur.
- Tours par carte : challenger/Impossible Dream **43**, challenger/Spaghetti **46** ; Easy **4 / 4 / 4** ; Medium **8 / 15 / 7** ; Hard **13 / 16 / 26**.
- **Flake8 réussi**.
- **Mypy réussi** avec les options obligatoires : « Success: no issues found in 36 source files ».

Ces résultats incluent la version de `main.py` avec `argparse` et `ValidatorError`. Les éditions documentaires ultérieures ne modifient pas le programme testé. Ils ne prouvent pas la terminaison pour toutes les cartes possibles.

## 8. Modification du rendu graphique — 2 novembre 2026

- **Branche :** `test-main` ; `main` n'est pas modifiée.
- **Rainbow :** sept disques concentriques rouge, orange, jaune, vert, cyan, indigo, violet ; contour et labels inchangés.
- **Caméra :** suppression de `src/view/utils/camera.py` et de ses huit méthodes. Suppression des contrôles de zoom, glisser et reset caméra.
- **Placement :** `CoordinateSystem.compute` garde son rôle de calcul des coordonnées logiques centrées ; `PygameView._display_replay` transforme celles-ci en positions écran ajustées à la taille de la fenêtre. `GraphRenderer` et `ReplayPlayer` partagent les mêmes positions.
- **Inventaire :** 83 méthodes dans 17 fichiers applicatifs (dont un fichier d'exceptions sans méthode explicite).
- **Tests :** les tests existants de rendu sont adaptés et un test vérifie les couleurs et les rayons décroissants de `rainbow`. **Vérification actuelle :** [workflow GitHub Actions réussi](https://github.com/Irohs6/fly_in_v2/actions/runs/41425411792) avec **206 tests réussis**, **11 cartes terminées**, **Flake8** et **mypy** sans erreur (35 fichiers Python vérifiés).

## 9. Simplification des exceptions — 2 novembre 2026

Sur `test-main`, les deux constructeurs `ConnectionError.__init__` et `HubError.__init__` sont supprimés. Les appels réels dans `Connection` et `Hub` fournissent tous un message ; aucun appel nu n'a été relevé dans les sources et tests. Les classes d'exceptions métier sont conservées, sans logique propre. L'inventaire descend donc de **85 à 83 méthodes explicites**. La vérification CI mentionnée plus haut précède cette dernière modification et doit être reconfirmée sur le nouveau commit.
