from django.core.management.base import BaseCommand
from django.db import transaction
from monitoring.models import Organization, Category, Zone, Device
from django.contrib.auth.models import User
from usuarios.models import UserProfile

class Command(BaseCommand):
    help = 'Carga datos de ejemplo para EcoEnergy'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos...')
        
        try:
            with transaction.atomic():
                # 1. Crear organización
                org, _ = Organization.objects.get_or_create(
                    name='EcoTech Solutions',
                    defaults={
                        'email': 'contacto@ecotech.cl',
                        'phone': '+56 2 2345 6789'
                    }
                )
                
                # 2. Crear categorías
                cat1, _ = Category.objects.get_or_create(
                    name='Climatización',
                    organization=org,
                    defaults={'description': 'Equipos de AC'}
                )
                
                cat2, _ = Category.objects.get_or_create(
                    name='Iluminación',
                    organization=org,
                    defaults={'description': 'Luces LED'}
                )
                
                # 3. Crear zonas
                zone1, _ = Zone.objects.get_or_create(
                    name='Oficina Principal',
                    organization=org,
                    defaults={'description': 'Piso 1'}
                )
                
                # 4. Crear dispositivos
                Device.objects.get_or_create(
                    name='AC Oficina',
                    organization=org,
                    defaults={
                        'max_consumption': 3.5,
                        'category': cat1,
                        'zone': zone1
                    }
                )
                
                Device.objects.get_or_create(
                    name='Luces LED',
                    organization=org,
                    defaults={
                        'max_consumption': 0.4,
                        'category': cat2,
                        'zone': zone1
                    }
                )
                
                self.stdout.write(self.style.SUCCESS('Datos cargados exitosamente'))
                self.stdout.write(f'Organizaciones: {Organization.objects.count()}')
                self.stdout.write(f'Categorías: {Category.objects.count()}')
                self.stdout.write(f'Zonas: {Zone.objects.count()}')
                self.stdout.write(f'Dispositivos: {Device.objects.count()}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))