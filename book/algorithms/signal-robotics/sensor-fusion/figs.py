# -*- coding: utf-8 -*-
"""Фігури до теми «Поєднання давачів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

PURP = "#8e44ad"     # поєднана оцінка
GOLD = "#b9770e"     # тепле виділення


def _polyline(pts, color, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (poly, color, sw, d))


# ── 1. Похибки давачів дзеркальні ─────────────────────────────────────────────
def fig_complementary():
    W, H = 700, 250
    f = [text(W / 2, 28, "Похибки гіроскопа й акселерометра дзеркальні", size=15, bold=True)]

    # ліва картка — гіроскоп
    f.append(rect(46, 60, 290, 132, fill="#eef3fb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(191, 86, "ГІРОСКОП", size=13, color=NEG, bold=True))
    f.append(text(191, 112, "швидкий, гладкий, точний накоротко", size=10, color=FIELD))
    f.append(text(191, 136, "але невпинно ДРЕЙФУЄ надовго", size=10, color=POS, bold=True))
    f.append(text(191, 168, "добрий на ВИСОКИХ частотах", size=9.5, color=MUTED, italic=True))

    # права картка — акселерометр/магнітометр
    f.append(rect(364, 60, 290, 132, fill="#eef7ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(509, 86, "АКСЕЛЕРОМЕТР / МАГНІТОМЕТР", size=10.5, color=FIELD, bold=True))
    f.append(text(509, 112, "абсолютний, без дрейфу", size=10, color=FIELD))
    f.append(text(509, 136, "але ШУМИТЬ і бреше в русі/завадах", size=10, color=POS, bold=True))
    f.append(text(509, 168, "добрий на НИЗЬКИХ частотах", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 224, "сила одного — точно слабкість іншого: ідеальна пара антиподів",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "complementary.svg"), W, H, *f)


# ── 2. Ідея поєднання: довіряй кожному в його силі ────────────────────────────
def fig_fusion_idea():
    W, H = 700, 260
    f = [text(W / 2, 28, "Довіряй кожному давачу там, де він сильний", size=15, bold=True)]

    # два входи зліва, поєднання в центрі, оцінка справа
    f.append(rect(40, 70, 188, 56, fill="#eef3fb", stroke=NEG, sw=1.6, rx=8))
    f.append(text(134, 94, "ГІРОСКОП", size=11, color=NEG, bold=True))
    f.append(text(134, 114, "швидкі зміни (накоротко)", size=9.5, color=MUTED))

    f.append(rect(40, 150, 188, 56, fill="#eef7ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(134, 174, "АКСЕЛЕРОМЕТР + МАГНІТОМЕТР", size=9, color=FIELD, bold=True))
    f.append(text(134, 194, "абсолютна правда (надовго)", size=9.5, color=MUTED))

    # вузол поєднання ⊕
    cx, cy = 392, 138
    f.append(circle(cx, cy, 26, fill="#f3eafb", stroke=PURP, sw=2.2))
    f.append(text(cx, cy + 8, "⊕", size=26, color=PURP, bold=True))
    f.append(text(cx, cy + 48, "поєднання", size=10.5, color=PURP, bold=True))

    f.append(arrow(228, 98, cx - 26, cy - 12, color=NEG, sw=1.8))
    f.append(arrow(228, 178, cx - 26, cy + 12, color=FIELD, sw=1.8))

    # вихід
    f.append(rect(488, 104, 188, 68, fill="#fbfbfb", stroke=PURP, sw=1.8, rx=8))
    f.append(text(582, 130, "ОЦІНКА ОРІЄНТАЦІЇ", size=10.5, color=PURP, bold=True))
    f.append(text(582, 150, "гладка й швидка", size=9.5, color=NEG))
    f.append(text(582, 165, "і водночас без дрейфу", size=9.5, color=FIELD))
    f.append(arrow(cx + 26, cy, 488, cy, color=PURP, sw=2.0))

    f.append(text(W / 2, 244, "ціле, що перевершує кожну зі своїх частин окремо",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "fusion-idea.svg"), W, H, *f)


# ── 3. Поєднання — це поділ за частотою (дві ваги в сумі = 1) ──────────────────
def fig_freq_split():
    W, H = 700, 300
    f = [text(W / 2, 28, "Поєднання — це поділ за частотою", size=15, bold=True)]

    ox, oy, top, right = 70, 232, 60, 640
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(right - 6, oy + 22, "частота →", size=11, bold=True))
    f.append(text(ox - 10, top + 4, "вага", size=10, anchor="end", bold=True))

    xc = (ox + right) / 2.0          # частота переходу
    span = right - 24 - ox
    hi = oy - 6                       # рівень ваги = 0
    lo = top + 8                      # рівень ваги = 1

    # вага акселерометра (НЧ): спадає зліва-направо, як ФНЧ
    accel = []
    gyro = []
    for i in range(81):
        t = i / 80.0
        x = ox + span * t
        fr = (x - xc) / (span * 0.16)        # крутість переходу
        wlow = 1.0 / (1.0 + math.exp(fr))     # ФНЧ-вага (1→0)
        whigh = 1.0 - wlow                     # ФВЧ-вага (0→1)
        accel.append((x, hi - (hi - lo) * wlow))
        gyro.append((x, hi - (hi - lo) * whigh))
    f.append(_polyline(accel, FIELD, sw=2.6))
    f.append(_polyline(gyro, NEG, sw=2.6))

    # лінія переходу
    f.append(line(xc, top + 2, xc, oy, color=POS, sw=1.6, dash="5,3"))
    f.append(text(xc, oy + 20, "частота переходу (α)", size=10, color=POS, bold=True))

    f.append(text(ox + 70, lo + 18, "акселерометр / магнітометр", size=10, color=FIELD,
                  anchor="start", bold=True))
    f.append(text(ox + 70, lo + 33, "(низькі частоти — повільна правда)", size=9, color=MUTED, anchor="start"))
    f.append(text(right - 60, lo + 18, "гіроскоп", size=10, color=NEG, anchor="end", bold=True))
    f.append(text(right - 60, lo + 33, "(високі частоти — швидка динаміка)", size=9, color=MUTED, anchor="end"))

    f.append(text(W / 2, 286, "дві ваги в сумі дають одиницю на кожній частоті — діапазон покрито без дірок",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(IMG, "freq-split.svg"), W, H, *f)


# ── 4. Поєднання в дії: дві погані оцінки → одна гарна ─────────────────────────
def fig_fusion_action():
    W, H = 700, 300
    f = [text(W / 2, 28, "З двох поганих оцінок поєднання дає одну гарну", size=15, bold=True)]

    ox, oy, top, right = 70, 244, 56, 596
    f.append(arrow(ox, oy, ox, top, color=INK, sw=1.6))
    f.append(arrow(ox, oy, right, oy, color=INK, sw=1.6))
    f.append(text(right - 6, oy + 22, "час →", size=11, bold=True))
    f.append(text(ox - 10, top + 4, "кут", size=10, anchor="end", bold=True))

    random.seed(7)
    n = 90
    truth_y = 150.0
    xs = [ox + (right - 18 - ox) * i / (n - 1) for i in range(n)]
    f.append(_polyline([(xs[0], truth_y), (xs[-1], truth_y)], "#d9d9d9", sw=1.6, dash="6,4"))
    f.append(text(xs[-1] - 6, truth_y - 8, "істина", size=9.5, color=MUTED, anchor="end", italic=True))

    # гіроскоп: гладкий, але повільно спливає геть
    gyro = [(xs[i], truth_y + 70 * (i / (n - 1)) ** 1.4) for i in range(n)]
    f.append(_polyline(gyro, POS, sw=2.0))
    f.append(text(xs[-1] - 4, gyro[-1][1] + 4, "гіроскоп: спливає", size=9.5, color=POS, anchor="end", bold=True))

    # акселерометр: тримається істини, але сильно тремтить
    accel = [(xs[i], truth_y + random.uniform(-26, 26)) for i in range(n)]
    f.append(_polyline(accel, NEG, sw=1.3))
    f.append(text(xs[6], truth_y - 40, "акселерометр: тремтить", size=9.5, color=NEG, anchor="start", bold=True))

    # поєднання: гладке й прив'язане до істини
    fus, s = [], truth_y + 14
    for i in range(n):
        s = 0.92 * (s) + 0.08 * accel[i][1]   # комплементарне зважування
        s = 0.985 * s + 0.015 * truth_y        # легке притягання до правди (роль акселя)
        fus.append((xs[i], s))
    f.append(_polyline(fus, PURP, sw=2.6))
    f.append(text(xs[40], truth_y + 36, "поєднання: гладке й без дрейфу", size=10, color=PURP, anchor="middle", bold=True))

    f.append(text(W / 2, 286, "дві недосконалі оцінки дають одну, кращу за обидві",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(IMG, "fusion-action.svg"), W, H, *f)


# ── 5. Два бонуси: менше шуму й більша стійкість ──────────────────────────────
def fig_redundancy():
    W, H = 700, 250
    f = [text(W / 2, 28, "Окрім приборкання дрейфу — ще два бонуси", size=15, bold=True)]

    # ліворуч — менше шуму
    f.append(rect(40, 60, 308, 150, fill="#fbfbfb", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(194, 84, "МЕНШЕ ШУМУ", size=12, color=FIELD, bold=True))
    random.seed(3)
    bx, by, bw = 64, 150, 260
    f.append(line(bx, by, bx + bw, by, color="#d9d9d9", sw=1.2))
    noisy = [(bx + bw * i / 40.0, by - 30 + random.uniform(-14, 14)) for i in range(41)]
    f.append(_polyline(noisy, MUTED, sw=1.0))
    # усереднене — гладеньке
    avg = []
    for i in range(41):
        lo = max(0, i - 3); hi = min(40, i + 3)
        m = sum(noisy[j][1] for j in range(lo, hi + 1)) / (hi - lo + 1)
        avg.append((noisy[i][0], m))
    f.append(_polyline(avg, FIELD, sw=2.4))
    f.append(text(194, 196, "незалежні джерела, усереднені → чистіше", size=9.5, color=MUTED, italic=True))

    # праворуч — стійкість
    f.append(rect(364, 60, 296, 150, fill="#fbfbfb", stroke=NEG, sw=1.6, rx=10))
    f.append(text(512, 84, "БІЛЬШЕ СТІЙКОСТІ", size=12, color=NEG, bold=True))
    # три давачі, один збоїть — оцінка тримається
    labels = [("гіроскоп", FIELD), ("акселерометр", POS), ("магнітометр", FIELD)]
    yy = 112
    for name, col in labels:
        ok = col == FIELD
        f.append(circle(404, yy, 6, fill=("#eef7ef" if ok else "#fdecea"),
                        stroke=(FIELD if ok else POS), sw=2))
        f.append(text(404, yy + 4, ("✓" if ok else "✕"), size=10,
                      color=(FIELD if ok else POS), bold=True))
        f.append(text(420, yy + 4, name + ("" if ok else "  — збій (удар/завада)"),
                      size=9.5, color=(INK if ok else POS), anchor="start", bold=not ok))
        yy += 26
    f.append(text(512, 196, "один збоїть — інші тримають оцінку", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 234, "кілька давачів — не лише точніше, а й надійніше, ніж один",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(IMG, "redundancy.svg"), W, H, *f)


# ── 6. Місток: давачі → поєднання → орієнтація → керування ────────────────────
def fig_bridge():
    W, H = 720, 200
    f = [text(W / 2, 28, "Куди веде поєднання", size=15, bold=True)]

    y = 96
    boxes = [
        ("3 давачі IMU", "сирі покази", NEG, 150),
        ("ПОЄДНАННЯ", "(AHRS)", PURP, 150),
        ("орієнтація", "кути / кватерніон", FIELD, 160),
        ("ПІД-керування", "тримає орієнтацію", GOLD, 160),
    ]
    x = 16
    centers = []
    for title_, sub, col, w in boxes:
        fill = "#f3eafb" if col == PURP else "#fbfbfb"
        f.append(rect(x, y - 32, w, 64, fill=fill, stroke=col, sw=2 if col == PURP else 1.6, rx=10))
        f.append(text(x + w / 2, y - 6, title_, size=11.5, color=col, bold=True))
        f.append(text(x + w / 2, y + 16, sub, size=9.5, color=MUTED))
        centers.append((x, x + w))
        x += w + 26
    for i in range(len(centers) - 1):
        f.append(arrow(centers[i][1], y, centers[i + 1][0], y, color=INK, sw=2.0))

    f.append(text(W / 2, 178, "орієнтація — місток між «відчути» і «втримати»",
                  size=11, color=INK, italic=True))
    render(os.path.join(IMG, "bridge.svg"), W, H, *f)


if __name__ == "__main__":
    fig_complementary()
    fig_fusion_idea()
    fig_freq_split()
    fig_fusion_action()
    fig_redundancy()
    fig_bridge()
    print("OK: 6 figures ->", IMG)
