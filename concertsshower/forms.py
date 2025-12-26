from django import forms
from django.utils import timezone

class ConcertForm(forms.Form):
    concert_title = forms.CharField(
        max_length=200,
        label='Название концерта',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название концерта'
        })
    )
    
    venue_address = forms.CharField(
        max_length=255,
        label='Адрес проведения',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес'
        })
    )
    
    concert_date = forms.DateTimeField(
        label='Дата и время',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    
    def clean_concert_date(self):
        date = self.cleaned_data['concert_date']
        if date and date < timezone.now():
            raise forms.ValidationError("Дата концерта не может быть в прошлом")
        return date

class ConcertApplicationForm(forms.Form):
    band = forms.ChoiceField(
        label='Выберите группу',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    message = forms.CharField(
        label='Сообщение для организатора',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Расскажите о вашей группе, репертуаре и почему вы хотите выступить на этом концерте...'
        }),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        user_bands = kwargs.pop('user_bands', [])
        super(ConcertApplicationForm, self).__init__(*args, **kwargs)
        
        band_choices = [(band.band_id, band.band_name) for band in user_bands]
        if not band_choices:
            self.fields['band'].widget.attrs['disabled'] = True
            self.fields['band'].help_text = 'Вы не состоите ни в одной группе'
        
        self.fields['band'].choices = band_choices