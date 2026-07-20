# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WARM = "#fdecea"   # заливка «погано»
COOL = "#e8f6ee"   # заливка «добре»
CALM = "#eaf0fd"   # заливка «нейтрально-холодне»


# ── 1. Тріщина: один рядок → два об'єкти → затерте оновлення ─────────────────
def fig_identity_crack():
    W, H = 1200, 740
    f = []

    f.append(text(W / 2, 40, "Один рядок, дві копії — і оплата зникає",
                  size=18, bold=True))

    # рядок бази ДО
    db, dbw, dbh = textbox(600, 112,
                           ["orders #42   (у базі ДО)",
                            "status = 'new'      discount = 0"],
                           size=13.5, bold=True, fill=CALM, stroke=NEG, sw=1.8,
                           min_w=460, pad=14)
    f.append(db)

    # розгалуження на два SELECT-и
    f.append(line(600, 112 + dbh / 2, 600, 200, color=LINE, sw=1.6))
    f.append(line(300, 200, 900, 200, color=LINE, sw=1.6))
    f.append(arrow(300, 200, 300, 262, color=LINE, sw=1.8))
    f.append(arrow(900, 200, 900, 262, color=LINE, sw=1.8))
    f.append(text(300, 182, "SELECT … WHERE id = 42", size=12, color=MUTED))
    f.append(text(900, 182, "SELECT … WHERE id = 42", size=12, color=MUTED))

    # два об'єкти
    a, aw, ah = textbox(300, 330,
                        ["order   (об'єкт A)",
                         "status   = 'paid'   ← змінили",
                         "discount = 0        (знімок)"],
                        size=13, fill=COOL, stroke=FIELD, sw=1.8,
                        min_w=340, pad=13)
    f.append(a)
    b, bw, bh = textbox(900, 330,
                        ["same   (об'єкт B)",
                         "status   = 'new'    (знімок)",
                         "discount = 15     ← змінили"],
                        size=13, fill=COOL, stroke=FIELD, sw=1.8,
                        min_w=340, pad=13)
    f.append(b)

    # «не той самий» — між боксами (проміжок 470…730)
    f.append(text(600, 322, "≠", size=34, bold=True, color=POS))
    f.append(text(600, 356, "order is same", size=11.5, color=MUTED))
    f.append(text(600, 374, "→ False", size=11.5, color=POS, bold=True))

    # два UPDATE-и
    f.append(arrow(300, 330 + ah / 2, 300, 452, color=POS, sw=1.8))
    f.append(arrow(900, 330 + bh / 2, 900, 452, color=POS, sw=1.8))

    u1, u1w, u1h = textbox(300, 500,
                           ["1. order.save()",
                            "SET status='paid', discount=0"],
                           size=12.5, fill=WARM, stroke=POS, sw=1.6,
                           min_w=340, pad=12)
    f.append(u1)
    u2, u2w, u2h = textbox(900, 500,
                           ["2. same.save()",
                            "SET status='new', discount=15"],
                           size=12.5, fill=WARM, stroke=POS, sw=1.6,
                           min_w=340, pad=12)
    f.append(u2)

    # злиття в результат
    f.append(line(300, 500 + u1h / 2, 300, 576, color=LINE, sw=1.6))
    f.append(line(900, 500 + u2h / 2, 900, 576, color=LINE, sw=1.6))
    f.append(line(300, 576, 900, 576, color=LINE, sw=1.6))
    f.append(arrow(600, 576, 600, 618, color=LINE, sw=1.8))

    res, rw, rh = textbox(600, 664,
                          ["orders #42   (у базі ПІСЛЯ)",
                           "status = 'new'   ← 'paid' затерто",
                           "discount = 15"],
                          size=13.5, bold=True, fill=WARM, stroke=POS, sw=2.2,
                          min_w=480, pad=14)
    f.append(res)

    f.append(text(600, 726,
                  "Обидва UPDATE законні, транзакція одна — базі нема на що скаржитися",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'identity-crack.svg'), W, H, *f)


