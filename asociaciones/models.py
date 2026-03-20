
from django.db import models, transaction
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from core.models import Organizacion
from django.conf import settings

# Create your models here.

# ─────────────────────────────
# INVENTARIO
# ─────────────────────────────

class Inventario(models.Model):
    descripcion = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField(default=1)
    observaciones = models.TextField(blank=True)
    archivo = models.FileField(
        upload_to="inventario/",
        blank=True,
        null=True
    )
    fecha_alta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descripcion

    





# ─────────────────────────────
# CONSTANTES GLOBALES
# ─────────────────────────────

METODOS_PAGO = [
    ("efectivo", "Efectivo"),
    ("transferencia", "Transferencia"),
    ("tarjeta", "Tarjeta"),
    ("bizum", "Bizum"),
]


# ─────────────────────────────
# SOCIOS Y FAMILIAS
# ─────────────────────────────

class Familia(models.Model):
    organizacion = models.ForeignKey(
        "core.Organizacion",
        on_delete=models.CASCADE
    )

    nombre = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "familia"
        verbose_name_plural = "familias"

    def __str__(self):
        return self.nombre
    

class Socio(models.Model):
    organizacion = models.ForeignKey(
        "core.Organizacion",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True, verbose_name="Socio activo")
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    familia = models.ForeignKey(
        Familia,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )


    en_whatsapp = models.BooleanField(default=False)
    es_colaborador = models.BooleanField(default=False)

    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    proteccion_datos = models.BooleanField(default=False)
    acepta_fotografias = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "01 · Socios"

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    def generar_cuotas_activas(self):
        from .models import Cuota, CuotaSocio

        cuotas_activas = Cuota.objects.filter(
            organizacion=self.organizacion,
            estado="activa"
        )

        for cuota in cuotas_activas:

            if CuotaSocio.objects.filter(socio=self, cuota=cuota).exists():
                continue

            if self.es_adulto():
                importe = cuota.importe_adulto
            else:
                importe = cuota.importe_menor

            CuotaSocio.objects.create(
                socio=self,
                cuota=cuota,
                importe=importe
            )

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        super().save(*args, **kwargs)

        if es_nuevo:
            self.generar_cuotas_activas()

    def es_adulto(self):
        if not self.fecha_nacimiento:
            return True
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
        return edad >= 18

    @property
    def es_menor(self):
        return not self.es_adulto()

    def edad(self):
        if not self.fecha_nacimiento:
            return None

        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def total_deuda(self):
        return self.cuotas_generadas.filter(
            pagada=False,
            cuota__estado="activa"
        ).aggregate(
            total=Sum("importe")
        )["total"] or 0

    def esta_al_corriente(self):
        return not self.cuotas_generadas.filter(pagada=False).exists()



# ─────────────────────────────
# CUOTAS
# ─────────────────────────────
class ConfiguracionCuota(models.Model):

    TIPO_CHOICES = [
        ("adulto", "Adulto"),
        ("menor", "Menor"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, unique=True)
    importe = models.DecimalField(max_digits=8, decimal_places=2)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo} - {self.importe}€"

class Cuota(models.Model):

    organizacion = models.ForeignKey(
        "core.Organizacion",
        on_delete=models.CASCADE
    )

    TIPO_CHOICES = [
        ("anual", "Anual"),
        ("extraordinaria", "Extraordinaria"),
    ]

    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("activa", "Activa"),
        ("cerrada", "Cerrada"),
    ]

    nombre = models.CharField(max_length=100)
    año = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="anual")

    importe_adulto = models.DecimalField(max_digits=8, decimal_places=2)
    importe_menor = models.DecimalField(max_digits=8, decimal_places=2)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="borrador"
    )

    fecha_emision = models.DateField(default=date.today)
    fecha_vencimiento = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organizacion", "tipo", "año"],
                condition=Q(tipo="anual"),
                name="unique_anual_por_año"
            )
        ]

    def __str__(self):
        return f"{self.nombre} {self.año}"

class CuotaSocio(models.Model):
    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name="cuotas_generadas"
    )
    cuota = models.ForeignKey(
        Cuota,
        on_delete=models.CASCADE,
        related_name="socios"
    )
    importe = models.DecimalField(max_digits=8, decimal_places=2)

    pagada = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("socio", "cuota")

    def __str__(self):
        return f"{self.socio} - {self.cuota}"
    
    
def generar_cuotas_para_definicion(cuota):

    if cuota.estado != "activa":
        raise ValidationError("La cuota debe estar activa")

    socios_activos = Socio.objects.filter(activo=True)

    for socio in socios_activos:

        if CuotaSocio.objects.filter(socio=socio, cuota=cuota).exists():
            continue

        if socio.es_adulto():
            importe = cuota.importe_adulto
        else:
            importe = cuota.importe_menor

        CuotaSocio.objects.create(
            socio=socio,
            cuota=cuota,
            importe=importe
        )
