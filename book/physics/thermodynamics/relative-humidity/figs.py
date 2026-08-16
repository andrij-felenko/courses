# -*- coding: utf-8 -*-
"""Фігури до теми «Відносна вологість повітря».
Запуск із теки теми: python figs.py -> SVG у ./img/
"""
import sys, os, math

# Чотири рівні вгору від book/physics/thermodynamics/relative-humidity до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Колірна палітра
BLUE_WATER = "#2457d6"
BLUE_LIGHT = "#e8f1fd"
RED_HOT    = "#c0392b"
RED_LIGHT  = "#fdecea"
GREEN_OK   = "#27ae60"
GREEN_BG   = "#eaefeb"
ORANGE     = "#d97706"
MUTED_GRAY = "#6b7280"
BORDER_GRAY= "#d1d5db"
FILL_BG    = "#f9fafb"


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=FILL_BG, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


# ── Фігура 1: Крива тиску насиченої пари та шлях до точки роси ────────────
def fig_saturation_curve():
    W, H = 840, 540
    frags = []

    ox, oy = 90, 440
    gw, gh = 700, 370
    
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))
    
    frags.append(text(ox + gw / 2, oy + 55, "Температура T (°C)", size=15, bold=True))
    frags.append(text(ox - 55, oy - gh / 2, "Парціальний тиск водяної пари e (гПа)", size=15, bold=True, anchor="middle"))

    temps = [0, 10, 20, 30, 40]
    def es(t):
        return 6.112 * math.exp(17.67 * t / (t + 243.5))

    max_p = 80.0
    for t in temps:
        cx = ox + (t / 40.0) * (gw - 40)
        frags.append(line(cx, oy, cx, oy + 6, color=LINE, sw=1.5))
        frags.append(text(cx, oy + 24, "%d°C" % t, size=13))

    p_ticks = [0, 20, 40, 60, 80]
    for p in p_ticks:
        cy = oy - (p / max_p) * (gh - 30)
        frags.append(line(ox - 6, cy, ox, cy, color=LINE, sw=1.5))
        frags.append(text(ox - 12, cy + 4, "%d" % p, size=13, anchor="end"))

    curve_pts = []
    for i in range(101):
        t = (i / 100.0) * 40.0
        p_val = es(t)
        cx = ox + (t / 40.0) * (gw - 40)
        cy = oy - (p_val / max_p) * (gh - 30)
        curve_pts.append((cx, cy))

    poly_pts = [(ox, oy)] + curve_pts + [(curve_pts[-1][0], oy)]
    frags.append(polygon(poly_pts, fill="#eef6ff", stroke="none"))
    frags.append(polyline(curve_pts, color=BLUE_WATER, sw=3.5))

    t_A, e_A = 30.0, 17.0
    xA = ox + (t_A / 40.0) * (gw - 40)
    yA = oy - (e_A / max_p) * (gh - 30)

    t_B = 15.0
    xB = ox + (t_B / 40.0) * (gw - 40)
    yB = yA

    frags.append(line(xA, yA, xB, yB, color=RED_HOT, sw=2.5, dash="6,4"))
    frags.append(arrow(xA, yA, (xA + xB) / 2 + 10, yA, color=RED_HOT, sw=2.5))

    frags.append(line(xA, yA, xA, oy, color=MUTED_GRAY, sw=1.2, dash="4,4"))
    frags.append(line(xB, yB, xB, oy, color=MUTED_GRAY, sw=1.2, dash="4,4"))
    frags.append(line(ox, yA, xB, yA, color=MUTED_GRAY, sw=1.2, dash="4,4"))

    frags.append(circle(xA, yA, 6, fill=ORANGE, stroke=INK, sw=1.8))
    frags.append(circle(xB, yB, 6, fill=BLUE_WATER, stroke=INK, sw=1.8))

    bA, _, _ = textbox(xA + 90, yA - 30, "Стан A: T = 30°C, e = 17 гПа\nRH = e / e_s = 40%", size=12, fill=FILL_BG, stroke=ORANGE)
    frags.append(bA)

    bB, _, _ = textbox(xB - 95, yB - 45, "Точка роси B: T_d ≈ 15°C\nRH = 100% (Конденсація)", size=12, fill=BLUE_LIGHT, stroke=BLUE_WATER)
    frags.append(bB)

    frags.append(text(ox + 380, oy - 270, "Крива насичення e_s(T)", size=14, color=BLUE_WATER, bold=True))
    frags.append(text(ox + 470, oy - 120, "Ненасичена пара (RH < 100%)", size=13, color=MUTED_GRAY, italic=True))
    frags.append(text(ox + 180, oy - 310, "Перенасичена пара\n(Випадання роси / туман)", size=13, color=RED_HOT, italic=True))

    render(os.path.join(IMG, "saturation-curve.svg"), W, H, *frags, title="Фазова крива тиску насиченої пари води e_s(T) та точка роси")


