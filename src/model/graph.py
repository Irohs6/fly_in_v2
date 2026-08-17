from collections import defaultdict
from src.parser.parser import HubDict, ParsedMap
from .hub import Hub
from .connection import Connection


class Graph:
    def __init__(self, data: ParsedMap) -> None:
        # Données attendues pour reconnaître start et end
        self._expected_start = self._extract_hub_data(data["start_hub"])
        self._expected_end = self._extract_hub_data(data["end_hub"])

        # Stockage des hubs et connexions
        self.hubs: dict[str, Hub] = {}
        self.zones = self.hubs
        self.connections: list[Connection] = []

        # Zones spéciales
        self.start_zone: Hub | None = None
        self.end_zone: Hub | None = None

        # Adjacence
        self.adjacency: dict[str, list[Connection]] = defaultdict(list)
        self.connection_map: dict[tuple[str, str], Connection] = {}

    @staticmethod
    def _extract_hub_data(hub: HubDict) -> dict[str, object]:
        return {
            "x": hub["x"],
            "y": hub["y"],
            "zone_type": hub.get("zone_type", "normal"),
            "capacity": hub.get("capacity", 1),
        }

    @staticmethod
    def _is_expected_hub(hub: Hub, expected: dict[str, object]) -> bool:
        return (
            hub.x == expected["x"]
            and hub.y == expected["y"]
            and hub.zone_type == expected["zone_type"]
            and hub.capacity == expected["capacity"]
        )

    def create_zone(self, hub: HubDict) -> Hub:
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

    def add_zone(self, hub: Hub) -> None:
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
