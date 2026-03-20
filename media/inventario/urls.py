from django.urls import path
from . import views

urlpatterns = [

    path("exportar/", views.inventario_export, name="inventario_export"),

]