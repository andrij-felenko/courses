# -*- coding: utf-8 -*-
"""Фігури для теми z-choho-zrobyty-korpus (З чого зробити корпус: друк, фрезерування, готова коробка).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра
COLOR_FDM      = "#ef4444"  # Червоний: 3D-друк (FDM/MJF)
COLOR_OFFSHELF = "#d97706"  # Бурштиновий: Готовий дороблений корпус (Gainta/Hammond)
COLOR_CNC      = "#0284c7"  # Блакитний: ЧПУ-фрезерування алюмінію (6061-T6)
COLOR_MOLD     = "#10b981"  # Зелений: Лиття під тиском (Injection Molding)
BG_CARD        = "#f8fafc"
BORDER_CARD    = "#cbd5e1"


# ── 1. Криві питомої собівартості технологій залежно від обсягу серії ──────────
def fig_volume_cost_curve():
    W, H = 860, 530
    frags = []

    # Тло
    frags.append(rect(10, 10, 840, 510, fill="#ffffff", stroke=BORDER_CARD, sw=1.0, rx=8))
    frags.append(text(430, 32, "Питома собівартість виготовлення 1 корпусу залежно від тиражу",
                      size=13, color=INK, bold=True))

    # Область графіка
    gx, gy, gw, gh = 75, 60, 515, 335
    frags.append(rect(gx, gy, gw, gh, fill=BG_CARD, stroke="#94a3b8", sw=1.0))

    # Горизонтальні лінії сітки (шкала вартості)
    grid_y_vals = [
        (gy + 20, "$1 000"),
        (gy + 115, "$100"),
        (gy + 215, "$10"),
        (gy + 315, "$1")
    ]
    for y_pos, label_val in grid_y_vals:
        frags.append(line(gx, y_pos, gx + gw, y_pos, color="#e2e8f0", sw=1.0, dash="3,3"))
        frags.append(text(gx - 8, y_pos + 4, label_val, size=10, color=MUTED, anchor="end"))

    # Вертикальні лінії сітки (шкала тиражу)
    grid_x_vals = [
        (gx + 25, "1 шт"),
        (gx + 125, "10 шт"),
        (gx + 225, "100 шт"),
        (gx + 325, "1 000 шт"),
        (gx + 425, "10k шт"),
        (gx + 495, "50k шт")
    ]
    for x_pos, label_val in grid_x_vals:
        frags.append(line(x_pos, gy, x_pos, gy + gh, color="#e2e8f0", sw=1.0, dash="3,3"))
        frags.append(text(x_pos, gy + gh + 15, label_val, size=9.5, color=MUTED))

    frags.append(text(gx + gw/2, gy + gh + 33, "Обсяг серії (тираж приладів у партії, логарифмічна шкала)", size=10, color=INK, bold=True))

    # Зони технологічного домінування (підкладки)
    # Зона 1: 3D-друк (1..15 шт)
    frags.append(rect(gx + 2, gy + 2, 140, gh - 4, fill="#fef2f2", stroke="none"))
    frags.append(text(gx + 72, gy + gh - 15, "Зона 3D-друку", size=10, color=COLOR_FDM, bold=True))

    # Зона 2: Готові / ЧПУ (15..500 шт)
    frags.append(rect(gx + 144, gy + 2, 140, gh - 4, fill="#f0f9ff", stroke="none"))
    frags.append(text(gx + 214, gy + gh - 15, "Зона ЧПУ / Доробки", size=10, color=COLOR_CNC, bold=True))

    # Зона 3: Лиття під тиском (>1000 шт)
    frags.append(rect(gx + 320, gy + 2, 193, gh - 4, fill="#ecfdf5", stroke="none"))
    frags.append(text(gx + 416, gy + gh - 15, "Зона Injection Molding", size=10, color=COLOR_MOLD, bold=True))

    # 1. Крива 3D-друку FDM/MJF
    pts_3d = [(gx + 25, gy + 175), (gx + 125, gy + 188), (gx + 225, gy + 198), (gx + 325, gy + 205), (gx + 425, gy + 210), (gx + 495, gy + 212)]
    for i in range(len(pts_3d) - 1):
        frags.append(line(pts_3d[i][0], pts_3d[i][1], pts_3d[i+1][0], pts_3d[i+1][1], color=COLOR_FDM, sw=2.5))
    for pt in pts_3d:
        frags.append(circle(pt[0], pt[1], 3.5, fill=COLOR_FDM, stroke="#ffffff", sw=1.2))

    # 2. Крива доробки готових корпусів Gainta/Hammond
    pts_offshelf = [(gx + 25, gy + 160), (gx + 125, gy + 192), (gx + 225, gy + 208), (gx + 325, gy + 215), (gx + 425, gy + 218)]
    for i in range(len(pts_offshelf) - 1):
        frags.append(line(pts_offshelf[i][0], pts_offshelf[i][1], pts_offshelf[i+1][0], pts_offshelf[i+1][1], color=COLOR_OFFSHELF, sw=2.5))
    for pt in pts_offshelf:
        frags.append(circle(pt[0], pt[1], 3.5, fill=COLOR_OFFSHELF, stroke="#ffffff", sw=1.2))

    # 3. Крива ЧПУ фрезерування Al 6061-T6
    pts_cnc = [(gx + 25, gy + 100), (gx + 125, gy + 148), (gx + 225, gy + 170), (gx + 325, gy + 178), (gx + 425, gy + 184)]
    for i in range(len(pts_cnc) - 1):
        frags.append(line(pts_cnc[i][0], pts_cnc[i][1], pts_cnc[i+1][0], pts_cnc[i+1][1], color=COLOR_CNC, sw=2.5))
    for pt in pts_cnc:
        frags.append(circle(pt[0], pt[1], 3.5, fill=COLOR_CNC, stroke="#ffffff", sw=1.2))

    # 4. Крива лиття під тиском Injection Molding
    pts_mold = [(gx + 25, gy + 10), (gx + 125, gy + 60), (gx + 225, gy + 115), (gx + 325, gy + 215), (gx + 425, gy + 290), (gx + 495, gy + 312)]
    for i in range(len(pts_mold) - 1):
        frags.append(line(pts_mold[i][0], pts_mold[i][1], pts_mold[i+1][0], pts_mold[i+1][1], color=COLOR_MOLD, sw=2.5))
    for pt in pts_mold:
        frags.append(circle(pt[0], pt[1], 3.5, fill=COLOR_MOLD, stroke="#ffffff", sw=1.2))

    # Права панель: Легенда та розшифровка
    lx, ly = 605, 60
    frags.append(rect(lx, ly, 235, 365, fill="#ffffff", stroke=BORDER_CARD, sw=1.2, rx=6))
    frags.append(text(lx + 117, ly + 22, "Технологічні профілі", size=11, color=INK, bold=True))

    tech_items = [
        ("3D-друк (FDM/MJF)", "NRE = 0. Оптимально для 1..20 шт.\nШвидке внесення змін у CAD.\nВисока питома вартість одиниці.", COLOR_FDM, "#fef2f2"),
        ("Готовий дороблений", "Литий ABS/Alu (Gainta/Hammond).\nОптимально для 10..250 шт.\nФрезерування отворів під порти.", COLOR_OFFSHELF, "#fffbeb"),
        ("ЧПУ фрезерування Al", "Сплав 6061-T6, анодування.\nОптимально для 10..500 шт.\nВідмінне тепловідведення та ЕМС.", COLOR_CNC, "#f0f9ff"),
        ("Лиття під тиском (IM)", "Сталева прес-форма ($8k–$30k).\nОптимально від 1 500+ шт.\nСобівартість виливка $1.5–$3.", COLOR_MOLD, "#ecfdf5")
    ]

    cur_y = ly + 36
    for title_it, desc_it, border_c, bg_c in tech_items:
        frags.append(rect(lx + 8, cur_y, 219, 73, fill=bg_c, stroke=border_c, sw=1.0, rx=4))
        frags.append(text(lx + 14, cur_y + 16, title_it, size=10, color=border_c, bold=True, anchor="start"))
        lines = desc_it.split("\n")
        frags.append(mtext(lx + 14, cur_y + 32, lines, size=9, color="#334155", anchor="start", lh=1.3))
        cur_y += 79

    # Висновок внизу
    b_bot, _, _ = textbox(430, 485,
                          ["Точка беззбитковості лиття під тиском настає при тиражі понад 1 500 корпусів.",
                           "Для серій до 300 шт доробка стандартних корпусів або ЧПУ-фрезерування дають найменший TCO."],
                          size=10, fill="#f0fdf4", stroke=FIELD, pad=6)
    frags.append(b_bot)

    render(os.path.join(OUT, "enclosure-technology-volume-cost-curve.svg"), W, H, *frags,
           title="Питома собівартість виготовлення 1 корпусу залежно від тиражу")


# ── 2. Геометрія паза та розрахунок стиснення ущільнювача IP67 ────────────────
def fig_gasket_groove_geometry():
    W, H = 860, 530
    frags = []

    frags.append(rect(10, 10, 840, 510, fill="#ffffff", stroke=BORDER_CARD, sw=1.0, rx=8))
    frags.append(text(430, 32, "Геометрія посадкового паза (Gland) та ступінь стиснення ущільнювача IP67/IP68",
                      size=13, color=INK, bold=True))

    # ── Ліва колонка: Вільний стан до стиснення ──
    x0, y0 = 35, 60
    w_col = 375
    frags.append(rect(x0, y0, w_col, 390, fill=BG_CARD, stroke=BORDER_CARD, sw=1.2, rx=6))
    frags.append(text(x0 + w_col/2, y0 + 24, "1. Вільний стан до затягування (d_cord > h_groove)", size=11, color=INK, bold=True))

    # Кришка корпусу (зверху)
    cy0 = y0 + 45
    frags.append(rect(x0 + 40, cy0, 295, 40, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(x0 + w_col/2, cy0 + 24, "Кришка корпусу (Top Cover)", size=10, color=INK, bold=True))

    # Стрілки зближення
    frags.append(arrow(x0 + 90, cy0 + 45, x0 + 90, cy0 + 68, color=COLOR_FDM, sw=1.8))
    frags.append(arrow(x0 + 285, cy0 + 45, x0 + 285, cy0 + 68, color=COLOR_FDM, sw=1.8))
    frags.append(text(x0 + w_col/2, cy0 + 58, "Зусилля притискання F_clamp", size=9.5, color=COLOR_FDM, bold=True))

    # Основа корпусу з пазом (Base Enclosure)
    by0 = cy0 + 75
    # Лівий фланець
    frags.append(rect(x0 + 40, by0, 85, 110, fill="#cbd5e1", stroke="#475569", sw=1.5))
    # Правий фланець
    frags.append(rect(x0 + 250, by0, 85, 110, fill="#cbd5e1", stroke="#475569", sw=1.5))
    # Дно паза
    frags.append(rect(x0 + 125, by0 + 65, 125, 45, fill="#cbd5e1", stroke="#475569", sw=1.5))

    # Тіло ущільнювача (O-Ring кругле в перерізі, вільний діаметр d = 2.5 мм)
    ring_cx, ring_cy = x0 + 187, by0 + 35
    frags.append(circle(ring_cx, ring_cy, 35, fill="#fed7aa", stroke="#ea580c", sw=2.0))
    frags.append(text(ring_cx, ring_cy + 4, "d_cord = 2.5 мм", size=10, color="#9a3412", bold=True))

    # Розмірні лінії паза
    # Ширина паза w_groove = 3.2 мм
    frags.append(line(x0 + 125, by0 + 120, x0 + 250, by0 + 120, color="#2563eb", sw=1.2))
    frags.append(line(x0 + 125, by0 + 115, x0 + 125, by0 + 125, color="#2563eb", sw=1.2))
    frags.append(line(x0 + 250, by0 + 115, x0 + 250, by0 + 125, color="#2563eb", sw=1.2))
    frags.append(text(x0 + 187, by0 + 134, "w_groove = 3.2 мм (1.28 × d)", size=10, color="#1d4ed8", bold=True))

    # Глибина паза h_groove = 1.85 мм
    frags.append(line(x0 + 258, by0, x0 + 258, by0 + 65, color="#2563eb", sw=1.2))
    frags.append(line(x0 + 253, by0, x0 + 263, by0, color="#2563eb", sw=1.2))
    frags.append(line(x0 + 253, by0 + 65, x0 + 263, by0 + 65, color="#2563eb", sw=1.2))
    frags.append(text(x0 + 302, by0 + 36, "h = 1.85 мм", size=10, color="#1d4ed8", bold=True))

    # Опис знизу колонки 1
    frags.append(mtext(x0 + w_col/2, y0 + 325,
                       ["Круглий шнур O-Ring або силіконова прокладка.",
                        "Вільний діаметр перерізу перевищує глибину паза на 25–30%.",
                        "Ширина паза розраховується з запасом на розширення гуми."],
                       size=9.5, color="#334155", lh=1.35))

    # ── Права колонка: Стиснений стан зі змиканням фланців ──
    x1 = 445
    frags.append(rect(x1, y0, w_col, 390, fill=BG_CARD, stroke=BORDER_CARD, sw=1.2, rx=6))
    frags.append(text(x1 + w_col/2, y0 + 24, "2. Стиснений робочий стан (IP67 герметизація)", size=11, color=POS, bold=True))

    # Кришка зімкнута з фланцями
    cy1 = y0 + 45
    frags.append(rect(x1 + 40, cy1 + 30, 295, 40, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(x1 + w_col/2, cy1 + 54, "Кришка зімкнута метал-до-металу", size=10, color=INK, bold=True))

    # Основа корпусу
    by1 = cy1 + 70
    frags.append(rect(x1 + 40, by1, 85, 110, fill="#cbd5e1", stroke="#475569", sw=1.5))
    frags.append(rect(x1 + 250, by1, 85, 110, fill="#cbd5e1", stroke="#475569", sw=1.5))
    frags.append(rect(x1 + 125, by1 + 65, 125, 45, fill="#cbd5e1", stroke="#475569", sw=1.5))

    # Деформований шнур (прямокутник із закругленими краями)
    frags.append(rect(x1 + 140, by1 + 10, 95, 55, fill="#fed7aa", stroke="#ea580c", sw=2.0, rx=20))
    frags.append(text(x1 + 187, by1 + 32, "Стиснення: 26%", size=10, color="#9a3412", bold=True))
    frags.append(text(x1 + 187, by1 + 48, "Заповнення: 78%", size=9.5, color="#9a3412"))

    # Бічні зазори розширення
    frags.append(arrow(x1 + 130, by1 + 20, x1 + 138, by1 + 35, color=COLOR_CNC, sw=1.2))
    frags.append(arrow(x1 + 245, by1 + 20, x1 + 237, by1 + 35, color=COLOR_CNC, sw=1.2))
    frags.append(text(x1 + w_col/2, by1 + 88, "Зазор для термічного розширення еластомеру", size=9, color=COLOR_CNC, bold=True))

    # Опис знизу колонки 2
    frags.append(mtext(x1 + w_col/2, y0 + 325,
                       ["Стиснення еластомеру 20–30% створює надійний бар'єр.",
                        "Коефіцієнт заповнення паза (Groove Fill) не перевищує 85%,",
                        "тому нестислива гума не блокує стик і не деформує корпус."],
                       size=9.5, color="#334155", lh=1.35))

    # Загальний підсумок знизу
    b_bot, _, _ = textbox(430, 485,
                          ["Правило розрахунку паза: Площа перерізу паза повинна бути на 15–25% більшою за площу перерізу ущільнювача.",
                           "Для корпусів з 3D-друку мінімальна товщина стінки навколо паза становить 2.0 мм через ризик мікропористості."],
                          size=10, fill="#f0fdf4", stroke=FIELD, pad=6)
    frags.append(b_bot)

    render(os.path.join(OUT, "ip67-gasket-groove-geometry.svg"), W, H, *frags,
           title="Геометрія посадкового паза та ступінь стиснення ущільнювача IP67/IP68")


def main():
    fig_volume_cost_curve()
    fig_gasket_groove_geometry()
    print("Всі фігури для z-choho-zrobyty-korpus згенеровано успішно.")


if __name__ == "__main__":
    main()
