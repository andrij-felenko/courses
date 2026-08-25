# -*- coding: utf-8 -*-
"""Фігури для теми «Класи P і NP та NP-повнота» (book/algorithms/complexity-computability)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_reduction():
    """A ≤ₚ B: поліномний перекладач + розв'язувач B = розв'язувач A."""
    W, H = 1080, 400
    yr = 150
    frags = []

    # ── конвеєр зліва направо ────────────────────────────────────────────────
    b1, w1, _ = textbox(115, yr, "Приклад\nзадачі A", size=15, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=2, pad=13)
    b2, w2, _ = textbox(360, yr, "Поліномний\nперекладач", size=15, bold=True,
                        fill="#e9f7ef", stroke=FIELD, sw=2.5, pad=13)
    b3, w3, _ = textbox(605, yr, "Приклад\nзадачі B", size=15, bold=True,
                        fill="#fdecea", stroke=POS, sw=2, pad=13)
    b4, w4, _ = textbox(830, yr, "Розв'язувач\nдля B", size=15, bold=True,
                        fill=FILL, stroke=LINE, sw=1.8, pad=13)
    b5, w5, _ = textbox(1000, yr, "так / ні", size=16, bold=True,
                        fill="#eef2f7", stroke="#c7ced6", sw=2, pad=13)
    frags += [b1, b2, b3, b4, b5]

    # стрілки між боксами (від правого краю до лівого краю сусіда)
    def edge(cx, w):
        return cx - w / 2, cx + w / 2
    l1r = edge(115, w1)[1]; l2l, l2r = edge(360, w2); l3l, l3r = edge(605, w3)
    l4l, l4r = edge(830, w4); l5l = edge(1000, w5)[0]
    for a, b in ((l1r, l2l), (l2r, l3l), (l3r, l4l), (l4r, l5l)):
        frags.append(arrow(a + 4, yr, b - 4, yr, color=INK, sw=2.2))

    # підпис зведення під перекладачем
    frags.append(text(360, yr + 62, "A ≤ₚ B", size=15, color=FIELD, bold=True, italic=True))
    # відповідь B — це й відповідь A
    frags.append(mtext(1000, yr + 56, ["= відповідь", "для A"], size=13,
                       color=MUTED))

    # ── стрілка важкості (проти напряму перекладу) ───────────────────────────
    hy = 250
    frags.append(arrow(l3r + 20, hy, l1r - 20, hy, color="#b8894a", sw=2.4))
    frags.append(text((115 + 605) / 2, hy - 12,
                      "важкість тече сюди: B не легша за A", size=14,
                      color="#a06a24", bold=True))

    # ── висновок ─────────────────────────────────────────────────────────────
    band, _, _ = textbox(540, 335,
                         "Швидкий (поліномний) розв'язувач B  ⇒  швидкий розв'язувач A",
                         size=16, bold=True, fill="#e9f7ef", stroke=FIELD, sw=2.5, pad=15)
    frags.append(band)

    render(os.path.join(IMG, "reduction.svg"), W, H, *frags,
           title="Зведення A ≤ₚ B: перекласти дешево — виміряти важкість")


def fig_domino():
    """NP-повні задачі сплетені взаємними зведеннями — стоять і падають разом."""
    W, H = 1000, 620
    cx, cy, R = 500, 320, 200
    frags = []

    names = ["SAT", "3-SAT", "Кліка", "Покриття\nвершин",
             "Розфарбування\nграфа", "Комівояжер", "Сума\nпідмножини"]
    n = len(names)
    pts = []
    for i in range(n):
        ang = math.radians(-90 + i * 360.0 / n)
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))

    # ребра-зведення по колу (в обидва боки — недирективні лінії)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        frags.append(line(ax, ay, bx, by, color="#9aa4b2", sw=2.2))

    # центральний висновок
    core, _, _ = textbox(cx, cy,
                        "поліномний алгоритм\nдля БУДЬ-ЯКОЇ однієї\n⇒  P = NP,\nі легкі всі одразу",
                        size=15, bold=True, fill="#e9f7ef", stroke=FIELD, sw=2.5, pad=14)
    frags.append(core)

    # вузли-задачі
    for (x, y), nm in zip(pts, names):
        box, _, _ = textbox(x, y, nm, size=14, bold=True,
                           fill="#fdecea", stroke=POS, sw=2, pad=11)
        frags.append(box)

    render(os.path.join(IMG, "domino.svg"), W, H, *frags,
           title="NP-повні задачі — одна спільнота, сплетена зведеннями")


def fig_three_tiers():
    """Три щаблі: P (легко) · NP-повні (важко) · нерозв'язні (неможливо)."""
    W, H = 1020, 430
    lx, lw = 24, 168
    cols = [(206, 258), (486, 258), (766, 258)]  # (x, width)
    y0, hh, rh = 60, 74, 78

    frags = []
    # кутовий підпис (порожня клітина над лівим стовпцем міток)
    frags.append(fitbox(lx, y0, lw, hh, "", fill=BG, stroke="none", sw=0))

    heads = [("P — легко", "#e9f7ef", FIELD),
             ("NP-повні — важко", AMBER_F, AMBER_S),
             ("Нерозв'язні — неможливо", "#f2f4f6", MUTED)]
    for (cx, cw), (h, f, s) in zip(cols, heads):
        frags.append(fitbox(cx, y0, cw, hh, h, size=16, bold=True, fill=f, stroke=s, sw=2.4))

    rows = [
        ("Знайти\nрозв'язок",
         [("швидко\n(поліном)", "#e9f7ef", FIELD),
          ("повільно\n(перебір 2ⁿ)", AMBER_F, AMBER_S),
          ("ніколи\n(алгоритму нема)", "#f2f4f6", MUTED)]),
        ("Перевірити\nсвідка",
         [("швидко", "#e9f7ef", FIELD),
          ("швидко", "#e9f7ef", FIELD),
          ("короткого\nсвідка немає", "#f2f4f6", MUTED)]),
        ("Приклади",
         [("сортування,\nнайкоротший шлях", BG, "#dfe4ea"),
          ("SAT, розфарбування,\nкомівояжер", BG, "#dfe4ea"),
          ("проблема\nзупинки", BG, "#dfe4ea")]),
    ]
    for r, (label, cells) in enumerate(rows):
        y = y0 + hh + r * rh
        frags.append(fitbox(lx, y, lw, rh, label, size=14, bold=True,
                            fill="#eef2f7", stroke="#c7ced6"))
        for (cx, cw), (txt, f, s) in zip(cols, cells):
            frags.append(fitbox(cx, y, cw, rh, txt, size=14, fill=f, stroke=s,
                                bold=(f != BG)))

    render(os.path.join(IMG, "three-tiers.svg"), W, H, *frags,
           title="Де стоїть NP-повнота: між легким і неможливим")


