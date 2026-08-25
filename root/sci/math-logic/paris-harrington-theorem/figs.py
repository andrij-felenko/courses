# -*- coding: utf-8 -*-
"""Фігури для теми «Теорема Паріса — Гаррінгтона» (book/algorithms/complexity-computability/paris-harrington-theorem)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_ramsey_vs_paris_harrington():
    """fig1-ramsey-vs-paris-harrington.svg: Порівняння класичної теореми Рамсея та підсиленого принципу Паріса — Гаррінгтона."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Розфарбування [X]ⁿ та умови монохроматичності підмножин H ⊆ X", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Класична теорема Рамсея
    frags.append(rect(30, 60, 390, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Класична скінченна теорема Рамсея", size=14, bold=True, color=BLUE_S))

    txt_r_cond = "Параметри: n (розмірність), m (поріг), c (кольори)\nВхідна множина: X = {1, 2, ..., N}"
    b_rc, _, _ = textbox(225, 130, txt_r_cond, size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_rc)

    txt_r_out = "Гарантована монохроматична підмножина H ⊆ X:\n1. Однорідне забарвлення: K([H]ⁿ) = {колір k}\n2. Вимога розміру: |H| ≥ m"
    b_ro, _, _ = textbox(225, 210, txt_r_out, size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_ro)

    txt_r_bound = "Оцінка порогу N:\n• n=2: N ≤ 2^{2m} (експоненціальна)\n• Загальне n: вежа експонент (примітивно-рекурсивна)\n• Довідність: Виводжувана у PA!"
    b_rb, _, _ = textbox(225, 305, txt_r_bound, size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_rb)

    # Права частина: Підсилений принцип Паріса — Гаррінгтона
    frags.append(rect(460, 60, 390, 330, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(655, 85, "Підсилений принцип Паріса — Гаррінгтона", size=14, bold=True, color=PURPLE_S))

    txt_ph_cond = "Параметри: n (розмірність), m (поріг), c (кольори)\nВхідна множина: X = {1, 2, ..., N}"
    b_phc, _, _ = textbox(655, 130, txt_ph_cond, size=11, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_phc)

    txt_ph_out = "Монохроматична підмножина H ⊆ X додатково ВЕЛИКА:\n1. Однорідне забарвлення: K([H]ⁿ) = {колір k}\n2. Вимога розміру: |H| ≥ m\n3. Умова великої множини: |H| ≥ min(H)"
    b_pho, _, _ = textbox(655, 215, txt_ph_out, size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_pho)

    txt_ph_bound = "Оцінка порогу N = PH(n, m, c):\n• n=2: Рівень функції Аккермана F_ω(m)\n• n>2: Скок до рівня F_{ω^{n-1}}(m)\n• Невиводжуваність: НЕВиводжувана у PA!"
    b_phb, _, _ = textbox(655, 310, txt_ph_bound, size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_phb)

    render(os.path.join(IMG, "fig1-ramsey-vs-paris-harrington.svg"), W, H, *frags)


def fig_fast_growing_hierarchy():
    """fig2-fast-growing-hierarchy.svg: Швидкозростаюча ієрархія функцій та прорив межі ε₀."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Швидкозростаюча ієрархія F_α(x) та бар'єр довідності арифметики Пеано (ε₀)", size=16, bold=True, color="#1e293b"))

    # Рівні ієрархії від F_0 до F_eps0
    levels = [
        ("F₀(x) = x + 1", "Примітивна інкрементація", 70, BLUE_F, BLUE_S),
        ("F₁(x) = 2x", "Лінійне зростання", 130, BLUE_F, BLUE_S),
        ("F₂(x) = x · 2ⁿ", "Поліноміальне/експоненціальне", 190, BLUE_F, BLUE_S),
        ("F₃(x) = 2↑↑x", "Вежа експонент (суперекспонента)", 250, AMBER_F, AMBER_S),
        ("F_ω(x)", "Функція Аккермана (поріг примітивної рекурсії)", 310, PURPLE_F, PURPLE_S),
    ]

    for label, desc, y, f_col, s_col in levels:
        frags.append(rect(30, y, 400, 46, fill=f_col, stroke=s_col, sw=1.2, rx=6))
        frags.append(text(120, y + 27, label, size=12, bold=True, color=s_col))
        frags.append(text(290, y + 27, desc, size=11, color="#334155"))

    # Поріг довідності PA
    frags.append(line(460, 60, 460, 410, color=RED_S, sw=2.5, dash="6,4"))
    frags.append(text(460, 52, "Бар'єр довідності PA: F_α(x), α < ε₀", size=12, bold=True, color=RED_S))

    # Верхній рівень F_eps0 та PH(n)
    frags.append(rect(490, 140, 360, 110, fill=RED_F, stroke=RED_S, sw=1.8, rx=8))
    frags.append(text(670, 170, "Рівень ε₀ (Епсилон-нуль)", size=14, bold=True, color=RED_S))
    
    txt_eps = "F_{ε₀}(x) = F_{ω^ω^...}(x)\nЗростає швидше за БУДЬ-ЯКУ\nдовідно-рекурсивну функцію в PA!"
    b_eps, _, _ = textbox(670, 215, txt_eps, size=11, bold=True, fill="#ffffff", stroke=RED_S)
    frags.append(b_eps)

    # Функція Паріса-Гаррінгтона
    frags.append(rect(490, 280, 360, 110, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=8))
    frags.append(text(670, 305, "Функція Паріса — Гаррінгтона PH(n)", size=13, bold=True, color=AMBER_S))

    txt_phf = "f(n) = PH(n, n, n)\nСкорость зростання відповідає F_{ε₀}(n)\nНаслідок: Твердження PH неможливо\nдовести в арифметиці Пеано!"
    b_phf, _, _ = textbox(670, 352, txt_phf, size=11, bold=True, fill="#ffffff", stroke=AMBER_S)
    frags.append(b_phf)

    render(os.path.join(IMG, "fig2-fast-growing-hierarchy.svg"), W, H, *frags)


def fig_compactness_and_models():
    """fig3-compactness-and-models.svg: Топологічна компактність проти нестандартних моделей M |= PA."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Чому PH істинна в ℕ, але невиводжувана у формальній теорії PA", size=16, bold=True, color="#1e293b"))

    # Блок 1: Стандартна модель N (Істинність)
    frags.append(rect(30, 60, 390, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Стандартна модель ℕ = {0, 1, 2, ...}", size=14, bold=True, color=GREEN_S))

    txt_n_1 = "Нескінченна теорема Рамсея:\nДля будь-якого забарвлення [ℕ]ⁿ\nіснує НЕСКІНЧЕННА однорідна H_∞"
    b_n1, _, _ = textbox(225, 135, txt_n_1, size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_n1)

    txt_n_2 = "Зрізання нескінченної множини:\nВзявши a = min(H_∞) та перші max(m, a)\nелементів, отримуємо велику монохроматичну H"
    b_n2, _, _ = textbox(225, 215, txt_n_2, size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_n2)

    txt_n_3 = "Лема Кеніга / Компактність:\nПерехід від нескінченного випадку до\nскінченного порогу N = PH(n, m, c)\n⇒ PH ІСТИННА в ℕ!"
    b_n3, _, _ = textbox(225, 305, txt_n_3, size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_n3)

    # Блок 2: Нестандартні моделі M |= PA (Невиводжуваність)
    frags.append(rect(460, 60, 390, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(655, 85, "Нестандартні моделі M ⊨ PA", size=14, bold=True, color=RED_S))

    txt_m_1 = "Нестандартні елементи:\nМодель M містить нескінченно великі\nчисла M > n для всіх стандартних n ∈ ℕ"
    b_m1, _, _ = textbox(655, 135, txt_m_1, size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_m1)

    txt_m_2 = "Конструкція контрприкладу в M:\nІснує внутрішнє забарвлення K в M без\nвеликих монохроматичних підмножин"
    b_m2, _, _ = textbox(655, 215, txt_m_2, size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_m2)

    txt_m_3 = "Еквівалентність 1-консистентності:\nPA ⊢ PH ⇔ PA ⊢ 1-Con(PA)\nЗа ІІ теоремою Геделя PA ⊬ 1-Con(PA)\n⇒ PH НЕВИВОДЖУВАНА у PA!"
    b_m3, _, _ = textbox(655, 305, txt_m_3, size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_m3)

    render(os.path.join(IMG, "fig3-compactness-and-models.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_ramsey_vs_paris_harrington()
    fig_fast_growing_hierarchy()
    fig_compactness_and_models()
    print("Figures generated successfully.")
