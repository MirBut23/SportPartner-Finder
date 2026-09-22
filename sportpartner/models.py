"""Сущности SportPartner Finder и относящееся к ним поведение."""

from datetime import date

from sportpartner.utils import (
    check_skill_compatibility, format_training_slot_status, is_event_upcoming,
    parse_date, positive_int, skill_level, text_value,
)


class User:
    """Базовый пользователь: идентификатор, имя и город."""

    def __init__(self, ident: int, name: str, city: str) -> None:
        self.id = positive_int(ident, "ID")
        self.name = text_value(name, "Имя")
        self.city = text_value(city, "Город")

    def __str__(self) -> str:
        return f"#{self.id} {self.name}, {self.city}"


class Athlete(User):
    """Спортсмен является пользователем с возрастом и уровнем."""

    def __init__(self, ident: int, name: str, age: int,
                 city: str, level: int) -> None:
        super().__init__(ident, name, city)
        self.age = positive_int(age, "Возраст")
        self._level = skill_level(level)

    @property
    def level(self) -> int:
        """Уровень нельзя изменить в обход проверки действующих заявок."""
        return self._level

    def compatibility(self, required_level: int) -> str:
        """Использовать сохранённую функцию ПР1 для текста совместимости."""
        return check_skill_compatibility(self.level, required_level)

    def is_compatible(self, required_level: int) -> bool:
        """Допустить разницу уровней не более единицы."""
        return abs(self.level - skill_level(required_level)) <= 1

    def __str__(self) -> str:
        return (f"#{self.id} {self.name}, {self.age} лет, {self.city}, "
                f"уровень {self.level}")

    def to_dict(self) -> dict:
        """Представить профиль в совместимом с ПР2 формате."""
        return {"id": self.id, "name": self.name, "age": self.age,
                "city": self.city, "level": self.level}

    @classmethod
    def from_dict(cls, row: dict) -> "Athlete":
        """Создать экземпляр из проверенной записи JSON."""
        return cls(row["id"], row["name"], row["age"],
                   row["city"], row["level"])


class SportType:
    """Вид спорта и необходимый инвентарь."""

    def __init__(self, ident: int, name: str, equipment: str) -> None:
        self.id = positive_int(ident, "ID")
        self.name = text_value(name, "Спорт")
        if not isinstance(equipment, str):
            raise ValueError("Инвентарь должен быть строкой")
        self.equipment = equipment

    def __str__(self) -> str:
        return f"#{self.id} {self.name} ({self.equipment})"

    def to_dict(self) -> dict:
        """Преобразовать вид спорта в словарь."""
        return {"id": self.id, "name": self.name,
                "equipment": self.equipment}

    @classmethod
    def from_dict(cls, row: dict) -> "SportType":
        """Восстановить вид спорта из JSON."""
        return cls(row["id"], row["name"], row["equipment"])


class TrainingEvent:
    """Тренировка хранит объект спорта и управляет свободными местами."""

    def __init__(self, ident: int, sport: SportType, city: str,
                 location: str, event_date: str, required_level: int,
                 capacity: int) -> None:
        self.id = positive_int(ident, "ID")
        if not isinstance(sport, SportType):
            raise ValueError("Нужен объект SportType")
        self.sport = sport
        self.city = text_value(city, "Город")
        self.location = text_value(location, "Место")
        self.date = parse_date(event_date)
        self._required_level = skill_level(required_level)
        self._capacity = positive_int(capacity, "Вместимость")
        self._participants: list[Athlete] = []

    @property
    def capacity(self) -> int:
        """Вместимость доступна только для чтения."""
        return self._capacity

    @property
    def required_level(self) -> int:
        """Уровень нельзя менять в обход проверки состава участников."""
        return self._required_level

    @property
    def participants(self) -> tuple[Athlete, ...]:
        """Неизменяемое представление списка участников."""
        return tuple(self._participants)

    @property
    def available_slots(self) -> int:
        """Вычислить свободные места из текущего состава."""
        return self.capacity - len(self._participants)

    def is_upcoming(self, today: date) -> bool:
        """Проверить актуальность даты через функцию ПР1."""
        return is_event_upcoming(self.date, today)

    def add_participant(self, athlete: Athlete) -> None:
        """Зарезервировать место; дата проверяется при новой заявке."""
        if not isinstance(athlete, Athlete):
            raise ValueError("Нужен объект Athlete")
        if not athlete.is_compatible(self.required_level):
            raise ValueError("Уровень подготовки не подходит")
        if any(a.id == athlete.id for a in self._participants):
            raise ValueError("Спортсмен уже записан")
        if self.available_slots <= 0:
            raise ValueError("Свободных мест нет")
        self._participants.append(athlete)

    def remove_participant(self, athlete: Athlete) -> None:
        """Освободить место спортсмена при отмене заявки."""
        for participant in self._participants:
            if participant.id == athlete.id:
                self._participants.remove(participant)
                return
        raise ValueError("Спортсмен не записан")

    def __str__(self) -> str:
        status = format_training_slot_status(
            self.capacity, len(self._participants),
        )
        return (f"#{self.id} {self.sport.name} | {self.city} | "
                f"{self.location} | {self.date} | "
                f"уровень {self.required_level} | {status}")

    def to_dict(self) -> dict:
        """Заменить ссылку на SportType его идентификатором."""
        return {"id": self.id, "sport_id": self.sport.id, "city": self.city,
                "location": self.location, "date": self.date.isoformat(),
                "required_level": self.required_level,
                "capacity": self.capacity}

    @classmethod
    def from_dict(cls, row: dict, sports: dict[int, SportType]
                  ) -> "TrainingEvent":
        """Связать событие с уже созданным объектом SportType."""
        return cls(row["id"], sports[row["sport_id"]], row["city"],
                   row["location"], row["date"], row["required_level"],
                   row["capacity"])


class MatchRequest:
    """Заявка объединяет спортсмена и тренировку через ссылки на объекты."""

    STATUSES = ("active", "cancelled")

    def __init__(self, ident: int, athlete: Athlete, event: TrainingEvent,
                 status: str = "active") -> None:
        self.id = positive_int(ident, "ID")
        if not isinstance(athlete, Athlete):
            raise ValueError("Нужен объект Athlete")
        if not isinstance(event, TrainingEvent):
            raise ValueError("Нужен объект TrainingEvent")
        if status not in self.STATUSES:
            raise ValueError("Неизвестный статус заявки")
        self.athlete = athlete
        self.event = event
        self._status = status
        if status == "active":
            event.add_participant(athlete)

    @property
    def status(self) -> str:
        """Статус меняется только согласованно с освобождением места."""
        return self._status

    def cancel(self) -> None:
        """Отменить заявку и освободить место в связанном событии."""
        if self.status == "cancelled":
            raise ValueError("Заявка уже отменена")
        self.event.remove_participant(self.athlete)
        self._status = "cancelled"

    def __str__(self) -> str:
        return (f"#{self.id}: спортсмен {self.athlete.id}, "
                f"тренировка {self.event.id}, {self.status}")

    def to_dict(self) -> dict:
        """Сериализовать ссылки на объекты в идентификаторы."""
        return {"id": self.id, "athlete_id": self.athlete.id,
                "event_id": self.event.id, "status": self.status}

    @classmethod
    def from_dict(cls, row: dict, athletes: dict[int, Athlete],
                  events: dict[int, TrainingEvent]) -> "MatchRequest":
        """Восстановить ссылки, включая заявки на прошедшие события."""
        return cls(row["id"], athletes[row["athlete_id"]],
                   events[row["event_id"]], row["status"])
