# -*- coding: utf-8 -*-
"""
figs-r11-s8-c-packages.py
Фігури до вставки 🔌 «Корпуси МК: DIP, QFP, QFN, BGA»
Теми: §4.11.8c — r11-s8-c-packages.md

fig-r11-8c-1-package-map.svg  — карта-вісь чотирьох класів за кроком і доступністю
fig-r11-8c-2-package-cross.svg — перетини DIP / QFP / QFN / BGA
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фіг 1: карта-вісь
# ─────────────────────────────────────────────────────────────────────────────
W1, H1 = 820, 380

# Кольори рівнів доступності
C_EASY   = "#d5f5e3"   # зелений — легко
C_MEDIUM = "#fef9c3"   # жовтий  — фен
C_HARD   = "#fde8d8"   # помаранч — важко
C_NOPE   = "#fde0e0"   # червоний — завод

STROKE_EASY   = "#27ae60"
STROKE_MEDIUM = "#f39c12"
STROKE_HARD   = "#e67e22"
STROKE_NOPE   = "#c0392b"

def fig1():
    parts = []

    # Заголовок
    parts.append(text(W1 / 2, 32, "Корпуси МК: крок виводів і складність ручного монтажу",
                      size=16, bold=True))

    # Підписи осей
    parts.append(text(W1 / 2, 60, "← менший крок, складніший монтаж —",
                      size=13, color=MUTED))

    # Вісь X (крок)
    axis_y = 310
    parts.append(arrow(60, axis_y, W1 - 40, axis_y, color=LINE, sw=2.0))
    parts.append(text(W1 - 30, axis_y + 5, "крок", size=12, color=MUTED, anchor="start"))

    # Чотири плашки (ліво → право = широкий крок → дрібний)
    boxes = [
        # (cx, ширина, назва, крок, монтаж, fill, stroke, підпис-монтаж)
        (130, 160, "DIP",  "2.54 мм",  "THT\nпанелька/наскрізь", C_EASY,   STROKE_EASY,  "легко"),
        (330, 160, "QFP",  "0.8 / 0.5 мм", "SMD\nніжки по периметру", C_MEDIUM, STROKE_MEDIUM, "фен не потрібен"),
        (530, 160, "QFN",  "0.5 / 0.4 мм", "SMD\nплощадки під краєм", C_HARD,   STROKE_HARD, "потрібен фен"),
        (720, 140, "BGA",  "≤ 0.8…0.35 мм", "Grid\nкульки під пузом", C_NOPE,  STROKE_NOPE, "лише завод"),
    ]

    BOX_H = 160
    for cx, bw, name, pitch, mount, fill, stroke, badge in boxes:
        by = 120
        # Основна рамка
        parts.append(rect(cx - bw/2, by, bw, BOX_H, fill=fill, stroke=stroke, sw=2, rx=10))
        # Назва корпусу
        parts.append(text(cx, by + 30, name, size=22, bold=True, color=INK))
        # Крок
        parts.append(text(cx, by + 56, pitch, size=12, color=MUTED))
        # Тип монтажу
        parts.append(mtext(cx, by + 90, mount.split("\n"), size=11, color=INK, lh=1.4))
        # Бейдж доступності
        badge_frag, bw2, bh2 = textbox(cx, by + BOX_H - 22, badge, size=11, pad=6,
                                        fill=fill, stroke=stroke, sw=1.5, color=stroke, bold=True)
        parts.append(badge_frag)

        # Крок-позначка на осі
        parts.append(line(cx, axis_y - 6, cx, axis_y + 6, color=stroke, sw=2))
        parts.append(text(cx, axis_y + 22, pitch.split("/")[0].strip(), size=10, color=stroke))

    # Підпис осі Y (вертикальний)
    parts.append(text(22, H1 / 2 - 30, "паяльна", size=12, color=MUTED))
    parts.append(text(22, H1 / 2 - 14, "доступність", size=12, color=MUTED))
    parts.append(arrow(22, H1 / 2 + 10, 22, 130, color=MUTED, sw=1.5))
    parts.append(text(22, H1 / 2 + 26, "↓ нижче", size=11, color=MUTED))

    # Підписи-легенди
    legend = [
        (C_EASY, STROKE_EASY, "Легко вдома"),
        (C_MEDIUM, STROKE_MEDIUM, "Прийнятно"),
        (C_HARD, STROKE_HARD, "Потрібен фен"),
        (C_NOPE, STROKE_NOPE, "Лише завод"),
    ]
    lx = 60
    for fill, stroke, label in legend:
        parts.append(rect(lx, H1 - 46, 14, 14, fill=fill, stroke=stroke, sw=1.5, rx=3))
        parts.append(text(lx + 20, H1 - 35, label, size=11, color=INK, anchor="start"))
        lx += 145

    render(os.path.join(IMG, "fig-r11-8c-1-package-map.svg"), W1, H1,
           *parts, title=None)
    print("fig-r11-8c-1-package-map.svg — OK")

fig1()


# ─────────────────────────────────────────────────────────────────────────────
# Фіг 2: перетини корпусів
# ─────────────────────────────────────────────────────────────────────────────
W2, H2 = 820, 340

def fig2():
    parts = []

    parts.append(text(W2 / 2, 28, "Де живе контакт — у перетині чотирьох корпусів",
                      size=16, bold=True))

    # Спільні параметри блоків
    block_w = 165
    gap = 22
    total_w = 4 * block_w + 3 * gap
    x0 = (W2 - total_w) / 2

    # Горизонтальна лінія — плата
    BOARD_Y = 230
    BOARD_H = 14
    # Плата повна ширина
    parts.append(rect(x0 - 10, BOARD_Y, total_w + 20, BOARD_H,
                      fill="#cfd8dc", stroke="#607d8b", sw=1.5, rx=0))
    parts.append(text(W2 / 2, BOARD_Y + BOARD_H / 2 + 5, "PCB (плата)",
                      size=11, color="#455a64"))

    packages = [
        ("DIP", "#d5f5e3", STROKE_EASY),
        ("QFP", "#fef9c3", STROKE_MEDIUM),
        ("QFN", "#fde8d8", STROKE_HARD),
        ("BGA", "#fde0e0", STROKE_NOPE),
    ]

    for i, (name, fill, stroke) in enumerate(packages):
        cx = x0 + i * (block_w + gap) + block_w / 2

        if name == "DIP":
            # Корпус над платою
            pkg_y, pkg_h = 90, 90
            parts.append(rect(cx - 50, pkg_y, 100, pkg_h, fill=fill, stroke=stroke, sw=2, rx=8))
            parts.append(text(cx, pkg_y + 28, "DIP", size=13, bold=True, color=INK))
            parts.append(mtext(cx, pkg_y + 52, ["кристал", "(зверху)"], size=10, color=MUTED, lh=1.3))
            # Ніжки — довгі, проходять крізь плату
            for nx in [cx - 28, cx - 14, cx, cx + 14, cx + 28]:
                # Ніжка від корпусу до верху плати
                parts.append(line(nx, pkg_y + pkg_h, nx, BOARD_Y, color=stroke, sw=2.5))
                # Ніжка під платою (паяний кінець)
                parts.append(line(nx, BOARD_Y + BOARD_H, nx, BOARD_Y + BOARD_H + 10,
                                  color="#f39c12", sw=2.5))
            # Підпис контакт
            tb, _, _ = textbox(cx, BOARD_Y + BOARD_H + 26, "крізь отвір\n(THT)", size=10, pad=5,
                                fill="#fffde7", stroke="#f39c12", sw=1.2, color="#7d6608")
            parts.append(tb)

        elif name == "QFP":
            # Корпус над платою, ніжки-крильця вбік
            pkg_y, pkg_h, pkg_w = 100, 80, 90
            parts.append(rect(cx - pkg_w/2, pkg_y, pkg_w, pkg_h, fill=fill, stroke=stroke, sw=2, rx=8))
            parts.append(text(cx, pkg_y + 28, "QFP", size=13, bold=True, color=INK))
            parts.append(text(cx, pkg_y + 50, "gull-wing", size=10, color=MUTED))
            # Крильця-ніжки з обох боків, покладені на плату
            wing_y = pkg_y + pkg_h  # нижній край корпусу
            LAND_Y = BOARD_Y        # поверхня плати
            for side in [-1, 1]:
                bx = cx + side * (pkg_w/2)
                # Вертикальна частина ніжки
                parts.append(line(bx, wing_y, bx, LAND_Y - 8, color=stroke, sw=2.2))
                # Горизонтальна частина «крильця» на платі
                parts.append(line(bx, LAND_Y - 8, bx + side * 20, LAND_Y,
                                  color=stroke, sw=2.2))
            tb, _, _ = textbox(cx, BOARD_Y + BOARD_H + 22, "площадка збоку\n(видно!)", size=10, pad=5,
                                fill="#fffde7", stroke=STROKE_MEDIUM, sw=1.2, color="#7d6608")
            parts.append(tb)

        elif name == "QFN":
            pkg_y, pkg_h, pkg_w = 110, 70, 100
            parts.append(rect(cx - pkg_w/2, pkg_y, pkg_w, pkg_h, fill=fill, stroke=stroke, sw=2, rx=8))
            parts.append(text(cx, pkg_y + 28, "QFN", size=13, bold=True, color=INK))
            parts.append(text(cx, pkg_y + 50, "no-leads", size=10, color=MUTED))
            # Площадки під краєм дна корпусу — коротенькі, на рівні плати
            pad_y = pkg_y + pkg_h
            for side in [-1, 1]:
                px = cx + side * 34
                # Коротка площадка-контакт під краєм
                parts.append(line(px, pad_y, px, BOARD_Y, color=stroke, sw=3))
            # Теплова площадка під центром
            parts.append(rect(cx - 20, pad_y, 40, 8, fill="#f39c12", stroke="#c0392b", sw=1.5, rx=2))
            parts.append(text(cx, pad_y + 6, "thermal pad", size=8, color="#7b241c"))
            tb, _, _ = textbox(cx, BOARD_Y + BOARD_H + 22, "під краєм дна\n(фен!)", size=10, pad=5,
                                fill="#fde8d8", stroke=STROKE_HARD, sw=1.2, color=STROKE_HARD)
            parts.append(tb)

        elif name == "BGA":
            pkg_y, pkg_h, pkg_w = 110, 70, 110
            parts.append(rect(cx - pkg_w/2, pkg_y, pkg_w, pkg_h, fill=fill, stroke=stroke, sw=2, rx=8))
            parts.append(text(cx, pkg_y + 28, "BGA", size=13, bold=True, color=INK))
            parts.append(text(cx, pkg_y + 50, "ball grid", size=10, color=MUTED))
            # Кульки — матриця 3×2 під пузом
            ball_y = pkg_y + pkg_h
            for bi, bxi in enumerate([-30, 0, 30]):
                bcx = cx + bxi
                # Кулька (коло)
                parts.append(circle(bcx, ball_y + 7, 6, fill="#b0bec5", stroke=stroke, sw=1.5))
            # Лінія — показує, що під платою нічого не видно
            tb, _, _ = textbox(cx, BOARD_Y + BOARD_H + 22, "під усім дном\n(рентген!)", size=10, pad=5,
                                fill="#fde0e0", stroke=STROKE_NOPE, sw=1.2, color=STROKE_NOPE)
            parts.append(tb)

        # Підпис назви корпусу знизу
        parts.append(text(cx, H2 - 12, name, size=13, bold=True, color=stroke))

    render(os.path.join(IMG, "fig-r11-8c-2-package-cross.svg"), W2, H2,
           *parts, title=None)
    print("fig-r11-8c-2-package-cross.svg — OK")

fig2()
