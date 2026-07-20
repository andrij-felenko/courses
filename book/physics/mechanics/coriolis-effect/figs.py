# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект Коріоліса».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def head_at(x, y, dx, dy, color=INK, size=10):
    """Наконечник стрілки у точці (x,y), напрям (dx,dy)."""
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    bx, by = x - ux * size, y - uy * size
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.4, head=9):
    """Дуга-стрілка від кута a0 до a1 (градуси, 0°=праворуч, проти год. на екрані з y-вниз)."""
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign
    ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    back = 2.2
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / back, py + ny * head / back,
            px - nx * head / back, py - ny * head / back, color))
    return path + h


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


# ── Фігура 1: два погляди на політ м'яча по обертовому диску ─────────────────
def fig_turntable():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Один політ — дві системи відліку", size=17, bold=True))

    R = 128
    theta = math.radians(74)          # на скільки повернувся диск за час польоту
    N = 60

    def disk(cx, cy, spoke_ang, label):
        out = circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.6)
        out += circle(cx, cy, 5, fill=INK, stroke=INK, sw=1)     # вісь у центрі
        # позначка на ободі (спиця), щоб було видно поворот диска
        mx = cx + R * math.cos(spoke_ang); my = cy - R * math.sin(spoke_ang)
        out += line(cx, cy, mx, my, color="#c9ced8", sw=2)
        out += circle(mx, my, 6, fill=FIELD, stroke=FIELD, sw=1)
        out += text(cx, cy + R + 26, label, size=13, bold=True)
        return out

    # ── ЛІВОРУЧ: інерціальний погляд (із землі) ──
    cxL, cyL = 210, 200
    f.append(disk(cxL, cyL, math.pi / 2 + theta, "погляд із землі"))
    f.append(text(cxL, cyL - R - 14, "диск обертається", size=12, color=FIELD))
    # позначка початкового положення спиці (звідки диск повернувся) — пунктир
    sx = cxL + R * math.cos(math.pi / 2); sy = cyL - R * math.sin(math.pi / 2)
    f.append(line(cxL, cyL, sx, sy, color="#dfe3ea", sw=2, dash="4 4"))
    f.append(arc_arrow(cxL, cyL, R - 16, 90, 90 + math.degrees(theta), color=FIELD, sw=2.2, head=9))
    # прямий політ м'яча від центра праворуч
    end = (cxL + R, cyL)
    f.append(polyline([(cxL, cyL), end], color=POS, sw=3))
    f.append(head_at(end[0], end[1], 1, 0, POS, 11))
    for s in (0.34, 0.67):
        f.append(circle(cxL + R * s, cyL, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(circle(cxL, cyL, 6, fill=POS, stroke=POS, sw=1))
    f.append(text(cxL + R * 0.5, cyL - 12, "м'яч летить прямо", size=12, bold=True, color=POS))

    # ── ПРАВОРУЧ: обертовий погляд (із каруселі) ──
    cxR, cyR = 552, 200
    f.append(disk(cxR, cyR, math.pi / 2, "погляд із каруселі"))
    f.append(text(cxR, cyR - R - 14, "диск «нерухомий»", size=12, color=MUTED))
    # траєкторія в обертовій системі: r=R·s, кут відносно диска повертається на -theta·s
    pts = []
    for i in range(N + 1):
        s = i / N
        ang = -theta * s                       # у бік, протилежний обертанню диска
        x = cxR + R * s * math.cos(ang)
        y = cyR - R * s * math.sin(ang)        # y-вниз: sin>0 → вгору; ang<0 → вниз
        pts.append((x, y))
    f.append(polyline(pts, color=POS, sw=3))
    ex, ey = pts[-1]; px, py = pts[-3]
    f.append(head_at(ex, ey, ex - px, ey - py, POS, 11))
    f.append(circle(cxR, cyR, 6, fill=POS, stroke=POS, sw=1))
    f.append(text(cxR + 34, cyR + 60, "м'яч виписує дугу", size=12, bold=True, color=POS, anchor="start"))

    # нижня плашка-підсумок
    b, w, h = textbox(W / 2, H - 20,
                      "жодної реальної сили — відхилення дає лише обертання системи",
                      size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "turntable-two-views.svg"), W, H, *f)


# ── Фігура 2: правило відхилення у двох півкулях (погляд згори на полюс) ──────
def fig_hemispheres():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Куди зносить: праворуч на півночі, ліворуч на півдні",
                  size=17, bold=True))

    R = 120

    def hemi(cx, cy, spin, defl, title, sub):
        # spin: 'ccw' | 'cw'; defl: +1 (праворуч від руху) | -1 (ліворуч)
        out = circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.6)
        out += text(cx, cy - R - 26, title, size=14, bold=True)
        out += text(cx, cy - R - 8, sub, size=12, color=MUTED)
        # обертання півкулі
        if spin == 'ccw':
            out += arc_arrow(cx, cy, R - 12, 40, 150, color=FIELD, sw=2.4, head=9)
            out += text(cx - R + 6, cy - R + 22, "обертання", size=11, color=FIELD, anchor="start")
        else:
            out += arc_arrow(cx, cy, R - 12, 150, 40, color=FIELD, sw=2.4, head=9)
            out += text(cx - R + 6, cy - R + 22, "обертання", size=11, color=FIELD, anchor="start")
        # тіло рухається «на північ» (вгору по екрану) від нижньої частини диска
        x0, y0 = cx, cy + 66
        x1, y1 = cx, cy - 40                      # вектор швидкості вгору
        out += varrow(x0, y0, x1, y1, color=NEG, sw=3, head=12)
        out += text(x1 - 8, y1 + 30, "v", size=15, bold=True, italic=True, color=NEG, anchor="end")
        # відхилення вбік (праворуч/ліворуч від руху)
        dx = 58 * defl
        out += varrow(cx, cy + 12, cx + dx, cy + 12, color=POS, sw=3, head=12)
        side = "праворуч" if defl > 0 else "ліворуч"
        out += text(cx + dx + 8 * defl, cy - 2,
                    "снос " + side, size=12, bold=True, color=POS,
                    anchor="start" if defl > 0 else "end")
        # пунктирна дуга реального шляху, що загинається вбік
        pts = []
        for i in range(21):
            s = i / 20.0
            yy = y0 + (y1 - y0) * s
            xx = cx + defl * 66 * s * s
            pts.append((xx, yy))
        out += polyline(pts, color=POS, sw=1.8, dash="5 4")
        return out

    f.append(hemi(210, 210, 'ccw', +1, "Північна півкуля", "згори на Північний полюс"))
    f.append(hemi(552, 210, 'cw', -1, "Південна півкуля", "згори на Південний полюс"))

    b, w, h = textbox(W / 2, H - 20,
                      "F_К = −2m (ω × v)   —   завжди перпендикулярна до швидкості",
                      size=13, pad=9, fill="#eef1fb", stroke=NEG, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "hemispheres-rule.svg"), W, H, *f)


