from src.parser.parser import Parser
from src.model.graph import Graph
from src.model.simulation import Simulation
from src.view.errors import DisplayError
from src.view.terminal import TerminalView


class Controller:
    """Coordinate map loading, simulation and display."""

    def __init__(self, map_path: str) -> None:
        """Store the map path without starting the simulation."""
        self.map_path = map_path

    def run(self, *, view_active: bool = True) -> None:
        """Simulate the map and display the results."""
        parser = Parser(self.map_path)
        data = parser.parse()

        graph = Graph(data)
        simulation = Simulation(graph)
        simulation.load_drones(data["nb_drones"])
        frames = simulation.simulate()

        TerminalView().display(frames)

        if view_active:
            try:
                from src.view.pygame_view import PygameView
            except ImportError as exc:
                raise DisplayError(
                    f"Cannot load graphical replay: {exc}. "
                    "Run 'poetry install' or use --view-desactivate."
                ) from exc

            view = PygameView(frames)
            view.display()
