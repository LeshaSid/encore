from django.urls import path
from . import views

app_name = 'concertsshower'

urlpatterns = [
    path('', views.upcoming_concerts, name='upcoming_concerts'),
    path('all/', views.all_concerts, name='all_concerts'),
    path('<int:concert_id>/', views.concert_detail, name='concert_detail'),
]