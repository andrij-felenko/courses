# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

FILLED = "#eafaf0"   # елемент у структурі (світло-зелений)
BAD    = "#fdecea"   # дорога / погана клітина
HEAD   = "#eef4ff"   # шапка таблиці


# ── fifo-lifo: черга зберігає порядок, стек його перевертає ───────────────────
# Ідея: ті самі A,B,C заходять в обидві структури однаково; черга віддає їх як
# прийшли (беремо з протилежного кінця), стек — задом наперед (той самий кінець).

def fig_fifo_lifo():
    W, H = 920, 430
    p = []
    p.append(line(465, 58, 465, H - 26, color="#d8dde3", sw=1.4, dash="6 5"))

    # ── Черга (ліворуч) ──
    p.append(text(235, 66, "Черга (FIFO)", size=16, color=NEG, bold=True))
    p.append(text(235, 88, "кладемо в хвіст, беремо з голови", size=11, color=MUTED))
    cw, ch = 56, 50
    qx0, qy = 96, 175
    for i, ltr in enumerate(["A", "B", "C"]):
        x = qx0 + i * cw
        p.append(rect(x, qy, cw - 6, ch, fill=FILLED, stroke=FIELD, sw=1.6, rx=5))
        p.append(text(x + (cw - 6) / 2, qy + ch / 2 + 6, ltr, size=17, color=INK, bold=True))
    # голова (ліворуч) — вихід
    lx = qx0
    p.append(arrow(lx - 12, qy + ch / 2, lx - 54, qy + ch / 2, color=NEG, sw=2.2))
    p.append(text(lx - 30, qy - 16, "голова", size=12, color=NEG, bold=True))
    p.append(text(lx - 30, qy + ch + 24, "забрати", size=10.5, color=MUTED))
    # хвіст (праворуч) — вхід
    rx = qx0 + 3 * cw
    p.append(arrow(rx + 42, qy + ch / 2, rx + 4, qy + ch / 2, color=FIELD, sw=2.2))
    p.append(text(rx + 20, qy - 16, "хвіст", size=12, color=FIELD, bold=True))
    p.append(text(rx + 20, qy + ch + 24, "покласти", size=10.5, color=MUTED))
    # порядок
    p.append(text(235, 336, "зайшли:  A → B → C", size=13, color=INK))
    p.append(text(235, 364, "вийшли:  A → B → C", size=14, color=FIELD, bold=True))
    p.append(text(235, 390, "порядок збережено", size=11.5, color=FIELD))

    # ── Стек (праворуч) ──
    p.append(text(690, 66, "Стек (LIFO)", size=16, color=POS, bold=True))
    p.append(text(690, 88, "кладемо й беремо з одного кінця", size=11, color=MUTED))
    sw_, sh = 76, 44
    sx, sy0 = 690 - sw_ / 2, 162
    for i, ltr in enumerate(["C", "B", "A"]):       # зверху вниз
        y = sy0 + i * sh
        p.append(rect(sx, y, sw_, sh - 4, fill=FILLED, stroke=FIELD, sw=1.6, rx=5))
        p.append(text(690, y + (sh - 4) / 2 + 6, ltr, size=17, color=INK, bold=True))
    p.append(arrow(690 - 28, sy0 - 44, 690 - 28, sy0 - 6, color=FIELD, sw=2.0))
    p.append(text(690 - 28, sy0 - 52, "кладемо", size=10, color=FIELD, bold=True))
    p.append(arrow(690 + 28, sy0 - 6, 690 + 28, sy0 - 44, color=POS, sw=2.0))
    p.append(text(690 + 28, sy0 - 52, "беремо", size=10, color=POS, bold=True))
    p.append(text(690, sy0 + 3 * sh + 18, "обидва — згори", size=10.5, color=MUTED))
    # порядок
    p.append(text(690, 336, "зайшли:  A → B → C", size=13, color=INK))
    p.append(text(690, 364, "вийшли:  C → B → A", size=14, color=POS, bold=True))
    p.append(text(690, 390, "порядок перевернуто", size=11.5, color=POS))

    render(os.path.join(OUT, "fifo-lifo.svg"), W, H, *p,
           title="Черга віддає елементи як прийшли, стек — задом наперед")


