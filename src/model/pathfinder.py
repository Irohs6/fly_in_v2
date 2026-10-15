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
        blocked_hubs: set[Hub] | None = None,
        saturated_connections: set[tuple[Hub, Hub]] | None = None,
    ) -> tuple[dict[Hub, float], dict[Hub, Hub | None]]:

        """Compute distances and predecessors from source. Exclude blocked
        hubs, blocked_hubs and saturated_connections in both directions.
        Favor priority hubs when updating equal-cost paths.
        Return dictionaries keyed by Hub; unreachable hubs have infinite
        distance and no predecessor.
        """
        distances: dict[Hub, float] = {
            hub: float("inf") for hub in self.graph.hubs.values()}

        predecessors: dict[Hub, Hub | None] = {
            hub: None for hub in self.graph.hubs.values()}

        distances[source] = 0
        # Prefer priority hubs when routing weights are equal.
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

            for connection in self.graph.get_connections(current_hub):
                neighbor = connection.get_other_hub(current_hub)

                # Keep finalized paths intact.
                if neighbor in visited:
                    continue

                if blocked_hubs and neighbor in blocked_hubs:
                    continue

                if saturated_connections and (
                    (connection.source, connection.target)
                    in saturated_connections
                    or (connection.target, connection.source)
                    in saturated_connections
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
        blocked_hubs: set[Hub] | None = None,
        saturated_connections: set[tuple[Hub, Hub]] | None = None,
    ) -> list[Hub]:

        """Return a path to end_hub including both endpoints. Default to
        start_hub when source is None and respect hub and connection
        exclusions. Return an empty list if the destination is
        unreachable.
        """
        if source is None:
            source = self.graph.start_hub

        target = self.graph.end_hub

        distances, predecessors = self.shortest_distances(
            source,
            blocked_hubs,
            saturated_connections,
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
