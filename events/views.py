import json
from pathlib import Path
from django.http import HttpResponse
from homepage.views import page

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
    items = ""
    for ev in events:
        sport = sports.get(ev.get("sport_id"), "Спорт")
        text = f"{ev.get('title', 'Тренировка')} ({sport}) — {ev.get('date')} в {ev.get('city')}"
        link = f"/events/{ev.get('id')}/"
        items += f'<li class="list-group-item d-flex justify-content-between align-items-center"><a href="{link}">{text}</a><span class="badge bg-primary rounded-pill">Мест: {ev.get("capacity")}</span></li>'
    content = f'''
    <h1>Список тренировок и событий</h1>
    <ul class="list-group mt-3">{items}</ul>
    '''
    return HttpResponse(page("Тренировки — SportPartner Finder", content))


def event_detail(request, event_id):
    data = get_data()
    events = data.get("events", [])
    sports = {s["id"]: s["name"] for s in data.get("sports", [])}
    event = next((e for e in events if e.get("id") == event_id), None)
    if event is None:
        content = '''
        <h1 class="text-danger">Событие не найдено</h1>
        <p>Тренировка с указанным ID отсутствует в базе.</p>
        <a href="/events/" class="btn btn-outline-secondary">← К списку тренировок</a>
        '''
        return HttpResponse(page("Событие не найдено", content), status=404)
    sport = sports.get(event.get("sport_id"), "Не указан")
    capacity = event.get("capacity", 0)
    badge = "bg-success" if capacity > 0 else "bg-danger"
    status_text = "Есть свободные места" if capacity > 0 else "Мест нет"
    content = f'''
    <div class="card">
        <div class="card-body">
            <h3 class="card-title">{event.get("title")}</h3>
            <p class="card-text"><strong>Вид спорта:</strong> {sport}</p>
            <p class="card-text"><strong>Город и локация:</strong> {event.get("city")}, {event.get("location")}</p>
            <p class="card-text"><strong>Дата:</strong> {event.get("date")}</p>
            <p class="card-text"><strong>Требуемый уровень:</strong> {event.get("min_level")} - {event.get("max_level")}</p>
            <p class="card-text"><strong>Статус:</strong> <span class="badge {badge}">{status_text}</span> (Вместимость: {capacity})</p>
            <a href="/events/" class="btn btn-outline-secondary mt-3">← К списку тренировок</a>
        </div>
    </div>
    '''
    return HttpResponse(page(event.get("title"), content), status=200)
