from django import forms
from django.utils import timezone
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "sport",
            "city",
            "location",
            "date",
            "min_level",
            "max_level",
            "capacity",
            "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "sport": forms.Select(attrs={"class": "form-select"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "min_level": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "max_level": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_date(self):
        event_date = self.cleaned_data["date"]
        if event_date < timezone.localdate():
            raise forms.ValidationError("Нельзя создать тренировку на прошедшую дату.")
        return event_date

    def clean(self):
        cleaned_data = super().clean()
        min_lvl = cleaned_data.get("min_level")
        max_lvl = cleaned_data.get("max_level")
        if min_lvl and max_lvl and min_lvl > max_lvl:
            raise forms.ValidationError("Минимальный уровень не может быть больше максимального.")
        return cleaned_data
