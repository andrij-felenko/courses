# -*- coding: utf-8 -*-
"""Фігури до теми «Ізоляція провідників».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_coaxial_field():
    """Фігура 1: Геометрія коаксіального кабелю та графік розподілу поля E(r)."""
    W, H = 760, 380
    f = []

    # Заголовок
    f.append(text(W / 2, 26, "Розподіл електричного поля у коаксіальній ізоляції", size=16, bold=True))

    # Рамка для поперечного перерізу кабелю (ліва частина)
    f.append(rect(20, 50, 350, 310, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(195, 75, "Поперечний переріз кабелю", size=13, bold=True, color="#1e40af"))

    # Зовнішня оболонка / екран (r2 = 110)
    cx, cy = 195, 215
    r2 = 100
    r1 = 38
    f.append(circle(cx, cy, r2, fill="#eef4ff", stroke="#2563eb", sw=2))

    # Ізоляція між r1 та r2 (заповнення)
    f.append(circle(cx, cy, r1, fill="#dbeafe", stroke="#1d4ed8", sw=2))

    # Внутрішня жила (провідник, під напругою U)
    f.append(circle(cx, cy, r1, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx, cy + 4, "Жила (+U)", size=12, bold=True, color=POS))

    # Стрілки електричного поля E(r) (радіальні)
    import math
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        x_start = cx + (r1 + 4) * math.cos(rad)
        y_start = cy + (r1 + 4) * math.sin(rad)
        x_end = cx + (r2 - 6) * math.cos(rad)
        y_end = cy + (r2 - 6) * math.sin(rad)
        f.append(arrow(x_start, y_start, x_end, y_end, color=FIELD, sw=1.5))

    # Позначення радіусів r1 та r2
    f.append(line(cx, cy, cx + r1, cy, color=POS, sw=1.5, dash="3,3"))
    f.append(text(cx + r1 / 2, cy - 8, "r₁", size=12, bold=True, color=POS))

    f.append(line(cx, cy, cx, cy - r2, color="#2563eb", sw=1.5, dash="3,3"))
    f.append(text(cx + 8, cy - r2 / 2, "r₂", size=12, bold=True, color="#2563eb"))

    # Рамка для графіка E(r) (права частина)
    f.append(rect(390, 50, 350, 310, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(565, 75, "Залежність напруженості E(r)", size=13, bold=True, color="#1e40af"))

    # Осі графіка
    ox, oy = 430, 310
    f.append(arrow(ox, oy, ox, 100, color=INK, sw=1.5)) # Вісь E
    f.append(text(ox - 15, 105, "E", size=13, bold=True))

    f.append(arrow(ox, oy, 720, oy, color=INK, sw=1.5)) # Вісь r
    f.append(text(715, oy + 20, "r", size=13, bold=True))

    # Пунктирні лінії радіусів на осі r
    xr1 = ox + 60
    xr2 = ox + 220
    f.append(line(xr1, oy, xr1, 120, color=MUTED, sw=1, dash="3,3"))
    f.append(text(xr1, oy + 18, "r₁", size=12, bold=True, color=POS))

    f.append(line(xr2, oy, xr2, 120, color=MUTED, sw=1, dash="3,3"))
    f.append(text(xr2, oy + 18, "r₂", size=12, bold=True, color="#2563eb"))

    # Максимальне та мінімальне поле E
    ye_max = 130
    ye_min = 260
    f.append(line(ox, ye_max, xr1, ye_max, color=POS, sw=1, dash="3,3"))
    f.append(text(ox - 25, ye_max + 4, "E_max", size=11, bold=True, color=POS))

    f.append(line(ox, ye_min, xr2, ye_min, color="#2563eb", sw=1, dash="3,3"))
    f.append(text(ox - 25, ye_min + 4, "E_min", size=11, bold=True, color="#2563eb"))

    # Крива E(r) ~ 1/r від xr1 до xr2
    curve_points = []
    for px in range(int(xr1), int(xr2) + 1, 4):
        # r змінюється від 1 до r2/r1
        t = (px - xr1) / (xr2 - xr1)
        r_val = 1.0 + t * 1.718 # r2/r1 ~ 2.718
        # E(r) ~ 1/r
        e_val = 1.0 / r_val
        py = ye_min + (1.0 - e_val) / (1.0 - 1.0 / 2.718) * (ye_max - ye_min)
        curve_points.append((px, py))

    path_str = "M %.1f %.1f " % curve_points[0]
    for px, py in curve_points[1:]:
        path_str += "L %.1f %.1f " % (px, py)

    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_str, POS))

    # Формула на графіку
    f.append(textbox(575, 140, "E(r) = U / (r · ln(r₂ / r₁))", size=12, pad=6, fill="#fffbe6", stroke="#d97706")[0])

    render(os.path.join(IMG, 'coaxial-field-distribution.svg'), W, H, *f)


def fig_breakdown_mechanisms():
    """Фігура 2: Чотири основні механізми руйнування ізоляції."""
    W, H = 780, 360
    f = []

    f.append(text(W / 2, 26, "Основні механізми руйнування електричної ізоляції", size=16, bold=True))

    cards = [
        ("Електричний пробій",
         ["Ударна іонізація", "Лавинне зростання струму", "Час: наносекунди", "Висока напруженість E_br"],
         "#fdecea", POS),
        ("Тепловий пробій",
         ["Діелектричні втрати tan δ", "Самороззігрів діелектрика", "Зростання провідності σ", "Тепловий вибух / розплав"],
         "#fff7ed", "#c2410c"),
        ("Частковий розряд",
         ["Газові мікропори у масі", "Локальне підсилення E-поля", "УФ-випромінювання та озон", "Діелектричні дерева"],
         "#f0fdf4", FIELD),
        ("Поверхневий трекінг",
         ["Волога та забруднення", "Витоки струму по поверхні", "Каустична обуглецьованість", "Перекриття між електродами"],
         "#eef4ff", NEG)
    ]

    card_w = 175
    card_h = 270
    gap = 15
    start_x = 20

    for i, (title_str, items, bg_color, border_color) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        cy = 55
        f.append(rect(cx, cy, card_w, card_h, fill=bg_color, stroke=border_color, sw=1.8, rx=8))
        f.append(text(cx + card_w / 2, cy + 28, title_str, size=13, bold=True, color=border_color))
        f.append(line(cx + 10, cy + 42, cx + card_w - 10, cy + 42, color=border_color, sw=1, dash="2,2"))

        for j, item in enumerate(items):
            iy = cy + 70 + j * 45
            f.append(textbox(cx + card_w / 2, iy, item, size=11, pad=5, fill="#ffffff", stroke=border_color, sw=1, min_w=card_w - 20)[0])

    render(os.path.join(IMG, 'breakdown-mechanisms.svg'), W, H, *f)


def fig_creepage_clearance():
    """Фігура 3: Ізоляційні відстані — повітряний зазор (Clearance) та шлях витоку (Creepage)."""
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 26, "Геометрія ізоляційних відстаней у розрахунку безпеки", size=16, bold=True))

    # Корпус ізолятора з пазом (по центру)
    f.append(rect(20, 50, W - 40, H - 76, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # Тіло діелектрика (сірий пластик)
    path_dielectric = (
        "M 80 270 "
        "L 250 270 "
        "L 250 170 "
        "L 330 170 "
        "L 330 220 "
        "L 430 220 "
        "L 430 170 "
        "L 510 170 "
        "L 510 270 "
        "L 680 270 "
        "L 680 310 "
        "L 80 310 Z"
    )
    f.append('<path d="%s" fill="#e5e7eb" stroke="#4b5563" stroke-width="2"/>' % path_dielectric)
    f.append(text(380, 290, "Основа діелектричного ізолятора (з внутрішнім пазом)", size=12, bold=True, color="#374151"))

    # Контакт 1 (лівий)
    f.append(rect(120, 110, 100, 60, fill="#fdecea", stroke=POS, sw=2, rx=4))
    f.append(text(170, 145, "Контакт 1 (+HV)", size=12, bold=True, color=POS))

    # Контакт 2 (правий)
    f.append(rect(540, 110, 100, 60, fill="#eef4ff", stroke=NEG, sw=2, rx=4))
    f.append(text(590, 145, "Контакт 2 (GND)", size=12, bold=True, color=NEG))

    # 1. Повітряний зазор (Clearance) — найкоротша пряма через повітря між контактами
    f.append(arrow(220, 140, 540, 140, color=POS, sw=2))
    f.append(arrow(540, 140, 220, 140, color=POS, sw=2))
    f.append(textbox(380, 105, "Повітряний зазор (Clearance)\nНайкоротша пряма лінія у повітрі", size=11, pad=6, fill="#ffffff", stroke=POS)[0])

    # 2. Шлях витоку (Creepage distance) — уздовж поверхні діелектрика
    path_creepage = (
        "M 220 170 "
        "L 250 170 "
        "L 250 170 "
        "L 330 170 "
        "L 330 220 "
        "L 430 220 "
        "L 430 170 "
        "L 510 170 "
        "L 540 170"
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,4"/>' % (path_creepage, FIELD))

    f.append(textbox(380, 250, "Шлях витоку (Creepage distance)\nНайкоротший шлях вздовж поверхні діелектрика з урахуванням пазу", size=11, pad=6, fill="#ffffff", stroke=FIELD)[0])

    render(os.path.join(IMG, 'creepage-clearance-geometry.svg'), W, H, *f)


if __name__ == '__main__':
    fig_coaxial_field()
    fig_breakdown_mechanisms()
    fig_creepage_clearance()
    print("Успішно згенеровано 3 фігури у ./img/")
