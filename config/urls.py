from django.contrib import admin
from django.urls import path, re_path, include

from asociaciones.views import (
    tenant_login, tenant_home, tenant_logout,
    socios_list, socio_create, socio_update, socio_delete,
    familia_create, familia_update, familia_delete,
    export_socios_excel, descargar_plantilla_socios, import_socios_excel,
    generar_cuotas_anuales, familia_ajax_crear,
    cuotas_list, cuota_create, cuota_activar, cuota_socios_list,
    TenantPasswordChangeView,
    actividades_list, familias_list, familia_detail,
    actividad_create, actividad_update, actividad_delete,
    inscripcion_create, inscripcion_delete, actividad_inscritos,
    pago_familiar, pagos_list, pago_create,
    cuota_importe, obtener_importe,
    obtener_socios_actividad, obtener_socios_cuota,
    gastos_list, gasto_create,
    patrocinadores_list, patrocinador_create,
    actividad_detail, patrocinador_detail, patrocinador_update,
    comunicaciones_list, comunicacion_create,
    organismos_list, organismo_create,
    tipo_comunicacion_create, organismo_ajax_create,
    tipo_comunicacion_ajax_create,
    comunicacion_detail, comunicacion_update,
    archivo_comunicacion_delete,
    tipo_contacto_ajax_create,
    contactos_list, contacto_create, contacto_update,
    contacto_detail, archivo_contacto_delete,
    inventario_list, inventario_create,
    categoria_inventario_ajax_create,
    inventario_update, inventario_detail,
    inventario_delete, archivo_inventario_delete, excel_export, excel_socios_deuda, informe_anual, cuota_update,
    cuota_delete, actividad_lista_asistencia, export_socios_deuda, gasto_delete,
)

