# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. back-emf-mechanism.svg ────────────────────────────────────────────────
def fig_back_emf_mechanism():
    W, H = 840, 360
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1, rx=0))

    # Ліва панель: Фізика індукції в котушці
    p.append(rect(20, 20, 245, 320, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(142, 45, "Фізика: обертання магніту", size=13, color=INK, bold=True))
    
    # Ротор з полюсами N / S
    cx, cy = 142, 125
    p.append(circle(cx, cy, 46, fill="#ffffff", stroke=LINE, sw=1.8))
    # N полюс (червоний)
    p.append(rect(cx - 36, cy - 36, 72, 36, fill="#ffdddd", stroke=POS, sw=1.5, rx=4))
    p.append(text(cx, cy - 14, "N (магніт)", size=12, color=POS, bold=True))
    # S полюс (синій)
    p.append(rect(cx - 36, cy, 72, 36, fill="#dce6f8", stroke=NEG, sw=1.5, rx=4))
    p.append(text(cx, cy + 22, "S (магніт)", size=12, color=NEG, bold=True))
    
    # Стрілка обертання omega
    p.append(arrow(cx + 42, cy - 25, cx + 42, cy + 25, color=FIELD, sw=2))
    p.append(text(cx + 56, cy + 5, "ω", size=15, color=FIELD, bold=True))

    # Котушка статора поруч
    p.append(rect(35, 185, 215, 38, fill="#ffffff", stroke="#caa24a", sw=1.6, rx=4))
    p.append(text(142, 202, "Обмотка статора (котушка)", size=11, color="#856404", bold=True))
    p.append(text(142, 216, "Зміна потоку: dΦ/dt", size=10, color=MUTED))

    # Виведена протиЕРС
    p.append(line(45, 235, 240, 235, color=MUTED, sw=1, dash="3,3"))
    p.append(text(142, 255, "Генерація протиЕРС:", size=11, color=INK, bold=True))
    p.append(text(142, 275, "E = ke · ω  (протидіє струму)", size=12, color=POS, bold=True))
    p.append(text(142, 305, "Закон Фарадея + Ленца", size=10, color=MUTED, italic=True))

    # Центральна панель: Еквівалентна електрична схема
    p.append(rect(280, 20, 265, 320, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(412, 45, "Еквівалентна схема фази", size=13, color=INK, bold=True))

    # Джерело напруги V_app
    p.append(circle(325, 110, 18, fill="#ffffff", stroke=POS, sw=1.8))
    p.append(text(325, 114, "V", size=13, color=POS, bold=True))
    p.append(text(325, 78, "+ Живлення", size=10, color=POS))
    
    # Провідник від V
    p.append(line(343, 110, 365, 110, color=LINE, sw=1.8))
    p.append(arrow(345, 102, 362, 102, color=POS, sw=1.5))
    p.append(text(355, 95, "I", size=11, color=POS, bold=True))

    # Резистор R (активний опір)
    p.append(rect(365, 100, 32, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(381, 114, "R", size=11, color=INK, bold=True))
    p.append(text(381, 88, "Опір", size=9, color=MUTED))

    p.append(line(397, 110, 415, 110, color=LINE, sw=1.8))

    # Індуктивність L
    p.append(rect(415, 102, 34, 16, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(432, 114, "L", size=11, color=FIELD, bold=True))
    p.append(text(432, 88, "L di/dt", size=9, color=MUTED))

    p.append(line(449, 110, 470, 110, color=LINE, sw=1.8))

    # Генератор протиЕРС E (полярність назустріч V)
    p.append(circle(488, 110, 18, fill="#fff2e6", stroke=POS, sw=1.8))
    p.append(text(488, 114, "E", size=13, color=POS, bold=True))
    p.append(text(488, 78, "ПротиЕРС", size=10, color=POS))

    # Стрілка протидії
    p.append(arrow(500, 138, 475, 138, color=POS, sw=1.5))
    p.append(text(488, 153, "назустріч V", size=9, color=POS))

    # Провід до землі
    p.append(line(506, 110, 525, 110, color=LINE, sw=1.8))
    p.append(line(525, 110, 525, 175, color=LINE, sw=1.8))
    p.append(line(525, 175, 325, 175, color=LINE, sw=1.8))
    p.append(line(325, 175, 325, 128, color=LINE, sw=1.8))

    # Рівняння Кірхгофа
    p.append(rect(295, 200, 235, 120, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(412, 222, "Рівняння рівноваги напруг:", size=11, color=INK, bold=True))
    p.append(text(412, 248, "V = I·R + L·(dI/dt) + E", size=12, color=INK, bold=True))
    p.append(text(412, 275, "В усталеному стані (dI/dt = 0):", size=10, color=MUTED))
    p.append(text(412, 300, "I = (V − E) / R = (V − ke·ω) / R", size=11, color=FIELD, bold=True))

    # Права панель: Три робочі режими
    p.append(rect(560, 20, 260, 320, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(690, 45, "3 режими роботи мотора", size=13, color=INK, bold=True))

    # Режим 1: Пуск / Заклинювання
    p.append(rect(570, 65, 240, 75, fill="#fff0f0", stroke=POS, sw=1.2, rx=4))
    p.append(text(690, 82, "1. Заклинювання / Пуск (ω = 0)", size=11, color=POS, bold=True))
    p.append(text(690, 99, "E = 0  →  I_stall = V / R  (максимум)", size=10, color=INK, bold=True))
    p.append(text(690, 116, "Струм обмежений лише міддю → нагрів", size=9, color=MUTED))
    p.append(text(690, 131, "Момент максимальний: T = kt · I_stall", size=9, color=POS))

    # Режим 2: Холостий хід
    p.append(rect(570, 150, 240, 75, fill="#f0f9f0", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(690, 167, "2. Холостий хід (ω = ω_max)", size=11, color=FIELD, bold=True))
    p.append(text(690, 184, "E → V  →  I_0 = (V − E) / R ≈ 0", size=10, color=INK, bold=True))
    p.append(text(690, 201, "Струм покриває лише тертя у підшипниках", size=9, color=MUTED))
    p.append(text(690, 216, "Гранична швидкість: ω_0 ≈ V / ke", size=9, color=FIELD))

    # Режим 3: Рекуперація / Гальмування
    p.append(rect(570, 235, 240, 90, fill="#edf4ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(690, 252, "3. Генерація / Рекуперація", size=11, color=NEG, bold=True))
    p.append(text(690, 269, "E > V (привід крутить вал) → I < 0", size=10, color=INK, bold=True))
    p.append(text(690, 286, "Струм тече НАЗАД у шину живлення", size=9, color=NEG))
    p.append(text(690, 302, "Електричне гальмування вала", size=9, color=MUTED))
    p.append(text(690, 317, "Небезпека росту Vbus на ключах", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "back-emf-mechanism.svg"), W, H, *p)

# ── 2. back-emf-waveforms.svg ────────────────────────────────────────────────
def fig_back_emf_waveforms():
    W, H = 840, 350
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1, rx=0))

    # Лівий блок: Трапецеподібна протиЕРС (BLDC)
    p.append(rect(20, 20, 385, 310, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(212, 45, "BLDC: Трапецеподібна протиЕРС", size=13, color=INK, bold=True))
    p.append(text(212, 63, "Зосереджені обмотки + прямокутний потік", size=10, color=MUTED))

    # Осі координат для BLDC
    bx, by = 50, 140
    p.append(line(bx, by, bx + 330, by, color=MUTED, sw=1))
    p.append(line(bx, by - 60, bx, by + 60, color=MUTED, sw=1))
    p.append(text(bx + 335, by + 4, "θ_el", size=10, color=MUTED))
    p.append(text(bx - 10, by - 45, "+E", size=10, color=POS))
    p.append(text(bx - 10, by + 50, "−E", size=10, color=NEG))

    trap_pts = [
        (bx, by), (bx + 25, by - 45), (bx + 125, by - 45), (bx + 175, by + 45),
        (bx + 275, by + 45), (bx + 300, by)
    ]
    path_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in trap_pts)
    p.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    p.append(text(bx + 75, by - 52, "Плато 120° (+E)", size=10, color=POS, bold=True))
    p.append(text(bx + 225, by + 58, "Плато 120° (−E)", size=10, color=NEG, bold=True))

    # Струм блокової 120° комутації (прямокутний струм)
    curr_pts = [
        (bx, by), (bx + 25, by), (bx + 25, by - 30), (bx + 125, by - 30),
        (bx + 125, by), (bx + 175, by), (bx + 175, by + 30), (bx + 275, by + 30),
        (bx + 275, by), (bx + 300, by)
    ]
    curr_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in curr_pts)
    p.append(f'<path d="{curr_d}" fill="none" stroke="{FIELD}" stroke-width="1.8" stroke-dasharray="4,2"/>')
    p.append(text(bx + 155, by - 15, "Струм I (120°)", size=10, color=FIELD, bold=True))

    # Пояснення добутку P = E * I
    p.append(rect(35, 215, 355, 100, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(212, 233, "Узгодження: прямокутний струм у плато 120°", size=10, color=INK, bold=True))
    p.append(text(212, 252, "P(t) = E(t) · I(t) = E_max · I_max = const", size=11, color=FIELD, bold=True))
    p.append(text(212, 272, "Момент сталий під час перекриття струму і плато", size=9, color=MUTED))
    p.append(text(212, 290, "При живленні синусом: виникає пульсація моменту!", size=9, color=POS, bold=True))
    p.append(text(212, 305, "Керування: 6-крокова комутація (Trapezoidal ESC)", size=9, color=INK))

    # Правий блок: Синусоїдальна протиЕРС (PMSM)
    p.append(rect(435, 20, 385, 310, fill=FILL, stroke=MUTED, sw=1.2, rx=6))
    p.append(text(627, 45, "PMSM: Синусоїдальна протиЕРС", size=13, color=INK, bold=True))
    p.append(text(627, 63, "Розподілені обмотки + скос пазів (skewing)", size=10, color=MUTED))

    # Осі координат для PMSM
    sx, sy = 465, 140
    p.append(line(sx, sy, sx + 330, sy, color=MUTED, sw=1))
    p.append(line(sx, sy - 60, sx, sy + 60, color=MUTED, sw=1))
    p.append(text(sx + 335, sy + 4, "θ_el", size=10, color=MUTED))
    p.append(text(sx - 10, sy - 45, "+E", size=10, color=POS))
    p.append(text(sx - 10, sy + 50, "−E", size=10, color=NEG))

    # Графік чистої синусоїди
    sin_pts = []
    for deg in range(0, 301, 10):
        rad = math.radians(deg * (360.0 / 300.0))
        px_val = sx + deg
        py_val = sy - 45 * math.sin(rad)
        sin_pts.append((px_val, py_val))
    sin_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in sin_pts)
    p.append(f'<path d="{sin_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    p.append(text(sx + 75, sy - 52, "E(θ) = E_max·sin(θ)", size=10, color=POS, bold=True))

    # Графік синусоїдного струму (у фазі)
    sin_i_pts = []
    for deg in range(0, 301, 10):
        rad = math.radians(deg * (360.0 / 300.0))
        px_val = sx + deg
        py_val = sy - 30 * math.sin(rad)
        sin_i_pts.append((px_val, py_val))
    sin_i_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in sin_i_pts)
    p.append(f'<path d="{sin_i_d}" fill="none" stroke="{FIELD}" stroke-width="1.8" stroke-dasharray="4,2"/>')
    p.append(text(sx + 225, sy - 15, "I(θ) = I_max·sin(θ)", size=10, color=FIELD, bold=True))

    # Пояснення 3-фазного синусу P = sum(E_k * I_k)
    p.append(rect(450, 215, 355, 100, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(627, 233, "Узгодження: синусоїдний 3-фазний струм", size=10, color=INK, bold=True))
    p.append(text(627, 252, "Σ E_k(t)·I_k(t) = 1.5 · E_max · I_max = const", size=11, color=FIELD, bold=True))
    p.append(text(627, 272, "Ідеально гладкий хід без пульсацій моменту від 0 об/хв", size=9, color=MUTED))
    p.append(text(627, 290, "При живленні трапецією: виникає акустичний шум і гарчання", size=9, color=POS))
    p.append(text(627, 305, "Керування: FOC (Field-Oriented Control) або SVPWM", size=9, color=INK))

    render(os.path.join(OUT, "back-emf-waveforms.svg"), W, H, *p)

# ── 3. sensorless-zcd-timing.svg ─────────────────────────────────────────────
def fig_sensorless_zcd_timing():
    W, H = 840, 360
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1, rx=0))

    p.append(text(420, 25, "Хронограма 6-крокової комутації та детектування нуля (ZCD)", size=13, color=INK, bold=True))

    ox, oy = 70, 48
    sec_w = 115
    sectors = [("Крок 1 (0°..60°)", "U+, V-, W: Z"),
               ("Крок 2 (60°..120°)", "U+, W-, V: Z"),
               ("Крок 3 (120°..180°)", "V+, W-, U: Z"),
               ("Крок 4 (180°..240°)", "V+, U-, W: Z"),
               ("Крок 5 (240°..300°)", "W+, U-, V: Z"),
               ("Крок 6 (300°..360°)", "W+, V-, U: Z")]

    for i in range(7):
        p.append(line(ox + i * sec_w, oy, ox + i * sec_w, oy + 215, color="#d0d5dd", sw=1.2, dash="3,3"))
        if i < 6:
            p.append(text(ox + i * sec_w + sec_w / 2, oy + 15, sectors[i][0], size=10, color=INK, bold=True))
            p.append(text(ox + i * sec_w + sec_w / 2, oy + 28, sectors[i][1], size=9, color=MUTED))

    wy = oy + 115
    p.append(text(ox - 35, wy - 8, "Фаза W", size=11, color=INK, bold=True))
    p.append(text(ox - 35, wy + 8, "(напруга)", size=9, color=MUTED))

    # Осі рівнів напруги
    p.append(line(ox, wy - 45, ox + 6 * sec_w, wy - 45, color="#e5e7eb", sw=1))
    p.append(text(ox - 10, wy - 42, "Vbus", size=9, color=POS))
    p.append(line(ox, wy, ox + 6 * sec_w, wy, color="#cbd5e1", sw=1.2))
    p.append(text(ox - 10, wy + 3, "Vbus/2", size=9, color=FIELD, bold=True))
    p.append(line(ox, wy + 45, ox + 6 * sec_w, wy + 45, color="#e5e7eb", sw=1))
    p.append(text(ox - 10, wy + 48, "GND", size=9, color=NEG))

    w_pts = [
        (ox, wy + 55),
        (ox + 18, wy + 55),
        (ox + 25, wy + 35),
        (ox + sec_w/2, wy),
        (ox + sec_w, wy - 35),
        (ox + sec_w, wy + 45),
        (ox + 2*sec_w, wy + 45),
        (ox + 3*sec_w, wy + 45),
        (ox + 3*sec_w, wy - 55),
        (ox + 3*sec_w + 18, wy - 55),
        (ox + 3*sec_w + 25, wy - 35),
        (ox + 3.5*sec_w, wy),
        (ox + 4*sec_w, wy + 35),
        (ox + 4*sec_w, wy - 45),
        (ox + 5*sec_w, wy - 45),
        (ox + 6*sec_w, wy - 45)
    ]
    w_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in w_pts)
    p.append(f'<path d="{w_path}" fill="none" stroke="{POS}" stroke-width="2.2"/>')

    # Підсвітка вікна маскування (Blanking Window)
    p.append(rect(ox, wy + 20, 22, 45, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    p.append(text(ox + 38, wy + 62, "Викид L·di/dt (маскується)", size=9, color=POS, bold=True, anchor="start"))

    # Точка ZCD
    zcd_x = ox + sec_w / 2
    p.append(circle(zcd_x, wy, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(line(zcd_x, wy, zcd_x, wy - 26, color=FIELD, sw=1.5))
    p.append(rect(zcd_x - 48, wy - 42, 96, 16, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(zcd_x, wy - 30, "ZCD подія (30°)", size=9, color=FIELD, bold=True))

    # Затримка 30° до наступної комутації
    p.append(line(zcd_x, wy + 15, ox + sec_w, wy + 15, color=LINE, sw=1.5))
    p.append(arrow(zcd_x, wy + 15, ox + sec_w, wy + 15, color=LINE, sw=1.5))
    p.append(text(zcd_x + sec_w / 4, wy + 28, "Затримка 30°", size=9, color=INK, bold=True))
    p.append(text(zcd_x + sec_w / 4, wy + 40, "t_delay = t_sector / 2", size=9, color=MUTED))

    # Нижня плашка: Сліпий старт мотора
    p.append(rect(ox, 270, 6 * sec_w, 75, fill=FILL, stroke=MUTED, sw=1.2, rx=4))
    p.append(text(420, 288, "Алгоритм безсенсорного запуску (коли при ω = 0 протиЕРС відсутня):", size=11, color=INK, bold=True))
    
    # 3 фази старту
    p.append(rect(ox + 10, 298, 210, 40, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    p.append(text(ox + 115, 312, "1. Вирівнювання (Alignment)", size=10, color=INK, bold=True))
    p.append(text(ox + 115, 326, "DC-струм у фіксовані фази", size=9, color=MUTED))

    p.append(rect(ox + 240, 298, 210, 40, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    p.append(text(ox + 345, 312, "2. Розгін наосліп (Open-loop ramp)", size=10, color=INK, bold=True))
    p.append(text(ox + 345, 326, "Примусове крутіння поля з розгоном", size=9, color=MUTED))

    p.append(rect(ox + 470, 298, 210, 40, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(ox + 575, 312, "3. Захоплення (Closed-loop ZCD)", size=10, color=FIELD, bold=True))
    p.append(text(ox + 575, 326, "Амплітуда E достатня → синхронізм", size=9, color=FIELD))

    render(os.path.join(OUT, "sensorless-zcd-timing.svg"), W, H, *p)

# ── 4. zcd-schematic-circuit.svg ─────────────────────────────────────────────
def fig_zcd_schematic_circuit():
    W, H = 860, 360
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke=MUTED, sw=1, rx=0))

    p.append(text(430, 25, "Схемотехніка безсенсорного детектування: дільники, віртуальна нейтраль та RC-фільтр", size=13, color=INK, bold=True))

    in_x = 55
    phases = [("Фаза U", 80), ("Фаза V", 155), ("Фаза W", 230)]
    for name, y in phases:
        p.append(circle(in_x, y, 5, fill=POS, stroke=LINE, sw=1.2))
        p.append(text(in_x - 10, y + 4, name, size=10, color=INK, bold=True, anchor="end"))
        p.append(line(in_x + 5, y, in_x + 35, y, color=LINE, sw=1.8))

    # Дільники напруги (R_top = 39k, R_bot = 3.3k)
    div_x = in_x + 35
    for _, y in phases:
        # R_top
        p.append(rect(div_x, y - 8, 36, 16, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
        p.append(text(div_x + 18, y + 4, "39k", size=9, color=INK, bold=True))
        p.append(line(div_x + 36, y, div_x + 70, y, color=LINE, sw=1.8))
        
        # Вузол поділеної напруги
        node_x = div_x + 70
        p.append(circle(node_x, y, 3, fill=INK, stroke=INK, sw=1))
        
        # R_bot до GND
        p.append(line(node_x, y, node_x, y + 20, color=LINE, sw=1.5))
        p.append(rect(node_x - 8, y + 20, 16, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
        p.append(text(node_x, y + 34, "3.3k", size=9, color=INK, bold=True))
        p.append(line(node_x, y + 40, node_x, y + 48, color=LINE, sw=1.5))
        # GND
        p.append(line(node_x - 6, y + 48, node_x + 6, y + 48, color=MUTED, sw=1.5))
        p.append(line(node_x - 3, y + 51, node_x + 3, y + 51, color=MUTED, sw=1.2))

        # Провід далі до зірки
        p.append(line(node_x, y, node_x + 65, y, color=LINE, sw=1.8))

    p.append(text(div_x + 30, 48, "Дільники (12..48V → 0..3.3V)", size=10, color=POS, bold=True))

    # Схема віртуальної середньої точки (зірка з 3 резисторів 10k)
    star_x = div_x + 135
    p.append(rect(star_x - 10, 58, 120, 205, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=4))
    p.append(text(star_x + 50, 72, "Віртуальна нейтраль", size=10, color="#334155", bold=True))

    for _, y in phases:
        p.append(line(star_x - 20, y, star_x + 5, y, color=LINE, sw=1.5))
        p.append(rect(star_x + 5, y - 7, 28, 14, fill="#ffffff", stroke="#475569", sw=1.2, rx=2))
        p.append(text(star_x + 19, y + 4, "10k", size=9, color=INK))
        p.append(line(star_x + 33, y, star_x + 70, y, color=LINE, sw=1.5))

    # З'єднання в одну середню точку V_neut_div
    neut_join_x = star_x + 70
    p.append(line(neut_join_x, 80, neut_join_x, 230, color=LINE, sw=1.8))
    p.append(circle(neut_join_x, 155, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(neut_join_x, 155, neut_join_x + 40, 155, color=FIELD, sw=1.8))

    # RC-фільтрація (R_f = 1k, C_f = 2.2nF)
    filt_x = star_x + 130
    p.append(text(filt_x + 40, 48, "RC-фільтрація ШІМ (20..50 kHz)", size=10, color=FIELD, bold=True))

    # Фаза W (нижня) підходить до неінвертувального (+) входу
    p.append(line(star_x + 10, 230, filt_x, 230, color=LINE, sw=1.8))
    p.append(rect(filt_x, 222, 28, 16, fill="#ffffff", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(filt_x + 14, 234, "1k", size=9, color=INK, bold=True))
    p.append(line(filt_x + 28, 230, filt_x + 65, 230, color=LINE, sw=1.8))
    
    # C_f до GND
    cap_x = filt_x + 45
    p.append(circle(cap_x, 230, 2.5, fill=INK, stroke=INK, sw=1))
    p.append(line(cap_x, 230, cap_x, 248, color=LINE, sw=1.5))
    p.append(line(cap_x - 7, 248, cap_x + 7, 248, color=FIELD, sw=1.8))
    p.append(line(cap_x - 7, 252, cap_x + 7, 252, color=FIELD, sw=1.8))
    p.append(text(cap_x + 16, 253, "2.2nF", size=9, color=FIELD))
    p.append(line(cap_x, 252, cap_x, 262, color=MUTED, sw=1.2))
    p.append(line(cap_x - 5, 262, cap_x + 5, 262, color=MUTED, sw=1.2))

    # RC-фільтр нейтралі
    p.append(rect(filt_x, 147, 28, 16, fill="#ffffff", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(filt_x + 14, 159, "1k", size=9, color=INK, bold=True))
    p.append(line(filt_x + 28, 155, filt_x + 65, 155, color=FIELD, sw=1.8))
    # C_f нейтралі
    cap_n_x = filt_x + 45
    p.append(circle(cap_n_x, 155, 2.5, fill=INK, stroke=INK, sw=1))
    p.append(line(cap_n_x, 155, cap_n_x, 172, color=LINE, sw=1.5))
    p.append(line(cap_n_x - 7, 172, cap_n_x + 7, 172, color=FIELD, sw=1.8))
    p.append(line(cap_n_x - 7, 176, cap_n_x + 7, 176, color=FIELD, sw=1.8))
    p.append(line(cap_n_x, 176, cap_n_x, 185, color=MUTED, sw=1.2))
    p.append(line(cap_n_x - 5, 185, cap_n_x + 5, 185, color=MUTED, sw=1.2))

    # Аналоговий компаратор
    comp_x = filt_x + 95
    comp_y = 192
    comp_pts = [(comp_x, comp_y - 45), (comp_x + 55, comp_y), (comp_x, comp_y + 45)]
    comp_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in comp_pts) + " Z"
    p.append(f'<path d="{comp_d}" fill="#ffffff" stroke="{LINE}" stroke-width="1.8"/>')
    
    # Входи + та -
    p.append(line(filt_x + 65, 155, comp_x, 168, color=FIELD, sw=1.8))
    p.append(text(comp_x + 8, 173, "−", size=13, color=NEG, bold=True))

    p.append(line(filt_x + 65, 230, comp_x, 216, color=POS, sw=1.8))
    p.append(text(comp_x + 8, 221, "+", size=13, color=POS, bold=True))

    p.append(text(comp_x + 28, comp_y + 4, "CMP", size=10, color=INK, bold=True))

    # Вихід компаратора
    p.append(line(comp_x + 55, comp_y, comp_x + 105, comp_y, color=LINE, sw=1.8))
    p.append(arrow(comp_x + 55, comp_y, comp_x + 105, comp_y, color=LINE, sw=1.8))

    # Мікроконтролер
    mcu_x = comp_x + 110
    p.append(rect(mcu_x, 130, 110, 130, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(mcu_x + 55, 152, "Мікроконтролер", size=11, color=INK, bold=True))
    p.append(text(mcu_x + 55, 166, "(STM32 / ESP32)", size=9, color=MUTED))
    p.append(line(mcu_x + 10, 176, mcu_x + 100, 176, color=MUTED, sw=0.8))
    p.append(text(mcu_x + 55, 195, "EXTI / Timer Capture", size=9, color=FIELD, bold=True))
    p.append(text(mcu_x + 55, 212, "Переривання по ZCD", size=9, color=INK))
    p.append(text(mcu_x + 55, 228, "Таймер затримки 30°", size=9, color=POS, bold=True))
    p.append(text(mcu_x + 55, 244, "→ Наступний крок", size=9, color=MUTED))

    # Нижній попереджувальний блок про фазовий зсув
    p.append(rect(40, 295, 780, 50, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(430, 314, "Критична вимога: затримка RC-фільтра phi = arctan(f / f_cutoff) вносить фазовий зсув ZCD!", size=10, color="#b45309", bold=True))
    p.append(text(430, 332, "Частота зрізу f_c = 1 / (2*pi*R_eq*C) мусить бути в 5-10 разів вищою за електричну частоту мотора, або компенсуватися в коді.", size=9, color=INK))

    render(os.path.join(OUT, "zcd-schematic-circuit.svg"), W, H, *p)

if __name__ == "__main__":
    fig_back_emf_mechanism()
    fig_back_emf_waveforms()
    fig_sensorless_zcd_timing()
    fig_zcd_schematic_circuit()
    print("All figures generated successfully.")
