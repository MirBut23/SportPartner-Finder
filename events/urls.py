from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.events_list, name="list"),
    path("available/", views.available_events, name="available"),
    path("<int:event_id>/", views.event_detail, name="detail"),
]
