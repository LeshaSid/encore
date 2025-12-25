from django.urls import path
from . import views

app_name = 'concertsshower'

urlpatterns = [
    # Список всех концертов
    path('', views.all_concerts, name='all_concerts'),
    
    # Предстоящие концерты
    path('upcoming/', views.upcoming_concerts, name='upcoming_concerts'),
    
    # Детальная страница (используем pk, чтобы соответствовать функции в views.py)
    path('<int:pk>/', views.concert_detail, name='concert_detail'),
]