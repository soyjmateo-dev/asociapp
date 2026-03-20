from django.urls import path
from . import views

urlpatterns = [
    # Pantalla principal de pagos rápidos por actividad
    path(
        "evento/pagos/<int:actividad_id>/",
        views.evento_pagos,
        name="evento_pagos"
    ),

    # Botón PAGAR
   
]
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
