# -*- coding: utf-8 -*-
"""Фігури до теми «Ентропія Шеннона» (shannon-entropy).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Інформація однієї події: I = log2(1/p) ─────────────────────────────────
# Ідея: передбачуване майже не коштує бітів, рідкісне коштує багато; p=½ → 1 біт.
def fig_surprise():
    W, H = 720, 400
    ox, oy = 100, 330
    aw, ah = 545, 250
    f = []
    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    f.append(text(ox + aw + 16, oy + 22, "ймовірність p", 11, INK, "end", bold=True))
    f.append(line(ox, oy + 4, ox, oy - ah - 4, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox - 8, oy - ah - 8, "інформація I, біт", 11, INK, "end", bold=True))

    y_max = 7.0
    def px(p): return ox + p * aw
    def py(v): return oy - (v / y_max) * ah

    for p, lab in [(0.0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1")]:
        f.append(line(px(p), oy, px(p), oy + 5, color=INK, sw=1.2))
        f.append(text(px(p), oy + 20, lab, 10, MUTED, "middle"))
    for v in range(0, 8):
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, str(v), 10, MUTED, "end"))
        if v:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # крива I = log2(1/p)
    pts = []
    p = 0.01
    while p <= 1.0001:
        pp = min(p, 1.0)
        pts.append("%.1f,%.1f" % (px(pp), py(min(math.log2(1.0 / pp), y_max))))
        p += 0.004
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # опорні точки
    marks = [(0.1, 3.32, "p=0.1 → 3.3 біта", "start", 12, -10),
             (0.5, 1.0, "p=½ → 1 біт", "start", 12, -10),
             (1.0, 0.0, "p=1 → 0", "end", -10, -12)]
    for p, v, lab, anc, dx, dy in marks:
        f.append(circle(px(p), py(v), 4.4, fill=POS, stroke=POS, sw=0))
        f.append(text(px(p) + dx, py(v) + dy, lab, 10.5, POS, anc, bold=True))

    f.append(text(px(0.17), py(6.3), "рідкісне → багато бітів", 11.5, MUTED, "start"))
    f.append(text(px(0.62), py(2.2), "передбачуване → майже 0 біт", 11.5, MUTED, "middle"))
    render(os.path.join(IMG, "surprise.svg"), W, H, *f,
           title="Інформація = несподіванка: I = log₂(1/p)")


# ── 2. Ентропія як зважене середнє несподіванки (worked, 4 символи) ───────────
# Ідея: часте коштує мало, рідкісне багато; внесок = частота·ціна; сума = H=1.75.
def fig_entropy_formula():
    W, H = 780, 430
    f = []
    base = 322
    scale = 205.0
    x0, bw, gap = 90, 62, 36
    syms = [("A", "½", "1 біт", 0.5), ("B", "¼", "2 біти", 0.5),
            ("C", "⅛", "3 біти", 0.375), ("D", "⅛", "3 біти", 0.375)]
    f.append(line(x0 - 12, base, x0 + 4 * (bw + gap) - gap + 12, base, color=INK, sw=1.4))
    for i, (s, pf, cost, contrib) in enumerate(syms):
        x = x0 + i * (bw + gap)
        h = contrib * scale
        f.append(rect(x, base - h, bw, h, fill="#eaf0fd", stroke=NEG, sw=1.8))
        f.append(text(x + bw / 2, base - h - 10, "внесок %.3g" % contrib, 10.5, NEG, "middle", bold=True))
        f.append(text(x + bw / 2, base + 22, s, 15, INK, "middle", bold=True))
        f.append(text(x + bw / 2, base + 40, "p = " + pf, 11, MUTED, "middle"))
        f.append(text(x + bw / 2, base + 56, "ціна " + cost, 10, MUTED, "middle"))
    f.append(text((x0 + 4 * (bw + gap) - gap) / 2 + 20, base + 82,
                  "канал команд шле один із чотирьох символів", 10.5, MUTED, "middle"))

    # праворуч — сама сума
    f.append(rect(468, 118, 268, 150, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(mtext(602, 150,
                   ["H = ½·1 + ¼·2 + ⅛·3 + ⅛·3",
                    "  = 0.5 + 0.5 + 0.375 + 0.375",
                    "  = 1.75 біта / символ"], 12, INK))
    f.append(line(484, 232, 720, 232, color="#cfd6dd", sw=1.2))
    f.append(text(602, 254, "наївно — 2 біти на 4 стани", 11, MUTED, "middle"))
    render(os.path.join(IMG, "entropy-formula.svg"), W, H, *f,
           title="Ентропія — зважене середнє несподіванки")


# ── 3. Межі ентропії двох наслідків: 1 біт при рівних, 0 на певному ───────────
# Ідея: максимум непередбачуваності — рівні шанси; передбачуване джерело → 0.
def fig_entropy_range():
    W, H = 720, 420
    ox, oy = 100, 345
    aw, ah = 545, 262
    f = []
    def Hb(p):
        if p <= 0 or p >= 1: return 0.0
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    y_max = 1.09
    def px(p): return ox + p * aw
    def py(v): return oy - (v / y_max) * ah

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=INK, sw=1.6))
    f.append(arrow(ox + aw, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    f.append(text(ox + aw + 16, oy + 22, "частка наслідку p", 11, INK, "end", bold=True))
    f.append(line(ox, oy + 4, ox, oy - ah - 4, color=INK, sw=1.6))
    f.append(arrow(ox, oy - ah, ox, oy - ah - 20, color=INK, sw=1.6))
    f.append(text(ox - 8, oy - ah - 8, "ентропія H, біт", 11, INK, "end", bold=True))

    for p, lab in [(0.0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "1")]:
        f.append(line(px(p), oy, px(p), oy + 5, color=INK, sw=1.2))
        f.append(text(px(p), oy + 20, lab, 10, MUTED, "middle"))
    for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
        f.append(line(ox - 5, py(v), ox, py(v), color=INK, sw=1.2))
        f.append(text(ox - 9, py(v) + 4, ("%.2f" % v).rstrip('0').rstrip('.'), 10, MUTED, "end"))
        if v:
            f.append(line(ox, py(v), ox + aw, py(v), color="#eef0f2", sw=1))

    # крива
    pts = ["%.1f,%.1f" % (px(0.0), py(0.0))]
    p = 0.002
    while p <= 0.9981:
        pts.append("%.1f,%.1f" % (px(p), py(Hb(p))))
        p += 0.004
    pts.append("%.1f,%.1f" % (px(1.0), py(0.0)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # максимум
    f.append(circle(px(0.5), py(1.0), 4.6, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(px(0.5), py(1.0) - 16, "рівні шанси → 1 біт (максимум)", 11, FIELD, "middle", bold=True))
    # точка давача тривоги — з винесеним униз підписом
    f.append(circle(px(0.1), py(Hb(0.1)), 4.6, fill=POS, stroke=POS, sw=0))
    f.append(line(px(0.1), py(Hb(0.1)) + 6, px(0.1), py(0.20), color=POS, sw=1.2, dash="3 3"))
    f.append(text(px(0.1) - 4, py(0.13), "давач тривоги: p=0.1 → 0.47 біта", 10.5, POS, "start", bold=True))
    # краї — нуль
    f.append(text(px(0.72), py(0.31), "певний наслідок → 0", 11, MUTED, "middle"))
    render(os.path.join(IMG, "entropy-range.svg"), W, H, *f,
           title="Ентропія двох наслідків: між 1 бітом і нулем")


# ── 4. Дві стіни Шеннона: підлога H і стеля C ─────────────────────────────────
# Ідея: кодер джерела тисне до H (нижче не можна), кодер каналу додає захист;
# усе проходить каналом ємності C (вище не можна). Надійно ⟺ H·R ≤ C.
def fig_two_limits():
    W, H = 900, 440
    f = []
    y, bh = 92, 76
    cy = y + bh / 2

    def box(x, w, title, sub, fill=FILL, stroke=LINE):
        r = rect(x, y, w, bh, fill=fill, stroke=stroke, sw=1.8, rx=9)
        lines = title.split("\n")
        if len(lines) > 1:
            t = mtext(x + w / 2, y + 26, lines, 12.5, INK, bold=True)
        else:
            t = text(x + w / 2, y + (30 if sub else bh / 2 + 5), title, 12.5, INK, "middle", bold=True)
        s = text(x + w / 2, y + 52, sub, 10.5, MUTED, "middle") if sub else ""
        return r + t + s

    f.append(box(28, 132, "Джерело", "H біт/символ"))
    f.append(box(206, 158, "Кодер джерела", "стиск → до H", "#eef6ef", FIELD))
    f.append(box(400, 158, "Кодер каналу", "+ захисні біти", "#fdecea", POS))
    f.append(box(594, 116, "Канал", "ємність C"))
    f.append(box(746, 126, "Декодер →\nОтримувач", ""))

    for x1, x2 in [(160, 206), (364, 400), (558, 594), (710, 746)]:
        f.append(arrow(x1, cy, x2, cy, color=INK, sw=2.0))

    # дві стіни — підлога під кодером джерела, стеля під каналом
    f.append(arrow(285, y + bh + 2, 285, 236, color=FIELD, sw=1.8))
    f.append(fitbox(198, 236, 174, 34, "ПІДЛОГА: нижче H\nне стиснути",
                    size=10.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True))
    f.append(arrow(652, y + bh + 2, 652, 236, color=POS, sw=1.8))
    f.append(fitbox(566, 236, 174, 34, "СТЕЛЯ: понад C\nне передати",
                    size=10.5, fill="#fdecea", stroke=POS, color=INK, bold=True))

    # підсумкова умова
    f.append(rect(250, 330, 400, 66, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(450, 358, "надійний зв'язок  ⟺  H · R ≤ C", 15, INK, "middle", bold=True))
    f.append(text(450, 381, "темп джерела вміщується під ємністю каналу", 10.5, MUTED, "middle"))
    render(os.path.join(IMG, "two-limits.svg"), W, H, *f,
           title="Дві стіни Шеннона: скільки треба (H) проти скільки можна (C)")


# ── 5. Родовід слова: термодинаміка → статистична фізика → інформація ─────────
# Ідея (для вставки hist-entropy-name): те саме слово й майже той самий вислів
# пройшли крізь три науки; Шеннонова H — це Ґіббсова S без сталої й у log₂.
def fig_entropy_lineage():
    W, H = 1000, 430
    f = []
    cy0, ch = 60, 196
    cw, gap, x0 = 220, 26, 20
    cards = [
        ("термодинаміка",     "Клаузіус", "Clausius", "німець · 1865",
         "dS = δQ / T",          "тепло δQ за температури T"),
        ("статистична фізика", "Больцман", "Boltzmann", "австрієць · 1877",
         "S = k · ln W",         "W — число рівних мікростанів"),
        ("статистична фізика", "Ґіббс",    "Gibbs",     "американець · 1902",
         "S = −k · ∑ pᵢ ln pᵢ",  "pᵢ — імовірність мікростану"),
        ("теорія інформації",  "Шеннон",   "Shannon",   "американець · 1948",
         "H = − ∑ pᵢ log₂ pᵢ",   "pᵢ — імовірність символу"),
    ]
    cxs = []
    for i, (field, name, tr, natyr, formula, note) in enumerate(cards):
        x = x0 + i * (cw + gap)
        cx = x + cw / 2
        cxs.append(cx)
        hot = i >= 2  # Ґіббс і Шеннон — виділяємо зеленим (там і стається збіг)
        f.append(rect(x, cy0, cw, ch, fill="#f7faf8" if hot else FILL,
                      stroke=FIELD if hot else LINE, sw=1.8 if hot else 1.5, rx=10))
        f.append(text(cx, cy0 + 26, field, 10.5, MUTED, "middle"))
        f.append(text(cx, cy0 + 52, name, 15, INK, "middle", bold=True))
        f.append(text(cx, cy0 + 70, tr, 10.5, MUTED, "middle", italic=True))
        f.append(text(cx, cy0 + 90, natyr, 10.5, INK, "middle"))
        f.append(rect(x + 14, cy0 + 104, cw - 28, 48,
                      fill="#eef6ef" if hot else "#eef0f2",
                      stroke=FIELD if hot else "#cfd6dd", sw=1.4, rx=7))
        f.append(text(cx, cy0 + 134, formula, 13, INK if hot else INK, "middle", bold=True))
        f.append(text(cx, cy0 + 180, note, 9.5, MUTED, "middle"))
        # стрілка руху ідеї в наступну картку (у проміжку, вище формул)
        if i < len(cards) - 1:
            f.append(arrow(x + cw + 2, cy0 + 90, x + cw + gap - 2, cy0 + 90,
                           color=INK, sw=1.8))

    # ── нижня рамка: збіг форми Ґіббс ↔ Шеннон ───────────────────────────────
    bx, by, bw, bh = 300, 296, 486, 118
    # короткі зелені містки від карток Ґіббса та Шеннона до рамки
    f.append(line(cxs[2], cy0 + ch, cxs[2], by, color=FIELD, sw=1.4, dash="3 3"))
    f.append(line(cxs[3], cy0 + ch, cxs[3], by, color=FIELD, sw=1.4, dash="3 3"))
    f.append(rect(bx, by, bw, bh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(bx + bw / 2, by + 24, "Збіг, що дав назву", 13, FIELD, "middle", bold=True))
    f.append(mtext(bx + 26, by + 50,
                   ["фізика (Ґіббс):     S = −k ∑ pᵢ · ln pᵢ",
                    "зв'язок (Шеннон):  H = −  ∑ pᵢ · log₂ pᵢ"], 12.5, INK, "start"))
    f.append(text(bx + bw / 2, by + 100,
                  "різниця лише в сталій k (Дж/К) та основі логарифма (ln → log₂)",
                  10.5, MUTED, "middle"))
    render(os.path.join(IMG, "entropy-lineage.svg"), W, H, *f,
           title="Родовід слова «ентропія»: одна формула крізь три науки")


# ── 6. Групування: той самий вибір двома кроками (аксіома Шеннона) ─────────────
# Ідея (для вставки math-entropy-axioms): H(½,⅓,⅙) = H(½,½) + ½·H(⅔,⅓).
# Спершу чесна монета; якщо випав «низ» — ще вибір із двох. Дерево = розбиття.
def fig_grouping():
    W, H = 900, 540
    f = []
    # вузли
    root = (120, 210)
    a    = (430, 108)
    node2= (300, 312)
    b    = (600, 250)
    c    = (600, 372)

    def node(p, r=8, fill=INK):
        return circle(p[0], p[1], r, fill=fill, stroke=fill, sw=0)

    # ребра (стрілки від батька до дитини)
    f.append(arrow(root[0] + 8, root[1] - 4, a[0] - 12, a[1] + 6, color=INK, sw=1.9))
    f.append(arrow(root[0] + 6, root[1] + 8, node2[0] - 12, node2[1] - 6, color=INK, sw=1.9))
    f.append(arrow(node2[0] + 10, node2[1] - 4, b[0] - 12, b[1] + 6, color=INK, sw=1.9))
    f.append(arrow(node2[0] + 10, node2[1] + 6, c[0] - 12, c[1] - 4, color=INK, sw=1.9))

    # підписи гілок (ймовірності кроку) — винесені збоку від ліній
    f.append(text(250, 150, "½", 15, NEG, "middle", bold=True))
    f.append(text(196, 268, "½", 15, NEG, "middle", bold=True))
    f.append(text(452, 268, "⅔", 15, FIELD, "middle", bold=True))
    f.append(text(452, 340, "⅓", 15, FIELD, "middle", bold=True))

    # вузли
    f.append(node(root)); f.append(node(node2))
    f.append(node(a, fill=POS)); f.append(node(b, fill=POS)); f.append(node(c, fill=POS))

    # підписи вузлів
    f.append(text(root[0] - 14, root[1] + 5, "старт", 11.5, INK, "end", bold=True))
    f.append(text(node2[0], node2[1] + 26, "(як випав «низ»)", 10, MUTED, "middle"))
    f.append(text(a[0] + 16, a[1] + 5, "a   ·   p = ½", 12.5, INK, "start", bold=True))
    f.append(text(b[0] + 16, b[1] + 5, "b   ·   p = ⅓", 12.5, INK, "start", bold=True))
    f.append(text(c[0] + 16, c[1] + 5, "c   ·   p = ⅙", 12.5, INK, "start", bold=True))

    # анотації двох кроків
    f.append(text(118, 118, "перший вибір: чесна монета  →  H(½, ½)", 11, NEG, "start"))
    f.append(text(300, 410, "другий вибір: із двох  →  H(⅔, ⅓)", 11, FIELD, "middle"))

    # рамка з тотожністю групування
    bx, by, bw, bh = 150, 442, 600, 86
    f.append(rect(bx, by, bw, bh, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(bx + bw / 2, by + 30, "H(½, ⅓, ⅙)  =  H(½, ½)  +  ½ · H(⅔, ⅓)",
                  15, INK, "middle", bold=True))
    f.append(text(bx + bw / 2, by + 58, "1.459 біта   =      1       +   ½ · 0.918   (та сама відповідь)",
                  11.5, MUTED, "middle"))
    render(os.path.join(IMG, "grouping.svg"), W, H, *f,
           title="Групування: обчислити ентропію прямо або двома кроками — однаково")


# ── 7. Основа логарифма — це лише вибір одиниці ───────────────────────────────
# Ідея (для вставки math-entropy-axioms): та сама несподіванка події p=1/10,
# зміряна трьома лінійками. Зміна основи логарифма тільки перейменовує одиницю.
def fig_units():
    W, H = 860, 470
    f = []
    x0, x1 = 150, 670          # 0 і кінець шкали (несподіванка p=1/10)
    rows = [
        (150, "основа 2  ·  біт (Sh)",  3.321928, [1, 2, 3],      "= 3.32 біта"),
        (258, "основа e  ·  нат",        2.302585, [1, 2],         "= 2.30 ната"),
        (366, "основа 10  ·  дит (Hart)", 1.000000, [0.5],          "= 1.00 дита"),
    ]
    # заголовок над лінійками
    f.append(text((x0 + x1) / 2, 74, "Та сама несподіванка події p = 1/10 — трьома лінійками",
                  12.5, INK, "middle", bold=True))

    # вертикаль, що сполучає кінці (та сама фізична точка)
    f.append(line(x1, 118, x1, 400, color=MUTED, sw=1.2, dash="4 4"))

    for y, lab, vmax, ticks, endval in rows:
        f.append(text(x0, y - 16, lab, 11, INK, "start", bold=True))
        f.append(line(x0, y, x1 + 6, y, color=INK, sw=1.7))
        f.append(arrow(x1, y, x1 + 22, y, color=INK, sw=1.7))
        # нуль
        f.append(line(x0, y - 6, x0, y + 6, color=INK, sw=1.4))
        f.append(text(x0, y + 22, "0", 10, MUTED, "middle"))
        # проміжні поділки цієї одиниці
        for tv in ticks:
            tx = x0 + (tv / vmax) * (x1 - x0)
            f.append(line(tx, y - 6, tx, y + 6, color=INK, sw=1.4))
            f.append(text(tx, y + 22, ("%.1f" % tv).rstrip('0').rstrip('.'), 10, MUTED, "middle"))
        # кінець-подія
        f.append(circle(x1, y, 5, fill=POS, stroke=POS, sw=0))
        f.append(text(x1 + 28, y + 5, endval, 11.5, POS, "start", bold=True))

    # підсумок-перерахунок унизу
    f.append(rect(120, 416, 620, 44, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=9))
    f.append(text(430, 443, "Зміна основи лише перейменовує одиницю:   1 нат = 1.443 біта,   1 дит = 3.322 біта",
                  11.5, INK, "middle", bold=True))
    render(os.path.join(IMG, "units.svg"), W, H, *f,
           title="Основа логарифма = вибір одиниці інформації")


if __name__ == "__main__":
    fig_surprise()
    fig_entropy_formula()
    fig_entropy_range()
    fig_two_limits()
    fig_entropy_lineage()
    fig_grouping()
    fig_units()
    print("OK: figures written to", IMG)
