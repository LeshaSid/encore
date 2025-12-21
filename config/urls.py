from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from for_authorization.views import home, custom_login, custom_logout, RegisterView, ProfileView, ProfileUpdateView, change_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('custom_admin.urls')),
    path('book/', include('booking.urls')),
    path('concerts/', include('concertsshower.urls')),
    path('groups/', include('groups.urls', namespace='groups')),
    
    path('', home, name='home'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', change_password, name='change_password'),
    
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='core/registration/password_reset.html',
             email_template_name='core/registration/password_reset_email.html'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='core/registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='core/registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='core/registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]