from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from core.models import Rehearsal, Band
from .forms import RehearsalsForm


def book(request):
    error = ""
    
    # Проверка структуры таблицы (для отладки)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'rehearsals'")
            columns = [row[0] for row in cursor.fetchall()]
            print("Columns in rehearsals table:", columns)
    except Exception as e:
        print(f"Error checking table structure: {e}")
    
    if request.method == "POST":
        form = RehearsalsForm(request.POST)
        if form.is_valid():
            try:
                # Сохраняем репетицию - band уже является объектом Band
                new_rehearsal = form.save()
                messages.success(request, "Репетиция успешно забронирована!")
                return redirect('book')
            except Exception as e:
                error = f"Ошибка сохранения: {str(e)}"
                messages.error(request, error)
        else:
            error = "Форма заполнена некорректно"
            messages.error(request, error)
    else:
        form = RehearsalsForm()

    # Загружаем репетиции с информацией о группах
    try:
        rehearsals = Rehearsal.objects.select_related('band').all()
    except Exception as e:
        rehearsals = []
        error = f"Ошибка загрузки данных: {str(e)}"
        messages.error(request, error)

    data = {
        "form": form,
        "error": error,
        "rehearsals": rehearsals
    }

    return render(request, "booking/bookPage.html", data)