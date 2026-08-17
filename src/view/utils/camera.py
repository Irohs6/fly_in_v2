class Camera:
    """
    Camera for the graphical representation of the graph
    centered around (0, 0).
    """

    def __init__(self, zoom_min: float = 0.15, zoom_max: float = 5.0) -> None:
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
        """
        Converts world coordinates to screen coordinates (pixels).

        The pipeline is:
            1. Apply the zoom → enlarges/reduces the world.
            2. Add the pan → manual camera movement.
            3. Center the world on the middle of the screen.

        Formule :
            screen_x = world_x * zoom + (screen_w / 2) + pan_x
            screen_y = world_y * zoom + (screen_h / 2) + pan_y
        """
        screen_x = world_x * self.zoom + screen_w / 2 + self.pan_x
        screen_y = world_y * self.zoom + screen_h / 2 + self.pan_y
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x: float, screen_y: float, screen_w: int,
                        screen_h: int) -> tuple[float, float]:
        """
        Converts screen pixels to world coordinates.

        Useful for:
            - zoom centered on the mouse
            - selecting a hub with the mouse
            - calculating trajectories in the world

        Pipeline inverse :
            1. Remove the screen centering.
            2. Remove the pan.
            3. Divide by the zoom.

        Formule :
            world_x = (screen_x - screen_w/2 - pan_x) / zoom
            world_y = (screen_y - screen_h/2 - pan_y) / zoom
        """
        world_x = (screen_x - screen_w / 2 - self.pan_x) / self.zoom
        world_y = (screen_y - screen_h / 2 - self.pan_y) / self.zoom
        return world_x, world_y

    # ───────────────────────────────────────────────
    # Zoom centered on the mouse
    # ───────────────────────────────────────────────
    def apply_zoom(self, mouse_x: float, mouse_y: float, screen_w: int,
                   screen_h: int, factor: float) -> None:
        """
        Applies a zoom centered on the mouse.
        factor > 1 : zoom in
        factor < 1 : zoom out
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
        """
        Starts a drag operation.
        """
        self._drag_start = (mouse_x, mouse_y, self.pan_x, self.pan_y)

    def drag(self, mouse_x: float, mouse_y: float) -> None:
        """
        Drags the camera based on mouse movement.
        """
        if not self._drag_start:
            return

        sx, sy, pan_start_x, pan_start_y = self._drag_start
        self.pan_x = pan_start_x + (mouse_x - sx)
        self.pan_y = pan_start_y + (mouse_y - sy)

    def end_drag(self) -> None:
        """
        Ends the drag operation.
        """
        self._drag_start = None

    # ───────────────────────────────────────────────
    # Reset
    # ───────────────────────────────────────────────
    def reset(self) -> None:
        """ Resets the camera to its default state."""
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
