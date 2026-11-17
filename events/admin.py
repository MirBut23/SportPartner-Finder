from django.contrib import admin
from django.db.models import Count, Q
from requests.models import Request
from .models import Event, Sport


class RequestInline(admin.TabularInline):
    model = Request
    fields = ("athlete", "status", "is_cancelled")
    extra = 0
    can_delete = False


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("id",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "sport",
        "city",
        "date",
        "capacity",
        "active_requests_count",
    )
    list_display_links = ("title",)
    list_editable = ("capacity",)
    list_filter = ("sport", "city", "date")
    search_fields = ("title", "city", "location", "sport__name")
    ordering = ("date", "id")
    list_per_page = 20
    readonly_fields = ("id",)
    date_hierarchy = "date"
    list_select_related = ("sport",)
    inlines = (RequestInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            active_requests=Count(
                "requests",
                filter=Q(requests__is_cancelled=False),
            )
        )

    @admin.display(description="Активных заявок", ordering="active_requests")
    def active_requests_count(self, obj):
        return obj.active_requests
