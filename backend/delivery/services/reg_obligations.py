# -*- coding: utf-8 -*-
"""Obrigações de notificação regulatória por módulo (os 9 frameworks do vCISO).

FIDELIDADE (crítico): a maioria das normas setoriais BR estabelece dever de comunicação
"tempestivo / assim que ciente", NÃO um prazo em horas. Nesses casos `deadline_hours=None` e
a obrigação é QUALITATIVA (o texto vai em `qualitative_note`). Não fabricar hora.
Exceção: LGPD/ANPD tem janela concreta (3 dias ÚTEIS) — como "dias úteis" != horas corridas,
mantemos `deadline_hours=None` e descrevemos o prazo em `qualitative_note` para não gerar um
countdown factualmente errado. TUDO requer validação de compliance antes de uso regulatório.
"""

REG_OBLIGATIONS = {
    "lgpd": [
        {
            "regulator": "ANPD",
            "obligation_ref": "LGPD art. 48 + Regulamento de Comunicação de Incidente (Res. CD/ANPD nº 15/2024)",
            "deadline_hours": None,
            "qualitative_note": (
                "Comunicar à ANPD e aos titulares afetados em prazo definido: o Regulamento "
                "de Comunicação de Incidente de Segurança fixa 3 (três) DIAS ÚTEIS a contar do "
                "conhecimento do incidente que possa acarretar risco ou dano relevante. Contagem "
                "em dias úteis (não horas corridas) — VALIDAR data-limite com compliance."
            ),
            "channel": "Peticionamento eletrônico ANPD",
        }
    ],
    "bacen": [
        {
            "regulator": "BACEN",
            "obligation_ref": "Res. CMN 4.893/2021 (política de segurança cibernética)",
            "deadline_hours": None,
            "qualitative_note": (
                "Registrar e tratar incidentes relevantes; comunicar ao supervisor conforme a "
                "regulamentação aplicável. A norma-base não fixa prazo em horas — VALIDAR."
            ),
            "channel": "Canais de supervisão BACEN",
        }
    ],
    "bcb85": [
        {
            "regulator": "BACEN",
            "obligation_ref": "Res. BCB 85/2021 art. 20, III",
            "deadline_hours": None,
            "qualitative_note": (
                "Comunicação TEMPESTIVA ao Banco Central de incidentes/interrupções de serviços "
                "relevantes que configurem situação de crise (a instituição define e documenta os "
                "critérios de crise — art. 20, p.ú.). Sem prazo em horas na norma."
            ),
            "channel": "Canais de supervisão BACEN",
        }
    ],
    "cvm": [
        {
            "regulator": "CVM",
            "obligation_ref": "Res. CVM 21/2021 + Res. CVM 35/2021 (controles internos)",
            "deadline_hours": None,
            "qualitative_note": (
                "Tratar e reportar incidentes conforme a política e os controles internos; "
                "comunicação ao regulador conforme as regras aplicáveis. Sem prazo em horas — VALIDAR."
            ),
            "channel": "Sistemas CVM",
        }
    ],
    "anbima": [
        {
            "regulator": "ANBIMA",
            "obligation_ref": "Regras e Procedimentos de Deveres Básicos (segurança cibernética)",
            "deadline_hours": None,
            "qualitative_note": (
                "Autorregulação: tratar incidentes e comunicar conforme os Deveres Básicos e o "
                "Guia de Cibersegurança. Sem prazo em horas."
            ),
            "channel": "Canais ANBIMA",
        }
    ],
    "susep": [
        {
            "regulator": "SUSEP",
            "obligation_ref": "Circular SUSEP 638/2021 (política de segurança cibernética)",
            "deadline_hours": None,
            "qualitative_note": (
                "Registrar, responder e comunicar incidentes relevantes conforme a política; "
                "comunicação ao supervisor conforme regras. Sem prazo em horas na norma — VALIDAR."
            ),
            "channel": "Canais SUSEP",
        }
    ],
    "ans": [
        {
            "regulator": "ANS / ANPD",
            "obligation_ref": "LGPD/ANPD (dados de saúde sensíveis) + boas práticas da saúde suplementar",
            "deadline_hours": None,
            "qualitative_note": (
                "Dados de saúde são sensíveis: a comunicação de incidente segue a LGPD/ANPD (ver "
                "o rastreador LGPD). A camada ANS é de boas práticas. Sem prazo próprio em horas."
            ),
            "channel": "Peticionamento ANPD / canais ANS",
        }
    ],
    "anatel": [
        {
            "regulator": "ANATEL",
            "obligation_ref": "Res. ANATEL 740/2020 (R-Ciber) art. 9º/17 + art. 2º-C",
            "deadline_hours": None,
            "qualitative_note": (
                "Notificar a Anatel os incidentes relevantes (forma e prazo definidos por ato do "
                "GT-Ciber). Adicionalmente, notificar a Anatel sempre que houver comunicação à ANPD "
                "(art. 2º-C). Sem prazo em horas no regulamento-base — VALIDAR ato do GT-Ciber."
            ),
            "channel": "Canais Anatel / GT-Ciber",
        }
    ],
    "aneel": [
        {
            "regulator": "ANEEL",
            "obligation_ref": "REN ANEEL 964/2021 art. 6º",
            "deadline_hours": None,
            "qualitative_note": (
                "Notificar a equipe de coordenação setorial designada os incidentes de MAIOR "
                "IMPACTO, com análise de causa, impacto e ações de mitigação, ASSIM QUE o agente "
                "tiver ciência do incidente e de sua dimensão (art. 6º, §3º). Sem prazo em horas."
            ),
            "channel": "Coordenação setorial / ANEEL",
        }
    ],
}
