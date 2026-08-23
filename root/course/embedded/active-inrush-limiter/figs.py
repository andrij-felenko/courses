# -*- coding: utf-8 -*-
"""Фігури до теми «Активний обмежувач пускового струму».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── 1. Кидок пускового струму голого конденсатора ────────────────────────────
def fig_inrush_spike():
    W, H = 720, 380
    f = []
    x0, y0 = 90, 300          # початок осей
    xr, yt = 670, 70
    f.append(arrow(x0, y0, xr, y0, color=INK, sw=2))   # вісь часу
    f.append(arrow(x0, y0, x0, yt, color=INK, sw=2))   # вісь струму
    f.append(text((x0 + xr) / 2, y0 + 36, "час від ввімкнення  →", size=13, color=INK))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">струм у плату  →</text>'
             % (34, (y0 + yt) / 2, FONT, INK, 34, (y0 + yt) / 2))

    peak_y = yt + 18          # висота піку
    base_y = y0 - 22          # рівень робочого струму (тонка лінія над нулем)
    xs = x0 + 30              # момент ввімкнення

    # гострий пік: різкий зліт і експоненційний спад
    pts = [(x0, y0)]
    pts.append((xs, y0))
    pts.append((xs + 4, peak_y))      # майже вертикальний фронт
    for i in range(1, 80):
        t = i / 79.0
        x = xs + 4 + t * 150
        y = peak_y + (base_y - peak_y) * (1 - math.exp(-t * 4.2))
        pts.append((x, y))
    # далі рівний робочий струм
    pts.append((xr - 20, base_y))
    f.append(polyline(pts, color=RED, sw=2.6))

    # лінія робочого струму — для контрасту
    f.append(line(xs, base_y, xr - 20, base_y, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(xr - 70, base_y - 10, "робочий струм", size=11.5, color=MUTED))

    # підписи піку
    f.append(line(xs + 4, peak_y, xs + 130, peak_y, color=MUTED, sw=1, dash="3 3"))
    bx = fitbox(xs + 60, peak_y - 46, 230, 34,
                "пік ≈ десятки ампер\n(U / крихітний опір шляху)",
                size=12, fill="#fdecea", stroke=RED, color="#7a1d12")
    f.append(bx)

    f.append(text(xs - 2, y0 + 18, "вмик.", size=11, color=INK))

    return render(os.path.join(IMG, "inrush-spike.svg"), W, H, *f,
                  title="Голий конденсатор: гострий кидок струму при ввімкненні")


# ── 2. Кістяк активного обмежувача ───────────────────────────────────────────
def fig_active_circuit():
    W, H = 720, 400
    f = []

    ytop = 110                # верхня (плюсова) силова шина
    ygnd = 320                # нижня шина (земля) — рівна горизонталь
    xL, xR = 70, 660          # ліва й права межі шин

    # MOSFET у розрив верхньої шини
    mw, mh = 120, 64
    mx = 250
    my = ytop - mh / 2
    sx_in = mx                # лівий вивід (стік)
    sx_out = mx + mw          # правий вивід (витік)

    # --- верхня шина: вхід → MOSFET → вихід ---
    f.append(text(xL, ytop - 22, "вхід +", size=12.5, color=POS, anchor="start", bold=True))
    f.append(line(xL, ytop, sx_in, ytop, color=INK, sw=2.6))
    f.append(rect(mx, my, mw, mh, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=8))
    f.append(text(mx + mw / 2, ytop - 4, "MOSFET", size=14, color=NEG, bold=True))
    f.append(text(mx + mw / 2, ytop + 16, "у розрив шини", size=10.5, color=MUTED))
    f.append(line(sx_out, ytop, xR, ytop, color=INK, sw=2.6))

    # --- нижня шина (земля) — одна рівна лінія ---
    f.append(text(xL, ygnd - 10, "вхід −", size=12.5, color=NEG, anchor="start"))
    f.append(line(xL, ygnd, xR, ygnd, color=INK, sw=2.6))
    f.append(gnd((xL + xR) / 2, ygnd))

    # --- RC-ланка на затвор (під MOSFET, нічого не перетинає) ---
    gx = mx + mw / 2          # вивід затвора по центру знизу
    gy_top = my + mh          # від низу корпусу
    gy_node = 200             # вузол затвора
    f.append(line(gx, gy_top, gx, gy_node, color=INK, sw=2))
    f.append(text(gx + 8, gy_top + 22, "затвор", size=10.5, color=INK, anchor="start"))

    # резистор від плюсової шини (точка перед MOSFET) вниз і в затвор
    rtap = 160                # точка відведення на плюсовій шині
    f.append(circle(rtap, ytop, 3, fill=INK, stroke=INK, sw=1))     # вузол-відгалуження
    f.append(line(rtap, ytop, rtap, gy_node, color=INK, sw=2))
    f.append(resistor_h(rtap, gy_node, gx, gy_node))
    f.append(text((rtap + gx) / 2, gy_node - 12, "R_зат (великий)", size=10.5, color=MUTED))

    # конденсатор затвора з вузла на землю
    cgy1 = gy_node + 26
    f.append(line(gx, gy_node, gx, cgy1, color=INK, sw=2))
    f.append(line(gx - 16, cgy1, gx + 16, cgy1, color=INK, sw=2.6))
    f.append(line(gx - 16, cgy1 + 7, gx + 16, cgy1 + 7, color=INK, sw=2.6))
    f.append(line(gx, cgy1 + 7, gx, ygnd, color=INK, sw=2))
    f.append(text(gx + 22, cgy1 + 2, "C_зат", size=10.5, color=MUTED, anchor="start"))

    # --- навантаження: конденсатор + плата, обидва на землю ---
    ccx = 500
    f.append(line(ccx, ytop, ccx, ytop + 30, color=INK, sw=2.2))
    f.append(line(ccx - 18, ytop + 30, ccx + 18, ytop + 30, color=INK, sw=2.6))
    f.append(line(ccx - 18, ytop + 37, ccx + 18, ytop + 37, color=INK, sw=2.6))
    f.append(line(ccx, ytop + 37, ccx, ygnd, color=INK, sw=2))
    f.append(text(ccx + 24, ytop + 26, "C_навант", size=11, color=INK, anchor="start"))

    pbw, pbh = 70, 54
    pbx = 580
    pby = ytop + 60
    f.append(rect(pbx, pby, pbw, pbh, fill=FILL, stroke=INK, sw=1.8, rx=6))
    f.append(text(pbx + pbw / 2, pby + 24, "плата", size=11.5, color=INK))
    f.append(text(pbx + pbw / 2, pby + 40, "(навант.)", size=9.5, color=MUTED))
    pcx = pbx + pbw / 2
    f.append(line(pcx, ytop, pcx, pby, color=INK, sw=2.2))
    f.append(line(pcx, pby + pbh, pcx, ygnd, color=INK, sw=2))

    # вузли-точки злиття на шинах
    for nx in (ccx, pcx):
        f.append(circle(nx, ytop, 3, fill=INK, stroke=INK, sw=1))
        f.append(circle(nx, ygnd, 3, fill=INK, stroke=INK, sw=1))
    f.append(circle(gx, ygnd, 3, fill=INK, stroke=INK, sw=1))

    # підпис-висновок
    f.append(text(W / 2, H - 22,
                  "великий R_зат повільно заряджає затвор → канал прочиняється плавно → "
                  "вихід наростає без кидка", size=11.5, color="#7a5a00"))

    return render(os.path.join(IMG, "active-circuit.svg"), W, H, *f,
                  title="Активний обмежувач: MOSFET як керований опір у шині")


# ── 3. Потужність на кристалі під час пуску (SOA) ────────────────────────────
def fig_soa_power():
    W, H = 720, 470
    f = []

    x0 = 95
    xr = 670
    # верхня панель: напруги й струм
    yt1, yb1 = 70, 210
    f.append(arrow(x0, yb1, xr, yb1, color=INK, sw=1.8))
    f.append(arrow(x0, yb1, x0, yt1, color=INK, sw=1.8))
    f.append(text(W / 2, yt1 - 16, "Напруги й струм під час наростання", size=13.5, bold=True, color=INK))

    n = 120
    tw = xr - x0 - 30
    # вихідна напруга росте (1 - e^-t)
    Vout = [(x0 + (i / (n - 1.0)) * tw,
             yb1 - (yb1 - yt1 - 10) * (1 - math.exp(-(i / (n - 1.0)) * 3.2)))
            for i in range(n)]
    # напруга на транзисторі = живлення - вихід (спадає)
    Vds = [(x0 + (i / (n - 1.0)) * tw,
            yt1 + 10 + (yb1 - yt1 - 10) * (1 - math.exp(-(i / (n - 1.0)) * 3.2)))
           for i in range(n)]
    f.append(polyline(Vout, color=GRN, sw=2.4))
    f.append(polyline(Vds, color=RED, sw=2.4))
    # струм заряду ~ сталий (трохи спадає до кінця)
    Icur = yb1 - 40
    f.append(line(x0, Icur, x0 + tw, Icur, color=NEG, sw=2.2, dash="6 4"))

    f.append(text(x0 + tw - 4, Vout[-1][1] - 8, "вихід U_вих", size=11, color=GRN, anchor="end"))
    f.append(text(x0 + 8, Vds[0][1] + 4, "на транзисторі (живл.−вих.)", size=11, color=RED, anchor="start"))
    f.append(text(x0 + tw - 4, Icur - 8, "струм заряду I", size=11, color=NEG, anchor="end"))

    # нижня панель: миттєва потужність = Vds * I
    yt2, yb2 = 280, 420
    f.append(arrow(x0, yb2, xr, yb2, color=INK, sw=1.8))
    f.append(arrow(x0, yb2, x0, yt2, color=INK, sw=1.8))
    f.append(text(W / 2, yt2 - 16, "Миттєва потужність у кристалі  =  напруга × струм", size=13.5, bold=True, color=INK))
    f.append(text((x0 + xr) / 2, yb2 + 34, "час наростання  →", size=12.5, color=INK))

    # P(t) ~ Vds(t) (бо I майже сталий): горб найвищий на початку
    Pmax = yt2 + 12
    pwr = []
    for i in range(n):
        t = i / (n - 1.0)
        vds = math.exp(-t * 3.2)          # частка від повної напруги
        icur = 1.0 - 0.15 * t             # майже сталий струм
        p = vds * icur
        pwr.append((x0 + t * tw, yb2 - (yb2 - Pmax) * p))
    # площа під кривою
    area = "%.2f,%.2f " % (x0, yb2)
    area += " ".join("%.2f,%.2f" % (x, y) for x, y in pwr)
    area += " %.2f,%.2f" % (x0 + tw, yb2)
    f.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.7"/>' % area)
    f.append(polyline(pwr, color=RED, sw=2.6))

    bx = fitbox(x0 + tw * 0.42, Pmax + 6, 250, 52,
                "уся ця площа — енергія ½·C·U²,\nщо гріє кристал за один пуск;\n"
                "розтягнеш час — горб подовжиться",
                size=11, fill="#fff7e6", stroke="#d9a441", color="#8a5a00")
    f.append(bx)

    return render(os.path.join(IMG, "soa-power.svg"), W, H, *f,
                  title="Чому повільний пуск гріє транзистор: потужність у кристалі")


# ── допоміжні елементи схеми ─────────────────────────────────────────────────
def gnd(x, y):
    return (line(x, y, x, y + 6, color=INK, sw=2)
            + line(x - 12, y + 6, x + 12, y + 6, color=INK, sw=2.4)
            + line(x - 7, y + 11, x + 7, y + 11, color=INK, sw=2)
            + line(x - 3, y + 16, x + 3, y + 16, color=INK, sw=2))


def resistor_h(x1, y, x2, y2=None):
    """Горизонтальний резистор-зиґзаґ між (x1,y) і (x2,y)."""
    y2 = y if y2 is None else y2
    seg = (x2 - x1)
    zx = x1 + seg * 0.18
    zw = seg * 0.64
    pts = [(x1, y), (zx, y)]
    k = 6
    for i in range(k):
        xx = zx + zw * (i + 0.5) / k
        yy = y + (-8 if i % 2 == 0 else 8)
        pts.append((xx, yy))
    pts.append((zx + zw, y))
    pts.append((x2, y))
    return polyline(pts, color=INK, sw=2)


def pin(x, y, side, name, color=INK):
    """Підписана ніжка корпусу: короткий вивід + назва. side ∈ L/R."""
    if side == "L":
        return (line(x, y, x - 16, y, color=INK, sw=2)
                + text(x - 22, y + 4, name, size=11, color=color, anchor="end"))
    return (line(x, y, x + 16, y, color=INK, sw=2)
            + text(x + 22, y + 4, name, size=11, color=color, anchor="start"))


# ── 4. Блок-схема контролера гарячого підключення ────────────────────────────
def fig_hotswap_block():
    W, H = 760, 480
    f = []

    # силовий тракт угорі: VIN → шунт → MOSFET → VOUT
    yb = 90
    xL, xR = 60, 700
    f.append(text(xL, yb - 18, "VIN +", size=12.5, color=POS, anchor="start", bold=True))
    f.append(line(xL, yb, 150, yb, color=INK, sw=3))
    # шунт
    f.append(resistor_h(150, yb, 250, yb))
    f.append(text(200, yb - 12, "шунт R_ш", size=10.5, color=MUTED))
    f.append(line(250, yb, 360, yb, color=INK, sw=3))
    # MOSFET-символ (спрощений блок)
    f.append(rect(360, yb - 26, 96, 52, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=8))
    f.append(text(408, yb - 2, "N-MOSFET", size=11.5, color=NEG, bold=True))
    f.append(text(408, yb + 14, "(зовнішній)", size=9.5, color=MUTED))
    f.append(line(456, yb, xR, yb, color=INK, sw=3))
    f.append(text(xR, yb - 18, "VOUT → плата", size=12.5, color=POS, anchor="end", bold=True))
    f.append(circle(150, yb, 3, fill=INK, stroke=INK, sw=1))
    f.append(circle(250, yb, 3, fill=INK, stroke=INK, sw=1))

    # корпус контролера
    cx0, cy0, cw, ch = 175, 200, 360, 230
    f.append(rect(cx0, cy0, cw, ch, fill="#ffffff", stroke=INK, sw=2.2, rx=12))
    f.append(text(cx0 + cw / 2, cy0 + 26, "КОНТРОЛЕР ГАРЯЧОГО ПІДКЛЮЧЕННЯ",
                  size=13, color=INK, bold=True))

    # внутрішні блоки
    def iblk(cx, cy, s, col=INK, fill="#f4f6f8"):
        b, w, h = textbox(cx, cy, s, size=10.5, fill=fill, stroke=col, sw=1.6, color=INK)
        return b

    f.append(iblk(cx0 + 95, cy0 + 70, "струмовий\nкомпаратор\n(поріг ≈ 50 мВ)", col=POS, fill="#fdecea"))
    f.append(iblk(cx0 + 265, cy0 + 70, "таймер\nвідключення", col="#d9a441", fill="#fff7e6"))
    f.append(iblk(cx0 + 95, cy0 + 158, "зарядний насос\nзатвора (dV/dt)", col=NEG, fill="#eaf0fd"))
    f.append(iblk(cx0 + 265, cy0 + 158, "логіка:\nретрай / латч", col=FIELD, fill="#eafaf0"))

    # зв'язки зі шунтом (SENSE+/SENSE−)
    f.append(line(150, yb, 150, cy0 + 70, color=POS, sw=1.6, dash="4 3"))
    f.append(line(150, cy0 + 70, cx0 + 35, cy0 + 70, color=POS, sw=1.6, dash="4 3"))
    f.append(text(140, cy0 + 58, "SENSE", size=9.5, color=POS, anchor="end"))
    f.append(line(250, yb, 250, cy0 - 10, color=POS, sw=1.2, dash="4 3"))
    f.append(line(250, cy0 - 10, 250, cy0, color=POS, sw=1.2, dash="4 3"))

    # GATE до затвора MOSFET
    f.append(line(cx0 + 95, cy0 + 130, cx0 + 95, 150, color=NEG, sw=2))
    f.append(line(cx0 + 95, 150, 408, 150, color=NEG, sw=2))
    f.append(line(408, 150, 408, yb + 26, color=NEG, sw=2))
    f.append(text(cx0 + 100, 145, "GATE", size=10, color=NEG, anchor="start", bold=True))

    # зовнішні ніжки контролера
    f.append(pin(cx0, cy0 + 110, "L", "VDD", color=POS))
    f.append(pin(cx0, cy0 + 135, "L", "EN/UVLO"))
    f.append(pin(cx0, cy0 + 200, "L", "C_таймер", color="#8a5a00"))
    f.append(pin(cx0 + cw, cy0 + 110, "R", "PG", color=FIELD))
    f.append(pin(cx0 + cw, cy0 + 135, "R", "FLT", color=POS))
    f.append(pin(cx0 + cw, cy0 + 200, "R", "GND", color=NEG))

    f.append(text(W / 2, H - 16,
                  "одна мікросхема: міряє струм на шунті, веде затвор повільно, "
                  "рахує час аварії й сигналить PG/FLT",
                  size=11.5, color="#555"))

    return render(os.path.join(IMG, "hotswap-block.svg"), W, H, *f,
                  title="Що всередині контролера гарячого підключення")


# ── 5. Таймер відключення: дозволений горб vs аварія ─────────────────────────
def fig_hotswap_timer():
    W, H = 760, 430
    f = []
    x0, y0 = 90, 330
    xr, yt = 700, 80
    f.append(arrow(x0, y0, xr, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, yt, color=INK, sw=1.8))
    f.append(text((x0 + xr) / 2, y0 + 34, "час  →", size=12.5, color=INK))
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %.1f)">струм крізь шунт  →</text>'
             % ((y0 + yt) / 2, FONT, INK, (y0 + yt) / 2))

    # поріг компаратора (горизонталь)
    thr = 150
    f.append(line(x0, thr, xr, thr, color=POS, sw=1.8, dash="6 4"))
    f.append(text(xr - 6, thr - 8, "поріг ≈ 50 мВ / R_ш", size=11, color=POS, anchor="end"))
    base = y0 - 18
    f.append(line(x0, base, xr, base, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(x0 + 6, base - 7, "робочий струм", size=10, color=MUTED, anchor="start"))

    # 1) дозволений пусковий горб: трохи нижче порога, короткий
    p1 = [(x0 + 10, base)]
    for i in range(40):
        t = i / 39.0
        x = x0 + 10 + t * 150
        y = base - (base - (thr + 16)) * math.sin(math.pi * t)
        p1.append((x, y))
    p1.append((x0 + 170, base))
    f.append(polyline(p1, color=FIELD, sw=2.6))
    f.append(text(x0 + 85, thr + 40, "пуск:\nгорб нижче порога", size=10.5, color=FIELD))

    # 2) перевантаження: над порогом, таймер біжить, відключення
    xs = 330
    p2 = [(xs, base)]
    p2.append((xs + 8, thr - 60))
    p2.append((xs + 150, thr - 70))   # тримається над порогом
    f.append(polyline(p2, color="#d9a441", sw=2.6))
    # зона "таймер біжить"
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff7e6" '
             'stroke="#d9a441" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.85" rx="4"/>'
             % (xs + 8, thr - 78, 150, (y0 - (thr - 78)) - 2))
    f.append(text(xs + 83, thr - 88, "таймер біжить", size=10.5, color="#8a5a00"))
    # момент відключення
    f.append(line(xs + 158, base, xs + 158, thr - 70, color=POS, sw=1.2, dash="2 3"))
    p2b = [(xs + 158, thr - 70), (xs + 160, base)]
    f.append(polyline(p2b, color=POS, sw=2.6))
    f.append(text(xs + 162, thr - 30, "MOSFET\nвимкнено", size=10.5, color=POS, anchor="start"))

    # 3) короткий: різкий пік → миттєве відключення (швидкий компаратор)
    xsc = 600
    f.append(line(xsc, base, xsc + 4, yt + 20, color=POS, sw=2.6))
    f.append(line(xsc + 4, yt + 20, xsc + 7, base, color=POS, sw=2.6))
    f.append(text(xsc + 12, yt + 36, "коротке:\nшвидкий\nкомпаратор", size=10, color=POS, anchor="start"))

    return render(os.path.join(IMG, "hotswap-timer.svg"), W, H, *f,
                  title="Як контролер вирішує: пуск терпіти, аварію — рвати")


if __name__ == "__main__":
    fig_inrush_spike()
    fig_active_circuit()
    fig_soa_power()
    fig_hotswap_block()
    fig_hotswap_timer()
    print("OK: 5 figур у", IMG)
