# -*- coding: utf-8 -*-
"""Фігури до теми «Потенціальна енергія в електричному полі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def path_tag(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{dash_attr}/>'

# ── Фігура 1: Переміщення заряду та робота поля ─────────────────────────────
def fig_charge_potential_work():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Робота електростатичного поля та зміна потенціальної енергії", size=16, bold=True))

    # Панель поля
    f.append(rect(20, 46, W - 40, H - 74, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=12))

    # Еквіпотенціальні лінії (вертикальні пунктири)
    phi_vals = ["φ₁ = 100 В", "φ₂ = 75 В", "φ₃ = 50 В", "φ₄ = 25 В", "φ₅ = 0 В"]
    x_coords = [80, 210, 340, 470, 600]
    for x, phi in zip(x_coords, phi_vals):
        f.append(line(x, 60, x, H - 65, color=MUTED, sw=1, dash="4,4"))
        f.append(text(x, 75, phi, size=11, color=MUTED))

    # Лінії напруженості поля E (горизонтальні зелені стрілки)
    for y in [110, 270]:
        f.append(line(50, y, 630, y, color=FIELD, sw=1.2, dash="6,3"))
        f.append(arrow(630, y, 650, y, color=FIELD, sw=1.5))
        f.append(text(660, y + 4, "E", size=13, bold=True, color=FIELD, anchor="start"))

    # Траєкторія руху заряду між точками A і B
    ax, ay = 140, 210
    bx, by = 490, 150

    # Криволінійний шлях C
    f.append(path_tag(f"M {ax} {ay} C 250 110, 380 260, {bx} {by}", stroke=POS, sw=2.5))
    f.append(arrow(330, 205, 350, 200, color=POS, sw=2.5))
    f.append(text(310, 235, "Шлях C", size=13, bold=True, color=POS))

    # Точка A
    f.append(circle(ax, ay, 9, fill=POS, stroke=INK, sw=1.2))
    f.append(text(ax, ay - 14, "Точка A (q > 0)", size=12, bold=True, color=INK))
    f.append(text(ax, ay + 22, "U_A = q φ₁", size=11, color=MUTED))

    # Точка B
    f.append(circle(bx, by, 9, fill=POS, stroke=INK, sw=1.2))
    f.append(text(bx, by - 14, "Точка B", size=12, bold=True, color=INK))
    f.append(text(bx, by + 22, "U_B = q φ₄", size=11, color=MUTED))

    # Сила поля та зовнішня сила на заряді під час руху
    px, py = 340, 198
    f.append(line(px, py, px + 30, py, color=FIELD, sw=2))
    f.append(arrow(px + 30, py, px + 50, py, color=FIELD, sw=2))
    f.append(text(px + 55, py - 6, "F_ел = qE", size=11, bold=True, color=FIELD, anchor="start"))

    # Нижній висновок
    b = textbox(W / 2, H - 22, "W_[A→B] = -ΔU = U_A - U_B = q (φ_A - φ_B)", size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)[0]
    f.append(b)

    return render(os.path.join(IMG, "charge-potential-work.svg"), W, H, *f)

# ── Фігура 2: Потенціальна енергія взаємодії двох точкових зарядів ───────────
def fig_pair_interaction_energy():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Потенціальна енергія взаємодії двох точкових зарядів U(r)", size=16, bold=True))

    # Ліва частина: Геометрія зарядів
    f.append(rect(20, 48, 300, H - 74, fill=FILL, stroke="#d0d7de", sw=1.2, rx=8))
    f.append(text(170, 70, "Взаємодія точкових зарядів", size=13, bold=True))

    # Заряд q1
    q1x, q1y = 80, 160
    f.append(circle(q1x, q1y, 16, fill=POS, stroke=INK, sw=1.5))
    f.append(text(q1x, q1y + 5, "+q₁", size=14, bold=True, color=BG))

    # Заряд q2
    q2x, q2y = 240, 160
    f.append(circle(q2x, q2y, 16, fill=POS, stroke=INK, sw=1.5))
    f.append(text(q2x, q2y + 5, "+q₂", size=14, bold=True, color=BG))

    # Відстань r12
    f.append(line(q1x + 18, q1y, q2x - 18, q2y, color=INK, sw=1.5))
    f.append(arrow(q1x + 20, q1y, q1x + 35, q1y, color=INK, sw=1.5))
    f.append(arrow(q2x - 20, q2y, q2x - 35, q2y, color=INK, sw=1.5))
    f.append(text(160, 150, "r₁₂", size=13, bold=True))

    # Сили відштовхування
    f.append(line(q1x - 18, q1y, q1x - 35, q1y, color=POS, sw=2))
    f.append(arrow(q1x - 35, q1y, q1x - 55, q1y, color=POS, sw=2))
    f.append(text(q1x - 60, q1y - 6, "F₁₂", size=11, bold=True, color=POS, anchor="end"))

    f.append(line(q2x + 18, q2y, q2x + 35, q2y, color=POS, sw=2))
    f.append(arrow(q2x + 35, q2y, q2x + 55, q2y, color=POS, sw=2))
    f.append(text(q2x + 60, q2y - 6, "F₂₁", size=11, bold=True, color=POS, anchor="start"))

    # Формула енергії для 2 зарядів
    b1 = textbox(170, 260, "U₁₂ = (1 / 4πε₀) · (q₁ q₂ / r₁₂)", size=12, pad=6, fill=BG, stroke=POS, sw=1.2, bold=True)[0]
    f.append(b1)
    f.append(text(170, 310, "Однойменні: U > 0 (відштовхування)", size=11, color=POS))
    f.append(text(170, 328, "Різнойменні: U < 0 (притягання)", size=11, color=NEG))

    # Права частина: Графік U(r)
    ox, oy = 370, 220
    f.append(rect(340, 48, 360, H - 74, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    f.append(text(520, 70, "Графік залежності U(r)", size=13, bold=True))

    # Осі координат
    f.append(line(ox, 95, ox, 330, color=INK, sw=1.5)) # U axis
    f.append(arrow(ox, 95, ox, 80, color=INK, sw=1.5))
    f.append(text(ox - 10, 85, "U", size=13, bold=True))

    f.append(line(ox - 10, oy, 660, oy, color=INK, sw=1.5)) # r axis
    f.append(arrow(660, oy, 680, oy, color=INK, sw=1.5))
    f.append(text(675, oy + 20, "r", size=13, bold=True))

    # Крива для одноіменних зарядів (U > 0, гіпербола у 1 чверті)
    pts_rep = []
    for rx_val in range(15, 290, 5):
        r_real = rx_val / 40.0
        u_val = 1.0 / r_real
        px = ox + rx_val
        py = oy - u_val * 40.0
        if py >= 90:
            pts_rep.append(f"{px:.1f},{py:.1f}")
    if pts_rep:
        f.append(path_tag("M " + " L ".join(pts_rep), stroke=POS, sw=2.5))
        f.append(text(570, 115, "q₁ q₂ > 0 (U > 0)", size=12, bold=True, color=POS))

    # Крива для різноїменних зарядів (U < 0, гіпербола у 4 чверті)
    pts_att = []
    for rx_val in range(15, 290, 5):
        r_real = rx_val / 40.0
        u_val = -1.0 / r_real
        px = ox + rx_val
        py = oy - u_val * 40.0
        if py <= 320:
            pts_att.append(f"{px:.1f},{py:.1f}")
    if pts_att:
        f.append(path_tag("M " + " L ".join(pts_att), stroke=NEG, sw=2.5))
        f.append(text(570, 295, "q₁ q₂ < 0 (U < 0)", size=12, bold=True, color=NEG))

    return render(os.path.join(IMG, "pair-interaction-energy.svg"), W, H, *f)

# ── Фігура 3: Густина енергії поля та локалізація в просторі ────────────────
def fig_field_energy_density():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Об'ємна густина енергії електричного поля w = ½ ε₀ E²", size=16, bold=True))

    # Фоновій контейнер простір
    f.append(rect(20, 48, W - 40, H - 74, fill="#f9fbfd", stroke=FIELD, sw=1.5, rx=12))

    # Заряд Q у центрі ліворуч
    cx, cy = 180, 200
    f.append(circle(cx, cy, 26, fill=POS, stroke=INK, sw=2))
    f.append(text(cx, cy + 6, "+Q", size=18, bold=True, color=BG))

    # Радіальні лінії силового поля E
    angles = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    for a in angles:
        rad = math.radians(a)
        x1 = cx + 30 * math.cos(rad)
        y1 = cy + 30 * math.sin(rad)
        x2 = cx + 240 * math.cos(rad)
        y2 = cy + 240 * math.sin(rad)
        x2 = max(35, min(W - 35, x2))
        y2 = max(60, min(H - 40, y2))
        f.append(line(x1, y1, x2, y2, color=FIELD, sw=1.3, dash="4,3"))
        if a % 60 == 0:
            xm = cx + 130 * math.cos(rad)
            ym = cy + 130 * math.sin(rad)
            f.append(arrow(xm - 10 * math.cos(rad), ym - 10 * math.sin(rad), xm, ym, color=FIELD, sw=1.5))

    # Об'ємний елемент dV у просторі поля
    vx, vy = 440, 140
    vw, vh = 110, 90
    f.append(rect(vx, vy, vw, vh, fill="#e8f5e9", stroke=FIELD, sw=2, rx=6))
    f.append(text(vx + vw / 2, vy + 28, "Елемент об'єму dV", size=12, bold=True, color=FIELD))
    f.append(text(vx + vw / 2, vy + 50, "w = ½ ε₀ E²", size=14, bold=True, color=INK))
    f.append(text(vx + vw / 2, vy + 70, "dW = w · dV", size=12, color=MUTED))

    # Поле E всередині dV
    f.append(line(vx - 25, vy + vh / 2, vx + vw, vy + vh / 2, color=FIELD, sw=2))
    f.append(arrow(vx + vw, vy + vh / 2, vx + vw + 25, vy + vh / 2, color=FIELD, sw=2))
    f.append(text(vx + vw + 35, vy + vh / 2 + 4, "E(r)", size=13, bold=True, color=FIELD, anchor="start"))

    # Права рамка з математичним зв'язком
    f.append(rect(430, 255, 250, 80, fill=BG, stroke=INK, sw=1.2, rx=8))
    f.append(text(555, 275, "Повна енергія поля:", size=12, bold=True))
    f.append(text(555, 302, "W = ∫ [V] (½ ε₀ E²) dV", size=14, bold=True, color=POS))

    # Нижній висновок
    b = textbox(220, H - 22, "Енергія локалізована в полі, а не «всередині» точкових зарядів", size=12, pad=6, fill=FILL, stroke=MUTED, sw=1.2)[0]
    f.append(b)

    return render(os.path.join(IMG, "field-energy-density.svg"), W, H, *f)

# ── Фігура 4: Механічна сила та градієнт потенціальної енергії ───────────────
def fig_capacitor_pull_force():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Втягування діелектрика в конденсатор: F = -∂U/∂x", size=16, bold=True))

    # Конденсатор і пластини
    px1, px2 = 100, 480
    py_top = 100
    py_bot = 250

    # Верхня пластина (+Q)
    f.append(rect(px1, py_top - 12, px2 - px1, 14, fill=POS, stroke=INK, sw=1.2, rx=2))
    f.append(text(px1 - 45, py_top - 2, "+Q", size=14, bold=True, color=POS))
    for x in range(px1 + 30, px2 - 20, 60):
        f.append(text(x, py_top + 18, "+", size=14, bold=True, color=POS))

    # Нижня пластина (-Q)
    f.append(rect(px1, py_bot, px2 - px1, 14, fill=NEG, stroke=INK, sw=1.2, rx=2))
    f.append(text(px1 - 45, py_bot + 12, "-Q", size=14, bold=True, color=NEG))
    for x in range(px1 + 30, px2 - 20, 60):
        f.append(text(x, py_bot - 6, "−", size=14, bold=True, color=NEG))

    # Діелектрична пластина (частково всунута)
    dx1 = 260
    dx2 = 580
    f.append(rect(dx1, py_top + 4, dx2 - dx1, py_bot - py_top - 8, fill="#e1f5fe", stroke=NEG, sw=1.8, rx=4))
    f.append(text((dx1 + px2) / 2, (py_top + py_bot) / 2 - 10, "Діелектрик (ε > 1)", size=13, bold=True, color=NEG))

    # Вісь х
    f.append(line(80, 300, 620, 300, color=INK, sw=1.5))
    f.append(arrow(620, 300, 640, 300, color=INK, sw=1.5))
    f.append(text(645, 304, "x", size=14, bold=True))

    # Позначення глибини занурення х
    f.append(line(px1, 280, px1, 310, color=MUTED, sw=1, dash="3,3"))
    f.append(line(dx1, 280, dx1, 310, color=MUTED, sw=1, dash="3,3"))
    f.append(line(px1 + 15, 290, dx1 - 15, 290, color=INK, sw=1.2))
    f.append(arrow(px1 + 15, 290, px1, 290, color=INK, sw=1.2))
    f.append(arrow(dx1 - 15, 290, dx1, 290, color=INK, sw=1.2))
    f.append(text((px1 + dx1) / 2, 284, "x", size=13, bold=True))

    # Електростатична сила втягування F_x
    f.append(line(dx1 - 45, (py_top + py_bot) / 2 + 15, dx1 - 70, (py_top + py_bot) / 2 + 15, color=POS, sw=2.5))
    f.append(arrow(dx1 - 45, (py_top + py_bot) / 2 + 15, dx1 - 70, (py_top + py_bot) / 2 + 15, color=POS, sw=2.5))
    f.append(text(dx1 - 80, (py_top + py_bot) / 2 + 20, "F_x", size=15, bold=True, color=POS, anchor="end"))

    # Текстова панель з формулою сили
    b = textbox(W / 2, H - 25, "При Q = const:   F_x = -(∂U / ∂x)_Q = ½ V² (dC / dx) > 0   (напрямлена в бік зростання ємності)", size=12.5, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)[0]
    f.append(b)

    return render(os.path.join(IMG, "capacitor-pull-force.svg"), W, H, *f)

if __name__ == '__main__':
    fig_charge_potential_work()
    fig_pair_interaction_energy()
    fig_field_energy_density()
    fig_capacitor_pull_force()
    print("Всі 4 фігури успішно згенеровано у ./img/")
