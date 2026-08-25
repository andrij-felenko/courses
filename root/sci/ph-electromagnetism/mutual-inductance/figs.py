# -*- coding: utf-8 -*-
"""Фігура вставки «Коефіцієнт трансформації і відбитий опір».
Імпортує спільний svgkit зі scripts/ (НЕ переписувати його функції).
Запуск:  python figs.py    (з теки теми)  →  пише у ./img/reflected.svg

reflected.svg — резистор R на вторинці очима джерела виглядає як R/n².
Ідея, яку важко передати самими словами: те саме навантаження «важчає» в n² разів.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (text, mtext, rect, line, render, INK, MUTED, POS, NEG,
                    FIELD, FILL)  # noqa: E402

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COILCOL = "#b5732e"   # мідь обмоток


def coil(cx, ytop, ybot, n, r, frags):
    """Намалювати обмотку як стос напівкіл (n витків) уздовж вертикалі."""
    step = (ybot - ytop) / n
    y = ytop
    for _ in range(n):
        frags.append('<path d="M %.1f,%.1f A %.1f %.1f 0 0 1 %.1f,%.1f" '
                     'fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (cx, y, r, step / 2, cx, y + step, COILCOL))
        y += step


def reflected():
    W, H = 820, 480
    frags = []

    # ── осердя (дві жирні вертикалі) ─────────────────────────────────
    cyt, cyb = 150.0, 340.0
    for x in (424.0, 436.0):
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                     'stroke="%s" stroke-width="3" stroke-linecap="round"/>'
                     % (x, cyt, x, cyb, INK))

    # ── обмотки: первинна (мало витків) і вторинна (багато) ──────────
    coil(408.0, 165.0, 325.0, 4, 22.0, frags)     # N₁
    coil(452.0, 165.0, 325.0, 8, 13.0, frags)     # N₂ = n·N₁ (тут n=2 для наочності)
    frags.append(text(388.0, 250.0, "N₁", size=13, color=INK, anchor="end", bold=True))
    frags.append(text(472.0, 250.0, "N₂ = n·N₁", size=13, color=INK, anchor="start", bold=True))

    # ── джерело (коло) зліва ─────────────────────────────────────────
    sx, sy = 150.0, 250.0
    frags.append('<circle cx="%.1f" cy="%.1f" r="24" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (sx, sy, FILL, INK))
    frags.append('<path d="M %.1f %.1f q 7 -14 14 0 q 7 14 14 0" fill="none" '
                 'stroke="%s" stroke-width="1.8"/>' % (sx - 14, sy, INK))  # ~ синусоїда

    # первинний контур (синій бік)
    frags.append(line(sx, sy - 24, sx, cyt + 15, NEG, 2.2))
    frags.append(line(sx, cyt + 15, 408.0, cyt + 15, NEG, 2.2))
    frags.append(line(sx, sy + 24, sx, cyb - 15, NEG, 2.2))
    frags.append(line(sx, cyb - 15, 408.0, cyb - 15, NEG, 2.2))
    frags.append(text(255.0, 152.0, "V₁, I₁", size=13, color=NEG, anchor="middle", bold=True))

    # ── навантаження R справа (червоний бік) ─────────────────────────
    rx = 700.0
    frags.append(line(452.0, cyt + 15, rx, cyt + 15, POS, 2.2))
    frags.append(line(452.0, cyb - 15, rx, cyb - 15, POS, 2.2))
    frags.append(rect(rx - 14, 215.0, 28, 70, fill=FILL, stroke=INK, sw=2, rx=0))
    frags.append(text(rx, 256.0, "R", size=15, color=INK, anchor="middle", bold=True))
    frags.append(line(rx, cyt + 15, rx, 215.0, POS, 2.2))
    frags.append(line(rx, 285.0, rx, cyb - 15, POS, 2.2))
    frags.append(text(580.0, 152.0, "V₂ = n·V₁,  I₂ = I₁/n", size=13,
                      color=POS, anchor="middle", bold=True))

    # ── висновок: очима джерела все це — один резистор R/n² ───────────
    frags.append('<rect x="96" y="372" width="320" height="86" rx="8" '
                 'fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % MUTED)
    frags.append('<line x1="96" y1="372" x2="416" y2="372" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="6,5" stroke-linecap="round"/>' % MUTED)
    frags.append(text(256.0, 396.0, "очима джерела все це —", size=12,
                      color=MUTED, anchor="middle", bold=True))
    frags.append(text(256.0, 421.0, "один резистор  R/n²", size=15,
                      color=FIELD, anchor="middle", bold=True))
    frags.append(text(256.0, 445.0, "(V₁/I₁ = (V₂/n)/(n·I₂) = R/n²)", size=11.5,
                      color=INK, anchor="middle"))

    # пояснення праворуч
    frags.append(mtext(560.0, 402.0,
                       ["n = N₂/N₁ — коефіцієнт трансформації;",
                        "знижувальний (n < 1) робить навантаження",
                        "«важчим», підвищувальний — «легшим»"],
                       size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, "reflected.svg"), W, H, *frags,
           title="Відбитий опір: що «бачить» джерело крізь трансформатор")


if __name__ == "__main__":
    reflected()
    print("written: img/reflected.svg")
