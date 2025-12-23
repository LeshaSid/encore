from django.shortcuts import render
from django.utils import timezone
from django.db.models import Prefetch
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Concert, Performance, Band

def upcoming_concerts(request):
    now = timezone.now()
    
   
    concerts = Concert.objects.filter(
        concert_date__gte=now
    ).order_by('concert_date')
    
   
    page = request.GET.get('page', 1)
    paginator = Paginator(concerts, 10)  
    
    try:
        paginated_concerts = paginator.page(page)
    except PageNotAnInteger:
        paginated_concerts = paginator.page(1)
    except EmptyPage:
        paginated_concerts = paginator.page(paginator.num_pages)
    
    
    concerts_with_bands = []
    for concert in paginated_concerts:
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
        'paginated_concerts': paginated_concerts,  
    }
    
    return render(request, 'concertsshower/upcoming_concerts.html', context)


def concert_detail(request, concert_id):
    try:
        concert = Concert.objects.get(concert_id=concert_id)
        performances = Performance.objects.filter(
            concert=concert
        ).select_related('band').order_by('performance_order')
        
        context = {
            'concert': concert,
            'performances': performances,
        }
        
        return render(request, 'concertsshower/concert_detail.html', context)
    except Concert.DoesNotExist:
        return render(request, 'concertsshower/concert_not_found.html', status=404)


def all_concerts(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    search_query = request.GET.get('search', '')
    
    concerts = Concert.objects.all()
    
    if from_date:
        concerts = concerts.filter(concert_date__gte=from_date)
    if to_date:
        concerts = concerts.filter(concert_date__lte=to_date)
    if search_query:
        concerts = concerts.filter(concert_title__icontains=search_query)
    
    concerts = concerts.order_by('concert_date')
    
    
    page = request.GET.get('page', 1)
    paginator = Paginator(concerts, 15) 
    
    try:
        paginated_concerts = paginator.page(page)
    except PageNotAnInteger:
        paginated_concerts = paginator.page(1)
    except EmptyPage:
        paginated_concerts = paginator.page(paginator.num_pages)
    
    context = {
        'concerts': paginated_concerts,  
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'concertsshower/all_concerts.html', context)