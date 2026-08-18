# -*- coding: utf-8 -*-
"""Фігури до теми «Пробій діелектрика».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"

def svg_path(points, stroke=LINE, sw=1.5, fill='none', dash=None):
    d_pts = []
    for i, pt in enumerate(points):
        cmd = 'M' if i == 0 else 'L'
        d_pts.append(f"{cmd} {pt[0]:.1f} {pt[1]:.1f}")
    d_str = " ".join(d_pts)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{dash_attr}/>'

# ── Фігура 1: Механізм електронної лавини та ударної іонізації ───────────────
def fig_avalanche_mechanism():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Електронна лавина та ударна іонізація в твердому діелектрику", size=15, bold=True))

    # Зони: валентна та провідності
    f.append(rect(60, 60, 640, 70, fill='#eef4ff', stroke=COLOR_BLUE, sw=1.5, rx=4))
    f.append(text(180, 85, "Зона провідності (порожня за T = 0 K)", size=12, bold=True, color=COLOR_BLUE))

    f.append(rect(60, 250, 640, 70, fill='#fdf2e9', stroke=COLOR_ORANGE, sw=1.5, rx=4))
    f.append(text(180, 275, "Валентна зона (заповнена електронами)", size=12, bold=True, color=COLOR_ORANGE))

    # Заборонена зона
    f.append(line(60, 130, 700, 130, color='#d6dde6', sw=1, dash='4,4'))
    f.append(line(60, 250, 700, 250, color='#d6dde6', sw=1, dash='4,4'))
    f.append(arrow(670, 245, 670, 135, color=INK, sw=1.2))
    f.append(arrow(670, 135, 670, 245, color=INK, sw=1.2))
    f.append(text(655, 190, "Eg > 4..9 eV", size=11, bold=True, color=INK, anchor='end'))

    # Електричне поле E
    f.append(arrow(80, 200, 220, 200, color=COLOR_RED, sw=2))
    f.append(text(150, 185, "Електричне поле E", size=12, bold=True, color=COLOR_RED))

    # Початковий електрон 1
    f.append(circle(120, 100, 8, fill=COLOR_BLUE, stroke='none'))
    f.append(text(120, 100, "e-", size=9, bold=True, color='#ffffff'))
    f.append(text(120, 80, "Затравочний електрон", size=10, color=INK))

    # Траєкторія прискорення
    f.append(svg_path([ (128, 100), (220, 100) ], stroke=COLOR_BLUE, sw=2, dash='3,3'))
    f.append(arrow(210, 100, 225, 100, color=COLOR_BLUE, sw=2))

    # Зіткнення та ударна іонізація
    f.append(circle(235, 100, 14, fill='#ffffff', stroke=COLOR_RED, sw=1.8))
    f.append(text(235, 104, "★", size=12, color=COLOR_RED))
    f.append(text(235, 75, "Ударне зіткнення", size=10, bold=True, color=COLOR_RED))

    # Вибивання електрона з валентної зони
    f.append(svg_path([ (235, 270), (235, 115) ], stroke=COLOR_GREEN, sw=1.8, dash='4,4'))
    f.append(arrow(235, 135, 235, 115, color=COLOR_GREEN, sw=1.8))
    f.append(circle(235, 270, 8, fill='#e74c3c', stroke='none')) # Дірка
    f.append(text(235, 270, "h+", size=9, bold=True, color='#ffffff'))
    f.append(text(235, 295, "Генерація дірки", size=10, color=COLOR_RED))

    # Два первинні електрони після іонізації
    f.append(svg_path([ (245, 100), (360, 80) ], stroke=COLOR_BLUE, sw=1.8, dash='2,2'))
    f.append(circle(360, 80, 8, fill=COLOR_BLUE, stroke='none'))
    f.append(text(360, 80, "e-", size=9, bold=True, color='#ffffff'))

    f.append(svg_path([ (245, 100), (360, 115) ], stroke=COLOR_BLUE, sw=1.8, dash='2,2'))
    f.append(circle(360, 115, 8, fill=COLOR_BLUE, stroke='none'))
    f.append(text(360, 115, "e-", size=9, bold=True, color='#ffffff'))

    # Наступна стадія розмноження (4 електрони)
    f.append(svg_path([ (368, 80), (470, 70) ], stroke=COLOR_BLUE, sw=1.5, dash='2,2'))
    f.append(circle(470, 70, 7, fill=COLOR_BLUE, stroke='none'))

    f.append(svg_path([ (368, 80), (470, 90) ], stroke=COLOR_BLUE, sw=1.5, dash='2,2'))
    f.append(circle(470, 90, 7, fill=COLOR_BLUE, stroke='none'))

    f.append(svg_path([ (368, 115), (470, 110) ], stroke=COLOR_BLUE, sw=1.5, dash='2,2'))
    f.append(circle(470, 110, 7, fill=COLOR_BLUE, stroke='none'))

    f.append(svg_path([ (368, 115), (470, 125) ], stroke=COLOR_BLUE, sw=1.5, dash='2,2'))
    f.append(circle(470, 125, 7, fill=COLOR_BLUE, stroke='none'))

    f.append(text(540, 98, "Лавинний приріст носіїв: N(t) = N0 exp(α x)", size=11, bold=True, color=COLOR_BLUE))

    render(os.path.join(IMG, "avalanche-mechanism.svg"), W, H, *f)

# ── Фігура 2: Тепловий вибух і баланс потужності ──────────────────────────────
def fig_thermal_runaway():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Тепловий баланс та умова теплового вибуху в діелектрику", size=15, bold=True))

    ox, oy = 100, 320
    f.append(arrow(ox, oy, ox + 600, oy, color=INK, sw=1.8))
    f.append(text(ox + 600, oy + 25, "Температура T (°C)", size=12, bold=True, color=INK))

    f.append(arrow(ox, oy, ox, oy - 260, color=INK, sw=1.8))
    f.append(text(ox - 10, oy - 265, "Потужність Q (Вт)", size=12, bold=True, color=INK))

    # Початкова температура T0
    f.append(line(ox + 50, oy, ox + 50, oy - 250, color='#bdc3c7', sw=1.2, dash='4,4'))
    f.append(text(ox + 50, oy + 18, "T0 (довкілля)", size=11, color=INK))

    # Пряма тепловідведення Q_loss
    f.append(line(ox + 50, oy, ox + 550, oy - 230, color=COLOR_GREEN, sw=2.2))
    f.append(text(ox + 460, oy - 240, "Тепловідведення Q_loss = λ (T - T0)", size=11, bold=True, color=COLOR_GREEN))

    # Крива виділення Q_gen1
    f.append(svg_path([ (ox + 50, oy), (ox + 180, oy - 30), (ox + 350, oy - 80), (ox + 520, oy - 190) ], stroke=COLOR_BLUE, sw=2))
    f.append(text(ox + 420, oy - 45, "Q_gen (слабке поле E1 < E_cr)", size=11, bold=True, color=COLOR_BLUE))

    # Точка стабільного теплового балансу A
    f.append(circle(ox + 215, oy - 42, 6, fill=COLOR_GREEN, stroke='none'))
    f.append(text(ox + 215, oy - 20, "Точка стабільності A", size=10, bold=True, color=COLOR_GREEN))

    # Крива виділення Q_gen2
    f.append(svg_path([ (ox + 50, oy), (ox + 180, oy - 55), (ox + 320, oy - 114), (ox + 500, oy - 240) ], stroke=COLOR_ORANGE, sw=2, dash='5,5'))
    f.append(circle(ox + 320, oy - 114, 6, fill=COLOR_ORANGE, stroke='none'))
    f.append(text(ox + 320, oy - 90, "Критична точка E_cr", size=10, bold=True, color=COLOR_ORANGE))

    # Крива виділення Q_gen3
    f.append(svg_path([ (ox + 50, oy), (ox + 160, oy - 70), (ox + 280, oy - 140), (ox + 420, oy - 260) ], stroke=COLOR_RED, sw=2.5))
    f.append(text(ox + 120, oy - 200, "Q_gen (E3 > E_cr): Тепловий вибух!", size=11, bold=True, color=COLOR_RED))

    # Стрелка розгону та напис
    f.append(arrow(ox + 300, oy - 150, ox + 300, oy - 210, color=COLOR_RED, sw=1.8))
    f.append(text(ox + 310, oy - 180, "Q_gen > Q_loss (некерований нагрів)", size=10, color=COLOR_RED, anchor="start"))

    render(os.path.join(IMG, "thermal-runaway.svg"), W, H, *f)

# ── Фігура 3: Карта механізмів пробою залежно від часу ───────────────────────
def fig_breakdown_mechanisms_map():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Карта режимів пробою: тривалість поля vs пробивна міцність", size=15, bold=True))

    ox, oy = 100, 320
    f.append(arrow(ox, oy, ox + 600, oy, color=INK, sw=1.8))
    f.append(text(ox + 600, oy + 25, "Тривалість прикладання напруги t (с)", size=12, bold=True, color=INK))

    f.append(arrow(ox, oy, ox, oy - 260, color=INK, sw=1.8))
    f.append(text(ox - 10, oy - 265, "Пробивне поле E_bd (МВ/м)", size=12, bold=True, color=INK))

    times = [ ("10⁻⁹ с", 50), ("10⁻⁶ с", 180), ("10⁻³ с", 310), ("1 с", 440), ("10⁵ с", 550) ]
    for label, xpos in times:
        f.append(line(ox + xpos, oy, ox + xpos, oy - 6, color=INK, sw=1.5))
        f.append(text(ox + xpos, oy + 18, label, size=10, color=INK))

    f.append(svg_path([ (ox + 20, oy - 240), (ox + 140, oy - 210), (ox + 280, oy - 150), (ox + 420, oy - 90), (ox + 560, oy - 50) ], stroke=COLOR_BLUE, sw=2.5))

    # Області режимів
    f.append(rect(ox + 20, oy - 235, 120, 160, fill='#eef4ff', stroke='none'))
    f.append(text(ox + 80, oy - 180, "Електронний", size=11, bold=True, color=COLOR_BLUE))
    f.append(text(ox + 80, oy - 165, "(лавинний)", size=10, color=COLOR_BLUE))

    f.append(rect(ox + 160, oy - 185, 140, 140, fill='#fdf2e9', stroke='none'))
    f.append(text(ox + 230, oy - 140, "Тепловий пробій", size=11, bold=True, color=COLOR_ORANGE))
    f.append(text(ox + 230, oy - 125, "(дисипація тепла)", size=10, color=COLOR_ORANGE))

    f.append(rect(ox + 320, oy - 130, 230, 110, fill='#eaafaf', stroke='none'))
    f.append(text(ox + 430, oy - 90, "Електрохімічне старіння", size=11, bold=True, color=COLOR_RED))
    f.append(text(ox + 430, oy - 75, "та часткові розряди (триїнг)", size=10, color=COLOR_RED))

    render(os.path.join(IMG, "breakdown-mechanisms-map.svg"), W, H, *f)

# ── Фігура 4: Розвиток електричного триїнгу від мікропори ────────────────────
def fig_treeing_discharges():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Розвиток електричного триїнгу (дендритів) від мікропори", size=15, bold=True))

    f.append(rect(60, 50, 640, 25, fill='#bdc3c7', stroke='#7f8c8d', sw=1.5, rx=2))
    f.append(text(W / 2, 67, "Верхній електрод (висока напруга HV)", size=12, bold=True, color=INK))

    f.append(rect(60, 310, 640, 25, fill='#bdc3c7', stroke='#7f8c8d', sw=1.5, rx=2))
    f.append(text(W / 2, 327, "Нижній електрод (заземлення GND)", size=12, bold=True, color=INK))

    f.append(rect(60, 75, 640, 235, fill='#f8f9fa', stroke='#d6dde6', sw=1.5))
    f.append(text(140, 100, "Твердий діелектрик (полімер / кераміка)", size=11, color='#7f8c8d'))

    # Пора у діелектрику
    f.append(rect(355, 96, 50, 28, fill='#fff3cd', stroke=COLOR_ORANGE, sw=1.8, rx=14))
    f.append(text(380, 110, "Мікропора", size=10, bold=True, color=COLOR_ORANGE))
    f.append(text(480, 110, "Часткові розряди (PD)", size=10, bold=True, color=COLOR_RED))
    f.append(arrow(430, 110, 410, 110, color=COLOR_RED, sw=1.2))

    branches = [
        [ (380, 124), (370, 150), (350, 175), (330, 200) ],
        [ (370, 150), (385, 180), (395, 210) ],
        [ (380, 124), (395, 160), (415, 185), (430, 220), (450, 255) ],
        [ (415, 185), (405, 215), (410, 245) ],
        [ (330, 200), (320, 230), (315, 270), (310, 310) ]
    ]
    for b in branches:
        f.append(svg_path(b, stroke=COLOR_PURPLE, sw=2))

    f.append(circle(310, 310, 6, fill=COLOR_RED, stroke='none'))
    f.append(text(230, 290, "Критичний пробій!", size=11, bold=True, color=COLOR_RED))
    f.append(arrow(260, 295, 300, 305, color=COLOR_RED, sw=1.5))

    render(os.path.join(IMG, "treeing-discharges.svg"), W, H, *f)

if __name__ == '__main__':
    fig_avalanche_mechanism()
    fig_thermal_runaway()
    fig_breakdown_mechanisms_map()
    fig_treeing_discharges()
    print("Всі 4 фігури успішно згенеровано у ./img/")
