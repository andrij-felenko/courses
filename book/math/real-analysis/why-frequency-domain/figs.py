# -*- coding: utf-8 -*-
"""Фігури для book/math/real-analysis/why-frequency-domain/why-frequency-domain.md
Генерує SVG у ./img/  Запуск: python figs.py
Імпортує спільний svgkit зі scripts/ (примітиви не переписувати).
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# F1 — Карта застосувань: з однієї здатності «розділяти за частотою»
#      виростає п'ять класів задач.
# ─────────────────────────────────────────────────────────────────────────────
def fig_app_map():
    W, H = 740, 332
    f = []
    f.append(text(W / 2, 26, "П'ять задач для частотної області", size=16, bold=True))

    # центральний вузол
    cx, cy, r = 150, 190, 56
    f.append(circle(cx, cy, r, fill="#eafaf0", stroke=FIELD, sw=2.4))
    f.append(mtext(cx, cy - 4, ["частотна", "область"], size=13, color=FIELD, bold=True))

    rows = [
        ("виявлення тонів", "DTMF, біп, тюнер", NEG),
        ("вібродіагностика", "оберти, дефекти", "#9a4ea8"),
        ("фільтрація",       "прибрати гул",    POS),
        ("пошук у шумі",     "слабкий тон",     "#9a7a1e"),
        ("стиснення",        "MP3, JPEG",       INK),
    ]
    bx, bw, bh = 360, 350, 44
    y0, gap = 60, 54
    for i, (title, sub, col) in enumerate(rows):
        by = y0 + i * gap
        f.append(line(cx + r, cy, bx - 6, by + bh / 2, color=col, sw=1.4))
        f.append(rect(bx, by, bw, bh, fill="#fbfbfb", stroke=col, sw=1.6, rx=8))
        f.append(text(bx + 14, by + 28, title, size=12, color=col, anchor="start", bold=True))
        f.append(text(bx + bw - 12, by + 28, sub, size=11, color=MUTED, anchor="end", italic=True))

    render(os.path.join(OUT, "app-map.svg"), W, H, *f)


# ── допоміжне: вісь спектра зі стовпчиками-піками ───────────────────────────
def _spectrum_axis(ox, oy, axw, top, label_x="частота"):
    """Горизонтальна вісь частоти з вертикальною віссю величини."""
    out = []
    out.append(arrow(ox, oy, ox, top, color=INK, sw=1.4))
    out.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.4))
    return out


def _peak(x, oy, h, color=FIELD, sw=6):
    return line(x, oy, x, oy - h, color=color, sw=sw)


# ─────────────────────────────────────────────────────────────────────────────
# F2 — Виявлення тонів: суміш двох тонів у часі (гудіння) → два піки в частоті.
# ─────────────────────────────────────────────────────────────────────────────
def fig_tone_detect():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 26, "Виявлення тонів: дві частоти кнопки — два піки", size=14, bold=True))

    # — ліворуч: час (сума двох синусів) —
    ox, oy, axw = 55, 150, 290
    f.append(line(ox, oy, ox + axw, oy, color="#e4e4e4", sw=1.2))
    pts = []
    for i in range(0, axw + 1):
        t = i / axw
        v = 26 * math.sin(2 * math.pi * 7 * t) + 22 * math.sin(2 * math.pi * 12.1 * t)
        pts.append("%.1f,%.1f" % (ox + i, oy - v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), NEG))
    f.append(text(ox + axw / 2, 250, "час: нерозбірливе гудіння", size=11, color=NEG, bold=True))

    # — стрілка → —
    f.append(arrow(358, oy, 398, oy, color=INK, sw=2))

    # — праворуч: частота (два піки) —
    fx, fy, faxw = 410, 205, 270
    f += _spectrum_axis(fx, fy, faxw, 71)
    p1 = fx + 78
    p2 = fx + 161
    f.append(_peak(p1, fy, 102, FIELD))
    f.append(text(p1, fy + 14, "770 Гц", size=10, color=MUTED))
    f.append(_peak(p2, fy, 102, FIELD))
    f.append(text(p2, fy + 14, "1336 Гц", size=10, color=MUTED))
    f.append(text((p1 + p2) / 2 + 20, 250, "частота: два піки — цифра «5»", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "tone-detect.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F3 — Вібродіагностика: здоровий спектр (оберти + гармоніки) + новий пік-дефект.
# ─────────────────────────────────────────────────────────────────────────────
def fig_vibration():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 26, "Вібродіагностика: новий пік — дефект", size=15, bold=True))

    ox, oy, axw = 70, 240, 580
    f += _spectrum_axis(ox, oy, axw + 12, 46)
    f.append(text(ox + axw - 4, oy + 18, "частота →", size=10, color=INK, bold=True))

    # шумова підлога (дрібні сірі стовпчики)
    random.seed(11)
    n = 40
    for i in range(n):
        x = ox + 29 + i * 13.05
        h = random.uniform(7, 11)
        f.append(line(x, oy, x, oy - h, color="#8a8a8a", sw=2))

    # гармоніки здорової машини (зелене)
    harm = [(139.6, 162, "оберти"), (209.2, 81, "2×"), (278.8, 50, "3×"), (348.4, 32, None)]
    for x, h, lab in harm:
        f.append(_peak(x, oy, h, FIELD))
        if lab:
            f.append(text(x, oy - h - 6, lab, size=9, color=FIELD, bold=True))

    # новий пік-дефект (червоне)
    f.append(_peak(476, oy, 90, POS))
    f.append(text(476, oy - 96, "новий пік = дефект!", size=10, color=POS, bold=True))

    f.append(text(W / 2, 284, "еталон здорової машини + сторожа за новими піками = поломка наперед",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(OUT, "vibration.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F4 — Фільтрація в частоті: сигнал+гул → спектр (гул окремий пік) →
#      занулити пік → обернене → чистий сигнал.
# ─────────────────────────────────────────────────────────────────────────────
def fig_freq_filter():
    W, H = 760, 270
    f = []
    f.append(text(W / 2, 24, "Фільтрація в частоті: вирізати пік гулу", size=14, bold=True))

    # — ліворуч: сигнал + гул —
    ox, oy, axw = 40, 110, 170
    f.append(line(ox, oy, ox + axw, oy, color="#e4e4e4", sw=1.0))
    pts = []
    for i in range(0, axw + 1):
        t = i / axw
        v = 16 * math.sin(2 * math.pi * 2.0 * t) + 13 * math.sin(2 * math.pi * 11.0 * t)
        pts.append("%.1f,%.1f" % (ox + i, oy - v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), NEG))
    f.append(text(ox + axw / 2, 164, "сигнал + гул", size=10.5, color=NEG, bold=True))

    f.append(arrow(218, oy, 250, oy, color=INK, sw=2))

    # — середина: спектр, гул — окремий пік, який зануляємо —
    sx, sy = 265, 150
    f += _spectrum_axis(sx, sy, 190, 46)
    f.append(_peak(sx + 22, sy, 76, FIELD))       # корисне
    f.append(_peak(sx + 130, sy, 63, FIELD))      # гул
    # хрестик «зануляємо» на піку гулу
    gx = sx + 130
    f.append(line(gx - 10, sy - 71, gx + 10, sy - 55, color=POS, sw=2))
    f.append(line(gx - 10, sy - 55, gx + 10, sy - 71, color=POS, sw=2))
    f.append(text(gx, sy - 79, "× зануляємо", size=9, color=POS, bold=True))
    f.append(text(sx + 90, 250, "спектр: гул окремо", size=9.5, color=FIELD, italic=True))

    f.append(arrow(458, oy, 520, oy, color=INK, sw=2))
    f.append(text(489, 98, "обернене", size=9, color=MUTED, italic=True))

    # — праворуч: чистий сигнал —
    cx, cy, caxw = 530, 110, 170
    f.append(line(cx, cy, cx + caxw, cy, color="#e4e4e4", sw=1.0))
    pts = []
    for i in range(0, caxw + 1):
        t = i / caxw
        v = 18 * math.sin(2 * math.pi * 2.0 * t)
        pts.append("%.1f,%.1f" % (cx + i, cy - v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), FIELD))
    f.append(text(cx + caxw / 2, 164, "чисто", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "freq-filter.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F5 — Витягти слабке: у часі суцільний шум (тону не видно),
#      у частоті — пік над шумовою підлогою.
# ─────────────────────────────────────────────────────────────────────────────
def fig_hidden_in_noise():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 26, "Витягти слабке: у часі шум, у частоті — пік", size=14, bold=True))

    # — ліворуч: час — слабкий тон + сильний шум —
    ox, oy, axw = 55, 150, 290
    f.append(line(ox, oy, ox + axw, oy, color="#e4e4e4", sw=1.2))
    random.seed(3)
    pts = []
    for i in range(0, axw + 1):
        t = i / axw
        tone = 7 * math.sin(2 * math.pi * 9 * t)
        noise = random.uniform(-34, 34)
        pts.append("%.1f,%.1f" % (ox + i, oy - tone - noise))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.1" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), NEG))
    f.append(text(ox + axw / 2, 250, "час: суцільний шум, тону не видно", size=10.5, color=NEG, bold=True))

    f.append(arrow(358, oy, 398, oy, color=INK, sw=2))

    # — праворуч: частота — низька підлога шуму + один пік —
    fx, fy, faxw = 410, 205, 270
    f += _spectrum_axis(fx, fy, faxw, 71)
    random.seed(8)
    for i in range(18):
        x = fx + 16 + i * 13
        h = random.uniform(6, 10)
        f.append(line(x, fy, x, fy - h, color=FIELD, sw=5))
    px = fx + 47
    f.append(_peak(px, fy, 102, FIELD))
    f.append(text(px, fy - 108, "тон!", size=9.5, color=FIELD, bold=True))
    f.append(text(fx + 130, 250, "частота: пік над шумом", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "hidden-in-noise.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# F6 — Час чи частота: дві колонки питань + засторога про буфер ШПФ.
# ─────────────────────────────────────────────────────────────────────────────
def fig_time_vs_freq():
    W, H = 720, 300
    f = []
    f.append(text(W / 2, 26, "Час чи частота: яка область під яке питання", size=14, bold=True))

    f.append(rect(40, 52, 300, 40, fill="#eef3fb", stroke=NEG, sw=1.8, rx=8))
    f.append(text(190, 77, "ЧАС — «коли»", size=12, color=NEG, bold=True))
    f.append(rect(380, 52, 300, 40, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(530, 77, "ЧАСТОТА — «що за тон»", size=12, color=FIELD, bold=True))

    left = ["коли сталася подія", "різкий фронт, транзієнт",
            "таймінг, синхронізація", "просте згладжування"]
    right = ["які тони всередині", "який період / оберти",
             "де гул-завада", "розділити перекриті"]
    for i, s in enumerate(left):
        f.append(text(60, 116 + i * 34, "• " + s, size=11, color=INK, anchor="start"))
    for i, s in enumerate(right):
        f.append(text(400, 116 + i * 34, "• " + s, size=11, color=INK, anchor="start"))

    f.append(fitbox(40, 256, 640, 34,
                    "засторога: ШПФ потребує буфера на N відліків → затримка + такти "
                    "(дрібне згладжування дешевше часовим фільтром)",
                    size=11, fill="#fdf6f5", stroke=POS, sw=1.4, color=INK))

    render(os.path.join(OUT, "time-vs-freq.svg"), W, H, *f)


if __name__ == "__main__":
    fig_app_map()
    fig_tone_detect()
    fig_vibration()
    fig_freq_filter()
    fig_hidden_in_noise()
    fig_time_vs_freq()
    print("Done — 6 SVG written to", OUT)