# ── Фігура 3: чому все впирається в широту (Ω·sin φ) ─────────────────────────
def fig_earth():
    W, H = 760, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Відхиляє лише вертикальна складова обертання: Ω·sin φ",
                  size=17, bold=True))

    cx, cy, R = 250, 240, 150
    # земна куля
    f.append(circle(cx, cy, R, fill="#f4f8fb", stroke=MUTED, sw=1.8))
    # екватор (сплюснутий еліпс)
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="4 4"/>'
             % (cx, cy, R, R * 0.30, MUTED))
    f.append(text(cx + R + 8, cy + 4, "екватор", size=11, color=MUTED, anchor="start"))
    # вісь обертання (пунктир) + ω на полюсі
    f.append(line(cx, cy + R + 24, cx, cy - R - 26, color=INK, sw=1.6, dash="6 5"))
    f.append(varrow(cx, cy - R - 4, cx, cy - R - 52, color=FIELD, sw=3, head=12))
    f.append(text(cx + 12, cy - R - 30, "ω (вісь Землі)", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(cx - 10, cy - R + 4, "полюс", size=11, color=MUTED, anchor="end"))

    # ── точка на широті φ у Північній півкулі: розклад ω на складову вздовж вертикалі ──
    aN = math.radians(50)                      # φ ≈ 50°
    P = (cx + R * math.cos(aN), cy - R * math.sin(aN))
    f.append(circle(P[0], P[1], 5, fill=INK, stroke=INK, sw=1))
    u = (math.cos(aN), -math.sin(aN))          # місцева вертикаль (радіус назовні)
    Lw = 66
    Wt = (P[0], P[1] - Lw)                      # вектор ω у точці — паралельний осі (вгору)
    proj = Lw * math.sin(aN)                    # складова ω вздовж вертикалі = Ω·sin φ
    Pp = (P[0] + u[0] * proj, P[1] + u[1] * proj)

    # місцева вертикаль
    f.append(varrow(P[0], P[1], P[0] + u[0] * 72, P[1] + u[1] * 72, color=NEG, sw=2.2, head=10))
    f.append(text(P[0] + u[0] * 80 + 6, P[1] + u[1] * 80, "місцева", size=11, color=NEG, anchor="start"))
    f.append(text(P[0] + u[0] * 80 + 6, P[1] + u[1] * 80 + 15, "вертикаль", size=11, color=NEG, anchor="start"))
    # ω у точці (паралельний осі)
    f.append(varrow(P[0], P[1], Wt[0], Wt[1], color=FIELD, sw=2.6, head=10))
    f.append(text(Wt[0] - 8, Wt[1] - 6, "ω", size=14, bold=True, italic=True, color=FIELD, anchor="end"))
    # проєкція ω на вертикаль — це і є те, що крутить горизонт
    f.append(line(P[0], P[1], Pp[0], Pp[1], color=POS, sw=5))
    f.append(line(Wt[0], Wt[1], Pp[0], Pp[1], color=MUTED, sw=1.2, dash="4 3"))
    # виноска до підпису складової (в чисте поле праворуч)
    lx, ly = 452, 150
    f.append(line((P[0] + Pp[0]) / 2, (P[1] + Pp[1]) / 2, lx - 4, ly, color=POS, sw=1.2, dash="3 3"))
    f.append(text(lx, ly - 2, "Ω·sin φ", size=13, bold=True, italic=True, color=POS, anchor="start"))
    f.append(text(lx, ly + 15, "крутить горизонт", size=11, color=POS, anchor="start"))

    # дуга широти φ у центрі (від екватора до радіуса точки)
    ra = 46
    ax0, ay0 = cx + ra, cy
    ax1, ay1 = cx + ra * math.cos(aN), cy - ra * math.sin(aN)
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (ax0, ay0, ra, ra, ax1, ay1, INK))
    f.append(text(cx + 40, cy - 22, "φ", size=15, bold=True, italic=True))

    # ── права колонка: полюс / екватор / формула ──
    px, pw = 540, 210
    f.append(fitbox(px, 60, pw, 62, "полюс (φ = 90°):\nΩ·sin φ = Ω — максимум",
                    size=12, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True))
    f.append(fitbox(px, 140, pw, 62, "екватор (φ = 0°):\nΩ·sin φ = 0 — не відхиляє",
                    size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.3, bold=True))
    f.append(fitbox(px, 224, pw, 66, "параметр Коріоліса\nf = 2 · Ω · sin φ",
                    size=13, pad=9, fill=FILL, stroke=INK, sw=1.4, bold=True))
    f.append(text(px + pw / 2, 320, "Ω ≈ 7.29 × 10⁻⁵ рад/с", size=12, color=MUTED))
    f.append(text(px + pw / 2, 340, "(один оберт за зоряну добу)", size=11, color=MUTED))
    return render(os.path.join(IMG, "earth-latitude.svg"), W, H, *f)


