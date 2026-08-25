# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми «Двоїстість Понтрягіна»."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_pontryagin_square():
    """Фігура 1: Квадрат двоїстості Понтрягіна — відповідності між групами та їхніми дуальними."""
    w, h = 820, 480
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 30, "Квадрат двоїстості Понтрягіна: класи груп та їхні характери", size=16, bold=True))

    # Стовпчик 1: Вихідна топологічна група G
    frags.append(fitbox(40, 60, 340, 40, "Вихідна абелева група G", size=14, bold=True, fill="#eaf2fd", stroke=NEG))

    # Стовпчик 2: Дуальна група характерів G^
    frags.append(fitbox(440, 60, 340, 40, "Дуальна група характерів G^ = Hom(G, T)", size=14, bold=True, fill="#fdecea", stroke=POS))

    # Пари двоїстості
    pairs = [
        ("Дискретна група Z (цілі числа)", "Компактне коло T = R/Z (фази)", "Ряди Фур'є (спектр дискретний)", 120),
        ("Компактне коло T (кути / період)", "Дискретна група Z (гармоніки)", "Аналіз періодичних коливань", 200),
        ("Неперервна пряма R (час)", "Неперервна пряма R (частота)", "Класичний інтеграл Фур'є (самодуальна)", 280),
        ("Скінченна циклічна Z_n", "Скінченна циклічна Z_n", "Дискретне перетворення Фур'є (DFT)", 360),
    ]

    for g_text, g_dual, note, y_pos in pairs:
        # Лівий блок
        frags.append(fitbox(40, y_pos, 340, 60, g_text, size=13, bold=True, fill=FILL, stroke=LINE))
        # Правий блок
        frags.append(fitbox(440, y_pos, 340, 60, g_dual, size=13, bold=True, fill=FILL, stroke=LINE))
        # Стрілка між ними (двостороння або подвійна)
        mid_y = y_pos + 30
        frags.append(line(385, mid_y - 4, 435, mid_y - 4, color=FIELD, sw=2))
        frags.append(line(385, mid_y + 4, 435, mid_y + 4, color=FIELD, sw=2))
        frags.append(text(410, mid_y - 12, "дуальність", size=10, color=MUTED, bold=False))
        frags.append(text(410, mid_y + 20, "G ≅ G^^", size=11, color=FIELD, bold=True))
        # Пояснення знизу під блоками
        frags.append(text(w / 2, y_pos + 66, note, size=11, color=MUTED, italic=True))

    # Підсумок властивостей
    frags.append(fitbox(40, 435, 740, 36, "Компактна G  <===>  Дискретна G^   |   Дискретна G  <===>  Компактна G^", size=12, bold=True, fill="#eef9f1", stroke=FIELD))

    render(os.path.join(OUT_DIR, "pontryagin-square.svg"), w, h, *frags)


