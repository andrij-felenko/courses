# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CSCOL = "#b07d00"   # колір ліній CS — теплий, окремий від трьох спільних


# ── star: зіркова топологія — спільні SCK/MOSI/MISO + окремий CS на кожного ────
# Ідея: три горизонтальні шини спільні для всіх ведених, а CS іде від ведучого
# до кожного веденого окремою лінією; звідси формула 3 + N ніжок.

def fig_star():
    W, H = 720, 360
    p = []
    # ведучий ліворуч
    mx, my, mw, mh = 40, 96, 120, 150
    p.append(rect(mx, my, mw, mh, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(mx + mw / 2, my + 26, "ВЕДУЧИЙ", size=13, color=FIELD, bold=True))
    p.append(text(mx + mw / 2, my + 44, "(master)", size=10, color=MUTED, italic=True))

    # три спільні шини — горизонтальні лінії під веденими
    bus_x0, bus_x1 = mx + mw, 690
    buses = [("SCK", 300, INK), ("MOSI", 318, POS), ("MISO", 336, FIELD)]
    for name, by, col in buses:
        p.append(line(bus_x0, by, bus_x1, by, color=col, sw=2.2))
        p.append(text(mx + mw + 6, by - 4, name, size=9.5, color=col, bold=True, anchor="start"))

    # три ведені у ряд
    sw_, sh_ = 120, 96
    sy = my
    sxs = [230, 400, 570]
    for i, sx in enumerate(sxs):
        p.append(rect(sx, sy, sw_, sh_, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(sx + sw_ / 2, sy + 26, "ведений %d" % i, size=11, color=INK, bold=True))
        # відведення трьох спільних шин угору в коробку
        for _, by, col in buses:
            p.append(line(sx + sw_ / 2, sy + sh_, sx + sw_ / 2, by, color=col, sw=1.1))
        # власна CS від ведучого до кожного
        p.append(text(sx + sw_ / 2, sy + 50, "CS%d" % i, size=11, color=CSCOL, bold=True))
        ax, ay = sx + sw_ / 2, sy + 56
        p.append(line(mx + mw, my + mh - 10, ax, ay, color=CSCOL, sw=1.6,
                      dash=None if i == 0 else "4 4"))
        # вістря стрілки вручну (svgkit arrow лише пряма з маркером)
    # підпис групи CS біля ведучого
    p.append(text(mx + mw / 2 - 2, my + mh - 20, "CS0 CS1 CS2", size=9.5, color=CSCOL, bold=True))

    p.append(text(W / 2, H - 18,
                  "три лінії спільні для всіх; CS — окрема на кожного → 3 + N ніжок",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "star.svg"), W, H, *p,
           title="Зірка: спільні SCK/MOSI/MISO, окремий CS на кожного")


# ── one-cs: рівно одна CS активна — інакше конфлікт на MISO ────────────────────
# Ідея: дві панелі. Ліворуч — опущена одна CS, MISO жене один ведений (добре).
# Праворуч — опущено дві CS, двоє женуть MISO разом (конфлікт, коротке).

def fig_one_cs():
    W, H = 720, 300
    p = []
    panel_w = 320
    for side, ox, title, ok in (("L", 30, "одна CS = 0 — гаразд", True),
                                ("R", 370, "дві CS = 0 — конфлікт", False)):
        p.append(rect(ox, 60, panel_w, 200,
                      fill="#eef6ef" if ok else "#fdecea",
                      stroke=FIELD if ok else POS, sw=1.8))
        p.append(text(ox + panel_w / 2, 84, title, size=12,
                      color=FIELD if ok else POS, bold=True))
        # лінія MISO
        miso_y = 224
        p.append(line(ox + 20, miso_y, ox + panel_w - 20, miso_y, color=INK, sw=2.0))
        p.append(text(ox + 24, miso_y + 16, "MISO", size=10, color=INK, anchor="start", bold=True))
        # двоє ведених
        for k, sx in enumerate((ox + 50, ox + panel_w - 130)):
            active = (k == 0) or (not ok)   # лівий завжди активний; правий — лише в конфлікті
            p.append(rect(sx, 110, 80, 60,
                          fill="#dff0df" if active else BG,
                          stroke=FIELD if active else MUTED, sw=1.6))
            p.append(text(sx + 40, 134, "ведений", size=9.5,
                          color=INK if active else MUTED))
            p.append(text(sx + 40, 150, "CS=0" if active else "CS=1", size=10,
                          color=FIELD if active else MUTED, bold=True))
            # лінія від веденого до MISO
            p.append(line(sx + 40, 170, sx + 40, miso_y,
                          color=FIELD if active else MUTED, sw=2.0 if active else 1.0,
                          dash=None if active else "3 4"))
            if active:
                p.append(text(sx + 40, 196, "жене", size=9, color=FIELD))
        if not ok:
            p.append(text(ox + panel_w / 2, miso_y + 16,
                          "двоє женуть → коротке", size=10, color=POS, bold=True))
    render(os.path.join(OUT, "one-cs.svg"), W, H, *p,
           title="Рівно одна CS активна (інакше конфлікт на MISO)")


# ── pin-cost: ціна в ніжках — SPI 3 + N проти двох у I2C ───────────────────────
# Ідея: дві криві кількості ніжок від числа ведених; SPI росте, I2C плаский.

def fig_pin_cost():
    W, H = 700, 320
    ox, oy = 70, 250
    aw, ah = 560, 196
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "ведених, N", size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 14, oy - ah - 2, "ніжок", size=11, color=INK, bold=True, anchor="end"))

    nmax, pinmax = 10, 14
    sx = aw / nmax
    sy = ah / pinmax

    def pt(n, pins):
        return ox + n * sx, oy - pins * sy

    # SPI: 3 + N
    spi = [pt(n, 3 + n) for n in range(1, nmax + 1)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % q for q in spi), POS))
    for n in (1, 5, 10):
        x, y = pt(n, 3 + n)
        p.append(circle(x, y, 3.2, fill=POS, stroke=POS))
        p.append(text(x, y - 10, "%d" % (3 + n), size=10, color=POS, bold=True))

    # I2C: завжди 2
    i2c = [pt(n, 2) for n in range(1, nmax + 1)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % q for q in i2c), FIELD))

    # легенда
    p.append(line(ox + 30, oy - ah + 8, ox + 56, oy - ah + 8, color=POS, sw=2.6))
    p.append(text(ox + 62, oy - ah + 12, "SPI: 3 + N (росте з кожним веденим)",
                  size=11, color=POS, anchor="start", bold=True))
    p.append(line(ox + 30, oy - ah + 28, ox + 56, oy - ah + 28, color=FIELD, sw=2.6))
    p.append(text(ox + 62, oy - ah + 32, "I2C: 2 (хоч скільки пристроїв)",
                  size=11, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "pin-cost.svg"), W, H, *p,
           title="Ціна в ніжках: SPI росте як 3 + N, I2C тримає 2")


