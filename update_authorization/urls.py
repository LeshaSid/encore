from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Авторизация
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Регистрация
    path('register/', views.register_choice, name='register_choice'),
    path('register/listener/', views.ListenerRegisterView.as_view(), name='register_listener'),
    path('register/musician/', views.MusicianRegisterView.as_view(), name='register_musician'),
    path('register/venue-owner/', views.VenueOwnerRegisterView.as_view(), name='register_venue_owner'),
    
    # Профиль
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Восстановление пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(
        form_class=views.CustomPasswordResetForm,
        template_name='core/registration/password_reset.html',
        email_template_name='core/registration/password_reset_email.html',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        form_class=views.CustomSetPasswordForm,
        template_name='core/registration/password_reset_confirm.html',
        success_url='/password-reset-complete/'
    ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
