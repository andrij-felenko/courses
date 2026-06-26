# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── transfer-line: offset зсуває, gain нахиляє; два пункти пришпилюють пряму ───
# Ідея: ідеальна пряма «вхід→вихід» і реальна (зсунута + з іншим нахилом).
# Дві опорні точки калібрування фіксують реальну пряму назад на ідеальну.

def fig_transfer_line():
    W, H = 760, 440
    ox, oy = 70, 360            # початок осей (лівий-нижній)
    aw, ah = 600, 300           # довжина осей

    p = [text(W / 2, 26, "Зсув (offset) і нахил (gain): що ламає й що лагодить калібрування",
              size=15, bold=True)]
    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=LINE, sw=1.8))
    p.append(text(ox - 10, oy - ah - 4, "вихід давача", size=11, color=MUTED, anchor="end"))
    p.append(text(ox + aw + 8, oy + 18, "справжня величина", size=11, color=MUTED, anchor="end"))

    def P(fx, fy):             # частки 0..1 → координати
        return ox + fx * aw, oy - fy * ah

    # ідеальна пряма: вихід = вхід (через початок, нахил 1)
    x0, y0 = P(0.0, 0.0); x1, y1 = P(1.0, 1.0)
    p.append(line(x0, y0, x1, y1, color=FIELD, sw=2.6))
    p.append(text(x1 - 4, y1 - 12, "ідеал: y = x", size=11, color=FIELD, anchor="end", bold=True))

    # реальна пряма: є зсув b=0.18 і нахил k=0.62 (занижує)
    b = 0.18; k = 0.62
    rx0, ry0 = P(0.0, b); rx1, ry1 = P(1.0, b + k * 1.0)
    p.append(line(rx0, ry0, rx1, ry1, color=POS, sw=2.6))
    p.append(text(rx1 + 6, ry1, "реальна:", size=11, color=POS, anchor="start", bold=True))
    p.append(text(rx1 + 6, ry1 + 15, "y = k·x + b", size=11, color=POS, anchor="start"))

    # offset — вертикальна відстань біля нуля
    p.append(line(ox - 0, P(0.0, 0.0)[1], ox - 0, P(0.0, b)[1], color=NEG, sw=2.2))
    p.append(line(ox - 6, P(0.0, b)[1], ox + 6, P(0.0, b)[1], color=NEG, sw=1.2))
    p.append(text(ox + 12, (P(0.0, 0.0)[1] + P(0.0, b)[1]) / 2 + 4, "offset b",
                  size=11, color=NEG, anchor="start", bold=True))

    # gain — різниця нахилів, показано «віялом» праворуч
    gx = 0.78
    p.append(line(*P(gx, k * gx + b), *P(gx, gx), color=NEG, sw=1.4, dash="4,3"))
    p.append(text(P(gx, (k * gx + b + gx) / 2)[0] + 8, P(gx, (k * gx + b + gx) / 2)[1] + 4,
                  "недобір нахилу", size=10, color=NEG, anchor="start"))
    p.append(text(P(gx, (k * gx + b + gx) / 2)[0] + 8, P(gx, (k * gx + b + gx) / 2)[1] + 18,
                  "→ малий gain", size=10, color=NEG, anchor="start"))

    # дві опорні точки калібрування (low ~0.15, high ~0.9)
    for fx, lbl in [(0.15, "опора low"), (0.9, "опора high")]:
        cxr, cyr = P(fx, k * fx + b)        # де реальний давач читає
        cxi, cyi = P(fx, fx)                # де має бути (на ідеалі)
        p.append(circle(cxr, cyr, 6, fill="#fdecea", stroke=POS, sw=2.0))
        p.append(circle(cxi, cyi, 6, fill="#eafaf1", stroke=FIELD, sw=2.0))
        p.append(line(cxr, cyr, cxi, cyi, color=INK, sw=1.0, dash="2,3"))
        p.append(text(cxi, cyi - 12, lbl, size=10, color=INK, bold=True))

    # підпис-висновок
    p.append(text(W / 2, H - 14,
                  "Дві опорні точки дають дві рівняння → з них однозначно k і b, що повертають реальну пряму на ідеал",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "transfer-line.svg"), W, H, *p)


