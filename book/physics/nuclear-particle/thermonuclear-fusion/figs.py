# -*- coding: utf-8 -*-
import sys, os
import math

# sys.path for svgkit (4 levels up from topic folder to scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def dashed_circle(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="4,4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))

def draw_cno_cycle(path):
    w, h = 920, 560
    frags = []

    # Main card container
    frags.append(rect(15, 15, 890, 530, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))

    # Main Title
    frags.append(text(w/2, 45, "Схема вуглецево-азотно-кисневого циклу (CNO-I / CN-цикл)", size=18, bold=True, color=INK))

    # Center label for Catalyst role
    cx, cy = 340, 295
    frags.append(dashed_circle(cx, cy, 75, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, dash="4,4"))
    frags.append(text(cx, cy - 20, "Ядерний каталіз", size=13, bold=True, color=INK))
    frags.append(text(cx, cy, "C, N, O не згоряють,", size=11, color=MUTED))
    frags.append(text(cx, cy + 15, "а циклюють!", size=11, color=MUTED))
    frags.append(text(cx, cy + 35, "4 p → ⁴He + 2e⁺ + 2νₑ", size=11, bold=True, color=POS))

    # Nodes of the CNO-I cycle arranged in a circle of radius R=170
    nodes = [
        {"name": "¹²C", "sub": "Вуглець-12", "x": cx, "y": cy - 170, "color": "#1e40af", "bg": "#dbeafe"},
        {"name": "¹³N", "sub": "Азот-13", "x": cx + 150, "y": cy - 85, "color": "#854d0e", "bg": "#fef08a"},
        {"name": "¹³C", "sub": "Вуглець-13", "x": cx + 150, "y": cy + 85, "color": "#1e40af", "bg": "#dbeafe"},
        {"name": "¹⁴N", "sub": "Азот-14 (Bottleneck)", "x": cx, "y": cy + 170, "color": "#991b1b", "bg": "#fee2e2"},
        {"name": "¹⁵O", "sub": "Кисень-15", "x": cx - 150, "y": cy + 85, "color": "#854d0e", "bg": "#fef08a"},
        {"name": "¹⁵N", "sub": "Азот-15", "x": cx - 150, "y": cy - 85, "color": "#1e40af", "bg": "#dbeafe"},
    ]

    # Reaction arrows and inputs/outputs between nodes
    reactions = [
        {"from": 0, "to": 1, "in": "+ p (протон)", "out": "+ γ (1.94 МЕв)", "type": "cap"},
        {"from": 1, "to": 2, "in": "", "out": "β⁺ розпад (T₁/₂=10 хв)\n+ e⁺ + νₑ (2.22 МЕв)", "type": "decay"},
        {"from": 2, "to": 3, "in": "+ p (протон)", "out": "+ γ (7.55 МЕв)", "type": "cap"},
        {"from": 3, "to": 4, "in": "+ p (найповільніша!)", "out": "+ γ (7.30 МЕв)", "type": "slow"},
        {"from": 4, "to": 5, "in": "", "out": "β⁺ розпад (T₁/₂=122 с)\n+ e⁺ + νₑ (2.75 МЕв)", "type": "decay"},
        {"from": 5, "to": 0, "in": "+ p (протон)", "out": "+ ⁴He (альфа!)\n(4.97 МЕв)", "type": "alpha"}
    ]

    # Draw reaction curved arrows and labels
    for r in reactions:
        n1 = nodes[r["from"]]
        n2 = nodes[r["to"]]
        
        mx = (n1["x"] + n2["x"]) / 2.0
        my = (n1["y"] + n2["y"]) / 2.0
        
        if r["type"] == "slow":
            stroke_col = POS
            sw = 3.0
        elif r["type"] == "decay":
            stroke_col = "#d97706"
            sw = 2.0
        elif r["type"] == "alpha":
            stroke_col = FIELD
            sw = 3.0
        else:
            stroke_col = "#2563eb"
            sw = 2.0
            
        dx = n2["x"] - n1["x"]
        dy = n2["y"] - n1["y"]
        dist = math.hypot(dx, dy)
        ux, uy = dx/dist, dy/dist
        
        start_x = n1["x"] + ux * 35
        start_y = n1["y"] + uy * 35
        end_x = n2["x"] - ux * 35
        end_y = n2["y"] - uy * 35
        
        frags.append(arrow(start_x, start_y, end_x, end_y, color=stroke_col, sw=sw))
        
        if r["in"]:
            frags.append(fitbox(mx + uy * 25 - 45, my - ux * 25 - 15, 90, 26, r["in"], size=10, fill="#ffffff", stroke=stroke_col))
        if r["out"]:
            frags.append(fitbox(mx - uy * 35 - 55, my + ux * 35 - 15, 110, 32, r["out"], size=9, fill="#f9fafb", stroke="#9ca3af"))

    # Draw nodes
    for n in nodes:
        frags.append(circle(n["x"], n["y"], 32, fill=n["bg"], stroke=n["color"], sw=2.5))
        frags.append(text(n["x"], n["y"] + 4, n["name"], size=14, bold=True, color=n["color"]))

    # Right side explanation panel
    rx = 690
    frags.append(fitbox(rx, 80, 200, 100, "1. Протонні захоплення\n¹²C, ¹³C, ¹⁴N захоплюють\nпротони p з випромінюванням\nгамма-квантів γ.", size=11, fill="#eff6ff", stroke="#2563eb"))
    frags.append(fitbox(rx, 195, 200, 100, "2. Радіоактивні розпади\n¹³N та ¹⁵O позитронно\nрозпадаються (β⁺), випускаючи\nнейтрино νₑ та позитрони e⁺.", size=11, fill="#fffbeb", stroke="#d97706"))
    frags.append(fitbox(rx, 310, 200, 105, "3. Вузьке місце циклу\nРеакція ¹⁴N(p,γ)¹⁵O — найповільніша.\nУся швидкість CNO залежить від неї;\n¹⁴N накопичується в ядрі.", size=11, fill="#fef2f2", stroke=POS, bold=True))
    frags.append(fitbox(rx, 430, 200, 95, "4. Замикання циклу\n¹⁵N(p,α)¹²C випускає ⁴He\nі відновлює ядро ¹²C.\nРезультат: 4p → ⁴He!", size=11, fill="#f0fdf4", stroke=FIELD, bold=True))

    render(path, w, h, *frags)

