# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: анатомія прикидки — розклад → множення → перевірка ────────────
def fig_anatomy():
    W, H = 880, 500
    els = []
    els.append(text(W/2, 30, "Прикидка: розкласти · оцінити кожне грубо · перемножити · перевірити", size=16, bold=True))

    cx = W/2

    # Крок 1: питання (вгорі, по центру)
    b1, w1, h1 = textbox(cx, 82, "Питання: скільки?", size=15, bold=True, min_w=280,
                         fill="#eef4ff", stroke=NEG)
    els.append(b1)

    # Крок 2: розклад на множники — три коробки в ряд, з великими проміжками
    fy = 176
    cols = [
        (175, "скільки\nодиниць"),
        (cx,  "× частка,\nщо годиться"),
        (705, "× скільки на одну /\nяк часто"),
    ]
    for bx, txt in cols:
        b2, w2, h2 = textbox(bx, fy, txt, size=13, min_w=210, fill=FILL)
        els.append(b2)
    # стрілка згори вниз у ЛІВУ колонку (повз центральний текст)
    els.append(arrow(cx, 82 + h1/2, 175, fy - 34))
    # позначка розкладу
    els.append(text(cx, fy - 44, "розклад на множники", size=12, color=MUTED, italic=True))

    # Крок 3: множення → результат (стрілка з-під ЛІВОЇ коробки, не через центр)
    ry = 288
    b3, w3, h3 = textbox(cx, ry, "≈ 10ⁿ   —   одна значуща цифра", size=15, bold=True,
                         min_w=400, fill="#eafaf0", stroke=FIELD)
    els.append(b3)
    els.append(arrow(175, fy + 24, cx - w3/2 + 30, ry - h3/2))

    # Крок 4: перевірка — дві гілки вниз, стрілки в БОКИ (не крізь підписи)
    cy = 400
    b4a, wa, ha = textbox(230, cy, "Інший бік:\nсходиться з відомим згори?", size=12,
                          min_w=300, fill="#f7f7f7")
    b4b, wb, hb = textbox(650, cy, "Межі:\nне менше нуля, не більше світу?", size=12,
                          min_w=320, fill="#f7f7f7")
    els.append(b4a)
    els.append(b4b)
    els.append(arrow(cx - 40, ry + h3/2, 230, cy - ha/2))
    els.append(arrow(cx + 40, ry + h3/2, 650, cy - hb/2))
    els.append(text(cx, cy - 4, "перевірка", size=12, color=MUTED, italic=True))

    els.append(text(cx, H-18, "жодне число не мусить бути точним — похибки гасять одна одну", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'anatomy.svg'), W, H, *els)


# ── Фігура 2: драбина затримок (числа Діна) на логарифмічній лінійці ─────────
def fig_latency():
    W, H = 900, 520
    els = []
    els.append(text(W/2, 30, "Драбина затримок: числа, які тримають у голові", size=16, bold=True))

    # Рядки: (назва, наносекунди, людський масштаб)
    rows = [
        ("Звернення до L1-кешу",            0.5,          "0.5 нс"),
        ("Хибний прогноз розгалуження",     5,            "5 нс"),
        ("Звернення до L2-кешу",            7,            "7 нс"),
        ("Захоплення м'ютекса",             25,           "25 нс"),
        ("Звернення до оперативної пам'яті", 100,         "100 нс"),
        ("1 КБ через мережу 1 Гбіт/с",      10_000,       "10 мкс"),
        ("Читання 1 МБ з пам'яті",          250_000,      "0.25 мс"),
        ("Обіг у межах одного ЦОД",         500_000,      "0.5 мс"),
        ("Читання 1 МБ з SSD",              1_000_000,    "1 мс"),
        ("Пошук доріжки на диску (HDD)",    10_000_000,   "10 мс"),
        ("Читання 1 МБ з диску (HDD)",      20_000_000,   "20 мс"),
        ("Пакет Каліфорнія → Європа → назад", 150_000_000, "150 мс"),
    ]

    import math
    left = 40
    label_w = 300
    bar_x0 = left + label_w + 12
    bar_x1 = W - 150
    lo, hi = math.log10(0.5), math.log10(150_000_000)
    def sx(ns):
        return bar_x0 + (math.log10(ns) - lo) / (hi - lo) * (bar_x1 - bar_x0)

    top = 70
    step = 34
    # вісь-підкладка
    els.append(line(bar_x0, top-10, bar_x0, top + len(rows)*step - 10, color="#dddddd", sw=1))
    # мітки порядків на осі
    for p, cap in [(0, "1 нс"), (3, "1 мкс"), (6, "1 мс"), (8, "100 мс")]:
        xx = bar_x0 + (p - lo) / (hi - lo) * (bar_x1 - bar_x0)
        els.append(line(xx, top-14, xx, top + len(rows)*step - 6, color="#eeeeee", sw=1, dash="3,4"))
        els.append(text(xx, top + len(rows)*step + 6, cap, size=11, color=MUTED))

    for i, (name, ns, human) in enumerate(rows):
        y = top + i*step
        els.append(text(left + label_w, y+4, name, size=13, anchor="end"))
        x = sx(ns)
        els.append(line(bar_x0, y, x, y, color=NEG if ns < 1000 else (FIELD if ns < 1_000_000 else POS), sw=3))
        els.append(circle(x, y, 4, fill=BG, stroke=INK, sw=1.5))
        els.append(text(x + 12, y+4, human, size=12, anchor="start", bold=True))

    els.append(text(W/2, H-18, "синє — усередині ядра · зелене — пам'ять/локальна мережа · червоне — диск і далеч; крок праворуч ≈ ×10", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, 'latency.svg'), W, H, *els)