# ── two-point-vs-multi: на кривому давачі пряма між кінцями лишає горб ────────

def fig_two_point_vs_multi():
    W, H = 760, 400
    ox, oy = 70, 320
    aw, ah = 610, 260

    p = [text(W / 2, 26, "Коли пряма бреше: нелінійний давач і два способи його випрямити",
              size=15, bold=True)]
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox + aw + 12, oy, color=LINE, sw=1.8))
    p.append(text(ox - 10, oy - ah - 4, "справжня величина", size=11, color=MUTED, anchor="end"))
    p.append(text(ox + aw + 8, oy + 18, "сирий код давача", size=11, color=MUTED, anchor="end"))

    def P(fx, fy):
        return ox + fx * aw, oy - fy * ah

    # справжня характеристика — вигнута (типова термопара/NTC): корінь-подібна
    def curve(fx):
        return 0.06 + 0.94 * (fx ** 0.62)
    pts = [P(i / 40.0, curve(i / 40.0)) for i in range(41)]
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))
    p.append(text(P(0.7, curve(0.7))[0] + 4, P(0.7, curve(0.7))[1] + 16,
                  "справжня крива давача", size=11, color=INK, anchor="start", bold=True))

    # двоточкова пряма — лише через кінці (0 і 1)
    a0 = P(0.0, curve(0.0)); a1 = P(1.0, curve(1.0))
    p.append(line(*a0, *a1, color=POS, sw=2.2, dash="7,4"))
    p.append(circle(*a0, 5, fill="#fdecea", stroke=POS, sw=2))
    p.append(circle(*a1, 5, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(a1[0] - 4, a1[1] + 18, "двоточкова пряма", size=11, color=POS, anchor="end", bold=True))

    # горб похибки в середині — стрілка між кривою і прямою біля fx=0.42
    fm = 0.42
    cy_curve = P(fm, curve(fm))[1]
    cy_line = oy - (curve(0.0) + (curve(1.0) - curve(0.0)) * fm) * ah
    p.append(line(P(fm, 0)[0], cy_curve, P(fm, 0)[0], cy_line, color=POS, sw=1.6))
    p.append(text(P(fm, 0)[0] - 8, (cy_curve + cy_line) / 2 + 4,
                  "похибка", size=10, color=POS, anchor="end", bold=True))

    # багатоточка — ламана через 5 опор по кривій
    knots = [0.0, 0.25, 0.5, 0.75, 1.0]
    kp = [P(fx, curve(fx)) for fx in knots]
    dd = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in kp)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (dd, FIELD))
    for x, y in kp:
        p.append(circle(x, y, 5, fill="#eafaf1", stroke=FIELD, sw=2))
    p.append(text(P(0.27, curve(0.27))[0], P(0.27, curve(0.27))[1] - 14,
                  "багатоточкова ламана", size=11, color=FIELD, bold=True))

    p.append(text(W / 2, H - 36,
                  "Дві точки фіксують лише кінці — у середині лишається горб; більше опор (або підгонка кривою) тулять",
                  size=11, color=MUTED))
    p.append(text(W / 2, H - 18,
                  "характеристику ближче до правди по всьому діапазону",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "two-point-vs-multi.svg"), W, H, *p)


# ── cal-flow: процедура як конвеєр (умови → опори → розв'язок → NVS → застосунок)

