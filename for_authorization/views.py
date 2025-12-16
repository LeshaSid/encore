from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import MusicianUser
from .forms import MusicianUserCreationForm, MusicianUserUpdateForm

def home(request):
    return render(request, 'core/home.html')


#def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"DEBUG Вход: username={username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            print("DEBUG: Аутентификация не удалась")
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'core/registration/login.html')


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')


class RegisterView(CreateView):
    form_class = MusicianUserCreationForm
    template_name = 'core/registration/register.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        print("REGISTER VIEW: Начало регистрации")

        self.object = form.save()
        
        login(self.request, self.object)

        messages.success(self.request, f'Регистрация прошла успешно! Добро пожаловать, {self.object.username}!')
        
        print(f"REGISTER VIEW: Регистрация завершена для {self.object.username}")
        
        return redirect(self.get_success_url())


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
    
    return render(request, 'core/registration/password_change.html', {
        'form': form
    })