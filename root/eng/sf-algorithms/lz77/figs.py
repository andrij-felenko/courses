# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── window: ковзне вікно = буфер пошуку + буфер попереду ──────────────────────
# Ідея: показати головну конструкцію LZ77 — рядок ділиться курсором на дві
# частини. Зліва (буфер пошуку) — уже бачене, наш «словник». Справа (буфер
# попереду) — те, що тільки кодуємо. Збіг шукаємо в лівому, дивлячись на правий.

def fig_window():
    W, H = 760, 250
    p = []
    cell = 28
    seq = "ABABCABABCD"
    cut = 5  # курсор: ліворуч уже закодоване, праворуч — попереду
    x0 = (W - len(seq) * cell) / 2
    y = 96
    for i, ch in enumerate(seq):
        if i < cut:
            fill, stroke, tc = "#eafaf0", FIELD, INK
        else:
            fill, stroke, tc = "#eef4ff", NEG, INK
        p.append(rect(x0 + i * cell, y, cell, cell, fill=fill, stroke=stroke, sw=1.4))
        p.append(text(x0 + i * cell + cell / 2, y + cell / 2 + 5, ch, size=13, color=tc, bold=True))

    # курсор між частинами
    cx = x0 + cut * cell
    p.append(line(cx, y - 16, cx, y + cell + 16, color=INK, sw=2.2))
    p.append(text(cx, y - 22, "курсор", size=10, color=INK, bold=True))

    # підписи двох буферів
    p.append(line(x0, y + cell + 24, cx - 3, y + cell + 24, color=FIELD, sw=2))
    p.append(text((x0 + cx) / 2, y + cell + 42, "буфер пошуку (уже бачене — словник)",
                  size=11, color=FIELD, bold=True))
    p.append(line(cx + 3, y + cell + 24, x0 + len(seq) * cell, y + cell + 24, color=NEG, sw=2))
    p.append(text((cx + x0 + len(seq) * cell) / 2, y + cell + 42, "буфер попереду (ще не кодоване)",
                  size=11, color=NEG, bold=True))

    p.append(text(W / 2, y + cell + 76,
                  "вікно ковзає праворуч; збіг для правого шукаємо в лівому",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "window.svg"), W, H, *p,
           title="Ковзне вікно: словник зліва, нове — справа")


# ── idea: збіг назад → трійка (offset, length, next) ─────────────────────────
# Ідея: найчистіше показати сам прийом. Бачимо повтор «ABAB», що вже траплявся
# 5 байтів тому; замість писати його заново — посилання назад: «вернись на 5,
# візьми 4, далі C». Це душа словникового стиснення одним поглядом.

