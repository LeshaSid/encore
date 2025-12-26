# concertsshower/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
import json
import os
from datetime import datetime

from .models import Concert, Performance, Band, Musician, BandMembership
from .forms import ConcertForm, ConcertApplicationForm
from .utils import (
    get_user_role, 
    get_user_musician, 
    get_user_bands, 
    get_user_primary_band,
    can_view_all_concerts,
    is_manager as utils_is_manager
)

APPLICATIONS_FILE = 'concert_applications.json'
EXTRA_CONCERTS_FILE = 'extra_concerts.json'


def load_applications():
    if not os.path.exists(APPLICATIONS_FILE):
        return []
    
    try:
        with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_applications(applications):
    with open(APPLICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(applications, f, ensure_ascii=False, indent=2)

def load_extra_concerts():
    if not os.path.exists(EXTRA_CONCERTS_FILE):
        return []
    
    try:
        with open(EXTRA_CONCERTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_extra_concerts(concerts):
    with open(EXTRA_CONCERTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(concerts, f, ensure_ascii=False, indent=2)

def get_application_by_id(application_id):
    applications = load_applications()
    for app in applications:
        if app.get('id') == application_id:
            return app
    return None

def get_user_applications(user):
    applications = load_applications()
    user_apps = []
    musician = get_user_musician(user)
    
    if musician:
        for app in applications:
            if app.get('musician_id') == musician.musician_id:
                user_apps.append(app)
    
    return user_apps

def create_application(concert_id, concert_source, band_id, musician_id, musician_name, message):
    """Создает новую заявку"""
    applications = load_applications()
    
    if applications:
        new_id = max(app.get('id', 0) for app in applications) + 1
    else:
        new_id = 1
    
    application = {
        'id': new_id,
        'concert_id': concert_id,
        'concert_source': concert_source,
        'band_id': band_id,
        'musician_id': musician_id,
        'musician_name': musician_name,
        'message': message,
        'status': 'pending',
        'response_message': '',
        'created_at': timezone.now().isoformat(),
        'updated_at': timezone.now().isoformat()
    }
    
    applications.append(application)
    save_applications(applications)
    return application

def update_application_status(application_id, new_status, response_message=''):
    """Обновляет статус заявки"""
    applications = load_applications()
    
    for app in applications:
        if app.get('id') == application_id:
            app['status'] = new_status
            app['response_message'] = response_message
            app['updated_at'] = timezone.now().isoformat()
            
            if new_status == 'approved' and app.get('concert_source') == 'db':
                try:
                    concert = Concert.objects.get(pk=app['concert_id'])
                    band = Band.objects.get(pk=app['band_id'])
                    
                    order = Performance.objects.filter(concert=concert).count() + 1
                    
                    Performance.objects.create(
                        band=band,
                        concert=concert,
                        performance_order=order
                    )
                except Exception as e:
                    print(f"Ошибка создания выступления: {e}")
            
            break
    
    save_applications(applications)


def upcoming_concerts(request):
    now = timezone.now()
    user_role = get_user_role(request.user) if request.user.is_authenticated else 'viewer'
    
    concerts = Concert.objects.filter(
        concert_date__gte=now
    ).order_by('concert_date')
    
    extra_concerts = []
    if user_role in ['organizer', 'musician']:
        extra_concerts = load_extra_concerts()
        extra_concerts = [
            c for c in extra_concerts 
            if datetime.fromisoformat(c['concert_date']) >= now
        ]
    
    context = {
        'concerts': concerts,
        'extra_concerts': extra_concerts,
        'now': now,
        'user_role': user_role,
    }
    return render(request, 'concertsshower/upcoming_concerts.html', context)

def all_concerts(request):
    now = timezone.now()
    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if not request.user.is_authenticated:
        messages.error(request, 'Необходимо войти в систему')
        return redirect('login')
    
    if not can_view_all_concerts(request.user):
        messages.error(request, 
            'У вас нет прав для просмотра всех концертов. '
            'Требуется статус персонала (менеджер) или профиль музыканта.'
        )
        return redirect('concertsshower:upcoming_concerts')
    
    user_role = get_user_role(request.user)
    
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
    
    concerts_data = []
    for concert in concerts_list:
        concerts_data.append({
            'id': concert.pk,
            'concert_title': concert.concert_title,
            'venue_address': concert.venue_address,
            'concert_date': concert.concert_date,
            'source': 'db'
        })
    
    if user_role in ['organizer', 'musician']:
        extra_concerts = load_extra_concerts()
        for concert in extra_concerts:
            concert_date = datetime.fromisoformat(concert['concert_date'])
            concerts_data.append({
                'id': concert.get('id', -len(concerts_data)),
                'concert_title': concert.get('concert_title', ''),
                'venue_address': concert.get('venue_address', ''),
                'concert_date': concert_date,
                'source': 'file',
                'organizer_name': concert.get('organizer_name', '')
            })
    
    paginator = Paginator(concerts_data, 9)
    page_number = request.GET.get('page')
    concerts_page = paginator.get_page(page_number)
    
    context = {
        'concerts': concerts_page,
        'now': now,
        'search_query': search_query,
        'from_date': from_date,
        'to_date': to_date,
        'user_role': user_role,
    }
    return render(request, 'concertsshower/all_concerts.html', context)

def concert_detail(request, pk):
    user_role = get_user_role(request.user) if request.user.is_authenticated else 'viewer'
    
    try:
        concert = Concert.objects.get(pk=pk)
        source = 'db'
        performances = concert.performances.all().select_related('band').order_by('performance_order')
        concert_dict = {
            'id': concert.pk,
            'concert_title': concert.concert_title,
            'venue_address': concert.venue_address,
            'concert_date': concert.concert_date,
            'source': 'db'
        }
    except Concert.DoesNotExist:
        extra_concerts = load_extra_concerts()
        concert_found = None
        for c in extra_concerts:
            if c.get('id') == pk:
                concert_found = c
                break
        
        if not concert_found:
            raise Http404("Концерт не найден")
        
        concert_dict = concert_found
        concert_dict['concert_date'] = datetime.fromisoformat(concert_dict['concert_date'])
        source = 'file'
        performances = []
        concert = None
    
    user_application = None
    if user_role in ['organizer', 'musician'] and request.user.is_authenticated:
        user_applications = get_user_applications(request.user)
        
        for app in user_applications:
            if app.get('concert_id') == pk and app.get('concert_source') == source:
                user_application = app
                break
    
    context = {
        'concert': concert_dict,
        'real_concert': concert,  # Для совместимости
        'performances': performances,
        'now': timezone.now(),
        'user_role': user_role,
        'user_application': user_application,
        'concert_source': source,
    }
    return render(request, 'concertsshower/concert_detail.html', context)

@login_required
def add_concert(request):
    user_role = get_user_role(request.user)
    
    if not utils_is_manager(request.user):
        messages.error(request, 'Только менеджеры (персонал) могут добавлять концерты')
        return redirect('concertsshower:upcoming_concerts')
    
    if request.method == 'POST':
        form = ConcertForm(request.POST)
        if form.is_valid():
            extra_concerts = load_extra_concerts()
            
            if extra_concerts:
                new_id = min([c.get('id', 0) for c in extra_concerts]) - 1
            else:
                new_id = -1
            
            concert_data = {
                'id': new_id,
                'concert_title': form.cleaned_data['concert_title'],
                'venue_address': form.cleaned_data['venue_address'],
                'concert_date': form.cleaned_data['concert_date'].isoformat(),
                'organizer_id': request.user.id,
                'organizer_name': request.user.username,
                'created_at': timezone.now().isoformat(),
                'updated_at': timezone.now().isoformat()
            }
            
            extra_concerts.append(concert_data)
            save_extra_concerts(extra_concerts)
            
            messages.success(request, f'Концерт "{form.cleaned_data["concert_title"]}" успешно создан!')
            return redirect('concertsshower:all_concerts')
    else:
        form = ConcertForm()
    
    context = {
        'form': form,
        'title': 'Добавление концерта',
        'user_role': user_role,
    }
    return render(request, 'concertsshower/concert_form.html', context)

@login_required
def edit_concert(request, pk):
    user_role = get_user_role(request.user)
    
    if not utils_is_manager(request.user):
        messages.error(request, 'Только менеджеры могут редактировать концерты')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    extra_concerts = load_extra_concerts()
    concert_to_edit = None
    for concert in extra_concerts:
        if concert.get('id') == pk:
            concert_to_edit = concert
            break
    
    if not concert_to_edit:
        messages.error(request, 'Можно редактировать только концерты, добавленные через систему')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    if request.method == 'POST':
        form = ConcertForm(request.POST)
        if form.is_valid():
            for concert in extra_concerts:
                if concert.get('id') == pk:
                    concert['concert_title'] = form.cleaned_data['concert_title']
                    concert['venue_address'] = form.cleaned_data['venue_address']
                    concert['concert_date'] = form.cleaned_data['concert_date'].isoformat()
                    concert['updated_at'] = timezone.now().isoformat()
                    break
            
            save_extra_concerts(extra_concerts)
            messages.success(request, f'Концерт "{form.cleaned_data["concert_title"]}" успешно обновлен!')
            return redirect('concertsshower:concert_detail', pk=pk)
    else:
        concert_date = datetime.fromisoformat(concert_to_edit['concert_date'])
        initial_data = {
            'concert_title': concert_to_edit['concert_title'],
            'venue_address': concert_to_edit['venue_address'],
            'concert_date': concert_date.strftime('%Y-%m-%dT%H:%M'),
        }
        form = ConcertForm(initial=initial_data)
    
    context = {
        'form': form,
        'concert': concert_to_edit,
        'title': 'Редактирование концерта',
        'user_role': user_role,
    }
    return render(request, 'concertsshower/concert_form.html', context)

@login_required
def delete_concert(request, pk):
    user_role = get_user_role(request.user)
    
    if not utils_is_manager(request.user):
        messages.error(request, 'Только менеджеры могут удалять концерты')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    try:
        concert = Concert.objects.get(pk=pk)
        messages.error(request, 'Нельзя удалить концерт из основной базы данных')
        return redirect('concertsshower:concert_detail', pk=pk)
    except Concert.DoesNotExist:
        extra_concerts = load_extra_concerts()
        updated_concerts = [c for c in extra_concerts if c.get('id') != pk]
        
        if len(updated_concerts) < len(extra_concerts):
            save_extra_concerts(updated_concerts)
            messages.success(request, 'Концерт успешно удален!')
            return redirect('concertsshower:all_concerts')
        else:
            messages.error(request, 'Концерт не найден')
            return redirect('concertsshower:all_concerts')

@login_required
def apply_for_concert(request, pk):
    user_role = get_user_role(request.user)
    
    if user_role != 'musician':
        messages.error(request, 'Только музыканты могут подавать заявки на концерты')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    musician = get_user_musician(request.user)
    if not musician:
        messages.error(request, 'Не удалось определить ваши данные как музыканта')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    user_bands = get_user_bands(request.user)
    if not user_bands:
        messages.error(request, 'Вы не состоите ни в одной группе')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    try:
        concert = Concert.objects.get(pk=pk)
        source = 'db'
        concert_date = concert.concert_date
        concert_title = concert.concert_title
    except Concert.DoesNotExist:
        extra_concerts = load_extra_concerts()
        concert_found = None
        for c in extra_concerts:
            if c.get('id') == pk:
                concert_found = c
                break
        
        if not concert_found:
            messages.error(request, 'Концерт не найден')
            return redirect('concertsshower:all_concerts')
        
        concert = concert_found
        source = 'file'
        concert_date = datetime.fromisoformat(concert['concert_date'])
        concert_title = concert['concert_title']
    
    if concert_date < timezone.now():
        messages.error(request, 'Нельзя подать заявку на прошедший концерт')
        return redirect('concertsshower:concert_detail', pk=pk)
    
    applications = load_applications()
    for app in applications:
        if (app.get('concert_id') == pk and 
            app.get('concert_source') == source and 
            app.get('musician_id') == musician.musician_id):
            messages.info(request, 'Вы уже подавали заявку на этот концерт')
            return redirect('concertsshower:concert_detail', pk=pk)
    
    if request.method == 'POST':
        form = ConcertApplicationForm(request.POST, user_bands=user_bands)
        if form.is_valid():
            band_id = int(form.cleaned_data['band'])
            message = form.cleaned_data['message']
            
            band_ids = [band.band_id for band in user_bands]
            if band_id not in band_ids:
                messages.error(request, 'Вы не можете подавать заявки от имени этой группы')
                return redirect('concertsshower:apply_for_concert', pk=pk)
            
            create_application(
                concert_id=pk,
                concert_source=source,
                band_id=band_id,
                musician_id=musician.musician_id,
                musician_name=f"{musician.first_name} {musician.last_name}",
                message=message
            )
            
            messages.success(request, 'Заявка успешно подана! Организатор рассмотрит её в ближайшее время.')
            return redirect('concertsshower:concert_detail', pk=pk)
    else:
        form = ConcertApplicationForm(user_bands=user_bands)
    
    context = {
        'form': form,
        'concert_title': concert_title,
        'concert_date': concert_date,
        'user_bands': user_bands,
        'user_role': user_role,
        'concert_source': source,
    }
    return render(request, 'concertsshower/apply_for_concert.html', context)

@login_required
def manage_applications(request):
    user_role = get_user_role(request.user)
    
    if not utils_is_manager(request.user):
        messages.error(request, 'Только менеджеры могут управлять заявками')
        return redirect('concertsshower:upcoming_concerts')
    
    applications = load_applications()
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = [app for app in applications if app.get('status') == status_filter]
    
    for app in applications:
        try:
            if app.get('concert_source') == 'db':
                concert = Concert.objects.get(pk=app['concert_id'])
                app['concert_title'] = concert.concert_title
                app['concert_date'] = concert.concert_date
            else:
                extra_concerts = load_extra_concerts()
                for c in extra_concerts:
                    if c.get('id') == app['concert_id']:
                        app['concert_title'] = c.get('concert_title', 'Неизвестно')
                        app['concert_date'] = datetime.fromisoformat(c.get('concert_date'))
                        break
            
            band = Band.objects.get(pk=app['band_id'])
            app['band_name'] = band.band_name
            
        except Exception as e:
            app['concert_title'] = 'Информация недоступна'
            app['concert_date'] = None
            app['band_name'] = 'Информация недоступна'
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'user_role': user_role,
    }
    return render(request, 'concertsshower/manage_applications.html', context)

@login_required
def update_application_status(request, application_id):
    user_role = get_user_role(request.user)
    
    if not utils_is_manager(request.user):
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        response_message = request.POST.get('response_message', '')
       
        valid_statuses = ['pending', 'approved', 'rejected', 'cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Неверный статус'}, status=400)
        
        update_application_status(application_id, new_status, response_message)
        
        return JsonResponse({'success': True, 'new_status': new_status})
    
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)

