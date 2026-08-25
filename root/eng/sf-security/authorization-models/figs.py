# -*- coding: utf-8 -*-
"""Фігури теми «Моделі авторизації». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

REDFILL = "#fdecea"
GRNFILL = "#e7f6ec"
BLUFILL = "#eaf0fd"


# ── 1. Одні ворота рішення ────────────────────────────────────────────────────
def fig_decision_gate():
    W, H = 1080, 470
    f = []

    # входи ліворуч
    inputs = [("суб'єкт", 120), ("дія", 196), ("ресурс", 272), ("контекст", 348)]
    in_right = None
    for name, cy in inputs:
        b, bw, bh = textbox(150, cy, name, size=13, fill=BLUFILL, stroke=NEG, pad=11, min_w=180)
        f.append(b)
        in_right = 150 + bw / 2

    # точка рішення (осердя)
    db, dw, dh = textbox(555, 234, "Точка рішення\nможна?(суб'єкт, дія, ресурс)",
                         size=15, bold=True, fill=GRNFILL, stroke=FIELD, sw=2.4, pad=16, min_w=300)
    f.append(db)
    d_left, d_right, d_top, d_bot = 555 - dw / 2, 555 + dw / 2, 234 - dh / 2, 234 + dh / 2

    # правила — знизу, живлять рішення
    rb, rw, rh = textbox(555, 400, "правила\nсписок · ролі · атрибути · зв'язки",
                         size=12, fill=FILL, stroke=MUTED, pad=12, min_w=300)
    f.append(rb)

    # стрілки входів → рішення (віялом)
    for _, cy in inputs:
        f.append(arrow(in_right + 8, cy, d_left - 8, 234, color=MUTED, sw=1.5))
    # правила → рішення
    f.append(arrow(555, 400 - rh / 2 - 6, 555, d_bot + 6, color=MUTED, sw=1.6))

    # виходи праворуч
    ob, ow, oh = textbox(905, 168, "дозволити", size=14, bold=True, fill=GRNFILL, stroke=FIELD, sw=2, pad=13, min_w=180)
    f.append(ob)
    f.append(plus(905 - ow / 2 - 18, 168))
    xb, xw, xh = textbox(905, 300, "відмовити", size=14, bold=True, fill=BLUFILL, stroke=NEG, sw=2, pad=13, min_w=180)
    f.append(xb)
    f.append(minus(905 - xw / 2 - 18, 300))
    f.append(text(905, 300 + xh / 2 + 22, "за замовчанням — сюди", size=12, color=MUTED))

    f.append(arrow(d_right + 8, 210, 905 - ow / 2 - 40, 168, color=FIELD, sw=1.8))
    f.append(arrow(d_right + 8, 258, 905 - xw / 2 - 40, 300, color=NEG, sw=1.8))

    render(out("decision-gate.svg"), W, H, *f,
           title="Одні ворота: місце застосування лише питає, рішення ухвалює окрема точка")


# ── 2. Прошарок ролей згортає «кожен до кожного» ──────────────────────────────
def fig_rbac_layer():
    W, H = 1080, 500
    f = []

    xU, xR, xP = 175, 545, 900
    f.append(text(xU, 70, "Люди", size=15, bold=True, color=INK))
    f.append(text(xR, 70, "Ролі", size=15, bold=True, color=INK))
    f.append(text(xP, 70, "Права", size=15, bold=True, color=INK))

    users = [("Ганна", 150), ("Богдан", 250), ("Орест", 350)]
    roles = [("редактор", 200), ("адмін", 330)]
    perms = [("читати", 120), ("писати", 220), ("видаляти", 320), ("налаштування", 420)]

    ub, rb_, pb = {}, {}, {}
    for name, cy in users:
        b, w, h = textbox(xU, cy, name, size=13, fill=FILL, stroke=LINE, pad=11, min_w=150)
        f.append(b); ub[name] = (xU + w / 2, cy)
    for name, cy in roles:
        b, w, h = textbox(xR, cy, name, size=13, bold=True, fill=BLUFILL, stroke=NEG, sw=2, pad=12, min_w=150)
        f.append(b); rb_[name] = (xR - w / 2, xR + w / 2, cy)
    for name, cy in perms:
        b, w, h = textbox(xP, cy, name, size=13, fill=GRNFILL, stroke=FIELD, pad=11, min_w=170)
        f.append(b); pb[name] = (xP - w / 2, cy)

    # люди → ролі
    for u, r in [("Ганна", "редактор"), ("Богдан", "редактор"), ("Орест", "адмін")]:
        ux, uy = ub[u]; rl, rr, ry = rb_[r]
        f.append(line(ux + 8, uy, rl - 8, ry, color=MUTED, sw=1.6))
    # ролі → права
    edges = [("редактор", "читати"), ("редактор", "писати"),
             ("адмін", "читати"), ("адмін", "писати"), ("адмін", "видаляти"), ("адмін", "налаштування")]
    for r, p in edges:
        rl, rr, ry = rb_[r]; px, py = pb[p]
        f.append(line(rr + 8, ry, px - 8, py, color=MUTED, sw=1.6))

    f.append(text(W / 2, 478, "два простих зв'язки замість «кожен користувач до кожного права»",
                  size=13, color=MUTED, italic=True))

    render(out("rbac-layer.svg"), W, H, *f,
           title="Роль — прошарок: людям видають ролі, ролям — права")


# ── 3. Вісь моделей: від «перелічити» до «обчислити» ─────────────────────────
def fig_model_axis():
    W, H = 1220, 470
    f = []

    axis_y = 250
    x0, x1 = 120, 1100
    f.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.4))
    f.append(arrow(x1 - 2, axis_y, x1 + 2, axis_y, color=INK, sw=2.4))
    f.append(arrow(x0 + 2, axis_y, x0 - 2, axis_y, color=INK, sw=2.4))

    # полюси осі — під рядком правил, щоб вертикальні зв'язки їх не перетинали
    f.append(text(x0 + 12, 432, "перелічити кожну пару явно", size=13, color=NEG, anchor="start", bold=True))
    f.append(text(x1 - 12, 432, "обчислити зі зв'язків і атрибутів", size=13, color=FIELD, anchor="end", bold=True))
    # верхній компроміс
    f.append(text(x0 + 12, 78, "◀ простіше · прозоріше · легше перевірити", size=12, color=MUTED, anchor="start"))
    f.append(text(x1 - 12, 78, "масштабніше · виразніше · важче перевіряти ▶", size=12, color=MUTED, anchor="end"))

    nodes = [
        (255, "ACL", "список\nна ресурсі", NEG, BLUFILL),
        (535, "RBAC", "роль → право", INK, FILL),
        (815, "ABAC", "правило\nнад атрибутами", INK, FILL),
        (1035, "ReBAC", "шлях\nу графі", FIELD, GRNFILL),
    ]
    for x, name, rule, col, fill in nodes:
        # назва моделі — над віссю
        nb, nw, nh = textbox(x, 150, name, size=15, bold=True, fill=fill, stroke=col, sw=2, pad=12, min_w=130)
        f.append(nb)
        f.append(line(x, 150 + nh / 2, x, axis_y - 9, color=col, sw=1.4))
        f.append(circle(x, axis_y, 9, fill=fill, stroke=col, sw=2.6))
        # де живе правило — під віссю
        rbx, rw, rh = textbox(x, 355, rule, size=12, fill=FILL, stroke=LINE, pad=11, min_w=150)
        f.append(line(x, axis_y + 9, x, 355 - rh / 2, color=col, sw=1.4))
        f.append(rbx)

    render(out("model-axis.svg"), W, H, *f,
           title="Моделі авторизації — точки однієї осі: від переліку до обчислення")


# ── 4. Матриця доступу і два способи її розрізати (вставка hist) ──────────────
def fig_matrix_cuts():
    W, H = 1200, 490
    f = []

    objs = ["звіт.md", "база клієнтів", "/etc/hosts", "принтер"]
    subs = ["Ганна", "Богдан", "Орест"]
    cells = [
        ["чит · пис", "чит",       "—",    "друк"],
        ["чит",       "чит · пис", "—",    "друк"],
        ["—",         "—",         "чит",  "—"],
    ]
    COL, ROW = 1, 1                       # який стовпчик і рядок підсвічуємо
    CROSS = "#e8f3f4"

    xh, wh = 30, 165                      # колонка з іменами
    x0, cw = 195, 170                     # сітка значень
    yh, hh = 112, 46                      # шапка з іменами об'єктів
    y0, rh = 158, 54
    x_end = x0 + cw * len(objs)           # 875
    y_end = y0 + rh * len(subs)           # 320

    # шапка
    f.append(rect(xh, yh, wh, hh, fill=FILL, stroke=LINE, sw=1.4))
    f.append(text(xh + wh / 2, yh + hh / 2 + 5, "хто \\ що", size=13, color=MUTED))
    for j, o in enumerate(objs):
        fill = BLUFILL if j == COL else FILL
        f.append(fitbox(x0 + cw * j, yh, cw, hh, o, size=13, bold=True, fill=fill, stroke=LINE, sw=1.4, rx=0))

    # рядки
    for i, s in enumerate(subs):
        y = y0 + rh * i
        f.append(rect(xh, y, wh, rh, fill=(GRNFILL if i == ROW else FILL), stroke=LINE, sw=1.4))
        f.append(text(xh + wh / 2, y + rh / 2 + 5, s, size=13, bold=True))
        for j in range(len(objs)):
            if i == ROW and j == COL:
                fill = CROSS
            elif j == COL:
                fill = BLUFILL
            elif i == ROW:
                fill = GRNFILL
            else:
                fill = BG
            f.append(rect(x0 + cw * j, y, cw, rh, fill=fill, stroke=LINE, sw=1.2, rx=0))
            f.append(text(x0 + cw * j + cw / 2, y + rh / 2 + 5, cells[i][j], size=13,
                          color=(MUTED if cells[i][j] == "—" else INK)))

    # виділення стовпчика й рядка
    f.append(rect(x0 + cw * COL, yh, cw, y_end - yh, fill="none", stroke=NEG, sw=3, rx=0))
    f.append(rect(xh, y0 + rh * ROW, x_end - xh, rh, fill="none", stroke=FIELD, sw=3, rx=0))

    # підпис до стовпчика — згори
    cbx, cbw, cbh = textbox(x0 + cw * COL + cw / 2, 70, "стовпчик — це список доступу (ACL)",
                            size=13, bold=True, fill=BLUFILL, stroke=NEG, sw=2, pad=12)
    f.append(cbx)
    f.append(arrow(x0 + cw * COL + cw / 2, 70 + cbh / 2 + 6, x0 + cw * COL + cw / 2, yh - 6, color=NEG, sw=1.8))

    # підпис до рядка — праворуч
    rbx, rbw, rbh = textbox(1040, y0 + rh * ROW + rh / 2, "рядок — це список повноважень\n(capability list)",
                            size=13, bold=True, fill=GRNFILL, stroke=FIELD, sw=2, pad=12)
    f.append(rbx)
    f.append(arrow(1040 - rbw / 2 - 8, y0 + rh * ROW + rh / 2, x_end + 8, y0 + rh * ROW + rh / 2, color=FIELD, sw=1.8))

    f.append(text(W / 2, 374, "«хто може цей ресурс?» — читаємо стовпчик", size=14, color=NEG, bold=True))
    f.append(text(W / 2, 404, "«що може ця людина?» — читаємо рядок", size=14, color=FIELD, bold=True))
    f.append(text(W / 2, 452, "клітин — 10¹², непорожніх — мільйонні частки: матрицю ніхто не зберігає цілою",
                  size=13, color=MUTED, italic=True))

    render(out("matrix-cuts.svg"), W, H, *f,
           title="Матриця доступу і два способи її розрізати")


# ── 5. Хронологія заторів (вставка hist) ──────────────────────────────────────
def fig_authz_timeline():
    W, H = 1340, 540
    f = []

    axis_y = 280
    f.append(line(80, axis_y, 1280, axis_y, color=INK, sw=2.4))
    f.append(arrow(1276, axis_y, 1282, axis_y, color=INK, sw=2.4))

    marks = [
        (155, "1965 · Multics",       "список на ресурсі",       "десятки людей — одна машина",   BLUFILL, NEG),
        (365, "1971 · матриця",       "спільна мова для схем",   "що взагалі означає «можна»",    BLUFILL, NEG),
        (575, "1973 · Белл і ЛаПадула", "мітки, яких власник не зніме", "власник не втримає таємниці", BLUFILL, NEG),
        (785, "1992 · ролі (RBAC)",   "прошарок між людьми й правами", "плинність кадрів у тисячах", FILL, LINE),
        (995, "2003 · XACML",         "правило над атрибутами",  "дозвіл залежить від обставин",  GRNFILL, FIELD),
        (1205, "2019 · Zanzibar",     "граф зв'язків на запит",  "люди діляться з людьми",        GRNFILL, FIELD),
    ]
    for k, (x, head, what, jam, fill, col) in enumerate(marks):
        up = (k % 2 == 0)
        cy = 140 if up else 420
        b, bw, bh = textbox(x, cy, head + "\n" + what + "\n" + jam,
                            size=13, fill=fill, stroke=col, sw=2, pad=12, min_w=200)
        f.append(b)
        y_from = cy + bh / 2 if up else cy - bh / 2
        f.append(line(x, y_from, x, axis_y + (-11 if up else 11), color=col, sw=1.5))
        f.append(circle(x, axis_y, 9, fill=fill, stroke=col, sw=2.6))

    f.append(text(W / 2, 512, "у кожній рамці: рік · модель · затор, який вона розчищала",
                  size=13, color=MUTED, italic=True))

    render(out("authz-timeline.svg"), W, H, *f,
           title="Кожна модель з'являлася там, де попередня впиралася в стіну")


# ── 6. Перевірка як обхід графа рівнями (вставка proj) ───────────────────────
def fig_rebac_walk():
    W, H = 1200, 735
    f = []

    xn, xr = 415, 880
    f.append(text(xn, 72, "вузол: множина «хто має relation до object»", size=13, color=MUTED))
    f.append(text(xr, 72, "що читаємо цим одним запитом", size=13, color=MUTED))

    bands = [
        ("рівень 0", "doc:api#editor",      "doc:api#editor\ndoc:api#parent"),
        ("рівень 1", "folder:specs#editor", "folder:specs#editor\nfolder:specs#parent"),
        ("рівень 2", "folder:root#editor",  "folder:root#editor\nfolder:root#parent"),
        ("рівень 3", "group:core#member",   "group:core#member"),
        ("рівень 4", "group:eng#member",    "group:eng#member"),
    ]
    edges = ["за зв'язком\nparent → editor",
             "за зв'язком\nparent → editor",
             "збережене\nребро (_this)",
             "збережене\nребро (_this)"]
    ys = [110, 222, 334, 446, 558]

    for i, (lvl, node, read) in enumerate(bands):
        y = ys[i]
        f.append(text(35, y + 5, lvl, size=13, color=MUTED, anchor="start"))
        nb, nw, nh = textbox(xn, y, node, size=14, bold=True, fill=BLUFILL, stroke=NEG, sw=2,
                             pad=12, min_w=290)
        f.append(nb)
        rb, rw, rh = textbox(xr, y, read, size=12, fill=FILL, stroke=LINE, pad=11, min_w=360)
        f.append(rb)
        f.append(line(xn + nw / 2 + 8, y, xr - rw / 2 - 8, y, color=MUTED, sw=1.3, dash="4 4"))

        if i < len(edges):
            f.append(arrow(xn, y + nh / 2 + 5, xn, ys[i + 1] - nh / 2 - 6, color=NEG, sw=1.8))
            f.append(mtext(xn - 105, y + nh / 2 + 28, edges[i], size=12, color=MUTED, anchor="end"))

    lb, lw, lh = textbox(xn, 655, "у сховищі знайдено ada — відповідь «так»",
                         size=14, bold=True, fill=GRNFILL, stroke=FIELD, sw=2.4, pad=13, min_w=290)
    f.append(arrow(xn, ys[-1] + 24, xn, 655 - lh / 2 - 6, color=FIELD, sw=1.8))
    f.append(lb)

    f.append(text(W / 2, 712, "5 рівнів — 5 походів у сховище; ширина рівня безплатна: два ключі їдуть одним запитом",
                  size=13, color=MUTED, italic=True))

    render(out("rebac-walk.svg"), W, H, *f,
           title="Перевірка «чи може ada редагувати doc:api» — обхід рівнями")


# ── 7. Кільце у зв'язках: мемо проти межі глибини (вставка proj) ─────────────
def fig_rebac_cycle():
    W, H = 1240, 480
    f = []
    f.append(line(620, 60, 620, 438, color=LINE, sw=1.2, dash="6 6"))

    def panel(cx, head, note, result, resfill, rescol, cut):
        g = []
        hb, hw, hh = textbox(cx, 82, head, size=14, bold=True,
                             fill=(GRNFILL if cut else REDFILL),
                             stroke=(FIELD if cut else POS), sw=2, pad=12, min_w=280)
        g.append(hb)
        n1, w1, h1 = textbox(cx, 180, "group:core#member", size=13, fill=BLUFILL, stroke=NEG,
                             sw=2, pad=12, min_w=260)
        n2, w2, h2 = textbox(cx, 300, "group:eng#member", size=13, fill=BLUFILL, stroke=NEG,
                             sw=2, pad=12, min_w=260)
        g.append(n1); g.append(n2)
        # справжнє ребро вниз
        g.append(arrow(cx - 58, 180 + h1 / 2 + 5, cx - 58, 300 - h2 / 2 - 6, color=MUTED, sw=1.7))
        # ребро, що замикає кільце (з мемо — розірване знаком ✕)
        if cut:
            g.append(line(cx + 58, 300 - h2 / 2 - 5, cx + 58, 257, color=MUTED, sw=1.7))
            g.append(arrow(cx + 58, 223, cx + 58, 180 + h1 / 2 + 6, color=MUTED, sw=1.7))
            g.append(circle(cx + 58, 240, 14, fill=BG, stroke=POS, sw=2.4))
            g.append(text(cx + 58, 245, "✕", size=15, color=POS, bold=True))
        else:
            g.append(arrow(cx + 58, 300 - h2 / 2 - 5, cx + 58, 180 + h1 / 2 + 6, color=POS, sw=1.7))
        nb, nw, nh = textbox(cx + 210, 240, note, size=12, fill=FILL, stroke=LINE, pad=10)
        g.append(nb)
        rb, rw, rh = textbox(cx, 400, result, size=13, bold=True, fill=resfill, stroke=rescol,
                             sw=2.4, pad=13, min_w=430)
        g.append(rb)
        return g

    f += panel(320, "пам'ятаємо розкриті вершини",
               "цю вершину вже\nрозкривали — стоп",
               "5 походів · чесне «ні»", GRNFILL, FIELD, cut=True)
    f += panel(900, "не пам'ятаємо — лише межа глибини",
               "розкриваємо знову:\nтуди-сюди до межі",
               "16 походів · помилка глибини", REDFILL, POS, cut=False)

    f.append(text(W / 2, 462, "цикл у даних: хтось вклав group:core назад у group:eng",
                  size=13, color=MUTED, italic=True))

    render(out("rebac-cycle.svg"), W, H, *f,
           title="Цикл у зв'язках: пам'ять про розкрите проти самої лише межі глибини")


if __name__ == "__main__":
    fig_decision_gate()
    fig_rbac_layer()
    fig_model_axis()
    fig_matrix_cuts()
    fig_authz_timeline()
    fig_rebac_walk()
    fig_rebac_cycle()
    print("OK: 7 фігур згенеровано в", IMG)
