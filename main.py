import argparse
import sys

from src.controller.controller import Controller
from src.parser.parser import ParseError


def main() -> int:
    """Parse les options et lance la simulation dans le mode demandé."""
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
    except (OSError, ParseError) as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Simulation interrupted.", file=sys.stderr)
        sys.exit(130)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
