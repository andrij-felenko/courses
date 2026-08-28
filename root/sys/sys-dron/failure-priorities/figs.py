# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Пріоритети відмов» (failure-priorities)."""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def make_priority_matrix():
    """Фігура 1: Конвеєр пріоритетного арбітражу аварійних станів автопілота."""
    w, h = 880, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Конвеєр пріоритетного арбітражу аварійних ситуацій", size=16, bold=True))

    # Стовпець 1: Вхідні прапорці відмов (Health Watchdogs)
    col1_x = 110
    frags.append(text(col1_x, 65, "Детектори відмов", size=13, bold=True, color=INK))
    
    # Блоки відмов
    failures = [
        ("Втрата зв'язку RC / GCS", "#eaf0fd", NEG),
        ("Низький заряд батареї (30%)", "#fef9e7", "#b7791f"),
        ("Глушіння GNSS / збій EKF", "#fef9e7", "#b7791f"),
        ("Критичний розряд (<10%)", "#fdecea", POS),
        ("Втрата просторового контролю", "#fdecea", POS),
    ]
    
    box_w, box_h = 180, 44
    box_ys = []
    for i, (label, fill_c, stroke_c) in enumerate(failures):
        by = 100 + i * 65
        box_ys.append(by)
        frags.append(fitbox(col1_x - box_w / 2, by - box_h / 2, box_w, box_h, label, size=12, bold=True, fill=fill_c, stroke=stroke_c, pad=4))

    # Стовпець 2: Блок арбітражу (Priority Arbiter)
    arb_cx, arb_cy = 380, 230
    arb_w, arb_h = 200, 310
    frags.append(rect(arb_cx - arb_w / 2, arb_cy - arb_h / 2, arb_w, arb_h, fill="#f8fafc", stroke="#475569", sw=2, rx=8))
    frags.append(text(arb_cx, arb_cy - 125, "Пріоритетний арбітр", size=14, bold=True, color=INK))
    frags.append(text(arb_cx, arb_cy - 105, "(таблиця ваг і рангів)", size=11, color=MUTED))

    # Лінії-стрілки від входів до арбітра
    for by in box_ys:
        frags.append(arrow(col1_x + box_w / 2, by, arb_cx - arb_w / 2, by, color="#64748b", sw=1.5))

    # Вміст арбітра: ієрархія ваг
    ladder = [
        ("Ранг 0: FTS / Парашут", POS),
        ("Ранг 1: Emergency Land", POS),
        ("Ранг 2: Geofence Breach", "#b7791f"),
        ("Ранг 3: Low Battery RTL", "#b7791f"),
        ("Ранг 4: RC Loss Action", NEG),
        ("Ранг 5: Sensor Degradation", MUTED),
    ]
    for i, (txt, c) in enumerate(ladder):
        ly = arb_cy - 75 + i * 36
        frags.append(rect(arb_cx - 85, ly - 13, 170, 26, fill=BG, stroke=c, sw=1.2, rx=4))
        frags.append(text(arb_cx, ly + 4, txt, size=11, bold=True, color=c))

    # Стовпець 3: Фільтр сенсорної здійсненності (Feasibility & Capabilities)
    feas_cx, feas_cy = 620, 230
    feas_w, feas_h = 160, 240
    frags.append(rect(feas_cx - feas_w / 2, feas_cy - feas_h / 2, feas_w, feas_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(feas_cx, feas_cy - 92, "Сенсорна", size=13, bold=True, color=FIELD))
    frags.append(text(feas_cx, feas_cy - 74, "здійсненність", size=13, bold=True, color=FIELD))
    frags.append(text(feas_cx, feas_cy - 52, "Перевірка 3D-позиції,", size=10, color=INK))
    frags.append(text(feas_cx, feas_cy - 38, "висоти та орієнтації", size=10, color=INK))

    frags.append(rect(feas_cx - 68, feas_cy - 15, 136, 44, fill=BG, stroke=FIELD, sw=1, rx=4))
    frags.append(text(feas_cx, feas_cy + 2, "RTL без GNSS ➔", size=10, color=POS, bold=True))
    frags.append(text(feas_cx, feas_cy + 18, "деградація до Land", size=10, color=POS, bold=True))

    frags.append(rect(feas_cx - 68, feas_cy + 42, 136, 44, fill=BG, stroke=FIELD, sw=1, rx=4))
    frags.append(text(feas_cx, feas_cy + 59, "Land без барометра ➔", size=10, color=POS, bold=True))
    frags.append(text(feas_cx, feas_cy + 75, "фіксований газ / FTS", size=10, color=POS, bold=True))

    # Стрілка між арбітром та здійсненністю
    frags.append(arrow(arb_cx + arb_w / 2, arb_cy, feas_cx - feas_w / 2, feas_cy, color="#64748b", sw=1.8))

    # Стовпець 4: Результуюча дія (Executive Dispatch)
    out_cx, out_cy = 795, 230
    frags.append(arrow(feas_cx + feas_w / 2, feas_cy, out_cx - 45, out_cy, color=FIELD, sw=2.2))
    
    frags.append(fitbox(out_cx - 50, out_cy - 55, 110, 110, "Атомарна\nбезпечна\nдія\n(Dispatch)", size=12, bold=True, fill="#fef2f2", stroke=POS, sw=2, pad=4))

    # Пояснювальний статус внизу
    frags.append(rect(50, 415, 780, 45, fill="#faf5ff", stroke="#9333ea", sw=1.2, rx=6))
    frags.append(text(440, 435, "Правило витіснення: аварія рангу 1 (Critical Battery) негайно перериває RTL (ранг 3),", size=11, bold=True, color="#6b21a8"))
    frags.append(text(440, 449, "а відсутність GNSS-фіксу деградує навігаційні маневри до керованої посадки на місці.", size=11, color="#6b21a8"))

    render(os.path.join(OUT_DIR, "priority-arbitration-matrix.svg"), w, h, *frags)


def make_timeline():
    """Фігура 2: Часова шкала конфлікту дій та витіснення менш пріоритетного стану."""
    w, h = 880, 400
    frags = []

    frags.append(text(w / 2, 28, "Хронологія виникнення аварій та витіснення станів (Preemption)", size=16, bold=True))

    # Часова вісь
    ax_x1, ax_x2, ax_y = 70, 810, 320
    frags.append(arrow(ax_x1, ax_y, ax_x2, ax_y, color=INK, sw=2))
    frags.append(text(ax_x2 - 15, ax_y + 25, "Час (с)", size=12, bold=True, color=INK))

    # Позначки часу на осі
    time_marks = [
        (0, 90, "0 с\nСтарт місії"),
        (5, 230, "5 с\nВтрата RC"),
        (7, 330, "7 с\nПідтвердж. RC"),
        (15, 480, "15 с\nГлушіння GNSS"),
        (20, 620, "20 с\nCritical Bat"),
        (28, 770, "28 с\nТоркання"),
    ]

    for t_val, tx, t_lbl in time_marks:
        frags.append(line(tx, ax_y - 6, tx, ax_y + 6, color=INK, sw=1.5))
        frags.append(mtext(tx, ax_y + 20, t_lbl, size=10, color=INK))

    # Смуги активних режимів автопілота
    row_y = 100
    
    # 1. Нормальна місія
    frags.append(rect(90, row_y - 25, 240, 50, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(210, row_y + 4, "MISSION (Політ за маршрутом)", size=11, bold=True, color=FIELD))

    # 2. RC Failsafe RTL
    frags.append(rect(330, row_y - 25, 290, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(475, row_y - 6, "RC FAILSAFE: RTL", size=11, bold=True, color=NEG))
    frags.append(text(475, row_y + 12, "(Набір висоти та повернення)", size=10, color=NEG))

    # 3. Emergency Land (Critical Battery)
    frags.append(rect(620, row_y - 25, 150, 50, fill="#fdecea", stroke=POS, sw=2, rx=6))
    frags.append(text(695, row_y - 6, "EMERGENCY LAND", size=11, bold=True, color=POS))
    frags.append(text(695, row_y + 12, "(Вертикальна посадка)", size=10, color=POS))

    # Події знизу (y = 190..238) зі стрілками ВГОРУ до часової шкали режимів (y = 125)
    # Подія 1: Обрив RC
    frags.append(fitbox(170, 190, 120, 48, "Обрив RC-лінку\n(таймаут 2.0 с)", size=10, fill="#f8fafc", stroke=NEG, pad=2))
    frags.append(arrow(230, 190, 330, row_y + 25, color=NEG, sw=1.5))

    # Подія 2: Глушіння GNSS
    frags.append(fitbox(420, 190, 120, 48, "Глушіння GNSS\n(деградація RTL)", size=10, fill="#fffbeb", stroke="#b7791f", pad=2))
    frags.append(line(480, 190, 480, row_y + 25, color="#b7791f", sw=1.5, dash="4,3"))

    # Подія 3: Critical Battery + Preemption
    frags.append(fitbox(555, 190, 130, 48, "Критична напруга!\n(Витіснення RTL)", size=10, bold=True, fill="#fdecea", stroke=POS, pad=2))
    frags.append(arrow(620, 190, 620, row_y + 25, color=POS, sw=2.2))

    # Маркер незворотності (Latch)
    frags.append(rect(630, 255, 140, 36, fill="#faf5ff", stroke="#9333ea", sw=1, rx=4))
    frags.append(text(700, 277, "Фіксація (Latch): не повертати RTL", size=9, bold=True, color="#6b21a8"))

    render(os.path.join(OUT_DIR, "action-preemption-timeline.svg"), w, h, *frags)


if __name__ == '__main__':
    make_priority_matrix()
    make_timeline()
    print("SVG generated successfully.")
