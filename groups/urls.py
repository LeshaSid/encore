from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.BandListView.as_view(), name='band_list'),
    path('create/', views.BandCreateView.as_view(), name='band_create'),
    path('<int:pk>/edit/', views.BandUpdateView.as_view(), name='band_update'),
    path('<int:pk>/delete/', views.BandDeleteView.as_view(), name='band_delete'),
    
    path('<int:pk>/members/', views.band_members, name='band_members'),
    path('<int:pk>/members/<int:member_id>/remove/', views.member_remove, name='member_remove'),
]