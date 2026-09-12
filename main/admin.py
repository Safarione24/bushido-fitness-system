from django.contrib import admin
from .models import Trainer, Zone, Tariff, Session, Booking


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'specialization')


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'visits_limit')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'zone', 'date', 'max_participants')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'created_at')