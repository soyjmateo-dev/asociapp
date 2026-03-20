import openpyxl
from django.http import HttpResponse


def generate_template(headers, filename):

    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(headers)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'

    wb.save(response)

    return response