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
    'rest_framework.authtoken',
    'rest_framework_simplejwt',  # AGREGADO para JWT
    'corsheaders',  # AGREGADO para CORS
    
    # Nuestras aplicaciones
    'monitoring',
    'usuarios',
    'smartconnect',  # NUEVA APP PARA LA EVALUACIÓN
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # AGREGADO - debe estar primero
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # ACTUALIZADO para producción

# NUEVO: Configuración para archivos media (imágenes subidas por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN (TEMPLATES HTML)
# =========================================================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Email backend para desarrollo (muestra en consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
# CONFIGURACIÓN DE CORS (para API)
# =========================================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Solo para desarrollo - cambiar en producción
CORS_ALLOW_ALL_ORIGINS = True  

# =========================================================================
# DJANGO REST FRAMEWORK - CONFIGURACIÓN MEJORADA
# =========================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT para API
        'rest_framework.authentication.SessionAuthentication',  # Para navegador
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # CAMBIADO: ahora requiere auth por defecto
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'EXCEPTION_HANDLER': 'smartconnect.utils.custom_exception_handler',  # AGREGADO: handler personalizado
}

# =========================================================================
# SIMPLE JWT - CONFIGURACIÓN COMPLETA
# =========================================================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=5),  # Token válido por 5 horas
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # Refresh token válido por 1 día
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

# =========================================================================
# CONFIGURACIÓN PARA PRODUCCIÓN (AWS)
# =========================================================================

# Descomentar y configurar para producción:
"""
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# Seguridad para producción
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
"""