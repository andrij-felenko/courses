# -*- coding: utf-8 -*-
"""Фігури для детальної статті «TCXO та OCXO» (guide/embedded/komponenty).
Чистий Python + svgkit, без залежностей. Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def _axes(x0, y0, w, h, xlab, ylab, title=None):
    """Осі з підписами. Повертає список фрагментів і замикання px,py."""
    frags = [line(x0, y0, x0 + w, y0, INK, 1.8),          # X
             line(x0, y0, x0, y0 - h, INK, 1.8)]          # Y (вгору)
    frags.append(text(x0 + w, y0 + 22, xlab, size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 8, y0 - h + 2, ylab, size=13, color=MUTED, anchor="end"))
    if title:
        frags.append(text(x0 + w / 2, y0 - h - 14, title, size=14, color=INK, bold=True))
    return frags


# ── 1. Кубічна крива частота–температура: AT-зріз проти SC-зрізу ──────────────
def fig_ft_cubic():
    W, H = 760, 470
    x0, y0, w, h = 90, 400, 600, 300
    cy = y0 - h / 2                       # рівень Δf/f = 0
    frags = [text(W / 2, 30, "Крива частота–температура: чому вона кубічна", size=17, bold=True),
             text(W / 2, 50, "AT-зріз — перегин коло +25 °C; SC-зріз — коло +90 °C, з пологою «полицею»",
                  size=12.5, color=MUTED, italic=True)]
    frags += _axes(x0, y0, w, h, "температура T, °C", "Δf/f, ppm")
    # горизонталь нуля
    frags.append(line(x0, cy, x0 + w, cy, MUTED, 1.0, dash="4,4"))
    frags.append(text(x0 - 8, cy + 4, "0", size=12, color=MUTED, anchor="end"))
    # шкала X: -40..+100
    Tmin, Tmax = -40.0, 100.0
    def px(T): return x0 + (T - Tmin) / (Tmax - Tmin) * w
    for T in (-40, 0, 25, 50, 90, 100):
        xx = px(T)
        frags.append(line(xx, y0, xx, y0 + 5, INK, 1.4))
        frags.append(text(xx, y0 + 20, str(T), size=11, color=MUTED))
    # шкала Y: ±25 ppm
    ppm_full = 25.0
    def py(v): return cy - v / ppm_full * (h / 2)
    for v in (-20, -10, 10, 20):
        yy = py(v)
        frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2))
        frags.append(text(x0 - 8, yy + 4, str(v), size=10.5, color=MUTED, anchor="end"))

    def cubic(a1, a3, Ti, T):        # Δf/f = a1(T-Ti) + a3(T-Ti)^3  [ppm]
        d = T - Ti
        return a1 * d + a3 * d ** 3

    # AT-зріз: перегин ~25 °C, a1 малий, a3 ~1.0e-4 ppm/°C^3 (масштабовано під вікно)
    ptsAT = []
    for i in range(0, 141):
        T = Tmin + i
        v = cubic(0.0, 8.7e-5, 25.0, T)
        ptsAT.append("%.1f,%.1f" % (px(T), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptsAT), POS))
    # SC-зріз: перегин ~90 °C — у нашому вікні видно лише пологий «хвіст»
    ptsSC = []
    for i in range(0, 141):
        T = Tmin + i
        v = cubic(0.0, 8.7e-5, 90.0, T)
        v = max(-ppm_full, min(ppm_full, v))
        ptsSC.append("%.1f,%.1f" % (px(T), py(v)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,4"/>' % (" ".join(ptsSC), NEG))

    # перегини (точки повороту нахилу)
    frags.append(circle(px(25), py(0), 4.5, fill="#fff", stroke=POS, sw=2))
    frags.append(circle(px(90), py(0), 4.5, fill="#fff", stroke=NEG, sw=2))
    frags.append(text(px(25), py(0) - 12, "перегин AT ≈ 25 °C", size=11, color=POS, bold=True))
    # полиця SC 70..85
    frags.append(line(px(70), py(cubic(0, 8.7e-5, 90, 70)), px(85), py(cubic(0, 8.7e-5, 90, 85)), FIELD, 6))
    frags.append(text(px(78), py(cubic(0, 8.7e-5, 90, 78)) + 26, "полога полиця SC", size=11, color=FIELD, bold=True))
    frags.append(text(px(90), py(0) + 20, "перегин SC ≈ 90 °C", size=11, color=NEG, bold=True))

    # легенда
    frags.append(line(x0 + 12, 78, x0 + 42, 78, POS, 2.6)); frags.append(text(x0 + 48, 82, "AT-зріз", size=12, color=INK, anchor="start"))
    frags.append(line(x0 + 150, 78, x0 + 180, 78, NEG, 2.6, dash="7,4")); frags.append(text(x0 + 186, 82, "SC-зріз", size=12, color=INK, anchor="start"))
    render(os.path.join(IMG, 'ft-cubic-cuts.svg'), W, H, *frags)


# ── 2. Компенсація як інверсія: дрейф + дзеркало + залишкова брижа (×20) ─────
def fig_compensation_inversion():
    W, H = 760, 500
    x0, y0, w, h = 90, 330, 600, 230
    cy = y0 - h / 2
    frags = [text(W / 2, 30, "TCXO: компенсація — це віднімання кубіки від самої себе", size=16.5, bold=True),
             text(W / 2, 50, "варикап додає дзеркальну поправку; лишається брижа недокомпенсації (внизу — ×20)",
                  size=12.5, color=MUTED, italic=True)]
    frags += _axes(x0, y0, w, h, "температура T, °C", "Δf/f, ppm")
    frags.append(line(x0, cy, x0 + w, cy, MUTED, 1.0, dash="4,4"))
    frags.append(text(x0 - 8, cy + 4, "0", size=12, color=MUTED, anchor="end"))
    Tmin, Tmax = -40.0, 85.0
    def px(T): return x0 + (T - Tmin) / (Tmax - Tmin) * w
    for T in (-40, 0, 25, 50, 85):
        xx = px(T); frags.append(line(xx, y0, xx, y0 + 5, INK, 1.4)); frags.append(text(xx, y0 + 19, str(T), size=11, color=MUTED))
    ppm_full = 22.0
    def py(v): return cy - v / ppm_full * (h / 2)
    for v in (-15, 15):
        yy = py(v); frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2)); frags.append(text(x0 - 8, yy + 4, "%+d" % v, size=10.5, color=MUTED, anchor="end"))

    a3 = 8.6e-5
    def drift(T): return a3 * (T - 25.0) ** 3            # голий кварц [ppm]
    # поправка = майже дзеркало, але з дрібною похибкою підгонки (недосконалий поліном)
    def corr(T):
        d = T - 25.0
        return -(a3 * d ** 3) + 0.35 * (d / 60.0) ** 2 * 1.0  # ледь недокомпенсовано на краях
    pd, pc, pr = [], [], []
    for i in range(0, 126):
        T = Tmin + i
        pd.append("%.1f,%.1f" % (px(T), py(drift(T))))
        pc.append("%.1f,%.1f" % (px(T), py(corr(T))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pd), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,4"/>' % (" ".join(pc), FIELD))
    # легенда
    frags.append(line(x0 + 12, 78, x0 + 40, 78, POS, 2.6)); frags.append(text(x0 + 46, 82, "голий кварц Δf/f(T)", size=11.5, color=INK, anchor="start"))
    frags.append(line(x0 + 230, 78, x0 + 258, 78, FIELD, 2.4, dash="7,4")); frags.append(text(x0 + 264, 82, "поправка варикапа", size=11.5, color=INK, anchor="start"))

    # ── нижня панель: залишок (drift+corr) з підсиленням ×20 ──
    yb0, hb = 470, 90
    cyb = yb0 - hb / 2
    frags.append(line(x0, yb0, x0 + w, yb0, INK, 1.6))
    frags.append(line(x0, cyb, x0 + w, cyb, MUTED, 1.0, dash="4,4"))
    frags.append(text(x0 - 8, cyb + 4, "0", size=11, color=MUTED, anchor="end"))
    ppm_b = 1.2
    def pyb(v): return cyb - v / ppm_b * (hb / 2)
    for v in (-1, 1):
        yy = pyb(v); frags.append(line(x0 - 5, yy, x0, yy, INK, 1.1)); frags.append(text(x0 - 8, yy + 4, "%+d" % v, size=10, color=MUTED, anchor="end"))
    pres = []
    for i in range(0, 126):
        T = Tmin + i
        pres.append("%.1f,%.1f" % (px(T), pyb(drift(T) + corr(T))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pres), NEG))
    frags.append(text(x0 + w, cyb - hb / 2 - 6, "залишкова брижа, ppm  (×20)", size=11.5, color=NEG, anchor="end", bold=True))
    render(os.path.join(IMG, 'compensation-inversion.svg'), W, H, *frags)


# ── 3. OCXO: статичне теплове підсилення + перехідний прогрів ────────────────
def fig_oven_gain():
    W, H = 760, 460
    # ліва панель: T_кристала vs T_довкілля
    x0, y0, w, h = 80, 350, 340, 250
    frags = [text(W / 2, 30, "OCXO: термостат гасить дрейф тепловим підсиленням", size=16, bold=True),
             text(W / 2, 50, "нахил «T кристала / T довкілля» ≈ 1/G — тому залишковий дрейф падає в G разів",
                  size=12.5, color=MUTED, italic=True)]
    frags += _axes(x0, y0, w, h, "T довкілля, °C", "T кристала, °C")
    Ta_min, Ta_max = -40.0, 80.0
    Tc_min, Tc_max = 78.0, 86.0
    def px(T): return x0 + (T - Ta_min) / (Ta_max - Ta_min) * w
    def py(T): return y0 - (T - Tc_min) / (Tc_max - Tc_min) * h
    for T in (-40, 0, 40, 80):
        xx = px(T); frags.append(line(xx, y0, xx, y0 + 5, INK, 1.3)); frags.append(text(xx, y0 + 19, str(T), size=10.5, color=MUTED))
    for T in (80, 82, 84):
        yy = py(T); frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2)); frags.append(text(x0 - 8, yy + 4, str(T), size=10.5, color=MUTED, anchor="end"))
    # без термостата: T_кристала = T_довкілля (крута лінія 1:1, тут вертикальний зріз показуємо стрілкою тексту)
    # з термостатом: уставка 82 °C, G=50 → нахил 1/50, поки нагрівач має запас (T_довк < 82)
    Tset, G = 82.0, 50.0
    seg = []
    for i in range(0, 121):
        Ta = Ta_min + i
        if Ta <= Tset:
            Tc = Tset + (Ta - Tset) / G
        else:
            Tc = Ta            # нагрівач не може охолоджувати — вище уставки термостат «здається»
        Tc = max(Tc_min, min(Tc_max, Tc))
        seg.append("%.1f,%.1f" % (px(Ta), py(Tc)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(seg), FIELD))
    frags.append(line(px(Tset), y0, px(Tset), y0 - h, POS, 1.2, dash="4,4"))
    frags.append(text(px(Tset), y0 - h - 4, "уставка 82 °C", size=11, color=POS, bold=True))
    frags.append(text(px(-10), py(81.6) - 8, "нахил ≈ 1/G", size=11.5, color=FIELD, bold=True, anchor="start"))
    frags.append(text(px(75), py(84.2), "втрата регулювання", size=10, color=MUTED, anchor="end"))

    # права панель: перехідний прогрів f(t)
    x1, y1, w1, h1 = 480, 350, 220, 250
    frags += _axes(x1, y1, w1, h1, "час від увімкнення, хв", "Δf/f, ppb")
    cy1 = y1 - h1 * 0.30
    frags.append(line(x1, cy1, x1 + w1, cy1, MUTED, 1.0, dash="4,4"))
    frags.append(text(x1 - 6, cy1 + 4, "0", size=10.5, color=MUTED, anchor="end"))
    import math
    ptw = []
    for i in range(0, 121):
        t = i / 20.0        # 0..6 хв
        v = 900.0 * math.exp(-t / 1.1) - 60.0 * math.exp(-t / 0.15)  # прогрів + вистрибування
        yy = cy1 - v / 950.0 * (h1 * 0.62)
        ptw.append("%.1f,%.1f" % (x1 + t / 6.0 * w1, yy))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptw), POS))
    for t in (0, 2, 4, 6):
        xx = x1 + t / 6.0 * w1; frags.append(line(xx, y1, xx, y1 + 5, INK, 1.3)); frags.append(text(xx, y1 + 19, str(t), size=10.5, color=MUTED))
    frags.append(line(x1, cy1 + 8, x1 + w1, cy1 + 8, FIELD, 1.4, dash="6,4"))
    frags.append(text(x1 + w1, cy1 - 6, "смуга готовності ±5 ppb", size=10, color=FIELD, anchor="end"))
    frags.append(text(x1 + w1 * 0.55, y1 - h1 + 30, "частота «пливе»,\nпоки термостат\nне вийде на режим", size=10.5, color=MUTED))
    render(os.path.join(IMG, 'oven-gain-warmup.svg'), W, H, *frags)


# ── 4. Девіація Алана: короткочасна vs довгочасна — де хто панує ─────────────
def fig_allan_crossover():
    W, H = 720, 440
    x0, y0, w, h = 90, 360, 560, 280
    frags = [text(W / 2, 30, "Хто панує коли: девіація Алана σ(τ) від часу усереднення", size=15.5, bold=True),
             text(W / 2, 50, "кварц/OCXO тримає короткі τ; GPS — довгі. GPSDO бере від кожного його сильний бік",
                  size=12, color=MUTED, italic=True)]
    frags += _axes(x0, y0, w, h, "час усереднення τ, с (лог)", "σ(τ) (лог)")
    # логарифмічні осі: τ 1e0..1e5, σ 1e-13..1e-9
    import math
    tmin, tmax = 0, 5          # десяткові порядки τ
    smin, smax = -13.0, -9.0
    def px(lt): return x0 + (lt - tmin) / (tmax - tmin) * w
    def py(ls): return y0 - (ls - smin) / (smax - smin) * h
    for e in range(tmin, tmax + 1):
        xx = px(e); frags.append(line(xx, y0, xx, y0 + 5, INK, 1.3)); frags.append(text(xx, y0 + 19, "10%d" % e, size=10.5, color=MUTED))
    for e in range(int(smin), int(smax) + 1):
        yy = py(e); frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2)); frags.append(text(x0 - 8, yy + 4, "10%d" % e, size=10, color=MUTED, anchor="end"))

    # локальний OCXO: падає як 1/sqrt(τ) на коротких, тоді флікер-полиця, тоді росте (дрейф/старіння)
    loc = []
    for i in range(0, 101):
        lt = tmin + i / 100.0 * (tmax - tmin)
        t = 10 ** lt
        s = math.sqrt((3e-12) ** 2 / t + (2e-12) ** 2) + 4e-14 * t   # білий+флікер+дрейф
        loc.append("%.1f,%.1f" % (px(lt), py(math.log10(s))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(loc), POS))
    # GPS: погано на коротких (шум 1PPS), добре на довгих (спадає, атомна прив'язка)
    gps = []
    for i in range(0, 101):
        lt = tmin + i / 100.0 * (tmax - tmin)
        t = 10 ** lt
        s = 3e-10 / t          # ~1/τ від квантування 1PPS
        s = max(s, 8e-14)
        gps.append("%.1f,%.1f" % (px(lt), py(math.log10(s))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,4"/>' % (" ".join(gps), NEG))
    # GPSDO: нижня обгортка обох
    do = []
    for i in range(0, 101):
        lt = tmin + i / 100.0 * (tmax - tmin)
        t = 10 ** lt
        sl = math.sqrt((3e-12) ** 2 / t + (2e-12) ** 2) + 4e-14 * t
        sg = max(3e-10 / t, 8e-14)
        do.append("%.1f,%.1f" % (px(lt), py(math.log10(min(sl, sg)))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.4" opacity="0.35"/>' % (" ".join(do), FIELD))

    # точка перетину (τ ~1000 c)
    frags.append(line(px(3), y0, px(3), y0 - h, MUTED, 1.0, dash="3,3"))
    frags.append(text(px(3), py(-12.6), "перетин:\nтут керування\nпереходить до GPS", size=10, color=MUTED))
    # легенда
    frags.append(line(x0 + 320, 80, x0 + 348, 80, POS, 2.6)); frags.append(text(x0 + 354, 84, "локальний OCXO/TCXO", size=11, color=INK, anchor="start"))
    frags.append(line(x0 + 320, 98, x0 + 348, 98, NEG, 2.6, dash="7,4")); frags.append(text(x0 + 354, 102, "сам GPS (1PPS)", size=11, color=INK, anchor="start"))
    frags.append(line(x0 + 320, 116, x0 + 348, 116, FIELD, 3.4)); frags.append(text(x0 + 354, 120, "GPSDO (вибирає краще)", size=11, color=INK, anchor="start"))
    render(os.path.join(IMG, 'allan-crossover.svg'), W, H, *frags)


# ── 5. [math] Як кут зрізу гасить молодші члени: сума складників кривої ────────
def fig_term_cancellation():
    W, H = 760, 470
    x0, y0, w, h = 90, 400, 600, 300
    cy = y0 - h / 2
    frags = [text(W / 2, 30, "Чому лишається кубіка: кут зрізу гасить лінійний і квадратичний члени", size=15.5, bold=True),
             text(W / 2, 50, "три складники Δf/f(T) окремо — при a₁≈0, a₂≈0 виживає тільки a₃·(T−Tᵢ)³",
                  size=12.5, color=MUTED, italic=True)]
    frags += _axes(x0, y0, w, h, "T − Tᵢ, °C", "внесок у Δf/f, ppm")
    frags.append(line(x0, cy, x0 + w, cy, MUTED, 1.0, dash="4,4"))
    frags.append(text(x0 - 8, cy + 4, "0", size=12, color=MUTED, anchor="end"))
    Dmin, Dmax = -60.0, 60.0
    def px(d): return x0 + (d - Dmin) / (Dmax - Dmin) * w
    for d in (-60, -30, 0, 30, 60):
        xx = px(d); frags.append(line(xx, y0, xx, y0 + 5, INK, 1.4)); frags.append(text(xx, y0 + 20, "%+d" % d if d else "0", size=11, color=MUTED))
    ppm_full = 25.0
    def py(v): return cy - v / ppm_full * (h / 2)
    for v in (-20, -10, 10, 20):
        yy = py(v); frags.append(line(x0 - 5, yy, x0, yy, INK, 1.2)); frags.append(text(x0 - 8, yy + 4, "%+d" % v, size=10.5, color=MUTED, anchor="end"))

    a3 = 1.0e-4        # ppm/°C^3 — виживає
    a1_res = 0.02      # мізерний залишок лінійного (для наочності «майже нуль»)
    a2_res = 0.0006    # мізерний залишок квадратичного
    def clamp(v): return max(-ppm_full, min(ppm_full, v))
    lin, quad, cub, tot = [], [], [], []
    for i in range(0, 121):
        d = Dmin + i
        lin.append("%.1f,%.1f" % (px(d), py(clamp(a1_res * d))))
        quad.append("%.1f,%.1f" % (px(d), py(clamp(a2_res * d * d))))
        cub.append("%.1f,%.1f" % (px(d), py(clamp(a3 * d ** 3))))
        tot.append("%.1f,%.1f" % (px(d), py(clamp(a1_res * d + a2_res * d * d + a3 * d ** 3))))
    # лінійний і квадратичний — тонкі, приглушені (майже лежать на нулі)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,4"/>' % (" ".join(lin), NEG))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="2,3"/>' % (" ".join(quad), MUTED))
    # кубічний — жирний
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(cub), POS))
    # сума — зелена, майже збігається з кубічною
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="8,4"/>' % (" ".join(tot), FIELD))

    frags.append(circle(px(0), py(0), 4.5, fill="#fff", stroke=INK, sw=2))
    frags.append(text(px(0) + 6, py(0) - 8, "перегин Tᵢ", size=11, color=INK, bold=True, anchor="start"))
    # легенда
    lx = x0 + 12
    frags.append(line(lx, 76, lx + 28, 76, POS, 2.8)); frags.append(text(lx + 34, 80, "a₃·(T−Tᵢ)³  — виживає", size=11.5, color=INK, anchor="start"))
    frags.append(line(lx, 94, lx + 28, 94, NEG, 1.6, dash="5,4")); frags.append(text(lx + 34, 98, "a₁·(T−Tᵢ)  ≈ 0 (кут гасить)", size=11.5, color=INK, anchor="start"))
    frags.append(line(lx + 300, 76, lx + 328, 76, MUTED, 1.6, dash="2,3")); frags.append(text(lx + 334, 80, "a₂·(T−Tᵢ)²  ≈ 0", size=11.5, color=INK, anchor="start"))
    frags.append(line(lx + 300, 94, lx + 328, 94, FIELD, 2.0, dash="8,4")); frags.append(text(lx + 334, 98, "сума всіх членів", size=11.5, color=INK, anchor="start"))
    render(os.path.join(IMG, 'term-cancellation.svg'), W, H, *frags)


# ── 6. [math] Дві нелінійності складаються в дзеркальну кубіку ────────────────
def fig_two_nonlinearities():
    import math
    W, H = 780, 560
    # три вертикальні панелі: C(V) → CL·(гіпербола 1/(C0+CL)) → підсумковий −Δf/f(T)
    frags = [text(W / 2, 30, "Звідки береться дзеркальна кубіка: дві нелінійності поспіль", size=16, bold=True),
             text(W / 2, 50, "варикап C(V) [опукла] · тяга 1/(C₀+CL) [гіпербола] → майже −a₃·(T−Tᵢ)³, плюс залишкова брижа",
                  size=12, color=MUTED, italic=True)]

    # спільні дані: температура задає напругу, напруга задає ємність, ємність задає зсув
    Tmin, Tmax, Ti = -40.0, 85.0, 26.0
    a3 = 1.0e-4
    C0 = 3.0            # пФ
    C1 = 5.0e-3         # пФ (=5 фФ)
    # ланка керування має так гнути V(T), щоб на виході вийшла −кубіка; змоделюймо
    # реальну (недосконалу) V(T) як кубічну за T, і подивимось підсумок.
    def Vof(T):        # керувальна напруга, В (0..3.3), монотонно спадна з T
        d = (T - Ti)
        return 1.65 - 0.9 * (d / 60.0) - 0.6 * (d / 60.0) ** 3
    def Cvar(V):       # варикап: ємність опукло падає з напругою (гіперабрупт), пФ
        return 6.0 + 34.0 / (1.0 + 0.9 * V) ** 1.6
    def CL(T):
        return Cvar(Vof(T))
    # C₁,C₀,CL усі в пФ → відношення безрозмірне; ·1e6 дає ppm
    def dfppm(T):
        return C1 / (2.0 * (C0 + CL(T))) * 1e6

    # ── панель A: C(V) ──
    ax, ay, aw, ah = 70, 250, 190, 150
    frags += _axes(ax, ay, aw, ah, "V, В", "C варикапа, пФ")
    def apx(V): return ax + V / 3.3 * aw
    def apy(C): return ay - (C - 6.0) / 36.0 * ah
    pa = []
    for i in range(0, 101):
        V = 3.3 * i / 100.0
        pa.append("%.1f,%.1f" % (apx(V), apy(Cvar(V))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pa), NEG))
    for V in (0, 1.65, 3.3):
        xx = apx(V); frags.append(line(xx, ay, xx, ay + 4, INK, 1.2)); frags.append(text(xx, ay + 17, ("%.1f" % V).rstrip("0").rstrip("."), size=10, color=MUTED))
    frags.append(text(ax + aw / 2, ay - ah - 10, "1. варикап C(V)", size=12, color=NEG, bold=True))
    frags.append(text(ax + aw / 2, ay - ah + 8, "опукла: спадає, вигинаючись", size=10, color=MUTED))

    # ── панель B: тяга vs CL (гіпербола) ──
    bx, by, bw, bh = 300, 250, 190, 150
    frags += _axes(bx, by, bw, bh, "C₀+CL, пФ", "Δf/f, ppm")
    Csum_min, Csum_max = 9.0, 45.0
    df_min, df_max = C1 / (2 * Csum_max) * 1e6, C1 / (2 * Csum_min) * 1e6
    def bpx(Cs): return bx + (Cs - Csum_min) / (Csum_max - Csum_min) * bw
    def bpy(df): return by - (df - df_min) / (df_max - df_min) * bh
    pb = []
    for i in range(0, 101):
        Cs = Csum_min + (Csum_max - Csum_min) * i / 100.0
        pb.append("%.1f,%.1f" % (bpx(Cs), bpy(C1 / (2 * Cs) * 1e6)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pb), FIELD))
    for Cs in (10, 25, 40):
        xx = bpx(Cs); frags.append(line(xx, by, xx, by + 4, INK, 1.2)); frags.append(text(xx, by + 17, str(Cs), size=10, color=MUTED))
    frags.append(text(bx + bw / 2, by - bh - 10, "2. тяга ∝ 1/(C₀+CL)", size=12, color=FIELD, bold=True))
    frags.append(text(bx + bw / 2, by - bh + 8, "гіпербола: теж крива", size=10, color=MUTED))

    # ── панель C: підсумковий зсув vs T проти ідеальної −кубіки ──
    cx, cyp, cw, ch = 530, 250, 190, 150
    frags += _axes(cx, cyp, cw, ch, "T, °C", "зсув частоти, ppm")
    # нормуймо: віднімемо середнє, покажемо як −Δf/f лягає на дзеркало кубіки
    Ts = [Tmin + k for k in range(0, int(Tmax - Tmin) + 1)]
    applied = [dfppm(T) for T in Ts]
    off = sum(applied) / len(applied)
    applied = [a - off for a in applied]                 # центрований прикладений зсув
    target = [-(a3 * (T - Ti) ** 3) for T in Ts]         # ідеальне дзеркало кубіки
    toff = sum(target) / len(target)
    target = [t - toff for t in target]
    allv = applied + target
    vmn, vmx = min(allv), max(allv)
    def cpx(T): return cx + (T - Tmin) / (Tmax - Tmin) * cw
    def cpy(v): return cyp - (v - vmn) / (vmx - vmn) * ch
    frags.append(line(cx, cpy(0), cx + cw, cpy(0), MUTED, 1.0, dash="4,4"))
    pt_t = ["%.1f,%.1f" % (cpx(T), cpy(v)) for T, v in zip(Ts, target)]
    pt_a = ["%.1f,%.1f" % (cpx(T), cpy(v)) for T, v in zip(Ts, applied)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,4"/>' % (" ".join(pt_t), POS))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pt_a), NEG))
    for T in (-40, 25, 85):
        xx = cpx(T); frags.append(line(xx, cyp, xx, cyp + 4, INK, 1.2)); frags.append(text(xx, cyp + 17, str(T), size=10, color=MUTED))
    frags.append(text(cx + cw / 2, cyp - ch - 10, "3. підсумок 1·2", size=12, color=INK, bold=True))

    # стрілки «·» між панелями
    frags.append(text((ax + aw + bx) / 2, ay - ah / 2, "·", size=30, color=INK, bold=True))
    frags.append(text((bx + bw + cx) / 2, by - bh / 2, "→", size=22, color=INK, bold=True))

    # легенда підсумку
    ly = 500
    frags.append(line(cx - 20, ly, cx + 8, ly, POS, 2.4, dash="7,4")); frags.append(text(cx + 14, ly + 4, "потрібне −a₃(T−Tᵢ)³", size=11, color=INK, anchor="start"))
    frags.append(line(cx - 20, ly + 20, cx + 8, ly + 20, NEG, 2.4)); frags.append(text(cx + 14, ly + 24, "що дала мережа", size=11, color=INK, anchor="start"))

    # підсумковий текст-рамка
    tb, twb, thb = fitbox(70, 470, 420, 66,
        "Дві криві множаться: опукле C(V) множиться на\nгіперболу 1/(C₀+CL). Мережу підбирають так, щоб добуток\nвиписав саме −кубіку. Незбіг у кутиках і є брижа недокомпенсації.",
        size=11, fill=FILL, stroke=MUTED), 420, 66
    frags.append(tb)
    render(os.path.join(IMG, 'two-nonlinearities.svg'), W, H, *frags)


# ── 7. [proj] Дві петлі, один ЦАП: швидкий feed-forward + повільний feedback ──
def fig_two_loops():
    """Архітектура прошивки: DCXO (розімкнена, швидка) + GPSDO (замкнена, повільна)
    зводяться додаванням у один ЦАП; railing підсумку живить антивіндап."""
    W, H = 1024, 470
    frags = [text(W / 2, 28, "Прошивка: дві петлі керують однією напругою на варикапі", size=16, bold=True),
             text(W / 2, 47, "швидка розімкнена (температура) + повільна замкнена (GPS) → сума в один ЦАП",
                  size=12, color=MUTED, italic=True)]

    # верхня доріжка — DCXO (feed-forward, швидко); нижня — GPSDO (feedback, повільно)
    yT = 120          # рівень верхньої доріжки
    yB = 300          # рівень нижньої доріжки
    # ── верх: давач → Горнер/поліном → база коду ──
    b1, w1, h1 = textbox(120, yT, "термодавач\nT, °C", size=11.5, fill="#eef6ff", stroke=NEG); frags.append(b1)
    b2, w2, h2 = textbox(320, yT, "поліном 3-го пор.\nГорнер, фікс. точка", size=11.5, fill="#eef6ff", stroke=NEG); frags.append(b2)
    b3, w3, h3 = textbox(520, yT, "код бази\n(центр + темп.)", size=11.5, fill="#eef6ff", stroke=NEG); frags.append(b3)
    frags.append(arrow(120 + w1 / 2, yT, 320 - w2 / 2, yT, NEG, 2.0))
    frags.append(arrow(320 + w2 / 2, yT, 520 - w3 / 2, yT, NEG, 2.0))
    frags.append(text(220, yT - 34, "feed-forward · швидко (32 Гц)", size=11, color=NEG, bold=True))
    frags.append(text(220, yT - 18, "знаємо наперед з калібрування", size=10, color=MUTED))

    # ── низ: 1PPS → фазомір → ПІ + антивіндап → тонка поправка ──
    c1, cw1, ch1 = textbox(120, yB, "1PPS від GPS\n(атомна прив'язка)", size=11.5, fill="#eafbf0", stroke=FIELD); frags.append(c1)
    c2, cw2, ch2 = textbox(320, yB, "фазомір\nΔφ, нс", size=11.5, fill="#eafbf0", stroke=FIELD); frags.append(c2)
    c3, cw3, ch3 = textbox(520, yB, "ПІ-регулятор\n+ антивіндап", size=11.5, fill="#eafbf0", stroke=FIELD); frags.append(c3)
    frags.append(arrow(120 + cw1 / 2, yB, 320 - cw2 / 2, yB, FIELD, 2.0))
    frags.append(arrow(320 + cw2 / 2, yB, 520 - cw3 / 2, yB, FIELD, 2.0))
    frags.append(text(220, yB + 34, "feedback · повільно (стала 10²–10³ с)", size=11, color=FIELD, bold=True))
    frags.append(text(220, yB + 50, "бачимо лише зовні — виправляємо старіння", size=10, color=MUTED))

    # ── суматор ──
    sx, sy = 700, (yT + yB) / 2
    frags.append(circle(sx, sy, 20, fill="#fff", stroke=INK, sw=2))
    frags.append(text(sx, sy + 6, "+", size=22, color=INK, bold=True))
    # дві гілки в суматор
    frags.append(arrow(520 + w3 / 2, yT, sx - 14, sy - 12, NEG, 2.0))
    frags.append(arrow(520 + cw3 / 2, yB, sx - 14, sy + 12, FIELD, 2.0))

    # ── ЦАП → варикап → частота ──
    d1, dw1, dh1 = textbox(sx, 415, "ЦАП → варикап → частота", size=12, fill=FILL, stroke=INK, bold=True); frags.append(d1)
    frags.append(arrow(sx, sy + 20, sx, 415 - dh1 / 2, INK, 2.2))

    # ── зворотний зв'язок railing → антивіндап ──
    # від ЦАП вгору-ліворуч у ПІ: пунктир, підпис
    fx = sx + 70
    frags.append(line(sx, 415, fx, 415, POS, 1.6, dash="5,4"))
    frags.append(line(fx, 415, fx, yB - 40, POS, 1.6, dash="5,4"))
    frags.append(line(fx, yB - 40, 520, yB - 40, POS, 1.6, dash="5,4"))
    frags.append(arrow(520, yB - 40, 520, yB - ch3 / 2, POS, 1.6))
    frags.append(text(fx + 8, (415 + yB) / 2, "статус railing:\nупер у край →\nстопори інтеграл", size=10, color=POS, anchor="start"))

    # ── holdover-гілка (від 1PPS-валідності) ──
    frags.append(text(120, yB + 74, "GPS зник → holdover:", size=10.5, color=MUTED, bold=True, anchor="start"))
    frags.append(text(120, yB + 90, "заморозити + екстраполювати вивчений дрейф", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'two-loops-one-dac.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_ft_cubic()
    fig_compensation_inversion()
    fig_oven_gain()
    fig_allan_crossover()
    fig_term_cancellation()
    fig_two_nonlinearities()
    fig_two_loops()
    print("OK: 7 figures ->", IMG)
