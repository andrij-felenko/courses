# -*- coding: utf-8 -*-
"""Фігури до статті «Суми Гаусса»."""
import sys, os, math

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_vector_sum():
    """Фігура 1: Послідовне додавання векторів квадратичної суми Гаусса g(1, 7) = i*sqrt(7)."""
    w, h = 640, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Векторна сума Гаусса для p = 7: g(1, 7) = i√7", size=17, bold=True))
    frags.append(text(w / 2, 48, "Додавання експонент e^(2πi·n²/7) в комплексній площині", size=13, color=MUTED, italic=True))

    # Координатна сітка
    cx, cy = 230, 410
    scale = 82.0  # пікселів на одиницю

    # Осі координат
    frags.append(line(40, cy, 410, cy, color="#d0d7de", sw=1.2))
    frags.append(line(cx, 470, cx, 60, color="#d0d7de", sw=1.2))
    frags.append(arrow(cx, cy, 415, cy, color=MUTED, sw=1.5))
    frags.append(arrow(cx, cy, cx, 55, color=MUTED, sw=1.5))
    frags.append(text(425, cy + 4, "Re", size=13, color=MUTED, bold=True))
    frags.append(text(cx, 45, "Im", size=13, color=MUTED, bold=True))

    # Засічки на осях
    for r in [-2, -1, 1, 2]:
        rx = cx + r * scale
        if 40 <= rx <= 410:
            frags.append(line(rx, cy - 4, rx, cy + 4, color=MUTED, sw=1))
            frags.append(text(rx, cy + 18, "%d" % r, size=11, color=MUTED))
    for im_val in [1, 2, 3]:
        ry = cy - im_val * scale
        if 60 <= ry <= 470:
            frags.append(line(cx - 4, ry, cx + 4, ry, color=MUTED, sw=1))
            frags.append(text(cx - 16, ry + 4, "%di" % im_val, size=11, color=MUTED))

    # Обчислення ланцюжка векторів для p = 7
    p = 7
    n_sq_mod = [(n * n) % p for n in range(p)]
    
    curr_x, curr_y = 0.0, 0.0
    colors = ["#2457d6", "#c0392b", "#d97706", "#27ae60", "#8e44ad", "#16a085", "#e67e22"]

    for n in range(p):
        k = n_sq_mod[n]
        angle = 2.0 * math.pi * k / p
        dx = math.cos(angle)
        dy = math.sin(angle)
        next_x = curr_x + dx
        next_y = curr_y + dy

        px1, py1 = cx + curr_x * scale, cy - curr_y * scale
        px2, py2 = cx + next_x * scale, cy - next_y * scale

        # Малюємо вектор
        frags.append(arrow(px1, py1, px2, py2, color=colors[n], sw=2.2))
        frags.append(circle(px2, py2, 3.5, fill=colors[n], stroke="#ffffff", sw=1))

        curr_x, curr_y = next_x, next_y

    # Підсумковий вектор результуючої суми g(1, 7) = (0, sqrt(7))
    res_px, res_py = cx + curr_x * scale, cy - curr_y * scale
    frags.append(line(cx, cy, res_px, res_py, color=FIELD, sw=3.5, dash="6,4"))
    frags.append(circle(res_px, res_py, 6, fill=FIELD, stroke="#ffffff", sw=1.5))

    # Легенда кроків (праворуч)
    leg_x = 425
    frags.append(rect(leg_x, 80, 200, 220, fill="#f8fafc", stroke="#cbd5e1", rx=8, sw=1.2))
    frags.append(text(leg_x + 100, 100, "Кроки додавання:", size=13, bold=True))

    for n in range(p):
        k = n_sq_mod[n]
        y_pos = 124 + n * 24
        frags.append(circle(leg_x + 18, y_pos - 4, 5, fill=colors[n], stroke="none"))
        frags.append(text(leg_x + 30, y_pos, "n=%d: n²≡%d → e^(2πi·%d/7)" % (n, k, k),
                         size=11, color=INK, anchor="start"))

    # Підсумковий бокс
    frags.append(rect(leg_x, 315, 200, 140, fill="#e8f5e9", stroke=FIELD, rx=8, sw=1.5))
    frags.append(text(leg_x + 100, 338, "Результат суми:", size=13, color=FIELD, bold=True))
    frags.append(text(leg_x + 100, 362, "g(1, 7) = i·√7", size=15, color=INK, bold=True))
    frags.append(text(leg_x + 100, 385, "≈ +2.64575 i", size=13, color=INK))
    frags.append(text(leg_x + 100, 410, "|g(1, 7)| = √7 ≈ 2.65", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'vector-sum.svg'), w, h, *frags)


def fig_fourier_bridge():
    """Фігура 2: Сума Гаусса як перетворення Фур'є між множильною та додавальною структурою."""
    w, h = 640, 310
    frags = []

    frags.append(text(w / 2, 28, "Сума Гаусса як місток між двома арифметичними світами", size=17, bold=True))

    # Ліва рамка: Множильна група
    box_l = fitbox(20, 75, 185, 110, "Мультиплікативна група\n𝔽ₚ* = {1, 2, ..., p-1}\n\nХарактер χ(a)\n(символ Лежандра)",
                   size=13, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8)
    frags.append(box_l)

    # Права рамка: Додавальна група
    box_r = fitbox(435, 75, 185, 110, "Адитивна група\n(𝔽ₚ, +) = {0, 1, ..., p-1}\n\nАддитивний характер\nψ(a) = e^(2πi·a/p)",
                   size=13, fill="#fff7ed", stroke=POS, sw=1.8, rx=8)
    frags.append(box_r)

    # Центральна стрілка та рамка перетворення Фур'є
    frags.append(arrow(210, 130, 430, 130, color=FIELD, sw=2.5))
    frags.append(arrow(430, 130, 210, 130, color=FIELD, sw=2.5))

    box_c = fitbox(220, 85, 200, 90, "Дискретне перетворення Фур'є\n\ng(χ) = ∑ χ(a) · e^(2πi·a / p)",
                   size=12, fill="#e8f5e9", stroke=FIELD, sw=2.0, rx=8, bold=True)
    frags.append(box_c)

    # Нижній висновок про модуль
    box_b = fitbox(30, 215, 580, 65, "Унітарність і симетрія: |g(χ)|² = p для будь-якого нетривіального характеру\nПеретворення зберігає норму (аналог рівності Парсеваля)",
                   size=13, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8)
    frags.append(box_b)

    render(os.path.join(OUT, 'fourier-bridge.svg'), w, h, *frags)


