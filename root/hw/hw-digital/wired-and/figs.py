# -*- coding: utf-8 -*-
"""Фігури до теми «Шина wired-AND».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Кут теми — ШИНА: багато мовців на одному дроті, «0» домінує над «1».
Підпис несе .md, тож великого заголовка всередині малюнка немає (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ZERO = NEG   # «0» / низький / домінантний — холодний синій
ONE  = POS   # «1» / високий / рецесивний — гарячий червоний


def gnd(cx, cy):
    return (line(cx, cy, cx, cy + 8, color=INK, sw=2) +
            line(cx - 9, cy + 8, cx + 9, cy + 8, color=INK, sw=2) +
            line(cx - 5, cy + 12, cx + 5, cy + 12, color=INK, sw=2) +
            line(cx - 2, cy + 16, cx + 2, cy + 16, color=INK, sw=2))


def pullup(cx, y_top, y_bus):
    """Резистор-підтяжка від VDD (згори) до шини: зиґзаґ + позначка Rp."""
    out = [text(cx, y_top - 6, "VDD", size=12, color=POS, bold=True),
           line(cx, y_top, cx, y_top + 14, color=INK, sw=2)]
    zx, zy = cx, y_top + 14
    pts = "%d,%d " % (zx, zy)
    for dx in [7, -7, 7, -7, 7, -7, 0]:
        zy += 8
        pts += "%d,%d " % (zx + dx, zy)
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, INK))
    out.append(text(cx - 26, zy - 22, "Rp", size=12, color=MUTED, italic=True))
    out.append(line(cx, zy, cx, y_bus, color=INK, sw=2))
    return "".join(out)


def sink(cx, cy, on, label, sub=None):
    """Ключ «лише вниз» (open-drain): on=True тягне вниз, on=False відпустив."""
    out = []
    box_c = ONE if on else MUTED
    out.append(rect(cx - 16, cy - 14, 32, 28, fill=BG, stroke=box_c, sw=2, rx=4))
    if on:
        out.append(line(cx, cy - 14, cx, cy + 14, color=ONE, sw=3))
    else:
        out.append(line(cx, cy - 14, cx, cy - 4, color=MUTED, sw=2.4))
        out.append(line(cx, cy + 4, cx, cy + 14, color=MUTED, sw=2.4))
        out.append(line(cx - 7, cy - 4, cx + 7, cy - 4, color=MUTED, sw=2.4))
    out.append(text(cx, cy + 30, label, size=12, color=INK))
    if sub is None:
        sub = "жене «0»" if on else "хоче «1»"
    out.append(text(cx, cy + 45, sub, size=10.5, color=(ONE if on else MUTED)))
    return "".join(out)


# ═══════════════════════════════════════════════════════════════════════════
# 1. КОНТРАКТ ШИНИ: багато мовців кажуть свій біт, а на дроті — «І» усіх.
#    Один домінантний «0» перекриває будь-яку кількість рецесивних «1».
#    Це таблиця шини, а не окремого вентиля: важить лише «є хоч один 0?».
# ═══════════════════════════════════════════════════════════════════════════
def fig_bus_contract():
    W, H = 720, 340
    f = []
    busy = 118
    busx1, busx2 = 150, 560
    f.append(pullup(85, 58, busy))
    f.append(line(85, busy, busx2, busy, color=INK, sw=3))
    f.append(text((busx1 + busx2) / 2, busy - 12, "спільна лінія  (усі під'єднані сюди)",
                  size=12, color=MUTED))
    # чотири мовці; один жене «0»
    xs = [210, 310, 410, 500]
    states = [False, False, True, False]   # третій домінує
    for x, on in zip(xs, states):
        f.append(line(x, busy, x, busy + 24, color=INK, sw=2))
        f.append(sink(x, busy + 38, on, "вузол"))
        f.append(gnd(x, busy + 68))
    # рівень на лінії = І усіх = 0 (кружечок одразу на кінці шини)
    res = "0" if any(states) else "1"
    rc = ZERO if res == "0" else ONE
    f.append(circle(busx2 + 24, busy, 15, fill=BG, stroke=rc, sw=2.6))
    f.append(text(busx2 + 24, busy + 6, res, size=18, color=rc, bold=True))
    f.append(text(busx2 + 24, busy - 24, "рівень шини", size=10.5, color=MUTED))
    # права рамка: правило шини — нижче, під кружечком, щоб не накладалась
    body, bw, bh = textbox(628, 200, "один «0»\nб'є будь-яке\nчисло «1»",
                           size=13, bold=True, fill="#eaf0fd", stroke=NEG)
    f.append(body)
    # низ: словник (два коротші рядки, щоб не вилазило за 720)
    f.append(text(W / 2, H - 46,
                  "«0» = домінантний: активно тягне, перемагає   ·   «1» = рецесивний: лише відпускає, поступається",
                  size=11, color=INK))
    f.append(text(W / 2, H - 22,
                  "шина = 1  ⟺  ВСІ рецесивні      шина = 0  ⟺  ХОЧ ОДИН домінантний",
                  size=12, color=INK, bold=True))
    render(os.path.join(IMG, "bus-contract.svg"), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# 2. УНАНІМНА ЗГОДА: «уся система готова». Кожен тримає «0», поки зайнятий,
#    і відпускає в «1», коли скінчив. Лінія підстрибне в «1» ЛИШЕ коли ВСІ
#    відпустили — це «І» усіх, зроблене дротом. Показуємо два моменти часу.
# ═══════════════════════════════════════════════════════════════════════════
def fig_ready_consensus():
    W, H = 720, 340
    f = []
    midx = W / 2
    f.append(line(midx, 66, midx, H - 26, color=MUTED, sw=1, dash="5,5"))

    def scene(ox, title, tcol, states, res):
        g = []
        busy = 132
        bx1, bx2 = ox - 120, ox + 120
        g.append(text(ox, 60, title, size=13, color=tcol, bold=True))
        g.append(pullup(ox - 150, 82, busy))
        g.append(line(ox - 150, busy, bx2, busy, color=INK, sw=3))
        xs = [ox - 70, ox, ox + 70]
        labs = ["A", "B", "C"]
        for x, on, lab in zip(xs, states, labs):
            g.append(line(x, busy, x, busy + 22, color=INK, sw=2))
            g.append(sink(x, busy + 34, on, lab,
                          sub=("зайнятий" if on else "готовий")))
            g.append(gnd(x, busy + 64))
        rc = ZERO if res == "0" else ONE
        g.append(circle(bx2 + 22, busy, 13, fill=BG, stroke=rc, sw=2.5))
        g.append(text(bx2 + 22, busy + 5, res, size=15, color=rc, bold=True))
        return "".join(g)

    f.append(scene(190, "поки хоч хто зайнятий", NEG,
                   [True, False, True], "0"))
    f.append(text(190, H - 34, "READY = 0 → «ще не всі»", size=12, color=ZERO, bold=True))
    f.append(scene(W - 190, "коли ВСІ відпустили", FIELD,
                   [False, False, False], "1"))
    f.append(text(W - 190, H - 34, "READY = 1 → «уся система готова»",
                  size=12, color=FIELD, bold=True))
    render(os.path.join(IMG, "ready-consensus.svg"), W, H, *f,
           title="Спільний READY: «1» лише за згоди всіх — це «І» дротом")


# ═══════════════════════════════════════════════════════════════════════════
# 3. ЦІНА ШИНИ: спад різкий (активний), підйом млявий (Rp заряджає ємність
#    усієї шини). Що більше вузлів — то більша Cш і повільніший фронт «1».
#    Показуємо форму сигналу: миттєвий зріз униз, RC-хвіст угору.
# ═══════════════════════════════════════════════════════════════════════════
def fig_rise_cost():
    import math
    W, H = 720, 300
    f = []
    ox, oy = 90, 210        # початок осей (лівий-нижній)
    plot_w, plot_h = 470, 150
    lo, hi = oy, oy - plot_h
    # осі
    f.append(line(ox, oy, ox + plot_w, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, hi - 10, color=MUTED, sw=1.5))
    f.append(text(ox - 16, lo + 4, "0", size=11, color=MUTED))
    f.append(text(ox - 16, hi + 4, "1", size=11, color=MUTED))
    f.append(text(ox + plot_w / 2, oy + 34, "час →", size=11, color=MUTED))

    # рівень «високо» тримається, тоді хтось тягне → різкий зріз униз
    x0 = ox + 20
    x_fall = ox + 150
    f.append(line(x0, hi, x_fall, hi, color=ONE, sw=2.6))         # рецесивна «1»
    f.append(line(x_fall, hi, x_fall, lo, color=ZERO, sw=2.6))    # активний спад
    f.append(text(x_fall, hi - 12, "хтось потягнув", size=10.5, color=ZERO))
    f.append(line(x_fall, lo, x_fall + 90, lo, color=ZERO, sw=2.6))  # домінантний «0»
    f.append(text(x_fall + 45, lo + 18, "тримає «0»", size=10.5, color=ZERO))

    # відпустив → пасивний RC-підйом крізь Rp
    x_rel = x_fall + 90
    pts = []
    for i in range(0, 141):
        t = i / 40.0                       # у сталих часу τ
        y = lo + (hi - lo) * (1 - math.exp(-t))
        pts.append("%.1f,%.1f" % (x_rel + i * 1.6, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), ONE))
    # підпис підйому — над кривою, у вільному верху праворуч
    f.append(mtext(x_rel + 105, hi - 4, ["млявий підйом:", "Rp заряджає Cш"],
                   size=10.5, color=INK))
    # пунктир порогу; підпис — ліворуч під віссю «1», щоб не чіпати рамку
    yth = lo + (hi - lo) * 0.7
    f.append(line(ox, yth, ox + plot_w, yth, color=MUTED, sw=1, dash="4,4"))
    f.append(text(ox + 6, yth - 6, "поріг «1»", size=10, color=MUTED, anchor="start"))

    # права рамка — компроміс
    body, bw, bh = textbox(650, 120,
                           "більше вузлів\n→ більша Cш\n→ повільніша «1»",
                           size=11.5, bold=True, fill="#fdecea", stroke=POS)
    f.append(body)
    f.append(mtext(650, 190, ["менша Rp —", "швидше, але", "гарячіший «0»"],
                   size=10.5, color=MUTED))
    render(os.path.join(IMG, "rise-cost.svg"), W, H, *f,
           title="Спад активний і різкий, підйом пасивний і млявий")


if __name__ == "__main__":
    fig_bus_contract()
    fig_ready_consensus()
    fig_rise_cost()
    print("OK: 3 фігури у", IMG)
