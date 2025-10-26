# monitoring/urls.py - VERSIÓN COMPLETA CON TODOS LOS CRUDS
from django.urls import path
from . import views
from . import zone_views
from . import device_views
from . import category_views
from . import measurement_views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # =======================================================================
    # ZONAS - CRUD COMPLETO
    # =======================================================================
    path('zonas/', zone_views.zona_list, name='zona_list'),
    path('zonas/crear/', zone_views.zona_create, name='zona_create'),
    path('zonas/<int:pk>/', zone_views.zona_detail, name='zona_detail'),
    path('zonas/<int:pk>/editar/', zone_views.zona_update, name='zona_update'),
    path('zonas/<int:pk>/eliminar/', zone_views.zona_delete_ajax, name='zona_delete_ajax'),
    
    # =======================================================================
    # DISPOSITIVOS - CRUD COMPLETO
    # =======================================================================
    path('devices/', device_views.device_list, name='device_list'),
    path('devices/crear/', device_views.device_create, name='device_create'),
    path('devices/<int:pk>/', device_views.device_detail, name='device_detail'),
    path('devices/<int:pk>/editar/', device_views.device_update, name='device_update'),
    path('devices/<int:pk>/eliminar/', device_views.device_delete_ajax, name='device_delete_ajax'),
    
    # =======================================================================
    # CATEGORÍAS - CRUD COMPLETO
    # =======================================================================
    path('categorias/', category_views.category_list, name='category_list'),
    path('categorias/crear/', category_views.category_create, name='category_create'),
    path('categorias/<int:pk>/editar/', category_views.category_update, name='category_update'),
    path('categorias/<int:pk>/eliminar/', category_views.category_delete_ajax, name='category_delete_ajax'),
    
    # =======================================================================
    # MEDICIONES - CRUD COMPLETO
    # =======================================================================
    path('measurements/', measurement_views.measurement_list, name='measurement_list'),
    path('measurements/crear/', measurement_views.measurement_create, name='measurement_create'),
    path('measurements/<int:pk>/editar/', measurement_views.measurement_update, name='measurement_update'),
    path('measurements/<int:pk>/eliminar/', measurement_views.measurement_delete_ajax, name='measurement_delete_ajax'),
]