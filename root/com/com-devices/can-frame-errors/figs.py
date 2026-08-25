# -*- coding: utf-8 -*-
"""Фігури до теми «Кадр CAN».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Структура кадру CAN (Standard 2.0A та Extended 2.0B) ───────────────────
def fig_frame_structure():
    W, H = 840, 460
    f = [text(W / 2, 26, "Структура кадру даних CAN (Standard 2.0A та Extended 2.0B)",
              size=14.5, bold=True)]

    # Заголовок блоку 2.0A
    f.append(text(40, 60, "Стандартний кадр (CAN 2.0A — 11-бітний ідентифікатор):",
                  size=12, bold=True, anchor="start", color=INK))

    # Поля кадру 2.0A: (x, w, label, bits, color_type)
    # Загальна ширина під поля = 760 (від x=40 до x=800)
    fields_20a = [
        ("SOF", 36, "1 б", "#eaf0fd", NEG),
        ("Identifier", 110, "11 б", "#eafaf1", FIELD),
        ("RTR", 36, "1 б", "#fdecea", POS),
        ("IDE", 36, "1 б (0)", "#f4f6f8", MUTED),
        ("r0", 30, "1 б", "#f4f6f8", MUTED),
        ("DLC", 54, "4 б", "#fef9e7", "#b7950b"),
        ("Data Field", 170, "0..8 байтів (0..64 б)", "#eafaf1", FIELD),
        ("CRC Field", 100, "15 б + Del (1б)", "#eaf0fd", NEG),
        ("ACK", 60, "Slot + Del", "#fdecea", POS),
        ("EOF", 70, "7 б (рецес.)", "#f4f6f8", MUTED),
        ("IFS", 58, "ITM 3б", "#f4f6f8", MUTED),
    ]

    curr_x = 40
    y_top = 75
    h_box = 48
    for name, bw, bits, fill, stroke in fields_20a:
        f.append(rect(curr_x, y_top, bw, h_box, fill=fill, stroke=stroke, sw=1.5, rx=4))
        f.append(text(curr_x + bw / 2, y_top + 20, name, size=11, bold=True, color=stroke))
        f.append(text(curr_x + bw / 2, y_top + 38, bits, size=9.5, color=MUTED))
        curr_x += bw

    # Зона Bit Stuffing для 2.0A
    # Від SOF (x=40) до кінця CRC (без делімітера) ~ x=40+36+110+36+36+30+54+170+84 = 596
    f.append(line(40, 134, 596, 134, color=FIELD, sw=2))
    f.append(line(40, 130, 40, 138, color=FIELD, sw=2))
    f.append(line(596, 130, 596, 138, color=FIELD, sw=2))
    f.append(text(318, 148, "Зона дії бітового заповнення (Bit Stuffing: SOF → CRC)",
                  size=10, bold=True, color=FIELD))

    # Зона фіксованого формату для 2.0A
    f.append(line(596, 134, 800, 134, color=POS, sw=2))
    f.append(line(800, 130, 800, 138, color=POS, sw=2))
    f.append(text(698, 148, "Фіксований формат (без стафінгу)",
                  size=10, bold=True, color=POS))

    # Розділювач
    f.append(line(40, 172, 800, 172, color="#e0e0e0", sw=1, dash="4,4"))

    # Заголовок блоку 2.0B
    f.append(text(40, 202, "Розширений кадр (CAN 2.0B — 29-бітний ідентифікатор):",
                  size=12, bold=True, anchor="start", color=INK))

    fields_20b = [
        ("SOF", 34, "1 б", "#eaf0fd", NEG),
        ("Base ID", 86, "11 б", "#eafaf1", FIELD),
        ("SRR", 34, "1 б (1)", "#fdecea", POS),
        ("IDE", 34, "1 б (1)", "#fdecea", POS),
        ("Ext ID", 112, "18 б", "#eafaf1", FIELD),
        ("RTR", 34, "1 б", "#fdecea", POS),
        ("r1, r0", 40, "2 б", "#f4f6f8", MUTED),
        ("DLC", 46, "4 б", "#fef9e7", "#b7950b"),
        ("Data Field", 140, "0..8 байтів", "#eafaf1", FIELD),
        ("CRC", 88, "15 б + Del", "#eaf0fd", NEG),
        ("ACK", 56, "Slot+Del", "#fdecea", POS),
        ("EOF", 56, "7 б", "#f4f6f8", MUTED),
        ("IFS", 40, "3 б", "#f4f6f8", MUTED),
    ]

    curr_x = 40
    y_ext = 217
    for name, bw, bits, fill, stroke in fields_20b:
        f.append(rect(curr_x, y_ext, bw, h_box, fill=fill, stroke=stroke, sw=1.5, rx=4))
        f.append(text(curr_x + bw / 2, y_ext + 20, name, size=10.5, bold=True, color=stroke))
        f.append(text(curr_x + bw / 2, y_ext + 38, bits, size=9, color=MUTED))
        curr_x += bw

    # Пояснювальні картки знизу
    b1, _, _ = textbox(230, 335,
                       "Пріоритет арбітражу:\nSRR = 1 (рецесивний) у 2.0B гарантує,\nщо 2.0A з тим самим Base ID виграє арбітраж",
                       size=10.5, fill="#fdfefe", stroke=MUTED)
    b2, _, _ = textbox(610, 335,
                       "Апаратне підтвердження (ACK):\nПередавач шле '1' (рецесивний),\nбудь-який коректний приймач шле '0' (домінантний)",
                       size=10.5, fill="#fdfefe", stroke=MUTED)
    f.append(b1)
    f.append(b2)

    # Підсумок унизу
    b_bot, _, _ = textbox(W / 2, 420,
                          "Разом: кадри CAN містять суворе чергування полів динамічного стафінгу та фіксованих делімітерів",
                          size=11, fill="#f4f6f8", stroke=INK)
    f.append(b_bot)

    render(os.path.join(IMG, "frame-structure.svg"), W, H, *f)


# ── 2. Механізм бітового заповнення (Bit Stuffing) ────────────────────────────
def fig_bit_stuffing():
    W, H = 820, 380
    f = [text(W / 2, 26, "Механізм бітового заповнення (Bit Stuffing) та дестафінгу в CAN",
              size=14.5, bold=True)]

    # 1. Сирий потік даних
    f.append(text(40, 64, "1. Сирий потік даних передавача (без стафінгу):", size=12, bold=True, anchor="start"))
    raw_bits = ["1", "1", "1", "1", "1", "0", "0", "0", "0", "0", "0", "1", "0", "1"]
    x0 = 40
    cell_w = 46
    cell_h = 36
    y1 = 78
    for i, b in enumerate(raw_bits):
        col = POS if b == "0" else NEG
        fill = "#fdecea" if b == "0" else "#eaf0fd"
        # виділення блоку з 5 однакових
        if i < 5 or (5 <= i <= 9):
            fill = "#fff9c4"
        f.append(rect(x0 + i * cell_w, y1, cell_w - 4, cell_h, fill=fill, stroke=col, sw=1.4, rx=4))
        f.append(text(x0 + i * cell_w + (cell_w - 4) / 2, y1 + 23, b, size=13, bold=True, color=col))

    f.append(text(x0 + 2.5 * cell_w, y1 + cell_h + 14, "5 послідовних «1»", size=9.5, color=MUTED))
    f.append(text(x0 + 7.5 * cell_w, y1 + cell_h + 14, "5 послідовних «0»", size=9.5, color=MUTED))

    # 2. Потік на шині зі вставленими стаф-бітами
    f.append(text(40, 160, "2. Реальний потік на шині (контролер вставляє інверсний біт):", size=12, bold=True, anchor="start"))
    stuffed_bits = [
        ("1", False), ("1", False), ("1", False), ("1", False), ("1", False),
        ("0", True),  # стаф-біт!
        ("0", False), ("0", False), ("0", False), ("0", False), ("0", False),
        ("1", True),  # стаф-біт!
        ("0", False), ("1", False), ("0", False), ("1", False)
    ]
    y2 = 174
    for i, (b, is_stuff) in enumerate(stuffed_bits):
        if is_stuff:
            col = "#8e44ad"
            fill = "#f4ecf7"
            sw = 2.2
        else:
            col = POS if b == "0" else NEG
            fill = "#fdecea" if b == "0" else "#eaf0fd"
            sw = 1.2
        f.append(rect(x0 + i * cell_w, y2, cell_w - 4, cell_h, fill=fill, stroke=col, sw=sw, rx=4))
        f.append(text(x0 + i * cell_w + (cell_w - 4) / 2, y2 + 23, b, size=13, bold=True, color=col))
        if is_stuff:
            f.append(text(x0 + i * cell_w + (cell_w - 4) / 2, y2 + cell_h + 14, "стаф", size=9.5, bold=True, color=col))

    # 3. Правило Stuff Error
    b_err, _, _ = textbox(W / 2, 290,
                          "Правило детекції Stuff Error:\nЯкщо приймач бачить 6 однакових бітів підряд у зоні стафінгу (SOF → CRC),\nвін негайно фіксує помилку стафінгу та перериває кадр активним прапорцем помилки!",
                          size=11, fill="#fdecea", stroke=POS)
    f.append(b_err)

    b_bot, _, _ = textbox(W / 2, 355,
                          "Призначення: 1) гарантовані фронти перепаду напруг для ресинхронізації; 2) розрізнення даних та Error Flag",
                          size=10.5, fill="#f4f6f8", stroke=MUTED)
    f.append(b_bot)

    render(os.path.join(IMG, "bit-stuffing.svg"), W, H, *f)


# ── 3. Каскадна сигналізація помилки (Active Error Frame) ──────────────────────
def fig_error_signaling_cascade():
    W, H = 820, 430
    f = [text(W / 2, 26, "Каскадне сповіщення про помилку та глобальне знищення кадру",
              size=14.5, bold=True)]

    # Горизонтальна шкала часу
    f.append(line(60, 58, 760, 58, color=INK, sw=1.5))
    f.append(arrow(750, 58, 765, 58, color=INK, sw=1.5))
    f.append(text(765, 50, "час (t)", size=10.5, color=MUTED, anchor="end"))

    # Вузол 1 (передавач або приймач, що першим виявив збій)
    y_n1 = 90
    f.append(text(40, y_n1 + 22, "Вузол A\n(виявив)", size=10.5, bold=True, anchor="start", color=POS))
    f.append(rect(140, y_n1, 190, 44, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(235, y_n1 + 19, "Active Error Flag", size=11, bold=True, color=POS))
    f.append(text(235, y_n1 + 35, "6 домінантних бітів ('0')", size=9.5, color=POS))

    f.append(rect(340, y_n1, 220, 44, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(450, y_n1 + 19, "Error Delimiter", size=11, bold=True, color=NEG))
    f.append(text(450, y_n1 + 35, "8 рецесивних бітів ('1')", size=9.5, color=NEG))

    # Вузол 2 та 3 (бачать порушення bit stuffing через домінантний сигнал Вузла A)
    y_n2 = 160
    f.append(text(40, y_n2 + 22, "Вузол B\n(інші)", size=10.5, bold=True, anchor="start", color=MUTED))
    f.append(rect(140, y_n2, 70, 44, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    f.append(text(175, y_n2 + 26, "прийом...", size=10, color=MUTED))

    # Вузол B фіксує Stuff Error і шле власний прапорець (зсунутий)
    f.append(rect(210, y_n2, 190, 44, fill="#fdecea", stroke=POS, sw=2, rx=6))
    f.append(text(305, y_n2 + 19, "Active Error Flag", size=11, bold=True, color=POS))
    f.append(text(305, y_n2 + 35, "6 домінантних бітів ('0')", size=9.5, color=POS))

    f.append(rect(410, y_n2, 220, 44, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(520, y_n2 + 19, "Error Delimiter", size=11, bold=True, color=NEG))
    f.append(text(520, y_n2 + 35, "8 рецесивних бітів ('1')", size=9.5, color=NEG))

    # Результуючий рівень на спільній шині (суперпозиція дротового-І)
    y_bus = 240
    f.append(text(40, y_bus + 22, "Шина CAN\n(дротове-І)", size=11, bold=True, anchor="start", color=INK))

    # Домінантне перекриття: від 140 до 400 (ширина 260 px = 6..12 бітів)
    f.append(rect(140, y_bus, 260, 44, fill="#f9ebea", stroke=POS, sw=2.5, rx=6))
    f.append(text(270, y_bus + 19, "Спільний домінантний рівень шини", size=11.5, bold=True, color=POS))
    f.append(text(270, y_bus + 35, "Суперпозиція: від 6 до 12 домінантних бітів", size=9.5, color=POS))

    # Спільний делімітер: від 410 до 630
    f.append(rect(410, y_bus, 220, 44, fill="#ebf5fb", stroke=NEG, sw=2, rx=6))
    f.append(text(520, y_bus + 19, "Спільний Error Delimiter", size=11, bold=True, color=NEG))
    f.append(text(520, y_bus + 35, "8 рецесивних бітів перед IFS", size=9.5, color=NEG))

    # Пояснення ефекту
    b_info, _, _ = textbox(W / 2, 335,
                           "Атомарність (Atomic Broadcast): або всі вузли приймають кадр бездоганно,\nабо будь-який вузол руйнує його для всієї мережі одночасно, запобігаючи споживанню хибних даних",
                           size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b_info)

    b_sub, _, _ = textbox(W / 2, 398,
                          "Після 8 рецесивних бітів делімітера та 3 бітів Intermission передавач негайно повторює кадр",
                          size=10.5, fill="#f4f6f8", stroke=MUTED)
    f.append(b_sub)

    render(os.path.join(IMG, "error-signaling-cascade.svg"), W, H, *f)


# ── 4. Скінченний автомат станів вузла (Fault Confinement) ─────────────────────
def fig_fault_confinement_fsm():
    W, H = 820, 450
    f = [text(W / 2, 26, "Локалізація несправностей: скінченний автомат станів вузла CAN",
              size=14.5, bold=True)]

    # Три основні блоки станів: Error Active, Error Passive, Bus Off
    # Box 1: Error Active (зліва)
    box1_w, box1_h = 220, 140
    b1_x, b1_y = 150, 140
    f.append(rect(b1_x - box1_w / 2, b1_y - box1_h / 2, box1_w, box1_h,
                  fill="#eafaf1", stroke=FIELD, sw=2.2, rx=8))
    f.append(text(b1_x, b1_y - 45, "ERROR ACTIVE", size=13, bold=True, color=FIELD))
    f.append(text(b1_x, b1_y - 25, "TEC < 128  ТА  REC < 128", size=10.5, bold=True, color=INK))
    f.append(text(b1_x, b1_y - 2, "• Повноправний учасник", size=10, color=INK))
    f.append(text(b1_x, b1_y + 16, "• Шле Active Error Flag", size=10, bold=True, color=POS))
    f.append(text(b1_x, b1_y + 34, "  (6 домінантних бітів)", size=9.5, color=MUTED))
    f.append(text(b1_x, b1_y + 52, "• Звичайна пауза IFS (3 біти)", size=9.5, color=MUTED))

    # Box 2: Error Passive (посередині)
    box2_w, box2_h = 230, 140
    b2_x, b2_y = 440, 140
    f.append(rect(b2_x - box2_w / 2, b2_y - box2_h / 2, box2_w, box2_h,
                  fill="#fef9e7", stroke="#d4ac0d", sw=2.2, rx=8))
    f.append(text(b2_x, b2_y - 45, "ERROR PASSIVE", size=13, bold=True, color="#b7950b"))
    f.append(text(b2_x, b2_y - 25, "TEC ≥ 128  АБО  REC ≥ 128", size=10.5, bold=True, color=INK))
    f.append(text(b2_x, b2_y - 2, "• Підозра на несправність", size=10, color=INK))
    f.append(text(b2_x, b2_y + 16, "• Шле Passive Error Flag", size=10, bold=True, color=NEG))
    f.append(text(b2_x, b2_y + 34, "  (6 рецесивних бітів)", size=9.5, color=MUTED))
    f.append(text(b2_x, b2_y + 52, "• Suspend Transmission (+8 б)", size=9.5, color=POS))

    # Box 3: Bus Off (справа)
    box3_w, box3_h = 180, 140
    b3_x, b3_y = 710, 140
    f.append(rect(b3_x - box3_w / 2, b3_y - box3_h / 2, box3_w, box3_h,
                  fill="#fdecea", stroke=POS, sw=2.2, rx=8))
    f.append(text(b3_x, b3_y - 45, "BUS OFF", size=13, bold=True, color=POS))
    f.append(text(b3_x, b3_y - 25, "TEC > 255", size=11, bold=True, color=POS))
    f.append(text(b3_x, b3_y - 2, "• Вузол ізольовано", size=10, bold=True, color=INK))
    f.append(text(b3_x, b3_y + 16, "• Трансивер відключено", size=10, color=INK))
    f.append(text(b3_x, b3_y + 34, "  від ведення ліній", size=9.5, color=MUTED))
    f.append(text(b3_x, b3_y + 52, "• Не шле жодних бітів", size=9.5, color=MUTED))

    # Стрілки переходів
    # Active -> Passive (пряма праворуч)
    f.append(arrow(260, 120, 325, 120, color="#b7950b", sw=2))
    f.append(text(292, 110, "TEC ≥ 128 | REC ≥ 128", size=9, bold=True, color="#b7950b"))

    # Passive -> Active (зворотна ліворуч)
    f.append(arrow(325, 160, 260, 160, color=FIELD, sw=2))
    f.append(text(292, 175, "TEC ≤ 127 & REC ≤ 127", size=9, bold=True, color=FIELD))

    # Passive -> Bus Off
    f.append(arrow(555, 140, 620, 140, color=POS, sw=2))
    f.append(text(587, 130, "TEC > 255", size=9.5, bold=True, color=POS))

    # Bus Off -> Active (довга дуга відновлення знизу)
    # Траєкторія через полілінію
    f.append(line(710, 210, 710, 255, color=FIELD, sw=1.8))
    f.append(line(710, 255, 150, 255, color=FIELD, sw=1.8))
    f.append(arrow(150, 255, 150, 210, color=FIELD, sw=1.8))
    f.append(text(430, 246, "Відновлення (Recovery): прослуховування 128 × 11 рецесивних бітів → TEC=0, REC=0",
                  size=10, bold=True, color=FIELD))

    # Таблиця правил лічильників
    b_rules, _, _ = textbox(W / 2, 335,
                            "Ваги лічильників помилок (асиметрична шкала покарання):\n"
                            "• Помилка при передачі (Tx Error): TEC += 8   (передавач відповідає за спотворення)\n"
                            "• Помилка при прийомі (Rx Error):  REC += 1   (захист приймачів від чужих шумів)\n"
                            "• Успішна передача кадру:          TEC -= 1   |   Успішний прийом кадру: REC -= 1",
                            size=10.5, fill="#f4f6f8", stroke=INK)
    f.append(b_rules)

    b_ft, _, _ = textbox(W / 2, 415,
                         "Результат: зламаний передавач ізолюється за 32 помилки поспіль, не руйнуючи зв'язок решти мережі",
                         size=10.5, fill="#eafaf1", stroke=FIELD)
    f.append(b_ft)

    render(os.path.join(IMG, "fault-confinement-fsm.svg"), W, H, *f)


# ── 5. Порівняння Classical CAN 2.0 та CAN FD ─────────────────────────────────
def fig_can_fd_comparison():
    W, H = 820, 410
    f = [text(W / 2, 26, "Класичний CAN 2.0 проти CAN FD (Flexible Data-rate)",
              size=14.5, bold=True)]

    # 1. Classical CAN 2.0
    f.append(text(40, 62, "Classical CAN 2.0 (єдина швидкість, макс. 8 байтів даних):",
                  size=12, bold=True, anchor="start"))
    # Смуга кадру 2.0
    f.append(rect(40, 76, 740, 46, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(120, 96, "Арбітраж (11/29 б)", size=11, bold=True, color=INK))
    f.append(text(120, 112, "500 кбіт/с", size=9.5, color=MUTED))

    f.append(line(200, 76, 200, 122, color=NEG, sw=1.2))
    f.append(text(380, 96, "Дані (0..8 байтів) + CRC-15", size=11.5, bold=True, color=POS))
    f.append(text(380, 112, "500 кбіт/с (фіксована швидкість арбітражу)", size=9.5, color=MUTED))

    f.append(line(580, 76, 580, 122, color=NEG, sw=1.2))
    f.append(text(680, 96, "ACK + EOF", size=11, bold=True, color=INK))
    f.append(text(680, 112, "500 кбіт/с", size=9.5, color=MUTED))

    # 2. CAN FD
    f.append(text(40, 160, "CAN FD (двошвидкісний режим, до 64 байтів даних):",
                  size=12, bold=True, anchor="start"))

    # Фаза арбітражу (номінальна швидкість)
    f.append(rect(40, 174, 180, 52, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(130, 196, "Фаза арбітражу", size=11, bold=True, color=INK))
    f.append(text(130, 214, "500 кбіт/с (SOF, ID, BRS)", size=9.5, color=NEG))

    # Фаза даних (прискорена швидкість)
    f.append(rect(225, 174, 395, 52, fill="#fdecea", stroke=POS, sw=2.4, rx=6))
    f.append(text(422, 196, "ПРИСКОРЕНА ФАЗА ДАНИХ (до 64 байтів) + CRC-17/21", size=11, bold=True, color=POS))
    f.append(text(422, 214, "2..5..8 Мбіт/с (перемикання бітом BRS = 1)", size=9.5, bold=True, color=POS))

    # Фаза підтвердження (повернення до номінальної швидкості)
    f.append(rect(625, 174, 155, 52, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(702, 196, "Фаза ACK / EOF", size=11, bold=True, color=INK))
    f.append(text(702, 214, "500 кбіт/с (CRC Del → EOF)", size=9.5, color=NEG))

    # Стрілочки перемикання швидкості
    f.append(arrow(220, 162, 230, 174, color=POS, sw=2))
    f.append(text(225, 152, "BRS Sample Point ↑", size=9, bold=True, color=POS))

    f.append(arrow(620, 174, 630, 162, color=NEG, sw=2))
    f.append(text(625, 152, "CRC Delimiter SP ↓", size=9, bold=True, color=NEG))

    # Інновації CAN FD внизу
    b_innov, _, _ = textbox(W / 2, 290,
                            "Ключові вдосконалення CAN FD (ISO 11898-1:2015):\n"
                            "• Пропускна здатність: до 8 разів вища за рахунок розгону фази даних до 2–8 Мбіт/с\n"
                            "• Обсяг корисного навантаження: розширено з 8 до 64 байтів на кадр (менший оверхед)\n"
                            "• Fixed Stuff Bits у полі CRC + Stuff Count (3 біти коду Грея): усунення вразливості каскадного стафінгу",
                            size=10.5, fill="#fef9e7", stroke="#d4ac0d")
    f.append(b_innov)

    b_ft2, _, _ = textbox(W / 2, 375,
                          "Сумісність: фаза арбітражу залишається надійним побітовим голосуванням з повним RTT",
                          size=10.5, fill="#f4f6f8", stroke=MUTED)
    f.append(b_ft2)

    render(os.path.join(IMG, "can-fd-comparison.svg"), W, H, *f)


if __name__ == "__main__":
    fig_frame_structure()
    fig_bit_stuffing()
    fig_error_signaling_cascade()
    fig_fault_confinement_fsm()
    fig_can_fd_comparison()
    print("All figures generated successfully.")
