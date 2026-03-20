import openpyxl
from django.http import HttpResponse


def export_queryset_to_excel(queryset, fields, headers, filename):
    """
    Exporta un queryset a Excel.

    queryset -> queryset filtrado por organización
    fields -> campos del modelo
    headers -> títulos de columnas
    filename -> nombre del archivo
    """

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Datos"

    # cabecera
    ws.append(headers)

    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)

            # si es callable (ej: metodo)
            if callable(value):
                value = value()

            row.append(str(value) if value else "")

        ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

    wb.save(response)

    return response