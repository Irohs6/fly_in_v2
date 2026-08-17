from src.controller.controller import Controller
from src.parser.parser import ParseError, format_parsing_result


def main() -> int:
    import sys

    map_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "assets/maps/easy/02_simple_fork.txt"
    )
    try:
        controller = Controller(map_path)
        controller.run()
    except (FileNotFoundError, ParseError) as exc:
        print(f"Erreur: {exc}")
        return 1
    except KeyboardInterrupt:
        print("Simulation interrupted.", file=sys.stderr)
        sys.exit(130)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
