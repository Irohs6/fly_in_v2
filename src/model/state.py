from dataclasses import dataclass


@dataclass(frozen=True)
class DroneState:
    """Drone state copied at the end of a turn.

    A position is a hub name or the endpoints of a connection in map order.
    The path and transit counters retain the simulation data, not screen
    coordinates or an animation progress value.
    """

    current_position: str | tuple[str, str]
    previous_zone: str | None
    path: tuple[str, ...]
    status: str
    transit_duration: int
    transit_turns: int


@dataclass(frozen=True)
class HubState:
    """Hub properties, actual occupants and reserved arrival slots."""

    name: str
    x: int
    y: int
    color: str
    zone_type: str
    capacity: int | float
    nb_drones: int
    reserved: int


@dataclass(frozen=True)
class ConnectionState:
    """Connection properties and capacity usage during the recorded turn.

    used_capacity includes drones that crossed or finished transit during
    this turn. in_transit counts only drones still on the connection at
    the end of the turn; those slots remain occupied on the next turn.
    """

    source: str
    target: str
    capacity: int | float
    used_capacity: int
    in_transit: int


@dataclass(frozen=True)
class TurnState:
    """Complete snapshot after movement and before capacity counters reset.

    Turn zero describes the initial state. Lookup dictionaries and entity
    records contain no live model objects. moved_drones preserves movement
    order for terminal output, including drones delivered during this turn.
    """

    turn: int
    start_hub: str
    end_hub: str
    drones: dict[int, DroneState]
    hubs: dict[str, HubState]
    connections: dict[tuple[str, str], ConnectionState]
    moved_drones: tuple[int, ...] = ()
