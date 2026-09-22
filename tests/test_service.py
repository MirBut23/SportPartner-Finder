"""Поведение проекта, в том числе пограничные случаи."""

from copy import deepcopy
from datetime import date

import pytest

from sportpartner import service as s
from sportpartner.utils import (
    check_skill_compatibility, format_training_slot_status, is_event_upcoming,
)

TODAY = date(2026, 9, 22)


def test_pr1_compatibility() -> None:
    assert check_skill_compatibility(3, 3).startswith("Идеальное")
    assert check_skill_compatibility(2, 3).startswith("Допустимое")
    assert check_skill_compatibility(1, 4).startswith("Уровень не подходит")


def test_pr1_dates_and_slots() -> None:
    assert is_event_upcoming(TODAY, TODAY)
    assert not is_event_upcoming(date(2026, 9, 21), TODAY)
    assert format_training_slot_status(4, 3) == "Осталось мест: 1"
    assert "закрыт" in format_training_slot_status(4, 4)


@pytest.mark.parametrize("level", [0, 6, True, "2"])
def test_invalid_level(level) -> None:
    with pytest.raises(ValueError):
        check_skill_compatibility(level, 3)


def test_join_last_slot_and_cancel(data: dict) -> None:
    assert s.available_slots(data, 1) == 1
    s.join_event(data, 1, 1, TODAY)
    assert s.available_slots(data, 1) == 0
    assert s.statistics(data)["active"] == 4
    s.cancel_request(data, 4)
    assert s.available_slots(data, 1) == 1
    assert s.statistics(data)["cancelled"] == 1
    s.join_event(data, 1, 1, TODAY)
    assert len(data["requests"]) == 5


def test_duplicate_rejected_without_mutation(data: dict) -> None:
    before = deepcopy(s.statistics(data))
    with pytest.raises(ValueError, match="уже записан"):
        s.join_event(data, 2, 1, TODAY)
    assert s.statistics(data) == before


def test_full_event(data: dict) -> None:
    s.join_event(data, 1, 1, TODAY)
    s.add_athlete(data, "Павел", 25, "Москва", 3)
    with pytest.raises(ValueError, match="мест"):
        s.join_event(data, 6, 1, TODAY)


def test_past_event(data: dict) -> None:
    with pytest.raises(ValueError, match="прошла"):
        s.join_event(data, 1, 4, TODAY)


def test_event_today(data: dict) -> None:
    s.join_event(data, 1, 1, date(2026, 10, 5))
    assert s.available_slots(data, 1) == 0


def test_incompatible_athlete(data: dict) -> None:
    with pytest.raises(ValueError, match="Уровень"):
        s.join_event(data, 5, 1, TODAY)


def test_missing_ids(data: dict) -> None:
    for athlete_id, event_id in [(99, 1), (1, 99)]:
        with pytest.raises(ValueError):
            s.join_event(data, athlete_id, event_id, TODAY)
    with pytest.raises(ValueError):
        s.cancel_request(data, 99)


def test_repeat_cancel(data: dict) -> None:
    s.cancel_request(data, 1)
    with pytest.raises(ValueError, match="уже отменена"):
        s.cancel_request(data, 1)


def test_search_and_sort(data: dict) -> None:
    found = list(s.find_events(data, "мОСк", "ТЕННИС", 1, TODAY))
    assert len(found) == 1
    assert "Спартак" in s.describe_event(data, found[0])
    assert not list(s.find_events(data, "Москва", "теннис", 2, TODAY))
    assert not list(s.find_events(data, "Москва", "теннис", 5, TODAY))
    ordered = s.sort_events(data["events"], "date")
    assert "2026-09-01" in s.describe_event(data, ordered[0])
    assert "2026-10-05" in s.describe_event(data, data["events"][0])
    with pytest.raises(ValueError):
        s.sort_events(data["events"], "oops")


def test_statistics(data: dict) -> None:
    result = s.statistics(data)
    assert result["cities"] == ["Казань", "Москва"]
    assert result["by_sport"]["Бег"] == 2


def test_add_profile_and_event(data: dict) -> None:
    s.add_athlete(data, "Новый", 22, "Москва", 2)
    s.add_event(data, 1, "Москва", "Корт 3", "2026-10-10", 3, 2)
    s.join_event(data, 6, 5, TODAY)
    assert s.available_slots(data, 5) == 1


@pytest.mark.parametrize("event_date", ["2026-02-30", "20261005", "oops"])
def test_invalid_event_date(data: dict, event_date: str) -> None:
    with pytest.raises(ValueError):
        s.add_event(data, 1, "Москва", "Корт", event_date, 3, 4)
    assert len(data["events"]) == 4


def test_invalid_profile_and_capacity(data: dict) -> None:
    with pytest.raises(ValueError):
        s.add_athlete(data, " ", 20, "Москва", 2)
    with pytest.raises(ValueError):
        s.add_event(data, 1, "Москва", "Корт", "2026-10-10", 2, 0)
    assert len(data["athletes"]) == 5
