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


import math


def _poly(pts, color, sw=3, dash=None):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, color, sw, da))


def _xmark(cx, cy, r=7, color=POS, sw=3):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


def marginal_lrm():
    """Гранична форма: вигода зачекати (|p'|·C_r) проти сталих накладних c."""
    W, H = 780, 470
    x0, y0, x1, y1 = 100, 74, 706, 372
    tmax, vmax = 12.0, 13.0
    Cr, carry = 120.0, 4.0
    X = lambda t: x0 + (t / tmax) * (x1 - x0)
    Y = lambda v: y1 - (v / vmax) * (y1 - y0)
    ben = lambda t: 0.1 * Cr * math.exp(-t / 6.0)   # |p'|·C_r, p=0.6·e^(−t/6)
    f = []
    f.append(line(x0, y0 - 8, x0, y1, color=INK, sw=2))
    f.append(line(x0, y1, x1 + 14, y1, color=INK, sw=2))
    f.append(arrow(x1 + 2, y1, x1 + 18, y1, color=INK))
    for v in (4, 8, 12):
        f.append(line(x0 - 5, Y(v), x0, Y(v), color=INK, sw=1.4))
        f.append(text(x0 - 10, Y(v) + 4, str(v), size=11, color=MUTED, anchor="end"))
    for t in (0, 3, 6, 9, 12):
        f.append(line(X(t), y1, X(t), y1 + 5, color=INK, sw=1.4))
        f.append(text(X(t), y1 + 20, str(t), size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, y1 + 42,
                  "тижні від старту  (знань більшає, залежні чекають)",
                  size=12, color=MUTED))
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %.1f)">'
             'люд.-дні за тиждень</text>' % ((y0 + y1) / 2, FONT, MUTED, (y0 + y1) / 2))
    f.append(line(X(0), Y(carry), X(tmax), Y(carry), color=POS, sw=3))
    pts = [(X(i * 0.2), Y(ben(i * 0.2))) for i in range(0, int(tmax / 0.2) + 1)]
    f.append(_poly(pts, NEG, sw=3))
    tstar = 6.0 * math.log(3.0)
    cx, cy = X(tstar), Y(carry)
    f.append(line(cx, cy, cx, y1, color=FIELD, sw=1.6, dash="5,5"))
    f.append(circle(cx, cy, 7, fill=BG, stroke=FIELD, sw=3))
    f.append(text(X(1.35), Y(11.7), "вигода зачекати ще тиждень",
                  size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(X(1.35), Y(10.6), "(на скільки впаде переробка)",
                  size=11, color=NEG, anchor="start"))
    f.append(text(X(9.2), Y(carry) - 15, "ціна тримати рішення відкритим",
                  size=12, color=POS, bold=True))
    box, bw, bh = textbox(470, Y(9.8), "останній\nвідповідальний момент",
                          size=13, bold=True, fill="#eafaf0", stroke=FIELD, pad=9)
    f.append(line(470, Y(9.8) + bh / 2 + 2, cx, cy - 9, color=FIELD, sw=1.4, dash="3,4"))
    f.append(box)
    render(os.path.join(OUT, 'marginal-lrm.svg'), W, H, *f,
           title="Гранична форма правила: коли перестати чекати")


def reversal_cliff():
    """Вартість відкоту росте з адопцією → очікувана переробка мінімальна перед стрибком."""
    W, H = 800, 470
    x0, y0, x1, y1 = 100, 78, 712, 384
    tmax, vmax = 12.0, 120.0
    X = lambda t: x0 + (t / tmax) * (x1 - x0)
    Y = lambda v: y1 - (v / vmax) * (y1 - y0)
    p = lambda t: 0.6 * math.exp(-t / 8.0)
    Cr = lambda t: (30 + 2 * t) if t < 6 else (90 + 2 * t)
    ER = lambda t: p(t) * Cr(t)
    f = []
    f.append(line(x0, y0 - 8, x0, y1, color=INK, sw=2))
    f.append(line(x0, y1, x1 + 14, y1, color=INK, sw=2))
    f.append(arrow(x1 + 2, y1, x1 + 18, y1, color=INK))
    for v in (30, 60, 90, 120):
        f.append(line(x0 - 5, Y(v), x0, Y(v), color=INK, sw=1.4))
        f.append(text(x0 - 10, Y(v) + 4, str(v), size=11, color=MUTED, anchor="end"))
    for t in (0, 3, 6, 9, 12):
        f.append(line(X(t), y1, X(t), y1 + 5, color=INK, sw=1.4))
        f.append(text(X(t), y1 + 20, str(t), size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, y1 + 42, "тижні від старту", size=12, color=MUTED))
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %.1f)">'
             'люд.-дні (вартість)</text>' % ((y0 + y1) / 2, FONT, MUTED, (y0 + y1) / 2))
    xc = X(6.0)
    f.append(line(xc, y0 - 4, xc, y1, color=MUTED, sw=1.6, dash="5,5"))
    f.append(text(xc, y0 - 12, "перший зовнішній клієнт", size=12, color=MUTED, bold=True))
    seg1 = [(X(i * 0.25), Y(Cr(i * 0.25))) for i in range(0, 24)]
    seg1.append((X(5.99), Y(Cr(5.99))))
    seg2 = [(X(6.0 + i * 0.25), Y(Cr(6.0 + i * 0.25))) for i in range(0, 25)]
    f.append(_poly(seg1, POS, sw=3))
    f.append(_poly(seg2, POS, sw=3))
    f.append(line(xc + 2, Y(Cr(5.99)), xc + 2, Y(Cr(6.0)), color=POS, sw=2, dash="3,3"))
    e1 = [(X(i * 0.25), Y(ER(i * 0.25))) for i in range(0, 24)]
    e1.append((X(5.99), Y(ER(5.99))))
    e2 = [(X(6.0 + i * 0.25), Y(ER(6.0 + i * 0.25))) for i in range(0, 25)]
    f.append(_poly(e1, NEG, sw=3))
    f.append(_poly(e2, NEG, sw=3))
    mx, my = X(5.6), Y(ER(5.6))
    f.append(circle(mx, my, 6, fill=BG, stroke=FIELD, sw=3))
    f.append(text(X(9.3), Y(116), "ціна відкоту росте з поширенням",
                  size=12, color=POS, bold=True))
    f.append(text(X(3.2), 372, "очікувана переробка  p·C_r",
                  size=12, color=NEG, bold=True))
    box, bw, bh = textbox(X(2.3), Y(96), "відповідальний момент:\nперед першим клієнтом",
                          size=12, bold=True, fill="#eafaf0", stroke=FIELD, pad=9)
    f.append(line(X(2.3), Y(96) + bh / 2 + 2, mx - 4, my - 6, color=FIELD, sw=1.3, dash="3,4"))
    f.append(box)
    render(os.path.join(OUT, 'reversal-cliff.svg'), W, H, *f,
           title="Коли відкат дорожчає з адопцією, момент настає раніше")


