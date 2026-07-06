# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def lrm_crossover():
    W, H = 760, 460
    # Осі: поле для графіка
    x0, y0 = 90, 60      # верх-ліво графіка
    x1, y1 = 690, 360    # низ-право графіка (вісь часу знизу)
    frags = []

    # Осі
    frags.append(line(x0, y0, x0, y1, color=INK, sw=2))        # вісь Y
    frags.append(line(x0, y1, x1 + 10, y1, color=INK, sw=2))   # вісь X (час)
    frags.append(arrow(x1 - 8, y1, x1 + 14, y1, color=INK))    # стрілка часу
    frags.append(text((x0 + x1) / 2, y1 + 42, "час →  (більше відомо, більше залежних чекає)",
                      size=13, color=MUTED))
    # Підпис осі Y — вертикальний, ліворуч від осі, щоб не накладатися
    frags.append('<text x="34" y="%.1f" font-family="%s" font-size="13" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 34 %.1f)">величина</text>'
                 % ((y0 + y1) / 2, FONT, MUTED, (y0 + y1) / 2))

    # Крива ВИГОДИ відкладання (спадає): знань більшає — вигода чекати меншає
    import math
    def curve_points(fn, n=60):
        pts = []
        for i in range(n + 1):
            t = i / n
            px = x0 + t * (x1 - x0)
            py = y1 - fn(t) * (y1 - y0)
            pts.append((px, py))
        return pts

    benefit = curve_points(lambda t: 0.85 * (1 - t) ** 1.6 + 0.05)
    cost    = curve_points(lambda t: 0.05 + 0.85 * t ** 2.2)

    def polyline(pts, color, sw=3):
        d = " ".join("%.1f,%.1f" % p for p in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (d, color, sw))

    frags.append(polyline(benefit, NEG))
    frags.append(polyline(cost, POS))

    # Точка перетину (аналітично приблизно): 0.85(1-t)^1.6+0.05 = 0.05+0.85 t^2.2
    def bf(t): return 0.85 * (1 - t) ** 1.6 + 0.05
    def cf(t): return 0.05 + 0.85 * t ** 2.2
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if bf(mid) > cf(mid): lo = mid
        else: hi = mid
    tX = (lo + hi) / 2
    cxX = x0 + tX * (x1 - x0)
    cyX = y1 - bf(tX) * (y1 - y0)

    # Вертикаль LRM (від точки перетину ВНИЗ до осі часу; не чіпає жодної рамки)
    frags.append(line(cxX, cyX + 10, cxX, y1, color=FIELD, sw=2, dash="6,5"))
    frags.append(circle(cxX, cyX, 7, fill=BG, stroke=FIELD, sw=3))

    # "Останній можливий момент" — праворуч від LRM, ближче до краю
    tP = 0.90
    cxP = x0 + tP * (x1 - x0)
    # вертикаль тягнемо лише в НИЖНІЙ половині — там немає рамок-міток
    frags.append(line(cxP, (y0 + y1) / 2 + 20, cxP, y1, color=MUTED, sw=1.6, dash="3,5"))

    # Підписи кривих — біля їхніх «своїх» кінців, подалі одна від одної й від перетину
    frags.append(text(x0 + 118, y0 + 30, "вигода відкладання", size=14, color=NEG, bold=True))
    frags.append(text(x0 + 118, y0 + 48, "(знань ще мало)", size=12, color=NEG))
    frags.append(text(x1 - 118, y0 + 30, "ціна відкладання", size=14, color=POS, bold=True))
    frags.append(text(x1 - 118, y0 + 48, "(усе чекає)", size=12, color=POS))

    # Мітка LRM — рамкою над точкою перетину; поводок від НИЗУ рамки до точки (обидва кінці — не крізь рамку)
    lrm_cy = cyX - 74
    box, bw, bh = textbox(cxX, lrm_cy, "останній\nвідповідальний момент",
                          size=13, bold=True, fill="#eafaf0", stroke=FIELD, pad=9)
    frags.append(line(cxX, lrm_cy + bh / 2 + 2, cxX, cyX - 9, color=FIELD, sw=1.4, dash="3,4"))
    frags.append(box)

    # Мітка "останній можливий" — праворуч зверху; поводок від НИЗУ рамки вниз до верху вертикалі
    pos_cy = y0 + 78
    lbl, lw, lh = textbox(cxP, pos_cy, "останній\nможливий\nмомент",
                          size=12, fill="#f4f6f8", stroke=MUTED, pad=8)
    frags.append(line(cxP, pos_cy + lh / 2 + 2, cxP, (y0 + y1) / 2 + 18, color=MUTED, sw=1.2, dash="3,4"))
    frags.append(lbl)

    render(os.path.join(OUT, 'lrm-crossover.svg'), W, H, *frags,
           title="Коли ухвалювати рішення: перетин вигоди й ціни відкладання")


