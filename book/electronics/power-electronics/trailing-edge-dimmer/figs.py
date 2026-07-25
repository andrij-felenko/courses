# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── спільні помічники ────────────────────────────────────────────────────────
def halfwave(x0, x1, yb, A, t0, t1, n=64):
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        x = x0 + (x1 - x0) * t
        y = yb - A * math.sin(math.pi * t)
        pts.append((x, y))
    return pts


def polyline(pts, color, sw=2.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (p, color, sw, d)


def filled(pts, yb, fill, opacity=0.16):
    x0 = pts[0][0]
    x1 = pts[-1][0]
    p = [(x0, yb)] + pts + [(x1, yb)]
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in p)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (s, fill, opacity)


def diode(p1, p2, color=INK, s=9):
    (x1, y1), (x2, y2) = p1, p2
    frag = line(x1, y1, x2, y2, color=color, sw=2)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    ax, ay = mx + ux * s, my + uy * s
    b1x, b1y = mx - ux * s + px * s, my - uy * s + py * s
    b2x, b2y = mx - ux * s - px * s, my - uy * s - py * s
    tri = '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (ax, ay, b1x, b1y, b2x, b2y, color)
    bar = line(ax + px * s, ay + py * s, ax - px * s, ay - py * s, color=color, sw=2.6)
    return frag + tri + bar


# ── Фігура 1: передній фронт проти заднього ──────────────────────────────────
def fig_edges():
    W, H = 980, 470
    yb, A = 300.0, 150.0
    lx0, lx1 = 70.0, 430.0
    rx0, rx1 = 550.0, 910.0
    f = []
    f.append(text((lx0 + lx1) / 2, 58, "Передній фронт (leading-edge)", size=16, bold=True))
    f.append(text((rx0 + rx1) / 2, 58, "Задній фронт (trailing-edge)", size=16, bold=True))
    # роздільна лінія між панелями
    f.append(line((lx1 + rx0) / 2, 80, (lx1 + rx0) / 2, 420, color="#d0d4d8", sw=1.2, dash="4,6"))
    # осі-нулі
    f.append(line(lx0 - 12, yb, lx1 + 12, yb, color=INK, sw=1.5))
    f.append(line(rx0 - 12, yb, rx1 + 12, yb, color=INK, sw=1.5))
    f.append(text(lx0 - 20, yb + 5, "0", size=12, color=MUTED, anchor="end"))
    f.append(text(rx1 + 20, yb + 5, "180°", size=12, color=MUTED, anchor="start"))
    # повна синусоїда пунктиром
    f.append(polyline(halfwave(lx0, lx1, yb, A, 0, 1), MUTED, sw=1.6, dash="5,6"))
    f.append(polyline(halfwave(rx0, rx1, yb, A, 0, 1), MUTED, sw=1.6, dash="5,6"))

    # LEADING: провідність від α=60° (t=1/3) до 180°
    la = 1.0 / 3
    lead = halfwave(lx0, lx1, yb, A, la, 1)
    f.append(filled(lead, yb, FIELD, 0.16))
    f.append(polyline(lead, POS, sw=3.2))
    jx = lx0 + (lx1 - lx0) * la
    jy = yb - A * math.sin(math.pi * la)
    f.append(line(jx, yb, jx, jy, color=POS, sw=3.2))  # різкий стрибок вмикання
    # підпис стрибка (нижче нуля, стрілка вгору до середини фронту)
    tb, w, h = textbox(178, 392, "стрибок напруги\nпри вмиканні", size=13, color=POS)
    f.append(tb)
    f.append(arrow(178, 392 - h / 2, jx - 4, (yb + jy) / 2 + 6, color=POS))
    # м'яке згасання праворуч
    tb, w, h = textbox(392, 356, "гасне сам\nу нулі", size=13, color=MUTED)
    f.append(tb)
    f.append(arrow(392 + w / 2 - 6, 356 - h / 2, lx1 - 6, yb - 8, color=MUTED))

    # TRAILING: провідність від 0 до β=120° (t=2/3)
    tbend = 2.0 / 3
    trail = halfwave(rx0, rx1, yb, A, 0, tbend)
    f.append(filled(trail, yb, FIELD, 0.16))
    f.append(polyline(trail, POS, sw=3.2))
    dx = rx0 + (rx1 - rx0) * tbend
    dy = yb - A * math.sin(math.pi * tbend)
    f.append(line(dx, yb, dx, dy, color=POS, sw=3.2))  # різкий обрив
    # м'яке вмикання ліворуч
    tb, w, h = textbox(600, 356, "м'яке вмикання\nв нулі", size=13, color=FIELD)
    f.append(tb)
    f.append(arrow(600 - w / 2 + 6, 356 - h / 2, rx0 + 6, yb - 8, color=FIELD))
    # підпис обриву (нижче, стрілка вгору)
    tb, w, h = textbox(792, 392, "різкий обрив\nструму", size=13, color=POS)
    f.append(tb)
    f.append(arrow(792, 392 - h / 2, dx + 4, (yb + dy) / 2 + 6, color=POS))

    render(os.path.join(OUT, 'leading-vs-trailing.svg'), W, H, *f)


