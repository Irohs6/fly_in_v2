from pathlib import Path

import pytest

from src.parser.parser import (
    ParseError,
    Parser,
    HubDict,
    ConnectionDict,
)
from src.parser.validator import MapValidator, ValidationError


def write_map(tmp_path: Path, content: str) -> Path:
    map_path = tmp_path / "sample_map.txt"
    map_path.write_text(content, encoding="utf-8")
    return map_path


def test_parser_returns_clean_map_data(tmp_path: Path) -> None:
    map_path = write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 3",
                "start_hub: hub 0 0 [color=green]",
                "hub: a 1 0 [zone=restricted color=red]",
                "hub: b 2 0",
                "end_hub: goal 3 0 [color=yellow]",
                "connection: hub-a",
                "connection: a-b [capacity=2]",
                "connection: b-goal",
            ]
        ),
    )

    data = Parser(str(map_path)).parse()

    assert data["nb_drones"] == 3
    assert data["start_hub"]["name"] == "hub"
    assert data["end_hub"]["name"] == "goal"
    assert [hub["name"] for hub in data["hubs"]] == ["a", "b"]
    assert data["connections"][0] == {
        "source": "hub",
        "target": "a",
        "capacity": 1,
    }
    assert data["connections"][1]["capacity"] == 2
    assert "line" not in data["start_hub"]
    assert "line" not in data["connections"][0]


def test_parser_reports_line_for_unknown_connection_endpoint(
    tmp_path: Path,
) -> None:
    map_path = write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: hub 0 0 [color=green]",
                "end_hub: goal 1 0 [color=yellow]",
                "connection: hub-missing",
            ]
        ),
    )

    with pytest.raises(ParseError, match=r"Ligne 4:.*hub inconnu"):
        Parser(str(map_path)).parse()


def test_parser_reports_line_for_duplicate_hub_names(tmp_path: Path) -> None:
    map_path = write_map(
        tmp_path,
        "\n".join(
            [
                "nb_drones: 1",
                "start_hub: hub 0 0 [color=green]",
                "hub: a 1 0",
                "hub: a 2 0",
                "end_hub: goal 3 0 [color=yellow]",
            ]
        ),
    )

    with pytest.raises(ParseError, match=r"Ligne 4:.*dupliqué"):
        Parser(str(map_path)).parse()


def test_validator_reports_line_for_unknown_connection_endpoint() -> None:
    start: HubDict = {
        "name": "hub",
        "x": 0,
        "y": 0,
        "color": "green",
        "capacity": float("inf"),
        "zone_type": "normal",
    }
    end: HubDict = {
        "name": "goal",
        "x": 1,
        "y": 0,
        "color": "yellow",
        "capacity": float("inf"),
        "zone_type": "normal",
    }
    hubs: list[HubDict] = [
        {
            "name": "a",
            "x": 1,
            "y": 1,
            "color": "red",
            "capacity": 1,
            "zone_type": "normal",
        }
    ]
    connections: list[ConnectionDict] = [
        {
            "source": "hub",
            "target": "missing",
            "capacity": 1
        }
    ]

    zone_entries: list[tuple[HubDict, int]] = [
        (start, 2),
        (hubs[0], 3),
        (end, 4),
    ]

    connection_entries: list[tuple[ConnectionDict, int]] = [
        (connections[0], 5)
    ]

    validator = MapValidator(
        1,
        start,
        end,
        hubs,
        connections,
        zone_entries,
        connection_entries,
    )

    with pytest.raises(ValidationError, match=r"Ligne 5:.*hub inconnu"):
        validator.validate()


def test_validator_reports_line_for_bad_zone_capacity() -> None:
    start: HubDict = {
        "name": "hub",
        "x": 0,
        "y": 0,
        "color": "green",
        "capacity": float("inf"),
        "zone_type": "normal",
    }
    end: HubDict = {
        "name": "goal",
        "x": 1,
        "y": 0,
        "color": "yellow",
        "capacity": float("inf"),
        "zone_type": "normal",
    }
    hubs: list[HubDict] = [
        {
            "name": "a",
            "x": 1,
            "y": 1,
            "color": "red",
            "capacity": 0,
            "zone_type": "normal",
        }
    ]
    connections: list[ConnectionDict] = []
    zone_entries: list[tuple[HubDict, int]] = [
        (start, 2),
        (hubs[0], 3),
        (end, 4),
    ]

    connection_entries: list[tuple[ConnectionDict, int]] = []

    validator = MapValidator(
        1,
        start,
        end,
        hubs,
        connections,
        zone_entries,
        connection_entries,
    )

    with pytest.raises(ValidationError, match=r"Ligne 3:.*capacité invalide"):
        validator.validate()


@pytest.mark.parametrize(
    "zone_type, connections, reachable",
    [
        ("normal", [], False),
        ("normal", ["start-a"], False),
        ("normal", ["start-a", "a-b", "b-start"], False),
        ("normal", ["start-goal"], True),
        ("normal", ["a-start", "goal-a"], True),
        ("restricted", ["start-a", "a-goal"], True),
        ("priority", ["start-a", "a-goal"], True),
        ("blocked", ["start-a", "a-goal"], False),
        ("blocked", ["start-a", "a-goal", "start-b", "b-goal"], True),
        ("normal", ["start-a", "a-b", "b-start", "b-goal"], True),
    ],
)
def test_parser_checks_reachability(
    tmp_path: Path,
    zone_type: str,
    connections: list[str],
    reachable: bool,
) -> None:
    map_path = write_map(
        tmp_path,
        "\n".join([
            "nb_drones: 2",
            "start_hub: start 0 0",
            f"hub: a 1 0 [zone={zone_type}]",
            "hub: b 1 1",
            "end_hub: goal 2 0",
            *(f"connection: {edge}" for edge in connections),
        ]),
    )

    if reachable:
        assert Parser(str(map_path)).parse()["end_hub"]["name"] == "goal"
    else:
        with pytest.raises(
            ParseError,
            match=r"Ligne 5: aucun chemin praticable.*start.*goal",
        ):
            Parser(str(map_path)).parse()


@pytest.mark.parametrize("blocked_terminal", ["start_hub", "end_hub"])
def test_parser_rejects_blocked_terminal(
    tmp_path: Path,
    blocked_terminal: str,
) -> None:
    lines = [
        "nb_drones: 1",
        "start_hub: start 0 0",
        "end_hub: goal 1 0",
        "connection: start-goal",
    ]
    lines = [
        line + " [zone=blocked]"
        if line.startswith(blocked_terminal + ":") else line
        for line in lines
    ]
    map_path = write_map(tmp_path, "\n".join(lines))
    with pytest.raises(ParseError, match="aucun chemin praticable"):
        Parser(str(map_path)).parse()
