# -*- coding: utf-8 -*-
"""Фігури до теми «Спіральна антена».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

WAVE = "#c0392b"     # електричне поле / хвиля
AXIS_COL = "#2457d6" # осьовий напрямок / режим
HELIX_COL = "#1a1a1a"# провідник спіралі

# ── 1. Геометрія спіральної антени та розгортка витка ──────────────────────
def fig_geometry():
    W, H = 760, 380
    f = [text(W / 2, 25, "Геометричні параметри спіральної антени", size=16, bold=True)]

    # Ліва частина: 3D-схема спіралі на екранній площині
    # Екран (Ground Plane)
    gp_x = 100
    gp_y1, gp_y2 = 70, 310
    f.append(line(gp_x, gp_y1, gp_x, gp_y2, color=MUTED, sw=4))
    f.append(mtext(gp_x - 10, 180, "Рефлектор (Ground Plane)\nD >= 0.75 lambda", size=11, color=MUTED, anchor="end"))

    # Вісь спіралі
    f.append(line(gp_x, 190, 440, 190, color=MUTED, sw=1, dash="4,4"))
    f.append(text(450, 194, "Вісь z", size=11, color=MUTED, anchor="start"))

    # Спіраль (4 витки)
    x0 = gp_x + 20
    y0 = 190
    radius = 50
    spacing = 65
    n_turns = 4

    # Малюємо спіраль покроково
    n_seg = 60
    pts = []
    for i in range(n_turns * n_seg + 1):
        t = i / n_seg
        x = x0 + t * spacing
        ang = 2 * math.pi * t
        y = y0 - radius * math.sin(ang)
        pts.append((x, y, math.cos(ang)))

    for i in range(len(pts) - 1):
        x1, y1, z1 = pts[i]
        x2, y2, z2 = pts[i+1]
        col = HELIX_COL if z1 + z2 >= 0 else MUTED
        sw = 2.8 if z1 + z2 >= 0 else 1.5
        f.append(line(x1, y1, x2, y2, color=col, sw=sw))

    # Коаксіальне живлення
    f.append(line(gp_x - 30, y0, gp_x + 20, y0, color=WAVE, sw=3))
    f.append(circle(gp_x, y0, 4, fill=WAVE, stroke=WAVE, sw=1))
    f.append(text(gp_x + 10, y0 + 20, "Живлення", size=11, color=WAVE, bold=True, anchor="start"))

    # Позначення розмірів на спіралі
    # Крок S
    x_t1 = x0 + 1 * spacing
    x_t2 = x0 + 2 * spacing
    f.append(line(x_t1, y0 + radius + 15, x_t2, y0 + radius + 15, color=AXIS_COL, sw=1.5))
    f.append(line(x_t1, y0 + radius + 8, x_t1, y0 + radius + 22, color=AXIS_COL, sw=1.5))
    f.append(line(x_t2, y0 + radius + 8, x_t2, y0 + radius + 22, color=AXIS_COL, sw=1.5))
    f.append(text((x_t1 + x_t2) / 2, y0 + radius + 32, "Крок S", size=12, color=AXIS_COL, bold=True))

    # Діаметр D
    f.append(line(x0 + 0.5 * spacing, y0 - radius, x0 + 0.5 * spacing, y0 + radius, color=AXIS_COL, sw=1.5))
    f.append(line(x0 + 0.5 * spacing - 6, y0 - radius, x0 + 0.5 * spacing + 6, y0 - radius, color=AXIS_COL, sw=1.5))
    f.append(line(x0 + 0.5 * spacing - 6, y0 + radius, x0 + 0.5 * spacing + 6, y0 + radius, color=AXIS_COL, sw=1.5))
    f.append(text(x0 + 0.5 * spacing - 12, y0, "Діаметр D", size=12, color=AXIS_COL, bold=True, anchor="end"))

    # Загальна довжина L
    x_end = x0 + n_turns * spacing
    f.append(line(x0, y0 - radius - 25, x_end, y0 - radius - 25, color=INK, sw=1.5))
    f.append(line(x0, y0 - radius - 32, x0, y0 - radius - 18, color=INK, sw=1.5))
    f.append(line(x_end, y0 - radius - 32, x_end, y0 - radius - 18, color=INK, sw=1.5))
    f.append(text((x0 + x_end) / 2, y0 - radius - 33, "Довжина L = N · S", size=12, bold=True))

    # Права частина: Трикутник розгортки одного витка
    tr_x = 520
    tr_y = 280
    tr_w = 180  # Довжина кола C = pi*D
    tr_h = 100  # Крок S

    # Трикутник
    f.append(line(tr_x, tr_y, tr_x + tr_w, tr_y, color=INK, sw=2))  # катет C
    f.append(line(tr_x + tr_w, tr_y, tr_x + tr_w, tr_y - tr_h, color=INK, sw=2))  # катет S
    f.append(line(tr_x, tr_y, tr_x + tr_w, tr_y - tr_h, color=AXIS_COL, sw=2.5))  # гіпотенуза L0

    # Дуга кута нахилу alpha
    f.append(line(tr_x + 40, tr_y, tr_x + 38, tr_y - 20, color=WAVE, sw=1.5))
    f.append(text(tr_x + 55, tr_y - 8, "alpha", size=13, color=WAVE, bold=True, italic=True))

    # Підписи сторін
    f.append(text(tr_x + tr_w / 2, tr_y + 20, "Довжина кола C = pi · D", size=12, bold=True))
    f.append(text(tr_x + tr_w + 12, tr_y - tr_h / 2, "Крок S", size=12, bold=True, anchor="start"))
    f.append(text(tr_x + tr_w / 2 - 20, tr_y - tr_h / 2 - 10, "Довжина витка L0", size=12, color=AXIS_COL, bold=True))

    render(os.path.join(IMG, "helix-geometry.svg"), W, H, *f)


# ── 2. Порівняння режимів випромінювання (Нормальний vs Осьовий) ────────────
def fig_modes():
    W, H = 760, 360
    f = [text(W / 2, 25, "Режими випромінювання спіральної антени", size=16, bold=True)]

    # Ліва панель: Нормальний режим (Broadside, C << lambda)
    cL_x = 190
    cL_y = 200

    # Заголовок панелі
    f.append(text(cL_x, 60, "Нормальний режим (Broadside)", size=14, bold=True))
    f.append(text(cL_x, 78, "C << lambda  (C < 0.2 lambda)", size=12, color=MUTED))

    # Маленька спіраль у центрі
    f.append(line(cL_x - 30, cL_y, cL_x + 30, cL_y, color=INK, sw=3))
    f.append(line(cL_x - 30, cL_y + 30, cL_x - 30, cL_y - 30, color=MUTED, sw=3)) # рефлектор

    # ДН (вісімка перпендикулярно осі)
    pts8_top = []
    pts8_bot = []
    for a in range(-90, 91):
        rad = math.radians(a)
        r = 75 * math.cos(rad)
        x_t = cL_x + r * math.sin(rad)
        y_t = cL_y - r * math.cos(rad)
        pts8_top.append("%.1f,%.1f" % (x_t, y_t))
        x_b = cL_x + r * math.sin(rad)
        y_b = cL_y + r * math.cos(rad)
        pts8_bot.append("%.1f,%.1f" % (x_b, y_b))

    f.append('<polygon points="%s" fill="%s" fill-opacity="0.15" stroke="%s" stroke-width="2"/>' %
             (" ".join(pts8_top), WAVE, WAVE))
    f.append('<polygon points="%s" fill="%s" fill-opacity="0.15" stroke="%s" stroke-width="2"/>' %
             (" ".join(pts8_bot), WAVE, WAVE))

    f.append(arrow(cL_x, cL_y, cL_x, cL_y - 85, color=WAVE, sw=2))
    f.append(arrow(cL_x, cL_y, cL_x, cL_y + 85, color=WAVE, sw=2))
    f.append(text(cL_x, cL_y - 95, "Випромінювання убоки", size=11, color=WAVE, bold=True))
    f.append(mtext(cL_x, cL_y + 110, "Низький коефіцієнт підсилення\nЛінійна / еліптична поляризація", size=11, color=INK))

    # Розділювач панелей
    f.append(line(380, 50, 380, 330, color=MUTED, sw=1, dash="4,4"))

    # Права панель: Осьовий режим (Axial / End-fire, C ~ lambda)
    cR_x = 480
    cR_y = 200

    f.append(text(cR_x + 90, 60, "Осьовий режим (End-fire)", size=14, bold=True))
    f.append(text(cR_x + 90, 78, "C ~ lambda  (0.75 lambda < C < 1.33 lambda)", size=12, color=MUTED))

    # Спіраль вздовж осі
    f.append(line(cR_x - 40, cR_y + 35, cR_x - 40, cR_y - 35, color=MUTED, sw=3)) # рефлектор
    # малюємо спіраль
    sp_pts = []
    for i in range(120):
        t = i / 30.0
        x = cR_x - 30 + t * 25
        y = cR_y + 22 * math.sin(2 * math.pi * t)
        sp_pts.append((x, y))
    for i in range(len(sp_pts)-1):
        f.append(line(sp_pts[i][0], sp_pts[i][1], sp_pts[i+1][0], sp_pts[i+1][1], color=HELIX_COL, sw=2.2))

    # Спрямована ДН вздовж осі (вузька пелюстка праворуч)
    lobe_pts = []
    for a in range(-80, 81):
        rad = math.radians(a)
        r = 140 * (math.cos(rad) ** 4)
        x_l = (cR_x + 70) + r * math.cos(rad)
        y_l = cR_y + r * math.sin(rad)
        lobe_pts.append("%.1f,%.1f" % (x_l, y_l))

    f.append('<polygon points="%s" fill="%s" fill-opacity="0.18" stroke="%s" stroke-width="2.5"/>' %
             (" ".join(lobe_pts), AXIS_COL, AXIS_COL))

    f.append(arrow(cR_x + 70, cR_y, cR_x + 220, cR_y, color=AXIS_COL, sw=2.5))
    f.append(text(cR_x + 160, cR_y - 15, "Максимум уздовж осі", size=12, color=AXIS_COL, bold=True))

    f.append(mtext(cR_x + 160, cR_y + 110, "Високе підсилення (10-18 дБ)\nКругова поляризація (RHCP/LHCP)", size=11, color=INK))

    render(os.path.join(IMG, "helix-modes.svg"), W, H, *f)


# ── 3. Узгодження імпедансу спіральної антени ───────────────────────────────
def fig_matching():
    W, H = 760, 320
    f = [text(W / 2, 25, "Методи імпедансного узгодження (140 Ом -> 50 Ом)", size=16, bold=True)]

    # Метод 1: Стрічковий плавний трансформатор (Tapered Strip)
    x1, y1 = 60, 65
    w1, h1 = 300, 220
    f.append(rect(x1, y1, w1, h1, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + w1/2, y1 + 24, "1. Стрічковий плавник (Taper)", size=13, bold=True))

    # Рефлектор
    f.append(line(x1 + 30, y1 + 60, x1 + 30, y1 + 180, color=MUTED, sw=4))
    # Стрічка плавного звуження від спіралі до коаксіалу
    tap_pts = "%d,%d %d,%d %d,%d %d,%d" % (
        x1 + 30, y1 + 115,
        x1 + 110, y1 + 105,
        x1 + 110, y1 + 135,
        x1 + 30, y1 + 125
    )
    f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (tap_pts, AXIS_COL, AXIS_COL))
    # Спіральний провідник від кінця трансформатора
    sp_pts = []
    for i in range(40):
        t = i / 10.0
        x = x1 + 110 + t * 15
        y = y1 + 120 + 20 * math.sin(2 * math.pi * t)
        sp_pts.append((x, y))
    for i in range(len(sp_pts)-1):
        f.append(line(sp_pts[i][0], sp_pts[i][1], sp_pts[i+1][0], sp_pts[i+1][1], color=HELIX_COL, sw=2))

    f.append(text(x1 + 30, y1 + 198, "50 Ом (Вхід)", size=11, color=WAVE, bold=True))
    f.append(text(x1 + 215, y1 + 198, "140 Ом (Спіраль)", size=11, color=AXIS_COL, bold=True))

    # Метод 2: Чвертьхвильовий трансформатор (Quarter-wave Transformer)
    x2, y2 = 400, 65
    w2, h2 = 300, 220
    f.append(rect(x2, y2, w2, h2, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x2 + w2/2, y2 + 24, "2. Чвертьхвильовий відрізок lambda/4", size=13, bold=True))

    # Рефлектор
    f.append(line(x2 + 30, y2 + 60, x2 + 30, y2 + 180, color=MUTED, sw=4))
    # Відрізок lambda/4 із Z0 = sqrt(50 * 140) = 83.7 Ом
    f.append(rect(x2 + 30, y2 + 112, 80, 16, fill=AXIS_COL, stroke=AXIS_COL, sw=1, rx=2))
    # Спіральний провідник від lambda/4
    sp_pts2 = []
    for i in range(40):
        t = i / 10.0
        x = x2 + 110 + t * 15
        y = y2 + 120 + 20 * math.sin(2 * math.pi * t)
        sp_pts2.append((x, y))
    for i in range(len(sp_pts2)-1):
        f.append(line(sp_pts2[i][0], sp_pts2[i][1], sp_pts2[i+1][0], sp_pts2[i+1][1], color=HELIX_COL, sw=2))

    f.append(text(x2 + 70, y2 + 102, "Z_0 = 83.7 Ом", size=11, color=INK, bold=True))
    f.append(text(x2 + 70, y2 + 143, "L = lambda / 4", size=11, color=INK, bold=True))
    f.append(text(x2 + 30, y2 + 198, "50 Ом", size=11, color=WAVE, bold=True))
    f.append(text(x2 + 215, y2 + 198, "140 Ом", size=11, color=AXIS_COL, bold=True))

    render(os.path.join(IMG, "matching.svg"), W, H, *f)


if __name__ == "__main__":
    fig_geometry()
    fig_modes()
    fig_matching()
    print("SVG фігури згенеровано успішно.")
