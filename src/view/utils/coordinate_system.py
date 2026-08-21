from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.hub import Hub


class CoordinateSystem:
    """Convertit les coordonnées de la map en coordonnées monde."""

    def __init__(
        self,
        cell_size: int = 400,
    ) -> None:
        self.cell_size = cell_size
        self.world_positions: dict[
            str,
            tuple[float, float]
        ] = {}

    def compute(
        self,
        hubs: Iterable["Hub"],
    ) -> dict[str, tuple[float, float]]:

        hub_list = list(hubs)

        if not hub_list:
            return {}

        min_x = min(hub.x for hub in hub_list)
        max_x = max(hub.x for hub in hub_list)

        min_y = min(hub.y for hub in hub_list)
        max_y = max(hub.y for hub in hub_list)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.world_positions = {
            hub.name: (
                (hub.x - center_x) * self.cell_size,
                (hub.y - center_y) * self.cell_size,
            )
            for hub in hub_list
        }

        return self.world_positions

    def get(
        self,
        hub_name: str,
    ) -> tuple[float, float] | None:
        return self.world_positions.get(hub_name)