# ── Фігура 4: історична лінія — доданок, що ім'я дістав останнім ──────────────
def fig_timeline():
    W, H = 880, 600
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Майже три століття: доданок з'явився в математиці, а ім'я дістав останнім",
                  size=16, bold=True))

    rows = [
        ("1651",  MUTED, "Річчолі й Ґрімальді: відхилення ядра —",
                         "його брали за доказ ПРОТИ обертання Землі"),
        ("1749",  NEG,   "Ейлер: доданок у рівняннях руху рідини,",
                         "ще без окремого фізичного тлумачення"),
        ("1778",  NEG,   "Лаплас: той самий доданок",
                         "у рівняннях океанських припливів"),
        ("1835",  FIELD, "Коріоліс: «складена відцентрова сила»",
                         "у теорії обертових МАШИН — не погоди"),
        ("1851",  POS,   "Фуко: маятник у паризькому Пантеоні —",
                         "обертання Землі нарешті стало видимим"),
        ("1857",  FIELD, "Феррел (1856) і Бейс-Балло (1857):",
                         "ефект уже керує вітрами й циклонами"),
        ("≈1920", INK,   "і лише тепер доданок дістає ім'я —",
                         "«сила Коріоліса»"),
    ]

    x_spine = 210
    y0, pitch = 98, 74

    # підсвітити два поворотні рядки (Коріоліс, Фуко) — фон під усе інше
    for idx, tint in ((3, "#f2f7f4"), (4, "#fdf2f1")):
        yc = y0 + pitch * idx
        f.append(rect(120, yc - 31, W - 120 - 26, 62, fill=tint, stroke='none', sw=0, rx=11))

    # хребет часу
    f.append(line(x_spine, y0 - 22, x_spine, y0 + pitch * (len(rows) - 1) + 22, color=MUTED, sw=2.2))

    for i, (yr, col, l1, l2) in enumerate(rows):
        yc = y0 + pitch * i
        f.append(text(x_spine - 32, yc + 5, yr, size=15, bold=True, color=col, anchor="end"))
        f.append(circle(x_spine, yc, 7.5, fill=col, stroke=col, sw=1))
        f.append(text(x_spine + 26, yc - 3, l1, size=13, bold=True, color=INK, anchor="start"))
        f.append(text(x_spine + 26, yc + 16, l2, size=12, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "coriolis-timeline.svg"), W, H, *f)


