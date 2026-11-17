from django import forms
from events.models import Event
from .models import Athlete, Request


class RequestFilterForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.order_by("title"),
        required=False,
        label="Тренировка",
        empty_label="Все тренировки",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    athlete = forms.ModelChoiceField(
        queryset=Athlete.objects.order_by("name"),
        required=False,
        label="Спортсмен",
        empty_label="Все спортсмены",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировать по",
        choices=[
            ("id", "Номеру (ID)"),
            ("athlete", "Спортсмену"),
            ("event", "Тренировке"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["athlete", "event"]
        labels = {
            "athlete": "Спортсмен",
            "event": "Тренировка",
        }
        help_texts = {
            "athlete": "Выберите спортсмена, подающего заявку.",
            "event": "Выберите тренировку с подходящим уровнем и свободными местами.",
        }
        widgets = {
            "athlete": forms.Select(attrs={"class": "form-select"}),
            "event": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        athlete = cleaned_data.get("athlete")
        event = cleaned_data.get("event")

        if athlete and event:
            if not event.is_suitable_for(athlete.level):
                raise forms.ValidationError(
                    f"Уровень спортсмена ({athlete.level}) не подходит для тренировки "
                    f"(требуется {event.min_level}–{event.max_level})."
                )
        return cleaned_data
