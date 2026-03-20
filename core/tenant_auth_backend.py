from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from core.middleware import get_current_db


class TenantModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        db = get_current_db()
        UserModel = get_user_model()

        if not db:
            return super().authenticate(request, username, password, **kwargs)

        try:
            user = UserModel.objects.using(db).get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
