# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій до теми «Опукла оболонка множини точок».
svgkit імпортуємо зі scripts/ (не копіюємо), вивід у ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: Поняття опуклої оболонки та натягнута стрічка ─────────────────
def fig_convex_hull_concept():
    W, H = 900, 440
    P = []
    P.append(text(W / 2, 28, "Опукла оболонка: мінімальний охопний многокутник", size=16, bold=True))

    # Точки оболонки (за годинниковою або проти годинникової)
    hull_pts = [
        (130, 240), (220, 110), (440, 80), (670, 130),
        (780, 270), (690, 370), (390, 390), (190, 350)
    ]
    # Внутрішні точки
    inner_pts = [
        (260, 220), (320, 160), (450, 190), (540, 160), (600, 250),
        (480, 280), (340, 310), (530, 330), (380, 230), (270, 280)
    ]

    # Полігон оболонки
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in hull_pts)
    P.append('<polygon points="%s" fill="#eafaf1" stroke="%s" stroke-width="2.8"/>' % (pts_str, FIELD))

    # Стрічки/вектори натягу по ребрах
    for i in range(len(hull_pts)):
        p1 = hull_pts[i]
        p2 = hull_pts[(i + 1) % len(hull_pts)]
        P.append(line(p1[0], p1[1], p2[0], p2[1], color=FIELD, sw=2.5))

    # Малювання внутрішніх точок
    for x, y in inner_pts:
        P.append(circle(x, y, 5.0, fill="#eaf0fd", stroke=NEG, sw=2.0))

    # Малювання вершин оболонки
    for i, (x, y) in enumerate(hull_pts):
        P.append(circle(x, y, 7.5, fill=BG, stroke=FIELD, sw=2.8))
        P.append(circle(x, y, 3.5, fill=FIELD, stroke=FIELD, sw=1.0))

    # Позначки та підписи
    P.append(text(450, 230, "Внутрішні точки множини S", size=13, color=NEG, bold=True))
    P.append(text(450, 250, "(не впливають на межу)", size=11, color=MUTED))

    P.append(text(440, 58, "Вершина оболонки (опорна точка)", size=12, color=FIELD, bold=True))
    P.append(text(790, 298, "Ребро оболонки", size=12, color=FIELD, bold=True, anchor="start"))

    # Пояснювальний блок знизу
    body1, _, _ = textbox(250, 415, "Будь-який відрізок між точками S лежить усередині цієї зони",
                          size=11, pad=7, fill="#ffffff", stroke="#d0d7de", color=INK)
    P.append(body1)

    body2, _, _ = textbox(700, 415, "Пружна нитка, натягнута навколо штифтів-точок",
                          size=11, pad=7, fill="#ffffff", stroke="#d0d7de", color=FIELD)
    P.append(body2)

    render("img/convex-hull-concept.svg", W, H, *P)


