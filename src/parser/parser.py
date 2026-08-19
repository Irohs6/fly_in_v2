from pathlib import Path
import sys
import math
from typing import TypedDict

# ============================
# TypedDict : types structurés
# ============================


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


# ============================
# Exceptions
# ============================


class ParseError(Exception):
    """Erreur de parsing du fichier de carte Fly-in."""

    pass


# ============================
# Parser
# ============================


class Parser:
    """Parser orienté objet pour les fichiers Fly-in."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines: list[tuple[int, str]] = []
        self.hub_zones: list[HubDict] = []
        self.zone_entries: list[tuple[HubDict, int]] = []
        self.conections: list[ConnectionDict] = []
        self.connection_entries: list[tuple[ConnectionDict, int]] = []
        self.nb_drones: int | None = None
        self.start_zone: HubDict | None = None
        self.end_zone: HubDict | None = None
        self.validator: object | None = None

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
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")

    # --- Parsing des zones ---
    def parse_hub_zone(
        self,
        raw: str,
        nb_line: int,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Parse une ligne de zone de hub."""

        zone_raw, _, meta_raw = raw.partition("[")
        parts = zone_raw.split()
        if len(parts) != 3:
            raise ParseError(
                f"Ligne {nb_line}: zone de hub invalide: {raw!r}. "
                "Format attendu: <nom> <x> <y> [meta]"
            )

        name, x_str, y_str = parts
        if not name:
            raise ParseError(f"Ligne {nb_line}: nom de zone vide.")
        if not (x_str.lstrip("-").isdigit() and y_str.lstrip("-").isdigit()):
            raise ParseError(
                f"Ligne {nb_line}: coordonnées invalides: {x_str!r}, {y_str!r}"
            )

        x, y = int(x_str), int(y_str)
        meta = self.parse_meta(meta_raw, nb_line)

        color = meta.get("color", "gray")
        capacity = int(meta.get("capacity", 1))
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

        edge_raw, _, meta_raw = raw.partition("[")
        edge = edge_raw.strip()

        if "-" not in edge:
            raise ParseError(
                f"Ligne {nb_line}: connection invalide: {raw!r}. "
                "Format attendu: <source>-<target> [meta]"
            )

        source, target = edge.split("-", 1)
        source = source.strip()
        target = target.strip()

        if not source or not target:
            raise ParseError(f"Ligne {nb_line}: connection invalide: {raw!r}.")

        meta = self.parse_meta(meta_raw, nb_line)
        cap_raw = meta.get("capacity", "1")

        if not cap_raw.isdigit() or int(cap_raw) <= 0:
            raise ParseError(
                f"Ligne {nb_line}: capacity invalide: {cap_raw!r}"
            )

        self.conections.append(
            {
                "source": source,
                "target": target,
                "capacity": int(cap_raw),
            }
        )
        self.connection_entries.append((self.conections[-1], nb_line))

    # --- Parsing des métadonnées ---
    def parse_meta(self, raw: str, nb_line: int) -> dict[str, str]:
        """Parse les métadonnées d'une zone de hub."""

        if not raw:
            return {}

        meta_raw = raw.strip()
        if not meta_raw.endswith("]"):
            raise ParseError(
                f"Ligne {nb_line}: métadonnées invalides: {raw!r}"
            )

        meta: dict[str, str] = {}
        for item in meta_raw[:-1].split():
            error_msg = f"Ligne {nb_line}: métadonnée invalide: {item!r}"
            if "=" not in item:
                raise ParseError(error_msg)
            key, value = item.split("=", 1)
            if not key or not value:
                raise ParseError(error_msg)
            meta[key] = value

        return meta

    # --- Parsing global ---
    def parse(self) -> ParsedMap:
        """Lit, parse puis valide entièrement une carte."""
        from src.parser.validator import MapValidator, ValidationError

        self.read()
        self.parse_ligne()

        self.validator = MapValidator(
            self.nb_drones,
            self.start_zone,
            self.end_zone,
            self.hub_zones,
            self.conections,
            self.zone_entries,
            self.connection_entries,
        )

        try:
            self.validator.validate()
        except ValidationError as exc:
            raise ParseError(str(exc)) from exc

        # À ce stade, la carte est valide → on garantit au type checker
        # que les champs ne sont plus None.
        assert self.nb_drones is not None
        assert self.start_zone is not None
        assert self.end_zone is not None

        return {
            "map_path": self.file_path,
            "nb_drones": self.nb_drones,
            "start_hub": self.start_zone,
            "hubs": self.hub_zones,
            "end_hub": self.end_zone,
            "connections": self.conections,
        }

    # --- Parsing des lignes ---
    def parse_ligne(self) -> None:
        if not self.lines:
            raise ParseError("No lines to parse. Please read the file first.")

        first_line = self.lines[0][1]
        if first_line is None or not first_line.startswith("nb_drones"):
            raise ParseError(
                "First line must specify the number of drones : <int>."
            )

        for nb_line, line in self.lines:
            if line.startswith("nb_drones"):
                raw = line.split(":", 1)[1].strip()
                error_msg = f"Ligne {nb_line}: nb_drones invalide: {raw!r}"
                if not raw.isdigit():
                    raise ParseError(error_msg)
                nb_drones = int(raw)
                if nb_drones <= 0:
                    raise ParseError(error_msg)
                self.nb_drones = nb_drones

            elif line.startswith("start_hub"):
                if self.start_zone is not None:
                    raise ParseError(
                        f"Ligne {nb_line}: start_hub déjà défini."
                    )
                raw = line.split(":", 1)[1].strip()
                if not raw:
                    raise ParseError(
                        f"Ligne {nb_line}: start_hub invalide: {raw!r}"
                    )
                self.parse_hub_zone(raw, nb_line, is_start=True)

            elif line.startswith("hub"):
                raw = line.split(":", 1)[1].strip()
                if not raw:
                    raise ParseError(f"Ligne {nb_line}: hub invalide: {raw!r}")
                self.parse_hub_zone(raw, nb_line)

            elif line.startswith("end_hub"):
                if self.end_zone is not None:
                    raise ParseError(f"Ligne {nb_line}: end_hub déjà défini.")
                raw = line.split(":", 1)[1].strip()
                if not raw:
                    raise ParseError(
                        f"Ligne {nb_line}: end_hub invalide: {raw!r}"
                    )
                self.parse_hub_zone(raw, nb_line, is_end=True)

            elif line.startswith("connection"):
                raw = line.split(":", 1)[1].strip()
                if not raw:
                    raise ParseError(
                        f"Ligne {nb_line}: connection invalide: {raw!r}"
                    )
                self.parse_connection(raw, nb_line)

            else:
                raise ParseError(f"Ligne {nb_line}: ligne inconnue: {line!r}")


