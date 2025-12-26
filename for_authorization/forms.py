from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
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

# Кастомная UserCreationForm для нашей модели
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем виджеты
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Имя пользователя'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтверждение пароля'})

# Форма 1: Зритель
class ViewerRegistrationForm(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email обязательным
        self.fields['email'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'viewer'
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user

# Форма 2: Музыкант/Менеджер
class MusicianRegistrationForm(CustomUserCreationForm):
    INSTRUMENT_CHOICES = [
        ('guitar', 'Гитара'),
        ('bass', 'Бас-гитара'),
        ('drums', 'Ударные'),
        ('keyboards', 'Клавишные'),
        ('piano', 'Фортепиано'),
        ('vocals', 'Вокал'),
        ('violin', 'Скрипка'),
        ('cello', 'Виолончель'),
        ('trumpet', 'Труба'),
        ('saxophone', 'Саксофон'),
        ('trombone', 'Тромбон'),
        ('flute', 'Флейта'),
        ('clarinet', 'Кларнет'),
        ('accordion', 'Аккордеон'),
        ('harp', 'Арфа'),
    ]
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    
    phone = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375XXXXXXXXX'})
    )
    
    instrument = forms.ChoiceField(
        required=True,
        choices=[('', 'Выберите инструмент')] + INSTRUMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_manager = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Я менеджер группы',
        initial=False
    )
    
    telegram = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email обязательным
        self.fields['email'].required = True
        # Обновляем метаданные для нашей модели
        self._meta.model = MusicianUser
        self._meta.fields = ('username', 'email', 'password1', 'password2', 
                            'first_name', 'last_name', 'phone', 'instrument', 
                            'telegram', 'is_manager')
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+375'):
            raise ValidationError('Телефон должен быть в формате +375XXXXXXXXX')
        if len(phone) != 13:  # +375 + 9 digits
            raise ValidationError('Телефон должен содержать 13 символов (формат: +375XXXXXXXXX)')
        return phone
    
    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram')
        if telegram and not telegram.startswith('@'):
            raise ValidationError('Telegram должен начинаться с @')
        return telegram
    
    def clean_instrument(self):
        instrument = self.cleaned_data.get('instrument')
        if not instrument:
            raise ValidationError('Пожалуйста, выберите инструмент')
        return instrument
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Определяем роль
        if self.cleaned_data.get('is_manager'):
            user.role = 'manager'
        else:
            user.role = 'musician'
            
        # Заполняем дополнительные поля
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.instrument = self.cleaned_data['instrument']
        user.telegram = self.cleaned_data.get('telegram', '')
        
        if commit:
            user.save()
        
        return user

# Форма 3: Владелец площадки
class VenueOwnerRegistrationForm(CustomUserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    
    phone = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375XXXXXXXXX'})
    )
    
    venue_name = forms.CharField(
        required=True,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название площадки'})
    )
    
    venue_address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Адрес площадки', 'rows': 3})
    )
    
    telegram = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем email обязательным
        self.fields['email'].required = True
        # Обновляем метаданные для нашей модели
        self._meta.model = MusicianUser
        self._meta.fields = ('username', 'email', 'password1', 'password2', 
                            'first_name', 'last_name', 'phone', 'telegram',
                            'venue_name', 'venue_address')
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+375'):
            raise ValidationError('Телефон должен быть в формате +375XXXXXXXXX')
        if len(phone) != 13:
            raise ValidationError('Телефон должен содержать 13 символов (формат: +375XXXXXXXXX)')
        return phone
    
    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram')
        if telegram and not telegram.startswith('@'):
            raise ValidationError('Telegram должен начинаться с @')
        return telegram
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'venue_owner'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.telegram = self.cleaned_data.get('telegram', '')
        user.venue_name = self.cleaned_data['venue_name']
        user.venue_address = self.cleaned_data['venue_address']
        
        if commit:
            user.save()
        
        return user

class MusicianUserUpdateForm(forms.ModelForm):
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'instrument', 'bio', 'telegram')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instrument': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telegram': forms.TextInput(attrs={'class': 'form-control'}),
        }