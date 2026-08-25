# -*- coding: utf-8 -*-
"""Фігури до теми «Загальна теорія відносності».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"
COLOR_DARK = "#2c3e50"

def helper_polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts, fill, stroke, sw)

def helper_path(d, color=None, stroke=None, sw=1.5, fill="none", dash=None):
    c = stroke or color or LINE
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d, c, sw, fill, d_attr)

def helper_ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))

polygon = helper_polygon
path = helper_path
ellipse = helper_ellipse


# ── Фігура 1: Принцип еквівалентності (мисленнєвий експеримент з ліфтом) ───
def fig_equivalence_elevator():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Принцип еквівалентності Ейнштейна: гравітація проти прискорення", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # Ліва частина: Кабіна на Землі
    cx1, cy1 = 190, 200
    f.append(rect(cx1 - 100, cy1 - 120, 200, 240, fill="#f8f9fa", stroke=COLOR_DARK, sw=2.2, rx=6))
    f.append(text(cx1, cy1 - 130, "А. Кабіна у полі тяжіння Землі (g)", size=13, bold=True, color=COLOR_DARK))

    # Спрощена постать спостерігача (кола + лінії)
    f.append(circle(cx1 - 40, cy1 - 20, 14, fill="#ebf5fb", stroke=COLOR_BLUE, sw=1.8))
    f.append(line(cx1 - 40, cy1 - 6, cx1 - 40, cy1 + 45, color=COLOR_BLUE, sw=2))
    f.append(line(cx1 - 40, cy1 + 45, cx1 - 55, cy1 + 90, color=COLOR_BLUE, sw=2))
    f.append(line(cx1 - 40, cy1 + 45, cx1 - 25, cy1 + 90, color=COLOR_BLUE, sw=2))
    f.append(line(cx1 - 40, cy1 + 10, cx1 - 15, cy1 + 30, color=COLOR_BLUE, sw=2))

    # Яблуко, що падає
    f.append(circle(cx1 + 35, cy1 + 20, 10, fill="#fdecea", stroke=COLOR_RED, sw=1.8))
    f.append(arrow(cx1 + 35, cy1 + 32, cx1 + 35, cy1 + 75, color=COLOR_RED, sw=2))
    f.append(text(cx1 + 50, cy1 + 55, "a = g", size=12, bold=True, color=COLOR_RED, anchor="start"))

    # Вектор g ззовні
    f.append(arrow(cx1 + 80, cy1 - 80, cx1 + 80, cy1 - 30, color=COLOR_ORANGE, sw=2.2))
    f.append(text(cx1 + 88, cy1 - 55, "g", size=14, bold=True, color=COLOR_ORANGE, anchor="start"))

    b1, w1, h1 = textbox(cx1, 355, "Тіло падає з прискоренням g під дією маси Землі",
                          size=11, pad=6, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b1)

    # Права частина: Прискорена кабіна в космосі
    cx2, cy2 = 570, 200
    f.append(rect(cx2 - 100, cy2 - 120, 200, 240, fill="#f8f9fa", stroke=COLOR_DARK, sw=2.2, rx=6))
    f.append(text(cx2, cy2 - 130, "Б. Кабіна у космосі з прискоренням a = g", size=13, bold=True, color=COLOR_DARK))

    # Спостерігач
    f.append(circle(cx2 - 40, cy2 - 20, 14, fill="#ebf5fb", stroke=COLOR_BLUE, sw=1.8))
    f.append(line(cx2 - 40, cy2 - 6, cx2 - 40, cy2 + 45, color=COLOR_BLUE, sw=2))
    f.append(line(cx2 - 40, cy2 + 45, cx2 - 55, cy2 + 90, color=COLOR_BLUE, sw=2))
    f.append(line(cx2 - 40, cy2 + 45, cx2 - 25, cy2 + 90, color=COLOR_BLUE, sw=2))
    f.append(line(cx2 - 40, cy2 + 10, cx2 - 15, cy2 + 30, color=COLOR_BLUE, sw=2))

    # Яблуко відпущене
    f.append(circle(cx2 + 35, cy2 + 20, 10, fill="#fdecea", stroke=COLOR_RED, sw=1.8))
    f.append(arrow(cx2 + 35, cy2 + 32, cx2 + 35, cy2 + 75, color=COLOR_RED, sw=2))
    f.append(text(cx2 + 50, cy2 + 55, "a_rel = g", size=12, bold=True, color=COLOR_RED, anchor="start"))

    # Вектор прискорення кабіни вгору
    f.append(arrow(cx2 + 80, cy2 + 50, cx2 + 80, cy2 - 10, color=COLOR_GREEN, sw=2.2))
    f.append(text(cx2 + 88, cy2 + 20, "a = g", size=14, bold=True, color=COLOR_GREEN, anchor="start"))

    b2, w2, h2 = textbox(cx2, 355, "Підлога доганяє тіло — ефект тотожний гравітації!",
                          size=11, pad=6, fill="#eafaf1", stroke="#a3e4d7", sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "equivalence-elevator.svg"), W, H, *f)


# ── Фігура 2: Викривлення простору-часу та гравітаційне лінзування ─────────
def fig_curved_spacetime_light():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Викривлення простору-часу та гравітаційне відхилення світла", size=16, bold=True))

    cx, cy = 380, 210

    # Сітка простору (горизонтальні та вертикальні лінії з прогином)
    for y_off in [-100, -50, 0, 50, 100]:
        y_base = cy + y_off
        bend = 40.0 / (1.0 + ((y_off / 60.0)**2)) if abs(y_off) < 120 else 0
        d_str = "M 60 %d Q %d %d 700 %d" % (y_base, cx, y_base + bend, y_base)
        f.append(path(d_str, color="#d0d7de", sw=1.2, fill="none"))

    for x_off in [-260, -180, -100, -20, 60, 140, 220, 300]:
        x_base = cx + x_off
        f.append(line(x_base, cy - 120, x_base, cy + 120, color="#d0d7de", sw=1.2))

    # Центральне масивне тіло
    f.append(circle(cx, cy, 32, fill="#fef9e7", stroke=COLOR_ORANGE, sw=2.5))
    f.append(text(cx, cy + 5, "Маса M", size=12, bold=True, color=COLOR_ORANGE))

    # Віддалена зоря
    star_x, star_y = 90, 110
    f.append(circle(star_x, star_y, 8, fill="#fbcfe8", stroke=COLOR_PURPLE, sw=2))
    f.append(text(star_x - 15, star_y - 12, "Справжня зоря", size=11, bold=True, color=COLOR_PURPLE, anchor="middle"))

    # Спостерігач на Землі
    obs_x, obs_y = 670, 110
    f.append(circle(obs_x, obs_y, 10, fill="#dbeafe", stroke=COLOR_BLUE, sw=2))
    f.append(text(obs_x, obs_y + 24, "Спостерігач (Земля)", size=11, bold=True, color=COLOR_BLUE))

    # Справжня викривлена траєкторія світла (геодезична)
    f.append(path("M %d %d Q %d %d %d %d" % (star_x, star_y, cx, cy - 75, obs_x, obs_y),
                  color=COLOR_RED, sw=2.5, fill="none"))
    f.append(text(cx, cy - 85, "Викривлений промінь (геодезична)", size=11, bold=True, color=COLOR_RED))

    # Уявна пряма траєкторія для спостерігача
    f.append(line(obs_x, obs_y, star_x - 30, star_y - 45, color=COLOR_PURPLE, sw=1.6, dash="5,4"))
    f.append(circle(star_x - 30, star_y - 45, 6, fill="none", stroke=COLOR_PURPLE, sw=1.6))
    f.append(text(star_x - 30, star_y - 58, "Уявне положення зорі", size=10, bold=True, color=COLOR_PURPLE, anchor="middle"))

    # Кут відхилення theta
    f.append(text(obs_x - 110, obs_y - 18, "Кут відхилення θ = 4GM / (c² b)", size=11, bold=True, color=COLOR_DARK, anchor="end"))

    b, w, h = textbox(W / 2, 350,
                      "Маса викривляє геометрію простору-часу. Світло рухається по найкоротшій лінії (геодезичній),\nяка здається викривленою для плоского спостерігача Евкліда.",
                      size=11, pad=7, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "curved-spacetime-light.svg"), W, H, *f)


# ── Фігура 3: Прецесія перигелію Меркурія ──────────────────────────────────
def fig_precession_mercury_orbit():
    W, H = 760, 390
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Аномальна прецесія перигелію орбіти в релятивістському полі", size=16, bold=True))

    midx = 240
    cy = 200

    # Сонце в фокусі
    sun_x, sun_y = midx - 30, cy
    f.append(circle(sun_x, sun_y, 22, fill="#fef9e7", stroke=COLOR_ORANGE, sw=2.5))
    f.append(text(sun_x, sun_y + 5, "Сонце", size=11, bold=True, color=COLOR_ORANGE))

    # Ньютонівська замкнена орбіта (пунктир)
    f.append(ellipse(midx, cy, 130, 80, fill="none", stroke=COLOR_BLUE, sw=1.6, dash="5,4"))
    f.append(text(midx - 30, cy + 98, "Ньютонівська орбіта", size=10, bold=True, color=COLOR_BLUE, anchor="middle"))

    # Релятивістська прецесуюча орбіта
    f.append(ellipse(midx + 12, cy - 12, 130, 80, fill="none", stroke=COLOR_RED, sw=2))
    f.append(ellipse(midx + 24, cy - 24, 130, 80, fill="none", stroke=COLOR_RED, sw=1.5, dash="4,3"))

    # Позначення зсуву перигелію
    f.append(arrow(sun_x, sun_y, midx + 130, cy, color=COLOR_BLUE, sw=1.4))
    f.append(arrow(sun_x, sun_y, midx + 142, cy - 12, color=COLOR_RED, sw=1.4))
    f.append(text(midx + 145, cy - 30, "Зсув Δφ", size=11, bold=True, color=COLOR_RED, anchor="start"))

    # Планета Меркурій
    f.append(circle(midx + 142, cy - 12, 7, fill="#e2e8f0", stroke=COLOR_DARK, sw=1.8))
    f.append(text(midx + 155, cy + 5, "Меркурій", size=10, bold=True, color=COLOR_DARK, anchor="start"))

    # Пояснювальний блок праворуч
    b, w, h = textbox(595, 190,
                      "Ньютонівська механіка (1/r²):\nОрбіта строго замкнена (еліпс).\n\nЗагальна теорія відносності:\nПотенціал має поправку ~ 1/r³.\n\nНаслідок — прецесія перигелію:\nΔφ = 6πGM / [c² a (1 − e²)]\n\nДля Меркурія: 43.03 кубових\nсекунд на століття (збіг із спостереженнями!).",
                      size=11, pad=10, fill="#eafaf1", stroke="#a3e4d7", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "precession-mercury-orbit.svg"), W, H, *f)


if __name__ == '__main__':
    fig_equivalence_elevator()
    fig_curved_spacetime_light()
    fig_precession_mercury_orbit()
    print("Усі 3 фігури згенеровано успішно у ./img/")