@login_required
def my_applications(request):
    user_role = get_user_role(request.user)
    
    if user_role != 'musician':
        messages.error(request, 'У вас нет доступа к этому разделу')
        return redirect('concertsshower:upcoming_concerts')
    
    applications = get_user_applications(request.user)
    
    for app in applications:
        try:
            if app.get('concert_source') == 'db':
                concert = Concert.objects.get(pk=app['concert_id'])
                app['concert_title'] = concert.concert_title
                app['concert_date'] = concert.concert_date
                app['venue_address'] = concert.venue_address
            else:
                extra_concerts = load_extra_concerts()
                for c in extra_concerts:
                    if c.get('id') == app['concert_id']:
                        app['concert_title'] = c.get('concert_title', 'Неизвестно')
                        app['concert_date'] = datetime.fromisoformat(c.get('concert_date'))
                        app['venue_address'] = c.get('venue_address', '')
                        break
            
            band = Band.objects.get(pk=app['band_id'])
            app['band_name'] = band.band_name
            
        except Exception as e:
            app['concert_title'] = 'Информация недоступна'
            app['concert_date'] = None
            app['venue_address'] = ''
            app['band_name'] = 'Информация недоступна'
    
    context = {
        'applications': applications,
        'user_role': user_role,
    }
    return render(request, 'concertsshower/my_applications.html', context)

@login_required
def cancel_application(request, application_id):
    user_role = get_user_role(request.user)
    
    if user_role != 'musician':
        messages.error(request, 'У вас нет прав для отмены заявок')
        return redirect('concertsshower:my_applications')
    
    application = get_application_by_id(application_id)
    if not application:
        messages.error(request, 'Заявка не найдена')
        return redirect('concertsshower:my_applications')
    
    musician = get_user_musician(request.user)
    if not musician or application.get('musician_id') != musician.musician_id:
        messages.error(request, 'Вы не можете отменить эту заявку')
        return redirect('concertsshower:my_applications')
    
    if application.get('status') not in ['pending', 'approved']:
        messages.error(request, 'Нельзя отменить заявку с текущим статусом')
        return redirect('concertsshower:my_applications')
    
    update_application_status(application_id, 'cancelled', 'Отменена пользователем')
    
    messages.success(request, 'Заявка успешно отменена')
    return redirect('concertsshower:my_applications')