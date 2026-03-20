from core.models import Settings
from core.utils.colors import PALETAS


def get_settings():
    return Settings.objects.first()


def get_colores():
    settings = get_settings()
    if not settings:
        return PALETAS["green"]

    return PALETAS.get(settings.color_primario, PALETAS["green"])