# ============================
# Formatage du résultat
# ============================


def _format_hub(hub: HubDict) -> str:
    return (
        f"{hub['name']} ({hub['x']}, {hub['y']}) "
        f"zone={hub['zone_type']} color={hub['color']} "
        f"cap={hub['capacity']}"
    )


def _format_connection(connection: ConnectionDict) -> str:
    return (
        f"{connection['source']} -> {connection['target']} "
        f"cap={connection['capacity']}"
    )


def format_parsing_result(data: ParsedMap) -> str:
    start_hub = data["start_hub"]
    end_hub = data["end_hub"]
    hubs = data["hubs"]
    connections = data["connections"]

    lines = [
        "=== Parsing Fly-in ===",
        f"Carte       : {data['map_path']}",
        f"Nb drones   : {data['nb_drones']}",
        f"Start hub   : {_format_hub(start_hub)}",
        f"End hub     : {_format_hub(end_hub)}",
        f"Hubs ({len(hubs)}):",
    ]

    for hub in hubs:
        lines.append(f"  - {_format_hub(hub)}")

    lines.append(f"Connections ({len(connections)}):")
    for connection in connections:
        lines.append(f"  - {_format_connection(connection)}")

    return "\n".join(lines)


# ============================
# Main
# ============================


def main() -> int:
    from src.controller.controller import Controller

    project_root = Path(__file__).resolve().parents[2]
    default_map = (
        project_root / "assets" / "maps" / "easy" / "02_simple_fork.txt"
    )

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = str(default_map)

    controller = Controller(file_path)
    try:
        data = controller.load_map()
    except (FileNotFoundError, ParseError) as exc:
        print(f"Erreur: {exc}")
        return 1

    print(format_parsing_result(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
