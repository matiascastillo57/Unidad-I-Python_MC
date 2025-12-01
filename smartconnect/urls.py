from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'sensores', views.SensorViewSet, basename='sensor')
router.register(r'barreras', views.BarreraViewSet, basename='barrera')
router.register(r'eventos', views.EventoViewSet, basename='evento')
router.register(r'usuarios', views.UserViewSet, basename='usuario')

urlpatterns = [
    # Endpoint obligatorio de información
    path('info/', views.api_info, name='api-info'),
    
    # Endpoint de validación de acceso
    path('acceso/validar/', views.validar_acceso_sensor, name='validar-acceso'),
    
    # Rutas del router
    path('', include(router.urls)),
]