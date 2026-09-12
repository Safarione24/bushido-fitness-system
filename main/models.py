from django.db import models
from django.contrib.auth.models import User


class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.specialization})"


class Zone(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    visits_limit = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Session(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateTimeField()
    max_participants = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} — {self.date:%d.%m.%Y %H:%M}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'session')  

    def __str__(self):
        return f"{self.user.username} — {self.session.title}"