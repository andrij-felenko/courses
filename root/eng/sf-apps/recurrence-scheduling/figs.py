# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox по центру, повертає (svg, півширина, піввисота)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: два годинники й розрив доби на переході ────────────────────────
def two_clocks_dst():
    W, H = 1040, 430
    p = []
    p.append(text(W / 2, 34, "Два годинники: настінний рівний, абсолютний — ні", size=18, bold=True))

    xs = [300, 560, 820]           # день −1, день переходу, день +1
    days = ["день до\nпереходу", "день\nпереходу", "день\nпісля"]
    bx = 495                        # межа переходу — тісно перед точкою «день переходу», повз написи інтервалів

    # ── настінна смуга ──
    yw = 150
    p.append(line(240, yw, 880, yw, color=MUTED, sw=1.4))
    p.append(text(70, yw - 12, "настінний час", size=13, bold=True, anchor="start"))
    p.append(text(70, yw + 8, "09:00 щодня", size=12, color=MUTED, anchor="start"))
    for i, x in enumerate(xs):
        p.append(circle(x, yw, 6, fill=BG, stroke=INK, sw=1.8))
        p.append(text(x, yw - 16, "09:00", size=13, bold=True))
    # інтервали настінні
    p.append(text((xs[0] + xs[1]) / 2, yw + 24, "+24 год", size=12, color=MUTED))
    p.append(text((xs[1] + xs[2]) / 2, yw + 24, "+24 год", size=12, color=MUTED))

    # ── абсолютна смуга ──
    ya = 300
    p.append(line(240, ya, 880, ya, color=MUTED, sw=1.4))
    p.append(text(70, ya - 12, "абсолютна мить", size=13, bold=True, anchor="start"))
    p.append(text(70, ya + 8, "(UTC)", size=12, color=MUTED, anchor="start"))
    utc = ["07:00", "06:00", "06:00"]
    for i, x in enumerate(xs):
        p.append(circle(x, ya, 6, fill=BG, stroke=FIELD, sw=1.8))
        p.append(text(x, ya - 16, utc[i], size=13, bold=True, color=FIELD))
    # інтервали абсолютні: перший — розрив 23 год
    p.append(text((xs[0] + xs[1]) / 2, ya + 26, "+23 год", size=13, color=POS, bold=True))
    p.append(text((xs[1] + xs[2]) / 2, ya + 26, "+24 год", size=12, color=MUTED))

    # день-підписи під нижньою смугою
    for i, x in enumerate(xs):
        p.append(text(x, ya + 54, days[i].split("\n")[0], size=11, color=MUTED))
        p.append(text(x, ya + 69, days[i].split("\n")[1], size=11, color=MUTED))

    # конектори: та сама 09:00 → різна мить (спиняємо вище написів UTC, щоб не перетинати їх)
    for x in xs:
        p.append(line(x, yw + 10, x, ya - 34, color=MUTED, sw=1.1, dash="4 5"))

    # межа переходу
    p.append(line(bx, 108, bx, ya + 40, color=POS, sw=1.4, dash="5 5"))
    p.append(text(bx, 100, "ніч переходу: 03:00 → 04:00", size=12, color=POS, bold=True))
    p.append(text(bx, 84, "(година зникає)", size=11, color=POS))

    render(os.path.join(IMG, "two-clocks-dst.svg"), W, H, *p)


# ── Фігура 2: правило, розгорнуте по нерівному календарю ─────────────────────
def rule_expand():
    W, H = 1180, 380
    p = []
    p.append(text(W / 2, 34, "Правило, а не список: розгортання по нерівному календарю", size=18, bold=True))

    # правило зверху
    rb, rbw, rbh = box_at(W / 2, 92, "FREQ=MONTHLY;BYMONTHDAY=31",
                          size=14, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, min_w=340)
    p.append(rb)
    p.append(arrow(W / 2, 92 + rbh, W / 2, 172, sw=1.8))
    p.append(text(W / 2 + 150, 150, "розгорнути календарем", size=12, color=MUTED, anchor="start"))

    months = ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"]
    has31 = [True, False, True, False, True, False, True, True, False, True, False, True]
    x0, pitch, yc = 108, 87, 250
    for i, m in enumerate(months):
        cx = x0 + i * pitch
        if has31[i]:
            b, _, _ = box_at(cx, yc, m + "\n31-е", size=13, bold=True,
                             fill="#eaf7ef", stroke=FIELD, min_w=68)
        else:
            b, _, _ = box_at(cx, yc, m + "\nнема", size=13,
                             fill=FILL, stroke=MUTED, color=MUTED, min_w=68)
        p.append(b)

    p.append(text(W / 2, 330,
                  "сім спрацювань на рік — лютий, квітень, червень, вересень, листопад 31-го числа не мають",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "rule-expand.svg"), W, H, *p)


