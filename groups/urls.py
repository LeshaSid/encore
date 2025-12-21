from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    # CRUD для групп
    path('', views.band_list, name='band_list'),
    path('create/', views.band_create, name='band_create'),
    path('<int:pk>/edit/', views.band_update, name='band_update'),
    path('<int:pk>/delete/', views.band_delete, name='band_delete'),
    
    # Управление составом группы
    path('<int:pk>/members/', views.band_members, name='band_members'),
    path('<int:pk>/members/<int:member_id>/remove/', views.member_remove, name='member_remove'),
]