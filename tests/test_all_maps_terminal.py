#!/usr/bin/env python3
"""Run the simulation on every provided map without pygame."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from src.model.graph import Graph
from src.model.pathfinder import Dijkstra
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.view.terminal import TerminalView


ROOT = Path(__file__).resolve().parents[1]
MAPS_DIR = ROOT / "assets" / "maps"


def iter_map_files() -> list[Path]:
    """Return every map file in the project."""
    return sorted(
        [
            path
            for path in MAPS_DIR.rglob("*.txt")
            if path.is_file()
        ],
        key=lambda path: str(
            path.relative_to(ROOT)
        ).lower(),
    )


def main() -> int:
    """Run the simulation on every map."""
    parser = argparse.ArgumentParser(
        description=(
            "Run every Fly-in map in terminal mode "
            "and write one report per map."
        )
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default="tests/results_by_map",
        help=(
            "Directory where one .txt file "
            "is written per map."
        ),
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    maps = iter_map_files()

    if not maps:
        print("No map files found.")
        return 1

    print(
        f"Testing {len(maps)} map(s) "
        "without pygame...\n"
    )

    failed: list[str] = []

    for map_path in maps:
        rel = map_path.relative_to(ROOT)

        print(f"=== {rel} ===")

        try:
            parser_map = Parser(
                str(map_path)
            )

            data = parser_map.parse()

            graph = Graph(data)

            pathfinder = Dijkstra(graph)

            simulation = Simulation(
                graph,
                pathfinder=pathfinder,
            )

            simulation.load_drones(
                data["nb_drones"]
            )

            turns = simulation.simulate()

            buffer = StringIO()

            with redirect_stdout(buffer):
                TerminalView().display(turns)

            report = buffer.getvalue()

            filename = (
                rel.as_posix()
                .replace("/", "_")
            )

            if not filename.endswith(".txt"):
                filename += ".txt"

            output_file = (
                output_dir / filename
            )

            output_file.write_text(
                report,
                encoding="utf-8",
            )

            print(
                "OK - solved in "
                f"{simulation.turn} turn(s)"
            )

            print(
                f"Saved report: {output_file}"
            )

        except Exception as exc:
            print(f"FAILED: {exc}")
            failed.append(str(rel))

        print()

    print("Summary:")

    if failed:
        print(
            f"{len(failed)} map(s) failed:"
        )

        for item in failed:
            print(f"- {item}")

        return 1

    print(
        "All maps passed without pygame."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
