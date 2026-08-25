# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

Vt = 0.02585


# ── спільна модель Ґуммеля — Пуна (для чесних графіків) ─────────────────────
def gp(vbe, vbc=0.0, IS=1e-14, BF=200.0, IKF=0.05, ISE=1e-13, NE=1.6, VAF=1e9):
    ef = math.exp(vbe / Vt)
    q1 = 1.0 / (1.0 - vbc / VAF)                       # base-width modulation (Ерлі)
    q2 = (IS / IKF) * (ef - 1.0)                       # high-level injection
    qb = 0.5 * q1 * (1.0 + math.sqrt(1.0 + 4.0 * q2))
    ic = IS / qb * (ef - 1.0)
    ib = IS / BF * (ef - 1.0) + ISE * (math.exp(vbe / (NE * Vt)) - 1.0)
    return ic, ib


def dot(cx, cy, r=4, color=INK):
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


# ── figure 1: Gummel plot + β як дзвін ───────────────────────────────────────
def fig_gummel():
    W, H = 920, 500
    p = []

    # ---------- ЛІВА панель: графік Ґуммеля ----------
    lx0, ly0, lxr, lyt = 108, 410, 430, 78
    vlo, vhi = 0.30, 0.85
    dlo, dhi = -10, 0                     # десяткові порядки струму
    def LX(v): return lx0 + (v - vlo) / (vhi - vlo) * (lxr - lx0)
    def LY(dec): return ly0 - (dec - dlo) / (dhi - dlo) * (ly0 - lyt)

    p.append(text((lx0 + lxr) / 2, 52, "Графік Ґуммеля: log I проти V_BE", 15, INK, bold=True))
    # (терміни струмів — кирилицею К/Б, як у решті книги)
    p.append(arrow(lx0, ly0, lxr + 12, ly0, INK, 2))
    p.append(arrow(lx0, ly0, lx0, lyt - 12, INK, 2))
    p.append(text(lxr + 8, ly0 + 28, "V_BE, В", 12, INK, anchor="end", italic=True))
    p.append(text(lx0 - 44, lyt - 2, "log₁₀ I", 12, INK, anchor="start", italic=True))

    # поділки X
    vx = 0.3
    while vx <= 0.851:
        px = LX(vx)
        p.append(line(px, ly0, px, ly0 + 5, INK, 1.3))
        p.append(text(px, ly0 + 22, "%.1f" % vx, 11, MUTED))
        vx += 0.1
    # поділки Y (порядки)
    for d in range(dlo, dhi + 1, 2):
        py = LY(d)
        p.append(line(lx0 - 5, py, lx0, py, INK, 1.3))
        p.append(text(lx0 - 12, py + 4, str(d), 11, MUTED, anchor="end"))
        p.append(line(lx0, py, lxr, py, "#eceff2", 1))

    # криві I_C та I_B
    ic_pts, ib_pts = [], []
    v = vlo
    while v <= vhi + 1e-9:
        ic, ib = gp(v)
        ic_pts.append("%.1f,%.1f" % (LX(v), LY(math.log10(ic))))
        ib_pts.append("%.1f,%.1f" % (LX(v), LY(math.log10(ib))))
        v += 0.005
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ic_pts), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ib_pts), POS))
    p.append(text(LX(0.845), LY(math.log10(gp(0.845)[0])) - 10, "I_К", 15, NEG, anchor="end", bold=True))
    p.append(text(LX(0.845), LY(math.log10(gp(0.845)[1])) + 20, "I_Б", 15, POS, anchor="end", bold=True))

    # проміжок = log β (у середині)
    vm = 0.60
    yc = LY(math.log10(gp(vm)[0])); yb = LY(math.log10(gp(vm)[1]))
    p.append(line(LX(vm), yc, LX(vm), yb, MUTED, 1.4, dash="3 3"))
    p.append(text(LX(vm) - 8, (yc + yb) / 2 + 4, "log β", 12, MUTED, anchor="end"))

    # анотації двох зламів
    p.append(text(LX(0.345), LY(-8.4), "витік у базі:", 11, POS, anchor="start"))
    p.append(text(LX(0.345), LY(-8.4) - 15, "I_Б задирається", 11, POS, anchor="start"))
    p.append(text(LX(0.83), LY(-1.2) + 4, "інжекція:", 11, NEG, anchor="end"))
    p.append(text(LX(0.83), LY(-1.2) + 19, "I_К гнеться", 11, NEG, anchor="end"))

    # ---------- ПРАВА панель: β(I_C) як дзвін ----------
    rx0, ry0, rxr, ryt = 590, 410, 878, 78
    clo, chi = -9, 0
    blo, bhi = 0, 200
    def RX(dec): return rx0 + (dec - clo) / (chi - clo) * (rxr - rx0)
    def RY(b): return ry0 - (b - blo) / (bhi - blo) * (ry0 - ryt)

    p.append(text((rx0 + rxr) / 2, 52, "Наслідок: β росте й падає", 15, INK, bold=True))
    p.append(arrow(rx0, ry0, rxr + 12, ry0, INK, 2))
    p.append(arrow(rx0, ry0, rx0, ryt - 12, INK, 2))
    p.append(text(rxr + 8, ry0 + 28, "log₁₀ I_К", 12, INK, anchor="end", italic=True))
    p.append(text(rx0 - 40, ryt - 2, "β", 13, INK, anchor="start", italic=True))

    for d in range(clo, chi + 1, 3):
        px = RX(d)
        p.append(line(px, ry0, px, ry0 + 5, INK, 1.3))
        p.append(text(px, ry0 + 22, str(d), 11, MUTED))
    for b in range(blo, bhi + 1, 50):
        py = RY(b)
        p.append(line(rx0 - 5, py, rx0, py, INK, 1.3))
        p.append(text(rx0 - 12, py + 4, str(b), 11, MUTED, anchor="end"))
        p.append(line(rx0, py, rxr, py, "#eceff2", 1))

    beta_pts = []
    v = vlo
    while v <= vhi + 1e-9:
        ic, ib = gp(v)
        d = math.log10(ic)
        if d >= clo:
            beta_pts.append("%.1f,%.1f" % (RX(d), RY(ic / ib)))
        v += 0.004
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(beta_pts), FIELD))

    p.append(text(RX(-7.4), RY(30), "витік", 11, POS, anchor="middle"))
    p.append(text(RX(-4.0), RY(188), "β ≈ BF", 12, INK, anchor="middle", bold=True))
    p.append(text(RX(-1.0), RY(40), "інжекція", 11, NEG, anchor="middle"))

    render(os.path.join(IMG, 'gummel-plot.svg'), W, H, "".join(p))


