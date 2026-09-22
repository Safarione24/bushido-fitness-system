from django.db import models
from django.contrib.auth.models import User


class Trainer(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    specialization = models.CharField(max_length=100, verbose_name='Специализация')

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.specialization})"


class Zone(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')

    class Meta:
        verbose_name = 'Зона'
        verbose_name_plural = 'Зоны'

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    duration_days = models.PositiveIntegerField(verbose_name='Длительность (дней)')
    visits_limit = models.PositiveIntegerField(verbose_name='Лимит посещений')

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self):
        return self.name


class Session(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, verbose_name='Тренер')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name='Зона')
    title = models.CharField(max_length=100, verbose_name='Название')
    date = models.DateTimeField(verbose_name='Дата и время')
    max_participants = models.PositiveIntegerField(verbose_name='Максимум участников')

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return f"{self.title} — {self.date:%d.%m.%Y %H:%M}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='Сессия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        unique_together = ('user', 'session')

    def __str__(self):
        return f"{self.user.username} — {self.session.title}"