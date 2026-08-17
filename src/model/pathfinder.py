from heapq import heappop, heappush

from .graph import Graph


class Dijkstra:
    def __init__(self, graph: Graph):
        self.graph = graph

    @staticmethod
    def _connection_key(
        source: str,
        target: str
    ) -> tuple[str, str]:
        """Retourne une clé stable pour une connexion."""
        return tuple(sorted((source, target)))

    def shortest_distances(
        self,
        source: str,
        blocked_zones: set[str] | None = None,
        saturated_conns: set[tuple[str, str]] | None = None,
        routing_seed: int = 0,
        usage_counts: dict[str, int] | None = None,
    ) -> tuple[dict[str, float], dict[str, str | None]]:

        distances = {
            name: float("inf")
            for name in self.graph.hubs
        }

        predecessors = {
            name: None
            for name in self.graph.hubs
        }

        distances[source] = 0

        queue = [(0, source)]
        visited: set[str] = set()

        while queue:
            current_distance, current_name = heappop(queue)

            if current_name in visited:
                continue

            visited.add(current_name)

            for connection in self.graph.get_neighbors(
                current_name
            ):
                if connection.source.name == current_name:
                    neighbor = connection.target
                else:
                    neighbor = connection.source

                neighbor_name = neighbor.name

                if (
                    blocked_zones
                    and neighbor_name in blocked_zones
                ):
                    continue

                if neighbor.zone_type == "blocked":
                    continue

                if saturated_conns:
                    key = self._connection_key(
                        connection.source.name,
                        connection.target.name,
                    )

                    if key in saturated_conns:
                        continue

                weight = neighbor.move_cost()

                if weight == float("inf"):
                    continue

                new_distance = current_distance + weight

                if new_distance < distances[neighbor_name]:
                    distances[neighbor_name] = new_distance
                    predecessors[neighbor_name] = current_name

                    heappush(
                        queue,
                        (new_distance, neighbor_name)
                    )

        return distances, predecessors

    def shortest_path(
        self,
        source: str | None = None,
        blocked_zones: set[str] | None = None,
        saturated_conns: set[tuple[str, str]] | None = None,
        routing_seed: int = 0,
        usage_counts: dict[str, int] | None = None,
    ) -> list:

        if source is None:
            if self.graph.start_zone is None:
                return []

            source = self.graph.start_zone.name

        if self.graph.end_zone is None:
            return []

        target = self.graph.end_zone.name

        distances, predecessors = self.shortest_distances(
            source,
            blocked_zones,
            saturated_conns,
            routing_seed,
            usage_counts,
        )

        if distances[target] == float("inf"):
            return []

        path: list[str] = []
        current: str | None = target

        while current is not None:
            path.append(current)
            current = predecessors[current]

        path.reverse()

        return [
            self.graph.hubs[name]
            for name in path
        ]

    def distance_to(
        self,
        source: str,
        target: str
    ) -> float:

        distances, _ = self.shortest_distances(source)

        return distances[target]