from django import forms  # type: ignore
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

from .models import (
    ContactMessage,
    Expediente,
    SolicitudEscritura,
    IndiceEscritura,
    ValorServicio,
)


def validar_rut_chileno(value: str) -> str:
    if not value:
        return value

    rut = value.replace(".", "").replace("-", "").upper().strip()

    if len(rut) < 2:
        raise ValidationError("RUT inválido.")

    cuerpo, dv = rut[:-1], rut[-1]

    if not cuerpo.isdigit():
        raise ValidationError("RUT inválido.")

    suma = 0
    multiplo = 2
    for d in reversed(cuerpo):
        suma += int(d) * multiplo
        multiplo += 1
        if multiplo > 7:
            multiplo = 2

    resto = suma % 11
    dv_esperado = 11 - resto
    if dv_esperado == 11:
        dv_calc = "0"
    elif dv_esperado == 10:
        dv_calc = "K"
    else:
        dv_calc = str(dv_esperado)

    if dv_calc != dv:
        raise ValidationError("RUT inválido.")

    return f"{int(cuerpo)}-{dv}"


class ContactForm(forms.ModelForm):
    SUBJECT_CHOICES = [
        ("Consulta", "Consultas"),
        ("Reclamo", "Reclamos"),
        ("Sugerencia", "Sugerencias"),
    ]

    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select
    )

    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "phone", "subject", "message"]
        labels = {
            "full_name": "Nombre completo",
            "email": "Correo electrónico",
            "phone": "Teléfono",
            "subject": "Asunto",
            "message": "Mensaje",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_classes = (
            "w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 "
            "text-sm text-slate-900 placeholder-slate-400 shadow-sm transition "
            "focus:border-slate-400 focus:outline-none focus:ring-4 focus:ring-slate-200"
        )

        self.fields["full_name"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "Ingresa tu nombre completo",
            "autocomplete": "name",
        })
        self.fields["email"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "correo@ejemplo.com",
            "autocomplete": "email",
        })
        self.fields["phone"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "+56 9 1234 5678",
            "autocomplete": "tel",
        })
        self.fields["subject"].widget.attrs.update({
            "class": base_classes,
        })
        self.fields["message"].widget.attrs.update({
            "class": base_classes + " resize-none",
            "placeholder": "Escribe aquí tu mensaje...",
            "rows": 6,
        })

    def clean_honeypot(self):
        value = self.cleaned_data.get("honeypot")
        if value:
            raise forms.ValidationError("Bot detectado.")
        return value


class SeguimientoForm(forms.Form):
    codigo = forms.CharField(
        label="Código de seguimiento",
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "w-full border rounded p-2",
            "placeholder": "Ej: NOTA-000123",
        }),
    )
    rut = forms.CharField(
        label="RUT (opcional)",
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full border rounded p-2",
            "placeholder": "Ej: 11.111.111-1",
        }),
    )

    def clean_rut(self):
        rut = self.cleaned_data.get("rut", "").strip()
        if not rut:
            return rut
        return validar_rut_chileno(rut)


class SolicitudEscrituraForm(forms.ModelForm):
    class Meta:
        model = SolicitudEscritura
        fields = [
            "nombre_completo",
            "email",
            "telefono",
            "area",
            "tipo_escritura",
            "descripcion",
        ]
        labels = {
            "nombre_completo": "Nombre completo",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "area": "Área del trámite",
            "tipo_escritura": "Tipo de trámite",
            "descripcion": "Descripción / antecedentes",
        }
        widgets = {
            "nombre_completo": forms.TextInput(attrs={
                "placeholder": "Ingresa tu nombre completo"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "ejemplo@correo.com"
            }),
            "telefono": forms.TextInput(attrs={
                "placeholder": "+56 9 XXXX XXXX"
            }),
            "area": forms.Select(),
            "tipo_escritura": forms.Select(),
            "descripcion": forms.Textarea(attrs={
                "placeholder": "Describe brevemente el trámite que necesitas realizar"
            }),
        }


class RegistroUsuarioForm(forms.ModelForm):
    nombre_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nombre Completo"})
    )
    rut = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={"placeholder": "RUT (ej: 12345678-5)"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Correo Electrónico"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirmar Contraseña"})
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = []

    def clean_rut(self):
        rut = self.cleaned_data.get("rut", "").strip()
        return validar_rut_chileno(rut)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def save(self, commit=True):
        user = User()

        nombre_completo = self.cleaned_data["nombre_completo"].strip()
        partes = nombre_completo.split(" ", 1)

        email = self.cleaned_data["email"].strip().lower()

        user.first_name = partes[0]
        user.last_name = partes[1] if len(partes) > 1 else ""
        user.email = email
        user.username = email
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            user.perfil.tipo = "usuario"
            user.perfil.rut = self.cleaned_data["rut"]
            user.perfil.save()

        return user


