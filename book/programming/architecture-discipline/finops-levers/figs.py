# -*- coding: utf-8 -*-
"""Фігури до статті «FinOps-важелі».
Вивід у ./img/. Імпортує svgkit зі scripts/ (не переписує)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_families():
    """Дві сім'ї важелів: ціна за одиницю проти кількості одиниць."""
    W, H = 860, 470
    frags = []
    frags.append(text(W / 2, 34, "Рахунок = ціна за одиницю × кількість одиниць",
                      size=17, bold=True))

    # Роздільна вертикаль
    frags.append(line(W / 2, 58, W / 2, H - 30, color=MUTED, sw=1.2, dash="6 6"))

    # Заголовки колонок
    frags.append(text(215, 82, "Важелі ЦІНИ", size=16, bold=True, color=NEG))
    frags.append(text(215, 102, "дешевша одиниця, кількість та сама", size=12, color=MUTED))
    frags.append(text(645, 82, "Важелі КІЛЬКОСТІ", size=16, bold=True, color=FIELD))
    frags.append(text(645, 102, "менше одиниць, ціна кожної та сама", size=12, color=MUTED))

    def lever(cx, y, name, note, accent):
        out = []
        w = 330
        x = cx - w / 2
        out.append(rect(x, y, w, 54, fill=FILL, stroke=accent, sw=1.8))
        out.append(text(x + 16, y + 23, name, size=14, bold=True, anchor="start"))
        out.append(text(x + 16, y + 42, note, size=11.5, color=MUTED, anchor="start"))
        return out

    ly0 = 122
    gap = 66
    left = [
        ("Обіцянка наперед", "рік/три роки → до −72 %"),
        ("Спот", "право забрати → −70..90 %"),
        ("Правильна полиця сховища", "рідко читаєш → холодна, дешевша"),
    ]
    right = [
        ("Масштабування до нуля", "гасне в затишші, платиш за спожите"),
        ("Right-sizing", "розмір під реальний апетит"),
        ("Прибирання простою", "вимкнути забуте й непотрібне"),
    ]
    for i, (n, note) in enumerate(left):
        frags += lever(215, ly0 + i * gap, n, note, NEG)
    for i, (n, note) in enumerate(right):
        frags += lever(645, ly0 + i * gap, n, note, FIELD)

    # Підписи-руки внизу колонок
    b1, w1, h1 = textbox(215, ly0 + 3 * gap + 18, "рука фінансів і адміністратора",
                         size=12, fill="#eaf0fd", stroke=NEG, sw=1.4)
    frags.append(b1)
    b2, w2, h2 = textbox(645, ly0 + 3 * gap + 18, "рука архітектора: рішення про форму",
                         size=12, fill="#eafaf1", stroke=FIELD, sw=1.4)
    frags.append(b2)

    render(os.path.join(IMG, 'two-families.svg'), W, H, *frags)


