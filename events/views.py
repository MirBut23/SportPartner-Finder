from datetime import datetime
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from .models import Event, Sport


def events_list(request):
    search_query = request.GET.get("q", "").strip()
    sport_id = request.GET.get("sport", "").strip()
    sort_by = request.GET.get("sort", "date")

    events_qs = Event.objects.select_related("sport").annotate(
        sport_name=F("sport__name")
    )

    if search_query:
        events_qs = events_qs.filter(
            Q(title__icontains=search_query) | Q(city__icontains=search_query)
        )

    if sport_id.isdigit():
        events_qs = events_qs.filter(sport_id=int(sport_id))

    allowed_sort = {
        "date": "date",
        "title": "title",
        "capacity": "-capacity",
    }
    sort_field = allowed_sort.get(sort_by, "date")
    events_qs = events_qs.order_by(sort_field, "id")

    context = {
        "events": events_qs,
        "sports": Sport.objects.order_by("name"),
        "search_query": search_query,
        "selected_sport": sport_id,
        "sort_by": sort_by,
    }
    return render(request, "events/event_list.html", context)


def event_detail(request, event_id):
    event = get_object_or_404(
        Event.objects.select_related("sport").annotate(
            sport_name=F("sport__name")
        ),
        pk=event_id,
    )
    return render(request, "events/event_detail.html", {"event": event})


def available_events(request):
    event_date = request.GET.get("date", "").strip()
    events_qs = []
    error = None

    if event_date:
        try:
            selected_date = datetime.strptime(event_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            events_qs = (
                Event.objects.select_related("sport")
                .annotate(sport_name=F("sport__name"))
                .filter(date=selected_date, capacity__gt=0)
                .order_by("title")
            )

    return render(
        request,
        "events/available.html",
        {
            "events": events_qs,
            "event_date": event_date,
            "error": error,
        },
    )
