"""Проверки и исходные функции практической работы 1."""

from datetime import date


def positive_int(value: int, field: str) -> int:
    """Проверить положительное целое число, исключая bool."""
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field}: нужно положительное целое число")
    return value


def text_value(value: str, field: str) -> str:
    """Проверить непустую строку."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: нужна непустая строка")
    return value.strip()


def skill_level(value: int) -> int:
    """Проверить уровень подготовки по шкале 1-5."""
    positive_int(value, "Уровень")
    if value > 5:
        raise ValueError("Уровень должен быть от 1 до 5")
    return value


def parse_date(value: str) -> date:
    """Преобразовать строку YYYY-MM-DD в дату."""
    if not isinstance(value, str):
        raise ValueError("Дата должна быть строкой YYYY-MM-DD")
    try:
        result = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Неверная дата, нужен формат YYYY-MM-DD") from error
    if result.isoformat() != value:
        raise ValueError("Нужен формат YYYY-MM-DD")
    return result


def check_skill_compatibility(user_level: int, required_level: int) -> str:
    """Вернуть исходное описание совместимости из ПР1."""
    diff = abs(skill_level(user_level) - skill_level(required_level))
    if diff == 0:
        return "Идеальное совпадение по уровню подготовки."
    if diff == 1:
        return "Допустимое совпадение (комфортная тренировка возможна)."
    return "Уровень не подходит (слишком большая разница в навыках)."


def is_event_upcoming(event_date: date, today_date: date) -> bool:
    """Событие актуально в день проведения и позже."""
    return event_date >= today_date


def format_training_slot_status(capacity: int, registered: int) -> str:
    """Вернуть исходное описание свободных мест из ПР1."""
    positive_int(capacity, "Вместимость")
    if type(registered) is not int or registered < 0:
        raise ValueError("Число участников не может быть отрицательным")
    available_slots = capacity - registered
    if available_slots > 0:
        return f"Осталось мест: {available_slots}"
    return "Все места заняты. Набор закрыт."
