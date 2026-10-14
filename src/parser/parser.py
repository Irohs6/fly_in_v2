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

    # --- Lecture du fichier ---
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

    # --- Parsing des zones ---
    def parse_hub(
        self,
        keyword: str,
        raw: str,
        line_number: int,
    ) -> None:
        """Parse a hub and its metadata, rejecting repeated start or end
        declarations.
        """
        if keyword == "start_hub" and self.start_hub is not None:
            raise ParseError(
                f"Line {line_number}: start_hub is already defined."
            )

        if keyword == "end_hub" and self.end_hub is not None:
            raise ParseError(
                f"Line {line_number}: end_hub is already defined."
            )

        zone_raw, marker, meta_raw = raw.partition("[")
        parts = zone_raw.split()
        if len(parts) != 3:
            raise ParseError(
                f"Line {line_number}: invalid hub declaration: {raw!r}. "
                "Expected format: <name> <x> <y> [meta]"
            )

        name, x_str, y_str = parts
        if "-" in name:
            raise ParseError(
                f"Line {line_number}: invalid hub name: {name!r} "
                "(hyphens are not allowed)."
            )
        x = self._parse_integer(x_str, line_number, "x coordinate")
        y = self._parse_integer(y_str, line_number, "y coordinate")
        meta = self.parse_metadata(
            marker + meta_raw,
            line_number,
            {"zone", "color", "capacity", "max_drones"},
        )

        color = meta.get("color", "gray")
        if "max_drones" in meta and "capacity" in meta:
            raise ParseError(
                f"Line {line_number}: duplicate metadata: "
                "capacity is already defined."
            )
        cap_raw = meta.get("max_drones") or meta.get("capacity") or "1"
        capacity = (
            math.inf if keyword in ("start_hub", "end_hub")
            else self._parse_integer(
                cap_raw, line_number, "capacity", positive=True,
            )
        )
        zone_type = meta.get("zone", "normal")

        hub: HubDict = {
            "name": name,
            "x": x,
            "y": y,
            "color": color,
            "capacity": capacity,
            "zone_type": zone_type,
        }

        if keyword == "start_hub":
            self.start_hub = hub
        elif keyword == "end_hub":
            self.end_hub = hub
        self.hub_entries.append((hub, line_number))

    # --- Parsing des connexions ---
    def parse_connection(self, raw: str, line_number: int) -> None:
        """Parse a connection declaration and its metadata."""

        edge_raw, marker, meta_raw = raw.partition("[")
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
            marker + meta_raw,
            line_number,
            {"capacity", "max_link_capacity"},
        )
        if "max_link_capacity" in meta and "capacity" in meta:
            raise ParseError(
                f"Line {line_number}: duplicate metadata: "
                "capacity is already defined."
            )
        cap_raw = meta.get("max_link_capacity") or meta.get("capacity") or "1"
        capacity = self._parse_integer(
            cap_raw, line_number, "capacity", positive=True,
        )

        connection: ConnectionDict = {
            "source": source,
            "target": target,
            "capacity": capacity,
        }
        self.connection_entries.append((connection, line_number))

    # --- Parsing des métadonnées ---
    def parse_metadata(
        self,
        raw: str,
        line_number: int,
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
                f"Line {line_number}: invalid metadata: {raw!r}"
            )

        meta: dict[str, str] = {}
        for item in meta_raw[1:-1].split():
            if item.count("=") != 1:
                raise ParseError(
                    f"Line {line_number}: invalid metadata item: {item!r}"
                )
            key, value = item.split("=", 1)
            if not key or not value:
                raise ParseError(
                    f"Line {line_number}: invalid metadata item: {item!r}"
                )
            if key not in allowed_keys:
                raise ParseError(
                    f"Line {line_number}: unknown metadata key {key!r}"
                )
            if key in meta:
                raise ParseError(
                    f"Line {line_number}: duplicate metadata: {key!r}"
                )
            meta[key] = value
        return meta

    @staticmethod
    def _parse_integer(
        raw: str,
        line_number: int,
        field: str,
        *,
        positive: bool = False,
    ) -> int:
        """Convert a decimal integer, reporting errors with line and field
        context.
        """
        pattern = r"[0-9]+" if positive else r"[+-]?[0-9]+"
        error_message = f"Line {line_number}: invalid {field}: {raw!r}"
        if re.fullmatch(pattern, raw) is None:
            raise ParseError(error_message)
        try:
            value = int(raw)
        except ValueError as error:
            raise ParseError(error_message) from error
        if positive and value <= 0:
            raise ParseError(error_message)
        return value

    # --- Parsing global ---
    def parse(self) -> ParsedMap:
        """Read, parse and validate a complete map."""
        from src.parser.validator import MapValidator, ValidationError

        # De nouvelles listes préservent les résultats d'un précédent parse.
        self.hub_entries = []
        self.connection_entries = []
        self.nb_drones = None
        self.start_hub = None
        self.end_hub = None
        self.read_file()
        if self.nb_drones is None:
            raise ParseError(
                f"Line {self.line_count}: missing nb_drones at end of file."
            )

        if self.start_hub is None:
            raise ParseError(
                f"Line {self.line_count}: missing start_hub at end of file."
            )

        if self.end_hub is None:
            raise ParseError(
                f"Line {self.line_count}: missing end_hub at end of file."
            )

        validator = MapValidator(
            start_hub=self.start_hub,
            end_hub=self.end_hub,
            hub_entries=self.hub_entries,
            connection_entries=self.connection_entries,
        )

        try:
            validator.validate()
        except ValidationError as error:
            raise ParseError(str(error)) from error

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

    # --- Parsing des lignes ---
    def parse_line(self, line: str, line_number: int) -> None:
        """Parse one declaration, requiring the drone count before any hub
        or connection. Report invalid syntax with its physical line number.
        """
        keyword, separator, raw = line.partition(":")
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

        if not separator or not raw:
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