# ── figure 2: як дихає нормований заряд бази q_b ─────────────────────────────
def fig_qb():
    W, H = 880, 470
    cx = 440
    p = []
    p.append(text(W / 2, 40, "Нормований заряд бази q_b дихає з двох боків", 16, INK, bold=True))

    # центральна рамка з формулою
    p.append(fitbox(280, 172, 320, 116,
                    "q_b = (q₁ / 2)·(1 + √(1 + 4·q₂))\n\nструм ділимо на q_b:\nI_К = (I_S / q_b)·(e^(V_BE/Vₜ) − e^(V_BC/Vₜ))",
                    13, fill="#eef7f0", stroke=FIELD, sw=1.8))

    # --- лівий бік: q1, ефект Ерлі ---
    p.append(fitbox(30, 150, 185, 64,
                    "q₁ — ефект Ерлі\nколектор з'їдає базу", 13, fill="#eaf0fd", stroke=NEG))
    by = 246
    p.append(rect(58, by, 52, 40, fill="#eaf0fd", stroke=LINE, sw=1))      # емітер
    p.append(rect(110, by, 42, 40, fill="#fdf0e3", stroke=LINE, sw=1))     # база (вужча)
    p.append(rect(152, by, 52, 40, fill="#eaf0fd", stroke=LINE, sw=1))     # колектор
    p.append(arrow(168, by + 20, 150, by + 20, NEG, 2))                    # деплеція тисне на базу
    p.append(text(131, by + 64, "база вужча → q_b↓", 12, NEG))
    p.append(text(131, by + 82, "→ струм росте", 12, NEG))
    p.append(arrow(217, 200, 276, 210, NEG, 2.4))                          # вплив у центр

    # --- правий бік: q2, високий рівень інжекції ---
    p.append(fitbox(665, 150, 185, 64,
                    "q₂ — інжекція\nзаряд накопичується", 13, fill="#fdecea", stroke=POS))
    ry = 246
    p.append(rect(668, ry, 52, 40, fill="#eaf0fd", stroke=LINE, sw=1))
    p.append(rect(720, ry, 58, 40, fill="#f6c9c0", stroke=LINE, sw=1))     # база «важча» (насичена зарядом)
    p.append(rect(778, ry, 42, 40, fill="#eaf0fd", stroke=LINE, sw=1))
    for dxp in (728, 740, 752, 764):
        p.append(dot(dxp, ry + 20, 3, POS))
    p.append(text(744, ry + 64, "база «важча» → q_b↑", 12, POS))
    p.append(text(744, ry + 82, "→ β падає", 12, POS))
    p.append(arrow(663, 200, 604, 210, POS, 2.4))                         # вплив у центр

    # нижній підсумок
    p.append(text(W / 2, 438, "q_b = 1  →  модель точно зводиться до Еберса — Молла",
                  14, INK, bold=True))
    render(os.path.join(IMG, 'qb-breathing.svg'), W, H, "".join(p))


