# -*- coding: utf-8 -*-
"""Фігури до вставки «TL431 — програмований стабілітрон» (comp-tl431.md).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Дві фігури, яких НЕ дає базова comp-voltage-reference.md:
  1) tl431-stability.svg — карта стійкості за ємністю навантаження («долина генерації»);
  2) tl431-smps.svg      — петля зворотного зв'язку імпульсного БЖ через оптопару.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Карта стійкості за ємністю на катоді ──────────────────────────────────
def fig_stability():
    W, H = 760, 360
    f = [text(W / 2, 28, "Стійкість TL431 за ємністю на катоді", size=16, bold=True)]

    # логарифмічна вісь ємності
    ax_y = 230
    x0, x1 = 70, 700
    f.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    f.append(arrow(x1 - 4, ax_y, x1 + 4, ax_y, color=INK))
    f.append(text(x1 + 6, ax_y + 5, "C", size=14, bold=True, italic=True, anchor="start"))

    # поділки (декади): 10pF 100pF 1nF 10nF 100nF 1µF 10µF
    ticks = ["10 пФ", "100 пФ", "1 нФ", "10 нФ", "100 нФ", "1 мкФ", "10 мкФ"]
    n = len(ticks)
    xs = [x0 + (x1 - x0 - 30) * i / (n - 1) for i in range(n)]
    for x, lab in zip(xs, ticks):
        f.append(line(x, ax_y - 5, x, ax_y + 5, color=INK, sw=1.4))
        f.append(text(x, ax_y + 22, lab, size=11, color=MUTED))

    # три смуги: стійко (мала C) | ГЕНЕРАЦІЯ | стійко (велика C)
    band_top, band_h = ax_y - 90, 70
    # межі ~ 50пФ і ~10мкФ; «долина» між ними
    xa = xs[0] + (xs[1] - xs[0]) * 0.7          # ~50 пФ
    xb = xs[5] + (xs[6] - xs[5]) * 0.6          # ~3..10 мкФ
    f.append(rect(x0, band_top, xa - x0, band_h, fill="#e8f6ee", stroke=FIELD, sw=1.5))
    f.append(rect(xa, band_top, xb - xa, band_h, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(rect(xb, band_top, x1 - 30 - xb, band_h, fill="#e8f6ee", stroke=FIELD, sw=1.5))

    f.append(text((x0 + xa) / 2, band_top + band_h / 2 + 4, "стійко", size=12, bold=True, color=FIELD))
    f.append(text((xa + xb) / 2, band_top + band_h / 2 - 4, "ГЕНЕРАЦІЯ", size=14, bold=True, color=POS))
    f.append(text((xa + xb) / 2, band_top + band_h / 2 + 16, "(петля дзвенить)", size=11, color=POS))
    f.append(text((xb + x1 - 30) / 2, band_top + band_h / 2 + 4, "стійко", size=12, bold=True, color=FIELD))

    # підписи-«куди ставити»
    f.append(text((x0 + xa) / 2, band_top - 12, "майже нічого", size=11, color=MUTED))
    f.append(text((xb + x1 - 30) / 2, band_top - 12, "явно багато", size=11, color=MUTED))

    # стрілка «не зупиняйся посередині»
    xm = (xa + xb) / 2
    f.append(line(xm, ax_y + 44, xm, band_top + band_h + 4, color=POS, sw=1.6, dash="5 4"))
    f.append(text(xm, ax_y + 60, "тут зупинятися НЕ можна", size=12, bold=True, color=POS))

    # нижній напис-висновок
    f.append(text(W / 2, H - 18,
                  "Безпечні береги — обабіч; «посередині» (≈1 нФ…1 мкФ) петля втрачає стійкість.",
                  size=12, color=INK))
    return render(os.path.join(IMG, "tl431-stability.svg"), W, H, *f)


# ── 2. TL431 як вузол похибки імпульсного БЖ (через оптопару) ────────────────
def fig_smps():
    W, H = 780, 380
    f = [text(W / 2, 26, "TL431 тримає вихід БЖ: дільник → петля → оптопара → ШІМ", size=15, bold=True)]

    # бар'єр ізоляції
    bx = 430
    f.append(line(bx, 56, bx, H - 30, color=MUTED, sw=1.4, dash="6 5"))
    f.append(text(bx, 50, "бар'єр ізоляції", size=11, color=MUTED))
    f.append(text(bx - 90, H - 14, "вторинна сторона", size=11, color=MUTED))
    f.append(text(bx + 100, H - 14, "первинна сторона", size=11, color=MUTED))

    # вихідна шина Vout (вторинна)
    yv = 90
    f.append(line(70, yv, 360, yv, color=POS, sw=4))
    f.append(text(70, yv - 12, "Vout (напр. 5 В)", size=12, bold=True, color=POS, anchor="start"))

    # оптопара: світлодіод з катода TL431
    led_x = 300
    f.append(line(led_x, yv, led_x, 140, color=POS, sw=2))
    f.append(text(led_x + 8, 128, "LED опто", size=11, color=MUTED, anchor="start"))
    f.append(circle(led_x, 150, 7, fill="#fff3e0", stroke="#b8860b", sw=1.8))

    # TL431 блок
    tx, ty, tw, th = 250, 200, 100, 70
    f.append(rect(tx, ty, tw, th, fill="#eef3f9", stroke=LINE, sw=2))
    f.append(text(tx + tw / 2, ty + 26, "TL431", size=14, bold=True))
    f.append(text(tx + tw / 2, ty + 46, "(вузол", size=10, color=MUTED))
    f.append(text(tx + tw / 2, ty + 60, "похибки)", size=10, color=MUTED))

    # катод TL431 ↔ світлодіод оптопари
    f.append(line(tx + tw / 2, ty, led_x, 157, color=INK, sw=1.6))
    f.append(text(tx + tw / 2 + 14, ty - 8, "CATHODE", size=10, color=MUTED, anchor="start"))

    # дільник R1/R2 з Vout на REF
    dx = 150
    f.append(line(dx, yv, dx, 210, color=INK, sw=1.6))           # від Vout вниз
    f.append(rect(dx - 12, 120, 24, 26, fill=FILL, stroke=LINE, sw=1.4))
    f.append(text(dx - 22, 136, "R1", size=11, bold=True, anchor="end"))
    f.append(line(dx, 146, dx, 178, color=INK, sw=1.6))
    # вузол REF
    f.append(circle(dx, 178, 4, fill=INK, stroke=INK))
    f.append(line(dx, 178, tx, ty + th / 2, color=INK, sw=1.6))  # до REF
    f.append(text(tx - 6, ty + th / 2 - 6, "REF", size=10, color=MUTED, anchor="end"))
    f.append(rect(dx - 12, 200, 24, 26, fill=FILL, stroke=LINE, sw=1.4))
    f.append(text(dx - 22, 216, "R2", size=11, bold=True, anchor="end"))
    f.append(line(dx, 226, dx, 300, color=INK, sw=1.6))

    # земля (ANODE / R2 низ)
    gy = 300
    f.append(line(dx, gy, tx + tw / 2, gy, color=INK, sw=1.6))
    f.append(line(tx + tw / 2, ty + th, tx + tw / 2, gy, color=INK, sw=1.6))  # ANODE вниз
    f.append(text(tx + tw / 2 + 10, ty + th + 14, "ANODE", size=10, color=MUTED, anchor="start"))
    for i in range(3):
        gw = 26 - i * 8
        f.append(line(dx - gw / 2, gy + 6 + i * 5, dx + gw / 2, gy + 6 + i * 5, color=INK, sw=1.6))

    # первинна сторона: фототранзистор → ШІМ → трансформатор
    f.append(circle(bx + 60, 150, 7, fill="#fff3e0", stroke="#b8860b", sw=1.8))
    f.append(text(bx + 60, 128, "фото-Т", size=11, color=MUTED))
    pwm = fitbox(bx + 110, 190, 110, 56, "ШІМ-\nконтролер", size=12, bold=True,
                 fill="#eef3f9", stroke=LINE)
    f.append(pwm)
    f.append(line(bx + 60, 157, bx + 60, 200, color=INK, sw=1.6))
    f.append(line(bx + 60, 200, bx + 110, 210, color=INK, sw=1.6))

    # напрям регулювання
    f.append(arrow(360, 70, 410, 70, color=NEG))
    f.append(text(385, 58, "Vout ↑", size=11, color=NEG))
    f.append(text(bx + 165, 270, "→ менше потужності → Vout ↓", size=11, color=NEG, anchor="middle"))

    return render(os.path.join(IMG, "tl431-smps.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stability()
    fig_smps()
    print("OK:", IMG)
