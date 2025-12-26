# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Venue, RehearsalSlot
from rehearsals.forms import BookingForm
from for_authorization.models import MusicianUser

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def venue_list(request):
    venues = Venue.objects.all()
    return render(request, 'core/venue_list.html', {'venues': venues})

@login_required
def venue_detail(request, pk):
    try:
        venue = Venue.objects.get(pk=pk)
    except Venue.DoesNotExist:
        raise Http404("Площадка не найдена")
    
    available_slots = RehearsalSlot.objects.filter(venue=venue, is_booked=False)
    return render(request, 'core/venue_detail.html', {
        'venue': venue,
        'available_slots': available_slots
    })

@login_required
def book_rehearsal(request, slot_id):
    if request.user.is_viewer():
        messages.error(request, "Зрители не могут бронировать репетиции")
        return redirect('home')
    
    try:
        slot = RehearsalSlot.objects.get(id=slot_id, is_booked=False)
    except RehearsalSlot.DoesNotExist:
        raise Http404("Слот для репетиции не найден или уже забронирован")
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.slot = slot
            booking.save()
            
            slot.is_booked = True
            slot.save()
            
            messages.success(request, "Репетиция успешно забронирована!")
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()
    
    return render(request, 'core/book_rehearsal.html', {
        'form': form,
        'slot': slot
    })

@login_required
def booking_confirmation(request, booking_id):
    return render(request, 'core/booking_confirmation.html', {'booking_id': booking_id})