# ─────────────────────────────
# ACTIVIDADES
# ─────────────────────────────

from core.models import TenantModel

class Actividad(TenantModel):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()

    cupo_maximo = models.PositiveIntegerField()
    coste_adulto = models.DecimalField(max_digits=8, decimal_places=2)
    coste_menor = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name_plural = "03 · Actividades"

    def __str__(self):
        return self.nombre

    def plazas_ocupadas(self):
        return self.inscripciones.count()

    def plazas_disponibles(self):
        return self.cupo_maximo - self.plazas_ocupadas()

    def total_gastos(self):
        return self.gastos.aggregate(
            total=Coalesce(Sum("importe"), Decimal("0.00"))
        )["total"]

    def ingresos_totales(self):
        return (
            self.inscripciones.filter(pagado=True).aggregate(
                total=Coalesce(Sum("importe_pagado"), Decimal("0.00"))
            )["total"]
            or Decimal("0.00")
        )


#        patrocinios = self.patrocinios.aggregate(
#            total=Coalesce(Sum("importe"), Decimal("0.00"))
#        )["total"]

#        return inscripciones + patrocinios

    def beneficio(self):
        return self.ingresos_totales() - self.total_gastos()

class Patrocinio(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        related_name="patrocinios",
        on_delete=models.CASCADE
    )
    empresa = models.CharField(max_length=255)
    aportacion = models.DecimalField(max_digits=10, decimal_places=2)
    año = models.PositiveIntegerField()
    fecha = models.DateField()
    observaciones = models.TextField(blank=True)

class Inscripcion(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name="inscripciones"
    )

    socio = models.ForeignKey(
        Socio,
        on_delete=models.CASCADE,
        related_name="inscripciones"
    )

    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

    importe_pagado = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("actividad", "socio")

    def __str__(self):
        return f"{self.socio} → {self.actividad}"

    def clean(self):

        # 🔒 Si todavía no tiene actividad asignada, no validar plazas
        if not self.actividad_id:
            return

        # 🔒 Control de plazas
        if not self.pk and self.actividad.plazas_disponibles() <= 0:
            raise ValidationError("No hay plazas disponibles para esta actividad")

        # 🔒 Multi-tenant seguridad
        if self.socio.organizacion != self.actividad.organizacion:
            raise ValidationError("El socio no pertenece a esta organización")

    def save(self, *args, **kwargs):

        # 💰 Cálculo automático de precio
        if not self.importe_pagado:

            if self.socio.es_menor:
                self.importe_pagado = self.actividad.coste_menor
            else:
                self.importe_pagado = self.actividad.coste_adulto

        super().save(*args, **kwargs)
# ─────────────────────────────
# PAGOS Y GASTOS
# ─────────────────────────────

class Pago(models.Model):
    socio = models.ForeignKey(
        Socio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos"
    )

    familia = models.ForeignKey(
        Familia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cuota = models.ForeignKey(
        Cuota,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos"
    )

    organizacion = models.ForeignKey(
        "core.Organizacion",
        on_delete=models.CASCADE
    )

    importe = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODOS_PAGO)
    fecha = models.DateField(default=date.today)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "05 · Pagos"

    def __str__(self):
        return f"{self.importe} €"

    # --------------------------------------------------
    # LÓGICA FINANCIERA
    # --------------------------------------------------

    def aplicar_pago_cuota_individual(self):
        if not (self.cuota and self.socio):
            return

        cuota_socio = CuotaSocio.objects.filter(
            socio=self.socio,
            cuota=self.cuota
        ).first()

        if not cuota_socio:
            return

        total_pagado = Pago.objects.filter(
            socio=self.socio,
            cuota=self.cuota,
            organizacion=self.organizacion
        ).aggregate(
            total=Sum("importe")
        )["total"] or Decimal("0.00")

        if total_pagado >= cuota_socio.importe:
            cuota_socio.pagada = True
            cuota_socio.fecha_pago = self.fecha
        else:
            cuota_socio.pagada = False
            cuota_socio.fecha_pago = None

        cuota_socio.save()

    def aplicar_pago_inscripcion(self):
        if not self.inscripcion:
            return

        total_pagado = Pago.objects.filter(
            inscripcion=self.inscripcion,
            organizacion=self.organizacion
        ).aggregate(
            total=Sum("importe")
        )["total"] or Decimal("0.00")

        if total_pagado >= self.inscripcion.importe_pagado:
            self.inscripcion.pagado = True
            self.inscripcion.fecha_pago = self.fecha
        else:
            self.inscripcion.pagado = False
            self.inscripcion.fecha_pago = None

        self.inscripcion.importe_pagado = total_pagado
        self.inscripcion.save()

    def aplicar_pago_familiar(self):
        if not (self.familia and self.cuota):
            return

        socios_familia = Socio.objects.filter(
            familia=self.familia,
            activo=True
        )

        for socio in socios_familia:
            cuota_socio = CuotaSocio.objects.filter(
                socio=socio,
                cuota=self.cuota
            ).first()

            if cuota_socio:
                cuota_socio.pagada = True
                cuota_socio.fecha_pago = self.fecha
                cuota_socio.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.aplicar_pago_cuota_individual()
        self.aplicar_pago_inscripcion()
        self.aplicar_pago_familiar()
        
