# -*- coding: utf-8 -*-
"""Фігури для теми «Коди з низькою щільністю перевірок на парність (LDPC)» (book/algorithms/complexity-computability/ldpc-codes)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
RED_F, RED_S = "#fef2f2", "#dc2626"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_tanner_graph_and_matrix():
    """tanner-graph-and-matrix.svg: Двочастковий граф Таннера та відповідна перевірочна матриця H."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Представлення LDPC-коду: перевірочна матриця H та граф Таннера", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Перевірочна матриця H (3x6)
    frags.append(rect(30, 60, 360, 350, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(210, 88, "Перевірочна матриця H (3 × 6)", size=14, bold=True, color="#334155"))

    # Таблиця 3x6
    grid_x0, grid_y0 = 80, 130
    cw, ch = 45, 45
    matrix_data = [
        [1, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 1, 0],
        [0, 0, 1, 0, 1, 1]
    ]

    # Заголовки стовпців (v1..v6)
    for j in range(6):
        frags.append(text(grid_x0 + j*cw + cw//2, grid_y0 - 10, f"v{j+1}", size=12, bold=True, color=BLUE_S))

    # Заголовки рядків (c1..c3)
    for i in range(3):
        frags.append(text(grid_x0 - 20, grid_y0 + i*ch + ch//2 + 4, f"c{i+1}", size=12, bold=True, color=GREEN_S))

    # Клітинки матриці
    for i in range(3):
        for j in range(6):
            val = matrix_data[i][j]
            bg = BLUE_F if val == 1 else "#ffffff"
            stk = BLUE_S if val == 1 else "#cbd5e1"
            txt_c = BLUE_S if val == 1 else "#94a3b8"
            frags.append(rect(grid_x0 + j*cw, grid_y0 + i*ch, cw, ch, fill=bg, stroke=stk, sw=1.5, rx=4))
            frags.append(text(grid_x0 + j*cw + cw//2, grid_y0 + i*ch + ch//2 + 4, str(val), size=14, bold=True, color=txt_c))

    frags.append(text(210, 310, "Специфіка LDPC: кожна строка/стовпець", size=12, color="#64748b"))
    frags.append(text(210, 330, "містить малу константну кількість одиниць", size=12, color="#64748b"))
    frags.append(text(210, 355, "Розрідженість: d_v = 2, d_c = 3", size=13, bold=True, color="#1e293b"))

    # Права панель: Двочастковий граф Таннера
    frags.append(rect(420, 60, 430, 350, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(635, 88, "Двочастковий граф Таннера", size=14, bold=True, color="#334155"))

    # Символьні вузли (Variable Nodes v1..v6) - ліворуч у графі
    v_pos = {}
    for j in range(6):
        x = 490
        y = 120 + j * 45
        v_pos[j+1] = (x, y)

    # Перевірочні вузли (Check Nodes c1..c3) - праворуч у графі
    c_pos = {}
    for i in range(3):
        x = 770
        y = 150 + i * 90
        c_pos[i+1] = (x, y)

    # Малювання ребер
    for i in range(3):
        for j in range(6):
            if matrix_data[i][j] == 1:
                x1, y1 = v_pos[j+1]
                x2, y2 = c_pos[i+1]
                frags.append(line(x1 + 18, y1, x2 - 18, y2, color="#475569", sw=1.8))

    # Малювання символьних вузлів (кола)
    for j in range(6):
        x, y = v_pos[j+1]
        frags.append(circle(x, y, 18, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
        frags.append(text(x, y + 4, f"v{j+1}", size=12, bold=True, color=BLUE_S))

    # Малювання перевірочних вузлів (квадрати)
    for i in range(3):
        x, y = c_pos[i+1]
        frags.append(rect(x - 18, y - 18, 36, 36, fill=GREEN_F, stroke=GREEN_S, sw=2.0, rx=4))
        frags.append(text(x, y + 4, f"c{i+1}", size=12, bold=True, color=GREEN_S))

    frags.append(text(490, 395, "Символьні вузли V (VN)", size=12, bold=True, color=BLUE_S))
    frags.append(text(770, 395, "Перевірочні вузли C (CN)", size=12, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "tanner-graph-and-matrix.svg"), W, H, *frags)

def fig_message_passing_decoding():
    """message-passing-decoding.svg: Ітеративна передача повідомлень у графі Таннера (Belief Propagation)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Ітеративний алгоритм передачі повідомлень (Message-Passing / Belief Propagation)", size=16, bold=True, color="#1e293b"))

    # Фаза 1: VN -> CN (Зліва направо)
    frags.append(rect(30, 60, 405, 330, fill="#ffffff", stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(232, 85, "Фаза 1: Повідомлення VN → CN (q_{v → c})", size=13, bold=True, color=BLUE_S))

    # Вузол v1
    frags.append(circle(80, 200, 22, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(80, 204, "v₁", size=13, bold=True, color=BLUE_S))

    # Вхідне канальне LLR
    frags.append(arrow(20, 200, 58, 200, color=AMBER_S, sw=2.0))
    frags.append(text(40, 185, "L_канал", size=11, bold=True, color=AMBER_S))

    # Сусідні c2 -> v1
    frags.append(arrow(80, 110, 80, 178, color=GREEN_S, sw=1.5))
    frags.append(text(105, 140, "r_{c₂ → v₁}", size=11, color=GREEN_S))

    # Вихідне q_{v1 -> c1}
    frags.append(arrow(102, 200, 330, 200, color=BLUE_S, sw=2.0))
    frags.append(rect(140, 175, 160, 48, fill=BLUE_F, stroke=BLUE_S, sw=1.0, rx=4))
    frags.append(text(220, 194, "q_{v₁ → c₁} = L₁ + r_{c₂ → v₁}", size=11, bold=True, color=BLUE_S))
    frags.append(text(220, 212, "(без вхідного r_{c₁ → v₁})", size=10, color="#64748b"))

    # Цільовий c1
    frags.append(rect(335, 182, 36, 36, fill=GREEN_F, stroke=GREEN_S, sw=2.0, rx=4))
    frags.append(text(353, 204, "c₁", size=12, bold=True, color=GREEN_S))

    # Фаза 2: CN -> VN (Справа наліво)
    frags.append(rect(445, 60, 405, 330, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(647, 85, "Фаза 2: Повідомлення CN → VN (r_{c → v})", size=13, bold=True, color=GREEN_S))

    # Вхідні q_{v2 -> c1}, q_{v3 -> c1}
    frags.append(arrow(490, 140, 740, 185, color=BLUE_S, sw=1.5))
    frags.append(text(550, 145, "q_{v₂ → c₁}", size=11, color=BLUE_S))

    frags.append(arrow(490, 260, 740, 215, color=BLUE_S, sw=1.5))
    frags.append(text(550, 265, "q_{v₃ → c₁}", size=11, color=BLUE_S))

    # Вузол c1
    frags.append(rect(745, 182, 36, 36, fill=GREEN_F, stroke=GREEN_S, sw=2.0, rx=4))
    frags.append(text(763, 204, "c₁", size=12, bold=True, color=GREEN_S))

    # Вихідне r_{c1 -> v1}
    frags.append(arrow(745, 200, 520, 200, color=GREEN_S, sw=2.0))
    frags.append(rect(540, 175, 170, 50, fill=GREEN_F, stroke=GREEN_S, sw=1.0, rx=4))
    frags.append(text(625, 193, "r_{c₁ → v₁} = f_CN(q_{v₂}, q_{v₃})", size=11, bold=True, color=GREEN_S))
    frags.append(text(625, 212, "Min-Sum / Sum-Product", size=10, color="#64748b"))

    # Цільовий v1
    frags.append(circle(480, 200, 22, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(480, 204, "v₁", size=13, bold=True, color=BLUE_S))

    # Принцип Extrinsic Information
    frags.append(text(440, 365, "Принцип зовнішньої інформації (Extrinsic Information):", size=12, bold=True, color="#1e293b"))
    frags.append(text(440, 385, "вузол не повертає зворотне повідомлення у той самий канал, з якого воно прийшло", size=11, color="#475569"))

    render(os.path.join(IMG, "message-passing-decoding.svg"), W, H, *frags)

def fig_girth_and_cycles():
    """girth-and-cycles.svg: Вплив коротких циклів (4-cycle) на незалежність повідомлень у графі Таннера."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Топологія графа Таннера: Обхват (Girth) та коротки цикли", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Короткий цикл завдовжки 4 (Girth = 4) - Шкідливо!
    frags.append(rect(30, 60, 405, 330, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(232, 85, "Шкідливий цикл завдовжки 4 (Girth = 4)", size=14, bold=True, color=RED_S))

    # Вузли циклу 4
    frags.append(circle(130, 150, 20, fill="#ffffff", stroke=BLUE_S, sw=2.0))
    frags.append(text(130, 154, "v₁", size=12, bold=True, color=BLUE_S))

    frags.append(circle(330, 150, 20, fill="#ffffff", stroke=BLUE_S, sw=2.0))
    frags.append(text(330, 154, "v₂", size=12, bold=True, color=BLUE_S))

    frags.append(rect(112, 252, 36, 36, fill="#ffffff", stroke=GREEN_S, sw=2.0, rx=4))
    frags.append(text(130, 274, "c₁", size=12, bold=True, color=GREEN_S))

    frags.append(rect(312, 252, 36, 36, fill="#ffffff", stroke=GREEN_S, sw=2.0, rx=4))
    frags.append(text(330, 274, "c₂", size=12, bold=True, color=GREEN_S))

    # Ребра циклу 4
    frags.append(line(130, 170, 130, 252, color=RED_S, sw=2.5))
    frags.append(line(330, 170, 330, 252, color=RED_S, sw=2.5))
    frags.append(line(148, 150, 310, 270, color=RED_S, sw=2.5))
    frags.append(line(310, 150, 148, 270, color=RED_S, sw=2.5))

    frags.append(text(232, 325, "Повідомлення повертається за 2 ітерації", size=12, bold=True, color=RED_S))
    frags.append(text(232, 345, "Втрата незалежності LLR → Корреляційне луна", size=11, color="#7f1d1d"))
    frags.append(text(232, 365, "Викликає передчасну позитивну кореляцію", size=11, color="#7f1d1d"))

    # Права панель: Локальне дерево (Girth >= 6) - Ідеально!
    frags.append(rect(445, 60, 405, 330, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(647, 85, "Деревоподібний окіл (Girth ≥ 6)", size=14, bold=True, color=GREEN_S))

    # Кореневий вузол v1
    frags.append(circle(647, 130, 20, fill="#ffffff", stroke=BLUE_S, sw=2.0))
    frags.append(text(647, 134, "v₁", size=12, bold=True, color=BLUE_S))

    # Рівень 1: CN c1, c2
    frags.append(rect(532, 200, 36, 36, fill="#ffffff", stroke=GREEN_S, sw=2.0, rx=4))
    frags.append(text(550, 222, "c₁", size=12, bold=True, color=GREEN_S))

    frags.append(rect(726, 200, 36, 36, fill="#ffffff", stroke=GREEN_S, sw=2.0, rx=4))
    frags.append(text(744, 222, "c₂", size=12, bold=True, color=GREEN_S))

    frags.append(line(632, 142, 563, 200, color=GREEN_S, sw=2.0))
    frags.append(line(662, 142, 731, 200, color=GREEN_S, sw=2.0))

    # Рівень 2: VN v2, v3, v4, v5
    v_leafs = [490, 610, 680, 800]
    for idx, lx in enumerate(v_leafs):
        frags.append(circle(lx, 280, 18, fill="#ffffff", stroke=BLUE_S, sw=2.0))
        frags.append(text(lx, 284, f"v{idx+2}", size=11, bold=True, color=BLUE_S))

    frags.append(line(540, 236, 495, 264, color=GREEN_S, sw=1.5))
    frags.append(line(560, 236, 605, 264, color=GREEN_S, sw=1.5))
    frags.append(line(735, 236, 690, 264, color=GREEN_S, sw=1.5))
    frags.append(line(755, 236, 795, 264, color=GREEN_S, sw=1.5))

    frags.append(text(647, 335, "Відсутність зациклень на K ітераціях", size=12, bold=True, color=GREEN_S))
    frags.append(text(647, 355, "Повідомлення статистично незалежні", size=11, color="#14532d"))
    frags.append(text(647, 375, "Точний збіг із теоретичною моделлю BP", size=11, color="#14532d"))

    render(os.path.join(IMG, "girth-and-cycles.svg"), W, H, *frags)

def fig_density_evolution_threshold():
    """density-evolution-threshold.svg: Залежність ймовірності помилки (BER) від SNR та поріг декодування."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Поведінка LDPC-коду: Границя Шеннона, Поріг декодування та Error Floor", size=16, bold=True, color="#1e293b"))

    # Осі графіку BER vs SNR
    ox, oy = 90, 350
    w_axis, h_axis = 720, 260

    frags.append(line(ox, oy, ox + w_axis, oy, color="#334155", sw=2.0))
    frags.append(line(ox, oy, ox, oy - h_axis, color="#334155", sw=2.0))

    frags.append(text(ox + w_axis//2, oy + 35, "Співвідношення сигнал/шум E_b / N_0 (дБ)", size=13, bold=True, color="#1e293b"))
    frags.append(text(40, oy - h_axis//2, "BER", size=13, bold=True, color="#1e293b"))

    # Засічки на осі Y (Log BER: 10^0, 10^-2, 10^-4, 10^-6)
    y_labels = ["10⁰", "10⁻²", "10⁻⁴", "10⁻⁶"]
    for i, lbl in enumerate(y_labels):
        y_pos = oy - i * 80
        frags.append(line(ox - 5, y_pos, ox, y_pos, color="#334155", sw=1.5))
        frags.append(text(ox - 25, y_pos + 4, lbl, size=11, color="#475569"))

    # Засічки на осі X (SNR: 0, 1, 2, 3, 4 dB)
    x_labels = ["0 дБ", "1 дБ", "2 дБ", "3 дБ", "4 дБ"]
    for i, lbl in enumerate(x_labels):
        x_pos = ox + i * 160
        frags.append(line(x_pos, oy, x_pos, oy + 5, color="#334155", sw=1.5))
        frags.append(text(x_pos, oy + 20, lbl, size=11, color="#475569"))

    # Вертикальна лінія Межа Шеннона (0.5 дБ -> x = 90 + 80 = 170)
    shannon_x = ox + 80
    frags.append(line(shannon_x, oy, shannon_x, oy - h_axis, color=PURPLE_S, sw=2.0, dash="5,5"))
    frags.append(text(shannon_x, oy - h_axis - 10, "Границя Шеннона", size=11, bold=True, color=PURPLE_S))

    # Вертикальна лінія Поріг LDPC (1.1 дБ -> x = 90 + 176 = 266)
    thresh_x = ox + 176
    frags.append(line(thresh_x, oy, thresh_x, oy - h_axis, color=GREEN_S, sw=2.0, dash="3,3"))
    frags.append(text(thresh_x + 35, oy - h_axis + 15, "Поріг LDPC (σ*)", size=11, bold=True, color=GREEN_S))

    # Крива 1: Без кодування (Uncoded BPSK)
    frags.append(line(ox, oy - 230, ox + 680, oy - 30, color="#94a3b8", sw=2.0))
    frags.append(text(ox + 540, oy - 70, "Без кодування", size=11, color="#64748b"))

    # Крива 2: Згортковий код
    frags.append(line(ox + 80, oy - 230, ox + 600, oy - 180, color=AMBER_S, sw=2.0))
    frags.append(text(ox + 500, oy - 195, "Згортковий код", size=11, color=AMBER_S))

    # Крива 3: LDPC-код (Падіння водоспадом / Waterfall region + Error Floor)
    ldpc_points = [
        (ox, oy - 220),
        (ox + 120, oy - 210),
        (thresh_x, oy - 190),       # Досягнення порогу
        (thresh_x + 40, oy - 100),   # Водоспад (Waterfall)
        (thresh_x + 80, oy - 20),    # Вихід на Error Floor
        (ox + 650, oy - 15)
    ]
    for i in range(len(ldpc_points) - 1):
        x1, y1 = ldpc_points[i]
        x2, y2 = ldpc_points[i+1]
        frags.append(line(x1, y1, x2, y2, color=BLUE_S, sw=3.0))

    frags.append(text(thresh_x + 90, oy - 120, "Область водоспаду (Waterfall)", size=11, bold=True, color=BLUE_S))

    # Підпис Error floor
    frags.append(rect(ox + 480, oy - 50, 180, 30, fill=RED_F, stroke=RED_S, sw=1.0, rx=4))
    frags.append(text(ox + 570, oy - 31, "Error Floor (Пастки)", size=11, bold=True, color=RED_S))

    render(os.path.join(IMG, "density-evolution-threshold.svg"), W, H, *frags)

def main():
    fig_tanner_graph_and_matrix()
    fig_message_passing_decoding()
    fig_girth_and_cycles()
    fig_density_evolution_threshold()
    print("Всі 4 фігури LDPC успішно згенеровано.")

if __name__ == "__main__":
    main()