def fig_idea():
    W, H = 760, 280
    p = []
    cell = 28
    seq = "ABABCABABC"
    x0 = (W - len(seq) * cell) / 2
    y = 86
    # позиції 5..8 — це повтор позицій 0..3; 9 — новий символ
    rep = set([5, 6, 7, 8])
    src = set([0, 1, 2, 3])
    for i, ch in enumerate(seq):
        if i in rep:
            fill, stroke = "#fdecea", POS
        elif i in src:
            fill, stroke = "#eafaf0", FIELD
        else:
            fill, stroke = "#f6f4ec", INK
        p.append(rect(x0 + i * cell, y, cell, cell, fill=fill, stroke=stroke, sw=1.4))
        p.append(text(x0 + i * cell + cell / 2, y + cell / 2 + 5, ch, size=13, color=INK, bold=True))

    # дуга «назад на 5» від початку повтору до джерела
    a = x0 + 5 * cell + cell / 2
    b = x0 + 0 * cell + cell / 2
    midy = y - 36
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" marker-end="url(#arrow)"/>' % (a, y - 4, (a + b) / 2, midy, b, y - 4, POS))
    p.append(text((a + b) / 2, midy - 4, "offset = 5  (вернись на 5 назад)", size=11, color=POS, bold=True))

    # підпис довжини збігу
    p.append(line(x0 + 5 * cell, y + cell + 10, x0 + 9 * cell, y + cell + 10, color=POS, sw=2))
    p.append(text(x0 + 7 * cell, y + cell + 26, "length = 4", size=11, color=POS, bold=True))
    p.append(text(x0 + 9 * cell + cell / 2, y + cell + 26, "next = C", size=11, color=INK, bold=True, anchor="start"))

    # вихідна трійка
    yo = y + cell + 70
    b3, bw, bh = textbox(W / 2, yo, "(offset 5, length 4, next C)", size=14, bold=True,
                         fill="#fdecea", stroke=POS, sw=1.8, color=POS)
    p.append(b3)
    p.append(text(W / 2, yo + bh / 2 + 22,
                  "замість 5 символів «ABABC» — одна трійка з посиланням назад",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "idea.svg"), W, H, *p,
           title="LZ77: повтор → (offset, length, next)")


# ── catches-repeats: що ловить LZ77, чого не бачить посимвольний код ──────────
# Ідея: контраст. Ентропійний код (Гаффман) і RLE дивляться на ОДИН символ /
# серію однакового; LZ77 ловить ПОВТОРЕНИЙ ВІЗЕРУНОК із кількох байтів — рід
# надлишку, невидимий посимвольно.

def fig_catches():
    W, H = 760, 300
    p = []
    cw, ch, gap = 224, 168, 24
    x0 = (W - (3 * cw + 2 * gap)) / 2
    y0 = 70
    cards = [
        ("ентропійний код", NEG, "#eef4ff",
         "частим символам —\nкоротші коди.\nбачить лише\nчастоту ОДНОГО\nсимволу"),
        ("RLE", "#d98a00", "#fdf6e3",
         "згортає серію\nОДНАКОВИХ\nпоспіль.\nне бачить\nрозділених повторів"),
        ("LZ77", FIELD, "#eafaf0",
         "посилається на\nцілий ВІЗЕРУНОК,\nщо вже траплявся.\nловить повтори,\nневидимі іншим"),
    ]
    for i, (title, col, fill, what) in enumerate(cards):
        x = x0 + i * (cw + gap)
        p.append(rect(x, y0, cw, ch, fill=fill, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, y0 + 26, title, size=13, color=col, bold=True))
        p.append(line(x + 18, y0 + 40, x + cw - 18, y0 + 40, color=col, sw=1, dash="4 3"))
        p.append(mtext(x + cw / 2, y0 + 64, what, size=11, color=INK))
    p.append(text(W / 2, y0 + ch + 32,
                  "«the…the…the» — нуль однакових поспіль, та візерунок повторюється: здобич саме LZ77",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "catches-repeats.svg"), W, H, *p,
           title="Три погляди на надлишок: символ, серія, візерунок")


# ── window-size: компроміс розміру вікна ─────────────────────────────────────
# Ідея: дві шальки. Велике вікно бачить далекі повтори (кращий стиск), але
# дорожче за пам'яттю й повільніше шукати; мале — навпаки. Це головний
# інженерний компроміс LZ77.

def fig_window_size():
    W, H = 760, 280
    p = []
    # ліва шалька — велике вікно
    lx = 200
    bl, bwl, bhl = textbox(lx, 78, "велике вікно", size=14, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(bl)
    p.append(mtext(lx, 78 + bhl / 2 + 30,
                   "+ бачить далекі повтори\n+ кращий стиск\n− більше пам'яті\n− повільніший пошук",
                   size=12, color=INK))

    # права шалька — мале вікно
    rx = 560
    br, bwr, bhr = textbox(rx, 78, "мале вікно", size=14, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.8, color=NEG)
    p.append(br)
    p.append(mtext(rx, 78 + bhr / 2 + 30,
                   "+ менше пам'яті\n+ швидший пошук\n− не дістає далеких\n   повторів — гірший стиск",
                   size=12, color=INK))

    p.append(text(W / 2, H - 22,
                  "DEFLATE бере 32 КіБ — компроміс стиск ↔ швидкість і пам'ять",
                  size=12, color=MUTED, italic=True, bold=True))
    render(os.path.join(OUT, "window-size.svg"), W, H, *p,
           title="Розмір вікна: стиск проти швидкості й пам'яті")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури для детальної версії (lz77-d.md)
# ════════════════════════════════════════════════════════════════════════════

# ── greedy-match: як кодувальник шукає найдовший збіг ─────────────────────────
# Ідея: показати сам пошук. Курсор стоїть; кодувальник пробує подовжувати
# збіг із кандидатом у словнику, поки символи однакові, і бере найдовший.

def fig_greedy_match():
    W, H = 760, 280
    p = []
    cell = 28
    seq = "ABCABCABCA"
    x0 = (W - len(seq) * cell) / 2
    y = 96
    cut = 6  # курсор: словник = ABCABC, попереду = ABCA
    for i, ch in enumerate(seq):
        if i < cut:
            fill, stroke = "#eafaf0", FIELD
        else:
            fill, stroke = "#eef4ff", NEG
        p.append(rect(x0 + i * cell, y, cell, cell, fill=fill, stroke=stroke, sw=1.4))
        p.append(text(x0 + i * cell + cell / 2, y + cell / 2 + 5, ch, size=13, color=INK, bold=True))

    cx = x0 + cut * cell
    p.append(line(cx, y - 14, cx, y + cell + 14, color=INK, sw=2.2))
    p.append(text(cx, y - 20, "курсор", size=10, color=INK, bold=True))

    # подовження збігу: кандидат на 3 назад (позиція 3) проти попереду (позиція 6)
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (x0 + 6 * cell + cell / 2, y - 4, x0 + 4.5 * cell, y - 40,
                x0 + 3 * cell + cell / 2, y - 4, POS))
    p.append(text(x0 + 4.5 * cell, y - 46, "кандидат: на 3 назад", size=11, color=POS, bold=True))

    p.append(mtext(W / 2, y + cell + 40,
                   "подовжуй, поки символи однакові: A=A, B=B, C=C, A=A → довжина 4\n"
                   "беремо НАЙДОВШИЙ збіг → (offset 3, length 4)",
                   size=11, color=INK))
    render(os.path.join(OUT, "greedy-match.svg"), W, H, *p,
           title="Пошук збігу: подовжуй, поки збігається")


# ── hash-chains: хеш-таблиця + ланцюги для швидкого пошуку ────────────────────
# Ідея: наївний пошук перебирає все вікно — повільно. Хешуємо трибайтові
# префікси; усі позиції з тим самим хешем зв'язані в ланцюг — перебираємо лише
# справді схожих кандидатів, від найсвіжішого вглиб.

def fig_hash_chains():
    W, H = 760, 320
    p = []
    # хеш-таблиця: бакет за трибайтовим префіксом
    bx, by, bw, bh = 44, 80, 132, 40
    p.append(rect(bx, by, bw, bh, fill="#f6f4ec", stroke=INK, sw=1.6))
    p.append(text(bx + bw / 2, by + bh / 2 + 5, "hash(\"ABC\")", size=12, color=INK, bold=True))
    p.append(text(bx + bw / 2, by - 12, "хеш-таблиця: префікс із 3 байтів", size=10, color=MUTED))

    # ланцюг позицій із тим самим хешем (від найсвіжішої вглиб)
    chain = [("поз. 27", "#eafaf0", FIELD), ("поз. 18", "#eef4ff", NEG),
             ("поз. 9", "#fdf6e3", "#d98a00"), ("поз. 0", "#fdecea", POS)]
    nx, ny, nw, nh, gap = 244, 80, 96, 40, 22
    px, py = bx + bw, by + bh / 2
    for i, (lbl, fill, col) in enumerate(chain):
        x = nx + i * (nw + gap)
        p.append(rect(x, ny, nw, nh, fill=fill, stroke=col, sw=1.6))
        p.append(text(x + nw / 2, ny + nh / 2 + 5, lbl, size=11, color=col, bold=True))
        # стрілка від попереднього
        if i == 0:
            p.append(line(px, py, x, ny + nh / 2, color=MUTED, sw=1.6))
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.6" marker-end="url(#arrow)"/>'
                     % (px, py, x - 1, ny + nh / 2, MUTED))
        else:
            xprev = nx + (i - 1) * (nw + gap) + nw
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.6" marker-end="url(#arrow)"/>'
                     % (xprev, ny + nh / 2, x - 1, ny + nh / 2, MUTED))

    p.append(mtext(W / 2, 190,
                   "усі місця, де вже траплявся префікс «ABC», зв'язані в ланцюг —\n"
                   "від найсвіжішого вглиб; перебираємо лише їх, не все вікно",
                   size=11, color=INK))
    p.append(text(W / 2, 250,
                  "глибину ланцюга обмежують (рівні стиску zlib): глибше — кращий стиск, повільніше",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "hash-chains.svg"), W, H, *p,
           title="Хеш-ланцюги: швидкий пошук замість перебору вікна")


# ── lazy-match: лінива оцінка — а може, наступний збіг довший? ────────────────
# Ідея: жадібний кодувальник бере перший знайдений збіг. Лінивий спершу
# дивиться, чи не дасть НАСТУПНА позиція довший збіг; якщо так — лишає тут
# літерал і бере довший збіг далі. Часто стискає краще.

def fig_lazy_match():
    W, H = 760, 290
    p = []
    cell = 26
    seq = "XABCYABCD"
    x0 = (W - len(seq) * cell) / 2

    # жадібний — угорі
    yg = 76
    p.append(text(40, yg - 14, "жадібно: береш перший збіг", size=12, color=NEG, bold=True, anchor="start"))
    for i, ch in enumerate(seq):
        p.append(rect(x0 + i * cell, yg, cell, cell, fill="#eef4ff", stroke=NEG, sw=1.2))
        p.append(text(x0 + i * cell + cell / 2, yg + cell / 2 + 4, ch, size=11, color=INK))
    p.append(text(x0 + len(seq) * cell + 12, yg + cell / 2 + 4, "«ABC» (3)", size=11, color=NEG, anchor="start", bold=True))

    p.append(line(40, 150, W - 40, 150, color=MUTED, sw=1, dash="4 4"))

    # лінивий — унизу
    yl = 186
    p.append(text(40, yl - 14, "ліниво: а наступний збіг довший?", size=12, color=FIELD, bold=True, anchor="start"))
    for i, ch in enumerate(seq):
        p.append(rect(x0 + i * cell, yl, cell, cell, fill="#eafaf0", stroke=FIELD, sw=1.2))
        p.append(text(x0 + i * cell + cell / 2, yl + cell / 2 + 4, ch, size=11, color=INK))
    p.append(text(x0 + len(seq) * cell + 12, yl + cell / 2 + 4, "літерал + «ABCD» (4)",
                  size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(W / 2, yl + cell + 30,
                  "відклавши збіг на крок, лінивий кодувальник часто ловить довший — кращий стиск",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "lazy-match.svg"), W, H, *p,
           title="Лінива оцінка: відкласти збіг заради довшого")


# ── lzss-vs-lz77: трійка проти прапорця ──────────────────────────────────────
# Ідея: пряме порівняння формату. LZ77 — жорстка трійка (символ чіпляється
# завжди). LZSS — біт-прапорець перемикає: літерал АБО пара; короткі збіги
# лишає літералами.

def fig_lzss_vs_lz77():
    W, H = 760, 300
    p = []
    # LZ77 — ліворуч
    lx = W * 0.27
    bl, bwl, bhl = textbox(lx, 76, "LZ77", size=15, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=1.8, color=NEG)
    p.append(bl)
    p.append(mtext(lx, 76 + bhl / 2 + 30,
                   "жорстка трійка:\n(offset, length, СИМВОЛ)\n\nсвіжий символ чіпляється\nдо КОЖНОГО посилання",
                   size=12, color=INK))

    # LZSS — праворуч
    rx = W * 0.73
    br, bwr, bhr = textbox(rx, 76, "LZSS", size=15, bold=True,
                           fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(br)
    p.append(mtext(rx, 76 + bhr / 2 + 30,
                   "1 біт-прапорець:\n0 → літерал   1 → (offset, length)\n\nкороткі невигідні збіги\nлишає літералами",
                   size=12, color=INK))

    p.append(line(W / 2, 64, W / 2, H - 56, color=MUTED, sw=1, dash="5 4"))
    p.append(text(W / 2, H - 24,
                  "DEFLATE бере саме LZSS, тоді дотискає все Гаффманом",
                  size=12, color=MUTED, italic=True, bold=True))
    render(os.path.join(OUT, "lzss-vs-lz77.svg"), W, H, *p,
           title="Формат: трійка LZ77 проти прапорця LZSS")


# ── deflate-pipeline: двоступеневий конвеєр DEFLATE ──────────────────────────
# Ідея: показати, як LZSS і Гаффман стоять у конвеєрі. Сирі дані → LZSS ловить
# повтори (літерали + посилання) → Гаффман дотискає → бітовий потік.

def fig_deflate_pipeline():
    W, H = 760, 230
    p = []
    cy = 110
    stages = [
        ("сирі\nдані", "#f6f4ec", INK),
        ("LZSS\nловить повтори", "#eafaf0", FIELD),
        ("Гаффман\nдотискає", "#eef4ff", NEG),
        ("стиснутий\nпотік", "#fdecea", POS),
    ]
    bw, bh, gap = 150, 70, 40
    x0 = (W - (4 * bw + 3 * gap)) / 2
    for i, (lbl, fill, col) in enumerate(stages):
        x = x0 + i * (bw + gap)
        p.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(mtext(x + bw / 2, cy - 4, lbl, size=12, color=col, bold=True))
        if i < len(stages) - 1:
            ax = x + bw
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="2" marker-end="url(#arrow)"/>'
                     % (ax + 4, cy, ax + gap - 4, cy, INK))
    # підписи проміжного формату
    p.append(text(x0 + bw + gap + bw / 2, cy + bh / 2 + 26,
                  "літерали + (offset, length)", size=10, color=MUTED))
    p.append(text(W / 2, cy + bh / 2 + 50,
                  "двоступеневий конвеєр: словниковий крок прибирає повтори, ентропійний — добирає решту",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "deflate-pipeline.svg"), W, H, *p,
           title="DEFLATE: LZSS + Гаффман у конвеєрі")


if __name__ == "__main__":
    # базова версія
    fig_window()
    fig_idea()
    fig_catches()
    fig_window_size()
    # детальна версія
    fig_greedy_match()
    fig_hash_chains()
    fig_lazy_match()
    fig_lzss_vs_lz77()
    fig_deflate_pipeline()
    print("OK: figures written to", OUT)
