# monitoring/urls.py (crear este archivo)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('measurements/', views.measurement_list, name='measurement_list'),
]