from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from events.models import Event
from .forms import RequestFilterForm, RequestForm
from .models import Request


def requests_list(request):
    form = RequestFilterForm(request.GET or None)
    form_valid = form.is_bound and form.is_valid()

    event_id = None
    athlete_id = None
    sort = "id"
    error = None

    if form.is_bound:
        if form_valid:
            selected_event = form.cleaned_data.get("event")
            selected_athlete = form.cleaned_data.get("athlete")
            event_id = selected_event.pk if selected_event else None
            athlete_id = selected_athlete.pk if selected_athlete else None
            sort = form.cleaned_data.get("sort") or "id"
        else:
            error = "Проверьте введённые значения фильтров."

    reqs_qs = Request.objects.active()

    if form_valid:
        if event_id:
            reqs_qs = reqs_qs.filter(event_id=event_id)
        if athlete_id:
            reqs_qs = reqs_qs.filter(athlete_id=athlete_id)

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
        "form": form,
        "error": error,
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


def request_create(request):
    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            athlete = form.cleaned_data["athlete"]
            event = form.cleaned_data["event"]

            already_booked = Request.objects.active().filter(
                athlete=athlete,
                event=event,
            ).exists()
            active_count = Request.objects.active().filter(event=event).count()

            if already_booked:
                form.add_error(None, "Этот спортсмен уже записан на выбранную тренировку.")
            elif active_count >= event.capacity:
                form.add_error(None, "На выбранную тренировку больше нет свободных мест.")
            else:
                form.save()
                return redirect("requests:list")
    else:
        form = RequestForm()

    return render(request, "requests/request_form.html", {"form": form})


def request_update(request, request_id):
    req_obj = get_object_or_404(Request.objects.active(), pk=request_id)

    if request.method == "POST":
        form = RequestForm(request.POST, instance=req_obj)
        if form.is_valid():
            athlete = form.cleaned_data["athlete"]
            event = form.cleaned_data["event"]

            already_booked = (
                Request.objects.active()
                .filter(athlete=athlete, event=event)
                .exclude(pk=req_obj.pk)
                .exists()
            )
            active_count = (
                Request.objects.active()
                .filter(event=event)
                .exclude(pk=req_obj.pk)
                .count()
            )

            if already_booked:
                form.add_error(None, "Этот спортсмен уже записан на выбранную тренировку.")
            elif active_count >= event.capacity:
                form.add_error(None, "На выбранную тренировку больше нет свободных мест.")
            else:
                form.save()
                return redirect("requests:list")
    else:
        form = RequestForm(instance=req_obj)

    return render(
        request,
        "requests/request_form.html",
        {"form": form, "req_obj": req_obj},
    )


@require_POST
def request_cancel(request, request_id):
    req_obj = get_object_or_404(Request.objects.active(), pk=request_id)
    req_obj.cancel()
    return redirect("requests:list")


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
