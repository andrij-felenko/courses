# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-troubles: дві біди живлення на одній шкалі частот ──────────────────────
# Ідея: зліва повільна пульсація перетворювача (велика амплітуда, низька f),
# справа швидкий шум чипа (мала амплітуда, висока f). Великий конденсатор
# закриває ліву смугу, дрібний — праву; разом увесь діапазон.

def fig_two_troubles():
    W, H = 720, 360
    ox, oy = 60, 250          # початок осі частот
    aw = 600
    p = []

    # вісь частот (логарифмічна, умовна) з підписами декад
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    decs = [("100 Гц", 0.0), ("10 кГц", 0.25), ("1 МГц", 0.5),
            ("10 МГц", 0.7), ("1 ГГц", 1.0)]
    for lab, t in decs:
        gx = ox + t * aw
        p.append(line(gx, oy, gx, oy + 5, color=LINE, sw=1.0))
        p.append(text(gx, oy + 19, lab, size=10, color=MUTED))
    p.append(text(ox + aw / 2, oy + 40, "частота завади (логарифмічна шкала)",
                  size=12, color=MUTED))

    # ── ліва «гора»: повільна пульсація перетворювача (велика, низька f) ──
    cxL = ox + 0.16 * aw
    # широкий низький горб
    pts = []
    for i in range(0, 81):
        x = ox + (i / 80.0) * (0.42 * aw)
        t = (x - cxL) / (0.13 * aw)
        y = oy - 120 * math.exp(-t * t)
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join(pts), POS))
    b, _, _ = textbox(cxL + 6, oy - 150, "пульсація перетворювача\nповільна · великий розмах",
                      size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.5, pad=8)
    p.append(b)

    # ── права «гора»: швидкий шум чипа (менша, висока f) ──
    cxR = ox + 0.78 * aw
    pts = []
    for i in range(0, 81):
        x = ox + (0.55 + (i / 80.0) * 0.45) * aw
        t = (x - cxR) / (0.10 * aw)
        y = oy - 78 * math.exp(-t * t)
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join(pts), NEG))
    b, _, _ = textbox(cxR - 4, oy - 112, "ривки логіки чипа\nдуже швидкі · малий розмах",
                      size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=8)
    p.append(b)

    # смуги покриття конденсаторами під віссю
    yb = oy + 56
    p.append(rect(ox, yb, 0.46 * aw, 16, fill="#fdecea", stroke=POS, sw=1.3, rx=3))
    p.append(text(ox + 0.23 * aw, yb + 12, "великий bulk закриває тут", size=10, color=POS))
    p.append(rect(ox + 0.52 * aw, yb, 0.48 * aw, 16, fill="#eaf0fd", stroke=NEG, sw=1.3, rx=3))
    p.append(text(ox + 0.76 * aw, yb + 12, "дрібний bypass закриває тут", size=10, color=NEG))

    render(os.path.join(OUT, "two-troubles.svg"), W, H, *p,
           title="Дві біди живлення — на різних частотах")


# ── impedance-vs-freq: V-крива опору конденсатора й роль ESL ──────────────────
# Ідея: опір кожного конденсатора має форму V — ємнісна вітка падає, індуктивна
# росте, дно на SRF (=ESR). Великий конденсатор має дно ліворуч, дрібний —
# праворуч; разом дають широку низькоомну долину. Логарифмічні обидві осі.