# ── Фігура 3: конвеєр — правило → місцева дата → мить → черга ────────────────
def schedule_pipeline():
    W, H = 1200, 380
    p = []
    p.append(text(W / 2, 34, "Правило — джерело правди; мить вираховують і віддають черзі", size=18, bold=True))

    yb = 205
    b1, w1, h1 = box_at(150, yb, "правило (RRULE)\n+ пояс Europe/Kyiv\n+ початок",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, min_w=220)
    b2, w2, h2 = box_at(455, yb, "наступна дата\n31.03  09:00\n(місцевого)",
                        size=13, bold=True, min_w=190)
    b3, w3, h3 = box_at(760, yb, "абсолютна мить\n06:00 UTC",
                        size=13, bold=True, fill="#eaf7ef", stroke=FIELD, sw=2, min_w=190)
    b4, w4, h4 = box_at(1055, yb, "черга задач →\nробітник виконає\n(ідемпотентно)",
                        size=13, bold=True, min_w=210)
    for b in (b1, b2, b3, b4):
        p.append(b)

    def link(cxa, wa, cxb, wb, label, color=INK):
        p.append(arrow(cxa + wa, yb, cxb - wb, yb, color=color, sw=1.7))
        mx = (cxa + wa + cxb - wb) / 2
        lines = label.split("\n")
        for k, ln in enumerate(lines):
            p.append(text(mx, yb - 26 - (len(lines) - 1 - k) * 15, ln, size=11, color=MUTED))

    link(150, w1, 455, w2, "розгорнути\nу настінному часі")
    link(455, w2, 760, w3, "перевести за базою\nпоясів на цю дату")
    link(760, w3, 1055, w4, "у чергу", color=FIELD)

    p.append(text(150, yb + h1 + 22, "джерело правди", size=12, italic=True, color=MUTED))
    p.append(text(W / 2, 340,
                  "матеріалізуй лише вікно попереду — не весь безкінечний ряд",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "schedule-pipeline.svg"), W, H, *p)


# ── Фігура 4 (вставка hist-tzdata): хроніка бази часових поясів ──────────────
def tzdb_timeline():
    W, H = 1100, 900
    p = []
    p.append(text(W / 2, 36, "Хроніка бази часових поясів", size=18, bold=True))

    ax = 300           # вісь
    bx = 700           # центр рамок подій
    bw = 700           # спільна ширина рамок
    y0, pitch = 118, 96

    rows = [
        ("1986 і раніше", "Артур Девід Олсон збирає правила поясів;\nобмін листами на машині elsie в NIH (США)", MUTED),
        ("від 1996", "Номер випуску — рік і мала літера: 1996a, 2012e, 2022b", MUTED),
        ("30 вересня 2011", "Astrolabe, Inc. подає позов проти Олсона й Еґґерта", POS),
        ("6 жовтня 2011", "FTP-сервер і поштовий список вимкнено", POS),
        ("14 жовтня 2011", "ICANN бере проєкт під опіку, адреса стає tz@iana.org", NEG),
        ("лютий 2012", "Позов відкликано з обіцянкою не позиватися;\nRFC 6557 закріплює порядок супроводу", NEG),
        ("вересень 2021", "Випуск 2021b зливає зони, чиї годинники\nзбігаються від 1970 року", MUTED),
        ("серпень 2022", "Випуск 2022b: Europe/Kiev → Europe/Kyiv", FIELD),
    ]

    ylast = y0 + (len(rows) - 1) * pitch
    p.append(line(ax, y0 - 34, ax, ylast + 34, color=MUTED, sw=1.6))

    for i, (when, what, col) in enumerate(rows):
        y = y0 + i * pitch
        p.append(text(ax - 30, y + 5, when, size=13, bold=True, anchor="end"))
        p.append(circle(ax, y, 7, fill=BG, stroke=col, sw=2.2))
        p.append(line(ax + 10, y, bx - bw / 2 - 8, y, color=MUTED, sw=1.1, dash="4 5"))
        fill = "#f7f8fa" if col is MUTED else (
            "#fdecea" if col is POS else ("#eaf0fd" if col is NEG else "#eaf7ef"))
        b, _, _ = box_at(bx, y, what, size=13, fill=fill, stroke=col, sw=1.8, min_w=bw)
        p.append(b)

    p.append(text(W / 2, ylast + 82,
                  "випуски виходять без розкладу — щойно черговий парламент змінить правило",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "tzdb-timeline.svg"), W, H, *p)


