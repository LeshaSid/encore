from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from core.models import Rehearsal, Band
from .forms import RehearsalsForm

def book(request):
    error = ""
    
    if request.method == "POST":
        form = RehearsalsForm(request.POST)
        if form.is_valid():
            try:
                rehearsal = form.save()
                messages.success(request, "Репетиция успешно забронирована!")
                return redirect('book')
            except Exception as e:
                error = f"Ошибка сохранения: {str(e)}"
                messages.error(request, error)
        else:
            error = "Форма заполнена некорректно"
            messages.error(request, error)
            
    form = RehearsalsForm()
    
    try:
        # Получаем все репетиции, сортируем по дате
        rehearsals = Rehearsal.objects.select_related('band').order_by('-rehearsal_date')
    except Exception as e:
        rehearsals = []
        error = f"Ошибка загрузки данных: {str(e)}"
        messages.error(request, error)
        
    data = {
        "form": form,
        "error": error,
        "rehearsals": rehearsals,
        "now": timezone.now()
    }
    return render(request, "booking/bookPage.html", data)