# ── Фігура 2: два способи зробити ключ змінного струму ───────────────────────
def fig_topologies():
    W, H = 1000, 560
    f = []
    f.append(text(255, 56, "Пара MOSFET спина-до-спини", size=16, bold=True))
    f.append(text(748, 56, "Один MOSFET у діодному мості", size=16, bold=True))
    f.append(line(500, 80, 500, 500, color="#d0d4d8", sw=1.2, dash="4,6"))

    # --- ЛІВА панель: back-to-back ---
    # прямокутна петля: джерело ~ у лівій стійці, навантаження зверху, два ключі знизу
    f.append(circle(95, 250, 24, fill="#eef2f7", stroke=INK, sw=2))
    f.append(text(95, 257, "~", size=26, bold=True))
    f.append(text(63, 254, "мережа", size=12, color=MUTED, anchor="end"))
    # ліва стійка (з розривом під джерело)
    f.append(line(95, 120, 95, 226, color=INK, sw=2))
    f.append(line(95, 274, 95, 360, color=INK, sw=2))
    # верхня шина + навантаження
    f.append(line(95, 120, 205, 120, color=INK, sw=2))
    f.append(fitbox(205, 98, 130, 44, "навантаження", size=13))
    f.append(line(335, 120, 445, 120, color=INK, sw=2))
    # права стійка вниз
    f.append(line(445, 120, 445, 360, color=INK, sw=2))
    # нижня шина з двома ключами (Q1 центр 185, Q2 центр 315, вузол між ними 250)
    f.append(line(95, 360, 158, 360, color=INK, sw=2))
    f.append(fitbox(158, 338, 54, 44, "Q1", size=15, bold=True))
    f.append(line(212, 360, 288, 360, color=INK, sw=2))
    f.append(circle(250, 360, 3.5, fill=INK, stroke=INK))
    f.append(text(250, 328, "спільний витік", size=11, color=MUTED))
    f.append(fitbox(288, 338, 54, 44, "Q2", size=15, bold=True))
    f.append(line(342, 360, 445, 360, color=INK, sw=2))
    # плаваючий драйвер затворів (унизу, дротики до затворів)
    f.append(fitbox(150, 448, 210, 46, "драйвер затворів\n(плаває на мережі)", size=12))
    f.append(line(185, 382, 185, 448, color=MUTED, sw=1.4, dash="4,4"))
    f.append(line(315, 382, 315, 448, color=MUTED, sw=1.4, dash="4,4"))
    # висновок
    tb, w, h = textbox(255, 522, "2 канали · малі втрати · керування плаває", size=12.5, color=FIELD, bold=True)
    f.append(tb)

    # --- ПРАВА панель: MOSFET у мості ---
    cx = 748.0
    top = (cx, 132.0)
    bot = (cx, 352.0)
    lft = (642.0, 242.0)
    rgt = (854.0, 242.0)
    # чотири діоди (усі «дивляться» на верх = DC+)
    f.append(diode(lft, top, color=INK))
    f.append(diode(rgt, top, color=INK))
    f.append(diode(bot, lft, color=INK))
    f.append(diode(bot, rgt, color=INK))
    # позначки DC (ліворуч від вертикальної діагоналі)
    f.append(text(cx - 16, 128, "+", size=16, color=POS, bold=True))
    f.append(text(cx - 16, 372, "−", size=16, color=NEG, bold=True))
    # MOSFET по діагоналі постійного струму (у центрі ромба)
    f.append(line(top[0], top[1], cx, 218, color=INK, sw=2))
    f.append(line(cx, 266, bot[0], bot[1], color=INK, sw=2))
    f.append(fitbox(cx - 46, 218, 92, 48, "Q", size=16, bold=True))
    # входи змінного струму (ліворуч і праворуч ромба)
    f.append(line(lft[0], lft[1], 594, 242, color=INK, sw=2))
    f.append(line(rgt[0], rgt[1], 902, 242, color=INK, sw=2))
    f.append(text(580, 247, "~", size=20, bold=True))
    f.append(text(916, 247, "~", size=20, bold=True))
    # висновок
    tb, w, h = textbox(748, 452, "1 ключ · просте керування (спільна земля)", size=12.5, color=INK, bold=True)
    f.append(tb)
    tb, w, h = textbox(748, 486, "але струм завжди крізь 2 діоди → тепло", size=12.5, color=POS, bold=True)
    f.append(tb)

    render(os.path.join(OUT, 'ac-switch-topologies.svg'), W, H, *f)


