# -*- coding: utf-8 -*-
"""Taxonomia de setores/subsetores de mercado para o onboarding vCISO.

Fonte única de verdade: dirige o wizard (setor → subsetor), a sugestão de
módulos regulatórios e o contexto de reguladores. O mercado financeiro é
aprofundado (múltiplos subsetores + reguladores brasileiros).

Módulos regulatórios que o produto SEMEIA hoje: lgpd, bacen, anbima, cvm.
Subsetores cujo regulador ainda não tem módulo próprio (SUSEP/PREVIC/ANS/…)
sugerem `lgpd` e exibem o(s) regulador(es) como contexto (`regulators`).
"""

# key -> {label, icon, subsectors: [{key, label, modules, regulators}]}
TAXONOMY = {
    "financial": {
        "label": "Mercado financeiro",
        "icon": "fa-landmark",
        "subsectors": [
            {"key": "bank_commercial", "label": "Banco comercial / múltiplo", "modules": ["lgpd", "bacen"], "regulators": ["BACEN", "CMN"], "norm": "Res. CMN 4.893/2021"},
            {"key": "bank_investment", "label": "Banco de investimento", "modules": ["lgpd", "bacen", "cvm"], "regulators": ["BACEN", "CVM"], "norm": "Res. CMN 4.893/2021"},
            {"key": "credit_union", "label": "Cooperativa de crédito", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Res. CMN 4.893/2021"},
            {"key": "credit_finance", "label": "Financeira / crédito (SCFI)", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Res. CMN 4.893/2021"},
            {"key": "payment_institution", "label": "Instituição de pagamento / adquirência", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Res. BCB 85/2021"},
            {"key": "fintech_credit", "label": "Fintech de crédito (SCD / SEP)", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Res. CMN 4.656/2018 · 4.893/2021"},
            {"key": "consortium", "label": "Administradora de consórcio", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Lei 11.795/2008 · Res. CMN 4.893/2021"},
            {"key": "fx", "label": "Câmbio / corretora de câmbio", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Lei 14.286/2021 · Res. CMN 4.893/2021"},
            {"key": "crypto_vasp", "label": "Criptoativos / exchange (VASP)", "modules": ["lgpd", "bacen"], "regulators": ["BACEN"], "norm": "Lei 14.478/2022 · Dec. 11.563/2023"},
            {"key": "broker_dtvm", "label": "Corretora / DTVM", "modules": ["lgpd", "cvm"], "regulators": ["CVM", "BACEN"], "norm": "Res. CVM 35/2021 · CMN 4.893/2021"},
            {"key": "asset_manager", "label": "Gestora de recursos (asset)", "modules": ["lgpd", "anbima"], "regulators": ["CVM", "ANBIMA"], "norm": "Res. CVM 21/2021"},
            {"key": "fiduciary_admin", "label": "Administrador fiduciário", "modules": ["lgpd", "cvm", "anbima"], "regulators": ["CVM", "ANBIMA"], "norm": "Res. CVM 21/2021 · 175/2022"},
            {"key": "wealth_private", "label": "Wealth / private banking", "modules": ["lgpd", "anbima"], "regulators": ["CVM", "ANBIMA"], "norm": "Res. CMN 4.893/2021 · CVM 21/2021"},
            {"key": "family_office", "label": "Family office", "modules": ["lgpd", "anbima"], "regulators": ["CVM", "ANBIMA"], "norm": "Res. CVM 21/2021 (se gere terceiros)"},
            {"key": "market_infra", "label": "Bolsa / infraestrutura de mercado", "modules": ["lgpd", "cvm"], "regulators": ["CVM", "BACEN"], "norm": "Resiliência operacional (CVM/BCB)"},
            {"key": "securitizer_fidc", "label": "Securitizadora / FIDC", "modules": ["lgpd", "cvm"], "regulators": ["CVM"], "norm": "Res. CVM 175/2022 · Lei 14.430/2022"},
            {"key": "insurer", "label": "Seguradora", "modules": ["lgpd", "susep"], "regulators": ["SUSEP", "CNSP"], "norm": "Circular SUSEP 638/2021"},
            {"key": "reinsurer", "label": "Resseguradora", "modules": ["lgpd", "susep"], "regulators": ["SUSEP"], "norm": "Circular SUSEP 638/2021"},
            {"key": "insurance_broker", "label": "Corretora de seguros", "modules": ["lgpd"], "regulators": ["SUSEP"], "norm": "LGPD (base)"},
            {"key": "capitalization", "label": "Capitalização", "modules": ["lgpd", "susep"], "regulators": ["SUSEP"], "norm": "Circular SUSEP 638/2021"},
            {"key": "pension_open", "label": "Previdência aberta (EAPC)", "modules": ["lgpd", "susep"], "regulators": ["SUSEP", "CNSP"], "norm": "Circular SUSEP 638/2021"},
            {"key": "pension_closed", "label": "Previdência fechada (EFPC)", "modules": ["lgpd"], "regulators": ["PREVIC", "CNPC"], "norm": "Guia de cyber PREVIC"},
        ],
    },
    "health": {
        "label": "Saúde",
        "icon": "fa-heart-pulse",
        "subsectors": [
            {"key": "health_plan", "label": "Operadora de saúde", "modules": ["lgpd", "ans"], "regulators": ["ANS"]},
            {"key": "hospital", "label": "Hospital", "modules": ["lgpd"], "regulators": ["ANVISA"]},
            {"key": "clinic", "label": "Clínica / consultório", "modules": ["lgpd"], "regulators": []},
            {"key": "lab", "label": "Laboratório / diagnóstico", "modules": ["lgpd"], "regulators": ["ANVISA"]},
            {"key": "pharma", "label": "Indústria farmacêutica", "modules": ["lgpd"], "regulators": ["ANVISA"]},
            {"key": "healthtech", "label": "Healthtech / telemedicina", "modules": ["lgpd"], "regulators": []},
        ],
    },
    "tech": {
        "label": "Tecnologia & Telecom",
        "icon": "fa-microchip",
        "subsectors": [
            {"key": "saas", "label": "SaaS / software", "modules": ["lgpd"], "regulators": []},
            {"key": "telecom", "label": "Telecom", "modules": ["lgpd", "anatel"], "regulators": ["ANATEL"], "norm": "Res. ANATEL 740/2020"},
            {"key": "cloud_dc", "label": "Cloud / data center", "modules": ["lgpd"], "regulators": []},
            {"key": "platform", "label": "Marketplace / plataforma digital", "modules": ["lgpd"], "regulators": []},
            {"key": "cybersec", "label": "Cibersegurança", "modules": ["lgpd"], "regulators": []},
        ],
    },
    "retail": {
        "label": "Varejo & Consumo",
        "icon": "fa-cart-shopping",
        "subsectors": [
            {"key": "retail_physical", "label": "Varejo físico", "modules": ["lgpd"], "regulators": []},
            {"key": "ecommerce", "label": "E-commerce", "modules": ["lgpd"], "regulators": []},
            {"key": "wholesale", "label": "Atacado / distribuição", "modules": ["lgpd"], "regulators": []},
            {"key": "cpg", "label": "Bens de consumo", "modules": ["lgpd"], "regulators": []},
        ],
    },
    "industry": {
        "label": "Indústria",
        "icon": "fa-industry",
        "subsectors": [
            {"key": "manufacturing", "label": "Manufatura", "modules": ["lgpd"], "regulators": []},
            {"key": "automotive", "label": "Automotivo", "modules": ["lgpd"], "regulators": []},
            {"key": "food_bev", "label": "Alimentos & bebidas", "modules": ["lgpd"], "regulators": ["ANVISA"]},
            {"key": "chemical", "label": "Química / petroquímica", "modules": ["lgpd"], "regulators": []},
            {"key": "construction", "label": "Construção / engenharia", "modules": ["lgpd"], "regulators": []},
        ],
    },
    "energy": {
        "label": "Energia & Utilities",
        "icon": "fa-bolt",
        "subsectors": [
            {"key": "power", "label": "Energia elétrica", "modules": ["lgpd"], "regulators": ["ANEEL"]},
            {"key": "oil_gas", "label": "Óleo & gás", "modules": ["lgpd"], "regulators": ["ANP"]},
            {"key": "sanitation", "label": "Saneamento", "modules": ["lgpd"], "regulators": ["ANA"]},
            {"key": "mining", "label": "Mineração", "modules": ["lgpd"], "regulators": ["ANM"]},
        ],
    },
    "public": {
        "label": "Setor público & Terceiro setor",
        "icon": "fa-building-columns",
        "subsectors": [
            {"key": "gov", "label": "Administração pública", "modules": ["lgpd"], "regulators": ["GSI/PR"], "norm": "PNCiber (Dec. 11.856/2023)"},
            {"key": "state_owned", "label": "Empresa estatal", "modules": ["lgpd"], "regulators": ["GSI/PR"], "norm": "E-Ciber (Dec. 10.222/2020)"},
            {"key": "ngo", "label": "ONG / terceiro setor", "modules": ["lgpd"], "regulators": []},
        ],
    },
    "services": {
        "label": "Serviços profissionais",
        "icon": "fa-briefcase",
        "subsectors": [
            {"key": "legal", "label": "Jurídico", "modules": ["lgpd"], "regulators": []},
            {"key": "accounting", "label": "Contábil / auditoria", "modules": ["lgpd"], "regulators": []},
            {"key": "consulting", "label": "Consultoria", "modules": ["lgpd"], "regulators": []},
            {"key": "education", "label": "Educação / edtech", "modules": ["lgpd"], "regulators": []},
            {"key": "logistics", "label": "Logística & transporte", "modules": ["lgpd"], "regulators": []},
            {"key": "agro", "label": "Agronegócio", "modules": ["lgpd"], "regulators": []},
        ],
    },
    "other": {
        "label": "Outro / híbrido",
        "icon": "fa-shapes",
        "subsectors": [
            {"key": "other", "label": "Outro / híbrido", "modules": ["lgpd"], "regulators": []},
        ],
    },
}


def sector_choices():
    return [(k, v["label"]) for k, v in TAXONOMY.items()]


def subsector_choices():
    out = []
    for sec in TAXONOMY.values():
        for sub in sec["subsectors"]:
            out.append((sub["key"], sub["label"]))
    return out


def subsector_index():
    """key do subsetor -> dict do subsetor (com modules/regulators)."""
    idx = {}
    for sec_key, sec in TAXONOMY.items():
        for sub in sec["subsectors"]:
            idx[sub["key"]] = {**sub, "sector": sec_key}
    return idx


def suggested_modules(subsector_key):
    return subsector_index().get(subsector_key, {}).get("modules", ["lgpd"])


def taxonomy_payload():
    """Estrutura aninhada para o wizard (setor -> subsetores com modules/regulators)."""
    return {
        k: {
            "label": v["label"],
            "icon": v.get("icon", ""),
            "subsectors": v["subsectors"],
        }
        for k, v in TAXONOMY.items()
    }