def fig_character_mapping():
    """Фігура 2: Дія характеру — гомоморфізм групи на комплексне одиничне коло."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 28, "Гомоморфізм характеру: перенесення групової операції на коло T", size=16, bold=True))

    # Зліва: Абелева група G (елементи g1, g2, g1+g2)
    frags.append(rect(40, 60, 320, 330, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(200, 90, "Абелева група (G, +)", size=15, bold=True, color=NEG))

    # Точки в G
    frags.append(circle(120, 160, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(120, 165, "g₁", size=14, bold=True, color=NEG))

    frags.append(circle(280, 160, 22, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(280, 165, "g₂", size=14, bold=True, color=NEG))

    # Операція додавання
    frags.append(arrow(145, 160, 255, 160, color=MUTED, sw=1.5))
    frags.append(text(200, 150, "додавання +", size=11, color=MUTED))

    # Сума
    frags.append(circle(200, 270, 26, fill="#d6e4fd", stroke=NEG, sw=2.5))
    frags.append(text(200, 275, "g₁ + g₂", size=14, bold=True, color=NEG))

    frags.append(arrow(120, 185, 180, 250, color=NEG, sw=1.5))
    frags.append(arrow(280, 185, 220, 250, color=NEG, sw=1.5))

    # Нейтральний елемент
    frags.append(circle(200, 350, 18, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(200, 355, "0", size=13, bold=True))
    frags.append(text(200, 380, "нейтральний елемент", size=10, color=MUTED))

    # Стрілка відображення χ
    frags.append(arrow(370, 210, 450, 210, color=FIELD, sw=2.5))
    frags.append(text(410, 195, "характер χ", size=14, bold=True, color=FIELD))
    frags.append(text(410, 230, "χ(g) ∈ T", size=12, color=FIELD))

    # Справа: Одиничне комплексне коло T (множення фаз e^{i θ})
    frags.append(rect(460, 60, 320, 330, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(620, 90, "Одиничне коло (T, ·)", size=15, bold=True, color=POS))

    # Комплексне коло
    cx, cy, r = 620, 230, 95
    # Осі
    frags.append(line(cx - 110, cy, cx + 110, cy, color="#d0d0d0", sw=1))
    frags.append(line(cx, cy - 110, cx, cy + 110, color="#d0d0d0", sw=1))
    frags.append(text(cx + 105, cy - 8, "Re", size=10, color=MUTED))
    frags.append(text(cx + 8, cy - 100, "Im", size=10, color=MUTED))

    frags.append(circle(cx, cy, r, fill="#ffffff", stroke=POS, sw=2))

    # Точка 1 на колі (χ(0) = 1)
    frags.append(circle(cx + r, cy, 5, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx + r + 20, cy + 4, "1 = χ(0)", size=11, bold=True, color=POS))

    # Точка χ(g1)
    ang1 = math.radians(40)
    p1_x = cx + r * math.cos(ang1)
    p1_y = cy - r * math.sin(ang1)
    frags.append(circle(p1_x, p1_y, 6, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(p1_x + 24, p1_y - 6, "χ(g₁)", size=12, bold=True, color=POS))

    # Точка χ(g2)
    ang2 = math.radians(75)
    p2_x = cx + r * math.cos(ang2)
    p2_y = cy - r * math.sin(ang2)
    frags.append(circle(p2_x, p2_y, 6, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(p2_x - 18, p2_y - 12, "χ(g₂)", size=12, bold=True, color=POS))

    # Точка χ(g1 + g2) = χ(g1) * χ(g2)
    ang_sum = ang1 + ang2
    psum_x = cx + r * math.cos(ang_sum)
    psum_y = cy - r * math.sin(ang_sum)
    frags.append(circle(psum_x, psum_y, 7, fill=POS, stroke=POS, sw=2))
    frags.append(text(psum_x - 45, psum_y - 8, "χ(g₁ + g₂)", size=12, bold=True, color=POS))

    # Дуга додавання кутів
    frags.append(text(cx, cy + 70, "χ(g₁ + g₂) = χ(g₁) · χ(g₂)", size=12, bold=True, color=INK))
    frags.append(text(cx, cy + 90, "додавання в G переходить у множення фаз", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "character-circle-mapping.svg"), w, h, *frags)


def fig_subgroup_annihilator():
    """Фігура 3: Двоїстість підгруп та ануляторів (ортогональних доповнень)."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 28, "Відповідність Ґалуа між підгрупами G та ануляторами в G^", size=16, bold=True))

    # Ліва ґратка: Підгрупи в G
    frags.append(fitbox(60, 60, 300, 40, "Ґратка замкнених підгруп у G", size=14, bold=True, fill="#eaf2fd", stroke=NEG))

    frags.append(fitbox(110, 120, 200, 45, "Вся група G", size=13, bold=True, fill=FILL, stroke=NEG))
    frags.append(fitbox(110, 210, 200, 45, "Підгрупа H ≤ G", size=13, bold=True, fill="#d6e4fd", stroke=NEG))
    frags.append(fitbox(110, 300, 200, 45, "Тривіальна підгрупа {0}", size=13, bold=True, fill=FILL, stroke=NEG))

    # Лінії включення зліва
    frags.append(line(210, 165, 210, 210, color=NEG, sw=2))
    frags.append(line(210, 255, 210, 300, color=NEG, sw=2))
    frags.append(text(190, 188, "⊆", size=16, bold=True, color=NEG))
    frags.append(text(190, 278, "⊆", size=16, bold=True, color=NEG))

    # Права ґратка: Анулятори в G^
    frags.append(fitbox(460, 60, 300, 40, "Ґратка ануляторів у G^", size=14, bold=True, fill="#fdecea", stroke=POS))

    frags.append(fitbox(510, 120, 200, 45, "Тривіальний анулятор {1} = G^⊥", size=12, bold=True, fill=FILL, stroke=POS))
    frags.append(fitbox(510, 210, 200, 45, "Анулятор H^⊥ ≤ G^", size=13, bold=True, fill="#fadbd8", stroke=POS))
    frags.append(fitbox(510, 300, 200, 45, "Вся дуальна група G^ = {0}^⊥", size=12, bold=True, fill=FILL, stroke=POS))

    # Лінії включення справа (перевернутий порядок!)
    frags.append(line(610, 165, 610, 210, color=POS, sw=2))
    frags.append(line(610, 255, 610, 300, color=POS, sw=2))
    frags.append(text(630, 188, "⊆", size=16, bold=True, color=POS))
    frags.append(text(630, 278, "⊆", size=16, bold=True, color=POS))

    # Стрілки взаємного обернення (анти-ізоморфізм порядків)
    frags.append(line(320, 142, 500, 322, color=FIELD, sw=1.8, dash="4,4"))
    frags.append(line(320, 322, 500, 142, color=FIELD, sw=1.8, dash="4,4"))
    frags.append(line(320, 232, 500, 232, color=FIELD, sw=2))

    frags.append(text(410, 218, "H  <===>  H^⊥", size=12, bold=True, color=FIELD))
    frags.append(text(410, 248, "порядок обертається", size=10, color=MUTED))

    # Канонічні ізоморфізми фактор-груп
    frags.append(fitbox(60, 375, 700, 45, "Канонічні ізоморфізми:   (G / H)^ ≅ H^⊥   та   H^ ≅ G^ / H^⊥", size=13, bold=True, fill="#eef9f1", stroke=FIELD))

    render(os.path.join(OUT_DIR, "subgroup-annihilator-lattice.svg"), w, h, *frags)