# ── Фігура (math): правило переносу похідної — вектор, застиглий в обертовій ──
def fig_transport():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Похідна вектора «знає» про обертання осей", size=16, bold=True))

    Ox, Oy, R = 210, 200, 128
    # коло, що його виписує кінець вектора
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.3" stroke-dasharray="5 5"/>' % (Ox, Oy, R, MUTED))

    aA, aB = math.radians(58), math.radians(78)
    tAx, tAy = Ox + R * math.cos(aA), Oy - R * math.sin(aA)
    tBx, tBy = Ox + R * math.cos(aB), Oy - R * math.sin(aB)

    # вектор A (застиглий для обертового спостерігача)
    f.append(line(Ox, Oy, tAx, tAy, color=NEG, sw=3))
    f.append(head_at(tAx, tAy, tAx - Ox, tAy - Oy, NEG, 12))
    f.append(text(tAx + 12, tAy + 4, "A", size=15, bold=True, italic=True, color=NEG, anchor="start"))
    # A' — той самий вектор за мить, повернутий разом з осями
    f.append(line(Ox, Oy, tBx, tBy, color=MUTED, sw=2, dash="6 4"))
    f.append(head_at(tBx, tBy, tBx - Ox, tBy - Oy, MUTED, 10))
    f.append(text(tBx - 12, tBy - 6, "A′", size=13, bold=True, italic=True, color=MUTED, anchor="end"))
    # приріст dA = (ω×A)·dt — тангенційний до кола
    f.append(line(tAx, tAy, tBx, tBy, color=POS, sw=3))
    f.append(head_at(tBx, tBy, tBx - tAx, tBy - tAy, POS, 11))
    mx, my = (tAx + tBx) / 2, (tAy + tBy) / 2
    f.append(line(mx, my, 300, 54, color=POS, sw=1.1, dash="3 3"))
    f.append(text(305, 52, "dA = (ω × A)·dt", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(305, 70, "перпендикулярно до A", size=11, color=MUTED, anchor="start"))

    # сенс обертання + символ осі з площини
    f.append(arc_arrow(Ox, Oy, 96, 205, 320, color=FIELD, sw=2.2, head=9))
    f.append(circle(150, 150, 9, fill="#ffffff", stroke=INK, sw=1.4))
    f.append(circle(150, 150, 2.4, fill=INK, stroke=INK, sw=1))
    f.append(text(133, 155, "ω", size=14, bold=True, italic=True, color=FIELD, anchor="end"))
    f.append(text(150, 176, "вісь із площини", size=10, color=MUTED))

    # права колонка: звідки береться ω× і сам результат
    f.append(fitbox(468, 92, 270, 66, "Кожен орт сам обертається:\ndêᵢ/dt = ω × êᵢ",
                    size=13, pad=10, fill=FILL, stroke=FIELD, sw=1.3, bold=True))
    f.append(fitbox(468, 182, 270, 72, "Правило переносу:\n(d/dt)_ін = (d/dt)_об + ω×",
                    size=13, pad=10, fill="#eef1fb", stroke=NEG, sw=1.4, bold=True))

    b, w, h = textbox(W / 2, 372, "(dA/dt)_об = 0     →     (dA/dt)_ін = ω × A",
                      size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "transport-theorem.svg"), W, H, *f)


