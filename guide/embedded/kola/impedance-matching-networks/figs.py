# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def cap_sym(x, y, horiz=False, label=None, lcolor=MUTED):
    """Конденсатор: дві паралельні пластини. (x,y) — центр. Виводи по осі."""
    g = 6   # півзазор між пластинами
    pl = 14  # довжина пластини
    out = []
    if horiz:
        out.append(line(x - g, y - pl, x - g, y + pl, color=INK, sw=2.4))
        out.append(line(x + g, y - pl, x + g, y + pl, color=INK, sw=2.4))
    else:
        out.append(line(x - pl, y - g, x + pl, y - g, color=INK, sw=2.4))
        out.append(line(x - pl, y + g, x + pl, y + g, color=INK, sw=2.4))
    if label:
        out.append(text(x + (pl + 12 if horiz else 0),
                        y + (4 if horiz else -pl - 8),
                        label, size=13, color=lcolor,
                        anchor='start' if horiz else 'middle', bold=True))
    return "".join(out)


def coil_sym(x1, y1, x2, y2, label=None, lcolor=MUTED):
    """Котушка: ланцюжок дужок уздовж відрізка (горизонт. або вертик.)."""
    out = []
    bumps = 4
    if y1 == y2:  # горизонтальна
        span = x2 - x1
        r = span / (2 * bumps)
        d = ["M %.1f %.1f" % (x1, y1)]
        for i in range(bumps):
            cx = x1 + (2 * i + 1) * r
            d.append("A %.1f %.1f 0 0 1 %.1f %.1f" % (r, r, cx + r, y1))
        path = '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(d), INK)
        out.append(path)
        if label:
            out.append(text((x1 + x2) / 2, y1 - r - 8, label, size=13, color=lcolor, bold=True))
    else:  # вертикальна
        span = y2 - y1
        r = span / (2 * bumps)
        d = ["M %.1f %.1f" % (x1, y1)]
        for i in range(bumps):
            cy = y1 + (2 * i + 1) * r
            d.append("A %.1f %.1f 0 0 0 %.1f %.1f" % (r, r, x1, cy + r))
        path = '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(d), INK)
        out.append(path)
        if label:
            out.append(text(x1 + r + 10, (y1 + y2) / 2 + 4, label, size=13, color=lcolor, anchor='start', bold=True))
    return "".join(out)


def node(cx, cy):
    return circle(cx, cy, 3.2, fill=INK, stroke=INK, sw=1)


def src_box(x, y, w, h, lines):
    return fitbox(x, y, w, h, lines, size=13, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG)


def load_box(x, y, w, h, lines):
    return fitbox(x, y, w, h, lines, size=13, fill="#fdecea", stroke=POS, bold=True, color=POS)


# ── Фігура 1: L-ланка між джерелом і навантаженням ──────────────────────────
def fig_l_network():
    W, H = 720, 340
    f = []
    yb = 250          # нижня (спільна) шина
    yt = 150          # верхня шина сигналу
    # джерело
    f.append(src_box(40, yt - 28, 110, 96, "Джерело\nбачить 50 Ω"))
    # навантаження
    f.append(load_box(W - 150, yt - 28, 110, 96, "Наван-\nтаження\n200 Ω"))
    # верхній провід: джерело -> вузол A -> послідовна котушка -> вузол B -> навантаження
    xA = 250
    xB = 470
    f.append(line(150, yt, xA, yt, color=LINE, sw=2))
    f.append(coil_sym(xA, yt, xB, yt, label="Xs  (послідовна)", lcolor=INK))
    f.append(line(xB, yt, W - 150, yt, color=LINE, sw=2))
    f.append(node(xA, yt))
    f.append(node(xB, yt))
    # паралельний конденсатор: з вузла A вниз на спільну шину
    f.append(line(xA, yt, xA, yt + 26, color=LINE, sw=2))
    f.append(cap_sym(xA, yt + 46, horiz=False))
    f.append(line(xA, yt + 60, xA, yb, color=LINE, sw=2))
    f.append(text(xA - 16, yt + 50, "Xp", size=13, color=INK, anchor='end', bold=True))
    f.append(text(xA - 16, yt + 68, "(паралельна)", size=11, color=MUTED, anchor='end'))
    # спільна нижня шина
    f.append(line(95, yt + 68, 95, yb, color=LINE, sw=2))
    f.append(line(95, yb, W - 95, yb, color=LINE, sw=2))
    f.append(line(W - 95, yt + 68, W - 95, yb, color=LINE, sw=2))
    f.append(node(xA, yb))
    # підписи ролей
    f.append(text(W / 2, yb + 34, "послідовна гасить реактивний залишок · паралельна тягне активний опір до цілі",
                  size=12, color=MUTED))
    f.append(text(W / 2, yb + 56, "тільки реактивності → жодного ома, що грів би",
                  size=12, color=FIELD, bold=True))
    render(os.path.join(OUT, 'l-network.svg'), W, H, *f,
           title="L-ланка: дві реактивності між джерелом і навантаженням")


