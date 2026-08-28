# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Зациклення, тремтіння й тупик у логіці цілей»."""

import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від root/sys/sys-dron/<slug>/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def make_chattering_hysteresis():
    """Фігура 1: Фазовий простір тремтіння (Chattering) та усунення через гістерезис і Dwell-таймер."""
    w, h = 900, 520
    frags = []

    frags.append(text(w / 2, 26, "Тремтіння логіки (Chattering) та фільтрація через гістерезис і Dwell-таймер", size=15, bold=True))

    # Ліва половина: Наївне перемикання з одним порогом (Chattering)
    panel1_x, panel1_y, panel1_w, panel1_h = 40, 55, 395, 415
    frags.append(rect(panel1_x, panel1_y, panel1_w, panel1_h, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    frags.append(text(panel1_x + panel1_w / 2, panel1_y + 24, "Наївний автомат: один поріг (Тремтіння)", size=13, bold=True, color=POS))

    # Графік сигналу 1
    g1_x, g1_y, g1_w, g1_h = panel1_x + 45, panel1_y + 45, 320, 140
    frags.append(arrow(g1_x, g1_y + g1_h, g1_x + g1_w + 10, g1_y + g1_h, color=INK, sw=1.5))
    frags.append(arrow(g1_x, g1_y + g1_h, g1_x, g1_y - 10, color=INK, sw=1.5))
    frags.append(text(g1_x + g1_w - 5, g1_y + g1_h + 20, "Час t", size=11, color=INK))
    frags.append(text(g1_x - 10, g1_y + 10, "Сигнал S(t)", size=10, color=INK, anchor="end"))

    # Поріг
    th1_y = g1_y + 65
    frags.append(line(g1_x, th1_y, g1_x + g1_w, th1_y, color=POS, sw=1.5, dash="4,3"))
    frags.append(text(g1_x + g1_w - 5, th1_y - 8, "Поріг S_th", size=10, bold=True, color=POS, anchor="end"))

    # Траєкторія шуму навколо порогу
    noisy_pts = [
        (g1_x + 10, g1_y + 120),
        (g1_x + 40, g1_y + 100),
        (g1_x + 70, g1_y + 78),
        (g1_x + 95, th1_y - 12),
        (g1_x + 115, th1_y + 14),
        (g1_x + 135, th1_y - 15),
        (g1_x + 155, th1_y + 12),
        (g1_x + 175, th1_y - 16),
        (g1_x + 195, th1_y + 14),
        (g1_x + 215, th1_y - 10),
        (g1_x + 240, g1_y + 35),
        (g1_x + 280, g1_y + 20),
        (g1_x + 310, g1_y + 15),
    ]
    for i in range(len(noisy_pts) - 1):
        x1, y1 = noisy_pts[i]
        x2, y2 = noisy_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color="#475569", sw=2))

    # Зона шуму
    frags.append(rect(g1_x + 85, th1_y - 20, 145, 40, fill="#fdecea", stroke=POS, sw=1, rx=4))
    frags.append(text(g1_x + 157, th1_y - 24, "Шум сенсора ±3σ", size=9, bold=True, color=POS))

    # Графік дискретного стану 1 (високочастотне перемикання)
    s1_y = g1_y + g1_h + 45
    s1_h = 70
    frags.append(arrow(g1_x, s1_y + s1_h, g1_x + g1_w + 10, s1_y + s1_h, color=INK, sw=1.5))
    frags.append(arrow(g1_x, s1_y + s1_h, g1_x, s1_y - 10, color=INK, sw=1.5))
    frags.append(text(g1_x - 10, s1_y + 15, "Цільовий стан", size=10, color=INK, anchor="end"))
    frags.append(text(g1_x - 8, s1_y + 22, "1: TRACK", size=9, color=POS, bold=True, anchor="end"))
    frags.append(text(g1_x - 8, s1_y + s1_h - 4, "0: SEARCH", size=9, color=MUTED, bold=True, anchor="end"))

    # Сходинки тремтіння
    step1_pts = [
        (g1_x, s1_y + s1_h),
        (g1_x + 95, s1_y + s1_h),
        (g1_x + 95, s1_y + 15),
        (g1_x + 115, s1_y + 15),
        (g1_x + 115, s1_y + s1_h),
        (g1_x + 135, s1_y + s1_h),
        (g1_x + 135, s1_y + 15),
        (g1_x + 155, s1_y + 15),
        (g1_x + 155, s1_y + s1_h),
        (g1_x + 175, s1_y + s1_h),
        (g1_x + 175, s1_y + 15),
        (g1_x + 195, s1_y + 15),
        (g1_x + 195, s1_y + s1_h),
        (g1_x + 215, s1_y + s1_h),
        (g1_x + 215, s1_y + 15),
        (g1_x + 310, s1_y + 15),
    ]
    for i in range(len(step1_pts) - 1):
        x1, y1 = step1_pts[i]
        x2, y2 = step1_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # Підпис патології
    frags.append(rect(panel1_x + 15, panel1_y + panel1_h - 75, panel1_w - 30, 60, fill="#fff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(panel1_x + panel1_w / 2, panel1_y + panel1_h - 55, "Патологія: 15..30 перемикань/с (Chattering)", size=10, bold=True, color=POS))
    frags.append(text(panel1_x + panel1_w / 2, panel1_y + panel1_h - 38, "Перегрів сервоприводів підвісу, зрив планера,", size=9, color=INK))
    frags.append(text(panel1_x + panel1_w / 2, panel1_y + panel1_h - 24, "стрибки струму живлення та розряд АКБ", size=9, color=INK))

    # Права половина: Подвійний поріг + Dwell-таймер (Стійка робота)
    panel2_x, panel2_y, panel2_w, panel2_h = 465, 55, 395, 415
    frags.append(rect(panel2_x, panel2_y, panel2_w, panel2_h, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(panel2_x + panel2_w / 2, panel2_y + 24, "Захищений автомат: Гістерезис + Dwell (Норма)", size=13, bold=True, color=FIELD))

    # Графік сигналу 2
    g2_x, g2_y, g2_w, g2_h = panel2_x + 45, panel2_y + 45, 320, 140
    frags.append(arrow(g2_x, g2_y + g2_h, g2_x + g2_w + 10, g2_y + g2_h, color=INK, sw=1.5))
    frags.append(arrow(g2_x, g2_y + g2_h, g2_x, g2_y - 10, color=INK, sw=1.5))
    frags.append(text(g2_x + g2_w - 5, g2_y + g2_h + 20, "Час t", size=11, color=INK))
    frags.append(text(g2_x - 10, g2_y + 10, "Сигнал S(t)", size=10, color=INK, anchor="end"))

    # Дві лінії порогів гістерезису
    th_hi_y = g2_y + 50
    th_lo_y = g2_y + 85
    frags.append(line(g2_x, th_hi_y, g2_x + g2_w, th_hi_y, color=FIELD, sw=1.5, dash="4,3"))
    frags.append(text(g2_x + g2_w - 5, th_hi_y - 6, "S_on (верхній)", size=10, bold=True, color=FIELD, anchor="end"))

    frags.append(line(g2_x, th_lo_y, g2_x + g2_w, th_lo_y, color=NEG, sw=1.5, dash="4,3"))
    frags.append(text(g2_x + g2_w - 5, th_lo_y + 14, "S_off (нижній)", size=10, bold=True, color=NEG, anchor="end"))

    # Смуга гістерезису
    frags.append(rect(g2_x, th_hi_y, g2_w, th_lo_y - th_hi_y, fill="#e8f5e9", stroke="#a5d6a7", sw=1, rx=0))
    frags.append(text(g2_x + 110, (th_hi_y + th_lo_y) / 2 + 4, "Петля гістерезису ΔH ≥ 6σ", size=10, bold=True, color="#2e7d32"))

    # Та сама траєкторія сигналу
    for i in range(len(noisy_pts) - 1):
        x1, y1 = noisy_pts[i]
        x2, y2 = noisy_pts[i + 1]
        frags.append(line(x1 + (panel2_x - panel1_x), y1, x2 + (panel2_x - panel1_x), y2, color="#475569", sw=2))

    # Маркер точки спрацювання S_on
    trig_x = g2_x + 240
    frags.append(circle(trig_x, g2_y + 35, 4, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(line(trig_x, g2_y + 35, trig_x, g2_y + g2_h + 45 + s1_h, color=FIELD, sw=1.2, dash="3,3"))
    frags.append(text(trig_x + 8, th_hi_y - 12, "Спрацювання S_on", size=9, bold=True, color=FIELD, anchor="start"))

    # Графік дискретного стану 2 (чіткий одиночний перехід)
    s2_y = g2_y + g2_h + 45
    s2_h = 70
    frags.append(arrow(g2_x, s2_y + s2_h, g2_x + g2_w + 10, s2_y + s2_h, color=INK, sw=1.5))
    frags.append(arrow(g2_x, s2_y + s2_h, g2_x, s2_y - 10, color=INK, sw=1.5))
    frags.append(text(g2_x - 10, s2_y + 15, "Цільовий стан", size=10, color=INK, anchor="end"))
    frags.append(text(g2_x - 8, s2_y + 22, "1: TRACK", size=9, color=FIELD, bold=True, anchor="end"))
    frags.append(text(g2_x - 8, s2_y + s2_h - 4, "0: SEARCH", size=9, color=MUTED, bold=True, anchor="end"))

    # Одиночна сходинка
    step2_pts = [
        (g2_x, s2_y + s2_h),
        (trig_x, s2_y + s2_h),
        (trig_x, s2_y + 15),
        (g2_x + 310, s2_y + 15),
    ]
    for i in range(len(step2_pts) - 1):
        x1, y1 = step2_pts[i]
        x2, y2 = step2_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=FIELD, sw=2.5))

    # Вікно утримання Dwell Timer
    frags.append(rect(trig_x, s2_y + 15, 60, s2_h - 15, fill="#dcfce7", stroke=FIELD, sw=1, rx=2))
    frags.append(text(trig_x + 30, s2_y + 45, "T_dwell", size=9, bold=True, color=FIELD))

    # Підпис результату
    frags.append(rect(panel2_x + 15, panel2_y + panel2_h - 75, panel2_w - 30, 60, fill="#fff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(panel2_x + panel2_w / 2, panel2_y + panel2_h - 55, "Результат: 0 брязкоту, детермінований перехід", size=10, bold=True, color=FIELD))
    frags.append(text(panel2_x + panel2_w / 2, panel2_y + panel2_h - 38, "Шум у смузі ΔH не змінює стан автопілота,", size=9, color=INK))
    frags.append(text(panel2_x + panel2_w / 2, panel2_y + panel2_h - 24, "Dwell-таймер гарантує f_switch ≤ 1 / T_dwell", size=9, color=INK))

    # Загальний статус внизу
    frags.append(rect(40, 480, 820, 32, fill="#f8fafc", stroke="#64748b", sw=1, rx=4))
    frags.append(text(w / 2, 500, "Математичний критерій: смуга гістерезису ΔH = S_on − S_off > 6σ_noise запобігає 99.7% хибних перемикань.", size=10, bold=True, color="#334155"))

    render(os.path.join(OUT_DIR, "target-chattering-hysteresis.svg"), w, h, *frags)


def make_cycle_deadlock_detection():
    """Фігура 2: Виявлення зациклень дій (Cycle Lock) та ієрархія розв'язання тупика (Deadlock)."""
    w, h = 900, 500
    frags = []

    frags.append(text(w / 2, 26, "Виявлення зациклень логіки дій та багаторівнева ескалація виходу з тупика", size=15, bold=True))

    # Лівий блок: Граф циклу дій (Cycle Lock)
    col1_x, col1_y, col1_w, col1_h = 40, 55, 410, 425
    frags.append(rect(col1_x, col1_y, col1_w, col1_h, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    frags.append(text(col1_x + col1_w / 2, col1_y + 24, "Виявлення замкненого циклу дій (Cycle Lock)", size=13, bold=True, color=POS))

    # 3 вузли циклу дій (A -> B -> C -> A)
    nA_x, nA_y = col1_x + 95, col1_y + 110
    nB_x, nB_y = col1_x + 315, col1_y + 110
    nC_x, nC_y = col1_x + 205, col1_y + 225

    box_w, box_h = 130, 44
    frags.append(fitbox(nA_x - box_w / 2, nA_y - box_h / 2, box_w, box_h, "Дія A:\nОбхід зліва", size=11, bold=True, fill="#fdecea", stroke=POS))
    frags.append(fitbox(nB_x - box_w / 2, nB_y - box_h / 2, box_w, box_h, "Дія B:\nВихід на коридор", size=11, bold=True, fill="#fef9e7", stroke="#b7791f"))
    frags.append(fitbox(nC_x - box_w / 2, nC_y - box_h / 2, box_w, box_h, "Дія C:\nКурс на ціль", size=11, bold=True, fill="#eaf0fd", stroke=NEG))

    # Стрілки циклу
    frags.append(arrow(nA_x + box_w / 2, nA_y, nB_x - box_w / 2, nB_y, color=POS, sw=2))
    frags.append(text((nA_x + nB_x) / 2, nA_y - 8, "Умова 1: Завада праворуч", size=9, color=INK))

    frags.append(arrow(nB_x, nB_y + box_h / 2, nC_x + box_w / 3, nC_y - box_h / 2, color=POS, sw=2))
    frags.append(text(nB_x - 10, (nB_y + nC_y) / 2 + 10, "Умова 2: Межа геозони", size=9, color=INK))

    frags.append(arrow(nC_x - box_w / 3, nC_y - box_h / 2, nA_x, nA_y + box_h / 2, color=POS, sw=2))
    frags.append(text(nA_x - 10, (nA_y + nC_y) / 2 + 10, "Умова 3: Кут на ціль", size=9, color=INK))

    # Центр циклу: Попередження про зациклення
    frags.append(circle(col1_x + 205, col1_y + 140, 24, fill="#fee2e2", stroke=POS, sw=1.8))
    frags.append(text(col1_x + 205, col1_y + 137, "A→B→C", size=9, bold=True, color=POS))
    frags.append(text(col1_x + 205, col1_y + 148, "Цикл!", size=9, bold=True, color=POS))

    # Кільцевий буфер історій станів (Ring Buffer)
    frags.append(rect(col1_x + 15, col1_y + 265, col1_w - 30, 70, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    frags.append(text(col1_x + col1_w / 2, col1_y + 282, "Кільцевий буфер просторово-часових підписів", size=10, bold=True, color=INK))

    # Осередки буфера
    buf_x0 = col1_x + 25
    buf_y0 = col1_y + 292
    cells = ["(A, g1)", "(B, g2)", "(C, g3)", "(A, g1)", "(B, g2)", "(C, g3)"]
    cw, ch = 56, 30
    for i, c_label in enumerate(cells):
        cx = buf_x0 + i * 60
        is_repeat = i >= 3
        c_fill = "#fdecea" if is_repeat else "#ffffff"
        c_stroke = POS if is_repeat else "#94a3b8"
        frags.append(rect(cx, buf_y0, cw, ch, fill=c_fill, stroke=c_stroke, sw=1.2, rx=3))
        frags.append(text(cx + cw / 2, buf_y0 + 19, c_label, size=9, bold=is_repeat, color=POS if is_repeat else INK))

    # Підпис детектора N-грам
    frags.append(rect(col1_x + 15, col1_y + 345, col1_w - 30, 68, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(col1_x + col1_w / 2, col1_y + 363, "Детектор: N-грамний збіг підписів (N ≥ 3)", size=10, bold=True, color=POS))
    frags.append(text(col1_x + col1_w / 2, col1_y + 380, "Хеш стану: H = hash(State_ID, ⌊x/Δx⌋, ⌊y/Δy⌋)", size=9, color=INK))
    frags.append(text(col1_x + col1_w / 2, col1_y + 396, "Фіксація зациклення активує контур ескалації ➔", size=9, bold=True, color=POS))

    # Правий блок: Ієрархія виходу з глухих кутів (Recovery Escalation)
    col2_x, col2_y, col2_w, col2_h = 470, 55, 390, 425
    frags.append(rect(col2_x, col2_y, col2_w, col2_h, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(col2_x + col2_w / 2, col2_y + 24, "Ієрархія ескалації виходу з тупика (Recovery)", size=13, bold=True, color=FIELD))

    # 4 рівні ескалації
    escalations = [
        ("Рівень 1: Стохастичне збурення", "Додавання випадкового вектору швидкості v_rand\nабо кутового зсуву курсу ±30°", "#f0fdf4", FIELD),
        ("Рівень 2: Віртуальна перешкода", "Динамічне внесення зони зациклення до карти вартостей\n(Costmap Inflation) як забороненого вокселя", "#fef9e7", "#b7791f"),
        ("Рівень 3: 3D маневр зміни ешелону", "Стрибок висоти Δz = +15 м для руйнування площинної\nсиметрії локальних мінімумів потенціального поля", "#eff6ff", NEG),
        ("Рівень 4: Аварійний скид на Loiter / RTL", "Переривання поточної цілі, перехід у режим зависання\nабо повернення на запасну точку безпеки (Rally)", "#fdecea", POS),
    ]

    esc_y0 = col2_y + 48
    esc_h = 78
    for i, (head_lbl, desc_lbl, bg_c, str_c) in enumerate(escalations):
        ey = esc_y0 + i * 88
        frags.append(rect(col2_x + 15, ey, col2_w - 30, esc_h, fill=bg_c, stroke=str_c, sw=1.5, rx=6))
        frags.append(text(col2_x + 25, ey + 20, head_lbl, size=11, bold=True, color=str_c, anchor="start"))
        lines_desc = desc_lbl.split("\n")
        frags.append(text(col2_x + 25, ey + 40, lines_desc[0], size=9, color=INK, anchor="start"))
        frags.append(text(col2_x + 25, ey + 56, lines_desc[1], size=9, color=MUTED, anchor="start"))
        
        # Стрілка переходу вниз між рівнями
        if i < len(escalations) - 1:
            frags.append(arrow(col2_x + col2_w - 35, ey + esc_h, col2_x + col2_w - 35, ey + esc_h + 10, color=str_c, sw=1.5))

    render(os.path.join(OUT_DIR, "goal-cycle-and-deadlock-detection.svg"), w, h, *frags)


if __name__ == '__main__':
    make_chattering_hysteresis()
    make_cycle_deadlock_detection()
    print("SVG figures generated successfully.")