# ── impls: порівняння реалізацій за вартістю ─────────────────────────────────
# Ідея: наївний масив коштує O(n) на забір (червона клітина), а кільце, список і
# два стеки дають O(1); кільце обмежене N, решта — безмежні; два стеки — аморт.

def fig_impls():
    W, H = 900, 402
    p = []
    headers = ["Реалізація", "Покласти", "Забрати", "Пам'ять", "Межа"]
    rows = [
        ("Наївний масив (зсув)", "O(1)", "O(n)", "O(n)", "росте"),
        ("Кільцевий буфер",      "O(1)", "O(1)", "O(N) фікс.", "до N"),
        ("Зв'язаний список",     "O(1)", "O(1)", "O(n) + вузли", "безмежна"),
        ("Два стеки",            "O(1)", "O(1)*", "O(n)", "безмежна"),
    ]
    colw = [252, 130, 130, 168, 130]
    x0 = (W - sum(colw)) / 2.0
    y0, rh = 76, 52

    cx = x0
    for j, htxt in enumerate(headers):
        p.append(rect(cx, y0, colw[j], rh, fill=HEAD, stroke=NEG, sw=1.4, rx=0))
        p.append(text(cx + colw[j] / 2, y0 + rh / 2 + 5, htxt, size=12.5, color=INK, bold=True))
        cx += colw[j]

    for r, row in enumerate(rows):
        ry = y0 + (r + 1) * rh
        cx = x0
        for j, val in enumerate(row):
            bad = (j == 2 and val.startswith("O(n)"))
            good = (j in (1, 2) and val.startswith("O(1)"))
            fill = BAD if bad else (FILLED if good else BG)
            stroke = POS if bad else (FIELD if good else "#c7ccd2")
            p.append(rect(cx, ry, colw[j], rh, fill=fill, stroke=stroke, sw=1.3, rx=0))
            if j == 0:
                p.append(text(cx + 14, ry + rh / 2 + 5, val, size=12.5, color=INK,
                              bold=True, anchor="start"))
            else:
                p.append(text(cx + colw[j] / 2, ry + rh / 2 + 5, val, size=13,
                              color=(POS if bad else INK), bold=False))
            cx += colw[j]

    p.append(text(W / 2, y0 + 5 * rh + 30,
                  "* амортизовано: окремий забір іноді дорогий, але в середньому O(1)",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "impls.svg"), W, H, *p,
           title="Реалізації черги: чим платимо за дешеві покласти й забрати")


# ── two-stacks: черга з двох стеків ──────────────────────────────────────────
# Ідея: стек перевертає порядок; вхідний тримає C,B,A догори дриґом; переливання
# — друге перевертання — повертає найстаріший A нагору вихідного, і виходить FIFO.

