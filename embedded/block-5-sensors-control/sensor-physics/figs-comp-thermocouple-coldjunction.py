# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 5.1.3c — Термопара і компенсація холодного спаю (MAX31855-клас).
Окремий файл, щоб не забруднювати основний figs.py.
Вивід → ./img/ (та сама папка що й figs.py розділу).

Запуск:
    python E:/develop/courses/embedded/block-5-sensors-control/ch28-sensor-physics/figs-ch28-s3-c-thermocouple-coldjunction.py

Перевірка:
    python E:/develop/courses/embedded/_tools/svgcheck.py \
        E:/develop/courses/embedded/block-5-sensors-control/ch28-sensor-physics --min-font 8
"""

import sys
import os

# ── спільний kit (НЕ переписувати — імпортувати) ─────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# Додаткові кольори для теплового контексту
HOTF   = "#fff4ec"   # бліде тепле тло (гарячий спай)
COLDF  = "#ecf2fb"   # бліде холодне тло (холодний спай/кімнатна температура)
POS    = "#c0392b"   # червоний — прапори несправності, «+»
NEG    = "#2457d6"   # синій — «−», холодне
FIELD  = "#27ae60"   # зелений — основні сигнальні потоки


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 5.1.3c.1 — внутрішня блок-схема MAX31855-клас
# ─────────────────────────────────────────────────────────────────────────────
def fig_blockdiagram():
    """
    Сигнальний ланцюг: T+/T- → підсилювач → суматор(+CJC) → АЦП → лінеаризація → SPI.
    Окрема верхня гілка: давач холодного спаю (CJC sensor) → суматор.
    Нижня гілка: детектор несправностей → прапори FAULT/OC/SCV/SCG.
    """
    W, H = 820, 420

    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W // 2, 26, "MAX31855-клас: що ховає 8-вивідний корпус",
                      16, INK, "middle", bold=True))

    # ── Зовнішній контур корпусу ───────────────────────────────────────────────
    chip_x, chip_y = 155, 60
    chip_w, chip_h = 500, 290
    frags.append(rect(chip_x, chip_y, chip_w, chip_h,
                      fill="#f9fbff", stroke="#5577aa", sw=2.5, rx=12))
    frags.append(text(chip_x + chip_w // 2, chip_y + 18,
                      "MAX31855 (корпус)", 11, "#5577aa", "middle", bold=True))

    # ── Блоки основного ланцюга (зліва направо, y≈180) ───────────────────────
    main_y  = 200     # центр рядка
    blocks  = [
        (220, main_y, "Вхідний\nпідсилювач\n×200"),
        (340, main_y, "Суматор\n(+CJC)"),
        (450, main_y, "АЦП"),
        (560, main_y, "Лінеаризація\n(крива K)"),
        (675, main_y, "32-біт\nрегістр"),
    ]

    box_w_target = 90

    for cx, cy, label in blocks:
        b, bw, bh = textbox(cx, cy, label, size=11, pad=9,
                            fill=FILL, stroke=LINE, sw=1.5,
                            color=INK, min_w=box_w_target)
        frags.append(b)

    # стрілки між блоками
    # T+/T- → підсилювач (вхід зліва)
    frags.append(arrow(chip_x - 60, main_y, chip_x + 9, main_y, FIELD, 2.0))
    frags.append(text(chip_x - 62, main_y - 14, "T+", 11, POS, "end", bold=True))
    frags.append(text(chip_x - 62, main_y + 18, "T−", 11, NEG, "end", bold=True))

    # підсилювач → суматор
    frags.append(arrow(272, main_y, 290, main_y, FIELD, 2.0))
    # суматор → АЦП
    frags.append(arrow(390, main_y, 410, main_y, FIELD, 2.0))
    # АЦП → лінеаризація
    frags.append(arrow(490, main_y, 510, main_y, FIELD, 2.0))
    # лінеаризація → регістр
    frags.append(arrow(615, main_y, 630, main_y, FIELD, 2.0))

    # SPI вихід → за межі корпусу
    frags.append(arrow(chip_x + chip_w - 10, main_y,
                       chip_x + chip_w + 55, main_y, FIELD, 2.0))
    spi_x = chip_x + chip_w + 55
    b2, _, _ = textbox(spi_x + 38, main_y, "SPI\n(SO/SCK/CS)", size=11, pad=8,
                       fill="#eaf7ec", stroke=FIELD, sw=1.8, color=FIELD, min_w=80)
    frags.append(b2)

    # ── Верхня гілка: давач холодного спаю → суматор ─────────────────────────
    cjc_x, cjc_y = 340, 100
    b3, _, _ = textbox(cjc_x, cjc_y, "Давач T\nкристала\n(CJC sensor)", size=11, pad=8,
                       fill=COLDF, stroke=NEG, sw=1.8, color=NEG, min_w=100)
    frags.append(b3)
    # стрілка: давач → суматор (вертикально вниз)
    frags.append(arrow(cjc_x, cjc_y + 30, cjc_x, main_y - 24, NEG, 2.0))
    frags.append(text(cjc_x + 6, (cjc_y + 30 + main_y - 24) // 2,
                      "T_клем", 10, NEG, "start", bold=False))

    # ── Нижня гілка: детектор несправностей ──────────────────────────────────
    det_x, det_y = 340, 320
    b4, _, _ = textbox(det_x, det_y, "Детектор\nобриву/КЗ", size=11, pad=8,
                       fill="#fdecea", stroke=POS, sw=1.8, color=POS, min_w=100)
    frags.append(b4)

    # стрілка від вхідного рядка вниз
    frags.append(arrow(270, main_y + 24, 270, det_y - 20, POS, 1.8))
    frags.append(arrow(270, det_y - 20, det_x - 52, det_y, POS, 1.8))

    # прапори FAULT виходять праворуч
    frags.append(arrow(det_x + 55, det_y, det_x + 55 + 30, det_y, POS, 1.8))
    b5, _, _ = textbox(det_x + 115, det_y, "FAULT\nOC / SCV / SCG", size=10, pad=7,
                       fill="#fdecea", stroke=POS, sw=1.5, color=POS, min_w=110)
    frags.append(b5)

    # ── Підписи вхідних виводів (зліва, поза корпусом) ───────────────────────
    pin_x = chip_x - 60
    frags.append(text(pin_x - 5, main_y - 26, "Термопара", 10, INK, "end"))

    # ── Примітка про холодний спай ────────────────────────────────────────────
    note_y = H - 24
    frags.append(text(W // 2, note_y,
                      "Давач CJC фізично поруч із клемами T+/T− — вимірює температуру саме там, де треба",
                      10, MUTED, "middle", italic=True))

    render(os.path.join(OUT, "fig-28-3c-1-blockdiagram.svg"), W, H, *frags,
           title=None)
    print("  saved fig-28-3c-1-blockdiagram.svg")


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 5.1.3c.2 — бітова карта 32-бітного SPI-слова MAX31855
# ─────────────────────────────────────────────────────────────────────────────
def fig_frame32():
    """
    Горизонтальна бітова карта 32-бітного слова.
    Групи: D31|D[30:18]|D17|D16|D[15:4]|D3|D2|D1|D0
    Прапори (D16, D2, D1, D0) виділені червоним.
    Температурні поля — нейтрально.
    """
    W, H = 860, 340

    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W // 2, 26, "32-бітне SPI-слово MAX31855: три відповіді в одному кадрі",
                      15, INK, "middle", bold=True))

    # ── Визначення груп (зліва → D31..D0) ───────────────────────────────────
    # Кожна група: (мітка рядку, підпис угорі, ширина_відносна, колір_заливки, колір_рамки)
    # Ширини задаємо у відносних одиницях, потім масштабуємо
    groups = [
        ("D31",      "знак TC",              1,  "#fdecea", POS),
        ("D30..D18", "температура TC\n0.25 °C / LSB",  13, "#eaf4fb", NEG),
        ("D17",      "резерв\n(0)",          1,  "#f4f4f4", MUTED),
        ("D16",      "FAULT",                1,  "#fdecea", POS),
        ("D15",      "знак CJC",             1,  "#fdecea", POS),
        ("D14..D4",  "температура CJC\n0.0625 °C / LSB", 11, "#f0f7ec", FIELD),
        ("D3",       "резерв\n(0)",          1,  "#f4f4f4", MUTED),
        ("D2",       "SCV\n(КЗ VCC)",        1,  "#fdecea", POS),
        ("D1",       "SCG\n(КЗ GND)",        1,  "#fdecea", POS),
        ("D0",       "OC\n(обрив)",          1,  "#fdecea", POS),
    ]

    total_units = sum(g[2] for g in groups)
    bar_x0 = 30
    bar_x1 = W - 30
    bar_w   = bar_x1 - bar_x0
    bar_y   = 100
    bar_h   = 60

    # Малюємо прямокутники-поля
    x_cur = bar_x0
    for label, caption, units, fill_c, stroke_c in groups:
        gw = bar_w * units / total_units
        # рамка поля
        frags.append(rect(x_cur, bar_y, gw, bar_h,
                          fill=fill_c, stroke=stroke_c, sw=1.8, rx=3))
        # мітка поля (знизу рамки, посередині)
        cx = x_cur + gw / 2
        frags.append(text(cx, bar_y + bar_h // 2 + 5,
                          label, 9 if len(label) > 4 else 10,
                          stroke_c, "middle", bold=True))
        x_cur += gw

    # ── Підписи груп (над рамками зі стрілками) ──────────────────────────────
    # Нам треба підписи з рамками над кожною групою
    # Прохід другий для підписів
    x_cur = bar_x0
    label_y_top  = 58   # верх рамки підпису
    label_h      = 34

    for label, caption, units, fill_c, stroke_c in groups:
        gw = bar_w * units / total_units
        cx = x_cur + gw / 2

        # Підпис-рамка над полем (лише якщо поле достатньо широке або підпис короткий)
        lines = caption.split("\n")
        max_line_len = max(len(l) for l in lines)
        fs = 9 if max_line_len > 12 or gw < 80 else 10
        # Якщо поле занадто вузьке — стрілка + підпис збоку (для D31, D17, D16, D15, D3, D2, D1, D0)
        if gw < 55:
            # підпис під рамкою зі стрілкою вниз
            label_down_y = bar_y + bar_h + 14
            frags.append(text(cx, label_down_y, caption, 8, stroke_c, "middle"))
        else:
            # підпис у рамці над полем
            b, bw, bh = textbox(cx, label_y_top, caption, size=fs, pad=5,
                                fill=fill_c, stroke=stroke_c, sw=1.2,
                                color=stroke_c if stroke_c != MUTED else INK,
                                min_w=max(gw - 6, 40))
            frags.append(b)
            # сполучна лінія від рамки підпису до поля
            frags.append(line(cx, label_y_top + label_h // 2 + 4,
                              cx, bar_y, stroke_c, 1.2, dash="3,3"))

        x_cur += gw

    # ── Підписи груп під картою (пояснення призначення) ──────────────────────
    explain_y = bar_y + bar_h + 50

    # Три великі групи-пояснення знизу
    # 1) температура TC
    tc_cx = bar_x0 + bar_w * (1 + 13 / 2) / total_units
    b6, _, _ = textbox(tc_cx, explain_y,
                       "Температура об'єкта\n(signed 14-bit, 0.25 °C/LSB)",
                       size=11, pad=8, fill="#eaf4fb", stroke=NEG, sw=1.5,
                       color=NEG, min_w=200)
    frags.append(b6)

    # 2) температура CJC
    cjc_start = 1 + 13 + 1 + 1 + 1
    cjc_cx = bar_x0 + bar_w * (cjc_start + 11 / 2) / total_units
    b7, _, _ = textbox(cjc_cx, explain_y,
                       "Температура клем-CJC\n(signed 12-bit, 0.0625 °C/LSB)",
                       size=11, pad=8, fill="#f0f7ec", stroke=FIELD, sw=1.5,
                       color=FIELD, min_w=210)
    frags.append(b7)

    # 3) прапори (D16 + D2/D1/D0)
    flags_cx = bar_x0 + bar_w * (1 + 13 + 1 + 0.5) / total_units
    b8, _, _ = textbox(flags_cx, explain_y + 50,
                       "FAULT (D16) = OR(D2,D1,D0)",
                       size=10, pad=7, fill="#fdecea", stroke=POS, sw=1.5,
                       color=POS, min_w=190)
    frags.append(b8)

    # Стрілки від груп до пояснень — прості лінії
    frags.append(line(tc_cx, bar_y + bar_h + 2, tc_cx, explain_y - 22, NEG, 1.2, dash="3,3"))
    frags.append(line(cjc_cx, bar_y + bar_h + 2, cjc_cx, explain_y - 22, FIELD, 1.2, dash="3,3"))
    frags.append(line(flags_cx, bar_y + bar_h + 2, flags_cx, explain_y + 28, POS, 1.2, dash="3,3"))

    # ── Примітка ──────────────────────────────────────────────────────────────
    frags.append(text(W // 2, H - 18,
                      "Правило: спочатку перевіряємо D16 (і D2/D1/D0), лише тоді декодуємо градуси",
                      10, POS, "middle", bold=True))

    render(os.path.join(OUT, "fig-28-3c-2-frame32.svg"), W, H, *frags,
           title=None)
    print("  saved fig-28-3c-2-frame32.svg")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_blockdiagram()
    fig_frame32()
    print("Усі фігури згенеровано.")
