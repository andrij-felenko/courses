# -*- coding: utf-8 -*-
"""
Фігури для вставки ch21-s8-a-binary-logging (⚙️ Бінарне логування).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Рис. 4.2.8a.3 — два конвеєри логування (текстовий vs бінарний).
Рис. 4.2.8a.4 — анатомія одного бінарного кадру побайтно.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.2.8a.3 — два конвеєри логування ────────────────────────────────────
def fig_binary_logging():
    """
    Два горизонтальні конвеєри поряд (ВГОРІ — текстовий, ВНИЗУ — бінарний).
    Кожен конвеєр: блок «Чіп» (Flash/CPU) → стрілка «UART» → блок «ПК».
    Акцент: де відбувається форматування (на чипі vs на ПК) і скільки байтів.
    """
    W, H = 920, 440

    CHIP_FILL  = "#e8f4fd"   # блакитний — чіп
    CHIP_STR   = NEG          # синій контур
    PC_FILL    = "#eef6ef"   # зелений — ПК/хост
    PC_STR     = FIELD        # зелений контур
    FMT_FILL   = "#fdecea"   # червоний — де форматування
    FMT_STR    = POS          # червоний
    WIRE_INK   = "#6b7280"   # MUTED — UART-лінія
    ARROW_CLR  = INK

    elems = []

    # ── Заголовок ──────────────────────────────────────────────────────────────
    elems.append(text(W / 2, 30, "Текстовий друк vs бінарне логування", size=17,
                      color=INK, anchor="middle", bold=True))
    elems.append(text(W / 2, 50, "де відбувається форматування і скільки байтів іде в дріт",
                      size=12, color=MUTED, anchor="middle"))

    # ── Геометрія двох рядів ──────────────────────────────────────────────────
    row_top   = 95    # y-центр верхнього рядка (текстовий)
    row_bot   = 285   # y-центр нижнього рядка (бінарний)
    row_h     = 130   # висота «смуги» рядка

    # Мітки рядків ліворуч
    label_x = 18
    elems.append(text(label_x, row_top - 10, "Текстовий", size=12, color=POS, anchor="start", bold=True))
    elems.append(text(label_x, row_top + 6,  "друк", size=12, color=POS, anchor="start", bold=True))
    elems.append(text(label_x, row_bot - 10, "Бінарний", size=12, color=NEG, anchor="start", bold=True))
    elems.append(text(label_x, row_bot + 6,  "лог", size=12, color=NEG, anchor="start", bold=True))

    # Розділова горизонтальна лінія між рядками
    sep_y = (row_top + row_bot) / 2
    elems.append(line(100, sep_y, W - 20, sep_y, color="#cccccc", sw=1.0, dash="4 4"))

    # ── Координати блоків ──────────────────────────────────────────────────────
    # Чіп-блок: дві комірки (Flash + CPU/printf)
    chip_x   = 105   # лівий край всього чіп-блоку
    chip_w   = 230
    chip_cy_top = row_top
    chip_cy_bot = row_bot

    # UART-провід
    wire_x1 = chip_x + chip_w + 10
    wire_x2 = 680
    wire_cx  = (wire_x1 + wire_x2) / 2

    # ПК-блок
    pc_x  = wire_x2 + 10
    pc_w  = 210
    pc_cx_top = pc_x + pc_w / 2
    pc_cx_bot = pc_x + pc_w / 2

    # ═══════════════════════════════════════════════════════════════════════════
    # ВЕРХНІЙ РЯДОК — текстовий друк
    # ═══════════════════════════════════════════════════════════════════════════
    cy = chip_cy_top
    bh = 108

    # Чіп: Flash (лівий під-блок) + printf-CPU (правий під-блок) в одній рамці
    chip_box_t, _, _ = textbox(chip_x + chip_w / 2, cy,
                               "ЧІП\nFlash: рядок-шаблон\n\"temp=%d mV…\" (25+ байтів)\n→ printf форматує int→ASCII",
                               size=12, pad=10,
                               fill=FMT_FILL, stroke=FMT_STR, sw=2.0, min_w=chip_w)
    elems.append(chip_box_t)

    # Мітка «форматування тут» над чіп-блоком
    fmt_label_y = cy - bh / 2 - 12
    elems.append(text(chip_x + chip_w / 2, fmt_label_y,
                      "⚙ форматування на чипі", size=11, color=POS,
                      anchor="middle", bold=True))

    # Стрілка UART → ПК (верхній рядок)
    elems.append(arrow(wire_x1, cy, wire_x2, cy, color=POS, sw=2.2))
    elems.append(text(wire_cx, cy - 14, "UART", size=11, color=WIRE_INK, anchor="middle", bold=True))
    elems.append(text(wire_cx, cy + 10, "~25 байтів тексту", size=12, color=POS,
                      anchor="middle", bold=True))
    elems.append(text(wire_cx, cy + 25, "(готовий рядок — повільно!)", size=10,
                      color=MUTED, anchor="middle"))

    # ПК: монітор показує як є
    pc_box_t, _, _ = textbox(pc_cx_top, cy,
                             "ПК\nМонітор:\ntemp=2350 mV\n(текст готовий)",
                             size=12, pad=10,
                             fill=PC_FILL, stroke=PC_STR, sw=2.0, min_w=pc_w - 10)
    elems.append(pc_box_t)

    # ═══════════════════════════════════════════════════════════════════════════
    # НИЖНІЙ РЯДОК — бінарний лог
    # ═══════════════════════════════════════════════════════════════════════════
    cy = chip_cy_bot

    # Чіп: Flash тримає лише ID
    chip_box_b, _, _ = textbox(chip_x + chip_w / 2, cy,
                               "ЧІП\nFlash: лише ID = 1\n(1–2 байти замість рядка)\n→ шле сирі байти арг.",
                               size=12, pad=10,
                               fill=CHIP_FILL, stroke=CHIP_STR, sw=2.0, min_w=chip_w)
    elems.append(chip_box_b)

    # Мітка «Flash дешевший»
    fmt_label_b_y = cy - bh / 2 - 12
    elems.append(text(chip_x + chip_w / 2, fmt_label_b_y,
                      "Flash зберігає лише ID", size=11, color=NEG,
                      anchor="middle", bold=True))

    # Стрілка UART → ПК (нижній рядок)
    elems.append(arrow(wire_x1, cy, wire_x2, cy, color=NEG, sw=2.2))
    elems.append(text(wire_cx, cy - 14, "UART", size=11, color=WIRE_INK, anchor="middle", bold=True))
    elems.append(text(wire_cx, cy + 10, "~6 байтів (×4 менше!)", size=12, color=NEG,
                      anchor="middle", bold=True))
    elems.append(text(wire_cx, cy + 25, "[0x7E · ID · arg0 · arg1]", size=10,
                      color=MUTED, anchor="middle"))

    # ПК: декодер + .elf збирає текст
    pc_box_b, _, _ = textbox(pc_cx_bot, cy,
                             "ПК\nДекодер + .elf:\n→ знаходить шаблон за ID\n→ temp=2350 mV",
                             size=12, pad=10,
                             fill=FMT_FILL, stroke=FMT_STR, sw=2.0, min_w=pc_w - 10)
    elems.append(pc_box_b)

    # Мітка «форматування тут» над ПК-блоком нижнього рядка
    fmt_pc_y = cy - bh / 2 - 12
    elems.append(text(pc_cx_bot, fmt_pc_y,
                      "⚙ форматування на ПК", size=11, color=POS,
                      anchor="middle", bold=True))

    # ── Підпис унизу ──────────────────────────────────────────────────────────
    elems.append(text(W / 2, H - 16,
                      "Бінарний лог: форматування переїхало з чипа на ПК — чіп шле жменю байтів, а не готовий текст",
                      size=11, color=MUTED, anchor="middle"))

    path = os.path.join(OUT, "fig-21-8ab-1-binary.svg")
    render(path, W, H, *elems)
    print("wrote fig-21-8ab-1-binary.svg")


# ── Рис. 4.2.8a.4 — анатомія одного бінарного кадру ──────────────────────────
def fig_binary_frame():
    """
    Анатомія кадру [0x7E | ID | N | arg0 | arg1 | XOR] побайтно.
    Кожен байт — окрема комірка; під кожною — роль і значення прикладу.
    """
    W, H = 820, 370

    FRAME_FILL  = "#e8f4fd"
    FRAME_STR   = NEG
    BYTE_FILL   = "#ffffff"
    MARKER_FILL = "#fdecea"
    MARKER_STR  = POS
    XOR_FILL    = "#eef6ef"
    XOR_STR     = FIELD

    elems = []

    # Заголовок
    elems.append(text(W / 2, 30, "Анатомія одного бінарного кадру", size=17,
                      color=INK, anchor="middle", bold=True))
    elems.append(text(W / 2, 50, "приклад: BLOG(LOG_TEMP, (int16_t)2350)  →  2350 = 0x092E  (little-endian)",
                      size=12, color=MUTED, anchor="middle"))

    # Байти кадру
    bytes_def = [
        ("0x7E", "маркер-початок\n(синхронізація)", MARKER_FILL, MARKER_STR),
        ("0x01", "ID шаблону\n(LOG_TEMP = 1)", FRAME_FILL, FRAME_STR),
        ("0x02", "N = довжина арг.\n(2 байти = int16_t)", FRAME_FILL, FRAME_STR),
        ("0x2E", "arg[0]\n(молодший байт\n2350 = 0x092E)", BYTE_FILL, FRAME_STR),
        ("0x09", "arg[1]\n(старший байт\nlittle-endian ESP32)", BYTE_FILL, FRAME_STR),
        ("0x7E\n⊕0x01\n⊕0x02\n⊕…", "XOR-контроль\n(помилка → ≠ 0)", XOR_FILL, XOR_STR),
    ]

    n = len(bytes_def)
    bw = 110     # ширина комірки
    bh_top = 64  # висота верхньої (значення байта) частини
    bh_bot = 80  # висота нижньої (підпис) частини
    gap = 10
    total_w = n * bw + (n - 1) * gap
    start_x = (W - total_w) / 2
    by_top = 80

    for i, (val, role, fill, stroke) in enumerate(bytes_def):
        bx = start_x + i * (bw + gap)

        # Верхня комірка — значення байта (жирне, велике)
        fbox_top = fitbox(bx, by_top, bw, bh_top, val,
                          size=15, pad=8, fill=fill, stroke=stroke, sw=2.0, bold=True)
        elems.append(fbox_top)

        # Нижня комірка — роль
        fbox_bot = fitbox(bx, by_top + bh_top + 4, bw, bh_bot, role,
                          size=11, pad=7, fill=FILL, stroke="#cccccc", sw=1.2)
        elems.append(fbox_bot)

        # Стрілочки між комірками (крім останньої)
        if i < n - 1:
            ax = bx + bw + gap / 2
            ay = by_top + bh_top / 2
            elems.append(arrow(bx + bw + 2, ay, bx + bw + gap - 2, ay,
                               color=MUTED, sw=1.5))

    # Загальна рамка навколо всіх комірок
    frame_pad = 14
    elems.append(rect(start_x - frame_pad, by_top - frame_pad,
                      total_w + 2 * frame_pad, bh_top + bh_bot + 4 + 2 * frame_pad,
                      fill="none", stroke="#aaaaaa", sw=1.2, rx=10))

    # Підпис «6 байтів загалом»
    elems.append(text(W / 2, by_top + bh_top + bh_bot + 4 + frame_pad + 18,
                      "Разом: 6 байтів замість ~25 байтів тексту. Загубив байт → XOR не зійдеться → декодер ресинхронізується на наступному 0x7E",
                      size=11, color=MUTED, anchor="middle"))

    # Нижня нотатка: сирі байти — НЕ ASCII
    note_y = H - 36
    raw_box, _, _ = textbox(W / 2, note_y,
                            "0x2E 0x09 — це СИРІ байти числа 2350, НЕ символи ASCII '2', '3', '5', '0'",
                            size=12, pad=9, fill=MARKER_FILL, stroke=MARKER_STR, sw=1.5)
    elems.append(raw_box)

    path = os.path.join(OUT, "fig-21-8ab-2-frame.svg")
    render(path, W, H, *elems)
    print("wrote fig-21-8ab-2-frame.svg")


if __name__ == "__main__":
    fig_binary_logging()
    fig_binary_frame()
