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


if __name__ == '__main__':
    fig_anatomy()
    fig_latency()
    fig_threshold()
    fig_record_flow()
    print("figs done")
