from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a administradores
    """
    message = "Solo los administradores pueden realizar esta acción"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si el usuario tiene perfil y es admin
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.es_admin()
        
        # Si no tiene perfil, verificar si es superusuario
        return request.user.is_superuser


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin: CRUD completo
    Operador: Solo lectura (GET, HEAD, OPTIONS)
    """
    message = "Solo los administradores pueden modificar datos"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Métodos seguros (lectura) permitidos para todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # Métodos de escritura solo para admin
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.es_admin()
        
        return request.user.is_superuser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite editar solo al propietario del objeto o a un admin
    """
    message = "Solo puedes editar tus propios datos o ser administrador"

    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos los autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin puede hacer todo
        if hasattr(request.user, 'perfil') and request.user.perfil.es_admin():
            return True
        
        if request.user.is_superuser:
            return True

        # El propietario puede editar
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'usuario_asignado'):
            return obj.usuario_asignado == request.user

        return False