import math
from collections import deque
from .parser import ConnectionDict, HubDict


class ValidationError(Exception):
    """Error while validating map data."""
    pass


class MapValidator:
    """Validate parsed map data against the Fly-in rules and project limits."""

    MAX_DRONES = 200
    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def __init__(
        self,
        nb_drones: int | None,
        start_hub: HubDict,
        end_hub: HubDict,
        hubs: list[HubDict],
        connections: list[ConnectionDict],
        zone_entries: list[tuple[HubDict, int]],
        connection_entries: list[tuple[ConnectionDict, int]],
    ) -> None:

        """Store parsed data and declaration line numbers. zone_entries and
        connection_entries associate declarations with their lines for
        error reporting.
        """
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.connections = connections
        self.zone_entries = zone_entries
        self.connection_entries = connection_entries

    def validate(self) -> None:
        """Validate every section of the map."""
        self._validate_nb_drones()
        self._validate_zones()
        self._validate_connections()
        self._check_unique_zone_names()
        self._check_connection_endpoints()
        self._check_duplicate_connections()
        self._check_reachable_end()

    def _validate_nb_drones(self) -> None:
        """Require a positive drone count no greater than MAX_DRONES."""
        if not isinstance(self.nb_drones, int):
            raise ValidationError(
                "Line 1: missing nb_drones declaration."
            )
        if self.nb_drones <= 0:
            raise ValidationError(
                "Line 1: the drone count must be positive."
            )

        if self.nb_drones > self.MAX_DRONES:
            raise ValidationError(
                f"nb_drones: {self.nb_drones} drones requested, "
                f"allowed limit: {self.MAX_DRONES}."
            )

    def _validate_zones(self) -> None:
        """Validate hubs and their metadata."""
        for hub, line in self.zone_entries:

            # Vérification du type de zone
            zone_type = hub.get("zone_type", "normal")
            if zone_type not in self.VALID_ZONE_TYPES:
                raise ValidationError(
                    f"Line {line}: invalid zone type '{zone_type}' "
                    f"for hub {hub['name']!r}"
                )

            # Vérification des clés inconnues
            for key in hub:
                if key in {"name", "x", "y", "zone_type", "color", "capacity"}:
                    continue
                raise ValidationError(
                    f"Line {line}: unknown metadata key '{key}' "
                    f"for hub {hub['name']!r}"
                )

            # Vérification de la capacité
            capacity = hub["capacity"]
            is_terminal_hub = hub is self.start_hub or hub is self.end_hub

            if is_terminal_hub and capacity == math.inf:
                continue

            if not isinstance(capacity, int) or capacity < 1:
                raise ValidationError(
                    f"Line {line}: invalid capacity "
                    f"for hub {hub['name']!r}"
                )

    def _validate_connections(self) -> None:
        """Validate connection keys and capacities. Raise ValidationError
        with the offending declaration line.
        """
        for connection, line in self.connection_entries:

            # Vérification des clés inconnues
            for key in connection:
                if key in {"source", "target", "capacity"}:
                    continue
                raise ValidationError(
                    f"Line {line}: unknown metadata key '{key}' "
                    "for connection "
                    f"{connection['source']!r}-{connection['target']!r}"
                )

            # Vérification de la capacité
            cap = connection["capacity"]
            if not isinstance(cap, int) or cap <= 0:
                raise ValidationError(
                    f"Line {line}: invalid connection capacity "
                    "for connection "
                    f"{connection['source']!r}-{connection['target']!r}"
                )

    def _check_unique_zone_names(self) -> None:
        """Reject duplicate hub names and report their declaration lines."""
        names: dict[str, int] = {}
        for hub, line in self.zone_entries:
            name = hub["name"]
            if name in names:
                first_line = names[name]
                raise ValidationError(
                    f"Line {line}: duplicate hub name: {name!r} "
                    f"(already defined on line {first_line})"
                )
            names[name] = line

    def _check_connection_endpoints(self) -> None:
        """Verify that each endpoint exists and precedes its connection.
        Raise ValidationError for unknown hubs or late declarations.
        """
        definition_lines = {
            hub["name"]: line for hub, line in self.zone_entries
        }
        for connection, line in self.connection_entries:
            for endpoint in (connection["source"], connection["target"]):
                if endpoint not in definition_lines:
                    raise ValidationError(
                        f"Line {line}: connection references unknown hub: "
                        f"{endpoint!r}"
                    )
                if definition_lines[endpoint] >= line:
                    raise ValidationError(
                        f"Line {line}: hub {endpoint!r} not yet defined "
                        f"(defined on line {definition_lines[endpoint]})."
                    )

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

                raise ValidationError(
                    f"Line {line}: "
                    f"Duplicate connection between "
                    f"{pair[0]} and {pair[1]} "
                    f"(already defined on line "
                    f"{first_line})"
                )

            checked_conn[pair] = line

    def _check_reachable_end(self) -> None:
        """Use BFS to check that start can reach end without blocked hubs."""
        hubs = [self.start_hub, *self.hubs, self.end_hub]
        adjacency: dict[str, list[str]] = {
            hub["name"]: []
            for hub in hubs
            if hub["zone_type"] != "blocked"
        }

        for connection in self.connections:
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
            line for hub, line in self.zone_entries
            if hub is self.end_hub
        )
        raise ValidationError(
            f"Line {end_line}: no traversable path "
            f"between {start!r} and {end!r} (blocked hubs excluded)."
        )
