# -*- coding: utf-8 -*-
"""Фігури до теми «NMEA 0183: речення супутникового приймача».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і примітиви — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальна кольорова палітра
PREFIX_COL = POS       # '$' або '!' (червоний/рубін)
TALKER_COL = "#8e44ad" # 'GN', 'GP', 'GL' (фіолетовий)
FMT_COL    = NEG       # 'GGA', 'RMC' (синій)
DATA_COL   = INK       # поля даних
CS_COL     = FIELD     # '*' і XOR-сума (зелений)
TERM_COL   = "#d35400" # '<CR><LF>' (помаранчевий)
GREY_COL   = MUTED
BOX_BG     = "#fdfefe"


# ── 1. Анатомія речення NMEA 0183 (sentence-structure.svg) ───────────────────
def fig_sentence_structure():
    W, H = 820, 360
    f = [text(W / 2, 24, "Структура речення NMEA 0183 (на прикладі $GNGGA)", size=15, bold=True)]

    # Комірки речення
    cells = [
        ("$", 28, PREFIX_COL, "#fdeeed", "Старт"),
        ("GN", 36, TALKER_COL, "#f4ecf7", "Talker"),
        ("GGA", 48, FMT_COL, "#eaf0fd", "Формат"),
        (",", 18, GREY_COL, FILL, ""),
        ("123519.00", 82, DATA_COL, BOX_BG, "Час UTC"),
        (",", 18, GREY_COL, FILL, ""),
        ("4807.038,N", 92, DATA_COL, BOX_BG, "Широта"),
        (",", 18, GREY_COL, FILL, ""),
        ("01131.000,E", 96, DATA_COL, BOX_BG, "Довгота"),
        (",", 18, GREY_COL, FILL, ""),
        ("1,08,0.9,...", 96, DATA_COL, BOX_BG, "Якість, Sat..."),
        ("*", 24, CS_COL, "#e8f8f5", "Розділ"),
        ("47", 34, CS_COL, "#e8f8f5", "XOR CS"),
        ("<CR><LF>", 74, TERM_COL, "#fef5e7", "Кінець"),
    ]

    x0 = 34
    y0 = 85
    h_cell = 42

    cur_x = x0
    for val, w_cell, stroke_c, fill_c, top_lbl in cells:
        f.append(rect(cur_x, y0, w_cell, h_cell, fill=fill_c, stroke=stroke_c, sw=1.6, rx=4))
        if top_lbl:
            f.append(text(cur_x + w_cell / 2, y0 - 8, top_lbl, size=10, color=stroke_c, bold=True))
        f.append(text(cur_x + w_cell / 2, y0 + h_cell / 2 + 5, val, size=11.5, color=stroke_c if top_lbl else GREY_COL, bold=True))
        cur_x += w_cell + 3

    total_w = cur_x - x0

    xor_start = x0 + 31
    xor_end = x0 + 28 + 3 + 36 + 3 + 48 + 3 + 18 + 3 + 82 + 3 + 18 + 3 + 92 + 3 + 18 + 3 + 96 + 3 + 18 + 3 + 96
    y_bracket = y0 + h_cell + 14

    f.append(line(xor_start, y_bracket, xor_end, y_bracket, color=FIELD, sw=2))
    f.append(line(xor_start, y_bracket - 5, xor_start, y_bracket + 5, color=FIELD, sw=2))
    f.append(line(xor_end, y_bracket - 5, xor_end, y_bracket + 5, color=FIELD, sw=2))
    f.append(text((xor_start + xor_end) / 2, y_bracket + 18,
                  "Діапазон 8-бітної суми XOR: побайтове виключне АБО всіх символів між '$' та '*'",
                  size=11, color=FIELD, bold=True))

    cs_center_x = x0 + total_w - 74 - 3 - 34 / 2
    f.append(arrow((xor_start + xor_end) / 2 + 180, y_bracket + 28, cs_center_x, y0 + h_cell + 6, color=FIELD, sw=1.6))

    f.append(fitbox(34, 185, 235, 140,
                    "Ідентифікатор джерела (Talker ID):\n"
                    "• GP — GPS (США)\n"
                    "• GL — ГЛОНАСС\n"
                    "• GA — Galileo (ЄС)\n"
                    "• GB / BD — BeiDou (КНР)\n"
                    "• GN — Комбінований GNSS",
                    size=10.5, color=INK, fill=FILL, stroke=TALKER_COL, sw=1.2))

    f.append(fitbox(285, 185, 245, 140,
                    "Формат речення (Formatter):\n"
                    "• GGA — координати, фікс, висота\n"
                    "• RMC — рекомендований мінімум\n"
                    "• GSA — активні супутники, DOP\n"
                    "• GSV — видимі супутники, SNR\n"
                    "• VTG — швидкість і курс",
                    size=10.5, color=INK, fill=FILL, stroke=FMT_COL, sw=1.2))

    f.append(fitbox(545, 185, 241, 140,
                    "Обмеження стандарту NMEA:\n"
                    "• Макс. довжина: 82 символи\n"
                    "• Порожні поля: дві коми ,, поспіль\n"
                    "• Кодування: 7-бітний ASCII (8-N-1)\n"
                    "• Контрольна сума: 2 hex-цифри\n"
                    "• Термінатор: 0x0D 0x0A (CR LF)",
                    size=10.5, color=INK, fill=FILL, stroke=GREY_COL, sw=1.2))

    render(os.path.join(IMG, "sentence-structure.svg"), W, H, *f)


# ── 2. Кінцевий автомат потокового парсера (fsm-parser.svg) ───────────────────
def fig_fsm_parser():
    W, H = 840, 390
    f = [text(W / 2, 24, "Кінцевий автомат (FSM) потокового парсера NMEA 0183", size=15, bold=True)]

    states = [
        (90, 110, "WAIT_START", "Очікування\n'$' або '!'", PREFIX_COL, "#fdeeed"),
        (280, 110, "READ_PAYLOAD", "Накопичення тіла\nоновлення XOR", FMT_COL, "#eaf0fd"),
        (480, 110, "READ_CS1", "Зчитування\nCS digit 1", CS_COL, "#e8f8f5"),
        (680, 110, "READ_CS2", "Зчитування CS 2\nзвірка суми", CS_COL, "#e8f8f5"),
        (680, 270, "WAIT_CR", "Очікування\n0x0D (CR)", TERM_COL, "#fef5e7"),
        (480, 270, "WAIT_LF", "Очікування\n0x0A (LF)", TERM_COL, "#fef5e7"),
        (240, 270, "SENTENCE_READY", "Пакет готовий\nвиклик обробника", FIELD, "#eafaf1"),
    ]

    for cx, cy, name, sub, stroke_c, fill_c in states:
        f.append(rect(cx - 70, cy - 32, 140, 64, fill=fill_c, stroke=stroke_c, sw=1.6, rx=6))
        f.append(text(cx, cy - 10, name, size=11, color=stroke_c, bold=True))
        lines = sub.split("\n")
        f.append(text(cx, cy + 8, lines[0], size=9.5, color=INK))
        if len(lines) > 1:
            f.append(text(cx, cy + 21, lines[1], size=9.5, color=INK))

    # Переходи між станами
    f.append(arrow(160, 110, 210, 110, color=INK, sw=1.6))
    f.append(text(185, 96, "байт == '$'", size=10, color=INK, bold=True))

    f.append(line(280, 78, 280, 56, color=MUTED, sw=1.4))
    f.append(line(280, 56, 320, 56, color=MUTED, sw=1.4))
    f.append(arrow(320, 56, 320, 78, color=MUTED, sw=1.4))
    f.append(text(300, 48, "байт ≠ '*' / xor ^= b", size=9.5, color=MUTED))

    f.append(arrow(350, 110, 410, 110, color=INK, sw=1.6))
    f.append(text(380, 96, "байт == '*'", size=10, color=INK, bold=True))

    f.append(arrow(550, 110, 610, 110, color=INK, sw=1.6))
    f.append(text(580, 96, "hex-цифра 1", size=10, color=INK, bold=True))

    f.append(arrow(680, 142, 680, 238, color=FIELD, sw=1.8))
    f.append(text(745, 190, "XOR збігся", size=10.5, color=FIELD, bold=True))

    f.append(arrow(610, 270, 550, 270, color=INK, sw=1.6))
    f.append(text(580, 256, "байт == '\\r'", size=10, color=INK, bold=True))

    f.append(arrow(410, 270, 310, 270, color=FIELD, sw=1.8))
    f.append(text(360, 256, "байт == '\\n'", size=10, color=FIELD, bold=True))

    f.append(arrow(170, 270, 90, 142, color=INK, sw=1.4))
    f.append(text(105, 230, "скидання FSM", size=9.5, color=MUTED))

    f.append(line(680, 142, 680, 165, color=POS, sw=1.4, dash="4,3"))
    f.append(line(680, 165, 90, 165, color=POS, sw=1.4, dash="4,3"))
    f.append(arrow(90, 165, 90, 142, color=POS, sw=1.4))
    f.append(text(390, 177, "Помилка суми XOR або переповнення буфера (>82 B) → скидання", size=10, color=POS, bold=True))

    f.append(fitbox(30, 345, 780, 34,
                    "Потоковий парсер не потребує динамічної пам'яті (0 alloc): байти обробляються безпосередньо в ISR або циклі опитування UART.",
                    size=10.5, color=INK, fill=FILL, stroke=GREY_COL, sw=1.2))

    render(os.path.join(IMG, "fsm-parser.svg"), W, H, *f)


# ── 3. Геоїд, еліпсоїд та висота GGA (geoid-separation.svg) ───────────────────
def fig_geoid_separation():
    W, H = 800, 380
    f = [text(W / 2, 24, "Співвідношення висот у реченні $GNGGA: еліпсоїд WGS-84 і геоїд", size=15, bold=True)]

    y_ellip = 300
    y_geoid = 240
    y_ground = 110

    f.append(line(60, y_ellip, 740, y_ellip, color=NEG, sw=2.2))
    f.append(text(745, y_ellip + 4, "Еліпсоїд WGS-84", size=11, color=NEG, anchor="start", bold=True))

    f.append(line(60, y_geoid, 740, y_geoid, color=FIELD, sw=2, dash="6,3"))
    f.append(text(745, y_geoid + 4, "Геоїд (рівень моря MSL)", size=11, color=FIELD, anchor="start", bold=True))

    f.append(line(60, 200, 250, y_ground, color=INK, sw=2.5))
    f.append(line(250, y_ground, 500, 160, color=INK, sw=2.5))
    f.append(line(500, 160, 740, 220, color=INK, sw=2.5))
    f.append(text(745, 220 + 4, "Поверхня Землі", size=11, color=INK, anchor="start", bold=True))

    rx_x, rx_y = 250, y_ground
    f.append(circle(rx_x, rx_y, 6, fill=POS, stroke=POS, sw=2))
    f.append(text(rx_x, rx_y - 12, "GNSS-антена (приймач)", size=11, color=POS, bold=True))

    x_h = 160
    f.append(arrow(x_h, y_ellip, x_h, rx_y + 12, color=NEG, sw=1.8))
    f.append(arrow(x_h, rx_y + 12, x_h, y_ellip, color=NEG, sw=1.8))
    f.append(textbox(x_h - 60, (y_ellip + rx_y) / 2, "h: висота над\nеліпсоїдом\nh = H + N", size=10, fill="#eaf0fd", stroke=NEG)[0])

    x_H = 340
    f.append(arrow(x_H, y_geoid, x_H, rx_y + 6, color=FIELD, sw=1.8))
    f.append(arrow(x_H, rx_y + 6, x_H, y_geoid, color=FIELD, sw=1.8))
    f.append(textbox(x_H + 75, (y_geoid + rx_y) / 2, "H: висота над геоїдом (MSL)\n(поле 9 GGA: 545.4, M)", size=10, fill="#e8f8f5", stroke=FIELD)[0])

    x_N = 540
    f.append(arrow(x_N, y_ellip, x_N, y_geoid, color=TALKER_COL, sw=1.8))
    f.append(arrow(x_N, y_geoid, x_N, y_ellip, color=TALKER_COL, sw=1.8))
    f.append(textbox(x_N + 80, (y_ellip + y_geoid) / 2, "N: перевищення геоїда над еліпсоїдом\n(поле 11 GGA: 46.9, M)", size=10, fill="#f4ecf7", stroke=TALKER_COL)[0])

    f.append(fitbox(60, 335, 680, 34,
                    "Зв'язок висот: h (еліпсоїд) = H (ортометрична над MSL) + N (геоїдальне перевищення)",
                    size=11, color=INK, fill=FILL, stroke=GREY_COL, bold=True))

    render(os.path.join(IMG, "geoid-separation.svg"), W, H, *f)


# ── 4. Геометрія сузір'я та фактор точності DOP (dop-geometry.svg) ───────────
def fig_dop_geometry():
    W, H = 820, 370
    f = [text(W / 2, 24, "Геометричний фактор зниження точності (DOP) у реченні $GNGSA", size=15, bold=True)]

    f.append(rect(40, 55, 350, 260, fill="#fdfefe", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(215, 80, "Оптимальне розташування (Низький HDOP < 1.5)", size=12, color=FIELD, bold=True))

    f.append(circle(90, 120, 12, fill="#e8f8f5", stroke=FIELD, sw=1.5))
    f.append(text(90, 124, "Sat 1", size=9, color=FIELD, bold=True))

    f.append(circle(340, 120, 12, fill="#e8f8f5", stroke=FIELD, sw=1.5))
    f.append(text(340, 124, "Sat 2", size=9, color=FIELD, bold=True))

    f.append(circle(215, 105, 12, fill="#e8f8f5", stroke=FIELD, sw=1.5))
    f.append(text(215, 109, "Sat 3", size=9, color=FIELD, bold=True))

    f.append(circle(215, 240, 7, fill=POS, stroke=POS, sw=2))
    f.append(text(215, 258, "Приймач", size=10, color=POS, bold=True))

    f.append(line(90, 120, 215, 240, color=FIELD, sw=1.4, dash="4,3"))
    f.append(line(340, 120, 215, 240, color=FIELD, sw=1.4, dash="4,3"))
    f.append(line(215, 105, 215, 240, color=FIELD, sw=1.4, dash="4,3"))

    f.append(rect(205, 233, 20, 14, fill="#fadbd8", stroke=POS, sw=1.5, rx=7))
    f.append(text(215, 285, "Кути перетину близькі до 90°\nКомпактна зона похибки (висока точність)", size=10, color=INK))

    f.append(rect(430, 55, 350, 260, fill="#fdfefe", stroke=POS, sw=1.6, rx=6))
    f.append(text(605, 80, "Скупчене розташування (Високий HDOP > 5.0)", size=12, color=POS, bold=True))

    f.append(circle(560, 110, 12, fill="#fdeeed", stroke=POS, sw=1.5))
    f.append(text(560, 114, "Sat 1", size=9, color=POS, bold=True))

    f.append(circle(605, 100, 12, fill="#fdeeed", stroke=POS, sw=1.5))
    f.append(text(605, 104, "Sat 2", size=9, color=POS, bold=True))

    f.append(circle(650, 110, 12, fill="#fdeeed", stroke=POS, sw=1.5))
    f.append(text(650, 114, "Sat 3", size=9, color=POS, bold=True))

    f.append(circle(605, 240, 7, fill=POS, stroke=POS, sw=2))
    f.append(text(605, 258, "Приймач", size=10, color=POS, bold=True))

    f.append(line(560, 110, 605, 240, color=POS, sw=1.4, dash="4,3"))
    f.append(line(605, 100, 605, 240, color=POS, sw=1.4, dash="4,3"))
    f.append(line(650, 110, 605, 240, color=POS, sw=1.4, dash="4,3"))

    f.append(rect(570, 235, 70, 10, fill="#fadbd8", stroke=POS, sw=1.5, rx=5))
    f.append(text(605, 285, "Гострі кути між променями\nВитягнутий еліпс похибки (низька точність)", size=10, color=INK))

    f.append(fitbox(40, 325, 740, 34,
                    "Речення GSA транслює метрики: PDOP² = HDOP² + VDOP². Менше значення — надійніший фікс.",
                    size=10.5, color=INK, fill=FILL, stroke=GREY_COL, bold=True))

    render(os.path.join(IMG, "dop-geometry.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sentence_structure()
    fig_fsm_parser()
    fig_geoid_separation()
    fig_dop_geometry()
    print("All figures generated successfully.")
