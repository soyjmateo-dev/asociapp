from django import forms
from asociaciones.models import Socio, Familia, Inscripcion, Pago, Cuota, Comunicacion, Organismo, TipoComunicacion
from asociaciones.models import Contacto, TipoContacto, ItemInventario, CategoriaInventario, ArchivoInventario
from datetime import date


class SocioForm(forms.ModelForm):

    class Meta:
        model = Socio
        fields = [
            "activo",
            "nombre",
            "apellidos",
            "fecha_nacimiento",
            "familia",
            "en_whatsapp",
            "es_colaborador",
            "email",
            "telefono",
            "proteccion_datos",
            "acepta_fotografias",
        ]

        widgets = {
            "fecha_nacimiento": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            )
        }

    def __init__(self, *args, organizacion=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar familias por organización
        if organizacion and "familia" in self.fields:
            self.fields["familia"].queryset = Familia.objects.filter(
                organizacion=organizacion
            )

        # Aplicar clases CSS
        for name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    "class": "form-check-input"
                })

            else:
                # No sobrescribir si ya tiene clase
                css = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{css} form-control".strip()

        # Asegurar formato correcto cuando se edita un socio existente
        if self.instance and self.instance.pk and self.instance.fecha_nacimiento:
            self.initial["fecha_nacimiento"] = self.instance.fecha_nacimiento.strftime("%Y-%m-%d")

    def clean(self):
        cleaned_data = super().clean()

        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")
        familia = cleaned_data.get("familia")

        if fecha_nacimiento:

            hoy = date.today()

            edad = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) <
                (fecha_nacimiento.month, fecha_nacimiento.day)
            )

            # Regla: menores deben tener familia
            if edad < 18 and not familia:
                self.add_error(
                    "familia",
                    "Los menores de edad deben pertenecer a una familia."
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        return instance
    
from django import forms
from .models import Actividad


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = [
            "nombre",
            "descripcion",
            "fecha",
            "cupo_maximo",
            "coste_adulto",
            "coste_menor",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
            "fecha": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "cupo_maximo": forms.NumberInput(attrs={
                "class": "form-control"
            }),
            "coste_adulto": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "coste_menor": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
        }

from django import forms
from asociaciones.models import Inscripcion, Socio

class InscripcionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        organizacion = kwargs.pop("organizacion", None)
        actividad = kwargs.pop("actividad", None)
        super().__init__(*args, **kwargs)

        if organizacion and actividad:

            # IDs ya inscritos
            inscritos_ids = actividad.inscripciones.values_list(
                "socio_id", flat=True
            )

            # Solo activos y NO inscritos
            self.fields["socio"].queryset = Socio.objects.filter(
                organizacion=organizacion,
                activo=True
            ).exclude(id__in=inscritos_ids)

        self.fields["socio"].widget.attrs.update({
            "class": "form-select select2"
        })

    class Meta:
        model = Inscripcion
        fields = ["socio"]

class PagoForm(forms.ModelForm):

    actividad = forms.ModelChoiceField(
        queryset=Actividad.objects.none(),
        required=False
    )

    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 2,
            "class": "form-control",
            "style": "resize: none;"
        }),
        required=False
    )
    class Meta:
        model = Pago
        fields = [
            "socio",
            "familia",
            "cuota",
            "actividad",   # 👈 en vez de inscripcion
            "metodo",
            "importe",
            "observaciones",
        ]

    def clean(self):
        cleaned_data = super().clean()

        cuota = cleaned_data.get("cuota")
        actividad = cleaned_data.get("actividad")
        socio = cleaned_data.get("socio")
        familia = cleaned_data.get("familia")

        # 🔹 No permitir cuota y actividad a la vez
        if cuota and actividad:
            raise forms.ValidationError(
                "No se puede registrar una cuota y una actividad en el mismo pago."
            )

        # 🔹 Debe existir una de las dos
        if not cuota and not actividad:
            raise forms.ValidationError(
                "Debe seleccionar una cuota o una actividad."
            )

        # 🔹 No permitir socio y familia a la vez
        if socio and familia:
            raise forms.ValidationError(
                "No puede seleccionar socio y familia al mismo tiempo."
            )

        # 🔹 Debe existir uno de los dos
        if not socio and not familia:
            raise forms.ValidationError(
                "Debe seleccionar un socio o una familia."
            )

        return cleaned_data

    from asociaciones.models import Actividad

    def __init__(self, *args, organizacion=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organizacion:
 
            self.fields["actividad"].queryset = Actividad.objects.filter(
                organizacion=organizacion
            )

            self.fields["socio"].queryset = Socio.objects.filter(
                organizacion=organizacion
            )

            self.fields["familia"].queryset = Familia.objects.filter(
                organizacion=organizacion
            )

            self.fields["cuota"].queryset = Cuota.objects.filter(
                organizacion=organizacion,
                estado="activa"
            )

            for field in self.fields.values():
                field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()

        socio = cleaned_data.get("socio")
        familia = cleaned_data.get("familia")
        cuota = cleaned_data.get("cuota")
        actividad = cleaned_data.get("actividad")
        importe = cleaned_data.get("importe")

        # No permitir mezclar cuota y actividad
        if cuota and actividad:
            raise forms.ValidationError(
                "No puedes pagar cuota y actividad en el mismo pago."
            )

        # Debe existir algo que pagar
        if not cuota and not actividad:
            raise forms.ValidationError(
                "Debes seleccionar una cuota o una actividad."
            )

        # Si es cuota → socio o familia
        if cuota and not socio and not familia:
            raise forms.ValidationError(
                "Debes seleccionar un socio o una familia para pagar una cuota."
            )

        # Si es actividad → requiere socio
        if actividad and not socio:
            raise forms.ValidationError(
                "Debes seleccionar un socio para pagar una actividad."
            )

        # Validar que el socio esté inscrito en la actividad
        if actividad and socio:
            from asociaciones.models import Inscripcion

            if not Inscripcion.objects.filter(
                actividad=actividad,
                socio=socio
            ).exists():
                raise forms.ValidationError(
                    "El socio no está inscrito en esa actividad."
                )

        return cleaned_data
    

class ComunicacionForm(forms.ModelForm):
    class Meta:
        model = Comunicacion
        fields = [
            "fecha",
            "organismo",
            "tipo",
            "asunto",
            "descripcion",
        ]

        widgets = {
            "fecha": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
            ),
            "organismo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "tipo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "asunto": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def __init__(self, *args, organizacion=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organizacion:
            self.fields["organismo"].queryset = Organismo.objects.filter(
                organizacion=organizacion
            )
            self.fields["tipo"].queryset = TipoComunicacion.objects.filter(
                organizacion=organizacion
            )
def __init__(self, *args, organizacion=None, **kwargs):
    super().__init__(*args, **kwargs)

    if self.instance and self.instance.pk and self.instance.fecha:
        self.initial["fecha"] = self.instance.fecha.strftime("%Y-%m-%d")

class OrganismoForm(forms.ModelForm):
    class Meta:
        model = Organismo
        fields = ["nombre", "activo"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class TipoComunicacionForm(forms.ModelForm):
    class Meta:
        model = TipoComunicacion
        fields = ["nombre", "activo"]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class ContactoForm(forms.ModelForm):

    def __init__(self, *args, organizacion=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organizacion:
            self.fields["tipo"].queryset = TipoContacto.objects.filter(
                organizacion=organizacion
            )

    class Meta:
        model = Contacto
        fields = [
            "tipo",
            "nombre",
            "apellidos",
            "empresa",
            "telefono",
            "email",
            "observaciones",
            "activo",
        ]

        widgets = {

            "tipo": forms.Select(attrs={"class": "form-select"}),

            "nombre": forms.TextInput(attrs={"class": "form-control"}),

            "apellidos": forms.TextInput(attrs={"class": "form-control"}),

            "empresa": forms.TextInput(attrs={"class": "form-control"}),

            "telefono": forms.TextInput(attrs={"class": "form-control"}),

            "email": forms.EmailInput(attrs={"class": "form-control"}),

            "observaciones": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            "activo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

class ItemInventarioForm(forms.ModelForm):

    class Meta:

        model = ItemInventario

        fields = [
            "categoria",
            "nombre",
            "descripcion",
            "ubicacion",
            "cantidad",
            "estado",
            "valor",
        ]

        widgets = {

            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),

            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),

            "ubicacion": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "cantidad": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

            "estado": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "valor": forms.NumberInput(
                attrs={"class": "form-control"}
            ),

        }