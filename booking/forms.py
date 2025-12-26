from core.models import Rehearsal, Band
from django.forms import ModelForm, TextInput, DateTimeInput, NumberInput, Select


class RehearsalsForm(ModelForm):
    class Meta():
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
            "duration_minutes": NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Введите длительность в минутах"
            }),
            "location": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите место проведения"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super(RehearsalsForm, self).__init__(*args, **kwargs)
        # Заменяем поле выбора группы на queryset с названиями групп
        self.fields['band'].queryset = Band.objects.all()
        self.fields['band'].label_from_instance = lambda obj: obj.band_name