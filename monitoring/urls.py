from django.urls import path
from . import views

urlpatterns = [
    # Vistas HTML
    path('', views.dashboard, name='dashboard'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('measurements/', views.measurement_list, name='measurement_list'),
    
    # APIs JSON (NUEVO)
    #path('api/measurements/', views.api_measurements_json, name='api_measurements'),
    #path('api/alerts/', views.api_alerts_json, name='api_alerts'),
    #path('api/devices/', views.api_devices_json, name='api_devices'),
]