# -*- coding: utf-8 -*-
# Фігури для вставки math-closed-loop-derivation.md (окремо від figs.py теми).
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: структурна схема замкненої петлі з вузлом суматора ───────────────
# Показує тракт R → ⊕ → C → P → Y і від'ємний зворотний зв'язок через H.
# Позначено E = R − H·Y (те, що входить у суматор) — джерело всієї викладки.

def fig_block_diagram():
    W, H = 760, 340
    p = []

    y = 150                      # головна лінія тракту
    yfb = 268                    # лінія зворотного зв'язку

    # координати ключових точок по горизонталі
    x_r = 40                     # вхід R
    x_sum = 150                  # суматор
    x_c = 300                    # блок C (регулятор)
    x_p = 470                    # блок P (об'єкт)
    x_y = 690                    # вихід Y
    x_tap = 640                  # відгалуження на зв'язок
    x_h = 380                    # блок H у зворотному тракті

    def block(cx, cw, label, sub):
        ch = 56
        q = [rect(cx - cw / 2, y - ch / 2, cw, ch, fill="#eef3fb", stroke=NEG, sw=1.8, rx=8)]
        q.append(text(cx, y - 4, label, size=20, color=INK, bold=True))
        q.append(text(cx, y + 16, sub, size=11, color=MUTED))
        return q

    # вхід R
    p.append(text(x_r - 4, y - 12, "R(s)", size=15, color=INK, bold=True, anchor="start"))
    p.append(text(x_r - 4, y + 20, "завдання", size=11, color=MUTED, anchor="start"))
    p.append(line(x_r, y, x_sum - 22, y, color=LINE, sw=2.0))
    p.append(arrow(x_sum - 34, y, x_sum - 20, y, color=LINE, sw=2.0))

    # суматор (кружок Σ); «+» на вході завдання, «−» на вході зворотного зв'язку
    p.append(circle(x_sum, y, 20, fill=BG, stroke=INK, sw=2.0))
    p.append(text(x_sum, y + 7, "Σ", size=22, color=INK, bold=True))
    p.append(text(x_sum - 26, y - 8, "+", size=17, color=NEG, bold=True))   # вхід R
    p.append(text(x_sum + 16, y + 22, "−", size=19, color=POS, bold=True))  # вхід H·Y

    # E(s) — сигнал похибки з суматора в регулятор
    p.append(line(x_sum + 20, y, x_c - 42, y, color=LINE, sw=2.0))
    p.append(arrow(x_c - 54, y, x_c - 40, y, color=LINE, sw=2.0))
    p.append(text((x_sum + 20 + x_c - 42) / 2, y - 12, "E(s)", size=14, color=POS, bold=True))
    p.append(text((x_sum + 20 + x_c - 42) / 2, y + 20, "похибка", size=10, color=MUTED))

    # блок C
    p += block(x_c, 74, "C(s)", "регулятор")
    p.append(line(x_c + 37, y, x_p - 42, y, color=LINE, sw=2.0))
    p.append(arrow(x_p - 54, y, x_p - 40, y, color=LINE, sw=2.0))

    # блок P
    p += block(x_p, 74, "P(s)", "об'єкт")
    p.append(line(x_p + 37, y, x_y, y, color=LINE, sw=2.0))
    p.append(arrow(x_y - 14, y, x_y, y, color=LINE, sw=2.0))

    # вихід Y
    p.append(text(x_y + 6, y - 12, "Y(s)", size=15, color=INK, bold=True, anchor="start"))
    p.append(text(x_y + 6, y + 20, "вихід", size=11, color=MUTED, anchor="start"))

    # відгалуження на зворотний зв'язок
    p.append(circle(x_tap, y, 4.0, fill=INK, stroke=INK, sw=1.0))
    p.append(line(x_tap, y, x_tap, yfb, color=LINE, sw=2.0))
    # униз, потім ліворуч через H, потім угору в суматор
    p.append(line(x_tap, yfb, x_h + 40, yfb, color=LINE, sw=2.0))
    p.append(arrow(x_h + 54, yfb, x_h + 40, yfb, color=LINE, sw=2.0))

    # блок H у зворотному тракті
    hh = 50
    p.append(rect(x_h - 40, yfb - hh / 2, 80, hh, fill="#eefaf0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x_h, yfb - 3, "H(s)", size=18, color=INK, bold=True))
    p.append(text(x_h, yfb + 15, "давач", size=11, color=MUTED))

    # від H ліворуч і вгору в суматор (нижній вхід)
    p.append(line(x_h - 40, yfb, x_sum, yfb, color=LINE, sw=2.0))
    p.append(line(x_sum, yfb, x_sum, y + 20, color=LINE, sw=2.0))
    p.append(arrow(x_sum, y + 34, x_sum, y + 20, color=LINE, sw=2.0))
    # підпис сигналу зворотного зв'язку
    p.append(text((x_h - 40 + x_sum) / 2, yfb + 18, "H·Y  (вимір)", size=12, color=FIELD, bold=True))

    # рамка з рівнянням вузла — ЧЕРЕЗ textbox
    b, bw, bh = textbox(x_c + 20, 46, "у суматорі:  E = R − H·Y",
                        size=15, color=INK, bold=True, fill="#fff8e6", stroke="#d9a400")
    p.append(b)

    render(os.path.join(OUT, "m-block-diagram.svg"), W, H, *p,
           title="Замкнена петля: суматор віднімає вимір H·Y від завдання R")


# ── Фігура 2: полюс визначає знак показника — LHP гасне, RHP росте ─────────────
# s-площина: ліва півплощина (стійко, e^(σt) з σ<0 згасає), уявна вісь (межа),
# права (зрив, σ>0 росте). Біля кількох полюсів — маленькі часові криві.

def fig_pole_sign():
    W, H = 760, 430
    p = []

    cx = 300                     # центр осей (Re=0, Im=0)
    cy = 210
    axr = 250                    # піврозмах осі Re
    ayr = 150                    # піврозмах осі Im

    # заливка правої півплощини (небезпечна)
    p.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="#fdece9"/>'
             % (cx, cy - ayr - 6, axr + 30, 2 * (ayr + 6)))
    # заливка лівої (стійка)
    p.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="#eefaf1"/>'
             % (cx - axr - 30, cy - ayr - 6, axr + 30, 2 * (ayr + 6)))

    # вісь Re
    p.append(line(cx - axr - 24, cy, cx + axr + 24, cy, color=INK, sw=1.6))
    p.append(arrow(cx + axr + 8, cy, cx + axr + 26, cy, color=INK, sw=1.6))
    p.append(text(cx + axr + 22, cy + 20, "Re s = σ", size=13, color=INK, italic=True, anchor="end"))
    # вісь Im (= межа стійкості)
    p.append(line(cx, cy + ayr + 20, cx, cy - ayr - 24, color=INK, sw=1.6))
    p.append(arrow(cx, cy - ayr - 8, cx, cy - ayr - 26, color=INK, sw=1.6))
    p.append(text(cx + 8, cy - ayr - 16, "Im s = ω", size=13, color=INK, italic=True, anchor="start"))

    # підписи півплощин
    p.append(text(cx - axr + 6, cy - ayr + 8, "σ < 0", size=15, color=FIELD, bold=True, anchor="start"))
    p.append(text(cx - axr + 6, cy - ayr + 28, "згасає — СТІЙКО", size=12, color=FIELD, anchor="start"))
    p.append(text(cx + axr - 6, cy - ayr + 8, "σ > 0", size=15, color=POS, bold=True, anchor="end"))
    p.append(text(cx + axr - 6, cy - ayr + 28, "росте — ЗРИВ", size=12, color=POS, anchor="end"))
    # межа
    p.append(text(cx + 6, cy + ayr + 14, "σ = 0 : межа (стале гойдання)", size=11, color=MUTED, anchor="start"))

    def mini_wave(mx, my, sigma, color=INK, w=64, amp=18):
        """Маленька осцилограма e^(sigma t)·cos: sigma<0 гасне, >0 росте, =0 стале.
        Обвідну обмежуємо, щоб крива росту не вилітала за свій мінікадр."""
        q = []
        # осі мініграфіка
        q.append(line(mx, my, mx + w, my, color=MUTED, sw=0.9))
        pts = []
        n = 90
        for i in range(n + 1):
            t = i / n
            env = math.exp(sigma * t * 1.9)
            if env > 2.6:            # стеля обвідної — крива лишається в кадрі
                env = 2.6
            # для росту стартова амплітуда менша, щоб хвіст помістився
            base = amp * (0.42 if sigma > 0 else 1.0)
            val = env * base * math.cos(2 * math.pi * 1.9 * t)
            xx = mx + t * w
            yy = my - val
            pts.append("%.1f,%.1f" % (xx, yy))
        q.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>'
                 % (" ".join(pts), color))
        return q

    def pole_pair(re, im_px, label, color, wave_sigma, side):
        """Пара полюсів (спряжені) на Re=re(px від cx), Im=±im_px; підпис і мінікрива."""
        q = []
        px = cx + re
        for sgn in (-1, 1):
            py = cy - sgn * im_px
            # хрестик — полюс
            r = 7
            q.append(line(px - r, py - r, px + r, py + r, color=color, sw=2.6))
            q.append(line(px - r, py + r, px + r, py - r, color=color, sw=2.6))
        # мінікрива поряд
        if side == "L":
            q += mini_wave(px - 78, cy - im_px - 30, wave_sigma, color=color)
            q.append(text(px - 78, cy - im_px - 52, label, size=11, color=color, bold=True, anchor="start"))
        elif side == "R":
            q += mini_wave(px + 12, cy - im_px - 30, wave_sigma, color=color)
            q.append(text(px + 12, cy - im_px - 52, label, size=11, color=color, bold=True, anchor="start"))
        else:  # межа
            q += mini_wave(px + 12, cy - im_px - 30, 0.0, color=color)
            q.append(text(px + 12, cy - im_px - 52, label, size=11, color=color, bold=True, anchor="start"))
        return q

    # стійка пара (ліворуч)
    p += pole_pair(-150, 70, "e^(−|σ|t) — гасне", FIELD, -1.0, "L")
    # межова пара (на уявній осі)
    p += pole_pair(0, 118, "e^(0·t) — стале", MUTED, 0.0, "B")
    # нестійка пара (праворуч)
    p += pole_pair(150, 70, "e^(+σt) — росте", POS, 1.0, "R")

    # підпис-висновок унизу через textbox
    b, bw, bh = textbox(cx, cy + ayr + 54,
                        "полюс = корінь 1 + L(s) = 0 ;  його Re σ = знак показника e^(σt)",
                        size=13, color=INK, bold=True, fill=FILL, stroke=LINE)
    p.append(b)

    render(os.path.join(OUT, "m-pole-sign.svg"), W, H, *p,
           title="Дійсна частина полюса задає долю: LHP згасає, RHP вибухає, вісь — межа")


if __name__ == "__main__":
    fig_block_diagram()
    fig_pole_sign()
    print("OK: figures written to", OUT)
