from src.model.connection import Connection
from src.model.drone import Drone
from src.model.graph import Graph
from src.model.hub import Hub
from src.model.simulation import Simulation
from src.parser.parser import Parser


def _build_simple_graph() -> Graph:
    graph = Graph({})
    start = Hub("start", capacity=10)
    a = Hub("a", capacity=1)
    b = Hub("b", capacity=1)
    end = Hub("goal", capacity=10)

    graph.add_zone(start)
    graph.add_zone(a)
    graph.add_zone(b)
    graph.add_zone(end)

    graph.add_connection(Connection(start, a, capacity=1))
    graph.add_connection(Connection(a, b, capacity=1))
    graph.add_connection(Connection(b, end, capacity=1))

    return graph


def test_waiting_drone_reroutes_to_alternate_path() -> None:
    graph = Graph({})
    start = Hub("start", capacity=10)
    a = Hub("a", capacity=1)
    b = Hub("b", capacity=1)
    goal = Hub("goal", capacity=10)

    graph.add_zone(start)
    graph.add_zone(a)
    graph.add_zone(b)
    graph.add_zone(goal)

    graph.add_connection(Connection(start, a, capacity=1))
    graph.add_connection(Connection(start, b, capacity=1))
    graph.add_connection(Connection(a, goal, capacity=1))
    graph.add_connection(Connection(b, goal, capacity=1))

    a.add_nb_drone(1)

    sim = Simulation(graph, debug=False)
    drone = Drone("D1", current_zone=start)
    drone.status = "waiting"
    drone.path = [a, goal]
    sim.drones = [drone]

    sim._reroute_waiting_drone(drone)

    assert drone.path[0].name == "b"


def test_ordered_drones_returns_loaded_order() -> None:
    graph = _build_simple_graph()
    sim = Simulation(graph, debug=False)
    sim.drones = [Drone("D1"), Drone("D2"), Drone("D3")]

    ordered = sim._ordered_drones()

    assert [d.drone_id for d in ordered] == ["D1", "D2", "D3"]


def test_custom_start_and_goal_names_are_supported() -> None:
    graph = Graph({})
    start = Hub("entry_start", capacity=10)
    mid = Hub("mid", capacity=1)
    end = Hub("destination_goal", capacity=10)

    graph.add_zone(start)
    graph.add_zone(mid)
    graph.add_zone(end)

    assert graph.start_zone is start
    assert graph.end_zone is end
    assert graph.hubs["entry_start"].name == "entry_start"
    assert graph.hubs["destination_goal"].name == "destination_goal"


def test_hub_max_drones_alias_matches_max_drone() -> None:
    zone = Hub("zone", capacity=3)

    assert zone.capacity == 3

    zone.capacity = 5
    assert zone.capacity == 5


def test_spaghetti_challenger_finishes_under_45_turns() -> None:
    parser = Parser("assets/maps/challenger/42_spaghetti.txt")
    data = parser.parse()

    graph = Graph(data)
    start = graph.create_zone(data["start_hub"])
    end = graph.create_zone(data["end_hub"])
    graph.add_zone(start)
    graph.add_zone(end)
    graph.start_zone = start
    graph.end_zone = end

    for hub in data["hubs"]:
        graph.add_zone(graph.create_zone(hub))

    for connection in data["connections"]:
        source = graph.hubs[connection["source"]]
        target = graph.hubs[connection["target"]]
        graph.add_connection(
            Connection(source, target, capacity=connection.get("capacity", 1))
        )

    sim = Simulation(graph, debug=False)
    sim.load_drones(data["nb_drones"])
    sim.start()
    sim.execute()

    assert sim.turn <= 45


def test_impossible_dream_finishes_under_45_turns() -> None:
    parser = Parser("assets/maps/challenger/01_the_impossible_dream.txt")
    data = parser.parse()

    graph = Graph(data)
    start = graph.create_zone(data["start_hub"])
    end = graph.create_zone(data["end_hub"])
    graph.add_zone(start)
    graph.add_zone(end)
    graph.start_zone = start
    graph.end_zone = end

    for hub in data["hubs"]:
        graph.add_zone(graph.create_zone(hub))

    for connection in data["connections"]:
        source = graph.hubs[connection["source"]]
        target = graph.hubs[connection["target"]]
        graph.add_connection(
            Connection(source, target, capacity=connection.get("capacity", 1))
        )

    sim = Simulation(graph, debug=False)
    sim.load_drones(data["nb_drones"])
    sim.start()
    sim.execute()

    assert sim.turn <= 45

