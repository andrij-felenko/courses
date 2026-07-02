# -*- coding: utf-8 -*-
"""Фігури до вставки «math-rlc-spike.md» (тема «Захист flyback»).

Кут вставки: неприборканий сплеск — це НЕ просто «висока напруга», а
перехідний процес RLC-контуру другого порядку. Дві фігури несуть те,
що словами передати важко:

  rlc-regimes.svg  — три режими напруги v(t) на паразитній ємності:
                     недо-/критично-/перезагашений; видно перший пік,
                     нижчий за ідеальний I₀·√(L/C), і дзвін після нього.
  peak-vs-zeta.svg — наскільки перший пік нижчий за ідеал залежно від ζ
                     (і дзеркальної Q): крива V_peak/(I₀·√(L/C)) та де
                     на ній сидить RC-снабер.

Окремий генератор поряд із figs.py статті-власника; спільний вивід ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), "img")


# ── 1. Три режими напруги на паразитній ємності ─────────────────────────────
def fig_rlc_regimes():
    """Усі три криві — з ОДНІЄЇ початкової умови (той самий I₀, L, C; різне R).
    Спільна шкала: пунктир = ідеал I₀·√(L/C). Видно, що недозагашений пік
    найвищий (майже ідеал) і дзвенить, критичний — один нижчий горб,
    перезагашений — ще нижчий і найповільніший. Форми — точні розв'язки."""
    W, H = 720, 430
    ox, oy = 84, 250          # нуль напруги
    pw = 566
    f = []
    f.append(text(W/2, 26, "Три режими сплеску: напруга v(t) на паразитній ємності", size=17, bold=True))

    # осі
    f.append(line(ox, oy, ox+pw, oy, color=INK, sw=2))            # вісь часу (нуль напруги)
    f.append(line(ox, 78, ox, oy+120, color=INK, sw=2))           # вісь v
    f.append(text(ox+pw-4, oy+26, "час →", size=13, color=INK, anchor="end"))
    f.append(text(ox-10, 82, "v", size=13, color=INK, anchor="end"))

    # рівень ідеалу
    ideal_y = 96
    amp = oy - ideal_y                      # px на одиницю (безрозм. напруги = 1)
    f.append(line(ox, ideal_y, ox+pw, ideal_y, color=MUTED, sw=1.2, dash="5,4"))
    f.append(text(ox+pw-4, ideal_y-8, "ідеал  I₀·√(L/C)  (без утрат)", size=12, color=MUTED, anchor="end"))

    # спільна шкала часу: ω0·t від 0 до Tmax (безрозмірний час)
    Tmax = 22.0                             # стільки ω0·t уміщаємо
    def tt(px): return Tmax * px / pw       # ω0·t для піксельного px

    def vfun(z, wt):
        # v(t)/(I0·√(L/C)) для послідовного RLC із поч. струмом I₀, v(0)=0:
        #   underdamped: (1/√(1-z²))·e^{-z·wt}·sin(√(1-z²)·wt)
        #   critical:    wt·e^{-wt}·... нормуємо на пік → множник e (пік=1)? Ні:
        #                точна форма v/(I0Z0)= wt·e^{-wt} (пік при wt=1 → e^{-1}=0.368)
        #   overdamped:  (1/(2√(z²-1)))·(e^{-(z-√)wt} − e^{-(z+√)wt})
        if z < 1 - 1e-9:
            s = math.sqrt(1-z*z)
            return (1/s)*math.exp(-z*wt)*math.sin(s*wt)
        elif abs(z-1) < 1e-9:
            return wt*math.exp(-wt)
        else:
            s = math.sqrt(z*z-1)
            return (1/(2*s))*(math.exp(-(z-s)*wt) - math.exp(-(z+s)*wt))

    def curve(z, color, sw):
        pts = []
        for px in range(0, pw+1, 2):
            y = oy - amp * vfun(z, tt(px))
            pts.append("%.1f,%.1f" % (ox+px, y))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), color, sw))

    zU = 0.12
    f.append(curve(3.0, FIELD, 2.2))       # перезагашений
    f.append(curve(1.0, INK, 2.2))         # критичний
    f.append(curve(zU, POS, 2.6))          # недозагашений

    # перший пік недозагашеного
    s = math.sqrt(1-zU*zU); wt_pk = math.atan(s/zU)/s
    vpk = vfun(zU, wt_pk)
    xpk, ypk = ox + pw*wt_pk/Tmax, oy - amp*vpk
    f.append(circle(xpk, ypk, 4, fill=POS, stroke=INK, sw=1.2))
    f.append(line(xpk, ypk, xpk, ideal_y, color=POS, sw=1, dash="2,3"))
    f.append(text(xpk+8, ypk+4, "перший пік < ідеал", size=12, color=POS, anchor="start"))

    # дзвін — стрілка на перший (від'ємний) горб; підпис ліворуч під ним
    wt_min = (math.pi + math.atan(s/zU))/s
    x2, y2 = ox+pw*wt_min/Tmax, oy - amp*vfun(zU, wt_min)
    f.append(text(ox+pw*0.34, oy+108, "дзвін після піка — теж гасити (RC-снабер)",
                  size=12, color=POS, anchor="middle", italic=True))
    f.append(arrow(ox+pw*0.34, oy+94, x2, y2+6, color=POS, sw=1.4))

    # позначка критичного горба
    f.append(text(ox+pw*1.0/Tmax+12, oy-amp*vfun(1.0,1.0)-6, "критичний: один горб", size=11, color=INK, anchor="start"))

    # легенда (верх праворуч, нижче лінії ідеалу, поза кривими)
    lx, ly = ox+pw-208, ideal_y+34
    f.append(line(lx, ly, lx+24, ly, color=POS, sw=2.6)); f.append(text(lx+30, ly+4, "недозагашений ζ<1", size=12, color=POS, anchor="start"))
    f.append(line(lx, ly+19, lx+24, ly+19, color=INK, sw=2.2)); f.append(text(lx+30, ly+23, "критичний ζ=1", size=12, color=INK, anchor="start"))
    f.append(line(lx, ly+38, lx+24, ly+38, color=FIELD, sw=2.2)); f.append(text(lx+30, ly+42, "перезагашений ζ>1", size=12, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "rlc-regimes.svg"), W, H, *f)