# ── Фігура 3: вимикання на індуктивному навантаженні — викид і снабер ────────
def fig_spike():
    W, H = 960, 470
    yb = 330.0
    x0, xoff, xend = 110.0, 470.0, 840.0
    f = []
    f.append(text(W / 2, 44, "Обрив струму в індуктивності: викид напруги і снабер", size=16, bold=True))
    # вісь часу
    f.append(line(90, yb, 880, yb, color=INK, sw=1.5))
    f.append(text(884, yb + 4, "t", size=14, italic=True))
    # момент вимикання
    f.append(line(xoff, 80, xoff, yb, color=MUTED, sw=1.3, dash="5,5"))
    f.append(text(xoff, yb + 22, "вимкнення", size=12, color=MUTED))

    # струм навантаження: наростає переднім фронтом, тоді обрив
    cur = []
    for i in range(49):
        t = i / 48.0
        x = x0 + (xoff - x0) * t
        y = yb - 120 * math.sin(math.pi * 0.5 * t)  # чверть-синус, наростання
        cur.append((x, y))
    f.append(polyline(cur, NEG, sw=3))
    f.append(line(xoff, cur[-1][1], xoff, yb, color=NEG, sw=3, dash="3,4"))  # різкий спад до нуля
    tb, w, h = textbox(250, 150, "струм навантаження", size=13, color=NEG)
    f.append(tb)
    f.append(arrow(250 + 10, 150 + h / 2, 360, yb - 88, color=NEG))

    # викид напруги без снабера — висока голка вгору
    spx = xoff
    spike = [(spx, yb), (spx + 6, 95), (spx + 12, 92), (spx + 20, 150),
             (spx + 34, 240), (spx + 52, 300), (spx + 78, yb)]
    f.append(polyline(spike, POS, sw=3))
    # «зубчастий» верх голки
    f.append(text(spx + 14, 84, "≈ кіловольти", size=12, color=POS, bold=True))
    tb, w, h = textbox(690, 150, "L·di/dt → викид напруги\n(без снабера)", size=13, color=POS)
    f.append(tb)
    f.append(arrow(690 - w / 2 + 8, 150, spx + 40, 175, color=POS))

    # зі снабером / повільним вимиканням — низький округлий горб
    snub = []
    for i in range(49):
        t = i / 48.0
        x = xoff + (xend - xoff) * t
        y = yb - 95 * math.exp(-((t - 0.18) ** 2) / 0.05) if t > 0 else yb
        snub.append((x, y))
    f.append(polyline(snub, FIELD, sw=3, dash="7,5"))
    tb, w, h = textbox(700, 300, "снабер / повільне вимикання\nгасить викид", size=13, color=FIELD)
    f.append(tb)
    f.append(arrow(700 - w / 2 + 8, 300 - h / 2, 560, yb - 78, color=FIELD))

    render(os.path.join(OUT, 'inductive-turnoff-spike.svg'), W, H, *f)


