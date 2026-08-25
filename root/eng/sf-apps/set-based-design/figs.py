# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _xmark(cx, cy, r=7, color=POS, sw=3):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


def point_vs_set():
    """Точкове (рання ставка → зіткнення → переробка) проти множинного
    (набір звужується обмеженнями до одного живого, без відкоту)."""
    W, H = 880, 470
    f = []

    # ── Верхня доріжка: точкове ──────────────────────────────────────────
    yT = 116
    x_start, x_end = 214, 648
    ttl1, w1, h1 = textbox(92, yT, "точкове\n(рання ставка)", size=12, bold=True,
                           fill="#fdecea", stroke=POS, pad=9)
    f.append(line(x_start, yT, x_end, yT, color=INK, sw=2))
    # старт-ставка
    f.append(circle(258, yT, 7, fill=FIELD, stroke=INK, sw=2))
    b, bw, bh = textbox(258, yT - 44, "рання ставка на A", size=11, fill=BG, stroke=FIELD, pad=7)
    f.append(b)
    # зіткнення
    f.append(_xmark(436, yT, 8, POS, 3))
    b, bw, bh = textbox(436, yT + 46, "факт спростував A", size=11, fill=BG, stroke=POS, pad=7)
    f.append(b)
    # переробка
    f.append(line(444, yT - 6, 618, yT - 6, color=POS, sw=4))
    f.append(arrow(608, yT - 6, 624, yT - 6, color=POS, sw=4))
    f.append(text(532, yT - 16, "переробка на B", size=11, color=POS, bold=True))
    # фініш
    f.append(circle(x_end, yT, 7, fill=BG, stroke=INK, sw=2))
    b, bw, bh = textbox(760, yT, "готово: пізно,\nз переробкою", size=11, fill=BG, stroke=MUTED, pad=8)
    f.append(b)
    f.append(ttl1)

    # ── Нижня доріжка: множинне (три треки) ──────────────────────────────
    yA, yB, yC = 250, 280, 310
    x_e1, x_e2, x_lrm = 384, 508, 700
    ttl2, w2, h2 = textbox(92, yB, "множинне\n(тримати набір)", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, pad=9)
    for yy, lab in ((yA, "A"), (yB, "B"), (yC, "C")):
        f.append(text(196, yy + 4, lab, size=12, color=MUTED, bold=True))
    # A виживає
    f.append(line(x_start, yA, x_lrm, yA, color=FIELD, sw=3))
    f.append(circle(x_lrm, yA, 7, fill=FIELD, stroke=INK, sw=2))
    b, bw, bh = textbox(792, yA, "обрано A:\nбез переробки", size=11, fill=BG, stroke=FIELD, pad=8)
    f.append(b)
    # B відпадає
    f.append(line(x_start, yB, x_e2, yB, color=INK, sw=2))
    f.append(_xmark(x_e2, yB, 6, POS, 2.5))
    # C відпадає
    f.append(line(x_start, yC, x_e1, yC, color=INK, sw=2))
    f.append(_xmark(x_e1, yC, 6, POS, 2.5))
    f.append(ttl2)
    # підписи вибуття — під треками
    b, bw, bh = textbox(x_e1, 360, "обмеження 1\n→ мінус C", size=11, fill=BG, stroke=MUTED, pad=7)
    f.append(b)
    b, bw, bh = textbox(x_e2, 360, "обмеження 2\n→ мінус B", size=11, fill=BG, stroke=MUTED, pad=7)
    f.append(b)
    b, bw, bh = textbox(x_lrm, 360, "збіжність:\nодин живий", size=11, fill="#eafaf0", stroke=FIELD, pad=7)
    f.append(b)

    # ── Вісь часу ────────────────────────────────────────────────────────
    ax_y = 418
    f.append(line(180, ax_y, 812, ax_y, color=INK, sw=2))
    f.append(arrow(802, ax_y, 826, ax_y, color=INK))
    f.append(text(496, ax_y + 24, "час — надходять факти й обмеження →", size=12, color=MUTED))

    render(os.path.join(OUT, 'point-vs-set.svg'), W, H, *f,
           title="Точкове проти множинного: рання ставка чи звуження набору")