# ── Фігура 5 (вставка hist-tzdata): дорога випуску до застосунку ─────────────
def tzdb_delivery():
    W, H = 1200, 470
    p = []
    p.append(text(W / 2, 36, "Один випуск — багато рук, і кожна зі своєю затримкою", size=18, bold=True))

    ymid = 250
    src, ws, _ = box_at(150, ymid, "випуск tzdb\n(наприклад 2026a)", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=2, min_w=210)
    p.append(src)

    mid_x, mid_w = 620, 430
    hops = [
        (128, "пакет tzdata в операційній системі"),
        (210, "середовище виконання: JVM, ICU"),
        (292, "бібліотеки мов і фреймворків"),
        (374, "Windows: власний перелік + мапа CLDR"),
    ]
    dst, wd, _ = box_at(1040, ymid, "твій застосунок", size=13, bold=True,
                        fill="#eaf7ef", stroke=FIELD, sw=2, min_w=210)
    p.append(dst)

    for y, label in hops:
        b, _, _ = box_at(mid_x, y, label, size=13, min_w=mid_w)
        p.append(b)
        p.append(arrow(150 + ws / 2 + 8, ymid, mid_x - mid_w / 2 - 8, y, color=MUTED, sw=1.5))
        p.append(arrow(mid_x + mid_w / 2 + 8, y, 1040 - wd / 2 - 8, ymid, color=MUTED, sw=1.5))

    p.append(text(W / 2, 438,
                  "поки твоя ланка не оновиться, застосунок рахує за вчорашніми правилами",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "tzdb-delivery.svg"), W, H, *p)


# ── Фігура 6 (вставка proj-expander): набір кандидатів одного періоду ────────
def period_funnel():
    W, H = 1120, 592
    p = []
    p.append(text(W / 2, 36, "Розгортач працює періодом, а не датою", size=18, bold=True))

    rb, rw, rh = box_at(W / 2, 96, "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1",
                        size=14, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, min_w=560)
    p.append(rb)

    bw, cx = 430, 400
    steps = [
        (200, "1. період", "Березень 2026 — усі 31 день", FILL, LINE),
        (320, "2. уточнення", "BYDAY лишає 22 робочі дні:\n02.03 … 31.03", "#f7f8fa", MUTED),
        (440, "3. відбір", "BYSETPOS=−1 бере останній:\n31.03, вівторок", "#eaf7ef", FIELD),
        (540, "4. локалізація", "31.03  18:00 EEST  =  15:00 UTC", "#eaf0fd", NEG),
    ]
    prev_bottom = 96 + rh
    for y, cap, body, fill, stroke in steps:
        p.append(text(cx - bw / 2, y - 40, cap, size=13, bold=True, anchor="start"))
        b, _, bh = box_at(cx, y, body, size=14, bold=True, fill=fill, stroke=stroke,
                          sw=1.8, min_w=bw)
        p.append(b)
        p.append(arrow(cx, prev_bottom + 5, cx, y - bh - 7, sw=1.6))
        prev_bottom = y + bh

    # бічна ремарка — чому відбір потребує ВСЬОГО набору періоду
    nx = 880
    for k, ln in enumerate(["остання п'ятниця березня —",
                            "27.03, а останній робочий —",
                            "31.03. Різні дати, тому крок 3"]):
        p.append(text(nx, 300 + k * 20, ln, size=13, color=MUTED))
    p.append(text(nx, 366, "мусить бачити весь набір", size=13, bold=True))
    p.append(text(nx, 386, "періоду, а не одну дату.", size=13, bold=True))
    p.append(line(cx + bw / 2 + 16, 440, nx - 150, 400, color=MUTED, sw=1.1, dash="4 5"))

    render(os.path.join(IMG, "period-funnel.svg"), W, H, *p)


