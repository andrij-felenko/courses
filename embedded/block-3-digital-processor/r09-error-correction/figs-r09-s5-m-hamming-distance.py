# -*- coding: utf-8 -*-
"""
Фігури до 🧮-вставки §3.9.5m — «Відстань Геммінга формально: кулі, межі, ціна надлишковості».
Окремий скрипт (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; червоний — акцент / «спіймано» / помилка,
синій — нейтральні дані / кодові слова, зелене — результат / висновок,
бурштин — те, на що дивимось. Шрифт sans-serif.
Нумерація підписів — за темою-вставкою «Рис. 3.9.5m.k».
Імена SVG містять суфікс s5m, щоб не змішуватися з рисунками тем розділу.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (єдина з figs.py розділу) ───────────────────────────────────────
RED   = "#c0271e"   # акцент / помилка / межа
BLUE  = "#1f47b5"   # нейтральні дані / кодові слова
GREEN = "#1f8a3b"   # результат / висновок / «ок»
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"   # на що дивимось
PALE_R = "#fbeceb"
PALE_B = "#eef2fb"
PALE_G = "#eef7f0"
PALE_A = "#faf3e0"
MONO  = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="mInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="mRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="mGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="mBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = {GREEN: "mGreen", RED: "mRed", BLUE: "mBlue"}.get(color, "mInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def circ(cx, cy, r, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def cell(x, y, w, h, s, fill="none", stroke=FAINT, sw=1.4, rx=4,
         tcol=INK, size=14, weight="bold", mono=True):
    out = rect(x, y, w, h, fill, stroke, sw, rx)
    out += text(x + w / 2, y + h * 0.64, s, size, tcol, "middle", weight, mono=mono)
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def hamming(a, b):
    """Відстань Геммінга між двома бітовими рядками рівної довжини."""
    return sum(1 for x, y in zip(a, b) if x != y)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.5m.1 — Відстань Геммінга як геометрія: куб усіх 3-бітних слів,
# ребро = одна зміна біта, відстань = найкоротший шлях ребрами. Показуємо,
# що d(010,100)=2, і що код {000,111} має мінімальну відстань 3 (через увесь куб).
# ════════════════════════════════════════════════════════════════════════════
def fig_cube():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "Відстань Геммінга — це геометрія: куб усіх слів, ребро = один біт",
              19, INK, "middle", "bold")
    s += text(W / 2, 53, "вершини — всі 3-бітні рядки; кожне ребро змінює рівно один біт; відстань = довжина найкоротшого шляху",
              12, GREY, "middle", style="italic")

    # ── проєкція 3-куба: задня й передня грані ─────────────────────────────
    # координати кодів за бітами (b2 b1 b0). Розкладаємо як квадрат + зсунутий квадрат.
    LX, LY = 120, 150          # лівий верх передньої грані
    side = 150                 # сторона квадрата
    dx, dy = 120, -86          # зсув задньої грані (псевдо-3D)

    # передня грань: b2=0 → 0xy ; задня: b2=1 → 1xy
    # у квадраті: гориз. = b0, верт. = b1 (низ b1=0, верх b1=1)
    def pos(code):
        b2, b1, b0 = int(code[0]), int(code[1]), int(code[2])
        x = LX + b0 * side + (b2 * dx)
        y = LY + (1 - b1) * side + (b2 * dy)
        return x, y

    codes = [f"{i:03b}" for i in range(8)]
    # ребра: пари, що різняться рівно одним бітом
    edges = []
    for i in range(8):
        for j in range(i + 1, 8):
            if hamming(codes[i], codes[j]) == 1:
                edges.append((codes[i], codes[j]))

    # спершу ребра (сірі), щоб вершини лягли зверху
    for a, b in edges:
        xa, ya = pos(a)
        xb, yb = pos(b)
        s += line(xa, ya, xb, yb, FAINT, 2.2)

    # підсвітимо мінімальну відстань коду {000, 111} — шлях 000→100→110→111 (3 ребра)
    path = ["000", "100", "110", "111"]
    for k in range(len(path) - 1):
        xa, ya = pos(path[k])
        xb, yb = pos(path[k + 1])
        s += line(xa, ya, xb, yb, RED, 3.4)

    # одна «двійка» для прикладу: 010 → 100 (через 000) — бурштинова дуга-пояснення
    # покажемо її окремо як підпис, без перевантаження ліній.

    # вершини
    CODE_PTS = {"000", "111"}   # кодові слова прикладу
    for c in codes:
        x, y = pos(c)
        is_word = c in CODE_PTS
        r = 21 if is_word else 17
        fill = PALE_B if is_word else "#ffffff"
        stc = BLUE if is_word else GREY
        sw = 2.6 if is_word else 1.6
        s += circ(x, y, r, fill, stc, sw)
        s += text(x, y + 5, c, 13 if is_word else 12, BLUE if is_word else INK,
                  "middle", "bold", mono=True)
    # підписи кодових слів
    x0, y0 = pos("000")
    s += text(x0 - 30, y0 + 34, "кодове слово", 11.5, BLUE, "middle", "bold")
    x1, y1 = pos("111")
    s += text(x1 + 6, y1 - 28, "кодове слово", 11.5, BLUE, "middle", "bold")

    # підпис червоного шляху
    s += text(560, 250, "d(000,111) = 3", 16, RED, "start", "bold", mono=True)
    s += text(560, 272, "(три ребра наскрізь через куб)", 12, RED, "start")

    # ── права колонка: означення відстані ─────────────────────────────────
    bx = 560
    s += rect(bx, 300, 350, 232, PALE_A, AMBER, 1.5, 12)
    s += text(bx + 175, 326, "Відстань Геммінга d(u, v)", 15, INK, "middle", "bold")
    s += text(bx + 175, 346, "(Hamming distance)", 11.5, GREY, "middle", style="italic")
    s += text(bx + 18, 374, "= кількість позицій, де u і v різні", 13, INK, "start", "bold", mono=False)
    # приклад порозрядно
    u = "1011010"
    v = "1001110"
    cw = 30
    sx = bx + 26
    sy = 398
    s += text(sx - 8, sy + 16, "u:", 12, BLUE, "end", "bold", mono=True)
    s += text(sx - 8, sy + 44, "v:", 12, BLUE, "end", "bold", mono=True)
    diff = 0
    for i in range(len(u)):
        cx = sx + i * cw
        differ = u[i] != v[i]
        if differ:
            s += rect(cx - 2, sy + 2, cw - 4, 56, PALE_R, RED, 1.4, 4)
            diff += 1
        s += text(cx + cw / 2 - 4, sy + 16, u[i], 14, INK, "middle", "bold", mono=True)
        s += text(cx + cw / 2 - 4, sy + 44, v[i], 14, INK, "middle", "bold", mono=True)
        if differ:
            s += text(cx + cw / 2 - 4, sy + 74, "↕", 13, RED, "middle", "bold")
    s += text(bx + 18, sy + 102, f"різних позицій: {diff}  ⇒  d(u, v) = {diff}",
              13.5, RED, "start", "bold", mono=False)

    save("fig-r09-s5m-1-cube.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.5m.2 — Кулі декодування й дві межі. Два кодові слова на відстані d;
# навколо кожного — куля радіуса t. Виявлення = d−1, виправлення = ⌊(d−1)/2⌋.
# Показуємо три випадки d=3, d=4, і чому кулі не мають перетинатися.
# ════════════════════════════════════════════════════════════════════════════
def fig_spheres():
    W, H = 940, 688
    s = header(W, H)
    s += text(W / 2, 32, "Кулі декодування: скільки помилок видно, а скільки виправно",
              19, INK, "middle", "bold")
    s += text(W / 2, 53, "довкола кожного кодового слова — куля радіуса t; поки кулі не злипаються, помилки до t виправні",
              12, GREY, "middle", style="italic")

    def scene(cx, label, d, t_corr, ok_corr):
        """Одна сцена: два кодові слова на відстані d, з кулями виправлення."""
        nonlocal s
        ay, by = 250, 250
        ax = cx - 150
        bx = cx + 150
        # вісь-«відстань»
        s += line(ax, ay, bx, by, INK, 2)
        # поділки відстані (d ребер)
        for k in range(d + 1):
            px = ax + (bx - ax) * k / d
            s += line(px, ay - 6, px, ay + 6, GREY, 1.4)
        s += text(cx, ay + 30, f"відстань d = {d}", 13.5, INK, "middle", "bold", mono=False)

        # кулі виправлення радіуса t навколо кожного слова
        rr = (bx - ax) * t_corr / d
        col = GREEN if ok_corr else RED
        pale = PALE_G if ok_corr else PALE_R
        if rr > 0:
            s += circ(ax, ay, rr, pale, col, 2, dash="6 4")
            s += circ(bx, by, rr, pale, col, 2, dash="6 4")
        # кодові слова
        for px in (ax, bx):
            s += circ(px, ay, 13, PALE_B, BLUE, 2.4)
        s += text(ax, ay + 4, "A", 13, BLUE, "middle", "bold")
        s += text(bx, by + 4, "B", 13, BLUE, "middle", "bold")
        s += text(cx, ay - 78, label, 14, INK, "middle", "bold")
        # підпис радіуса
        if rr > 0:
            s += arrow(ax, ay - 4, ax + rr, ay - 4, col, 1.8)
            s += text(ax + rr / 2, ay - 12, f"t={t_corr}", 11.5, col, "middle", "bold", mono=True)
        # вердикт
        if ok_corr:
            s += text(cx, ay + 64, "кулі не торкаються →", 11.5, GREEN, "middle", "bold")
            s += text(cx, ay + 80, "1 помилку видно й виправно", 11.5, GREEN, "middle", "bold")
        else:
            s += text(cx, ay + 64, "кулі стикаються →", 11.5, RED, "middle", "bold")
            s += text(cx, ay + 80, "виправити не можна", 11.5, RED, "middle", "bold")

    # d=2: кулі радіуса 0 «торкаються» сусіднім словом — виправлення немає, лише виявлення
    scene(250, "d = 2: лише виявлення (1 біт)", 2, 0, False)
    # d=3: t=1 — одна помилка виправна, кулі ще не злиплись
    scene(680, "d = 3: виявлення 2, виправлення 1", 3, 1, True)

    # ── нижня панель: формули двох меж ────────────────────────────────────
    py = 360
    s += rect(60, py, W - 120, 150, "#ffffff", INK, 1.6, 12)
    s += text(W / 2, py + 30, "Дві межі через мінімальну відстань d_min",
              16, INK, "middle", "bold")
    # ліворуч — виявлення
    s += rect(90, py + 50, 370, 78, PALE_A, AMBER, 1.4, 10)
    s += text(275, py + 76, "ВИЯВЛЕННЯ (detect)", 13.5, INK, "middle", "bold")
    s += text(275, py + 102, "помилок ловимо до:  d_min − 1", 15, INK, "middle", "bold", mono=True)
    s += text(275, py + 120, "(будь-яка зміна < d не дотягне до іншого слова)", 10.5, GREY, "middle")
    # праворуч — виправлення
    s += rect(480, py + 50, 370, 78, PALE_G, GREEN, 1.4, 10)
    s += text(665, py + 76, "ВИПРАВЛЕННЯ (correct)", 13.5, INK, "middle", "bold")
    s += text(665, py + 102, "помилок чинимо до:  t = ⌊(d_min − 1) / 2⌋", 15, GREEN, "middle", "bold", mono=True)
    s += text(665, py + 120, "(куля радіуса t навколо кожного слова не перетинає сусідню)", 10.5, GREY, "middle")

    # рядок-таблиця d → виявлення/виправлення
    ty = py + 168
    s += text(W / 2, ty, "Як це читати для типових d:", 13, INK, "middle", "bold")
    cols = ["d_min", "виявляє", "виправляє t", "приклад коду"]
    rows = [
        ["1", "0", "0", "без захисту"],
        ["2", "1", "0", "біт парності (§3.9.2)"],
        ["3", "2", "1", "Геммінг (7,4) (§3.9.6)"],
        ["4", "3", "1", "SECDED — §3.9.7"],
    ]
    cw = [120, 150, 170, 320]
    tx0 = (W - sum(cw)) / 2
    hy = ty + 14
    cx = tx0
    for w, hd in zip(cw, cols):
        s += rect(cx, hy, w, 26, PALE_B, BLUE, 1.3, 5)
        s += text(cx + w / 2, hy + 18, hd, 12, INK, "middle", "bold", mono=False)
        cx += w
    for i, rrow in enumerate(rows):
        ry = hy + 26 + i * 24
        cx = tx0
        for j, (w, v) in enumerate(zip(cw, rrow)):
            hi = (rrow[0] == "3")
            s += rect(cx, ry, w, 24, PALE_A if hi else "#ffffff", AMBER if hi else FAINT, 1.2, 4)
            col = GREEN if (j == 2 and v != "0") else (RED if (j == 2 and v == "0") else INK)
            s += text(cx + w / 2, ry + 17, v, 12, col, "middle",
                      "bold" if j < 3 else "normal", mono=(j < 3))
            cx += w

    save("fig-r09-s5m-2-spheres.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.9.5m.3 — Ціна надлишковості: дві межі-стелі. Зліва — пакування куль
# (Геммінгова межа): кулі радіуса t не повинні перекриватися, тож їх «об'єм»
# не вміщається понад 2ⁿ. Справа — таблиця: щоб підняти d, треба додавати біти
# (падає швидкість коду R = k/n).
# ════════════════════════════════════════════════════════════════════════════
def fig_cost():
    W, H = 940, 580
    s = header(W, H)
    s += text(W / 2, 32, "Ціна надлишковості: за більшу відстань платять бітами",
              19, INK, "middle", "bold")
    s += text(W / 2, 53, "кулі декодування мусять уміститися в просторі 2ⁿ слів — звідси стеля на d при заданих n і k",
              12, GREY, "middle", style="italic")

    # ── ліворуч: пакування куль у простір 2ⁿ слів ─────────────────────────
    bx0, by0 = 70, 90
    bw, bh = 380, 300
    s += rect(bx0, by0, bw, bh, "#fcfcff", BLUE, 1.6, 12)
    s += text(bx0 + bw / 2, by0 + 24, "Простір усіх слів: 2ⁿ точок", 14, INK, "middle", "bold")
    s += text(bx0 + bw / 2, by0 + 42, "(кожне слово — точка n-куба)", 11, GREY, "middle", style="italic")
    # розкидані кодові слова з не-перекривними кулями
    centers = [
        (135, 150), (250, 135), (360, 175),
        (150, 250), (270, 235), (385, 285),
        (115, 330), (250, 330), (360, 360),
    ]
    rr = 40
    for (cx, cy) in centers:
        s += circ(cx, cy, rr, PALE_G, GREEN, 1.6, dash="5 4")
    for (cx, cy) in centers:
        s += circ(cx, cy, 7, PALE_B, BLUE, 2.2)
    # підпис однієї кулі
    cx, cy = centers[4]
    s += arrow(cx, cy, cx + rr * 0.92, cy - rr * 0.38, AMBER, 1.8)
    s += text(cx + 30, cy - 26, "куля радіуса t", 11.5, AMBER, "start", "bold")
    s += text(cx + 30, cy - 12, "(виправні слова)", 10.5, AMBER, "start")
    s += text(centers[0][0] - 6, centers[0][1] + 4, "•", 12, BLUE, "middle", "bold")
    s += text(bx0 + bw / 2, by0 + bh - 12,
              "Кулі не перекриваються — інакше слово впало б у дві відразу",
              11, GREEN, "middle", "bold")
    # формула-стеля під картинкою
    s += rect(bx0, by0 + bh + 14, bw, 78, PALE_A, AMBER, 1.4, 10)
    s += text(bx0 + bw / 2, by0 + bh + 38, "Межа пакування куль (Геммінгова межа):",
              12.5, INK, "middle", "bold")
    s += text(bx0 + bw / 2, by0 + bh + 62,
              "2ᵏ · V(n, t)  ≤  2ⁿ", 16, INK, "middle", "bold", mono=True)
    s += text(bx0 + bw / 2, by0 + bh + 80,
              "(число слів × об'єм кулі вміщається в простір)", 10.5, GREY, "middle")

    # ── праворуч: таблиця ціни — як росте n при сталому k=4, щоб підняти d ──
    tx0, ty0 = 500, 90
    s += text(tx0, ty0 + 4, "Ціна за відстань (даних k = 4 біти):", 14, INK, "start", "bold")
    cols = ["d_min", "всього n", "надлишок\nn−k", "швидкість\nR = k/n", "виправляє"]
    cw = [80, 90, 95, 110, 95]
    rows = [
        ["1", "4", "0", "1.00", "0"],
        ["2", "5", "1", "0.80", "0"],
        ["3", "7", "3", "0.57", "1"],
        ["4", "8", "4", "0.50", "1"],
    ]
    hy = ty0 + 18
    cx = tx0
    for w, hd in zip(cw, cols):
        s += rect(cx, hy, w, 46, PALE_B, BLUE, 1.3, 5)
        for k, part in enumerate(hd.split("\n")):
            s += text(cx + w / 2, hy + 19 + k * 15, part, 11, INK, "middle", "bold", mono=False)
        cx += w
    for i, rrow in enumerate(rows):
        ry = hy + 46 + i * 40
        cx = tx0
        hi = (rrow[0] == "3")
        for j, (w, v) in enumerate(zip(cw, rrow)):
            s += rect(cx, ry, w, 40, PALE_A if hi else "#ffffff", AMBER if hi else FAINT, 1.2, 4)
            col = INK
            if j == 3:
                col = RED        # швидкість падає
            if j == 4 and v != "0":
                col = GREEN
            s += text(cx + w / 2, ry + 25, v, 13, col, "middle", "bold", mono=True)
            cx += w
    # стрілка «надлишок росте / швидкість падає»
    ay = hy + 46
    s += arrow(tx0 + sum(cw) + 16, ay + 6, tx0 + sum(cw) + 16, ay + 150, RED, 2)
    s += text(tx0 + sum(cw) + 22, ay + 70, "більше d", 11, RED, "start", "bold")
    s += text(tx0 + sum(cw) + 22, ay + 86, "→ більше біт", 11, RED, "start", "bold")
    s += text(tx0 + sum(cw) + 22, ay + 102, "→ нижча", 11, RED, "start", "bold")
    s += text(tx0 + sum(cw) + 22, ay + 118, "    швидкість", 11, RED, "start", "bold")

    # нижній висновок праворуч
    s += rect(tx0, hy + 46 + len(rows) * 40 + 18, 410, 96, PALE_G, GREEN, 1.5, 10)
    s += text(tx0 + 205, hy + 46 + len(rows) * 40 + 42,
              "Безкоштовного захисту не буває.", 13.5, INK, "middle", "bold")
    s += text(tx0 + 16, hy + 46 + len(rows) * 40 + 66,
              "Кожен крок d угору з'їдає швидкість R: біти", 11.5, INK, "start", mono=False)
    s += text(tx0 + 16, hy + 46 + len(rows) * 40 + 84,
              "коду йдуть на контроль, а не на корисні дані.", 11.5, INK, "start", mono=False)
    # нижня стрічка
    s += rect(60, H - 36, W - 120, 26, PALE_R, RED, 1.4, 8)
    s += text(W / 2, H - 18,
              "Сінглтонова межа ставить інший бік стелі: d_min ≤ n − k + 1 — більше d вимагає більше надлишку n−k.",
              11.5, INK, "middle", "bold")
    save("fig-r09-s5m-3-cost.svg", s)


if __name__ == "__main__":
    fig_cube()
    fig_spheres()
    fig_cost()
    print("r09-s5m (hamming-distance) figures done.")