def fig_two_stacks():
    W, H = 900, 470
    p = []
    sw_, sh = 66, 42
    sy0 = 168

    # ── лівий стек: вхідний ──
    lx = 200
    p.append(text(lx, 78, "Вхідний стек", size=14, color=NEG, bold=True))
    p.append(text(lx, 98, "кладемо сюди", size=10.5, color=MUTED))
    for i, ltr in enumerate(["C", "B", "A"]):       # зверху вниз
        y = sy0 + i * sh
        p.append(rect(lx - sw_ / 2, y, sw_, sh - 4, fill=FILLED, stroke=NEG, sw=1.6, rx=5))
        p.append(text(lx, y + (sh - 4) / 2 + 6, ltr, size=16, color=INK, bold=True))
    p.append(arrow(lx, sy0 - 42, lx, sy0 - 6, color=NEG, sw=2.0))
    p.append(text(lx, sy0 - 50, "пхаємо A, B, C", size=10, color=NEG))
    p.append(text(lx, sy0 + 3 * sh + 16, "зверху C — останній", size=10, color=MUTED))

    # ── правий стек: вихідний (після переливання) ──
    rx = 700
    p.append(text(rx, 78, "Вихідний стек", size=14, color=FIELD, bold=True))
    p.append(text(rx, 98, "знімаємо звідси", size=10.5, color=MUTED))
    for i, ltr in enumerate(["A", "B", "C"]):       # зверху вниз
        y = sy0 + i * sh
        p.append(rect(rx - sw_ / 2, y, sw_, sh - 4, fill=FILLED, stroke=FIELD, sw=1.6, rx=5))
        p.append(text(rx, y + (sh - 4) / 2 + 6, ltr, size=16, color=INK, bold=True))
    p.append(arrow(rx, sy0 - 6, rx, sy0 - 42, color=FIELD, sw=2.0))
    p.append(text(rx, sy0 - 50, "знімаємо A першим", size=10, color=FIELD))
    p.append(text(rx, sy0 + 3 * sh + 16, "зверху A — найстаріший", size=10, color=MUTED))

    # ── переливання посередині ──
    p.append(text(W / 2, 200, "переливаємо", size=13, color=INK, bold=True))
    p.append(text(W / 2, 220, "по одному: C, B, A", size=10.5, color=MUTED))
    p.append(arrow(lx + sw_ / 2 + 26, sy0 + sh + 20, rx - sw_ / 2 - 26, sy0 + sh + 20,
                   color=INK, sw=2.2))

    p.append(mtext(W / 2, 372, [
        "Стек перевертає порядок. Вхідний тримає C, B, A догори дриґом.",
        "Переливання — це друге перевертання: воно скасовує перше,",
        "і у вихідному найстаріший A опиняється зверху.",
        "Виходять A, B, C — рівно в тому порядку, в якому зайшли.",
    ], size=11.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "two-stacks.svg"), W, H, *p,
           title="Черга з двох стеків: двічі перевернути — те саме, що не перевертати")


# ── amort-bank: реальна вартість стрибає, амортизована лишається ≤2 ───────────
# Ідея: 8 операцій із прогону. Вгорі — реальна робота c_i (два переливання
# стрибають до 3). Внизу — потенціал Φ=|вхідний| як «банк»: росте на enqueue,
# спорожняється на переливанні, оплачуючи стрибок.

def fig_amort_bank():
    W, H = 940, 520
    p = []
    ops  = ["enq A", "enq B", "deq→A", "enq C", "enq D", "deq→B", "deq→C", "deq→D"]
    cost = [1, 1, 3, 1, 1, 1, 3, 1]     # реальна робота c_i
    phi  = [1, 2, 0, 1, 2, 2, 0, 0]     # Φ = розмір вхідного ПІСЛЯ операції
    pour = [False, False, True, False, False, False, True, False]

    x0, slot, bw = 116, 96, 52
    xend = x0 + 7 * slot + bw           # правий край останнього стовпчика
    def cx(i): return x0 + i * slot + bw / 2

    # ── верхня панель: реальна вартість ──
    base, unit = 250, 44
    p.append(text(W / 2, 40, "Реальна вартість операції cᵢ  (одиниць роботи)",
                  size=14.5, color=INK, bold=True))
    yceil = base - 2 * unit
    p.append(line(x0 - 16, yceil, xend + 12, yceil, color=NEG, sw=1.6, dash="7 5"))
    p.append(text(xend + 18, yceil + 4, "â ≤ 2", size=12, color=NEG, bold=True, anchor="start"))
    p.append(line(x0 - 16, base, xend + 12, base, color=INK, sw=1.4))
    for i in range(8):
        h = cost[i] * unit
        x = x0 + i * slot
        p.append(rect(x, base - h, bw, h, fill=(BAD if pour[i] else FILLED),
                      stroke=(POS if pour[i] else FIELD), sw=1.6, rx=4))
        p.append(text(x + bw / 2, base - h - 9, str(cost[i]),
                      size=13, color=(POS if pour[i] else INK), bold=True))
        p.append(text(x + bw / 2, base + 20, ops[i], size=10.5, color=INK))
        p.append(text(x + bw / 2, base + 35, "#%d" % (i + 1), size=9.5, color=MUTED))
    for i in (2, 6):
        p.append(text(cx(i), base - cost[i] * unit - 27, "переливання", size=10, color=POS, bold=True))

    # ── нижня панель: потенціал (банк) ──
    base2, unit2 = 470, 36
    p.append(text(W / 2, 322,
                  "Потенціал Φ = розмір вхідного стека  (банк наперед оплачених переливань)",
                  size=13.5, color=INK, bold=True))
    p.append(line(x0 - 16, base2, xend + 12, base2, color=INK, sw=1.4))
    for i in range(8):
        h = phi[i] * unit2
        x = x0 + i * slot
        drained = i in (2, 6)          # переливання спорожнило банк саме тут
        if h > 0:
            p.append(rect(x, base2 - h, bw, h, fill=HEAD, stroke=NEG, sw=1.4, rx=4))
        p.append(text(x + bw / 2, (base2 - h - 8) if h > 0 else base2 - 8,
                      str(phi[i]), size=12.5 if drained else 11.5,
                      color=POS if drained else NEG, bold=True))
    p.append(text(W / 2, base2 + 30,
                  "червоний 0 — банк спорожнено переливанням (кроки 3 і 7)",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "amort-bank.svg"), W, H, *p,
           title="Реальна вартість стрибає на переливанні, амортизована лишається ≤ 2")


