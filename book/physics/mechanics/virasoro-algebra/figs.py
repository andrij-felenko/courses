# -*- coding: utf-8 -*-
"""Фігури до статті «Алгебра Вірасоро та конформна аномалія».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Fig 1: Конформні генератори та векторні поля на колі ───────────────────────
def fig_conformal_mapping_circle():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Геометрична інтерпретація генераторів Вірасоро Lₙ на колі S¹", size=15, bold=True))

    # Схема трьох базових випадків: L_-1 (перенос), L_0 (дилатація), L_1 (спеціальне конформне)
    centers = [(150, 240, "L₋₁ = -∂/∂z", "Трансляція (зсув)", POS),
               (410, 240, "L₀ = -z ∂/∂z", "Масштабування (дилатація)", FIELD),
               (670, 240, "L₁ = -z² ∂/∂z", "Спеціальне конформне", NEG)]

    R = 85
    for cx, cy, label_mode, label_desc, col in centers:
        # Зовнішній фон
        f.append(circle(cx, cy, R + 25, fill="#f8fafc", stroke="#e2e8f0", sw=1.2))
        # Одиничне коло S^1
        f.append(circle(cx, cy, R, fill="none", stroke="#94a3b8", sw=2.0))

        # Осі координат
        f.append(line(cx - R - 20, cy, cx + R + 20, cy, color="#cbd5e1", sw=1.0))
        f.append(line(cx, cy - R - 20, cx, cy + R + 20, color="#cbd5e1", sw=1.0))

        # Накреслити стрілки векторного поля вздовж кола
        n_arrows = 12
        for i in range(n_arrows):
            angle = 2 * math.pi * i / n_arrows
            px = cx + R * math.cos(angle)
            py = cy - R * math.sin(angle)

            # Вектор генератора в залежності від mode
            if "L₋₁" in label_mode:
                # Постійний вектор напрямку x
                vx, vy = 22, 0
            elif "L₀" in label_mode:
                # Радіальний вектор від центру або донгенціальний
                vx = 22 * math.cos(angle)
                vy = -22 * math.sin(angle)
            else:
                # L_1: пропорційно z^2
                vx = 22 * math.cos(2 * angle)
                vy = -22 * math.sin(2 * angle)

            f.append(arrow(px, py, px + vx, py + vy, color=col, sw=2.0))
            f.append(circle(px, py, 3, fill=col, stroke=col, sw=1))

        # Заголовки точок
        lb1, w1, h1 = textbox(cx, cy - R - 45, label_mode, size=13, pad=6, fill="#ffffff", stroke=col, sw=1.5, bold=True, color=INK)
        f.append(lb1)

        lb2, w2, h2 = textbox(cx, cy + R + 45, label_desc, size=11, pad=5, fill="#ffffff", stroke="#cbd5e1", sw=1.0, color=MUTED)
        f.append(lb2)

    # Загальний підпис знизу
    f.append(text(W / 2, H - 20, "Підалгебра sl(2,ℂ) = {L₋₁, L₀, L₁} формує глобальні конформні перетворення сфери Рімана", size=12, color=INK, italic=True))

    render(os.path.join(IMG, 'conformal-mapping-circle.svg'), W, H, *f)


# ── Fig 2: Модуль Верма та ієрархія станів ────────────────────────────────────
def fig_verma_module_tree():
    W, H = 820, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Структура модуля Верма V(c, h) та рівня збуджень", size=15, bold=True))

    # Рівні N = 0, 1, 2, 3
    levels = [
        (0, 80, ["|h, c⟩"], "Основний стан (первинне поле), Lₙ|h⟩ = 0 (n > 0)", POS),
        (1, 170, ["L₋₁|h, c⟩"], "Рівень N = 1 (вимірність 1)", FIELD),
        (2, 280, ["L₋₂|h, c⟩", "L₋₁²|h, c⟩"], "Рівень N = 2 (вимірність 2, p(2) = 2)", NEG),
        (3, 400, ["L₋₃|h, c⟩", "L₋₁L₋₂|h, c⟩", "L₋₁³|h, c⟩"], "Рівень N = 3 (вимірність 3, p(3) = 3)", "#7c3aed"),
    ]

    # Малюємо горизонтальні пунктирні лінії рівнів
    for N, y, states, desc, col in levels:
        f.append(line(70, y, W - 70, y, color="#e2e8f0", sw=1.5, dash="6,4"))
        f.append(text(100, y - 18, f"N = {N}", size=13, color=col, bold=True, anchor="start"))
        f.append(text(W - 80, y - 18, desc, size=11, color=MUTED, anchor="end"))

        # Розміщення вузлів станів
        n_st = len(states)
        step_x = 240
        start_x = W / 2 - (n_st - 1) * step_x / 2
        for idx, st in enumerate(states):
            nx = start_x + idx * step_x
            tb, tw, th = textbox(nx, y, st, size=13, pad=8, fill="#ffffff", stroke=col, sw=1.8, color=INK, bold=True)
            f.append(tb)

            # Лінії зв'язку від попереднього рівня
            if N == 1:
                f.append(arrow(W / 2, 100, nx, y - 18, color=MUTED, sw=1.2))
            elif N == 2:
                f.append(arrow(W / 2, 190, nx, y - 18, color=MUTED, sw=1.2))
            elif N == 3:
                # Зв'язки від 2 до 3
                parent_x = W / 2 - step_x / 2 if idx < 2 else W / 2 + step_x / 2
                f.append(arrow(parent_x, 300, nx, y - 18, color=MUTED, sw=1.2))

    # Рамка детермінанта Каца
    lb_kac, kw, kh = textbox(W / 2, H - 35, "Визначник Каца det M^(N)(c, h) = 0 визначає наявність нуль-векторів та вироджень", size=12, pad=7, fill="#fffbebe6", stroke="#f59e0b", sw=1.5, color=INK, bold=True)
    f.append(lb_kac)

    render(os.path.join(IMG, 'verma-module-tree.svg'), W, H, *f)


# ── Fig 3: Від циліндра до комплексної площини у теорії струн ─────────────────
def fig_string_worldsheet_conformal():
    W, H = 820, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Відображення світової поверхні струни z = exp(τ + iσ)", size=15, bold=True))

    # Ліворуч: Світовий циліндр (tau, sigma)
    f.append(text(200, 60, "Світовий циліндр (τ, σ)", size=14, bold=True, color=POS))
    f.append(rect(100, 90, 200, 280, fill="#eff6ff", stroke=POS, sw=1.8, rx=8))

    # Сітка на циліндрі
    for t_y in [140, 190, 240, 290, 340]:
        f.append(line(100, t_y, 300, t_y, color="#93c5fd", sw=1.2, dash="4,3"))
    for s_x in [140, 180, 220, 260]:
        f.append(line(s_x, 90, s_x, 370, color="#93c5fd", sw=1.2, dash="4,3"))

    f.append(arrow(100, 395, 300, 395, color=POS, sw=1.5))
    f.append(text(200, 415, "Час τ ∈ (-∞, +∞)", size=11, color=POS))

    f.append(arrow(80, 370, 80, 90, color=FIELD, sw=1.5))
    f.append(text(50, 230, "σ ∈ [0, 2π]", size=11, color=FIELD))

    # Центр: Конформний перехід z = e^(tau + i sigma)
    f.append(arrow(320, 230, 450, 230, color=INK, sw=2.5))
    lb_map, mw, mh = textbox(385, 200, "z = e^(τ + iσ)\n(Конформне відображення)", size=12, pad=6, fill="#ffffff", stroke="#64748b", sw=1.2, color=INK, bold=True)
    f.append(lb_map)

    # Праворуч: Комплексна площина z
    f.append(text(640, 60, "Комплексна площина z", size=14, bold=True, color=NEG))
    cx, cy = 640, 230
    f.append(circle(cx, cy, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))

    # Концентричні кола (tau = const)
    for r in [30, 60, 90, 120]:
        f.append(circle(cx, cy, r, fill="none", stroke="#93c5fd", sw=1.2))

    # Промені (sigma = const)
    for a_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(a_deg)
        f.append(line(cx, cy, cx + 130 * math.cos(rad), cy - 130 * math.sin(rad), color="#93c5fd", sw=1.2, dash="4,3"))

    # Осі z
    f.append(arrow(cx - 145, cy, cx + 145, cy, color=INK, sw=1.5))
    f.append(arrow(cx, cy + 145, cx, cy - 145, color=INK, sw=1.5))
    f.append(text(cx + 130, cy + 18, "Re(z)", size=11, color=INK))
    f.append(text(cx + 15, cy - 130, "Im(z)", size=11, color=INK))

    # Точка минулого tau -> -infinity у z = 0
    f.append(circle(cx, cy, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(cx - 45, cy + 18, "τ → -∞ (z=0)", size=10, color=POS, bold=True))

    f.append(text(W / 2, H - 15, "Операторний розклад T(z) = ∑ Lₙ z⁻ⁿ⁻² перетворює модові амплітуди на генератори Вірасоро", size=12, color=INK, italic=True))

    render(os.path.join(IMG, 'string-worldsheet-conformal.svg'), W, H, *f)


# ── Fig 4: Баланс та компенсація центрального заряду ─────────────────────────
def fig_anomaly_cancellation_diagram():
    W, H = 820, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Механізм компенсації конформної аномалії c_total = c_matter + c_ghost = 0", size=15, bold=True))

    # Два блоки: матерія та духи Фадеєва-Попова
    tb_m, wm, hm = textbox(240, 140, "Матеріальний сектор (Бозони Xᵐ)\nc_matter = D\n(+1 на кожен просторово-часовий вимір)", size=13, pad=10, fill="#eff6ff", stroke=NEG, sw=1.8, color=INK, bold=True)
    f.append(tb_m)

    tb_g, wg, hg = textbox(580, 140, "Духовий сектор BRST (Духи b, c)\nc_ghost = -26\n(-26 від калібрування дифеоморфізмів)", size=13, pad=10, fill="#fff1f2", stroke=POS, sw=1.8, color=INK, bold=True)
    f.append(tb_g)

    # Стрілки сумування до центрального вузла
    f.append(arrow(240, 200, 360, 270, color=NEG, sw=2.0))
    f.append(arrow(580, 200, 460, 270, color=POS, sw=2.0))

    # Підсумковий вузол квантової узгодженості
    tb_tot, wt, ht = textbox(410, 300, "Повна конформна аномалія:\nc_total = D - 26 = 0  ⇒  D = 26", size=14, pad=12, fill="#f0fdf4", stroke=FIELD, sw=2.2, color=INK, bold=True)
    f.append(tb_tot)

    # Нижня аналітична рамка про наслідки
    tb_res, wr, hr = textbox(410, 400, "Умови D = 26 (бозонна струна) та D = 10 (суперструна, c_ghost = -15) усувають духи з від'ємною нормою (No-Ghost Theorem)", size=11.5, pad=6, fill="#ffffff", stroke="#94a3b8", sw=1.2, color=MUTED, bold=False)
    f.append(tb_res)

    render(os.path.join(IMG, 'anomaly-cancellation-diagram.svg'), W, H, *f)


if __name__ == '__main__':
    fig_conformal_mapping_circle()
    fig_verma_module_tree()
    fig_string_worldsheet_conformal()
    fig_anomaly_cancellation_diagram()
    print("Всі фігури успішно згенеровано у ./img/")
