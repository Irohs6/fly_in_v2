from collections.abc import Iterable, Mapping

from src.model.connection import Connection
from src.model.hub import Hub


class TerminalView:
    """Affiche les mouvements dans le format obligatoire du sujet V3."""

    def display(
        self,
        turns: Iterable[Mapping[int, Hub | Connection]],
    ) -> None:
        """Affiche exactement une ligne par tour de simulation."""
        for movements in turns:
            print(
                " ".join(
                    f"D{drone_id}-{self._format_destination(destination)}"
                    for drone_id, destination in movements.items()
                )
            )

    @staticmethod
    def _format_destination(destination: Hub | Connection) -> str:
        """Nomme la zone ou la connexion telle que définie dans la carte."""
        if isinstance(destination, Connection):
            return f"{destination.source.name}-{destination.target.name}"
        return destination.name
