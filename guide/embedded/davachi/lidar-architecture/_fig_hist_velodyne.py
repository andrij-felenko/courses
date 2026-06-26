# -*- coding: utf-8 -*-
# Окремий генератор однієї фігури для вставки hist-velodyne-darpa.md.
# Винесено зі спільного figs.py, бо той у цій теці редагують паралельні агенти
# (math-вставка). Виводить img/darpa-timeline.svg тим самим svgkit.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

LASER = "#c0392b"
ECHO  = "#2457d6"
GOOD  = "#27ae60"
DOT   = "#1f8a3b"


# ── Історична нитка: три гонки, що породили обертовий LiDAR ────────────────────
# Від стереокамер (2004) через перший обертовий прототип (2005) до HDL-64E,
# що вінчав 5 із 6 фіналістів Urban Challenge (2007).
def fig_darpa_timeline():
    W, H = 760, 360
    f = []
    f.append(text(W/2, 30, "Як гонка в пустелі породила обертовий LiDAR", size=15, bold=True))

    axy = 118
    x0, x1 = 70, W - 50
    f.append(line(x0, axy, x1, axy, color=MUTED, sw=2))
    f.append(arrow(x1 - 2, axy, x1 + 14, axy, color=MUTED, sw=2))

    # (частка осі, рік, що зробив, деталь, колір, результат гонки)
    miles = [
        (0.10, "2004", "Стереокамери",            "вантажівка Голла\nбачить погано",  LASER,      "1-ша гонка:\nніхто не фінішує"),
        (0.46, "2005", "Перший обертовий\nприлад", "Голл крутить\nлазер на даху",       "#8e44ad",  "Голл не дійшов;\nвиграв Stanley (SICK)"),
        (0.84, "2007", "HDL-64E",                  "64 промені, 360°,\n~$75 000",       DOT,        "5 із 6 фіналістів,\nразом із BOSS (CMU)"),
    ]
    for fr, yr, head, sub, col, res in miles:
        x = x0 + fr * (x1 - x0 - 10)
        f.append(circle(x, axy, 7, fill=BG, stroke=col, sw=2.6))
        f.append(text(x, axy - 16, yr, size=14, bold=True, color=col))
        f.append(fitbox(x - 92, axy + 18, 184, 44, head, size=12, bold=True,
                        fill="#f4f6f8", stroke=col, sw=2, color=col))
        f.append(fitbox(x - 92, axy + 66, 184, 40, sub, size=10, color=INK,
                        fill=BG, stroke=MUTED, sw=1.1))
        win = "5 із 6" in res
        f.append(fitbox(x - 92, axy + 112, 184, 42, res, size=10, color=INK,
                        fill=("#eef7ee" if win else "#fff5f5"),
                        stroke=(GOOD if win else MUTED), sw=1.2))

    b, w, h = textbox(W/2, H - 22,
                      "три цикли гонки — і «обертовий бочонок» став синонімом «справжнього» LiDAR",
                      size=12, color=INK, fill=FILL, stroke=LINE)
    f.append(b)
    return render(os.path.join(OUT, "darpa-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_darpa_timeline()
    print("OK: darpa-timeline.svg")