# ── Фігура 7 (вставка proj-expander): якір INTERVAL ──────────────────────────
def interval_anchor():
    W, H = 1180, 524
    p = []
    p.append(text(W / 2, 36, "Від чого відлічувати INTERVAL: правило чи попереднє спрацювання",
                  size=18, bold=True))
    p.append(text(W / 2, 62, "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=31   від 31.01.2026",
                  size=13, color=MUTED))

    months = ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер", "Вер",
              "Жов", "Лис", "Гру", "Січ", "Лют", "Бер"]
    x0, pitch = 118, 70
    xs = [x0 + i * pitch for i in range(len(months))]

    yA, yB, yAx = 148, 312, 410

    # вісь місяців
    p.append(line(x0 - 34, yAx, xs[-1] + 34, yAx, color=MUTED, sw=1.4))
    for i, m in enumerate(months):
        p.append(line(xs[i], yAx - 5, xs[i], yAx + 5, color=MUTED, sw=1.2))
        p.append(text(xs[i], yAx + 24, m, size=12, color=MUTED))
    p.append(text(xs[0] - 6, yAx + 48, "2026", size=12, bold=True, color=MUTED, anchor="start"))
    p.append(text(xs[12] - 6, yAx + 48, "2027", size=12, bold=True, color=MUTED, anchor="start"))

    # ряд А — якір на правилі (правильно)
    p.append(text(x0 - 52, yA - 38, "якір на правилі: період № 0, 3, 6, 9, 12 від старту",
                  size=13, bold=True, color=FIELD, anchor="start"))
    p.append(line(x0 - 34, yA, xs[-1] + 34, yA, color=MUTED, sw=1.2, dash="3 5"))
    planned = [0, 3, 6, 9, 12]
    hitsA = [0, 6, 9, 12]
    for i in planned:
        p.append(circle(xs[i], yA, 9, fill=BG, stroke=FIELD, sw=1.6))
    for i in hitsA:
        p.append(circle(xs[i], yA, 6, fill=FIELD, stroke=FIELD, sw=1.5))
    p.append(text(xs[3], yA + 32, "у квітні 31-го немає:", size=11, color=POS, bold=True))
    p.append(text(xs[3], yA + 47, "період пропущено,", size=11, color=MUTED))
    p.append(text(xs[3], yA + 62, "сітка не зсунулась", size=11, color=MUTED))

    # ряд Б — якір на попередньому спрацюванні (хибно)
    p.append(text(x0 - 52, yB - 38, "якір на попередньому спрацюванні: «+3 місяці, а як немає — далі»",
                  size=13, bold=True, color=POS, anchor="start"))
    p.append(line(x0 - 34, yB, xs[-1] + 34, yB, color=MUTED, sw=1.2, dash="3 5"))
    hitsB = [0, 4, 7, 11, 14]
    for i in hitsB:
        p.append(circle(xs[i], yB, 6, fill=POS, stroke=POS, sw=1.5))
    for a, b in zip(hitsB, hitsB[1:]):
        p.append(line(xs[a], yB, xs[b], yB, color=POS, sw=1.6))
    p.append(text(xs[4], yB + 32, "фаза з'їхала", size=11, color=POS, bold=True))
    p.append(text(xs[4], yB + 47, "на місяць — назавжди", size=11, color=POS))

    p.append(text(W / 2, 500,
                  "правильно: 31.01 · 31.07 · 31.10 · 31.01 — хибно: 31.01 · 31.05 · 31.08 · 31.12 · 31.03",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "interval-anchor.svg"), W, H, *p)