# ── figure 3: вихідні характеристики — пласкі (E-M) проти нахилених (G-P) ────
def fig_output():
    W, H = 760, 470
    x0, y0, xr, yt = 92, 402, 700, 70
    Vmax, Imax = 5.0, 6.0
    def X(v): return x0 + v / Vmax * (xr - x0)
    def Y(i): return y0 - i / Imax * (y0 - yt)
    p = []
    p.append(text(W / 2, 40, "Що додає модель у площині виходу", 16, INK, bold=True))
    p.append(arrow(x0, y0, xr + 10, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt - 10, INK, 2))
    p.append(text(xr + 6, y0 + 28, "V_CE, В", 12, INK, anchor="end", italic=True))
    p.append(text(x0 - 42, yt - 2, "I_К, мА", 12, INK, anchor="start", italic=True))
    for v in range(0, 6):
        px = X(v)
        p.append(line(px, y0, px, y0 + 5, INK, 1.3))
        p.append(text(px, y0 + 22, str(v), 11, MUTED))
    for i in range(0, 7, 2):
        py = Y(i)
        p.append(line(x0 - 5, py, x0, py, INK, 1.3))
        p.append(text(x0 - 12, py + 4, str(i), 11, MUTED, anchor="end"))

    VAF = 45.0
    for Ic0, col in ((2.0, NEG), (4.0, POS)):
        # Еберс — Молл: пласке плато (пунктир)
        emp = []
        v = 0.25
        while v <= Vmax + 1e-9:
            emp.append("%.1f,%.1f" % (X(v), Y(Ic0)))
            v += 0.05
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="6 4"/>'
                 % (" ".join(emp), MUTED))
        # Ґуммель — Пун: нахил (ефект Ерлі) + загин у насичення коло нуля
        gpp = []
        v = 0.0
        while v <= Vmax + 1e-9:
            sat = 1.0 - math.exp(-v / 0.08)          # м'який загин коло V_CE→0
            ic = Ic0 * (1.0 + v / VAF) * sat
            gpp.append("%.1f,%.1f" % (X(v), Y(ic)))
            v += 0.02
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(gpp), col))

    # підписи кривих
    p.append(text(X(4.9), Y(4.0 * (1 + 4.9 / VAF)) - 10, "G-P", 13, POS, anchor="end", bold=True))
    p.append(text(X(4.9), Y(2.0 * (1 + 4.9 / VAF)) - 10, "G-P", 13, NEG, anchor="end", bold=True))
    p.append(text(X(2.4), Y(4.0) + 18, "E-M: плато пласке", 12, MUTED))

    # анотація нахилу
    p.append(fitbox(X(0.5), Y(5.9), 250, 40,
                    "G-P: плато нахилене — ефект Ерлі\nусі лінії сходяться в −V_A", 11,
                    fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'output-early.svg'), W, H, "".join(p))


