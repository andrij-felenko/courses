# -*- coding: utf-8 -*-
"""Фігури для теми «Універсальне хешування» (book/algorithms/complexity-computability/universal-hashing)."""
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

def fig1_adversarial_collapse():
    """fig1-adversarial-collapse.svg: Колізійна атака на фіксовану хеш-функцію проти універсального хешування."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Детерміноване хешування (атака) проти Універсального сімейства (випадковий вибір)", size=15, bold=True, color="#1e293b"))

    # Ліва частина: Фіксована хеш-функція h(x)
    frags.append(rect(30, 60, 395, 335, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(227, 85, "Детерміноване h(x) (фіксоване)", size=13, bold=True, color=RED_S))
    frags.append(text(227, 105, "Супротивник знає h(x) → будує S = {k₁, k₂, ..., kₙ}", size=11, color="#7f1d1d"))

    # Вхідні ключі ліворуч
    keys_left = ["k₁", "k₂", "k₃", "k₄", "k₅"]
    for i, k in enumerate(keys_left):
        b, _, _ = textbox(70, 145 + i * 45, k, size=11, bold=True, fill="#ffffff", stroke=RED_S)
        frags.append(b)

    # Хеш-таблиця ліворуч (всі колізять у бакет 2)
    frags.append(text(340, 130, "Бакети", size=11, bold=True, color="#475569"))
    for b_idx in range(5):
        fill_color = "#fee2e2" if b_idx == 2 else "#ffffff"
        stroke_color = RED_S if b_idx == 2 else "#94a3b8"
        frags.append(rect(310, 145 + b_idx * 45, 60, 35, fill=fill_color, stroke=stroke_color, sw=1.5, rx=4))
        frags.append(text(340, 167 + b_idx * 45, f"[{b_idx}]", size=11, color="#1e293b"))

    # Стрілки колізій ліворуч
    for i in range(5):
        frags.append(line(95, 145 + i * 45, 310, 235, color=RED_S, sw=1.5))

    frags.append(text(227, 375, "Деградація: O(n) пошук (список списків)", size=11, bold=True, color=RED_S))

    # Права частина: Універсальне сімейство H
    frags.append(rect(455, 60, 395, 335, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(652, 85, "Універсальне сімейство H", size=13, bold=True, color=GREEN_S))
    frags.append(text(652, 105, "Супротивник обирає S → вибір h ∈ H після цього!", size=11, color="#14532d"))

    # Вхідні ключі праворуч
    for i, k in enumerate(keys_left):
        b, _, _ = textbox(495, 145 + i * 45, k, size=11, bold=True, fill="#ffffff", stroke=GREEN_S)
        frags.append(b)

    # Хеш-таблиця праворуч (рівномірний розподіл)
    frags.append(text(765, 130, "Бакети", size=11, bold=True, color="#475569"))
    for b_idx in range(5):
        frags.append(rect(735, 145 + b_idx * 45, 60, 35, fill="#e6f4ea", stroke=GREEN_S, sw=1.5, rx=4))
        frags.append(text(765, 167 + b_idx * 45, f"[{b_idx}]", size=11, color="#1e293b"))

    # Стрілки рівномірного розподілу праворуч
    target_buckets = [0, 2, 4, 1, 3]
    for i, tb in enumerate(target_buckets):
        frags.append(line(520, 145 + i * 45, 735, 162 + tb * 45, color=GREEN_S, sw=1.5))

    frags.append(text(652, 375, "Гарантія: E[Cₓ] ≤ 1 + n/m = O(1)", size=11, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "fig1-adversarial-collapse.svg"), W, H, *frags)


def fig2_modular_family():
    """fig2-modular-family.svg: Модульне лінійне універсальне сімейство h_{a,b}(x) = ((a*x + b) mod p) mod m."""
    W, H = 880, 360
    frags = []

    frags.append(rect(10, 10, 860, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Двоетапне відображення модульного універсального сімейства Hₚ,ₘ", size=15, bold=True, color="#1e293b"))

    # Вхідний ключ x
    b_in, _, _ = textbox(80, 170, "Вхідний ключ\nx ∈ U", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_in)

    # Крок 1: Афінне перетворення у скінченному полі Z_p
    frags.append(line(135, 170, 210, 170, color=BLUE_S, sw=2))
    b_step1, _, _ = textbox(330, 170, "Крок 1: Афінне перетворення у Zₚ\ny = (a · x + b) mod p\na ∈ {1,...,p-1}, b ∈ {0,...,p-1}", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_step1)

    # Крок 2: Звуження до m бакетів
    frags.append(line(450, 170, 520, 170, color=PURPLE_S, sw=2))
    b_step2, _, _ = textbox(630, 170, "Крок 2: Зменшення модулю\nh(x) = y mod m\nm бакетів хеш-таблиці", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_step2)

    # Вихідний бакет
    frags.append(line(740, 170, 790, 170, color=AMBER_S, sw=2))
    b_out, _, _ = textbox(830, 170, "Індекс\n[0..m-1]", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_out)

    # Пояснювальні примітки внизу
    note_box = "Властивості конструкції:\n1. p — просте число, p > |U| (розмір універсуму ключів)\n2. a, b обираються випадково й рівномірно з Zₚ (a ≠ 0)\n3. Вірогідність колізії для будь-яких x ≠ y: P[h(x) = h(y)] < 1/m"
    b_note, _, _ = textbox(440, 280, note_box, size=11, fill="#ffffff", stroke="#64748b")
    frags.append(b_note)

    render(os.path.join(IMG, "fig2-modular-family.svg"), W, H, *frags)


def fig3_multiply_shift():
    """fig3-multiply-shift.svg: Множильно-зсувне хешування Dietzfelbinger (Multiply-Shift Hashing)."""
    W, H = 880, 380
    frags = []

    frags.append(rect(10, 10, 860, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Апаратна схема множильно-зсувного хешування (Multiply-Shift Hashing)", size=15, bold=True, color="#1e293b"))

    # Вхідний ключ x (w бітів) та випадковий коефіцієнт a (w бітів)
    b_x, _, _ = textbox(140, 80, "Вхідний ключ x\n(w-бітне ціле)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_a, _, _ = textbox(140, 160, "Випадкова непарна стала a\n(w-бітне ціле, a ≡ 1 mod 2)", size=11, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_x)
    frags.append(b_a)

    # Блок множення
    frags.append(line(220, 80, 290, 120, color=BLUE_S, sw=1.8))
    frags.append(line(245, 160, 290, 120, color=PURPLE_S, sw=1.8))
    
    b_mult, _, _ = textbox(360, 120, "Цілочисельне множення\n(a · x) mod 2ʷ\n64-бітний результат", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_mult)

    # Блок зсуву бітів
    frags.append(line(440, 120, 500, 120, color=AMBER_S, sw=2))
    b_shift, _, _ = textbox(600, 120, "Побітовий зсув праворуч\n>> (w - M)\nВиділення старших M бітів", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_shift)

    # Вихід
    frags.append(line(700, 120, 760, 120, color=TEAL_S, sw=2))
    b_out, _, _ = textbox(810, 120, "Хеш-код h(x)\nM бітів\n[0..2ᴹ-1]", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_out)

    # Візуалізація регістра бітів
    frags.append(rect(140, 240, 600, 45, fill="#ffffff", stroke="#475569", sw=1.5, rx=4))
    frags.append(text(440, 225, "64-бітний результат добутку (a · x)", size=11, bold=True, color="#1e293b"))

    # Старші M бітів (зелені)
    frags.append(rect(140, 240, 160, 45, fill=GREEN_F, stroke=GREEN_S, sw=1.5))
    frags.append(text(220, 267, "Старші M бітів (Хеш-код)", size=11, bold=True, color=GREEN_S))

    # Молодші w-M бітів (сірі)
    frags.append(rect(300, 240, 440, 45, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    frags.append(text(520, 267, "Молодші (w - M) бітів (відкидаються зсувом >>)", size=11, color="#64748b"))

    frags.append(text(440, 335, "Без ділення! Одна апаратна інструкція множення IMUL та один зсув SHR", size=12, bold=True, color=TEAL_S))

    render(os.path.join(IMG, "fig3-multiply-shift.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_adversarial_collapse()
    fig2_modular_family()
    fig3_multiply_shift()
    print("Усі фігури для універсального хешування успішно згенеровано.")
