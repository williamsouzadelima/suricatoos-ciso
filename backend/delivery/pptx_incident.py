"""Relatório pós-incidente (PIR) em PPTX — reusa VERBATIM o toolkit de slides do
pptx_engagement.py (tema Midnight Indigo). Retorna io.BytesIO. Agregação read-only up-front,
slides condicionais por presença de dado (mesmo padrão do deck de engajamento)."""
import io

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from django.utils.timezone import now

from .pptx_engagement import (
    new_slide, header, footer, card, kpi, chips, text, rrect, rect, bg,
    _picture, _provider_logo,
    W, H, MX, CW,
    INK, INK2, INDIGO, VIOLET, SKY, EMERALD, AMBER, ROSE,
    S900, S700, S600, S500, S400, S300, S200, S100, WHITE,
)
from .services.incident_cost import compute_incident_cost


def _fmt_dt(dt):
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"


def build_incident_pptx(incident, lang="pt"):
    # ---- agregação read-only ----
    plan = getattr(incident, "response_plan", None)
    cost = compute_incident_cost(incident)
    phases = list(incident.ir_phases.all().order_by("order"))
    tasks = list(
        incident.ir_tasks.select_related("phase", "applied_control").all()
    )
    roles = list(incident.ir_roles.select_related("actor").all())
    stakeholders = list(incident.ir_stakeholders.all().order_by("order", "party"))
    notifs = list(incident.ir_notifications.all().order_by("regulator"))
    timeline = list(incident.timeline_entries.all().order_by("timestamp"))
    tasks_by_phase = {}
    for t in tasks:
        tasks_by_phase.setdefault(t.phase_id, []).append(t)
    # evidências via timeline
    evidences = []
    for te in timeline:
        for ev in te.evidences.all():
            evidences.append(ev.name)
    for n in notifs:
        for ev in n.evidences.all():
            evidences.append(ev.name)
    evidences = list(dict.fromkeys(evidences))  # dedup preservando ordem

    sev = incident.get_severity_display()
    status = incident.get_status_display()
    reported = incident.reported_at
    resolved = incident.resolved_at
    duration = None
    if reported and resolved:
        hrs = max((resolved - reported).total_seconds() / 3600.0, 0.0)
        duration = f"{hrs:.0f}h"

    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    today = now().strftime("%d/%m/%Y")
    plogo = _provider_logo()
    page = 0

    # ---------- S1 Capa ----------
    sl = new_slide(prs, INK)
    rect(sl, Inches(0), Inches(0), Inches(0.28), H, ROSE)
    rrect(sl, W - Inches(3.05), Inches(0.55), Inches(2.3), Inches(0.5), INK2, radius=0.5, line=ROSE)
    text(sl, W - Inches(3.05), Inches(0.55), Inches(2.3), Inches(0.5), "CONFIDENCIAL", 11,
         bold=True, color=ROSE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if plogo:
        _picture(sl, plogo, MX, Inches(0.5), Inches(2.4), Inches(0.62))
    text(sl, MX, Inches(2.4), CW, Inches(0.35), "RELATÓRIO PÓS-INCIDENTE (PIR)", 13,
         bold=True, color=ROSE)
    text(sl, MX, Inches(2.8), CW, Inches(1.3), incident.name, 38, bold=True, color=WHITE)
    text(sl, MX, Inches(4.35), CW, Inches(0.4),
         f"Severidade: {sev}   ·   Status: {status}", 14, color=S300)
    text(sl, MX, Inches(4.8), CW, Inches(0.4),
         f"Reportado: {_fmt_dt(reported)}   ·   Resolvido: {_fmt_dt(resolved)}", 13, color=S400)
    text(sl, MX, H - Inches(0.85), Inches(6), Inches(0.35), "SURICATOOS vCISO", 12, bold=True, color=ROSE)
    text(sl, W - MX - Inches(4), H - Inches(0.85), Inches(4), Inches(0.35),
         f"Gerado em {today}", 11, color=S400, align=PP_ALIGN.RIGHT)

    # ---------- S2 Sumário executivo ----------
    page += 1
    sl = new_slide(prs)
    header(sl, "Visão geral", "Sumário executivo",
           "Panorama do incidente, resposta e impacto financeiro estimado.")
    ky, kh = Inches(2.5), Inches(1.9)
    kw = (CW - Inches(0.6)) / 4
    kpis = [
        ("Severidade", sev, incident.get_status_display(), ROSE),
        ("Duração", duration or "em curso", "reportado→resolvido", AMBER),
        ("Atividades", str(len(tasks)), f"{len(phases)} fases", INDIGO),
        ("Custo total", cost["total_fmt"], "P&L do incidente", EMERALD),
    ]
    for i, (lb, v, sub, acc) in enumerate(kpis):
        kpi(sl, MX + i * (kw + Inches(0.2)), ky, kw, kh, lb, v, sub, acc)
    band_y = ky + kh + Inches(0.4)
    summary = (plan.exec_summary if (plan and plan.exec_summary) else
               "Resumo executivo a preencher no encerramento do incidente.")
    rrect(sl, MX, band_y, CW, Inches(1.5), S100, radius=0.06)
    text(sl, MX + Inches(0.3), band_y + Inches(0.2), CW - Inches(0.6), Inches(1.1),
         summary, 12.5, color=S600, spacing=1.25)
    if incident.is_bcp_activated:
        text(sl, MX, band_y + Inches(1.6), CW, Inches(0.3),
             "⚠  Plano de continuidade de negócios (BCP) ativado durante o incidente.",
             12, bold=True, color=AMBER)
    footer(sl, page)

    # ---------- S3 Linha do tempo ----------
    if timeline:
        page += 1
        sl = new_slide(prs)
        header(sl, "Cronologia", "Linha do tempo do incidente")
        y = Inches(2.3)
        for te in timeline[:11]:
            rrect(sl, MX, y, Inches(2.4), Inches(0.5), S100, radius=0.2)
            text(sl, MX, y, Inches(2.4), Inches(0.5), _fmt_dt(te.timestamp), 10.5,
                 bold=True, color=S700, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            label = te.get_entry_type_display()
            text(sl, MX + Inches(2.6), y, Inches(2.0), Inches(0.5), label, 11, bold=True,
                 color=INDIGO, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, MX + Inches(4.7), y, CW - Inches(4.7), Inches(0.5),
                 (te.entry or te.observation or "")[:120], 11, color=S600,
                 anchor=MSO_ANCHOR.MIDDLE)
            y += Inches(0.62)
        footer(sl, page)

    # ---------- S4 Runbook / fases ----------
    if phases:
        page += 1
        sl = new_slide(prs)
        header(sl, "Resposta", "Runbook — fases e atividades",
               f"Plano {plan.get_standard_display() if plan else 'NIST SP 800-61'}.")
        cw = (CW - Inches(0.6)) / 2
        positions = [
            (MX, Inches(2.3)), (MX + cw + Inches(0.6), Inches(2.3)),
            (MX, Inches(4.55)), (MX + cw + Inches(0.6), Inches(4.55)),
        ]
        accents = [INDIGO, SKY, AMBER, EMERALD]
        for i, ph in enumerate(phases[:4]):
            l, t = positions[i]
            ch = Inches(2.05)
            card(sl, l, t, cw, ch, accents[i % 4])
            pts = tasks_by_phase.get(ph.id, [])
            text(sl, l + Inches(0.3), t + Inches(0.22), cw - Inches(0.6), Inches(0.5),
                 ph.name, 13, bold=True, color=S900)
            names = "\n".join(f"•  {p.applied_control.name if p.applied_control else '—'}"
                              for p in pts[:5]) or "•  (sem atividades)"
            text(sl, l + Inches(0.3), t + Inches(0.72), cw - Inches(0.6), Inches(1.2),
                 names, 10.5, color=S600, spacing=1.15)
        footer(sl, page)

    # ---------- S5 Time & RACI ----------
    if roles:
        page += 1
        sl = new_slide(prs)
        header(sl, "Equipe", "Time de resposta & RACI")
        y = Inches(2.3)
        rrect(sl, MX, y, CW, Inches(0.44), S900, radius=0.08)
        text(sl, MX + Inches(0.2), y, Inches(4.5), Inches(0.44), "PAPEL", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, MX + Inches(5.0), y, Inches(4.5), Inches(0.44), "RESPONSÁVEL", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, W - MX - Inches(2.2), y, Inches(2.0), Inches(0.44), "RACI", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        y += Inches(0.5)
        for i, r in enumerate(roles[:9]):
            if i % 2 == 0:
                rrect(sl, MX, y, CW, Inches(0.46), S100, radius=0.05)
            text(sl, MX + Inches(0.2), y, Inches(4.6), Inches(0.46), r.get_role_display(),
                 11.5, bold=True, color=S700, anchor=MSO_ANCHOR.MIDDLE)
            actor = str(r.actor) if r.actor_id else "—"
            text(sl, MX + Inches(5.0), y, Inches(4.5), Inches(0.46), actor, 11.5, color=S600,
                 anchor=MSO_ANCHOR.MIDDLE)
            text(sl, W - MX - Inches(2.2), y, Inches(2.0), Inches(0.46), r.get_raci_display(),
                 11.5, color=INDIGO, anchor=MSO_ANCHOR.MIDDLE)
            y += Inches(0.5)
        footer(sl, page)

    # ---------- S5b Matriz de comunicação (stakeholders) ----------
    if stakeholders:
        page += 1
        sl = new_slide(prs)
        header(sl, "Comunicações", "Matriz de comunicação (stakeholders)",
               "Quem informar, quando, por qual canal e o status da comunicação.")
        _stcolor = {"pending": AMBER, "notified": SKY, "acknowledged": EMERALD, "not_required": S400}
        y = Inches(2.3)
        rrect(sl, MX, y, CW, Inches(0.44), S900, radius=0.08)
        text(sl, MX + Inches(0.2), y, Inches(4.5), Inches(0.44), "STAKEHOLDER", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, MX + Inches(5.0), y, Inches(2.6), Inches(0.44), "QUANDO", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, MX + Inches(7.8), y, Inches(2.4), Inches(0.44), "CANAL", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, W - MX - Inches(2.0), y, Inches(2.0), Inches(0.44), "STATUS", 10, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        y += Inches(0.5)
        for i, sh in enumerate(stakeholders[:10]):
            if i % 2 == 0:
                rrect(sl, MX, y, CW, Inches(0.44), S100, radius=0.05)
            text(sl, MX + Inches(0.2), y, Inches(4.7), Inches(0.44),
                 f"{sh.name}", 10.5, bold=True, color=S700, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, MX + Inches(5.0), y, Inches(2.6), Inches(0.44),
                 sh.get_when_to_notify_display(), 10, color=S600, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, MX + Inches(7.8), y, Inches(2.4), Inches(0.44),
                 (sh.channel or "—")[:26], 10, color=S600, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, W - MX - Inches(2.0), y, Inches(2.0), Inches(0.44),
                 sh.get_status_display(), 10, bold=True,
                 color=_stcolor.get(sh.status, S400), align=PP_ALIGN.RIGHT,
                 anchor=MSO_ANCHOR.MIDDLE)
            y += Inches(0.48)
        footer(sl, page)

    # ---------- S6 Comunicações & clock regulatório ----------
    if notifs:
        page += 1
        sl = new_slide(prs)
        header(sl, "Comunicações", "Notificações regulatórias",
               "Obrigações do(s) regulador(es) do cliente. Prazos requerem validação de compliance.")
        y = Inches(2.4)
        for n in notifs[:8]:
            rrect(sl, MX, y, CW, Inches(0.56), S100, radius=0.05)
            text(sl, MX + Inches(0.25), y, Inches(2.2), Inches(0.56), n.regulator, 12,
                 bold=True, color=S900, anchor=MSO_ANCHOR.MIDDLE)
            prazo = (f"{n.deadline_hours}h" if n.deadline_hours else "tempestivo")
            acc = ROSE if n.is_overdue else INDIGO
            text(sl, MX + Inches(2.5), y, CW - Inches(4.6), Inches(0.56),
                 n.obligation_ref[:80], 10.5, color=S600, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, W - MX - Inches(2.0), y, Inches(1.9), Inches(0.56),
                 f"{prazo} · {n.get_status_display()}", 10.5, bold=True, color=acc,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
            y += Inches(0.64)
        footer(sl, page)

    # ---------- S7 Evidências ----------
    if evidences:
        page += 1
        sl = new_slide(prs)
        header(sl, "Forense", "Registro de evidências")
        ev_txt = "\n".join(f"•  {name}" for name in evidences[:16])
        text(sl, MX, Inches(2.4), CW, Inches(4.0), ev_txt, 12.5, color=S600, spacing=1.3)
        footer(sl, page)

    # ---------- S8 P&L do incidente ----------
    page += 1
    sl = new_slide(prs)
    header(sl, "Financeiro", "P&L do incidente",
           "Custo determinístico: esforço + impacto de negócio + fornecedores + multas.")
    ky, kh = Inches(2.4), Inches(1.9)
    kw = (CW - Inches(0.6)) / 4
    _basis = "apontadas" if cost.get("effort_basis") == "logged" else "estimadas"
    pnl = [
        ("Esforço de resposta", cost["response_effort_fmt"], f"{cost.get('effort_hours', cost['estimated_hours']):.0f}h {_basis}", INDIGO),
        ("Impacto de negócio", cost["business_impact_fmt"], f"{cost['downtime_hours']:.0f}h downtime", VIOLET),
        ("Fornecedores", cost["external_vendor_fmt"], "forense/jurídico", SKY),
        ("Multas", cost["regulatory_fines_fmt"], "regulatórias", ROSE),
    ]
    for i, (lb, v, sub, acc) in enumerate(pnl):
        kpi(sl, MX + i * (kw + Inches(0.2)), ky, kw, kh, lb, v, sub, acc)
    band_y = ky + kh + Inches(0.4)
    rrect(sl, MX, band_y, CW, Inches(0.9), S900, radius=0.1)
    text(sl, MX, band_y, CW, Inches(0.9),
         f"CUSTO TOTAL ESTIMADO   ·   {cost['total_fmt']}", 20, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if cost["by_asset"]:
        y = band_y + Inches(1.1)
        by = "   ".join(f"{a['catalog']}: {a['total_fmt']}" for a in cost["by_asset"][:4])
        text(sl, MX, y, CW, Inches(0.5), "Por catálogo de negócio:  " + by, 11, color=S500)
    footer(sl, page)

    # ---------- S9 Lições aprendidas / encerramento ----------
    page += 1
    sl = new_slide(prs)
    header(sl, "Pós-incidente", "Lições aprendidas & próximos passos")
    lessons = (plan.lessons_learned if (plan and plan.lessons_learned) else
               "Lições aprendidas a consolidar na reunião de pós-incidente.")
    text(sl, MX, Inches(2.4), CW, Inches(2.0), lessons, 13, color=S600, spacing=1.3)
    resolution = incident.resolution or ""
    if resolution:
        text(sl, MX, Inches(4.6), CW, Inches(0.3), "RESOLUÇÃO", 10, bold=True, color=S500)
        text(sl, MX, Inches(4.95), CW, Inches(1.4), resolution, 12, color=S600, spacing=1.25)
    footer(sl, page)

    out = io.BytesIO()
    prs.save(out)
    out.seek(0)
    return out
