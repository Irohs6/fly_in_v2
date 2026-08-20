from heapq import heappop, heappush
from itertools import count

from .graph import Graph
from .hub import Hub


class Dijkstra:
    def __init__(self, graph: Graph):
        self.graph = graph

    def shortest_distances(
        self,
        source: Hub,
        blocked_zones: set[Hub] | None = None,
        saturated_conns: set[tuple[Hub, Hub]] | None = None,
    ) -> tuple[dict[Hub, float], dict[Hub, Hub | None]]:

        distances = {hub: float("inf") for hub in self.graph.hubs.values()}

        predecessors = {hub: None for hub in self.graph.hubs.values()}

        distances[source] = 0

        queue_counter = count()
        queue: list[tuple[float, int, Hub]] = [
            (0, next(queue_counter), source)
        ]
        visited: set[Hub] = set()

        while queue:
            current_distance, _, current_hub = heappop(queue)

            if current_hub in visited:
                continue

            visited.add(current_hub)

            for connection in self.graph.get_neighbors(current_hub):
                if connection.source is current_hub:
                    neighbor = connection.target
                else:
                    neighbor = connection.source

                if blocked_zones and neighbor in blocked_zones:
                    continue

                if neighbor.zone_type == "blocked":
                    continue

                if saturated_conns and any(
                    connection.connects(source, target)
                    for source, target in saturated_conns
                        ):
                    continue

                weight = neighbor.move_cost()

                if weight == float("inf"):
                    continue

                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_hub

                    heappush(
                        queue,
                        (new_distance, next(queue_counter), neighbor),
                    )

        return distances, predecessors

    def shortest_path(
        self,
        source: Hub | None = None,
        blocked_zones: set[Hub] | None = None,
        saturated_conns: set[tuple[Hub, Hub]] | None = None,
    ) -> list[Hub]:

        if source is None:
            if self.graph.start_zone is None:
                return []

            source = self.graph.start_zone

        if self.graph.end_zone is None:
            return []

        target = self.graph.end_zone

        distances, predecessors = self.shortest_distances(
            source,
            blocked_zones,
            saturated_conns,
        )

        if distances[target] == float("inf"):
            return []

        path: list[Hub] = []
        current: Hub | None = target

        while current is not None:
            path.append(current)
            current = predecessors[current]

        path.reverse()

        return path

    def distance_to(self, source: Hub, target: Hub) -> float:
        distances, _ = self.shortest_distances(source)
        return distances[target]
