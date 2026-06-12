# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки «📜 AVR: два студенти з Тронгейма».
Тема 4.11.2, файл r11-s2-history-avr.md.
Нумерація фігур: Рис. 4.11.2i.k.
SVG-файли → ./img/fig-r11-s2i-1-*.svg, fig-r11-s2i-2-*.svg

Запуск: python figs-r11-s2-history-avr.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Рис. 4.11.2i.1 — Таймлайн-ланцюг: від студентського задуму до Arduino ───
def fig1_timeline():
    """Чотири щаблі: NTH → Nordic VLSI → Atmel → Arduino.
    Наскрізна нитка «1 такт = 1 інструкція» проходить крізь усі щаблі."""
    W, H = 860, 420

    stages = [
        ("~1994–1996", "NTH, Тронгейм",
         "Боген + Воллан\nСтудентський задум:\n«8-біт ядро під C\nта 1 такт = 1 інструкція»",
         FILL, LINE),
        ("~1996–1997", "Nordic VLSI",
         "µRISC — перший\nробочий кремній.\nЗадум стає\nреальним чипом.",
         "#e8f4f8", NEG),
        ("кін. 1990-х", "Atmel Norway",
         "AVR + Flash.\nАТ90S-серія:\nISP-прошивка\nбез програматора.",
         "#eef6ee", FIELD),
        ("2005+", "Arduino\n(ATmega168/328)",
         "Масове поширення.\nЦіле покоління\nперших прошивок\nна AVR.",
         "#fff8e6", POS),
    ]

    parts = []

    # Заголовок
    parts.append(text(W / 2, 32, "Від студентського задуму в Тронгеймі до серця Arduino",
                      18, INK, "middle", bold=True))
    parts.append(text(W / 2, 54, "кожен щабель наближає ідею «такт-у-такт, дружній до C» до масового чипа",
                      12, MUTED, "middle"))

    # Обчислення позицій блоків
    margin = 48
    gap = 28
    n = len(stages)
    total_w = W - 2 * margin
    box_w = (total_w - gap * (n - 1)) / n
    box_h = 140
    top_y = 80

    for i, (yr, title, desc, fill, stroke) in enumerate(stages):
        cx = margin + i * (box_w + gap) + box_w / 2
        cy = top_y + box_h / 2

        # Рамка щабля через fitbox
        parts.append(fitbox(cx - box_w / 2, top_y, box_w, box_h,
                            title, size=13, pad=8, fill=fill, stroke=stroke, sw=2, rx=8,
                            bold=True, color=INK))

        # Дата над блоком
        parts.append(text(cx, top_y - 10, yr, 11, MUTED, "middle"))

        # Опис під блоком
        desc_lines = desc.split("\n")
        desc_y = top_y + box_h + 20
        for j, dl in enumerate(desc_lines):
            parts.append(text(cx, desc_y + j * 15, dl, 11, INK, "middle"))

        # Стрілка між щаблями
        if i < n - 1:
            ax1 = cx + box_w / 2
            ax2 = ax1 + gap
            ay = cy
            parts.append(arrow(ax1, ay, ax2 - 6, ay, color=LINE, sw=2))

    # Нитка-теза внизу
    thread_y = H - 34
    parts.append(line(margin, thread_y, W - margin, thread_y, color=FIELD, sw=2.5, dash="8 4"))
    tb, tw, th = textbox(W / 2, H - 16,
                         "наскрізна нитка: 1 такт = 1 інструкція, ядро під компілятор C",
                         size=12, pad=7, fill="#f0faf0", stroke=FIELD, color=FIELD, sw=1.5)
    parts.append(tb)

    render(os.path.join(OUT, "fig-r11-s2i-1-from-thesis-to-arduino.svg"),
           W, H, *parts)
    print("wrote fig-r11-s2i-1-from-thesis-to-arduino.svg")


