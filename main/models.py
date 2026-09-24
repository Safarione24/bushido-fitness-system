from django.db import models
from django.contrib.auth.models import User


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Trainer(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    specialization = models.CharField(max_length=100, verbose_name='Специализация')
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True, verbose_name='Фото')
    description = models.TextField(blank=True, verbose_name='Описание')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Zone(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    description = models.TextField(blank=True, verbose_name='Описание')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Зона'
        verbose_name_plural = 'Зоны'

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    duration_days = models.PositiveIntegerField(verbose_name='Длительность (дней)')
    visits_limit = models.PositiveIntegerField(verbose_name='Лимит посещений', help_text='0 = безлимит')
    description = models.TextField(blank=True, verbose_name='Описание')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'

    def __str__(self):
        return f"{self.name} — {self.price} ₽"

    def is_unlimited(self):
        return self.visits_limit == 0

    def visits_display(self):
        return 'Безлимит' if self.is_unlimited() else f'{self.visits_limit} посещений'


class Session(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, verbose_name='Тренер')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name='Зона')
    title = models.CharField(max_length=100, verbose_name='Название')
    date = models.DateTimeField(verbose_name='Дата и время')
    max_participants = models.PositiveIntegerField(verbose_name='Максимум участников')
    description = models.TextField(blank=True, verbose_name='Описание')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} — {self.date:%d.%m.%Y %H:%M}"

    def booked_count(self):
        return self.booking_set.filter(status='approved', is_deleted=False).count()

    def free_places(self):
        return max(0, self.max_participants - self.booked_count())


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='Сессия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    moderation_reason = models.TextField(blank=True, verbose_name='Комментарий модератора')
    moderated_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата модерации')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.session.title} ({self.get_status_display()})"

    def is_active(self):
        return self.status == 'approved'

    def is_pending(self):
        return self.status == 'pending'

    def is_rejected(self):
        return self.status == 'rejected'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='Сессия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f"{self.user.username} → {self.session.title}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='comments', verbose_name='Сессия')
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:40]}"