# ── 2. Вузьке горло: усе завантаження проходить через мапу ───────────────────
def fig_map_lookup():
    W, H = 1240, 700
    f = []

    f.append(text(W / 2, 40, "Мапа на шляху завантаження: другому об'єктові ніде народитися",
                  size=17, bold=True))

    CX = 400          # центр колонки-блоксхеми

    # вхід
    inb, inw, inh = textbox(CX, 100,
                            "будь-який шлях завантаження (Order, 42)",
                            size=13, bold=True, fill=CALM, stroke=NEG, sw=1.8, pad=13)
    f.append(inb)
    f.append(text(CX, 68, "за ключем · через зв'язок · із результату запиту",
                  size=11.5, color=MUTED))
    f.append(arrow(CX, 100 + inh / 2, CX, 178, color=LINE, sw=1.8))

    # рішення
    dec, dw, dh = textbox(CX, 212, "(Order, 42) вже у мапі?",
                          size=13.5, bold=True, fill=FILL, stroke=INK, sw=2, pad=14)
    f.append(dec)

    # ── гілка «так» — ліворуч
    f.append(arrow(CX - dw / 2, 212, 210, 212, color=FIELD, sw=1.9))
    f.append(text((CX - dw / 2 + 210) / 2, 194, "ТАК", size=11.5, bold=True, color=FIELD))
    hit, hw, hh = textbox(120, 212, ["влучання:", "віддати той", "самий об'єкт"],
                          size=12.5, bold=True, fill=COOL, stroke=FIELD, sw=1.8, pad=12)
    f.append(hit)
    f.append(text(120, 212 + hh / 2 + 24, "жодного SELECT,", size=11, color=MUTED))
    f.append(text(120, 212 + hh / 2 + 40, "жодного об'єкта", size=11, color=MUTED))

    # ── гілка «ні» — донизу
    f.append(arrow(CX, 212 + dh / 2, CX, 298, color=POS, sw=1.9))
    f.append(text(CX + 46, 262, "НІ", size=11.5, bold=True, color=POS))

    sel, sw_, sh = textbox(CX, 334, "SELECT … WHERE id = 42",
                           size=12.5, fill=WARM, stroke=POS, sw=1.6, min_w=330, pad=12)
    f.append(sel)
    f.append(arrow(CX, 334 + sh / 2, CX, 412, color=LINE, sw=1.8))

    bld, bw, bh = textbox(CX, 448, "зібрати об'єкт із рядка",
                          size=12.5, fill=FILL, stroke=LINE, sw=1.6, min_w=330, pad=12)
    f.append(bld)
    f.append(arrow(CX, 448 + bh / 2, CX, 526, color=LINE, sw=1.8))

    reg, rw, rh = textbox(CX, 562, "зареєструвати: (Order, 42) → об'єкт",
                          size=12.5, bold=True, fill=COOL, stroke=FIELD, sw=2, min_w=330, pad=12)
    f.append(reg)
    f.append(arrow(CX, 562 + rh / 2, CX, 632, color=LINE, sw=1.8))

    out, ow, oh = textbox(CX, 662, "віддати новий об'єкт",
                          size=12.5, fill=CALM, stroke=NEG, sw=1.6, min_w=330, pad=11)
    f.append(out)

    # ── сама мапа праворуч
    MX = 950
    f.append(rect(770, 150, 400, 300, fill="#fbfbfd", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(MX, 182, "МАПА СЕСІЇ", size=13.5, bold=True, color=INK))
    f.append(text(MX, 204, "ключ — ПАРА (тип, первинний ключ)", size=11, color=MUTED))

    rows = [("(Order, 42)", "Order#42"),
            ("(Order, 43)", "Order#43"),
            ("(Customer, 7)", "Customer#7")]
    for i, (k, v) in enumerate(rows):
        ry = 250 + i * 62
        kb, kw, kh = textbox(872, ry, k, size=12, fill="#ffffff", stroke=NEG,
                             sw=1.5, min_w=150, pad=9)
        f.append(kb)
        f.append(arrow(872 + kw / 2 + 4, ry, 1020, ry, color=MUTED, sw=1.5))
        vb, vw, vh = textbox(1090, ry, v, size=12, fill=COOL, stroke=FIELD,
                             sw=1.5, min_w=120, pad=9)
        f.append(vb)

    # зв'язки блоксхеми з мапою
    f.append(arrow(CX + dw / 2, 224, 770, 290, color=MUTED, sw=1.5))
    f.append(text(640, 242, "пошук", size=11.5, color=MUTED, bold=True))

    f.append(arrow(CX + rw / 2, 550, 770, 420, color=FIELD, sw=1.5))
    f.append(text(660, 500, "запис", size=11.5, color=FIELD, bold=True))

    f.append(text(MX, 490, "На пару (тип, ключ) — рівно один об'єкт,", size=12, color=INK))
    f.append(text(MX, 510, "скільки б шляхів до нього не вело.", size=12, color=INK))

    render(os.path.join(IMG, 'map-lookup.svg'), W, H, *f)


# ── 3. Межа життя мапи: сесія проти застосунку ──────────────────────────────
def fig_map_scope():
    W, H = 1320, 600
    f = []

    f.append(text(W / 2, 38, "Та сама структура даних: у межах сесії — гарантія, на весь застосунок — кеш",
                  size=17, bold=True))

    # ══ ЛІВОРУЧ: мапа в межах сесії ═══════════════════════════════════════
    f.append(rect(40, 66, 590, 500, fill="#fbfefc", stroke=FIELD, sw=2, rx=12))
    f.append(text(335, 100, "МАПА В МЕЖАХ СЕСІЇ", size=14.5, bold=True, color=FIELD))

    for cx, name in ((190, "A"), (480, "B")):
        f.append(rect(cx - 100, 124, 200, 116, fill="#ffffff", stroke=MUTED, sw=1.6, rx=8))
        f.append(text(cx, 150, "Запит " + name, size=12.5, bold=True, color=INK))
        mb, mw, mh = textbox(cx, 200, "мапа " + name, size=12,
                             fill=COOL, stroke=FIELD, sw=1.6, min_w=130, pad=10)
        f.append(mb)

    f.append(text(335, 268, "мапи не перетинаються й не переживають запит",
                  size=11.5, color=MUTED, italic=True))

    for i, s in enumerate(["живе рівно стільки, скільки одиниця роботи",
                           "несвіжість ≤ тривалість одного запиту",
                           "нічого не ділиться — замки не потрібні",
                           "інвалідувати нічого: зникає разом із сесією"]):
        f.append(text(72, 308 + i * 28, "·  " + s, size=12, color=INK, anchor="start"))

    f.append(fitbox(80, 442, 510, 74,
                    ["ГАРАНТІЯ ТОТОЖНОСТІ", "умова правильності, а не оптимізація"],
                    size=14, fill=COOL, stroke=FIELD, sw=2.2, bold=True, color=FIELD))

    # ══ ПРАВОРУЧ: мапа на весь застосунок ═════════════════════════════════
    f.append(rect(690, 66, 590, 500, fill="#fffcfc", stroke=POS, sw=2, rx=12))
    f.append(text(985, 100, "МАПА НА ВЕСЬ ЗАСТОСУНОК", size=14.5, bold=True, color=POS))

    for cx, name in ((840, "A"), (1130, "B")):
        f.append(rect(cx - 90, 124, 180, 54, fill="#ffffff", stroke=MUTED, sw=1.6, rx=8))
        f.append(text(cx, 156, "Запит " + name, size=12.5, bold=True, color=INK))

    f.append(arrow(840, 178, 940, 222, color=POS, sw=1.8))
    f.append(arrow(1130, 178, 1030, 222, color=POS, sw=1.8))

    sb, sbw, sbh = textbox(985, 250, "СПІЛЬНА МАПА", size=13, bold=True,
                           fill=WARM, stroke=POS, sw=2, min_w=230, pad=11)
    f.append(sb)

    f.append(text(985, 292, "одна на всіх — і назавжди",
                  size=11.5, color=MUTED, italic=True))

    for i, s in enumerate(["друге джерело правди — несвіжість безмежна",
                           "чужі напівзмінені об'єкти течуть між запитами",
                           "кілька потоків одночасно — потрібні замки",
                           "з'являється окрема задача інвалідації"]):
        f.append(text(722, 336 + i * 28, "·  " + s, size=12, color=INK, anchor="start"))

    f.append(fitbox(730, 460, 510, 74,
                    ["ЦЕ ВЖЕ КЕШ", "з усією його ціною — і це вже інший патерн"],
                    size=14, fill=WARM, stroke=POS, sw=2.2, bold=True, color=POS))

    render(os.path.join(IMG, 'map-scope.svg'), W, H, *f)


# ── 4. Розгортка: скінченний граф → нескінченне дерево шляхів ────────────────
def fig_unfolding():
    W, H = 1220, 690
    f = []

    f.append(text(W / 2, 40, "Без мапи спуск будує не граф, а дерево його шляхів",
                  size=18, bold=True))

    f.append(line(580, 72, 580, 590, color=MUTED, sw=1.4, dash="6,5"))

    # ── ліворуч: граф бази ───────────────────────────────────────────────
    f.append(text(285, 96, "Граф бази — скінченний", size=14.5, bold=True, color=NEG))

    o42, ow, oh = textbox(285, 185, ["orders #42", "customer_id = 7"],
                          size=12.5, fill=CALM, stroke=NEG, sw=1.8,
                          min_w=220, pad=11)
    f.append(o42)
    c7, cw, ch = textbox(285, 405, ["customers #7", "orders ∋ #42"],
                         size=12.5, fill=CALM, stroke=NEG, sw=1.8,
                         min_w=220, pad=11)
    f.append(c7)

    f.append(arrow(230, 185 + oh / 2, 230, 405 - ch / 2, color=LINE, sw=1.8))
    f.append(arrow(340, 405 - ch / 2, 340, 185 + oh / 2, color=LINE, sw=1.8))
    f.append(text(208, 299, "потрібен клієнт", size=11.5, color=MUTED, anchor="end"))
    f.append(text(362, 299, "потрібні замовлення", size=11.5, color=MUTED, anchor="start"))

    f.append(text(285, 492, "2 вузли · 2 ребра · цикл", size=13.5, bold=True))
    f.append(text(285, 516, "усе, що є в базі", size=12, color=MUTED, italic=True))

    # ── праворуч: розгортка ──────────────────────────────────────────────
    f.append(text(890, 96, "Розгортка з кореня #42 — нескінченна",
                  size=14.5, bold=True, color=POS))

    prev = None
    bh = 0
    rows = [(160, "orders #42"), (250, "customers #7"),
            (340, "orders #42"), (430, "customers #7")]
    for y, lab in rows:
        b, bw, bh = textbox(890, y, lab, size=12.5, fill=WARM, stroke=POS,
                            sw=1.6, min_w=200, pad=9)
        f.append(b)
        if prev is not None:
            f.append(arrow(890, prev + bh / 2, 890, y - bh / 2, color=POS, sw=1.7))
        prev = y

    f.append(arrow(890, 430 + bh / 2, 890, 478, color=POS, sw=1.7))
    f.append(text(890, 506, "⋮", size=30, bold=True, color=POS))
    f.append(text(890, 540, "кожен виток — новий об'єкт і новий SELECT",
                  size=12, color=MUTED, italic=True))

    f.append(fitbox(60, 606, 1100, 66,
                    ["Розгортка скінченна  ⟺  з кореня не досяжний ЖОДЕН цикл",
                     "цикл #42 → #7 → #42 досяжний, тож дерево шляхів нескінченне — а з ним і рекурсія"],
                    size=13.5, fill=WARM, stroke=POS, sw=2.2, bold=True, color=POS))

    render(os.path.join(IMG, 'unfolding.svg'), W, H, *f)


# ── 5. Реєстрація до спуску: що саме робить спуск скінченним ─────────────────
def fig_register_order():
    W, H = 1340, 775
    f = []

    f.append(text(W / 2, 40, "Той самий код, різний порядок двох рядків — і різна скінченність",
                  size=18, bold=True))

    panels = [
        (40, POS, WARM, "ХИБНО: реєстрація ПІСЛЯ зв'язків",
         [("row = SELECT(k)", ""),
          ("o   = allocate(row)", ""),
          ("for k' in refs(row):", "← спуск"),
          ("    o.link(load(k'))", ""),
          ("M[k] = o", "← реєстрація")],
         "Спуск на циклі #42 ⇄ #7:",
         [(0, "load(#42)   M = {}", INK, ""),
          (1, "load(#7)    M = {}", INK, ""),
          (2, "load(#42)   M = {}", POS, "← та сама діра"),
          (3, "load(#7)    M = {}", POS, ""),
          (4, "⋮", POS, "")],
         ["M[k] не встигає заповнитися ДО спуску,",
          "тож влучання не стається ніколи → переповнення стека"]),
        (700, FIELD, COOL, "ПРАВИЛЬНО: реєстрація ДО зв'язків",
         [("row = SELECT(k)", ""),
          ("o   = allocate(row)", ""),
          ("M[k] = o", "← реєстрація"),
          ("for k' in refs(row):", "← спуск"),
          ("    o.link(load(k'))", "")],
         "Спуск на тому самому циклі:",
         [(0, "load(#42)   M = {}         → M = {42}", INK, ""),
          (1, "load(#7)    M = {42}       → M = {42, 7}", INK, ""),
          (2, "load(#42)   M = {42, 7}    → ВЛУЧАННЯ", FIELD, ""),
          (3, "віддає o42 — сірий, зв'язки ще не всі", MUTED, ""),
          (0, "коло замкнулося · 2 SELECT-и · кінець", FIELD, "")],
         ["Реєстрація сталася ДО спуску,",
          "тож другий прихід за #42 упирається в мапу → скінченно"]),
    ]

    for px, accent, wash, header, code, tracelab, trace, verdict in panels:
        f.append(rect(px, 70, 600, 545, fill="#ffffff", stroke=accent, sw=2.2, rx=10))
        f.append(text(px + 300, 104, header, size=14.5, bold=True, color=accent))

        for i, (ln, note) in enumerate(code):
            y = 144 + i * 28
            f.append(text(px + 28, y, ln, size=12.5, anchor="start", color=INK))
            if note:
                f.append(text(px + 330, y, note, size=11.5, anchor="start",
                              color=accent, bold=True))

        f.append(line(px + 24, 296, px + 576, 296, color=MUTED, sw=1.2, dash="5,4"))
        f.append(text(px + 28, 322, tracelab, size=12.5, anchor="start",
                      bold=True, color=MUTED))

        for i, (depth, ln, col, note) in enumerate(trace):
            y = 352 + i * 26
            f.append(text(px + 28 + depth * 22, y, ln, size=12,
                          anchor="start", color=col))
            if note:
                f.append(text(px + 430, y, note, size=11, anchor="start",
                              color=col, bold=True))

        f.append(fitbox(px + 24, 502, 552, 92, verdict, size=13,
                        fill=wash, stroke=accent, sw=2, bold=True, color=accent))

    # ── нижня смуга: три кольори ─────────────────────────────────────────
    f.append(rect(40, 636, 1260, 116, fill=CALM, stroke=NEG, sw=2, rx=8))
    f.append(text(670, 666, "Три стани вузла у спуску", size=13.5, bold=True, color=NEG))

    for cx, fillc, lab in ((150, "#ffffff", "білий — ще не бачили"),
                           (500, "#9aa3af", "сірий — зареєстрований, зв'язки ще ні"),
                           (920, "#1a1a1a", "чорний — добудований")):
        f.append(circle(cx, 698, 13, fill=fillc, stroke=LINE, sw=1.8))
        f.append(text(cx + 24, 703, lab, size=12, anchor="start", color=INK))

    f.append(text(670, 736,
                  "Мапа мусить ловити СІРИХ. Реєстрація після зв'язків фарбує лише чорних — "
                  "а на циклі до чорного не доходить ніколи.",
                  size=12.5, color=POS, bold=True))

    render(os.path.join(IMG, 'register-order.svg'), W, H, *f)


# ── 6. Бієкція ключ ↔ об'єкт і дві її поломки ───────────────────────────────
def fig_bijection():
    W, H = 1320, 580
    f = []

    f.append(text(W / 2, 38, "Інваріант тотожності: мапа — бієкція, і ламається вона з двох боків",
                  size=17.5, bold=True))

    f.append(line(450, 66, 450, 520, color=MUTED, sw=1.4, dash="6,5"))
    f.append(line(880, 66, 880, 520, color=MUTED, sw=1.4, dash="6,5"))

    def keybox(x, y, s, accent):
        b, w, h = textbox(x, y, s, size=12, fill="#ffffff", stroke=accent,
                          sw=1.8, min_w=140, pad=9)
        return b

    def objdot(x, y, s, accent):
        return (circle(x, y, 24, fill="#ffffff", stroke=accent, sw=1.8)
                + text(x, y + 5, s, size=13, bold=True, color=accent))

    panels = [
        (230, FIELD, COOL, "ЦІЛА", "функція + ін'єкція",
         [("(Order, 42)", 200), ("(Order, 58)", 292)],
         [("o₁", 200), ("o₂", 292)],
         [(200, 200), (292, 292)],
         "бієкція dom(M) → im(M)",
         ["a is b   ⇔   той самий рядок",
          "порівняння за посиланням стає",
          "перевіркою тотожності рядка"]),
        (660, POS, WARM, "ДВІЙНИК", "порушена функційність",
         [("(Order, 42)", 246)],
         [("o₁", 200), ("o₂", 292)],
         [(246, 200), (246, 292)],
         "M — уже не функція",
         ["a is b = False для ОДНОГО рядка",
          "два знімки, два UPDATE-и,",
          "друге затирає перше"]),
        (1090, POS, WARM, "ЗЛИТТЯ", "порушена ін'єктивність",
         [("(Order, 42)", 200), ("(Order, 58)", 292)],
         [("o₁", 246)],
         [(200, 246), (292, 246)],
         "M — уже не ін'єкція",
         ["a is b = True для РІЗНИХ рядків",
          "стереже незмінність ключа:",
          "змінив pk у мапі — злив дві сутності"]),
    ]

    for cx, accent, wash, title_, sub, keys, objs, links, verdict, notes in panels:
        kx, ox = cx - 95, cx + 92

        f.append(text(cx, 92, title_, size=15, bold=True, color=accent))
        f.append(text(cx, 114, sub, size=11.5, color=MUTED, italic=True))

        f.append(text(kx, 158, "ключі K", size=12, bold=True, color=MUTED))
        f.append(text(ox, 158, "об'єкти O", size=12, bold=True, color=MUTED))

        for s, y in keys:
            f.append(keybox(kx, y, s, accent))
        for s, y in objs:
            f.append(objdot(ox, y, s, accent))
        for ky, oy in links:
            f.append(arrow(kx + 74, ky, ox - 30, oy, color=accent, sw=1.8))

        f.append(fitbox(cx - 190, 340, 380, 46, verdict, size=13,
                        fill=wash, stroke=accent, sw=2, bold=True, color=accent))

        for i, n in enumerate(notes):
            f.append(text(cx, 424 + i * 24, n, size=11.5, color=INK))

    render(os.path.join(IMG, 'bijection.svg'), W, H, *f)


# ── 7. Дисципліна досяжності: хто кого тримає ───────────────────────────────
import math


def _weak_arrow(x1, y1, x2, y2, color=MUTED, sw=1.7):
    """Пунктирна стрілка: arrow() пунктиру не вміє, тож вістря малюємо самі."""
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 10 * math.cos(ang), y2 - 10 * math.sin(ang)
    out = line(x1, y1, hx, hy, color=color, sw=sw, dash="7,5")
    ax, ay = hx + 5 * math.sin(ang), hy - 5 * math.cos(ang)
    bx, by = hx - 5 * math.sin(ang), hy + 5 * math.cos(ang)
    out += ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
            % (x2, y2, ax, ay, bx, by, color))
    return out


