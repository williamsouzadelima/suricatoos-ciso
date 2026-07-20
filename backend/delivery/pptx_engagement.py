"""Relatório PPTX de engajamento vCISO (tema Suricatoos Navy). Reusa os helpers de desenho
de core.pptx_generator e os charts de core.generators. Retorna io.BytesIO."""
import io
from collections import Counter
from datetime import timedelta

from pptx import Presentation
from pptx.util import Inches
from pptx.enum.text import PP_ALIGN

from core.pptx_generator import (
    _bg,
    _box,
    _rect,
    _img,
    _header,
    NAVY,
    BLUE,
    EMERALD,
    AMBER,
    ROSE,
    GRAY,
    SLATE7,
    SLATE5,
    SLATE4,
    SLATE1,
    WHITE,
    W,
    H,
    M,
)
from core.generators import plot_donut

from .models import EngagementPhase, PlanTask
from .services.eisenhower import derive_eisenhower


def _slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def _phase_short(name):
    return (name or "").split("·")[0].strip()[:26]


def build_engagement_pptx(engagement, lang="pt"):
    eng = engagement
    folder = eng.folder
    client = folder.name
    day_zero = eng.day_zero
    period = ""
    if day_zero:
        end = day_zero + timedelta(days=100)
        period = f"{day_zero.strftime('%d/%m/%Y')} — {end.strftime('%d/%m/%Y')}"

    phases = list(EngagementPhase.objects.filter(engagement=eng).order_by("order"))
    tasks = list(
        PlanTask.objects.filter(engagement=eng).select_related(
            "applied_control", "phase"
        )
    )
    contracted = float(eng.contracted_hours) if eng.contracted_hours is not None else None
    estimated = float(eng.estimated_hours_total)
    logged = float(eng.logged_hours_total)
    util = round(estimated / contracted * 100, 1) if contracted else None
    over = contracted is not None and estimated > contracted

    status_counter = Counter()
    quad_counter = Counter()
    for pt in tasks:
        if pt.applied_control_id:
            status_counter[pt.applied_control.status] += 1
        quad_counter[derive_eisenhower(pt)["quadrant"]] += 1
    total_tasks = len(tasks)
    done_tasks = status_counter.get("active", 0)

    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    # ---- Slide 1: capa ----
    sl = _slide(prs)
    _bg(sl, NAVY)
    _rect(sl, Inches(0), Inches(0), Inches(0.35), H, BLUE)
    _box(sl, M, Inches(2.1), Inches(11), Inches(0.6),
         "Relatório de Engajamento vCISO", 20, bold=True, color=SLATE4)
    _box(sl, M, Inches(2.7), Inches(11.8), Inches(1.3), client, 40, bold=True, color=WHITE)
    if period:
        _box(sl, M, Inches(4.1), Inches(11), Inches(0.5),
             f"Plano de 100 dias · {period}", 14, color=SLATE4)
    _box(sl, M, Inches(4.6), Inches(11), Inches(0.5),
         f"Status: {eng.get_status_display()}", 14, color=SLATE4)
    _box(sl, M, Inches(6.6), Inches(6), Inches(0.4),
         "SURICATOOS vCISO", 12, bold=True, color=BLUE)
    _rect(sl, Inches(10.8), Inches(0.5), Inches(2.0), Inches(0.5), ROSE)
    _box(sl, Inches(10.8), Inches(0.57), Inches(2.0), Inches(0.4),
         "CONFIDENCIAL", 11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # ---- Slide 2: sumário executivo (KPI cards) ----
    sl = _slide(prs)
    _bg(sl, WHITE)
    _header(sl, "Sumário Executivo")
    cards = [
        ("Horas contratadas", "—" if contracted is None else f"{contracted:g}", BLUE),
        ("Horas estimadas", f"{estimated:g}", SLATE7),
        ("Utilização", "—" if util is None else f"{util:g}%", ROSE if over else EMERALD),
        ("Tarefas", str(total_tasks), SLATE7),
        ("Concluídas", f"{done_tasks}/{total_tasks}", EMERALD),
    ]
    cw, ch, gap = Inches(2.3), Inches(2.0), Inches(0.2)
    total_w = 5 * cw + 4 * gap
    x0 = int((W - total_w) / 2)
    y0 = Inches(2.4)
    for i, (label, value, color) in enumerate(cards):
        x = x0 + i * (cw + gap)
        _rect(sl, x, y0, cw, ch, SLATE1)
        _rect(sl, x, y0, cw, Inches(0.12), color)
        _box(sl, x, y0 + Inches(0.55), cw, Inches(0.9), value, 34, bold=True,
             color=color, align=PP_ALIGN.CENTER)
        _box(sl, x, y0 + ch - Inches(0.6), cw, Inches(0.5), label, 12,
             color=SLATE5, align=PP_ALIGN.CENTER)
    if over:
        _box(sl, M, Inches(5.1), W - 2 * M, Inches(0.5),
             "Atencao: esforco estimado acima do orcamento contratado.", 13,
             bold=True, color=ROSE, align=PP_ALIGN.CENTER)

    # ---- Slide 3: esforço por fase (donut) ----
    phase_hours = [
        {
            "category": _phase_short(p.name),
            "value": float(sum((pt.estimated_hours or 0) for pt in tasks if pt.phase_id == p.id)),
        }
        for p in phases
    ]
    if any(d["value"] for d in phase_hours):
        sl = _slide(prs)
        _bg(sl, WHITE)
        _header(sl, "Esforco estimado por fase")
        buf = plot_donut(phase_hours)
        _img(sl, buf, M, Inches(1.2), width=Inches(7.6))
        ly = Inches(2.2)
        for d in phase_hours:
            _box(sl, Inches(8.4), ly, Inches(4.4), Inches(0.5),
                 f"{d['category']}: {d['value']:g}h", 14, color=SLATE7)
            ly += Inches(0.7)

    # ---- Slide 4: progresso por fase ----
    sl = _slide(prs)
    _bg(sl, WHITE)
    _header(sl, "Progresso por fase")
    y = Inches(1.6)
    for p in phases:
        ph_tasks = [pt for pt in tasks if pt.phase_id == p.id]
        n = len(ph_tasks)
        done = sum(1 for pt in ph_tasks if pt.applied_control_id and pt.applied_control.status == "active")
        pct = round(done / n * 100) if n else 0
        _box(sl, M, y, Inches(9), Inches(0.4), p.name, 13, bold=True, color=SLATE7)
        _box(sl, Inches(11.3), y, Inches(1.5), Inches(0.4), f"{done}/{n}", 13,
             color=SLATE5, align=PP_ALIGN.RIGHT)
        bar_y = y + Inches(0.5)
        _rect(sl, M, bar_y, Inches(12.3), Inches(0.35), SLATE1)
        if pct:
            _rect(sl, M, bar_y, Inches(12.3 * pct / 100), Inches(0.35), EMERALD)
        y += Inches(1.45)

    # ---- Slide 5: matriz de Eisenhower ----
    sl = _slide(prs)
    _bg(sl, WHITE)
    _header(sl, "Matriz de Eisenhower")
    quads = [
        ("do", "Fazer (urgente + importante)", ROSE),
        ("schedule", "Agendar (importante)", BLUE),
        ("delegate", "Delegar (urgente)", AMBER),
        ("eliminate", "Eliminar", GRAY),
    ]
    cw2, ch2, gap2 = Inches(5.8), Inches(2.4), Inches(0.3)
    x0 = M + Inches(0.4)
    y0 = Inches(1.4)
    positions = [
        (x0, y0),
        (x0 + cw2 + gap2, y0),
        (x0, y0 + ch2 + gap2),
        (x0 + cw2 + gap2, y0 + ch2 + gap2),
    ]
    for (key, label, color), (x, y) in zip(quads, positions):
        _rect(sl, x, y, cw2, ch2, SLATE1)
        _rect(sl, x, y, Inches(0.12), ch2, color)
        _box(sl, x + Inches(0.3), y + Inches(0.2), cw2 - Inches(0.6), Inches(0.5),
             label, 13, bold=True, color=SLATE7)
        _box(sl, x + Inches(0.3), y + Inches(0.7), cw2 - Inches(0.6), Inches(1.3),
             str(quad_counter.get(key, 0)), 44, bold=True, color=color)

    # ---- Slide 6: tarefas P1 ----
    p1 = [pt for pt in tasks if pt.applied_control_id and pt.applied_control.priority == 1]
    if p1:
        sl = _slide(prs)
        _bg(sl, WHITE)
        _header(sl, "Tarefas prioritarias (P1)")
        cols = [("Tarefa", Inches(7.2)), ("Fase", Inches(3.5)), ("Prazo", Inches(1.6))]
        x, y, rh = M, Inches(1.2), Inches(0.5)
        for hdr, w in cols:
            _rect(sl, x, y, w, rh, SLATE7)
            _box(sl, x + Inches(0.08), y + Inches(0.08), w - Inches(0.16), rh,
                 hdr, 11, bold=True)
            x += w
        y += rh
        for i, pt in enumerate(p1[:11]):
            ac = pt.applied_control
            rowbg = SLATE1 if i % 2 else WHITE
            x = M
            vals = [ac.name, _phase_short(pt.phase.name) if pt.phase_id else "", str(ac.eta or "")]
            for (hdr, w), val in zip(cols, vals):
                _rect(sl, x, y, w, rh, rowbg)
                _box(sl, x + Inches(0.08), y + Inches(0.08), w - Inches(0.16), rh,
                     str(val)[:62], 10, color=SLATE7)
                x += w
            y += rh

    # ---- Slide final ----
    sl = _slide(prs)
    _bg(sl, NAVY)
    _box(sl, Inches(0), Inches(3.0), W, Inches(1.2), "Obrigado", 52, bold=True,
         color=WHITE, align=PP_ALIGN.CENTER)
    _box(sl, Inches(0), Inches(4.3), W, Inches(0.5), "vciso.suricatoos.com", 16,
         color=BLUE, align=PP_ALIGN.CENTER)

    out = io.BytesIO()
    prs.save(out)
    out.seek(0)
    return out
