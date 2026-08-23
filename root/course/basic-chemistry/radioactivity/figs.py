# -*- coding: utf-8 -*-
"""Фігури до теми «Радіоактивність» (book/chemistry/radiochemistry/radioactivity)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: три види випромінювання і перепони, які їх спиняють ──────────
def fig_rays_shields():
    W, H = 960, 460
    frags = [text(480, 34, "Три види випромінювання і перепони, які їх спиняють",
                  size=17, bold=True)]

    rows = [
        ("альфа", "два протони й два нейтрони — важкий уламок ядра", "аркуш паперу",
         POS, 60, "паперу", 210),
        ("бета", "швидкий електрон із розпаду нейтрона", "кілька мм алюмінію",
         NEG, 60, "алюмінію", 460),
        ("гама", "промінь, а не частинка — зайва енергія збудженого ядра", "товстий свинець / бетон",
         FIELD, 60, "свинцю", 760),
    ]

    x_src = 60
    y_rows = [130, 260, 390]
    row_h = 96

    for (name, desc, stop_label, color, xs, stop_word, stop_x), y in zip(rows, y_rows):
        # джерело
        frags.append(circle(x_src, y, 20, fill="#fff", stroke=color, sw=3))
        frags.append(text(x_src, y + 5, "•", size=22, bold=True, color=color))
        frags.append(text(x_src, y - 34, name, size=15, bold=True, color=color))

        # перепона (позиція й товщина різні для наочності пробивної сили)
        barrier_x = {"альфа": 210, "бета": 460, "гама": 760}[name]
        barrier_w = {"альфа": 16, "бета": 34, "гама": 70}[name]
        frags.append(rect(barrier_x, y - 42, barrier_w, 84, fill="#e9edf2", stroke=MUTED, sw=1.5, rx=2))
        frags.append(text(barrier_x + barrier_w / 2.0, y + 58, stop_word, size=12, color=MUTED))

        # промінь: суцільна лінія до перепони, пунктир (застряг) далі не йде для альфа/бета,
        # для гама лінія проходить наскрізь до правого краю
        frags.append(line(x_src + 22, y, barrier_x, y, color=color, sw=3))
        if name == "гама":
            frags.append(line(barrier_x + barrier_w, y, 900, y, color=color, sw=3))
            frags.append(text(barrier_x + barrier_w + 14, y - 14, "проходить далі за всіх",
                              size=12, anchor="start", color=MUTED))
        else:
            frags.append(text(barrier_x + barrier_w + 14, y - 14, "застрягає тут", size=12, color=MUTED))

        frags.append(text(x_src, y + 40, desc, size=12, anchor="start", color=MUTED))

    frags.append(mtext(480, 436, [
        "порядок назв (альфа, бета, гама — перші літери грецької абетки) повторює порядок пробивної сили:",
        "альфа найважча й найповільніша, гама — це вже не частинка, а найпроникніше випромінювання",
    ], size=13, color=MUTED))

    render(os.path.join(IMG, 'rays-shields.svg'), W, H, *frags)


# ── Фігура 2: період напіврозпаду — кожні 8 днів удвічі менше ──────────────
def fig_half_life():
    W, H = 900, 440
    frags = [text(450, 34, "Йод-131: кожні 8 днів кількість хистких ядер зменшується вдвічі",
                  size=17, bold=True)]

    steps = [
        ("початок", "0 днів", 1000000),
        ("через 8 днів", "8 днів", 500000),
        ("через 16 днів", "16 днів", 250000),
        ("через 24 дні", "24 дні", 125000),
        ("через 32 дні", "32 дні", 62500),
    ]

    x0, x1 = 90, 850
    y_base = 360
    max_h = 250
    n = len(steps)
    slot = (x1 - x0) / float(n)
    bar_w = slot * 0.5

    frags.append(line(x0 - 10, y_base, x1 + 10, y_base, color=INK, sw=2))

    max_val = steps[0][2]
    for i, (label, day_label, val) in enumerate(steps):
        cx = x0 + slot * (i + 0.5)
        h = max(6, max_h * (val / float(max_val)))
        y = y_base - h
        frags.append(rect(cx - bar_w / 2.0, y, bar_w, h, fill="#e8f7ee", stroke=FIELD, sw=2, rx=3))
        frags.append(text(cx, y - 12, "{:,}".format(val).replace(",", " "), size=13, bold=True))
        frags.append(text(cx, y_base + 22, day_label, size=13, color=MUTED))

    for i in range(n - 1):
        cx1 = x0 + slot * (i + 0.5)
        cx2 = x0 + slot * (i + 1.5)
        h1 = max(6, max_h * (steps[i][2] / float(max_val)))
        y1 = y_base - h1 - 20
        frags.append(arrow(cx1 + bar_w / 2.0 + 6, y1, cx2 - bar_w / 2.0 - 6, y1, color=MUTED))
        frags.append(text((cx1 + cx2) / 2.0, y1 - 8, "½", size=14, bold=True, color=MUTED))

    frags.append(mtext(450, 410, [
        "за кожні 8 днів (період напіврозпаду Йоду-131) зникає рівно половина ядер, що лишалися —",
        "тому за місяць (32 дні, чотири періоди) від мільйона лишається лише шістнадцята частина",
    ], size=13, color=MUTED))

    render(os.path.join(IMG, 'half-life.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_rays_shields()
    fig_half_life()
    print("ok")
