from pathlib import Path

from src.parser.parser import Parser, ParsedMap, ParseError
from src.model.graph import Graph
from src.model.simulation import Simulation
from src.view.pygame_view import PygameView
from src.view.terminal import TerminalView
from src.model.pathfinder import Dijkstra


class Controller:
    """Orchestrates the application components."""

    def __init__(self, map_path: str | Path):
        self.map_path = self._resolve_map_path(map_path)
        self.parser = Parser(str(self.map_path))

        self.data: ParsedMap | None = None
        self.graph: Graph | None = None
        self.simulation: Simulation | None = None
        self.view: PygameView | None = None

        self._initialize()

    def _initialize(self) -> None:
        """Load the map and initialize the application."""

        self.data = self.load_map()

        # Build the graph from the parsed map.
        self.graph = Graph(self.data)

        # Create the pathfinder.
        pathfinder = Dijkstra(self.graph)

        # Create the simulation.
        self.simulation = Simulation(
            self.graph,
            pathfinder=pathfinder,
        )

        # Create all drones and calculate their initial paths.
        self.simulation.load_drones(
            self.data["nb_drones"]
        )

        # Run the simulation.
        turns = self.simulation.simulate()
        TerminalView().display(turns)

        # Create the visual representation.
        self.view = PygameView(
            self.graph,
            self.simulation.recorder.frames,
        )

    def run(self) -> None:
        """Start the graphical interface."""

        if self.view is not None:
            self.view.display()

    def _resolve_map_path(
        self,
        map_path: str | Path,
    ) -> Path:
        """Resolve the path to the map file."""

        path = Path(map_path)

        if path.exists():
            return path.resolve()

        project_root = Path(__file__).resolve().parents[2]

        cleaned_parts = [
            part
            for part in path.parts
            if part not in (".", "..")
        ]

        return project_root.joinpath(
            *cleaned_parts
        ).resolve()

    def load_map(self) -> ParsedMap:
        """Parse and return the map data."""

        parsed_data = self.parser.parse()
        self.data = parsed_data

        return parsed_data

    def get_summary(self) -> ParsedMap:
        """Return the parsed map."""

        if self.data is None:
            raise ParseError("Aucune carte chargée.")

        return self.data