# ── Вставка api-rrule: порядок застосування BY-полів ─────────────────────────
def rrule_by_order():
    W, H = 1280, 440
    p = []
    p.append(text(W / 2, 34, "Порядок застосування BY-полів — фіксований стандартом", size=18, bold=True))

    y1, y2 = 175, 322

    p.append(text(40, 118, "спершу звужують ДАТУ", size=12, bold=True, color=MUTED, anchor="start"))
    p.append(text(40, 268, "потім — ЧАС доби", size=12, bold=True, color=MUTED, anchor="start"))

    b0, w0, h0 = box_at(120, y1, "FREQ + INTERVAL\nпотік початків\nперіодів",
                        size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, min_w=180)
    p.append(b0)

    row1 = [("BYMONTH", 320), ("BYWEEKNO", 500), ("BYYEARDAY", 680),
            ("BYMONTHDAY", 870), ("BYDAY", 1060)]
    halves1 = []
    for name, cx in row1:
        b, hw, hh = box_at(cx, y1, name, size=13, bold=True, min_w=120)
        p.append(b)
        halves1.append((cx, hw, hh))

    p.append(arrow(120 + w0, y1, halves1[0][0] - halves1[0][1], y1, sw=1.7))
    for i in range(len(halves1) - 1):
        cxa, hwa, _ = halves1[i]
        cxb, hwb, _ = halves1[i + 1]
        p.append(arrow(cxa + hwa, y1, cxb - hwb, y1, sw=1.7))

    row2 = [("BYHOUR", 320), ("BYMINUTE", 500), ("BYSECOND", 680)]
    halves2 = []
    for name, cx in row2:
        b, hw, hh = box_at(cx, y2, name, size=13, bold=True, min_w=120)
        p.append(b)
        halves2.append((cx, hw, hh))
    for i in range(len(halves2) - 1):
        cxa, hwa, _ = halves2[i]
        cxb, hwb, _ = halves2[i + 1]
        p.append(arrow(cxa + hwa, y2, cxb - hwb, y2, sw=1.7))

    # перехід із рядка дат у рядок часу
    ybend = 248
    lx, lhw, lhh = halves1[-1]
    fx, fhw, fhh = halves2[0]
    p.append(line(lx, y1 + lhh, lx, ybend, color=MUTED, sw=1.5))
    p.append(line(lx, ybend, fx, ybend, color=MUTED, sw=1.5))
    p.append(arrow(fx, ybend, fx, y2 - fhh, color=MUTED, sw=1.5))

    # BYSETPOS — останній, над готовим набором періоду
    sx = 990
    bs, shw, shh = box_at(sx, y2, "BYSETPOS", size=13, bold=True,
                          fill="#fdecea", stroke=POS, sw=2, min_w=150)
    p.append(bs)
    lastx, lasthw, _ = halves2[-1]
    p.append(arrow(lastx + lasthw, y2, sx - shw, y2, color=POS, sw=1.7))
    p.append(text((lastx + lasthw + sx - shw) / 2, y2 - 26, "готовий набір", size=11, color=MUTED))
    p.append(text((lastx + lasthw + sx - shw) / 2, y2 - 11, "за один період", size=11, color=MUTED))
    p.append(text(sx, y2 + shh + 24, "вибирає n-й з набору", size=11, color=POS))

    p.append(text(W / 2, 412,
                  "поля в рядку можна писати в будь-якому порядку — застосовуються вони все одно в цьому",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "rrule-by-order.svg"), W, H, *p)


