from django.contrib import admin # type: ignore
from .models import ContactMessage, Service, Tramite, Expediente, SolicitudEscritura

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "subject", "created_at")
    search_fields = ("full_name", "email", "subject", "message")
    list_filter = ("created_at",)
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "updated_at", "price_ref")
    list_filter = ("is_active",)
    search_fields = ("name", "short_description", "description", "requirements")

@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "categoria", "precio_referencial", "activo")
    list_filter = ("activo", "categoria")
    search_fields = ("nombre", "descripcion", "requisitos")

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ("codigo_seguimiento", "tipo", "rut_cliente", "estado", "fecha_ingreso")
    list_filter = ("estado", "tipo", "fecha_ingreso")
    search_fields = ("codigo_seguimiento", "rut_cliente")

@admin.register(SolicitudEscritura)
class SolicitudEscrituraAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_completo", "tipo_escritura", "email", "creado_en")
    list_filter = ("tipo_escritura", "creado_en")
    search_fields = ("nombre_completo", "email")