def fig_refs_discipline():
    W, H = 1300, 786
    f = []

    f.append(text(W / 2, 40, "Хто тримає об'єкт живим — той і вирішує, коли він помре",
                  size=18, bold=True))
    f.append(text(W / 2, 66,
                  "той самий об'єкт, та сама мапа — різниця лише в тому, чи встигли його змінити",
                  size=12.5, color=MUTED, italic=True))

    def panel(ox, header, accent, bg, dirty):
        g = []
        g.append(rect(ox, 88, 600, 596, fill=bg, stroke=accent, sw=2, rx=12))
        g.append(text(ox + 300, 124, header, size=15, bold=True, color=accent))
        g.append(text(ox + 300, 150,
                      "об'єкт змінили — і сесія про це вже знає" if dirty
                      else "об'єкт лише прочитали й нічого не чіпали",
                      size=11.5, color=MUTED))

        for label, hy, live in (("код запиту", 218, True),
                                ("мапа сесії", 318, True),
                                ("одиниця роботи", 418, dirty)):
            b, bw, bh = textbox(ox + 132, hy, label, size=12.5, bold=True,
                                fill="#ffffff" if live else FILL,
                                stroke=LINE if live else MUTED,
                                sw=1.6, min_w=184, pad=10,
                                color=INK if live else MUTED)
            g.append(b)

        g.append(text(ox + 132, 456,
                      "тут лежить цей об'єкт" if dirty else "порожня — писати нічого",
                      size=10.5, color=MUTED, italic=True))

        ob, ow, oh = textbox(ox + 452, 318,
                             ["Order #42", "status = 'paid'" if dirty else "status = 'new'"],
                             size=13, bold=True, fill=CALM if dirty else COOL,
                             stroke=accent, sw=2, min_w=192, pad=12)
        g.append(ob)

        L, R = ox + 228, ox + 352
        g.append(arrow(L, 218, R, 294, color=INK, sw=2))
        g.append(_weak_arrow(L, 318, R, 318))
        if dirty:
            g.append(arrow(L, 418, R, 342, color=accent, sw=2.4))
        # чиста колонка: одиниця роботи цього об'єкта не тримає — стрілки просто нема

        verdict = (["код відпустив об'єкт —",
                    "а одиниця роботи ще тримає.",
                    "Об'єкт живе до commit(), і лише коли",
                    "списки почистять — аж тоді помирає."]
                   if dirty else
                   ["код відпустив об'єкт —",
                    "і сильних посилань не лишилось.",
                    "Об'єкт помирає негайно, а мапа",
                    "прибирає порожню комірку сама."])
        g.append(fitbox(ox + 44, 498, 512, 110, verdict, size=13,
                        fill="#ffffff", stroke=accent, sw=2, color=INK))

        g.append(text(ox + 300, 646, "ЗМІНИ ДОЖИЛИ ДО ЗАПИСУ" if dirty else "ПАМ'ЯТЬ ВІЛЬНА",
                      size=13.5, bold=True, color=accent))
        return g

    f += panel(40, "ЧИСТИЙ ОБ'ЄКТ", FIELD, "#fbfefc", False)
    f += panel(660, "БРУДНИЙ ОБ'ЄКТ", NEG, "#fafbff", True)

    f.append(line(290, 712, 356, 712, color=INK, sw=2.4))
    f.append(text(366, 717, "сильне посилання — тримає об'єкт живим",
                  size=12, color=INK, anchor="start"))
    f.append(line(770, 712, 836, 712, color=MUTED, sw=1.7, dash="7,5"))
    f.append(text(846, 717, "слабке — не тримає", size=12, color=MUTED, anchor="start"))

    f.append(text(W / 2, 760,
                  "Список того, що треба записати, і список того, що треба тримати живим, — це один список.",
                  size=13.5, bold=True, color=INK))

    render(os.path.join(IMG, 'refs-discipline.svg'), W, H, *f)


