"""Проверка восстановления данных и защиты исходного JSON."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from sportpartner import service
from sportpartner.storage import load_data, save_data


@pytest.fixture
def raw() -> dict:
    path = Path(__file__).parent / "fixtures" / "store.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_roundtrip(data: dict, tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    save_data(path, data)
    loaded = load_data(path)
    assert service.statistics(loaded) == service.statistics(data)
    assert service.describe_event(loaded, loaded["events"][0]) == (
        service.describe_event(data, data["events"][0])
    )


def test_missing_and_broken_files(tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    with pytest.raises(FileNotFoundError):
        load_data(path)
    path.write_text("broken", encoding="utf-8")
    with pytest.raises(ValueError):
        load_data(path)
    assert path.read_text() == "broken"


@pytest.mark.parametrize("damage", [
    "duplicate", "reference", "status", "overflow", "shape", "level",
    "duplicate_request", "bad_date", "wrong_type",
])
def test_invalid_json_schema(raw: dict, tmp_path: Path, damage: str) -> None:
    if damage == "duplicate":
        raw["events"].append(raw["events"][0].copy())
    elif damage == "reference":
        raw["requests"][0]["athlete_id"] = 999
    elif damage == "status":
        raw["requests"][0]["status"] = "unknown"
    elif damage == "overflow":
        raw["events"][0]["capacity"] = 1
    elif damage == "shape":
        raw.pop("sports")
    elif damage == "level":
        raw["athletes"][1]["level"] = 5
    elif damage == "duplicate_request":
        row = raw["requests"][0].copy()
        row["id"] = 99
        raw["requests"].append(row)
    elif damage == "bad_date":
        raw["events"][0]["date"] = "2026-02-30"
    else:
        raw["athletes"][0]["id"] = True
    path = tmp_path / "store.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError):
        load_data(path)


def test_failed_write_preserves_file(data: dict, tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    save_data(path, data)
    before = path.read_bytes()
    with patch("sportpartner.storage.os.replace", side_effect=OSError("disk")):
        with pytest.raises(OSError):
            save_data(path, data)
    assert path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [path]
