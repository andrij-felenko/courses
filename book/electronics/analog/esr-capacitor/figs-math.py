# -*- coding: utf-8 -*-
"""Фігури до математичної вставки «Крива повного опору» (esr-capacitor/math-impedance-curve).
Окремий генератор, щоб не чіпати figs.py статті; пише в ту саму ./img/.
  z-sum-complex.svg — складання трьох послідовних опорів у комплексній площині:
                      ESR по дійсній осі + (ωL − 1/ωC) по уявній; модуль = гіпотенуза.
  z-curve-log.svg   — точна крива |Z|(f) у лог-лог осях: дві асимптоти (−1/ωC і ωL),
                      їх перетин = f₀, дно дотикається рівня ESR.
Запуск:  python figs-math.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. z-sum-complex.svg — три послідовні опори як вектори в комплексній площині
# ════════════════════════════════════════════════════════════════════════════
def fig_z_sum():
    W, H = 660, 430
    f = []
    f.append(text(W / 2, 32, "Повний опір як гіпотенуза: ESR + j·(ωL − 1/ωC)", size=15, bold=True))

    ox, oy = 150, 250          # початок координат
    # осі
    f.append(arrow(ox - 30, oy, ox + 380, oy, color=INK, sw=1.6))       # дійсна (опір)
    f.append(arrow(ox, oy + 130, ox, oy - 170, color=INK, sw=1.6))      # уявна (реактивність)
    f.append(text(ox + 376, oy + 20, "дійсна вісь: опір (тепло)", size=11, color=INK, anchor="end"))
    f.append(text(ox + 6, oy - 162, "уявна вісь: реактивність", size=11, color=INK, anchor="start"))
    f.append(text(ox + 6, oy - 148, "+jωL вгору, −j/ωC вниз", size=10, color=MUTED, anchor="start"))

    # масштаб
    R = 150.0                   # ESR-вектор уздовж дійсної осі (пікселів)
    Xind = 120.0                # +ωL вгору
    Xcap = 200.0                # −1/ωC вниз (довший — нижче за резонанс)
    Xnet = Xind - Xcap          # = −80, чиста реактивність ємнісна (вниз)

    # ESR — горизонтальний вектор
    f.append(arrow(ox, oy, ox + R, oy, color=POS, sw=2.8))
    f.append(text(ox + R / 2, oy + 20, "ESR", size=12, color=POS, bold=True))

    # допоміжні вектори реактивностей від кінця ESR (пунктир) — показати −1/ωC і +ωL
    ex = ox + R
    f.append(line(ex, oy, ex, oy - Xind, color=MUTED, sw=1.6, dash="5 4"))   # +ωL вгору
    f.append(text(ex + 8, oy - Xind + 18, "+ωL", size=10, color=MUTED, anchor="start"))
    f.append(text(ex + 8, oy - Xind + 32, "(індуктивна)", size=9, color=MUTED, anchor="start"))
    f.append(line(ex, oy - Xind, ex, oy - Xnet, color=NEG, sw=1.6, dash="5 4"))  # −1/ωC униз
    f.append(text(ex + 8, oy - Xind - 26, "−1/ωC", size=10, color=NEG, anchor="start"))
    f.append(text(ex + 8, oy - Xind - 12, "(ємнісна, довша)", size=9, color=NEG, anchor="start"))

    # підсумкова чиста реактивність (вниз, бо нижче за резонанс)
    f.append(line(ex, oy, ex, oy - Xnet, color=FIELD, sw=2.2))
    f.append(text(ex + 8, oy - Xnet / 2 + 4, "X = ωL − 1/ωC", size=11, color=FIELD, anchor="start"))
    f.append(text(ex + 8, oy - Xnet / 2 + 18, "(тут < 0)", size=9, color=MUTED, anchor="start"))

    # вектор Z — гіпотенуза від початку до кінця (ESR, X)
    zx, zy = ex, oy - Xnet
    f.append(arrow(ox, oy, zx, zy, color=INK, sw=3.0))
    f.append(text((ox + zx) / 2 - 14, (oy + zy) / 2 + 24, "|Z|", size=14, color=INK, bold=True, anchor="end"))

    # прямий кут між ESR і X
    f.append(line(ex - 12, oy, ex - 12, oy - 12, color=MUTED, sw=1.2))
    f.append(line(ex - 12, oy - 12, ex, oy - 12, color=MUTED, sw=1.2))

    body, w0, h0 = textbox(W / 2, 360,
                           "Три послідовні опори додаються як вектори: активний ESR лягає на дійсну вісь,\n"
                           "реактивності — на уявну (ωL вгору, 1/ωC вниз) і частково гасять одна одну.\n"
                           "Повний опір |Z| — гіпотенуза прямокутного трикутника з катетами ESR і (ωL − 1/ωC)",
                           size=11, color=INK, fill="#fbfbfc", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "z-sum-complex.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. z-curve-log.svg — точна крива |Z|(f) з двома асимптотами й дном на ESR
# ════════════════════════════════════════════════════════════════════════════
def fig_z_curve():
    import math as _m
    W, H = 700, 430
    f = []
    f.append(text(W / 2, 30, "Крива |Z|(f): дві прямі-асимптоти і дно на рівні ESR", size=15, bold=True))

    # межі області побудови (усе всередині них кліпиться)
    ox, oy = 95, 320           # низ-ліво (вісь X)
    axw, axh = 520, 250
    top = oy - axh             # верхній край області
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))            # вісь lg f
    f.append(arrow(ox, oy, ox, top - 6, color=INK, sw=1.6))            # вісь lg|Z|
    f.append(text(ox + axw - 4, oy + 22, "lg f  →", size=12, color=INK, anchor="end"))
    f.append(text(ox - 12, top + 6, "lg|Z|", size=12, color=INK, bold=True, anchor="end"))

    # умовна модель: ω від 10^-2.2 до 10^2.2 (резонанс посередині, ω₀=1, |Z|min=esr)
    N = 240
    DEC = 2.2
    esr = 0.16
    xL, xR = ox + 8, ox + axw - 16

    def wof(i):  return 10.0 ** (-DEC + 2 * DEC * i / (N - 1))
    def zmag(i):
        w = wof(i); X = w - 1.0 / w
        return _m.sqrt(esr * esr + X * X)
    def cap(i):  return 1.0 / wof(i)     # ємнісна вітка −1/ωC
    def ind(i):  return wof(i)           # індуктивна вітка ωL

    vals = [zmag(i) for i in range(N)]
    lgmin = _m.log10(esr) - 0.10         # трохи нижче дна, щоб горизонталь ESR влізла
    lgmax = _m.log10(max(vals)) + 0.06
    def px(i): return xL + (xR - xL) * i / (N - 1)
    def pyv(v):
        y = oy - (axh - 18) * ((_m.log10(v) - lgmin) / (lgmax - lgmin))
        return y
    # кліп точки в межі області [top .. oy]; точка поза межами відкидається
    def poly_clipped(valfn, lo_i=0, hi_i=N):
        pts = []
        for i in range(lo_i, hi_i):
            y = pyv(valfn(i))
            if top - 0.5 <= y <= oy + 0.5:
                pts.append("%.1f,%.1f" % (px(i), y))
        return " ".join(pts)

    # пунктирні асимптоти (обидві обрізані по області)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="6 5"/>' % (poly_clipped(cap), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="6 5"/>' % (poly_clipped(ind), MUTED))
    # суцільна крива |Z|
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (poly_clipped(zmag), INK))

    # рівень ESR — горизонталь-дно
    yE = pyv(esr)
    f.append(line(ox, yE, xR, yE, color=POS, sw=1.6, dash="5 4"))
    f.append(text(ox + 4, yE - 8, "|Z| = ESR — рівень дна (мінімум)", size=11, color=POS, bold=True, anchor="start"))

    # частота резонансу — вертикаль крізь дно (мінімум vals)
    imin = min(range(N), key=lambda i: vals[i])
    fx = px(imin)
    f.append(line(fx, oy, fx, pyv(vals[imin]), color=FIELD, sw=1.4, dash="4 4"))
    f.append(circle(fx, pyv(vals[imin]), 4.5, fill="#ffffff", stroke=FIELD, sw=2.4))
    f.append(text(fx, oy + 22, "f₀ = 1/(2π√(LC))", size=11, color=FIELD, bold=True, anchor="middle"))

    # підписи нахилів — біля видимих ділянок асимптот
    iC = int(0.16 * N); iI = int(0.86 * N)
    f.append(text(px(iC) + 8, pyv(cap(iC)) + 4, "−1/ωC  (нахил −1)", size=10, color=NEG, anchor="start"))
    f.append(text(px(iI) - 8, pyv(ind(iI)) + 4, "+ωL  (нахил +1)", size=10, color=MUTED, anchor="end"))

    body, w0, h0 = textbox(W / 2, 372,
                           "Дві реактивності в лог-лог осях — прямі однакового нахилу різного знаку, що перетинаються рівно на f₀.\n"
                           "Корінь у формулі — це геометрична середина: f₀ стоїть якраз посередині між ними за логарифмом.\n"
                           "Крива |Z| лягає на більшу з віток, а на резонансі сідає на горизонталь ESR — це її мінімум",
                           size=11, color=INK, fill="#fbfbfc", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "z-curve-log.svg"), W, H, *f)


if __name__ == "__main__":
    fig_z_sum()
    fig_z_curve()
    print("OK: 2 фігури у", IMG)
