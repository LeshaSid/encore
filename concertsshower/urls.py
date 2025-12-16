from django.urls import path
from . import views

app_name = 'concertsshower'

urlpatterns = [
    path('upcoming/', views.upcoming_concerts, name='upcoming_concerts'),
    path('all/', views.all_concerts, name='all_concerts'),
    path('concert/<int:concert_id>/', views.concert_detail, name='concert_detail'),
]