# ── Фігура 3: точність не потрібна — потрібен бік від порога ─────────────────
def fig_threshold():
    W, H = 820, 360
    els = []
    els.append(text(W/2, 30, "Рішення залежить від БОКУ порога, не від точної цифри", size=16, bold=True))

    # горизонтальна вісь-число (лог), поріг посередині
    axis_y = 150
    x0, x1 = 70, W-70
    els.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2))
    els.append(text(x0-6, axis_y+5, "мало", size=12, anchor="end", color=MUTED))
    els.append(text(x1+6, axis_y+5, "багато", size=12, anchor="start", color=MUTED))

    # поріг
    tx = (x0 + x1) / 2
    els.append(line(tx, axis_y-70, tx, axis_y+70, color=INK, sw=2, dash="6,5"))
    b, bw, bh = textbox(tx, axis_y-92, "поріг рішення\n(бюджет / межа)", size=12, bold=True,
                        min_w=210, fill="#fff8e1", stroke="#b8860b")
    els.append(b)

    # діапазон прикидки — брусок із «вусами» (невизначеність), цілком ЛІВОРУЧ порога
    est_lo, est_hi = x0+70, tx-70
    els.append(line(est_lo, axis_y, est_hi, axis_y, color=FIELD, sw=8))
    els.append(line(est_lo, axis_y-9, est_lo, axis_y+9, color=FIELD, sw=3))
    els.append(line(est_hi, axis_y-9, est_hi, axis_y+9, color=FIELD, sw=3))
    els.append(circle((est_lo+est_hi)/2, axis_y, 5, fill=BG, stroke=FIELD, sw=2.5))
    els.append(text((est_lo+est_hi)/2, axis_y+34, "прикидка з усім розкидом", size=12, color=FIELD, bold=True))
    els.append(text((est_lo+est_hi)/2, axis_y+52, "×3 в обидва боки", size=11, color=MUTED, italic=True))

    # висновок
    b2, w2, h2 = textbox((est_lo+est_hi)/2, axis_y+96, "весь брусок ліворуч порога →\nвідповідь однозначна", size=12,
                         bold=True, min_w=320, fill="#eafaf0", stroke=FIELD)
    els.append(b2)

    els.append(text(W/2, H-14, "уточнювати цифру варто, лише коли брусок НАКРИВАЄ поріг", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'threshold.svg'), W, H, *els)


# ── Фігура 4: запис оцінки як конвеєр припущення → число → вироки ────────────
def fig_record_flow():
    W, H = 940, 470
    els = []
    els.append(text(W/2, 30, "Запис оцінки: припущення течуть у число, число проти порогів — у вироки", size=15, bold=True))

    # ── ліва колонка: припущення полями (кожне з одиницею) ──
    ax = 175
    ay0 = 96
    astep = 44
    assumptions = [
        ("записів = 50·10⁶", "шт"),
        ("ключ = 16 Б",       "Б"),
        ("покажчик = 8 Б",    "Б"),
        ("накладні = ×2",     "—"),
    ]
    els.append(text(ax, ay0 - 30, "припущення (з одиницями)", size=12, color=MUTED, italic=True))
    a_boxes = []
    for i, (label, unit) in enumerate(assumptions):
        by = ay0 + i * astep
        b, bw, bh = textbox(ax, by, label, size=13, min_w=230, fill=FILL, stroke=NEG)
        els.append(b)
        a_boxes.append((by, bh))

    # ── центр: чиста функція розкладу ──
    fx = 500
    fy = ay0 + (len(assumptions) - 1) * astep / 2
    bf, fw, fh = textbox(fx, fy, "розклад\n(чиста функція)", size=14, bold=True,
                         min_w=180, fill="#eef4ff", stroke=NEG)
    els.append(bf)
    # стрілки з кожного припущення у функцію
    for by, bh in a_boxes:
        els.append(arrow(ax + 118, by, fx - fw/2, fy + (by - fy) * 0.28))

    # ── число (результат) ──
    nx = 500
    ny = fy + 150
    bn, nw, nh = textbox(nx, ny, "число:  ≈ 2.4 ГБ", size=15, bold=True,
                         min_w=240, fill="#eafaf0", stroke=FIELD)
    els.append(bn)
    els.append(arrow(fx, fy + fh/2, nx, ny - nh/2))

    # ── права колонка: два пороги → два вироки ──
    vx = 800
    # верхній: сервер — влазить
    b1, w1, h1 = textbox(vx, 150, "поріг: 64 ГБ\n(сервер)", size=13, bold=True,
                         min_w=190, fill="#fff8e1", stroke="#b8860b")
    els.append(b1)
    v1, vw1, vh1 = textbox(vx, 226, "ВЛАЗИТЬ\nзапас ×27", size=13, bold=True,
                           min_w=170, fill="#eafaf0", stroke=FIELD, color=FIELD)
    els.append(v1)
    els.append(arrow(vx, 150 + h1/2, vx, 226 - vh1/2))

    # нижній: вбудований — не влазить
    b2, w2, h2 = textbox(vx, 322, "поріг: 256 МБ\n(вбудований)", size=13, bold=True,
                         min_w=190, fill="#fff8e1", stroke="#b8860b")
    els.append(b2)
    v2, vw2, vh2 = textbox(vx, 398, "НЕ ВЛАЗИТЬ\nперевищення ×8", size=13, bold=True,
                           min_w=200, fill="#fdecea", stroke=POS, color=POS)
    els.append(v2)
    els.append(arrow(vx, 322 + h2/2, vx, 398 - vh2/2))

    # число → обидва пороги
    els.append(arrow(nx + nw/2, ny, vx - w1/2, 150 + 8))
    els.append(arrow(nx + nw/2, ny, vx - w2/2, 322 - 8))

    els.append(text(W/2, H-14, "перерахунок = змінити ОДНЕ поле ліворуч; конвеєр сам доведе до вироку", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'record-flow.svg'), W, H, *els)


