#!/usr/bin/env python3
"""Run the simulation on every provided map and print the terminal result only.

This script intentionally avoids the pygame view and only exercises the
simulation engine and parser.
"""

from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout

from src.model.graph import Graph
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.model.pathfinder import Dijkstra

ROOT = Path(__file__).resolve().parents[1]
MAPS_DIR = ROOT / "assets" / "maps"


def iter_map_files() -> list[Path]:
    """Return every map file in the project, sorted by folder and name."""
    return sorted(
        [p for p in MAPS_DIR.rglob("*.txt") if p.is_file()],
        key=lambda p: (str(p.relative_to(ROOT)).lower()),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run every Fly-in map in terminal mode and write one "
                    ".txt report per map."
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="tests/results_by_map",
        help="Directory where one .txt file is written per map.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    maps = iter_map_files()
    if not maps:
        print("No map files found.")
        return 1

    print(f"Testing {len(maps)} map(s) without pygame...\n")
    failed: list[str] = []

    for map_path in maps:
        rel = map_path.relative_to(ROOT)
        print(f"=== {rel} ===")
        try:
            parser_map = Parser(str(map_path))
            data = parser_map.parse()
            graph = Graph(data)

            pathfinder = Dijkstra(graph)
            simulation = Simulation(graph, debug=False, pathfinder=pathfinder)
            simulation.load_drones(data["nb_drones"])

            buffer = StringIO()
            with redirect_stdout(buffer):
                simulation.simulate()

            report = buffer.getvalue()
            filename = rel.as_posix().replace("/", "_")
            if not filename.endswith(".txt"):
                filename += ".txt"
            output_file = output_dir / filename
            output_file.write_text(report, encoding="utf-8")
            print(f"OK - solved in {simulation.turn} turn(s)")
            print(f"Saved report: {output_file}")
        except Exception as exc:  # pragma: no cover - debug utility
            print(f"FAILED: {exc}")
            failed.append(str(rel))
        print()

    print("Summary:")
    if failed:
        print(f"{len(failed)} map(s) failed:")
        for item in failed:
            print(f"- {item}")
        return 1

    print("All maps passed without pygame.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
