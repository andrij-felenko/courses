# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки до §3.6.6 — «Пули блоків: динамічна пам'ять
без фрагментації» (Модуль 3, Розділ 3.6, до теми 3.6.6).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/ тієї самої папки розділу.
Імена файлів УНІКАЛЬНІ: fig-19-6pool-*.svg — щоб не зіткнутися з уже наявними
fig-19-6a-* (toy-allocator) і fig-19-6m-* (fragmentation) у цьому ж розділі.

Стиль (AUTHORING §9): білий фон; «+» червоний, «−» синій; «вільне» зелене;
стрілки через marker; шрифт sans-serif. Єдиний вигляд із рештою розділу —
допоміжні функції скопійовано з figs.py розділу. Підписи — «Рис. 3.6.6a.k»
(нумерація триває після toy-allocator-вставки до тієї самої теми).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"

USED_FILL = "#fbe6e4"   # зайнятий слот (червонувата)
FREE_FILL = "#e7f3ea"   # вільний слот (зеленувата)
HDR_FILL  = "#f3f6fb"   # службова смужка (синювата)
WASTE     = "#f3ead7"   # змарнований хвіст (внутрішня фрагментація)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def curve(x1, y1, cx, cy, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(s, n):
    words, ln, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            ln.append(cur)
            cur = w
    if cur:
        ln.append(cur)
    return ln


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6a.1 — анатомія пулу: однаковісінькі слоти над суцільною ареною,
# а вільні слоти зшито у free list, причому покажчик next ЖИВЕ ВСЕРЕДИНІ
# самого вільного слота (службового заголовка на блок не треба).
# ════════════════════════════════════════════════════════════════════════════
def fig_anatomy():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 32, "Пул блоків: один масив, нарізаний на однакові слоти", 21, INK, "middle", "bold")
    s += text(W / 2, 54, "усі слоти одного розміру; вільні зшито в список, а посилання next лежить ВСЕРЕДИНІ вільного слота",
              12, GREY, "middle", style="italic")

    # суцільна арена, поділена на 8 рівних слотів
    x0, y0 = 60, 118
    n = 8
    sw_px = 100        # ширина слота на схемі
    sh = 104           # висота слота
    # стан: True=вільний, False=зайнятий. Порядок у вільному списку — як на схемі.
    occ = [False, True, False, False, True, False, True, False]  # False=зайнятий
    # індекси вільних слотів (за адресою)
    free_idx = [i for i, f in enumerate(occ) if f]

    # підпис арени під смугою
    s += arrow(x0, y0 + sh + 30, x0 + n * sw_px, y0 + sh + 30, GREY, 1.6)
    s += text(x0, y0 + sh + 48, "низькі адреси", 11.5, GREY, "start", style="italic")
    s += text(x0 + n * sw_px, y0 + sh + 48, "вищі адреси →", 11.5, GREY, "end", style="italic")
    s += text(x0 + n * sw_px / 2, y0 - 14, "арена пулу = суцільний масив байтів (виділяється раз, статично)",
              11.5, GREY, "middle", style="italic")

    # малюємо слоти
    for i in range(n):
        x = x0 + i * sw_px
        if occ[i]:
            s += rect(x, y0, sw_px, sh, FREE_FILL, GREEN, 2)
            s += text(x + sw_px / 2, y0 + 30, "ВІЛЬНО", 12.5, GREEN, "middle", "bold")
            # поле next усередині вільного слота
            s += rect(x + 10, y0 + 44, sw_px - 20, 30, "#ffffff", GREEN, 1.4, 4)
            s += mono(x + sw_px / 2, y0 + 64, "next →", 11.5, GREEN, "middle", "bold")
        else:
            s += rect(x, y0, sw_px, sh, USED_FILL, RED, 2)
            s += text(x + sw_px / 2, y0 + 30, "зайнято", 12.5, RED, "middle", "bold")
            s += text(x + sw_px / 2, y0 + 58, "дані", 11.5, RED, "middle")
        # номер слота
        s += mono(x + 4, y0 + sh - 8, f"#{i}", 10.5, GREY)

    # голова вільного списку
    hx, hy = x0, y0 + sh + 86
    s += rect(hx, hy, 150, 40, "#fff7e8", AMBER, 1.8, 6)
    s += text(hx + 75, hy + 18, "free_head", 13.5, INK, "middle", "bold")
    s += text(hx + 75, hy + 33, "(вершина стека вільних)", 10, GREY, "middle", style="italic")

    def slot_bottom(i):
        return x0 + i * sw_px + sw_px / 2, y0 + sh

    # дуга від голови до першого вільного слота (знизу)
    fx, fy = slot_bottom(free_idx[0])
    s += curve(hx + 150, hy + 8, (hx + 150 + fx) / 2, hy - 6, fx, fy + 4, GREEN, 2.2)

    # дуги next між вільними слотами — поверху арени
    for a, b in zip(free_idx, free_idx[1:]):
        ax = x0 + a * sw_px + sw_px - 16
        bx = x0 + b * sw_px + 16
        midx = (ax + bx) / 2
        s += curve(ax, y0 - 2, midx, y0 - 40, bx, y0 - 2, GREEN, 2.2)
        s += text(midx, y0 - 44, "next", 10.5, GREEN, "middle", "bold")
    # останній → NULL
    lx = x0 + free_idx[-1] * sw_px + sw_px - 16
    s += curve(lx, y0 - 2, lx + 36, y0 - 36, lx + 64, y0 - 2, GREEN, 2.2)
    s += text(lx + 72, y0 - 4, "NULL", 11.5, GREY, "start", "bold")

    # пояснювальні ноти
    ny = y0 + sh + 150
    s += rect(60, ny, W - 120, 152, "#fcfcfc", FAINT, 1.4, 8)
    notes = [
        ("Усі слоти — рівно одного розміру.",
         "Арену ділять на N однакових клітинок наперед. Будь-який запит дістає цілий слот; «впору чи ні» вирішує єдине порівняння з розміром слота."),
        ("Заголовка на блок не треба.",
         "Поки слот вільний, його власне тіло порожнє — туди й кладуть посилання next. Зайнятий слот віддає всі байти даним: службових витрат на блок нуль."),
        ("Free list тут — простий стек.",
         "free_head вказує на перший вільний слот, той — на наступний (next), і так до NULL. Порядок у списку не зобов'язаний збігатися з порядком адрес."),
    ]
    yy = ny + 24
    for h, b in notes:
        s += text(78, yy, "•", 14, AMBER, "start", "bold")
        s += text(92, yy, h, 12.5, INK, "start", "bold")
        for j, t in enumerate(_wrap(b, 96)):
            s += text(92, yy + 16 + j * 15, t, 11.5, INK, "start")
        yy += 16 + 15 * len(_wrap(b, 96)) + 6
    save("fig-19-6pool-1-anatomy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6a.2 — O(1): alloc = зняти вершину списку, free = покласти назад;
# і контраст із загальним розпорядником, що ШУКАЄ блок по списку (first-fit).
# ════════════════════════════════════════════════════════════════════════════
def fig_o1():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "Виділення й звільнення за O(1): зняв вершину — поклав назад", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "pool_alloc бере перший слот зі списку (без пошуку); pool_free кладе слот назад на вершину",
              12, GREY, "middle", style="italic")

    # ── ЛІВО: pool_alloc — pop з вершини ──────────────────────────────────────
    lx = 70
    s += rect(lx, 86, 380, 200, "#f1f7f2", GREEN, 1.7, 10)
    s += text(lx + 190, 110, "pool_alloc()  —  знімаємо вершину", 13.5, GREEN, "middle", "bold")

    # ланцюжок вільних слотів (вертикально)
    cx = lx + 70
    cy = 132
    bw, bh, gap = 150, 30, 16
    chain = ["слот A", "слот B", "слот C"]
    for i, nm in enumerate(chain):
        y = cy + i * (bh + gap)
        fill = "#ffffff" if i else "#d8efdf"
        s += rect(cx, y, bw, bh, fill, GREEN, 1.6 if i else 2.4, 5)
        s += text(cx + bw / 2, y + 20, nm, 12, INK, "middle", "bold" if i == 0 else "normal")
        if i < len(chain) - 1:
            s += arrow(cx + bw / 2, y + bh + 2, cx + bw / 2, y + bh + gap - 2, GREEN, 1.6)
            s += mono(cx + bw / 2 + 8, y + bh + gap / 2 + 5, "next", 10, GREEN)
    # голова → A
    s += text(cx - 56, cy + 12, "free_head", 11.5, AMBER, "start", "bold")
    s += arrow(cx - 8, cy + 14, cx, cy + 14, AMBER, 1.8)
    # видача A назовні
    s += arrow(cx + bw + 6, cy + 14, cx + bw + 60, cy + 14, RED, 2)
    s += text(cx + bw + 64, cy + 10, "→ повертаємо", 11, RED, "start", "bold")
    s += text(cx + bw + 64, cy + 25, "  адресу A", 11, RED, "start")
    s += text(lx + 16, 270, "free_head ← A.next (тепер вершина = B).  Жодного перебору — три-чотири інструкції.",
              10.8, INK, "start", style="italic")

    # ── ПРАВО: pool_free — push на вершину ────────────────────────────────────
    rx = 490
    s += rect(rx, 86, 380, 200, "#eef3fb", BLUE, 1.7, 10)
    s += text(rx + 190, 110, "pool_free(p)  —  кладемо назад", 13.5, BLUE, "middle", "bold")
    cx2 = rx + 110
    for i, nm in enumerate(["слот B", "слот C"]):
        y = cy + (i + 1) * (bh + gap)
        s += rect(cx2, y, bw, bh, "#ffffff", BLUE, 1.6, 5)
        s += text(cx2 + bw / 2, y + 20, nm, 12, INK, "middle")
        if i == 0:
            s += arrow(cx2 + bw / 2, y + bh + 2, cx2 + bw / 2, y + bh + gap - 2, BLUE, 1.6)
    # повернений слот стає новою вершиною
    s += rect(cx2, cy, bw, bh, "#d6e4fa", BLUE, 2.4, 5)
    s += text(cx2 + bw / 2, cy + 20, "p (повертаємо)", 11.5, BLUE, "middle", "bold")
    s += arrow(cx2 + bw / 2, cy + bh + 2, cx2 + bw / 2, cy + bh + gap - 2, BLUE, 1.8)
    s += mono(cx2 + bw / 2 + 8, cy + bh + gap / 2 + 5, "next", 10, BLUE)
    s += text(cx2 - 66, cy + 12, "free_head", 11.5, AMBER, "start", "bold")
    s += arrow(cx2 - 8, cy + 14, cx2, cy + 14, AMBER, 1.8)
    s += text(rx + 16, 270, "p.next ← free_head;  free_head ← p.  Теж кілька інструкцій — і теж O(1).",
              10.8, INK, "start", style="italic")

    # ── НИЗ: контраст із загальним розпорядником (first-fit, §3.6.6a) ─────────
    by = 320
    s += rect(60, by, W - 120, 200, "#fdf4f4", RED, 1.6, 10)
    s += text(W / 2, by + 26, "Чому це швидше за звичайний malloc", 14.5, RED, "middle", "bold")

    # загальний розпорядник: пошук по різнорозмірних блоках
    gy = by + 52
    gx = 90
    gen = [("48", "free", GREEN), ("16", "зайн.", RED), ("32", "free", GREEN),
           ("96", "free", GREEN), ("24", "зайн.", RED)]
    px = gx
    for sz, lab, col in gen:
        w = 70 + int(sz) // 2
        fill = FREE_FILL if col == GREEN else USED_FILL
        s += rect(px, gy, w, 40, fill, col, 1.6, 4)
        s += mono(px + 6, gy + 17, f"{sz}Б", 11, col)
        s += text(px + w / 2, gy + 33, lab, 10.5, col, "middle")
        px += w + 6
    s += text(gx, gy - 8, "malloc(40): перебирає список, міряє КОЖЕН блок «чи влізе 40?», ділить знайдений…",
              11, INK, "start")
    # «лупа» пошуку
    s += arrow(gx + 20, gy + 56, gx + 20, gy + 44, RED, 1.6)
    s += text(gx + 26, gy + 60, "малий?", 10, RED, "start")
    s += arrow(gx + 150, gy + 56, gx + 150, gy + 44, RED, 1.6)
    s += text(gx + 156, gy + 60, "зайнятий?", 10, RED, "start")
    s += arrow(gx + 300, gy + 56, gx + 300, gy + 44, GREEN, 1.6)
    s += text(gx + 306, gy + 60, "влазить → ділю", 10, GREEN, "start")

    # підсумковий рядок
    s += rect(90, by + 150, W - 180, 38, "#f1f7f2", GREEN, 1.7, 8)
    s += text(W / 2, by + 173,
              "Пул: усі слоти однакові → шукати нема чого. Вершину видно одразу — звідси O(1) і сталий, передбачуваний час.",
              12, INK, "middle", "bold")
    save("fig-19-6pool-2-o1.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6a.3 — чого пул позбувається і чим платить: нуль зовнішньої
# фрагментації (будь-який вільний слот годиться), але є дві межі —
# внутрішня фрагментація (хвіст слота марнується) і запит, більший за слот.
# ════════════════════════════════════════════════════════════════════════════
def fig_tradeoff():
    W, H = 940, 580
    s = header(W, H)
    s += text(W / 2, 32, "Що пул прибирає — і чим за це платить", 21, INK, "middle", "bold")
    s += text(W / 2, 54, "зовнішньої фрагментації немає за визначенням; натомість з'являється внутрішня — і жорстка стеля розміру",
              12, GREY, "middle", style="italic")

    # ── ВЕРХ-ЛІВО: нуль зовнішньої фрагментації ──────────────────────────────
    lx, ly = 60, 92
    s += rect(lx, ly, 410, 196, "#f1f7f2", GREEN, 1.7, 10)
    s += text(lx + 205, ly + 24, "Зовнішньої фрагментації НЕМАЄ", 14, GREEN, "middle", "bold")
    # ряд однакових слотів, частина вільна, частина зайнята, в довільному порядку
    sx, sy, sc, sg = lx + 22, ly + 48, 44, 8
    pat = [0, 1, 1, 0, 1, 0, 0, 1]   # 1=вільний
    for i, f in enumerate(pat):
        x = sx + i * (sc + sg)
        fill = FREE_FILL if f else USED_FILL
        col = GREEN if f else RED
        s += rect(x, sy, sc, 44, fill, col, 1.8, 4)
        s += text(x + sc / 2, sy + 27, "✓" if f else "·", 14, col, "middle", "bold")
    s += text(lx + 22, sy + 70, "Будь-який вільний слот годиться для будь-якого запиту —", 11, INK, "start")
    s += text(lx + 22, sy + 86, "усі однакові. «Розкиданих уламків, що не влазять», не буває:", 11, INK, "start")
    s += text(lx + 22, sy + 102, "є вільний слот → виділення вдається. Завжди.", 11, GREEN, "start", "bold")
    s += text(lx + 22, sy + 124, "(порівняй з «паркінгом із проміжками» §3.6.6 — тут проміжки", 10.3, GREY, "start", style="italic")
    s += text(lx + 22, sy + 138, "однакові, тож кожен придатний)", 10.3, GREY, "start", style="italic")

    # ── ВЕРХ-ПРАВО: внутрішня фрагментація (хвіст марнується) ─────────────────
    rx = 500
    s += rect(rx, ly, 380, 196, "#fff8ee", AMBER, 1.7, 10)
    s += text(rx + 190, ly + 24, "Зате з'являється ВНУТРІШНЯ", 14, AMBER, "middle", "bold")
    # один слот: корисна частина + змарнований хвіст
    bx, by2, bw2 = rx + 40, ly + 48, 300
    s += rect(bx, by2, bw2, 46, "#ffffff", INK, 1.6, 4)
    used_w = bw2 * 0.62
    s += rect(bx, by2, used_w, 46, USED_FILL, RED, 1.6, 0)
    s += rect(bx + used_w, by2, bw2 - used_w, 46, WASTE, AMBER, 1.4, 0)
    s += text(bx + used_w / 2, by2 + 28, "дані 40 Б", 12, RED, "middle", "bold")
    s += text(bx + used_w + (bw2 - used_w) / 2, by2 + 22, "марно", 10.5, AMBER, "middle", "bold")
    s += text(bx + used_w + (bw2 - used_w) / 2, by2 + 36, "24 Б", 10.5, AMBER, "middle")
    s += text(bx, by2 - 6, "слот 64 Б", 11, GREY, "start", style="italic")
    s += text(rx + 24, by2 + 80, "Поклав 40 Б у слот на 64 Б — 24 Б усередині слота", 11, INK, "start")
    s += text(rx + 24, by2 + 96, "лежать без діла. Це внутрішня фрагментація:", 11, INK, "start")
    s += text(rx + 24, by2 + 112, "плата за те, що всі слоти однакові.", 11, AMBER, "start", "bold")
    s += text(rx + 24, by2 + 134, "Лік: підбирати розмір слота близько до типового", 10.3, GREY, "start", style="italic")
    s += text(rx + 24, by2 + 148, "запиту (або тримати кілька пулів різних розмірів).", 10.3, GREY, "start", style="italic")

    # ── НИЗ: жорстка стеля + як вибирають кількість слотів ────────────────────
    ny = ly + 218
    s += rect(60, ny, W - 120, 144, "#fdf4f4", RED, 1.6, 10)
    s += text(W / 2, ny + 26, "Дві тверді межі, з якими треба рахуватися", 14.5, RED, "middle", "bold")
    items = [
        ("Запит більший за слот — відмова.",
         "Слот фіксований: треба 100 Б, а слот 64 Б — виділення провалюється, хоч вільних слотів багато. Розмір слота обирають під найбільший очікуваний об'єкт."),
        ("Скінчилися слоти — теж відмова.",
         "Слотів рівно N (виділено на старті). Узяв усі — наступний alloc дає NULL. Тому N рахують під пік одночасно живих об'єктів, із запасом."),
    ]
    yy = ny + 50
    for h, b in items:
        s += text(82, yy, "■", 12, RED, "start", "bold")
        s += text(100, yy, h, 12.5, INK, "start", "bold")
        for j, t in enumerate(_wrap(b, 104)):
            s += text(100, yy + 16 + j * 15, t, 11, INK, "start")
        yy += 16 + 15 * len(_wrap(b, 104)) + 6
    save("fig-19-6pool-3-tradeoff.svg", s)


if __name__ == "__main__":
    fig_anatomy()
    fig_o1()
    fig_tradeoff()
    print("done.")
