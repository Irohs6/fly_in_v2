from heapq import heappop, heappush
from itertools import count

from .graph import Graph
from .hub import Hub


class Dijkstra:
    """Find paths minimizing travel time, favoring priority hubs on ties."""
    def __init__(self, graph: Graph):
        """Associate the graph with the pathfinder without computing a path."""
        self.graph = graph

    def shortest_distances(
        self,
        source: Hub,
        blocked_zones: set[Hub] | None = None,
        saturated_conns: set[tuple[Hub, Hub]] | None = None,
    ) -> tuple[dict[Hub, float], dict[Hub, Hub | None]]:

        """Compute distances and predecessors from source. Exclude blocked
        hubs, blocked_zones and saturated_conns in both directions. For
        equal travel times, prefer paths through more priority hubs.
        Return dictionaries keyed by Hub; unreachable hubs have infinite
        distance and no predecessor.
        """
        distances: dict[Hub, float] = {
            hub: float("inf") for hub in self.graph.hubs.values()}

        predecessors: dict[Hub, Hub | None] = {
            hub: None for hub in self.graph.hubs.values()}

        distances[source] = 0
        # À durée égale, maximiser le nombre de zones priority traversées.
        priorities: dict[Hub, int] = {
            hub: 0 for hub in self.graph.hubs.values()
        }

        queue_counter = count()
        queue: list[tuple[float, int, int, Hub]] = [
            (0, 0, next(queue_counter), source)
        ]
        visited: set[Hub] = set()

        while queue:
            current_distance, priority_score, _, current_hub = heappop(queue)

            if current_hub in visited:
                continue

            visited.add(current_hub)

            for connection in self.graph.get_neighbors(current_hub):
                neighbor = connection.get_extremities(current_hub)

                if blocked_zones and neighbor in blocked_zones:
                    continue

                if saturated_conns and (
                    (connection.source, connection.target) in saturated_conns
                    or (connection.target, connection.source)
                    in saturated_conns
                ):
                    continue

                weight = neighbor.move_cost()

                if weight == float("inf"):
                    continue

                new_distance = current_distance + weight

                new_priority = priority_score - int(
                    neighbor.zone_type == "priority"
                )
                if (new_distance, new_priority) < (
                    distances[neighbor], priorities[neighbor]
                ):
                    distances[neighbor] = new_distance
                    priorities[neighbor] = new_priority
                    predecessors[neighbor] = current_hub

                    heappush(
                        queue,
                        (new_distance, new_priority,
                         next(queue_counter), neighbor),
                    )

        return distances, predecessors

    def shortest_path(
        self,
        source: Hub | None = None,
        blocked_zones: set[Hub] | None = None,
        saturated_conns: set[tuple[Hub, Hub]] | None = None,
    ) -> list[Hub]:

        """Return a path to end_zone including both endpoints. Default to
        start_zone when source is None and respect hub and connection
        exclusions. Return an empty list if the destination is
        unreachable.
        """
        if source is None:
            source = self.graph.start_zone

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
        """Return the minimum source-to-target cost, or infinity if
        unreachable.
        """
        distances, _ = self.shortest_distances(source)
        return distances[target]