def set_based_convergence():
    """Точкове проти множинного проєктування: коли обрати одразу проти тримати набір."""
    W, H = 840, 448
    f = []
    ax_y = 400
    f.append(line(170, ax_y, 800, ax_y, color=INK, sw=2))
    f.append(arrow(790, ax_y, 814, ax_y, color=INK))
    f.append(text(495, ax_y + 24, "час — надходять факти й обмеження →", size=12, color=MUTED))
    x_start, x_e1, x_e2, x_lrm = 195, 360, 505, 690
    yT = 118
    ttl1, w1, h1 = textbox(92, yT, "точкове\n(обрати одразу)", size=12, bold=True,
                           fill="#fdecea", stroke=POS, pad=8)
    f.append(ttl1)
    f.append(line(x_start, yT, 648, yT, color=INK, sw=2))
    f.append(circle(240, yT, 7, fill=FIELD, stroke=INK, sw=2))
    b, bw, bh = textbox(240, yT - 42, "рання ставка на A", size=11, fill=BG, stroke=FIELD, pad=7)
    f.append(b)
    f.append(_xmark(410, yT, 7, POS, 3))
    b, bw, bh = textbox(410, yT + 44, "факт спростував A", size=11, fill=BG, stroke=POS, pad=7)
    f.append(b)
    f.append(line(412, yT - 4, 600, yT - 4, color=POS, sw=4))
    f.append(arrow(590, yT - 4, 606, yT - 4, color=POS, sw=4))
    f.append(text(505, yT - 14, "переробка на B", size=11, color=POS, bold=True))
    f.append(circle(624, yT, 7, fill=BG, stroke=INK, sw=2))
    b, bw, bh = textbox(724, yT, "готово —\nпізно, з переробкою", size=11, fill=BG, stroke=MUTED, pad=8)
    f.append(b)
    yA, yB, yC = 250, 276, 302
    ttl2, w2, h2 = textbox(92, yB, "множинне\n(тримати набір)", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, pad=8)
    f.append(ttl2)
    for yy, lab in ((yA, "A"), (yB, "B"), (yC, "C")):
        f.append(text(182, yy + 4, lab, size=12, color=MUTED, bold=True))
    f.append(line(x_start, yA, x_lrm, yA, color=FIELD, sw=3))
    f.append(line(x_start, yB, x_e2, yB, color=INK, sw=2))
    f.append(_xmark(x_e2, yB, 6, POS, 2.5))
    f.append(line(x_start, yC, x_e1, yC, color=INK, sw=2))
    f.append(_xmark(x_e1, yC, 6, POS, 2.5))
    f.append(circle(x_lrm, yA, 7, fill=FIELD, stroke=INK, sw=2))
    b, bw, bh = textbox(760, yA, "єдиний живий —\nобрано\nбез переробки", size=11,
                        fill=BG, stroke=FIELD, pad=8)
    f.append(b)
    for xe, lab in ((x_e1, "обмеження 1 → мінус C"), (x_e2, "обмеження 2 → мінус B"),
                    (x_lrm, "LRM: обрано A")):
        f.append(text(xe, 356, lab, size=11, color=MUTED))
    render(os.path.join(OUT, 'set-based-convergence.svg'), W, H, *f,
           title="Точкове проти множинного: як тримати вибір відкритим")


