# -*- coding: utf-8 -*-
"""Фігури для теми «Ігри Артура — Мерліна» (book/algorithms/complexity-computability/arthur-merlin-games)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_BG = "#ffffff"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_ARTHUR = "#dbeafe"       # синій для Артура (верифікатора)
COLOR_ARTHUR_BORDER = "#2563eb"
COLOR_MERLIN = "#fef3c7"       # жовтий/бурштиновий для Мерліна (доводжувача)
COLOR_MERLIN_BORDER = "#d97706"
COLOR_SUCCESS = "#d1fae5"      # зелений для прийняття
COLOR_SUCCESS_BORDER = "#059669"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_ma_vs_am():
    """Фігура 1: Порівняння структур протоколів MA (приватні монети) та AM (публічні монети)."""
    W, H = 960, 500
    frags = []

    # Заголовок
    t_box, _, _ = textbox(480, 35, "Порівняння ігрових моделей Merlin-Arthur (MA) та Arthur-Merlin (AM)",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Ліва панель — Протокол MA (Merlin -> Arthur)
    frags.append(rect(30, 75, 435, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(247, 105, "Модель MA (Приватні монети)", size=15, bold=True, color="#1e3a8a"))
    frags.append(text(247, 127, "Мерлін відправляє сертифікат до випадкових монет", size=12, italic=True, color=COLOR_MUTED))

    # Крок 1 MA: Мерлін надсилає m
    tb_m1, _, _ = textbox(247, 175, "1. Мерлін створює доказове повідомлення m\n(спираючись лише на вхід x)",
                          size=12, bold=True, fill=COLOR_MERLIN, stroke=COLOR_MERLIN_BORDER, sw=1.5, pad=8)
    frags.append(tb_m1)
    frags.append(arrow(247, 215, 247, 245, color=COLOR_LINE, sw=1.5))

    # Крок 2 MA: Артур підкидає приватні монети r
    tb_a1, _, _ = textbox(247, 285, "2. Артур підкидає ПРИВАТНІ монети r\n(Мерлін не бачить результатів r)",
                          size=12, bold=True, fill=COLOR_ARTHUR, stroke=COLOR_ARTHUR_BORDER, sw=1.5, pad=8)
    frags.append(tb_a1)
    frags.append(arrow(247, 325, 247, 355, color=COLOR_LINE, sw=1.5))

    # Крок 3 MA: Детермінована перевірка V(x, m, r)
    tb_v1, _, _ = textbox(247, 395, "3. Перевірка: V(x, m, r) ∈ {Прийняти, Відхилити}\n(Помилка: Completeness ≥ 2/3, Soundness ≤ 1/3)",
                          size=12, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER, sw=1.5, pad=8)
    frags.append(tb_v1)


    # Права панель — Протокол AM (Arthur -> Merlin -> Arthur)
    frags.append(rect(495, 75, 435, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(712, 105, "Модель AM (Публічні монети)", size=15, bold=True, color="#7c2d12"))
    frags.append(text(712, 127, "Артур відкриває монети r першим", size=12, italic=True, color=COLOR_MUTED))

    # Крок 1 AM: Артур підкидає і публікує r
    tb_a2, _, _ = textbox(712, 175, "1. Артур підкидає ПУБЛІЧНІ монети r\nта відкриває їх Мерліну",
                          size=12, bold=True, fill=COLOR_ARTHUR, stroke=COLOR_ARTHUR_BORDER, sw=1.5, pad=8)
    frags.append(tb_a2)
    frags.append(arrow(712, 215, 712, 245, color=COLOR_LINE, sw=1.5))

    # Крок 2 AM: Мерлін відповідь m(x, r)
    tb_m2, _, _ = textbox(712, 285, "2. Мерлін підбирає повідомлення m(x, r)\nзнаючи конкретний виклик r",
                          size=12, bold=True, fill=COLOR_MERLIN, stroke=COLOR_MERLIN_BORDER, sw=1.5, pad=8)
    frags.append(tb_m2)
    frags.append(arrow(712, 325, 712, 355, color=COLOR_LINE, sw=1.5))

    # Крок 3 AM: Детермінована перевірка V(x, r, m)
    tb_v2, _, _ = textbox(712, 395, "3. Перевірка: V(x, r, m) ∈ {Прийняти, Відхилити}\n(Потужніша модель: MA ⊆ AM)",
                          size=12, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER, sw=1.5, pad=8)
    frags.append(tb_v2)

    render(os.path.join(IMG, "fig1-ma-vs-am.svg"), W, H, *frags)


def fig2_gni_am_protocol():
    """Фігура 2: Схема інтерактивного AM-протоколу для неізоморфізму графів (GNI)."""
    W, H = 940, 480
    frags = []

    # Заголовок
    t_box, _, _ = textbox(470, 35, "Інтерактивний AM-протокол для неізоморфізму графів (GNI)",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Вхідні дані
    t_in, _, _ = textbox(470, 85, "Вхідні дані: графи G₀ та G₁ з одинаковою кількістю вершин n",
                         size=13, bold=True, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, pad=6)
    frags.append(t_in)

    # Крок 1: Артур створює викликовий граф H
    frags.append(rect(50, 130, 390, 140, fill=COLOR_ARTHUR, stroke=COLOR_ARTHUR_BORDER, sw=1.5, rx=8))
    frags.append(text(245, 155, "Крок 1: Артур (Випадковий виклик)", size=14, bold=True, color="#1e3a8a"))
    frags.append(mtext(245, 205, "1. Обирає монетку b ∈ {0, 1} випадково\n2. Обирає випадкову перестановку π ∈ Sₙ\n3. Будує граф H = π(G_b)\n4. Надсилає H Мерліну", size=12, color="#1e3a8a"))

    # Стрілка Артур -> Мерлін
    frags.append(arrow(440, 200, 490, 200, color=COLOR_LINE, sw=2))
    frags.append(text(465, 185, "Граф H", size=12, bold=True, color=COLOR_LINE))

    # Крок 2: Мерлін розпізнає граф
    frags.append(rect(500, 130, 390, 140, fill=COLOR_MERLIN, stroke=COLOR_MERLIN_BORDER, sw=1.5, rx=8))
    frags.append(text(695, 155, "Крок 2: Мерлін (Обчислення)", size=14, bold=True, color="#7c2d12"))
    frags.append(mtext(695, 205, "1. Отримує граф H від Артура\n2. Використовує нескінченні ресурси,\n   щоб визначити, чи H ≅ G₀ чи H ≅ G₁\n3. Відсилає відповідь b' ∈ {0, 1}", size=12, color="#7c2d12"))

    # Стрілка Мерлін -> Артур
    frags.append(arrow(490, 240, 440, 240, color=COLOR_LINE, sw=2))
    frags.append(text(465, 255, "Індекс b'", size=12, bold=True, color=COLOR_LINE))

    # Крок 3: Вердикт Артура
    frags.append(rect(170, 310, 600, 140, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(470, 335, "Крок 3: Вердикт Артура (Прийняття рішення)", size=14, bold=True, color="#0f172a"))
    frags.append(text(470, 365, "Артур приймає доказ тоді і тільки тоді, коли b' == b", size=13, bold=True, color="#059669"))

    # Аналіз імовірностей
    frags.append(rect(190, 385, 270, 50, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER, sw=1, rx=6))
    frags.append(text(325, 405, "Якщо G₀ ≇ G₁: Pr[Accept] = 1.0", size=12, bold=True, color="#065f46"))
    frags.append(text(325, 423, "(Графи неізоморфні, Мерлін не помиляється)", size=10, italic=True, color="#065f46"))

    frags.append(rect(480, 385, 270, 50, fill="#fee2e2", stroke="#dc2626", sw=1, rx=6))
    frags.append(text(615, 405, "Якщо G₀ ≅ G₁: Pr[Accept] = 0.5", size=12, bold=True, color="#991b1b"))
    frags.append(text(615, 423, "(Графи ізоморфні, H ≅ G₀ ≅ G₁, вгадування)", size=10, italic=True, color="#991b1b"))

    render(os.path.join(IMG, "fig2-gni-am-protocol.svg"), W, H, *frags)


def fig3_complexity_landscape():
    """Фігура 3: Ієрархія класів складності навколо Arthur-Merlin ігор та IP."""
    W, H = 940, 520
    frags = []

    # Заголовок
    t_box, _, _ = textbox(470, 35, "Місце класів MA та AM у ландшафті теорії складності",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Велика зовнішня область PSPACE = IP
    frags.append(rect(40, 75, 860, 410, fill="#f8fafc", stroke="#64748b", sw=2, rx=12))
    frags.append(text(470, 102, "Класи IP = PSPACE (Інтерактивні доведення з поліномною кількістю раундів)", size=14, bold=True, color="#334155"))

    # Область PH (Поліноміальна ієрархія)
    frags.append(rect(70, 120, 800, 345, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=10))
    frags.append(text(470, 145, "Поліноміальна ієрархія (PH) та рівень Σ₂ᵖ ∩ Π₂ᵖ", size=13, bold=True, color="#1e293b"))

    # Область AM
    frags.append(rect(100, 165, 740, 280, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(470, 190, "Клас AM (Arthur-Merlin games, публічні монети, 2 раунди)", size=14, bold=True, color="#0369a1"))
    frags.append(text(470, 208, "Також AM = AM[k] = IP[k] для будь-якої сталої кількості раундів k ≥ 2", size=11, italic=True, color="#0284c7"))

    # Область MA
    frags.append(rect(140, 225, 660, 200, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(470, 250, "Клас MA (Merlin-Arthur, приватні монети, 2 раунди)", size=13, bold=True, color="#b45309"))

    # Вкладені класи NP та BPP
    frags.append(rect(180, 275, 270, 135, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(text(315, 300, "Клас NP (Сертифікати)", size=13, bold=True, color="#991b1b"))
    frags.append(mtext(315, 345, "Детермінована перевірка\nдетермінованого свідка\nNP ⊆ MA", size=11, color="#991b1b"))

    frags.append(rect(490, 275, 270, 135, fill="#d1fae5", stroke="#059669", sw=1.5, rx=6))
    frags.append(text(625, 300, "Клас BPP (Імовірнісні P)", size=13, bold=True, color="#065f46"))
    frags.append(mtext(625, 345, "Ймовірнісний верифікатор\nбез доводжувача\nBPP ⊆ MA", size=11, color="#065f46"))

    render(os.path.join(IMG, "fig3-complexity-landscape.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_ma_vs_am()
    fig2_gni_am_protocol()
    fig3_complexity_landscape()
    print("Всі фігури успішно згенеровано у", IMG)