# ── early-pour-bug: раннє переливання руйнує FIFO ────────────────────────────
# Ідея: out=[B] (наступний за FIFO), in=[C,D]. Правильно — не переливати й зняти B.
# Помилка — перелити попри непорожній out: C,D лягають поверх B, знімається C.

def fig_early_pour_bug():
    W, H = 900, 500
    p = []
    p.append(fitbox(150, 34, 600, 52,
                    "Стан:  вихідний = [B]  (зверху B — за FIFO наступний),   вхідний = [C, D]",
                    size=13, fill=FILL, stroke=MUTED, color=INK, bold=True))

    cw, ch = 96, 46
    p.append(line(W / 2, 108, W / 2, H - 96, color="#d8dde3", sw=1.4, dash="6 5"))

    # ── ліворуч: правильно ──
    lx = 240
    p.append(text(lx, 132, "Правильно", size=15, color=FIELD, bold=True))
    p.append(text(lx, 152, "вихідний непорожній → НЕ переливаємо", size=10.5, color=MUTED))
    ly = 232
    p.append(text(lx, ly - 16, "вихідний", size=11, color=MUTED))
    p.append(rect(lx - cw / 2, ly, cw, ch, fill=FILLED, stroke=FIELD, sw=1.7, rx=5))
    p.append(text(lx, ly + ch / 2 + 6, "B", size=18, color=INK, bold=True))
    p.append(fitbox(lx - 118, 336, 236, 50, "pop → B  ✓\nобслужили найстаріший",
                    size=12.5, fill=FILLED, stroke=FIELD, color=INK, bold=True))

    # ── праворуч: помилка ──
    rx = 655
    p.append(text(rx, 132, "Помилка", size=15, color=POS, bold=True))
    p.append(text(rx, 152, "перелили попри непорожній вихідний", size=10.5, color=MUTED))
    ry0 = 196
    stack = [("C", False), ("D", False), ("B", True)]   # зверху вниз після хибного переливання
    p.append(text(rx, ry0 - 16, "вихідний (зіпсутий)", size=11, color=POS))
    for i, (lt, isB) in enumerate(stack):
        yy = ry0 + i * ch
        p.append(rect(rx - cw / 2, yy, cw, ch,
                      fill=("#f3d9d4" if isB else FILLED),
                      stroke=(POS if isB else FIELD), sw=1.7, rx=5))
        p.append(text(rx, yy + ch / 2 + 6, lt, size=18, color=INK, bold=True))
    p.append(text(rx + cw / 2 + 12, ry0 + 2 * ch + ch / 2 + 5,
                  "← B застряг унизу", size=11, color=POS, bold=True, anchor="start"))
    p.append(fitbox(rx - 122, 396, 244, 50, "pop → C  ✗\nвидали C, а мали B",
                    size=12.5, fill=BAD, stroke=POS, color=INK, bold=True))

    p.append(mtext(W / 2, 468, [
        "Переливати можна ЛИШЕ коли вихідний стек порожній —",
        "інакше новіші елементи лягають поверх старіших, і FIFO ламається.",
    ], size=11.5, color=INK, lh=1.5))

    render(os.path.join(OUT, "early-pour-bug.svg"), W, H, *p,
           title="Раннє переливання руйнує порядок: новіші лягають поверх старіших")


