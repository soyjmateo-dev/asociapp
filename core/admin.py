from django.contrib import admin, messages
from .models import Organizacion, UsuarioOrganizacion
from django.core.management import call_command

@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activa", "fecha_creacion")
    search_fields = ("nombre", "slug")
    list_filter = ("activa",)
    actions = ["provisionar_base_datos"]

    
@admin.register(UsuarioOrganizacion)
class UsuarioOrganizacionAdmin(admin.ModelAdmin):
    list_display = ("user", "organizacion", "rol", "activa", "fecha_alta")
    list_filter = ("rol", "activa")
