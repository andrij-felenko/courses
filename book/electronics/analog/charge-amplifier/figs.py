# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def opamp(cx, cy, w=70, h=64, label="−A"):
    """Трикутник ОП, вершина праворуч. Повертає (svg, in_minus_xy, in_plus_xy, out_xy)."""
    x0 = cx - w / 2
    top = (x0, cy - h / 2)
    bot = (x0, cy + h / 2)
    tip = (cx + w / 2, cy)
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
           % (top[0], top[1], bot[0], bot[1], tip[0], tip[1], "#f4f6f8", LINE))
    in_minus = (x0, cy - h / 4)
    in_plus = (x0, cy + h / 4)
    out = tip
    s = tri
    s += text(x0 + 12, in_minus[1] + 5, "−", size=16, color=NEG, bold=True)
    s += text(x0 + 12, in_plus[1] + 5, "+", size=16, color=POS, bold=True)
    return s, in_minus, in_plus, out


def gnd(x, y, label=None):
    s = line(x, y, x, y + 10)
    s += line(x - 11, y + 10, x + 11, y + 10, sw=2)
    s += line(x - 7, y + 14, x + 7, y + 14, sw=2)
    s += line(x - 3, y + 18, x + 3, y + 18, sw=2)
    if label:
        s += text(x, y + 33, label, size=11, color=MUTED)
    return s


