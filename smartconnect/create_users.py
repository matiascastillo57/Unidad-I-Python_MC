"""
Script para crear usuarios de prueba
Guardar en: smartconnect/management/commands/create_users.py
Ejecutar con: python manage.py create_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from smartconnect.models import PerfilUsuario, Departamento


class Command(BaseCommand):
    help = 'Crea usuarios de prueba con sus perfiles'

    def handle(self, *args, **kwargs):
        # Crear departamentos
        dep1, _ = Departamento.objects.get_or_create(
            nombre="TI",
            defaults={
                'descripcion': 'Departamento de Tecnologías de Información',
                'ubicacion': 'Piso 3'
            }
        )
        
        dep2, _ = Departamento.objects.get_or_create(
            nombre="RRHH",
            defaults={
                'descripcion': 'Recursos Humanos',
                'ubicacion': 'Piso 2'
            }
        )

        # Crear Admin
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@smartconnect.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                is_staff=True
            )
            PerfilUsuario.objects.create(
                user=admin_user,
                rol='admin',
                telefono='+56912345678',
                departamento=dep1
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuario admin creado'))
        else:
            self.stdout.write(self.style.WARNING('✗ Usuario admin ya existe'))

        # Crear Operador
        if not User.objects.filter(username='operador').exists():
            op_user = User.objects.create_user(
                username='operador',
                email='operador@smartconnect.com',
                password='operador123',
                first_name='Juan',
                last_name='Pérez'
            )
            PerfilUsuario.objects.create(
                user=op_user,
                rol='operador',
                telefono='+56987654321',
                departamento=dep2
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuario operador creado'))
        else:
            self.stdout.write(self.style.WARNING('✗ Usuario operador ya existe'))

        self.stdout.write(self.style.SUCCESS('\n=== Credenciales ==='))
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Operador: operador / operador123')