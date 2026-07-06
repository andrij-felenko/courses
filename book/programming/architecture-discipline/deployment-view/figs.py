# -*- coding: utf-8 -*-
"""Фігури до статті «В'ю розгортання і динамічні в'ю»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: те саме логічне → на реальному залізі ─────────────────────────
def fig_static_to_deploy():
    W, H = 760, 470
    p = []
    # ліворуч: статичний контейнер (один прямокутник)
    p.append(text(180, 62, "Що в статичному в'ю", size=15, bold=True, color=MUTED))
    p.append(fitbox(95, 90, 170, 78, "API\n(один контейнер)",
                    size=14, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(fitbox(95, 210, 170, 78, "База даних\n(один контейнер)",
                    size=14, bold=True, fill="#eef2ff", stroke=NEG))
    p.append(arrow(180, 168, 180, 210, color=NEG))

    # стрілка-перехід
    p.append(text(380, 150, "розгортання", size=13, italic=True, color=MUTED))
    p.append(arrow(300, 165, 460, 165, color=INK, sw=2.2))

    # праворуч: інфраструктура
    p.append(text(590, 62, "Що у в'ю розгортання", size=15, bold=True, color=MUTED))
    # рамка «дата-центр» велика
    p.append(rect(470, 78, 270, 372, fill="#f7fdf9", stroke=FIELD, sw=1.6))
    p.append(text(605, 98, "Дата-центр (prod)", size=13, bold=True, color=FIELD))

    # балансувальник
    p.append(fitbox(520, 112, 170, 44, "Балансувальник",
                    size=12, bold=True, fill="#fff6e6", stroke="#b8860b"))
    # три вузли з інстансами API
    xs = [485, 570, 655]
    for i, x in enumerate(xs):
        p.append(rect(x - 5, 176, 78, 66, fill="#eef7f0", stroke=FIELD, sw=1.3))
        p.append(text(x + 34, 194, "вузол", size=10, color=FIELD))
        p.append(fitbox(x, 200, 68, 34, "API",
                        size=11, bold=True, fill="#eef2ff", stroke=NEG))
        p.append(arrow(605, 156, x + 34, 176, color="#b8860b", sw=1.3))
    # база — одна репліка окремо
    p.append(rect(560, 300, 96, 66, fill="#eef7f0", stroke=FIELD, sw=1.3))
    p.append(text(608, 318, "вузол", size=10, color=FIELD))
    p.append(fitbox(566, 324, 84, 34, "БД",
                    size=11, bold=True, fill="#eef2ff", stroke=NEG))
    for x in xs:
        p.append(line(x + 34, 242, 608, 300, color=MUTED, sw=1.0, dash="4 3"))
    p.append(text(605, 392, "три копії API за одним", size=11, color=INK))
    p.append(text(605, 408, "балансувальником — одна", size=11, color=INK))
    p.append(text(605, 424, "«коробка» стала трьома", size=11, color=INK))

    render(os.path.join(IMG, 'static-to-deploy.svg'), W, H, *p)


# ── Фігура 2: статичний бік проти динамічного (нумеровані взаємодії) ─────────
def fig_static_vs_dynamic():
    W, H = 780, 340
    p = []
    p.append(text(W / 2, 30, "Ті самі контейнери — але показано ПОРЯДОК викликів",
                  size=14, bold=True, color=MUTED))
    # чотири вузли рядком, з великими проміжками
    BW, BH, BY = 140, 58, 130
    xs = {"web": 30, "api": 220, "auth": 410, "db": 600}
    labels = {"web": "Веб-\nзастосунок", "api": "API",
              "auth": "Сервіс\nавторизації", "db": "База даних"}
    cx = {k: xs[k] + BW / 2 for k in xs}
    top, bot = BY, BY + BH
    for k in xs:
        p.append(fitbox(xs[k], BY, BW, BH, labels[k], size=12, bold=True,
                        fill="#eef2ff", stroke=NEG))

    def numbadge(mx, my, n):
        return (circle(mx, my, 12, fill="#fdecea", stroke=POS, sw=1.6) +
                text(mx, my + 4, n, size=12, bold=True, color=POS))

    # прямі виклики над рамками зліва направо — стрілки НАД коробками, підписи вище
    def top_arrow(a, b, n, up=42):
        y = BY - up
        p.append(line(cx[a], top, cx[a], y, color=POS, sw=1.6))
        p.append(arrow(cx[a], y, cx[b], y, color=POS, sw=1.8))
        p.append(line(cx[b], y, cx[b], top, color=POS, sw=1.6))
        p.append(numbadge((cx[a] + cx[b]) / 2, y, n))

    # виклики під рамками справа наліво — стрілки ПІД коробками
    def bot_arrow(a, b, n, down=42):
        y = bot + down
        p.append(line(cx[a], bot, cx[a], y, color=POS, sw=1.6))
        p.append(arrow(cx[a], y, cx[b], y, color=POS, sw=1.8))
        p.append(line(cx[b], y, cx[b], bot, color=POS, sw=1.6))
        p.append(numbadge((cx[a] + cx[b]) / 2, y, n))

    top_arrow("web", "api", "1", up=42)      # запит логіну
    top_arrow("api", "auth", "2", up=78)     # перевірка (вище, щоб не збігтися з 1)
    top_arrow("auth", "db", "3", up=42)      # читання
    bot_arrow("api", "web", "4", down=44)    # відповідь назад

    p.append(text(W / 2, 322,
                  "1 запит логіну   2 перевірка облікових даних   "
                  "3 читання з бази   4 відповідь користувачу",
                  size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'static-vs-dynamic.svg'), W, H, *p)


# ── Фігура 3: де стоять ці два в'ю серед решти ──────────────────────────────
def fig_view_map():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 34, "Статична будова — окремо, поведінка й залізо — окремо",
                  size=14, bold=True, color=MUTED))

    # ліва колона — статичні рівні (стос)
    p.append(rect(70, 70, 250, 230, fill="#f7fdf9", stroke=FIELD, sw=1.4))
    p.append(text(195, 92, "Статичні рівні (з чого)", size=12, bold=True, color=FIELD))
    labels = ["Контекст", "Контейнери", "Компоненти", "Код"]
    for i, lb in enumerate(labels):
        y = 108 + i * 46
        p.append(fitbox(100, y, 190, 36, lb, size=12, bold=True,
                        fill="#eef2ff", stroke=NEG))

    # права зона — два доповняльні в'ю
    p.append(text(535, 92, "Доповняльні в'ю", size=12, bold=True, color="#b8860b"))
    p.append(fitbox(430, 112, 210, 66,
                    "Динамічний в'ю\n(як працює в часі)",
                    size=12, bold=True, fill="#fff6e6", stroke="#b8860b"))
    p.append(fitbox(430, 208, 210, 66,
                    "В'ю розгортання\n(на яке залізо лягає)",
                    size=12, bold=True, fill="#fff6e6", stroke="#b8860b"))

    # зв'язки: обидва спираються на «контейнери»
    p.append(arrow(290, 154, 430, 145, color=MUTED, sw=1.4))
    p.append(arrow(290, 154, 430, 241, color=MUTED, sw=1.4))
    p.append(text(360, 128, "ті самі", size=10, italic=True, color=MUTED))
    p.append(text(360, 143, "контейнери", size=10, italic=True, color=MUTED))

    render(os.path.join(IMG, 'view-map.svg'), W, H, *p)


if __name__ == '__main__':
    fig_static_to_deploy()
    fig_static_vs_dynamic()
    fig_view_map()
    print("done")
