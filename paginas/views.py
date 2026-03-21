import random
from django.core.mail import send_mail # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib import messages# type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings# type: ignore
from .forms import (ContactForm, SeguimientoForm,SolicitudEscrituraForm,RegistroUsuarioForm, LoginUsuarioForm, ExpedienteGestionForm,
    IndiceEscrituraForm, ValorServicioForm,SolicitarRecuperacionForm,
    VerificarCodigoRecuperacionForm,
    RestablecerClaveForm)
from .models import (Service, Tramite, Expediente,SolicitudEscritura,
 IndiceEscritura, ContactMessage, ValorServicio, VerificacionCorreo, RecuperacionClave)
from django.utils import timezone # type: ignore
from datetime import timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q

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


def servicios_notariales(request):
    return render(request, 'pages/servicios_notariales.html')

def escrituras_publicas(request):
    servicios = ValorServicio.objects.filter(
        categoria="Escrituras Públicas",
        activo=True
    ).order_by("orden", "nombre")

    return render(request, "pages/escrituras_publicas.html", {
        "servicios": servicios,
    })

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
    servicios = ValorServicio.objects.filter(
        categoria="Documentos Privados",
        activo=True
    ).order_by("orden", "nombre")

    return render(request, "pages/documentos_privados.html", {
        "servicios": servicios,
    })

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


class CustomLoginView(LoginView):
    template_name = "pages/login.html"
    authentication_form = LoginUsuarioForm

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_active:
            messages.warning(self.request, "Debes verificar tu correo antes de iniciar sesión.")
            return redirect("verificar_correo", user_id=user.id)

        login(self.request, user)

        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url:
            return redirect(next_url)

        if hasattr(user, "perfil") and user.perfil.tipo == "funcionario":
            return redirect("panel_funcionario")

        return redirect("home")

    def form_invalid(self, form):
        if "captcha" in form.errors:
            messages.error(self.request, "Por favor, marca el reCAPTCHA.")
        elif "__all__" in form.errors:
            messages.error(self.request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(self.request, "Revisa los datos ingresados.")

        return self.render_to_response(self.get_context_data(form=form))
def registro_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                user.perfil.tipo = "usuario"
                user.perfil.rut = form.cleaned_data["rut"]
                user.perfil.save()

                codigo = generar_codigo_verificacion()

                VerificacionCorreo.objects.update_or_create(
                    user=user,
                    defaults={
                        "codigo": codigo,
                        "vence_en": obtener_fecha_vencimiento(10),
                        "intentos": 0,
                        "verificado": False,
                    }
                )

                enviar_codigo_verificacion(user.email, codigo)

                messages.success(
                    request,
                    "Tu cuenta fue creada. Te enviamos un código de verificación a tu correo."
                )
                return redirect("verificar_correo", user_id=user.id)

            except Exception as e:
                messages.error(request, f"No se pudo crear la cuenta o enviar el correo: {e}")
        else:
            print(form.errors)
            messages.error(request, "No se pudo crear la cuenta. Revisa los campos.")
    else:
        form = RegistroUsuarioForm()

    return render(request, "pages/registro.html", {"form": form})

def verificar_correo(request, user_id):
    user = get_object_or_404(User, id=user_id)
    verificacion = get_object_or_404(VerificacionCorreo, user=user)

    if verificacion.verificado:
        messages.info(request, "Tu correo ya fue verificado.")
        return redirect("login")

    if request.method == "POST":
        codigo_ingresado = request.POST.get("codigo", "").strip()

        if verificacion.esta_vencido():
            messages.error(request, "El código venció. Solicita uno nuevo.")
            return redirect("verificar_correo", user_id=user.id)

        if verificacion.intentos >= 5:
            messages.error(request, "Superaste el máximo de intentos. Solicita un nuevo código.")
            return redirect("reenviar_codigo", user_id=user.id)

        if codigo_ingresado == verificacion.codigo:
            user.is_active = True
            user.save(update_fields=["is_active"])

            verificacion.verificado = True
            verificacion.save(update_fields=["verificado"])

            messages.success(request, "Correo verificado correctamente. Ya puedes iniciar sesión.")
            return redirect("login")

        verificacion.intentos += 1
        verificacion.save(update_fields=["intentos"])
        messages.error(request, "Código incorrecto.")

    return render(request, "pages/verificar_correo.html", {
        "user_id": user.id,
        "email": user.email,
        "vence_en": verificacion.vence_en,
    })

def reenviar_codigo(request, user_id):
    user = get_object_or_404(User, id=user_id)
    verificacion = get_object_or_404(VerificacionCorreo, user=user)

    if user.is_active or verificacion.verificado:
        messages.info(request, "La cuenta ya está verificada.")
        return redirect("login")

    nuevo_codigo = generar_codigo_verificacion()

    verificacion.codigo = nuevo_codigo
    verificacion.vence_en = obtener_fecha_vencimiento(10)
    verificacion.intentos = 0
    verificacion.verificado = False
    verificacion.save()

    try:
        enviar_codigo_verificacion(user.email, nuevo_codigo)
        messages.success(request, "Te enviamos un nuevo código.")
    except Exception as e:
        messages.error(request, f"No se pudo reenviar el código: {e}")

    return redirect("verificar_correo", user_id=user.id)


def logout_view(request):
    logout(request)
    return redirect("home")

def es_funcionario(user):
    return user.is_authenticated and hasattr(user, "perfil") and user.perfil.tipo == "funcionario"





@login_required
@user_passes_test(es_funcionario)
def panel_funcionario(request):
    solicitudes = (
        SolicitudEscritura.objects
        .filter(expediente__isnull=True)
        .order_by("-creado_en")
    )

    expedientes_lista = (
        Expediente.objects
        .select_related("solicitud")
        .order_by("-fecha_ingreso")
    )

    mensajes_contacto = ContactMessage.objects.order_by("-created_at")[:20]
    
    paginator = Paginator(expedientes_lista, 10)
    page_number = request.GET.get("page")
    expedientes = paginator.get_page(page_number)

    context = {
        "solicitudes": solicitudes,
        "expedientes": expedientes,
        "mensajes_contacto": mensajes_contacto,
        "total_solicitudes": SolicitudEscritura.objects.count(),
        "total_expedientes": Expediente.objects.count(),
        "solicitudes_pendientes": SolicitudEscritura.objects.filter(expediente__isnull=True).count(),
        "total_mensajes_contacto": ContactMessage.objects.count(),
    }

    return render(request, "pages/panel_funcionario.html", context)

@login_required
@user_passes_test(es_funcionario)
def crear_expediente_desde_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudEscritura, id=solicitud_id)

    if hasattr(solicitud, "expediente"):
        messages.warning(request, "Esta solicitud ya tiene un expediente asociado.")
        return redirect("panel_funcionario")

    expediente = Expediente.objects.create(
        solicitud=solicitud,
        tipo=solicitud.get_tipo_escritura_display(),
        rut_cliente="",
        estado="recibido",
        observaciones_publicas=""
    )

    messages.success(
        request,
        f"Expediente {expediente.codigo_seguimiento} creado correctamente."
    )
    return redirect("panel_funcionario")

