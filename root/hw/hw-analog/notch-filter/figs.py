# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Що таке режекторна характеристика: вузький провал ─────────────────────
def fig_concept():
    W, H = 760, 330
    x0, y0, x1, y1 = 95, 70, 700, 250            # рамка осей
    f0x = (x0 + x1) / 2                            # центр провалу по осі
    base = y0 + 10                                 # рівень «1» (полиця)
    bot = y1                                       # дно провалу

    def curve():
        pts = []
        N = 240
        for i in range(N + 1):
            u = i / N                              # 0..1 уздовж осі (лог-частота)
            d = (u - 0.5)
            k = 1.0 - math.exp(-(d * d) / (2 * 0.0016))   # гострий провал майже до 0
            yy = base + (bot - base) * (1 - k)
            pts.append((x0 + u * (x1 - x0), yy))
        return pts

    poly = " ".join("%.1f,%.1f" % p for p in curve())

    frags = [
        line(x0, base, x1, base, color=MUTED, sw=1, dash="4 4"),
        line(x0, y0, x0, y1, color=INK, sw=1.5),
        line(x0, y1, x1, y1, color=INK, sw=1.5),
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, POS),
        line(f0x, y0, f0x, y1, color=MUTED, sw=1, dash="3 4"),
        text(f0x, y1 + 20, "f₀", size=15, bold=True),
        text(f0x, y1 + 38, "(частота-ціль)", size=11, color=MUTED),
        text(x0 - 8, base + 4, "1", size=13, anchor="end"),
        text(x0 - 8, bot - 2, "0", size=13, anchor="end"),
        text(x0 - 58, (y0 + y1) / 2, "K", size=15, bold=True),
        text(x0 + 70, base - 8, "пропускає", size=12, color=FIELD, anchor="middle"),
        text(x1 - 70, base - 8, "пропускає", size=12, color=FIELD, anchor="middle"),
        text(f0x, base - 6, "ріже саме тут", size=12, color=POS),
        text((x0 + x1) / 2, H - 8, "частота (лог)", size=12, color=MUTED),
    ]
    render(os.path.join(IMG, 'concept.svg'), W, H, *frags,
           title="Режекторний фільтр: вузький провал на одній частоті")


# ── 2. Twin-T: дві гілки T, що гасять одна одну на f0 ────────────────────────
def fig_twint():
    W, H = 760, 360
    xin, xout = 110, 600
    yT1 = 110                                      # верхній T — R-C-R (повільний шлях)
    yT2 = 250                                      # нижній T — C-R-C (швидкий шлях)
    xa, xb = 250, 460                              # вузли всередині T
    yg = 320                                       # земляна шина
    midu = (xa + xb) / 2

    def node(x, y):
        return circle(x, y, 4, fill=INK, stroke=INK)

    frags = []
    # вхід / вихід — спільні стовпи
    frags += [text(xin, 70, "вхід", size=12, color=MUTED),
              text(xout, 70, "вихід", size=12, color=MUTED),
              line(xin, 90, xin, yT2, color=INK, sw=1.5),
              line(xout, 90, xout, yT2, color=INK, sw=1.5)]

    # ── верхній T: R — (шунт 2C) — R
    frags += [
        line(xin, yT1, xa, yT1, color=INK, sw=2),
        line(xb, yT1, xout, yT1, color=INK, sw=2),
        text((xin + xa) / 2, yT1 - 10, "R", size=14, bold=True, color=NEG),
        text((xb + xout) / 2, yT1 - 10, "R", size=14, bold=True, color=NEG),
        node(xa, yT1), node(xb, yT1),
        line(xa, yT1, xb, yT1, color=INK, sw=2),
        node(midu, yT1),
        line(midu, yT1, midu, (yT1 + yg) / 2, color=INK, sw=2),
        text(midu + 18, (yT1 + yg) / 2 - 4, "2C", size=13, bold=True, color=POS),
        text((xin + xa) / 2, yT1 + 20, "R-C-R", size=11, color=MUTED),
    ]

    # ── нижній T: C — (шунт R/2) — C
    frags += [
        line(xin, yT2, xa, yT2, color=INK, sw=2),
        line(xb, yT2, xout, yT2, color=INK, sw=2),
        line(xa, yT2, xb, yT2, color=INK, sw=2),
        text((xin + xa) / 2, yT2 - 10, "C", size=14, bold=True, color=POS),
        text((xb + xout) / 2, yT2 - 10, "C", size=14, bold=True, color=POS),
        node(xa, yT2), node(xb, yT2), node(midu, yT2),
        line(midu, yT2, midu, yg, color=INK, sw=2),
        text(midu + 20, (yT2 + yg) / 2 + 4, "R/2", size=13, bold=True, color=NEG),
        text((xin + xa) / 2, yT2 + 20, "C-R-C", size=11, color=MUTED),
    ]

    # земляна шина + з'єднання шунтів
    frags += [line(midu, (yT1 + yg) / 2, midu, yT2, color=INK, sw=2),
              line(xa, yg, xb, yg, color=INK, sw=2)]

    # символ землі
    gx = midu
    frags += [line(gx, yg, gx, yg + 12, color=INK, sw=2),
              line(gx - 14, yg + 12, gx + 14, yg + 12, color=INK, sw=2),
              line(gx - 9, yg + 17, gx + 9, yg + 17, color=INK, sw=1.6),
              line(gx - 4, yg + 22, gx + 4, yg + 22, color=INK, sw=1.4)]

    # підписи-ролі гілок праворуч
    frags += [mtext(xout + 70, yT1 - 4, ["верхня гілка:", "пропускає низькі"],
                    size=10, color=MUTED),
              mtext(xout + 70, yT2 - 4, ["нижня гілка:", "пропускає високі"],
                    size=10, color=MUTED)]

    box, bw, bh = textbox(W / 2, 50,
                          "На f₀ виходи двох гілок рівні й протифазні → на виході гаснуть",
                          size=12, fill="#fff7f5", stroke=POS)
    frags = [box] + frags
    render(os.path.join(IMG, 'twint.svg'), W, H, *frags,
           title="Подвійний T (twin-T): гілка низьких + гілка високих у протифазі")