def _ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, opacity=1.0):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
            'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, rx, ry, fill, opacity, stroke, sw))


def fig_np_equivalence():
    """Дві рівносильні дефініції NP: перевіряч зі свідком ↔ недетермінована МТ."""
    W, H = 1180, 580
    frags = []

    # ── ЛІВА панель: перевіряч зі свідком ────────────────────────────────────
    hb, _, _ = textbox(255, 78, "Означення A · перевіряч зі свідком", size=15,
                       bold=True, fill="#eaf0fd", stroke=NEG, sw=2, pad=12)
    frags.append(hb)
    bx1, _, _ = textbox(150, 158, "вхід x", size=14, bold=True,
                        fill=FILL, stroke=LINE, sw=1.6, pad=12)
    bx2, _, _ = textbox(372, 158, "свідок w\n|w| ≤ p(n)", size=14, bold=True,
                        fill="#e9f7ef", stroke=FIELD, sw=2, pad=12)
    frags += [bx1, bx2]
    vb, _, _ = textbox(261, 258, "V(x, w)\nполіномний час", size=14, bold=True,
                       fill=FILL, stroke=LINE, sw=1.8, pad=13)
    frags.append(vb)
    ob, _, _ = textbox(261, 352, "прийняти / відхилити", size=14, bold=True,
                       fill="#eef2f7", stroke="#c7ced6", sw=2, pad=12)
    frags.append(ob)
    frags.append(arrow(150, 178, 222, 236, color=INK, sw=2))
    frags.append(arrow(372, 178, 300, 236, color=INK, sw=2))
    frags.append(arrow(261, 282, 261, 330, color=INK, sw=2))
    frags.append(mtext(261, 420, ["x ∈ L  ⟺  ∃ w, |w| ≤ p(n) :",
                                  "V(x, w) = прийняти"], size=14, bold=True, color=NEG))

    # ── ПРАВА панель: недетермінована машина Тюринга (дерево гілок) ───────────
    hb2, _, _ = textbox(915, 78, "Означення B · недетермінована МТ", size=15,
                        bold=True, fill="#e9f7ef", stroke=FIELD, sw=2, pad=12)
    frags.append(hb2)
    root = (915, 142)
    l1 = [(820, 222), (915, 222), (1010, 222)]
    g = [(968, 306), (1052, 306)]
    # ребра дерева
    for p in l1:
        frags.append(line(root[0], root[1] + 9, p[0], p[1] - 9, color=MUTED, sw=1.8))
    frags.append(line(l1[2][0], l1[2][1] + 9, g[0][0], g[0][1] - 9, color=MUTED, sw=1.8))
    # виграшна гілка — зелена, товща
    frags.append(line(root[0], root[1] + 9, l1[2][0], l1[2][1] - 9, color=FIELD, sw=3.4))
    frags.append(line(l1[2][0], l1[2][1] + 9, g[1][0], g[1][1] - 9, color=FIELD, sw=3.4))
    # вузли
    frags.append(circle(root[0], root[1], 9, fill="#eef2f7", stroke=INK, sw=2))
    frags.append(text(root[0], root[1] - 18, "старт", size=13, bold=True))
    for p in l1[:2] + [g[0]]:
        frags.append(circle(p[0], p[1], 8, fill="#f2f4f6", stroke=MUTED, sw=1.8))
    for p in [l1[2]]:
        frags.append(circle(p[0], p[1], 8, fill="#e9f7ef", stroke=FIELD, sw=2.4))
    frags.append(circle(g[1][0], g[1][1], 9, fill=FIELD, stroke=FIELD, sw=2))
    frags.append(text(g[1][0] + 4, g[1][1] + 26, "приймає", size=13, bold=True, color=FIELD))
    frags.append(mtext(760, 250, ["інші гілки", "відхиляють"], size=12, color=MUTED))
    frags.append(mtext(915, 402, ["x ∈ L  ⟺  існує гілка", "обчислення, що приймає"],
                       size=14, bold=True, color=FIELD))

    # ── місток між означеннями ───────────────────────────────────────────────
    frags.append(arrow(505, 168, 690, 168, color="#b8894a", sw=2.2))
    frags.append(text(597, 153, "вгадати w = зробити недетерм. вибори", size=13,
                      color="#a06a24", bold=True))
    frags.append(arrow(690, 300, 505, 300, color="#b8894a", sw=2.2))
    frags.append(text(597, 320, "вибори вздовж гілки = свідок w", size=13,
                      color="#a06a24", bold=True))

    band, _, _ = textbox(590, 512,
                         "Той самий клас: «угадати свідка + перевірити за поліном»  ≡  «є недетермінована гілка, що приймає за поліном»",
                         size=14, bold=True, fill="#fff6e5", stroke="#e08a1e", sw=2, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "np-equivalence.svg"), W, H, *frags,
           title="Дві рівносильні дефініції NP — і місток між ними")


