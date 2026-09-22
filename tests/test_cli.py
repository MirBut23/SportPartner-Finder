"""Прогоны всех пунктов меню и обработки ошибок."""

from datetime import date
from pathlib import Path
from unittest.mock import patch

from sportpartner.cli import run_menu
from sportpartner.storage import load_data, save_data
from sportpartner.service import statistics


def test_all_menu_commands(data: dict, tmp_path: Path, capsys) -> None:
    path = tmp_path / "store.json"
    save_data(path, data)
    commands = [
        "1", "2", "Москва", "теннис", "1", "3", "capacity",
        "4", "1", "1", "5", "4", "6", "7",
        "8", "Тест", "20", "Москва", "2",
        "9", "2", "Москва", "Парк", "2026-10-10", "2", "10",
        "10", "11", "oops", "4", "not-an-id", "0",
    ]
    with patch("builtins.input", side_effect=commands):
        assert run_menu(data, path, date(2026, 9, 22)) == 0
    output = capsys.readouterr().out
    assert output.count("Изменение сохранено") == 4
    assert "Неизвестная команда" in output
    assert "Ошибка:" in output
    stats = statistics(load_data(path))
    assert stats["athletes"] == 6 and stats["events"] == 5
    assert stats["active"] == 3 and stats["cancelled"] == 1


def test_save_failure_rolls_back_memory(data: dict, tmp_path: Path,
                                        capsys) -> None:
    path = tmp_path / "store.json"
    save_data(path, data)
    commands = ["4", "1", "1", "1", "0"]
    with patch("builtins.input", side_effect=commands):
        with patch("sportpartner.cli.save_data", side_effect=OSError("disk")):
            run_menu(data, path, date(2026, 9, 22))
    output = capsys.readouterr().out
    assert "Осталось мест: 1" in output
    assert statistics(load_data(path))["active"] == 3


def test_eof_exits(data: dict, tmp_path: Path) -> None:
    with patch("builtins.input", side_effect=EOFError):
        assert run_menu(data, tmp_path / "store.json", date.today()) == 0
