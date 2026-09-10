from pathlib import Path

import pytest

from src.parser.parser import ParseError, Parser


VALID_LINES = [
    "nb_drones: 2",
    "start_hub: start 0 0",
    "hub: a 1 0",
    "end_hub: goal 2 0",
    "connection: start-a",
    "connection: a-goal",
]


def make_parser(tmp_path: Path, lines: list[str]) -> Parser:
    path = tmp_path / "map.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return Parser(str(path))


@pytest.mark.parametrize("index", range(6))
def test_missing_separator(tmp_path: Path, index: int) -> None:
    lines = VALID_LINES.copy()
    lines[index] = lines[index].replace(":", "", 1)
    with pytest.raises(ParseError, match=rf"Ligne {index + 1}:"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("index", range(6))
def test_empty_value(tmp_path: Path, index: int) -> None:
    lines = VALID_LINES.copy()
    lines[index] = lines[index].partition(":")[0] + ":"
    with pytest.raises(ParseError, match=rf"Ligne {index + 1}:"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("index", range(6))
def test_keyword_must_match_exactly(tmp_path: Path, index: int) -> None:
    lines = VALID_LINES.copy()
    lines[index] = lines[index].replace(":", "_typo:", 1)
    with pytest.raises(ParseError, match=rf"Ligne {index + 1}:"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("value", ["0", "-1", "abc", "1.5", "²"])
@pytest.mark.parametrize("index", [0, 2, 4])
def test_invalid_positive_integer(
    tmp_path: Path, value: str, index: int,
) -> None:
    lines = VALID_LINES.copy()
    if index == 0:
        lines[index] = f"nb_drones: {value}"
    else:
        lines[index] += f" [capacity={value}]"
    with pytest.raises(ParseError, match=rf"Ligne {index + 1}:"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("value", ["--1", "1.5", "abc", "²", "1_000"])
@pytest.mark.parametrize("axis", [0, 1])
def test_invalid_coordinate(tmp_path: Path, value: str, axis: int) -> None:
    lines = VALID_LINES.copy()
    coordinates = ["1", "0"]
    coordinates[axis] = value
    lines[2] = f"hub: a {coordinates[0]} {coordinates[1]}"
    with pytest.raises(ParseError, match="Ligne 3: coordonnée"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("index", [1, 2, 3])
def test_hyphen_in_hub_name(tmp_path: Path, index: int) -> None:
    lines = VALID_LINES.copy()
    lines[index] = lines[index].replace(": ", ": invalid-", 1)
    with pytest.raises(ParseError, match=rf"Ligne {index + 1}: nom"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize(
    "metadata",
    [
        "[", "[capacity=2", "[capacity=2]]", "[[capacity=2]",
        "[capacity=2] trailing", "[capacity=2] [capacity=3]",
        "[capacity]", "[=2]", "[capacity=]", "[capacity==2]",
        "[capacity=2 capacity=3]", "[unknown=3]",
    ],
)
@pytest.mark.parametrize("index", [2, 4])
def test_invalid_metadata(tmp_path: Path, metadata: str, index: int) -> None:
    lines = VALID_LINES.copy()
    lines[index] += " " + metadata
    with pytest.raises(ParseError, match=rf"Ligne {index + 1}:"):
        make_parser(tmp_path, lines).parse()


def test_connection_rejects_zone_metadata(tmp_path: Path) -> None:
    lines = VALID_LINES.copy()
    lines[4] += " [zone=normal]"
    with pytest.raises(ParseError, match="Ligne 5:.*inconnue"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize(
    "edge", ["start", "start--a", "start-a-b", "-a", "start-", "start-a b"],
)
def test_invalid_connection(tmp_path: Path, edge: str) -> None:
    lines = VALID_LINES.copy()
    lines[4] = f"connection: {edge}"
    with pytest.raises(ParseError, match="Ligne 5: connection invalide"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("edge", ["start-a", "a-start"])
def test_connection_before_hub(tmp_path: Path, edge: str) -> None:
    lines = VALID_LINES.copy()
    lines.insert(2, f"connection: {edge}")
    with pytest.raises(ParseError, match="Ligne 3:.*non encore défini"):
        make_parser(tmp_path, lines).parse()


def test_duplicate_drone_count(tmp_path: Path) -> None:
    lines = VALID_LINES + ["nb_drones: 3"]
    with pytest.raises(ParseError, match="Ligne 7: nb_drones déjà défini"):
        make_parser(tmp_path, lines).parse()


@pytest.mark.parametrize("value", ["0", "-3", "abc", "1.5", "2"])
def test_terminal_capacity_is_ignored(tmp_path: Path, value: str) -> None:
    lines = VALID_LINES.copy()
    for index in (1, 3):
        lines[index] += f" [capacity={value}]"
    data = make_parser(tmp_path, lines).parse()
    assert data["start_hub"]["capacity"] == float("inf")
    assert data["end_hub"]["capacity"] == float("inf")


def test_valid_metadata_and_signed_coordinates(tmp_path: Path) -> None:
    lines = VALID_LINES.copy()
    lines[2] = "hub: a -12 +3 [color=custom_color capacity=2 zone=priority]"
    lines[4] += " []"
    data = make_parser(tmp_path, lines).parse()
    assert data["hubs"][0] == {
        "name": "a", "x": -12, "y": 3, "color": "custom_color",
        "capacity": 2, "zone_type": "priority",
    }


def test_parser_can_be_reused_without_mutating_previous_result(
    tmp_path: Path,
) -> None:
    parser = make_parser(tmp_path, VALID_LINES)
    first = parser.parse()
    Path(parser.file_path).write_text(
        "\n".join(VALID_LINES).replace("hub: a 1 0", "hub: a 3 0"),
        encoding="utf-8",
    )
    second = parser.parse()
    assert first["hubs"][0]["x"] == 1
    assert second["hubs"][0]["x"] == 3
    assert len(second["connections"]) == 2


def test_parser_can_retry_after_error(tmp_path: Path) -> None:
    parser = make_parser(tmp_path, VALID_LINES + ["invalid"])
    with pytest.raises(ParseError):
        parser.parse()
    Path(parser.file_path).write_text("\n".join(VALID_LINES), encoding="utf-8")
    assert parser.parse()["nb_drones"] == 2
