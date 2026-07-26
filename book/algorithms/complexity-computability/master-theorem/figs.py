# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ROOT = "#c0392b"   # корінь / робота вгорі (гаряче)
LEAF = "#27ae60"   # листя / кількість унизу (зелене)
COOL = "#2457d6"   # звичайні вузли (холодне)
PURPLE = "#7c3aed" # пізніше узагальнення (Акра–Баззі)


def rot_text(x, y, s, size=14, color=INK, bold=False):
    """Текст, повернутий на -90° (читається знизу вгору)."""
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="middle" transform="rotate(-90 %.1f %.1f)"%s>%s</text>'
            % (x, y, FONT, size, color, x, y, w, esc(s)))


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — дві сили: робота кореня f(n) проти кількості листя n^(log_b a)
# ════════════════════════════════════════════════════════════════════════════
def fig_contest():
    W, H = 920, 440
    f = []

    cx = 432                 # центр дерева
    cost_x = 812             # колонка «робота рівня»
    cnt_x = 150              # права межа колонки «вузлів»

    # заголовки колонок
    f.append(text(cnt_x, 48, "вузлів", size=12.5, bold=True, color=MUTED, anchor="end"))
    f.append(text(cost_x, 48, "робота рівня", size=12.5, bold=True, color=MUTED))
    f.append(line(724, 64, 724, 356, color=MUTED, sw=1.2, dash="5 5"))

    def box(x, y, s, w, fill, stroke, sw=1.7, size=13):
        f.append(rect(x - w / 2, y - 17, w, 34, fill=fill, stroke=stroke, sw=sw))
        f.append(text(x, y + 5, s, size=size, color=INK))

    # ── рівень 0: корінь (робота f(n) — гаряча сила) ──
    y0 = 84
    box(cx, y0, "n", 58, "#fdecea", ROOT, sw=2.2)
    f.append(text(cnt_x, y0 + 5, "1", size=13, color=INK, anchor="end"))
    f.append(text(cost_x, y0 + 5, "f(n)", size=14, bold=True, color=ROOT))

    # ── рівень 1: a вузлів n/b ──
    y1 = 162
    c1 = [cx - 150, cx, cx + 150]
    for x in c1:
        f.append(line(cx, y0 + 17, x, y1 - 17, color=MUTED, sw=1.1))
    for x in c1:
        box(x, y1, "n/b", 66, "#eef2ff", COOL)
    f.append(text(cnt_x, y1 + 5, "a", size=13, color=INK, anchor="end"))
    f.append(text(cost_x, y1 + 5, "a · f(n/b)", size=13.5, color=INK))

    # ── проміжок «…» ──
    ymid = 224
    for x in c1:
        f.append(line(x, y1 + 17, x, ymid - 12, color=MUTED, sw=1.0, dash="3 4"))
    f.append(text(cx, ymid + 2, "⋮      рівень k:  aᵏ вузлів по  n/bᵏ      ⋮",
                  size=12.5, color=MUTED, italic=True))
    f.append(text(cnt_x, ymid + 2, "aᵏ", size=12.5, color=MUTED, anchor="end"))
    f.append(text(cost_x, ymid + 2, "aᵏ · f(n/bᵏ)", size=13, color=INK))

    # ── листя (кількість n^(log_b a) — холодна сила) ──
    yl = 292
    nleaf, lw, lg = 15, 24, 8
    total = nleaf * lw + (nleaf - 1) * lg
    lx = cx - total / 2
    for x in c1:
        f.append(line(x, ymid + 12, x, yl - 15, color=MUTED, sw=1.0, dash="3 4"))
    for i in range(nleaf):
        f.append(rect(lx + i * (lw + lg), yl - 15, lw, 30,
                      fill="#eaf7ef", stroke=LEAF, sw=1.4))
    f.append(text(cnt_x, yl + 5, "n^(log_b a)", size=13, bold=True, color=LEAF, anchor="end"))
    f.append(text(cost_x, yl + 5, "робота листя", size=13, bold=True, color=LEAF))
    f.append(text(cx, yl + 40, "n^(log_b a) листків розміру 1 — базовий випадок",
                  size=12.5, color=INK))

    # ── брама глибини ліворуч ──
    gx = 44
    f.append(line(gx, y0, gx, yl, color=INK, sw=1.4))
    f.append(line(gx, y0, gx + 8, y0, color=INK, sw=1.4))
    f.append(line(gx, yl, gx + 8, yl, color=INK, sw=1.4))
    f.append(rot_text(26, (y0 + yl) / 2, "log_b n рівнів", size=13.5, bold=True, color=COOL))

    # ── підсумок: змагання двох сил ──
    f.append(line(90, 384, 830, 384, color=MUTED, sw=1.0))
    f.append(text(W / 2, 414,
                  "Вартість = хто переважить зі зростанням n",
                  size=16, bold=True, color=INK))
    f.append(text(W / 2, 436,
                  "робота кореня  f(n)      проти      кількість листя  n^(log_b a)",
                  size=13, italic=True, color=MUTED))

    render(os.path.join(OUT, "contest.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — рецепт: три випадки за порівнянням f(n) з n^(log_b a)
# ════════════════════════════════════════════════════════════════════════════
def fig_recipe():
    W, H = 940, 312
    f = []

    cols = [
        ("Порівняти  f(n)  з  n^(log_b a)", 322),
        ("Режим", 150),
        ("Тоді  T(n) =", 250),
        ("Приклад", 176),
    ]
    # (c1, c2, c3, c4, колір-режиму)
    rows = [
        ("f(n) РОСТЕ ПОВІЛЬНІШЕ\nза  n^(log_b a)", "панує листя",
         "Θ(n^(log_b a))", "Карацуба\n3T(n/2)+n → n^1.585", LEAF),
        ("f(n) РОСТЕ ТОЧНО ТАК САМО\nяк  n^(log_b a)", "баланс",
         "Θ(n^(log_b a) · log n)", "сорт. злиттям\n2T(n/2)+n → n·log n", COOL),
        ("f(n) РОСТЕ ШВИДШЕ\nза  n^(log_b a)", "панує корінь",
         "Θ(f(n))", "2T(n/2)+n² → n²", ROOT),
    ]

    x0, y0 = 26, 46
    hh, rh = 42, 68
    xs = [x0]
    for _, w in cols:
        xs.append(xs[-1] + w)

    # заголовок таблиці
    f.append(text(W / 2, 28,
                  "Рецепт: порівняти f(n) з листяною лінією n^(log_b a)",
                  size=15, bold=True, color=INK))

    # шапка
    for i, (name, w) in enumerate(cols):
        f.append(rect(xs[i], y0, w, hh, fill="#eef2ff", stroke=COOL, sw=1.4))
        f.append(text(xs[i] + w / 2, y0 + hh / 2 + 5, name, size=12.5, bold=True, color=INK))

    # рядки
    for r, (c1, c2, c3, c4, rc) in enumerate(rows):
        y = y0 + hh + r * rh
        tint = {LEAF: "#eaf7ef", COOL: "#eef2ff", ROOT: "#fdecea"}[rc]
        cells = [c1, c2, c3, c4]
        for i, val in enumerate(cells):
            fill = BG
            stroke = LINE
            bold = False
            if i == 1:                     # режим — тонований, жирний
                fill, stroke, bold = tint, rc, True
            elif i == 2:                   # підсумок — тонований, жирний
                fill, stroke, bold = tint, rc, True
            f.append(fitbox(xs[i], y, cols[i][1], rh, val, size=13, pad=7,
                            fill=fill, stroke=stroke, sw=1.1, bold=bold))

    render(os.path.join(OUT, "recipe.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 (для hist-вставки) — стрічка часу: як народжувався й дорослішав рецепт
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W, H = 980, 344
    f = []

    xs = [148, 388, 628, 868]
    baseline = 176

    # ── вісь часу (стрілка вправо) ──
    f.append(line(80, baseline, 916, baseline, color=MUTED, sw=2.2))
    f.append('<polygon points="916,%.1f 903,%.1f 903,%.1f" fill="%s"/>'
             % (baseline, baseline - 6, baseline + 6, MUTED))

    miles = [
        ("1976", "Чотири фарби", MUTED, "#eef0f2",
         "Вольфганг Гакен\nі Кеннет Аппель\nдоводять теорему\nпро чотири фарби"),
        ("1980", "Нотатка", LEAF, "#eaf7ef",
         "Бентлі, Д. Гакен,\nСакс у SIGACT\nNews: «загальний\nметод» поділу"),
        ("1990", "Ім'я", COOL, "#eef2ff",
         "Кормен, Лейзерсон,\nРівест — підручник\nдає назву\n«майстер-теорема»"),
        ("1998", "Продовження", PURPLE, "#f3edfd",
         "Акра й Баззі:\nнерівний поділ,\nщілини між\nвипадками закрито"),
    ]

    bw, bh = 212, 100
    for x, (yr, tag, col, tint, desc) in zip(xs, miles):
        # вузол на осі
        f.append(circle(x, baseline, 10, fill=tint, stroke=col, sw=2.6))
        f.append(circle(x, baseline, 3.4, fill=col, stroke=col, sw=1))
        # рік і ярлик — над віссю
        f.append(text(x, 112, yr, size=26, bold=True, color=col))
        f.append(text(x, 138, tag, size=13.5, bold=True, color=INK))
        f.append(line(x, baseline - 10, x, 148, color=col, sw=1.2, dash="3 3"))
        # опис — під віссю
        f.append(line(x, baseline + 10, x, 208, color=col, sw=1.2))
        f.append(fitbox(x - bw / 2, 208, bw, bh, desc, size=12.5, pad=9,
                        fill=BG, stroke=col, sw=1.4, color=INK))

    # ── дужка «родина Гакенів» над 1976 і 1980 ──
    bx1, bx2, by = xs[0], xs[1], 74
    f.append(line(bx1, by, bx2, by, color=INK, sw=1.3))
    f.append(line(bx1, by, bx1, by + 9, color=INK, sw=1.3))
    f.append(line(bx2, by, bx2, by + 9, color=INK, sw=1.3))
    f.append(text((bx1 + bx2) / 2, by - 8, "Гакен → Гакен: батько й донька",
                  size=12.5, italic=True, color=INK))

    render(os.path.join(OUT, "timeline.svg"), W, H, *f,
           title="Дві декади: від нотатки до назви (і далі)")


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 (для proj-вставки) — числова межа класифікатора: три зони за знаком
#            (d − c*) і смуга ε, де float не суддя, а баланс підтверджують точно
# ════════════════════════════════════════════════════════════════════════════
def fig_classify():
    W, H = 960, 380
    f = []

    zt, zh = 150, 110            # верх і висота зон
    zb = zt + zh                 # низ зон
    cx = 480                     # центр = c*
    lx0, lw = 90, 350            # ліва зона (листя)
    rx0, rw = 520, 350           # права зона (корінь)
    bx0, bw = 445, 70            # центральна смуга ε

    f.append(text(W / 2, 28, "Класифікатор: де лежить d відносно c* = log_b a",
                  size=16, bold=True, color=INK))

    # ── брама рішення над смугою ──
    gate = ("d ≈ c* — плаваючій комі не вірю.\n"
            "Перевіряю ЦІЛЕ рівняння  b^d = a:\n"
            "= a → баланс  Θ(n^c* · log n)      ≠ a → поза межами")
    gb, gw, gh = textbox(cx, 82, gate, size=12.5, pad=11,
                         fill="#f7f9ff", stroke=COOL, sw=1.5, color=INK)
    f.append(gb)
    # розрив у з'єднувальній лінії — обходить напис "d ≈ c*" замість перетину
    ytxt = zt - 8
    f.append(line(cx, 82 + gh / 2, cx, ytxt - 9, color=COOL, sw=1.4, dash="4 4"))
    f.append(line(cx, ytxt + 4, cx, zt, color=COOL, sw=1.4, dash="4 4"))

    # ── три зони ──
    f.append(rect(lx0, zt, lw, zh, fill="#eaf7ef", stroke=LEAF, sw=1.4))
    f.append(rect(bx0, zt, bw, zh, fill="#eef2ff", stroke=COOL, sw=1.4))
    f.append(rect(rx0, zt, rw, zh, fill="#fdecea", stroke=ROOT, sw=1.4))
    f.append(line(cx, zt, cx, zb, color=COOL, sw=1.8))       # лінія c*

    # ── підписи лівої зони (листя) ──
    lcx = lx0 + lw / 2 - 8
    f.append(text(lcx, zt + 34, "d  <  c*   (із запасом)", size=13, color=MUTED))
    f.append(text(lcx, zt + 62, "панує ЛИСТЯ", size=16, bold=True, color=LEAF))
    f.append(text(lcx, zt + 92, "T = Θ(n^c*)", size=14, bold=True, color=INK))

    # ── підписи правої зони (корінь) ──
    rcx = rx0 + rw / 2 + 8
    f.append(text(rcx, zt + 34, "d  >  c*   (із запасом)", size=13, color=MUTED))
    f.append(text(rcx, zt + 62, "панує КОРІНЬ", size=16, bold=True, color=ROOT))
    f.append(text(rcx, zt + 92, "T = Θ(n^d)", size=14, bold=True, color=INK))

    # ── позначки смуги ──
    f.append(text(cx, zt - 8, "d ≈ c*", size=12.5, bold=True, color=COOL))
    f.append(text(cx, zb + 20, "смуга ε", size=11.5, italic=True, color=MUTED))

    # ── вісь показника d під зонами ──
    ay = 322
    f.append(arrow(90, ay, 890, ay, color=INK, sw=1.6))
    f.append(text(884, ay - 10, "d", size=13, bold=True, color=INK, anchor="end"))
    f.append(line(cx, zb + 30, cx, ay, color=MUTED, sw=1.0, dash="3 4"))
    f.append(text(cx, ay + 20, "c*", size=12.5, bold=True, color=COOL))
    f.append(text(150, ay + 20, "менші показники", size=11, color=MUTED, anchor="start"))
    f.append(text(824, ay + 20, "більші показники", size=11, color=MUTED, anchor="end"))

    render(os.path.join(OUT, "classify-line.svg"), W, H, *f)


if __name__ == "__main__":
    fig_contest()
    fig_recipe()
    fig_timeline()
    fig_classify()
    print("OK: contest.svg, recipe.svg, timeline.svg, classify-line.svg")
