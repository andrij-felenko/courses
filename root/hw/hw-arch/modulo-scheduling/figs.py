# -*- coding: utf-8 -*-
"""Оновлений figs.py із виправленою геометрією."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_loop_execution_modes():
    """Порівняння послідовного виконання, розгортання та Modulo Scheduling."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Порівняння схем виконання циклу: послідовна, розгорнута і Modulo Scheduling", size=15, bold=True))

    # Секція 1: Послідовне виконання
    frags.append(textbox(130, 65, "Послідовне виконання\n(без перекриття)", size=12, pad=6, fill="#f8fafc", bold=True)[0])
    for i in range(3):
        x = 240 + i * 180
        frags.append(rect(x, 50, 160, 32, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(x + 80, 70, "Ітерація %d (5 тактів)" % i, size=11, bold=True))
        if i < 2:
            frags.append(arrow(x + 160, 66, x + 180, 66, color=MUTED, sw=1.2))

    frags.append(text(790, 70, "15 тактів", size=12, color=POS, bold=True, anchor="end"))
    frags.append(line(40, 105, 780, 105, color="#cbd5e1", sw=1, dash="4,4"))

    # Секція 2: Розгортання циклу
    frags.append(textbox(130, 145, "Розгортання циклу\n(Unrolling x3)", size=12, pad=6, fill="#f8fafc", bold=True)[0])
    frags.append(rect(240, 130, 480, 32, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(480, 150, "Об'єднане тіло: 3x Load → 3x Calc → 3x Store (тривалі затримки між стадіями)", size=11, bold=True, color="#92400e"))
    frags.append(text(790, 150, "11 тактів", size=12, color="#b45309", bold=True, anchor="end"))
    frags.append(line(40, 185, 780, 185, color="#cbd5e1", sw=1, dash="4,4"))

    # Секція 3: Modulo Scheduling
    frags.append(textbox(130, 265, "Modulo Scheduling\n(II = 1 такт,\n3 стадії конвеєра)", size=12, pad=6, fill="#eff6ff", stroke=NEG, bold=True)[0])

    frags.append(rect(240, 210, 120, 110, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(300, 230, "ПРОЛОГ", size=12, bold=True, color=POS))
    frags.append(text(300, 255, "Такт 0: Iter0 (L)", size=10))
    frags.append(text(300, 275, "Такт 1: Iter0(C), Iter1(L)", size=10))
    frags.append(text(300, 300, "Наповнення конвеєра", size=9, color=MUTED, italic=True))

    frags.append(rect(370, 210, 240, 110, fill="#f0fdf4", stroke=FIELD, sw=2, rx=4))
    frags.append(text(490, 230, "СТАБІЛЬНЕ ЯДРО (KERNEL)", size=12, bold=True, color=FIELD))
    frags.append(text(490, 255, "Щотакту (II = 1) одночасно:", size=10, bold=True))
    frags.append(text(490, 275, "Iter i (S) + Iter i+1 (C) + Iter i+2 (L)", size=11, color=INK))
    frags.append(text(490, 300, "Темп: 1 готова ітерація за такт!", size=10, color=FIELD, bold=True))

    frags.append(rect(620, 210, 120, 110, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(680, 230, "ЕПІЛОГ", size=12, bold=True, color=POS))
    frags.append(text(680, 255, "Злив конвеєра", size=10))
    frags.append(text(680, 275, "Завершення", size=10))
    frags.append(text(680, 300, "останніх ітерацій", size=9, color=MUTED, italic=True))

    frags.append(text(790, 265, "N + 2 такти", size=12, color=FIELD, bold=True, anchor="end"))
    frags.append(text(w / 2, 345, "Стабільне ядро досягає максимального завантаження функціональних блоків процесора", size=12, color=MUTED, italic=True))

    return render(os.path.join(IMG_DIR, "fig-loop-execution-modes.svg"), w, h, *frags)


def fig_mrt_allocation():
    """Таблиця модульного резервування (MRT) та відображення тактів."""
    w, h = 800, 340
    frags = []

    frags.append(text(w / 2, 26, "Модульна таблиця резервування (MRT) для інтервалу II = 2", size=15, bold=True))

    # Ліва частина: Часова шкала глобального розкладу (Time t)
    frags.append(text(140, 60, "Глобальний час (t)", size=13, bold=True))
    ops = [
        ("t = 0", "Load x[i]", "Mem0", "#eff6ff", NEG),
        ("t = 1", "Load y[i]", "Mem1", "#eff6ff", NEG),
        ("t = 2", "Mul r1, r2", "ALU0", "#fef3c7", "#b45309"),
        ("t = 3", "Add r3, r4", "ALU1", "#fef3c7", "#b45309"),
        ("t = 4", "Store z[i]", "Mem0", "#f0fdf4", FIELD),
    ]

    for i, (t_lbl, op_name, res, bg_c, txt_c) in enumerate(ops):
        y = 80 + i * 44
        frags.append(rect(30, y, 65, 34, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(62, y + 21, t_lbl, size=11, bold=True))

        frags.append(rect(105, y, 145, 34, fill=bg_c, stroke=txt_c, sw=1.2, rx=4))
        frags.append(text(177, y + 21, "%s (%s)" % (op_name, res), size=11, bold=True, color=txt_c))

        slot = i % 2
        dest_y = 110 + slot * 65
        frags.append(arrow(255, y + 17, 340, dest_y, color=MUTED, sw=1.2))

    frags.append(textbox(295, 60, "Відображення:\nслот = t mod II", size=11, pad=5, fill="#f1f5f9", bold=True)[0])
    frags.append(text(570, 60, "Таблиця MRT (II = 2 рядки)", size=13, bold=True))

    cols = ["Mem0", "Mem1", "ALU0", "ALU1"]
    col_w = 85
    tbl_start_x = 425
    tbl_y = 85

    # Заголовки колонок
    for c_idx, c_name in enumerate(cols):
        cx = tbl_start_x + c_idx * col_w
        frags.append(rect(cx, tbl_y, col_w, 25, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=2))
        frags.append(text(cx + col_w / 2, tbl_y + 17, c_name, size=11, bold=True))

    mrt_grid = [
        [("Load / Store", FIELD), ("Вільний", MUTED), ("Mul", "#b45309"), ("Вільний", MUTED)],
        [("Вільний", MUTED), ("Load y", NEG), ("Вільний", MUTED), ("Add", "#b45309")]
    ]

    for r_idx in range(2):
        ry = tbl_y + 30 + r_idx * 65
        # Заголовок рядка (не перекриває колонки: розташований ліворуч від tbl_start_x)
        frags.append(rect(tbl_start_x - 80, ry, 75, 55, fill="#f8fafc", stroke=LINE, sw=1.2, rx=3))
        frags.append(text(tbl_start_x - 42, ry + 24, "Слот %d" % r_idx, size=11, bold=True))
        frags.append(text(tbl_start_x - 42, ry + 42, "(t mod 2=%d)" % r_idx, size=9, color=MUTED))

        for c_idx in range(4):
            cx = tbl_start_x + c_idx * col_w
            cell_txt, cell_c = mrt_grid[r_idx][c_idx]
            bg = "#ffffff" if cell_txt == "Вільний" else "#f0fdf4" if cell_c == FIELD else "#eff6ff" if cell_c == NEG else "#fef3c7"
            frags.append(rect(cx, ry, col_w, 55, fill=bg, stroke=LINE, sw=1.2, rx=3))
            frags.append(text(cx + col_w / 2, ry + 32, cell_txt, size=10, bold=(cell_txt != "Вільний"), color=cell_c))

    frags.append(text(w / 2, 320, "Жоден ресурс не містить колізій (не більше однієї операції на комірку в такті mod II)", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG_DIR, "fig-mrt-allocation.svg"), w, h, *frags)


def fig_ddg_recurrence():
    """Граф залежностей за даними (DDG) та рекурентний контур."""
    w, h = 680, 360
    frags = []

    frags.append(text(w / 2, 26, "Граф залежностей (DDG) та рекурентний контур (RecMII)", size=15, bold=True))

    frags.append(circle(140, 90, 28, fill="#eff6ff", stroke=NEG, sw=2))
    frags.append(text(140, 95, "Load A", size=11, bold=True, color=NEG))

    frags.append(circle(300, 90, 28, fill="#eff6ff", stroke=NEG, sw=2))
    frags.append(text(300, 95, "Load B", size=11, bold=True, color=NEG))

    frags.append(circle(220, 180, 28, fill="#fef3c7", stroke="#d97706", sw=2))
    frags.append(text(220, 185, "Mul", size=12, bold=True, color="#b45309"))

    frags.append(circle(220, 280, 32, fill="#fef2f2", stroke=POS, sw=2.5))
    frags.append(text(220, 285, "Acc (+)", size=13, bold=True, color=POS))

    frags.append(arrow(155, 110, 205, 160, color=LINE, sw=1.5))
    frags.append(text(165, 145, "d=2, δ=0", size=10, bold=True, color=MUTED))

    frags.append(arrow(285, 110, 235, 160, color=LINE, sw=1.5))
    frags.append(text(275, 145, "d=2, δ=0", size=10, bold=True, color=MUTED))

    frags.append(arrow(220, 208, 220, 248, color=LINE, sw=1.5))
    frags.append(text(245, 230, "d=2, δ=0", size=10, bold=True, color=MUTED))

    frags.append('<path d="M 190 290 C 100 310, 90 230, 190 270" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>' % POS)
    frags.append(textbox(90, 255, "Рекурентний зв'язок:\nAcc[i] → Acc[i+1]\nЗатримка d = 1\nДистанція δ = 1", size=10, pad=5, fill="#fff1f2", stroke=POS, bold=True)[0])

    frags.append(rect(400, 70, 250, 240, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(525, 95, "Розрахунок бар'єрів MII", size=13, bold=True))

    frags.append(text(415, 130, "1. Ресурсний бар'єр (ResMII):", size=11, bold=True))
    frags.append(text(425, 150, "• 2 порти пам'яті: ⌈2 / 2⌉ = 1", size=10))
    frags.append(text(425, 168, "• 1 блок множення: ⌈1 / 1⌉ = 1", size=10))
    frags.append(text(425, 186, "• 1 блок АЛП: ⌈1 / 1⌉ = 1", size=10))
    frags.append(text(425, 206, "→ ResMII = 1 такт", size=11, bold=True, color=FIELD))

    frags.append(text(415, 235, "2. Рекурентний бар'єр (RecMII):", size=11, bold=True))
    frags.append(text(425, 255, "Контур Acc → Acc:", size=10))
    frags.append(text(425, 273, "RecMII = ⌈∑d / ∑δ⌉ = ⌈1 / 1⌉ = 1", size=10, bold=True))
    frags.append(text(425, 295, "→ MII = max(ResMII, RecMII) = 1", size=11, bold=True, color=POS))

    frags.append(text(w / 2, 342, "Рекурентний контур визначає мінімально можливу відстань між ітераціями за даними", size=11, color=MUTED, italic=True))

    return render(os.path.join(IMG_DIR, "fig-ddg-recurrence.svg"), w, h, *frags)


def fig_rotating_registers():
    """Схема апаратних ротаційних регістрів та предикатів (IA-64 / Hexagon)."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 26, "Апаратний механізм ротації регістрів і предикатів у конвеєрі", size=15, bold=True))

    frags.append(rect(40, 55, 350, 130, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(215, 80, "Логічні регістри інструкції (IA-64)", size=12, bold=True))
    frags.append(textbox(120, 125, "Стадія 0 (Read)\nПише в r32", size=11, pad=5, fill="#eff6ff", stroke=NEG, bold=True)[0])
    frags.append(textbox(215, 125, "Стадія 1 (Calc)\nЧитає з r33", size=11, pad=5, fill="#fef3c7", stroke="#d97706", bold=True)[0])
    frags.append(textbox(310, 125, "Стадія 2 (Write)\nЧитає з r34", size=11, pad=5, fill="#f0fdf4", stroke=FIELD, bold=True)[0])

    frags.append(textbox(215, 168, "Базовий покажчик ротації: RRB = (RRB - 1) mod 96", size=10, pad=4, fill="#ffffff", color=POS, bold=True)[0])

    frags.append(arrow(395, 120, 445, 120, color=POS, sw=2))
    frags.append(text(420, 110, "br.ctop", size=11, bold=True, color=POS))

    frags.append(rect(450, 55, 330, 130, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(615, 80, "Фізичний регістровий файл (Кільце)", size=12, bold=True, color=FIELD))

    regs = [("R100", "i+2"), ("R101", "i+1"), ("R102", "i"), ("R103", "i-1")]
    for idx, (r_name, r_iter) in enumerate(regs):
        rx = 475 + idx * 72
        frags.append(rect(rx, 105, 64, 45, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(rx + 32, 123, r_name, size=11, bold=True))
        frags.append(text(rx + 32, 140, "Iter %s" % r_iter, size=9, color=MUTED))

    frags.append(text(615, 172, "Автоматичне перейменування без інструкцій mov!", size=10, color=FIELD, bold=True))

    frags.append(rect(40, 205, 740, 120, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(410, 230, "Керування фазами через предикати стадій (p16 = Пролог, p17 = Ядро, p18 = Епілог)", size=12, bold=True))

    stages_data = [
        ("Такт 0 (Пролог)", "p16 = 1", "p17 = 0", "p18 = 0", "Стартує Iter 0 (Load)"),
        ("Такт 1 (Пролог)", "p16 = 1", "p17 = 1", "p18 = 0", "Iter 1 (Load) + Iter 0 (Calc)"),
        ("Такт 2..N (Ядро)", "p16 = 1", "p17 = 1", "p18 = 1", "Iter i+2 (L) + Iter i+1 (C) + Iter i (S)"),
        ("Такт N+1 (Епілог)", "p16 = 0", "p17 = 1", "p18 = 1", "Нових ітерацій немає, злив даних"),
        ("Такт N+2 (Епілог)", "p16 = 0", "p17 = 0", "p18 = 1", "Фінал останньої ітерації N-1 (Store)"),
    ]

    for s_idx, (t_name, p16, p17, p18, desc) in enumerate(stages_data):
        sx = 55 + s_idx * 144
        frags.append(rect(sx, 245, 138, 68, fill="#ffffff", stroke=LINE, sw=1, rx=3))
        frags.append(text(sx + 69, 260, t_name, size=10, bold=True))
        frags.append(text(sx + 69, 277, "%s | %s | %s" % (p16, p17, p18), size=9, bold=True, color=POS if "0" in p16 or "0" in p18 else FIELD))
        frags.append(text(sx + 69, 296, desc, size=9, color=MUTED))

    frags.append(text(w / 2, 345, "Єдине тіло циклу виконує пролог, ядро та епілог завдяки вмиканню/вимиканню предикатів", size=11, color=MUTED, italic=True))

    return render(os.path.join(IMG_DIR, "fig-rotating-registers.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_loop_execution_modes()
    fig_mrt_allocation()
    fig_ddg_recurrence()
    fig_rotating_registers()
    print("Всі фігури згенеровано успішно.")
