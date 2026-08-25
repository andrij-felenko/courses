# -*- coding: utf-8 -*-
"""Фігури до теми «Колірне субдискретування (chroma subsampling)».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Порівняння контрастно-частотної характеристики (CSF) ока ────────────
def fig_eye_acuity():
    W, H = 760, 270
    f = [text(W / 2, 22, "Просторова чутливість ока: яскравість проти кольору", size=15, bold=True)]

    x0, y0 = 80, 225
    xw, yh = 630, 155

    # Зона колірного субдискретизування (нижня частина графіка)
    f.append(f'<rect x="{x0 + 220}" y="{y0 - yh + 55}" width="380" height="{yh - 55}" fill="#fef3c7" fill-opacity="0.35" rx="4"/>')

    # осі
    f.append(line(x0, y0, x0 + xw + 10, y0, color=INK, sw=1.5))
    f.append(line(x0, y0, x0, y0 - yh - 10, color=INK, sw=1.5))

    f.append(text(x0 + xw, y0 + 22, "Просторова частота (цикли / град. кута)", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 15, y0 - yh - 5, "Контрастна чутливість", size=11, color=MUTED, anchor="start"))

    # Сітка та засічки
    for i in range(1, 6):
        cx = x0 + i * (xw / 5.5)
        f.append(line(cx, y0, cx, y0 - yh, color="#e5e7eb", sw=1, dash="3,3"))

    # Крива яркості Y (висока роздільність)
    pts_y = [(x0, y0 - 15), (x0 + 80, y0 - 75), (x0 + 180, y0 - 145), (x0 + 320, y0 - 95), (x0 + 480, y0 - 35), (x0 + 600, y0 - 5)]
    poly_y = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_y)
    f.append(f'<path d="M {poly_y}" fill="none" stroke="#2563eb" stroke-width="3"/>')

    # Крива кольору Cb/Cr
    pts_c = [(x0, y0 - 70), (x0 + 80, y0 - 65), (x0 + 160, y0 - 45), (x0 + 260, y0 - 20), (x0 + 380, y0 - 6), (x0 + 480, y0 - 2)]
    poly_c = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_c)
    f.append(f'<path d="M {poly_c}" fill="none" stroke="#dc2626" stroke-width="3" stroke-dasharray="6,4"/>')

    # Пояснювальні плашки зверху у чистій зоні над графіком
    f.append(rect(430, 15, 290, 52, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(line(445, 30, 475, 30, color="#2563eb", sw=3))
    f.append(text(485, 34, "Яскравість Y (Палички & Колбочки)", size=11, color=INK, bold=True, anchor="start"))
    f.append(line(445, 50, 475, 50, color="#dc2626", sw=3, dash="6,4"))
    f.append(text(485, 54, "Колір Cb/Cr (Колбочки)", size=11, color=INK, bold=True, anchor="start"))

    # Напис зони під графіком у бежевій зоні
    f.append(text(490, 205, "Зона субдискретизування кольору", size=11, color="#b45309", bold=True))

    render(os.path.join(IMG, 'eye-acuity.svg'), W, H, *f)


# ── 2. Сітки субдискретизації 4:4:4, 4:2:2, 4:2:0, 4:1:1 ───────────────────
def fig_subsampling_grids():
    W, H = 820, 360
    f = [text(W / 2, 25, "Геометрія відліків у блоці 4×2 пікселів", size=15, bold=True)]

    configs = [
        ("4:4:4", "100% даних (24 біт/пікс)", [
            [(1,1), (1,1), (1,1), (1,1)],
            [(1,1), (1,1), (1,1), (1,1)]
        ], 30, 50),
        ("4:2:2", "66.7% даних (16 біт/пікс)", [
            [(1,1), (0,0), (1,1), (0,0)],
            [(1,1), (0,0), (1,1), (0,0)]
        ], 430, 50),
        ("4:2:0", "50% даних (12 біт/пікс)", [
            [(0.5,0.5), (0,0), (0.5,0.5), (0,0)],
            [(0,0), (0,0), (0,0), (0,0)]
        ], 30, 200),
        ("4:1:1", "50% даних (12 біт/пікс)", [
            [(1,1), (0,0), (0,0), (0,0)],
            [(1,1), (0,0), (0,0), (0,0)]
        ], 430, 200)
    ]

    for title, sub, grid, ox, oy in configs:
        f.append(rect(ox, oy, 360, 135, fill="#fafafa", stroke=FIELD, sw=1.2, rx=6))
        f.append(text(ox + 15, oy + 22, title, size=14, bold=True, color=INK, anchor="start"))
        f.append(text(ox + 75, oy + 22, f"({sub})", size=11, color=MUTED, anchor="start"))

        # Малюємо 4x2 сітку пікселів
        gx0, gy0 = ox + 20, oy + 35
        cell_w, cell_h = 42, 40

        for r in range(2):
            for c in range(4):
                px = gx0 + c * cell_w
                py = gy0 + r * cell_h
                # Піксельна комірка Y
                f.append(rect(px, py, cell_w, cell_h, fill="#ffffff", stroke="#cbd5e1", sw=1))
                # Відлік Y (яскравість - точка в центрі)
                f.append(circle(px + cell_w/2, py + cell_h/2, 4, fill="#64748b"))

                # Хрома-відліки
                has_cb_cr = grid[r][c]
                if has_cb_cr[0] == 1:
                    # 1:1 в пікселі
                    f.append(circle(px + cell_w/2 - 6, py + cell_h/2, 5, fill="#2563eb")) # Cb
                    f.append(circle(px + cell_w/2 + 6, py + cell_h/2, 5, fill="#dc2626")) # Cr

        # Окремо для 4:2:0 намалюємо спільні хрома-точки між 2x2
        if title == "4:2:0":
            # Точка 1 для лівих 2x2
            cx1 = gx0 + cell_w
            cy1 = gy0 + cell_h
            f.append(circle(cx1 - 6, cy1, 6, fill="#2563eb", stroke="#ffffff", sw=1.5))
            f.append(circle(cx1 + 6, cy1, 6, fill="#dc2626", stroke="#ffffff", sw=1.5))
            # Точка 2 для правих 2x2
            cx2 = gx0 + 3 * cell_w
            cy2 = gy0 + cell_h
            f.append(circle(cx2 - 6, cy2, 6, fill="#2563eb", stroke="#ffffff", sw=1.5))
            f.append(circle(cx2 + 6, cy2, 6, fill="#dc2626", stroke="#ffffff", sw=1.5))

        # Легенда міні
        lx = ox + 200
        ly = oy + 55
        f.append(circle(lx, ly, 4, fill="#64748b"))
        f.append(text(lx + 10, ly + 4, "Y (яскравість)", size=10, color=INK, anchor="start"))
        f.append(circle(lx, ly + 22, 5, fill="#2563eb"))
        f.append(text(lx + 10, ly + 26, "Cb (синій різничний)", size=10, color=INK, anchor="start"))
        f.append(circle(lx, ly + 44, 5, fill="#dc2626"))
        f.append(text(lx + 10, ly + 48, "Cr (червоний різничний)", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, 'subsampling-grids.svg'), W, H, *f)


# ── 3. Колірний аліасинг проти КІХ-фільтрації ──────────────────────────────
def fig_chroma_aliasing():
    W, H = 780, 240
    f = [text(W / 2, 25, "Наївне проріджування колірної межі проти КІХ-фільтрації", size=15, bold=True)]

    # Ліворуч: наївний вибірковий метод (без ФНЧ -> аліасинг, колірний зубчастий край)
    f.append(rect(40, 50, 330, 165, fill="#fff5f5", stroke="#fca5a5", sw=1.2, rx=6))
    f.append(text(205, 72, "Наївно: кожен 2-й відлік (без ФНЧ)", size=13, bold=True, color="#991b1b"))

    # Градієнт/перехід без фільтра
    f.append(text(60, 100, "Вхідний різкий колірний перехід:", size=11, color=INK, anchor="start"))
    colors_in = ["#ef4444", "#ef4444", "#3b82f6", "#3b82f6"]
    for i, col in enumerate(colors_in):
        f.append(rect(60 + i*40, 110, 38, 25, fill=col, stroke="#cbd5e1"))

    f.append(text(60, 160, "Вихід після проріджування та відновлення:", size=11, color=INK, anchor="start"))
    colors_bad = ["#ef4444", "#ef4444", "#3b82f6", "#3b82f6"]
    for i, col in enumerate(colors_bad):
        f.append(rect(60 + i*40, 170, 38, 25, fill=col, stroke="#cbd5e1"))

    f.append(text(235, 186, "❌ Колірний аліасинг", size=11, color="#991b1b", bold=True, anchor="start"))

    # Праворуч: з ФНЧ [1 2 1]/4
    f.append(rect(410, 50, 330, 165, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    f.append(text(575, 72, "Правильно: ФНЧ [1 2 1]/4 + проріджування", size=13, bold=True, color="#166534"))

    f.append(text(430, 100, "Вхідний різкий колірний перехід:", size=11, color=INK, anchor="start"))
    for i, col in enumerate(colors_in):
        f.append(rect(430 + i*40, 110, 38, 25, fill=col, stroke="#cbd5e1"))

    f.append(text(430, 160, "Вихід із плавною антиаліасинговою фазою:", size=11, color=INK, anchor="start"))
    colors_good = ["#ef4444", "#b9559b", "#6366f1", "#3b82f6"]
    for i, col in enumerate(colors_good):
        f.append(rect(430 + i*40, 170, 38, 25, fill=col, stroke="#cbd5e1"))

    f.append(text(605, 186, "✓ М'який градієнт", size=11, color="#166534", bold=True, anchor="start"))

    render(os.path.join(IMG, 'chroma-aliasing.svg'), W, H, *f)


# ── 4. Порівняння пропускної здатності для 4K60 HDR ─────────────────────────
def fig_bandwidth_saving():
    W, H = 760, 240
    f = [text(W / 2, 25, "Необхідна пропускна здатність відеопотоку 4K60 (10-біт HDR)", size=15, bold=True)]

    x0, y0 = 180, 200
    bar_h = 32

    items = [
        ("4:4:4 (без субдискретування)", 17.9, "#ef4444", "17.9 Гбіт/с (Потрібен HDMI 2.1)"),
        ("4:2:2 (студійне субдискр.)", 11.9, "#f59e0b", "11.9 Гбіт/с (Вміщається в HDMI 2.0)"),
        ("4:2:0 (споживче субдискр.)", 8.95, "#10b981", "8.95 Гбіт/с (Оптимум для вебу та ТБ)")
    ]

    max_val = 20.0
    max_w = 480

    for i, (label, val, color, note) in enumerate(items):
        by = y0 - (2 - i) * 52 - bar_h
        bw = (val / max_val) * max_w

        f.append(text(x0 - 15, by + bar_h/2 + 4, label, size=11, color=INK, bold=True, anchor="end"))
        f.append(rect(x0, by, bw, bar_h, fill=color, rx=4))
        f.append(text(x0 + bw + 10, by + bar_h/2 + 4, note, size=11, color=INK, anchor="start"))

    # Межа HDMI 2.0 (18 Гбіт/с)
    h20_x = x0 + (18.0 / max_val) * max_w
    f.append(line(h20_x, 45, h20_x, y0 + 10, color="#94a3b8", sw=2, dash="4,4"))
    f.append(text(h20_x, y0 + 22, "Межа HDMI 2.0 (18 Гбіт/с)", size=10, color="#64748b", anchor="middle", bold=True))

    render(os.path.join(IMG, 'bandwidth-saving.svg'), W, H, *f)


if __name__ == '__main__':
    fig_eye_acuity()
    fig_subsampling_grids()
    fig_chroma_aliasing()
    fig_bandwidth_saving()
    print("Всі SVG фігури успішно згенеровано.")