# ── 8. Коли сесія дізнається про бруд ───────────────────────────────────────
def fig_dirty_timing():
    W, H = 1300, 766
    f = []

    f.append(text(W / 2, 40,
                  "Коли сесія дізнається про зміну — і чому від цього залежить сила посилання",
                  size=17.5, bold=True))
    f.append(text(W / 2, 66, "той самий код, дві механіки стеження за змінами",
                  size=12.5, color=MUTED, italic=True))

    def band(oy, header, sub, accent, segs, ticks, note, note_x):
        g = []
        g.append(rect(40, oy, 1220, 296, fill="#fcfcfd", stroke=accent, sw=1.8, rx=12))
        g.append(text(70, oy + 34, header, size=14, bold=True, color=accent, anchor="start"))
        g.append(text(70, oy + 56, sub, size=11.5, color=MUTED, anchor="start"))

        nb, nw, nh = textbox(note_x, oy + 102, note, size=11.5, bold=True,
                             fill="#ffffff", stroke=accent, sw=1.6, pad=10)
        g.append(nb)

        bar_y, bar_h = oy + 136, 50
        for x1, x2, label, fillc in segs:
            g.append(fitbox(x1, bar_y, x2 - x1, bar_h, label, size=12,
                            fill=fillc, stroke=MUTED, sw=1.4, pad=10))

        ax_y = oy + 220
        g.append(arrow(110, ax_y, 1196, ax_y, color=MUTED, sw=1.5))
        g.append(text(1212, ax_y + 5, "час", size=11, color=MUTED, anchor="start"))

        for tx, l1, l2 in ticks:
            g.append(line(tx, bar_y + bar_h, tx, ax_y - 7, color=MUTED, sw=1.2, dash="3,4"))
            g.append(circle(tx, ax_y, 5, fill=accent, stroke=accent, sw=1))
            g.append(text(tx, ax_y + 28, l1, size=11.5, bold=True, color=INK))
            g.append(text(tx, ax_y + 46, l2, size=11, color=MUTED))
        return g

    f += band(88,
              "ПЕРЕХОПЛЕНЕ ПРИСВОЄННЯ — так це робить SQLAlchemy",
              "присвоєння перехоплює пастка: сесія дізнається про бруд у ту саму мить",
              FIELD,
              [(240, 600, "чистий · у мапі слабко", COOL),
               (600, 980, "брудний · одиниця роботи тримає сильно", CALM),
               (980, 1200, "чистий · знову слабко", COOL)],
              [(240, "load(Order, 42)", "об'єкт у мапі"),
               (600, "order.status = 'paid'", "пастка спрацювала"),
               (980, "commit()", "списки чистять")],
              ["тут дізнались — тут і втримали:", "вікна небезпеки немає"], 600)

    f += band(420,
              "ЗНІМОК-ЗВІРКА — так це робить Hibernate",
              "присвоєння ніхто не перехоплює: бруд знайдеться аж на flush, коли звірять зі знімком",
              POS,
              [(240, 600, "чистий · знімок стану збережено", COOL),
               (600, 980, "брудний — і ніхто про це не знає", WARM),
               (980, 1200, "звірка зі знімком → UPDATE", COOL)],
              [(240, "load(Order, 42)", "+ знімок стану"),
               (600, "order.status = 'paid'", "тиша"),
               (980, "flush()", "аж тепер звірка")],
              ["вікно, у якому слабка мапа", "втратила б зміни мовчки"], 790)

    f.append(text(W / 2, 744,
                  "Втримати можна лише те, про що знаєш. Хто дізнається аж на flush — мусить тримати сильно все.",
                  size=13.5, bold=True, color=INK))

    render(os.path.join(IMG, 'dirty-timing.svg'), W, H, *f)


