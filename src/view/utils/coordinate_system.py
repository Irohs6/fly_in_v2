from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.hub import Hub
    from src.model.state import HubState


class CoordinateSystem:
    """Convert map coordinates into world positions."""

    MAX_WORLD_SPAN = 10_000

    def __init__(
        self,
        cell_size: int = 400,
    ) -> None:
        """Store cell_size as the scale factor for world positions."""
        self.cell_size = cell_size

    def compute(
        self,
        hubs: Iterable["Hub | HubState"],
    ) -> dict[str, tuple[float, float]]:

        """Center hubs and return their world positions by name. Scale by
        cell_size, reducing large extents proportionally on both axes to
        keep positions usable by Pygame. Return an empty dictionary for
        empty input.
        """
        hub_list = list(hubs)

        if not hub_list:
            return {}

        min_x = min(hub.x for hub in hub_list)
        max_x = max(hub.x for hub in hub_list)

        min_y = min(hub.y for hub in hub_list)
        max_y = max(hub.y for hub in hub_list)

        span = max(max_x - min_x, max_y - min_y)
        if span * self.cell_size > self.MAX_WORLD_SPAN:
            # Divide integers before conversion to avoid float overflow.
            return {
                hub.name: (
                    (2 * hub.x - min_x - max_x) / (2 * span)
                    * self.MAX_WORLD_SPAN,
                    (2 * hub.y - min_y - max_y) / (2 * span)
                    * self.MAX_WORLD_SPAN,
                )
                for hub in hub_list
            }
        # Subtract before conversion to handle large coordinate offsets.
        return {
            hub.name: (
                (2 * hub.x - min_x - max_x) / 2 * self.cell_size,
                (2 * hub.y - min_y - max_y) / 2 * self.cell_size,
            )
            for hub in hub_list
        }