# ── 3. Глибина й ширина: Q керує гостротою провалу ───────────────────────────
def fig_q():
    W, H = 760, 340
    x0, y0, x1, y1 = 95, 70, 700, 270
    base = y0 + 12
    bot = y1
    f0x = (x0 + x1) / 2

    def curve(width):
        pts = []
        N = 240
        sig2 = 2 * width * width
        for i in range(N + 1):
            u = i / N
            d = u - 0.5
            k = math.exp(-(d * d) / sig2)
            yy = base + (bot - base) * k
            pts.append((x0 + u * (x1 - x0), yy))
        return " ".join("%.1f,%.1f" % p for p in pts)

    frags = [
        line(x0, base, x1, base, color=MUTED, sw=1, dash="4 4"),
        line(x0, y0, x0, y1, color=INK, sw=1.5),
        line(x0, y1, x1, y1, color=INK, sw=1.5),
        line(f0x, y0, f0x, y1, color=MUTED, sw=1, dash="3 4"),
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (curve(0.085), NEG),
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (curve(0.022), POS),
        text(f0x, y1 + 20, "f₀", size=14, bold=True),
        text(x0 - 8, base + 4, "1", size=13, anchor="end"),
        text(x0 - 8, bot - 2, "0", size=13, anchor="end"),
        text(x1 - 6, base - 26, "вузький, високе Q", size=12, color=POS, anchor="end"),
        text(x1 - 6, base - 10, "широкий, низьке Q", size=12, color=NEG, anchor="end"),
        text((x0 + x1) / 2, H - 8, "частота (лог)", size=12, color=MUTED),
    ]
    render(os.path.join(IMG, 'q.svg'), W, H, *frags,
           title="Та сама f₀, різна добротність: ширина провалу = f₀ / Q")


# ── 4. Дві гілки: модулі ФНЧ і ФВЧ перетинаються на f0 (math-insert) ─────────
def fig_branches():
    W, H = 760, 360
    x0, y0, x1, y1 = 95, 70, 690, 280
    base = y0 + 6                                  # рівень «повної передачі» гілки
    bot = y1
    f0x = (x0 + x1) / 2

    # модуль першого порядку: ФНЧ ~ 1/√(1+(f/fc)²), ФВЧ ~ (f/fc)/√(1+(f/fc)²)
    # для наочності беремо однопорядкові форми, що перетинаються на середині
    def lp_curve():
        pts = []
        N = 240
        for i in range(N + 1):
            u = i / N
            r = math.exp((u - 0.5) * 6)            # f/fc у лог-розгортці
            m = 1.0 / math.sqrt(1 + r * r)
            pts.append((x0 + u * (x1 - x0), base + (bot - base) * (1 - m)))
        return " ".join("%.1f,%.1f" % p for p in pts)

    def hp_curve():
        pts = []
        N = 240
        for i in range(N + 1):
            u = i / N
            r = math.exp((u - 0.5) * 6)
            m = r / math.sqrt(1 + r * r)
            pts.append((x0 + u * (x1 - x0), base + (bot - base) * (1 - m)))
        return " ".join("%.1f,%.1f" % p for p in pts)

    cross_y = base + (bot - base) * (1 - 1 / math.sqrt(2))   # 0.707 на f0

    frags = [
        line(x0, base, x1, base, color=MUTED, sw=1, dash="4 4"),
        line(x0, y0, x0, y1, color=INK, sw=1.5),
        line(x0, y1, x1, y1, color=INK, sw=1.5),
        line(f0x, y0, f0x, y1, color=MUTED, sw=1, dash="3 4"),
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (lp_curve(), NEG),
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (hp_curve(), POS),
        circle(f0x, cross_y, 5, fill=FIELD, stroke=FIELD),
        text(f0x + 8, cross_y - 8, "рівні тут", size=12, color=FIELD, anchor="start"),
        text(f0x, y1 + 20, "f₀", size=14, bold=True),
        text(x0 - 8, base + 4, "1", size=13, anchor="end"),
        text(x0 - 8, bot - 2, "0", size=13, anchor="end"),
        text(x0 + 60, base + 26, "ФНЧ (R-C-R)", size=12, color=NEG, anchor="start"),
        text(x1 - 6, base + 26, "ФВЧ (C-R-C)", size=12, color=POS, anchor="end"),
        text((x0 + x1) / 2, H - 8, "частота (лог)", size=12, color=MUTED),
    ]
    render(os.path.join(IMG, 'branches.svg'), W, H, *frags,
           title="Модулі двох гілок перетинаються рівно на f₀")


