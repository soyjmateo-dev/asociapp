from django.db import connections
from django.conf import settings
from core.middleware import get_current_db
import copy


class DatabaseRouter:

    def db_for_read(self, model, **hints):
        alias = get_current_db()
        if alias:
            if alias not in connections.databases:
                new_db_config = copy.deepcopy(settings.DATABASES["default"])
                new_db_config["NAME"] = alias
                connections.databases[alias] = new_db_config
            return alias
        return "default"

    def db_for_write(self, model, **hints):
        alias = get_current_db()
        if alias:
            if alias not in connections.databases:
                new_db_config = copy.deepcopy(settings.DATABASES["default"])
                new_db_config["NAME"] = alias
                connections.databases[alias] = new_db_config
            return alias
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return app_label == "core"
        return app_label != "core"
