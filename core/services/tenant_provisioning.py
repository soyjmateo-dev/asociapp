from django.db import connection
from django.conf import settings
from django.core.management import call_command
from psycopg2 import sql


class TenantProvisioningService:

    @staticmethod
    def create_database(db_name, db_user):
        connection.ensure_connection()
        connection.connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("""
                    CREATE DATABASE {} 
                    OWNER {}
                    ENCODING 'UTF8'
                    TEMPLATE template0;
                """).format(
                    sql.Identifier(db_name),
                    sql.Identifier(db_user),
                )
            )

        connection.connection.autocommit = False

    @staticmethod
    def migrate_database(db_alias):
        call_command("migrate", database=db_alias, interactive=False)

    @staticmethod
    def create_superuser(db_alias, username, email, password):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        User.objects.db_manager(db_alias).create_superuser(
            username=username,
            email=email,
            password=password,
        )

    @classmethod
    def provision_tenant(cls, slug, admin_email, admin_password):
        db_name = f"db_{slug}"
        db_alias = db_name
        db_user = settings.DATABASES["default"]["USER"]

        cls.create_database(db_name, db_user)
        cls.migrate_database(db_alias)

        cls.create_superuser(
            db_alias,
            username=f"admin_{slug}",
            email=admin_email,
            password=admin_password,
        )
