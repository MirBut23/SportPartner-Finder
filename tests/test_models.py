"""Специфические проверки объектной модели и сохранения связей."""

from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest

from sportpartner import service
from sportpartner.models import Athlete, MatchRequest, SportType, User
from sportpartner.storage import load_data, save_data


def test_inheritance_and_polymorphism() -> None:
    users = [User(1, "Анна", "Москва"), Athlete(2, "Иван", 20, "Москва", 2)]
    assert isinstance(users[1], User)
    assert "уровень" not in str(users[0])
    assert "уровень 2" in str(users[1])
    assert users[1].compatibility(3).startswith("Допустимое")


def test_load_restores_shared_objects(data: dict) -> None:
    request = data["requests"][0]
    event = data["events"][0]
    assert request.event is event
    assert request.athlete is data["athletes"][1]
    assert event.sport is data["sports"][0]
    assert event.participants[0] is request.athlete
    assert event.available_slots == 1


def test_status_is_read_only(data: dict) -> None:
    request = data["requests"][0]
    with pytest.raises(AttributeError):
        request.status = "cancelled"
    assert request.status == "active"
    request.cancel()
    assert request.status == "cancelled"
    assert request.event.available_slots == 2


def test_protected_capacity_and_level(data: dict) -> None:
    event = data["events"][0]
    with pytest.raises(AttributeError):
        event.capacity = 0
    with pytest.raises(AttributeError):
        data["athletes"][0].level = 5
    assert isinstance(event.participants, tuple)


def test_deepcopy_preserves_links(data: dict) -> None:
    copied = deepcopy(data)
    assert copied["requests"][0].event is copied["events"][0]
    assert copied["requests"][0].event is not data["events"][0]


def test_roundtrip_cancel_and_join(data: dict, tmp_path: Path) -> None:
    service.join_event(data, 1, 1, date(2026, 9, 22))
    service.cancel_request(data, 1)
    path = tmp_path / "store.json"
    save_data(path, data)
    loaded = load_data(path)
    assert loaded["requests"][0].status == "cancelled"
    assert loaded["requests"][3].event is loaded["events"][0]
    assert loaded["events"][0].available_slots == 1


def test_historical_active_requests_load(data: dict, tmp_path: Path) -> None:
    data["events"][0].date = date(2020, 1, 1)
    path = tmp_path / "store.json"
    save_data(path, data)
    loaded = load_data(path)
    assert loaded["events"][0].available_slots == 1
    with pytest.raises(ValueError, match="прошла"):
        service.join_event(loaded, 1, 1, date(2026, 9, 22))


def test_detached_reference_rejected(data: dict, tmp_path: Path) -> None:
    data["requests"][0].athlete = deepcopy(data["athletes"][1])
    with pytest.raises(ValueError):
        save_data(tmp_path / "store.json", data)


def test_participant_without_request_rejected(data: dict,
                                              tmp_path: Path) -> None:
    data["events"][0].add_participant(data["athletes"][0])
    with pytest.raises(ValueError):
        save_data(tmp_path / "store.json", data)


def test_classmethods() -> None:
    sport = SportType.from_dict({"id": 1, "name": "Бег", "equipment": ""})
    assert sport.to_dict()["name"] == "Бег"
    athlete = Athlete.from_dict({"id": 1, "name": "Анна", "city": "Москва",
                                 "age": 20, "level": 2})
    assert athlete.is_compatible(3)


def test_bad_status_does_not_reserve(data: dict) -> None:
    event = data["events"][0]
    with pytest.raises(ValueError):
        MatchRequest(99, data["athletes"][0], event, "wrong")
    assert event.available_slots == 1
