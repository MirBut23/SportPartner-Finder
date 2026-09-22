"""Сценарии приложения: поиск объектов, запись, сортировка, статистика."""

from collections import Counter
from collections.abc import Iterator
from datetime import date
from typing import TypeVar

from sportpartner.models import Athlete, MatchRequest, SportType, TrainingEvent

Entity = Athlete | MatchRequest | SportType | TrainingEvent
T = TypeVar("T", Athlete, MatchRequest, SportType, TrainingEvent)


def get_item(data: dict, collection: str, ident: int) -> Entity:
    """Найти объект в коллекции или сообщить об отсутствующем ID."""
    for item in data[collection]:
        if item.id == ident:
            return item
    raise ValueError(f"{collection}: ID {ident} не найден")


def next_id(rows: list[T]) -> int:
    """Выдать следующий ID без удаления истории заявок."""
    return max((row.id for row in rows), default=0) + 1


def add_athlete(data: dict, name: str, age: int,
                city: str, level: int) -> Athlete:
    """Создать проверенный объект спортсмена и добавить в коллекцию."""
    athlete = Athlete(next_id(data["athletes"]), name, age, city, level)
    data["athletes"].append(athlete)
    return athlete


def add_event(data: dict, sport_id: int, city: str, location: str,
              event_date: str, required_level: int,
              capacity: int) -> TrainingEvent:
    """Создать тренировку, связанную с существующим видом спорта."""
    sport = get_item(data, "sports", sport_id)
    event = TrainingEvent(next_id(data["events"]), sport, city, location,
                          event_date, required_level, capacity)
    data["events"].append(event)
    return event


def registered_count(data: dict, event_id: int) -> int:
    """Посчитать активных участников объекта TrainingEvent."""
    return len(get_item(data, "events", event_id).participants)


def available_slots(data: dict, event_id: int) -> int:
    """Делегировать вычисление свободных мест объекту тренировки."""
    return get_item(data, "events", event_id).available_slots


def join_event(data: dict, athlete_id: int, event_id: int,
               today: date | None = None) -> MatchRequest:
    """Связать спортсмена и актуальную тренировку через новую заявку."""
    athlete = get_item(data, "athletes", athlete_id)
    event = get_item(data, "events", event_id)
    if not event.is_upcoming(today or date.today()):
        raise ValueError("Тренировка уже прошла")
    request = MatchRequest(next_id(data["requests"]), athlete, event)
    data["requests"].append(request)
    return request


def cancel_request(data: dict, request_id: int) -> MatchRequest:
    """Найти заявку и поручить ей согласованную отмену."""
    request = get_item(data, "requests", request_id)
    request.cancel()
    return request


def find_events(data: dict, city: str = "", sport: str = "",
                athlete_id: int | None = None,
                today: date | None = None) -> Iterator[TrainingEvent]:
    """Генерировать подходящие объекты тренировок."""
    athlete = (get_item(data, "athletes", athlete_id)
               if athlete_id is not None else None)
    for event in data["events"]:
        if city.casefold() not in event.city.casefold():
            continue
        if sport.casefold() not in event.sport.name.casefold():
            continue
        if not event.is_upcoming(today or date.today()):
            continue
        if event.available_slots <= 0:
            continue
        if athlete is not None:
            if not athlete.is_compatible(event.required_level):
                continue
            if any(a.id == athlete.id for a in event.participants):
                continue
        yield event


def sort_events(events: list[TrainingEvent], key: str = "date"
                ) -> list[TrainingEvent]:
    """Сортировать копию списка объектов по выбранному атрибуту."""
    if key not in ("date", "capacity"):
        raise ValueError("Сортировка: date или capacity")
    return sorted(events, key=lambda event: getattr(event, key))


def statistics(data: dict) -> dict:
    """Вернуть ту же статистику, что и в функциональной версии."""
    sports = Counter(e.sport.name for e in data["events"])
    return {
        "athletes": len(data["athletes"]), "events": len(data["events"]),
        "active": sum(r.status == "active" for r in data["requests"]),
        "cancelled": sum(r.status == "cancelled" for r in data["requests"]),
        "cities": sorted({e.city for e in data["events"]}),
        "by_sport": dict(sports),
    }


def describe_event(data: dict, event: TrainingEvent) -> str:
    """Сохранить интерфейс ПР2, используя строковое представление."""
    return str(event)


def describe_athlete(athlete: Athlete) -> str:
    """Использовать полиморфное строковое представление спортсмена."""
    return str(athlete)


def describe_request(request: MatchRequest) -> str:
    """Использовать строковое представление заявки."""
    return str(request)


def describe_sport(sport: SportType) -> str:
    """Использовать строковое представление вида спорта."""
    return str(sport)
