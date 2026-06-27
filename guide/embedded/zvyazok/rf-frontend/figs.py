# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def block(cx, cy, w, h, label, sub=None, fill=FILL, stroke=LINE):
    out = rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=2)
    if sub:
        out += text(cx, cy - 3, label, size=15, bold=True)
        out += text(cx, cy + 15, sub, size=11, color=MUTED)
    else:
        out += text(cx, cy + 5, label, size=15, bold=True)
    return out


# ── 1. Блок-схема RF-тракту ─────────────────────────────────────────────────
def fig_frontend():
    W, H = 740, 360
    f = []
    # антена
    ax, ay = 70, 180
    f.append(line(ax, ay, ax, ay - 42, sw=2))
    f.append(line(ax - 22, ay - 42, ax + 22, ay - 42, sw=2))
    f.append(line(ax - 22, ay - 42, ax - 10, ay - 60, sw=2))
    f.append(line(ax + 22, ay - 42, ax + 10, ay - 60, sw=2))
    f.append(text(ax, ay + 24, "антена", size=12, color=MUTED))
    f.append(text(ax, ay + 40, "50 Ω", size=11, color=MUTED))

    # балун
    bx = 190
    f.append(line(ax, ay, bx - 45, ay, sw=2))
    f.append(block(bx, ay, 90, 56, "балун", "1 ↔ 2 проводи", fill="#eef7f0", stroke=FIELD))

    # перемикач T/R
    sx = 340
    f.append(line(bx + 45, ay, sx - 38, ay, sw=2))
    f.append(circle(sx, ay, 30, fill="#fff7e6", stroke="#b8860b", sw=2))
    f.append(text(sx, ay + 5, "T/R", size=15, bold=True, color="#7a5b00"))
    f.append(text(sx, ay + 50, "перемикач", size=12, color=MUTED))

    # верхня гілка — PA (передача)
    px = 540
    f.append(line(sx + 21, ay - 21, px - 70, ay - 80, sw=2))
    f.append(block(px, ay - 80, 120, 56, "PA", "підсилювач передачі", fill="#fdecea", stroke=POS))
    f.append(arrow(px - 60, ay - 80, px + 60, ay - 80, color=POS))  # напрям до антени
    f.append(text(px, ay - 122, "ПЕРЕДАЧА (Tx)", size=12, bold=True, color=POS))

    # нижня гілка — LNA (прийом)
    f.append(line(sx + 21, ay + 21, px - 70, ay + 80, sw=2))
    f.append(block(px, ay + 80, 120, 56, "LNA", "малошумний прийому", fill="#eaf0fd", stroke=NEG))
    f.append(arrow(px + 60, ay + 80, px - 60, ay + 80, color=NEG))  # напрям від антени
    f.append(text(px, ay + 122, "ПРИЙОМ (Rx)", size=12, bold=True, color=NEG))

    # трансивер
    tx = 690
    f.append(line(px + 60, ay - 80, tx, ay - 80, sw=2))
    f.append(line(tx, ay - 80, tx, ay + 80, sw=2))
    f.append(line(px + 60, ay + 80, tx, ay + 80, sw=2))
    f.append(line(tx, ay, tx + 20, ay, sw=2))
    f.append(text(tx - 4, ay - 8, "до", size=11, color=MUTED, anchor="end"))
    f.append(text(tx - 4, ay + 8, "чипа", size=11, color=MUTED, anchor="end"))

    render(os.path.join(IMG, 'frontend-block.svg'), W, H, *f)


