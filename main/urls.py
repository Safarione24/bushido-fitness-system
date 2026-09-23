from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('sessions/', views.session_list, name='session_list'),
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),

    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/create/<int:session_id>/', views.booking_create, name='booking_create_for_session'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),

    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/toggle/<int:session_id>/', views.favorite_toggle, name='favorite_toggle'),
    path('favorites/<int:pk>/delete/', views.favorite_delete, name='favorite_delete'),

    path('comments/add/<int:session_id>/', views.comment_add, name='comment_add'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),

    path('export/bookings/', views.export_bookings, name='export_bookings'),
    path('export/session/<int:pk>/', views.export_session, name='export_session'),
]