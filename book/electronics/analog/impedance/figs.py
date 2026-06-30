# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Дві складові опору: що кожна РОБИТЬ з енергією ───────────────────────
def fig_two_parts():
    W, H = 720, 330
    frags = []
    frags.append(text(W/2, 30, "Z = R + jX : опір + реактивність", size=17, bold=True))

    # ліва панель — резистивна частина R
    bx, by, bw, bh = 40, 70, 300, 210
    frags.append(rect(bx, by, bw, bh, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(bx+bw/2, by+34, "Дійсна частина  R", size=15, bold=True, color=POS))
    frags.append(text(bx+bw/2, by+62, "(активний опір)", size=12, color=MUTED))
    frags.append(text(bx+bw/2, by+104, "струм і напруга у фазі", size=13))
    frags.append(text(bx+bw/2, by+132, "енергія йде в тепло", size=13))
    frags.append(text(bx+bw/2, by+160, "(незворотно)", size=12, color=MUTED))
    frags.append(text(bx+bw/2, by+196, "вимір: оми, що гріються", size=12, color=MUTED, italic=True))

    # права панель — реактивна частина X
    cx0 = 380
    frags.append(rect(cx0, by, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(cx0+bw/2, by+34, "Уявна частина  X", size=15, bold=True, color=NEG))
    frags.append(text(cx0+bw/2, by+62, "(реактивний опір)", size=12, color=MUTED))
    frags.append(text(cx0+bw/2, by+104, "струм зсунутий на 90°", size=13))
    frags.append(text(cx0+bw/2, by+132, "енергія гойдається туди-сюди", size=13))
    frags.append(text(cx0+bw/2, by+160, "(повертається назад)", size=12, color=MUTED))
    frags.append(text(cx0+bw/2, by+196, "вимір: оми, що не гріють", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'two-parts.svg'), W, H, *frags)


# ── 2. Імпеданс як стрілка в комплексній площині: |Z| і кут φ ───────────────
def fig_triangle():
    W, H = 560, 420
    frags = []
    frags.append(text(W/2, 28, "Z = R + jX : модуль |Z| і кут φ", size=17, bold=True))

    ox, oy = 90, 340          # початок координат
    axlen = 380
    # осі
    frags.append(arrow(ox, oy, ox+axlen, oy, color=INK, sw=1.6))      # Re →
    frags.append(arrow(ox, oy, ox, oy-300, color=INK, sw=1.6))        # Im ↑
    frags.append(text(ox+axlen+4, oy+5, "Re  (R, оми)", size=12, color=MUTED, anchor="start"))
    frags.append(text(ox-8, oy-300+2, "Im  (X)", size=12, color=MUTED, anchor="end"))

    R = 250.0
    X = 200.0
    px, py = ox + R, oy - X
    # катети
    frags.append(line(ox, oy, px, oy, color=POS, sw=2.4))             # R
    frags.append(line(px, oy, px, py, color=NEG, sw=2.4))             # X
    # гіпотенуза = Z
    frags.append(arrow(ox, oy, px, py, color=FIELD, sw=2.8))
    frags.append(circle(px, py, 4, fill=FIELD, stroke=FIELD))

    frags.append(text(ox+R/2, oy+22, "R", size=15, bold=True, color=POS))
    frags.append(text(px+16, oy-X/2, "X", size=15, bold=True, color=NEG, anchor="start"))
    frags.append(text(ox+R/2-26, oy-X/2-18, "|Z|", size=15, bold=True, color=FIELD))

    # дужка кута
    frags.append('<path d="M %.1f %.1f A 48 48 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (ox+48, oy, ox+48*0.78, oy-48*0.62, INK))
    frags.append(text(ox+60, oy-18, "φ", size=15, bold=True))

    # формули збоку
    bx, by = 300, 70
    box = fitbox(bx, by, 230, 96,
                 "|Z| = √(R² + X²)\nφ = arctan(X / R)\nZ = |Z| · (cos φ + j·sin φ)",
                 size=13, fill=FILL, stroke=LINE)
    frags.append(box)

    render(os.path.join(OUT, 'triangle.svg'), W, H, *frags)


# ── 3. Як |Z| трьох елементів залежить від частоти ──────────────────────────
def fig_vs_freq():
    W, H = 640, 380
    frags = []
    frags.append(text(W/2, 28, "Повний опір |Z| елементів проти частоти", size=17, bold=True))

    ox, oy = 80, 320
    aw, ah = 500, 250
    frags.append(arrow(ox, oy, ox+aw, oy, color=INK, sw=1.6))
    frags.append(arrow(ox, oy, ox, oy-ah, color=INK, sw=1.6))
    frags.append(text(ox+aw+2, oy+18, "частота f →", size=12, color=MUTED, anchor="end"))
    frags.append(text(ox-10, oy-ah+2, "|Z|, оми", size=12, color=MUTED, anchor="end"))

    import math
    N = 60
    x0, x1 = ox+8, ox+aw-10
    ytop = oy-ah+30
    ybot = oy-12

    def poly(fn, color, sw=2.6):
        pts = []
        for i in range(N+1):
            t = i/N
            f = 10 ** (t*3)                 # частота 1..1000 (лог)
            v = fn(f)
            # лог по вертикалі, обрізаємо
            lv = math.log10(max(v, 0.3))
            yy = ybot - (lv + 0.5)/3.5 * (ybot-ytop)
            yy = max(ytop, min(ybot, yy))
            xx = x0 + t*(x1-x0)
            pts.append("%.1f,%.1f" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (" ".join(pts), color, sw)

    # R = const, Z_L = ωL росте, Z_C = 1/(ωC) спадає (умовні величини)
    frags.append(poly(lambda f: 30.0, INK))                       # R
    frags.append(poly(lambda f: 0.30 * f, NEG))                   # котушка
    frags.append(poly(lambda f: 3000.0 / f, POS))                # конденсатор

    frags.append(text(x1-2, ybot - (math.log10(30)+0.5)/3.5*(ybot-ytop) - 8, "R (резистор) — плоско", size=12, color=INK, anchor="end"))
    frags.append(text(x1-2, ytop+14, "котушка  Z_L = ωL ↑", size=12, color=NEG, anchor="end"))
    frags.append(text(x0+6, ytop+14, "конденсатор  Z_C = 1/(ωC) ↓", size=12, color=POS, anchor="start"))

    render(os.path.join(OUT, 'vs-freq.svg'), W, H, *frags)


# ── 4. Часова шкала: терміни, скуті Гевісайдом, і закон Ома для AC ───────────
def fig_heaviside_timeline():
    W, H = 760, 300
    frags = []
    frags.append(text(W/2, 30, "Що скував Гевісайд за два роки", size=17, bold=True))

    ox, oy = 70, 150
    ax = 640
    frags.append(arrow(ox, oy, ox+ax, oy, color=INK, sw=2))
    frags.append(text(ox+ax+2, oy+22, "час", size=12, color=MUTED, anchor="end"))

    # рік-мітки: 1886 .. 1887 рівномірно
    events = [
        (0.06, "лют. 1886", "inductance", "індуктивність", NEG),
        (0.30, "лип. 1886", "impedance", "імпеданс", FIELD),
        (0.62, "1887", "V = I·Z", "закон Ома для AC", POS),
        (0.90, "груд. 1887", "admittance", "адмітанс", NEG),
    ]
    x0, x1 = ox+20, ox+ax-30
    for i, (t, date, term, ua, col) in enumerate(events):
        xx = x0 + t*(x1-x0)
        up = (i % 2 == 0)
        ty = oy-70 if up else oy+52
        frags.append(line(xx, oy, xx, ty + (28 if up else -16), color=LINE, sw=1.2))
        frags.append(circle(xx, oy, 6, fill=col, stroke=col))
        box = fitbox(xx-78, ty-(0 if up else 0), 156, 46,
                     "%s\n%s — %s" % (date, term, ua),
                     size=12, fill=FILL, stroke=col)
        frags.append(box)

    render(os.path.join(OUT, 'heaviside-timeline.svg'), W, H, *frags)


# ── 5. До і після Штайнмеца: диференціали → алгебра стрілок ──────────────────
def fig_before_after():
    W, H = 800, 340
    frags = []
    frags.append(text(W/2, 30, "Внесок Штайнмеца (AIEE, 1893)", size=17, bold=True))

    bw, bh = 320, 230
    # ліва панель — як було
    lx, ly = 40, 70
    frags.append(rect(lx, ly, bw, bh, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(lx+bw/2, ly+30, "БУЛО: диференціальний аналіз", size=14, bold=True, color=POS))
    frags.append(text(lx+bw/2, ly+72, "v = L · di/dt", size=14))
    frags.append(text(lx+bw/2, ly+100, "тригонометрія фаз", size=13, color=MUTED))
    frags.append(text(lx+bw/2, ly+128, "система рівнянь у часі", size=13, color=MUTED))
    frags.append(text(lx+bw/2, ly+170, "пів сторінки на дільник", size=12, color=MUTED, italic=True))
    frags.append(text(lx+bw/2, ly+198, "ремесло для математика", size=12, color=MUTED, italic=True))

    # стрілка переходу
    mx = lx+bw+20
    frags.append(arrow(mx, ly+bh/2, mx+58, ly+bh/2, color=FIELD, sw=3))
    frags.append(text(mx+30, ly+bh/2-12, "фазор", size=12, bold=True, color=FIELD))

    # права панель — як стало
    rx = mx+78
    frags.append(rect(rx, ly, bw, bh, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(rx+bw/2, ly+30, "СТАЛО: алгебра стрілок", size=14, bold=True, color=NEG))
    frags.append(text(rx+bw/2, ly+72, "V = Z · I", size=14))
    frags.append(text(rx+bw/2, ly+100, "Z = R + jX", size=14))
    frags.append(text(rx+bw/2, ly+128, "звичайна арифметика", size=13, color=MUTED))
    frags.append(text(rx+bw/2, ly+170, "три рядки замість сторінки", size=12, color=MUTED, italic=True))
    frags.append(text(rx+bw/2, ly+198, "доступно кожному інженеру", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'before-after.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_two_parts()
    fig_triangle()
    fig_vs_freq()
    fig_heaviside_timeline()
    fig_before_after()
    print("figures written to", OUT)
