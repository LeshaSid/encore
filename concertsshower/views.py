from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Concert, Performance

def upcoming_concerts(request):
    """Отображение только предстоящих концертов"""
    # Используем timezone.now() для корректного учета времени сервера
    now = timezone.now()
    
    # Фильтруем концерты: дата больше или равна текущей
    concerts = Concert.objects.filter(
        concert_date__gte=now
    ).order_by('concert_date')
    
    context = {
        'concerts': concerts,
        'now': now,
    }
    return render(request, 'concertsshower/upcoming_concerts.html', context)

def all_concerts(request):
    """Архив всех концертов с фильтрацией и поиском"""
    now = timezone.now()
    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    concerts_list = Concert.objects.all().order_by('-concert_date')
    
    if search_query:
        concerts_list = concerts_list.filter(
            Q(concert_title__icontains=search_query) | 
            Q(venue_address__icontains=search_query)
        )
    
    if from_date:
        concerts_list = concerts_list.filter(concert_date__date__gte=from_date)
    
    if to_date:
        concerts_list = concerts_list.filter(concert_date__date__lte=to_date)
        
    paginator = Paginator(concerts_list, 9)
    page_number = request.GET.get('page')
    concerts = paginator.get_page(page_number)
    
    context = {
        'concerts': concerts,
        'now': now,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, 'concertsshower/all_concerts.html', context)

def concert_detail(request, pk):
    """Детальная информация о концерте (исправлен аргумент pk)"""
    concert = get_object_or_404(Concert, pk=pk)
    # Предзагрузка групп для оптимизации запросов
    performances = concert.performances.all().select_related('band').order_by('performance_order')
    
    context = {
        'concert': concert,
        'performances': performances,
        'now': timezone.now(),
    }
    return render(request, 'concertsshower/concert_detail.html', context)