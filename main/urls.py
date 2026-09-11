from django.urls import path
from . import views

urlpatterns = [
    path('',          views.home_view,     name='home'),
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('bookings/',        views.booking_list,   name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),  
]