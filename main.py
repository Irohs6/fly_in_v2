import argparse
import sys

from src.controller.controller import Controller
from src.parser.parser import ParseError
from src.view.errors import DisplayError


def main() -> int:
    """Parse command-line options and run the requested simulation mode."""
    parser = argparse.ArgumentParser(description="Simulate drone routing.")
    parser.add_argument(
        "map", nargs="?", default="assets/maps/easy/02_simple_fork.txt",
        help="Map file to simulate.",
    )
    parser.add_argument(
        "--no-gui", action="store_true",
        help="Print movements without Pygame or replay recording.",
    )
    args = parser.parse_args()
    try:
        controller = Controller(args.map)
        controller.run(is_view=not args.no_gui)
    except (OSError, ParseError, DisplayError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Simulation interrupted.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
