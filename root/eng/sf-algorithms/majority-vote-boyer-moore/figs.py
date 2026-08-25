# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми Голосування більшості (Бойєр — Мур)."""

import sys
import os

# 4 рівні вгору до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def draw_pairing_cancellation():
    """Фігура 1: Принцип взаємного скорочення пар відмінних елементів."""
    w, h = 840, 360
    frags = []

    # Фон секцій
    frags.append(rect(15, 40, 810, 305, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(420, 68, "Взаємне скорочення пар відмінних елементів у потоці (N = 9)", size=15, bold=True, color=INK))

    # Вхідний потік: A, B, A, C, A, A, D, A, B
    frags.append(text(80, 110, "Вхідний потік:", size=13, bold=True, color=INK, anchor="start"))
    
    stream = ["A", "B", "A", "C", "A", "A", "D", "A", "B"]
    x_start = 205
    for i, val in enumerate(stream):
        cx = x_start + i * 65
        is_maj = (val == "A")
        fill_c = "#dbeafe" if is_maj else "#fee2e2"
        stroke_c = "#2563eb" if is_maj else "#dc2626"
        text_c = "#1e40af" if is_maj else "#991b1b"
        b, _, _ = textbox(cx, 105, val, size=14, pad=8, fill=fill_c, stroke=stroke_c, color=text_c, bold=True, min_w=40)
        frags.append(b)

    # Пояснення частот
    frags.append(text(420, 155, "Кількість A = 5 (більше ніж N/2 = 4.5). Інші елементи: B = 2, C = 1, D = 1 (разом 4).", size=12, italic=True, color=MUTED))

    # Пари для скорочення
    frags.append(text(80, 195, "Спарювання:", size=13, bold=True, color=INK, anchor="start"))

    pairs = [
        ("Пара 1: (A, B)", "Взаємне знищення", 240, 205, "#f1f5f9", "#64748b"),
        ("Пара 2: (A, C)", "Взаємне знищення", 380, 205, "#f1f5f9", "#64748b"),
        ("Пара 3: (A, D)", "Взаємне знищення", 520, 205, "#f1f5f9", "#64748b"),
        ("Пара 4: (A, B)", "Взаємне знищення", 660, 205, "#f1f5f9", "#64748b"),
    ]

    for title, sub, cx, cy, fill_c, stroke_c in pairs:
        b, _, _ = textbox(cx, cy, f"{title}\n{sub}", size=11, pad=6, fill=fill_c, stroke=stroke_c, color=INK, min_w=125)
        frags.append(b)

    # Підсумок знищення
    frags.append(line(80, 255, 760, 255, color="#cbd5e1", sw=1.5))

    frags.append(text(80, 295, "Залишок:", size=13, bold=True, color=INK, anchor="start"))
    
    b_survivor, _, _ = textbox(240, 290, "Елемент A (1 екземпляр)", size=13, pad=8, fill="#dcfce7", stroke="#16a34a", color="#15803d", bold=True, min_w=190)
    frags.append(b_survivor)

    frags.append(text(360, 295, "→ Переможець голосування гарантовано є істинною більшістю", size=12, bold=True, color="#15803d", anchor="start"))

    out_path = os.path.join(IMG_DIR, "fig-pairing-cancellation.svg")
    render(out_path, w, h, *frags)


def draw_state_transitions():
    """Фігура 2: Автомат станів і покрокова логіка оновлення лічильника."""
    w, h = 840, 370
    frags = []

    # Фон секцій
    frags.append(rect(15, 40, 810, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(420, 68, "Потоковий автомат переходів алгоритму Бойєра — Мура", size=15, bold=True, color=INK))

    # Вхідний вузол: новий елемент x
    b_in, _, _ = textbox(110, 155, "Вхідний\nелемент x", size=13, pad=8, fill="#ffffff", stroke="#2563eb", color="#1e40af", bold=True, min_w=110)
    frags.append(b_in)

    # Стрілка до першої перевірки
    frags.append(arrow(170, 155, 230, 155, color=LINE, sw=1.5))

    # Умова 1: count == 0?
    b_cond1, _, _ = textbox(305, 155, "count == 0 ?", size=13, pad=8, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=True, min_w=130)
    frags.append(b_cond1)

    # Гілка ТАК (count == 0) -> призначити кандидата
    frags.append(arrow(305, 120, 305, 95, color="#16a34a", sw=1.5))
    frags.append(text(315, 108, "Так", size=11, bold=True, color="#16a34a", anchor="start"))
    b_set, _, _ = textbox(475, 95, "candidate = x\ncount = 1", size=12, pad=6, fill="#dcfce7", stroke="#16a34a", color="#15803d", bold=True, min_w=150)
    frags.append(b_set)
    frags.append(arrow(305, 95, 395, 95, color="#16a34a", sw=1.5))

    # Гілка НІ -> Умова 2: x == candidate?
    frags.append(arrow(305, 190, 305, 225, color="#dc2626", sw=1.5))
    frags.append(text(315, 208, "Ні", size=11, bold=True, color="#dc2626", anchor="start"))

    b_cond2, _, _ = textbox(305, 260, "x == candidate ?", size=13, pad=8, fill="#fef3c7", stroke="#d97706", color="#92400e", bold=True, min_w=150)
    frags.append(b_cond2)

    # Гілка ТАК (x == candidate) -> count++
    frags.append(arrow(385, 245, 480, 215, color="#2563eb", sw=1.5))
    frags.append(text(410, 222, "Так", size=11, bold=True, color="#2563eb", anchor="start"))
    b_inc, _, _ = textbox(570, 205, "count++\n(посилення переваги)", size=12, pad=6, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True, min_w=170)
    frags.append(b_inc)

    # Гілка НІ (x != candidate) -> count--
    frags.append(arrow(385, 275, 480, 305, color="#dc2626", sw=1.5))
    frags.append(text(410, 302, "Ні", size=11, bold=True, color="#dc2626", anchor="start"))
    b_dec, _, _ = textbox(570, 305, "count--\n(взаємне скорочення)", size=12, pad=6, fill="#fee2e2", stroke="#dc2626", color="#991b1b", bold=True, min_w=170)
    frags.append(b_dec)

    # Вихід до наступного елемента
    frags.append(arrow(660, 95, 750, 150, color=LINE, sw=1.5))
    frags.append(arrow(660, 205, 750, 160, color=LINE, sw=1.5))
    frags.append(arrow(660, 305, 750, 170, color=LINE, sw=1.5))

    b_next, _, _ = textbox(760, 160, "Наступний\nелемент", size=12, pad=6, fill="#ffffff", stroke=LINE, color=INK, bold=True, min_w=95)
    frags.append(b_next)

    out_path = os.path.join(IMG_DIR, "fig-state-transitions.svg")
    render(out_path, w, h, *frags)


def draw_misra_gries_generalization():
    """Фігура 3: Узагальнення Місри — Гріса для пошуку елементів із частотою > N/k (k-1 слотів)."""
    w, h = 840, 370
    frags = []

    # Фон секцій
    frags.append(rect(15, 40, 810, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(420, 68, "Узагальнення алгоритму (Місра — Гріс) для k = 3 (поріг > N/3, 2 слоти)", size=15, bold=True, color=INK))

    # Стан слотів лічильників
    frags.append(text(190, 110, "Поточні слоти кандидатів (k - 1 = 2):", size=13, bold=True, color=INK))

    b_s1, _, _ = textbox(190, 160, "Слот 1: Кандидат C₁ = 'Alpha'\nЛічильник count₁ = 4", size=12, pad=8, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True, min_w=250)
    frags.append(b_s1)

    b_s2, _, _ = textbox(190, 240, "Слот 2: Кандидат C₂ = 'Beta'\nЛічильник count₂ = 2", size=12, pad=8, fill="#dbeafe", stroke="#2563eb", color="#1e40af", bold=True, min_w=250)
    frags.append(b_s2)

    # Розділювач
    frags.append(line(350, 95, 350, 330, color="#cbd5e1", sw=1.5))

    # Вхідний елемент і логіка
    frags.append(text(580, 110, "Надходить новий елемент x:", size=13, bold=True, color=INK))

    b_cases = [
        ("Випадок 1: x ∈ {C₁, C₂}", "Збільшити відповідний count_i++", 580, 155, "#dcfce7", "#16a34a", "#15803d"),
        ("Випадок 2: Є вільний слот", "Записати x у вільний слот з count = 1", 580, 215, "#fef3c7", "#d97706", "#92400e"),
        ("Випадок 3: x ∉ {C₁, C₂} і всі зайняті", "Зменшити ВСІ лічильники: count₁--, count₂--\n(групове знищення трійки різних значень)", 580, 285, "#fee2e2", "#dc2626", "#991b1b"),
    ]

    for title, desc, cx, cy, fill_c, stroke_c, text_c in b_cases:
        b, _, _ = textbox(cx, cy, f"{title}\n{desc}", size=11, pad=6, fill=fill_c, stroke=stroke_c, color=text_c, bold=True, min_w=390)
        frags.append(b)

    out_path = os.path.join(IMG_DIR, "fig-misra-gries-generalization.svg")
    render(out_path, w, h, *frags)


if __name__ == "__main__":
    draw_pairing_cancellation()
    draw_state_transitions()
    draw_misra_gries_generalization()
    print("Згенеровано 3 фігури у папку img/")
