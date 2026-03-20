from django.http import Http404, HttpResponseForbidden
from core.models import Organizacion, UsuarioOrganizacion


class TenantMiddleware:

    EXCLUDED_PATHS = ["admin", "static", "media"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.organizacion = None
        path_parts = request.path.strip("/").split("/")

        if not path_parts or not path_parts[0]:
            return self.get_response(request)

        first_part = path_parts[0]

        # Rutas excluidas
        if first_part in self.EXCLUDED_PATHS:
            return self.get_response(request)

        # Detectar organización
        try:
            organizacion = Organizacion.objects.get(
                slug=first_part,
                activa=True
            )
            request.organizacion = organizacion
        except Organizacion.DoesNotExist:
            raise Http404("Organización no encontrada")

        # 🔥 Si es login o logout, NO validamos pertenencia
        if len(path_parts) > 1 and path_parts[1] in ["login", "logout"]:
            return self.get_response(request)

        # 🔥 Si NO está autenticado, dejamos que la vista redirija
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 🔐 Validar pertenencia SOLO si está autenticado
        pertenece = UsuarioOrganizacion.objects.filter(
            user=request.user,
            organizacion=organizacion,
            activa=True
        ).exists()

        if not pertenece:
            return HttpResponseForbidden("No perteneces a esta organización")

        return self.get_response(request)