# ── Фігура (math): звідки двійка — два однакові внески по Ω·v ─────────────────
def fig_factor2():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Множник 2: два однакові внески по Ω·v", size=16, bold=True))

    R = 112

    def base_disk(cx, cy):
        out = circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.6)
        out += circle(cx, cy, 4, fill=INK, stroke=INK, sw=1)
        out += arc_arrow(cx, cy, 40, 40, 150, color=FIELD, sw=2, head=8)
        out += text(cx + 38, cy - 30, "ω", size=13, bold=True, italic=True, color=FIELD, anchor="start")
        return out

    # ── ЛІВОРУЧ: обід біжить швидше (внесок від (d/dt)_об(ω×r)) ──
    cxL, cyL = 205, 195
    f.append(base_disk(cxL, cyL))
    f.append(varrow(cxL + 64, cyL, cxL + 110, cyL, color=NEG, sw=3, head=11))
    f.append(text(cxL + 90, cyL + 22, "v_об", size=13, bold=True, italic=True, color=NEG))
    # ободова швидкість росте з радіусом: коротка/довга тангенційні
    f.append(varrow(cxL + 44, cyL, cxL + 44, cyL - 15, color=MUTED, sw=2, head=7))
    f.append(varrow(cxL + 92, cyL, cxL + 92, cyL - 32, color=MUTED, sw=2, head=8))
    # бічна добавка Ω·v
    f.append(varrow(cxL + 64, cyL, cxL + 64, cyL - 44, color=POS, sw=3, head=12))
    f.append(text(cxL + 72, cyL - 48, "Ω·v", size=13, bold=True, color=POS, anchor="start"))
    f.append(fitbox(88, 322, 234, 62, "Внесок 1: обід біжить швидше\n(d/dt)_об(ω×r) = ω × v",
                    size=12, pad=8, fill=FILL, stroke=FIELD, sw=1.3, bold=True))

    # ── ПРАВОРУЧ: сам вектор швидкості обертається (внесок від ω×) ──
    cxR, cyR = 555, 195
    f.append(base_disk(cxR, cyR))
    f.append(varrow(cxR + 64, cyR, cxR + 110, cyR, color=NEG, sw=3, head=11))
    f.append(text(cxR + 90, cyR + 22, "v_об", size=13, bold=True, italic=True, color=NEG))
    # той самий вектор за мить, повернутий разом з диском
    dx2, dy2 = 44 * math.cos(math.radians(24)), -44 * math.sin(math.radians(24))
    f.append(line(cxR + 64, cyR, cxR + 64 + dx2, cyR + dy2, color=MUTED, sw=2, dash="5 4"))
    f.append(head_at(cxR + 64 + dx2, cyR + dy2, dx2, dy2, MUTED, 9))
    f.append(text(cxR + 64 + dx2 + 8, cyR + dy2 - 4, "за мить", size=11, color=MUTED, anchor="start"))
    # зміна кінця — бічна, знову Ω·v
    f.append(varrow(cxR + 110, cyR, cxR + 64 + dx2, cyR + dy2, color=POS, sw=3, head=10))
    f.append(text(cxR + 118, cyR - 12, "Ω·v", size=13, bold=True, color=POS, anchor="start"))
    f.append(fitbox(438, 322, 234, 62, "Внесок 2: вектор v_об обертається\nоператор ω× → ω × v",
                    size=12, pad=8, fill="#eef1fb", stroke=NEG, sw=1.3, bold=True))

    f.append(plus(380, 195, 15))

    b, w, h = textbox(W / 2, 410, "обидва = Ω·v      →      разом  2·(ω × v)",
                      size=15, pad=10, fill=FILL, stroke=INK, sw=1.5, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "factor-two.svg"), W, H, *f)


def darrow(x1, y1, x2, y2, color=INK, sw=3, head=11):
    """Двобічна стрілка (наконечники з обох кінців)."""
    return (line(x1, y1, x2, y2, color=color, sw=sw)
            + head_at(x2, y2, x2 - x1, y2 - y1, color, head)
            + head_at(x1, y1, x1 - x2, y1 - y2, color, head))


def _sine(x0, x1, yc, amp, phase, cycles=2, n=140):
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = phase + 2 * math.pi * cycles * t
        pts.append((x0 + (x1 - x0) * t, yc - amp * math.sin(ang)))
    return pts