from django.contrib.auth.views import PasswordChangeDoneView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    path("admin/", admin.site.urls),

    re_path(r"^(?P<slug>[\w-]+)/login/$", tenant_login),
    re_path(r"^(?P<slug>[\w-]+)/logout/$", tenant_logout),

    re_path(r"^(?P<slug>[\w-]+)/socios/$", socios_list, name="socios_list"),
    re_path(r"^(?P<slug>[\w-]+)/socios/nuevo/$", socio_create, name="socio_create"),
    re_path(r"^(?P<slug>[\w-]+)/socios/(?P<pk>\d+)/editar/$", socio_update, name="socio_update"),
    re_path(r"^(?P<slug>[\w-]+)/socios/(?P<pk>\d+)/eliminar/$", socio_delete, name="socio_delete"),

    re_path(r"^(?P<slug>[\w-]+)/familias/nueva/$", familia_create),
    re_path(r"^(?P<slug>[\w-]+)/familias/(?P<pk>\d+)/editar/$", familia_update),
    re_path(r"^(?P<slug>[\w-]+)/familias/(?P<pk>\d+)/eliminar/$", familia_delete),
    re_path(r"^(?P<slug>[\w-]+)/familias/$", familias_list),
    re_path(r"^(?P<slug>[\w-]+)/familias/(?P<pk>\d+)/$", familia_detail),

    path("<slug:slug>/socios/exportar/", export_socios_excel, name="export_socios"),
    path("<slug:slug>/socios/plantilla/", descargar_plantilla_socios, name="plantilla_socios"),
 
    path("<slug:slug>/cuotas/generar/", generar_cuotas_anuales, name="generar_cuotas"),
    path("<slug:slug>/familias/ajax/crear/", familia_ajax_crear),

    path("<slug:slug>/cuotas/", cuotas_list, name="cuotas_list"),
    path("<slug:slug>/cuotas/nuevo/", cuota_create, name="cuota_create"),
    path("<slug:slug>/cuotas/<int:cuota_id>/activar/", cuota_activar, name="cuota_activar"),
    path("<slug:slug>/cuotas/<int:cuota_id>/socios/", cuota_socios_list, name="cuota_socios_list"),

    path("<slug:slug>/actividades/", actividades_list, name="actividades_list"),
    path("<slug:slug>/actividades/nueva/", actividad_create, name="actividad_create"),
    path("<slug:slug>/actividades/<int:pk>/editar/", actividad_update, name="actividad_update"),
    path("<slug:slug>/actividades/<int:pk>/eliminar/", actividad_delete, name="actividad_delete"),
    path("<slug:slug>/actividades/<int:pk>/", actividad_detail, name="actividad_detail"),

    path("<slug:slug>/actividades/<int:actividad_id>/inscribir/", inscripcion_create, name="inscripcion_create"),
    path("<slug:slug>/actividades/<int:actividad_id>/inscritos/", actividad_inscritos, name="actividad_inscritos"),
    path("<slug:slug>/inscripciones/<int:inscripcion_id>/eliminar/", inscripcion_delete, name="inscripcion_delete"),

    path("<slug:slug>/pagos/", pagos_list, name="pagos_list"),
    path("<slug:slug>/pagos/nuevo/", pago_create, name="pago_create"),

    path("<slug:slug>/ajax/socios-actividad/", obtener_socios_actividad, name="socios_actividad"),
    path("<slug:slug>/ajax/socios-cuota/", obtener_socios_cuota, name="socios_cuota"),

    path("<slug:slug>/cuotas/<int:cuota_id>/importe/", cuota_importe, name="cuota_importe"),
    path("<slug:slug>/ajax/importe/", obtener_importe, name="obtener_importe"),

    path("<slug:slug>/gastos/", gastos_list, name="gastos_list"),
    path("<slug:slug>/gastos/nuevo/", gasto_create, name="gasto_create"),

    path("<slug:slug>/patrocinadores/", patrocinadores_list, name="patrocinadores_list"),
    path("<slug:slug>/patrocinadores/nuevo/", patrocinador_create, name="patrocinador_create"),
    path("<slug:slug>/patrocinadores/<int:pk>/", patrocinador_detail, name="patrocinador_detail"),
    path("<slug:slug>/patrocinadores/<int:pk>/editar/", patrocinador_update, name="patrocinador_update"),

    path("<slug:slug>/comunicaciones/", comunicaciones_list, name="comunicaciones_list"),
    path("<slug:slug>/comunicaciones/nueva/", comunicacion_create, name="comunicacion_create"),
    path("<slug:slug>/comunicaciones/<int:pk>/", comunicacion_detail, name="comunicacion_detail"),
    path("<slug:slug>/comunicaciones/<int:pk>/editar/", comunicacion_update, name="comunicacion_update"),
    path("<slug:slug>/comunicaciones/archivo/<int:pk>/eliminar/", archivo_comunicacion_delete,
         name="archivo_comunicacion_delete"),

    path("<slug:slug>/organismos/", organismos_list, name="organismos_list"),
    path("<slug:slug>/organismos/nuevo/", organismo_create, name="organismo_create"),

    path("<slug:slug>/tipos-comunicacion/nuevo/", tipo_comunicacion_create, name="tipo_comunicacion_create"),
    path("<slug:slug>/organismos/ajax/create/", organismo_ajax_create, name="organismo_ajax_create"),
    path("<slug:slug>/tipos-comunicacion/ajax/create/", tipo_comunicacion_ajax_create,
         name="tipo_comunicacion_ajax_create"),

    path("<slug:slug>/contactos/", contactos_list, name="contactos_list"),
    path("<slug:slug>/contactos/nuevo/", contacto_create, name="contacto_create"),
    path("<slug:slug>/contactos/<int:pk>/editar/", contacto_update, name="contacto_update"),
    path("<slug:slug>/contactos/<int:pk>/", contacto_detail, name="contacto_detail"),
    path("<slug:slug>/contactos/archivo/<int:pk>/eliminar/", archivo_contacto_delete,
         name="archivo_contacto_delete"),

    path("<slug:slug>/tipos-contacto/ajax/create/", tipo_contacto_ajax_create,
         name="tipo_contacto_ajax_create"),

    path("<slug:slug>/inventario/", inventario_list, name="inventario_list"),
    path("<slug:slug>/inventario/nuevo/", inventario_create, name="inventario_create"),
    path("<slug:slug>/inventario/categorias/ajax/create/", categoria_inventario_ajax_create,
         name="categoria_inventario_ajax_create"),
    path("<slug:slug>/inventario/<int:pk>/editar/", inventario_update, name="inventario_update"),
    path("<slug:slug>/inventario/<int:pk>/", inventario_detail, name="inventario_detail"),
    path("<slug:slug>/inventario/<int:pk>/eliminar/", inventario_delete, name="inventario_delete"),
    path("<slug:slug>/inventario/archivo/<int:pk>/eliminar/", archivo_inventario_delete,
         name="archivo_inventario_delete"),
    path("<slug:slug>/export/<str:model>/", excel_export, name="excel_export"),
    path("<slug:slug>/socios/export/deuda/", excel_socios_deuda, name="excel_socios_deuda"),
    path("<slug:slug>/informe-anual/", informe_anual, name="informe_anual"),

    path("<slug:slug>/cuotas/<int:pk>/editar/", cuota_update, name="cuota_update"),
    path("<slug:slug>/cuotas/<int:pk>/eliminar/", cuota_delete, name="cuota_delete"),
    path("<slug:slug>/actividades/<int:pk>/lista/", actividad_lista_asistencia, name="actividad_lista"),
    path("<slug:slug>/socios/deuda/", export_socios_deuda, name="socios_deuda_excel"),
    path("<slug:slug>/socios/importar/", import_socios_excel, name="socios_importar"),
    path("<slug:slug>/gastos/<int:pk>/eliminar/", gasto_delete, name="gasto_delete"),

    re_path(r"^(?P<slug>[\w-]+)/$", tenant_home),

    re_path(
        r"^(?P<slug>[\w-]+)/password-change/$",
        TenantPasswordChangeView.as_view(),
        name="password_change"
    ),

    re_path(
        r"^(?P<slug>[\w-]+)/password-change/done/$",
        PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done"
    ),
]


if settings.DEBUG:
    urlpatterns = static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    ) + urlpatterns