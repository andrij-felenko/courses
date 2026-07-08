# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Розгалуження за станом проти об'єктів-станів ──────────────────────────
def fig_switch_vs_objects():
    W, H = 860, 470
    frags = []
    frags.append(text(W / 2, 30, "Один прапорець стану, розмазаний по методах — проти об'єкта на кожен стан",
                      size=16, bold=True))

    # роздільна вісь
    frags.append(line(W / 2, 58, W / 2, 432, color=MUTED, sw=1.2, dash="5 5"))

    # ── ЛІВОРУЧ: розгалуження ──
    lcx = W / 4
    frags.append(text(lcx, 78, "РОЗГАЛУЖЕННЯ ЗА СТАНОМ", size=13, color=POS, bold=True))
    frags.append(text(lcx, 96, "кожен метод питає state знову", size=11, color=MUTED, italic=True))
    methods = [
        "pay()   → switch(state){…}",
        "ship()  → switch(state){…}",
        "cancel()→ switch(state){…}",
    ]
    my = 124
    for m in methods:
        frags.append(rect(lcx - 165, my, 330, 40, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
        frags.append(text(lcx, my + 25, m, size=13, color=INK))
        my += 52
    # виноска про біль
    frags.append(fitbox(lcx - 165, my + 6, 330, 78,
                        "новий стан → правити КОЖЕН метод;\nодин пропущений case —\nтихий баг",
                        size=12.5, pad=10, fill=BG, stroke=POS, sw=1.4, rx=8, color=INK))

    # ── ПРАВОРУЧ: об'єкти-стани ──
    rcx = 3 * W / 4
    frags.append(text(rcx, 78, "ОБ'ЄКТ НА КОЖЕН СТАН", size=13, color=FIELD, bold=True))
    frags.append(text(rcx, 96, "поведінка стану зібрана в ньому", size=11, color=MUTED, italic=True))
    states = ["New", "Paid", "Shipped"]
    sy = 124
    for s in states:
        frags.append(rect(rcx - 165, sy, 330, 40, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
        frags.append(text(rcx - 150, sy + 25, s, size=13, color=INK, anchor="start", bold=True))
        frags.append(text(rcx + 150, sy + 25, "pay ship cancel", size=11.5, color=MUTED, anchor="end"))
        sy += 52
    frags.append(fitbox(rcx - 165, sy + 6, 330, 78,
                        "новий стан → новий клас збоку;\nстарі не чіпаєш,\nпропустити case ніде",
                        size=12.5, pad=10, fill=BG, stroke=FIELD, sw=1.4, rx=8, color=INK))

    render(os.path.join(OUT, 'switch-vs-objects.svg'), W, H, *frags)


# ── 2. Діаграма переходів: життєвий цикл документа ──────────────────────────
def fig_transitions():
    W, H = 820, 380
    frags = []
    frags.append(text(W / 2, 30, "Стан + подія → новий стан: життєвий цикл документа", size=16, bold=True))

    # три стани-вузли в ряд + петля відхилення
    r = 62
    ys = 190
    nodes = {
        "Чернетка":  (130, ys),
        "На розгляді": (410, ys),
        "Опубліковано": (690, ys),
    }
    # спершу малюємо стрілки, тоді вузли поверх
    def edge(a, b, label, dy=0, curve=0, lx=None, above=True):
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        # горизонтальний перехід між сусідами: від краю до краю кола
        if y1 == y2 and curve == 0:
            frags.append(arrow(x1 + r, y1 + dy, x2 - r, y2 + dy, color=NEG, sw=2))
            mx = (x1 + x2) / 2
            ly = y1 + dy - 12 if above else y1 + dy + 22
            frags.append(text(mx, ly, label, size=12.5, color=NEG, bold=True))
        return

    edge("Чернетка", "На розгляді", "надіслати")
    edge("На розгляді", "Опубліковано", "схвалити")

    # петля відхилення: На розгляді → Чернетка, дугою знизу
    x1, y1 = nodes["На розгляді"]
    x2, y2 = nodes["Чернетка"]
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2"/>'
                 % (x1 - r * 0.5, y1 + r * 0.85, x1 - 40, y1 + 120, x2 + 40, y2 + 120, x2 + r * 0.5, y2 + r * 0.85, POS))
    frags.append('<path d="M %.1f %.1f l 10 -2 l -1 11 z" fill="%s"/>' % (x2 + r * 0.5, y2 + r * 0.85, POS))
    frags.append(text((x1 + x2) / 2, ys + 128, "відхилити", size=12.5, color=POS, bold=True))

    # петля-самоперехід на «Опубліковано»: архівувати (у себе, зверху)
    x3, y3 = nodes["Опубліковано"]
    frags.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (x3 - r * 0.4, y3 - r * 0.9, x3 - 55, y3 - 120, x3 + 55, y3 - 120, x3 + r * 0.4, y3 - r * 0.9, MUTED))
    frags.append('<path d="M %.1f %.1f l 2 10 l -11 -2 z" fill="%s"/>' % (x3 + r * 0.4, y3 - r * 0.9, MUTED))
    frags.append(text(x3, y3 - 128, "змінити → знову На розгляді", size=11.5, color=MUTED, italic=True))

    # вузли
    for name, (cx, cy) in nodes.items():
        frags.append(circle(cx, cy, r, fill="#f4f6f8", stroke=INK, sw=2.2))
        frags.append(text(cx, cy + 5, name, size=13, color=INK, bold=True))

    # старт
    frags.append(text(120, ys + r + 26, "старт", size=11, color=MUTED, italic=True))
    frags.append(text(W / 2, H - 16,
                      "у стані «Опубліковано» подія «надіслати» нічого не робить — правило належить самому стану",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'transitions.svg'), W, H, *frags)


# ── 3. Стан проти Стратегії: той самий кістяк, різний намір ─────────────────
def fig_state_vs_strategy():
    W, H = 880, 430
    frags = []
    frags.append(text(W / 2, 30, "Той самий кістяк — протилежний намір", size=16, bold=True))

    frags.append(line(W / 2, 60, W / 2, 402, color=MUTED, sw=1.2, dash="5 5"))

    # спільні три ролі підписами (ідентичні обабіч) — покажемо як однакові рамки
    lcx = W / 4
    rcx = 3 * W / 4

    # заголовки
    frags.append(rect(lcx - 150, 70, 300, 36, fill="#f4f6f8", stroke=POS, sw=2.2, rx=8))
    frags.append(text(lcx, 94, "СТРАТЕГІЯ", size=14, color=POS, bold=True))
    frags.append(rect(rcx - 150, 70, 300, 36, fill="#f4f6f8", stroke=FIELD, sw=2.2, rx=8))
    frags.append(text(rcx, 94, "СТАН", size=14, color=FIELD, bold=True))

    # контекст (однакова коробка обабіч)
    for cx, col in [(lcx, POS), (rcx, FIELD)]:
        frags.append(rect(cx - 130, 130, 260, 44, fill=BG, stroke=INK, sw=1.8, rx=8))
        frags.append(text(cx, 157, "Контекст → тримає поле", size=12.5, color=INK, bold=True))
    # три взаємозамінні реалізації
    for cx, col, labels in [(lcx, POS, ["ByBike", "ByCar", "ByFoot"]),
                            (rcx, FIELD, ["Draft", "Review", "Live"])]:
        bx = cx - 130
        bw = 260 / 3 - 8
        for i, lb in enumerate(labels):
            x = bx + i * (260 / 3) + 4
            frags.append(rect(x, 200, bw, 38, fill="#f4f6f8", stroke=col, sw=1.5, rx=6))
            frags.append(text(x + bw / 2, 224, lb, size=12, color=INK))
        # стрілка від контексту вниз до реалізацій
        frags.append(arrow(cx, 174, cx, 198, color=col, sw=1.6))

    # ── ключова відмінність унизу ──
    # хто ставить поле
    frags.append(fitbox(lcx - 150, 264, 300, 62,
                        "ХТО ставить поле: КЛІЄНТ зовні,\nодин раз. Далі не міняється.",
                        size=12.5, pad=10, fill="#fdecea", stroke=POS, sw=1.6, rx=8, color=INK))
    frags.append(fitbox(rcx - 150, 264, 300, 62,
                        "ХТО ставить поле: САМІ стани,\nперемикаючи Контекст на льоту.",
                        size=12.5, pad=10, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8, color=INK))
    # що знають одна про одну
    frags.append(fitbox(lcx - 150, 336, 300, 52,
                        "реалізації одна про одну\nне знають",
                        size=12.5, pad=8, fill=BG, stroke=POS, sw=1.3, rx=8, color=INK))
    frags.append(fitbox(rcx - 150, 336, 300, 52,
                        "стани ЗНАЮТЬ наступний\nі перемикають на нього",
                        size=12.5, pad=8, fill=BG, stroke=FIELD, sw=1.3, rx=8, color=INK))

    render(os.path.join(OUT, 'state-vs-strategy.svg'), W, H, *frags)


# ── 4. Повна таблиця переходів замовлення (матриця стан × подія) ────────────
def fig_transition_table():
    # стани (рядки) × події (колонки); клітина — куди веде або чому заборонено
    states = ["New", "Paid", "Shipped", "Cancelled", "Refunded"]
    events = ["pay", "ship", "cancel", "refund"]
    # (текст, вид): "go"=дозволено з переходом, "no"=заборона (кидок), "ig"=ігнор
    cells = {
        ("New",       "pay"):    ("→ Paid",     "go"),
        ("New",       "ship"):   ("кидок",      "no"),
        ("New",       "cancel"): ("→ Cancelled","go"),
        ("New",       "refund"): ("кидок",      "no"),
        ("Paid",      "pay"):    ("кидок",      "no"),
        ("Paid",      "ship"):   ("→ Shipped",  "go"),
        ("Paid",      "cancel"): ("→ Refunded", "go"),
        ("Paid",      "refund"): ("→ Refunded", "go"),
        ("Shipped",   "pay"):    ("кидок",      "no"),
        ("Shipped",   "ship"):   ("ігнор",      "ig"),
        ("Shipped",   "cancel"): ("кидок",      "no"),
        ("Shipped",   "refund"): ("→ Refunded", "go"),
        ("Cancelled", "pay"):    ("кидок",      "no"),
        ("Cancelled", "ship"):   ("кидок",      "no"),
        ("Cancelled", "cancel"): ("ігнор",      "ig"),
        ("Cancelled", "refund"): ("кидок",      "no"),
        ("Refunded",  "pay"):    ("кидок",      "no"),
        ("Refunded",  "ship"):   ("кидок",      "no"),
        ("Refunded",  "cancel"): ("кидок",      "no"),
        ("Refunded",  "refund"): ("ігнор",      "ig"),
    }
    colw = 148
    rowh = 46
    x0 = 150          # ліва колонка під назви станів
    y0 = 92           # верх під шапку подій
    W = x0 + len(events) * colw + 24
    H = y0 + len(states) * rowh + 60
    frags = []
    frags.append(text(W / 2, 32, "Таблиця дозволених переходів: рядок — стан, колонка — подія",
                      size=16, bold=True))
    frags.append(text(W / 2, 54, "зелена клітина веде далі; червона кидає; сіра тихо ігнорує",
                      size=12, color=MUTED, italic=True))

    # кутова клітина
    frags.append(rect(24, y0 - rowh, x0 - 24, rowh, fill=FILL, stroke=MUTED, sw=1.2, rx=0))
    frags.append(text(24 + (x0 - 24) / 2, y0 - rowh / 2 + 5, "стан \\ подія", size=12,
                      color=MUTED, italic=True))
    # шапка подій
    for j, ev in enumerate(events):
        cx = x0 + j * colw
        frags.append(rect(cx, y0 - rowh, colw, rowh, fill="#eef1f4", stroke=MUTED, sw=1.2, rx=0))
        frags.append(text(cx + colw / 2, y0 - rowh / 2 + 5, ev + "()", size=13, color=INK, bold=True))
    # рядки станів
    for i, st in enumerate(states):
        ry = y0 + i * rowh
        frags.append(rect(24, ry, x0 - 24, rowh, fill="#eef1f4", stroke=MUTED, sw=1.2, rx=0))
        frags.append(text(24 + (x0 - 24) / 2, ry + rowh / 2 + 5, st, size=13, color=INK, bold=True))
        for j, ev in enumerate(events):
            cx = x0 + j * colw
            txt, kind = cells[(st, ev)]
            if kind == "go":
                fill, stroke, col = "#eafaf0", FIELD, INK
            elif kind == "no":
                fill, stroke, col = "#fdecea", POS, POS
            else:
                fill, stroke, col = "#f1f2f4", MUTED, MUTED
            frags.append(rect(cx, ry, colw, rowh, fill=fill, stroke=stroke, sw=1.4, rx=0))
            frags.append(text(cx + colw / 2, ry + rowh / 2 + 5, txt, size=12.5, color=col,
                              bold=(kind == "go")))

    frags.append(text(W / 2, H - 22,
                      "20 клітин = 5 станів × 4 події — рівно стільки правил має описати будь-яка реалізація",
                      size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, 'transition-table.svg'), W, H, *frags)


# ── 5. Як росте складність: switch-таблиця проти класів ─────────────────────
def fig_complexity_growth():
    W, H = 860, 470
    frags = []
    frags.append(text(W / 2, 30, "Що доводиться правити, коли додаєш ОДИН стан", size=16, bold=True))

    frags.append(line(W / 2, 58, W / 2, 400, color=MUTED, sw=1.2, dash="5 5"))

    lcx = W / 4
    rcx = 3 * W / 4

    # ── ЛІВОРУЧ: switch-таблиця ──
    frags.append(text(lcx, 80, "SWITCH ЗА СТАНОМ", size=13.5, color=POS, bold=True))
    frags.append(text(lcx, 98, "один текст на всі стани й події", size=11, color=MUTED, italic=True))
    frags.append(fitbox(lcx - 175, 116, 350, 52,
                        "новий стан → зайти в КОЖЕН із E методів\nі дописати гілку; забудеш одну — тихий баг",
                        size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.5, rx=8, color=INK))
    # стовпчики зростання правок: 3,4,5 станів
    base = 300
    for k, (n, ev) in enumerate([(3, 4), (4, 4), (5, 4)]):
        bx = lcx - 150 + k * 105
        bh = n * ev * 6          # висота ∝ n*E (площа таблиці)
        frags.append(rect(bx, base - bh, 66, bh, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
        frags.append(text(bx + 33, base - bh - 8, "%d×%d" % (n, ev), size=12, color=POS, bold=True))
        frags.append(text(bx + 33, base + 18, "%d гілок" % (n * ev), size=11.5, color=INK))
    frags.append(text(lcx, base + 44, "ростуть УСІ клітини: O(станів × подій)", size=12,
                      color=POS, bold=True))
    frags.append(text(lcx, base + 64, "додаючи стан, чіпаєш старий код", size=11.5, color=MUTED, italic=True))

    # ── ПРАВОРУЧ: клас на стан ──
    frags.append(text(rcx, 80, "КЛАС НА СТАН", size=13.5, color=FIELD, bold=True))
    frags.append(text(rcx, 98, "кожен стан — свій файл", size=11, color=MUTED, italic=True))
    frags.append(fitbox(rcx - 175, 116, 350, 52,
                        "новий стан → ОДИН новий клас збоку;\nстарі класи не відкриваєш зовсім",
                        size=12, pad=9, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=8, color=INK))
    for k, (n, ev) in enumerate([(3, 4), (4, 4), (5, 4)]):
        bx = rcx - 150 + k * 105
        bh = n * 14              # висота ∝ кількості класів (лінійно)
        frags.append(rect(bx, base - bh, 66, bh, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=4))
        frags.append(text(bx + 33, base - bh - 8, "%d" % n, size=12, color=FIELD, bold=True))
        frags.append(text(bx + 33, base + 18, "%d класів" % n, size=11.5, color=INK))
    frags.append(text(rcx, base + 44, "додається ОДИН клас: O(станів)", size=12, color=FIELD, bold=True))
    frags.append(text(rcx, base + 64, "старий код лишається закритим", size=11.5, color=MUTED, italic=True))

    frags.append(text(W / 2, H - 14,
                      "але кожен клас коштує файла: за малих E switch коротший, за багатьох станів класи дешевші в рості",
                      size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, 'complexity-growth.svg'), W, H, *frags)


# ── 6. Історичні шари: від нервових мереж до об'єктів (для hist-вставки) ─────
def fig_history_layers():
    W, H = 900, 480
    frags = []
    frags.append(text(W / 2, 30, "Три шари, на яких виросла машина станів", size=16, bold=True))

    bx = 60
    ax = W - 52                 # вісь часу праворуч
    bw = ax - bx - 44

    # вісь часу
    frags.append(arrow(ax, 434, ax, 74, color=MUTED, sw=1.6))
    frags.append(text(ax + 6, 70, "час", size=11, color=MUTED, anchor="start", italic=True))
    for yr, yy in [("1943", 410), ("1955", 306), ("1987", 156), ("1994", 100)]:
        frags.append(text(ax - 6, yy + 4, yr, size=11, color=MUTED, anchor="end"))
        frags.append(line(ax - 3, yy, ax + 3, yy, color=MUTED, sw=1))

    # шар 1 — нервові мережі / поняття автомата (низ)
    frags.append(fitbox(bx, 356, bw, 78,
                        "НЕРВОВІ МЕРЕЖІ  →  ПОНЯТТЯ АВТОМАТА\n"
                        "Мак-Каллок і Піттс 1943 · Кліні 1956 (регулярні події)\n"
                        "система живе скінченним набором станів",
                        size=12.5, pad=9, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    # шар 2 — Белл Лабс
    frags.append(fitbox(bx, 256, bw, 78,
                        "БЕЛЛ ЛАБС  →  ДВІ ІМЕННІ ФОРМИ\n"
                        "Мілі 1955: вихід = f(стан, вхід) · Мур 1956: вихід = g(стан)\n"
                        "формальний синтез послідовнісних схем",
                        size=12.5, pad=9, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=10))
    # шар 3 — статечарти
    frags.append(fitbox(bx, 156, bw, 78,
                        "СТАТЕЧАРТИ  →  ПРИБОРКАНА СКЛАДНІСТЬ\n"
                        "Гарел 1987: ієрархія (глибина) + ортогональність\n"
                        "великий автомат перестає вибухати",
                        size=12.5, pad=9, fill="#fdecea", stroke=POS, sw=1.8, rx=10))
    # вершина — патерн Стан
    frags.append(fitbox(bx + bw / 2 - 195, 78, 390, 52,
                        "ПАТЕРН СТАН — Банда чотирьох, 1994\n"
                        "кожен стан стає ОБ'ЄКТОМ (приклад: TCPConnection)",
                        size=12, pad=8, fill=FILL, stroke=INK, sw=2, rx=10))

    # стрілки «спирається на» знизу вгору між серединами смуг
    mid = bx + bw / 2
    frags.append(arrow(mid, 356, mid, 335, color=MUTED, sw=1.6))
    frags.append(arrow(mid, 256, mid, 235, color=MUTED, sw=1.6))
    frags.append(arrow(mid, 156, mid, 131, color=MUTED, sw=1.6))

    render(os.path.join(OUT, 'history-layers.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_switch_vs_objects()
    fig_transitions()
    fig_state_vs_strategy()
    fig_transition_table()
    fig_complexity_growth()
    fig_history_layers()
    print("figures written to", OUT)
