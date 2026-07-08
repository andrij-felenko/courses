# -*- coding: utf-8 -*-
# Фігури до вставки math-c-rate.md (окремий генератор, щоб не колідувати з figs.py).
# Вивід — у ту саму ./img теки теми.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# math-fig 1: I·t = const — гіпербола «струм ↔ час роботи».
# Той самий заряд 2.2 А·год розтягується або стискається в часі залежно від струму.
# ─────────────────────────────────────────────────────────────────────────────
def fig_runtime():
    W, H = 900, 560
    frags = []
    frags.append(text(W / 2, 34, "Один заряд 2.2 А·год: більший струм — коротший час  (I · t = const)",
                      size=16, bold=True))

    ox, oy = 130, 452          # початок осей (низ-ліво)
    plot_w, plot_h = 640, 360
    Imax = 70.0                # ампери по X
    Tmax = 3.5                 # години по Y

    def sx(i):  return ox + i / Imax * plot_w
    def sy(t):  return oy - t / Tmax * plot_h

    # горизонтальні напрямні (по часу) — лише вони суцільні, короткі стуби по струму
    for t in range(0, 4):
        y = sy(t)
        frags.append(line(ox, y, ox + plot_w, y, color="#e9ecf2", sw=1))
        frags.append(text(ox - 16, y + 5, "%d" % t, size=12, color=MUTED, anchor="end"))
    for t in (0.5, 1.5, 2.5):
        frags.append(text(ox - 16, sy(t) + 5, "%.1f" % t, size=11, color="#aab0bb", anchor="end"))
    # струм — короткі позначки під віссю (щоб жодна вертикаль не тяглася крізь написи)
    for i in range(0, int(Imax) + 1, 10):
        x = sx(i)
        frags.append(line(x, oy, x, oy + 6, color=MUTED, sw=1))
        frags.append(text(x, oy + 22, str(i), size=12, color=MUTED))

    frags.append(line(ox, oy, ox + plot_w, oy, color=INK, sw=2))          # X
    frags.append(line(ox, oy, ox, oy - plot_h, color=INK, sw=2))          # Y
    frags.append(text(ox + plot_w / 2, oy + 46, "струм навантаження, А", size=13, color=INK))
    frags.append(text(ox - 96, oy - plot_h / 2, "час роботи, год", size=13, color=INK))

    # сама гіпербола t = 2.2 / I
    Q = 2.2
    pts = []
    i = Q / Tmax           # від струму, де t=Tmax (щоб не летіти в нескінченність)
    while i <= Imax:
        pts.append("%.1f,%.1f" % (sx(i), sy(Q / i)))
        i += 0.25
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (" ".join(pts), NEG))

    # три робочі точки (написи в чистих зонах між напрямними, не на кривій)
    def dot(i, note, lx, ly, col, anchor):
        x, y = sx(i), sy(Q / i)
        out = circle(x, y, 6, fill=col, stroke=BG, sw=2)
        out += text(lx, ly, note, size=12.5, color=col, bold=True, anchor=anchor)
        return out
    frags.append(dot(2.2, "2.2 А → 1.0 год", sx(2.2) + 16, sy(1.0) - 16, FIELD, "start"))  # 1C
    frags.append(dot(11.0, "11 А → 12 хв", sx(11.0) + 16, sy(0.2) - 60, NEG, "start"))     # ~5C
    frags.append(dot(44.0, "44 А → 3 хв", sx(44.0) - 14, 300, POS, "end"))                 # 20C

    # підпис-формула у вільному верхньому куті (над напрямними — жодна лінія туди не сягає)
    box, bw, bh = textbox(ox + plot_w - 132, 70,
                          ["площа під точкою стала:", "струм × час = 2.2 А·год"],
                          size=12.5, fill="#eef2fe", stroke=NEG, sw=1.5, pad=10)
    frags.append(box)

    render(os.path.join(IMG, 'runtime.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# math-fig 2: просідання напруги — V(I) = V_хх − I·R (навантажувальна пряма).
# ─────────────────────────────────────────────────────────────────────────────
def fig_sag():
    W, H = 900, 560
    frags = []
    frags.append(text(W / 2, 34, "Напруга під струмом просідає прямо:  V = V_хх − I · R_внутр",
                      size=16, bold=True))

    ox, oy = 130, 452
    plot_w, plot_h = 620, 358
    Imax = 66.0
    Vtop = 13.0            # верх шкали напруги
    Vbot = 8.8            # низ шкали (трохи нижче порога 9.0, щоб поріг був видимий над віссю)

    def sx(i):  return ox + i / Imax * plot_w
    def sy(v):  return oy - (v - Vbot) / (Vtop - Vbot) * plot_h

    # горизонтальні напрямні (по напрузі) — суцільні; струм — короткі стуби під віссю
    for v in range(9, 14):
        y = sy(v)
        frags.append(line(ox, y, ox + plot_w, y, color="#e9ecf2", sw=1))
        frags.append(text(ox - 14, y + 5, "%d" % v, size=12, color=MUTED, anchor="end"))
    for i in range(0, int(Imax) + 1, 10):
        x = sx(i)
        frags.append(line(x, oy, x, oy + 6, color=MUTED, sw=1))
        frags.append(text(x, oy + 22, str(i), size=12, color=MUTED))

    frags.append(line(ox, oy, ox + plot_w, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - plot_h, color=INK, sw=2))
    frags.append(text(ox + plot_w / 2, oy + 46, "струм навантаження, А", size=13, color=INK))
    frags.append(text(ox - 96, oy - plot_h / 2, "напруга на клемах, В", size=13, color=INK))

    # нижній поріг 9.0 В (червона стіна) — над віссю
    yb = sy(9.0)
    frags.append(line(ox, yb, ox + plot_w, yb, color=POS, sw=2, dash="6 4"))
    frags.append(text(ox + plot_w - 6, yb - 9, "нижній поріг 9.0 В", size=11.5,
                      color=POS, anchor="end"))

    # навантажувальна пряма V = 12.6 − I·R, R = 0.030 Ом
    Vhh = 12.6
    R = 0.030
    x0, y0 = sx(0), sy(Vhh)
    xE, yE = sx(Imax), sy(Vhh - Imax * R)
    frags.append(line(x0, y0, xE, yE, color=NEG, sw=3))
    frags.append(circle(x0, y0, 6, fill=NEG, stroke=BG, sw=2))
    frags.append(text(x0 + 14, y0 - 12, "12.6 В — холостий хід (I = 0)", size=12.5,
                      color=NEG, bold=True, anchor="start"))

    # робоча точка 40 А
    Iw = 40.0
    Vw = Vhh - Iw * R
    xw, yw = sx(Iw), sy(Vw)
    frags.append(line(xw, oy, xw, yw, color=MUTED, sw=1, dash="3 3"))
    frags.append(line(ox, yw, xw, yw, color=MUTED, sw=1, dash="3 3"))
    frags.append(circle(xw, yw, 6, fill=POS, stroke=BG, sw=2))
    frags.append(text(xw + 14, yw + 5, "40 А → 11.4 В", size=12.5, color=POS, bold=True,
                      anchor="start"))

    # просвіт I·R між рівнем V_хх і прямою при 40 А (напис у чистій смузі, не на напрямній)
    y_hh_at = sy(Vhh)
    frags.append(line(xw + 62, y_hh_at, xw + 62, yw, color=POS, sw=1.5))
    frags.append(line(xw + 58, y_hh_at, xw + 66, y_hh_at, color=POS, sw=1.5))
    frags.append(line(xw + 58, yw, xw + 66, yw, color=POS, sw=1.5))
    frags.append(text(xw + 72, sy(12.2), "втрата", size=11.5, color=POS, anchor="start"))
    frags.append(text(xw + 72, sy(12.0), "I·R = 1.2 В", size=11.5, color=POS, anchor="start"))

    # параметри прикладу — верхній правий кут, над навантажувальною прямою
    box, bw, bh = textbox(ox + plot_w - 118, 122,
                          ["R_внутр ≈ 30 мОм", "нахил прямої = −R"],
                          size=12, fill="#fdeeee", stroke=POS, sw=1.5, pad=9)
    frags.append(box)

    render(os.path.join(IMG, 'sag.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# math-fig 3: чесна віддача — надрукований C проти реальних ~65% і твій струм.
# ─────────────────────────────────────────────────────────────────────────────
def fig_derate():
    W, H = 900, 430
    frags = []
    frags.append(text(W / 2, 34, "Чесна віддача — 60–70 % від напису: рахуй свій струм від неї",
                      size=16, bold=True))

    ox = 250                 # ліва межа смуг (праворуч від підписів)
    right = 850
    Amax = 70.0
    def bx(a):  return ox + a / Amax * (right - ox)

    rows = [
        ("Напис 30C × 2.2 А·год", 66.0, "#c9d4f0", NEG,   "= 66 А (обіцянка)"),
        ("Чесно ≈ 65 %",          43.0, "#f6d9d9", POS,   "≈ 43 А (на це рахуй)"),
        ("Твій струм на газі",    28.0, "#cdeccd", FIELD, "28 А — влазить із запасом"),
    ]
    y0 = 96
    bh = 54
    gap = 32
    y_bottom = y0 + 3 * (bh + gap) - gap

    # шкала зверху — лише короткі стуби над смугами (жодної вертикалі крізь написи)
    frags.append(line(ox, y0 - 12, right, y0 - 12, color="#d7dbe3", sw=1))
    for a in range(0, int(Amax) + 1, 10):
        x = bx(a)
        frags.append(line(x, y0 - 16, x, y0 - 8, color=MUTED, sw=1))
        frags.append(text(x, y0 - 22, str(a), size=11, color=MUTED))
    frags.append(text(bx(35), y0 - 44, "струм, А", size=12.5, color=INK))

    y = y0
    for label, amps, fill, edge, note in rows:
        frags.append(text(ox - 18, y + bh / 2 + 5, label, size=13, color=INK,
                          anchor="end", bold=True))
        frags.append(rect(ox, y, bx(amps) - ox, bh, fill=fill, stroke=edge, sw=2))
        frags.append(text(bx(amps) + 12, y + bh / 2 + 5, note, size=12, color=edge,
                          anchor="start", bold=True))
        y += bh + gap

    # вертикальна риска «чесної стелі» через усі смуги
    xh = bx(43.0)
    frags.append(line(xh, y0 - 6, xh, y_bottom + 6, color=POS, sw=1.5, dash="5 4"))

    frags.append(text(W / 2, H - 22,
                      "Запас між зеленою смугою і червоною рискою — те, що тримає пакет прохолодним.",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'derate.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_runtime()
    fig_sag()
    fig_derate()
    print("ok")
