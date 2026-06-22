# -*- coding: utf-8 -*-
# Фігури теми «Тактовий сигнал». svgkit імпортуємо, не переписуємо (§5 AUTHORING).
# Вивід — у ./img/, імена — slug без номерів. Після запуску: python ../../../../scripts/svgcheck.py img
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#b8862b"   # бурштиновий акцент (перекіс, кераміка)


def square_wave(x0, y_lo, y_hi, period, n, sw=2.3, color=INK, start_high=False):
    """Прямокутна хвиля з n півперіодами завширшки period/2 кожен."""
    half = period / 2.0
    pts = [(x0, y_lo if not start_high else y_hi)]
    x = x0
    hi = start_high
    for _ in range(n):
        pts.append((x, y_hi if hi else y_lo))
        x += half
        pts.append((x, y_hi if hi else y_lo))
        hi = not hi
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (s, color, sw))


# ── clock: період T, частота f, шкала частот ─────────────────────────────────
def fig_clock():
    W, H = 760, 330
    p = []
    y_lo, y_hi = 150, 108
    x0, period = 110, 130
    p.append(line(x0, y_lo, x0 + period * 4, y_lo, color="#e0e0e0", sw=1.0))
    p.append(square_wave(x0, y_lo, y_hi, period, 8))
    p.append(text(x0 - 12, y_lo - 18, "такт", size=12.5, color=INK, anchor="end", bold=True))
    # фронти (висхідні) — маркери
    edges = [x0 + period * k for k in range(5)]
    for ex in edges:
        p.append(text(ex, y_hi - 10, "▲", size=9, color=POS, bold=True))
    # період T між першим і другим фронтом
    p.append(line(x0, y_lo + 26, x0 + period, y_lo + 26, color=POS, sw=1.6))
    p.append(line(x0, y_lo + 20, x0, y_lo + 32, color=POS, sw=1.6))
    p.append(line(x0 + period, y_lo + 20, x0 + period, y_lo + 32, color=POS, sw=1.6))
    p.append(text(x0 + period / 2, y_lo + 46, "період T", size=12, color=POS, bold=True))
    # рамка з частотами
    bx, by, bw, bh = 110, 210, 540, 96
    p.append(rect(bx, by, bw, bh, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(bx + bw / 2, by + 24, "f = 1/T — скільки тактів за секунду:", size=12.5, color=INK, bold=True))
    cols = [
        (bx + 95, "1 Гц", "1 такт/с"),
        (bx + 230, "16 МГц", "ядро Arduino Uno"),
        (bx + 365, "240 МГц", "ядро ESP32"),
        (bx + 480, "3 ГГц", "процесор ПК"),
    ]
    for cx, big, small in cols:
        p.append(text(cx, by + 56, big, size=13, color=POS, bold=True))
        p.append(text(cx, by + 76, small, size=10.5, color=MUTED))
    render(os.path.join(OUT, "clock.svg"), W, H, *p,
           title="Такт — рівномірна прямокутна хвиля: період T, частота f = 1/T")


# ── synchronous: один такт розходиться до всіх тригерів ──────────────────────
def fig_synchronous():
    W, H = 840, 330
    p = []
    # джерело такту
    p.append(rect(60, 150, 90, 50, fill="#fdf4f4", stroke=POS, sw=2, rx=8))
    p.append(text(105, 180, "ТАКТ", size=12, color=POS, bold=True))
    # вертикальна шина такту
    busx = 210
    p.append(line(150, 175, busx, 175, color=POS, sw=2))
    p.append(circle(busx, 175, 3.0, fill=POS, stroke=POS, sw=1))
    p.append(line(busx, 105, busx, 270, color=POS, sw=2))
    # 4 тригери
    fy = [100, 150, 200, 250]
    for i, yy in enumerate(fy):
        p.append(line(busx, yy + 9, 280, yy + 9, color=POS, sw=1.4))
        p.append(circle(busx, yy + 9, 2.5, fill=POS, stroke=POS, sw=1))
        p.append(rect(280, yy, 96, 34, fill="#fafafa", stroke=INK, sw=1.8, rx=5))
        p.append(text(328, yy + 22, "тригер %d" % (i + 1), size=10.5, color=INK, bold=True))
        # позначка тактового входу (трикутник)
        p.append('<path d="M 280,%.0f L 292,%.0f L 280,%.0f" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (yy + 4, yy + 11, yy + 18, INK))
    p.append(text(328, 305, "усі тактовані РАЗОМ", size=11, color=POS, bold=True))
    # пояснювальна рамка
    bx, by, bw, bh = 440, 100, 380, 184
    p.append(rect(bx, by, bw, bh, fill="#f4f7f4", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(bx + bw / 2, by + 26, "Що дає спільний такт:", size=12.5, color=INK, bold=True))
    lines = [
        "• єдиний момент зміни стану — фронт такту",
        "• між фронтами все «застигло», і логіка",
        "   спокійно встигає порахувати наступне",
        "• система передбачувана:",
        "   крок — порахувати — крок — порахувати",
        "• це і є СИНХРОННИЙ дизайн",
    ]
    yy = by + 52
    for ln in lines:
        p.append(text(bx + 18, yy, ln, size=11, color=INK, anchor="start"))
        yy += 22
    render(os.path.join(OUT, "synchronous.svg"), W, H, *p,
           title="Один такт розходиться до всіх тригерів — усі крокують разом")


def inverter(x, y, sw=2):
    """Інвертор-трикутник вістрям вправо з кружком, вхід зліва, вихід справа."""
    body = ('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="#fafafa" '
            'stroke="%s" stroke-width="%.1f"/>' % (x, y - 14, x, y + 14, x + 34, y, INK, sw))
    bubble = circle(x + 40, y, 6.0, fill=BG, stroke=INK, sw=sw)
    return body + bubble, x + 46  # вихід після кружка


# ── generate: кільцевий генератор + кварцовий генератор ───────────────────────
def fig_generate():
    W, H = 860, 350
    p = []
    # ── ліва панель: кільце з 3 інверторів ──
    p.append(rect(40, 70, 380, 250, fill="none", stroke="#e4e4e4", sw=1.5, rx=10))
    p.append(text(230, 96, "Кільцевий генератор (3 інвертори)", size=12, color=INK, bold=True))
    yline = 165
    xs = [120, 210, 300]
    out_x = None
    for xi in xs:
        frag, ox = inverter(xi, yline)
        p.append(frag)
        if xi != xs[0]:
            p.append(line(prev_out, yline, xi, yline, color=INK, sw=1.6))
        prev_out = ox
        out_x = ox
    # зворотний зв'язок з виходу останнього на вхід першого
    p.append(line(out_x, yline, out_x, 125, color=INK, sw=1.6))
    p.append(line(out_x, 125, 92, 125, color=INK, sw=1.6))
    p.append(line(92, 125, 92, yline, color=INK, sw=1.6))
    p.append(arrow(92, yline, 120, yline, color=INK, sw=1.6))
    # хвиля під кільцем (нерівна — «гуляє»)
    p.append(line(92, 252, 400, 252, color="#e4e4e4", sw=1.0))
    p.append(square_wave(92, 252, 224, 70, 9, sw=2.2, color=POS))
    p.append(text(230, 290, "просто, та частота «гуляє»", size=11, color=POS, bold=True))
    p.append(text(230, 308, "(залежить від затримок, T°, напруги)", size=10, color=MUTED, italic=True))
    # ── права панель: кварцовий генератор ──
    p.append(rect(440, 70, 380, 250, fill="none", stroke="#e4e4e4", sw=1.5, rx=10))
    p.append(text(630, 96, "Кварцовий генератор", size=12, color=INK, bold=True))
    yq = 165
    frag, ox = inverter(560, yq)
    p.append(text(577, 138, "підсилювач", size=9.5, color=MUTED))
    p.append(frag)
    p.append(line(ox, yq, 700, yq, color=INK, sw=1.6))
    # зворотна петля через кварц
    p.append(line(540, yq, 540, 225, color=INK, sw=1.6))
    p.append(line(540, 225, 700, 225, color=INK, sw=1.6))
    p.append(line(700, 225, 700, yq, color=INK, sw=1.6))
    p.append(arrow(540, yq, 560, yq, color=INK, sw=1.6))
    # символ кварцу на нижній гілці
    qx = 620
    p.append(line(qx - 26, 225, qx - 8, 225, color=INK, sw=1.8))
    p.append(line(qx - 8, 211, qx - 8, 239, color=INK, sw=2.4))
    p.append(rect(qx - 6, 209, 12, 32, fill="#eef7ee", stroke=FIELD, sw=2, rx=2))
    p.append(line(qx + 8, 211, qx + 8, 239, color=INK, sw=2.4))
    p.append(line(qx + 8, 225, qx + 26, 225, color=INK, sw=1.8))
    p.append(text(qx, 256, "кварц", size=10, color=FIELD, bold=True))
    p.append(text(706, yq + 4, "такт", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(630, 290, "точна, стабільна частота", size=11, color=FIELD, bold=True))
    p.append(text(630, 308, "(механічний резонанс кристала)", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "generate.svg"), W, H, *p,
           title="Звідки береться такт: кільцевий генератор (неточно) і кварц (точно)")


# ── period-budget: критичний шлях і максимальна частота ──────────────────────
def fig_period_budget():
    W, H = 860, 400
    p = []
    # верхній рядок: такт із двома періодами
    p.append(text(108, 96, "такт", size=12.5, color=INK, anchor="end", bold=True))
    cy = 106
    p.append(line(120, cy, 820, cy, color="#e4e4e4", sw=1.0))
    # один широкий період між фронтами на 250 і 620
    p.append('<polyline points="120,106 250,106 250,80 290,80 290,106 620,106 620,80 660,80 660,106 820,106" '
             'fill="none" stroke="%s" stroke-width="2.3" stroke-linejoin="round"/>' % INK)
    p.append(line(250, 72, 250, 330, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(620, 72, 620, 330, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(250, 70, "▲", size=9, color=POS, bold=True))
    p.append(text(620, 70, "▲", size=9, color=POS, bold=True))
    p.append(line(250, 132, 620, 132, color=POS, sw=1.6))
    p.append(text(435, 126, "період T", size=11.5, color=POS, bold=True))
    # середній рядок: логіка встигла
    p.append(text(95, 185, "логіка", size=11, color=INK, anchor="end", bold=True))
    p.append('<polyline points="250,200 270,200 340,172 520,172 620,172" fill="none" '
             'stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % FIELD)
    p.append(text(390, 165, "порахувала й «устоялась»", size=10, color=FIELD, bold=True))
    p.append(line(520, 158, 520, 186, color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(520, 186, 620, 186, color=FIELD, sw=1.6))
    p.append(text(570, 200, "запас", size=9.5, color=FIELD, bold=True))
    p.append(text(258, 220, "✓ встигла до наступного фронту", size=11, color=FIELD, anchor="start", bold=True))
    # нижній рядок: надто швидко
    p.append(text(95, 290, "надто", size=10.5, color=POS, anchor="end", bold=True))
    p.append(text(95, 304, "швидко", size=10.5, color=POS, anchor="end", bold=True))
    p.append(line(450, 322, 450, 270, color=POS, sw=1.4, dash="4 3"))
    p.append(text(450, 262, "наступний фронт ТУТ", size=10, color=POS, bold=True))
    p.append('<polyline points="250,322 270,322 430,288 470,288" fill="none" '
             'stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % GOLD)
    p.append(text(360, 344, "✘ логіка ще рахує — фронт ловить «сире» → помилка",
                  size=10.5, color=POS, bold=True))
    p.append(text(W / 2, 384, "Є МАКСИМАЛЬНА частота: T ≥ найдовший шлях логіки + запас",
                  size=12, color=INK, bold=True))
    render(os.path.join(OUT, "period-budget.svg"), W, H, *p,
           title="Бюджет періоду: логіка мусить устигнути між фронтами")


# ── skew: дерево такту й перекіс ─────────────────────────────────────────────
def fig_skew():
    W, H = 860, 340
    p = []
    p.append(rect(60, 150, 80, 44, fill="#fdf4f4", stroke=POS, sw=2, rx=8))
    p.append(text(100, 177, "ТАКТ", size=11, color=POS, bold=True))
    busx = 200
    p.append(line(140, 172, busx, 172, color=POS, sw=2))
    p.append(circle(busx, 172, 3.0, fill=POS, stroke=POS, sw=1))
    p.append(line(busx, 110, busx, 250, color=POS, sw=2))
    for yy in (110, 172, 250):
        p.append(line(busx, yy, 280, yy, color=POS, sw=1.6))
        p.append(rect(280, yy - 16, 80, 32, fill="#fafafa", stroke=INK, sw=1.6, rx=5))
        p.append(text(320, yy + 4, "тригер", size=10, color=INK, bold=True))
        p.append('<path d="M 280,%.0f L 292,%.0f L 280,%.0f" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (yy - 5, yy + 2, yy + 9, INK))
    p.append(text(420, 168, "«дерево такту»", size=11, color=MUTED, anchor="start", italic=True))
    p.append(text(420, 188, "(балансують довжини гілок,", size=10, color=MUTED, anchor="start"))
    p.append(text(420, 204, "щоб фронт приходив рівно)", size=10, color=MUTED, anchor="start"))
    # рамка про перекіс
    bx, by, bw, bh = 560, 110, 280, 170
    p.append(rect(bx, by, bw, bh, fill="#fbf6ec", stroke=GOLD, sw=1.6, rx=10))
    p.append(text(bx + bw / 2, by + 26, "Перекіс (skew):", size=12.5, color=GOLD, bold=True))
    lines = [
        "якщо один тригер бачить фронт",
        "пізніше за сусіда, дані можуть",
        "«прослизнути» на зайвий щабель —",
        "і синхронність ламається.",
    ]
    yy = by + 52
    for ln in lines:
        p.append(text(bx + 20, yy, ln, size=11, color=INK, anchor="start"))
        yy += 20
    p.append(text(bx + 20, yy + 6, "тому такт розводять акуратно,", size=10, color=MUTED, anchor="start", italic=True))
    p.append(text(bx + 20, yy + 24, "як гілки однакової довжини", size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "skew.svg"), W, H, *p,
           title="Розведення такту деревом: перекіс (skew) ламає синхронність")


# ── accuracy: драбина точності джерел такту у ppm (лог-шкала) ─────────────────
def fig_accuracy():
    W, H = 900, 500
    p = []
    # лог-вісь: 0.1 .. 100000 ppm → x
    x_left, x_right = 322.0, 802.0
    lo_e, hi_e = -1, 5            # 10^-1 .. 10^5
    def X(ppm):
        e = math.log10(ppm)
        return x_left + (e - lo_e) / (hi_e - lo_e) * (x_right - x_left)
    axis_y = 432
    # сітка
    for e in range(lo_e, hi_e + 1):
        gx = X(10 ** e)
        p.append(line(gx, 66, gx, axis_y, color="#ededed", sw=1.0))
        p.append(line(gx, axis_y - 5, gx, axis_y + 5, color=INK, sw=1.6))
        lab = {-1: "0.1", 0: "1", 1: "10", 2: "100", 3: "1 000", 4: "10 000", 5: "100 000"}[e]
        p.append(text(gx, axis_y + 22, lab, size=11, color=MUTED))
    p.append(line(x_left, axis_y, x_right + 4, axis_y, color=INK, sw=2))
    p.append(text(x_right + 12, axis_y + 4, "ppm", size=12, color=INK, anchor="start", bold=True))
    p.append(text(x_left, axis_y + 46, "← точніше", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(x_right, axis_y + 46, "грубіше →", size=11, color=POS, anchor="end", bold=True))
    # поріг «вистачає для UART і RTC» біля 50 ppm
    thr = X(50)
    p.append(line(thr, 78, thr, axis_y, color=FIELD, sw=1.4, dash="4 4"))
    p.append(text(thr - 8, 76, "лівіше — вистачає для UART і RTC", size=10, color=FIELD, anchor="end", italic=True))
    # рядки: (назва, lo_ppm, hi_ppm, колір, підпис)
    rows = [
        ("RC-генератор у чипі",       10000, 50000, POS,   "вбудований, безкоштовний; «гуляє» з T° і живленням"),
        ("RC після калібрування",      1000, 20000, POS,   "підправлений на заводі, та все одно повзе"),
        ("Керамічний резонатор",       3000,  5000, GOLD,  "дешевий, CL уже всередині; точність середня"),
        ("Кварцовий резонатор",          10,    50, FIELD, "робоча конячка точного такту в МК"),
        ("Годинниковий кварц 32768 Гц",   5,    20, FIELD, "для лічби реального часу (RTC)"),
        ("TCXO: кварц + термокомпенсація",0.5,   2, NEG,   "тримає точність і в спеку, і в холод"),
        ("MEMS-генератор",                5,    30, FIELD, "кремнієва балка замість кристала; міцний до ударів"),
    ]
    y = 92
    for name, a, b, col, note in rows:
        xa, xb = X(a), X(b)
        p.append(text(16, y, name, size=12.5, color=INK, anchor="start", bold=True))
        p.append(line(xa, y - 4, xb, y - 4, color=col, sw=6))
        # підпис діапазону біля грубшого краю
        p.append(text(xb + 8, y, "±%s–%s ppm" % (fmt(a), fmt(b)), size=11, color=col, anchor="start", bold=True))
        p.append(text(xa, y + 14, note, size=9.5, color=MUTED, anchor="start", italic=True))
        y += 48
    render(os.path.join(OUT, "accuracy.svg"), W, H, *p,
           title="Драбина точності джерел такту: похибка частоти у ppm")


def fmt(v):
    if v == int(v):
        return "{:,}".format(int(v)).replace(",", " ")
    return ("%g" % v)


# ── pierce: кварц у схемі Пірса (інвертор, Rf, два CL) ────────────────────────
def fig_pierce():
    W, H = 760, 360
    p = []
    # центр: інвертор між XTAL1 (ліворуч) і XTAL2 (праворуч)
    inx, iny = 330, 175
    p.append('<path d="M %.0f,%.0f L %.0f,%.0f L %.0f,%.0f Z" fill="#fafafa" stroke="%s" stroke-width="2"/>'
             % (inx, iny - 26, inx, iny + 26, inx + 56, iny, INK))
    p.append(circle(inx + 62, iny, 5.0, fill=BG, stroke=INK, sw=2))
    p.append(text(inx + 28, iny - 40, "інвертор-підсилювач (усередині МК)", size=10.5, color=INK, italic=True))
    x1, x2 = inx, inx + 67           # XTAL1 (вхід), XTAL2 (вихід)
    p.append(text(x1, iny - 70, "XTAL1", size=11, color=INK, bold=True))
    p.append(text(x2, iny - 70, "XTAL2", size=11, color=INK, bold=True))
    topy = iny - 62
    p.append(line(x1, iny, x1, topy, color=INK, sw=2))
    p.append(line(x2, iny, x2, topy, color=INK, sw=2))
    # кварц між вершинами
    p.append(line(x1, topy, x1 + 22, topy, color=INK, sw=2))
    p.append(rect(x1 + 22, topy - 10, 23, 20, fill="#eef7ee", stroke=FIELD, sw=2, rx=3))
    p.append(text((x1 + x2) / 2, topy - 16, "КВАРЦ", size=11, color=FIELD, bold=True))
    p.append(line(x2 - 22, topy, x2, topy, color=INK, sw=2))
    # Rf паралельно інвертору (нижня петля)
    p.append(line(x1, iny, x1 - 34, iny, color=INK, sw=2))
    p.append(line(x1 - 34, iny, x1 - 34, iny + 70, color=INK, sw=2))
    p.append(rect(x1 - 50, iny + 70, 32, 16, fill=BG, stroke=GOLD, sw=2, rx=3))
    p.append(text(x1 - 34, iny + 82, "Rf", size=11, color=GOLD, bold=True))
    p.append(line(x1 - 34, iny + 86, x1 - 34, iny + 120, color=INK, sw=2))
    p.append(line(x1 - 34, iny + 120, x2, iny + 120, color=INK, sw=2))
    p.append(line(x2, iny, x2, iny + 120, color=INK, sw=2))
    p.append(text(x1 - 70, iny + 12, "Rf: тримає інвертор", size=9.5, color=GOLD, anchor="start"))
    p.append(text(x1 - 70, iny + 26, "у лінійному режимі", size=9.5, color=GOLD, anchor="start"))
    p.append(text(x1 - 70, iny + 40, "(часто вже в чипі)", size=9.5, color=MUTED, anchor="start"))
    # два конденсатори CL від кожної ніжки на землю
    for cxp, lab_dx in ((x1, -4), (x2, 4)):
        midy = topy + 30
        p.append(line(cxp, topy, cxp, midy, color=INK, sw=1.6))
        p.append(line(cxp - 12, midy, cxp + 12, midy, color=INK, sw=2.4))
        p.append(line(cxp - 12, midy + 8, cxp + 12, midy + 8, color=INK, sw=2.4))
        p.append(line(cxp, midy + 8, cxp, midy + 48, color=INK, sw=1.6))
        # земля
        gy = midy + 48
        p.append(line(cxp - 12, gy, cxp + 12, gy, color=NEG, sw=2.4))
        p.append(line(cxp - 8, gy + 5, cxp + 8, gy + 5, color=NEG, sw=2))
        p.append(line(cxp - 4, gy + 10, cxp + 4, gy + 10, color=NEG, sw=2))
        p.append(text(cxp + 16, midy + 4, "CL", size=11, color=INK, anchor="start", bold=True))
    p.append(text((x1 + x2) / 2, iny + 150, "два CL (≈ 12–22 пФ) задають «навантаження» кварцу",
                  size=10, color=MUTED))
    p.append(text((x1 + x2) / 2, iny + 168, "номінал — зі специфікації кварцу (load capacitance)",
                  size=9.5, color=MUTED))
    # ліворуч — сам резонатор (2 ніжки)
    rx = 95
    p.append(text(rx, 92, "Кварцовий резонатор", size=12, color=INK, bold=True))
    p.append(text(rx, 108, "(2 ніжки, без полярності)", size=10, color=MUTED))
    p.append(line(rx, 128, rx, 146, color=INK, sw=2))
    p.append(line(rx - 16, 146, rx + 16, 146, color=INK, sw=3))
    p.append(rect(rx - 11, 152, 22, 26, fill="#eef7ee", stroke=FIELD, sw=2, rx=2))
    p.append(line(rx - 16, 184, rx + 16, 184, color=INK, sw=3))
    p.append(line(rx, 184, rx, 202, color=INK, sw=2))
    p.append(text(rx, 222, "напис «40.000» = 40 МГц", size=9.5, color=MUTED))
    render(os.path.join(OUT, "pierce.svg"), W, H, *p,
           title="Кварц у схемі Пірса: інвертор, Rf і два навантажувальні конденсатори CL")


# ── drift: два наслідки похибки — годинник пливе, зв'язок зривається ──────────
def fig_drift():
    W, H = 840, 430
    p = []
    # ── ліва картка: годинник пливе ──
    p.append(rect(50, 56, 350, 330, fill=BG, stroke="#e4e4e4", sw=1.5, rx=8))
    p.append(text(225, 82, "1) Годинник «пливе»", size=14, color=INK, bold=True))
    p.append(text(225, 102, "похибка × час = накопичений відхід", size=11, color=MUTED, italic=True))
    p.append(text(225, 120, "1 ppm ≈ 0.0864 с за добу", size=11, color=FIELD))
    cols = [(72, "джерело", "start"), (215, "ppm", "middle"), (300, "за добу", "middle"), (372, "за рік", "middle")]
    for cx, lab, an in cols:
        p.append(text(cx, 150, lab, size=11, color=INK, anchor=an, bold=True))
    p.append(line(70, 158, 388, 158, color="#e4e4e4", sw=1.4))
    rows = [
        ("RC у чипі",  "±30 000", "43.2 хв", "11.0 дн", POS),
        ("кераміка",   "±4 000",  "5.8 хв",  "1.5 дн",  GOLD),
        ("кварц МК",   "±30",     "2.6 с",   "16 хв",   FIELD),
        ("кварц RTC",  "±20",     "1.7 с",   "11 хв",   FIELD),
        ("TCXO",       "±1",      "0.086 с", "32 с",    NEG),
    ]
    yy = 182
    for name, ppm, d, yr, col in rows:
        p.append(text(72, yy, name, size=11, color=INK, anchor="start"))
        p.append(text(215, yy, ppm, size=11, color=col, bold=True))
        p.append(text(300, yy, d, size=11, color=INK))
        p.append(text(372, yy, yr, size=11, color=col, bold=True))
        yy += 30
    p.append(text(225, yy + 18, "RC за рік «з'їде» на тижні —", size=10, color=POS, italic=True))
    p.append(text(225, yy + 34, "тримати реальний час на ньому не можна", size=10, color=POS, italic=True))
    # ── права картка: зв'язок ──
    p.append(rect(440, 56, 350, 330, fill=BG, stroke="#e4e4e4", sw=1.5, rx=8))
    p.append(text(615, 82, "2) Зв'язок «розсинхрониться»", size=13.5, color=INK, bold=True))
    p.append(text(615, 102, "два боки шини рахують біти своїми тактами", size=10.5, color=MUTED, italic=True))
    p.append(text(615, 130, "сумарне розходження двох боків:", size=11, color=INK))
    # смуга 0..4%, поріг 2%
    bx, bw = 470, 270
    seg = bw / 4.0
    p.append(rect(bx, 146, seg * 2, 20, fill="#e8f6ec", stroke=FIELD, sw=1.5, rx=0))
    p.append(rect(bx + seg * 2, 146, seg, 20, fill="#fbf3df", stroke=GOLD, sw=1.5, rx=0))
    p.append(rect(bx + seg * 3, 146, seg, 20, fill="#fae8e6", stroke=POS, sw=1.5, rx=0))
    for k in range(5):
        gx = bx + seg * k
        p.append(line(gx, 166, gx, 172, color=MUTED, sw=1.4))
        p.append(text(gx, 184, "%d %%" % k, size=10, color=MUTED))
    p.append(text(bx + seg, 160, "надійно", size=10, color=FIELD, bold=True))
    p.append(text(bx + seg * 3.5, 160, "збій", size=10, color=POS, bold=True))
    p.append(text(615, 214, "Пара тактів і де вона лягає:", size=11, color=INK, bold=True))
    bullets = [
        ("два кварци: 0.006 % — величезний запас", FIELD),
        ("кераміка + кварц: ~0.4 % — ще надійно", FIELD),
        ("дві кераміки: ~0.8 % — теж проходить", FIELD),
        ("RC + кварц: ~3 % — уже на межі зриву", POS),
    ]
    yy = 238
    for txt, col in bullets:
        p.append(circle(460, yy - 4, 3.5, fill=col, stroke=col, sw=1))
        p.append(text(472, yy, txt, size=10.5, color=col, anchor="start"))
        yy += 24
    p.append(text(615, yy + 14, "ось чому UART на «голому» RC часто не злітає", size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "drift.svg"), W, H, *p,
           title="Що означає ppm на практиці: відхід годинника й запас зв'язку")


if __name__ == "__main__":
    fig_clock()
    fig_synchronous()
    fig_generate()
    fig_period_budget()
    fig_skew()
    fig_accuracy()
    fig_pierce()
    fig_drift()
    print("OK: figures written to", OUT)
