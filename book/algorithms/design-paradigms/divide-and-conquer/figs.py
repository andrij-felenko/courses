# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SPLIT = "#2457d6"   # поділ (холодне)
MERGE = "#27ae60"   # зліплювання / впорядковане (зелене)
ACC   = "#c0392b"   # акцент


def rot_text(x, y, s, size=14, color=INK, bold=False):
    """Текст, повернутий на -90° (читається знизу вгору)."""
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="middle" transform="rotate(-90 %.1f %.1f)"%s>%s</text>'
            % (x, y, FONT, size, color, x, y, w, esc(s)))


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — три рухи парадигми: розділити · підкорити · поєднати
# ════════════════════════════════════════════════════════════════════════════
def fig_skeleton():
    W, H = 880, 420
    f = []

    # заголовки трьох рухів
    f.append(text(190, 46, "1. Розділити", size=15, bold=True, color=SPLIT))
    f.append(text(440, 46, "2. Підкорити", size=15, bold=True, color=INK))
    f.append(text(715, 46, "3. Поєднати", size=15, bold=True, color=MERGE))

    # ── задача ──
    b1, w1, h1 = textbox(150, 175, "Задача\n(розмір n)", size=15, pad=14,
                         fill="#eef2ff", stroke=SPLIT, sw=2)
    f.append(b1)

    # ── дві підзадачі ──
    sub_y = [120, 250]
    subx = 445
    sboxes = []
    for sy in sub_y:
        b, w, h = textbox(subx, sy, "Підзадача\n(n/2)", size=14, pad=12,
                          fill=FILL, stroke=LINE, sw=1.6)
        f.append(b)
        sboxes.append((subx, sy, w, h))

    # стрілки «розділити»: від задачі до кожної підзадачі
    for (sx, sy, sw_, sh) in sboxes:
        f.append(arrow(150 + w1 / 2, 175, sx - sw_ / 2 - 4, sy, color=SPLIT, sw=2))

    # рекурсія: під кожною підзадачею — тьмяний натяк, що вона ділиться далі
    for (sx, sy, sw_, sh) in sboxes:
        yb = sy + sh / 2
        f.append(line(sx, yb + 4, sx, yb + 22, color=MUTED, sw=1.4, dash="4 4"))
        f.append(text(sx, yb + 38, "… той самий метод …", size=11.5,
                      color=MUTED, italic=True))

    # ── розв'язок ──
    bo, wo, ho = textbox(730, 175, "Розв'язок\nзадачі", size=15, pad=14,
                         fill="#eaf7ef", stroke=MERGE, sw=2)
    f.append(bo)

    # стрілки «поєднати»: від кожної підзадачі до розв'язку
    for (sx, sy, sw_, sh) in sboxes:
        f.append(arrow(sx + sw_ / 2 + 4, sy, 730 - wo / 2 - 4, 175, color=MERGE, sw=2))

    # базовий випадок — знизу, окремим рядком
    bb = fitbox(150, 345, 580, 52,
                "Базовий випадок: найдрібніша задача (розмір 1), яку розв'язують "
                "прямо, без поділу — це підлога рекурсії.",
                size=13, fill="#fbfbe8", stroke="#b59f00", sw=1.5)
    f.append(bb)
    f.append(arrow(445, 300, 300, 348, color=MUTED, sw=1.5))

    render(os.path.join(OUT, "skeleton.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — дерево рекурсії: n роботи на кожному з log₂n рівнів → n·log₂n
# ════════════════════════════════════════════════════════════════════════════
def fig_tree():
    W, H = 900, 470
    f = []

    x0, xw = 120, 540           # ліва межа й повна ширина смуг
    cost_x = 792                # колонка вартості рівня
    bh = 30                     # висота смуги

    # вертикальний роздільник колонки вартості
    f.append(line(700, 44, 700, 352, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(cost_x, 40, "робота на рівні", size=12.5, bold=True, color=MUTED))

    def level_bars(y, count, label, gap):
        each = (xw - (count - 1) * gap) / count
        centers = []
        for i in range(count):
            x = x0 + i * (each + gap)
            f.append(rect(x, y, each, bh, fill="#eef2ff", stroke=SPLIT, sw=1.5))
            if each > 40:
                f.append(text(x + each / 2, y + bh / 2 + 5, label, size=13, color=INK))
            centers.append(x + each / 2)
        return centers

    # рівень 0
    y0 = 64
    c0 = level_bars(y0, 1, "n", 0)
    f.append(text(cost_x, y0 + 20, "n", size=14, bold=True, color=ACC))

    # рівень 1
    y1 = 138
    c1 = level_bars(y1, 2, "n/2", 16)
    f.append(text(cost_x, y1 + 20, "2 · n/2 = n", size=13, color=ACC))

    # рівень 2
    y2 = 212
    c2 = level_bars(y2, 4, "n/4", 12)
    f.append(text(cost_x, y2 + 20, "4 · n/4 = n", size=13, color=ACC))

    # прямі з'єднання батько→діти
    for cx in c1:
        f.append(line(c0[0], y0 + bh, cx, y1, color=MUTED, sw=1.1))
    for i, px in enumerate(c1):
        for cx in c2[i * 2:i * 2 + 2]:
            f.append(line(px, y1 + bh, cx, y2, color=MUTED, sw=1.1))

    # проміжок «…»
    ymid = 270
    f.append(text((x0 + x0 + xw) / 2, ymid, "⋮      кожен рівень у сумі дає  n      ⋮",
                  size=13, color=MUTED, italic=True))
    for cx in c2:
        f.append(line(cx, y2 + bh, cx, ymid - 14, color=MUTED, sw=1.0, dash="3 4"))

    # листки
    yl = 300
    nleaf = 18
    lw, lg = 22, 8
    total = nleaf * lw + (nleaf - 1) * lg
    lx = (x0 + x0 + xw) / 2 - total / 2
    for i in range(nleaf):
        x = lx + i * (lw + lg)
        f.append(rect(x, yl, lw, bh, fill="#eaf7ef", stroke=MERGE, sw=1.3))
    f.append(text((x0 + x0 + xw) / 2, yl + bh + 22,
                  "n листків розміру 1 — базовий випадок", size=12.5, color=INK))
    f.append(text(cost_x, yl + 20, "n · 1 = n", size=13, color=ACC))

    # брама глибини ліворуч
    f.append(line(78, y0, 78, yl + bh, color=INK, sw=1.4))
    f.append(line(78, y0, 86, y0, color=INK, sw=1.4))
    f.append(line(78, yl + bh, 86, yl + bh, color=INK, sw=1.4))
    f.append(rot_text(40, (y0 + yl + bh) / 2, "log₂n рівнів", size=14, bold=True, color=SPLIT))

    # підсумок
    f.append(line(120, 392, 780, 392, color=MUTED, sw=1.0))
    f.append(text(W / 2, 424,
                  "Разом: n роботи × log₂n рівнів  ≈  n · log₂n",
                  size=17, bold=True, color=INK))

    render(os.path.join(OUT, "tree.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — сортування злиттям: поділ до одинаків, тоді злиття вгору
# ════════════════════════════════════════════════════════════════════════════
def fig_mergesort():
    W, H = 640, 470
    f = []

    cellw, cellh = 42, 32
    gap = 14                    # проміжок між групами
    cx = 356                    # центр рядів

    def draw_row(y, groups, sorted_row=False):
        widths = [len(g) * cellw for g in groups]
        total = sum(widths) + (len(groups) - 1) * gap
        x = cx - total / 2
        fill = "#eaf7ef" if sorted_row else "#eef2ff"
        stroke = MERGE if sorted_row else SPLIT
        for g in groups:
            gw = len(g) * cellw
            f.append(rect(x, y, gw, cellh, fill=fill, stroke=stroke, sw=1.6))
            for k, v in enumerate(g):
                xcell = x + k * cellw
                if k > 0:
                    f.append(line(xcell, y + 3, xcell, y + cellh - 3,
                                  color=stroke, sw=0.8))
                f.append(text(xcell + cellw / 2, y + cellh / 2 + 6, str(v),
                              size=15, color=INK, bold=sorted_row))
            x += gw + gap

    # рядки: поділ (r1..r4), потім злиття (r5..r7)
    rows_split = [
        (58,  [[5, 2, 8, 1, 9, 4, 7, 3]]),
        (108, [[5, 2, 8, 1], [9, 4, 7, 3]]),
        (158, [[5, 2], [8, 1], [9, 4], [7, 3]]),
        (208, [[5], [2], [8], [1], [9], [4], [7], [3]]),
    ]
    for y, g in rows_split:
        draw_row(y, g)

    rows_merge = [
        (300, [[2, 5], [1, 8], [4, 9], [3, 7]]),
        (350, [[1, 2, 5, 8], [3, 4, 7, 9]]),
        (400, [[1, 2, 3, 4, 5, 7, 8, 9]]),
    ]
    for y, g in rows_merge:
        draw_row(y, g, sorted_row=True)

    # роздільник фаз
    f.append(line(96, 262, 616, 262, color=MUTED, sw=1.2, dash="6 5"))
    f.append(text(cx, 254, "одинаки вже впорядковані — базовий випадок",
                  size=12, color=MUTED, italic=True))

    # мітки фаз ліворуч
    f.append(rot_text(40, 145, "Поділ", size=15, bold=True, color=SPLIT))
    f.append(rot_text(40, 370, "Злиття", size=15, bold=True, color=MERGE))

    # напрям
    f.append(text(cx, 448, "розділяємо навпіл униз, тоді зливаємо впорядковане вгору",
                  size=12, color=INK))

    render(os.path.join(OUT, "mergesort.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 (hist) — родовід поділу: віхи від гасла до наріжного прийому
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W = 812
    # (рік, хто, [рядки опису], заливка, обвід)
    items = [
        ("давнина", "«Divide et impera»",
         ["Гасло війни й влади. Приписують Філіпові II й Цезарю —",
          "та в античних джерелах слогана нема (пізніша латина)."],
         "#f4f6f8", MUTED),
        ("1805", "Карл Фрідріх Ґаусс · німець",
         ["Поділ у розрахунку орбіт астероїдів — ідея ШПФ за 160",
          "років до самої ШПФ. Рукопис лишився неопублікованим."],
         "#eaf7ef", MERGE),
        ("1945", "Джон фон Нейман · угор.-амер.",
         ["Сортування злиттям — одна з перших програм,",
          "продуманих саме під комп'ютер (машина EDVAC)."],
         "#eef2ff", SPLIT),
        ("1960", "Анатолій Карацуба · росіянин",
         ["За тиждень спростував гіпотезу Колмогорова:",
          "множення за n^log₂3 ≈ n^1.58, а не за n²."],
         "#fff3e0", ACC),
        ("1965", "Кулі й Тьюкі · американці",
         ["Швидке перетворення Фур'є за n·log n замість n².",
          "Той самий поділ, що й у Ґаусса, — аж тепер визнаний."],
         "#eaf7ef", MERGE),
        ("1969", "Фолькер Штрассен · німець",
         ["Множення матриць за n^log₂7 ≈ n^2.81, а не n³:",
          "«метод Ґаусса не оптимальний»."],
         "#fff3e0", ACC),
    ]
    top, row_h = 58, 100
    spine_x = 214
    cardx, cardw = 252, 536
    H = top + len(items) * row_h + 20
    f = []
    ny = [top + i * row_h + row_h / 2 for i in range(len(items))]
    # хребет часу
    f.append(line(spine_x, ny[0], spine_x, ny[-1], color=MUTED, sw=2))
    for i, (year, who, desc, fill, stroke) in enumerate(items):
        cy = ny[i]
        ch = 76
        # рік — ліворуч від хребта
        f.append(text(spine_x - 28, cy + 5, year, size=14, bold=True, color=INK, anchor="end"))
        # вузол на хребті
        f.append(circle(spine_x, cy, 8, fill=stroke, stroke=BG, sw=2.5))
        # з'єднувач вузол → картка
        f.append(line(spine_x + 8, cy, cardx, cy, color=MUTED, sw=1.4))
        # картка
        f.append(rect(cardx, cy - ch / 2, cardw, ch, fill=fill, stroke=stroke, sw=1.6))
        # хто (жирний заголовок)
        f.append(text(cardx + 16, cy - ch / 2 + 24, who, size=14, bold=True,
                      color=INK, anchor="start"))
        # опис (два рядки)
        f.append(mtext(cardx + 16, cy - ch / 2 + 45, desc, size=13, color=INK,
                       anchor="start", lh=1.25))
    render(os.path.join(OUT, "timeline.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Вставка math-recurrence — Фігура A: символьне дерево рекурсії (aᵏ, n/bᵏ)
# ════════════════════════════════════════════════════════════════════════════
def fig_tree_generic():
    W, H = 960, 530
    f = []

    cx = 450                      # центр дерева
    cost_x = 838                  # колонка вартості рівня
    cnt_x = 176                   # права межа колонки лічби вузлів

    f.append(text(cnt_x, 52, "вузлів", size=12.5, bold=True, color=MUTED, anchor="end"))
    f.append(text(cost_x, 52, "робота рівня", size=12.5, bold=True, color=MUTED))
    f.append(line(760, 66, 760, 402, color=MUTED, sw=1.2, dash="5 5"))

    def box(x, y, s, w=None, fill="#eef2ff", stroke=SPLIT, sw=1.6, size=13):
        if w is None:
            w = text_width(s, size) + 18
        f.append(rect(x - w / 2, y - 16, w, 32, fill=fill, stroke=stroke, sw=sw))
        f.append(text(x, y + 5, s, size=size, color=INK))

    # рівень 0 — корінь
    y0 = 84
    box(cx, y0, "n", w=54)
    f.append(text(cnt_x, y0 + 5, "1", size=13, color=INK, anchor="end"))
    f.append(text(cost_x, y0 + 5, "f(n)", size=13.5, bold=True, color=ACC))

    # рівень 1 — a вузлів n/b
    y1 = 158
    c1 = [cx - 150, cx, cx + 150]
    for x in c1:
        f.append(line(cx, y0 + 16, x, y1 - 16, color=MUTED, sw=1.1))
    for x in c1:
        box(x, y1, "n/b", w=64)
    f.append(text(cnt_x, y1 + 5, "a", size=13, color=INK, anchor="end"))
    f.append(text(cost_x, y1 + 5, "a · f(n/b)", size=13.5, color=ACC))

    # рівень 2 — a² вузлів n/b²
    y2 = 232
    c2 = [cx - 210 + i * 84 for i in range(6)]
    for j, x in enumerate(c2):
        parent = c1[min(j // 2, 2)]
        f.append(line(parent, y1 + 16, x, y2 - 16, color=MUTED, sw=1.0))
    for x in c2:
        box(x, y2, "n/b²", w=60, size=12)
    f.append(text(cnt_x, y2 + 5, "a²", size=13, color=INK, anchor="end"))
    f.append(text(cost_x, y2 + 5, "a² · f(n/b²)", size=13.5, color=ACC))

    # проміжок «…»
    ymid = 292
    f.append(text(cx, ymid, "⋮      рівень k:  aᵏ вузлів по  n/bᵏ      ⋮",
                  size=13, color=MUTED, italic=True))
    f.append(text(cnt_x, ymid + 1, "aᵏ", size=13, color=MUTED, anchor="end"))
    f.append(text(cost_x, ymid + 1, "aᵏ · f(n/bᵏ)", size=13.5, color=ACC))

    # листя
    yl = 350
    nleaf, lw, lg = 15, 24, 9
    total = nleaf * lw + (nleaf - 1) * lg
    lx = cx - total / 2
    for i in range(nleaf):
        f.append(rect(lx + i * (lw + lg), yl - 14, lw, 28,
                      fill="#eaf7ef", stroke=MERGE, sw=1.3))
    f.append(text(cnt_x, yl + 5, "n^(log_b a)", size=12.5, bold=True,
                  color=MERGE, anchor="end"))
    f.append(text(cost_x, yl + 5, "n^(log_b a) · T(1)", size=12.5, bold=True, color=MERGE))
    f.append(text(cx, yl + 40, "n^(log_b a) листків розміру 1 — базовий випадок",
                  size=12.5, color=INK))

    # брама глибини ліворуч
    gx = 46
    f.append(line(gx, y0, gx, yl, color=INK, sw=1.4))
    f.append(line(gx, y0, gx + 8, y0, color=INK, sw=1.4))
    f.append(line(gx, yl, gx + 8, yl, color=INK, sw=1.4))
    f.append(rot_text(26, (y0 + yl) / 2, "log_b n рівнів", size=13.5, bold=True, color=SPLIT))

    # підсумок
    f.append(line(90, 432, 900, 432, color=MUTED, sw=1.0))
    f.append(text(W / 2, 468, "T(n) = Σ aᵏ·f(n/bᵏ)  +  n^(log_b a)·T(1)",
                  size=16, bold=True, color=INK))
    f.append(text(W / 2, 496, "сума за рівнями (геометрична)          робота листя",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "tree-generic.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Вставка math-recurrence — Фігура B: три режими геометричної прогресії
# ════════════════════════════════════════════════════════════════════════════
def fig_regimes():
    W, H = 980, 400
    f = []

    f.append(text(W / 2, 30,
                  "робота за рівнями — геометрична прогресія зі знаменником  r = a / bᵈ",
                  size=14, bold=True, color=INK))

    panels = [
        (170, "r < 1", "панує корінь", [150, 112, 82, 60, 44], "top", "Θ(f(n))"),
        (490, "r = 1", "баланс",       [112, 112, 112, 112, 112], "all", "Θ(f(n) · log n)"),
        (810, "r > 1", "панує листя",  [44, 60, 82, 112, 150], "bot", "Θ(n^(log_b a))"),
    ]

    top_y = 118
    bh, gap = 26, 9

    for (pcx, rtag, who, widths, hi, concl) in panels:
        f.append(text(pcx, 66, rtag, size=20, bold=True, color=INK))
        f.append(text(pcx, 90, who, size=14, bold=True, color=SPLIT))
        left = pcx - 75
        for i, w in enumerate(widths):
            y = top_y + i * (bh + gap)
            dom = (hi == "all") or (hi == "top" and i == 0) or \
                  (hi == "bot" and i == len(widths) - 1)
            fill = "#eaf7ef" if dom else "#eef2ff"
            stroke = MERGE if dom else SPLIT
            f.append(rect(left, y, w, bh, fill=fill, stroke=stroke, sw=1.6))
        by = top_y + 5 * (bh + gap) + 14
        f.append(fitbox(pcx - 120, by, 240, 42, concl, size=15, bold=True,
                        fill=FILL, stroke=INK, sw=1.4))

    f.append(rot_text(30, top_y + 2 * (bh + gap), "рівні дерева  →", size=13, color=MUTED))

    render(os.path.join(OUT, "regimes.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Вставка math-recurrence — Фігура C: чотири виведення через майстер-теорему
# ════════════════════════════════════════════════════════════════════════════
def fig_mastercases():
    W, H = 1000, 320
    f = []

    cols = [
        ("Алгоритм", 150),
        ("Рекурентність", 215),
        ("c* = log_b a", 140),
        ("f(n)", 80),
        ("Випадок", 150),
        ("T(n)", 175),
    ]
    rows = [
        ("Сортування злиттям", "T(n)=2T(n/2)+n",    "1",             "n",  "2 · баланс", "Θ(n log n)"),
        ("Двійковий пошук",    "T(n)=T(n/2)+Θ(1)",   "0",             "1",  "2 · баланс", "Θ(log n)"),
        ("Карацуба",           "T(n)=3T(n/2)+Θ(n)",  "log₂3 ≈ 1.585", "n",  "1 · листя",  "Θ(n^1.585)"),
        ("Штрассен",           "T(n)=7T(n/2)+Θ(n²)", "log₂7 ≈ 2.807", "n²", "1 · листя",  "Θ(n^2.807)"),
    ]

    x0, y0 = 30, 30
    hh, rh = 42, 52
    xs = [x0]
    for _, w in cols:
        xs.append(xs[-1] + w)

    for i, (name, w) in enumerate(cols):
        f.append(rect(xs[i], y0, w, hh, fill="#eef2ff", stroke=SPLIT, sw=1.4))
        f.append(text(xs[i] + w / 2, y0 + hh / 2 + 5, name, size=13, bold=True, color=INK))

    for r, row in enumerate(rows):
        y = y0 + hh + r * rh
        leaf = "листя" in row[4]
        for i, (name, w) in enumerate(cols):
            fill = BG
            if i == 5:
                fill = "#eaf7ef" if leaf else "#fff7e6"
            f.append(fitbox(xs[i], y, w, rh, row[i], size=13, pad=6, fill=fill,
                            stroke=LINE, sw=1.0, bold=(i == 0 or i == 5)))

    render(os.path.join(OUT, "mastercases.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Вставка proj-mergesort — Фігура 1: один крок злиття (покажчики i, j, k)
# ════════════════════════════════════════════════════════════════════════════
def fig_merge_indices():
    W, H = 780, 470
    f = []

    cw, ch = 46, 36
    GREY = "#e5e7eb"

    def cells(x0, y, vals, consumed, fill_active, stroke, ptr_idx=None,
              ptr_label="", ptr_color=INK):
        """Ряд клітин; consumed — множина спожитих індексів (притемнені);
        ptr_idx — індекс, над яким малюємо покажчик згори."""
        for idx, v in enumerate(vals):
            x = x0 + idx * cw
            fill = GREY if idx in consumed else fill_active
            f.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=1.6))
            col = MUTED if idx in consumed else INK
            f.append(text(x + cw / 2, y + ch / 2 + 6, str(v), size=16, color=col,
                          bold=(idx not in consumed)))
        if ptr_idx is not None:
            px = x0 + ptr_idx * cw + cw / 2
            f.append(text(px, y - 30, ptr_label, size=16, bold=True, color=ptr_color))
            f.append(arrow(px, y - 24, px, y - 4, color=ptr_color, sw=2))

    # ── два джерела на одному рядку ──
    ytop = 130
    lx = 96
    # ліва частина [2,5,8], спожито індекс 0 (значення 2); покажчик i на індексі 1
    cells(lx, ytop, [2, 5, 8], {0}, "#eef2ff", SPLIT, ptr_idx=1, ptr_label="i", ptr_color=SPLIT)
    f.append(text(lx + 3 * cw / 2, ytop + ch + 26, "ліва  a[lo:mid)", size=13,
                  bold=True, color=SPLIT))
    f.append(text(lx + 3 * cw / 2, ytop + ch + 46, "півінтервал [lo, mid)", size=11.5,
                  italic=True, color=MUTED))

    rx = lx + 3 * cw + 70
    # права частина [1,4,9], спожито індекс 0 (значення 1); покажчик j на індексі 1
    cells(rx, ytop, [1, 4, 9], {0}, "#eaf7ef", MERGE, ptr_idx=1, ptr_label="j", ptr_color=MERGE)
    f.append(text(rx + 3 * cw / 2, ytop + ch + 26, "права  a[mid:hi)", size=13,
                  bold=True, color=MERGE))
    f.append(text(rx + 3 * cw / 2, ytop + ch + 46, "півінтервал [mid, hi)", size=11.5,
                  italic=True, color=MUTED))

    # ── буфер знизу ──
    ybuf = 320
    bx = 96
    bvals = ["1", "2", "·", "·", "·", "·"]
    for idx, v in enumerate(bvals):
        x = bx + idx * cw
        filled = idx < 2
        f.append(rect(x, ybuf, cw, ch, fill=("#fbfbe8" if filled else BG),
                      stroke=("#b59f00" if filled else MUTED),
                      sw=1.6, ))
        f.append(text(x + cw / 2, ybuf + ch / 2 + 6, v, size=16,
                      color=(INK if filled else MUTED), bold=filled))
    # покажчик k на першій вільній клітині (індекс 2)
    kpx = bx + 2 * cw + cw / 2
    f.append(text(kpx, ybuf - 30, "k", size=16, bold=True, color="#b59f00"))
    f.append(arrow(kpx, ybuf - 24, kpx, ybuf - 4, color="#b59f00", sw=2))
    f.append(text(bx + 6 * cw / 2, ybuf + ch + 26, "buf  (приймач злиття)", size=13,
                  bold=True, color="#8a7a00"))

    # тьмяні стрілки джерела → буфер (натяк напряму)
    f.append(text(W / 2, 250, "меншу з двох верхівок → у buf[k], зсуваємо покажчик",
                  size=12.5, italic=True, color=MUTED))

    # ── наступний крок + правило стійкості ──
    step = fitbox(150, 400, 480, 30,
                  "порівнюємо a[i]=5 та a[j]=4  →  менша 4  →  buf[k]=4, j++",
                  size=13.5, fill=FILL, stroke=INK, sw=1.4)
    f.append(step)
    f.append(text(W / 2, 452,
                  "на рівних (a[i] == a[j]) беремо з ЛІВОЇ — умова ≤ — і зберігаємо стійкість",
                  size=12.5, italic=True, color=SPLIT))

    render(os.path.join(OUT, "merge-indices.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Вставка proj-mergesort — Фігура 2: сортування знизу вгору (подвоєння ширини)
# ════════════════════════════════════════════════════════════════════════════
def fig_bottomup():
    W, H = 700, 470
    f = []

    cw, ch = 48, 34
    cx = 380
    base = [5, 2, 8, 1, 9, 4, 7, 3]

    def draw(y, groups, done=False):
        widths = [len(g) * cw for g in groups]
        total = sum(widths) + (len(groups) - 1) * 16
        x = cx - total / 2
        fill = "#eaf7ef" if done else "#eef2ff"
        stroke = MERGE if done else SPLIT
        for g in groups:
            gw = len(g) * cw
            f.append(rect(x, y, gw, ch, fill=fill, stroke=stroke, sw=1.7))
            for k, v in enumerate(g):
                xc = x + k * cw
                if k > 0:
                    f.append(line(xc, y + 3, xc, y + ch - 3, color=stroke, sw=0.8))
                f.append(text(xc + cw / 2, y + ch / 2 + 6, str(v), size=15,
                              color=INK, bold=done))
            x += gw + 16

    # рядки рознесено на крок 98 (замість 80) і підпис-примітку перенесено
    # ПІД ряд клітинок (а не вбік від них) — так він ніколи не заходить
    # на широкі клітинки сусідніх колонок
    rows = [
        (66,  [[5], [2], [8], [1], [9], [4], [7], [3]], False, "ширина 1", "вісім одинаків"),
        (164, [[2, 5], [1, 8], [4, 9], [3, 7]], True, "1 → 2", "зливаємо сусідів у пари"),
        (262, [[1, 2, 5, 8], [3, 4, 7, 9]], True, "2 → 4", "пари — у четвірки"),
        (360, [[1, 2, 3, 4, 5, 7, 8, 9]], True, "4 → 8", "весь масив упорядковано"),
    ]
    for y, g, done, wlab, note in rows:
        draw(y, g, done)
        f.append(text(70, y + ch / 2 + 5, wlab, size=13, bold=True,
                      color=(MERGE if done else SPLIT), anchor="middle"))
        f.append(text(cx, y + ch + 22, note, size=11.5, italic=True,
                      color=MUTED, anchor="middle"))

    f.append(text(cx, 442, "жодної рекурсії — два вкладені цикли: ширина × 2 щопроходу",
                  size=12.5, italic=True, color=INK))

    render(os.path.join(OUT, "bottomup.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Вставка proj-mergesort — Фігура 3: пінг-понг двома буферами (без copy-back)
# ════════════════════════════════════════════════════════════════════════════
def fig_pingpong():
    W, H = 720, 380
    f = []

    barw, barh = 300, 46
    ax = W / 2 - barw / 2
    ay = 70            # масив a — угорі
    by = 250           # буфер buf — унизу

    f.append(rect(ax, ay, barw, barh, fill="#eef2ff", stroke=SPLIT, sw=2))
    f.append(text(ax + barw / 2, ay + barh / 2 + 6, "масив  a", size=16, bold=True, color=SPLIT))
    f.append(rect(ax, by, barw, barh, fill="#fbfbe8", stroke="#b59f00", sw=2))
    f.append(text(ax + barw / 2, by + barh / 2 + 6, "буфер  buf", size=16, bold=True, color="#8a7a00"))

    # проходи-стрілки, що чергують напрям (buf→a, a→buf, buf→a)
    xs = [ax + barw * 0.20, ax + barw * 0.50, ax + barw * 0.80]
    passes = [
        (xs[0], "up",   "прохід 1", "ширина 1"),
        (xs[1], "down", "прохід 2", "ширина 2"),
        (xs[2], "up",   "прохід 3", "ширина 4"),
    ]
    for x, direction, lab, wlab in passes:
        ty = (ay + barh + by) / 2
        # напис «прохід N / ширина N» сидить біля середини стрілки — лінію
        # розриваємо навколо нього (два сегменти, стрілка лише на кінцевому),
        # щоб вона йшла ПОВЗ напис, а не наскрізь крізь нього
        gtop, gbot = ty - 20, ty + 20
        if direction == "up":            # з buf у a, знизу вгору
            f.append(line(x, by - 6, x, gbot, color=MERGE, sw=2.4))
            f.append(arrow(x, gtop, x, ay + barh + 6, color=MERGE, sw=2.4))
        else:                            # з a у buf, згори вниз
            f.append(line(x, ay + barh + 6, x, gtop, color=SPLIT, sw=2.4))
            f.append(arrow(x, gbot, x, by - 6, color=SPLIT, sw=2.4))
        f.append(text(x, ty - 8, lab, size=12.5, bold=True, color=INK))
        f.append(text(x, ty + 10, wlab, size=11, italic=True, color=MUTED))

    f.append(text(W / 2, 335,
                  "приймач кожного проходу стає джерелом наступного — copy-back зникає",
                  size=13, italic=True, color=INK))
    f.append(text(W / 2, 358,
                  "лишається щонайбільше один фінальний перенос, якщо результат осів у buf",
                  size=11.5, italic=True, color=MUTED))

    render(os.path.join(OUT, "pingpong.svg"), W, H, *f)


if __name__ == "__main__":
    fig_skeleton()
    fig_tree()
    fig_mergesort()
    fig_timeline()
    fig_tree_generic()
    fig_regimes()
    fig_mastercases()
    fig_merge_indices()
    fig_bottomup()
    fig_pingpong()
    print("OK: skeleton.svg, tree.svg, mergesort.svg, timeline.svg, "
          "tree-generic.svg, regimes.svg, mastercases.svg, "
          "merge-indices.svg, bottomup.svg, pingpong.svg")
