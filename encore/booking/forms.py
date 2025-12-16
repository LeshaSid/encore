from .models import Rehearsals, Bands, Concerts
from django.forms import ModelForm, TextInput, DateTimeInput


class RehearsalsForm(ModelForm):
    class Meta():
        model = Rehearsals
        fields = ["band_id", "rehearsal_date", "duration", "location"]

        widgets = {            
            "band_id": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter band id"
            }), 
            "rehearsal_date": DateTimeInput(attrs={
                "class": "form-control",
                "placeholder": "Enter date"
            }),
            "duration": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter duration"
            }),
            "location": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter location"
            })
        }