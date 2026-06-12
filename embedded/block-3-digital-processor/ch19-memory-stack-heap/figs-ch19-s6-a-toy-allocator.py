# -*- coding: utf-8 -*-
"""
Генератор SVG для ⚙️-вставки §3.6.6a — «Іграшковий malloc: free list,
виділення, злиття сусідніх блоків» (Модуль 3, Розділ 3.6, до теми 3.6.6).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/ тієї самої папки розділу.
Імена файлів унікальні: fig-19-6a-*.svg (6a = вставка до теми 3.6.6).

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker; єдиний
вигляд із рештою розділу — допоміжні функції скопійовано з figs.py розділу.
Підписи у тексті — «Рис. 3.6.6a.k».
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

# заливки регіонів пам'яті
USED_FILL = "#fbe6e4"   # зайнятий блок (червонувата)
FREE_FILL = "#e7f3ea"   # вільний блок (зеленувата)
HDR_FILL  = "#f3f6fb"   # службовий заголовок блоку (синювата)


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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


# ────────────────────────────────────────────────────────────────────────────
# спільний примітив: «блок» на стрічці пам'яті з службовим заголовком (header)
#   x..x+w по горизонталі; смуга заввишки BH; зверху тонкий заголовок з розміром
# ────────────────────────────────────────────────────────────────────────────
def mem_block(x, y, w, bh, kind, size_label, body_label="", hdr_next=None):
    """kind: 'used'|'free'. Малює заголовок (службове поле) + тіло блоку."""
    s = ""
    hdr_h = 22
    fill = USED_FILL if kind == "used" else FREE_FILL
    edge = RED if kind == "used" else GREEN
    # тіло блоку
    s += rect(x, y, w, bh, fill, edge, 2)
    # службовий заголовок (header) — окрема вузька смужка вгорі
    s += rect(x, y, w, hdr_h, HDR_FILL, BLUE, 1.4)
    s += mono(x + 6, y + 15, size_label, 12, BLUE)
    # підпис тіла
    if body_label:
        s += text(x + w / 2, y + hdr_h + (bh - hdr_h) / 2 + 5, body_label,
                  13.5, edge, "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6a.1 — анатомія: free list як однозв'язний список вільних блоків
# над тією самою стрічкою пам'яті, у кожному блоці службовий заголовок size|next
# ════════════════════════════════════════════════════════════════════════════
def fig_anatomy():
    W, H = 940, 588
    s = header(W, H)
    s += text(W / 2, 32, "Анатомія купи: один масив байтів + список вільних блоків", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен блок носить службовий заголовок (розмір, чи вільний, посилання next); вільні зшито в free list",
              12, GREY, "middle", style="italic")

    # стрічка пам'яті: послідовність блоків зліва направо
    x0, y0, BH = 60, 110, 96
    # (kind, ширина_px, людський_розмір, тіло, чи_у_free_list)
    blocks = [
        ("used", 150, "48 Б", "зайнято", False),
        ("free", 120, "32 Б", "ВІЛЬНО", True),
        ("used", 170, "64 Б", "зайнято", False),
        ("free", 100, "24 Б", "ВІЛЬНО", True),
        ("free", 200, "80 Б", "ВІЛЬНО", True),
    ]
    # координати блоків
    xs = []
    x = x0
    for k, w, *_ in blocks:
        xs.append(x)
        x += w
    end = x

    # підпис «низькі/високі адреси» під стрічкою
    s += arrow(x0, y0 + BH + 26, end, y0 + BH + 26, GREY, 1.6)
    s += text(x0, y0 + BH + 44, "низькі адреси", 11.5, GREY, "start", style="italic")
    s += text(end, y0 + BH + 44, "вищі адреси →", 11.5, GREY, "end", style="italic")

    for i, (k, w, sz, lab, infl) in enumerate(blocks):
        s += mem_block(xs[i], y0, w, BH, k, f"size {sz}", lab)
        # позначка «чи вільний» у заголовку праворуч
        flag = "free=0" if k == "used" else "free=1"
        s += mono(xs[i] + w - 6, y0 + 15, flag, 11, RED if k == "used" else GREEN, "end")

    # вузол-голова списку
    hx, hy = x0, 360
    s += rect(hx, hy, 130, 38, "#fff7e8", AMBER, 1.8, 6)
    s += text(hx + 65, hy + 17, "free_list", 13.5, INK, "middle", "bold")
    s += text(hx + 65, hy + 32, "(голова списку)", 10.5, GREY, "middle", style="italic")

    # дуги next: голова → перший вільний → другий вільний → третій вільний → NULL
    free_idx = [i for i, b in enumerate(blocks) if b[4]]
    # точки «next» беремо біля верху кожного вільного блоку
    def top_mid(i):
        return xs[i] + blocks[i][1] / 2, y0
    # від голови (правий край вузла) до низу першого вільного блоку
    fx, fy = top_mid(free_idx[0])
    s += curve(hx + 130, hy + 19, (hx + 130 + fx) / 2 + 20, hy + 12, fx, fy + BH + 4, GREEN, 2.2)
    # між вільними блоками — дуги поверху
    for a, b in zip(free_idx, free_idx[1:]):
        ax, _ = top_mid(a)
        bx, _ = top_mid(b)
        ax = xs[a] + blocks[a][1] - 14
        bx = xs[b] + 14
        midx = (ax + bx) / 2
        s += curve(ax, y0 - 2, midx, y0 - 46, bx, y0 - 2, GREEN, 2.2)
        s += text(midx, y0 - 50, "next", 11, GREEN, "middle", "bold")
    # останній → NULL
    lx = xs[free_idx[-1]] + blocks[free_idx[-1]][1] - 14
    s += curve(lx, y0 - 2, lx + 40, y0 - 40, lx + 70, y0 - 2, GREEN, 2.2)
    s += text(lx + 78, y0 - 4, "NULL", 12, GREY, "start", "bold")

    # пояснювальна нота: зайняті блоки у списку НЕ присутні
    ny = 410
    s += rect(60, ny, W - 120, 168, "#fcfcfc", FAINT, 1.4, 8)
    notes = [
        ("Службовий заголовок (header).", "Кілька байтів перед кожним блоком: його розмір, прапорець «вільний?» і — у вільних — посилання next. За них платить кожне виділення."),
        ("Free list — лише вільні блоки.", "Зайняті в списку не присутні; вони «зникають», поки їх не повернуть. Голова free_list — єдина точка входу в перебір."),
        ("Адреси ростуть зліва направо.", "Сусідство в пам'яті ≠ сусідство у списку: вільні блоки за адресою можуть бути розкидані, а next зв'язує їх у будь-якому порядку."),
    ]
    yy = ny + 24
    for h, b in notes:
        s += text(78, yy, "•", 14, AMBER, "start", "bold")
        s += text(92, yy, h, 12.5, INK, "start", "bold")
        # перенесення тіла (вужче — кирилиця ширша за латиницю)
        words = b.split()
        ln, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= 74:
                cur = (cur + " " + w).strip()
            else:
                ln.append(cur); cur = w
        if cur:
            ln.append(cur)
        for j, t in enumerate(ln):
            s += text(92, yy + 16 + j * 15, t, 11.5, INK, "start")
        yy += 16 + 15 * len(ln) + 8
    save("fig-19-6a-1-anatomy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6a.2 — first-fit + split: malloc(40) йде по списку, бере перший,
# що влазить, і відрізає від нього хвіст назад у free list
# ════════════════════════════════════════════════════════════════════════════
def fig_firstfit():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 32, "Виділення: «перший, що влазить» (first-fit) + відрізання хвоста (split)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "malloc(40): йдемо по free list, беремо перший блок ≥ 40; якщо лишок великий — ділимо блок надвоє",
              12, GREY, "middle", style="italic")

    # верхній рядок: ДО — список з трьох вільних блоків, по них іде покажчик пошуку
    x0 = 70
    yT = 96
    BH = 70
    befs = [("16 Б", 110, False), ("24 Б", 130, False), ("96 Б", 220, True)]  # третій підходить
    s += text(x0, yT - 14, "ДО malloc(40): пробігаємо список, поки блок не влізе", 13.5, INK, "start", "bold")
    xs = []
    x = x0
    for sz, w, ok in befs:
        xs.append(x); x += w + 30
    for i, (sz, w, ok) in enumerate(befs):
        s += mem_block(xs[i], yT, w, BH, "free", f"size {sz}", "ВІЛЬНО")
        # вердикт пошуку
        verdict = "40 ≤ 96 ✓ беремо" if ok else "40 > розмір ✗"
        s += text(xs[i] + w / 2, yT + BH + 18, verdict, 11.5,
                  GREEN if ok else RED, "middle", "bold")
    # стрілки «йдемо далі» між блоками
    for i in range(len(befs) - 1):
        a = xs[i] + befs[i][1]
        b = xs[i + 1]
        s += arrow(a + 4, yT + BH / 2, b - 4, yT + BH / 2, BLUE, 2)
    # покажчик free_list зверху над першим
    s += text(xs[0], yT - 32, "free_list →", 12, AMBER, "start", "bold")

    # стрілка переходу ДО→ПІСЛЯ
    s += arrow(W / 2, yT + BH + 38, W / 2, yT + BH + 70, INK, 2.4)
    s += text(W / 2 + 12, yT + BH + 60, "беремо блок 96 Б під запит 40 Б", 12.5, INK, "start", "bold")

    # нижній рядок: ПІСЛЯ — блок 96 поділено: 40 віддано, 56 лишилось вільним
    yB = 360
    s += text(x0, yB - 14, "ПІСЛЯ: блок 96 Б ділимо — 40 Б віддаємо, решту (56 Б − header) лишаємо у free list", 13.5, INK, "start", "bold")
    # позиція колишнього блоку 96
    bx = xs[2]
    # частина, яку віддали (used 40)
    wU = 96
    wF = 150
    s += mem_block(bx, yB, wU, BH, "used", "size 40", "ВИДАНО")
    s += mem_block(bx + wU, yB, wF, BH, "free", "size 56", "ЛИШОК")
    # підписи під ними
    s += text(bx + wU / 2, yB + BH + 18, "повертаємо покажчик сюди", 11, RED, "middle", "bold")
    s += arrow(bx + wU / 2, yB + BH + 24, bx + 10, yB + BH - 6, RED, 1.6)
    s += text(bx + wU + wF / 2, yB + BH + 18, "хвіст → назад у free list", 11, GREEN, "middle", "bold")

    # права колонка: правила вибору блоку
    rx = bx + wU + wF + 40
    s += rect(rx, yB - 6, W - rx - 40, BH + 34, "#fcfcfc", FAINT, 1.4, 8)
    s += text(rx + 14, yB + 16, "Стратегії вибору:", 12.5, INK, "start", "bold")
    rules = [
        "first-fit — перший, що влазить (швидко)",
        "best-fit — найтісніший (менше марнує)",
        "лишок < порога → не ділимо, віддаємо цілим",
    ]
    for j, r in enumerate(rules):
        s += text(rx + 14, yB + 34 + j * 17, "• " + r, 11, INK, "start")

    save("fig-19-6a-2-firstfit.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.6a.3 — free + злиття сусідів (coalescing): три стани
#   (а) до free; (б) блок звільнено, але дроблено; (в) після злиття — суцільний
# ════════════════════════════════════════════════════════════════════════════
def fig_coalesce():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 32, "Повернення + злиття сусідніх вільних блоків (coalescing)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 54, "free сам по собі лишає дрібні уламки; ліки — одразу зливати щойно звільнений блок із вільними сусідами",
              12, GREY, "middle", style="italic")

    x0 = 70
    BH = 62
    # три горизонтальні стрічки (стани), кожна — одна й та сама ділянка пам'яті
    def strip(y, label, parts, braces=None):
        s2 = text(x0, y - 12, label, 13.5, INK, "start", "bold")
        xs = []
        x = x0
        for kind, w, sz, lab in parts:
            xs.append(x); x += w
        for i, (kind, w, sz, lab) in enumerate(parts):
            s2 += mem_block(xs[i], y, w, BH, kind, f"{sz}", lab)
        return s2, xs, x

    # (а) ДО: вільний 24 — зайнятий 32 (його зараз звільнять) — вільний 40
    yA = 100
    partsA = [
        ("free", 130, "size 24", "ВІЛЬНО"),
        ("used", 150, "size 32", "звільняємо"),
        ("free", 180, "size 40", "ВІЛЬНО"),
    ]
    sA, xsA, endA = strip(yA, "(а) ДО free: посередині зайнятий блок, обабіч — два вільні сусіди", partsA)
    s += sA
    # позначка free(p) на середній блок
    s += arrow(xsA[1] + 75, yA - 30, xsA[1] + 75, yA - 2, RED, 2)
    s += text(xsA[1] + 75, yA - 36, "free(p)", 12.5, RED, "middle", "bold")

    # (б) НАЇВНО: середній став вільним, але це три ОКРЕМІ дрібні вільні блоки
    yB = 250
    partsB = [
        ("free", 130, "size 24", "вільний"),
        ("free", 150, "size 32", "вільний"),
        ("free", 180, "size 40", "вільний"),
    ]
    sB, xsB, endB = strip(yB, "(б) НАЇВНО (без злиття): три окремі вільні блоки — фрагментація, великий запит не влазить", partsB)
    s += sB
    # дужка «3 уламки»
    s += text((x0 + endB) / 2, yB + BH + 22, "24 + 32 + 40 = 96 Б вільно, але порізано на 3 шматки",
              12, RED, "middle", "bold")

    # перехід (б)→(в)
    s += arrow(W / 2, yB + BH + 34, W / 2, yB + BH + 64, GREEN, 2.6)
    s += text(W / 2 + 12, yB + BH + 56, "злиття сусідів (coalesce)", 12.5, GREEN, "start", "bold")

    # (в) ПІСЛЯ ЗЛИТТЯ: один суцільний вільний блок
    yC = 420
    # сумарна ширина = сума трьох (приблизно), мінус два «зниклі» заголовки — для образу
    wC = 130 + 150 + 180
    sC = text(x0, yC - 12, "(в) ПІСЛЯ злиття: один суцільний вільний блок — і зайві заголовки зникли", 13.5, INK, "start", "bold")
    sC += mem_block(x0, yC, wC, BH, "free", "size 96+", "ОДИН ВЕЛИКИЙ ВІЛЬНИЙ БЛОК")
    s += sC
    s += text(x0 + wC / 2, yC + BH + 22, "тепер великий запит знову влазить; фрагментацію відкотили",
              12, GREEN, "middle", "bold")

    # права нота: як знаходять сусідів (boundary tags)
    nx, ny = end_x = x0 + wC + 28, yC - 8
    s += rect(nx, ny, W - nx - 36, BH + 40, "#fff7e8", AMBER, 1.4, 8)
    s += text(nx + 12, ny + 18, "Як знайти сусіда:", 12, INK, "start", "bold")
    for j, t in enumerate([
        "наступний — поряд: адреса+розмір",
        "попередній — «граничні мітки»",
        "(boundary tags, Knuth): розмір",
        "дублюється і в кінці блоку",
    ]):
        s += text(nx + 12, ny + 34 + j * 15, t, 10.5, INK, "start")

    save("fig-19-6a-3-coalesce.svg", s)


if __name__ == "__main__":
    fig_anatomy()
    fig_firstfit()
    fig_coalesce()
    print("ch19 §3.6.6a insert figures done.")