def _tcircle(cx, cy, r, color):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.12" '
            'stroke="%s" stroke-width="2.2"/>' % (cx, cy, r, color, color))


def intersection():
    """Три придатні області перекриваються; рішення — у спільному перетині.
    Кандидат, що влаштовує лише дві з трьох, відкидається."""
    W, H = 760, 580
    AMBER = "#c77d18"
    f = []

    # Три області (кола)
    top = (378, 232); bl = (300, 362); br = (456, 362); r = 132
    f.append(_tcircle(*top, r, FIELD))
    f.append(_tcircle(*bl, r, NEG))
    f.append(_tcircle(*br, r, AMBER))

    # Підписи областей — кожен у СВОЇЙ-лише зоні (не в перетині)
    f.append(text(378, 132, "сховище", size=15, color=FIELD, bold=True))
    f.append(text(210, 452, "транспорт", size=15, color=NEG, bold=True))
    f.append(text(548, 452, "бюджет", size=15, color=AMBER, bold=True))

    # Центр — потрійний перетин: рішення
    b, bw, bh = textbox(378, 322, "рішення —\nу перетині", size=13, bold=True,
                        fill=BG, stroke=FIELD, pad=9)
    f.append(b)

    # Відкинутий кандидат: у сховище∩транспорт, поза бюджетом
    ex, ey = 288, 278
    f.append(_xmark(ex, ey, 7, POS, 3))
    lb, lw, lh = textbox(150, 200, "влаштовує 2 з 3:\nне влазить у бюджет\n→ відкинуто",
                         size=11, fill=BG, stroke=POS, pad=8)
    f.append(line(150 + lw / 2, 200 + 6, ex - 8, ey - 6, color=POS, sw=1.3, dash="3,4"))
    f.append(lb)

    # Підпис-висновок унизу
    b, bw, bh = textbox(378, 536,
                        "зайве раннє звуження будь-якої області ризикує лишити перетин порожнім",
                        size=12, fill="#f4f6f8", stroke=MUTED, pad=9)
    f.append(b)

    render(os.path.join(OUT, 'intersection.svg'), W, H, *f,
           title="Інтеграція перетином: рішення там, де області перекриваються")


