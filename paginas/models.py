from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ("Consulta", "Consulta"),
        ("Reclamo", "Reclamo"),
        ("Sugerencia", "Sugerencia"),
    ]
    
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    replied = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages_replied",
    )

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
    AREA_CHOICES = [
        ("notaria", "Notaría"),
        ("conservador", "Conservador"),
    ]

    TIPO_CHOICES = [
        # Notaría
        ("compraventa", "Compraventa"),
        ("poder", "Poder"),
        ("arrendamiento", "Arrendamiento"),
        ("alzamiento", "Alzamiento"),
        ("mutuo", "Mutuo"),
        ("hipoteca", "Hipoteca"),
        ("prenda", "Prenda"),
        ("resciliacion", "Resciliación"),
        ("otros_notaria", "Otro trámite notarial"),

        # Conservador
        ("inscripcion_dominio", "Inscripción de dominio"),
        ("hipotecas_gravamenes", "Hipotecas y gravámenes"),
        ("interdicciones_prohibiciones", "Interdicciones y prohibiciones"),
        ("certificados", "Certificados"),
        ("archivo_documentos", "Archivo de documentos"),
        ("copias_inscripciones", "Copias de inscripciones"),
        ("otros_conservador", "Otro trámite de conservador"),
    ]

    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)

    area = models.CharField(
        max_length=20,
        choices=AREA_CHOICES,
        default="notaria"
    )

    tipo_escritura = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES
    )

    descripcion = models.TextField(
        help_text="Describe brevemente el motivo o antecedentes del trámite."
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Trámite"
        verbose_name_plural = "Solicitudes de Trámites"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_area_display()} - {self.get_tipo_escritura_display()}"
    
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


class ValorServicio(models.Model):
    categoria = models.CharField(max_length=100)
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    icono = models.CharField(max_length=20, blank=True, default="📄")
    valor = models.CharField(max_length=100)
    descripcion_corta = models.TextField(blank=True, default="")
    descripcion_larga = models.TextField(blank=True, default="")
    tramite_codigo = models.CharField(max_length=50, blank=True, default="")
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    mostrar_valor = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["categoria", "orden", "nombre"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.valor}"

class VerificacionCorreo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="verificacion_correo")
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    vence_en = models.DateTimeField()
    intentos = models.PositiveIntegerField(default=0)
    verificado = models.BooleanField(default=False)

    def esta_vencido(self):
        return timezone.now() > self.vence_en

    def __str__(self):
        return f"Verificación de {self.user.username}"

class RecuperacionClave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recuperaciones_clave")
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    vence_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    intentos = models.PositiveIntegerField(default=0)

    def esta_vencido(self):
        return timezone.now() > self.vence_en

    def __str__(self):
        return f"Recuperación de {self.user.email}"

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, "perfil"):
        instance.perfil.save()

def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.nombre)
    super().save(*args, **kwargs)