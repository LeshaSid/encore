from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from core.models import Rehearsal
from .forms import RehearsalsForm


def book(request):
    error = ""
    
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
                id = ''
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT band FROM rehearsals JOIN Bands ON rehearsals.band = Bands.band_id WHERE band_name = {form.cleaned_data['band']}")
                    id = cursor.fetchall()[0]
                newData = Rehearsal(band=id,
                                     rehearsal_date=form.cleaned_data['rehearsal_date'],
                                     duration_minutes=form.cleaned_data['duration_minutes'],
                                     location=form.cleaned_data['location'])
                newData.save()
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
        rehearsals = Rehearsal.objects.all()
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