from collections import defaultdict
from src.parser.parser import ParsedMap, ConnectionDict
from .hub import Hub
from .connection import Connection


class Graph:
    """Hub graph with indexed bidirectional connections."""
    def __init__(self, data: ParsedMap) -> None:

        # Stockage des hubs et connexions
        """Build hubs and their indexes from validated map data."""
        self.hubs: dict[str, Hub] = {
            hub["name"]: Hub(**hub) for hub in data.get("hubs", [])
        }

        # Zones spéciales
        self.start_zone: Hub = (
            Hub(**data["start_hub"])
        )
        self.end_zone: Hub = (
            Hub(**data["end_hub"])
        )

        self.hubs[self.start_zone.name] = self.start_zone
        self.hubs[self.end_zone.name] = self.end_zone

        self.connections = self._build_connections(data.get("connections", []))

        # Adjacence
        self.adjacency: dict[str, list[Connection]] = defaultdict(list)
        self.connection_map: dict[tuple[Hub, Hub], Connection] = {}

        for connection in self.connections:
            self._index_connection(connection)

    def _build_connections(
        self,
        raw_connections: list[ConnectionDict],
    ) -> list[Connection]:
        """Build connections from an already validated map."""

        return [
            Connection(
                source=self.hubs[conn["source"]],
                target=self.hubs[conn["target"]],
                capacity=conn.get("capacity", 1),
            )
            for conn in raw_connections
        ]

    def _index_connection(
        self,
        connection: Connection,
    ) -> None:
        """Index a connection in the adjacency and endpoint lookup
        structures.
        """

        self.adjacency[connection.source.name].append(connection)
        self.adjacency[connection.target.name].append(connection)

        self.connection_map[
            (connection.source, connection.target)
        ] = connection

        self.connection_map[
            (connection.target, connection.source)
        ] = connection

    def get_neighbors(self, zone: Hub) -> list[Connection]:
        """Return connections incident to zone, or an empty list."""
        return self.adjacency.get(zone.name, [])

    def get_connection(self, source: Hub, target: Hub) -> Connection | None:
        """Return the connection between source and target, or None if
        absent.
        """
        return self.connection_map.get((source, target))
