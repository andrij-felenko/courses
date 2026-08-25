# -*- coding: utf-8 -*-
"""Фігури до статті «Прикладний час». Запуск із теки теми: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_two_axes():
    """Одна мить на осі UTC — і кілька настінних написів на неї."""
    W, H = 820, 320
    frags = []

    # горизонтальна вісь миттєвостей
    axis_y = 238
    frags.append(line(60, axis_y, 748, axis_y, color=INK, sw=2.2))
    frags.append(arrow(748, axis_y, 772, axis_y, color=INK, sw=2.2))
    frags.append(text(66, axis_y + 30, "вісь миттєвостей (UTC)", size=13,
                      color=MUTED, anchor="start", italic=True))

    # одна виділена мить
    dot_x = 410
    frags.append(line(dot_x, axis_y, dot_x, axis_y - 12, color=POS, sw=2))
    frags.append(circle(dot_x, axis_y, 7, fill=POS, stroke=POS, sw=2))
    frags.append(text(dot_x, axis_y + 30, "08:00 UTC", size=15, color=POS, bold=True))

    # три настінні прочитання тієї самої миті
    reads = [
        (170, "Лондон  +1", "09:00"),
        (410, "Київ  +3",   "11:00"),
        (650, "Токіо  +9",  "17:00"),
    ]
    box_cy = 96
    for bx, city, hhmm in reads:
        body, bw, bh = textbox(bx, box_cy, city + "\n" + hhmm, size=15,
                               pad=12, min_w=120, bold=False)
        frags.append(body)
        # стрілка від миті до низу рамки
        frags.append(arrow(dot_x, axis_y - 14, bx, box_cy + bh / 2 + 4,
                           color=LINE, sw=1.6))

    return render(os.path.join(IMG, "two-axes.svg"), W, H, *frags,
                  title="Одна мить — багато прочитань")


def fig_three_clocks():
    """Три питання про час → три механізми → три правила."""
    W, H = 860, 306
    frags = []

    # заголовки колонок
    frags.append(text(150, 58, "питання", size=13, color=MUTED, italic=True))
    frags.append(text(435, 58, "механізм", size=13, color=MUTED, italic=True))
    frags.append(text(715, 58, "правило", size=13, color=MUTED, italic=True))

    QX, QW = 40, 220
    MX, MW = 310, 250
    AX, AW = 610, 210
    BH = 54
    rows = [
        ("Котра зараз мить?", "UTC-лічильник\n(секунди від 1970)",
         "зберігай і рахуй", "#eafaf1", FIELD),
        ("Що на стіні тут?", "часовий пояс + tz-база",
         "переводь лише на межі", FILL, LINE),
        ("Скільки триває?", "монотонний годинник",
         "мір тривалість ним", "#eaf0fd", NEG),
    ]
    ys = [80, 152, 224]
    for (q, m, a, fill, stroke), y in zip(rows, ys):
        cy = y + BH / 2
        frags.append(fitbox(QX, y, QW, BH, q, size=15, fill=fill, stroke=stroke, bold=True))
        frags.append(fitbox(MX, y, MW, BH, m, size=14, fill=fill, stroke=stroke))
        frags.append(fitbox(AX, y, AW, BH, a, size=14, fill=fill, stroke=stroke))
        frags.append(arrow(QX + QW, cy, MX, cy, color=LINE, sw=1.6))
        frags.append(arrow(MX + MW, cy, AX, cy, color=LINE, sw=1.6))

    return render(os.path.join(IMG, "three-clocks.svg"), W, H, *frags,
                  title="Три ролі часу в застосунку")


def fig_time_chain():
    """Ланцюг домовленостей: від залізничного часу до скасування високосних секунд."""
    W, H = 940, 300
    frags = []
    axis_y = 185

    frags.append(line(52, axis_y, 906, axis_y, color=INK, sw=2.2))
    frags.append(arrow(906, axis_y, 926, axis_y, color=INK, sw=2.2))

    items = [
        ("1840", "GWR: лондонський\nчас на всій лінії"),
        ("1883", "залізниці США:\nдень двох полуднів"),
        ("1884", "Вашингтон:\nмеридіан Ґрінвіча"),
        ("1955", "перший цезієвий\nгодинник (NPL)"),
        ("1967", "секунда SI:\n9 192 631 770"),
        ("1972", "UTC із високосною\nсекундою"),
        ("1986", "tz-база:\nчинні правила зон"),
        ("2035", "високосних секунд\nбільше не буде"),
    ]
    for i, (yr, body) in enumerate(items):
        x = 100 + 105 * i
        above = (i % 2 == 0)
        cy = 100 if above else 232
        planned = (i == len(items) - 1)
        box, w, h = textbox(x, cy, yr + "\n" + body, size=13, pad=10, min_w=120,
                            fill="#fafafa" if planned else FILL,
                            stroke=MUTED if planned else LINE)
        frags.append(box)
        if above:
            frags.append(line(x, cy + h / 2, x, axis_y - 7, color=LINE, sw=1.4))
        else:
            frags.append(line(x, axis_y + 7, x, cy - h / 2, color=LINE, sw=1.4))
        frags.append(circle(x, axis_y, 5, fill=BG, stroke=INK, sw=2))

    return render(os.path.join(IMG, "time-chain.svg"), W, H, *frags,
                  title="Ланцюг домовленостей про єдиний час")


def fig_utc_scales():
    """TAI, UT1 і UTC: рівний атомний лік, нерівна планета й сходинки між ними."""
    import math
    W, H = 880, 320
    frags = []

    x0, x1 = 100, 640
    y0 = 88            # рівень TAI (нуль розбіжності)
    span = 182.0       # повне відставання UT1 на правому краї
    steps = 27
    step_px = span / steps

    # TAI — пряма
    frags.append(line(x0, y0, x1 + 8, y0, color=INK, sw=2.4))

    # UT1 — плавна крива з нерівним ходом
    def ut1(t):
        return y0 + span * (0.90 * t ** 1.10 + 0.10 * t
                            + 0.012 * math.sin(2 * math.pi * 2.2 * t))

    N = 240
    pts = [(x0 + (x1 - x0) * i / N, ut1(i / N)) for i in range(N + 1)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        frags.append(line(ax, ay, bx, by, color=NEG, sw=2.0))

    # UTC — сходинки по цілій секунді
    lvl, sx = 0, x0
    for px, py in pts:
        k = int((py - y0) // step_px)
        if k > lvl:
            frags.append(line(sx, y0 + lvl * step_px, px, y0 + lvl * step_px,
                              color=POS, sw=2.2))
            frags.append(line(px, y0 + lvl * step_px, px, y0 + k * step_px,
                              color=POS, sw=2.2))
            lvl, sx = k, px
    frags.append(line(sx, y0 + lvl * step_px, x1, y0 + lvl * step_px, color=POS, sw=2.2))

    # підписи осей
    frags.append(text(92, y0 + 5, "0", size=12, color=MUTED, anchor="end"))
    frags.append(text(92, y0 + span + 5, "−27 с", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0, 302, "1972", size=12, color=MUTED))
    frags.append(text(x1, 302, "2016", size=12, color=MUTED))

    # легенда
    legend = [
        (110, "TAI\nрівний атомний лік", INK),
        (185, "UTC\nтікає як TAI,\nстрибає цілою секундою", POS),
        (262, "UT1\nза обертанням Землі", NEG),
    ]
    for cy, body, col in legend:
        box, w, h = textbox(760, cy, body, size=13, pad=10, stroke=col, color=col)
        frags.append(box)

    return render(os.path.join(IMG, "utc-scales.svg"), W, H, *frags,
                  title="Три шкали часу й сходинки високосних секунд")


def fig_user_day():
    """Календарна доба користувача як проміжок митей: 23, 24 і 25 годин."""
    W, H = 880, 326
    frags = []

    frags.append(text(W / 2, 54, "півзакритий проміжок митей:   [ від … до )",
                      size=13, color=MUTED, italic=True))

    X0 = 148            # ліва межа смуг
    HW = 21.0           # пікселів на годину
    BH = 32
    rows = [
        ("29 бер 2026", 23, "03:00 не існувало", "#eaf0fd", NEG,
         "28.03  22:00Z", "29.03  21:00Z"),
        ("1 чер 2026", 24, "звичайна доба", FILL, LINE,
         "31.05  21:00Z", "01.06  21:00Z"),
        ("25 жов 2026", 25, "03:00 трапилося двічі", "#fbeae8", POS,
         "24.10  21:00Z", "25.10  22:00Z"),
    ]
    ys = [94, 170, 246]
    for (day, hours, note, fill, stroke, a, b), y in zip(rows, ys):
        w = hours * HW
        cy = y + BH / 2
        frags.append(text(118, cy + 5, day, size=13, color=INK, anchor="end", bold=True))
        frags.append(rect(X0, y, w, BH, fill=fill, stroke=stroke, sw=1.8))
        frags.append(text(X0 - 13, cy + 6, "[", size=19, color=stroke, bold=True))
        frags.append(text(X0 + w + 13, cy + 6, ")", size=19, color=stroke, bold=True))
        frags.append(text(X0 + w / 2, cy + 5, note, size=12, color=INK))
        frags.append(text(X0 + w + 32, cy + 6, "%d год" % hours, size=15,
                          color=stroke, anchor="start", bold=True))
        frags.append(text(X0, y + BH + 16, a, size=11, color=MUTED, anchor="start"))
        frags.append(text(X0 + w, y + BH + 16, b, size=11, color=MUTED, anchor="end"))

    frags.append(text(W / 2, 312,
                      "довжина смуги — скільки реального часу вміщає календарна доба киянина",
                      size=12, color=MUTED, italic=True))

    return render(os.path.join(IMG, "user-day.svg"), W, H, *frags,
                  title="Доба користувача на осі митей")


if __name__ == "__main__":
    p1 = fig_two_axes()
    p2 = fig_three_clocks()
    p3 = fig_time_chain()
    p4 = fig_utc_scales()
    p5 = fig_user_day()
    print("written:", p1)
    print("written:", p2)
    print("written:", p3)
    print("written:", p4)
    print("written:", p5)
