from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone

from .models import Booking, Session, Favorite, Comment
from .forms import BookingForm, CommentForm
from .exports import export_bookings_to_excel, export_bookings_by_session


def home_view(request):
    upcoming = Session.objects.filter(date__gte=timezone.now())[:6]
    return render(request, 'main/home.html', {'upcoming': upcoming})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать в Bushido!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Вы вошли в систему')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def session_list(request):
    query = request.GET.get('q', '')
    sessions = Session.objects.filter(date__gte=timezone.now())
    if query:
        sessions = sessions.filter(
            Q(title__icontains=query) |
            Q(trainer__last_name__icontains=query) |
            Q(zone__name__icontains=query)
        )
    return render(request, 'main/session_list.html', {
        'sessions': sessions,
        'query': query,
    })


def session_detail(request, pk):
    session = get_object_or_404(Session, pk=pk)
    comments = session.comments.all()
    comment_form = CommentForm()

    is_booked = False
    is_favorite = False
    if request.user.is_authenticated:
        is_booked = Booking.objects.filter(
            user=request.user, session=session, status='approved'
        ).exists()
        is_favorite = Favorite.objects.filter(
            user=request.user, session=session
        ).exists()

    return render(request, 'main/session_detail.html', {
        'session': session,
        'comments': comments,
        'comment_form': comment_form,
        'is_booked': is_booked,
        'is_favorite': is_favorite,
        'now': timezone.now(),
    })


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).select_related('session', 'session__trainer')
    return render(request, 'main/booking_list.html', {'bookings': bookings})


@login_required
def booking_create(request, session_id=None):
    initial = {}
    if session_id:
        initial['session'] = session_id

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            session = form.cleaned_data['session']

            if session.date < timezone.now():
                messages.error(request, 'Нельзя записаться на прошедшую сессию')
                return redirect('session_list')

            if session.free_places() <= 0:
                messages.error(request, 'Мест не осталось')
                return redirect('session_detail', pk=session.pk)

            if Booking.objects.filter(user=request.user, session=session).exists():
                messages.warning(request, 'Вы уже записаны на эту сессию')
                return redirect('booking_list')

            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = 'pending'
            booking.save()
            messages.success(request, f'Заявка на «{session.title}» отправлена на модерацию')
            return redirect('booking_list')
    else:
        form = BookingForm(initial=initial)

    return render(request, 'main/booking_form.html', {'form': form})


@login_required
def booking_edit(request, pk):
    messages.info(request, 'Изменение записи недоступно. Удалите и создайте заново.')
    return redirect('booking_list')


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        booking.is_deleted = True
        booking.deleted_at = timezone.now()
        booking.save()
        messages.success(request, 'Запись удалена')
        return redirect('booking_list')

    return render(request, 'main/booking_confirm_delete.html', {'booking': booking})


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('session', 'session__trainer')
    return render(request, 'main/favorite_list.html', {'favorites': favorites})


@login_required
def favorite_toggle(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, session=session)

    if not created and not fav.is_deleted:
        fav.is_deleted = True
        fav.deleted_at = timezone.now()
        fav.save()
        messages.info(request, 'Удалено из избранного')
    else:
        fav.is_deleted = False
        fav.deleted_at = None
        fav.save()
        messages.success(request, 'Добавлено в избранное')

    return redirect(request.META.get('HTTP_REFERER', 'session_list'))

@login_required
def favorite_delete(request, pk):
    fav = get_object_or_404(Favorite, pk=pk, user=request.user)
    fav.is_deleted = True
    fav.deleted_at = timezone.now()
    fav.save()
    messages.info(request, 'Удалено из избранного')
    return redirect('favorite_list')


@login_required
def comment_add(request, session_id):
    session = get_object_or_404(Session, pk=session_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.session = session
            comment.save()
            messages.success(request, 'Комментарий добавлен')

    return redirect('session_detail', pk=session.pk)


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.user != request.user and not request.user.is_staff:
        messages.error(request, 'Нет прав на удаление')
        return redirect('session_detail', pk=comment.session.pk)

    session_pk = comment.session.pk
    comment.is_deleted = True
    comment.deleted_at = timezone.now()
    comment.save()
    messages.info(request, 'Комментарий удалён')
    return redirect('session_detail', pk=session_pk)


@login_required
def export_bookings(request):
    if not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('home')

    buffer = export_bookings_to_excel()
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'bookings_{timezone.now():%Y%m%d_%H%M}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_session(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('home')

    session = get_object_or_404(Session, pk=pk)
    buffer = export_bookings_by_session(session)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'session_{session.pk}_{timezone.now():%Y%m%d}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response