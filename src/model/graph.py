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
            hub["name"]: Hub(**hub) for hub in data["hubs"]
        }

        # Zones spéciales
        self.start_hub: Hub = (
            Hub(**data["start_hub"])
        )
        self.end_hub: Hub = (
            Hub(**data["end_hub"])
        )

        self.hubs[self.start_hub.name] = self.start_hub
        self.hubs[self.end_hub.name] = self.end_hub

        self.connections = self._build_connections(data["connections"])

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
                source=self.hubs[connection["source"]],
                target=self.hubs[connection["target"]],
                capacity=connection["capacity"],
            )
            for connection in raw_connections
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

    def get_connections(self, hub: Hub) -> list[Connection]:
        """Return connections incident to hub, or an empty list."""
        return self.adjacency.get(hub.name, [])

    def get_connection(self, source: Hub, target: Hub) -> Connection | None:
        """Return the connection between source and target, or None if
        absent.
        """
        return self.connection_map.get((source, target))
