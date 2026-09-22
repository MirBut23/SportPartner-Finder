"""Проверка схемы JSON и связности данных до изменения состояния."""

from sportpartner.utils import (
    parse_date, positive_int, skill_level, text_value,
)

COLLECTIONS = ("athletes", "sports", "events", "requests")


def validate_data(data: dict) -> dict:
    """Проверить идентификаторы, ссылки, статусы и вместимость."""
    if not isinstance(data, dict):
        raise ValueError("Корень JSON должен быть объектом")
    if set(data) != set(COLLECTIONS):
        raise ValueError("Нужны athletes, sports, events, requests")
    indexes = {}
    for name in COLLECTIONS:
        rows = data[name]
        if not isinstance(rows, list):
            raise ValueError(f"{name}: ожидается список")
        indexes[name] = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"{name}: запись должна быть словарём")
            ident = positive_int(row.get("id"), "ID")
            if ident in indexes[name]:
                raise ValueError(f"{name}: повтор ID {ident}")
            indexes[name][ident] = row
    for row in data["athletes"]:
        text_value(row.get("name"), "Имя")
        text_value(row.get("city"), "Город")
        positive_int(row.get("age"), "Возраст")
        skill_level(row.get("level"))
    for row in data["sports"]:
        text_value(row.get("name"), "Вид спорта")
        if not isinstance(row.get("equipment"), str):
            raise ValueError("Инвентарь должен быть строкой")
    for row in data["events"]:
        text_value(row.get("city"), "Город")
        text_value(row.get("location"), "Место")
        parse_date(row.get("date"))
        positive_int(row.get("capacity"), "Вместимость")
        skill_level(row.get("required_level"))
        sport_id = positive_int(row.get("sport_id"), "Вид спорта")
        if sport_id not in indexes["sports"]:
            raise ValueError("Тренировка ссылается на неизвестный спорт")
    active_pairs = set()
    counts = {}
    for row in data["requests"]:
        athlete_id = positive_int(row.get("athlete_id"), "Спортсмен")
        event_id = positive_int(row.get("event_id"), "Тренировка")
        if athlete_id not in indexes["athletes"]:
            raise ValueError("Заявка ссылается на неизвестного спортсмена")
        if event_id not in indexes["events"]:
            raise ValueError("Заявка ссылается на неизвестную тренировку")
        if row.get("status") not in ("active", "cancelled"):
            raise ValueError("Неизвестный статус заявки")
        if row["status"] == "active":
            pair = (athlete_id, event_id)
            if pair in active_pairs:
                raise ValueError("Повторная активная заявка")
            active_pairs.add(pair)
            athlete = indexes["athletes"][athlete_id]
            event = indexes["events"][event_id]
            if abs(athlete["level"] - event["required_level"]) > 1:
                raise ValueError("Уровень активного участника не подходит")
            counts[event_id] = counts.get(event_id, 0) + 1
    for event_id, count in counts.items():
        if count > indexes["events"][event_id]["capacity"]:
            raise ValueError("Вместимость тренировки превышена")
    return data
