from django.urls import path
from . import views

app_name = 'concertsshower'

urlpatterns = [
    path('', views.all_concerts, name='all_concerts'),
    
    path('upcoming/', views.upcoming_concerts, name='upcoming_concerts'),
    
    path('<int:pk>/', views.concert_detail, name='concert_detail'),
]