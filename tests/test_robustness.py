import pytest

from src.model.connection import Connection
from src.model.hub import Hub
from src.model.drone import Drone
from src.model.graph import Graph
from src.model.simulation import Simulation
from src.parser.parser import ParsedMap, Parser


def make_reroute_map() -> ParsedMap:
    return {
        "map_path": "reroute.map",
        "nb_drones": 1,
        "start_hub": {
            "name": "start",
            "x": 0,
            "y": 0,
            "color": "green",
            "capacity": float("inf"),
            "zone_type": "normal",
        },
        "hubs": [
            {
                "name": "a",
                "x": 1,
                "y": 0,
                "color": "white",
                "capacity": 1,
                "zone_type": "normal",
            },
            {
                "name": "b",
                "x": 1,
                "y": 1,
                "color": "white",
                "capacity": 1,
                "zone_type": "normal",
            },
        ],
        "end_hub": {
            "name": "goal",
            "x": 2,
            "y": 0,
            "color": "red",
            "capacity": float("inf"),
            "zone_type": "normal",
        },
        "connections": [
            {
                "source": "start",
                "target": "a",
                "capacity": 1,
            },
            {
                "source": "start",
                "target": "b",
                "capacity": 1,
            },
            {
                "source": "a",
                "target": "goal",
                "capacity": 1,
            },
            {
                "source": "b",
                "target": "goal",
                "capacity": 1,
            },
        ],
    }


def make_pipeline_map() -> ParsedMap:
    return {
        "map_path": "pipeline.map",
        "nb_drones": 3,
        "start_hub": {
            "name": "start",
            "x": 0,
            "y": 0,
            "color": "green",
            "capacity": float("inf"),
            "zone_type": "normal",
        },
        "hubs": [
            {
                "name": "a",
                "x": 1,
                "y": 0,
                "color": "white",
                "capacity": 1,
                "zone_type": "normal",
            },
            {
                "name": "b",
                "x": 2,
                "y": 0,
                "color": "white",
                "capacity": 1,
                "zone_type": "normal",
            },
        ],
        "end_hub": {
            "name": "goal",
            "x": 3,
            "y": 0,
            "color": "red",
            "capacity": float("inf"),
            "zone_type": "normal",
        },
        "connections": [
            {
                "source": "start",
                "target": "a",
                "capacity": 1,
            },
            {
                "source": "a",
                "target": "b",
                "capacity": 1,
            },
            {
                "source": "b",
                "target": "goal",
                "capacity": 1,
            },
        ],
    }


def test_drone_reroutes_to_alternate_path() -> None:
    graph = Graph(
        make_reroute_map()
    )

    simulation = Simulation(graph)

    start = graph.start_zone
    a = graph.hubs["a"]
    b = graph.hubs["b"]
    goal = graph.end_zone

    assert goal is not None

    a.add_nb_drone()

    drone = Drone(
        1,
        current_position=start,
    )

    drone.set_path([
        a,
        goal,
    ])

    found = simulation._reroute_drone(
        drone,
        blocked_zones={a},
        saturated_connections=set(),
    )

    assert found is True
    assert drone.path == [
        b,
        goal,
    ]


def test_zone_freed_can_be_reused_in_same_turn() -> None:
    graph = Graph(
        make_pipeline_map()
    )

    simulation = Simulation(graph)

    simulation.load_drones(3)
    simulation.simulate()

    assert simulation.turn == 5
    assert all(
        drone.current_position is graph.end_zone
        for drone in simulation.drones
    )


@pytest.mark.parametrize(
    "map_path",
    [
        (
            "assets/maps/challenger/"
            "42_spaghetti.txt"
        ),
        (
            "assets/maps/challenger/"
            "01_the_impossible_dream.txt"
        ),
    ],
)
def test_challenger_maps_finish(
    map_path: str,
) -> None:
    parser = Parser(map_path)

    data = parser.parse()

    graph = Graph(data)

    simulation = Simulation(graph)

    simulation.load_drones(
        data["nb_drones"]
    )

    simulation.simulate()

    assert all(
        drone.current_position
        is graph.end_zone
        for drone in simulation.drones
    )

    assert simulation.turn > 0


@pytest.mark.parametrize("resource", ["hub", "connection"])
def test_move_reroutes_when_next_resource_is_full(resource: str) -> None:
    graph = Graph(make_reroute_map())
    simulation = Simulation(graph)
    simulation.load_drones(1)
    drone = simulation.drones[0]
    drone.set_path([graph.hubs["a"], graph.end_zone])
    if resource == "hub":
        graph.hubs["a"].add_nb_drone()
    else:
        graph.connections[0].add_nb_drone()

    movements: dict[int, Hub | Connection] = {}
    simulation._try_drone_move(drone, movements)

    assert drone.current_position is graph.hubs["b"]
    assert movements == {1: graph.hubs["b"]}
    assert drone.path == [graph.end_zone]


def test_move_waits_and_keeps_path_when_all_routes_are_full() -> None:
    graph = Graph(make_reroute_map())
    simulation = Simulation(graph)
    simulation.load_drones(1)
    drone = simulation.drones[0]
    graph.hubs["a"].add_nb_drone()
    graph.hubs["b"].add_nb_drone()

    movements: dict[int, Hub | Connection] = {}
    simulation._try_drone_move(drone, movements)

    assert drone.status == "waiting"
    assert drone.current_position is graph.start_zone
    assert drone.path == [graph.hubs["b"], graph.end_zone]
    assert movements == {}


def test_empty_path_before_arrival_fails_immediately() -> None:
    simulation = Simulation(Graph(make_reroute_map()))
    simulation.load_drones(1)
    simulation.drones[0].set_path([])

    with pytest.raises(RuntimeError, match="chemin vide"):
        simulation.simulate()
