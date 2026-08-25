# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для теми «Межа Міньотта».
Створює діаграми:
1. img/modular-lifting-pipeline.svg — конвеєр факторизації многочленів у CAS через модулярну арифметику, лему Гензеля та межу Міньотта.
2. img/mahler-measure-roots.svg — геометрична інтерпретація міри Малера на комплексній площині та оцінка коренів дільника.
3. img/coefficient-bounds-growth.svg — порівняння оцінок коефіцієнтів дільників многочлена (Коші, Ландау, Міньотт, Бозамі).
"""

import os
import math
import sys

# Додаємо шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')

def ensure_out_dir():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

def fig_modular_lifting_pipeline():
    """
    Діаграма конвеєра комп'ютерної алгебри:
    f(x) in Z[x] -> mod p -> факторизація в F_p[x] -> підйом Гензеля mod p^k -> зупинка за межею Міньотта -> Z[x] дільники.
    """
    w, h = 860, 480
    frags = []

    # Підзаголовок
    frags.append(text(w / 2, 48, "Відновлення точних цілочисельних множників діленням f(x) mod pᵏ", size=13, color=MUTED))

    # Стовпчик 1: Вхідний многочлен f(x) у Z[x]
    box1_x, box1_y, box1_w, box1_h = 40, 80, 230, 110
    frags.append(rect(box1_x, box1_y, box1_w, box1_h, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(box1_x + box1_w/2, box1_y + 24, "Вхідний многочлен f(x) ∈ ℤ[x]", size=13, bold=True, color=NEG))
    frags.append(text(box1_x + box1_w/2, box1_y + 48, "f(x) = aₙ xⁿ + … + a₁ x + a₀", size=13))
    frags.append(text(box1_x + box1_w/2, box1_y + 70, "Обчислення евклідової норми ||f||₂", size=12, color=MUTED))
    frags.append(text(box1_x + box1_w/2, box1_y + 92, "та висоти багаточлена ||f||_∞", size=12, color=MUTED))

    # Стрілка вниз до вибору простого p
    frags.append(arrow(box1_x + box1_w/2, box1_y + box1_h, box1_x + box1_w/2, box1_y + box1_h + 35, color=LINE, sw=2))
    frags.append(text(box1_x + box1_w/2 + 8, box1_y + box1_h + 20, "редукція mod p", size=11, color=MUTED, anchor="start"))

    # Стовпчик 1 (низ): Модулярна факторизація
    box2_x, box2_y, box2_w, box2_h = 40, 225, 230, 110
    frags.append(rect(box2_x, box2_y, box2_w, box2_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(box2_x + box2_w/2, box2_y + 24, "Факторизація в 𝔽ₚ[x]", size=13, bold=True, color=FIELD))
    frags.append(text(box2_x + box2_w/2, box2_y + 48, "f(x) ≡ g₁(x) … gᵣ(x)  (mod p)", size=12))
    frags.append(text(box2_x + box2_w/2, box2_y + 70, "Алгоритм Берлекампа / Кантора", size=12, color=MUTED))
    frags.append(text(box2_x + box2_w/2, box2_y + 92, "Швидкий поліноміальний час", size=11, color=MUTED))

    # Стрілка праворуч до підйому Гензеля
    frags.append(arrow(box2_x + box2_w, box2_y + box2_h/2, box2_x + box2_w + 50, box2_y + box2_h/2, color=LINE, sw=2))
    frags.append(text(box2_x + box2_w + 25, box2_y + box2_h/2 - 10, "підйом", size=12, bold=True, color=LINE))

    # Стовпчик 2: Підйом Гензеля
    box3_x, box3_y, box3_w, box3_h = 320, 210, 230, 140
    frags.append(rect(box3_x, box3_y, box3_w, box3_h, fill="#fdf4ff", stroke="#9333ea", sw=2, rx=8))
    frags.append(text(box3_x + box3_w/2, box3_y + 24, "Підйом Гензеля mod pᵏ", size=13, bold=True, color="#9333ea"))
    frags.append(text(box3_x + box3_w/2, box3_y + 48, "f(x) ≡ g(x) · h(x)  (mod pᵏ)", size=12))
    frags.append(text(box3_x + box3_w/2, box3_y + 70, "Квадратична збіжність:", size=12, color=MUTED))
    frags.append(text(box3_x + box3_w/2, box3_y + 92, "p → p² → p⁴ → p⁸ → … → pᵏ", size=12, bold=True, color="#9333ea"))
    frags.append(text(box3_x + box3_w/2, box3_y + 118, "Подвоєння розрядів за крок", size=11, color=MUTED))

    # Блок межі Міньотта (вгорі посередині) - критерій зупинки!
    box4_x, box4_y, box4_w, box4_h = 320, 80, 230, 95
    frags.append(rect(box4_x, box4_y, box4_w, box4_h, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    frags.append(text(box4_x + box4_w/2, box4_y + 22, "Межа Міньотта B(f)", size=13, bold=True, color=POS))
    frags.append(text(box4_x + box4_w/2, box4_y + 44, "B(f) = (n-1 над k-1)·||f||₂ + (n-1 над k)·|aₙ|", size=11, bold=True))
    frags.append(text(box4_x + box4_w/2, box4_y + 66, "Гарантія: |bⱼ| ≤ B(f) для всіх j", size=12, color=MUTED))
    frags.append(text(box4_x + box4_w/2, box4_y + 84, "Критерій: pᵏ > 2 · |aₙ| · B(f)", size=12, bold=True, color=POS))

    # Стрілка керування від межі Міньотта до підйому Гензеля (умова зупинки)
    frags.append(line(box4_x + box4_w/2, box4_y + box4_h, box3_x + box3_w/2, box3_y, color=POS, sw=2, dash="4,4"))
    frags.append(text(box4_x + box4_w/2 + 8, box4_y + box4_h + 18, "поріг зупинки", size=11, bold=True, color=POS, anchor="start"))

    # Стрілка праворуч від Гензеля до відновлення коефіцієнтів
    frags.append(arrow(box3_x + box3_w, box3_y + box3_h/2, box3_x + box3_w + 50, box3_y + box3_h/2, color=LINE, sw=2))
    frags.append(text(box3_x + box3_w + 25, box3_y + box3_h/2 - 10, "pᵏ > 2B", size=11, bold=True, color=POS))

    # Стовпчик 3: Відновлення в Z[x]
    box5_x, box5_y, box5_w, box5_h = 600, 210, 220, 140
    frags.append(rect(box5_x, box5_y, box5_w, box5_h, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(box5_x + box5_w/2, box5_y + 24, "Симетричне відображення", size=13, bold=True, color=NEG))
    frags.append(text(box5_x + box5_w/2, box5_y + 48, "bⱼ ≡ cⱼ (mod pᵏ)", size=13))
    frags.append(text(box5_x + box5_w/2, box5_y + 70, "bⱼ ∈ [-pᵏ/2, pᵏ/2]", size=12, bold=True, color=LINE))
    frags.append(text(box5_x + box5_w/2, box5_y + 94, "Однозначне відновлення", size=12, color=MUTED))
    frags.append(text(box5_x + box5_w/2, box5_y + 118, "без модулярного шуму!", size=12, bold=True, color=FIELD))

    # Нижня панель: результат комбінації множників
    box6_x, box6_y, box6_w, box6_h = 160, 385, 540, 70
    frags.append(rect(box6_x, box6_y, box6_w, box6_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(box6_x + box6_w/2, box6_y + 24, "Результат: точний розклад на незвідні множники в ℤ[x]", size=13, bold=True, color=INK))
    frags.append(text(box6_x + box6_w/2, box6_y + 48, "f(x) = g(x) · h(x)  (без перебору нескінченних цілих чисел)", size=12, color=MUTED))

    target = os.path.join(OUT_DIR, "modular-lifting-pipeline.svg")
    render(target, w, h, *frags, title="Конвеєр модулярної факторизації та роль межі Міньотта")

def fig_mahler_measure_roots():
    """
    Геометрична ілюстрація міри Малера на комплексній площині.
    Одиничне коло |z| = 1. Корені alpha_i всередині кола (внесок 1) та ззовні кола (внесок |alpha_i|).
    """
    w, h = 800, 480
    frags = []

    # Підзаголовок
    frags.append(text(w / 2, 48, "Корені всередині одиничного круга дають множник 1, ззовні — свій радіус |αᵢ|", size=13, color=MUTED))

    cx, cy = 230, 255
    radius = 115

    # Координатна сітка
    frags.append(line(cx - 180, cy, cx + 180, cy, color="#94a3b8", sw=1.5))
    frags.append(line(cx, cy - 160, cx, cy + 160, color="#94a3b8", sw=1.5))
    frags.append(text(cx + 175, cy - 8, "Re(z)", size=12, color=MUTED, anchor="end"))
    frags.append(text(cx + 8, cy - 145, "Im(z)", size=12, color=MUTED, anchor="start"))

    # Одиничний круг (заливка)
    frags.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#f0fdf4" stroke="{FIELD}" stroke-width="2.5" stroke-dasharray="6,4"/>')
    frags.append(text(cx + radius - 15, cy + 18, "1.0", size=11, color=FIELD))
    frags.append(text(cx - radius + 15, cy + 18, "-1.0", size=11, color=FIELD, anchor="end"))
    frags.append(text(cx + 8, cy - radius + 15, "i", size=11, color=FIELD, anchor="start"))
    frags.append(text(cx + 8, cy + radius - 5, "-i", size=11, color=FIELD, anchor="start"))

    # Підпис одиничного кола
    frags.append(text(cx - 40, cy - radius - 10, "Одиничне коло |z| = 1", size=12, bold=True, color=FIELD))

    # Корені всередині одиничного кола
    in_roots = [
        (cx + 38, cy - 48, "α₁"),
        (cx - 58, cy - 38, "α₂"),
        (cx - 18, cy + 68, "α₃")
    ]
    for rx, ry, lbl in in_roots:
        frags.append(circle(rx, ry, 6, fill=NEG, stroke=BG, sw=1.5))
        frags.append(text(rx + 10, ry + 4, lbl, size=13, bold=True, color=NEG, anchor="start"))

    # Корені ззовні одиничного кола
    out_roots = [
        (cx + 125, cy - 75, "α₄"),
        (cx - 115, cy + 85, "α₅")
    ]
    for rx, ry, lbl in out_roots:
        # Радіус-вектор від центру
        frags.append(line(cx, cy, rx, ry, color=POS, sw=1.5, dash="3,3"))
        frags.append(circle(rx, ry, 6, fill=POS, stroke=BG, sw=1.5))
        frags.append(text(rx + 10, ry + 4, lbl, size=13, bold=True, color=POS, anchor="start"))

    # Права панель: Алгебраїчні висновки та властивості
    px, py, pw, ph = 460, 80, 310, 360
    frags.append(rect(px, py, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    frags.append(text(px + pw/2, py + 24, "Ключові властивості міри Малера", size=13, bold=True, color=INK))

    # Пункт 1: Мультиплікативність
    frags.append(text(px + 15, py + 55, "1. Мультиплікативність:", size=12, bold=True, color=NEG, anchor="start"))
    frags.append(text(px + 25, py + 75, "f(x) = g(x) · h(x)  ⇒", size=12, anchor="start"))
    frags.append(text(px + 25, py + 95, "M(f) = M(g) · M(h)", size=12, bold=True, color=NEG, anchor="start"))

    # Пункт 2: Нерівність для дільника
    frags.append(text(px + 15, py + 125, "2. Оцінка дільника g(x):", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(px + 25, py + 145, "Оскільки M(h) ≥ 1 для h ∈ ℤ[x],", size=12, color=MUTED, anchor="start"))
    frags.append(text(px + 25, py + 165, "M(g) ≤ M(f)", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(px + 25, py + 185, "Дільник не може мати більшу міру!", size=11, color=MUTED, anchor="start"))

    # Пункт 3: Нерівність Ландау
    frags.append(text(px + 15, py + 215, "3. Нерівність Ландау (1905):", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(px + 25, py + 235, "M(f) ≤ ||f||₂ = √(∑ |aᵢ|²)", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(px + 25, py + 255, "Міра коренів обмежена довжиною", size=11, color=MUTED, anchor="start"))
    frags.append(text(px + 25, py + 273, "вектора коефіцієнтів у ℂⁿ⁺¹!", size=11, color=MUTED, anchor="start"))

    # Пункт 4: Підсумок для коефіцієнтів
    frags.append(text(px + 15, py + 303, "4. Висновок для коефіцієнтів:", size=12, bold=True, color=INK, anchor="start"))
    frags.append(text(px + 25, py + 325, "|bⱼ| ≤ (deg g над j) · ||f||₂", size=12, bold=True, color=POS, anchor="start"))

    target = os.path.join(OUT_DIR, "mahler-measure-roots.svg")
    render(target, w, h, *frags, title="Геометричний зміст міри Малера M(f) = |aₙ| · ∏ max(1, |αᵢ|)")

def fig_coefficient_bounds_growth():
    """
    Графік порівняння зростання оцінок максимального коефіцієнта дільника:
    Наївна оцінка Коші 2^n ||f||_∞ vs Оцінка Гельфонда vs Межа Міньотта vs Межа Бозамі.
    """
    w, h = 820, 480
    frags = []

    # Підзаголовок
    frags.append(text(w / 2, 48, "Логарифмічна шкала log₂(B) для многочлена степеня n з нормою ||f||₂ = 100", size=13, color=MUTED))

    # Область графіка
    gx, gy, gw, gh = 90, 80, 450, 320

    # Сітка та осі
    frags.append(rect(gx, gy, gw, gh, fill="#fcfcfd", stroke="#cbd5e1", sw=1.5, rx=0))

    # Горизонтальні лінії (log2 B від 0 до 50)
    for val, y_pct in [(0, 1.0), (10, 0.8), (20, 0.6), (30, 0.4), (40, 0.2), (50, 0.0)]:
        y_pos = gy + y_pct * gh
        frags.append(line(gx, y_pos, gx + gw, y_pos, color="#e2e8f0", sw=1))
        frags.append(text(gx - 12, y_pos + 4, f"{val}", size=11, color=MUTED, anchor="end"))

    frags.append(text(gx - 40, gy + gh/2, "log₂(B) [біти модуля pᵏ]", size=12, bold=True, color=INK, anchor="middle"))

    # Вертикальні лінії (степінь многочлена n від 4 до 32)
    degrees = [4, 8, 12, 16, 20, 24, 28, 32]
    for d in degrees:
        x_pct = (d - 4) / 28.0
        x_pos = gx + x_pct * gw
        frags.append(line(x_pos, gy, x_pos, gy + gh, color="#e2e8f0", sw=1))
        frags.append(text(x_pos, gy + gh + 18, f"n={d}", size=11, color=MUTED, anchor="middle"))

    frags.append(text(gx + gw/2, gy + gh + 38, "Степінь вхідного многочлена n", size=12, bold=True, color=INK, anchor="middle"))

    def map_pt(d, log_val):
        x_pct = (d - 4) / 28.0
        y_pct = 1.0 - (log_val / 50.0)
        return (gx + x_pct * gw, gy + max(0, min(gh, y_pct * gh)))

    # 1. Гельфонд
    pts_gelfond = [map_pt(d, d * 1.4427 + 6.64) for d in degrees]
    path_gelfond = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_gelfond)
    frags.append(f'<path d="{path_gelfond}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # 2. Наївна бінарна (2^n)
    pts_naive = [map_pt(d, d + 6.64) for d in degrees]
    path_naive = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_naive)
    frags.append(f'<path d="{path_naive}" fill="none" stroke="#f97316" stroke-width="2" stroke-dasharray="5,4"/>')

    # 3. Межа Міньотта
    pts_mignotte = []
    for d in degrees:
        binom_val = math.comb(d, d // 2)
        log_val = math.log2(binom_val * 100.0)
        pts_mignotte.append(map_pt(d, log_val))
    path_mignotte = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_mignotte)
    frags.append(f'<path d="{path_mignotte}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    for px, py in pts_mignotte:
        frags.append(circle(px, py, 4, fill=NEG, stroke=BG, sw=1))

    # 4. Межа Бозамі (Beauzamy 1990)
    pts_beauzamy = []
    for d in degrees:
        log_val = (d / 2.0) + 6.64 - 0.5 * math.log2(max(1, d))
        pts_beauzamy.append(map_pt(d, log_val))
    path_beauzamy = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_beauzamy)
    frags.append(f'<path d="{path_beauzamy}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    for px, py in pts_beauzamy:
        frags.append(circle(px, py, 4, fill=FIELD, stroke=BG, sw=1))

    # Легенда праворуч
    lx, ly, lw, lh = 560, 80, 240, 320
    frags.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(lx + lw/2, ly + 24, "Порівняння методів", size=13, bold=True, color=INK))

    # 1. Гельфонд
    frags.append(line(lx + 15, ly + 55, lx + 45, ly + 55, color=POS, sw=2.5))
    frags.append(text(lx + 55, ly + 50, "Оцінка Гельфонда", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(lx + 55, ly + 65, "B ~ eⁿ · ||f||_∞  (найгрубша)", size=10, color=MUTED, anchor="start"))

    # 2. Наївна Коші
    frags.append(line(lx + 15, ly + 105, lx + 45, ly + 105, color="#f97316", sw=2, dash="5,4"))
    frags.append(text(lx + 55, ly + 100, "Наївна оцінка Коші", size=11, bold=True, color="#f97316", anchor="start"))
    frags.append(text(lx + 55, ly + 115, "B ~ 2ⁿ · ||f||_∞", size=10, color=MUTED, anchor="start"))

    # 3. Межа Міньотта
    frags.append(line(lx + 15, ly + 155, lx + 45, ly + 155, color=NEG, sw=3))
    frags.append(circle(lx + 30, ly + 155, 3, fill=NEG, stroke=BG, sw=1))
    frags.append(text(lx + 55, ly + 150, "Межа Міньотта (1974)", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(text(lx + 55, ly + 165, "B = (n над n/2) · ||f||₂", size=10, color=MUTED, anchor="start"))
    frags.append(text(lx + 55, ly + 180, "Економія до 40% бітів!", size=10, bold=True, color=NEG, anchor="start"))

    # 4. Бозамі
    frags.append(line(lx + 15, ly + 225, lx + 45, ly + 225, color=FIELD, sw=2.5))
    frags.append(circle(lx + 30, ly + 225, 3, fill=FIELD, stroke=BG, sw=1))
    frags.append(text(lx + 55, ly + 220, "Межа Бозамі (1990)", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(lx + 55, ly + 235, "B ~ 2ⁿ/² · [f]₂  (норма Бомб'єрі)", size=10, color=MUTED, anchor="start"))
    frags.append(text(lx + 55, ly + 250, "Асимптотично найщільніша", size=10, color=MUTED, anchor="start"))

    # Примітка внизу легенди
    frags.append(text(lx + lw/2, ly + 295, "Менший log₂(B) ⇒ менше підйомів", size=10, bold=True, color=LINE))

    target = os.path.join(OUT_DIR, "coefficient-bounds-growth.svg")
    render(target, w, h, *frags, title="Порівняння оцінок верхньої межі коефіцієнтів дільника B(f)")

def main():
    ensure_out_dir()
    fig_modular_lifting_pipeline()
    fig_mahler_measure_roots()
    fig_coefficient_bounds_growth()
    print("All figures generated successfully.")

if __name__ == '__main__':
    main()