@login_required
@user_passes_test(es_funcionario)
def editar_expediente(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)

    if request.method == "POST":
        form = ExpedienteGestionForm(request.POST, instance=expediente)
        if form.is_valid():
            form.save()
            messages.success(request, "Expediente actualizado correctamente.")
            return redirect("panel_funcionario")
    else:
        form = ExpedienteGestionForm(instance=expediente)

    return render(request, "pages/editar_expediente.html", {
        "expediente": expediente,
        "form": form,
    })


@login_required
@user_passes_test(es_funcionario)
def notificar_expediente_listo(request, expediente_id):
    expediente = get_object_or_404(Expediente, id=expediente_id)

    if not expediente.solicitud or not expediente.solicitud.email:
        messages.error(request, "Este expediente no tiene un correo asociado para notificar.")
        return redirect("panel_funcionario")

    asunto = f"Su escritura {expediente.codigo_seguimiento} está lista"
    mensaje = (
        f"Estimado/a {expediente.solicitud.nombre_completo},\n\n"
        f"Le informamos que su escritura asociada al código {expediente.codigo_seguimiento} "
        f"se encuentra actualmente en estado: {expediente.get_estado_display()}.\n\n"
        f"Observaciones:\n"
        f"{expediente.observaciones_publicas or 'Sin observaciones adicionales.'}\n\n"
        f"Si necesita más información, puede responder este correo o contactarse con la notaría.\n\n"
        f"Saludos,\n"
        f"Notaría Felipe Velásquez"
    )

    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[expediente.solicitud.email],
        fail_silently=False,
    )

    expediente.notificado_cliente = True
    expediente.fecha_notificacion = timezone.now()
    expediente.save(update_fields=["notificado_cliente", "fecha_notificacion"])

    messages.success(request, f"Se notificó al cliente en {expediente.solicitud.email}.")
    return redirect("panel_funcionario")