# ── 2. Чому перший каскад вирішує шум ───────────────────────────────────────
def fig_cascade():
    W, H = 720, 320
    f = []
    f.append(text(W / 2, 26, "Той самий шум, дві позиції каскаду", size=16, bold=True))

    def chain(y, lna_first, caption):
        x0 = 70
        f.append(line(x0 - 30, y, x0, y, sw=2))
        f.append(text(x0 - 34, y - 8, "сигнал", size=10, color=MUTED, anchor="end"))
        names = [("LNA", "×100", "#eaf0fd", NEG), ("мікшер", "шум +", "#fdecea", POS)]
        if not lna_first:
            names = [names[1], names[0]]
        cx = x0 + 60
        for i, (nm, sub, fl, st) in enumerate(names):
            f.append(block(cx, y, 96, 50, nm, sub, fill=fl, stroke=st))
            if i == 0:
                f.append(arrow(x0, y, cx - 48, y))
            cx2 = cx + 130
            f.append(arrow(cx + 48, y, cx2 - 48, y) if i == 0 else "")
            cx = cx2
        f.append(arrow(cx - 130 + 48, y, cx - 48, y))
        f.append(block(cx, y, 80, 50, "вихід", None, fill=FILL))
        f.append(text(x0 - 30, y + 44, caption, size=12, anchor="start"))
        return cx

    cend = chain(110, True, "LNA першим: шум мікшера ділиться на ×100 → майже не чути")
    chain(230, False, "мікшер першим: його шум іде на повну → SNR зруйновано")
    # підсумок-смужка
    f.append(text(W / 2, 300, "перший каскад задає шумове число всього тракту", size=12, bold=True, color=FIELD))
    render(os.path.join(IMG, 'cascade-noise.svg'), W, H, *f)


# ── 3. Балун: дві протифази → один провід ───────────────────────────────────
def fig_balun():
    W, H = 700, 320
    f = []
    f.append(text(W / 2, 26, "Балун: два протифазні сигнали ↔ один проти землі", size=15, bold=True))
    # ліворуч — диференційна пара (чип)
    import math
    lx, mid = 70, 170
    f.append(text(lx + 70, 64, "чип (диференційно)", size=12, color=MUTED))
    # дві синусоїди в протифазі
    def sine(x0, y0, amp, ph, color):
        pts = []
        for i in range(0, 121):
            xx = x0 + i * 1.0
            yy = y0 - amp * math.sin(i / 120.0 * 2 * math.pi * 2 + ph)
            pts.append("%.1f,%.1f" % (xx, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), color)
    f.append(line(lx, mid - 34, lx + 122, mid - 34, color=MUTED, sw=1, dash="3,3"))
    f.append(sine(lx, mid - 34, 22, 0, POS))
    f.append(text(lx - 6, mid - 34, "+", size=18, bold=True, color=POS, anchor="end"))
    f.append(line(lx, mid + 40, lx + 122, mid + 40, color=MUTED, sw=1, dash="3,3"))
    f.append(sine(lx, mid + 40, 22, math.pi, NEG))
    f.append(text(lx - 6, mid + 40, "−", size=18, bold=True, color=NEG, anchor="end"))

    # балун у центрі
    bx = 360
    f.append(line(lx + 122, mid - 34, bx - 50, mid - 34, color=POS, sw=2))
    f.append(line(lx + 122, mid + 40, bx - 50, mid + 40, color=NEG, sw=2))
    body, bw, bh = textbox(bx, mid + 3, "балун", size=16, pad=18, fill="#eef7f0", stroke=FIELD, bold=True, min_w=100)
    f.append(body)

    # праворуч — несиметрично (антена + земля)
    rx = 560
    f.append(line(bx + 50, mid - 16, rx, mid - 16, sw=2))
    f.append(sine(rx - 40, mid - 16, 28, 0, INK))
    # сигнальний провід
    f.append(text(rx + 86, 64, "антена (проти землі)", size=12, color=MUTED))
    # земля
    gy = mid + 56
    f.append(line(bx + 50, gy, rx + 100, gy, color=INK, sw=2))
    for i in range(5):
        gx = bx + 70 + i * 18
        f.append(line(gx, gy, gx - 8, gy + 12, color=INK, sw=1.5))
    f.append(text(rx + 70, gy + 26, "земля = опора", size=11, color=MUTED))
    f.append(text(rx + 60, mid - 50, "удвічі більший розмах", size=11, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, 'balun-diff-se.svg'), W, H, *f)


