# -*- coding: utf-8 -*-
"""Фігури для статті «Гауссові цілі числа ℤ[i]».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL  = "#eafaf1"
RED_FILL    = "#fdecea"
BLUE_FILL   = "#eaf0fd"
GRAY_FILL   = "#eceff1"
ORANGE      = "#e67e22"
ORANGE_FILL = "#fdf1e5"
GREEN_HEAD  = "#b7e6cd"
YELLOW_FILL = "#fef9e7"


# ─────────────────────────────────────────────────────────────────────────
# Фігура 1 — Решітка ℤ[i] на комплексній площині: одиниці та асоційовані
# ─────────────────────────────────────────────────────────────────────────
def fig_gaussian_lattice():
    W, H = 840, 560
    p = []
    p.append(text(W/2, 28, "Решітка Гауссових цілих чисел ℤ[i] та група одиниць", size=18, bold=True))

    cx, cy = 290, 290
    scale = 65

    # Сітка ліній
    for i in range(-3, 4):
        x = cx + i * scale
        y = cy + i * scale
        p.append(line(cx - 3.4 * scale, y, cx + 3.4 * scale, y, color="#e0e0e0", sw=1))
        p.append(line(x, cy - 3.4 * scale, x, cy + 3.4 * scale, color="#e0e0e0", sw=1))

    # Головні осі
    p.append(line(cx - 3.5 * scale, cy, cx + 3.6 * scale, cy, color=LINE, sw=1.8))
    p.append(line(cx, cy + 3.5 * scale, cx, cy - 3.6 * scale, color=LINE, sw=1.8))
    p.append(text(cx + 3.6 * scale + 16, cy + 5, "Re", size=14, bold=True, color=INK))
    p.append(text(cx, cy - 3.6 * scale - 12, "Im", size=14, bold=True, color=INK))

    # Одиничне коло N(z) = 1
    p.append(circle(cx, cy, scale, fill="none", stroke=POS, sw=1.6))

    # Вузли решітки
    for a in range(-3, 4):
        for b in range(-3, 4):
            x = cx + a * scale
            y = cy - b * scale
            p.append(circle(x, y, 3, fill="#888888", stroke="#888888", sw=0))

    # Чотири оборотні одиниці (група одиниць {1, i, -1, -i})
    units = [
        (1, 0, "1", 18, 16),
        (0, 1, "i", 14, -10),
        (-1, 0, "-1", -20, 16),
        (0, -1, "-i", 16, 16)
    ]
    for a, b, lbl, dx, dy in units:
        x = cx + a * scale
        y = cy - b * scale
        p.append(circle(x, y, 6, fill=POS, stroke=BG, sw=1.5))
        p.append(text(x + dx, y + dy, lbl, size=15, bold=True, color=POS))

    # Приклад елемента α = 2 + i та його чотирьох асоційованих
    assoc = [
        (2, 1, "α = 2 + i", 36, -8, POS),
        (-1, 2, "iα = -1 + 2i", -44, -12, NEG),
        (-2, -1, "-α = -2 - i", -44, 18, MUTED),
        (1, -2, "-iα = 1 - 2i", 40, 18, FIELD)
    ]
    # Коло радіуса √5
    r_sqrt5 = scale * math.sqrt(5)
    p.append(circle(cx, cy, r_sqrt5, fill="none", stroke=FIELD, sw=1.2))

    for a, b, lbl, dx, dy, col in assoc:
        x = cx + a * scale
        y = cy - b * scale
        p.append(line(cx, cy, x, y, color=col, sw=1.5))
        p.append(circle(x, y, 5.5, fill=col, stroke=BG, sw=1.5))
        p.append(text(x + dx, y + dy, lbl, size=13, bold=True, color=col))

    # Права панель із поясненнями
    px = 560
    p.append(fitbox(px, 70, 250, 120,
                    "Група одиниць ℤ[i]×:\n"
                    "• N(u) = a² + b² = 1\n"
                    "• u ∈ {1, i, -1, -i}\n"
                    "• Повороти площини на 90°",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.5))

    p.append(fitbox(px, 205, 250, 145,
                    "Асоційовані елементи:\n"
                    "• α, iα, -α, -iα\n"
                    "• Мають однакову норму:\n"
                    "  N(α) = 2² + 1² = 5\n"
                    "• Лежать на одному колі r = √5",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(fitbox(px, 365, 250, 155,
                    "Властивості норми:\n"
                    "• N(a + bi) = a² + b²\n"
                    "• N(α·β) = N(α)·N(β)\n"
                    "• N(α) = 0 ⇔ α = 0\n"
                    "• N(α) = 1 ⇔ α — одиниця",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    render(os.path.join(IMG, "gaussian-grid-lattice.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 2 — Геометрія ділення з остачею: диск радіуса 1/√2 < 1
# ─────────────────────────────────────────────────────────────────────────
def fig_euclidean_division():
    W, H = 840, 520
    p = []
    p.append(text(W/2, 28, "Геометричне обґрунтування ділення з остачею в ℤ[i]", size=18, bold=True))

    cx, cy = 260, 270
    scale = 210

    # Квадрат решітки 1x1
    x0, y0 = cx - scale/2, cy + scale/2
    x1, y1 = cx + scale/2, cy - scale/2

    # Заливка квадрата
    p.append(rect(x0, y1, scale, scale, fill="#fcfcfc", stroke="#cccccc", sw=1.5))

    # Вершини квадрата (цілі точки q)
    vertices = [
        (x0, y0, "q₀"),
        (x1, y0, "q₀ + 1"),
        (x0, y1, "q₀ + i"),
        (x1, y1, "q₀ + 1 + i")
    ]

    # Круг радіуса 1 (показує критичну межу норми)
    p.append(circle(x0, y1, scale, fill="none", stroke="#dddddd", sw=1.2))

    # Диск радіуса 1/√2 навколо лівої верхньої вершини (найближчої до вибраної точки)
    r_max = scale / math.sqrt(2)
    p.append(circle(x0, y1, r_max, fill="#e8f8f5", stroke=FIELD, sw=1.8))

    # Точка частки у полі комплексних чисел z = α / β
    zx = x0 + 0.35 * scale
    zy = y1 + 0.30 * scale
    p.append(line(x0, y1, zx, zy, color=POS, sw=2))
    p.append(circle(zx, zy, 5.5, fill=POS, stroke=BG, sw=1.5))
    p.append(text(zx + 40, zy + 6, "z = α / β", size=14, bold=True, color=POS))

    # Підпис довжини відрізка
    p.append(text((x0 + zx)/2 - 30, (y1 + zy)/2 - 14, "|z - q| ≤ 1/√2", size=12.5, bold=True, color=POS))

    # Центр квадрата
    p.append(circle(cx, cy, 4, fill=MUTED, stroke=MUTED, sw=0))
    p.append(text(cx + 8, cy + 24, "центр (d = 1/√2)", size=12, color=MUTED, italic=True))

    # Вершини
    for vx, vy, lbl in vertices:
        is_closest = (vx == x0 and vy == y1)
        col = FIELD if is_closest else INK
        p.append(circle(vx, vy, 6 if is_closest else 4.5, fill=col, stroke=BG, sw=1.5))
        dx = -28 if vx == x0 else 32
        dy = 22 if vy == y0 else -18
        p.append(text(vx + dx, vy + dy, lbl, size=14, bold=True, color=col))

    # Пояснення праворуч
    px = 530
    p.append(fitbox(px, 65, 285, 125,
                    "Алгоритм округлення:\n"
                    "1. Обчислюємо z = α / β у ℂ\n"
                    "   z = x + yi (дійсні x, y)\n"
                    "2. Округлюємо до найближчих цілих:\n"
                    "   q = ⌊x + ½⌋ + ⌊y + ½⌋·i ∈ ℤ[i]",
                    size=13, fill=FILL, stroke=LINE, sw=1.5))

    p.append(fitbox(px, 205, 285, 145,
                    "Оцінка відстані:\n"
                    "• |x - Re(q)| ≤ ½\n"
                    "• |y - Im(q)| ≤ ½\n"
                    "• |z - q|² ≤ (½)² + (½)² = ½\n"
                    "• |z - q| ≤ 1/√2 ≈ 0.707 < 1",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(fitbox(px, 365, 285, 130,
                    "Остача r = α - q·β:\n"
                    "• N(r) = N(β) · |z - q|²\n"
                    "• N(r) ≤ ½ · N(β) < N(β)\n"
                    "⇒ Кільце ℤ[i] є евклідовим!",
                    size=13, fill=YELLOW_FILL, stroke=ORANGE, sw=1.5))

    render(os.path.join(IMG, "euclidean-division-circle.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 3 — Прості числа Гаусса на комплексній площині
# ─────────────────────────────────────────────────────────────────────────
def fig_gaussian_primes_plane():
    W, H = 840, 580
    p = []
    p.append(text(W/2, 28, "Розподіл простих чисел Гаусса на площині", size=18, bold=True))

    cx, cy = 290, 305
    scale = 46

    # Сітка
    for i in range(-5, 6):
        x = cx + i * scale
        y = cy + i * scale
        p.append(line(cx - 5.4 * scale, y, cx + 5.4 * scale, y, color="#ebebeb", sw=1))
        p.append(line(x, cy - 5.4 * scale, x, cy + 5.4 * scale, color="#ebebeb", sw=1))

    # Осі
    p.append(line(cx - 5.5 * scale, cy, cx + 5.6 * scale, cy, color=LINE, sw=1.8))
    p.append(line(cx, cy + 5.5 * scale, cx, cy - 5.6 * scale, color=LINE, sw=1.8))
    p.append(text(cx + 5.6 * scale + 15, cy + 5, "Re", size=14, bold=True, color=INK))
    p.append(text(cx, cy - 5.6 * scale - 10, "Im", size=14, bold=True, color=INK))

    # Перевірка простоти в Z[i]
    def is_prime_zi(a, b):
        if a == 0 and b == 0: return False
        norm = a*a + b*b
        if norm == 1: return False
        if a == 0: return (abs(b) % 4 == 3) and is_rational_prime(abs(b))
        if b == 0: return (abs(a) % 4 == 3) and is_rational_prime(abs(a))
        return is_rational_prime(norm)

    def is_rational_prime(n):
        if n < 2: return False
        for d in range(2, int(math.isqrt(n)) + 1):
            if n % d == 0: return False
        return True

    # Малювання точок
    for a in range(-5, 6):
        for b in range(-5, 6):
            if a == 0 and b == 0: continue
            x = cx + a * scale
            y = cy - b * scale
            norm = a*a + b*b

            if is_prime_zi(a, b):
                if norm == 2:
                    # Розгалужене (1+i)
                    p.append(circle(x, y, 6, fill=POS, stroke=BG, sw=1.2))
                elif a == 0 or b == 0:
                    # Інертне (на осях, p = 3)
                    p.append(circle(x, y, 6, fill=NEG, stroke=BG, sw=1.2))
                else:
                    # Розщеплене (p ≡ 1 mod 4: 2+i, 3+2i, 4+i...)
                    p.append(circle(x, y, 5.5, fill=FIELD, stroke=BG, sw=1.2))
            else:
                p.append(circle(x, y, 2.5, fill="#b0b0b0", stroke="#b0b0b0", sw=0))

    # Підписи ключових простих чисел
    p.append(text(cx + 1*scale + 16, cy - 1*scale - 8, "1+i", size=12, bold=True, color=POS))
    p.append(text(cx + 2*scale + 20, cy - 1*scale - 8, "2+i", size=12, bold=True, color=FIELD))
    p.append(text(cx + 1*scale + 20, cy - 2*scale - 8, "1+2i", size=12, bold=True, color=FIELD))
    p.append(text(cx + 3*scale + 14, cy + 18, "3", size=13, bold=True, color=NEG))
    p.append(text(cx + 16, cy - 3*scale - 8, "3i", size=13, bold=True, color=NEG))

    # Права панель легенди
    px = 565
    p.append(fitbox(px, 70, 255, 130,
                    "Розгалужене просте (N=2):\n"
                    "• 1 + i та його 3 асоційовані\n"
                    "• 2 = -i·(1 + i)²\n"
                    "• Єдине парне просте число",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.5))

    p.append(fitbox(px, 215, 255, 145,
                    "Розщеплені прості (p ≡ 1 mod 4):\n"
                    "• p = a² + b² = (a+bi)(a-bi)\n"
                    "• Приклади: 5 = (2+i)(2-i)\n"
                    "  13 = (3+2i)(3-2i), 17, 29, 41\n"
                    "• 8 точок симетрії для кожного p",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    p.append(fitbox(px, 375, 255, 140,
                    "Інертні прості (p ≡ 3 mod 4):\n"
                    "• Не розкладаються в ℤ[i]\n"
                    "• Лежать строго на осях Re та Im\n"
                    "• Приклади: 3, 7, 11, 19, 23, 31\n"
                    "• Норма в ℤ[i] дорівнює p²",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.5))

    render(os.path.join(IMG, "gaussian-primes-plane.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 4 — Три випадки розкладу простих чисел: класифікаційна схема
# ─────────────────────────────────────────────────────────────────────────
def fig_prime_splitting_cases():
    W, H = 840, 430
    p = []
    p.append(text(W/2, 28, "Класифікація простих чисел у кільці ℤ[i]", size=18, bold=True))

    bw = 240
    bh = 330
    gap = 25
    x_start = 35
    top = 65

    # 1. Розгалуження
    bx1 = x_start
    p.append(rect(bx1, top, bw, bh, fill=RED_FILL, stroke=POS, sw=2, rx=8))
    p.append(text(bx1 + bw/2, top + 26, "РОЗГАЛУЖЕННЯ", size=15, bold=True, color=POS))
    p.append(text(bx1 + bw/2, top + 48, "p = 2", size=14, bold=True, color=INK))
    p.append(line(bx1 + 15, top + 60, bx1 + bw - 15, top + 60, color=POS, sw=1))

    t1 = ("• Розклад на множники:\n"
          "  2 = -i · (1 + i)²\n\n"
          "• Дільник подвійної кратності:\n"
          "  1 + i та 1 - i асоційовані\n"
          "  1 - i = -i·(1 + i)\n\n"
          "• Норма дільника:\n"
          "  N(1 + i) = 1² + 1² = 2\n\n"
          "• Дискримінант ділиться на 2")
    p.append(mtext(bx1 + 15, top + 80, t1, size=12.5, color=INK, anchor="start", lh=1.3))

    # 2. Розщеплення
    bx2 = bx1 + bw + gap
    p.append(rect(bx2, top, bw, bh, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=8))
    p.append(text(bx2 + bw/2, top + 26, "РОЗЩЕПЛЕННЯ", size=15, bold=True, color=FIELD))
    p.append(text(bx2 + bw/2, top + 48, "p ≡ 1 (mod 4)", size=14, bold=True, color=INK))
    p.append(line(bx2 + 15, top + 60, bx2 + bw - 15, top + 60, color=FIELD, sw=1))

    t2 = ("• Розклад на два прості:\n"
          "  p = (a + bi)(a - bi)\n\n"
          "• Сума двох квадратів:\n"
          "  p = a² + b² (теорема Ферма)\n\n"
          "• Множники неасоційовані:\n"
          "  π = a + bi,  π̄ = a - bi\n"
          "  N(π) = N(π̄) = p\n\n"
          "• Приклади: 5, 13, 17, 29, 37, 41")
    p.append(mtext(bx2 + 15, top + 80, t2, size=12.5, color=INK, anchor="start", lh=1.3))

    # 3. Інерція
    bx3 = bx2 + bw + gap
    p.append(rect(bx3, top, bw, bh, fill=BLUE_FILL, stroke=NEG, sw=2, rx=8))
    p.append(text(bx3 + bw/2, top + 26, "ІНЕРЦІЯ", size=15, bold=True, color=NEG))
    p.append(text(bx3 + bw/2, top + 48, "p ≡ 3 (mod 4)", size=14, bold=True, color=INK))
    p.append(line(bx3 + 15, top + 60, bx3 + bw - 15, top + 60, color=NEG, sw=1))

    t3 = ("• Залишається простим:\n"
          "  p не ділиться в ℤ[i]\n\n"
          "• Не є сумою двох квадратів:\n"
          "  a² + b² ≢ 3 (mod 4)\n\n"
          "• Норма як елемента ℤ[i]:\n"
          "  N(p) = p² + 0² = p²\n\n"
          "• Приклади: 3, 7, 11, 19, 23, 31")
    p.append(mtext(bx3 + 15, top + 80, t3, size=12.5, color=INK, anchor="start", lh=1.3))

    render(os.path.join(IMG, "prime-splitting-cases.svg"), W, H, *p)


if __name__ == "__main__":
    fig_gaussian_lattice()
    fig_euclidean_division()
    fig_gaussian_primes_plane()
    fig_prime_splitting_cases()
    print("All figures generated successfully.")
