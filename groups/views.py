# groups/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from core.models import Band, BandMembership, Musician
from for_authorization.models import MusicianUser
from .forms import BandForm, AddMemberForm

def get_current_musician(user):
    """Получить объект Musician, связанный с пользователем"""
    if not user.is_authenticated or not user.phone:
        return None
    try:
        return Musician.objects.get(phone=user.phone)
    except Musician.DoesNotExist:
        return None

class BandListView(LoginRequiredMixin, ListView):
    model = Band
    template_name = 'groups/band_list.html'
    context_object_name = 'bands'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_viewer():
            messages.error(request, "У вас нет прав для просмотра списка групп.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().order_by('band_name')
        user = self.request.user
        
        if user.is_musician():
            musician = get_current_musician(user)
            if musician:
                queryset = queryset.filter(bandmembership__musician=musician)
            else:
                queryset = queryset.none()
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(band_name__icontains=search_query) |
                Q(genre__icontains=search_query)
            )
        
        genre_filter = self.request.GET.get('genre', '')
        if genre_filter:
            queryset = queryset.filter(genre=genre_filter)
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['genre_filter'] = self.request.GET.get('genre', '')
        context['genres'] = Band.objects.values_list('genre', flat=True).distinct().order_by('genre')
        
        user = self.request.user
        if user.is_musician():
            musician = get_current_musician(user)
            if musician:
                context['total_bands'] = Band.objects.filter(bandmembership__musician=musician).count()
                context['total_genres'] = Band.objects.filter(bandmembership__musician=musician).values('genre').distinct().count()
                context['total_musicians'] = Musician.objects.filter(bandmembership__band__in=Band.objects.filter(bandmembership__musician=musician)).distinct().count()
            else:
                context['total_bands'] = 0
                context['total_genres'] = 0
                context['total_musicians'] = 0
        else:  # manager, venue_owner
            context['total_bands'] = Band.objects.count()
            context['total_genres'] = Band.objects.values('genre').distinct().count()
            context['total_musicians'] = Musician.objects.count()
        
        return context

class BandCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Band
    form_class = BandForm
    template_name = 'groups/band_form.html'
    success_url = reverse_lazy('groups:band_list')

    def test_func(self):
        return self.request.user.can_manage_bands()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание новой группы'
        context['submit_text'] = 'Создать группу'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Группа "{form.instance.band_name}" успешно создана!')
        return super().form_valid(form)

class BandUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Band
    form_class = BandForm
    template_name = 'groups/band_form.html'
    success_url = reverse_lazy('groups:band_list')

    def test_func(self):
        if not self.request.user.can_manage_bands():
            return False
        
        band = self.get_object()
        
        # Проверяем, является ли пользователь менеджером этой группы
        if self.request.user.is_manager():
            musician = get_current_musician(self.request.user)
            if not musician:
                return False
            return BandMembership.objects.filter(band=band, musician=musician).exists()
        
        # Владельцы площадок могут редактировать все группы
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование группы: {self.object.band_name}'
        context['submit_text'] = 'Сохранить изменения'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Группа "{form.instance.band_name}" успешно обновлена!')
        return super().form_valid(form)

class BandDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Band
    template_name = 'groups/band_confirm_delete.html'
    success_url = reverse_lazy('groups:band_list')

    def test_func(self):
        if not self.request.user.can_manage_bands():
            return False
        
        band = self.get_object()
        
        if self.request.user.is_manager():
            musician = get_current_musician(self.request.user)
            if not musician:
                return False
            return BandMembership.objects.filter(band=band, musician=musician).exists()
        
        return True

    def delete(self, request, *args, **kwargs):
        band_name = self.get_object().band_name
        messages.success(request, f'Группа "{band_name}" успешно удалена!')
        return super().delete(request, *args, **kwargs)

@login_required
def band_members(request, pk):
    band = get_object_or_404(Band, pk=pk)
    user = request.user
    
    if user.is_viewer():
        messages.error(request, "У вас нет прав для просмотра состава группы.")
        return redirect('home')
    
    if user.is_musician():
        musician = get_current_musician(user)
        if not musician or not BandMembership.objects.filter(band=band, musician=musician).exists():
            messages.error(request, "Вы не являетесь участником этой группы.")
            return redirect('groups:band_list')
    
    add_form = None
    if user.can_manage_bands():
        add_form = AddMemberForm(band=band)
    
    if request.method == 'POST' and 'add_member' in request.POST and user.can_manage_bands():
        add_form = AddMemberForm(request.POST, band=band)
        if add_form.is_valid():
            membership = add_form.save(commit=False)
            membership.band = band
            membership.save()
            musician_name = f"{membership.musician.first_name} {membership.musician.last_name}"
            messages.success(request, f'Музыкант {musician_name} добавлен в группу!')
            return redirect('groups:band_members', pk=band.pk)
    
    memberships = BandMembership.objects.filter(band=band).select_related('musician').order_by('-join_date')
    context = {
        'band': band,
        'memberships': memberships,
        'add_form': add_form,
        'is_manager': user.can_manage_bands()
    }
    return render(request, 'groups/band_members.html', context)

@login_required
@user_passes_test(lambda u: u.can_manage_bands())
def member_remove(request, pk, member_id):
    band = get_object_or_404(Band, pk=pk)
    membership = get_object_or_404(BandMembership, id=member_id, band=band)
    
    if request.user.is_manager():
        current_musician = get_current_musician(request.user)
        if not current_musician or not BandMembership.objects.filter(band=band, musician=current_musician).exists():
            messages.error(request, "У вас нет прав для управления этой группой.")
            return redirect('groups:band_list')
    
    if request.method == 'POST':
        musician_name = f"{membership.musician.first_name} {membership.musician.last_name}"
        membership.delete()
        messages.success(request, f'Музыкант {musician_name} удален из группы!')
        return redirect('groups:band_members', pk=band.pk)
    
    return render(request, 'groups/member_confirm_remove.html', {
        'band': band,
        'membership': membership
    })