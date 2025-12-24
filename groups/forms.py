from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import Band, BandMembership, Musician


class BandForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = ['band_name', 'genre', 'founded_date']
        widgets = {
            'band_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название группы'
            }),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'founded_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'band_name': 'Название группы',
            'genre': 'Жанр',
            'founded_date': 'Дата основания',
        }
    
    def clean_founded_date(self):
        founded_date = self.cleaned_data.get('founded_date')
        if founded_date and founded_date > timezone.now().date():
            raise ValidationError('Дата основания не может быть в будущем')
        return founded_date
    
    def clean_band_name(self):
        band_name = self.cleaned_data.get('band_name')
        if band_name and len(band_name.strip()) < 2:
            raise ValidationError('Название группы должно содержать минимум 2 символа')
        return band_name.strip()


class AddMemberForm(forms.ModelForm):
    musician = forms.ModelChoiceField(
        queryset=Musician.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Музыкант'
    )
    join_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Дата вступления',
        initial=timezone.now().date()
    )
    
    class Meta:
        model = BandMembership
        fields = ['musician', 'join_date']
    
    def __init__(self, *args, **kwargs):
        self.band = kwargs.pop('band', None)
        super().__init__(*args, **kwargs)
        if self.band:
            existing_members = self.band.bandmembership_set.values_list('musician_id', flat=True)
            self.fields['musician'].queryset = Musician.objects.exclude(
                musician_id__in=existing_members
            )
    
    def clean(self):
        cleaned_data = super().clean()
        musician = cleaned_data.get('musician')
        join_date = cleaned_data.get('join_date')
        
        if musician and self.band:
            if BandMembership.objects.filter(band=self.band, musician=musician).exists():
                raise ValidationError('Этот музыкант уже состоит в группе')
        
        if join_date and join_date > timezone.now().date():
            raise ValidationError('Дата вступления не может быть в будущем')
        
        return cleaned_data