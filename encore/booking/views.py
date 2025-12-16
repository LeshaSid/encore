from django.shortcuts import render, redirect
from .models import Rehearsals
from .forms import RehearsalsForm


def book(request):
    error = ""
    if request.method == "POST":
        form = RehearsalsForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            
            form.save()
        else:
            error = "Incorrect form"
        return redirect('/book')


    form = RehearsalsForm()

    rehearsals = Rehearsals.objects.all()

    data = {
        "form": form,
        "error": error,
        "rehearsals": rehearsals
    }


    return render(request, "booking/bookPage.html", data)