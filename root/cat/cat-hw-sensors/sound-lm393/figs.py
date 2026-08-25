# -*- coding: utf-8 -*-
"""Фігури до статті «Звуковий давач з мікрофоном (LM393)».
Три SVG: тракт сигналу, принципова схема модуля, підключення пін-у-пін.
Запуск: python figs.py  → пише у ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Тракт сигналу: чому це поріг, а не вимірювач
# ─────────────────────────────────────────────────────────────────────────────
def fig_chain():
    W, H = 820, 360
    p = []

    # чотири блоки-станції
    y = 150
    bw, bh = 150, 88
    xs = [30, 250, 470, 640]

    # 1 — мікрофон
    p.append(fitbox(xs[0], y, bw, bh,
                    "Електретний\nмікрофон\n(звук → струм)",
                    size=14, fill="#eef4ff", stroke=NEG, bold=True))
    # 2 — резистор зміщення
    p.append(fitbox(xs[1], y, bw, bh,
                    "Резистор зміщення\n(струм → напруга,\nсирий сигнал)",
                    size=13, fill=FILL, bold=True))
    # 3 — компаратор
    p.append(fitbox(xs[2], y, bw - 20, bh,
                    "LM393\nпорівнює\nз порогом",
                    size=14, fill="#eafaf0", stroke=FIELD, bold=True))
    # 4 — вихід
    p.append(fitbox(xs[3], y, bw, bh,
                    "Цифровий вихід\n0 або 1\n(відкритий колектор)",
                    size=13, fill=FILL, bold=True))

    # стрілки між блоками
    p.append(arrow(xs[0] + bw, y + bh / 2, xs[1], y + bh / 2))
    p.append(arrow(xs[1] + bw, y + bh / 2, xs[2], y + bh / 2))
    p.append(arrow(xs[2] + bw - 20, y + bh / 2, xs[3], y + bh / 2))

    # поріг збоку від компаратора — окремим написом, щоб не накладати
    tx = xs[2] + (bw - 20) / 2
    p.append(text(tx, y - 22, "поріг задає гвинтик", size=13, color=MUTED))
    p.append(arrow(tx, y - 14, tx, y - 2, color=MUTED, sw=1.5))

    # знизу — підпис-висновок під кожним переходом
    p.append(text((xs[1] + xs[2]) / 2 + bw / 2 - 10, y + bh + 34,
                  "гучніше → більший розмах, але ЛІНІЙНОГО підсилення тут нема",
                  size=13, color=INK))
    p.append(text((xs[3]) + bw / 2, y + bh + 34,
                  "лунко → 0, тиша → 1", size=13, color=POS, bold=True))

    return render(os.path.join(IMG, 'signal-chain.svg'), W, H, *p,
                  title="Тракт сигналу: мікрофон → сирий сигнал → поріг → біт")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Принципова схема модуля
# ─────────────────────────────────────────────────────────────────────────────
def fig_schematic():
    W, H = 880, 500
    p = []

    # шини живлення
    vcc_y, gnd_y = 64, 452
    x0, x1 = 70, 820
    p.append(line(x0, vcc_y, x1, vcc_y, color=POS, sw=2.5))
    p.append(line(x0, gnd_y, x1, gnd_y, color=NEG, sw=2.5))
    p.append(text(x0, vcc_y - 12, "+V (3.3–5 В)", size=14, color=POS, anchor="start", bold=True))
    p.append(text(x0, gnd_y + 26, "GND", size=14, color=NEG, anchor="start", bold=True))

    def res_v(x, top, h, label, sub=None, fill=FILL, stroke=LINE):
        """Вертикальний резистор: рамка + підпис ЗЛІВА, щоб жоден дріт її не перетнув."""
        p.append(rect(x - 16, top, 32, h, fill=fill, stroke=stroke, sw=1.6))
        p.append(text(x - 24, top + h / 2 + 4, label, size=13, anchor="end", bold=True))
        if sub:
            p.append(text(x + 24, top + h / 2 + 4, sub, size=11, color=MUTED, anchor="start"))

    # ── ліворуч: мікрофон + резистор зміщення ──
    mic_x = 130
    node_mic_y = 250                       # вузол сирого сигналу
    p.append(line(mic_x, vcc_y, mic_x, 120))
    res_v(mic_x, 120, 46, "Rзм", "≈2 кΩ")
    p.append(line(mic_x, 166, mic_x, node_mic_y))
    # мікрофон від вузла до землі
    p.append(circle(mic_x, node_mic_y + 60, 30, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(mic_x, node_mic_y + 56, "MIC", size=13, color=NEG, bold=True))
    p.append(text(mic_x, node_mic_y + 72, "JFET", size=11, color=MUTED))
    p.append(line(mic_x, node_mic_y + 90, mic_x, gnd_y))
    p.append(circle(mic_x, node_mic_y, 3.5, fill=INK, stroke=INK))
    # відведення сирого сигналу праворуч (у «+» входу)
    p.append(line(mic_x, node_mic_y, 300, node_mic_y))

    # ── тример-подільник задає поріг ──
    pot_x = 300
    thr_y = 320
    p.append(line(pot_x, vcc_y, pot_x, 150))
    p.append(rect(pot_x - 20, 150, 40, 150, fill="#fff7e6", stroke="#b8860b", sw=1.8))
    p.append(text(pot_x, 222, "тример", size=12, bold=True))
    p.append(text(pot_x, 240, "10 кΩ", size=11, color=MUTED))
    p.append(line(pot_x, 300, pot_x, gnd_y))
    # повзунок → поріг (виходить праворуч на нижньому рівні)
    p.append(line(pot_x + 20, thr_y - 40, pot_x + 44, thr_y - 40, color="#b8860b", sw=1.8))
    p.append(line(pot_x + 44, thr_y - 40, pot_x + 44, thr_y, color="#b8860b", sw=1.8))
    p.append(line(pot_x + 44, thr_y, 470, thr_y, color="#b8860b", sw=1.8))
    p.append(text(pot_x + 90, thr_y - 8, "поріг", size=12, color="#b8860b"))

    # ── компаратор LM393 (трикутник) ──
    cx = 480
    cy = (node_mic_y + thr_y) / 2          # між двома входами
    tri = ('<path d="M%d %d L%d %d L%d %d Z" fill="#eafaf0" stroke="%s" stroke-width="2"/>'
           % (cx, cy - 55, cx, cy + 55, cx + 96, cy, FIELD))
    p.append(tri)
    p.append(text(cx + 30, cy + 5, "LM393", size=13, bold=True))
    # входи: «+» вгорі (сигнал мікрофона), «−» внизу (поріг)
    p.append(text(cx + 12, node_mic_y + 5, "+", size=17, color=POS, bold=True))
    p.append(text(cx + 12, thr_y + 5, "−", size=17, color=NEG, bold=True))
    p.append(line(300, node_mic_y, cx, node_mic_y))     # сигнал → «+»
    p.append(line(470, thr_y, cx, thr_y))               # поріг → «−»
    # короткі стуби живлення компаратора (не через увесь малюнок)
    p.append(line(cx + 40, cy - 37, cx + 40, vcc_y, color=POS, sw=1, dash="4 4"))
    p.append(line(cx + 55, cy + 37, cx + 55, gnd_y, color=NEG, sw=1, dash="4 4"))

    # ── вихід: відкритий колектор + підтяжка + LED тривоги ──
    out_x = cx + 96
    node_out_x = 660
    p.append(line(out_x, cy, node_out_x, cy))
    p.append(circle(node_out_x, cy, 3.5, fill=INK, stroke=INK))
    # підтяжка до +V (підпис зліва — дріт її не чіпає)
    p.append(line(node_out_x, cy, node_out_x, 150))
    res_v(node_out_x, 150, 44, "Rпд", "10 кΩ")
    p.append(line(node_out_x, 150, node_out_x, vcc_y))
    # штир OUT донизу
    p.append(line(node_out_x, cy, node_out_x, cy + 90))
    p.append(circle(node_out_x, cy + 90, 5, fill=BG, stroke=INK, sw=2))
    p.append(text(node_out_x, cy + 112, "OUT", size=13, bold=True))

    # LED тривоги: +V → R → LED → вузол виходу
    led_x = 750
    p.append(line(led_x, vcc_y, led_x, 150))
    res_v(led_x, 150, 40, "R")
    p.append(line(led_x, 190, led_x, 300))
    p.append('<path d="M%d %d L%d %d L%d %d Z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (led_x - 12, 300, led_x + 12, 300, led_x, 324, POS))
    p.append(line(led_x - 14, 324, led_x + 14, 324, color=POS, sw=2))
    p.append(text(led_x + 22, 316, "LED", size=11, color=MUTED, anchor="start"))
    p.append(text(led_x + 22, 330, "тривоги", size=11, color=MUTED, anchor="start"))
    p.append(line(led_x, 324, led_x, cy))
    p.append(line(led_x, cy, node_out_x, cy))
    p.append(circle(led_x, cy, 3.5, fill=INK, stroke=INK))

    return render(os.path.join(IMG, 'schematic.svg'), W, H, *p,
                  title="Принципова схема: мікрофон, тример-поріг, компаратор LM393, вихід")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Підключення пін-у-пін
# ─────────────────────────────────────────────────────────────────────────────
def fig_wiring():
    W, H = 820, 430
    p = []

    # три спільні рівні дротів — далеко один від одного
    y_out, y_vcc, y_gnd = 150, 210, 270

    # модуль ліворуч
    mx, my, mw, mh = 60, 80, 250, 250
    p.append(rect(mx, my, mw, mh, fill="#eef4ff", stroke=NEG, sw=2, rx=10))
    p.append(text(mx + mw / 2, my + 30, "Модуль LM393", size=16, bold=True, color=NEG))
    p.append(text(mx + mw / 2, my + 50, "(звуковий, 3 штирі)", size=12, color=MUTED))
    # мікрофон-кружок і тример — вгорі, вище рівнів дротів
    p.append(circle(mx + 62, my + 92, 24, fill=BG, stroke=NEG, sw=2))
    p.append(text(mx + 62, my + 97, "MIC", size=12, bold=True))
    p.append(rect(mx + 150, my + 74, 50, 36, fill="#fff7e6", stroke="#b8860b", sw=1.6))
    p.append(text(mx + 175, my + 96, "тример", size=10))

    # три штирі на правому краю модуля
    px = mx + mw
    mod_pins = [("OUT", y_out, INK), ("+", y_vcc, POS), ("−", y_gnd, NEG)]
    for name, yy, col in mod_pins:
        p.append(circle(px, yy, 6, fill=BG, stroke=INK, sw=2))
        p.append(text(px - 16, yy + 5, name, size=14, anchor="end", bold=True, color=col))

    # плата МК праворуч
    bx, by, bw2, bh2 = 580, 80, 200, 250
    p.append(rect(bx, by, bw2, bh2, fill="#eafaf0", stroke=FIELD, sw=2, rx=10))
    p.append(text(bx + bw2 / 2, by + 30, "Мікроконтролер", size=15, bold=True, color=FIELD))
    p.append(text(bx + bw2 / 2, by + 50, "(Arduino / ESP32)", size=11, color=MUTED))
    mcu_pins = [("D2", y_out), ("5V / 3.3V", y_vcc), ("GND", y_gnd)]
    for name, yy in mcu_pins:
        p.append(circle(bx, yy, 6, fill=BG, stroke=INK, sw=2))
        p.append(text(bx + 16, yy + 5, name, size=13, anchor="start", bold=True))

    # прямі дроти (рівні збігаються — без зламів)
    p.append(line(px, y_out, bx, y_out, color=INK, sw=2.4))
    p.append(line(px, y_vcc, bx, y_vcc, color=POS, sw=2.4))
    p.append(line(px, y_gnd, bx, y_gnd, color=NEG, sw=2.4))

    # підписи призначення — НАД відповідним дротом, по центру проміжку
    midx = (px + bx) / 2
    p.append(text(midx, y_out - 12, "сигнал → цифровий вхід", size=12, color=MUTED))
    p.append(text(midx, y_vcc - 12, "живлення", size=12, color=MUTED))
    p.append(text(midx, y_gnd - 12, "спільна земля", size=12, color=MUTED))

    # примітка про 4-й штир AO
    note = ("У 4-штиревих варіантах є ще AO — сирий аналоговий сигнал мікрофона\n"
            "на вхід АЦП. У класичного блакитного модуля лише цифровий OUT.")
    p.append(fitbox(120, 356, 580, 52, note, size=12, fill="#fff9e6",
                    stroke="#b8860b", color=INK))

    return render(os.path.join(IMG, 'wiring.svg'), W, H, *p,
                  title="Підключення: OUT → цифровий вхід, живлення й спільна земля")


if __name__ == '__main__':
    fig_chain()
    fig_schematic()
    fig_wiring()
    print("OK: signal-chain.svg, schematic.svg, wiring.svg")