# ── Фігура (hist): часова лінія — прилади знизу, димери зверху ────────────────
def fig_timeline():
    W, H = 1200, 590
    axis_y = 320.0
    x0, x1 = 100.0, 1120.0
    y_lo, y_hi = 1955.0, 2015.0

    def yx(yr):
        return x0 + (x1 - x0) * (yr - y_lo) / (y_hi - y_lo)

    f = []
    # смуги двох епох (межа ≈ коли зʼявився силовий транзистор)
    bx = yx(1981)
    f.append(rect(88, 124, bx - 88, 416, fill="#eef6f1", stroke="none", sw=0, rx=10))
    f.append(rect(bx, 124, 1132 - bx, 416, fill="#eef2fb", stroke="none", sw=0, rx=10))
    # заголовки смуг (над смугами, на білому)
    f.append(text((88 + bx) / 2, 108, "ПЕРЕДНІЙ ФРОНТ — симісторний димер", size=13.5, color=FIELD, bold=True))
    f.append(text((bx + 1132) / 2, 108, "ЗАДНІЙ ФРОНТ — транзисторний ключ", size=13.5, color=NEG, bold=True))
    # вісь часу з десятковими мітками
    f.append(line(x0 - 8, axis_y, x1 + 8, axis_y, color=INK, sw=2))
    for yr in (1960, 1970, 1980, 1990, 2000, 2010):
        xx = yx(yr)
        f.append(line(xx, axis_y - 6, xx, axis_y + 6, color=INK, sw=1.4))
        f.append(text(xx, axis_y + 26, str(yr), size=12, color=MUTED))

    def event(cx, cy, yr, label, dot):
        ex = yx(yr)
        f.append(circle(ex, axis_y, 5, fill=dot, stroke=dot, sw=1))
        tb, w, h = textbox(cx, cy, label, size=12.5, color=INK, stroke=MUTED)
        if cy < axis_y:
            f.append(line(ex, axis_y - 5, cx, cy + h / 2, color=dot, sw=1.3))
        else:
            f.append(line(ex, axis_y + 5, cx, cy - h / 2, color=dot, sw=1.3))
        f.append(tb)

    # зверху — димери й техніка фазового керування
    event(168, 178, 1959, "Спіра: димер у коробці\nпатент 1959 · Lutron 1961", INK)
    event(500, 178, 1978.5, "Зворотний фронт у патентах\nта IEEE · 1978–79", FIELD)
    event(670, 254, 1988.5, "ELV-димер на MOSFET\nдля електронних трансформаторів\n1987–90", FIELD)
    event(1035, 178, 2010, "Епоха LED\nзадній фронт — масовий", FIELD)
    # знизу — напівпровідникові прилади, що вмикають можливості
    event(134, 410, 1957, "Тиристор (SCR)\nGE · 1957", NEG)
    event(236, 488, 1963, "Симістор (triac)\nGE · 1963", NEG)
    event(457, 410, 1976, "Силовий MOSFET\n1975–78", NEG)
    event(593, 488, 1984, "IGBT\n1980-ті", NEG)

    render(os.path.join(OUT, 'hist-timeline.svg'), W, H, *f, title="Дві половини хвилі й прилади, що їх уможливили")


