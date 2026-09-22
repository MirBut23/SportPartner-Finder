"""Консольное меню; каждое изменение сохраняется как транзакция."""

from argparse import ArgumentParser
from copy import deepcopy
from datetime import date
from pathlib import Path

from sportpartner import service
from sportpartner.storage import load_data, save_data

MENU = """
1. Все тренировки       2. Поиск подходящих тренировок
3. Сортировка           4. Записаться на тренировку
5. Отменить заявку      6. Все заявки
7. Статистика           8. Добавить спортсмена
9. Добавить тренировку  10. Спортсмены
11. Виды спорта         0. Выход
"""


def show_events(data: dict, events: list) -> None:
    """Вывести карточки или сообщение о пустом результате."""
    if not events:
        print("Тренировки не найдены")
    for event in events:
        print(service.describe_event(data, event))


def run_menu(data: dict, path: Path, today: date) -> int:
    """Обрабатывать ввод без потери данных при неудачном сохранении."""
    while True:
        print(MENU)
        try:
            command = input("Команда: ").strip()
            if command == "0":
                return 0
            if command == "1":
                show_events(data, data["events"])
            elif command == "2":
                city = input("Город (Enter = любой): ").strip()
                sport = input("Спорт (Enter = любой): ").strip()
                value = input("ID спортсмена (Enter = любой): ").strip()
                athlete_id = int(value) if value else None
                show_events(data, list(service.find_events(
                    data, city, sport, athlete_id, today,
                )))
            elif command == "3":
                key = input("Ключ date/capacity: ").strip()
                show_events(data, service.sort_events(data["events"], key))
            elif command == "6":
                for request in data["requests"]:
                    print(service.describe_request(request))
                if not data["requests"]:
                    print("Заявок нет")
            elif command == "7":
                for name, value in service.statistics(data).items():
                    print(f"{name}: {value}")
            elif command == "10":
                for athlete in data["athletes"]:
                    print(service.describe_athlete(athlete))
            elif command == "11":
                for sport in data["sports"]:
                    print(service.describe_sport(sport))
            elif command in ("4", "5", "8", "9"):
                candidate = deepcopy(data)
                if command == "4":
                    athlete_id = int(input("ID спортсмена: "))
                    event_id = int(input("ID тренировки: "))
                    service.join_event(candidate, athlete_id, event_id, today)
                elif command == "5":
                    request_id = int(input("ID заявки: "))
                    service.cancel_request(candidate, request_id)
                elif command == "8":
                    name = input("Имя: ")
                    age = int(input("Возраст: "))
                    city = input("Город: ")
                    level = int(input("Уровень 1-5: "))
                    service.add_athlete(candidate, name, age, city, level)
                else:
                    sport_id = int(input("ID вида спорта: "))
                    city = input("Город: ")
                    location = input("Место: ")
                    event_date = input("Дата YYYY-MM-DD: ")
                    level = int(input("Уровень 1-5: "))
                    capacity = int(input("Число мест: "))
                    service.add_event(candidate, sport_id, city, location,
                                      event_date, level, capacity)
                save_data(path, candidate)
                data = candidate
                print("Изменение сохранено")
            else:
                print("Неизвестная команда")
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена")
            return 0


def main() -> int:
    """Загрузить файл и запустить меню с реальной или учебной датой."""
    parser = ArgumentParser(description="SportPartner Finder")
    default = Path(__file__).resolve().parent.parent / "data" / "store.json"
    parser.add_argument("--data", type=Path, default=default)
    parser.add_argument("--today", type=date.fromisoformat,
                        default=date.today())
    args = parser.parse_args()
    try:
        data = load_data(args.data)
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки: {error}. Исходный файл не изменён.")
        return 1
    print(f"SportPartner Finder | дата проверки {args.today}")
    return run_menu(data, args.data, args.today)
