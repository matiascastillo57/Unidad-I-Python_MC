# ecoenergy/decorators.py
"""
Decoradores personalizados para manejo de permisos con mejor UX
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def permission_required_with_message(perm, redirect_url='zona_list'):
    """
    Decorador que verifica permisos y muestra mensaje amigable.
    
    En lugar de mostrar 403, redirige con un mensaje explicativo.
    
    Args:
        perm: Permiso requerido (ej: 'monitoring.add_zone')
        redirect_url: URL a la que redirigir si no tiene permiso
    
    Uso:
        @permission_required_with_message('monitoring.add_zone')
        def zona_create(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Verificar si el usuario tiene el permiso
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            
            # Si no tiene permiso, redirigir con mensaje
            messages.warning(
                request,
                f'No tienes permisos para realizar esta acción. '
                f'Contacta al administrador si necesitas acceso.'
            )
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def ajax_login_required(view_func):
    """
    Decorador para vistas AJAX que requieren autenticación.
    Retorna JSON en lugar de redirigir.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.http import JsonResponse
            return JsonResponse({
                'ok': False,
                'error': 'Debes iniciar sesión para realizar esta acción'
            }, status=401)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def ajax_permission_required(perm):
    """
    Decorador para vistas AJAX que requieren un permiso específico.
    Retorna JSON en lugar de redirigir.
    """
    def decorator(view_func):
        @wraps(view_func)
        @ajax_login_required
        def wrapper(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            
            from django.http import JsonResponse
            return JsonResponse({
                'ok': False,
                'error': 'No tienes permisos para realizar esta acción'
            }, status=403)
        
        return wrapper
    return decorator