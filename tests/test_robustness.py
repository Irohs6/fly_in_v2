import pytest

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
        current_zone=start,
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
        drone.current_zone
        is graph.end_zone
        for drone in simulation.drones
    )

    assert simulation.turn > 0