# ── timeline-history: як жива черга стала структурою даних ───────────────────
# Ідея: давня звичка «перший прийшов — перший вийшов» тричі перекладена —
# на мову математики (Ерланг), машини (спулінг) і структур даних (Кнут).

def fig_history():
    W, H = 1040, 476
    AMBER = "#b9770e"
    axis_y = 232
    p = []

    # підзаголовок ліворуч (передісторія)
    p.append(text(58, 58, "жива черга — старша за письмо", size=12.5,
                  color=MUTED, anchor="start", italic=True))

    # вісь часу зі стрілкою праворуч
    p.append(line(58, axis_y, 946, axis_y, color="#c7ccd2", sw=2.0))
    p.append(arrow(946, axis_y, 982, axis_y, color="#c7ccd2", sw=2.0))
    p.append(text(966, axis_y + 26, "час", size=11.5, color=MUTED))

    # вузли: (x, рядки-боксу, рік, колір-року, заливка, обвід, рядки-підпису)
    nodes = [
        (180, ["Аґнер Ерланг", "Копенгаген"], "1909 · 1917", NEG,
         "#eef4ff", NEG,
         ["виклики — пуассонів", "потік; формули втрат", "і чекання (FCFS)"]),
        (405, ["Девід Кендалл"], "1953", NEG,
         "#eef4ff", NEG,
         ["нотація черг;", "дисципліни FIFO,", "LIFO, випадкова"]),
        (630, ["IBM 7070", "спулінг (SPOOL)"], "1958", AMBER,
         "#fff5e6", AMBER,
         ["перша велика черга", "в машині: буфер між", "процесором і папером"]),
        (855, ["Дональд Кнут", "TAOCP, том 1"], "1968", FIELD,
         "#eafaf0", FIELD,
         ["черга, стек, дек —", "названі структури", "даних"]),
    ]

    for x, box_lines, year, ycol, fill, stroke, cap in nodes:
        # бокс «хто / де» над віссю
        box, bw, bh = textbox(x, 148, "\n".join(box_lines), size=13,
                              pad=11, fill=fill, stroke=stroke, sw=1.6,
                              color=INK, bold=True, rx=7)
        p.append(box)
        # вертикальний з'єднувач до крапки на осі
        p.append(line(x, 148 + bh / 2 + 2, x, axis_y - 7, color="#c7ccd2", sw=1.4))
        # крапка на осі
        p.append(circle(x, axis_y, 6, fill=INK, stroke=BG, sw=1.5))
        # рік під віссю
        p.append(text(x, axis_y + 34, year, size=15, color=ycol, bold=True))
        # підпис «що зроблено»
        p.append(mtext(x, axis_y + 58, cap, size=11, color=INK, lh=1.5))

    render(os.path.join(OUT, "timeline-history.svg"), W, H, *p,
           title="Черга: тричі перекладена давня звичка")


if __name__ == "__main__":
    fig_fifo_lifo()
    fig_impls()
    fig_two_stacks()
    fig_amort_bank()
    fig_early_pour_bug()
    fig_history()
    print("figs: готово")