@login_required
def indices_escrituras(request):
    q = request.GET.get("q", "").strip()
    campo = request.GET.get("campo", "todos")
    anio = request.GET.get("anio", "").strip()

    indices = IndiceEscritura.objects.all()

    if anio:
        indices = indices.filter(anio=anio)

    if q:
        if campo == "comparecientes":
            indices = indices.filter(comparecientes__icontains=q)
        elif campo == "materia":
            indices = indices.filter(materia__icontains=q)
        elif campo == "repertorio":
            indices = indices.filter(numero_repertorio__icontains=q)
        elif campo == "foja":
            indices = indices.filter(foja__icontains=q)
        elif campo == "anio":
            indices = indices.filter(anio__icontains=q)
        else:
            indices = indices.filter(
                Q(comparecientes__icontains=q) |
                Q(materia__icontains=q) |
                Q(numero_repertorio__icontains=q) |
                Q(foja__icontains=q) |
                Q(anio__icontains=q)
            )

    anios = (
        IndiceEscritura.objects
        .values_list("anio", flat=True)
        .distinct()
        .order_by("-anio")
    )

    paginator = Paginator(indices, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "q": q,
        "campo": campo,
        "anio": anio,
        "anios": anios,
        "total_registros": indices.count(),
    }
    return render(request, "pages/indices_escrituras.html", context)

@login_required
@user_passes_test(es_funcionario)
def gestion_indices(request):
    indices = IndiceEscritura.objects.all().order_by("-anio", "foja", "numero_repertorio")
    return render(request, "pages/gestion_indices.html", {
        "indices": indices
    })


@login_required
@user_passes_test(es_funcionario)
def crear_indice(request):
    if request.method == "POST":
        form = IndiceEscrituraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Índice creado correctamente.")
            return redirect("gestion_indices")
    else:
        form = IndiceEscrituraForm()

    return render(request, "pages/editar_indice.html", {
        "form": form,
        "titulo": "Crear índice",
    })


@login_required
@user_passes_test(es_funcionario)
def editar_indice(request, indice_id):
    indice = get_object_or_404(IndiceEscritura, id=indice_id)

    if request.method == "POST":
        form = IndiceEscrituraForm(request.POST, instance=indice)
        if form.is_valid():
            form.save()
            messages.success(request, "Índice actualizado correctamente.")
            return redirect("gestion_indices")
    else:
        form = IndiceEscrituraForm(instance=indice)

    return render(request, "pages/editar_indice.html", {
        "form": form,
        "titulo": "Editar índice",
        "indice": indice,
    })

@login_required
@user_passes_test(es_funcionario)
def gestionar_valores(request):
    valores = ValorServicio.objects.all()
    return render(request, "pages/gestionar_valores.html", {"valores": valores})


@login_required
@user_passes_test(es_funcionario)
def editar_valor(request, valor_id):
    valor = get_object_or_404(ValorServicio, id=valor_id)

    if request.method == "POST":
        form = ValorServicioForm(request.POST, instance=valor)
        if form.is_valid():
            form.save()
            messages.success(request, "Valor actualizado correctamente.")
            return redirect("gestionar_valores")
    else:
        form = ValorServicioForm(instance=valor)

    return render(request, "pages/editar_valor.html", {
        "form": form,
        "valor": valor
    })

@login_required
def responder_mensaje_contacto(request, mensaje_id):
    if request.method != "POST":
        return redirect("panel_funcionario")

    mensaje = get_object_or_404(ContactMessage, id=mensaje_id)

    respuesta = request.POST.get("respuesta", "").strip()

    if not respuesta:
        messages.error(request, "La respuesta no puede ir vacía.")
        return redirect("panel_funcionario")

    asunto = f"Respuesta a tu {mensaje.subject.lower()} - Notaría Felipe Velásquez"

    cuerpo = f"""
Hola {mensaje.full_name},

Te escribimos en respuesta al mensaje que enviaste a través del formulario de contacto de la notaría.

Tu mensaje fue:
"{mensaje.message}"

Nuestra respuesta:
{respuesta}

Saludos cordiales,
Notaría Felipe Velásquez
""".strip()

    try:
        send_mail(
            subject=asunto,
            message=cuerpo,
            from_email=None,  # usa DEFAULT_FROM_EMAIL
            recipient_list=[mensaje.email],
            fail_silently=False,
        )

        mensaje.replied = True
        mensaje.reply_message = respuesta
        mensaje.replied_at = timezone.now()
        mensaje.replied_by = request.user
        mensaje.save()

        messages.success(request, f"Respuesta enviada correctamente a {mensaje.email}.")
    except Exception as e:
        messages.error(request, f"No se pudo enviar el correo: {e}")

    return redirect("panel_funcionario")

@login_required
@user_passes_test(es_funcionario)
def eliminar_mensaje_contacto(request, mensaje_id):
    if request.method != "POST":
        return redirect("panel_funcionario")

    mensaje = get_object_or_404(ContactMessage, id=mensaje_id)

    if not mensaje.replied:
        messages.error(request, "Solo puedes eliminar mensajes que ya fueron respondidos.")
        return redirect("panel_funcionario")

    nombre = mensaje.full_name
    correo = mensaje.email
    mensaje.delete()

    messages.success(
        request,
        f"El mensaje de {nombre} ({correo}) fue eliminado correctamente."
    )
    return redirect("panel_funcionario")

