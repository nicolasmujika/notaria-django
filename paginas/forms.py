from django import forms # type: ignore
from .models import ContactMessage,Expediente, SolicitudEscritura
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

def validar_rut_chileno(value: str) -> str:
   
    if not value:
        return value

    rut = value.replace(".", "").replace("-", "").upper().strip()

    if len(rut) < 2:
        raise ValidationError("RUT inválido.")

    cuerpo, dv = rut[:-1], rut[-1]

    if not cuerpo.isdigit():
        raise ValidationError("RUT inválido.")

    # cálculo dígito verificador
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
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

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
            "placeholder": "Motivo de tu mensaje",
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
# importa Escritura si la vas a usar después, por ahora no es necesario aquí


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
        fields = ["nombre_completo", "email", "telefono", "tipo_escritura", "descripcion"]
        widgets = {
            "nombre_completo": forms.TextInput(attrs={"placeholder": "Ingresa tu nombre completo"}),
            "email": forms.EmailInput(attrs={"placeholder": "ejemplo@correo.com"}),
            "telefono": forms.TextInput(attrs={"placeholder": "+56 9 XXXX XXXX"}),
            "tipo_escritura": forms.Select(),
            "descripcion": forms.Textarea(attrs={"placeholder": "Describe brevemente el trámite que necesitas realizar"}),
        }

class RegistroUsuarioForm(forms.ModelForm):
    nombre_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nombre Completo"})
    )
    rut = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={"placeholder": "RUT"})
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
    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        nombre_completo = self.cleaned_data["nombre_completo"]
        partes = nombre_completo.strip().split(" ", 1)
        user.first_name = partes[0]
        user.last_name = partes[1] if len(partes) > 1 else ""
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
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