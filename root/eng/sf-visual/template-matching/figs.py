# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. metric-comparison: Чому сира кореляція тягнеться до відблиску, а ZNCC стійкий ──
def fig_metric_comparison():
    W, H = 900, 380
    p = []

    pw, ph = 265, 250
    y0 = 65

    # Панель 1: Сцена
    x1 = 20
    p.append(rect(x1, y0, pw, ph, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x1 + pw / 2, y0 - 14, "Сцена зі зміною освітлення", size=13, bold=True))
    
    # Шаблон у сцені (затінений хрестик / мітка)
    p.append(rect(x1 + 20, y0 + 35, 75, 75, fill="#f0f2f5", stroke=LINE, sw=1.2, rx=4))
    # Хрестик єдиним контуром path (без накладання прямокутників)
    cx0, cy0 = x1 + 57.5, y0 + 72.5
    w_arm, h_arm = 9.0, 24.0
    cross_path = (f"M {cx0 - w_arm:.1f} {cy0 - h_arm:.1f} "
                  f"H {cx0 + w_arm:.1f} V {cy0 - w_arm:.1f} "
                  f"H {cx0 + h_arm:.1f} V {cy0 + w_arm:.1f} "
                  f"H {cx0 + w_arm:.1f} V {cy0 + h_arm:.1f} "
                  f"H {cx0 - w_arm:.1f} V {cy0 + w_arm:.1f} "
                  f"H {cx0 - h_arm:.1f} V {cy0 - w_arm:.1f} "
                  f"H {cx0 - w_arm:.1f} Z")
    p.append(f'<path d="{cross_path}" fill="#4a5568" stroke="none"/>')
    p.append(text(x1 + 57, y0 + 130, "Ціль (α=0.5)", size=11, color=INK, bold=True))

    # Світлова пляма / відблиск праворуч
    p.append(rect(x1 + 140, y0 + 30, 95, 95, fill="#fff9db", stroke="#f59f00", sw=1.5, rx=47))
    p.append(circle(x1 + 187, y0 + 77, 28, fill="#ffe066", stroke="none"))
    p.append(circle(x1 + 187, y0 + 77, 10, fill="#ffffff", stroke="none"))
    p.append(text(x1 + 187, y0 + 140, "Яскравий відблиск", size=11, color=POS, bold=True))
    p.append(text(x1 + 187, y0 + 156, "(велика енергія)", size=10, color=MUTED))

    # Рамка шаблону окремо внизу панелі
    p.append(fitbox(x1 + 15, y0 + 180, pw - 30, 48, "Еталонний шаблон T\n(хрестоподібний маркер)", size=11, fill="#edf2f7", stroke=LINE, sw=1.2, bold=True))

    # Панель 2: Сира крос-кореляція CC = Σ I·T
    x2 = 315
    p.append(rect(x2, y0, pw, ph, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x2 + pw / 2, y0 - 14, "Сира крос-кореляція (CC)", size=13, bold=True))

    # Графік відгуку CC
    p.append(line(x2 + 25, y0 + ph - 55, x2 + pw - 20, y0 + ph - 55, color=LINE, sw=1.2)) # вісь X
    p.append(line(x2 + 25, y0 + 25, x2 + 25, y0 + ph - 55, color=LINE, sw=1.2))           # вісь Y
    p.append(text(x2 + 20, y0 + 20, "R_CC", size=10, color=MUTED, anchor="end"))
    
    # Крива відгуку
    curve_cc = [
        (x2 + 30, y0 + ph - 65), (x2 + 45, y0 + ph - 70),
        (x2 + 58, y0 + ph - 105), # справжня ціль
        (x2 + 75, y0 + ph - 70), (x2 + 115, y0 + ph - 60),
        (x2 + 155, y0 + ph - 120), (x2 + 187, y0 + ph - 185), # хибний максимум
        (x2 + 220, y0 + ph - 100), (x2 + 245, y0 + ph - 60)
    ]
    path_cc = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in curve_cc)
    p.append(f'<path d="{path_cc}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    p.append(circle(x2 + 187, y0 + ph - 185, 4, fill=POS, stroke="none"))
    p.append(text(x2 + 187, y0 + ph - 195, "Хибний максимум!", size=10, color=POS, bold=True))
    p.append(circle(x2 + 58, y0 + ph - 105, 3, fill=MUTED, stroke="none"))
    p.append(text(x2 + 58, y0 + ph - 115, "Ціль пропущено", size=9, color=MUTED))

    # Висновок під CC
    p.append(fitbox(x2 + 12, y0 + ph - 42, pw - 24, 30, "Σ I·T тягнеться до найбільшої яскравості", size=10, fill="#fdecea", stroke=POS, sw=1.0, color=POS, bold=True))

    # Панель 3: ZNCC
    x3 = 610
    p.append(rect(x3, y0, pw, ph, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x3 + pw / 2, y0 - 14, "Нормалізована ZNCC", size=13, bold=True))

    # Графік відгуку ZNCC
    p.append(line(x3 + 25, y0 + ph - 55, x3 + pw - 20, y0 + ph - 55, color=LINE, sw=1.2)) # вісь X
    p.append(line(x3 + 25, y0 + 25, x3 + 25, y0 + ph - 55, color=LINE, sw=1.2))           # вісь Y
    p.append(text(x3 + 20, y0 + 20, "R_ZNCC", size=10, color=MUTED, anchor="end"))
    
    # Крива відгуку ZNCC
    curve_zncc = [
        (x3 + 30, y0 + ph - 60), (x3 + 42, y0 + ph - 65),
        (x3 + 58, y0 + ph - 180), # чіткий максимум = 1.0
        (x3 + 75, y0 + ph - 65), (x3 + 115, y0 + ph - 58),
        (x3 + 155, y0 + ph - 60), (x3 + 187, y0 + ph - 62),
        (x3 + 220, y0 + ph - 58), (x3 + 245, y0 + ph - 56)
    ]
    path_zncc = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in curve_zncc)
    p.append(f'<path d="{path_zncc}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')
    p.append(circle(x3 + 58, y0 + ph - 180, 4, fill=FIELD, stroke="none"))
    p.append(text(x3 + 58, y0 + ph - 190, "Глобальний пік (+1.0)", size=10, color=FIELD, bold=True))
    p.append(text(x3 + 187, y0 + ph - 74, "Відблиск пригнічено (~0)", size=9, color=MUTED))

    # Висновок під ZNCC
    p.append(fitbox(x3 + 12, y0 + ph - 42, pw - 24, 30, "Центрування й нормування виділяють форму", size=10, fill="#eafaf0", stroke=FIELD, sw=1.0, color=FIELD, bold=True))

    render(os.path.join(OUT, "metric-comparison.svg"), W, H, *p,
           title="Порівняння метрик: уразливість сирої кореляції та стійкість ZNCC до засвічень")