# ── Фігура 2: Предикат повороту (орієнтація трійки точок) ───────────────────
def fig_orientation_turn():
    W, H = 920, 360
    P = []
    P.append(text(W / 2, 28, "Геометричний предикат повороту: знак векторного добутку", size=16, bold=True))

    centers = [160, 460, 760]
    titles = [
        "Лівий поворот (CCW)",
        "Правий поворот (CW)",
        "Колінеарні точки"
    ]
    subtitles = [
        "cross(p1, p2, p3) > 0",
        "cross(p1, p2, p3) < 0",
        "cross(p1, p2, p3) = 0"
    ]

    for i in range(3):
        cx = centers[i]
        P.append(rect(cx - 135, 55, 270, 285, fill="#fcfdfd", stroke="#d0d7de", rx=8))
        P.append(text(cx, 82, titles[i], size=14, bold=True, color=FIELD if i == 0 else (POS if i == 1 else MUTED)))
        P.append(text(cx, 102, subtitles[i], size=12, bold=True, color=INK))

    # 1. Лівий поворот
    ax, ay = 80, 270
    bx, by = 190, 210
    cx, cy = 180, 130
    P.append(arrow(ax, ay, bx, by, color=INK, sw=2.2))
    P.append(arrow(bx, by, cx, cy, color=FIELD, sw=2.2))
    P.append(line(ax, ay, bx + (bx-ax)*0.5, by + (by-ay)*0.5, color=MUTED, sw=1.2, dash="4 4"))
    P.append(circle(ax, ay, 5.5, fill=BG, stroke=INK, sw=2))
    P.append(circle(bx, by, 5.5, fill=BG, stroke=INK, sw=2))
    P.append(circle(cx, cy, 5.5, fill=BG, stroke=FIELD, sw=2.5))
    P.append(text(ax - 14, ay + 6, "A", size=13, bold=True))
    P.append(text(bx + 14, by + 10, "B", size=13, bold=True))
    P.append(text(cx + 14, cy - 4, "C", size=13, bold=True, color=FIELD))
    # Дуга повороту ліворуч
    P.append('<path d="M 215 195 A 30 30 0 0 0 190 165" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>' % FIELD)
    P.append(text(160, 318, "C ліворуч від вектора AB", size=11, color=FIELD, bold=True))

    # 2. Правий поворот
    ax, ay = 380, 270
    bx, by = 470, 180
    cx, cy = 540, 240
    P.append(arrow(ax, ay, bx, by, color=INK, sw=2.2))
    P.append(arrow(bx, by, cx, cy, color=POS, sw=2.2))
    P.append(line(ax, ay, bx + (bx-ax)*0.5, by + (by-ay)*0.5, color=MUTED, sw=1.2, dash="4 4"))
    P.append(circle(ax, ay, 5.5, fill=BG, stroke=INK, sw=2))
    P.append(circle(bx, by, 5.5, fill=BG, stroke=INK, sw=2))
    P.append(circle(cx, cy, 5.5, fill=BG, stroke=POS, sw=2.5))
    P.append(text(ax - 14, ay + 6, "A", size=13, bold=True))
    P.append(text(bx - 12, by - 12, "B", size=13, bold=True))
    P.append(text(cx + 14, cy + 6, "C", size=13, bold=True, color=POS))
    # Дуга повороту праворуч
    P.append('<path d="M 505 145 A 30 30 0 0 1 520 185" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>' % POS)
    P.append(text(460, 318, "C праворуч від вектора AB", size=11, color=POS, bold=True))

    # 3. Колінеарні
    ax, ay = 670, 260
    bx, by = 750, 205
    cx, cy = 830, 150
    P.append(arrow(ax, ay, bx, by, color=INK, sw=2.2))
    P.append(arrow(bx, by, cx, cy, color=MUTED, sw=2.2))
    P.append(circle(ax, ay, 5.5, fill=BG, stroke=INK, sw=2))
    P.append(circle(bx, by, 5.5, fill=BG, stroke=INK, sw=2))
    P.append(circle(cx, cy, 5.5, fill=BG, stroke=MUTED, sw=2.5))
    P.append(text(ax - 14, ay + 6, "A", size=13, bold=True))
    P.append(text(bx - 12, by - 12, "B", size=13, bold=True))
    P.append(text(cx + 14, cy - 4, "C", size=13, bold=True, color=MUTED))
    P.append(text(760, 318, "A, B, C лежать на одній прямій", size=11, color=MUTED, bold=True))

    render("img/orientation-turn.svg", W, H, *P)


