import json
from pathlib import Path
from django.shortcuts import render

DATA_FILE = Path("data/store.json")


def get_data():
    if not DATA_FILE.exists():
        return {"events": [], "sports": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def events_list(request):
    data = get_data()
    events = data.get("events", [])
    sports = {s["id"]: s["name"] for s in data.get("sports", [])}
    for e in events:
        e["sport_name"] = sports.get(e.get("sport_id"), "Спорт")
    return render(request, "events/event_list.html", {"events": events})


def event_detail(request, event_id):
    data = get_data()
    events = data.get("events", [])
    sports = {s["id"]: s["name"] for s in data.get("sports", [])}
    event = next((e for e in events if e.get("id") == event_id), None)
    if event:
        event["sport_name"] = sports.get(event.get("sport_id"), "Спорт")
    status_code = 200 if event else 404
    return render(
        request,
        "events/event_detail.html",
        {"event": event},
        status=status_code,
    )
