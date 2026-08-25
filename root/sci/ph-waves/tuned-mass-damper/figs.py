# -*- coding: utf-8 -*-
"""Фігури до теми «Настроєний гаситель коливань».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── фізика 2-DOF (перевірено чисельно) ──────────────────────────────────────
def resp(g, f, mu, zeta):
    """Нормований розмах головної маси X₁·K/F₀ (Ден Гартоґ).
    g=ω/ω_p, f=ωₐ/ω_p, μ=m/M, zeta=c/(2mω_p)."""
    num = (2 * zeta * g) ** 2 + (g * g - f * f) ** 2
    den = ((2 * zeta * g) ** 2) * ((g * g - 1 + mu * g * g) ** 2) + \
          (mu * f * f * g * g - (g * g - 1) * (g * g - f * f)) ** 2
    return math.sqrt(num / den) if den > 1e-12 else 1e9


def bare(g, zs):
    """Голий 1-DOF резонанс без гасителя."""
    return 1.0 / math.sqrt((1 - g * g) ** 2 + (2 * zs * g) ** 2)


# ── допоміжне малювання ──────────────────────────────────────────────────────
def spring(x1, x2, y, coils=6, amp=12, lead=14):
    seg = (x2 - x1 - 2 * lead) / coils
    pts = [(x1, y), (x1 + lead, y)]
    for i in range(coils):
        pts.append((x1 + lead + seg * (i + 0.25), y - amp))
        pts.append((x1 + lead + seg * (i + 0.75), y + amp))
    pts.append((x2 - lead, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def dashpot(x1, x2, y):
    out = []
    cyl_x, cyl_w, cyl_h = x1 + 12, 34, 26
    out.append(line(x1, y, cyl_x, y, color=INK, sw=2.2))
    out.append(line(cyl_x, y - cyl_h / 2, cyl_x + cyl_w, y - cyl_h / 2, color=INK, sw=2.2))
    out.append(line(cyl_x, y + cyl_h / 2, cyl_x + cyl_w, y + cyl_h / 2, color=INK, sw=2.2))
    out.append(line(cyl_x, y - cyl_h / 2, cyl_x, y + cyl_h / 2, color=INK, sw=2.2))
    px = cyl_x + cyl_w - 10
    out.append(line(px, y - cyl_h / 2 + 3, px, y + cyl_h / 2 - 3, color=INK, sw=3.2))
    out.append(line(px, y, x2, y, color=INK, sw=2.2))
    return "".join(out)


def wall(x, y1, y2, side=1):
    out = [line(x, y1, x, y2, color=INK, sw=3)]
    yy = y1 + 6
    while yy < y2:
        out.append(line(x, yy, x + 12 * side, yy - 12, color=MUTED, sw=1.4))
        yy += 14
    return "".join(out)


def clamped_path(PX, PY, samples, amax, color, sw=2.6, dash=None):
    """Полілінія з відсіканням зверху: там, де значення > amax, лінія розривається
    (перо піднімається), тож пік «вилітає» за верх без пласкої шапки."""
    segs, cur = [], []
    for xd, yv in samples:
        if yv <= amax:
            cur.append((PX(xd), PY(yv)))
        else:
            if cur:
                cur.append((PX(xd), PY(amax)))     # добіг до верхнього краю
                segs.append(cur)
                cur = []
    if cur:
        segs.append(cur)
    ds = ' stroke-dasharray="%s"' % dash if dash else ''
    out = []
    for seg in segs:
        if len(seg) < 2:
            continue
        d = "M %.1f %.1f " % seg[0] + " ".join("L %.1f %.1f" % p for p in seg[1:])
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                   % (d, color, sw, ds))
    return "".join(out)


# ── Фігура 1: концепція — головна маса + гаситель у протифазі ────────────────
def fig_concept():
    W, H = 820, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Настроєний гаситель: другий осцилятор, що штовхає у відповідь",
                  size=16, bold=True))

    wx = 70
    ymid = 190
    f.append(wall(wx, 118, 262))

    # головна маса M
    Mx, Mw, Mh = 300, 130, 118
    My = ymid
    f.append(rect(Mx, My - Mh / 2, Mw, Mh, fill="#e8edf3", stroke=INK, sw=2, rx=6))
    f.append(text(Mx + Mw / 2, My - 6, "M", size=30, bold=True))
    f.append(text(Mx + Mw / 2, My + 22, "конструкція", size=12, color=MUTED))

    # пружина K від стіни до M
    f.append(spring(wx, Mx, My, coils=7, amp=14))
    f.append(text((wx + Mx) / 2, My - 30, "пружина K", size=13))
    f.append(text((wx + Mx) / 2, My + 40, "ω_p = √(K/M)", size=12, color=MUTED))

    # гаситель: пружина k (верх) + демпфер c (низ) від M до малої маси m
    mx, mw, mh = 620, 84, 74
    my = ymid
    f.append(spring(Mx + Mw, mx, my - 20, coils=5, amp=10, lead=12))
    f.append(text((Mx + Mw + mx) / 2, my - 46, "пружина k", size=12))
    f.append(dashpot(Mx + Mw, mx, my + 24))
    f.append(text((Mx + Mw + mx) / 2 + 4, my + 52, "демпфер c", size=12))
    f.append(rect(mx, my - mh / 2, mw, mh, fill="#eafaf1", stroke=FIELD, sw=2, rx=6))
    f.append(text(mx + mw / 2, my - 2, "m", size=24, bold=True, color="#1e7a45"))
    f.append(text(mx + mw / 2, my + 22, "гаситель", size=11, color=MUTED))

    # зовнішня сила (вітер) на M — згори
    f.append(arrow(Mx + Mw / 2 - 70, 96, Mx + Mw / 2 - 6, 96, color=POS, sw=3.2))
    f.append(text(Mx + Mw / 2 - 76, 92, "вітер F(t)", size=13, bold=True, color=POS,
                  anchor="end"))

    # стрілки протифази під масами
    ay = 300
    f.append(arrow(Mx + Mw / 2 - 6, ay, Mx + Mw / 2 + 66, ay, color=INK, sw=2.6))
    f.append(text(Mx + Mw / 2 + 30, ay + 20, "M → праворуч", size=12, bold=True))
    f.append(arrow(mx + mw / 2 + 6, ay, mx + mw / 2 - 60, ay, color=FIELD, sw=2.6))
    f.append(text(mx + mw / 2 - 20, ay + 20, "m ← ліворуч", size=12, bold=True,
                  color="#1e7a45"))

    b, bw, bh = textbox(W / 2, 348,
                        "гаситель настроєно: ωₐ = √(k/m) дорівнює докучливій частоті конструкції",
                        size=13, pad=9, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "tmd-concept.svg"), W, H, *f)


# ── Фігура 2: антирезонанс — провал і два нові піки (гаситель без демпфера) ──
def fig_absorber_notch():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Гаситель без демпфера: замість піка — провал, але обабіч два нові піки",
                  size=16, bold=True))

    ox, oy = 92, 392
    rx, ty = 770, 74
    g0, g1, amax = 0.55, 1.62, 7.0

    def PX(g):
        return ox + (rx - ox) * ((g - g0) / (g1 - g0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  ω / ω_p  →", size=13, anchor="end"))
    f.append(text(ox - 60, ty + 20, "розмах", size=13, bold=True, anchor="start"))
    f.append(text(ox - 60, ty + 38, "конструкції", size=11, color=MUTED, anchor="start"))

    for gg in (0.6, 0.8, 1.0, 1.2, 1.4, 1.6):
        f.append(line(PX(gg), oy, PX(gg), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(gg), oy + 22, "%.1f" % gg, size=11, color=MUTED))
    for aa in (1, 3, 5, 7):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 13, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))

    f.append(line(ox, PY(1), rx, PY(1), color=MUTED, sw=1.1, dash="5,6"))
    f.append(line(PX(1), oy, PX(1), ty + 8, color=MUTED, sw=1.1, dash="4,6"))
    f.append(text(PX(1), ty + 2, "частота настроєння", size=11, color=MUTED))

    # без гасителя (сіра, тонке структурне загасання)
    smp = [(g, bare(g, 0.03)) for g in [g0 + i * 0.003 for i in range(int((g1 - g0) / 0.003) + 1)]]
    f.append(clamped_path(PX, PY, smp, amax, MUTED, sw=2.0, dash="7,5"))
    f.append(text(PX(1.0) + 8, PY(6.4), "без гасителя", size=12, bold=True, color=MUTED,
                  anchor="start"))

    # з гасителем без демпфера (f=1, μ=0.1, ζ=0)
    smp = [(g, resp(g, 1.0, 0.1, 0.0)) for g in [g0 + i * 0.002 for i in range(int((g1 - g0) / 0.002) + 1)]]
    f.append(clamped_path(PX, PY, smp, amax, POS, sw=2.6))

    # анотації
    f.append(text(PX(1.0), PY(0.0) - 12, "антирезонанс: розмах → 0", size=12, bold=True,
                  color=POS))
    f.append(circle(PX(1.0), PY(0.0), 3.6, fill=POS, stroke=POS, sw=1))
    f.append(text(PX(0.86) - 6, PY(4.0), "новий пік", size=11, color=POS, anchor="end"))
    f.append(text(PX(1.205) + 6, PY(4.6), "новий пік", size=11, color=POS, anchor="start"))

    b, bw, bh = textbox(W / 2, H - 26,
                        "два осцилятори = дві власні частоти (нормальні моди): один пік розщепився надвоє",
                        size=12, pad=9, fill="#fdecec", stroke=POS, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "absorber-notch.svg"), W, H, *f)


# ── Фігура 3: компроміс загасання — замале / оптимальне / завелике ──────────
def fig_damping_tradeoff():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Загасання гасителя: замале лишає піки, завелике «морозить» гаситель",
                  size=16, bold=True))

    ox, oy = 92, 396
    rx, ty = 770, 78
    g0, g1, amax = 0.6, 1.45, 12.0
    mu = 0.1
    f_opt = 1.0 / (1 + mu)
    za_opt = math.sqrt(3 * mu / (8 * (1 + mu) ** 3))

    def PX(g):
        return ox + (rx - ox) * ((g - g0) / (g1 - g0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  ω / ω_p  →", size=13, anchor="end"))
    f.append(text(ox - 60, ty + 20, "розмах", size=13, bold=True, anchor="start"))
    f.append(text(ox - 60, ty + 38, "конструкції", size=11, color=MUTED, anchor="start"))

    for gg in (0.6, 0.8, 1.0, 1.2, 1.4):
        f.append(line(PX(gg), oy, PX(gg), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(gg), oy + 22, "%.1f" % gg, size=11, color=MUTED))
    for aa in (2, 4, 6, 8, 10, 12):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 13, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))
    f.append(line(PX(1), oy, PX(1), ty + 8, color=MUTED, sw=1.1, dash="4,6"))

    step = 0.0025
    N = int((g1 - g0) / step) + 1
    # замале загасання
    smp = [(g0 + i * step, resp(g0 + i * step, f_opt, mu, 0.03 * f_opt)) for i in range(N)]
    f.append(clamped_path(PX, PY, smp, amax, NEG, sw=2.4))
    # завелике загасання
    smp = [(g0 + i * step, resp(g0 + i * step, f_opt, mu, 0.45 * f_opt)) for i in range(N)]
    f.append(clamped_path(PX, PY, smp, amax, POS, sw=2.4))
    # оптимальне загасання
    smp = [(g0 + i * step, resp(g0 + i * step, f_opt, mu, za_opt * f_opt)) for i in range(N)]
    f.append(clamped_path(PX, PY, smp, amax, FIELD, sw=3.0))

    # легенда (у вільному верхньому лівому куті)
    lx, ly = ox + 20, ty + 8
    rows = [(NEG, "замале загасання — гострі піки"),
            (POS, "завелике — гаситель «примерз», один пік"),
            (FIELD, "оптимальне — два однакові низькі піки")]
    for i, (col, tx) in enumerate(rows):
        yy = ly + i * 22
        f.append(line(lx, yy - 4, lx + 26, yy - 4, color=col, sw=3.2))
        f.append(text(lx + 34, yy, tx, size=12, color=INK, anchor="start"))

    # позначка рівня оптимального піка
    apk = math.sqrt(1 + 2 / mu)
    f.append(line(ox, PY(apk), rx, PY(apk), color=FIELD, sw=1.1, dash="3,6"))
    f.append(text(rx - 4, PY(apk) - 8, "√(1 + 2/μ) ≈ 4.6", size=11, color="#1e7a45",
                  anchor="end"))
    return render(os.path.join(IMG, "damping-tradeoff.svg"), W, H, *f)


# ── Фігура 4: залишковий пік проти масового відношення ──────────────────────
def fig_mass_ratio():
    W, H = 780, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Більший гаситель — нижчий пік, але виграш швидко насичується",
                  size=16, bold=True))

    ox, oy = 96, 350
    rx, ty = 730, 74
    mu0, mu1, amax = 0.0, 0.15, 20.0

    def PX(mu):
        return ox + (rx - ox) * ((mu - mu0) / (mu1 - mu0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "масове відношення  μ = m/M", size=13, anchor="end"))
    f.append(text(ox - 66, ty + 20, "залишковий", size=12, bold=True, anchor="start"))
    f.append(text(ox - 66, ty + 38, "пік  A/A₀", size=12, bold=True, anchor="start"))

    for mm in (0.0, 0.03, 0.06, 0.09, 0.12, 0.15):
        f.append(line(PX(mm), oy, PX(mm), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(mm), oy + 22, "%d%%" % round(mm * 100), size=11, color=MUTED))
    for aa in (4, 8, 12, 16, 20):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 13, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))

    # крива √(1+2/μ)
    pts = []
    mu = 0.004
    while mu <= mu1 + 1e-9:
        pts.append((PX(mu), PY(math.sqrt(1 + 2 / mu))))
        mu += 0.001
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, NEG))

    # робоча точка прикладу μ=0.02 → 10
    mp, ap = 0.02, math.sqrt(1 + 2 / 0.02)
    f.append(line(PX(mp), oy, PX(mp), PY(ap), color=MUTED, sw=1.1, dash="4,5"))
    f.append(line(ox, PY(ap), PX(mp), PY(ap), color=MUTED, sw=1.1, dash="4,5"))
    f.append(circle(PX(mp), PY(ap), 4.6, fill=POS, stroke=POS, sw=1))
    f.append(text(PX(mp) + 12, PY(ap) - 8, "приклад: μ = 2 %  →  пік ≈ 10", size=12,
                  bold=True, color=POS, anchor="start"))

    f.append(text(PX(0.11), PY(5.0), "далі крива майже полога —", size=11, color=MUTED,
                  anchor="start"))
    f.append(text(PX(0.11), PY(5.0) + 17, "зайва маса дає мало", size=11, color=MUTED,
                  anchor="start"))
    return render(os.path.join(IMG, "mass-ratio.svg"), W, H, *f)


# ── Фігура 5 (історія): хронологія ідеї від язичкового частотоміра до вежі ──
def fig_timeline():
    W, H = 1100, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Шлях однієї ідеї: настроєний осцилятор-партнер, 1904 → 2004",
                  size=16, bold=True))

    axy = 232
    xs = [95 + i * 151.7 for i in range(7)]

    # ── смуги-ери над віссю ──
    eras = [(0, 2, POS, "НАРОДЖЕННЯ · Фрам"),
            (3, 4, NEG, "ТЕОРІЯ · Ормондройд і Ден Гартоґ"),
            (5, 6, FIELD, "ЗАСТОСУВАННЯ · вежі")]
    for a, b, col, lab in eras:
        xa, xb = xs[a] - 34, xs[b] + 34
        cx = (xa + xb) / 2
        f.append(line(xa, 74, xb, 74, color=col, sw=2))
        f.append(line(xa, 74, xa, 80, color=col, sw=2))
        f.append(line(xb, 74, xb, 80, color=col, sw=2))
        f.append(text(cx, 66, lab, size=13, bold=True, color=col))

    # ── вісь часу ──
    f.append(line(52, axy, 1010, axy, color=INK, sw=2.4))
    f.append(arrow(1010, axy, 1038, axy, color=INK, sw=2.4))
    f.append(text(1066, axy + 5, "час", size=12, color=MUTED, anchor="end"))

    # ── вузли ──
    data = [
        ("1904", ["Фрам:", "язичковий", "частотомір"], POS, True),
        ("1909", ["протикренові", "цистерни;", "заявка"], POS, False),
        ("1911", ["патент US 989,958:", "поглинач без", "демпфера"], POS, True),
        ("1928", ["Ормондройд,", "Ден Гартоґ:", "нерухомі точки"], NEG, False),
        ("1934", ["«Mechanical", "Vibrations» —", "метод у книзі"], NEG, True),
        ("1977", ["Ситикорп-центр:", "перший TMD", "у хмарочосі"], FIELD, False),
        ("2004", ["Тайбей 101:", "куля 660 т"], FIELD, True),
    ]
    for x, (year, lines, era, up) in zip(xs, data):
        boxcy = 150 if up else 312
        body, w, h = textbox(x, boxcy, "\n".join(lines), size=12, pad=8,
                             fill=FILL, stroke=era, sw=1.4, color=INK)
        if up:
            f.append(line(x, boxcy + h / 2, x, axy - 6, color=era, sw=1.6))
            f.append(text(x, boxcy - h / 2 - 9, year, size=16, bold=True, color=era))
        else:
            f.append(line(x, boxcy - h / 2, x, axy + 6, color=era, sw=1.6))
            f.append(text(x, boxcy + h / 2 + 20, year, size=16, bold=True, color=era))
        f.append(body)
        f.append(circle(x, axy, 6, fill=era, stroke=BG, sw=2))

    b, bw, bh = textbox(W / 2, 444,
                        "Той самий принцип — маленька настроєна маса, що перебирає коливання на себе — з корабельного мостка дійшов до вершини хмарочоса",
                        size=13, pad=9, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "timeline-tmd.svg"), W, H, *f)


# ── Фігура 6 (math): дві нерухомі точки — усі криві сходяться в P і Q ────────
def fig_fixed_points():
    W, H = 860, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Дві нерухомі точки: усі криві сходяться в P і Q — хоч яке загасання ζ",
                  size=16, bold=True))

    ox, oy = 104, 432
    rx, ty = 812, 96
    g0, g1e, amax = 0.55, 1.45, 8.0
    mu = 0.1
    f_opt = 1.0 / (1 + mu)
    za_opt = math.sqrt(3 * mu / (8 * (1 + mu) ** 3))
    # нерухомі точки з біквадратного рівняння (при оптимальному настроєнні)
    s = 2.0 / (1 + mu)
    prod = 2.0 / ((1 + mu) ** 2 * (2 + mu))
    disc = math.sqrt(s * s - 4 * prod)
    gP = math.sqrt((s - disc) / 2)
    gQ = math.sqrt((s + disc) / 2)
    Aeq = math.sqrt(1 + 2 / mu)

    def PX(g):
        return ox + (rx - ox) * ((g - g0) / (g1e - g0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "частота  g = ω / ω_p  →", size=13, anchor="end"))
    f.append(text(ox - 66, ty + 18, "розмах", size=13, bold=True, anchor="start"))
    f.append(text(ox - 66, ty + 36, "X₁·K / F₀", size=11, color=MUTED, anchor="start"))

    for gg in (0.6, 0.8, 1.0, 1.2, 1.4):
        f.append(line(PX(gg), oy, PX(gg), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(gg), oy + 22, "%.1f" % gg, size=11, color=MUTED))
    for aa in (2, 4, 6, 8):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 13, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))

    # рівень залишкового піка √(1+2/μ)
    f.append(line(ox, PY(Aeq), rx, PY(Aeq), color=FIELD, sw=1.2, dash="3,6"))
    f.append(text(rx - 4, PY(Aeq) - 9, "√(1 + 2/μ) = √21 ≈ 4.58", size=11,
                  color="#1e7a45", anchor="end"))
    # вертикальні напрямні до P, Q
    f.append(line(PX(gP), oy, PX(gP), PY(Aeq), color=MUTED, sw=1.0, dash="4,6"))
    f.append(line(PX(gQ), oy, PX(gQ), PY(Aeq), color=MUTED, sw=1.0, dash="4,6"))

    step = 0.002
    N = int((g1e - g0) / step) + 1
    curves = [(0.03, NEG, 2.2, "7,4"),
              (0.09, MUTED, 2.0, None),
              (0.30, POS, 2.4, None),
              (za_opt, FIELD, 3.2, None)]
    for z, col, sw, dash in curves:
        smp = [(g0 + i * step, resp(g0 + i * step, f_opt, mu, z)) for i in range(N)]
        f.append(clamped_path(PX, PY, smp, amax, col, sw=sw, dash=dash))

    # точки P, Q поверх кривих
    f.append(circle(PX(gP), PY(Aeq), 5.2, fill=FIELD, stroke=INK, sw=1.4))
    f.append(circle(PX(gQ), PY(Aeq), 5.2, fill=FIELD, stroke=INK, sw=1.4))
    f.append(text(PX(gP) - 6, PY(Aeq) - 13, "P", size=16, bold=True, color="#1e7a45",
                  anchor="end"))
    f.append(text(PX(gQ) + 9, PY(Aeq) - 13, "Q", size=16, bold=True, color="#1e7a45",
                  anchor="start"))

    # легенда — вільний верхній правий кут
    lx, ly = PX(1.15), ty + 6
    rows = [(NEG, "замале  ζ = 0.03"),
            (MUTED, "мале  ζ = 0.09"),
            (FIELD, "оптимальне  ζ ≈ 0.168"),
            (POS, "завелике  ζ = 0.30")]
    for i, (col, tx) in enumerate(rows):
        yy = ly + i * 21
        f.append(line(lx, yy - 4, lx + 26, yy - 4, color=col, sw=3.2))
        f.append(text(lx + 34, yy, tx, size=12, color=INK, anchor="start"))

    b, bw, bh = textbox(W / 2, H - 28,
                        "P і Q не залежать від ζ; настроєння f = 1/(1+μ) робить їх однаково високими",
                        size=13, pad=9, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "fixed-points.svg"), W, H, *f)


# ── Фігура (proj): пошук настроєння — висоти двох піків сходяться до рівних ──
def fig_proj_tuning():
    W, H = 800, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Що шукає код: висоти двох піків як функції настроєння f",
                  size=16, bold=True))

    ox, oy = 96, 392
    rx, ty = 764, 78
    f0, f1, amax = 0.80, 1.00, 8.5
    mu = 0.1
    fopt = 1.0 / (1 + mu)
    zopt = math.sqrt(3 * mu / (8 * (1 + mu) ** 3))
    apk = math.sqrt(1 + 2 / mu)

    def PX(ff):
        return ox + (rx - ox) * ((ff - f0) / (f1 - f0))

    def PY(a):
        return oy - (oy - ty) * (min(a, amax) / amax)

    def two_peaks(ff):
        gs = [0.55 + i * 0.001 for i in range(int(0.9 / 0.001) + 1)]
        vals = [resp(g, ff, mu, zopt) for g in gs]
        isplit = min(range(len(gs)), key=lambda i: abs(gs[i] - ff))
        return max(vals[:isplit + 1]), max(vals[isplit:])

    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, ty - 6, color=INK, sw=1.8))
    f.append(text(rx - 4, oy + 34, "настроєння  f = ωₐ / ω_p  →", size=13, anchor="end"))
    f.append(text(ox - 72, ty + 18, "висота", size=13, bold=True, anchor="start"))
    f.append(text(ox - 72, ty + 36, "піка", size=13, bold=True, anchor="start"))

    for ff in (0.80, 0.85, 0.90, 0.95, 1.00):
        f.append(line(PX(ff), oy, PX(ff), oy + 6, color=INK, sw=1.3))
        f.append(text(PX(ff), oy + 22, "%.2f" % ff, size=11, color=MUTED))
    for aa in (2, 4, 6, 8):
        f.append(line(ox - 6, PY(aa), ox, PY(aa), color=INK, sw=1.3))
        f.append(text(ox - 13, PY(aa) + 4, "%d" % aa, size=11, color=MUTED, anchor="end"))

    step = 0.0025
    N = int((f1 - f0) / step) + 1
    lo = [(f0 + i * step, two_peaks(f0 + i * step)[0]) for i in range(N)]
    hi = [(f0 + i * step, two_peaks(f0 + i * step)[1]) for i in range(N)]

    def poly(samples, color, sw):
        pts = [(PX(x), PY(y)) for x, y in samples if y <= amax]
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)

    f.append(line(ox, PY(apk), rx, PY(apk), color=MUTED, sw=1.1, dash="3,6"))
    f.append(text(ox + 8, PY(apk) - 8, "√(1 + 2/μ) ≈ 4.6", size=11, color=MUTED, anchor="start"))

    f.append(poly(lo, NEG, 2.8))
    f.append(poly(hi, POS, 2.8))

    f.append(line(PX(fopt), oy, PX(fopt), PY(apk), color=FIELD, sw=1.2, dash="4,5"))
    f.append(circle(PX(fopt), PY(apk), 5.0, fill=FIELD, stroke=FIELD, sw=1))

    f.append(text(PX(0.815), PY(two_peaks(0.815)[1]) - 12, "верхній пік", size=12,
                  bold=True, color=POS, anchor="start"))
    f.append(text(PX(0.985), PY(two_peaks(0.985)[0]) - 12, "нижній пік", size=12,
                  bold=True, color=NEG, anchor="end"))
    f.append(text(PX(fopt), ty + 22, "f = 1/(1+μ)", size=12, bold=True, color="#1e7a45"))
    f.append(text(PX(fopt), ty + 40, "піки рівні → оптимум", size=11, color="#1e7a45"))

    b, bw, bh = textbox(W / 2, H - 26,
                        "збий настроєння в будь-який бік — один пік злітає; код шукає f, де вони зрівнялись",
                        size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "proj-tuning.svg"), W, H, *f)


# ── Фігура (proj): часова симуляція вежі під випадковим вітром, з TMD і без ──
def _wind(n, dt, seed=7):
    import random
    rng = random.Random(seed)
    tau = 1.0 / 1.5            # стала кореляції ~ 1/(1.5·ω_p)
    a = dt / (tau + dt)
    w = [0.0]
    for _ in range(n + 2):
        w.append(w[-1] + a * (rng.gauss(0, 1) - w[-1]))
    return w


def _sway(mu, ftune, zeta, zeta_s, dt, n, wind, coupled=True):
    """RK4 для 2-DOF; coupled=False → k=c=0 (гола вежа). Повертає x₁(t)."""
    M = K = wp = 1.0
    m = mu
    k = mu * ftune * ftune if coupled else 0.0
    c = 2 * zeta * m * wp if coupled else 0.0
    cs = 2 * zeta_s * M * wp
    s = [0.0, 0.0, 0.0, 0.0]

    def deriv(st, F):
        x1, v1, x2, v2 = st
        a1 = (-K * x1 - cs * v1 - k * (x1 - x2) - c * (v1 - v2) + F) / M
        a2 = (-k * (x2 - x1) - c * (v2 - v1)) / m
        return [v1, a1, v2, a2]

    out = []
    for i in range(n):
        F0, F1 = wind[i], wind[i + 1]
        Fm = 0.5 * (F0 + F1)
        k1 = deriv(s, F0)
        k2 = deriv([s[j] + 0.5 * dt * k1[j] for j in range(4)], Fm)
        k3 = deriv([s[j] + 0.5 * dt * k2[j] for j in range(4)], Fm)
        k4 = deriv([s[j] + dt * k3[j] for j in range(4)], F1)
        s = [s[j] + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) for j in range(4)]
        out.append(s[0])
    return out


def fig_proj_time():
    W, H = 820, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Верхівка вежі під випадковим вітром: без гасителя і з ним",
                  size=16, bold=True))

    mu, zeta_s = 0.02, 0.01
    fo = 1.0 / (1 + mu)
    zo = math.sqrt(3 * mu / (8 * (1 + mu) ** 3))
    dt, T = 0.06, 260.0
    n = int(T / dt)
    wind = _wind(n, dt)
    xb = _sway(mu, fo, zo, zeta_s, dt, n, wind, coupled=False)
    xt = _sway(mu, fo, zo, zeta_s, dt, n, wind, coupled=True)

    amp = max(abs(v) for v in xb) * 1.08

    def rms(a):
        seg = a[int(0.25 * len(a)):]
        return (sum(v * v for v in seg) / len(seg)) ** 0.5

    rb, rt = rms(xb), rms(xt)
    ox, rxx = 88, 792
    T1 = T

    def PX(t):
        return ox + (rxx - ox) * (t / T1)

    panels = [(64, 200, "без гасителя", xb, rb, POS),
              (270, 406, "з настроєним гасителем (μ = 2 %)", xt, rt, FIELD)]
    for pytop, pybot, lbl, xs, r, col in panels:
        mid = (pytop + pybot) / 2
        half = (pybot - pytop) / 2

        def PY(v, mid=mid, half=half):
            return mid - half * (max(-amp, min(amp, v)) / amp)

        f.append(rect(ox, pytop, rxx - ox, pybot - pytop, fill="none", stroke=MUTED,
                      sw=1.0, rx=4))
        f.append(line(ox, mid, rxx, mid, color=MUTED, sw=1.0, dash="2,6"))
        f.append(line(ox, PY(r), rxx, PY(r), color=col, sw=1.0, dash="5,5"))
        f.append(line(ox, PY(-r), rxx, PY(-r), color=col, sw=1.0, dash="5,5"))
        pts = [(PX(i * dt), PY(xs[i])) for i in range(n)]
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (d, col))
        f.append(text(ox + 8, pytop + 18, lbl, size=13, bold=True, color=col, anchor="start"))
        f.append(text(rxx - 8, pytop + 18, "розмах (RMS) = %.2f" % r, size=12, bold=True,
                      color=col, anchor="end"))

    for tt in (0, 50, 100, 150, 200, 250):
        f.append(line(PX(tt), 406, PX(tt), 412, color=INK, sw=1.2))
        f.append(text(PX(tt), 428, "%d" % tt, size=11, color=MUTED))
    f.append(text(rxx - 4, 448, "час  (T_p = 2π/ω_p ≈ 6.3 — один період вежі)  →", size=12,
                  anchor="end"))

    drop = 100 * (1 - rt / rb)
    b, bw, bh = textbox(W / 2, H - 24,
                        "той самий вітер, той самий відрізок часу — гаситель зрізав розмах на %d %%" % round(drop),
                        size=13, pad=9, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "proj-timedomain.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_concept(), fig_absorber_notch(), fig_damping_tradeoff(), fig_mass_ratio(),
          fig_timeline(), fig_fixed_points(), fig_proj_tuning(), fig_proj_time()]
    print("written:")
    for p in ps:
        print("  ", p)