class LoginUsuarioForm(AuthenticationForm):
    username = forms.CharField(
        label="Correo Electrónico",
        widget=forms.TextInput(attrs={"placeholder": "Correo Electrónico"})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Contraseña"})
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class ExpedienteGestionForm(forms.ModelForm):
    class Meta:
        model = Expediente
        fields = ["rut_cliente", "estado", "observaciones_publicas"]
        widgets = {
            "rut_cliente": forms.TextInput(attrs={
                "class": "w-full border rounded p-2",
                "placeholder": "Ej: 11.111.111-1"
            }),
            "estado": forms.Select(attrs={
                "class": "w-full border rounded p-2"
            }),
            "observaciones_publicas": forms.Textarea(attrs={
                "class": "w-full border rounded p-2",
                "rows": 4,
                "placeholder": "Comentario visible para el cliente"
            }),
        }

    def clean_rut_cliente(self):
        rut = self.cleaned_data.get("rut_cliente", "").strip()
        if not rut:
            return rut
        return validar_rut_chileno(rut)


class IndiceEscrituraForm(forms.ModelForm):
    class Meta:
        model = IndiceEscritura
        fields = [
            "comparecientes",
            "materia",
            "acto",
            "objeto",
            "fecha",
            "numero_repertorio",
            "foja",
            "anio",
        ]
        widgets = {
            "comparecientes": forms.Textarea(attrs={
                "class": "indice-input indice-textarea indice-textarea-sm",
                "rows": 3,
                "placeholder": "Ej: Juan Pérez / María Soto",
            }),
            "materia": forms.TextInput(attrs={
                "class": "indice-input",
                "placeholder": "Resumen de la materia",
            }),
            "acto": forms.TextInput(attrs={
                "class": "indice-input",
                "placeholder": "Ej: Compraventa, Permuta",
            }),
            "objeto": forms.Textarea(attrs={
                "class": "indice-input indice-textarea",
                "rows": 4,
                "placeholder": "Detalle del objeto o antecedente",
            }),
            "fecha": forms.TextInput(attrs={
                "class": "indice-input",
                "placeholder": "Ej: 31-12 o dejar vacío",
            }),
            "numero_repertorio": forms.TextInput(attrs={
                "class": "indice-input",
                "placeholder": "Ej: 1234",
            }),
            "foja": forms.TextInput(attrs={
                "class": "indice-input",
                "placeholder": "Ej: 56",
            }),
            "anio": forms.NumberInput(attrs={
                "class": "indice-input",
                "placeholder": "Ej: 2022",
                "min": "1900",
                "max": "2100",
            }),
        }


class ValorServicioForm(forms.ModelForm):
    class Meta:
        model = ValorServicio
        fields = [
            "categoria",
            "nombre",
            "tramite_codigo",
            "valor",
            "descripcion_corta",
            "descripcion_larga",
            "orden",
            "activo",
            "mostrar_valor",
        ]
        widgets = {
            "categoria": forms.TextInput(attrs={
                "class": "gv-input",
                "placeholder": "Ej: Escrituras Públicas"
            }),
            "nombre": forms.TextInput(attrs={
                "class": "gv-input",
                "placeholder": "Ej: Compraventa"
            }),
            "tramite_codigo": forms.TextInput(attrs={
                "class": "gv-input",
                "placeholder": "Ej: compraventa"
            }),
            "valor": forms.TextInput(attrs={
                "class": "gv-input",
                "placeholder": "Ej: $45.000 + imp."
            }),
            "descripcion_corta": forms.Textarea(attrs={
                "class": "gv-input",
                "rows": 3,
                "placeholder": "Texto corto visible en la tarjeta"
            }),
            "descripcion_larga": forms.Textarea(attrs={
                "class": "gv-input",
                "rows": 6,
                "placeholder": "Texto más completo para el detalle"
            }),
            "orden": forms.NumberInput(attrs={
                "class": "gv-input",
                "min": "0"
            }),
        }


class SolicitarRecuperacionForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "Ingresa tu correo"})
    )
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class VerificarCodigoRecuperacionForm(forms.Form):
    codigo = forms.CharField(
        max_length=6,
        label="Código de verificación",
        widget=forms.TextInput(attrs={"placeholder": "123456"})
    )


class RestablecerClaveForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Nueva contraseña"})
    )
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirmar nueva contraseña"})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data