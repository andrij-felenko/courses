# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Друкований іскровий проміжок (PCB Spark Gap)».
Запуск: python figs.py -> ./img/*.svg
Імпортуємо svgkit зі scripts/."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# Палітра для друкованих плат
COPPER = "#b45309"      # мідні доріжки / полігони
MASK = "#166534"        # паяльна маска (темно-зелений)
KEEPOUT = "#fef3c7"     # зона без маски (Soldermask Keepout)
ARC = "#ea580c"         # електрична дуга / іскра


# ── Фігура 1: Геометричні топології друкованих іскрових проміжків ───────────
def fig_types():
    w, h = 980, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Основні геометрії друкованих іскрових розрядників на платі", size=16, bold=True))

    # 4 колонки для 4 топологій
    col_w = 215
    cols = [
        ("Одиночне вістря (шеврон)", 30),
        ("Зубчастий гребінець", 265),
        ("Пальцева структура", 500),
        ("Напівкруглі електроди", 735),
    ]

    for title, cx_left in cols:
        frags.append(rect(cx_left, 55, col_w, 445, fill="#fafafa", stroke="#e5e7eb", sw=1.5, rx=8))
        frags.append(text(cx_left + col_w / 2, 78, title, size=13, bold=True, color=INK))

    # 1. Одиночний шеврон
    # Зона keepout (без маски)
    frags.append('<rect x="45.0" y="105.0" width="185.0" height="230.0" rx="4" fill="%s" stroke="#fcd34d" stroke-width="1.2" stroke-dasharray="4,3"/>' % KEEPOUT)
    frags.append(text(137, 122, "вікно маски (Keepout)", size=10, color=MUTED, italic=True))
    # Верхній провідник (лінія)
    frags.append(rect(120, 135, 35, 45, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append('<polygon points="110,180 165,180 137.5,215" fill="%s" stroke="%s" stroke-width="1.5"/>' % (COPPER, LINE))
    # Нижній провідник (земля)
    frags.append('<polygon points="110,260 165,260 137.5,225" fill="%s" stroke="%s" stroke-width="1.5"/>' % (COPPER, LINE))
    frags.append(rect(120, 260, 35, 45, fill=COPPER, stroke=LINE, sw=1.5))
    # Розмір зазору d
    frags.append(line(175, 215, 175, 225, color=POS, sw=1.5))
    frags.append(line(170, 215, 180, 215, color=POS, sw=1.2))
    frags.append(line(170, 225, 180, 225, color=POS, sw=1.2))
    frags.append(text(205, 224, "d ≈ 0.3 мм", size=11, color=POS, bold=True, anchor="start"))
    # Іскра
    frags.append('<polyline points="137.5,215 140,218 135,222 137.5,225" fill="none" stroke="%s" stroke-width="2.5"/>' % ARC)

    b1, _, _ = textbox(137, 395, "Мінімальна напруга пробою\nчерез високу концентрацію E.\nШвидке обгорання вістря.", size=11, pad=8, fill="#ffffff", stroke="#d1d5db")
    frags.append(b1)

    # 2. Зубчастий гребінець (багатоточковий)
    frags.append('<rect x="280.0" y="105.0" width="185.0" height="230.0" rx="4" fill="%s" stroke="#fcd34d" stroke-width="1.2" stroke-dasharray="4,3"/>' % KEEPOUT)
    frags.append(text(372, 122, "вікно маски (Keepout)", size=10, color=MUTED, italic=True))
    # Верхня шина
    frags.append(rect(300, 140, 145, 30, fill=COPPER, stroke=LINE, sw=1.5))
    for tx in [320, 355, 390, 425]:
        frags.append('<polygon points="%d,170 %d,170 %d,205" fill="%s" stroke="%s" stroke-width="1.2"/>' % (tx - 12, tx + 12, tx, COPPER, LINE))
    # Нижня шина
    frags.append(rect(300, 270, 145, 30, fill=COPPER, stroke=LINE, sw=1.5))
    for tx in [320, 355, 390, 425]:
        frags.append('<polygon points="%d,270 %d,270 %d,235" fill="%s" stroke="%s" stroke-width="1.2"/>' % (tx - 12, tx + 12, tx, COPPER, LINE))
    # Кілька розрядів
    for tx in [320, 390]:
        frags.append('<polyline points="%d,205 %d,215 %d,225 %d,235" fill="none" stroke="%s" stroke-width="2"/>' % (tx, tx + 3, tx - 3, tx, ARC))

    b2, _, _ = textbox(372, 395, "Розподіл енергії між зубцями.\nВища надійність і довговічність\nпри багаторазових ударах.", size=11, pad=8, fill="#ffffff", stroke="#d1d5db")
    frags.append(b2)

    # 3. Пальцева структура (Interdigital)
    frags.append('<rect x="515.0" y="105.0" width="185.0" height="230.0" rx="4" fill="%s" stroke="#fcd34d" stroke-width="1.2" stroke-dasharray="4,3"/>' % KEEPOUT)
    frags.append(text(607, 122, "вікно маски (Keepout)", size=10, color=MUTED, italic=True))
    # Верхня база і пальці
    frags.append(rect(535, 140, 145, 20, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append(rect(555, 160, 16, 75, fill=COPPER, stroke=LINE, sw=1.2))
    frags.append(rect(615, 160, 16, 75, fill=COPPER, stroke=LINE, sw=1.2))
    # Нижня база і пальці
    frags.append(rect(535, 280, 145, 20, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append(rect(585, 205, 16, 75, fill=COPPER, stroke=LINE, sw=1.2))
    frags.append(rect(645, 205, 16, 75, fill=COPPER, stroke=LINE, sw=1.2))

    b3, _, _ = textbox(607, 395, "Велика площа перекриття.\nНизький опір дуги, але\nпідвищена ємність (> 0.5 пФ).", size=11, pad=8, fill="#ffffff", stroke="#d1d5db")
    frags.append(b3)

    # 4. Напівкруглі / овальні електроди
    frags.append('<rect x="750.0" y="105.0" width="185.0" height="230.0" rx="4" fill="%s" stroke="#fcd34d" stroke-width="1.2" stroke-dasharray="4,3"/>' % KEEPOUT)
    frags.append(text(842, 122, "вікно маски (Keepout)", size=10, color=MUTED, italic=True))
    # Верхній напівкруг
    frags.append(rect(815, 135, 55, 30, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append('<path d="M 815,165 C 815,205 870,205 870,165 Z" fill="%s" stroke="%s" stroke-width="1.5"/>' % (COPPER, LINE))
    # Нижній напівкруг
    frags.append(rect(815, 275, 55, 30, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append('<path d="M 815,275 C 815,235 870,235 870,275 Z" fill="%s" stroke="%s" stroke-width="1.5"/>' % (COPPER, LINE))
    # Зазор
    frags.append(line(842.5, 195, 842.5, 245, color=ARC, sw=2.5))

    b4, _, _ = textbox(842, 395, "Однорідніше поле між сферами.\nВища стабільність порогу,\nменша ерозія металу.", size=11, pad=8, fill="#ffffff", stroke="#d1d5db")
    frags.append(b4)

    render(os.path.join(IMG, "pcb-spark-gap-types.svg"), w, h, *frags,
           title="Основні геометричні форми друкованих іскрових розрядників на платі")


# ── Фігура 2: Концентрація електричного поля на гострому вістрі ──────────────
def fig_field():
    w, h = 940, 460
    frags = []

    frags.append(text(w / 2, 26, "Електростатика розрядника: однорідне поле проти концентрації на вістрі", size=15, bold=True))

    # Ліва панель: плоскі пластини
    frags.append(rect(35, 50, 415, 390, fill="#fbfbfb", stroke="#e5e7eb", sw=1.5, rx=8))
    frags.append(text(242, 75, "Плоскі паралельні електроди", size=14, bold=True, color=INK))
    frags.append(text(242, 95, "Однорідне поле (E = U / d)", size=12, color=MUTED, italic=True))

    # Пластини
    frags.append(rect(80, 130, 325, 24, fill=POS, stroke=LINE, sw=1.5, rx=3))
    frags.append(text(242, 146, "Анод (+U)", size=12, color="#ffffff", bold=True))
    frags.append(rect(80, 290, 325, 24, fill=NEG, stroke=LINE, sw=1.5, rx=3))
    frags.append(text(242, 306, "Катод (0 В, земля)", size=12, color="#ffffff", bold=True))

    # Лінії поля (рівномірні)
    for lx in range(110, 380, 32):
        frags.append(line(lx, 154, lx, 290, color=FIELD, sw=1.5, dash="4,3"))
        frags.append('<polygon points="%d,225 %d,217 %d,225" fill="%s"/>' % (lx - 3, lx, lx + 3, FIELD))

    # Розмір d
    frags.append(line(60, 154, 60, 290, color=LINE, sw=1.5))
    frags.append(line(55, 154, 65, 154, color=LINE, sw=1.2))
    frags.append(line(55, 290, 65, 290, color=LINE, sw=1.2))
    frags.append(text(48, 226, "d", size=13, bold=True, anchor="end"))

    b_left, _, _ = textbox(242, 375, "Поле всюди однакове: E = U / d.\nПробій вимагає E_крит ≈ 3 кВ/мм у всьому об'ємі.\nДля d = 0.3 мм пробивна напруга U_пр ≈ 900–1200 В.", size=11, pad=8, fill="#ffffff", stroke="#d1d5db")
    frags.append(b_left)

    # Права панель: зустрічні гострі вістря
    frags.append(rect(490, 50, 415, 390, fill="#fbfbfb", stroke="#e5e7eb", sw=1.5, rx=8))
    frags.append(text(697, 75, "Зустрічні гострі вістря (зубці)", size=14, bold=True, color=INK))
    frags.append(text(697, 95, "Неоднорідне поле з коефіцієнтом підсилення β", size=12, color=MUTED, italic=True))

    # Верхнє вістря
    frags.append(rect(650, 115, 95, 22, fill=POS, stroke=LINE, sw=1.5, rx=2))
    frags.append('<polygon points="650,137 745,137 697.5,190" fill="%s" stroke="%s" stroke-width="1.5"/>' % (POS, LINE))
    frags.append(text(697, 130, "+U", size=11, color="#ffffff", bold=True))

    # Нижнє вістря
    frags.append('<polygon points="650,283 745,283 697.5,230" fill="%s" stroke="%s" stroke-width="1.5"/>' % (NEG, LINE))
    frags.append(rect(650, 283, 95, 22, fill=NEG, stroke=LINE, sw=1.5, rx=2))
    frags.append(text(697, 299, "Земля (0 В)", size=11, color="#ffffff", bold=True))

    # Центральна лінія
    frags.append(line(697.5, 190, 697.5, 230, color=ARC, sw=2.5))
    # Викривлені силові лінії
    frags.append('<path d="M 693,188 C 665,200 665,220 693,232" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,2"/>' % FIELD)
    frags.append('<path d="M 702,188 C 730,200 730,220 702,232" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,2"/>' % FIELD)
    frags.append('<path d="M 680,175 C 620,195 620,225 680,245" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % FIELD)
    frags.append('<path d="M 715,175 C 775,195 775,225 715,245" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,2"/>' % FIELD)

    # Зони високої напруженості
    frags.append(circle(697.5, 190, 12, fill="#fef08a", stroke="#eab308", sw=1.2))
    frags.append(circle(697.5, 230, 12, fill="#fef08a", stroke="#eab308", sw=1.2))
    frags.append(text(765, 192, "E_max = β · E_avg", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(765, 206, "(β ≈ 5 ... 15)", size=10, color=MUTED, anchor="start"))

    b_right, _, _ = textbox(697, 375, "Заряд накопичується на малому радіусі r_tip.\nЛокальне поле перевищує поріг іонізації раніше:\nударна лавина стартує при значно нижчій напрузі.", size=11, pad=8, fill="#ffffff", stroke="#d1d5db")
    frags.append(b_right)

    render(os.path.join(IMG, "field-concentration-tips.svg"), w, h, *frags,
           title="Концентрація електричного поля на гострих вістрях друкованого розрядника")


# ── Фігура 3: Паяльна маска, вікно Keepout та фрезерований паз ───────────────
def fig_mask():
    w, h = 940, 480
    frags = []

    frags.append(text(w / 2, 26, "Вплив паяльної маски та карбонізація діелектрика при розряді", size=15, bold=True))

    # Ліворуч: Помилка — маска покриває зазор
    frags.append(rect(35, 50, 415, 410, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    frags.append(text(242, 75, "ПОМИЛКА: Маска в зазорі розрядника", size=13, bold=True, color=POS))

    # Підкладка FR-4
    frags.append(rect(60, 180, 365, 75, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(text(242, 222, "Діелектрик FR-4 (склотекстоліт)", size=12, color="#854d0e", bold=True))

    # Мідні провідники
    frags.append(rect(60, 155, 120, 25, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append(text(120, 172, "Мідь (+U)", size=11, color="#ffffff", bold=True))
    frags.append(rect(305, 155, 120, 25, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append(text(365, 172, "Мідь (GND)", size=11, color="#ffffff", bold=True))

    # Паяльна маска накриває провідники по боках
    frags.append(rect(60, 140, 120, 15, fill=MASK, stroke="#14532d", sw=1.2, rx=1))
    frags.append(rect(305, 140, 120, 15, fill=MASK, stroke="#14532d", sw=1.2, rx=1))
    frags.append(text(242, 128, "Паяльна маска в зазорі вигоріла!", size=10, color=POS, bold=True))

    # Карбонізація (чорна пляма / сажа)
    frags.append(rect(180, 140, 125, 25, fill="#1f2937", stroke="#111827", sw=1.5, rx=3))
    frags.append(text(242, 156, "Вуглецевий нагар (сажа)", size=10, color="#f87171", bold=True))

    # Стрілка струму витоку крізь сажу
    frags.append(arrow(150, 195, 335, 195, color=POS, sw=2))
    frags.append(text(242, 206, "Постійне коротке замикання (R < 100 Ом)", size=10, color=POS, bold=True))

    b_err, _, _ = textbox(242, 335, "Високотемпературна дуга випалює\nорганічні смоли маски до чистого вуглецю.\nВиникає незворотний струмопровідний місток.\nПлата стає непридатною після першого ж удару.", size=11, pad=8, fill="#ffffff", stroke="#fca5a5")
    frags.append(b_err)

    # Праворуч: Правильне рішення — Soldermask Keepout + Air Slot
    frags.append(rect(490, 50, 415, 410, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(697, 75, "ПРАВИЛЬНО: Вікно маски + повітряний паз", size=13, bold=True, color="#15803d"))

    # Підкладка FR-4 з фрезерованим пазом
    frags.append(rect(515, 180, 140, 75, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=2))
    frags.append(rect(745, 180, 135, 75, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=2))
    # Фрезерований паз
    frags.append('<rect x="655.0" y="180.0" width="90.0" height="75.0" rx="1" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,2"/>')
    frags.append(text(700, 222, "Паз (Air Slot)", size=11, color="#64748b", italic=True))

    # Мідні провідники
    frags.append(rect(515, 155, 140, 25, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append(text(585, 172, "Мідь (+U)", size=11, color="#ffffff", bold=True))
    frags.append(rect(740, 155, 140, 25, fill=COPPER, stroke=LINE, sw=1.5))
    frags.append(text(810, 172, "Мідь (GND)", size=11, color="#ffffff", bold=True))

    # Паяльна маска з відступом (Keepout)
    frags.append(rect(515, 140, 100, 15, fill=MASK, stroke="#14532d", sw=1.2, rx=1))
    frags.append(rect(780, 140, 100, 15, fill=MASK, stroke="#14532d", sw=1.2, rx=1))
    frags.append(text(697, 132, "Soldermask Keepout (відступ ≥ 0.5 мм)", size=10, color="#15803d", bold=True))

    # Чиста іскра в повітрі
    frags.append('<polyline points="655,167 675,160 690,174 710,161 740,167" fill="none" stroke="%s" stroke-width="2.5"/>' % ARC)

    b_ok, _, _ = textbox(697, 335, "Маска повністю видалена з зони розряду.\nІскра горить виключно в чистому повітрі.\nФрезерований паз усуває поверхневий шлях витоку.\nОпір після розряду залишається > 10¹² Ом.", size=11, pad=8, fill="#ffffff", stroke="#86efac")
    frags.append(b_ok)

    render(os.path.join(IMG, "soldermask-carbonization.svg"), w, h, *frags,
           title="Небезпека карбонізації паяльної маски та правильне проектування вікна Keepout")


# ── Фігура 4: Багаторівневий каскад захисту та динаміка напруг ───────────────
def fig_cascade():
    w, h = 960, 520
    frags = []

    frags.append(text(w / 2, 26, "Багаторівневий захист: узгодження іскрового розрядника, імпедансу та TVS", size=15, bold=True))

    # Верхня частина: принципова схема
    frags.append(rect(30, 50, 900, 170, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(50, 72, "Схема каскадної координації захисту", size=13, bold=True, anchor="start", color=INK))

    # Вхідний сплеск
    frags.append(text(65, 115, "ESD / Сплеск", size=11, color=POS, bold=True))
    frags.append(text(65, 130, "(до 8–15 кВ)", size=10, color=MUTED))
    frags.append(arrow(115, 125, 160, 125, color=POS, sw=2.5))

    # Вхідна лінія
    frags.append(line(160, 125, 780, 125, color=INK, sw=2.5))

    # 1-й ступінь: PCB Spark Gap
    frags.append(circle(250, 125, 4, fill=INK, stroke=INK, sw=1.5))
    frags.append(line(250, 125, 250, 142, color=INK, sw=2))
    # Зубці розрядника
    frags.append('<polygon points="242,142 258,142 250,152" fill="%s" stroke="%s" stroke-width="1.2"/>' % (COPPER, LINE))
    frags.append('<polygon points="242,168 258,168 250,158" fill="%s" stroke="%s" stroke-width="1.2"/>' % (COPPER, LINE))
    frags.append(line(250, 168, 250, 190, color=NEG, sw=2))
    # Земля
    frags.append(line(238, 190, 262, 190, color=NEG, sw=2.5))
    frags.append(line(242, 194, 258, 194, color=NEG, sw=2))
    frags.append(line(246, 198, 254, 198, color=NEG, sw=1.5))
    frags.append(text(250, 105, "1. PCB Spark Gap", size=11, bold=True, color=POS))
    frags.append(text(250, 212, "Скидає 90–95% енергії", size=10, color=MUTED))

    # Розв'язувальний імпеданс (резистор / індуктивність доріжки)
    frags.append(rect(380, 112, 90, 26, fill="#ffffff", stroke=LINE, sw=1.8, rx=3))
    frags.append(text(425, 129, "R_s / L_trace", size=11, bold=True))
    frags.append(text(425, 103, "Координуючий імпеданс", size=10, color="#0284c7", bold=True))
    frags.append(text(425, 150, "ΔU = L·(di/dt) + R·i", size=10, color=MUTED, italic=True))

    # 2-й ступінь: TVS-діод
    frags.append(circle(590, 125, 4, fill=INK, stroke=INK, sw=1.5))
    frags.append(line(590, 125, 590, 145, color=INK, sw=2))
    # Діодний символ
    frags.append('<polygon points="578,145 602,145 590,165" fill="#ffffff" stroke="%s" stroke-width="1.8"/>' % INK)
    frags.append(line(576, 165, 604, 165, color=INK, sw=2))
    frags.append(line(576, 165, 576, 169, color=INK, sw=1.5))
    frags.append(line(604, 165, 604, 161, color=INK, sw=1.5))
    frags.append(line(590, 165, 590, 190, color=NEG, sw=2))
    # Земля
    frags.append(line(578, 190, 602, 190, color=NEG, sw=2.5))
    frags.append(line(582, 194, 598, 194, color=NEG, sw=2))
    frags.append(line(586, 198, 594, 198, color=NEG, sw=1.5))
    frags.append(text(590, 105, "2. TVS-діод", size=11, bold=True, color="#0284c7"))
    frags.append(text(590, 212, "Швидкий клемпінг (< 1 нс)", size=10, color=MUTED))

    # Захищена мікросхема
    frags.append(rect(740, 95, 140, 60, fill="#f1f5f9", stroke=LINE, sw=2, rx=4))
    frags.append(text(810, 122, "Захищена IC", size=12, bold=True))
    frags.append(text(810, 139, "PHY / MCU вхід", size=10, color=MUTED))

    # Нижня частина: Часові діаграми напруги
    frags.append(rect(30, 235, 900, 270, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(50, 258, "Динаміка напруг у часі: спрацювання каскаду", size=13, bold=True, anchor="start", color=INK))

    # Осі графіка
    frags.append(arrow(90, 460, 880, 460, color=LINE, sw=1.5))
    frags.append(text(880, 475, "Час (нс)", size=11, anchor="end"))
    frags.append(arrow(90, 460, 90, 280, color=LINE, sw=1.5))
    frags.append(text(80, 285, "Напруга U (кВ)", size=11, anchor="end"))

    # Позначки напруг на осі Y
    frags.append(line(85, 310, 95, 310, color=LINE, sw=1.2))
    frags.append(text(80, 314, "U_spark (1.5 кВ)", size=10, color=POS, anchor="end", bold=True))

    frags.append(line(85, 370, 95, 370, color=LINE, sw=1.2))
    frags.append(text(80, 374, "U_clamp_tvs (12 В)", size=10, color="#0284c7", anchor="end", bold=True))

    # Крива 1: Вхідна напруга на розряднику (червона)
    # Швидко росте, на t_spark падає через дугу до десятків вольтів
    frags.append('<path d="M 90,460 C 130,360 170,300 220,310 L 235,420 L 850,445" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    frags.append(text(250, 315, "Пробій зазору (іскра запалилась!)", size=10, color=POS, bold=True, anchor="start"))

    # Крива 2: Напруга на вході мікросхеми / TVS (синя)
    # Швидко підрізається TVS діодом до U_clamp
    frags.append('<path d="M 90,460 C 110,430 130,370 170,370 L 850,370" fill="none" stroke="#0284c7" stroke-width="2.2"/>')
    frags.append(text(550, 360, "Напруга на вході IC обмежена TVS (безпечні 10–15 В)", size=10, color="#0284c7", bold=True, anchor="start"))

    # Часові маркери
    frags.append(line(170, 280, 170, 460, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(170, 475, "t_1: TVS вмикається (<1 нс)", size=9, color=MUTED))

    frags.append(line(230, 280, 230, 460, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(275, 490, "t_2: Spark Gap пробивається (~5–10 нс)", size=9, color=POS, bold=True))

    render(os.path.join(IMG, "multistage-protection-cascade.svg"), w, h, *frags,
           title="Багаторівневий захист: динаміка координації між іскровим розрядником і TVS-діодом")


if __name__ == "__main__":
    fig_types()
    fig_field()
    fig_mask()
    fig_cascade()
    print("Всі 4 фігури успішно згенеровано у ./img/")