def fig_constructive_destructive():
    """Фігура 3: Звичайна сума експонент (згасання) проти зваженої суми Гаусса (підсилення)."""
    w, h = 640, 360
    frags = []

    frags.append(text(w / 2, 28, "Деструктивна інтерференція vs Підсилення сум Гаусса", size=17, bold=True))

    # Верхній блок: Звичайна сума без ваг (згасає до -1)
    y1 = 120
    frags.append(rect(30, y1 - 45, 580, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(160, y1 - 20, "1. Звичайна сума експонент (без ваг):", size=13, color=POS, bold=True))
    frags.append(text(160, y1 + 10, "∑_{a=1}^{p-1} e^(2πi·a/p) = -1", size=15, color=INK, bold=True))
    
    frags.append(text(440, y1 - 15, "Рівномірний розподіл по колу:", size=12, color=MUTED))
    frags.append(text(440, y1 + 8, "усі вектори взаємно знищуються,", size=12, color=MUTED))
    frags.append(text(440, y1 + 26, "лишаючи лише -1 (без n=0).", size=12, color=MUTED))

    # Нижній блок: Зважена сума Гаусса (підсилюється до sqrt(p))
    y2 = 260
    frags.append(rect(30, y2 - 45, 580, 105, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(160, y2 - 20, "2. Зважена сума Гаусса (з характером χ):", size=13, color=FIELD, bold=True))
    frags.append(text(160, y2 + 10, "g(χ) = ∑_{a=1}^{p-1} χ(a) · e^(2πi·a/p)", size=15, color=INK, bold=True))
    frags.append(text(160, y2 + 34, "Модуль: |g(χ)| = √p", size=14, color=FIELD, bold=True))

    frags.append(text(440, y2 - 15, "Характер χ(a) = ±1 перевертає", size=12, color=MUTED))
    frags.append(text(440, y2 + 5, "фази нелишків, перетворюючи", size=12, color=MUTED))
    frags.append(text(440, y2 + 25, "гасіння на конструктивну спіраль!", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'constructive-destructive.svg'), w, h, *frags)


def fig_mod4_sign_pattern():
    """Фігура 4: Чотириоперіодичний паттерн знаку квадратичної суми Гаусса g(1, p)."""
    w, h = 640, 420
    frags = []

    frags.append(text(w / 2, 28, "Закон знаку Гаусса: залежність g(1, p) від p mod 4", size=17, bold=True))

    cx, cy = 320, 220

    # Координатні осі
    frags.append(line(60, cy, 580, cy, color="#cbd5e1", sw=1.5))
    frags.append(line(cx, 55, cx, 370, color="#cbd5e1", sw=1.5))
    frags.append(arrow(cx, cy, 585, cy, color=INK, sw=1.8))
    frags.append(arrow(cx, cy, cx, 50, color=INK, sw=1.8))

    frags.append(text(595, cy + 4, "Re", size=13, bold=True, anchor="start"))
    frags.append(text(cx, 40, "Im", size=13, bold=True))

    # Права півплощина (p ≡ 1 mod 4): g(1, p) = +sqrt(p) > 0
    box_p1 = fitbox(365, 80, 210, 120, "p ≡ 1 (mod 4)\n\ng(1, p) = +√p\n(чисто дійсне, додатне)\n\nПриклади: p = 5, 13, 17, 29\ng(1, 5) = +√5 ≈ +2.236",
                    size=12, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8)
    frags.append(box_p1)
    frags.append(arrow(cx + 10, cy, cx + 80, cy, color=NEG, sw=3))
    frags.append(circle(cx + 80, cy, 5, fill=NEG, stroke="#ffffff", sw=1))

    # Верхня півплощина (p ≡ 3 mod 4): g(1, p) = +i*sqrt(p)
    box_p3 = fitbox(65, 80, 210, 120, "p ≡ 3 (mod 4)\n\ng(1, p) = +i·√p\n(чисто уявне, додатне ім.)\n\nПриклади: p = 3, 7, 11, 19\ng(1, 7) = +i·√7 ≈ +2.645i",
                    size=12, fill="#fff7ed", stroke=POS, sw=1.5, rx=8)
    frags.append(box_p3)
    frags.append(arrow(cx, cy - 10, cx, cy - 80, color=POS, sw=3))
    frags.append(circle(cx, cy - 80, 5, fill=POS, stroke="#ffffff", sw=1))

    # Нижній висновок
    box_foot = fitbox(70, 360, 500, 45, "Гаусс доводив цей знак понад 4 роки (1801–1805): g(1, p)² = (-1)^((p-1)/2) · p",
                      size=12, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6, italic=True)
    frags.append(box_foot)

    render(os.path.join(OUT, 'mod4-sign-pattern.svg'), w, h, *frags)


if __name__ == '__main__':
    fig_vector_sum()
    fig_fourier_bridge()
    fig_constructive_destructive()
    fig_mod4_sign_pattern()
    print("Всі 4 фігури для gauss-sums успішно згенеровано.")
