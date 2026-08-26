#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «ШІМ, мотор і АЦП: чому показ давача танцює під газом».
Всі розміри, відступи та розміщення написів узгоджені з svgkit і svgcheck.py.
"""

import os
import sys

# Підключаємо спільний модуль svgkit з кореневої директорії scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def polyline(pts, stroke=LINE, sw=1.5, fill="none"):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{pts_str}" stroke="{stroke}" stroke-width="{sw:.1f}" fill="{fill}"/>'


def fig_coupling_mechanisms():
    """Фігура 1: Три шляхи проникнення завад від ШІМ-мотора в аналоговий вимірювальний тракт."""
    w, h = 820, 460
    f = []

    # Три великі блоки для трьох механізмів
    col_w = 245
    col_gap = 25
    x_start = 20
    top_y = 60
    box_h = 375

    # 1. Кондуктивний зв'язок по спільній землі
    x1 = x_start
    f.append(rect(x1, top_y, col_w, box_h, fill="#fff8f7", stroke=POS, sw=1.8, rx=8))
    f.append(fitbox(x1 + 10, top_y + 12, col_w - 20, 42, "1. Спільний імпеданс\n(Кондуктивний)", size=14, bold=True, fill="#fdecea", stroke=POS))

    # Схема 1
    # Джерело живлення
    f.append(rect(x1 + 25, top_y + 70, 70, 35, fill=FILL, stroke=LINE, sw=1.2))
    f.append(text(x1 + 60, top_y + 92, "V_BAT", size=12, bold=True))

    # Силовий міст + мотор
    f.append(rect(x1 + 145, top_y + 70, 80, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(x1 + 185, top_y + 90, "H-міст", size=12, bold=True, color=POS))
    f.append(text(x1 + 185, top_y + 107, "+ Мотор", size=11, color=POS))

    # Аналоговий давач + АЦП
    f.append(rect(x1 + 145, top_y + 155, 80, 50, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(x1 + 185, top_y + 175, "Давач", size=12, bold=True, color=NEG))
    f.append(text(x1 + 185, top_y + 192, "+ АЦП", size=11, color=NEG))

    # З'єднання
    f.append(line(x1 + 95, top_y + 80, x1 + 145, top_y + 80, color=POS, sw=2))
    f.append(line(x1 + 60, top_y + 105, x1 + 60, top_y + 240, color=LINE, sw=1.5))
    f.append(line(x1 + 60, top_y + 240, x1 + 185, top_y + 240, color=LINE, sw=2))

    # Повернення струмів
    f.append(line(x1 + 185, top_y + 120, x1 + 185, top_y + 240, color=POS, sw=2.5))
    f.append(line(x1 + 185, top_y + 205, x1 + 185, top_y + 240, color=NEG, sw=1.5))

    # Паразитний імпеданс на спільній ділянці
    f.append(rect(x1 + 90, top_y + 230, 65, 20, fill="#fff275", stroke=LINE, sw=1.2))
    f.append(text(x1 + 122, top_y + 245, "R_gnd, L_gnd", size=10, bold=True))

    # Стрілка струму мотора
    f.append(arrow(x1 + 170, top_y + 235, x1 + 80, top_y + 235, color=POS, sw=2))
    f.append(text(x1 + 125, top_y + 223, "I_мотора (di/dt)", size=11, color=POS, bold=True))

    # Формула і пояснення
    f.append(fitbox(x1 + 10, top_y + 270, col_w - 20, 95, "Спільна доріжка землі:\nV_шум = I·R + L·(di/dt)\n\nСтрибок струму на L_gnd\nзміщує опорний рівень АЦП\nна сотні мілівольтів.", size=12, fill="#ffffff", stroke=MUTED))


    # 2. Ємнісна наводка (dV/dt)
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, top_y, col_w, box_h, fill="#fdfefe", stroke=NEG, sw=1.8, rx=8))
    f.append(fitbox(x2 + 10, top_y + 12, col_w - 20, 42, "2. Ємнісний зв'язок\n(Наводка dV/dt)", size=14, bold=True, fill="#eaf0fd", stroke=NEG))

    # Силовий вузол перемикання (SW)
    f.append(rect(x2 + 25, top_y + 75, 195, 36, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(x2 + 122, top_y + 98, "Силова фаза (ШІМ: 0 → 24 В)", size=12, bold=True, color=POS))

    # Паразитна ємність
    f.append(line(x2 + 122, top_y + 111, x2 + 122, top_y + 145, color=MUTED, sw=1.5, dash="4,3"))
    f.append(line(x2 + 100, top_y + 145, x2 + 144, top_y + 145, color=LINE, sw=2))
    f.append(line(x2 + 100, top_y + 153, x2 + 144, top_y + 153, color=LINE, sw=2))
    f.append(text(x2 + 175, top_y + 152, "C_пар (1–5 пФ)", size=11, bold=True, color=MUTED))
    f.append(line(x2 + 122, top_y + 153, x2 + 122, top_y + 185, color=MUTED, sw=1.5, dash="4,3"))

    # Високоомна лінія давача
    f.append(rect(x2 + 25, top_y + 185, 195, 36, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(x2 + 122, top_y + 208, "Аналогова доріжка (R_вх > 10 кОм)", size=12, bold=True, color=NEG))

    # Струм зміщення
    f.append(arrow(x2 + 110, top_y + 115, x2 + 110, top_y + 180, color=POS, sw=2))
    f.append(text(x2 + 65, top_y + 140, "I_disp", size=11, bold=True, color=POS))

    # Формула і пояснення
    f.append(fitbox(x2 + 10, top_y + 270, col_w - 20, 95, "Струм через паразитну ємність:\nI_disp = C_пар · (dV/dt)\n\nНа високому опорі R_вх\nструм породжує сплески\nнапруги до десятків вольт.", size=12, fill="#ffffff", stroke=MUTED))


    # 3. Індуктивна наводка (di/dt магнітне поле)
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, top_y, col_w, box_h, fill="#f9fbf9", stroke=FIELD, sw=1.8, rx=8))
    f.append(fitbox(x3 + 10, top_y + 12, col_w - 20, 42, "3. Індуктивний зв'язок\n(Магнітне поле петлі)", size=14, bold=True, fill="#eafaf1", stroke=FIELD))

    # Силова петля струму
    f.append(rect(x3 + 25, top_y + 70, 195, 60, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    f.append(text(x3 + 122, top_y + 92, "Силова петля мотора", size=12, bold=True, color=POS))
    f.append(text(x3 + 122, top_y + 112, "Велика площа A₁ · Струм di/dt", size=11, color=POS))
    f.append(arrow(x3 + 40, top_y + 120, x3 + 200, top_y + 120, color=POS, sw=1.8))

    # Магнітне поле B(t)
    f.append(circle(x3 + 80, top_y + 160, 14, fill="#f4fbf7", stroke=FIELD, sw=1.5))
    f.append(text(x3 + 80, top_y + 165, "B(t)", size=11, bold=True, color=FIELD))
    f.append(circle(x3 + 165, top_y + 160, 14, fill="#f4fbf7", stroke=FIELD, sw=1.5))
    f.append(text(x3 + 165, top_y + 165, "B(t)", size=11, bold=True, color=FIELD))
    f.append(text(x3 + 122, top_y + 165, "Взаємна індукція M", size=11, bold=True, color=FIELD))

    # Аналогова вимірювальна петля
    f.append(rect(x3 + 25, top_y + 190, 195, 55, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    f.append(text(x3 + 122, top_y + 212, "Контур сигналу давача", size=12, bold=True, color=NEG))
    f.append(text(x3 + 122, top_y + 230, "Петля площею A₂ до АЦП", size=11, color=NEG))

    # Формула і пояснення
    f.append(fitbox(x3 + 10, top_y + 270, col_w - 20, 95, "Наведена ЕРС у контурі:\nV_ind = -M · (di/dt)\n\nЗмінний магнітний потік\nвід силових провідників наводить\nЕРС прямо в сигнальну петлю.", size=12, fill="#ffffff", stroke=MUTED))

    render(os.path.join(IMG_DIR, "coupling-mechanisms.svg"), w, h, *f, title="Шляхи проникнення ШІМ-завад у вимірювальний тракт")


def fig_pcb_grounding():
    """Фігура 2: Топологія друкованої плати: помилкова послідовна земля проти зіркового заземлення."""
    w, h = 820, 460
    f = []

    half_w = 380
    top_y = 60
    box_h = 375

    # Ліва половина: Помилка (ланцюгове заземлення)
    x1 = 20
    f.append(rect(x1, top_y, half_w, box_h, fill="#fff8f7", stroke=POS, sw=1.5, rx=8))
    f.append(fitbox(x1 + 15, top_y + 15, half_w - 30, 36, "НЕПРАВИЛЬНО: Послідовна спільна земля", size=14, bold=True, fill="#fdecea", stroke=POS))

    # Блоки зліва
    f.append(rect(x1 + 25, top_y + 70, 80, 45, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(x1 + 65, top_y + 95, "Джерело\n(АКБ)", size=11, bold=True))

    f.append(rect(x1 + 145, top_y + 70, 100, 45, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(x1 + 195, top_y + 95, "Драйвер + Мотор\n(Струми 10–30 А)", size=10, bold=True, color=POS))

    f.append(rect(x1 + 275, top_y + 70, 80, 45, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(x1 + 315, top_y + 95, "Давач\n+ АЦП МК", size=11, bold=True, color=NEG))

    # Земляна шина знизу
    f.append(line(x1 + 65, top_y + 115, x1 + 65, top_y + 200, color=LINE, sw=2))
    f.append(line(x1 + 195, top_y + 115, x1 + 195, top_y + 200, color=POS, sw=3))
    f.append(line(x1 + 315, top_y + 115, x1 + 315, top_y + 200, color=NEG, sw=1.5))

    # Послідовна шина землі
    f.append(line(x1 + 65, top_y + 200, x1 + 315, top_y + 200, color=POS, sw=3))
    f.append(arrow(x1 + 180, top_y + 215, x1 + 80, top_y + 215, color=POS, sw=2))
    f.append(text(x1 + 130, top_y + 235, "I_силовий (ШІМ-імпульси)", size=11, bold=True, color=POS))

    # Зона шуму
    f.append(fitbox(x1 + 20, top_y + 260, half_w - 40, 105, "Катастрофічний ефект:\nСтрум мотора тече по ділянці землі давача.\nПадіння напруги ΔV = I_motor · Z_gnd створює\nдинамічний зсув опорної точки АЦП.\nПоказ давача «скаче» в такт із газом.", size=12, fill="#ffffff", stroke=POS))


    # Права половина: Зіркове заземлення (Star Ground / Кельвін)
    x2 = 420
    f.append(rect(x2, top_y, half_w, box_h, fill="#f9fbf9", stroke=FIELD, sw=1.5, rx=8))
    f.append(fitbox(x2 + 15, top_y + 15, half_w - 30, 36, "ПРАВИЛЬНО: Зіркова точка / Розділення зон", size=14, bold=True, fill="#eafaf1", stroke=FIELD))

    # Джерело і конденсатор з зірковою точкою
    f.append(rect(x2 + 25, top_y + 70, 75, 45, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(x2 + 62, top_y + 95, "Джерело\n+ C_bulk", size=11, bold=True))

    f.append(circle(x2 + 160, top_y + 180, 12, fill="#fff275", stroke=LINE, sw=2))
    f.append(text(x2 + 160, top_y + 184, "★", size=14, bold=True, color=POS))
    f.append(text(x2 + 160, top_y + 205, "Star Point (GND)", size=10, bold=True))

    # Силова зона
    f.append(rect(x2 + 225, top_y + 70, 130, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(x2 + 290, top_y + 90, "Силова зона (PGND)", size=11, bold=True, color=POS))
    f.append(text(x2 + 290, top_y + 107, "Драйвер + H-міст + Мотор", size=9, color=POS))

    # Аналогова зона
    f.append(rect(x2 + 225, top_y + 150, 130, 50, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(x2 + 290, top_y + 170, "Аналог (AGND)", size=11, bold=True, color=NEG))
    f.append(text(x2 + 290, top_y + 187, "Давач + Кельвін + АЦП", size=9, color=NEG))

    # Окремі шляхи повернення струму до зірки
    f.append(line(x2 + 62, top_y + 115, x2 + 160, top_y + 180, color=LINE, sw=2.5))
    f.append(line(x2 + 290, top_y + 120, x2 + 160, top_y + 180, color=POS, sw=2.5))
    f.append(line(x2 + 290, top_y + 200, x2 + 160, top_y + 180, color=NEG, sw=1.5))

    # Пояснення переваг
    f.append(fitbox(x2 + 20, top_y + 260, half_w - 40, 105, "Чистий результат:\n1. Силовий поворотний струм PGND замикається\n   на конденсатор живлення, не заходячи в AGND.\n2. Аналогова земля AGND під'єднана в одній точці.\n3. Диференційні лінії Кельвіна усувають падіння.", size=12, fill="#ffffff", stroke=FIELD))

    render(os.path.join(IMG_DIR, "pcb-grounding-star-split.svg"), w, h, *f, title="Топологія друкованої плати: послідовна земля проти зіркової")


def fig_pwm_adc_sync_timing():
    """Фігура 3: Центрований ШІМ, комутаційний дзвін та синхронізована вибірка АЦП за TRGO."""
    w, h = 820, 480
    f = []

    # Сітка часу та осі
    top_y = 60
    f.append(rect(20, top_y, 780, 400, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    # Лінії фаз ШІМ
    # 1. Лічильник таймера (Center-Aligned Up-Down)
    f.append(text(120, top_y + 35, "Лічильник TIM (Up-Down):", size=13, bold=True, anchor="end"))
    f.append(line(130, top_y + 55, 280, top_y + 15, color=FIELD, sw=2))
    f.append(line(280, top_y + 15, 430, top_y + 55, color=FIELD, sw=2))
    f.append(line(430, top_y + 55, 580, top_y + 15, color=FIELD, sw=2))
    f.append(line(580, top_y + 15, 730, top_y + 55, color=FIELD, sw=2))

    f.append(text(280, top_y + 10, "Вершина (ARR / Overflow)", size=10, bold=True, color=FIELD))
    f.append(text(430, top_y + 68, "Низ (0 / Underflow)", size=10, bold=True, color=FIELD))

    # 2. Сигнал ШІМ на затворі / фазі
    f.append(text(120, top_y + 115, "Сигнал ШІМ (Phase):", size=13, bold=True, anchor="end"))
    # Низький рівень -> фронт -> високий рівень -> спад -> низький
    f.append(line(130, top_y + 130, 200, top_y + 130, color=POS, sw=2))
    f.append(line(200, top_y + 130, 200, top_y + 90, color=POS, sw=2))
    f.append(line(200, top_y + 90, 360, top_y + 90, color=POS, sw=2))
    f.append(line(360, top_y + 90, 360, top_y + 130, color=POS, sw=2))
    f.append(line(360, top_y + 130, 500, top_y + 130, color=POS, sw=2))
    f.append(line(500, top_y + 130, 500, top_y + 90, color=POS, sw=2))
    f.append(line(500, top_y + 90, 660, top_y + 90, color=POS, sw=2))
    f.append(line(660, top_y + 90, 660, top_y + 130, color=POS, sw=2))
    f.append(line(660, top_y + 130, 730, top_y + 130, color=POS, sw=2))

    # 3. Реальна напруга / шум комутації (дзвін LC)
    f.append(text(120, top_y + 200, "Шум і комутаційний дзвін:", size=13, bold=True, anchor="end"))
    # Лінія з викидами на фронтах
    f.append(line(130, top_y + 205, 195, top_y + 205, color=LINE, sw=1.5))
    # Дзвін при вмиканні
    f.append(polyline([(195, top_y + 205), (200, top_y + 165), (205, top_y + 235), (210, top_y + 180),
                       (215, top_y + 220), (220, top_y + 195), (225, top_y + 210), (230, top_y + 205)],
                      stroke=POS, sw=2, fill="none"))
    # Тихе вікно
    f.append(line(230, top_y + 205, 355, top_y + 205, color=FIELD, sw=2.5))
    # Дзвін при вимиканні
    f.append(polyline([(355, top_y + 205), (360, top_y + 240), (365, top_y + 175), (370, top_y + 225),
                       (375, top_y + 190), (380, top_y + 215), (385, top_y + 200), (390, top_y + 205)],
                      stroke=POS, sw=2, fill="none"))
    # Тихе вікно під час паузи
    f.append(line(390, top_y + 205, 495, top_y + 205, color=FIELD, sw=2.5))
    # Наступний дзвін
    f.append(polyline([(495, top_y + 205), (500, top_y + 165), (505, top_y + 235), (510, top_y + 180),
                       (515, top_y + 220), (520, top_y + 195), (525, top_y + 210), (530, top_y + 205)],
                      stroke=POS, sw=2, fill="none"))
    f.append(line(530, top_y + 205, 655, top_y + 205, color=FIELD, sw=2.5))

    # Виділення «Тихого вікна»
    f.append(rect(235, top_y + 160, 115, 80, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(292, top_y + 178, "ТИХЕ ВІКНО", size=11, bold=True, color=FIELD))
    f.append(text(292, top_y + 195, "dV/dt = 0", size=10, bold=True, color=FIELD))
    f.append(text(292, top_y + 210, "Дзвін затух", size=10, color=FIELD))

    # Небезпечна зона шуму (асинхронне зчитування)
    f.append(rect(190, top_y + 160, 42, 80, fill="#fdecea", stroke=POS, sw=1, rx=4))
    f.append(text(211, top_y + 252, "Шум di/dt", size=9, bold=True, color=POS))

    # 4. Імпульс тригера TRGO та вікно вибірки АЦП
    f.append(text(120, top_y + 300, "Апаратний тригер TRGO:", size=13, bold=True, anchor="end"))
    f.append(line(130, top_y + 310, 275, top_y + 310, color=LINE, sw=1.5))
    f.append(rect(275, top_y + 285, 10, 25, fill=NEG, stroke=NEG, sw=1))
    f.append(line(285, top_y + 310, 575, top_y + 310, color=LINE, sw=1.5))
    f.append(rect(575, top_y + 285, 10, 25, fill=NEG, stroke=NEG, sw=1))
    f.append(line(585, top_y + 310, 730, top_y + 310, color=LINE, sw=1.5))

    f.append(arrow(280, top_y + 280, 280, top_y + 230, color=NEG, sw=2))
    f.append(text(280, top_y + 265, "Вибірка АЦП строго в центрі!", size=11, bold=True, color=NEG))

    # 5. Підсумковий блок унизу
    f.append(fitbox(30, top_y + 335, 760, 55, "Принцип фазової синхронізації:\nТаймер у режимі Center-Aligned генерує апаратний тригер TRGO строго на вершині рахунку (ARR).\nАЦП фіксує напругу на конденсаторі Sample & Hold у момент, коли всі перехідні процеси затухли.", size=12, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG_DIR, "pwm-adc-sync-timing.svg"), w, h, *f, title="Синхронізація вибірки АЦП за центром імпульсу ШІМ")


def fig_filtering_median_iir():
    """Фігура 4: Порівняння роботи фільтра IIR та комбінованого фільтра Медіана+IIR при наявності викидів."""
    w, h = 820, 450
    f = []

    top_y = 60
    f.append(rect(20, top_y, 780, 370, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    # Лівий графік: Звичайний IIR/EMA розмазує викид
    x1 = 40
    plot_w = 345
    plot_h = 170

    f.append(rect(x1, top_y + 35, plot_w, plot_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(x1 + plot_w / 2, top_y + 25, "Тільки IIR / Експоненційний фільтр (Помилка)", size=12, bold=True, color=POS))

    # Корисний сигнал (істинне значення)
    f.append(line(x1 + 20, top_y + 130, x1 + plot_w - 20, top_y + 130, color=MUTED, sw=1.5, dash="4,3"))
    f.append(text(x1 + 75, top_y + 122, "Істинний сигнал", size=10, color=MUTED))

    # Сирий сигнал із комутаційним глітчем
    raw_pts1 = [(x1 + 20, top_y + 130), (x1 + 70, top_y + 128), (x1 + 120, top_y + 132),
                (x1 + 140, top_y + 130), (x1 + 145, top_y + 50), (x1 + 150, top_y + 130), # Глітч!
                (x1 + 200, top_y + 129), (x1 + 260, top_y + 131), (x1 + 325, top_y + 130)]
    for p in raw_pts1:
        f.append(circle(p[0], p[1], 3, fill=POS, stroke=POS))
    f.append(text(x1 + 155, top_y + 60, "Глітч (+1000 LSB)", size=10, bold=True, color=POS))

    # Вихід IIR (довгий «хвіст» спотворення)
    iir_pts = [(x1 + 20, top_y + 130), (x1 + 140, top_y + 130),
               (x1 + 150, top_y + 75),  # стрибок
               (x1 + 180, top_y + 95),  # повільне затухання
               (x1 + 220, top_y + 112),
               (x1 + 270, top_y + 124),
               (x1 + 325, top_y + 129)]
    f.append(polyline(iir_pts, stroke=POS, sw=2.5, fill="none"))
    f.append(text(x1 + 220, top_y + 90, "Спотворене середнє!", size=10, bold=True, color=POS))

    f.append(fitbox(x1, top_y + 220, plot_w, 95, "Дефект IIR / ковзного середнього:\nОдиночний комутаційний викид повністю потрапляє\nв накопичувач фільтра, зміщуючи середнє значення\nна десятки вибірок уперед. З'являється фазова затримка\nта систематична помилка вимірювання.", size=11, fill="#fdecea", stroke=POS))


    # Правий графік: Каскад Медіана (N=3/5) + IIR
    x2 = 435
    f.append(rect(x2, top_y + 35, plot_w, plot_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(x2 + plot_w / 2, top_y + 25, "Каскад: Медіанний фільтр + IIR (Ідеально)", size=12, bold=True, color=FIELD))

    # Корисний сигнал
    f.append(line(x2 + 20, top_y + 130, x2 + plot_w - 20, top_y + 130, color=MUTED, sw=1.5, dash="4,3"))
    f.append(text(x2 + 75, top_y + 122, "Істинний сигнал", size=10, color=MUTED))

    # Сирі точки з тим самим глітчем
    raw_pts2 = [(x2 + 20, top_y + 130), (x2 + 70, top_y + 128), (x2 + 120, top_y + 132),
                (x2 + 140, top_y + 130), (x2 + 145, top_y + 50), (x2 + 150, top_y + 130),
                (x2 + 200, top_y + 129), (x2 + 260, top_y + 131), (x2 + 325, top_y + 130)]
    for p in raw_pts2:
        f.append(circle(p[0], p[1], 3, fill=MUTED, stroke=MUTED))

    # Вихід медіанного фільтра (глітч зрізано в нуль)
    med_pts = [(x2 + 20, top_y + 130), (x2 + 70, top_y + 129), (x2 + 120, top_y + 131),
               (x2 + 140, top_y + 130), (x2 + 150, top_y + 130), # глітч видалено!
               (x2 + 200, top_y + 130), (x2 + 260, top_y + 130), (x2 + 325, top_y + 130)]
    f.append(polyline(med_pts, stroke=FIELD, sw=2.5, fill="none"))
    f.append(text(x2 + 145, top_y + 60, "Викид відкинуто медіаною", size=10, bold=True, color=FIELD))

    f.append(fitbox(x2, top_y + 220, plot_w, 95, "Перевага каскадного фільтра:\n1. 3-точковий медіанний фільтр повністю знищує\n   одиночні викиди без зміни фази та амплітуди.\n2. Наступний IIR-каскад спокійно згладжує\n   залишковий тепловий гауссів шум АЦП.", size=11, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(IMG_DIR, "glitch-filtering-median-iir.svg"), w, h, *f, title="Робота цифрових фільтрів під дією комутаційних викидів")


if __name__ == "__main__":
    fig_coupling_mechanisms()
    fig_pcb_grounding()
    fig_pwm_adc_sync_timing()
    fig_filtering_median_iir()
    print("Всі SVG-фігури згенеровано успішно.")
