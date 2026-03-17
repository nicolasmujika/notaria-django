from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class ContactMessage(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} · {self.full_name} · {self.subject}"


class Service(models.Model):
    name = models.CharField(max_length=120)
    short_description = models.CharField(max_length=240, blank=True)
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    price_ref = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.id} · {self.name}"


class Tramite(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    requisitos = models.TextField(blank=True)
    precio_referencial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto en pesos chilenos (opcional)."
    )
    activo = models.BooleanField(default=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Trámite"
        verbose_name_plural = "Trámites"

    def __str__(self):
        return self.nombre


class Expediente(models.Model):
    ESTADOS = [
        ("recibido", "Recibido"),
        ("en_redaccion", "En redacción"),
        ("en_firma", "En firma"),
        ("listo_retiro", "Listo para retiro"),
        ("entregado", "Entregado"),
        ("anulado", "Anulado"),
    ]

    notificado_cliente = models.BooleanField(default=False)
    fecha_notificacion = models.DateTimeField(null=True, blank=True)

    solicitud = models.OneToOneField(
    "SolicitudEscritura",
    on_delete=models.CASCADE,
    related_name="expediente",
    null=True,
    blank=True
    )

    codigo_seguimiento = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    tipo = models.CharField(max_length=100)
    rut_cliente = models.CharField(
        max_length=12,
        blank=True,
        help_text="Ej: 11.111.111-1 (opcional)"
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="recibido")
    observaciones_publicas = models.TextField(blank=True)

    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Genera el código solo la primera vez
        if not self.codigo_seguimiento:
            ultimo = Expediente.objects.order_by("id").last()
            nuevo_id = 1 if not ultimo else ultimo.id + 1
            self.codigo_seguimiento = f"NOTA-{nuevo_id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo_seguimiento


class SolicitudEscritura(models.Model):
    TIPO_CHOICES = [
        ("compraventa", "Compraventa"),
        ("poder", "Poder"),
        ("arrendamiento", "Arrendamiento"),
        ("otros", "Otro tipo de escritura"),
    ]

    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    tipo_escritura = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField(
        help_text="Describe brevemente el motivo o antecedentes de la escritura."
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Escritura"
        verbose_name_plural = "Solicitudes de Escrituras"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_tipo_escritura_display()}"
    
class PerfilUsuario(models.Model):
    TIPO_CHOICES = [
        ("usuario", "Usuario"),
        ("funcionario", "Funcionario"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="usuario")
    rut = models.CharField(max_length=12, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"

class IndiceEscritura(models.Model):
    CAMPO_CHOICES = [
        ("comparecientes", "Comparecientes"),
        ("materia", "Materia"),
        ("repertorio", "N° Repertorio"),
        ("foja", "Foja"),
        ("anio", "Año"),
        ("todos", "Todos los campos"),
    ]

    comparecientes = models.TextField()
    materia = models.CharField(max_length=255)
    fecha = models.CharField(max_length=20, blank=True, help_text="Ej: 31-12")
    numero_repertorio = models.CharField(max_length=50, blank=True)
    foja = models.CharField(max_length=50, blank=True)
    anio = models.PositiveIntegerField()
    acto = models.CharField(max_length=100, blank=True)
    objeto = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-anio", "-numero_repertorio"]
        verbose_name = "Índice de Escritura Pública"
        verbose_name_plural = "Índices de Escrituras Públicas"

    def __str__(self):
        return f"{self.comparecientes[:60]} - {self.materia} ({self.anio})"
    

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, "perfil"):
        instance.perfil.save()