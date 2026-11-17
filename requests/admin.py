from django.contrib import admin, messages
from .models import Athlete, Request


class AthleteRequestInline(admin.TabularInline):
    model = Request
    fields = ("event", "status", "is_cancelled")
    extra = 0
    can_delete = False


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "level", "city")
    list_display_links = ("name",)
    list_editable = ("level",)
    search_fields = ("name", "city")
    list_filter = ("level", "city")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (AthleteRequestInline,)


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "athlete",
        "event",
        "event_city",
        "status",
        "is_cancelled",
    )
    list_display_links = ("id",)
    search_fields = ("athlete__name", "event__title")
    list_filter = ("is_cancelled", "status", "event__date")
    ordering = ("-id",)
    list_per_page = 20
    readonly_fields = ("id",)
    list_select_related = ("athlete", "event")
    autocomplete_fields = ("athlete", "event")
    actions = ("cancel_requests", "restore_requests")

    @admin.display(description="Город тренировки", ordering="event__city")
    def event_city(self, obj):
        return obj.event.city

    @admin.action(description="Отменить выбранные заявки")
    def cancel_requests(self, request, queryset):
        count = 0
        for req_obj in queryset:
            req_obj.cancel()
            count += 1
        self.message_user(
            request,
            f"Отменено заявок: {count}.",
            messages.SUCCESS,
        )

    @admin.action(description="Вернуть в активные")
    def restore_requests(self, request, queryset):
        updated = queryset.update(is_cancelled=False, status="active")
        self.message_user(
            request,
            f"Возвращено в активные: {updated}.",
            messages.SUCCESS,
        )
