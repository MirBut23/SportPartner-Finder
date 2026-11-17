from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from events.models import Event, Sport
from .models import Athlete, Request


class RequestTests(TestCase):
    def setUp(self):
        self.sport = Sport.objects.create(name="Бег")
        self.tomorrow = timezone.localdate() + timedelta(days=1)
        self.event = Event.objects.create(
            title="Кросс в парке",
            sport=self.sport,
            city="Москва",
            location="Парк Горького",
            date=self.tomorrow,
            min_level=2,
            max_level=4,
            capacity=2,
        )
        self.athlete_ok = Athlete.objects.create(name="Иван", level=3, city="Москва")
        self.athlete_low = Athlete.objects.create(name="Новичок", level=1, city="Москва")
        self.req = Request.objects.create(athlete=self.athlete_ok, event=self.event)

    def test_active_manager_and_list_view(self):
        self.assertEqual(Request.objects.active().count(), 1)
        resp = self.client.get(reverse("requests:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Иван")

    def test_create_request_level_and_duplicate_validation(self):
        # Неподходящий уровень спортсмена
        resp_low = self.client.post(
            reverse("requests:create"),
            data={"athlete": self.athlete_low.pk, "event": self.event.pk},
        )
        self.assertEqual(resp_low.status_code, 200)
        self.assertEqual(Request.objects.active().count(), 1)

        # Повторная заявка того же спортсмена
        resp_dup = self.client.post(
            reverse("requests:create"),
            data={"athlete": self.athlete_ok.pk, "event": self.event.pk},
        )
        self.assertEqual(resp_dup.status_code, 200)
        self.assertEqual(Request.objects.active().count(), 1)

    def test_edit_request_no_self_conflict(self):
        resp = self.client.post(
            reverse("requests:update", args=[self.req.pk]),
            data={"athlete": self.athlete_ok.pk, "event": self.event.pk},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Request.objects.active().count(), 1)

    def test_cancel_requires_post_and_preserves_record(self):
        url_cancel = reverse("requests:cancel", args=[self.req.pk])
        # GET-запрос запрещён (405 Method Not Allowed)
        resp_get = self.client.get(url_cancel)
        self.assertEqual(resp_get.status_code, 405)

        # POST-запрос меняет статус без удаления из БД
        resp_post = self.client.post(url_cancel)
        self.assertEqual(resp_post.status_code, 302)
        self.req.refresh_from_db()
        self.assertTrue(self.req.is_cancelled)
        self.assertEqual(self.req.status, "cancelled")
        self.assertEqual(Request.objects.active().count(), 0)
        self.assertEqual(Request.objects.count(), 1)
