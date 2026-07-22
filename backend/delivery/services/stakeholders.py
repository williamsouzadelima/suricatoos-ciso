"""Semeia (idempotente) uma matriz de comunicação de crise padrão para um incidente.
As partes 'regulador' são derivadas do conjunto de reguladores do cliente (via taxonomia),
com o template puxado das obrigações — mesma fonte do clock regulatório (fidelidade)."""
from django.db import transaction

from delivery.models import IncidentStakeholder
from .regulatory import resolve_regulator_modules
from .reg_obligations import REG_OBLIGATIONS

W = IncidentStakeholder.When
P = IncidentStakeholder.Party

# Matriz base (party, name, title, when, channel, cadence, template, order)
_BASE = [
    (P.INTERNAL, "Patrocinador executivo / Diretoria", "Sponsor executivo", W.IMMEDIATE,
     "Ligação + e-mail", "No início e a cada marco",
     "Resumo executivo: o que aconteceu, impacto estimado, ações em curso e próxima atualização.", 0),
    (P.INTERNAL, "Equipe de resposta / TI", "Incident Commander e time técnico", W.IMMEDIATE,
     "Sala de crise (war room)", "Contínua",
     "Status técnico: escopo, contenção, próximos passos e bloqueios.", 1),
    (P.INTERNAL, "Jurídico / DPO", "Jurídico e Encarregado (DPO)", W.ON_ESCALATION,
     "E-mail + call", "Em escaladas e antes de comunicações externas",
     "Avaliação de obrigações legais/regulatórias e de dados pessoais; validação de comunicados externos.", 2),
    (P.INTERNAL, "Comunicação / Imprensa", "Assessoria de comunicação", W.ON_ESCALATION,
     "E-mail", "Sob demanda",
     "Preparar posicionamento e Q&A; nenhuma declaração externa sem aprovação.", 3),
    (P.CUSTOMER, "Clientes afetados", "Base de clientes impactada", W.ON_ESCALATION,
     "Aviso oficial / status page", "Conforme a evolução",
     "Comunicado factual: serviço afetado, impacto, medidas de proteção e canal de suporte.", 10),
    (P.VENDOR, "Fornecedores / provedores críticos", "Fornecedores de serviços relevantes", W.ON_REQUEST,
     "E-mail + call", "Sob demanda",
     "Acionar suporte do fornecedor; solicitar logs/ações conforme o contrato.", 30),
    (P.LAW_ENFORCEMENT, "Autoridades / CERT.br", "Autoridades competentes / CSIRT", W.ON_ESCALATION,
     "Canal oficial", "Se aplicável",
     "Registro/boletim junto às autoridades e compartilhamento com o CSIRT setorial, conforme o caso.", 40),
]


@transaction.atomic
def seed_stakeholders(incident):
    """Cria a matriz padrão (idempotente por incident+name) + uma linha por regulador do cliente."""
    created = 0

    def add(party, name, title, when, channel, cadence, template, order):
        nonlocal created
        _obj, was_created = IncidentStakeholder.objects.get_or_create(
            incident=incident,
            name=name,
            defaults={
                "party": party,
                "title": title,
                "when_to_notify": when,
                "channel": channel,
                "cadence": cadence,
                "message_template": template,
                "order": order,
            },
        )
        if was_created:
            created += 1

    for row in _BASE:
        add(*row)

    # partes 'regulador' derivadas do cliente
    order = 20
    for mod in resolve_regulator_modules(incident):
        for ob in REG_OBLIGATIONS.get(mod, []):
            add(
                P.REGULATOR,
                f"Regulador — {ob['regulator']}",
                ob.get("obligation_ref", ""),
                W.IMMEDIATE,
                ob.get("channel", ""),
                "Conforme a norma",
                ob.get("qualitative_note", ""),
                order,
            )
            order += 1

    return {"stakeholders": created}