# ── 9. Родовід: звідки прийшла карта тотожності й де обірвалася гілка ────────
def fig_lineage():
    W, H = 1300, 1010
    f = []

    f.append(text(W / 2, 40, "Родовід карти тотожності: три гілки й одна обірвана",
                  size=18, bold=True))
    f.append(text(W / 2, 66,
                  "назва старша за книжку, інваріант старший за назву, а гілка без сесії не прижилася",
                  size=12.5, color=MUTED, italic=True))

    SPINE = 250
    f.append(line(SPINE, 100, SPINE, 952, color=MUTED, sw=2))

    C_TOP = "#eaf0fd"   # гілка TopLink / Смолток
    C_HIB = "#e8f6ee"   # гілка Hibernate
    C_CAN = "#f4f6f8"   # канон: книжка і стандарт
    C_RAI = "#fdecea"   # гілка Rails

    rows = [
        ("1986", C_TOP, "«Object Identity» — доповідь на OOPSLA, Портленд",
                        "Сетраг Хошафян і Джордж Коупленд: тотожність — не поле, а окрема властивість"),
        ("1994", C_TOP, "TOPLink для Смолтока — перший промисловий ORM",
                        "The Object People, Оттава; «TOP» у назві — це самі The Object People"),
        ("1997", C_TOP, "Біла книга TOPLink 4.0: інваріант записано словами",
                        "«один первинний ключ — рівно один об'єкт в іміджі»; Unit of Work — щойно доданий"),
        ("1999", C_TOP, "FullIdentityMap · WeakIdentityMap · NoIdentityMap",
                        "назва «identity map» уже в класах API — за три роки до книжки"),
        ("2000", C_TOP, "GLORP: «запит адресують сесії, а не класу»",
                        "Алан Найт, головний архітектор TOPLink, називає розвилку вголос"),
        ("2001", C_HIB, "Hibernate: сесія як карта тотожності",
                        "Гевін Кінг, 23 травня; Session → Map<EntityKey, Object>"),
        ("2002", C_CAN, "PoEAA: назву записано — і розсуджено суперечку",
                        "5 листопада, Мартін Фаулер: тотожність — головне, кеш — побічне"),
        ("2006", C_CAN, "JPA: інваріант стає нормою стандарту",
                        "обидві гілки за одним столом: Майк Кіт (TopLink) і Гевін Кінг (Hibernate)"),
        ("2010", C_RAI, "Ruby Summer of Code, проєкт №12: мапа для Rails",
                        "Марцін Рачковський (Краків), ментор Еміліо Тагуа (Мендоса)"),
        ("2011", C_RAI, "Rails 3.1: мапа є — але вимкнена за замовчуванням",
                        "9 травня вимкнув, 10 травня описав чому: мапа не стежить за зв'язками"),
        ("2012", C_RAI, "«Remove IdentityMap»: 33 файли, −966 рядків",
                        "сам патерн — 144 рядки; решта 820 — гачки, розповзлі по Active Record"),
        ("2013", C_RAI, "Rails 4.0 виходить без мапи",
                        "фрагменти в публічному API доживуть аж до 2014-го"),
    ]

    y0, pitch = 128, 74
    for i, (year, fill, head, sub) in enumerate(rows):
        y = y0 + i * pitch
        f.append(rect(300, y - 30, 880, 60, fill=fill, stroke=LINE, sw=1.5))
        f.append(circle(SPINE, y, 8, fill=fill, stroke=LINE, sw=2))
        f.append(line(SPINE + 8, y, 300, y, color=MUTED, sw=1.4))
        f.append(text(150, y + 6, year, size=16, bold=True))
        f.append(text(320, y - 6, head,
                      size=fit_font(head, 840, 14, True), bold=True, anchor="start"))
        f.append(text(320, y + 17, sub,
                      size=fit_font(sub, 840, 12, False), color=MUTED, anchor="start"))

    f.append(text(W / 2, 985,
                  "Гілки, що вижили, несли мапу разом із сесією. Гілка, що взяла саму мапу, всохла.",
                  size=13.5, bold=True, color=INK))

    render(os.path.join(IMG, 'lineage.svg'), W, H, *f)


