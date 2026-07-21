"""Relatório PPTX de engajamento vCISO — deck executivo (tema Midnight Indigo).
Design system próprio (fonte sans, cards arredondados, narrativa). Retorna io.BytesIO."""
import io
from collections import Counter
from datetime import timedelta

from django.utils.timezone import now

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from core.models import Asset, ComplianceAssessment, RequirementAssessment
from .models import EngagementPhase, PlanTask, ClientIntake
from .services.eisenhower import derive_eisenhower

FONT = "Arial"

# ---- paleta Midnight Indigo ----
INK = RGBColor(0x0B, 0x10, 0x24)
INK2 = RGBColor(0x15, 0x1C, 0x38)
INDIGO = RGBColor(0x63, 0x66, 0xF1)
INDIGO_D = RGBColor(0x4F, 0x46, 0xE5)
VIOLET = RGBColor(0x8B, 0x5C, 0xF6)
SKY = RGBColor(0x0E, 0xA5, 0xE9)
EMERALD = RGBColor(0x10, 0xB9, 0x81)
AMBER = RGBColor(0xF5, 0x9E, 0x0B)
ROSE = RGBColor(0xEF, 0x44, 0x44)
S900 = RGBColor(0x0F, 0x17, 0x2A)
S700 = RGBColor(0x33, 0x41, 0x55)
S600 = RGBColor(0x47, 0x55, 0x69)
S500 = RGBColor(0x64, 0x74, 0x8B)
S400 = RGBColor(0x94, 0xA3, 0xB8)
S300 = RGBColor(0xCB, 0xD5, 0xE1)
S200 = RGBColor(0xE2, 0xE8, 0xF0)
S100 = RGBColor(0xF3, 0xF5, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

W, H = Inches(13.333), Inches(7.5)
MX = Inches(0.75)
CW = W - 2 * MX

SUBSECTOR = {
    "bank": "Banco / instituição de crédito",
    "asset_manager": "Gestora de Recursos (ANBIMA)",
    "broker": "Corretora / DTVM (CVM)",
    "other": "Grupo financeiro (híbrido)",
}


def _noshadow(sp):
    sp.shadow.inherit = False
    return sp


def bg(sl, color):
    sl.background.fill.solid()
    sl.background.fill.fore_color.rgb = color


def rrect(sl, l, t, w, h, fill, radius=0.06, line=None):
    sp = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    if line is not None:
        sp.line.color.rgb = line
        sp.line.width = Pt(1)
    else:
        sp.line.fill.background()
    try:
        sp.adjustments[0] = radius
    except Exception:
        pass
    return _noshadow(sp)


def rect(sl, l, t, w, h, fill):
    sp = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    return _noshadow(sp)


def text(sl, l, t, w, h, s, size=12, bold=False, color=S700,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.05):
    tb = sl.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    for i, ln in enumerate(str(s).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = ln
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return tb


def chips(sl, l, t, items, color=INDIGO, gap=0.14):
    x = l
    for label in items:
        w = Inches(0.11 * len(label) + 0.34)
        rrect(sl, x, t, w, Inches(0.36), color, radius=0.5)
        text(sl, x, t, w, Inches(0.36), label, 10.5, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += w + Inches(gap)


def new_slide(prs, color=WHITE):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    bg(sl, color)
    return sl


def header(sl, kicker, title, takeaway=None):
    text(sl, MX, Inches(0.55), CW, Inches(0.3), kicker.upper(), 11, bold=True, color=INDIGO)
    text(sl, MX, Inches(0.84), CW, Inches(0.55), title, 25, bold=True, color=S900)
    rect(sl, MX, Inches(1.42), Inches(0.6), Pt(3), INDIGO)
    if takeaway:
        text(sl, MX, Inches(1.58), CW, Inches(0.55), takeaway, 13, color=S500)


def footer(sl, page):
    text(sl, MX, H - Inches(0.48), Inches(6), Inches(0.3),
         "SURICATOOS vCISO  ·  CONFIDENCIAL", 9, bold=True, color=S400)
    text(sl, W - MX - Inches(1.5), H - Inches(0.48), Inches(1.5), Inches(0.3),
         str(page), 9, color=S400, align=PP_ALIGN.RIGHT)


def card(sl, l, t, w, h, accent=INDIGO, fill=S100):
    rrect(sl, l, t, w, h, fill, radius=0.05)
    rect(sl, l + Inches(0.0), t + Inches(0.18), Inches(0.06), h - Inches(0.36), accent)
    return l, t, w, h


def kpi(sl, l, t, w, h, label, value, sub=None, accent=INDIGO):
    card(sl, l, t, w, h, accent)
    px = l + Inches(0.28)
    pw = w - Inches(0.5)
    text(sl, px, t + Inches(0.24), pw, Inches(0.3), label.upper(), 9.5, bold=True, color=S500)
    text(sl, px, t + Inches(0.52), pw, Inches(0.7), value, 29, bold=True, color=accent)
    if sub:
        text(sl, px, t + h - Inches(0.56), pw, Inches(0.44), sub, 10, color=S500)


# =====================================================================
def build_engagement_pptx(engagement, lang="pt"):
    eng = engagement
    folder = eng.folder
    client = folder.name
    dz = eng.day_zero
    period = ""
    if dz:
        period = f"{dz.strftime('%d/%m/%Y')} — {(dz + timedelta(days=100)).strftime('%d/%m/%Y')}"

    phases = list(EngagementPhase.objects.filter(engagement=eng).order_by("order"))
    tasks = list(PlanTask.objects.filter(engagement=eng).select_related("applied_control", "phase"))
    contracted = float(eng.contracted_hours) if eng.contracted_hours is not None else None
    estimated = float(eng.estimated_hours_total)
    util = round(estimated / contracted * 100) if contracted else None
    monthly = (eng.sla or {}).get("monthly_hours") if isinstance(eng.sla, dict) else None

    quad = Counter()
    for pt in tasks:
        quad[derive_eisenhower(pt)["quadrant"]] += 1
    p1 = [pt for pt in tasks if pt.applied_control_id and pt.applied_control.priority == 1]

    assets = list(Asset.objects.filter(folder=folder).order_by("type", "name"))
    primary = [a for a in assets if a.type == "PR"]
    support = [a for a in assets if a.type == "SP"]

    cas = list(ComplianceAssessment.objects.filter(folder=folder).select_related("framework"))
    fw_info = []
    for ca in cas:
        n = RequirementAssessment.objects.filter(
            compliance_assessment=ca, requirement__assessable=True
        ).count()
        short = ca.framework.name.split("—")[0].split("-")[0].strip()[:34]
        fw_info.append((short, n))

    intake = ClientIntake.objects.filter(folder=folder).first()
    subsector = intake.subsector if (intake and intake.subsector) else ""
    if subsector:
        sector_label = SUBSECTOR.get(subsector, "Setor financeiro — mercado de capitais")
    else:
        fwset = " ".join(f[0] for f in fw_info).upper()
        if "ANBIMA" in fwset and "CVM" in fwset:
            sector_label = "Gestora de recursos · valores mobiliários (ANBIMA · CVM)"
        elif "ANBIMA" in fwset:
            sector_label = SUBSECTOR["asset_manager"]
        elif "CVM" in fwset:
            sector_label = SUBSECTOR["broker"]
        else:
            sector_label = "Setor financeiro — mercado de capitais"
    fw_chips = [f[0].replace("Resolução CVM nº 21/2021", "CVM 21") for f in fw_info] or ["—"]
    fw_chips = [c.replace("ANBIMA", "ANBIMA")[:22] for c in fw_chips]

    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    today = now().strftime("%d/%m/%Y")

    # ---------- S1 Capa ----------
    sl = new_slide(prs, INK)
    rect(sl, Inches(0), Inches(0), Inches(0.28), H, INDIGO)
    rrect(sl, W - Inches(3.05), Inches(0.55), Inches(2.3), Inches(0.5), INK2, radius=0.5, line=INDIGO)
    text(sl, W - Inches(3.05), Inches(0.55), Inches(2.3), Inches(0.5), "CONFIDENCIAL", 11,
         bold=True, color=INDIGO, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(sl, MX, Inches(2.55), CW, Inches(0.35), "RELATÓRIO DE ENGAJAMENTO vCISO", 13,
         bold=True, color=INDIGO)
    text(sl, MX, Inches(2.95), CW, Inches(1.1), client, 42, bold=True, color=WHITE)
    if period:
        text(sl, MX, Inches(4.35), CW, Inches(0.4), f"Plano de 100 dias  ·  {period}", 14, color=S300)
    text(sl, MX, Inches(4.8), CW, Inches(0.4), f"Status: {eng.get_status_display()}", 13, color=S400)
    text(sl, MX, H - Inches(0.85), Inches(6), Inches(0.35), "SURICATOOS vCISO", 12, bold=True, color=INDIGO)
    text(sl, W - MX - Inches(4), H - Inches(0.85), Inches(4), Inches(0.35),
         f"Gerado em {today}", 11, color=S400, align=PP_ALIGN.RIGHT)

    # ---------- S2 Contexto & escopo ----------
    sl = new_slide(prs)
    header(sl, "Cliente", "Contexto & escopo regulatório",
           "Quem é o cliente, o que regula a operação e como o engajamento está estruturado.")
    ct = Inches(2.4)
    ch = Inches(3.4)
    cw = (CW - Inches(0.4)) / 2
    card(sl, MX, ct, cw, ch, INDIGO)
    text(sl, MX + Inches(0.3), ct + Inches(0.25), cw - Inches(0.6), Inches(0.3), "PERFIL", 10, bold=True, color=S500)
    text(sl, MX + Inches(0.3), ct + Inches(0.6), cw - Inches(0.6), Inches(0.5), sector_label, 15, bold=True, color=S900)
    biz = "\n".join(f"•  {a.name}" for a in primary) or "•  (a mapear no diagnóstico)"
    text(sl, MX + Inches(0.3), ct + Inches(1.25), cw - Inches(0.6), Inches(2.0),
         "Unidades / funções de negócio:\n" + biz, 12, color=S600, spacing=1.25)
    x2 = MX + cw + Inches(0.4)
    card(sl, x2, ct, cw, ch, VIOLET)
    text(sl, x2 + Inches(0.3), ct + Inches(0.25), cw - Inches(0.6), Inches(0.3),
         "ESCOPO REGULATÓRIO", 10, bold=True, color=S500)
    chips(sl, x2 + Inches(0.3), ct + Inches(0.65), fw_chips[:4], color=INDIGO)
    text(sl, x2 + Inches(0.3), ct + Inches(1.3), cw - Inches(0.6), Inches(2.0),
         "Frameworks-alvo do gap-assessment do cliente, mais o piso legal do setor "
         "(CVM Res. 35/21 e CMN 4.893/21) a considerar na jornada.", 12, color=S600, spacing=1.25)
    # faixa modelo
    by = ct + ch + Inches(0.35)
    rrect(sl, MX, by, CW, Inches(0.75), S900, radius=0.12)
    model = f"Plano de 100 dias   ·   Retainer {monthly}h/mês   ·   Início {dz.strftime('%d/%m/%Y') if dz else '—'}"
    text(sl, MX, by, CW, Inches(0.75), model, 14, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    footer(sl, 2)

    # ---------- S3 Sumário executivo ----------
    sl = new_slide(prs)
    fase_atual = (phases[0].name.split("·")[-1].split("&")[0].strip() if phases else "Diagnóstico")
    header(sl, "Visão geral", "Sumário executivo",
           "Plano estabelecido; execução guiada por prioridade dentro do retainer.")
    ky = Inches(2.5)
    kh = Inches(2.0)
    kw = (CW - Inches(0.6)) / 4
    cards = [
        ("Fase atual", fase_atual, "0–30 dias", INDIGO),
        ("Tarefas do plano", str(len(tasks)), f"{len(phases)} fases", SKY),
        ("Esforço estimado", f"{estimated:g}h", "escopo completo", VIOLET),
        ("Retainer", f"{monthly or '—'}h/mês", "modelo budget", EMERALD),
    ]
    for i, (lb, v, sub, acc) in enumerate(cards):
        kpi(sl, MX + i * (kw + Inches(0.2)), ky, kw, kh, lb, v, sub, acc)
    band_y = ky + kh + Inches(0.45)
    rrect(sl, MX, band_y, CW, Inches(1.0), S100, radius=0.08)
    rect(sl, MX, band_y + Inches(0.18), Inches(0.06), Inches(0.64), AMBER)
    note = (f"Prioridade guia as {monthly}h/mês: das {len(tasks)} tarefas, "
            f"{quad.get('do', 0)} são urgentes+importantes (Fazer). O plano completo "
            f"({estimated:g}h) é maior que o retainer — executado como backlog priorizado.")
    text(sl, MX + Inches(0.3), band_y, CW - Inches(0.6), Inches(1.0), note, 13, color=S700,
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
    footer(sl, 3)

    # ---------- S4 Modelo de entrega ----------
    if contracted:
        sl = new_slide(prs)
        header(sl, "Modelo", f"Retainer {monthly}h/mês · execução priorizada",
               "O plano completo excede o retainer — por isso a priorização é o motor da entrega.")
        months = round(estimated / monthly, 1) if monthly else None
        # barra comparativa
        bx, bw = MX, CW
        y = Inches(2.7)
        text(sl, bx, y, bw, Inches(0.3), "Esforço do plano completo vs. capacidade do retainer", 12, bold=True, color=S700)
        bar_y = y + Inches(0.5)
        full_w = bw
        rrect(sl, bx, bar_y, full_w, Inches(0.5), S200, radius=0.3)
        win = float(contracted)
        frac = max(min(win / estimated, 1.0), 0.06)
        rrect(sl, bx, bar_y, int(full_w * frac), Inches(0.5), EMERALD, radius=0.3)
        text(sl, bx, bar_y + Inches(0.6), bw, Inches(0.3),
             f"Orçamento da janela (100 dias): {contracted:g}h", 11, color=EMERALD, bold=True)
        text(sl, bx, bar_y + Inches(0.6), bw, Inches(0.3),
             f"Plano completo: {estimated:g}h", 11, color=S500, align=PP_ALIGN.RIGHT)
        # 3 cartões de leitura
        cy = bar_y + Inches(1.3)
        cw3 = (CW - Inches(0.6)) / 3
        chh = Inches(1.7)
        facts = [
            ("Utilização na janela", f"{util}%", "esforço estimado ÷ orçamento", ROSE),
            ("Ritmo de execução", f"~{months} meses", f"plano completo a {monthly}h/mês", AMBER),
            ("O que decide o mês", "Prioridade", "Eisenhower + tarefas P1", INDIGO),
        ]
        for i, (lb, v, sub, acc) in enumerate(facts):
            kpi(sl, MX + i * (cw3 + Inches(0.3)), cy, cw3, chh, lb, v, sub, acc)
        footer(sl, 4)

    # ---------- S5 Roadmap ----------
    sl = new_slide(prs)
    header(sl, "Plano", "Roadmap de 100 dias · 3 fases",
           "Diagnóstico → Quick Wins & Roadmap → Execução & Governança.")
    py = Inches(2.4)
    ph_h = Inches(3.7)
    pw = (CW - Inches(0.6)) / 3
    accents = [INDIGO, VIOLET, SKY]
    for i, ph in enumerate(phases[:3]):
        px = MX + i * (pw + Inches(0.3))
        card(sl, px, py, pw, ph_h, accents[i % 3])
        ix = px + Inches(0.3)
        iw = pw - Inches(0.6)
        text(sl, ix, py + Inches(0.25), iw, Inches(0.3), f"FASE {ph.order}", 10, bold=True, color=accents[i % 3])
        nm = ph.name.split("·")[-1].strip()
        text(sl, ix, py + Inches(0.55), iw, Inches(0.6), nm, 15, bold=True, color=S900)
        rng = f"Dia {ph.day_start}–{ph.day_end}"
        if ph.date_start and ph.date_end:
            rng += f"\n{ph.date_start.strftime('%d/%m')} – {ph.date_end.strftime('%d/%m')}"
        text(sl, ix, py + Inches(1.3), iw, Inches(0.7), rng, 11, color=S500, spacing=1.2)
        text(sl, ix, py + Inches(2.15), iw, Inches(0.9),
             (ph.objective or "")[:130], 11, color=S600, spacing=1.2)
        ph_tasks = [pt for pt in tasks if pt.phase_id == ph.id]
        hrs = sum((pt.estimated_hours or 0) for pt in ph_tasks)
        rrect(sl, ix, py + ph_h - Inches(0.7), iw, Inches(0.5), S200, radius=0.2)
        text(sl, ix, py + ph_h - Inches(0.7), iw, Inches(0.5),
             f"{len(ph_tasks)} tarefas  ·  {float(hrs):g}h", 11, bold=True, color=S700,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    footer(sl, 5)

    # ---------- S6 Eisenhower ----------
    sl = new_slide(prs)
    header(sl, "Priorização", "Matriz de Eisenhower",
           "Como as tarefas do plano se distribuem — e o que entra primeiro no retainer.")
    quads = [
        ("do", "Fazer", "urgente + importante", ROSE),
        ("schedule", "Agendar", "importante", INDIGO),
        ("delegate", "Delegar", "urgente", AMBER),
        ("eliminate", "Eliminar", "nem urgente nem importante", S500),
    ]
    gx, gy = MX, Inches(2.2)
    qcw = (CW - Inches(0.4)) / 2
    qch = Inches(2.0)
    pos = [(gx, gy), (gx + qcw + Inches(0.4), gy),
           (gx, gy + qch + Inches(0.3)), (gx + qcw + Inches(0.4), gy + qch + Inches(0.3))]
    for (key, title, sub, acc), (x, y) in zip(quads, pos):
        card(sl, x, y, qcw, qch, acc)
        text(sl, x + Inches(0.35), y + Inches(0.3), qcw - Inches(0.7), Inches(0.4), title, 15, bold=True, color=S900)
        text(sl, x + Inches(0.35), y + Inches(0.7), qcw - Inches(0.7), Inches(0.3), sub, 10.5, color=S500)
        text(sl, x + Inches(0.35), y + Inches(1.05), qcw - Inches(0.7), Inches(1.0),
             str(quad.get(key, 0)), 40, bold=True, color=acc)
    footer(sl, 6)

    # ---------- S7 Foco P1 ----------
    if p1:
        sl = new_slide(prs)
        header(sl, "Foco", "Prioridades imediatas (P1)",
               f"As {len(p1)} tarefas P1 guiam o retainer — as primeiras por prazo abaixo.")
        y = Inches(2.35)
        for i, pt in enumerate(p1[:9]):
            ac = pt.applied_control
            rowbg = S100 if i % 2 == 0 else WHITE
            rrect(sl, MX, y, CW, Inches(0.46), rowbg, radius=0.12)
            rect(sl, MX + Inches(0.0), y + Inches(0.08), Inches(0.05), Inches(0.3), INDIGO)
            text(sl, MX + Inches(0.25), y, Inches(8.2), Inches(0.46), ac.name[:70], 12, bold=True,
                 color=S900, anchor=MSO_ANCHOR.MIDDLE)
            ph_nm = pt.phase.name.split("·")[-1].strip() if pt.phase_id else ""
            text(sl, MX + Inches(8.5), y, Inches(2.6), Inches(0.46), ph_nm[:26], 10.5,
                 color=S500, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, W - MX - Inches(1.3), y, Inches(1.3), Inches(0.46),
                 ac.eta.strftime("%d/%m/%Y") if ac.eta else "", 10.5, color=S500,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
            y += Inches(0.5)
        footer(sl, 7)

    # ---------- S8 Frameworks & gap-assessment ----------
    if fw_info:
        sl = new_slide(prs)
        header(sl, "Conformidade", "Frameworks & gap-assessment",
               "Bases regulatórias estruturadas e prontas para avaliação de aderência.")
        y = Inches(2.4)
        fcw = (CW - Inches(0.4)) / max(len(fw_info[:3]), 1)
        for i, (nm, n) in enumerate(fw_info[:3]):
            x = MX + i * (fcw + Inches(0.2))
            card(sl, x, y, fcw, Inches(2.6), [INDIGO, VIOLET, SKY][i % 3])
            text(sl, x + Inches(0.3), y + Inches(0.3), fcw - Inches(0.6), Inches(0.9), nm, 15, bold=True, color=S900)
            text(sl, x + Inches(0.3), y + Inches(1.3), fcw - Inches(0.6), Inches(0.4),
                 f"{n}", 30, bold=True, color=[INDIGO, VIOLET, SKY][i % 3])
            text(sl, x + Inches(0.3), y + Inches(1.95), fcw - Inches(0.6), Inches(0.4),
                 "requisitos avaliáveis", 11, color=S500)
        text(sl, MX, y + Inches(2.9), CW, Inches(0.5),
             "Status: gap-assessments criados no domínio do cliente, prontos para avaliação. "
             "Conteúdo construído de fonte oficial — requer validação de compliance antes do uso formal.",
             11, color=S500, spacing=1.2)
        footer(sl, 8)

    # ---------- S9 Ativos ----------
    sl = new_slide(prs)
    header(sl, "Ativos", "Ativos & superfície mapeada",
           "Superfície pública identificada; o inventário interno é a primeira entrega do diagnóstico.")
    y = Inches(2.4)
    colw = (CW - Inches(0.4)) / 2
    ah = Inches(2.7)
    card(sl, MX, y, colw, ah, INDIGO)
    text(sl, MX + Inches(0.3), y + Inches(0.28), colw - Inches(0.6), Inches(0.3),
         "FUNÇÕES DE NEGÓCIO (PRIMARY)", 10, bold=True, color=S500)
    text(sl, MX + Inches(0.3), y + Inches(0.75), colw - Inches(0.6), Inches(1.8),
         "\n".join(f"•  {a.name}" for a in primary) or "—", 13, color=S700, spacing=1.4)
    x2 = MX + colw + Inches(0.4)
    card(sl, x2, y, colw, ah, SKY)
    text(sl, x2 + Inches(0.3), y + Inches(0.28), colw - Inches(0.6), Inches(0.3),
         "SUPERFÍCIE PÚBLICA (SUPPORT)", 10, bold=True, color=S500)
    text(sl, x2 + Inches(0.3), y + Inches(0.75), colw - Inches(0.6), Inches(1.8),
         "\n".join(f"•  {a.name}" for a in support) or "—", 13, color=S700, spacing=1.4)
    text(sl, MX, y + ah + Inches(0.3), CW, Inches(0.4),
         "Sistemas internos, bases de dados sensíveis e fornecedores críticos serão inventariados "
         "na Fase 1 (Inventário de ativos e dados).", 11, color=S500, spacing=1.2)
    footer(sl, 9)

    # ---------- S10 Próximos passos ----------
    sl = new_slide(prs)
    header(sl, "Ação", "Próximos passos", "O que destrava a execução das primeiras semanas.")
    steps = [
        ("Constituir o time de entrega", "Atribuir o vCISO e analistas ao domínio do cliente (acesso e responsabilidades)."),
        ("Inventário de ativos e dados", "Levantar sistemas internos, dados sensíveis e fornecedores críticos (Fase 1)."),
        ("Iniciar os gap-assessments", "Avaliar aderência a CVM/ANBIMA a partir das bases já estruturadas."),
        ("Executar os quick wins P1", "Atacar as tarefas urgentes+importantes dentro do retainer do mês."),
    ]
    y = Inches(2.35)
    for i, (t, d) in enumerate(steps):
        rrect(sl, MX, y, CW, Inches(0.95), S100, radius=0.08)
        rrect(sl, MX + Inches(0.25), y + Inches(0.22), Inches(0.5), Inches(0.5), INDIGO, radius=0.5)
        text(sl, MX + Inches(0.25), y + Inches(0.22), Inches(0.5), Inches(0.5), str(i + 1), 16,
             bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, MX + Inches(1.0), y + Inches(0.16), CW - Inches(1.3), Inches(0.35), t, 14, bold=True, color=S900)
        text(sl, MX + Inches(1.0), y + Inches(0.52), CW - Inches(1.3), Inches(0.35), d, 11.5, color=S600)
        y += Inches(1.1)
    footer(sl, 10)

    # ---------- S11 Encerramento ----------
    sl = new_slide(prs, INK)
    rect(sl, Inches(0), Inches(0), Inches(0.28), H, INDIGO)
    text(sl, MX, Inches(2.9), CW, Inches(1.0), "Obrigado", 46, bold=True, color=WHITE)
    text(sl, MX, Inches(4.0), CW, Inches(0.5),
         "Programa vCISO · Suricatoos", 16, color=S300)
    text(sl, MX, Inches(4.5), CW, Inches(0.4), "vciso.suricatoos.com", 14, bold=True, color=INDIGO)

    out = io.BytesIO()
    prs.save(out)
    out.seek(0)
    return out
