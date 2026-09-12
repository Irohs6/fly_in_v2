from pathlib import Path
from typing import TYPE_CHECKING

from src.parser.parser import Parser, ParsedMap
from src.model.graph import Graph
from src.model.simulation import Simulation
from src.view.terminal import TerminalView

if TYPE_CHECKING:
    from src.view.pygame_view import PygameView


class Controller:
    """Orchestrates the application components."""

    def __init__(self, map_path: str | Path):
        """Prépare le chemin et le parser sans lire la carte ni lancer de
        simulation.
        """
        self.map_path = Path(map_path)
        self.parser = Parser(str(self.map_path))

        self.data: ParsedMap | None = None
        self.graph: Graph | None = None
        self.simulation: Simulation | None = None
        self.view: "PygameView | None" = None

    def run(self, *, is_view: bool = True) -> None:
        """Charge la carte, simule et affiche les mouvements puis le replay."""
        self.view = None
        self.data = self.load_map()
        self.graph = Graph(self.data)
        self.simulation = Simulation(self.graph, record_replay=is_view)
        self.simulation.load_drones(self.data["nb_drones"])
        TerminalView().display(self.simulation.simulate())

        if is_view:
            from src.view.pygame_view import PygameView

            self.view = PygameView(
                self.graph, self.simulation.recorder.frames,
            )
            self.view.display()

    def load_map(self) -> ParsedMap:
        """Parse and return the map data."""

        self.parser.file_path = str(self.map_path)
        parsed_data = self.parser.parse()
        self.data = parsed_data

        return parsed_data
