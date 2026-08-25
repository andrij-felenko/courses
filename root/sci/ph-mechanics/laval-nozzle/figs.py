# -*- coding: utf-8 -*-
"""Фігури до теми «Сопло Лаваля».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_SUB = "#2980b9"   # дозвуковий потік (синій)
COLOR_SONIC = "#e67e22" # критичний переріз / звук (помаранчевий)
COLOR_SUPER = "#c0392b" # надзвуковий потік (червоний)
COLOR_SHOCK = "#8e44ad" # скачок ущільнення (фіолетовий)
COLOR_WALL = "#34495e"  # стінки сопла (темно-сірий)
COLOR_GRID = "#ecf0f1"  # сітка

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'

def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def uarrow(x, y, ux, uy, L, color, sw=2.5):
    return arrow(x, y, x + ux * L, y + uy * L, color=color, sw=sw)

# ── Фігура 1: Геометрія та фізичні зони сопла Лаваля ──────────────────────────
def fig_nozzle_geometry():
    W, H = 960, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Геометрія та фізичні зони сопла Лаваля", size=17, bold=True))
    
    cy = 180
    
    f.append(line(50, cy, 910, cy, color="#bdc3c7", sw=1.2, dash="5,5"))
    f.append(text(925, cy + 4, "x", size=13, italic=True, color=MUTED))
    
    f.append(line(380, 50, 380, 310, color=COLOR_SONIC, sw=1.5, dash="4,4"))
    
    pts_sub_top = [(80, cy - 130), (180, cy - 105), (280, cy - 70), (380, cy - 50)]
    pts_sub_bot = [(380, cy + 50), (280, cy + 70), (180, cy + 105), (80, cy + 130)]
    poly_sub = pts_sub_top + pts_sub_bot
    f.append(polygon(poly_sub, fill="#ebf5fb", stroke="none", sw=0))
    
    pts_sup_top = [(380, cy - 50), (500, cy - 75), (650, cy - 115), (780, cy - 145), (880, cy - 160)]
    pts_sup_bot = [(880, cy + 160), (780, cy + 145), (650, cy + 115), (500, cy + 75), (380, cy + 50)]
    poly_sup = pts_sup_top + pts_sup_bot
    f.append(polygon(poly_sup, fill="#fdf2e9", stroke="none", sw=0))
    
    path_top = "M 80,50 C 200,60 300,130 380,130 C 460,130 650,50 880,20"
    path_bot = "M 80,310 C 200,300 300,230 380,230 C 460,230 650,310 880,340"
    f.append(path(path_top, fill="none", stroke=COLOR_WALL, sw=4))
    f.append(path(path_bot, fill="none", stroke=COLOR_WALL, sw=4))
    
    path_top_outer = "M 80,40 C 200,50 300,120 380,120 C 460,120 650,40 880,10"
    path_bot_outer = "M 80,320 C 200,310 300,240 380,240 C 460,240 650,320 880,350"
    f.append(path(path_top_outer, fill="none", stroke="#95a5a6", sw=1.5, dash="2,4"))
    f.append(path(path_bot_outer, fill="none", stroke="#95a5a6", sw=1.5, dash="2,4"))
    
    f.append(text(180, cy - 142, "Конфузор (A₁)", size=13, bold=True, color=COLOR_SUB))
    f.append(text(380, cy - 142, "Горловина A*", size=13, bold=True, color=COLOR_SONIC))
    f.append(text(650, cy - 142, "Дифузор (A₂)", size=13, bold=True, color=COLOR_SUPER))
    
    f.append(arrow(110, cy, 170, cy, color=COLOR_SUB, sw=2.5))
    f.append(text(140, cy - 12, "M < 1", size=13, bold=True, color=COLOR_SUB))
    
    f.append(arrow(350, cy, 410, cy, color=COLOR_SONIC, sw=3.0))
    f.append(text(380, cy - 12, "M = 1", size=13, bold=True, color=COLOR_SONIC))
    
    f.append(arrow(600, cy, 690, cy, color=COLOR_SUPER, sw=3.5))
    f.append(text(645, cy - 12, "M > 1", size=13, bold=True, color=COLOR_SUPER))
    
    gy_top = 370
    gy_bot = 490
    f.append(line(80, gy_bot, 880, gy_bot, color="#bdc3c7", sw=1.2))
    f.append(line(80, gy_top, 80, gy_bot, color="#bdc3c7", sw=1.2))
    f.append(text(65, gy_top + 10, "P, M", size=12, italic=True, color=MUTED))
    f.append(line(380, gy_top, 380, gy_bot, color=COLOR_SONIC, sw=1.0, dash="3,3"))
    
    path_P = f"M 80,{gy_top + 15} C 250,{gy_top + 25} 350,{gy_top + 55} 380,{gy_top + 65} C 450,{gy_top + 80} 650,{gy_top + 105} 880,{gy_top + 112}"
    f.append(path(path_P, fill="none", stroke=COLOR_SUB, sw=2.5))
    f.append(text(150, gy_top + 28, "Тиск P(x)", size=12, bold=True, color=COLOR_SUB))
    
    path_M = f"M 80,{gy_bot - 10} C 250,{gy_bot - 20} 350,{gy_bot - 50} 380,{gy_bot - 60} C 450,{gy_bot - 75} 650,{gy_bot - 100} 880,{gy_bot - 112}"
    f.append(path(path_M, fill="none", stroke=COLOR_SUPER, sw=2.5))
    f.append(text(720, gy_bot - 75, "Число Маха M(x)", size=12, bold=True, color=COLOR_SUPER))
    
    f.append(circle(380, gy_top + 65, 4, fill=COLOR_SONIC))
    f.append(text(440, gy_top + 63, "P* (критичний)", size=11, color=COLOR_SONIC))
    
    render(os.path.join(IMG, 'nozzle-geometry.svg'), W, H, *f)

# ── Фігура 2: Диференціальне співвідношення Гюгоньо ────────────────────────────
def fig_hugoniot_relation():
    W, H = 940, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Зв'язок зміни перерізу та швидкості: співвідношення Гюгоньо", size=17, bold=True))
    
    box_f, _, _ = textbox(W / 2, 70, "dA / A = (M² - 1) · (du / u)", size=16, pad=10,
                          fill="#f4f6f7", stroke="#7f8c8d", sw=1.5, bold=True)
    f.append(box_f)
    
    x1 = 240
    f.append(text(x1, 130, "Дозвуковий режим (M < 1)", size=15, bold=True, color=COLOR_SUB))
    f.append(text(x1, 150, "M² - 1 < 0  =>  знаки dA та du ПРОТИЛЕЖНІ", size=12.5, color=MUTED))
    
    cy1 = 230
    pts_conv = [(x1-150, cy1-45), (x1+150, cy1-20), (x1+150, cy1+20), (x1-150, cy1+45)]
    f.append(polygon(pts_conv, fill="#ebf5fb", stroke=COLOR_SUB, sw=2))
    f.append(arrow(x1-100, cy1, x1-40, cy1, color=COLOR_SUB, sw=2))
    f.append(arrow(x1+20, cy1, x1+100, cy1, color=COLOR_SUB, sw=3.2))
    f.append(text(x1, cy1 - 8, "du > 0 (розгін)", size=12, bold=True, color=COLOR_SUB))
    f.append(textbox(x1, cy1 + 80, "Звуження каналу (dA < 0)\nприскорює дозвуковий газ", size=12, pad=6,
                     fill="#ffffff", stroke=COLOR_SUB, sw=1.2)[0])

    x2 = 700
    f.append(text(x2, 130, "Надзвуковий режим (M > 1)", size=15, bold=True, color=COLOR_SUPER))
    f.append(text(x2, 150, "M² - 1 > 0  =>  знаки dA та du ЗБІГАЮТЬСЯ", size=12.5, color=MUTED))
    
    cy2 = 230
    pts_div = [(x2-150, cy2-20), (x2+150, cy2-45), (x2+150, cy2+45), (x2-150, cy2+20)]
    f.append(polygon(pts_div, fill="#fdf2e9", stroke=COLOR_SUPER, sw=2))
    f.append(arrow(x2-100, cy2, x2-40, cy2, color=COLOR_SUPER, sw=2.5))
    f.append(arrow(x2+20, cy2, x2+110, cy2, color=COLOR_SUPER, sw=3.8))
    f.append(text(x2, cy2 - 8, "du > 0 (розгін)", size=12, bold=True, color=COLOR_SUPER))
    f.append(textbox(x2, cy2 + 80, "Розширення каналу (dA > 0)\nприскорює надзвуковий газ!", size=12, pad=6,
                     fill="#ffffff", stroke=COLOR_SUPER, sw=1.2)[0])
    
    f.append(line(W / 2, 115, W / 2, 410, color="#d5dbdb", sw=1.2, dash="4,4"))
    
    render(os.path.join(IMG, 'hugoniot-relation.svg'), W, H, *f)

# ── Фігура 3: Режими роботи сопла за протитиском ───────────────────────────────
def fig_nozzle_regimes():
    W, H = 960, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Режими витікання газу із сопла Лаваля залежно від протитиску P_amb", size=16, bold=True))
    
    boxes = [
        (60, 60, 410, 210, "1. Дозвуковий режим (P_amb занадто високий)",
         COLOR_SUB, "Газ не досягає M=1 у горловині. Сопло працює як труба Вентурі.", "M < 1 усюди"),
        (490, 60, 410, 210, "2. Перерозширений зі скачком усередині",
         COLOR_SHOCK, "У дифузорі виникає прямий скачок ущільнення. Потік за ним дозвуковий.", "M > 1 -> Скачок -> M < 1"),
        (60, 300, 410, 210, "3. Розрахунковий режим (P_e = P_amb)",
         COLOR_SUPER, "Повне ізоентропійне розширення. Гладкий надзвуковий струмінь на виході.", "M > 1 на виході (ідеальний)"),
        (490, 300, 410, 210, "4. Недорозширений режим (P_e > P_amb)",
         "#d35400", "Тиск на зрізі вищий за зовнішній. Розширення продовжується поза соплом.", "Віяло Прандтля-Майєра")
    ]
    
    for x, y, w, h, title_str, col, desc_str, tag_str in boxes:
        f.append(rect(x, y, w, h, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        f.append(text(x + 12, y + 24, title_str, size=13.5, bold=True, color=col, anchor="start"))
        
        cx_min = x + 30
        cy_mid = y + 100
        
        p_top = f"M {cx_min},{cy_mid-35} L {cx_min+60},{cy_mid-12} L {cx_min+200},{cy_mid-45}"
        p_bot = f"M {cx_min},{cy_mid+35} L {cx_min+60},{cy_mid+12} L {cx_min+200},{cy_mid+45}"
        f.append(path(p_top, fill="none", stroke=COLOR_WALL, sw=2))
        f.append(path(p_bot, fill="none", stroke=COLOR_WALL, sw=2))
        
        if "1. Дозвуковий" in title_str:
            f.append(arrow(cx_min+10, cy_mid, cx_min+180, cy_mid, color=COLOR_SUB, sw=2))
        elif "2. Перерозширений" in title_str:
            f.append(arrow(cx_min+10, cy_mid, cx_min+110, cy_mid, color=COLOR_SUPER, sw=2.5))
            f.append(line(cx_min+120, cy_mid-22, cx_min+120, cy_mid+22, color=COLOR_SHOCK, sw=3))
            f.append(arrow(cx_min+130, cy_mid, cx_min+195, cy_mid, color=COLOR_SUB, sw=1.8))
        elif "3. Розрахунковий" in title_str:
            f.append(arrow(cx_min+10, cy_mid, cx_min+190, cy_mid, color=COLOR_SUPER, sw=3.2))
            f.append(rect(cx_min+200, cy_mid-42, 120, 84, fill="#fdf2e9", stroke=COLOR_SUPER, sw=1, rx=0))
        elif "4. Недорозширений" in title_str:
            f.append(arrow(cx_min+10, cy_mid, cx_min+190, cy_mid, color=COLOR_SUPER, sw=3.2))
            f.append(line(cx_min+200, cy_mid-45, cx_min+280, cy_mid-60, color="#d35400", sw=2, dash="4,2"))
            f.append(line(cx_min+200, cy_mid+45, cx_min+280, cy_mid+60, color="#d35400", sw=2, dash="4,2"))
            
        f.append(text(x + 12, y + 175, desc_str, size=11.5, color=MUTED, anchor="start"))
        f.append(text(x + w - 12, y + 24, tag_str, size=11, bold=True, color=col, anchor="end"))

    render(os.path.join(IMG, 'nozzle-regimes.svg'), W, H, *f)

# ── Фігура 4: Залежність A / A* від M ──────────────────────────────────────────
def fig_area_mach_curve():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Залежність відношення площ A / A* від числа Маха M (γ = 1.4)", size=16, bold=True))
    
    ox, oy = 90, 400
    w_ax, h_ax = 700, 330
    
    f.append(line(ox, oy, ox + w_ax, oy, color="#7f8c8d", sw=1.5))
    f.append(line(ox, oy, ox, oy - h_ax, color="#7f8c8d", sw=1.5))
    f.append(text(ox + w_ax + 15, oy + 4, "M", size=14, bold=True, italic=True))
    f.append(text(ox - 15, oy - h_ax - 10, "A / A*", size=14, bold=True))
    
    for m_val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        x_pos = ox + (m_val / 3.2) * w_ax
        f.append(line(x_pos, oy, x_pos, oy - h_ax, color="#f0f3f4", sw=1))
        f.append(text(x_pos, oy + 20, f"{m_val:.1f}", size=12, color=MUTED))
        
    for a_val in [1.0, 2.0, 3.0, 4.0, 5.0]:
        y_pos = oy - ((a_val - 0.8) / 4.5) * h_ax
        f.append(line(ox, y_pos, ox + w_ax, y_pos, color="#f0f3f4", sw=1))
        f.append(text(ox - 25, y_pos + 4, f"{a_val:.1f}", size=12, color=MUTED))
        
    def area_ratio(m):
        if m < 0.01: return 100.0
        g = 1.4
        term = (2.0 / (g + 1.0)) * (1.0 + 0.5 * (g - 1.0) * m * m)
        exp = (g + 1.0) / (2.0 * (g - 1.0))
        return (1.0 / m) * (term ** exp)

    pts_sub = []
    pts_sup = []
    
    steps = 40
    for i in range(steps + 1):
        m = 0.15 + (1.0 - 0.15) * (i / steps)
        ar = area_ratio(m)
        if ar <= 5.2:
            px = ox + (m / 3.2) * w_ax
            py = oy - ((ar - 0.8) / 4.5) * h_ax
            pts_sub.append((px, py))
            
    for i in range(steps + 1):
        m = 1.0 + (3.1 - 1.0) * (i / steps)
        ar = area_ratio(m)
        if ar <= 5.2:
            px = ox + (m / 3.2) * w_ax
            py = oy - ((ar - 0.8) / 4.5) * h_ax
            pts_sup.append((px, py))

    path_sub_str = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_sub)
    path_sup_str = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_sup)
    
    f.append(path(path_sub_str, fill="none", stroke=COLOR_SUB, sw=3))
    f.append(path(path_sup_str, fill="none", stroke=COLOR_SUPER, sw=3))
    
    xm1 = ox + (1.0 / 3.2) * w_ax
    ym1 = oy - ((1.0 - 0.8) / 4.5) * h_ax
    f.append(circle(xm1, ym1, 6, fill=COLOR_SONIC, stroke="#ffffff", sw=2))
    
    # Зсуваємо рамку підпису праворуч і вгору від точки M=1, щоб лінія M=1 не розсікала текст
    f.append(textbox(xm1 + 150, ym1 - 40, "Критична точка M = 1 (A = A*)\nМінімум геометрії сопла", size=12, pad=6,
                     fill="#fef5e7", stroke=COLOR_SONIC, sw=1.2, color=COLOR_SONIC, bold=True)[0])

    f.append(text(ox + 100, oy - 220, "Дозвуковий розгін", size=13, bold=True, color=COLOR_SUB))
    f.append(text(ox + 440, oy - 220, "Надзвуковий розгін", size=13, bold=True, color=COLOR_SUPER))

    render(os.path.join(IMG, 'area-mach-curve.svg'), W, H, *f)

# ── Фігура 5: Прямий скачок ущільнення в дифузорі ─────────────────────────────
def fig_shock_wave_nozzle():
    W, H = 920, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    
    f.append(text(W / 2, 28, "Структура прямого скачка ущільнення у дифузорі сопла", size=16, bold=True))
    
    cy = 200
    p_top = f"M 100,{cy-40} L 820,{cy-140}"
    p_bot = f"M 100,{cy+40} L 820,{cy+140}"
    f.append(path(p_top, fill="none", stroke=COLOR_WALL, sw=3.5))
    f.append(path(p_bot, fill="none", stroke=COLOR_WALL, sw=3.5))
    
    xs = 460
    ys_top = cy - 90
    ys_bot = cy + 90
    
    poly_pre = [(100, cy-40), (xs, ys_top), (xs, ys_bot), (100, cy+40)]
    poly_post = [(xs, ys_top), (820, cy-140), (820, cy+140), (xs, ys_bot)]
    f.append(polygon(poly_pre, fill="#fdf2e9", stroke="none", sw=0))
    f.append(polygon(poly_post, fill="#ebf5fb", stroke="none", sw=0))
    
    f.append(line(xs, ys_top - 10, xs, ys_bot + 10, color=COLOR_SHOCK, sw=4.5))
    f.append(text(xs, ys_top - 22, "Скачок ущільнення", size=13, bold=True, color=COLOR_SHOCK))
    
    f.append(arrow(150, cy, 350, cy, color=COLOR_SUPER, sw=3.2))
    f.append(text(250, cy - 14, "M₁ > 1 (Надзвуковий)", size=13, bold=True, color=COLOR_SUPER))
    f.append(text(250, cy + 20, "Тиск P₁, Температура T₁", size=12, color=MUTED))
    
    f.append(arrow(530, cy, 700, cy, color=COLOR_SUB, sw=2.2))
    f.append(text(615, cy - 14, "M₂ < 1 (Дозвуковий)", size=13, bold=True, color=COLOR_SUB))
    f.append(text(615, cy + 20, "Тиск P₂ > P₁, Температура T₂ > T₁", size=12, color=MUTED))
    
    box_info, _, _ = textbox(W / 2, 380,
                             "Стрибок параметрів на скачку (Ренкін — Гюгоньо):\n"
                             "• Число Маха падає: M₂ < 1   • Статичний тиск стрибає: P₂ > P₁\n"
                             "• Повний тиск втрачається: P₀₂ < P₀₁   • Ентропія зростає: ΔS > 0",
                             size=12.5, pad=10, fill="#ffffff", stroke=COLOR_SHOCK, sw=1.5)
    f.append(box_info)
    
    render(os.path.join(IMG, 'shock-wave-nozzle.svg'), W, H, *f)

if __name__ == '__main__':
    fig_nozzle_geometry()
    fig_hugoniot_relation()
    fig_nozzle_regimes()
    fig_area_mach_curve()
    fig_shock_wave_nozzle()
    print("Успішно згенеровано 5 фігур у ./img/")
