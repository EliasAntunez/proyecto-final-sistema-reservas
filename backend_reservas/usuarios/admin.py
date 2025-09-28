from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Cliente, Administrador

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'nombre', 'apellido', 'tipo_usuario', 'is_active')
    list_filter = ('tipo_usuario', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'nombre', 'apellido')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'telefono', 'tipo_usuario')
        }),
    )

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'nombre_completo', 'telefono', 'date_joined')
    search_fields = ('username', 'email', 'nombre', 'apellido')
    readonly_fields = ('tipo_usuario',)
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'telefono')
        }),
        ('Estado', {
            'fields': ('is_active', 'tipo_usuario')
        }),
    )

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'nombre_completo', 'is_active')  # Removí 'complejo_asignado'
    search_fields = ('username', 'email', 'nombre', 'apellido')
    readonly_fields = ('tipo_usuario',)
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'telefono')
        }),
        ('Estado', {
            'fields': ('is_active', 'tipo_usuario')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo administrador
            obj.set_password(form.cleaned_data.get('password', '123456'))
        super().save_model(request, obj, form, change)