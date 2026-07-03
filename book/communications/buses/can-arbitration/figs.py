# -*- coding: utf-8 -*-
"""Фігури до теми «Арбітраж CAN».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Дротове-І: один «домінантний» вузол тягне всю шину в 0 ─────────────────
def fig_wired_and():
    W, H = 760, 400
    f = [text(W / 2, 28, "Домінантний біт (0) перемагає рецесивний (1): досить одного, хто тягне лінію вниз",
              size=14.5, bold=True)]

    # спільна лінія шини
    busY = 300
    x0, x1 = 70, W - 70
    f.append(line(x0, busY, x1, busY, color=INK, sw=3))
    f.append(text(x0 - 8, busY + 4, "шина", size=11, bold=True, color=INK, anchor="end"))

    # три вузли зверху, кожен «штовхає» своє значення
    nodes = [
        (200, "1", True,  "рецесивний\n(відпускає)"),
        (380, "0", False, "ДОМІНАНТНИЙ\n(тягне вниз)"),
        (560, "1", True,  "рецесивний\n(відпускає)"),
    ]
    for nx, bit, recessive, note in nodes:
        col = NEG if recessive else POS
        fill = "#eaf0fd" if recessive else "#fdecea"
        f.append(rect(nx - 46, 70, 92, 58, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(text(nx, 92, "вузол", size=10.5, color=MUTED))
        f.append(text(nx, 116, "шле «%s»" % bit, size=12, bold=True, color=col))
        # з'єднання вниз до шини
        if recessive:
            # рецесивний: «відпускає» — пунктир, стрілки немає
            f.append(line(nx, 128, nx, busY, color=MUTED, sw=1.4, dash="4,4"))
            f.append(text(nx, 168, note.split("\n")[0], size=9.5, color=MUTED))
            f.append(text(nx, 182, note.split("\n")[1], size=9.5, color=MUTED))
        else:
            # домінантний: активно тягне — товста лінія зі стрілкою вниз
            f.append(arrow(nx, 128, nx, busY - 6, color=POS, sw=2.6))
            f.append(text(nx, 168, note.split("\n")[0], size=9.5, bold=True, color=POS))
            f.append(text(nx, 182, note.split("\n")[1], size=9.5, color=POS))

    # підтяжка, що тримає рецесивний рівень, коли ніхто не тягне
    f.append(line(x1, busY, x1, busY - 40, color=NEG, sw=1.6))
    f.append(rect(x1 - 10, busY - 62, 20, 16, fill=BG, stroke=NEG, sw=1.4))
    f.append(text(x1, busY - 74, "підтяжка → «1»", size=9.5, color=NEG))

    b, _, _ = textbox(W / 2, 372,
                      "результат на шині = 0: логіка дротового-І (wired-AND) — 0 перемагає всіх",
                      size=11.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "wired-and.svg"), W, H, *f)


# ── 2. Побітовий арбітраж: хто послав рецесивний, а побачив домінантний — вибуває ─
def fig_arbitration():
    W, H = 780, 470
    f = [text(W / 2, 26, "Арбітраж біт за бітом: у кого менший ідентифікатор — той і виграв, без зіткнення",
              size=14.5, bold=True)]

    # три вузли з різними ID (11 біт скорочено до 8 для наочності)
    # A = 0b0011.0100, B = 0b0011.0010, C = 0b0011.0110
    ids = [
        ("A", [0, 0, 1, 1, 0, 1, 0, 0]),
        ("B", [0, 0, 1, 1, 0, 0, 1, 0]),
        ("C", [0, 0, 1, 1, 0, 1, 1, 0]),
    ]
    bus = [0, 0, 1, 1, 0, 0, 1, 0]  # дротове-І усіх, хто ще в грі
    nbits = 8

    ox = 150
    step = (W - ox - 60) / nbits
    rowH = 46
    topY = 74

    # заголовок бітів
    for k in range(nbits):
        f.append(text(ox + step * (k + 0.5), topY - 10, "b%d" % (nbits - 1 - k),
                      size=9.5, color=MUTED))

    # де кожен вузол вибуває: перший біт, де він рецесивний(1), а шина домінантна(0)
    def drop_at(bits):
        for k in range(nbits):
            if bits[k] == 1 and bus[k] == 0:
                return k
        return None

    drops = {name: drop_at(bits) for name, bits in ids}

    for r, (name, bits) in enumerate(ids):
        y = topY + 14 + r * rowH
        d = drops[name]
        col = FIELD if d is None else INK
        f.append(text(ox - 16, y + 4, "вузол " + name, size=11, bold=True,
                      color=col, anchor="end"))
        for k in range(nbits):
            cx = ox + step * (k + 0.5)
            lost = (d is not None and k > d)
            if lost:
                # вибув — блідо
                f.append(text(cx, y + 4, str(bits[k]), size=12, color="#c3cad4"))
                continue
            bit = bits[k]
            bcol = POS if bit == 0 else NEG
            # позначка: цей вузол на цьому біті шле 0 чи 1
            f.append(text(cx, y + 4, str(bit), size=13, bold=(k == d), color=bcol))
            if k == d:
                # саме тут програв: обвести
                f.append(circle(cx, y, 12, fill="none", stroke=POS, sw=2))
        if d is not None:
            f.append(text(ox + step * (d + 0.5), y + 22, "вибув", size=9, color=POS))
        else:
            f.append(text(ox + step * nbits + 8, y + 4, "← ВИГРАВ", size=10.5,
                          bold=True, color=FIELD, anchor="start"))

    # рядок шини (дротове-І)
    ybus = topY + 14 + 3 * rowH + 10
    f.append(line(ox - 120, ybus - 22, W - 50, ybus - 22, color="#d6dde6", sw=1.2, dash="5,5"))
    f.append(text(ox - 16, ybus + 4, "ШИНА", size=11, bold=True, color=INK, anchor="end"))
    for k in range(nbits):
        cx = ox + step * (k + 0.5)
        bcol = POS if bus[k] == 0 else NEG
        f.append(rect(cx - 13, ybus - 14, 26, 26, fill=("#fdecea" if bus[k] == 0 else "#eaf0fd"),
                      stroke=bcol, sw=1.4, rx=4))
        f.append(text(cx, ybus + 5, str(bus[k]), size=13, bold=True, color=bcol))

    b, _, _ = textbox(W / 2, 448,
                      "хто послав «1», а на шині побачив «0» — миттєво замовкає; переможець веде кадр далі неушкодженим",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "arbitration.svg"), W, H, *f)


# ── 3. Домінантний і рецесивний на диференційній парі CAN_H / CAN_L ───────────
def fig_levels():
    W, H = 740, 400
    f = [text(W / 2, 26, "«0» і «1» на парі CAN: домінантний РОЗВОДИТЬ лінії, рецесивний їх ЗВОДИТЬ",
              size=14.5, bold=True)]

    cw = 320
    lx, rx = 55, W - 55 - cw
    topY = 58
    boxH = 250

    # вертикальна вісь напруги (спільна ідея для обох панелей — підписи в кожній)
    def panel(px, title, tcol, fillc, vH, vL, note):
        f.append(rect(px, topY, cw, boxH, fill=fillc, stroke=tcol, sw=1.8, rx=10))
        f.append(text(px + cw / 2, topY + 24, title, size=12.5, bold=True, color=tcol))
        # осі: 0..5 В
        axX = px + 60
        axTop, axBot = topY + 50, topY + 200
        f.append(line(axX, axTop, axX, axBot, color=MUTED, sw=1.2))
        for v, lab in ((0, "0 В"), (2.5, "2.5"), (5, "5 В")):
            yy = axBot - (v / 5.0) * (axBot - axTop)
            f.append(line(axX - 4, yy, axX + 4, yy, color=MUTED, sw=1))
            f.append(text(axX - 8, yy + 4, lab, size=8.5, color=MUTED, anchor="end"))
        # рівні CAN_H і CAN_L
        xr0, xr1 = axX + 20, px + cw - 24
        yH = axBot - (vH / 5.0) * (axBot - axTop)
        yL = axBot - (vL / 5.0) * (axBot - axTop)
        f.append(line(xr0, yH, xr1, yH, color=POS, sw=2.6))
        f.append(text(xr1 + 2, yH + 4, "CAN_H", size=9.5, bold=True, color=POS, anchor="start"))
        f.append(line(xr0, yL, xr1, yL, color=NEG, sw=2.6))
        f.append(text(xr1 + 2, yL + 4, "CAN_L", size=9.5, bold=True, color=NEG, anchor="start"))
        # стрілка різниці
        xm = (xr0 + xr1) / 2
        if abs(yH - yL) > 6:
            f.append(arrow(xm, yL - 1, xm, yH + 1, color=FIELD, sw=1.6))
            f.append(arrow(xm, yH + 1, xm, yL - 1, color=FIELD, sw=1.6))
            f.append(text(xm + 8, (yH + yL) / 2 + 4, "≈2 В", size=9.5, bold=True, color=FIELD, anchor="start"))
        else:
            f.append(text(xm, yH - 8, "різниця ≈ 0", size=9.5, color=MUTED))
        f.append(text(px + cw / 2, topY + 226, note, size=10.3, italic=True, color=tcol))

    panel(lx, "Рецесивний = «1» (спокій)", NEG, "#eaf0fd",
          2.5, 2.5, "обидві лінії ≈2.5 В → різниця ≈0")
    panel(rx, "Домінантний = «0» (активний)", POS, "#fbeee6",
          3.5, 1.5, "H вгору, L вниз → різниця ≈2 В")

    b, _, _ = textbox(W / 2, 380,
                      "рецесивний легко «перетягти»: досить одному розвести лінії — і вся шина бачить домінантний 0",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "levels.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wired_and()
    fig_arbitration()
    fig_levels()
    print("OK: 3 figures ->", IMG)
