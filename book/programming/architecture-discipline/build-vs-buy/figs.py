# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def spectrum():
    W, H = 860, 380
    parts = []

    # Головна вісь
    ax_y = 120
    x0, x1 = 90, W - 90
    parts.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.2))
    parts.append(arrow(x1 - 2, ax_y, x1 + 2, ax_y, color=INK, sw=2.2))
    parts.append(arrow(x0 + 2, ax_y, x0 - 2, ax_y, color=INK, sw=2.2))

    # Полюси осі — підписи стоять НАД віссю, по краях, поза рамками варіантів
    parts.append(text(x0 + 4, ax_y - 58, "чуже · швидко", size=13, color=MUTED, anchor="start", italic=True))
    parts.append(text(x1 - 4, ax_y - 58, "своє · під контролем", size=13, color=MUTED, anchor="end", italic=True))

    # Чотири варіанти як рамки на осі (від «чужого» ліворуч до «свого» праворуч)
    labels = [
        ("adopt\n(відкрите)", FIELD),
        ("SaaS\n(оренда)",    FIELD),
        ("buy\n(ліцензія)",   NEG),
        ("build\n(своє)",     POS),
    ]
    n = len(labels)
    span = x1 - x0
    xs = [x0 + span * (i + 0.5) / n for i in range(n)]
    for cx, (lab, col) in zip(xs, labels):
        # маркер на осі
        parts.append(circle(cx, ax_y, 5, fill=BG, stroke=col, sw=2.2))
        # рамка з підписом під маркером
        body, bw, bh = textbox(cx, ax_y + 46, lab, size=14, pad=9, stroke=col, sw=1.8, min_w=110)
        parts.append(body)

    # Дві протилежні стрілки-виміри під варіантами — обидві ростуть управо
    lane_y1 = 250
    lane_y2 = 300
    lx0, lx1 = xs[0], xs[-1]
    parts.append(arrow(lx0, lane_y1, lx1, lane_y1, color=POS, sw=2))
    parts.append(text((lx0 + lx1) / 2, lane_y1 - 12, "контроль над рішенням росте →",
                      size=13, color=POS, bold=True))
    parts.append(arrow(lx0, lane_y2, lx1, lane_y2, color=NEG, sw=2))
    parts.append(text((lx0 + lx1) / 2, lane_y2 - 12, "тягар супроводу й оновлень росте →",
                      size=13, color=NEG, bold=True))

    # Нижній підсумок-рядок
    parts.append(text(W / 2, 345, "більше свого = більше влади, але й більше зобов'язань",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'spectrum.svg'), W, H, *parts)


def timeline():
    # Дві нитки думки, що сходяться праворуч у точку «рішення build vs buy».
    W, H = 1040, 560
    parts = []

    x_left = 70
    x_join = 900          # x, де нитки сходяться
    y_top = 130           # нитка «оренда-як-послуга»
    y_bot = 400           # нитка «ядро / фон»

    # Заголовки ниток (ліворуч, поза вузлами)
    parts.append(text(x_left, y_top - 74, "оренда-як-послуга", size=15, color=POS,
                      anchor="start", bold=True))
    parts.append(text(x_left, y_bot - 74, "поділ на ядро та фон", size=15, color=FIELD,
                      anchor="start", bold=True))

    # ── Верхня нитка: вузли з роками ──
    top_nodes = [
        (0.02, "1961", "Маккарті:\nобчислення —\nкомунальна послуга"),
        (0.24, "1960-70-ті", "поділ часу:\nоренда\nмашинного часу"),
        (0.50, "кінець 1990-х", "хвиля ASP\n(«apps on tap»)"),
        (0.72, "лют. 2001", "SIIA-довідник:\nназва\n«software\nas a service»"),
        (0.93, "бер. 2005", "Кеніг:\nабревіатура\n«SaaS»"),
    ]
    # ── Нижня нитка: один вузол ──
    bot_nodes = [
        (0.50, "2000", "Мур, «Living on\nthe Fault Line»:\nядро vs фон"),
    ]

    span = x_join - x_left

    def draw_thread(nodes, y, col):
        # базова лінія нитки
        parts.append(line(x_left, y, x_join, y, color=col, sw=2.2))
        xs = []
        for frac, yr, lab in nodes:
            cx = x_left + span * frac
            xs.append(cx)
            # маркер року на лінії
            parts.append(circle(cx, y, 5.5, fill=BG, stroke=col, sw=2.2))
            # рік — над лінією, окремо, невеликим кеглем
            parts.append(text(cx, y - 16, yr, size=12, color=INK, bold=True))
            # підпис-рамка — під лінією, з запасом ширини
            body, bw, bh = textbox(cx, y + 58, lab, size=12, pad=8,
                                   stroke=col, sw=1.5, min_w=132)
            parts.append(body)
        return xs

    top_xs = draw_thread(top_nodes, y_top, POS)
    bot_xs = draw_thread(bot_nodes, y_bot, FIELD)

    # ── Точка сходження праворуч ──
    y_mid = (y_top + y_bot) / 2
    cx_join = x_join + 60
    # обидві нитки ведуть у спільний вузол
    parts.append(line(x_join, y_top, cx_join, y_mid, color=MUTED, sw=1.8))
    parts.append(line(x_join, y_bot, cx_join, y_mid, color=MUTED, sw=1.8))
    body, bw, bh = textbox(cx_join, y_mid, "рішення\nbuild vs buy", size=14, pad=11,
                           stroke=INK, sw=2, min_w=120, fill=FILL)
    parts.append(body)

    # Підсумок унизу
    parts.append(text(W / 2, H - 22,
                      "ядро (з 2000) каже ДЕ перевага · оренда (з 1961) робить ДЕШЕВИМ усе поза нею",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'timeline.svg'), W, H, *parts)


if __name__ == '__main__':
    spectrum()
    timeline()
    print('done')
