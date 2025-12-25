from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from django.contrib.auth import password_validation
from .models import MusicianUser

class MusicianAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя или Email'}),
        label='Имя пользователя или Email'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
        label='Пароль'
    )

# ============ ФОРМА ДЛЯ ЗРИТЕЛЯ ============
class ListenerRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя *',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'})
    )
    
    email = forms.EmailField(
        required=True,
        label='Email *',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'}),
        validators=[validate_email]
    )
    
    password1 = forms.CharField(
        label='Пароль *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Минимум 8 символов'}),
        min_length=8,
        help_text='Минимум 8 символов'
    )
    
    password2 = forms.CharField(
        label='Подтверждение пароля *',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )
    
    class Meta:
        model = MusicianUser
        fields = ('username', 'email')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if MusicianUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Введите корректный email адрес')
        
        if MusicianUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        
        if password1:
            password_validation.validate_password(password1, self.instance)
        
        return cleaned_data
    
    def save(self, commit=True):
        user = MusicianUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            user_type='listener'
        )
        user.is_active = True
        if commit:
            user.save()
        return user


# ============ ФОРМА ДЛЯ МУЗЫКАНТА/МЕНЕДЖЕРА ============
class MusicianRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        required=True,
        label='Email *',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        validators=[validate_email]
    )
    
    password1 = forms.CharField(
        label='Пароль *',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text='Минимум 8 символов'
    )
    
    password2 = forms.CharField(
        label='Подтверждение пароля *',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        required=True,
        label='Имя *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        required=True,
        label='Фамилия *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        required=True,
        label='Телефон *',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375292223344'}),
        validators=[RegexValidator(
            regex=r'^\+375(17|25|29|33|44)\d{7}$',
            message="Формат: '+375292223344' (белорусский номер)"
        )]
    )
    
    instrument = forms.ChoiceField(
        required=True,
        label='Инструмент *',
        choices=MusicianUser.INSTRUMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    telegram = forms.CharField(
        required=False,
        label='Telegram (необязательно)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
        validators=[RegexValidator(
            regex=r'^@[A-Za-z0-9_]{5,32}$',
            message="Формат: @username (только латинские буквы, цифры и _)"
        )]
    )
    
    is_group_manager = forms.BooleanField(
        required=False,
        label='Я менеджер группы',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'instrument', 'telegram')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if MusicianUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MusicianUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        
        if password1:
            password_validation.validate_password(password1, self.instance)
        
        return cleaned_data
    
    def save(self, commit=True):
        user_type = 'manager' if self.cleaned_data.get('is_group_manager') else 'musician'
        
        user = MusicianUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            user_type=user_type,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data['phone'],
            instrument=self.cleaned_data['instrument'],
            telegram=self.cleaned_data.get('telegram') or None,
            is_group_manager=self.cleaned_data.get('is_group_manager', False)
        )
        user.is_active = True

        if commit:
            user.save()
        return user

# ============ ФОРМА ДЛЯ ВЛАДЕЛЬЦА ПЛОЩАДКИ ============
class VenueOwnerRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        required=True,
        label='Email *',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        validators=[validate_email]
    )
    
    password1 = forms.CharField(
        label='Пароль *',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text='Минимум 8 символов'
    )
    
    password2 = forms.CharField(
        label='Подтверждение пароля *',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        required=True,
        label='Имя *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        required=True,
        label='Фамилия *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        required=True,
        label='Телефон *',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375292223344'}),
        validators=[RegexValidator(
            regex=r'^\+375(17|25|29|33|44)\d{7}$',
            message="Формат: '+375292223344' (белорусский номер)"
        )]
    )
    
    venue_name = forms.CharField(
        required=True,
        label='Название площадки *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    venue_address = forms.CharField(
        required=True,
        label='Адрес площадки *',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    telegram = forms.CharField(
        required=False,
        label='Telegram (необязательно)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
        validators=[RegexValidator(
            regex=r'^@[A-Za-z0-9_]{5,32}$',
            message="Формат: @username (только латинские буквы, цифры и _)"
        )]
    )
    
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'venue_name', 'venue_address', 'telegram')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if MusicianUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MusicianUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        
        if password1:
            password_validation.validate_password(password1, self.instance)
        
        return cleaned_data
    
    def save(self, commit=True):
        user = MusicianUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            user_type='venue_owner',
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone=self.cleaned_data['phone'],
            venue_name=self.cleaned_data['venue_name'],
            venue_address=self.cleaned_data['venue_address'],
            telegram=self.cleaned_data.get('telegram') or None
        )
        user.is_active = True
        if commit:
            user.save()
        return user


# ============ ВОССТАНОВЛЕНИЕ ПАРОЛЯ ============
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'}),
        label='Email',
        validators=[validate_email]
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Новый пароль'}),
        label='Новый пароль',
        min_length=8,
        help_text=password_validation.password_validators_help_text_html()
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}),
        label='Подтверждение пароля'
    )

# ============ ОБНОВЛЕНИЕ ПРОФИЛЯ ============
class MusicianUserUpdateForm(forms.ModelForm):
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'instrument', 
                 'telegram', 'bio', 'venue_name', 'venue_address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instrument': forms.Select(attrs={'class': 'form-control'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'venue_name': forms.TextInput(attrs={'class': 'form-control'}),
            'venue_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
