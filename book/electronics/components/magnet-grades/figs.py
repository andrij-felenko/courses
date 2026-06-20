# -*- coding: utf-8 -*-
"""Фігури теми «Класи магнітів». Імпортує спільний svgkit зі scripts/.
Запуск:  python figs.py    (з теки теми)  →  пише у ./img/

Дві фігури:
  energy-bars.svg — стовпчики (BH)max: ферит проти неодимового ряду N35…N52.
  temp-limits.svg — температурні стелі (робоча межа й точка Кюрі) для фериту й неодиму.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (text, rect, line, render, INK, MUTED, POS, FIELD)  # noqa: E402

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#c9952b"   # «слабшає» — проміжна зона
GREY = "#8a8a8a"


# ── Фігура 1: енергетичний добуток (BH)max ──────────────────────────────────
def energy_bars():
    W, H = 820, 470
    x0, ybase, ytop = 90.0, 392.0, 90.0      # осі
    scale = (ybase - ytop) / 400.0            # 0..400 кДж/м³ по висоті
    frags = []
    # осі
    frags.append(line(x0, ytop, x0, ybase, color=INK, sw=2))
    frags.append(line(x0, ybase, 780, ybase, color=INK, sw=2))
    # сітка 100/200/300/400
    for v in (100, 200, 300, 400):
        y = ybase - v * scale
        frags.append(line(86, y, 770, y, color="#e4e4e4", sw=1))
        frags.append(text(80, y + 4, str(v), size=11, color=MUTED, anchor="end"))
    frags.append('<text transform="rotate(-90 34 230)" x="34.0" y="230.0" '
                 'font-family="%s" font-size="12" fill="%s" text-anchor="middle" '
                 'font-weight="700">(BH)max, кДж/м³</text>' % (
                     "'Segoe UI', 'DejaVu Sans', Arial, sans-serif", MUTED))
    # стовпчики: (підпис, значення, колір)
    bars = [("Ферит", 28, GREY), ("N35", 279, FIELD), ("N42", 334, FIELD), ("N52", 398, POS)]
    bw, gap = 96.0, 56.0
    bx = 136.0
    for label, val, col in bars:
        bh = val * scale
        by = ybase - bh
        frags.append(rect(bx, by, bw, bh, fill=col, stroke=INK, sw=1.8, rx=4))
        frags.append(text(bx + bw / 2, by - 10, "≈ %d" % val, size=13, color=INK, bold=True))
        frags.append(text(bx + bw / 2, 414, label, size=13, color=INK, bold=True))
        bx += bw + gap
    frags.append(text(136 + bw / 2, 430, "(керамічний)", size=12, color=INK))
    # підсумкова смужка
    frags.append(rect(90, 432, 690, 30, fill="#f1f6ef", stroke=FIELD, sw=1.4, rx=8))
    frags.append(text(435, 452,
                      "Число в марці Nxx — це і є приблизно (BH)max у МГс·Е: "
                      "N52 ≈ 52 МГс·Е ≈ 398 кДж/м³.", size=12, color=INK, bold=True))
    render(os.path.join(IMG, "energy-bars.svg"), W, H, *frags,
           title="Скільки поля «запасено»: енергетичний добуток (BH)max")


# ── Фігура 2: температурні стелі ─────────────────────────────────────────────
def temp_limits():
    W, H = 820, 440
    xL, xR = 120.0, 760.0
    tmax = 600.0
    sx = (xR - xL) / tmax

    def X(t):
        return xL + t * sx

    frags = []
    # вісь температури
    frags.append(line(xL, 390, xR, 390, color=INK, sw=2))
    for t in (0, 80, 150, 200, 310, 450, 600):
        frags.append(line(X(t), 386, X(t), 394, color=INK, sw=1.6))
        frags.append(text(X(t), 410, str(t), size=11, color=MUTED))
    frags.append(text(440, 430, "температура, °C", size=12, color=MUTED, bold=True))
    # легенда
    leg = [("робоча зона", "#dff0df", FIELD, 120),
           ("слабшає (втрата сили)", "#fdeccd", GOLD, 270),
           ("поля немає (за Кюрі)", "#ececec", GREY, 480)]
    for lab, fill, stroke, lx in leg:
        frags.append(rect(lx, 70, 18, 14, fill=fill, stroke=stroke, sw=1.2, rx=3))
        frags.append(text(lx + 24, 82, lab, size=11, color=INK, anchor="start"))

    # рядок матеріалу: назва, робоча межа, точка Кюрі, y
    def row(name, work, curie, y):
        frags.append(text(108, y + 18, name, size=12, color=INK, anchor="end", bold=True))
        frags.append(rect(xL, y, X(work) - xL, 26, fill="#dff0df", stroke=FIELD, sw=1.4, rx=4))
        frags.append(rect(X(work), y, X(curie) - X(work), 26, fill="#fdeccd", stroke=GOLD, sw=1.4, rx=0))
        frags.append(rect(X(curie), y, xR - X(curie), 26, fill="#ececec", stroke=GREY, sw=1.2, rx=0))
        frags.append(line(X(work), y - 8, X(work), y + 34, color=GOLD, sw=2, dash="4 3"))
        frags.append(text(X(work), y - 12, "≈%d°C" % work, size=11, color=GOLD, bold=True))
        frags.append(line(X(curie), y - 8, X(curie), y + 34, color=POS, sw=2))
        frags.append(text(X(curie), y + 48, "Кюрі ≈%d°C" % curie, size=11, color=POS, bold=True))

    row("Ферит", 250, 450, 137)
    row("Неодим N", 80, 310, 237)
    row("Неодим SH", 150, 340, 327)
    render(os.path.join(IMG, "temp-limits.svg"), W, H, *frags,
           title="Температурна стеля: робоча межа і точка Кюрі")


if __name__ == "__main__":
    energy_bars()
    temp_limits()
    print("OK: energy-bars.svg, temp-limits.svg")
