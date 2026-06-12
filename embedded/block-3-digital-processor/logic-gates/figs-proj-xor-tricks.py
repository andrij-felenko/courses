# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для ⚙️-вставки до теми 3.2.4 — «XOR-трюки».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-15-4a-*).
НЕ чіпає головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів у тексті — Рис. 3.2.4a.k.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
ORANGE = "#e08030"
PURPLE = "#7a3fb0"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange", PURPLE: "aPurple"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = '"Cascadia Code", "Consolas", monospace' if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family={chr(39)}{fam}{chr(39)} font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill=INK, stroke="none", sw=0, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" fill-opacity="{opacity}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# Малюнок одного 8-бітного «слова» з підсвіченими бітами.
def bitrow(x, y, bits, cell=26, highlight=None, fill_on="#fdeceb", fill_off="#ffffff",
           ink_on=RED, ink_off=INK, border=GREY, size=14):
    """bits — рядок із '0'/'1'; highlight — set індексів (зліва направо) для зеленої рамки."""
    s = ""
    hl = highlight or set()
    for i, b in enumerate(bits):
        cx = x + i * cell
        on = (b == "1")
        f = fill_on if on else fill_off
        col = ink_on if on else ink_off
        bw = 2.4 if i in hl else 1.2
        bc = GREEN if i in hl else border
        s += rect(cx, y, cell, cell, f, bc, bw, 4)
        s += text(cx + cell / 2, y + cell / 2 + size * 0.36, b, size, col, "middle", "bold", mono=True)
    return s


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.2.4a.1 — парність слова згортанням: серійний ланцюг vs паралельний фолд
# ════════════════════════════════════════════════════════════════════════════
def fig_parity_fold():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 30, "Парність слова: серійно за 31 крок  чи  паралельно за 5",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "та сама XOR-сума всіх бітів — але «складена» навпіл логарифмічно, а не пройдена біт за бітом",
              11, GREY, "middle", style="italic")

    # ── ліворуч: серійний ланцюг (як у §3.2.4) — наочно, але повільно ──
    lx = 40
    s += rect(lx, 78, 250, 250, "#fbfbff", BLUE, 1.6, 12)
    s += text(lx + 125, 102, "Серійно: біт за бітом", 13, BLUE, "middle", "bold")
    s += text(lx + 125, 122, "p = p XOR біт[i],  i = 0..31", 11, INK, "middle", mono=True)
    # стовпчик акумулятора, що повзе вниз
    word = "10110011"
    bx = lx + 36
    by = 146
    acc = 0
    s += text(bx - 14, by - 8, "p:", 11, GREY, "end", "bold")
    for i, ch in enumerate(word):
        acc ^= (ch == "1")
        yy = by + i * 18
        s += text(bx, yy, f"^ {ch}", 12, INK if ch == "0" else RED, "start", mono=True)
        s += text(bx + 64, yy, "→", 12, GREY, "middle")
        s += text(bx + 88, yy, str(acc), 12, GREEN if acc else INK, "start", "bold", mono=True)
    s += text(lx + 125, by + 8 * 18 + 4, "(8 бітів; для 32-бітного", 9.5, GREY, "middle", style="italic")
    s += text(lx + 125, by + 8 * 18 + 18, "слова — 31 XOR підряд)", 9.5, GREY, "middle", style="italic")
    s += text(lx + 125, by + 8 * 18 + 38, "довго: кроків = число бітів", 10.5, BLUE, "middle", "bold")

    # ── праворуч: паралельний фолд — половина XOR половину ──
    rx = 330
    s += rect(rx, 78, 575, 360, "#f6fbf7", GREEN, 1.8, 12)
    s += text(rx + 287, 102, "Паралельно: згортання навпіл (folding)", 13.5, GREEN, "middle", "bold")
    s += text(rx + 287, 121, "x ^= x >> 16;  x ^= x >> 8;  x ^= x >> 4 ...  — log₂N кроків", 11, INK, "middle", mono=True)

    # демонстрація фолду на 8 бітах: 8 → 4 → 2 → 1
    demo = "10110011"
    stages = []
    cur = list(demo)
    stages.append(("вихідні 8 бітів", "".join(cur)))
    # крок >>4
    a = int("".join(cur), 2)
    a ^= a >> 4
    cur = list(format(a & 0xFF, "08b"))
    stages.append(("x ^= x >> 4  (склали половини)", "".join(cur)))
    a ^= a >> 2
    cur = list(format(a & 0xFF, "08b"))
    stages.append(("x ^= x >> 2", "".join(cur)))
    a ^= a >> 1
    cur = list(format(a & 0xFF, "08b"))
    stages.append(("x ^= x >> 1", "".join(cur)))

    cell = 30
    sx = rx + 150
    sy = 150
    for k, (label, bits) in enumerate(stages):
        yy = sy + k * 62
        s += text(rx + 18, yy + cell / 2 + 4, label, 10.5, INK, "start")
        # підсвітити молодший біт на останньому кроці
        hl = {7} if k == len(stages) - 1 else None
        s += bitrow(sx, yy, bits, cell, highlight=hl, size=15)
        if k < len(stages) - 1:
            s += arrow(sx + 4 * cell, yy + cell + 4, sx + 4 * cell, yy + 62 - 4, GREY, 1.8)
    # рамка-результат
    res_y = sy + 3 * 62
    s += text(sx + 8 * cell + 16, res_y + cell / 2 + 4, "← парність у молодшому біті", 11, GREEN, "start", "bold")
    s += text(rx + 287, 418, "швидко: кроків = log₂N (для 32 біт — лише 5 XOR-зсувів, а не 31)",
              10.5, GREEN, "middle", "bold")

    # ── підсумкова стрічка внизу ──
    s += rect(40, 460, 865, 78, "#fffaf2", ORANGE, 1.6, 12)
    s += text(472, 484, "Чому це та сама відповідь", 12.5, ORANGE, "middle", "bold")
    s += text(60, 508, "XOR асоціативний і комутативний, тож суму всіх 32 бітів можна групувати як завгодно. Згортаючи слово навпіл,",
              11, INK, "start")
    s += text(60, 526, "ми XOR-имо біт i з бітом i+16, потім i з i+8 і т. д. — наприкінці молодший біт несе XOR-суму ВСІХ бітів: парність.",
              11, INK, "start")
    save("fig-15-4a-1-parity-fold.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.2.4a.2 — обмін без тимчасової змінної: три XOR і чому це працює
# ════════════════════════════════════════════════════════════════════════════
def fig_xor_swap():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 30, "Обмін двох змінних без тимчасової: три XOR поспіль",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "a ^= b;  b ^= a;  a ^= b;   — після трьох рядків a і b помінялися значеннями",
              11, GREY, "middle", style="italic", )

    # початкові значення (4 біти для наочності)
    A0 = "1100"
    B0 = "1010"
    a = int(A0, 2)
    b = int(B0, 2)

    col_a = RED
    col_b = BLUE
    cell = 34

    # колонки
    xa = 250
    xb = 560
    s += text(xa + 2 * cell, 86, "a", 16, col_a, "middle", "bold", mono=True)
    s += text(xb + 2 * cell, 86, "b", 16, col_b, "middle", "bold", mono=True)
    s += text(120, 86, "крок", 12, GREY, "middle", "bold")

    rows = []
    rows.append(("початок", format(a, "04b"), format(b, "04b")))
    # a ^= b
    a ^= b
    rows.append(("a ^= b", format(a, "04b"), format(b, "04b")))
    # b ^= a   (тепер b отримує початкове a)
    b ^= a
    rows.append(("b ^= a", format(a, "04b"), format(b, "04b")))
    # a ^= b   (a отримує початкове b)
    a ^= b
    rows.append(("a ^= b", format(a, "04b"), format(b, "04b")))

    y0 = 110
    dy = 70
    for k, (lbl, ba, bb) in enumerate(rows):
        yy = y0 + k * dy
        s += text(120, yy + cell / 2 + 4, lbl, 12, INK, "middle", "bold", mono=True)
        # підсвітка фінального рядка
        hl = set(range(4)) if k == len(rows) - 1 else None
        s += bitrow(xa, yy, ba, cell, highlight=hl, ink_on=col_a, fill_on="#fdeceb", size=16)
        s += bitrow(xb, yy, bb, cell, highlight=hl, ink_on=col_b, fill_on="#eaf0fb", size=16)
        if k < len(rows) - 1:
            s += arrow(120, yy + cell + 2, 120, yy + dy - 4, GREY, 1.6)

    # анотації справа: що несе кожна змінна на мові a0,b0
    ax = xb + 4 * cell + 26
    notes = [
        "a=a₀,  b=b₀",
        "a = a₀⊕b₀",
        "b = (a₀⊕b₀)⊕b₀ = a₀",
        "a = (a₀⊕b₀)⊕a₀ = b₀",
    ]
    ncol = [GREY, PURPLE, BLUE, RED]
    for k, (nt, nc) in enumerate(zip(notes, ncol)):
        yy = y0 + k * dy + cell / 2 + 4
        s += text(ax, yy, nt, 12.5, nc, "start", "bold", mono=True)

    # пояснювальна стрічка
    s += rect(40, 410, 865, 110, "#fffaf2", ORANGE, 1.6, 12)
    s += text(472, 434, "Чому виходить — і чим це небезпечне", 12.5, ORANGE, "middle", "bold")
    s += text(60, 458, "Ключ — самозворотність XOR:  x ⊕ y ⊕ y = x.  Друге присвоєння кладе в b комбінацію (a₀⊕b₀)⊕b₀ = a₀,",
              11, INK, "start")
    s += text(60, 476, "третє — кладе в a комбінацію (a₀⊕b₀)⊕a₀ = b₀.  Значення помінялися, тимчасова змінна не знадобилась.",
              11, INK, "start")
    s += text(60, 500, "Пастка:  якщо a і b — ОДНА Й ТА САМА комірка (i == j у swap(arr[i], arr[j])), перший XOR обнулить її в нуль.",
              11, RED, "start", "bold")
    save("fig-15-4a-2-xor-swap.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.2.4a.3 — пошук відмінного біта: A^B світить різниці, x&-x ловить молодшу
# ════════════════════════════════════════════════════════════════════════════
def fig_diff_bit():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 30, "Де саме два слова різняться: A ⊕ B світить усі відмінні біти",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "а потім x & (−x) вихоплює НАЙМОЛОДШИЙ відмінний біт — без жодного циклу",
              11, GREY, "middle", style="italic")

    A = "10110100"
    B = "10010110"
    a = int(A, 2)
    b = int(B, 2)
    x = a ^ b                       # 00100010
    low = x & (-x)                  # ізолювати молодший 1: 00000010

    cell = 38
    gx = 250
    # де відрізняються (для зеленої рамки)
    diff = {i for i in range(8) if A[i] != B[i]}
    xb = format(x, "08b")
    lowb = format(low, "08b")
    lowidx = {i for i in range(8) if lowb[i] == "1"}

    y0 = 96
    rows = [
        ("A", A, RED, "#fdeceb", None),
        ("B", B, BLUE, "#eaf0fb", None),
        ("A ⊕ B", xb, GREEN, "#eef7f0", diff),
        ("A ⊕ B  &  −(A ⊕ B)", lowb, PURPLE, "#f3ecfa", lowidx),
    ]
    for k, (lbl, bits, col, fon, hl) in enumerate(rows):
        yy = y0 + k * 66
        s += text(gx - 18, yy + cell / 2 + 4, lbl, 13, col, "end", "bold", mono=True)
        s += bitrow(gx, yy, bits, cell, highlight=hl, ink_on=col, fill_on=fon, size=17)
        if k == 1:
            s += text(gx + 8 * cell + 20, yy + cell + 6, "↓ XOR порозрядно", 11, GREEN, "start", "bold")
        if k == 2:
            s += text(gx + 8 * cell + 20, yy + cell + 6, "↓ ізолювати молодший 1", 11, PURPLE, "start", "bold")

    # підписи позицій (вага розрядів)
    yb = y0 - 16
    for i in range(8):
        s += text(gx + i * cell + cell / 2, yb, str(7 - i), 10, GREY, "middle", mono=True)
    s += text(gx + 8 * cell + 20, yb, "← номер розряду", 10, GREY, "start", style="italic")

    # анотації: скільки й де відмінностей (рахуємо чесно з даних) — нижче останнього рядка
    diffweights = [str(7 - i) for i in sorted(diff)]
    s += text(gx + 4 * cell, y0 + 3 * 66 + cell + 22,
              f"різняться розряди {', '.join(diffweights)};  popcount(A⊕B) = {bin(x).count('1')} = відстань Геммінга",
              11, GREEN, "middle", "bold")

    # права колонка — як працює x & -x
    px = 690
    s += rect(px, 300, 215, 150, "#f3ecfa", PURPLE, 1.6, 12)
    s += text(px + 107, 324, "Чому  x & (−x)", 12.5, PURPLE, "middle", "bold")
    s += text(px + 16, 348, "−x = (інверсія x) + 1.", 10.5, INK, "start")
    s += text(px + 16, 366, "Додавання 1 «перевертає»", 10.5, INK, "start")
    s += text(px + 16, 384, "усі молодші нулі назад в 1,", 10.5, INK, "start")
    s += text(px + 16, 402, "а молодший 1 лишає 1 —", 10.5, INK, "start")
    s += text(px + 16, 420, "тож AND залишає рівно його.", 10.5, INK, "start")

    # стрічка внизу
    s += rect(40, 470, 865, 56, "#fffaf2", ORANGE, 1.6, 12)
    s += text(472, 493, "Навіщо це на практиці", 12, ORANGE, "middle", "bold")
    s += text(472, 514, "Дебаунс і зміна стану портів: A⊕B = «які піни змінилися», далі &−x обходить їх по одному (O(числа змін), не O(32)).",
              10.5, INK, "middle")
    save("fig-15-4a-3-diff-bit.svg", s)


if __name__ == "__main__":
    fig_parity_fold()
    fig_xor_swap()
    fig_diff_bit()
    print("OK")
