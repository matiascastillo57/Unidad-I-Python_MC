from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Sensor, Departamento, Evento, Barrera, PerfilUsuario
from .serializers import (
    SensorSerializer, DepartamentoSerializer, EventoSerializer,
    BarreraSerializer, UserSerializer, AccesoSensorSerializer,
    ControlBarreraSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminUser


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """
    Endpoint obligatorio con información del proyecto
    """
    return Response({
        "autor": ["Tu Nombre Completo"],  # CAMBIAR POR TU NOMBRE
        "asignatura": "Programación Back End",
        "proyecto": "SmartConnect - Sistema de Control de Acceso RFID",
        "descripcion": "API RESTful para administrar sensores RFID, usuarios, departamentos y eventos de acceso. Implementa autenticación JWT y control de permisos por roles.",
        "version": "1.0"
    })


class DepartamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de Departamentos
    Admin: CRUD completo
    Operador: Solo lectura
    """
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })


class SensorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de Sensores RFID
    Admin: CRUD completo
    Operador: Solo lectura
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def list(self, request):
        queryset = self.get_queryset()
        
        # Filtros opcionales
        estado = request.query_params.get('estado', None)
        departamento = request.query_params.get('departamento', None)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if departamento:
            queryset = queryset.filter(departamento_id=departamento)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def cambiar_estado(self, request, pk=None):
        """Endpoint para cambiar el estado de un sensor"""
        sensor = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in ['activo', 'inactivo', 'bloqueado', 'perdido']:
            return Response(
                {"error": "Estado inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sensor.estado = nuevo_estado
        sensor.save()
        
        serializer = self.get_serializer(sensor)
        return Response(serializer.data)


class BarreraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de Barreras
    """
    queryset = Barrera.objects.all()
    serializer_class = BarreraSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def controlar(self, request, pk=None):
        """
        Endpoint para abrir/cerrar barrera manualmente
        POST /api/barreras/{id}/controlar/
        Body: {"accion": "abrir"} o {"accion": "cerrar"}
        """
        barrera = self.get_object()
        serializer = ControlBarreraSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        accion = serializer.validated_data['accion']
        
        # Registrar evento
        tipo_evento = 'apertura_manual' if accion == 'abrir' else 'cierre_manual'
        Evento.objects.create(
            barrera=barrera,
            tipo=tipo_evento,
            usuario_responsable=request.user,
            descripcion=f"Control manual: {accion}",
            ip_origen=self.get_client_ip(request)
        )
        
        # Cambiar estado de barrera
        if accion == 'abrir':
            barrera.abrir()
        else:
            barrera.cerrar()
        
        return Response({
            "mensaje": f"Barrera {accion} exitosamente",
            "barrera": BarreraSerializer(barrera).data
        })

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consulta de Eventos
    Admin: CRUD completo
    Operador: Solo lectura
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def list(self, request):
        queryset = self.get_queryset()
        
        # Filtros opcionales
        tipo = request.query_params.get('tipo', None)
        sensor_id = request.query_params.get('sensor', None)
        fecha_desde = request.query_params.get('fecha_desde', None)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if sensor_id:
            queryset = queryset.filter(sensor_id=sensor_id)
        
        # Limitar a últimos 100 eventos por defecto
        queryset = queryset[:100]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de Usuarios
    Solo lectura para todos
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([AllowAny])
def validar_acceso_sensor(request):
    """
    Endpoint para validar acceso de un sensor RFID
    POST /api/acceso/validar/
    Body: {"uid_mac": "XX:XX:XX:XX:XX:XX", "barrera_id": 1}
    """
    serializer = AccesoSensorSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uid_mac = serializer.validated_data['uid_mac']
    barrera_id = serializer.validated_data.get('barrera_id')
    
    try:
        sensor = Sensor.objects.get(uid_mac=uid_mac)
        
        # Verificar estado del sensor
        if sensor.estado != 'activo':
            # Registrar intento denegado
            Evento.objects.create(
                sensor=sensor,
                tipo='acceso_denegado',
                descripcion=f"Sensor en estado: {sensor.estado}",
                ip_origen=get_client_ip(request)
            )
            
            return Response({
                "acceso": "denegado",
                "motivo": f"Sensor {sensor.estado}",
                "sensor": SensorSerializer(sensor).data
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Acceso permitido
        barrera = None
        if barrera_id:
            barrera = Barrera.objects.filter(id=barrera_id).first()
            if barrera:
                barrera.abrir()
        
        Evento.objects.create(
            sensor=sensor,
            barrera=barrera,
            tipo='acceso_permitido',
            descripcion="Acceso autorizado",
            ip_origen=get_client_ip(request)
        )
        
        return Response({
            "acceso": "permitido",
            "mensaje": "Acceso autorizado",
            "sensor": SensorSerializer(sensor).data,
            "barrera": BarreraSerializer(barrera).data if barrera else None
        })
        
    except Sensor.DoesNotExist:
        return Response({
            "acceso": "denegado",
            "motivo": "Sensor no registrado"
        }, status=status.HTTP_404_NOT_FOUND)


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip