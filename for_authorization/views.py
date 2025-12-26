from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import MusicianUser
from .forms import (
    MusicianAuthenticationForm, 
    MusicianUserUpdateForm,
    ViewerRegistrationForm,
    MusicianRegistrationForm,
    VenueOwnerRegistrationForm
)

def home(request):
    return render(request, 'core/home.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = MusicianAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Ошибка в форме входа.')
    else:
        form = MusicianAuthenticationForm()
    
    return render(request, 'core/registration/login.html', {'form': form})

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')

def register_view(request):
    """Простое функциональное представление для регистрации"""
    if request.user.is_authenticated:
        return redirect('home')
    
    form_type = request.GET.get('type', 'viewer')
    form = None
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type', form_type)
        
        if form_type == 'musician' or form_type == 'manager':
            form = MusicianRegistrationForm(request.POST)
            if form_type == 'manager':
                # Для менеджера устанавливаем чекбокс
                form.data = form.data.copy()
                form.data['is_manager'] = 'on'
        elif form_type == 'venue_owner':
            form = VenueOwnerRegistrationForm(request.POST)
        else:
            form = ViewerRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Автоматически логиним пользователя
            login(request, user)
            
            # Сообщение об успешной регистрации
            role_display = dict(MusicianUser.ROLE_CHOICES).get(user.role, user.role)
            messages.success(request, f'Регистрация прошла успешно! Вы зарегистрированы как {role_display}.')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            # Для отладки
            print("Form errors:", form.errors)
    else:
        if form_type == 'musician':
            form = MusicianRegistrationForm()
        elif form_type == 'manager':
            form = MusicianRegistrationForm()
        elif form_type == 'venue_owner':
            form = VenueOwnerRegistrationForm()
        else:
            form = ViewerRegistrationForm()
    
    return render(request, 'core/registration/register.html', {
        'form': form,
        'form_type': form_type,
        'role_choices': MusicianUser.ROLE_CHOICES,
        'show_manager_checkbox': form_type == 'manager'
    })

# Альтернатива: классное представление (более простое)
class RegisterView(CreateView):
    model = MusicianUser
    template_name = 'core/registration/register.html'
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        # Используем функциональное представление для простоты
        return register_view(request)

class ProfileView(LoginRequiredMixin, DetailView):
    model = MusicianUser
    template_name = 'core/profile/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = MusicianUser
    form_class = MusicianUserUpdateForm
    template_name = 'core/profile/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/profile/password_change.html', {'form': form})