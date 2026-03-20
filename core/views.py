from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from decimal import Decimal
from core.decorators import tenant_login_required
from .excel import export_model_to_excel
from asociaciones.models import Socio, CuotaSocio, Actividad, Inscripcion, Pago


def historial_socio(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id)

    # ───── CUOTAS ─────
    cuotas = (
        CuotaSocio.objects
        .filter(socio=socio)
        .select_related("cuota")
        .order_by("-cuota__fecha_creacion")
    )

    total_cuotas_pagadas = cuotas.filter(pagada=True).aggregate(
        total=Coalesce(Sum("importe"), Decimal("0.00"))
    )["total"]

    total_cuotas_pendientes = cuotas.filter(pagada=False).aggregate(
        total=Coalesce(Sum("importe"), Decimal("0.00"))
    )["total"]

    # ───── ACTIVIDADES ─────
    inscripciones = (
        Inscripcion.objects
        .filter(socio=socio)
        .select_related("actividad")
        .order_by("-actividad__fecha")
    )

    total_actividades_pagadas = inscripciones.filter(pagado=True).aggregate(
        total=Coalesce(Sum("importe_pagado"), Decimal("0.00"))
    )["total"]

    # ───── PAGOS ─────
    pagos = (
        Pago.objects
        .filter(socio=socio)
        .order_by("-fecha")
    )

    total_pagado = total_cuotas_pagadas + total_actividades_pagadas
    total_pendiente = total_cuotas_pendientes

    estado = "al_dia" if total_pendiente == 0 else "pendiente"

    context = {
        "socio": socio,
        "cuotas": cuotas,
        "inscripciones": inscripciones,
        "pagos": pagos,
        "total_pagado": total_pagado,
        "total_pendiente": total_pendiente,
        "estado": estado,
    }

    return render(request, "core/historial_socio.html", context)


def socio_publico(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id)

    cuotas = (
        CuotaSocio.objects
        .filter(socio=socio)
        .select_related("cuota")
        .order_by("-cuota__fecha_creacion")
    )

    inscripciones = (
        Inscripcion.objects
        .filter(socio=socio)
        .select_related("actividad")
        .order_by("-actividad__fecha")
    )

    pagos = (
        Pago.objects
        .filter(socio=socio)
        .order_by("-fecha")
    )

    total_pendiente = cuotas.filter(pagada=False).aggregate(
        total=Coalesce(Sum("importe"), Decimal("0.00"))
    )["total"]

    context = {
        "socio": socio,
        "cuotas": cuotas,
        "inscripciones": inscripciones,
        "pagos": pagos,
        "total_pendiente": total_pendiente,
    }

    return render(request, "public/socio_historial.html", context)


# ─────────────────────────────────────────
# EVENTOS / PAGOS DE ACTIVIDADES
# ─────────────────────────────────────────

def evento_pagos(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)

    inscripciones = (
        actividad.inscripciones
        .select_related("socio")
        .order_by("socio__apellidos", "socio__nombre")
    )

    return render(
        request,
        "core/evento_pagos.html",
        {
            "actividad": actividad,
            "inscripciones": inscripciones,
        },
    )


def evento_pagar(request, inscripcion_id):
    inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)

    if not inscripcion.pagado:
        importe = (
            inscripcion.actividad.coste_menor
            if inscripcion.socio.es_menor
            else inscripcion.actividad.coste_adulto
        )

        # Marcar inscripción como pagada
        inscripcion.pagado = True
        inscripcion.fecha_pago = now()
        inscripcion.importe_pagado = importe
        inscripcion.save()

        # Crear registro de pago
        Pago.objects.create(
            socio=inscripcion.socio,
            actividad=inscripcion.actividad,
            metodo="efectivo",
            importe=importe,
            observaciones="Pago durante la propia actividad",
        )

    return redirect(
        "evento_pagos",
        actividad_id=inscripcion.actividad.id
    )

from django.apps import apps
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from .excel import export_model_to_excel
from core.decorators import tenant_login_required


@tenant_login_required
def excel_export(request, slug, model):

    try:
        model_obj = apps.get_model("asociaciones", model)
    except LookupError:
        raise PermissionDenied("Modelo no encontrado")

    if not model_obj:
        raise PermissionDenied("Modelo inválido")

    return export_model_to_excel(
        request,
        "asociaciones",
        model
    )