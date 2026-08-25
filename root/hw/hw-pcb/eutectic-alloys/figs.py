# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: фазова діаграма Sn-Pb ──────────────────────────────────────────
def fig_phase():
    W, H = 760, 470
    frags = []

    # осі: X — % олова (0..100), Y — температура (°C, 130..340)
    x0, x1 = 90, 690          # ліва/права межа поля даних
    y0, y1 = 410, 70          # низ/верх поля (y росте вниз, тому y0>y1)
    Tmin, Tmax = 130, 340
    Smin, Smax = 0, 100       # % Sn

    def X(sn):  # % олова -> піксель X
        return x0 + (sn - Smin) / (Smax - Smin) * (x1 - x0)
    def Y(T):   # °C -> піксель Y
        return y0 + (T - Tmin) / (Tmax - Tmin) * (y1 - y0)

    # рамка поля
    frags.append(rect(x0, y1, x1 - x0, y0 - y1, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=2))

    # горизонтальні сітки-температури з підписами
    for T in (150, 183, 200, 250, 300):
        yy = Y(T)
        col = POS if T == 183 else "#e6e9ee"
        sw = 1.6 if T == 183 else 1.0
        dash = "5,4" if T == 183 else None
        frags.append(line(x0, yy, x1, yy, color=col, sw=sw, dash=dash))
        frags.append(text(x0 - 8, yy + 4, "%d" % T, size=12, color=(POS if T == 183 else MUTED), anchor="end"))
    # вісь X — підписи складу
    for sn in (0, 20, 40, 60, 63, 80, 100):
        xx = X(sn)
        frags.append(line(xx, y0, xx, y0 + 5, color=MUTED, sw=1.0))
        lbl = "63" if sn == 63 else "%d" % sn
        frags.append(text(xx, y0 + 20, lbl, size=11, color=(FIELD if sn == 63 else MUTED)))
    frags.append(text((x0 + x1) / 2, y0 + 42, "% олова (решта — свинець) →", size=13, color=INK))
    frags.append(text(x0 - 60, (y0 + y1) / 2, "T, °C", size=13, color=INK))

    # координати ключових точок
    Pb_mp, Sn_mp, eut_T, eut_sn = 327.0, 232.0, 183.0, 63.0

    # ЛІКВІДУС: від т.пл. свинцю (0% Sn) вниз до евтектики, тоді вгору до т.пл. олова
    liq = [(0, Pb_mp), (20, 280), (40, 238), (eut_sn, eut_T), (80, 205), (100, Sn_mp)]
    pts = " ".join("%.1f,%.1f" % (X(s), Y(T)) for s, T in liq)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, NEG))

    # СОЛІДУС: горизонталь евтектики на 183 між гілками розчинності + скошені краї
    # ліва межа розчинності Pb(Sn) ~ 19% Sn при евт., права Sn(Pb) ~ 97% Sn
    sol_left, sol_right = 19.0, 97.0
    frags.append(line(X(0), Y(Pb_mp), X(sol_left), Y(eut_T), color=INK, sw=2.0))
    frags.append(line(X(sol_left), Y(eut_T), X(sol_right), Y(eut_T), color=INK, sw=2.0))
    frags.append(line(X(sol_right), Y(eut_T), X(100), Y(Sn_mp), color=INK, sw=2.0))

    # евтектична точка
    ex, ey = X(eut_sn), Y(eut_T)
    frags.append(circle(ex, ey, 6, fill=FIELD, stroke=INK, sw=1.4))
    b, bw, bh = textbox(ex + 8, ey - 42, "евтектика\n63/37 · 183 °C", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    # позначки чистих металів
    frags.append(circle(X(0), Y(Pb_mp), 4, fill=NEG, stroke=INK, sw=1.0))
    frags.append(text(X(0) + 6, Y(Pb_mp) - 8, "Pb 327 °C", size=11, color=INK, anchor="start"))
    frags.append(circle(X(100), Y(Sn_mp), 4, fill=NEG, stroke=INK, sw=1.0))
    frags.append(text(X(100) - 6, Y(Sn_mp) - 8, "Sn 232 °C", size=11, color=INK, anchor="end"))

    # підписи областей фаз (кашоподібні — ЛІВОРУЧ від демо-лінії x=40%, щоб та не різала напис)
    frags.append(text(X(50), Y(320), "РІДИНА (розплав)", size=13, color=NEG, bold=True))
    frags.append(text(X(26), Y(206), "рідина + кристали", size=11, color=MUTED, anchor="end"))
    frags.append(text(X(26), Y(193), "(кашоподібна зона)", size=11, color=MUTED, anchor="end"))
    frags.append(text(X(50), Y(158), "ТВЕРДА суміш", size=13, color=INK, bold=True))

    # позначити «діапазон плавлення» для 40% Sn: вертикальний відрізок від солідуса(183) до лідуса
    sn_demo = 40.0
    yliq_demo = Y(238)   # лідус при 40% (з масиву вище)
    ysol_demo = Y(eut_T)
    frags.append(line(X(sn_demo), ysol_demo, X(sn_demo), yliq_demo, color=POS, sw=2.4, dash="3,3"))
    frags.append(circle(X(sn_demo), yliq_demo, 4, fill=POS, stroke=INK, sw=1.0))
    frags.append(circle(X(sn_demo), ysol_demo, 4, fill=POS, stroke=INK, sw=1.0))

    # легенда ліній
    frags.append(line(x0 + 470, y1 + 18, x0 + 500, y1 + 18, color=NEG, sw=2.4))
    frags.append(text(x0 + 506, y1 + 22, "лідус", size=11, color=INK, anchor="start"))
    frags.append(line(x0 + 470, y1 + 36, x0 + 500, y1 + 36, color=INK, sw=2.0))
    frags.append(text(x0 + 506, y1 + 40, "солідус", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'phase.svg'), W, H, *frags,
           title="Фазова діаграма олово-свинець")


# ── Фігура 2: криві застигання — евтектика проти суміші ─────────────────────
def fig_cooling():
    W, H = 720, 380
    frags = []
    x0, x1 = 90, 660
    y0, y1 = 320, 70
    Tmin, Tmax = 150, 320
    tmin, tmax = 0, 100  # умовний час

    def X(t): return x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)
    def Y(T): return y0 + (T - Tmin) / (Tmax - Tmin) * (y1 - y0)

    frags.append(rect(x0, y1, x1 - x0, y0 - y1, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=2))
    for T in (183, 200, 250, 300):
        yy = Y(T)
        col = POS if T == 183 else "#e6e9ee"
        frags.append(line(x0, yy, x1, yy, color=col, sw=(1.4 if T == 183 else 1.0),
                          dash=("5,4" if T == 183 else None)))
        frags.append(text(x0 - 8, yy + 4, "%d" % T, size=11,
                          color=(POS if T == 183 else MUTED), anchor="end"))
    frags.append(text((x0 + x1) / 2, y0 + 34, "час охолодження →", size=12, color=INK))
    frags.append(text(x0 - 58, (y0 + y1) / 2, "T, °C", size=12, color=INK))

    # ЕВТЕКТИКА: спад до 183, різка ПЛОЩАДКА, далі спад — як чистий метал
    eut = [(0, 300), (32, 183), (60, 183), (100, 165)]
    pts = " ".join("%.1f,%.1f" % (X(t), Y(T)) for t, T in eut)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, FIELD))
    frags.append(text(X(46), Y(183) - 10, "площадка — застигає ОДРАЗУ", size=11, color=FIELD, bold=True))
    # ідентифікатор кривої — у порожній смузі між 250 і 200 °C ліворуч (жодна гілка/сітка не ріже)
    b, bw, bh = textbox(X(11), Y(222), "63/37\nевтектика", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD)
    frags.append(b)

    # НЕЕВТЕКТИКА (напр. 40/60): злам на лідусі, ПОХИЛА ділянка (каша), тоді площадка на 183
    non = [(0, 300), (24, 238), (58, 183), (72, 183), (100, 165)]
    pts2 = " ".join("%.1f,%.1f" % (X(t), Y(T)) for t, T in non)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6,4"/>' % (pts2, POS))
    # позначити похилу кашоподібну ділянку
    frags.append(circle(X(24), Y(238), 4, fill=POS, stroke=INK, sw=1.0))
    frags.append(text(X(24) + 6, Y(238) - 6, "лідус: почалась каша", size=11, color=POS, anchor="start"))
    frags.append(circle(X(58), Y(183), 4, fill=POS, stroke=INK, sw=1.0))
    frags.append(text(X(58) + 8, Y(183) + 26, "солідус: тільки тут тверда", size=11, color=POS, anchor="start"))
    b2, bw2, bh2 = textbox(X(89), Y(222), "неевтектика\nдіапазон", size=12, bold=True,
                           fill="#fdecea", stroke=POS)
    frags.append(b2)

    render(os.path.join(IMG, 'cooling.svg'), W, H, *frags,
           title="Криві застигання: евтектика проти суміші")


if __name__ == "__main__":
    fig_phase()
    fig_cooling()
    print("figs done")
