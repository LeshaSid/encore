from django import forms
from django.utils import timezone
from core.models import Rehearsal, Performance
from core.forms import MusicianForm, BandForm, ConcertForm, BandMembershipForm


class RehearsalForm(forms.ModelForm):
    class Meta:
        model = Rehearsal
        fields = ['band', 'rehearsal_date', 'duration_minutes', 'location']
        widgets = {
            'rehearsal_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'step': 15
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите место проведения'
            }),
            'band': forms.Select(attrs={'class': 'form-control'})
        }
    
    def clean_rehearsal_date(self):
        rehearsal_date = self.cleaned_data.get('rehearsal_date')
        if rehearsal_date and rehearsal_date < timezone.now():
            raise forms.ValidationError('Дата репетиции не может быть в прошлом')
        return rehearsal_date
    
    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration and duration < 15:
            raise forms.ValidationError('Минимальная продолжительность репетиции - 15 минут')
        if duration and duration > 480:
            raise forms.ValidationError('Максимальная продолжительность репетиции - 8 часов (480 минут)')
        return duration


class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ['concert', 'band', 'performance_order']
        widgets = {
            'concert': forms.Select(attrs={'class': 'form-control'}),
            'band': forms.Select(attrs={'class': 'form-control'}),
            'performance_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            })
        }
    
    def clean_performance_order(self):
        order = self.cleaned_data.get('performance_order')
        concert = self.cleaned_data.get('concert')
        band = self.cleaned_data.get('band')
        
        if concert and band and order:
            existing = Performance.objects.filter(
                concert=concert,
                performance_order=order
            )
            
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            else:
                existing = existing.exclude(band=band)
            
            if existing.exists():
                raise forms.ValidationError('Этот порядок уже занят другим выступлением на этом концерте')
        
        return order


__all__ = [
    'MusicianForm', 'BandForm', 'ConcertForm', 'BandMembershipForm',
    'RehearsalForm', 'PerformanceForm'
]