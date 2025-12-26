from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.models import Band, BandMembership, Musician
from .forms import BandForm, AddMemberForm

def get_current_musician(user):
    if not user.is_authenticated or not user.phone:
        return None
    try:
        return Musician.objects.get(phone=user.phone)
    except Musician.DoesNotExist:
        return None

def is_manager(user):
    return user.is_authenticated and user.is_staff

class BandListView(LoginRequiredMixin, ListView):
    model = Band
    template_name = 'groups/band_list.html'
    context_object_name = 'bands'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_staff and get_current_musician(request.user) is None:
            messages.error(request, "У вас нет прав для просмотра списка групп. Требуется профиль музыканта.")
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().order_by('band_name')
        user = self.request.user
        
        if not user.is_staff:
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
        return is_manager(self.request.user)

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
        return is_manager(self.request.user)

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
        return is_manager(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Группа "{self.object.band_name}" успешно удалена!')
        return super().form_valid(form)

@login_required
def band_members(request, pk):
    band = get_object_or_404(Band, pk=pk)
    user = request.user
    
    if not user.is_staff:
        musician = get_current_musician(user)
        if not musician:
            messages.error(request, "Доступ запрещен.")
            return redirect('home')
        
        if not BandMembership.objects.filter(band=band, musician=musician).exists():
            messages.error(request, "Вы не являетесь участником этой группы.")
            return redirect('groups:band_list')

    add_form = None
    if user.is_staff:
        add_form = AddMemberForm(band=band)
        if request.method == 'POST' and 'add_member' in request.POST:
            add_form = AddMemberForm(request.POST, band=band)
            if add_form.is_valid():
                membership = add_form.save(commit=False)
                membership.band = band
                membership.save()
                messages.success(request, f'Музыкант добавлен в группу!')
                return redirect('groups:band_members', pk=band.pk)

    memberships = BandMembership.objects.filter(band=band).select_related('musician').order_by('-join_date')
    
    context = {
        'band': band,
        'memberships': memberships,
        'add_form': add_form,
        'is_manager': user.is_staff
    }
    
    return render(request, 'groups/band_members.html', context)


@login_required
@user_passes_test(is_manager)
def member_remove(request, pk, member_id):
    band = get_object_or_404(Band, pk=pk)
    membership = get_object_or_404(BandMembership, id=member_id, band=band)
    
    if request.method == 'POST':
        musician_name = str(membership.musician)
        membership.delete()
        messages.success(request, f'Музыкант {musician_name} удален из группы!')
        return redirect('groups:band_members', pk=band.pk)
    
    return render(request, 'groups/member_confirm_remove.html', {
        'band': band,
        'membership': membership
    })