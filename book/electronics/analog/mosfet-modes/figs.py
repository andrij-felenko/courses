# -*- coding: utf-8 -*-
"""Фігури до теми «MOSFET: збагачений і збіднювальний режим».
Чотири фігури:
  two-types.svg      — два роди при Vgs=0: збагачений (каналу нема, поле творить) vs
                       збіднювальний (канал є, поле прибирає); нормально-закритий/відкритий
  transfer.svg       — передавальні криві ID(Vgs): де сидить поріг (+ vs −), звідки тече струм
  regions.svg        — вихідна характеристика ID(Vds): тріод (як резистор) → защемлення → насичення
  pinchoff.svg       — переріз каналу: при рості Vds канал звужується біля стоку й защемлюється
Запуск швидкий, без зациклень.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Два роди транзистора при Vgs = 0 ──────────────────────────────────────
def fig_two_types():
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 26, "Vgs = 0 (затвор не чіпаємо): хто проводить, хто ні", size=16, bold=True))

    def panel(x0, title, sub, channel_present, accent):
        out = []
        out.append(rect(x0, 56, 320, 300, fill="#fcfcfd", stroke=MUTED, sw=1.3))
        out.append(text(x0 + 160, 80, title, size=15, bold=True, color=accent))
        out.append(text(x0 + 160, 100, sub, size=12, color=MUTED))
        # підкладка
        bx, by, bw, bh = x0 + 40, 150, 240, 120
        out.append(rect(bx, by, bw, bh, fill="#eef1f4", stroke=LINE, sw=1.4))
        out.append(text(x0 + 160, by + bh - 10, "підкладка", size=11, color=MUTED))
        # витік / стік (n+ острівці)
        out.append(rect(bx + 8, by + 6, 46, 40, fill="#dfe7f5", stroke=NEG, sw=1.4))
        out.append(text(bx + 31, by + 30, "S", size=13, bold=True, color=NEG))
        out.append(rect(bx + bw - 54, by + 6, 46, 40, fill="#dfe7f5", stroke=NEG, sw=1.4))
        out.append(text(bx + bw - 31, by + 30, "D", size=13, bold=True, color=NEG))
        # затвор + ізолятор
        out.append(rect(bx + 54, by - 26, bw - 108, 12, fill="#e9e4d6", stroke="#b8a86a", sw=1.2))
        out.append(rect(bx + 54, by - 12, bw - 108, 6, fill="#cfe9d9", stroke=FIELD, sw=1.0))
        out.append(text(x0 + 160, by - 32, "затвор", size=11, color=MUTED))
        # канал між S і D
        cy = by + 18
        if channel_present:
            out.append(rect(bx + 54, cy, bw - 108, 14, fill="#cdeedd", stroke=FIELD, sw=1.6))
            out.append(text(x0 + 160, cy + 11, "канал є", size=11, bold=True, color=FIELD))
            out.append(arrow(bx + 8, by + 70, bx + bw - 8, by + 70, color=accent, sw=2.4))
            out.append(text(x0 + 160, by + 88, "струм тече вже зараз", size=12, bold=True, color=accent))
        else:
            out.append(line(bx + 54, cy + 7, bx + bw - 54, cy + 7, color=POS, sw=1.6, dash="5 4"))
            out.append(text(x0 + 160, cy + 11, "каналу нема", size=11, bold=True, color=POS))
            out.append(text(x0 + 160, by + 88, "розрив: струм не тече", size=12, bold=True, color=accent))
        return out

    f += panel(40, "Збагачений (нормально-закритий)",
               "поле затвора ТВОРИТЬ канал", False, POS)
    f += panel(400, "Збіднювальний (нормально-відкритий)",
               "поле затвора ПРИБИРАЄ канал", True, FIELD)
    render(os.path.join(IMG, "two-types.svg"), W, H, *f)


# ── 2. Передавальні криві ID(Vgs) ────────────────────────────────────────────
def fig_transfer():
    W, H = 720, 420
    ox, oy = 110, 330          # початок осей
    axw, axh = 540, 250
    f = []
    f.append(text(W / 2, 28, "Звідки тече струм: поріг збагаченого vs збіднювального", size=16, bold=True))
    # осі
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vgs", size=13, italic=True))
    f.append(text(ox - 70, oy - axh + 8, "ID  (струм стоку)", size=12, anchor="start", italic=True))
    # вісь Vgs=0
    zx = ox + 230
    f.append(line(zx, oy, zx, oy - axh, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(zx, oy + 20, "0", size=12, color=MUTED))

    import math
    # збагачений: поріг праворуч від 0 (Vth>0), струм лише за Vth
    vth_e = zx + 80
    pts = []
    for i in range(0, 230):
        x = vth_e + i
        if x > ox + axw - 6:
            break
        d = (x - vth_e) * 0.95
        y = oy - min(d, axh - 16)
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), POS))
    f.append(line(ox, oy, vth_e, oy, color=POS, sw=2.6))      # до порога струму нема
    f.append(circle(vth_e, oy, 4, fill="#fff", stroke=POS, sw=2))
    f.append(line(vth_e, oy, vth_e, oy + 8, color=POS, sw=1.4))
    f.append(text(vth_e, oy + 24, "Vth>0", size=12, bold=True, color=POS))
    f.append(text(ox + axw - 6, oy - axh + 60, "збагачений", size=13, bold=True, color=POS, anchor="end"))
    f.append(text(ox + axw - 6, oy - axh + 78, "(нормально-закритий)", size=11, color=POS, anchor="end"))

    # збіднювальний: поріг ліворуч від 0 (Vth<0); при Vgs=0 вже тече IDSS
    vth_d = zx - 130
    pts2 = []
    for i in range(0, 360):
        x = vth_d + i
        if x > ox + axw - 6:
            break
        d = (x - vth_d) * 0.62
        y = oy - min(d, axh - 16)
        pts2.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts2), FIELD))
    f.append(line(ox, oy, vth_d, oy, color=FIELD, sw=2.6))
    f.append(circle(vth_d, oy, 4, fill="#fff", stroke=FIELD, sw=2))
    f.append(line(vth_d, oy, vth_d, oy + 8, color=FIELD, sw=1.4))
    f.append(text(vth_d, oy + 24, "Vth<0", size=12, bold=True, color=FIELD))
    # позначити IDSS при Vgs=0
    idss_y = oy - (zx - vth_d) * 0.62
    f.append(circle(zx, idss_y, 4, fill="#fff", stroke=FIELD, sw=2))
    f.append(line(ox, idss_y, zx, idss_y, color=FIELD, sw=1.0, dash="3 4"))
    f.append(text(ox - 6, idss_y + 4, "IDSS", size=11, color=FIELD, anchor="end"))
    f.append(text(ox + 150, oy - axh + 30, "збіднювальний", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(ox + 150, oy - axh + 48, "(нормально-відкритий)", size=11, color=FIELD, anchor="start"))
    render(os.path.join(IMG, "transfer.svg"), W, H, *f)


# ── 3. Вихідна характеристика ID(Vds): тріод → насичення ─────────────────────
def fig_regions():
    W, H = 720, 430
    ox, oy = 100, 340
    axw, axh = 560, 270
    f = []
    f.append(text(W / 2, 26, "Два робочі режими каналу: тріод і насичення", size=16, bold=True))
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vds", size=13, italic=True))
    f.append(text(ox - 56, oy - axh + 6, "ID", size=13, anchor="start", italic=True))

    import math
    # кілька кривих для різних Vgs; кожна: парабола в тріоді до Vds=Vgs-Vth, далі плато
    curves = [(0.40, "#9bb7ef", 0.42), (0.62, NEG, 0.70), (0.86, "#16307a", 1.05)]
    for vov_frac, col, plat in curves:
        vp = ox + vov_frac * axw * 0.62        # точка защемлення (Vds = Vov)
        ipl = oy - plat / 1.05 * (axh - 30)    # рівень плато
        pts = []
        # тріод: росте, загинаючись (квадратично-увігнуто) до защемлення
        n = 60
        for i in range(0, n + 1):
            t = i / n
            x = ox + t * (vp - ox)
            # струм ~ ipl*(2t - t^2): монотонний, нахил до 0 на защемленні
            d = (2 * t - t * t)
            y = oy - d * (oy - ipl)
            pts.append("%.1f,%.1f" % (x, y))
        # насичення: майже горизонтально (легкий нахил — ефект каналу)
        for i in range(1, 60):
            x = vp + i * ((ox + axw - 14 - vp) / 60.0)
            y = ipl - i * 0.10
            pts.append("%.1f,%.1f" % (x, y))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), col))
        f.append(circle(vp, ipl, 3.5, fill="#fff", stroke=col, sw=1.8))
    f.append(text(ox + axw - 14, oy - axh + 70, "більший Vgs", size=12, color=NEG, anchor="end"))
    f.append(text(ox + axw - 14, oy - axh + 88, "→ вища крива", size=12, color=NEG, anchor="end"))

    # межа защемлення: Vds = Vgs - Vth (пунктир крізь точки защемлення)
    f.append(line(ox + 0.40 * axw * 0.62, oy - 0.40 / 1.05 * (axh - 30),
                  ox + 0.86 * axw * 0.62 + 30, oy - 0.86 / 1.05 * (axh - 30) - 40,
                  color=POS, sw=1.6, dash="6 4"))
    f.append(text(ox + 250, oy - 60, "межа: Vds = Vgs − Vth", size=12, bold=True, color=POS))

    # підписи зон
    f.append(text(ox + 70, oy - 18, "ТРІОД", size=13, bold=True, color=MUTED))
    f.append(text(ox + 70, oy - 4, "(як резистор)", size=10, color=MUTED))
    f.append(text(ox + 420, oy - 18, "НАСИЧЕННЯ", size=13, bold=True, color=MUTED))
    f.append(text(ox + 420, oy - 4, "(джерело струму)", size=10, color=MUTED))
    render(os.path.join(IMG, "regions.svg"), W, H, *f)


# ── 4. Защемлення каналу при рості Vds ───────────────────────────────────────
def fig_pinchoff():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Чому струм перестає рости: канал защемлюється біля стоку", size=15, bold=True))

    def cell(x0, title, vds_label, taper, pinched):
        out = []
        out.append(text(x0 + 150, 60, title, size=13, bold=True))
        out.append(text(x0 + 150, 78, vds_label, size=11, color=MUTED))
        bx, by, bw, bh = x0 + 20, 110, 260, 110
        out.append(rect(bx, by, bw, bh, fill="#eef1f4", stroke=LINE, sw=1.3))
        # S / D
        out.append(rect(bx + 6, by + bh - 46, 40, 40, fill="#dfe7f5", stroke=NEG, sw=1.3))
        out.append(text(bx + 26, by + bh - 22, "S", size=12, bold=True, color=NEG))
        out.append(rect(bx + bw - 46, by + bh - 46, 40, 40, fill="#dfe7f5", stroke=NEG, sw=1.3))
        out.append(text(bx + bw - 26, by + bh - 22, "D", size=12, bold=True, color=NEG))
        # затвор
        out.append(rect(bx + 46, by - 18, bw - 92, 10, fill="#e9e4d6", stroke="#b8a86a", sw=1.1))
        out.append(text(x0 + 150, by - 24, "затвор", size=10, color=MUTED))
        # канал як клин: товстий біля S, тонший біля D
        left_t = 18
        right_t = int(18 * (1 - taper))
        x1 = bx + 46
        x2 = bx + bw - 46
        ytop = by + 8
        poly = "%d,%d %d,%d %d,%d %d,%d" % (
            x1, ytop, x2, ytop, x2, ytop + right_t, x1, ytop + left_t)
        out.append('<polygon points="%s" fill="#cdeedd" stroke="%s" stroke-width="1.4"/>' % (poly, FIELD))
        if pinched:
            out.append(circle(x2 - 4, ytop + 2, 6, fill="#fdecea", stroke=POS, sw=1.8))
            out.append(text(x2 + 6, ytop + 6, "защемлено", size=11, bold=True, color=POS, anchor="start"))
            out.append(text(x0 + 150, by + bh + 26, "струм вийшов на стелю", size=11, bold=True, color=POS))
        else:
            out.append(text(x0 + 150, by + bh + 26, "канал суцільний", size=11, color=FIELD))
        return out

    f += cell(20, "Малий Vds", "канал майже рівний", 0.25, False)
    f += cell(380, "Vds ≥ Vgs − Vth", "біля стоку канал зник", 1.0, True)
    render(os.path.join(IMG, "pinchoff.svg"), W, H, *f)


# ── 5. Канал як клин із координатою x: заряд Q(x) і потенціал V(x) ────────────
#   Серце виведення: уздовж каналу потенціал росте 0→Vds, тому перекриття
#   місцеве (Vgs−Vth−V(x)) меншає, заряд рідшає — і це треба інтегрувати по x.
def fig_channel_x():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 26, "Канал уздовж координати x: заряд рідшає до стоку",
                  size=16, bold=True))
    bx, by, bw, bh = 70, 110, 620, 120
    # підкладка-смуга
    f.append(rect(bx, by, bw, bh, fill="#eef1f4", stroke=LINE, sw=1.3))
    # витік / стік
    f.append(rect(bx - 2, by + bh - 52, 50, 46, fill="#dfe7f5", stroke=NEG, sw=1.4))
    f.append(text(bx + 23, by + bh - 24, "S", size=14, bold=True, color=NEG))
    f.append(text(bx + 23, by + bh + 18, "x = 0", size=11, color=MUTED))
    f.append(text(bx + 23, by + bh + 33, "V = 0", size=11, color=NEG))
    f.append(rect(bx + bw - 48, by + bh - 52, 50, 46, fill="#dfe7f5", stroke=NEG, sw=1.4))
    f.append(text(bx + bw - 23, by + bh - 24, "D", size=14, bold=True, color=NEG))
    f.append(text(bx + bw - 23, by + bh + 18, "x = L", size=11, color=MUTED))
    f.append(text(bx + bw - 23, by + bh + 33, "V = Vds", size=11, color=NEG))
    # затвор зверху
    f.append(rect(bx + 50, by - 26, bw - 100, 12, fill="#e9e4d6", stroke="#b8a86a", sw=1.2))
    f.append(text(W / 2, by - 32, "затвор (Vgs)", size=12, color=MUTED))
    # канал-клин: товстий біля S, тонший біля D
    x1, x2 = bx + 50, bx + bw - 50
    ytop = by + 10
    left_t, right_t = 40, 14
    poly = "%d,%d %d,%d %d,%d %d,%d" % (x1, ytop, x2, ytop,
                                       x2, ytop + right_t, x1, ytop + left_t)
    f.append('<polygon points="%s" fill="#cdeedd" stroke="%s" stroke-width="1.5"/>' % (poly, FIELD))
    # стрілка струму ID (стала вздовж каналу)
    f.append(arrow(x1 + 8, ytop + 60, x2 - 8, ytop + 60, color=POS, sw=2.4))
    f.append(text(W / 2, ytop + 54, "ID — той самий у кожному перерізі", size=12, bold=True, color=POS))
    # підписи місцевого заряду
    f.append(text(x1 + 40, ytop - 4, "Q густий", size=11, bold=True, color=FIELD))
    f.append(text(x2 - 44, ytop - 4, "Q рідкий", size=11, bold=True, color=FIELD))
    # елемент dx
    xm = bx + 50 + (bw - 100) * 0.55
    f.append(line(xm, ytop - 4, xm, ytop + left_t + 24, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(xm + 22, ytop - 4, xm + 22, ytop + left_t + 24, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(xm + 11, ytop + left_t + 38, "dx", size=11, italic=True, color=MUTED))
    # формула місцевого заряду
    b2, w2, h2 = textbox(W / 2, by + bh + 70,
                         "місцеве перекриття:  Vgs − Vth − V(x)\n"
                         "заряд на одиницю довжини:  Q(x) = Cox·W·(Vgs − Vth − V(x))",
                         size=12, fill="#f7fbf8", stroke=FIELD, pad=10)
    f.append(b2)
    render(os.path.join(IMG, "channel-x.svg"), W, H, *f)


# ── 6. Тріодна парабола й дотик насичення: неперервне зшивання на Vds=Vov ─────
#   ID(Vds) при сталому Vgs: парабола росте до вершини при Vds=Vov (нахил=0),
#   там підхоплює горизонтальна полиця насичення — гладко, без зламу.
def fig_parabola_join():
    W, H = 720, 420
    ox, oy = 90, 330
    axw, axh = 560, 250
    f = []
    f.append(text(W / 2, 26, "Тріодна парабола сама лягає в полицю насичення",
                  size=16, bold=True))
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 24, "Vds", size=13, italic=True))
    f.append(text(ox - 60, oy - axh + 6, "ID", size=13, anchor="start", italic=True))

    # парабола ID = k[(Vov)Vds − Vds²/2]; вершина при Vds=Vov, ID=k·Vov²/2
    vov_px = 300.0                  # екранна довжина до защемлення
    peak = axh - 40                 # висота вершини
    vp_x = ox + vov_px
    pk_y = oy - peak
    pts = []
    n = 70
    for i in range(0, n + 1):
        t = i / n                   # t = Vds/Vov від 0 до 1
        x = ox + t * vov_px
        d = (2 * t - t * t)         # нормований струм: 0→1 з нахилом 0 на t=1
        y = oy - d * peak
        pts.append("%.1f,%.1f" % (x, y))
    # суцільна тріодна гілка
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), NEG))
    # продовження параболи ПУНКТИРОМ за вершину (куди вона «хотіла б» піти — униз)
    pts2 = []
    for i in range(0, 36):
        t = 1 + i / 70.0
        x = ox + t * vov_px
        if x > ox + axw - 10:
            break
        d = (2 * t - t * t)
        y = oy - d * peak
        pts2.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>' % (" ".join(pts2), MUTED))
    # полиця насичення: горизонталь від вершини
    f.append(line(vp_x, pk_y, ox + axw - 14, pk_y, color=POS, sw=2.6))
    # вершина-точка зшивання
    f.append(circle(vp_x, pk_y, 4.5, fill="#fff", stroke=INK, sw=2))
    f.append(line(vp_x, oy, vp_x, pk_y, color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(vp_x, oy + 20, "Vds = Vov", size=12, bold=True, color=INK))
    # рівень ID насичення
    f.append(line(ox, pk_y, vp_x, pk_y, color=MUTED, sw=1.0, dash="3 4"))
    f.append(text(ox - 6, pk_y + 4, "k·Vov²/2", size=11, color=POS, anchor="end"))
    # підписи гілок
    f.append(text(ox + 120, oy - 70, "тріод: парабола", size=12, bold=True, color=NEG))
    f.append(text(vp_x + 70, pk_y - 14, "насичення: полиця", size=12, bold=True, color=POS))
    f.append(text(vp_x + 70, pk_y + 30, "(парабола пунктиром —", size=10, color=MUTED))
    f.append(text(vp_x + 70, pk_y + 44, "куди б пішла без защемлення)", size=10, color=MUTED))
    # позначка «нахил = 0 у вершині»
    f.append(line(vp_x - 40, pk_y, vp_x + 40, pk_y, color=FIELD, sw=1.4))
    f.append(text(vp_x, pk_y - 12, "нахил = 0", size=10, bold=True, color=FIELD))
    render(os.path.join(IMG, "parabola-join.svg"), W, H, *f)


# ── 7. Два множники квадрата: густина × поле ─────────────────────────────────
#   Перекриття водночас згущує канал (∝ Vov) і збільшує дрейфове поле (∝ Vov);
#   струм — добуток, тому ∝ Vov². Дві стрілки ростуть, добуток — квадрат.
def fig_two_factors():
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 26, "Чому квадрат: перекриття діє двічі", size=16, bold=True))

    def bar(cx, label, sub, frac, col):
        out = []
        x0, y0, bw, bh = cx - 70, 90, 140, 130
        out.append(text(cx, y0 - 14, label, size=13, bold=True, color=col))
        out.append(rect(x0, y0, bw, bh, fill="#fcfcfd", stroke=MUTED, sw=1.2))
        fh = bh * frac
        out.append(rect(x0 + 18, y0 + bh - fh, bw - 36, fh, fill=col, stroke="none", sw=0, rx=4))
        out.append(text(cx, y0 + bh + 18, sub, size=11, color=MUTED))
        return out

    f += bar(150, "густина носіїв", "∝ Vov", 0.62, FIELD)
    f.append(text(290, 168, "×", size=30, bold=True, color=INK))
    f += bar(430, "дрейфове поле", "∝ Vov", 0.62, NEG)
    f.append(text(580, 168, "=", size=30, bold=True, color=INK))
    # результат: квадрат
    b, w, h = textbox(640, 155, "струм\n∝ Vov²", size=15, bold=True,
                      fill="#fdecea", stroke=POS, color=POS, pad=12)
    f.append(b)
    f.append(text(W / 2, 270,
                  "Підняв перекриття вдвічі — і носіїв удвічі більше, і тягне їх удвічі сильніше: струм у 4 рази.",
                  size=12, color=INK))
    render(os.path.join(IMG, "two-factors.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_types()
    fig_transfer()
    fig_regions()
    fig_pinchoff()
    fig_channel_x()
    fig_parabola_join()
    fig_two_factors()
    print("OK: 7 figures ->", IMG)
