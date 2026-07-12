# -*- coding: utf-8 -*-
# Фігура для історичної вставки hist-seam-origin.md.
# Окремий файл, щоб не чіпати figs.py готової статті-власника.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_history():
    """Вертикальна стрічка часу: від JUnit до Legacy Seam."""
    W, H = 860, 640
    frags = []

    ax = 150                       # вісь
    y0, dy = 108, 112
    nodes = [
        ("1997", "JUnit",
         ["Кент Бек і Еріх Гамма пишуть юніт-тест",
          "у літаку до OOPSLA — тестування виходить"], INK, False),
        ("1999", "CppUnit",
         ["Фезерс переносить JUnit у C++ —",
          "мову, що чинить опір тестам"], INK, False),
        ("2002", "Стаття Object Mentor",
         ["названо «дилему легасі-коду»:",
          "щоб тестувати — міняй, щоб міняти — тестуй"], INK, False),
        ("2004", "Книжка: «Модель шва»",
         ["три роди швів за конвеєром збірки:",
          "препроцесорний · лінк · об'єктний"], POS, True),
        ("2024", "Фаулер, «Legacy Seam»",
         ["шов поза тестами: зонди спостережності,",
          "витиснення старого новим"], FIELD, False),
    ]

    ys = [y0 + i * dy for i in range(len(nodes))]
    frags.append(line(ax, ys[0], ax, ys[-1], color=MUTED, sw=2))

    for (yr, title, desc, col, hot), y in zip(nodes, ys):
        # вузол
        if hot:
            frags.append(circle(ax, y, 12, fill="#fdecea", stroke=POS, sw=2.6))
        else:
            frags.append(circle(ax, y, 9, fill=BG, stroke=col, sw=2.2))
        # рік — ліворуч від осі
        frags.append(text(ax - 34, y + 6, yr, size=19, bold=True,
                          color=col, anchor="end"))
        # подія — праворуч від осі
        frags.append(text(ax + 30, y - 6, title, size=15, bold=True,
                          color=INK, anchor="start"))
        frags.append(mtext(ax + 30, y + 15, desc, size=13, color=MUTED,
                           anchor="start", lh=1.32))

    render(os.path.join(OUT, 'seam-history.svg'), W, H, *frags,
           title="Від JUnit до Legacy Seam: як народився шов")


if __name__ == '__main__':
    fig_history()
    print("figure written to", OUT)
