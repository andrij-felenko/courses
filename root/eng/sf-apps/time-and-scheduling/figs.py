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

    axis_y = 238
    frags.append(line(60, axis_y, 748, axis_y, color=INK, sw=2.2))
    frags.append(arrow(748, axis_y, 772, axis_y, color=INK, sw=2.2))
    frags.append(text(66, axis_y + 30, "вісь миттєвостей (UTC)", size=13,
                      color=MUTED, anchor="start", italic=True))

    dot_x = 410
    frags.append(line(dot_x, axis_y, dot_x, axis_y - 12, color=POS, sw=2))
    frags.append(circle(dot_x, axis_y, 7, fill=POS, stroke=POS, sw=2))
    frags.append(text(dot_x, axis_y + 30, "08:00 UTC", size=15, color=POS, bold=True))

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
        frags.append(arrow(dot_x, axis_y - 14, bx, box_cy + bh / 2 + 4,
                           color=LINE, sw=1.6))

    return render(os.path.join(IMG, "two-axes.svg"), W, H, *frags,
                  title="Одна мить — багато прочитань")


def fig_three_clocks():
    """Три питання про час → три механізми → три правила."""
    W, H = 860, 306
    frags = []

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
    y0 = 88
    span = 182.0
    steps = 27
    step_px = span / steps

    frags.append(line(x0, y0, x1 + 8, y0, color=INK, sw=2.4))

    def ut1(t):
        return y0 + span * (0.90 * t ** 1.10 + 0.10 * t
                            + 0.012 * math.sin(2 * math.pi * 2.2 * t))

    N = 240
    pts = [(x0 + (x1 - x0) * i / N, ut1(i / N)) for i in range(N + 1)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        frags.append(line(ax, ay, bx, by, color=NEG, sw=2.0))

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

    frags.append(text(92, y0 + 5, "0", size=12, color=MUTED, anchor="end"))
    frags.append(text(92, y0 + span + 5, "−27 с", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0, 302, "1972", size=12, color=MUTED))
    frags.append(text(x1, 302, "2016", size=12, color=MUTED))

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

    X0 = 148
    HW = 21.0
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


def fig_monotonic_vs_wall_clock():
    """Порівняння поведінки CLOCK_REALTIME та CLOCK_MONOTONIC у часі."""
    W, H = 880, 420
    frags = []

    frags.append(text(W / 2, 36, "Поведінка стінного та монотонного годинників при збуреннях",
                      size=16, color=INK, bold=True))

    y_rt_base = 150
    frags.append(text(50, y_rt_base - 50, "CLOCK_REALTIME (стінний час): стрибки, зміщення та розриви",
                      size=13, color=POS, anchor="start", bold=True))
    
    frags.append(line(50, y_rt_base, 830, y_rt_base, color=MUTED, sw=1.2))
    
    frags.append(line(70, 175, 250, 115, color=POS, sw=2.4))
    frags.append(circle(250, 115, 4, fill=POS, stroke=POS))
    
    frags.append(line(250, 115, 250, 155, color=POS, sw=1.8, dash="4,4"))
    frags.append(arrow(250, 115, 250, 150, color=POS, sw=1.8))
    frags.append(circle(250, 155, 4, fill=BG, stroke=POS, sw=2))
    
    frags.append(line(250, 155, 500, 75, color=POS, sw=2.4))
    frags.append(circle(500, 75, 4, fill=POS, stroke=POS))
    
    frags.append(line(500, 75, 500, 45, color=POS, sw=1.8, dash="4,4"))
    frags.append(arrow(500, 75, 500, 50, color=POS, sw=1.8))
    frags.append(circle(500, 45, 4, fill=BG, stroke=POS, sw=2))
    
    frags.append(line(500, 45, 780, 20, color=POS, sw=2.4))

    b1, _, _ = textbox(250, 75, "NTP step\n(стрибок назад −500мс)", size=11, pad=6,
                       fill="#fff5f5", stroke=POS, color=POS)
    frags.append(b1)
    
    b2, _, _ = textbox(500, 115, "DST / settimeofday\n(стрибок уперед +1год)", size=11, pad=6,
                       fill="#fff5f5", stroke=POS, color=POS)
    frags.append(b2)
    
    b3, _, _ = textbox(720, 150, "Пастка: t2 − t1 < 0\n(від'ємна тривалість!)", size=11, pad=6,
                       fill="#fff0f0", stroke=POS, color=POS, bold=True)
    frags.append(b3)

    frags.append(line(50, 225, 830, 225, color="#e0e0e0", sw=1.5, dash="6,6"))

    y_mono_base = 350
    frags.append(text(50, y_mono_base - 90, "CLOCK_MONOTONIC (інтервальний час): строго не спадає, без розривів",
                      size=13, color=FIELD, anchor="start", bold=True))
    
    frags.append(line(50, y_mono_base, 830, y_mono_base, color=MUTED, sw=1.2))
    
    frags.append(line(70, 360, 780, 260, color=FIELD, sw=2.8))
    frags.append(arrow(770, 261.5, 785, 259, color=FIELD, sw=2.8))
    
    t1_x, t1_y = 200, 343
    t2_x, t2_y = 600, 286
    frags.append(circle(t1_x, t1_y, 5, fill=FIELD, stroke=FIELD))
    frags.append(circle(t2_x, t2_y, 5, fill=FIELD, stroke=FIELD))
    frags.append(line(t1_x, t1_y, t1_x, y_mono_base + 12, color=FIELD, sw=1.2, dash="3,3"))
    frags.append(line(t2_x, t2_y, t2_x, y_mono_base + 12, color=FIELD, sw=1.2, dash="3,3"))
    frags.append(text(t1_x, y_mono_base + 24, "t1 (старт)", size=12, color=INK, bold=True))
    frags.append(text(t2_x, y_mono_base + 24, "t2 (кінець)", size=12, color=INK, bold=True))
    
    frags.append(line(t1_x, y_mono_base + 38, t2_x, y_mono_base + 38, color=FIELD, sw=1.6))
    frags.append(arrow(t1_x + 15, y_mono_base + 38, t1_x, y_mono_base + 38, color=FIELD, sw=1.6))
    frags.append(arrow(t2_x - 15, y_mono_base + 38, t2_x, y_mono_base + 38, color=FIELD, sw=1.6))
    frags.append(text((t1_x + t2_x) / 2, y_mono_base + 54, "Δt = t2 − t1 > 0 завжди гарантовано",
                      size=12, color=FIELD, bold=True))

    mb1, _, _ = textbox(380, 260, "Плавне коригування частоти (NTP slew)\nбез стрибків і без повернення назад",
                        size=11, pad=8, fill="#f0fff4", stroke=FIELD, color=FIELD)
    frags.append(mb1)

    return render(os.path.join(IMG, "monotonic-vs-wall-clock.svg"), W, H, *frags,
                  title="Монотонний проти стінного годинника")


def fig_ntp_slew_vs_step():
    """Коригування часу NTP: стрибок (step) проти плавного затягування (slew)."""
    W, H = 880, 360
    frags = []

    frags.append(text(W / 2, 34, "Підлаштування часу NTP: стрибок (Step) проти затягування (Slew)",
                      size=16, color=INK, bold=True))

    col1_cx = 240
    frags.append(text(col1_cx, 70, "Стрибок (Step: settimeofday)", size=14, color=POS, bold=True))
    
    s_x0, s_y0 = 60, 260
    frags.append(line(s_x0, s_y0, 420, s_y0, color=MUTED, sw=1.2))
    frags.append(line(s_x0, s_y0, s_x0, 100, color=MUTED, sw=1.2))
    frags.append(text(420, s_y0 + 20, "час (t)", size=11, color=MUTED))
    frags.append(text(s_x0 - 10, 100, "показ", size=11, color=MUTED, anchor="end"))
    
    frags.append(line(s_x0, 240, 400, 120, color=MUTED, sw=1.4, dash="4,4"))
    
    frags.append(line(s_x0, 260, 220, 166, color=POS, sw=2.2))
    frags.append(circle(220, 166, 4, fill=POS, stroke=POS))
    frags.append(line(220, 166, 220, 134, color=POS, sw=2.0, dash="3,3"))
    frags.append(arrow(220, 166, 220, 138, color=POS, sw=2.0))
    frags.append(circle(220, 134, 4, fill=BG, stroke=POS, sw=2))
    frags.append(line(220, 134, 400, 80, color=POS, sw=2.2))
    
    sb, _, _ = textbox(col1_cx, 305, "Миттєвий розрив шкали\nПорушує монотонність та ламає таймери",
                       size=11, pad=6, fill="#fff5f5", stroke=POS, color=POS)
    frags.append(sb)

    frags.append(line(450, 60, 450, 330, color="#dddddd", sw=1.5))

    col2_cx = 660
    frags.append(text(col2_cx, 70, "Затягування (Slew: adjtime / PLL)", size=14, color=FIELD, bold=True))
    
    w_x0, w_y0 = 480, 260
    frags.append(line(w_x0, w_y0, 840, w_y0, color=MUTED, sw=1.2))
    frags.append(line(w_x0, w_y0, w_x0, 100, color=MUTED, sw=1.2))
    frags.append(text(840, w_y0 + 20, "час (t)", size=11, color=MUTED))
    frags.append(text(w_x0 - 10, 100, "показ", size=11, color=MUTED, anchor="end"))
    
    frags.append(line(w_x0, 240, 820, 120, color=MUTED, sw=1.4, dash="4,4"))
    
    frags.append(line(w_x0, 260, 580, 193, color=FIELD, sw=2.2))
    frags.append(line(580, 193, 720, 115, color=FIELD, sw=2.4))
    frags.append(line(720, 115, 820, 82, color=FIELD, sw=2.2))
    
    frags.append(circle(580, 193, 3, fill=FIELD, stroke=FIELD))
    frags.append(circle(720, 115, 3, fill=FIELD, stroke=FIELD))
    
    wb, _, _ = textbox(col2_cx, 305, "Зміна темпу ходу (до ±500 PPM)\nШкала неперервна, порядок подій збережено",
                       size=11, pad=6, fill="#f0fff4", stroke=FIELD, color=FIELD)
    frags.append(wb)

    return render(os.path.join(IMG, "ntp-slew-vs-step.svg"), W, H, *frags,
                  title="NTP Slew проти Step")


if __name__ == "__main__":
    p1 = fig_two_axes()
    p2 = fig_three_clocks()
    p3 = fig_time_chain()
    p4 = fig_utc_scales()
    p5 = fig_user_day()
    p6 = fig_monotonic_vs_wall_clock()
    p7 = fig_ntp_slew_vs_step()
    print("written:", p1)
    print("written:", p2)
    print("written:", p3)
    print("written:", p4)
    print("written:", p5)
    print("written:", p6)
    print("written:", p7)
