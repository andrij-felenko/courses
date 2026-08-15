# -*- coding: utf-8 -*-
"""Фігури для теми «Криптографічне зобов'язання» (book/algorithms/complexity-computability/cryptographic-commitment)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_BG = "#ffffff"
COLOR_HEADER = "#e2e8f0"
COLOR_PROVER = "#dbeafe"       # синій для Доводжувача (Alice)
COLOR_PROVER_BORDER = "#2563eb"
COLOR_VERIFIER = "#fef3c7"     # жовтий для Верифікатора (Bob)
COLOR_VERIFIER_BORDER = "#d97706"
COLOR_MATH = "#f3e8ff"         # фіолетовий для математичних операцій
COLOR_MATH_BORDER = "#7e22ce"
COLOR_SUCCESS = "#d1fae5"      # зелений для Результату / Перевірки
COLOR_SUCCESS_BORDER = "#059669"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_commitment_two_phases():
    """Фігура 1: Двофазна архітектура схеми криптографічного зобов'язання (Commit та Open)."""
    W, H = 940, 480
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(470, 30, "Двофазна архітектура схеми криптографічного зобов'язання",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва панель — Фаза 1: Зобов'язання (Commit Phase)
    frags.append(rect(25, 70, 430, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(240, 95, "Фаза 1: Зобов'язання (Commit Phase)", size=14, bold=True, color="#1e3a8a"))
    frags.append(text(240, 112, "Приховування: Верифікатор не бачить m", size=10.5, italic=True, color=COLOR_MUTED))

    # Стовпчики Alice та Bob у Фазі 1
    frags.append(textbox(115, 155, "Аліса (Доводжувач)\nПовідомлення: m\nВипадковість: r", size=10.5, bold=True, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(365, 155, "Боб (Верифікатор)\nОтримує c\nНе знає m та r", size=10.5, bold=True, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    # Крок 1 у Фазі 1
    frags.append(textbox(115, 235, "c = Commit(m, r)\n(Обчислення)", size=10.5, fill="#ffffff", stroke=COLOR_PROVER_BORDER)[0])
    frags.append(arrow(185, 235, 295, 235, color=COLOR_LINE, sw=1.8))
    frags.append(text(240, 222, "Передача c", size=10, bold=True, color="#1e3a8a"))

    # Властивість Приховування (Hiding)
    frags.append(textbox(240, 315, "Властивість Приховування (Hiding):\nНеможливо обчислити m з c\nPr[Bob вгадає m] = 1 / |M|", size=10, bold=True, fill=COLOR_MATH, stroke=COLOR_MATH_BORDER)[0])

    # Стан Боба після Фази 1
    frags.append(textbox(365, 400, "Зафіксовано c\nm залишається в таємниці", size=10, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])


    # Права панель — Фаза 2: Відкриття (Reveal / Open Phase)
    frags.append(rect(485, 70, 430, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(700, 95, "Фаза 2: Відкриття (Reveal Phase)", size=14, bold=True, color="#5b21b6"))
    frags.append(text(700, 112, "Зв'язування: Аліса не змінить m на m'", size=10.5, italic=True, color=COLOR_MUTED))

    # Стовпчики Alice та Bob у Фазі 2
    frags.append(textbox(575, 155, "Аліса (Доводжувач)\nВідкриває секрет\nПересилає (m, r)", size=10.5, bold=True, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(825, 155, "Боб (Верифікатор)\nПеревіряє c =?= Commit(m, r)", size=10.5, bold=True, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    # Крок 2 у Фазі 2
    frags.append(arrow(645, 235, 755, 235, color=COLOR_LINE, sw=1.8))
    frags.append(text(700, 222, "Відкриття (m, r)", size=10, bold=True, color="#5b21b6"))

    # Властивість Зв'язування (Binding)
    frags.append(textbox(700, 315, "Властивість Зв'язування (Binding):\nАліса не може знайти (m', r')\nтакі що Commit(m', r') = c", size=10, bold=True, fill=COLOR_MATH, stroke=COLOR_MATH_BORDER)[0])

    # Результат перевірки
    frags.append(textbox(825, 400, "Open(c, m, r) = 1\n(Успішна верифікація)", size=10, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])

    render(os.path.join(IMG, "fig1-commitment-two-phases.svg"), W, H, *frags)


def fig2_pedersen_homomorphic_tx():
    """Фігура 2: Гомоморфне додавання зобов'язань Педерсена у конфіденційних транзакціях."""
    W, H = 940, 440
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(470, 30, "Гомоморфне додавання зобов'язань Педерсена в балансі транзакцій",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва частина: Вхідні зобов'язання (Inputs)
    frags.append(rect(30, 75, 270, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(165, 105, "Входи транзакції (Inputs)", size=13, bold=True, color="#1e3a8a"))

    frags.append(textbox(165, 160, "Вхід 1: v₁ = 50, r₁\nC₁ = g⁵⁰ · hʳ¹ mod p", size=10.5, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(text(165, 220, "+", size=18, bold=True, color=COLOR_LINE))
    frags.append(textbox(165, 270, "Вхід 2: v₂ = 30, r₂\nC₂ = g³⁰ · hʳ² mod p", size=10.5, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])

    frags.append(textbox(165, 360, "Сума входів: C_in = C₁ · C₂\nC_in = g⁸⁰ · hʳ¹⁺ʳ² mod p", size=10.5, bold=True, fill=COLOR_MATH, stroke=COLOR_MATH_BORDER)[0])

    # Стрелка переходу
    frags.append(arrow(310, 240, 360, 240, color=COLOR_LINE, sw=2.0))
    frags.append(text(335, 225, "≡", size=20, bold=True, color=COLOR_LINE))

    # Права частина: Вихідні зобов'язання (Outputs)
    frags.append(rect(370, 75, 270, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(505, 105, "Виходи транзакції (Outputs)", size=13, bold=True, color="#5b21b6"))

    frags.append(textbox(505, 160, "Вихід 1: v₃ = 70, r₃\nC₃ = g⁷⁰ · hʳ³ mod p", size=10.5, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(text(505, 220, "+", size=18, bold=True, color=COLOR_LINE))
    frags.append(textbox(505, 270, "Комісія: v_fee = 10, r_fee = 0\nC_fee = g¹⁰ mod p", size=10.5, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])

    frags.append(textbox(505, 360, "Сума виходів: C_out = C₃ · C_fee\nC_out = g⁸⁰ · hʳ³ mod p", size=10.5, bold=True, fill=COLOR_MATH, stroke=COLOR_MATH_BORDER)[0])

    # Нижня перевірка балансу
    frags.append(rect(660, 75, 250, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(785, 105, "Перевірка балансу", size=13, bold=True, color="#047857"))

    frags.append(textbox(785, 180, "За умови: r₁ + r₂ = r₃\nC_in / C_out = g⁰ · h⁰ = 1", size=10.5, bold=True, fill="#ffffff", stroke="#059669")[0])

    frags.append(textbox(785, 300, "Верифікація збереження маси:\n∑ v_in = ∑ v_out + fee\nБЕЗ розголошення значень v_i!", size=10, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])

    render(os.path.join(IMG, "fig1-commitment-two-phases.svg"), W, H, *frags)


def fig3_commitment_comparison():
    """Фігура 3: Порівняльний аналіз основних схем криптографічного зобов'язання."""
    W, H = 940, 450
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(470, 30, "Порівняльний аналіз архітектур криптографічних зобов'язань",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Схема 1: Хеш-зобов'язання
    frags.append(rect(25, 70, 210, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(130, 98, "Хеш-зобов'язання", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(130, 118, "c = H(m || r)", size=11, bold=True, color=COLOR_MUTED))
    frags.append(textbox(130, 175, "Приховування:\nОбчислювальне\n(Random Oracle)", size=10, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(130, 250, "Зв'язування:\nОбчислювальне\n(Стійкість до колізій)", size=10, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(textbox(130, 345, "Властивості:\n• Розмір доказу: O(1)\n• Гомоморфізм: Відсутній\n• Квантова стійкість: Так", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])

    # Схема 2: Зобов'язання Педерсена
    frags.append(rect(250, 70, 210, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(355, 98, "Схема Педерсена", size=13, bold=True, color="#5b21b6"))
    frags.append(text(355, 118, "c = gᵐ · hʳ mod p", size=11, bold=True, color=COLOR_MUTED))
    frags.append(textbox(355, 175, "Приховування:\nБЕЗУМОВНЕ\n(Інформаційно-теоретичне)", size=10, bold=True, fill=COLOR_SUCCESS, stroke=COLOR_SUCCESS_BORDER)[0])
    frags.append(textbox(355, 250, "Зв'язування:\nОбчислювальне\n(Важкість дискр. логарифма)", size=10, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(textbox(355, 345, "Властивості:\n• Розмір доказу: O(1)\n• Гомоморфізм: Адитивний\n• Квантова стійкість: Ні", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])

    # Схема 3: Поліноміальне KZG
    frags.append(rect(475, 70, 210, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(580, 98, "Схема KZG (Kate)", size=13, bold=True, color="#991b1b"))
    frags.append(text(580, 118, "C = g^{f(α)} ∈ G₁", size=11, bold=True, color=COLOR_MUTED))
    frags.append(textbox(580, 175, "Приховування:\nОбчислювальне\n(Захист випадковістю)", size=10, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(580, 250, "Зв'язування:\nОбчислювальне\n(q-SBDH припущення)", size=10, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(textbox(580, 345, "Властивості:\n• Оцінка полінома: O(1)\n• Потрібен Trusted Setup\n• Гомоморфізм: Линійний", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])

    # Схема 4: Дерева Меркла (Vector Commitment)
    frags.append(rect(700, 70, 215, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(807, 98, "Дерево Меркла", size=13, bold=True, color="#047857"))
    frags.append(text(807, 118, "Root = H(... H(v₁)...)", size=11, bold=True, color=COLOR_MUTED))
    frags.append(textbox(807, 175, "Приховування:\nНі (без blinding factor)\nАбо опціональне", size=10, fill=COLOR_PROVER, stroke=COLOR_PROVER_BORDER)[0])
    frags.append(textbox(807, 250, "Зв'язування:\nОбчислювальне\n(Стійкість до колізій)", size=10, fill=COLOR_VERIFIER, stroke=COLOR_VERIFIER_BORDER)[0])
    frags.append(textbox(807, 345, "Властивості:\n• Розмір відкриття: O(log N)\n• Зауваження: Поклітинне\n• Без Trusted Setup", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])

    render(os.path.join(IMG, "fig3-commitment-comparison.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_commitment_two_phases()
    fig2_pedersen_homomorphic_tx()
    fig3_commitment_comparison()
    print("Усі 3 фігури успішно згенеровано у ./img/")
