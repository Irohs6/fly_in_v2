import math
import re
from typing import TypedDict


class HubDict(TypedDict):
    name: str
    x: int
    y: int
    color: str
    capacity: float
    zone_type: str


class ConnectionDict(TypedDict):
    source: str
    target: str
    capacity: float


class ParsedMap(TypedDict):
    map_path: str
    nb_drones: int
    start_hub: HubDict
    hubs: list[HubDict]
    end_hub: HubDict
    connections: list[ConnectionDict]


class ParseError(Exception):
    """Erreur de parsing du fichier de carte Fly-in."""

    pass


class Parser:
    """Parser orienté objet pour les fichiers Fly-in."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines: list[tuple[int, str]] = []
        self.hub_zones: list[HubDict] = []
        self.zone_entries: list[tuple[HubDict, int]] = []
        self.connections: list[ConnectionDict] = []
        self.connection_entries: list[tuple[ConnectionDict, int]] = []
        self.nb_drones: int | None = None
        self.start_zone: HubDict | None = None
        self.end_zone: HubDict | None = None

    # --- Lecture du fichier ---
    def read(self) -> None:
        """Lit le fichier Fly-in, supprime les commentaires et lignes vides."""
        self.lines = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as maps_file:
                for nb_line, raw in enumerate(maps_file, start=1):
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    self.lines.append((nb_line, line))
        except UnicodeDecodeError as exc:
            raise ParseError(
                f"Carte {self.file_path!r}: encodage UTF-8 invalide."
            ) from exc
        except OSError as exc:
            raise ParseError(
                f"Impossible de lire la carte {self.file_path!r}: "
                f"{exc.strerror or str(exc)}"
            ) from exc

    # --- Parsing des zones ---
    def parse_hub_zone(
        self,
        raw: str,
        nb_line: int,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Parse une ligne de zone de hub."""

        zone_raw, marker, meta_raw = raw.partition("[")
        parts = zone_raw.split()
        if len(parts) != 3:
            raise ParseError(
                f"Ligne {nb_line}: zone de hub invalide: {raw!r}. "
                "Format attendu: <nom> <x> <y> [meta]"
            )

        name, x_str, y_str = parts
        if "-" in name:
            raise ParseError(
                f"Ligne {nb_line}: nom de zone invalide: {name!r} "
                "(tirets interdits)."
            )
        x = self._parse_integer(x_str, nb_line, "coordonnée x")
        y = self._parse_integer(y_str, nb_line, "coordonnée y")
        meta = self.parse_meta(
            marker + meta_raw, nb_line, {"zone", "color", "capacity"},
        )

        color = meta.get("color", "gray")
        capacity = (
            math.inf if is_start or is_end
            else self._parse_integer(
                meta.get("capacity", "1"), nb_line, "capacity", positive=True,
            )
        )
        zone_type = meta.get("zone", "normal")

        zone: HubDict = {
            "name": name,
            "x": x,
            "y": y,
            "color": color,
            "capacity": capacity,
            "zone_type": zone_type,
        }

        if is_start and is_end:
            raise ParseError(
                f"Ligne {nb_line}: une zone ne peut pas être start et end."
            )

        if is_start:
            zone["capacity"] = math.inf
            self.start_zone = zone
            self.zone_entries.append((zone, nb_line))
            return

        if is_end:
            zone["capacity"] = math.inf
            self.end_zone = zone
            self.zone_entries.append((zone, nb_line))
            return

        self.hub_zones.append(zone)
        self.zone_entries.append((zone, nb_line))

    # --- Parsing des connexions ---
    def parse_connection(self, raw: str, nb_line: int) -> None:
        """Parse une ligne de connection."""

        edge_raw, marker, meta_raw = raw.partition("[")
        edge = edge_raw.strip()

        if edge.count("-") != 1:
            raise ParseError(
                f"Ligne {nb_line}: connection invalide: {raw!r}. "
                "Format attendu: <source>-<target> [meta]"
            )

        source, target = edge.split("-", 1)
        source = source.strip()
        target = target.strip()

        if (
            not source or not target
            or any(char.isspace() for char in source + target)
        ):
            raise ParseError(f"Ligne {nb_line}: connection invalide: {raw!r}.")

        meta = self.parse_meta(marker + meta_raw, nb_line, {"capacity"})
        capacity = self._parse_integer(
            meta.get("capacity", "1"), nb_line, "capacity", positive=True,
        )

        self.connections.append(
            {
                "source": source,
                "target": target,
                "capacity": capacity,
            }
        )
        self.connection_entries.append((self.connections[-1], nb_line))

    # --- Parsing des métadonnées ---
    def parse_meta(
        self,
        raw: str,
        nb_line: int,
        allowed_keys: set[str],
    ) -> dict[str, str]:
        """Valide un bloc complet de métadonnées et ses clés autorisées."""
        if not raw:
            return {}

        meta_raw = raw.strip()
        if (
            not meta_raw.startswith("[")
            or not meta_raw.endswith("]")
            or "[" in meta_raw[1:]
            or "]" in meta_raw[:-1]
        ):
            raise ParseError(
                f"Ligne {nb_line}: métadonnées invalides: {raw!r}"
            )

        meta: dict[str, str] = {}
        for item in meta_raw[1:-1].split():
            if item.count("=") != 1:
                raise ParseError(
                    f"Ligne {nb_line}: métadonnée invalide: {item!r}"
                )
            key, value = item.split("=", 1)
            if not key or not value:
                raise ParseError(
                    f"Ligne {nb_line}: métadonnée invalide: {item!r}"
                )
            if key not in allowed_keys:
                raise ParseError(
                    f"Ligne {nb_line}: clé de métadonnée inconnue {key!r}"
                )
            if key in meta:
                raise ParseError(
                    f"Ligne {nb_line}: métadonnée dupliquée: {key!r}"
                )
            meta[key] = value
        return meta

    @staticmethod
    def _parse_integer(
        raw: str,
        nb_line: int,
        field: str,
        *,
        positive: bool = False,
    ) -> int:
        """Convertit un entier décimal avec une erreur contextualisée."""
        pattern = r"[0-9]+" if positive else r"[+-]?[0-9]+"
        error = f"Ligne {nb_line}: {field} invalide: {raw!r}"
        if re.fullmatch(pattern, raw) is None:
            raise ParseError(error)
        try:
            value = int(raw)
        except ValueError as exc:
            raise ParseError(error) from exc
        if positive and value <= 0:
            raise ParseError(error)
        return value

    # --- Parsing global ---
    def parse(self) -> ParsedMap:
        """Lit, parse puis valide entièrement une carte."""
        from src.parser.validator import MapValidator, ValidationError

        # De nouvelles listes préservent les résultats d'un précédent parse.
        self.hub_zones = []
        self.zone_entries = []
        self.connections = []
        self.connection_entries = []
        self.nb_drones = None
        self.start_zone = None
        self.end_zone = None
        self.read()
        self.parse_lines()
        if self.nb_drones is None:
            raise ParseError(
                "nb_drones manquant."
            )

        if self.start_zone is None:
            raise ParseError(
                "start_hub manquant."
            )

        if self.end_zone is None:
            raise ParseError(
                "end_hub manquant."
            )

        validator = MapValidator(
            self.nb_drones,
            self.start_zone,
            self.end_zone,
            self.hub_zones,
            self.connections,
            self.zone_entries,
            self.connection_entries,
        )

        try:
            validator.validate()
        except ValidationError as exc:
            raise ParseError(str(exc)) from exc

        return {
            "map_path": self.file_path,
            "nb_drones": self.nb_drones,
            "start_hub": self.start_zone,
            "hubs": self.hub_zones,
            "end_hub": self.end_zone,
            "connections": self.connections,
        }

    # --- Parsing des lignes ---
    def parse_lines(self) -> None:
        if not self.lines:
            raise ParseError("No lines to parse. Please read the file first.")

        first_number, first_line = self.lines[0]
        if first_line.partition(":")[0].strip() != "nb_drones":
            raise ParseError(
                f"Ligne {first_number}: la première ligne doit définir "
                "nb_drones: <entier positif>."
            )

        for nb_line, line in self.lines:
            keyword, separator, raw = line.partition(":")
            keyword = keyword.strip()
            raw = raw.strip()
            if not separator or not raw:
                raise ParseError(
                    f"Ligne {nb_line}: ligne invalide: {line!r}. "
                    "Format attendu: <mot-clé>: <valeur>."
                )

            if keyword == "nb_drones":
                if self.nb_drones is not None:
                    raise ParseError(
                        f"Ligne {nb_line}: nb_drones déjà défini."
                    )
                self.nb_drones = self._parse_integer(
                    raw, nb_line, "nb_drones", positive=True,
                )
            elif keyword == "start_hub":
                if self.start_zone is not None:
                    raise ParseError(
                        f"Ligne {nb_line}: start_hub déjà défini."
                    )
                self.parse_hub_zone(raw, nb_line, is_start=True)
            elif keyword == "hub":
                self.parse_hub_zone(raw, nb_line)
            elif keyword == "end_hub":
                if self.end_zone is not None:
                    raise ParseError(f"Ligne {nb_line}: end_hub déjà défini.")
                self.parse_hub_zone(raw, nb_line, is_end=True)
            elif keyword == "connection":
                self.parse_connection(raw, nb_line)
            else:
                raise ParseError(f"Ligne {nb_line}: ligne inconnue: {line!r}")
