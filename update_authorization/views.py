from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeForm

from .models import MusicianUser
from .forms import (
    MusicianAuthenticationForm,
    ListenerRegistrationForm,
    MusicianRegistrationForm,
    VenueOwnerRegistrationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    MusicianUserUpdateForm
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

def register_choice(request):
    """Страница выбора типа регистрации"""
    return render(request, 'core/registration/register_choice.html')

class ListenerRegisterView(CreateView):
    form_class = ListenerRegistrationForm
    template_name = 'core/registration/register_listener.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Регистрация зрителя прошла успешно! Теперь вы можете войти.')
        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class MusicianRegisterView(CreateView):
    form_class = MusicianRegistrationForm
    template_name = 'core/registration/register_musician.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        user_type = "менеджера группы" if user.is_group_manager else "музыканта"
        messages.success(self.request, f'Регистрация {user_type} прошла успешно! Теперь вы можете войти.')
        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class VenueOwnerRegisterView(CreateView):
    form_class = VenueOwnerRegistrationForm
    template_name = 'core/registration/register_venue_owner.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Регистрация владельца площадки прошла успешно! Теперь вы можете войти.')
        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

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