# ── Фігура 2: два кроки трансформації (R вниз, X у нуль) ─────────────────────
def fig_two_steps():
    W, H = 720, 300
    f = []
    cy = 165
    bw, bh = 150, 70
    gap = 60
    x0 = 30
    # три стани, з'єднані стрілками
    st = [
        ("Навантаження", "R = 200 Ω\nX = 0", FILL, LINE, INK),
        ("Після паралельної", "R → 50 Ω\nX = залишок", "#eafaf0", FIELD, INK),
        ("Після послідовної", "R = 50 Ω\nX = 0", "#eaf0fd", NEG, NEG),
    ]
    xs = []
    x = x0
    for i, (cap, body, fill, stroke, col) in enumerate(st):
        xs.append(x)
        f.append(text(x + bw / 2, cy - bh / 2 - 14, cap, size=13, color=MUTED, bold=True))
        f.append(fitbox(x, cy - bh / 2, bw, bh, body, size=14, fill=fill, stroke=stroke, color=col, bold=True))
        x += bw + gap
    # стрілки + підписи дій
    a1x1 = xs[0] + bw
    a1x2 = xs[1]
    f.append(arrow(a1x1 + 6, cy, a1x2 - 6, cy, color=FIELD, sw=2.2))
    f.append(text((a1x1 + a1x2) / 2, cy - 12, "паралельний", size=11, color=FIELD, bold=True))
    f.append(text((a1x1 + a1x2) / 2, cy + 22, "рухає R", size=11, color=FIELD))
    a2x1 = xs[1] + bw
    a2x2 = xs[2]
    f.append(arrow(a2x1 + 6, cy, a2x2 - 6, cy, color=NEG, sw=2.2))
    f.append(text((a2x1 + a2x2) / 2, cy - 12, "послідовний", size=11, color=NEG, bold=True))
    f.append(text((a2x1 + a2x2) / 2, cy + 22, "гасить X", size=11, color=NEG))
    # підсумок
    f.append(text(W / 2, cy + bh / 2 + 60,
                  "трансформація опору й гасіння залишку — дві окремі дії двох елементів",
                  size=12.5, color=INK))
    render(os.path.join(OUT, 'two-steps.svg'), W, H, *f,
           title="L-ланка у два кроки: спершу опір, тоді реактивність")


# ── Фігура 3: топології L, П, Т ─────────────────────────────────────────────
def topo_frame(ox, oy, w, h, title):
    out = [rect(ox, oy, w, h, fill=BG, stroke="#d0d4da", sw=1.3, rx=8)]
    out.append(text(ox + w / 2, oy + 22, title, size=14, color=INK, bold=True))
    return out


def fig_topologies():
    W, H = 760, 320
    f = []
    pw = 232
    ph = 230
    pad = 16
    gap = (W - 3 * pw - 2 * pad) / 2
    oy = 56
    yt = oy + 90     # верхня шина
    yb = oy + 180    # нижня шина
    xs_in = 36       # відступ входу всередині панелі
    xs_out = pw - 36

    # --- панель L ---
    ox = pad
    f += topo_frame(ox, oy, pw, ph, "L  (дві реактивності)")
    xin, xout = ox + xs_in, ox + xs_out
    xmid = (xin + xout) / 2
    f.append(line(xin, yt, xmid, yt, color=LINE, sw=2))
    f.append(coil_sym(xmid, yt, xout, yt))
    f.append(line(xin, yb, xout, yb, color=LINE, sw=2))
    f.append(line(xin, yt, xin, yb, color=LINE, sw=2))   # лівий борт (вхід)
    f.append(line(xout, yt, xout, yb, color=LINE, sw=2))  # правий борт (вихід)
    f.append(line(xmid, yt, xmid, yt + 22, color=LINE, sw=2))
    f.append(cap_sym(xmid, yt + 42, horiz=False))
    f.append(line(xmid, yt + 56, xmid, yb, color=LINE, sw=2))
    f.append(node(xmid, yt)); f.append(node(xmid, yb))
    f.append(text(ox + pw / 2, oy + ph - 14, "Q задано відношенням опорів", size=11, color=MUTED))

    # --- панель П ---
    ox = pad + pw + gap
    f += topo_frame(ox, oy, pw, ph, "П  (три реактивності)")
    xin, xout = ox + xs_in, ox + xs_out
    f.append(line(xin, yt, xout, yt, color=LINE, sw=2))
    f.append(line(xin, yb, xout, yb, color=LINE, sw=2))
    # послідовна котушка посередині верхньої шини
    f.append(coil_sym(xin + 40, yt, xout - 40, yt))
    # два паралельні конденсатори по краях
    for xc in (xin, xout):
        f.append(line(xc, yt, xc, yt + 22, color=LINE, sw=2))
        f.append(cap_sym(xc, yt + 42, horiz=False))
        f.append(line(xc, yt + 56, xc, yb, color=LINE, sw=2))
        f.append(node(xc, yt)); f.append(node(xc, yb))
    f.append(text(ox + pw / 2, oy + ph - 14, "+ вільний параметр: смуга", size=11, color=FIELD, bold=True))

    # --- панель Т ---
    ox = pad + 2 * (pw + gap)
    f += topo_frame(ox, oy, pw, ph, "Т  (три реактивності)")
    xin, xout = ox + xs_in, ox + xs_out
    xmid = (xin + xout) / 2
    f.append(line(xin, yb, xout, yb, color=LINE, sw=2))
    f.append(line(xin, yt, xin, yb, color=LINE, sw=2))
    f.append(line(xout, yt, xout, yb, color=LINE, sw=2))
    # два послідовні елементи на верхній шині
    f.append(coil_sym(xin, yt, xmid - 6, yt))
    f.append(coil_sym(xmid + 6, yt, xout, yt))
    f.append(node(xmid, yt))
    # паралельний конденсатор посередині
    f.append(line(xmid, yt, xmid, yt + 22, color=LINE, sw=2))
    f.append(cap_sym(xmid, yt + 42, horiz=False))
    f.append(line(xmid, yt + 56, xmid, yb, color=LINE, sw=2))
    f.append(node(xmid, yb))
    f.append(text(ox + pw / 2, oy + ph - 14, "гнучка до широких навантажень", size=11, color=MUTED))

    render(os.path.join(OUT, 'topologies.svg'), W, H, *f,
           title="Топології узгоджувачів: L, П і Т")


if __name__ == '__main__':
    fig_l_network()
    fig_two_steps()
    fig_topologies()
    print("done")
