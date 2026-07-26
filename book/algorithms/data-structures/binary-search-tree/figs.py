# -*- coding: utf-8 -*-
"""Фігури до статті «Двійкове дерево пошуку (BST)».
Малюємо загальні (не обов'язково повні) дерева: x — за in-order-рангом,
y — за глибиною. Такий розклад сам собою відбиває порядок і не дає накладань."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GRN_F = "#eafaf0"   # заливка збереженого / наступника
GRN_S = FIELD
RED_F = "#fdecea"   # заливка вузла на видалення
BAND  = "#eef6ff"   # світла смуга піддерева


# ── Модель дерева ────────────────────────────────────────────────────────────
class TN:
    __slots__ = ("key", "left", "right")
    def __init__(self, key, left=None, right=None):
        self.key, self.left, self.right = key, left, right


def assign(root):
    """Кожному вузлу — (in-order ранг, глибина)."""
    pos, c = {}, [0]
    def walk(n, d):
        if n is None:
            return
        walk(n.left, d + 1)
        pos[n] = (c[0], d); c[0] += 1
        walk(n.right, d + 1)
    walk(root, 0)
    return pos


def nodes(root):
    out = []
    def walk(n):
        if n is None:
            return
        walk(n.left); out.append(n); walk(n.right)
    walk(root)
    return out


def poly(pts, fill, opacity=1.0):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    op = ' fill-opacity="%.2f"' % opacity if opacity < 1 else ''
    return '<polygon points="%s" fill="%s"%s/>' % (d, fill, op)


def tri(pts, fill, stroke="#9db8de", sw=1.6):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (d, fill, stroke, sw))


def draw_tree(parts, root, X0, Y0, COL, ROW, r=20, fs=15, mark=None):
    """Малює дерево: спершу ребра, потім вузли. mark: {key:(fill,stroke,tcol)}."""
    mark = mark or {}
    pos = assign(root)
    ctr = {n: (X0 + rk * COL, Y0 + d * ROW) for n, (rk, d) in pos.items()}
    # ребра
    for n in nodes(root):
        for ch in (n.left, n.right):
            if ch is not None:
                a, b = ctr[n], ctr[ch]
                parts.append(line(a[0], a[1], b[0], b[1], color="#c8ccd2", sw=1.8))
    # вузли
    for n in nodes(root):
        cx, cy = ctr[n]
        if n.key in mark:
            f, s, t = mark[n.key]
            parts.append(circle(cx, cy, r, fill=f, stroke=s, sw=2.4))
            parts.append(text(cx, cy + fs * 0.35, n.key, size=fs, color=t, bold=True))
        else:
            parts.append(circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.8))
            parts.append(text(cx, cy + fs * 0.35, n.key, size=fs, color=INK, bold=True))
    return ctr


# Демо-дерево статті: 50(30(20,40(35,45)),70(60,80))
def demo_tree():
    return TN(50,
              TN(30, TN(20), TN(40, TN(35), TN(45))),
              TN(70, TN(60), TN(80)))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — інваріант на цілому піддереві
# ─────────────────────────────────────────────────────────────────────────────
def fig_invariant():
    W, H = 820, 470
    X0, Y0, COL, ROW, r = 92, 96, 76, 84, 21
    p = []
    root = demo_tree()
    pos = assign(root)
    ctr = {n: (X0 + rk * COL, Y0 + d * ROW) for n, (rk, d) in pos.items()}
    # смуги-піддерева (позаду вузлів): ліве < 50, праве > 50
    L = [n for n in nodes(root) if n.key in (20, 30, 35, 40, 45)]
    R = [n for n in nodes(root) if n.key in (60, 70, 80)]
    def band(sub, apex_key):
        xs = [ctr[n][0] for n in sub]
        ax, ay = ctr[[n for n in sub if n.key == apex_key][0]]
        base_y = Y0 + 3 * ROW + r + 6
        return poly([(ax, ay - r - 4), (min(xs) - r - 6, base_y),
                     (max(xs) + r + 6, base_y)], BAND)
    p.append(band(L, 30))
    p.append(band(R, 70))
    draw_tree(p, root, X0, Y0, COL, ROW, r=r,
              mark={50: (GRN_F, GRN_S, INK)})
    # підписи під смугами (з запасом, у чистій зоні)
    ly = Y0 + 3 * ROW + r + 34
    lx = (ctr[[n for n in L if n.key == 20][0]][0] + ctr[[n for n in L if n.key == 45][0]][0]) / 2
    rx = (ctr[[n for n in R if n.key == 60][0]][0] + ctr[[n for n in R if n.key == 80][0]][0]) / 2
    p.append(text(lx, ly, "усі ключі < 50", size=15, color=NEG, bold=True))
    p.append(text(rx, ly, "усі ключі > 50", size=15, color=POS, bold=True))
    render(os.path.join(OUT, "invariant.svg"), W, H, *p,
           title="Інваріант BST діє на ціле піддерево")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — пошук: спуск одним шляхом
# ─────────────────────────────────────────────────────────────────────────────
def fig_search():
    W, H = 820, 560
    X0, Y0, COL, ROW, r = 92, 96, 76, 84, 21
    p = []
    root = demo_tree()
    pos = assign(root)
    ctr = {n: (X0 + rk * COL, Y0 + d * ROW) for n, (rk, d) in pos.items()}
    path = [50, 30, 40, 45]
    # підсвітити ребра шляху
    def cen(k): return ctr[[n for n in nodes(root) if n.key == k][0]]
    for a, b in zip(path, path[1:]):
        xa, ya = cen(a); xb, yb = cen(b)
        p.append(line(xa, ya, xb, yb, color=GRN_S, sw=3.4))
    mark = {k: (GRN_F, GRN_S, INK) for k in path}
    mark[45] = (GRN_F, GRN_S, FIELD)
    draw_tree(p, root, X0, Y0, COL, ROW, r=r, mark=mark)
    # кроки порівняння — окремим списком під деревом (без перетину з деревом)
    steps = [(50, "50:  45 < 50  →  ліворуч"),
             (30, "30:  45 > 30  →  праворуч"),
             (40, "40:  45 > 40  →  праворуч"),
             (45, "45:  45 = 45  →  знайдено ✓")]
    ly0 = Y0 + 3 * ROW + r + 56
    for i, (k, s) in enumerate(steps):
        col = FIELD if k == 45 else MUTED
        p.append(text(X0, ly0 + i * 30, s, size=15, color=col,
                      anchor="start", bold=(k == 45)))
    render(os.path.join(OUT, "search.svg"), W, H, *p,
           title="Пошук 45: спуск одним шляхом")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — видалення вузла з двома дітьми через наступника
# ─────────────────────────────────────────────────────────────────────────────
def fig_delete():
    W, H = 860, 430
    ROW, COL, r = 86, 62, 20
    p = []
    # ДО: 30(20, 40(35,45)) — видаляємо 30, наступник 35
    before = TN(30, TN(20), TN(40, TN(35), TN(45)))
    draw_tree(p, before, 70, 110, COL, ROW, r=r,
              mark={30: (RED_F, POS, POS), 35: (GRN_F, GRN_S, FIELD)})
    p.append(text(70 + 2 * COL, 92, "до", size=15, color=MUTED, bold=True))
    p.append(text(70 + 2 * COL, 360, "30 має двох дітей;", size=13.5, color=MUTED))
    p.append(text(70 + 2 * COL, 380, "наступник 35 — найлівіший справа", size=13.5, color=MUTED))
    # стрілка-перехід
    p.append(arrow(384, 200, 470, 200, color=INK, sw=2.2))
    p.append(text(427, 184, "35 на місце 30", size=13.5, color=INK, bold=True))
    # ПІСЛЯ: 35(20, 40(_,45))
    after = TN(35, TN(20), TN(40, None, TN(45)))
    draw_tree(p, after, 560, 110, COL, ROW, r=r,
              mark={35: (GRN_F, GRN_S, FIELD)})
    p.append(text(560 + 2 * COL, 92, "після", size=15, color=MUTED, bold=True))
    p.append(text(560 + 2 * COL, 360, "порядок цілий,", size=13.5, color=MUTED))
    p.append(text(560 + 2 * COL, 380, "колишній лист 35 зник", size=13.5, color=MUTED))
    render(os.path.join(OUT, "delete-successor.svg"), W, H, *p,
           title="Видалення вузла з двома дітьми")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — збалансоване проти виродженого
# ─────────────────────────────────────────────────────────────────────────────
def fig_balanced():
    W, H = 860, 470
    r = 20
    p = []
    # ліворуч: збалансоване 30(20(10,_),40(_,50))
    bal = TN(30, TN(20, TN(10), None), TN(40, None, TN(50)))
    draw_tree(p, bal, 70, 108, 62, 84, r=r, mark={30: (GRN_F, GRN_S, INK)})
    p.append(text(70 + 2 * 62, 84, "гілкувате", size=15, color=FIELD, bold=True))
    p.append(text(70 + 2 * 62, 420, "h ≈ log₂ n", size=15, color=FIELD, bold=True))
    p.append(text(70 + 2 * 62, 442, "усі операції O(log n)", size=13, color=MUTED))
    # роздільник
    p.append(line(430, 90, 430, 400, color="#d0d4da", sw=1.4, dash="5,5"))
    # праворуч: вироджене 10-20-30-40-50 (усе праворуч)
    vine = TN(10, None, TN(20, None, TN(30, None, TN(40, None, TN(50)))))
    draw_tree(p, vine, 520, 108, 58, 66, r=r, mark={10: (RED_F, POS, POS)})
    p.append(text(600, 84, "вироджене (вставка за зростанням)", size=15, color=POS, bold=True))
    p.append(text(690, 442, "h = n  →  пошук O(n), знову список", size=13, color=MUTED))
    render(os.path.join(OUT, "balanced-vs-degenerate.svg"), W, H, *p,
           title="Ті самі ключі — дві форми")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 5 — обертання зберігає порядок, зменшує висоту
# ─────────────────────────────────────────────────────────────────────────────
def fig_rotation():
    W, H = 760, 380
    r = 22
    p = []
    # ДО: правий ланцюг 1->2->3
    before = TN(1, None, TN(2, None, TN(3)))
    draw_tree(p, before, 80, 96, 66, 80, r=r)
    p.append(text(80 + COL_MID(2), 300, "in-order: 1, 2, 3", size=14, color=MUTED))
    p.append(text(80 + COL_MID(2), 322, "h = 3", size=14, color=POS, bold=True))
    # стрілка
    p.append(arrow(360, 175, 450, 175, color=INK, sw=2.4))
    p.append(text(405, 158, "ліве обертання", size=14, color=INK, bold=True))
    # ПІСЛЯ: 2(1,3)
    after = TN(2, TN(1), TN(3))
    draw_tree(p, after, 500, 120, 66, 80, r=r, mark={2: (GRN_F, GRN_S, INK)})
    p.append(text(500 + 66, 300, "in-order: 1, 2, 3", size=14, color=MUTED))
    p.append(text(500 + 66, 322, "h = 2", size=14, color=FIELD, bold=True))
    render(os.path.join(OUT, "rotation.svg"), W, H, *p,
           title="Обертання: порядок той самий, висота менша")


def COL_MID(rank):
    return rank * 66


# ─────────────────────────────────────────────────────────────────────────────
# Фігури до історичної вставки «hist-bst-birth»
# ─────────────────────────────────────────────────────────────────────────────
def polyline(pts, color, sw=3.0, dash=None):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, color, sw, da))


# Фіг. H1 — тридцятирічна хронологія: народження ідеї → вирок про видалення
def fig_history_timeline():
    W, H = 1120, 470
    axis_y = 236
    x0, x1 = 70, 1050
    p = []
    events = [
        ("1959",    "Дуглас\nперший натяк",                                 FIELD),
        ("1960",    "Віндлі · Бут+Колін\nБернерс-Лі+Вілер\n(троє незалежно)", FIELD),
        ("1962",    "Гіббард\nвидалення + теорема",                          FIELD),
        ("1975",    "Нотт\nпролом у доказі",                                 POS),
        ("1978",    "Йонассен+Кнут\nнавіть 3 ключі — жах",                   POS),
        ("1983",    "Епінґер\nасиметрія псує дерево",                        POS),
        ("1989–90", "Калбертсон+Манро\nсередня глибина Θ(√n)",              POS),
    ]
    n = len(events)
    span = x1 - x0
    xs = [x0 + span * (i + 0.5) / n for i in range(n)]
    split = (xs[2] + xs[3]) / 2
    # вісь + дві ери
    p.append(line(x0, axis_y, x1, axis_y, color="#c8ccd2", sw=3))
    p.append(line(x0, axis_y, split, axis_y, color=FIELD, sw=5))
    p.append(line(split, axis_y, x1, axis_y, color=POS, sw=5))
    p.append(text((x0 + split) / 2, axis_y - 100, "НАРОДЖЕННЯ ІДЕЇ",
                  size=14, color=FIELD, bold=True))
    p.append(text((split + x1) / 2, axis_y + 112,
                  "ТРИДЦЯТИРІЧНА ПОМИЛКА У ВИДАЛЕННІ", size=14, color=POS, bold=True))
    size = 13
    for i, (yr, lbl, col) in enumerate(events):
        cx = xs[i]
        above = (i % 2 == 0)
        p.append(circle(cx, axis_y, 6, fill=BG, stroke=col, sw=2.6))
        # рік — з протилежного від картки боку осі
        yy = axis_y + 22 if above else axis_y - 14
        p.append(text(cx, yy, yr, size=14, color=col, bold=True))
        lines_ = lbl.split("\n")
        h_est = len(lines_) * size * 1.3 + 20 - size * 0.3
        gap = 32
        cy = axis_y - gap - h_est / 2 if above else axis_y + gap + h_est / 2
        edge = cy + h_est / 2 if above else cy - h_est / 2
        p.append(line(cx, axis_y, cx, edge, color=col, sw=1.6))
        body, w, hh = textbox(cx, cy, lbl, size=size, pad=10,
                              fill=FILL, stroke=col, sw=1.6, color=INK)
        p.append(body)
    render(os.path.join(OUT, "history-timeline.svg"), W, H, *p,
           title="Тридцять років від ідеї до вироку про видалення")


# Фіг. H2 — куди заводить асиметричне видалення: √n замість log n
def fig_growth_sqrt():
    import math
    W, H = 1000, 440
    L, R, T, B = 100, 920, 80, 356
    NMAX, YMAX = 4096, 68
    p = []
    def X(v): return L + (v / NMAX) * (R - L)
    def Y(v): return B - (v / YMAX) * (B - T)
    # осі
    p.append(line(L, T, L, B, color=INK, sw=1.8))
    p.append(line(L, B, R, B, color=INK, sw=1.8))
    for v in (12, 32, 64):
        yy = Y(v)
        p.append(line(L, yy, R, yy, color="#e9ecf1", sw=1))
        p.append(text(L - 10, yy + 4, str(v), size=12, color=MUTED, anchor="end"))
    for nn in (1024, 2048, 3072, 4096):
        xx = X(nn)
        p.append(line(xx, B, xx, B + 5, color=INK, sw=1.4))
        p.append(text(xx, B + 21, str(nn), size=12, color=MUTED))
    # криві
    sqrt_pts = [(X(nn), Y(math.sqrt(nn))) for nn in range(0, NMAX + 1, 32)]
    log_pts  = [(X(nn), Y(math.log2(nn) if nn >= 1 else 0)) for nn in range(0, NMAX + 1, 32)]
    p.append(polyline(log_pts, FIELD, sw=3.2))
    p.append(polyline(sqrt_pts, POS, sw=3.2))
    # підписи кривих — у чистих зонах між кривими / під логарифмом
    p.append(mtext(600, 198, ["√n — після багатьох", "асиметричних видалень"],
                   size=13, color=POS, bold=True))
    p.append(text(560, 338, "log₂n — випадкове / збалансоване",
                  size=13, color=FIELD))
    # заголовки осей
    p.append(text((L + R) / 2, B + 42, "n — кількість ключів у дереві", size=13, color=INK))
    p.append(text(L - 12, T - 18, "середня глибина вузла (порівнянь на пошук)",
                  size=12.5, color=INK, anchor="start"))
    # виноска-магнітуда у порожньому верхньому лівому куті
    body, w, hh = textbox(
        328, 126,
        "при n = 1 000 000\nзбалансоване:  log₂n ≈ 20\nасиметричне:   √n = 1000  (у ~50× гірше)",
        size=13, pad=12, fill="#fdf2f0", stroke=POS, sw=1.4, color=INK)
    p.append(body)
    render(os.path.join(OUT, "growth-sqrt.svg"), W, H, *p,
           title="Куди заводить асиметричне видалення: √n замість log n")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. P1 (proj) — те саме дерево: абстракція проти пам'яті (записи + вказівники)
# ─────────────────────────────────────────────────────────────────────────────
def _record(x, y, key, lnull, rnull):
    """Запис вузла: три комірки [key|left|right]. Повертає (parts, Lцентр, Rцентр)."""
    W_, H_, k, c = 108, 30, 40, 34
    parts = [rect(x, y, W_, H_, fill=FILL, stroke=LINE, sw=1.6, rx=4),
             line(x + k, y, x + k, y + H_, color=LINE, sw=1.1),
             line(x + k + c, y, x + k + c, y + H_, color=LINE, sw=1.1),
             text(x + k / 2, y + H_ / 2 + 5, key, size=15, color=INK, bold=True)]
    lx, rx, yc = x + k + c / 2, x + k + c + c / 2, y + H_ / 2
    parts.append(text(lx, yc + 5, "∅", size=13, color=MUTED) if lnull
                 else circle(lx, yc, 3.4, fill=INK, stroke=INK))
    parts.append(text(rx, yc + 5, "∅", size=13, color=MUTED) if rnull
                 else circle(rx, yc, 3.4, fill=INK, stroke=INK))
    return parts, (lx, yc), (rx, yc)


def fig_memory():
    W, H = 880, 430
    p = []
    # ── ліворуч: абстрактне дерево 50(30(_,40),70) ──
    tree = TN(50, TN(30, None, TN(40)), TN(70))
    draw_tree(p, tree, 70, 132, 48, 92, r=18, mark={50: (GRN_F, GRN_S, INK)})
    p.append(text(140, 108, "абстрактно", size=14, color=MUTED, bold=True))
    p.append(line(360, 92, 360, 372, color="#d0d4da", sw=1.4, dash="5,5"))
    # ── праворуч: записи в купі ──
    for cx, s in ((540, "key"), (577, "left"), (611, "right")):
        p.append(text(cx, 72, s, size=9, color=MUTED))
    p.append(text(514, 97, "root →", size=12, color=MUTED, anchor="end", bold=True))
    a50, l50, r50c = _record(520, 78,  50, lnull=False, rnull=False)
    a30, l30, r30c = _record(444, 182, 30, lnull=True,  rnull=False)
    a70, l70, r70c = _record(700, 182, 70, lnull=True,  rnull=True)
    a40, l40, r40c = _record(474, 292, 40, lnull=True,  rnull=True)
    for a in (a50, a30, a70, a40):
        p.extend(a)
    # стрілки-вказівники до верхів записів-цілей (top-center = x+54)
    p.append(arrow(l50[0],  l50[1] + 3,  498, 182, color=INK, sw=1.6))
    p.append(arrow(r50c[0], r50c[1] + 3, 754, 182, color=INK, sw=1.6))
    p.append(arrow(r30c[0], r30c[1] + 3, 528, 292, color=INK, sw=1.6))
    render(os.path.join(OUT, "memory-layout.svg"), W, H, *p,
           title="Те саме дерево: картинка і пам'ять")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. P2 (proj) — ітеративна вставка вказівником-на-вказівник (Node** p)
# ─────────────────────────────────────────────────────────────────────────────
def fig_iter_insert():
    W, H = 880, 420
    p = []
    tree = TN(50, TN(30), TN(70, TN(60), TN(80)))
    X0, Y0, COL, ROW, r = 64, 104, 50, 86, 18
    pos = assign(tree)
    ctr = {n: (X0 + rk * COL, Y0 + d * ROW) for n, (rk, d) in pos.items()}

    def cen(key):
        return ctr[[n for n in nodes(tree) if n.key == key][0]]
    # підсвітити спуск 50→70→60 (товсті зелені під сірими ребрами)
    for a, b in ((50, 70), (70, 60)):
        xa, ya = cen(a); xb, yb = cen(b)
        p.append(line(xa, ya, xb, yb, color=GRN_S, sw=3.6))
    draw_tree(p, tree, X0, Y0, COL, ROW, r=r,
              mark={50: (GRN_F, GRN_S, INK), 70: (GRN_F, GRN_S, INK),
                    60: (GRN_F, GRN_S, INK)})
    # новий листок 65 правим сином 60
    x60, y60 = cen(60)
    nx, ny = x60 + 40, y60 + ROW - 18
    p.append(line(x60, y60, nx, ny, color=GRN_S, sw=2.6))
    p.append(circle(nx, ny, r, fill=GRN_F, stroke=GRN_S, sw=2.4))
    p.append(text(nx, ny + 6, "65", size=15, color=FIELD, bold=True))
    p.append(text(nx, ny + r + 22, "*p = new Node(65)", size=12.5,
                  color=FIELD, bold=True))
    # ── панель кроків праворуч ──
    px, py, pw, ph = 470, 112, 384, 214
    p.append(rect(px, py, pw, ph, fill="#f7f9fc", stroke="#d9dee6", sw=1.4, rx=8))
    p.append(text(px + pw / 2, py + 30, "ітеративний спуск: Node** p",
                  size=13.5, color=INK, bold=True))
    rows = [("p = &root",       "→  50", MUTED, False),
            ("p = &(50→right)", "→  70", MUTED, False),
            ("p = &(70→left)",  "→  60", MUTED, False),
            ("p = &(60→right)", "→  ∅",  FIELD, True)]
    ry = py + 66
    for lft, rgt, col, bold in rows:
        p.append(text(px + 32, ry, lft, size=13, color=INK, anchor="start"))
        p.append(text(px + 232, ry, rgt, size=13, color=col, anchor="start", bold=bold))
        ry += 30
    p.append(text(px + 32, ry + 6, "*p = new Node(65)", size=13,
                  color=FIELD, anchor="start", bold=True))
    render(os.path.join(OUT, "iter-insert.svg"), W, H, *p,
           title="Вставка вказівником-на-вказівник")


# ─────────────────────────────────────────────────────────────────────────────
# Фігури до математичної вставки «math-bst-height»
# ─────────────────────────────────────────────────────────────────────────────

# Фіг. M1 — три висоти як функції n: лінійний найгірший проти логарифмічного
def fig_height_growth():
    import math
    W, H = 820, 480
    L, R, T, B = 95, 735, 80, 380         # рамка графіка
    NMAX, YMAX = 100.0, 100.0
    def mx(v): return L + (v / NMAX) * (R - L)
    def my(v): return B - (v / YMAX) * (B - T)
    p = []
    # сітка
    for t in (0, 20, 40, 60, 80, 100):
        p.append(line(mx(t), B, mx(t), T, color="#eef1f4", sw=1))
        p.append(line(L, my(t), R, my(t), color="#eef1f4", sw=1))
        p.append(text(mx(t), B + 18, "%d" % t, size=12, color=MUTED))
        if t > 0:
            p.append(text(L - 10, my(t) + 4, "%d" % t, size=12, color=MUTED, anchor="end"))
    # осі поверх сітки
    p.append(line(L, T, L, B, color=INK, sw=1.8))
    p.append(line(L, B, R, B, color=INK, sw=1.8))
    p.append(text(R, B + 36, "n — кількість ключів", size=13, color=INK, anchor="end"))
    p.append(text(L - 34, T - 16, "висота / глибина", size=13, color=INK, anchor="start"))
    # криві
    def curve(f):
        return [(mx(n), my(min(f(n), YMAX))) for n in range(1, 101)]
    worst = [(mx(n), my(n)) for n in range(1, 101)]
    expc = curve(lambda n: 4.311 * math.log(n))
    avgc = curve(lambda n: 2.0 * math.log(n))
    flr = curve(lambda n: math.log(n, 2))
    p.append(polyline(worst, POS, sw=3.0))
    p.append(polyline(expc, INK, sw=2.6))
    p.append(polyline(avgc, FIELD, sw=2.6))
    p.append(polyline(flr, MUTED, sw=2.2, dash="6,5"))
    # мітка просто на діагоналі
    p.append(text(mx(66) + 8, my(66) - 8, "h = n", size=15, color=POS, bold=True, anchor="start"))
    # легенда — у порожньому трикутнику над діагоналлю (верх-ліворуч)
    lx, ly = 122, 106
    rows = [(POS, 3.0, None, "найгірший випадок:  h = n"),
            (INK, 2.6, None, "сподівана висота  ≈ 4.31·ln n"),
            (FIELD, 2.6, None, "середня глибина  ≈ 2·ln n ≈ 1.39·log₂n"),
            (MUTED, 2.2, "6,5", "межа балансу  ≈ log₂ n")]
    p.append(rect(lx - 16, ly - 24, 372, 24 * len(rows) + 16, fill="#ffffff",
                  stroke="#d6dae0", sw=1.2, rx=8))
    for i, (c, sw, dash, lab) in enumerate(rows):
        yy = ly + i * 24
        p.append(line(lx, yy, lx + 34, yy, color=c, sw=sw, dash=dash))
        p.append(text(lx + 46, yy + 4, lab, size=13.5, color=INK, anchor="start"))
    # нижній підпис-приклад
    p.append(text((L + R) / 2, 454,
                  "n = 100:   найгірший 100   ·   сподівана ≈ 20   ·   середня ≈ 9   ·   межа ≈ 7",
                  size=13.5, color=MUTED))
    render(os.path.join(OUT, "height-growth.svg"), W, H, *p,
           title="Висота BST: лінійний найгірший випадок проти логарифмічного середнього")


# Фіг. M2 — розклад внутрішньої довжини шляху за коренем (двигун рекурентності)
def fig_pathlen_recurrence():
    W, H = 820, 430
    p = []
    rx, ry = 410, 104
    # ребра до піддерев
    p.append(line(rx, ry, 300, 150, color="#c8ccd2", sw=2))
    p.append(line(rx, ry, 520, 150, color="#c8ccd2", sw=2))
    # трикутники-піддерева
    p.append(tri([(300, 150), (150, 320), (395, 320)], BAND))
    p.append(tri([(520, 150), (445, 320), (690, 320)], BAND))
    p.append(mtext(282, 246, ["ліве піддерево", "i − 1 менших ключів",
                              "(теж випадковий BST)"], size=14, color=INK))
    p.append(mtext(552, 246, ["праве піддерево", "n − i більших ключів",
                              "(теж випадковий BST)"], size=14, color=INK))
    # корінь-вузол поверх
    p.append(circle(rx, ry, 24, fill=GRN_F, stroke=GRN_S, sw=2.6))
    p.append(text(rx, ry + 6, "i", size=17, color=INK, bold=True, italic=True))
    p.append(text(rx, 50, "корінь = ключ рангу i", size=14, color=INK, bold=True))
    p.append(text(rx, 68, "(перший вставлений; ранг i рівноймовірний, 1/n)",
                  size=12, color=MUTED))
    # формула-рекурентність
    body, w, hh = textbox(410, 362, "I(n)  =  (n − 1)  +  I(i − 1)  +  I(n − i)",
                          size=16, pad=12, bold=True, fill="#f4f8ff", stroke="#9db8de")
    p.append(body)
    p.append(text(410, 402,
                  "+(n − 1): кожен із n − 1 не-кореневих вузлів на одне ребро глибший через корінь",
                  size=12.5, color=MUTED))
    render(os.path.join(OUT, "pathlen-recurrence.svg"), W, H, *p,
           title="Розклад внутрішньої довжини шляху за коренем")


if __name__ == "__main__":
    fig_invariant()
    fig_search()
    fig_delete()
    fig_balanced()
    fig_rotation()
    fig_history_timeline()
    fig_growth_sqrt()
    fig_memory()
    fig_iter_insert()
    fig_height_growth()
    fig_pathlen_recurrence()
    print("BST figures written to", OUT)
