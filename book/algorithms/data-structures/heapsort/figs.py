# -*- coding: utf-8 -*-
"""Фігури для статті «Сортування купою (heapsort)» та її проєкту.
Генерує чотири SVG у ./img: heapsort-inplace, heapsort-phases, sortdown-step
(для статті) і heap-index-map (для вставки proj-heapsort — 0-індексація дітей
та межа внутрішні/листки).
Значення в прикладах узгоджені з покроковим прогоном у статті
(max-купа [9,7,8,3,6,2])."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HEAP = "#eef2f7"   # купа (світло-сіре)
TAIL = "#e6f7ee"   # відсортований хвіст (світло-зелене)
HOT  = "#fdecea"   # виділення пари, що обмінюється
GRN  = "#1e824c"   # темно-зелений напис


def cell(x, y, w, h, val, fill=FILL, stroke=LINE, sw=1.5, tc=INK):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=4) +
            text(x + w / 2, y + h / 2 + 6, val, size=17, color=tc, bold=True))


def node(cx, cy, val, r=18, fill=FILL, stroke=LINE, sw=1.8, tc=INK):
    return (circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw) +
            text(cx, cy + 6, val, size=16, color=tc, bold=True))


# ── Фігура 1: один масив — дві зони, межа повзе вліво ────────────────────────
def fig_inplace():
    W, H = 520, 280
    cw, ch = 48, 40
    x0 = 150
    rows = [
        ("після кроку 1", [9, 7, 8, 3, 6, 2], [8, 7, 2, 3, 6, 9], 5),
        ("після кроку 2", None,               [7, 6, 2, 3, 8, 9], 4),
        ("після кроку 3", None,               [6, 3, 2, 7, 8, 9], 3),
    ]
    f = []
    # легенда
    ly = 52
    f.append(rect(140, ly - 13, 16, 16, fill=HEAP, stroke=LINE, sw=1.2, rx=3))
    f.append(text(162, ly, "купа (тане)", size=13, anchor="start", color=MUTED))
    f.append(rect(268, ly - 13, 16, 16, fill=TAIL, stroke=LINE, sw=1.2, rx=3))
    f.append(text(290, ly, "відсортований хвіст (росте)", size=13, anchor="start", color=MUTED))
    y = 84
    for label, _pre, vals, hc in rows:
        f.append(text(x0 - 14, y + ch / 2 + 5, label, size=13, anchor="end", color=MUTED))
        for i, v in enumerate(vals):
            fill = HEAP if i < hc else TAIL
            f.append(cell(x0 + i * cw, y, cw, ch, str(v), fill=fill))
        bx = x0 + hc * cw
        f.append(line(bx, y - 8, bx, y + ch + 8, color=POS, sw=3.5))
        y += 56
    f.append(text(x0 + 3 * cw, y + 4, "межа купи повзе вліво  ←", size=12,
                  anchor="middle", color=POS))
    render(os.path.join(IMG, "heapsort-inplace.svg"), W, H, *f,
           title="Один масив — дві зони")


# ── Фігура 2: дві фази на смузі часу ─────────────────────────────────────────
def fig_phases():
    W, H = 780, 250
    f = []
    barY, barH = 100, 52
    x1, x2, x3 = 90, 214, 690     # фаза1: 90..214 ; фаза2: 214..690 (ширша)
    # фаза 1 — heapify
    f.append(rect(x1, barY, x2 - x1, barH, fill=HEAP, stroke=LINE, sw=1.5, rx=5))
    f.append(text((x1 + x2) / 2, barY - 16, "Фаза 1 — heapify", size=14, bold=True))
    f.append(text((x1 + x2) / 2, barY + barH / 2 + 5, "дешева", size=13, color=MUTED))
    f.append(text((x1 + x2) / 2, barY + barH + 24, "O(n)", size=15, color=NEG, bold=True))
    # фаза 2 — (n−1) просіювань
    f.append(rect(x2, barY, x3 - x2, barH, fill=TAIL, stroke=LINE, sw=1.5, rx=5))
    f.append(text((x2 + x3) / 2, barY - 16, "Фаза 2 — (n−1) просіювань вниз", size=14, bold=True))
    f.append(text((x2 + x3) / 2, barY + barH / 2 + 5, "уся вага тут", size=13, color=MUTED))
    f.append(text((x2 + x3) / 2, barY + barH + 24, "(n−1) × O(log n)  =  O(n log n)",
                  size=15, color=NEG, bold=True))
    # підсумкова дужка
    by = barY + barH + 44
    f.append(line(x1, by, x1, by + 9, color=INK, sw=1.5))
    f.append(line(x1, by + 9, x3, by + 9, color=INK, sw=1.5))
    f.append(line(x3, by, x3, by + 9, color=INK, sw=1.5))
    f.append(text((x1 + x3) / 2, by + 30,
                  "Разом: O(n log n) — однаковий за будь-якого входу", size=14, bold=True))
    render(os.path.join(IMG, "heapsort-phases.svg"), W, H, *f,
           title="Дві фази — і вся вага у другій")


# ── Фігура 3: анатомія одного кроку (дерево + масив), до і після ──────────────
def fig_step():
    W, H = 720, 330
    f = []
    r = 18

    def tree_edges(pts):
        return "".join(line(a[0], a[1], b[0], b[1], color=LINE, sw=1.5) for a, b in pts)

    def arr(cx, y, vals, hi_fill, cw=32, ch=28):
        out = []
        x = cx - len(vals) * cw / 2
        for i, v in enumerate(vals):
            out.append(cell(x + i * cw, y, cw, ch, str(v), fill=hi_fill.get(i, FILL)))
        return "".join(out)

    # ── ЛІВЕ дерево: до кроку (корінь = максимум) ──
    lcx = 150
    f.append(text(lcx, 62, "До кроку: корінь — максимум", size=13, bold=True))
    lroot = (lcx, 100); ll1 = (lcx - 52, 163); lr1 = (lcx + 52, 163)
    ll2a = (lcx - 80, 226); ll2b = (lcx - 24, 226); lr2a = (lcx + 24, 226)
    f.append(tree_edges([(lroot, ll1), (lroot, lr1), (ll1, ll2a), (ll1, ll2b), (lr1, lr2a)]))
    f.append(node(*ll1, "7")); f.append(node(*lr1, "8"))
    f.append(node(*ll2a, "3")); f.append(node(*ll2b, "6"))
    f.append(node(*lroot, "9", fill=HOT, stroke=POS))     # максимум (піде в хвіст)
    f.append(node(*lr2a, "2", fill=HOT, stroke=POS))      # останній (піде в корінь)
    f.append(arr(lcx, 262, [9, 7, 8, 3, 6, 2], {0: HOT, 5: HOT}))
    f.append(text(lcx, 308, "червоні — корінь і останній обмінюються", size=12, color=POS))

    # ── стрілка переходу ──
    f.append(arrow(305, 175, 415, 175, color=INK, sw=2.4))
    f.append(text(360, 150, "обмін 9 ⇄ 2,", size=13, anchor="middle", bold=True))
    f.append(text(360, 205, "тоді вниз", size=13, anchor="middle", bold=True))

    # ── ПРАВЕ дерево: після (купа знову правильна) ──
    rcx = 570
    f.append(text(rcx, 62, "Після: новий корінь тоне вниз", size=13, bold=True))
    rroot = (rcx, 100); rl1 = (rcx - 52, 163); rr1 = (rcx + 52, 163)
    rl2a = (rcx - 80, 226); rl2b = (rcx - 24, 226)
    f.append(tree_edges([(rroot, rl1), (rl1, rl2a), (rl1, rl2b)]))
    # шлях просіювання: 2 з кореня в праву дитину (обмін із більшою — 8)
    f.append(arrow(rroot[0] + 8, rroot[1] + 6, rr1[0] - 6, rr1[1] - 8, color=GRN, sw=2.2))
    f.append(node(*rl1, "7")); f.append(node(*rl2a, "3")); f.append(node(*rl2b, "6"))
    f.append(node(*rroot, "8", fill=TAIL, stroke=GRN))    # більша дитина піднялась
    f.append(node(*rr1, "2", fill=HOT, stroke=POS))       # елемент занурився
    rfill = {i: HEAP for i in range(5)}
    rfill[5] = TAIL
    f.append(arr(rcx, 262, [8, 7, 2, 3, 6, 9], rfill))
    f.append(text(rcx, 308, "9 у хвості — на місці назавжди", size=12, color=GRN))

    render(os.path.join(IMG, "sortdown-step.svg"), W, H, *f,
           title="Анатомія одного кроку heapsort")


# ── Фігура 4 (для proj): 0-індексація дітей і межа внутрішні/листки ───────────
def fig_index_map():
    W, H = 760, 448
    BLUE = "#2457d6"   # NEG — обвід внутрішніх
    GRN2 = "#27ae60"   # FIELD — обвід листків
    f = []

    # легенда
    f.append(rect(118, 42, 15, 15, fill=HEAP, stroke=BLUE, sw=1.6, rx=3))
    f.append(text(142, 55, "внутрішні вузли 0…4 — просіюємо", size=13,
                  anchor="start", color=MUTED))
    f.append(rect(432, 42, 15, 15, fill=TAIL, stroke=GRN2, sw=1.6, rx=3))
    f.append(text(456, 55, "листки 5…9 — пропускаємо", size=13,
                  anchor="start", color=MUTED))

    # координати вузлів (індекс: x,y)
    P = {0: (380, 98), 1: (200, 168), 2: (560, 168),
         3: (120, 238), 4: (280, 238), 5: (480, 238), 6: (640, 238),
         7: (90, 308), 8: (160, 308), 9: (245, 308)}
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (3, 8), (4, 9)]

    # ребра (під вузлами)
    for a, b in edges:
        f.append(line(P[a][0], P[a][1], P[b][0], P[b][1], color=LINE, sw=1.5))
    # відсутня права дитина вузла 4 (індекс 10 ≥ n) — пунктиром
    f.append('<line x1="280" y1="238" x2="330" y2="308" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="4 4"/>' % MUTED)
    f.append('<circle cx="330" cy="308" r="19" fill="none" stroke="%s" '
             'stroke-width="1.5" stroke-dasharray="4 4"/>' % MUTED)
    f.append(text(330, 313, "10", size=15, color=MUTED))
    f.append(text(330, 344, "10 ≥ n — нема", size=11, color=MUTED))

    # підписи формул на ребрах кореня
    f.append(text(292, 130, "2i+1", size=12, color=MUTED))
    f.append(text(470, 130, "2i+2", size=12, color=MUTED))

    # вузли
    for i, (cx, cy) in P.items():
        if i == 4:                                   # останній внутрішній — старт heapify
            f.append(node(cx, cy, str(i), r=20, fill=HOT, stroke=POS, sw=2.6, tc=POS))
        elif i <= 4:
            f.append(node(cx, cy, str(i), fill=HEAP, stroke=BLUE, sw=1.8))
        else:
            f.append(node(cx, cy, str(i), fill=TAIL, stroke=GRN2, sw=1.8))

    # виноска старту heapify
    f.append(arrow(430, 326, 300, 252, color=POS, sw=2.0))
    f.append(mtext(470, 298, ["heapify стартує з i = n/2−1 = 4", "і йде вниз до 0"],
                   size=13, color=POS, bold=True))

    # масив індексів
    ay, aw, ah, ax0 = 366, 40, 32, 210
    f.append(text(200, ay + ah / 2 + 5, "індекс:", size=13, anchor="end", color=MUTED))
    for i in range(10):
        fill = HOT if i == 4 else (HEAP if i < 5 else TAIL)
        tc = POS if i == 4 else INK
        f.append(cell(ax0 + i * aw, ay, aw, ah, str(i), fill=fill, tc=tc))

    # формула-підсумок
    f.append(text(W / 2, 428, "діти(i) = 2·i+1 та 2·i+2      батько(c) = (c−1)/2",
                  size=14, bold=True))

    render(os.path.join(IMG, "heap-index-map.svg"), W, H, *f,
           title="0-індексація: індекс вузла → індекси дітей")


# ── Фігура 5 (для вставки hist): три внески, одна назва ───────────────────────
def fig_contributions():
    W, H = 880, 452
    AMBER = "#c98a17"
    f = []
    px, pw, ph, gap = 70, 740, 96, 12
    panels = [
        (NEG,   "#eef2fb", "1964", "Джон Вільямс", "британець",  "Ідея + структура",
         ["Купа сортує на місці; O(n log n) гарантовано.",
          "Та будував купу згори — зайві O(n log n)."]),
        (FIELD, "#eaf7f0", "1964", "Роберт Флойд", "американець", "Ефективна форма на місці",
         ["Побудова знизу за O(n); чистий спуск на місці.",
          "Форма, якою heapsort пишуть досі. З його treesort."]),
        (AMBER, "#fbf4e6", "1997", "Девід Массер", "американець", "Гібрид — і справжня робота",
         ["introsort: quicksort для швидкості + heapsort-запобіжник.",
          "Лежить у std::sort — і майже ніколи не спрацьовує."]),
    ]
    y = 64
    for stripe, fill, year, name, nat, nature, desc in panels:
        f.append(rect(px, y, pw, ph, fill=fill, stroke=LINE, sw=1.4, rx=8))
        f.append(rect(px, y, 8, ph, fill=stripe, stroke=stripe, sw=0, rx=0))
        # ліва зона: рік / ім'я / національність (центровані у смузі 0..150)
        lc = px + 78
        f.append(text(lc, y + 44, year, size=25, color=stripe, bold=True))
        f.append(text(lc, y + 68, name, size=13, color=INK, bold=True))
        f.append(text(lc, y + 86, nat, size=11, color=MUTED))
        f.append(line(px + 156, y + 16, px + 156, y + ph - 16, color=LINE, sw=1.0))
        # права зона: характер внеску + опис
        rx0 = px + 176
        f.append(text(rx0, y + 36, nature, size=16, color=stripe, anchor="start", bold=True))
        f.append(mtext(rx0, y + 60, desc, size=12, color=MUTED, anchor="start", lh=1.35))
        y += ph + gap
    # підсумкова смуга
    sy = y + 4
    f.append(rect(px, sy, pw, 48, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=8))
    f.append(mtext(px + pw / 2, sy + 20,
                   ["«heapsort», який ти запускаєш = ідея Вільямса + форма Флойда,",
                    "а introsort (1997) дав цій формі роботу — усередині std::sort"],
                   size=13, color=INK, bold=True, lh=1.35))
    render(os.path.join(IMG, "heapsort-contributions.svg"), W, H, *f,
           title="Три подарунки, одна назва — і 33 роки до діла")


# ── Фігура 6 (вставка math): ціна другої фази — площа під ⌊log₂ m⌋ ────────────
def fig_sortdown_cost():
    import math
    W, H = 880, 330
    f = []
    ms = list(range(1, 16))
    hs = [int(math.floor(math.log2(m))) for m in ms]  # 0,1,1,2,2,2,2,3×8
    x0 = 120          # ліва межа першого стовпчика
    base = 252        # базова лінія
    bw = 32
    lvh = 46          # px на рівень
    top = base - 3 * lvh
    # вісь Y із поділками 0..3
    f.append(line(x0 - 10, base + 2, x0 - 10, top - 16, color=INK, sw=1.4))
    for lv in range(0, 4):
        yy = base - lv * lvh
        f.append(line(x0 - 14, yy, x0 - 10, yy, color=INK, sw=1.2))
        f.append(text(x0 - 20, yy + 4, str(lv), size=12, anchor="end", color=MUTED))
    f.append(text(x0 - 14, top - 26, "⌊log₂ m⌋", size=12, anchor="start", color=MUTED, bold=True))
    # базова лінія
    f.append(line(x0 - 10, base, x0 + 15 * bw + 6, base, color=INK, sw=1.4))
    # стовпчики-сходинка
    for i, (m, h) in enumerate(zip(ms, hs)):
        bx = x0 + i * bw
        if h > 0:
            f.append(rect(bx + 3, base - h * lvh, bw - 6, h * lvh,
                          fill=HEAP, stroke=NEG, sw=1.3, rx=2))
        f.append(text(bx + bw / 2, base + 16, str(m), size=11, anchor="middle", color=MUTED))
    f.append(text(x0 + 15 * bw / 2, base + 38,
                  "розмір купи m на кроці сортдауну  (n = 16)",
                  size=12, anchor="middle", color=MUTED))
    # анотація праворуч, поза стовпчиками
    box, _, _ = textbox(738, 150,
                        ["площа = Σ ⌊log₂ m⌋ = 34 рівні",
                         "≈  n·log₂ n − Θ(n)",
                         "×2 порівн./рівень  →  ≈ 2n·log₂ n"],
                        size=13, pad=12, fill=FILL, stroke=NEG, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "math-sortdown-cost.svg"), W, H, *f,
           title="Ціна другої фази — площа під сходинкою ⌊log₂ m⌋")


# ── Фігура 7 (вставка math): мала величина тоне на всю висоту; виняток рівних ─
def fig_no_lucky_case():
    W, H = 900, 420
    f = []
    # ── ліворуч: спуск малої величини 2 по гілці більших дітей ──
    root = (220, 108)
    n14, n9 = (150, 184), (300, 184)
    n13, n8 = (95, 262), (205, 262)
    n12, n6 = (60, 340), (152, 340)
    for a, b in [(root, n14), (root, n9), (n14, n13), (n14, n8), (n13, n12), (n13, n6)]:
        f.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=1.5))
    # зелені стрілки спуску вздовж спини 2 → 14 → 13 → 12
    for a, b in [(root, n14), (n14, n13), (n13, n12)]:
        f.append(arrow(a[0] - 6, a[1] + 10, b[0] + 6, b[1] - 10, color=GRN, sw=2.2))
    # вузли-сестри (не на шляху)
    f.append(node(*n9, "9")); f.append(node(*n8, "8")); f.append(node(*n6, "6"))
    # спина (більші діти) + посаджений корінь
    f.append(node(*n14, "14", fill=TAIL, stroke=GRN))
    f.append(node(*n13, "13", fill=TAIL, stroke=GRN))
    f.append(node(*n12, "12", fill=TAIL, stroke=GRN))
    f.append(node(*root, "2", fill=HOT, stroke=POS, sw=2.4, tc=POS))
    f.append(text(220, 74, "у корені — мала посаджена величина 2", size=13, bold=True))
    # колонка порівнянь, вирівняна по рівнях
    for (yy, s) in [(188, "2 < 14  → тоне"), (266, "2 < 13  → тоне"),
                    (344, "2 < 12  → лист")]:
        f.append(text(360, yy, s, size=13, anchor="start", color=GRN, bold=True))
    # розділювач
    f.append(line(575, 70, 575, 372, color=LINE, sw=1.0, dash="5 5"))
    # ── праворуч: правило зупину + виняток рівних ключів ──
    box1, _, _ = textbox(738, 108, ["Правило зупину", "x ⩾ обидві дитини"],
                         size=13, pad=11, fill=FILL, stroke=INK, sw=1.3, bold=True)
    f.append(box1)
    er, ea, eb = (738, 205), (695, 275), (781, 275)
    f.append(line(er[0], er[1], ea[0], ea[1], color=LINE, sw=1.5))
    f.append(line(er[0], er[1], eb[0], eb[1], color=LINE, sw=1.5))
    f.append(node(*er, "=", fill=TAIL, stroke=GRN))
    f.append(node(*ea, "=", fill=TAIL, stroke=GRN))
    f.append(node(*eb, "=", fill=TAIL, stroke=GRN))
    box2, _, _ = textbox(738, 344, ["усі ключі рівні:", "стоп на глибині 0  →  O(n)"],
                         size=12, pad=10, fill="#eaf7f0", stroke=GRN, sw=1.4)
    f.append(box2)
    render(os.path.join(IMG, "math-no-lucky-case.svg"), W, H, *f,
           title="Мала величина тоне на всю висоту; єдина втеча — рівні ключі")


if __name__ == "__main__":
    fig_inplace()
    fig_phases()
    fig_step()
    fig_index_map()
    fig_contributions()
    fig_sortdown_cost()
    fig_no_lucky_case()
    print("OK:", os.listdir(IMG))
