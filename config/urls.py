from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('book/', include('booking.urls')),
    path('concerts/', include('concertsshower.urls')),
    path('', RedirectView.as_view(url='/book/', permanent=True)),  # Главная страница
]