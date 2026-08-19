#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор фігур до теми «Теорія перколації» (percolation-theory)."""

import os
import sys

# Підключаємо svgkit з кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_site_vs_bond():
    """Фігура 1: Порівняння вузлової (Site) та реберної (Bond) перколації на 2D-ґратці."""
    w, h = 820, 420
    frags = []

    # Заголовок загальний
    frags.append(text(w / 2, 28, "Вузлова (Site) та реберна (Bond) перколація на квадратній ґратці", size=16, bold=True))

    # --- Ліва панель: Вузлова перколація ---
    lx0, ly0 = 30, 60
    pw, ph = 365, 330
    frags.append(rect(lx0, ly0, pw, ph, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(lx0 + pw / 2, ly0 + 26, "Вузлова перколація (Site)", size=14, bold=True, color=POS))
    frags.append(text(lx0 + pw / 2, ly0 + 46, "Випадково зайняті вузли (ймовірність p)", size=12, color=MUTED))

    # Малюємо сітку вузлів 5x5
    # Конфігурація зайнятості для Site (1 - зайнятий, 0 - порожній)
    # Зробимо прохідний кластер (зелений/активний) і ізольовані вузли
    site_grid = [
        [0, 1, 1, 0, 1],
        [1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [1, 0, 1, 1, 1],
        [0, 1, 0, 1, 0]
    ]
    # Кластер, що протікає зверху вниз: (0,1)->(0,2)->(1,1)->(2,1)->(2,2)->(2,3)->(3,2)->(3,3)->(4,3)
    span_cluster = {(0, 1), (0, 2), (1, 1), (2, 1), (2, 2), (2, 3), (3, 2), (3, 3), (4, 3), (3, 4)}

    gx0, gy0 = lx0 + 45, ly0 + 75
    step = 55

    # Сітка ліній (пунктир як фон)
    for r in range(5):
        frags.append(line(gx0, gy0 + r * step, gx0 + 4 * step, gy0 + r * step, color="#d0d7de", sw=1, dash="3,3"))
    for c in range(5):
        frags.append(line(gx0 + c * step, gy0, gx0 + c * step, gy0 + 4 * step, color="#d0d7de", sw=1, dash="3,3"))

    # Зв'язки між зайнятими сусідніми вузлами
    for r in range(5):
        for c in range(5):
            if site_grid[r][c] == 1:
                # Вправо
                if c + 1 < 5 and site_grid[r][c + 1] == 1:
                    is_span = (r, c) in span_cluster and (r, c + 1) in span_cluster
                    col = FIELD if is_span else "#57606a"
                    sw_val = 3.5 if is_span else 2.0
                    frags.append(line(gx0 + c * step, gy0 + r * step, gx0 + (c + 1) * step, gy0 + r * step, color=col, sw=sw_val))
                # Вниз
                if r + 1 < 5 and site_grid[r + 1][c] == 1:
                    is_span = (r, c) in span_cluster and (r + 1, c) in span_cluster
                    col = FIELD if is_span else "#57606a"
                    sw_val = 3.5 if is_span else 2.0
                    frags.append(line(gx0 + c * step, gy0 + r * step, gx0 + c * step, gy0 + (r + 1) * step, color=col, sw=sw_val))

    # Вузли
    for r in range(5):
        for c in range(5):
            cx = gx0 + c * step
            cy = gy0 + r * step
            if site_grid[r][c] == 1:
                if (r, c) in span_cluster:
                    frags.append(circle(cx, cy, 11, fill="#d4edda", stroke=FIELD, sw=2.5))
                else:
                    frags.append(circle(cx, cy, 9, fill="#e1e4e8", stroke="#57606a", sw=1.8))
            else:
                frags.append(circle(cx, cy, 6, fill="#ffffff", stroke="#c0c4c8", sw=1.2))

    # Пояснення внизу лівої панелі
    frags.append(text(lx0 + pw / 2, ly0 + ph - 18, "Зелений: перколяційний кластер між краями", size=11, color=FIELD, bold=True))

    # --- Права панель: Реберна перколація ---
    rx0 = lx0 + pw + 30
    frags.append(rect(rx0, ly0, pw, ph, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(rx0 + pw / 2, ly0 + 26, "Реберна перколація (Bond)", size=14, bold=True, color=NEG))
    frags.append(text(rx0 + pw / 2, ly0 + 46, "Всі вузли існують, ребра відкриті з ймовірністю p", size=12, color=MUTED))

    rgx0, rgy0 = rx0 + 45, ly0 + 75

    # Горизонтальні ребра (5 рядків по 4 ребра)
    h_bonds = [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [1, 1, 0, 1],
        [0, 1, 1, 1],
        [1, 0, 1, 0]
    ]
    # Вертикальні ребра (4 проміжки по 5 ребер)
    v_bonds = [
        [0, 1, 1, 0, 0],
        [1, 1, 0, 1, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 1, 0, 1]
    ]

    # Пунктирна фонова сітка для закритих ребер
    for r in range(5):
        frags.append(line(rgx0, rgy0 + r * step, rgx0 + 4 * step, rgy0 + r * step, color="#e5e8eb", sw=1, dash="2,2"))
    for c in range(5):
        frags.append(line(rgx0 + c * step, rgy0, rgx0 + c * step, rgy0 + 4 * step, color="#e5e8eb", sw=1, dash="2,2"))

    # Відкриті горизонтальні ребра
    for r in range(5):
        for c in range(4):
            if h_bonds[r][c] == 1:
                frags.append(line(rgx0 + c * step, rgy0 + r * step, rgx0 + (c + 1) * step, rgy0 + r * step, color=NEG, sw=3))

    # Відкриті вертикальні ребра
    for r in range(4):
        for c in range(5):
            if v_bonds[r][c] == 1:
                frags.append(line(rgx0 + c * step, rgy0 + r * step, rgx0 + c * step, rgy0 + (r + 1) * step, color=NEG, sw=3))

    # Вузли (всі присутні)
    for r in range(5):
        for c in range(5):
            cx = rgx0 + c * step
            cy = rgy0 + r * step
            frags.append(circle(cx, cy, 6, fill="#2457d6", stroke="#1d44a8", sw=1.5))

    frags.append(text(rx0 + pw / 2, ly0 + ph - 18, "Синій: відкриті зв'язки провідності", size=11, color=NEG, bold=True))

    render(os.path.join(IMG_DIR, "site-vs-bond-percolation.svg"), w, h, *frags)


def fig_phase_transition():
    """Фігура 2: Фазовий перехід другого роду та сингулярності при p_c."""
    w, h = 800, 420
    frags = []

    frags.append(text(w / 2, 26, "Фазовий перехід другого роду: потужність кластера та сприйнятливість", size=16, bold=True))

    # Вісь координат
    ox, oy = 90, 340
    pw, ph = 620, 260

    # Фонова сітка і вісі
    frags.append(line(ox, oy, ox + pw, oy, color=LINE, sw=2))  # вісь X
    frags.append(line(ox, oy, ox, oy - ph, color=LINE, sw=2))  # вісь Y

    # Стрілки осей
    frags.append(arrow(ox + pw, oy, ox + pw + 25, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy - ph, ox, oy - ph - 20, color=LINE, sw=2))

    frags.append(text(ox + pw + 35, oy + 5, "p", size=15, bold=True, anchor="start"))
    frags.append(text(ox - 10, oy - ph - 25, "P∞(p), χ(p)", size=14, bold=True, anchor="middle"))

    # Позначки по осі X
    frags.append(text(ox, oy + 20, "0", size=12, color=MUTED))
    frags.append(text(ox + pw, oy + 20, "1.0", size=12, color=MUTED))

    # Критична точка p_c (на 60% ширини ~ 0.593)
    pc_x = ox + int(pw * 0.593)
    frags.append(line(pc_x, oy, pc_x, oy - ph + 20, color=POS, sw=1.5, dash="4,4"))
    frags.append(circle(pc_x, oy, 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(pc_x, oy + 22, "pc ≈ 0.5927", size=13, bold=True, color=POS))

    # Крива P_infinity(p) (порядок): 0 при p < p_c, потім зростає як (p - p_c)^beta (beta = 5/36 ~ 0.139)
    # Дуже крутий підйом біля p_c
    pts_p = []
    # від 0 до pc_x: лінія 0
    pts_p.append((ox, oy))
    pts_p.append((pc_x, oy))
    # від pc_x до 1.0: зростання
    steps = 40
    for i in range(1, steps + 1):
        frac = i / float(steps)
        p_val = 0.593 + frac * (1.0 - 0.593)
        # (p - pc)^0.14
        y_val = ((p_val - 0.593) / (1.0 - 0.593)) ** 0.35  # візуальне масштабування
        px = pc_x + frac * (ox + pw - pc_x)
        py = oy - y_val * (ph - 40)
        pts_p.append((px, py))

    # Малюємо криву P_infinity товстою зеленою лінією
    for i in range(len(pts_p) - 1):
        x1, y1 = pts_p[i]
        x2, y2 = pts_p[i + 1]
        frags.append(line(x1, y1, x2, y2, color=FIELD, sw=3.5))

    # Крива chi(p) (середній розмір скінченних кластерів / сприйнятливість): розбігається в p_c як |p - p_c|^-gamma
    pts_chi_left = []
    for i in range(30):
        frac = i / 30.0
        p_val = 0.1 + frac * (0.593 - 0.1 - 0.02)
        dist = 0.593 - p_val
        val = 0.05 + 0.08 / (dist ** 0.8)
        val = min(val, 1.0)
        px = ox + (p_val / 1.0) * pw
        py = oy - val * (ph - 50)
        pts_chi_left.append((px, py))

    pts_chi_right = []
    for i in range(30):
        frac = i / 30.0
        p_val = 0.593 + 0.02 + frac * (0.95 - 0.593 - 0.02)
        dist = p_val - 0.593
        val = 0.05 + 0.08 / (dist ** 0.8)
        val = min(val, 1.0)
        px = ox + (p_val / 1.0) * pw
        py = oy - val * (ph - 50)
        pts_chi_right.append((px, py))

    for i in range(len(pts_chi_left) - 1):
        frags.append(line(pts_chi_left[i][0], pts_chi_left[i][1], pts_chi_left[i + 1][0], pts_chi_left[i + 1][1], color=NEG, sw=2, dash="5,3"))
    for i in range(len(pts_chi_right) - 1):
        frags.append(line(pts_chi_right[i][0], pts_chi_right[i][1], pts_chi_right[i + 1][0], pts_chi_right[i + 1][1], color=NEG, sw=2, dash="5,3"))

    # Пояснювальні плашки з формулами та описами (через fitbox / textbox)
    t1, _, _ = textbox(ox + 130, oy - 210, "Підкритичний режим (p < pc)\nНемає нескінченного кластера: P∞ = 0\nЛише ізольовані острівці", size=12, fill="#f8f9fa", stroke="#d0d7de")
    frags.append(t1)

    t2, _, _ = textbox(ox + pw - 100, oy - 140, "Надкритичний режим (p > pc)\nP∞(p) ∝ (p − pc)ᵝ\nУтворюється гігантський кластер", size=12, fill="#e8f5e9", stroke=FIELD, color="#1b5e20")
    frags.append(t2)

    t3, _, _ = textbox(pc_x, oy - ph + 45, "Критична точка pc\nСприйнятливість розбігається:\nχ(p) ∝ |p − pc|⁻ᵞ", size=12, fill="#e3f2fd", stroke=NEG, color="#0d47a1")
    frags.append(t3)

    # Легенда
    leg_x, leg_y = ox + 40, oy - 60
    frags.append(line(leg_x, leg_y, leg_x + 35, leg_y, color=FIELD, sw=3.5))
    frags.append(text(leg_x + 45, leg_y + 4, "P∞(p) — частка вузлів у нескінченному кластері", size=12, anchor="start", bold=True))

    frags.append(line(leg_x, leg_y + 22, leg_x + 35, leg_y + 22, color=NEG, sw=2, dash="5,3"))
    frags.append(text(leg_x + 45, leg_y + 26, "χ(p) — середній розмір скінченних кластерів", size=12, anchor="start", color=NEG))

    render(os.path.join(IMG_DIR, "percolation-phase-transition.svg"), w, h, *frags)


def fig_dual_lattice():
    """Фігура 3: Планарна двоїстість на квадратній ґратці та доведення p_c = 1/2."""
    w, h = 800, 420
    frags = []

    frags.append(text(w / 2, 26, "Планарна двоїстість квадратної ґратки: блокуючий бар'єр та pc = 1/2", size=16, bold=True))

    # Малюємо пряму ґратку (сині вершини і ребра) та двоїсту ґратку (червоні вершини і ребра)
    gx0, gy0 = 70, 75
    step = 70
    N = 4  # 4x4 клітинок

    # Пряма ґратка (Primal Lattice L)
    # Зліва направо шукаємо протікання
    # Двоїста ґратка (Dual Lattice L*) блокує згори донизу

    # Фонова пряма сітка (тонкі лінії)
    for r in range(N + 1):
        frags.append(line(gx0, gy0 + r * step, gx0 + N * step, gy0 + r * step, color="#c8d6e5", sw=1.2))
    for c in range(N + 1):
        frags.append(line(gx0 + c * step, gy0, gx0 + c * step, gy0 + N * step, color="#c8d6e5", sw=1.2))

    # Двоїста сітка (пунктирні червоні лінії через центри граней)
    dgx0, dgy0 = gx0 + step / 2, gy0 + step / 2
    for r in range(N):
        frags.append(line(dgx0, dgy0 + r * step, dgx0 + (N - 1) * step, dgy0 + r * step, color="#ffcdd2", sw=1.2, dash="3,3"))
    for c in range(N):
        frags.append(line(dgx0 + c * step, dgy0, dgx0 + c * step, dgy0 + (N - 1) * step, color="#ffcdd2", sw=1.2, dash="3,3"))

    # Виділяємо вертикальний блокуючий бар'єр на двоїстій ґратці (закриті ребра прямої ґратки)
    # Бар'єр іде через центри: (0,1) -> (1,1) -> (2,2) -> (3,2)
    dual_barrier_edges = [
        ((0, 1), (1, 1)),
        ((1, 1), (1, 2)),
        ((1, 2), (2, 2)),
        ((2, 2), (3, 2))
    ]
    for (r1, c1), (r2, c2) in dual_barrier_edges:
        x1 = dgx0 + c1 * step
        y1 = dgy0 + r1 * step
        x2 = dgx0 + c2 * step
        y2 = dgy0 + r2 * step
        frags.append(line(x1, y1, x2, y2, color=POS, sw=3.5))

    # Вузли прямої ґратки
    for r in range(N + 1):
        for c in range(N + 1):
            frags.append(circle(gx0 + c * step, gy0 + r * step, 5, fill="#2457d6", stroke="#103a94", sw=1.5))

    # Вузли двоїстої ґратки (у центрах комірок)
    for r in range(N):
        for c in range(N):
            frags.append(circle(dgx0 + c * step, dgy0 + r * step, 6, fill="#ffebee", stroke=POS, sw=1.8))

    # Права інформаційна панель
    info_x = gx0 + N * step + 45
    info_y = gy0
    info_w = w - info_x - 30
    info_h = N * step

    frags.append(rect(info_x, info_y, info_w, info_h, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    frags.append(text(info_x + info_w / 2, info_y + 25, "Принцип Крамерса — Ванньє", size=14, bold=True))

    items = [
        "1. Пряма ґратка L (синя):",
        "   протікання зліва направо",
        "   відбувається по відкритих ребрах (p).",
        "",
        "2. Двоїста ґратка L* (червона):",
        "   кожне ребро e* перетинає e.",
        "   e* відкрите в L* ⇔ e закрите в L (1−p).",
        "",
        "3. Топологічна теорема:",
        "   Горизонтальний шлях у L існує тоді",
        "   й лише тоді, коли НЕМАЄ вертикального",
        "   блокуючого шляху в L*.",
        "",
        "4. Самодвоїстість квадратної ґратки:",
        "   L ≅ L*  ⇒  pc + pc* = 1  ⇒  pc = 1/2"
    ]
    for i, it in enumerate(items):
        bold = it.startswith("1.") or it.startswith("2.") or it.startswith("3.") or it.startswith("4.")
        col = POS if it.startswith("4.") else (NEG if it.startswith("1.") else INK)
        frags.append(text(info_x + 15, info_y + 55 + i * 18, it, size=11.5, anchor="start", bold=bold, color=col))

    # Підпис під сіткою
    frags.append(text(gx0 + (N * step) / 2, gy0 + N * step + 32, "Червона лінія: блокуючий бар'єр закритих ребер у двоїстій ґратці L*", size=12, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "dual-lattice-square.svg"), w, h, *frags)


def fig_newman_ziff_sweep():
    """Фігура 4: Конвеєр алгоритму Ньюмана–Зіффа: від перестановки до згортки."""
    w, h = 820, 400
    frags = []

    frags.append(text(w / 2, 26, "Алгоритм Ньюмана–Зіффа: швидке моделювання через DSU та згортку", size=16, bold=True))

    # 4 етапи конвеєра
    # 1: Генерація перестановки
    # 2: Покрокове додавання сайту + DSU Find/Union
    # 3: Мікроканонічний облік An
    # 4: Біноміальна згортка для всіх p

    bw = 175
    bh = 260
    y0 = 65
    gap = 20
    x0 = 30

    stages = [
        ("1. Перестановка", ["Випадковий порядок", "відкриття сайтів:", "π = (s₁, s₂, ..., sₙ)", "Рівномірний розподіл", "без повторень"], "#e3f2fd", NEG),
        ("2. Інкремент DSU", ["Додавання сайту sₙ", "Опитування сусідів", "Find(u), Find(v)", "Union-by-size: O(1)", "Стиснення шляхів"], "#f3e5f5", "#7b1fa2"),
        ("3. Мікроканоніка", ["Облік для кожного n:", "• макс. кластер Sₘₐₓ(n)", "• стан протікання R(n)", "• сума квадратів ∑sᵢ²", "Один прохід O(N)!"], "#e8f5e9", FIELD),
        ("4. Згортка по p", ["Біноміальний перехід:", "⟨A⟩(p) = ∑ Aₙ·B(N,n,p)", "Отримуємо криві", "для ВСІХ значень p", "миттєво за O(N)"], "#fff3e0", "#e65100")
    ]

    for i, (stitle, slines, fill_col, border_col) in enumerate(stages):
        bx = x0 + i * (bw + gap)
        frags.append(rect(bx, y0, bw, bh, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(bx + bw / 2, y0 + 26, stitle, size=13, bold=True, color=border_col))
        frags.append(line(bx + 12, y0 + 38, bx + bw - 12, y0 + 38, color=border_col, sw=1, dash="2,2"))

        for j, line_txt in enumerate(slines):
            is_hl = line_txt.startswith("⟨A⟩") or line_txt.startswith("•") or "O(N)" in line_txt or "O(1)" in line_txt
            frags.append(text(bx + bw / 2, y0 + 65 + j * 26, line_txt, size=11.5, bold=is_hl, color=INK))

        # Стрілка між блоками
        if i < 3:
            ax = bx + bw + 3
            frags.append(arrow(ax, y0 + bh / 2, ax + gap - 6, y0 + bh / 2, color=LINE, sw=2))

    # Нижній висновок
    b_msg, _, _ = textbox(w / 2, y0 + bh + 35, "Результат: замість M незалежних запусків Монте-Карло складності O(M · N)\nалгоритм Ньюмана–Зіффа будує повний спектр перколяції за один прохід O(N).", size=12.5, fill="#f8f9fa", stroke=FIELD, color="#1b5e20", bold=True)
    frags.append(b_msg)

    render(os.path.join(IMG_DIR, "newman-ziff-sweep.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_site_vs_bond()
    fig_phase_transition()
    fig_dual_lattice()
    fig_newman_ziff_sweep()
    print("Всі 4 фігури успішно згенеровано.")
