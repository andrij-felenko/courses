# -*- coding: utf-8 -*-
"""Фігури до статті «Гілки, злиття, ребейз і пошук регресії». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
BLUE_FILL = "#eaf0fd"
RED_FILL = "#fdecea"
GRAY_FILL = "#eceff1"


def node(cx, cy, label, r=24, fill=FILL, stroke=INK, sw=2, tsize=14, tcolor=INK):
    s = circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw)
    s += text(cx, cy + 5, label, size=tsize, bold=True, color=tcolor)
    return s


def under(cx, cy, r, s, size=12, color=MUTED, gap=18):
    return text(cx, cy + r + gap, s, size=size, color=color)


def tag(cx, cy, s, fill=BLUE_FILL, stroke=NEG):
    body, w, h = textbox(cx, cy, s, size=13, pad=8, fill=fill, stroke=stroke, sw=1.5, color=INK, bold=True)
    return body


# ── 1. Гілка як ім'я коміта + два можливі стосунки двох гілок ────────────────
def fig_refs():
    W, H = 1000, 530
    p = []

    # ── ліва колонка: два випадки ───────────────────────────────────────────
    p.append(rect(30, 62, 470, 190, fill=BG, stroke=MUTED, sw=1.2))
    p.append(text(265, 92, "Розбіжності немає: main — предок feature", size=14, bold=True))
    ys = 168
    xs = [120, 210, 300, 390]
    for i in range(1, 4):
        p.append(arrow(xs[i] - 22, ys, xs[i - 1] + 22, ys, color=MUTED, sw=1.6))
    for x, lab in zip(xs, ["A", "B", "C", "D"]):
        p.append(node(x, ys, lab, r=22))
    p.append(tag(210, 228, "main"))
    p.append(tag(390, 228, "feature", fill=GREEN_FILL, stroke=FIELD))

    p.append(rect(30, 272, 470, 226, fill=BG, stroke=MUTED, sw=1.2))
    p.append(text(265, 302, "Розбіжність: жоден не предок другого", size=14, bold=True))
    p.append(node(110, 400, "A", r=22))
    p.append(node(196, 400, "B", r=22))
    p.append(arrow(196 - 22, 400, 110 + 22, 400, color=MUTED, sw=1.6))
    p.append(node(300, 356, "M1", r=22))
    p.append(node(386, 356, "M2", r=22))
    p.append(node(300, 452, "F1", r=22))
    p.append(node(386, 452, "F2", r=22))
    p.append(arrow(386 - 22, 356, 300 + 22, 356, color=MUTED, sw=1.6))
    p.append(arrow(386 - 22, 452, 300 + 22, 452, color=MUTED, sw=1.6))
    p.append(arrow(282, 366, 214, 392, color=MUTED, sw=1.6))
    p.append(arrow(282, 442, 214, 410, color=MUTED, sw=1.6))
    p.append(tag(452, 356, "main"))
    p.append(tag(452, 452, "feature", fill=GREEN_FILL, stroke=FIELD))

    # ── права колонка: ланцюг імен ──────────────────────────────────────────
    p.append(rect(530, 62, 440, 436, fill=BG, stroke=MUTED, sw=1.2))
    p.append(text(750, 92, "Гілка — ім'я коміта, HEAD — ім'я гілки", size=14, bold=True))

    b1, w1, h1 = textbox(750, 158, ".git/HEAD\nref: refs/heads/feature", size=13, pad=12)
    p.append(b1)
    p.append(arrow(750, 158 + h1 / 2 + 4, 750, 236, color=NEG, sw=1.8))
    b2, w2, h2 = textbox(750, 282, ".git/refs/heads/feature\n7e0b94c1…", size=13, pad=12)
    p.append(b2)
    p.append(arrow(750, 282 + h2 / 2 + 4, 750, 372, color=NEG, sw=1.8))
    p.append(node(750, 404, "F2", r=26))
    p.append(text(750, 458, "коміт із таким хешем", size=12, color=MUTED))
    p.append(text(750, 482, "новий коміт → у файлі гілки новий хеш", size=12, color=MUTED))

    render(os.path.join(IMG, "refs-and-divergence.svg"), W, H, *p,
           title="Що таке гілка й коли дві гілки розійшлися")


# ── 2. Злиття проти ребейзу ─────────────────────────────────────────────────
def fig_merge_rebase():
    W, H = 1020, 480
    p = []

    # ЗЛИТТЯ ────────────────────────────────────────────────────────────────
    p.append(rect(30, 60, 470, 386, fill=BG, stroke=MUTED, sw=1.2))
    p.append(text(265, 90, "Злиття: додано вузол, старі імена цілі", size=14, bold=True))
    p.append(node(110, 244, "A"))
    p.append(under(110, 244, 24, "3f1a"))
    p.append(node(190, 244, "B"))
    p.append(under(190, 244, 24, "7e0b"))
    p.append(arrow(190 - 24, 244, 110 + 24, 244, color=MUTED, sw=1.6))

    p.append(node(286, 172, "M1"))
    p.append(text(286, 138, "c412", size=12, color=MUTED))
    p.append(arrow(286 - 22, 182, 190 + 16, 224, color=MUTED, sw=1.6))

    p.append(node(286, 322, "F1"))
    p.append(under(286, 322, 24, "91ab"))
    p.append(node(366, 322, "F2"))
    p.append(under(366, 322, 24, "55dc"))
    p.append(arrow(366 - 24, 322, 286 + 24, 322, color=MUTED, sw=1.6))
    p.append(arrow(286 - 22, 312, 190 + 16, 266, color=MUTED, sw=1.6))

    p.append(node(452, 244, "M", fill=BLUE_FILL, stroke=NEG))
    p.append(under(452, 244, 24, "b83e", color=NEG))
    p.append(arrow(452 - 22, 234, 286 + 22, 182, color=NEG, sw=1.8))
    p.append(arrow(452 - 22, 254, 366 + 22, 312, color=NEG, sw=1.8))
    p.append(text(265, 412, "жоден зі старих хешів не змінився", size=13, color=INK))

    # РЕБЕЙЗ ────────────────────────────────────────────────────────────────
    p.append(rect(520, 60, 470, 386, fill=BG, stroke=MUTED, sw=1.2))
    p.append(text(755, 90, "Ребейз: коміти перераховано, імена нові", size=14, bold=True))
    row = 190
    xs = [592, 672, 752, 838, 918]
    labs = ["A", "B", "M1", "F1′", "F2′"]
    hs = ["3f1a", "7e0b", "c412", "2b7e", "a94f"]
    for i in range(1, 5):
        p.append(arrow(xs[i] - 24, row, xs[i - 1] + 24, row, color=MUTED, sw=1.6))
    for i, (x, lab, h) in enumerate(zip(xs, labs, hs)):
        new = i >= 3
        p.append(node(x, row, lab, fill=RED_FILL if new else FILL, stroke=POS if new else INK))
        p.append(under(x, row, 24, h, color=POS if new else MUTED))

    p.append(node(838, 330, "F1", fill=GRAY_FILL, stroke=MUTED))
    p.append(under(838, 330, 24, "91ab"))
    p.append(node(918, 330, "F2", fill=GRAY_FILL, stroke=MUTED))
    p.append(under(918, 330, 24, "55dc"))
    p.append(line(918 - 24, 330, 838 + 24, 330, color=MUTED, sw=1.4, dash="5,4"))
    p.append(line(838 - 24, 322, 672 + 20, 216, color=MUTED, sw=1.4, dash="5,4"))
    p.append(text(755, 412, "старі F1, F2 лишилися без імені — тільки в reflog", size=13, color=INK))

    render(os.path.join(IMG, "merge-vs-rebase.svg"), W, H, *p,
           title="Два виходи з розбіжності: злити або перерахувати")


# ── 3. Bisect на графі ──────────────────────────────────────────────────────
def fig_bisect():
    W, H = 940, 500
    p = []

    main_y = 190
    G = (90, main_y)
    C1, C2, C3, C4 = (190, main_y), (290, main_y), (390, main_y), (490, main_y)
    M = (640, main_y)
    C6 = (750, main_y)
    S1, S2 = (340, 340), (470, 340)

    def edge(a, b, color=MUTED, sw=1.6):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        d = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / d, dy / d
        return arrow(x1 + ux * 26, y1 + uy * 26, x2 - ux * 30, y2 - uy * 30, color=color, sw=sw)

    for a, b in [(C1, G), (C2, C1), (C3, C2), (C4, C3), (M, C4), (C6, M), (S1, C2), (S2, S1), (M, S2)]:
        p.append(edge(a, b))

    p.append(node(*G, "G", fill=GREEN_FILL, stroke=FIELD, r=26))
    p.append(text(G[0], G[1] - 44, "добрий", size=13, color=FIELD, bold=True))
    p.append(node(*C6, "C6", fill=RED_FILL, stroke=POS, r=26))
    p.append(text(C6[0], C6[1] - 44, "поганий", size=13, color=POS, bold=True))

    scored = [(C1, "C1", 1, 1, -1), (C2, "C2", 2, 2, -1), (C3, "C3", 3, 3, -1),
              (C4, "C4", 4, 4, -1), (M, "M", 7, 1, -1),
              (S1, "S1", 3, 3, +1), (S2, "S2", 4, 4, +1)]
    for (pos, lab, a, sc, side) in scored:
        best = (sc == 4)
        p.append(node(pos[0], pos[1], lab, r=26,
                      fill=BLUE_FILL if best else FILL,
                      stroke=NEG if best else INK,
                      sw=3 if best else 2))
        p.append(text(pos[0], pos[1] + side * 46, "a=%d · бал %d" % (a, sc), size=12,
                      color=NEG if best else MUTED))

    p.append(fitbox(60, 402, 820, 74,
                    "N = 8 кандидатів (усе, що досяжне з поганого й недосяжне з доброго)\n"
                    "a(X) — скільки кандидатів досяжні з X разом із ним;  бал = min(a, N − a);  "
                    "тестуємо максимальний — тут його дають двоє: C4 і S2",
                    size=14, pad=12, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, "bisect-dag.svg"), W, H, *p,
           title="Пошук регресії: у графі немає середини, є найкраще половинення")


# ── 4. Вставка proj: наївна сума ваг бреше на злитті ────────────────────────
def fig_naive_sum():
    W, H = 960, 480
    p = []

    def edge(a, b, color=MUTED, sw=1.8, r=28):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        d = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / d, dy / d
        return arrow(x1 + ux * r, y1 + uy * r, x2 - ux * (r + 6), y2 - uy * (r + 6), color=color, sw=sw)

    A = (110, 250)
    B = (250, 250)
    L = (410, 158)
    R = (410, 342)
    M = (560, 250)

    for a, b in [(B, A), (L, B), (R, B), (M, L), (M, R)]:
        p.append(edge(a, b))

    p.append(node(*A, "A", r=28, fill=RED_FILL, stroke=POS, sw=2.5))
    p.append(node(*B, "B", r=28, fill=RED_FILL, stroke=POS, sw=2.5))
    p.append(node(*L, "L", r=28))
    p.append(node(*R, "R", r=28))
    p.append(node(*M, "M", r=28, fill=BLUE_FILL, stroke=NEG, sw=3))

    p.append(text(A[0], A[1] + 52, "a = 1", size=13, color=MUTED))
    p.append(text(B[0], B[1] + 52, "a = 2", size=13, color=MUTED))
    p.append(text(L[0], L[1] - 46, "a = 3", size=13, color=MUTED))
    p.append(text(R[0], R[1] + 52, "a = 3", size=13, color=MUTED))
    p.append(text(M[0], M[1] + 52, "a = 5", size=13, color=NEG, bold=True))

    p.append(text(180, 400, "A і B досяжні і через L, і через R", size=13, color=POS))
    p.append(text(180, 422, "— спільна частина двох гілок", size=13, color=POS))

    p.append(fitbox(660, 96, 268, 130,
                    "наївно\n"
                    "a(M) = 1 + a(L) + a(R)\n"
                    "     = 1 + 3 + 3 = 7\n"
                    "7 > N = 5  ✗",
                    size=15, pad=12, fill=RED_FILL, stroke=POS, sw=1.8, bold=True))
    p.append(fitbox(660, 254, 268, 130,
                    "насправді\n"
                    "a(M) = |{A,B,L,R,M}|\n"
                    "     = 5\n"
                    "бал = min(5, 0) = 0",
                    size=15, pad=12, fill=BLUE_FILL, stroke=NEG, sw=1.8, bold=True))

    p.append(fitbox(60, 40, 868, 42,
                    "N = 5 кандидатів;  a(X) — скільки з них досяжні з X разом із ним самим",
                    size=15, pad=10, fill=BG, stroke=MUTED, sw=1.2))
    p.append(fitbox(400, 400, 528, 56,
                    "різниця 7 − 5 = 2 — це рівно |{A, B}|,\n"
                    "перетин двох гілок, полічений двічі",
                    size=14, pad=10, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, "bisect-naive-sum.svg"), W, H, *p,
           title="Чому суму ваг батьків не можна брати за вагу злиття")


# ── 5. Вставка proj: три джерела ваги + ранній вихід ────────────────────────
def fig_weight_sources():
    W, H = 980, 430
    p = []

    def edge(a, b, r=26):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        d = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / d, dy / d
        return arrow(x1 + ux * r, y1 + uy * r, x2 - ux * (r + 6), y2 - uy * (r + 6), color=MUTED, sw=1.8)

    panels = [(40, "Немає кандидатів-батьків"), (355, "Один батько"), (670, "Злиття: два батьки")]
    for x0, title_ in panels:
        p.append(rect(x0, 56, 270, 250, fill=BG, stroke=MUTED, sw=1.2))
        p.append(text(x0 + 135, 84, title_, size=14, bold=True))

    # панель 1
    p.append(node(175, 170, "X", r=26, fill=BLUE_FILL, stroke=NEG, sw=2.5))
    p.append(text(175, 232, "a(X) = 1", size=15, bold=True, color=NEG))
    p.append(text(175, 274, "ціна: O(1)", size=13, color=MUTED))

    # панель 2
    p.append(node(430, 170, "P", r=26))
    p.append(node(560, 170, "X", r=26, fill=BLUE_FILL, stroke=NEG, sw=2.5))
    p.append(edge((560, 170), (430, 170)))
    p.append(text(490, 232, "a(X) = a(P) + 1", size=15, bold=True, color=NEG))
    p.append(text(490, 274, "ціна: O(1)", size=13, color=MUTED))

    # панель 3
    p.append(node(745, 132, "P₁", r=26))
    p.append(node(745, 210, "P₂", r=26))
    p.append(node(875, 170, "X", r=26, fill=BLUE_FILL, stroke=NEG, sw=2.5))
    p.append(edge((875, 170), (745, 132)))
    p.append(edge((875, 170), (745, 210)))
    p.append(text(805, 252, "окремий обхід від X", size=14, bold=True, color=NEG))
    p.append(text(805, 280, "ціна: O(m + e)", size=13, color=MUTED))

    p.append(fitbox(40, 330, 900, 66,
                    "Ранній вихід: щойно |2·a(X) − N| ≤ 1, бал уже дорівнює максимально можливому ⌊N/2⌋ —\n"
                    "решту вершин, зокрема й недораховані злиття, рахувати не треба",
                    size=15, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    render(os.path.join(IMG, "bisect-weight-sources.svg"), W, H, *p,
           title="Звідки береться вага вершини і коли підрахунок можна обірвати")


# ── Стани «операція в польоті» і виходи з них (до вставки api-history-commands) ──
def fig_inflight():
    W, H = 1060, 660
    p = []

    EX_X, EX_W, EX_H = 560, 440, 44      # геометрія коробок-виходів
    ST_X, ST_W, ST_H = 60, 240, 56       # геометрія коробки стану

    def exit_row(cy, s, fill, stroke):
        return fitbox(EX_X, cy - EX_H / 2, EX_W, EX_H, s, size=13, pad=10,
                      fill=fill, stroke=stroke, sw=1.6)

    def state_box(cy, s):
        return fitbox(ST_X, cy - ST_H / 2, ST_W, ST_H, s, size=14, pad=10,
                      fill=RED_FILL, stroke=POS, sw=2, bold=True)

    def wire(cy_from, cy_to):
        return arrow(ST_X + ST_W + 8, cy_from, EX_X - 10, cy_to, color=MUTED, sw=1.8)

    # ── смуга 1: злиття ─────────────────────────────────────────────────────
    p.append(text(45, 66, "Конфлікт злиття: у теці .git з'явився MERGE_HEAD",
                  size=15, bold=True, anchor="start"))
    p.append(state_box(168, "git merge\nзупинився на конфлікті"))
    for cy, s, fill, stroke in [
        (110, "--continue → коміт-злиття з двома батьками", GREEN_FILL, FIELD),
        (168, "--abort → стан рівно такий, як до злиття", BLUE_FILL, NEG),
        (226, "--quit → маркер знято, зроблене лишається", GRAY_FILL, MUTED),
    ]:
        p.append(wire(168, cy))
        p.append(exit_row(cy, s, fill, stroke))

    p.append(line(40, 272, 1020, 272, color=MUTED, sw=1.2, dash="7,6"))

    # ── смуга 2: перебазування ──────────────────────────────────────────────
    p.append(text(45, 310, "Перебазування в польоті: тека .git/rebase-merge/",
                  size=15, bold=True, anchor="start"))
    p.append(state_box(439, "git rebase\nспіткнувся на коміті"))
    for cy, s, fill, stroke in [
        (352, "--continue → накласти коміт і йти далі за планом", GREEN_FILL, FIELD),
        (410, "--skip → поточний коміт викинуто зовсім", RED_FILL, POS),
        (468, "--abort → гілка туди, де стартувала", BLUE_FILL, NEG),
        (526, "--quit → зупинка, HEAD лишається де є", GRAY_FILL, MUTED),
    ]:
        p.append(wire(439, cy))
        p.append(exit_row(cy, s, fill, stroke))

    p.append(fitbox(40, 572, 980, 64,
                    "Стан операції видно командою git status.\n"
                    "Поки маркер у теці .git не знято, коміт і перемикання гілок відмовляються працювати.",
                    size=13, pad=12, fill=BG, stroke=MUTED, sw=1.2))

    render(os.path.join(IMG, "inflight-states.svg"), W, H, *p,
           title="Операція в польоті: виходи й що кожен гарантує")


if __name__ == "__main__":
    fig_refs()
    fig_merge_rebase()
    fig_bisect()
    fig_naive_sum()
    fig_weight_sources()
    fig_inflight()
    print("ok:", os.listdir(IMG))
