# -*- coding: utf-8 -*-
"""Фігури для теми «Техніка двох спостережуваних літералів (Watched Literals)» (book/algorithms/complexity-computability/watched-literals)."""
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

def fig1_watched_literals_invariant():
    """fig1-watched-literals-invariant.svg: Схема інваріанту 2WL у диз'юнкті та реорганізація покажчиків."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Інваріант двох спостережуваних літералів (2WL) при присвоєнні змінних", size=16, bold=True, color="#1e293b"))

    # Диз'юнкт C = (x₁ ∨ ¬x₂ ∨ x₃ ∨ ¬x₄)
    frags.append(text(440, 70, "Диз'юнкт C = (x₁ ∨ ¬x₂ ∨ x₃ ∨ ¬x₄), довжина k = 4", size=13, italic=True, color="#334155"))

    # Початковий стан (w1 = pos 0, w2 = pos 1)
    frags.append(rect(30, 95, 820, 140, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(160, 120, "1. Початковий стан: w₁ = pos 0 (x₁), w₂ = pos 1 (¬x₂)", size=12, bold=True, color=BLUE_S))

    lits_1 = [("x₁", "неприсвоєний", AMBER_F, AMBER_S), 
              ("¬x₂", "неприсвоєний", AMBER_F, AMBER_S), 
              ("x₃", "неприсвоєний", GRAY_F, GRAY_S), 
              ("¬x₄", "неприсвоєний", GRAY_F, GRAY_S)]
    
    xs_1 = [120, 300, 480, 660]
    for i, (l_text, l_st, f_col, s_col) in enumerate(lits_1):
        is_w = i in [0, 1]
        t_str = f"pos {i}: {l_text}\n[{l_st}]" + ("\nWATCHED" if is_w else "")
        b, _, _ = textbox(xs_1[i], 165, t_str, size=11, fill=f_col, stroke=s_col)
        frags.append(b)

    # Подія: ¬x₂ отримує значення 1, тому літерал ¬x₂ становиться хибним (False)
    frags.append(arrow(440, 245, 440, 275, color=RED_S, sw=2.5))
    b_ev, _, _ = textbox(440, 260, "ПОДІЯ: x₂ := 1 ⟹ літерал ¬x₂ оцінюється як FALSE!\nПошук нового не-хибного літерала для переносу покажчика w₂", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_ev)

    # Оновлений стан (сканування знаходить pos 3 (¬x₄), w2 переноситься на pos 3)
    frags.append(rect(30, 285, 820, 140, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(210, 310, "2. Оновлений стан: w₁ = pos 0 (x₁), w₂ перенесено на pos 3 (¬x₄)", size=12, bold=True, color=GREEN_S))

    lits_2 = [("x₁", "неприсвоєний", AMBER_F, AMBER_S), 
              ("¬x₂", "FALSE (x₂=1)", RED_F, RED_S), 
              ("x₃", "неприсвоєний", GRAY_F, GRAY_S), 
              ("¬x₄", "неприсвоєний", GREEN_F, GREEN_S)]

    for i, (l_text, l_st, f_col, s_col) in enumerate(lits_2):
        is_w = i in [0, 3]
        t_str = f"pos {i}: {l_text}\n[{l_st}]" + ("\nWATCHED" if is_w else "")
        b, _, _ = textbox(xs_1[i], 355, t_str, size=11, fill=f_col, stroke=s_col)
        frags.append(b)

    render(os.path.join(IMG, "fig1-watched-literals-invariant.svg"), W, H, *frags)

def fig2_bcp_state_machine():
    """fig2-bcp-state-machine.svg: Автомат станів диз'юнкта в алгоритмі BCP під дією присвоєнь."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Переходи станів диз'юнкта в алгоритмі Unit Propagation (BCP)", size=16, bold=True, color="#1e293b"))

    # Стан 1: Активний диз'юнкт (2WL інваріант виконується)
    b_st1, _, _ = textbox(200, 120, "АКТИВНИЙ ДИЗ'ЮНКТ\nОбидва спостережувані\nлітерали w₁, w₂ ∉ {FALSE}\nІнваріант 2WL виконується", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_st1)

    # Стан 2: Перенос покажчика (Shift Watch)
    b_st2, _, _ = textbox(680, 120, "ПЕРЕНОС ПОКАЖЧИКА\nОдин з літералів wᵢ := FALSE\nЗнайдено новий не-хибний L'\nwᵢ ↦ L' (без поширення)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_st2)

    # Стан 3: Одиничний диз'юнкт (Unit Propagation)
    b_st3, _, _ = textbox(200, 320, "ОДИНИЧНИЙ ДИЗ'ЮНКТ (Unit)\nw₁ := FALSE, а w₂ неприсвоєний\nНемає заміни для w₁!\nОбов'язкове присвоєння w₂ := TRUE", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_st3)

    # Стан 4: КонфліКТний диз'юнкт (Conflict)
    b_st4, _, _ = textbox(680, 320, "КОНФЛІКТ (Conflict)\nОбидва w₁, w₂ := FALSE\nНемає кандидату для заміни!\nПовернення CDCL та виведення", size=12, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_st4)

    # Стрілки переходів між станами
    frags.append(arrow(330, 105, 540, 105, color=PURPLE_S, sw=1.8))
    b_lbl1, _, _ = textbox(435, 88, "wᵢ став FALSE, є заміна", size=10, fill="#ffffff", stroke=PURPLE_S)
    frags.append(b_lbl1)

    frags.append(arrow(540, 135, 330, 135, color=BLUE_S, sw=1.8))
    b_lbl2, _, _ = textbox(435, 150, "Успішна заміна покажчика", size=10, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_lbl2)

    frags.append(arrow(160, 175, 160, 275, color=AMBER_S, sw=2.0))
    b_lbl3, _, _ = textbox(110, 225, "w₁=FALSE,\nнема заміни", size=10, fill="#ffffff", stroke=AMBER_S)
    frags.append(b_lbl3)

    frags.append(arrow(720, 175, 720, 275, color=RED_S, sw=2.0))
    b_lbl4, _, _ = textbox(770, 225, "w₁=FALSE,\nw₂ вже FALSE", size=10, fill="#ffffff", stroke=RED_S)
    frags.append(b_lbl4)

    frags.append(arrow(340, 320, 530, 320, color=RED_S, sw=1.8))
    b_lbl5, _, _ = textbox(435, 320, "Присвоєння w₂:=TRUE веде до суперечності", size=10, fill="#ffffff", stroke=RED_S)
    frags.append(b_lbl5)

    render(os.path.join(IMG, "fig2-bcp-state-machine.svg"), W, H, *frags)

def fig3_backtrack_lazy_behavior():
    """fig3-backtrack-lazy-behavior.svg: Порівняння поведінки при поверненні (backtrack): лічильники проти 2WL."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Поведінка при скасуванні присвоєнь (Backtrack): Традиційні лічильники vs 2WL", size=16, bold=True, color="#1e293b"))

    # Ліва колонка: Класичний підхід з лічильниками
    frags.append(rect(30, 60, 390, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Традиційні лічильники (DPLL / SATO)", size=14, bold=True, color=RED_S))

    txt_cnt = "• При кожному скасуванні xᵢ := UNASSIGNED:\n  Обов'язкове інкрементування лічильників\n  у всіх диз'юнктах, де присутній xᵢ.\n• Складність повернення: O(|C| · k)\n• Масові записи в пам'ять (Un-trail stack)\n• Промивання L1/L2 кешу при бектрекінгу"
    b_cnt, _, _ = textbox(225, 175, txt_cnt, size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_cnt)

    b_cnt_res, _, _ = textbox(225, 330, "ВИТРАТИ ПАМ'ЯТІ: O(Всього змінних)\nВисока затримка шини RAM", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_cnt_res)

    # Права колонка: Лінивий підхід 2WL
    frags.append(rect(460, 60, 390, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(655, 85, "Техніка 2WL (Chaff / MiniSAT / CaDiCaL)", size=14, bold=True, color=GREEN_S))

    txt_2wl = "• При скасуванні xᵢ := UNASSIGNED:\n  НУЛЬ операцій із диз'юнктами!\n  Покажчики w₁, w₂ залишаються на місцях.\n• Інваріант 2WL гарантовано ЗБЕРІГАЄТЬСЯ:\n  якщо wᵢ ∉ {FALSE} до скасування,\n  то після скасування поготів wᵢ ∉ {FALSE}.\n• Складність повернення: O(1)"
    b_2wl, _, _ = textbox(655, 175, txt_2wl, size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_2wl)

    b_2wl_res, _, _ = textbox(655, 330, "ВИТРАТИ ПАМ'ЯТІ ПРИ БЕКТРЕКУ: 0 БАЙТ\nЗбереження стану кешу", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_2wl_res)

    render(os.path.join(IMG, "fig3-backtrack-lazy-behavior.svg"), W, H, *frags)

if __name__ == "__main__":
    fig1_watched_literals_invariant()
    fig2_bcp_state_machine()
    fig3_backtrack_lazy_behavior()
    print("Figures generated successfully.")