# ── 4. FEM: що сидить в одному корпусі (вставка comp-fem) ────────────────────
def fig_fem_block():
    W, H = 740, 380
    f = []
    f.append(text(W / 2, 26, "Модуль фронт-енду: три деталі в одному корпусі", size=16, bold=True))

    # корпус модуля — пунктирна рамка
    mx, my, mw, mh = 200, 70, 340, 250
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="#f7faf8" '
             'stroke="%s" stroke-width="2" stroke-dasharray="7,5"/>' % (mx, my, mw, mh, FIELD))
    f.append(text(mx + mw / 2, my - 8, "корпус FEM (≈ 3×3 мм)", size=11, color=FIELD))

    # антенний вивід (праворуч)
    ax = mx + mw + 70
    ay = my + mh / 2
    f.append(line(ax, ay, ax, ay - 36, sw=2))
    f.append(line(ax - 18, ay - 36, ax + 18, ay - 36, sw=2))
    f.append(line(ax - 18, ay - 36, ax - 8, ay - 52, sw=2))
    f.append(line(ax + 18, ay - 36, ax + 8, ay - 52, sw=2))
    f.append(text(ax, ay + 22, "ANT", size=12, bold=True, color=MUTED))
    f.append(text(ax, ay + 38, "50 Ω", size=10, color=MUTED))

    # перемикач T/R усередині, біля антенного краю
    sx = mx + mw - 56
    f.append(line(mx + mw, ay, ax, ay, sw=2))   # вивід ANT назовні
    f.append(circle(sx, ay, 28, fill="#fff7e6", stroke="#b8860b", sw=2))
    f.append(text(sx, ay + 4, "T/R", size=13, bold=True, color="#7a5b00"))

    # PA (верхня гілка)
    px = mx + 110
    f.append(block(px, my + 70, 116, 50, "PA", "+20…+22 dBm", fill="#fdecea", stroke=POS))
    f.append(arrow(px + 58, my + 70, sx - 20, ay - 18, color=POS))
    f.append(text(px, my + 36, "ПЕРЕДАЧА", size=10, bold=True, color=POS))

    # LNA (нижня гілка) з відведенням bypass
    lx = px
    f.append(block(lx, my + 180, 116, 50, "LNA", "NF ≈ 2 dB", fill="#eaf0fd", stroke=NEG))
    f.append(arrow(sx - 20, ay + 18, lx + 58, my + 180, color=NEG))
    f.append(text(lx, my + 214, "ПРИЙОМ", size=10, bold=True, color=NEG))
    # пунктир bypass — обхід LNA
    f.append(line(lx - 58, my + 180, lx - 58, my + 230, color=MUTED, sw=1.4, dash="4,3"))
    f.append(line(lx - 58, my + 230, lx + 58, my + 230, color=MUTED, sw=1.4, dash="4,3"))
    f.append(line(lx + 58, my + 230, lx + 58, my + 205, color=MUTED, sw=1.4, dash="4,3"))
    f.append(text(lx, my + 246, "bypass (обхід)", size=10, color=MUTED, italic=True))

    # сигнальні виводи ліворуч: RF-вхід/вихід + керування
    rf_y = ay
    f.append(line(mx - 70, my + 70, px - 58, my + 70, sw=2))
    f.append(line(mx - 70, my + 180, lx - 58, my + 180, sw=2))
    f.append(text(mx - 74, my + 66, "TX in", size=11, color=MUTED, anchor="end"))
    f.append(text(mx - 74, my + 184, "RX out", size=11, color=MUTED, anchor="end"))
    # керування
    for i, (nm, yy) in enumerate([("TX_EN", my + 110), ("RX_EN", my + 140), ("MODE", my + 215)]):
        f.append(line(mx - 70, yy, mx, yy, color="#7a5b00", sw=1.6))
        f.append(text(mx - 74, yy + 4, nm, size=10, color="#7a5b00", anchor="end"))
    f.append(text(mx - 40, my + mh + 4, "керування з MCU", size=10, color="#7a5b00", anchor="middle"))

    render(os.path.join(IMG, 'fem-block.svg'), W, H, *f)