# ── figure 4 (hist): родовід моделі — вертикальна лінія часу ─────────────────
def fig_lineage():
    W, H = 900, 742
    sx = 258                       # x хребта часу
    p = []
    p.append(text(W / 2, 38, "Родовід моделі Ґуммеля — Пуна", 18, INK, bold=True))

    rows = [
        # (рік, заголовок, опис, роль)
        ("1954",    "Еберс і Молл",   "транзистор як два зчеплені діоди — скелет моделі", "anc"),
        ("1954",    "Вебстер",        "β падає при великому струмі: високий рівень інжекції", "anc"),
        ("1957",    "Бофой і Спаркс", "«транзистор, керований зарядом» — ідея заряд-контролю", "anc"),
        ("1964",    "Ґуммель",        "самоузгоджена ітерація рівнянь приладу — «метод Ґуммеля»", "anc"),
        ("1970",    "Ґуммель і Пун",  "інтегральна модель заряд-контролю · BSTJ 49, с. 827", "star"),
        ("1970-ті", "SPICE (Берклі)", "бере модель стандартним BJT симулятора", "after"),
        ("1985+",   "Нащадки",        "VBIC · Mextram · HICUM — те саме ядро, більше ефектів", "after"),
    ]

    y0, dy = 108, 92
    # хребет
    p.append(line(sx, y0 - 20, sx, y0 + (len(rows) - 1) * dy + 20, MUTED, 2.4))

    bx, bw, bh = 300, 566, 66
    for i, (yr, ttl, desc, role) in enumerate(rows):
        cy = y0 + i * dy
        # рік ліворуч від хребта
        p.append(text(sx - 34, cy + 5, yr, 15, INK, anchor="end", bold=True))
        # рамка праворуч
        if role == "star":
            fill, stroke, dotc, dotr = "#eaf6ee", FIELD, FIELD, 9
        elif role == "after":
            fill, stroke, dotc, dotr = FILL, LINE, INK, 6
        else:
            fill, stroke, dotc, dotr = "#f6f7f9", "#c4ccd4", MUTED, 6
        p.append(rect(bx, cy - bh / 2, bw, bh, fill=fill, stroke=stroke,
                      sw=2.0 if role == "star" else 1.4))
        p.append(line(sx, cy, bx, cy, MUTED, 1.4))          # відросток до рамки
        p.append(circle(sx, cy, dotr, fill=dotc, stroke=dotc, sw=1))
        p.append(text(bx + 18, cy - 8, ttl, 15, INK, anchor="start", bold=True))
        p.append(text(bx + 18, cy + 16, desc, 12.5, MUTED, anchor="start"))

    # згрупувати передісторію дужкою
    top = y0 - 8
    bot = y0 + 3 * dy + 8
    gx = 96
    p.append(line(gx, top, gx, bot, MUTED, 1.6))
    p.append(line(gx, top, gx + 8, top, MUTED, 1.6))
    p.append(line(gx, bot, gx + 8, bot, MUTED, 1.6))
    p.append(text(gx - 6, (top + bot) / 2 - 6, "перед-", 11, MUTED, anchor="end"))
    p.append(text(gx - 6, (top + bot) / 2 + 9, "історія", 11, MUTED, anchor="end"))

    render(os.path.join(IMG, 'lineage.svg'), W, H, "".join(p))


