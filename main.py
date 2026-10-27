import json
from pathlib import Path

DATA_FILE = Path("data/store.json")


def load_data():
    if not DATA_FILE.exists():
        return {
            "sports": [],
            "athletes": [],
            "events": [],
            "requests": [],
        }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_events(data):
    events = data.get("events", [])
    sports = {s["id"]: s["name"] for s in data.get("sports", [])}
    print("\n=== Список тренировок ===")
    if not events:
        print("Тренировок пока нет.")
        return
    for e in events:
        s_name = sports.get(e.get("sport_id"), "Спорт")
        cap = e.get("capacity", 0)
        status = f"Мест: {cap}" if cap > 0 else "Мест нет"
        print(
            f"[{e['id']}] {e['title']} ({s_name}) | "
            f"{e['city']}, {e['location']} | {e['date']} | {status}"
        )


def add_event(data):
    print("\n=== Создание новой тренировки ===")
    sports = data.get("sports", [])
    if not sports:
        sports = [
            {"id": 1, "name": "Теннис"},
            {"id": 2, "name": "Баскетбол"},
            {"id": 3, "name": "Бег"},
        ]
        data["sports"] = sports

    print("Выберите вид спорта:")
    for s in sports:
        print(f"  {s['id']}. {s['name']}")
    try:
        sport_id = int(input("Введите ID вида спорта: ").strip())
    except ValueError:
        sport_id = 1

    title = input("Название тренировки: ").strip() or "Тренировка"
    city = input("Город [Москва]: ").strip() or "Москва"
    location = input("Локация (корт, манеж): ").strip() or "Спорткомплекс"
    date = input("Дата (ГГГГ-ММ-ДД) [2026-10-30]: ").strip() or "2026-10-30"

    try:
        capacity = int(input("Количество мест [2]: ").strip() or "2")
    except ValueError:
        capacity = 2

    events = data.get("events", [])
    next_id = max([e["id"] for e in events], default=0) + 1

    new_event = {
        "id": next_id,
        "title": title,
        "sport_id": sport_id,
        "city": city,
        "location": location,
        "date": date,
        "min_level": 1,
        "max_level": 5,
        "capacity": capacity,
    }

    events.append(new_event)
    data["events"] = events
    save_data(data)
    print(f"\nУспешно создано событие #{next_id}: '{title}'!")


def list_requests(data):
    reqs = data.get("requests", [])
    athletes = {a["id"]: a["name"] for a in data.get("athletes", [])}
    events = {e["id"]: e["title"] for e in data.get("events", [])}
    print("\n=== Список заявок ===")
    if not reqs:
        print("Заявок нет.")
        return
    for r in reqs:
        ath = athletes.get(r.get("athlete_id"), "Спортсмен")
        ev = events.get(r.get("event_id"), "Тренировка")
        print(f"Заявка #{r['id']}: {ath} -> {ev} [{r.get('status')}]")


def main_menu():
    while True:
        data = load_data()
        print("\n==================================")
        print("   SportPartner Finder — Меню     ")
        print("==================================")
        print("1. Показать список тренировок")
        print("2. Создать новую тренировку")
        print("3. Показать список заявок")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            list_events(data)
        elif choice == "2":
            add_event(data)
        elif choice == "3":
            list_requests(data)
        elif choice == "0":
            print("Завершение работы.")
            break
        else:
            print("Неверный пункт, попробуйте снова.")


if __name__ == "__main__":
    main_menu()
