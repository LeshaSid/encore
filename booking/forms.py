from core.models import Rehearsal, Band
from django import forms
from django.forms import ModelForm, TextInput, DateTimeInput, Select

class RehearsalsForm(ModelForm):
    class Meta:
        model = Rehearsal
        fields = ["band", "rehearsal_date", "duration_minutes", "location"]
        widgets = {
            "band": Select(attrs={
                "class": "form-control",
                "placeholder": "Выберите группу"
            }),
            "rehearsal_date": DateTimeInput(attrs={
                "class": "form-control",
                "placeholder": "Выберите дату и время",
                "type": "datetime-local"
            }),
            "duration_minutes": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Введите продолжительность в минутах",
                "min": 15
            }),
            "location": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите место проведения"
            })
        }