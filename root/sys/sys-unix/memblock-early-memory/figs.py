# -*- coding: utf-8 -*-
"""Фігури для теми «memblock: пам'ять до того, як з'явився розподільник сторінок»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

GRN_F = "#eafaf0"
BLU_F = "#eaf0fd"
RED_F = "#fdecea"
YEL_F = "#fff5e0"
GRY_F = "#eceff3"


# ── 1. Два масиви й вільні вікна ───────────────────────────────────────────
def fig_two_lists():
    W, H = 1400, 470
    X0, X1 = 260, 1250
    SPAN = 8.0  # ГіБ

    def px(g):
        return X0 + (g / SPAN) * (X1 - X0)

    F = []

    # вісь адрес
    F.append(line(X0, 62, X1, 62, color=LINE, sw=1.2))
    for g in (0, 2, 4, 6, 8):
        F.append(line(px(g), 56, px(g), 68, color=LINE, sw=1.2))
        F.append(text(px(g), 42, "%d ГіБ" % g, size=13, color=MUTED))

    rowh = 46
    y_mem, y_res, y_free = 110, 230, 350

    # ── memory[]
    mem = [(0.0, 3.5), (4.0, 8.0)]
    for a, b in mem:
        F.append(rect(px(a), y_mem, px(b) - px(a), rowh, fill=BLU_F, stroke=LINE, sw=1.4))
    F.append(text(px(3.75), y_mem - 16, "діра адрес", size=13, color=MUTED))

    # ── reserved[]
    res = [(0.90, 1.00, "образ ядра", 0),
           (1.60, 1.75, "initramfs", 1),
           (2.60, 2.90, "область CMA", 0),
           (3.35, 3.50, "таблиці прошивки", 1),
           (7.50, 8.00, "описувачі сторінок", 0)]
    for a, b, lab, rowi in res:
        F.append(rect(px(a), y_res, max(px(b) - px(a), 7), rowh, fill=RED_F, stroke=POS, sw=1.4))
        ly = y_res + rowh + 26 + rowi * 26
        F.append(text((px(a) + px(b)) / 2, ly, lab, size=13, color=MUTED))

    # ── вільно = memory − reserved
    free = [(0.00, 0.90), (1.00, 1.60), (1.75, 2.60), (2.90, 3.35), (4.00, 7.50)]
    for a, b in free:
        F.append(rect(px(a), y_free, px(b) - px(a), rowh, fill=GRN_F, stroke=NEG, sw=1.4))

    # підписи рядків ліворуч
    F.append(mtext(30, y_mem + 16, ["memory[]", "що взагалі є"],
                   size=14, anchor="start", color=INK))
    F.append(mtext(30, y_res + 16, ["reserved[]", "що вже зайняте"],
                   size=14, anchor="start", color=INK))
    F.append(mtext(30, y_free + 16, ["вільно", "рахують щоразу"],
                   size=14, anchor="start", color=INK))

    render(os.path.join(IMG, 'memblock-lists.svg'), W, H, *F,
           title="Два масиви memblock і вільні вікна між ними")


# ── 2. Чому коло замикається ───────────────────────────────────────────────
def fig_bootstrap_chain():
    W, H = 1060, 720
    CX = 400
    F = []

    steps = [
        (90, "Розподільник сторінок роздає кадри\nі веде списки вільних блоків", BLU_F, LINE),
        (240, "Список тримають описувачі:\nна кожен кадр — своя структура", BLU_F, LINE),
        (390, "На 64 ГіБ описувачі важать ≈ 1 ГіБ —\nїх треба розмістити ДО першої роздачі", YEL_F, LINE),
        (540, "Отже, потрібен розподільник, чий власний\nоблік не потребує розподільника", RED_F, POS),
        (665, "memblock: два масиви діапазонів,\nвкомпільовані в образ ядра", GRN_F, NEG),
    ]
    boxes = []
    for cy, s, fill, stroke in steps:
        body, w, h = textbox(CX, cy, s, size=14, pad=14, fill=fill, stroke=stroke, sw=1.6)
        F.append(body)
        boxes.append((cy, h))

    labels = ["щоб працювати, потребує",
              "які самі треба виділити",
              "а виділяти ще нічим",
              "розрив кола"]
    for i in range(4):
        cy0, h0 = boxes[i]
        cy1, h1 = boxes[i + 1]
        y0 = cy0 + h0 / 2 + 4
        y1 = cy1 - h1 / 2 - 6
        F.append(arrow(CX, y0, CX, y1, color=LINE, sw=1.8))
        F.append(text(700, (y0 + y1) / 2 + 5, labels[i], size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'bootstrap-chain.svg'), W, H, *F,
           title="Чому першому розподільникові не можна мати власних структур")


# ── 3. Передача естафети ───────────────────────────────────────────────────
def fig_handover():
    W, H = 1440, 500
    PY, PH = 200, 230
    F = []

    panels = [
        (40, 360, "Прошивка передала карту",
         ["e820 · таблиці EFI · дерево пристроїв",
          "діапазони описані, але власника",
          "в них ще немає",
          "виділити не можна нічим"], GRY_F, LINE),
        (500, 400, "Доба memblock",
         ["memblock_add — що взагалі є",
          "memblock_reserve — що зайняте",
          "memblock_alloc — виділити зверху вниз",
          "описувачі, таблиці, pgdat, CMA"], YEL_F, LINE),
        (1000, 400, "Після memblock_free_all()",
         ["вільні діапазони віддані buddy",
          "далі — alloc_pages і kmalloc",
          "код і масиви memblock звільнено",
          "разом із рештою секцій .init"], GRN_F, NEG),
    ]
    for x, w, title_s, lines, fill, stroke in panels:
        F.append(rect(x, PY, w, PH, fill=fill, stroke=stroke, sw=1.6))
        F.append(text(x + w / 2, PY + 34, title_s, size=15, color=INK, bold=True))
        for i, ln in enumerate(lines):
            F.append(text(x + 20, PY + 76 + i * 34, ln, size=13, color=MUTED, anchor="start"))

    F.append(arrow(410, PY + PH / 2, 490, PY + PH / 2, color=LINE, sw=2))
    F.append(arrow(910, PY + PH / 2, 990, PY + PH / 2, color=LINE, sw=2))
    F.append(text(450, 150, "розбір карти", size=13, color=MUTED))
    F.append(text(950, 150, "передача естафети", size=13, color=MUTED))

    render(os.path.join(IMG, 'memblock-handover.svg'), W, H, *F,
           title="Три доби ранньої пам'яті та момент передачі")


# ── 4. Куди дівається різниця між Σmemory і MemTotal ───────────────────────
def fig_balance():
    W, H = 1300, 570
    X0, X1 = 290, 1240
    SPAN = 16.0  # ГіБ

    def px(g):
        return X0 + (g / SPAN) * (X1 - X0)

    def bar(a, b, y, h, fill, stroke):
        return rect(px(a), y, max(px(b) - px(a), 9), h, fill=fill, stroke=stroke, sw=1.4)

    F = []
    BH = 44

    # вісь
    F.append(line(X0, 62, X1, 62, color=LINE, sw=1.2))
    for g in (0, 4, 8, 12, 16):
        F.append(line(px(g), 56, px(g), 68, color=LINE, sw=1.2))
        F.append(text(px(g), 42, "%d ГіБ" % g, size=13, color=MUTED))

    rows = [
        (95, ["Σ memblock.memory", "знімок у debugfs"],
         [(0.0, 15.9375, BLU_F, LINE), (15.9375, 16.0, GRY_F, LINE)],
         "16.00 ГіБ — усе, що прошивка назвала пам'яттю; сірий хвіст — 64 МіБ NOMAP, "
         "яких ядро не відображає й нікому не роздає"),
        (205, ["кадри з описувачем", "physpages"],
         [(0.0, 15.9375, BLU_F, LINE)],
         "15.94 ГіБ — рівно друге число в рядку журналу «Memory: … / … available»"),
        (315, ["мить memblock_free_all()", "хто що дістав"],
         [(0.0, 15.1875, GRN_F, NEG), (15.1875, 15.9375, RED_F, POS)],
         "15.19 ГіБ пішло розподільникові сторінок · 768 МіБ лишилося в reserved "
         "(описувачі, образ ядра, initramfs, 256 МіБ CMA)"),
        (425, ["MemTotal зараз", "/proc/meminfo"],
         [(0.0, 15.1875, GRN_F, NEG), (15.1875, 15.4375, YEL_F, LINE),
          (15.4375, 15.4766, YEL_F, LINE)],
         "15.48 ГіБ — до розподільника пізніше повернулися CMA (256 МіБ) "
         "та звільнені init-секції з initramfs (40 МіБ)"),
    ]

    for y, label, segs, note in rows:
        for a, b, fill, stroke in segs:
            F.append(bar(a, b, y, BH, fill, stroke))
        F.append(mtext(25, y + 16, label, size=14, anchor="start", color=INK))
        F.append(text(X0, y + BH + 26, note, size=13, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'memblock-balance.svg'), W, H, *F,
           title="Від суми memblock.memory до MemTotal: куди дівається різниця")


fig_two_lists()
fig_bootstrap_chain()
fig_handover()
fig_balance()
print("ok")
