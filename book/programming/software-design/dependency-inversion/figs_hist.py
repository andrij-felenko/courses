# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Хронологія народження DIP: від метрик залежностей до літери D у SOLID ─────
def fig_dip_timeline():
    W, H = 1080, 470
    frags = []

    # горизонтальна вісь часу
    axis_y = 250
    x0, x1 = 90, W - 60
    frags.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    frags.append(arrow(x1 - 2, axis_y, x1 + 24, axis_y, color=INK, sw=2.4))

    # віхи: (частка_осі 0..1, рік, підпис, вгору?, колір рамки)
    milestones = [
        (0.00, "1994", "Метрики якості:\nвиміряти залежності", True,  MUTED),
        (0.24, "1996", "The C++ Report:\nстаття про DIP",       False, INK),
        (0.60, "2000", "«Design Principles…»:\nмова про rot",   True,  MUTED),
        (0.90, "~2004", "Фізерс зшиває\nп'ять правил у SOLID",  False, FIELD),
    ]

    for frac, year, label, up, col in milestones:
        x = x0 + frac * (x1 - x0 - 30)
        # засічка на осі
        frags.append(line(x, axis_y - 9, x, axis_y + 9, color=INK, sw=2.2))
        # рік — біля осі, з протилежного боку від картки
        if up:
            frags.append(text(x, axis_y + 26, year, size=14, bold=True, color=INK))
            by = axis_y - 78            # картка вгорі
        else:
            frags.append(text(x, axis_y - 18, year, size=14, bold=True, color=INK))
            by = axis_y + 96            # картка внизу

        box, bw, bh = textbox(x, by, label, size=12.5, pad=11,
                              fill="#ffffff", stroke=col, sw=1.9, color=INK)
        frags.append(box)
        # тонка ніжка від засічки до картки
        if up:
            frags.append(line(x, axis_y - 10, x, by + bh / 2, color=col, sw=1.2, dash="4,4"))
        else:
            frags.append(line(x, axis_y + 10, x, by - bh / 2, color=col, sw=1.2, dash="4,4"))

    frags.append(text(x0, axis_y - 118,
                      "Річ з'явилася першою — коротке ім'я «SOLID» дісталося їй аж за вісім років",
                      size=13, bold=True, anchor="start", color=INK))

    render(os.path.join(IMG, 'dip-timeline.svg'), W, H, *frags,
           title="Народження DIP: принцип випередив свій акронім")


if __name__ == "__main__":
    fig_dip_timeline()
    print("figures written to", IMG)
