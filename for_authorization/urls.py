from django.urls import path
from . import views
from .views import ProfileView, ProfileUpdateView, change_password

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', change_password, name='change_password'),
]