# -*- coding: utf-8 -*-
"""Фігури до статті «Рівняння на ривок і поріг хаосу».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

VC = "#2980b9"   # 1 вимір / швидкість — синє
JC = "#d35400"   # ривок / 3 вимір — гарячий помаранчевий (герой теми)


# ── Драбина вимірів: чому неперервний хаос починається з 3-го ─────────────────
def fig_chaos_dimension_ladder():
    W, H = 1040, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Чому неперервний хаос починається з третього виміру", size=18, bold=True))

    cxs = (185, 520, 855)
    f.append(line(350, 66, 350, 410, color="#dfe4ea", sw=1.2, dash="4,6"))
    f.append(line(690, 66, 690, 410, color="#dfe4ea", sw=1.2, dash="4,6"))

    # 1 вимір: сповзання до нерухомої точки
    cx = cxs[0]
    f.append(textbox(cx, 84, "1 вимір", size=14, pad=7, fill="#eaf0fd",
                     stroke=VC, sw=1.5, color=VC, bold=True)[0])
    y0 = 210
    f.append(line(cx - 118, y0, cx + 118, y0, color=INK, sw=1.8))
    fp = cx + 18
    f.append(circle(fp, y0, 6.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(fp, y0 - 16, "рівновага", size=11.5, color=MUTED))
    for sx in (-96, -58, 92, 54):
        d = -14 if sx > 0 else 14
        f.append(arrow(cx + sx, y0, cx + sx + d, y0, color=INK, sw=2.0))
    f.append(textbox(cx, 302, "точка лише\nсповзає до рівноваги\n— жодних коливань",
                     size=12, pad=9, fill=FILL, stroke=LINE, sw=1.2, color=INK)[0])

    # 2 виміри: граничний цикл
    cx = cxs[1]
    cy = 208
    f.append(textbox(cx, 84, "2 виміри", size=14, pad=7, fill="#e6f5ec",
                     stroke="#1c7a43", sw=1.5, color="#1c7a43", bold=True)[0])
    f.append(line(cx - 108, cy, cx + 108, cy, color=MUTED, sw=1.1))
    f.append(line(cx, cy + 92, cx, cy - 92, color=MUTED, sw=1.1))
    ra, rb = 86, 66
    sp = []
    th = 0.0
    while th <= 7.2 * math.pi:
        k = math.exp(-0.052 * th)
        rr = 1.0 - 0.86 * k
        sp.append("%.1f,%.1f" % (cx + rr * ra * math.cos(th), cy - rr * rb * math.sin(th)))
        th += 0.09
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" opacity="0.7"/>'
             % (" ".join(sp), VC))
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="3"/>'
             % (cx, cy, ra, rb, "#1c7a43"))
    f.append(text(cx, cy + 84, "граничний цикл", size=11.5, color="#1c7a43", bold=True))
    f.append(textbox(cx, 360, "траєкторія замикається\nу петлю — теж без хаосу",
                     size=12, pad=9, fill=FILL, stroke=LINE, sw=1.2, color=INK)[0])

    # 3 виміри: дивний атрактор
    cx = cxs[2]
    cy = 214
    f.append(textbox(cx, 84, "3 виміри", size=14, pad=7, fill="#fdf0e6",
                     stroke=JC, sw=1.5, color=JC, bold=True)[0])
    bx, by, bw, bh = cx - 96, cy - 78, 168, 150
    ddx, ddy = 34, -26
    fr = [(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh)]
    bk = [(x + ddx, y + ddy) for (x, y) in fr]

    def poly(pts, o):
        return ('<polygon points="%s" fill="none" stroke="#c7ccd4" stroke-width="1.2" opacity="%.2f"/>'
                % (" ".join("%.1f,%.1f" % p for p in pts), o))
    f.append(poly(fr, 0.9))
    f.append(poly(bk, 0.55))
    for a_, b_ in zip(fr, bk):
        f.append(line(a_[0], a_[1], b_[0], b_[1], color="#c7ccd4", sw=1.2))

    def lemn(off):
        pts = []
        t = 0.0
        while t <= 2 * math.pi + 0.001:
            den = 1.0 + math.sin(t) ** 2
            X = 78 * math.cos(t) / den
            Y = 58 * math.sin(t) * math.cos(t) / den
            pts.append("%.1f,%.1f" % (cx + X + off[0], cy + Y + off[1]))
            t += 0.03
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), JC)
    f.append(lemn((ddx * 0.5, ddy * 0.5)))
    f.append('<g opacity="0.5">' + lemn((0, 0)) + '</g>')
    f.append(text(cx + 6, cy + 92, "дивний атрактор", size=11.5, color=JC, bold=True))
    f.append(textbox(cx, 360, "траєкторія складається\nсама на себе — хаос",
                     size=12, pad=9, fill=FILL, stroke=LINE, sw=1.2, color=INK)[0])

    return render(os.path.join(IMG, "chaos-dimension-ladder.svg"), W, H, *f)


# ── Найпростіший дисипативний хаотичний потік на ривку (Спротт, 1997) ─────────
def fig_sprott_attractor():
    W, H = 660, 730
    A = 2.017

    def deriv(s):
        x, y, z = s
        return (y, z, -A * z + y * y - x)

    def rk4(s, h):
        k1 = deriv(s)
        k2 = deriv(tuple(s[i] + 0.5 * h * k1[i] for i in range(3)))
        k3 = deriv(tuple(s[i] + 0.5 * h * k2[i] for i in range(3)))
        k4 = deriv(tuple(s[i] + h * k3[i] for i in range(3)))
        return tuple(s[i] + h / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(3))

    s = (0.05, 0.0, 0.0)
    h = 0.01
    for _ in range(8000):
        s = rk4(s, h)
    xs, ys = [], []
    for _ in range(30000):
        s = rk4(s, h)
        xs.append(s[0])
        ys.append(s[1])

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    PL, PT, PW, PH = 74, 92, 512, 496

    def Xx(x):
        return PL + (x - xmin) / (xmax - xmin) * PW

    def Yy(y):
        return PT + PH - (y - ymin) / (ymax - ymin) * PH

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Найпростіший хаотичний потік на ривку (Спротт, 1997)", size=17, bold=True))
    f.append(text(W / 2, 56, "d³x/dt³ = −A·ẍ + ẋ² − x,   A ≈ 2.017", size=13.5, color=JC, bold=True))
    f.append(rect(PL, PT, PW, PH, fill="#fffdfb", stroke="#e4dfda", sw=1.2, rx=4))
    pts = " ".join("%.1f,%.1f" % (Xx(x), Yy(y)) for x, y in zip(xs, ys))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="0.5" opacity="0.75"/>'
             % (pts, JC))
    f.append(text(PL + PW / 2, PT + PH + 26, "x  (положення)", size=12.5, italic=True, color=MUTED))
    f.append(text(PL - 20, PT + PH / 2, "ẋ", size=15, italic=True, color=MUTED, anchor="end"))
    b = textbox(W / 2, 665,
                "Один закон на ривок породжує траєкторію,\n"
                "що ніколи не повторюється. Показники Ляпунова\n"
                "(0.055, 0, −2.072): додатний — розбігання шляхів (хаос),\n"
                "від'ємний — стиск на тонкий атрактор розмірності ≈ 2.03",
                size=11.5, pad=10, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(b)
    return render(os.path.join(IMG, "sprott-attractor.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chaos_dimension_ladder()
    fig_sprott_attractor()
    print("OK: фігури у", IMG)