# ── figure (вставка math): профіль носіїв, число Ґуммеля, ICCR ───────────────
def fig_base_profile():
    W, H = 940, 540
    x0, y0, xr, yt = 156, 420, 690, 116
    p = []
    p.append(text(W / 2, 40, "Заряд у базі керує струмом: профіль носіїв і число Ґуммеля",
                  15, INK, bold=True))

    # осі
    p.append(arrow(x0, y0, xr + 150, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt - 14, INK, 2))
    p.append(text(xr + 148, y0 + 26, "x (поперек бази)", 12, INK, anchor="end", italic=True))
    p.append(text(x0 - 6, yt - 20, "густина носіїв (не в масштабі)", 12, INK, anchor="start", italic=True))

    # межі нейтральної бази
    p.append(line(x0, y0, x0, yt, MUTED, 1, dash="2 4"))
    p.append(line(xr, y0, xr, yt, MUTED, 1, dash="2 4"))
    p.append(text(x0, y0 + 34, "емітерний край", 12, NEG))
    p.append(text(xr, y0 + 34, "колекторний край", 12, POS))
    p.append(text((x0 + xr) / 2, y0 + 58, "нейтральна база, ширина W", 12, INK))

    # рівень легування N_A — число Ґуммеля = площа під ним
    yNA = 262
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eaf7ee" stroke="none"/>'
             % (x0, yNA, xr - x0, y0 - yNA))
    p.append(line(x0, yNA, xr, yNA, FIELD, 2.4))
    p.append(text(xr - 6, yNA - 9, "p ≈ N_A  (дірки = легування)", 12, FIELD, anchor="end", bold=True))
    p.append(text(x0 + 250, y0 - 26, "площа = число Ґуммеля  G_B = ∫ N_A dx", 12, FIELD, anchor="middle"))

    # профіль електронів n(x): трикутник від n(0) до ~0 на колекторі
    yn0 = 150
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#e7edfb" stroke="none"/>'
             % (x0, yn0, xr, y0, x0, y0))
    p.append(line(x0, yn0, xr, y0, NEG, 2.6))
    p.append(text(x0 + 8, yn0 - 12, "n(x): вприснуті електрони", 12, NEG, anchor="start", bold=True))

    # нахил → струм; площа → рухомий заряд
    sx = x0 + 120
    sy = yn0 + (y0 - yn0) * ((sx - x0) / (xr - x0))
    p.append(text(sx + 8, sy - 12, "нахил → I_К (дифузія)", 12, NEG, anchor="start"))
    p.append(text(x0 + 150, y0 - 58, "площа → рухомий заряд Q_diff", 12, NEG, anchor="start"))

    # формула n(0)
    p.append(fitbox(x0 - 2, 60, 256, 40, "n(0) = (n_i² / N_A)·e^(V_BE/Vₜ)", 13, fill=FILL, stroke=LINE))

    # Ерлі: колектор з'їдає базу (рамка вгорі праворуч + рухома межа)
    p.append(fitbox(468, 60, 224, 46,
                    "Ерлі: колектор з'їдає базу\n→ G_B ↓ → q_b < 1", 12, fill="#fdecea", stroke=POS))
    xe = xr - 48
    p.append(line(xe, y0, xe, yNA - 44, POS, 1.8, dash="5 3"))
    p.append(arrow(xr - 6, yNA - 24, xe + 2, yNA - 24, POS, 2))

    render(os.path.join(IMG, 'base-charge-profile.svg'), W, H, "".join(p))


