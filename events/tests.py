from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .forms import EventForm
from .models import Event, Sport


class EventTests(TestCase):
    def setUp(self):
        self.sport = Sport.objects.create(name="Теннис")
        self.tomorrow = timezone.localdate() + timedelta(days=1)
        self.event = Event.objects.create(
            title="Утренний спарринг",
            sport=self.sport,
            city="Москва",
            location="Корт №1",
            date=self.tomorrow,
            min_level=2,
            max_level=4,
            capacity=4,
        )

    def test_events_list_and_detail(self):
        resp_list = self.client.get(reverse("events:list"))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, "Утренний спарринг")

        resp_detail = self.client.get(reverse("events:detail", args=[self.event.pk]))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, "Теннис")

    def test_event_detail_404(self):
        resp = self.client.get(reverse("events:detail", args=[99999]))
        self.assertEqual(resp.status_code, 404)

    def test_event_form_valid_and_past_date_validation(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        bad_form = EventForm(
            data={
                "title": "Прошлая тренировка",
                "sport": self.sport.pk,
                "city": "Москва",
                "location": "Зал",
                "date": yesterday.isoformat(),
                "min_level": 1,
                "max_level": 3,
                "capacity": 2,
            }
        )
        self.assertFalse(bad_form.is_valid())
        self.assertIn("date", bad_form.errors)

        resp = self.client.post(
            reverse("events:create"),
            data={
                "title": "Вечерний матч",
                "sport": self.sport.pk,
                "city": "Москва",
                "location": "Корт №2",
                "date": self.tomorrow.isoformat(),
                "min_level": 1,
                "max_level": 5,
                "capacity": 6,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Event.objects.count(), 2)
