from collections import deque
from .parser import ConnectionDict, HubDict


class ValidationError(Exception):
    """Error while validating map data."""
    pass


class MapValidator:
    """Validate zone types and graph consistency of parsed map data.

    Parser has already checked the input syntax, keys and numeric values.
    """

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def __init__(
        self,
        start_hub: HubDict,
        end_hub: HubDict,
        hub_entries: list[tuple[HubDict, int]],
        connection_entries: list[tuple[ConnectionDict, int]],
    ) -> None:

        """Store parsed data and declaration line numbers. hub_entries and
        connection_entries associate declarations with their lines for
        error reporting.
        """
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hub_entries = hub_entries
        self.connection_entries = connection_entries

    def validate(self) -> None:
        """Validate the consistency of parsed map data."""
        self._check_zone_types()
        self._check_unique_hub_names()
        self._check_connection_endpoints()
        self._check_duplicate_connections()
        self._check_reachable_end()

    def _check_zone_types(self) -> None:
        """Require a supported zone type for every hub."""
        for hub, line in self.hub_entries:
            zone_type = hub["zone_type"]
            if zone_type not in self.VALID_ZONE_TYPES:
                raise ValidationError(
                    f"Line {line}: invalid zone type '{zone_type}' "
                    f"for hub {hub['name']!r}"
                )

    def _check_unique_hub_names(self) -> None:
        """Reject duplicate hub names and report their declaration lines."""
        names: dict[str, int] = {}
        for hub, line in self.hub_entries:
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
            hub["name"]: line for hub, line in self.hub_entries
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
        raise ValidationError(
            f"Line {end_line}: no traversable path "
            f"between {start!r} and {end!r} (blocked hubs excluded)."
        )
