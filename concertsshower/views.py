from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from core.models import Concert, Performance, Band


def upcoming_concerts(request):
    now = timezone.now()
    
    # Получаем концерты начиная с текущего времени
    concerts = Concert.objects.filter(
        concert_date__gte=now
    ).order_by('concert_date')[:10]
    
    concerts_with_bands = []
    for concert in concerts:
        performances = Performance.objects.filter(concert=concert).select_related('band')
        bands = [performance.band for performance in performances]
        concerts_with_bands.append({
            'concert': concert,
            'bands': bands,
            'performance_count': len(bands)
        })
    
    context = {
        'concerts_with_bands': concerts_with_bands,
        'current_time': now,
        'now': now,
    }
    
    return render(request, 'concertsshower/upcoming_concerts.html', context)


def concert_detail(request, concert_id):
    now = timezone.now()
    concert = get_object_or_404(Concert, concert_id=concert_id)
    performances = Performance.objects.filter(
        concert=concert
    ).select_related('band').order_by('performance_order')
    
    context = {
        'concert': concert,
        'performances': performances,
        'now': now,
    }
    
    return render(request, 'concertsshower/concert_detail.html', context)


def all_concerts(request):
    now = timezone.now()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    search_query = request.GET.get('search', '')
    
    concerts = Concert.objects.all()
    
    # Применяем фильтры
    if from_date:
        concerts = concerts.filter(concert_date__gte=from_date)
    if to_date:
        concerts = concerts.filter(concert_date__lte=to_date)
    if search_query:
        concerts = concerts.filter(
            Q(concert_title__icontains=search_query) |
            Q(venue_address__icontains=search_query)
        )
    
    concerts = concerts.order_by('concert_date')
    
    context = {
        'concerts': concerts,
        'search_query': search_query,
        'now': now,
        'request': request,  # Добавляем request в контекст
    }
    
    return render(request, 'concertsshower/all_concerts.html', context)