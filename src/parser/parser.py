import math
import re
from typing import TypedDict


class HubDict(TypedDict):
    """Parsed hub identity, coordinates, type and capacity."""
    name: str
    x: int
    y: int
    color: str
    capacity: float
    zone_type: str


class ConnectionDict(TypedDict):
    """Parsed connection endpoint names and capacity."""
    source: str
    target: str
    capacity: float


class ParsedMap(TypedDict):
    """Validated map with drone count, terminal hubs and connections."""
    map_path: str
    nb_drones: int
    start_hub: HubDict
    hubs: list[HubDict]
    end_hub: HubDict
    connections: list[ConnectionDict]


class ParseError(Exception):
    """Error while parsing a Fly-in map file."""

    pass


class Parser:
    """Object-oriented parser for Fly-in map files."""

    def __init__(self, file_path: str):
        """Store the file path and initialize parser state without reading
        it.
        """
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
        """Read a UTF-8 map, skipping empty lines and comment-only lines.
        Preserve line numbers and wrap read or decoding failures in
        ParseError with the file path.
        """
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
                f"Map {self.file_path!r}: invalid UTF-8 encoding."
            ) from exc
        except OSError as exc:
            raise ParseError(
                f"Cannot read map {self.file_path!r}: "
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
        """Parse a hub declaration and its metadata."""

        zone_raw, marker, meta_raw = raw.partition("[")
        parts = zone_raw.split()
        if len(parts) != 3:
            raise ParseError(
                f"Line {nb_line}: invalid hub declaration: {raw!r}. "
                "Expected format: <name> <x> <y> [meta]"
            )

        name, x_str, y_str = parts
        if "-" in name:
            raise ParseError(
                f"Line {nb_line}: invalid hub name: {name!r} "
                "(hyphens are not allowed)."
            )
        x = self._parse_integer(x_str, nb_line, "x coordinate")
        y = self._parse_integer(y_str, nb_line, "y coordinate")
        meta = self.parse_meta(
            marker + meta_raw,
            nb_line,
            {"zone", "color", "capacity", "max_drones"},
        )

        color = meta.get("color", "gray")
        if "max_drones" in meta and "capacity" in meta:
            raise ParseError(
                f"Line {nb_line}: duplicate metadata: "
                "capacity is already defined."
            )
        cap_raw = meta.get("max_drones") or meta.get("capacity") or "1"
        capacity = (
            math.inf if is_start or is_end
            else self._parse_integer(
                cap_raw, nb_line, "capacity", positive=True,
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
                f"Line {nb_line}: a hub cannot be both start and end."
            )

        if is_start:
            self.start_zone = zone
        elif is_end:
            self.end_zone = zone
        else:
            self.hub_zones.append(zone)
        self.zone_entries.append((zone, nb_line))

    # --- Parsing des connexions ---
    def parse_connection(self, raw: str, nb_line: int) -> None:
        """Parse a connection declaration and its metadata."""

        edge_raw, marker, meta_raw = raw.partition("[")
        edge = edge_raw.strip()

        if edge.count("-") != 1:
            raise ParseError(
                f"Line {nb_line}: invalid connection: {raw!r}. "
                "Expected format: <source>-<target> [meta]"
            )

        source, target = edge.split("-", 1)
        source = source.strip()
        target = target.strip()

        if (
            not source or not target
            or any(char.isspace() for char in source + target)
        ):
            raise ParseError(f"Line {nb_line}: invalid connection: {raw!r}.")

        meta = self.parse_meta(
            marker + meta_raw,
            nb_line,
            {"capacity", "max_link_capacity"},
        )
        if "max_link_capacity" in meta and "capacity" in meta:
            raise ParseError(
                f"Line {nb_line}: duplicate metadata: "
                "capacity is already defined."
            )
        cap_raw = meta.get("max_link_capacity") or meta.get("capacity") or "1"
        capacity = self._parse_integer(
            cap_raw, nb_line, "capacity", positive=True,
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
        """Validate a complete metadata block and its allowed keys."""
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
                f"Line {nb_line}: invalid metadata: {raw!r}"
            )

        meta: dict[str, str] = {}
        for item in meta_raw[1:-1].split():
            if item.count("=") != 1:
                raise ParseError(
                    f"Line {nb_line}: invalid metadata item: {item!r}"
                )
            key, value = item.split("=", 1)
            if not key or not value:
                raise ParseError(
                    f"Line {nb_line}: invalid metadata item: {item!r}"
                )
            if key not in allowed_keys:
                raise ParseError(
                    f"Line {nb_line}: unknown metadata key {key!r}"
                )
            if key in meta:
                raise ParseError(
                    f"Line {nb_line}: duplicate metadata: {key!r}"
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
        """Convert a decimal integer, reporting errors with line and field
        context.
        """
        pattern = r"[0-9]+" if positive else r"[+-]?[0-9]+"
        error = f"Line {nb_line}: invalid {field}: {raw!r}"
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
        """Read, parse and validate a complete map."""
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
                "missing nb_drones."
            )

        if self.start_zone is None:
            raise ParseError(
                "missing start_hub."
            )

        if self.end_zone is None:
            raise ParseError(
                "missing end_hub."
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
        """Interpret input lines while preserving line numbers. Require
        nb_drones on the first meaningful line, then recognize hub and
        connection declarations. Raise ParseError for invalid syntax.
        """
        if not self.lines:
            raise ParseError("No lines to parse. Please read the file first.")

        first_number, first_line = self.lines[0]
        first_keyword = first_line.partition(":")[0].strip()
        if first_keyword not in ("nb_drones", "drones", "nb_drone"):
            raise ParseError(
                f"Line {first_number}: the first line must define "
                "nb_drones: <positive integer>."
            )

        for nb_line, line in self.lines:
            keyword, separator, raw = line.partition(":")
            keyword = keyword.strip()
            raw = raw.strip()
            if not separator or not raw:
                raise ParseError(
                    f"Line {nb_line}: invalid line: {line!r}. "
                    "Expected format: <keyword>: <value>."
                )

            if keyword in ("nb_drones", "drones", "nb_drone"):
                if self.nb_drones is not None:
                    raise ParseError(
                        f"Line {nb_line}: nb_drones is already defined."
                    )
                self.nb_drones = self._parse_integer(
                    raw, nb_line, "nb_drones", positive=True,
                )
            elif keyword == "start_hub":
                if self.start_zone is not None:
                    raise ParseError(
                        f"Line {nb_line}: start_hub is already defined."
                    )
                self.parse_hub_zone(raw, nb_line, is_start=True)
            elif keyword == "hub":
                self.parse_hub_zone(raw, nb_line)
            elif keyword == "end_hub":
                if self.end_zone is not None:
                    raise ParseError(
                        f"Line {nb_line}: end_hub is already defined."
                    )
                self.parse_hub_zone(raw, nb_line, is_end=True)
            elif keyword == "connection":
                self.parse_connection(raw, nb_line)
            else:
                raise ParseError(
                    f"Line {nb_line}: unknown declaration: {line!r}"
                )
