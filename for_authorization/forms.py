from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import MusicianUser

class MusicianAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Имя пользователя'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Пароль'
    )


class MusicianUserCreationForm(forms.ModelForm):
   
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Минимум 8 символов'
    )
    
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
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
        if MusicianUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        
        return cleaned_data
    
    def save(self, commit=True):
        print("РЕГИСТРАЦИЯ: Создание пользователя через create_user")
        user = MusicianUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        
        user.is_active = True
        
        if commit:
            user.save()
        
        print(f"Пользователь создан: {user.username} (ID: {user.id})")
        print(f"Email: {user.email}")
        print(f"is_active: {user.is_active}")
        print(f"Проверка пароля: {user.check_password(self.cleaned_data['password1'])}")
        
        from django.contrib.auth import authenticate
        auth_user = authenticate(
            username=user.username,
            password=self.cleaned_data['password1']
        )
        print(f"Authenticate результат: {auth_user}")
        
        if auth_user:
            print("УСПЕХ: Пользователь может войти!")
        else:
            print("ОШИБКА: Authenticate не нашел пользователя")
        
        
        return user


class MusicianUserUpdateForm(forms.ModelForm):
    
    class Meta:
        model = MusicianUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'instrument')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instrument': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MusicianPasswordChangeForm(PasswordChangeForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'