# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Послідовності де Брейна».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

HL   = "#fde3b3"   # підсвітка вікна
HL2  = "#cfe8d6"   # м'яка зелена підсвітка
VERT = "#eef2fb"   # заливка вершини


# ── Фігура 1: означення — кільце з усіма вікнами ─────────────────────────────
# Що таке послідовність де Брейна на найменшому прикладі B(2,3)=00010111.
# Вгорі — стрічка з восьми бітів плюс два бліді символи-обгортання (початок,
# підклеєний через стик). Нижче — сходинка з восьми положень ковзного вікна
# завширшки три; кожне читає свою двійкову трійку, і всі вісім трійок різні.
# Головна думка: вісім символів несуть те, на що нарізно пішло б 8×3=24.
def fig_window():
    W, H = 940, 500
    parts = []
    bits = [0, 0, 0, 1, 0, 1, 1, 1]
    ext = bits + bits[:2]                    # +2 символи обгортання
    cw, ch = 56, 50
    x0, ytop = 180, 78

    # стрічка
    for i, b in enumerate(ext):
        x = x0 + i * cw
        wrap = i >= 8
        parts.append(rect(x, ytop, cw, ch,
                          fill="#f7f9fb" if wrap else BG,
                          stroke="#c9d2db" if wrap else INK,
                          sw=1.4, rx=4))
        parts.append(text(x + cw / 2, ytop + ch / 2 + 8, str(b),
                          size=22, bold=not wrap,
                          color=MUTED if wrap else INK))
    # стик
    xs = x0 + 8 * cw
    parts.append(line(xs, ytop - 12, xs, ytop + ch + 12, color=POS, sw=1.6, dash="4 3"))
    parts.append(text(xs + 2 * cw / 2, ytop - 20, "стик: кінець ↔ початок",
                      size=11, color=POS))
    parts.append(text(x0 - 12, ytop + ch / 2 + 5, "кільце:", size=12,
                      color=MUTED, anchor="end"))

    # сходинка вікон
    triples = ["000", "001", "010", "101", "011", "111", "110", "100"]
    yb0, bh, step = ytop + ch + 28, 26, 32
    for i, tri in enumerate(triples):
        x = x0 + i * cw
        y = yb0 + i * step
        parts.append(rect(x, y, 3 * cw, bh, fill=HL, stroke="#e0a94a", sw=1.3, rx=4))
        parts.append(text(x + 3 * cw / 2, y + bh / 2 + 5,
                          "позиція %d  →  %s" % (i, tri), size=13, bold=True))

    parts.append(fitbox(90, H - 52, W - 180, 40,
                 "Вісім положень вікна — усі вісім трійок, кожна рівно раз. Вісім символів у кільці\n"
                 "несуть те, на що виписаними нарізно пішло б 8×3 = 24 символи.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/window.svg", W, H, *parts,
           title="Послідовність де Брейна B(2,3): усі вісім трійок в одному кільці")


# ── Фігура 2: серце теми — граф де Брейна й ейлерів цикл ──────────────────────
# Головний поворот: слова стають РЕБРАМИ графа, а вершинами — їхні (n-1)-літерні
# перекриття. Для n=3: 4 вершини (двобітові слова), 8 ребер (трибітові). Ребро
# abc веде від префікса ab до суфікса bc. У кожної вершини вхідний степінь = 2 =
# вихідному (збалансована), граф зв'язний — тому ейлерів цикл (кожне ребро раз)
# існує, і його написи дають послідовність де Брейна.
def fig_graph():
    W, H = 900, 600
    r = 36
    N = {"00": (250, 175), "01": (650, 175), "10": (250, 445), "11": (650, 445)}
    parts = []

    def path_arrow(d, color=INK, sw=2.6):
        return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'marker-end="url(#arrow)"/>' % (d, color, sw))

    def lbl(cx, cy, s):
        return textbox(cx, cy, s, size=13, pad=5, fill=BG, stroke="none",
                       sw=0, bold=True, color="#8a5a12")[0]

    def darrow(a, b, bend, label):
        ax, ay = N[a]; bx, by = N[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        mx, my = (ax + bx) / 2, (ay + by) / 2
        cx, cy = mx + nx * bend, my + ny * bend
        # обрізаємо до меж вершин (у бік контрольної точки)
        s1x, s1y = cx - ax, cy - ay
        d1 = math.hypot(s1x, s1y) or 1
        sx, sy = ax + s1x / d1 * r, ay + s1y / d1 * r
        s2x, s2y = cx - bx, cy - by
        d2 = math.hypot(s2x, s2y) or 1
        ex, ey = bx + s2x / d2 * r, by + s2y / d2 * r
        out = path_arrow("M %.1f %.1f Q %.1f %.1f %.1f %.1f" % (sx, sy, cx, cy, ex, ey))
        lx, ly = mx + nx * (bend + math.copysign(20, bend)), my + ny * (bend + math.copysign(20, bend))
        return out + lbl(lx, ly, label)

    def selfloop(a, theta_deg, label):
        x, y = N[a]
        th = math.radians(theta_deg)
        Lp = 48
        a1, a2 = th - 0.40, th + 0.40
        sx, sy = x + r * math.cos(a1), y + r * math.sin(a1)
        ex, ey = x + r * math.cos(a2), y + r * math.sin(a2)
        c1x, c1y = x + (r + Lp) * math.cos(a1), y + (r + Lp) * math.sin(a1)
        c2x, c2y = x + (r + Lp) * math.cos(a2), y + (r + Lp) * math.sin(a2)
        out = path_arrow("M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f"
                         % (sx, sy, c1x, c1y, c2x, c2y, ex, ey))
        lx, ly = x + (r + Lp + 20) * math.cos(th), y + (r + Lp + 22) * math.sin(th)
        return out + lbl(lx, ly, label)

    # чотири сторони квадрата (кожна вигинається назовні) — напрямлений обхід
    parts.append(darrow("00", "01", -38, "001"))   # верх
    parts.append(darrow("01", "11", -38, "011"))   # право
    parts.append(darrow("11", "10", -38, "110"))   # низ
    parts.append(darrow("10", "00", -38, "100"))   # ліво
    # дві діагоналі 01↔10 — розведені в різні боки
    parts.append(darrow("01", "10", 74, "010"))
    parts.append(darrow("10", "01", 74, "101"))
    # петлі
    parts.append(selfloop("00", 225, "000"))
    parts.append(selfloop("11", 45, "111"))

    # вершини
    for name, (x, y) in N.items():
        parts.append(circle(x, y, r, fill=VERT, stroke=NEG, sw=2.4))
        parts.append(text(x, y + 6, name, size=18, bold=True))

    parts.append(fitbox(90, H - 66, W - 180, 46,
                 "Ребро abc = слово, веде від префікса ab до суфікса bc. У кожній вершині 2 входять і 2 виходять (збалансована), граф зв'язний —\n"
                 "тому маршрут через усі 8 ребер по разу (ейлерів цикл) існує; його написи й дають послідовність де Брейна.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/graph.svg", W, H, *parts,
           title="Граф де Брейна B(2,3): слова — це ребра, а не вершини")


# ── Фігура 3: застосування — позиція біта через послідовність де Брейна ───────
# Найпряміший приклад, де «усі вікна різні» стає швидким кодом. Ізолюємо
# наймолодший біт (x&−x = 2^p), множимо на 32-бітову константу-послідовність
# (це зсув на p), беремо старші 5 бітів (унікальне вікно) і через табличку
# дістаємо саму позицію p. Приклад: наймолодший біт на позиції 3.
def fig_ctz():
    W, H = 1000, 400
    parts = []
    stages = [
        ("вхід  x", "…0010 1000", "наймолодша 1 — поз. 3"),
        ("x & (−x)", "0x0000 0008", "лишився один біт = 2³"),
        ("× 0x077CB531", "0x3BE5 A988", "множення = зсув на 3"),
        (">> 27", "7", "старші 5 бітів = вікно"),
        ("table[7]", "3", "вікно → позиція"),
    ]
    bw, bh, gap = 172, 118, 15
    total = len(stages) * bw + (len(stages) - 1) * gap
    x0 = (W - total) / 2
    ytop = 96
    for i, (title, val, note) in enumerate(stages):
        x = x0 + i * (bw + gap)
        last = i == len(stages) - 1
        parts.append(rect(x, ytop, bw, bh,
                          fill="#eef7f0" if last else FILL,
                          stroke=FIELD if last else NEG, sw=2.2 if last else 1.8))
        parts.append(text(x + bw / 2, ytop + 26, title, size=13.5, bold=True,
                          color=(FIELD if last else INK)))
        parts.append(line(x + 14, ytop + 38, x + bw - 14, ytop + 38,
                          color="#d6dde4", sw=1))
        parts.append(text(x + bw / 2, ytop + 68, val, size=16, bold=True,
                          color=(POS if not last else FIELD)))
        parts.append(fitbox(x + 8, ytop + 84, bw - 16, 26, note, size=10.5,
                           fill=BG, stroke="none", sw=0, color=MUTED))
        if i:
            xa = x - gap - 2
            parts.append(arrow(xa - 9, ytop + bh / 2, x + 2, ytop + bh / 2,
                              color=INK, sw=2.2))

    parts.append(fitbox(x0, ytop + bh + 40, total, 40,
                 "Усі 32 п'ятибітові вікна константи 0x077CB531 різні — тому старші 5 бітів однозначно кажуть позицію,\n"
                 "а табличку з вікна в позицію заготовляють заздалегідь. Три дії й одне звертання до пам'яті, без циклів.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/ctz.svg", W, H, *parts,
           title="Позиція біта за три команди: множення на послідовність де Брейна")


# ── Фігура 4 (до вставки math-counting): дві арборесценції dB(2,3) ────────────
# Серце підрахунку: теорема BEST зводить число кілець до числа арборесценцій —
# остовних дерев, усі ребра яких дивляться в корінь. Для dB(2,3) із коренем 00
# таких дерев рівно ДВА, і саме тому B(2,3)=2. Кожна панель показує 4 вершини й
# три деревні ребра (кожна не-коренева вершина віддає рівно одне ребро в бік
# кореня); корінь 00 підсвічено зеленим. Різняться панелі лише вибором ребра з
# вершини 01: 01→10 проти 01→11.
def fig_arbor():
    W, H = 980, 560
    r = 32
    parts = []
    green_fill = "#cfe8d6"

    def panel(ox, oy, title, e01):
        V = {"00": (ox + 60, oy + 60), "01": (ox + 320, oy + 60),
             "10": (ox + 60, oy + 320), "11": (ox + 320, oy + 320)}
        out = []
        # деревні ребра (a→b) з ручним зсувом підпису-слова
        edges = [(e01[0], e01[1], e01[2]),
                 ("11", "10", (0, 30)),
                 ("10", "00", (-30, 0))]
        for a, b, off in edges:
            ax, ay = V[a]; bx, by = V[b]
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            sx, sy = ax + ux * r, ay + uy * r
            ex, ey = bx - ux * r, by - uy * r
            out.append(arrow(sx, sy, ex, ey, color=FIELD, sw=3.0))
            word = a + b[-1]                     # напис ребра = слово довжини 3
            mx, my = (ax + bx) / 2, (ay + by) / 2
            out.append(text(mx + off[0], my + off[1] + 4, word,
                            size=12, color=MUTED, bold=True))
        # вершини (корінь виділено)
        for name, (x, y) in V.items():
            root = name == "00"
            out.append(circle(x, y, r, fill=green_fill if root else VERT,
                              stroke=FIELD if root else NEG, sw=2.8 if root else 2.2))
            out.append(text(x, y + 6, name, size=17, bold=True))
        rx, ry = V["00"]
        out.append(text(rx, ry - r - 12, "корінь", size=11, color=FIELD, bold=True))
        out.append(text(ox + 190, oy - 16, title, size=14, bold=True))
        return out

    parts += panel(50, 120, "дерево 1:  ребро 01→10", ("01", "10", (-30, -8)))
    parts += panel(540, 120, "дерево 2:  ребро 01→11", ("01", "11", (26, 0)))

    # роздільник
    parts.append(line(505, 108, 505, 470, color="#d6dde4", sw=1.4, dash="5 4"))

    parts.append(fitbox(70, H - 66, W - 140, 46,
                 "Кожна не-коренева вершина віддає рівно одне ребро в бік кореня 00 — виходить остовне дерево-арборесценція. Вибір вільний лише у вершини 01\n"
                 "(→10 чи →11), тож дерев рівно два: tw = 2. Стільки ж, скільки й кілець, — і справді B(2,3) = 2.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/arbor.svg", W, H, *parts,
           title="Дві арборесценції графа dB(2,3) — і тому дві послідовності")


# ── Фігура 5 (вставка proj-construct): три способи → два кільця ───────────────
# Головна думка розбору побудови: три різні алгоритми (FKM, Гірхольцер,
# жадібний «найбільший») на B(2,3) видають лише ДВА різні кільця. FKM і
# Гірхольцер лягають на одне й те саме кільце 00010111 (різняться тільки точкою
# старту — Гірхольцер починає на 2 позиції далі), а жадібний дає дзеркальне
# 00011101. Більше двох не буває — стільки й дає формула підрахунку (=2).
def fig_three():
    W, H = 940, 560
    R, nr = 104, 18
    parts = []

    def ring(cx, cy, bits, starts):
        frag = []
        # напрямна лінія кільця + стрілка напряму читання (за годинниковою)
        frag.append(circle(cx, cy, R, fill="none", stroke="#d6dde4", sw=1.4))
        a1, a2 = math.radians(-104), math.radians(-64)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        x2, y2 = cx + R * math.cos(a2), cy + R * math.sin(a2)
        frag.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                    'fill="none" stroke="%s" stroke-width="2" '
                    'marker-end="url(#arrow)"/>' % (x1, y1, R, R, x2, y2, MUTED))
        # підсвітка стартових вузлів (кольорове кільце навколо)
        for i, col in starts.items():
            th = math.radians(-90 + 45 * i)
            x, y = cx + R * math.cos(th), cy + R * math.sin(th)
            frag.append(circle(x, y, nr + 5, fill="none", stroke=col, sw=3.2))
        # вузли-біти
        for i, b in enumerate(bits):
            th = math.radians(-90 + 45 * i)
            x, y = cx + R * math.cos(th), cy + R * math.sin(th)
            frag.append(circle(x, y, nr, fill=VERT, stroke=NEG, sw=2))
            frag.append(text(x, y + 6, str(b), size=17, bold=True))
        return frag

    cxA, cyA = 258, 250
    cxB, cyB = 682, 250
    bitsA = [0, 0, 0, 1, 0, 1, 1, 1]   # 00010111
    bitsB = [0, 0, 0, 1, 1, 1, 0, 1]   # 00011101

    parts += ring(cxA, cyA, bitsA, {0: FIELD, 2: NEG})
    parts += ring(cxB, cyB, bitsB, {0: POS})

    # мітки стартів (кольорові теги поза кільцем)
    parts.append(textbox(cxA, cyA - R - 34, "FKM — старт", size=12.5, pad=6,
                         fill="#eafaf0", stroke=FIELD, sw=2, color="#1e7a44", bold=True)[0])
    parts.append(textbox(cxA + R + 50, cyA, "Гірхольцер", size=12.5, pad=6,
                         fill="#eaf0fd", stroke=NEG, sw=2, color=NEG, bold=True)[0])
    parts.append(textbox(cxB, cyB - R - 34, "жадібний «найбільший»", size=12.5, pad=6,
                         fill="#fdeceb", stroke=POS, sw=2, color=POS, bold=True)[0])

    # підписи кілець
    parts.append(text(cxA, cyA + R + 46, "кільце  00010111", size=15, bold=True))
    parts.append(text(cxA, cyA + R + 68,
                     "FKM і Гірхольцер — те саме кільце, старт зсунуто на 2",
                     size=11.5, color=MUTED))
    parts.append(text(cxB, cyB + R + 46, "кільце  00011101", size=15, bold=True))
    parts.append(text(cxB, cyB + R + 68, "дзеркальне до сусіднього", size=11.5, color=MUTED))

    parts.append(fitbox(90, H - 62, W - 180, 44,
                 "Три способи побудови — але з точністю до обертання лише ДВА різні кільця B(2,3).\n"
                 "Рівно стільки, скільки дає формула числа послідовностей: (k!)^(k^(n−1)) / k^n = 2.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/three-methods.svg", W, H, *parts,
           title="Три алгоритми побудови — дві різні послідовності B(2,3)")


# ── Фігура 6 (вставка hist-de-bruijn): санскритський мнемонік як B(2,3) ───────
# Рядок yamātārājabhānasalagām: 10 складів, кожен легкий (л) чи важкий (в).
# Вісім ковзних вікон завширшки три дають усі вісім стоп-ґан, кожну рівно раз —
# тобто послідовність де Брейна B(2,3), виписану в рядок. Останні два склади
# (la, gaṃ) — «хвіст», що дочитує вікна через стик (n−1=2 зайві символи).
def fig_sanskrit():
    W, H = 980, 560
    parts = []
    syl = ["ya", "mā", "tā", "rā", "ja", "bhā", "na", "sa", "la", "gaṃ"]
    wt  = ["л",  "в",  "в",  "в",  "л",  "в",   "л",  "л",  "л",  "в"]
    cw, ch = 72, 58
    x0, ytop = 150, 82

    # стрічка складів
    for i, (s, w) in enumerate(zip(syl, wt)):
        x = x0 + i * cw
        tail = i >= 8
        heavy = (w == "в")
        parts.append(rect(x, ytop, cw, ch,
                          fill="#f7f9fb" if tail else BG,
                          stroke="#c9d2db" if tail else INK, sw=1.4, rx=5))
        parts.append(text(x + cw / 2, ytop + 24, s, size=19, bold=not tail,
                          color=MUTED if tail else INK))
        parts.append(text(x + cw / 2, ytop + 47, w, size=14, bold=True,
                          color=(MUTED if tail else (POS if heavy else NEG))))
    parts.append(text(x0 - 14, ytop + ch / 2 + 4, "рядок:", size=12,
                      color=MUTED, anchor="end"))
    # позначка «хвіст»
    xt = x0 + 8 * cw
    parts.append(line(xt, ytop - 10, xt, ytop + ch + 10, color=MUTED, sw=1.4, dash="4 3"))
    parts.append(text(xt + cw, ytop - 18, "хвіст: дочитує вікна", size=11, color=MUTED))

    # сходинка вікон-ґан
    ganas = [("я-ґана", "л·в·в"), ("ма-ґана", "в·в·в"), ("та-ґана", "в·в·л"),
             ("ра-ґана", "в·л·в"), ("джа-ґана", "л·в·л"), ("бга-ґана", "в·л·л"),
             ("на-ґана", "л·л·л"), ("са-ґана", "л·л·в")]
    yb0, bh, step = ytop + ch + 26, 26, 30
    for i, (nm, pat) in enumerate(ganas):
        x = x0 + i * cw
        y = yb0 + i * step
        parts.append(rect(x, y, 3 * cw, bh, fill=HL, stroke="#e0a94a", sw=1.3, rx=4))
        parts.append(text(x + 3 * cw / 2, y + bh / 2 + 5,
                          "%s   %s" % (nm, pat), size=13, bold=True))

    parts.append(fitbox(80, H - 54, W - 160, 42,
                 "Вісім вікон — вісім стоп-ґан, кожна названа першим складом; усі вісім трійок «легке/важке» різні.\n"
                 "Це послідовність де Брейна B(2,3), виписана в рядок: два склади хвоста — дочитані через стик вікна.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/hist-sanskrit.svg", W, H, *parts,
           title="Санскритський мнемонік yamātārājabhānasalagām — це B(2,3)")


# ── Фігура 7 (вставка hist-de-bruijn): часова смуга (пере)відкриттів ──────────
# Той самий об'єкт знаходили знову й знову. Вузли: Пінгала (давнина, непевно),
# друк мнемоніка 1869, доведення Флая Сент-Марі 1894, узагальнення Мартіна 1934,
# гіпотеза Постхумуса 1944 і доведення де Брейна 1946, теорема BEST 1951,
# визнання пріоритету 1975. Розрив осі між давниною і 1869 — вісь не масштабна.
def fig_timeline():
    W, H = 1240, 480
    parts = []
    yax = 250
    xL, xR = 90, W - 90
    nodes = [
        ("≈II ст. до н.е.?", ["Пінгала: перелік", "трійок складів"],         "up",   True),
        ("1869",            ["Браун друкує", "мнемонік"],                     "down", False),
        ("1894",            ["де Рів'єр питає ·", "Флай Сент-Марі доводить"], "up",   False),
        ("1934",            ["Мартін: будь-яка", "абетка"],                   "down", False),
        ("1944",            ["Постхумус: гіпотеза", "(телеком)"],             "up",   False),
        ("1946",            ["де Брейн доводить", "→ назва"],                 "down", False),
        ("1951",            ["Аарденне-Еренфест", "+ де Брейн: BEST"],        "up",   False),
        ("1975",            ["де Брейн визнає", "Флая Сент-Марі"],            "down", False),
    ]
    n = len(nodes)
    xs = [xL + (xR - xL) * i / (n - 1) for i in range(n)]

    # вісь (перший сегмент — пунктир, бо величезний розрив у часі)
    parts.append(line(xs[0], yax, xs[1], yax, color=MUTED, sw=2, dash="6 5"))
    parts.append(line(xs[1], yax, xs[-1], yax, color=INK, sw=2.2))
    # злам осі між давниною і 1869
    xb = (xs[0] + xs[1]) / 2
    parts.append(line(xb - 8, yax + 9, xb - 1, yax - 9, color=MUTED, sw=2))
    parts.append(line(xb + 1, yax + 9, xb + 8, yax - 9, color=MUTED, sw=2))

    for (yr, desc, side, uncertain), x in zip(nodes, xs):
        up = (side == "up")
        # вузол
        if uncertain:
            parts.append(circle(x, yax, 8, fill=BG, stroke=MUTED, sw=2))
            parts.append(text(x, yax + 4, "?", size=12, bold=True, color=MUTED))
        else:
            parts.append(circle(x, yax, 7, fill=FIELD, stroke=INK, sw=1.6))
        # рік — біля осі з боку опису
        parts.append(text(x, yax - 18 if up else yax + 27, yr, size=13.5, bold=True,
                          color=(MUTED if uncertain else INK)))
        # опис — далі від осі, у рамці; сполучну лінійку креслимо ПЕРЕД рамкою
        by = yax - 74 if up else yax + 74
        box, bw, bh = textbox(x, by, "\n".join(desc), size=11.5, pad=7,
                              fill=FILL, stroke="#c9d2db", sw=1.3)
        y1 = (yax - 28) if up else (yax + 36)
        y2 = (by + bh / 2) if up else (by - bh / 2)
        parts.append(line(x, y1, x, y2, color="#c9d2db", sw=1.2))
        parts.append(box)

    parts.append(fitbox(110, H - 56, W - 220, 44,
                 "Той самий об'єкт відкривали заново: мнемонік (тверда згадка 1869) · двійкова теорія 1894 ·\n"
                 "перевідкриття 1944–46 · узагальнення 1951 · визнання пріоритету 1975. Вісь не масштабна.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/hist-timeline.svg", W, H, *parts,
           title="Послідовності де Брейна: хроніка (пере)відкриттів")


# ── Фігура 8 (вставка proj-debruijn-ctz): таблиця = обернена перестановка ─────
# Головна думка вставки: 32-входова табличка CTZ не магічна — це ОБЕРНЕНА
# перестановка. Пряма мапа p → вікно w(p) = (0x077CB531·2ᵖ) >> 27 бієктивна на
# {0…31} саме тому, що всі 32 вікна різні (властивість де Брейна); табличка
# зберігає обернену стрілку table[w(p)] = p. Верхня стрічка — вікно w(p) за
# позицією p, нижня — table[w] за вікном w; нижня і є верхньою, прочитаною
# навпаки. Значення рахуємо тут-таки, не вписуючи руками.
def fig_gen():
    W, H = 1004, 372
    C, sh = 0x077CB531, 27
    win = [((C << p) & 0xFFFFFFFF) >> sh for p in range(32)]   # позиція → вікно
    table = [0] * 32
    for p in range(32):
        table[win[p]] = p                                      # вікно → позиція
    cw, ch, x0 = 27, 34, 70
    hp = 3                                                      # приклад: позиція 3…
    hw = win[hp]                                                # …дає вікно 7

    def strip(y, vals, hi):
        out = []
        for i, v in enumerate(vals):
            x = x0 + i * cw
            hit = i == hi
            out.append(rect(x, y, cw, ch, fill=HL if hit else BG,
                            stroke="#e0a94a" if hit else "#c9d2db",
                            sw=1.9 if hit else 1.2, rx=3))
            out.append(text(x + cw / 2, y + ch / 2 + 5, str(v), size=13, bold=hit))
        return out

    parts = []
    parts.append(text(x0, 58, "згори: для позиції p (0…31 зліва направо) — її 5-бітове вікно w(p)",
                      size=12.5, color=MUTED, anchor="start"))
    parts += strip(72, win, hp)

    parts.append(text(360, 196, "таблиця: за вікном w (0…31) — позиція table[w] = p",
                      size=12.5, color=MUTED, anchor="start"))
    parts += strip(210, table, hw)

    # лінійка індексів під нижньою стрічкою
    for i in list(range(0, 29, 4)) + [31]:
        parts.append(text(x0 + i * cw + cw / 2, 258, str(i), size=10.5, color=MUTED))

    # приклад-стрілка: клітинка p=3 (низ стрічки 1) → клітинка w=7 (верх стрічки 2)
    sx = x0 + hp * cw + cw / 2
    ex = x0 + hw * cw + cw / 2
    parts.append('<path d="M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                 % (sx, 106, sx, 152, ex, 162, ex, 208, POS))
    parts.append(textbox(628, 148,
                 "приклад: позиція p = 3 дає вікно w = 7,\nтож у слот 7 таблиці кладемо 3 — і table[7] = 3",
                 size=12, pad=9, fill="#fff7ec", stroke="#e0a94a", sw=1.4)[0])

    parts.append(fitbox(70, 288, W - 140, 62,
                 "У кожній стрічці числа 0…31 стоять по разу — це перестановки. Мапа «позиція → вікно» бієктивна саме тому,\n"
                 "що всі 32 вікна різні (властивість де Брейна); нижня стрічка — та сама мапа навпаки, тобто готова таблиця пошуку.",
                 size=12.5, fill=HL2, stroke=FIELD, sw=2))

    render("img/gen-table.svg", W, H, *parts,
           title="Таблиця пошуку — це обернена перестановка константи де Брейна")


if __name__ == "__main__":
    fig_window()
    fig_graph()
    fig_ctz()
    fig_arbor()
    fig_three()
    fig_sanskrit()
    fig_timeline()
    fig_gen()
    print("OK: window, graph, ctz, arbor, three-methods, hist-sanskrit, hist-timeline, gen-table")
