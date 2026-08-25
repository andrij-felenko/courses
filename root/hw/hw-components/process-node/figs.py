# -*- coding: utf-8 -*-
"""Фігури теми «Техпроцес» (book/electronics/microelectronics/process-node).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Назва вузла vs реальні розміри ────────────────────────────────────────
def fig_node_vs_real():
    W, H = 720, 300
    out = []
    # ліворуч — велика «мітка»
    box, bw, bh = textbox(175, 130, "«5 нм»", size=30, bold=True, pad=18,
                          fill="#fdecea", stroke=POS, sw=2.5, color=POS, min_w=190)
    out.append(box)
    out.append(text(175, 172, "назва техпроцесу", size=13, color=INK))
    # стрілка «насправді»
    out.append(arrow(290, 110, 372, 110))
    out.append(text(331, 98, "насправді на чипі", size=11.5, color=MUTED))
    # праворуч — таблиця реальних розмірів
    rows = [("Крок між затворами (gate pitch)", "≈ 50 нм", False),
            ("Крок металевих доріжок (metal pitch)", "≈ 30 нм", False),
            ("Фізична довжина затвора", "≈ 16–20 нм", False),
            ("«5 нм» як розмір чогось", "— нічого", True)]
    rx0, ry0, rw, rh, gap = 392, 72, 300, 38, 8
    for i, (lab, val, hot) in enumerate(rows):
        y = ry0 + i * (rh + gap)
        fill = "#fbeaea" if hot else FILL
        stroke = POS if hot else LINE
        out.append(rect(rx0, y, rw, rh, fill=fill, stroke=stroke,
                        sw=1.8 if hot else 1.4))
        out.append(text(rx0 + 12, y + 24, lab, size=12, color=INK,
                        anchor="start", bold=hot))
        out.append(text(rx0 + rw - 12, y + 24, val, size=12.5,
                        color=POS if hot else INK, anchor="end", bold=True))
    return render(os.path.join(IMG, "node-vs-real.svg"), W, H, *out,
                  title="«5 нм» — це назва покоління, а не фізичний розмір")


# ── 2. Щільність транзисторів по вузлах ──────────────────────────────────────
def fig_density():
    W, H = 720, 320
    out = []
    ax_x, ax_y0, ax_top = 78, 285, 70
    out.append(line(ax_x, ax_y0, 690, ax_y0, color=INK, sw=1.5))   # вісь X
    out.append(line(ax_x, ax_y0, ax_x, ax_top, color=INK, sw=1.5)) # вісь Y
    out.append(text(ax_x - 4, ax_y0 - 205, "млн транз. / мм²", size=11.5,
                    color=MUTED, anchor="start"))
    bars = [("90 нм", 1.5), ("45 нм", 3.3), ("28 нм", 12), ("14 нм", 38),
            ("7 нм", 100), ("5 нм", 170), ("3 нм", 290)]
    vmax = 300.0
    plot_h = ax_y0 - ax_top
    bw, slot = 56, 86
    for i, (lab, val) in enumerate(bars):
        cx = 118 + i * slot
        h = max(1.5, val / vmax * plot_h)
        y = ax_y0 - h
        out.append(rect(cx - bw / 2, y, bw, h, fill=FIELD, stroke="#176f3a",
                        sw=1.4, rx=0))
        out.append(text(cx, y - 6, ("%g" % val), size=11.5, color="#176f3a",
                        bold=True))
        out.append(text(cx, ax_y0 + 18, lab, size=12, color=INK))
    return render(os.path.join(IMG, "density.svg"), W, H, *out,
                  title="Що справді росте від вузла до вузла — щільність")


# ── 3. Планарний → FinFET → GAA ──────────────────────────────────────────────
def fig_finfet():
    W, H = 720, 280
    out = []
    # — Планарний —
    cxA = 145
    out.append(text(cxA, 64, "Планарний", size=14, color=INK, bold=True))
    out.append(text(cxA, 82, "затвор лише згори", size=11.5, color=MUTED))
    out.append(rect(cxA - 70, 168, 140, 22, fill="#f3c0bb", stroke=POS, sw=1.4, rx=0))  # канал
    out.append(rect(cxA - 40, 146, 80, 22, fill="#9bb0d8", stroke=NEG, sw=1.6, rx=0))   # затвор
    out.append(text(cxA, 161, "затвор", size=11, color=INK, bold=True))
    out.append(text(cxA, 214, "контакт лише з 1 боку", size=11, color=MUTED))
    # — FinFET —
    cxB = 370
    out.append(text(cxB, 64, "FinFET", size=14, color=INK, bold=True))
    out.append(text(cxB, 82, "затвор із трьох боків", size=11.5, color=MUTED))
    out.append(rect(cxB - 12, 128, 24, 72, fill="#f3c0bb", stroke=POS, sw=1.4, rx=0))    # ребро-канал
    out.append('<rect x="%.1f" y="%.1f" width="60" height="50" rx="0" fill="none" stroke="%s" stroke-width="3"/>' % (cxB - 30, 138, NEG))
    out.append(line(cxB - 30, 188, cxB + 30, 188, color=BG, sw=4))
    out.append(text(cxB, 118, "ребро (fin)", size=11, color=POS, bold=True))
    out.append(text(cxB, 214, "затвор огортає 3 боки", size=11, color=MUTED))
    # — GAA —
    cxC = 595
    out.append(text(cxC, 64, "GAA / nanosheet", size=14, color=INK, bold=True))
    out.append(text(cxC, 82, "затвор з усіх боків", size=11.5, color=MUTED))
    for cy in (138, 162, 186):
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="38" ry="13" fill="none" stroke="%s" stroke-width="2"/>' % (cxC, cy, NEG))
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="30" ry="8" fill="#f3c0bb" stroke="%s" stroke-width="1.4"/>' % (cxC, cy, POS))
    out.append(text(cxC, 214, "затвор оточує канал увесь", size=11, color=MUTED))
    return render(os.path.join(IMG, "finfet-gaa.svg"), W, H, *out,
                  title="Прогрес — не лише дрібніше, а й інша форма затвора")


if __name__ == "__main__":
    fig_node_vs_real()
    fig_density()
    fig_finfet()
    print("ok: node-vs-real.svg, density.svg, finfet-gaa.svg")
