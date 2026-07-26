# -*- coding: utf-8 -*-
"""Фігури для статті «Фібоначчієва купа». Запуск із теки теми: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

R = 22  # радіус вузла


def node(cx, cy, key, marked=False, fill=FILL, dim=False):
    st = POS if marked else (MUTED if dim else LINE)
    sw = 2.6 if marked else 1.6
    s = circle(cx, cy, R, fill=fill, stroke=st, sw=sw)
    s += text(cx, cy + 5.5, str(key), size=16, color=(MUTED if dim else INK), bold=True)
    if marked:
        s += text(cx + R * 0.95, cy - R * 0.72, "m", size=12, color=POS, bold=True)
    return s


def edge(x1, y1, x2, y2, color=LINE, sw=1.5, dash=None):
    # ребро від нижнього краю батька до верхнього краю дитини (по прямій)
    import math
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    return line(x1 + ux * R, y1 + uy * R, x2 - ux * R, y2 - uy * R, color=color, sw=sw, dash=dash)


# ── Фігура 1: ліс дерев з властивістю купи ──────────────────────────────────
def fig_forest():
    W, H = 940, 560
    f = []
    # корені з деревами (heap-ordered)
    roots = [150, 330, 470, 600]
    ry = 175
    # шина кореневого списку
    f.append(line(roots[0], 128, roots[-1], 128, color=NEG, sw=2))
    f.append('<polygon points="%.1f,128 %.1f,123 %.1f,133" fill="%s"/>' % (roots[0]-8, roots[0], roots[0], NEG))
    f.append('<polygon points="%.1f,128 %.1f,123 %.1f,133" fill="%s"/>' % (roots[-1]+8, roots[-1], roots[-1], NEG))
    for rx in roots:
        f.append(line(rx, 128, rx, ry - R, color=NEG, sw=1.4, dash="3,3"))
    # дуга кільця (з останнього назад у перший)
    f.append('<path d="M %d 122 Q %d 72 %d 122" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5,4"/>'
             % (roots[-1], (roots[0]+roots[-1])//2, roots[0], NEG))
    f.append(text((roots[0]+roots[-1])/2, 62, "кореневий список — кільцевий, двобічно зв'язаний", size=13, color=NEG))

    # min-вказівник
    f.append(text(66, ry + 5, "min", size=14, color=FIELD, bold=True))
    f.append(arrow(90, ry, roots[0] - R - 4, ry, color=FIELD, sw=2))

    # дерево кореня 1 (мінімум)
    f.append(edge(roots[0], ry, 110, 265)); f.append(edge(roots[0], ry, 200, 265))
    f.append(edge(110, 265, 110, 355))
    f.append(node(roots[0], ry, 1))
    f.append(node(110, 265, 4)); f.append(node(200, 265, 8))
    f.append(node(110, 355, 12))
    # дерево кореня 3
    f.append(edge(roots[1], ry, roots[1], 265))
    f.append(node(roots[1], ry, 3)); f.append(node(roots[1], 265, 6))
    # дерево кореня 7 (лист)
    f.append(node(roots[2], ry, 7))
    # дерево кореня 5, дитина 9 — помічена
    f.append(edge(roots[3], ry, roots[3], 265))
    f.append(node(roots[3], ry, 5)); f.append(node(roots[3], 265, 9, marked=True))

    # виноска: поля вузла
    f.append(fitbox(710, 150, 205, 250,
                    "Поля одного вузла:\n\nkey — ключ\ndegree — к-сть дітей\nmark — чи вже\n   втратив дитину\nparent, child\nleft, right —\n   сусіди в кільці",
                    size=14, pad=12, fill="#f0f5ff", stroke=NEG))
    # легенда позначки
    f.append(text(150, 470, "m — помічений вузол (утратив одну дитину після того, як став не-коренем)",
                  size=13, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'forest.svg'), W, H, *f,
           title="Фібоначчієва купа: ліс дерев, у кожному — властивість купи")


# ── Фігура 2: ущільнення (зв'язування дерев однакового степеня) ──────────────
def fig_consolidate():
    W, H = 940, 470
    f = []
    # Панель A: два корені степеня 1
    f.append(text(230, 78, "Два корені однакового степеня (= 1)", size=15, bold=True))
    f.append(edge(150, 120, 150, 205)); f.append(node(150, 120, 3)); f.append(node(150, 205, 10))
    f.append(edge(320, 120, 320, 205)); f.append(node(320, 120, 7)); f.append(node(320, 205, 8))
    f.append(text(150, 258, "степінь 1", size=13, color=MUTED))
    f.append(text(320, 258, "степінь 1", size=13, color=MUTED))

    # стрілка переходу
    f.append(arrow(410, 165, 510, 165, color=INK, sw=2.2))
    f.append(text(460, 150, "зв'язати", size=13, bold=True))
    f.append(text(460, 320, "менший ключ —\nстає батьком", size=12, color=FIELD))
    # (двом рядкам — mtext)
    f[-1] = mtext(460, 300, ["менший ключ", "стає батьком"], size=12, color=FIELD)

    # Панель B: одне дерево степеня 2
    f.append(text(700, 78, "Одне дерево степеня 2", size=15, bold=True))
    f.append(edge(700, 120, 640, 205)); f.append(edge(700, 120, 760, 205))
    f.append(edge(760, 205, 760, 290))
    f.append(node(700, 120, 3))
    f.append(node(640, 205, 10)); f.append(node(760, 205, 7))
    f.append(node(760, 290, 8))
    f.append(text(700, 340, "степінь 2", size=13, color=MUTED))

    # нижнє правило
    f.append(fitbox(60, 384, 820, 68,
                    "Проходимо кореневий список, розкладаючи дерева в масив за степенем.\n"
                    "Двоє одного степеня — зв'язуємо в одне; наприкінці лишається щонайбільше O(log n) коренів.",
                    size=13, pad=10, fill="#f0fbf3", stroke=FIELD))
    render(os.path.join(OUT, 'consolidate.svg'), W, H, *f,
           title="Ущільнення при вилученні мінімуму")


# ── Фігура 3: каскадний розріз при зменшенні ключа ──────────────────────────
def fig_cascade():
    W, H = 980, 560
    f = []
    # роздільник панелей
    f.append(line(490, 60, 490, 520, color=MUTED, sw=1, dash="4,5"))

    # Панель «До»
    f.append(text(245, 82, "До: decrease-key  9 → 1", size=15, bold=True))
    f.append(edge(210, 130, 210, 225))
    f.append(edge(210, 225, 140, 320)); f.append(edge(210, 225, 285, 320))
    f.append(edge(140, 320, 140, 415))
    f.append(node(210, 130, 4))
    f.append(node(210, 225, 5, marked=True))
    f.append(node(140, 320, 8, marked=True)); f.append(node(285, 320, 11))
    f.append(node(140, 415, 9))
    f.append(text(60, 420, "9→1", size=14, color=POS, bold=True, anchor="start"))
    f.append(arrow(95, 418, 140 - R - 4, 415, color=POS, sw=2))

    # Панель «Після» — кореневий список
    f.append(text(740, 82, "Після: каскад розрізів", size=15, bold=True))
    rl = [575, 675, 775, 880]
    f.append(line(rl[0], 128, rl[-1], 128, color=NEG, sw=2))
    for rx in rl:
        f.append(line(rx, 128, rx, 150 - R, color=NEG, sw=1.2, dash="3,3"))
    f.append(node(rl[0], 150, 4))
    f.append(node(rl[1], 150, 1, fill="#eaf0fd"))
    f.append(node(rl[2], 150, 8))
    f.append(edge(rl[3], 150, rl[3], 240)); f.append(node(rl[3], 150, 5)); f.append(node(rl[3], 240, 11))
    f.append(text(728, 112, "кореневий список поповнився", size=12, color=NEG))

    # пояснення каскаду
    f.append(fitbox(540, 300, 400, 175,
                    "1 порушив порядок (менший за батька) → розрізали, у корені.\n\n8 було помічене → втрата другої дитини → теж розрізали, зняли позначку.\n\n5 було помічене → теж розрізали.\n\nКорінь 4 позначок не має → каскад спинився.",
                    size=13, pad=12, fill="#fff5f4", stroke=POS))
    render(os.path.join(OUT, 'cascading-cut.svg'), W, H, *f,
           title="Зменшення ключа: розріз і каскад угору")


# ── Фігура 4: хірургія вказівників на кільцевому списку (для proj-вставки) ────
def fig_pointer_surgery():
    W, H = 960, 660
    NEW = POS  # червоним — змінені вказівники
    f = []

    def arcp(fx, fy, tx, ty, side, color=NEW, sw=1.7):
        # дуга від краю вузла (fx,fy) до краю (tx,ty), зверху ('top') чи знизу
        oy = -15 if side == 'top' else 15
        sx = fx + (14 if tx > fx else -14)
        ex = tx + (-14 if tx > fx else 14)
        sy, ey = fy + oy, ty + oy
        cx = (sx + ex) / 2
        cy = (min(sy, ey) - 34) if side == 'top' else (max(sy, ey) + 34)
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
                % (sx, sy, cx, cy, ex, ey, color, sw))

    # ── Рядок 1: list_union — вкинути x у кільце ──
    f.append(text(W / 2, 60, "Вкинути x у кільце (list_union): чотири перезчеплення зшивають два цикли в один",
                  size=14, bold=True))
    ay = 175
    ax, xx, anx = 280, 480, 680
    f.append(line(185, ay, ax - R, ay, color=MUTED, sw=1.3, dash="4,4"))
    f.append(text(168, ay + 6, "…", size=18, color=MUTED))
    f.append(line(anx + R, ay, 778, ay, color=MUTED, sw=1.3, dash="4,4"))
    f.append(text(792, ay + 6, "…", size=18, color=MUTED))
    # верхні дуги — вказівники right
    f.append(arcp(ax, ay, xx, ay, 'top'))
    f.append(arcp(xx, ay, anx, ay, 'top'))
    f.append(text((ax + xx) / 2, 102, "a->right = x", size=13, color=NEW, bold=True))
    f.append(text((xx + anx) / 2, 102, "x->right = an", size=13, color=NEW, bold=True))
    # нижні дуги — вказівники left
    f.append(arcp(xx, ay, ax, ay, 'bottom'))
    f.append(arcp(anx, ay, xx, ay, 'bottom'))
    f.append(text((ax + xx) / 2, 258, "x->left = a", size=13, color=NEW, bold=True))
    f.append(text((xx + anx) / 2, 258, "an->left = x", size=13, color=NEW, bold=True))
    f.append(node(ax, ay, "a"))
    f.append(node(xx, ay, "x", fill="#eaf0fd"))
    f.append(node(anx, ay, "an"))

    # роздільник
    f.append(line(60, 300, W - 60, 300, color=MUTED, sw=1, dash="3,6"))

    # ── Рядок 2: list_remove — вирвати x ──
    f.append(text(W / 2, 340, "Вирвати x (list_remove): місток в обхід x, тоді x замикається сам на себе",
                  size=14, bold=True))
    by = 445
    Lx, Rx = 300, 660
    f.append(line(205, by, Lx - R, by, color=MUTED, sw=1.3, dash="4,4"))
    f.append(text(188, by + 6, "…", size=18, color=MUTED))
    f.append(line(Rx + R, by, 758, by, color=MUTED, sw=1.3, dash="4,4"))
    f.append(text(772, by + 6, "…", size=18, color=MUTED))
    # місток L<->R
    f.append(arcp(Lx, by, Rx, by, 'top'))
    f.append(text((Lx + Rx) / 2, 372, "L->right = R", size=13, color=NEW, bold=True))
    f.append(arcp(Rx, by, Lx, by, 'bottom'))
    f.append(text((Lx + Rx) / 2, 528, "R->left = L", size=13, color=NEW, bold=True))
    f.append(node(Lx, by, "L"))
    f.append(node(Rx, by, "R"))
    # вирваний x нижче, приглушений, із петлею сам на себе
    ex_x, ex_y = 480, 592
    f.append(node(ex_x, ex_y, "x", dim=True))
    f.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (ex_x - 12, ex_y + R - 4, ex_x - 54, ex_y + 46, ex_x + 54, ex_y + 46, ex_x + 12, ex_y + R - 4, NEW))
    f.append(text(ex_x + 76, ex_y + 6, "x->left = x->right = x", size=13, color=NEW, bold=True, anchor="start"))

    render(os.path.join(OUT, 'pointer-surgery.svg'), W, H, *f,
           title="Хірургія вказівників на кільцевому двобічному списку")


# ── Фігура 5 (hist): родовід — таймлайн трьох куп + стенфордський вузол 1972 ──
def fig_lineage():
    W, H = 1000, 500
    f = []
    axis_y = 250
    # вісь часу
    f.append(arrow(80, axis_y, 934, axis_y, color=MUTED, sw=2))
    f.append(text(902, axis_y + 22, "час →", size=12, color=MUTED))

    milestones = [
        dict(cx=210, year="1964", name="Двійкова купа",
             a="Дж. Вільямс (J. Williams)", b="heapsort · CACM",
             bf=FILL, bs=MUTED),
        dict(cx=500, year="1978", name="Біноміальна купа",
             a="Жан Вюймен (J. Vuillemin)", b="CACM 21(4)",
             bf="#eef3fe", bs=NEG),
        dict(cx=800, year="1984", name="Фібоначчієва купа",
             a="Фредман і Тарджан", b="FOCS · JACM 1987",
             bf="#fdecea", bs=POS),
    ]
    for m in milestones:
        cx = m['cx']
        bx, by, bw, bh = cx - 125, 100, 250, 116
        f.append(rect(bx, by, bw, bh, fill=m['bf'], stroke=m['bs'], sw=1.6, rx=8))
        f.append(text(cx, 135, m['year'], size=22, color=INK, bold=True))
        f.append(text(cx, 164, m['name'], size=16, color=INK, bold=True))
        f.append(text(cx, 188, m['a'], size=12, color=MUTED))
        f.append(text(cx, 206, m['b'], size=11, color=MUTED))
        f.append(line(cx, by + bh, cx, axis_y - 11, color=m['bs'], sw=1.3, dash="3,3"))
        f.append(circle(cx, axis_y, 10, fill=m['bf'], stroke=m['bs'], sw=2.4))

    # нижня панель: стенфордський вузол 1972
    px, py, pw, ph = 90, 300, 820, 176
    f.append(rect(px, py, pw, ph, fill="#f0fbf3", stroke=FIELD, sw=1.6, rx=10))
    for cx in (500, 800):  # Вюймен і Фредман–Тарджан тягнуться до 1972-го
        f.append(line(cx, axis_y + 11, cx, py, color=MUTED, sw=1.3, dash="3,3"))
    f.append(text(500, 334, "Одна кафедра, один рік", size=17, color=INK, bold=True))
    f.append(mtext(500, 366,
                   ["Жан Вюймен, Майкл Фредман і Роберт Тарджан здобули докторат у Стенфорді 1972 року",
                    "(наукові керівники — Зогар Манна, Дональд Кнут і Роберт Флойд відповідно).",
                    "Біноміальна й фібоначчієва купи виросли з тієї самої школи."],
                   size=14, color=INK, lh=1.4))
    f.append(text(500, 456, "Мета — зменшити ключ за O(1); наслідок — Дейкстра і Прим за O(E + V·log V).",
                  size=13, color=FIELD, bold=True))
    render(os.path.join(OUT, 'lineage.svg'), W, H, *f,
           title="Родовід фібоначчієвої купи")


# ── Фігура 6: чому i-та дитина має степінь ≥ i−2 (для math-вставки) ───────────
def fig_degree_bound():
    W, H = 980, 620
    f = []
    # корінь x
    f.append(node(490, 100, "x"))
    f.append(text(538, 96, "степінь k  ⇒  k дітей", size=13, color=MUTED, anchor="start"))
    # діти
    cxs = [130, 300, 470, 640, 810]
    labels = ["y₁", "y₂", "y₃", "y₄", "y₅"]
    degs = ["deg ≥ 0", "deg ≥ 0", "deg ≥ 1", "deg ≥ 2", "deg ≥ 3"]
    sizes = ["s₀", "s₀", "s₁", "s₂", "s₃"]
    cy = 320
    for cx in cxs:
        f.append(edge(490, 100, cx, cy))
    for cx, lb, dg, sz in zip(cxs, labels, degs, sizes):
        f.append(node(cx, cy, lb))
        f.append(text(cx, cy + 52, dg, size=13, color=INK, bold=True))
        ax, bx = cx - 42, cx + 42
        ty0, ty1 = 398, 478
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="1.3"/>'
                 % (cx, ty0, ax, ty1, bx, ty1, "#eef2f7", MUTED))
        f.append(text(cx, 452, "≥ " + sz, size=14, color=INK))
    f.append(text(490, 505, "мінімальні розміри піддерев", size=12, color=MUTED))
    # нижня рамка з міркуванням і рекурентою
    f.append(fitbox(70, 524, 840, 82,
                    "Коли yᵢ приєднали до x, діти y₁…yᵢ₋₁ вже висіли на x ⇒ степінь x тоді був ≥ i−1. "
                    "Зв'язують лише рівних за степенем ⇒ deg(yᵢ) = deg(x) ≥ i−1; відтоді yᵢ втратив щонайбільше одну дитину ⇒ deg(yᵢ) ≥ i−2.\n"
                    "Тому мінімум вузлів: sₖ ≥ 1 + s₀ + s₀ + s₁ + s₂ + … + sₖ₋₂.",
                    size=13, pad=12, fill="#f0f5ff", stroke=NEG))
    render(os.path.join(OUT, 'degree-bound.svg'), W, H, *f,
           title="Чому i-та дитина має степінь ≥ i−2")


# ── Фігура 7: найменші дерева — фібоначчієві (для math-вставки) ───────────────
def fig_fib_trees():
    W, H = 1000, 500
    f = []
    y0, y1, y2 = 115, 220, 325

    def leaf(cx, cy, fill=FILL):
        return node(cx, cy, "", fill=fill)

    # ── T3 (ліворуч): корінь + діти степенів 0,0,1 ──
    r3 = 150
    f.append(edge(r3, y0, 95, y1)); f.append(edge(r3, y0, 150, y1)); f.append(edge(r3, y0, 215, y1))
    f.append(edge(215, y1, 215, y2))
    f.append(leaf(r3, y0)); f.append(leaf(95, y1)); f.append(leaf(150, y1))
    f.append(leaf(215, y1)); f.append(leaf(215, y2))
    f.append(text(150, 385, "T₃ = 5 вузлів", size=14, bold=True))
    # ⊕
    f.append(text(292, 232, "⊕", size=32, color=INK))
    # ── T2 (посередині): корінь + діти 0,0 ──
    r2 = 400
    f.append(edge(r2, y0, 365, y1)); f.append(edge(r2, y0, 435, y1))
    f.append(leaf(r2, y0, fill="#eaf0fd")); f.append(leaf(365, y1, fill="#eaf0fd"))
    f.append(leaf(435, y1, fill="#eaf0fd"))
    f.append(text(400, 300, "T₂ = 3", size=14, bold=True))
    f.append(text(400, 338, "як нова дитина", size=12, color=NEG))
    # =
    f.append(text(527, 232, "=", size=32, color=INK))
    # ── T4 (праворуч): корінь + діти 0,0,1,2 ──
    r4 = 720
    f.append(rect(776, 190, 122, 168, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=10))
    for cx in (615, 675, 735, 835):
        f.append(edge(r4, y0, cx, y1))
    f.append(edge(735, y1, 735, y2))
    f.append(edge(835, y1, 800, y2)); f.append(edge(835, y1, 870, y2))
    f.append(leaf(r4, y0))
    f.append(leaf(615, y1)); f.append(leaf(675, y1)); f.append(leaf(735, y1)); f.append(leaf(735, y2))
    f.append(leaf(835, y1, fill="#dbe6fb")); f.append(leaf(800, y2, fill="#dbe6fb")); f.append(leaf(870, y2, fill="#dbe6fb"))
    f.append(text(720, 385, "T₄ = 8 вузлів", size=14, bold=True))
    # підсумкове рівняння
    f.append(fitbox(228, 410, 544, 66,
                    "|T₄| = |T₃| + |T₂| = 5 + 3 = 8      ⟺      F₆ = F₅ + F₄\n"
                    "мінімальні дерева ростуть за Фібоначчі:  sₖ = sₖ₋₁ + sₖ₋₂",
                    size=14, pad=10, fill="#f0fbf3", stroke=FIELD))
    render(os.path.join(OUT, 'fibonacci-trees.svg'), W, H, *f,
           title="Найменші дерева — фібоначчієві: Tₖ = Tₖ₋₁ ⊕ Tₖ₋₂")


if __name__ == '__main__':
    fig_forest()
    fig_consolidate()
    fig_cascade()
    fig_pointer_surgery()
    fig_lineage()
    fig_degree_bound()
    fig_fib_trees()
    print("OK: forest.svg, consolidate.svg, cascading-cut.svg, pointer-surgery.svg, lineage.svg, "
          "degree-bound.svg, fibonacci-trees.svg")
