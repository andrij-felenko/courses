# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Таймаут на кожну поведінку» (taimaut-na-kozhnu-povedinku)."""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def make_timeout_pipeline():
    """Фігура 1: Тривимірний конвеєр контролю таймаутів поведінки."""
    w, h = 900, 470
    frags = []

    frags.append(text(w / 2, 28, "Тривимірний конвеєр моніторингу життєвого циклу поведінки", size=16, bold=True))

    # Стовпець 1: Джерела вимірювань (Сенсори та системні годинники)
    col1_x = 115
    frags.append(text(col1_x, 65, "Джерела метрик", size=13, bold=True, color=INK))

    sources = [
        ("Монотонний таймер\n(CLOCK_MONOTONIC)", "#f8fafc", "#475569"),
        ("Оцінка EKF: позиція,\nшвидкість і коваріація", "#eff6ff", NEG),
        ("Стан шини живлення:\nнапруга, струм і SoC", "#fefce8", "#ca8a04"),
    ]

    s_box_w, s_box_h = 190, 56
    s_ys = [120, 220, 320]
    for i, (label, fill_c, stroke_c) in enumerate(sources):
        by = s_ys[i]
        frags.append(fitbox(col1_x - s_box_w / 2, by - s_box_h / 2, s_box_w, s_box_h, label, size=11, bold=True, fill=fill_c, stroke=stroke_c, pad=4))

    # Стовпець 2: Три незалежні компаратори таймаутів
    col2_x = 380
    frags.append(text(col2_x, 65, "Рівні контролю таймауту", size=13, bold=True, color=INK))

    levels = [
        ("Жорсткий таймаут (Hard Deadline)", "t_elapsed > T_hard_max\nПримусовий аварійний вихід", "#fee2e2", POS),
        ("М'який наглядач поступу (Progress Watchdog)", "v_prog < v_min або ΔP_cov > σ_max\nВиявлення буксування та стагнації", "#eff6ff", NEG),
        ("Енергетичний ліміт (Energy Budget)", "E_rem - E_RTL(d_home) ≤ E_reserve\nТочка неповернення за зарядом", "#fef9c3", "#a16207"),
    ]

    c_box_w, c_box_h = 280, 68
    for i, (head, desc, fill_c, stroke_c) in enumerate(levels):
        by = s_ys[i]
        # Стрілка від джерела до компаратора
        frags.append(arrow(col1_x + s_box_w / 2, by, col2_x - c_box_w / 2, by, color="#64748b", sw=1.6))
        
        # Блок компаратора
        bx, by_top = col2_x - c_box_w / 2, by - c_box_h / 2
        frags.append(rect(bx, by_top, c_box_w, c_box_h, fill=fill_c, stroke=stroke_c, sw=1.6, rx=6))
        frags.append(text(col2_x, by - 12, head, size=11, bold=True, color=stroke_c))
        frags.append(mtext(col2_x, by + 6, desc, size=10, color=INK, lh=1.25))

    # Стовпець 3: Модуль арбітражу та формування сигналів тривоги
    col3_x = 650
    frags.append(text(col3_x, 65, "Арбітр тривог", size=13, bold=True, color=INK))

    arb_w, arb_h = 170, 270
    arb_cx, arb_cy = col3_x, 220
    frags.append(rect(arb_cx - arb_w / 2, arb_cy - arb_h / 2, arb_w, arb_h, fill="#faf5ff", stroke="#7e22ce", sw=1.8, rx=8))
    frags.append(text(arb_cx, arb_cy - 105, "Behavior", size=13, bold=True, color="#6b21a8"))
    frags.append(text(arb_cx, arb_cy - 88, "Watchdog Arbiter", size=13, bold=True, color="#6b21a8"))
    frags.append(text(arb_cx, arb_cy - 65, "Обчислення типу події:", size=10, color=INK))

    events = [
        ("• TIME_EXPIRED", POS),
        ("• STAGNATION", NEG),
        ("• SENSOR_DRIFT", MUTED),
        ("• LOW_ENERGY", "#a16207"),
    ]
    for j, (ev, col) in enumerate(events):
        frags.append(text(arb_cx, arb_cy - 38 + j * 24, ev, size=10, bold=True, color=col))

    frags.append(rect(arb_cx - 72, arb_cy + 70, 144, 46, fill=BG, stroke="#7e22ce", sw=1, rx=4))
    frags.append(text(arb_cx, arb_cy + 87, "Генерація сигналу", size=10, bold=True, color="#6b21a8"))
    frags.append(text(arb_cx, arb_cy + 103, "переривання поведінки", size=10, color=INK))

    # Стрілки від трьох рівнів до арбітра
    for by in s_ys:
        frags.append(arrow(col2_x + c_box_w / 2, by, arb_cx - arb_w / 2, by, color="#7e22ce", sw=1.5))

    # Стовпець 4: Вихідний диспетчер ескалації
    col4_x = 825
    frags.append(arrow(arb_cx + arb_w / 2, arb_cy, col4_x - 45, arb_cy, color="#7e22ce", sw=2.2))
    frags.append(fitbox(col4_x - 45, arb_cy - 50, 95, 100, "Диспетчер\nескалації\n(Escalation\nCascade)", size=11, bold=True, fill="#fef2f2", stroke=POS, sw=2, pad=4))

    # Пояснювальний статус у підвалі
    frags.append(rect(45, 395, 810, 52, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(450, 416, "Принцип раннього відсікання: енергетичний таймаут або фіксація буксування", size=11, bold=True, color=INK))
    frags.append(text(450, 432, "переривають завислу дію задовго до вичерпання повного жорсткого ліміту часу.", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "timeout-monitoring-pipeline.svg"), w, h, *frags)


def make_escalation_ladder():
    """Фігура 2: Дерево та каскад ескалації дій після спрацювання таймауту."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 28, "Каскад ескалації дій автопілота при зриві таймауту", size=16, bold=True))

    # Початковий стан: Спрацювання таймауту
    start_x, start_y = 90, 230
    frags.append(fitbox(start_x - 70, start_y - 45, 140, 90, "Сигнал таймауту\n(Watchdog\nTimeout Event)", size=11, bold=True, fill="#fee2e2", stroke=POS, sw=2, pad=4))

    # Рівень 1: Retry & Relaxation (Спроба з пом'якшенням умов)
    r1_x, r1_y = 345, 115
    frags.append(arrow(start_x + 70, start_y - 25, r1_x - 85, r1_y + 15, color="#475569", sw=1.6))
    frags.append(fitbox(175, 130, 75, 24, "Спроби < N", size=9, bold=True, fill="#f0fdf4", stroke=FIELD, pad=2))

    r1_w, r1_h = 170, 95
    frags.append(rect(r1_x - r1_w / 2, r1_y - r1_h / 2, r1_w, r1_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(r1_x, r1_y - 28, "Рівень 1: Retry & Relax", size=11, bold=True, color=FIELD))
    frags.append(text(r1_x, r1_y - 10, "• Розширення acceptance radius", size=9.5, color=INK))
    frags.append(text(r1_x, r1_y + 8, "• Зміна ракурсу камери", size=9.5, color=INK))
    frags.append(text(r1_x, r1_y + 26, "• Перезапуск пошуку мітки", size=9.5, color=INK))

    # Рівень 2: Fallback (Запасна поведінка)
    r2_x, r2_y = 345, 345
    frags.append(arrow(start_x + 70, start_y + 25, r2_x - 85, r2_y - 15, color="#475569", sw=1.6))
    frags.append(fitbox(175, 305, 75, 24, "Спроби = max", size=9, bold=True, fill="#fee2e2", stroke=POS, pad=2))

    r2_w, r2_h = 170, 95
    frags.append(rect(r2_x - r2_w / 2, r2_y - r2_h / 2, r2_w, r2_h, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(r2_x, r2_y - 28, "Рівень 2: Fallback", size=11, bold=True, color=NEG))
    frags.append(text(r2_x, r2_y - 10, "• Пропуск точки (Skip WP)", size=9.5, color=INK))
    frags.append(text(r2_x, r2_y + 8, "• Перехід у Loiter / Hold", size=9.5, color=INK))
    frags.append(text(r2_x, r2_y + 26, "• Запасний майданчик (Alt LZ)", size=9.5, color=INK))

    # Блок перевірки енергії та сенсорної спроможності
    eval_x, eval_y = 595, 230
    eval_w, eval_h = 165, 130
    frags.append(rect(eval_x - eval_w / 2, eval_y - eval_h / 2, eval_w, eval_h, fill="#f8fafc", stroke="#334155", sw=1.8, rx=6))
    frags.append(text(eval_x, eval_y - 45, "Оцінка безпеки", size=12, bold=True, color=INK))
    frags.append(text(eval_x, eval_y - 28, "та енергії", size=12, bold=True, color=INK))
    frags.append(text(eval_x, eval_y - 4, "Чи вистачає заряду", size=10, color=MUTED))
    frags.append(text(eval_x, eval_y + 12, "на політ додому (RTL)?", size=10, color=MUTED))
    frags.append(text(eval_x, eval_y + 32, "Чи дійсний 3D-фікс?", size=10, color=MUTED))

    # Стрілки від Retry та Fallback до оцінки
    frags.append(arrow(r1_x + r1_w / 2, r1_y + 15, eval_x - eval_w / 2, eval_y - 30, color="#64748b", sw=1.4))
    frags.append(arrow(r2_x + r2_w / 2, r2_y - 15, eval_x - eval_w / 2, eval_y + 30, color="#64748b", sw=1.4))

    # Рівень 3: Аварійне повернення додому (RTL)
    r3_x, r3_y = 855, 120
    frags.append(arrow(eval_x + eval_w / 2, eval_y - 35, r3_x - 90, r3_y + 10, color=FIELD, sw=1.8))
    frags.append(fitbox(690, 130, 68, 24, "Заряд OK", size=9, bold=True, fill="#ecfdf5", stroke=FIELD, pad=2))

    r3_w, r3_h = 180, 80
    frags.append(rect(r3_x - r3_w / 2, r3_y - r3_h / 2, r3_w, r3_h, fill="#ecfdf5", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(r3_x, r3_y - 20, "Рівень 3A: Emergency RTL", size=11, bold=True, color=FIELD))
    frags.append(text(r3_x, r3_y - 2, "Повернення на безпечній висоті", size=9.5, color=INK))
    frags.append(text(r3_x, r3_y + 16, "за прямою траєкторією", size=9.5, color=INK))

    # Рівень 3Б: Негайна аварійна посадка (Forced Emergency Land)
    r4_x, r4_y = 855, 340
    frags.append(arrow(eval_x + eval_w / 2, eval_y + 35, r4_x - 90, r4_y - 10, color=POS, sw=2.0))
    frags.append(fitbox(685, 305, 75, 24, "Дефіцит / збій", size=9, bold=True, fill="#fef2f2", stroke=POS, pad=2))

    r4_w, r4_h = 180, 80
    frags.append(rect(r4_x - r4_w / 2, r4_y - r4_h / 2, r4_w, r4_h, fill="#fef2f2", stroke=POS, sw=2.0, rx=6))
    frags.append(text(r4_x, r4_y - 20, "Рівень 3B: Emergency Land", size=11, bold=True, color=POS))
    frags.append(text(r4_x, r4_y - 2, "Вертикальне кероване зниження", size=9.5, color=INK))
    frags.append(text(r4_x, r4_y + 16, "на поточному місці", size=9.5, color=INK))

    # Підвал
    frags.append(rect(45, 415, 890, 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(490, 434, "Детермінізм реакції: кожна гілка ескалації має гарантований кінцевий стан,", size=11, bold=True, color=INK))
    frags.append(text(490, 449, "що виключає нескінченні цикли очікування та запобігає некерованому розряду батареї.", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "behavior-escalation-ladder.svg"), w, h, *frags)


if __name__ == "__main__":
    make_timeout_pipeline()
    make_escalation_ladder()
    print("Фігури успішно згенеровано.")
