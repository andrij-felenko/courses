# -*- coding: utf-8 -*-
"""Фігури до теми «Вага».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def hatch(x0, y0, x1, y1, step=16, color=MUTED, sw=1.0, dx=9, dy=9):
    """Штрихування вздовж лінії (підлога/земля)."""
    out = [line(x0, y0, x1, y1, color=color, sw=1.6)]
    n = int(math.hypot(x1 - x0, y1 - y0) // step)
    if n <= 0:
        return "".join(out)
    ux, uy = (x1 - x0) / (n * step), (y1 - y0) / (n * step)
    for i in range(n + 1):
        px, py = x0 + ux * step * i, y0 + uy * step * i
        out.append(line(px, py, px - dx, py + dy, color=color, sw=sw))
    return "".join(out)


def person(cx, base_y, col=INK, h=120):
    """Схематична фігурка людини, ноги на base_y."""
    head_r = h * 0.16
    hy = base_y - h
    out = [circle(cx, hy + head_r, head_r, fill="#ffffff", stroke=col, sw=2.2)]
    ty = hy + 2 * head_r
    out.append(line(cx, ty, cx, base_y - h * 0.34, color=col, sw=2.6))              # тулуб
    out.append(line(cx, ty + 6, cx - h * 0.19, ty + h * 0.24, color=col, sw=2.6))   # руки
    out.append(line(cx, ty + 6, cx + h * 0.19, ty + h * 0.24, color=col, sw=2.6))
    out.append(line(cx, base_y - h * 0.34, cx - h * 0.15, base_y, color=col, sw=2.6))  # ноги
    out.append(line(cx, base_y - h * 0.34, cx + h * 0.15, base_y, color=col, sw=2.6))
    return "".join(out)


def coil_v(x, y0, y1, n, amp, color=INK, sw=2.0):
    """Вертикальна пружинка-зигзаг."""
    pts = [(x, y0)]
    seg = (y1 - y0) / (2 * n)
    for i in range(1, 2 * n):
        pts.append((x + (amp if i % 2 else -amp), y0 + seg * i))
    pts.append((x, y1))
    return polyline(pts, color=color, sw=sw)


def scale_box(cx, top, w=150, h=30, reading=None, tint="#eef2fb"):
    """Схематичні терези-платформа з віконцем показу."""
    out = [rect(cx - w / 2, top, w, h, fill=tint, stroke=INK, sw=2, rx=6)]
    ww = 54
    out.append(rect(cx - ww / 2, top + h * 0.5 - 9, ww, 18, fill="#ffffff", stroke=MUTED, sw=1.3, rx=3))
    if reading is not None:
        out.append(text(cx, top + h * 0.5 + 5, reading, size=11, bold=True, color=INK))
    return "".join(out)


# ── Фігура 1: терези показують силу опори, а не тяжіння ────────────────────────
def fig_scale_reads_support():
    W, H = 980, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Що насправді міряють терези: не тяжіння, а поштовх опори", size=17, bold=True))

    cx = 330
    base = 420
    # земля під платформою
    f.append(hatch(150, base + 30, 520, base + 30, step=18, color=NEG))
    # платформа терезів
    f.append(scale_box(cx, base, w=156, h=30, reading="N"))
    f.append(person(cx, base, col=INK, h=128))

    # напис над людиною — тяжіння діє на кожну частинку
    f.append(text(cx, base - 168, "тяжіння тягне кожну частинку тіла рівномірно — саме собою невідчутне",
                  size=12.5, color=MUTED))
    # розподілені тонкі стрілочки крізь тулуб
    for dx in (-20, 0, 20):
        f.append(arrow(cx + dx, base - 96, cx + dx, base - 70, color=MUTED, sw=1.2))

    # головна стрілка m·g (ліворуч)
    mgx = cx - 118
    f.append(arrow(mgx, base - 96, mgx, base - 8, color=INK, sw=3.2))
    f.append(text(mgx - 10, base - 54, "m·g", size=15, bold=True, color=INK, anchor="end"))
    f.append(text(mgx - 10, base - 36, "тяжіння", size=11, color=MUTED, anchor="end"))

    # стрілка N — реакція опори (праворуч, від платформи вгору у стопи)
    nx = cx + 100
    f.append(arrow(nx, base - 2, nx, base - 78, color=FIELD, sw=3.4))
    f.append(mtext(nx + 12, base - 66, ["N — сила", "реакції опори"], size=12.5, bold=True,
                   color=FIELD, anchor="start", lh=1.25))

    # третій закон — тіло тисне на майданчик
    f.append(arrow(cx, base + 2, cx, base + 20, color=POS, sw=2.6))
    f.append(text(cx, base + 58, "тіло тисне на майданчик так само (3-й закон)", size=11.5, color=POS))

    # права панель — рівність у спокої
    b, w, h = textbox(770, 250, "у спокої:  N = m·g", size=16, pad=12,
                      fill="#eaf7ee", stroke=FIELD, sw=1.6, bold=True)
    f.append(b)
    f.append(fitbox(628, 300, 284, 78,
                    ["пружина всередині ловить силу N,", "з якою тіло тисне на майданчик —",
                     "а не тяжіння. Тому в спокої", "прилад показує вагу тяжіння m·g."],
                    size=12.5, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    b, w, h = textbox(W / 2, H - 28,
                      "тяжіння невідчутне; вага, яку ти відчуваєш і читаєш на шкалі, — це поштовх опори N",
                      size=13.5, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "scale-reads-support.svg"), W, H, *f)


# ── Фігура 2: вага в ліфті — чотири стани ──────────────────────────────────────
def fig_elevator_weight():
    W, H = 1260, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Вага в ліфті: уявна вага N = m·(g + a)   (людина 70 кг)", size=17, bold=True))

    # 4 панелі
    panels = [
        (185, "спокій / рівний хід", "a = 0",       686, FIELD, "#eaf7ee", "up0"),
        (485, "розгін угору",        "a = +2 м/с²", 826, POS,   "#fdecea", "up"),
        (785, "розгін униз",         "a = −2 м/с²", 546, NEG,   "#eaf0fd", "down"),
        (1075, "вільне падіння",     "a = −g",        0, MUTED, "#f4f6f8", "fall"),
    ]
    box_top, box_h, box_w = 96, 300, 200
    floor_y = box_top + box_h - 24
    Nmax = 826.0
    for cx, title, atxt, N, col, tint, kind in panels:
        # кабіна
        f.append(rect(cx - box_w / 2, box_top, box_w, box_h, fill="#ffffff", stroke=INK, sw=2, rx=8))
        f.append(text(cx, box_top - 30, title, size=13.5, bold=True, color=col))
        f.append(text(cx, box_top - 12, atxt, size=12, color=INK))
        # підлога кабіни
        f.append(line(cx - box_w / 2 + 8, floor_y, cx + box_w / 2 - 8, floor_y, color=INK, sw=2))
        f.append(hatch(cx - box_w / 2 + 8, floor_y + 1, cx + box_w / 2 - 8, floor_y + 1,
                       step=16, color=MUTED, dx=7, dy=7))

        if kind == "fall":
            # людина ширяє над підлогою + трос обірвано
            pbase = floor_y - 46
            f.append(person(cx, pbase, col=INK, h=104))
            f.append(text(cx, floor_y - 6, "ширяє — опори немає", size=11, color=MUTED))
            # m·g лишається
            f.append(arrow(cx - 66, pbase - 70, cx - 66, pbase - 18, color=INK, sw=2.6))
            f.append(text(cx - 74, pbase - 44, "m·g", size=12, bold=True, color=INK, anchor="end"))
            # N = 0
            f.append(text(cx + 64, pbase - 40, "N = 0", size=13, bold=True, color=col))
        else:
            pbase = floor_y
            # маленькі терези під ногами
            f.append(rect(cx - 40, floor_y - 12, 80, 12, fill=tint, stroke=col, sw=1.8, rx=3))
            f.append(person(cx, floor_y - 12, col=INK, h=104))
            # m·g — однакова довжина в усіх (тяжіння не міняється)
            f.append(arrow(cx - 66, pbase - 150, cx - 66, pbase - 98, color=INK, sw=2.6))
            f.append(text(cx - 74, pbase - 128, "m·g", size=12, bold=True, color=INK, anchor="end"))
            # N — довжина ∝ N (реакція опори)
            nlen = 30 + 118 * (N / Nmax)
            f.append(arrow(cx + 60, floor_y - 12, cx + 60, floor_y - 12 - nlen, color=col, sw=3.2))
            f.append(text(cx + 68, floor_y - 12 - nlen / 2, "N", size=13, bold=True, color=col, anchor="start"))

        # стрілка прискорення кабіни збоку
        if kind == "up":
            f.append(arrow(cx - box_w / 2 - 22, box_top + 150, cx - box_w / 2 - 22, box_top + 70, color=POS, sw=3.4))
            f.append(text(cx - box_w / 2 - 30, box_top + 120, "a", size=14, bold=True, color=POS, anchor="end"))
        elif kind == "down":
            f.append(arrow(cx - box_w / 2 - 22, box_top + 70, cx - box_w / 2 - 22, box_top + 150, color=NEG, sw=3.4))
            f.append(text(cx - box_w / 2 - 30, box_top + 120, "a", size=14, bold=True, color=NEG, anchor="end"))
        elif kind == "fall":
            f.append(arrow(cx - box_w / 2 - 22, box_top + 70, cx - box_w / 2 - 22, box_top + 168, color=MUTED, sw=3.4))
            f.append(text(cx - box_w / 2 - 30, box_top + 130, "a = g", size=12, bold=True, color=MUTED, anchor="end"))
            f.append(text(cx, box_top + 20, "трос обірвано", size=11, italic=True, color=POS))

        # показ терезів під кабіною
        rlbl = ("%d Н" % N) if N else "0 Н"
        kg = ("≈ %d кг" % round(N / 9.8)) if N else "0"
        b, w, h = textbox(cx, box_top + box_h + 40, ["терези: " + rlbl, kg],
                          size=13, pad=9, fill=tint, stroke=col, sw=1.6, color=col, bold=True)
        f.append(b)

    b, w, h = textbox(W / 2, H - 26,
                      "важить прискорення опори, а не напрям руху: угору на сталій швидкості — вага звичайна; тіло скрізь те саме — гуляє лише N",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "elevator-weight.svg"), W, H, *f)


# ── Фігура 3: пружинні терези (вага) проти коромисла (маса) ────────────────────
def fig_spring_vs_balance():
    W, H = 1120, 620
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Пружина міряє вагу, коромисло — масу", size=17, bold=True))

    f.append(line(W / 2, 66, W / 2, H - 96, color=MUTED, sw=1.2, dash="6 7"))

    # ── ЛІВОРУЧ: пружинні терези, два місця ──
    f.append(fitbox(70, 62, 430, 32, "ПРУЖИННІ терези — читають силу опори (вагу)",
                    size=14, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))

    def spring_scene(cx, top, place, reading, col):
        out = [text(cx, top - 6, place, size=13.5, bold=True, color=col)]
        out.append(hatch(cx - 70, top + 6, cx + 70, top + 6, step=16, color=MUTED, dx=7, dy=-8))
        out.append(coil_v(cx, top + 6, top + 70, 6, 11, color=col, sw=2.2))
        out.append(rect(cx - 30, top + 70, 60, 44, fill="#eef2fb", stroke=INK, sw=2, rx=5))
        out.append(text(cx, top + 96, "70 кг", size=13, bold=True, color=INK))
        b, w, h = textbox(cx + 132, top + 58, "показує " + reading, size=13, pad=9,
                          fill="#fdf0ee", stroke=POS, sw=1.4, color=POS, bold=True)
        out.append(b)
        return "".join(out)

    f.append(spring_scene(200, 150, "на Землі  (g = 9.8)", "686 Н", POS))
    f.append(spring_scene(200, 340, "на Місяці  (g = 1.62)", "113 Н", "#a9946b"))
    f.append(fitbox(60, 470, 430, 46,
                    ["розтяг пружини ∝ силі опори:", "залежить від g — на Місяці показує вшестеро менше"],
                    size=12.5, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    # ── ПРАВОРУЧ: коромислові терези ──
    f.append(fitbox(620, 62, 440, 32, "КОРОМИСЛОВІ терези — порівнюють маси",
                    size=14, fill="#eaf7ee", stroke=FIELD, sw=1.6, bold=True, color=FIELD))

    def balance(cx, top, place, col):
        out = [text(cx, top - 6, place, size=13.5, bold=True, color=col)]
        # стійка
        out.append(line(cx, top + 8, cx, top + 84, color=INK, sw=3))
        # коромисло (рівне)
        beam_y = top + 16
        out.append(line(cx - 96, beam_y, cx + 96, beam_y, color=INK, sw=3))
        out.append(circle(cx, beam_y, 5, fill="#ffffff", stroke=INK, sw=2))
        # опора-трикутник
        out.append(polyline([(cx - 16, top + 84), (cx + 16, top + 84), (cx, top + 60), (cx - 16, top + 84)],
                            color=INK, sw=2))
        # ліва шалька — невідоме тіло
        out.append(line(cx - 96, beam_y, cx - 96, beam_y + 34, color=MUTED, sw=1.4))
        out.append(rect(cx - 122, beam_y + 34, 52, 34, fill="#eef2fb", stroke=INK, sw=2, rx=4))
        out.append(text(cx - 96, beam_y + 55, "70 кг", size=12, bold=True, color=INK))
        # права шалька — різноважки
        out.append(line(cx + 96, beam_y, cx + 96, beam_y + 34, color=MUTED, sw=1.4))
        out.append(rect(cx + 74, beam_y + 34, 44, 22, fill="#eaf7ee", stroke=FIELD, sw=2, rx=3))
        out.append(rect(cx + 80, beam_y + 20, 32, 14, fill="#eaf7ee", stroke=FIELD, sw=2, rx=2))
        out.append(text(cx + 150, beam_y + 44, "різно-", size=11, color=FIELD, anchor="start"))
        out.append(text(cx + 150, beam_y + 58, "важки", size=11, color=FIELD, anchor="start"))
        return "".join(out)

    f.append(balance(760, 150, "на Землі", FIELD))
    f.append(balance(760, 340, "на Місяці", "#a9946b"))
    f.append(fitbox(600, 470, 470, 46,
                    ["g діє на обидві шальки однаково й скорочується:", "рівновага на тих самих різноважках — і на Землі, і на Місяці"],
                    size=12.5, fill="#eaf7ee", stroke=FIELD, sw=1.3, color=FIELD))

    b, w, h = textbox(W / 2, H - 34,
                      ["пружинні терези читають m·g — тому міряють ВАГУ й залежать від місця;",
                       "коромисло порівнює тіло з різноважками — g зникає, тому воно міряє МАСУ, скрізь однаково"],
                      size=13, pad=12, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "spring-vs-balance.svg"), W, H, *f)


# ── Профіль руху ліфта (та сама S-крива, що в коді вставки) ────────────────────
def _ride_series(n=480):
    a_max, t_jerk, t_hold, t_cruise = 1.2, 0.8, 0.6, 3.0
    t1 = t_jerk; t2 = t1 + t_hold; t3 = t2 + t_jerk; t4 = t3 + t_cruise
    t5 = t4 + t_jerk; t6 = t5 + t_hold; t7 = t6 + t_jerk; t_end = t7 + 0.6

    def acc(t):
        if t < t1:  return  a_max * (t / t_jerk)
        if t < t2:  return  a_max
        if t < t3:  return  a_max * (1 - (t - t2) / t_jerk)
        if t < t4:  return  0.0
        if t < t5:  return -a_max * ((t - t4) / t_jerk)
        if t < t6:  return -a_max
        if t < t7:  return -a_max * (1 - (t - t6) / t_jerk)
        return 0.0

    G = 9.80665
    dt = t_end / n
    ts, ns, vs = [], [], []
    t, v = 0.0, 0.0
    for _ in range(n + 1):
        ts.append(t); ns.append((G + acc(t)) / G); vs.append(v)
        v += acc(t) * dt; t += dt
    return ts, ns, vs, t_end, t3, t4     # t3 = кінець розгону, t4 = початок гальмування


# ── Фігура 4: показ терезів упродовж усієї поїздки ліфтом ──────────────────────
def fig_elevator_ride():
    W, H = 1120, 680
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Показ терезів упродовж однієї поїздки ліфтом (людина 70 кг)", size=17, bold=True))

    ts, ns, vs, T, tA, tB = _ride_series()
    X0, X1 = 118, 1052
    def X(t): return X0 + (t / T) * (X1 - X0)

    # спільна зелена смуга «рівний хід» на обидві панелі
    xa, xb = X(tA), X(tB)
    f.append(rect(xa, 92, xb - xa, 494, fill="#eafaf0", stroke='none', sw=0, rx=0))

    # заголовки фаз (окремий рядок, щоб не налазили на криві)
    f.append(text((X0 + xa) / 2, 84, "розгін угору", size=12.5, bold=True, color=POS))
    f.append(text((xa + xb) / 2, 84, "рівний хід (a = 0)", size=12.5, bold=True, color=FIELD))
    f.append(text((xb + X1) / 2, 84, "гальмування", size=12.5, bold=True, color=NEG))

    # ── Панель A: уявна вага N/mg ──
    Atop, Abot = 108, 300
    vminA, vmaxA = 0.84, 1.16
    def YA(v): return Abot - (v - vminA) / (vmaxA - vminA) * (Abot - Atop)
    f.append(rect(X0, Atop, X1 - X0, Abot - Atop, fill="none", stroke=MUTED, sw=1.2))
    f.append(text(X0 - 8, Atop - 6, "вага N / mg  (у частках звичайної ваги)", size=12, color=INK, anchor="start"))
    for yt in (0.9, 1.0, 1.1):
        yy = YA(yt)
        f.append(line(X0, yy, X1, yy, color=("#c9ccd1" if yt == 1.0 else "#e9ebef"),
                      sw=(1.3 if yt == 1.0 else 1.0), dash=("6 5" if yt == 1.0 else None)))
        f.append(text(X0 - 10, yy + 4, "%.1f" % yt, size=11, color=MUTED, anchor="end"))
    f.append(polyline([(X(t), YA(v)) for t, v in zip(ts, ns)], color=INK, sw=2.8))
    # позначки піку й провалу
    f.append(text(X(1.0), YA(1.122) - 12, "пік 1.12 g — важчаєш", size=12, bold=True, color=POS))
    f.append(text(X(6.3), YA(0.878) + 22, "провал 0.88 g — легшаєш", size=12, bold=True, color=NEG))
    f.append(text((xa + xb) / 2, YA(1.0) - 12, "рівно 1.00 g", size=12, bold=True, color=FIELD))

    # ── Панель B: швидкість ──
    Btop, Bbot = 372, 566
    vmaxB = 1.9
    def YB(v): return Bbot - v / vmaxB * (Bbot - Btop)
    f.append(rect(X0, Btop, X1 - X0, Bbot - Btop, fill="none", stroke=MUTED, sw=1.2))
    f.append(text(X0 - 8, Btop - 6, "швидкість кабіни v, м/с", size=12, color=INK, anchor="start"))
    for yt in (0.0, 0.5, 1.0, 1.5):
        yy = YB(yt)
        f.append(line(X0, yy, X1, yy, color=("#c9ccd1" if yt == 0 else "#e9ebef"),
                      sw=(1.3 if yt == 0 else 1.0)))
        f.append(text(X0 - 10, yy + 4, "%.1f" % yt, size=11, color=MUTED, anchor="end"))
    f.append(polyline([(X(t), YB(v)) for t, v in zip(ts, vs)], color=NEG, sw=2.8))
    f.append(text((xa + xb) / 2, YB(1.68) - 12, "швидкість найбільша — а вага звичайна", size=12, bold=True, color=FIELD))

    # вісь часу
    for tt in range(0, 9):
        xx = X(tt)
        f.append(line(xx, Bbot, xx, Bbot + 6, color=MUTED, sw=1.2))
        f.append(text(xx, Bbot + 22, "%d" % tt, size=11, color=MUTED))
    f.append(text(X1, Bbot + 22, "  час, с", size=11.5, color=INK, anchor="start"))

    # вертикальні межі фаз крізь обидві панелі
    for xx in (xa, xb):
        f.append(line(xx, Atop, xx, Bbot, color=FIELD, sw=1.2, dash="4 5"))

    b, w, h = textbox(W / 2, H - 40,
                      ["ліфт їде вгору ВСЮ поїздку (v ≥ 0), та вага змінюється лише коли міняється ШВИДКІСТЬ:",
                       "важчаєш на розгоні, звичайна вага на рівному ході (хоч швидкість там найбільша), легшаєш на гальмуванні"],
                      size=12.5, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "elevator-ride.svg"), W, H, *f)


# ── Фігура 5: буденні маневри, виражені в частках g ────────────────────────────
def fig_g_maneuvers():
    W, H = 1080, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Уявна вага в буденних маневрах — у частках звичайної ваги (g)", size=17, bold=True))

    rows = [
        ("Вільне падіння / невагомість", 0.00, MUTED, ""),
        ("Ліфт гальмує перед зупинкою",  0.88, NEG,   ""),
        ("Стоїш на землі",               1.00, INK,   ""),
        ("Ліфт розганяється вгору",      1.12, POS,   ""),
        ("Різке гальмування авто",       1.35, POS,   "(бічне ~0.9 g)"),
        ("Гірки, низ великої петлі",     4.00, POS,   ""),
        ("Винищувач виходить із піке",   5.00, POS,   ""),
    ]
    Lx = 372                      # права межа підписів ліворуч
    B0 = 388                      # початок стовпчиків
    scale = 128                   # px на одну g
    y0, dy = 96, 60
    x1g = B0 + scale * 1.0

    # лінія «1 g» на весь графік
    f.append(line(x1g, 72, x1g, y0 + dy * len(rows) - 18, color=INK, sw=1.4, dash="6 5"))
    f.append(text(x1g, 66, "1 g — звичайна вага", size=12.5, bold=True, color=INK))

    for i, (name, val, col, note) in enumerate(rows):
        cy = y0 + dy * i
        f.append(text(Lx, cy + 5, name, size=13, color=INK, anchor="end"))
        bar_w = scale * val
        if val > 0.02:
            f.append(rect(B0, cy - 13, bar_w, 26, fill=("#fdecea" if col is POS else
                          "#eaf0fd" if col is NEG else "#eef1f4"), stroke=col, sw=1.8, rx=4))
        else:
            f.append(circle(B0, cy, 4, fill=col, stroke=col, sw=1))
        lbl = "%.2f g" % val
        f.append(text(B0 + bar_w + 12, cy + 5, lbl, size=13, bold=True, color=col, anchor="start"))
        if note:
            f.append(text(B0 + bar_w + 84, cy + 5, note, size=11, color=MUTED, anchor="start"))

    b, w, h = textbox(W / 2, H - 34,
                      "усе це — один поштовх опори N на одиницю маси: більший за 1 g притискає (важчаєш), менший відпускає, нуль — невагомість",
                      size=12.5, pad=11, fill="#eef2fb", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "g-maneuvers.svg"), W, H, *f)


# ── Фігура 6: Арістотелів світ природних місць ──────────────────────────────────
def fig_hist_natural_place():
    W, H = 1040, 760
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Арістотелів світ природних місць чотирьох стихій", size=17, bold=True))

    cx, cy = 260, 310
    f.append(text(cx, 96, "Світ Арістотеля: концентричні природні місця", size=13.5, bold=True, color=INK))

    r_fire, r_air, r_water, r_earth = 190, 145, 102, 55
    f.append(circle(cx, cy, r_fire, fill="#fdecea", stroke=POS, sw=2))
    f.append(circle(cx, cy, r_air, fill="#f4f6f8", stroke=MUTED, sw=2))
    f.append(circle(cx, cy, r_water, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(circle(cx, cy, r_earth, fill="#a9946b", stroke=INK, sw=2))

    # легенда праворуч — колір відповідає заливці кільця
    legend = [
        ("#fdecea", POS, "Вогонь", "найлегший, лине вгору (levitas)"),
        ("#f4f6f8", MUTED, "Повітря", "легке — теж тягнеться вгору"),
        ("#eaf0fd", NEG, "Вода", "важка — тягнеться вниз (gravitas)"),
        ("#a9946b", INK, "Земля", "найважча — у самому центрі світу"),
    ]
    lx, ly0, ldy = 560, 140, 92
    f.append(text(lx, ly0 - 30, "Чотири стихії за природним місцем", size=13.5, bold=True, color=INK))
    for i, (fill, col, name, desc) in enumerate(legend):
        ly = ly0 + i * ldy
        f.append(rect(lx, ly - 11, 22, 22, fill=fill, stroke=col, sw=1.8, rx=4))
        f.append(text(lx + 34, ly, name, size=13.5, bold=True, color=col, anchor="start"))
        f.append(fitbox(lx + 34, ly + 12, 340, 34, desc, size=12, color=MUTED,
                        fill="none", stroke="none", sw=0))

    # нижні панелі: камінь (gravitas, вниз) і полум'я (levitas, вгору)
    f.append(circle(230, 590, 14, fill="#a9946b", stroke=INK, sw=2))
    f.append(text(230, 570, "камінь", size=12.5, bold=True, color=INK))
    f.append(arrow(230, 610, 230, 662, color=POS, sw=3))
    b, w, h = textbox(230, 690, ["gravitas: тягнеться вниз —", "вроджена важкість тіла"],
                      size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.4, color=POS)
    f.append(b)

    f.append(circle(680, 662, 13, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(680, 570, "полум'я", size=12.5, bold=True, color=INK))
    f.append(arrow(680, 646, 680, 594, color=FIELD, sw=3))
    b, w, h = textbox(680, 690, ["levitas: тягнеться вгору —", "вроджена легкість, не «менша вага»"],
                      size=12, pad=10, fill="#eaf7ee", stroke=FIELD, sw=1.4, color=FIELD)
    f.append(b)

    b, w, h = textbox(W / 2, H - 22,
                      "вага тут — вроджена вдача самого тіла: ніхто не тягне ззовні, тіло рухається до свого природного місця",
                      size=13, pad=11, fill="#eef2fb", stroke=NEG, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "hist-natural-place.svg"), W, H, *f)


# ── Фігура 7: три домівки ваги ───────────────────────────────────────────────
def fig_hist_weight_migrates():
    W, H = 1200, 640
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Домівка ваги переселяється: тіло → стосунок → дотик", size=17, bold=True))

    f.append(line(410, 80, 410, H - 70, color=MUTED, sw=1.2, dash="6 7"))
    f.append(line(805, 80, 805, H - 70, color=MUTED, sw=1.2, dash="6 7"))

    # ── Панель 1: Арістотель — вага всередині тіла ──
    cx1 = 205
    f.append(text(cx1, 195, "Арістотель", size=14.5, bold=True, color=POS))
    f.append(text(cx1, 213, "вага — вдача тіла", size=12, color=MUTED))
    f.append(circle(cx1, 315, 88, fill="none", stroke=POS, sw=1.8))
    f.append(person(cx1, 390, col=INK, h=140))
    b, w, h = textbox(cx1, 470, ["вага живе всередині тіла —", "вроджений нахил, як колір чи форма"],
                      size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.4, color=POS)
    f.append(b)

    # ── Панель 2: Ньютон — вага як стосунок двох тіл ──
    cx2 = 610
    f.append(text(cx2, 195, "Ньютон", size=14.5, bold=True, color=FIELD))
    f.append(text(cx2, 213, "вага — стосунок двох тіл", size=12, color=MUTED))
    f.append(circle(cx2, 260, 12, fill=INK, stroke=INK, sw=1))
    f.append(circle(cx2, 400, 46, fill="#dfe7f5", stroke=INK, sw=2))
    f.append(arrow(cx2, 275, cx2, 348, color=POS, sw=3))
    f.append(line(cx2, 348, cx2, 354, color=POS, sw=3))
    f.append(text(cx2 + 22, 312, "P = m·g", size=13.5, bold=True, color=POS, anchor="start"))
    f.append(text(cx2 - 22, 312, "через", size=10.5, color=MUTED, anchor="end"))
    f.append(text(cx2 - 22, 326, "порожнечу", size=10.5, color=MUTED, anchor="end"))
    b, w, h = textbox(cx2, 470, ["вага — сила між двома тілами;", "без другого тіла її просто немає"],
                      size=12, pad=10, fill="#eaf7ee", stroke=FIELD, sw=1.4, color=FIELD)
    f.append(b)

    # ── Панель 3: сучасне операційне означення — вага на дотику з опорою ──
    cx3 = 1000
    f.append(text(cx3, 195, "Сьогодні (операційно)", size=14.5, bold=True, color=NEG))
    f.append(text(cx3, 213, "вага — на дотику з опорою", size=12, color=MUTED))
    f.append(person(cx3, 390, col=INK, h=140))
    f.append(scale_box(cx3, 390, w=150, h=26, reading="N"))
    f.append(arrow(cx3 + 95, 388, cx3 + 95, 322, color=NEG, sw=3))
    f.append(text(cx3 + 107, 350, "N", size=14, bold=True, color=NEG, anchor="start"))
    b, w, h = textbox(cx3, 470, ["N — сила реакції опори,", "яку насправді читає прилад"],
                      size=12, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.4, color=NEG)
    f.append(b)

    b, w, h = textbox(W / 2, H - 26,
                      "одне слово, три різні домівки: вроджена вдача → стосунок двох тіл на відстані → дотик з опорою",
                      size=13, pad=11, fill="#eef2fb", stroke=INK, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "hist-weight-migrates.svg"), W, H, *f)


# ── Фігура 8: уявна вага як вектор g_eff = g − a ─────────────────────────────
def fig_apparent_weight_vector():
    W, H = 1360, 640
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Уявна вага як вектор: W = m·(g − a), g_eff = g − a", size=17, bold=True))

    f.append(line(430, 78, 430, H - 66, color=MUTED, sw=1.2, dash="6 7"))
    f.append(line(850, 78, 850, H - 66, color=MUTED, sw=1.2, dash="6 7"))

    # ── Панель A: у спокої (a = 0) ──
    Ox, Oy = 230, 130
    f.append(text(Ox, 96, "У спокої (a = 0)", size=14, bold=True, color=INK))
    f.append(circle(Ox, Oy, 4, fill=INK, stroke=INK, sw=1))
    f.append(arrow(Ox, Oy, Ox, Oy + 150, color=FIELD, sw=3.4))
    f.append(text(Ox + 16, Oy + 80, "g_eff = g", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(line(Ox, Oy + 150, Ox, Oy + 200, color=MUTED, sw=1.4, dash="4 5"))
    f.append(text(Ox, Oy + 224, "виска висить прямо вниз", size=11.5, color=MUTED))
    b, w, h = textbox(Ox, 560, ["«низ» вертикальний,", "модуль не змінений"],
                      size=12, pad=10, fill="#eaf7ee", stroke=FIELD, sw=1.4, color=FIELD)
    f.append(b)

    # ── Панель B: розгін угору (a > 0, вертикально) ──
    Bx, Oy = 640, 130
    f.append(text(Bx, 96, "Розгін угору (a > 0)", size=14, bold=True, color=INK))
    gx = Bx - 26
    f.append(circle(gx, Oy, 4, fill=INK, stroke=INK, sw=1))
    f.append(arrow(gx, Oy, gx, Oy + 140, color=INK, sw=3))
    f.append(text(gx - 14, Oy + 76, "g", size=13, bold=True, color=INK, anchor="end"))
    f.append(arrow(gx, Oy + 140, gx, Oy + 180, color=POS, sw=2.6))
    f.append(text(gx - 14, Oy + 166, "−a", size=12, bold=True, color=POS, anchor="end"))
    fx = Bx + 42
    f.append(arrow(fx, Oy, fx, Oy + 180, color=FIELD, sw=3.4))
    f.append(text(fx + 16, Oy + 100, "g_eff", size=13, bold=True, color=FIELD, anchor="start"))
    b, w, h = textbox(Bx, 560, ["g_eff подовжується,", "напрям той самий — важчаєш"],
                      size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.4, color=POS)
    f.append(b)

    # ── Панель C: боковий поштовх (гальмо / віраж) ──
    Cx, Oy = 1080, 130
    f.append(text(Cx, 96, "Боковий поштовх (гальмо/віраж)", size=13.5, bold=True, color=INK))
    f.append(circle(Cx, Oy, 4, fill=INK, stroke=INK, sw=1))
    f.append(arrow(Cx, Oy, Cx, Oy + 140, color=INK, sw=3))
    f.append(text(Cx - 14, Oy + 76, "g", size=13, bold=True, color=INK, anchor="end"))
    f.append(arrow(Cx, Oy + 140, Cx + 80, Oy + 140, color=POS, sw=2.6))
    f.append(text(Cx + 40, Oy + 158, "−a", size=12, bold=True, color=POS, anchor="middle"))
    f.append(arrow(Cx, Oy, Cx + 80, Oy + 140, color=FIELD, sw=3.4))
    f.append(text(Cx + 96, Oy + 128, "g_eff", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(Cx + 18, Oy + 200, "θ", size=13, bold=True, color=MUTED, anchor="start"))
    b, w, h = textbox(Cx, 560, ["g_eff хилиться на кут θ:", "tan θ = a / g — народжується новий «низ»"],
                      size=12, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.4, color=NEG)
    f.append(b)

    b, w, h = textbox(W / 2, H - 26,
                      "від точки підвісу відкладаємо g донизу, від його вістря — вектор −a; стрілка до кінця й є g_eff = g − a",
                      size=13, pad=11, fill="#eef2fb", stroke=INK, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "apparent-weight-vector.svg"), W, H, *f)


# ── Фігура 9: похилий віраж — g_eff перпендикулярно дорозі ──────────────────
def fig_banked_turn():
    W, H = 1040, 640
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Похилий віраж: полотно нахилене так, що g_eff тисне перпендикулярно в дорогу",
                  size=15.5, bold=True))

    f.append(line(640, 78, 640, H - 66, color=MUTED, sw=1.2, dash="6 7"))

    Px, Py = 360, 380
    theta = math.radians(25)
    dxr, dyr = 154.1, 71.9  # довжина 170 уздовж полотна
    right = (Px + dxr, Py - dyr)   # зовнішній (піднятий) край
    left = (Px - dxr, Py + dyr)    # внутрішній (нижчий) край
    f.append(line(180, Py, 540, Py, color=MUTED, sw=1.2, dash="5 5"))
    f.append(line(Px, 300, Px, 470, color=MUTED, sw=1.2, dash="4 5"))
    f.append(line(left[0], left[1], right[0], right[1], color=INK, sw=5))
    f.append(circle(Px, Py, 7, fill="#dfe7f5", stroke=INK, sw=2))

    f.append(arrow(Px, Py, Px, Py + 90, color=INK, sw=3.2))
    f.append(text(Px - 14, Py + 50, "g", size=13, bold=True, color=INK, anchor="end"))

    f.append(arrow(Px, Py, Px - 90, Py, color=NEG, sw=2.6))
    f.append(text(Px - 110, Py - 18, "a → до центру", size=11.5, bold=True, color=NEG, anchor="end"))

    f.append(arrow(Px, Py, Px + 90, Py, color=POS, sw=2.6))
    f.append(text(Px + 110, Py - 18, "−a (назовні)", size=11.5, bold=True, color=POS, anchor="start"))

    gx, gy = Px + 90 * math.sin(theta), Py + 90 * math.cos(theta)
    f.append(arrow(Px, Py, gx, gy, color=FIELD, sw=3.4))
    f.append(text(gx + 16, gy - 6, "g_eff", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(Px + 16, Py + 78, "θ", size=13, bold=True, color=MUTED, anchor="start"))

    f.append(text(200, 92, "Похилий поворот у розрізі", size=13.5, bold=True, color=INK))

    f.append(text(830, 108, "Умова ідеального нахилу", size=14, bold=True, color=INK))
    b, w, h = textbox(830, 150, "tan θ = v² / (r·g)", size=16, pad=12, fill="#eaf7ee", stroke=FIELD, sw=1.6, bold=True)
    f.append(b)
    f.append(fitbox(670, 190, 320, 74,
                    ["якщо нахилити полотно рівно на θ,", "g_eff дивиться перпендикулярно в дорогу —",
                     "бокової складової тертя вже не треба"],
                    size=12, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    legend = [(INK, "g — тяжіння (вниз)"),
              (NEG, "a — доцентрове (до центру)"),
              (POS, "−a — назовні (від центру)"),
              (FIELD, "g_eff = g − a — уявний низ, ⟂ дорозі")]
    ly0 = 320
    for i, (col, lbl) in enumerate(legend):
        ly = ly0 + i * 42
        f.append(rect(670, ly - 11, 20, 20, fill="#ffffff", stroke=col, sw=2, rx=4))
        f.append(text(700, ly + 4, lbl, size=12, color=col, anchor="start"))

    b, w, h = textbox(W / 2, H - 26,
                      "залізнична колія, автомагістральний віраж і трек велодрому нахилені саме так — під розрахункову швидкість",
                      size=13, pad=11, fill="#eef2fb", stroke=INK, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "banked-turn.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_scale_reads_support(), fig_elevator_weight(), fig_spring_vs_balance(),
          fig_elevator_ride(), fig_g_maneuvers(),
          fig_hist_natural_place(), fig_hist_weight_migrates(),
          fig_apparent_weight_vector(), fig_banked_turn()]
    print("written:")
    for p in ps:
        print("  ", p)