def fig_scale_to_demand():
    """Той самий профіль попиту: стеля під пік (порожнє) vs слідування за попитом."""
    W, H = 820, 588
    frags = []
    frags.append(text(W / 2, 34, "Той самий добовий попит — два рахунки", size=17, bold=True))

    # Крива попиту за 24 години (нормована 0..1): нічний провал, ранковий і денний піки
    demand = [0.10, 0.08, 0.07, 0.09, 0.15, 0.35, 0.62, 0.85,
              0.78, 0.70, 0.66, 0.72, 0.80, 0.74, 0.60, 0.55,
              0.68, 0.58, 0.40, 0.30, 0.24, 0.20, 0.15, 0.12]
    peak = max(demand)

    def panel(ox, oy, pw, ph, title, follow):
        out = []
        out.append(text(ox + pw / 2, oy - 10, title, size=14, bold=True))
        base_y = oy + ph - 34
        axis_x = ox + 40
        top_y = oy + 16
        plot_w = pw - 60
        plot_h = base_y - top_y
        # осі
        out.append(line(axis_x, top_y, axis_x, base_y, color=LINE, sw=1.4))
        out.append(line(axis_x, base_y, ox + pw - 16, base_y, color=LINE, sw=1.4))
        out.append(text(axis_x - 8, top_y + 4, "потужність", size=10.5, color=MUTED, anchor="end"))
        out.append(text(ox + pw / 2, base_y + 24, "час доби (24 год)", size=11, color=MUTED))

        n = len(demand)
        dx = plot_w / (n - 1)

        def px(i):
            return axis_x + i * dx

        def py(v):
            return base_y - v * plot_h

        ceil_y = py(peak)

        if not follow:
            # Стеля під пік: заштрихована площа МІЖ стелею і кривою = порожнє
            # багатокутник: уздовж стелі вперед, уздовж кривої назад
            pts = ["%.1f,%.1f" % (px(0), ceil_y)]
            pts.append("%.1f,%.1f" % (px(n - 1), ceil_y))
            for i in range(n - 1, -1, -1):
                pts.append("%.1f,%.1f" % (px(i), py(demand[i])))
            out.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.9"/>'
                       % " ".join(pts))
            # лінія стелі
            out.append(line(px(0), ceil_y, px(n - 1), ceil_y, color=POS, sw=2.2))
            out.append(text(px(n - 1) - 4, ceil_y - 8, "стеля під пік", size=11,
                            color=POS, bold=True, anchor="end"))
        else:
            # Слідування за попитом: заливка ПІД кривою = оплачене
            pts = ["%.1f,%.1f" % (px(0), base_y)]
            for i in range(n):
                pts.append("%.1f,%.1f" % (px(i), py(demand[i])))
            pts.append("%.1f,%.1f" % (px(n - 1), base_y))
            out.append('<polygon points="%s" fill="#eafaf1" stroke="none"/>'
                       % " ".join(pts))

        # крива попиту поверх усього
        poly = " ".join("%.1f,%.1f" % (px(i), py(demand[i])) for i in range(n))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                   % (poly, INK))
        return out, base_y

    p1, _ = panel(70, 96, 680, 170, "Стеля тримають під пік усі 24 год", follow=False)
    frags += p1
    b1, w1, h1 = textbox(410, 300, "заштриховане — оплачене порожнє (над реальним попитом)",
                         size=12, fill="#fdecea", stroke=POS, sw=1.4)
    frags.append(b1)

    p2, _ = panel(70, 372, 680, 170, "Потужність слідує за попитом (гасне в затишші)", follow=True)
    frags += p2
    b2, w2, h2 = textbox(410, 552, "платиться лише площа під кривою попиту",
                         size=12, fill="#eafaf1", stroke=FIELD, sw=1.4)
    frags.append(b2)

    render(os.path.join(IMG, 'scale-to-demand.svg'), W, H, *frags)


