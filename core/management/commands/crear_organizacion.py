from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Crea base de datos para una organización"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, required=True)

    def handle(self, *args, **options):

        slug = options["slug"]
        db_name = f"db_{slug}"   # 👈 ESTA LÍNEA ES CLAVE

        if self.database_exists(db_name):
            self.stdout.write(self.style.WARNING(
                f"La base {db_name} ya existe."
            ))
            return

        # 1️⃣ Crear base
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE "{db_name}"')

        self.stdout.write(self.style.SUCCESS(
            f"Base {db_name} creada correctamente."
        ))

        # 2️⃣ Registrar dinámicamente en Django
        import copy

        new_db_config = copy.deepcopy(settings.DATABASES["default"])
        new_db_config["NAME"] = db_name

        settings.DATABASES[db_name] = new_db_config


        # 3️⃣ Ejecutar migraciones
        self.stdout.write("Ejecutando migraciones...")
        call_command("migrate", database=db_name, verbosity=1)
        self.stdout.write("Migraciones completadas.")


        self.stdout.write(self.style.SUCCESS(
            f"Base {db_name} migrada correctamente."
        ))

        User = get_user_model()

        username = f"admin_{slug}"
        email = f"admin@{slug}.local"
        password = "Cambiar123!"

        if not User.objects.using(db_name).filter(username=username).exists():
            User.objects.db_manager(db_name).create_superuser(
                username=username,
                email=email,
                password=password,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Superusuario {username} creado en {db_name}"
        ))

        self.stdout.write(
            self.style.SUCCESS(f"Usuario {username} existe: " +
            str(User.objects.using(db_name).filter(username=username).exists()))
        )

    def database_exists(self, db_name):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                [db_name]
            )
            return cursor.fetchone() is not None