# ── Рис. 4.11.2i.2 — «Чому олівець працює»: CISC vs AVR-конвеєр ─────────────
def fig2_one_clock():
    """Ліворуч — 8051/CISC: 12 тактів на операцію.
    Праворуч — AVR: двоступеневий конвеєр, ~1 такт; 32 регістри.
    Висновок: ≈1 MIPS/МГц → такти можна рахувати олівцем."""
    W, H = 800, 400

    parts = []

    # Заголовок
    parts.append(text(W / 2, 30, "Чому олівець працює: CISC/8051 проти AVR",
                      18, INK, "middle", bold=True))
    parts.append(text(W / 2, 50, "ті самі МГц, зовсім різна робота за такт",
                      12, MUTED, "middle"))

    mid = W / 2
    col_l = mid / 2          # центр лівої колонки
    col_r = mid + mid / 2    # центр правої колонки
    top = 70

    # ── Ліва колонка: 8051 / CISC ─────────────────────────────────────────────
    tb, _, _ = textbox(col_l, top + 18, "8051 / CISC-підхід", size=14, pad=9,
                       fill="#fdecea", stroke=POS, sw=2, bold=True, color=POS)
    parts.append(tb)

    # Такти кварцу — 12 прямокутників
    tick_y = top + 55
    tick_w = 22
    tick_h = 24
    tick_gap = 3
    n_ticks = 12
    total_tick_w = n_ticks * (tick_w + tick_gap) - tick_gap
    tick_x0 = col_l - total_tick_w / 2
    for i in range(n_ticks):
        fx = tick_x0 + i * (tick_w + tick_gap)
        color = "#ffc0b8" if i < 12 else FILL
        parts.append(fitbox(fx, tick_y, tick_w, tick_h, str(i + 1),
                            size=9, pad=2, fill=color, stroke=POS, sw=1, rx=3))
    parts.append(text(col_l, tick_y + tick_h + 14, "12 тактів кварцу",
                      11, POS, "middle", bold=True))
    parts.append(text(col_l, tick_y + tick_h + 28, "= 1 машинна операція",
                      11, POS, "middle"))

    # Регістри — мало
    reg_y = tick_y + tick_h + 50
    parts.append(text(col_l, reg_y, "Робочі регістри: 4–8 шт.", 11, MUTED, "middle"))
    parts.append(text(col_l, reg_y + 16, "Операнди часто через RAM", 11, MUTED, "middle"))

    # Підсумок
    summ_y = reg_y + 46
    tb2, _, _ = textbox(col_l, summ_y, "≈ 1 МГц → ~83 000 оп./с\n(12 МГц, ориг. 8051)",
                        size=11, pad=8, fill="#fff0f0", stroke=POS, sw=1.2, color=POS)
    parts.append(tb2)

    # ── Роздільник ─────────────────────────────────────────────────────────────
    parts.append(line(mid, top, mid, H - 20, color=MUTED, sw=1, dash="5 5"))
    tb_vs, _, _ = textbox(mid, top + 18, "vs", size=14, pad=6,
                          fill=BG, stroke=MUTED, sw=1.2, color=MUTED)
    parts.append(tb_vs)

    # ── Права колонка: AVR ─────────────────────────────────────────────────────
    tb, _, _ = textbox(col_r, top + 18, "AVR (RISC)", size=14, pad=9,
                       fill="#eaf0fd", stroke=NEG, sw=2, bold=True, color=NEG)
    parts.append(tb)

    # Конвеєр: 2 стадії
    pipe_y = top + 55
    stages = [("Вибірка\n(Fetch)", "#d0e8ff"), ("Виконання\n(Execute)", "#d0f0e8")]
    stage_w = 90
    stage_h = 46
    pipe_gap = 10
    pipe_x0 = col_r - (len(stages) * stage_w + pipe_gap) / 2
    for i, (lbl, fc) in enumerate(stages):
        fx = pipe_x0 + i * (stage_w + pipe_gap)
        parts.append(fitbox(fx, pipe_y, stage_w, stage_h, lbl,
                            size=11, pad=6, fill=fc, stroke=NEG, sw=1.5, rx=5))
        if i < len(stages) - 1:
            parts.append(arrow(fx + stage_w, pipe_y + stage_h / 2,
                               fx + stage_w + pipe_gap - 2, pipe_y + stage_h / 2,
                               color=NEG, sw=1.5))

    parts.append(text(col_r, pipe_y + stage_h + 14, "двоступеневий конвеєр",
                      11, NEG, "middle", bold=True))
    parts.append(text(col_r, pipe_y + stage_h + 28, "~1 такт = 1 інструкція (більшість команд)",
                      11, NEG, "middle"))

    # 32 регістри
    reg_y_r = pipe_y + stage_h + 50
    parts.append(text(col_r, reg_y_r, "32 регістри загального призначення", 11, NEG, "middle", bold=True))
    parts.append(text(col_r, reg_y_r + 16, "більшість операцій — регістр←→регістр", 11, MUTED, "middle"))

    # Підсумок
    summ_y_r = reg_y_r + 46
    tb3, _, _ = textbox(col_r, summ_y_r, "≈ 1 MIPS / МГц\nтакти можна рахувати олівцем",
                        size=11, pad=8, fill="#eaf4ff", stroke=NEG, sw=1.2, color=NEG)
    parts.append(tb3)

    # Висновок внизу
    concl_y = H - 26
    tb4, _, _ = textbox(W / 2, concl_y,
                        "Саме це рішення з 1990-х дозволяє в §4.11.2 рахувати затримки bit-bang і нопи «на пальцях»",
                        size=11, pad=8, fill="#f0faf0", stroke=FIELD, sw=1.5, color=FIELD)
    parts.append(tb4)

    render(os.path.join(OUT, "fig-r11-s2i-2-one-clock-one-instruction.svg"),
           W, H, *parts)
    print("wrote fig-r11-s2i-2-one-clock-one-instruction.svg")


if __name__ == "__main__":
    fig1_timeline()
    fig2_one_clock()
    print("Done.")