def fig_breakeven():
    """Поріг завантаження: роздрібний рахунок (нахилена пряма) проти
    обіцянки (горизонталь). Перетин = поріг beta = committed/retail."""
    W, H = 820, 470
    frags = []
    frags.append(text(W / 2, 34, "Місячний рахунок за завантаженням: роздріб проти обіцянки",
                      size=16, bold=True))

    ox, oy = 90, 78
    plot_w, plot_h = 600, 300
    base_y = oy + plot_h
    top_y = oy

    # осі
    frags.append(line(ox, top_y, ox, base_y, color=LINE, sw=1.5))
    frags.append(line(ox, base_y, ox + plot_w, base_y, color=LINE, sw=1.5))
    frags.append(text(ox - 12, top_y + 6, "$ / міс", size=11.5, color=MUTED, anchor="end"))
    frags.append(text(ox + plot_w / 2, base_y + 40, "завантаження (частка ввімкнених годин)",
                      size=12, color=MUTED))

    # Модель: retail = 0.10·(u·720), committed = 0.07·720 = 50.40 (пласко)
    retail_hr = 0.10
    committed_hr = 0.07
    Hm = 720.0
    committed = committed_hr * Hm            # 50.40
    retail_at_full = retail_hr * Hm          # 72.00
    ymax = retail_at_full * 1.08             # запас угорі

    def px(u):    # u у 0..1
        return ox + u * plot_w

    def py(dollars):
        return base_y - (dollars / ymax) * plot_h

    # поділки осі X (0..100 %)
    for u in (0.0, 0.25, 0.5, 0.7, 1.0):
        x = px(u)
        frags.append(line(x, base_y, x, base_y + 6, color=LINE, sw=1.2))
        frags.append(text(x, base_y + 22, "%d%%" % int(u * 100), size=11, color=MUTED))

    # горизонталь обіцянки
    yc = py(committed)
    frags.append(line(ox, yc, ox + plot_w, yc, color=NEG, sw=2.4))
    frags.append(text(ox + plot_w - 6, yc - 10, "обіцянка = 50.40 $ (пласко)",
                      size=12, color=NEG, bold=True, anchor="end"))

    # нахилена пряма роздрібу від (0,0) до (1, 72)
    frags.append(line(px(0.0), py(0.0), px(1.0), py(retail_at_full), color=POS, sw=2.4))
    frags.append(text(px(1.0) - 4, py(retail_at_full) - 10, "роздріб = 0.10·год",
                      size=12, color=POS, bold=True, anchor="end"))

    # точка перетину — поріг 70 %
    ub = committed_hr / retail_hr            # 0.70
    xb, yb = px(ub), py(committed)
    frags.append(line(xb, base_y, xb, yb, color=MUTED, sw=1.3, dash="5 5"))
    frags.append(circle(xb, yb, 6, fill=BG, stroke=INK, sw=2.2))

    # підпис порога — осторонь від ліній, у власній рамці
    b1, w1, h1 = textbox(xb - 150, yb - 70, "поріг завантаження 70 %\n(нижче — роздріб; вище — обіцянка)",
                         size=11.5, fill="#fff8e6", stroke="#b8860b", sw=1.5)
    frags.append(b1)
    frags.append(line(xb - 150 + w1 / 2 - 10, yb - 70 + h1 / 2, xb - 6, yb - 4,
                      color="#b8860b", sw=1.2, dash="4 4"))

    # зони дешевизни — підписи в кутах, подалі від кривих
    frags.append(text(px(0.28), py(6), "тут дешевший роздріб", size=11.5,
                      color=POS, anchor="middle"))
    frags.append(text(px(0.87), py(committed) + 30, "тут дешевша обіцянка", size=11.5,
                      color=NEG, anchor="middle"))

    render(os.path.join(IMG, 'breakeven.svg'), W, H, *frags)