# ── Фігура 5 (detailed): чому добуток грубих множників точніший за кожен ──────
def fig_error_cancel():
    W, H = 900, 470
    els = []
    els.append(text(W/2, 30, "Чому добуток грубих множників точніший за кожен окремо", size=16, bold=True))
    cx = W/2

    els.append(text(cx, 64, "кожен множник оцінено грубо — одні завеликі, інші замалі", size=12, color=MUTED, italic=True))
    tugs = [(150,'u'),(215,'d'),(280,'d'),(345,'u'),(410,'d'),
            (475,'u'),(540,'u'),(605,'d'),(670,'u'),(735,'d')]
    by = 110
    for x, d in tugs:
        if d == 'u':
            els.append(line(x, by, x, by-26, color=POS, sw=3))
            els.append(circle(x, by-26, 3.2, fill=BG, stroke=POS, sw=1.5))
        else:
            els.append(line(x, by, x, by+26, color=NEG, sw=3))
            els.append(circle(x, by+26, 3.2, fill=BG, stroke=NEG, sw=1.5))
    els.append(line(120, by, 760, by, color="#dddddd", sw=1))
    els.append(text(792, by-10, "завищено", size=11, color=POS, anchor="start"))
    els.append(text(792, by+14, "занижено", size=11, color=NEG, anchor="start"))

    # два бруски-розкиди, центровані на cx
    wy = 224
    els.append(rect(cx-300, wy, 600, 30, fill="#fdecea", stroke=POS, sw=1.5))
    els.append(text(cx, wy-12, "якби похибки складались в один бік: розкид ×N  (10 множників ×1.5 → ×55)", size=12, color=POS))
    ry = 304
    els.append(rect(cx-70, ry, 140, 30, fill="#eafaf0", stroke=FIELD, sw=1.5))
    els.append(text(cx, ry+50, "насправді (гасяться): розкид ×√N  (ті самі 10 множників → лише ×3.5)", size=12, color=FIELD))
    els.append(line(cx-300, wy+30, cx-70, ry, color="#cccccc", sw=1, dash="3,4"))
    els.append(line(cx+300, wy+30, cx+70, ry, color="#cccccc", sw=1, dash="3,4"))

    els.append(text(cx, H-20, "похибки незалежні → у лог-просторі складаються ДИСПЕРСІЇ, тому спред росте як √N, а не N", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'error-cancel.svg'), W, H, *els)


# ── Фігура 6 (detailed): затримка через океан — підлога швидкості світла ──────
def fig_light_floor():
    W, H = 900, 450
    els = []
    els.append(text(W/2, 30, "Затримка через океан — переважно тверда підлога швидкості світла", size=16, bold=True))

    lb, lw, lh = textbox(140, 112, "Каліфорнія", size=14, bold=True, min_w=150, fill=FILL, stroke=NEG)
    rb, rw, rh = textbox(760, 112, "Європа", size=14, bold=True, min_w=150, fill=FILL, stroke=NEG)
    els.append(lb); els.append(rb)

    els.append(line(216, 112, 684, 112, color="#cccccc", sw=1, dash="5,5"))
    els.append(text(450, 96, "по прямій ≈ 9000 км", size=11, color=MUTED))
    els.append('<polyline points="216,124 330,150 470,150 610,148 684,124" fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)
    els.append(text(450, 172, "волокно ≈ 10 000 км", size=11, color=FIELD))

    calc = ("v = c / n = 3·10⁸ / 1.47 ≈ 2·10⁸ м/с   →   ≈ 5 мкс/км\n"
            "10 000 км · 5 мкс/км ≈ 50 мс в один бік   →   ≈ 100 мс туди-й-назад")
    cb, cbw, cbh = textbox(450, 232, calc, size=13, min_w=560, fill="#eef4ff", stroke=NEG)
    els.append(cb)

    by = 302
    bx0, total = 130, 640
    fw = int(total * 100/150)
    els.append(rect(bx0, by, fw, 36, fill="#eafaf0", stroke=FIELD, sw=1.5))
    els.append(rect(bx0+fw, by, total-fw, 36, fill="#fff8e1", stroke="#b8860b", sw=1.5))
    els.append(text(bx0+fw/2, by+22, "фізична межа ≈ 100 мс", size=12, bold=True, color=FIELD))
    els.append(text(bx0+fw+(total-fw)/2, by+22, "маршрут+комутація ≈ 50 мс", size=11, color="#8a6d0b"))
    els.append(text(bx0+total+12, by+22, "= 150 мс", size=13, bold=True, anchor="start"))

    els.append(text(W/2, H-18, "≈100 мс — тверда підлога: інженерія її не прибере; тому балакучий протокол між континентами приречений", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'light-floor.svg'), W, H, *els)


# ── Фігура 7 (detailed): Little's Law — потік крізь систему ───────────────────
def fig_littles_law():
    W, H = 900, 430
    els = []
    els.append(text(W/2, 30, "Little's Law: скільки всередині = темп надходження × час усередині", size=16, bold=True))

    sx0, sy0, sw_, sh_ = 310, 95, 300, 140
    els.append(rect(sx0, sy0, sw_, sh_, fill=FILL, stroke=INK, sw=2))
    els.append(text(sx0+sw_/2, sy0+22, "система", size=13, bold=True, color=MUTED))
    for (x, y) in [(370,150),(420,175),(470,150),(520,176),(560,150),(410,200),(500,200)]:
        els.append(circle(x, y, 9, fill="#eef4ff", stroke=NEG, sw=1.6))

    els.append(arrow(150, 165, sx0-4, 165))
    els.append(text(150, 150, "λ надходять (req/с)", size=12, bold=True, anchor="start"))
    els.append(arrow(sx0+sw_+4, 165, 782, 165))
    els.append(text(694, 150, "виходять", size=12, anchor="start"))

    els.append(text(sx0+sw_/2, sy0+sh_+26, "L — скільки одиниць усередині водночас", size=12, bold=True, color=NEG))
    els.append(text(sx0+sw_/2, sy0+sh_+48, "W — скільки часу кожна проводить усередині", size=12, italic=True, color=MUTED))

    eb, ew, eh = textbox(250, 352, "L = λ · W", size=20, bold=True, min_w=190, fill="#eafaf0", stroke=FIELD)
    els.append(eb)
    wb, ww, wh = textbox(645, 352, "λ = 2000/с · W = 0.05 с\n→ L = 100 у роботі водночас", size=13, bold=True, min_w=320, fill="#eef4ff", stroke=NEG)
    els.append(wb)

    els.append(text(W/2, H-14, "той самий закон дає число потоків, розмір пулу з'єднань і пам'ять під запити в польоті", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'littles-law.svg'), W, H, *els)


# ── Фігура 8 (detailed): коліно черги R = S/(1−ρ) ────────────────────────────
def fig_knee():
    W, H = 900, 500
    els = []
    els.append(text(W/2, 30, "Коліно черги: час відповіді вибухає, коли завантаження йде до 100%", size=16, bold=True))

    x0, x1 = 96, 770
    y0, yb = 90, 410
    R_cap = 20
    def px(r): return x0 + r*(x1-x0)
    def py(R): return yb - min(R, R_cap)/R_cap*(yb-y0)

    els.append(rect(px(0.0), y0, px(0.7)-px(0.0), yb-y0, fill="#f2fbf5", stroke="none", sw=0))
    els.append(rect(px(0.85), y0, px(1.0)-px(0.85), yb-y0, fill="#fdeeec", stroke="none", sw=0))

    els.append(line(x0, yb, x1+22, yb, color=INK, sw=2))
    els.append(line(x0, y0-12, x0, yb, color=INK, sw=2))
    els.append(text(x1+26, yb+5, "ρ→1", size=11, color=MUTED, anchor="start"))

    els.append(text(x0, 52, "час відповіді", size=12, anchor="start"))
    els.append(text(x0, 68, "(× час обслуговування S)", size=11, color=MUTED, anchor="start"))

    for r in [0.0, 0.5, 0.7, 0.9, 1.0]:
        xx = px(r)
        els.append(line(xx, yb, xx, yb+5, color=INK, sw=1))
        els.append(text(xx, yb+20, ("%.1f" % r), size=11, color=MUTED))
    els.append(text((x0+x1)/2, yb+42, "завантаження ρ = λ / пропускна здатність", size=12))

    for R in [1, 2, 5, 10, 20]:
        yy = py(R)
        els.append(line(x0-5, yy, x0, yy, color=INK, sw=1))
        els.append(text(x0-9, yy+4, ("%d" % R), size=11, color=MUTED, anchor="end"))

    poly = []
    r = 0.0
    while r <= 0.951:
        poly.append((px(r), py(1.0/(1.0-r))))
        r += 0.02
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in poly)
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, POS))
    els.append(arrow(px(0.95), py(20)+8, px(0.95), y0-4, color=POS))
    els.append(text(px(0.95)+8, y0+6, "→ ∞", size=12, bold=True, color=POS, anchor="start"))

    for r, R in [(0.5,2),(0.8,5),(0.9,10),(0.95,20)]:
        els.append(circle(px(r), py(R), 4, fill=BG, stroke=POS, sw=2))

    # таблиця-виноска у порожньому верхньому-лівому куті
    tb, tw, th = textbox(215, 176, "ρ=0.5  → ×2\nρ=0.8  → ×5\nρ=0.9  → ×10\nρ=0.95 → ×20\nρ=0.99 → ×100",
                         size=12, min_w=150, fill=BG, stroke=POS)
    els.append(tb)
    els.append(text(690, 366, "коліно черги", size=13, bold=True, color=POS))

    els.append(line(px(0.7), y0, px(0.7), yb, color=FIELD, sw=1.5, dash="5,4"))
    els.append(text(px(0.7), y0-2, "тримай пік нижче ~70%", size=11, color=FIELD))

    els.append(text(W/2, H-16, "R = S / (1 − ρ): запас до 100% — не розкіш, а захист від вибуху черги; сайзинг по коліну, не по середньому", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'knee.svg'), W, H, *els)


