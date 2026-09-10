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

    def run(self, *, gui: bool = True) -> None:
        """Charge la carte, simule et affiche les mouvements puis le replay."""
        self.view = None
        self.data = self.load_map()
        self.graph = Graph(self.data)
        self.simulation = Simulation(self.graph, record_replay=gui)
        self.simulation.load_drones(self.data["nb_drones"])
        TerminalView().display(self.simulation.simulate())

        if gui:
            from src.view.pygame_view import PygameView

            self.view = PygameView(
                self.graph, self.simulation.recorder.frames,
            )
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

        self.parser.file_path = str(self._resolve_map_path(self.map_path))
        parsed_data = self.parser.parse()
        self.data = parsed_data

        return parsed_data
