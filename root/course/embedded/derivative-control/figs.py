# -*- coding: utf-8 -*-
"""Фігури детальної статті «Д-складова». Запуск: python figs.py
svgkit імпортуємо зі scripts/ (не переписуємо). Імена файлів — за slug, без номерів.
Ці фігури доповнюють базову статтю (там slope/brake/pi-vs-pid/higher-kp/noise-spikes/
derivative-kick); тут — глибші: спектр підсилення похідної, стеля шуму фільтра,
демпфування другого порядку, фазове випередження проти відставання."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (s, color, sw, d))


def axes(ox, oy, ax_w, ax_h, xlabel="час", ylabel=None):
    q = [line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6),
         arrow(ox, oy - ax_h + 14, ox, oy - ax_h, color=INK, sw=1.6),
         line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6),
         arrow(ox + ax_w - 14, oy, ox + ax_w, oy, color=INK, sw=1.6)]
    if xlabel:
        q.append(text(ox + ax_w, oy + 18, xlabel, size=12, color=MUTED, italic=True, anchor="end"))
    if ylabel:
        q.append(text(ox + 2, oy - ax_h - 6, ylabel, size=12, color=MUTED, anchor="start"))
    return q


def legend_row(x, y, color, label, sw=3.0, dash=None):
    return (line(x, y, x + 26, y, color=color, sw=sw, dash=dash) +
            text(x + 32, y + 4, label, size=12, color=color, anchor="start", bold=True))


# ── 1: спектр підсилення — ідеальна похідна vs фільтрована (лог-лог, схематично) ──
def fig_derivative_gain():
    W, H = 760, 380
    ox, oy = 96, 300
    ax_w, ax_h = 600, 244
    p = axes(ox, oy, ax_w, ax_h, xlabel="частота (log ω)", ylabel="підсилення |G| (log)")

    span_x = ax_w - 70
    span_y = ax_h - 60

    # ідеальна похідна: пряма з нахилом +1 у лог-лог (|G| = ω) — росте без стелі
    ideal = [(ox + 40 + (i / 100.0) * span_x, oy - 20 - (i / 100.0) * span_y) for i in range(101)]
    p.append(polyline(ideal, color=POS, sw=3.0))

    # фільтрована sN/(s+N): нахил +1 до кутової частоти N, далі полиця (стеля ≈ N)
    corner = 0.58
    plateau_y = oy - 20 - corner * span_y
    filt = []
    for i in range(101):
        t = i / 100.0
        x = ox + 40 + t * span_x
        y = (oy - 20 - t * span_y) if t <= corner else plateau_y
        filt.append((x, y))
    p.append(polyline(filt, color=FIELD, sw=3.4))

    # вертикаль кутової частоти N
    cx = ox + 40 + corner * span_x
    p.append(line(cx, oy, cx, plateau_y, color=MUTED, sw=1.4, dash="4,4"))
    p.append(text(cx, oy + 18, "ω = N", size=13, color=MUTED, bold=True))

    # смуга «де живе шум» (високі частоти)
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fbe4e1" opacity="0.45"/>'
             % (cx + 6, oy - ax_h + 10, ox + ax_w - (cx + 6) - 6, ax_h - 10))
    p.append(text((cx + ox + ax_w) / 2, oy - ax_h + 34, "тут живе шум", size=13, color=POS, bold=True))

    # стеля фільтра
    p.append(text(ox + ax_w - 8, plateau_y - 10, "стеля ≈ Kd·N", size=12, color=FIELD, anchor="end", bold=True))
    p.append(text(ox + 40 + 0.30 * span_x, oy - 20 - 0.30 * span_y - 10,
                  "нахил +1", size=12, color=POS, bold=True, anchor="start"))

    p.append(legend_row(ox + 8, oy - ax_h - 4, POS, "чиста похідна s (росте без стелі)"))
    p.append(legend_row(ox + 340, oy - ax_h - 4, FIELD, "фільтрована sN/(s+N)"))
    render(os.path.join(OUT, "derivative-gain.svg"), W, H, *p)


# ── 2: N як компроміс — мала N (сильний фільтр) проти великої N (майже чиста s) ──
def fig_filter_tradeoff():
    W, H = 760, 360
    ox, oy = 96, 288
    ax_w, ax_h = 600, 236
    p = axes(ox, oy, ax_w, ax_h, xlabel="частота (log ω)", ylabel="підсилення |G| (log)")

    span_x = ax_w - 70
    span_y = ax_h - 56

    def curve(corner, color, sw):
        plate = oy - 20 - corner * span_y
        pts = []
        for i in range(101):
            t = i / 100.0
            x = ox + 40 + t * span_x
            y = (oy - 20 - t * span_y) if t <= corner else plate
            pts.append((x, y))
        return polyline(pts, color=color, sw=sw), plate, ox + 40 + corner * span_x

    # мала N — низька полиця, сильно ріже шум, але й корисну похідну «згинає» рано
    c_lo, plate_lo, x_lo = curve(0.34, NEG, 3.2)
    # велика N — висока полиця, майже чиста похідна, майже не ріже шум
    c_hi, plate_hi, x_hi = curve(0.80, POS, 3.2)
    p.append(c_lo)
    p.append(c_hi)

    for xx, plate, lab, col in [(x_lo, plate_lo, "мала N", NEG), (x_hi, plate_hi, "велика N", POS)]:
        p.append(line(xx, oy, xx, plate, color=col, sw=1.2, dash="3,4"))
    p.append(text(x_lo, oy + 18, "мала N", size=12, color=NEG, bold=True))
    p.append(text(x_hi, oy + 18, "велика N", size=12, color=POS, bold=True))

    p.append(mtext(ox + ax_w - 8, plate_lo + 16, "сильно ріже шум,\nале й корисне гне рано",
                   size=11, color=NEG, anchor="end"))
    p.append(mtext(ox + ax_w - 8, plate_hi - 18, "майже чиста похідна,\nшум майже не ріже",
                   size=11, color=POS, anchor="end"))

    p.append(legend_row(ox + 8, oy - ax_h - 4, NEG, "мала N: демпфування чисте, шуму мало"))
    p.append(legend_row(ox + 360, oy - ax_h - 4, POS, "велика N: демпфування різке, шуму багато"))
    render(os.path.join(OUT, "filter-tradeoff.svg"), W, H, *p)


# ── 3: демпфування другого порядку — Kd рухає систему від коливань до перезгасання ──
def fig_damping_family():
    W, H = 760, 360
    ox, oy = 92, 292
    ax_w, ax_h = 610, 244
    p = axes(ox, oy, ax_w, ax_h, ylabel="вихід y")

    top = oy - ax_h + 26
    base = oy
    unit = (base - top) / 1.98          # px на y=1.0; лишаємо запас зверху під переліт + легенду
    setpoint_y = base - unit            # рівень завдання (y-plot = 1)

    # завдання (пунктир)
    p.append(line(ox, setpoint_y, ox + ax_w - 6, setpoint_y, color=MUTED, sw=1.4, dash="6,5"))
    p.append(text(ox + ax_w - 6, setpoint_y - 8, "завдання", size=11, color=MUTED, anchor="end"))

    T = 3.2
    def resp(zeta, wn=3.4):
        pts = []
        for i in range(241):
            t = T * i / 240.0
            if zeta < 1.0:
                wd = wn * math.sqrt(1 - zeta * zeta)
                y = 1 - math.exp(-zeta * wn * t) * (math.cos(wd * t) + (zeta * wn / wd) * math.sin(wd * t))
            elif abs(zeta - 1.0) < 1e-6:
                y = 1 - math.exp(-wn * t) * (1 + wn * t)
            else:
                s1 = -wn * (zeta - math.sqrt(zeta * zeta - 1))
                s2 = -wn * (zeta + math.sqrt(zeta * zeta - 1))
                A = s2 / (s2 - s1)
                B = -s1 / (s2 - s1)
                y = 1 + A * math.exp(s1 * t) + B * math.exp(s2 * t)
            x = ox + (ax_w - 40) * (t / T) + 6
            pts.append((x, base - unit * y))
        return pts

    # ζ малий (мало D) — переліт і коливання; ζ≈0.7 влучно; ζ>1 перезгасання (забагато D — мляво)
    p.append(polyline(resp(0.25), color=POS, sw=2.8))
    p.append(polyline(resp(0.7), color=FIELD, sw=3.0))
    p.append(polyline(resp(2.2), color=NEG, sw=2.6, dash="7,5"))

    p.append(legend_row(ox + 12, top - 6, POS, "ζ≈0.25  мало D: переліт, гойдання"))
    p.append(legend_row(ox + 12, top + 12, FIELD, "ζ≈0.7  влучно: швидко, майже без перельоту"))
    p.append(legend_row(ox + 372, top - 6, NEG, "ζ>1  забагато D: мляво"))
    render(os.path.join(OUT, "damping-family.svg"), W, H, *p)


# ── 4: фаза — похідна веде на +90°, інтеграл відстає на −90° (фазори) ──────────
def fig_phase_lead_lag():
    W, H = 720, 366
    cx, cy, R = 360, 176, 104

    p = []
    # два кола-циферблати: ліворуч інтеграл, праворуч похідна
    def phasor(cxx, title, ang_deg, color, note):
        q = [circle(cxx, cy, R, fill=BG, stroke=MUTED, sw=1.4)]
        # осі
        q.append(line(cxx - R - 8, cy, cxx + R + 8, cy, color=MUTED, sw=1.0))
        q.append(line(cxx, cy - R - 8, cxx, cy + R + 8, color=MUTED, sw=1.0))
        # опорний вектор (сигнал помилки) — вправо
        q.append(arrow(cxx, cy, cxx + R - 6, cy, color=INK, sw=2.4))
        q.append(text(cxx + R - 4, cy + 18, "e", size=13, color=INK, bold=True, anchor="start"))
        # вектор дії під кутом
        a = math.radians(ang_deg)
        ex = cxx + (R - 6) * math.cos(-a)
        ey = cy + (R - 6) * math.sin(-a)
        q.append(arrow(cxx, cy, ex, ey, color=color, sw=3.0))
        # дуга кута
        q.append(text(cxx, cy - R - 18, title, size=14, color=color, bold=True))
        q.append(text(cxx, cy + R + 30, note, size=12, color=MUTED))
        return q

    p += phasor(188, "похідна D: +90°", 90, FIELD, "діє РАНІШЕ → випередження")
    p += phasor(532, "інтеграл I: −90°", -90, POS, "діє ПІЗНІШЕ → відставання")

    p.append(text(360, 352, "P сидить на 0° (у фазі з помилкою); D тягне фазу вгору, I — вниз",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "phase-lead-lag.svg"), W, H, *p)


# ── 5: виведення реальної похідної — каскад s × ФНЧ + карта нуль/полюс ──────
def fig_derivative_cascade():
    """Для вставки math-derivative-filter: ідеальний диференціатор s послідовно
    з однополюсним ФНЧ N/(s+N) дає реальну похідну; праворуч — карта нуля й полюса."""
    W, H = 820, 300
    p = []

    # ── ліворуч: ланцюг блоків ──
    by = 96
    bh = 62
    # блок 1: диференціатор s
    b1, w1, _ = textbox(150, by, "диференціатор\ns", size=15, pad=14,
                        fill="#eaf0fd", stroke=NEG, sw=2.0, bold=True, color=NEG)
    p.append(b1)
    # блок 2: ФНЧ N/(s+N)
    b2, w2, _ = textbox(360, by, "ФНЧ 1-го порядку\nN/(s + N)", size=15, pad=14,
                        fill="#eafaf1", stroke=FIELD, sw=2.0, bold=True, color=FIELD)
    p.append(b2)

    # стрілки входу/виходу
    p.append(arrow(52, by, 150 - w1 / 2 - 4, by, color=INK, sw=2.2))
    p.append(text(50, by - 12, "e", size=15, color=INK, bold=True, anchor="middle"))
    p.append(arrow(150 + w1 / 2 + 4, by, 360 - w2 / 2 - 4, by, color=INK, sw=2.2))
    p.append(arrow(360 + w2 / 2 + 4, by, 360 + w2 / 2 + 70, by, color=INK, sw=2.2))
    p.append(text(360 + w2 / 2 + 92, by - 12, "u_D", size=15, color=INK, bold=True, anchor="middle"))

    # добуток під ланцюгом
    p.append(text(260, by + 78, "D(s) = Kd · s · N/(s+N) = Kd·s / (1 + s/N)",
                  size=14, color=INK, bold=True, anchor="middle"))
    p.append(text(260, by + 104, "нуль у 0 (це похідна) · полюс у −N (це фільтр)",
                  size=12, color=MUTED, anchor="middle"))

    # ── праворуч: карта нуль/полюс (s-площина) ──
    cx0, cy0 = 662, 150
    axr = 118
    # осі
    p.append(line(cx0 - axr, cy0, cx0 + axr, cy0, color=INK, sw=1.4))
    p.append(arrow(cx0 + axr - 14, cy0, cx0 + axr, cy0, color=INK, sw=1.4))
    p.append(line(cx0, cy0 + axr - 20, cx0, cy0 - axr + 20, color=INK, sw=1.4))
    p.append(arrow(cx0, cy0 - axr + 34, cx0, cy0 - axr + 20, color=INK, sw=1.4))
    p.append(text(cx0 + axr + 4, cy0 + 16, "Re", size=12, color=MUTED, anchor="start"))
    p.append(text(cx0 + 6, cy0 - axr + 24, "Im", size=12, color=MUTED, anchor="start"))

    # нуль у початку координат (кружечок)
    p.append(circle(cx0, cy0, 9, fill=BG, stroke=NEG, sw=2.6))
    p.append(text(cx0 + 4, cy0 - 16, "нуль (s=0)", size=12, color=NEG, bold=True, anchor="start"))

    # полюс у −N (хрестик) ліворуч
    px = cx0 - 78
    p.append(line(px - 8, cy0 - 8, px + 8, cy0 + 8, color=FIELD, sw=3.0))
    p.append(line(px - 8, cy0 + 8, px + 8, cy0 - 8, color=FIELD, sw=3.0))
    p.append(text(px, cy0 + 26, "полюс s = −N", size=12, color=FIELD, bold=True, anchor="middle"))
    p.append(line(px, cy0, px, cy0 + 40, color=FIELD, sw=1.0, dash="3,4"))

    render(os.path.join(OUT, "derivative-cascade.svg"), W, H, *p)


# ── 6: фаза реальної похідної — ідеал рівно +90°, фільтр забирає вгорі ──────
def fig_phase_price():
    """Для вставки: фазова характеристика. Ідеальна похідна дає +90° на всіх
    частотах; реальна sN/(s+N) починає з +90°, а вище N спадає до 0° — фазова ціна."""
    W, H = 760, 360
    ox, oy = 92, 300
    ax_w, ax_h = 610, 250
    p = axes(ox, oy, ax_w, ax_h, xlabel="частота (log ω)")

    span_x = ax_w - 60
    # вісь фази: 0°…+90°
    y90 = oy - (ax_h - 40)          # рівень +90°
    y45 = oy - (ax_h - 40) / 2
    y0 = oy
    # мітки градусів
    for yy, lab in [(y0, "0°"), (y45, "45°"), (y90, "90°")]:
        p.append(line(ox - 4, yy, ox + 4, yy, color=MUTED, sw=1.2))
        p.append(text(ox - 10, yy + 4, lab, size=11, color=MUTED, anchor="end"))
    p.append(text(ox + 2, y90 - 12, "фаза (випередження)", size=12, color=MUTED, anchor="start"))

    # ідеальна похідна: рівно +90° всюди
    p.append(polyline([(ox + 10, y90), (ox + 10 + span_x, y90)], color=POS, sw=3.0, dash="7,5"))

    # реальна sN/(s+N): фаза = 90° − atan(ω/N); малюємо в log-осі ω
    # x відображає log(ω); кутова частота N — де фаза = 45°
    corner = 0.56                    # позиція ω = N на осі
    pts = []
    for i in range(161):
        t = i / 160.0
        x = ox + 10 + t * span_x
        # log-декади відносно N: dec = (t - corner)*range
        dec = (t - corner) * 6.0     # ~6 декад по всій осі
        w_over_N = 10.0 ** dec
        phase = 90.0 - math.degrees(math.atan(w_over_N))   # 90° внизу ω, →0° вгорі
        y = y90 + (1.0 - phase / 90.0) * (y0 - y90)         # phase=90→y90(верх), 0→y0(низ)
        pts.append((x, y))
    p.append(polyline(pts, color=FIELD, sw=3.4))

    # вертикаль ω = N (де фаза реальної = 45°)
    cxN = ox + 10 + corner * span_x
    p.append(line(cxN, oy, cxN, y45, color=MUTED, sw=1.4, dash="4,4"))
    p.append(text(cxN, oy + 18, "ω = N", size=13, color=MUTED, bold=True))
    p.append(circle(cxN, y45, 4, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(text(cxN + 8, y45 - 8, "тут уже лише +45°", size=11, color=FIELD, bold=True, anchor="start"))

    # анотації
    p.append(text(ox + 10 + 0.16 * span_x, y90 - 10, "ідеал: +90° всюди",
                  size=12, color=POS, bold=True, anchor="start"))
    p.append(mtext(ox + 10 + span_x, y0 + 44,
                   "вище N фільтр забирає\nвипередження — фазова ціна",
                   size=11, color=FIELD, anchor="end"))

    p.append(legend_row(ox + 10, oy - ax_h - 4, POS, "ідеальна похідна s: рівно +90°", dash="7,5"))
    p.append(legend_row(ox + 350, oy - ax_h - 4, FIELD, "реальна sN/(s+N): спадає вище N"))
    render(os.path.join(OUT, "phase-price.svg"), W, H, *p)


if __name__ == "__main__":
    fig_derivative_gain()
    fig_filter_tradeoff()
    fig_damping_family()
    fig_phase_lead_lag()
    fig_derivative_cascade()
    fig_phase_price()
    print("OK: derivative-gain, filter-tradeoff, damping-family, phase-lead-lag, "
          "derivative-cascade, phase-price")
