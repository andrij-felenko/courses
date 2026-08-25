# -*- coding: utf-8 -*-
"""Фігури до теми «Одометрія».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── Накопичення дрейфу: оцінка відпливає від правди тим далі, чим довший шлях ──
def fig_drift_accumulation():
    W, H = 760, 470
    f = [text(W / 2, 30, "Похибка одометрії накопичується: що довший шлях, то далі оцінка від правди",
              size=15, bold=True)]

    # координатна область
    ox, oy = 70, 360            # початок осей (низ-ліво)
    span_x = 620                # довжина осі шляху
    # осі
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))          # вісь X (пройдений шлях)
    f.append(line(ox, oy, ox, 70, color=MUTED, sw=1.4))                   # вісь Y (положення)
    f.append(text(ox + span_x, oy + 24, "пройдений шлях →", size=11, color=MUTED, anchor="end"))

    # спільний старт
    f.append(circle(ox, oy, 4, fill=FIELD, stroke=FIELD))
    f.append(text(ox - 6, oy + 18, "старт", size=10, color=MUTED, anchor="middle"))

    # справжній шлях — плавна крива (еталон)
    true_pts = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        yy = oy - 90 - 60 * math.sin(t * 2.3)        # довільний плавний маршрут
        true_pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in true_pts), FIELD))

    # оцінка одометрії — той самий шлях + ПОХИБКА, що росте зі шляхом (дрейф)
    est_pts = []
    for i in range(0, 201):
        t = i / 200.0
        xx, yy = true_pts[i]
        drift = (t ** 1.6) * 120                       # відхилення росте з пройденим шляхом
        est_pts.append((xx, yy - drift))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="7,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in est_pts), POS))

    # «розрив» між лініями у кількох точках — наочно, що щілина розширюється
    for t in (0.28, 0.55, 0.82):
        i = int(t * 200)
        x0, y0t = true_pts[i]
        _, y0e = est_pts[i]
        f.append(line(x0, y0t, x0, y0e, color=MUTED, sw=1.0, dash="2,3"))
    # підпис щілини на правому краї
    xr, yrt = true_pts[-1]
    _, yre = est_pts[-1]
    f.append(line(xr - 0, yrt, xr - 0, yre, color=INK, sw=1.4))
    f.append(text(xr - 8, (yrt + yre) / 2, "помилка", size=10.5, bold=True, color=INK, anchor="end"))
    f.append(text(xr - 8, (yrt + yre) / 2 + 15, "росте", size=10.5, bold=True, color=INK, anchor="end"))

    # легенда
    lx, ly = ox + 30, 96
    f.append(line(lx, ly, lx + 34, ly, color=FIELD, sw=2.8))
    f.append(text(lx + 42, ly + 4, "справжній шлях", size=11.5, color=INK, anchor="start"))
    f.append(line(lx, ly + 22, lx + 34, ly + 22, color=POS, sw=2.8, dash="7,4"))
    f.append(text(lx + 42, ly + 26, "оцінка одометрії (інтеграл руху + похибка)",
                  size=11.5, color=INK, anchor="start"))

    # висновкова рамка
    b, _, _ = textbox(W / 2, 444,
                      "біля старту лінії майже збігаються; кожен крок додає крихту похибки до суми → щілина невпинно ширшає",
                      size=11.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "drift-accumulation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_drift_accumulation()
    print("OK: 1 figure ->", IMG)
