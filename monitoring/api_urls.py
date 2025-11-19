# monitoring/api_urls.py
"""
URLs para la API REST de EcoEnergy
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    OrganizationViewSet,
    CategoryViewSet,
    ZoneViewSet,
    DeviceViewSet,
    MeasurementViewSet,
    AlertViewSet,
    DashboardStatsAPIView,
    HealthCheckAPIView,
    ProjectInfoAPIView
)

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'measurements', MeasurementViewSet, basename='measurement')
router.register(r'alerts', AlertViewSet, basename='alert')

# URLs de la API
urlpatterns = [
    # Health check y info
    path('health/', HealthCheckAPIView.as_view(), name='api-health'),
    path('info/', ProjectInfoAPIView.as_view(), name='api-info'),
    
    # Dashboard stats
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api-dashboard-stats'),
    
    # ViewSets (genera automáticamente las rutas CRUD)
    path('', include(router.urls)),
]

# Rutas generadas automáticamente por el router:
# 
# Organizations:
#   GET    /api/organizations/           - Listar todas
#   POST   /api/organizations/           - Crear nueva
#   GET    /api/organizations/{id}/      - Ver detalle
#   PUT    /api/organizations/{id}/      - Actualizar completa
#   PATCH  /api/organizations/{id}/      - Actualizar parcial
#   DELETE /api/organizations/{id}/      - Eliminar
#
# Categories:
#   GET    /api/categories/              - Listar todas
#   POST   /api/categories/              - Crear nueva
#   GET    /api/categories/{id}/         - Ver detalle
#   PUT    /api/categories/{id}/         - Actualizar
#   PATCH  /api/categories/{id}/         - Actualizar parcial
#   DELETE /api/categories/{id}/         - Eliminar
#   GET    /api/categories/{id}/devices/ - Dispositivos de la categoría
#
# Zones:
#   GET    /api/zones/                   - Listar todas
#   POST   /api/zones/                   - Crear nueva
#   GET    /api/zones/{id}/              - Ver detalle
#   PUT    /api/zones/{id}/              - Actualizar
#   PATCH  /api/zones/{id}/              - Actualizar parcial
#   DELETE /api/zones/{id}/              - Eliminar
#   GET    /api/zones/{id}/devices/      - Dispositivos de la zona
#
# Devices:
#   GET    /api/devices/                        - Listar todos
#   POST   /api/devices/                        - Crear nuevo
#   GET    /api/devices/{id}/                   - Ver detalle
#   PUT    /api/devices/{id}/                   - Actualizar
#   PATCH  /api/devices/{id}/                   - Actualizar parcial
#   DELETE /api/devices/{id}/                   - Eliminar
#   GET    /api/devices/{id}/measurements/      - Mediciones del dispositivo
#   GET    /api/devices/{id}/alerts/            - Alertas del dispositivo
#   GET    /api/devices/{id}/stats/             - Estadísticas del dispositivo
#
# Measurements:
#   GET    /api/measurements/            - Listar todas
#   POST   /api/measurements/            - Crear nueva
#   GET    /api/measurements/{id}/       - Ver detalle
#   PUT    /api/measurements/{id}/       - Actualizar
#   PATCH  /api/measurements/{id}/       - Actualizar parcial
#   DELETE /api/measurements/{id}/       - Eliminar
#
# Alerts:
#   GET    /api/alerts/                  - Listar todas
#   POST   /api/alerts/                  - Crear nueva
#   GET    /api/alerts/{id}/             - Ver detalle
#   PUT    /api/alerts/{id}/             - Actualizar
#   PATCH  /api/alerts/{id}/             - Actualizar parcial
#   DELETE /api/alerts/{id}/             - Eliminar
#   POST   /api/alerts/{id}/resolve/     - Marcar como resuelta
#
# Parámetros de query disponibles:
#
# Devices:
#   ?category=1           - Filtrar por categoría
#   ?zone=2               - Filtrar por zona
#   ?search=texto         - Buscar en nombre/descripción
#
# Measurements:
#   ?device=1             - Filtrar por dispositivo
#   ?date_from=2025-01-01 - Desde fecha
#   ?date_to=2025-12-31   - Hasta fecha
#
# Alerts:
#   ?device=1             - Filtrar por dispositivo
#   ?severity=HIGH        - Filtrar por severidad
#   ?is_resolved=true     - Filtrar resueltas/pendientes