"""Операции с коллекциями спортсменов, тренировок и заявок."""

from collections import Counter
from collections.abc import Iterator
from datetime import date

from sportpartner.utils import (
    format_training_slot_status, is_event_upcoming, parse_date,
    positive_int, skill_level, text_value,
)


def get_item(data: dict, collection: str, ident: int) -> dict:
    """Найти запись или сообщить об отсутствующем ID."""
    for item in data[collection]:
        if item["id"] == ident:
            return item
    raise ValueError(f"{collection}: ID {ident} не найден")


def next_id(rows: list[dict]) -> int:
    """Выдать ID, не переиспользуя отменённые заявки."""
    return max((row["id"] for row in rows), default=0) + 1


def add_athlete(data: dict, name: str, age: int,
                city: str, level: int) -> dict:
    """Добавить проверенный профиль спортсмена."""
    athlete = {
        "id": next_id(data["athletes"]),
        "name": text_value(name, "Имя"),
        "age": positive_int(age, "Возраст"),
        "city": text_value(city, "Город"),
        "level": skill_level(level),
    }
    data["athletes"].append(athlete)
    return athlete


def add_event(data: dict, sport_id: int, city: str, location: str,
              event_date: str, required_level: int, capacity: int) -> dict:
    """Добавить тренировку существующего вида спорта."""
    get_item(data, "sports", sport_id)
    event = {
        "id": next_id(data["events"]), "sport_id": sport_id,
        "city": text_value(city, "Город"),
        "location": text_value(location, "Место"),
        "date": parse_date(event_date).isoformat(),
        "required_level": skill_level(required_level),
        "capacity": positive_int(capacity, "Вместимость"),
    }
    data["events"].append(event)
    return event


def registered_count(data: dict, event_id: int) -> int:
    """Посчитать только активные заявки выбранной тренировки."""
    return sum(r["event_id"] == event_id and r["status"] == "active"
               for r in data["requests"])


def available_slots(data: dict, event_id: int) -> int:
    """Вернуть количество свободных мест."""
    event = get_item(data, "events", event_id)
    return event["capacity"] - registered_count(data, event_id)


def join_event(data: dict, athlete_id: int, event_id: int,
               today: date | None = None) -> dict:
    """Записать спортсмена, проверив дату, уровень, дубликаты и места."""
    athlete = get_item(data, "athletes", athlete_id)
    event = get_item(data, "events", event_id)
    if not is_event_upcoming(parse_date(event["date"]), today or date.today()):
        raise ValueError("Тренировка уже прошла")
    if abs(athlete["level"] - event["required_level"]) > 1:
        raise ValueError("Уровень подготовки не подходит")
    for request in data["requests"]:
        if (request["athlete_id"] == athlete_id
                and request["event_id"] == event_id
                and request["status"] == "active"):
            raise ValueError("Спортсмен уже записан")
    if available_slots(data, event_id) <= 0:
        raise ValueError("Свободных мест нет")
    request = {
        "id": next_id(data["requests"]), "athlete_id": athlete_id,
        "event_id": event_id, "status": "active",
    }
    data["requests"].append(request)
    return request


def cancel_request(data: dict, request_id: int) -> dict:
    """Отменить активную заявку, сохранив её в истории."""
    request = get_item(data, "requests", request_id)
    if request["status"] == "cancelled":
        raise ValueError("Заявка уже отменена")
    request["status"] = "cancelled"
    return request


def find_events(data: dict, city: str = "", sport: str = "",
                athlete_id: int | None = None,
                today: date | None = None) -> Iterator[dict]:
    """Генерировать подходящие события с местами и актуальной датой."""
    athlete = (get_item(data, "athletes", athlete_id)
               if athlete_id is not None else None)
    for event in data["events"]:
        discipline = get_item(data, "sports", event["sport_id"])
        if city.casefold() not in event["city"].casefold():
            continue
        if sport.casefold() not in discipline["name"].casefold():
            continue
        if not is_event_upcoming(parse_date(event["date"]),
                                 today or date.today()):
            continue
        if available_slots(data, event["id"]) <= 0:
            continue
        if athlete is not None:
            if abs(athlete["level"] - event["required_level"]) > 1:
                continue
            if any(r["athlete_id"] == athlete_id
                   and r["event_id"] == event["id"]
                   and r["status"] == "active" for r in data["requests"]):
                continue
        yield event


def sort_events(events: list[dict], key: str = "date") -> list[dict]:
    """Сортировать копию по дате или вместимости."""
    if key not in ("date", "capacity"):
        raise ValueError("Сортировка: date или capacity")
    return sorted(events, key=lambda event: event[key])


def statistics(data: dict) -> dict:
    """Вернуть статистику количества, городов и видов спорта."""
    sports = Counter(get_item(data, "sports", e["sport_id"])["name"]
                     for e in data["events"])
    return {
        "athletes": len(data["athletes"]), "events": len(data["events"]),
        "active": sum(r["status"] == "active" for r in data["requests"]),
        "cancelled": sum(r["status"] == "cancelled"
                         for r in data["requests"]),
        "cities": sorted({e["city"] for e in data["events"]}),
        "by_sport": dict(sports),
    }


def describe_event(data: dict, event: dict) -> str:
    """Сформировать карточку события для консоли."""
    sport = get_item(data, "sports", event["sport_id"])["name"]
    status = format_training_slot_status(
        event["capacity"], registered_count(data, event["id"]),
    )
    return (f"#{event['id']} {sport} | {event['city']} | "
            f"{event['location']} | "
            f"{event['date']} | уровень {event['required_level']} | {status}")


def describe_athlete(athlete: dict) -> str:
    """Сформировать краткое представление профиля."""
    return (f"#{athlete['id']} {athlete['name']}, {athlete['age']} лет, "
            f"{athlete['city']}, уровень {athlete['level']}")


def describe_request(request: dict) -> str:
    """Сформировать краткое представление заявки."""
    return (f"#{request['id']}: спортсмен {request['athlete_id']}, "
            f"тренировка {request['event_id']}, {request['status']}")


def describe_sport(sport: dict) -> str:
    """Сформировать представление вида спорта."""
    return f"#{sport['id']} {sport['name']} ({sport['equipment']})"
