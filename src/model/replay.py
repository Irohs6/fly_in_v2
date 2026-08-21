from dataclasses import dataclass


@dataclass
class DroneReplayState:
    drone_id: str
    source: str
    target: str
    progress: float
    status: str


@dataclass
class ReplayFrame:
    turn: int
    drones: dict[str, DroneReplayState]
    hub_counts: dict[str, int]
