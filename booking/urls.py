# booking/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.book, name='book'),  # Добавьте name='book'
]