from django.db import models
from events.models import Event


class Athlete(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Имя спортсмена",
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name="Уровень подготовки",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
    )

    def __str__(self):
        return f"{self.name} (ур. {self.level})"

    class Meta:
        ordering = ["name"]
        verbose_name = "Спортсмен"
        verbose_name_plural = "Спортсмены"


class Request(models.Model):
    athlete = models.ForeignKey(
        Athlete,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name="Спортсмен",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name="Тренировка",
    )
    status = models.CharField(
        max_length=50,
        default="active",
        verbose_name="Статус заявки",
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Заявка отменена",
    )

    def cancel(self):
        self.is_cancelled = True
        self.status = "cancelled"
        self.save(update_fields=["is_cancelled", "status"])

    def __str__(self):
        return f"Заявка #{self.pk}: {self.athlete} -> {self.event}"

    class Meta:
        ordering = ["pk"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
