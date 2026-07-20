# -*- coding: utf-8 -*-
"""Фігури до статті «Сховище ключ — значення». Запуск із теки теми: python figs.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GOOD = FIELD      # зелений — сильна сторона
WEAK = POS        # червоний — слабка сторона
HL   = "#e9f8ef"  # світло-зелена заливка виділеного


def box(x, y, w, h, s, size=13, fill=FILL, stroke=LINE, sw=1.5, bold=False, color=INK):
    return rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw) + \
           text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, bold=bold, color=color)


# ── Фіг. 1. Три способи знайти ключ ────────────────────────────────────────
def fig_lookup():
    W, H = 960, 430
    cx = [160, 480, 800]          # центри трьох панелей
    parts = [text(W / 2, 30, "Знайти значення за ключем — три структури", size=17, bold=True)]

    # рамки панелей
    for c in cx:
        parts.append(rect(c - 150, 52, 300, 348, fill=BG, stroke=MUTED, sw=1.2))

    keys = ["мел", "сем", "кім", "ада"]         # 4 ключі
    bw, bh, gap = 58, 34, 8
    row_w = 4 * bw + 3 * gap                     # 256

    # --- Панель 1: несортований масив, шукаємо "ада" (індекс 3) ---
    c = cx[0]; x0 = c - row_w / 2; yrow = 210
    parts.append(text(c, 78, "1. Несортований", size=14, bold=True))
    parts.append(text(c, 98, 'шукаємо "ада"', size=12, color=MUTED))
    for i, k in enumerate(keys):
        bx = x0 + i * (bw + gap)
        hit = (i == 3)
        parts.append(box(bx, yrow, bw, bh, k, fill=HL if hit else FILL,
                         stroke=GOOD if hit else LINE, sw=2 if hit else 1.5, bold=hit))
        parts.append(text(bx + bw / 2, yrow - 12, str(i + 1), size=12, color=MUTED))
        if i < 3:  # стрілочки перебору між першими боксами
            parts.append(arrow(bx + bw + 1, yrow + bh / 2, bx + bw + gap - 1, yrow + bh / 2, color=MUTED, sw=1.4))
    parts.append(text(c, yrow - 34, "перевіряємо кожен →", size=12, color=MUTED))
    parts.append(text(c, 300, "O(n)", size=20, bold=True, color=WEAK))
    parts.append(fitbox(c - 138, 322, 276, 60, "перебрати всі, поки не трапиться потрібний",
                        size=12, fill=BG, stroke="none", color=INK))

    # --- Панель 2: сортований масив, двійковий пошук "сем" ---
    skeys = ["ада", "кім", "мел", "сем"]        # відсортовано
    c = cx[1]; x0 = c - row_w / 2; yrow = 210
    parts.append(text(c, 78, "2. Сортований", size=14, bold=True))
    parts.append(text(c, 98, 'двійковий пошук "сем"', size=12, color=MUTED))
    for i, k in enumerate(skeys):
        bx = x0 + i * (bw + gap)
        hit = (i == 3)
        parts.append(box(bx, yrow, bw, bh, k, fill=HL if hit else FILL,
                         stroke=GOOD if hit else LINE, sw=2 if hit else 1.5, bold=hit))
    # стрілки: до середини (індекс 2, "мел") і до цілі (індекс 3, "сем")
    mid_x = x0 + 2 * (bw + gap) + bw / 2
    tgt_x = x0 + 3 * (bw + gap) + bw / 2
    parts.append(text(c, 128, "стрибаємо навпіл", size=12, color=NEG))
    parts.append(arrow(c, 158, mid_x, yrow - 8, color=NEG, sw=1.6))
    parts.append(arrow(mid_x, yrow - 8, tgt_x, yrow - 8, color=NEG, sw=1.6))
    parts.append(text(c, 300, "O(log n)", size=20, bold=True, color=INK))
    parts.append(fitbox(c - 138, 322, 276, 60, "двійковий пошук — O(log n),\nвставка зсуває решту — O(n)",
                        size=12, fill=BG, stroke="none", color=INK))

    # --- Панель 3: хеш ---
    c = cx[2]
    parts.append(text(c, 78, "3. Хеш-таблиця", size=14, bold=True))
    parts.append(box(c - 55, 96, 110, 28, '"сем"', size=13, bold=True))
    parts.append(arrow(c, 124, c, 146, color=LINE, sw=1.6))
    parts.append(box(c - 62, 146, 124, 28, "hash( ) mod 4", size=12, fill="#eef2fb", stroke=NEG))
    # маленький стовпчик кошиків 0..3, ціль — кошик 2
    bxw = 130; bstep = 25; bh3 = 22; by0 = 186
    for i in range(4):
        by = by0 + i * bstep
        hit = (i == 2)
        parts.append(box(c - bxw / 2, by, bxw, bh3, "кошик %d" % i, size=11,
                         fill=HL if hit else FILL, stroke=GOOD if hit else LINE,
                         sw=2 if hit else 1.3, bold=hit))
    b2y = by0 + 2 * bstep + bh3 / 2
    parts.append(arrow(c - bxw / 2 - 5, 176, c - bxw / 2 - 4, b2y, color=GOOD, sw=1.8))
    parts.append(text(c + bxw / 2 + 22, b2y + 4, "→ 2", size=13, bold=True, color=GOOD))
    parts.append(text(c, 300, "O(1)", size=20, bold=True, color=INK))
    parts.append(fitbox(c - 138, 322, 276, 60, "адресу рахуємо з ключа — одразу в ціль",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'lookup-approaches.svg'), W, H, *parts)


# ── Фіг. 2. Механізм хеш-таблиці ──────────────────────────────────────────
def fig_hash_table():
    W, H = 1000, 490
    parts = [text(W / 2, 30, "Хеш-таблиця: адреса кошика просто з ключа", size=17, bold=True)]

    # ліворуч — конвеєр ключ → хеш → остача → адреса
    lx = 40
    parts.append(box(lx, 90, 150, 40, 'ключ  "kyiv"', size=14, bold=True))
    parts.append(arrow(lx + 75, 130, lx + 75, 160, sw=1.7))
    parts.append(box(lx, 160, 150, 40, "хеш-функція", size=13, fill="#eef2fb", stroke=NEG))
    parts.append(arrow(lx + 75, 200, lx + 75, 228, sw=1.7))
    parts.append(box(lx - 6, 228, 162, 36, "h = 3 921 470 118", size=12))
    parts.append(arrow(lx + 75, 264, lx + 75, 292, sw=1.7))
    parts.append(box(lx, 292, 150, 38, "h mod 8  =  6", size=13, fill="#eef2fb", stroke=NEG, bold=True))
    parts.append(text(lx + 75, 356, "→ адреса кошика", size=12, color=MUTED))

    # праворуч — масив кошиків 0..7
    ax = 470; aw = 150; ah = 40; ay0 = 62
    for i in range(8):
        ay = ay0 + i * (ah + 4)
        hit = (i == 6)
        parts.append(box(ax, ay, aw, ah, "кошик %d" % i, size=13,
                         fill=HL if hit else FILL, stroke=GOOD if hit else LINE,
                         sw=2.2 if hit else 1.4, bold=hit))
    # стрілка від "h mod 8 = 6" до кошика 6
    y6 = ay0 + 6 * (ah + 4) + ah / 2
    parts.append(arrow(lx + 150, 311, ax - 2, y6, color=GOOD, sw=2))

    # ланцюжок колізії з кошика 6
    ch_y = y6
    n1x = ax + aw + 34
    parts.append(arrow(ax + aw, ch_y, n1x - 2, ch_y, color=LINE, sw=1.6))
    parts.append(box(n1x, ch_y - 20, 120, 40, "kyiv → …", size=12, fill=HL, stroke=GOOD))
    n2x = n1x + 120 + 30
    parts.append(arrow(n1x + 120, ch_y, n2x - 2, ch_y, color=LINE, sw=1.6))
    parts.append(box(n2x, ch_y - 20, 120, 40, "kiev → …", size=12))
    parts.append(text((n1x + n2x + 120) / 2 - 30, ch_y - 32, "ланцюжок колізії", size=12, color=MUTED))

    parts.append(fitbox(40, 438, 920, 40,
                        "два ключі з тією самою адресою висять у спільному кошику коротким списком (ланцюжком)",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'hash-table.svg'), W, H, *parts)


# ── Фіг. 3. Порівняння рушіїв ─────────────────────────────────────────────
def fig_tradeoffs():
    W, H = 980, 372
    parts = [text(W / 2, 30, "Один інтерфейс — різні рушії під різний доступ", size=17, bold=True)]

    labelw = 236
    cols = ["Точковий get", "Порядок,\nдіапазон", "Запис", "На диску"]
    ncol = len(cols)
    x0 = 24; y0 = 58
    colw = (W - 2 * x0 - labelw) / ncol          # ширина колонки-властивості
    hrow = 50; rrow = 66

    # шапка
    for j, cname in enumerate(cols):
        cxx = x0 + labelw + j * colw
        parts.append(rect(cxx, y0, colw, hrow, fill="#eef2fb", stroke=LINE, sw=1.3))
        parts.append(fitbox(cxx + 4, y0 + 4, colw - 8, hrow - 8, cname, size=13, bold=True,
                            fill="none", stroke="none"))
    parts.append(rect(x0, y0, labelw, hrow, fill="#f0f1f3", stroke=LINE, sw=1.3))
    parts.append(text(x0 + labelw / 2, y0 + hrow / 2 + 5, "Рушій", size=13, bold=True))

    # рядки: (назва, [(текст, колір)] × 4)
    rows = [
        ("Хеш-таблиця", [("O(1) середнє", GOOD), ("немає", WEAK), ("O(1)", GOOD), ("гірше", WEAK)]),
        ("Збалансоване дерево /\nB-дерево", [("O(log n)", INK), ("так", GOOD), ("O(log n)", INK), ("добре", GOOD)]),
        ("LSM-дерево (лог)", [("O(log n)+", INK), ("так", GOOD), ("дуже швидко", GOOD), ("чудово", GOOD)]),
    ]
    for i, (name, cells) in enumerate(rows):
        ry = y0 + hrow + i * rrow
        parts.append(rect(x0, ry, labelw, rrow, fill="#f7f8fa", stroke=LINE, sw=1.3))
        parts.append(fitbox(x0 + 6, ry + 6, labelw - 12, rrow - 12, name, size=13, bold=True,
                            fill="none", stroke="none"))
        for j, (txt, col) in enumerate(cells):
            cxx = x0 + labelw + j * colw
            parts.append(rect(cxx, ry, colw, rrow, fill=BG, stroke=LINE, sw=1.1))
            parts.append(fitbox(cxx + 4, ry + 6, colw - 8, rrow - 12, txt, size=13,
                                bold=(col != INK), color=col, fill="none", stroke="none"))

    render(os.path.join(OUT, 'tradeoffs.svg'), W, H, *parts)


# ── Фіг. 4. Розподіл по кільцю вузлів ─────────────────────────────────────
def fig_partitioning():
    W, H = 780, 500
    cx, cy, R = 390, 262, 150
    parts = [text(W / 2, 30, "Ключі на кільці вузлів: розподіл і копії", size=17, bold=True)]

    def pол(r, deg):
        a = math.radians(deg)
        return cx + r * math.cos(a), cy - r * math.sin(a)

    # кільце
    parts.append(circle(cx, cy, R, fill=BG, stroke=MUTED, sw=2))

    # вузли на 60/150/240/330°
    node_deg = {"A": 60, "B": 150, "C": 240, "D": 330}
    node_pt = {}
    for name, d in node_deg.items():
        px, py = pол(R, d)
        node_pt[name] = (px, py)
        parts.append(circle(px, py, 13, fill="#dfe7fb", stroke=NEG, sw=2))
        lx, ly = pол(R + 34, d)
        parts.append(text(lx, ly + 5, "Вузол " + name, size=13, bold=True, color=NEG))

    # ключі: (позначка, кут, вузол-власник за годинниковою)
    keys = [("k1", 105, "A"), ("k2", 200, "B"), ("k3", 300, "D")]
    for kname, d, owner in keys:
        px, py = pол(R, d)
        parts.append(rect(px - 9, py - 9, 18, 18, fill=HL, stroke=GOOD, sw=1.8, rx=3))
        lx, ly = pол(R - 30, d)
        parts.append(text(lx, ly + 4, kname, size=12, bold=True, color=GOOD))
        ox, oy = node_pt[owner]
        parts.append(arrow(px, py, ox, oy, color=GOOD, sw=1.6))

    # реплікація k1: пунктиром на наступні два вузли (B, C)
    px, py = pол(R, 105)
    for rep in ("B", "C"):
        ox, oy = node_pt[rep]
        parts.append(line(px, py, ox, oy, color=MUTED, sw=1.3, dash="5,4"))

    parts.append(mtext(cx, cy - 6, ["кільце", "хешу"], size=12, color=MUTED))

    parts.append(fitbox(30, 436, 720, 54,
                        "суцільна стрілка — власник ключа (найближчий вузол за годинниковою стрілкою);\n"
                        "пунктир — копії ключа k1 на сусідніх вузлах для відмовостійкості",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'partitioning.svg'), W, H, *parts)

# ── Фіг. 5. Анатомія put (вставка proj-hash-kv-store) ─────────────────────
DEC  = "#fff6e0"   # заливка розвилки
DECS = "#b7791f"   # обвід розвилки


def fig_put_anatomy():
    W, H = 980, 700
    parts = [text(W / 2, 30, "Що робить put(«dog», 7) крок за кроком", size=17, bold=True)]

    mx, mw = 70, 360           # ліва (головна) колонка
    mc = mx + mw / 2
    rx, rw = 610, 320          # права колонка — вихід із розвилки
    rc = rx + rw / 2

    def step(y, h, s, size=13, fill=FILL, stroke=LINE, bold=False, color=INK):
        return fitbox(mx, y, mw, h, s, size=size, fill=fill, stroke=stroke, bold=bold, color=color)

    # 1 — старт
    parts.append(step(60, 40, 'put("dog", 7)', size=15, bold=True, fill=HL, stroke=GOOD))
    parts.append(arrow(mc, 100, mc, 126, sw=1.7))
    # 2 — хеш
    parts.append(step(126, 44, 'h = хеш("dog") = 0xE6685B61', size=13,
                      fill="#eef2fb", stroke=NEG))
    parts.append(arrow(mc, 170, mc, 196, sw=1.7))
    # 3 — індекс кошика
    parts.append(step(196, 44, "i = h & (m − 1) = 1", size=13, fill="#eef2fb", stroke=NEG, bold=True))
    parts.append(text(mx + mw + 16, 222, "m = 8", size=12, color=MUTED, anchor="start"))
    parts.append(arrow(mc, 240, mc, 266, sw=1.7))
    # 4 — прохід ланцюжком
    parts.append(step(266, 44, "пройти ланцюжок кошика 1", size=13))
    parts.append(arrow(mc, 310, mc, 336, sw=1.7))
    # 5 — розвилка «ключ уже є?»
    parts.append(fitbox(mx, 336, mw, 52, 'ключ "dog" уже в ланцюжку?', size=13,
                        fill=DEC, stroke=DECS, sw=2, rx=18))
    #     гілка «так» → оновити
    parts.append(arrow(mx + mw, 362, rx - 2, 362, color=DECS, sw=1.7))
    parts.append(text((mx + mw + rx) / 2, 352, "так", size=12, bold=True, color=DECS))
    parts.append(fitbox(rx, 338, rw, 48, "оновити значення на місці;\nn не змінюється", size=12,
                        fill=HL, stroke=GOOD))
    parts.append(text(rc, 404, "кінець", size=12, color=MUTED))
    #     гілка «ні» вниз
    parts.append(arrow(mc, 388, mc, 428, color=DECS, sw=1.7))
    parts.append(text(mc + 24, 412, "ні", size=12, bold=True, color=DECS))
    # 6 — новий вузол
    parts.append(step(428, 48, "новий вузол у голову ланцюжка;\nn += 1", size=13))
    parts.append(arrow(mc, 476, mc, 502, sw=1.7))
    # 7 — розвилка «чи не тісно?»
    parts.append(fitbox(mx, 502, mw, 52, "n / m  >  0.75 ?", size=14,
                        fill=DEC, stroke=DECS, sw=2, rx=18, bold=True))
    #     гілка «ні» → кінець
    parts.append(arrow(mx + mw, 528, rx - 2, 528, color=DECS, sw=1.7))
    parts.append(text((mx + mw + rx) / 2, 518, "ні", size=12, bold=True, color=DECS))
    parts.append(fitbox(rx, 508, rw, 40, "кінець", size=13, fill=BG, stroke=MUTED))
    #     гілка «так» вниз
    parts.append(arrow(mc, 554, mc, 594, color=DECS, sw=1.7))
    parts.append(text(mc + 24, 578, "так", size=12, bold=True, color=DECS))
    # 8 — розширення
    parts.append(step(594, 50, "розширити: m ×= 2, перехешувати всі n пар", size=13,
                      fill="#fdecea", stroke=WEAK, bold=True))
    parts.append(text(mx + mw + 16, 613, "рідко:", size=12, color=MUTED, anchor="start"))
    parts.append(text(mx + mw + 16, 631, "O(n), але", size=12, color=MUTED, anchor="start"))
    parts.append(text(mx + mw + 16, 649, "розмазане", size=12, color=MUTED, anchor="start"))

    parts.append(fitbox(70, 662, 500, 28,
                        "усе, крім останнього кроку, — стала робота",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'put-anatomy.svg'), W, H, *parts)


# ── Фіг. 6. Розширення й перехешування ────────────────────────────────────
def fig_resize_rehash():
    W, H = 1060, 640
    parts = [text(W / 2, 30, "Розширення: маска бере ще один біт", size=17, bold=True)]

    # ── ліва таблиця m = 8 ──
    lx, lw, lh, lgap = 46, 62, 34, 6
    ly0 = 96
    parts.append(text(lx + 150, 66, "було:  m = 8,  n = 7  →  α = 0.875", size=13, bold=True, color=WEAK))
    chains8 = {0: ["owl"], 1: ["act", "dog"], 3: ["cat"], 4: ["cot"], 5: ["fox", "elk"]}
    nodew, nodeh, nodegap = 62, 26, 26
    y_of8 = {}
    for i in range(8):
        y = ly0 + i * (lh + lgap)
        y_of8[i] = y + lh / 2
        parts.append(box(lx, y, lw, lh, str(i), size=13, bold=True,
                         fill="#f0f1f3" if i in chains8 else BG))
        for j, k in enumerate(chains8.get(i, [])):
            nx = lx + lw + nodegap + j * (nodew + nodegap)
            parts.append(arrow(nx - nodegap + 2, y + lh / 2, nx - 3, y + lh / 2, color=MUTED, sw=1.4))
            hot = (k == "fox")
            parts.append(box(nx, y + (lh - nodeh) / 2, nodew, nodeh, k, size=12,
                             fill="#fdecea" if hot else FILL, stroke=WEAK if hot else LINE,
                             sw=2 if hot else 1.4, bold=hot, color=WEAK if hot else INK))

    # ── права таблиця m = 16 ──
    rx, rw2, rh, rgap = 700, 62, 24, 4
    ry0 = 82
    parts.append(text(rx + 130, 66, "стало:  m = 16,  α = 0.4375", size=13, bold=True, color=GOOD))
    chains16 = {0: ["owl"], 1: ["act", "dog"], 3: ["cat"], 4: ["cot"], 5: ["elk"], 13: ["fox"]}
    y_of16 = {}
    for i in range(16):
        y = ry0 + i * (rh + rgap)
        y_of16[i] = y + rh / 2
        parts.append(box(rx, y, rw2, rh, str(i), size=12, bold=True,
                         fill="#f0f1f3" if i in chains16 else BG))
        for j, k in enumerate(chains16.get(i, [])):
            nx = rx + rw2 + 20 + j * (nodew + 20)
            parts.append(arrow(nx - 18, y + rh / 2, nx - 3, y + rh / 2, color=MUTED, sw=1.3))
            hot = (k == "fox")
            parts.append(box(nx, y + (rh - nodeh) / 2, nodew, nodeh, k, size=12,
                             fill="#fdecea" if hot else FILL, stroke=WEAK if hot else LINE,
                             sw=2 if hot else 1.4, bold=hot, color=WEAK if hot else INK))

    # ── переїзд fox: 5 → 13 (коридор y_of8[5] між рамками, стояк — праворуч від них) ──
    VX = 662
    parts.append(line(lx + lw + nodegap + nodew, y_of8[5], VX, y_of8[5], color=WEAK, sw=1.8, dash="6,4"))
    parts.append(line(VX, y_of8[5], VX, y_of16[13], color=WEAK, sw=1.8, dash="6,4"))
    parts.append(arrow(VX, y_of16[13], rx - 4, y_of16[13], color=WEAK, sw=1.8))
    parts.append(text(430, y_of8[5] - 12, "переїхав", size=12, bold=True, color=WEAK))

    # ── правило посередині (вище коридору) ──
    parts.append(fitbox(300, 150, 330, 116,
                        "нова маска = 15 замість 7:\nдодався рівно один біт — біт 3.\n\n"
                        "i_нов  =  i_стар      (біт 3 = 0)\n"
                        "i_нов  =  i_стар + 8  (біт 3 = 1)",
                        size=12, fill="#eef2fb", stroke=NEG, sw=1.6))

    # ── розбір двох ключів кошика 5 (нижче коридору) ──
    parts.append(fitbox(300, 360, 330, 130,
                        "кошик 5 розпався надвоє:\n\n"
                        "fox: …1101₂   біт 3 = 1  →  5 + 8 = 13\n"
                        "elk: …0101₂   біт 3 = 0  →  5\n\n"
                        "act і dog лишились разом у кошику 1",
                        size=12, fill=BG, stroke=MUTED, sw=1.4))

    parts.append(fitbox(46, 578, 600, 48,
                        "жодна пара не міняє кошик «навмання»: кожна або лишається на місці,\n"
                        "або зсувається рівно на старий розмір таблиці",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'resize-rehash.svg'), W, H, *parts)


# ══ Фігури до вставки math-load-factor.md ══════════════════════════════════

# ── Фіг. 7. Однакове α — різна ціна (другий момент) ────────────────────────
def fig_second_moment():
    W, H = 1020, 500
    parts = [text(W / 2, 30, "Однакове α — різна ціна: усе вирішує сума квадратів", size=17, bold=True)]

    def panel(cx, title, sub, loads, s2, cost, ok):
        p = []
        col = GOOD if ok else WEAK
        p.append(rect(cx - 240, 50, 480, 292, fill=BG, stroke=MUTED, sw=1.2))
        p.append(text(cx, 74, title, size=14, bold=True, color=col))
        p.append(text(cx, 94, sub, size=12, color=MUTED))
        bx = cx - 224; bw = 70; bh = 20; y0 = 112; step = 28
        for j in range(8):
            by = y0 + j * step
            p.append(box(bx, by, bw, bh, "кошик %d" % j, size=10))
            if loads[j] == 0:
                p.append(text(bx + bw + 16, by + bh / 2 + 4, "—", size=12,
                              color=MUTED, anchor="start"))
            for t in range(loads[j]):
                kx = bx + bw + 14 + t * 25
                p.append(rect(kx, by + 1, 20, 18, fill=HL, stroke=col, sw=1.4, rx=3))
            p.append(text(cx + 234, by + bh / 2 + 4, "L%d=%d" % (j, loads[j]),
                          size=10, color=MUTED, anchor="end"))
        p.append(fitbox(cx - 240, 356, 480, 106,
                        "Σ Lⱼ = 8        α = 8/8 = 1        ← однакове!\n"
                        "Σ Lⱼ² = %d                          ← ось де різниця\n"
                        "очікувана вартість get = %s" % (s2, cost),
                        size=13, fill="#f7f8fa", stroke=col, sw=1.6))
        return p

    parts += panel(258, "Добра хеш-функція", "8 ключів рівно по 8 кошиках",
                   [1] * 8, 8, "1.0 порівняння", True)
    parts += panel(762, "Хеш-функція h(k) = 0", "ті самі 8 ключів — усі в кошик 0",
                   [8, 0, 0, 0, 0, 0, 0, 0], 64, "4.5 порівняння", False)

    render(os.path.join(OUT, 'load-factor-second-moment.svg'), W, H, *parts)


# ── Фіг. 8. Пуассонів розподіл довжин кошиків ──────────────────────────────
def fig_poisson():
    W, H = 960, 470
    parts = [text(W / 2, 30, "Довжини кошиків при α = 0.75: хвіст, тонший за експоненту", size=17, bold=True)]

    lam = 0.75
    pr = []
    fact = 1.0
    for k in range(9):
        if k > 0:
            fact *= k
        pr.append(math.exp(-lam) * (lam ** k) / fact)

    x0, y0 = 108, 330
    plot_w, plot_h = 700, 224
    bw = 44
    step = plot_w / 9.0

    parts.append(line(x0, y0, x0 + plot_w, y0, color=INK, sw=1.8))
    parts.append(line(x0, y0, x0, y0 - plot_h - 10, color=INK, sw=1.8))
    parts.append(text(x0 - 52, y0 - plot_h / 2, "Pr[Lⱼ = k]", size=12, color=MUTED))
    parts.append(text(x0 + plot_w / 2, y0 + 56, "k — довжина ланцюжка в кошику", size=13))

    for k in range(9):
        cxb = x0 + step * k + step / 2
        h = pr[k] / pr[0] * plot_h
        parts.append(rect(cxb - bw / 2, y0 - h, bw, h, fill=HL, stroke=GOOD, sw=1.6, rx=3))
        parts.append(text(cxb, y0 + 20, str(k), size=13, bold=True))
        lbl = ("%.3f" % pr[k]) if pr[k] >= 0.001 else ("%.0e" % pr[k])
        parts.append(text(cxb, y0 - h - 9, lbl, size=10, color=MUTED))

    cx8 = x0 + step * 8 + step / 2
    parts.append(line(cx8, y0 - 92, cx8, y0 - 12, color=WEAK, sw=1.4, dash="4,3"))
    parts.append(fitbox(cx8 - 208, y0 - 148, 190, 50,
                        "поріг Java: кошик\nстає деревом", size=11,
                        fill="#fdecea", stroke=WEAK, sw=1.4))

    parts.append(fitbox(50, 384, 860, 58,
                        "Pr[Lⱼ = k] ≈ e^(−α)·α^k / k!  — факторіал у знаменнику гасить хвіст швидше за будь-яку експоненту:\n"
                        "кошик на 4 ключі — раз на 160, на 8 ключів — раз на 850 тисяч. Довгий ланцюжок випадково НЕ трапляється.",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'load-factor-poisson.svg'), W, H, *parts)


# ── Фіг. 9. Геометрична сума проти арифметичної ────────────────────────────
def fig_growth():
    W, H = 1020, 500
    parts = [text(W / 2, 30, "Чому подвоєння, а не приріст: геометрична сума проти арифметичної", size=17, bold=True)]

    base_y = 296
    max_h = 168

    def panel(cx, title, sub, costs, total, note, ok):
        p = []
        col = GOOD if ok else WEAK
        p.append(rect(cx - 240, 50, 480, 288, fill=BG, stroke=MUTED, sw=1.2))
        p.append(text(cx, 74, title, size=14, bold=True, color=col))
        p.append(text(cx, 94, sub, size=12, color=MUTED))
        n = len(costs)
        span = 396.0
        bw = 32
        step = span / n
        bx0 = cx - span / 2
        p.append(line(bx0 - 10, base_y, bx0 + span + 10, base_y, color=INK, sw=1.6))
        mx = float(max(costs))
        for i, c in enumerate(costs):
            bxx = bx0 + step * i + step / 2
            h = c / mx * max_h
            p.append(rect(bxx - bw / 2, base_y - h, bw, h, fill=HL if ok else "#fdecea",
                          stroke=col, sw=1.5, rx=3))
            p.append(text(bxx, base_y - h - 8, str(c), size=11, color=INK, bold=True))
        p.append(text(cx, base_y + 22, "кожен стовпчик — одне перекладання таблиці", size=11, color=MUTED))
        p.append(fitbox(cx - 240, 352, 480, 60, "%s\n%s" % (total, note),
                        size=13, fill="#f7f8fa", stroke=col, sw=1.6))
        return p

    parts += panel(258, "Подвоєння місткості (r = 2)", "перекладання на 1, 2, 4, 8, 16, 32",
                   [1, 2, 4, 8, 16, 32],
                   "копіювань разом: 1+2+4+8+16+32 = 63 < 2n",
                   "останнє важить більше за всі попередні разом", True)
    parts += panel(762, "Приріст на стале c = 8", "перекладання на 8, 16, 24, 32, 40, 48, 56",
                   [8, 16, 24, 32, 40, 48, 56],
                   "копіювань разом: 8+16+…+56 = 224  ≈  n²/(2c)",
                   "жодне не мале — сума росте квадратично", False)

    parts.append(fitbox(50, 428, 920, 54,
                        "Обидві таблиці дійшли до n = 64. Подвоєння: 63 копіювання. Приріст на 8: 224 — і розрив росте разом з n:\n"
                        "при n = 10⁶ подвоєння дає ≈ 10⁶ копіювань, а приріст на 1000 — ≈ 5·10⁸: у 500 разів більше.",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'load-factor-growth.svg'), W, H, *parts)


# ── Фіг. 10. Метод потенціалу: пилка, що з'їдає сплески ────────────────────
def fig_potential():
    W, H = 1020, 560
    parts = [text(W / 2, 30, "Метод потенціалу: Φ = 2n − m з'їдає сплески", size=17, bold=True)]

    # (номер вставки, фактична вартість, Φ після вставки)
    ops = [(1, 1, 1), (2, 2, 2), (3, 3, 2), (4, 1, 4), (5, 5, 2), (6, 1, 4),
           (7, 1, 6), (8, 1, 8), (9, 9, 2), (10, 1, 4), (11, 1, 6), (12, 1, 8),
           (13, 1, 10), (14, 1, 12), (15, 1, 14), (16, 1, 16)]

    x0 = 96
    span = 800
    step = span / len(ops)
    bw = 28

    # ── верхній графік: фактична вартість + амортизована ──
    ty = 248
    th = 160
    parts.append(text(x0 + span / 2, 64, "фактична вартість однієї вставки", size=13, bold=True))
    parts.append(line(x0 - 12, ty, x0 + span + 12, ty, color=INK, sw=1.6))
    parts.append(line(x0 - 12, ty, x0 - 12, ty - th - 14, color=INK, sw=1.6))
    for i, (num, act, _) in enumerate(ops):
        bxx = x0 + step * i + step / 2
        h = act / 9.0 * th
        spike = act > 1
        parts.append(rect(bxx - bw / 2, ty - h, bw, h,
                          fill="#fdecea" if spike else FILL,
                          stroke=WEAK if spike else LINE, sw=1.6 if spike else 1.2, rx=3))
        if spike:
            parts.append(text(bxx, ty - h - 8, str(act), size=11, bold=True, color=WEAK))
        parts.append(text(bxx, ty + 18, str(num), size=10, color=MUTED))
    y3 = ty - 3 / 9.0 * th
    parts.append(line(x0 - 12, y3, x0 + span + 12, y3, color=GOOD, sw=2.2, dash="7,4"))
    parts.append(text(x0 + span + 16, y3 + 4, "ам = 3", size=12, bold=True,
                      color=GOOD, anchor="start"))
    parts.append(text(x0 + span / 2, ty + 40, "номер вставки", size=11, color=MUTED))

    # ── нижній графік: потенціал Φ ──
    py = 480
    ph = 120
    parts.append(text(x0 + span / 2, 304, "потенціал Φ = 2n − m", size=13, bold=True, color=NEG))
    parts.append(line(x0 - 12, py, x0 + span + 12, py, color=INK, sw=1.6))
    parts.append(line(x0 - 12, py, x0 - 12, py - ph - 14, color=INK, sw=1.6))
    pts = []
    for i, (num, _, phi) in enumerate(ops):
        bxx = x0 + step * i + step / 2
        pts.append((bxx, py - phi / 16.0 * ph))
    for i in range(len(pts) - 1):
        parts.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=NEG, sw=2))
    for (bxx, byy) in pts:
        parts.append(circle(bxx, byy, 4, fill=NEG, stroke=NEG, sw=1))
    parts.append(text(x0 + span / 2, py + 24, "номер вставки", size=11, color=MUTED))

    parts.append(fitbox(50, 504, 920, 44,
                        "Сплеск фактичної вартості (перекладання) точно збігається з обвалом Φ: ам = факт + ΔΦ = 3 щоразу.",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'load-factor-potential.svg'), W, H, *parts)


# ══ Фігури до вставки hist-associative-to-dynamo.md ════════════════════════

AMBER = "#b7791f"   # третя смуга — мережева доба


# ── Фіг. 11. Сімдесят років, той самий інтерфейс ───────────────────────────
def fig_timeline():
    W, H = 1180, 480
    parts = [text(W / 2, 32, "Сімдесят років ідеї «ключ — значення»: три нитки", size=17, bold=True)]

    labw = 152          # колонка з назвою нитки
    x0 = 190            # ліва межа перших карток
    cw, cgap = 146, 18  # картка й проміжок: 6·146 + 5·18 = 966
    ch = 88
    lane_y = [64, 196, 328]

    lanes = [
        ("Механізм:\nяк порахувати\nадресу", NEG, [
            ("1953", "Лун: ланцюжки\nу нотатці IBM"),
            ("1954", "Амдал, Бьоме,\nРочестер, Семюел:\nвідкрита адресація"),
            ("1956", "Дьюмі: перша\nпублікація"),
            ("1957", "Єршов: те саме\nнезалежно, СРСР"),
            ("1957", "Петерсон: перша\nвелика праця"),
            ("1967", "слово «хешування»\nпотрапляє в друк"),
        ]),
        ("Поняття:\nсловник\nусередині мови", GOOD, [
            ("1960", "Lisp: асоціативні\nсписки (a-lists)"),
            ("1966", "MUMPS: globals —\nсловник на диску"),
            ("1967", "SNOBOL4: тип\nTABLE у мові"),
            ("1977", "awk: словник\nу один рядок"),
            ("1979", "dbm: хеш на диску\n(Unix V7)"),
            ("1987", "Perl: «хеш» стає\nпобутовим словом"),
        ]),
        ("Мережа:\nсловник більший\nза машину", AMBER, [
            ("1997", "консистентне\nхешування (STOC)"),
            ("2003", "memcached: словник\nперетнув мережу"),
            ("2007", "Dynamo (SOSP):\nдоступність вище\nза узгодженість"),
            ("2008", "Cassandra:\nDynamo + BigTable"),
            ("2009", "Redis; зустріч,\nщо назвала NoSQL"),
            ("2012", "DynamoDB: не\nалгоритм, а сервіс"),
        ]),
    ]

    for (lname, col, cards), ly in zip(lanes, lane_y):
        # смуга-підкладка
        parts.append(rect(24, ly - 6, W - 48, ch + 12, fill="#fafbfc", stroke=MUTED, sw=1.0))
        parts.append(fitbox(24, ly - 6, labw, ch + 12, lname, size=12, bold=True,
                            fill="none", stroke="none", color=col))
        for i, (year, label) in enumerate(cards):
            cx = x0 + i * (cw + cgap)
            parts.append(rect(cx, ly, cw, ch, fill=FILL, stroke=col, sw=1.6))
            parts.append(text(cx + cw / 2, ly + 21, year, size=15, bold=True, color=col))
            parts.append(fitbox(cx + 6, ly + 30, cw - 12, ch - 36, label, size=11,
                                fill="none", stroke="none"))

    parts.append(fitbox(24, 428, W - 48, 40,
                        "Інтерфейс put / get / delete не змінився за всі сімдесят років — "
                        "змінювалося обмеження під ним: спершу тіснота пам'яті, потім виразність мови, "
                        "потім диск, потім мережа, а наприкінці — ціна обслуговування.",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'kv-timeline.svg'), W, H, *parts)


# ── Фіг. 12. Dynamo: система, зібрана з чужих частин ───────────────────────
def fig_dynamo_assembly():
    W, H = 1120, 570
    parts = [text(W / 2, 32, "Dynamo не винайшов майже жодної своєї частини", size=17, bold=True)]

    # ── ліворуч: п'ять запозичених частин ──
    px, pw, ph = 40, 310, 64
    py = [70, 148, 226, 304, 382]
    borrowed = [
        "1979 · Кворуми для читання й запису\nДевід Гіффорд, SOSP",
        "1979 · Дерева Меркла\nРальф Меркл, патент США",
        "1987 · Gossip / anti-entropy\nDemers та ін., PODC, Xerox PARC",
        "1988 · Векторні годинники\nФідж і Маттерн, незалежно один від одного",
        "1997 · Консистентне хешування\nКаргер, Леман, Лейтон, Левін та ін., STOC",
    ]
    parts.append(text(px + pw / 2, 58, "узяте готовим", size=13, bold=True, color=MUTED))
    for s, y in zip(borrowed, py):
        parts.append(fitbox(px, y, pw, ph, s, size=12, fill=FILL, stroke=NEG, sw=1.5))

    # ── центр: Dynamo ──
    bx, bw2, by, bh2 = 470, 220, 183, 150
    parts.append(rect(bx, by, bw2, bh2, fill=HL, stroke=GOOD, sw=2.6))
    parts.append(text(bx + bw2 / 2, by + 44, "Dynamo", size=22, bold=True, color=GOOD))
    parts.append(fitbox(bx + 8, by + 60, bw2 - 16, bh2 - 72,
                        "SOSP, жовтень 2007\nдев'ятеро авторів", size=13,
                        fill="none", stroke="none"))

    # стрілки: частини → Dynamo (у чистому коридорі 350…470)
    for y, ty in zip(py, (198, 224, 255, 286, 314)):
        parts.append(arrow(px + pw + 4, y + ph / 2, bx - 4, ty, color=NEG, sw=1.5))

    # ── праворуч: власний внесок ──
    rx, rw3 = 762, 318
    parts.append(text(rx + rw3 / 2, 58, "власне Dynamo", size=13, bold=True, color=MUTED))
    parts.append(fitbox(rx, 150, rw3, 112,
                        "своє: нещільний кворум,\nпідказана передача (hinted handoff),\nвіртуальні вузли",
                        size=12, fill=FILL, stroke=AMBER, sw=1.8))
    parts.append(fitbox(rx, 300, rw3, 90,
                        "і головне — це працювало\nна бойових замовленнях\nі про це надрукували статтю",
                        size=12, fill="#fff6e0", stroke=AMBER, sw=1.8, bold=True))
    parts.append(arrow(bx + bw2 + 4, 240, rx - 4, 206, color=AMBER, sw=1.6))
    parts.append(arrow(bx + bw2 + 4, 290, rx - 4, 345, color=AMBER, sw=1.6))

    parts.append(fitbox(40, 460, W - 80, 74,
                        "Жодна з п'яти частин ліворуч не Amazonова, а найстаршій тут майже тридцять років.\n"
                        "Внесок Dynamo — не примітив, а система: дібрати частини під одну вимогу «ніколи не казати ні»,\n"
                        "змусити їх працювати разом на живому кошику покупця — і розповісти про це вголос.",
                        size=12, fill=BG, stroke="none", color=INK))

    render(os.path.join(OUT, 'dynamo-assembly.svg'), W, H, *parts)


if __name__ == "__main__":
    fig_lookup()
    fig_hash_table()
    fig_tradeoffs()
    fig_partitioning()
    fig_put_anatomy()
    fig_resize_rehash()
    fig_second_moment()
    fig_poisson()
    fig_growth()
    fig_potential()
    fig_timeline()
    fig_dynamo_assembly()
    print("OK: 12 фігур у", OUT)
