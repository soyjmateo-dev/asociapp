from django.utils.safestring import mark_safe

def render_estado_pago(deuda):
    if deuda > 0:
        return mark_safe('<span class="estado-bad">Debe</span>')
    return mark_safe('<span class="estado-ok">Al día</span>')
