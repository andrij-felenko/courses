# -*- coding: utf-8 -*-
"""Фігури теми «Перший дотик до готової плати» (root/course/embedded/pershyi-dotyk-do-hotovoi-platy).
svgkit імпортуємо зі scripts/ (AUTHORING §5).

    python figs.py        # генерує всі SVG у ./img/
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. visual-inspection.svg — три критичні зони оптичного контролю ─────────
def fig_visual_inspection():
    W, H = 720, 270
    parts = []
    pw = 224
    gap = 12
    x0 = 12

    def panel_frame(px, title, sub):
        parts.append(rect(px, 10, pw, H - 20, fill="#fbfcfd", stroke=LINE, sw=1.3, rx=8))
        parts.append(text(px + pw / 2, 32, title, size=13, color=INK, bold=True))
        parts.append(text(px + pw / 2, 48, sub, size=11, color=MUTED, italic=True))

    # Панель 1: Містки припою між ніжками QFP/QFN
    p1 = x0
    panel_frame(p1, "Містки припою", "коротке між виводами чипа")
    cx1 = p1 + pw / 2
    # Тіло чипа
    parts.append(rect(cx1 - 60, 68, 120, 36, fill="#2b2f36", stroke="#111", sw=1.2, rx=3))
    parts.append(text(cx1, 90, "QFP / IC", size=11, color="#f4f6f8", bold=True))
    # Ніжки чипа донизу
    pin_xs = [cx1 - 44, cx1 - 22, cx1, cx1 + 22, cx1 + 44]
    for px_ in pin_xs:
        parts.append(rect(px_ - 5, 104, 10, 38, fill="#c9ccd1", stroke="#6b7280", sw=1))
        # Контактний майданчик (пад)
        parts.append(rect(px_ - 7, 142, 14, 16, fill="#d4af37", stroke="#8a6a3a", sw=1))

    # Олов'яний місток між 2-ю і 3-ю ніжками
    parts.append('<path d="M%.1f 126 Q %.1f 134 %.1f 126 Q %.1f 118 %.1f 126 Z" fill="#9aa0a8" stroke="%s" stroke-width="1.5"/>'
                 % (pin_xs[1] + 5, (pin_xs[1] + pin_xs[2]) / 2, pin_xs[2] - 5, (pin_xs[1] + pin_xs[2]) / 2, pin_xs[1] + 5, POS))
    parts.append(text(cx1 - 11, 166, "міст припою!", size=10, color=POS, bold=True))
    parts.append(mtext(cx1, H - 32, ["Каніфольний флюс і обплітка", "прибирають перемичку"], size=10, color=MUTED))

    # Панель 2: Ключ першої ніжки (Pin 1)
    p2 = x0 + pw + gap
    panel_frame(p2, "Ключ орієнтації", "крапка чи зріз проти плати")
    cx2 = p2 + pw / 2
    # Контур посадкового місця на платі (шовкодрук)
    parts.append(rect(cx2 - 50, 72, 100, 100, fill="#1e3d29", stroke="#ffffff", sw=1.4, rx=4))
    # Позначка pin 1 на шовкодруку (біла крапка у лівому верхньому кутку)
    parts.append(circle(cx2 - 38, 84, 4, fill="#ffffff", stroke="#ffffff", sw=1))
    parts.append(text(cx2 - 24, 88, "шовк", size=9, color="#ffffff", anchor="start"))
    # Чип встановлено навпаки (крапка внизу праворуч)
    parts.append(rect(cx2 - 40, 96, 80, 70, fill="#2b2f36", stroke="#111", sw=1.2, rx=3))
    parts.append(text(cx2, 132, "MCU", size=12, color="#f4f6f8", bold=True))
    # Крапка на самому чипі (перевернутий)
    parts.append(circle(cx2 + 28, 154, 4, fill=POS, stroke="#ffffff", sw=1))
    parts.append(text(cx2 + 20, 158, "чип", size=9, color=POS, anchor="end", bold=True))
    # Попередження про розворот
    parts.append(text(cx2, 180, "чип розвернуто на 180°!", size=10, color=POS, bold=True))
    parts.append(mtext(cx2, H - 32, ["Звіряй крапку/зріз чипа", "з кутом на шовкодруку"], size=10, color=MUTED))

    # Панель 3: Пастка полярності конденсаторів
    p3 = x0 + 2 * (pw + gap)
    panel_frame(p3, "Пастка полярності", "тантал (+) проти електроліту (–)")
    cx3 = p3 + pw / 2

    # Електролітичний (алюмінієвий)
    y_el = 78
    parts.append(circle(cx3 - 48, y_el + 20, 18, fill="#a0a5aa", stroke="#333", sw=1.2))
    # Смужка на електроліті - це МІНУС
    parts.append('<path d="M%.1f %.1f A 18 18 0 0 1 %.1f %.1f L %.1f %.1f A 18 18 0 0 0 %.1f %.1f Z" fill="#2457d6"/>'
                 % (cx3 - 66, y_el + 20, cx3 - 48, y_el + 2, cx3 - 48, y_el + 38, cx3 - 66, y_el + 20))
    parts.append(text(cx3 - 56, y_el + 23, "–", size=13, color="#ffffff", bold=True))
    parts.append(text(cx3 - 48, y_el + 48, "Електроліт: смуга = МІНУС", size=9, color=NEG, bold=True))

    # Танталовий SMD
    y_tan = 138
    parts.append(rect(cx3 - 75, y_tan, 60, 26, fill="#c87820", stroke="#6a3c08", sw=1.2, rx=2))
    # Смужка на танталі - це ПЛЮС!
    parts.append(rect(cx3 - 75, y_tan, 12, 26, fill="#3a1c02", stroke="none"))
    parts.append(text(cx3 - 69, y_tan + 17, "+", size=12, color="#ffffff", bold=True))
    parts.append(text(cx3 - 35, y_tan + 17, "10uF", size=10, color="#ffffff"))
    parts.append(text(cx3 + 12, y_tan + 12, "Тантал SMD:", size=10, color=POS, bold=True, anchor="start"))
    parts.append(text(cx3 + 12, y_tan + 26, "смуга = ПЛЮС!", size=10, color=POS, bold=True, anchor="start"))

    parts.append(mtext(cx3, H - 32, ["Зворотне ввімкнення танталу", "призводить до вибуху чи КЗ"], size=10, color=MUTED))

    render(out("visual-inspection.svg"), W, H, *parts,
           title="Три критичні зони оптичного контролю перед подачею напруги")


# ── 2. cold-check-rails.svg — холодна продзвонка шин живлення ────────────────
def fig_cold_check_rails():
    W, H = 720, 290
    parts = []

    # Тло плати
    parts.append(rect(16, 20, 688, H - 36, fill="#f8fafc", stroke=LINE, sw=1.4, rx=10))

    # Блоки перетворювачів
    # Вхідне живлення (VIN / 5V)
    parts.append(rect(40, 50, 110, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    parts.append(text(95, 76, "Шина VIN", size=12, color=POS, bold=True))
    parts.append(text(95, 96, "5.0 В (Вхід)", size=10, color=MUTED))

    # Стабілізатор Buck 3.3V
    parts.append(arrow(150, 80, 200, 80, color=POS, sw=2))
    parts.append(rect(200, 50, 120, 60, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    parts.append(text(260, 76, "Step-Down 3V3", size=12, color="#b45309", bold=True))
    parts.append(text(260, 96, "I/O та периферія", size=10, color=MUTED))

    # Стабілізатор LDO 1.2V (Core)
    parts.append(arrow(320, 80, 370, 80, color="#d97706", sw=2))
    parts.append(rect(370, 50, 120, 60, fill="#e0e7ff", stroke=NEG, sw=1.5, rx=6))
    parts.append(text(430, 76, "LDO 1V2 Core", size=12, color=NEG, bold=True))
    parts.append(text(430, 96, "Ядро процесора", size=10, color=MUTED))

    # Спільна шина Землі (GND)
    parts.append(rect(40, 160, 450, 24, fill="#374151", stroke="#111", sw=1.2, rx=4))
    parts.append(text(265, 176, "СПІЛЬНА ЗЕМЛЯ (GND PLANE)", size=11, color="#f9fafb", bold=True))

    # Мультиметр
    mx, my = 540, 50
    parts.append(rect(mx, my, 144, 190, fill="#1e293b", stroke="#0f172a", sw=2, rx=10))
    # Екран мультиметра
    parts.append(rect(mx + 12, my + 14, 120, 44, fill="#84cc16", stroke="#3f6212", sw=1.5, rx=4))
    parts.append(text(mx + 72, my + 44, "47.2 Ω", size=20, color="#14532d", bold=True))
    # Перемикач
    parts.append(circle(mx + 72, my + 100, 20, fill="#334155", stroke="#cbd5e1", sw=1.5))
    parts.append(text(mx + 72, my + 104, "Ω", size=14, color="#ffffff", bold=True))
    parts.append(text(mx + 72, my + 140, "Режим опору", size=11, color="#94a3b8"))

    # Щупи мультиметра
    # Чорний щуп на GND
    parts.append(line(mx + 36, my + 170, 400, 172, color="#111", sw=2.4))
    parts.append(circle(400, 172, 5, fill="#111", stroke="#ffffff", sw=1))
    parts.append(text(400, 200, "COM (GND)", size=10, color=INK, bold=True))

    # Червоний щуп на шину Core 1.2V
    parts.append(line(mx + 108, my + 170, 440, 110, color=POS, sw=2.4))
    parts.append(circle(440, 110, 5, fill=POS, stroke="#ffffff", sw=1))

    # Таблиця очікуваних опорів знизу
    parts.append(rect(30, 200, 470, 60, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(text(50, 218, "Очікувані значення опору на холодній платі (відносно GND):", size=10, color=INK, bold=True, anchor="start"))
    parts.append(text(50, 234, "• Шина 5V / VIN:  > 100 кОм (заряд конденсаторів)", size=10, color=POS, anchor="start"))
    parts.append(text(50, 248, "• Шина 3.3V I/O:   > 5–10 кОм (периферія в спокої)", size=10, color="#b45309", anchor="start"))
    parts.append(text(280, 248, "• Шина 1.2V Core: 15–50 Ом (НОРМА ДЛЯ ЯДРА, не КЗ!)", size=10, color=NEG, bold=True, anchor="start"))

    render(out("cold-check-rails.svg"), W, H, *parts,
           title="Холодна перевірка опору шин живлення мультиметром до подачі живлення")


# ── 3. power-up-sequence.svg — послідовність подачі напруг і життєві сигнали ─
def fig_power_up_sequence():
    W, H = 720, 290
    parts = []

    # Часова вісь знизу
    t_start, t_end = 120, 660
    parts.append(line(t_start, 250, t_end + 20, 250, color=LINE, sw=1.6))
    parts.append(text(t_end + 30, 254, "t", size=13, color=LINE, bold=True))
    parts.append(text(t_start, 266, "0 мс", size=10, color=MUTED))
    parts.append(text(240, 266, "5 мс", size=10, color=MUTED))
    parts.append(text(360, 266, "10 мс", size=10, color=MUTED))
    parts.append(text(500, 266, "25 мс", size=10, color=MUTED))
    parts.append(text(620, 266, "50 мс", size=10, color=MUTED))

    # Вертикальні лінії прив'язки
    for tx in [140, 240, 360, 500, 620]:
        parts.append(line(tx, 40, tx, 250, color="#e2e8f0", sw=1, dash="4,4"))

    # Графік 1: Вхідна напруга VIN (5V)
    y1 = 60
    parts.append(text(105, y1 - 4, "VIN (5V)", size=11, color=POS, bold=True, anchor="end"))
    parts.append(line(t_start, y1, 140, y1, color=POS, sw=2))
    parts.append(line(140, y1, 170, y1 - 20, color=POS, sw=2.5))
    parts.append(line(170, y1 - 20, t_end, y1 - 20, color=POS, sw=2.5))
    parts.append(text(180, y1 - 24, "5.0 В", size=10, color=POS))

    # Графік 2: Шина 3.3V I/O (LDO / Buck)
    y2 = 105
    parts.append(text(105, y2 - 4, "VDD (3.3V)", size=11, color="#b45309", bold=True, anchor="end"))
    parts.append(line(t_start, y2, 200, y2, color="#b45309", sw=2))
    parts.append(line(200, y2, 240, y2 - 20, color="#b45309", sw=2.5))
    parts.append(line(240, y2 - 20, t_end, y2 - 20, color="#b45309", sw=2.5))
    parts.append(text(250, y2 - 24, "3.3 В", size=10, color="#b45309"))

    # Графік 3: Шина ядра VCORE (1.2V)
    y3 = 150
    parts.append(text(105, y3 - 4, "VCORE (1.2V)", size=11, color=NEG, bold=True, anchor="end"))
    parts.append(line(t_start, y3, 300, y3, color=NEG, sw=2))
    parts.append(line(300, y3, 360, y3 - 20, color=NEG, sw=2.5))
    parts.append(line(360, y3 - 20, t_end, y3 - 20, color=NEG, sw=2.5))
    parts.append(text(370, y3 - 24, "1.2 В", size=10, color=NEG))

    # Графік 4: Сигнал Power Good (PGOOD)
    y4 = 195
    parts.append(text(105, y4 - 4, "PGOOD", size=11, color=FIELD, bold=True, anchor="end"))
    parts.append(line(t_start, y4, 500, y4, color=FIELD, sw=2))
    parts.append(line(500, y4, 505, y4 - 20, color=FIELD, sw=2.5))
    parts.append(line(505, y4 - 20, t_end, y4 - 20, color=FIELD, sw=2.5))
    parts.append(text(515, y4 - 24, "HIGH (живлення стабільне)", size=10, color=FIELD, bold=True))

    # Графік 5: Апаратний скид nRST
    y5 = 235
    parts.append(text(105, y5 - 4, "nRST (Reset)", size=11, color=INK, bold=True, anchor="end"))
    parts.append(line(t_start, y5, 620, y5, color=INK, sw=2))
    parts.append(line(620, y5, 625, y5 - 20, color=INK, sw=2.5))
    parts.append(line(625, y5 - 20, t_end, y5 - 20, color=INK, sw=2.5))
    parts.append(text(632, y5 - 10, "Чип стартує!", size=10, color=INK, bold=True))

    render(out("power-up-sequence.svg"), W, H, *parts,
           title="Часова діаграма Power Sequencing, сигналу Power Good та зняття апаратного скиду")


# ── 4. crystal-probing-trap.svg — пастка перевірки кварцового резонатора ────
def fig_crystal_probing_trap():
    W, H = 720, 270
    parts = []

    # Ліва половина: Пасивний щуп зриває генерацію
    p1 = 12
    pw = 338
    parts.append(rect(p1, 10, pw, H - 20, fill="#fef2f2", stroke=POS, sw=1.3, rx=8))
    parts.append(text(p1 + pw / 2, 32, "Помилка: пасивний щуп 10x на кварці", size=12, color=POS, bold=True))

    cx1 = p1 + 90
    # Інвертор генератора Пірса всередині MCU
    parts.append(rect(p1 + 20, 65, 80, 110, fill="#334155", stroke="#0f172a", sw=1.2, rx=4))
    parts.append(text(p1 + 60, 95, "MCU", size=12, color="#ffffff", bold=True))
    parts.append(text(p1 + 82, 120, "OSC_IN", size=9, color="#94a3b8", anchor="end"))
    parts.append(text(p1 + 82, 150, "OSC_OUT", size=9, color="#94a3b8", anchor="end"))

    # Кварцовий резонатор ззовні
    qx = p1 + 160
    parts.append(line(p1 + 85, 120, qx, 120, color=INK, sw=1.6))
    parts.append(line(p1 + 85, 150, qx, 150, color=INK, sw=1.6))
    parts.append(rect(qx, 105, 30, 60, fill="#cbd5e1", stroke="#475569", sw=1.4, rx=2))
    parts.append(text(qx + 15, 139, "XTAL", size=9, color=INK, bold=True))

    # Конденсатори навантаження C1, C2
    parts.append(line(qx + 40, 120, qx + 70, 120, color=INK, sw=1.4))
    parts.append(line(qx + 40, 150, qx + 70, 150, color=INK, sw=1.4))
    parts.append(rect(qx + 70, 112, 10, 16, fill="#fef08a", stroke="#ca8a04", sw=1))
    parts.append(rect(qx + 70, 142, 10, 16, fill="#fef08a", stroke="#ca8a04", sw=1))
    parts.append(text(qx + 95, 124, "C1 12pF", size=9, color=MUTED))
    parts.append(text(qx + 95, 154, "C2 12pF", size=9, color=MUTED))

    # Щуп осцилографа тикається в OSC_IN
    parts.append(line(qx + 15, 105, qx + 15, 75, color=POS, sw=2))
    parts.append(circle(qx + 15, 105, 4, fill=POS, stroke="#ffffff", sw=1))
    parts.append(textbox(qx + 65, 72, "Щуп 10x (+15 пФ)\nзриває коливання!", size=9, color=POS, bold=True, fill="#fff", stroke=POS)[0])

    parts.append(mtext(p1 + pw / 2, H - 34,
                       ["Ємність щупа (12–15 пФ) порівнянна з C1/C2,",
                        "що шунтує контур і глушить генератор Пірса"], size=10, color=POS))

    # Права половина: Правильні методи перевірки
    p2 = 370
    parts.append(rect(p2, 10, pw, H - 20, fill="#f0fdf4", stroke=FIELD, sw=1.3, rx=8))
    parts.append(text(p2 + pw / 2, 32, "Правильно: неінвазивні методи перевірки", size=12, color=FIELD, bold=True))

    # Варіант А: Буферизований вихід MCO
    parts.append(rect(p2 + 20, 60, 298, 70, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    parts.append(text(p2 + 30, 80, "Варіант 1: Буферизований вивід MCO", size=11, color=FIELD, bold=True, anchor="start"))
    parts.append(text(p2 + 30, 98, "Налаштувати вивід тактової частоти на пін MCO", size=10, color=INK, anchor="start"))
    parts.append(text(p2 + 30, 114, "(Microcontroller Clock Output) через внутрішній буфер.", size=9, color=MUTED, anchor="start"))

    # Варіант Б: Активний щуп або H-field петля
    parts.append(rect(p2 + 20, 140, 298, 70, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    parts.append(text(p2 + 30, 160, "Варіант 2: Активний щуп / H-Field антена", size=11, color=FIELD, bold=True, anchor="start"))
    parts.append(text(p2 + 30, 178, "Активний FET-щуп (< 1 пФ) або безконтактна", size=10, color=INK, anchor="start"))
    parts.append(text(p2 + 30, 194, "магнітна петля біля корпусу резонатора.", size=9, color=MUTED, anchor="start"))

    parts.append(mtext(p2 + pw / 2, H - 34,
                       ["Буфер чи безконтактний зонд показують справжній",
                        "сигнал генератора без впливу на зворотний зв'язок"], size=10, color=FIELD))

    render(out("crystal-probing-trap.svg"), W, H, *parts,
           title="Чому пасивний щуп осцилографа зупиняє кварцовий генератор та як це обійти")


def main():
    fig_visual_inspection()
    fig_cold_check_rails()
    fig_power_up_sequence()
    fig_crystal_probing_trap()
    print("Згенеровано всі фігури у", IMG)


if __name__ == "__main__":
    main()
