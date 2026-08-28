# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Конвеєр переходу від схеми до топології плати ─────────────────────────
def fig_schematic_to_pcb_pipeline():
    W, H = 880, 390
    f = []
    f.append(text(W / 2, 28, "Конвеєр перенесення схеми в топологію друкованої плати", size=16, bold=True))

    stages = [
        ("1. Схема (Capture)", ["Логічні символи (RefDes)", "Електричні вузли (Nets)", "Електричний контроль (ERC)"], "#eef2ff", NEG),
        ("2. Прив'язка корпусів", ["Символ → Футпринт", "Мапінг виводів (Pin-Pad)", "Бібліотеки 3D/IPC"], "#f5f3ff", "#7c3aed"),
        ("3. Нетліст та ECO", ["Граф з'єднань (Netlist)", "Forward Annotation", "Синхронізація UUID"], "#ecfdf5", FIELD),
        ("4. Класи ланцюгів", ["Групування сигналів", "Ширини та зазори", "Імпеданс і топологія"], "#fffbeb", "#d97706"),
        ("5. Трасування й DRC", ["Розведення доріжок", "Перевірка DRC/DFM", "Генерація Gerber / ODB++"], "#fef2f2", POS),
    ]

    bw = 152
    bh = 190
    gap = 18
    start_x = (W - (5 * bw + 4 * gap)) / 2
    y_box = 60

    for i, (title, items, fill_col, border_col) in enumerate(stages):
        bx = start_x + i * (bw + gap)
        # card box
        f.append(rect(bx, y_box, bw, bh, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        # header
        f.append(text(bx + bw / 2, y_box + 26, title, size=13, bold=True, color=border_col))
        f.append(line(bx + 10, y_box + 38, bx + bw - 10, y_box + 38, color=border_col, sw=1, dash="3,3"))
        
        # bullets
        for j, itm in enumerate(items):
            ty = y_box + 64 + j * 38
            # bullet point
            f.append(circle(bx + 18, ty - 4, 3, fill=border_col, stroke=border_col))
            # text broken into 2 lines if needed
            words = itm.split(" ")
            if len(itm) > 18:
                mid = len(words) // 2
                l1 = " ".join(words[:mid])
                l2 = " ".join(words[mid:])
                f.append(text(bx + 26, ty - 8, l1, size=11, color=INK, anchor="start"))
                f.append(text(bx + 26, ty + 6, l2, size=11, color=MUTED, anchor="start"))
            else:
                f.append(text(bx + 26, ty, itm, size=11, color=INK, anchor="start"))

        # transition arrow to next stage
        if i < 4:
            ax1 = bx + bw + 2
            ax2 = bx + bw + gap - 2
            ay = y_box + bh / 2
            f.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.8))

    # Bottom explanation panel: Engineering Feedback Loop (ECO / Back Annotation)
    py = y_box + bh + 30
    pw = W - 2 * start_x
    f.append(rect(start_x, py, pw, 80, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    f.append(text(start_x + pw / 2, py + 22, "Зворотний інженерний зв'язок (Engineering Change Order & Back Annotation)", size=12, bold=True, color=INK))
    
    # Flow indicators
    f.append(line(start_x + 80, py + 48, start_x + pw - 80, py + 48, color="#64748b", sw=1.5, dash="4,4"))
    f.append(arrow(start_x + pw - 120, py + 48, start_x + 120, py + 48, color="#dc2626", sw=1.8))
    f.append(text(start_x + pw / 2, py + 68, "Зворотне перейменування контактів, перестановка вентилів (Gate Swap) та узгодження змін без втрати геометрії", size=11, color=MUTED))

    render(os.path.join(IMG, "schematic-to-pcb-pipeline.svg"), W, H, "".join(f))


# ── 2. Матриця правил і обмежень класів ланцюгів ──────────────────────────────
def fig_net_class_rules_matrix():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 28, "Ієрархія та матриця зазорів класів ланцюгів (Net Classes)", size=16, bold=True))

    # Left: 4 primary net classes visual profiles
    col_w = 410
    x_left = 35
    y_start = 58
    card_h = 72
    card_gap = 12

    classes = [
        ("Power / GND (Силові шини)", "Ширина: 0.8–3.0 мм | Зазор: 0.25–0.4 мм | Via: 0.8/0.4 мм", "Струмове навантаження, мінімальний опір та падіння напруги", "#fee2e2", POS),
        ("High-Speed Diff (Швидкісні диференційні)", "Ширина: 0.15 мм | Зазор у парі: 0.12 мм | Довжина: ΔL < 0.1 мм", "Контрольований імпеданс (90/100 Ом), захист від фазового перекосу", "#e0e7ff", NEG),
        ("Sensitive Analog (Чутливий аналог)", "Ширина: 0.25 мм | Зазор ізоляції: 0.5–1.0 мм | Guard Ring", "Мінімізація ємнісних та індуктивних перехресних завад", "#ecfdf5", FIELD),
        ("Standard Digital (Цифрові GPIO/Control)", "Ширина: 0.20 мм | Зазор: 0.20 мм | Стандартний Via 0.6/0.3 мм", "Базові правила трасування сигналів низької частоти", "#f8fafc", INK),
    ]

    for i, (cname, params, desc, fcol, bcol) in enumerate(classes):
        cy = y_start + i * (card_h + card_gap)
        f.append(rect(x_left, cy, col_w, card_h, fill=fcol, stroke=bcol, sw=1.5, rx=6))
        f.append(text(x_left + 14, cy + 20, cname, size=12, bold=True, color=bcol, anchor="start"))
        f.append(text(x_left + 14, cy + 40, params, size=11, bold=True, color=INK, anchor="start"))
        f.append(text(x_left + 14, cy + 58, desc, size=10, color=MUTED, anchor="start"))

    # Right: Clearance Matrix Table (Міжкласова матриця зазорів)
    x_right = 470
    table_w = 375
    f.append(rect(x_right, y_start, table_w, 324, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(x_right + table_w / 2, y_start + 24, "Матриця міжосьових зазорів (Clearance Matrix)", size=13, bold=True, color=INK))

    # Grid headers
    grid_x0 = x_right + 95
    grid_y0 = y_start + 50
    cell_w = 64
    cell_h = 48

    headers = ["Power", "Hi-Speed", "Analog", "Digital"]
    for j, h_title in enumerate(headers):
        f.append(text(grid_x0 + j * cell_w + cell_w / 2, grid_y0 + 20, h_title, size=10, bold=True, color=INK))
        f.append(text(x_right + 48, grid_y0 + 36 + (j + 1) * cell_h - cell_h / 2, h_title, size=10, bold=True, color=INK))

    # Grid lines
    for r in range(5):
        f.append(line(x_right + 15, grid_y0 + 36 + r * cell_h, x_right + table_w - 15, grid_y0 + 36 + r * cell_h, color="#e2e8f0", sw=1))
    for c in range(5):
        f.append(line(grid_x0 + c * cell_w, grid_y0 + 10, grid_x0 + c * cell_w, grid_y0 + 36 + 4 * cell_h, color="#e2e8f0", sw=1))

    # Matrix data: row x col
    # Values: (Clearance in mm, highlight flag)
    matrix_data = [
        ["0.25 мм", "0.40 мм", "0.60 мм", "0.30 мм"],  # Power
        ["0.40 мм", "0.12* мм", "0.50 мм", "0.35 мм"],  # Hi-Speed
        ["0.60 мм", "0.50 мм", "0.20 мм", "0.40 мм"],  # Analog
        ["0.30 мм", "0.35 мм", "0.40 мм", "0.20 мм"],  # Digital
    ]

    for r in range(4):
        for c in range(4):
            val = matrix_data[r][c]
            cx = grid_x0 + c * cell_w + cell_w / 2
            cy = grid_y0 + 36 + r * cell_h + cell_h / 2 + 4
            is_critical = (r == 0 and c == 2) or (r == 2 and c == 0) or (r == 1 and c == 1)
            txt_col = POS if is_critical else (NEG if r == c else INK)
            f.append(text(cx, cy, val, size=11, bold=is_critical or (r == c), color=txt_col))

    f.append(text(x_right + table_w / 2, y_start + 306, "* усередині пари; між парою та іншими лініями діє правило 3W (0.45 мм)", size=9.5, italic=True, color=MUTED))

    render(os.path.join(IMG, "net-class-rules-matrix.svg"), W, H, "".join(f))


if __name__ == "__main__":
    fig_schematic_to_pcb_pipeline()
    fig_net_class_rules_matrix()
    print("Figures generated successfully.")