# ── Фігура 3: Алгоритм Ендрю (монотонний ланцюг) ───────────────────────────
def fig_monotone_chain():
    W, H = 960, 460
    P = []
    P.append(text(W / 2, 28, "Побудова монотонного ланцюга Ендрю (Andrew's Monotone Chain)", size=16, bold=True))

    # 4 квадранти
    panels = [
        (30, 50, 435, 185, "1. Сортування за x (та y)", "Впорядкування O(n log n) зліва направо"),
        (495, 50, 435, 185, "2. Нижня оболонка (Lower Hull)", "Стек: лише ліві повороти зліва направо"),
        (30, 255, 435, 185, "3. Верхня оболонка (Upper Hull)", "Стек: лише ліві повороти справа наліво"),
        (495, 255, 435, 185, "4. Об'єднання ланцюгів", "Видалення дублікатів крайніх точок")
    ]

    for px, py, pw, ph, title_p, desc_p in panels:
        P.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#d0d7de", rx=6))
        P.append(text(px + 14, py + 22, title_p, size=13, bold=True, anchor="start", color=INK))
        P.append(text(px + pw - 14, py + 22, desc_p, size=10.5, color=MUTED, anchor="end"))

    # Панель 1: Сортовані точки з номерами
    p1_pts = [(70 + i*60, 110 + (30 if i%2 else 70)) for i in range(6)]
    for i, (x, y) in enumerate(p1_pts):
        P.append(circle(x, y, 5.5, fill="#eaf0fd", stroke=NEG, sw=2.0))
        P.append(text(x, y - 10, "p%d" % (i+1), size=11, bold=True, color=NEG))
    P.append(arrow(60, 215, 420, 215, color=MUTED, sw=1.5))
    P.append(text(430, 219, "+x", size=11, color=MUTED, anchor="start", bold=True))

    # Панель 2: Нижня оболонка
    p2_pts = [(535 + i*60, 110 + (30 if i%2 else 70)) for i in range(6)]
    # Ребра нижньої оболонки: p1 -> p3 -> p5 -> p6
    lower_idx = [0, 2, 4, 5]
    for i in range(len(lower_idx) - 1):
        i1, i2 = lower_idx[i], lower_idx[i+1]
        P.append(line(p2_pts[i1][0], p2_pts[i1][1], p2_pts[i2][0], p2_pts[i2][1], color=FIELD, sw=2.5))
    # Відхилені точки (нелівий поворот)
    P.append(line(p2_pts[0][0], p2_pts[0][1], p2_pts[1][0], p2_pts[1][1], color=POS, sw=1.5, dash="3 3"))
    P.append(line(p2_pts[1][0], p2_pts[1][1], p2_pts[2][0], p2_pts[2][1], color=POS, sw=1.5, dash="3 3"))
    P.append(text(p2_pts[1][0], p2_pts[1][1] - 12, "виштовхнуто (CW)", size=10, color=POS, bold=True))

    for i, (x, y) in enumerate(p2_pts):
        is_hull = i in lower_idx
        c_col = FIELD if is_hull else MUTED
        P.append(circle(x, y, 5.0, fill=BG, stroke=c_col, sw=2.0))

    # Панель 3: Верхня оболонка
    p3_pts = [(70 + i*60, 315 + (30 if i%2 else 70)) for i in range(6)]
    upper_idx = [5, 3, 1, 0]
    for i in range(len(upper_idx) - 1):
        i1, i2 = upper_idx[i], upper_idx[i+1]
        P.append(line(p3_pts[i1][0], p3_pts[i1][1], p3_pts[i2][0], p3_pts[i2][1], color=NEG, sw=2.5))
    for i, (x, y) in enumerate(p3_pts):
        is_hull = i in upper_idx
        c_col = NEG if is_hull else MUTED
        P.append(circle(x, y, 5.0, fill=BG, stroke=c_col, sw=2.0))
    P.append(arrow(410, 420, 60, 420, color=NEG, sw=1.5))
    P.append(text(50, 424, "-x", size=11, color=NEG, anchor="end", bold=True))

    # Панель 4: Повний полігон
    p4_pts = [(535 + i*60, 315 + (30 if i%2 else 70)) for i in range(6)]
    hull_all = [p4_pts[0], p4_pts[2], p4_pts[4], p4_pts[5], p4_pts[3], p4_pts[1]]
    poly_str = " ".join("%.1f,%.1f" % (x, y) for x, y in hull_all)
    P.append('<polygon points="%s" fill="#eafaf1" stroke="%s" stroke-width="2.6"/>' % (poly_str, FIELD))
    for x, y in p4_pts:
        P.append(circle(x, y, 5.5, fill=BG, stroke=FIELD, sw=2.2))
    P.append(text(712, 385, "Замкнена опукла оболонка", size=12, color=FIELD, bold=True))

    render("img/monotone-chain-steps.svg", W, H, *P)