# ── 2. ncc-vector-geometry: Геометричний зміст ZNCC у багатовимірному просторі ──
def fig_ncc_vector_geometry():
    W, H = 860, 390
    p = []

    bw, bh = 245, 280
    y0 = 60

    # Етап 1: Сирі вектори
    x1 = 20
    p.append(rect(x1, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x1 + bw / 2, y0 + 24, "1. Простір пікселів ℝᴰ", size=12, bold=True))
    
    # Осі координат
    ox1, oy1 = x1 + 40, y0 + bh - 55
    p.append(arrow(ox1, oy1, ox1 + 165, oy1, color=MUTED, sw=1.2))
    p.append(arrow(ox1, oy1, ox1, oy1 - 150, color=MUTED, sw=1.2))
    p.append(text(ox1 + 165, oy1 + 16, "p₁", size=10, color=MUTED))
    p.append(text(ox1 - 14, oy1 - 145, "p₂", size=10, color=MUTED))

    # Вектори
    p.append(arrow(ox1, oy1, ox1 + 80, oy1 - 60, color=LINE, sw=2.0))
    p.append(text(ox1 + 88, oy1 - 62, "T", size=11, bold=True))

    p.append(arrow(ox1, oy1, ox1 + 105, oy1 - 125, color=POS, sw=2.0))
    p.append(text(ox1 + 110, oy1 - 128, "I' = αI + β", size=11, color=POS, bold=True))

    p.append(arrow(ox1, oy1, ox1 + 60, oy1 - 70, color=NEG, sw=1.8))
    p.append(text(ox1 + 68, oy1 - 72, "I", size=11, color=NEG, bold=True))

    p.append(fitbox(x1 + 10, y0 + bh - 38, bw - 20, 26, "Зсув освітлення β зміщує вектор", size=10, fill="#f4f6f8", stroke=LINE, sw=1.0))

    # Стрілка переходу 1->2
    p.append(arrow(x1 + bw + 6, y0 + bh / 2, x1 + bw + 28, y0 + bh / 2, color=LINE, sw=1.6))

    # Етап 2: Центрування (віднімання середнього)
    x2 = 305
    p.append(rect(x2, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x2 + bw / 2, y0 + 24, "2. Центрування (Σ xᵢ = 0)", size=12, bold=True))

    ox2, oy2 = x2 + bw / 2, y0 + bh / 2 + 10
    # Площина нульового середнього
    p.append(line(ox2 - 95, oy2 + 75, ox2 + 95, oy2 - 75, color=FIELD, sw=2.0, dash="5 4"))
    p.append(text(ox2 + 45, oy2 - 82, "Гіперплощина Σxᵢ=0", size=9, color=FIELD, bold=True))

    # Вектори на площині
    p.append(arrow(ox2, oy2, ox2 + 70, oy2 - 55, color=POS, sw=2.2))
    p.append(text(ox2 + 76, oy2 - 58, "I'̃ = α·Ĩ", size=10, color=POS, bold=True))

    p.append(arrow(ox2, oy2, ox2 + 42, oy2 - 33, color=NEG, sw=2.0))
    p.append(text(ox2 + 45, oy2 - 20, "Ĩ", size=10, color=NEG, bold=True))

    p.append(arrow(ox2, oy2, ox2 - 55, oy2 - 60, color=LINE, sw=2.0))
    p.append(text(ox2 - 70, oy2 - 60, "T̃", size=10, bold=True))

    p.append(fitbox(x2 + 10, y0 + bh - 38, bw - 20, 26, "β зникає: I'̃ та Ĩ на одному промені", size=10, fill="#eafaf0", stroke=FIELD, sw=1.0, color=FIELD, bold=True))

    # Стрілка переходу 2->3
    p.append(arrow(x2 + bw + 6, y0 + bh / 2, x2 + bw + 28, y0 + bh / 2, color=LINE, sw=1.6))

    # Етап 3: Нормування на одиничну довжину
    x3 = 590
    p.append(rect(x3, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x3 + bw / 2, y0 + 24, "3. Сфера одиничного радіуса", size=12, bold=True))

    ox3, oy3 = x3 + bw / 2, y0 + bh / 2 + 10
    r_unit = 70
    p.append(f'<circle cx="{ox3:.1f}" cy="{oy3:.1f}" r="{r_unit:.1f}" fill="#f8fafc" stroke="{LINE}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    p.append(text(ox3 + r_unit + 6, oy3 + 4, "‖x‖ = 1", size=10, color=MUTED))

    # Нормовані вектори u_I та u_T
    p.append(arrow(ox3, oy3, ox3 + r_unit * 0.75, oy3 - r_unit * 0.66, color=FIELD, sw=2.5))
    p.append(text(ox3 + r_unit * 0.75 + 10, oy3 - r_unit * 0.66 - 4, "u_I' = u_I", size=10, color=FIELD, bold=True))

    p.append(arrow(ox3, oy3, ox3 - r_unit * 0.6, oy3 - r_unit * 0.8, color=LINE, sw=2.2))
    p.append(text(ox3 - r_unit * 0.6 - 18, oy3 - r_unit * 0.8 - 4, "u_T", size=10, bold=True))

    # Дуга кута θ
    p.append(text(ox3 + 6, oy3 - 35, "θ", size=11, color=POS, bold=True))
    p.append(fitbox(x3 + 10, y0 + bh - 38, bw - 20, 26, "ZNCC = cos(θ) = ⟨u_I, u_T⟩ ∈ [−1, 1]", size=10, fill="#eaf0fd", stroke=NEG, sw=1.0, color=NEG, bold=True))

    render(os.path.join(OUT, "ncc-vector-geometry.svg"), W, H, *p,
           title="Геометрична сутність ZNCC: центрування прибирає зміщення, нормування — масштаб")


# ── 3. integral-images-fast-ncc: Швидке обчислення локального середнього й дисперсії ──
def fig_integral_images():
    W, H = 840, 360
    p = []
    
    x1, y1 = 35, 65
    w1, h1 = 385, 260
    p.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x1 + w1 / 2, y1 - 12, "Інтегральна таблиця: сума вікна за O(1)", size=13, bold=True))

    # Сітка зображення
    p.append(rect(x1 + 25, y1 + 25, 335, 190, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
    
    # Прямокутне вікно запиту W
    wx, wy, ww, wh = x1 + 115, y1 + 75, 155, 95
    p.append(rect(wx, wy, ww, wh, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=2))
    p.append(text(wx + ww / 2, wy + wh / 2, "Вікно W (M × N)", size=12, color=FIELD, bold=True))

    # 4 кутові точки: A, B, C, D
    p.append(circle(wx, wy, 5, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(wx - 14, wy - 8, "A", size=12, color=POS, bold=True))

    p.append(circle(wx + ww, wy, 5, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(wx + ww + 14, wy - 8, "B", size=12, color=POS, bold=True))

    p.append(circle(wx, wy + wh, 5, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(wx - 14, wy + wh + 14, "C", size=12, color=POS, bold=True))

    p.append(circle(wx + ww, wy + wh, 5, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(wx + ww + 14, wy + wh + 14, "D", size=12, color=POS, bold=True))

    # Формула під сіткою
    p.append(fitbox(x1 + 15, y1 + h1 - 34, w1 - 30, 26, "Сума у вікні = S(D) − S(B) − S(C) + S(A)", size=10, fill="#edf2f7", stroke=LINE, sw=1.0, bold=True))

    # Права частина: Як рахується ZNCC локально
    x2, y2 = 445, 65
    w2, h2 = 360, 260
    p.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(x2 + w2 / 2, y2 - 12, "Дві таблиці для повного нормування", size=13, bold=True))

    # Блок 1: Таблиця першого порядку S(x,y)
    p.append(rect(x2 + 15, y2 + 20, w2 - 30, 62, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x2 + 25, y2 + 40, "Таблиця сум: S(x,y) = Σ I(u,v)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 25, y2 + 63, "→ Локальне середнє: Ī = Sum(S, W) / (M·N)", size=10, color=INK, anchor="start"))

    # Блок 2: Таблиця другого порядку S2(x,y)
    p.append(rect(x2 + 15, y2 + 92, w2 - 30, 62, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x2 + 25, y2 + 112, "Таблиця квадратів: S₂(x,y) = Σ I²(u,v)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(x2 + 25, y2 + 135, "→ Локальна енергія: Σ I² = Sum(S₂, W)", size=10, color=INK, anchor="start"))

    # Блок 3: Обчислення знаменника ZNCC
    p.append(rect(x2 + 15, y2 + 164, w2 - 30, 78, fill="#fdf2f8", stroke=POS, sw=1.2, rx=4))
    p.append(text(x2 + 25, y2 + 184, "Дисперсія патча за 8 звернень до пам'яті:", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(x2 + 25, y2 + 204, "σ_I = √[ Sum(S₂, W) − (Sum(S, W))² / (M·N) ]", size=10, color=INK, bold=True, anchor="start"))
    p.append(text(x2 + 25, y2 + 224, "Складність: O(1) незалежно від розміру шаблону!", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "integral-images-fast-ncc.svg"), W, H, *p,
           title="Інтегральні зображення: миттєве обчислення локального середнього та дисперсії")


# ── 4. pyramid-coarse-to-fine: Багаторівневий пірамідальний пошук ──
def fig_pyramid_search():
    W, H = 880, 420
    p = []

    # Верхній відступ від заголовка
    y_top = 65

    # Рівень L2: 1/4 розміру
    x1, y1 = 25, y_top + 35
    w1, h1 = 190, 140
    p.append(text(x1 + w1 / 2, y_top + 18, "Рівень 2 (1/4 шкали, 240×135 px)", size=11, bold=True))
    p.append(rect(x1, y1, w1, h1, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    
    # Сітка повного перебору
    p.append(rect(x1 + 8, y1 + 8, w1 - 16, h1 - 16, fill="#fee2e2", stroke=POS, sw=1.0))
    p.append(circle(x1 + 115, y1 + 70, 12, fill="none", stroke=POS, sw=2))
    p.append(circle(x1 + 115, y1 + 70, 3, fill=POS, stroke="none"))
    p.append(fitbox(x1 + 75, y1 + 92, 80, 24, "Пік (x₂, y₂)", size=9, fill="#ffffff", stroke=POS, sw=1.0, color=POS, bold=True))
    p.append(fitbox(x1, y1 + h1 + 18, w1, 48, "Повний перебір\n100% простору кадру", size=10, fill="#fdecea", stroke=POS, sw=1.0, color=POS, bold=True))

    # Стрілка масштабування ×2 на L1
    p.append(arrow(x1 + w1 + 8, y1 + h1 / 2, x1 + w1 + 45, y1 + h1 / 2, color=LINE, sw=1.8))
    p.append(text(x1 + w1 + 26, y1 + h1 / 2 - 10, "×2", size=11, bold=True))

    # Рівень L1: 1/2 розміру
    x2 = 295
    w2, h2 = 245, 175
    y2 = y_top + 25
    p.append(text(x2 + w2 / 2, y_top + 18, "Рівень 1 (1/2 шкали, 480×270 px)", size=11, bold=True))
    p.append(rect(x2, y2, w2, h2, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    
    # Центр кандидата (2*x2, 2*y2) і вузьке вікно пошуку ±δ
    cx2, cy2 = x2 + 145, y2 + 85
    p.append(rect(cx2 - 28, cy2 - 28, 56, 56, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=3))
    p.append(circle(cx2, cy2, 3, fill=MUTED, stroke="none"))
    p.append(circle(cx2 + 4, cy2 - 3, 4, fill=NEG, stroke="none"))
    p.append(fitbox(cx2 - 40, cy2 + 34, 80, 24, "Вікно ±δ (±4 px)", size=9, fill="#ffffff", stroke=NEG, sw=1.0, color=NEG, bold=True))
    p.append(fitbox(x2, y2 + h2 + 20, w2, 48, "Уточнення навколо 2·(x₂, y₂)\nПеревірка лише 81 позиції", size=10, fill="#eff6ff", stroke=NEG, sw=1.0, color=NEG, bold=True))

    # Стрілка масштабування ×2 на L0
    p.append(arrow(x2 + w2 + 8, y2 + h2 / 2, x2 + w2 + 45, y2 + h2 / 2, color=LINE, sw=1.8))
    p.append(text(x2 + w2 + 26, y2 + h2 / 2 - 10, "×2", size=11, bold=True))

    # Рівень L0: 1/1 оригінал
    x3 = 615
    w3, h3 = 240, 205
    y3 = y_top + 10
    p.append(text(x3 + w3 / 2, y_top + 18, "Рівень 0 (Оригінал 1:1, 960×540 px)", size=11, bold=True))
    p.append(rect(x3, y3, w3, h3, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
    
    # Вузьке вікно пошуку ±δ і субпіксельний максимум
    cx3, cy3 = x3 + 145, y3 + 105
    p.append(rect(cx3 - 20, cy3 - 20, 40, 40, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=2))
    p.append(circle(cx3 + 2, cy3 - 1, 4, fill=FIELD, stroke="none"))
    p.append(fitbox(cx3 - 42, cy3 + 26, 84, 24, "Точний пік (x*, y*)", size=9, fill="#ffffff", stroke=FIELD, sw=1.0, color=FIELD, bold=True))
    p.append(fitbox(x3, y3 + h3 + 20, w3, 48, "Фінальна локалізація\nСубпіксельна парабола", size=10, fill="#eafaf0", stroke=FIELD, sw=1.0, color=FIELD, bold=True))

    render(os.path.join(OUT, "pyramid-coarse-to-fine.svg"), W, H, *p,
           title="Пірамідальний пошук: звуження простору перебору від повного кадру до вузького вікна")


# ── 5. fft-phase-correlation: Конвеєр фазової кореляції через 2D FFT ──
def fig_fft_phase_correlation():
    W, H = 880, 320
    p = []

    bw, bh = 175, 200
    y0 = 65

    # Блок 1: Просторові зображення
    x1 = 20
    p.append(rect(x1, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x1 + bw / 2, y0 + 22, "1. Просторові кадри", size=11, bold=True))
    p.append(rect(x1 + 25, y0 + 45, 125, 75, fill="#f8fafc", stroke=LINE, sw=1.0, rx=3))
    p.append(rect(x1 + 60, y0 + 65, 30, 30, fill="#cbd5e1", stroke="none"))
    p.append(text(x1 + bw / 2, y0 + 135, "Зображення I(x,y)", size=10, bold=True))
    p.append(text(x1 + bw / 2, y0 + 155, "Шаблон T(x,y)", size=10, color=MUTED))
    p.append(fitbox(x1 + 10, y0 + bh - 32, bw - 20, 24, "Доповнення нулями", size=9, fill="#f1f5f9", stroke=LINE, sw=1.0))

    # Стрілка 1->2
    p.append(arrow(x1 + bw + 4, y0 + bh / 2, x1 + bw + 34, y0 + bh / 2, color=LINE, sw=1.6))
    p.append(text(x1 + bw + 19, y0 + bh / 2 - 10, "2D FFT", size=10, bold=True))

    # Блок 2: Спектри Фур'є
    x2 = 235
    p.append(rect(x2, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x2 + bw / 2, y0 + 22, "2. Частотний домен", size=11, bold=True))
    p.append(circle(x2 + bw / 2, y0 + 85, 35, fill="#fef3c7", stroke="#f59f00", sw=1.2))
    p.append(circle(x2 + bw / 2, y0 + 85, 12, fill="#f59f00", stroke="none"))
    p.append(text(x2 + bw / 2, y0 + 135, "Спектри F_I та F_T", size=10, bold=True))
    p.append(text(x2 + bw / 2, y0 + 155, "F_I = ℱ{I}, F_T = ℱ{T}", size=9, color=MUTED))
    p.append(fitbox(x2 + 10, y0 + bh - 32, bw - 20, 24, "Комплексні амплітуди", size=9, fill="#fef3c7", stroke="#f59f00", sw=1.0))

    # Стрілка 2->3
    p.append(arrow(x2 + bw + 4, y0 + bh / 2, x2 + bw + 34, y0 + bh / 2, color=LINE, sw=1.6))
    p.append(text(x2 + bw + 19, y0 + bh / 2 - 10, "R(u,v)", size=10, bold=True))

    # Блок 3: Фазовий крос-спектр
    x3 = 450
    p.append(rect(x3, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x3 + bw / 2, y0 + 22, "3. Фазовий спектр", size=11, bold=True))
    p.append(rect(x3 + 25, y0 + 45, 125, 75, fill="#eff6ff", stroke=NEG, sw=1.2, rx=3))
    p.append(text(x3 + bw / 2, y0 + 80, "F_I · F_T*", size=12, color=NEG, bold=True))
    p.append(line(x3 + 45, y0 + 87, x3 + bw - 45, y0 + 87, color=NEG, sw=1.5))
    p.append(text(x3 + bw / 2, y0 + 103, "|F_I · F_T*|", size=11, color=NEG, bold=True))
    p.append(text(x3 + bw / 2, y0 + 138, "Нормалізація амплітуд", size=9, bold=True))
    p.append(fitbox(x3 + 10, y0 + bh - 32, bw - 20, 24, "Залишається лише фаза", size=9, fill="#eff6ff", stroke=NEG, sw=1.0, color=NEG, bold=True))

    # Стрілка 3->4
    p.append(arrow(x3 + bw + 4, y0 + bh / 2, x3 + bw + 34, y0 + bh / 2, color=LINE, sw=1.6))
    p.append(text(x3 + bw + 19, y0 + bh / 2 - 10, "2D IFFT", size=10, bold=True))

    # Блок 4: Дельта-пік
    x4 = 665
    p.append(rect(x4, y0, bw, bh, fill="#ffffff", stroke=LINE, sw=1.4, rx=6))
    p.append(text(x4 + bw / 2, y0 + 22, "4. Просторовий відгук", size=11, bold=True))
    
    # 3D/2D дельта-пік на площині
    p.append(rect(x4 + 25, y0 + 45, 125, 75, fill="#f8fafc", stroke=FIELD, sw=1.2, rx=3))
    p.append(line(x4 + 35, y0 + 105, x4 + 140, y0 + 105, color=MUTED, sw=1.0))
    p.append(line(x4 + 85, y0 + 105, x4 + 85, y0 + 55, color=FIELD, sw=2.5)) # пік
    p.append(circle(x4 + 85, y0 + 55, 4, fill=FIELD, stroke="none"))
    p.append(text(x4 + 85, y0 + 48, "δ(x−Δx, y−Δy)", size=10, color=FIELD, bold=True))

    p.append(text(x4 + bw / 2, y0 + 138, "Ідеальний дельта-пік", size=10, color=FIELD, bold=True))
    p.append(fitbox(x4 + 10, y0 + bh - 32, bw - 20, 24, "Координати зсуву (Δx, Δy)", size=9, fill="#eafaf0", stroke=FIELD, sw=1.0, color=FIELD, bold=True))

    render(os.path.join(OUT, "fft-phase-correlation-pipeline.svg"), W, H, *p,
           title="Фазова кореляція: перехід у частотний домен зводить зсув до гострого імпульсу Дірака")


if __name__ == "__main__":
    fig_metric_comparison()
    fig_ncc_vector_geometry()
    fig_integral_images()
    fig_pyramid_search()
    fig_fft_phase_correlation()
    print("All figures generated successfully.")
