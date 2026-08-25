# -*- coding: utf-8 -*-
"""
Фігури до статті «Порівняння двох послідовностей: найдовша спільна підпослідовність і алгоритми diff».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_edit_graph_myers():
    W, H = 860, 540
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Граф редагування Маєрса (Edit Graph) та діагональний пошук", size=15, bold=True))

    ox, oy = 80, 80
    cw, ch = 52, 50

    # Sequence A (horizontal, deletions) = A B C A B B A (N = 7)
    # Sequence B (vertical, insertions)   = C B A B A C   (M = 6)
    seqA = ["A", "B", "C", "A", "B", "B", "A"]
    seqB = ["C", "B", "A", "B", "A", "C"]
    N, M = len(seqA), len(seqB)

    # Column labels (A elements)
    for i, ch_a in enumerate(seqA):
        x = ox + i * cw + cw / 2
        parts.append(text(x, oy - 22, "A[%d]" % (i + 1), size=10, color=MUTED))
        parts.append(text(x, oy - 8, ch_a, size=14, bold=True, color=POS))

    # Row labels (B elements)
    for j, ch_b in enumerate(seqB):
        y = oy + j * ch + ch / 2
        parts.append(text(ox - 38, y + 4, "B[%d]" % (j + 1), size=10, color=MUTED))
        parts.append(text(ox - 16, y + 4, ch_b, size=14, bold=True, color=NEG))

    # Draw grid lines (horizontal & vertical)
    for i in range(N + 1):
        x = ox + i * cw
        parts.append(line(x, oy, x, oy + M * ch, color="#e2e8f0", sw=1.2))
        parts.append(text(x, oy + M * ch + 16, str(i), size=10, color=MUTED))

    for j in range(M + 1):
        y = oy + j * ch
        parts.append(line(ox, y, ox + N * cw, y, color="#e2e8f0", sw=1.2))
        parts.append(text(ox - 14, y + 4, str(j), size=10, color=MUTED))

    # Draw diagonal lines k = x - y (dashed background)
    # k ranges from -M to N
    for k in range(-M, N + 1):
        pts = []
        for x_val in range(N + 1):
            y_val = x_val - k
            if 0 <= y_val <= M:
                pts.append((ox + x_val * cw, oy + y_val * ch))
        if len(pts) >= 2:
            p_start, p_end = pts[0], pts[-1]
            parts.append(line(p_start[0], p_start[1], p_end[0], p_end[1], color="#cbd5e1", sw=1, dash="3,3"))

    # Diagonal match edges (snakes)
    matches = []
    for i in range(N):
        for j in range(M):
            if seqA[i] == seqB[j]:
                matches.append((i, j))
                x1, y1 = ox + i * cw, oy + j * ch
                x2, y2 = ox + (i + 1) * cw, oy + (j + 1) * ch
                parts.append(line(x1, y1, x2, y2, color="#86efac", sw=2.5))

    path_nodes = [
        (0, 0),
        (1, 0),  # del A
        (1, 1),  # ins C
        (2, 2),  # snake B
        (3, 2),  # del C
        (4, 3),  # snake A
        (5, 4),  # snake B
        (6, 4),  # del B
        (7, 5),  # snake A
        (7, 6),  # ins C
    ]

    for idx in range(len(path_nodes) - 1):
        n1 = path_nodes[idx]
        n2 = path_nodes[idx + 1]
        x1, y1 = ox + n1[0] * cw, oy + n1[1] * ch
        x2, y2 = ox + n2[0] * cw, oy + n2[1] * ch

        is_snake = (n2[0] - n1[0] == 1 and n2[1] - n1[1] == 1)
        if is_snake:
            parts.append(arrow(x1, y1, x2, y2, color=FIELD, sw=3.5))
        elif n2[0] > n1[0]:  # Del (Horizontal)
            parts.append(arrow(x1, y1, x2, y2, color=POS, sw=2.5))
        else:  # Ins (Vertical)
            parts.append(arrow(x1, y1, x2, y2, color=NEG, sw=2.5))

    # Grid intersection points
    for i in range(N + 1):
        for j in range(M + 1):
            x = ox + i * cw
            y = oy + j * ch
            parts.append(circle(x, y, 3, fill="#64748b", stroke="none"))

    # Highlight start & end points
    parts.append(circle(ox, oy, 6, fill="#ffffff", stroke=FIELD, sw=2.5))
    parts.append(circle(ox + N * cw, oy + M * ch, 6, fill=FIELD, stroke="#ffffff", sw=1.5))

    # Right info panel
    rx, ry, rw, rh = 500, 75, 335, 425
    parts.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(rx + rw / 2, ry + 26, "Геометрія простору станів", size=13, bold=True, color=INK))

    # Legend items
    leg_y = ry + 60
    # Horizontal
    parts.append(arrow(rx + 20, leg_y, rx + 65, leg_y, color=POS, sw=2.5))
    parts.append(text(rx + 78, leg_y + 4, "Горизонтальний крок (x + 1):", size=11, bold=True, anchor="start", color=POS))
    parts.append(text(rx + 78, leg_y + 19, "Видалення з A (вартість +1 правка)", size=10, anchor="start", color=MUTED))

    leg_y += 48
    # Vertical
    parts.append(arrow(rx + 42, leg_y - 12, rx + 42, leg_y + 16, color=NEG, sw=2.5))
    parts.append(text(rx + 78, leg_y + 4, "Вертикальний крок (y + 1):", size=11, bold=True, anchor="start", color=NEG))
    parts.append(text(rx + 78, leg_y + 19, "Вставка з B (вартість +1 правка)", size=10, anchor="start", color=MUTED))

    leg_y += 48
    # Diagonal
    parts.append(arrow(rx + 20, leg_y - 10, rx + 62, leg_y + 12, color=FIELD, sw=3.2))
    parts.append(text(rx + 78, leg_y + 4, "Діагональний крок — Змія (Snake):", size=11, bold=True, anchor="start", color=FIELD))
    parts.append(text(rx + 78, leg_y + 19, "Збіг символів A[x]==B[y] (вартість 0)", size=10, anchor="start", color=MUTED))

    leg_y += 50
    # Diagonal invariant box
    parts.append(rect(rx + 15, leg_y, rw - 30, 150, fill="#f0fdf4", stroke="#86efac", sw=1, rx=4))
    parts.append(text(rx + rw / 2, leg_y + 22, "Діагональний інваріант k = x − y", size=11, bold=True, color="#166534"))
    
    desc_lines = [
        "• Крок D пересуває координати на нові k.",
        "• Зсув k-1 → k: рух вправо (видалення).",
        "• Зсув k+1 → k: рух вниз (вставка).",
        "• Парність k завжди збігається з парністю D.",
        "• Складність: O((N + M) · D) замість O(N · M)."
    ]
    for idx, l in enumerate(desc_lines):
        parts.append(text(rx + 25, leg_y + 46 + idx * 21, l, size=10, anchor="start", color="#1e293b"))

    render(os.path.join(IMG, "edit-graph-myers.svg"), W, H, *parts)


def fig_hirschberg_split():
    W, H = 860, 520
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Алгоритм Гіршберґа: розділяй і володарюй у матриці DP", size=15, bold=True))

    ox, oy = 70, 75
    mw, mh = 380, 380

    # Main DP rectangle (0,0) to (N,M)
    parts.append(rect(ox, oy, mw, mh, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    
    # Mid-line horizontal (i = N/2)
    mid_y = oy + mh / 2
    parts.append(line(ox, mid_y, ox + mw, mid_y, color="#dc2626", sw=2, dash="4,4"))

    # Labels for sequence A (Y axis) and B (X axis)
    parts.append(text(ox - 32, oy + mh / 4, "A[1 .. N/2]", size=11, bold=True, color="#1e293b"))
    parts.append(text(ox - 32, oy + 3 * mh / 4, "A[N/2+1 .. N]", size=11, bold=True, color="#1e293b"))
    parts.append(text(ox - 20, mid_y + 4, "i = N/2", size=11, bold=True, color="#dc2626"))

    parts.append(text(ox + mw / 4, oy - 14, "B[1 .. j*]", size=11, bold=True, color="#1e293b"))
    parts.append(text(ox + 3 * mw / 4, oy - 14, "B[j*+1 .. M]", size=11, bold=True, color="#1e293b"))

    # Split point j*
    split_x = ox + int(mw * 0.48)
    parts.append(line(split_x, oy, split_x, oy + mh, color="#2563eb", sw=1.5, dash="3,3"))
    parts.append(text(split_x, oy - 28, "Оптимальний розріз j*", size=10, bold=True, color="#2563eb"))

    # Sub-problem 1: Top-Left (0..N/2, 0..j*)
    parts.append(rect(ox, oy, split_x - ox, mid_y - oy, fill="#dbeafe", stroke="#3b82f6", sw=1.5))
    parts.append(text(ox + (split_x - ox) / 2, oy + (mid_y - oy) / 2 - 8, "Підзадача 1 (Top-Left)", size=11, bold=True, color="#1e40af"))
    parts.append(text(ox + (split_x - ox) / 2, oy + (mid_y - oy) / 2 + 10, "Рекурсивний виклик", size=10, color="#3b82f6"))

    # Sub-problem 2: Bottom-Right (N/2..N, j*..M)
    parts.append(rect(split_x, mid_y, ox + mw - split_x, oy + mh - mid_y, fill="#dcfce7", stroke="#22c55e", sw=1.5))
    parts.append(text(split_x + (ox + mw - split_x) / 2, mid_y + (oy + mh - mid_y) / 2 - 8, "Підзадача 2 (Bottom-Right)", size=11, bold=True, color="#166534"))
    parts.append(text(split_x + (ox + mw - split_x) / 2, mid_y + (oy + mh - mid_y) / 2 + 10, "Рекурсивний виклик", size=10, color="#16a34a"))

    # Forward DP arrow (from top-left to mid-line)
    parts.append(arrow(ox + 30, oy + 25, split_x - 15, mid_y - 10, color="#2563eb", sw=2))
    parts.append(text(ox + 90, oy + 80, "Прямий DP вектор", size=10, bold=True, color="#2563eb"))
    parts.append(text(ox + 90, oy + 95, "Lfwd[N/2, j]", size=9, color="#1d4ed8"))

    # Backward DP arrow (from bottom-right to mid-line)
    parts.append(arrow(ox + mw - 30, oy + mh - 25, split_x + 15, mid_y + 10, color="#16a34a", sw=2))
    parts.append(text(ox + mw - 90, oy + mh - 80, "Зворотний DP вектор", size=10, bold=True, color="#16a34a"))
    parts.append(text(ox + mw - 90, oy + mh - 65, "Lbwd[N/2, j]", size=9, color="#15803d"))

    # Optimal midpoint circle
    parts.append(circle(split_x, mid_y, 7, fill="#dc2626", stroke="#ffffff", sw=2))
    parts.append(text(split_x + 8, mid_y - 12, "(N/2, j*)", size=10, bold=True, color="#dc2626", anchor="start"))

    # Start & End markers
    parts.append(circle(ox, oy, 5, fill="#1e293b", stroke="none"))
    parts.append(text(ox + 12, oy + 16, "(0, 0)", size=9, color=MUTED, anchor="start"))
    parts.append(circle(ox + mw, oy + mh, 5, fill="#1e293b", stroke="none"))
    parts.append(text(ox + mw - 12, oy + mh - 8, "(N, M)", size=9, color=MUTED, anchor="end"))

    # Right side explanation panel
    rx, ry, rw, rh = 490, 75, 345, 410
    parts.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=6))
    parts.append(text(rx + rw / 2, ry + 24, "Чому пам'ять стає лінійною O(N + M)", size=12, bold=True, color=INK))

    steps = [
        ("1. Поділ рядків навпіл:", "Фіксуємо середину першої послідовності i = N / 2."),
        ("2. Прямий прохід DP (Score Lfwd):", "Обчислюємо DP від (0,0) до рядка N/2 за 2 векторні рядки (O(M) пам'яті)."),
        ("3. Зворотний прохід (Score Lbwd):", "Обчислюємо DP від (N,M) назад до рядка N/2 також за 2 рядки пам'яті."),
        ("4. Пошук точки перетину j*:", "Знаходимо індекс j, де Lfwd[j] + Lbwd[j] є максимальним. Ця точка гарантовано належить оптимальному вирівнюванню."),
        ("5. Рекурсивне розбиття:", "Залишаються лише прямокутники Top-Left та Bottom-Right (сумарна площа = 1/2 від початкової).")
    ]

    sy = ry + 55
    for title_s, body_s in steps:
        parts.append(text(rx + 15, sy, title_s, size=10, bold=True, anchor="start", color="#0f172a"))
        parts.append(text(rx + 15, sy + 15, body_s, size=9, anchor="start", color="#475569"))
        sy += 38

    # Complexity box at bottom right
    cy = ry + rh - 90
    parts.append(rect(rx + 15, cy, rw - 30, 75, fill="#eff6ff", stroke="#bfdbfe", sw=1, rx=4))
    parts.append(text(rx + rw / 2, cy + 18, "Сумарна складність Гіршберґа", size=10, bold=True, color="#1e40af"))
    parts.append(text(rx + rw / 2, cy + 38, "Час: NM · (1 + 1/2 + 1/4 + ...) = 2 · N · M = O(N · M)", size=9, color="#1e3a8a"))
    parts.append(text(rx + rw / 2, cy + 56, "Пам'ять: 2 · (M + 1) комірки = O(N + M)", size=9, bold=True, color="#166534"))

    render(os.path.join(IMG, "hirschberg-split.svg"), W, H, *parts)


def fig_patience_diff_anchors():
    W, H = 860, 500
    parts = []

    parts.append(rect(0, 0, W, H, fill="#ffffff", stroke="#e0e0e0", sw=1))
    parts.append(text(W / 2, 28, "Patience Diff проти Myers: збереження семантичних меж коду", size=15, bold=True))

    col_w = 380
    col_h = 410

    # Left Column: Standard Myers on Code
    lx, ly = 40, 65
    parts.append(rect(lx, ly, col_w, col_h, fill="#fffafb", stroke="#fca5a5", sw=1.2, rx=6))
    parts.append(text(lx + col_w / 2, ly + 24, "Стандартний Myers (LCS)", size=13, bold=True, color="#991b1b"))
    parts.append(text(lx + col_w / 2, ly + 40, "Жадібне зіставлення перших однакових дужок '}'", size=9, color=MUTED))

    # Myers diff visualization
    m_lines = [
        ("  void init() {", "#334155", "#ffffff"),
        ("-     setup_cache();", "#b91c1c", "#fee2e2"),
        ("+     setup_cache();", "#15803d", "#dcfce7"),
        ("+     init_metrics();", "#15803d", "#dcfce7"),
        ("  }", "#334155", "#ffffff"),
        (" ", "#64748b", "#ffffff"),
        ("- void process() {", "#b91c1c", "#fee2e2"),
        ("-     compute();", "#b91c1c", "#fee2e2"),
        ("- }", "#b91c1c", "#fee2e2"),
        ("+ void handle_req() {", "#15803d", "#dcfce7"),
        ("+     process();", "#15803d", "#dcfce7"),
        ("+ }", "#15803d", "#dcfce7"),
    ]
    
    my = ly + 65
    for text_line, col_text, col_bg in m_lines:
        parts.append(rect(lx + 15, my - 12, col_w - 30, 20, fill=col_bg, stroke="none"))
        parts.append(text(lx + 22, my + 3, text_line, size=10, color=col_text, anchor="start"))
        my += 22

    # Myers trap box
    parts.append(rect(lx + 15, ly + col_h - 75, col_w - 30, 60, fill="#fef2f2", stroke="#f87171", sw=1, rx=4))
    parts.append(text(lx + col_w / 2, ly + col_h - 56, "⚠️ Проблема жадібного збігу", size=10, bold=True, color="#b91c1c"))
    parts.append(text(lx + col_w / 2, ly + col_h - 38, "Дужка '}' функції process() зіставляється", size=9, color="#7f1d1d"))
    parts.append(text(lx + col_w / 2, ly + col_h - 24, "із закривальною дужкою старої функції init().", size=9, color="#7f1d1d"))

    # Right Column: Patience Diff
    rx, ry = 440, 65
    parts.append(rect(rx, ry, col_w, col_h, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    parts.append(text(rx + col_w / 2, ry + 24, "Patience Diff (LIS унікальних рядків)", size=13, bold=True, color="#166534"))
    parts.append(text(rx + col_w / 2, ry + 40, "Фіксація сигнатур функцій як непорушних якорів", size=9, color=MUTED))

    # Patience diff visualization
    p_lines = [
        ("  void init() {", "#334155", "#ffffff"),
        ("      setup_cache();", "#334155", "#ffffff"),
        ("+     init_metrics();", "#15803d", "#dcfce7"),
        ("  }", "#334155", "#ffffff"),
        (" ", "#64748b", "#ffffff"),
        ("- void process() {", "#b91c1c", "#fee2e2"),
        ("-     compute();", "#b91c1c", "#fee2e2"),
        ("- }", "#b91c1c", "#fee2e2"),
        ("+ void handle_req() {", "#15803d", "#dcfce7"),
        ("+     process();", "#15803d", "#dcfce7"),
        ("+ }", "#15803d", "#dcfce7"),
    ]

    py = ry + 65
    for text_line, col_text, col_bg in p_lines:
        parts.append(rect(rx + 15, py - 12, col_w - 30, 20, fill=col_bg, stroke="none"))
        # Highlight unique anchors
        if "void init()" in text_line or "void process()" in text_line or "void handle_req()" in text_line:
            parts.append(rect(rx + col_w - 105, py - 11, 85, 18, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=3))
            parts.append(text(rx + col_w - 62, py + 2, "Унікальний якір", size=9, bold=True, color="#1d4ed8"))
        parts.append(text(rx + 22, py + 3, text_line, size=10, color=col_text, anchor="start"))
        py += 22

    # Patience advantage box
    parts.append(rect(rx + 15, ry + col_h - 75, col_w - 30, 60, fill="#ecfdf5", stroke="#34d399", sw=1, rx=4))
    parts.append(text(rx + col_w / 2, ry + col_h - 56, "✓ Семантична цілісність блоків", size=10, bold=True, color="#065f46"))
    parts.append(text(rx + col_w / 2, ry + col_h - 38, "Опорні точки (сигнатури) фіксують контекст,", size=9, color="#047857"))
    parts.append(text(rx + col_w / 2, ry + col_h - 24, "дужки не плутаються між сусідніми функціями.", size=9, color="#047857"))

    render(os.path.join(IMG, "patience-diff-anchors.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_edit_graph_myers()
    fig_hirschberg_split()
    fig_patience_diff_anchors()
    print("All figures rendered successfully.")
