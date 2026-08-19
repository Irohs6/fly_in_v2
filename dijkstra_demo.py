from pathlib import Path
import sys

from src.model.graph import Graph
from src.model.pathfinder import Dijkstra
from src.parser.parser import Parser


def main() -> int:
    project_root = Path(__file__).resolve().parent
    default_map = (
        project_root / "assets" / "maps" / "hard" / "02_capacity_hell.txt"
    )

    if len(sys.argv) > 1:
        map_path = Path(sys.argv[1])
    else:
        map_path = default_map

    parser = Parser(str(map_path))
    data = parser.parse()
    graph = Graph(data)
    pathfinder = Dijkstra(graph)

    path = pathfinder.shortest_path()

    print(f"Map: {map_path}")
    print(f"Start: {graph.start_zone.name}")
    print(f"End: {graph.end_zone.name}")

    if not path:
        print("Path: no path found")
        return 1

    print("Path: " + " -> ".join(hub.name for hub in path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
