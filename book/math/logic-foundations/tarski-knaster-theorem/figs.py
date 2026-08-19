# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Теорема Тарського — Кнастера про нерухому точку».
Книга: math, Секція: logic-foundations, Слуг: tarski-knaster-theorem.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def make_lattice_fixed_points():
    """Фігура 1: Повна ґратка, префіксні/постфіксні точки та підґратка нерухомих точок."""
    w, h = 720, 500
    frags = []

    # Заголовок
    frags.append(text(360, 24, "Структура повної ґратки та нерухомих точок f(x)", size=16, bold=True))

    # Область ґратки (зовнішній ромб)
    # ⊤ зверху (360, 65), ⊥ знизу (360, 445), ліворуч (150, 255), праворуч (570, 255)
    frags.append('<polygon points="360,65 570,255 360,445 150,255" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="4,4"/>')

    # Область постфіксних точок x <= f(x) (нижня зона)
    frags.append('<polygon points="360,445 210,310 510,310" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.2"/>')

    # Область префіксних точок f(x) <= x (верхня зона)
    frags.append('<polygon points="360,65 210,200 510,200" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.2"/>')

    # Підґратка нерухомих точок Fix(f) (внутрішній виділений ромб)
    # gfp (360, 165), lfp (360, 345), ліва точка (290, 255), права точка (430, 255)
    frags.append('<polygon points="360,165 430,255 360,345 290,255" fill="#dcfce7" stroke="#16a34a" stroke-width="2.2"/>')

    # Лінії зв'язку між ключовими вузлами
    frags.append(line(360, 65, 360, 165, color="#64748b", sw=1.5, dash="3,3"))
    frags.append(line(360, 345, 360, 445, color="#64748b", sw=1.5, dash="3,3"))
    frags.append(line(290, 255, 360, 165, color="#16a34a", sw=1.5))
    frags.append(line(290, 255, 360, 345, color="#16a34a", sw=1.5))
    frags.append(line(430, 255, 360, 165, color="#16a34a", sw=1.5))
    frags.append(line(430, 255, 360, 345, color="#16a34a", sw=1.5))

    # Написи для зон (через textbox збоку, щоб не перетинати вертикальну лінію)
    b_pre, _, _ = textbox(235, 115, "Префіксні точки\nf(x) ≤ x", size=11, fill="#ffffff", stroke="#fca5a5", color="#b91c1c")
    frags.append(b_pre)

    b_post, _, _ = textbox(235, 395, "Постфіксні точки\nx ≤ f(x)", size=11, fill="#ffffff", stroke="#93c5fd", color="#1d4ed8")
    frags.append(b_post)

    # Вузли
    # ⊤ (Top)
    frags.append(circle(360, 65, 7, fill="#ffffff", stroke="#0f172a", sw=2))
    frags.append(text(360, 52, "⊤ (найбільший елемент ґратки)", size=13, bold=True))

    # ⊥ (Bottom)
    frags.append(circle(360, 445, 7, fill="#ffffff", stroke="#0f172a", sw=2))
    frags.append(text(360, 467, "⊥ (найменший елемент ґратки)", size=13, bold=True))

    # gfp (Greatest Fixed Point)
    frags.append(circle(360, 165, 6, fill="#16a34a", stroke="#0f172a", sw=2))
    b_gfp, _, _ = textbox(535, 165, "gfp(f) = ⋁ { x | x ≤ f(x) }\nнайбільша нерухома точка", size=11, fill="#ffffff", stroke="#16a34a", sw=1.5)
    frags.append(b_gfp)
    frags.append(line(367, 165, 430, 165, color="#16a34a", sw=1.2))

    # lfp (Least Fixed Point)
    frags.append(circle(360, 345, 6, fill="#16a34a", stroke="#0f172a", sw=2))
    b_lfp, _, _ = textbox(535, 345, "lfp(f) = ⋀ { x | f(x) ≤ x }\nнайменша нерухома точка", size=11, fill="#ffffff", stroke="#16a34a", sw=1.5)
    frags.append(b_lfp)
    frags.append(line(367, 345, 430, 345, color="#16a34a", sw=1.2))

    # Внутрішні нерухомі точки
    frags.append(circle(290, 255, 5, fill="#16a34a", stroke="#0f172a", sw=1.5))
    frags.append(circle(430, 255, 5, fill="#16a34a", stroke="#0f172a", sw=1.5))
    b_fix, _, _ = textbox(360, 255, "Fix(f) — повна\nпідґратка", size=11, fill="#ffffff", stroke="#16a34a", color="#15803d", bold=True)
    frags.append(b_fix)

    # Пояснювальний блок ліворуч
    b_info, _, _ = textbox(115, 165, "Теорема Тарського — Кнастера:\nFix(f) не порожня і\nутворює повну ґратку", size=11, fill="#ffffff", stroke="#64748b", pad=8)
    frags.append(b_info)

    render(os.path.join(OUT_DIR, "lattice-fixed-points.svg"), w, h, *frags)