# ── Фігура (comp): механізм — привід × обертання → коріолісів рух ─────────────
def fig_gyro_principle():
    W, H = 820, 450
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Механізм: привід дає швидкість v, обертання ω домішує коріолісів рух упоперек",
                  size=15, bold=True))

    # рамка-якір + пружини + інерційна маса (це резонатор «пружина–маса»)
    fx0, fy0, fs = 120, 120, 260
    cx, cy = fx0 + fs / 2, fy0 + fs / 2       # (250, 250)
    f.append(rect(fx0, fy0, fs, fs, fill="none", stroke=MUTED, sw=1.6, rx=12))
    ms = 62

    def _spring(x1, y1, x2, y2):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = -(y2 - y1), (x2 - x1)
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L * 8, ny / L * 8
        return polyline([(x1, y1), (mx + nx, my + ny), (mx - nx, my - ny), (x2, y2)],
                        color=MUTED, sw=1.8)

    f.append(_spring(cx - ms, cy, fx0, cy))
    f.append(_spring(cx + ms, cy, fx0 + fs, cy))
    f.append(_spring(cx, cy - ms, cx, fy0))
    f.append(_spring(cx, cy + ms, cx, fy0 + fs))
    f.append(rect(cx - ms, cy - ms, 2 * ms, 2 * ms, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    f.append(text(cx, cy - 3, "інерційна", size=12, color=INK))
    f.append(text(cx, cy + 14, "маса m", size=12, color=INK))

    # привід — двобічна горизонтальна (x)
    f.append(darrow(cx - 50, 158, cx + 50, 158, color=NEG, sw=3, head=11))
    f.append(text(cx, 146, "v — привід (x)", size=12, bold=True, color=NEG))
    # коріолісова сила — двобічна вертикальна (y), праворуч від маси
    f.append(darrow(cx + 95, cy - 46, cx + 95, cy + 46, color=POS, sw=3, head=11))
    f.append(text(cx + 104, cy - 6, "F_К", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(cx + 104, cy + 12, "сенс (y)", size=11, color=POS, anchor="start"))
    # ω — вісь із площини
    f.append(circle(fx0 + 40, fy0 + 44, 9, fill=BG, stroke=FIELD, sw=2))
    f.append(circle(fx0 + 40, fy0 + 44, 2.4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(arc_arrow(fx0 + 40, fy0 + 44, 20, 205, 330, color=FIELD, sw=2.1, head=8))
    f.append(text(fx0 + 58, fy0 + 40, "ω", size=15, bold=True, italic=True, color=FIELD, anchor="start"))
    f.append(text(fx0 + 58, fy0 + 55, "(вісь ⊙)", size=10, color=MUTED, anchor="start"))

    # права колонка — причиновий ланцюг
    rx, rw = 434, 344
    rcx = rx + rw / 2
    f.append(fitbox(rx, 108, rw, 50, "v — швидкість приводу (стала амплітуда)",
                    size=12, pad=9, fill=FILL, stroke=NEG, sw=1.4, bold=True))
    f.append(varrow(rcx, 158, rcx, 176, color=MUTED, sw=2, head=8))
    f.append(fitbox(rx, 176, rw, 50, "ω — обертання корпусу (це й шукаємо)",
                    size=12, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True))
    f.append(varrow(rcx, 226, rcx, 244, color=MUTED, sw=2, head=8))
    f.append(fitbox(rx, 244, rw, 52, "F_К = 2mΩv   —   бічна сила, ⟂ до v",
                    size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.4, bold=True))
    f.append(varrow(rcx, 296, rcx, 320, color=MUTED, sw=2, head=8))
    f.append(fitbox(rx, 320, rw, 56, "амплітуда коливань по y ∝ ω\n→ знімає ємнісний давач",
                    size=12, pad=9, fill=FILL, stroke=INK, sw=1.4, bold=True))

    b, w, h = textbox(cx, 418, "ω = 0 → лише рух по x;   ω ≠ 0 → домішок по y ∝ ω",
                      size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "gyro-principle.svg"), W, H, *f)


# ── Фігура (comp): зчитувальний тракт — синхронне детектування ────────────────
def fig_gyro_readout():
    W, H = 880, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Зчитувальний тракт: демодуляція сенсу на частоті приводу",
                  size=15, bold=True))

    ym = 150

    def blk(cx, w, label, stroke, fill=FILL, cy=ym, h=64):
        return fitbox(cx - w / 2, cy - h / 2, w, h, label, size=12, pad=7,
                      fill=fill, stroke=stroke, sw=1.6, bold=True)

    S = (95, 120)      # МЕМС
    CA = (258, 104)    # зарядовий підсилювач
    DM = (418, 118)    # демодулятор
    LP = (566, 96)     # ФНЧ
    SC = (706, 112)    # масштаб/калібр
    f.append(blk(S[0], S[1], "МЕМС-структура\n(привід + сенс)", INK, h=74))
    f.append(blk(CA[0], CA[1], "зарядовий\nпідсилювач", NEG))
    f.append(blk(DM[0], DM[1], "синхронний\nдемодулятор ×", POS))
    f.append(blk(LP[0], LP[1], "ФНЧ\n(смуга)", FIELD))
    f.append(blk(SC[0], SC[1], "масштаб +\nкалібровка", INK))

    def between(a, aw, b, bw, y=ym):
        f.append(varrow(a + aw / 2, y, b - bw / 2, y, color=LINE, sw=2.4, head=10))

    between(*S, *CA); between(*CA, *DM); between(*DM, *LP); between(*LP, *SC)
    f.append(varrow(SC[0] + SC[1] / 2, ym, SC[0] + SC[1] / 2 + 40, ym, color=LINE, sw=2.4, head=10))
    f.append(text(SC[0] + SC[1] / 2 + 46, ym - 6, "Ω", size=15, bold=True, anchor="start"))
    f.append(text(SC[0] + SC[1] / 2 + 46, ym + 12, "у шину", size=11, color=MUTED, anchor="start"))

    # мітки несучої
    f.append(text((S[0] + CA[0]) / 2 + 8, ym - 22, "на несучій ω_пр", size=10, color=MUTED))
    f.append(text((DM[0] + LP[0]) / 2, ym - 22, "базова смуга", size=10, color=MUTED))

    # контур приводу знизу + опорна фаза в демодулятор
    DRV = (95, 300, 150, 54)   # cx, cy, w, h
    f.append(fitbox(DRV[0] - DRV[2] / 2, DRV[1] - DRV[3] / 2, DRV[2], DRV[3],
                    "контур приводу:\nAGC + ФАПЧ", size=12, pad=7, fill="#eef1fb",
                    stroke=NEG, sw=1.5, bold=True))
    f.append(varrow(S[0] - 18, ym + 37, DRV[0] - 18, DRV[1] - DRV[3] / 2, color=LINE, sw=2, head=8))
    f.append(varrow(DRV[0] + 18, DRV[1] - DRV[3] / 2, S[0] + 18, ym + 37, color=LINE, sw=2, head=8))
    f.append(text(S[0] + 40, (ym + 37 + DRV[1] - 27) / 2 + 4, "тримає v сталим", size=10,
                  color=MUTED, anchor="start"))
    # опорна фаза → демодулятор (зелений пунктир)
    f.append(line(DRV[0] + DRV[2] / 2, DRV[1] - 8, DM[0], DM[1] + DM[3] if False else ym + 32,
                  color=FIELD, sw=2, dash="6 4"))
    f.append(head_at(DM[0], ym + 32, 0, -1, FIELD, 9))
    f.append(text(300, 250, "опорна фаза приводу", size=11, color=FIELD, anchor="start"))

    b, w, h = textbox(W / 2, H - 20,
                      "демодуляція множить сенс на опорний сигнал приводу — це синхронний підсилювач (lock-in)",
                      size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "gyro-readout.svg"), W, H, *f)


# ── Фігура (comp): Коріоліс проти квадратури (фаза 90°) ───────────────────────
def fig_gyro_quadrature():
    W, H = 830, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Коріоліс і квадратура: та сама частота, зсув на 90° — розділяє фаза",
                  size=15, bold=True))

    # ── ліворуч: x(t) і v(t) на одній осі часу ──
    x0, x1, yc, A = 60, 420, 170, 70
    f.append(line(x0, yc, x1 + 8, yc, color=MUTED, sw=1.4))
    f.append(text(x1 + 12, yc + 4, "t", size=12, color=MUTED, anchor="start"))
    f.append(polyline(_sine(x0, x1, yc, A, math.pi / 2), color=NEG, sw=2.6))   # x=cos
    f.append(polyline(_sine(x0, x1, yc, A * 0.86, math.pi), color=FIELD, sw=2.6))  # v=−sin
    f.append(text(x0 + 4, yc - A - 14, "x(t) — зсув приводу (сюди синфазна квадратура)",
                  size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(x0 + 4, yc + A + 24, "v(t) — швидкість (сюди синфазний Коріоліс)",
                  size=12, bold=True, color=FIELD, anchor="start"))
    f.append(fitbox(x0, yc + A + 40, 360, 42,
                    "та сама частота — рознесені на 90°",
                    size=12, pad=7, fill=FILL, stroke=INK, sw=1.3, bold=True))

    # ── праворуч: фазова діаграма ──
    pcx, pcy, R = 630, 200, 96
    f.append(line(pcx - R - 14, pcy, pcx + R + 14, pcy, color=MUTED, sw=1.4))    # вісь v (Коріоліс)
    f.append(line(pcx, pcy + R + 14, pcx, pcy - R - 14, color=MUTED, sw=1.4))    # вісь x (квадратура)
    f.append(text(pcx + R + 18, pcy + 4, "фаза v", size=11, color=POS, anchor="start"))
    f.append(text(pcx + R + 18, pcy + 18, "(Коріоліс)", size=10, color=POS, anchor="start"))
    f.append(text(pcx + 6, pcy - R - 6, "фаза x (квадратура)", size=11, color=NEG, anchor="start"))
    # вектор Коріоліса (малий, ∝ω) уздовж осі v
    f.append(varrow(pcx, pcy, pcx + 58, pcy, color=POS, sw=3.2, head=11))
    f.append(text(pcx + 30, pcy + 20, "∝ ω", size=12, bold=True, color=POS))
    # вектор квадратури (великий) уздовж осі x
    f.append(varrow(pcx, pcy, pcx, pcy - 84, color=NEG, sw=3.2, head=11))
    f.append(text(pcx - 8, pcy - 60, "квадратура", size=11, bold=True, color=NEG, anchor="end"))
    # вісь демодуляції з малою похибкою фази θ
    th = math.radians(24)
    dxx, dyy = math.cos(th), -math.sin(th)
    f.append(line(pcx, pcy, pcx + (R + 6) * dxx, pcy + (R + 6) * dyy, color=INK, sw=1.8, dash="5 4"))
    f.append(head_at(pcx + (R + 6) * dxx, pcy + (R + 6) * dyy, dxx, dyy, INK, 9))
    f.append(text(pcx + 30, pcy - 74, "вісь демодуляції", size=10, color=INK, anchor="start"))
    f.append(text(pcx + 12, pcy - 12, "θ", size=13, bold=True, italic=True, anchor="start"))

    b, w, h = textbox(W / 2, H - 24,
                      ["демодуляція за фазою приводу бере Коріоліс і глушить квадратуру;",
                       "похибка фази θ підмішує квадратуру (cos → sin θ)"],
                      size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "gyro-quadrature.svg"), W, H, *f)


