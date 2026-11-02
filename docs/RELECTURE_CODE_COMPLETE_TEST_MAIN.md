# Fly-in — Relecture complète du code, méthode par méthode

> **Objectif : te réapproprier le projet**, relire chaque ligne et retrouver les choix techniques. Ce n'est pas un bulletin de notes ni une proposition de refonte automatique. Les corrections décidées lors de la relecture ont été appliquées à `test-main` ; les autres idées restent des questions à trancher.

**Source exacte :** branche [`test-main`](https://github.com/Irohs6/fly_in_v2/tree/test-main), état du 2 novembre 2026 après suppression de `Camera` et ajout du rendu `rainbow`. **83 méthodes/fonctions explicites dans 17 fichiers applicatifs.** Les structures sans méthode explicite et classes d'erreurs sont présentées à part.

## Comment lire le document

Pour **chacune** des 83 méthodes : tu disposes du **code relevé sur la branche après modifications**, du fichier GitHub d'origine et de la ligne, d'une explication des paramètres/variables et des décisions à discuter. L'ordre suit un **parcours des appels depuis `main()`** : quand une méthode appelle une autre méthode du projet, on descend dans l'appel ; quand elle est déjà étudiée, on ne reproduit pas une deuxième fois son code. Les chemins alternatifs (déclarations de carte, transit restricted, reroutage, événements Pygame) sont placés à la suite de leur point d'entrée. Les méthodes implicites `__str__`, `__repr__` et les exceptions sont à la fin. **Ce n'est pas un ordre chronologique unique valable pour toutes les cartes**, car le flux dépend de l'entrée, des capacités et des événements utilisateur.

**À bien distinguer :** `ParseError` = erreur de lecture/syntaxe ; `ValidatorError` = carte syntaxiquement lisible mais structurellement invalide ; `HubError`/`ConnectionError` = invariants du modèle ; `DisplayError` = interface. `main` capte les erreurs attendues.

## Sommaire — accès direct aux méthodes

### I. Entrée, arguments, contrôleur et lecture de carte
- [01 — `main`](#m001)
- [02 — `Controller.__init__`](#m002)
- [03 — `Controller.run`](#m003)
- [04 — `Parser.__init__`](#m004)
- [05 — `Parser.parse`](#m005)
- [06 — `Parser.read_file`](#m006)
- [07 — `Parser.parse_line`](#m007)
- [08 — `Parser._parse_integer`](#m008)
- [09 — `Parser.parse_hub`](#m009)
- [10 — `Parser.parse_metadata`](#m010)
- [11 — `Parser.parse_connection`](#m011)

### II. Validation sémantique de la carte
- [12 — `MapValidator.__init__`](#m012)
- [13 — `MapValidator.validate`](#m013)
- [14 — `MapValidator._check_zone_types`](#m014)
- [15 — `MapValidator._check_unique_hub_names`](#m015)
- [16 — `MapValidator._check_connection_endpoints`](#m016)
- [17 — `MapValidator._check_duplicate_connections`](#m017)
- [18 — `MapValidator._check_reachable_end`](#m018)

### III. Construction du graphe
- [19 — `Graph.__init__`](#m019)
- [20 — `Hub.__init__`](#m020)
- [21 — `Graph._build_connections`](#m021)
- [22 — `Connection.__init__`](#m022)
- [23 — `Graph._index_connection`](#m023)

### IV. Préparation de la simulation et calcul du chemin initial
- [24 — `Simulation.__init__`](#m024)
- [25 — `Dijkstra.__init__`](#m025)
- [26 — `Recorder.__init__`](#m026)
- [27 — `Simulation.load_drones`](#m027)
- [28 — `Dijkstra.shortest_path`](#m028)
- [29 — `Dijkstra.shortest_distances`](#m029)
- [30 — `Graph.get_connections`](#m030)
- [31 — `Connection.get_other_hub`](#m031)
- [32 — `Hub.move_cost`](#m032)
- [33 — `Hub.transit_duration`](#m033)
- [34 — `Drone.__init__`](#m034)
- [35 — `Drone.set_path`](#m035)
- [36 — `Hub.add_drone`](#m036)
- [37 — `Hub.is_available`](#m037)
- [38 — `Recorder.record`](#m038)

### V. Boucle des tours, mouvement, transit et reroutage
- [39 — `Simulation.simulate`](#m039)
- [40 — `Simulation._all_drones_delivered`](#m040)
- [41 — `Simulation._prepare_connections_for_turn`](#m041)
- [42 — `Drone.path_turns`](#m042)
- [43 — `Simulation._advance_drone`](#m043)
- [44 — `Simulation._move_or_wait`](#m044)
- [45 — `Graph.get_connection`](#m045)
- [46 — `Connection.is_available`](#m046)
- [47 — `Simulation.move_drone`](#m047)
- [48 — `Hub.remove_drone`](#m048)
- [49 — `Drone.move_to_zone`](#m049)
- [50 — `Drone.begin_transit`](#m050)
- [51 — `Hub.reserve`](#m051)
- [52 — `Connection.use_capacity`](#m052)
- [53 — `Simulation._reroute_drone`](#m053)
- [54 — `Drone.wait`](#m054)
- [55 — `Drone.advance_transit`](#m055)
- [56 — `Hub.release_reservation`](#m056)
- [57 — `Drone.deliver`](#m057)

### VI. Sortie terminal et affichage Pygame
- [58 — `TerminalView.display`](#m058)
- [59 — `PygameView.__init__`](#m059)
- [60 — `PygameView.display`](#m060)
- [61 — `PygameView._display_replay`](#m061)
- [62 — `CoordinateSystem.__init__`](#m062)
- [63 — `CoordinateSystem.compute`](#m063)
- [64 — `GraphRenderer.__init__`](#m064)
- [65 — `HubRenderer.__init__`](#m065)
- [66 — `ConnectionRenderer.__init__`](#m066)
- [67 — `ReplayPlayer.__init__`](#m067)
- [68 — `ReplayPlayer.handle_event`](#m068)
- [69 — `ReplayPlayer.next_turn`](#m069)
- [70 — `ReplayPlayer.previous_turn`](#m070)
- [71 — `ReplayPlayer.restart`](#m071)
- [72 — `GraphRenderer.draw`](#m072)
- [73 — `ConnectionRenderer.draw`](#m073)
- [74 — `HubRenderer.draw`](#m074)
- [75 — `HubRenderer.radius`](#m075)
- [76 — `ReplayPlayer.draw`](#m076)
- [77 — `ReplayPlayer._state_position`](#m077)
- [78 — `ReplayPlayer._draw_drone`](#m078)
- [79 — `ReplayPlayer._drone_color`](#m079)
- [80 — `ReplayPlayer.draw_overlay`](#m080)

### VII. Méthodes spéciales et exceptions non déclenchées par le chemin nominal
- [81 — `Connection.__repr__`](#m081)
- [82 — `Hub.__str__`](#m082)
- [83 — `Hub.__repr__`](#m083)

## Schéma du parcours principal

```text
main
 └─ Controller.run
    ├─ Parser.parse
    │  ├─ read_file → parse_line
    │  │  ├─ _parse_integer
    │  │  ├─ parse_hub → _parse_integer → parse_metadata
    │  │  └─ parse_connection → parse_metadata → _parse_integer
    │  └─ MapValidator.validate → 5 vérifications
    ├─ Graph.__init__ → Hub / Connection / index
    ├─ Simulation.load_drones → Dijkstra.shortest_path → shortest_distances
    ├─ Simulation.simulate (tours)
    │  ├─ _prepare_connections_for_turn
    │  ├─ _advance_drone → _move_or_wait
    │  │  ├─ move_drone → Hub / Drone / Connection
    │  │  └─ _reroute_drone → Dijkstra (si obstacle)
    │  ├─ Drone.advance_transit (si restricted)
    │  └─ Recorder.record → TurnState
    ├─ TerminalView.display
    └─ PygameView.display (si mode graphique)
       └─ _display_replay → CoordinateSystem /
                            GraphRenderer / ReplayPlayer
```


---

## I. Entrée, arguments, contrôleur et lecture de carte

<a id="m001"></a>

### 01 — `main`

**Source :** [`main.py`, ligne 10](https://github.com/Irohs6/fly_in_v2/blob/test-main/main.py#L10)

```python
def main() -> int:
    """Parse command-line options and run the requested simulation mode."""
    parser = argparse.ArgumentParser(
        description="Run a Fly-in drone simulation."
    )
    parser.add_argument(
        "map_path",
        nargs="?",
        default="assets/maps/easy/02_simple_fork.txt",
        help="Path to the map file.",
    )
    parser.add_argument(
        "--no-view",
        dest="view_active",
        action="store_false",
        help="Print movements without graphical replay.",
    )
    arguments = parser.parse_args()

    try:
        controller = Controller(map_path=arguments.map_path)
        controller.run(view_active=arguments.view_active)
    except (OSError, ParseError, ValidatorError, DisplayError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Simulation interrupted.", file=sys.stderr)
        return 130

    return 0

```

**Lecture du code.** `argparse.ArgumentParser` gère maintenant les arguments CLI. Le positionnel `map_path` (avec `nargs="?"`) accepte zéro ou **un** chemin ; sans argument, la carte par défaut est choisie. `parser.parse_args()` gère automatiquement `-h/--help`, les options inconnues et les arguments en trop. `--no-view` met `view_active` à `False` via `store_false`. Le contrôleur lance la simulation. Les erreurs de lecture, parsing, validation et affichage produisent une seule ligne sur `stderr` avec retour `1` ; `KeyboardInterrupt` renvoie `130`. Les erreurs d'arguments sont gérées par `argparse` avec sortie `2` (et `SystemExit`), l'aide avec sortie `0`.

**Variables, noms et cohérence.** `map_paths` a été supprimée : une liste n'était pas justifiée pour une seule map. `arguments.map_path` est un `str` transmis tel quel à `Controller` ; `arguments.view_active` contrôle l'ouverture de Pygame. L'import `ValidatorError` et son interception restent voulus : `Parser.parse()` ne convertit plus cette erreur en `ParseError`.

**Décision prise sur `test-main`.** Conserver `argparse` et la seule map positionnelle. Utiliser exclusivement `--no-view` : le code, les tests et les commandes du README sont maintenant alignés, sans alias. Éviter tout nouveau changement direct sur `main` avant la fusion finale.

<a id="m002"></a>

### 02 — `Controller.__init__`

**Source :** [`src/controller/controller.py`, ligne 11](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/controller/controller.py#L11)

```python
    def __init__(self, map_path: str) -> None:
        """Store the map path without starting the simulation."""
        self.map_path = map_path
```

**Lecture du code.** Accepte **un seul paramètre `map_path: str`** en plus de `self` et le stocke. Ne lit ni carte ni interface : créer un contrôleur n'exécute rien. C'est ce que contrôle un test de construction sans effet de bord.

**Variables, noms et cohérence.** Le nom `map_path` est cohérent entre `main`, `Controller` et `Parser`. Le `str | Path` superflu a déjà été éliminé ; aucun retour nécessaire vers `Path`.

**Décision à prendre.** Conserver. Un constructeur court est une bonne chose ici.

<a id="m003"></a>

### 03 — `Controller.run`

**Source :** [`src/controller/controller.py`, ligne 15](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/controller/controller.py#L15)

```python
    def run(self, *, view_active: bool = True) -> None:
        """Simulate the map and display the results."""
        parser = Parser(self.map_path)
        data = parser.parse()

        graph = Graph(data)
        simulation = Simulation(graph)
        simulation.load_drones(data["nb_drones"])
        frames = simulation.simulate()

        TerminalView().display(frames)

        if view_active:
            try:
                from src.view.pygame_view import PygameView
            except ImportError as exc:
                raise DisplayError(
                    f"Cannot load graphical replay: {exc}. "
                    "Run 'poetry install' or use --no-view."
                ) from exc

            view = PygameView(frames)
            view.display()
```

**Lecture du code.** Instancie `Parser`, récupère un `ParsedMap`, crée `Graph`, prépare une `Simulation`, charge le nombre de drones, lance tous les tours, puis affiche d'abord la sortie texte. L'import de `PygameView` est **volontairement retardé** jusqu'à l'option graphique, afin que le mode terminal n'exige pas le module Pygame. Si l'import échoue, un `DisplayError` clair est levé.

**Variables, noms et cohérence.** `data` est un dictionnaire typé mais son nom est générique : `map_data` ou `parsed_map` aiderait à se relire. `frames` désigne des instantanés de simulation, pas des images Pygame : `turn_states` serait plus explicite. `view_active` est un booléen à argument nommé (`*`) ; cela évite l'appel ambigu `run(False)`.

**Décision à prendre.** À discuter : noms `data`/`frames`, pas une nouvelle couche d'abstraction. Remarque : si Pygame échoue, le terminal a déjà été imprimé, c'est un choix d'ordre explicite.

<a id="m004"></a>

### 04 — `Parser.__init__`

**Source :** [`src/parser/parser.py`, ligne 42](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L42)

```python
    def __init__(self, map_path: str):
        """Store the file path and initialize parser state without reading
        it.
        """
        self.map_path = map_path
        self.line_count = 0
        self.hub_entries: list[tuple[HubDict, int]] = []
        self.connection_entries: list[tuple[ConnectionDict, int]] = []
        self.nb_drones: int | None = None
        self.start_hub: HubDict | None = None
        self.end_hub: HubDict | None = None
```

**Lecture du code.** Prépare `map_path`, `line_count`, deux listes de couples **(déclaration, ligne physique)** et trois valeurs encore inconnues (`nb_drones`, `start_hub`, `end_hub`). `None` signifie « pas encore déclaré », distinct de zéro ou d'une donnée invalide.

**Variables, noms et cohérence.** `hub_entries` et `connection_entries` conservent les lignes pour que `MapValidator` puisse pointer les erreurs. Le nom `line_count` indique un nombre total de lignes, pas « prochaine ligne », et il est remis à zéro à la lecture. L'annotation `map_path: str` suffit.

**Décision à prendre.** Conserver ; ne pas confondre `HubDict` (données lues) et `Hub` (objet du modèle).

<a id="m005"></a>

### 05 — `Parser.parse`

**Source :** [`src/parser/parser.py`, ligne 269](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L269)

```python
    def parse(self) -> ParsedMap:
        """Read, parse and validate a complete map."""
        from src.parser.validator import MapValidator

        # New lists preserve the results of a previous parse.
        self.hub_entries = []
        self.connection_entries = []
        self.nb_drones = None
        self.start_hub = None
        self.end_hub = None
        self.read_file()
        if self.nb_drones is None:
            raise ParseError(
                f"Line {self.line_count + 1}: "
                "missing nb_drones at end of file."
            )

        if self.start_hub is None:
            raise ParseError(
                f"Line {self.line_count + 1}:"
                " missing start_hub at end of file."
            )

        if self.end_hub is None:
            raise ParseError(
                f"Line {self.line_count + 1}:"
                " missing end_hub at end of file."
            )

        validator = MapValidator(
            start_hub=self.start_hub,
            end_hub=self.end_hub,
            hub_entries=self.hub_entries,
            connection_entries=self.connection_entries,
        )

        validator.validate()

        return {
            "map_path": self.map_path,
            "nb_drones": self.nb_drones,
            "start_hub": self.start_hub,
            "hubs": [
                hub for hub, _ in self.hub_entries
                if hub is not self.start_hub and hub is not self.end_hub
            ],
            "end_hub": self.end_hub,
            "connections": [
                connection for connection, _ in self.connection_entries
            ],
        }
```

**Lecture du code.** Réinitialise cinq champs avant la lecture : le **même objet Parser peut relire un fichier modifié** sans réutiliser les anciens hubs. Appelle `read_file`, vérifie que le fichier annonce drones, départ et arrivée, puis construit et appelle `MapValidator`. Il n'attrape pas `ValidatorError` : cette erreur remonte désormais directement à `main`. Le dictionnaire retourné contient start/end séparément et les autres hubs dans `hubs`.

**Variables, noms et cohérence.** Le commentaire « New lists preserve the results of a previous parse » mérite explication : on affecte de **nouvelles listes**, on ne vide pas les anciennes en place. Dans le `return`, `hub is not self.start_hub` teste l'identité du dictionnaire pour retirer les deux terminaux, et non une égalité de nom. L'import local `MapValidator` évite la dépendance circulaire `validator.py` → `parser.py`.

**Décision à prendre.** À discuter : mieux séparer les TypedDict dans un module `types` pour faire l'import en tête ? Pas indispensable ; créer un fichier uniquement pour cela peut être du sur-design.

<a id="m006"></a>

### 06 — `Parser.read_file`

**Source :** [`src/parser/parser.py`, ligne 55](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L55)

```python
    def read_file(self) -> None:
        """Read and parse a UTF-8 map one line at a time.
        Skip empty lines and comment-only lines.
        Preserve physical line numbers and the total line count. Wrap
        read or decoding failures in ParseError with the file path.
        """
        self.line_count = 0
        try:
            with open(self.map_path, "r", encoding="utf-8") as maps_file:
                for line_number, raw in enumerate(maps_file, start=1):
                    self.line_count = line_number
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    self.parse_line(line, line_number)
        except UnicodeDecodeError as error:
            raise ParseError(
                f"Map {self.map_path!r}: invalid UTF-8 encoding."
            ) from error
        except OSError as error:
            raise ParseError(
                f"Cannot read map {self.map_path!r}: "
                f"{error.strerror or str(error)}"
            ) from error
```

**Lecture du code.** Ouvre le fichier avec `encoding='utf-8'`, fait `enumerate(..., start=1)` et conserve les **vrais numéros de lignes**, y compris commentaires et lignes vides. `strip()` enlève les espaces extérieurs ; un commentaire n'est ignoré que si la ligne commence par `#` après nettoyage. Appelle `parse_line` sur chaque déclaration. Les erreurs UTF-8 et lecture système sont contextualisées avec le chemin.

**Variables, noms et cohérence.** `raw` est ici la ligne physique brute, puis `line` la ligne nettoyée. `maps_file` pourrait être `map_file` au singulier. Les commentaires **en fin de ligne** ne sont pas traités comme commentaires : à vérifier par rapport au sujet, pas à modifier sans accord.

**Décision à prendre.** À discuter : garder `read_file` comme méthode séparée de `parse` (utile pour la séparation lecture/syntaxe).

<a id="m007"></a>

### 07 — `Parser.parse_line`

**Source :** [`src/parser/parser.py`, ligne 322](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L322)

```python
    def parse_line(self, line: str, line_number: int) -> None:
        """Parse one declaration, requiring the drone count before any hub
        or connection. Report invalid syntax with its physical line number.
        """
        if line.count(":") != 1:
            raise ParseError(
                f"Line {line_number}: invalid line: {line!r}. "
                "Expected exactly one ':'."
            )
        keyword, _, raw = line.partition(":")
        keyword = keyword.strip()
        raw = raw.strip()
        if (
            self.nb_drones is None
            and keyword not in ("nb_drones", "drones", "nb_drone")
        ):
            raise ParseError(
                f"Line {line_number}: the first line must define "
                "nb_drones: <positive integer>."
            )

        if not raw:
            raise ParseError(
                f"Line {line_number}: invalid line: {line!r}. "
                "Expected format: <keyword>: <value>."
            )

        if keyword in ("nb_drones", "drones", "nb_drone"):
            if self.nb_drones is not None:
                raise ParseError(
                    f"Line {line_number}: nb_drones is already defined."
                )
            self.nb_drones = self._parse_integer(
                raw, line_number, "nb_drones", positive=True,
            )
        elif keyword in ("start_hub", "hub", "end_hub"):
            self.parse_hub(keyword, raw, line_number)
        elif keyword == "connection":
            self.parse_connection(raw, line_number)
        else:
            raise ParseError(
                f"Line {line_number}: unknown declaration: {line!r}"
            )
```

**Lecture du code.** Vérifie qu'il y a **exactement un `:`** ; `partition(':')` sépare mot-clé et valeur, puis `strip()` enlève les espaces. Tant que `nb_drones` n'est pas présent, aucune autre déclaration n'est acceptée. Le nombre de drones passe par `_parse_integer`; les zones par `parse_hub`; les connexions par `parse_connection`; tout autre mot-clé lève `ParseError`.

**Variables, noms et cohérence.** Le `_` est le séparateur renvoyé par `partition`, volontairement inutilisé puisqu'il est déjà validé par `count`. Les alias `drones` et `nb_drone` coexistent avec `nb_drones` : bonne compatibilité, mais à confronter au sujet si l'on préfère une grammaire stricte.

**Décision à prendre.** À discuter : le choix d'autoriser des alias et l'usage de la chaîne littérale `nb_drones` à plusieurs endroits.

<a id="m008"></a>

### 08 — `Parser._parse_integer`

**Source :** [`src/parser/parser.py`, ligne 245](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L245)

```python
    @staticmethod
    def _parse_integer(
        raw: str,
        line_number: int,
        field: str,
        *,
        positive: bool = False,
```

**Lecture du code.** `@staticmethod` car n'utilise aucun état de `Parser`. Construit une expression régulière pour entier signé ou chiffres uniquement si `positive=True`; renvoie un vrai `int`. La vérification `value <= 0` rejette explicitement zéro en mode positif. Une valeur mal formée déclenche `ParseError` avec champ et numéro de ligne.

**Variables, noms et cohérence.** `pattern`, `error_message` et `raw` sont explicites. Le `try/except ValueError` après `re.fullmatch` n'est **pas nécessaire pour les petites entrées normales**, mais peut traiter le refus de Python de convertir un entier gigantesque ; le supprimer rendrait cette erreur moins contextualisée. Ici, le `return` fournit un entier, jamais `None`.

**Décision à prendre.** Conserver le contrat, discuter seulement si l'on veut simplifier au détriment des diagnostics extrêmes.

<a id="m009"></a>

### 09 — `Parser.parse_hub`

**Source :** [`src/parser/parser.py`, ligne 81](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L81)

```python
    def parse_hub(
        self,
        hub_type: str,
        raw: str,
        line_number: int,
```

**Lecture du code.** Refuse plusieurs start/end. `partition('[')` sépare les trois champs `name x y` des métadonnées ; l'appel `parse_metadata` contrôle crochets, clés et valeurs. Deux appels à `_parse_integer` lisent les coordonnées ; `capacity` par défaut vaut 1 sauf **start/end à capacité infinie**. Le dictionnaire final garde nom, position, couleur, capacité et type de zone, et est ajouté avec sa ligne.

**Variables, noms et cohérence.** `hub_type` signifie ici **type de déclaration** (`start_hub`, `hub`, `end_hub`) alors que `zone_type` signifie **nature de zone** (`normal`, `restricted`, etc.) : attention au mot « type » employé pour deux choses. `zone_raw`, `bracket`, `meta_raw`, `capacity_raw` sont des noms liés au parsing. Les métadonnées `max_drones` et `capacity` sont deux alias, refusés ensemble.

**Décision à prendre.** À discuter : `hub_type` → `declaration_type`, `zone_raw` → `hub_fields` ; décider si une capacité malformée sur start/end doit être signalée au lieu d'être ignorée puisque l'infini s'impose.

<a id="m010"></a>

### 10 — `Parser.parse_metadata`

**Source :** [`src/parser/parser.py`, ligne 202](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L202)

```python
    @staticmethod
    def parse_metadata(
        raw: str,
        line_number: int,
        allowed_keys: set[str],
```

**Lecture du code.** Si `raw` est vide, renvoie `{}`. Sinon exige une paire unique de crochets englobants, découpe les éléments par espaces, exige **un seul `=`**, une clé/valeur non vide, une clé autorisée et aucune clé répétée ; renvoie `dict[str, str]` sans convertir les nombres (responsabilité des parsers spécialisés).

**Variables, noms et cohérence.** `meta_raw` est le contenu avec ses crochets, puis `meta` le dictionnaire de paires. `allowed_keys` est un ensemble passé par l'appelant, donc la méthode ne connaît pas les règles propres à un hub ou une connexion. L'exception est `ParseError`, pas `ValidatorError`, car il s'agit de syntaxe.

**Décision à prendre.** À discuter : renommer `raw` → `raw_metadata`, `meta` → `metadata` pour une lecture plus uniforme.

<a id="m011"></a>

### 11 — `Parser.parse_connection`

**Source :** [`src/parser/parser.py`, ligne 153](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/parser.py#L153)

```python
    def parse_connection(self, raw: str, line_number: int) -> None:
        """Parse a connection declaration and its metadata."""

        edge_raw, bracket, meta_raw = raw.partition("[")
        edge = edge_raw.strip()

        if edge.count("-") != 1:
            raise ParseError(
                f"Line {line_number}: invalid connection: {raw!r}. "
                "Expected format: <source>-<target> [meta]"
            )

        source, target = edge.split("-", 1)
        source = source.strip()
        target = target.strip()

        if (
            not source or not target
            or any(char.isspace() for char in source + target)
        ):
            raise ParseError(
                f"Line {line_number}: invalid connection: {raw!r}."
            )

        meta = self.parse_metadata(
            bracket + meta_raw,
            line_number,
            {"capacity", "max_link_capacity"},
        )
        if "max_link_capacity" in meta and "capacity" in meta:
            raise ParseError(
                f"Line {line_number}: duplicate metadata: "
                "capacity is already defined."
            )
        capacity_raw = (
            meta.get("max_link_capacity") or meta.get("capacity") or "1"
        )
        capacity = self._parse_integer(
            capacity_raw, line_number, "capacity", positive=True,
        )

        connection: ConnectionDict = {
            "source": source,
            "target": target,
            "capacity": capacity,
        }
        self.connection_entries.append((connection, line_number))
```

**Lecture du code.** Découpe `source-target` et les métadonnées éventuelles, exige un seul tiret, enlève les espaces aux extrémités, refuse les noms vides/avec espaces internes. `parse_metadata` autorise `capacity` ou `max_link_capacity` ; les deux ensemble sont refusés ; la capacité est un entier strictement positif ou 1 par défaut. Enregistre le dictionnaire et la ligne source.

**Variables, noms et cohérence.** `edge_raw`, `edge`, `source`, `target`, `bracket`, `meta_raw`, `capacity_raw` sont les valeurs intermédiaires. `edge` est le nom générique anglais d'une connexion ; ailleurs le projet dit `connection`. `edge_raw` → `connection_raw` serait plus cohérent, ou adopter « edge » partout.

**Décision à prendre.** À discuter : conserver `connection` comme vocabulaire unique et éventuellement retirer `edge`.


---

## II. Validation sémantique de la carte

<a id="m012"></a>

### 12 — `MapValidator.__init__`

**Source :** [`src/parser/validator.py`, ligne 18](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L18)

```python
    def __init__(
        self,
        start_hub: HubDict,
        end_hub: HubDict,
        hub_entries: list[tuple[HubDict, int]],
        connection_entries: list[tuple[ConnectionDict, int]],
```

**Lecture du code.** Reçoit start/end et toutes les déclarations avec leurs lignes, déjà passées par l'analyse syntaxique. Stocke les objets sans recopier les listes. Le validateur s'occupe de **cohérence**, pas de lire ou convertir les valeurs.

**Variables, noms et cohérence.** À l'appel, `hub_entries` contient aussi les terminaux. L'annotation `tuple[HubDict, int]` est importante pour les messages d'erreur, pas décorative.

**Décision à prendre.** Conserver. Le nom `MapValidator` décrit bien la responsabilité.

<a id="m013"></a>

### 13 — `MapValidator.validate`

**Source :** [`src/parser/validator.py`, ligne 35](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L35)

```python
    def validate(self) -> None:
        """Validate the consistency of parsed map data."""
        self._check_zone_types()
        self._check_unique_hub_names()
        self._check_connection_endpoints()
        self._check_duplicate_connections()
        self._check_reachable_end()
```

**Lecture du code.** Exécute successivement les cinq contrôles : types, noms, références, doublons de connexions, accessibilité. **L'ordre détermine quelle erreur sort en premier** quand plusieurs erreurs sont présentes. Ne renvoie aucune valeur, l'absence d'exception signifie réussite.

**Variables, noms et cohérence.** Le terme `validate()` est standard pour une méthode qui lève en cas d'échec. Les méthodes privées sont spécialisées, évitant une grosse fonction monolithique. `ValidatorError` est directement récupérée par `main`.

**Décision à prendre.** Conserver cette orchestration.

<a id="m014"></a>

### 14 — `MapValidator._check_zone_types`

**Source :** [`src/parser/validator.py`, ligne 43](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L43)

```python
    def _check_zone_types(self) -> None:
        """Require a supported zone type for every hub."""
        for hub, line in self.hub_entries:
            zone_type = hub["zone_type"]
            if zone_type not in self.VALID_ZONE_TYPES:
                raise ValidatorError(
                    f"Line {line}: invalid zone type '{zone_type}' "
                    f"for hub {hub['name']!r}"
                )
```

**Lecture du code.** Parcourt toutes les zones (départ et arrivée inclus), vérifie `zone_type` dans `VALID_ZONE_TYPES`. Une valeur non reconnue entraîne `ValidatorError` avec la ligne et le nom de la zone.

**Variables, noms et cohérence.** `zone_type` est cohérent avec le champ du dictionnaire ; le nom `_check_zone_types` annonce précisément le contrôle. Ici, `line` est un entier de ligne et non du texte.

**Décision à prendre.** Conserver.

<a id="m015"></a>

### 15 — `MapValidator._check_unique_hub_names`

**Source :** [`src/parser/validator.py`, ligne 53](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L53)

```python
    def _check_unique_hub_names(self) -> None:
        """Reject duplicate hub names and report their declaration lines."""
        names: dict[str, int] = {}
        for hub, line in self.hub_entries:
            name = hub["name"]
            if name in names:
                first_line = names[name]
                raise ValidatorError(
                    f"Line {line}: duplicate hub name: {name!r} "
                    f"(already defined on line {first_line})"
                )
            names[name] = line
```

**Lecture du code.** Maintient un dictionnaire `names: nom -> première ligne`. Si le même nom revient, la deuxième ligne et la première sont mentionnées dans l'erreur. Ne fait pas de conversion ni de tri.

**Variables, noms et cohérence.** `names` peut être lu comme un ensemble, pourtant contient des **numéros de ligne** : `hub_name_lines` serait plus descriptif. `first_line` est déjà explicite.

**Décision à prendre.** À discuter : renommer la variable locale uniquement.

<a id="m016"></a>

### 16 — `MapValidator._check_connection_endpoints`

**Source :** [`src/parser/validator.py`, ligne 66](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L66)

```python
    def _check_connection_endpoints(self) -> None:
        """Verify that each endpoint exists and precedes its connection.
        Raise ValidatorError for unknown hubs or late declarations.
        """
        definition_lines = {
            hub["name"]: line for hub, line in self.hub_entries
        }
        for connection, line in self.connection_entries:
            for endpoint in (connection["source"], connection["target"]):
                if endpoint not in definition_lines:
                    raise ValidatorError(
                        f"Line {line}: connection references unknown hub: "
                        f"{endpoint!r}"
                    )
                if definition_lines[endpoint] >= line:
                    raise ValidatorError(
                        f"Line {line}: hub {endpoint!r} not yet defined "
                        f"(defined on line {definition_lines[endpoint]})."
                    )
```

**Lecture du code.** Prépare `definition_lines` (nom de zone → ligne). Pour chaque connexion, vérifie que `source` et `target` existent et ont été déclarés **avant** la connexion. Un hub déclaré plus tard est donc refusé, même si son nom apparaît finalement dans la carte.

**Variables, noms et cohérence.** `endpoint` est un terme de graphe correct mais peut être remplacé par `hub_name` pour la cohérence Hub. `definition_lines` reflète bien le rôle réel. Cette exigence de déclaration avant usage mérite d'être comparée au sujet si tu hésites.

**Décision à prendre.** À discuter : vocabulaire `endpoint`/`hub_name` ; l'ordre de déclaration est une règle fonctionnelle, pas une préférence esthétique.

<a id="m017"></a>

### 17 — `MapValidator._check_duplicate_connections`

**Source :** [`src/parser/validator.py`, ligne 86](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L86)

```python
    def _check_duplicate_connections(self) -> None:
        """Reject duplicate connections, including reversed endpoint pairs."""
        checked_conn: dict[tuple[str, str], int] = {}

        for connection, line in self.connection_entries:
            source = connection["source"]
            target = connection["target"]

            if source < target:
                pair = (source, target)
            else:
                pair = (target, source)

            if pair in checked_conn:
                first_line = checked_conn[pair]

                raise ValidatorError(
                    f"Line {line}: "
                    f"Duplicate connection between "
                    f"{pair[0]} and {pair[1]} "
                    f"(already defined on line "
                    f"{first_line})"
                )

            checked_conn[pair] = line
```

**Lecture du code.** Pour chaque lien, construit un couple de noms ordonné alphabétiquement afin de traiter `A-B` et `B-A` comme **la même connexion**. `checked_conn` mémorise la première ligne. La répétition lève `ValidatorError`.

**Variables, noms et cohérence.** `checked_conn` est une abréviation qui cache que la valeur est une ligne : `connection_lines` serait plus clair. La condition `source < target` normalise le couple mais ne vérifie pas à elle seule un auto-lien `A-A`.

**Décision à prendre.** À discuter : remplacer `checked_conn` ; déterminer si les connexions d'une zone à elle-même doivent être explicitement rejetées.

<a id="m018"></a>

### 18 — `MapValidator._check_reachable_end`

**Source :** [`src/parser/validator.py`, ligne 112](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/parser/validator.py#L112)

```python
    def _check_reachable_end(self) -> None:
        """Use BFS to check that start can reach end without blocked hubs."""
        adjacency: dict[str, list[str]] = {
            hub["name"]: []
            for hub, _ in self.hub_entries
            if hub["zone_type"] != "blocked"
        }

        for connection, _ in self.connection_entries:
            source = connection["source"]
            target = connection["target"]
            if source in adjacency and target in adjacency:
                adjacency[source].append(target)
                adjacency[target].append(source)

        start = self.start_hub["name"]
        end = self.end_hub["name"]
        queue: deque[str] = deque()
        visited: set[str] = set()
        if start in adjacency:
            queue.append(start)
            visited.add(start)

        while queue:
            current = queue.popleft()
            if current == end:
                return
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        end_line = next(
            line for hub, line in self.hub_entries
            if hub is self.end_hub
        )
        raise ValidatorError(
            f"Line {end_line}: no traversable path "
            f"between {start!r} and {end!r} (blocked hubs excluded)."
        )
```

**Lecture du code.** Construit une table d'adjacence excluant les zones `blocked`, puis y ajoute les connexions dont les deux extrémités restent accessibles. Démarre une **BFS** avec `deque`, visite les voisins et retourne immédiatement si elle atteint end. Sinon, récupère le numéro de ligne de end et lève `ValidatorError`.

**Variables, noms et cohérence.** `queue` et `visited` ont des rôles classiques en BFS. `adjacency` est temporaire et contient **des noms**, contrairement à `Graph.adjacency` qui contient des objets Connection : même nom, représentation différente. Le BFS prouve seulement l'existence d'un chemin statique, pas l'absence de congestion ou de blocage pendant la simulation.

**Décision à prendre.** À discuter : une classe `Graph` intermédiaire serait de la duplication ; ce petit BFS de validation reste justifié.


---

## III. Construction du graphe

<a id="m019"></a>

### 19 — `Graph.__init__`

**Source :** [`src/model/graph.py`, ligne 9](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L9)

```python
    def __init__(self, data: ParsedMap) -> None:
        """Build hubs and their indexes from validated map data."""
        # Hub and connection storage
        self.hubs: dict[str, Hub] = {
            hub["name"]: Hub(**hub) for hub in data["hubs"]
        }

        # Start and end hubs
        self.start_hub: Hub = (
            Hub(**data["start_hub"])
        )
        self.end_hub: Hub = (
            Hub(**data["end_hub"])
        )

        self.hubs[self.start_hub.name] = self.start_hub
        self.hubs[self.end_hub.name] = self.end_hub

        self.connections = self._build_connections(data["connections"])

        # Adjacency
        self.adjacency: dict[str, list[Connection]] = defaultdict(list)
        self.connection_map: dict[tuple[Hub, Hub], Connection] = {}

        for connection in self.connections:
            self._index_connection(connection)
```

**Lecture du code.** Transforme chaque dictionnaire `HubDict` en `Hub(**hub)`, crée ensuite les objets start/end, les ajoute au même dictionnaire `self.hubs`. `_build_connections` crée les `Connection`. Enfin, `adjacency` associe un nom à ses liens et `connection_map` associe deux objets Hub à un même lien, indexé dans les deux sens.

**Variables, noms et cohérence.** `data` pourrait être `parsed_map`. `self.hubs` inclut aussi les terminaux après construction. `self.connections` est une liste ; `connection_map` permet la recherche rapide, `adjacency` fournit les voisins. Les trois structures ne sont pas automatiquement du doublon inutile : elles servent à des accès différents.

**Décision à prendre.** À discuter : simplifier `Hub(**data['start_hub'])` sur plusieurs lignes, et fixer le vocabulaire `hub`/`zone` dans le projet.

<a id="m020"></a>

### 20 — `Hub.__init__`

**Source :** [`src/model/hub.py`, ligne 6](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L6)

```python
    def __init__(self, name: str, color: str = "white",
                 zone_type: str = "normal", capacity: int | float = 1,
                 x: int = 0, y: int = 0) -> None:

        """Initialize hub properties with no occupants or reservations."""
        self.name = name
        self.color = color
        self.zone_type = zone_type
        self.capacity = capacity
        self.x = x
        self.y = y
        self.nb_drones = 0
        self.reserved = 0
```

**Lecture du code.** Reçoit identité, couleur, nature de zone, capacité, coordonnées, puis initialise `nb_drones=0` et `reserved=0`. Les valeurs viennent du parser ; une zone `blocked` reste constructible mais ne sera pas traversable via le pathfinder.

**Variables, noms et cohérence.** `nb_drones` est un compteur, `reserved` est un **nombre de places déjà promises** à des drones en transit. Les noms sont incohérents entre `nb_drones` et `reserved` (l'un parle de drones, l'autre non). `reserved_slots` ou `reserved_drones` serait plus parlant. Les deux sont utilisés dans `is_available`.

**Décision à prendre.** À discuter : harmoniser noms et langue, sans confondre `nb_drones` du fichier (effectif total) et `nb_drones` d'une zone (occupants).

<a id="m021"></a>

### 21 — `Graph._build_connections`

**Source :** [`src/model/graph.py`, ligne 36](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L36)

```python
    def _build_connections(
        self,
        raw_connections: list[ConnectionDict],
```

**Lecture du code.** Transforme la liste de dictionnaires de connexion en objets `Connection`, en retrouvant les deux références `Hub` depuis `self.hubs`. Le validateur garantit que les noms existent. Retourne une liste d'objets sans enregistrer leur adjacence.

**Variables, noms et cohérence.** `raw_connections` est trompeur : les valeurs sont **déjà analysées et validées**, pas des chaînes brutes. `connection_data` ou `parsed_connections` serait plus juste.

**Décision à prendre.** À discuter : nom de paramètre ; garder la méthode car elle sépare clairement instanciation et indexation.

<a id="m022"></a>

### 22 — `Connection.__init__`

**Source :** [`src/model/connection.py`, ligne 7](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L7)

```python
    def __init__(self, source: Hub, target: Hub, capacity: int | float):
        """Connect source and target with the given capacity and no usage.
        """
        self.source = source
        self.target = target
        self.capacity = capacity
        self.used_capacity = 0
```

**Lecture du code.** Stocke les deux objets Hub de la connexion non orientée, la capacité et `used_capacity=0`. C'est un état vivant, à la différence de `ConnectionState` qui est une copie figée pour l'affichage.

**Variables, noms et cohérence.** `source` et `target` peuvent suggérer un sens unique, alors que l'accès est bidirectionnel. Ce sont les noms lus dans la carte, **pas une direction imposée**. `endpoint_a`/`endpoint_b` refléterait mieux le modèle mais entraînerait beaucoup de renommages. `used_capacity` signifie « passages consommés ce tour ».

**Décision à prendre.** À discuter : conserver `source/target` pour cohérence avec la carte, ou mieux expliciter la bidirectionnalité.

<a id="m023"></a>

### 23 — `Graph._index_connection`

**Source :** [`src/model/graph.py`, ligne 51](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L51)

```python
    def _index_connection(
        self,
        connection: Connection,
```

**Lecture du code.** Ajoute chaque connexion à la liste d'adjacence de ses deux zones, puis à `connection_map` sous les clés `(source,target)` et `(target,source)`. Les deux clés renvoient **le même objet Connection** : sa capacité est donc partagée entre les sens.

**Variables, noms et cohérence.** `connection_map` est un index de couple d'objets, pas une copie des connexions. L'implémentation est volontairement symétrique ; ne pas supprimer l'une des entrées.

**Décision à prendre.** Conserver, éventuellement renommer `_index_connection` → `_register_connection` selon le vocabulaire choisi.


---

## IV. Préparation de la simulation et calcul du chemin initial

<a id="m024"></a>

### 24 — `Simulation.__init__`

**Source :** [`src/model/simulation.py`, ligne 13](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L13)

```python
    def __init__(
        self,
        graph: Graph,
        pathfinder: Dijkstra | None = None,
```

**Lecture du code.** Reçoit `Graph` et éventuellement un `Dijkstra` préconstruit pour les tests ; autrement instancie son propre pathfinder. Prépare liste des drones, compteur de tours initialisé à zéro et `Recorder`. Aucun drone n'est encore créé.

**Variables, noms et cohérence.** `pathfinder: Dijkstra | None` introduit une injection de dépendance utile aux tests ; c'est un cas où une option supplémentaire peut être justifiée. `self.turn` représente un numéro de tour, différent de la durée d'un trajet. `Recorder` est partagé par terminal et affichage.

**Décision à prendre.** Conserver. Éviter d'ajouter d'autres couches sans besoin.

<a id="m025"></a>

### 25 — `Dijkstra.__init__`

**Source :** [`src/model/pathfinder.py`, ligne 10](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/pathfinder.py#L10)

```python
    def __init__(self, graph: Graph):
        """Associate the graph with the pathfinder without computing a path."""
        self.graph = graph
```

**Lecture du code.** Stocke une référence à `Graph` ; ne cherche aucun chemin à la construction. Le vrai calcul se produit à l'appel de `shortest_distances`.

**Variables, noms et cohérence.** `graph` est un nom clair ; cette classe ne manipule pas les données de parsing.

**Décision à prendre.** Conserver.

<a id="m026"></a>

### 26 — `Recorder.__init__`

**Source :** [`src/model/recorder.py`, ligne 12](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/recorder.py#L12)

```python
    def __init__(self) -> None:
        """Initialize the shared simulation history."""
        self.frames: list[TurnState] = []
```

**Lecture du code.** Initialise `frames: list[TurnState]`. La liste sera remplie au tour zéro et après chaque tour complet. Chaque frame contient des **copies de valeurs**, pas les objets `Drone` vivants.

**Variables, noms et cohérence.** `frames` est commun à Pygame et à l'historique, mais une frame est ici un instantané d'un tour ; `turn_states` ferait moins penser à des images affichées à 60 FPS.

**Décision à prendre.** À discuter : garder `frames` si le terme est déjà bien intégré à l'interface.

<a id="m027"></a>

### 27 — `Simulation.load_drones`

**Source :** [`src/model/simulation.py`, ligne 32](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L32)

```python
    def load_drones(self, nb_drones: int) -> None:
        """Create drones in the starting hub."""
        if self.drones:
            raise RuntimeError(
                "Drones have already been loaded."
            )
        path = self.pathfinder.shortest_path()

        for index in range(nb_drones):
            drone = Drone(
                index + 1,
                current_position=self.graph.start_hub,
            )
            drone.set_path(path[1:])
            self.drones.append(drone)
            self.graph.start_hub.add_drone()
        self.recorder.record(self.turn, self.graph, self.drones)
```

**Lecture du code.** Refuse de charger une seconde fois des drones non vides. Calcule **un chemin initial commun** avec `shortest_path()`, instancie les drones avec des IDs 1..N à start, leur affecte `path[1:]` pour ne pas compter la zone où ils se trouvent déjà, incrémente l'occupation de start, puis enregistre l'état du tour zéro.

**Variables, noms et cohérence.** `path` est le chemin complet renvoyé par Dijkstra, alors que `drone.path` est le **chemin restant**. `path[1:]` est donc essentiel. Le calcul est fait une fois : on ne lance pas N fois Dijkstra au départ. La capacité de start est infinie.

**Décision à prendre.** À discuter : `load_drones` ou `initialize_drones` ? Le vrai risque serait un chemin initial vide, mais `MapValidator` vérifie la connectivité statique.

<a id="m028"></a>

### 28 — `Dijkstra.shortest_path`

**Source :** [`src/model/pathfinder.py`, ligne 96](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/pathfinder.py#L96)

```python
    def shortest_path(
        self,
        source: Hub | None = None,
        blocked_hubs: set[Hub] | None = None,
        saturated_connections: set[tuple[Hub, Hub]] | None = None,
```

**Lecture du code.** Prend éventuellement une zone de départ différente du start habituel et des ensembles de hubs/liens exclus. Utilise `shortest_distances`, vérifie si `end_hub` est atteignable, remonte les prédécesseurs de end jusqu'au départ, inverse la liste et retourne le chemin **avec les deux extrémités**.

**Variables, noms et cohérence.** `source=None` signifie « utiliser le départ du Graph », pas un sommet indéfini. `target` est toujours le end du projet. `path` contient des `Hub`, pas des noms. La condition `current is not None` arrête la remontée au prédécesseur initial absent.

**Décision à prendre.** Conserver : c'est le vrai service utilisé par la simulation. **`distance_to` a été supprimée** car l'application ne l'utilisait pas.

<a id="m029"></a>

### 29 — `Dijkstra.shortest_distances`

**Source :** [`src/model/pathfinder.py`, ligne 14](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/pathfinder.py#L14)

```python
    def shortest_distances(
        self,
        source: Hub,
        blocked_hubs: set[Hub] | None = None,
        saturated_connections: set[tuple[Hub, Hub]] | None = None,
```

**Lecture du code.** Construit `distances` initialisées à l'infini, `predecessors` à `None` et `priorities` à zéro. Un tas `heapq` contient `(distance, score_priority, compteur_unique, Hub)`, ce qui évite de comparer directement les objets Hub en cas d'égalité. Parcourt les connexions bidirectionnelles, ignore les voisins déjà finalisés, les hubs bloqués et les liens saturés, puis met à jour distance et prédécesseur si le tuple **(coût, score de priorité)** est meilleur.

**Variables, noms et cohérence.** Le poids est le coût **d'entrée dans la zone suivante** (`neighbor.move_cost()`) : restricted vaut 2 tours, normal/priority 1 et blocked ∞. `priority_score` devient plus négatif à chaque hub priority : à coût égal, on préfère en traverser davantage. `count()` sert uniquement de départage stable dans le tas. `visited` indique les zones finalisées, pas les zones interdites.

**Décision à prendre.** À discuter : `priorities` → `priority_scores`, `queue_counter` → `tie_breaker`, et éviter les noms `blocked_hubs` (interdictions explicites) / `blocked` (type de zone) trop proches. Pas de refactor de l'algorithme sans tests adversariaux.

<a id="m030"></a>

### 30 — `Graph.get_connections`

**Source :** [`src/model/graph.py`, ligne 70](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L70)

```python
    def get_connections(self, hub: Hub) -> list[Connection]:
        """Return connections incident to hub, or an empty list."""
        return self.adjacency.get(hub.name, [])
```

**Lecture du code.** Récupère dans `adjacency` la liste des connexions incidentes à une zone ; renvoie `[]` si aucune clé ne correspond. Cette méthode est appelée dans chaque exploration de Dijkstra.

**Variables, noms et cohérence.** Le paramètre est `hub: Hub` mais la recherche se fait avec `hub.name`. Ainsi l'index est par noms et pas par identité d'objet ; cohérent tant que le graphe possède des noms uniques.

**Décision à prendre.** Conserver.

<a id="m031"></a>

### 31 — `Connection.get_other_hub`

**Source :** [`src/model/connection.py`, ligne 29](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L29)

```python
    def get_other_hub(self, hub: Hub) -> Hub:
        """Return the opposite hub. Raise ConnectionError if hub is not an
        endpoint.
        """
        if self.source is hub:
            return self.target

        if self.target is hub:
            return self.source

        raise ConnectionError(
            f"Hub {hub.name} is not connected by this connection."
        )
```

**Lecture du code.** Vérifie si `hub` est exactement l'objet `source` ou `target` (`is`) et retourne l'autre. Si ce n'est aucune des deux extrémités, lève `ConnectionError` pour signaler un usage invalide.

**Variables, noms et cohérence.** Le test d'identité est intentionnel : les `Hub` du graphe sont des objets uniques. `other` n'est pas « direction imposée », c'est l'extrémité opposée. Méthode utilisée à la fois par Dijkstra et pour terminer un transit.

**Décision à prendre.** Conserver. On pourrait dire `get_opposite_hub`, mais le nom actuel est naturel.

<a id="m032"></a>

### 32 — `Hub.move_cost`

**Source :** [`src/model/hub.py`, ligne 56](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L56)

```python
    def move_cost(self) -> float:
        """Return the travel duration as weight, or infinity if blocked."""
        if self.zone_type == "blocked":
            return float("inf")
        return float(self.transit_duration())
```

**Lecture du code.** Si le type de zone est `blocked`, renvoie `inf`. Sinon appelle `transit_duration()` et renvoie une valeur flottante compatible avec les distances de Dijkstra. L'appel n'est pas une action de déplacement, seulement un **poids d'arête vers la zone**.

**Variables, noms et cohérence.** `move_cost` peut évoquer un tarif, pas une durée ; `travel_cost` ou `entry_cost` serait plus précis. La méthode tient compte du type de **zone d'arrivée** car elle est appelée sur le voisin.

**Décision à prendre.** À discuter : nom `move_cost` ; conserver la logique séparée de `transit_duration` si la règle blocked reste centralisée ici.

<a id="m033"></a>

### 33 — `Hub.transit_duration`

**Source :** [`src/model/hub.py`, ligne 62](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L62)

```python
    def transit_duration(self) -> int:
        """Return two turns for restricted hubs and one for other types.
        Pathfinding prevents entry into blocked hubs.
        """
        if self.zone_type == "restricted":
            return 2

        return 1
```

**Lecture du code.** Renvoie `2` si la zone est restricted, `1` sinon, y compris pour blocked : le filtrage de blocked est fait dans `move_cost`, pas dans cette méthode. Utilisée aussi par `Drone.path_turns` pour les estimations de durée restante.

**Variables, noms et cohérence.** `transit_duration` pourrait faire croire que le temps est toujours passé sur une connexion, alors que le coût décrit l'**entrée dans un hub**. `travel_turns` ou `entry_turns` serait potentiellement plus intuitif.

**Décision à prendre.** À discuter : choisir un nom unique et l'appliquer partout, sans changer les coûts.

<a id="m034"></a>

### 34 — `Drone.__init__`

**Source :** [`src/model/drone.py`, ligne 9](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L9)

```python
    def __init__(
        self,
        drone_id: int,
        current_position: Hub
```

**Lecture du code.** Place un drone dans un `Hub`, fixe son numéro, prépare une zone précédente absente (`None`), un chemin restant vide et l'état `idle`. `current_position` accepte ensuite soit un Hub soit une Connection, car un passage restricted occupe une connexion pendant un tour.

**Variables, noms et cohérence.** `current_position` est plus précis que `current_zone` dans un modèle où l'on peut être sur une connexion. `previous_zone` reste forcément un `Hub`. `status` est une chaîne sans Enum (`idle`, `moving`, `in_transit`, `waiting`, `delivered`) : simple mais sensible aux fautes dans les chaînes.

**Décision à prendre.** À discuter : introduire un `Literal` pour `status` plutôt qu'un Enum lourd, ou garder la simplicité actuelle.

<a id="m035"></a>

### 35 — `Drone.set_path`

**Source :** [`src/model/drone.py`, ligne 98](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L98)

```python
    def set_path(self, path: list[Hub]) -> None:
        """Replace the remaining path with a copy of path."""
        self.path = path.copy()
```

**Lecture du code.** Reçoit une liste de zones restantes et en fait une **copie** avec `path.copy()`. Cela permet à chaque drone de modifier son chemin sans toucher à la liste utilisée par un autre.

**Variables, noms et cohérence.** `set_path` est un vrai point d'entrée utilisé à l'initialisation et au reroutage. `path` contient les étapes futures, sans le Hub où le drone se trouve déjà.

**Décision à prendre.** Conserver.

<a id="m036"></a>

### 36 — `Hub.add_drone`

**Source :** [`src/model/hub.py`, ligne 20](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L20)

```python
    def add_drone(self) -> None:
        """Add one drone, raising HubError if capacity would be exceeded."""
        if not self.is_available():
            raise HubError("Cannot add more drones than the maximum allowed")
        self.nb_drones += 1
```

**Lecture du code.** Appelle `is_available()` avant d'incrémenter `nb_drones`, sinon lève `HubError`. Cette même garde protège les arrivées ordinaires et les entrées à l'issue d'un transit après libération de la réservation.

**Variables, noms et cohérence.** `add_drone` laisse entendre une liste d'objets, mais ne manipule qu'un **compteur**. `increment_occupancy` serait techniquement exact mais plus verbeux ; dans le contexte, `add_drone` se comprend.

**Décision à prendre.** À discuter : le nom, mais pas le contrôle de capacité.

<a id="m037"></a>

### 37 — `Hub.is_available`

**Source :** [`src/model/hub.py`, ligne 32](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L32)

```python
    def is_available(self) -> bool:
        """Return whether a slot is free, accounting for reservations."""
        return self.nb_drones + self.reserved < self.capacity
```

**Lecture du code.** Retourne `nb_drones + reserved < capacity`. Il faut additionner **présents et places réservées** : sinon un nouveau drone pourrait prendre la place d'un drone déjà engagé dans une zone restricted.

**Variables, noms et cohérence.** `reserved` n'est donc pas du code mort : il est essentiel. Avec capacité infinie, le résultat est toujours vrai pour une occupation finie.

**Décision à prendre.** Conserver ; éventuellement nommer `has_free_capacity` pour distinguer du fait qu'une zone blocked n'est pas traversable.

<a id="m038"></a>

### 38 — `Recorder.record`

**Source :** [`src/model/recorder.py`, ligne 16](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/recorder.py#L16)

```python
    def record(
        self,
        turn: int,
        graph: Graph,
        drones: list[Drone],
        moved_drones: tuple[int, ...] = (),
```

**Lecture du code.** Pour chaque drone, copie sa position comme **nom de Hub** ou **paire de noms d'extrémités** si en transit. Le `Counter` compte les transits restés sur chaque connexion. Copie ensuite tous les hubs et les connexions dans des dataclasses `frozen=True`, puis ajoute un `TurnState` avec le tour, les mouvements et les structures indépendantes du modèle.

**Variables, noms et cohérence.** `moved_drones` contient uniquement les IDs qui ont avancé **ce tour**, et sert à la sortie texte. `frame.drones` est un dictionnaire de snapshots par ID. Important : `frozen=True` protège les objets dataclass, pas les dictionnaires imbriqués de `TurnState` contre une modification extérieure. L'historique est indépendant des objets vivants, mais pas profondément immutable.

**Décision à prendre.** À discuter : `transits` pour les liens dont le sens est inversé. Les clés sont actuellement `(connection.source.name, connection.target.name)` même si le drone traverse dans l'autre sens : c'est volontaire pour comptabiliser par connexion physique.


---

## V. Boucle des tours, mouvement, transit et reroutage

<a id="m039"></a>

### 39 — `Simulation.simulate`

**Source :** [`src/model/simulation.py`, ligne 218](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L218)

```python
    def simulate(self) -> list[TurnState]:
        """Run to completion and return the initial and completed states."""
        while not self._all_drones_delivered():
            self._prepare_connections_for_turn()
            moved_drones = []
            for drone in sorted(
                self.drones, key=lambda drone: drone.path_turns(),
            ):
                if self._advance_drone(drone):
                    moved_drones.append(drone.drone_id)
            self.turn += 1
            self.recorder.record(
                self.turn, self.graph, self.drones, tuple(moved_drones),
            )
        return self.recorder.frames
```

**Lecture du code.** La boucle continue tant que `_all_drones_delivered()` est faux. À chaque tour, `_prepare_connections_for_turn` remet les usages des liens à jour. Les drones sont triés par `path_turns()` croissant, puis chacun passe au plus une fois dans `_advance_drone`. Les IDs de ceux qui ont bougé sont conservés, le compteur de tour est incrémenté et `Recorder.record` prend la photographie. La méthode retourne `recorder.frames`.

**Variables, noms et cohérence.** `moved_drones` est une liste locale convertie en tuple dans la frame ; les vues ne recalculent pas les déplacements. **Le tri en cours de tour** est calculé sur un snapshot de la liste triée : la modification du chemin d'un drone ne le fait pas changer de rang avant le prochain tour. La boucle n'a pas de détection d'absence de progrès prolongée.

**Décision à prendre.** À discuter : nom `simulate`, condition de sortie et stratégie d'ordonnancement. Risque à analyser : un drone traité avant la libération d'une zone par un autre pourrait attendre un tour de plus. Ne pas conclure à une violation sans reproduction.

<a id="m040"></a>

### 40 — `Simulation._all_drones_delivered`

**Source :** [`src/model/simulation.py`, ligne 181](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L181)

```python
    def _all_drones_delivered(self) -> bool:
        """Return whether all drones have reached the destination."""
        return all(
            drone.current_position == self.graph.end_hub
            for drone in self.drones
        )
```

**Lecture du code.** Renvoie `all(drone.current_position == end_hub for drone in drones)`. C'est la condition d'arrêt de la simulation. `all([])` vaudrait `True`, mais `load_drones` est censé être appelé avant et le parser exige un nombre positif.

**Variables, noms et cohérence.** Le nom explique parfaitement le prédicat ; il ne vérifie pas `status == 'delivered'`, car la **position** est le fait déterminant. `_advance_drone` marque l'état delivered à l'arrivée.

**Décision à prendre.** Conserver.

<a id="m041"></a>

### 41 — `Simulation._prepare_connections_for_turn`

**Source :** [`src/model/simulation.py`, ligne 210](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L210)

```python
    def _prepare_connections_for_turn(self) -> None:
        """Prepare a new turn, retaining only ongoing transit occupancy."""
        for connection in self.graph.connections:
            connection.used_capacity = 0
        for drone in self.drones:
            if isinstance(drone.current_position, Connection):
                drone.current_position.use_capacity()
```

**Lecture du code.** Remet d'abord `used_capacity=0` sur toutes les connexions, puis parcourt les drones **encore en transit** pour consommer leurs places sur le lien durant le tour courant. Cette réoccupation évite qu'un nouveau drone emprunte un lien déjà occupé.

**Variables, noms et cohérence.** La méthode modifie directement `connection.used_capacity = 0`, sans méthode `Connection.reset_capacity()`. C'est un choix de frontière de responsabilité : simple mais encapsulation limitée. `prepare` est cohérent puisqu'il prépare un nouveau tour.

**Décision à prendre.** À discuter : conserver l'accès direct ou introduire `reset_usage()` **uniquement** si l'on veut que Connection possède toute la logique de compteur.

<a id="m042"></a>

### 42 — `Drone.path_turns`

**Source :** [`src/model/drone.py`, ligne 89](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L89)

```python
    def path_turns(self) -> int:
        """Sum the travel durations of the remaining path. Time already
        spent in transit is not subtracted.
        """
        return sum(
            zone.transit_duration()
            for zone in self.path
        )
```

**Lecture du code.** Somme les `transit_duration()` de chaque Hub **restant** dans `drone.path`. Estimation utilisée pour prioriser les drones et comparer les détours. Ne tient pas compte d'une durée de transit déjà entamée ni d'une attente future.

**Variables, noms et cohérence.** `path_turns()` désigne une estimation de durée restante si le parcours reste libre ; `remaining_path_cost()` serait plus fidèle, car ce n'est pas une prédiction exacte du temps jusqu'à l'arrivée.

**Décision à prendre.** À discuter : renommer selon la signification sans modifier le tri.

<a id="m043"></a>

### 43 — `Simulation._advance_drone`

**Source :** [`src/model/simulation.py`, ligne 188](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L188)

```python
    def _advance_drone(
        self,
        drone: Drone,
```

**Lecture du code.** Si le drone est déjà à end, le marque delivered et ne bouge pas. S'il est sur une connexion, appelle `advance_transit()`, libère la réservation de la destination puis y incrémente l'occupation. Sinon tente `_move_or_wait()`. Termine en marquant `delivered` tout drone arrivé à end et renvoie si le drone s'est déplacé.

**Variables, noms et cohérence.** `moved=True` lors d'une arrivée de transit signifie qu'elle doit apparaître dans la sortie de ce tour ; le lien parcouru est encore compté par le Recorder. `destination` est `Hub | None` pour le contrat de `advance_transit`, même si dans cette branche le drone est bien sur Connection et devrait toujours recevoir un Hub.

**Décision à prendre.** À discuter : la vérification `if destination is not None` est défensive ; on peut la garder pour cohérence avec l'annotation plutôt que l'effacer aveuglément.

<a id="m044"></a>

### 44 — `Simulation._move_or_wait`

**Source :** [`src/model/simulation.py`, ligne 116](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L116)

```python
    def _move_or_wait(
        self,
        drone: Drone,
```

**Lecture du code.** Vérifie que le drone est dans un Hub et possède un chemin restant. Sauvegarde **une copie du chemin d'origine et son coût** ; prépare les ensembles de hubs bloqués et de liens saturés, et interdit d'abord la zone précédente pour éviter le demi-tour immédiat. Dans la boucle, regarde le prochain Hub, cherche la connexion, vérifie les deux capacités, ordonne un mouvement si possible ; sinon exclut les ressources indisponibles et appelle `_reroute_drone`. Si aucun chemin alternatif n'existe, le drone attend. Si le détour coûte **plus de deux tours supplémentaires** par rapport au chemin original, il restaure ce dernier puis attend.

**Variables, noms et cohérence.** `blocked_hubs` inclut ici les hubs temporairement pleins **et** le hub précédent ; ce n'est pas la même chose qu'un hub de type `blocked`. `saturated_connections` stocke des couples de Hub et Dijkstra vérifie les deux orientations. `original_cost` est calculé avant la tentative et ne représente **pas** la durée réelle d'attente.

**Décision à prendre.** À discuter : noms `_move_or_wait` et `_reroute_drone` sont clairs ; l'exclusion systématique de `previous_zone`, le seuil `+2` et le risque de repasser plusieurs fois dans `while True` méritent un scénario concret. Ne pas modifier l'heuristique sans validation.

<a id="m045"></a>

### 45 — `Graph.get_connection`

**Source :** [`src/model/graph.py`, ligne 74](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/graph.py#L74)

```python
    def get_connection(self, source: Hub, target: Hub) -> Connection | None:
        """Return the connection between source and target, or None if
        absent.
        """
        return self.connection_map.get((source, target))
```

**Lecture du code.** Consulte le dictionnaire `connection_map` indexé par deux objets Hub. Retourne la même `Connection` quel que soit l'ordre des deux Hub, ou `None` si aucun lien direct.

**Variables, noms et cohérence.** `get_connection` est le terme juste ; renvoie `Connection | None`, donc le test `if connection is None` dans `_move_or_wait` est nécessaire.

**Décision à prendre.** Conserver.

<a id="m046"></a>

### 46 — `Connection.is_available`

**Source :** [`src/model/connection.py`, ligne 25](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L25)

```python
    def is_available(self) -> bool:
        """Return whether another unit of capacity is available this turn."""
        return self.used_capacity < self.capacity
```

**Lecture du code.** Compare `used_capacity < capacity`. Une connexion est bidirectionnelle, donc la capacité est partagée : deux drones en sens opposés consomment le même compteur.

**Variables, noms et cohérence.** `is_available` signifie place **sur le lien pendant le tour**, pas capacité de destination. Le code doit vérifier en plus `Hub.is_available()` ; c'est fait dans `_move_or_wait`.

**Décision à prendre.** Conserver.

<a id="m047"></a>

### 47 — `Simulation.move_drone`

**Source :** [`src/model/simulation.py`, ligne 54](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L54)

```python
    def move_drone(
        self,
        drone: Drone,
        connection: Connection,
        target_hub: Hub,
```

**Lecture du code.** Récupère le Hub actuel, refuse qu'il s'agisse déjà d'une connexion, puis décrémente l'occupation de départ. Si le Hub cible est restricted, le drone entre sur la connexion (`begin_transit`) et **réserve** une place d'arrivée. Sinon le drone rejoint immédiatement le Hub (`move_to_zone`) et on incrémente l'occupation. Termine par la consommation d'une capacité de lien.

**Variables, noms et cohérence.** La méthode suppose que les capacités ont été vérifiées **avant son appel** par `_move_or_wait`; elle n'effectue pas une validation atomique avant de modifier le départ. Cela fonctionne avec la structure courante, mais explique pourquoi elle ne doit pas être appelée arbitrairement depuis un autre endroit. `move_drone` peut être nommé `_move_drone` si l'on veut marquer cette convention.

**Décision à prendre.** À discuter : faut-il rendre la méthode privée ou lui faire vérifier elle-même les préconditions ? Éviter une double vérification inutile sans raison.

<a id="m048"></a>

### 48 — `Hub.remove_drone`

**Source :** [`src/model/hub.py`, ligne 26](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L26)

```python
    def remove_drone(self) -> None:
        """Remove one drone, raising HubError if the hub is empty."""
        if self.nb_drones - 1 < 0:
            raise HubError("Cannot remove more drones than currently present")
        self.nb_drones -= 1
```

**Lecture du code.** Vérifie que `nb_drones` ne deviendrait pas négatif, puis décrémente. Utilisée au début d'un mouvement et avant une réservation restricted.

**Variables, noms et cohérence.** `self.nb_drones - 1 < 0` équivaut ici à `self.nb_drones <= 0`, plus direct à lire ; les valeurs sont des compteurs entiers.

**Décision à prendre.** À discuter : simplifier la condition, changement sans effet fonctionnel.

<a id="m049"></a>

### 49 — `Drone.move_to_zone`

**Source :** [`src/model/drone.py`, ligne 23](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L23)

```python
    def move_to_zone(
        self,
        zone: Hub,
```

**Lecture du code.** Vérifie que le drone n'est pas sur une Connection, conserve l'ancien Hub comme `previous_zone`, change `current_position` pour la zone cible, consomme le premier élément du chemin avec `pop(0)`, puis marque `moving`.

**Variables, noms et cohérence.** `zone: Hub` alors que le reste parle le plus souvent de `hub` et `target_hub`. `move_to_zone()` pourrait être `move_to_hub()` pour cohérence, à condition de renommer les appels. `pop(0)` coûte O(n) sur une liste, mais les chemins usuels sont courts ; pas un problème à optimiser sans mesure.

**Décision à prendre.** À discuter : cohérence `zone` vs `hub`, qui revient dans plusieurs classes.

<a id="m050"></a>

### 50 — `Drone.begin_transit`

**Source :** [`src/model/drone.py`, ligne 42](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L42)

```python
    def begin_transit(
        self,
        connection: Connection,
```

**Lecture du code.** Empêche de lancer un transit si le drone est déjà sur une Connection. Enregistre le Hub précédent, remplace `current_position` par la connexion et passe le statut à `in_transit`. **Le compteur de capacité et la réservation ne sont pas modifiés ici** : ils appartiennent à Simulation.

**Variables, noms et cohérence.** `connection` est passé en paramètre, sans coût ni destination ; l'extrémité d'arrivée est déduite plus tard de `previous_zone` grâce à `get_other_hub`. Cette répartition évite d'avoir deux fois la logique de capacité.

**Décision à prendre.** Conserver la responsabilité ; à discuter seulement si l'on veut rapprocher les états et les réservations dans le modèle.

<a id="m051"></a>

### 51 — `Hub.reserve`

**Source :** [`src/model/hub.py`, ligne 36](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L36)

```python
    def reserve(self) -> None:
        """Reserve a slot for a drone in transit. Raise HubError if
        occupancy and reservations reach capacity.
        """
        if not self.is_available():
            raise HubError(
                "Cannot reserve more than hub capacity"
            )

        self.reserved += 1
```

**Lecture du code.** Appelle `is_available` pour empêcher les réservations au-delà de la capacité puis incrémente `reserved`. La réservation est créée quand un drone commence à traverser vers une zone restricted.

**Variables, noms et cohérence.** `reserved` désigne **des places**, pas nécessairement des drones déjà présents. Le test avant incrément est nécessaire.

**Décision à prendre.** Conserver.

<a id="m052"></a>

### 52 — `Connection.use_capacity`

**Source :** [`src/model/connection.py`, ligne 15](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L15)

```python
    def use_capacity(self) -> None:
        """Use one unit of capacity for the current turn.
        Raise ConnectionError if capacity would be exceeded.
        """
        if not self.is_available():
            raise ConnectionError(
                "Cannot add more drones than the maximum allowed"
            )
        self.used_capacity += 1
```

**Lecture du code.** Vérifie `is_available()` puis incrémente `used_capacity`. Appelée lors d'un nouveau passage et lors de la réservation de la place d'un transit toujours en cours au début d'un tour.

**Variables, noms et cohérence.** `use_capacity` fait penser à une consommation définitive, mais le compteur est **réinitialisé chaque tour** ; `occupy_for_turn()` serait plus descriptif. Message d'erreur « add more drones » décrit un dépassement de lien, pas l'ajout d'un drone au hub : à clarifier.

**Décision à prendre.** À discuter : noms `used_capacity`/`use_capacity`, et texte d'erreur.

<a id="m053"></a>

### 53 — `Simulation._reroute_drone`

**Source :** [`src/model/simulation.py`, ligne 85](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/simulation.py#L85)

```python
    def _reroute_drone(
        self,
        drone: Drone,
        blocked_hubs: set[Hub],
        saturated_connections: set[
            tuple[Hub, Hub]
        ],
```

**Lecture du code.** Si le drone se trouve sur Connection, renvoie `False`. Sinon appelle Dijkstra depuis son Hub courant avec les interdictions temporaires. Une route de longueur inférieure à deux n'apporte aucun prochain saut ; sinon `set_path(path[1:])` remplace le chemin restant et renvoie `True`.

**Variables, noms et cohérence.** Cette méthode **ne déplace pas** le drone ; la boucle appelante réessaie immédiatement `_move_or_wait` avec la nouvelle première étape. Le contrôle du coût de détour reste dans `_move_or_wait`, donc la méthode n'est pas responsable du seuil `+2`.

**Décision à prendre.** Conserver ; ne pas mélanger recherche de chemin et déplacement.

<a id="m054"></a>

### 54 — `Drone.wait`

**Source :** [`src/model/drone.py`, ligne 81](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L81)

```python
    def wait(self) -> None:
        """Mark the drone as waiting without changing its position."""
        self.status = "waiting"
```

**Lecture du code.** Ne change ni position ni chemin : met seulement `status='waiting'`. Au tour suivant, le drone pourra tenter le chemin courant.

**Variables, noms et cohérence.** `waiting` est important pour le Recorder et l'affichage, même si le terminal n'affiche que les drones ayant réellement bougé.

**Décision à prendre.** Conserver.

<a id="m055"></a>

### 55 — `Drone.advance_transit`

**Source :** [`src/model/drone.py`, ligne 59](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L59)

```python
    def advance_transit(self) -> Hub | None:
        """Complete a restricted move on the turn after departure.

        Return the destination, or None when there is no active transit.
        Consume the path step and raise RuntimeError if departure is missing.
        """
        if not isinstance(self.current_position, Connection):
            return None

        if self.previous_zone is None:
            raise RuntimeError(
                f"Drone {self.drone_id}: missing connection or departure hub."
            )

        destination = self.current_position.get_other_hub(
            self.previous_zone)
        self.current_position = destination
        self.path.pop(0)
        self.status = "moving"

        return destination
```

**Lecture du code.** Si le drone n'est pas sur Connection, renvoie `None`. Sinon vérifie qu'il connaît le Hub d'origine, récupère l'autre extrémité de la connexion, déplace le drone sur ce Hub, consomme la prochaine étape du chemin et marque `moving`. **Simulation** libère ensuite la réservation et incrémente le Hub.

**Variables, noms et cohérence.** `advance_transit` est un nom assez général alors qu'il **termine** ici un transit en un seul appel : `finish_transit()` serait peut-être plus exact. `destination` est reconstruite à partir de `previous_zone` et non stockée séparément.

**Décision à prendre.** À discuter : renommer `finish_transit` pour rendre le cycle de deux tours explicite.

<a id="m056"></a>

### 56 — `Hub.release_reservation`

**Source :** [`src/model/hub.py`, ligne 47](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L47)

```python
    def release_reservation(self) -> None:
        """Release one reservation, raising HubError if none exists."""
        if self.reserved == 0:
            raise HubError(
                "No reservation to release"
            )

        self.reserved -= 1
```

**Lecture du code.** Vérifie qu'il existe au moins une place réservée avant de décrémenter. À l'arrivée après un transit, Simulation fait cela **avant** `add_drone` : la place passe de réservée à occupée sans dépasser la capacité.

**Variables, noms et cohérence.** `release_reservation` n'est pas un simple reset : c'est le transfert de réservation vers occupation, indispensable à la logique restricted.

**Décision à prendre.** Conserver.

<a id="m057"></a>

### 57 — `Drone.deliver`

**Source :** [`src/model/drone.py`, ligne 85](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/drone.py#L85)

```python
    def deliver(self) -> None:
        """Mark the drone as delivered without changing its position."""
        self.status = "delivered"
```

**Lecture du code.** Met `status='delivered'`, ne modifie pas la position. Appelée quand le drone se trouve dans end, y compris juste après l'arrivée.

**Variables, noms et cohérence.** Le nom de statut est utilisé dans les snapshots et les tests. `deliver` est un verbe de la mission (livrer), pas une référence au message terminal.

**Décision à prendre.** Conserver.


---

## VI. Sortie terminal et affichage Pygame

<a id="m058"></a>

### 58 — `TerminalView.display`

**Source :** [`src/view/terminal.py`, ligne 9](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/terminal.py#L9)

```python
    def display(self, turns: Iterable[TurnState]) -> None:
        """Print one line per completed turn, omitting the initial state."""
        for frame in turns:
            if frame.turn == 0:
                continue
            movements = []
            for drone_id in frame.moved_drones:
                position = frame.drones[drone_id].current_position
                destination = position if isinstance(position, str) else (
                    "-".join(position)
                )
                movements.append(f"D{drone_id}-{destination}")
            print(" ".join(movements), flush=True)
```

**Lecture du code.** Parcourt les `TurnState` et ignore le tour zéro. Pour chaque drone qui a avancé ce tour (`moved_drones`), récupère une position qui est soit le nom d'un Hub soit un couple de noms de lien ; construit `D<ID>-<destination>` et imprime tous les déplacements du tour sur une ligne, y compris une ligne vide si aucun drone n'a bougé.

**Variables, noms et cohérence.** `turns: Iterable[TurnState]` accepte liste, tuple ou générateur, un choix de souplesse raisonnable. Le paramètre `turns` convient mieux que `frames` à cette vue. `destination` est soit une zone soit une connexion formatée avec `-` ; nom suffisamment contextuel.

**Décision à prendre.** Conserver la sortie stricte, importante pour le sujet. Pas de logs de debug mélangés.

<a id="m059"></a>

### 59 — `PygameView.__init__`

**Source :** [`src/view/pygame_view.py`, ligne 18](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/pygame_view.py#L18)

```python
    def __init__(
        self,
        replay_frames: list[TurnState],
```

**Lecture du code.** Conserve `replay_frames` ; n'initialise aucune fenêtre. Les constantes de classe `SCREEN_W/H=0` et `CELL_SIZE=160` configurent la taille de départ automatique et l'échelle des positions.

**Variables, noms et cohérence.** `replay_frames` est cohérent avec la vue, bien que les objets soient des états de tours. La taille 0×0 avec `pygame.RESIZABLE` dépend de la politique SDL de création de fenêtre.

**Décision à prendre.** À discuter : dimensions par défaut si tu préfères une taille fixe à l'ouverture.

<a id="m060"></a>

### 60 — `PygameView.display`

**Source :** [`src/view/pygame_view.py`, ligne 25](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/pygame_view.py#L25)

```python
    def display(self) -> None:
        """Display the replay and always release Pygame resources.

        Wrap expected Pygame errors in DisplayError for the entry point.
        Other exceptions propagate after cleanup.
        """
        try:
            self._display_replay()
        except pygame.error as exc:
            raise DisplayError(
                f"Cannot display graphical replay: {exc}"
            ) from exc
        finally:
            pygame.quit()
```

**Lecture du code.** Lance `_display_replay` dans un `try`. Seuls les `pygame.error` sont transformés en `DisplayError` ; toute autre exception remonte, mais `pygame.quit()` s'exécute **toujours** grâce à `finally`. Une interruption ne laisse donc pas de fenêtre ouverte par cette méthode.

**Variables, noms et cohérence.** `exc` pour l'exception est idiomatique. La séparation de `display` et `_display_replay` permet d'isoler le nettoyage du détail de la boucle événementielle.

**Décision à prendre.** Conserver.

<a id="m061"></a>

### 61 — `PygameView._display_replay`

**Source :** [`src/view/pygame_view.py`, ligne 39](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/pygame_view.py#L39)

```python
    def _display_replay(self) -> None:
        """Initialize the window and run the interactive replay loop."""
        if not self.replay_frames:
            return
        pygame.init()

        screen = pygame.display.set_mode(
            (self.SCREEN_W, self.SCREEN_H),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption("Fly'in")

        font_small = pygame.font.SysFont(
            "arial",
            20,
            bold=True,
        )

        clock = pygame.time.Clock()

        coord = CoordinateSystem(
            cell_size=self.CELL_SIZE
        )
        world_positions = coord.compute(
            self.replay_frames[0].hubs.values()
        )

        renderer = GraphRenderer(
            screen=screen,
            font=font_small,
        )

        replay = ReplayPlayer(
            frames=self.replay_frames,
        )

        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False

                replay.handle_event(event)

            screen_w, screen_h = screen.get_size()
            max_x = max(
                (abs(x) for x, _ in world_positions.values()),
                default=0.0,
            )
            max_y = max(
                (abs(y) for _, y in world_positions.values()),
                default=0.0,
            )
            scale = min(
                1.0,
                (screen_w - 160) / (2 * max_x) if max_x else 1.0,
                (screen_h - 160) / (2 * max_y) if max_y else 1.0,
            )
            scale = max(0.0, scale)
            positions = {
                name: (
                    int(screen_w / 2 + x * scale),
                    int(screen_h / 2 + y * scale),
                )
                for name, (x, y) in world_positions.items()
            }

            frame = replay.frames[replay.current_index]
            renderer.draw(frame, positions)
            replay.draw(screen, font_small, positions)
            replay.draw_overlay(screen, font_small)

            pygame.display.flip()
```

**Lecture du code.** Initialise la fenêtre et le replay, puis calcule les coordonnées logiques centrées avec `CoordinateSystem`. Chaque rafraîchissement convertit ces coordonnées en positions écran ajustées à la taille de la fenêtre, sans zoom ni déplacement de caméra. Échap ferme la fenêtre, les flèches et R pilotent le replay.

**Variables, noms et cohérence.** `world_positions` conserve les coordonnées logiques centrées, `positions` les pixels de l'écran. `scale` ajuste automatiquement le cadrage lors d'un redimensionnement ; ce n'est pas un zoom interactif.

**Décision à prendre.** **MODIFIÉ** : suppression de `Camera`, du zoom, du glisser et de la touche C. Cadrage automatique conservé.

<a id="m062"></a>

### 62 — `CoordinateSystem.__init__`

**Source :** [`src/view/utils/coordinate_system.py`, ligne 14](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/utils/coordinate_system.py#L14)

```python
    def __init__(
        self,
        cell_size: int = 400,
```

**Lecture du code.** Stocke `cell_size` qui traduit les coordonnées numériques de la carte en unités monde pour le renderer. PygameView fournit actuellement 160.

**Variables, noms et cohérence.** `cell_size=400` dans la signature est une **valeur par défaut différente** de celle passée depuis PygameView. Ce n'est pas un bug quand l'appel explicite 160, mais le double réglage peut surprendre un lecteur.

**Décision à prendre.** À discuter : supprimer la valeur par défaut si cette classe est toujours appelée avec un paramètre explicite, ou aligner les constantes.

<a id="m063"></a>

### 63 — `CoordinateSystem.compute`

**Source :** [`src/view/utils/coordinate_system.py`, ligne 21](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/utils/coordinate_system.py#L21)

```python
    def compute(
        self,
        hubs: Iterable["Hub | HubState"],
```

**Lecture du code.** Convertit le conteneur `hubs` en liste pour pouvoir y passer plusieurs fois, renvoie `{}` si vide. Mesure les coordonnées extrêmes et centre le graphe. Si la plage * cell_size dépasse `MAX_WORLD_SPAN`, normalise les positions dans une plage bornée ; sinon applique directement l'échelle. Utilise des différences d'entiers avant la conversion flottante pour supporter de grandes coordonnées.

**Variables, noms et cohérence.** `span` est le plus grand écart sur X/Y. Le nom `positions` n'est pas utilisé ici : la sortie est un dictionnaire de **coordonnées monde centrées**. Le `TYPE_CHECKING` évite un import runtime de deux classes, les annotations sont des références différées.

**Décision à prendre.** Conserver l'algorithme tant que les tests de grandes coordonnées passent ; on peut discuter `compute` → `world_positions` ou `compute_positions`.

<a id="m064"></a>

### 64 — `GraphRenderer.__init__`

**Source :** [`src/view/graph_renderer.py`, ligne 136](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L136)

```python
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Associate the screen and font with the entity renderers."""
        self.screen = screen
        self.hub_renderer = HubRenderer(font)
        self.connection_renderer = ConnectionRenderer(font)
```

**Lecture du code.** Conserve l'écran et construit deux dessinateurs spécialisés utilisant la même police : `HubRenderer` et `ConnectionRenderer`. Ils ne connaissent que le `TurnState`, pas les objets de simulation.

**Variables, noms et cohérence.** `screen` est stocké ici, alors que HubRenderer/ConnectionRenderer le reçoivent à chaque `draw` : légère asymétrie, mais pas de duplication fonctionnelle.

**Décision à prendre.** À discuter : cohérence du passage de `screen`, sans imposer une refonte de toutes les signatures.

<a id="m065"></a>

### 65 — `HubRenderer.__init__`

**Source :** [`src/view/graph_renderer.py`, ligne 41](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L41)

```python
    def __init__(self, font: pygame.font.Font) -> None:
        """Store the font used for hub labels."""
        self.font = font
```

**Lecture du code.** Conserve la police Pygame pour écrire noms et compteurs des zones. Les couleurs et tailles sont des constantes de classe, pas des champs ajoutés à chaque instance.

**Variables, noms et cohérence.** `font` est suffisant et lisible.

**Décision à prendre.** Conserver.

<a id="m066"></a>

### 66 — `ConnectionRenderer.__init__`

**Source :** [`src/view/graph_renderer.py`, ligne 91](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L91)

```python
    def __init__(self, font: pygame.font.Font) -> None:
        """Store the font used for connection capacity labels."""
        self.font = font
```

**Lecture du code.** Conserve la police Pygame pour écrire nombre de passages et transits. Les trois valeurs graphiques `CONN_FILL`, `CONN_BORDER`, `BAND_WIDTH` sont des constantes.

**Variables, noms et cohérence.** Nom cohérent avec `HubRenderer` ; l'objet dessine une connexion, pas des drones.

**Décision à prendre.** Conserver.

<a id="m067"></a>

### 67 — `ReplayPlayer.__init__`

**Source :** [`src/view/replay_player.py`, ligne 19](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L19)

```python
    def __init__(
        self,
        frames: list[TurnState],
```

**Lecture du code.** Stocke la liste de snapshots et fixe `current_index=0`, correspondant au tour zéro. La méthode ne lance pas de lecture automatique : l'utilisateur avance/revient manuellement via le clavier.

**Variables, noms et cohérence.** `current_index` est un **index dans la liste** et non le numéro du tour ; ils coïncident dans l'historique normal, mais ce n'est pas garanti si la liste est filtrée.

**Décision à prendre.** Conserver ; `current_turn_index` serait plus explicite mais plus long.

<a id="m068"></a>

### 68 — `ReplayPlayer.handle_event`

**Source :** [`src/view/replay_player.py`, ligne 40](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L40)

```python
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle arrow keys and R, ignoring other events."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_RIGHT:
            self.next_turn()

        elif event.key == pygame.K_LEFT:
            self.previous_turn()

        elif event.key == pygame.K_r:
            self.restart()
```

**Lecture du code.** Ignore tout sauf `pygame.KEYDOWN`. La flèche droite appelle `next_turn`, la gauche `previous_turn`, R `restart`. Les événements de caméra et de fermeture sont gérés séparément dans PygameView.

**Variables, noms et cohérence.** `handle_event` est un nom générique parce que ReplayPlayer gère un sous-ensemble des événements, pas tous. `_handle_keydown` préciserait le comportement, mais l'appel actuel depuis PygameView est lisible.

**Décision à prendre.** Conserver.

<a id="m069"></a>

### 69 — `ReplayPlayer.next_turn`

**Source :** [`src/view/replay_player.py`, ligne 54](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L54)

```python
    def next_turn(self) -> None:
        """Select the next frame without passing the last frame."""
        if self.current_index >= len(self.frames) - 1:
            return

        self.current_index += 1
```

**Lecture du code.** N'avance pas au-delà de `len(frames)-1`, sinon incrémente `current_index`. C'est un déplacement dans l'historique enregistré, pas un nouveau tour de simulation.

**Variables, noms et cohérence.** `next_turn` exprime correctement l'intention de l'utilisateur.

**Décision à prendre.** Conserver.

<a id="m070"></a>

### 70 — `ReplayPlayer.previous_turn`

**Source :** [`src/view/replay_player.py`, ligne 61](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L61)

```python
    def previous_turn(self) -> None:
        """Select the previous frame without passing the first frame."""
        self.current_index = max(
            self.current_index - 1,
            0,
        )
```

**Lecture du code.** Décrémente l'index tout en bornant le minimum à zéro avec `max(...)`. Ne modifie pas le graphe, seulement le snapshot affiché.

**Variables, noms et cohérence.** Un nom `previous_frame` serait plus technique mais le mot « tour » est le concept utilisateur.

**Décision à prendre.** Conserver.

<a id="m071"></a>

### 71 — `ReplayPlayer.restart`

**Source :** [`src/view/replay_player.py`, ligne 68](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L68)

```python
    def restart(self) -> None:
        """Reset the selection to the beginning of the replay."""
        self.current_index = 0
```

**Lecture du code.** Remet la sélection au premier snapshot (`current_index=0`). Ne relance pas `Simulation.simulate()` et ne réinitialise pas les drones.

**Variables, noms et cohérence.** `restart` peut suggérer **relancer la simulation** alors qu'il signifie « revenir au début du replay » : `go_to_start()` ou `reset_replay()` serait plus précis.

**Décision à prendre.** À discuter : renommer pour ne pas confondre avec un redémarrage de la mission.

<a id="m072"></a>

### 72 — `GraphRenderer.draw`

**Source :** [`src/view/graph_renderer.py`, ligne 154](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L154)

```python
    def draw(
        self,
        frame: TurnState,
        positions: dict[str, tuple[int, int]],
    ) -> None:
        """Draw the recorded connections and hubs at screen positions."""
        self.screen.fill(self.BG_COLOR)
        for connection in frame.connections.values():
            self.connection_renderer.draw(
                self.screen, positions[connection.source],
                positions[connection.target], connection,
            )
        for hub in frame.hubs.values():
            self.hub_renderer.draw(
                self.screen, hub, positions[hub.name],
                is_terminal=hub.name in (frame.start_hub, frame.end_hub),
            )
```

**Lecture du code.** Efface l'écran, dessine les connexions puis les hubs aux positions écran déjà calculées. La transformation des coordonnées n'appartient plus au renderer.

**Variables, noms et cohérence.** `positions` contient directement les coordonnées en pixels partagées avec `ReplayPlayer.draw` ; aucun paramètre caméra.

**Décision à prendre.** **MODIFIÉ** : dessin direct, sans projection caméra.

<a id="m073"></a>

### 73 — `ConnectionRenderer.draw`

**Source :** [`src/view/graph_renderer.py`, ligne 108](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L108)

```python
    def draw(
        self,
        screen: pygame.Surface,
        source_position: tuple[int, int],
        target_position: tuple[int, int],
        state: ConnectionState,
    ) -> None:
        """Draw turn usage separately from drones still in transit."""
        if source_position == target_position:
            return
        border_width = self.BAND_WIDTH
        pygame.draw.line(
            screen, self.CONN_BORDER, source_position, target_position,
            border_width,
        )
        color = (90, 150, 210) if state.used_capacity else self.CONN_FILL
        pygame.draw.line(
            screen, color, source_position, target_position,
            max(1, border_width - 3),
        )
        capacity = (
            "∞" if state.capacity == float("inf") else str(state.capacity)
        )
        usage = f"{state.used_capacity}/{capacity}"
        if state.in_transit:
            usage += f" ({state.in_transit} in transit)"
        label = self.font.render(usage, True, (210, 220, 235))
        label_rect = label.get_rect()
        label_rect.midbottom = (
            (source_position[0] + target_position[0]) // 2,
            (source_position[1] + target_position[1]) // 2 - 6,
        )
        screen.blit(label, label_rect)
```

**Lecture du code.** Ignore les liens sans longueur à l'écran, dessine une bande de fond et une bande intérieure dépendant de l'occupation, puis les compteurs de capacité et de transit.

**Variables, noms et cohérence.** `source_position` et `target_position` sont des pixels ; `BAND_WIDTH` fixe désormais l'épaisseur, sans zoom.

**Décision à prendre.** **MODIFIÉ** : suppression du paramètre zoom.

<a id="m074"></a>

### 74 — `HubRenderer.draw`

**Source :** [`src/view/graph_renderer.py`, ligne 59](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L59)

```python
    def draw(
        self,
        screen: pygame.Surface,
        zone: HubState,
        position: tuple[int, int],
        is_terminal: bool = False,
    ) -> None:
        """Draw a hub using only the selected turn's recorded values."""
        radius = self.radius(zone)
        if zone.color == "rainbow":
            count = len(self.RAINBOW_COLORS)
            for index, color in enumerate(self.RAINBOW_COLORS):
                ring_radius = max(1, radius * (count - index) // count)
                pygame.draw.circle(screen, color, position, ring_radius)
        else:
            pygame.draw.circle(
                screen, self.COLOR_MAP.get(zone.color, (200, 200, 200)),
                position, radius,
            )
        pygame.draw.circle(
            screen, (255, 215, 0) if is_terminal else (255, 255, 255),
            position, radius, 3 if is_terminal else 2,
        )
        label = self.font.render(zone.name, True, (230, 230, 235))
        label_rect = label.get_rect()
        label_rect.midbottom = (position[0], position[1] - radius - 6)
        screen.blit(label, label_rect)

        capacity = "∞" if zone.capacity == float("inf") else str(zone.capacity)
        occupancy = f"{zone.nb_drones}/{capacity}"
        if zone.reserved:
            occupancy += f" +{zone.reserved} reserved"
        info = self.font.render(occupancy, True, (255, 255, 255))
        info_rect = info.get_rect()
        info_rect.midtop = (position[0], position[1] + radius + 6)
        screen.blit(info, info_rect)
```

**Lecture du code.** Dessine un disque normal pour les couleurs classiques. Si `zone.color == 'rainbow'`, dessine sept disques pleins concentriques avec des rayons décroissants : rouge, orange, jaune, vert, cyan, indigo, violet. Dessine ensuite le contour, le nom, l'occupation/capacité et les réservations.

**Variables, noms et cohérence.** `RAINBOW_COLORS` contient sept RGB distincts. `count`, `index` et `ring_radius` assurent l'empilement du plus grand au plus petit. Les couleurs inconnues conservent le gris de repli.

**Décision à prendre.** **MODIFIÉ** : vrai rendu `rainbow` concentrique, sans zoom.

<a id="m075"></a>

### 75 — `HubRenderer.radius`

**Source :** [`src/view/graph_renderer.py`, ligne 53](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/graph_renderer.py#L53)

```python
    def radius(self, zone: HubState) -> int:
        """Compute a bounded pixel radius from hub capacity."""
        radius = self.HUB_BASE_RADIUS + zone.capacity * self.HUB_SCALE
        radius = max(self.HUB_MIN_RADIUS, min(self.HUB_MAX_RADIUS, radius))
        return int(radius)
```

**Lecture du code.** Calcule le rayon à partir de la capacité puis le borne entre des tailles minimales et maximales ; la capacité infinie de start/end reste correctement bornée.

**Variables, noms et cohérence.** Le paramètre `zoom` a disparu ; le rayon est fixe en pixels.

**Décision à prendre.** **MODIFIÉ** : suppression du zoom, calcul borné conservé.

<a id="m076"></a>

### 76 — `ReplayPlayer.draw`

**Source :** [`src/view/replay_player.py`, ligne 87](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L87)

```python
    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        hub_positions: Mapping[str, tuple[float, float]],
    ) -> None:
        """Draw one representative per hub and all drones in transit."""
        if not self.frames:
            return

        current_frame = self.frames[
            self.current_index
        ]

        representatives: dict[str, int] = {}
        for drone_id, state in current_frame.drones.items():
            recorded_position = state.current_position
            if isinstance(recorded_position, str):
                representatives[recorded_position] = min(
                    drone_id,
                    representatives.get(recorded_position, drone_id),
                )

        for drone_id, state in current_frame.drones.items():
            if (
                isinstance(state.current_position, str)
                and drone_id != representatives[state.current_position]
            ):
                continue

            position = self._state_position(
                state, hub_positions,
            )

            screen_position = (int(position[0]), int(position[1]))

            self._draw_drone(
                screen,
                screen_position,
                drone_id,
                font,
            )
```

**Lecture du code.** Prend le plus petit ID comme représentant des drones présents sur un même hub et affiche tous les drones encore en transit. `_state_position` donne la position écran du hub ou le milieu de la connexion ; `_draw_drone` dessine directement.

**Variables, noms et cohérence.** `hub_positions` est une `Mapping[str, tuple[float, float]]` acceptant des coordonnées écran calculées dans la vue. Il n'y a plus de transformation par la caméra.

**Décision à prendre.** **MODIFIÉ** : coordonnées écran partagées avec GraphRenderer ; caméra supprimée.

<a id="m077"></a>

### 77 — `ReplayPlayer._state_position`

**Source :** [`src/view/replay_player.py`, ligne 72](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L72)

```python
    def _state_position(
        self,
        state: DroneState,
        hub_positions: dict[str, tuple[float, float]],
```

**Lecture du code.** Si la position est un nom de Hub, renvoie sa coordonnée monde ; si c'est le couple d'extrémités d'une connexion, renvoie le **milieu géométrique**. Cela représente le drone au milieu pendant son transit restricted.

**Variables, noms et cohérence.** `position` a deux types (`str | tuple[str,str]`) : la distinction correspond exactement à `DroneState.current_position`. Pour un transit de deux tours, cette méthode n'interpole pas une progression continue : elle choisit le milieu fixe dans une frame.

**Décision à prendre.** Conserver si la visualisation reste tour par tour ; une animation fluide demanderait une autre donnée temporelle.

<a id="m078"></a>

### 78 — `ReplayPlayer._draw_drone`

**Source :** [`src/view/replay_player.py`, ligne 140](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L140)

```python
    def _draw_drone(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        drone_id: int,
        font: pygame.font.Font,
```

**Lecture du code.** Calcule la couleur selon l'ID, construit trois sommets autour de la position, dessine un triangle plein avec contour blanc, puis rend l'étiquette `D_<id>` à droite.

**Variables, noms et cohérence.** `size=10` fixe la taille du triangle en pixels, comme les hubs : aucun zoom interactif. `position` est en pixels ; les coordonnées de points sont calculées à partir du centre.

**Décision à prendre.** Conserver la taille fixe en pixels et l'étiquette lisible.

<a id="m079"></a>

### 79 — `ReplayPlayer._drone_color`

**Source :** [`src/view/replay_player.py`, ligne 28](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L28)

```python
    def _drone_color(
        self,
        drone_id: int,
```

**Lecture du code.** Assigne l'une des six couleurs de `DRONE_COLORS` selon `(drone_id-1) % len(...)`. Les drones ont une couleur stable d'un tour à l'autre ; les couleurs se répètent à partir du septième.

**Variables, noms et cohérence.** `color_index` est correct ; `DRONE_COLORS` n'est pas une couleur stockée dans le modèle. La répétition est intentionnelle pour une palette courte.

**Décision à prendre.** Conserver.

<a id="m080"></a>

### 80 — `ReplayPlayer.draw_overlay`

**Source :** [`src/view/replay_player.py`, ligne 185](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/view/replay_player.py#L185)

```python
    def draw_overlay(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
```

**Lecture du code.** Affiche le numéro de tour courant sur le dernier tour (`Turn X/Y`), les raccourcis du replay et une légende des capacités des hubs/connexions. Écrit directement sur la surface Pygame, sans modifier le modèle.

**Variables, noms et cohérence.** Le label `Turn X/Y` reprend les snapshots, donc tour zéro visible au début. L'aide affiche gauche/droite/R mais pas Échap/C/zoom/drag, gérés par PygameView : une incohérence d'interface, pas une erreur de simulation.

**Décision à prendre.** À discuter : compléter l'aide affichée et éviter de dupliquer les descriptions de contrôles.


---

## VII. Méthodes spéciales et exceptions non déclenchées par le chemin nominal

<a id="m081"></a>

### 81 — `Connection.__repr__`

**Source :** [`src/model/connection.py`, ligne 43](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/connection.py#L43)

```python
    def __repr__(self) -> str:
        """Return a detailed connection representation for debugging."""
        return (
            f"Connection(source={self.source.name}, target={self.target.name},"
            f" capacity={self.capacity}, used_capacity={self.used_capacity})"
        )
```

**Lecture du code.** Renvoie une représentation textuelle d'une connexion avec noms des extrémités, capacité et usage. Python l'utilise lors d'un `repr(obj)` ou lorsqu'on inspecte des listes/objets en console, même si le programme ne l'appelle pas explicitement.

**Variables, noms et cohérence.** Ce n'est pas automatiquement du code mort : c'est une méthode spéciale de diagnostic. Le choix de la conserver dépend de ton souhait de déboguer le projet interactif.

**Décision à prendre.** À discuter : garder une représentation informative ou s'en passer pour alléger.

<a id="m082"></a>

### 82 — `Hub.__str__`

**Source :** [`src/model/hub.py`, ligne 71](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L71)

```python
    def __str__(self) -> str:
        """Describe the hub properties and current occupancy."""
        return (
            f"Hub(name={self.name}, color={self.color}, "
            f"zone_type={self.zone_type}, capacity={self.capacity}, "
            f"nb_drones={self.nb_drones}, x={self.x}, y={self.y})"
        )
```

**Lecture du code.** Renvoie une chaîne décrivant nom, couleur, type, capacité, occupation et coordonnées. Elle peut être utilisée par `str(hub)` et par des sorties de debug.

**Variables, noms et cohérence.** `nb_drones` est montré mais **pas `reserved`**, alors que les réservations sont essentielles aux bugs de capacité ; la représentation de debug est donc incomplète si on veut diagnostiquer les transits.

**Décision à prendre.** À discuter : supprimer la méthode si aucun diagnostic ne l'utilise, ou ajouter `reserved` pour la rendre réellement utile.

<a id="m083"></a>

### 83 — `Hub.__repr__`

**Source :** [`src/model/hub.py`, ligne 79](https://github.com/Irohs6/fly_in_v2/blob/test-main/src/model/hub.py#L79)

```python
    def __repr__(self) -> str:
        """Return the hub description for debugging."""
        return self.__str__()
```

**Lecture du code.** Réutilise `self.__str__()` afin que l'affichage d'un Hub dans une liste ou dans une console ressemble à `str(hub)`.

**Variables, noms et cohérence.** `__repr__` et `__str__` doublent intentionnellement l'interface Python, mais pas le code de formatage. Python appelle `__repr__` implicitement dans divers contextes, donc l'absence d'appel écrit n'est pas une preuve de code mort.

**Décision à prendre.** À discuter : nécessité de deux méthodes spéciales pour un projet scolaire.

## VIII. Les classes qui ne définissent pas de méthode explicite

Les `TypedDict` `HubDict`, `ConnectionDict` et `ParsedMap` dans `parser.py` définissent la **forme des dictionnaires**. `Parser` fabrique ces structures, `MapValidator` les valide, `Graph` les transforme en vrais objets. Elles ne possèdent pas de méthode applicative : inutile d'inventer un objet `Hub` dans le parser.

`src/model/state.py` contient quatre `@dataclass(frozen=True)` : `DroneState` (position/état/chemin), `HubState` (coordonnées/occupation/réservations), `ConnectionState` (connexion/usage/transit) et `TurnState` (ensemble d'un tour, avec `moved_drones`). Elles sont créées par `Recorder.record` et lues par les vues. Elles **n'ont aucune méthode `def` écrite dans le fichier**, Python génère certaines méthodes spéciales. Leur `frozen=True` ne rend pas immuables les dictionnaires contenues dans `TurnState`.

`ParseError`, `ValidatorError`, `DisplayError`, `ConnectionError` et `HubError` sont des classes d'exception sans constructeur spécifique. Les deux dernières gardent leur rôle d'exception métier pour les opérations sur `Connection` et `Hub`. Tous les appels relevés fournissent un message explicite.

Le `src/view/__init__.py` configure `PYGAME_HIDE_SUPPORT_PROMPT=1` pour éviter que Pygame imprime une bannière qui polluerait la sortie terminal du sujet. Dans `main.py`, le bloc `if __name__ == "__main__": raise SystemExit(main())` convertit le code retour en statut processus.

## IX. Points à discuter en priorité, **sans aucune modification automatique**

| Priorité de relecture | Observation dans le code | Changement éventuel |
|---|---|---|
| 1 | `main.main` manipule `map_paths` alors qu'une seule carte est admise | Une variable unique |
| 2 | `Controller.run` utilise `data` et `frames` | `parsed_map` et `turn_states` |
| 3 | `Parser.parse_hub` utilise `hub_type` pour start/hub/end et `zone_type` pour normal/restricted | `declaration_type` |
| 4 | `Parser.parse_connection` alterne `edge_raw` et `connection` | Un seul vocabulaire |
| 5 | `MapValidator` utilise `names` et `checked_conn` pour des dictionnaires de **lignes** | `hub_name_lines` et `connection_lines` |
| 6 | `Graph._build_connections` reçoit des données déjà validées mais les appelle `raw_connections` | `connection_data` |
| 7 | `Hub.nb_drones` et `Hub.reserved` mélangent unités implicites | `occupants` et `reserved_slots` selon préférence |
| 8 | `Drone.move_to_zone` vs `Hub` et `HubRenderer.draw(zone=...)` | Unifier `zone` et `hub` |
| 9 | `Drone.advance_transit()` **termine** un trajet et `path_turns()` fournit un **coût** de chemin | `finish_transit` et `remaining_path_cost` |
| 10 | `Simulation.move_drone` est publique mais suppose des vérifications faites ailleurs | Rendre privée ou documenter la précondition |
| 11 | `Hub.remove_drone` teste `nb_drones - 1 < 0` | Test direct `nb_drones <= 0` |
| 13 | `Hub.__str__` ne montre pas `reserved` | Ajouter ce champ ou supprimer un debug non utilisé |
| 15 | `ReplayPlayer.restart` revient au début du **replay**, sans relancer le moteur | `reset_replay` |
| 17 | `Simulation.simulate` ne détecte pas un état sans progression | Construire d'abord un cas reproductible, puis décider |
| 18 | `Simulation._move_or_wait` bloque les retours vers `previous_zone` et refuse les détours > coût+2 | Choix métier / heuristique à retester avec cartes précises |
| 19 | `Connection` emploie `source/target` pour un lien bidirectionnel | Conserver pour coller au fichier ou renommer `endpoint_a/b` |
| 20 | Le parser et le validateur importent leurs types dans des sens qui obligent un import local | Conserver ou isoler les TypedDict, mais pas inventer de complexité sans besoin |

## X. Vérification technique et limites

**Simplification effectuée :** `ConnectionError.__init__` et `HubError.__init__` ont été supprimés après vérification des appels. Les classes métier restent définies dans `src/model/errors.py` avec un simple `pass`. Le présent inventaire recense donc **83 méthodes**, et les sections 84 et 85 précédentes n'ont plus lieu d'être. La vérification automatisée citée plus bas ne couvre pas encore cette suppression.


**Actualisation du 2 novembre 2026 :** suppression des huit méthodes de caméra et du module `camera.py` ; l'inventaire comptait alors 85 méthodes, puis 83 après suppression des deux constructeurs d'exceptions. La fenêtre ajuste automatiquement les positions au cadre, sans zoom/pan. `rainbow` est dessiné par sept disques concentriques. Les six méthodes d'affichage modifiées figurent ci-dessus avec leur code réel.


Le [dernier workflow de vérification après les modifications graphiques](https://github.com/Irohs6/fly_in_v2/actions/runs/41425411792) a réussi : **206 tests**, **11 cartes sur 11**, **Flake8 et mypy sans erreur** (35 fichiers Python vérifiés). Cela couvre les tests exécutés, pas tous les graphes possibles.

**Les propositions encore listées au tableau IX ne sont pas appliquées dans le code**. Ce rapport te laisse décider, après lecture, quelles modifications valent la peine et dans quel ordre les réaliser. Sauf mention explicite, les remarques « à discuter » sont des recommandations de clarté, non des bugs prouvés.
