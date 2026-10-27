import sqlite3
from pathlib import Path
from django.shortcuts import render

DB_PATH = Path("data/sportpartner.sqlite")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def requests_list(request):
    conn = get_db()
    query = """
    SELECT requests.id, athletes.name AS athlete_name,
           events.title AS event_title, requests.status
    FROM requests
    JOIN athletes ON requests.athlete_id = athletes.id
    JOIN events ON requests.event_id = events.id
    WHERE requests.is_cancelled = 0
    ORDER BY requests.id;
    """
    reqs = conn.execute(query).fetchall()
    conn.close()
    return render(request, "requests/request_list.html", {"requests": reqs})


def request_detail(request, request_id):
    conn = get_db()
    query = """
    SELECT requests.id, athletes.name AS athlete_name,
           events.title AS event_title, requests.status
    FROM requests
    JOIN athletes ON requests.athlete_id = athletes.id
    JOIN events ON requests.event_id = events.id
    WHERE requests.id = ?;
    """
    req_item = conn.execute(query, (request_id,)).fetchone()
    conn.close()
    status_code = 200 if req_item else 404
    return render(
        request,
        "requests/request_detail.html",
        {"req": req_item},
        status=status_code,
    )


def statistics(request):
    conn = get_db()
    query = """
    SELECT events.title AS event_title,
           COUNT(requests.id) AS requests_count
    FROM events
    LEFT JOIN requests ON events.id = requests.event_id
                      AND requests.is_cancelled = 0
    GROUP BY events.id, events.title
    ORDER BY requests_count DESC;
    """
    stats = conn.execute(query).fetchall()
    conn.close()
    return render(request, "requests/statistics.html", {"statistics": stats})
