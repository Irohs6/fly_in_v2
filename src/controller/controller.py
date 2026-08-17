from pathlib import Path

from src.parser.parser import ParseError, Parser, ParsedMap, HubDict, ConnectionDict
from src.model.graph import Graph
from src.model.simulation import Simulation
from src.view.pygame_view import Pygame_view
from src.model.pathfinder import Dijkstra


class Controller:
    """Orchestrates map parsing and validation for the Fly-in application."""

    def __init__(self, map_path: str | Path):
        self.map_path = self._resolve_map_path(map_path)
        self.parser = Parser(str(self.map_path))
        self.data: ParsedMap | None = None

        self.graph: Graph | None = None
        self.simulation: Simulation | None = None

        self._initialize()

    def _initialize(self) -> None:
        self.data = self.load_map()

        nb_drones: int = self.data["nb_drones"]
        start_hub: HubDict = self.data["start_hub"]
        hubs: list[HubDict] = self.data["hubs"]
        end_hub: HubDict = self.data["end_hub"]
        connections: list[ConnectionDict] = self.data["connections"]

        # Graph construction
        self.graph = Graph(self.data)

        # Zones
        self.graph.add_zone(self.graph.create_zone(start_hub))
        self.graph.add_zone(self.graph.create_zone(end_hub))

        for hub in hubs:
            self.graph.add_zone(self.graph.create_zone(hub))

        # Connections
        for connection in connections:
            source_hub = self.graph.hubs[connection["source"]]
            target_hub = self.graph.hubs[connection["target"]]
            capacity = connection.get("capacity", 1)

            graph_connection = self.graph.create_connection(
                source_hub, target_hub, capacity=capacity
            )
            self.graph.add_connection(graph_connection)

        # Pathfinder + Simulation
        pathfinder = Dijkstra(self.graph)
        self.simulation = Simulation(self.graph, debug=False, pathfinder=pathfinder)

        self.simulation.load_drones(nb_drones)
        self.simulation.simulate()

        self.view = Pygame_view(self.graph, self.simulation)

    def run(self) -> None:
        if self.view is not None:
            self.view.display()

    def _resolve_map_path(self, map_path: str | Path) -> Path:
        path = Path(map_path)
        if path.exists():
            return path.resolve()

        project_root = Path(__file__).resolve().parents[2]
        cleaned_parts = [part for part in path.parts if part not in (".", "..")]
        return (project_root.joinpath(*cleaned_parts)).resolve()

    def load_map(self) -> ParsedMap:
        parsed_data = self.parser.parse()
        self.data = parsed_data
        return parsed_data

    def get_summary(self) -> ParsedMap:
        if self.data is None:
            raise ParseError("Aucune carte chargée.")
        return self.data
