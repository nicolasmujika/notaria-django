from django.core.mail import send_mail # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib import messages# type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings# type: ignore
from .forms import ContactForm, SeguimientoForm,SolicitudEscrituraForm
from .models import Service, Tramite, Expediente,SolicitudEscritura
from django.utils import timezone # type: ignore
from datetime import timedelta

def home(request):
    return render(request, "pages/home.html")

def contact(request):
    # Rate limit básico: máximo 1 mensaje cada 30 segundos por sesión
    now = timezone.now()
    last_post = request.session.get("last_contact_post")
    if request.method == "POST" and last_post:
        last = timezone.datetime.fromisoformat(last_post)
        if now - last < timedelta(seconds=30):
            messages.error(request, "Espera unos segundos antes de enviar otro mensaje.")
            return redirect("contact")

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            obj = form.save()

            body = (
                f"Nuevo mensaje de contacto (ID {obj.id}):\n\n"
                f"Nombre: {obj.full_name}\n"
                f"Email: {obj.email}\n"
                f"Teléfono: {obj.phone}\n"
                f"Asunto: {obj.subject}\n\n"
                f"Mensaje:\n{obj.message}\n"
            )

            send_mail(
                subject=f"[Contacto Notaría] {obj.subject}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECIPIENT],
                fail_silently=False,
            )

            # guarda timestamp para rate limit
            request.session["last_contact_post"] = now.isoformat()

            messages.success(request, "Tu mensaje fue enviado correctamente.")
            return redirect("contact")
    else:
        form = ContactForm()

    context = {
        "form": form,
        "address": "Dirección de la Notaría, Ciudad",
        "hours": [
            ("Lunes a Viernes", "09:00–14:00 / 15:30–18:00"),
            ("Sábado", "09:00–13:00"),
        ],
        "phone_display": "+56 32 123 4567",
        "email_display": "contacto@notaria.local",
        "gmap_embed": "https://www.google.com/maps/embed?pb=TU_EMBED_AQUI",
    }
    return render(request, "pages/contact.html", context)

def services_list(request):
    q = request.GET.get("q", "").strip()
    qs = Service.objects.filter(is_active=True)
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, "pages/tramites_list.html", {"items": qs, "q": q})

def service_detail(request, id: int):
    obj = get_object_or_404(Service, pk=id, is_active=True)
    return render(request, "pages/tramite_detail.html", {"obj": obj})

def quienes_somos(request):
    return render(request, 'pages/quienes_somos.html')



def horario_atencion(request):
    return render(request, 'pages/horario_atencion.html')

def tramites_comunes(request):
    return render(request, 'pages/tramites_comunes.html')

def preguntas_frecuentes(request):
    return render(request, 'pages/preguntas_frecuentes.html')

def enlaces_interes(request):
    return render(request, 'pages/enlaces_interes.html')

def servicios_notariales(request):
    return render(request, 'pages/servicios_notariales.html')

def escrituras_publicas(request):
    return render(request, 'pages/escrituras_publicas.html')

def solicitud_escrituras(request):
    if request.method == "POST":
        form = SolicitudEscrituraForm(request.POST)
        if form.is_valid():
            obj = form.save()

            # cuerpo del correo para la notaría
            body = (
                f"Nueva solicitud de escritura (ID {obj.id}):\n\n"
                f"Nombre: {obj.nombre_completo}\n"
                f"Email: {obj.email}\n"
                f"Teléfono: {obj.telefono}\n"
                f"Tipo de escritura: {obj.get_tipo_escritura_display()}\n\n"
                f"Descripción:\n{obj.descripcion}\n"
            )

            send_mail(
                subject=f"[Solicitud Escritura] {obj.get_tipo_escritura_display()}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECIPIENT],
                fail_silently=False,
            )

            messages.success(
                request,
                "Tu solicitud fue enviada correctamente. Nos pondremos en contacto contigo."
            )
            return redirect("solicitud_escrituras")
    else:
        form = SolicitudEscrituraForm()

    return render(request, "pages/solicitud_escrituras.html", {"form": form})


def validar_documentos(request):
    return render(request, 'pages/validar_documentos.html')

def seguimiento_escrituras(request):
    return render(request, 'pages/seguimiento_escrituras.html')

def notaria_en_linea(request):
    return render(request, 'pages/notaria_en_linea.html')

from .models import Tramite

def tramites_list(request):
    tramites = Tramite.objects.filter(activo=True).order_by("nombre")
    return render(request, "pages/tramites_list.html", {"tramites": tramites})


def tramite_detail(request, tramite_id: int):
    tramite = Tramite.objects.get(pk=tramite_id)
    return render(request, "pages/tramite_detail.html", {"tramite": tramite})

def documentos_privados(request):
    return render(request, 'pages/documentos_privados.html')

def seguimiento_escrituras(request):
    resultado = None
    error = None

    if request.method == "POST":
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data["codigo"].strip()
            rut = form.cleaned_data["rut"].strip()

            qs = Expediente.objects.filter(codigo_seguimiento__iexact=codigo)
            if rut:
                qs = qs.filter(rut_cliente__iexact=rut)

            if qs.exists():
                resultado = qs.first()
            else:
                error = "No se encontró ninguna escritura con los datos ingresados."
    else:
        form = SeguimientoForm()

    context = {
        "form": form,
        "resultado": resultado,
        "error": error,
    }
    return render(request, "pages/seguimiento_escrituras.html", context)
