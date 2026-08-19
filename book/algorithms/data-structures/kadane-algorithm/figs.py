# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для статті про алгоритм Кадане."""

import sys
import os

# scripts/ у корені репозиторію (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_complexity_comparison():
    """Фігура 1: Порівняння підходів розв'язання задачі про максимальний підмасив."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Еволюція складності задачі про максимальний підмасив", size=16, bold=True))

    # Стовпчик 1: Наївний підхід O(N^3)
    c1_x, c1_y = 145, 185
    b1, bw1, bh1 = textbox(c1_x, c1_y, 
        "Наївний перебір O(N³)\n"
        "3 вкладені цикли:\n"
        "• початок i від 0 до N-1\n"
        "• кінець j від i до N-1\n"
        "• підсумовування k від i до j\n"
        "Обчислення з нуля для кожного [i..j]",
        size=12, pad=12, fill="#fdf2f0", stroke=POS, min_w=230)
    frags.append(b1)
    frags.append(text(c1_x, 70, "Наївний алгоритм", size=14, bold=True, color=POS))
    frags.append(text(c1_x, 320, "Час: O(N³) | Пам'ять: O(1)", size=12, bold=True, color=POS))

    # Стрілка 1 -> 2
    frags.append(arrow(265, 185, 305, 185, color=MUTED, sw=2))

    # Стовпчик 2: Префіксні суми O(N^2)
    c2_x, c2_y = 410, 185
    b2, bw2, bh2 = textbox(c2_x, c2_y, 
        "Префіксні суми O(N²)\n"
        "2 вкладені цикли:\n"
        "• масив префіксів P[k]\n"
        "• сума [i..j] = P[j+1] - P[i]\n"
        "• обчислення суми за O(1)\n"
        "Перебір N(N+1)/2 пар індексів",
        size=12, pad=12, fill="#fbf8e8", stroke="#d4ac0d", min_w=230)
    frags.append(b2)
    frags.append(text(c2_x, 70, "Префіксна оптимізація", size=14, bold=True, color="#b7950b"))
    frags.append(text(c2_x, 320, "Час: O(N²) | Пам'ять: O(N)", size=12, bold=True, color="#b7950b"))

    # Стрілка 2 -> 3
    frags.append(arrow(530, 185, 570, 185, color=MUTED, sw=2))

    # Стовпчик 3: Алгоритм Кадане O(N)
    c3_x, c3_y = 675, 185
    b3, bw3, bh3 = textbox(c3_x, c3_y, 
        "Алгоритм Кадане O(N)\n"
        "1 лінійний прохід:\n"
        "• динамічний стан на кроці i\n"
        "• S[i] = max(A[i], S[i-1] + A[i])\n"
        "• оновлення глобального max\n"
        "Скидання при від'ємному накопиченні",
        size=12, pad=12, fill="#eafaf1", stroke=FIELD, min_w=230)
    frags.append(b3)
    frags.append(text(c3_x, 70, "Динамічне програмування", size=14, bold=True, color=FIELD))
    frags.append(text(c3_x, 320, "Час: O(N) | Пам'ять: O(1)", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "kadane-complexity-comparison.svg"), w, h, *frags)


def fig_state_machine():
    """Фігура 2: Принцип локального вибору на кроці i в алгоритмі Кадане."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Логіка прийняття рішень на кожному кроці i", size=16, bold=True))

    # Поточний стан
    s_x, s_y = 150, 175
    b_curr, _, _ = textbox(s_x, s_y,
        "Попередній стан:\n"
        "S[i-1] (накопичена сума\n"
        "підмасиву, що завершується в i-1)",
        size=12, pad=12, fill=FILL, stroke=LINE, min_w=210)
    frags.append(b_curr)

    # Вхідний елемент A[i]
    frags.append(rect(340, 150, 100, 50, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(390, 172, "Елемент A[i]", size=12, bold=True, color=NEG))
    frags.append(text(390, 190, "(поточне число)", size=10, color=MUTED))

    # Стрілки до входу
    frags.append(arrow(260, 175, 335, 175, color=LINE, sw=1.8))

    # Розгалуження умов
    frags.append(arrow(445, 160, 545, 115, color=FIELD, sw=2))
    frags.append(text(495, 125, "S[i-1] > 0", size=11, bold=True, color=FIELD))

    frags.append(arrow(445, 190, 545, 235, color=POS, sw=2))
    frags.append(text(495, 230, "S[i-1] ≤ 0", size=11, bold=True, color=POS))

    # Результат 1: Продовження
    b_ext, _, _ = textbox(675, 115,
        "Продовжити поточний підмасив:\n"
        "S[i] = S[i-1] + A[i]\n"
        "(попередній префікс є вигідним)",
        size=12, pad=10, fill="#eafaf1", stroke=FIELD, min_w=240)
    frags.append(b_ext)

    # Результат 2: Початок нового
    b_rst, _, _ = textbox(675, 235,
        "Почати новий підмасив з A[i]:\n"
        "S[i] = A[i]\n"
        "(попередній тягар лише зменшує суму)",
        size=12, pad=10, fill="#fdf2f0", stroke=POS, min_w=240)
    frags.append(b_rst)

    # Оновлення глобального максимуму внизу
    frags.append(rect(150, 305, 520, 36, fill="#f4f6f7", stroke=LINE, sw=1, rx=4))
    frags.append(text(410, 328, "Глобальне оновлення: max_so_far = max(max_so_far, S[i])", size=12, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "kadane-state-machine.svg"), w, h, *frags)


def fig_2d_reduction():
    """Фігура 3: Зведення двовимірної задачі (матриця R x C) до одновимірного Кадане."""
    w, h = 820, 380
    frags = []

    frags.append(text(w / 2, 28, "Двовимірний Кадане: стиснення стовпців між рядками r1 та r2", size=16, bold=True))

    # Матриця R x C
    mx, my = 50, 65
    mw, mh = 260, 240
    frags.append(rect(mx, my, mw, mh, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(mx + mw / 2, my + 20, "Матриця A розміром R × C", size=12, bold=True))

    # Рядки r1 та r2 (підсвічена смуга)
    r1_y = my + 60
    r2_y = my + 170
    frags.append(rect(mx + 10, r1_y, mw - 20, r2_y - r1_y + 30, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=4))
    frags.append(line(mx + 5, r1_y, mx + mw - 5, r1_y, color="#b7950b", sw=2, dash="4,3"))
    frags.append(text(mx + 25, r1_y - 6, "рядок r1", size=11, bold=True, color="#b7950b"))
    frags.append(line(mx + 5, r2_y + 30, mx + mw - 5, r2_y + 30, color="#b7950b", sw=2, dash="4,3"))
    frags.append(text(mx + 25, r2_y + 44, "рядок r2", size=11, bold=True, color="#b7950b"))

    # Стовпчики всередині виділення
    for ci in range(5):
        cx = mx + 60 + ci * 35
        frags.append(rect(cx, r1_y + 8, 26, r2_y - r1_y + 14, fill="#fdedec", stroke=POS, sw=1, rx=2))
        frags.append(text(cx + 13, r1_y + 45, "∑", size=12, color=POS, bold=True))

    # Стрілка перетворення (стиснення)
    frags.append(arrow(320, 175, 410, 175, color=LINE, sw=2))
    frags.append(text(365, 155, "Стиснення", size=11, bold=True))
    frags.append(text(365, 195, "стовпців", size=11, color=MUTED))

    # Одновимірний масив стиснених сум
    ax, ay = 425, 145
    frags.append(text(595, ay - 15, "1D масив тимчасових сум: temp[c] = ∑ A[r][c] для r ∈ [r1..r2]", size=12, bold=True))
    for i in range(5):
        cell_x = ax + i * 68
        frags.append(rect(cell_x, ay, 62, 55, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=4))
        frags.append(text(cell_x + 31, ay + 24, "temp[%d]" % i, size=11, bold=True, color=NEG))
        vals = ["+4", "−2", "+9", "+7", "−5"]
        frags.append(text(cell_x + 31, ay + 44, vals[i], size=12, bold=True, color=INK))

    # Виділення найкращого 1D підмасиву
    frags.append(rect(ax + 2 * 68 - 4, ay - 4, 2 * 68 + 70, 63, fill="none", stroke=FIELD, sw=2.5, rx=6))
    frags.append(text(ax + 3 * 68, ay + 80, "1D Кадане знаходить [c1..c2] = [2..3] (сума = 16)", size=11, bold=True, color=FIELD))

    # Підсумок складності
    frags.append(rect(50, 325, 720, 38, fill=FILL, stroke=LINE, sw=1, rx=4))
    frags.append(text(410, 348, "Загальна складність: O(R² · C) при фіксації пар (r1, r2) та лінійному проході за O(C)", size=12, bold=True))

    render(os.path.join(IMG_DIR, "kadane-2d-matrix-reduction.svg"), w, h, *frags)


def fig_circular_subarray():
    """Фігура 4: Пошук максимального підмасиву у кільцевому масиві."""
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Кільцевий підмасив: класичний випадок проти циклічного обгортання", size=16, bold=True))

    # Випадок 1: Без обгортання
    b1_x, b1_y = 210, 175
    b1, _, _ = textbox(b1_x, b1_y,
        "Випадок 1: Лінійний підмасив (без переходу)\n\n"
        "• Оптимальний підмасив лежить суцільно всередині:\n"
        "  [ ... |  МАКСИМУМ  | ... ]\n"
        "• Знаходиться звичайним 1D Кадане\n"
        "• Результат: max_kadane",
        size=12, pad=12, fill="#eafaf1", stroke=FIELD, min_w=360)
    frags.append(b1)
    frags.append(text(b1_x, 70, "Варіант А: Звичайний максимум", size=14, bold=True, color=FIELD))

    # Випадок 2: З обгортанням через межу
    b2_x, b2_y = 610, 175
    b2, _, _ = textbox(b2_x, b2_y,
        "Випадок 2: Циклічне обгортання через краї\n\n"
        "• Максимум складається з префікса й суфікса:\n"
        "  [ МАКС_1 |  МІНІМУМ  | МАКС_2 ]\n"
        "• Еквівалент: total_sum − min_kadane\n"
        "• Вирізаємо серцевину з мінімальною сумою",
        size=12, pad=12, fill="#fef9e7", stroke="#d4ac0d", min_w=360)
    frags.append(b2)
    frags.append(text(b2_x, 70, "Варіант Б: Циклічний максимум", size=14, bold=True, color="#b7950b"))

    # Граничний випадок (усі від'ємні)
    frags.append(rect(50, 295, 720, 48, fill="#fdf2f0", stroke=POS, sw=1.5, rx=6))
    frags.append(text(410, 316, "Критичний крайовий випадок: Усі елементи масиву від'ємні!", size=12, bold=True, color=POS))
    frags.append(text(410, 334, "Якщо total_sum == min_kadane (порожній залишок), відповіддю є max_kadane, а не 0", size=11, color=INK))

    render(os.path.join(IMG_DIR, "kadane-circular-subarray.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_complexity_comparison()
    fig_state_machine()
    fig_2d_reduction()
    fig_circular_subarray()
    print("Всі фігури згенеровано успішно.")
