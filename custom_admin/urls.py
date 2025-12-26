from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),

    path('musicians/', views.musician_list, name='musician_list'),
    path('musicians/create/', views.musician_create, name='musician_create'),
    path('musicians/<int:pk>/edit/', views.musician_update, name='musician_update'),
    path('musicians/<int:pk>/delete/', views.musician_delete, name='musician_delete'),

    path('bands/', views.band_list, name='band_list'),
    path('bands/create/', views.band_create, name='band_create'),
    path('bands/<int:pk>/edit/', views.band_update, name='band_update'),
    path('bands/<int:pk>/delete/', views.band_delete, name='band_delete'),

    path('concerts/', views.concert_list, name='concert_list'),
    path('concerts/create/', views.concert_create, name='concert_create'),
    path('concerts/<int:pk>/edit/', views.concert_update, name='concert_update'),
    path('concerts/<int:pk>/delete/', views.concert_delete, name='concert_delete'),

    path('rehearsals/', views.rehearsal_list, name='rehearsal_list'),
    path('rehearsals/create/', views.rehearsal_create, name='rehearsal_create'),
    path('rehearsals/<int:pk>/edit/', views.rehearsal_update, name='rehearsal_update'),
    path('rehearsals/<int:pk>/delete/', views.rehearsal_delete, name='rehearsal_delete'),

    path('memberships/', views.membership_list, name='membership_list'),
    path('memberships/create/', views.membership_create, name='membership_create'),
    path('memberships/<int:pk>/edit/', views.membership_update, name='membership_update'),
    path('memberships/<int:pk>/delete/', views.membership_delete, name='membership_delete'),

    path('performances/', views.performance_list, name='performance_list'),
    path('performances/create/', views.performance_create, name='performance_create'),
    path('performances/<int:pk>/edit/', views.performance_update, name='performance_update'),
    path('performances/<int:pk>/delete/', views.performance_delete, name='performance_delete'),
]