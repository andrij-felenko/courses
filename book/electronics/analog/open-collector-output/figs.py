# -*- coding: utf-8 -*-
"""Фігури до теми «Вихід з відкритим колектором».
Три фігури:
  oc-circuit.svg   — схема ВК із зовнішньою підтяжкою, два стани
  wired-and.svg    — кілька ВК на одній лінії (монтажне «І»)
  pullup-tradeoff.svg — компроміс підтяжки: швидкість фронту проти струму
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def vrail(cx, y, label):
    """Вузол живлення: коротка горизонталь + підпис."""
    return (line(cx - 16, y, cx + 16, y, color=POS, sw=2.4) +
            text(cx, y - 8, label, size=13, color=POS, bold=True))


def res_v(cx, ytop, ylen, label=None, side="right"):
    """Вертикальний резистор (зиґзаґ) від ytop донизу на ylen."""
    n, w = 6, 7
    seg = ylen / (n + 1)
    pts = ["%.1f,%.1f" % (cx, ytop), "%.1f,%.1f" % (cx, ytop + seg / 2)]
    for i in range(n):
        x = cx + (w if i % 2 == 0 else -w)
        pts.append("%.1f,%.1f" % (x, ytop + seg / 2 + seg * (i + 0.5)))
    pts.append("%.1f,%.1f" % (cx, ytop + ylen - seg / 2))
    pts.append("%.1f,%.1f" % (cx, ytop + ylen))
    out = '<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (
        " ".join(pts), INK)
    if label:
        lx = cx + 16 if side == "right" else cx - 16
        anc = "start" if side == "right" else "end"
        out += text(lx, ytop + ylen / 2 + 4, label, size=12, color=INK,
                    anchor=anc)
    return out


def npn(cx, cy, label=None, on=False):
    """Символ NPN: коло, база зліва, колектор угорі, емітер унизу зі стрілкою.
    Повертає (svg, ctop_y, cbot_y, base_x) — точки під'єднання."""
    r = 20
    col = FIELD if on else INK
    body = circle(cx, cy, r, fill="#eafaf0" if on else FILL, stroke=col, sw=2)
    # вертикальна пластина бази
    body += line(cx - 6, cy - 13, cx - 6, cy + 13, color=col, sw=2.6)
    # вивід бази вліво
    body += line(cx - 6, cy, cx - 24, cy, color=col, sw=2)
    # колектор (угору)
    body += line(cx - 6, cy - 8, cx + 9, cy - 18, color=col, sw=2)
    body += line(cx + 9, cy - 18, cx + 9, cy - 34, color=col, sw=2)
    # емітер (униз, зі стрілкою назовні)
    body += line(cx - 6, cy + 8, cx + 9, cy + 18, color=col, sw=2)
    body += line(cx + 9, cy + 18, cx + 9, cy + 34, color=col, sw=2)
    # стрілка емітера
    ax, ay = cx + 4.5, cy + 14
    body += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
             % (ax, ay, ax + 9, ay + 1, ax + 3, ay + 7, col))
    if label:
        body += text(cx + 30, cy + 4, label, size=12, color=INK, anchor="start")
    return body, cy - 34, cy + 34, cx - 24


def node(cx, cy):
    return circle(cx, cy, 3.2, fill=INK, stroke=INK, sw=1)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — схема ВК із підтяжкою, два стани
