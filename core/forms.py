from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Musician, Band, Concert, BandMembership


class MusicianForm(forms.ModelForm):
    class Meta:
        model = Musician
        fields = '__all__'
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+375'):
            raise ValidationError('Phone must start with +375')
        if len(phone) != 13:
            raise ValidationError('Phone must be 13 characters long')
        return phone
    
    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram')
        if telegram and not telegram.startswith('@'):
            raise ValidationError('Telegram username must start with @')
        return telegram


class BandForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = '__all__'
        widgets = {
            'founded_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_founded_date(self):
        founded_date = self.cleaned_data.get('founded_date')
        if founded_date > timezone.now().date():
            raise ValidationError('Founded date cannot be in the future')
        return founded_date


class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = '__all__'
        widgets = {
            'concert_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_concert_date(self):
        concert_date = self.cleaned_data.get('concert_date')
        if concert_date < timezone.now():
            raise ValidationError('Concert date cannot be in the past')
        return concert_date


class BandMembershipForm(forms.ModelForm):
    class Meta:
        model = BandMembership
        fields = '__all__'
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_join_date(self):
        join_date = self.cleaned_data.get('join_date')
        if join_date > timezone.now().date():
            raise ValidationError('Join date cannot be in the future')
        return join_date
