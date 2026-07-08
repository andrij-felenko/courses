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


if __name__ == '__main__':
    fig_method_vs_abstract()
    fig_switch_vs_registry()
    fig_gof_timeline()
    print("figs done")
