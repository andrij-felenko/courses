# -*- coding: utf-8 -*-
"""Фігури до теми «Дробово-лінійні перетворення Мьобіуса».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def fig_elementary():
    W, H = 820, 360
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0)]
    frags.append(text(W / 2, 28, "Елементарне розкладання перетворення Мьобіуса", size=16, bold=True))

    steps = [
        ("1. Зсув аргументу", "z ↦ z + d/c", "Паралельне перенесення", 80),
        ("2. Інверсія", "z₁ ↦ 1/z₁", "Дзеркальне відбиття та інверсія", 270),
        ("3. Масштаб і поворот", "z₂ ↦ α·z₂", "Множення на α = (bc-ad)/c²", 460),
        ("4. Підсумковий зсув", "w ↦ z₃ + a/c", "Перенесення в точку a/c", 650)
    ]

    for title_str, formula_str, desc_str, cx in steps:
        box_w, box_h = 160, 110
        cy = 120
        frags.append(rect(cx - box_w/2, cy - box_h/2, box_w, box_h, fill=FILL, stroke=LINE, sw=1.5, rx=8))
        frags.append(text(cx, cy - 30, title_str, size=13, bold=True, color=INK))
        frags.append(text(cx, cy - 2, formula_str, size=14, bold=True, color=NEG))
        frags.append(text(cx, cy + 28, desc_str, size=11, color=MUTED))

    # Стрілки між кроками
    for cx in [160, 350, 540]:
        frags.append(arrow(cx, 120, cx + 30, 120, color=LINE, sw=2.0))

    # Нижній геометричний блок — що відбувається з колом
    frags.append(rect(40, 210, 740, 120, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=8))
    frags.append(text(W/2, 232, "Геометричний результат послідовних дій на комплексну площину", size=13, bold=True, color=INK))

    # Міні-діаграми внизу
    # 1. Початкова сітка / коло
    frags.append(circle(120, 280, 22, fill="none", stroke=NEG, sw=1.5))
    frags.append(line(120, 250, 120, 310, color=MUTED, sw=1.0, dash="2,2"))
    frags.append(line(90, 280, 150, 280, color=MUTED, sw=1.0, dash="2,2"))
    frags.append(text(120, 320, "Прямі / Кола", size=11, color=INK))

    frags.append(arrow(170, 280, 210, 280, color=MUTED, sw=1.5))

    # 2. Інверсія кола в інше коло / пряму
    frags.append(circle(270, 280, 22, fill="none", stroke=POS, sw=1.5))
    frags.append(line(235, 305, 305, 255, color=POS, sw=1.2, dash="3,3"))
    frags.append(text(270, 320, "Збереження кіл", size=11, color=INK))

    frags.append(arrow(330, 280, 370, 280, color=MUTED, sw=1.5))

    # 3. Деформація кутів — кути зберігаються
    frags.append(line(420, 260, 460, 300, color=FIELD, sw=1.8))
    frags.append(line(420, 300, 460, 260, color=NEG, sw=1.8))
    frags.append(circle(440, 280, 12, fill="none", stroke=MUTED, sw=1.0))
    frags.append(text(440, 320, "Конформність (90°)", size=11, color=INK))

    frags.append(arrow(490, 280, 530, 280, color=MUTED, sw=1.5))

    # 4. Готовий результат
    frags.append(circle(640, 280, 26, fill="none", stroke=POS, sw=2.0))
    frags.append(circle(640, 280, 3, fill=POS, stroke=POS, sw=1.0))
    frags.append(text(640, 320, "Образ w = f(z)", size=11, bold=True, color=INK))

    render(os.path.join(IMG, 'mobius-elementary.svg'), W, H, *frags)


def fig_stereographic():
    W, H = 780, 440
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0)]
    frags.append(text(W / 2, 26, "Стереографічна проекція сфери Рімана на комплексну площину", size=16, bold=True))

    cx, cy = 340, 220
    R = 120

    # Комплексна площина ℂ (перспектива / паралелограм)
    p_x1, p_y1 = 80, 270
    p_x2, p_y2 = 620, 270
    p_x3, p_y3 = 520, 390
    p_x4, p_y4 = 20, 390
    plane_path = f'<polygon points="{p_x1},{p_y1} {p_x2},{p_y2} {p_x3},{p_y3} {p_x4},{p_y4}" fill="#f0f4f8" stroke="#94a3b8" stroke-width="1.5"/>'
    frags.append(plane_path)
    frags.append(text(410, 375, "Комплексна площина ℂ (z = x + iy)", size=12, bold=True, color=MUTED))

    # Сфера (коло з екватором)
    frags.append(circle(cx, cy, R, fill="#ffffff", stroke=LINE, sw=2.0))
    # Екватор (еліпс)
    frags.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="35" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    # Північний та Південний полюси
    N_pt = (cx, cy - R)
    S_pt = (cx, cy + R)
    frags.append(circle(N_pt[0], N_pt[1], 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(N_pt[0], N_pt[1] - 12, "Північний полюс N (∞)", size=13, bold=True, color=POS))

    frags.append(circle(S_pt[0], S_pt[1], 4, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(S_pt[0], S_pt[1] + 20, "Південний полюс S (0)", size=12, color=NEG))

    # Точка P на сфері
    px, py = cx + 80, cy - 60
    frags.append(circle(px, py, 4.5, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(px + 14, py - 4, "Точка P(x, y, Z) на сфері", size=12, bold=True, color=FIELD))

    # Проекційний промінь від N через P до площини z
    t_proj = (cy - N_pt[1]) / (py - N_pt[1])
    zx = N_pt[0] + t_proj * (px - N_pt[0])
    zy = N_pt[1] + t_proj * (py - N_pt[1]) + 60

    frags.append(line(N_pt[0], N_pt[1], zx, zy, color=POS, sw=1.8, dash="5,3"))
    frags.append(circle(zx, zy, 5, fill=POS, stroke=POS, sw=1))
    frags.append(text(zx + 15, zy + 15, "Проекція z ∈ ℂ", size=13, bold=True, color=POS))

    # Пояснювальний блок праворуч
    info_x, info_y = 650, 140
    frags.append(rect(info_x - 70, info_y, 180, 160, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(info_x, info_y + 24, "Властивості:", size=13, bold=True, color=INK))
    frags.append(text(info_x, info_y + 55, "• N ↦ Нескінченність ∞", size=11, color=INK))
    frags.append(text(info_x, info_y + 80, "• S ↦ Початок координат 0", size=11, color=INK))
    frags.append(text(info_x, info_y + 105, "• Кола на сфері ↦", size=11, color=INK))
    frags.append(text(info_x, info_y + 125, "  Кола/Прямі на ℂ", size=11, bold=True, color=NEG))
    frags.append(text(info_x, info_y + 148, "• Поворот сфери ≡ Мьобіус", size=11, color=FIELD))

    render(os.path.join(IMG, 'stereographic-projection.svg'), W, H, *frags)


def fig_aberration():
    W, H = 800, 420
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0)]
    frags.append(text(W / 2, 26, "Релятивістська аберація світла та дія групи Лоренца PSL(2,ℂ)", size=16, bold=True))

    # Ліва панель: Спокій (v = 0)
    lx, ly = 200, 210
    R = 110
    frags.append(circle(lx, ly, R, fill="#0f172a", stroke=MUTED, sw=2.0))
    frags.append(text(lx, ly - R - 15, "Нерухомий спостерігач (v = 0)", size=13, bold=True, color=INK))

    for a in range(0, 360, 30):
        rad = math.radians(a)
        sx = lx + (R - 15) * math.cos(rad)
        sy = ly + (R - 15) * math.sin(rad)
        frags.append(circle(sx, sy, 2.5, fill="#ffffff", stroke="#ffffff", sw=1))
    for a in range(0, 360, 45):
        rad = math.radians(a)
        sx = lx + 55 * math.cos(rad)
        sy = ly + 55 * math.sin(rad)
        frags.append(circle(sx, sy, 2.0, fill="#60a5fa", stroke="#60a5fa", sw=1))
    frags.append(f'<circle cx="{lx}" cy="{ly}" r="55" fill="none" stroke="#60a5fa" stroke-width="1.2" stroke-dasharray="3,3"/>')

    frags.append(circle(lx, ly, 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(lx, ly + 25, "Око", size=11, color="#ffffff"))

    # Центральна стрілка бусту
    frags.append(arrow(340, ly, 440, ly, color=POS, sw=2.5))
    frags.append(text(390, ly - 15, "Буст Лоренца", size=13, bold=True, color=POS))
    frags.append(text(390, ly + 18, "v = 0.8c", size=12, bold=True, color=NEG))

    # Права панель: Рух зі швидкістю v = 0.8c
    rx, ry = 600, 210
    frags.append(circle(rx, ry, R, fill="#0f172a", stroke=MUTED, sw=2.0))
    frags.append(text(rx, ry - R - 15, "Релятивістський рух (v = 0.8c)", size=13, bold=True, color=INK))

    beta = 0.8
    for a in range(0, 360, 30):
        rad = math.radians(a)
        cos_th = math.cos(rad)
        sin_th = math.sin(rad)
        cos_th_p = (cos_th + beta) / (1.0 + beta * cos_th)
        sin_th_p = math.sqrt(max(0.0, 1.0 - cos_th_p**2)) * (1.0 if sin_th >= 0 else -1.0)
        sx = rx + (R - 15) * cos_th_p
        sy = ry + (R - 15) * sin_th_p
        frags.append(circle(sx, sy, 2.5, fill="#ffffff", stroke="#ffffff", sw=1))

    c_shift = beta * 35
    frags.append(f'<circle cx="{rx + c_shift}" cy="{ry}" r="45" fill="none" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="3,3"/>')
    for a in range(0, 360, 45):
        rad = math.radians(a)
        cos_th = math.cos(rad)
        sin_th = math.sin(rad)
        cos_th_p = (cos_th + beta) / (1.0 + beta * cos_th)
        sin_th_p = math.sqrt(max(0.0, 1.0 - cos_th_p**2)) * (1.0 if sin_th >= 0 else -1.0)
        sx = rx + c_shift + 45 * cos_th_p
        sy = ry + 45 * sin_th_p
        frags.append(circle(sx, sy, 2.0, fill="#60a5fa", stroke="#60a5fa", sw=1))

    frags.append(circle(rx, ry, 4, fill=POS, stroke=POS, sw=1))

    # Нижній висновок
    frags.append(rect(100, 350, 600, 50, fill=FILL, stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(400, 380, "Головний інваріант: сузір'я стискаються вперед, але КРУГЛІ форми лишаються КРУГЛИМИ!", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'relativistic-aberration.svg'), W, H, *frags)


def fig_grid_transform():
    W, H = 800, 420
    frags = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0)]
    frags.append(text(W / 2, 26, "Конформне перетворення сітки: прямі лінії ↦ ортогональні кола", size=16, bold=True))

    # Ліва панель: Декартова сітка у площині z
    lx, ly = 200, 210
    box_s = 140
    frags.append(rect(lx - box_s, ly - box_s, 2*box_s, 2*box_s, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(lx, ly - box_s - 12, "Площина z (Декартова сітка)", size=13, bold=True, color=INK))

    frags.append(line(lx - box_s, ly, lx + box_s, ly, color=MUTED, sw=1.0))
    frags.append(line(lx, ly - box_s, lx, ly + box_s, color=MUTED, sw=1.0))

    for offset in [-90, -60, -30, 30, 60, 90]:
        frags.append(line(lx + offset, ly - box_s, lx + offset, ly + box_s, color=NEG, sw=1.2, dash="4,4"))
        frags.append(line(lx - box_s, ly + offset, lx + box_s, ly + offset, color=POS, sw=1.2, dash="4,4"))

    frags.append(circle(lx + 30, ly - 30, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(lx + 45, ly - 40, "90°", size=11, bold=True, color=FIELD))

    # Центральна стрілка відображення
    frags.append(arrow(360, ly, 440, ly, color=LINE, sw=2.0))
    frags.append(text(400, ly - 16, "f(z) = (z-1)/(z+1)", size=13, bold=True, color=NEG))

    # Права панель: Площина w (Кола Аполлонія)
    rx, ry = 600, 210
    frags.append(rect(rx - box_s, ry - box_s, 2*box_s, 2*box_s, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(rx, ry - box_s - 12, "Площина w (Ортогональні кола)", size=13, bold=True, color=INK))

    frags.append(line(rx - box_s, ry, rx + box_s, ry, color=MUTED, sw=1.0))
    frags.append(line(rx, ry - box_s, rx, ry + box_s, color=MUTED, sw=1.0))

    for r_c in [25, 50, 85, 120]:
        frags.append(f'<circle cx="{rx + r_c/2}" cy="{ry}" r="{r_c}" fill="none" stroke="{NEG}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    for r_c in [30, 65, 110]:
        frags.append(f'<circle cx="{rx}" cy="{ry + r_c/2}" r="{r_c}" fill="none" stroke="{POS}" stroke-width="1.2" stroke-dasharray="4,4"/>')
        frags.append(f'<circle cx="{rx}" cy="{ry - r_c/2}" r="{r_c}" fill="none" stroke="{POS}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    frags.append(circle(rx + 35, ry - 35, 3.5, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(rx + 50, ry - 45, "90° збережено!", size=11, bold=True, color=FIELD))

    frags.append(text(W / 2, 390, "Конформність: перетворення зберігає кути між кривими в кожній точці", size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'circle-grid-transform.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_elementary()
    fig_stereographic()
    fig_aberration()
    fig_grid_transform()
    print("Усі фігури успішно згенеровано в ./img/")
