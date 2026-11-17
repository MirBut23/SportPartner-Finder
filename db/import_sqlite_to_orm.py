import os
import sys
import sqlite3
from datetime import date
from pathlib import Path
import django
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SOURCE_DB = BASE_DIR / "data" / "sportpartner.sqlite"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportpartner.settings")
django.setup()

from events.models import Sport, Event
from requests.models import Athlete, Request


def main():
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row

        sports = connection.execute("SELECT id, name FROM sports ORDER BY id").fetchall()
        athletes = connection.execute("SELECT id, name, level, city FROM athletes ORDER BY id").fetchall()
        events = connection.execute(
            "SELECT id, title, sport_id, city, location, date, min_level, max_level, capacity FROM events ORDER BY id"
        ).fetchall()
        requests_rows = connection.execute(
            "SELECT id, athlete_id, event_id, status, is_cancelled FROM requests ORDER BY id"
        ).fetchall()

    with transaction.atomic():
        for row in sports:
            Sport.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"]},
            )

        for row in athletes:
            Athlete.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "level": row["level"],
                    "city": row["city"],
                },
            )

        for row in events:
            event_date = date.fromisoformat(row["date"])
            Event.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "title": row["title"],
                    "sport_id": row["sport_id"],
                    "city": row["city"],
                    "location": row["location"],
                    "date": event_date,
                    "min_level": row["min_level"],
                    "max_level": row["max_level"],
                    "capacity": row["capacity"],
                },
            )

        for row in requests_rows:
            Request.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "athlete_id": row["athlete_id"],
                    "event_id": row["event_id"],
                    "status": row["status"],
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )

    print("Перенос данных завершён успешно!")
    print(f"Видов спорта: {Sport.objects.count()}")
    print(f"Спортсменов: {Athlete.objects.count()}")
    print(f"Тренировок: {Event.objects.count()}")
    print(f"Заявок: {Request.objects.count()}")


if __name__ == "__main__":
    main()
