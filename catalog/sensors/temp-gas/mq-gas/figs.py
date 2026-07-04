# -*- coding: utf-8 -*-
"""Фігури до статті MQ — давач газу (catalog/sensors/temp-gas/mq-gas).
Вивід — ./img/*.svg. Запуск: python figs.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WARM = "#d6a419"   # «гаряче» — нагрівач


# ── 1. Принцип: SnO2 + нагрівач → опір міняється → дільник → напруга ──────────
def fig_principle():
    W, H = 820, 470
    f = []
    f.append(text(410, 30, "Що всередині: нагріта кулька SnO₂ міняє опір від газу", size=16, bold=True))

    # Керамічний корпус із чутливим елементом (ліворуч)
    f.append(rect(50, 70, 330, 250, fill="#f6f2ea", stroke=WARM, sw=1.6, rx=12))
    f.append(text(215, 92, "Чутливий елемент", size=13, bold=True, color="#8a6d10"))

    # Кулька SnO2
    f.append(circle(150, 190, 46, fill="#fbe9c6", stroke=WARM, sw=2))
    f.append(text(150, 186, "SnO₂", size=17, bold=True, color="#8a6d10"))
    f.append(text(150, 206, "олова діоксид", size=10, color=MUTED))

    # Спіраль нагрівача всередині
    f.append(text(150, 250, "нагрівач усередині", size=10.5, color=POS))
    f.append(text(150, 265, "~200–400 °C", size=11, color=POS, bold=True))

    # Дві ситуації: чисте повітря / є газ
    b1, w1, h1 = textbox(300, 150, "чисте повітря:\nкисень тримає\nелектрони →\nопір ВЕЛИКИЙ", size=10.5,
                         pad=8, fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(b1)
    b2, w2, h2 = textbox(300, 250, "є горючий газ:\nреагує з киснем,\nвертає електрони →\nопір ПАДАЄ", size=10.5,
                         pad=8, fill="#fdecea", stroke=POS, color=POS)
    f.append(b2)

    # Дільник напруги (праворуч): Vc → Rs(sensor) → вузол AO → RL → GND
    f.append(text(600, 92, "Дільник напруги на виході", size=13, bold=True))
    top_y = 120
    node_y = 210
    gnd_y = 300
    xline = 600
    f.append(text(xline, top_y - 8, "Vc = 5 В", size=12, color=POS, bold=True))
    # дріт від Vc до верху резистора Rs, і від низу Rs до вузла (не крізь рамку!)
    f.append(line(xline, top_y, xline, top_y + 22, color=INK, sw=2))
    f.append(line(xline, top_y + 68, xline, node_y, color=INK, sw=2))
    # Rs — резистор давача (змінний)
    f.append(rect(xline - 22, top_y + 22, 44, 46, fill="#fbe9c6", stroke=WARM, sw=1.8, rx=4))
    f.append(text(xline, top_y + 40, "Rₛ", size=13, bold=True, color="#8a6d10"))
    f.append(text(xline, top_y + 56, "давач", size=9.5, color=MUTED))
    # вузол AO
    f.append(circle(xline, node_y, 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(line(xline, node_y, xline + 46, node_y, color=FIELD, sw=2))
    f.append(text(xline + 52, node_y + 4, "→ AO (вихід)", size=12, color=FIELD, bold=True, anchor="start"))
    # RL — навантажувальний резистор
    f.append(line(xline, node_y, xline, node_y + 22, color=INK, sw=2))
    f.append(rect(xline - 22, node_y + 22, 44, 46, fill=FILL, stroke=LINE, sw=1.6, rx=4))
    f.append(text(xline, node_y + 40, "Rₗ", size=13, bold=True))
    f.append(text(xline, node_y + 56, "~10–47 кОм", size=9, color=MUTED))
    f.append(line(xline, node_y + 68, xline, gnd_y, color=INK, sw=2))
    # земля
    f.append(line(xline - 18, gnd_y, xline + 18, gnd_y, color=INK, sw=2.4))
    f.append(line(xline - 11, gnd_y + 6, xline + 11, gnd_y + 6, color=INK, sw=2))
    f.append(line(xline - 5, gnd_y + 12, xline + 5, gnd_y + 12, color=INK, sw=2))

    # стрілка від елемента до дільника
    f.append(arrow(384, 195, 500, 195, color=INK, sw=2))
    f.append(text(442, 182, "Rₛ", size=12, bold=True))

    # висновок унизу
    b, bw, bh = textbox(410, 400, "Опір давача Rₛ падає, коли є газ → напруга на AO РОСТЕ. Більше газу — вища напруга.",
                        size=12.5, pad=9, fill="#fff8e6", stroke=WARM)
    f.append(b)

    render(os.path.join(IMG, "mq-principle.svg"), W, H, *f)


# ── 2. Анатомія модуля + підключення пін-у-пін до МК ─────────────────────────
def fig_wiring():
    W, H = 840, 470
    f = []
    f.append(text(420, 28, "Модуль MQ і підключення до мікроконтролера", size=16, bold=True))

    # Плата модуля
    f.append(rect(60, 70, 300, 300, fill="#eef1f4", stroke=LINE, sw=1.6, rx=12))
    f.append(text(210, 94, "Модуль MQ (Keyes)", size=13, bold=True))

    # Металевий ковпачок давача (сітка)
    f.append(circle(140, 165, 42, fill="#dfe4ea", stroke=LINE, sw=2))
    f.append(circle(140, 165, 30, fill="#eef1f4", stroke=MUTED, sw=1))
    for dx in (-20, -8, 4, 16):
        f.append(line(140 + dx, 138, 140 + dx, 192, color=MUTED, sw=1))
    for dy in (-20, -8, 4, 16):
        f.append(line(113, 165 + dy, 167, 165 + dy, color=MUTED, sw=1))
    f.append(text(140, 224, "давач у сітчастому", size=10, color=MUTED))
    f.append(text(140, 238, "ковпачку", size=10, color=MUTED))

    # LM393 + потенціометр + світлодіоди
    b1, _, _ = textbox(285, 150, "LM393\nкомпаратор", size=11, pad=8, fill=FILL, stroke=LINE, bold=True)
    f.append(b1)
    f.append(rect(258, 190, 54, 24, fill="#cfe8ff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(285, 206, "поріг ⚙", size=10.5, color=NEG, bold=True))
    f.append(text(285, 232, "(синій гвинтик)", size=9, color=MUTED))
    f.append(circle(250, 262, 5, fill="#c0392b", stroke=POS, sw=1))
    f.append(text(300, 266, "LED живлення / DO", size=9.5, color=MUTED))
    f.append(circle(250, 280, 5, fill="#27ae60", stroke=FIELD, sw=1))

    # 4 контакти знизу плати
    pins = [("VCC", POS), ("GND", INK), ("DO", NEG), ("AO", FIELD)]
    px0, py = 100, 340
    for i, (name, col) in enumerate(pins):
        cx = px0 + i * 55
        f.append(circle(cx, py, 8, fill="#fff", stroke=col, sw=2))
        f.append(text(cx, py + 24, name, size=11.5, color=col, bold=True))

    # МК праворуч
    f.append(rect(600, 110, 180, 250, fill=FILL, stroke=LINE, sw=1.6, rx=12))
    f.append(text(690, 134, "Мікроконтролер", size=13, bold=True))
    mk = [("5 В", 180, POS), ("GND", 220, INK), ("цифр. пін", 260, NEG), ("A0 (АЦП)", 300, FIELD)]
    for name, y, col in mk:
        f.append(circle(600, y, 6, fill="#fff", stroke=col, sw=2))
        f.append(text(668, y + 4, name, size=11, color=col, bold=(col == FIELD)))

    # дроти від пінів модуля до МК
    f.append(line(100, 348, 600, 180, color=POS, sw=2))   # VCC → 5В
    f.append(line(155, 348, 600, 220, color=INK, sw=2))   # GND
    f.append(line(210, 348, 600, 260, color=NEG, sw=2))   # DO → цифр
    f.append(line(265, 348, 600, 300, color=FIELD, sw=2)) # AO → A0

    # підказки
    f.append(text(420, 402, "AO — плавна напруга (читаєш АЦП). DO — «0/1» за порогом гвинтика.",
                  size=11.5, color=MUTED))
    f.append(text(420, 420, "Живлення строго 5 В: нагрівач тягне ~150 мА (~0.8 Вт).",
                  size=11.5, color=POS, bold=True))
    f.append(text(420, 438, "На 3.3-В плату AO/DO веди через дільник — рівень інакше 5 В.",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "mq-wiring.svg"), W, H, *f)


# ── 3. Калібрувальна крива Rs/Ro у log-log: степенева залежність ──────────────
def fig_curve():
    W, H = 720, 470
    f = []
    f.append(text(360, 28, "Чому потрібне калібрування: Rs/Ro vs концентрація (log-log)", size=14.5, bold=True))

    # осі
    ox, oy = 130, 360      # початок (лівий-нижній)
    ax_w, ax_h = 470, 270
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))        # X
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))        # Y
    f.append(text(ox + ax_w / 2, oy + 42, "концентрація газу, ppm (лог. шкала)", size=11.5, color=MUTED))
    f.append(text(ox - 92, oy - ax_h / 2, "Rₛ / R₀", size=13, color=MUTED, bold=True, anchor="start"))

    # позначки X (200, 1000, 5000, 10000 ppm)
    xticks = [(0.0, "200"), (0.33, "1000"), (0.72, "5000"), (1.0, "10000")]
    for fx, lab in xticks:
        x = ox + fx * ax_w
        f.append(line(x, oy, x, oy + 5, color=INK, sw=1.4))
        f.append(text(x, oy + 20, lab, size=10, color=MUTED))
    # позначки Y (0.1, 1, 10)
    yticks = [(0.0, "0.1"), (0.5, "1"), (1.0, "10")]
    for fy, lab in yticks:
        y = oy - fy * ax_h
        f.append(line(ox - 5, y, ox, y, color=INK, sw=1.4))
        f.append(text(ox - 22, y + 4, lab, size=10, color=MUTED))

    # кілька прямих (у log-log) для різних газів — спадні
    def logline(x0f, y0f, x1f, y1f, color, name, ny):
        x0 = ox + x0f * ax_w; y0 = oy - y0f * ax_h
        x1 = ox + x1f * ax_w; y1 = oy - y1f * ax_h
        f.append(line(x0, y0, x1, y1, color=color, sw=2.4))
        f.append(text(x1 + 6, y1 + ny, name, size=11, color=color, bold=True, anchor="start"))

    logline(0.0, 0.92, 1.0, 0.30, POS, "LPG", 4)
    logline(0.0, 0.80, 1.0, 0.16, FIELD, "метан", 4)
    logline(0.0, 0.62, 1.0, 0.04, NEG, "H₂", 4)

    # рамка-пояснення (два рядки, щоб не вилазити за 720)
    b, bw, bh = textbox(360, 428, "Пряма в log-log = степенева залежність ppm = a·(Rₛ/R₀)^b.\n"
                        "R₀ — опір у чистому повітрі; калібруєш його раз, тоді рахуєш газ.",
                        size=11.5, pad=9, fill="#fff8e6", stroke=WARM)
    f.append(b)

    render(os.path.join(IMG, "mq-curve.svg"), W, H, *f)


if __name__ == "__main__":
    fig_principle()
    fig_wiring()
    fig_curve()
    print("OK: mq-principle.svg, mq-wiring.svg, mq-curve.svg")
