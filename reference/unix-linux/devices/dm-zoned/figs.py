# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
GRAY_FILL = "#eef1f4"


# ── Перенаправлення запитів у dm-zoned ──────────────────────────────────────
def fig_arch():
    W, H = 1080, 460
    p = []

    p.append(text(40, 28, "Кожен запит dm-zoned спрямовує за характером запису",
                  size=16, anchor="start", bold=True))

    p.append(fitbox(40, 190, 200, 80, "Файлова система\next4 / XFS",
                    size=14, fill=GRAY_FILL, stroke=LINE))

    p.append(fitbox(310, 175, 190, 110, "dm-zoned\nтаблиця\nвідповідностей",
                    size=14, fill=GRAY_FILL, stroke=INK, sw=1.8, bold=True))

    p.append(arrow(240, 230, 305, 230))

    p.append(fitbox(650, 50, 300, 90, "Буферні зони\n(Conventional)",
                    size=14, fill=BLUE_FILL, stroke=NEG, sw=1.8))
    p.append(fitbox(650, 320, 300, 90, "Зони даних\n(Sequential Write Required)",
                    size=14, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    p.append(arrow(500, 200, 645, 100, color=NEG))
    p.append(text(560, 128, "випадковий запис", size=13, color=NEG))

    p.append(arrow(500, 260, 645, 330, color=FIELD))
    p.append(text(560, 322, "послідовний запис", size=13, color=FIELD))

    p.append(arrow(800, 145, 800, 315, color=MUTED, sw=2))
    p.append(mtext(820, 214, ["Zone Reclaim:", "валідні дані переносяться",
                              "буферна зона очищується"],
                   size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'dm-zoned-arch.svg'), W, H, *p)


if __name__ == "__main__":
    fig_arch()