def cap(x1, y1, x2, y2, label=None, color=LINE):
    """Конденсатор між двома точками (горизонтальний); дві пластини посередині."""
    mx = (x1 + x2) / 2
    s = line(x1, y1, mx - 5, y1, color=color)
    s += line(mx - 5, y1 - 11, mx - 5, y1 + 11, color=color, sw=2.4)
    s += line(mx + 5, y1 - 11, mx + 5, y1 + 11, color=color, sw=2.4)
    s += line(mx + 5, y1, x2, y1, color=color)
    if label:
        s += text(mx, y1 - 17, label, size=12, color=color, bold=True)
    return s


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1: чому зарядовий, а не вольтовий — кабель псує вольтовий, не псує зарядовий
# ════════════════════════════════════════════════════════════════════════════
def fig_why():
    W, H = 760, 430
    p = []
    p.append(text(W / 2, 26, "Один давач, два підсилювачі — кабель псує лише вольтовий", size=16, bold=True))

    # ── Верх: вольтовий підсилювач ──
    yv = 130
    p.append(text(150, 58, "Вольтовий вхід", size=13, bold=True, color=NEG))
    # п'єзо як джерело заряду
    p.append(circle(80, yv, 20, fill="#fff"))
    p.append(text(80, yv + 5, "q", size=15, italic=True, bold=True))
    p.append(text(80, yv - 30, "п'єзо", size=11, color=MUTED))
    p.append(gnd(80, yv + 20))
    # кабель -> ємність кабелю на землю
    p.append(line(100, yv, 250, yv))
    # вертикальний конденсатор кабелю
    p.append(line(220, yv, 220, yv + 28))
    p.append(line(212, yv + 28, 228, yv + 28, sw=2.4))
    p.append(line(212, yv + 36, 228, yv + 36, sw=2.4))
    p.append(text(262, yv + 36, "C_каб", size=12, color=POS, bold=True))
    p.append(gnd(220, yv + 40))
    # вхід підсилювача (буфер, дуже високий вхідний опір)
    sa, im, ip, out = opamp(330, yv, label="×1")
    p.append(sa)
    p.append(line(250, yv, im[0], im[1]))
    p.append(gnd(ip[0] - 4, ip[1] + 4))
    p.append(line(ip[0], ip[1], ip[0] - 4, ip[1]))
    p.append(line(out[0], out[1], 420, yv))
    p.append(text(450, yv + 5, "U_вих", size=13, bold=True))
    # підпис проблеми
    box = fitbox(490, yv - 34, 250, 70,
                 "U = q / (C_п'єзо + C_каб)\nкабель ВХОДИТЬ у знаменник →\nдовжина кабелю міняє підсилення",
                 size=11, fill="#fdecea", stroke=POS, color="#7a2018")
    p.append(box)

    # роздільник
    p.append(line(40, 232, W - 40, 232, color="#d0d4d8", dash="5 5"))

    # ── Низ: зарядовий підсилювач ──
    yc = 330
    p.append(text(150, 262, "Зарядовий вхід", size=13, bold=True, color=FIELD))
    p.append(circle(80, yc, 20, fill="#fff"))
    p.append(text(80, yc + 5, "q", size=15, italic=True, bold=True))
    p.append(text(80, yc - 30, "п'єзо", size=11, color=MUTED))
    p.append(gnd(80, yc + 20))
    # кабель
    p.append(line(100, yc, 300, yc))
    # ємність кабелю — тепер між сигналом і ВІРТУАЛЬНОЮ землею: напруга на ній 0
    p.append(line(220, yc, 220, yc + 28))
    p.append(line(212, yc + 28, 228, yc + 28, sw=2.4))
    p.append(line(212, yc + 36, 228, yc + 36, sw=2.4))
    p.append(text(262, yc + 36, "C_каб", size=12, color=MUTED, bold=True))
    p.append(gnd(220, yc + 40))
    # ОП із ємнісним ЗЗ
    sa, im, ip, out = opamp(380, yc, label="−A")
    p.append(line(300, yc, im[0], im[1]))
    p.append(gnd(ip[0] - 4, ip[1] + 4))
    p.append(line(ip[0], ip[1], ip[0] - 4, ip[1]))
    # вузол віртуальної землі
    p.append(circle(im[0], im[1], 3.2, fill=FIELD, stroke=FIELD))
    p.append(text(im[0] - 6, im[1] - 12, "0 В", size=11, color=FIELD, bold=True, anchor="end"))
    # зворотний конденсатор C_f зверху
    p.append(line(im[0], im[1], im[0], yc - 56))
    p.append(cap(im[0], yc - 56, out[0] + 30, yc - 56, label="C_f", color=NEG))
    p.append(line(out[0] + 30, yc - 56, out[0] + 30, yc))
    p.append(sa)
    p.append(line(out[0], yc, out[0] + 30, yc))
    p.append(line(out[0] + 30, yc, 470, yc))
    p.append(text(498, yc + 5, "U_вих", size=13, bold=True))
    box = fitbox(540, yc - 34, 200, 70,
                 "U = − q / C_f\nкабель — між 0 В і 0 В:\nне заряджається, не впливає",
                 size=11, fill="#eafaf1", stroke=FIELD, color="#1e6b3a")
    p.append(box)

    render(os.path.join(IMG, 'why-charge.svg'), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2: будова зарядового підсилювача — заряд перетікає на C_f, R_f скидає DC
# ════════════════════════════════════════════════════════════════════════════
def fig_circuit():
    W, H = 700, 380
    p = []
    p.append(text(W / 2, 26, "Будова: заряд давача перетікає на C_f, а R_f повільно скидає сталу", size=15, bold=True))

    yc = 215
    # п'єзо-давач: джерело заряду + власна ємність
    p.append(circle(70, yc, 22, fill="#fff"))
    p.append(text(70, yc + 5, "q", size=16, italic=True, bold=True))
    p.append(text(70, yc - 33, "п'єзодавач", size=11, color=MUTED))
    p.append(gnd(70, yc + 22))
    p.append(line(92, yc, 250, yc))

    # ОП
    sa, im, ip, out = opamp(330, yc, label="−A")
    p.append(line(250, yc, im[0], im[1]))
    p.append(gnd(ip[0] - 4, ip[1] + 4))
    p.append(line(ip[0], ip[1], ip[0] - 4, ip[1]))
    p.append(sa)

    # вузол віртуальної землі
    nx, ny = im[0], im[1]
    p.append(circle(nx, ny, 3.4, fill=FIELD, stroke=FIELD))
    p.append(text(nx - 8, ny - 30, "віртуальна", size=11, color=FIELD, bold=True, anchor="middle"))
    p.append(text(nx - 8, ny - 17, "земля ≈ 0 В", size=11, color=FIELD, bold=True, anchor="middle"))

    # вихід
    ox = out[0] + 40
    p.append(line(out[0], yc, ox, yc))
    p.append(line(ox, yc, 560, yc))
    p.append(text(592, yc + 5, "U_вих", size=14, bold=True))

    # C_f зверху (ближній рівень)
    p.append(line(nx, ny, nx, yc - 56))
    p.append(cap(nx, yc - 56, ox, yc - 56, label="C_f  (задає підсилення)", color=NEG))
    p.append(line(ox, yc - 56, ox, yc))

    # R_f паралельно (дальній рівень) — скидання заряду
    p.append(line(nx, ny, nx, yc - 100))
    rx1 = nx
    rx2 = ox
    p.append(line(rx1, yc - 100, rx1 + 50, yc - 100))
    # зигзаг резистора
    zx = rx1 + 50
    zy = yc - 100
    seg = (rx2 - 30 - zx) / 6
    path = "M%.1f %.1f" % (zx, zy)
    for i in range(1, 6):
        xx = zx + i * seg
        yy = zy + (10 if i % 2 else -10)
        path += " L%.1f %.1f" % (xx, yy)
    path += " L%.1f %.1f" % (rx2 - 30, zy)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (path, MUTED))
    p.append(line(rx2 - 30, zy, ox, zy))
    p.append(line(ox, zy, ox, yc - 56))
    p.append(text((rx1 + rx2) / 2, yc - 112, "R_f  (дуже великий: скидає сталу)", size=12, color=MUTED, bold=True))

    # підпис під схемою — рух заряду
    box = fitbox(70, yc + 60, 560, 56,
                 "Скільки заряду давач уганяє у вузол — стільки ОП «забирає» на C_f, тримаючи вузол при 0 В.\n"
                 "Уся напруга з'являється на C_f:  U_вих = − q / C_f.",
                 size=12, fill="#f4f6f8", stroke=LINE)
    p.append(box)

    render(os.path.join(IMG, 'circuit.svg'), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3: відгук на сталу силу — без R_f тримає вічно, з R_f повільно «спливає»
# ════════════════════════════════════════════════════════════════════════════
def fig_droop():
    W, H = 700, 320
    p = []
    p.append(text(W / 2, 26, "Відгук на тривалу силу: R_f задає, як швидко вихід «спливає» до нуля", size=15, bold=True))

    # осі
    x0, y0 = 90, 250
    xmax, ytop = 640, 70
    p.append(arrow(x0, y0, xmax, y0))
    p.append(arrow(x0, y0, x0, ytop))
    p.append(text(xmax, y0 + 22, "час", size=12, color=MUTED, anchor="end"))
    p.append(text(x0 - 10, ytop + 4, "U_вих", size=12, color=MUTED, anchor="end"))

    # момент прикладання сили
    tx = 170
    p.append(line(tx, y0, tx, ytop + 10, color="#d0d4d8", dash="4 4"))
    p.append(text(tx, y0 + 20, "сила прикладена", size=11, color=MUTED))

    ylevel = 110  # рівень «повного» виходу

    # ідеал: без R_f — ступінь і тримається
    import math
    # стрибок вертикально
    p.append(line(tx, y0, tx, ylevel, color=FIELD, sw=2.4))
    p.append(line(tx, ylevel, xmax - 6, ylevel, color=FIELD, sw=2.4))
    p.append(text(xmax - 6, ylevel - 8, "без R_f: тримає (ідеал)", size=11, color=FIELD, bold=True, anchor="end"))

    # реал: з R_f — стрибок, тоді експоненційний спад
    p.append(line(tx, y0, tx, ylevel, color=NEG, sw=2.4))
    pts = []
    tau_px = 150.0
    for i in range(0, 471):
        x = tx + i
        if x > xmax - 6:
            break
        u = (y0 - ylevel) * math.exp(-i / tau_px)
        y = y0 - u
        pts.append((x, y))
    path = "M%.1f %.1f" % (pts[0][0], pts[0][1])
    for x, y in pts[1:]:
        path += " L%.1f %.1f" % (x, y)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, NEG))
    p.append(text(tx + 175, ylevel + 70, "з R_f: спливає за τ = R_f·C_f", size=11, color=NEG, bold=True, anchor="middle"))

    # позначка тау
    ttau = tx + tau_px
    p.append(line(ttau, y0, ttau, y0 + 6, color=NEG))
    p.append(text(ttau, y0 + 20, "τ", size=12, color=NEG, italic=True, bold=True))

    box = fitbox(x0, y0 + 36, xmax - x0, 40,
                 "Сталу силу п'єзодавач не «бачить» вічно: заряд стікає крізь R_f. Великий R_f → довгий τ → нижче можна виміряти.",
                 size=11, fill="#f4f6f8", stroke=LINE)
    p.append(box)

    render(os.path.join(IMG, 'droop.svg'), W, H, *p)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 (історія): шлях від п'єзоефекту 1880 до промислового вимірювання
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W, H = 780, 360
    p = []
    p.append(text(W / 2, 28, "Сім десятиліть від відкриття ефекту до приладу", size=16, bold=True))

    # вісь часу
    ax0, ax1 = 70, W - 40
    ay = 150
    p.append(line(ax0, ay, ax1, ay, color=LINE, sw=2.2))
    p.append(arrow(ax1 - 0.1, ay, ax1, ay))

    # роки → координата (1880…1970)
    def xof(year):
        return ax0 + (ax1 - ax0 - 16) * (year - 1880) / (1970 - 1880)

    # ділення-роки на осі
    for yr in (1880, 1900, 1920, 1940, 1960):
        x = xof(yr)
        p.append(line(x, ay - 5, x, ay + 5, color=MUTED, sw=1.4))
        p.append(text(x, ay + 20, str(yr), size=11, color=MUTED))

    # довга «мертва» пауза 1880→1948 — затінити
    p.append(line(xof(1882), ay, xof(1947), ay, color="#c9ccd1", sw=6))
    p.append(text((xof(1882) + xof(1947)) / 2, ay - 12,
                  "майже 70 років без надійного приладу", size=11, color=MUTED, italic=True))

    # ── віхи: (рік, текст, угору?, колір рамки, заливка, колір тексту) ──
    def milestone(year, lines, up, stroke, fill, tcol):
        x = xof(year)
        # точка на осі
        p.append(circle(x, ay, 4.2, fill=stroke, stroke=stroke))
        bw, bh = 168, 60
        if up:
            by = ay - 34 - bh
            p.append(line(x, ay - 4, x, by + bh, color=stroke, sw=1.4))
        else:
            by = ay + 34
            p.append(line(x, ay + 4, x, by, color=stroke, sw=1.4))
        bx = min(max(x - bw / 2, 8), W - 8 - bw)
        p.append(fitbox(bx, by, bw, bh, lines, size=11, fill=fill, stroke=stroke, color=tcol))

    milestone(1880, "1880 — брати Кюрі\nкварц під силою віддає заряд\n(але заряд тікає й гуляє)",
              up=True, stroke=MUTED, fill="#f4f6f8", tcol=INK)
    milestone(1948, "≈1948 — Кістлер (SLM, Вінтертур)\nвузол при 0 В, заряд → на C_f\nпатент 1950",
              up=False, stroke=FIELD, fill="#eafaf1", tcol="#1e6b3a")
    milestone(1965, "1960-ті — MOSFET + тефлон/каптон\nмала база дозріла →\nпромислове застосування",
              up=True, stroke=NEG, fill="#eaf0fd", tcol="#1b3a8a")

    render(os.path.join(IMG, 'timeline.svg'), W, H, *p)


if __name__ == '__main__':
    fig_why()
    fig_circuit()
    fig_droop()
    fig_timeline()
    print("ok")