# ── Фігура 2: Принцип дії психрометра ─────────────────────────────────────
def fig_psychrometer_concept():
    W, H = 860, 520
    frags = []

    # Сухий термометр (зліва)
    sx = 180
    sy = 100
    tw, th = 34, 250
    
    frags.append(rect(sx, sy, tw, th, fill=FILL_BG, stroke=LINE, sw=2, rx=15))
    frags.append(rect(sx + 13, sy + 20, 8, th - 40, fill="#ffffff", stroke=MUTED_GRAY, sw=1))
    frags.append(rect(sx + 13, sy + 100, 8, th - 120, fill=RED_HOT, stroke="none"))
    frags.append(circle(sx + 17, sy + th - 10, 16, fill=RED_HOT, stroke=LINE, sw=2))

    b_dry, _, _ = textbox(sx + 17, sy - 30, "Сухий термометр\nT = 25.0°C", size=14, bold=True, fill=RED_LIGHT, stroke=RED_HOT)
    frags.append(b_dry)

    # Вологий термометр (справа)
    wx = 640
    wy = 100

    frags.append(rect(wx, wy, tw, th, fill=FILL_BG, stroke=LINE, sw=2, rx=15))
    frags.append(rect(wx + 13, wy + 20, 8, th - 40, fill="#ffffff", stroke=MUTED_GRAY, sw=1))
    frags.append(rect(wx + 13, wy + 145, 8, th - 165, fill=BLUE_WATER, stroke="none"))
    frags.append(circle(wx + 17, wy + th - 10, 16, fill=BLUE_WATER, stroke=LINE, sw=2))

    # Волога тканина (ґніт) навколо резервуара
    frags.append(polygon([(wx - 4, wy + th - 26), (wx + 38, wy + th - 26), (wx + 38, wy + th + 8), (wx - 4, wy + th + 8)], fill="#bfe0f2", stroke=BLUE_WATER, sw=2))

    # Резервуар з водою під вологим термометром - зсунутий нижче (на 60px), щоб не налізав!
    frags.append(rect(wx - 10, wy + th + 55, 54, 40, fill=BLUE_LIGHT, stroke=BLUE_WATER, sw=2, rx=4))
    frags.append(text(wx + 17, wy + th + 79, "Вода", size=11, color=BLUE_WATER, bold=True))

    # Ґніт (довша смужка тканини між резервуаром термометра і ванночкою води)
    frags.append(rect(wx + 10, wy + th + 10, 14, 45, fill="#bfe0f2", stroke=BLUE_WATER, sw=1.5))

    # Стрелочки випаровування від вологого ґніту
    for dx, dy in [(-45, -15), (45, -15), (-40, 15), (45, 15)]:
        frags.append(arrow(wx + 17, wy + th - 10, wx + 17 + dx, wy + th - 10 + dy, color=BLUE_WATER, sw=1.8))
    
    frags.append(text(wx + 110, wy + th - 10, "Потік випаровування H₂O\n(поглинає L_v Дж/кг)", size=12, color=BLUE_WATER, bold=True, anchor="start"))

    b_wet, _, _ = textbox(wx + 17, wy - 30, "Вологий термометр\nT_w = 18.5°C", size=14, bold=True, fill=BLUE_LIGHT, stroke=BLUE_WATER)
    frags.append(b_wet)

    # Центральний пояснювальний блок (баланс енергії)
    b_mid, _, _ = textbox(410, 240, "Психрометрична різниця:\nΔT = T − T_w = 6.5°C\n\nТепловий баланс ґноту:\nКонвективний приплив тепла\n= Потік охолодження випаровуванням\n\nЧим сухіше повітря (нижча RH),\nтим швидше випаровування\nі більша різниця ΔT!", size=13, fill=GREEN_BG, stroke=GREEN_OK, pad=12)
    frags.append(b_mid)

    render(os.path.join(IMG, "psychrometer-concept.svg"), W, H, *frags, title="Фізичний принцип психрометра: охолодження випаровуванням")


