from django.contrib import admin
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Trainer, Zone, Tariff, Session, Booking, Favorite, Comment
from .exports import export_bookings_to_excel, export_bookings_by_session


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'specialization')
    search_fields = ('last_name', 'first_name', 'specialization')


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')
    search_fields = ('name',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'visits_display')
    search_fields = ('name',)

    @admin.display(description='Лимит посещений')
    def visits_display(self, obj):
        return obj.visits_display()


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('user', 'created_at', 'status', 'moderation_reason')
    readonly_fields = ('user', 'created_at')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'zone', 'date', 'max_participants', 'booked_count')
    list_filter = ('zone', 'trainer')
    search_fields = ('title',)
    date_hierarchy = 'date'
    inlines = [BookingInline]
    actions = ['export_session_excel']

    @admin.display(description='Записано')
    def booked_count(self, obj):
        return obj.booked_count()

    @admin.action(description='Экспорт в Excel (записи этой сессии)')
    def export_session_excel(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Выберите одну сессию', level=messages.ERROR)
            return

        session = queryset.first()
        buffer = export_bookings_by_session(session)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="session_{session.pk}.xlsx"'
        return response


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'created_at', 'status_display', 'moderated_at')
    list_filter = ('status', 'session')
    search_fields = ('user__username', 'session__title')
    readonly_fields = ('created_at', 'moderated_at')
    actions = ['approve_bookings', 'reject_with_reason', 'export_all_excel']
    fieldsets = (
        ('Основное', {'fields': ('user', 'session', 'created_at')}),
        ('Модерация', {'fields': ('status', 'moderation_reason', 'moderated_at')}),
    )

    @admin.display(description='Статус')
    def status_display(self, obj):
        colors = {
            'pending': '🟡 На модерации',
            'approved': '🟢 Одобрена',
            'rejected': '🔴 Отклонена',
        }
        return colors.get(obj.status, obj.status)

    @admin.action(description='✅ Одобрить выбранные')
    def approve_bookings(self, request, queryset):
        count = queryset.update(
            status='approved',
            moderation_reason='',
            moderated_at=timezone.now()
        )
        self.message_user(request, f'Одобрено записей: {count}')

    @admin.action(description='❌ Отклонить с причиной')
    def reject_with_reason(self, request, queryset):
        if 'apply' in request.POST:
            reason = request.POST.get('reason', '').strip()
            if not reason:
                self.message_user(request, 'Укажите причину', level=messages.ERROR)
                return redirect(request.get_full_path())

            count = queryset.update(
                status='rejected',
                moderation_reason=reason,
                moderated_at=timezone.now()
            )
            self.message_user(request, f'Отклонено записей: {count}')
            return redirect(request.get_full_path())

        return render(request, 'admin/cancel_with_reason.html', {
            'bookings': queryset,
            'title': 'Отклонение записей с указанием причины',
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })

    @admin.action(description='📊 Экспорт всех записей в Excel')
    def export_all_excel(self, request, queryset):
        buffer = export_bookings_to_excel()
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="bookings.xlsx"'
        return response


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'created_at')
    search_fields = ('user__username', 'session__title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'short_text', 'created_at')
    search_fields = ('user__username', 'text')

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:60]