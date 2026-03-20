import openpyxl

from django.apps import apps
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.db.models import ForeignKey
from django.db.models.fields.files import FileField, ImageField
from django.utils.timezone import localtime
from openpyxl.styles import Font

# Campos que nunca queremos exportar
CAMPOS_EXCLUIDOS = {
    "id",
    "organizacion",
    "created_at",
    "updated_at",
    "creado",
    "activo",
}


def export_model_to_excel(request, app_label, model_name, queryset_override=None, filename=None):

    model = apps.get_model(app_label, model_name)

    if not model:
        raise PermissionDenied("Modelo no encontrado")

    # Seguridad multi-tenant
    if hasattr(model, "organizacion"):
        if queryset_override is not None:
            queryset = queryset_override
        else:
            queryset = model.objects.filter(
                organizacion=request.organizacion
            )
    else:
        queryset = model.objects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Datos"

    # Obtener campos útiles
    fields = []

    for field in model._meta.fields:

        if field.name in CAMPOS_EXCLUIDOS:
            continue

        if isinstance(field, (FileField, ImageField)):
            continue

        fields.append(field)

    # Cabeceras bonitas
    headers = [field.verbose_name.title() for field in fields]

    if model_name == "Socio":
        headers.append("Estado cuotas")
        headers.append("Deuda total")

    ws.append(headers)

    # Filas
    for obj in queryset:

        row = []

        for field in fields:

            value = getattr(obj, field.name)

            if value is None:
                row.append("")
                continue

            if isinstance(field, ForeignKey):
                row.append(str(value))
                continue

            if hasattr(value, "strftime"):
                try:
                    value = localtime(value)
                except:
                    pass

                row.append(value.strftime("%Y-%m-%d"))
                continue

            row.append(str(value))

        # ───────────────────────
        # CAMPOS EXTRA PARA SOCIOS
        # ───────────────────────

        if model_name == "Socio":
  
            deuda = obj.total_deuda()

            if deuda > 0:
                estado = "⚠ Pendiente"
            else:
                estado = "✔ Al corriente"

            row.append(estado)
            row.append(deuda)

        ws.append(row)
    
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if not filename:
        filename = f"{model_name}.xlsx"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    formatear_excel(ws)
    
    wb.save(response)

    return response

def formatear_excel(ws):

    # Cabecera en negrita
    for cell in ws[1]:
        cell.font = Font(bold=True)

    # Congelar cabecera
    ws.freeze_panes = "A2"

    # Ajustar ancho columnas
    for column in ws.columns:

        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        ws.column_dimensions[column_letter].width = max_length + 2