# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: дві сім'ї CRDT — везеться стан проти везеться операція ──────────────
# Ідея: зліва репліка шле ВЕСЬ свій стан, приймач зливає його операцією join;
# канал може губити/дублювати/переставляти — досить, щоб пакет колись дійшов.
# Справа репліка шле саму ОПЕРАЦІЮ; паралельні операції мусять комутувати, а
# канал — доставити кожну рівно раз і в причинному порядку. Різна ціна, різні
# вимоги до каналу — та сама збіжність.
def fig_families():
    W, H = 960, 470
    p = []

    def panel(px, title, subtitle, ship_label, rule_label, chan_label, accent):
        out = []
        pw, ph = 420.0, 340.0
        py = 70.0
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=12))
        out.append(text(px + pw / 2, py + 30, title, size=15, color=accent, bold=True))
        out.append(text(px + pw / 2, py + 52, subtitle, size=12, color=MUTED))
        # дві репліки
        ry = py + 92
        rw, rh = 118.0, 52.0
        ax = px + 34
        bx = px + pw - 34 - rw
        out.append(fitbox(ax, ry, rw, rh, "Репліка A", size=13, fill="#eef2f7", stroke=LINE, bold=True))
        out.append(fitbox(bx, ry, rw, rh, "Репліка B", size=13, fill="#eef2f7", stroke=LINE, bold=True))
        # стрілка A → B з підписом «що їде»
        ay = ry + rh / 2
        out.append(arrow(ax + rw + 6, ay, bx - 6, ay, color=accent, sw=2.2))
        b, bw, bh = textbox((ax + rw + bx) / 2, ay - 34, ship_label, size=12,
                            pad=8, fill="#ffffff", stroke=accent, color=accent, bold=True)
        out.append(b)
        # що робить приймач
        out.append(fitbox(px + 30, ry + rh + 46, pw - 60, 46, rule_label, size=12.5,
                          fill="#f4f8f4" if accent == FIELD else "#fdf2ee",
                          stroke=accent, color=INK, bold=True))
        # вимога до каналу
        out.append(fitbox(px + 30, ry + rh + 108, pw - 60, 58, chan_label, size=12,
                          fill="#f7f8fa", stroke="#c7ced6", color=INK))
        return out

    p.extend(panel(26, "Стан (CvRDT)", "convergent — збіжний",
                   "весь стан",
                   "приймач: злиття = join (найменша верхня межа)",
                   "канал може губити, дублювати й переставляти —\nдосить, щоб пакет КОЛИСЬ дійшов", FIELD))
    p.extend(panel(514, "Операції (CmRDT)", "commutative — комутативний",
                   "сама операція",
                   "приймач: застосувати операцію на місці",
                   "паралельні операції мусять комутувати; канал —\nрівно раз і в причинному порядку", POS))

    render(os.path.join(OUT, "families.svg"), W, H, *p,
           title="Дві сім'ї CRDT: чим саме обмінюються репліки")


# ── Фіг. 2: лічильник-що-росте як поелементний максимум ─────────────────────────
# Ідея: стан G-Counter — вектор «скільки нарахувала кожна репліка». Злиття бере
# поелементний максимум: воно комутативне, асоціативне й ІДЕМПОТЕНТНЕ (повтор
# нічого не змінює), тож хоч як тасуй і дублюй доставку — усі дійдуть того самого
# вектора, а значення — його сума.
def fig_gcounter():
    W, H = 900, 430
    p = []
    labels = ["A", "B", "C"]
    va = [3, 1, 0]
    vb = [2, 1, 4]
    vm = [max(x, y) for x, y in zip(va, vb)]

    def vec(cx, cy, title, vals, hi=None, accent=LINE):
        out = []
        cell = 56.0
        n = len(vals)
        total_w = cell * n
        x0 = cx - total_w / 2
        out.append(text(cx, cy - 40, title, size=13.5, color=accent, bold=True))
        # шапки реплік
        for i, lb in enumerate(labels):
            out.append(text(x0 + cell * (i + 0.5), cy - 16, lb, size=11.5, color=MUTED))
        for i, v in enumerate(vals):
            bx = x0 + cell * i
            isbold = hi is not None and hi[i]
            fill = "#eef7f0" if isbold else "#f4f6f8"
            stroke = FIELD if isbold else LINE
            out.append(rect(bx, cy, cell, cell, fill=fill, stroke=stroke, sw=1.6, rx=6))
            out.append(text(bx + cell / 2, cy + cell / 2 + 8, str(v), size=22,
                            color=INK, bold=True))
        return out, x0, total_w

    # два вхідні вектори зліва згори й знизу
    fa, _, _ = vec(240, 90, "стан на A", va)
    fb, _, _ = vec(240, 250, "стан на B", vb)
    # результат праворуч
    hi = [vm[i] == va[i] or True for i in range(3)]  # усі — з максимуму
    fm, xm, wm = vec(690, 170, "після злиття (max поелементно)", vm, hi=hi, accent=FIELD)
    p.extend(fa); p.extend(fb); p.extend(fm)

    # знак злиття
    p.append(text(455, 175, "⊔", size=40, color=FIELD, bold=True))
    p.append(arrow(300, 118, 560, 165, color="#c7ced6", sw=1.6))
    p.append(arrow(300, 250, 560, 200, color="#c7ced6", sw=1.6))

    # значення = сума
    p.append(fitbox(560, 300, 260, 44,
                    "значення = 3 + 1 + 4 = 8", size=14,
                    fill="#eef7f0", stroke=FIELD, color=INK, bold=True))
    # властивість
    p.append(fitbox(60, 340, 780, 46,
                    "max(x, x) = x  —  повторне або переставлене злиття дає той самий вектор",
                    size=13, fill="#f7f8fa", stroke="#c7ced6", color=INK))

    render(os.path.join(OUT, "gcounter-merge.svg"), W, H, *p,
           title="Лічильник-що-росте: злиття — це поелементний максимум")


