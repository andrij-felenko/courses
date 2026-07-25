# -*- coding: utf-8 -*-
"""Фігури до статті «Робастні оцінки» (book/math/statistics).
Дві фігури, кожна несе вагу:
  1) breakdown.svg  — точка зламу: один викид тягне середнє в нескінченність, медіану — ні
  2) efficiency.svg — ціна стійкості: ефективність оцінки vs точка зламу (mean/trim/median)
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Точка зламу: викид тягне середнє, медіану — ні ────────────────────────
def fig_breakdown():
    W, H = 900, 430
    els = []
    els.append(text(W / 2, 30,
                    "Точка зламу: один викид зсуває середнє необмежено, медіану — ні",
                    size=15, bold=True))
    # числова вісь; дев'ять «чесних» читань купкою ліворуч, десяте — викид ПОЗА шкалою
    ax_y = 210
    x0, x1 = 70, 620
    els.append(line(x0, ax_y, x1 + 10, ax_y, color=INK, sw=1.4))
    els.append(text(x1 + 18, ax_y + 5, "значення", size=12, anchor="start", color=MUTED))
    # дев'ять читань довкола «істини» у лівій третині (шкала показує лише околицю купки)
    cluster = [0.06, 0.08, 0.10, 0.11, 0.12, 0.13, 0.15, 0.17, 0.19]  # медіана купки = 0.12
    outlier_real = 3.5   # величезний викид (10σ і більше) — на шкалу не влазить
    def px_of(fr):
        return x0 + (x1 - x0) * fr
    for fr in cluster:
        els.append(circle(px_of(fr), ax_y, 5, fill=NEG, stroke=NEG))
    els.append(text(px_of(0.125), ax_y + 26, "дев'ять чесних вимірів", size=12, color=NEG, anchor="middle"))
    # викид — за правим краєм: стрілка «за шкалу»
    els.append(arrow(x1 - 30, ax_y, x1 + 8, ax_y, color=POS, sw=2.6))
    els.append(text(x1 - 4, ax_y - 14, "викид ≫", size=12, color=POS, bold=True, anchor="end"))
    els.append(text(x1 - 4, ax_y + 20, "(далеко, поза шкалою)", size=10, color=POS, anchor="end"))
    # медіана десяти — п'яте/шосте за порядком, стоїть у самій купці (викид скраю шеренги)
    med = 0.125
    els.append(line(px_of(med), ax_y - 62, px_of(med), ax_y + 12, color=FIELD, sw=2.6))
    els.append(text(px_of(med), ax_y - 68, "медіана — у купці", size=13, color=FIELD, bold=True, anchor="middle"))
    # середнє — потягнуте викидом далеко праворуч (≈ (сума купки + 3.5)/10 ≈ 0.46)
    mean = (sum(cluster) + outlier_real) / 10.0
    els.append(line(px_of(mean), ax_y - 40, px_of(mean), ax_y + 12, color=POS, sw=2.6, dash="5,4"))
    els.append(text(px_of(mean), ax_y - 46, "середнє — потягнуте", size=13, color=POS, bold=True, anchor="middle"))
    els.append(arrow(px_of(med) + 8, ax_y + 46, px_of(mean) - 6, ax_y + 46, color=POS, sw=2))
    els.append(text((px_of(med) + px_of(mean)) / 2, ax_y + 64,
                    "один викид тягне сюди", size=11, color=POS, anchor="middle"))
    # права колонка — суть точки зламу
    body, bw, bh = textbox(770, 210,
        ["Точка зламу —", "частка «зіпсутих»,", "що зриває оцінку:", "",
         "середнє: 0%",
         "(1 викид → ∞)", "",
         "медіана: 50%",
         "(тримає, поки", "чесних більшість)"],
        size=13, pad=12)
    els.append(body)
    els.append(text(W / 2, 405,
                    "Медіана дивиться на ПОРЯДОК, тож розмір викиду їй байдужий; середнє додає його значення.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "breakdown.svg"), W, H, *els)


# ── 2. Ціна стійкості: ефективність vs точка зламу ───────────────────────────
def fig_efficiency():
    W, H = 900, 440
    els = []
    els.append(text(W / 2, 30,
                    "Ціна стійкості: що стійкіша оцінка, то менше вона «вичавлює» з чистих даних",
                    size=15, bold=True))
    # осі: X — точка зламу (0..50%), Y — ефективність на гаусі (0..100%)
    px, py, pw, ph = 90, 70, 560, 300
    x0, yb = px, py + ph
    els.append(line(x0, yb, x0 + pw, yb, color=INK, sw=1.5))
    els.append(line(x0, py, x0, yb, color=INK, sw=1.5))
    els.append(text(x0 + pw / 2, yb + 40, "точка зламу (стійкість) →", size=13, anchor="middle", color=MUTED))
    # підписи осі X
    for fr, lab in [(0.0, "0%"), (0.25, "25%"), (0.5, "50%")]:
        gx = x0 + pw * (fr / 0.5)
        els.append(line(gx, yb, gx, yb + 5, color=INK, sw=1.2))
        els.append(text(gx, yb + 20, lab, size=11, anchor="middle", color=MUTED))
    # підпис осі Y (вертикально)
    els.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
               'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">ефективність на гаусі</text>'
               % (px - 44, py + ph / 2, FONT, MUTED, px - 44, py + ph / 2))
    for fr, lab in [(0.0, "0%"), (0.5, "50%"), (0.637, "64%"), (0.83, "83%"), (1.0, "100%")]:
        gy = yb - ph * fr
        els.append(line(x0 - 5, gy, x0, gy, color=INK, sw=1.2))
        els.append(text(x0 - 10, gy + 4, lab, size=10, anchor="end", color=MUTED))
    def pt(bp, eff):
        return x0 + pw * (bp / 0.5), yb - ph * eff
    # три оцінки
    mx, my = pt(0.0, 1.0)       # середнє
    tx, ty = pt(0.25, 0.83)     # усічене 20–25% (ефективність ~83%, точка зламу ~25%)
    dx, dy = pt(0.5, 0.637)     # медіана
    # сполучна лінія-компроміс
    els.append(line(mx, my, tx, ty, color=MUTED, sw=1.6, dash="4,4"))
    els.append(line(tx, ty, dx, dy, color=MUTED, sw=1.6, dash="4,4"))
    els.append(circle(mx, my, 7, fill=POS, stroke=POS))
    els.append(circle(tx, ty, 7, fill=FIELD, stroke=FIELD))
    els.append(circle(dx, dy, 7, fill=NEG, stroke=NEG))
    # підписи винесені геть від пунктирної кривої-компромісу:
    # середнє (кут) — над точкою; усічене — над точкою; медіана — праворуч (там вільно)
    els.append(text(mx + 12, my - 25, "середнє", size=13, color=POS, anchor="start", bold=True))
    els.append(text(mx + 12, my - 8, "100% / злам 0%", size=11, color=POS, anchor="start"))
    els.append(text(tx + 10, ty - 25, "усічене 25%", size=13, color=FIELD, anchor="start", bold=True))
    els.append(text(tx + 10, ty - 8, "~83% / злам 25%", size=11, color=FIELD, anchor="start"))
    els.append(text(dx, dy + 18, "медіана", size=13, color=NEG, anchor="middle", bold=True))
    els.append(text(dx, dy + 35, "64% / злам 50%", size=11, color=NEG, anchor="middle"))
    # права колонка — читання графіка
    body, bw, bh = textbox(775, 220,
        ["Читати так:", "",
         "→ праворуч = стійкіше",
         "↓ нижче = дорожче",
         "  (треба більше N", "   на ту саму тишу)", "",
         "Медіана коштує ~36%:",
         "її 100 вимірів дають",
         "тишу ~64 вимірів", "середнього"],
        size=12, pad=12)
    els.append(body)
    render(os.path.join(IMG, "efficiency.svg"), W, H, *els)


if __name__ == "__main__":
    fig_breakdown()
    fig_efficiency()
    print("OK: breakdown, efficiency")
