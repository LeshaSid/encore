from core.models import Rehearsal
from django.forms import ModelForm, TextInput, DateTimeInput, NumberInput


class RehearsalsForm(ModelForm):
    class Meta():
        model = Rehearsal
        fields = ["band", "rehearsal_date", "duration_minutes", "location"]

        widgets = {            
            "band": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter band name"
            }), 
            "rehearsal_date": DateTimeInput(attrs={
                "class": "form-control",
                "placeholder": "Enter date",
                "type": "datetime-local"
            }),
            "duration_minutes": NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter duration in minutes"
            }),
            "location": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter location"
            })
        }