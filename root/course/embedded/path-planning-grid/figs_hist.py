# -*- coding: utf-8 -*-
"""Фігури для вставки hist-a-star-shakey.md — окремий генератор, щоб НЕ чіпати figs.py теми.
Вивід у ./img/ (той самий, що й у figs.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def timeline():
    """Смуга часу проєкту Shakey у SRI: одна потреба — цілий кущ ідей."""
    W, H = 860, 430
    ax_y = 150                      # рівень осі часу
    x0, x1 = 70, 790                # ліва/права межі осі
    t0, t1 = 1964, 1973             # роки-межі

    def X(year):
        return x0 + (year - t0) / (t1 - t0) * (x1 - x0)

    frags = []

    # Смуга тривалості проєкту (1966–1972) — вона ж «замінює» вісь на своєму відрізку.
    bx0, bx1 = X(1966), X(1972)

    # Вісь часу зі стрілкою — двома відрізками ПОВЗ смугу, щоб лінія не різала її напис.
    frags.append(line(x0 - 10, ax_y, bx0, ax_y, color=INK, sw=2))
    frags.append(arrow(bx1, ax_y, x1 + 20, ax_y, color=INK, sw=2))

    # Позначки років під віссю.
    for yr in range(1964, 1974):
        xx = X(yr)
        frags.append(line(xx, ax_y - 5, xx, ax_y + 5, color=MUTED, sw=1.4))
        frags.append(text(xx, ax_y + 22, str(yr), size=12, color=MUTED))

    frags.append(rect(bx0, ax_y - 13, bx1 - bx0, 26, fill="#eaf3ec", stroke=FIELD, sw=1.6, rx=6))
    frags.append(text((bx0 + bx1) / 2, ax_y + 4, "проєкт Shakey у SRI", size=12,
                      color="#1e7a44", bold=True))

    # Події: (рік, підпис, вгору?, колір рамки).
    events = [
        (1964, ["квітень 1964:", "пропозиція SRI", "до ARPA"], True, LINE),
        (1966, ["1966:", "старт проєкту"], False, LINE),
        (1968, ["1968:", "A* — Гарт,", "Нільссон, Рафаель"], True, POS),
        (1971, ["1971:", "планувальник", "STRIPS"], False, LINE),
        (1972, ["1972:", "перетворення Гафа", "(Дуда і Гарт)"], True, NEG),
    ]
    for yr, lines, up, col in events:
        xx = X(yr)
        # Виноска-крапка на осі.
        frags.append(circle(xx, ax_y, 5, fill=col, stroke=col, sw=1))
        box, bw, bh = textbox(0, 0, "\n".join(lines), size=12, pad=8,
                              stroke=col, fill="#ffffff")
        if up:
            cy = ax_y - 40 - bh / 2
            leg_y0, leg_y1 = ax_y - 5, cy + bh / 2
        else:
            cy = ax_y + 66 + bh / 2
            # ніжка донизу СТАРТУЄ нижче підпису року (≈ ax_y+22), щоб не різати його
            leg_y0, leg_y1 = ax_y + 32, cy - bh / 2
        # Тонка ніжка від осі до рамки.
        frags.append(line(xx, leg_y0, xx, leg_y1, color=col, sw=1.2, dash="3,3"))
        # Рамку зсуваємо, тримаючи в межах полотна.
        cx = min(max(xx, x0 + bw / 2), x1 - bw / 2 + 10)
        frags.append(line(xx, leg_y1, cx, cy + (bh / 2 if up else -bh / 2), color=col, sw=1.2, dash="3,3")
                     if abs(cx - xx) > 1 else "")
        moved, _, _ = textbox(cx, cy, "\n".join(lines), size=12, pad=8,
                              stroke=col, fill="#ffffff")
        frags.append(moved)

    # Підпис-теза внизу.
    thesis, tw, th = textbox(W / 2, H - 40,
                             "Один робот, що мусив сам знайти дорогу, → цілий кущ методів",
                             size=13, pad=10, stroke=FIELD, fill="#eaf3ec", bold=True)
    frags.append(thesis)

    render(os.path.join(IMG, "shakey-timeline.svg"), W, H, *frags,
           title="Куди A* пустив коріння: смуга часу проєкту Shakey")


if __name__ == "__main__":
    timeline()
    print("ok: shakey-timeline.svg")
