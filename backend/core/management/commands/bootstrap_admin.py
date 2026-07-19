import secrets
import string

import structlog
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from iam.models import Folder, User, UserGroup

logger = structlog.get_logger(__name__)

DEFAULT_ADMIN_EMAIL = "admin@suricatoos.local"
PASSWORD_LENGTH = 20
# Sem caracteres ambiguos (O/0, l/1/I) para a senha poder ser copiada da tela sem erro.
PASSWORD_ALPHABET = (
    "".join(c for c in string.ascii_letters + string.digits if c not in "O0lI1")
    + "!@#%^&*-_=+"
)


def generate_password(length: int = PASSWORD_LENGTH) -> str:
    """Senha aleatoria criptograficamente segura, garantindo variedade de classes."""
    while True:
        password = "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(not c.isalnum() for c in password)
        ):
            return password


class Command(BaseCommand):
    help = (
        "Cria o administrador inicial com senha aleatoria e a exibe uma unica vez. "
        "Idempotente: nao faz nada se o administrador ja existir (use --force para redefinir a senha)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=settings.CISO_ASSISTANT_SUPERUSER_EMAIL or DEFAULT_ADMIN_EMAIL,
            help=f"E-mail do administrador (padrao: CISO_ASSISTANT_SUPERUSER_EMAIL ou {DEFAULT_ADMIN_EMAIL})",
        )
        parser.add_argument(
            "--password",
            default=None,
            help="Senha explicita. Se omitida, uma senha aleatoria e gerada.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Redefine a senha mesmo se o usuario ja existir.",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Nao imprime as credenciais (uso em automacao).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        email = options["email"].strip()
        force = options["force"]
        quiet = options["quiet"]

        user = User.objects.filter(email=email).first()
        if user and not force:
            self.stdout.write(
                self.style.WARNING(
                    f"O administrador '{email}' ja existe; nada a fazer. "
                    "Use --force para redefinir a senha."
                )
            )
            return

        password = options["password"] or generate_password()
        generated = options["password"] is None

        created = user is None
        if created:
            user = User.objects.create_superuser(email=email)

        user.set_password(password)
        user.is_superuser = True
        user.is_active = True
        user.save()

        try:
            administrators = UserGroup.objects.get(
                name="BI-UG-ADM", folder=Folder.get_root_folder()
            )
        except UserGroup.DoesNotExist as exc:
            raise CommandError(
                "Grupo de administradores nao encontrado. Rode 'manage.py migrate' antes deste comando."
            ) from exc
        user.user_groups.add(administrators)

        logger.info(
            "bootstrap admin",
            email=email,
            created=created,
            password_generated=generated,
        )

        if quiet:
            return

        action = "criado" if created else "atualizado"
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Administrador {action}."))
        self.stdout.write("")
        self.stdout.write(f"  Usuario: {email}")
        if generated:
            self.stdout.write(f"  Senha:   {password}")
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Anote a senha agora: ela e aleatoria e nao sera exibida novamente. "
                    "Troque-a apos o primeiro acesso."
                )
            )
        else:
            self.stdout.write("  Senha:   (a que foi informada em --password)")
        self.stdout.write("")
