# -*- coding: utf-8 -*-
"""Фігури до теми «Сила між паралельними провідниками».
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
COLOR_GRAY = "#7f8c8d"

def write_svg(frags, path, w, h):
    render(path, w, h, *frags)

def dcircle(cx, cy, r, stroke='#95a5a6', sw=1.2, dash="4,4"):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{stroke}" stroke-width="{sw:.1f}" stroke-dasharray="{dash}"/>'

def dellipse(cx, cy, rx, ry, fill='none', stroke=COLOR_BLUE, sw=2.0):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── Фігура 1: Притягання паралельних струмів ────────────────────────────────
def fig_parallel_wires_fields():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Взаємодія паралельних провідників з однойменними струмами (Притягання)", size=15, bold=True))

    cx1, cy1 = 200, 180
    cx2, cy2 = 440, 180
    r_wire = 18

    # Магнітні лінії для лівого та правого провідників
    for r_field in [45, 75, 110]:
        f.append(dcircle(cx1, cy1, r_field, stroke='#95a5a6', sw=1.2, dash="4,4"))
        f.append(dcircle(cx2, cy2, r_field, stroke='#95a5a6', sw=1.2, dash="4,4"))

    # Результуючі напнуті магнітні лінії довкола обох дротів
    f.append(dellipse(320, 180, 240, 130, fill='none', stroke=COLOR_BLUE, sw=2.2))
    f.append(dellipse(320, 180, 200, 105, fill='none', stroke=COLOR_BLUE, sw=1.8))

    # Стрілки напряму поля на спільних лініях
    f.append(arrow(320, 50, 340, 50, color=COLOR_BLUE, sw=2))
    f.append(arrow(320, 310, 300, 310, color=COLOR_BLUE, sw=2))

    # Провідник 1
    f.append(circle(cx1, cy1, r_wire, fill='#e8f0fe', stroke=COLOR_BLUE, sw=2.5))
    f.append(text(cx1, cy1 + 5, "⊗ I₁", size=13, bold=True, color=COLOR_BLUE))
    f.append(text(cx1, cy1 - 28, "Провідник 1", size=12, bold=True))

    # Провідник 2
    f.append(circle(cx2, cy2, r_wire, fill='#e8f0fe', stroke=COLOR_BLUE, sw=2.5))
    f.append(text(cx2, cy2 + 5, "⊗ I₂", size=13, bold=True, color=COLOR_BLUE))
    f.append(text(cx2, cy2 - 28, "Провідник 2", size=12, bold=True))

    # Вектори сил F12 та F21
    f.append(arrow(cx1 + r_wire, cy1, cx1 + 90, cy1, color=COLOR_RED, sw=3.5))
    f.append(text(cx1 + 45, cy1 - 12, "F₁₂", size=15, bold=True, color=COLOR_RED))

    f.append(arrow(cx2 - r_wire, cy2, cx2 - 90, cy2, color=COLOR_RED, sw=3.5))
    f.append(text(cx2 - 55, cy2 - 12, "F₂₁", size=15, bold=True, color=COLOR_RED))

    # Відстань r між осями
    f.append(line(cx1, cy1 + 90, cx2, cy1 + 90, color=COLOR_DARK, sw=1.5))
    f.append(line(cx1, cy1 + 75, cx1, cy1 + 105, color=COLOR_DARK, sw=1.2))
    f.append(line(cx2, cy2 + 75, cx2, cy2 + 105, color=COLOR_DARK, sw=1.2))
    f.append(text(320, cy1 + 84, "відстань r", size=13, bold=True, color=COLOR_DARK))

    # Пояснювальний блок справа
    box_x = 550
    f.append(rect(box_x, 60, 150, 240, fill='#f8f9fa', stroke='#bdc3c7', sw=1.5, rx=6))
    f.append(text(box_x + 75, 82, "Фізичний механізм", size=12, bold=True, color=COLOR_DARK))
    f.append(text(box_x + 75, 110, "1. Поле B₁ від I₁", size=11, color=INK))
    f.append(text(box_x + 75, 128, "діє на струм I₂.", size=11, color=INK))
    f.append(text(box_x + 75, 155, "2. Між дротами", size=11, color=INK))
    f.append(text(box_x + 75, 173, "поля віднімаються.", size=11, color=COLOR_BLUE))
    f.append(text(box_x + 75, 200, "3. Назовні поля", size=11, color=INK))
    f.append(text(box_x + 75, 218, "додаються.", size=11, color=COLOR_BLUE))
    f.append(text(box_x + 75, 255, "Натяг ліній B", size=12, bold=True, color=COLOR_RED))
    f.append(text(box_x + 75, 275, "ЗШТОВХУЄ дроти!", size=12, bold=True, color=COLOR_RED))

    write_svg(f, os.path.join(IMG, 'parallel-wires-fields.svg'), W, H)


# ── Фігура 2: Відштовхування відносно протилежних струмів ───────────────────
def fig_antiparallel_wires_fields():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Взаємодія паралельних провідників з протилежними струмами (Відштовхування)", size=15, bold=True))

    cx1, cy1 = 220, 180
    cx2, cy2 = 440, 180
    r_wire = 18

    # Поле лівого (I1 ⊗ в екран)
    for r_field in [40, 65, 90]:
        f.append(circle(cx1, cy1, r_field, fill='none', stroke=COLOR_BLUE, sw=1.5))
    f.append(arrow(cx1, cy1 - 65, cx1 + 15, cy1 - 65, color=COLOR_BLUE, sw=1.8))
    f.append(arrow(cx1 + 65, cy1, cx1 + 65, cy1 + 15, color=COLOR_BLUE, sw=1.8))

    # Поле правого (I2 ⊙ з екрану)
    for r_field in [40, 65, 90]:
        f.append(circle(cx2, cy2, r_field, fill='none', stroke=COLOR_GREEN, sw=1.5))
    f.append(arrow(cx2, cy2 - 65, cx2 - 15, cy2 - 65, color=COLOR_GREEN, sw=1.8))
    f.append(arrow(cx2 - 65, cy2, cx2 - 65, cy2 + 15, color=COLOR_GREEN, sw=1.8))

    # Провідник 1 (⊗ I1)
    f.append(circle(cx1, cy1, r_wire, fill='#e8f0fe', stroke=COLOR_BLUE, sw=2.5))
    f.append(text(cx1, cy1 + 5, "⊗ I₁", size=13, bold=True, color=COLOR_BLUE))
    f.append(text(cx1, cy1 - 28, "Провідник 1 (в екран)", size=12, bold=True))

    # Провідник 2 (⊙ I2)
    f.append(circle(cx2, cy2, r_wire, fill='#e8f8f5', stroke=COLOR_GREEN, sw=2.5))
    f.append(text(cx2, cy2 + 5, "⊙ I₂", size=13, bold=True, color=COLOR_GREEN))
    f.append(text(cx2, cy2 - 28, "Провідник 2 (з екрану)", size=12, bold=True))

    # Вектори сил F12 та F21 (направлені НАЗОВНІ)
    f.append(arrow(cx1 - r_wire, cy1, cx1 - 90, cy1, color=COLOR_RED, sw=3.5))
    f.append(text(cx1 - 55, cy1 - 12, "F₁₂", size=15, bold=True, color=COLOR_RED))

    f.append(arrow(cx2 + r_wire, cy2, cx2 + 90, cy2, color=COLOR_RED, sw=3.5))
    f.append(text(cx2 + 45, cy2 - 12, "F₂₁", size=15, bold=True, color=COLOR_RED))

    # Підсилене поле у зазорі
    f.append(rect(305, 110, 50, 140, fill='#fadbd8', stroke=COLOR_RED, sw=1.2, rx=4))
    f.append(text(330, 160, "Густе поле B", size=11, bold=True, color=COLOR_RED))
    f.append(text(330, 180, "у зазорі!", size=11, bold=True, color=COLOR_RED))
    f.append(text(330, 200, "(B₁ + B₂)", size=10, bold=True, color=COLOR_DARK))

    # Пояснення справа
    box_x = 550
    f.append(rect(box_x, 60, 150, 240, fill='#f8f9fa', stroke='#bdc3c7', sw=1.5, rx=6))
    f.append(text(box_x + 75, 82, "Фізичний механізм", size=12, bold=True, color=COLOR_DARK))
    f.append(text(box_x + 75, 110, "1. Поля в зазорі", size=11, color=INK))
    f.append(text(box_x + 75, 128, "ДОДАЮТЬСЯ.", size=11, bold=True, color=COLOR_RED))
    f.append(text(box_x + 75, 155, "2. Магнітний тиск", size=11, color=INK))
    f.append(text(box_x + 75, 173, "w = B²/(2μ₀)", size=11, bold=True, color=COLOR_DARK))
    f.append(text(box_x + 75, 191, "у зазорі максимальний.", size=11, color=INK))
    f.append(text(box_x + 75, 225, "Високий тиск", size=12, bold=True, color=COLOR_RED))
    f.append(text(box_x + 75, 245, "РОЗПИРАЄ дроти", size=12, bold=True, color=COLOR_RED))
    f.append(text(box_x + 75, 265, "урізнобіч!", size=12, bold=True, color=COLOR_RED))

    write_svg(f, os.path.join(IMG, 'antiparallel-wires-fields.svg'), W, H)


# ── Фігура 3: Електродинамічні сили у трифазному шинопроводі ───────────────
def fig_busbar_short_circuit():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Електродинамічні сили в шинопроводі під час ударного короткого замикання", size=15, bold=True))

    b1_x = 140
    b2_x = 360
    b3_x = 580
    b_y = 120
    b_w, b_h = 30, 160

    # Опорні ізолятори
    f.append(rect(b1_x - 10, b_y + b_h, 50, 40, fill='#d5dbdb', stroke=COLOR_DARK, sw=1.8, rx=3))
    f.append(rect(b2_x - 10, b_y + b_h, 50, 40, fill='#d5dbdb', stroke=COLOR_DARK, sw=1.8, rx=3))
    f.append(rect(b3_x - 10, b_y + b_h, 50, 40, fill='#d5dbdb', stroke=COLOR_DARK, sw=1.8, rx=3))
    f.append(rect(60, b_y + b_h + 40, 640, 15, fill='#7f8c8d', stroke=COLOR_DARK, sw=1.5, rx=2))
    f.append(text(380, b_y + b_h + 52, "Сталева несуча балка / конструкція розподільчого щита", size=12, color='#ffffff', bold=True))

    # Мідні шини
    f.append(rect(b1_x, b_y, b_w, b_h, fill='#e59866', stroke=COLOR_ORANGE, sw=2, rx=2))
    f.append(text(b1_x + b_w / 2, b_y + 40, "L₁", size=16, bold=True, color='#7e5109'))
    f.append(text(b1_x + b_w / 2, b_y + 80, "i₁(t)", size=13, bold=True, color=COLOR_DARK))
    f.append(text(b1_x + b_w / 2, b_y + 110, "+50 kA", size=11, bold=True, color=COLOR_RED))

    f.append(rect(b2_x, b_y, b_w, b_h, fill='#e59866', stroke=COLOR_ORANGE, sw=2, rx=2))
    f.append(text(b2_x + b_w / 2, b_y + 40, "L₂", size=16, bold=True, color='#7e5109'))
    f.append(text(b2_x + b_w / 2, b_y + 80, "i₂(t)", size=13, bold=True, color=COLOR_DARK))
    f.append(text(b2_x + b_w / 2, b_y + 110, "-80 kA", size=11, bold=True, color=COLOR_BLUE))

    f.append(rect(b3_x, b_y, b_w, b_h, fill='#e59866', stroke=COLOR_ORANGE, sw=2, rx=2))
    f.append(text(b3_x + b_w / 2, b_y + 40, "L₃", size=16, bold=True, color='#7e5109'))
    f.append(text(b3_x + b_w / 2, b_y + 80, "i₃(t)", size=13, bold=True, color=COLOR_DARK))
    f.append(text(b3_x + b_w / 2, b_y + 110, "+30 kA", size=11, bold=True, color=COLOR_RED))

    # Відстані a між шинами
    f.append(line(b1_x + b_w, b_y - 25, b2_x, b_y - 25, color=COLOR_DARK, sw=1.5))
    f.append(line(b1_x + b_w, b_y - 35, b1_x + b_w, b_y - 15, color=COLOR_DARK, sw=1.2))
    f.append(line(b2_x, b_y - 35, b2_x, b_y - 15, color=COLOR_DARK, sw=1.2))
    f.append(text((b1_x + b_w + b2_x) / 2, b_y - 32, "a = 250 мм", size=12, bold=True))

    f.append(line(b2_x + b_w, b_y - 25, b3_x, b_y - 25, color=COLOR_DARK, sw=1.5))
    f.append(line(b2_x + b_w, b_y - 35, b2_x + b_w, b_y - 15, color=COLOR_DARK, sw=1.2))
    f.append(line(b3_x, b_y - 35, b3_x, b_y - 15, color=COLOR_DARK, sw=1.2))
    f.append(text((b2_x + b_w + b3_x) / 2, b_y - 32, "a = 250 мм", size=12, bold=True))

    # Електродинамічні сили на шину L2 в піковий момент КЗ
    f.append(arrow(b2_x, b_y + 60, b2_x - 110, b_y + 60, color=COLOR_RED, sw=4))
    f.append(text(b2_x - 60, b_y + 42, "F_din = 18.5 кН/м", size=13, bold=True, color=COLOR_RED))

    # Згинний момент на ізолятор
    f.append(arrow(b2_x + 15, b_y + b_h + 15, b2_x - 60, b_y + b_h + 15, color=COLOR_PURPLE, sw=3))
    f.append(text(b2_x - 30, b_y + b_h + 32, "M_згин", size=12, bold=True, color=COLOR_PURPLE))

    # Попередження про руйнування
    f.append(rect(60, 50, 200, 45, fill='#fef9e7', stroke='#f1c40f', sw=1.5, rx=4))
    f.append(text(160, 68, "Ризик: вигин шин та", size=11, bold=True, color='#b7950b'))
    f.append(text(160, 86, "розрив ізоляторів!", size=11, bold=True, color=COLOR_RED))

    write_svg(f, os.path.join(IMG, 'busbar-short-circuit.svg'), W, H)


# ── Фігура 4: Рейкотрон та Z-пінч ──────────────────────────────────────────
def fig_railgun_force():
    W, H = 760, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Приклади потужних взаємодій: Рейкотрон (ліворуч) та Z-пінч плазми (праворуч)", size=15, bold=True))

    midx = W / 2
    f.append(line(midx, 45, midx, H - 25, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Рейкотрон (Railgun) ---
    f.append(text(midx / 2, 52, "Рейкотрон: відштовхування рейок і розгін снаряда", size=13, bold=True, color=COLOR_DARK))

    # Верхня рейка (+ струм вправо)
    f.append(rect(50, 90, 260, 20, fill='#f5b041', stroke=COLOR_ORANGE, sw=2, rx=3))
    f.append(arrow(60, 100, 180, 100, color=COLOR_BLUE, sw=2.5))
    f.append(text(120, 80, "Верхня рейка (струм I →)", size=11, bold=True, color=COLOR_BLUE))

    # Нижня рейка (- струм вліво)
    f.append(rect(50, 210, 260, 20, fill='#f5b041', stroke=COLOR_ORANGE, sw=2, rx=3))
    f.append(arrow(180, 220, 60, 220, color=COLOR_BLUE, sw=2.5))
    f.append(text(120, 245, "Нижня рейка (струм ← I)", size=11, bold=True, color=COLOR_BLUE))

    # Рухома якорь-снаряд (вертикальна перемичка)
    f.append(rect(180, 110, 40, 100, fill='#e74c3c', stroke=COLOR_RED, sw=2, rx=3))
    # Текст на якорі без стрілки, що його перетинає!
    f.append(text(200, 160, "Якір", size=13, bold=True, color='#ffffff'))

    # Сила відштовхування рейок F_out
    f.append(arrow(120, 90, 120, 60, color=COLOR_RED, sw=2.5))
    f.append(text(120, 52, "F_розпирання", size=10, bold=True, color=COLOR_RED))

    f.append(arrow(120, 230, 120, 260, color=COLOR_RED, sw=2.5))
    f.append(text(120, 275, "F_розпирання", size=10, bold=True, color=COLOR_RED))

    # Сила Лоренца F_accel на снаряд вздовж ствола
    f.append(arrow(225, 160, 315, 160, color=COLOR_GREEN, sw=4))
    f.append(text(270, 142, "Сила прискорення F_L", size=11, bold=True, color=COLOR_GREEN))
    f.append(text(270, 180, "v > 2000 м/с", size=11, bold=True, color=COLOR_DARK))

    # --- ПРАВА ЧАСТИНА: Z-пінч плазми ---
    f.append(text(midx + midx / 2, 52, "Z-пінч: самостискання плазмового шнура", size=13, bold=True, color=COLOR_DARK))

    # Плазмовий шнур (циліндр)
    px, py = 560, 160
    f.append(dellipse(px, py, 60, 90, fill='#ebf5fb', stroke=COLOR_BLUE, sw=2.0))

    # Окремі паралельні нитки струму всередині плазми
    for dy in [-50, -25, 0, 25, 50]:
        f.append(line(px - 40, py + dy, px + 40, py + dy, color=COLOR_PURPLE, sw=1.8))
        f.append(arrow(px - 20, py + dy, px + 20, py + dy, color=COLOR_PURPLE, sw=1.8))

    f.append(text(px, py - 65, "Струмові нитки I ∥ I", size=11, bold=True, color=COLOR_PURPLE))

    # Сили стискання F_pinch (вказівка всередину циліндра)
    f.append(arrow(px - 75, py, px - 35, py, color=COLOR_RED, sw=3))
    f.append(arrow(px + 75, py, px + 35, py, color=COLOR_RED, sw=3))
    f.append(arrow(px, py - 100, px, py - 65, color=COLOR_RED, sw=3))
    f.append(arrow(px, py + 100, px, py + 65, color=COLOR_RED, sw=3))

    f.append(text(px, py + 118, "Магнітний стиск (Z-Pinch)", size=12, bold=True, color=COLOR_RED))

    write_svg(f, os.path.join(IMG, 'railgun-force.svg'), W, H)


if __name__ == '__main__':
    fig_parallel_wires_fields()
    fig_antiparallel_wires_fields()
    fig_busbar_short_circuit()
    fig_railgun_force()
    print("Усі 4 фігури успішно створено в ./img/")
