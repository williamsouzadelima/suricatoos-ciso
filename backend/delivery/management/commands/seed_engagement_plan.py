"""Semeia (idempotente) o plano de 100 dias vCISO no folder de um cliente.

Ex.: manage.py seed_engagement_plan --folder "Cliente X" --create-folder \
     --hours 200 --day-zero 2026-07-20 --modules lgpd
"""
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from iam.models import Folder
from delivery.models import Engagement
from delivery.services.provisioning import create_client_folder
from delivery.services.seeding import seed_engagement_plan


class Command(BaseCommand):
    help = "Semeia o plano de 100 dias vCISO no folder de um cliente (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument("--folder", required=True, help="id ou nome do Folder (cliente)")
        parser.add_argument(
            "--create-folder",
            action="store_true",
            help="cria o Folder DOMAIN se não existir",
        )
        parser.add_argument("--template", default="vciso-100d")
        parser.add_argument("--modules", default="", help="csv: lgpd,bacen,...")
        parser.add_argument("--hours", type=float, default=None, help="horas contratadas")
        parser.add_argument("--day-zero", required=True, help="âncora do plano (YYYY-MM-DD)")

    def _resolve_folder(self, ref, create):
        folder = None
        if len(ref) >= 8 and "-" in ref:
            folder = Folder.objects.filter(id=ref).first()
        if folder is None:
            folder = Folder.objects.filter(name=ref).first()
        if folder is None:
            if create:
                folder, made = create_client_folder(ref)
                self.stdout.write(
                    f"Folder {'criado' if made else 'reaproveitado'}: {folder.name} ({folder.id})"
                )
            else:
                raise CommandError(f"Folder '{ref}' não encontrado (use --create-folder).")
        return folder

    def handle(self, *args, **opts):
        folder = self._resolve_folder(opts["folder"], opts["create_folder"])
        day_zero = datetime.strptime(opts["day_zero"], "%Y-%m-%d").date()

        engagement, created = Engagement.objects.get_or_create(
            folder=folder,
            status=Engagement.Status.ONBOARDING,
            defaults={
                "name": f"Engajamento vCISO — {folder.name}",
                "hours_model": Engagement.HoursModel.BUDGET,
                "contracted_hours": opts["hours"],
                "day_zero": day_zero,
            },
        )
        changed = False
        if engagement.day_zero is None:
            engagement.day_zero = day_zero
            changed = True
        if opts["hours"] is not None and engagement.contracted_hours is None:
            engagement.contracted_hours = opts["hours"]
            changed = True
        if changed:
            engagement.save()

        modules = [m.strip() for m in opts["modules"].split(",") if m.strip()]
        result = seed_engagement_plan(
            engagement, template=opts["template"], modules=modules
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed OK — engagement={'criado' if created else 'existente'} "
                f"({engagement.id}) folder='{folder.name}' "
                f"horas_contratadas={engagement.contracted_hours} "
                f"esforço_estimado_total={engagement.estimated_hours_total}h "
                f"AppliedControls+={result['applied_controls']} "
                f"PlanTasks+={result['plan_tasks']}"
            )
        )
