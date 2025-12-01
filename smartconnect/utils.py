from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para la API
    """
    # Llamar al handler por defecto primero
    response = exception_handler(exc, context)

    if response is not None:
        # Personalizar el formato de error
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
        }

        # Agregar mensaje personalizado según el código de estado
        if response.status_code == 400:
            custom_response_data['mensaje'] = 'Error de validación en los datos enviados'
            custom_response_data['detalles'] = response.data
        
        elif response.status_code == 401:
            custom_response_data['mensaje'] = 'No autenticado. Token requerido o inválido'
            custom_response_data['detalles'] = 'Debe proporcionar un token JWT válido en el header Authorization'
        
        elif response.status_code == 403:
            custom_response_data['mensaje'] = 'No tiene permisos para realizar esta acción'
            custom_response_data['detalles'] = response.data.get('detail', 'Permisos insuficientes')
        
        elif response.status_code == 404:
            custom_response_data['mensaje'] = 'Recurso no encontrado'
            custom_response_data['detalles'] = response.data.get('detail', 'El recurso solicitado no existe')
        
        elif response.status_code == 405:
            custom_response_data['mensaje'] = 'Método HTTP no permitido'
            custom_response_data['detalles'] = response.data
        
        else:
            custom_response_data['mensaje'] = 'Error en la solicitud'
            custom_response_data['detalles'] = response.data

        response.data = custom_response_data

    return response


def handler404(request, exception=None):
    """
    Handler personalizado para rutas inexistentes (404)
    """
    return Response({
        'error': True,
        'status_code': 404,
        'mensaje': 'Ruta no encontrada',
        'detalles': f'La ruta {request.path} no existe en esta API',
        'rutas_disponibles': {
            'autenticacion': '/api/token/',
            'informacion': '/api/info/',
            'departamentos': '/api/departamentos/',
            'sensores': '/api/sensores/',
            'barreras': '/api/barreras/',
            'eventos': '/api/eventos/',
            'usuarios': '/api/usuarios/',
            'validar_acceso': '/api/acceso/validar/'
        }
    }, status=status.HTTP_404_NOT_FOUND)


def handler500(request, exception=None):
    """
    Handler personalizado para errores del servidor (500)
    """
    return Response({
        'error': True,
        'status_code': 500,
        'mensaje': 'Error interno del servidor',
        'detalles': 'Ha ocurrido un error inesperado. Por favor contacte al administrador.'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)