# ── 2. Наскільки перший пік нижчий за ідеал залежно від ζ ────────────────────
def fig_peak_vs_zeta():
    W, H = 720, 420
    ox, oy = 92, 330
    pw, ph = 558, 262
    f = []
    f.append(text(W/2, 26, "Перший пік проти ідеалу: залежність від загасання", size=17, bold=True))

    f.append(line(ox, oy, ox+pw, oy, color=INK, sw=2))
    f.append(line(ox, oy, ox, oy-ph, color=INK, sw=2))
    f.append(text(ox+pw/2, oy+34, "коефіцієнт загасання  ζ  →", size=13, color=INK))
    f.append('<text x="%d" y="%d" font-family="%s" font-size="13" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %d %d)">V_peak / (I₀·√(L/C))</text>'
             % (26, oy-ph/2, FONT, INK, 26, oy-ph/2))

    zmax = 2.0
    def X(z): return ox + pw * (z/zmax)
    def Y(r): return oy - ph * r          # r у 0..1

    # рівень 1.0 (ідеал)
    f.append(line(ox, Y(1.0), ox+pw, Y(1.0), color=MUTED, sw=1.2, dash="5,4"))
    f.append(text(ox+pw-4, Y(1.0)-8, "ідеал (без утрат)", size=12, color=MUTED, anchor="end"))
    for r,lab in [(1.0,"1.0"),(0.5,"0.5"),(0.0,"0")]:
        f.append(text(ox-8, Y(r)+4, lab, size=11, color=MUTED, anchor="end"))
    # сітка по ζ
    for z in [0.5,1.0,1.5,2.0]:
        f.append(line(X(z), oy, X(z), oy+5, color=INK, sw=1.5))
        f.append(text(X(z), oy+20, "%.1f"%z, size=11, color=MUTED))

    # множник = максимум v(t)/(I₀·√(L/C)) для послідовного RLC із поч. струмом.
    # Замість аналітичних гілок рахуємо максимум напряму (чесно й без сингулярностей
    # у ζ→1): це те саме v(t), що на першій фігурі.
    def vfun(z, wt):
        if z < 1 - 1e-9:
            s = math.sqrt(1-z*z); return (1/s)*math.exp(-z*wt)*math.sin(s*wt)
        elif abs(z-1) < 1e-9:
            return wt*math.exp(-wt)
        else:
            s = math.sqrt(z*z-1)
            return (1/(2*s))*(math.exp(-(z-s)*wt) - math.exp(-(z+s)*wt))
    def factor_norm(z):
        # шукаємо перший максимум по сітці ω₀·t ∈ (0, 30]
        best = 0.0; wt = 0.001
        while wt <= 30.0:
            v = vfun(z, wt)
            if v > best: best = v
            elif v < best - 1e-6 and best > 0:  # пройшли перший максимум
                break
            wt += 0.01
        return best

    pts=[]
    z=0.02
    while z <= zmax+1e-9:
        pts.append("%.1f,%.1f"%(X(z), Y(min(1.0, factor_norm(z)))))
        z += 0.02
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'%(" ".join(pts), POS))

    # вертикалі-межі режимів
    f.append(line(X(1.0), oy, X(1.0), oy-ph, color=INK, sw=1.2, dash="4,4"))
    f.append(text(X(1.0), oy-ph-6, "ζ=1 (критичне)", size=12, color=INK))
    f.append(text(X(0.55), oy-ph+16, "недозагашений: дзвенить", size=12, color=POS, anchor="middle"))
    f.append(text(X(1.55), oy-ph+16, "перезагашений", size=12, color=FIELD, anchor="middle"))

    # точки-орієнтири
    def dot(z, lab, dy=-14, dx=0, col=INK, anch="middle"):
        r = min(1.0, factor_norm(z))
        s = circle(X(z), Y(r), 5, fill=col, stroke=INK, sw=1.3)
        s += text(X(z)+dx, Y(r)+dy, lab, size=11, bold=True, color=col, anchor=anch)
        return s
    f.append(dot(0.02, "ζ→0: пік = ідеал", dy=18, dx=6, col=MUTED, anch="start"))
    f.append(dot(0.5, "ζ=0.5 (Q=1): пік ≈ 0.55 ідеалу", dy=-12, dx=8, col=POS, anch="start"))
    # операційна точка снабера R≈√(L/C): у ПАРАЛЕЛЬНІЙ ролі це ζ≈0.5
    f.append(line(X(0.5), Y(factor_norm(0.5)), X(0.5), oy, color=POS, sw=1, dash="2,3"))

    # вісь-дзеркало Q (у правій нижній частині, де крива вже низько — вільно)
    f.append(text(ox+pw-6, Y(0.30), "велике ζ ⇄ мала Q", size=12, color=MUTED, anchor="end", italic=True))
    f.append(text(ox+pw-6, Y(0.30)+16, "(Q = 1/(2ζ))", size=11, color=MUTED, anchor="end", italic=True))

    render(os.path.join(IMG, "peak-vs-zeta.svg"), W, H, *f)


if __name__ == "__main__":
    if not os.path.isdir(IMG):
        os.makedirs(IMG)
    fig_rlc_regimes()
    fig_peak_vs_zeta()
    print("OK: 2 figures written to", IMG)
