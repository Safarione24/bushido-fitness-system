from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Booking


class BookingCreateTests(TestCase):

    def setUp(self):
        """Создаём пользователя, который будет добавлять записи"""
        self.user = User.objects.create_user(
            username='testuser',
            password='StrongPass123'
        )

    def test_create_page_requires_login(self):
        """Гость не может открыть страницу создания"""
        response = self.client.get(reverse('booking_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_page_opens_for_user(self):
        """Авторизованный видит форму создания"""
        self.client.login(username='testuser', password='StrongPass123')
        response = self.client.get(reverse('booking_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')

    def test_create_booking_success(self):
        """Успешное создание записи"""
        self.client.login(username='testuser', password='StrongPass123')
        response = self.client.post(reverse('booking_create'), {
            'title': 'Каратэ',
            'date': '2026-10-01 18:00',
        })
        # редирект на список
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('booking_list'))

        # запись создана
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()

        # привязана к текущему пользователю
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.title, 'Каратэ')

    def test_create_booking_invalid_data(self):
        """Пустая форма не создаёт запись"""
        self.client.login(username='testuser', password='StrongPass123')
        response = self.client.post(reverse('booking_create'), {
            'title': '',
            'date': '',
        })
        # остались на странице с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 0)

    def test_create_booking_binds_current_user(self):
        """Даже если два юзера — запись привязывается к тому, кто вошёл"""
        other = User.objects.create_user(username='other', password='StrongPass123')
        self.client.login(username='testuser', password='StrongPass123')

        self.client.post(reverse('booking_create'), {
            'title': 'Бокс',
            'date': '2026-10-02 19:00',
        })

        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.user)
        self.assertNotEqual(booking.user, other)

    def test_created_booking_appears_in_list(self):
        """Созданная запись видна в списке"""
        self.client.login(username='testuser', password='StrongPass123')
        self.client.post(reverse('booking_create'), {
            'title': 'Айкидо',
            'date': '2026-10-03 17:00',
        })

        response = self.client.get(reverse('booking_list'))
        self.assertContains(response, 'Айкидо')