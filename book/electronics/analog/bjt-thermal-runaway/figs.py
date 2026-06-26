# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Петля додатного зворотного зв'язку (саме розгін) ──────────────────────
def fig_loop():
    W, H = 720, 380
    parts = []
    cx, cy = W / 2, 210
    # чотири вузли петлі по колу
    nodes = [
        (cx,        78,  "температура\nкристала ↑"),
        (cx + 250,  cy,  "струм\nколектора ↑"),
        (cx,        342, "потужність\nна кристалі ↑"),
        (cx - 250,  cy,  "ще тепліше"),
    ]
    boxes = []
    for x, y, s in nodes:
        b, w, h = textbox(x, y, s, size=15, pad=12, bold=True,
                          fill="#fdecea", stroke=POS, sw=2)
        boxes.append((x, y, w, h))
        parts.append(b)
    # дуги-стрілки за годинниковою (між сусідніми вузлами)
    seq = [0, 1, 2, 3, 0]
    for i in range(4):
        x1, y1, _, _ = boxes[seq[i]]
        x2, y2, _, _ = boxes[seq[i + 1]]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # відсунути кінці від центрів рамок
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        parts.append(arrow(x1 + ux * 95, y1 + uy * 45,
                           x2 - ux * 95, y2 - uy * 45, color=POS, sw=2.4))
    parts.append(text(cx, cy + 5, "+", size=40, color=POS, bold=True))
    parts.append(text(cx, cy + 34, "замкнена петля", size=13, color=MUTED))
    return render(os.path.join(OUT, 'runaway-loop.svg'), W, H, *parts,
                  title="Тепловий розгін — петля з додатним знаком")


# ── 2. Зсув кривої Vbe(T): тепліше → крива ліворуч → за тієї ж напруги більший струм ──
def fig_vbe_shift():
    W, H = 720, 420
    parts = []
    ox, oy = 110, 350          # початок осей
    aw, ah = 540, 280
    parts.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))        # вісь Vbe
    parts.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))        # вісь Ic
    parts.append(text(ox + aw, oy + 26, "напруга база–емітер  Vbe", size=13, color=INK, anchor="end"))
    parts.append(text(ox - 14, oy - ah, "струм  Ic", size=13, color=INK, anchor="end"))

    import math
    def expo(shift, color, dash=None):
        # експонента Ic ~ exp((V-shift)/k); shift зсуває криву ліворуч (тепліше)
        k = 46.0
        pts = []
        for px in range(0, aw + 1, 4):
            v = px
            y = math.exp((v - 250 + shift) / k)
            if y > ah:
                y = ah
            pts.append((ox + px, oy - y))
            if y >= ah:
                break
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>' % (d, color, da))

    parts.append(expo(0,  NEG))          # холодна крива
    parts.append(expo(60, POS))          # гаряча крива (зсунута ліворуч)

    # фіксована напруга зміщення — вертикаль
    vx = ox + 232
    parts.append(line(vx, oy, vx, oy - ah, color=MUTED, sw=1.4, dash="4 4"))
    parts.append(text(vx, oy + 20, "та сама\nVbe".split("\n")[0], size=12, color=MUTED))
    parts.append(text(vx, oy + 34, "Vbe", size=12, color=MUTED))

    # точки перетину вертикалі з двома кривими
    k = 46.0
    y_cold = math.exp((232 - 250 + 0) / k)
    y_hot = math.exp((232 - 250 + 60) / k)
    y_cold = min(y_cold, ah); y_hot = min(y_hot, ah)
    parts.append(circle(vx, oy - y_cold, 5, fill=NEG, stroke=NEG))
    parts.append(circle(vx, oy - y_hot, 5, fill=POS, stroke=POS))
    parts.append(arrow(vx + 16, oy - y_cold, vx + 16, oy - y_hot + 6, color=POS, sw=2))
    parts.append(text(vx + 26, oy - (y_cold + y_hot) / 2, "+ΔIc", size=13, color=POS, anchor="start", bold=True))

    parts.append(fitbox(ox + 300, oy - ah + 6, 230, 52,
                        "−2 мВ/°C: нагрів зсуває\nкриву ліворуч",
                        size=13, fill="#fdecea", stroke=POS, color=POS))
    parts.append(text(ox + 70, oy - ah + 20, "холодний", size=12, color=NEG, anchor="start", bold=True))
    return render(os.path.join(OUT, 'vbe-shift.svg'), W, H, *parts,
                  title="Чому нагрів сам піднімає струм за незмінної напруги")


# ── 3. Емітерний резистор розриває петлю ────────────────────────────────────
def fig_emitter_cure():
    W, H = 720, 360
    parts = []
    # ліворуч: без Re — петля замкнена; праворуч: з Re — розірвана
    # ЛІВО
    lx = 185
    parts.append(text(lx, 56, "Без емітерного резистора", size=14, bold=True, color=POS))
    a, _, _ = textbox(lx, 120, "Ic ↑", size=15, bold=True, fill="#fdecea", stroke=POS, sw=2)
    b, _, _ = textbox(lx, 250, "нагрів ↑", size=15, bold=True, fill="#fdecea", stroke=POS, sw=2)
    parts += [a, b]
    parts.append(arrow(lx + 36, 132, lx + 36, 232, color=POS, sw=2.4))
    parts.append(arrow(lx - 36, 232, lx - 36, 132, color=POS, sw=2.4))
    parts.append(text(lx + 92, 190, "ніщо\nне гальмує".split("\n")[0], size=12, color=MUTED, anchor="start"))
    parts.append(text(lx + 92, 204, "ніщо не гальмує", size=12, color=MUTED, anchor="start"))

    # розділювач
    parts.append(line(W / 2, 44, W / 2, H - 24, color=MUTED, sw=1.2, dash="5 5"))

    # ПРАВО
    rx = 535
    parts.append(text(rx, 56, "З емітерним резистором Re", size=14, bold=True, color=FIELD))
    c, _, _ = textbox(rx, 120, "Ic хоче ↑", size=15, bold=True, fill="#eafaf0", stroke=FIELD, sw=2)
    d, _, _ = textbox(rx, 250, "більше падає на Re", size=14, bold=True, fill="#eafaf0", stroke=FIELD, sw=2)
    parts += [c, d]
    parts.append(arrow(rx + 70, 132, rx + 70, 232, color=FIELD, sw=2.4))
    # зустрічна стрілка — гальмо (повертає назад і прикриває)
    parts.append(arrow(rx - 70, 232, rx - 70, 132, color=NEG, sw=2.4))
    parts.append(text(rx - 78, 190, "Vbe падає →\nIc назад".split("\n")[0], size=12, color=NEG, anchor="end"))
    parts.append(text(rx - 78, 204, "Ic назад", size=12, color=NEG, anchor="end"))
    parts.append(text(rx, H - 18, "петлю розірвано", size=13, color=FIELD, bold=True))
    return render(os.path.join(OUT, 'emitter-cure.svg'), W, H, *parts,
                  title="Емітерний резистор — від'ємний зворотний зв'язок проти розгону")


if __name__ == '__main__':
    fig_loop()
    fig_vbe_shift()
    fig_emitter_cure()
    print('figs done')
