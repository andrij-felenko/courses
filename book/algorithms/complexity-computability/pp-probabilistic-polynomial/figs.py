# -*- coding: utf-8 -*-
"""Фігури для теми «Клас PP: ймовірнісний поліноміальний час»
(book/algorithms/complexity-computability/pp-probabilistic-polynomial)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_pp_vs_bpp_threshold():
    """Порівняння порогів прийняття в BPP (обмежена хиба) та PP (необмежений поріг)."""
    W, H = 1140, 520
    frags = []
    lx, rx = 300, 840  # центри панелей

    frags.append(line(570, 50, 570, 390, color="#d5dbe2", sw=2, dash="7 7"))

    # Заголовки панелей
    frags.append(textbox(lx, 75, "Клас BPP: обмежена хиба", size=16, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)[0])
    frags.append(textbox(rx, 75, "Клас PP: необмежений поріг", size=16, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.4, pad=13)[0])

    # Вісь імовірностей для BPP (ліво)
    frags.append(line(120, 310, 480, 310, color="#333", sw=2))  # вісь
    frags.append(rect(140, 290, 100, 40, rx=4, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(190, 315, ["x ∉ L: ≤ 1/3"], size=12, bold=True, color=POS))

    frags.append(rect(340, 290, 100, 40, rx=4, fill="#e9f7ef", stroke=FIELD, sw=1.5))
    frags.append(mtext(390, 315, ["x ∈ L: ≥ 2/3"], size=12, bold=True, color=FIELD))

    # Гарантований зазор (gap)
    frags.append(arrow(240, 260, 335, 260, color="#27ae60", sw=2.5))
    frags.append(mtext(290, 240, ["зазор ε ≥ 1/poly(n)"], size=12, bold=True, color="#27ae60"))

    frags.append(mtext(lx, 160, ["Мажоритарне голосування зменшує",
                                "хибу до 2⁻ᵏ за поліноміальний час"],
                       size=13, color="#2c3e50", bold=True))

    # Вісь імовірностей для PP (право)
    frags.append(line(660, 310, 1020, 310, color="#333", sw=2))  # вісь
    # Порогова лінія на 1/2 (840)
    frags.append(line(840, 230, 840, 340, color="#e74c3c", sw=2, dash="4 4"))
    frags.append(mtext(840, 215, ["поріг = 1/2"], size=13, bold=True, color="#e74c3c"))

    frags.append(rect(670, 290, 165, 40, rx=4, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(752, 315, ["x ∉ L: ≤ 1/2"], size=12, bold=True, color=POS))

    frags.append(rect(845, 290, 165, 40, rx=4, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(mtext(927, 315, ["x ∈ L: > 1/2"], size=12, bold=True, color=POS))

    # Крихітний зазор
    frags.append(mtext(rx, 160, ["Зазор може бути ε = 2⁻ᵖ⁽ⁿ⁾ —",
                                "ампліфікація вимагає O(2²ᵖ⁽ⁿ⁾) випробувань"],
                       size=13, color=POS, bold=True))

    # Нижня смуга-висновок
    band, _, _ = textbox(W / 2, 445,
                         "BPP — практична ймовірність з ампліфікацією. PP — точний підрахунок більшості гілок, недосяжний для фізичного аналізу.",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "pp-vs-bpp-threshold.svg"), W, H, *frags,
           title="BPP проти PP: обмежений зазор проти порогового підрахунку")


def fig_complexity_hierarchy_pp():
    """Карта класів складності навколо PP та теорема Тоди."""
    W, H = 1140, 560
    frags = []

    frags.append(rect(40, 40, 1060, 420, rx=12, fill="#f4f6f7", stroke="#bdc3c7", sw=2))
    frags.append(mtext(570, 70, ["ІЄРАРХІЯ СКЛАДНОСТІ ТА ВМІЩЕННЯ КЛАСУ PP"], size=16, bold=True, color="#2c3e50"))

    # PSPACE зовнішній контейнер
    frags.append(rect(70, 100, 1000, 340, rx=10, fill="#ebf5fb", stroke="#2980b9", sw=2))
    frags.append(mtext(140, 125, ["PSPACE"], size=15, bold=True, color="#2980b9"))

    # P^PP = P^#P і теорема Тоди
    frags.append(rect(100, 145, 940, 275, rx=8, fill="#fdf2e9", stroke="#e67e22", sw=2))
    frags.append(mtext(240, 170, ["Pᵖᵖ = P──────── (Оракул PP / #P)"], size=14, bold=True, color="#e67e22"))
    frags.append(mtext(278, 170, ["#P"], size=14, bold=True, color="#e67e22"))

    # PP область
    frags.append(rect(120, 190, 550, 215, rx=8, fill="#fadede", stroke="#c0392b", sw=2))
    frags.append(mtext(170, 215, ["Клас PP"], size=15, bold=True, color="#c0392b"))

    # BPP в середині PP
    frags.append(rect(140, 235, 230, 150, rx=6, fill="#e8f8f5", stroke="#16a085", sw=2))
    frags.append(mtext(180, 260, ["BPP"], size=14, bold=True, color="#16a085"))

    # P в середині BPP
    frags.append(rect(160, 280, 110, 85, rx=4, fill="#d4efdf", stroke="#27ae60", sw=2))
    frags.append(mtext(215, 325, ["P"], size=15, bold=True, color="#27ae60"))

    # NP та coNP в середині PP (зовні BPP)
    frags.append(rect(390, 235, 130, 65, rx=6, fill="#fef9e7", stroke="#f39c12", sw=2))
    frags.append(mtext(455, 272, ["NP"], size=14, bold=True, color="#f39c12"))

    frags.append(rect(530, 235, 120, 65, rx=6, fill="#fef9e7", stroke="#f39c12", sw=2))
    frags.append(mtext(590, 272, ["coNP"], size=14, bold=True, color="#f39c12"))

    # PH (Поліноміальна ієрархія)
    frags.append(rect(700, 190, 320, 215, rx=8, fill="#f5eeed", stroke="#8e44ad", sw=2))
    frags.append(mtext(860, 218, ["PH (Поліноміальна ієрархія)"], size=14, bold=True, color="#8e44ad"))
    frags.append(mtext(860, 255, ["Σ₂P, Π₂P, Σ₃P, ..."], size=13, color="#8e44ad"))

    # Стрілка теореми Тоди: PH ⊆ P^PP
    frags.append(arrow(700, 310, 675, 310, color="#8e44ad", sw=2.5))
    frags.append(mtext(860, 310, ["Теорема Тоди (1989):"], size=13, bold=True, color="#8e44ad"))
    frags.append(mtext(860, 335, ["PH ⊆ Pᵖᵖ"], size=15, bold=True, color="#8e44ad"))

    # Нижня смуга
    band, _, _ = textbox(W / 2, 500,
                         "PP охоплює NP та coNP, а з детермінованим оракулом Pᵖᵖ повністю поглинає всю поліноміальну ієрархію PH.",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "complexity-hierarchy-pp.svg"), W, H, *frags,
           title="Розташування класу PP в ієрархії складності")


def fig_majsat_tree():
    """Дерево обчислень ймовірнісної Тюрінг-машини для MAJSAT (підрахунок більшості)."""
    W, H = 1140, 500
    frags = []

    frags.append(mtext(570, 45, ["Дерево обчислень ймовірнісної Тюрінг-машини (2ⁿ гілок)"],
                       size=16, bold=True, color="#2c3e50"))

    # Корінь дерева
    frags.append(textbox(570, 95, "Вхідний вираз φ(x₁, ..., xₙ)", size=14, bold=True,
                         fill="#ebf5fb", stroke="#2980b9", sw=2, pad=10)[0])

    # Рівень 1 гілкування
    frags.append(line(570, 115, 350, 165, color="#7f8c8d", sw=2))
    frags.append(line(570, 115, 790, 165, color="#7f8c8d", sw=2))

    frags.append(textbox(350, 175, "x₁ = 0 (p = 1/2)", size=12, bold=True,
                         fill="#f4f6f7", stroke="#7f8c8d", sw=1.5, pad=8)[0])
    frags.append(textbox(790, 175, "x₁ = 1 (p = 1/2)", size=12, bold=True,
                         fill="#f4f6f7", stroke="#7f8c8d", sw=1.5, pad=8)[0])

    # Рівень 2 гілкування
    frags.append(line(350, 195, 200, 245, color="#7f8c8d", sw=1.5, dash="3 3"))
    frags.append(line(350, 195, 500, 245, color="#7f8c8d", sw=1.5, dash="3 3"))
    frags.append(line(790, 195, 640, 245, color="#7f8c8d", sw=1.5, dash="3 3"))
    frags.append(line(790, 195, 940, 245, color="#7f8c8d", sw=1.5, dash="3 3"))

    # Листя (результати гілок)
    frags.append(textbox(200, 260, "Гілка 1: 1 (ПРИЙНЯТО)", size=11, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=1.5, pad=6)[0])
    frags.append(textbox(500, 260, "Гілка 2: 0 (ВІДХИЛЕНО)", size=11, bold=True,
                         fill="#fdecea", stroke=POS, sw=1.5, pad=6)[0])
    frags.append(textbox(640, 260, "Гілка 3: 1 (ПРИЙНЯТО)", size=11, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=1.5, pad=6)[0])
    frags.append(textbox(940, 260, "Гілка 4: 1 (ПРИЙНЯТО)", size=11, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=1.5, pad=6)[0])

    # Блок підрахунку під деревом
    frags.append(rect(150, 320, 840, 85, rx=8, fill="#fff6e5", stroke=AMBER_S, sw=2))
    frags.append(mtext(570, 350, ["Підрахунок гілок:  N(прийнято) = 3,  N(відхилено) = 1  (Всього = 2² = 4)"],
                       size=14, bold=True, color="#d35400"))
    frags.append(mtext(570, 380, ["Умова PP:  N(прийнято) > 2ⁿ⁻¹  =>  3 > 2  =>  ВИРАЗ НАЛЕЖИТЬ ДО MAJSAT"],
                       size=14, bold=True, color=FIELD))

    # Нижня смуга
    band, _, _ = textbox(W / 2, 455,
                         "Імовірнісна машина приймає тоді й лише тоді, коли більшість усіх обчислювальних шляхів повертають 1.",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "majsat-tree.svg"), W, H, *frags,
           title="Дерево обчислень ймовірнісної Тюрінг-машини та умова більшості")


if __name__ == "__main__":
    fig_pp_vs_bpp_threshold()
    fig_complexity_hierarchy_pp()
    fig_majsat_tree()
    print("Всі фігури згенеровано успішно.")
