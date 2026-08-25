# -*- coding: utf-8 -*-
"""
Фігури до статті «Пошук найближчого сусіда: точний перебір, індекс і наближена відповідь».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_exact_partition_pruning():
    """Фігура 1: Відсікання простору за нерівністю трикутника (метричне дерево / опорна точка)."""
    W, H = 840, 420
    parts = []

    parts.append(text(W / 2, 26, "Геометричне відтинання пошуку за нерівністю трикутника", size=16, bold=True, color=INK))

    # Ліва панель: 2D розбиття сферичною межею (Ball/VP partition)
    bx1, by1, bw1, bh1 = 30, 45, 400, 355
    parts.append(rect(bx1, by1, bw1, bh1, fill="#fcfcfc", stroke="#d0d0d0", sw=1, rx=6))
    parts.append(text(bx1 + bw1 / 2, by1 + 22, "Розбиття простору опорною точкою P", size=13, bold=True, color=INK))

    # Центр опорної точки P
    px, py = bx1 + 180, by1 + 195
    r_split = 110  # Радіус поділу

    # Затінення внутрішньої та зовнішньої півсфер
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#edf7ed" stroke="%s" stroke-width="1.8" stroke-dasharray="5,5"/>' % (px, py, r_split, FIELD))
    parts.append(text(px, py - r_split - 8, "Сферична межа розбиття R_split", size=11, color=FIELD, bold=True))

    # Запит q та його радіус пошуку r
    qx, qy = bx1 + 325, by1 + 95
    rq = 50  # Поточна найкраща відстань до сусіда
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fde8e8" fill-opacity="0.6" stroke="%s" stroke-width="1.8"/>' % (qx, qy, rq, POS))

    # Точка q
    parts.append(circle(qx, qy, 5, fill=POS, stroke=LINE, sw=1.2))
    parts.append(text(qx + 12, qy - 8, "Запит q", size=12, color=POS, bold=True, anchor="start"))
    parts.append(text(qx + rq + 6, qy + 16, "Радіус r (d_min)", size=10, color=POS, italic=True, anchor="start"))

    # Точка P
    parts.append(circle(px, py, 5, fill=NEG, stroke=LINE, sw=1.2))
    parts.append(text(px - 12, py + 18, "Опорна точка P", size=12, color=NEG, bold=True, anchor="end"))

    # Відрізок між P та q
    parts.append(line(px, py, qx, qy, color=LINE, sw=1.5, dash="3,3"))
    mid_x, mid_y = (px + qx) / 2, (py + qy) / 2
    parts.append(text(mid_x - 15, mid_y - 10, "d(q, P)", size=11, color=INK, bold=True))

    # Точки всередині сфери
    in_pts = [(px - 50, py - 40), (px - 30, py + 50), (px + 40, py + 30), (px - 60, py + 20)]
    for ix, iy in in_pts:
        parts.append(circle(ix, iy, 3.5, fill=FIELD, stroke=LINE, sw=1))
    parts.append(text(px - 40, py - 60, "Піддерево: d(P, x) ≤ R", size=10, color=FIELD, italic=True))

    # Точки ззовні
    out_pts = [(bx1 + 50, by1 + 70), (bx1 + 330, by1 + 280), (bx1 + 80, by1 + 310)]
    for ox, oy in out_pts:
        parts.append(circle(ox, oy, 3.5, fill=MUTED, stroke=LINE, sw=1))
    parts.append(text(bx1 + 90, by1 + 330, "Піддерево: d(P, x) > R", size=10, color=MUTED, italic=True))

    # Права панель: Алгебраїчна умова відсікання
    bx2, by2, bw2, bh2 = 450, 45, 360, 355
    parts.append(rect(bx2, by2, bw2, bh2, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(text(bx2 + bw2 / 2, by2 + 22, "Правило відсікання піддерева", size=13, bold=True, color=INK))

    tb1, _, _ = textbox(bx2 + bw2 / 2, by2 + 80,
                        "Нерівність трикутника:\n|d(q, P) − d(P, x)| ≤ d(q, x)",
                        size=12, pad=10, fill="#ffffff", stroke="#94a3b8", bold=True)
    parts.append(tb1)

    tb2, _, _ = textbox(bx2 + bw2 / 2, by2 + 180,
                        "Умова повного пропуску кулі:\nЯкщо d(q, P) − R_split > r,\nто для всіх внутрішніх x:\nd(q, x) > r (немає ближчих!)",
                        size=11, pad=10, fill="#f0fdf4", stroke=FIELD, color=INK)
    parts.append(tb2)

    tb3, _, _ = textbox(bx2 + bw2 / 2, by2 + 290,
                        "Результат: усе внутрішнє піддерево\nвідкидається за ОДНЕ обчислення d(q, P)\nбез перевірки окремих точок.",
                        size=11, pad=10, fill="#ffffff", stroke="#cbd5e1", color=MUTED)
    parts.append(tb3)

    render(os.path.join(IMG, "exact-partition-pruning.svg"), W, H, *parts)


def fig_curse_of_dimensionality_search():
    """Фігура 2: Прокляття розмірності та деградація просторових дерев."""
    W, H = 840, 420
    parts = []

    parts.append(text(W / 2, 26, "Прокляття розмірності: розпад просторового індексування", size=16, bold=True, color=INK))

    # Ліва панель: 2D простір (Ефективний пошук)
    bx1, by1, bw1, bh1 = 30, 45, 370, 355
    parts.append(rect(bx1, by1, bw1, bh1, fill="#f4fbf7", stroke=FIELD, sw=1.2, rx=6))
    parts.append(text(bx1 + bw1 / 2, by1 + 22, "Низька розмірність (2D/3D): O(log N)", size=13, bold=True, color=FIELD))

    # Сітка розбиття KD-дерева 2D
    gx, gy, gw, gh = bx1 + 35, by1 + 45, 300, 200
    parts.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#94a3b8", sw=1))
    # Вертикальний поділ
    parts.append(line(gx + 160, gy, gx + 160, gy + gh, color="#64748b", sw=1.5))
    # Горизонтальні поділи
    parts.append(line(gx, gy + 110, gx + 160, gy + 110, color="#94a3b8", sw=1.2, dash="3,3"))
    parts.append(line(gx + 160, gy + 80, gx + gw, gy + 80, color="#94a3b8", sw=1.2, dash="3,3"))

    # Запит q та куля пошуку в 2D
    cqx, cqy = gx + 70, gy + 55
    cr = 38
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#dcfce7" stroke="%s" stroke-width="1.8"/>' % (cqx, cqy, cr, FIELD))
    parts.append(circle(cqx, cqy, 4.5, fill=POS, stroke=LINE, sw=1))
    parts.append(text(cqx, cqy - 8, "q", size=11, bold=True, color=POS))

    parts.append(text(bx1 + bw1 / 2, by1 + 270, "Куля запиту перетинає 1 клітинку", size=11, bold=True, color=FIELD))
    parts.append(text(bx1 + bw1 / 2, by1 + 295, "90% гілок дерева відсікаються миттєво", size=11, color=MUTED))
    parts.append(text(bx1 + bw1 / 2, by1 + 325, "Перевіряється лише < 5% точок бази", size=11, color=INK))

    # Права панель: Висока розмірність D > 64 (Деградація)
    bx2, by2, bw2, bh2 = 440, 45, 370, 355
    parts.append(rect(bx2, by2, bw2, bh2, fill="#fef2f2", stroke=POS, sw=1.2, rx=6))
    parts.append(text(bx2 + bw2 / 2, by2 + 22, "Висока розмірність (D > 64): O(N)", size=13, bold=True, color=POS))

    # Концентрація об'єму на гіперкубі
    hx, hy, hw, hh = bx2 + 35, by2 + 45, 300, 200
    parts.append(rect(hx, hy, hw, hh, fill="#ffffff", stroke="#fca5a5", sw=1))

    # Багато перетинів гіперплощинами
    for i in range(1, 6):
        parts.append(line(hx + i * 50, hy, hx + i * 50, hy + hh, color="#fca5a5", sw=1, dash="2,2"))
    for j in range(1, 4):
        parts.append(line(hx, hy + j * 50, hx + hw, hy + j * 50, color="#fca5a5", sw=1, dash="2,2"))

    # Велика куля запиту, що зачіпає всі межі через концентрацію відстаней
    hqx, hqy = hx + 150, hy + 100
    hr = 85
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fee2e2" fill-opacity="0.6" stroke="%s" stroke-width="1.8"/>' % (hqx, hqy, hr, POS))
    parts.append(circle(hqx, hqy, 4.5, fill=POS, stroke=LINE, sw=1))
    parts.append(text(hqx, hqy - 8, "q", size=11, bold=True, color=POS))

    parts.append(text(bx2 + bw2 / 2, by2 + 270, "Куля запиту перетинає майже всі межі", size=11, bold=True, color=POS))
    parts.append(text(bx2 + bw2 / 2, by2 + 295, "Бекґтрекінг обходить 95–100% листків", size=11, color=MUTED))
    parts.append(text(bx2 + bw2 / 2, by2 + 325, "Дерево стає повільнішим за прямий SIMD-скан", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "curse-of-dimensionality-search.svg"), W, H, *parts)


def fig_ann_taxonomy_methods():
    """Фігура 3: Таксономія 4 головних родин наближеного пошуку (ANN)."""
    W, H = 840, 420
    parts = []

    parts.append(text(W / 2, 26, "Чотири родини індексів наближеного пошуку (ANN)", size=16, bold=True, color=INK))

    col_w = 180
    gap = 20
    top_y = 50
    card_h = 350

    cards = [
        ("Дерева та ліси", "Tree-based", "#3b82f6", [
            "Ідея: випадкові проєкції",
            "та бінарне розбиття.",
            "— KD-ліс (FLANN)",
            "— Annoy (RP-дерева)",
            "",
            "Плюси: проста побудова",
            "Мінуси: пам'ять на ліс,",
            "падіння при D > 128"
        ]),
        ("Хешування", "Hashing (LSH)", "#8b5cf6", [
            "Ідея: колізії для близьких",
            "точок у спільні бакети.",
            "— SimHash, Cross-Polytope",
            "— Multi-probe LSH",
            "",
            "Плюси: гарантії збіжності",
            "Мінуси: багато таблиць,",
            "великий оверхед пам'яті"
        ]),
        ("Квантування", "Quantization", "#10b981", [
            "Ідея: стиснення векторів",
            "у короткі байт-коди.",
            "— Product Quant (PQ)",
            "— IVF-PQ (Faiss)",
            "",
            "Плюси: стиснення до 95%,",
            "мільярдні бази в RAM",
            "Мінуси: втрата деталізації"
        ]),
        ("Графи сусідства", "Graph-based", "#ef4444", [
            "Ідея: жадібний блукач",
            "по малому світу.",
            "— HNSW, NSW",
            "— Vamana / DiskANN",
            "",
            "Плюси: найвищий Recall/QPS",
            "Мінуси: довга побудова,",
            "високе споживання RAM"
        ])
    ]

    for i, (title, sub, col, lines) in enumerate(cards):
        cx = 30 + i * (col_w + gap)
        # Рамка картки
        parts.append(rect(cx, top_y, col_w, card_h, fill="#fafafa", stroke=col, sw=1.5, rx=6))
        # Плашка заголовка
        parts.append(rect(cx, top_y, col_w, 48, fill=col, stroke=col, sw=1, rx=6))
        parts.append(text(cx + col_w / 2, top_y + 20, title, size=13, bold=True, color="#ffffff"))
        parts.append(text(cx + col_w / 2, top_y + 38, sub, size=10, italic=True, color="#e0e7ff"))

        # Текст
        curr_y = top_y + 70
        for ln in lines:
            if not ln:
                curr_y += 8
                continue
            is_header = ln.startswith("Плюси:") or ln.startswith("Мінуси:")
            bold_flag = is_header
            text_col = INK if not is_header else (FIELD if ln.startswith("Плюси:") else POS)
            parts.append(text(cx + 12, curr_y, ln, size=11, bold=bold_flag, color=text_col, anchor="start"))
            curr_y += 22

    render(os.path.join(IMG, "ann-taxonomy-methods.svg"), W, H, *parts)


def fig_ann_tradeoff_quadrangle():
    """Фігура 4: Чотирикутний компроміс параметрів індексування (Recall, QPS, Memory, Build)."""
    W, H = 840, 420
    parts = []

    parts.append(text(W / 2, 26, "Інженерний компроміс систем векторного пошуку", size=16, bold=True, color=INK))

    # Центр діаграми
    ox, oy = 240, 230
    L_axis = 140

    # Сітка рівнів 25%, 50%, 75%, 100%
    for step in [0.25, 0.5, 0.75, 1.0]:
        r_step = L_axis * step
        pts = [
            (ox, oy - r_step),
            (ox + r_step, oy),
            (ox, oy + r_step),
            (ox - r_step, oy)
        ]
        pts_str = " ".join("%.1f,%.1f" % p for p in pts)
        parts.append('<polygon points="%s" fill="none" stroke="#e2e8f0" stroke-width="1.2"/>' % pts_str)

    # Осі
    parts.append(line(ox - L_axis - 10, oy, ox + L_axis + 10, oy, color="#94a3b8", sw=1.5))
    parts.append(line(ox, oy - L_axis - 10, ox, oy + L_axis + 10, color="#94a3b8", sw=1.5))

    # Підписи осей
    parts.append(text(ox, oy - L_axis - 15, "Точність (Recall@k)", size=11, bold=True, color=INK))
    parts.append(text(ox + L_axis + 15, oy + 4, "Швидкість (QPS)", size=11, bold=True, color=INK, anchor="start"))
    parts.append(text(ox, oy + L_axis + 20, "Компактність (RAM)", size=11, bold=True, color=INK))
    parts.append(text(ox - L_axis - 15, oy + 4, "Оновлення (Build)", size=11, bold=True, color=INK, anchor="end"))

    # Полігон 1: HNSW
    p_hnsw = [
        (ox, oy - L_axis * 0.95),
        (ox + L_axis * 0.90, oy),
        (ox, oy + L_axis * 0.35),
        (ox - L_axis * 0.30, oy)
    ]
    parts.append('<polygon points="%s" fill="#ef4444" fill-opacity="0.25" stroke="#ef4444" stroke-width="2"/>' % " ".join("%.1f,%.1f" % p for p in p_hnsw))

    # Полігон 2: IVF-PQ
    p_ivfpq = [
        (ox, oy - L_axis * 0.75),
        (ox + L_axis * 0.70, oy),
        (ox, oy + L_axis * 0.95),
        (ox - L_axis * 0.60, oy)
    ]
    parts.append('<polygon points="%s" fill="#10b981" fill-opacity="0.25" stroke="#10b981" stroke-width="2"/>' % " ".join("%.1f,%.1f" % p for p in p_ivfpq))

    # Полігон 3: Exact Brute Force
    p_flat = [
        (ox, oy - L_axis * 1.0),
        (ox + L_axis * 0.15, oy),
        (ox, oy + L_axis * 0.70),
        (ox - L_axis * 1.0, oy)
    ]
    parts.append('<polygon points="%s" fill="#3b82f6" fill-opacity="0.20" stroke="#3b82f6" stroke-width="2" stroke-dasharray="4,4"/>' % " ".join("%.1f,%.1f" % p for p in p_flat))

    # Легенда праворуч
    lx, ly, lw, lh = 500, 65, 310, 325
    parts.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    parts.append(text(lx + lw / 2, ly + 25, "Порівняння стратегій пошуку", size=13, bold=True, color=INK))

    items = [
        ("#3b82f6", "Точний скан (Flat Brute Force)", "100% Recall, нульовий індекс,\nале низький QPS при N > 100k"),
        ("#ef4444", "Графовий індекс (HNSW)", "Максимальний QPS і точність (98%+),\nвимагає +150..300% пам'яті під ребра"),
        ("#10b981", "Стиснення (IVF-PQ)", "Стискає базу до 4–16 разів,\nшвидкий пошук ціною квантування")
    ]

    cur_ly = ly + 65
    for col, name, desc in items:
        parts.append(rect(lx + 15, cur_ly - 8, 16, 16, fill=col, stroke=LINE, sw=1, rx=3))
        parts.append(text(lx + 40, cur_ly + 5, name, size=12, bold=True, color=INK, anchor="start"))
        lines = desc.split("\n")
        parts.append(text(lx + 40, cur_ly + 23, lines[0], size=10, color=MUTED, anchor="start"))
        parts.append(text(lx + 40, cur_ly + 37, lines[1], size=10, color=MUTED, anchor="start"))
        cur_ly += 80

    render(os.path.join(IMG, "ann-quadrangle-tradeoff.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_exact_partition_pruning()
    fig_curse_of_dimensionality_search()
    fig_ann_taxonomy_methods()
    fig_ann_tradeoff_quadrangle()
    print("All figures generated successfully.")