def fig_hierarchy():
    """Концентричні класи P ⊆ NP ⊆ PSPACE ⊆ EXPTIME + примітка про строгий стрибок."""
    W, H = 940, 580
    frags = []
    # чотири вкладені рамки (зовнішня — EXPTIME, внутрішня — P)
    frags.append(rect(40, 66, 860, 434, fill="#fbfcfd", stroke=MUTED, sw=2, rx=18))
    frags.append(rect(112, 128, 716, 320, fill="#f4f6f8", stroke="#8a93a0", sw=2, rx=16))
    frags.append(rect(196, 190, 548, 214, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=14))
    frags.append(rect(310, 250, 320, 108, fill="#e9f7ef", stroke=FIELD, sw=2.4, rx=12))

    # підписи-заголовки в верхній смузі кожної рамки
    frags.append(text(470, 92, "EXPTIME — розв'язне за час 2^poly(n)", size=15, bold=True, color=MUTED))
    frags.append(text(470, 152, "PSPACE — поліномна пам'ять", size=15, bold=True, color="#5a6472"))
    frags.append(text(470, 213, "NP — свідок перевіряється за поліном", size=15, bold=True, color=NEG))
    frags.append(mtext(470, 292, ["P — розв'язне за поліном", "(сортування, найкоротший шлях)"],
                       size=14, bold=True, color=FIELD))

    # приклади в нижніх смугах
    frags.append(text(470, 388, "SAT, розфарбування, комівояжер — NP-повні", size=13, bold=True, color=NEG))
    frags.append(text(470, 432, "QBF — істинність кванторної булевої формули", size=13, color="#5a6472"))
    frags.append(text(470, 484, "будь-яка NP-задача грубим перебором усіх свідків", size=13, color=MUTED))

    cap, _, _ = textbox(470, 545,
                        "Усі включення доведені. Теорема ієрархії за часом дає P ⊊ EXPTIME — тож бодай один ⊆ строгий, лише невідомо котрий",
                        size=13, bold=True, fill="#fff6e5", stroke="#e08a1e", sw=2, pad=12)
    frags.append(cap)

    render(os.path.join(IMG, "hierarchy.svg"), W, H, *frags,
           title="Ланцюг класів: P ⊆ NP ⊆ PSPACE ⊆ EXPTIME")