def when_set_based():
    """Карта 2×2: вартість відкоту × невизначеність. Множинне — лише в куті
    «дорогий відкіт + густий туман»."""
    W, H = 780, 560
    x0, y0, x1, y1 = 150, 96, 690, 476
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    f = []

    # Підсвічений кут — top-right (висока невизначеність + дорогий відкіт)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
             'fill="#27ae60" fill-opacity="0.12" stroke="none"/>'
             % (xm, y0, x1 - xm, ym - y0))

    # Сітка 2×2
    f.append(rect(x0, y0, x1 - x0, y1 - y0, fill="none", stroke=INK, sw=2, rx=8))
    f.append(line(xm, y0, xm, y1, color=INK, sw=1.6))
    f.append(line(x0, ym, x1, ym, color=INK, sw=1.6))

    # Ярлики квадрантів
    tl = ((x0 + xm) / 2, (y0 + ym) / 2)
    tr = ((xm + x1) / 2, (y0 + ym) / 2)
    binl = ((x0 + xm) / 2, (ym + y1) / 2)
    binr = ((xm + x1) / 2, (ym + y1) / 2)
    b, bw, bh = textbox(tl[0], tl[1], "точкове:\nзроби й виправ", size=13, bold=True,
                        fill=BG, stroke=MUTED, pad=9)
    f.append(b)
    b, bw, bh = textbox(tr[0], tr[1], "МНОЖИННЕ\nПРОЄКТУВАННЯ", size=14, bold=True,
                        fill=BG, stroke=FIELD, color=FIELD, pad=10)
    f.append(b)
    b, bw, bh = textbox(binl[0], binl[1], "просто вибери\nзараз", size=13,
                        fill=BG, stroke=MUTED, pad=9)
    f.append(b)
    b, bw, bh = textbox(binr[0], binr[1], "вирішуй свідомо —\nтуману нема", size=13,
                        fill=BG, stroke=MUTED, pad=9)
    f.append(b)

    # Мета-хід: зробити оборотним = зсув уліво (над верхнім рядом, у підсвіченому куті)
    f.append(line(tr[0] + 6, y0 + 30, tl[0] + 46, y0 + 30, color=NEG, sw=1.8, dash="5,4"))
    f.append(arrow(tl[0] + 62, y0 + 30, tl[0] + 44, y0 + 30, color=NEG, sw=1.8))
    f.append(text((tl[0] + tr[0]) / 2 + 8, y0 + 18, "зроби оборотним → зсув уліво",
                  size=11, color=NEG, bold=True))

    # Осі: підписи стовпців (вартість відкоту)
    f.append(text((x0 + xm) / 2, y1 + 24, "дешевий відкіт", size=12, color=MUTED))
    f.append(text((xm + x1) / 2, y1 + 24, "дорогий відкіт", size=12, color=MUTED))
    f.append(text((x0 + x1) / 2, y1 + 48, "вартість відкоту →", size=13, color=INK, bold=True))

    # Осі: підписи рядків (невизначеність)
    f.append(text(x0 - 14, (y0 + ym) / 2, "висока", size=12, color=MUTED, anchor="end"))
    f.append(text(x0 - 14, (ym + y1) / 2, "низька", size=12, color=MUTED, anchor="end"))
    f.append('<text x="46" y="%.1f" font-family="%s" font-size="13" fill="%s" '
             'font-weight="700" text-anchor="middle" transform="rotate(-90 46 %.1f)">'
             'невизначеність, яку можна збити →</text>'
             % ((y0 + y1) / 2, FONT, INK, (y0 + y1) / 2))

    render(os.path.join(OUT, 'when-set-based.svg'), W, H, *f,
           title="Коли розводити набір: дорогий відкіт при густому тумані")


