# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: Геометрія закону Ламберта (індикатриса I(θ) та проєкція площі)
# ═══════════════════════════════════════════════════════════════════════════
def fig_lambert_geometry():
    W, H = 720, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, 'Геометрія закону Ламберта: індикатриса сили світла та проєкція площі', 15, INK, 'middle', bold=True))

    # --- Ліва частина: Індикатриса I(θ) = I₀ · cos θ ---
    ox1, oy1 = 180, 360
    f.append(text(ox1, 60, 'А. Індикатриса сили світла I(θ)', 13, INK, 'middle', bold=True))
    
    # Поверхня dA
    f.append(rect(ox1 - 90, oy1, 180, 16, fill='#eaf2fb', stroke=NEG, sw=1.5, rx=2))
    f.append(text(ox1, oy1 + 12, 'елемент поверхні dA', 11, NEG, 'middle', bold=True))

    # Нормаль n
    f.append(line(ox1, oy1, ox1, oy1 - 250, color=INK, sw=2, dash='6,4'))
    f.append(text(ox1 + 10, oy1 - 240, 'нормаль n̂ (θ = 0°)', 11, INK, 'start', bold=True))

    # Коло індикатриси (діаметр I₀ = 200px, радіус 100px, центр в (ox1, oy1 - 100))
    f.append('<circle cx="%d" cy="%d" r="100" fill="#2457d6" fill-opacity="0.08" stroke="#2457d6" stroke-width="2" stroke-dasharray="4,3"/>' % (ox1, oy1 - 100))
    f.append(text(ox1 - 108, oy1 - 150, 'I(θ) = I₀ · cos θ', 12, '#2457d6', 'end', bold=True))

    # Вектор I₀ вздовж нормалі
    f.append(arrow(ox1, oy1, ox1, oy1 - 200, color=POS, sw=2.5))
    f.append(text(ox1 + 12, oy1 - 195, 'I₀ (максимум)', 11, POS, 'start', bold=True))

    # Вектор I(θ) під кутом 45°
    ang = math.radians(45)
    r_len = 200 * math.cos(ang)
    vx = ox1 + r_len * math.sin(ang)
    vy = oy1 - r_len * math.cos(ang)
    f.append(arrow(ox1, oy1, vx, vy, color=FIELD, sw=2.2))
    f.append(text(vx + 10, vy + 4, 'I(θ) = I₀ cos 45°', 11, FIELD, 'start', bold=True))

    # Дуга кута θ
    f.append('<path d="M %d %d A 60 60 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
             (ox1, oy1 - 60, ox1 + 60 * math.sin(ang), oy1 - 60 * math.cos(ang), FIELD))
    f.append(text(ox1 + 22, oy1 - 70, 'θ', 12, FIELD, 'middle', bold=True))

    # Розділювальна лінія
    f.append(line(360, 50, 360, 400, color=LINE, sw=1, dash='4,4'))

    # --- Права частина: Скорочення проєкованої площі dA_proj ---
    ox2, oy2 = 540, 360
    f.append(text(ox2, 60, 'Б. Проєкція площі під кутом θ', 13, INK, 'middle', bold=True))

    # Похила або горизонтальна площа
    f.append(rect(ox2 - 100, oy2, 200, 16, fill='#eaf2fb', stroke=NEG, sw=1.5, rx=2))
    f.append(text(ox2, oy2 + 12, 'реальна площа dA', 11, NEG, 'middle', bold=True))

    # Нормаль n
    f.append(line(ox2, oy2, ox2, oy2 - 250, color=INK, sw=1.8, dash='6,4'))

    # Напрям спостереження під 50°
    ang2 = math.radians(50)
    len_beam = 220
    bx = ox2 + len_beam * math.sin(ang2)
    by = oy2 - len_beam * math.cos(ang2)

    # Пучок променів від dA
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#2457d6" fill-opacity="0.1" stroke="#2457d6" stroke-width="1.5" stroke-dasharray="4,3"/>' %
             (ox2 - 90, oy2, ox2 + 90, oy2, ox2 + 90 + 140 * math.sin(ang2), oy2 - 140 * math.cos(ang2), ox2 - 90 + 140 * math.sin(ang2), oy2 - 140 * math.cos(ang2)))

    f.append(arrow(ox2, oy2, bx, by, color=POS, sw=2.5))
    f.append(text(bx + 8, by - 6, 'напрям на спостерігача', 11, POS, 'start', bold=True))

    # Лінія проєкованої площі
    f.append(line(ox2 - 60 * math.cos(ang2) + 90 * math.sin(ang2), oy2 - 60 * math.sin(ang2) - 90 * math.cos(ang2),
                  ox2 + 60 * math.cos(ang2) + 90 * math.sin(ang2), oy2 + 60 * math.sin(ang2) - 90 * math.cos(ang2),
                  color=FIELD, sw=3))
    f.append(text(ox2 + 40, oy2 - 165, 'dA_proj = dA · cos θ', 11, FIELD, 'end', bold=True))

    # Висновок унизу
    f.append(text(W / 2, H - 15, 'Яскравість L = I(θ) / dA_proj = (I₀ cos θ) / (dA cos θ) = I₀ / dA = const', 12, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'lambert-geometry.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Типи відбиття (дзеркальне, ламбертове, реальне мікрофасетне)
# ═══════════════════════════════════════════════════════════════════════════
def fig_diffuse_vs_specular():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, 'Порівняння типів відбиття світла поверхнею', 15, INK, 'middle', bold=True))

    # 1. Дзеркальне (Specular)
    c1_x, c1_y = 120, 270
    f.append(text(c1_x, 55, 'А. Дзеркальне відбиття', 12, INK, 'middle', bold=True))
    f.append(line(c1_x - 90, c1_y, c1_x + 90, c1_y, color=INK, sw=2))
    # Штриховка дзеркала
    for idx in range(-8, 9):
        f.append(line(c1_x + idx * 10, c1_y, c1_x + idx * 10 - 6, c1_y + 8, color=MUTED, sw=1))

    # Падаючий і відбитий промінь
    f.append(arrow(c1_x - 65, c1_y - 130, c1_x, c1_y, color=POS, sw=2.2))
    f.append(arrow(c1_x, c1_y, c1_x + 65, c1_y - 130, color=POS, sw=2.2))
    f.append(line(c1_x, c1_y, c1_x, c1_y - 140, color=MUTED, sw=1, dash='3,3'))
    f.append(text(c1_x, c1_y + 24, 'ідеально гладка поверхня', 10, MUTED, 'middle'))
    f.append(text(c1_x, c1_y - 145, 'θ_r = θ_i', 11, POS, 'middle', bold=True))

    # Роздільник 1
    f.append(line(240, 45, 240, 320, color=LINE, sw=1, dash='4,4'))

    # 2. Ідеальне Ламбертове (Diffuse)
    c2_x, c2_y = 360, 270
    f.append(text(c2_x, 55, 'Б. Ламбертове розсіювання', 12, INK, 'middle', bold=True))
    f.append(line(c2_x - 90, c2_y, c2_x + 90, c2_y, color=INK, sw=2))
    f.append(rect(c2_x - 90, c2_y, 180, 10, fill='#eaf2fb', stroke='none'))

    # Падаючий промінь
    f.append(arrow(c2_x - 65, c2_y - 130, c2_x, c2_y, color=POS, sw=2.2))

    # Ламбертова півсфера/купол відбиття
    f.append('<circle cx="%d" cy="%d" r="60" fill="#2457d6" fill-opacity="0.12" stroke="#2457d6" stroke-width="1.8" stroke-dasharray="4,3"/>' % (c2_x, c2_y - 60))
    for angle in [-60, -35, 0, 35, 60]:
        rad = math.radians(angle)
        length = 120 * math.cos(rad)
        vx = c2_x + length * math.sin(rad)
        vy = c2_y - length * math.cos(rad)
        f.append(arrow(c2_x, c2_y, vx, vy, color=FIELD, sw=1.5))

    f.append(text(c2_x, c2_y + 24, 'об\'ємне/мікрооб\'ємне розсіювання', 10, MUTED, 'middle'))
    f.append(text(c2_x + 68, c2_y - 85, 'I(θ) ∝ cos θ', 11, FIELD, 'start', bold=True))

    # Роздільник 2
    f.append(line(480, 45, 480, 320, color=LINE, sw=1, dash='4,4'))

    # 3. Реальне мікрофасетне (Real Microfacet)
    c3_x, c3_y = 600, 270
    f.append(text(c3_x, 55, 'В. Реальна шорстка поверхня', 12, INK, 'middle', bold=True))
    
    # Зигзагоподібна поверхня (мікрофасети)
    zigzag = ["M %d %d" % (c3_x - 90, c3_y)]
    for i in range(-8, 9):
        zx = c3_x + i * 10
        zy = c3_y + (-3 if i % 2 == 0 else 3)
        zigzag.append("L %d %d" % (zx, zy))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(zigzag), INK))

    # Падаючий промінь
    f.append(arrow(c3_x - 65, c3_y - 130, c3_x, c3_y, color=POS, sw=2.2))

    # Комбінована пелюстка (дифузна основа + дзеркальний пік)
    lobe_path = [
        "M %d %d" % (c3_x - 70, c3_y),
        "C %d %d, %d %d, %d %d" % (c3_x - 60, c3_y - 50, c3_x - 10, c3_y - 70, c3_x, c3_y - 75),
        "C %d %d, %d %d, %d %d" % (c3_x + 20, c3_y - 85, c3_x + 50, c3_y - 140, c3_x + 70, c3_y - 130),
        "C %d %d, %d %d, %d %d" % (c3_x + 75, c3_y - 80, c3_x + 65, c3_y - 30, c3_x + 70, c3_y)
    ]
    f.append('<path d="%s" fill="#c0392b" fill-opacity="0.15" stroke="#c0392b" stroke-width="1.8"/>' % " ".join(lobe_path))
    f.append(text(c3_x + 52, c3_y - 140, 'дзеркальний пік', 10, NEG, 'start', bold=True))
    f.append(text(c3_x - 65, c3_y - 35, 'дифузна фон-сойка', 10, FIELD, 'end', italic=True))

    f.append(text(c3_x, c3_y + 24, 'суміш дифузії та бліку', 10, MUTED, 'middle'))

    f.append(text(W / 2, H - 15, 'Ідеально дифузна поверхня рівномірно якрава з усіх кутів; реальні тіла мають блик', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'diffuse-vs-specular.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Вплив кута нахилу поверхні на освітленість (Сонячна панель)
# ═══════════════════════════════════════════════════════════════════════════
def fig_solar_tilt_effect():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Вплив кута нахилу поверхні на освітленість (закон косинуса для приймача)', 15, INK, 'middle', bold=True))

    # --- Ліворуч: Пряме падіння світла (θ = 0°) ---
    c1_x, c1_y = 180, 260
    f.append(text(c1_x, 58, 'А. Перпендикулярне падіння (θ = 0°)', 12, INK, 'middle', bold=True))

    # Панель перпендикулярна (горизонтальна)
    f.append(rect(c1_x - 90, c1_y, 180, 14, fill='#2457d6', stroke=INK, sw=1.8, rx=2))
    f.append(text(c1_x, c1_y + 30, 'площа панелі A', 11, INK, 'middle', bold=True))

    # Нормаль
    f.append(line(c1_x, c1_y, c1_x, c1_y - 170, color=INK, sw=1.5, dash='4,4'))
    f.append(text(c1_x + 8, c1_y - 160, 'n̂', 11, INK, 'start', bold=True))

    # 5 променів світла прямовисно вниз
    for i in range(-2, 3):
        rx = c1_x + i * 36
        f.append(arrow(rx, c1_y - 160, rx, c1_y - 5, color=POS, sw=2))

    f.append(text(c1_x, c1_y - 175, 'потік Φ₀ (5 променів на ширину A)', 10, POS, 'middle', bold=True))
    f.append(text(c1_x, c1_y + 48, 'Освітленість E = E₀ · cos 0° = E₀ (100%)', 11, POS, 'middle', bold=True))

    # Розділювач
    f.append(line(360, 50, 360, 330, color=LINE, sw=1, dash='4,4'))

    # --- Праворуч: Нахилена поверхня (θ = 60°) ---
    c2_x, c2_y = 540, 260
    f.append(text(c2_x, 58, 'Б. Падіння під кутом (θ = 60°)', 12, INK, 'middle', bold=True))

    # Панель нахилена під 60°
    ang = math.radians(60)
    pw = 180

    # Накреслити нахилену пластину
    p_x1 = c2_x - (pw / 2) * math.cos(ang)
    p_y1 = c2_y + (pw / 2) * math.sin(ang)
    p_x2 = c2_x + (pw / 2) * math.cos(ang)
    p_y2 = c2_y - (pw / 2) * math.sin(ang)
    f.append(line(p_x1, p_y1, p_x2, p_y2, color=INK, sw=6))
    f.append(text(c2_x + 35, c2_y + 30, 'та сама площа A', 11, INK, 'middle', bold=True))

    # Нормаль до нахиленої панелі
    nx = c2_x - 140 * math.sin(ang)
    ny = c2_y - 140 * math.cos(ang)
    f.append(line(c2_x, c2_y, nx, ny, color=INK, sw=1.5, dash='4,4'))
    f.append(text(nx - 10, ny - 6, 'n̂', 11, INK, 'end', bold=True))

    # Промені світла прямовисно вниз з такою самою густиною
    for i in range(-2, 3):
        rx = c2_x + i * 36
        ry = c2_y - math.tan(ang) * (rx - c2_x)
        if ry <= c2_y + 80 and ry >= c2_y - 80:
            f.append(arrow(rx, c2_y - 160, rx, ry - 4, color=POS, sw=2))
        else:
            f.append(line(rx, c2_y - 160, rx, c2_y + 40, color=MUTED, sw=1.2, dash='3,3'))

    # Дуга кута між світлом (вертикаль) і нормаллю
    f.append('<path d="M %d %d A 50 50 0 0 0 %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
             (c2_x, c2_y - 50, c2_x - 50 * math.sin(ang), c2_y - 50 * math.cos(ang), FIELD))
    f.append(text(c2_x - 18, c2_y - 58, 'θ = 60°', 11, FIELD, 'end', bold=True))

    f.append(text(c2_x, c2_y - 175, 'потік розтягується: вловлюється 2.5 променя', 10, NEG, 'middle', bold=True))
    f.append(text(c2_x, c2_y + 48, 'Освітленість E = E₀ · cos 60° = 0.5 · E₀ (50%)', 11, NEG, 'middle', bold=True))

    f.append(text(W / 2, H - 15, 'Для максимального збору енергії трекери повертають панелі перпендикулярно до сонця (θ = 0°)', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'solar-tilt-effect.svg'), W, H, *f)


fig_lambert_geometry()
fig_diffuse_vs_specular()
fig_solar_tilt_effect()
print('All Lambert figures regenerated.')
