# -*- coding: utf-8 -*-
"""Фігури до статті «Скін-ефект». Чистий Python + svgkit, без залежностей."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def hot(t):
    """t in [0,1] -> колір густини струму: 0 світло-сірий (нема), 1 гарячий (макс)."""
    t = max(0.0, min(1.0, t))
    # від блідого до POS (гарячого)
    r0, g0, b0 = 0xf0, 0xf2, 0xf5     # майже білий
    r1, g1, b1 = 0xc0, 0x39, 0x2b     # POS
    r = int(r0 + (r1 - r0) * t)
    g = int(g0 + (g1 - g0) * t)
    b = int(b0 + (b1 - b0) * t)
    return "#%02x%02x%02x" % (r, g, b)


# ── Фіг. 1: розподіл густини по перерізу за зростання частоти ─────────────────
def fig_current_distribution():
    W, H = 720, 305
    frags = []
    frags.append(text(W / 2, 28, "Густина струму по перерізу проводу", size=17, bold=True))

    R = 62
    cy = 160
    # чотири переріз-кола з різною δ (глибиною робочого шару відносно R)
    cases = [
        (110, "постійний струм", 99.0),   # рівномірно (δ >> R)
        (300, "низька f",        0.55),   # δ ≈ 0.55R
        (490, "висока f",        0.22),   # δ ≈ 0.22R
        (660, "дуже висока f",   0.09),   # δ ≈ 0.09R
    ]
    NR = 26  # кількість кілець для градієнта
    for cx, label, dfrac in cases:
        # малюємо концентричні кільця: густина ~ exp(-(глибина)/δ)
        for i in range(NR, 0, -1):
            r_out = R * i / NR
            depth = R - r_out          # глибина від поверхні
            t = math.exp(-depth / (dfrac * R)) if dfrac < 10 else 1.0
            frags.append(circle(cx, cy, r_out, fill=hot(t), stroke="none", sw=0))
        # обвід металу
        frags.append(circle(cx, cy, R, fill="none", stroke=INK, sw=2))
        frags.append(text(cx, cy + R + 26, label, size=13, color=INK))

    # стрілка «частота росте» — нижче за підписи перерізів
    frags.append(arrow(150, 282, 620, 282, color=MUTED, sw=2))
    frags.append(text(W / 2, 276, "частота зростає  →  робочий шар тоншає", size=12, color=MUTED))
    render(os.path.join(IMG, "current-distribution.svg"), W, H, *frags)


# ── Фіг. 2: експоненційний спад густини вглиб ────────────────────────────────
def fig_skin_depth_curve():
    W, H = 700, 380
    frags = []
    frags.append(text(W / 2, 30, "Спад густини струму вглиб металу", size=17, bold=True))

    x0, y0 = 90, 300     # початок осей (поверхня зверху ліворуч)
    xw, yh = 540, 220
    # осі
    frags.append(line(x0, y0 - yh, x0, y0, color=INK, sw=2))         # вісь J (вертикальна)
    frags.append(line(x0, y0, x0 + xw, y0, color=INK, sw=2))          # вісь глибини
    frags.append(text(x0 - 12, y0 - yh - 6, "J", size=14, italic=True, anchor="end"))
    frags.append(text(x0 + xw, y0 + 24, "глибина від поверхні", size=12, color=MUTED, anchor="end"))

    # крива J = exp(-x/δ); δ на 1/4 ширини осі
    delta_px = xw / 4.2
    pts = []
    N = 120
    for i in range(N + 1):
        xx = xw * i / N
        J = math.exp(-xx / delta_px)
        px = x0 + xx
        py = y0 - J * yh
        pts.append((px, py))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # позначки δ, 2δ, 3δ з рівнями 1/e, 1/e², 1/e³
    marks = [(1, "δ", "1/e ≈ 0.37"), (2, "2δ", "0.14"), (3, "3δ", "0.05")]
    for k, lbl, val in marks:
        xx = k * delta_px
        J = math.exp(-k)
        px = x0 + xx
        py = y0 - J * yh
        frags.append(line(px, y0, px, py, color=MUTED, sw=1.2, dash="4 4"))
        frags.append(line(x0, py, px, py, color=MUTED, sw=1.2, dash="4 4"))
        frags.append(circle(px, py, 4, fill=POS, stroke="none", sw=0))
        frags.append(text(px, y0 + 20, lbl, size=13, bold=True, color=INK))
        frags.append(text(px + 8, py - 8, val, size=11, color=MUTED, anchor="start"))

    # рівень поверхні J0
    frags.append(text(x0 - 10, y0 - yh + 4, "J₀", size=12, color=INK, anchor="end"))
    frags.append(line(x0, y0 - yh, x0 + 6, y0 - yh, color=INK, sw=1.5))

    box = fitbox(x0 + xw - 250, y0 - yh - 8, 250, 44,
                 "на глибині δ струму лишається\nлише 37 %  —  глибше метал майже не працює",
                 size=12, fill=FILL, stroke=FIELD, color=INK)
    frags.append(box)
    render(os.path.join(IMG, "skin-depth-curve.svg"), W, H, *frags)


# ── Фіг. 3: три способи боротьби ─────────────────────────────────────────────
def fig_mitigation():
    W, H = 720, 300
    frags = []
    frags.append(text(W / 2, 30, "Дати струмові більше поверхні", size=17, bold=True))

    cy = 150
    # 1) порожниста трубка
    cx = 130
    frags.append(circle(cx, cy, 46, fill="none", stroke=INK, sw=2))
    frags.append(circle(cx, cy, 34, fill=BG, stroke=INK, sw=2))
    # робочий шар — кільце по краю
    for i in range(10):
        rr = 46 - i * 1.2
        frags.append(circle(cx, cy, rr, fill="none", stroke=hot(math.exp(-i * 1.2 / 6)), sw=1.2))
    frags.append(circle(cx, cy, 46, fill="none", stroke=INK, sw=2))
    frags.append(text(cx, cy + 74, "трубка", size=13, bold=True))
    frags.append(text(cx, cy + 92, "серцевину прибрано", size=11, color=MUTED))

    # 2) ліцендрат — пучок тонких жилок
    cx = 360
    frags.append(circle(cx, cy, 48, fill=BG, stroke=MUTED, sw=1.5, ))
    # жилки — маленькі кола, кожна залита як «повністю робоча»
    import random
    random.seed(3)
    placed = []
    for _ in range(400):
        if len([1 for _ in placed]) >= 19:
            break
        a = random.uniform(0, 2 * math.pi)
        rad = random.uniform(0, 34)
        jx, jy = cx + rad * math.cos(a), cy + rad * math.sin(a)
        ok = all((jx - px) ** 2 + (jy - py) ** 2 > 13 ** 2 for px, py in placed)
        if ok:
            placed.append((jx, jy))
    for jx, jy in placed:
        frags.append(circle(jx, jy, 5.5, fill=hot(0.9), stroke=INK, sw=1))
    frags.append(text(cx, cy + 74, "ліцендрат", size=13, bold=True))
    frags.append(text(cx, cy + 92, "багато тонких жилок", size=11, color=MUTED))

    # 3) широка смуга
    cx = 590
    bw, bh = 150, 22
    frags.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=hot(0.85), stroke=INK, sw=2, rx=3))
    frags.append(text(cx, cy + 74, "смуга", size=13, bold=True))
    frags.append(text(cx, cy + 92, "великий периметр", size=11, color=MUTED))

    render(os.path.join(IMG, "mitigation.svg"), W, H, *frags)


# ── Фіг. 4 (вставка comp-litz): конструкція джгута — транспозиція жилок ───────
def fig_litz_construction():
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 28, "Одна товста жила проти джгута ліцендрату", size=17, bold=True))

    # ЛІВОРУЧ: суцільна товста жила — працює лише кільце по краю
    cxl, cy, R = 165, 150, 60
    NR = 22
    for i in range(NR, 0, -1):
        r_out = R * i / NR
        depth = R - r_out
        t = math.exp(-depth / (0.16 * R))       # тонкий робочий шар
        frags.append(circle(cxl, cy, r_out, fill=hot(t), stroke="none", sw=0))
    frags.append(circle(cxl, cy, R, fill="none", stroke=INK, sw=2))
    frags.append(text(cxl, cy + R + 28, "суцільна жила", size=13, bold=True))
    frags.append(text(cxl, cy + R + 46, "працює лише шкірка", size=11, color=MUTED))

    # ПРАВОРУЧ: джгут — багато тонких жилок, кожна залита повністю
    cxr = 470
    frags.append(circle(cxr, cy, R + 4, fill=BG, stroke=MUTED, sw=1.5))
    import random
    random.seed(7)
    placed = []
    for _ in range(1500):
        if len(placed) >= 31:
            break
        a = random.uniform(0, 2 * math.pi)
        rad = R * math.sqrt(random.uniform(0, 1)) * 0.82
        jx, jy = cxr + rad * math.cos(a), cy + rad * math.sin(a)
        if all((jx - px) ** 2 + (jy - py) ** 2 > 15.5 ** 2 for px, py in placed):
            placed.append((jx, jy))
    for jx, jy in placed:
        frags.append(circle(jx, jy, 6.2, fill=hot(0.92), stroke=INK, sw=0.9))
    frags.append(text(cxr, cy + R + 28, "джгут ліцендрату", size=13, bold=True))
    frags.append(text(cxr, cy + R + 46, "кожна жилка працює вся", size=11, color=MUTED))

    # праворуч — підпис про транспозицію (fitbox повертає рядок)
    frags.append(fitbox(590, cy - 58, 118, 116,
                        "жилки\nпереплетені:\nкожна по черзі\nі зовні,\nі в осерді\nджгута",
                        size=12, fill=FILL, stroke=FIELD, color=INK))
    frags.append(arrow(560, cy, 590, cy, color=MUTED, sw=1.6))
    render(os.path.join(IMG, "litz-construction.svg"), W, H, *frags)


# ── Фіг. 5 (вставка comp-litz): де ліцендрат перестає допомагати ──────────────
def fig_litz_window():
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 30, "Опір за частотою: коли ліцендрат виграє, а коли ні", size=16, bold=True))

    x0, y0 = 92, 320
    xw, yh = 560, 240
    # осі
    frags.append(line(x0, y0 - yh, x0, y0, color=INK, sw=2))
    frags.append(line(x0, y0, x0 + xw, y0, color=INK, sw=2))
    frags.append(text(x0 - 12, y0 - yh - 8, "R_ac / R_dc", size=13, italic=True, anchor="start"))
    frags.append(text(x0 + xw, y0 + 26, "частота (лог)", size=12, color=MUTED, anchor="end"))
    frags.append(line(x0, y0, x0 + 6, y0, color=INK, sw=1.5))
    frags.append(text(x0 - 8, y0 + 4, "1", size=11, color=INK, anchor="end"))

    N = 160
    # суцільна жила: R_ac/R_dc ~ 1 на низах, потім росте ~√f (скін-ефект)
    solid = []
    litz = []
    for i in range(N + 1):
        u = i / N                       # 0..1 по осі (лог-частота)
        # суцільна: плаский до 0.25, далі корінь-подібне зростання
        s = 1.0 + 5.8 * max(0.0, u - 0.22) ** 1.35
        # ліцендрат: низько й рівно в робочому вікні, круто вгору у хвості (жилки > δ,
        # міжжильна ємність і близькість джгута) — врешті переганяє суцільну
        base = 1.03 + 0.28 * max(0.0, u - 0.30)
        tail = 7.2 * max(0.0, u - 0.72) ** 2.2
        l = base + tail
        sc = lambda v: y0 - min(v, 7.0) / 7.0 * yh
        solid.append((x0 + xw * u, sc(s)))
        litz.append((x0 + xw * u, sc(l)))

    def path(pts, col, sw=3, dash=None):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%d"%s/>' % (d, col, sw, da)

    frags.append(path(solid, MUTED, sw=2.5, dash="7 5"))
    frags.append(path(litz, POS, sw=3))

    # межа вікна — вертикаль, де криві перетинаються (хвіст ліцендрату вгору)
    xcross = x0 + xw * 0.80
    frags.append(line(xcross, y0 - yh, xcross, y0, color=INK, sw=1.2, dash="3 4"))
    frags.append(fitbox(xcross - 6 - 150, y0 - yh + 4, 150, 40,
                        "вище цієї частоти жилки\nсамі товщі за δ — виграшу нема",
                        size=11, fill=FILL, stroke=FIELD, color=INK))

    # підписи кривих
    frags.append(text(x0 + xw * 0.36, y0 - yh * 0.10, "суцільна жила", size=12, color=MUTED, anchor="start"))
    frags.append(text(x0 + xw * 0.06, y0 - yh * 0.20, "ліцендрат", size=12, bold=True, color=POS, anchor="start"))

    # зона виграшу
    frags.append(fitbox(x0 + 14, y0 - yh + 8, 150, 26, "тут ліцендрат виграє",
                        size=11, fill="#eaf6ee", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "litz-window.svg"), W, H, *frags)


# ── Фіг. (вставка math): спад амплітуди + поворот фази вглиб ──────────────────
def fig_field_decay_phase():
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 30, "Поле в металі: спад і поворот фази з глибиною", size=16, bold=True))

    x0 = 80          # вісь J (поверхня)
    ymid = 190       # нульова лінія коливання
    xw = 560
    amp = 92         # амплітуда на поверхні (px)
    delta_px = xw / 5.2   # δ у пікселях уздовж глибини

    # осі
    frags.append(line(x0, ymid - amp - 16, x0, ymid + amp + 16, color=INK, sw=2))   # вертикальна (J)
    frags.append(line(x0, ymid, x0 + xw + 10, ymid, color=MUTED, sw=1.2))           # нульова лінія
    frags.append(text(x0 - 10, ymid - amp - 8, "J", size=14, italic=True, anchor="end"))
    frags.append(text(x0 + xw + 8, ymid + 24, "глибина x", size=12, color=MUTED, anchor="end"))

    # згасне коливання J = e^(-x/δ)·cos(x/δ) та обвідна ±e^(-x/δ)
    N = 260
    wave, envU, envL = [], [], []
    for i in range(N + 1):
        xx = xw * i / N
        env = math.exp(-xx / delta_px)
        px = x0 + xx
        wave.append((px, ymid - amp * env * math.cos(xx / delta_px)))
        envU.append((px, ymid - amp * env))
        envL.append((px, ymid + amp * env))

    def path_of(pts, stroke, sw, dash=None):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, stroke, sw, da)

    frags.append(path_of(envU, MUTED, 1.4, dash="5 4"))
    frags.append(path_of(envL, MUTED, 1.4, dash="5 4"))
    frags.append(path_of(wave, POS, 2.6))

    # позначки δ, 2δ, 3δ на осі глибини
    for k, lbl in [(1, "δ"), (2, "2δ"), (3, "3δ")]:
        px = x0 + k * delta_px
        env = math.exp(-k)
        frags.append(line(px, ymid + amp + 8, px, ymid - amp - 8, color=FIELD, sw=1.0, dash="2 5"))
        frags.append(text(px, ymid + amp + 26, lbl, size=13, bold=True, color=INK))
        frags.append(circle(px, ymid - amp * env, 3.5, fill=MUTED, stroke="none", sw=0))
    frags.append(text(x0 + delta_px + 6, ymid - amp * math.exp(-1) - 8, "1/e ≈ 0.37", size=11, color=MUTED, anchor="start"))

    # протифаза на πδ
    xpi = x0 + math.pi * delta_px
    frags.append(line(xpi, ymid + amp + 8, xpi, ymid - amp - 20, color=NEG, sw=1.0, dash="2 4"))
    frags.append(text(xpi, ymid - amp - 24, "πδ: протифаза", size=11, color=NEG))

    frags.append(fitbox(x0 + xw - 236, ymid + 28, 236, 40,
                        "обвідна — чистий спад e^(−x/δ);\nвсередині коливання відстає за фазою",
                        size=11, fill=FILL, stroke=FIELD, color=INK))
    render(os.path.join(IMG, "field-decay-phase.svg"), W, H, *frags)


# ── Фіг. (вставка math): хвильове число k=(1+j)/δ на комплексній площині ──────
def fig_wavenumber():
    W, H = 560, 380
    frags = []
    frags.append(text(W / 2, 30, "Хвильове число  k = (1+j)/δ  на площині", size=16, bold=True))

    ox, oy = 155, 250     # початок координат
    L = 150               # довжина 1/δ у px
    frags.append(arrow(ox - 30, oy, ox + L + 55, oy, color=INK, sw=1.8))    # Re
    frags.append(arrow(ox, oy + 30, ox, oy - L - 55, color=INK, sw=1.8))    # Im
    frags.append(text(ox + L + 52, oy + 22, "Re k", size=13, color=INK, anchor="end"))
    frags.append(text(ox + 10, oy - L - 40, "Im k", size=13, color=INK, anchor="start"))

    kx, ky = ox + L, oy - L
    frags.append(line(ox, oy, kx, ky, color=POS, sw=3))
    frags.append(circle(kx, ky, 5, fill=POS, stroke="none", sw=0))
    frags.append(text(kx + 10, ky - 6, "k", size=15, bold=True, italic=True, color=POS, anchor="start"))

    frags.append(line(kx, ky, kx, oy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(line(kx, ky, ox, ky, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text((ox + kx) / 2, oy + 20, "1/δ  (згасання)", size=12, color=INK))
    frags.append(text(ox - 12, (oy + ky) / 2, "1/δ", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 12, (oy + ky) / 2 + 16, "(фаза)", size=11, color=MUTED, anchor="end"))

    # дуга кута 45°
    ar = 44
    pts = []
    for i in range(21):
        a = (math.pi / 4) * i / 20
        pts.append((ox + ar * math.cos(a), oy - ar * math.sin(a)))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (d, FIELD))
    frags.append(text(ox + ar + 26, oy - ar / 2 + 2, "45°", size=13, bold=True, color=FIELD, anchor="start"))

    frags.append(fitbox(ox + 30, oy + 34, 300, 52,
                        "Re і Im рівні (обидві 1/δ): метал\nзгасає так само швидко, як обертає\nфазу — це підпис дифузії поля",
                        size=11, fill=FILL, stroke=FIELD, color=INK))
    render(os.path.join(IMG, "wavenumber.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_current_distribution()
    fig_skin_depth_curve()
    fig_mitigation()
    fig_litz_construction()
    fig_litz_window()
    fig_field_decay_phase()
    fig_wavenumber()
    print("figs done")
