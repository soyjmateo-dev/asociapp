from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings
from django.db import connections
from core.middleware import get_current_db


class TenantSessionMiddleware(SessionMiddleware):

    def process_request(self, request):
        db = get_current_db()

        if db:
            request.session = self.SessionStore(session_key=None)
            request.session._db = db
        else:
            super().process_request(request)
