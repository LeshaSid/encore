# booking/forms.py
from .models import Rehearsals
from django.forms import ModelForm, TextInput, DateTimeInput, NumberInput


class RehearsalsForm(ModelForm):
    class Meta():
        model = Rehearsals
        fields = ["band_id", "rehearsal_date", "duration_minutes", "location"]  # Изменено

        widgets = {            
            "band_id": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter band name"
            }), 
            "rehearsal_date": DateTimeInput(attrs={
                "class": "form-control",
                "placeholder": "Enter date",
                "type": "datetime-local"
            }),
            "duration_minutes": NumberInput(attrs={  # Изменено
                "class": "form-control",
                "placeholder": "Enter duration in minutes"
            }),
            "location": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter location"
            })
        }