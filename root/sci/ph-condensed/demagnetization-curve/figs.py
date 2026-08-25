# -*- coding: utf-8 -*-
"""Фігури до теми «Крива розмагнічування та робоча точка магніту».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"
COLOR_B = "#1d4ed8"      # Індукція B (синій)
COLOR_J = "#d97706"      # Намагніченість J (помаранчевий)
COLOR_LOAD = "#059669"   # Робоча лінія (зелений)
COLOR_RECOIL = "#7c3aed" # Лінія повернення (пурпуровий)
COLOR_RECT = "#eff6ff"   # Прямокутник (BH)_max
COLOR_ALERT = "#dc2626"  # Червоний акцент / незворотні втрати

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Другий квадрант: B(H) та J(H) ──────────────────────────────────
def fig_quadrant2_demag_curves(path):
    W, H_canvas = 780, 480
    f = []

    # Фон та заголовок
    f.append(rect(0, 0, W, H_canvas, fill="#ffffff", stroke=BORDER, rx=0))
    f.append(text(W / 2, 28, "Другий квадрант петлі гістерезису: криві B(H) та J(H)", size=16, bold=True, color=INK))

    # Система координат (другий квадрант: H від від'ємного до 0, B від 0 до додатного)
    x0, y0 = 520, 390  # Початок координат (H=0, B=0)
    x_min = 120        # Напрямок -H (ліворуч)
    y_max = 80         # Напрямок +B, +J (вгору)

    # Осі
    f.append(arrow(x0, y0, x_min - 30, y0, color=INK, sw=1.8))  # Ос -H
    f.append(arrow(x0, y0, x0, y_max - 25, color=INK, sw=1.8))  # Ос +B, +J

    # Підписи осей
    f.append(text(x_min - 45, y0 + 5, "H (кА/м)", size=13, bold=True, color=INK, anchor="end"))
    f.append(text(x0 + 15, y_max - 20, "B, J (Тл)", size=13, bold=True, color=INK, anchor="start"))

    # Параметри для побудови кривих
    x_Hcj = 170
    x_Hcb = 330
    y_Br = 120

    # Штриховані допоміжні лінії сітки
    f.append(line(x_Hcj, y0, x_Hcj, y_Br - 20, color=MUTED, sw=1, dash="4,4"))
    f.append(line(x_Hcb, y0, x_Hcb, y0 - 150, color=MUTED, sw=1, dash="4,4"))
    f.append(line(x_min - 10, y_Br, x0, y_Br, color=MUTED, sw=1, dash="4,4"))

    # Прямокутник (BH)_max
    x_opt = 390
    y_opt = 220
    f.append(rect(x_opt, y_opt, x0 - x_opt, y0 - y_opt, fill="#dbeafe", stroke=COLOR_B, sw=1.2, rx=0))
    f.append(text((x_opt + x0) / 2, (y_opt + y0) / 2 + 5, "(BH)max", size=12, bold=True, color=COLOR_B))

    # Побудова плавної кривої J(H)
    d_J = f"M {x0} {y_Br} C {x0-150} {y_Br-2}, {x_Hcj+80} {y_Br-5}, {x_Hcj+30} {y_Br+30} C {x_Hcj} {y_Br+70}, {x_Hcj-10} {y0-20}, {x_Hcj-35} {y0}"
    f.append(path_svg(d_J, fill="none", stroke=COLOR_J, sw=2.5))

    # Побудова кривої B(H)
    d_B = f"M {x0} {y_Br} C {x0-100} {y_Br+30}, {x_Hcb+60} {y0-60}, {x_Hcb} {y0}"
    f.append(path_svg(d_B, fill="none", stroke=COLOR_B, sw=2.5))

    # Точки на осях та кривих
    f.append(circle(x0, y_Br, 4, fill=COLOR_B, stroke=INK, sw=1))
    f.append(text(x0 + 12, y_Br + 5, "B_r = J_r (Залишкова індукція)", size=12, bold=True, color=COLOR_B, anchor="start"))

    f.append(circle(x_Hcb, y0, 4, fill=COLOR_B, stroke=INK, sw=1))
    f.append(text(x_Hcb, y0 + 22, "H_cb", size=12, bold=True, color=COLOR_B, anchor="middle"))
    f.append(text(x_Hcb, y0 + 38, "(Коерцитивність B)", size=10, color=MUTED, anchor="middle"))

    f.append(circle(x_Hcj - 35, y0, 4, fill=COLOR_J, stroke=INK, sw=1))
    f.append(text(x_Hcj - 35, y0 + 22, "H_cj", size=12, bold=True, color=COLOR_J, anchor="middle"))
    f.append(text(x_Hcj - 35, y0 + 38, "(Власна коерцитивність J)", size=10, color=MUTED, anchor="middle"))

    f.append(circle(x_opt, y_opt, 5, fill=POS, stroke=INK, sw=1))
    f.append(text(x_opt - 10, y_opt - 10, "Робоча точка (H_opt, B_opt)", size=11, bold=True, color=POS, anchor="end"))

    # Легенда праворуч зверху
    leg_x, leg_y = 60, 60
    f.append(rect(leg_x, leg_y, 250, 85, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(line(leg_x + 15, leg_y + 25, leg_x + 45, leg_y + 25, color=COLOR_J, sw=2.5))
    f.append(text(leg_x + 55, leg_y + 29, "J(H) — Інтринсивна крива", size=11, bold=True, color=COLOR_J, anchor="start"))
    f.append(line(leg_x + 15, leg_y + 55, leg_x + 45, leg_y + 55, color=COLOR_B, sw=2.5))
    f.append(text(leg_x + 55, leg_y + 59, "B(H) — Індукційна крива", size=11, bold=True, color=COLOR_B, anchor="start"))

    # Пояснювальний текстовий блок знизу
    f.append(fitbox(40, 415, 700, 45, 
                    "B(H) = μ₀·H + J(H). Для висококоерцитивних матеріалів (NdFeB, SmCo) H_cj значно перевищує H_cb,\nщо забезпечує високу стійкість до розмагнічування у відкритому магнітному колі.",
                    size=11, fill="#f1f5f9", stroke=BORDER))

    return render(path, W, H_canvas, *f)

# ── Фігура 2: Розмагнічувальне поле та коло з зазором ─────────────────────────
def fig_magnetic_circuit_gap(path):
    W, H_canvas = 780, 440
    f = []

    f.append(rect(0, 0, W, H_canvas, fill="#ffffff", stroke=BORDER, rx=0))
    f.append(text(W / 2, 26, "Магнітне коло з повітряним зазором та розмагнічувальне поле H_d", size=16, bold=True, color=INK))

    # Ліва панель: стержень/магніт у вакуумі
    f.append(rect(20, 55, 360, 320, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(200, 80, "Постійний магніт у відкритому просторі", size=13, bold=True, color=INK))

    # Стержень магніту
    mx, my, mw, mh = 100, 140, 200, 70
    f.append(rect(mx, my, mw, mh, fill="#e2e8f0", stroke=INK, sw=2, rx=4))
    f.append(text(mx + mw/2, my + 25, "Постійний магніт", size=12, bold=True, color=INK))
    f.append(text(mx + mw/2, my + 45, "Намагніченість J", size=11, color=COLOR_J))

    # Полюси (+sigma_m, -sigma_m)
    f.append(text(mx - 15, my + mh/2 + 4, "S (−σ_m)", size=12, bold=True, color=NEG))
    f.append(text(mx + mw + 20, my + mh/2 + 4, "N (+σ_m)", size=12, bold=True, color=POS))

    # Вектор намагніченості J (вправо)
    f.append(arrow(mx + 40, my + mh/2, mx + mw - 40, my + mh/2, color=COLOR_J, sw=2.5))
    f.append(text(mx + mw/2, my + mh/2 - 8, "J", size=12, bold=True, color=COLOR_J))

    # Вектор розмагнічувального поля H_d (всередині магніту — вліво!)
    f.append(arrow(mx + mw - 40, my + mh + 25, mx + 40, my + mh + 25, color=POS, sw=2.5))
    f.append(text(mx + mw/2, my + mh + 42, "H_d = −N_d · J / μ₀", size=12, bold=True, color=POS))

    # Лінії зовнішнього поля B
    f.append(path_svg(f"M {mx+mw} {my+15} C {mx+mw+60} {my-50}, {mx-60} {my-50}, {mx} {my+15}", fill="none", stroke=COLOR_B, sw=1.5, dash="4,3"))
    f.append(path_svg(f"M {mx+mw} {my+mh-15} C {mx+mw+60} {my+mh+80}, {mx-60} {my+mh+80}, {mx} {my+mh-15}", fill="none", stroke=COLOR_B, sw=1.5, dash="4,3"))
    f.append(text(200, my - 45, "Лінії індукції B", size=10, color=COLOR_B))

    # Права панель: замкнений музпровід з повітряним зазором
    f.append(rect(400, 55, 360, 320, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(580, 80, "Магнітопровід з повітряним зазором", size=13, bold=True, color=INK))

    # П-подібний магнітопровід (м'яке залізо)
    f.append(rect(440, 120, 280, 170, fill="#e2e8f0", stroke=INK, sw=2, rx=6))
    f.append(rect(490, 160, 180, 90, fill="#ffffff", stroke=INK, sw=1.5, rx=4))

    # Вставка постійного магніту ліворуч у магнітопроводі
    f.append(rect(440, 160, 50, 90, fill="#bfdbfe", stroke=COLOR_B, sw=2, rx=0))
    f.append(text(465, 200, "Магніт", size=11, bold=True, color=COLOR_B))
    f.append(text(465, 215, "l_m", size=10, italic=True, color=INK))

    # Повітряний зазор праворуч у магнітопроводі
    f.append(rect(670, 185, 50, 40, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=0))
    f.append(text(695, 202, "Зазор", size=10, bold=True, color="#854d0e"))
    f.append(text(695, 216, "l_g", size=10, italic=True, color=INK))

    # Рівняння закон Кулона / Кирхгофа для кола
    f.append(text(580, 310, "H_m·l_m + H_g·l_g = 0  ⇒  H_m = −H_g·(l_g / l_m)", size=11, bold=True, color=INK))
    f.append(text(580, 335, "B_m·A_m = B_g·A_g  (збереження потоку)", size=11, color=MUTED))

    # Текстове пояснення внизу
    f.append(fitbox(40, 380, 700, 45,
                    "Розрив магнітного кола створює поверхневі магнітні полюси, які формують внутрішнє розмагнічувальне поле H_d.\nГеометрія магніту та розмір зазору визначають нахил робочої лінії B/H.",
                    size=11, fill="#f1f5f9", stroke=BORDER))

    return render(path, W, H_canvas, *f)

# ── Фігура 3: Робоча лінія (Load Line) та зміна геометрії ─────────────────────
def fig_load_line_operating_point(path):
    W, H_canvas = 780, 480
    f = []

    f.append(rect(0, 0, W, H_canvas, fill="#ffffff", stroke=BORDER, rx=0))
    f.append(text(W / 2, 28, "Робоча лінія (load line) та вплив коефіцієнта розмагнічування N", size=16, bold=True, color=INK))

    # Графік у 2 квадранті
    x0, y0 = 500, 390
    x_min = 100
    y_max = 70

    f.append(arrow(x0, y0, x_min - 30, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, y_max - 20, color=INK, sw=1.8))

    f.append(text(x_min - 40, y0 + 5, "H (кА/м)", size=13, bold=True, color=INK, anchor="end"))
    f.append(text(x0 + 15, y_max - 15, "B (Тл)", size=13, bold=True, color=INK, anchor="start"))

    y_Br = 110
    x_Hcb = 260

    # Крива B(H)
    d_B = f"M {x0} {y_Br} C {x0-120} {y_Br+20}, {x_Hcb+50} {y0-70}, {x_Hcb} {y0}"
    f.append(path_svg(d_B, fill="none", stroke=COLOR_B, sw=2.8))
    f.append(text(x0 + 10, y_Br + 5, "B_r", size=12, bold=True, color=COLOR_B, anchor="start"))

    # Робочі лінії з різними нахилами (P_c = |B/H|)
    x1, y1 = 440, 140
    f.append(line(x0, y0, x1 - 80, y1 - 60, color=COLOR_LOAD, sw=2))
    f.append(circle(x1, y1, 5, fill=POS, stroke=INK, sw=1))
    f.append(text(x1 - 10, y1 - 10, "P₁ (Довгий стержень, P_c > 10)", size=11, bold=True, color=COLOR_LOAD, anchor="end"))

    x2, y2 = 360, 205
    f.append(line(x0, y0, x2 - 120, y2 - 80, color=COLOR_LOAD, sw=2, dash="6,3"))
    f.append(circle(x2, y2, 5, fill=POS, stroke=INK, sw=1))
    f.append(text(x2 - 10, y2 - 12, "P_opt (Оптимум (BH)_max, P_c ≈ 1.2)", size=11, bold=True, color=COLOR_B, anchor="end"))

    x3, y3 = 280, 290
    f.append(line(x0, y0, x3 - 120, y3 - 50, color=COLOR_LOAD, sw=2))
    f.append(circle(x3, y3, 5, fill=COLOR_ALERT, stroke=INK, sw=1))
    f.append(text(x3 - 10, y3 + 18, "P₃ (Плоский диск, P_c < 0.5)", size=11, bold=True, color=COLOR_ALERT, anchor="end"))

    # Легенда праворуч
    leg_x, leg_y = 540, 100
    f.append(rect(leg_x, leg_y, 225, 170, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(leg_x + 112, leg_y + 22, "Коефіцієнт провідності P_c", size=12, bold=True, color=INK))

    f.append(text(leg_x + 15, leg_y + 50, "P_c = |B / H| = μ₀ · (1−N) / N", size=11, bold=True, color=COLOR_LOAD, anchor="start"))
    f.append(text(leg_x + 15, leg_y + 75, "Для прямого зазору:", size=11, color=MUTED, anchor="start"))
    f.append(text(leg_x + 15, leg_y + 95, "P_c = μ₀ · (A_g · l_m) / (A_m · l_g)", size=11, bold=True, color=INK, anchor="start"))

    f.append(line(leg_x + 15, leg_y + 115, leg_x + 210, leg_y + 115, color=BORDER, sw=1))
    f.append(text(leg_x + 15, leg_y + 135, "• N → 0 : P_c → ∞ (стержень)", size=10, color=INK, anchor="start"))
    f.append(text(leg_x + 15, leg_y + 152, "• N → 1 : P_c → 0 (пластина)", size=10, color=INK, anchor="start"))

    # Пояснювальний блок знизу
    f.append(fitbox(40, 415, 700, 45,
                    "Робоча точка P є перетином кривої розмагнічування B(H) та робочої лінії (load line).\nЧим коротший магніт уздовж осі намагнічування, тим більший N, пологиша робоча лінія і нижча робоча індукція B_op.",
                    size=11, fill="#f1f5f9", stroke=BORDER))

    return render(path, W, H_canvas, *f)

# ── Фігура 4: Лінія повернення (Recoil line) та незворотне розмагнічування ──────
def fig_recoil_dynamic_demag(path):
    W, H_canvas = 780, 480
    f = []

    f.append(rect(0, 0, W, H_canvas, fill="#ffffff", stroke=BORDER, rx=0))
    f.append(text(W / 2, 28, "Динамічна лінія повернення (recoil line) та точку згину кривої", size=16, bold=True, color=INK))

    x0, y0 = 540, 390
    x_min = 100
    y_max = 70

    f.append(arrow(x0, y0, x_min - 30, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, y_max - 20, color=INK, sw=1.8))

    f.append(text(x_min - 40, y0 + 5, "H (кА/м)", size=13, bold=True, color=INK, anchor="end"))
    f.append(text(x0 + 15, y_max - 15, "B (Тл)", size=13, bold=True, color=INK, anchor="start"))

    y_Br = 110
    x_knee = 260

    # Крива J(H) з чітким згином (knee)
    d_J = f"M {x0} {y_Br} L {x_knee+40} {y_Br} C {x_knee+10} {y_Br}, {x_knee} {y_Br+30}, {x_knee-40} {y0}"
    f.append(path_svg(d_J, fill="none", stroke=COLOR_J, sw=2, dash="4,4"))

    # Крива B(H) з точкою згину (knee point)
    d_B = f"M {x0} {y_Br} L {x_knee+40} {y_Br+30} C {x_knee+10} {y_Br+45}, {x_knee-10} {y0-60}, {x_knee-50} {y0}"
    f.append(path_svg(d_B, fill="none", stroke=COLOR_B, sw=2.5))

    # Точка згину (knee point)
    x_k, y_k = x_knee + 10, y_Br + 50
    f.append(circle(x_k, y_k, 5, fill=COLOR_ALERT, stroke=INK, sw=1))
    f.append(text(x_k - 12, y_k + 5, "Згин (knee point)", size=11, bold=True, color=COLOR_ALERT, anchor="end"))

    # Статична робоча точка Q0 (вище згину)
    x_q0, y_q0 = 420, 160
    f.append(circle(x_q0, y_q0, 5, fill=COLOR_LOAD, stroke=INK, sw=1))
    f.append(text(x_q0 + 10, y_q0 - 10, "Q₀ (Початкова робоча точка)", size=11, bold=True, color=COLOR_LOAD, anchor="start"))

    # Імпульс зовнішнього розмагнічувального поля H_ext відкидає точку за згин до Q1
    x_q1, y_q1 = 200, 310
    f.append(arrow(x_q0, y_q0, x_q1, y_q1, color=COLOR_ALERT, sw=2))
    f.append(circle(x_q1, y_q1, 5, fill=COLOR_ALERT, stroke=INK, sw=1))
    f.append(text(x_q1 - 10, y_q1 + 18, "Q₁ (Зовнішнє поле H_ext)", size=11, bold=True, color=COLOR_ALERT, anchor="end"))

    # Зняття поля: повернення по ЛІНІЇ ПОВЕРНЕННЯ (recoil line) до нової точки Q2
    x_q2, y_q2 = 420, 245
    d_recoil = f"M {x_q1} {y_q1} L {x_q2} {y_q2}"
    f.append(path_svg(d_recoil, fill="none", stroke=COLOR_RECOIL, sw=2.5))
    f.append(circle(x_q2, y_q2, 5, fill=COLOR_RECOIL, stroke=INK, sw=1))
    f.append(text(x_q2 + 12, y_q2 + 5, "Q₂ (Новий стан після розмагнічування)", size=11, bold=True, color=COLOR_RECOIL, anchor="start"))

    # Стрілка нахилу лінії повернення (mu_rec)
    f.append(text((x_q1 + x_q2)/2 - 20, (y_q1 + y_q2)/2 - 10, "Лінія повернення (μ_rec)", size=11, bold=True, color=COLOR_RECOIL))

    # Падіння індукції ΔB_irrev
    f.append(line(x_q0 + 30, y_q0, x_q0 + 30, y_q2, color=COLOR_ALERT, sw=1.5, dash="3,3"))
    f.append(arrow(x_q0 + 30, y_q0, x_q0 + 30, y_q2, color=COLOR_ALERT, sw=1.5))
    f.append(text(x_q0 + 40, (y_q0 + y_q2) / 2 + 4, "ΔB_irrev (Незворотна втрата)", size=11, bold=True, color=COLOR_ALERT, anchor="start"))

    # Пояснювальний текстовий блок знизу
    f.append(fitbox(40, 415, 700, 45,
                    "Якщо зовнішнє поле протитиску або підвищення температури зміщує робочу точку за точку згину (knee point),\nмагніт повертається вздовж лінії повернення з нахилом μ_rec, зазнаючи незворотної втрати намагніченості ΔB_irrev.",
                    size=11, fill="#f1f5f9", stroke=BORDER))

    return render(path, W, H_canvas, *f)

# ── Запуск генерації ────────────────────────────────────────────────────────
def main():
    figs = [
        ("quadrant2-demag-curves.svg", fig_quadrant2_demag_curves),
        ("magnetic-circuit-gap.svg", fig_magnetic_circuit_gap),
        ("load-line-operating-point.svg", fig_load_line_operating_point),
        ("recoil-dynamic-demag.svg", fig_recoil_dynamic_demag),
    ]

    for fname, func in figs:
        path = os.path.join(IMG_DIR, fname)
        func(path)
        print(f"Згенеровано: {path}")

if __name__ == "__main__":
    main()