# ── Вставка math-queueing: закон Літтла через площу (одиниці-секунди) ─────────
def fig_ll_area():
    W, H = 900, 480
    els = []
    els.append(text(W/2, 30, "Закон Літтла через площу: одиниці-секунди рахуємо двічі", size=16, bold=True))

    axis_y = 300
    t0, t1 = 110, 760
    # смуги-«одиниці»: кожна одиниця живе від приходу до виходу; площа рядка = Wᵢ
    rows = [
        (104, 150, 300, "W₁"),
        (138, 180, 258, "W₂"),
        (172, 220, 470, "W₃"),
        (206, 300, 452, "W₄"),
        (240, 360, 620, "W₅"),
        (274, 470, 700, "W₆"),
    ]
    for cy, xa, xb, lab in rows:
        els.append(rect(xa, cy-9, xb-xa, 18, fill="#eef4ff", stroke=NEG, sw=1.4))
        els.append(text(xb+7, cy+4, lab, size=12, bold=True, anchor="start", color=NEG))

    # вертикальний зріз у момент t*: висота = N(t*)
    tx = 380
    els.append(line(tx, 92, tx, axis_y, color=POS, sw=1.8, dash="6,5"))
    els.append(text(tx, 82, "N(t*) = 3", size=13, bold=True, color=POS))

    # вісь часу
    els.append(line(t0, axis_y, t1, axis_y, color=INK, sw=2))
    els.append(text(t0, axis_y+18, "0", size=12, color=MUTED))
    els.append(text(t1, axis_y+18, "T", size=12, color=MUTED, bold=True))
    els.append(text((t0+t1)/2, axis_y+18, "час", size=12, color=MUTED, italic=True))

    # два читання тієї самої площі
    lb, lw, lh = textbox(248, 356, "рядками:\nплоща = Σ Wᵢ", size=13, min_w=250, fill="#f2fbf5", stroke=FIELD)
    els.append(lb)
    rb, rw, rh = textbox(636, 356, "стовпчиками:\nплоща = ∫ N(t) dt", size=13, min_w=250, fill="#f2fbf5", stroke=FIELD)
    els.append(rb)

    eb, ew, eh = textbox(W/2, 420, "L = (1/T)∫N dt = (приходів/T) · (Σ Wᵢ /приходів) = λ · W", size=14, bold=True, min_w=560, fill="#eafaf0", stroke=FIELD)
    els.append(eb)

    els.append(text(W/2, 466, "жодного припущення про потік, обслуговування чи порядок — тому закон універсальний", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'll-area.svg'), W, H, *els)


