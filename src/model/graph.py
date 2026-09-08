from collections import defaultdict
from src.parser.parser import ParsedMap, ConnectionDict
from .hub import Hub
from .connection import Connection


class Graph:
    def __init__(self, data: ParsedMap) -> None:

        # Stockage des hubs et connexions
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
        built_connections: list[Connection] = []

        for conn in raw_connections:
            source_name = conn["source"]
            target_name = conn["target"]

            source_hub = self.hubs.get(source_name)
            target_hub = self.hubs.get(target_name)

            if source_hub is None or target_hub is None:
                missing_hubs = [
                    name
                    for name, hub in (
                        (source_name, source_hub),
                        (target_name, target_hub),
                    )
                    if hub is None
                ]
                raise ValueError(
                    "Unknown hub name(s) in connection "
                    f"{source_name}-{target_name}: {', '.join(missing_hubs)}"
                )

            built_connections.append(
                Connection(
                    source=source_hub,
                    target=target_hub,
                    capacity=conn.get("capacity", 1),
                )
            )

        return built_connections

    def _index_connection(
        self,
        connection: Connection,
    ) -> None:
        """Indexe une connexion dans les structures de voisinage."""

        self.adjacency[connection.source.name].append(connection)
        self.adjacency[connection.target.name].append(connection)

        self.connection_map[
            (connection.source, connection.target)
        ] = connection

        self.connection_map[
            (connection.target, connection.source)
        ] = connection

    def get_neighbors(self, zone: Hub) -> list[Connection]:
        return self.adjacency.get(zone.name, [])

    def get_connection(self, source: Hub, target: Hub) -> Connection | None:
        return self.connection_map.get((source, target))