# ════════════════════════════════════════════════════════════════════════════
def fig_circuit():
    W, H = 640, 380
    f = []
    f.append(text(W / 2, 26, "Вихід з відкритим колектором: транзистор лише тягне вниз",
                  size=15, bold=True))

    def one(ox, title, on, level_txt, level_col):
        g = []
        railx, raily = ox, 70
        g.append(vrail(railx, raily, "+Vpu"))
        # підтяжка від шини до вузла виходу
        g.append(res_v(railx, raily, 60, "Rпідт", side="right"))
        outy = raily + 60
        # вузол виходу
        outx = railx
        g.append(node(outx, outy))
        # лінія виходу вправо
        g.append(line(outx, outy, outx + 70, outy, color=INK, sw=2))
        g.append(text(outx + 74, outy - 8, "вихід", size=12, color=INK,
                      anchor="start"))
        lb, lw, lh = textbox(outx + 96, outy + 16, level_txt, size=12,
                             fill="#eafaf0" if level_col == FIELD else "#fdecea",
                             stroke=level_col, bold=True)
        g.append(lb)
        # колектор транзистора йде до вузла виходу
        tr, ctop, cbot, bx = npn(outx, outy + 70, on=on)
        g.append(line(outx, outy, outx, ctop, color=INK, sw=2))
        g.append(tr)
        # база
        g.append(line(bx, outy + 70, bx - 34, outy + 70, color=INK, sw=2))
        bb, bw, bh = textbox(bx - 60, outy + 70,
                             "1" if on else "0", size=13,
                             fill="#eafaf0" if on else FILL,
                             stroke=FIELD if on else MUTED, bold=True)
        g.append(bb)
        g.append(text(bx - 60, outy + 92, "вхід", size=10, color=MUTED))
        # земля
        g.append(line(outx, cbot, outx, cbot + 8, color=INK, sw=2))
        g.append(gnd(outx, cbot + 8))
        g.append(text(ox, 52, title, size=12, color=INK, bold=True))
        return "".join(g)

    f.append(one(150, "Вхід «1» → транзистор відкритий", True,
                 "≈ 0 В\nтягне", FIELD))
    f.append(one(440, "Вхід «0» → транзистор закритий", False,
                 "≈ +Vpu\nвідпускає", POS))

    f.append(render(os.path.join(IMG, "oc-circuit.svg"), W, H, *f))


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — монтажне «І»: кілька ВК на одній лінії
# ════════════════════════════════════════════════════════════════════════════
def fig_wired_and():
    W, H = 640, 360
    f = []
    f.append(text(W / 2, 26, "Спільна лінія: хто потягнув вниз — той і виграв",
                  size=15, bold=True))
    busy = 150
    x0, x1 = 70, 540
    # шина живлення + підтяжка
    f.append(vrail(110, 70, "+Vpu"))
    f.append(res_v(110, 70, 56, "Rпідт", side="left"))
    f.append(line(110, 126, 110, busy, color=INK, sw=2))
    f.append(node(110, busy))
    # спільна лінія
    f.append(line(x0, busy, x1, busy, color=INK, sw=2.6))
    f.append(text(x1 + 6, busy + 4, "спільна\nлінія".split("\n")[0], size=11,
                  color=MUTED, anchor="start"))
    f.append(text(x1 + 6, busy + 17, "лінія", size=11, color=MUTED,
                  anchor="start"))

    # три транзистори, що звисають із лінії
    states = [("A: 0", False), ("B: 1", True), ("C: 0", False)]
    xs = [200, 320, 440]
    pulled = any(on for _, on in states)
    for (lab, on), xx in zip(states, xs):
        f.append(node(xx, busy))
        tr, ctop, cbot, bx = npn(xx, busy + 70, on=on)
        f.append(line(xx, busy, xx, ctop, color=INK, sw=2))
        f.append(tr)
        f.append(line(xx, cbot, xx, cbot + 8, color=INK, sw=2))
        f.append(gnd(xx, cbot + 8))
        bb, bw, bh = textbox(xx, busy + 122, lab, size=12,
                             fill="#eafaf0" if on else FILL,
                             stroke=FIELD if on else MUTED, bold=True)
        f.append(bb)

    # підсумок-стан лінії
    res, rw, rh = textbox(110, busy + 90,
                          "лінія = 0\n(B потягнув)", size=12,
                          fill="#eafaf0", stroke=FIELD, bold=True)
    f.append(res)
    f.append(arrow(110, busy + 8, 110, busy + 90 - rh / 2, color=FIELD, sw=1.6))

    note, nw, nh = textbox(W / 2, H - 26,
                           "Лінія на «1», лише поки мовчать усі; один відкритий транзистор — і вся лінія на «0».",
                           size=11, fill=FILL, stroke=MUTED)
    f.append(note)
    f.append(render(os.path.join(IMG, "wired-and.svg"), W, H, *f))


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — компроміс підтяжки
# ════════════════════════════════════════════════════════════════════════════
def fig_tradeoff():
    W, H = 680, 340
    f = []
    f.append(text(W / 2, 26, "Підтяжка: великий опір економить струм, та сповільнює фронт",
                  size=15, bold=True))
    # осі
    ox, oy = 80, 250          # початок координат
    axw, axh = 430, 170
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=2))          # час →
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=2))          # напруга ↑
    f.append(text(ox + axw, oy + 22, "час", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - axh + 4, "U", size=13, color=MUTED, anchor="end"))
    # рівень +Vpu
    vtop = oy - axh + 20
    f.append(line(ox, vtop, ox + axw, vtop, color=POS, sw=1.4, dash="5,4"))
    f.append(text(ox + axw + 4, vtop + 4, "+Vpu", size=11, color=POS,
                  anchor="start"))
    f.append(line(ox, oy, ox + axw, oy, color=NEG, sw=1.0, dash="3,4"))

    # момент відпускання транзистора
    t0 = ox + 60
    f.append(line(t0, oy, t0, vtop, color=MUTED, sw=1.0, dash="2,4"))
    f.append(text(t0, oy + 18, "транзистор відпустив", size=10, color=MUTED))

    def curve(tau_px, color, lab1, lab2, laby):
        pts = []
        span = axw - 40
        for i in range(0, span + 1, 4):
            t = i
            u = (vtop - oy) * (1 - math.exp(-t / tau_px)) + oy
            pts.append("%.1f,%.1f" % (t0 + t, u))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), color))
        lx = t0 + span + 8
        f.append(text(lx, laby, lab1, size=11, color=color, anchor="start"))
        f.append(text(lx, laby + 14, lab2, size=11, color=color, anchor="start"))

    curve(45, FIELD, "малий Rпідт:", "фронт крутий", vtop + 30)
    curve(150, POS, "великий Rпідт:", "фронт млявий", vtop + 72)

    note, nw, nh = textbox(W / 2, H - 22,
                           "Спад до «0» транзистор робить різко; підйом до «1» тягне лише підтяжка: τ = Rпідт · C.",
                           size=11, fill=FILL, stroke=MUTED)
    f.append(note)
    f.append(render(os.path.join(IMG, "pullup-tradeoff.svg"), W, H, *f))


if __name__ == "__main__":
    fig_circuit()
    fig_wired_and()
    fig_tradeoff()
    print("OK: 3 файли у", IMG)
