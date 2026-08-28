# -*- coding: utf-8 -*-
"""Фігури до статті «Засоби проєктування плат (EDA)».
Дві фігури:
  eda-pipeline.svg — конвеєр проєктування від схеми й правил до виробничих файлів
  eda-matrix.svg   — порівняльна матриця САПР (KiCad, Altium, Cadence Allegro, EasyEDA)
Запуск: python figs.py  → пише SVG у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. eda-pipeline.svg — конвеєр проєктування друкованої плати в САПР
# ════════════════════════════════════════════════════════════════════════════
def fig_eda_pipeline():
    W, H = 840, 390
    f = []

    f.append(text(W / 2, 28, "Конвеєр проєктування друкованої плати в середовищі EDA", size=15, bold=True))

    # 4 етапи (колонки)
    stages = [
        (115, "1. СХЕМА", ["Схемотехнічний ввід", "Умовні позначення", "Ієрархічні аркуші", "Контроль правил ERC"], "#eaf0fd", NEG),
        (325, "2. СИНХРОНІЗАЦІЯ", ["Список кіл (Netlist)", "Призначення корпусів", "Оновлення плати", "Зворотні правки ECO"], "#fef6e7", "#d97706"),
        (535, "3. ТОПОЛОГІЯ", ["Стек шарів і плата", "Розміщення деталей", "Трасування доріжок", "Перевірка правил DRC"], "#eef7f0", FIELD),
        (735, "4. ВИРОБНИЦТВО", ["Шари Gerber (RS-274X/X2)", "Отвори свердління (NC Drill)", "Координати Pick & Place", "Специфікація BOM"], "#fdf0ea", POS),
    ]

    bw, bh = 175, 175
    y_box = 55

    for cx, title, items, bg_col, stroke_col in stages:
        f.append(rect(cx - bw / 2, y_box, bw, bh, fill=bg_col, stroke=stroke_col, sw=1.8, rx=8))
        f.append(text(cx, y_box + 24, title, size=13, bold=True, color=stroke_col))
        f.append(line(cx - bw / 2 + 10, y_box + 36, cx + bw / 2 - 10, y_box + 36, color=stroke_col, sw=1.0, dash="3 3"))

        iy = y_box + 60
        for itm in items:
            f.append(circle(cx - bw / 2 + 18, iy - 4, 3, fill=stroke_col, stroke=stroke_col))
            f.append(text(cx - bw / 2 + 28, iy, itm, size=10.5, anchor="start", color=INK))
            iy += 26

    # Прямі стрілки між етапами (вперед)
    f.append(arrow(115 + bw / 2 + 3, y_box + bh / 2 - 15, 325 - bw / 2 - 5, y_box + bh / 2 - 15, color=LINE, sw=1.8))
    f.append(arrow(325 + bw / 2 + 3, y_box + bh / 2 - 15, 535 - bw / 2 - 5, y_box + bh / 2 - 15, color=LINE, sw=1.8))
    f.append(arrow(535 + bw / 2 + 3, y_box + bh / 2 - 15, 735 - bw / 2 - 5, y_box + bh / 2 - 15, color=LINE, sw=1.8))

    # Зворотний зв'язок (Back-annotation / ECO)
    eco_y = y_box + bh + 30
    f.append(line(535, y_box + bh, 535, eco_y, color=MUTED, sw=1.3, dash="4 4"))
    f.append(line(535, eco_y, 115, eco_y, color=MUTED, sw=1.3, dash="4 4"))
    f.append(arrow(115, eco_y, 115, y_box + bh + 4, color=MUTED, sw=1.3))
    f.append(textbox(325, eco_y, "Зворотна анотація: зміна пінів / гейтів на платі передається в схему (ECO)", size=10, pad=5, fill="#f4f6f8", stroke=MUTED, color=MUTED)[0])

    # Нижній пояснювальний блок
    f.append(rect(30, 310, 780, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(W / 2, 330, "EDA зв'язує абстрактну схемотехніку з фізичною геометрією міді через єдину базу топології.", size=11, bold=True, color=INK))
    f.append(text(W / 2, 350, "Автоматичні перевірки ERC (електричні правила) та DRC (технологічні зазори) виявляють помилки до виготовлення.", size=10.5, color=MUTED))

    render(os.path.join(IMG, "eda-pipeline.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. eda-matrix.svg — порівняльна матриця САПР електроніки
# ════════════════════════════════════════════════════════════════════════════
def fig_eda_matrix():
    W, H = 840, 410
    f = []

    f.append(text(W / 2, 26, "Порівняльна характеристика провідних EDA-систем", size=15, bold=True))

    cols = [
        (120, "KiCad", "#eef2fb", NEG, [
            ("Ліцензія", "Open Source (GPLv3)"),
            ("Формат", "Текстовий S-expr (Git)"),
            ("Швидкісні лінії", "Базові пари / довжини"),
            ("Скрипти", "Потужний Python API"),
            ("Фокус", "OSHW, R&D, стартапи"),
        ]),
        (325, "Altium Designer", "#fdf0ea", POS, [
            ("Ліцензія", "Комерційна пропрієтарна"),
            ("Формат", "Уніфікована БД / Altium 365"),
            ("Швидкісні лінії", "Розширені правила й підгонка"),
            ("Скрипти", "Delphi, JS, VBScript"),
            ("Фокус", "Промисловий стандарт"),
        ]),
        (530, "Cadence Allegro", "#eef7f0", FIELD, [
            ("Ліцензія", "Enterprise-комерційна"),
            ("Формат", "Пропрієтарний бінарний"),
            ("Швидкісні лінії", "Глибокий Constraint Mgr + SI"),
            ("Скрипти", "SKILL (Lisp-подібний)"),
            ("Фокус", "Сервери, DDR5, PCIe, RF"),
        ]),
        (725, "EasyEDA", "#fef6e7", "#d97706", [
            ("Ліцензія", "Хмарний freemium"),
            ("Формат", "JSON у хмарі вендора"),
            ("Швидкісні лінії", "Спрощені правила"),
            ("Скрипти", "Web API / розширення"),
            ("Фокус", "Швидкі прототипи / JLCPCB"),
        ]),
    ]

    bw = 190
    y_top = 48
    bh = 315

    for cx, title, bg_col, stroke_col, rows in cols:
        f.append(rect(cx - bw / 2, y_top, bw, bh, fill=bg_col, stroke=stroke_col, sw=1.8, rx=8))
        f.append(text(cx, y_top + 24, title, size=13.5, bold=True, color=stroke_col))
        f.append(line(cx - bw / 2 + 8, y_top + 36, cx + bw / 2 - 8, y_top + 36, color=stroke_col, sw=1.0, dash="3 3"))

        ry = y_top + 58
        for label, val in rows:
            f.append(text(cx, ry, label.upper(), size=9, bold=True, color=MUTED))
            f.append(text(cx, ry + 16, val, size=10.5, bold=False, color=INK))
            ry += 52
            if label != rows[-1][0]:
                f.append(line(cx - bw / 2 + 15, ry - 14, cx + bw / 2 - 15, ry - 14, color="#e2e8f0", sw=0.8))

    f.append(text(W / 2, 385, "Вибір САПР залежить від складності шин (DDR/PCIe), вимог до командної співпраці та бюджету ліцензування.", size=10.5, color=MUTED))

    render(os.path.join(IMG, "eda-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_eda_pipeline()
    fig_eda_matrix()
    print("OK: generated 2 figures in img/")
