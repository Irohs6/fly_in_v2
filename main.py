import sys

from src.controller.controller import Controller
from src.parser.parser import ParseError
from src.view.errors import DisplayError


def main() -> int:
    """Parse command-line options and run the requested simulation mode."""
    arguments = sys.argv[1:]
    if "-h" in arguments or "--help" in arguments:
        print(
            "Usage: python main.py [map_path] [--view-desactivate]\n"
            "Default map: assets/maps/easy/02_simple_fork.txt\n"
            "--view-desactivate: print movements without graphical replay."
        )
        return 0

    view_active = "--view-desactivate" not in arguments
    map_paths = []
    for argument in arguments:
        if argument == "--view-desactivate":
            continue
        if argument.startswith("-"):
            print(f"Error: unknown option {argument}.", file=sys.stderr)
            return 2
        map_paths.append(argument)

    if len(map_paths) > 1:
        print("Error: expected only one map path.", file=sys.stderr)
        return 2
    map_path = (
        map_paths[0] if map_paths else "assets/maps/easy/02_simple_fork.txt"
    )
    try:
        controller = Controller(map_path=map_path)
        controller.run(view_active=view_active)
    except (OSError, ParseError, DisplayError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Simulation interrupted.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