def fig_cal_flow():
    W, H = 900, 430
    p = [text(W / 2, 26, "Процедура калібрування: від опорного еталона до коефіцієнтів у польоті",
              size=15, bold=True)]

    yc = 150
    boxes = [
        (95,  "Умови:\nтемпература,\nживлення,\nпрогрів", "#fff8e1", "#c79100"),
        (270, "Подати відомий\nеталон\n(low і high)", FILL, LINE),
        (445, "Зняти сирий код,\nусереднити\nN відліків", FILL, LINE),
        (620, "Розв'язати\nk і b\n(або таблицю)", "#eafaf1", FIELD),
        (790, "Записати\nкоефіцієнти\nв NVS/EEPROM", "#e8eaf6", NEG),
    ]
    cxs = []
    for cx, txt, fill, stroke in boxes:
        b, bw, bh = textbox(cx, yc, txt, size=11, fill=fill, stroke=stroke, sw=2.0, min_w=120)
        p.append(b)
        cxs.append((cx, bw))
    for i in range(len(cxs) - 1):
        cx, bw = cxs[i]; nx, nbw = cxs[i + 1]
        p.append(arrow(cx + bw / 2, yc, nx - nbw / 2, yc, color=INK))

    # «один раз на виробництві» над першими чотирма
    p.append(line(30, 84, 710, 84, color=MUTED, sw=1.0, dash="5,4"))
    p.append(text(370, 76, "← один раз: на стенді / на виробництві →", size=11, color=MUTED))

    # рантайм-гілка вниз від NVS
    nx, nbw = cxs[-1]
    p.append(arrow(nx, yc + 44, nx, 250, color=NEG))
    rb, rbw, rbh = textbox(nx, 290, "У кожному читанні:\nсирий код → формула\n→ величина у фіз.\nодиницях", size=11,
                           fill="#e8eaf6", stroke=NEG, sw=2.0, min_w=180)
    p.append(rb)
    p.append(line(30, 250, W - 20, 250, color=NEG, sw=1.0, dash="5,4"))
    p.append(text(200, 242, "↓ щоразу в роботі (рантайм) ↓", size=11, color=NEG))

    # формула застосунку
    fb = fitbox(nx - 130, 330, 230, 56, "value = (raw − b) / k\nабо інтерполяція таблиці",
                size=12, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=2.0)
    p.append(fb)

    # ключова пересторога зліва внизу
    wb = fitbox(40, 290, 300, 96,
                "Калібрування = ЗМІРЯТИ похибку\nвідносно еталона.\nЗастосування корекції = окремий крок\n(adjustment). Еталон має бути\nточнішим за давач.",
                size=11, color=POS, fill="#fff5f5", stroke=POS, sw=1.5)
    p.append(wb)

    render(os.path.join(OUT, "cal-flow.svg"), W, H, *p)


# ── error-fan: коридор похибки калібрувальної прямої, вузькі vs широкі опори ──
# Дві панелі. У кожній — пучок прямих, що його дає ±σ на двох опорах:
# між опорами коридор вузький, за ними розкривається (екстраполяція).
# Зліва опори стоять купкою (вузько) → довгі краї на екстраполяції.
# Справа опори ~10% і ~90% → майже весь діапазон в інтерполяції.

