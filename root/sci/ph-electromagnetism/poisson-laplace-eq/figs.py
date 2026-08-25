# -*- coding: utf-8 -*-
"""Фігури до теми «Рівняння Пуассона і Лапласа».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Фігура 1: Порівняння Пуассона та Лапласа ────────────────────────────────
def fig_poisson_vs_laplace():
    W, H = 760, 360
    frags = []
    
    # Заголовок
    frags.append(text(W / 2, 28, "Порівняння областей дій рівнянь Пуассона та Лапласа", size=16, bold=True))

    midx = W / 2
    frags.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    # Ліва частина — Рівняння Пуассона
    frags.append(text(midx / 2, 55, "Рівняння Пуассона (область із зарядом ρ ≠ 0)", size=13, bold=True, color=POS))
    # Контур області
    frags.append(rect(30, 80, 320, 200, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    # Об'ємний заряд (знаки +)
    for cx, cy in [(90, 130), (160, 110), (230, 140), (120, 180), (200, 190), (270, 170)]:
        frags.append(circle(cx, cy, 14, fill="#fbe9e7", stroke=POS, sw=1.2))
        frags.append(text(cx, cy + 4, "+", size=14, bold=True, color=POS))
    # Лінії поля (виходять з об'єму)
    frags.append(arrow(160, 110, 160, 60, color=POS, sw=1.5))
    frags.append(arrow(230, 140, 300, 140, color=POS, sw=1.5))
    frags.append(arrow(90, 130, 40, 130, color=POS, sw=1.5))
    # Формула
    tb1, _, _ = textbox(190, 240, "∇²φ = −ρ / ε₀", size=15, bold=True, fill="#ffffff", stroke=POS, sw=1.5)
    frags.append(tb1)
    frags.append(text(190, 310, "Джерела/стоки поля є всередині області", size=12, italic=True, color=INK))

    # Права частина — Рівняння Лапласа
    frags.append(text(midx + midx / 2, 55, "Рівняння Лапласа (вакуум або діелектрик, ρ = 0)", size=13, bold=True, color=NEG))
    # Контур області між електродами
    frags.append(rect(410, 80, 320, 200, fill="#f0f4fe", stroke=NEG, sw=1.8, rx=8))
    # Електроди з боків
    frags.append(rect(410, 80, 20, 200, fill="#d0e1fd", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(420, 180, "V₁", size=13, bold=True, color=NEG))
    frags.append(rect(710, 80, 20, 200, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=2))
    frags.append(text(720, 180, "V₂", size=13, bold=True, color=INK))
    # Силові лінії проходять наскрізь
    for y in [120, 150, 180, 210]:
        frags.append(arrow(435, y, 705, y, color=NEG, sw=1.4))
    # Формула
    tb2, _, _ = textbox(570, 240, "∇²φ = 0", size=15, bold=True, fill="#ffffff", stroke=NEG, sw=1.5)
    frags.append(tb2)
    frags.append(text(570, 310, "Поле задається лише на межах (електродах)", size=12, italic=True, color=INK))

    render(os.path.join(IMG, "poisson-vs-laplace.svg"), W, H, *frags)


# ── Фігура 2: Властивість середнього значення ──────────────────────────────
def fig_mean_value_property():
    W, H = 680, 340
    frags = []
    
    frags.append(text(W / 2, 26, "Теорема про середнє значення для рівняння Лапласа", size=16, bold=True))

    # Сфера/коло навколо точки x0
    cx, cy, R = 220, 180, 100
    frags.append(circle(cx, cy, R, fill="#f4f8ff", stroke=NEG, sw=2.0))
    frags.append(circle(cx, cy, 5, fill=NEG, stroke=NEG, sw=1.0))
    frags.append(text(cx, cy - 12, "φ(x₀)", size=14, bold=True, color=NEG))

    # Радіус R
    frags.append(line(cx, cy, cx + R * 0.707, cy - R * 0.707, color=LINE, sw=1.5, dash="4,4"))
    frags.append(text(cx + R * 0.35 + 8, cy - R * 0.35 - 5, "R", size=13, bold=True, color=INK))

    # Точки на колі S
    import math
    for angle in [0, 1.047, 2.094, 3.1415, 4.188, 5.235]:
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)
        frags.append(circle(px, py, 3.5, fill=POS, stroke=POS, sw=1.0))

    frags.append(text(cx + R + 18, cy, "Сфера S", size=12, color=MUTED))

    # Пояснення праворуч
    tx = 480
    tb, _, _ = textbox(tx, 140, "φ(x₀) = (1 / 4π R²) ∮ₛ φ dS", size=15, bold=True, fill="#ffffff", stroke=NEG, sw=1.8)
    frags.append(tb)

    frags.append(text(tx, 210, "Потенціал у центрі дорівнює", size=13, bold=True, color=INK))
    frags.append(text(tx, 230, "середньому арифметичному потенціалів", size=13, color=INK))
    frags.append(text(tx, 250, "на очіпляючій сфері S.", size=13, color=INK))
    frags.append(text(tx, 290, "Наслідок: локальні максимуми/мінімуми", size=12, bold=True, color=POS))
    frags.append(text(tx, 310, "усередині порожньої області неможливі!", size=12, color=POS))

    render(os.path.join(IMG, "mean-value-property.svg"), W, H, *frags)


# ── Фігура 3: 5-точковий шаблон кінцево-різницевої сітки ────────────────────
def fig_fdm_5point_stencil():
    W, H = 720, 360
    frags = []
    
    frags.append(text(W / 2, 26, "5-точковий хрестоподібний шаблон сітки (FDM)", size=16, bold=True))

    cx, cy = 230, 190
    h = 80

    # Сітка (пунктир)
    for offset in [-h, 0, h]:
        frags.append(line(cx - h - 30, cy + offset, cx + h + 30, cy + offset, color="#e2e8f0", sw=1.2, dash="3,3"))
        frags.append(line(cx + offset, cy - h - 30, cx + offset, cy + h + 30, color="#e2e8f0", sw=1.2, dash="3,3"))

    # Зв'язки між вузлами — малюємо ВІД КРАЇВ центрального круга (r=18) до КРАЇВ сусіда (r=16)
    frags.append(line(cx + 18, cy, cx + h - 16, cy, color=FIELD, sw=2.2))
    frags.append(line(cx - 18, cy, cx - h + 16, cy, color=FIELD, sw=2.2))
    frags.append(line(cx, cy - 18, cx, cy - h + 16, color=FIELD, sw=2.2))
    frags.append(line(cx, cy + 18, cx, cy + h - 16, color=FIELD, sw=2.2))

    # Крок h
    frags.append(text(cx + h / 2, cy - 10, "h", size=12, bold=True, color=FIELD))
    frags.append(text(cx - 12, cy - h / 2, "h", size=12, bold=True, color=FIELD))

    # Центральний вузол
    frags.append(circle(cx, cy, 18, fill="#e6f4ea", stroke=FIELD, sw=2.2))
    frags.append(text(cx, cy + 4, "i, j", size=12, bold=True, color=FIELD))

    # 4 сусідні вузли
    nodes = [
        (cx + h, cy, "i+1, j"),
        (cx - h, cy, "i-1, j"),
        (cx, cy - h, "i, j+1"),
        (cx, cy + h, "i, j-1")
    ]
    for nx, ny, lbl in nodes:
        frags.append(circle(nx, ny, 16, fill="#ffffff", stroke=LINE, sw=1.8))
        frags.append(text(nx, ny + 4, lbl, size=11, bold=True, color=INK))

    # Формула праворуч
    tx = 530
    tb, _, _ = textbox(tx, 130, "φ[i][j] = ¼ (φ[i+1][j] + φ[i-1][j] +\n          φ[i][j+1] + φ[i][j-1]) +\n        + ¼ h² (ρ[i][j] / ε₀)", size=13, bold=True, fill="#ffffff", stroke=FIELD, sw=1.8)
    frags.append(tb)

    frags.append(text(tx, 230, "Дискретне наближення оператора Лапласа:", size=12, bold=True, color=INK))
    frags.append(text(tx, 255, "∇²φ ≈ (φ[i+1][j] + φ[i-1][j] + φ[i][j+1] +", size=12, color=MUTED))
    frags.append(text(tx, 275, "       + φ[i][j-1] − 4φ[i][j]) / h²", size=12, color=MUTED))
    frags.append(text(tx, 310, "Основа чисельних методів Якобі та Гаусса-Зейделя", size=12, italic=True, color=INK))

    render(os.path.join(IMG, "fdm-5point-stencil.svg"), W, H, *frags)


# ── Фігура 4: Крайові умови ──────────────────────────────────────────────────
def fig_boundary_conditions():
    W, H = 760, 360
    frags = []
    
    frags.append(text(W / 2, 26, "Класифікація крайових умов у задачах електростатики", size=16, bold=True))

    # 3 блоки для трьох типів крайових умов
    box_w = 220
    box_h = 240
    y0 = 75

    # 1. Діріхле
    x1 = 30
    frags.append(rect(x1, y0, box_w, box_h, fill="#f0f4fe", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(x1 + box_w / 2, y0 + 30, "Умова Діріхле (1-го роду)", size=13, bold=True, color=NEG))
    frags.append(rect(x1 + 30, y0 + 60, box_w - 60, 45, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(x1 + box_w / 2, y0 + 87, "φ|Γ = V₀ (фіксований)", size=13, bold=True, color=NEG))
    frags.append(text(x1 + box_w / 2, y0 + 130, "Фіксований потенціал", size=12, bold=True, color=INK))
    frags.append(text(x1 + box_w / 2, y0 + 155, "Металеві електроди,", size=12, color=MUTED))
    frags.append(text(x1 + box_w / 2, y0 + 175, "підключені до джерел", size=12, color=MUTED))
    frags.append(text(x1 + box_w / 2, y0 + 195, "напруги.", size=12, color=MUTED))

    # 2. Неймана
    x2 = 270
    frags.append(rect(x2, y0, box_w, box_h, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    frags.append(text(x2 + box_w / 2, y0 + 30, "Умова Неймана (2-го роду)", size=13, bold=True, color=POS))
    frags.append(rect(x2 + 20, y0 + 60, box_w - 40, 45, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    frags.append(text(x2 + box_w / 2, y0 + 87, "∂φ/∂n|Γ = −Eₙ = σ / ε₀", size=13, bold=True, color=POS))
    frags.append(text(x2 + box_w / 2, y0 + 130, "Фіксована нормальна похідна", size=12, bold=True, color=INK))
    frags.append(text(x2 + box_w / 2, y0 + 155, "Задана густина заряду σ", size=12, color=MUTED))
    frags.append(text(x2 + box_w / 2, y0 + 175, "або ізольована межа", size=12, color=MUTED))
    frags.append(text(x2 + box_w / 2, y0 + 195, "(Eₙ = 0, ∂φ/∂n = 0).", size=12, color=MUTED))

    # 3. Робена
    x3 = 510
    frags.append(rect(x3, y0, box_w, box_h, fill="#e6f4ea", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(x3 + box_w / 2, y0 + 30, "Умова Робена (змішана)", size=13, bold=True, color=FIELD))
    frags.append(rect(x3 + 15, y0 + 60, box_w - 30, 45, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(x3 + box_w / 2, y0 + 87, "a·φ + b·(∂φ/∂n) = c", size=13, bold=True, color=FIELD))
    frags.append(text(x3 + box_w / 2, y0 + 130, "Лінійна комбінація", size=12, bold=True, color=INK))
    frags.append(text(x3 + box_w / 2, y0 + 155, "Межа розділу середовищ,", size=12, color=MUTED))
    frags.append(text(x3 + box_w / 2, y0 + 175, "тонкі діелектричні шари,", size=12, color=MUTED))
    frags.append(text(x3 + box_w / 2, y0 + 195, "конвективний теплообмін.", size=12, color=MUTED))

    render(os.path.join(IMG, "boundary-conditions.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_poisson_vs_laplace()
    fig_mean_value_property()
    fig_fdm_5point_stencil()
    fig_boundary_conditions()
    print("Фігури успішно згенеровано у ./img/")
