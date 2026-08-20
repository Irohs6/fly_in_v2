class Recorder:

    def __init__(self) -> None:
        self.tours: list[dict[str, str | None]] = []
        self.replay_frames: list[dict[str, object]] = []

    def record(
        self,
        turn: int,
        drones,
        hubs,
        connections,
    ) -> None:
        """Enregistre l'état courant de la simulation."""
        pass