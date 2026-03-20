from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    site_header = "Administración"
    site_title = "Administración"
    index_title = "Panel de gestión"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        socios_models = []
        finanzas_models = []

        for app in app_list:
            for model in app["models"]:
                if model["object_name"] in ["Socio", "Familia"]:
                    socios_models.append(model)
                elif model["object_name"] in ["Pago", "Cuota", "Gasto"]:
                    finanzas_models.append(model)

        custom_app_list = []

        if socios_models:
            custom_app_list.append({
                "name": "Socios",
                "app_label": "socios",
                "models": socios_models,
            })

        if finanzas_models:
            custom_app_list.append({
                "name": "Finanzas",
                "app_label": "finanzas",
                "models": finanzas_models,
            })

        return custom_app_list
