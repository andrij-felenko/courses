#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор діаграм для теми DIAC (power-electronics/diac)."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_structure_5layer():
    """Фігура 1: П'ятишарова напівпровідникова структура DIAC (N-P-N-P-N) та еквівалент."""
    w, h = 820, 420
    frags = []

    # Заголовок блоку 1: Фізичний кристал
    frags.append(text(210, 35, "П'ятишаровий кристал (N-P-N-P-N)", size=15, bold=True))

    # Вивід Анод 1 (A1 / MT1)
    frags.append(rect(180, 55, 60, 18, fill="#a0aec0", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(210, 68, "A1 (MT1)", size=12, bold=True))
    frags.append(line(210, 45, 210, 55, color=LINE, sw=2))

    # Шари напівпровідника
    # N1 шар
    frags.append(rect(110, 73, 200, 45, fill="#fed7d7", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(210, 100, "N1 (емітер 1)", size=13, bold=True, color=POS))

    # P1 шар
    frags.append(rect(110, 118, 200, 45, fill="#bee3f8", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(210, 145, "P1 (база 1)", size=13, bold=True, color=NEG))

    # N2 шар (центральна база)
    frags.append(rect(110, 163, 200, 55, fill="#feebc8", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(210, 194, "N2 (центральна база)", size=13, bold=True, color="#c05621"))

    # P2 шар
    frags.append(rect(110, 218, 200, 45, fill="#bee3f8", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(210, 245, "P2 (база 2)", size=13, bold=True, color=NEG))

    # N3 шар
    frags.append(rect(110, 263, 200, 45, fill="#fed7d7", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(210, 290, "N3 (емітер 2)", size=13, bold=True, color=POS))

    # Вивід Анод 2 (A2 / MT2)
    frags.append(rect(180, 308, 60, 18, fill="#a0aec0", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(210, 321, "A2 (MT2)", size=12, bold=True))
    frags.append(line(210, 326, 210, 340, color=LINE, sw=2))

    # Позначення переходів (J1, J2, J3, J4)
    frags.append(text(80, 122, "J1 (P-N)", size=11, color=MUTED, anchor="end"))
    frags.append(line(85, 118, 110, 118, color=MUTED, sw=1, dash="3,3"))

    frags.append(text(80, 167, "J2 (N-P)", size=11, color=MUTED, anchor="end"))
    frags.append(line(85, 163, 110, 163, color=MUTED, sw=1, dash="3,3"))

    frags.append(text(80, 222, "J3 (P-N)", size=11, color=MUTED, anchor="end"))
    frags.append(line(85, 218, 110, 218, color=MUTED, sw=1, dash="3,3"))

    frags.append(text(80, 267, "J4 (N-P)", size=11, color=MUTED, anchor="end"))
    frags.append(line(85, 263, 110, 263, color=MUTED, sw=1, dash="3,3"))

    # Пояснення напрямків струму
    b1, _, _ = textbox(210, 380, "Полярність A1 > A2: працює шлях N1-P1-N2-P2\nПолярність A2 > A1: працює шлях N3-P2-N2-P1", size=12, fill="#edf2f7")
    frags.append(b1)

    # Розділювач
    frags.append(line(420, 30, 420, 400, color="#e2e8f0", sw=1.5))

    # Блок 2: Еквівалентна схема з двох антипаралельних диністорів та символ
    frags.append(text(620, 35, "Еквівалент і графічний символ", size=15, bold=True))

    # Зустрічно-паралельні 4-шарові диністори
    # Лівий диністор (вниз)
    frags.append(line(510, 70, 510, 95, color=LINE, sw=1.8))
    frags.append(rect(480, 95, 60, 70, fill="#f7fafc", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(510, 120, "Диністор", size=11, bold=True))
    frags.append(text(510, 140, "P-N-P-N ↓", size=11, color=POS))
    frags.append(line(510, 165, 510, 190, color=LINE, sw=1.8))

    # Правий диністор (вгору)
    frags.append(line(610, 70, 610, 95, color=LINE, sw=1.8))
    frags.append(rect(580, 95, 60, 70, fill="#f7fafc", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(610, 120, "Диністор", size=11, bold=True))
    frags.append(text(610, 140, "P-N-P-N ↑", size=11, color=NEG))
    frags.append(line(610, 165, 610, 190, color=LINE, sw=1.8))

    # З'єднання вхід/вихід еквівалента
    frags.append(line(510, 70, 610, 70, color=LINE, sw=1.8))
    frags.append(line(560, 50, 560, 70, color=LINE, sw=2))
    frags.append(text(560, 42, "A1", size=13, bold=True))

    frags.append(line(510, 190, 610, 190, color=LINE, sw=1.8))
    frags.append(line(560, 190, 560, 210, color=LINE, sw=2))
    frags.append(text(560, 226, "A2", size=13, bold=True))

    # Стрілка еквівалентності
    frags.append(text(685, 135, "≡", size=24, bold=True, color=MUTED))

    # Графічний символ DIAC (два зустрічні трикутники)
    sx, sy = 750, 130
    frags.append(line(sx, sy - 55, sx, sy - 20, color=LINE, sw=2))
    frags.append(text(sx, sy - 63, "A1", size=13, bold=True))

    # Символ діодів назустріч
    frags.append(line(sx - 16, sy - 20, sx + 16, sy - 20, color=LINE, sw=1.8))
    # Трикутник вниз
    frags.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        sx - 14, sy - 20, sx + 14, sy - 20, sx, sy, FILL, LINE))
    # Трикутник вгору
    frags.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
        sx - 14, sy + 20, sx + 14, sy + 20, sx, sy, FILL, LINE))
    frags.append(line(sx - 16, sy + 20, sx + 16, sy + 20, color=LINE, sw=1.8))

    frags.append(line(sx, sy + 20, sx, sy + 55, color=LINE, sw=2))
    frags.append(text(sx, sy + 70, "A2", size=13, bold=True))

    # Текстова врізка під символом
    b2, _, _ = textbox(620, 330, "Повна двобічна симетрія:\nприлад не має керуючого затвора\nі вмикається виключно напругою", size=12, fill="#f0fff4", stroke=FIELD)
    frags.append(b2)

    render(os.path.join(OUT_DIR, "diac-structure-5layer.svg"), w, h, *frags)


def fig_iv_curve():
    """Фігура 2: Симетрична вольт-амперна характеристика (ВАХ) DIAC."""
    w, h = 820, 520
    frags = []

    # Заголовок
    frags.append(text(410, 25, "Симетрична вольт-амперна характеристика (ВАХ) DIAC", size=15, bold=True))

    # Центр координат
    cx, cy = 410, 265

    # Вісі координат
    frags.append(arrow(60, cy, 760, cy, color=LINE, sw=1.5))
    frags.append(text(765, cy - 10, "+V", size=14, bold=True))
    frags.append(text(65, cy - 10, "−V", size=14, bold=True))

    frags.append(arrow(cx, 490, cx, 45, color=LINE, sw=1.5))
    frags.append(text(cx + 15, 55, "+I", size=14, bold=True))
    frags.append(text(cx + 15, 485, "−I", size=14, bold=True))

    # Крива I квадранта (додатна півхвиля)
    path_q1 = (
        f"M {cx} {cy} "
        f"Q {cx+120} {cy-5}, {cx+185} {cy-15} "
        f"Q {cx+210} {cy-22}, {cx+210} {cy-32} "
        f"L {cx+140} {cy-115} "
        f"Q {cx+145} {cy-165}, {cx+165} {cy-205}"
    )
    frags.append(f'<path d="{path_q1}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Крива III квадранта (від'ємна півхвиля - точкова симетрія)
    path_q3 = (
        f"M {cx} {cy} "
        f"Q {cx-120} {cy+5}, {cx-185} {cy+15} "
        f"Q {cx-210} {cy+22}, {cx-210} {cy+32} "
        f"L {cx-140} {cy+115} "
        f"Q {cx-145} {cy+165}, {cx-165} {cy+205}"
    )
    frags.append(f'<path d="{path_q3}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Пунктирні лінії проекцій для V_BO та I_BO
    frags.append(line(cx + 210, cy, cx + 210, cy - 32, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(cx, cy - 32, cx + 210, cy - 32, color=MUTED, sw=1.2, dash="3,3"))

    frags.append(line(cx - 210, cy, cx - 210, cy + 32, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(cx, cy + 32, cx - 210, cy + 32, color=MUTED, sw=1.2, dash="3,3"))

    # Пунктир для залишкової напруги (після спаду)
    frags.append(line(cx + 140, cy, cx + 140, cy - 115, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(cx - 140, cy, cx - 140, cy + 115, color=MUTED, sw=1.2, dash="3,3"))

    # Позначки на вісях
    frags.append(text(cx + 210, cy + 18, "+V_BO (~32 В)", size=12, bold=True, color=POS))
    frags.append(text(cx + 140, cy + 18, "V_F (~22 В)", size=11, color=MUTED))
    frags.append(text(cx - 210, cy - 10, "−V_BO (~−32 В)", size=12, bold=True, color=NEG))
    frags.append(text(cx - 140, cy - 10, "−V_F", size=11, color=MUTED))

    frags.append(text(cx - 30, cy - 30, "+I_BO", size=11, color=MUTED, anchor="end"))
    frags.append(text(cx + 35, cy + 35, "−I_BO", size=11, color=MUTED, anchor="start"))

    # Стрілка спаду напруги (Dynamic Foldback ΔV)
    frags.append(arrow(cx + 205, cy - 70, cx + 145, cy - 70, color="#d69e2e", sw=2))
    frags.append(text(cx + 175, cy - 80, "ΔV (~10 В)", size=12, bold=True, color="#b7791f"))

    # Струм утримання I_H
    frags.append(line(cx, cy - 115, cx + 140, cy - 115, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(cx - 10, cy - 112, "I_H", size=12, bold=True, anchor="end"))

    # Підписи ключових областей
    b_blk, _, _ = textbox(570, 360, "1. Стан блокування (I < 10 мкА)\n2. Лавинний пробій при V = V_BO\n3. Від'ємний опір (dV/dI < 0)\n4. Провідний стан (розряд C)", size=12, fill="#f7fafc")
    frags.append(b_blk)

    # Точки на графіку
    frags.append(circle(cx + 210, cy - 32, 4, fill=POS, stroke=LINE, sw=1))
    frags.append(circle(cx + 140, cy - 115, 4, fill=POS, stroke=LINE, sw=1))
    frags.append(circle(cx - 210, cy + 32, 4, fill=NEG, stroke=LINE, sw=1))
    frags.append(circle(cx - 140, cy + 115, 4, fill=NEG, stroke=LINE, sw=1))

    # Виноски до точок
    frags.append(text(cx + 220, cy - 42, "Точка перемикання (V_BO, I_BO)", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(cx + 130, cy - 130, "Спадання напруги (Foldback)", size=11, color="#b7791f", anchor="end"))

    render(os.path.join(OUT_DIR, "diac-iv-curve.svg"), w, h, *frags)


def fig_waveforms():
    """Фігура 3: Часові діаграми фазового регулятора з RC-DIAC."""
    w, h = 820, 480
    frags = []

    frags.append(text(410, 25, "Формування імпульсу відмикання симістора через RC-DIAC", size=15, bold=True))

    x0, x1 = 120, 760
    w_t = x1 - x0

    # 1. Напруга мережі (Синусоїда)
    y1 = 80
    frags.append(text(60, y1, "V_mains", size=12, bold=True))
    frags.append(line(x0, y1, x1, y1, color=MUTED, sw=1))
    p_mains = (
        f"M {x0} {y1} "
        f"Q {x0+w_t*0.125} {y1-40}, {x0+w_t*0.25} {y1} "
        f"Q {x0+w_t*0.375} {y1+40}, {x0+w_t*0.5} {y1} "
        f"Q {x0+w_t*0.625} {y1-40}, {x0+w_t*0.75} {y1} "
        f"Q {x0+w_t*0.875} {y1+40}, {x1} {y1}"
    )
    frags.append(f'<path d="{p_mains}" fill="none" stroke="#4a5568" stroke-width="1.8"/>')

    # 2. Напруга на конденсаторі V_C
    y2 = 180
    frags.append(text(60, y2, "V_C (на C)", size=12, bold=True))
    frags.append(line(x0, y2, x1, y2, color=MUTED, sw=1))
    frags.append(line(x0, y2 - 28, x1, y2 - 28, color=POS, sw=1, dash="4,3"))
    frags.append(text(x0 - 10, y2 - 25, "+V_BO", size=10, color=POS, anchor="end"))
    frags.append(line(x0, y2 + 28, x1, y2 + 28, color=NEG, sw=1, dash="4,3"))
    frags.append(text(x0 - 10, y2 + 31, "−V_BO", size=10, color=NEG, anchor="end"))

    t_f1 = x0 + int(w_t * 0.15)
    t_z1 = x0 + int(w_t * 0.25)
    t_f2 = x0 + int(w_t * 0.40)
    t_z2 = x0 + int(w_t * 0.50)
    t_f3 = x0 + int(w_t * 0.65)
    t_z3 = x0 + int(w_t * 0.75)

    p_vc = (
        f"M {x0} {y2} "
        f"Q {x0+w_t*0.08} {y2-15}, {t_f1} {y2-28} "
        f"L {t_f1} {y2-8} "
        f"L {t_z1} {y2} "
        f"Q {x0+w_t*0.33} {y2+15}, {t_f2} {y2+28} "
        f"L {t_f2} {y2+8} "
        f"L {t_z2} {y2} "
        f"Q {x0+w_t*0.58} {y2-15}, {t_f3} {y2-28} "
        f"L {t_f3} {y2-8} "
        f"L {t_z3} {y2} "
        f"L {x1} {y2}"
    )
    frags.append(f'<path d="{p_vc}" fill="none" stroke="#d69e2e" stroke-width="2.2"/>')

    # 3. Струм імпульсу в затвор
    y3 = 280
    frags.append(text(60, y3, "I_Gate (DIAC)", size=12, bold=True))
    frags.append(line(x0, y3, x1, y3, color=MUTED, sw=1))

    frags.append(line(t_f1, y3, t_f1, y3 - 35, color=POS, sw=2.5))
    frags.append(text(t_f1 + 8, y3 - 25, "Імпульс >1 А", size=10, bold=True, color=POS, anchor="start"))

    frags.append(line(t_f2, y3, t_f2, y3 + 35, color=NEG, sw=2.5))
    frags.append(text(t_f2 + 8, y3 + 30, "Від'ємний імпульс", size=10, bold=True, color=NEG, anchor="start"))

    frags.append(line(t_f3, y3, t_f3, y3 - 35, color=POS, sw=2.5))

    # 4. Напруга на навантаженні
    y4 = 390
    frags.append(text(60, y4, "V_Load", size=12, bold=True))
    frags.append(line(x0, y4, x1, y4, color=MUTED, sw=1))

    p_load = (
        f"M {x0} {y4} L {t_f1} {y4} "
        f"L {t_f1} {y4-35} "
        f"Q {x0+w_t*0.20} {y4-30}, {t_z1} {y4} "
        f"L {t_f2} {y4} "
        f"L {t_f2} {y4+35} "
        f"Q {x0+w_t*0.45} {y4+30}, {t_z2} {y4} "
        f"L {t_f3} {y4} "
        f"L {t_f3} {y4-35} "
        f"Q {x0+w_t*0.70} {y4-30}, {t_z3} {y4} "
        f"L {x1} {y4}"
    )
    frags.append(f'<path d="{p_load}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')

    # Вертикальні лінії моменту вмикання
    frags.append(line(t_f1, y1 - 40, t_f1, y4 + 40, color=POS, sw=1, dash="2,2"))
    frags.append(line(t_f2, y1 - 40, t_f2, y4 + 40, color=NEG, sw=1, dash="2,2"))

    # Позначення кута фазового відсікання
    frags.append(text(t_f1, 460, "Кут відсікання α", size=12, bold=True, color=POS))
    frags.append(text(t_f2, 460, "Симетричний кут α", size=12, bold=True, color=NEG))

    render(os.path.join(OUT_DIR, "diac-triac-waveforms.svg"), w, h, *frags)


def fig_antihysteresis():
    """Фігура 4: Схема одинарного RC-кола з гістерезисом проти подвійного RC-кола."""
    w, h = 820, 420
    frags = []

    frags.append(text(410, 25, "Усунення стрибка («snap-on») подвійним RC-ланцюжком", size=15, bold=True))

    # Схема A: Простий одинарний RC (з гістерезисом)
    frags.append(text(210, 55, "А. Простий RC-димер (із гістерезисом)", size=13, bold=True))

    frags.append(text(70, 90, "Фаза L", size=12, bold=True))
    frags.append(line(90, 90, 150, 90, color=LINE, sw=2))

    # Потенціометр R_pot
    frags.append(rect(150, 80, 50, 20, fill="#edf2f7", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(175, 94, "R_пот", size=11, bold=True))

    frags.append(line(200, 90, 240, 90, color=LINE, sw=2))
    frags.append(circle(240, 90, 3, fill=INK, stroke=LINE, sw=1))

    # Конденсатор C1 вниз
    frags.append(line(240, 90, 240, 140, color=LINE, sw=2))
    frags.append(line(225, 140, 255, 140, color=LINE, sw=2))
    frags.append(line(225, 147, 255, 147, color=LINE, sw=2))
    frags.append(text(270, 145, "C1", size=12, bold=True))
    frags.append(line(240, 147, 240, 200, color=LINE, sw=2))
    frags.append(text(240, 215, "Нейтраль N / MT1", size=11, color=MUTED))

    # DIAC вправо
    frags.append(line(240, 90, 290, 90, color=LINE, sw=2))
    frags.append(rect(290, 80, 45, 20, fill="#feebc8", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(312, 94, "DIAC", size=11, bold=True))
    frags.append(line(335, 90, 370, 90, color=LINE, sw=2))
    frags.append(text(375, 94, "→ Gate", size=12, bold=True, color=POS, anchor="start"))

    b_a, _, _ = textbox(210, 310, "Вада: після пробою DIAC конденсатор C1\nскидає заряд не до 0, а до V_residual.\nПри регулюванні виникає стрибок запалювання\n(лампа спалахує одразу на 30% яскравості)", size=11, fill="#fff5f5", stroke=POS)
    frags.append(b_a)

    # Розділювач
    frags.append(line(420, 50, 420, 390, color="#e2e8f0", sw=1.5))

    # Схема Б: Подвійне RC-коло (Double RC Anti-hysteresis)
    frags.append(text(620, 55, "Б. Подвійне RC-коло (без гістерезису)", size=13, bold=True))

    frags.append(text(460, 90, "Фаза L", size=12, bold=True))
    frags.append(line(480, 90, 510, 90, color=LINE, sw=2))

    # R_pot
    frags.append(rect(510, 80, 45, 20, fill="#edf2f7", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(532, 94, "R_пот", size=10, bold=True))
    frags.append(line(555, 90, 580, 90, color=LINE, sw=2))
    frags.append(circle(580, 90, 3, fill=INK, stroke=LINE, sw=1))

    # C1 (головний фазозсувний)
    frags.append(line(580, 90, 580, 140, color=LINE, sw=2))
    frags.append(line(568, 140, 592, 140, color=LINE, sw=2))
    frags.append(line(568, 147, 592, 147, color=LINE, sw=2))
    frags.append(text(605, 145, "C1 (0.1 мкФ)", size=10, bold=True))
    frags.append(line(580, 147, 580, 200, color=LINE, sw=2))

    # Розв'язуючий резистор R2
    frags.append(line(580, 90, 620, 90, color=LINE, sw=2))
    frags.append(rect(620, 80, 40, 20, fill="#edf2f7", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(640, 94, "R2", size=10, bold=True))
    frags.append(line(660, 90, 685, 90, color=LINE, sw=2))
    frags.append(circle(685, 90, 3, fill=INK, stroke=LINE, sw=1))

    # Другий малий конденсатор C2
    frags.append(line(685, 90, 685, 140, color=LINE, sw=2))
    frags.append(line(673, 140, 697, 140, color=LINE, sw=2))
    frags.append(line(673, 147, 697, 147, color=LINE, sw=2))
    frags.append(text(710, 145, "C2 (22 нФ)", size=10, bold=True))
    frags.append(line(685, 147, 685, 200, color=LINE, sw=2))

    frags.append(line(580, 200, 685, 200, color=LINE, sw=2))
    frags.append(text(632, 215, "Нейтраль N / MT1", size=11, color=MUTED))

    # DIAC після другого ступеня
    frags.append(line(685, 90, 725, 90, color=LINE, sw=2))
    frags.append(rect(725, 80, 40, 20, fill="#feebc8", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(745, 94, "DIAC", size=10, bold=True))
    frags.append(line(765, 90, 785, 90, color=LINE, sw=2))
    frags.append(text(790, 94, "→ G", size=12, bold=True, color=FIELD, anchor="start"))

    b_b, _, _ = textbox(620, 310, "Перевага: розряджається лише малий C2.\nГоловний конденсатор C1 зберігає плавний\nфазовий зсув без стрибка напруги.\nРегулювання починається плавно від 1%", size=11, fill="#f0fff4", stroke=FIELD)
    frags.append(b_b)

    render(os.path.join(OUT_DIR, "diac-dimmer-antihysteresis.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_structure_5layer()
    fig_iv_curve()
    fig_waveforms()
    fig_antihysteresis()
    print("Всі фігури DIAC успішно згенеровано.")
