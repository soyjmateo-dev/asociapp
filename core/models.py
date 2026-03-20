from django.db import models
from django.conf import settings


class Organizacion(models.Model):
    nombre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Forzamos slug en minúsculas
        self.slug = self.slug.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"

class UsuarioOrganizacion(models.Model):

    ROL_CHOICES = [
        ("admin", "Administrador Total"),
        ("tesorero", "Tesorero"),
        ("secretario", "Secretario"),
        ("lectura", "Solo lectura"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organizacion = models.ForeignKey("Organizacion", on_delete=models.CASCADE)

    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    activa = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organizacion")
        verbose_name = "Usuario Organización"
        verbose_name_plural = "Usuarios Organizaciones"
    def __str__(self):
        return f"{self.user} - {self.organizacion} ({self.rol})"

class TenantModel(models.Model):
    organizacion = models.ForeignKey(
        Organizacion,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