def draw_bethe_temperature_rates(path):
    w, h = 840, 500
    frags = []

    frags.append(rect(15, 15, 810, 470, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 42, "Залежність швидкості термоядерного енерговиділення від температури", size=18, bold=True, color=INK))

    # Graph axes area
    gx, gy, gw, gh = 70, 90, 420, 330
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))

    # Axes lines
    frags.append(arrow(gx + 30, gy + gh - 30, gx + gw - 15, gy + gh - 30, color=INK, sw=2))
    frags.append(text(gx + gw - 60, gy + gh - 10, "Температура T (10⁶ K)", size=11, color=INK, bold=True))

    frags.append(arrow(gx + 30, gy + gh - 30, gx + 30, gy + 20, color=INK, sw=2))
    frags.append(mtext(gx + 5, gy + 25, ["Енерговиділення ε", "(Вт / кг, лог. шкалa)"], size=11, color=INK, bold=True))

    # Temperature ticks
    ticks = [
        (10, "10"),
        (15.7, "15.7 (Сонце)"),
        (20, "20"),
        (25, "25"),
        (30, "30")
    ]
    for t_val, label in ticks:
        px = gx + 30 + (t_val - 5) * (gw - 60) / 27.0
        frags.append(line(px, gy + gh - 30, px, gy + gh - 25, color=INK, sw=1.5))
        frags.append(text(px, gy + gh - 12, label, size=9, color=MUTED))

    # pp-chain path (blue)
    pp_points = []
    for t_val in range(6, 32):
        px = gx + 30 + (t_val - 5) * (gw - 60) / 27.0
        py = (gy + gh - 30) - 25 * math.log10((t_val / 15.0)**4 + 0.1) - 60
        py = max(gy + 30, min(gy + gh - 35, py))
        pp_points.append((px, py))

    pp_path_str = "M " + " L ".join(["%.1f %.1f" % p for p in pp_points])
    frags.append('<path d="%s" fill="none" stroke="#2563eb" stroke-width="3"/>' % pp_path_str)

    # CNO cycle path (red/amber)
    cno_points = []
    for t_val in range(10, 32):
        px = gx + 30 + (t_val - 5) * (gw - 60) / 27.0
        py = (gy + gh - 30) - 22 * math.log10((t_val / 16.0)**17 + 0.001) - 30
        py = max(gy + 30, min(gy + gh - 35, py))
        cno_points.append((px, py))

    cno_path_str = "M " + " L ".join(["%.1f %.1f" % p for p in cno_points])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (cno_path_str, POS))

    # Crossover point annotation
    cross_x = gx + 30 + (16.2 - 5) * (gw - 60) / 27.0
    cross_y = (gy + gh - 30) - 105
    frags.append(circle(cross_x, cross_y, 6, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(dashed_circle(cross_x, cross_y, 14, fill="none", stroke=FIELD, sw=1.5, dash="3,3"))
    frags.append(fitbox(cross_x - 70, cross_y - 55, 140, 35, "Перетин: T ≈ 1.6·10⁷ K\nM ≈ 1.3 M_☉", size=10, fill="#fef3c7", stroke=FIELD, bold=True, color=FIELD))

    # Labels directly on graph
    frags.append(text(gx + 120, gy + gh - 90, "pp-ланцюжок (ε ∝ T⁴)", size=12, bold=True, color="#2563eb"))
    frags.append(text(gx + 260, gy + 70, "CNO-цикл (ε ∝ T¹⁷)", size=12, bold=True, color=POS))

    # Right side explanation panel
    rx = 515
    frags.append(fitbox(rx, 90, 290, 85, "1. pp-ланцюжок (маломасивні зорі)\nЧудовий опір температурі ε ∝ T⁴.\nДомінує в Сонці (T_c ≈ 15.7·10⁶ K),\nзабезпечує стабільне горіння мільярди років.", size=11, fill="#eff6ff", stroke="#2563eb"))
    frags.append(fitbox(rx, 190, 290, 100, "2. CNO-цикл (масивні зорі M > 1.3 M_☉)\nЕкстремальна чутливість ε ∝ T¹⁷!\nНайменше підвищення температури\nвикликає вибуховий приріст енергії.\nДомінує у гарячих ядрах.", size=11, fill="#fef2f2", stroke=POS, bold=True))
    frags.append(fitbox(rx, 305, 290, 115, "3. Наслідки для структури зорі\nЧерез ε ∝ T¹⁷ енерговиділення CNO\nгостро сфокусоване в центрі ядра.\nЦе створює колосальний потік тепла\nі формує конвективне ядро в масивних зорях.", size=11, fill="#f0fdf4", stroke=FIELD))

    render(path, w, h, *frags)

if __name__ == '__main__':
    img_dir = make_img_dir()
    draw_cno_cycle(os.path.join(img_dir, 'cno-cycle.svg'))
    draw_bethe_temperature_rates(os.path.join(img_dir, 'bethe-temperature-rates.svg'))
    print("All figures successfully generated in img/")