# ── Вставка math-queueing: хвіст затримки — середнє проти P99 ─────────────────
def fig_tail():
    import math
    W, H = 900, 470
    els = []
    els.append(text(W/2, 30, "Хвіст затримки: середнє тримає SLA, а користувач живе на P99", size=16, bold=True))

    x0, x1 = 100, 660
    y0, yb = 92, 360
    kmax = 6.0
    def px(k): return x0 + (k/kmax)*(x1-x0)
    def py(dens):  # dens ∈ [0,1] відносно піку
        return yb - dens*(yb-y0)

    # вісь
    els.append(line(x0, yb, x1+16, yb, color=INK, sw=2))
    els.append(line(x0, y0-8, x0, yb, color=INK, sw=2))
    els.append(text(x0, 78, "щільність часу в системі", size=12, anchor="start", color=MUTED, italic=True))
    for k in range(0, 7):
        xx = px(k)
        els.append(line(xx, yb, xx, yb+5, color=INK, sw=1))
        cap = "0" if k == 0 else ("R" if k == 1 else "%dR" % k)
        els.append(text(xx, yb+20, cap, size=11, color=MUTED))
    els.append(text((x0+x1)/2, yb+40, "час у системі (в одиницях середнього R)", size=12))

    # крива щільності (експонента)
    poly = []
    k = 0.0
    while k <= kmax + 1e-9:
        poly.append((px(k), py(math.exp(-k))))
        k += 0.1
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in poly)
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts, NEG))

    # заштрихований хвіст за P99 (k = 4.605 .. kmax)
    kt = math.log(100.0)
    tail = [(px(kt), yb)]
    k = kt
    while k <= kmax + 1e-9:
        tail.append((px(k), py(math.exp(-k))))
        k += 0.1
    tail.append((px(kmax), yb))
    tp = " ".join("%.1f,%.1f" % (x, y) for x, y in tail)
    els.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="1"/>' % (tp, POS))

    # маркер середнього R (k=1)
    els.append(line(px(1), yb, px(1), py(math.exp(-1)), color=INK, sw=1.6, dash="4,4"))
    els.append(text(px(1), py(math.exp(-1))-10, "середнє = R", size=12, bold=True))

    # маркер P99
    els.append(text(px(kt)+6, 150, "P99 ≈ 4.6·R", size=13, bold=True, color=POS, anchor="start"))
    els.append(arrow(px(kt)+40, 158, px(kt)+8, yb-14, color=POS))
    els.append(text(px(kt)+6, 172, "останній 1% — отут", size=11, color=POS, anchor="start"))

    # табличка перцентилів
    tb, tw, th = textbox(792, 205, "P50  ≈ 0.69·R\nP90  ≈ 2.30·R\nP99  ≈ 4.61·R\nP99.9 ≈ 6.91·R", size=13, min_w=180, fill=BG, stroke=NEG)
    els.append(tb)

    els.append(text(W/2, H-16, "R = S/(1−ρ), тож P99 ≈ 4.6·S/(1−ρ): хвіст їде тим самим коліном, лише в 4.6 раза вище", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'tail.svg'), W, H, *els)


# ── Вставка math-queueing: мінливість обслуговування (1+C²)/2 ─────────────────
def fig_pk_variability():
    W, H = 860, 450
    els = []
    els.append(text(W/2, 30, "Мінливість обслуговування множить чергу (Полачек–Хінчин)", size=16, bold=True))

    fb, fw, fh = textbox(W/2, 72, "W_q = [ρ/(1−ρ)] · S · (1+C²)/2", size=15, bold=True, min_w=440, fill="#eef4ff", stroke=NEG)
    els.append(fb)

    yb = 372
    scale = 46.0  # px на одиницю множника
    bars = [
        (190, 0.5, "×0.5", "Детермінований\nC² = 0", FIELD),
        (430, 1.0, "×1.0", "Експоненційний\nC² = 1", NEG),
        (670, 5.0, "×5.0", "Мінливий (H₂)\nC² = 9", POS),
    ]
    els.append(line(90, yb, 790, yb, color=INK, sw=1.5))
    for cx, mult, top, name, col in bars:
        h = mult*scale
        els.append(rect(cx-60, yb-h, 120, h, fill=BG, stroke=col, sw=2))
        els.append(text(cx, yb-h-10, top, size=14, bold=True, color=col))
        els.append(mtext(cx, yb+22, name, size=12, color=INK))

    els.append(text(W/2, H-14, "той самий ρ і S — черга різниться в ×10: зменшити розкид обслуговування = вкоротити хвіст", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'variability.svg'), W, H, *els)