# ── Фігура 3: Зміна відносної вологості під час нагрівання повітря ───────
def fig_humidity_temperature_relation():
    W, H = 860, 480
    frags = []

    x1, y1 = 100, 110
    bw, bh = 260, 270
    
    frags.append(rect(x1, y1, bw, bh, fill=BLUE_LIGHT, stroke=BLUE_WATER, sw=2, rx=10))
    frags.append(text(x1 + bw / 2, y1 + 30, "Зовнішнє повітря (взимку)", size=15, bold=True, color=BLUE_WATER))
    
    info1 = ["Температура: T = 0°C",
             "Парціальний тиск: e = 4.9 гПа",
             "Тиск насичення: e_s = 6.1 гПа",
             "",
             "Відносна вологість:",
             "RH = (4.9 / 6.1) · 100%",
             "= 80% (Повітря вологе)"]
    frags.append(mtext(x1 + bw / 2, y1 + 65, info1, size=13, anchor="middle", lh=1.35))

    # Стрелка нагрівання в центрі - окремі окремі тексти вище і нижче стрілки, щоб не накладалися!
    frags.append(arrow(x1 + bw + 20, y1 + bh / 2, x1 + bw + 120, y1 + bh / 2, color=RED_HOT, sw=3.5))
    frags.append(text(x1 + bw + 70, y1 + bh / 2 - 25, "Нагрівання в батареї", size=13, color=RED_HOT, bold=True, anchor="middle"))
    frags.append(text(x1 + bw + 70, y1 + bh / 2 + 30, "(вміст H₂O сталий)", size=12, color=MUTED_GRAY, italic=True, anchor="middle"))

    x2 = x1 + bw + 140
    frags.append(rect(x2, y1, bw, bh, fill=RED_LIGHT, stroke=RED_HOT, sw=2, rx=10))
    frags.append(text(x2 + bw / 2, y1 + 30, "Повітря в кімнаті (після нагріву)", size=15, bold=True, color=RED_HOT))

    info2 = ["Температура: T = 22°C",
             "Парціальний тиск: e = 4.9 гПа",
             "Тиск насичення: e_s = 26.4 гПа!",
             "",
             "Відносна вологість:",
             "RH = (4.9 / 26.4) · 100%",
             "= 18.5% (Вкрай сухе)"]
    frags.append(mtext(x2 + bw / 2, y1 + 65, info2, size=13, anchor="middle", lh=1.35))

    b_bot, _, _ = textbox(W / 2, y1 + bh + 50, "Висновок: При ізобаричному нагріванні абсолютна кількість вологи не змінюється (e = const),\nале тиск насичення e_s(T) зростає експоненційно -> Відносна вологість RH катастрофічно падає!", size=13, fill=FILL_BG, stroke=INK, pad=10)
    frags.append(b_bot)

    render(os.path.join(IMG, "humidity-temperature-relation.svg"), W, H, *frags, title="Падіння відносної вологості під час нагрівання повітря взимку")


# ── Фігура 4: Будова ємнісного полімерного давача вологості ───────────────
def fig_capacitive_sensor():
    W, H = 840, 500
    frags = []

    cx, cy = 140, 100
    sw, sh = 560, 240

    frags.append(rect(cx, cy, sw, sh, fill=FILL_BG, stroke=LINE, sw=2, rx=8))

    frags.append(rect(cx + 40, cy + 170, sw - 80, 40, fill="#b8bcc4", stroke=INK, sw=2, rx=4))
    frags.append(text(cx + sw / 2, cy + 195, "Нижній металевий електрод (обкладка 1)", size=14, bold=True))

    frags.append(rect(cx + 40, cy + 90, sw - 80, 80, fill="#fef3c7", stroke=ORANGE, sw=2, rx=4))
    frags.append(text(cx + sw / 2, cy + 120, "Гігроскопічний полімерний шар (діелектрик)", size=14, bold=True, color=ORANGE))
    frags.append(text(cx + sw / 2, cy + 145, "Абсорбує молекули вологи H₂O -> ε_r зростає від ≈ 3.0 до 80.0!", size=12, color=MUTED_GRAY, italic=True))

    frags.append(rect(cx + 40, cy + 50, sw - 80, 40, fill="#d1d5db", stroke=INK, sw=2, rx=4))
    frags.append(text(cx + sw / 2, cy + 74, "Пористий верхній електрод (пропускає водяну пару H₂O)", size=14, bold=True))

    # Молекули водяної пари (кружечки з r=11 та size=10, щоб не порушувати правило >8px!)
    for mx, my in [(cx + 90, cy + 20), (cx + 210, cy + 15), (cx + 330, cy + 22), (cx + 450, cy + 18)]:
        frags.append(circle(mx, my, 11, fill=BLUE_LIGHT, stroke=BLUE_WATER, sw=1.5))
        frags.append(text(mx, my + 3, "H₂O", size=10, color=BLUE_WATER, bold=True))
        frags.append(arrow(mx, my + 12, mx, my + 55, color=BLUE_WATER, sw=1.8))

    frags.append(line(cx + 100, cy + 210, cx + 100, cy + 300, color=INK, sw=2.5))
    frags.append(line(cx + 460, cy + 50, cx + 460, cy + 10, color=INK, sw=2.5))
    frags.append(line(cx + 460, cy + 10, cx + 580, cy + 10, color=INK, sw=2.5))
    frags.append(line(cx + 580, cy + 10, cx + 580, cy + 300, color=INK, sw=2.5))

    b_meas, _, _ = textbox(cx + sw / 2, cy + 330, "Формула ємності: C = ε₀ · ε_r(RH) · A / d\nЗміна вологості RH -> зміна ε_r -> зміна ємності C -> вимірювання АЦП / генератором частоти", size=13, fill=GREEN_BG, stroke=GREEN_OK, pad=10)
    frags.append(b_meas)

    render(os.path.join(IMG, "capacitive-sensor.svg"), W, H, *frags, title="Принцип будови та роботи ємнісного полімерного давача вологості")


if __name__ == "__main__":
    fig_saturation_curve()
    fig_psychrometer_concept()
    fig_humidity_temperature_relation()
    fig_capacitive_sensor()
    print("Фігури успішно згенеровано у ./img/")