def generar_codigo_verificacion():
    return f"{random.randint(0, 999999):06d}"


def obtener_fecha_vencimiento(minutos=10):
    return timezone.now() + timedelta(minutes=minutos)


def enviar_codigo_verificacion(destinatario, codigo):
    asunto = "Código de verificación de correo"
    mensaje = (
        f"Hola,\n\n"
        f"Tu código de verificación es: {codigo}\n\n"
        f"Este código vence en 10 minutos.\n\n"
        f"Si no solicitaste este registro, ignora este correo."
    )

    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destinatario],
        fail_silently=False,
    )
def enviar_codigo_recuperacion(destinatario, codigo):
    asunto = "Recuperación de contraseña"
    mensaje = (
        f"Hola,\n\n"
        f"Tu código para restablecer tu contraseña es: {codigo}\n\n"
        f"Este código vence en 10 minutos.\n\n"
        f"Si no solicitaste este cambio, ignora este correo."
    )

    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[destinatario],
        fail_silently=False,
    )

def olvide_clave(request):
    if request.method == "POST":
        form = SolicitarRecuperacionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()

            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                messages.error(request, "No existe una cuenta asociada a ese correo.")
                return render(request, "pages/olvide_clave.html", {"form": form})

            codigo = generar_codigo_verificacion()

            RecuperacionClave.objects.filter(user=user, usado=False).update(usado=True)

            RecuperacionClave.objects.create(
                user=user,
                codigo=codigo,
                vence_en=obtener_fecha_vencimiento(10),
                intentos=0,
            )

            try:
                enviar_codigo_recuperacion(user.email, codigo)
                messages.success(request, "Te enviamos un código para recuperar tu contraseña.")
                return redirect("verificar_codigo_recuperacion", user_id=user.id)
            except Exception as e:
                messages.error(request, f"No se pudo enviar el correo: {e}")
    else:
        form = SolicitarRecuperacionForm()

    return render(request, "pages/olvide_clave.html", {"form": form})

def verificar_codigo_recuperacion(request, user_id):
    user = get_object_or_404(User, id=user_id)

    recuperacion = (
        RecuperacionClave.objects
        .filter(user=user, usado=False)
        .order_by("-creado_en")
        .first()
    )

    if not recuperacion:
        messages.error(request, "No hay una solicitud de recuperación activa.")
        return redirect("olvide_clave")

    if request.method == "POST":
        form = VerificarCodigoRecuperacionForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data["codigo"].strip()

            if recuperacion.esta_vencido():
                messages.error(request, "El código venció. Solicita uno nuevo.")
                return redirect("olvide_clave")

            if recuperacion.intentos >= 5:
                messages.error(request, "Superaste el máximo de intentos. Solicita uno nuevo.")
                return redirect("olvide_clave")

            if codigo != recuperacion.codigo:
                recuperacion.intentos += 1
                recuperacion.save(update_fields=["intentos"])
                messages.error(request, "Código incorrecto.")
                return render(request, "pages/verificar_codigo_recuperacion.html", {
                    "form": form,
                    "user_id": user.id,
                    "email": user.email,
                })

            request.session["recuperacion_user_id"] = user.id
            request.session["recuperacion_codigo_ok"] = True

            messages.success(request, "Código verificado correctamente.")
            return redirect("restablecer_clave")
    else:
        form = VerificarCodigoRecuperacionForm()

    return render(request, "pages/verificar_codigo_recuperacion.html", {
        "form": form,
        "user_id": user.id,
        "email": user.email,
    })

def restablecer_clave(request):
    user_id = request.session.get("recuperacion_user_id")
    codigo_ok = request.session.get("recuperacion_codigo_ok")

    if not user_id or not codigo_ok:
        messages.error(request, "Primero debes validar tu código de recuperación.")
        return redirect("olvide_clave")

    user = get_object_or_404(User, id=user_id)

    recuperacion = (
        RecuperacionClave.objects
        .filter(user=user, usado=False)
        .order_by("-creado_en")
        .first()
    )

    if not recuperacion or recuperacion.esta_vencido():
        messages.error(request, "La recuperación ya no es válida. Solicita una nueva.")
        return redirect("olvide_clave")

    if request.method == "POST":
        form = RestablecerClaveForm(request.POST)
        if form.is_valid():
            nueva_clave = form.cleaned_data["password1"]
            user.set_password(nueva_clave)
            user.save()

            recuperacion.usado = True
            recuperacion.save(update_fields=["usado"])

            request.session.pop("recuperacion_user_id", None)
            request.session.pop("recuperacion_codigo_ok", None)

            messages.success(request, "Tu contraseña fue actualizada correctamente.")
            return redirect("login")
    else:
        form = RestablecerClaveForm()

    return render(request, "pages/restablecer_clave.html", {"form": form})