def fig_error_fan():
    W, H = 820, 430
    p = [text(W / 2, 26, "Куди ставити опори: коридор похибки прямої вузький МІЖ ними, ширший ЗА ними",
              size=15, bold=True)]

    def panel(ox, title, lo, hi, color):
        oy = 360
        aw, ah = 320, 250
        # осі
        out = [arrow(ox, oy, ox, oy - ah - 10, color=LINE, sw=1.6),
               arrow(ox, oy, ox + aw + 10, oy, color=LINE, sw=1.6),
               text(ox + aw / 2, oy - ah - 16, title, size=12, bold=True, color=color),
               text(ox + aw + 8, oy + 18, "величина", size=10, color=MUTED, anchor="end"),
               text(ox + 2, oy - ah - 2, "код", size=10, color=MUTED, anchor="start")]

        def P(fx, fy):
            return ox + fx * aw, oy - fy * ah

        # робочий діапазон — увесь 0..1; справжня пряма y = 0.10 + 0.80·x
        def yline(fx):
            return 0.10 + 0.80 * fx

        # сім прямих пучка: смикаємо кожну опору на ±σ (вертикальний коридор).
        # Малюємо лише в межах панелі по fy∈[0,1]: круті лінії вузьких опор
        # інакше вибігають за полотно — обрізаємо їх по верх/низ осей.
        sig = 0.045

        def clip_seg(kk, bb):
            # повертає кінці відрізка прямої y=kk·fx+bb, обрізаного по fx∈[0,1] і fy∈[0,1]
            pts = []
            for fx in (0.0, 1.0):                       # перетин з лівим/правим краєм
                fy = kk * fx + bb
                if -1e-9 <= fy <= 1 + 1e-9:
                    pts.append((min(max(fx, 0), 1), min(max(fy, 0), 1)))
            if abs(kk) > 1e-9:
                for fy in (0.0, 1.0):                   # перетин з верхом/низом
                    fx = (fy - bb) / kk
                    if -1e-9 <= fx <= 1 + 1e-9:
                        pts.append((min(max(fx, 0), 1), min(max(fy, 0), 1)))
            return pts[:2] if len(pts) >= 2 else None

        combos = [(+sig, +sig), (+sig, -sig), (-sig, +sig), (-sig, -sig),
                  (+sig, 0), (-sig, 0), (0, +sig), (0, -sig)]
        for dlo, dhi in combos:
            ylo = yline(lo) + dlo
            yhi = yline(hi) + dhi
            kk = (yhi - ylo) / (hi - lo)
            bb = ylo - kk * lo
            seg = clip_seg(kk, bb)
            if seg:
                (fxa, fya), (fxb, fyb) = seg
                out.append(line(*P(fxa, fya), *P(fxb, fyb), color=color, sw=1.0))
        # центральна (істинна) пряма — жирніша
        out.append(line(*P(0.0, yline(0.0)), *P(1.0, yline(1.0)), color=INK, sw=2.2))

        # дві опори з коридором ±σ
        for fx, lbl in [(lo, "опора"), (hi, "опора")]:
            cx, cy = P(fx, yline(fx))
            out.append(line(cx, P(fx, yline(fx) + sig)[1], cx, P(fx, yline(fx) - sig)[1],
                            color=color, sw=2.4))
            out.append(circle(cx, cy, 4.5, fill=BG, stroke=color, sw=2.0))
            out.append(text(cx, oy + 16, "%d%%" % round(fx * 100), size=10, color=color, bold=True))

        # позначити зони: інтерполяція (між) vs екстраполяція (за краями)
        out.append(line(P(lo, 0)[0], oy + 26, P(hi, 0)[0], oy + 26, color=FIELD, sw=2.0))
        out.append(text((P(lo, 0)[0] + P(hi, 0)[0]) / 2, oy + 40, "інтерполяція",
                        size=10, color=FIELD, bold=True))
        if lo > 0.02:
            out.append(line(P(0, 0)[0], oy + 26, P(lo, 0)[0], oy + 26, color=POS, sw=2.0))
        if hi < 0.98:
            out.append(line(P(hi, 0)[0], oy + 26, P(1.0, 0)[0], oy + 26, color=POS, sw=2.0))
        out.append(text(ox + aw / 2, oy + 56, "(червоне = екстраполяція)", size=9, color=POS))
        return out

    p += panel(60, "вузькі опори (≈45% і 55%)", 0.45, 0.55, NEG)
    p += panel(460, "широкі опори (≈10% і 90%)", 0.10, 0.90, FIELD)

    p.append(text(W / 2, H - 12,
                  "Той самий ±σ на опорах: вузько — майже весь діапазон на екстраполяції (похибка велика); широко — в інтерполяції (мала)",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "error-fan.svg"), W, H, *p)


# ── cal-fsm: автомат калібрувального режиму (для proj-вставки) ────────────────
# Лінія успіху WARMUP→…→SAVE→DONE; спільна гілка ABORT від трьох бід.

