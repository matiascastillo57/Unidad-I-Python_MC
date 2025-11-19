from pathlib import Path
import os
from django.contrib.messages import constants as msg


BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-iiq3aar(6%k3f09%q^0v6nofy_q=p&#7dvt7#b))=mrz^ky@z$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
     'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    
    # Nuestras aplicaciones
    'monitoring',
    'usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecoenergy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecoenergy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# NUEVO: Configuración para archivos media (imágenes subidas por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de autenticación
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # Obtener de variable de entorno
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Obtener de variable de entorno
DEFAULT_FROM_EMAIL = 'noreply@ecoenergy.com'

# Configuración de autenticación
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email backend para desarrollo (muestra en consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Agregar al final de ecoenergy/settings.py

# =========================================================================
# CONFIGURACIÓN DE SESIONES
# =========================================================================

# Duración de la cookie de sesión (en segundos) - 2 horas
SESSION_COOKIE_AGE = 60 * 60 * 2

# ¿La sesión expira al cerrar el navegador?
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ¿Actualizar expiración en cada request?
SESSION_SAVE_EVERY_REQUEST = False

# Seguridad de las cookies (activar en producción con HTTPS)
SESSION_COOKIE_SECURE = False  # Cambiar a True en producción

# Solo enviar cookie en el mismo sitio (protección CSRF)
SESSION_COOKIE_SAMESITE = 'Lax'  # Opciones: 'Lax', 'Strict', 'None'

# Backend de sesión (default: base de datos)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =========================================================================
# CONFIGURACIÓN DE MENSAJES (MESSAGE FRAMEWORK)
# =========================================================================

from django.contrib.messages import constants as msg

MESSAGE_TAGS = {
    msg.DEBUG: 'secondary',
    msg.INFO: 'info',
    msg.SUCCESS: 'success',
    msg.WARNING: 'warning',
    msg.ERROR: 'danger',  # Bootstrap usa 'danger' en lugar de 'error'
}

# Nivel mínimo de mensajes a mostrar
MESSAGE_LEVEL = msg.DEBUG  # Mostrar todos los niveles

# Storage de mensajes (usa sesión por defecto)
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# =========================================================================
# PÁGINAS DE ERROR PERSONALIZADAS
# =========================================================================

# Esto hace que Django use tus templates personalizados para errores
# Crear: templates/404.html y templates/403.html
DEBUG = True  # En producción cambiar a False para ver las páginas de error


# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}