# ── 5. Фазори двох внесків на f0: рівні, протифазні → сума нуль ───────────────
def fig_phasor():
    W, H = 760, 320
    cx, cy = W / 2, 175
    L = 150                                        # довжина фазора

    frags = []
    # осі
    frags += [line(cx - L - 30, cy, cx + L + 30, cy, color=MUTED, sw=1, dash="3 4"),
              line(cx, cy - 120, cx, cy + 120, color=MUTED, sw=1, dash="3 4"),
              text(cx + L + 36, cy + 4, "Re", size=12, color=MUTED, anchor="start"),
              text(cx + 6, cy - 120, "Im", size=12, color=MUTED, anchor="start")]
    # внесок ФНЧ — праворуч (умовно «+»), підпис біля свого вістря
    frags += [arrow(cx, cy, cx + L, cy, color=NEG, sw=2.6),
              text(cx + L - 4, cy - 14, "внесок гілки ФНЧ", size=13, bold=True, color=NEG, anchor="end")]
    # внесок ФВЧ — ліворуч, рівний за модулем, протилежний
    frags += [arrow(cx, cy, cx - L, cy, color=POS, sw=2.6),
              text(cx - L + 4, cy - 14, "внесок гілки ФВЧ", size=13, bold=True, color=POS, anchor="start")]
    # дуга-позначка 180°
    frags += [text(cx, cy + 90, "180° між ними → однакові за модулем, протилежні за знаком",
                   size=12, color=INK),
              text(cx, cy + 112, "H_ФНЧ(f₀) + H_ФВЧ(f₀) = 0", size=14, bold=True, color=FIELD)]
    render(os.path.join(IMG, 'phasor.svg'), W, H, *frags,
           title="На f₀ два фазори рівні й протилежні — сума гасне в нуль")


# ── 6. Історія: від вимірювального нуля до викидача гулу (hist-insert) ────────
def fig_history():
    W, H = 880, 380
    xL, xR = 165, 715                              # межі осі часу (з полем під крайні картки)
    ymain = 250                                     # лінія часу
    yr0, yr1 = 1936, 1940                           # роки-якорі (рік -> x)

    def X(year):
        return xL + (year - yr0) / (yr1 - yr0) * (xR - xL)

    frags = []
    # вісь часу з рисками-роками
    frags += [line(xL, ymain, xR, ymain, color=INK, sw=2)]
    for y in (1936, 1937, 1938, 1939, 1940):
        x = X(y)
        frags += [line(x, ymain - 5, x, ymain + 5, color=INK, sw=1.5),
                  text(x, ymain + 22, str(y), size=12, color=MUTED)]

    # три віхи-картки над лінією, кожна на своєму році
    def milestone(year, dy, title, who, accent):
        x = X(year)
        box, bw, bh = textbox(x, ymain - dy, title, size=11, bold=True,
                              fill="#ffffff", stroke=accent, color=INK, pad=7)
        stem = line(x, ymain, x, ymain - dy + bh / 2, color=accent, sw=1.5, dash="2 3")
        dot = circle(x, ymain, 4.5, fill=accent, stroke=accent)
        sub = text(x, ymain - dy + bh / 2 + 15, who, size=10, color=MUTED)
        return [stem, box, dot, sub]

    frags += milestone(1936, 175, "Патент Augustadt\n(подано 1936, видано 1938)",
                       "Bell Labs · викидач гулу", POS)
    frags += milestone(1938, 100, "Стаття й патент Scott\n(IRE 1938, патент 1939)",
                       "General Radio · нуль у ЗЗ", NEG)
    frags += milestone(1940, 175, "Огляд Tuttle (IRE 28)\nнуль-кола радіочастот",
                       "General Radio · вимір без транса", FIELD)

    # підпис-нитка під віссю
    box2, bw2, bh2 = textbox(W / 2, 330,
        "Один нуль на f₀ — і вимірювальний баланс, і чистий генератор, і зарубка проти мережі",
        size=12, fill="#f4f6f8", stroke=MUTED)
    frags = [box2] + frags

    render(os.path.join(IMG, 'history.svg'), W, H, *frags,
           title="Подвійне T: один нуль — три застосування за п'ять років")


if __name__ == "__main__":
    fig_concept()
    fig_twint()
    fig_q()
    fig_branches()
    fig_phasor()
    fig_history()
    print("figs OK")
