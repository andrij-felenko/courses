# -*- coding: utf-8 -*-
"""Фігури для теми «Теорема Рамсея» (book/algorithms/complexity-computability/ramseys-theorem)."""
import sys, os, math
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

def fig_party_problem():
    """fig1-party-problem.svg: Граф K6 із розфарбуванням ребер у 2 кольори та виділеним червоним трикутником K3."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Проблема вечірки: будь-яка розмальовка ребер K₆ містить монохроматичний K₃", size=16, bold=True, color="#1e293b"))

    # Позиції 6 вершин регулярного 6-кутника
    cx, cy, r = 320, 240, 150
    pts = []
    for i in range(6):
        angle = math.pi / 3 * i - math.pi / 2
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    # Матриця суміжності кольорів для цікавого розфарбування K6 з червоним трикутником (0, 2, 4)
    # 1 - Red, 0 - Blue
    colors = [
        [0, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0]
    ]

    # Намалюємо спочатку звичайні сині ребра
    for i in range(6):
        for j in range(i + 1, 6):
            if colors[i][j] == 0:
                frags.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], color=BLUE_S, sw=2))

    # Намалюємо червоні ребра (трикутник 0-2-4 товстішим)
    for i in range(6):
        for j in range(i + 1, 6):
            if colors[i][j] == 1:
                is_target = (i in (0, 2, 4)) and (j in (0, 2, 4))
                sw_val = 4.5 if is_target else 2.5
                frags.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], color=RED_S, sw=sw_val))

    # Вершини
    v_names = ["v₁", "v₂", "v₃", "v₄", "v₅", "v₆"]
    for i in range(6):
        px, py = pts[i]
        is_highlight = i in (0, 2, 4)
        f_col = RED_F if is_highlight else "#ffffff"
        s_col = RED_S if is_highlight else BLUE_S
        frags.append(circle(px, py, 18, fill=f_col, stroke=s_col, sw=2.5))
        frags.append(text(px, py + 4, v_names[i], size=13, bold=True, color="#1e293b"))

    # Пояснювальна панель праворуч
    panel_x, panel_y, panel_w, panel_h = 550, 70, 300, 340
    frags.append(rect(panel_x, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(panel_x + 150, panel_y + 30, "Аналіз принципом Діріхле", size=14, bold=True, color="#1e293b"))

    expl_str = (
        "1. Беремо довільну вершину v₁.\n"
        "   З неї виходить 5 ребер.\n\n"
        "2. За принципом Діріхле (Dirichlet):\n"
        "   принаймні ⌈5/2⌉ = 3 ребра\n"
        "   мають однаковий колір (напр. червоний).\n\n"
        "3. Нехай це ребра (v₁,v₃), (v₁,v₅), (v₁,v₆).\n\n"
        "4. Якщо між v₃, v₅, v₆ є хоч одне\n"
        "   червоне ребро → маємо червоний K₃.\n"
        "   Якщо всі ребра сині → маємо синій K₃.\n\n"
        "Висновок: R(3, 3) = 6."
    )
    b_expl, _, _ = textbox(panel_x + 150, panel_y + 195, expl_str, size=11, fill="#f8fafc", stroke=RED_S)
    frags.append(b_expl)

    render(os.path.join(IMG, "fig1-party-problem.svg"), W, H, *frags)


def fig_ramsey_recursion():
    """fig2-ramsey-recursion.svg: Рекурсивний розклад Вершини v для доведення нерівності Ердеша-Секереша R(r,s) <= R(r-1,s) + R(r,s-1)."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Схема рекурсивного доведення Ердеша — Секереша: R(r, s) ≤ R(r-1, s) + R(r, s-1)", size=15, bold=True, color="#1e293b"))

    # Верхня вершина v
    vx, vy = 440, 80
    frags.append(circle(vx, vy, 22, fill=AMBER_F, stroke=AMBER_S, sw=3))
    frags.append(text(vx, vy + 5, "v", size=16, bold=True, color="#1e293b"))
    frags.append(text(vx, vy - 32, "Довільна вершина в Kₙ (де n = R(r-1, s) + R(r, s-1))", size=12, italic=True, color="#475569"))

    # Блок ліворуч: Червоні сусіди V_R
    vr_x, vr_y, vr_w, vr_h = 60, 190, 340, 200
    frags.append(rect(vr_x, vr_y, vr_w, vr_h, fill=RED_F, stroke=RED_S, sw=2, rx=8))
    frags.append(text(vr_x + vr_w // 2, vr_y + 25, "Множина червоних сусідів V_R", size=13, bold=True, color=RED_S))
    frags.append(text(vr_x + vr_w // 2, vr_y + 48, "|V_R| ≥ R(r-1, s)", size=12, bold=True, color="#1e293b"))

    txt_vr = (
        "За визначенням числа Рамсея:\n"
        "V_R містить або:\n"
        "• Червоний K_{r-1} → разом з v\n"
        "  утворює Червоний K_r!\n"
        "• Синій K_s → вже є шуканим\n"
        "  синім графом!"
    )
    b_vr, _, _ = textbox(vr_x + vr_w // 2, vr_y + 130, txt_vr, size=11, fill="#ffffff", stroke=RED_S)
    frags.append(b_vr)

    # Блок праворуч: Сині сусіди V_B
    vb_x, vb_y, vb_w, vb_h = 480, 190, 340, 200
    frags.append(rect(vb_x, vb_y, vb_w, vb_h, fill=BLUE_F, stroke=BLUE_S, sw=2, rx=8))
    frags.append(text(vb_x + vb_w // 2, vb_y + 25, "Множина синіх сусідів V_B", size=13, bold=True, color=BLUE_S))
    frags.append(text(vb_x + vb_w // 2, vb_y + 48, "|V_B| ≥ R(r, s-1)", size=12, bold=True, color="#1e293b"))

    txt_vb = (
        "За визначенням числа Рамсея:\n"
        "V_B містить або:\n"
        "• Червоний K_r → вже є шуканим\n"
        "  червоним графом!\n"
        "• Синій K_{s-1} → разом з v\n"
        "  утворює Синій K_s!"
    )
    b_vb, _, _ = textbox(vb_x + vb_w // 2, vb_y + 130, txt_vb, size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_vb)

    # Стрілки / ребра від v до блоків
    frags.append(line(vx - 15, vy + 15, vr_x + vr_w // 2, vr_y, color=RED_S, sw=3))
    frags.append(text(300, 130, "Червоні ребра", size=11, bold=True, color=RED_S))

    frags.append(line(vx + 15, vy + 15, vb_x + vb_w // 2, vb_y, color=BLUE_S, sw=3))
    frags.append(text(560, 130, "Сині ребра", size=11, bold=True, color=BLUE_S))

    # Текст внизу
    frags.append(text(440, 420, "Принцип Діріхле: n - 1 = |V_R| + |V_B| ≥ R(r-1, s) + R(r, s-1) - 1", size=12, bold=True, color="#1e293b"))

    render(os.path.join(IMG, "fig2-ramsey-recursion.svg"), W, H, *frags)


def fig_bounds_gap():
    """fig3-bounds-gap.svg: Порівняння верхніх та нижніх асимптотичних меж для діагональних чисел Рамсея R(k, k)."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Асимптотична вилка діагональних чисел Рамсея R(k, k)", size=16, bold=True, color="#1e293b"))

    # Графічна рамка (координатні осі)
    ox, oy, gw, gh = 90, 380, 480, 310
    frags.append(line(ox, oy, ox + gw, oy, color="#64748b", sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color="#64748b", sw=2))

    frags.append(text(ox + gw // 2, oy + 35, "Розмір кліки k", size=12, bold=True, color="#1e293b"))
    frags.append(text(ox - 50, oy - gh // 2, "Оцінка R(k, k)", size=12, bold=True, color="#1e293b"))

    # Засічки на осі X (k = 3, 4, 5, 6, 8, 10)
    ks = [3, 4, 5, 6, 8, 10]
    for i, k in enumerate(ks):
        kx = ox + int((i + 0.5) * (gw / len(ks)))
        frags.append(line(kx, oy, kx, oy + 5, color="#64748b", sw=1.5))
        frags.append(text(kx, oy + 20, str(k), size=11, color="#334155"))

    # Криві
    pts_upper = []
    pts_lower = []
    pts_break = []
    for i, k in enumerate(ks):
        kx = ox + int((i + 0.5) * (gw / len(ks)))
        y_up = oy - int(30 + 25 * (k**1.4))
        y_low = oy - int(15 + 6 * (2**(k/2)))
        y_brk = oy - int(25 + 18 * (k**1.3))
        pts_upper.append((kx, max(oy - gh + 20, y_up)))
        pts_lower.append((kx, max(oy - gh + 20, y_low)))
        pts_break.append((kx, max(oy - gh + 20, y_brk)))

    # Малюємо криві
    for i in range(len(ks) - 1):
        frags.append(line(pts_upper[i][0], pts_upper[i][1], pts_upper[i+1][0], pts_upper[i+1][1], color=RED_S, sw=3))
        frags.append(line(pts_break[i][0], pts_break[i][1], pts_break[i+1][0], pts_break[i+1][1], color=PURPLE_S, sw=2.5))
        frags.append(line(pts_lower[i][0], pts_lower[i][1], pts_lower[i+1][0], pts_lower[i+1][1], color=GREEN_S, sw=3))

    # Точки на кривих
    for p in pts_upper:
        frags.append(circle(p[0], p[1], 4, fill=RED_S, stroke="#ffffff", sw=1))
    for p in pts_break:
        frags.append(circle(p[0], p[1], 4, fill=PURPLE_S, stroke="#ffffff", sw=1))
    for p in pts_lower:
        frags.append(circle(p[0], p[1], 4, fill=GREEN_S, stroke="#ffffff", sw=1))

    # Легенда та пояснення праворуч
    lx, ly = 600, 70
    frags.append(rect(lx, ly, 250, 320, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(lx + 125, ly + 25, "Межі R(k, k)", size=14, bold=True, color="#1e293b"))

    # Верхня класична
    frags.append(line(lx + 15, ly + 65, lx + 45, ly + 65, color=RED_S, sw=3))
    frags.append(text(lx + 135, ly + 65, "Верхня класична (1935):\nR(k, k) ≤ 4ᵏ / √(πk)", size=11, bold=True, color=RED_S))

    # Верхня проривна 2023
    frags.append(line(lx + 15, ly + 135, lx + 45, ly + 135, color=PURPLE_S, sw=2.5))
    frags.append(text(lx + 135, ly + 135, "Прорив Кампоса та ін. (2023):\nR(k, k) ≤ (4 - ε)ᵏ", size=11, bold=True, color=PURPLE_S))

    # Нижня імовірнісна
    frags.append(line(lx + 15, ly + 205, lx + 45, ly + 205, color=GREEN_S, sw=3))
    frags.append(text(lx + 135, ly + 205, "Нижня імовірнісна (1947):\nR(k, k) > √2ᵏ  = 2ᵏ/²", size=11, bold=True, color=GREEN_S))

    # Зона невідомого
    b_unk, _, _ = textbox(lx + 125, ly + 275, "Експоненціальний розрив\nміж √2 та 4 залишається\nвідкритим задачею!", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_unk)

    render(os.path.join(IMG, "fig3-bounds-gap.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_party_problem()
    fig_ramsey_recursion()
    fig_bounds_gap()
    print("Figures generated successfully.")