def fig_fourier_duality():
    """Фігура 4: Гармонійний аналіз на LCA-групах — пряме та обернене перетворення Фур'є."""
    w, h = 820, 420
    frags = []

    frags.append(text(w / 2, 28, "Гармонійний аналіз: двоїстість Фур'є між функціями на G та спектром на G^", size=16, bold=True))

    # Лівий блок: Простір функцій L^2(G)
    frags.append(rect(40, 60, 320, 320, fill=FILL, stroke=NEG, sw=2, rx=8))
    frags.append(text(200, 95, "Часовий / просторовий домен", size=14, bold=True, color=NEG))
    frags.append(text(200, 120, "Простір L²(G, dμ)", size=16, bold=True, color=INK))

    frags.append(fitbox(60, 150, 280, 60, "Сигнал f(g) на групі G\nЕнергія: ||f||² = ∫_G |f(g)|² dμ(g)", size=12, bold=False, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(60, 230, 280, 60, "Згортка сигналів:\n(f * h)(g) = ∫_G f(y) h(g - y) dμ(y)", size=12, bold=False, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(60, 310, 280, 50, "Зсув сигналу: T_y f(g) = f(g - y)", size=12, bold=False, fill="#ffffff", stroke=LINE))

    # Правий блок: Простір спектрів L^2(G^)
    frags.append(rect(460, 60, 320, 320, fill=FILL, stroke=POS, sw=2, rx=8))
    frags.append(text(620, 95, "Частотний / спектральний домен", size=14, bold=True, color=POS))
    frags.append(text(620, 120, "Простір L²(G^, dν)", size=16, bold=True, color=INK))

    frags.append(fitbox(480, 150, 280, 60, "Спектр f^(χ) на дуальній групі G^\nЕнергія: ||f^||² = ∫_{G^} |f^(χ)|² dν(χ)", size=12, bold=False, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(480, 230, 280, 60, "Поточковий добуток:\n(f * h)^(χ) = f^(χ) · h^(χ)", size=12, bold=False, fill="#ffffff", stroke=LINE))

    frags.append(fitbox(480, 310, 280, 50, "Модуляція фази: (T_y f)^(χ) = χ(y)⁻¹ · f^(χ)", size=12, bold=False, fill="#ffffff", stroke=LINE))

    # Стрілка вперед: Пряме перетворення Фур'є F
    frags.append(arrow(370, 150, 450, 150, color=FIELD, sw=2.5))
    frags.append(text(410, 138, "F (пряме)", size=12, bold=True, color=FIELD))
    frags.append(text(410, 172, "f^(χ) = ∫ f χ̄", size=10, color=MUTED))

    # Стрілка назад: Обернене перетворення Фур'є F^-1
    frags.append(arrow(450, 230, 370, 230, color=FIELD, sw=2.5))
    frags.append(text(410, 218, "F⁻¹ (обернене)", size=12, bold=True, color=FIELD))
    frags.append(text(410, 252, "f(g) = ∫ f^ χ", size=10, color=MUTED))

    # Теорема Планшереля внизу
    frags.append(fitbox(40, 388, 740, 26, "Теорема Планшереля:  ||f||_{L²(G)} = ||f^||_{L²(G^)}  (ізометрія Гільбертових просторів)", size=11, bold=True, fill="#eef9f1", stroke=FIELD))

    render(os.path.join(OUT_DIR, "fourier-duality-transform.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_pontryagin_square()
    fig_character_mapping()
    fig_subgroup_annihilator()
    fig_fourier_duality()
    print("Всі фігури згенеровано успішно.")
