# -*- coding: utf-8 -*-
# Фігури вставки math-slope-traction (окремий генератор, щоб не заважати figs.py).
# Вивід — у ту саму теку ./img/. Запуск: python figs_slope.py
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── m-1: розклад ваги на схилі; кут між m·g і нормаллю = кут схилу ────────────
def m_decompose():
    W, H = 720, 430
    frags = []
    frags.append(text(W/2, 26, "Чому вздовж схилу тягне саме m·g·sin α", size=17, bold=True))

    ax, ay = 90, 350
    ang = 30 * math.pi/180
    L = 470
    bx, by = ax + L*math.cos(ang), ay - L*math.sin(ang)
    frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="#eef1f4" stroke="%s" stroke-width="2"/>' % (ax, ay, bx, by, bx, ay, LINE))
    frags.append(text(ax+62, ay-8, "α", size=16, italic=True, bold=True))

    cx, cy = ax + 235*math.cos(ang), ay - 235*math.sin(ang) - 22
    frags.append(circle(cx, cy, 4, fill=INK, stroke=INK))

    ux, uy = math.cos(ang), -math.sin(ang)      # уздовж схилу (вгору +)
    nx, ny = math.sin(ang), math.cos(ang)       # нормаль до поверхні (від неї +)

    scale = 150
    gx, gy = cx, cy + scale
    frags.append(arrow(cx, cy, gx, gy, color=INK, sw=2.6))
    frags.append(text(gx+12, gy-4, "m·g", size=14, italic=True, bold=True, anchor="start"))

    comp_along = scale*math.sin(ang)
    sax, say = cx - comp_along*ux, cy - comp_along*uy
    frags.append(arrow(cx, cy, sax, say, color=POS, sw=2.8))
    frags.append(text(sax-6, say+18, "m·g·sin α", size=14, color=POS, bold=True, anchor="end"))

    comp_norm = scale*math.cos(ang)
    snx, sny = cx - comp_norm*nx, cy - comp_norm*ny
    frags.append(arrow(cx, cy, snx, sny, color=NEG, sw=2.8))
    frags.append(text(snx-10, sny+2, "m·g·cos α", size=14, color=NEG, bold=True, anchor="end"))

    frags.append(line(sax, say, gx, gy, color=MUTED, sw=1.2, dash="4 3"))
    frags.append(line(snx, sny, gx, gy, color=MUTED, sw=1.2, dash="4 3"))

    body, bw, bh = textbox(W/2, 410,
        "кут між m·g і нормаллю дорівнює куту схилу α  →  уздовж: sin α,  впоперек: cos α",
        size=13, bold=True, fill="#f4f6f8", stroke=LINE)
    frags.append(body)
    render(os.path.join(OUT, 'decompose.svg'), W, H, *frags)


