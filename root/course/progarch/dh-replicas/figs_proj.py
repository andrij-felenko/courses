# -*- coding: utf-8 -*-
# Фігури для вставки proj-dh-replica-reads.md. Окремий скрипт (не чіпає figs.py,
# який паралельно редагують інші агенти). Вивід — у ту саму теку ./img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
NEUT    = "#eef2f6"
AMBER_D = "#b06d0a"


# ── Фігура: що показав вимір — баг проти маршрутизації ─────────────────────────
def fig_measure():
    W, H = 1180, 560
    f = []
    f.append(text(590, 40, "Що показав вимір: баг проти маршрутизації", size=17, bold=True))

    # ── ЛІВА панель: read-your-writes порушено ──
    f.append(text(320, 86, "read-your-writes порушено", size=14, bold=True))
    f.append(text(320, 106, "(з 577 перечитувань екрана)", size=12, color=MUTED))
    axis_y = 468
    f.append(line(150, axis_y, 560, axis_y, color=INK, sw=1.6))

    bx1, bw = 220, 96
    h1 = 300                                              # 346 → 300 px
    f.append(rect(bx1, axis_y - h1, bw, h1, fill=RED_T, stroke=POS, sw=1.8))
    f.append(text(bx1 + bw / 2, axis_y - h1 - 34, "346", size=22, color=POS, bold=True))
    f.append(text(bx1 + bw / 2, axis_y - h1 - 14, "60% стейл", size=12, color=POS, bold=True))
    f.append(mtext(bx1 + bw / 2, axis_y + 24, ["БЕЗ", "маршрутизації"], size=12, bold=True))

    bx2 = 410
    f.append(rect(bx2, axis_y - 5, bw, 5, fill=GREEN_T, stroke=FIELD, sw=1.8))
    f.append(text(bx2 + bw / 2, axis_y - 22, "0", size=22, color=FIELD, bold=True))
    f.append(mtext(bx2 + bw / 2, axis_y + 24, ["З", "маршрутизацією"], size=12, bold=True))

    f.append(text(320, 522, "…і 59 стрибків «час назад» → теж 0", size=12, color=MUTED, italic=True))

    # ── ПРАВА панель: куди пішли читання ──
    f.append(text(870, 86, "Куди пішли читання (з маршрутизацією)", size=14, bold=True))
    f.append(mtext(870, 170, ["масштаб збережено: ~9 із 10 читань",
                              "лідера взагалі не турбують"], size=13, color=MUTED))
    sx, sw2, sy, sh = 640, 460, 214, 66
    wf = sw2 * 0.901
    f.append(rect(sx, sy, wf, sh, fill=AMBER_T, stroke=AMBER_D, sw=1.8, rx=4))
    f.append(rect(sx + wf, sy, sw2 - wf, sh, fill=GREEN_T, stroke=FIELD, sw=1.8, rx=4))
    f.append(text(sx + wf / 2, sy + sh / 2 + 5, "фоловери · 90.1%", size=15, bold=True))
    f.append(arrow(sx + sw2 - 22, sy + sh + 42, sx + sw2 - 22, sy + sh + 4, color=FIELD, sw=1.8))
    f.append(text(sx + sw2 - 22, sy + sh + 60, "лідер · 9.9%", size=13, color=FIELD, bold=True))

    f.append(fitbox(620, 372, 490, 96,
                    "Той самий потік читань, той самий лаг.\nМаршрутизація прибрала баг "
                    "(346 → 0) і майже не забрала розвантаження: клас «свій свіжий запис» — "
                    "лише сотні перечитувань проти десятків тисяч читань.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "measure-before-after.svg"), W, H, *f)


# ── Фігура: розгортка розміру вікна лагу — баг ↔ навантаження ──────────────────
def fig_lag_window_sweep():
    W, H = 1180, 610
    f = []
    f.append(text(590, 34, "Розмір вікна: замале — баг, завелике — лідер під навантаженням",
                  size=16, bold=True))

    X0, X1 = 175, 1025          # X: вікно 0..3.0 с
    YT, YB = 108, 438
    def px(w):  return X0 + w * (X1 - X0) / 3.0
    def pyv(v): return YB - v * (YB - YT) / 360.0
    def pyp(p): return YB - p * (YB - YT) / 100.0

    # межа найгіршого лага — підпис угорі, окремо від осі X
    f.append(text(px(1.0), 74, "межа: найгірший лаг фоловера = 1.0 с", size=12, bold=True))

    # зони
    f.append(rect(X0, YT, px(1.0) - X0, YB - YT, fill=RED_T, stroke=RED_T, sw=0, rx=0))
    f.append(rect(px(1.0), YT, X1 - px(1.0), YB - YT, fill=AMBER_T, stroke=AMBER_T, sw=0, rx=0))
    f.append(text((X0 + px(1.0)) / 2, YT + 26, "замале → баг протікає", size=12,
                  color=POS, bold=True))
    f.append(text((px(1.0) + X1) / 2, YT + 26, "завелике → зайвий тягар на лідера", size=12,
                  color=AMBER_D, bold=True))

    # осі
    f.append(line(X0, YB, X1, YB, color=INK, sw=1.6))
    f.append(line(X0, YT, X0, YB, color=POS, sw=1.6))
    f.append(line(X1, YT, X1, YB, color=FIELD, sw=1.6))
    f.append(mtext(74, (YT + YB) / 2, ["RYW", "порушено"], size=12, color=POS, bold=True))
    f.append(mtext(1108, (YT + YB) / 2, ["re-read", "→ лідер, %"], size=12, color=FIELD, bold=True))

    for w in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        f.append(line(px(w), YB, px(w), YB + 6, color=INK, sw=1.3))
        f.append(text(px(w), YB + 24, ("%g" % w), size=11, color=MUTED))
    f.append(text((X0 + X1) / 2, YB + 46, "вікно лагу LAG_WINDOW, с", size=13, bold=True))
    for v in (0, 100, 200, 300):
        f.append(text(X0 - 14, pyv(v) + 4, str(v), size=11, color=POS, anchor="end"))
    for p in (0, 50, 100):
        f.append(text(X1 + 14, pyp(p) + 4, str(p), size=11, color=FIELD, anchor="start"))

    f.append(line(px(1.0), YT, px(1.0), YB, color=INK, sw=1.4, dash="6 5"))

    viol = [(0.0, 348), (0.25, 203), (0.5, 100), (1.0, 0), (1.5, 0), (3.0, 0)]
    load = [(0.0, 0), (0.25, 25), (0.5, 50), (1.0, 100), (1.5, 100), (3.0, 100)]

    for (w1, v1), (w2, v2) in zip(viol, viol[1:]):
        f.append(line(px(w1), pyv(v1), px(w2), pyv(v2), color=POS, sw=3))
    for w, v in viol:
        f.append(circle(px(w), pyv(v), 5, fill=RED_T, stroke=POS, sw=2))
        if v > 0:
            f.append(text(px(w) + 22, pyv(v) - 6, str(v), size=11, color=POS, bold=True))
    for (w1, p1), (w2, p2) in zip(load, load[1:]):
        f.append(line(px(w1), pyp(p1), px(w2), pyp(p2), color=FIELD, sw=3))
    for w, p in load:
        f.append(circle(px(w), pyp(p), 5, fill=GREEN_T, stroke=FIELD, sw=2))

    f.append(fitbox(175, 512, 850, 80,
                    "Порушення падають до нуля рівно там, де вікно дотягується до найгіршого лага "
                    "(1.0 с);\nчастка перечитувань, прибитих до лідера, тим часом лізе з 0 до 100%. "
                    "Праве правило: вікно ≥ хвіст (p99) ВИМІРЯНОГО лага з запасом — ставка на хвіст, "
                    "а не на середнє.",
                    size=13, fill=NEUT, stroke=MUTED, color=INK))

    render(os.path.join(OUT, "lag-window-sweep.svg"), W, H, *f)


if __name__ == "__main__":
    fig_measure()
    fig_lag_window_sweep()
    print("OK: proj figures written to", OUT)
