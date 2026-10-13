import json
from pathlib import Path
from django.shortcuts import render

DATA_FILE = Path("data/store.json")


def get_data():
    if not DATA_FILE.exists():
        return {"requests": [], "athletes": [], "events": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def requests_list(request):
    data = get_data()
    reqs = data.get("requests", [])
    athletes = {a["id"]: a["name"] for a in data.get("athletes", [])}
    events = {e["id"]: e["title"] for e in data.get("events", [])}
    for r in reqs:
        r["athlete_name"] = athletes.get(
            r.get("athlete_id"), "Спортсмен"
        )
        r["event_title"] = events.get(
            r.get("event_id"), "Событие"
        )
    return render(
        request,
        "requests/request_list.html",
        {"requests": reqs},
    )


def request_detail(request, request_id):
    data = get_data()
    reqs = data.get("requests", [])
    athletes = {a["id"]: a["name"] for a in data.get("athletes", [])}
    events = {e["id"]: e["title"] for e in data.get("events", [])}
    req_item = next((r for r in reqs if r.get("id") == request_id), None)
    if req_item:
        req_item["athlete_name"] = athletes.get(
            req_item.get("athlete_id"), "Спортсмен"
        )
        req_item["event_title"] = events.get(
            req_item.get("event_id"), "Событие"
        )
    status_code = 200 if req_item else 404
    return render(
        request,
        "requests/request_detail.html",
        {"req": req_item},
        status=status_code,
    )
