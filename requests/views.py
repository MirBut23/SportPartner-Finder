from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, render
from events.models import Event
from .models import Athlete, Request


def requests_list(request):
    event_id = request.GET.get("event", "").strip()
    athlete_id = request.GET.get("athlete", "").strip()
    sort = request.GET.get("sort", "id")

    reqs_qs = Request.objects.exclude(is_cancelled=True)

    if event_id.isdigit():
        reqs_qs = reqs_qs.filter(event_id=int(event_id))

    if athlete_id.isdigit():
        reqs_qs = reqs_qs.filter(athlete_id=int(athlete_id))

    reqs_qs = reqs_qs.annotate(
        athlete_name=F("athlete__name"),
        event_title=F("event__title"),
    )

    sort_fields = {
        "id": "id",
        "athlete": "athlete_name",
        "event": "event_title",
    }
    sort_field = sort_fields.get(sort, "id")
    reqs_qs = reqs_qs.order_by(sort_field, "id")

    reqs_qs = reqs_qs.values(
        "id",
        "athlete_name",
        "event_title",
        "status",
        "is_cancelled",
    )

    paginator = Paginator(reqs_qs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "requests": page_obj,
        "page_obj": page_obj,
        "events": Event.objects.order_by("title"),
        "athletes": Athlete.objects.order_by("name"),
        "selected_event": event_id,
        "selected_athlete": athlete_id,
        "sort": sort,
    }
    return render(request, "requests/request_list.html", context)


def request_detail(request, request_id):
    req_item = get_object_or_404(
        Request.objects.select_related("athlete", "event").annotate(
            athlete_name=F("athlete__name"),
            event_title=F("event__title"),
        ),
        pk=request_id,
    )
    return render(request, "requests/request_detail.html", {"req": req_item})


def statistics(request):
    stats = (
        Event.objects.annotate(
            requests_count=Count(
                "requests",
                filter=Q(requests__is_cancelled=False),
            ),
            event_title=F("title"),
        )
        .values("event_title", "requests_count")
        .order_by("-requests_count", "title")
    )
    return render(request, "requests/statistics.html", {"statistics": stats})
