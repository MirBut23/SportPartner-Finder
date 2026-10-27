import sqlite3
from pathlib import Path
from django.shortcuts import render

DB_PATH = Path("data/sportpartner.sqlite")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def events_list(request):
    conn = get_db()
    query = """
    SELECT events.id, events.title, sports.name AS sport_name,
           events.city, events.location, events.date, events.capacity
    FROM events
    JOIN sports ON events.sport_id = sports.id
    ORDER BY events.id;
    """
    events = conn.execute(query).fetchall()
    conn.close()
    return render(request, "events/event_list.html", {"events": events})


def event_detail(request, event_id):
    conn = get_db()
    query = """
    SELECT events.id, events.title, sports.name AS sport_name,
           events.city, events.location, events.date,
           events.min_level, events.max_level, events.capacity
    FROM events
    JOIN sports ON events.sport_id = sports.id
    WHERE events.id = ?;
    """
    event = conn.execute(query, (event_id,)).fetchone()
    conn.close()
    status_code = 200 if event else 404
    return render(
        request,
        "events/event_detail.html",
        {"event": event},
        status=status_code,
    )


def available_events(request):
    event_date = request.GET.get("date")
    events = []
    if event_date:
        conn = get_db()
        query = """
        SELECT events.id, events.title, sports.name AS sport_name,
               events.city, events.location, events.date, events.capacity
        FROM events
        JOIN sports ON events.sport_id = sports.id
        WHERE events.date = ? AND events.capacity > 0
        ORDER BY events.title;
        """
        events = conn.execute(query, (event_date,)).fetchall()
        conn.close()
    return render(
        request,
        "events/available.html",
        {"events": events, "event_date": event_date},
    )
