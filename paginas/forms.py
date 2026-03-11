from django import forms # type: ignore
from .models import ContactMessage,Expediente, SolicitudEscritura
from django.core.exceptions import ValidationError

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
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "w-full border rounded p-2"}),
            "email": forms.EmailInput(attrs={"class": "w-full border rounded p-2"}),
            "phone": forms.TextInput(attrs={"class": "w-full border rounded p-2"}),
            "subject": forms.TextInput(attrs={"class": "w-full border rounded p-2"}),
            "message": forms.Textarea(attrs={"class": "w-full border rounded p-2", "rows": 5}),
        }
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
            "nombre_completo": forms.TextInput(attrs={"class": "w-full border rounded p-2"}),
            "email": forms.EmailInput(attrs={"class": "w-full border rounded p-2"}),
            "telefono": forms.TextInput(attrs={"class": "w-full border rounded p-2"}),
            "tipo_escritura": forms.Select(attrs={"class": "w-full border rounded p-2"}),
            "descripcion": forms.Textarea(attrs={"class": "w-full border rounded p-2", "rows": 5}),
        }