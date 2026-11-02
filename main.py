import argparse
import sys

from src.controller.controller import Controller
from src.parser.parser import ParseError
from src.view.errors import DisplayError


def main() -> int:
    """Parse command-line options and run the requested simulation mode."""
    parser = argparse.ArgumentParser(
        description="Run a Fly-in drone simulation."
    )
    parser.add_argument(
        "map_path",
        nargs="?",
        default="assets/maps/easy/02_simple_fork.txt",
        help="Path to the map file.",
    )
    parser.add_argument(
        "--no-view",
        "--view-desactivate",
        dest="view_active",
        action="store_false",
        help="Print movements without graphical replay.",
    )
    arguments = parser.parse_args()

    try:
        controller = Controller(map_path=arguments.map_path)
        controller.run(view_active=arguments.view_active)
    except (OSError, ParseError, DisplayError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Simulation interrupted.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
