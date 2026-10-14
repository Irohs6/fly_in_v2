from collections.abc import Iterable

from src.model.state import TurnState


class TerminalView:
    """Display recorded movements in the format required by the subject."""

    def display(self, turns: Iterable[TurnState]) -> None:
        """Print one line per completed turn, omitting the initial state."""
        for frame in turns:
            if frame.turn == 0:
                continue
            movements = []
            for drone_id in frame.moved_drones:
                position = frame.drones[drone_id].current_position
                destination = position if isinstance(position, str) else (
                    "-".join(position)
                )
                movements.append(f"D{drone_id}-{destination}")
            print(" ".join(movements))
