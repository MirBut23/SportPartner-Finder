import json
from pathlib import Path
from django.http import HttpResponse
from homepage.views import page

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
    items = ""
    for r in reqs:
        ath_name = athletes.get(r.get("athlete_id"), "Спортсмен")
        ev_title = events.get(r.get("event_id"), "Тренировка")
        status = r.get("status", "pending")
        badge = "bg-success" if status == "active" else "bg-secondary"
        link = f"/requests/{r.get('id')}/"
        items += f'''
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <a href="{link}">Заявка #{r.get("id")}: {ath_name} → {ev_title}</a>
            <span class="badge {badge}">{status}</span>
        </li>
        '''
    content = f'''
    <h1>Список заявок на участие</h1>
    <ul class="list-group mt-3">{items}</ul>
    '''
    return HttpResponse(page("Заявки — SportPartner Finder", content))


def request_detail(request, request_id):
    data = get_data()
    reqs = data.get("requests", [])
    athletes = {a["id"]: a["name"] for a in data.get("athletes", [])}
    events = {e["id"]: e["title"] for e in data.get("events", [])}
    req_item = next((r for r in reqs if r.get("id") == request_id), None)
    if req_item is None:
        content = '''
        <h1 class="text-danger">Заявка не найдена</h1>
        <p>Заявка с указанным ID отсутствует в системе.</p>
        <a href="/requests/" class="btn btn-outline-secondary">← К списку заявок</a>
        '''
        return HttpResponse(page("Заявка не найдена", content), status=404)
    ath_name = athletes.get(req_item.get("athlete_id"), "Неизвестен")
    ev_title = events.get(req_item.get("event_id"), "Неизвестно")
    status = req_item.get("status", "pending")
    badge = "bg-success" if status == "active" else "bg-secondary"
    content = f'''
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">Заявка #{req_item.get("id")}</h3>
            <p class="card-text"><strong>Спортсмен:</strong> {ath_name}</p>
            <p class="card-text"><strong>Событие:</strong> {ev_title}</p>
            <p class="card-text"><strong>Статус:</strong> <span class="badge {badge}">{status}</span></p>
            <a href="/requests/" class="btn btn-outline-secondary mt-3">← К списку заявок</a>
        </div>
    </div>
    '''
    return HttpResponse(page(f"Заявка #{req_item.get('id')}", content), status=200)
