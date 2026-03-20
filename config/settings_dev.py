from .settings_base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "core_db",
        "USER": "saas_user",
        "PASSWORD": "saas123",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

LANGUAGE_CODE = "es"
TIME_ZONE = "Europe/Madrid"

ADMIN_SITE_HEADER = "🧪 GESTIÓN ASOCIACIÓN · PRUEBAS"