def fig_three_tier():
    """Пікуватий добовий профіль, розкладений по трьох тарифах:
    база (обіцянка) — плаский низ; сплеск (спот) — середня смуга;
    пік понад ємність спота (роздріб) — верхівки."""
    W, H = 1000, 540
    frags = []
    frags.append(text(W / 2, 34, "Один профіль попиту, три тарифи під ним", size=16, bold=True))

    # той самий добовий профіль, що в статті (нормований 0..1)
    demand = [0.10, 0.08, 0.07, 0.09, 0.15, 0.35, 0.62, 0.85,
              0.78, 0.70, 0.66, 0.72, 0.80, 0.74, 0.60, 0.55,
              0.68, 0.58, 0.40, 0.30, 0.24, 0.20, 0.15, 0.12]
    n = len(demand)

    ox, oy = 70, 92
    plot_w, plot_h = 720, 300
    base_y = oy + plot_h
    top_y = oy
    dx = plot_w / (n - 1)

    frags.append(line(ox, top_y, ox, base_y, color=LINE, sw=1.5))
    frags.append(line(ox, base_y, ox + plot_w, base_y, color=LINE, sw=1.5))
    frags.append(text(ox - 10, top_y + 6, "машин", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox + plot_w / 2, base_y + 26, "час доби (24 год)", size=11.5, color=MUTED))

    def px(i):
        return ox + i * dx

    def py(v):
        return base_y - v * plot_h

    # рівні розкрою: база (обіцянка) до 0.30, спот до 0.66, вище — роздріб
    base_lvl = 0.30
    spot_lvl = 0.66

    # смуга БАЗИ (обіцянка): від 0 до min(demand, base_lvl) — тут завжди повно
    band_base = []
    band_base.append("%.1f,%.1f" % (px(0), base_y))
    for i in range(n):
        band_base.append("%.1f,%.1f" % (px(i), py(min(demand[i], base_lvl))))
    band_base.append("%.1f,%.1f" % (px(n - 1), base_y))
    frags.append('<polygon points="%s" fill="#dfe8fb" stroke="none"/>' % " ".join(band_base))

    # смуга СПОТА: від base_lvl до min(demand, spot_lvl), лише де demand > base_lvl
    band_spot = []
    band_spot.append("%.1f,%.1f" % (px(0), py(base_lvl)))
    for i in range(n):
        band_spot.append("%.1f,%.1f" % (px(i), py(max(base_lvl, min(demand[i], spot_lvl)))))
    band_spot.append("%.1f,%.1f" % (px(n - 1), py(base_lvl)))
    frags.append('<polygon points="%s" fill="#d6f0e0" stroke="none"/>' % " ".join(band_spot))

    # смуга РОЗДРІБУ: від spot_lvl до demand, лише де demand > spot_lvl
    band_ret = []
    band_ret.append("%.1f,%.1f" % (px(0), py(spot_lvl)))
    for i in range(n):
        band_ret.append("%.1f,%.1f" % (px(i), py(max(spot_lvl, demand[i]))))
    band_ret.append("%.1f,%.1f" % (px(n - 1), py(spot_lvl)))
    frags.append('<polygon points="%s" fill="#fbe0dc" stroke="none"/>' % " ".join(band_ret))

    # лінії рівнів розкрою
    frags.append(line(ox, py(base_lvl), ox + plot_w, py(base_lvl), color=NEG, sw=1.8, dash="7 5"))
    frags.append(line(ox, py(spot_lvl), ox + plot_w, py(spot_lvl), color=FIELD, sw=1.8, dash="7 5"))

    # крива попиту поверх усього
    poly = " ".join("%.1f,%.1f" % (px(i), py(demand[i])) for i in range(n))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, INK))

    # підписи смуг — праворуч від графіка, кожен у своїй рамці, з запасом
    lx = ox + plot_w + 18
    bb, wbb, hbb = textbox(lx + 70, py(base_lvl / 2), "БАЗА → обіцянка\n(−30 %, є завжди)",
                           size=11.5, fill="#dfe8fb", stroke=NEG, sw=1.5)
    frags.append(bb)
    bs, wbs, hbs = textbox(lx + 70, py((base_lvl + spot_lvl) / 2), "СПЛЕСК → спот\n(−80 %, перезапускне)",
                           size=11.5, fill="#d6f0e0", stroke=FIELD, sw=1.5)
    frags.append(bs)
    br, wbr, hbr = textbox(lx + 70, py(spot_lvl + 0.14), "ПІК → роздріб\n(повна ціна, надійно)",
                           size=11.5, fill="#fbe0dc", stroke=POS, sw=1.5)
    frags.append(br)

    render(os.path.join(IMG, 'three-tier.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_two_families()
    fig_scale_to_demand()
    fig_breakeven()
    fig_three_tier()
    print("OK: two-families.svg, scale-to-demand.svg, breakeven.svg, three-tier.svg")
