from django.db import models


class Sport(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Вид спорта",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Вид спорта"
        verbose_name_plural = "Виды спорта"


class Event(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название тренировки",
    )
    sport = models.ForeignKey(
        Sport,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Вид спорта",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
    )
    location = models.CharField(
        max_length=200,
        verbose_name="Локация",
    )
    date = models.DateField(
        verbose_name="Дата проведения",
    )
    min_level = models.PositiveIntegerField(
        default=1,
        verbose_name="Минимальный уровень",
    )
    max_level = models.PositiveIntegerField(
        default=5,
        verbose_name="Максимальный уровень",
    )
    capacity = models.PositiveIntegerField(
        default=2,
        verbose_name="Вместимость (мест)",
    )

    def is_suitable_for(self, athlete_level):
        return self.min_level <= athlete_level <= self.max_level

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        ordering = ["date", "pk"]
        verbose_name = "Тренировка"
        verbose_name_plural = "Тренировки"
