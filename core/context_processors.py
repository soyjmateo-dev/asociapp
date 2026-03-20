from core.models import Settings

def global_settings(request):
    return {
        "settings": Settings.objects.first()
    }
