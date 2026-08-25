# -*- coding: utf-8 -*-
"""Фігури до теми «Fuel gauge» (паливомір без шунта).
Дві фігури:
  block-diagram.svg — чип сидить лише на напрузі комірки, без шунта в силовій лінії;
                      назовні I²C (SOC/VCELL) і ALRT-переривання.
  ocv-curve.svg     — форма кривої OCV(SoC): похила хімія читається всюди,
                      плоске плато (LFP) «осліплює» напруговий метод.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def gnd(cx, y, label="GND"):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8)]
    out.append(line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.3))
    out.append(line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0))
    out.append(line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8))
    if label:
        out.append(text(cx, y + 33, label, size=11, color=INK, bold=True))
    return "".join(out)


def dot(cx, cy):
    return '<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (cx, cy, INK)


# ── Фігура 1: блок-схема — напруга замість шунта ─────────────────────────────
def fig_block_diagram():
    W, H = 880, 430
    f = [text(W / 2, 30, "Паливомір сидить на напрузі комірки — без шунта в силовій лінії",
              size=16, bold=True)]

    railY = 96                      # силова лінія комірка → система
    cellX = 84
    sysX = 800

    # комірка (зелена рамка) ліворуч
    cb, cw, ch = rect(cellX - 42, railY - 30, 84, 60, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8), 84, 60
    f.append(cb)
    f.append(text(cellX, railY - 8, "комірка", size=11, color="#1f6e33", bold=True))
    f.append(text(cellX, railY + 12, "Li 1S", size=10, color=INK))

    # силова лінія до системи — БЕЗ шунта
    f.append(line(cellX + 42, railY, sysX - 30, railY, color=POS, sw=2.6))
    f.append(text(sysX - 24, railY + 4, "у систему", size=11, color=POS, anchor="start", bold=True))
    dot_x = (cellX + 42 + sysX) / 2
    # маркер «тут НЕ потрібен шунт» на силовій лінії
    mx = 360
    f.append(line(mx - 22, railY - 16, mx + 22, railY + 16, color=MUTED, sw=1.6, dash="4,3"))
    f.append(line(mx + 22, railY - 16, mx - 22, railY + 16, color=MUTED, sw=1.6, dash="4,3"))
    f.append(text(mx, railY - 26, "немає шунта", size=11, color=POS, bold=True))
    f.append(text(mx, railY + 36, "(нема падіння й нагріву)", size=10, color=MUTED))

    # паливомір (синя рамка) у центрі-низу
    gx, gy, gw, gh = 250, 220, 220, 130
    f.append(rect(gx, gy, gw, gh, fill="#eef3fb", stroke="#1f47b5", sw=2, rx=12))
    f.append(text(gx + gw / 2, gy + 26, "паливомір", size=13, color="#1f47b5", bold=True))
    f.append(text(gx + gw / 2, gy + 50, "модель комірки", size=10, color=INK))
    f.append(text(gx + gw / 2, gy + 70, "міряє лише напругу", size=10, color=INK))
    f.append(text(gx + gw / 2, gy + 92, "→ рахує SOC, %", size=11, color="#1f6e33", bold=True))
    f.append(text(gx + gw / 2, gy + 112, "(без інтеграла струму)", size=10, color=MUTED))

    # відвід напруги комірки в паливомір (вимір + живлення)
    tapX = cellX
    f.append(line(tapX, railY + 30, tapX, gy + 60, color=FIELD, sw=1.6, dash="4,3"))
    f.append(line(tapX, gy + 60, gx, gy + 60, color=FIELD, sw=1.6, dash="4,3"))
    f.append(dot(tapX, railY))
    f.append(text((tapX + gx) / 2, gy + 53, "напруга комірки", size=9.5, color="#1f6e33"))
    f.append(text((tapX + gx) / 2, gy + 73, "(вимір + живлення)", size=9, color=MUTED))

    # МК праворуч
    mcuX, mcuY, mcuW, mcuH = 640, 220, 170, 130
    f.append(rect(mcuX, mcuY, mcuW, mcuH, fill="#ffffff", stroke=INK, sw=2, rx=12))
    f.append(text(mcuX + mcuW / 2, mcuY + 28, "МК", size=13, color=INK, bold=True))

    # I²C: паливомір ↔ МК
    busY = mcuY + 50
    f.append(line(gx + gw, busY, mcuX, busY, color="#1f47b5", sw=2))
    f.append(text((gx + gw + mcuX) / 2, busY - 8, "I²C (SDA/SCL)", size=10, color="#1f47b5", bold=True))
    f.append(text((gx + gw + mcuX) / 2, busY + 12, "читає SOC, VCELL", size=9.5, color=INK))

    # ALRT: переривання
    altY = mcuY + 96
    f.append(line(gx + gw, altY, mcuX, altY, color="#b5732e", sw=2))
    f.append(text((gx + gw + mcuX) / 2, altY + 16, "ALRT → переривання", size=9.5, color="#b5732e", bold=True))
    f.append(text((gx + gw + mcuX) / 2, altY + 33, "(будить МК при низькому заряді)", size=9, color=MUTED))

    f.append(text(W / 2, 414,
                  "Нема резистора в силовому колі — нема втрат на ньому; SoC дає модель напруги, а не інтеграл струму.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "block-diagram.svg"), W, H, *f)


# ── Фігура 2: форма кривої OCV(SoC) ─────────────────────────────────────────
def fig_ocv_curve():
    W, H = 860, 430
    f = [text(W / 2, 30, "Форма кривої OCV(SoC) вирішує точність напругового паливоміра",
              size=16, bold=True)]

    ox, oy = 90, 350            # початок осей
    rx, ty = 690, 80           # правий/верхній край поля
    f.append(line(ox, oy, rx, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, ty, color=INK, sw=1.6))
    f.append(text((ox + rx) / 2, oy + 38, "SoC, %", size=12, color=INK, bold=True))
    f.append(text(ox - 56, (oy + ty) / 2, "OCV, В", size=12, color=INK, bold=True))

    # підписи осі X
    for frac, lab in [(0.0, "0"), (0.5, "50"), (1.0, "100")]:
        x = ox + frac * (rx - ox)
        f.append(line(x, oy, x, oy + 6, color=INK, sw=1.4))
        f.append(text(x, oy + 22, lab, size=10, color=INK))
    # підписи осі Y (3.3 .. 4.2)
    for v, lab in [(3.3, "3.3"), (3.75, "3.75"), (4.2, "4.2")]:
        yy = oy - (v - 3.3) / 0.9 * (oy - ty)
        f.append(line(ox - 6, yy, ox, yy, color=INK, sw=1.4))
        f.append(text(ox - 12, yy + 4, lab, size=10, color=INK, anchor="end"))

    def Y(v):       # напруга → піксель
        return oy - (v - 3.3) / 0.9 * (oy - ty)

    def X(soc):     # відсоток → піксель
        return ox + soc / 100.0 * (rx - ox)

    # похила крива (NMC): помітний нахил усюди, крутіша на краях
    pts = []
    for i in range(0, 101):
        s = i
        # гладка монотонна форма від 3.30 до 4.20 з S-подібним вигином
        v = 3.30 + 0.9 * (0.5 - 0.5 * math.cos(math.pi * (s / 100.0)))
        pts.append("%.1f,%.1f" % (X(s), Y(v)))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" L ".join(pts), "#1f47b5"))
    f.append(text(X(78) + 6, Y(3.30 + 0.9 * (0.5 - 0.5 * math.cos(math.pi * 0.78))) - 10,
                  "похила хімія (NMC)", size=11, color="#1f47b5", bold=True, anchor="start"))

    # крива з плато (LFP): майже плоска в середині (тримаємо в межах поля, ≥3.30)
    pts2 = []
    for i in range(0, 101):
        s = i / 100.0
        if s < 0.12:
            v = 3.31 + (3.40 - 3.31) * (s / 0.12)
        elif s < 0.88:
            v = 3.40 + (3.44 - 3.40) * ((s - 0.12) / 0.76)
        else:
            v = 3.44 + (3.62 - 3.44) * ((s - 0.88) / 0.12)
        pts2.append("%.1f,%.1f" % (X(i), Y(v)))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,4"/>' % (
        " L ".join(pts2), FIELD))
    f.append(text(X(45), Y(3.42) - 12, "плоске плато (LFP)", size=11, color="#1f6e33", bold=True))

    # та сама вилка напруги ±мВ на обох кривих: на плато вона лягає в широкий
    # діапазон SoC, на похилій — у вузький. Однакова за висотою вертикальна риска.
    half = 0.013      # ±13 мВ — однаково на обох
    # на плато (LFP) ~50% SoC
    f.append(line(X(50), Y(3.42 - half), X(50), Y(3.42 + half), color=POS, sw=3))
    f.append(text(X(50), Y(3.42 + half) - 8, "±мВ", size=10, color=POS, bold=True))
    # на похилій (NMC) ~25% SoC, де крива добре нахилена
    vN = 3.30 + 0.9 * (0.5 - 0.5 * math.cos(math.pi * 0.25))
    f.append(line(X(25), Y(vN - half), X(25), Y(vN + half), color=POS, sw=3))
    f.append(text(X(25), Y(vN - half) + 22, "ті самі ±мВ", size=10, color=POS, bold=True, anchor="middle"))

    # бічна легенда-висновок
    lx, ly, lw, lh = 700, 90, 150, 150
    f.append(rect(lx, ly, lw, lh, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=8))
    f.append(fitbox(lx + 10, ly + 12, lw - 20, 56,
                    "похила: малий зсув\nнапруги → малий\nзсув SoC (точно)",
                    size=10, fill="#eef3fb", stroke="#1f47b5", color=INK))
    f.append(fitbox(lx + 10, ly + 78, lw - 20, 60,
                    "плато: ті самі мВ\n→ великий зсув SoC\n(метод сліпне)",
                    size=10, fill="#eef6ef", stroke=FIELD, color=INK))

    f.append(text(W / 2, 414,
                  "На плато ≤2 мВ/% напруга вже не відрізняє 45 % від 55 %; на похилій хімії ті самі мілівольти коштують частку відсотка.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "ocv-curve.svg"), W, H, *f)


if __name__ == "__main__":
    fig_block_diagram()
    fig_ocv_curve()
    print("OK: block-diagram, ocv-curve -> img/")
