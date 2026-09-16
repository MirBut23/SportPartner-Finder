from datetime import date

# 1. Функция проверки совпадения уровня подготовки
def check_skill_compatibility(user_level: int, required_level: int) -> str:
    diff = abs(user_level - required_level)
    if diff == 0:
        return "Идеальное совпадение по уровню подготовки."
    elif diff == 1:
        return "Допустимое совпадение (комфортная тренировка возможна)."
    else:
        return "Уровень не подходит (слишком большая разница в навыках)."

# 2. Функция проверки актуальности даты тренировки
def is_event_upcoming(event_date: date, today_date: date) -> bool:
    return event_date >= today_date

# 3. Функция формирования статуса наличия свободных мест
def format_training_slot_status(capacity: int, registered: int) -> str:
    available_slots = capacity - registered
    if available_slots > 0:
        return f"Осталось мест: {available_slots}"
    else:
        return "Все места заняты. Набор закрыт."

# Входные данные карточки тренировки
event_sport = "Большой теннис"
event_location = "Корт 'Спартак', площадка 2"
event_target_level = 3  # Шкала от 1 (новичок) до 5 (профи)
event_capacity = 4
event_registered_count = 3
event_date = date(2026, 10, 5)

# Данные пользователя, ищущего напарника
user_name = "Алексей"
user_skill_level = 2
today = date(2026, 9, 20)

print(f"=== Проверка тренировки: {event_sport} ===")
print(f"Место проведения: {event_location}")
print(f"Дата события: {event_date}")

# Проверка 1: Дата
if is_event_upcoming(event_date, today):
    print("Статус даты: Событие актуально")
else:
    print("Статус даты: Событие уже прошло")

# Проверка 2: Места
slot_status = format_training_slot_status(event_capacity, event_registered_count)
print(f"Свободные места: {slot_status}")

# Проверка 3: Совместимость уровня
compatibility = check_skill_compatibility(user_skill_level, event_target_level)
print(f"Совместимость для кандидата {user_name} (уровень {user_skill_level}): {compatibility}")
