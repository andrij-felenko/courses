# -*- coding: utf-8 -*-
"""Фігури до теми «Панель, фрезерування, маркування, тестові купони»
(root/hw/hw-pcb/panel-frezeruvannia-markuvannia-testovi-kupony).

Дві фігури:
  1. panel-breakaway-tabs.svg  — Геометрія перфорованої перемички (mouse bites), лінія злому та зони напружень.
  2. impedance-test-coupon.svg — Монтажна панель з оптичними реперами, технологічними отворами та TDR-купоном.

Запуск: python figs.py -> пише SVG у ./img/
"""
import sys
import os

# 4 рівні вгору до кореня репозиторію -> scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. panel-breakaway-tabs.svg — Геометрія перфорованої перемички
# ════════════════════════════════════════════════════════════════════════════
def fig_panel_breakaway_tabs():
    W, H = 880, 500
    f = []

    # Загальний фон
    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))

    # Заголовок
    f.append(text(W / 2, 28, "Геометрія перфорованої перемички (Mouse Bites) та зони напружень", size=16, bold=True, color=INK))

    # Ліва частина: креслення перемички
    left_x, left_y, left_w, left_h = 20, 52, 500, 430
    f.append(rect(left_x, left_y, left_w, left_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(left_x + left_w / 2, left_y + 24, "Конструкція вузла фрезерування й перфорації", size=13, bold=True, color=INK))

    # Верхній блок: Технологічне поле панелі (Rail)
    rail_y = left_y + 40
    rail_h = 70
    f.append(rect(left_x + 15, rail_y, left_w - 30, rail_h, fill="#d5e8d4", stroke="#27ae60", sw=1.5, rx=4))
    f.append(text(left_x + left_w / 2, rail_y + 30, "Технологічне поле панелі (Rail / Waste Strip)", size=13, bold=True, color="#1e7e34"))
    f.append(text(left_x + left_w / 2, rail_y + 50, "Затискається в конвеєрних рейках лінії SMT", size=11, color=MUTED))

    # Паз фрезерування (Milling Slot) 2.0 mm
    slot_y = rail_y + rail_h
    slot_h = 60
    # Зліва від перемички
    f.append(rect(left_x + 15, slot_y, 160, slot_h, fill="#ffffff", stroke="#9e9e9e", sw=1.2, rx=0))
    f.append(text(left_x + 95, slot_y + 35, "Паз фрези 2.0 мм", size=11, bold=True, color="#616161"))
    # Справа від перемички
    f.append(rect(left_x + 295, slot_y, 190, slot_h, fill="#ffffff", stroke="#9e9e9e", sw=1.2, rx=0))
    f.append(text(left_x + 390, slot_y + 35, "Паз фрези 2.0 мм", size=11, bold=True, color="#616161"))

    # Сама перемичка (Breakaway Tab) у центрі шириною 120 px (4.0 мм)
    tab_x = left_x + 175
    tab_w = 120
    tab_h = slot_h
    f.append(rect(tab_x, slot_y, tab_w, tab_h, fill="#fff2cc", stroke="#d6b656", sw=1.5, rx=0))
    f.append(text(tab_x + tab_w / 2, slot_y + 22, "Перемичка (Tab)", size=11, bold=True, color="#b78103"))
    f.append(text(tab_x + tab_w / 2, slot_y + 40, "Ширина W = 4.0 мм", size=10, color="#b78103"))

    # Нижня частина: Робоча плата (PCB)
    pcb_y = slot_y + slot_h
    pcb_h = 180
    f.append(rect(left_x + 15, pcb_y, left_w - 30, pcb_h, fill="#e1d5e7", stroke="#8e44ad", sw=1.5, rx=4))
    f.append(text(left_x + left_w / 2, pcb_y + pcb_h - 15, "Корисна друкована плата (PCB)", size=13, bold=True, color="#6c3483"))

    # Отвори перфорації (Mouse Bites)
    # 5 отворів діаметром 0.6 мм
    holes_y = pcb_y + 7
    start_hole_x = tab_x + 16
    for i in range(5):
        hx = start_hole_x + i * 22
        f.append(circle(hx, holes_y, 6.0, fill="#ffffff", stroke=POS, sw=1.5))
        f.append(circle(hx, holes_y, 1.2, fill=POS, stroke="none"))

    # Лінія злому (пунктир через отвори)
    f.append(line(tab_x - 5, holes_y, tab_x + tab_w + 5, holes_y, color=POS, sw=1.5, dash="4,3"))
    f.append(text(tab_x + tab_w / 2, holes_y - 10, "Лінія злому", size=10, bold=True, color=POS))

    # Зона заборони міді (Copper Keepout) навколо перемички
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="none" stroke="#e67e22" stroke-width="1.5" stroke-dasharray="3,3"/>' % (tab_x - 10, pcb_y + 16, tab_w + 20, 24))
    f.append(text(left_x + 95, pcb_y + 24, "Заборона міді ≥ 0.5 мм", size=10, bold=True, color="#d35400"))

    # Зона заборони компонентів (Component Keepout) біля лінії згину
    f.append(rect(left_x + 25, pcb_y + 45, left_w - 50, 52, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    f.append(text(left_x + left_w / 2, pcb_y + 64, "Зона механічного напруження (Keepout MLCC / BGA ≥ 2.0..3.0 мм)", size=10, bold=True, color=POS))
    f.append(text(left_x + left_w / 2, pcb_y + 82, "Ризик розтріскування кераміки конденсаторів під час депанелізації", size=9.5, color=POS))

    # Компоненти на платі
    # Безпечний MLCC
    f.append(rect(left_x + 50, pcb_y + 112, 55, 30, fill="#bdc3c7", stroke=LINE, sw=1.2, rx=3))
    f.append(text(left_x + 77, pcb_y + 128, "C1 (OK)", size=10, bold=True, color=INK))
    f.append(text(left_x + 77, pcb_y + 138, "> 3.0 мм", size=9.5, color=FIELD))

    # Небезпечний MLCC (поруч із перемичкою - заборонено)
    f.append(rect(tab_x + 32, pcb_y + 112, 55, 30, fill="#f5b7b1", stroke=POS, sw=1.5, rx=3))
    f.append(text(tab_x + 59, pcb_y + 128, "C2 (БРАК)", size=10, bold=True, color=POS))
    f.append(text(tab_x + 59, pcb_y + 138, "< 1.0 мм", size=9.5, color=POS))

    # Розмірна стрілка заглиблення отворів (Inset = 0.15..0.20 mm)
    f.append(arrow(left_x + 420, pcb_y, left_x + 420, holes_y, color="#2980b9", sw=1.5))
    f.append(text(left_x + 420, pcb_y + 24, "Заглиблення 0.15 мм", size=10, bold=True, color="#2980b9"))

    # Права частина: Інженерні правила та норми
    right_x, right_y, right_w, right_h = 535, 52, 325, 430
    f.append(rect(right_x, right_y, right_w, right_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(right_x + right_w / 2, right_y + 24, "Норми проектування перемичок", size=13, bold=True, color=INK))

    rules = [
        ("Ширина перемички", "3.0 – 5.0 мм (для плати 1.6 мм)"),
        ("Діаметр отворів", "0.50 – 0.80 мм (типово 0.6 мм)"),
        ("Крок отворів (Pitch)", "0.80 – 1.20 мм (місток 0.2..0.4 мм)"),
        ("Зсув лінії центрів", "0.15 – 0.20 мм всередину контуру"),
        ("Зазор до міді", "≥ 0.50 мм від краю отворів"),
        ("Зазор до MLCC", "≥ 2.0 мм (паралельно) / 3.0 мм (вздовж)"),
        ("Зазор до BGA / QFN", "≥ 3.0 – 5.0 мм до корпусу ІС"),
        ("Ширина паза фрези", "2.0 мм або 2.4 мм (стандарт фрез)")
    ]

    for idx, (title_str, val_str) in enumerate(rules):
        ry = right_y + 44 + idx * 36
        f.append(rect(right_x + 10, ry, right_w - 20, 30, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))
        f.append(text(right_x + 18, ry + 19, title_str, size=11, bold=True, color=INK, anchor="start"))
        f.append(text(right_x + right_w - 18, ry + 19, val_str, size=10, bold=False, color="#1e7e34" if "≥" in val_str or "0." in val_str else MUTED, anchor="end"))

    # Блок наслідку заглиблення
    note_y = right_y + right_h - 78
    f.append(rect(right_x + 10, note_y, right_w - 20, 65, fill="#eaf2f8", stroke="#2980b9", sw=1.2, rx=4))
    f.append(text(right_x + right_w / 2, note_y + 18, "Чому отвори заглиблюють (Inset):", size=11, bold=True, color="#1a5276"))
    f.append(text(right_x + right_w / 2, note_y + 36, "Залишки зломаних «вусиків» лишаються", size=10, color="#2471a3"))
    f.append(text(right_x + right_w / 2, note_y + 50, "в заглибині й не заважають монтажу в корпус.", size=10, color="#2471a3"))

    out_path = os.path.join(IMG, 'panel-breakaway-tabs.svg')
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<defs>\n')
        fp.write('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
        fp.write('    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n' % LINE)
        fp.write('  </marker>\n')
        fp.write('</defs>\n')
        fp.write("\n".join(f))
        fp.write('\n</svg>\n')
    print("Generated:", out_path)


# ════════════════════════════════════════════════════════════════════════════
# 2. impedance-test-coupon.svg — Монтажна панель і купон TDR
# ════════════════════════════════════════════════════════════════════════════
def fig_impedance_test_coupon():
    W, H = 880, 500
    f = []

    # Загальний фон
    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))

    # Заголовок
    f.append(text(W / 2, 28, "Розкладка монтажної панелі: репери, отвори та TDR-купон контролю імпедансу", size=16, bold=True, color=INK))

    # Ліва зона: Схема монтажної панелі (Panel Layout)
    p_x, p_y, p_w, p_h = 20, 52, 460, 430
    f.append(rect(p_x, p_y, p_w, p_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(p_x + p_w / 2, p_y + 22, "Монтажна панель (Delivery Assembly Panel)", size=13, bold=True, color=INK))

    # Технологічні поля (Rails)
    rw = 28
    # Верхня рейка
    f.append(rect(p_x + 12, p_y + 35, p_w - 24, rw, fill="#d5e8d4", stroke="#27ae60", sw=1.2, rx=0))
    f.append(text(p_x + p_w / 2, p_y + 53, "Верхнє технологічне поле (Rail 7.0 мм)", size=11, bold=True, color="#1e7e34"))
    # Нижня рейка
    f.append(rect(p_x + 12, p_y + p_h - 35 - rw, p_w - 24, rw, fill="#d5e8d4", stroke="#27ae60", sw=1.2, rx=0))
    f.append(text(p_x + p_w / 2, p_y + p_h - 22 - rw / 2, "Нижнє технологічне поле (Rail 7.0 мм)", size=11, bold=True, color="#1e7e34"))

    # Базові отвори кріплення (Tooling Holes NPTH Ø3.2 мм) у 4 кутах
    f.append(circle(p_x + 26, p_y + 49, 7.0, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(p_x + 26, p_y + 53, "H", size=9.5, bold=True, color=INK))

    f.append(circle(p_x + p_w - 26, p_y + 49, 7.0, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(p_x + p_w - 26, p_y + 53, "H", size=9.5, bold=True, color=INK))

    f.append(circle(p_x + 26, p_y + p_h - 49, 7.0, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(p_x + 26, p_y + p_h - 45, "H", size=9.5, bold=True, color=INK))

    f.append(circle(p_x + p_w - 26, p_y + p_h - 49, 7.0, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(text(p_x + p_w - 26, p_y + p_h - 45, "H", size=9.5, bold=True, color=INK))

    # Глобальні оптичні репери (Global Fiducials - 3 штуки асиметрично)
    # Репер 1 (Top-Left)
    f.append(circle(p_x + 52, p_y + 49, 6.0, fill="#ffffff", stroke="#b87333", sw=1.5))
    f.append(circle(p_x + 52, p_y + 49, 2.5, fill="#b87333", stroke="none"))
    f.append(text(p_x + 52, p_y + 32, "FID1", size=9.5, bold=True, color="#b87333"))

    # Репер 2 (Top-Right)
    f.append(circle(p_x + p_w - 52, p_y + 49, 6.0, fill="#ffffff", stroke="#b87333", sw=1.5))
    f.append(circle(p_x + p_w - 52, p_y + 49, 2.5, fill="#b87333", stroke="none"))
    f.append(text(p_x + p_w - 52, p_y + 32, "FID2", size=9.5, bold=True, color="#b87333"))

    # Репер 3 (Bottom-Left)
    f.append(circle(p_x + 52, p_y + p_h - 49, 6.0, fill="#ffffff", stroke="#b87333", sw=1.5))
    f.append(circle(p_x + 52, p_y + p_h - 49, 2.5, fill="#b87333", stroke="none"))
    f.append(text(p_x + 52, p_y + p_h - 26, "FID3 (захист 180°)", size=9.5, bold=True, color="#b87333"))

    # Матриця 2x2 плати всередині
    board_w = 195
    board_h = 135
    boards = [
        (p_x + 22, p_y + 70, "Плата 1 (PCB #1)"),
        (p_x + 242, p_y + 70, "Плата 2 (PCB #2)"),
        (p_x + 22, p_y + 220, "Плата 3 (PCB #3)"),
        (p_x + 242, p_y + 220, "Плата 4 (PCB #4)")
    ]

    for bx, by, btitle in boards:
        f.append(rect(bx, by, board_w, board_h, fill="#e1d5e7", stroke="#8e44ad", sw=1.5, rx=4))
        f.append(text(bx + board_w / 2, by + 22, btitle, size=11, bold=True, color="#6c3483"))

        # Локальний репер на платі
        f.append(circle(bx + 15, by + board_h - 15, 4.5, fill="#ffffff", stroke="#b87333", sw=1.2))
        f.append(circle(bx + 15, by + board_h - 15, 1.8, fill="#b87333", stroke="none"))
        f.append(text(bx + 48, by + board_h - 11, "Local FID", size=9.5, color="#b87333"))

        # DataMatrix код на платі
        f.append(rect(bx + board_w - 32, by + 10, 22, 22, fill="#333333", stroke="none", rx=1))
        f.append(rect(bx + board_w - 28, by + 14, 6, 6, fill="#ffffff", stroke="none"))
        f.append(rect(bx + board_w - 18, by + 22, 5, 5, fill="#ffffff", stroke="none"))

        # BGA IC у центрі
        f.append(rect(bx + 68, by + 45, 60, 50, fill="#2c3e50", stroke=LINE, sw=1.2, rx=2))
        f.append(text(bx + 98, by + 72, "BGA MCU", size=10, bold=True, color="#ffffff"))

    # Права зона: Тестовий купон імпедансу TDR (Impedance Test Coupon)
    c_x, c_y, c_w, c_h = 495, 52, 365, 430
    f.append(rect(c_x, c_y, c_w, c_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(c_x + c_w / 2, c_y + 22, "Купон контролю імпедансу (TDR Coupon)", size=13, bold=True, color=INK))

    # Опис розташування
    f.append(text(c_x + c_w / 2, c_y + 40, "Розміщується на технологічному полі виробничої панелі", size=10, color=MUTED))

    # Схема купона (вузька смуга довжиною ≥ 150 мм)
    coup_x = c_x + 15
    coup_y = c_y + 55
    coup_w = c_w - 30
    coup_h = 175
    f.append(rect(coup_x, coup_y, coup_w, coup_h, fill="#fff2cc", stroke="#d6b656", sw=1.5, rx=6))

    # 1. Одинарна мікросмужкова лінія 50 Ом (Single-ended Microstrip)
    f.append(text(coup_x + 12, coup_y + 25, "1. Одинарна лінія 50 Ω (SE Microstrip):", size=10, bold=True, color="#7d5a00", anchor="start"))
    # Контактні майданчики GSG (Ground-Signal-Ground)
    f.append(rect(coup_x + 12, coup_y + 35, 14, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    f.append(text(coup_x + 19, coup_y + 48, "G", size=9.5, bold=True, color="#ffffff"))
    f.append(rect(coup_x + 30, coup_y + 35, 14, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    f.append(text(coup_x + 37, coup_y + 48, "S", size=9.5, bold=True, color="#ffffff"))
    f.append(rect(coup_x + 48, coup_y + 35, 14, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    f.append(text(coup_x + 55, coup_y + 48, "G", size=9.5, bold=True, color="#ffffff"))
    # Доріжка
    f.append(line(coup_x + 65, coup_y + 44, coup_x + coup_w - 20, coup_y + 44, color="#b87333", sw=3.5))
    f.append(text(coup_x + coup_w - 15, coup_y + 47, "50 Ω", size=10, bold=True, color="#7d5a00", anchor="start"))

    # 2. Диференційна пара 100 Ом (Differential Stripline)
    f.append(text(coup_x + 12, coup_y + 80, "2. Диференційна пара 100 Ω (Diff Pair):", size=10, bold=True, color="#7d5a00", anchor="start"))
    # Пади GS-SG
    f.append(rect(coup_x + 12, coup_y + 90, 12, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    f.append(rect(coup_x + 26, coup_y + 90, 12, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    f.append(rect(coup_x + 40, coup_y + 90, 12, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    f.append(rect(coup_x + 54, coup_y + 90, 12, 18, fill="#b87333", stroke=LINE, sw=1, rx=2))
    # Дві паралельні доріжки
    f.append(line(coup_x + 70, coup_y + 95, coup_x + coup_w - 25, coup_y + 95, color="#b87333", sw=2.5))
    f.append(line(coup_x + 70, coup_y + 103, coup_x + coup_w - 25, coup_y + 103, color="#b87333", sw=2.5))
    f.append(text(coup_x + coup_w - 18, coup_y + 102, "100 Ω", size=10, bold=True, color="#7d5a00", anchor="start"))

    # 3. Купон мікрошліфа отворів (PTH Hole Coupon)
    f.append(text(coup_x + 12, coup_y + 135, "3. Купон шліфа металізації отворів (IPC-TM-650):", size=10, bold=True, color="#7d5a00", anchor="start"))
    for h_idx in range(6):
        hx = coup_x + 30 + h_idx * 28
        f.append(circle(hx, coup_y + 155, 7.5, fill="#b87333", stroke=LINE, sw=1.2))
        f.append(circle(hx, coup_y + 155, 4.0, fill="#ffffff", stroke=LINE, sw=1))
    f.append(text(coup_x + coup_w - 60, coup_y + 158, "Daisy Chain", size=9.5, color=MUTED))

    # Секція з вимогами TDR
    tdr_y = c_y + 245
    tdr_h = 170
    f.append(rect(c_x + 15, tdr_y, c_w - 30, tdr_h, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))
    f.append(text(c_x + c_w / 2, tdr_y + 22, "Параметри тесту рефлектометром (TDR):", size=11, bold=True, color=INK))

    tdr_points = [
        "Довжина лінії L ≥ 150 мм (для виходу на полицю Z0)",
        "Фронт імпульсу tr = 20–35 пс (смуга до 20 ГГц)",
        "Точність контролю імпедансу: ±5% або ±10%",
        "Відсутність компонентів (чиста лінія передачі)",
        "Шліф (Microsection): товщина міді в отворі ≥ 20–25 мкм",
        "Тест на термошок: плавання в припої 288 °C / 10 с"
    ]

    for idx, pt in enumerate(tdr_points):
        f.append(circle(c_x + 30, tdr_y + 44 + idx * 20, 3, fill="#27ae60", stroke="none"))
        f.append(text(c_x + 40, tdr_y + 48 + idx * 20, pt, size=9.5, color=INK, anchor="start"))

    out_path = os.path.join(IMG, 'impedance-test-coupon.svg')
    with open(out_path, 'w', encoding='utf-8') as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<defs>\n')
        fp.write('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
        fp.write('    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n' % LINE)
        fp.write('  </marker>\n')
        fp.write('</defs>\n')
        fp.write("\n".join(f))
        fp.write('\n</svg>\n')
    print("Generated:", out_path)


if __name__ == "__main__":
    fig_panel_breakaway_tabs()
    fig_impedance_test_coupon()