# ── Вставка math-queueing: кілька серверів (M/M/c) пом'якшують коліно ─────────
def fig_mmc():
    W, H = 900, 500
    els = []
    els.append(text(W/2, 30, "Кілька серверів пом'якшують коліно: пул тримає вищий ρ безпечно", size=16, bold=True))

    def erlang_b(c, a):
        B = 1.0
        for k in range(1, c+1):
            B = a*B/(k + a*B)
        return B
    def erlang_c(c, a):
        B = erlang_b(c, a)
        rho = a/c
        return B/(1.0 - rho*(1.0-B))
    def rs(c, rho):
        a = c*rho
        return 1.0 + erlang_c(c, a)/(c*(1.0-rho))

    x0, x1 = 100, 770
    y0, yb = 80, 420
    vmax = 15.0
    def px(r): return x0 + r*(x1-x0)
    def py(v): return yb - (min(v, vmax)-1.0)/(vmax-1.0)*(yb-y0)

    # осі
    els.append(line(x0, yb, x1+18, yb, color=INK, sw=2))
    els.append(line(x0, y0-6, x0, yb, color=INK, sw=2))
    els.append(text(x0, 64, "R / S", size=13, anchor="start", bold=True))
    for r in [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0]:
        xx = px(r)
        els.append(line(xx, yb, xx, yb+5, color=INK, sw=1))
        els.append(text(xx, yb+20, ("%.2f" % r).rstrip("0").rstrip("."), size=11, color=MUTED))
    els.append(text((x0+x1)/2, yb+42, "завантаження на сервер  ρ", size=12))
    for v in [1, 2, 5, 10, 15]:
        yy = py(v)
        els.append(line(x0-5, yy, x0, yy, color=INK, sw=1))
        els.append(text(x0-9, yy+4, "%d" % v, size=11, color=MUTED, anchor="end"))

    series = [(1, POS, "c = 1 (один сервер)"),
              (2, NEG, "c = 2"),
              (4, FIELD, "c = 4"),
              (8, INK, "c = 8 (велика ферма)")]
    for c, col, _lab in series:
        poly = []
        r = 0.01
        while r <= 0.985:
            v = rs(c, r)
            poly.append((px(r), py(v)))
            r += 0.01
        pts = " ".join("%.1f,%.1f" % (x, y) for x, y in poly)
        els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, col))

    # легенда у порожньому верхньому-лівому куті
    lx, ly = 150, 108
    els.append(rect(lx-16, ly-22, 250, 116, fill=BG, stroke="#dddddd", sw=1))
    for i, (c, col, lab) in enumerate(series):
        yy = ly + i*26
        els.append(line(lx, yy, lx+34, yy, color=col, sw=3))
        els.append(text(lx+44, yy+4, lab, size=12, anchor="start"))

    els.append(text(W/2, H-16, "що більший пул, то ближче до 100% можна підходити — правило кореня: запас ≈ √c серверів", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'mmc.svg'), W, H, *els)