def make_fixed_point_iteration():
    """Фігура 2: Ітеративне наближення нерухомої точки (Кліні та спадна ітерація)."""
    w, h = 680, 360
    frags = []

    frags.append(text(340, 24, "Конструктивне ітеративне наближення нерухомих точок", size=16, bold=True))

    # Ліва колонка: Висхідна ітерація від ⊥ до lfp
    b1, _, _ = textbox(190, 65, "Висхідна ітерація Кліні\nвід найменшого елемента ⊥", size=13, fill="#eff6ff", stroke="#3b82f6", bold=True)
    frags.append(b1)

    steps_up = [
        ("x₀ = ⊥", "базовий стан (немає інформації)"),
        ("x₁ = f(⊥)", "перший крок трансформатора"),
        ("x₂ = f²(⊥)", "накопичення фактів"),
        ("...", "ітерації монотонного зростання"),
        ("x* = lfp(f)", "стабілізація: f(x*) = x*"),
    ]

    y_start = 120
    for i, (expr, desc) in enumerate(steps_up):
        cy = y_start + i * 44
        is_last = (i == len(steps_up) - 1)
        fill_c = "#dcfce7" if is_last else "#ffffff"
        strk_c = "#16a34a" if is_last else "#94a3b8"
        b_step, _, _ = textbox(190, cy, f"{expr}  —  {desc}", size=11, fill=fill_c, stroke=strk_c, sw=1.5, bold=is_last)
        frags.append(b_step)
        if i < len(steps_up) - 1:
            frags.append(arrow(190, cy + 14, 190, cy + 30, color="#3b82f6", sw=1.5))

    # Права колонка: Спадна ітерація від ⊤ до gfp
    b2, _, _ = textbox(490, 65, "Спадна двоїста ітерація\nвід найбільшого елемента ⊤", size=13, fill="#fef2f2", stroke="#ef4444", bold=True)
    frags.append(b2)

    steps_down = [
        ("y₀ = ⊤", "максимальна невизначеність"),
        ("y₁ = f(⊤)", "відсікання неможливих станів"),
        ("y₂ = f²(⊤)", "уточнення безпечного інваріанта"),
        ("...", "ітерації монотонного спадання"),
        ("y* = gfp(f)", "стабілізація: f(y*) = y*"),
    ]

    for i, (expr, desc) in enumerate(steps_down):
        cy = y_start + i * 44
        is_last = (i == len(steps_down) - 1)
        fill_c = "#dcfce7" if is_last else "#ffffff"
        strk_c = "#16a34a" if is_last else "#94a3b8"
        b_step, _, _ = textbox(490, cy, f"{expr}  —  {desc}", size=11, fill=fill_c, stroke=strk_c, sw=1.5, bold=is_last)
        frags.append(b_step)
        if i < len(steps_down) - 1:
            frags.append(arrow(490, cy + 14, 490, cy + 30, color="#ef4444", sw=1.5))

    render(os.path.join(OUT_DIR, "fixed-point-iteration.svg"), w, h, *frags)


def make_abstract_interpretation():
    """Фігура 3: Зв'язок Галуа та обчислення нерухомої точки в аналізі програм."""
    w, h = 680, 360
    frags = []

    frags.append(text(340, 24, "Абстрактна інтерпретація: зведення до нерухомої точки", size=16, bold=True))

    # Конкретна область ліворуч (Concrete Domain)
    frags.append(rect(40, 60, 240, 260, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(160, 85, "Конкретна область P(S)", size=14, bold=True, color="#0f172a"))
    frags.append(text(160, 105, "Точні стани програми (нескінченні)", size=11, color="#64748b"))

    b_c1, _, _ = textbox(160, 150, "C₀: початкові стани {x = 0}", size=11, fill="#ffffff", stroke="#94a3b8")
    b_c2, _, _ = textbox(160, 240, "C*: точний інваріант програми", size=11, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_c1)
    frags.append(b_c2)
    frags.append(arrow(160, 168, 160, 222, color="#0f172a", sw=1.5))
    frags.append(text(175, 195, "F", size=13, bold=True))
    frags.append(text(110, 195, "необчислювано", size=10, color="#ef4444", italic=True))

    # Абстрактна область праворуч (Abstract Domain - ґратка)
    frags.append(rect(400, 60, 240, 260, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    frags.append(text(520, 85, "Абстрактна ґратка L", size=14, bold=True, color="#15803d"))
    frags.append(text(520, 105, "Інтервали [l, u] (скінченна висота)", size=11, color="#166534"))

    b_a1, _, _ = textbox(520, 150, "A₀ = α(C₀) = [0, 0]", size=11, fill="#ffffff", stroke="#16a34a")
    b_a2, _, _ = textbox(520, 240, "A* = lfp(F#) = [0, 100]", size=11, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(b_a1)
    frags.append(b_a2)
    frags.append(arrow(520, 168, 520, 222, color="#16a34a", sw=2.0))
    frags.append(text(538, 195, "F#", size=13, bold=True, color="#15803d"))
    frags.append(text(465, 195, "ітерація lfp", size=10, color="#15803d", italic=True))

    # Стрілки Галуа між областями (Абстракція α та конкретизація γ)
    frags.append(arrow(245, 140, 440, 140, color="#2563eb", sw=1.6))
    frags.append(text(340, 130, "абстракція α", size=12, bold=True, color="#2563eb"))

    frags.append(arrow(440, 250, 245, 250, color="#7c3aed", sw=1.6))
    frags.append(text(340, 268, "конкретизація γ", size=12, bold=True, color="#7c3aed"))

    # Гарантія коректності
    frags.append(text(340, 305, "Гарантія безпеки: C* ⊆ γ(lfp(F#))", size=12, bold=True, color="#0f172a"))

    render(os.path.join(OUT_DIR, "abstract-interpretation-flow.svg"), w, h, *frags)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    make_lattice_fixed_points()
    make_fixed_point_iteration()
    make_abstract_interpretation()
    print("All figures successfully generated in", OUT_DIR)


if __name__ == "__main__":
    main()