# ── Фіг. 3: напіврешітка станів — злиття є найменша верхня межа ─────────────────
# Ідея: стани впорядковані «хто кого включає». Два паралельні стани s1, s2
# непорівнянні, але мають спільну НАЙМЕНШУ верхню межу s1⊔s2 — саме її дає злиття.
# Стан лише «лізе вгору» (монотонність); низ ⊥ — початок. Будь-яка пара має join —
# тому всі репліки сходяться в одну вершину.
def fig_semilattice():
    W, H = 820, 524
    p = []

    def node(cx, cy, lab, accent=LINE, fill="#f4f6f8", r=27):
        return (circle(cx, cy, r, fill=fill, stroke=accent, sw=2.0) +
                text(cx, cy + 6, lab, size=15, color=accent, bold=True))

    # координати
    bot = (410, 428)           # ⊥
    l1  = (250, 318)           # s1
    l2  = (570, 318)           # s2
    mid = (410, 318)           # ще один стан для «решітковості»
    top = (410, 182)           # join = s1 ⊔ s2

    # ребра (знизу вгору) — малюємо ПЕРЕД вузлами
    for a, b in [(bot, l1), (bot, mid), (bot, l2), (l1, top), (l2, top), (mid, top)]:
        p.append(line(a[0], a[1], b[0], b[1], color="#b9c2cc", sw=1.8))

    # вузли
    p.append(node(*bot, lab="⊥", accent=MUTED))
    p.append(node(*l1, lab="s₁", accent=NEG))
    p.append(node(*l2, lab="s₂", accent=NEG))
    p.append(node(*mid, lab="t", accent=MUTED, fill="#f7f8fa"))
    p.append(node(*top, lab="s₁⊔s₂", accent=FIELD, fill="#eef7f0", r=34))

    # підписи (з відступом, повз лінії й вузли)
    p.append(text(158, 318, "паралельні", size=12, color=NEG, anchor="end"))
    p.append(text(662, 318, "стани", size=12, color=NEG, anchor="start"))
    p.append(text(410, 128, "найменша верхня межа (join)", size=12.5, color=FIELD, bold=True))

    # стрілка монотонності збоку
    p.append(arrow(724, 428, 724, 182, color="#c7ced6", sw=2.0))
    p.append(text(752, 300, "стан", size=12, color=MUTED, anchor="start"))
    p.append(text(752, 317, "лише", size=12, color=MUTED, anchor="start"))
    p.append(text(752, 334, "росте", size=12, color=MUTED, anchor="start"))

    # нижня рамка-висновок
    p.append(fitbox(110, 466, 600, 40,
                    "будь-яка пара станів має спільний join → репліки сходяться в одну вершину",
                    size=12.5, fill="#f7f8fa", stroke="#c7ced6", color=INK))

    render(os.path.join(OUT, "semilattice.svg"), W, H, *p,
           title="Стани як напіврешітка: злиття — найменша верхня межа")


