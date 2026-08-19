# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Дуальний простір» (book/math/algebra/dual-space).
Використовує спільний модуль svgkit з каталогу scripts.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")


def fig_covector_hyperplanes():
    """Фігура 1: Вектор як стрілка проти ковектора як набору паралельних рівневих площин."""
    w, h = 760, 370
    frags = []

    # Ліва панель: Вектор v як спрямована стрілка
    frags.append(rect(20, 20, 345, 330, fill="none", stroke=MUTED, sw=1, rx=8))
    frags.append(text(192, 50, "Вектор v у просторі V", size=15, bold=True, color=INK))
    frags.append(text(192, 70, "Стрілка: величина та напрямок", size=12, color=MUTED))

    # Координатні осі лівої панелі
    frags.append(line(50, 260, 330, 260, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(line(70, 280, 70, 95, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(text(340, 264, "x₁", size=12, color=MUTED, anchor="start"))
    frags.append(text(70, 85, "x₂", size=12, color=MUTED))
    frags.append(circle(70, 260, 3, fill=LINE, stroke=LINE))
    frags.append(text(60, 272, "0", size=11, color=MUTED))

    # Вектор v (стрілка)
    frags.append(arrow(70, 260, 250, 140, color=POS, sw=3))
    tb_v, _, _ = textbox(270, 125, "v = (3, 2)", size=13, pad=6, fill="#fdecea", stroke=POS, bold=True, color=POS)
    frags.append(tb_v)

    # Підпис під стрілкою
    frags.append(text(192, 330, "Елемент простору: стан, переміщення, швидкість", size=11, color=INK))

    # Права панель: Ковектор phi як рівневі площини
    frags.append(rect(395, 20, 345, 330, fill="none", stroke=MUTED, sw=1, rx=8))
    frags.append(text(567, 50, "Ковектор φ у дуальному просторі V*", size=15, bold=True, color=INK))
    frags.append(text(567, 70, "Паралельні рівневі лінії φ(v) = k", size=12, color=MUTED))

    y_base = 250
    x_base = 450
    frags.append(circle(x_base, y_base, 3, fill=LINE, stroke=LINE))
    frags.append(text(440, 262, "0", size=11, color=MUTED))

    lines_data = [
        (0, 415, 250, 480, 120, "φ = 0 (ядро)"),
        (2, 445, 250, 510, 120, "φ = 2"),
        (4, 475, 250, 540, 120, "φ = 4"),
        (6, 505, 250, 570, 120, "φ = 6"),
        (8, 535, 250, 600, 120, "φ = 8"),
    ]

    for k, lx1, ly1, lx2, ly2, lbl in lines_data:
        is_ker = (k == 0)
        c = NEG if not is_ker else LINE
        sw = 1.8 if not is_ker else 2.2
        dash = None if not is_ker else "4,2"
        frags.append(line(lx1, ly1, lx2, ly2, color=c, sw=sw, dash=dash))
        frags.append(text(lx2 + 4, ly2 - 2, lbl, size=10, color=c, anchor="start", bold=is_ker))

    # Вектор v, що пронизує рівневі лінії
    frags.append(arrow(x_base, y_base, x_base + 135, y_base - 90, color=POS, sw=2.5))
    frags.append(text(x_base + 140, y_base - 95, "v", size=13, color=POS, bold=True))

    # Точки перетину
    for px, py in [(x_base + 27, y_base - 18), (x_base + 54, y_base - 36), (x_base + 81, y_base - 54), (x_base + 108, y_base - 72), (x_base + 135, y_base - 90)]:
        frags.append(circle(px, py, 3.5, fill="#ffffff", stroke=POS, sw=1.5))

    tb_action, _, _ = textbox(567, 285, "Дія ⟨φ, v⟩ = 8: стрілка пронизує 8 засічок лінійки", size=11, pad=5, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG)
    frags.append(tb_action)

    frags.append(text(567, 330, "Прилад вимірювання: градієнт, ціна, лінійна форма", size=11, color=INK))

    out_path = os.path.join(IMG_DIR, "covector-hyperplanes.svg")
    render(out_path, w, h, *frags)


def fig_basis_transformation():
    """Фігура 2: Зміна базису: контраваріантні координати вектора проти коваріантних компонент ковектора."""
    w, h = 760, 370
    frags = []

    # Лівий блок: Початковий базис
    frags.append(rect(20, 20, 345, 330, fill="none", stroke=MUTED, sw=1, rx=8))
    frags.append(text(192, 50, "Початковий базис e₁, e₂", size=15, bold=True, color=INK))
    frags.append(text(192, 70, "Координатна сітка одиничного масштабу", size=12, color=MUTED))

    ox1, oy1 = 60, 240
    # Сітка початкова
    for i in range(4):
        frags.append(line(ox1 + i * 50, oy1, ox1 + i * 50, oy1 - 140, color="#f0f2f5", sw=1))
    for i in range(4):
        frags.append(line(ox1, oy1 - i * 45, ox1 + 150, oy1 - i * 45, color="#f0f2f5", sw=1))

    # Базисні вектори
    frags.append(arrow(ox1, oy1, ox1 + 50, oy1, color=LINE, sw=2.5))
    frags.append(text(ox1 + 25, oy1 + 16, "e₁", size=12, bold=True, color=LINE))
    frags.append(arrow(ox1, oy1, ox1, oy1 - 45, color=LINE, sw=2.5))
    frags.append(text(ox1 - 14, oy1 - 22, "e₂", size=12, bold=True, color=LINE))

    # Вектор v = 2 e₁ + e₂
    frags.append(arrow(ox1, oy1, ox1 + 100, oy1 - 45, color=POS, sw=2.5))
    frags.append(text(ox1 + 105, oy1 - 50, "v = 2e₁ + 1e₂", size=11, bold=True, color=POS, anchor="start"))

    # Дуальні лінії e¹*
    frags.append(line(ox1 + 50, oy1 + 10, ox1 + 50, oy1 - 150, color=NEG, sw=1.5, dash="4,2"))
    frags.append(text(ox1 + 50, oy1 - 155, "e¹* = 1", size=10, color=NEG, bold=True))

    tb_left, _, _ = textbox(192, 285, "Координата v¹ = 2, значення e¹*(v) = 2", size=11, pad=5, fill="#f4f6f8", stroke=MUTED, color=INK)
    frags.append(tb_left)
    frags.append(text(192, 330, "Масштаб базису 1 → одиничний крок", size=11, color=MUTED))

    # Правий блок: Розтягнутий базис e₁' = 2 e₁
    frags.append(rect(395, 20, 345, 330, fill="none", stroke=MUTED, sw=1, rx=8))
    frags.append(text(567, 50, "Новий базис e₁′ = 2e₁, e₂′ = e₂", size=15, bold=True, color=INK))
    frags.append(text(567, 70, "Базис розтягнуто вдвічі по осі x₁", size=12, color=MUTED))

    ox2, oy2 = 435, 240
    # Сітка нова
    for i in range(3):
        frags.append(line(ox2 + i * 100, oy2, ox2 + i * 100, oy2 - 140, color="#f0f2f5", sw=1))
    for i in range(4):
        frags.append(line(ox2, oy2 - i * 45, ox2 + 200, oy2 - i * 45, color="#f0f2f5", sw=1))

    # Нові базисні вектори
    frags.append(arrow(ox2, oy2, ox2 + 100, oy2, color=LINE, sw=2.5))
    frags.append(text(ox2 + 50, oy2 + 16, "e₁′ = 2e₁", size=12, bold=True, color=LINE))
    frags.append(arrow(ox2, oy2, ox2, oy2 - 45, color=LINE, sw=2.5))
    frags.append(text(ox2 - 14, oy2 - 22, "e₂′", size=12, bold=True, color=LINE))

    # Той самий вектор v, але його координата зменшилась: v¹' = 1
    frags.append(arrow(ox2, oy2, ox2 + 100, oy2 - 45, color=POS, sw=2.5))
    frags.append(text(ox2 + 105, oy2 - 50, "v = 1e₁′ + 1e₂′", size=11, bold=True, color=POS, anchor="start"))

    # Дуальний базис e'¹* має стиснутися / погустішати
    frags.append(line(ox2 + 100, oy2 + 10, ox2 + 100, oy2 - 150, color=NEG, sw=1.5, dash="4,2"))
    frags.append(text(ox2 + 100, oy2 - 155, "e′¹* = 1 (при x₁=2)", size=10, color=NEG, bold=True))

    tb_right, _, _ = textbox(567, 285, "Контраваріантність: v¹′ = ½ v¹ | Коваріантність: e′¹* = ½ e¹*", size=10.5, pad=5, fill="#fdecea", stroke=POS, bold=True, color=INK)
    frags.append(tb_right)
    frags.append(text(567, 330, "Векторні координати і ковектори міняються навпаки", size=11, color=MUTED))

    out_path = os.path.join(IMG_DIR, "basis-transformation.svg")
    render(out_path, w, h, *frags)


def fig_dual_map_pullback():
    """Фігура 3: Пряме відображення A: V -> W та дуальне A*: W* -> V* (pullback)."""
    w, h = 760, 320
    frags = []

    # Верхній рівень: векторні простори V і W
    tb_v, _, _ = textbox(160, 80, "Простір станів V\nелемент: вектор v", size=13, pad=8, fill="#fdecea", stroke=POS, bold=True, color=INK)
    frags.append(tb_v)

    tb_w, _, _ = textbox(600, 80, "Простір цілей W\nелемент: вектор w = A(v)", size=13, pad=8, fill="#fdecea", stroke=POS, bold=True, color=INK)
    frags.append(tb_w)

    # Пряма стрілка A: V -> W
    frags.append(arrow(265, 80, 475, 80, color=POS, sw=3))
    frags.append(text(370, 65, "Пряма дія A : V → W", size=13, bold=True, color=POS))
    frags.append(text(370, 100, "Переносить вектор: v ↦ A(v)", size=11, color=MUTED))

    # Нижній рівень: дуальні простори V* і W*
    tb_vstar, _, _ = textbox(160, 240, "Дуальний простір V*\nковектор: A*(ψ)", size=13, pad=8, fill="#eaf0fd", stroke=NEG, bold=True, color=INK)
    frags.append(tb_vstar)

    tb_wstar, _, _ = textbox(600, 240, "Дуальний простір W*\nковектор-детектор: ψ", size=13, pad=8, fill="#eaf0fd", stroke=NEG, bold=True, color=INK)
    frags.append(tb_wstar)

    # Зворотна стрілка A*: W* -> V* (Pullback)
    frags.append(arrow(475, 240, 265, 240, color=NEG, sw=3))
    frags.append(text(370, 225, "Дуальне відображення A* : W* → V*", size=13, bold=True, color=NEG))
    frags.append(text(370, 260, "Підтягує вимірювання (pullback): ψ ↦ ψ ∘ A", size=11, color=MUTED))

    # Вертикальні зв'язки (вимірювання / оцінка)
    frags.append(line(160, 125, 160, 195, color=FIELD, sw=1.8, dash="4,2"))
    frags.append(text(160, 163, "⟨A*ψ, v⟩", size=12, bold=True, color=FIELD))

    frags.append(line(600, 125, 600, 195, color=FIELD, sw=1.8, dash="4,2"))
    frags.append(text(600, 163, "⟨ψ, Av⟩", size=12, bold=True, color=FIELD))

    # Рівність результату вимірювання
    frags.append(text(370, 163, "≡ Одне й те саме число: ⟨A*ψ, v⟩ = ⟨ψ, Av⟩", size=12.5, bold=True, color=FIELD))

    out_path = os.path.join(IMG_DIR, "dual-map-pullback.svg")
    render(out_path, w, h, *frags)


def fig_annihilator_geometry():
    """Фігура 4: Підпростір U і його анулятор U^0."""
    w, h = 760, 360
    frags = []

    # Ліва панель: Підпростір U в просторі V
    frags.append(rect(20, 20, 345, 320, fill="none", stroke=MUTED, sw=1, rx=8))
    frags.append(text(192, 50, "Підпростір U ⊂ V (dim U = 1)", size=15, bold=True, color=INK))
    frags.append(text(192, 70, "Пряма лінія через 0 у площині V", size=12, color=MUTED))

    # Координати
    ox1, oy1 = 192, 175
    frags.append(line(40, oy1, 340, oy1, color="#e5e7eb", sw=1))
    frags.append(line(ox1, 260, ox1, 90, color="#e5e7eb", sw=1))
    frags.append(circle(ox1, oy1, 3, fill=LINE, stroke=LINE))
    frags.append(text(ox1 - 10, oy1 + 14, "0", size=11, color=MUTED))

    # Лінія U під кутом
    frags.append(line(70, 235, 314, 115, color=POS, sw=3))
    frags.append(text(320, 115, "U", size=14, bold=True, color=POS, anchor="start"))
    frags.append(arrow(ox1, oy1, ox1 + 70, oy1 - 35, color=POS, sw=2))
    frags.append(text(ox1 + 45, oy1 - 42, "u ∈ U", size=11, bold=True, color=POS))

    frags.append(text(192, 315, "Вектори, що лежать уздовж прямої U", size=11, color=INK))

    # Права панель: Анулятор U^0 у V*
    frags.append(rect(395, 20, 345, 320, fill="none", stroke=MUTED, sw=1, rx=8))
    frags.append(text(567, 50, "Анулятор U⁰ ⊂ V* (dim U⁰ = 1)", size=15, bold=True, color=INK))
    frags.append(text(567, 70, "Ковектори φ, де φ(u) = 0 для всіх u ∈ U", size=12, color=MUTED))

    # Рівневі лінії: нахилені паралельно до U
    # y = -0.5 x -> нахил dy/dx = -0.5
    frags.append(line(435, 215, 680, 95, color=NEG, sw=2.5, dash="4,2"))
    frags.append(text(685, 95, "φ = 0 (ker φ ⊇ U)", size=11, bold=True, color=NEG, anchor="start"))

    frags.append(line(415, 175, 660, 55, color=NEG, sw=1.5))
    frags.append(text(665, 55, "φ = 1", size=10, color=NEG, anchor="start"))

    tb_dim, _, _ = textbox(567, 260, "Теорема про розмірність:\ndim(U) + dim(U⁰) = 1 + 1 = 2 = dim(V)", size=11, pad=6, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG)
    frags.append(tb_dim)

    frags.append(text(567, 315, "Ковектори зникають на всьому підпросторі U", size=11, color=INK))

    out_path = os.path.join(IMG_DIR, "annihilator-geometry.svg")
    render(out_path, w, h, *frags)


def main():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
    fig_covector_hyperplanes()
    fig_basis_transformation()
    fig_dual_map_pullback()
    fig_annihilator_geometry()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
