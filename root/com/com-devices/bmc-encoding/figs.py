# -*- coding: utf-8 -*-
"""Фігури до теми «BMC-кодування: як USB-C передає біти по CC».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (імпорт із scripts/)."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Порівняння кодувань NRZ, Manchester та BMC ────────────────────────────
def fig_bmc_waveform():
    W, H = 840, 480
    f = [text(W / 2, 28, "Порівняння лінійних кодів: NRZ, Manchester та BMC", size=16, bold=True)]

    # Бітова послідовність
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    n_bits = len(bits)
    x_start = 130
    bit_w = 80
    total_w = n_bits * bit_w

    # Заголовок шкали бітів
    for i, b in enumerate(bits):
        bx = x_start + i * bit_w
        # Вертикальні пунктири меж бітів
        f.append(line(bx, 52, bx, 410, color="#d1d5db", sw=1.0, dash="3,3"))
        # Бітова мітка
        f.append(text(bx + bit_w / 2, 68, "біти: %d" % b if i == 0 else str(b), size=13, color=INK, bold=True))
    f.append(line(x_start + total_w, 52, x_start + total_w, 410, color="#d1d5db", sw=1.0, dash="3,3"))

    # 1. NRZ-L
    y1_top, y1_bot = 95, 145
    f.append(text(x_start - 15, (y1_top + y1_bot) / 2 + 4, "NRZ-L", size=13, color=INK, anchor="end", bold=True))
    nrz_pts = []
    curr_lvl = None
    for i, b in enumerate(bits):
        bx = x_start + i * bit_w
        lvl = y1_top if b == 1 else y1_bot
        if i > 0 and lvl != curr_lvl:
            nrz_pts.append((bx, curr_lvl))
            nrz_pts.append((bx, lvl))
        elif i == 0:
            nrz_pts.append((bx, lvl))
        nrz_pts.append((bx + bit_w, lvl))
        curr_lvl = lvl
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in nrz_pts), POS))
    f.append(text(x_start + total_w + 12, (y1_top + y1_bot) / 2 + 4, "втрата синхронізації на '00'", size=11, color=MUTED, anchor="start"))

    # 2. Manchester (IEEE 802.3: 0 = Low->High, 1 = High->Low)
    y2_top, y2_bot = 180, 230
    f.append(text(x_start - 15, (y2_top + y2_bot) / 2 + 4, "Manchester", size=13, color=INK, anchor="end", bold=True))
    man_pts = []
    curr_end_lvl = None
    for i, b in enumerate(bits):
        bx = x_start + i * bit_w
        mid_x = bx + bit_w / 2
        start_lvl = y2_top if b == 1 else y2_bot
        end_lvl = y2_bot if b == 1 else y2_top
        if i > 0 and start_lvl != curr_end_lvl:
            man_pts.append((bx, curr_end_lvl))
            man_pts.append((bx, start_lvl))
        elif i == 0:
            man_pts.append((bx, start_lvl))
        man_pts.append((mid_x, start_lvl))
        man_pts.append((mid_x, end_lvl))
        man_pts.append((bx + bit_w, end_lvl))
        curr_end_lvl = end_lvl
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in man_pts), NEG))
    f.append(text(x_start + total_w + 12, (y2_top + y2_bot) / 2 + 4, "чутливий до інверсії фази", size=11, color=MUTED, anchor="start"))

    # 3. BMC (Biphase Mark Code)
    y3_top, y3_bot = 265, 315
    f.append(text(x_start - 15, (y3_top + y3_bot) / 2 + 4, "BMC (USB PD)", size=13, color=FIELD, anchor="end", bold=True))
    bmc_pts = []
    curr_state = 0  # 0 = bot, 1 = top
    for i, b in enumerate(bits):
        bx = x_start + i * bit_w
        mid_x = bx + bit_w / 2
        # Transition at start of cell
        curr_state = 1 - curr_state
        lvl_start = y3_top if curr_state == 1 else y3_bot
        if i == 0:
            bmc_pts.append((bx, lvl_start))
        else:
            prev_lvl = y3_top if (1 - curr_state) == 1 else y3_bot
            bmc_pts.append((bx, prev_lvl))
            bmc_pts.append((bx, lvl_start))

        if b == 1:
            # Transition in middle
            bmc_pts.append((mid_x, lvl_start))
            curr_state = 1 - curr_state
            lvl_mid = y3_top if curr_state == 1 else y3_bot
            bmc_pts.append((mid_x, lvl_mid))
            bmc_pts.append((bx + bit_w, lvl_mid))
        else:
            # No transition in middle
            bmc_pts.append((bx + bit_w, lvl_start))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in bmc_pts), FIELD))
    f.append(text(x_start + total_w + 12, (y3_top + y3_bot) / 2 + 4, "самотактування + інваріантність", size=11, color=FIELD, anchor="start", bold=True))

    # 4. BMC Inverted (показати інваріантність)
    y4_top, y4_bot = 350, 400
    f.append(text(x_start - 15, (y4_top + y4_bot) / 2 + 4, "BMC (інверсія)", size=13, color=MUTED, anchor="end"))
    bmc_inv_pts = []
    for x, y in bmc_pts:
        mapped_y = y4_bot if abs(y - y3_top) < 1 else y4_top
        bmc_inv_pts.append((x, mapped_y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5,3"/>'
             % (" ".join("%.1f,%.1f" % p for p in bmc_inv_pts), "#7c3aed"))
    f.append(text(x_start + total_w + 12, (y4_top + y4_bot) / 2 + 4, "декодує ті самі біти: 1 0 1 1 0 0 1 0", size=11, color="#7c3aed", anchor="start"))

    # Пояснювальний блок
    b, _, _ = textbox(W / 2, 448,
                      "BMC міняє рівень на початку кожного біта. Логічна '1' додає перехід у середині інтервалу, '0' лишає рівень незмінним.\nІнформація закодована в наявності переходів, а не в полярності напруги, тому інверсія сигналу не спотворює дані.",
                      size=11, fill="#f0fdf4", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "bmc-waveform.svg"), W, H, *f)


# ── 2. Апаратна структура лінії CC: DC-розпізнавання та BMC PHY ─────────────
def fig_cc_line_mux():
    W, H = 840, 440
    f = [text(W / 2, 26, "Апаратна комутація лінії CC: статичний DC-режим та BMC-трансивер", size=16, bold=True)]

    # Ліва частина: Порт джерела (Source)
    f.append(rect(40, 55, 340, 310, fill="#f8fafc", stroke=LINE, rx=8))
    f.append(text(210, 80, "USB PD Source (Контролер джерела)", size=14, bold=True))

    # Rp підтяжка та комутатор
    f.append(rect(65, 105, 130, 60, fill="#fff", stroke=MUTED))
    f.append(text(130, 128, "Підтяжка Rp", size=12, bold=True))
    f.append(text(130, 148, "56k / 22k / 10k", size=11, color=MUTED))

    f.append(rect(225, 105, 130, 60, fill="#fff", stroke=MUTED))
    f.append(text(290, 128, "ADC / Компаратор", size=12, bold=True))
    f.append(text(290, 148, "Виявлення пристрою", size=11, color=MUTED))

    # Перемикач режимів / BMC PHY
    f.append(rect(65, 195, 290, 145, fill="#eff6ff", stroke=NEG, rx=6))
    f.append(text(210, 220, "BMC Фізичний рівень (PHY)", size=13, color=NEG, bold=True))

    f.append(rect(85, 240, 115, 80, fill="#fff", stroke=NEG))
    f.append(text(142, 265, "Драйвер TX", size=12, bold=True))
    f.append(text(142, 285, "Push-Pull", size=11, color=MUTED))
    f.append(text(142, 303, "0 .. 1.12 В (300 кбіт/с)", size=10, color=NEG))

    f.append(rect(220, 240, 115, 80, fill="#fff", stroke=NEG))
    f.append(text(277, 265, "Приймач RX", size=12, bold=True))
    f.append(text(277, 285, "Компаратор V_th", size=11, color=MUTED))
    f.append(text(277, 303, "Поріг ≈ 0.55 В", size=10, color=NEG))

    # Центральна частина: Провід CC в кабелі
    f.append(line(380, 185, 460, 185, color=FIELD, sw=3.5))
    f.append(text(420, 172, "Лінія CC", size=13, color=FIELD, bold=True))
    f.append(text(420, 204, "1 провід", size=11, color=MUTED))
    f.append(text(420, 220, "C_cable ≤ 1 нФ", size=10, color=MUTED))

    # Права частина: Порт приймача (Sink)
    f.append(rect(460, 55, 340, 310, fill="#f8fafc", stroke=LINE, rx=8))
    f.append(text(630, 80, "USB PD Sink (Контролер пристрою)", size=14, bold=True))

    # Rd підтяжка та компаратор
    f.append(rect(485, 105, 130, 60, fill="#fff", stroke=MUTED))
    f.append(text(550, 128, "Підтяжка Rd", size=12, bold=True))
    f.append(text(550, 148, "5.1 кОм на GND", size=11, color=MUTED))

    f.append(rect(645, 105, 130, 60, fill="#fff", stroke=MUTED))
    f.append(text(710, 128, "ADC / Детектор", size=12, bold=True))
    f.append(text(710, 148, "Оцінка струму Rp", size=11, color=MUTED))

    # BMC PHY на Sink
    f.append(rect(485, 195, 290, 145, fill="#eff6ff", stroke=NEG, rx=6))
    f.append(text(630, 220, "BMC Фізичний рівень (PHY)", size=13, color=NEG, bold=True))

    f.append(rect(505, 240, 115, 80, fill="#fff", stroke=NEG))
    f.append(text(562, 265, "Приймач RX", size=12, bold=True))
    f.append(text(562, 285, "Компаратор V_th", size=11, color=MUTED))
    f.append(text(562, 303, "Поріг ≈ 0.55 В", size=10, color=NEG))

    f.append(rect(640, 240, 115, 80, fill="#fff", stroke=NEG))
    f.append(text(697, 265, "Драйвер TX", size=12, bold=True))
    f.append(text(697, 285, "Push-Pull", size=11, color=MUTED))
    f.append(text(697, 303, "0 .. 1.12 В (300 кбіт/с)", size=10, color=NEG))

    # З'єднання всередині Source і Sink до лінії CC
    f.append(line(195, 135, 380, 185, color=MUTED, sw=1.5, dash="4,3"))
    f.append(line(355, 280, 380, 185, color=NEG, sw=2))

    f.append(line(460, 185, 485, 135, color=MUTED, sw=1.5, dash="4,3"))
    f.append(line(460, 185, 505, 280, color=NEG, sw=2))

    # Пояснювальний блок
    b, _, _ = textbox(W / 2, 402,
                      "Лінія CC працює у двох режимах: у статиці резистори Rp/Rd визначають підключення та струм 5 В;\nпід час передачі пакетів PD трансивер з низьким вихідним опором модулює BMC-сигнал розмахом 1.1 В.",
                      size=11, fill="#f8fafc", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "cc-line-mux.svg"), W, H, *f)


# ── 3. Анатомія пакета USB PD: Преамбула, SOP, Дані, CRC, EOP ────────────────
def fig_pd_frame_structure():
    W, H = 860, 430
    f = [text(W / 2, 26, "Структура пакета USB Power Delivery на фізичному рівні CC", size=16, bold=True)]

    # Головна лінійка пакета
    y = 70
    h = 85

    # Блоки пакета (x, w, назва, підпис, колір заливки, колір рамки)
    blocks = [
        (35, 150, "Преамбула (Preamble)", "64 біти (0101...01)\nСинхронізація ФАПЧ", "#fef3c7", "#d97706"),
        (190, 140, "SOP Ordered Set", "4 символи 4b/5b (20 біт)\nSync-1, Sync-1, Sync-1, Sync-2", "#dbeafe", "#2563eb"),
        (335, 125, "Заголовок (Header)", "16 біт (20 біт у 4b/5b)\nТип, ID, к-сть об'єктів", "#e0e7ff", "#4f46e5"),
        (465, 155, "Дані (Data Objects)", "0 .. 7 об'єктів по 32 біти\n(PDO, RDO, запити)", "#f3e8ff", "#9333ea"),
        (625, 115, "CRC-32", "32 біти (40 біт у 4b/5b)\nКонтрольна сума", "#fee2e2", "#dc2626"),
        (745, 80, "EOP", "1 символ 4b/5b\nКінець пакета", "#f1f5f9", "#475569")
    ]

    for bx, bw, title, subtitle, fill_c, stroke_c in blocks:
        f.append(rect(bx, y, bw, h, fill=fill_c, stroke=stroke_c, sw=2, rx=6))
        f.append(text(bx + bw / 2, y + 26, title, size=11, color=INK, bold=True))
        lines = subtitle.split("\n")
        for idx, ln in enumerate(lines):
            f.append(text(bx + bw / 2, y + 48 + idx * 17, ln, size=10, color=MUTED))

    # Стрілка напрямку передачі
    f.append(arrow(35, 180, 825, 180, color=LINE, sw=2))
    f.append(text(W / 2, 200, "Послідовність передачі бітів у лінію CC (MSB/LSB правила) →", size=11, color=MUTED))

    # Блок деталізації кодування 4b/5b
    f.append(rect(35, 220, 790, 125, fill="#f8fafc", stroke=LINE, rx=6))
    f.append(text(W / 2, 244, "Конвеєр перетворення даних перед виходом у провід", size=13, bold=True))

    # Етапи: Байти -> 4b/5b кодування -> BMC модуляція -> Лінія CC
    stages = [
        (50, 175, "1. Дані (Payload)", "Заголовок, PDO, CRC-32\n(розбиття по 4 біти)"),
        (245, 175, "2. Таблиця 4b/5b", "Перетворення у 5 біт\n(K-коди SOP, без '000')"),
        (440, 175, "3. BMC модулятор", "Генерація фронтів\n(300 кбіт/с, 3.33 мкс)"),
        (635, 170, "4. Лінія CC", "Аналоговий сигнал\n(0 .. 1.12 В, кабель)")
    ]
    for sx, sw, stitle, sdesc in stages:
        f.append(rect(sx, 260, sw, 70, fill="#fff", stroke=MUTED, rx=4))
        f.append(text(sx + sw / 2, 282, stitle, size=11, bold=True))
        lines = sdesc.split("\n")
        for idx, ln in enumerate(lines):
            f.append(text(sx + sw / 2, 301 + idx * 15, ln, size=10, color=MUTED))

    # Стрілки між етапами
    f.append(arrow(226, 295, 244, 295, color=LINE, sw=1.5))
    f.append(arrow(421, 295, 439, 295, color=LINE, sw=1.5))
    f.append(arrow(616, 295, 634, 295, color=LINE, sw=1.5))

    # Пояснювальний блок
    b, _, _ = textbox(W / 2, 390,
                      "Преамбула стабілізує поріг компаратора приймача. Стартова послідовність SOP визначає тип адресата\n(пристрій чи e-marker кабелю). Корисні байти кодуються 4b/5b для контролю фронтів і захищаються CRC-32.",
                      size=11, fill="#f0fdf4", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "pd-frame-structure.svg"), W, H, *f)


# ── 4. Часові вікна дискримінації та стробування BMC ─────────────────────────
def fig_bmc_timing_windows():
    W, H = 840, 430
    f = [text(W / 2, 26, "Часові вікна декодування BMC: розрізнення півбіта (t_half) та повного біта (t_full)", size=16, bold=True)]

    # Вісь часу розміщена нижче блоків
    ox = 80
    oy = 250
    axis_len = 680
    f.append(line(ox, oy, ox + axis_len, oy, color=LINE, sw=2))
    f.append(arrow(ox + axis_len - 10, oy, ox + axis_len, oy, color=LINE, sw=2))
    f.append(text(ox + axis_len + 10, oy + 4, "t (мкс)", size=12, bold=True, anchor="start"))

    # Маркер початку: t = 0 (опорний фронт)
    f.append(line(ox, 70, ox, oy + 25, color=POS, sw=2.5))
    f.append(text(ox, 58, "t = 0 (Опорний фронт)", size=12, color=POS, bold=True))

    # Часовий масштаб: 1 бітовий інтервал tBit = 3.33 мкс
    scale = 120.0  # px per microsecond
    x_half = ox + 1.667 * scale
    x_full = ox + 3.333 * scale

    # Зони на осі (y від 80 до 230):
    box_top = 80
    box_h = 150

    # 1. Шумова зона (< 0.25 tBit = 0.83 мкс)
    x_noise = ox + 0.833 * scale
    f.append(rect(ox, box_top, x_noise - ox, box_h, fill="#fee2e2", stroke="none"))
    f.append(text((ox + x_noise) / 2, box_top + 30, "Шум / брязкіт", size=11, color=POS, bold=True))
    f.append(text((ox + x_noise) / 2, box_top + 60, "< 0.83 мкс", size=10, color=POS))
    f.append(text((ox + x_noise) / 2, box_top + 85, "(ігнорується)", size=10, color=POS))

    # 2. Вікно півбіта (t_half: 0.25 .. 0.75 tBit -> 0.83 .. 2.50 мкс)
    x_half_max = ox + 2.500 * scale
    f.append(rect(x_noise, box_top, x_half_max - x_noise, box_h, fill="#dbeafe", stroke="none"))
    f.append(line(x_half, box_top, x_half, box_top + 40, color=NEG, sw=2, dash="4,3"))
    f.append(line(x_half, box_top + 110, x_half, box_top + box_h, color=NEG, sw=2, dash="4,3"))
    f.append(text(x_half, box_top + 25, "Вікно півбіта (1.67 мкс)", size=11, color=NEG, bold=True))
    f.append(text(x_half, box_top + 65, "Детектовано '1'", size=13, color=NEG, bold=True))
    f.append(text(x_half, box_top + 85, "(очікується 2-й півбіт)", size=10, color=NEG))
    f.append(text(x_half, box_top + 130, "0.83 .. 2.50 мкс", size=10, color=NEG))

    # 3. Вікно повного біта (t_full: 0.75 .. 1.25 tBit -> 2.50 .. 4.16 мкс)
    x_full_max = ox + 4.167 * scale
    f.append(rect(x_half_max, box_top, x_full_max - x_half_max, box_h, fill="#dcfce7", stroke="none"))
    f.append(line(x_full, box_top, x_full, box_top + 40, color=FIELD, sw=2, dash="4,3"))
    f.append(line(x_full, box_top + 110, x_full, box_top + box_h, color=FIELD, sw=2, dash="4,3"))
    f.append(text(x_full, box_top + 25, "Вікно повного біта (3.33 мкс)", size=11, color=FIELD, bold=True))
    f.append(text(x_full, box_top + 65, "Детектовано '0'", size=13, color=FIELD, bold=True))
    f.append(text(x_full, box_top + 85, "(перехід закриває біт)", size=10, color=FIELD))
    f.append(text(x_full, box_top + 130, "2.50 .. 4.16 мкс", size=10, color=FIELD))

    # 4. Зона таймауту (> 1.25 tBit = 4.16 мкс)
    f.append(rect(x_full_max, box_top, (ox + axis_len) - x_full_max - 20, box_h, fill="#fef3c7", stroke="none"))
    f.append(text((x_full_max + ox + axis_len - 20) / 2, box_top + 30, "Таймаут / Тиша", size=11, color="#d97706", bold=True))
    f.append(text((x_full_max + ox + axis_len - 20) / 2, box_top + 60, "> 4.16 мкс", size=10, color="#d97706"))
    f.append(text((x_full_max + ox + axis_len - 20) / 2, box_top + 85, "(кінець пакета)", size=10, color="#d97706"))

    # Позначки на осі часу
    ticks = [
        (ox, "0"),
        (x_noise, "0.83"),
        (x_half, "1.67"),
        (x_half_max, "2.50"),
        (x_full, "3.33"),
        (x_full_max, "4.16")
    ]
    for tx, lbl in ticks:
        f.append(line(tx, oy - 6, tx, oy + 6, color=LINE, sw=1.5))
        f.append(text(tx, oy + 22, lbl, size=11, color=INK))

    # Пояснювальний блок
    b, _, _ = textbox(W / 2, 385,
                      "Декодер вимірює інтервал між сусідніми фронтами за допомогою таймера. Інтервал біля 1.67 мкс відповідає\nполовині біта (символ '1'), а інтервал біля 3.33 мкс — цілому біту (символ '0'). Широкі вікна допускають джиттер до ±25%.",
                      size=11, fill="#f8fafc", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "bmc-timing-windows.svg"), W, H, *f)


def main():
    fig_bmc_waveform()
    fig_cc_line_mux()
    fig_pd_frame_structure()
    fig_bmc_timing_windows()
    print("Всі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
