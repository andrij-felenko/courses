# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір контролера і частоти комутації».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Що всередині power-модуля: один корпус проти розсипу деталей ─────────────
def fig_inside_module():
    W, H = 760, 380
    f = [text(W / 2, 30, "Power-модуль: усе живлення зведено в один корпус",
              size=16, bold=True)]

    # ── ЛІВОРУЧ: дискретно — багато окремих деталей на платі ──
    f.append(text(195, 64, "дискретно: купа деталей", size=14, bold=True, color=MUTED))
    f.append(rect(40, 80, 310, 250, fill="#fbfcfd", stroke=LINE, sw=1.4))
    # розкидані компоненти
    spots = [
        (95, 120, "контролер"), (235, 120, "верх.\nключ"),
        (95, 185, "котушка"), (235, 185, "нижн.\nключ"),
        (95, 250, "Cвх"), (165, 250, "Cвих"),
        (245, 250, "Rдоб."), (300, 185, "Rзвор."),
    ]
    for x, y, lab in spots:
        f.append(fitbox(x - 42, y - 22, 84, 44, lab, size=11, fill=FILL))
    # павутиння доріжок між ними
    for a, b in [((137, 120), (193, 120)), ((95, 142), (95, 163)),
                 ((137, 185), (193, 185)), ((95, 207), (95, 228)),
                 ((137, 250), (123, 250)), ((207, 250), (203, 250)),
                 ((235, 142), (235, 163)), ((277, 185), (258, 185))]:
        f.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(195, 318, "розводити, добирати, паяти — все вручну",
                  size=11, color=MUTED))

    # стрілка-перехід
    f.append(arrow(360, 200, 405, 200, color=FIELD, sw=2.4))

    # ── ПРАВОРУЧ: модуль — один корпус ──
    f.append(text(575, 64, "модуль: один корпус", size=14, bold=True, color=FIELD))
    f.append(rect(420, 80, 300, 250, fill="#f1faf4", stroke=FIELD, sw=2.2))
    # вміст усередині корпусу
    f.append(fitbox(445, 110, 120, 40, "контролер", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(575, 110, 120, 40, "обидва\nключі", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(445, 165, 250, 46, "котушка (усередині корпусу)",
                    size=12, fill="#eaf4ff", stroke=NEG))
    f.append(fitbox(445, 225, 120, 38, "Cвх", size=12, fill=BG, stroke=LINE))
    f.append(fitbox(575, 225, 120, 38, "звор. зв'язок", size=11, fill=BG, stroke=LINE))
    # ніжки назовні
    pins = ["VIN", "EN", "FB", "VOUT", "PG", "GND"]
    px = 440
    for p in pins:
        f.append(rect(px, 332, 6, 14, fill=INK, stroke=INK, sw=1))
        f.append(text(px + 3, 360, p, size=10, color=INK))
        px += 47
    f.append(text(570, 300, "лишилось підвести живлення й 2-3 деталі",
                  size=11, color=FIELD))

    render(os.path.join(IMG, "inside-module.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside_module()
    print("OK: figs written to", IMG)
