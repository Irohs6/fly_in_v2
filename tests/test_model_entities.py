import pytest

from src.model.connection import Connection
from src.model.drone import Drone
from src.model.errors import ConnectionError, HubError
from src.model.graph import Graph
from src.model.hub import Hub


def make_map_data() -> dict:
    return {
        "map_path": "dummy.map",
        "nb_drones": 2,
        "start_hub": {
            "name": "START",
            "x": 0,
            "y": 0,
            "color": "green",
            "capacity": float("inf"),
            "zone_type": "normal",
        },
        "hubs": [
            {
                "name": "A",
                "x": 1,
                "y": 1,
                "color": "white",
                "capacity": 2,
                "zone_type": "normal",
            },
            {
                "name": "B",
                "x": 2,
                "y": 1,
                "color": "white",
                "capacity": 2,
                "zone_type": "priority",
            },
        ],
        "end_hub": {
            "name": "END",
            "x": 3,
            "y": 1,
            "color": "red",
            "capacity": float("inf"),
            "zone_type": "normal",
        },
        "connections": [
            {"source": "START", "target": "A", "capacity": 1},
            {"source": "A", "target": "B", "capacity": 2},
            {"source": "B", "target": "END", "capacity": 1},
        ],
    }


def test_hub_capacity_and_move_cost_rules() -> None:
    hub = Hub(name="A", capacity=1)

    hub.add_nb_drone()
    assert hub.nb_drone == 1

    with pytest.raises(HubError):
        hub.add_nb_drone()

    hub.remove_nb_drone()
    assert hub.nb_drone == 0

    with pytest.raises(HubError):
        hub.remove_nb_drone()

    restricted = Hub(name="R", zone_type="restricted")
    blocked = Hub(name="X", zone_type="blocked")
    priority = Hub(name="P", zone_type="priority")
    normal = Hub(name="N", zone_type="normal")

    assert restricted.move_cost() == 2.0
    assert blocked.move_cost() == float("inf")
    assert priority.move_cost() == 0.9
    assert normal.move_cost() == 1.0


def test_connection_capacity_rules() -> None:
    a = Hub("A")
    b = Hub("B")
    conn = Connection(source=a, target=b, capacity=1)

    conn.add_nb_drone()
    assert conn.nb_drone == 1

    with pytest.raises(ConnectionError):
        conn.add_nb_drone()

    conn.remove_nb_drone()
    assert conn.nb_drone == 0

    with pytest.raises(ConnectionError):
        conn.remove_nb_drone()

    with pytest.raises(ConnectionError):
        conn.set_capacity(-1)


def test_drone_transit_lifecycle() -> None:
    start = Hub("START")
    end = Hub("END")
    conn = Connection(source=start, target=end, capacity=2)
    drone = Drone(drone_id="D1", current_zone=start)

    drone.begin_transit(connection=conn, cost=2, destination=end)
    assert drone.in_transit is True
    assert drone.destination is end
    assert drone.moving_connection == (True, conn)
    assert drone.status == "in_transit"

    drone.finish_transit(zone=end)
    assert drone.in_transit is False
    assert drone.destination is None
    assert drone.current_zone is end
    assert drone.previous_zone is start
    assert drone.moving_connection == (False, None)
    assert drone.status == "moving"


def test_graph_builds_connections_with_existing_hubs() -> None:
    graph = Graph(make_map_data())

    assert len(graph.connections) == 3

    first = graph.connections[0]
    assert first.source is graph.hubs["START"]
    assert first.target is graph.hubs["A"]


def test_graph_initializes_adjacency_and_connection_map() -> None:
    graph = Graph(make_map_data())

    neighbors_a = graph.get_neighbors(graph.hubs["A"])
    assert len(neighbors_a) == 2

    assert graph.get_connection("START", "A") is not None
    assert graph.get_connection("A", "START") is not None


def test_graph_raises_on_unknown_hub_in_connection() -> None:
    data = make_map_data()
    data["connections"] = [
        {"source": "START", "target": "MISSING", "capacity": 1}
    ]

    with pytest.raises(ValueError, match=r"Unknown hub name\(s\)"):
        Graph(data)


def test_graph_requires_start_and_end_hub() -> None:
    data = make_map_data()
    del data["start_hub"]

    with pytest.raises(ValueError, match="Both start_hub and end_hub"):
        Graph(data)
