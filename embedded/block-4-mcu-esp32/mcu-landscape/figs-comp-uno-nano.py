# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 4.11.2c — «Плата Uno/Nano-класу».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-11-2c-1-board-anatomy.svg  — блок-схема Uno/Nano vs ESP32 DevKit
  fig-11-2c-2-integration-ladder.svg — сходи самодостатності плат
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Блок-схема Uno/Nano vs ESP32 DevKit ──────────────────────────

def fig1_board_anatomy():
    W, H = 860, 520
    frags = []

    # ─── заголовки колонок ──────────────────────────────────────────────────
    tb, _, _ = textbox(215, 34, "Uno/Nano-клас (AVR ATmega328P)", size=14,
                       fill="#e8f4fd", stroke=NEG, bold=True, pad=10)
    frags.append(tb)
    tb2, _, _ = textbox(645, 34, "ESP32 DevKit", size=14,
                        fill="#edf7ed", stroke=FIELD, bold=True, pad=10)
    frags.append(tb2)

    # ─── роздільна лінія ────────────────────────────────────────────────────
    frags.append(line(430, 58, 430, H - 30, color=MUTED, sw=1.2, dash="6,4"))

    # ─── вузли лівої колонки (AVR-плата) ────────────────────────────────────
    avr_nodes = [
        (215, 110, "USB-UART міст\nFT232 / CH340-клас", "#e8f4fd", NEG),
        (215, 195, "Зовнішній кварц 16 МГц\n(бляшаний резонатор)", "#e8f4fd", NEG),
        (215, 280, "Лінійний стабілізатор\n(AMS1117-клас → 5 В)", "#e8f4fd", NEG),
        (215, 360, "DIP-панелька\n(чип вийнятний!)", "#e8f4fd", NEG),
        (215, 435, "Кнопка reset\n(апаратне скидання)", "#e8f4fd", NEG),
    ]

    # окремий блок «другий чип USB» тільки для Uno
    tb_uno, _, _ = textbox(215, 110, "USB-UART міст\nFT232 / CH340-клас\n(або окремий 8U2/16U2 AVR\nна класичній Uno)", size=12,
                           fill="#e8f4fd", stroke=NEG, pad=10)
    frags.append(tb_uno)
    tb_kv, _, _ = textbox(215, 200, "Зовнішній кварц 16 МГц\n(фіксована частота, без PLL)", size=12,
                          fill="#e8f4fd", stroke=NEG, pad=10)
    frags.append(tb_kv)
    tb_ldo, _, _ = textbox(215, 285, "Лінійний стабілізатор\n(5 В або 3.3 В)", size=12,
                           fill="#e8f4fd", stroke=NEG, pad=10)
    frags.append(tb_ldo)
    tb_dip, _, _ = textbox(215, 360, "DIP-панелька\n(чип вийнятний)", size=12,
                           fill="#e8f4fd", stroke=NEG, pad=10)
    frags.append(tb_dip)
    tb_rst, _, _ = textbox(215, 430, "Кнопка reset\n+ гребінки GPIO\n(рівні: переважно 5 В!)", size=12,
                           fill="#fef3e2", stroke="#e67e22", pad=10)
    frags.append(tb_rst)

    # ─── вузли правої колонки (ESP32 DevKit) ────────────────────────────────
    tb_br, _, _ = textbox(645, 110, "USB-UART міст\nCP210x / CH340-клас", size=12,
                          fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_br)
    tb_pll, _, _ = textbox(645, 200, "Кварц 40 МГц + PLL\n(до 240 МГц; всередині чипа)", size=12,
                           fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_pll)
    tb_ldo2, _, _ = textbox(645, 285, "LDO 3.3 В\n(AMS1117-клас)", size=12,
                            fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_ldo2)
    tb_mod, _, _ = textbox(645, 360, "WROOM-модуль\n(чип назавжди припаяний)", size=12,
                           fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_mod)
    tb_btn, _, _ = textbox(645, 430, "Кнопки EN + BOOT\n+ гребінки GPIO\n(рівні: 3.3 В!)", size=12,
                           fill="#edf7ed", stroke=FIELD, pad=10)
    frags.append(tb_btn)

    # ─── ядро чипа в центрі кожної колонки (внизу) ──────────────────────────
    # (вказуємо стрілками що «навколо ядра»)
    frags.append(line(70, 58, 70, H - 30, color=MUTED, sw=0.8, dash="3,3"))
    frags.append(line(790, 58, 790, H - 30, color=MUTED, sw=0.8, dash="3,3"))

    # ─── підпис-висновок унизу ───────────────────────────────────────────────
    note = ("Навколо 8-бітного AVR — більше дискретних вузлів;  "
            "у ESP32 USB-логіку / тактування глибше інтегровано в чип")
    tb_note, _, _ = textbox(430, H - 18, note, size=11, fill="#f8f8f8",
                            stroke=MUTED, pad=8, color=MUTED)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-11-2c-1-board-anatomy.svg"), W, H,
           *frags,
           title="Анатомія плати: Uno/Nano-клас vs ESP32 DevKit")


# ── Фігура 2: Сходи самодостатності плат ───────────────────────────────────

def fig2_integration_ladder():
    W, H = 820, 360
    frags = []

    # горизонтальна шкала «сходів»
    steps = [
        ("Pro Mini-клас", "без USB\n(треба зовн. FTDI)", "#fdecea", POS),
        ("Nano-клас", "USB на борту\n(під макетку)", "#fef9e7", "#e67e22"),
        ("Uno-клас", "USB + шилд-роз'єм\n+ DIP-панелька", "#edf7ed", FIELD),
        ("ESP32 DevKit", "USB + Wi-Fi/BLE\nінтегровані в чип\nавто-скидання", "#e8f4fd", NEG),
    ]

    n = len(steps)
    col_w = W // n
    bar_h = 200
    base_y = H - 60
    bar_bottom = base_y

    for i, (label, sub, fill, stroke_c) in enumerate(steps):
        bh = int(bar_h * (i + 1) / n)
        bx = i * col_w + 20
        bw = col_w - 40
        by = bar_bottom - bh

        # стовпчик
        frags.append(fitbox(bx, by, bw, bh, label + "\n" + sub,
                            size=12, fill=fill, stroke=stroke_c, sw=2, pad=8))

    # підпис осі X
    tb_ax, _, _ = textbox(W // 2, H - 20, "Рівень інтеграції / самодостатності →", size=12,
                          fill="#f8f8f8", stroke=MUTED, pad=6, color=MUTED)
    frags.append(tb_ax)

    render(os.path.join(OUT, "fig-11-2c-2-integration-ladder.svg"), W, H,
           *frags,
           title="Сходи самодостатності плат: від Pro Mini до ESP32 DevKit")


# ── Запуск ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p1 = fig1_board_anatomy()
    p2 = fig2_integration_ladder()
    print("Готово:")
    print("  ", os.path.join(OUT, "fig-11-2c-1-board-anatomy.svg"))
    print("  ", os.path.join(OUT, "fig-11-2c-2-integration-ladder.svg"))
