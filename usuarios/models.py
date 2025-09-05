# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User
from monitoring.models import Organization

class UserProfile(models.Model):
    """
    Perfil de usuario que extiende el modelo User de Django
    y lo relaciona con una organización
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        help_text="Usuario de Django"
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        help_text="Empresa a la que pertenece el usuario"
    )
    phone = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Teléfono del usuario"
    )
    position = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Cargo en la empresa"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization.name}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"