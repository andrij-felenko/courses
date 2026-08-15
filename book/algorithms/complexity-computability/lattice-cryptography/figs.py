# -*- coding: utf-8 -*-
"""Фігури для теми «Решіткова криптографія» (book/algorithms/complexity-computability/lattice-cryptography)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_lattice_basis():
    """Порівняння поганого й хорошого базису решітки: СВП та стрічка шифрування."""
    W, H = 1080, 520
    frags = []

    # Тло двох панелей
    frags.append(rect(40, 50, 480, 430, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=12))
    frags.append(rect(560, 50, 480, 430, fill="#f8fafc", stroke="#cbd5e1", sw=2, rx=12))

    frags.append(text(280, 85, "Поганий базис (вузький кут, довгі вектори)", size=16, bold=True, color=POS))
    frags.append(text(800, 85, "Хороший (редукований) базис (майже ортогональний)", size=16, bold=True, color=FIELD))

    ox1, oy1 = 200, 330
    v1 = (140, 30)   # довгий
    v2 = (170, 130)  # довгий під гострим кутом

    # Вузли решітки для лівої панелі
    for i in range(-2, 3):
        for j in range(-2, 3):
            px = ox1 + i * 70 + j * 40
            py = oy1 - i * 20 - j * 80
            if 55 <= px <= 505 and 105 <= py <= 465:
                frags.append(circle(px, py, 3.5, fill="#64748b", stroke="none", sw=0))

    # Вектори v1, v2 (поганий базис)
    frags.append(arrow(ox1, oy1, ox1 + v1[0], oy1 - v1[1], color=POS, sw=3))
    frags.append(text(ox1 + v1[0] + 15, oy1 - v1[1] - 5, "b₁ (поганий)", size=14, bold=True, color=POS))
    frags.append(arrow(ox1, oy1, ox1 + v2[0], oy1 - v2[1], color=POS, sw=3))
    frags.append(text(ox1 + v2[0] + 15, oy1 - v2[1] + 15, "b₂ (поганий)", size=14, bold=True, color=POS))

    # Найкоротший вектор v_short = v2 - v1 = (30, 100)
    frags.append(arrow(ox1, oy1, ox1 + 30, oy1 - 100, color=FIELD, sw=3))
    frags.append(text(ox1 + 35, oy1 - 110, "v_short (СВП)", size=13, bold=True, color=FIELD))

    # Пояснення лівої панелі
    frags.append(text(280, 445, "СВП важка: v_short не збігається з базисом", size=13, bold=True, color=MUTED))

    # Права панель — хороший базис
    ox2, oy2 = 720, 330
    u1 = (110, 10)  # короткий
    u2 = (30, 100)  # короткий, майже ортогональний

    for i in range(-2, 3):
        for j in range(-2, 3):
            px = ox2 + i * u1[0] + j * u2[0]
            py = oy2 - i * u1[1] - j * u2[1]
            if 575 <= px <= 1025 and 105 <= py <= 465:
                frags.append(circle(px, py, 3.5, fill="#64748b", stroke="none", sw=0))

    frags.append(arrow(ox2, oy2, ox2 + u1[0], oy2 - u1[1], color=FIELD, sw=3))
    frags.append(text(ox2 + u1[0] + 10, oy2 - u1[1] + 15, "e₁ (ортогональний)", size=14, bold=True, color=FIELD))
    frags.append(arrow(ox2, oy2, ox2 + u2[0], oy2 - u2[1], color=FIELD, sw=3))
    frags.append(text(ox2 + u2[0] + 10, oy2 - u2[1] - 5, "e₂ (ортогональний)", size=14, bold=True, color=FIELD))

    frags.append(text(800, 445, "СВП легка: найкоротший вектор — це і є базис", size=13, bold=True, color=FIELD))

    render(os.path.join(IMG, "lattice-basis.svg"), W, H, *frags,
           title="Поганий проти хорошим базисом решітки: основа стійкості")


def fig_lwe_decryption():
    """Геометрія LWE шифрування та зняття шуму при декодуванні."""
    W, H = 1040, 420
    frags = []

    # Смуга значень mod q
    y_line = 180
    x_start, x_end = 100, 940
    frags.append(line(x_start, y_line, x_end, y_line, color=INK, sw=3))

    # Риски інтервалу
    frags.append(line(x_start, y_line - 15, x_start, y_line + 15, color=INK, sw=2.5))
    frags.append(text(x_start, y_line + 38, "0", size=15, bold=True))

    x_mid = (x_start + x_end) / 2
    frags.append(line(x_mid, y_line - 15, x_mid, y_line + 15, color=INK, sw=2.5))
    frags.append(text(x_mid, y_line + 38, "q / 2", size=15, bold=True))

    frags.append(line(x_end, y_line - 15, x_end, y_line + 15, color=INK, sw=2.5))
    frags.append(text(x_end, y_line + 38, "q", size=15, bold=True))

    # Зона біта 0 (біля 0 та q)
    frags.append(rect(x_start, y_line - 35, 160, 70, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(x_start + 80, y_line - 45, "Зона біта 0", size=13, bold=True, color=FIELD))

    # Зона біта 1 (біля q/2)
    frags.append(rect(x_mid - 120, y_line - 35, 240, 70, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(x_mid, y_line - 45, "Зона біта 1", size=13, bold=True, color=NEG))

    # Повідомлення 1 -> m * (q/2)
    frags.append(circle(x_mid, y_line, 6, fill=NEG, stroke=NEG, sw=2))
    frags.append(text(x_mid, y_line - 15, "m · ⌊q/2⌋", size=14, bold=True, color=NEG))

    # Точка з шумом: m*(q/2) + e
    x_noisy = x_mid + 45
    frags.append(arrow(x_mid, y_line - 60, x_noisy, y_line - 60, color=AMBER_S, sw=2.5))
    frags.append(text(x_mid + 22, y_line - 75, "Шум e (малий)", size=13, bold=True, color=AMBER_S))

    frags.append(circle(x_noisy, y_line, 7, fill=AMBER_S, stroke=INK, sw=2))
    frags.append(text(x_noisy + 10, y_line + 25, "c₂ - ⟨c₁, s⟩ = m·⌊q/2⌋ + e", size=14, bold=True, color=INK))

    # Стрілка округлення
    frags.append(arrow(x_noisy, y_line + 65, x_mid, y_line + 65, color=FIELD, sw=2.5))
    frags.append(text(x_mid + 30, y_line + 85, "Округлення до найближчого (0 чи q/2) -> біт 1", size=13, bold=True, color=FIELD))

    # Висновок
    band, _, _ = textbox(520, 365,
                         "Декодування успішне, якщо шум |e| < q / 4. Помилка усувається округленням до точки решітки.",
                         size=14, bold=True, fill="#fff6e5", stroke="#e08a1e", sw=2, pad=12)
    frags.append(band)

    render(os.path.join(IMG, "lwe-decryption.svg"), W, H, *frags,
           title="Механізм декодування LWE: зняття шуму округленням")


def fig_reduction_worst_to_average():
    """Схема зведення Аптая: найгірший випадок СВП -> середній випадок SIS/LWE."""
    W, H = 1000, 360
    yr = 140
    frags = []

    b1, w1, _ = textbox(160, yr, "Найгірший випадок\n(Worst-case SIVP/SVP)\nв БУДЬ-ЯКІЙ решітці", size=15, bold=True,
                        fill="#fdecea", stroke=POS, sw=2.2, pad=14)
    b2, w2, _ = textbox(500, yr, "Теорема Аптая / Реґева\n(Квантове / класичне\nзведення)", size=15, bold=True,
                        fill="#fff6e5", stroke=AMBER_S, sw=2.5, pad=14)
    b3, w3, _ = textbox(840, yr, "Середній випадок\n(Average-case SIS/LWE)\nдля випадкової матриці A", size=15, bold=True,
                        fill="#e9f7ef", stroke=FIELD, sw=2.2, pad=14)

    frags += [b1, b2, b3]

    # Стрілка зведення (ліворуч вправо)
    frags.append(arrow(160 + w1/2 + 5, yr, 500 - w2/2 - 5, yr, color=INK, sw=2.5))
    frags.append(arrow(500 + w2/2 + 5, yr, 840 - w3/2 - 5, yr, color=INK, sw=2.5))

    # Стрілка гарантії стійкості (праворуч вліво)
    hy = 260
    frags.append(arrow(840 - w3/2, hy, 160 + w1/2, hy, color=POS, sw=2.5))
    frags.append(text(500, hy - 14, "Гарантія безпеки: зламати випадковий екземпляр = розв'язати найважчу решітку",
                      size=13, bold=True, color=POS))

    band, _, _ = textbox(500, 320,
                         "Фундаментальний прорив: на відміну від RSA, стійкість не залежить від 'вдалого' вибору ключів.",
                         size=14, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, pad=12)
    frags.append(band)

    render(os.path.join(IMG, "reduction-worst-to-average.svg"), W, H, *frags,
           title="Зведення від найгіршого до середнього випадку в решітках")


if __name__ == "__main__":
    fig_lattice_basis()
    fig_lwe_decryption()
    fig_reduction_worst_to_average()
    print("OK:", sorted(os.listdir(IMG)))
