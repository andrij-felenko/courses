# -*- coding: utf-8 -*-
"""Фігури до теми «Інверсія фази в ОП (phase inversion)».
Три фігури:
  what-you-see.svg — вхід виходить за синфазне вікно: вихід не клипить угорі, а кидається ВНИЗ (фаза перевернулась)
  cm-window.svg    — синфазне вікно: смуга дозволених напруг між рейками; вище/нижче — вхідний каскад глухне й перевертає знак
  the-fix.svg      — послідовний резистор + діодні фіксатори тримають вхід усередині вікна
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def what_you_see():
    """Повторювач: поки вхід у вікні — вихід стежить; вхід вилазить угору — вихід КИДАЄТЬСЯ ВНИЗ, не вгору."""
    W, H = 720, 380
    p = []
    ox, oy = 70, 210     # початок осі часу
    axw = 560
    midy = oy
    amp = 110            # амплітуда вхідної синусоїди (пікове перевищить вікно)
    top_lim = 70         # верхня межа синфазного вікна (від midy вгору)
    bot_lim = 120        # нижня межа (вниз) — несиметрично, як у реалі
    railhi = 150         # де «висить» вихід після перевороту (низ)

    # осі
    p.append(line(ox, midy, ox + axw, midy, color=MUTED, sw=1))
    p.append(text(ox + axw + 8, midy + 4, "t", size=13, color=MUTED, anchor="start"))

    # смуга синфазного вікна
    p.append(rect(ox, midy - top_lim, axw, top_lim + bot_lim, fill="#eafaf0", stroke=FIELD, sw=1, rx=2))
    p.append(line(ox, midy - top_lim, ox + axw, midy - top_lim, color=FIELD, sw=1.5, dash="5 4"))
    p.append(text(ox + 6, midy - top_lim - 6, "верх синфазного вікна", size=11, color=FIELD, anchor="start"))

    # вхідний сигнал (пунктир) — синусоїда, що ПЕРЕВИЩУЄ вікно вгорі
    N = 240
    in_pts = []
    for k in range(N + 1):
        xx = ox + axw * k / N
        ph = 2 * math.pi * 1.6 * k / N
        in_pts.append((xx, midy - amp * math.sin(ph)))
    d_in = "M" + " L".join("%.1f %.1f" % q for q in in_pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % (d_in, NEG))

    # вихід: стежить, поки вхід ≤ верх вікна; щойно вхід перевищив — стрибок ВНИЗ до railhi
    out_pts = []
    for k in range(N + 1):
        xx = ox + axw * k / N
        ph = 2 * math.pi * 1.6 * k / N
        s = math.sin(ph)
        in_y = midy - amp * s
        over = in_y < (midy - top_lim)      # вхід вище верхньої межі вікна
        if over:
            y = midy + railhi               # переворот: кидається ВНИЗ
        else:
            y = in_y
        out_pts.append((xx, y, over))
    # малюємо суцільними сегментами, переходи на стрибку — окремо
    seg = []
    for (xx, yy, over) in out_pts:
        seg.append((xx, yy))
    d_out = "M" + " L".join("%.1f %.1f" % (q[0], q[1]) for q in seg)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d_out, POS))

    # позначки
    p.append(text(ox + 86, midy - amp - 6, "вхід (хоче стежити)", size=11, color=NEG, anchor="start"))
    # знайти перший інтервал over для виноски
    first_over_x = None
    for (xx, yy, over) in out_pts:
        if over:
            first_over_x = xx
            break
    if first_over_x:
        p.append(text(first_over_x + 40, midy + railhi - 8,
                      "вихід ПЕРЕВЕРНУВСЯ — кинувся до НИЖНЬОЇ рейки", size=11, bold=True, color=POS, anchor="start"))
        p.append(arrow(first_over_x, midy - top_lim - 2, first_over_x, midy + railhi - 14, color=POS, sw=2))

    b, _, _ = textbox(W / 2, 352,
                      "Поки вхід у зеленому вікні — вихід чесно стежить. Щойно вхід виліз ВГОРУ за межу,\n"
                      "вихід не впирається у верхню рейку — він кидається до ПРОТИЛЕЖНОЇ. Це інверсія фази.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'what-you-see.svg'), W, H, *p,
           title="Інверсія фази: вихід тікає не туди, куди штовхає вхід")


def cm_window():
    """Синфазне вікно між рейками: усередині — норма; вище/нижче — вхідний каскад глухне, знак перевертається."""
    W, H = 700, 420
    p = []
    cx = 250
    bw = 150
    top = 70
    bot = 360
    # «труба» між рейками
    p.append(rect(cx - bw / 2, top, bw, bot - top, fill=BG, stroke=MUTED, sw=1, rx=4))
    # рейки
    p.append(line(cx - bw / 2 - 20, top, cx + bw / 2 + 20, top, color=POS, sw=2.6))
    p.append(text(cx + bw / 2 + 26, top + 4, "V+  (верхня рейка)", size=12, color=POS, anchor="start"))
    p.append(line(cx - bw / 2 - 20, bot, cx + bw / 2 + 20, bot, color=NEG, sw=2.6))
    p.append(text(cx + bw / 2 + 26, bot + 4, "V−  (нижня рейка)", size=12, color=NEG, anchor="start"))

    # межі синфазного вікна — усередині, із запасом від рейок
    win_top = top + 55
    win_bot = bot - 70
    p.append(rect(cx - bw / 2, win_top, bw, win_bot - win_top, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=3))
    p.append(line(cx - bw / 2, win_top, cx + bw / 2, win_top, color=FIELD, sw=1.5, dash="5 4"))
    p.append(line(cx - bw / 2, win_bot, cx + bw / 2, win_bot, color=FIELD, sw=1.5, dash="5 4"))
    p.append(text(cx, (win_top + win_bot) / 2 - 8, "СИНФАЗНЕ", size=14, bold=True, color=FIELD))
    p.append(text(cx, (win_top + win_bot) / 2 + 12, "ВІКНО", size=14, bold=True, color=FIELD))
    p.append(text(cx, (win_top + win_bot) / 2 + 30, "тут ОП працює", size=11, color=MUTED))

    # верхня заборонена зона
    p.append(text(cx, (top + win_top) / 2 - 6, "надто близько до V+", size=11, bold=True, color=POS))
    p.append(text(cx, (top + win_top) / 2 + 10, "каскад глухне → переворот", size=10, color=POS))
    # нижня заборонена зона
    p.append(text(cx, (win_bot + bot) / 2 - 6, "нижче V− (навіть на 0.3 В)", size=11, bold=True, color=NEG))
    p.append(text(cx, (win_bot + bot) / 2 + 10, "паразитний діод → переворот", size=10, color=NEG))

    # права колонка: що з виходом у кожній зоні
    rx = cx + bw / 2 + 26
    arr_x = cx + bw / 2 + 8
    # норма — вихід стежить
    p.append(arrow(arr_x, (win_top + win_bot) / 2, rx - 4, (win_top + win_bot) / 2, color=FIELD, sw=2))
    b1, w1, h1 = textbox(rx + 92, (win_top + win_bot) / 2, "вихід стежить за входом\n(правильний знак)",
                         size=11, fill="#eafaf0", stroke=FIELD)
    p.append(b1)

    b, _, _ = textbox(W / 2, 398,
                      "Синфазна напруга — це «де посередині» сидять ОБИДВА входи. Доки вона в зеленому вікні —\n"
                      "усе гаразд. Вилізла за межу (до будь-якої рейки) — вхідний каскад зривається й знак перевертається.",
                      size=12, fill="#f4f6f8", stroke=LINE)
    p.append(b)
    render(os.path.join(OUT, 'cm-window.svg'), W, H, *p,
           title="Синфазне вікно: вузька смуга між рейками, де ОП ще «при тямі»")


def the_fix():
    """Послідовний резистор + два діоди-фіксатори: струм обмежено, вхід не вилазить за рейки."""
    W, H = 720, 360
    p = []
    y = 170
    # джерело сигналу зліва
    p.append(circle(70, y, 24, fill=BG, stroke=LINE, sw=1.8))
    p.append(text(70, y + 5, "Uвх", size=13, bold=True))
    p.append(text(70, y + 44, "може вилізти за рейки", size=10, color=MUTED))

    # послідовний резистор
    rx1, rx2 = 130, 230
    p.append(line(94, y, rx1, y, color=INK, sw=2))
    p.append(rect(rx1, y - 11, rx2 - rx1, 22, fill=FILL, stroke=LINE, sw=1.6, rx=3))
    p.append(text((rx1 + rx2) / 2, y + 5, "Rпосл", size=12, bold=True))
    p.append(text((rx1 + rx2) / 2, y - 18, "1 кОм", size=11, color=MUTED))

    # вузол входу + лінія до ОП
    nodex = 330
    p.append(line(rx2, y, nodex + 130, y, color=INK, sw=2))
    p.append(circle(nodex, y, 3.2, fill=INK, stroke=INK))

    # два діоди-фіксатори: до V+ і до V−
    railhi_y = y - 95
    raillo_y = y + 95
    p.append(line(nodex, y, nodex, railhi_y, color=INK, sw=1.8))
    p.append(line(nodex, y, nodex, raillo_y, color=INK, sw=1.8))
    # рейки
    p.append(line(nodex - 60, railhi_y, nodex + 60, railhi_y, color=POS, sw=2.4))
    p.append(text(nodex + 66, railhi_y + 4, "V+", size=12, bold=True, color=POS, anchor="start"))
    p.append(line(nodex - 60, raillo_y, nodex + 60, raillo_y, color=NEG, sw=2.4))
    p.append(text(nodex + 66, raillo_y + 4, "V−", size=12, bold=True, color=NEG, anchor="start"))
    # символ діода вгору (трикутник вістрям до рейки)
    def diode(cx, cy, up):
        s = -1 if up else 1
        tri = '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.4"/>' % (
            cx - 7, cy + 9 * s, cx + 7, cy + 9 * s, cx, cy - 9 * s, FILL, LINE)
        bar = line(cx - 8, cy - 9 * s, cx + 8, cy - 9 * s, color=LINE, sw=2)
        return tri + bar
    p.append(diode(nodex, (y + railhi_y) / 2, up=True))
    p.append(diode(nodex, (y + raillo_y) / 2, up=False))
    p.append(text(nodex - 12, (y + railhi_y) / 2 + 4, "D1", size=11, color=MUTED, anchor="end"))
    p.append(text(nodex - 12, (y + raillo_y) / 2 + 4, "D2", size=11, color=MUTED, anchor="end"))

    # ОП-трикутник справа
    ax = nodex + 130
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, y - 34, ax, y + 34, ax + 70, y, FILL, LINE))
    p.append(text(ax + 22, y + 5, "ОП", size=14, bold=True))
    p.append(arrow(ax + 70, y, ax + 120, y, color=INK, sw=2))
    p.append(text(ax + 96, y - 8, "вихід", size=11, color=MUTED, anchor="start"))

    # пояснення дії
    p.append(text(nodex, railhi_y - 14, "вхід полізе вище V+ → D1 відкрився, тримає", size=10, color=POS))
    p.append(text(nodex, raillo_y + 22, "полізе нижче V− → D2 відкрився, тримає", size=10, color=NEG))

    b, _, _ = textbox(W / 2, 332,
                      "Резистор обмежує струм, діоди D1/D2 не пускають вузол за рейки — вхід ОП лишається у вікні.\n"
                      "Перевага: дешево й надійно. Часто простіше взяти ОП, у якому захист уже всередині.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'the-fix.svg'), W, H, *p,
           title="Лік від перевороту: послідовний резистор + діодні фіксатори на рейки")


if __name__ == '__main__':
    what_you_see()
    cm_window()
    the_fix()
    print("OK: 3 figures ->", OUT)