# ── Фіг. 4: OR-Set — чому «додавання перемагає» ─────────────────────────────────
# Ідея: кожне додавання елемента народжує УНІКАЛЬНИЙ тег. Видалення прибирає лише
# ті теги, які воно на місці бачило. Паралельне додавання дало НОВИЙ тег a₂, якого
# видалення не бачило, — тож після злиття x лишається. Конфлікт add/remove
# вирішено детерміновано на користь додавання.
def fig_orset():
    W, H = 900, 496
    p = []

    # спільний початок
    p.append(fitbox(330, 58, 240, 56,
                    "спочатку скрізь:\nx має тег a₁", size=13,
                    fill="#eef2f7", stroke=LINE, color=INK, bold=True))
    # стрілки віялом до ВЕРХІВ гілкових рамок (не перетинають підписів)
    p.append(arrow(408, 116, 258, 182, color="#c7ced6", sw=1.8))
    p.append(arrow(492, 116, 642, 182, color="#c7ced6", sw=1.8))

    # ліва гілка — A видаляє (заголовок — перший рядок УСЕРЕДИНІ рамки)
    p.append(fitbox(96, 186, 316, 104,
                    "Репліка A — паралельно\nremove(x): прибрати теги,\nщо БАЧУ зараз  →  {a₁}\nдодано { }    видалено { a₁ }",
                    size=12.5, fill="#eaf0fd", stroke=NEG, color=INK))

    # права гілка — B додає
    p.append(fitbox(488, 186, 316, 104,
                    "Репліка B — паралельно\nadd(x): народити НОВИЙ тег a₂\n\nдодано { a₂ }    видалено { }",
                    size=12.5, fill="#fdecea", stroke=POS, color=INK))

    # злиття
    p.append(arrow(254, 294, 404, 350, color="#c7ced6", sw=1.8))
    p.append(arrow(646, 294, 496, 350, color="#c7ced6", sw=1.8))
    p.append(fitbox(238, 354, 424, 92,
                    "після злиття\nдодано { a₁, a₂ }    видалено { a₁ }\nживі теги = {a₂} ≠ ∅   →   x У МНОЖИНІ",
                    size=13, fill="#eef7f0", stroke=FIELD, color=INK, bold=True))
    p.append(text(450, 474, "додавання перемагає: новий тег a₂ переживає видалення, що його не бачило",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "or-set.svg"), W, H, *p,
           title="OR-Set: унікальні теги роблять «додавання перемагає»")


