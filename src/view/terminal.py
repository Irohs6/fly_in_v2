from collections.abc import Iterable, Mapping

from src.model.connection import Connection
from src.model.hub import Hub


class TerminalView:
    """Display movements in the format required by the V3 subject."""

    def display(
        self,
        turns: Iterable[Mapping[int, Hub | Connection]],
    ) -> None:
        """Print exactly one line per simulation turn."""
        for movements in turns:
            print(
                " ".join(
                    f"D{drone_id}-{self._format_destination(destination)}"
                    for drone_id, destination in movements.items()
                )
            )

    @staticmethod
    def _format_destination(destination: Hub | Connection) -> str:
        """Name a hub or connection as declared in the map."""
        if isinstance(destination, Connection):
            return f"{destination.source.name}-{destination.target.name}"
        return destination.name