# ── Фігура 4: Розбиття у Quickhull ──────────────────────────────────────────
def fig_quickhull_partition():
    W, H = 920, 400
    P = []
    P.append(text(W / 2, 28, "Алгоритм Quickhull: розділення площини та відкидання точок", size=16, bold=True))

    # Базові точки
    min_x = (110, 240)
    max_x = (810, 240)
    p_furthest = (460, 80)

    # Внутрішній трикутник
    tri_pts = [min_x, p_furthest, max_x]
    tri_str = " ".join("%.1f,%.1f" % (x, y) for x, y in tri_pts)
    P.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="1.8" stroke-dasharray="4 3"/>' % (tri_str, POS))

    # Базова пряма
    P.append(line(min_x[0], min_x[1], max_x[0], max_x[1], color=INK, sw=2.2))

    # Висота до найвіддаленішої точки
    P.append(line(p_furthest[0], p_furthest[1], p_furthest[0], 240, color=MUTED, sw=1.5, dash="3 3"))
    P.append(text(p_furthest[0] + 12, 165, "h_max (макс. відстань)", size=11, color=MUTED, anchor="start"))

    # Внутрішні точки (всередині трикутника - відкидаються)
    discarded = [
        (320, 200), (430, 180), (520, 190), (610, 210), (460, 220), (370, 225)
    ]
    for x, y in discarded:
        P.append(circle(x, y, 4.5, fill="#fdecea", stroke=POS, sw=1.8))
        # Хрестик відкидання
        P.append(line(x-3, y-3, x+3, y+3, color=POS, sw=1.2))
        P.append(line(x-3, y+3, x+3, y-3, color=POS, sw=1.2))

    # Точки підмножини S1 (ліворуч від p_furthest)
    s1_pts = [(220, 120), (310, 95), (260, 150)]
    for x, y in s1_pts:
        P.append(circle(x, y, 5.0, fill="#eafaf1", stroke=FIELD, sw=2.0))

    # Точки підмножини S2 (праворуч від p_furthest)
    s2_pts = [(620, 110), (700, 140), (660, 85)]
    for x, y in s2_pts:
        P.append(circle(x, y, 5.0, fill="#eafaf1", stroke=FIELD, sw=2.0))

    # Нижні точки
    lower_pts = [(280, 310), (490, 340), (680, 290)]
    for x, y in lower_pts:
        P.append(circle(x, y, 5.0, fill="#eaf0fd", stroke=NEG, sw=2.0))

    # Опорні вершини
    P.append(circle(min_x[0], min_x[1], 7.0, fill=BG, stroke=INK, sw=2.5))
    P.append(circle(max_x[0], max_x[1], 7.0, fill=BG, stroke=INK, sw=2.5))
    P.append(circle(p_furthest[0], p_furthest[1], 7.0, fill=BG, stroke=FIELD, sw=2.8))

    P.append(text(min_x[0] - 12, min_x[1] + 20, "P_min (min x)", size=12, bold=True, anchor="end"))
    P.append(text(max_x[0] + 12, max_x[1] + 20, "P_max (max x)", size=12, bold=True, anchor="start"))
    P.append(text(p_furthest[0], p_furthest[1] - 14, "C (найвіддаленіша точка над AB)", size=13, bold=True, color=FIELD))

    # Підписи підмножин
    body_s1, _, _ = textbox(260, 60, "Підмножина S1 (рекурсія над AC)", size=11, pad=6, fill="#ffffff", stroke=FIELD, color=FIELD)
    P.append(body_s1)
    body_s2, _, _ = textbox(660, 60, "Підмножина S2 (рекурсія над CB)", size=11, pad=6, fill="#ffffff", stroke=FIELD, color=FIELD)
    P.append(body_s2)

    P.append(text(460, 205, "Точки всередині ΔABC відкидаються", size=12, bold=True, color=POS))
    P.append(text(460, 320, "Підмножина нижніх точок (рекурсія під AB)", size=12, bold=True, color=NEG))

    render("img/quickhull-partition.svg", W, H, *P)


if __name__ == "__main__":
    fig_convex_hull_concept()
    fig_orientation_turn()
    fig_monotone_chain()
    fig_quickhull_partition()
    print("OK: 4 figures -> img/")
