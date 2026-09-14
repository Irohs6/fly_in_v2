class Camera:
    """Camera for the graph display, centered at the world origin."""

    def __init__(self, zoom_min: float = 0.15, zoom_max: float = 5.0) -> None:
        """Initialize a centered camera with the given zoom limits."""
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self.zoom_min = zoom_min
        self.zoom_max = zoom_max

        # For dragging
        self._drag_start: tuple[float, float, float, float] | None = None

    # ───────────────────────────────────────────────
    # Projection monde → écran
    # ───────────────────────────────────────────────
    def world_to_screen(self, world_x: float, world_y: float, screen_w: int,
                        screen_h: int) -> tuple[int, int]:
        """Convert world coordinates to screen pixels. Apply zoom and pan,
        then offset by the screen center.
        """
        screen_x = world_x * self.zoom + screen_w / 2 + self.pan_x
        screen_y = world_y * self.zoom + screen_h / 2 + self.pan_y
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x: float, screen_y: float, screen_w: int,
                        screen_h: int) -> tuple[float, float]:
        """Convert screen pixels to world coordinates. Subtract the screen
        center and pan, then divide by zoom.
        """
        world_x = (screen_x - screen_w / 2 - self.pan_x) / self.zoom
        world_y = (screen_y - screen_h / 2 - self.pan_y) / self.zoom
        return world_x, world_y

    # ───────────────────────────────────────────────
    # Zoom centered on the mouse
    # ───────────────────────────────────────────────
    def apply_zoom(self, mouse_x: float, mouse_y: float, screen_w: int,
                   screen_h: int, factor: float) -> None:
        """Zoom around the mouse position. Factors above one zoom in;
        factors below one zoom out.
        """

        # Position monde avant zoom
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y,
                                                screen_w, screen_h)

        # Apply the zoom
        new_zoom = self.zoom * factor
        new_zoom = max(self.zoom_min, min(self.zoom_max, new_zoom))

        # Recalculate the pan to keep the world point under the mouse
        self.pan_x = mouse_x - screen_w / 2 - world_x * new_zoom
        self.pan_y = mouse_y - screen_h / 2 - world_y * new_zoom

        self.zoom = new_zoom

    # ───────────────────────────────────────────────
    # Pan (drag)
    # ───────────────────────────────────────────────
    def start_drag(self, mouse_x: float, mouse_y: float) -> None:
        """Start dragging from the given mouse position."""
        self._drag_start = (mouse_x, mouse_y, self.pan_x, self.pan_y)

    def drag(self, mouse_x: float, mouse_y: float) -> None:
        """Pan the camera according to mouse movement during a drag."""
        if not self._drag_start:
            return

        sx, sy, pan_start_x, pan_start_y = self._drag_start
        self.pan_x = pan_start_x + (mouse_x - sx)
        self.pan_y = pan_start_y + (mouse_y - sy)

    def end_drag(self) -> None:
        """End the current drag operation."""
        self._drag_start = None

    # ───────────────────────────────────────────────
    # Reset
    # ───────────────────────────────────────────────
    def reset(self) -> None:
        """Reset the camera zoom and pan to their defaults."""
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
