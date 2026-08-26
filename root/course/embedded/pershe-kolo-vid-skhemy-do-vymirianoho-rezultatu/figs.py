# -*- coding: utf-8 -*-
"""Фігури до теми «Перше коло від схеми до виміряного результату».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG

def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── 1. Наскрізний цикл інженерної верифікації ────────────────────────────────
def fig_validation_cycle():
    W, H = 820, 310
    f = []
    
    # 5 блоків у ланцюжку
    steps = [
        ("1. Розрахунок", "Теорія й номінали\nсхеми (папір/SPICE)", 90, 95),
        ("2. Макет", "Збірка на макетці:\nврахування паразитів", 240, 95),
        ("3. DC-режим", "Статична перевірка:\nструми й вузлові U", 390, 95),
        ("4. AC-динаміка", "Осцилограф: фронти,\nвикиди та дзвоніння", 540, 95),
        ("5. Декомпозиція", "Аналіз розбіжностей\nі корекція моделі", 690, 95),
    ]
    
    bw, bh = 125, 76
    for title, desc, cx, cy in steps:
        f.append(rect(cx - bw/2, cy - bh/2, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
        f.append(text(cx, cy - 18, title, size=13, color=INK, bold=True))
        f.append(mtext(cx, cy + 8, desc, size=11, color=MUTED, lh=1.25))

    # Прямі стрілки між кроками
    for i in range(len(steps) - 1):
        x1 = steps[i][2] + bw/2
        x2 = steps[i+1][2] - bw/2
        f.append(arrow(x1, 95, x2, 95, color=LINE, sw=1.8))
        
    # Зворотний зв'язок від кроку 5 до кроку 1 (петля калібрування)
    x_end = steps[4][2]
    x_start = steps[0][2]
    f.append(line(x_end, 95 + bh/2, x_end, 230, color=POS, sw=1.8))
    f.append(line(x_end, 230, x_start, 230, color=POS, sw=1.8))
    f.append(arrow(x_start, 230, x_start, 95 + bh/2 + 2, color=POS, sw=1.8))
    
    # Підпис на петлі зворотного зв'язку
    bx = fitbox(280, 214, 260, 32, "Ітеративне уточнення моделі й паразитів",
                size=12, fill="#fdecea", stroke=POS, color="#7a1d12", bold=True)
    f.append(bx)
    
    # Позначки категорій під блоками
    f.append(rect(30, 260, 220, 30, fill="#edf2f7", stroke="#cbd5e0", sw=1, rx=4))
    f.append(text(140, 280, "Етап 1: Теоретичний задум", size=11, color="#2d3748"))
    
    f.append(rect(290, 260, 360, 30, fill="#ebf8ff", stroke="#bee3f8", sw=1, rx=4))
    f.append(text(470, 280, "Етап 2: Фізичні вимірювання (DC + AC)", size=11, color="#2b6cb0"))
    
    f.append(rect(670, 260, 120, 30, fill="#f0fff4", stroke="#c6f6d5", sw=1, rx=4))
    f.append(text(730, 280, "Етап 3: Синтез", size=11, color="#276749"))

    render(os.path.join(IMG, "validation-cycle.svg"), W, H, *f,
           title="Повний наскрізний цикл розробки та валідації електричного вузла")


# ── 2. Паразитні параметри безпаєчної макетної плати ─────────────────────────
def fig_breadboard_parasitics():
    W, H = 800, 370
    f = []
    
    # Ліва частина: фізичний вигляд контактних рейок
    f.append(rect(40, 60, 330, 270, fill="#f7fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(205, 85, "Фізична будова контактів макетки", size=13, bold=True))
    
    # 3 контактні рейки (металеві пружинні смужки)
    for idx, x in enumerate([85, 170, 255]):
        f.append(rect(x, 110, 50, 190, fill="#edf2f7", stroke="#4a5568", sw=1.5, rx=4))
        f.append(text(x + 25, 130, "Рейка %d" % (idx + 1), size=11, color="#4a5568", bold=True))
        # гнізда-отвори
        for y in [150, 180, 210, 240, 270]:
            f.append(circle(x + 25, y, 7, fill="#ffffff", stroke="#2d3748", sw=1.2))
            
    # Паразитна ємність між сусідніми рейками
    f.append(line(135, 180, 170, 180, color=NEG, sw=1.8, dash="3 3"))
    f.append(text(152, 170, "Cp", size=11, color=NEG, bold=True))
    f.append(text(152, 195, "2–5 пФ", size=10, color=NEG))
    
    f.append(line(220, 240, 255, 240, color=NEG, sw=1.8, dash="3 3"))
    f.append(text(237, 230, "Cp", size=11, color=NEG, bold=True))
    f.append(text(237, 255, "2–5 пФ", size=10, color=NEG))

    # Права частина: еквівалентна електрична схема паразитів
    f.append(rect(400, 60, 360, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(580, 85, "Еквівалентна схема одного з'єднання", size=13, bold=True))
    
    # Вхідний і вихідний вузли
    f.append(circle(440, 160, 5, fill=INK, stroke=INK))
    f.append(text(440, 140, "Вузол A", size=11, bold=True))
    
    # Контактний опір 1
    f.append(line(440, 160, 470, 160, color=LINE, sw=2))
    f.append(rect(470, 150, 35, 20, fill="#fff", stroke=RED, sw=1.5))
    f.append(text(487, 140, "R_конт1", size=10, color=RED, bold=True))
    f.append(text(487, 185, "0.1–0.5 Ом", size=9, color=RED))
    
    # Індуктивність дроту-перемички
    f.append(line(505, 160, 535, 160, color=LINE, sw=2))
    # Спрощена котушка індуктивності
    f.append(line(535, 160, 580, 160, color=LINE, sw=2.5))
    f.append(text(557, 140, "L_провід", size=10, color="#d69e2e", bold=True))
    f.append(text(557, 185, "≈1 нГн/мм", size=9, color="#d69e2e"))
    
    # Контактний опір 2
    f.append(line(580, 160, 610, 160, color=LINE, sw=2))
    f.append(rect(610, 150, 35, 20, fill="#fff", stroke=RED, sw=1.5))
    f.append(text(627, 140, "R_конт2", size=10, color=RED, bold=True))
    f.append(text(627, 185, "0.1–0.5 Ом", size=9, color=RED))
    
    f.append(line(645, 160, 710, 160, color=LINE, sw=2))
    f.append(circle(710, 160, 5, fill=INK, stroke=INK))
    f.append(text(710, 140, "Вузол B", size=11, bold=True))
    
    # Паразитна ємність на землю та між шинами
    f.append(line(557, 160, 557, 220, color=NEG, sw=1.5))
    f.append(line(545, 220, 570, 220, color=NEG, sw=2.5))
    f.append(line(545, 228, 570, 228, color=NEG, sw=2.5))
    f.append(line(557, 228, 557, 265, color=NEG, sw=1.5))
    
    # Земля
    f.append(line(545, 265, 570, 265, color=LINE, sw=2))
    f.append(line(550, 270, 565, 270, color=LINE, sw=1.5))
    f.append(line(554, 275, 561, 275, color=LINE, sw=1.2))
    f.append(text(620, 225, "C_паразитна\n(2–5 пФ)", size=10, color=NEG, bold=True))
    
    # Пояснювальний блок унизу
    f.append(rect(400, 300, 360, 24, fill="#fff5f5", stroke="#feb2b2", sw=1, rx=4))
    f.append(text(580, 316, "Складає паразитичний RLC-фільтр низьких частот", size=10, color=RED, bold=True))

    render(os.path.join(IMG, "breadboard-parasitics.svg"), W, H, *f,
           title="Паразитні опори, ємності та індуктивності контактних груп макетки")


# ── 3. Ефект навантаження досліджуваного кола вольтметром (DC Loading) ───────
def fig_dc_loading_effect():
    W, H = 820, 320
    f = []
    
    # Ліворуч: ідеальна схема дільника
    f.append(rect(30, 55, 340, 245, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(200, 80, "Високоомний дільник (Теорія vs Реальність)", size=12, bold=True))
    
    # Джерело 5В
    f.append(line(70, 110, 70, 250, color=LINE, sw=1.8))
    f.append(circle(70, 180, 16, fill="#ffffff", stroke=POS, sw=2))
    f.append(text(70, 185, "5 В", size=11, color=POS, bold=True))
    
    # R1 = 1 МОм
    f.append(line(70, 110, 140, 110, color=LINE, sw=1.8))
    f.append(rect(140, 100, 45, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(162, 92, "R1 = 1.0 MΩ", size=10, bold=True))
    
    # Вузол V_out
    f.append(line(185, 110, 240, 110, color=LINE, sw=1.8))
    f.append(circle(240, 110, 4, fill=INK, stroke=INK))
    f.append(text(240, 95, "V_out", size=11, bold=True))
    
    # R2 = 1 МОм
    f.append(line(240, 110, 240, 150, color=LINE, sw=1.8))
    f.append(rect(230, 150, 20, 45, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(275, 175, "R2 = 1.0 MΩ", size=10, bold=True))
    f.append(line(240, 195, 240, 250, color=LINE, sw=1.8))
    
    # Замикання землі
    f.append(line(70, 250, 320, 250, color=LINE, sw=1.8))
    
    # Підключений вольтметр із вхідним опором Rm
    f.append(line(240, 110, 320, 110, color=NEG, sw=1.5, dash="3 3"))
    f.append(rect(300, 145, 40, 50, fill="#ebf8ff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(320, 168, "V", size=13, color=NEG, bold=True))
    f.append(text(320, 185, "R_m", size=10, color=NEG))
    f.append(line(320, 195, 320, 250, color=NEG, sw=1.5, dash="3 3"))

    # Теоретичний розрахунок врізка
    f.append(rect(45, 215, 175, 30, fill="#f0fff4", stroke="#9ae6b4", sw=1, rx=4))
    f.append(text(132, 234, "Без приладу: V_out = 2.50 В", size=10, color="#22543d", bold=True))

    # Праворуч: таблиця-порівняння впливу різних приладів
    f.append(rect(390, 55, 400, 245, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    f.append(text(590, 80, "Виміряна напруга залежно від вхідного опору приладу", size=12, bold=True))
    
    # Рядки таблиці
    rows = [
        ("Дешевий мультиметр", "R_m = 1.0 MΩ", "1.67 В", "−33.3%", "#e53e3e"),
        ("Стандартний DMM (10M)", "R_m = 10 MΩ", "2.38 В", "−4.8%", "#dd6b20"),
        ("Прецизійний DMM", "R_m = 100 MΩ", "2.49 В", "−0.4%", "#3182ce"),
        ("Електрометр / FET-щуп", "R_m > 10 GΩ", "2.50 В", "< 0.01%", "#38a169"),
    ]
    
    # Шапка таблиці
    f.append(rect(405, 100, 370, 26, fill="#edf2f7", stroke="#cbd5e0", sw=1, rx=3))
    f.append(text(465, 117, "Прилад / Клас", size=10, color="#4a5568", bold=True))
    f.append(text(555, 117, "Опір R_m", size=10, color="#4a5568", bold=True))
    f.append(text(635, 117, "Показ", size=10, color="#4a5568", bold=True))
    f.append(text(715, 117, "Похибка", size=10, color="#4a5568", bold=True))
    
    y_start = 140
    for title, rm, v_meas, err, col in rows:
        f.append(text(465, y_start, title, size=10, anchor="middle"))
        f.append(text(555, y_start, rm, size=10, anchor="middle", bold=True))
        f.append(text(635, y_start, v_meas, size=10, anchor="middle", bold=True))
        f.append(text(715, y_start, err, size=10, color=col, anchor="middle", bold=True))
        f.append(line(405, y_start + 8, 775, y_start + 8, color="#e2e8f0", sw=1))
        y_start += 32
        
    f.append(rect(405, 262, 370, 26, fill="#fefcbf", stroke="#d69e2e", sw=1, rx=4))
    f.append(text(590, 279, "Формула Тевеніна: V_вим = V_тх · R_m / (R_th + R_m)", size=10, color="#744210", bold=True))

    render(os.path.join(IMG, "dc-loading-effect.svg"), W, H, *f,
           title="Ефект навантаження досліджуваного кола внутрішнім опором вольтметра")


# ── 4. Динамічні спотворення осцилографічного щупа: дзвоніння та фронти ──────
def fig_ac_probe_ringing():
    W, H = 820, 360
    f = []
    
    x0, y0 = 80, 280
    xr, yt = 760, 60
    
    # Координатні осі
    f.append(arrow(x0, y0, xr, y0, color=INK, sw=1.8))  # час
    f.append(arrow(x0, y0, x0, yt, color=INK, sw=1.8))  # напруга
    f.append(text(xr - 20, y0 + 20, "Час (t)  →", size=11, color=INK))
    f.append(text(x0 - 25, yt + 10, "U(t)", size=12, color=INK, bold=True))
    
    # Рівень логічної «1» (3.3 В) та «0» (0 В)
    v1_y = 130
    f.append(line(x0, v1_y, xr - 40, v1_y, color=MUTED, sw=1, dash="4 4"))
    f.append(text(x0 - 25, v1_y + 4, "3.3 В", size=11, color=MUTED))
    f.append(text(x0 - 25, y0 + 4, "0.0 В", size=11, color=MUTED))
    
    # 1. Ідеальний сигнал (чистий вхідний імпульс)
    pts_ideal = [
        (x0 + 20, y0),
        (x0 + 80, y0),
        (x0 + 85, v1_y),
        (xr - 50, v1_y)
    ]
    f.append(polyline(pts_ideal, color="#a0aec0", sw=1.6, dash="3 3"))
    f.append(text(210, v1_y - 12, "Ідеальний вхідний сигнал (tr = 2 нс)", size=10, color="#718096"))

    # 2. Правильне вимірювання (короткий пружинний контакт заземлення Ground Spring)
    # Швидкий плавний фронт без дзвону
    pts_good = [(x0 + 20, y0), (x0 + 80, y0)]
    for i in range(1, 40):
        t = i / 39.0
        x = x0 + 80 + t * 45
        y = y0 - (y0 - v1_y) * (1 / (1 + math.exp(- (t - 0.4) * 10)))
        pts_good.append((x, y))
    pts_good.append((xr - 50, v1_y))
    f.append(polyline(pts_good, color=FIELD, sw=2.4))
    f.append(text(340, v1_y - 25, "Короткий контакт (Ground Spring): чистий фронт", size=11, color=FIELD, bold=True))

    # 3. Вимірювання з довгим крокодилом заземлення (15 см дріт = 150 нГн L_loop + 15 пФ C_probe)
    # Збуджується паразитичний LC-дзвін з перерегулюванням
    pts_bad = [(x0 + 20, y0), (x0 + 80, y0)]
    for i in range(1, 140):
        t = i / 139.0
        x = x0 + 80 + t * 400
        # Затухаюча синусоїда
        damping = math.exp(-t * 4.5)
        osc = math.sin(t * 35.0)
        # S-подібний підйом + накладене коливання
        base = 1.0 / (1.0 + math.exp(- (t * 6.0 - 1.5)))
        val = base - 0.42 * damping * osc if t > 0.05 else 0.0
        y = y0 - (y0 - v1_y) * val
        pts_bad.append((x, y))
    pts_bad.append((xr - 50, v1_y))
    f.append(polyline(pts_bad, color=RED, sw=2.4))
    
    # Анотації: Перерегулювання (Overshoot)
    peak_x = x0 + 80 + 32
    peak_y = v1_y - 42
    f.append(arrow(peak_x + 50, peak_y - 10, peak_x + 4, peak_y + 4, color=RED, sw=1.5))
    f.append(text(peak_x + 130, peak_y - 12, "Перерегулювання (Overshoot +68%)", size=10, color=RED, bold=True))
    
    # Анотації: Дзвоніння (Ringing)
    ring_x = x0 + 80 + 130
    ring_y = v1_y + 25
    f.append(line(ring_x, ring_y - 20, ring_x, ring_y + 35, color=RED, sw=1, dash="2 2"))
    f.append(text(ring_x + 75, ring_y + 38, "Паразитний дзвін f_рез ≈ 103 МГц", size=10, color=RED))

    # Легенда унизу
    f.append(rect(60, 305, 700, 42, fill="#f7fafc", stroke="#cbd5e0", sw=1, rx=6))
    f.append(line(80, 326, 110, 326, color=FIELD, sw=2.5))
    f.append(text(210, 330, "Щуп 10X з пружиною (L_loop ≈ 5 нГн)", size=10, bold=True))
    
    f.append(line(350, 326, 380, 326, color=RED, sw=2.5))
    f.append(text(530, 330, "Щуп 10X з довгим крокодилом 15 см (L_loop ≈ 150 нГн)", size=10, color=RED, bold=True))

    render(os.path.join(IMG, "ac-probe-ringing.svg"), W, H, *f,
           title="Вплив індуктивності петлі заземлення щупа на форму крутого фронту")


if __name__ == "__main__":
    fig_validation_cycle()
    fig_breadboard_parasitics()
    fig_dc_loading_effect()
    fig_ac_probe_ringing()
    print("All figures generated successfully.")