def lrm_lineage():
    # Родовід терміна: 4 віхи згори вниз, стрілки-переходи; ліворуч — «домен».
    W, H = 780, 620
    cx = 470                      # центр колонки карток
    frags = []

    # Віхи: (рік, актор, суть) — кожна картка автопідганяється під текст
    stages = [
        ("рання 1990-х",
         "Ґлен Баллард і Ґреґ Гауелл",
         "будівельний майданчик: система Last Planner;\nпотік робіт замість дат"),
        ("1997",
         "Lean Construction Institute",
         "означення в глосарії: LRM — мить, коли\nневирішення прибирає важливу альтернативу"),
        ("2003",
         "Мері й Том Поппендік",
         "книга Lean Software Development: термін\nявно перенесено в софт («вирішувати пізно»)"),
        ("2011",
         "Ребекка Вірфс-Брок",
         "критика зловживання: не «останній», а\n«найвідповідальніший» момент — не прокрастинація"),
    ]

    top = 62
    gap = 138                     # відстань між центрами карток (з запасом на стрілку)
    box_w = 470                   # спільна ширина карток — щоб рядки не тислися
    centers = []
    for i, (yr, who, what) in enumerate(stages):
        cy = top + i * gap
        centers.append(cy)
        # Рамка-картка фіксованої ширини, текст усередині через fitbox
        bx, by = cx - box_w / 2, cy - 46
        frags.append(rect(bx, by, box_w, 92, fill=BG, stroke=FIELD, sw=2, rx=10))
        # Рік — окремим виразним рядком угорі картки
        frags.append(text(cx, by + 24, yr, size=16, color=FIELD, bold=True))
        # Хто
        frags.append(text(cx, by + 46, who, size=14, color=INK, bold=True))
        # Що сталося (2 рядки)
        lines = what.split("\n")
        frags.append(text(cx, by + 66, lines[0], size=12, color=MUTED))
        frags.append(text(cx, by + 82, lines[1], size=12, color=MUTED))

    # Стрілки-переходи між картками (від низу однієї до верху наступної)
    for i in range(len(centers) - 1):
        y1 = centers[i] + 46
        y2 = centers[i + 1] - 46
        frags.append(arrow(cx, y1 + 2, cx, y2 - 2, color=INK, sw=2))

    # Ліворуч — вертикальні смуги «домену»: будівництво (верх) → софт (низ)
    lab_x = 96
    # Будівництво охоплює віхи 0..1
    top_b = centers[0] - 46
    bot_b = centers[1] + 46
    frags.append(line(lab_x + 40, top_b, lab_x + 40, bot_b, color=POS, sw=3))
    b1, bw1, bh1 = textbox(lab_x, (top_b + bot_b) / 2, "ощадливе\nбудівництво",
                           size=13, bold=True, fill="#fdecea", stroke=POS, pad=9)
    frags.append(b1)
    # Софт охоплює віхи 2..3
    top_s = centers[2] - 46
    bot_s = centers[3] + 46
    frags.append(line(lab_x + 40, top_s, lab_x + 40, bot_s, color=NEG, sw=3))
    b2, bw2, bh2 = textbox(lab_x, (top_s + bot_s) / 2, "ощадлива\nрозробка ПЗ",
                           size=13, bold=True, fill="#eaf0fd", stroke=NEG, pad=9)
    frags.append(b2)

    render(os.path.join(OUT, 'lrm-lineage.svg'), W, H, *frags,
           title="Родовід терміна «останній відповідальний момент»")


if __name__ == "__main__":
    lrm_crossover()
    lrm_lineage()
    print("done")
