"""Provisionamento da estrutura do cliente a partir do intake (mínimo do MVP: cria o Folder
DOMAIN do cliente). Perimeter/time/assets entram nas próximas fases."""
from iam.models import Folder


def create_client_folder(name, parent=None):
    """Cria (ou retorna, se já existir com esse nome) um Folder DOMAIN para o cliente."""
    existing = Folder.objects.filter(name=name, content_type=Folder.ContentType.DOMAIN).first()
    if existing:
        return existing, False
    parent = parent or Folder.get_root_folder()
    folder = Folder.objects.create(
        name=name,
        content_type=Folder.ContentType.DOMAIN,
        parent_folder=parent,
    )
    return folder, True
