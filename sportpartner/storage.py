"""Чтение UTF-8 JSON и атомарная запись через временный файл."""

import json
import os
import tempfile
from pathlib import Path

from sportpartner.validation import validate_data
from sportpartner.models import Athlete, MatchRequest, SportType, TrainingEvent


def load_data(path: str | Path) -> dict:
    """Загрузить проверенные данные; ошибки передать интерфейсу."""
    with Path(path).open(encoding="utf-8") as stream:
        raw = validate_data(json.load(stream))
    athletes = {row["id"]: Athlete.from_dict(row)
                for row in raw["athletes"]}
    sports = {row["id"]: SportType.from_dict(row) for row in raw["sports"]}
    events = {row["id"]: TrainingEvent.from_dict(row, sports)
              for row in raw["events"]}
    requests = [MatchRequest.from_dict(row, athletes, events)
                for row in raw["requests"]]
    return {"athletes": list(athletes.values()),
            "sports": list(sports.values()),
            "events": list(events.values()), "requests": requests}


def save_data(path: str | Path, data: dict) -> None:
    """Сохранить весь набор, не оставляя частично записанный JSON."""
    raw = {name: [item.to_dict() for item in rows]
           for name, rows in data.items()}
    validate_data(raw)
    athletes = {a.id: a for a in data["athletes"]}
    sports = {s.id: s for s in data["sports"]}
    events = {e.id: e for e in data["events"]}
    for event in data["events"]:
        if sports.get(event.sport.id) is not event.sport:
            raise ValueError("Нарушена ссылка на объект спорта")
        expected = {r.athlete.id for r in data["requests"]
                    if r.event is event and r.status == "active"}
        if {a.id for a in event.participants} != expected:
            raise ValueError("Участники не согласованы с заявками")
        if any(athletes.get(a.id) is not a for a in event.participants):
            raise ValueError("Нарушена ссылка на объект участника")
    for request in data["requests"]:
        if (athletes.get(request.athlete.id) is not request.athlete
                or events.get(request.event.id) is not request.event):
            raise ValueError("Нарушены ссылки заявки на объекты")
    target = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent,
            prefix=target.name + ".", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(raw, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