# ── m-2: попит на тягу vs стеля зчеплення — кут зриву α* ─────────────────────
def m_traction_ceiling():
    W, H = 720, 440
    frags = []
    frags.append(text(W/2, 26, "Дві криві: скільки тяги треба й скільки дозволяє зчеплення", size=16, bold=True))

    ox, oy = 90, 360
    axw, axh = 560, 290
    frags.append(arrow(ox, oy, ox, oy-axh, color=INK, sw=1.8))
    frags.append(arrow(ox, oy, ox+axw, oy, color=INK, sw=1.8))
    frags.append(text(ox-8, oy-axh+4, "сила", size=12, anchor="end"))
    frags.append(text(ox+axw, oy+20, "кут схилу α", size=12, anchor="end"))
    frags.append(text(ox-8, oy+16, "0", size=11, color=MUTED, anchor="end"))

    mg = 40.0; mu = 0.6; crr = 0.06
    a_max = 42.0 * math.pi/180
    def X(a): return ox + (a / a_max) * axw
    # масштаб Y — під найбільшу з двох сил на всьому діапазоні (щоб нічого не втекло)
    Fpeak = max(mg*math.sin(a_max) + crr*mg*math.cos(a_max), mu*mg)
    fmax_scale = (axh-24) / Fpeak
    def Y(F): return oy - F * fmax_scale

    dem, cei = [], []
    n = 60
    for k in range(n+1):
        a = a_max * k/n
        Fneed = mg*math.sin(a) + crr*mg*math.cos(a)
        Fmax  = mu*mg*math.cos(a)
        dem.append((X(a), Y(Fneed)))
        cei.append((X(a), Y(Fmax)))
    dpath = "M" + " L".join("%.1f %.1f" % p for p in dem)
    cpath = "M" + " L".join("%.1f %.1f" % p for p in cei)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (cpath, NEG))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dpath, POS))

    cross = None
    for k in range(n):
        a0 = a_max*k/n; a1 = a_max*(k+1)/n
        d0 = (mg*math.sin(a0)+crr*mg*math.cos(a0)) - mu*mg*math.cos(a0)
        d1 = (mg*math.sin(a1)+crr*mg*math.cos(a1)) - mu*mg*math.cos(a1)
        if d0 <= 0 <= d1:
            t = -d0/(d1-d0) if d1 != d0 else 0
            ac = a0 + t*(a1-a0)
            cross = (X(ac), Y(mu*mg*math.cos(ac)))
            break
    if cross:
        frags.append(circle(cross[0], cross[1], 7, fill="#fff", stroke=INK, sw=2.4))
        frags.append(line(cross[0], cross[1], cross[0], oy, color=MUTED, sw=1.2, dash="4 3"))
        frags.append(text(cross[0], oy+18, "α*", size=13, bold=True, italic=True))

    frags.append(text(X(a_max*0.80), Y(mg*math.sin(a_max*0.80)+crr*mg)-6, "потрібна тяга", size=13, color=POS, bold=True, anchor="end"))
    frags.append(text(X(a_max*0.16), Y(mu*mg*math.cos(a_max*0.16))-12, "стеля зчеплення  µ·m·g·cos α", size=13, color=NEG, bold=True, anchor="start"))

    body, bw, bh = textbox(ox+axw*0.52, oy-axh+2,
        "правіше α* колесо зриває в буксування —\nхоч який момент дай мотору",
        size=12, bold=True, fill="#fdecea", stroke=POS)
    frags.append(body)
    render(os.path.join(OUT, 'ceiling.svg'), W, H, *frags)


# ── m-3: вікно передавального числа редуктора ───────────────────────────────
def m_gear_window():
    W, H = 720, 370
    frags = []
    frags.append(text(W/2, 26, "Вікно передавального числа редуктора", size=17, bold=True))

    ox, oy = 80, 200
    axw = 560
    # вісь — по НИЖНЬОМУ краю смуги зон (не по центру), щоб не різати написи всередині зон
    axis_y = oy + 30
    frags.append(arrow(ox, axis_y, ox+axw, axis_y, color=INK, sw=1.8))
    frags.append(text(ox+axw, axis_y+22, "передавальне число  i", size=12, anchor="end"))

    lo = ox + axw*0.32
    hi = ox + axw*0.66
    frags.append(rect(ox, oy-30, lo-ox, 60, fill="#fdecea", stroke=POS, sw=1.4))
    frags.append(rect(lo, oy-30, hi-lo, 60, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(rect(hi, oy-30, ox+axw-hi, 60, fill="#eef1f4", stroke=NEG, sw=1.4))

    frags.append(line(lo, oy-48, lo, oy+42, color=POS, sw=1.6, dash="4 3"))
    frags.append(line(hi, oy-48, hi, oy+42, color=NEG, sw=1.6, dash="4 3"))
    frags.append(text(lo, oy-54, "i_min", size=13, bold=True, italic=True, color=POS))
    frags.append(text(hi, oy-54, "i_max", size=13, bold=True, italic=True, color=NEG))

    frags.append(fitbox(ox+6, oy-28, lo-ox-10, 56,
        "замало моменту:\nне залізе на схил",
        size=11, color=POS, bold=True, fill="none", stroke="none"))
    frags.append(text((lo+hi)/2, oy+5, "робоче вікно", size=14, color=FIELD, bold=True))
    frags.append(fitbox(hi+4, oy-28, ox+axw-hi-8, 56,
        "завелике i:\nповільно, зрив/стопор",
        size=11, color=NEG, bold=True, fill="none", stroke="none"))

    body1, w1, h1 = textbox(lo, oy+92,
        "i_min: момент на колесі ≥\nпотрібного на схил (запас ×2–3)",
        size=11, fill="#fdecea", stroke=POS)
    frags.append(body1)
    body2, w2, h2 = textbox(hi, oy+92,
        "i_max: тяга ≤ стелі зчеплення\nі струм ≤ безпечного",
        size=11, fill="#eef1f4", stroke=NEG)
    frags.append(body2)
    render(os.path.join(OUT, 'gear-window.svg'), W, H, *frags)


if __name__ == '__main__':
    m_decompose()
    m_traction_ceiling()
    m_gear_window()
    print("ok: decompose.svg, ceiling.svg, gear-window.svg")
