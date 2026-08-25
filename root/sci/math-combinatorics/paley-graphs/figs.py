# -*- coding: utf-8 -*-
"""Фігури для теми «Графи Пейлі (Paley Graphs)» (book/algorithms/complexity-computability/paley-graphs)."""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import rect, circle, line, text, textbox, render

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
RED_F, RED_S = "#fef2f2", "#dc2626"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_paley_p13_structure():
    """paley-p13-structure.svg: Кругова структура графа Пейлі P_13."""
    W, H = 880, 480
    frags = []

    frags.append(rect(10, 10, 860, 460, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Топологія графа Пейлі P₁₃ над полем F₁₃ (p = 13 ≡ 1 mod 4)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: кругове розміщення вершин
    cx, cy, r = 240, 250, 160
    n = 13
    residues = {1, 3, 4, 9, 10, 12}  # Квадратичні лишки mod 13

    # Координати вершин
    pts = []
    for i in range(n):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append((x, y))

    # Ребра: x ~ y iff (x - y) mod 13 in residues
    clique_nodes = {0, 1, 4}  # 1-0=1 in Q, 4-0=4 in Q, 4-1=3 in Q -> Кліка розміру 3

    for i in range(n):
        for j in range(i + 1, n):
            diff = (j - i) % n
            if diff in residues:
                is_clique_edge = (i in clique_nodes and j in clique_nodes)
                if is_clique_edge:
                    color = RED_S
                    sw = 2.8
                elif diff in (1, 12):
                    color = "#93c5fd"
                    sw = 1.2
                elif diff in (3, 10):
                    color = "#c084fc"
                    sw = 1.2
                else:  # diff in (4, 9)
                    color = "#86efac"
                    sw = 1.2
                frags.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], color=color, sw=sw))

    # Вершини
    for i in range(n):
        x, y = pts[i]
        if i in clique_nodes:
            frags.append(circle(x, y, 16, fill=RED_F, stroke=RED_S, sw=2.2))
            frags.append(text(x, y + 4, str(i), size=12, bold=True, color=RED_S))
        else:
            frags.append(circle(x, y, 14, fill=BLUE_F, stroke=BLUE_S, sw=1.6))
            frags.append(text(x, y + 4, str(i), size=11, bold=True, color=BLUE_S))

    # Права панель з поясненнями
    frags.append(rect(460, 60, 400, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(660, 85, "Алгебраїчні властивості P₁₃", size=14, bold=True, color="#1e293b"))

    lines_info = (
        "• Вершини: V = {0, 1, 2, ..., 12} = F₁₃\n"
        "• Квадратичні лишки Q: {1, 3, 4, 9, 10, 12}\n"
        "  (1²=1, 2²=4, 3²=9, 4²=3, 5²=12, 6²=10)\n"
        "• Нерегулярні нелишки N: {2, 5, 6, 7, 8, 11}\n\n"
        "• Регулярність: d = (13 - 1)/2 = 6 ребер на вузол\n"
        "• Самодоповнюваність: P₁₃ ≅ P̄₁₃\n"
        "  (множення на нелишок 2 переводить граф\n"
        "   у його точне доповнення)\n\n"
        "• Виділена червоним кліка {0, 1, 4}:\n"
        "  1 - 0 = 1 ∈ Q, 4 - 0 = 4 ∈ Q, 4 - 1 = 3 ∈ Q\n"
        "• Число кліки: ω(P₁₃) = 3\n"
        "• Число незалежності: α(P₁₃) = 3\n"
        "  (оцінка Гофмана: ω, α ≤ ⌊√13⌋ = 3)"
    )
    b_info, _, _ = textbox(660, 260, lines_info, size=11, fill=GRAY_F, stroke="#cbd5e1", pad=10)
    frags.append(b_info)

    render(os.path.join(IMG, "paley-p13-structure.svg"), W, H, *frags)


def fig_paley_srg_parameters():
    """paley-srg-parameters.svg: Сильно регулярні параметри графа Пейлі: сусіди суміжних і несуміжних вершин."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Сильно регулярний граф srg(q, (q-1)/2, (q-5)/4, (q-1)/4)", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Суміжні вершини (u ~ v) -> спільних сусідів λ = (q-5)/4
    frags.append(rect(30, 60, 395, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(227, 85, "Суміжні вершини (u ~ v) у P₁₃", size=13, bold=True, color=BLUE_S))

    # Вузли u=0 та v=1 (суміжні, бо 1-0 = 1 in Q)
    u_x, u_y = 120, 190
    v_x, v_y = 330, 190

    # Спільні сусіди: z ∈ {4, 10}, бо (4-0=4 ∈ Q, 4-1=3 ∈ Q) та (10-0=10 ∈ Q, 10-1=9 ∈ Q)
    z1_x, z1_y = 225, 130
    z2_x, z2_y = 225, 250

    # Ребро між u та v
    frags.append(line(u_x, u_y, v_x, v_y, color=BLUE_S, sw=2.5))
    frags.append(text(227, 198, "ребро (u ~ v)", size=10, bold=True, color=BLUE_S))

    # Ребра до спільних сусідів
    for zx, zy in [(z1_x, z1_y), (z2_x, z2_y)]:
        frags.append(line(u_x, u_y, zx, zy, color=GREEN_S, sw=1.8))
        frags.append(line(v_x, v_y, zx, zy, color=GREEN_S, sw=1.8))

    # Малювання вузлів
    frags.append(circle(u_x, u_y, 16, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(u_x, u_y + 4, "0", size=12, bold=True, color=BLUE_S))

    frags.append(circle(v_x, v_y, 16, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(v_x, v_y + 4, "1", size=12, bold=True, color=BLUE_S))

    frags.append(circle(z1_x, z1_y, 15, fill=GREEN_F, stroke=GREEN_S, sw=2.0))
    frags.append(text(z1_x, z1_y + 4, "4", size=11, bold=True, color=GREEN_S))

    frags.append(circle(z2_x, z2_y, 15, fill=GREEN_F, stroke=GREEN_S, sw=2.0))
    frags.append(text(z2_x, z2_y + 4, "10", size=11, bold=True, color=GREEN_S))

    b_left, _, _ = textbox(227, 335, "λ = (q - 5)/4 = (13 - 5)/4 = 2\nДля будь-якої пари суміжних вершин\nрівно 2 спільні сусіди (вузли 4 і 10)", size=11, fill=BLUE_F, stroke=BLUE_S, pad=8)
    frags.append(b_left)

    # Права панель: Несуміжні вершини (u ≁ w) -> спільних сусідів μ = (q-1)/4
    frags.append(rect(455, 60, 395, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(652, 85, "Несуміжні вершини (u ≁ w) у P₁₃", size=13, bold=True, color=RED_S))

    # Вузли u=0 та w=2 (несуміжні, бо 2-0 = 2 ∉ Q)
    u2_x, u2_y = 545, 190
    w_x, w_y = 755, 190

    # Пунктирна лінія відсутності ребра
    frags.append(line(u2_x, u2_y, w_x, w_y, color=GRAY_S, sw=1.5, dash="4 4"))
    frags.append(text(652, 198, "немає ребра (u ≁ w)", size=10, italic=True, color=GRAY_S))

    t1_x, t1_y = 652, 120
    t2_x, t2_y = 652, 160
    t3_x, t3_y = 652, 260

    for tx, ty in [(t1_x, t1_y), (t2_x, t2_y), (t3_x, t3_y)]:
        frags.append(line(u2_x, u2_y, tx, ty, color=PURPLE_S, sw=1.8))
        frags.append(line(w_x, w_y, tx, ty, color=PURPLE_S, sw=1.8))

    frags.append(circle(u2_x, u2_y, 16, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(u2_x, u2_y + 4, "0", size=12, bold=True, color=BLUE_S))

    frags.append(circle(w_x, w_y, 16, fill=RED_F, stroke=RED_S, sw=2.0))
    frags.append(text(w_x, w_y + 4, "2", size=12, bold=True, color=RED_S))

    frags.append(circle(t1_x, t1_y, 14, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8))
    frags.append(text(t1_x, t1_y + 4, "1", size=11, bold=True, color=PURPLE_S))

    frags.append(circle(t2_x, t2_y, 14, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8))
    frags.append(text(t2_x, t2_y + 4, "3", size=11, bold=True, color=PURPLE_S))

    frags.append(circle(t3_x, t3_y, 14, fill=PURPLE_F, stroke=PURPLE_S, sw=1.8))
    frags.append(text(t3_x, t3_y + 4, "12", size=11, bold=True, color=PURPLE_S))

    b_right, _, _ = textbox(652, 335, "μ = (q - 1)/4 = (13 - 1)/4 = 3\nДля будь-якої пари несуміжних вершин\nрівно 3 спільні сусіди (вузли 1, 3 і 12)", size=11, fill=PURPLE_F, stroke=PURPLE_S, pad=8)
    frags.append(b_right)

    render(os.path.join(IMG, "paley-srg-parameters.svg"), W, H, *frags)


def fig_paley_first_order_extension():
    """paley-first-order-extension.svg: Властивість розширення першого порядку A_{s, t} та апроксимація графа Радо."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Аксіома розширення першого порядку A_{s, t} у графах Пейлі", size=16, bold=True, color="#1e293b"))

    # Ліва область: Множини U та W
    frags.append(rect(30, 60, 470, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(265, 85, "Пошук вузла розширення z для неперетинних U і W", size=13, bold=True, color="#1e293b"))

    # Множина U (зелена рамка)
    frags.append(rect(50, 110, 160, 160, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(130, 130, "Множина U (|U| = s)", size=12, bold=True, color=GREEN_S))
    frags.append(text(130, 146, "всі мають бути суміжними", size=10, italic=True, color=GREEN_S))

    u_nodes = [(90, 185), (170, 185), (130, 235)]
    for i, (ux, uy) in enumerate(u_nodes):
        frags.append(circle(ux, uy, 14, fill="#ffffff", stroke=GREEN_S, sw=1.8))
        frags.append(text(ux, uy + 4, f"u{i+1}", size=10, bold=True, color=GREEN_S))

    # Множина W (червона рамка)
    frags.append(rect(50, 290, 160, 85, fill=RED_F, stroke=RED_S, sw=1.5, rx=6))
    frags.append(text(130, 310, "Множина W (|W| = t)", size=12, bold=True, color=RED_S))
    frags.append(text(130, 326, "всі мають бути несуміжними", size=10, italic=True, color=RED_S))

    w_nodes = [(90, 350), (170, 350)]
    for i, (wx, wy) in enumerate(w_nodes):
        frags.append(circle(wx, wy, 14, fill="#ffffff", stroke=RED_S, sw=1.8))
        frags.append(text(wx, wy + 4, f"w{i+1}", size=10, bold=True, color=RED_S))

    # Вузол z (справа в лівій панелі)
    zx, zy = 400, 220
    frags.append(circle(zx, zy, 22, fill=PURPLE_F, stroke=PURPLE_S, sw=2.5))
    frags.append(text(zx, zy + 5, "z", size=15, bold=True, color=PURPLE_S))
    frags.append(text(zx, zy + 38, "Вузол свідка z", size=11, bold=True, color=PURPLE_S))

    # Ребра від U до z (суцільні зелені)
    for ux, uy in u_nodes:
        frags.append(line(ux, uy, zx, zy, color=GREEN_S, sw=2.0))

    # Ребра від W до z (пунктирні червоні)
    for wx, wy in w_nodes:
        frags.append(line(wx, wy, zx, zy, color=RED_S, sw=1.5, dash="4 3"))

    # Права панель: Теорема Вейля та квазівипадковість
    frags.append(rect(515, 60, 335, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(682, 85, "Оцінка через суми Вейля", size=13, bold=True, color="#1e293b"))

    text_weil = (
        "Кількість свідків N(U, W):\n\n"
        "N(U, W) = ∑_{z ∉ U∪W} ∏_{u∈U} (1+χ(z-u))/2\n"
        "                   · ∏_{w∈W} (1-χ(z-w))/2\n\n"
        "За оцінкою характерних сум Вейля:\n"
        "| N(U,W) - q/2ˢ⁺ᵗ | ≤ 1/2 ( (s+t-2)√q + 1 )\n\n"
        "Умова існування свідка z:\n"
        "Якщо q > (s + t)² · 2²⁽ˢ⁺ᵗ⁾, то N(U, W) > 0.\n\n"
        "Наслідок для теорії моделей:\n"
        "Графи Пейлі є скінченними детермінованими\n"
        "апроксимаціями універсального випадкового\n"
        "графа Радо (Rado graph)."
    )
    b_weil, _, _ = textbox(682, 235, text_weil, size=11, fill=AMBER_F, stroke=AMBER_S, pad=10)
    frags.append(b_weil)

    render(os.path.join(IMG, "paley-first-order-extension.svg"), W, H, *frags)


def fig_paley_spectrum_gap():
    """paley-spectrum-gap.svg: Спектральний розподіл власних значень графа Пейлі P_q."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Спектр матриці суміжності A(P_q) та спектральна щілина", size=16, bold=True, color="#1e293b"))

    # Вісь спектра
    y_axis = 200
    frags.append(line(80, y_axis, 800, y_axis, color="#475569", sw=2.0))
    frags.append(line(440, y_axis - 15, 440, y_axis + 15, color="#94a3b8", sw=1.5))
    frags.append(text(440, y_axis + 35, "0", size=13, color="#64748b"))

    # Власне значення s = (-1 - √q)/2
    s_x = 280
    frags.append(line(s_x, y_axis - 40, s_x, y_axis + 40, color=RED_S, sw=3.0))
    frags.append(text(s_x, y_axis - 50, "s = (-1 - √q)/2", size=13, bold=True, color=RED_S))
    frags.append(text(s_x, y_axis + 35, "кратність (q-1)/2", size=11, color=RED_S))

    # Власне значення r = (-1 + √q)/2
    r_x = 560
    frags.append(line(r_x, y_axis - 40, r_x, y_axis + 40, color=GREEN_S, sw=3.0))
    frags.append(text(r_x, y_axis - 50, "r = (-1 + √q)/2", size=13, bold=True, color=GREEN_S))
    frags.append(text(r_x, y_axis + 35, "кратність (q-1)/2", size=11, color=GREEN_S))

    # Головне власне значення k = (q - 1)/2
    k_x = 760
    frags.append(line(k_x, y_axis - 50, k_x, y_axis + 50, color=BLUE_S, sw=3.5))
    frags.append(text(k_x, y_axis - 60, "k = (q - 1)/2", size=14, bold=True, color=BLUE_S))
    frags.append(text(k_x, y_axis + 35, "кратність 1 (вектор 1)", size=11, bold=True, color=BLUE_S))

    # Спектральна щілина
    frags.append(rect(r_x, 100, k_x - r_x, 32, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=4))
    frags.append(text((r_x + k_x) / 2, 121, "Спектральна щілина γ = k - r = (q - √q)/2", size=12, bold=True, color=PURPLE_S))

    # Нижній блок підсумку
    info_bottom = (
        "Властивості квазівипадковості та розширення:\n"
        "• Друге за модулем власне значення: λ(P_q) = max(|r|, |s|) = (1 + √q)/2 ≈ √q / 2\n"
        "• Нормоване розширення: λ(P_q) / k = (1 + √q)/(q - 1) = 1/(√q - 1) = O(1/√q) → 0 при q → ∞\n"
        "• Expander Mixing Lemma: для будь-яких S, T ⊂ V виконується | e(S,T) - |S|·|T|/2 | ≤ (√q / 2) · √(|S|·|T|)"
    )
    b_bot, _, _ = textbox(440, 315, info_bottom, size=11, fill="#ffffff", stroke="#cbd5e1", pad=10)
    frags.append(b_bot)

    render(os.path.join(IMG, "paley-spectrum-gap.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_paley_p13_structure()
    fig_paley_srg_parameters()
    fig_paley_first_order_extension()
    fig_paley_spectrum_gap()
    print("All figures generated successfully!")