def convergence_journal():
    """Журнал трекера в дії: удавана збіжність на здогаді → відкликання факта
    розширює набір САМО → виміряні факти звужують його до одного живого."""
    W, H = 1080, 570
    AMBER = "#c77d18"
    f = []

    x_open, x_f1, x_ret, x_f2, x_f3, x_dl = 205, 315, 460, 620, 780, 985
    xa, xb = 175, 1010
    yI, yM, yK = 190, 232, 274
    DEAD = "#9aa1ab"

    # ── Смуга подій ──────────────────────────────────────────────────────
    for cx, s, stroke, fill in (
        (x_open, "набір\nвідкрито", MUTED, BG),
        (x_f1,   "F1 · здогад\n«треба точно раз»", POS, "#fdecea"),
        (x_ret,  "F1 ВІДКЛИКАНО\nвимога хибна", NEG, "#eaf0fd"),
        (x_f2,   "F2 · виміряно\nпік 20 000/с", FIELD, "#eafaf0"),
        (x_f3,   "F3 · документ\nбюджет 5 год/тиж", FIELD, "#eafaf0"),
    ):
        b, bw, bh = textbox(cx, 96, s, size=11, fill=fill, stroke=stroke, pad=7)
        f.append(b)
        f.append(line(cx, 96 + bh / 2, cx, 300, color=MUTED, sw=1, dash="2,5"))

    # Дедлайн — стіна праворуч
    b, bw, bh = textbox(x_dl, 96, "дедлайн\nзбіжності", size=11, fill=BG, stroke=AMBER, pad=7)
    f.append(b)
    f.append(line(x_dl, 96 + bh / 2, x_dl, 450, color=AMBER, sw=2, dash="6,5"))

    # ── Три доріжки ──────────────────────────────────────────────────────
    for yy, lab in ((yI, "in-process"), (yM, "managed-queue"), (yK, "kafka")):
        f.append(text(160, yy + 4, lab, size=12, color=INK, anchor="end", bold=True))

    def live(y, x1, x2):
        return line(x1, y, x2, y, color=FIELD, sw=4)

    def dead(y, x1, x2):
        return line(x1, y, x2, y, color=DEAD, sw=1.6, dash="4,4")

    # in-process: живий → вбитий здогадом → воскрес → вбитий виміром
    f.append(live(yI, x_open, x_f1)); f.append(_xmark(x_f1, yI, 6, POS, 2.5))
    f.append(dead(yI, x_f1, x_ret)); f.append(circle(x_ret, yI, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(live(yI, x_ret, x_f2)); f.append(_xmark(x_f2, yI, 6, POS, 2.5))
    f.append(dead(yI, x_f2, xb))

    # managed-queue: той самий провал — і виживає до кінця
    f.append(live(yM, x_open, x_f1)); f.append(_xmark(x_f1, yM, 6, POS, 2.5))
    f.append(dead(yM, x_f1, x_ret)); f.append(circle(x_ret, yM, 5, fill=NEG, stroke=NEG, sw=1))
    f.append(live(yM, x_ret, xb))
    f.append(circle(xb, yM, 7, fill=FIELD, stroke=INK, sw=2))

    # kafka: здогад його НЕ чіпав — вибув на документі
    f.append(live(yK, x_open, x_f3)); f.append(_xmark(x_f3, yK, 6, POS, 2.5))
    f.append(dead(yK, x_f3, xb))

    # ── Лічильник живих по відрізках ─────────────────────────────────────
    f.append(text(160, 324, "живих у наборі:", size=11, color=MUTED, anchor="end"))
    for cx, n, col in ((260, "3", MUTED), (387, "1", POS), (540, "3", NEG),
                       (700, "2", MUTED), (895, "1", FIELD)):
        f.append(circle(cx, 320, 13, fill=BG, stroke=col, sw=2))
        f.append(text(cx, 325, n, size=13, color=col, bold=True))

    # ── Присуди трекера ──────────────────────────────────────────────────
    for cx, s, stroke, fill in (
        (387, "УДАВАНА ЗБІЖНІСТЬ\nживий лише kafka —\nвибуття на здогаді", POS, "#fdecea"),
        (540, "набір розширився САМ\n(стан = згортка)", NEG, "#eaf0fd"),
        (895, "ЗБІГЛОСЯ\nmanaged-queue,\nвибуття доведені", FIELD, "#eafaf0"),
    ):
        b, bw, bh = textbox(cx, 396, s, size=11, fill=fill, stroke=stroke, pad=8)
        f.append(line(cx, 333, cx, 396 - bh / 2, color=stroke, sw=1, dash="3,4"))
        f.append(b)

    # ── Вісь часу ────────────────────────────────────────────────────────
    ax = 470
    f.append(line(xa, ax, 1034, ax, color=INK, sw=2))
    f.append(arrow(1026, ax, 1050, ax, color=INK))
    for cx, d in ((x_open, "01.03"), (x_f1, "02.03"), (x_ret, "20.03"),
                  (x_f2, "28.03"), (x_f3, "10.04"), (x_dl, "15.05")):
        f.append(line(cx, ax - 5, cx, ax + 5, color=INK, sw=1.5))
        f.append(text(cx, ax + 22, d, size=11, color=MUTED))
    f.append(text(590, ax + 48, "час — надходять факти, набір звужується й розширюється →",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'convergence-journal.svg'), W, H, *f,
           title="Журнал збіжності: кожне звуження — за фактом із доказом")


def fix_gate():
    """П'ять станів набору — і лише ОДИН дозволяє фіксувати рішення."""
    W, H = 1010, 540
    AMBER = "#c77d18"
    f = []

    x_cond, x_verd, x_need = 168, 452, 772
    rows = [
        (110, "живих 0", "ПОРОЖНЬО", POS, "#fdecea",
         "перетин порожній: розшир набір\nабо послаб межу — у журналі"),
        (190, "живих > 1,\nдедлайн попереду", "ЗВУЖУЄМО", NEG, "#eaf0fd",
         "нормальний стан: назви факт,\nщо вб'є котрогось, і виміряй"),
        (280, "живих > 1,\nдедлайн минув", "ЗАСТРЯГЛО", AMBER, "#fdf3e3",
         "задарма фактів не буде: обирай\nзараз за аналізом компромісів"),
        (370, "живий 1,\nвибуття на здогаді", "УДАВАНА\nЗБІЖНІСТЬ", POS, "#fdecea",
         "доведи факт або поверни\nваріант у набір — не фіксуй"),
        (460, "живий 1,\nвибуття доведені", "ЗБІГЛОСЯ", FIELD, "#eafaf0",
         "рішення визріло:\nфіксуй і запиши ADR"),
    ]

    for y, cond, verd, col, fill, need in rows:
        b, bw, bh = textbox(x_cond, y, cond, size=11, fill=BG, stroke=MUTED, pad=8)
        f.append(b)
        left_edge = x_cond + bw / 2

        vb, vw, vh = textbox(x_verd, y, verd, size=13, bold=True, fill=fill,
                             stroke=col, color=col, pad=9, min_w=150)
        f.append(arrow(left_edge + 8, y, x_verd - vw / 2 - 8, y, color=MUTED, sw=1.6))
        f.append(vb)

        nb, nw, nh = textbox(x_need, y, need, size=11, fill=FILL, stroke=MUTED, pad=8)
        f.append(arrow(x_verd + vw / 2 + 8, y, x_need - nw / 2 - 8, y, color=MUTED, sw=1.6))
        f.append(nb)

    # Заголовки колонок
    f.append(text(x_cond, 66, "стан набору", size=12, color=INK, bold=True))
    f.append(text(x_verd, 66, "присуд", size=12, color=INK, bold=True))
    f.append(text(x_need, 66, "чого вимагає трекер", size=12, color=INK, bold=True))

    b, bw, bh = textbox(W / 2, 510,
                        "фіксувати дозволено рівно в одному стані з п'яти — у решті трекер каже, "
                        "якої роботи бракує",
                        size=12, fill="#f4f6f8", stroke=MUTED, pad=9)
    f.append(b)

    render(os.path.join(OUT, 'fix-gate.svg'), W, H, *f,
           title="Ворота фіксації: коли набір справді збігся, а коли лише вдає")


def round_trip():
    """Кругова подорож ідеї: народилася в софті (компілятор конструкцій, 1989),
    підтвердилася в металі (Тойота, 1993–99), вернулася в софт (2003)."""
    W, H = 1040, 470
    AMBER = "#c77d18"
    f = []

    y_soft, y_auto = 140, 340
    x89, x93, x95, x99, x03 = 220, 405, 600, 770, 935

    # ── Вузли (спершу рахуємо ширини рамок, щоб провести лінії ПОВЗ них) ──
    nodes = [
        (x89, y_soft, "1989 · компілятор\nконструкцій (MIT)", NEG, "#eaf0fd"),
        (x93, y_auto, "1993 · перша\nпоїздка в Тойоту", AMBER, "#fdf3e3"),
        (x95, y_auto, "1994–95 · назва «SBCE»,\n«другий парадокс»", AMBER, "#fdf3e3"),
        (x99, y_auto, "1999 · три\nпринципи SBCE", AMBER, "#fdf3e3"),
        (x03, y_soft, "2003 · Поппендіки,\n«Amplify Learning»", NEG, "#eaf0fd"),
    ]
    spans = []
    for cx, cy, label, col, bgc in nodes:
        lines_ = label.split("\n")
        bw = max(text_width(ln, 11, True) for ln in lines_) + 2 * 8
        spans.append((cx - bw / 2, cx + bw / 2))

    # ── Дві доріжки: софт і автопром — пунктир розірваний під вузлами ─────
    def _track(y, x_from, x_to, node_spans):
        gap = 8
        cuts = sorted(sp for sp in node_spans if sp[0] < x_to and sp[1] > x_from)
        cursor = x_from
        for lo, hi in cuts:
            if lo - gap > cursor:
                f.append(line(cursor, y, lo - gap, y, color=MUTED, sw=1, dash="4,5"))
            cursor = max(cursor, hi + gap)
        if cursor < x_to:
            f.append(line(cursor, y, x_to, y, color=MUTED, sw=1, dash="4,5"))

    soft_spans = [spans[0], spans[4]]
    auto_spans = [spans[1], spans[2], spans[3]]
    _track(y_soft, 150, 1000, soft_spans)
    _track(y_auto, 150, 1000, auto_spans)
    b, _, _ = textbox(70, y_soft, "СОФТ", size=12, bold=True,
                      fill="#eaf0fd", stroke=NEG, color=NEG, pad=9)
    f.append(b)
    b, _, _ = textbox(70, y_auto, "АВТОПРОМ", size=12, bold=True,
                      fill="#fdf3e3", stroke=AMBER, color=AMBER, pad=9)
    f.append(b)

    # ── Вузли ────────────────────────────────────────────────────────────
    for cx, cy, label, col, bgc in nodes:
        b, bw, bh = textbox(cx, cy, label, size=11, bold=True,
                            fill=bgc, stroke=col, color=INK, pad=8)
        f.append(b)

    # ── Перехід униз: теорія пішла шукати живий приклад ───────────────────
    yb = 250
    f.append(line(x89, y_soft + 22, x89, yb, color=INK, sw=2))
    f.append(line(x89, yb, x93, yb, color=INK, sw=2))
    f.append(arrow(x93, yb, x93, y_auto - 22, color=INK, sw=2))
    b, w1, _ = textbox((x89 + x93) / 2, 208, "теорія пішла\nшукати живий приклад",
                       size=11, fill=BG, stroke=MUTED, color=MUTED, pad=8)
    f.append(b)

    # ── Перехід угору: ідея вертається в софт ────────────────────────────
    f.append(line(x99, y_auto - 22, x99, yb, color=FIELD, sw=2.4))
    f.append(line(x99, yb, x03, yb, color=FIELD, sw=2.4))
    f.append(arrow(x03, yb, x03, y_soft + 22, color=FIELD, sw=2.4))
    b, w2, _ = textbox((x99 + x03) / 2, 208, "ідея вернулась —\nуже «ощадливою»",
                       size=11, fill=BG, stroke=FIELD, color=FIELD, pad=8)
    f.append(b)

    # ── Вісь часу ────────────────────────────────────────────────────────
    f.append(line(150, 410, 980, 410, color=INK, sw=1.6))
    f.append(arrow(970, 410, 1000, 410, color=INK, sw=1.6))
    f.append(text(575, 438, "час →", size=12, color=MUTED))

    # Самоперевірка розкладки: вузли не налазять, підписи влазять у коридори
    for i in range(len(spans) - 1):
        gap = spans[i + 1][0] - spans[i][1]
        assert gap > 12, "вузли %d/%d налазять: зазор %.1f" % (i, i + 1, gap)
    assert w1 < (x93 - x89) - 16, "підпис переходу вниз ширший за коридор"
    assert w2 < (x03 - x99) - 16, "підпис переходу вгору ширший за коридор"

    render(os.path.join(OUT, 'round-trip.svg'), W, H, *f,
           title="Кругова подорож ідеї: з софту в метал і назад у софт")


if __name__ == "__main__":
    point_vs_set()
    intersection()
    when_set_based()
    convergence_journal()
    fix_gate()
    round_trip()
    print("done")
