from django.urls import path
from . import views

app_name = 'dispositivos'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('panel/', views.panel_dispositivos, name='panel'),
    path('dispositivo/<int:id>/', views.detalle_dispositivo, name='detalle'),
    path('mediciones/', views.lista_mediciones, name='mediciones'),
]