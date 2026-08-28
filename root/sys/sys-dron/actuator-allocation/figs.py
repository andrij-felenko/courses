#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми actuator-allocation.
Вивід у ./img/
"""

import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_allocation_pipeline():
    """Фігура 1: Конвеєр розподілу керування — від віртуальних сил до приводів."""
    w, h = 820, 260
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Блок 1: Регулятори орієнтації та висоти
    b1, _, _ = textbox(110, 110, "Контури керування\n(PID орієнтації й висоти)\nτ = [F_z, M_x, M_y, M_z]ᵀ", 
                       size=12, pad=10, fill=FILL, stroke=LINE, min_w=170)
    elements.append(b1)
    
    # Стрілка 1 -> 2
    elements.append(arrow(195, 110, 245, 110, color=LINE, sw=1.8))
    elements.append(text(220, 95, "τ_des", size=11, color=INK, bold=True))
    
    # Блок 2: Контрол-алокатор (розподіл)
    b2_body = rect(250, 40, 290, 160, fill="#edf2f7", stroke=LINE, sw=1.8, rx=8)
    elements.append(b2_body)
    elements.append(text(395, 65, "Control Allocation (Алокатор)", size=13, color=INK, bold=True))
    
    # Підблоки всередині алокатора (без вкладених rect-рамок щоб уникнути конфліктів)
    elements.append(text(395, 100, "Псевдообернена матриця: u_raw = B⁺ · τ", size=11, color=INK, bold=True))
    elements.append(arrow(395, 112, 395, 130, color=MUTED, sw=1.4))
    elements.append(text(395, 150, "Пріоритетна десатурація та межі", size=11, color="#b45309", bold=True))
    elements.append(text(395, 170, "u = SaturationHandler(u_raw)", size=11, color="#b45309"))
    
    # Стрілка 2 -> 3
    elements.append(arrow(540, 110, 595, 110, color=LINE, sw=1.8))
    elements.append(text(567, 95, "u ∈ [0, 1]", size=11, color=INK, bold=True))
    
    # Блок 3: Виконавчі приводи
    b3_body = rect(600, 35, 200, 170, fill=FILL, stroke=LINE, sw=1.5, rx=8)
    elements.append(b3_body)
    elements.append(text(700, 60, "Фізичні приводи", size=12, color=INK, bold=True))
    
    # Рядки приводів
    elements.append(text(700, 95, "ESC / Мотори 1..m (тяга F_i)", size=11, color=INK))
    elements.append(text(700, 130, "Сервоприводи (рулі δ_i)", size=11, color=INK))
    elements.append(text(700, 165, "Поворотні балки (векторизація)", size=11, color=MUTED))
    
    # Пояснення знизу
    elements.append(text(410, 235, "Віртуальне керування τ (сили/моменти) транслюється через геометрію рами B у фізичні сигнали u", 
                         size=12, color=MUTED, italic=True))
    
    # Збірка SVG
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'allocation-pipeline.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_geometry_to_matrix():
    """Фігура 2: Зв'язок фізичної геометрії ротора та стовпчика матриці B."""
    w, h = 820, 320
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Ліва частина: Схема ротора в просторі
    elements.append(rect(20, 20, 360, 275, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(200, 48, "Фізична модель ротора i", size=13, color=INK, bold=True))
    
    # Центр мас
    elements.append(circle(90, 180, 7, fill=LINE, stroke=LINE))
    elements.append(text(90, 205, "Центр мас (0,0,0)", size=11, color=INK))
    
    # Вектор позиції r_i
    elements.append(arrow(90, 180, 260, 110, color=NEG, sw=2))
    elements.append(text(150, 130, "Плече r_i = [x_i, y_i, z_i]ᵀ", size=11, color=NEG, bold=True))
    
    # Ротор i
    elements.append(circle(260, 110, 16, fill="#fee2e2", stroke=POS, sw=2))
    elements.append(text(260, 114, "M_i", size=11, color=POS, bold=True))
    
    # Вектор тяги F_i
    elements.append(arrow(260, 94, 260, 40, color=POS, sw=2.2))
    elements.append(text(310, 65, "Тяга F_i = c_t · u_i", size=11, color=POS, bold=True))
    
    # Текстовий опис сил і моментів
    elements.append(text(200, 240, "Реактивний момент: Q_i = d_i · c_m · u_i", size=11, color=MUTED))
    elements.append(text(200, 265, "Момент від тяги: M_i = r_i × F_i", size=11, color=MUTED))
    
    # Права частина: Матриця B та її стовпчик
    elements.append(rect(400, 20, 400, 275, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    elements.append(text(600, 48, "Стовпчик b_i матриці ефективності B", size=13, color=INK, bold=True))
    
    # Текстові формули стовпчика без вкладених rect
    elements.append(text(430, 90, "F_z :  -c_t · n_z,i", size=12, color=INK, bold=True, anchor="start"))
    elements.append(text(430, 140, "M_x :  c_t · (y_i · n_z,i - z_i · n_y,i) + c_m · d_i · n_x,i", size=11, color=INK, anchor="start"))
    elements.append(text(430, 190, "M_y :  c_t · (z_i · n_x,i - x_i · n_z,i) + c_m · d_i · n_y,i", size=11, color=INK, anchor="start"))
    elements.append(text(430, 240, "M_z :  c_t · (x_i · n_y,i - y_i · n_x,i) + c_m · d_i · n_z,i", size=11, color=INK, anchor="start"))
    
    # Пояснення параметрів
    elements.append(text(600, 275, "n_i — напрямний вектор осі тяги; d_i ∈ {+1, -1} — напрям обертання", size=10, color=MUTED))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'geometry-to-effectiveness.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_airframes_comparison():
    """Фігура 3: Порівняння схем алокації: Квадро-X, Гексакоптер та Літак (V-Tail / Елевони)."""
    w, h = 840, 270
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # 1. Quad X
    elements.append(rect(20, 20, 250, 230, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(145, 45, "Квадрокоптер Quad-X", size=13, color=INK, bold=True))
    elements.append(text(145, 68, "4 мотори → 4 ступені свободи", size=11, color=MUTED))
    elements.append(text(145, 90, "Матриця B: 4 × 4 (квадратна)", size=11, color=INK, bold=True))
    elements.append(text(145, 115, "u = B⁻¹ · τ", size=12, color=NEG, bold=True))
    elements.append(text(145, 145, "• Єдиний точний розв'язок", size=11, color=INK))
    elements.append(text(145, 170, "• Нульова надлишковість", size=11, color=INK))
    elements.append(text(145, 195, "• Відмова 1 мотора → аварія", size=11, color=POS, bold=True))
    
    # 2. Hexa X
    elements.append(rect(295, 20, 250, 230, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    elements.append(text(420, 45, "Гексакоптер Hexa-X", size=13, color=INK, bold=True))
    elements.append(text(420, 68, "6 моторів → 4 ступені свободи", size=11, color=MUTED))
    elements.append(text(420, 90, "Матриця B: 4 × 6 (надлишкова)", size=11, color=INK, bold=True))
    elements.append(text(420, 115, "u = Bᵀ(B Bᵀ)⁻¹ · τ", size=12, color=FIELD, bold=True))
    elements.append(text(420, 145, "• Безліч можливих розв'язків", size=11, color=INK))
    elements.append(text(420, 170, "• Мінімум енергії: min ||u||₂", size=11, color=INK))
    elements.append(text(420, 195, "• Відмовостійкість при аварії", size=11, color=FIELD, bold=True))
    
    # 3. Fixed Wing (V-tail / Elevons)
    elements.append(rect(570, 20, 250, 230, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8))
    elements.append(text(695, 45, "Літак / VTOL (Елевони / V-Tail)", size=12, color=INK, bold=True))
    elements.append(text(695, 68, "Тяга мотора + сервоповерхні", size=11, color=MUTED))
    elements.append(text(695, 90, "Матриця B: неоднорідні приводи", size=11, color=INK, bold=True))
    elements.append(text(695, 115, "u_servo = B_aero⁺ · M_des", size=12, color="#ca8a04", bold=True))
    elements.append(text(695, 145, "• Елевони: Крен + Тангаж", size=11, color=INK))
    elements.append(text(695, 170, "• V-Tail: Тангаж + Рискання", size=11, color=INK))
    elements.append(text(695, 195, "• Залежність від швидкості q(V)", size=11, color=INK))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'multirotor-vs-fixedwing-mixing.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_desaturation_ladder():
    """Фігура 4: Драбина пріоритетів десатурації при виході приводів на насичення."""
    w, h = 800, 280
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    elements.append(text(400, 30, "Ієрархія пріоритетів збереження керованості при насиченні приводів", 
                         size=13, color=INK, bold=True))
    
    # 3 рівні сходів
    # Рівень 1: Roll & Pitch
    b1_body = rect(50, 60, 700, 50, fill="#fee2e2", stroke=POS, sw=1.8, rx=6)
    elements.append(b1_body)
    elements.append(text(180, 90, "Пріоритет 1: Крен і Тангаж (Roll & Pitch)", size=12, color=POS, bold=True))
    elements.append(text(520, 90, "Гарантія кутової стійкості (втрата = перекидання апарата)", size=11, color=INK))
    
    # Рівень 2: Yaw
    b2_body = rect(100, 125, 650, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6)
    elements.append(b2_body)
    elements.append(text(230, 155, "Пріоритет 2: Рискання (Yaw)", size=12, color="#d97706", bold=True))
    elements.append(text(540, 155, "Масштабується або обнуляється при дефіциті тяги мотора", size=11, color=INK))
    
    # Рівень 3: Thrust
    b3_body = rect(150, 190, 600, 50, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=6)
    elements.append(b3_body)
    elements.append(text(280, 220, "Пріоритет 3: Загальна тяга (Thrust)", size=12, color=NEG, bold=True))
    elements.append(text(560, 220, "Зсувається вниз/вгору для вивільнення запасу під моменти", size=11, color=INK))
    
    # Стрілка спадання пріоритету
    elements.append(arrow(35, 65, 35, 235, color=POS, sw=2.5))
    elements.append(text(25, 150, "Пріоритет", size=10, color=POS, bold=True, anchor="middle"))
    
    # Пояснення знизу
    elements.append(text(400, 262, "Краще втратити кілька метрів висоти чи градусів курсу, ніж допустити неконтрольований крен", 
                         size=11, color=MUTED, italic=True))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#c0392b"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'desaturation-priority-ladder.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_allocation_pipeline()
    fig_geometry_to_matrix()
    fig_airframes_comparison()
    fig_desaturation_ladder()
