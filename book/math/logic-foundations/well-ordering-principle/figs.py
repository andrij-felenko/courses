# -*- coding: utf-8 -*-
"""Фігури до статті «Принцип повного впорядкування».
Запуск:  python figs.py   → пише SVG у ./img/
  least    — у яких множин є найменший елемент (ℕ так, ℤ⁻ ні, (0,1) ні)
  descent  — спуск у ℕ мусить обірватися; у ℚ триває без кінця
  division — ділення з остачею: остача = найменший елемент множини a−b·k
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eaf7ef"
REDFILL = "#fdecea"
BLUEFILL = "#eaf0fd"
ROW = "#f4f6f8"


# ── 1. У яких множин є найменший елемент ─────────────────────────────────────
def fig_least():
    W, H = 960, 470
    f = [text(W / 2, 32, "Чи є в множині найменший елемент?", size=19, bold=True),
         text(W / 2, 54, "принцип обіцяє його лише для натуральних чисел — не для цілих і не для дійсних",
              size=12.5, color=MUTED, italic=True)]

    # три горизонтальні смуги-приклади
    lane_x0, lane_x1 = 250, 880       # де живе числова пряма кожного прикладу
    label_x = 60                       # ліворуч — назва множини
    verdict_x = 905                    # праворуч — так/ні
    lanes_y = [150, 270, 390]

    # ── смуга 1: підмножина ℕ — найменший Є ──
    y = lanes_y[0]
    f.append(text(label_x, y - 30, "Натуральні:", size=13.5, bold=True, anchor="start"))
    f.append(text(label_x, y - 10, "парні ≥ 4", size=12, color=MUTED, anchor="start"))
    f.append(line(lane_x0, y, lane_x1, y, color=INK, sw=1.6))
    pts = [(300, "4", True), (400, "6", False), (500, "8", False),
           (600, "10", False), (700, "12", False)]
    for x, lab, least in pts:
        f.append(circle(x, y, 8, fill=(GREENFILL if least else BG),
                        stroke=(FIELD if least else INK), sw=(2.4 if least else 1.5)))
        f.append(text(x, y - 18, lab, size=12.5, bold=least, color=(FIELD if least else INK)))
    f.append(text(770, y - 4, "…", size=20, bold=True))
    f.append(text(300, y + 30, "найменший", size=11.5, bold=True, color=FIELD))
    f.append(('<path d="M 300 %d L 300 %d" fill="none" stroke="%s" stroke-width="1.8" '
              'marker-end="url(#arrow)"/>' % (y + 22, y + 12, FIELD)))
    box1, w1, h1 = textbox(verdict_x, y, "є", size=15, bold=True,
                           fill=GREENFILL, stroke=FIELD, color=FIELD, min_w=56)
    f.append(box1)

    # ── смуга 2: від'ємні цілі — найменшого НЕМА (спуск ліворуч) ──
    y = lanes_y[1]
    f.append(text(label_x, y - 30, "Цілі:", size=13.5, bold=True, anchor="start"))
    f.append(text(label_x, y - 10, "від'ємні", size=12, color=MUTED, anchor="start"))
    f.append(line(lane_x0, y, lane_x1, y, color=INK, sw=1.6))
    pts = [(760, "−1"), (660, "−2"), (560, "−3"), (460, "−4"), (360, "−5")]
    for x, lab in pts:
        f.append(circle(x, y, 8, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, y - 18, lab, size=12.5))
    # стрілка «менше без кінця» ліворуч
    f.append(arrow(320, y, lane_x0 + 8, y, color=POS, sw=2.0))
    f.append(text(300, y + 30, "меншає без кінця", size=11.5, bold=True, color=POS, anchor="start"))
    box2, w2, h2 = textbox(verdict_x, y, "нема", size=15, bold=True,
                           fill=REDFILL, stroke=POS, color=POS, min_w=56)
    f.append(box2)

    # ── смуга 3: відкритий проміжок (0,1) — найменшого НЕМА (згущення до 0) ──
    y = lanes_y[2]
    f.append(text(label_x, y - 30, "Дійсні:", size=13.5, bold=True, anchor="start"))
    f.append(text(label_x, y - 10, "проміжок (0,1)", size=12, color=MUTED, anchor="start"))
    f.append(line(lane_x0, y, lane_x1, y, color=INK, sw=1.6))
    # порожнє коло на 0 (край не входить)
    f.append(text(lane_x0, y - 18, "0", size=12.5, color=MUTED))
    f.append(circle(lane_x0, y, 7, fill=BG, stroke=MUTED, sw=1.6))
    f.append(text(lane_x1, y - 18, "1", size=12.5, color=MUTED))
    # точки, що згущуються до 0
    for x in (560, 470, 410, 372, 350, 338, 331):
        f.append(circle(x, y, 4.5, fill=INK, stroke=INK, sw=1))
    f.append(arrow(360, y, lane_x0 + 10, y, color=POS, sw=2.0))
    f.append(text(430, y + 30, "ближче до 0 без кінця (0 не входить)",
                  size=11.5, bold=True, color=POS, anchor="start"))
    box3, w3, h3 = textbox(verdict_x, y, "нема", size=15, bold=True,
                           fill=REDFILL, stroke=POS, color=POS, min_w=56)
    f.append(box3)

    render(os.path.join(IMG, "least.svg"), W, H, *f)


# ── 2. Спуск, який мусить обірватися (ℕ) проти нескінченного (ℚ) ──────────────
def fig_descent():
    W, H = 940, 430
    f = [text(W / 2, 32, "Спуск донизу: коли він мусить зупинитися", size=19, bold=True),
         text(W / 2, 54, "у натуральних числах є дно — падати вічно не можна; у раціональних дна немає",
              size=12.5, color=MUTED, italic=True)]

    # ── ліва панель: ℕ — сходинки до дна ──
    lx = 90
    f.append(text(lx + 150, 92, "Натуральні числа", size=15, bold=True, color=FIELD))
    steps = [("17", 0), ("9", 1), ("4", 2), ("2", 3), ("1", 4)]
    step_w, step_h = 70, 34
    base_x, top_y = lx + 40, 120
    for lab, i in steps:
        x = base_x + i * 46
        y = top_y + i * 44
        first = (i == 0)
        last = (i == len(steps) - 1)
        f.append(rect(x, y, step_w, step_h,
                      fill=(GREENFILL if last else ROW),
                      stroke=(FIELD if last else LINE), sw=(2.2 if last else 1.4), rx=6))
        f.append(text(x + step_w / 2, y + step_h / 2 + 5, lab, size=14, bold=(first or last)))
        if not last:
            nx = base_x + (i + 1) * 46
            ny = top_y + (i + 1) * 44
            f.append(arrow(x + step_w / 2 + 6, y + step_h,
                           nx + step_w / 2 - 6, ny, color=NEG, sw=1.8))
    # дно
    dy = top_y + (len(steps) - 1) * 44 + step_h + 22
    f.append(line(lx + 20, dy, lx + 340, dy, color=FIELD, sw=2.4))
    f.append(text(lx + 180, dy + 22, "ДНО: далі падати нікуди", size=12.5, bold=True, color=FIELD))
    f.append(text(lx + 180, dy + 42, "спуск обривається за скінченне число кроків",
                  size=11, color=MUTED, italic=True))

    # роздільник
    f.append(line(W / 2, 88, W / 2, 400, color="#d7dbe0", sw=1.4, dash="5,5"))

    # ── права панель: ℚ — спуск без кінця ──
    rx = 540
    f.append(text(rx + 150, 92, "Раціональні числа", size=15, bold=True, color=POS))
    qsteps = [("1", 0), ("½", 1), ("¼", 2), ("⅛", 3)]
    for lab, i in qsteps:
        x = rx + 40 + i * 46
        y = 120 + i * 44
        f.append(rect(x, y, step_w, step_h, fill=BLUEFILL, stroke=NEG, sw=1.4, rx=6))
        f.append(text(x + step_w / 2, y + step_h / 2 + 5, lab, size=14, bold=True))
        nx = rx + 40 + (i + 1) * 46
        ny = 120 + (i + 1) * 44
        f.append(arrow(x + step_w / 2 + 6, y + step_h,
                       nx + step_w / 2 - 6, ny, color=NEG, sw=1.8))
    # хвіст «…без кінця»
    tx = rx + 40 + 4 * 46
    ty = 120 + 4 * 44
    f.append(text(tx + step_w / 2, ty + 10, "…", size=22, bold=True, color=POS))
    f.append(text(rx + 175, ty + 40, "дна немає: вполовинюй вічно",
                  size=12.5, bold=True, color=POS))
    f.append(text(rx + 175, ty + 60, "найменшого елемента не існує",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "descent.svg"), W, H, *f)


# ── 3. Ділення з остачею через найменший елемент ─────────────────────────────
def fig_division():
    W, H = 940, 440
    f = [text(W / 2, 32, "Ділення з остачею: остача — це найменший невід'ємний залишок",
              size=18, bold=True),
         text(W / 2, 54, "приклад  a = 17,  b = 5:  беремо всі невід'ємні  17 − 5·k  і серед них найменший",
              size=12.5, color=MUTED, italic=True)]

    # числова пряма 17 − 5k
    ly = 210
    f.append(line(120, ly, 860, ly, color=INK, sw=1.6))
    # точки: k=0→17, k=1→12, k=2→7, k=3→2 (найменший невід'ємний), k=4→-3 (нижче нуля, поза S)
    marks = [(17, "17", 0, True), (12, "12", 1, True), (7, "7", 2, True),
             (2, "2", 3, True), (-3, "−3", 4, False)]
    # масштаб: значення від -3 до 17 → x від 150 до 830
    def vx(v):
        return 150 + (v + 3) * (830 - 150) / 20.0
    # позначка нуля
    f.append(line(vx(0), ly - 10, vx(0), ly + 10, color=MUTED, sw=1.4))
    f.append(text(vx(0), ly + 28, "0", size=12, color=MUTED))
    for v, lab, k, inS in marks:
        x = vx(v)
        least = (v == 2)
        col = FIELD if least else (POS if not inS else INK)
        fillc = GREENFILL if least else (REDFILL if not inS else BG)
        f.append(circle(x, ly, 9 if least else 7, fill=fillc, stroke=col, sw=(2.6 if least else 1.6)))
        f.append(text(x, ly - 20, lab, size=13, bold=(least or not inS), color=col))
        f.append(text(x, ly - 40, "k=%d" % k, size=11, color=MUTED))

    # зелена дужка: найменший = остача
    f.append(text(vx(2), ly + 34, "остача r = 2", size=13, bold=True, color=FIELD))
    f.append(('<path d="M %.1f %d L %.1f %d" fill="none" stroke="%s" stroke-width="1.8" '
              'marker-end="url(#arrow)"/>' % (vx(2), ly + 48, vx(2), ly + 14, FIELD)))
    # червона позначка: нижче нуля вже не беремо
    f.append(text(vx(-3), ly + 34, "< 0 — не беремо", size=11.5, bold=True, color=POS))

    # пояснювальні рамки внизу
    by = 320
    f.append(fitbox(120, by, 340, 88,
                    "S = { 17 − 5·k ≥ 0 } = { 17, 12, 7, 2 }\n\n"
                    "непорожня → має найменший елемент",
                    size=13, fill=ROW, stroke=LINE, color=INK))
    f.append(fitbox(500, by, 340, 88,
                    "найменший r = 2,  при  q = 3:\n"
                    "17 = 5·3 + 2,   0 ≤ 2 < 5\n\n"
                    "більший залишок (7) дав би менший (7−5=2)",
                    size=12.5, fill=GREENFILL, stroke=FIELD, color=INK))

    render(os.path.join(IMG, "division.svg"), W, H, *f)


# ── Хронологія теореми про повне впорядкування (для вставки hist-zermelo) ─────
def fig_timeline():
    W, H = 1180, 600
    f = [text(W / 2, 38, "Хронологія теореми про повне впорядкування", size=20, bold=True),
         text(W / 2, 62, "як Канторів «закон мислення» став аксіомою, що розколола математику",
              size=13, color=MUTED, italic=True)]

    spine_y = 315
    f.append(line(70, spine_y, 1120, spine_y, color=INK, sw=2.2))
    f.append(arrow(1095, spine_y, 1135, spine_y, color=INK, sw=2.2))

    # (x, рік, колір-акцент, заливка картки, рядки, картка згори?)
    events = [
        (150, "1883", INK,   ROW,
         ["Кантор", "«Grundlagen»", "всяку множину —", "цілком упорядкувати:",
          "«закон мислення»", "без доведення"], True),
        (370, "1900", INK,   ROW,
         ["Гільберт", "Париж, 1-ша проблема", "поряд із гіпотезою", "континууму:",
          "чи можна впорядкувати", "весь континуум?"], False),
        (590, "1904", FIELD, GREENFILL,
         ["Цермело", "лист Гільбертові,", "три сторінки —", "доведення теореми",
          "й виокремлена", "аксіома вибору"], True),
        (810, "1905", POS,   REDFILL,
         ["Розкол: «П'ять листів»", "Борель, Бер, Лебеґ —", "проти (вибір без",
          "правила); Адамар —", "за. Пеано, Пуанкаре", "теж критикують"], False),
        (1030, "1908", NEG,  BLUEFILL,
         ["Цермело: друге", "доведення + сім", "аксіом теорії множин", "(предок ZF).",
          "Теорема рівносильна", "аксіомі вибору"], True),
    ]
    cardw, cardh = 208, 150
    for x, year, acc, cfill, lines, above in events:
        if above:
            cy = 115
            f.append(line(x, cy + cardh, x, spine_y - 15, color=acc, sw=1.6))
        else:
            cy = spine_y + 35
            f.append(line(x, spine_y + 15, x, cy, color=acc, sw=1.6))
        f.append(fitbox(x - cardw / 2, cy, cardw, cardh, "\n".join(lines),
                        size=12.5, pad=9, fill=cfill, stroke=acc, sw=1.6, color=INK))
        # рік — біла пігулка на осі часу (перекриває лінію, тож напис читкий)
        box, w, h = textbox(x, spine_y, year, size=15, bold=True,
                            fill=BG, stroke=acc, color=acc, min_w=68)
        f.append(box)

    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


fig_timeline()  # згенерувати одразу — незалежно від блоку __main__ (паралельні правки файла)


# ── 4. Рецепт: як побудувати спадну міру (для вставки proj-termination) ───────
def fig_recipe():
    W, H = 1000, 780
    f = [text(W / 2, 34, "Як побудувати спадну міру", size=20, bold=True),
         text(W / 2, 56, "п'ять питань поспіль: пройшов усі — зупинку доведено; спіткнувся — бачиш, де саме",
              size=12.5, color=MUTED, italic=True)]

    cx0, cw = 110, 410                 # головна колонка
    cxc = cx0 + cw / 2                 # її вісь (для вертикальних стрілок)
    tx0, tw = 620, 350                 # колонка наслідків праворуч

    # два верхні кроки
    f.append(fitbox(cx0, 92, cw, 54, "1. Стан: які величини міняє прохід або виклик?",
                    size=13.5, fill=ROW, stroke=LINE, color=INK))
    f.append(arrow(cxc, 146, cxc, 190, color=INK, sw=1.7))
    f.append(fitbox(cx0, 190, cw, 54,
                    "2. Кандидат-міра: що спадає до умови виходу —\nвідстань, яку цикл закриває?",
                    size=13, fill=ROW, stroke=LINE, color=INK))
    f.append(arrow(cxc, 244, cxc, 288, color=INK, sw=1.7))

    # три питання-розвилки
    dec_y = [288, 400, 512]
    dec_txt = [
        "3. Спадає СТРОГО щоразу — на кожній гілці\nй у кожному виклику?",
        "4. Живе в ℕ — є дно, крок не менший за одиницю?",
        "5. Одного числа досить?",
    ]
    for y, s in zip(dec_y, dec_txt):
        f.append(fitbox(cx0, y, cw, 60, s, size=13, fill=BLUEFILL, stroke=NEG, color=INK))

    # вертикальні «так»-переходи вниз
    f.append(arrow(cxc, 348, cxc, 400, color=FIELD, sw=1.9))
    f.append(text(cxc + 18, 378, "так", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(cxc, 460, cxc, 512, color=FIELD, sw=1.9))
    f.append(text(cxc + 18, 490, "так", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(arrow(cxc, 572, cxc, 636, color=FIELD, sw=1.9))
    f.append(text(cxc + 18, 608, "так", size=12, bold=True, color=FIELD, anchor="start"))

    # праві наслідки (дві червоні глухі, одна синя-конструктивна)
    def branch(y, s, fill, stroke):
        mid = y + 30
        f.append(arrow(cx0 + cw, mid, tx0, mid, color=stroke, sw=1.7))
        f.append(text((cx0 + cw + tx0) / 2, mid - 8, "ні", size=11.5, bold=True, color=stroke))
        f.append(fitbox(tx0, y, tw, 60, s, size=12, fill=fill, stroke=stroke, color=INK))

    branch(288, "Ні — якась гілка лишає міру тією самою.\nЛанцюг спаду рветься: зупинка НЕ доведена.",
           REDFILL, POS)
    branch(400, "Ні — у ℝ чи в ℤ без дна спуск нескінченний:\n1 > ½ > ¼ > …   або   −1, −3, −5, …",
           REDFILL, POS)
    # синя гілка «одного числа мало» — не глуха, вливається у «Готово»
    y5 = 500
    mid5 = y5 + 32
    f.append(arrow(cx0 + cw, mid5, tx0, mid5, color=NEG, sw=1.7))
    f.append(text((cx0 + cw + tx0) / 2, mid5 - 8, "ні", size=11.5, bold=True, color=NEG))
    f.append(fitbox(tx0, y5, tw, 64,
                    "Ні — піднеси до кортежу за словниковим\nпорядком (ℕ×ℕ) або до структури за\nпідтермами. Обидва фундовані.",
                    size=11.5, fill=BLUEFILL, stroke=NEG, color=INK))
    # ця синя гілка теж веде вниз до «Готово»
    f.append(('<path d="M %.1f %d L %.1f %d L %.1f %d" fill="none" stroke="%s" '
              'stroke-width="1.7" marker-end="url(#arrow)"/>'
              % (tx0 + tw / 2, y5 + 64, tx0 + tw / 2, 662, 640, 662, NEG)))

    # підсумкова зелена смуга
    f.append(fitbox(150, 636, 700, 76,
                    "V: Стан → ℕ  (чи інша фундована множина),  строго спадна щокроку\n"
                    "⟹  нескінченного спуску немає  ⟹  зупинку доведено",
                    size=14, fill=GREENFILL, stroke=FIELD, color=INK))

    render(os.path.join(IMG, "recipe.svg"), W, H, *f)


# ── 5. Структурна рекурсія: спуск підтермами (для вставки proj-termination) ───
def fig_subterm():
    W, H = 1000, 560
    f = [text(W / 2, 34, "Структурна рекурсія: міра — саме дерево", size=19, bold=True),
         text(W / 2, 56, "кожен виклик — на власному піддереві; підтермовий порядок фундований, бо дерево скінченне",
              size=12.5, color=MUTED, italic=True)]

    # вузли дерева ( (3+4) × (5+6) )
    root = (300, 118)
    l2 = [(185, 248), (415, 248)]
    leaves = [(120, 378), (250, 378), (350, 378), (480, 378)]
    edges = [(root, l2[0]), (root, l2[1]),
             (l2[0], leaves[0]), (l2[0], leaves[1]),
             (l2[1], leaves[2]), (l2[1], leaves[3])]
    # ребра дерева + пунктирні стрілки «рекурсивний виклик»
    for a, b in edges:
        f.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=1.4))
    for a, b in edges:
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = (dx * dx + dy * dy) ** 0.5
        ax, ay = a[0] + dx / d * 26, a[1] + dy / d * 26
        bx, by = b[0] - dx / d * 24, b[1] - dy / d * 24
        f.append(arrow(ax, ay, bx, by, color=FIELD, sw=1.6))
    # вузли
    def node(p, lab, leaf=False):
        f.append(circle(p[0], p[1], (20 if leaf else 23),
                        fill=(GREENFILL if leaf else BLUEFILL),
                        stroke=(FIELD if leaf else NEG), sw=2.0))
        f.append(text(p[0], p[1] + 6, lab, size=16, bold=True,
                      color=(FIELD if leaf else NEG)))
    node(root, "×")
    node(l2[0], "+"); node(l2[1], "+")
    for p, lab in zip(leaves, ["3", "4", "5", "6"]):
        node(p, lab, leaf=True)
    f.append(text(300, 452, "внутрішній вузол → рекурсія в дітей;  листок → база, спуск спинився",
                  size=11.5, color=MUTED, italic=True))

    # права панель — пояснення
    px = 600
    f.append(fitbox(px, 96, 360, 82,
                    "Міра — саме ДЕРЕВО, а «менше» —\n«бути власним піддеревом».",
                    size=13, fill=ROW, stroke=LINE, color=INK))
    f.append(fitbox(px, 194, 360, 96,
                    "Порядок фундований, бо дерево скінченне:\nланцюга дедалі менших піддерев\nбез кінця не буває.",
                    size=12.5, fill=BLUEFILL, stroke=NEG, color=INK))
    f.append(fitbox(px, 306, 360, 120,
                    "Числовий двійник у ℕ — кількість вузлів:\n"
                    "eval(×) = 7  →  eval(+) = 3  →  eval(3) = 1  →  лист.\n"
                    "Спадає щоразу, дно = листок.",
                    size=12.5, fill=GREENFILL, stroke=FIELD, color=INK))

    render(os.path.join(IMG, "subterm.svg"), W, H, *f)


# ── 6. Коло рівносильностей WO ⟹ WI ⟹ SI ⟹ WO (для вставки math-well-founded) ─
def fig_wf_cycle():
    W, H = 980, 560
    f = [text(W / 2, 34, "Коло рівносильностей на ℕ", size=19, bold=True),
         text(W / 2, 56, "замкнене коло імплікацій → усі три твердження рівносильні, кожна пара в обидва боки",
              size=12.5, color=MUTED, italic=True)]

    wi = (490, 160)   # верхня вершина
    wo = (250, 430)   # ліва
    si = (730, 430)   # права
    nb1, w1, h1 = textbox(wi[0], wi[1], "Слабка індукція\n(WI)", size=14.5, bold=True,
                          fill=BLUEFILL, stroke=NEG, color=INK, min_w=240)
    nb2, w2, h2 = textbox(wo[0], wo[1], "Повне впорядкування\n(WO)", size=14.5, bold=True,
                          fill=GREENFILL, stroke=FIELD, color=INK, min_w=240)
    nb3, w3, h3 = textbox(si[0], si[1], "Сильна індукція\n(SI)", size=14.5, bold=True,
                          fill=ROW, stroke=LINE, color=INK, min_w=240)

    # стрілки по колу: WO → WI → SI → WO
    f.append(arrow(wo[0] + 60, wo[1] - h2 / 2 - 4, wi[0] - 78, wi[1] + h1 / 2 + 6, color=FIELD, sw=2.2))
    f.append(arrow(wi[0] + 78, wi[1] + h1 / 2 + 6, si[0] - 60, si[1] - h3 / 2 - 4, color=NEG, sw=2.2))
    f.append(arrow(si[0] - w3 / 2 - 6, si[1], wo[0] + w2 / 2 + 6, wo[1], color=INK, sw=2.2))

    # підписи стрілок осторонь від ліній
    f.append(mtext(95, 250, ["найменший", "порушник m —", "ні m=0, ні m>0"],
                   size=12.5, color=FIELD, anchor="start", bold=True))
    f.append(mtext(748, 250, ["підсиль P до", "Q(n) = «P", "скрізь ≤ n»"],
                   size=12.5, color=NEG, anchor="start", bold=True))
    f.append(text(490, 488, "множина без найменшого — порожня", size=13, color=INK, bold=True))

    f.extend([nb1, nb2, nb3])
    render(os.path.join(IMG, "wf_cycle.svg"), W, H, *f)


# ── 7. Найменший проти мінімального (для вставки math-well-founded) ───────────
def fig_wf_minimal():
    W, H = 980, 500
    f = [text(W / 2, 34, "Найменший проти мінімального", size=19, bold=True),
         text(W / 2, 56, "на лінії — те саме; коли лінію прибрати — мінімальних кілька, найменшого може не бути",
              size=12.5, color=MUTED, italic=True)]
    f.append(line(W / 2, 88, W / 2, 470, color="#d7dbe0", sw=1.4, dash="5,5"))

    # ── ліворуч: ℕ — одне дно ──
    f.append(text(255, 112, "Натуральні числа: одне дно", size=15, bold=True, color=FIELD))
    ly = 258
    f.append(line(80, ly, 425, ly, color=INK, sw=1.6))
    pts = [(120, "0", True), (190, "1", False), (260, "2", False),
           (330, "3", False), (398, "4", False)]
    for x, lab, least in pts:
        f.append(circle(x, ly, 10 if least else 7,
                        fill=(GREENFILL if least else BG),
                        stroke=(FIELD if least else INK), sw=(2.6 if least else 1.5)))
        f.append(text(x, ly - 20, lab, size=13, bold=least, color=(FIELD if least else INK)))
    f.append(text(432, ly + 5, "…", size=20, bold=True))
    f.append(('<path d="M 120 %d L 120 %d" fill="none" stroke="%s" stroke-width="1.8" '
              'marker-end="url(#arrow)"/>' % (ly + 46, ly + 16, FIELD)))
    f.append(text(120, ly + 66, "найменший = мінімальний", size=12, bold=True, color=FIELD))
    f.append(text(255, 430, "«під ним нічого» і «нижчий за всіх» тут — одне", size=12, color=MUTED, italic=True))

    # ── праворуч: фундоване, не лінійне — два мінімальні, найменшого нема ──
    f.append(text(735, 112, "Фундоване, але не лінійне", size=15, bold=True, color=POS))
    f.append(text(735, 134, "стрілка вгору: нижчий стоїть R-нижче", size=11, color=MUTED, italic=True))
    d = (740, 190)
    c = (740, 272)
    a = (650, 356)
    b = (830, 356)
    f.append(arrow(a[0] + 11, a[1] - 11, c[0] - 11, c[1] + 11, color=INK, sw=1.8))
    f.append(arrow(b[0] - 11, b[1] - 11, c[0] + 11, c[1] + 11, color=INK, sw=1.8))
    f.append(arrow(c[0], c[1] - 16, d[0], d[1] + 16, color=INK, sw=1.8))
    for (nx, ny), lab, mini in [(d, "d", False), (c, "c", False), (a, "a", True), (b, "b", True)]:
        f.append(circle(nx, ny, 16, fill=(GREENFILL if mini else BG),
                        stroke=(FIELD if mini else INK), sw=(2.4 if mini else 1.6)))
        f.append(text(nx, ny + 5, lab, size=14, bold=True, color=(FIELD if mini else INK)))
    f.append(text(650, 394, "мінімальний", size=11.5, bold=True, color=FIELD))
    f.append(text(830, 394, "мінімальний", size=11.5, bold=True, color=FIELD))
    f.append(text(735, 432, "a і b незрівнянні → «найменшого» (нижчого за всіх) нема",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "wf_minimal.svg"), W, H, *f)


# ── 8. Ординали за межею ℕ і три випадки трансфінітної індукції (вставка) ─────
def fig_wf_ordinals():
    W, H = 980, 470
    f = [text(W / 2, 34, "Трансфінітна індукція: наступники й границі за межею ℕ", size=18, bold=True),
         text(W / 2, 56, "граничні ординали дістаються лише знизу цілим стрибком — попередника в них немає",
              size=12.5, color=MUTED, italic=True)]

    ay = 175
    f.append(line(70, ay, 915, ay, color=INK, sw=1.6))

    def succ(x, lab):
        f.append(circle(x, ay, 6, fill=BG, stroke=INK, sw=1.5))
        f.append(text(x, ay - 18, lab, size=11.5, color=INK))

    def dots(x):
        f.append(text(x, ay + 6, "…", size=20, bold=True, color=MUTED))

    def limit(x, lab):
        f.append(circle(x, ay, 9, fill=GREENFILL, stroke=FIELD, sw=2.6))
        f.append(text(x, ay - 20, lab, size=13, bold=True, color=FIELD))
        f.append(('<path d="M %d %d L %d %d" fill="none" stroke="%s" stroke-width="1.6" '
                  'marker-end="url(#arrow)"/>' % (x, ay + 40, x, ay + 13, FIELD)))
        f.append(text(x, ay + 58, "гранична", size=10.5, bold=True, color=FIELD))

    for x, lab in [(100, "0"), (140, "1"), (180, "2"), (220, "3")]:
        succ(x, lab)
    dots(266)
    limit(340, "ω")
    for x, lab in [(394, "ω+1"), (442, "ω+2")]:
        succ(x, lab)
    dots(492)
    limit(566, "ω·2")
    dots(652)
    limit(772, "ω²")
    dots(872)

    by = 300
    f.append(fitbox(80, by, 252, 96,
                    "α = 0\n\nменших нема → база:\nдоводимо P(0) прямо",
                    size=13, fill=ROW, stroke=LINE, color=INK))
    f.append(fitbox(364, by, 252, 96,
                    "α = β+1  (наступник)\n\nє найбільший менший β →\nзвичний крок від β",
                    size=13, fill=BLUEFILL, stroke=NEG, color=INK))
    f.append(fitbox(648, by, 252, 96,
                    "α — гранична\n\nпопередника нема → збери\nP(β) для ВСІХ β < α разом",
                    size=13, fill=GREENFILL, stroke=FIELD, color=INK))

    render(os.path.join(IMG, "wf_ordinals.svg"), W, H, *f)


if __name__ == "__main__":
    fig_least()
    fig_descent()
    fig_division()
    fig_recipe()
    fig_subterm()
    fig_wf_cycle()
    fig_wf_minimal()
    fig_wf_ordinals()
    print("OK: least, descent, division, recipe, subterm, wf_cycle, wf_minimal, wf_ordinals ->", IMG)
