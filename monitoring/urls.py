# monitoring/urls.py - VERSIÓN ACTUALIZADA
from django.urls import path
from . import views
from . import zone_views

urlpatterns = [
    # Vistas HTML principales
    path('', views.dashboard, name='dashboard'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('measurements/', views.measurement_list, name='measurement_list'),
    
    # =====================================================================
    # CRUD DE ZONAS (NUEVO)
    # =====================================================================
    path('zonas/', zone_views.zona_list, name='zona_list'),
    path('zonas/crear/', zone_views.zona_create, name='zona_create'),
    path('zonas/<int:pk>/', zone_views.zona_detail, name='zona_detail'),
    path('zonas/<int:pk>/editar/', zone_views.zona_update, name='zona_update'),
    path('zonas/<int:pk>/eliminar/', zone_views.zona_delete_ajax, name='zona_delete_ajax'),
    
    # Ejemplo con filtros en sesión (opcional)
    path('zonas/filtros/', zone_views.zona_list_with_filters, name='zona_list_with_filters'),
    
    # APIs JSON (si las deseas activar)
    # path('api/measurements/', views.api_measurements_json, name='api_measurements'),
    # path('api/alerts/', views.api_alerts_json, name='api_alerts'),
    # path('api/devices/', views.api_devices_json, name='api_devices'),
]