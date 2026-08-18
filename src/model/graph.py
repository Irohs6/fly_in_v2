from collections import defaultdict
from src.parser.parser import HubDict, ParsedMap, ConnectionDict
from .hub import Hub
from .connection import Connection


class Graph:
    def __init__(self, data: ParsedMap) -> None:

        self.data = data
        # Stockage des hubs et connexions
        self.hubs: dict[str, Hub] = {hub["name"]: Hub(**hub) for hub in data.get("hubs", [])}
        self.connections: list[Connection] = []

        # Zones spéciales
        self.start_zone: Hub = (Hub(**data["start_hub"])
                                if "start_hub" in data else None)
        self.end_zone: Hub | None = (Hub(**data["end_hub"])
                                     if "end_hub" in data else None)

        # Adjacence
        self.adjacency: dict[str, list[Connection]] = defaultdict(list)
        self.connection_map: dict[tuple[str, str], Connection] = {}

    def create_hub(self, hub: HubDict) -> Hub:
        return Hub(
            name=hub["name"],
            color=hub.get("color", "white"),
            zone_type=hub.get("zone_type", "normal"),
            capacity=hub.get("capacity", 1),
            x=hub["x"],
            y=hub["y"],
        )

    def create_connection(self, source: Hub, target: Hub, capacity: int | float = 1) -> Connection:
        if not isinstance(source, Hub) or not isinstance(target, Hub):
            raise ValueError("Source and target must be Hub instances")
        if capacity < 0:
            raise ValueError("Capacity must be a non-negative number")

        return Connection(source=source, target=target, capacity=capacity)

    def add_hub(self, hub: Hub) -> None:
        self.hubs[hub.name] = hub
        self.zones = self.hubs

        if self.start_zone is None and self._is_expected_hub(hub, self._expected_start):
            self.start_zone = hub

        if self.end_zone is None and self._is_expected_hub(hub, self._expected_end):
            self.end_zone = hub

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

        self.adjacency[connection.source.name].append(connection)
        self.adjacency[connection.target.name].append(connection)

        self.connection_map[(connection.source.name, connection.target.name)] = connection
        self.connection_map[(connection.target.name, connection.source.name)] = connection

    def get_neighbors(self, zone_name: str) -> list[Connection]:
        return self.adjacency.get(zone_name, [])

    def get_connection(self, source_name: str, target_name: str) -> Connection | None:
        return self.connection_map.get((source_name, target_name))
