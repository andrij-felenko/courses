# -*- coding: utf-8 -*-
"""Фігури теми «Феритова клема» (book/electronics/pcb/ferrite-clamp).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG теми у ./img/
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── допоміжне: феритове кільце (тор у розрізі) ───────────────────────────────
def ring(cx, cy, rx, ry, label=None):
    """Кільце як два овали (зовнішній/внутрішній), сіра «феритова» заливка."""
    s = ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#d9dce0" '
         'stroke="%s" stroke-width="2"/>' % (cx, cy, rx, ry, INK))
    s += ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
          'stroke="%s" stroke-width="1.5"/>' % (cx, cy, rx * 0.46, ry * 0.46, BG, INK))
    if label:
        s += text(cx, cy + ry + 18, label, size=12, color=MUTED)
    return s


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — протифазне проти синфазного: поля скасовуються / додаються
# ════════════════════════════════════════════════════════════════════════════
def fig_cm_dm():
    W, H = 720, 360
    el = []

    # ── ліва панель: протифазне (струм «туди-назад») ──
    cx = 185
    el.append(text(cx, 40, "Протифазне (сигнал «туди-назад»)", size=14, bold=True))
    ry, rx = 78, 40
    cy = 175
    el.append(ring(cx, cy, rx, ry))
    # дві жили крізь кільце
    el.append(line(cx - 14, 95, cx - 14, 255, color=INK, sw=3))
    el.append(line(cx + 14, 95, cx + 14, 255, color=INK, sw=3))
    # стрілки струму: ліва вниз (туди), права вгору (назад)
    el.append(arrow(cx - 14, 110, cx - 14, 150, color=POS))
    el.append(arrow(cx + 14, 240, cx + 14, 200, color=NEG))
    el.append(text(cx - 36, 105, "I", size=13, color=POS, bold=True, italic=True))
    el.append(text(cx + 36, 105, "I", size=13, color=NEG, bold=True, italic=True))
    # підсумок під панеллю
    b, w, h = textbox(cx, 305, "Потоки скасовуються\nферит невидимий → сигнал проходить",
                      size=12, fill="#eafaf0", stroke=FIELD, color="#1e7a46")
    el.append(b)

    # ── розділювач ──
    el.append(line(360, 70, 360, 330, color=MUTED, sw=1, dash="5,5"))

    # ── права панель: синфазне (струм в один бік) ──
    cx = 535
    el.append(text(cx, 40, "Синфазне (завада, спільна всім жилам)", size=14, bold=True))
    cy = 175
    el.append(ring(cx, cy, rx, ry))
    el.append(line(cx - 14, 95, cx - 14, 255, color=INK, sw=3))
    el.append(line(cx + 14, 95, cx + 14, 255, color=INK, sw=3))
    # обидві стрілки в один бік (вниз)
    el.append(arrow(cx - 14, 110, cx - 14, 150, color=POS))
    el.append(arrow(cx + 14, 110, cx + 14, 150, color=POS))
    el.append(text(cx - 36, 105, "I", size=13, color=POS, bold=True, italic=True))
    el.append(text(cx + 36, 105, "I", size=13, color=POS, bold=True, italic=True))
    b, w, h = textbox(cx, 305, "Потоки додаються\nферит вмикається → завада гасне теплом",
                      size=12, fill="#fdecea", stroke=POS, color="#a3271b")
    el.append(b)

    render(out("cm-dm.svg"), W, H, *el)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — витки крізь кільце: опір росте як N²
# ════════════════════════════════════════════════════════════════════════════
def fig_turns():
    W, H = 720, 330
    el = []
    el.append(text(W / 2, 34, "Більше витків крізь те саме кільце — опір як N²",
                   size=15, bold=True))

    panels = [(150, 1, "1 проходження", "≈ 100 Ом", "#eef2f7", LINE),
              (370, 2, "2 витки", "≈ 400 Ом", "#fff6e6", "#b8860b"),
              (590, 3, "3 витки", "≈ 900 Ом", "#fdecea", POS)]
    cy = 165
    rx, ry = 34, 64
    for cx, n, cap, ohm, fill, stroke in panels:
        el.append(ring(cx, cy, rx, ry))
        # n проходжень кабелю крізь кільце
        spread = 9
        x0 = cx - (n - 1) * spread / 2.0
        for k in range(n):
            x = x0 + k * spread
            el.append(line(x, cy - ry - 22, x, cy + ry + 22, color=INK, sw=2.4))
        el.append(text(cx, 70, cap, size=13, bold=True))
        b, w, h = fitbox(cx - 55, 262, 110, 34, ohm, size=14, bold=True,
                         fill=fill, stroke=stroke, color=INK), 110, 34
        el.append(b)
        if n > 1:
            el.append(text(cx, 314, "%d² = %d×" % (n, n * n), size=12, color=MUTED))

    render(out("turns.svg"), W, H, *el)


if __name__ == "__main__":
    fig_cm_dm()
    fig_turns()
    print("figs: cm-dm.svg, turns.svg")