# ── 5. FEM: дві ніжки → чотири стани, у такт із протоколом ───────────────────
def fig_fem_states():
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 26, "Дві ніжки керування — чотири стани FEM", size=16, bold=True))

    # таблиця станів
    tx, ty = 60, 60
    cw = [120, 90, 90, 170]
    rows = [
        ("режим", "TX_EN", "RX_EN", "що в тракті"),
        ("сон", "0", "0", "усе вимкнено, ~0 мкА"),
        ("прийом", "0", "1", "антена → LNA"),
        ("передача", "1", "0", "PA → антена"),
        ("(заборонено)", "1", "1", "обидві гілки — не можна"),
    ]
    colors = [INK, MUTED, NEG, POS, "#999999"]
    rh = 34
    x = tx
    # заголовок-рамка
    for r, row in enumerate(rows):
        x = tx
        for c, cell in enumerate(row):
            fill = "#eef2f7" if r == 0 else BG
            f.append(rect(x, ty + r * rh, cw[c], rh, fill=fill, stroke="#ccd2da", sw=1, rx=0))
            col = INK if r == 0 else (colors[r] if c == 0 else INK)
            bold = (r == 0) or (c == 0)
            f.append(text(x + cw[c] / 2, ty + r * rh + rh / 2 + 4, cell, size=12,
                          color=col, bold=bold))
            x += cw[c]

    # часова діаграма turnaround унизу
    dy = ty + len(rows) * rh + 46
    f.append(text(W / 2, dy - 16, "перемикання в такт із протоколом (turnaround ≈ кілька мкс)",
                  size=12, bold=True, color=FIELD))
    bx0, bx1 = 90, 640
    # лінія RX_EN
    yr = dy + 16
    f.append(text(bx0 - 8, yr + 4, "RX_EN", size=11, color=NEG, anchor="end"))
    f.append(line(bx0, yr, bx0 + 180, yr, color=NEG, sw=2.2))            # high
    f.append(line(bx0 + 180, yr, bx0 + 180, yr + 22, color=NEG, sw=2.2))
    f.append(line(bx0 + 180, yr + 22, bx0 + 230, yr + 22, color=NEG, sw=2.2, dash="3,2"))  # пауза
    f.append(line(bx0 + 230, yr + 22, bx0 + 550, yr + 22, color=NEG, sw=2.2))
    # лінія TX_EN
    yt = dy + 60
    f.append(text(bx0 - 8, yt + 4, "TX_EN", size=11, color=POS, anchor="end"))
    f.append(line(bx0, yt + 22, bx0 + 205, yt + 22, color=POS, sw=2.2))
    f.append(line(bx0 + 205, yt + 22, bx0 + 205, yt, color=POS, sw=2.2))
    f.append(line(bx0 + 205, yt, bx0 + 420, yt, color=POS, sw=2.2))      # high (TX)
    f.append(line(bx0 + 420, yt, bx0 + 420, yt + 22, color=POS, sw=2.2))
    f.append(line(bx0 + 420, yt + 22, bx0 + 550, yt + 22, color=POS, sw=2.2))
    # зона turnaround
    f.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#fff7e6" stroke="#b8860b" '
             'stroke-width="1" stroke-dasharray="3,2" rx="3"/>' % (bx0 + 180, yr - 6, 50, yt - yr + 34))
    f.append(text(bx0 + 205, yr - 12, "обидві 0", size=9, color="#7a5b00"))
    # підписи фаз
    f.append(text(bx0 + 90, yt + 50, "прийом", size=11, color=NEG, bold=True))
    f.append(text(bx0 + 312, yt + 50, "передача", size=11, color=POS, bold=True))
    f.append(text(bx0 + 490, yt + 50, "прийом", size=11, color=NEG, bold=True))

    render(os.path.join(IMG, 'fem-states.svg'), W, H, *f)