def fig_impedance():
    W, H = 720, 430
    ox, oy = 70, 330          # лівий-нижній кут поля
    aw, ah = 600, 270
    p = []

    # лог-шкала частоти від 1 кГц до 1 ГГц
    flo, fhi = 1e3, 1e9
    def xpos(f):
        return ox + (math.log10(f) - math.log10(flo)) / (math.log10(fhi) - math.log10(flo)) * aw
    # лог-шкала опору від 1 мОм (низ) до 100 Ом (верх)
    zlo, zhi = 1e-3, 1e2
    def ypos(z):
        return oy - (math.log10(z) - math.log10(zlo)) / (math.log10(zhi) - math.log10(zlo)) * ah

    # сітка частот
    for f, lab in [(1e3, "1 кГц"), (1e4, "10к"), (1e5, "100к"),
                   (1e6, "1 МГц"), (1e7, "10М"), (1e8, "100М"), (1e9, "1 ГГц")]:
        gx = xpos(f)
        p.append(line(gx, oy - ah, gx, oy, color="#eef1f5", sw=1.0))
        p.append(line(gx, oy, gx, oy + 5, color=LINE, sw=1.0))
        p.append(text(gx, oy + 18, lab, size=10, color=MUTED))
    # сітка опору
    for z, lab in [(1e-3, "1 мОм"), (1e-2, "10м"), (1e-1, "100м"),
                   (1.0, "1 Ом"), (1e1, "10"), (1e2, "100")]:
        gy = ypos(z)
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f5", sw=1.0))
        p.append(text(ox - 8, gy + 4, lab, size=10, color=MUTED, anchor="end"))

    # крива опору конденсатора: Z = sqrt( (1/(2pi f C))^2 + ESR^2 + (2pi f L)^2 )
    def zcurve(C, L, ESR, color, dash=None):
        pts = []
        for i in range(0, 201):
            f = flo * (fhi / flo) ** (i / 200.0)
            xc = 1.0 / (2 * math.pi * f * C)
            xl = 2 * math.pi * f * L
            z = math.sqrt((xc - xl) ** 2 + ESR ** 2)   # реактивна частина віднімається
            z = max(z, zlo)
            pts.append("%.1f,%.1f" % (xpos(f), ypos(z)))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>'
                % (" ".join(pts), color, d))

    # великий 100 мкФ: ESL 15 нГн, ESR 0.2 Ом → SRF ~130 кГц
    p.append(zcurve(100e-6, 15e-9, 0.2, POS))
    # дрібний 100 нФ: ESL 0.5 нГн, ESR 0.03 Ом → SRF ~22 МГц
    p.append(zcurve(100e-9, 0.5e-9, 0.03, NEG))

    # позначки дна (SRF)
    f1 = 1.0 / (2 * math.pi * math.sqrt(15e-9 * 100e-6))
    f2 = 1.0 / (2 * math.pi * math.sqrt(0.5e-9 * 100e-9))
    p.append(circle(xpos(f1), ypos(0.2), 5, fill="#fff", stroke=POS, sw=2))
    p.append(circle(xpos(f2), ypos(0.03), 5, fill="#fff", stroke=NEG, sw=2))

    # підписи кривих
    b, _, _ = textbox(xpos(8e3), ypos(8.0), "100 мкФ\n(електроліт)", size=11, bold=True,
                      color=POS, fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    p.append(b)
    b, _, _ = textbox(xpos(2.2e8), ypos(7.0), "100 нФ\n(кераміка)", size=11, bold=True,
                      color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.5, pad=7)
    p.append(b)

    # підписи природи віток
    p.append(text(xpos(3e3), ypos(0.01), "керує C", size=10, color=MUTED, italic=True))
    p.append(text(xpos(3e8), ypos(0.4), "керує ESL", size=10, color=MUTED, italic=True))

    # осі
    p.append(line(ox, oy - ah, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 40, "частота (логарифмічна шкала)", size=12, color=MUTED))
    p.append('<text x="22" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 22, %.0f)">опір конденсатора (лог.)</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    render(os.path.join(OUT, "impedance-vs-freq.svg"), W, H, *p,
           title="Опір конденсатора залежно від частоти (дно — на SRF)")


# ── cap-hierarchy: каскад фільтрації від перетворювача до ніжок чипа ───────────
# Ідея: перетворювач → bulk (велика, далеко) → bypass (мала, упритул) → чип.
# Естафета заряду; кожен рівень — свій діапазон частот і своя відстань.

def fig_hierarchy():
    W, H = 760, 360
    p = []
    railY = 120               # лінія живлення (шина)
    gndY = 270                # земля
    x0 = 70
    x_conv = 130
    x_bulk = 320
    x_byp = 520
    x_chip = 660

    # шина живлення й земля
    p.append(line(x0, railY, x_chip + 30, railY, color=POS, sw=2.4))
    p.append(line(x0, gndY, x_chip + 30, gndY, color=INK, sw=2.0))
    p.append(text(x0 - 4, railY - 10, "+V", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(x0 - 4, gndY + 20, "земля", size=11, color=MUTED, anchor="start"))

    # перетворювач (джерело)
    b = fitbox(x_conv - 52, railY - 36, 104, 72, "перетворювач\n(трохи брудна\nнапруга)",
               size=11, fill="#f4f6f8", stroke=LINE, sw=1.6, pad=6)
    p.append(b)

    def cap(x, label, sub, color, fill, big=False):
        # вертикальний конденсатор від шини до землі
        out = []
        midy = (railY + gndY) / 2
        out.append(line(x, railY, x, midy - 9, color=color, sw=2.0))
        # дві пластини
        plw = 22 if big else 15
        out.append(line(x - plw, midy - 9, x + plw, midy - 9, color=color, sw=3.0))
        out.append(line(x - plw, midy + 9, x + plw, midy + 9, color=color, sw=3.0))
        out.append(line(x, midy + 9, x, gndY, color=color, sw=2.0))
        b2, _, _ = textbox(x, midy + 42, label, size=11, bold=True, color=color,
                           fill=fill, stroke=color, sw=1.4, pad=6)
        out.append(b2)
        out.append(text(x, midy - 24, sub, size=9, color=MUTED))
        return "".join(out)

    p.append(cap(x_bulk, "bulk\n100 мкФ", "повільне · далеко", POS, "#fdecea", big=True))
    p.append(cap(x_byp, "bypass\n100 нФ", "швидке · упритул", NEG, "#eaf0fd"))

    # чип
    b = fitbox(x_chip - 44, railY - 34, 88, 68, "чип\n(ривки\nструму)",
               size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, pad=6)
    p.append(b)

    # естафета заряду — стрілки справа наліво над шиною
    ay = railY - 52
    p.append(arrow(x_chip - 30, ay, x_byp + 26, ay, color=FIELD, sw=1.8))
    p.append(arrow(x_byp - 26, ay, x_bulk + 30, ay, color=FIELD, sw=1.8))
    p.append(arrow(x_bulk - 30, ay, x_conv + 30, ay, color=FIELD, sw=1.8))
    p.append(text((x_byp + x_chip) / 2, ay - 8, "віддає миттєво", size=9, color=FIELD))
    p.append(text((x_bulk + x_byp) / 2, ay - 8, "підживлює", size=9, color=FIELD))
    p.append(text((x_conv + x_bulk) / 2, ay - 8, "підживлює", size=9, color=FIELD))

    p.append(text(W / 2, H - 14,
                  "заряд тече естафетою: чим ближче до чипа, тим менший і швидший конденсатор",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cap-hierarchy.svg"), W, H, *p,
           title="Ієрархія фільтрації: bulk → bypass → чип")


# ── lc-frequency-response: АЧХ LC-ланки з піком резонансу й гасінням ───────────
# Ідея (для вставки math-lc-filter): передавання LC-фільтра — три криві з різною
# добротністю. Висока Q (мало втрат) дає гострий ПІК над одиницею біля f0 — той
# самий резонансний підйом. Q = 0.707 (Баттерворт) — максимально пласка без піку.
# Низька Q (перегашено) — рано м'якне. Вище f0 усі сходяться на −40 дБ/декаду.

def fig_lc_response():
    W, H = 720, 440
    ox, oy = 70, 330
    aw, ah = 600, 280
    p = []

    # вісь X: f/f0 у лог-масштабі від 0.1 до 100
    rlo, rhi = 0.1, 100.0
    def xpos(r):
        return ox + (math.log10(r) - math.log10(rlo)) / (math.log10(rhi) - math.log10(rlo)) * aw
    # вісь Y: підсилення в дБ від +18 (верх) до −78 (низ)
    ghi, glo = 18.0, -78.0
    def ypos(g):
        return oy - (g - glo) / (ghi - glo) * ah

    # сітка X (декади f/f0)
    for r, lab in [(0.1, "0.1"), (1.0, "f₀"), (10.0, "10"), (100.0, "100")]:
        gx = xpos(r)
        p.append(line(gx, oy - ah, gx, oy, color="#eef1f5", sw=1.0))
        p.append(line(gx, oy, gx, oy + 5, color=LINE, sw=1.0))
        p.append(text(gx, oy + 18, lab, size=10, color=MUTED))
    # вертикаль f0 — виразніша
    p.append(line(xpos(1.0), oy - ah, xpos(1.0), oy, color=MUTED, sw=1.0, dash="3,3"))
    # сітка Y (дБ)
    for g in [12, 0, -12, -24, -36, -48, -60, -72]:
        gy = ypos(g)
        p.append(line(ox, gy, ox + aw, gy, color="#eef1f5", sw=1.0))
        lab = ("+%d" % g) if g > 0 else ("%d" % g)
        p.append(text(ox - 8, gy + 4, lab, size=9, color=MUTED, anchor="end"))
    # лінія 0 дБ — жирніша (рівень «один до одного»)
    p.append(line(ox, ypos(0), ox + aw, ypos(0), color="#cfd6df", sw=1.4))

    # |H| другого порядку: |H| = 1 / sqrt( (1-x^2)^2 + (x/Q)^2 ),  x = f/f0
    def hcurve(Q, color, dash=None, sw=2.6):
        pts = []
        for i in range(0, 241):
            x = rlo * (rhi / rlo) ** (i / 240.0)
            mag = 1.0 / math.sqrt((1 - x * x) ** 2 + (x / Q) ** 2)
            g = 20 * math.log10(mag)
            g = max(glo, min(ghi, g))
            pts.append("%.1f,%.1f" % (xpos(x), ypos(g)))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                % (" ".join(pts), color, sw, d))

    p.append(hcurve(8.0, POS))         # висока Q — гострий пік
    p.append(hcurve(0.707, FIELD))     # Баттерворт — пласко
    p.append(hcurve(0.3, NEG, dash="6,4"))  # перегашено — рано м'якне

    # позначка піку для Q=8 (висота піку ≈ 20log10 Q = 18 дБ)
    p.append(circle(xpos(1.0), ypos(20 * math.log10(8.0)), 4, fill="#fff", stroke=POS, sw=2))

    # підписи кривих
    b, _, _ = textbox(xpos(0.42), ypos(13.5), "Q ≈ 8\nрезонансний пік", size=11, bold=True,
                      color=POS, fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    p.append(b)
    b, _, _ = textbox(xpos(0.16), ypos(-20), "Q = 0.707\nпласко (Баттерворт)", size=11, bold=True,
                      color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.5, pad=7)
    p.append(b)
    b, _, _ = textbox(xpos(0.62), ypos(-40), "Q = 0.3\nперегашено", size=11, bold=True,
                      color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.4, pad=7)
    p.append(b)
    # нахил спаду
    p.append(text(xpos(38), ypos(-50), "−40 дБ/декаду", size=10, color=MUTED, italic=True))

    # осі
    p.append(line(ox, oy - ah, ox, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw / 2, oy + 40, "частота / f₀  (логарифмічна шкала)", size=12, color=MUTED))
    p.append('<text x="22" y="%.0f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90, 22, %.0f)">передавання, дБ</text>'
             % (oy - ah / 2, FONT, MUTED, oy - ah / 2))

    render(os.path.join(OUT, "lc-frequency-response.svg"), W, H, *p,
           title="АЧХ LC-ланки: пік за високої Q, пласко за Q=0.707")


# ── damping-rl: ланка ферит+конденсатор і три способи погасити резонанс ────────
# Ідея: Г-ланка (ферит послідовно, C на землю) утворює контур; показати, де
# додають опір — послідовно з C, паралельно феритові, — і що сам ферит на
# робочій частоті вже несе власний R (вбудоване гасіння).

def fig_damping():
    W, H = 760, 380
    p = []
    railY = 110
    gndY = 290
    x_in = 90
    x_fer = 250
    x_node = 430
    x_out = 660

    # шина живлення (вхід → ферит → вузол → вихід) і земля
    p.append(line(x_in, railY, x_fer - 34, railY, color=POS, sw=2.4))
    p.append(line(x_fer + 34, railY, x_out, railY, color=POS, sw=2.4))
    p.append(line(x_in, gndY, x_out, gndY, color=INK, sw=2.0))
    p.append(text(x_in - 6, railY - 10, "+V (брудна)", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x_out - 4, railY - 10, "+V (чиста)", size=11, color=FIELD, bold=True, anchor="end"))
    p.append(text(x_in - 6, gndY + 20, "земля", size=11, color=MUTED, anchor="start"))

    # ── ферит: прямокутник на шині з підписом R||L ──
    p.append(rect(x_fer - 34, railY - 16, 68, 32, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=4))
    p.append(text(x_fer, railY + 5, "ферит", size=11, color=INK, bold=True))
    b, _, _ = textbox(x_fer, railY - 44, "R_ф(f) + jωL_ф", size=10, bold=True,
                      color=MUTED, fill="#ffffff", stroke=LINE, sw=1.0, pad=5)
    p.append(b)
    p.append(text(x_fer, railY + 40, "перекриває дорогу ВЧ", size=9, color=MUTED, italic=True))

    # ── основний конденсатор C від вузла до землі (з опційним R_d послідовно) ──
    midy = (railY + gndY) / 2
    p.append(line(x_node, railY, x_node, midy - 28, color=NEG, sw=2.0))
    # пластини C
    p.append(line(x_node - 16, midy - 28, x_node + 16, midy - 28, color=NEG, sw=3.0))
    p.append(line(x_node - 16, midy - 12, x_node + 16, midy - 12, color=NEG, sw=3.0))
    p.append(text(x_node + 24, midy - 20, "C", size=12, color=NEG, bold=True, anchor="start"))
    # R_d у тій самій вітці (гасний опір)
    p.append(rect(x_node - 12, midy - 4, 24, 30, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=3))
    p.append(text(x_node + 24, midy + 14, "R_d", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(line(x_node, midy + 26, x_node, gndY, color=NEG, sw=2.0))
    p.append(text(x_node, midy - 20, "відводить ВЧ убік", size=9, color=MUTED, anchor="middle"))

    # ── підписи трьох способів гасіння ──
    b = fitbox(x_in - 4, gndY + 36, 230, 50,
               "1) R_d послідовно з C\n(забирає трохи ВЧ-послаблення)",
               size=10, fill="#eafaf1", stroke=FIELD, sw=1.4, pad=6, color=INK)
    p.append(b)
    b = fitbox(x_in + 250, gndY + 36, 230, 50,
               "2) ферит із потрібним R_ф\nна робочій частоті — гасить сам",
               size=10, fill="#f4f6f8", stroke=LINE, sw=1.4, pad=6, color=INK)
    p.append(b)
    b = fitbox(x_in + 500, gndY + 36, 170, 50,
               "3) C з помірним ESR\nдодає втрат у вітку",
               size=10, fill="#eaf0fd", stroke=NEG, sw=1.4, pad=6, color=INK)
    p.append(b)

    render(os.path.join(OUT, "damping-rl.svg"), W, H, *p,
           title="Г-ланка ферит+C і три способи погасити резонанс")


if __name__ == "__main__":
    fig_two_troubles()
    fig_impedance()
    fig_hierarchy()
    fig_lc_response()
    fig_damping()
    print("OK: figures written to", OUT)