def ledger_lifecycle():
    """Життя одного запису реєстру: open → armed → due → superseded,
    з відбоєм (гасить тремтіння) і лічильником N-поспіль (антидребезг)."""
    W, H = 760, 520
    cx = 300
    f = []
    nodes = [
        (80,  "відкрите\n(open)",       BG,        FIELD),
        (200, "зведене\n(armed)",       "#eafaf0", FIELD),
        (330, "настало\n(due)",         "#fdecea", POS),
        (450, "замінене\n(superseded)", "#f4f6f8", MUTED),
    ]
    boxes = []
    for cy, label, fill, stroke in nodes:
        box, bw, bh = textbox(cx, cy, label, size=14, bold=True,
                              fill=fill, stroke=stroke, pad=11)
        boxes.append((box, bw, bh))
    ys = [n[0] for n in nodes]
    hs = [b[2] for b in boxes]
    ws = [b[1] for b in boxes]

    # Стрілки вниз між станами (малюємо ДО рамок — рамки з фоном перекриють хвости)
    f.append(arrow(cx, ys[0] + hs[0] / 2 + 2, cx, ys[1] - hs[1] / 2 - 2, color=INK, sw=2))
    f.append(arrow(cx, ys[1] + hs[1] / 2 + 2, cx, ys[2] - hs[2] / 2 - 2, color=POS, sw=2))
    f.append(arrow(cx, ys[2] + hs[2] / 2 + 2, cx, ys[3] - hs[3] / 2 - 2, color=INK, sw=2))

    # Підписи переходів — праворуч від стрілок
    f.append(text(cx + 72, (ys[0] + ys[1]) / 2 + 4, "проєкція ≥ arm",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(cx + 72, (ys[1] + ys[2]) / 2 - 5, "проєкція ≥ fire,",
                  size=12, color=POS, anchor="start", bold=True))
    f.append(text(cx + 72, (ys[1] + ys[2]) / 2 + 13, "N вимірів поспіль",
                  size=12, color=POS, anchor="start"))
    f.append(text(cx + 72, (ys[2] + ys[3]) / 2 - 5, "власник обрав опцію,",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(cx + 72, (ys[2] + ys[3]) / 2 + 13, "ADR замінено",
                  size=12, color=MUTED, anchor="start"))

    # Зворотна дуга armed → open (відбій): ліворуч
    lx = 150
    f.append(line(cx - ws[1] / 2, ys[1], lx, ys[1], color=NEG, sw=1.8))
    f.append(line(lx, ys[1], lx, ys[0], color=NEG, sw=1.8))
    f.append(arrow(lx, ys[0], cx - ws[0] / 2, ys[0], color=NEG, sw=1.8))
    f.append(text(lx - 10, (ys[0] + ys[1]) / 2 - 5, "нижче arm —",
                  size=12, color=NEG, anchor="end"))
    f.append(text(lx - 10, (ys[0] + ys[1]) / 2 + 13, "відбій",
                  size=12, color=NEG, anchor="end", bold=True))

    # Рамки станів — поверх стрілок
    for box, bw, bh in boxes:
        f.append(box)

    render(os.path.join(OUT, 'ledger-lifecycle.svg'), W, H, *f,
           title="Життя запису в реєстрі: зведення, стійкість, спрацювання")


def leadtime_forecast():
    """Спрацювати за ПРОГНОЗОМ перетину порогу на L наперед, а не по факту.
    Показано смугу arm..fire (deadband), ряд p99, екстраполяцію та lead time L."""
    W, H = 820, 470
    x0, y0, x1, y1 = 90, 70, 720, 360
    tmax, vmax = 14.0, 240.0
    X = lambda t: x0 + (t / tmax) * (x1 - x0)
    Y = lambda v: y1 - (v / vmax) * (y1 - y0)
    fire, arm = 200.0, 150.0
    f = []

    # Смуга гістерезису arm..fire (позаду всього)
    f.append(rect(x0, Y(fire), x1 - x0, Y(arm) - Y(fire),
                  fill="#eef6f0", stroke="none", sw=0, rx=0))
    # Осі
    f.append(line(x0, y0 - 8, x0, y1, color=INK, sw=2))
    f.append(line(x0, y1, x1 + 14, y1, color=INK, sw=2))
    f.append(arrow(x1 + 2, y1, x1 + 18, y1, color=INK))
    for v in (50, 100, 150, 200):
        f.append(line(x0 - 5, Y(v), x0, Y(v), color=INK, sw=1.4))
        f.append(text(x0 - 10, Y(v) + 4, str(v), size=11, color=MUTED, anchor="end"))
    for t in range(0, 15, 2):
        f.append(line(X(t), y1, X(t), y1 + 5, color=INK, sw=1.4))
        f.append(text(X(t), y1 + 20, str(t), size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, y1 + 40, "тижні від старту", size=12, color=MUTED))
    f.append('<text x="30" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 30 %.1f)">'
             'p99 латентності, мс</text>' % ((y0 + y1) / 2, FONT, MUTED, (y0 + y1) / 2))

    # Пороги
    f.append(line(x0, Y(fire), x1, Y(fire), color=POS, sw=2.4))
    f.append(line(x0, Y(arm), x1, Y(arm), color=MUTED, sw=1.8, dash="6,5"))
    f.append(text(x0 + 6, Y(fire) - 8, "fire = 200 (спрацювання)",
                  size=12, color=POS, anchor="start", bold=True))
    f.append(text(x0 + 6, Y(arm) + 16, "arm = 150 (зведення)",
                  size=12, color=MUTED, anchor="start"))

    # Фактичний ряд p99 (тижні 0..8)
    series = [40, 58, 78, 96, 112, 128, 150, 160, 168]
    pts = [(X(t), Y(series[t])) for t in range(len(series))]
    f.append(_poly(pts, NEG, sw=3))

    tn, slope = 8, 11.0
    tc = tn + (fire - series[tn]) / slope        # 8 + 32/11 ≈ 10.9
    # Екстраполяція (пунктир) від краю ряду
    f.append(_poly([(X(tn), Y(series[tn])), (X(12), Y(series[tn] + slope * 4))],
                   NEG, sw=2, dash="6,5"))
    # Вертикальні провідники: «тепер» і «перетин факту»
    f.append(line(X(tn), Y(series[tn]), X(tn), y1, color=FIELD, sw=1.4, dash="4,4"))
    f.append(line(X(tc), Y(fire), X(tc), y1, color=MUTED, sw=1.4, dash="4,4"))
    # Точки
    f.append(circle(X(tn), Y(series[tn]), 6, fill=FIELD, stroke=INK, sw=2))
    f.append(circle(X(tc), Y(fire), 6, fill=BG, stroke=POS, sw=2.5))
    f.append(text(X(tn) + 8, Y(series[tn]) - 8, "тепер (тижд. 8)",
                  size=11, color=MUTED, anchor="start"))
    f.append(text(X(tc) + 6, Y(fire) + 18, "перетин факту (≈11)",
                  size=11, color=POS, anchor="start"))
    # Дужка lead time L
    yb = Y(220)
    f.append(line(X(tn), yb, X(tc), yb, color=INK, sw=1.6))
    f.append(line(X(tn), yb - 5, X(tn), yb + 5, color=INK, sw=1.6))
    f.append(line(X(tc), yb - 5, X(tc), yb + 5, color=INK, sw=1.6))
    f.append(text((X(tn) + X(tc)) / 2, yb - 8, "L ≈ 3 тижні",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'leadtime-forecast.svg'), W, H, *f,
           title="Спрацювати за прогнозом перетину, а не по факту")


def binomial_option():
    """Відкладання як кол-опціон: одно-кроковий біноміальний розрахунок вартості чекання."""
    W, H = 900, 512
    f = []
    R = (150, 250)    # корінь-рішення
    F = (432, 140)    # вузол «зафіксувати зараз»
    Wt = (432, 338)   # вузол «чекати»
    P = (760, 140)    # payoff зафіксувати
    U = (762, 250)    # результат: підтвердив
    D = (762, 424)    # результат: спростував
    # гілки-лінії (кінці — біля дрібних вузлів/країв рамок, не під написами)
    f.append(line(R[0], R[1], F[0], F[1], color=INK, sw=2))
    f.append(line(R[0], R[1], Wt[0], Wt[1], color=INK, sw=2))
    f.append(line(Wt[0] + 6, Wt[1] - 4, U[0] - 66, U[1] + 6, color=INK, sw=2))
    f.append(line(Wt[0] + 6, Wt[1] + 4, D[0] - 66, D[1] - 6, color=INK, sw=2))
    f.append(arrow(F[0] + 7, F[1], P[0] - 64, F[1], color=INK, sw=2))
    # вузли-кола
    f.append(circle(R[0], R[1], 8, fill=FIELD, stroke=INK, sw=2))
    f.append(circle(F[0], F[1], 7, fill=BG, stroke=INK, sw=2))
    f.append(circle(Wt[0], Wt[1], 7, fill=BG, stroke=INK, sw=2))
    # підпис кореня — ЛІВОРУЧ (порожньо)
    b, bw, bh = textbox(86, 250, "момент t\n(відкрито)", size=12, bold=True,
                        fill="#eafaf0", stroke=FIELD, pad=8)
    f.append(b)
    # підписи вузлів: «зафіксувати» — зверху, «чекати» — знизу
    f.append(text(F[0], F[1] - 20, "зафіксувати зараз", size=13, color=INK, bold=True))
    f.append(text(Wt[0], Wt[1] + 38, "чекати · c = 4", size=13, color=NEG, bold=True))
    # payoff зафіксувати
    pb, pw, ph = textbox(P[0], P[1], "очікувана\nпереробка = 72", size=12,
                         fill="#fdecea", stroke=POS, pad=9)
    f.append(pb)
    # два результати досліду
    ub, uw, uh = textbox(U[0], U[1], "підтвердив 0.6\np=0.1 → 12", size=12,
                         fill=BG, stroke=FIELD, pad=9)
    f.append(ub)
    db, dw, dh = textbox(D[0], D[1], "спростував 0.4\np=0.5 → 60", size=12,
                         fill=BG, stroke=FIELD, pad=9)
    f.append(db)
    # вердикт-смуга внизу
    vb, vw, vh = textbox(432, 484,
                         "тримати 35.2  <  зафіксувати 72   →   опціон вартий 36.8",
                         size=13, bold=True, fill="#f4f6f8", stroke=INK, pad=9)
    f.append(vb)
    render(os.path.join(OUT, 'binomial-option.svg'), W, H, *f,
           title="Відкладання як кол-опціон: тримати чи виконати")


def tstar_vs_learning():
    """t* як функція темпу навчання λ — горб, а не схил."""
    W, H = 820, 470
    x0, y0, x1, y1 = 104, 74, 742, 384
    lam_max, t_max = 0.6, 8.0
    X = lambda l: x0 + (l / lam_max) * (x1 - x0)
    Y = lambda t: y1 - (t / t_max) * (y1 - y0)

    def tstar(l):
        v = 18.0 * l
        return math.log(v) / l if v > 1.0 else 0.0

    f = []
    f.append(line(x0, y0 - 8, x0, y1, color=INK, sw=2))
    f.append(line(x0, y1, x1 + 14, y1, color=INK, sw=2))
    f.append(arrow(x1 + 2, y1, x1 + 18, y1, color=INK))
    for t in (2, 4, 6, 8):
        f.append(line(x0 - 5, Y(t), x0, Y(t), color=INK, sw=1.4))
        f.append(text(x0 - 12, Y(t) + 4, str(t), size=11, color=MUTED, anchor="end"))
    for l in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        f.append(line(X(l), y1, X(l), y1 + 5, color=INK, sw=1.4))
        f.append(text(X(l), y1 + 20, ("%.1f" % l), size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, y1 + 42, "темп навчання  λ  (як швидко рідшає туман) →",
                  size=12, color=MUTED))
    f.append('<text x="34" y="%.1f" font-family="%s" font-size="12" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %.1f)">'
             'відповідальний момент t* (тижнів)</text>'
             % ((y0 + y1) / 2, FONT, MUTED, (y0 + y1) / 2))
    # крива-горб
    pts = [(X(i / 100.0), Y(tstar(i / 100.0))) for i in range(2, 61)]
    f.append(_poly(pts, NEG, sw=3))
    # база λ=1/6
    lb = 1.0 / 6.0
    bx, by = X(lb), Y(tstar(lb))
    f.append(line(bx, by, bx, y1, color=FIELD, sw=1.5, dash="5,5"))
    f.append(circle(bx, by, 6, fill=BG, stroke=FIELD, sw=3))
    bb, bw, bh = textbox(X(0.075), Y(7.4), "база λ=1/6\nt*≈6.6", size=12, bold=True,
                         fill="#eafaf0", stroke=FIELD, pad=8)
    f.append(line(X(0.075), Y(7.4) + bh / 2 + 2, bx - 6, by - 6,
                  color=FIELD, sw=1.2, dash="3,4"))
    f.append(bb)
    # пік — зверху-праворуч (порожньо над спадним боком)
    pk, pw, ph = textbox(X(0.34), Y(7.5), "найдовше варто чекати —\nпосередині",
                         size=12, fill=BG, stroke=MUTED, pad=8)
    f.append(pk)
    # швидке навчання — низ-право, під кривою
    sb, sw2, sh = textbox(X(0.47), Y(1.7), "швидке навчання:\nпотрібне взнаєш рано",
                          size=12, fill=BG, stroke=MUTED, pad=8)
    f.append(line(X(0.47), Y(1.7) - sh / 2 - 2, X(0.52), Y(tstar(0.52)) + 6,
                  color=MUTED, sw=1.2, dash="3,4"))
    f.append(sb)
    # мляве навчання — низ-ліво (лівіше базової пунктирної вертикалі)
    f.append(text(X(0.045), Y(0.6), "мляве: чекати марно", size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'tstar-vs-learning.svg'), W, H, *f,
           title="Момент проти темпу навчання: не схил, а горб")


if __name__ == "__main__":
    lrm_crossover()
    lrm_lineage()
    marginal_lrm()
    reversal_cliff()
    set_based_convergence()
    ledger_lifecycle()
    leadtime_forecast()
    binomial_option()
    tstar_vs_learning()
    print("done")
