# -*- coding: utf-8 -*-
"""Фігури для вставки math-compensation (математика компенсації BMP280).
Вивід у ./img/. Запуск:  python figs_math.py
Окремий файл, щоб не чіпати figs.py статті-власника.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: конвеєр компенсації — чому порядок і звідки t_fine ──────────────
def fig_pipeline():
    W, H = 940, 560
    frags = []

    frags.append(text(W / 2, 54, "чому спершу температура, а потім тиск — і що їх зшиває", size=13, color=MUTED))

    # NVM — заводські коефіцієнти (ліворуч, живлять обидва поліноми)
    b, wn, hn = textbox(150, 300, "NVM чипа\n(0x88…0x9F)\ndig_T1..T3\ndig_P1..P9\nсвої в кожного\nекземпляра", size=12,
                        bold=True, fill="#fff7e6", stroke="#b8860b", min_w=190)
    frags.append(b)

    # Верхня доріжка: сирий T → поліном T → °C + t_fine
    b, wa, ha = textbox(430, 150, "сирий adc_T\n20 біт", size=12, bold=True,
                        fill="#eef2ff", stroke=NEG, min_w=150)
    frags.append(b)
    b, wb, hb = textbox(660, 150, "поліном\nтемператури", size=12, bold=True,
                        fill="#ffffff", stroke=NEG, min_w=170)
    frags.append(b)
    frags.append(line(430 + wa / 2, 150, 660 - wb / 2, 150, color=NEG, sw=2.2))

    # Виходи полінома T: °C (нагору) і t_fine (донизу)
    b, wc, hc = textbox(860, 100, "T, °C", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=90)
    frags.append(b)
    frags.append(line(660 + wb / 2, 140, 860 - wc / 2, 100, color=FIELD, sw=2.0))

    b, wt, ht = textbox(660, 300, "t_fine\n(температурна\nпоправка)", size=12, bold=True,
                        fill="#fdecea", stroke=POS, min_w=170)
    frags.append(b)
    frags.append(line(660, 150 + hb / 2, 660, 300 - ht / 2, color=POS, sw=2.4))

    # Нижня доріжка: сирий P → поліном P (вживає t_fine) → Pa
    b, wp, hp = textbox(430, 440, "сирий adc_P\n20 біт", size=12, bold=True,
                        fill="#eef2ff", stroke=NEG, min_w=150)
    frags.append(b)
    b, wq, hq = textbox(660, 440, "поліном\nтиску\n(вживає t_fine)", size=12, bold=True,
                        fill="#ffffff", stroke=NEG, min_w=170)
    frags.append(b)
    frags.append(line(430 + wp / 2, 440, 660 - wq / 2, 440, color=NEG, sw=2.2))
    # t_fine спускається в поліном тиску
    frags.append(line(660, 300 + ht / 2, 660, 440 - hq / 2, color=POS, sw=2.4))

    b, wr, hr = textbox(860, 440, "тиск, Pa", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD, min_w=110)
    frags.append(b)
    frags.append(line(660 + wq / 2, 440, 860 - wr / 2, 440, color=FIELD, sw=2.0))

    # NVM живить обидва поліноми (дві тонкі лінії)
    frags.append(line(150 + wn / 2, 250, 660 - wb / 2 - 6, 175, color="#b8860b", sw=1.6, dash="5,4"))
    frags.append(line(150 + wn / 2, 350, 660 - wq / 2 - 6, 420, color="#b8860b", sw=1.6, dash="5,4"))

    # Підпис-стрілка порядку
    b, _, _ = textbox(430, 300, "порядок\nобовʼязковий\n↓ згори вниз", size=11, bold=True,
                      fill="#f4f6f8", stroke=MUTED, min_w=140)
    frags.append(b)

    render(os.path.join(IMG, "pipeline.svg"), W, H, *frags,
           title="Конвеєр компенсації BMP280")


# ── Фігура 2: чому сирий відлік нелінійний і пливе від температури ────────────
def fig_nonlinear():
    W, H = 900, 520
    frags = []
    frags.append(text(W / 2, 52, "сирий 20-бітний відлік проти справжнього тиску", size=13, color=MUTED))

    # Осі
    ox, oy = 130, 430          # початок координат (лівий-нижній)
    ax_w, ax_h = 660, 320
    frags.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=2))        # X
    frags.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=2))        # Y
    frags.append(text(ox + ax_w / 2, oy + 42, "справжній тиск p  →", size=12, color=INK))
    frags.append(text(ox - 96, oy - ax_h / 2, "сирий", size=12, color=INK, anchor="middle"))
    frags.append(text(ox - 96, oy - ax_h / 2 + 18, "adc_P", size=12, color=INK, anchor="middle"))

    # Дві криві (нелінійні), зсунуті одна від одної температурою.
    # Беремо просту опуклу форму: y = base + k*(x^1.35), масштабуємо в рамку.
    import math
    def curve(color, dx, label, ly):
        pts = []
        N = 40
        for i in range(N + 1):
            fx = i / N
            fy = 0.12 + 0.8 * (fx ** 1.32)          # нелінійна залежність
            X = ox + 30 + fx * (ax_w - 70)
            Y = oy - (fy * (ax_h - 30)) - dx
            pts.append("%.1f,%.1f" % (X, Y))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                     % (" ".join(pts), color))
        # підпис кривої біля правого кінця
        frags.append(text(ox + ax_w - 12, ly, label, size=12, color=color, anchor="end", bold=True))

    curve(NEG, 0, "при +25 °C", oy - ax_h + 40)
    curve(POS, 46, "при +5 °C (зсув)", oy - ax_h + 66)

    # Показ «однаковий тиск → різний сирий відлік»
    xv = ox + 30 + 0.62 * (ax_w - 70)
    frags.append(line(xv, oy, xv, oy - ax_h + 30, color=MUTED, sw=1.4, dash="4,4"))
    b, _, _ = textbox(xv + 118, oy - 150,
                      "той самий тиск →\nрізний сирий відлік\nпоки не врахуєш T",
                      size=11, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=200)
    frags.append(b)

    b, _, _ = textbox(300, oy - ax_h - 4,
                      "залежність вигнута (не пряма) і зсувається з температурою —\nтому потрібні і поліном, і t_fine",
                      size=11, bold=True, fill="#fff7e6", stroke="#b8860b", min_w=470)
    frags.append(b)

    render(os.path.join(IMG, "nonlinear.svg"), W, H, *frags,
           title="Нелінійність і температурний дрейф сирого відліку")


if __name__ == "__main__":
    fig_pipeline()
    fig_nonlinear()
    print("OK: pipeline.svg, nonlinear.svg")
