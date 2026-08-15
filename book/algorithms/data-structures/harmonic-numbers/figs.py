# -*- coding: utf-8 -*-
"""Фігури до статті «Гармонічні числа».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Розкладка — із запасом, підписи рознесено.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_integral_bounds():
    """Фігура 1: Інтегральна оцінка гармонічного ряду через криву 1/x."""
    W, H = 840, 520
    parts = []

    parts.append(text(W / 2, 36, "Інтегральна оцінка H[n] та стала Ейлера — Маскероні γ", size=17, bold=True))

    L, R = 90, 780
    T, B = 80, 430

    xmax = 6.2
    ymax = 1.25

    def X(x):
        return L + (x / xmax) * (R - L)

    def Y(y):
        return B - (y / ymax) * (B - T)

    # 1. Зафарбування площі під ступенями H[n] (верхня сума)
    for k in range(1, 6):
        x_left = X(k)
        x_right = X(k + 1)
        w_rect = x_right - x_left
        h_val = 1.0 / k
        y_top = Y(h_val)
        h_rect = B - y_top
        parts.append(rect(x_left, y_top, w_rect, h_rect, fill="#e8f0fe", stroke="none"))

    # 2. Площа під кривою 1/x (інтеграл від 1 до 6)
    pts_curve_area = [(X(1.0), B)]
    x_val = 1.0
    while x_val <= 6.0001:
        pts_curve_area.append((X(x_val), Y(1.0 / x_val)))
        x_val += 0.05
    pts_curve_area.append((X(6.0), B))
    d_area = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_curve_area)
    parts.append(f'<polygon points="{d_area}" fill="#d2e3fc" opacity="0.65" stroke="none"/>')

    # 3. Осі координат
    parts.append(line(L, T, L, B, color=INK, sw=1.8))
    parts.append(line(L, B, R + 10, B, color=INK, sw=1.8))
    parts.append(text((L + R) / 2, B + 46, "значення k (змінна підсумовування)", size=13.5))
    parts.append(text(L - 55, (T + B) / 2, "1/k", size=13.5, color=INK, bold=True))

    # Позначки на осі X (k = 1..6)
    for k in range(1, 7):
        xk = X(k)
        parts.append(line(xk, B, xk, B + 6, color=INK, sw=1.4))
        parts.append(text(xk, B + 24, str(k), size=12.5, color=MUTED))

    # Позначки на осі Y (1/1, 1/2, 1/3, 1/4)
    y_ticks = [(1.0, "1"), (0.5, "1/2"), (1.0 / 3.0, "1/3"), (0.25, "1/4")]
    for yv, ylab in y_ticks:
        yk = Y(yv)
        parts.append(line(L - 6, yk, L, yk, color=INK, sw=1.4))
        parts.append(text(L - 14, yk + 4, ylab, size=12, color=MUTED, anchor="end"))

    # 4. Контури верхніх прямокутників (H[n])
    for k in range(1, 6):
        xl = X(k)
        xr = X(k + 1)
        y_top = Y(1.0 / k)
        parts.append(line(xl, y_top, xr, y_top, color=NEG, sw=1.8))
        parts.append(line(xr, y_top, xr, B, color=NEG, sw=1.2, dash="3,3"))

    # 5. Сама крива y = 1/x
    pts_curve = []
    x_val = 0.85
    while x_val <= 6.15:
        pts_curve.append((X(x_val), Y(1.0 / x_val)))
        x_val += 0.02
    d_curve = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_curve)
    parts.append(f'<polyline points="{d_curve}" fill="none" stroke="{POS}" stroke-width="2.6"/>')

    # 6. Пояснювальні написи та легенда
    lx, ly = R - 320, T + 10
    parts.append(rect(lx - 10, ly - 10, 320, 110, fill=FILL, stroke=MUTED, sw=1.0, rx=4))
    
    parts.append(rect(lx, ly + 4, 24, 14, fill="#e8f0fe", stroke=NEG, sw=1.4))
    parts.append(text(lx + 34, ly + 16, "Сходинки H[n] = ∑ 1/k  (верхня сума)", size=12.5, anchor="start"))

    parts.append(line(lx, ly + 38, lx + 24, ly + 38, color=POS, sw=2.6))
    parts.append(text(lx + 34, ly + 42, "Крива f(x) = 1/x  (інтеграл ln n)", size=12.5, anchor="start"))

    parts.append(rect(lx, ly + 60, 24, 14, fill="#d2e3fc", stroke="none"))
    parts.append(text(lx + 34, ly + 72, "Залишковий клиновий зазорок  γ ≈ 0.5772", size=12, color=NEG, anchor="start", bold=True))

    x_gap = X(1.5)
    y_gap_top = Y(1.0)
    y_gap_bot = Y(1.0 / 1.5)
    y_gap_mid = (y_gap_top + y_gap_bot) / 2
    parts.append(arrow(x_gap + 50, y_gap_mid - 20, x_gap + 8, y_gap_mid, color=NEG, sw=1.5))
    parts.append(text(x_gap + 58, y_gap_mid - 24, "Різниця між сходинкою й кривою", size=11.5, color=NEG, anchor="start"))

    render(os.path.join(IMG, "integral-bounds.svg"), W, H, *parts)


def fig_algorithm_applications():
    """Фігура 2: Застосування гармонічних чисел в алгоритмах та структурах даних."""
    W, H = 880, 520
    parts = []

    parts.append(text(W / 2, 34, "Гармонічні числа H[N] у фундаментальних алгоритмах", size=17, bold=True))

    card_w, card_h = 390, 190
    cards = [
        (45, 75, "1. Швидке сортування (QuickSort)",
         "C(N) = 2(N+1) H[N] - 4N",
         "Середня кількість порівнянь елементів",
         "Очікувана складність:  2 N ln N + O(N)",
         "#eaf0fd", NEG),

        (475, 75, "2. Випадкові дерева пошуку (BST)",
         "E[D] = 2 H[N] - 3",
         "Середня глибина випадкового вузла",
         "Середня глибина вузла:  2 ln N - 1.85",
         "#eafaf0", POS),

        (45, 290, "3. Хеш-таблиці та Coupon Collector",
         "E[T] = N H[N]",
         "Очікувана кількість спроб до повного покриття",
         "Складність покриття:  N ln N + γ N + 1/2",
         "#fdf6ea", "#b56500"),

        (475, 290, "4. Пропускні списки та випадковий максимум",
         "E[M] = H[N]",
         "Кількість оновлень максимуму в перестановці",
         "Середня кількість рівнів у Skip List:  log2 N",
         "#efeaf2", "#5e2ca5")
    ]

    for cx, cy, title, formula, desc, note, bg_col, border_col in cards:
        parts.append(rect(cx, cy, card_w, card_h, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        parts.append(text(cx + 20, cy + 30, title, size=15, bold=True, anchor="start", color=INK))
        
        fx, fy, fw, fh = cx + 20, cy + 48, card_w - 40, 42
        parts.append(rect(fx, fy, fw, fh, fill=FILL, stroke=border_col, sw=1.2, rx=5))
        parts.append(text(fx + fw / 2, fy + 26, formula, size=16, bold=True, color=border_col))
        
        parts.append(text(cx + 20, cy + 114, desc, size=12.5, color=INK, anchor="start"))
        parts.append(text(cx + 20, cy + 144, note, size=12.5, color=MUTED, anchor="start"))

    parts.append(rect(45, 492, 790, 20, fill="none", stroke="none"))
    parts.append(text(W / 2, 500, "Усі ці результати випливають з асимптотики: H[N] = ln N + γ + O(1/N)", size=13, color=MUTED, bold=True))

    render(os.path.join(IMG, "algorithm-applications.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_integral_bounds()
    fig_algorithm_applications()
    print("OK: 2 SVG у", IMG)
