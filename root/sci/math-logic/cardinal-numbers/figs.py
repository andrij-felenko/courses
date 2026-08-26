# -*- coding: utf-8 -*-
"""Фігури до теми «Кардинальні числа (потужність)».
Запуск: python figs.py  → генерує SVG у теці ./img/
  1. cantor-bernstein      — Побудова взаємно однозначної відповідності за теоремою Кантора-Бернштейна
  2. cardinal-hierarchies  — Ієрархії Алеф і Бет: зіставлення потужностей типових множин
  3. uncomputable-gap      — Кардинальний розрив між зліченними програмами та незліченними задачами
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL   = "#fdecea"
BLUEFILL  = "#eaf0fd"
YELLOWFILL = "#fef9e7"
GRAYFILL  = "#f4f6f8"


def fig_cantor_bernstein():
    W, H = 960, 480
    f = [
        text(W / 2, 28, "Теорема Кантора — Бернштейна: з двох ін'єкцій у бієкцію", size=18, bold=True),
        text(W / 2, 50, "ланцюжки прообразів розбивають множини на класи, для кожного обирається пряме або обернене відображення",
             size=12, color=MUTED, italic=True)
    ]

    # Стовпчики множин A та B
    ax = 220
    bx = 740

    # Заголовки множин
    box_a, _, _ = textbox(ax, 90, "Множина A", size=15, bold=True, fill=BLUEFILL, stroke=NEG, min_w=160)
    box_b, _, _ = textbox(bx, 90, "Множина B", size=15, bold=True, fill=GREENFILL, stroke=FIELD, min_w=160)
    f.append(box_a)
    f.append(box_b)

    # Лінії-контейнери
    f.append(rect(ax - 90, 115, 180, 290, fill="#f8fafc", stroke=NEG, sw=1.2, rx=8))
    f.append(rect(bx - 90, 115, 180, 290, fill="#f8fafc", stroke=FIELD, sw=1.2, rx=8))

    # Секції ланцюжків усередині A та B
    # 1. Початок в A (A-ланцюг) -> застосовуємо f
    y1 = 160
    f.append(rect(ax - 80, y1 - 25, 160, 50, fill=BLUEFILL, stroke=NEG, sw=1.0, rx=5))
    f.append(text(ax, y1 - 6, "Частина A_A", size=12, bold=True, color=NEG))
    f.append(text(ax, y1 + 12, "(початок в A \\ g[B])", size=10.5, color=MUTED))

    f.append(rect(bx - 80, y1 - 25, 160, 50, fill=BLUEFILL, stroke=NEG, sw=1.0, rx=5))
    f.append(text(bx, y1 - 6, "Образ f[A_A]", size=12, bold=True, color=NEG))
    f.append(text(bx, y1 + 12, "накривається через f", size=10.5, color=MUTED))

    f.append(arrow(ax + 85, y1, bx - 85, y1, color=NEG, sw=2.0))
    f.append(text((ax + bx) / 2, y1 - 10, "h(x) = f(x)", size=12, bold=True, color=NEG))

    # 2. Початок в B (B-ланцюг) -> застосовуємо g^{-1}
    y2 = 240
    f.append(rect(ax - 80, y2 - 25, 160, 50, fill=GREENFILL, stroke=FIELD, sw=1.0, rx=5))
    f.append(text(ax, y2 - 6, "Образ g[B_B]", size=12, bold=True, color=FIELD))
    f.append(text(ax, y2 + 12, "прообраз через g", size=10.5, color=MUTED))

    f.append(rect(bx - 80, y2 - 25, 160, 50, fill=GREENFILL, stroke=FIELD, sw=1.0, rx=5))
    f.append(text(bx, y2 - 6, "Частина B_B", size=12, bold=True, color=FIELD))
    f.append(text(bx, y2 + 12, "(початок в B \\ f[A])", size=10.5, color=MUTED))

    f.append(arrow(bx - 85, y2, ax + 85, y2, color=FIELD, sw=2.0))
    f.append(text((ax + bx) / 2, y2 - 10, "g(y) [тому h(x) = g⁻¹(x)]", size=12, bold=True, color=FIELD))

    # 3. Нескінченні або циклічні ланцюжки (C-ланцюг) -> підійде будь-яке (наприклад f)
    y3 = 320
    f.append(rect(ax - 80, y3 - 25, 160, 50, fill=YELLOWFILL, stroke="#b7950b", sw=1.0, rx=5))
    f.append(text(ax, y3 - 6, "Частина A_∞", size=12, bold=True, color="#7d6608"))
    f.append(text(ax, y3 + 12, "(нескінченний родовід)", size=10.5, color=MUTED))

    f.append(rect(bx - 80, y3 - 25, 160, 50, fill=YELLOWFILL, stroke="#b7950b", sw=1.0, rx=5))
    f.append(text(bx, y3 - 6, "Частина B_∞", size=12, bold=True, color="#7d6608"))
    f.append(text(bx, y3 + 12, "повний збіг образів", size=10.5, color=MUTED))

    f.append(arrow(ax + 85, y3, bx - 85, y3, color="#b7950b", sw=2.0))
    f.append(text((ax + bx) / 2, y3 - 10, "h(x) = f(x)", size=12, bold=True, color="#7d6608"))

    # Підсумок у нижній рамці
    f.append(rect(ax - 90, 420, bx - ax + 180, 44, fill=GRAYFILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(W / 2, 447, "Результат: взаємно однозначна функція h: A → B без залишків і накладок",
                  size=13, bold=True, color=INK))

    render(os.path.join(IMG, "cantor-bernstein.svg"), W, H, *f)


def fig_cardinal_hierarchies():
    W, H = 1000, 500
    f = [
        text(W / 2, 28, "Сходи нескінченностей: Алеф-ієрархія та Бет-ієрархія", size=18, bold=True),
        text(W / 2, 50, "Алефи рахують усі можливі початкові ординали; Бети виникають через послідовне взяття булеана (2^κ)",
             size=12, color=MUTED, italic=True)
    ]

    # Дві осі поруч
    x_aleph = 280
    x_beth  = 720

    # Шапка колонок
    box_al, _, _ = textbox(x_aleph, 90, "Алеф-ієрархія (ℵ)", size=15, bold=True, fill=BLUEFILL, stroke=NEG, min_w=220)
    box_bt, _, _ = textbox(x_beth, 90, "Бет-ієрархія (ℶ)", size=15, bold=True, fill=GREENFILL, stroke=FIELD, min_w=220)
    f.append(box_al)
    f.append(box_bt)

    # Рівні
    levels = [
        (380, "ℵ₀", "ℶ₀", "Зліченна множина: ℕ, ℤ, ℚ, прості числа, коди програм", BLUEFILL, GREENFILL),
        (280, "ℵ₁", "ℶ₁", "Континуум c = 2^ℵ₀: ℝ, ℂ, відрізок [0, 1], точки площини ℝ²", BLUEFILL, GREENFILL),
        (180, "ℵ₂", "ℶ₂", "Булеан континууму 2^c: усі підмножини ℝ, усі функції ℝ → ℝ", BLUEFILL, GREENFILL)
    ]

    for y, al_sym, bt_sym, desc, c1, c2 in levels:
        # Блок Алефа
        box1, _, _ = textbox(x_aleph, y, al_sym, size=18, bold=True, fill=c1, stroke=NEG, min_w=90)
        f.append(box1)
        # Блок Бета
        box2, _, _ = textbox(x_beth, y, bt_sym, size=18, bold=True, fill=c2, stroke=FIELD, min_w=90)
        f.append(box2)

        # Опис посередині / знизу
        f.append(rect(100, y + 26, 800, 28, fill=GRAYFILL, stroke="#e2e8f0", sw=1.0, rx=4))
        f.append(text(W / 2, y + 45, desc, size=11.5, color=INK))

    # Стрілки росту вгору
    f.append(arrow(x_aleph, 345, x_aleph, 315, color=NEG, sw=2.0))
    f.append(text(x_aleph - 70, 333, "+1 початковий", size=10.5, bold=True, color=NEG))

    f.append(arrow(x_aleph, 245, x_aleph, 215, color=NEG, sw=2.0))
    f.append(text(x_aleph - 70, 233, "+1 початковий", size=10.5, bold=True, color=NEG))

    f.append(arrow(x_beth, 345, x_beth, 315, color=FIELD, sw=2.0))
    f.append(text(x_beth + 70, 333, "степінь 2^κ", size=10.5, bold=True, color=FIELD))

    f.append(arrow(x_beth, 245, x_beth, 215, color=FIELD, sw=2.0))
    f.append(text(x_beth + 70, 233, "степінь 2^κ", size=10.5, bold=True, color=FIELD))

    # Зв'язок на рівні нуль: ℵ₀ = ℶ₀
    f.append(line(x_aleph + 55, 380, x_beth - 55, 380, color=INK, sw=1.5, dash="4,4"))
    f.append(text(W / 2, 375, "ℵ₀ = ℶ₀ (завжди тотожні)", size=12, bold=True, color=INK))

    # Гіпотеза континууму (CH) між ℵ₁ та ℶ₁
    f.append(line(x_aleph + 55, 280, x_beth - 55, 280, color=POS, sw=1.8, dash="5,5"))
    f.append(rect(W / 2 - 130, 268, 260, 24, fill=REDFILL, stroke=POS, sw=1.2, rx=4))
    f.append(text(W / 2, 285, "Гіпотеза континууму: чи ℵ₁ = ℶ₁?", size=11.5, bold=True, color=POS))

    # Нижній висновок
    f.append(rect(80, 450, 840, 36, fill=YELLOWFILL, stroke="#b7950b", sw=1.2, rx=6))
    f.append(text(W / 2, 473, "У системі ZFC рівність ℵ₁ = ℶ₁ неможливо ані довести, ані спростувати (вона незалежна від аксіом).",
                  size=12, bold=True, color="#7d6608"))

    render(os.path.join(IMG, "cardinal-hierarchies.svg"), W, H, *f)


def fig_uncomputable_gap():
    W, H = 960, 420
    f = [
        text(W / 2, 28, "Кардинальний розрив: обчислювальні програми проти задач", size=18, bold=True),
        text(W / 2, 50, "тексти програм завжди зліченні (ℵ₀), тоді як простір задач має потужність континууму (2^ℵ₀)",
             size=12, color=MUTED, italic=True)
    ]

    # Лівий блок: програми
    x1 = 260
    f.append(rect(x1 - 180, 85, 360, 240, fill=BLUEFILL, stroke=NEG, sw=1.5, rx=8))
    f.append(text(x1, 115, "Множина всіх програм / алгоритмів", size=14.5, bold=True, color=NEG))
    f.append(text(x1, 140, "Тексти скінченної довжини в абетці Σ", size=12, color=MUTED))

    progs = [
        "1: def is_even(n): return n % 2 == 0",
        "2: def is_prime(n): ...",
        "3: def sort_array(arr): ...",
        "4: int main() { return 0; }",
        "..."
    ]
    for i, p in enumerate(progs):
        f.append(rect(x1 - 160, 160 + i * 26, 320, 22, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=3))
        f.append(text(x1 - 150, 176 + i * 26, p, size=11, color=INK, anchor="start"))

    box_sz1, _, _ = textbox(x1, 302, "Потужність: ℵ₀ (зліченна)", size=13, bold=True, fill="#ffffff", stroke=NEG, min_w=200)
    f.append(box_sz1)

    # Правий блок: задачі
    x2 = 700
    f.append(rect(x2 - 180, 85, 360, 240, fill=REDFILL, stroke=POS, sw=1.5, rx=8))
    f.append(text(x2, 115, "Множина всіх задач розпізнавання", size=14.5, bold=True, color=POS))
    f.append(text(x2, 140, "Усі можливі предикати f: ℕ → {0, 1}", size=12, color=MUTED))

    funcs = [
        "• Функція парності",
        "• Проблема зупинки тюрінг-машини",
        "• Завдання замощення площини",
        "• Незліченний океан довільних бітових масок",
        "..."
    ]
    for i, fn in enumerate(funcs):
        f.append(rect(x2 - 160, 160 + i * 26, 320, 22, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=3))
        f.append(text(x2 - 150, 176 + i * 26, fn, size=11, color=INK, anchor="start"))

    box_sz2, _, _ = textbox(x2, 302, "Потужність: 2^ℵ₀ = c (незліченна)", size=13, bold=True, fill="#ffffff", stroke=POS, min_w=220)
    f.append(box_sz2)

    # Стрілка між ними
    f.append(arrow(x1 + 185, 205, x2 - 185, 205, color=MUTED, sw=1.8))
    f.append(text(W / 2, 195, "Ін'єкція", size=12, bold=True, color=MUTED))
    f.append(text(W / 2, 225, "ℵ₀ < 2^ℵ₀", size=14, bold=True, color=POS))

    # Нижній висновок
    f.append(rect(60, 345, 840, 52, fill=YELLOWFILL, stroke="#b7950b", sw=1.2, rx=6))
    f.append(text(W / 2, 368, "Кардинальний наслідок: програм незрівнянно менше, ніж задач.",
                  size=13, bold=True, color="#7d6608"))
    f.append(text(W / 2, 388, "Майже будь-яка математична задача розпізнавання є алгоритмічно нерозв'язною.",
                  size=11.5, color="#7d6608"))

    render(os.path.join(IMG, "uncomputable-gap.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cantor_bernstein()
    fig_cardinal_hierarchies()
    fig_uncomputable_gap()
    print("Всі 3 фігури згенеровано успішно.")
