from core.middleware import get_current_db


class TenantRouter:

    def db_for_read(self, model, **hints):
        db = get_current_db()
        if db:
            return db
        return "default"

    def db_for_write(self, model, **hints):
        db = get_current_db()
        if db:
            return db
        return "default"
