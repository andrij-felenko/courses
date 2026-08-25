# -*- coding: utf-8 -*-
"""Фігури до теми «Осцилятор Дуффінга».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MAIN = "#2457d6"
ACCENT = "#c0392b"
GREEN = "#27ae60"
BORDER = "#d0d7de"

def head_at(x, y, dx, dy, color=INK, size=8):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.4, by + ny * size * 0.4,
               bx - nx * size * 0.4, by - ny * size * 0.4, color))

def varrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=9):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)

# ── Фігура 1: Потенціальний рельєф та кубічна відновлювальна сила ───────────
def fig_duffing_potential():
    W, H = 840, 420
    f = []

    f.append(text(W / 2, 28, "Потенціальний рельєф V(x) та нелінійні режими осцилятора Дуффінга", size=16, bold=True))

    # Ліва панель: Одноямні потенціали (Жорсткий та М'який)
    x0, y0 = 50, 65
    w_p, h_p = 340, 320
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x0 + w_p / 2, y0 + 24, "Одноямний потенціал (α > 0)", size=13, bold=True))

    cx1, cy1 = x0 + w_p / 2, y0 + 200

    # Осі
    f.append(varrow(x0 + 25, cy1, x0 + w_p - 25, cy1, color=MUTED, sw=1.5))
    f.append(text(x0 + w_p - 20, cy1 + 18, "x", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx1, y0 + h_p - 25, cx1, y0 + 45, color=MUTED, sw=1.5))
    f.append(text(cx1 - 10, y0 + 52, "V(x)", size=12, color=MUTED, anchor="end"))

    # Потенціальні криві
    pts_harm = []
    pts_hard = []
    pts_soft = []

    for i in range(101):
        xn = (i - 50) / 45.0  # від -1.11 до 1.11
        px = cx1 + xn * 130

        # Гармонічний: 0.5 * x^2
        v_h = 0.5 * xn**2
        py_h = cy1 - v_h * 150
        pts_harm.append((px, py_h))

        # Жорсткий: 0.5 * x^2 + 0.25 * x^4
        v_hd = 0.5 * xn**2 + 0.25 * xn**4
        py_hd = cy1 - v_hd * 150
        pts_hard.append((px, py_hd))

        # М'який: 0.5 * x^2 - 0.15 * x^4
        v_sf = 0.5 * xn**2 - 0.15 * xn**4
        py_sf = cy1 - v_sf * 150
        pts_soft.append((px, py_sf))

    # Малювання ліній
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_harm if y0+45 <= p[1] <= y0+h_p-25), MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_hard if y0+45 <= p[1] <= y0+h_p-25), ACCENT))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_soft if y0+45 <= p[1] <= y0+h_p-25), MAIN))

    # Легенда зліва
    f.append(line(x0 + 35, y0 + 290, x0 + 65, y0 + 290, color=ACCENT, sw=2.5))
    f.append(text(x0 + 72, y0 + 294, "Жорсткий (β > 0)", size=11, color=INK, anchor="start"))

    f.append(line(x0 + 175, y0 + 290, x0 + 205, y0 + 290, color=MAIN, sw=2.2))
    f.append(text(x0 + 212, y0 + 294, "М'який (β < 0)", size=11, color=INK, anchor="start"))

    # Права панель: Двоямний потенціал (α < 0, β > 0)
    x1, y1 = 450, 65
    f.append(rect(x1, y1, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x1 + w_p / 2, y1 + 24, "Двоямний потенціал (α < 0, β > 0)", size=13, bold=True))

    cx2, cy2 = x1 + w_p / 2, y1 + 170

    # Осі
    f.append(varrow(x1 + 25, cy2, x1 + w_p - 25, cy2, color=MUTED, sw=1.5))
    f.append(text(x1 + w_p - 20, cy2 + 18, "x", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx2, y1 + h_p - 25, cx2, y1 + 45, color=MUTED, sw=1.5))
    f.append(text(cx2 - 10, y1 + 52, "V(x)", size=12, color=MUTED, anchor="end"))

    # Двоямний потенціал: -0.5 * x^2 + 0.25 * x^4
    pts_dw = []
    for i in range(101):
        xn = (i - 50) / 32.0  # від -1.56 до 1.56
        px = cx2 + xn * 85
        v_dw = -0.5 * xn**2 + 0.25 * xn**4
        py_dw = cy2 - v_dw * 160
        pts_dw.append((px, py_dw))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_dw if y1+45 <= p[1] <= y1+h_p-25), GREEN))

    # Точки мінімумів та сідла
    x_min1 = cx2 - 1.0 * 85
    x_min2 = cx2 + 1.0 * 85
    y_min = cy2 - (-0.25) * 160

    f.append(circle(x_min1, y_min, 4.5, fill=GREEN, stroke=INK, sw=1.2))
    f.append(circle(x_min2, y_min, 4.5, fill=GREEN, stroke=INK, sw=1.2))
    f.append(circle(cx2, cy2, 4.5, fill=ACCENT, stroke=INK, sw=1.2))

    f.append(text(x_min1, y_min + 18, "-x₀", size=11, color=INK, bold=True))
    f.append(text(x_min2, y_min + 18, "+x₀", size=11, color=INK, bold=True))
    f.append(text(cx2 + 18, cy2 - 8, "Сідло", size=11, color=ACCENT, bold=True))

    # Потенціальний бар'єр
    f.append(line(cx2 - 40, cy2, cx2 + 40, cy2, color=MUTED, sw=1.0, dash="3,3"))
    f.append(varrow(cx2 - 50, cy2, cx2 - 50, y_min, color=ACCENT, sw=1.2, head=6))
    f.append(text(cx2 - 62, (cy2 + y_min)/2 + 4, "ΔV", size=11, color=ACCENT, bold=True))

    out_file = os.path.join(IMG, "duffing-potential.svg")
    render(out_file, W, H, *f)
    print("Generated duffing-potential.svg")

# ── Фігура 2: Амплітудно-частотна характеристика та гістерезис ─────────────
def fig_duffing_resonance():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 26, "Амплітудно-частотна характеристика та гістерезисний стрибок", size=16, bold=True))

    x0, y0 = 60, 60
    w_p, h_p = 720, 340
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    cx0, cy0 = x0 + 70, y0 + h_p - 45

    # Осі
    f.append(varrow(cx0, cy0, x0 + w_p - 40, cy0, color=MUTED, sw=1.8))
    f.append(text(x0 + w_p - 35, cy0 + 24, "Частота збудження ω", size=13, bold=True, color=INK, anchor="end"))

    f.append(varrow(cx0, cy0, cx0, y0 + 35, color=MUTED, sw=1.8))
    f.append(text(cx0 - 15, y0 + 40, "Амплітуда А", size=13, bold=True, color=INK, anchor="end"))

    # Скелетна крива (хребтовий графік)
    pts_skel = []
    for i in range(80):
        a = i / 79.0 * 220
        w_sk = cx0 + 200 + 0.0028 * a**2
        py = cy0 - a
        pts_skel.append((w_sk, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_skel), MUTED))
    f.append(text(cx0 + 320, cy0 - 180, "Скелетна крива ω(А)", size=11, color=MUTED, italic=True))

    # Резонансна крива жорсткого осцилятора (зі згином вправо)
    # Нижній підйом: від w0 до w1
    pts_up = []
    for i in range(50):
        t = i / 49.0
        w_px = cx0 + 50 + t * 240
        a_px = 30 + 130 * (t**1.8)
        pts_up.append((w_px, cy0 - a_px))

    # Верхня верхівка, яка нахиляється вправо
    pts_top = []
    for i in range(40):
        t = i / 39.0
        w_px = cx0 + 290 + t * 90
        a_px = 160 + 75 * math.sin(t * math.pi) - t * 30
        pts_top.append((w_px, cy0 - a_px))

    # Нестійка гілка (зворотній згин) - пунктир
    w_jump_up = cx0 + 380
    w_jump_dn = cx0 + 260
    a_top_jump = cy0 - 205
    a_bot_jump = cy0 - 85

    pts_unstable = [
        (w_jump_up, a_top_jump),
        (cx0 + 330, cy0 - 140),
        (w_jump_dn, a_bot_jump)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_unstable), ACCENT))

    # Спадаюча правий край
    pts_right = []
    for i in range(40):
        t = i / 39.0
        w_px = w_jump_up + t * 200
        a_px = 205 * math.exp(-t * 2.2) + 20
        pts_right.append((w_px, cy0 - a_px))

    # Малювання стійких гілок
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_up), MAIN))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_top), MAIN))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_right), MAIN))

    # Стрибки амплітуди (стрілки гістерезису)
    # Стрибок вниз при збільшенні частоти (w_jump_up)
    f.append(varrow(w_jump_up, a_top_jump + 5, w_jump_up, cy0 - 45, color=ACCENT, sw=2.2, head=10))
    f.append(text(w_jump_up + 12, (a_top_jump + cy0 - 45)/2, "Стрибок вниз", size=11, color=ACCENT, bold=True, anchor="start"))

    # Стрибок вгору при зменшенні частоти (w_jump_dn)
    f.append(varrow(w_jump_dn, a_bot_jump - 5, w_jump_dn, cy0 - 175, color=GREEN, sw=2.2, head=10))
    f.append(text(w_jump_dn - 12, (a_bot_jump + cy0 - 175)/2, "Стрибок вгору", size=11, color=GREEN, bold=True, anchor="end"))

    # Позначки частот на осі
    f.append(line(w_jump_dn, cy0 - 4, w_jump_dn, cy0 + 6, color=MUTED, sw=1.5))
    f.append(text(w_jump_dn, cy0 + 20, "ω₁", size=12, bold=True))

    f.append(line(w_jump_up, cy0 - 4, w_jump_up, cy0 + 6, color=MUTED, sw=1.5))
    f.append(text(w_jump_up, cy0 + 20, "ω₂", size=12, bold=True))

    # Область двостабільності
    f.append(rect(w_jump_dn, y0 + 45, w_jump_up - w_jump_dn, cy0 - (y0 + 45), fill="#FFF4E5", stroke="none"))
    f.append(text((w_jump_dn + w_jump_up)/2, y0 + 65, "Зона двостабільності", size=11, color="#D97706", bold=True))

    out_file = os.path.join(IMG, "duffing-resonance.svg")
    render(out_file, W, H, *f)
    print("Generated duffing-resonance.svg")

# ── Фігура 3: Хаотичний фазовий портрет та переріз Пуанкаре ───────────────
def fig_duffing_poincare():
    W, H = 840, 440
    f = []

    f.append(text(W / 2, 26, "Хаотичний фазовий портрет та фрактальний переріз Пуанкаре", size=16, bold=True))

    # Ліва панель: Фазовий портрет міжямного хаосу
    x0, y0 = 50, 60
    w_p, h_p = 340, 340
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x0 + w_p / 2, y0 + 24, "Фазовий простір (x, v): міжямний хаос", size=13, bold=True))

    cx1, cy1 = x0 + w_p / 2, y0 + 190

    # Осі
    f.append(varrow(x0 + 20, cy1, x0 + w_p - 20, cy1, color=MUTED, sw=1.5))
    f.append(text(x0 + w_p - 15, cy1 + 16, "x", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx1, y0 + h_p - 20, cx1, y0 + 45, color=MUTED, sw=1.5))
    f.append(text(cx1 - 10, y0 + 52, "v", size=12, color=MUTED, anchor="end"))

    # Зображення хаотичних витків (дві петлі навколо мінімумів x=-1 та x=+1 з міжямними перескоками)
    pts_left_well = []
    pts_right_well = []
    pts_cross = []

    # Траєкторія лівої ями
    for i in range(120):
        t = i / 119.0 * 4 * math.pi
        r = 50 + 20 * math.sin(t * 1.5)
        px = cx1 - 75 + r * math.cos(t)
        py = cy1 + r * 0.8 * math.sin(t)
        pts_left_well.append((px, py))

    # Траєкторія правої ями
    for i in range(120):
        t = i / 119.0 * 4 * math.pi
        r = 50 + 22 * math.cos(t * 1.3)
        px = cx1 + 75 + r * math.cos(t)
        py = cy1 + r * 0.8 * math.sin(t)
        pts_right_well.append((px, py))

    # Перехідні витки через сідло x=0
    for i in range(80):
        t = (i / 79.0 - 0.5) * 2.2
        px = cx1 + t * 90
        py = cy1 + 70 * math.sin(t * math.pi) * (1 - 0.3 * t**2)
        pts_cross.append((px, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" opacity="0.75"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_left_well), MAIN))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" opacity="0.75"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_right_well), MAIN))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_cross), ACCENT))

    # Центри та сідло
    f.append(circle(cx1 - 75, cy1, 4, fill=MAIN, stroke=INK, sw=1.0))
    f.append(circle(cx1 + 75, cy1, 4, fill=MAIN, stroke=INK, sw=1.0))
    f.append(circle(cx1, cy1, 4, fill=ACCENT, stroke=INK, sw=1.0))

    # Права панель: Переріз Пуанкаре (дивний атрактор)
    x1, y1 = 450, 60
    f.append(rect(x1, y1, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x1 + w_p / 2, y1 + 24, "Переріз Пуанкаре: Дивний атрактор Уеди", size=13, bold=True))

    cx2, cy2 = x1 + w_p / 2, y1 + 190

    # Осі
    f.append(varrow(x1 + 20, cy2, x1 + w_p - 20, cy2, color=MUTED, sw=1.5))
    f.append(text(x1 + w_p - 15, cy2 + 16, "x", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx2, y1 + h_p - 20, cx2, y1 + 45, color=MUTED, sw=1.5))
    f.append(text(cx2 - 10, y1 + 52, "v", size=12, color=MUTED, anchor="end"))

    # Генерація точок дивного атрактора у вигляді закрученого канторового віяла
    for i in range(350):
        u = (i / 350.0)
        angle = u * 2.5 * math.pi - 1.2
        r = 40 + 70 * u + 12 * math.sin(u * 20)
        for branch in [-8, -3, 0, 3, 8]:
            px = cx2 + r * math.cos(angle) + branch * math.sin(angle * 2)
            py = cy2 + r * 0.75 * math.sin(angle) + branch * math.cos(angle * 2)
            if x1 + 25 <= px <= x1 + w_p - 25 and y1 + 45 <= py <= y1 + h_p - 25:
                f.append(circle(px, py, 1.2, fill=ACCENT, stroke="none"))

    f.append(text(x1 + w_p / 2, y1 + h_p - 30, "Стробоскопічний зріз: t = 2πk / ω", size=11, color=MUTED, italic=True))

    out_file = os.path.join(IMG, "duffing-poincare.svg")
    render(out_file, W, H, *f)
    print("Generated duffing-poincare.svg")

if __name__ == "__main__":
    fig_duffing_potential()
    fig_duffing_resonance()
    fig_duffing_poincare()
