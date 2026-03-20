from .settings_base import *

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(
        "postgres://saas_user:laolma123@127.0.0.1:5432/laolma"
    )
}

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True