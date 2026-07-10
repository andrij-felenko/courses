# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фабричний метод (один продукт) проти абстрактної фабрики (родина) ────────
def fig_method_vs_abstract():
    W, H = 1120, 620
    frags = []

    # роздільник посередині
    frags.append(line(W / 2, 92, W / 2, H - 28, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: ФАБРИЧНИЙ МЕТОД ═══════════
    lcx = W / 4
    frags.append(text(lcx, 58, "Фабричний метод", size=17, bold=True, color=NEG))
    frags.append(text(lcx, 80, "один продукт через діру в базі", size=12, color=MUTED))

    # база з дірою
    base, bw, bh = textbox(lcx, 148,
                           ["Application", "createDocument()  ← діра"],
                           size=12.5, bold=True, fill="#eaf0fd", stroke=NEG,
                           sw=1.8, min_w=250)
    frags.append(base)

    # два нащадки
    kids = [("DrawingApp", lcx - 135), ("SpreadsheetApp", lcx + 135)]
    kid_y = 268
    for nm, kx in kids:
        frags.append(line(lcx, 148 + bh / 2, kx, kid_y - 24, color=NEG, sw=1.3))
        b, kw, kh = textbox(kx, kid_y, nm, size=12, bold=True,
                            fill="#eaf0fd", stroke=NEG, sw=1.5, min_w=138)
        frags.append(b)
        # кожен нащадок → свій ЄДИНИЙ продукт
        prod = "DrawingDocument" if "Draw" in nm else "SpreadsheetDoc"
        frags.append(arrow(kx, kid_y + kh / 2, kx, 372 - 24, color=NEG, sw=1.6))
        p, _, _ = textbox(kx, 372, prod, size=11, fill=FILL, stroke=LINE,
                          sw=1.4, min_w=150)
        frags.append(p)

    frags.append(text(lcx, 452, "кожен нащадок віддає",
                      size=12.5, color=INK))
    frags.append(text(lcx, 472, "рівно ОДИН продукт", size=12.5, bold=True, color=INK))

    # ═══════════ ПРАВОРУЧ: АБСТРАКТНА ФАБРИКА ═══════════
    rcx = 3 * W / 4
    frags.append(text(rcx, 58, "Абстрактна фабрика", size=17, bold=True, color=FIELD))
    frags.append(text(rcx, 80, "узгоджена родина продуктів", size=12, color=MUTED))

    # інтерфейс фабрики з трьома creates
    iface, iw, ih = textbox(rcx, 158,
                            ["UiFactory", "createButton()",
                             "createCheckbox()", "createInput()"],
                            size=12, bold=True, fill="#e8f6ee", stroke=FIELD,
                            sw=1.8, min_w=210)
    frags.append(iface)

    # дві конкретні фабрики (теми), кожна → трійка
    themes = [("DarkFactory", rcx - 150, ["Dark", "Btn", "Chk", "Inp"]),
              ("LightFactory", rcx + 150, ["Light", "Btn", "Chk", "Inp"])]
    fac_y = 300
    for nm, fx, prods in themes:
        frags.append(line(rcx, 158 + ih / 2, fx, fac_y - 26, color=FIELD, sw=1.3))
        b, fw, fh = textbox(fx, fac_y, nm, size=12, bold=True,
                            fill="#e8f6ee", stroke=FIELD, sw=1.5, min_w=140)
        frags.append(b)
        # рамка-родина навколо трьох продуктів
        fam_x = fx - 78
        fam_y = fac_y + fh / 2 + 22
        frags.append(rect(fam_x, fam_y, 156, 96, fill="#f4fbf7",
                          stroke=FIELD, sw=1.4, rx=8))
        pref = prods[0]
        labels = ["%s%s" % (pref, s) for s in prods[1:]]
        for i, lab in enumerate(labels):
            py = fam_y + 22 + i * 26
            frags.append(text(fx, py, lab, size=11, color=INK))
        frags.append(arrow(fx, fac_y + fh / 2, fx, fam_y - 2, color=FIELD, sw=1.5))

    frags.append(text(rcx, 500, "одна фабрика — ЦІЛА трійка з однієї теми",
                      size=12.5, bold=True, color=INK))
    frags.append(text(rcx, 522, "елементи різних тем змішати неможливо",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'method-vs-abstract.svg'), W, H, *frags)


# ── Три способи вибрати клас за ключем: switch → таблиця → самореєстрація ─────
def fig_switch_vs_registry():
    W, H = 1200, 640
    frags = []

    # три колонки з широким запасом, щоб написи не накладались
    col_cx = [W * 0.185, W * 0.5, W * 0.815]
    titles = [
        ("if / else ланцюг", NEG),
        ("таблиця-реєстр", FIELD),
        ("самореєстрація", POS),
    ]
    subs = [
        "вибір усередині гілок",
        "вибір у даних (мапі)",
        "клас вписує себе сам",
    ]
    for cx, (t, c), sub in zip(col_cx, titles, subs):
        frags.append(text(cx, 44, t, size=16, bold=True, color=c))
        frags.append(text(cx, 66, sub, size=11.5, color=MUTED))

    # роздільники між колонками
    for x in (W / 3, 2 * W / 3):
        frags.append(line(x, 82, x, H - 118, color="#d0d5db", sw=1.1, dash="6,6"))

    box_top = 96
    box_w = 300

    # ── Колонка 1: switch-функція з гілками всередині ────────────────────────
    fitbox(0, 0, 1, 1, "x")  # no-op guard (лишаємо API теплим)
    c1 = col_cx[0]
    frags.append(fitbox(c1 - box_w / 2, box_top, box_w, 214,
                        "parserForFile(ext):\n"
                        "  if ext=='json' → new Json\n"
                        "  if ext=='csv'  → new Csv\n"
                        "  if ext=='xml'  → new Xml\n"
                        "  else → помилка",
                        size=13, fill="#eaf0fd", stroke=NEG, sw=1.6, pad=14))
    # маркер: тіло функції росте
    frags.append(text(c1, box_top + 214 + 24,
                     "гілки ЖИВУТЬ у тілі функції", size=12, color=INK))

    # ── Колонка 2: мала функція + окрема таблиця ─────────────────────────────
    c2 = col_cx[1]
    tbl_h = 116
    frags.append(fitbox(c2 - box_w / 2, box_top, box_w, tbl_h,
                        "PARSERS  (дані):\n"
                        "  json → JsonParser\n"
                        "  csv  → CsvParser\n"
                        "  xml  → XmlParser",
                        size=13, fill="#eef8f2", stroke=FIELD, sw=1.6, pad=12))
    fn_y = box_top + tbl_h + 26
    frags.append(arrow(c2, box_top + tbl_h + 2, c2, fn_y - 2, color=FIELD, sw=1.5))
    frags.append(fitbox(c2 - box_w / 2, fn_y, box_w, 66,
                        "parserForFile(ext):\n"
                        "  return PARSERS[ext]()   ← стала",
                        size=12.5, fill=FILL, stroke=LINE, sw=1.4, pad=12))
    frags.append(text(c2, fn_y + 66 + 24,
                     "функція мала й НЕ міняється", size=12, color=INK))

    # ── Колонка 3: класи самі вписуються в реєстр ────────────────────────────
    c3 = col_cx[2]
    reg_y = box_top
    reg, rw, rh = textbox(c3, reg_y + 26, "PARSERS  (порожній старт)",
                          size=12.5, bold=True, fill="#fdecea", stroke=POS,
                          sw=1.6, min_w=box_w)
    frags.append(reg)
    kids = [("@parses('json')  Json", reg_y + 96),
            ("@parses('csv')   Csv", reg_y + 150),
            ("@parses('yaml')  Yaml", reg_y + 204)]
    for label, ky in kids:
        b, _, _ = textbox(c3, ky, label, size=12, fill=FILL, stroke=LINE,
                          sw=1.3, min_w=box_w)
        frags.append(b)
        # стрілка від класу вгору в реєстр — праворуч від текстів, повз написи
        ax = c3 + box_w / 2 - 8
        frags.append(arrow(ax, ky - 12, ax, reg_y + 26 + rh / 2 + 4,
                          color=POS, sw=1.3))
    frags.append(text(c3, reg_y + 204 + 40,
                     "фабрика взагалі НЕ знає списку", size=12, color=INK))

    # ── Нижній рядок: що правиш при НОВОМУ форматі ───────────────────────────
    band_y = H - 96
    frags.append(line(40, band_y - 14, W - 40, band_y - 14,
                     color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, band_y + 4,
                     "Додаємо новий формат — де правка?",
                     size=13.5, bold=True, color=INK))
    edits = [
        (c1, "у ТІЛІ функції (+гілка)", NEG),
        (c2, "один рядок у таблиці", FIELD),
        (c3, "ніде — клас вписав себе", POS),
    ]
    for cx, msg, c in edits:
        frags.append(text(cx, band_y + 32, msg, size=12.5, bold=True, color=c))

    render(os.path.join(IMG, 'switch-vs-registry.svg'), W, H, *frags)


# ── Часова смуга народження патернів (для hist-вставки) ──────────────────────
def fig_gof_timeline():
    W, H = 1080, 760
    frags = []

    frags.append(text(W / 2, 40, "Як визрівали патерни проєктування",
                      size=18, bold=True, color=INK))
    frags.append(text(W / 2, 62, "від архітектури будівель до каталогу коду",
                      size=12.5, color=MUTED))

    spine_x = W / 2
    top, bot = 96, H - 40
    frags.append(line(spine_x, top, spine_x, bot, color="#c4cad2", sw=3))

    # (рік, заголовок, [рядки опису], сторона, колір)
    events = [
        ("1977", "«A Pattern Language»",
         ["Крістофер Александер:", "мова взірців в архітектурі"], "L", FIELD),
        ("1987", "Бек і Каннінгем",
         ["перший перенос патернів", "у код (Smalltalk, OOPSLA)"], "R", POS),
        ("кінець 1980-х", "ET++  ·  InterViews",
         ["два GUI-каркаси на C++:", "Цюрих (Гамма) і Стенфорд"], "L", NEG),
        ("1990", "OOPSLA, Оттава",
         ["секція «Architecture Handbook»:", "Гамма й Гелм знайомляться"], "R", INK),
        ("1991", "Докторат Гамми",
         ["Цюрихський університет:", "патерни виловлено з ET++"], "L", NEG),
        ("1993", "ECOOP, Кайзерслаутерн",
         ["стаття: фабричний метод", "і абстрактна фабрика — вже названі"], "R", POS),
        ("1994", "«Design Patterns»",
         ["банда чотирьох, Addison-Wesley:", "каталог із 23 патернів"], "L", FIELD),
    ]

    n = len(events)
    y0, y1 = top + 34, bot - 22
    box_w = 356
    gap = 46  # відступ рамки від хребта — написи гарантовано повз лінію

    for i, (yr, title, subs, side, color) in enumerate(events):
        cy = y0 + (y1 - y0) * i / (n - 1)

        # вузол на хребті кольору події
        frags.append(circle(spine_x, cy, 7, fill=color, stroke=BG, sw=2.5))

        # рамка з описом ліворуч або праворуч, гарантовано поза хребтом;
        # рік — перший рядок самої рамки, тож накластися нема на що
        lines = ["%s — %s" % (yr, title)] + subs
        bx = spine_x - gap - box_w if side == "L" else spine_x + gap
        bh = 78
        frags.append(fitbox(bx, cy - bh / 2, box_w, bh,
                            "\n".join(lines), size=12.5, pad=12,
                            fill=FILL, stroke=color, sw=1.6))
        # тонка поличка від хребта до рамки
        shelf_x2 = bx + box_w if side == "L" else bx
        frags.append(line(spine_x, cy, shelf_x2, cy, color=color, sw=1.2))

    render(os.path.join(IMG, 'gof-timeline.svg'), W, H, *frags)


# ── Фабричний метод як діра у незмінному скелеті (Template Method) ────────────
def fig_template_hole():
    W, H = 1040, 600
    frags = []

    frags.append(text(W / 2, 40, "Фабричний метод — одна діра у незмінному скелеті",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62,
                      "каркас пише алгоритм один раз; нащадок заповнює лише одну ланку",
                      size=12.5, color=MUTED))

    # ── База: шаблонний метод newDocument() зі стосом кроків ──────────────────
    bx, bw = 300, 440
    frags.append(rect(bx, 96, bw, 240, fill=BG, stroke=INK, sw=1.8, rx=8))
    frags.append(text(bx + bw / 2, 122, "newDocument()  ·  незмінний скелет",
                      size=13, bold=True, color=INK))
    frags.append(line(bx + 12, 134, bx + bw - 12, 134, color="#d0d5db", sw=1))

    # крок-діра (виділений) і три фіксовані кроки
    frags.append(rect(bx + 14, 146, bw - 28, 44, fill="#fdecea", stroke=POS, sw=1.7, rx=6))
    frags.append(text(bx + bw / 2, 173, "① doc = createDocument()   ← ДІРА",
                      size=12.5, bold=True, color=POS))
    for label, y in [("② doc.open()", 196),
                     ("③ registerInRecent(doc)", 236),
                     ("④ return doc", 276)]:
        frags.append(rect(bx + 14, y, bw - 28, 36, fill="#eef2f7", stroke=LINE, sw=1.2, rx=6))
        frags.append(text(bx + bw / 2, y + 24, label, size=12.5, color=INK))

    # нотатка праворуч від діри (текст поза рамкою бази, стрілка веде в діру)
    frags.append(arrow(768, 171, 730, 171, color=POS, sw=1.5))
    frags.append(text(774, 160, "цю ланку —", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(774, 184, "і лише її — заповнює нащадок",
                      size=12, color=POS, anchor="start"))

    # ── Два нащадки, що вставляють свій продукт у діру ────────────────────────
    for nm, cx, body in [("DrawingApp", 340, "return new DrawingDocument()"),
                         ("SpreadsheetApp", 700, "return new SpreadsheetDocument()")]:
        b, w2, h2 = textbox(cx, 456, [nm, "createDocument():", body],
                            size=12, fill="#fbeeec", stroke=POS, sw=1.5, min_w=250)
        frags.append(b)
        frags.append(arrow(cx, 456 - h2 / 2, 520, 336, color=INK, sw=1.4))

    frags.append(text(W / 2, 542,
                      "Голлівудський принцип — «не дзвоніть нам, ми подзвонимо вам»:",
                      size=12.5, color=MUTED))
    frags.append(text(W / 2, 562,
                      "не ти кличеш каркас, а каркас у потрібну мить кличе твій createDocument().",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, 'template-hole.svg'), W, H, *frags)


# ── Дешева й дорога вісь абстрактної фабрики (родини × види продукту) ─────────
def fig_variation_matrix():
    W, H = 940, 456
    frags = []
    frags.append(text(W / 2, 38, "Абстрактна фабрика: дешева вісь і дорога вісь",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 60, "родина — це рядок;  вид продукту — це стовпець",
                      size=12.5, color=MUTED))

    xs = [90, 250, 400, 550, 700, 850]     # мітка | Button Checkbox Input | Slider(ghost)
    ys = [96, 150, 212, 274, 336]          # header | Dark Light | Solar(ghost)
    kinds = ["Button", "Checkbox", "Input"]

    # ── Шапка ─────────────────────────────────────────────────────────────────
    frags.append(rect(xs[0], ys[0], xs[1] - xs[0], ys[1] - ys[0], fill="#eef2f7", stroke=LINE, sw=1.2))
    frags.append(text((xs[0] + xs[1]) / 2, (ys[0] + ys[1]) / 2 + 4, "родина / вид", size=11.5, color=MUTED))
    for j, k in enumerate(kinds):
        frags.append(rect(xs[j + 1], ys[0], xs[j + 2] - xs[j + 1], ys[1] - ys[0], fill="#eef2f7", stroke=LINE, sw=1.2))
        frags.append(text((xs[j + 1] + xs[j + 2]) / 2, (ys[0] + ys[1]) / 2 + 4, k, size=12.5, bold=True, color=INK))
    gcx = (xs[4] + xs[5]) / 2
    frags.append(rect(xs[4], ys[0], xs[5] - xs[4], ys[1] - ys[0], fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(gcx, ys[0] + 22, "Slider", size=12.5, bold=True, color=POS))
    frags.append(text(gcx, ys[0] + 40, "новий вид", size=10.5, color=POS))

    # ── Рядки-родини ──────────────────────────────────────────────────────────
    fams = [("DarkFactory", "Dark", 1, "#ffffff", LINE, False),
            ("LightFactory", "Light", 2, "#ffffff", LINE, False),
            ("SolarFactory", "Solar", 3, "#eef8f2", FIELD, True)]
    for nm, pref, ri, cellfill, cst, ghost in fams:
        ry0, ry1 = ys[ri], ys[ri + 1]
        rcy = (ry0 + ry1) / 2
        lf = "#eef8f2" if ghost else "#eef2f7"
        lst = FIELD if ghost else LINE
        frags.append(rect(xs[0], ry0, xs[1] - xs[0], ry1 - ry0, fill=lf, stroke=lst, sw=1.5 if ghost else 1.2, rx=4))
        if ghost:
            frags.append(text((xs[0] + xs[1]) / 2, rcy - 4, nm, size=11.5, bold=True, color=FIELD))
            frags.append(text((xs[0] + xs[1]) / 2, rcy + 14, "нова родина", size=10.5, color=FIELD))
        else:
            frags.append(text((xs[0] + xs[1]) / 2, rcy + 4, nm, size=12, bold=True, color=INK))
        for j, k in enumerate(kinds):
            frags.append(rect(xs[j + 1], ry0, xs[j + 2] - xs[j + 1], ry1 - ry0, fill=cellfill, stroke=cst, sw=1.2, rx=4))
            frags.append(text((xs[j + 1] + xs[j + 2]) / 2, rcy + 4, pref + k, size=11.5, color=(FIELD if ghost else INK)))
        if not ghost:
            frags.append(rect(xs[4], ry0, xs[5] - xs[4], ry1 - ry0, fill="#fdecea", stroke=POS, sw=1.3, rx=4))
            frags.append(text(gcx, rcy + 4, pref + "Slider", size=11.5, color=POS))
        else:
            frags.append(rect(xs[4], ry0, xs[5] - xs[4], ry1 - ry0, fill="#f7f7f9", stroke=MUTED, sw=1.1, rx=4))
            frags.append(text(gcx, rcy + 4, "…", size=13, color=MUTED))

    frags.append(text(W / 2, 382, "↓  додати РОДИНУ (рядок): одна нова фабрика — старі недоторкані",
                      size=12.5, bold=True, color=FIELD))
    frags.append(text(W / 2, 408, "→  додати ВИД (стовпець): нова сигнатура в КОЖНІЙ фабриці одразу",
                      size=12.5, bold=True, color=POS))
    render(os.path.join(IMG, 'variation-matrix.svg'), W, H, *frags)


# ── Дві реалізації абстрактної фабрики: N класів проти 1 класу + даних ────────
def fig_two_impls():
    W, H = 1180, 560
    frags = []

    # роздільник (не доходить до нижнього краю, щоб не різати написи)
    frags.append(line(W / 2, 92, W / 2, 530, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: КЛАС НА РОДИНУ ═══════════
    lcx = 296
    frags.append(text(lcx, 52, "Класична: клас на кожну родину", size=15, bold=True, color=NEG))
    frags.append(text(lcx, 74, "родина — це ТИП; N класів, метод на кожен вид", size=11, color=MUTED))

    iface, iw, ih = textbox(lcx, 150,
                            ["«DbFactory» — інтерфейс", "createConnection()",
                             "createCommand()", "createTransaction()"],
                            size=12, bold=True, fill="#eaf0fd", stroke=NEG,
                            sw=1.8, min_w=250)
    frags.append(iface)

    kids = [("PostgresFactory", 206, "Pg"), ("MySqlFactory", 386, "My")]
    for nm, kx, pref in kids:
        frags.append(line(lcx, 192, kx, 252, color=NEG, sw=1.3))
        b, kw, kh = textbox(kx, 292,
                            [nm, "new %sConnection" % pref, "new %sCommand" % pref,
                             "new %sTransaction" % pref],
                            size=11, bold=True, fill="#eaf0fd", stroke=NEG,
                            sw=1.5, min_w=178)
        frags.append(b)

    frags.append(text(lcx, 360, "…і так на КОЖНУ СУБД (SQLite, Oracle, …)",
                      size=11, color=MUTED))
    frags.append(text(lcx, 410, "один клас = вся родина однієї СУБД, зшита ТИПАМИ",
                      size=12, bold=True, color=INK))
    frags.append(text(lcx, 432, "нова СУБД → +1 клас;  новий ВИД → метод у КОЖЕН клас",
                      size=11, color=MUTED))

    # ═══════════ ПРАВОРУЧ: ОДИН КЛАС + РЕЄСТР ═══════════
    rcx = 884
    frags.append(text(rcx, 52, "Прототипна: один клас + реєстр", size=15, bold=True, color=FIELD))
    frags.append(text(rcx, 74, "родина — це ДАНІ; продукти клонуємо зі взірців", size=11, color=MUTED))

    pf, pw, ph = textbox(rcx, 150,
                         ["PrototypeFactory — ОДИН клас", "create(kind):",
                          "    return registry[kind].clone()"],
                         size=12, bold=True, fill="#e8f6ee", stroke=FIELD,
                         sw=1.8, min_w=320)
    frags.append(pf)
    frags.append(arrow(rcx, 183, rcx, 258, color=FIELD, sw=1.6))

    t1, t1w, t1h = textbox(rcx, 290,
                           ["реєстр прототипів = Postgres", "connection → PgConnection",
                            "command → PgCommand", "transaction → PgTransaction"],
                           size=11, fill="#f4fbf7", stroke=FIELD, sw=1.4, min_w=330)
    frags.append(t1)

    frags.append(arrow(694, 327, 694, 383, color=POS, sw=1.4))
    frags.append(text(rcx, 352, "▼ підмінити НАБІР — той самий клас, інша СУБД",
                      size=11, bold=True, color=POS))

    t2, t2w, t2h = textbox(rcx, 418,
                           ["реєстр прототипів = MySQL", "connection → MyConnection",
                            "command → MyCommand", "transaction → MyTransaction"],
                           size=11, fill="#f4fbf7", stroke=FIELD, sw=1.4, min_w=330)
    frags.append(t2)

    frags.append(text(rcx, 500, "1 клас; яку СУБД брати — вирішують ДАНІ реєстру",
                      size=12, bold=True, color=INK))
    frags.append(text(rcx, 522, "але узгодженість родини тепер тримають дані, не типи",
                      size=11, color=POS))

    render(os.path.join(IMG, 'two-impls.svg'), W, H, *frags)


# ── Клонування взірця: поверхневе (спільне вкладене) проти глибокого ──────────
def fig_clone_depth():
    W, H = 1180, 560
    frags = []

    frags.append(line(W / 2, 92, W / 2, 428, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: ПОВЕРХНЕВЕ ═══════════
    lcx = 296
    frags.append(text(lcx, 50, "Поверхневе клонування (shallow)", size=15, bold=True, color=POS))
    frags.append(text(lcx, 72, "копіюємо об'єкт — вкладене лишається СПІЛЬНИМ", size=11, color=MUTED))

    b, _, _ = textbox(196, 160, ["Command — взірець", "params ▾"],
                      size=11, fill="#eaf0fd", stroke=LINE, sw=1.5, min_w=150)
    frags.append(b)
    b, _, _ = textbox(396, 160, ["клон = взірець.clone()", "params ▾"],
                      size=11, fill="#eaf0fd", stroke=LINE, sw=1.5, min_w=150)
    frags.append(b)

    sh, _, _ = textbox(296, 300, ["ОДИН список params", "[ id, name, … ]"],
                       size=11, bold=True, fill="#fdecea", stroke=POS, sw=1.7, min_w=210)
    frags.append(sh)
    frags.append(arrow(196, 184, 270, 296, color=POS, sw=1.5))
    frags.append(arrow(396, 184, 322, 296, color=POS, sw=1.5))

    frags.append(text(lcx, 372, "змінив params у клоні — воно змінилось і у взірця",
                      size=11.5, bold=True, color=POS))
    frags.append(text(lcx, 394, "стан ТЕЧЕ між копіями — прихована помилка", size=11, color=INK))

    # ═══════════ ПРАВОРУЧ: ГЛИБОКЕ ═══════════
    rcx = 884
    frags.append(text(rcx, 50, "Глибоке клонування (deep)", size=15, bold=True, color=FIELD))
    frags.append(text(rcx, 72, "рекурсивно копіюємо й вкладене — копії незалежні", size=11, color=MUTED))

    b, _, _ = textbox(784, 160, ["Command — взірець", "params ▾"],
                      size=11, fill="#e8f6ee", stroke=LINE, sw=1.5, min_w=150)
    frags.append(b)
    b, _, _ = textbox(984, 160, ["клон = взірець.clone()", "params ▾"],
                      size=11, fill="#e8f6ee", stroke=LINE, sw=1.5, min_w=150)
    frags.append(b)

    a, _, _ = textbox(784, 300, ["params взірця", "[ id, name ]"],
                      size=11, fill="#f4fbf7", stroke=FIELD, sw=1.5, min_w=178)
    frags.append(a)
    a, _, _ = textbox(984, 300, ["params клона — СВІЙ", "[ id, name ]"],
                      size=11, fill="#f4fbf7", stroke=FIELD, sw=1.5, min_w=178)
    frags.append(a)
    frags.append(arrow(784, 184, 784, 296, color=FIELD, sw=1.5))
    frags.append(arrow(984, 184, 984, 296, color=FIELD, sw=1.5))

    frags.append(text(rcx, 372, "клон має ВЛАСНИЙ список — об'єкти незалежні",
                      size=11.5, bold=True, color=FIELD))
    frags.append(text(rcx, 394, "але глибока копія дорога, а сокет/файл не копіюються",
                      size=11, color=INK))

    # ── Нижня смуга: коли взірець узагалі годиться ───────────────────────────
    frags.append(line(60, 438, W - 60, 438, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, 468, "Прототип працює лише коли clone() копіює на ПОТРІБНУ глибину:",
                      size=12.5, bold=True, color=INK))
    frags.append(text(W / 2, 492,
                      "продукт-значення (SQL + параметри) клонується;  продукт із живим ресурсом (сокет) — ні.",
                      size=11.5, color=MUTED))
    frags.append(text(W / 2, 516,
                      "тому взірець годиться для Command;  Connection частіше лишають класу на родину.",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'clone-depth.svg'), W, H, *frags)


# ── Проблема виразности: одна матриця, розрізана рядками (ООП) і стовпцями (ФП) ─
def fig_expression_duality():
    W, H = 1180, 600
    frags = []
    frags.append(text(W / 2, 40, "Проблема виразності: одна матриця, два розрізи",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62,
                      "типи — рядки, операції — стовпці; одиниця коду — або рядок, або стовпець",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 92, W / 2, H - 92, color="#d0d5db", sw=1.2, dash="6,6"))

    ops = ["eval", "show", "simp"]
    types = ["Lit", "Add", "Mul"]
    hdrW, hdrH, cw, ch = 78, 34, 68, 44
    oy = 120

    def panel(ox, unit, title, cap_cheap, cap_dear):
        cx = ox + (hdrW + 3 * cw) / 2          # центр «ядра» сітки
        p = [text(cx, 106, title, size=14, bold=True, color=INK)]
        # кут
        p.append(rect(ox, oy, hdrW, hdrH, fill="#eef2f7", stroke=LINE, sw=1.1))
        p.append(text(ox + hdrW / 2, oy + hdrH / 2 + 4, "тип·опер", size=10, color=MUTED))
        # шапка-операції (стовпці); у ФП саме вони — одиниця коду, тож зелені
        colunit = (unit == "col")
        for j, op in enumerate(ops):
            cxj = ox + hdrW + j * cw
            p.append(rect(cxj, oy, cw, hdrH, fill=("#e8f6ee" if colunit else "#eef2f7"),
                          stroke=(FIELD if colunit else LINE), sw=(1.5 if colunit else 1.1)))
            p.append(text(cxj + cw / 2, oy + hdrH / 2 + 4, op, size=12, bold=colunit, color=INK))
        # шапка-типи (рядки) + тіло; в ООП рядки — одиниця коду, тож зелені
        rowunit = (unit == "row")
        for i, tp in enumerate(types):
            ry = oy + hdrH + i * ch
            p.append(rect(ox, ry, hdrW, ch, fill=("#e8f6ee" if rowunit else "#eef2f7"),
                          stroke=(FIELD if rowunit else LINE), sw=(1.5 if rowunit else 1.1)))
            p.append(text(ox + hdrW / 2, ry + ch / 2 + 4, tp, size=12, bold=rowunit, color=INK))
            for j in range(3):
                cxj = ox + hdrW + j * cw
                p.append(rect(cxj, ry, cw, ch, fill=BG, stroke="#c9ced6", sw=1.0))
        # привид: новий РЯДОК унизу
        cheap_row = (unit == "row")
        rc = FIELD if cheap_row else POS
        rt = "#eef8f2" if cheap_row else "#fdecea"
        ry = oy + hdrH + 3 * ch
        p.append(rect(ox, ry, hdrW, ch, fill=rt, stroke=rc, sw=1.6, rx=4))
        p.append(text(ox + hdrW / 2, ry + ch / 2 + 4, "+тип", size=11.5, bold=True, color=rc))
        for j in range(3):
            cxj = ox + hdrW + j * cw
            p.append(rect(cxj, ry, cw, ch, fill=rt, stroke=rc, sw=1.3, rx=4))
        # привид: новий СТОВПЕЦЬ праворуч
        cc = POS if cheap_row else FIELD
        ct = "#fdecea" if cheap_row else "#eef8f2"
        cxg = ox + hdrW + 3 * cw
        p.append(rect(cxg, oy, cw, hdrH, fill=ct, stroke=cc, sw=1.6, rx=4))
        p.append(text(cxg + cw / 2, oy + hdrH / 2 + 4, "+опер", size=11, bold=True, color=cc))
        for i in range(3):
            ry2 = oy + hdrH + i * ch
            p.append(rect(cxg, ry2, cw, ch, fill=ct, stroke=cc, sw=1.3, rx=4))
        # підписи: зелене — дешева вісь, червоне — дорога
        p.append(text(cx, 372, cap_cheap, size=12, bold=True, color=FIELD))
        p.append(text(cx, 394, cap_dear, size=12, bold=True, color=POS))
        return p

    frags += panel(145, "row", "Об'єктний розклад (ООП): код = РЯДОК",
                   "+тип — 1 клас, старе ціле", "+опер — метод у КОЖЕН клас")
    frags += panel(744, "col", "Функційний розклад (ФП): код = СТОВПЕЦЬ",
                   "+опер — 1 функція, старе ціле", "+тип — гілка в КОЖНУ функцію")
    frags.append(text(W / 2, 556,
                      "Що одна сторона дарує (зелене), друга бере за те саме плату (червоне): осі протилежні.",
                      size=12.5, color=INK))
    render(os.path.join(IMG, 'expression-duality.svg'), W, H, *frags)


# ── Чотири виходи з вилки на площині «дешево додати тип / операцію» ───────────
def fig_escape_quadrants():
    W, H = 1000, 600
    frags = []
    frags.append(text(W / 2, 38, "Чотири виходи з вилки — і хибний вихід",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 60,
                      "осі: чи дешево додати ОПЕРАЦІЮ (праворуч) і чи дешево додати ТИП (вгору)",
                      size=12.5, color=MUTED))

    L, R, T, B = 150, 858, 100, 470
    midx, midy = (L + R) / 2, (T + B) / 2
    frags.append(rect(L, T, R - L, B - T, fill=BG, stroke="#c9ced6", sw=1.2))
    frags.append(line(midx, T, midx, B, color="#d0d5db", sw=1.1, dash="5,5"))
    frags.append(line(L, midy, R, midy, color="#d0d5db", sw=1.1, dash="5,5"))

    def qbox(cx, cy, lines, hl=False, faint=False):
        fill = "#eafaf1" if hl else (BG if faint else FILL)
        stroke = FIELD if hl else ("#d0d5db" if faint else LINE)
        color = MUTED if faint else INK
        b, _, _ = textbox(cx, cy, lines, size=12, fill=fill, stroke=stroke,
                          sw=(2 if hl else 1.3), color=color, bold=hl)
        return b

    frags.append(qbox(327, 192, ["ООП · Абстрактна фабрика",
                                 "рядки — даром,", "стовпці — за плату"]))
    frags.append(qbox(681, 192, ["Мультиметоди · Класи типів",
                                 "Tagless-final · Object algebras",
                                 "обидві осі — відкрито"], hl=True))
    frags.append(qbox(327, 377, ["(обидві дорого —", "свідомо не тут)"], faint=True))
    frags.append(qbox(681, 377, ["ФП · взірці · Відвідувач",
                                 "стовпці — даром,", "рядки — за плату"]))

    # відвідувач — двобічна діагональ (поворот між рогами, не вихід)
    frags.append(arrow(430, 225, 575, 352, color=NEG, sw=1.6))
    frags.append(arrow(575, 352, 430, 225, color=NEG, sw=1.6))
    frags.append(text(300, 320, "Відвідувач — поворот, не вихід", size=12, color=NEG))

    # осьові мітки
    frags.append(text(300, 492, "операцію: ДОРОГО", size=12, bold=True, color=POS))
    frags.append(text(700, 492, "операцію: ДЕШЕВО", size=12, bold=True, color=FIELD))
    frags.append(text(midx, 510, "→ додати операцію (стовпець)", size=11.5, color=MUTED))
    frags.append(mtext(78, 150, ["тип:", "ДЕШЕВО"], size=11.5, color=FIELD, bold=True))
    frags.append(mtext(78, 452, ["тип:", "ДОРОГО"], size=11.5, color=POS, bold=True))

    frags.append(text(W / 2, 540,
                      "ООП-ріг (фабрика) і ФП-ріг стоять навпроти по діагоналі; Відвідувач лише возить між ними.",
                      size=12, color=INK))
    frags.append(text(W / 2, 562,
                      "Правий-верхній кут — справжній вихід: додати і тип, і операцію, не чіпаючи старого.",
                      size=12, color=INK))
    render(os.path.join(IMG, 'escape-quadrants.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_method_vs_abstract()
    fig_switch_vs_registry()
    fig_gof_timeline()
    fig_template_hole()
    fig_variation_matrix()
    fig_two_impls()
    fig_clone_depth()
    fig_expression_duality()
    fig_escape_quadrants()
    print("figs done")
