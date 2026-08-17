
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.zone import Zone


class CoordinateSystem:
    """Coordinate system for the graphical representation of the graph
        centered around (0, 0)."""

    def __init__(self, cell_size: int = 400):
        self.cell_size = cell_size
        self.world_positions: dict[str, tuple[float, float]] = {}

    def compute(self, zones: list["Zone"]) -> dict[str, tuple[float, float]]:
        """
        Computes the world positions of the zones, centered around (0, 0).
        """
        zones = list(zones)
        if not zones:
            return {}

        # Calcul du centre géométrique
        min_x = min(z.x for z in zones)
        max_x = max(z.x for z in zones)
        min_y = min(z.y for z in zones)
        max_y = max(z.y for z in zones)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Transformation en coordonnées monde
        self.world_positions = {
            z.name: (
                (z.x - center_x) * self.cell_size,
                (z.y - center_y) * self.cell_size,
            )
            for z in zones
        }

        return self.world_positions

    def get(self, zone_name: str) -> tuple[float, float] | None:
        """
        Returns the world position of the specified zone.
        """
        return self.world_positions.get(zone_name)