# ── 10. Кому належить мапа: сесія-власниця проти нічийного графа ─────────────
def fig_ownership():
    W, H = 1300, 790
    f = []

    f.append(text(W / 2, 40, "Чому та сама мапа тримає в Hibernate і руйнує в Rails",
                  size=18, bold=True))
    f.append(text(W / 2, 66, "річ не в якості мапи, а в тому, чи є кому володіти графом",
                  size=12.5, color=MUTED, italic=True))

    # ── ЛІВА панель: сесія володіє всім ──
    f.append(rect(40, 96, 600, 560, fill="#fcfcfd", stroke=FIELD, sw=2, rx=12))
    f.append(text(70, 130, "СЕСІЯ ВОЛОДІЄ ВСІМ — TopLink · Hibernate · JPA",
                  size=13.5, bold=True, color=FIELD, anchor="start"))

    b, _, _ = textbox(340, 176, "session.get(Order, 42)", size=13, bold=True,
                      fill="#ffffff", stroke=MUTED, sw=1.5, pad=10)
    f.append(b)
    f.append(arrow(340, 196, 340, 228, color=LINE, sw=1.8))

    f.append(rect(80, 228, 520, 300, fill=COOL, stroke=FIELD, sw=1.8, rx=10))
    f.append(text(340, 256, "Сесія · контекст персистентності", size=13.5, bold=True))
    for i, s in enumerate([
        "карта тотожності:  (тип, ключ) → об'єкт",
        "одиниця роботи:  список змінених об'єктів",
        "колекції зв'язків — обгорнуті сесією",
        "порядок flush — теж її рішення",
    ]):
        f.append(fitbox(104, 278 + i * 58, 472, 44, s, size=12.5,
                        fill="#ffffff", stroke=MUTED, sw=1.3, pad=10))

    f.append(fitbox(80, 552, 520, 76,
                    ["Симетрію зв'язків тримає розробник — за правилом,",
                     "оголошеним із першого дня. Але правило Є КОМУ адресувати:",
                     "у графа є власник."],
                    size=12.5, fill="#ffffff", stroke=FIELD, sw=1.6, pad=10))

    # ── ПРАВА панель: мапу нема кому віддати ──
    f.append(rect(660, 96, 600, 560, fill="#fcfcfd", stroke=POS, sw=2, rx=12))
    f.append(text(690, 130, "ГРАФ — НІЧИЙ — Active Record", size=13.5, bold=True,
                  color=POS, anchor="start"))

    b2, _, _ = textbox(960, 176, "Post.find(42)   ← класовий метод", size=13, bold=True,
                       fill="#ffffff", stroke=MUTED, sw=1.5, pad=10)
    f.append(b2)
    f.append(text(960, 212, "сесії, якій це адресувати, не існує", size=11.5,
                  color=MUTED, italic=True))
    f.append(arrow(960, 224, 960, 256, color=POS, sw=1.8))

    f.append(fitbox(700, 256, 520, 62,
                    ["Thread.current[:identity_map]",
                     "глобальна змінна з гарною назвою + middleware на запит"],
                    size=12.5, fill=WARM, stroke=POS, sw=1.8, pad=10))

    f.append(arrow(960, 318, 960, 350, color=POS, sw=1.8))

    f.append(fitbox(700, 350, 520, 62,
                    ["@post.comments — запам'ятано на самому об'єкті",
                     "мапа про цю колекцію не знає й не інвалідує її"],
                    size=12.5, fill=WARM, stroke=POS, sw=1.8, pad=10))

    f.append(arrow(960, 412, 960, 444, color=POS, sw=1.8))

    f.append(fitbox(700, 444, 520, 84,
                    ["Поки мапи не було, ДРУГА КОПІЯ перечитувала колекцію —",
                     "і саме вона, непомітно, тримала граф свіжим.",
                     "Мапа прибрала копію — і разом із нею перечитування."],
                    size=12.5, fill="#ffffff", stroke=POS, sw=1.6, pad=10))

    f.append(fitbox(660 + 20, 552, 520, 76,
                    ["Правило «тримай обидва боки зв'язку» тут ніколи не було потрібне —",
                     "тож десять років коду його не знає. Мапа створила потребу",
                     "в правилі заднім числом."],
                    size=12.5, fill="#ffffff", stroke=POS, sw=1.6, pad=10))

    f.append(text(W / 2, 700,
                  "Карта тотожності — не деталь, яку доставляють. Це властивість архітектури, у якої є сесія.",
                  size=14, bold=True, color=INK))
    f.append(text(W / 2, 730,
                  "Hibernate теж не стежить за зв'язками. Різниця в тому, що там є кому за них відповідати.",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, 'ownership.svg'), W, H, *f)


if __name__ == '__main__':
    fig_identity_crack()
    fig_map_lookup()
    fig_map_scope()
    fig_unfolding()
    fig_register_order()
    fig_bijection()
    fig_refs_discipline()
    fig_dirty_timing()
    fig_lineage()
    fig_ownership()
    print("ok:", os.listdir(IMG))