# ── Вставка math-error-propagation: √N — рахунок живих клітин матриці коваріацій
def fig_covariance_grid():
    W, H = 900, 470
    els = []
    els.append(text(W/2, 30, "Чому розкид росте як √N: рахунок живих клітин у матриці коваріацій", size=16, bold=True))

    n = 5
    cell = 30
    gw = n * cell

    def grid(gx0, gy0, correlated):
        out = []
        for i in range(n):
            for j in range(n):
                x = gx0 + j * cell
                y = gy0 + i * cell
                if i == j:
                    out.append(rect(x, y, cell, cell, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=0))
                elif correlated:
                    out.append(rect(x, y, cell, cell, fill="#fdecea", stroke=POS, sw=1.1, rx=0))
                else:
                    out.append(rect(x, y, cell, cell, fill=BG, stroke="#dddddd", sw=1, rx=0))
        return out

    lx, ly = 150, 100
    els.append(text(lx + gw/2, ly - 26, "Незалежні похибки", size=14, bold=True, color=FIELD))
    els.extend(grid(lx, ly, correlated=False))
    els.append(text(lx + gw/2, ly + gw + 30, "живі лише N діагональних клітин", size=12))
    els.append(text(lx + gw/2, ly + gw + 52, "Var = N·σ²  →  розкид σ√N", size=13, bold=True, color=FIELD))

    rx, ry = 600, 100
    els.append(text(rx + gw/2, ry - 26, "Змовлені (найгірше)", size=14, bold=True, color=POS))
    els.extend(grid(rx, ry, correlated=True))
    els.append(text(rx + gw/2, ry + gw + 30, "живі всі N² клітин", size=12))
    els.append(text(rx + gw/2, ry + gw + 52, "Var = N²·σ²  →  розкид σN", size=13, bold=True, color=POS))

    mid = 450
    els.append(rect(mid - 12, 158, 18, 18, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=0))
    els.append(text(mid + 14, 166, "діагональ:", size=11, anchor="start", color=MUTED))
    els.append(text(mid + 14, 182, "дисперсія σ²", size=11, anchor="start", color=MUTED))
    els.append(rect(mid - 12, 214, 18, 18, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
    els.append(text(mid + 14, 222, "поза нею:", size=11, anchor="start", color=MUTED))
    els.append(text(mid + 14, 238, "коваріація", size=11, anchor="start", color=MUTED))

    els.append(text(W/2, H-18, "розкид = √(сума живих клітин): √N проти √(N²)=N — увесь виграш у тому, що поза діагоналлю нулі", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'covariance-grid.svg'), W, H, *els)


# ── Вставка math-error-propagation: логнормальна смуга — множник, не «плюс-мінус»
def fig_lognormal_band():
    import math
    W, H = 900, 460
    els = []
    els.append(text(W/2, 30, "Оцінка логнормальна: смуга довіри — це множник ×B / ÷B, а не «плюс-мінус»", size=15, bold=True))

    x0, x1 = 90, 810
    yb, ytop = 300, 92
    xc = (x0 + x1) / 2
    sigmaE = 0.906                   # σ√N для прикладу: N=5, σ=ln1.5≈0.405
    umax = 2.35 * sigmaE

    def ux(u):
        return xc + u / umax * (x1 - xc)

    def bell(u):
        return yb - math.exp(-u*u / (2*sigmaE*sigmaE)) * (yb - ytop)

    def band(u1, u2, fill):
        pts = [(ux(u1), yb)]
        k = 0
        while k <= 48:
            uu = u1 + (u2 - u1) * k / 48
            pts.append((ux(uu), bell(uu)))
            k += 1
        pts.append((ux(u2), yb))
        return '<polygon points="%s" fill="%s" stroke="none"/>' % (
            " ".join("%.1f,%.1f" % p for p in pts), fill)

    els.append(band(-2*sigmaE, 2*sigmaE, "#eef4ff"))
    els.append(band(-sigmaE, sigmaE, "#cfe0fb"))

    poly = []
    u = -umax
    while u <= umax + 1e-9:
        poly.append((ux(u), bell(u)))
        u += umax / 90
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (
        " ".join("%.1f,%.1f" % p for p in poly), NEG))

    els.append(line(x0, yb, x1, yb, color=INK, sw=2))
    els.append(line(xc, yb, xc, bell(0) - 4, color=INK, sw=1.5, dash="4,4"))
    els.append(text(xc, ytop - 10, "ваша оцінка (медіана)", size=12, bold=True))

    ticks = [(-2*sigmaE, "÷6"), (-sigmaE, "÷2.5"), (0, "×1"), (sigmaE, "×2.5"), (2*sigmaE, "×6")]
    for u, lab in ticks:
        els.append(line(ux(u), yb, ux(u), yb + 6, color=INK, sw=1))
        els.append(text(ux(u), yb + 22, lab, size=12))

    y68 = yb + 48
    y95 = yb + 80
    els.append(line(ux(-sigmaE), y68, ux(sigmaE), y68, color=NEG, sw=2))
    els.append(line(ux(-sigmaE), y68 - 5, ux(-sigmaE), y68 + 5, color=NEG, sw=2))
    els.append(line(ux(sigmaE), y68 - 5, ux(sigmaE), y68 + 5, color=NEG, sw=2))
    els.append(text(xc, y68 + 17, "68% — істина в межах ×2.5", size=11, color=NEG))
    els.append(line(ux(-2*sigmaE), y95, ux(2*sigmaE), y95, color=FIELD, sw=2))
    els.append(line(ux(-2*sigmaE), y95 - 5, ux(-2*sigmaE), y95 + 5, color=FIELD, sw=2))
    els.append(line(ux(2*sigmaE), y95 - 5, ux(2*sigmaE), y95 + 5, color=FIELD, sw=2))
    els.append(text(xc, y95 + 17, "95% — істина в межах ×6", size=11, color=FIELD))

    els.append(text(W/2, H-12, "смуга симетрична в лог-просторі → у лінійному це множник; тут N=5 множників по ×1.5 дають 95%-смугу ×6", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, 'lognormal-band.svg'), W, H, *els)


# ── Вставка math-error-propagation: зсув росте як N, розкид — як √N ────────────
def fig_bias_vs_spread():
    import math
    W, H = 900, 470
    els = []
    els.append(text(W/2, 30, "Зсув росте як N, розкид — лише як √N: чому гасіння не бере системну похибку", size=15, bold=True))

    x0, x1 = 90, 790
    yb, ytop = 380, 78
    Nmax = 40
    ymax = 4.2
    sig, mu = 0.4, 0.1

    def px(N):
        return x0 + N / Nmax * (x1 - x0)

    def py(v):
        return yb - v / ymax * (yb - ytop)

    Ncross = 16
    els.append(rect(px(0), ytop, px(Ncross) - px(0), yb - ytop, fill="#f2fbf5", stroke="none", sw=0))
    els.append(rect(px(Ncross), ytop, px(Nmax) - px(Ncross), yb - ytop, fill="#fdeeec", stroke="none", sw=0))

    els.append(line(x0, yb, x1 + 16, yb, color=INK, sw=2))
    els.append(line(x0, ytop - 6, x0, yb, color=INK, sw=2))
    els.append(text(x1 + 20, yb + 5, "N", size=13, anchor="start", bold=True))
    els.append(text(x0 - 4, ytop - 12, "лог-похибка (в одиницях σ, μ)", size=11, anchor="start", color=MUTED))

    for N in [0, 10, 16, 20, 30, 40]:
        els.append(line(px(N), yb, px(N), yb + 5, color=INK, sw=1))
        els.append(text(px(N), yb + 20, str(N), size=11, color=MUTED))
    els.append(text((x0 + x1) / 2, yb + 40, "кількість множників N", size=12))

    def curve(fn, color):
        pts = []
        N = 0.0
        while N <= Nmax + 1e-9:
            pts.append((px(N), py(fn(N))))
            N += 0.5
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (
            " ".join("%.1f,%.1f" % p for p in pts), color)

    els.append(curve(lambda N: sig * math.sqrt(N), NEG))
    els.append(curve(lambda N: mu * N, POS))

    vcross = mu * Ncross
    els.append(line(px(Ncross), ytop, px(Ncross), yb, color=MUTED, sw=1.2, dash="5,4"))
    els.append(circle(px(Ncross), py(vcross), 5, fill=BG, stroke=INK, sw=2))
    els.append(text(px(Ncross), py(vcross) - 14, "N* = 16", size=11, bold=True))

    els.append(text(px(Nmax) + 2, py(mu * Nmax) - 2, "зсув μN", size=12, bold=True, color=POS, anchor="start"))
    els.append(text(px(Nmax) + 2, py(sig * math.sqrt(Nmax)) - 2, "розкид σ√N", size=12, bold=True, color=NEG, anchor="start"))

    els.append(text(px(8), ytop + 34, "розкид більший", size=12, color=NEG, bold=True))
    els.append(text(px(8), ytop + 52, "гасіння працює", size=11, color=MUTED))
    els.append(text(px(29), ytop + 34, "зсув більший", size=12, color=POS, bold=True))
    els.append(text(px(29), ytop + 52, "гасіння безсиле", size=11, color=MUTED))

    els.append(text(W/2, H-16, "перетин при N* = (σ/μ)²; далі праворуч системний зсув переважає випадковий розкид — і росте лінійно", size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, 'bias-vs-spread.svg'), W, H, *els)


if __name__ == '__main__':
    fig_anatomy()
    fig_latency()
    fig_threshold()
    fig_record_flow()
    fig_error_cancel()
    fig_light_floor()
    fig_littles_law()
    fig_knee()
    fig_ll_area()
    fig_tail()
    fig_pk_variability()
    fig_mmc()
    fig_covariance_grid()
    fig_lognormal_band()
    fig_bias_vs_spread()
    print("figs done")


# ── Вставка proj-sensitivity: торнадо чутливості ─────────────────────────────
def fig_tornado():
    W, H = 940, 430
    els = []
    els.append(text(W/2, 28, "Торнадо чутливості: який множник дає найбільше розкиду відповіді", size=16, bold=True))

    # реальні числа з робочого прикладу (піковий трафік, запитів/с): назва, lo, hi
    rows = [
        ("peak_frac", 667, 4000),
        ("actions",  1000, 1667),
        ("sessions", 1111, 1556),
        ("DAU",      1200, 1467),
        ("req",      1333, 1333),
    ]
    NOM, THR = 1333, 2000
    ax_lo, ax_hi = 300, 4300
    bx0, bx1 = 250, 700
    def sx(v): return bx0 + (v - ax_lo) / (ax_hi - ax_lo) * (bx1 - bx0)

    top, step = 96, 54
    yb0, yb1 = top - 32, top + (len(rows) - 1) * step + 32
    els.append(line(sx(NOM), yb0, sx(NOM), yb1, color=MUTED, sw=1.4, dash="5,4"))
    els.append(text(sx(NOM), yb1 + 18, "номінал 1333", size=11, color=MUTED))
    els.append(line(sx(THR), yb0, sx(THR), yb1, color="#b8860b", sw=2))
    els.append(text(sx(THR), yb0 - 8, "поріг: 1 сервер = 2000/с", size=12, bold=True, color="#8a6d0b"))

    labx = 720
    for i, (name, lo, hi) in enumerate(rows):
        y = top + i * step
        els.append(text(238, y + 4, name, size=13, anchor="end", bold=(name == "peak_frac")))
        if lo == hi:
            els.append(circle(sx(lo), y, 5, fill=BG, stroke=MUTED, sw=2))
            els.append(text(labx, y + 4, "Δ = 0 — відомо точно", size=12, color=MUTED, anchor="start"))
        else:
            crosses = lo < THR < hi
            col = POS if crosses else FIELD
            fillc = "#fdecea" if crosses else "#eafaf0"
            els.append(rect(sx(lo), y - 13, sx(hi) - sx(lo), 26, fill=fillc, stroke=col, sw=1.8))
            els.append(text(labx, y + 4, "Δ = %d   (%d…%d)" % (hi - lo, lo, hi), size=12,
                            anchor="start", color=(POS if crosses else INK), bold=crosses))

    els.append(text(W/2, H - 14, "гойдаємо ОДИН множник по його діапазону, решту тримаємо на номіналі; найдовший брусок — той, що варто уточнити чи поміряти", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'tornado.svg'), W, H, *els)


# ── Вставка proj-sensitivity: інтервал vs Монте-Карло vs поріг ────────────────
def fig_spread():
    W, H = 940, 470
    els = []
    els.append(text(W/2, 26, "Інтервал vs Монте-Карло: де насправді ризик перейти поріг", size=16, bold=True))
    els.append(text(W/2, 48, "Монте-Карло: розподіл 100 000 прогонів моделі", size=12, color=MUTED, italic=True))

    x0, x1 = 80, 860
    VMAX = 6800.0
    def sx(v): return x0 + v / VMAX * (x1 - x0)
    ay = 340
    hmax = 200
    THR = 2000

    # гістограма Монте-Карло — РЕАЛЬНІ висоти (32 біни, 300..4300 запитів/с)
    heights = [0.000, 0.001, 0.035, 0.180, 0.369, 0.598, 0.753, 0.899, 1.000, 1.000,
               0.949, 0.932, 0.831, 0.824, 0.741, 0.680, 0.654, 0.581, 0.540, 0.471,
               0.420, 0.374, 0.317, 0.269, 0.230, 0.183, 0.148, 0.117, 0.090, 0.062,
               0.038, 0.027]
    blo, bw = 300.0, 125.0
    for i, hgt in enumerate(heights):
        c = blo + i * bw
        over = (c + bw / 2) > THR
        els.append(rect(sx(c), ay - hgt * hmax, max(1.0, sx(c + bw) - sx(c) - 1), hgt * hmax,
                        fill=("#fdecea" if over else "#eafaf0"),
                        stroke=(POS if over else FIELD), sw=0.8, rx=0))

    # вісь і мітки
    els.append(line(x0, ay, x1, ay, color=INK, sw=2))
    for v in [0, 2000, 4000, 6000]:
        els.append(line(sx(v), ay, sx(v), ay + 5, color=INK, sw=1))
        els.append(text(sx(v), ay + 19, str(v), size=11, color=MUTED))
    els.append(text(x1, ay + 19, "запитів/с", size=11, color=MUTED, anchor="end"))

    # поріг
    els.append(line(sx(THR), ay - hmax - 8, sx(THR), ay + 8, color="#b8860b", sw=2))
    tb, tw, th = textbox(sx(THR), ay - hmax - 24, "поріг 2000/с", size=12, bold=True,
                         min_w=130, fill="#fff8e1", stroke="#b8860b")
    els.append(tb)

    # хвіст P(понад поріг)
    els.append(text(sx(3050), ay - 132, "P(понад поріг)", size=12, bold=True, color=POS))
    els.append(text(sx(3050), ay - 110, "≈ 44%", size=16, bold=True, color=POS))

    # нота про гасіння похибок (у чистій правій зоні над віссю)
    nb, nw, nh = textbox(695, 168, "крайнощі інтервалу\nмайже не трапляються:\nпохибки гасяться (≈ √N)",
                         size=12, min_w=250, fill=BG, stroke=NEG, color=NEG)
    els.append(nb)

    # інтервал (край-край) — вусата лінія під віссю
    wy = ay + 44
    els.append(line(sx(375), wy, sx(6417), wy, color=MUTED, sw=2.5))
    els.append(line(sx(375), wy - 8, sx(375), wy + 8, color=MUTED, sw=2.5))
    els.append(line(sx(6417), wy - 8, sx(6417), wy + 8, color=MUTED, sw=2.5))
    els.append(text(sx(3396), wy + 22, "інтервал (край-край): 375 … 6417 — якби ВСІ похибки змовились одночасно", size=12, color=MUTED))

    els.append(text(W/2, H - 14, "інтервал лякає шириною, але його краї майже неможливі; Монте-Карло показує РЕАЛЬНИЙ ризик — 44% перейти поріг", size=12, color=MUTED, italic=True))
    render(os.path.join(OUT, 'spread.svg'), W, H, *els)


if __name__ == '__main__':
    fig_tornado()
    fig_spread()
    print("proj-sensitivity figs done")
