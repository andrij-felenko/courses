# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')

# ── Фігура: одна модель → три проєкції (в'ю) ──────────────────────────────────
# Показуємо, що логічний / процесний / розгортання — не три різні системи,
# а три фільтри над однією моделлю; той самий елемент (prices) видно в кожному
# під своїм кутом. Три колонки з ЗАПАСОМ, підписи стоять поза чужими лініями.
def fig_projections():
    W, H = 860, 470
    parts = []

    # ── спільна модель угорі (джерело правди) ──
    mx, my, mw, mh = W / 2 - 150, 66, 300, 58
    parts.append(rect(mx, my, mw, mh, fill="#fff7e6", stroke="#b8860b", sw=2))
    parts.append(text(W / 2, my + 23, "Одна модель системи", size=15, bold=True, color=INK))
    parts.append(text(W / 2, my + 44, "усі елементи й зв'язки разом", size=12.5, color=MUTED))

    # ── три колонки-проєкції ──
    colw = 236
    gap = (W - 3 * colw) / 4
    top = 196          # верх рамок колонок
    boxh = 236
    xs = [gap + i * (colw + gap) for i in range(3)]

    titles = [
        ("Логічний в'ю", "фільтр: залежності", INK),
        ("Процесний в'ю", "фільтр: виклики в часі", NEG),
        ("В'ю розгортання", "фільтр: вузли", FIELD),
    ]

    # стрілки від моделі до кожної колонки — ведемо повз написи, у верх колонки
    for i, x in enumerate(xs):
        cx = x + colw / 2
        parts.append(line(W / 2, my + mh, cx, top - 8, color="#c4c9d0", sw=1.6, dash="5,4"))

    # вміст кожної проєкції: два вузли-елементи + підпис зв'язку між ними.
    # prices присутній у ВСІХ трьох (обведений кольором проєкції) — те саме,
    # видно під різним кутом.
    contents = [
        # (верхній вузол, нижній вузол, підпис зв'язку, підпис-суть під колонкою)
        ("orders", "prices", "залежить від", "стійка залежність"),
        ("orders", "prices", "викликає →", "подія в часі"),
        ("node-eu", "prices", "стоїть на", "prices — на node-us!"),
    ]

    for i, x in enumerate(xs):
        title, sub, col = titles[i]
        # рамка колонки
        parts.append(rect(x, top, colw, boxh, fill="#f4f6f8", stroke=LINE, sw=1.5))
        parts.append(text(x + colw / 2, top + 24, title, size=14.5, bold=True, color=col))
        parts.append(text(x + colw / 2, top + 44, sub, size=12, color=MUTED))

        top_node, bot_node, edge_lbl, essence = contents[i]

        # два вузли всередині колонки, з великим вертикальним запасом
        n_y1 = top + 84
        n_y2 = top + 168
        cx = x + colw / 2

        # верхній вузол
        b1, w1, h1 = textbox(cx, n_y1, top_node, size=13.5, bold=True,
                             fill=BG, stroke=MUTED, sw=1.6, pad=11, min_w=96)
        # нижній вузол — prices скрізь; у розгортанні нижній = prices теж
        hot = (bot_node == "prices")
        b2, w2, h2 = textbox(cx, n_y2, bot_node, size=13.5, bold=True,
                             fill=("#eaf7ee" if col == FIELD and hot else BG),
                             stroke=(col if hot else MUTED),
                             sw=(2.2 if hot else 1.6), pad=11, min_w=96)

        # стрілка між вузлами (зверху вниз), збоку від центру — щоб підпис став поруч, не на лінії
        ax = cx - 6
        parts.append(arrow(ax, n_y1 + h1 / 2, ax, n_y2 - h2 / 2, color=col, sw=1.8))
        # підпис зв'язку — праворуч від стрілки, поза лінією й вузлами
        parts.append(text(cx + 30, (n_y1 + n_y2) / 2 + 4, edge_lbl, size=12, color=col, anchor="start"))

        parts.append(b1)
        parts.append(b2)

        # підпис-суть під колонкою, у власному рядку з запасом
        parts.append(text(cx, top + boxh + 22, essence, size=12, italic=True,
                          color=(POS if col == FIELD and "node-us" in essence else MUTED)))

    parts.append(text(W / 2, 34, "Три в'ю — три проєкції однієї моделі", size=17, bold=True, color=INK))
    render(os.path.join(IMG, 'projections.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_projections()
    print("figures written")