# ── Фігура (hist): ємнісний вхід — голка пускового струму проти мʼякого старту ─
def fig_cap_inrush():
    W, H = 1040, 540
    f = []
    lx0, lx1 = 80.0, 470.0
    rx0, rx1 = 570.0, 960.0
    yv, yi, Av = 176.0, 430.0, 92.0
    f.append(text((lx0 + lx1) / 2, 52, "Передній фронт у ємнісний вхід", size=16, bold=True))
    f.append(text((rx0 + rx1) / 2, 52, "Задній фронт: старт у нулі", size=16, bold=True))
    f.append(line((lx1 + rx0) / 2, 74, (lx1 + rx0) / 2, 512, color="#d0d4d8", sw=1.2, dash="4,6"))
    # нульові осі напруги й струму + літери U / I
    for (a, b) in ((lx0, lx1), (rx0, rx1)):
        f.append(line(a - 10, yv, b + 10, yv, color=INK, sw=1.3))
        f.append(line(a - 10, yi, b + 10, yi, color=INK, sw=1.3))
    for a in (lx0, rx0):
        f.append(text(a - 18, yv + 4, "U", size=13, color=MUTED, italic=True, anchor="end"))
        f.append(text(a - 18, yi + 4, "I", size=13, color=MUTED, italic=True, anchor="end"))

    # ЛІВА панель: передній фронт
    f.append(polyline(halfwave(lx0, lx1, yv, Av, 0, 1), MUTED, sw=1.6, dash="5,6"))
    jt = 0.42
    lead = halfwave(lx0, lx1, yv, Av, jt, 1)
    f.append(filled(lead, yv, FIELD, 0.15))
    f.append(polyline(lead, INK, sw=3))
    jx = lx0 + (lx1 - lx0) * jt
    jy = yv - Av * math.sin(math.pi * jt)
    f.append(line(jx, yv, jx, jy, color=INK, sw=3))              # стрибок напруги
    # струм: голка пускового струму в мить стрибка
    spk = [(lx0, yi), (jx, yi), (jx + 4, yi - 150), (jx + 11, yi - 150),
           (jx + 24, yi - 62), (jx + 44, yi - 20), (jx + 80, yi - 5), (lx1, yi)]
    f.append(polyline(spk, POS, sw=3))
    tb, w, h = textbox(150, 250, "стрибок напруги\nв уже високій точці", size=12.5, color=INK)
    f.append(tb)
    f.append(arrow(150 + w / 2 - 6, 250 - h / 2, jx - 3, (yv + jy) / 2, color=INK))
    tb, w, h = textbox(158, 360, "голка пускового\nструму", size=12.5, color=POS, bold=True)
    f.append(tb)
    f.append(arrow(158 + w / 2 - 6, 360 - h / 2 + 4, jx - 3, yi - 120, color=POS))
    tb, w, h = textbox(275, 500, "гудіння · EMI · нагрів", size=13, color=POS, bold=True)
    f.append(tb)

    # ПРАВА панель: задній фронт
    f.append(polyline(halfwave(rx0, rx1, yv, Av, 0, 1), MUTED, sw=1.6, dash="5,6"))
    dt = 0.62
    trail = halfwave(rx0, rx1, yv, Av, 0, dt)
    f.append(filled(trail, yv, FIELD, 0.15))
    f.append(polyline(trail, INK, sw=3))
    dx = rx0 + (rx1 - rx0) * dt
    dy = yv - Av * math.sin(math.pi * dt)
    f.append(line(dx, yv, dx, yv, color=INK, sw=3))
    f.append(line(dx, dy, dx, yv, color=INK, sw=3))              # обрив у кінці
    # струм: плавний горб без голки
    hump = [(rx0, yi)]
    for i in range(1, 41):
        t = dt * i / 40.0
        x = rx0 + (rx1 - rx0) * t
        y = yi - 58 * math.exp(-((t - 0.16) ** 2) / 0.03)
        hump.append((x, y))
    hump.append((dx, yi))
    hump.append((rx1, yi))
    f.append(polyline(hump, FIELD, sw=3))
    tb, w, h = textbox(720, 250, "вмикання в нулі —\nстрибати нема з чого", size=12.5, color=INK)
    f.append(tb)
    f.append(arrow(720 - w / 2 + 6, 250 - h / 2, rx0 + 8, yv - 6, color=INK))
    tb, w, h = textbox(775, 360, "плавний заряд,\nбез голки", size=12.5, color=FIELD, bold=True)
    f.append(tb)
    f.append(arrow(775 - w / 2 + 6, 360 - h / 2 + 4, 690, yi - 44, color=FIELD))
    tb, w, h = textbox(765, 500, "тихо · без ударів", size=13, color=FIELD, bold=True)
    f.append(tb)

    render(os.path.join(OUT, 'hist-capacitive-inrush.svg'), W, H, *f)


if __name__ == '__main__':
    fig_edges()
    fig_topologies()
    fig_spike()
    fig_timeline()
    fig_cap_inrush()
    print("ok:", os.listdir(OUT))