# ── 6. Кут провідності: A / AB / B / C (вставка comp-pa-classes) ─────────────
def fig_conduction():
    import math
    W, H = 720, 420
    f = []
    f.append(text(W / 2, 26, "Кут провідності: яку частку періоду транзистор «живий»", size=15, bold=True))

    panels = [
        ("Клас A", 360, "весь період", "η ≤ 50 %", FILL, INK),
        ("Клас AB", 220, "трохи > пів", "≈ 50–70 %", "#eef7f0", FIELD),
        ("Клас B", 180, "рівно пів", "≤ 78.5 %", "#eaf0fd", NEG),
        ("Клас C", 110, "менше пів", "до ~80 %; рве форму", "#fdecea", POS),
    ]
    pw = 165
    x0 = 30
    basey = 150
    amp = 46
    for idx, (nm, ang, frac, eff, fill, st) in enumerate(panels):
        cx = x0 + idx * (pw + 12) + pw / 2
        left = cx - pw / 2 + 14
        right = cx + pw / 2 - 14
        span = right - left
        f.append(rect(cx - pw / 2, 50, pw, 350, fill=fill, stroke=st, sw=1.5))
        f.append(text(cx, 78, nm, size=15, bold=True, color=st))
        f.append(line(left, basey, right, basey, color=MUTED, sw=1))
        full = []
        cond = []
        N = 160
        for i in range(N + 1):
            ph = i / float(N) * 2 * math.pi
            xx = left + i / float(N) * span
            s = math.sin(ph)
            full.append("%.1f,%.1f" % (xx, basey - amp * s))
            d = abs(((ph - math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi)
            if d <= math.radians(ang / 2.0) + 1e-6:
                yy = basey - amp * s if (s > 0 or ang >= 360) else basey
                cond.append("%.1f,%.1f" % (xx, yy))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>'
                 % (" ".join(full), MUTED))
        if cond:
            xfirst = cond[0].split(",")[0]
            xlast = cond[-1].split(",")[0]
            pts = "%s,%.1f " % (xfirst, basey) + " ".join(cond) + " %s,%.1f" % (xlast, basey)
            f.append('<polygon points="%s" fill="%s" fill-opacity="0.28" stroke="none"/>' % (pts, st))
            f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(cond), st))
        f.append(text(cx, basey + 56, "%d°" % ang, size=20, bold=True, color=st))
        f.append(text(cx, basey + 76, frac, size=11, color=MUTED))
        f.append(fitbox(cx - pw / 2 + 12, basey + 92, pw - 24, 50, eff, size=12, bold=True,
                        fill=BG, stroke=st, color=st))
    f.append(text(W / 2, 410, "вужчий кут провідності → вища ефективність, але гірша лінійність",
                  size=12, bold=True, color=MUTED))
    render(os.path.join(IMG, 'pa-conduction.svg'), W, H, *f)