# ── figure (вставка math): розв'язок квадратного рівняння для q_b ────────────
def fig_qb_master():
    W, H = 780, 470
    x0, y0, xr, yt = 100, 402, 700, 90
    q2max, qbmax = 8.0, 3.4

    def X(q): return x0 + q / q2max * (xr - x0)
    def Y(q): return y0 - q / qbmax * (y0 - yt)

    p = []
    p.append(text(W / 2, 40, "Розв'язок для q_b = ½·(1 + √(1 + 4·q₂))   (при q₁ = 1)",
                  15, INK, bold=True))
    p.append(arrow(x0, y0, xr + 12, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt - 12, INK, 2))
    p.append(text(xr + 8, y0 + 28, "q₂  (рівень інжекції)", 12, INK, anchor="end", italic=True))
    p.append(text(x0 - 34, yt - 4, "q_b", 13, INK, anchor="start", italic=True))

    for q in range(0, 9, 2):
        px = X(q)
        p.append(line(px, y0, px, y0 + 5, INK, 1.3))
        p.append(text(px, y0 + 22, str(q), 11, MUTED))
    for q in (0, 1, 2, 3):
        py = Y(q)
        p.append(line(x0 - 5, py, x0, py, INK, 1.3))
        p.append(text(x0 - 12, py + 4, str(q), 11, MUTED, anchor="end"))
        p.append(line(x0, py, xr, py, "#eceff2", 1))

    pts = []
    q = 0.0
    while q <= q2max + 1e-9:
        qb = 0.5 * (1 + math.sqrt(1 + 4 * q))
        pts.append("%.1f,%.1f" % (X(q), Y(qb)))
        q += 0.05
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), FIELD))

    la = []
    q = 0.0
    while q <= 1.25:
        la.append("%.1f,%.1f" % (X(q), Y(1 + q)))
        q += 0.05
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
             % (" ".join(la), NEG))
    ha = []
    q = 0.55
    while q <= q2max + 1e-9:
        ha.append("%.1f,%.1f" % (X(q), Y(math.sqrt(q))))
        q += 0.05
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>'
             % (" ".join(ha), POS))

    p.append(dot(X(0), Y(1), 4, INK))
    p.append(text(X(0) + 10, Y(1) - 9, "q_b = 1 → Еберс — Молл", 12, INK, anchor="start"))
    p.append(text(X(0.95), Y(1.95) - 12, "q_b ≈ 1 + q₂", 12, NEG, anchor="start"))
    p.append(text(X(6.3), Y(math.sqrt(6.3)) + 24, "q_b ≈ √q₂", 12, POS, anchor="middle"))
    p.append(fitbox(X(3.3), Y(3.36), 256, 44,
                    "мала q₂ → q_b ≈ 1 (β стале)\nвелика q₂ → q_b росте (β падає)",
                    11, fill=FILL, stroke=LINE))
    render(os.path.join(IMG, 'qb-master.svg'), W, H, "".join(p))


