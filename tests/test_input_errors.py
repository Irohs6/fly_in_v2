import errno
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

import main
from src.parser.parser import ParseError, Parser


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("case", ["directory", "encoding", "missing"])
@pytest.mark.parametrize("terminal_only", [False, True])
def test_cli_reports_unreadable_map_without_traceback(
    tmp_path: Path, case: str, terminal_only: bool,
) -> None:
    target = tmp_path / "map.txt"
    if case == "directory":
        target.mkdir()
    elif case == "encoding":
        target.write_bytes(b"\xff\xfe")
    command = [sys.executable, "main.py", str(target)]
    if terminal_only:
        command.append("--no-gui")
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.startswith("Erreur: ")
    assert str(target) in result.stderr
    assert "Traceback" not in result.stderr
    assert len(result.stderr.splitlines()) == 1
    if case == "encoding":
        assert "UTF-8 invalide" in result.stderr


@pytest.mark.parametrize("code", [errno.EACCES, errno.EIO])
def test_read_os_error_is_contextualized(tmp_path: Path, code: int) -> None:
    target = tmp_path / "map.txt"
    error = OSError(code, "read failure", str(target))
    with patch("builtins.open", side_effect=error):
        with pytest.raises(ParseError, match="Impossible de lire") as caught:
            Parser(str(target)).parse()
    assert str(target) in str(caught.value)
    assert caught.value.__cause__ is error


def test_permission_denied_at_entry_point(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", [
        "main.py", "assets/maps/easy/01_linear_path.txt", "--no-gui",
    ])
    with patch("builtins.open", side_effect=PermissionError(
        errno.EACCES, "Permission denied",
    )):
        assert main.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Permission denied" in captured.err
    assert "Traceback" not in captured.err


def test_path_resolution_os_error_is_reported(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["main.py", "--no-gui"])
    with patch.object(Path, "resolve", side_effect=OSError(
        errno.EACCES, "Permission denied",
    )):
        assert main.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Permission denied" in captured.err
    assert "Traceback" not in captured.err
