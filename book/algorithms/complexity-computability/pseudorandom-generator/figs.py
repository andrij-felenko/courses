# -*- coding: utf-8 -*-
"""Фігури для теми «Псевдовипадкові генератори та бар'єр природних доведень»
(book/algorithms/complexity-computability/pseudorandom-generator)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра
COLOR_BG_BOX = "#f8fafc"
COLOR_GRID_BORDER = "#cbd5e1"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_BG = "#dbeafe"
COLOR_SUCCESS = "#059669"
COLOR_SUCCESS_BG = "#d1fae5"
COLOR_WARNING = "#d97706"
COLOR_WARNING_BG = "#fef3c7"
COLOR_DANGER = "#dc2626"
COLOR_DANGER_BG = "#fee2e2"
COLOR_MUTED = "#64748b"
INK = "#0f172a"


def fig_prg_architecture():
    """Фігура 1: Архітектура псевдовипадкового генератора та статистичного розрізнювача."""
    W, H = 940, 380
    frags = []

    # Головний фоновий прямокутник
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Заголовок блоку
    frags.append(text(W / 2, 35, "Архітектура псевдовипадкового генератора та статистичного розрізнювача", size=16, bold=True, color=INK))

    # Джерело насінини (Seed)
    x_seed, y_seed = 40, 110
    frags.append(rect(x_seed, y_seed, 140, 70, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2, rx=6))
    frags.append(text(x_seed + 70, y_seed + 30, "Коротке насіння", size=13, bold=True, color=COLOR_ACCENT))
    frags.append(text(x_seed + 70, y_seed + 50, "s ∈ {0,1}ᵏ", size=12, color=INK))

    # Стрілка Seed -> PRG
    frags.append(arrow(x_seed + 140, y_seed + 35, x_seed + 210, y_seed + 35, color=COLOR_ACCENT, sw=2))

    # Генератор (PRG G)
    x_prg = 210
    frags.append(rect(x_prg, y_seed, 160, 70, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2, rx=6))
    frags.append(text(x_prg + 80, y_seed + 30, "Генератор G", size=14, bold=True, color=COLOR_SUCCESS))
    frags.append(text(x_prg + 80, y_seed + 50, "G: {0,1}ᵏ → {0,1}ᵐ", size=12, color=INK))

    # Стрілка PRG -> Multiplexer
    frags.append(arrow(x_prg + 160, y_seed + 35, x_prg + 240, y_seed + 35, color=COLOR_SUCCESS, sw=2))
    frags.append(text(x_prg + 200, y_seed + 20, "G(s)", size=12, bold=True, color=COLOR_SUCCESS))

    # Джерело Справжнього Хаосу (True Random)
    x_rand, y_rand = 40, 240
    frags.append(rect(x_rand, y_rand, 330, 70, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, sw=2, rx=6))
    frags.append(text(x_rand + 165, y_rand + 30, "Справжній хаос (Рівномірний розподіл)", size=13, bold=True, color=COLOR_WARNING))
    frags.append(text(x_rand + 165, y_rand + 50, "r ∈_R {0,1}ᵐ", size=12, color=INK))

    # Стрілка Random -> Multiplexer
    frags.append(arrow(x_rand + 330, y_rand + 35, x_prg + 240, y_rand + 35, color=COLOR_WARNING, sw=2))
    frags.append(text(x_rand + 370, y_rand + 20, "r", size=12, bold=True, color=COLOR_WARNING))

    # Переключатель / Вибір входу (Multiplexer)
    x_mux = 450
    frags.append(rect(x_mux, 160, 100, 110, fill=COLOR_HEADER_BG, stroke=COLOR_MUTED, sw=2, rx=6))
    frags.append(text(x_mux + 50, 195, "Випадковий", size=12, bold=True, color=INK))
    frags.append(text(x_mux + 50, 215, "вибір w", size=12, bold=True, color=INK))
    frags.append(text(x_mux + 50, 240, "w ∈ {G(s), r}", size=11, color=COLOR_MUTED))

    # Стрілка Mux -> Distinguisher
    frags.append(arrow(x_mux + 100, 215, x_mux + 170, 215, color=INK, sw=2))
    frags.append(text(x_mux + 135, 195, "Рядок w", size=12, bold=True, color=INK))

    # Схема-Розрізнювач (Distinguisher D)
    x_dist = 620
    frags.append(rect(x_dist, 160, 160, 110, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=2, rx=6))
    frags.append(text(x_dist + 80, 195, "Розрізнювач D", size=14, bold=True, color=COLOR_DANGER))
    frags.append(text(x_dist + 80, 220, "Схема Size(D) ≤ S", size=12, color=INK))
    frags.append(text(x_dist + 80, 245, "Вихід b ∈ {0, 1}", size=11, color=COLOR_MUTED))

    # Перевага розрізнення
    bot_box, _, _ = textbox(W / 2, 335,
                            "Умова стійкості: |Pr[D(G(s))=1] - Pr[D(r)=1]| < ε (Жодна схема розміру S не розрізняє G(s) від r)",
                            size=12, bold=True, fill=COLOR_BG_BOX, stroke=COLOR_GRID_BORDER, pad=8)
    frags.append(bot_box)

    render(os.path.join(IMG, "prg-architecture.svg"), W, H, *frags,
           title="Архітектура псевдовипадкового генератора G та розрізнювача D")


def fig_nw_design_structure():
    """Фігура 2: Структура Нісана-Вігдерсона (NW Generator) та комбінаторний дизайн."""
    W, H = 940, 420
    frags = []

    # Головний фоновий прямокутник
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(W / 2, 35, "Конструкція генератора Нісана–Вігдерсона (NW PRG)", size=16, bold=True, color=INK))

    # Головний Seed (довжини d)
    x_seed, y_seed = 40, 70
    frags.append(rect(x_seed, y_seed, 860, 45, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2, rx=6))
    frags.append(text(x_seed + 430, y_seed + 27, "Вхідне насіння z = (z₁, z₂, ..., zⴞ) ∈ {0,1}ᵈ", size=13, bold=True, color=COLOR_ACCENT))

    # 4 Блоки підмножин (Комбінаторний дизайн)
    y_sub = 165
    box_w = 180
    gap = 40
    subsets = [
        ("Підмножина S₁", "z|S₁ (l біт)", "f(z|S₁)", "Біт y₁"),
        ("Підмножина S₂", "z|S₂ (l біт)", "f(z|S₂)", "Біт y₂"),
        ("...", "...", "...", "..."),
        ("Підмножина Sₘ", "z|Sₘ (l біт)", "f(z|Sₘ)", "Біт yₘ")
    ]

    for i, (title_str, proj_str, func_str, out_str) in enumerate(subsets):
        x_sub = 40 + i * (box_w + gap)

        # Стрілка від seed до підмножини
        frags.append(arrow(x_sub + box_w / 2, y_seed + 45, x_sub + box_w / 2, y_sub, color=COLOR_ACCENT, sw=1.5))

        # Блок обчислення
        bg_col = COLOR_SUCCESS_BG if i != 2 else COLOR_BG_BOX
        border_col = COLOR_SUCCESS if i != 2 else COLOR_GRID_BORDER

        frags.append(rect(x_sub, y_sub, box_w, 110, fill=bg_col, stroke=border_col, sw=2, rx=6))
        frags.append(text(x_sub + box_w / 2, y_sub + 25, title_str, size=13, bold=True, color=border_col))
        frags.append(text(x_sub + box_w / 2, y_sub + 50, proj_str, size=12, color=INK))
        frags.append(text(x_sub + box_w / 2, y_sub + 75, func_str, size=12, bold=True, color=COLOR_ACCENT))

        # Стрілка до виходу
        frags.append(arrow(x_sub + box_w / 2, y_sub + 110, x_sub + box_w / 2, y_sub + 155, color=COLOR_SUCCESS, sw=1.5))

    # Підсумковий вихідний рядок y
    y_out = y_sub + 155
    frags.append(rect(x_seed, y_out, 860, 45, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2, rx=6))
    frags.append(text(x_seed + 430, y_out + 27, "Вихідний псевдовипадковий рядок y = (y₁, y₂, ..., yⴘ) ∈ {0,1}ᵐ", size=13, bold=True, color=COLOR_SUCCESS))

    # Перетин підмножин
    bot_box, _, _ = textbox(W / 2, 380,
                            "Умова дизайну: |Sᵢ| = l, |Sᵢ ∩ Sⱼ| ≤ γ для всіх i ≠ j  ⇒  Забезпечує малопотужний вплив інших бітів",
                            size=12, bold=True, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, pad=6)
    frags.append(bot_box)

    render(os.path.join(IMG, "nw-design-structure.svg"), W, H, *frags,
           title="Комбінаторна схема розширення насіння у NW PRG")


def fig_natural_proofs_barrier():
    """Фігура 3: Парадокс бар'єра природних доведень (Razborov-Rudich Barrier)."""
    W, H = 940, 420
    frags = []

    # Головний фоновий прямокутник
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(W / 2, 35, "Парадокс природних доведень (Розрізнювач на основі властивості Pₙ)", size=16, bold=True, color=INK))

    # Ліва частина: Простір усіх булевих функцій F_n
    x_left = 40
    box_w = 400
    frags.append(rect(x_left, 70, box_w, 280, fill="#f1f5f9", stroke=COLOR_MUTED, sw=2, rx=8))
    frags.append(text(x_left + box_w / 2, 95, "Простір усіх функцій Fₙ (2²ⁿ функцій)", size=14, bold=True, color=INK))

    # Внутрішня область: Стійкі PRG (Малі схеми Im(G))
    frags.append(rect(x_left + 25, 125, 350, 90, fill=COLOR_SUCCESS_BG, stroke=COLOR_SUCCESS, sw=2, rx=6))
    frags.append(text(x_left + 200, 150, "Множина виходів PRG G(s)", size=13, bold=True, color=COLOR_SUCCESS))
    frags.append(text(x_left + 200, 175, "Обчислюються МАЛИМИ схемами Size ≤ S(n)", size=11, color=INK))
    frags.append(text(x_left + 200, 195, "Не мають властивості Pₙ (Корисність Pₙ)", size=11, color=COLOR_DANGER))

    # Внутрішня область: Натуральна властивість P_n
    frags.append(rect(x_left + 25, 235, 350, 95, fill=COLOR_ACCENT_BG, stroke=COLOR_ACCENT, sw=2, rx=6))
    frags.append(text(x_left + 200, 260, "Натуральна властивість Pₙ", size=13, bold=True, color=COLOR_ACCENT))
    frags.append(text(x_left + 200, 282, "1. Конструктивність: Pₙ(f) обчислювана за poly(2ⁿ)", size=11, color=INK))
    frags.append(text(x_left + 200, 304, "2. Великість: Pr_f[Pₙ(f) = 1] ≥ 1/poly(n)", size=11, color=INK))

    # Стрілка від лівої картини до правої
    frags.append(arrow(x_left + box_w + 15, 210, x_left + box_w + 75, 210, color=COLOR_DANGER, sw=3))
    frags.append(text(x_left + box_w + 45, 190, "Перетворення", size=12, bold=True, color=COLOR_DANGER))

    # Права частина: Сконструйований розрізнювач D_P
    x_right = 540
    box_w_r = 360
    frags.append(rect(x_right, 70, box_w_r, 280, fill=COLOR_DANGER_BG, stroke=COLOR_DANGER, sw=2, rx=8))
    frags.append(text(x_right + box_w_r / 2, 95, "Ефективний розрізнювач D_Pₙ", size=14, bold=True, color=COLOR_DANGER))

    tb_r = fitbox(x_right + 20, 120, box_w_r - 40, 210, [
        "Алгоритм D_Pₙ(w):",
        "1. Інтерпретує рядок w довжини 2ⁿ",
        "   як таблицю істинності функції f_w.",
        "2. Обчислює знаменник Pₙ(f_w).",
        "3. Якщо Pₙ(f_w) = 1, повертає 1 (Хаос).",
        "4. Якщо Pₙ(f_w) = 0, повертає 0 (PRG).",
        "",
        "Результат: Розрізняє G(s) від r з",
        "перевагою Adv ≥ 1/poly(n) - 0!",
        "Це ЛАМАЄ стійкість PRG!"
    ], size=12, color=INK, lh=20)
    frags.append(tb_r)

    # Нижній висновок
    bot_box, _, _ = textbox(W / 2, 380,
                            "Суперечність: Стійкий PRG існує  ⇒  Природне доведення P ≠ NP НЕ ІСНУЄ для загальних схем P/poly",
                            size=12, bold=True, fill=COLOR_WARNING_BG, stroke=COLOR_WARNING, pad=6)
    frags.append(bot_box)

    render(os.path.join(IMG, "natural-proofs-barrier.svg"), W, H, *frags,
           title="Формування розрізнювача D з натуральної властивості Pₙ")


if __name__ == "__main__":
    fig_prg_architecture()
    fig_nw_design_structure()
    fig_natural_proofs_barrier()
    print("Успішно згенеровано 3 фігури у теці img/")
