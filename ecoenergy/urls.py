# ecoenergy/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Aplicación principal (templates HTML)
    path('', include('monitoring.urls')),
    
    # Autenticación de usuarios (templates HTML)
    path('auth/', include('usuarios.urls')),
    
    # ============================================
    # API REST - Autenticación JWT
    # ============================================
    path('api/login/', TokenObtainPairView.as_view(), name='api_token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    
    # API REST - Endpoints (protegidos con JWT)
    path('api/', include('monitoring.api_urls')),
    
    # DRF Auth (para navegador - interfaz web de DRF)
    path('api-auth/', include('rest_framework.urls')),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)