# ── Вставка api-rrule: те саме поле обмежує або розмножує ────────────────────
def rrule_limit_expand():
    W, H = 1180, 440
    p = []
    p.append(text(W / 2, 34, "Одне поле, дві ролі: роль визначає FREQ", size=18, bold=True))
    p.append(line(590, 62, 590, 366, color=MUTED, sw=1.2, dash="5 6"))

    # ── ліворуч: сито ──
    bl, wl, hl = box_at(295, 92, "FREQ=DAILY;BYMONTHDAY=15,30",
                        size=13, bold=True, fill=FILL, stroke=MUTED, min_w=260)
    p.append(bl)
    p.append(text(295, 150, "31 мить, що їх дав FREQ=DAILY", size=12, color=MUTED))

    x0, pitch, yd = 70, 15, 195
    for d in range(1, 32):
        cx = x0 + (d - 1) * pitch
        if d in (15, 30):
            p.append(circle(cx, yd, 6, fill="#eaf7ef", stroke=FIELD, sw=2))
        else:
            p.append(circle(cx, yd, 4, fill=BG, stroke=MUTED, sw=1))
    p.append(text(x0 + 14 * pitch, 174, "15", size=11, bold=True, color=FIELD))
    p.append(text(x0 + 29 * pitch, 174, "30", size=11, bold=True, color=FIELD))
    p.append(text(x0, 218, "1", size=10, color=MUTED))
    p.append(text(x0 + 30 * pitch, 218, "31", size=10, color=MUTED))
    p.append(text(295, 248, "лишилося 2", size=12, bold=True, color=FIELD))
    p.append(arrow(295, 258, 295, 278, sw=1.6))
    b, _, _ = box_at(295, 312, "обмежує (limit)\n31 → 2\nполе просіює наявні миті",
                     size=13, bold=True, fill="#eaf7ef", stroke=FIELD, sw=2, min_w=280)
    p.append(b)

    # ── праворуч: множник ──
    br, wr, hr = box_at(885, 92, "FREQ=MONTHLY;BYMONTHDAY=15,30",
                        size=13, bold=True, fill=FILL, stroke=MUTED, min_w=260)
    p.append(br)
    p.append(circle(885, 152, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(950, 156, "одна мить на місяць", size=11, color=MUTED, anchor="start"))
    p.append(arrow(885, 161, 822, 206, color=NEG, sw=1.5))
    p.append(arrow(885, 161, 948, 206, color=NEG, sw=1.5))
    p.append(circle(818, 213, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(circle(952, 213, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(818, 246, "15-е", size=12, bold=True, color=NEG))
    p.append(text(952, 246, "30-е", size=12, bold=True, color=NEG))
    p.append(arrow(885, 258, 885, 278, sw=1.6))
    b, _, _ = box_at(885, 312, "розмножує (expand)\n1 → 2\nз однієї миті робить кілька",
                     size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, min_w=280)
    p.append(b)

    p.append(text(W / 2, 410,
                  "той самий BYMONTHDAY=15,30: під DAILY — сито, під MONTHLY — множник",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(IMG, "rrule-limit-expand.svg"), W, H, *p)


# ── Фігура (math): березневий зсув року ──────────────────────────────────────
def calendar_march_shift():
    W, H = 1160, 344
    p = []
    p.append(text(W / 2, 34, "Березневий зсув: нерівний місяць переїжджає в кінець року",
                  size=18, bold=True))

    bw, gap, x0 = 76, 4, 150
    pitch = bw + gap

    def row(y, names, lens, hi_idx):
        for i, (nm, ln) in enumerate(zip(names, lens)):
            x = x0 + i * pitch
            cx = x + bw / 2
            if i == hi_idx:
                p.append(rect(x, y, bw, 48, fill="#fdecea", stroke=POS, sw=2))
                p.append(text(cx, y + 20, nm, size=13, bold=True, color=POS))
                p.append(text(cx, y + 38, ln, size=11, bold=True, color=POS))
            else:
                p.append(rect(x, y, bw, 48, fill=FILL, stroke=MUTED, sw=1.2))
                p.append(text(cx, y + 20, nm, size=13, bold=True))
                p.append(text(cx, y + 38, ln, size=11, color=MUTED))

    civ = "Січ Лют Бер Кві Тра Чер Лип Сер Вер Жов Лис Гру".split()
    civ_l = "31 28|29 31 30 31 30 31 31 30 31 30 31".split()
    row(70, civ, civ_l, 1)
    p.append(text(138, 99, "звичайний рік", size=13, bold=True, anchor="end"))

    p.append(text(W / 2, 152,
                  "лютий усередині — його змінна довжина зсуває всі десять наступних місяців",
                  size=13, color=MUTED))

    shf = "Бер Кві Тра Чер Лип Сер Вер Жов Лис Гру Січ Лют".split()
    shf_l = "31 30 31 30 31 31 30 31 30 31 31 28|29".split()
    row(198, shf, shf_l, 11)
    p.append(text(138, 227, "зсунутий рік", size=13, bold=True, anchor="end"))

    offs = [0, 31, 61, 92, 122, 153, 184, 214, 245, 275, 306, 337]
    p.append(text(138, 274, "зсув, діб", size=11, color=NEG, anchor="end"))
    for i, o in enumerate(offs):
        p.append(text(x0 + i * pitch + bw / 2, 274, str(o), size=12, bold=True, color=NEG))

    p.append(text(W / 2, 312,
                  "зсуви місяців стали сталими, а 29 лютого — це просто doy 365, останній номер року",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "calendar-march-shift.svg"), W, H, *p)


# ── Фігура (math): драбина наближень тропічного року ─────────────────────────
def leap_approx_ladder():
    import math
    W, H = 1140, 432
    p = []
    p.append(text(W / 2, 34, "Наближення 0.24219 доби: точність проти довжини циклу",
                  size=18, bold=True))
    p.append(text(W / 2, 62, "довжина смуги — скільки років до похибки в одну добу (шкала логарифмічна)",
                  size=12, color=MUTED))

    rows = [
        ("1/4 · юліанський",        128,     False),
        ("97/400 · григоріанський", 3226,    True),
        ("8/33 · 33-річний цикл",   4269,    False),
        ("218/900 · новоюліанський", 31034,  True),
        ("31/128 · 128-річний цикл", 400000, False),
    ]
    xb, ys, dy, bh = 352, 110, 60, 30
    for i, (lab, yrs, adopted) in enumerate(rows):
        cy = ys + i * dy
        col = NEG if adopted else FIELD
        fil = "#eaf0fd" if adopted else "#eaf7ef"
        w = math.log10(yrs) / 6.0 * 600
        p.append(rect(xb, cy - bh / 2, w, bh, fill=fil, stroke=col, sw=2))
        p.append(text(xb - 12, cy + 5, lab, size=13, bold=True, anchor="end"))
        s = f"{yrs:,}".replace(",", " ")
        p.append(text(xb + w + 12, cy + 5, s + " років", size=13, bold=True, color=col, anchor="start"))

    p.append(rect(352, 388, 16, 14, fill="#eaf7ef", stroke=FIELD, sw=1.6, rx=3))
    p.append(text(376, 400, "підхідний дріб — оптимум за точністю на цю довжину циклу",
                  size=12, color=MUTED, anchor="start"))
    p.append(rect(772, 388, 16, 14, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=3))
    p.append(text(796, 400, "ухвалений календар", size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "leap-approx-ladder.svg"), W, H, *p)


# ── Фігура (math): підтягнути проти пропустити ───────────────────────────────
def clamp_vs_skip():
    W, H = 1180, 374
    p = []
    p.append(text(W / 2, 34, "Дві відповіді на «31 лютого»: підтягнути чи пропустити",
                  size=18, bold=True))
    p.append(line(590, 58, 590, 344, color=MUTED, sw=1.2, dash="5 6"))

    # ── ліворуч: clamp ──
    p.append(text(305, 80, "Підтягнути до останнього дня", size=14, bold=True))
    p.append(arrow(140, 190, 296, 148, color=MUTED, sw=1.5))
    p.append(arrow(365, 140, 462, 140, color=MUTED, sw=1.5))
    p.append(arrow(150, 200, 462, 268, color=MUTED, sw=1.5))
    p.append(text(228, 152, "+1 міс", size=11, color=MUTED))
    p.append(text(414, 128, "+1 міс", size=11, color=MUTED))
    p.append(text(310, 254, "+2 міс", size=11, color=MUTED))
    for cx, cy, s, col in [(140, 190, "31.01", INK), (330, 140, "28.02", MUTED),
                           (500, 140, "28.03", POS), (500, 270, "31.03", POS)]:
        b, _, _ = box_at(cx, cy, s, size=14, bold=True, color=col,
                         fill=BG, stroke=col if col is POS else LINE, sw=1.8, min_w=68)
        p.append(b)
    p.append(text(500, 212, "≠", size=24, bold=True, color=POS))
    p.append(text(305, 330, "той самий старт, різні шляхи — різні відповіді",
                  size=12, color=MUTED))

    # ── праворуч: skip ──
    p.append(text(885, 80, "Пропустити: правило — предикат над номером доби", size=14, bold=True))
    b, _, _ = box_at(885, 132, "P(N): день місяця = 31", size=13, bold=True,
                     fill=FILL, stroke=MUTED, min_w=250)
    p.append(b)
    p.append(line(636, 225, 1140, 225, color=MUTED, sw=1.4))
    marks = [(680, "31.01", True), (760, "лютий", False), (840, "31.03", True),
             (920, "квітень", False), (1000, "31.05", True)]
    for x, lab, hit in marks:
        if hit:
            p.append(circle(x, 225, 8, fill="#eaf7ef", stroke=FIELD, sw=2.2))
            p.append(text(x, 262, lab, size=12, bold=True, color=FIELD))
        else:
            p.append(circle(x, 225, 6, fill=BG, stroke=MUTED, sw=1.4))
            p.append(text(x, 262, lab, size=12, color=MUTED))
            p.append(text(x, 280, "31-го немає", size=11, color=MUTED))
    p.append(text(1092, 225 - 16, "N", size=13, italic=True, color=MUTED))
    p.append(text(885, 330, "кожен N перевіряють окремо — шляху немає",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "clamp-vs-skip.svg"), W, H, *p)


if __name__ == "__main__":
    two_clocks_dst()
    rule_expand()
    schedule_pipeline()
    tzdb_timeline()
    tzdb_delivery()
    period_funnel()
    interval_anchor()
    rrule_by_order()
    rrule_limit_expand()
    calendar_march_shift()
    leap_approx_ladder()
    clamp_vs_skip()
    print("figures written to", IMG)