def fig_np_conp():
    """NP та co-NP: асиметрія свідка, факторизація в перетині."""
    W, H = 1020, 560
    frags = []
    npc = (420, 300)
    cnp = (660, 300)
    rx, ry = 300, 175
    frags.append(_ellipse(npc[0], npc[1], rx, ry, fill="#eaf0fd", stroke=NEG, sw=2.4, opacity=0.55))
    frags.append(_ellipse(cnp[0], cnp[1], rx, ry, fill="#e9f7ef", stroke=FIELD, sw=2.4, opacity=0.55))

    frags.append(text(250, 210, "NP", size=22, bold=True, color=NEG))
    frags.append(text(830, 210, "co-NP", size=22, bold=True, color=FIELD))
    frags.append(mtext(238, 305, ["свідок ТАК:", "SAT, розфарбування", "(NP-повні)"],
                       size=13, bold=True, color=NEG))
    frags.append(mtext(842, 305, ["свідок НІ:", "UNSAT,", "TAUTOLOGY"],
                       size=13, bold=True, color=FIELD))

    # перетин
    frags.append(text(540, 178, "NP ∩ co-NP", size=14, bold=True, color="#6b7280"))
    frags.append(text(540, 240, "факторизація", size=14, bold=True, color="#a06a24"))
    frags.append(_ellipse(540, 340, 96, 50, fill="#ffffff", stroke=INK, sw=2))
    frags.append(text(540, 346, "P", size=20, bold=True, color=INK))

    band, _, _ = textbox(510, 500,
                         "NP свідчить «ТАК» · co-NP свідчить «НІ» · факторизація має обидва свідки, тож у перетині — і навряд чи NP-повна",
                         size=13, bold=True, fill="#fff6e5", stroke="#e08a1e", sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "np-conp.svg"), W, H, *frags,
           title="NP та co-NP: асиметрія свідка й місце факторизації")