def fig_cal_fsm():
    W, H = 920, 470
    p = [text(W / 2, 26, "Автомат калібрувального режиму: успіх униз по списку, біда — в ABORT",
              size=15, bold=True)]

    col_x = 250
    states = [
        ("WARMUP",   "прогрів: нуль\nперестав повзти", FILL, LINE),
        ("WAIT_LOW", "оператор ставить\nнижню опору", FILL, LINE),
        ("AVG_LOW",  "усереднити N,\nперевірити розкид", "#fff8e1", "#c79100"),
        ("WAIT_HIGH","оператор ставить\nверхню опору", FILL, LINE),
        ("AVG_HIGH", "усереднити N,\nперевірити розкид", "#fff8e1", "#c79100"),
        ("COMPUTE",  "k, b + перевірка\nздорового глузду", "#eafaf1", FIELD),
        ("SAVE",     "запис у NVS:\nверсія, CRC, 2 слоти", "#eafaf1", FIELD),
        ("DONE",     "коефіцієнти в роботу", "#eafaf1", FIELD),
    ]
    y0, dy = 70, 47
    centers = []
    for i, (name, sub, fill, stroke) in enumerate(states):
        cy = y0 + i * dy
        b, bw, bh = textbox(col_x, cy, name + "\n" + sub, size=10.5,
                            fill=fill, stroke=stroke, sw=1.8, min_w=210)
        p.append(b)
        centers.append((cy, bw, bh))
    for i in range(len(states) - 1):
        cy, bw, bh = centers[i]
        ny = centers[i + 1][0]
        p.append(arrow(col_x, cy + bh / 2, col_x, ny - centers[i + 1][2] / 2, color=FIELD, sw=2.0))

    iy = y0 - dy
    ib, ibw, ibh = textbox(col_x, iy, "IDLE\nстаре калібрування працює", size=10.5,
                           fill="#eef2f7", stroke=MUTED, sw=1.6, min_w=210)
    p.append(ib)
    p.append(arrow(col_x, iy + ibh / 2, col_x, centers[0][0] - centers[0][2] / 2, color=INK, sw=1.8))
    p.append(text(col_x + 130, iy, "старт", size=10, color=MUTED, anchor="start"))

    ax = 660
    ab, abw, abh = textbox(ax, y0 + 4 * dy, "ABORT", size=13,
                           fill="#fff5f5", stroke=POS, sw=2.2, min_w=150)
    p.append(ab)
    p.append(text(ax, y0 + 4 * dy + abh / 2 + 16, "старе калібрування —", size=10, color=POS))
    p.append(text(ax, y0 + 4 * dy + abh / 2 + 30, "НЕДОТОРКАНЕ", size=10, color=POS, bold=True))
    bus_x = ax - abw / 2
    for idx, lbl in [(2, "розкид"), (4, "розкид"), (5, "безглуздя"), (6, "запис")]:
        cy, bw, bh = centers[idx]
        sx = col_x + bw / 2
        midx = (sx + bus_x) / 2
        p.append(line(sx, cy, midx, cy, color=POS, sw=1.6))
        p.append(arrow(midx, cy, bus_x, y0 + 4 * dy, color=POS, sw=1.6))
        p.append(text((sx + midx) / 2, cy - 6, lbl, size=9, color=POS))

    rb, rbw, rbh = textbox(ax, y0 + 7 * dy, "робоче читання:\n(raw − b) / k", size=11,
                           fill="#e8eaf6", stroke=NEG, sw=2.0, min_w=190)
    p.append(rb)
    p.append(arrow(col_x + centers[7][1] / 2, centers[7][0], ax - rbw / 2, y0 + 7 * dy, color=NEG, sw=1.8))
    p.append(text((col_x + ax) / 2, centers[7][0] - 8, "нові коефіцієнти", size=9, color=NEG))
    p.append(arrow(ax, y0 + 4 * dy + abh / 2, ax, y0 + 7 * dy - rbh / 2, color=MUTED, sw=1.4))
    p.append(text(ax + 12, (y0 + 4 * dy + y0 + 7 * dy) / 2, "старі", size=9, color=MUTED, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "Коефіцієнти оновлюються рівно в одній точці — успішному SAVE; будь-яка біда веде в ABORT, не псуючи наявне",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "cal-fsm.svg"), W, H, *p)


# ── cal-store-layout: атомарний запис двома слотами (ping-pong) ───────────────