# ── Фіг. 5: хронологія — дві течії сходяться у формалізації 2011 ────────────────
# Ідея (для вставки-історії): CRDT народився зі злиття двох незалежних морок —
# СПІЛЬНЕ РЕДАГУВАННЯ (синій трек: OT → WOOT → Commutative RDT → Treedoc) і
# ДОСТУПНІ ДАНІ В ІНДУСТРІЇ (червоний трек: епідемічні алгоритми → Bayou → Dynamo).
# Обидві течії впадають у зелений вузол 2011 року (формалізація, SEC, CvRDT+CmRDT),
# а 2015-й дельта-варіант здешевлює доставку.
def fig_timeline():
    W, H = 940, 612
    p = []

    BLUE_F, RED_F, GREEN_F = "#eef2fb", "#fdeeec", "#eef7f0"
    spine_x = 460.0

    def ev(cy, year, side, lines, accent, fill, node=True):
        out = []
        r = 21.0
        # картка ліворуч або праворуч від хребта
        cw, ch = 350.0, 48.0
        if side == "L":
            cx = 70.0
            out.append(line(cx + cw, cy, spine_x - r, cy, color="#c7ced6", sw=1.4))
        else:
            cx = 520.0
            out.append(line(cx, cy, spine_x + r, cy, color="#c7ced6", sw=1.4))
        out.append(fitbox(cx, cy - ch / 2, cw, ch, lines, size=12.5, pad=9,
                          fill=fill, stroke=accent, color=INK))
        # вузол-рік на хребті (для спареного 2007-го малюємо лише раз)
        if node:
            out.append(circle(spine_x, cy, r, fill="#ffffff", stroke="#6b7280", sw=2.2))
            out.append(text(spine_x, cy + 4, year, size=12, color=INK, bold=True))
        return out

    # хребет часу (до зеленого підсумку 2011)
    p.append(line(spine_x, 74, spine_x, 430, color="#c2c9d2", sw=2.4))

    # трек «спільне редагування» — синій; трек «доступність» — червоний
    p.extend(ev(102, "1987", "R",
                "1987 · епідемічні алгоритми (Demers, Xerox PARC)\nчутки й анти-ентропія: рознести оновлення без лідера",
                POS, RED_F))
    p.extend(ev(160, "1989", "L",
                "1989 · операційні перетворення (OT)\nEllis і Gibbs, редактор GROVE — правки як операції",
                NEG, BLUE_F))
    p.extend(ev(218, "1995", "R",
                "1995 · Bayou (Xerox PARC)\nприймати запис будь-де, узгоджувати згодом",
                POS, RED_F))
    p.extend(ev(276, "2006", "L",
                "2006 · WOOT — «WithOut OT»\nOster, Urso, Molli, Imine — стабільні позиції",
                NEG, BLUE_F))
    p.extend(ev(334, "2007", "L",
                "2007 · Commutative RDT\nShapiro, Preguiça — абревіатуру CRDT названо",
                NEG, BLUE_F))
    p.extend(ev(334, "2007", "R",
                "2007 · Dynamo (Amazon)\nсіблінги кошика: злиття перекладено на застосунок",
                POS, RED_F, node=False))
    p.extend(ev(392, "2009", "L",
                "2009 · Treedoc\nPreguiça, Marques, Shapiro, Letia — дерево позицій",
                NEG, BLUE_F))

    # обидві течії впадають у вузол 2011
    p.append(arrow(spine_x, 430, spine_x, 441, color="#9aa3ad", sw=2.0))

    # 2011 — зелений підсумок на всю ширину
    p.append(fitbox(150, 442, 640, 66,
                    "2011 · Conflict-free Replicated Data Types\nсильна кінцева узгодженість (SEC) · CvRDT + CmRDT об'єднано\nShapiro · Preguiça · Baquero · Zawirski",
                    size=13, pad=10, fill=GREEN_F, stroke=FIELD, color=INK, bold=True))
    p.append(arrow(spine_x, 508, spine_x, 528, color=FIELD, sw=2.0))
    # 2015 — дельта-варіант
    p.append(fitbox(250, 530, 440, 42,
                    "2015 · δ-CRDT (Almeida, Shoker, Baquero): слати лише дельту",
                    size=12.5, pad=9, fill=GREEN_F, stroke=FIELD, color=INK, bold=True))

    # легенда
    ly = 592.0
    p.append(rect(150, ly - 9, 16, 16, fill=BLUE_F, stroke=NEG, sw=1.6, rx=3))
    p.append(text(174, ly + 4, "спільне редагування", size=11.5, color=MUTED, anchor="start"))
    p.append(rect(392, ly - 9, 16, 16, fill=RED_F, stroke=POS, sw=1.6, rx=3))
    p.append(text(416, ly + 4, "доступність даних", size=11.5, color=MUTED, anchor="start"))
    p.append(rect(610, ly - 9, 16, 16, fill=GREEN_F, stroke=FIELD, sw=1.6, rx=3))
    p.append(text(634, ly + 4, "теорія CRDT", size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Дві течії сходяться: як визрів CRDT (1987–2015)")


# ── Фіг. 6 (math): алгебра ⟺ порядок — три закони і є об'єднання ─────────────────
# Ідея: зліва три алгебраїчні закони ⊔ (комут./асоц./ідемп.); вони означують
# відношення a⊑b ⟺ a⊔b=b, і справа воно постає як частковий порядок, де a⊔b —
# найменша верхня межа пари. Дві половини — той самий об'єкт.
def fig_algebra_order():
    W, H = 980, 430
    p = []

    def node(cx, cy, lab, accent=LINE, fill="#f4f6f8", r=26):
        return (circle(cx, cy, r, fill=fill, stroke=accent, sw=2.0) +
                text(cx, cy + 6, lab, size=14, color=accent, bold=True))

    # ── ліва панель: алгебра ──
    p.append(rect(40, 70, 360, 300, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=12))
    p.append(text(220, 102, "Алгебра", size=14.5, color=INK, bold=True))
    p.append(text(220, 168, "a ⊔ b = b ⊔ a", size=20, color=INK, bold=True))
    p.append(text(220, 190, "комутативність", size=11.5, color=MUTED))
    p.append(text(220, 250, "(a⊔b)⊔c = a⊔(b⊔c)", size=17, color=INK, bold=True))
    p.append(text(220, 272, "асоціативність", size=11.5, color=MUTED))
    p.append(text(220, 332, "a ⊔ a = a", size=20, color=INK, bold=True))
    p.append(text(220, 354, "ідемпотентність", size=11.5, color=MUTED))

    # ── місток посередині ──
    p.append(text(490, 120, "той самий об'єкт", size=12.5, color=MUTED, bold=True))
    p.append(text(490, 238, "⟺", size=48, color=FIELD, bold=True))
    b, _, _ = textbox(490, 330, "a ⊑ b  ⟺  a⊔b = b", size=14,
                      pad=10, fill="#eef7f0", stroke=FIELD, color=INK, bold=True)
    p.append(b)

    # ── права панель: порядок (діаграма Гассе) ──
    p.append(rect(580, 70, 360, 300, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=12))
    p.append(text(760, 102, "Порядок", size=14.5, color=INK, bold=True))
    p.append(text(760, 126, "join = найменша верхня межа", size=11.5, color=FIELD, bold=True))
    top = (760, 178); a = (688, 260); bb = (832, 260); bot = (760, 338)
    for u, v in [(bot, a), (bot, bb), (a, top), (bb, top)]:
        p.append(line(u[0], u[1], v[0], v[1], color="#b9c2cc", sw=1.8))
    p.append(node(*top, lab="a⊔b", accent=FIELD, fill="#eef7f0", r=30))
    p.append(node(*a, lab="a", accent=NEG))
    p.append(node(*bb, lab="b", accent=NEG))
    p.append(node(*bot, lab="⊥", accent=MUTED, r=22))

    render(os.path.join(OUT, "algebra-order.svg"), W, H, *p,
           title="Три закони ⊔ рівносильні порядку, де злиття — супремум пари")


# ── Фіг. 7 (math): лінеаризації сполучені перестановками паралельних ─────────────
# Ідея: причинний порядок a→c, b паралельна обом. Причинна доставка → порядок
# застосування є лінеаризацією цього порядку. Три лінеаризації, що поважають a→c,
# сполучені перестановкою пари ПАРАЛЕЛЬНИХ операцій; ті комутують — тож стан один.
def fig_linearizations():
    W, H = 1020, 480
    p = []

    # ── лівий бік: причинний порядок ──
    p.append(text(190, 120, "причинний порядок", size=13, color=INK, bold=True))
    p.append(text(190, 140, "на операціях {a, b, c}", size=12, color=MUTED))

    def onode(cx, cy, lab, accent=LINE, fill="#f4f6f8", r=27):
        return (circle(cx, cy, r, fill=fill, stroke=accent, sw=2.0) +
                text(cx, cy + 6, lab, size=17, color=accent, bold=True))

    p.append(arrow(155, 326, 155, 264, color=MUTED, sw=2.0))   # a → c
    p.append(onode(155, 235, "c", accent=LINE))
    p.append(onode(155, 353, "a", accent=LINE))
    p.append(onode(290, 294, "b", accent=NEG))
    p.append(text(155, 405, "a → c причинно", size=12, color=INK))
    p.append(text(338, 288, "b ∥ a,  b ∥ c", size=12, color=INK, anchor="start"))
    p.append(text(338, 306, "(паралельна обом)", size=11, color=MUTED, anchor="start"))

    # ── правий бік: три лінеаризації ──
    p.append(rect(560, 150, 400, 300, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=12))
    p.append(text(760, 178, "лінеаризації — порядки застосування O′", size=12.5,
                  color=INK, bold=True))

    bw, bh, gap = 52.0, 42.0, 8.0
    x0 = 700 - (bw * 3 + gap * 2) / 2

    def row(y, seq):
        out = []
        for i, ch in enumerate(seq):
            bx = x0 + i * (bw + gap)
            out.append(fitbox(bx, y, bw, bh, ch, size=18,
                              fill="#f4f6f8", stroke=LINE, color=INK, bold=True))
        return out

    p.extend(row(205, ["b", "a", "c"]))
    p.extend(row(305, ["a", "b", "c"]))
    p.extend(row(405, ["a", "c", "b"]))

    p.append(arrow(700, 249, 700, 303, color="#c7ced6", sw=1.8))
    p.append(arrow(700, 349, 700, 403, color="#c7ced6", sw=1.8))
    p.append(text(772, 282, "⇄ паралельні a, b", size=11.5, color=INK, anchor="start"))
    p.append(text(772, 382, "⇄ паралельні b, c", size=11.5, color=INK, anchor="start"))

    p.append(text(760, 468,
                  "усі три дають той самий стан: причинне ребро a → c збережене скрізь",
                  size=12, color=INK))

    render(os.path.join(OUT, "linearizations.svg"), W, H, *p,
           title="Лінеаризації сполучені перестановками паралельних операцій")


if __name__ == "__main__":
    fig_families()
    fig_gcounter()
    fig_semilattice()
    fig_orset()
    fig_timeline()
    fig_algebra_order()
    fig_linearizations()
    print("OK: figures written to", OUT)