def fig_asymmetry():
    """Перевірити свідка — один прохід O(n); знайти — розгалуження на 2ⁿ гілок."""
    W, H = 1120, 450
    frags = []
    frags.append(line(548, 66, 548, 410, color="#d5dbe2", sw=2, dash="7 7"))

    # ── ЛІВОРУЧ: перевірка свідка за один прохід ─────────────────────────────
    t, _, _ = textbox(278, 80, "Перевірити свідка", size=17, bold=True,
                      fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=12)
    frags.append(t)
    frags.append(text(278, 116, "один прохід — O(n)", size=14, color=FIELD, bold=True))

    vals = ["3", "34", "4", "12", "5", "2"]
    chosen = {2, 4}                      # обрані елементи свідка: 4 і 5
    x0, cw, gap, yb = 64, 60, 8, 176
    for i, v in enumerate(vals):
        x = x0 + i * (cw + gap)
        hi = i in chosen
        frags.append(fitbox(x, yb, cw, 46, v, size=17, bold=hi,
                            fill=("#e9f7ef" if hi else "#eef2f7"),
                            stroke=(FIELD if hi else "#aab2bd"), sw=(2.6 if hi else 1.6)))
    xr = x0 + len(vals) * (cw + gap) - gap
    frags.append(text((x0 + xr) / 2, yb + 74, "1 прохід зліва направо", size=13, color=MUTED))
    frags.append(arrow(x0, yb + 86, xr, yb + 86, color=INK, sw=2.4))
    band, _, _ = textbox(278, yb + 150, "4 + 5 = 9 = ціль   ✓", size=16, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)
    frags.append(band)

    # ── ПРАВОРУЧ: перебір 2ⁿ гілок (дерево «взяти / не взяти») ────────────────
    t2, _, _ = textbox(824, 80, "Знайти перебором", size=17, bold=True,
                       fill="#fdecea", stroke=POS, sw=2.4, pad=12)
    frags.append(t2)
    frags.append(text(824, 116, "2ⁿ гілок", size=14, color=POS, bold=True))

    rx0, rx1, top, bot, levels = 606, 1052, 150, 306, 4
    prev = []
    for lvl in range(levels + 1):
        cnt = 2 ** lvl
        y = top + lvl * (bot - top) / levels
        xs = [rx0 + (rx1 - rx0) * (k + 0.5) / cnt for k in range(cnt)]
        pts = [(x, y) for x in xs]
        for k, (x, y2) in enumerate(pts):
            if prev:
                px, py = prev[k // 2]
                frags.append(line(px, py, x, y2, color="#c6cdd6", sw=1.2))
        prev = pts
        frags.append(text(rx0 - 30, y + 4, str(cnt), size=12, color=MUTED,
                          anchor="end", bold=True))
    # внутрішні вузли — крапки; листки — глухі, один ✓
    for lvl in range(levels):
        cnt = 2 ** lvl
        y = top + lvl * (bot - top) / levels
        for k in range(cnt):
            x = rx0 + (rx1 - rx0) * (k + 0.5) / cnt
            frags.append(circle(x, y, 2.6, fill="#8a93a0", stroke="none", sw=0))
    cnt = 2 ** levels
    good = 11
    for k in range(cnt):
        x = rx0 + (rx1 - rx0) * (k + 0.5) / cnt
        if k == good:
            frags.append(circle(x, bot, 6.5, fill="#e9f7ef", stroke=FIELD, sw=2.4))
        else:
            frags.append(circle(x, bot, 3.2, fill="#f2f4f6", stroke="#c6cdd6", sw=1))
    frags.append(text(824, bot + 44, "2ⁿ листків: майже всі глухі, один ✓",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "pass-vs-branch.svg"), W, H, *frags,
           title="Перевірити — один прохід; знайти — цілий ліс на 2ⁿ гілок")


def fig_three_roles():
    """Той самий граф C6, три ролі одного набору {0,2,4}:
    незалежна множина в G · кліка в доповненні · покриття = решта вершин."""
    W, H = 1240, 480
    R, nr, cy = 88, 15, 272
    C6 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    Ec = set((min(u, v), max(u, v)) for (u, v) in C6)
    COMP = [(i, j) for i in range(6) for j in range(i + 1, 6) if (i, j) not in Ec]
    IS, VC, TRI = {0, 2, 4}, {1, 3, 5}, {(0, 2), (2, 4), (0, 4)}
    frags = []

    def pos(cx):
        return [(cx + R * math.cos(math.radians(-90 + i * 60)),
                 cy + R * math.sin(math.radians(-90 + i * 60))) for i in range(6)]

    def node(x, y, i, hi, cf, cs):
        f = cf if hi else "#eef2f7"
        s = cs if hi else "#aab2bd"
        return (circle(x, y, nr, fill=f, stroke=s, sw=(3 if hi else 1.8)) +
                text(x, y + 5, str(i), size=15, bold=hi,
                     color=(cs if hi else "#6b7280")))

    def panel(cx, edges, hiset, cf, cs, bold_edges=None):
        pts = pos(cx)
        out = []
        for (u, v) in edges:
            he = bold_edges and (min(u, v), max(u, v)) in bold_edges
            out.append(line(pts[u][0], pts[u][1], pts[v][0], pts[v][1],
                            color=(cs if he else "#9aa4b2"), sw=(3.4 if he else 2.1)))
        for i, (x, y) in enumerate(pts):
            out.append(node(x, y, i, i in hiset, cf, cs))
        return out

    # A — незалежна множина в G
    frags.append(textbox(216, 82, "1. Незалежна множина в G",
                         size=15, bold=True, fill="#e9f7ef", stroke=FIELD, sw=2.3, pad=11)[0])
    frags += panel(216, C6, IS, "#e9f7ef", FIELD)
    frags.append(text(216, 420, "жодні дві обрані не суміжні", size=13, color=MUTED))

    # B — кліка в доповненні Ḡ (той самий набір)
    frags.append(textbox(620, 82, "2. Кліка в доповненні Ḡ",
                         size=15, bold=True, fill="#e9f7ef", stroke=FIELD, sw=2.3, pad=11)[0])
    frags += panel(620, COMP, IS, "#e9f7ef", FIELD, bold_edges=TRI)
    frags.append(text(620, 420, "ті самі три — тепер попарно суміжні", size=13, color=MUTED))

    # C — покриття вершин у G (решта вершин)
    frags.append(textbox(1024, 82, "3. Покриття вершин у G",
                         size=15, bold=True, fill="#fff6e5", stroke=AMBER_S, sw=2.3, pad=11)[0])
    frags += panel(1024, C6, VC, "#fff6e5", AMBER_S)
    frags.append(text(1024, 420, "решта: кожне ребро торкнуте", size=13, color=MUTED))

    render(os.path.join(IMG, "three-roles.svg"), W, H, *frags,
           title="Один набір {0, 2, 4} — три задачі: зведення пересуває погляд, не граф")


if __name__ == "__main__":
    fig_reduction()
    fig_domino()
    fig_three_tiers()
    fig_np_equivalence()
    fig_hierarchy()
    fig_np_conp()
    fig_asymmetry()
    fig_three_roles()
    print("OK:", sorted(os.listdir(IMG)))
