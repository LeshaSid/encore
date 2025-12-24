from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Concert, Performance, Band

def upcoming_concerts(request):
    now = timezone.now()
    concerts = Concert.objects.filter(concert_date__gte=now).order_by('concert_date')
    return render(request, 'concertsshower/upcoming_concerts.html', {
        'concerts': concerts,
        'now': now
    })

def all_concerts(request):
    concerts = Concert.objects.all().order_by('-concert_date')
    return render(request, 'concertsshower/all_concerts.html', {
        'concerts': concerts,
        'now': timezone.now()
    })

def concert_detail(request, concert_id):
    concert = get_object_or_404(Concert, pk=concert_id)
    performances = Performance.objects.filter(concert=concert).order_by('performance_order')
    return render(request, 'concertsshower/concert_detail.html', {
        'concert': concert,
        'performances': performances,
        'now': timezone.now()
    })