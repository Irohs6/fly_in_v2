from collections.abc import Iterable, Mapping


class TerminalView:
    """Affiche les mouvements dans le format obligatoire du sujet V3."""

    def display(self, turns: Iterable[Mapping[int, str]]) -> None:
        """Affiche exactement une ligne par tour de simulation."""
        for movements in turns:
            print(
                " ".join(
                    f"{drone_id}-{destination}"
                    for drone_id, destination in movements.items()
                )
            )