# ── 7. ККД проти відступу: A, B, Doherty (вставка comp-pa-classes) ───────────
def fig_backoff():
    import math
    W, H = 720, 420
    f = []
    f.append(text(W / 2, 26, "Drain efficiency проти відступу від піку", size=16, bold=True))

    gx0, gy0 = 95, 345
    gw, gh = 545, 265
    f.append(line(gx0, gy0, gx0 + gw, gy0, sw=2))
    f.append(line(gx0, gy0, gx0, gy0 - gh, sw=2))
    f.append(text(gx0 + gw / 2, gy0 + 52, "відступ від піку, dB  (праворуч — менша потужність) →",
                  size=12, color=MUTED))
    f.append(text(gx0 - 64, gy0 - gh / 2, "ККД", size=12, color=MUTED, anchor="middle"))
    f.append(text(gx0 - 64, gy0 - gh / 2 + 16, "%", size=11, color=MUTED, anchor="middle"))

    xmax = 12.0
    ymax = 80.0
    def X(b): return gx0 + b / xmax * gw
    def Y(e): return gy0 - e / ymax * gh
    for e in (20, 40, 60, 78.5):
        f.append(line(gx0, Y(e), gx0 + gw, Y(e), color="#e3e6ea", sw=1))
        f.append(text(gx0 - 8, Y(e) + 4, "%g" % e, size=10, color=MUTED, anchor="end"))
    for b in (0, 3, 6, 9, 12):
        f.append(line(X(b), gy0, X(b), gy0 + 5, color=MUTED, sw=1))
        f.append(text(X(b), gy0 + 20, "%d" % b, size=11, color=MUTED))

    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10" stroke="none"/>'
             % (X(6), gy0 - gh, X(10) - X(6), gh, FIELD))
    f.append(text((X(6) + X(10)) / 2, gy0 - gh + 14, "робоча зона", size=11, color=FIELD, bold=True))
    f.append(text((X(6) + X(10)) / 2, gy0 - gh + 30, "OFDM / Wi-Fi", size=10, color=FIELD))

    def curveA():
        return [(b, 50.0 * 10 ** (-b / 10.0)) for b in (i / 120.0 * xmax for i in range(121))]
    def curveB():
        return [(b, 78.5 * 10 ** (-b / 20.0)) for b in (i / 120.0 * xmax for i in range(121))]
    def curveD():
        pts = []
        for i in range(121):
            b = i / 120.0 * xmax
            base = 78.5 * 10 ** (-b / 20.0)
            hump = 26.0 * math.exp(-((b - 6.0) ** 2) / (2 * 1.7 ** 2))
            pts.append((b, min(78.5, base + hump)))
        return pts

    def draw(pts, color, sw=2.6):
        s = " ".join("%.1f,%.1f" % (X(b), Y(e)) for b, e in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (s, color, sw))

    draw(curveA(), POS)
    draw(curveB(), NEG)
    draw(curveD(), FIELD, sw=3.0)

    def dot(b, e, color):
        f.append(circle(X(b), Y(e), 3.5, fill=color, stroke=BG, sw=1))
    dot(0, 50, POS); dot(6, 12.5, POS)
    dot(0, 78.5, NEG); dot(6, 39.3, NEG)
    dot(6, 65, FIELD)
    f.append(text(X(6) + 6, Y(12.5) + 4, "12.5 %", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(X(6) + 6, Y(39.3) - 6, "39.3 %", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(X(6) + 6, Y(65) - 6, "≈ 65 %", size=11, bold=True, color=FIELD, anchor="start"))

    lx, ly = gx0 + 330, gy0 - gh + 18
    f.append(line(lx, ly, lx + 26, ly, color=POS, sw=2.6))
    f.append(text(lx + 32, ly + 4, "клас A  (η ∝ потужності)", size=12, color=INK, anchor="start"))
    f.append(line(lx, ly + 22, lx + 26, ly + 22, color=NEG, sw=2.6))
    f.append(text(lx + 32, ly + 26, "клас B  (η ∝ напрузі)", size=12, color=INK, anchor="start"))
    f.append(line(lx, ly + 44, lx + 26, ly + 44, color=FIELD, sw=3.0))
    f.append(text(lx + 32, ly + 48, "Doherty  (другий горб)", size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, 'pa-backoff.svg'), W, H, *f)


# ── 8. Шлях трьох порцій шуму крізь два каскади (вставка math-friis) ─────────
def fig_friis_paths():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 26, "Три порції шуму — три різні шляхи підсилення", size=16, bold=True))

    y = 150
    # два каскади
    g1x, g2x = 250, 470
    f.append(block(g1x, y, 120, 60, "каскад 1", "× G₁", fill="#eaf0fd", stroke=NEG))
    f.append(block(g2x, y, 120, 60, "каскад 2", "× G₂", fill="#fdecea", stroke=POS))
    # лінія сигналу крізь усе
    f.append(line(70, y, g1x - 60, y, sw=2))
    f.append(arrow(g1x + 60, y, g2x - 60, y))
    f.append(arrow(g2x + 60, y, 660, y))
    f.append(text(70, y - 12, "вхід", size=11, color=MUTED, anchor="start"))
    f.append(text(658, y - 12, "вихід", size=11, color=MUTED, anchor="end"))

    # джерела шуму, що втручаються в різних точках
    # N0 + N1 — на вході першого
    f.append(plus(150, y - 56, 9))
    f.append(text(150, y - 74, "N₀ + N₁", size=12, bold=True, anchor="middle"))
    f.append(line(150, y - 47, 150, y - 9, color=MUTED, sw=1.4, dash="3,3"))
    f.append(text(150, y + 30, "входять на самому", size=10, color=MUTED))
    f.append(text(150, y + 44, "початку → × G₁·G₂", size=10, color=NEG, anchor="middle"))

    # N2 — на вході другого
    f.append(plus(370, y - 56, 9))
    f.append(text(370, y - 74, "N₂", size=12, bold=True, anchor="middle"))
    f.append(line(370, y - 47, 370, y - 9, color=MUTED, sw=1.4, dash="3,3"))
    f.append(text(370, y + 30, "втручається пізніше", size=10, color=MUTED))
    f.append(text(370, y + 44, "→ лише × G₂", size=10, color=POS, anchor="middle"))

    # підсумок-рамка: віднесення на спільний вхід
    body, bw, bh = textbox(W / 2, 300, "на спільний вхід:  N₁ + N₂ / G₁     →     F = F₁ + (F₂−1) / G₁",
                           size=14, pad=14, fill="#eef7f0", stroke=FIELD, bold=True)
    f.append(body)

    render(os.path.join(IMG, 'friis-noise-paths.svg'), W, H, *f)


if __name__ == '__main__':
    fig_frontend()
    fig_cascade()
    fig_balun()
    fig_fem_block()
    fig_fem_states()
    fig_conduction()
    fig_backoff()
    fig_friis_paths()
    print("ok")