# ── Фігура (comp): дві топології — камертон і кільце ──────────────────────────
def fig_gyro_topologies():
    W, H = 830, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Дві топології класу: камертон і кільце (келихова мода)",
                  size=15, bold=True))

    # ── ЛІВОРУЧ: камертон ──
    f.append(text(200, 62, "камертон", size=14, bold=True, color=INK))
    baseY = 320
    f.append(rect(140, baseY, 120, 22, fill="#eef2f7", stroke=INK, sw=1.8, rx=5))
    # дві голки
    for tx in (162, 238):
        f.append(rect(tx - 12, 150, 24, baseY - 150, fill="#eef2f7", stroke=INK, sw=1.8, rx=6))
        f.append(circle(tx, 150, 15, fill="#eef2f7", stroke=INK, sw=1.8))
    # привід: протифазні горизонтальні стрілки
    f.append(varrow(150, 240, 128, 240, color=NEG, sw=2.6, head=10))
    f.append(varrow(250, 240, 272, 240, color=NEG, sw=2.6, head=10))
    f.append(text(200, 300, "привід: протифазні коливання", size=11, color=NEG))
    # ω уздовж стебла (вертикальна вісь)
    f.append(varrow(200, baseY + 22, 200, baseY + 58, color=FIELD, sw=3, head=11))
    f.append(text(212, baseY + 46, "ω", size=14, bold=True, italic=True, color=FIELD, anchor="start"))
    # коріоліс: протифазно з площини (⊙ / ⊗)
    f.append(circle(162, 150, 6, fill=BG, stroke=POS, sw=2))
    f.append(circle(162, 150, 1.8, fill=POS, stroke=POS, sw=1))
    f.append(line(238 - 4, 150 - 4, 238 + 4, 150 + 4, color=POS, sw=2))
    f.append(line(238 - 4, 150 + 4, 238 + 4, 150 - 4, color=POS, sw=2))
    f.append(text(162, 128, "⊙", size=13, bold=True, color=POS))
    f.append(text(238, 128, "⊗", size=13, bold=True, color=POS))
    f.append(text(200, 108, "коріоліс: протифазно з площини", size=11, color=POS))
    f.append(fitbox(70, 356, 260, 46, "різницевий сигнал глушить спільну заваду\n(удар, лінійне g)",
                    size=11, pad=7, fill=FILL, stroke=INK, sw=1.3, bold=True))

    # ── ПРАВОРУЧ: кільце ──
    f.append(text(620, 62, "кільце", size=14, bold=True, color=INK))
    cx, cy, R = 620, 210, 92
    f.append(circle(cx, cy, R, fill="none", stroke=INK, sw=6))
    # мода приводу — еліпс, витягнутий горизонтально
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="5 4"/>' % (cx, cy, R + 16, R - 16, NEG))
    # мода сенсу — той самий еліпс, повернутий на 45°
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="5 4" transform="rotate(-45 %.1f %.1f)"/>'
             % (cx, cy, R + 16, R - 16, POS, cx, cy))
    for a in (0, 90, 180, 270):
        ax = cx + R * math.cos(math.radians(a)); ay = cy - R * math.sin(math.radians(a))
        f.append(circle(ax, ay, 4.5, fill=NEG, stroke=NEG, sw=1))
    for a in (45, 135, 225, 315):
        ax = cx + R * math.cos(math.radians(a)); ay = cy - R * math.sin(math.radians(a))
        f.append(circle(ax, ay, 4.5, fill=POS, stroke=POS, sw=1))
    # ω у центрі
    f.append(circle(cx, cy, 9, fill=BG, stroke=FIELD, sw=2))
    f.append(circle(cx, cy, 2.4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(arc_arrow(cx, cy, 24, 210, 330, color=FIELD, sw=2.1, head=8))
    f.append(text(cx + 20, cy + 4, "ω", size=13, bold=True, italic=True, color=FIELD, anchor="start"))
    f.append(text(cx - R - 6, cy - R - 4, "привід", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(cx + R - 30, cy - R - 4, "сенс (45°)", size=11, bold=True, color=POS, anchor="start"))
    f.append(fitbox(490, 356, 270, 46, "вісесиметрія → можна міряти КУТ прямо\n(обертання переганяє хвилю — ефект Браяна)",
                    size=11, pad=7, fill=FILL, stroke=INK, sw=1.3, bold=True))
    return render(os.path.join(IMG, "gyro-topologies.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_turntable(), fig_hemispheres(), fig_earth(), fig_timeline(),
          fig_transport(), fig_factor2(),
          fig_gyro_principle(), fig_gyro_readout(), fig_gyro_quadrature(),
          fig_gyro_topologies()]
    print("written:")
    for p in ps:
        print("  ", p)
