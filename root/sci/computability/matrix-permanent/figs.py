# -*- coding: utf-8 -*-
"""Фігури для теми «Перманент матриці та складність обчислення»
(book/algorithms/complexity-computability/matrix-permanent)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_det_vs_perm():
    """Визначник vs Перманент: порівняння алгебраїчних властивостей та складності."""
    W, H = 1140, 480
    frags = []
    lx, rx = 300, 840
    frags.append(line(570, 60, 570, 340, color="#d5dbe2", sw=2, dash="7 7"))

    # Headers
    frags.append(textbox(lx, 82, "Визначник   det(A)", size=16, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)[0])
    frags.append(textbox(rx, 82, "Перманент   perm(A)", size=16, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.4, pad=13)[0])

    # Formulas
    frags.append(textbox(lx, 158, "det(A) = Σσ sgn(σ) · ∏ᵢ a[i, σ(i)]",
                         size=15, bold=True, fill=BG, stroke="#c7ced6", sw=1.6, pad=13)[0])
    frags.append(textbox(rx, 158, "perm(A) = Σσ ∏ᵢ a[i, σ(i)]",
                         size=15, bold=True, fill=BG, stroke="#c7ced6", sw=1.6, pad=13)[0])

    # Annotations
    frags.append(mtext(lx, 220, ["знак sgn(σ) = ±1 занулює поправки",
                                 "при додаванні однакових рядків"],
                       size=13, color=NEG, bold=True))
    frags.append(mtext(rx, 220, ["відсутність знаку sgn(σ) унеможливлює",
                                 "занулення поправок методом Гаусса"],
                       size=13, color=POS, bold=True))

    # Consequences
    frags.append(textbox(lx, 310, "Метод Гаусса: O(n³) ∈ P", size=15, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)[0])
    frags.append(textbox(rx, 310, "#P-повна задача (Валіант, 1979)", size=15, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.4, pad=13)[0])

    # Bottom summary
    band, _, _ = textbox(W / 2, 415,
                         "Зникнення одного знаку sgn(σ) руйнує знакозмінну симетрію і перетворює поліноміальну задачу O(n³) на #P-повне обчислення.",
                         size=14, bold=True, fill="#f4f6f8", stroke="#b0bec5", sw=1.8, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "permanent-definition.svg"), W, H, *frags,
           title="Визначник vs Перманент: порівняння алгебраїчних властивостей та складності")


def fig_valiant_gadgets():
    """Схема гаджетного зведення Валіанта від 3SAT до 0/1-перманента."""
    W, H = 1180, 480
    frags = []

    # Title / Top box
    tbox, _, _ = textbox(W / 2, 45, "Зведення Валіанта (1979): 3SAT ⟶ 0/1-перманент",
                         size=16, bold=True, fill="#eef2f7", stroke="#4a6572", sw=2, pad=12)
    frags.append(tbox)

    # 3 Column boxes representing reduction stages
    x1, x2, x3 = 180, 590, 1000
    y_center = 230
    box_w, box_h = 260, 220

    # Stage 1: 3SAT Formula
    frags.append(rect(x1 - box_w // 2, y_center - box_h // 2, box_w, box_h, fill="#ffffff", stroke="#2b5b84", sw=2, rx=8))
    frags.append(mtext(x1, y_center - 70, ["Булева формула 3SAT", "φ = C₁ ∧ C₂ ∧ ... ∧ Cₘ"], size=15, bold=True, color="#2b5b84"))
    frags.append(mtext(x1, y_center + 10, ["• Змінні x₁, x₂, ..., xₙ", "• Клози Cⱼ = (l₁ ∨ l₂ ∨ l₃)", "• Питання: N(φ) > 0?"], size=13, color="#333333"))

    # Stage 2: Gadget Graph Construction
    frags.append(rect(x2 - box_w // 2, y_center - box_h // 2, box_w, box_h, fill="#ffffff", stroke="#e08a1e", sw=2, rx=8))
    frags.append(mtext(x2, y_center - 70, ["Зважений граф G", "Гаджети змінових і клозів"], size=15, bold=True, color="#e08a1e"))
    frags.append(mtext(x2, y_center + 10, ["• Гаджет змінної (2 цикли)", "• Гаджет клозу (3 входи)", "• Перехідні фільтри (-1, 2)"], size=13, color="#333333"))

    # Stage 3: 0/1 Adjacency Matrix
    frags.append(rect(x3 - box_w // 2, y_center - box_h // 2, box_w, box_h, fill="#ffffff", stroke="#27ae60", sw=2, rx=8))
    frags.append(mtext(x3, y_center - 70, ["0/1 Матриця суміжності A", "Розбиття вершин та mod M"], size=15, bold=True, color="#27ae60"))
    frags.append(mtext(x3, y_center + 10, ["• Розщеплення вершин", "• perm(A) mod M = N(φ)·k", "• Точний підрахунок"], size=13, color="#333333"))

    # Connecting arrows
    frags.append(arrow(x1 + box_w // 2 + 10, y_center + 30, x2 - box_w // 2 - 10, y_center + 30, color="#e08a1e", sw=2.5))
    frags.append(arrow(x2 + box_w // 2 + 10, y_center + 30, x3 - box_w // 2 - 10, y_center + 30, color="#27ae60", sw=2.5))

    # Labels on arrows positioned well clear of the arrows
    frags.append(mtext((x1 + x2) // 2, y_center - 15, ["побудова", "гаджетів"], size=12, color="#7f8c8d", bold=True))
    frags.append(mtext((x2 + x3) // 2, y_center - 15, ["заміна ваг", "0/1-елементами"], size=12, color="#7f8c8d", bold=True))

    # Bottom summary
    band, _, _ = textbox(W / 2, 415,
                         "Валіант довів: число покриттів циклами у побудованому графі дорівнює perm(A), що вимірює число виконуючих наборів 3SAT.",
                         size=14, bold=True, fill="#f4f6f8", stroke="#b0bec5", sw=1.8, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "valiant-gadget-reduction.svg"), W, H, *frags,
           title="Зведення Валіанта (1979): 3SAT ⟶ 0/1-перманент")


def fig_ryser_inclusion_exclusion():
    """Схематичне зображення принципу включень-виключень Райзера та коду Ґрея."""
    W, H = 1080, 480
    frags = []

    # Title
    tbox, _, _ = textbox(W / 2, 45, "Формула Райзера: включення-виключення та код Ґрея",
                         size=16, bold=True, fill="#eef2f7", stroke="#4a6572", sw=2, pad=12)
    frags.append(tbox)

    # Left: Subset Inclusion-Exclusion
    lx = 290
    frags.append(rect(lx - 230, 220 - 115, 460, 230, fill="#ffffff", stroke="#2980b9", sw=2, rx=8))
    frags.append(mtext(lx, 130, ["Суми по підмножинах стовпців S ⊆ {1, ..., n}"], size=15, bold=True, color="#2980b9"))
    frags.append(mtext(lx, 210, [
        "• Розгляд усіх 2ⁿ підмножин стовпців S",
        "• Сума рядків P(S) = ∏ᵢ (∑ⱼ∈S a[i,j])",
        "• Знакозмінний коефіцієнт (-1)|S| відсіває небієктивні відображення",
        "• Залишається точно n! трансверсалей = perm(A)"
    ], size=13, color="#2c3e50"))

    # Right: Gray Code Optimization
    rx = 790
    frags.append(rect(rx - 230, 220 - 115, 460, 230, fill="#ffffff", stroke="#27ae60", sw=2, rx=8))
    frags.append(mtext(rx, 130, ["Оптимізація кодом Ґрея: з O(2ⁿ·n) до O(2ⁿ)"], size=15, bold=True, color="#27ae60"))
    frags.append(mtext(rx, 210, [
        "• Послідовність підмножин змінюється лише на 1 біт",
        "• Оновлення векторів суми рядків за O(1) додавання/віднімання",
        "• Загальна складність O(2ⁿ n) скорочується до O(2ⁿ)",
        "• Практична межа: n ≈ 30...40 замість n = 12"
    ], size=13, color="#2c3e50"))

    # Arrow connecting left to right
    frags.append(arrow(520, 220, 560, 220, color="#27ae60", sw=3))

    # Bottom note
    band, _, _ = textbox(W / 2, 415,
                         "Формула Райзера замінює n! перестановок сумуванням по 2ⁿ підмножинах. Код Ґрея робить кожен крок за O(1).",
                         size=14, bold=True, fill="#f4f6f8", stroke="#b0bec5", sw=1.8, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "ryser-inclusion-exclusion.svg"), W, H, *frags,
           title="Формула Райзера: включення-виключення та код Ґрея")


def fig_quantum_boson_sampling():
    """Бозонний семплінг: фізична інтерферометрія та обчислення перманентів."""
    W, H = 1080, 480
    frags = []

    # Title
    tbox, _, _ = textbox(W / 2, 45, "Бозонний семплінг Ааронсона-Архіпова (2011)",
                         size=16, bold=True, fill="#eef2f7", stroke="#4a6572", sw=2, pad=12)
    frags.append(tbox)

    # 3 Stage Boxes
    x1, x2, x3 = 190, 540, 890
    y_c = 220
    w_box, h_box = 270, 220

    # Photons Input
    frags.append(rect(x1 - w_box // 2, y_c - h_box // 2, w_box, h_box, fill="#ffffff", stroke="#8e44ad", sw=2, rx=8))
    frags.append(mtext(x1, y_c - 70, ["Однофотонні джерела", "n фотонів у m модах"], size=15, bold=True, color="#8e44ad"))
    frags.append(mtext(x1, y_c + 10, ["• Нерозрізнені бозони", "• Початковий стан |1,1,...,0,0⟩", "• Симетрія квантових станів"], size=13, color="#333333"))

    # Interferometer
    frags.append(rect(x2 - w_box // 2, y_c - h_box // 2, w_box, h_box, fill="#ffffff", stroke="#d35400", sw=2, rx=8))
    frags.append(mtext(x2, y_c - 70, ["Лінійний інтерферометр", "Унітарна матриця U (m×m)"], size=15, bold=True, color="#d35400"))
    frags.append(mtext(x2, y_c + 10, ["• Дільники променя та фазообертачі", "• Квантова інтерференція", "• Матричні елементи U[i,j]"], size=13, color="#333333"))

    # Output probabilities & Permanent
    frags.append(rect(x3 - w_box // 2, y_c - h_box // 2, w_box, h_box, fill="#ffffff", stroke="#c0392b", sw=2, rx=8))
    frags.append(mtext(x3, y_c - 70, ["Амплітуда і Перманент", "P(S→T) = |perm(U_{S,T})|²"], size=15, bold=True, color="#c0392b"))
    frags.append(mtext(x3, y_c + 10, ["• Амплітуда = perm(U_{S,T})", "• #P-важкість класичної імітації", "• Квантова перевага над суперкомп'ютером"], size=13, color="#333333"))

    # Arrows
    frags.append(arrow(x1 + w_box // 2 + 10, y_c, x2 - w_box // 2 - 10, y_c, color="#d35400", sw=2.5))
    frags.append(arrow(x2 + w_box // 2 + 10, y_c, x3 - w_box // 2 - 10, y_c, color="#c0392b", sw=2.5))

    # Bottom summary
    band, _, _ = textbox(W / 2, 415,
                         "Імовірність виявлення фотонів на виході інтерферометра пропорційна квадрату модуля перманента підматриці U.",
                         size=14, bold=True, fill="#f4f6f8", stroke="#b0bec5", sw=1.8, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "quantum-boson-sampling.svg"), W, H, *frags,
           title="Бозонний семплінг Ааронсона-Архіпова (2011)")


if __name__ == "__main__":
    fig_det_vs_perm()
    fig_valiant_gadgets()
    fig_ryser_inclusion_exclusion()
    fig_quantum_boson_sampling()
    print("Всі 4 фігури згенеровано успішно.")