def fig_cal_store_layout():
    W, H = 880, 470
    p = [text(W / 2, 26, "Атомарний запис коефіцієнтів: розкладка й дві комірки проти brownout",
              size=15, bold=True)]

    fields = [("magic", NEG), ("version", "#c79100"), ("k", FIELD), ("b", FIELD), ("seq", NEG), ("CRC", POS)]
    fx, fy, fw, fh = 90, 56, 116, 40
    p.append(text(W / 2, fy - 8, "один слот cal_store_t:", size=11, color=MUTED))
    for i, (nm, col) in enumerate(fields):
        x = fx + i * fw
        p.append(rect(x, fy, fw - 6, fh, fill="#f4f6f8", stroke=col, sw=2.0))
        p.append(text(x + (fw - 6) / 2, fy + fh / 2 + 5, nm, size=12, color=col, bold=True))
    p.append(text(fx, fy + fh + 18, "magic+version: «моє калібрування мого формату»",
                  size=10, color=MUTED, anchor="start"))
    p.append(text(fx, fy + fh + 33, "CRC покриває все ліворуч → ловить будь-яке псування байтів",
                  size=10, color=MUTED, anchor="start"))

    yrow = 200
    colw = 270
    xs = [60, 60 + colw, 60 + 2 * colw]
    titles = ["1. до запису", "2. пишемо в СТАРІШИЙ (B)", "3. після запису"]

    def slot(cx, cy, name, seq, fill, stroke, note=None, notecol=MUTED):
        b, bw, bh = textbox(cx, cy, "%s  seq=%s" % (name, seq), size=12,
                            fill=fill, stroke=stroke, sw=2.2, min_w=180)
        out = [b]
        if note:
            out.append(text(cx, cy + bh / 2 + 16, note, size=10, color=notecol, bold=True))
        return out

    p.append(text(xs[0] + 90, yrow - 18, titles[0], size=12, bold=True))
    p += slot(xs[0] + 90, yrow + 18, "A", 7, "#eafaf1", FIELD, "чинний (новіший)", FIELD)
    p += slot(xs[0] + 90, yrow + 78, "B", 6, "#eef2f7", MUTED, "старий", MUTED)

    p.append(text(xs[1] + 90, yrow - 18, titles[1], size=12, bold=True))
    p += slot(xs[1] + 90, yrow + 18, "A", 7, "#eafaf1", FIELD, "НЕ чіпаємо", FIELD)
    p += slot(xs[1] + 90, yrow + 78, "B", "8?", "#fff5f5", POS, "пишеться зараз", POS)
    p.append(text(xs[1] + 90, yrow + 122, "⚡ brownout тут → побитий лише B", size=10, color=POS, bold=True))

    p.append(text(xs[2] + 90, yrow - 18, titles[2], size=12, bold=True))
    p += slot(xs[2] + 90, yrow + 18, "B", 8, "#eafaf1", FIELD, "новий чинний", FIELD)
    p += slot(xs[2] + 90, yrow + 78, "A", 7, "#eef2f7", MUTED, "тепер старий", MUTED)

    p.append(arrow(xs[0] + 188, yrow + 48, xs[1] + 2, yrow + 48, color=INK))
    p.append(arrow(xs[1] + 188, yrow + 48, xs[2] + 2, yrow + 48, color=INK))

    wb = fitbox(60, H - 96, W - 120, 60,
                "Читач бере слот із більшим seq, що проходить CRC. Новіший побитий → відкат на старіший ціле.\n"
                "Єдину чинну копію ніколи не перезаписуємо → у пам'яті завжди є хоч одне ціле калібрування.",
                size=11, color=FIELD, fill="#eafaf1", stroke=FIELD, sw=1.5)
    p.append(wb)

    render(os.path.join(OUT, "cal-store-layout.svg"), W, H, *p)


if __name__ == "__main__":
    fig_transfer_line()
    fig_two_point_vs_multi()
    fig_cal_flow()
    fig_error_fan()
    fig_cal_fsm()
    fig_cal_store_layout()
    print("OK: figures generated")