# ── figure (вставка proj): мапа видобування параметрів із графіка Ґуммеля ─────
def fig_extract_map():
    W, H = 980, 560
    p = []
    p.append(text(W / 2, 34, "Мапа видобування: яка риса кривої дає який параметр", 16, INK, bold=True))

    x0, y0, xr, yt = 118, 470, 606, 74
    vlo, vhi = 0.30, 0.82
    dlo, dhi = -12, -1
    def X(v): return x0 + (v - vlo) / (vhi - vlo) * (xr - x0)
    def Y(dec): return y0 - (dec - dlo) / (dhi - dlo) * (y0 - yt)

    p.append(arrow(x0, y0, xr + 12, y0, INK, 2))
    p.append(arrow(x0, y0, x0, yt - 12, INK, 2))
    p.append(text(xr + 8, y0 + 28, "V_BE, В", 12, INK, anchor="end", italic=True))
    p.append(text(x0 - 46, yt - 4, "log₁₀ I", 12, INK, anchor="start", italic=True))
    vx = 0.3
    while vx <= 0.821:
        px = X(vx)
        p.append(line(px, y0, px, y0 + 5, INK, 1.2))
        p.append(text(px, y0 + 21, "%.1f" % vx, 10, MUTED))
        vx += 0.1
    for d in range(dlo, dhi + 1, 2):
        py = Y(d)
        p.append(line(x0 - 5, py, x0, py, INK, 1.2))
        p.append(text(x0 - 11, py + 4, str(d), 10, MUTED, anchor="end"))
        p.append(line(x0, py, xr, py, "#eef1f4", 1))

    IS, BF, IKF, ISE, NE = 1e-14, 250.0, 0.08, 8e-13, 2.0
    ic_pts, ib_pts = [], []
    v = vlo
    while v <= vhi + 1e-9:
        ic, ib = gp(v, IS=IS, BF=BF, IKF=IKF, ISE=ISE, NE=NE)
        ic_pts.append("%.1f,%.1f" % (X(v), Y(math.log10(ic))))
        ib_pts.append("%.1f,%.1f" % (X(v), Y(math.log10(ib))))
        v += 0.004
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ic_pts), NEG))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ib_pts), POS))

    def onc(v): return X(v), Y(math.log10(gp(v, IS=IS, BF=BF, IKF=IKF, ISE=ISE, NE=NE)[0]))
    def onb(v): return X(v), Y(math.log10(gp(v, IS=IS, BF=BF, IKF=IKF, ISE=ISE, NE=NE)[1]))
    p.append(text(onc(0.70)[0], onc(0.70)[1] - 12, "I_К", 14, NEG, anchor="middle", bold=True))
    p.append(text(onb(0.66)[0] + 6, onb(0.66)[1] + 16, "I_Б", 14, POS, anchor="start", bold=True))

    mx1, my1 = onc(0.60)                        # середня пряма I_К → I_S, NF
    mx2c, my2c = onc(0.62); mx2b, my2b = onb(0.62)   # проміжок → BF
    mx3, my3 = onb(0.375)                        # низ I_Б → ISE, NE
    mx4, my4 = onc(0.775)                        # коліно I_К → IKF
    p.append(line(mx2c, my2c, mx2b, my2b, FIELD, 1.8, dash="3 3"))

    # праві виноски: рамка з полем + поводир до риси на кривій
    bx, bw = 794, 314
    def callout(cy, s, feat, col):
        p.append(line(feat[0], feat[1], bx - bw / 2, cy, MUTED, 1.2))
        p.append(circle(feat[0], feat[1], 3.4, fill=col, stroke=col, sw=1))
        p.append(fitbox(bx - bw / 2, cy - 26, bw, 52, s, 12, fill=FILL, stroke=col, sw=1.6))

    callout(100, "коліно I_К: тут крива відстала\nвід прямої в 1.6× → I_К = IKF", (mx4, my4), NEG)
    callout(178, "середня пряма I_К: нахил = 1/(NF·Vₜ);\nпродовж до V_BE=0 → перетин = I_S", (mx1, my1), NEG)
    callout(272, "проміжок між прямими на плато\n= ln β;  β-плато = BF", ((mx2c + mx2b) / 2, (my2c + my2b) / 2), FIELD)
    callout(368, "низ I_Б, власне пологіше коліно:\nнахил = 1/(NE·Vₜ), перетин = ISE", (mx3, my3), POS)

    p.append(fitbox(118, 512, 748, 38,
                    "VAF тут не видно (V_BC = 0): його беруть окремо — з нахилу плато вихідної кривої I_К–V_CE (ефект Ерлі)",
                    12, fill="#eef7f0", stroke=FIELD, sw=1.4))
    render(os.path.join(IMG, 'extract-map.svg'), W, H, "".join(p))


if __name__ == '__main__':
    fig_gummel()
    fig_qb()
    fig_output()
    fig_lineage()
    fig_base_profile()
    fig_qb_master()
    fig_extract_map()
    print("figs done:", sorted(os.listdir(IMG)))