# ── daisy: ланцюжок — один CS на всіх, дані течуть наскрізь ────────────────────
# Ідея: ведені послідовно (MOSI → S0 → S1 → S2 → MISO назад); SCK і один CS
# спільні; усе разом — одне довге кільце зсувних регістрів.

def fig_daisy():
    W, H = 720, 320
    p = []
    y = 150
    mx, mw, mh = 30, 100, 80
    p.append(rect(mx, y - mh / 2, mw, mh, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(mx + mw / 2, y - 4, "ВЕДУЧИЙ", size=11, color=FIELD, bold=True))
    p.append(text(mx + mw / 2, y + 14, "(master)", size=9, color=MUTED, italic=True))

    sxs = [190, 360, 530]
    sw_, sh_ = 110, 70
    prev_r = mx + mw
    for i, sx in enumerate(sxs):
        p.append(rect(sx, y - sh_ / 2, sw_, sh_, fill=FILL, stroke=INK, sw=1.8))
        p.append(text(sx + sw_ / 2, y + 4, "S%d" % i, size=13, color=INK, bold=True))
        p.append(arrow(prev_r, y - 14, sx, y - 14, color=POS, sw=2))
        prev_r = sx + sw_
    p.append(text((mx + mw + sxs[0]) / 2, y - 22, "MOSI", size=9, color=POS, bold=True))

    # MISO останнього повертається до ведучого знизу
    last_r = sxs[-1] + sw_
    ret_y = y + 90
    p.append(line(last_r, y - 14, last_r + 24, y - 14, color=FIELD, sw=2))
    p.append(line(last_r + 24, y - 14, last_r + 24, ret_y, color=FIELD, sw=2))
    p.append(line(last_r + 24, ret_y, mx + mw / 2, ret_y, color=FIELD, sw=2))
    p.append(line(mx + mw / 2, ret_y, mx + mw / 2, y + mh / 2, color=FIELD, sw=2,
                  dash=None))
    p.append(arrow(mx + mw / 2, ret_y - 1, mx + mw / 2, y + mh / 2, color=FIELD, sw=2))
    p.append(text((last_r + mx) / 2, ret_y - 8, "MISO останнього повертається до ведучого",
                  size=10, color=FIELD, italic=True))

    p.append(text(W / 2, 70, "SCK і ОДНА CS — спільні на всіх", size=12, color=CSCOL, bold=True))
    p.append(text(W / 2, H - 18,
                  "дані прошивають усіх поспіль, наче один довгий зсувний регістр",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "daisy.svg"), W, H, *p,
           title="Ланцюжок (daisy-chain): один CS, дані наскрізь")


# ── decoder: дешифратор робить багато CS з кількох ліній ──────────────────────
# Ідея: ведучий дає 3 адресні лінії в дешифратор «3-у-8», той піднімає рівно
# один із 8 виходів CS; 3 ніжки керують вісьмома пристроями.

def fig_decoder():
    W, H = 720, 360
    p = []
    mx, my, mw, mh = 30, 130, 110, 90
    p.append(rect(mx, my, mw, mh, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text(mx + mw / 2, my + mh / 2 - 6, "ВЕДУЧИЙ", size=11, color=FIELD, bold=True))
    p.append(text(mx + mw / 2, my + mh / 2 + 12, "3 лінії", size=10, color=MUTED, italic=True))

    # дешифратор
    dx, dy, dw, dh = 240, 90, 130, 180
    p.append(rect(dx, dy, dw, dh, fill="#fff7e6", stroke=CSCOL, sw=2))
    p.append(text(dx + dw / 2, dy + dh / 2 - 6, "дешифратор", size=12, color=CSCOL, bold=True))
    p.append(text(dx + dw / 2, dy + dh / 2 + 12, "3 → 8", size=13, color=CSCOL, bold=True))

    # 3 адресні лінії ведучий → дешифратор
    for k in range(3):
        ly = my + 22 + k * 22
        p.append(line(mx + mw, ly, dx, dy + 30 + k * 22, color=INK, sw=1.6))
    p.append(text((mx + mw + dx) / 2, my + 8, "A0 A1 A2", size=10, color=INK, bold=True))

    # 8 виходів CS
    ox2 = dx + dw
    for k in range(8):
        oy2 = dy + 14 + k * (dh - 28) / 7
        p.append(line(ox2, oy2, ox2 + 70, oy2, color=CSCOL, sw=1.4))
        p.append(text(ox2 + 76, oy2 + 4, "CS%d" % k, size=9.5, color=CSCOL, anchor="start", bold=True))
    p.append(text(ox2 + 100, dy - 6, "8 окремих CS", size=11, color=CSCOL, bold=True, anchor="middle"))

    p.append(text(W / 2, H - 18,
                  "3 ніжки замість 8: активний завжди рівно один вихід",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "decoder.svg"), W, H, *p,
           title="Дешифратор: багато CS із кількох ліній")


# ── pitfalls: три часті помилки з лінією CS ───────────────────────────────────
# Ідея: три картки-симптоми, кожна — окрема аварія й коротка протидія.

def fig_pitfalls():
    W, H = 720, 300
    p = []
    cards = [
        ("Плаваюча CS", "ніжка «у повітрі» —\nведений ловить хибний\nвибір", "тримай CS визначеною"),
        ("Дві опущені CS", "двоє ведених женуть\nMISO разом —\nконфлікт", "опускай рівно одну"),
        ("CS не піднято", "команди «злипаються»\nодна з одною", "піднімай після обміну"),
    ]
    cw, gap = 210, 20
    x = (W - (cw * 3 + gap * 2)) / 2
    for title, body, fix in cards:
        p.append(rect(x, 64, cw, 180, fill="#fdecea", stroke=POS, sw=1.8))
        p.append(text(x + cw / 2, 92, title, size=13, color=POS, bold=True))
        p.append(mtext(x + cw / 2, 124, body, size=11, color=INK, lh=1.35))
        p.append(line(x + 16, 198, x + cw - 16, 198, color=POS, sw=1.0, dash="3 3"))
        p.append(mtext(x + cw / 2, 220, fix, size=11, color=FIELD, bold=True))
        x += cw + gap
    p.append(text(W / 2, H - 16,
                  "усі CS високі за замовчуванням; одну опустив на обмін — одразу підняв",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "pitfalls.svg"), W, H, *p,
           title="Часті пастки з лінією CS")


if __name__ == "__main__":
    fig_star()
    fig_one_cs()
    fig_pin_cost()
    fig_daisy()
    fig_decoder()
    fig_pitfalls()
    print("OK: figures written to", OUT)