class Gasto(models.Model):
    fecha = models.DateField()
    concepto = models.CharField(max_length=255)
    importe = models.DecimalField(max_digits=10, decimal_places=2)

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default="efectivo"
    )

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gastos"
    )

    archivo = models.FileField(upload_to="gastos/", null=True, blank=True)
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "06 · Gastos"

    def __str__(self):
        return self.concepto


# ─────────────────────────────
# COMUNICACIONES INSTITUCIONALES
# ─────────────────────────────

class Organismo(models.Model):
    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE
    )

    nombre = models.CharField(max_length=255)

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TipoComunicacion(models.Model):
    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE
    )

    nombre = models.CharField(max_length=100)

    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Comunicacion(models.Model):

    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE
    )

    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.PROTECT,
        related_name="comunicaciones"
    )

    tipo = models.ForeignKey(
        TipoComunicacion,
        on_delete=models.PROTECT,
        related_name="comunicaciones"
    )

    fecha = models.DateField()

    asunto = models.CharField(max_length=255)

    descripcion = models.TextField(blank=True)

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-created_at"]

    def __str__(self):
        return f"{self.fecha} - {self.asunto}"
    
class ArchivoComunicacion(models.Model):
    comunicacion = models.ForeignKey(
        Comunicacion,
        on_delete=models.CASCADE,
        related_name="archivos"
    )

    archivo = models.FileField(upload_to="comunicaciones/")
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.descripcion or self.archivo.name
    
# ─────────────────────────────
# CONTACTOS
# ─────────────────────────────

class TipoContacto(models.Model):
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Contacto(models.Model):

    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE)

    tipo = models.ForeignKey(
        TipoContacto,
        on_delete=models.PROTECT,
        related_name="contactos"
    )

    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150, blank=True)
    empresa = models.CharField(max_length=150, blank=True)

    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    observaciones = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

class ArchivoContacto(models.Model):

    contacto = models.ForeignKey(
        Contacto,
        on_delete=models.CASCADE,
        related_name="archivos"
    )

    archivo = models.FileField(upload_to="contactos/")
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.archivo.name
    
# ─────────────────────────────
# PATROCINADORES
# ─────────────────────────────

class Patrocinador(models.Model):
    empresa = models.CharField(max_length=255)
    nombre_contacto = models.CharField(max_length=255, blank=True)

    telefono = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patrocinadores",
        help_text="Dejar vacío si el patrocinio es general"
    )

    aportacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    año = models.PositiveIntegerField()  # 👈 NUEVO

    logotipo = models.ImageField(
        upload_to="patrocinadores/",
        null=True,
        blank=True
    )

    documento = models.FileField(
        upload_to="patrocinadores/documentos/",
        blank=True,
        null=True
    )
    
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "07 · Patrocinadores"

    def __str__(self):
        return self.empresa

# ─────────────────────────────
# INVENTARIO
# ─────────────────────────────

class CategoriaInventario(models.Model):

    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE
    )

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class ItemInventario(models.Model):

    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE
    )

    categoria = models.ForeignKey(
        CategoriaInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    nombre = models.CharField(max_length=200)

    descripcion = models.TextField(blank=True)

    ubicacion = models.CharField(
        max_length=200,
        blank=True
    )

    cantidad = models.IntegerField(default=1)

    estado = models.CharField(
        max_length=50,
        default="Disponible"
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class ArchivoInventario(models.Model):

    item = models.ForeignKey(
        ItemInventario,
        on_delete=models.CASCADE,
        related_name="archivos"
    )

    archivo = models.FileField(upload_to="inventario/")

    descripcion = models.CharField(max_length=255, blank=True)

    es_imagen = models.BooleanField(default=False)

    def __str__(self):
        return self.archivo.name