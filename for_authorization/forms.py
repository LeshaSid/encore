# for_authorization/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import MusicianUser

class MusicianAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        label='Имя пользователя'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
        label='Пароль'
    )

class MusicianUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'})
    )
    
    instrument = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Инструмент'})
    )
    
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'password1', 'password2', 'phone', 'instrument')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.instrument = self.cleaned_data.get('instrument', '')
        
        if commit:
            user.save()
        
        return user

class MusicianUserUpdateForm(forms.ModelForm):
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'instrument', 'bio')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instrument': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }