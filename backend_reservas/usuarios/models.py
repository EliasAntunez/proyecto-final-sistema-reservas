from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Clase base Usuario que extiende AbstractUser
    """
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador del Complejo'),
    ]
    
    nombre = models.CharField(max_length=50, blank=False)
    apellido = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo_usuario = models.CharField(
        max_length=15,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente'
    )
    
    # Resolver conflictos de related_name con AbstractUser
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usuario_set',
        related_query_name='usuario'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usuario_set',
        related_query_name='usuario'
    )
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_usuario_display()}"
    
    def es_cliente(self):
        return self.tipo_usuario == 'cliente'
    
    def es_empleado(self):
        return self.tipo_usuario == 'empleado'
    
    def es_administrador(self):
        return self.tipo_usuario == 'administrador'
    
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()


class Cliente(Usuario):
    """
    Cliente: Se autoregistra, gestiona sus propias reservas
    """
    def save(self, *args, **kwargs):
        # Asegurar que el tipo sea cliente
        self.tipo_usuario = 'cliente'
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Administrador(Usuario):
    """
    Administrador del Complejo: Creado desde Django Admin por el desarrollador
    Gestiona empleados, espacios deportivos y configuración del complejo
    """
    
    def save(self, *args, **kwargs):
        # Asegurar que el tipo sea administrador
        self.tipo_usuario = 'administrador'
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Administrador del Complejo"
        verbose_name_plural = "Administradores de Complejo"