# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SETTLED = "#27ae60"   # зафіксований (у скарбниці)
FRONT   = "#e08a1e"   # межа / щойно витягнутий
FAR     = "#9aa3af"   # ще нескінченність
EDGEC   = "#94a3b8"   # ребра тла


def node(cx, cy, name, dist, fill=FILL, stroke=LINE, r=22):
    """Вузол-кружок із іменем усередині й підписом-відстанню зверху."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, name, size=15, color=INK, bold=True)
    out += text(cx, cy - r - 7, dist, size=12, color=stroke if stroke != LINE else MUTED, bold=True)
    return out


def wedge(x1, y1, x2, y2, w, r1=22, r2=22, col=EDGEC, sw=2.0, dash=None):
    """Ребро між двома вузлами (з відступом на радіуси) + вага посередині."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    out = line(ax, ay, bx, by, color=col, sw=sw, dash=dash)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    # невеликий білий підклад під число ваги
    out += circle(mx, my, 10, fill=BG, stroke="none", sw=0)
    out += text(mx, my + 4, str(w), size=12, color=INK, bold=True)
    return out


# ── ФІГ.1 Крок послаблення: сусід пропонує коротший шлях ──────────────────────
# Ідея: у вузла v є поточна оцінка d[v]. Через щойно зафіксований u веде шлях
# завдовжки d[u]+w. Якщо він коротший — оцінку v ЗБИВАЄМО до d[u]+w. Це єдина
# операція, з якої зроблено весь алгоритм.
def fig_relax():
    W, H = 720, 300
    p = []
    ux, uy = 150.0, 150.0
    vx, vy = 540.0, 150.0

    # ребро u→v з вагою
    p.append(wedge(ux, uy, vx, vy, 3, col=INK, sw=2.4))

    # u — зафіксований (зелений), відстань відома й остаточна
    p.append(node(ux, uy, "u", "d[u] = 7", fill="#eaf7ee", stroke=SETTLED))
    # v — поточна (стара) оцінка велика
    p.append(node(vx, vy, "v", "d[v] = 12", fill=FILL, stroke=FAR))

    # підпис ребра
    p.append(text((ux + vx) / 2, uy - 34, "вага ребра  w = 3", size=12, color=MUTED))

    # обчислення під ребром
    b, bw, bh = textbox((ux + vx) / 2, 232,
                        "новий шлях через u:  d[u] + w = 7 + 3 = 10\n10 < 12  →  збиваємо  d[v] := 10",
                        size=13, bold=True, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "relax.svg"), W, H, *p,
           title="Крок послаблення: сусід пропонує коротший шлях")


# ── ФІГ.2 Жадібна межа: найближчий нефіксований можна фіксувати назавжди ───────
# Ідея: скарбниця зафіксованих росте. Черга віддає нефіксований вузол із
# НАЙМЕНШОЮ оцінкою. Довести коротший шлях до нього неможливо: будь-який інший
# маршрут виходить за межу через дорожчий вузол, тож не буде коротшим.
def fig_greedy():
    W, H = 760, 480
    p = []
    cx, cy, r = 250.0, 200.0, 150.0

    # «хмара» зафіксованого (зелена зона)
    p.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#eaf7ee" '
             'stroke="%s" stroke-width="2" stroke-dasharray="6 5"/>'
             % (cx, cy, r, 130, SETTLED))
    p.append(text(cx, cy - 108, "СКАРБНИЦЯ (відстань остаточна)", size=12.5, color=SETTLED, bold=True))

    # старт і кілька зафіксованих усередині
    p.append(node(cx - 90, cy, "s", "0", fill="#eaf7ee", stroke=SETTLED, r=20))
    p.append(node(cx - 10, cy - 45, "a", "2", fill="#eaf7ee", stroke=SETTLED, r=20))
    p.append(node(cx + 5, cy + 55, "b", "5", fill="#eaf7ee", stroke=SETTLED, r=20))

    # кандидат на межі — найменша оцінка серед нефіксованих
    fx, fy = cx + 260, cy - 60
    p.append(node(fx, fy, "x", "6", fill="#fdf0dd", stroke=FRONT, r=22))
    # дорожчий сусід зовні
    gx, gy = cx + 260, cy + 90
    p.append(node(gx, gy, "y", "9", fill=FILL, stroke=FAR, r=22))

    # ребра з межі скарбниці до кандидатів
    p.append(wedge(cx - 10, cy - 45, fx, fy, 4, r1=20, col=INK, sw=2.2))
    p.append(wedge(cx + 5, cy + 55, gx, gy, 4, r1=20, col=EDGEC))
    p.append(wedge(gx, gy, fx, fy, 1, col=EDGEC, dash="4 4"))

    # висновок
    b, bw, bh = textbox(W / 2, 428,
                        "x — найменша оцінка поза скарбницею (6).  Будь-який інший шлях до x\n"
                        "вийшов би через дорожчий вузол (≥ 6) → не був би коротшим.\n"
                        "Отже 6 остаточне: фіксуємо x і рухаємо межу далі.",
                        size=12.5, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "greedy.svg"), W, H, *p,
           title="Жадібна межа: найближчий поза скарбницею — вже остаточний")


# ── ФІГ.3 Наскрізний прогін: порядок фіксації й підсумкові відстані ────────────
# Ідея: на конкретному графі показуємо порядок, у якому вузли лягають у
# скарбницю (за зростанням відстані), і остаточні d[]. Числа під вузлами —
# найкоротша відстань від s; жирна лінія — ребра дерева найкоротших шляхів.
def fig_trace():
    W, H = 760, 420
    p = []
    P = {
        "s": (110, 210),
        "a": (300, 90),
        "b": (300, 330),
        "c": (520, 90),
        "d": (520, 330),
        "e": (700, 210),
    }
    dist = {"s": 0, "a": 4, "b": 2, "c": 5, "d": 7, "e": 8}
    order = ["s", "b", "a", "c", "d", "e"]  # порядок фіксації

    # усі ребра з вагами (тло)
    E = [("s", "a", 4), ("s", "b", 2), ("a", "c", 1), ("b", "a", 1),
         ("b", "d", 5), ("c", "e", 3), ("d", "e", 2), ("c", "d", 3)]
    # ребра дерева найкоротших шляхів (жирні): s-b, b-a, a-c, c-e, b-d? d=7 через b(2)+5
    tree = {("s", "b"), ("b", "a"), ("a", "c"), ("c", "e"), ("b", "d")}

    for u, v, w in E:
        is_tree = (u, v) in tree or (v, u) in tree
        col = SETTLED if is_tree else EDGEC
        sw = 3.0 if is_tree else 1.8
        x1, y1 = P[u]; x2, y2 = P[v]
        p.append(wedge(x1, y1, x2, y2, w, col=col, sw=sw))

    # вузли з порядковим номером фіксації та відстанню
    for name, (x, y) in P.items():
        p.append(node(x, y, name, "d=%d" % dist[name], fill="#eaf7ee", stroke=SETTLED))
        k = order.index(name) + 1
        p.append(circle(x + 20, y - 20, 11, fill=FRONT, stroke=BG, sw=1.5))
        p.append(text(x + 20, y - 16, str(k), size=11, color=BG, bold=True))

    # легенда
    p.append(circle(560, 385, 10, fill=FRONT, stroke=BG, sw=1.5))
    p.append(text(560, 389, "1", size=10, color=BG, bold=True))
    p.append(text(576, 389, "— порядок фіксації (за зростанням d)", size=11, color=MUTED, anchor="start"))
    p.append(line(120, 385, 150, 385, color=SETTLED, sw=3.0))
    p.append(text(158, 389, "— ребро дерева найкоротших шляхів", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "trace.svg"), W, H, *p,
           title="Прогін: порядок фіксації і підсумкові відстані від s")


# ── ФІГ.4 (вставка hist) Двадцять хвилин проти трьох років ────────────────────
# Ідея: показати наскрізну іронію історії — задум народився миттєво (≈20 хв на
# терасі 1956-го), а публікація прийшла аж 1959-го. На одній осі життя Дейкстри:
# народження, перший «програміст», кав'ярня+ARMAC, друк. Контраст «мить осяяння»
# ↔ «повільний друк» несе головну думку вставки.
def fig_timeline():
    W, H = 820, 360
    p = []
    yaxis = 170.0
    # чотири рівновіддалені зупинки — читається чисто, без нагромадження рамок
    xs = [140.0, 340.0, 540.0, 720.0]

    # головна вісь часу
    p.append(line(90.0, yaxis, 760.0, yaxis, color=INK, sw=2.4))
    p.append(text(766.0, yaxis + 5, "час", size=12, color=MUTED, anchor="start"))

    events = [
        ("1930", "народження\n(Роттердам)", FAR, +1),
        ("1952", "перший «програміст»\nНідерландів", MUTED, -1),
        ("1956", "тераса кав'ярні + ARMAC\n≈ 20 хвилин", FRONT, +1),
        ("1959", "друк у Numerische\nMathematik", SETTLED, -1),
    ]
    for x, (lab, note, col, side) in zip(xs, events):
        p.append(circle(x, yaxis, 7, fill=col, stroke=BG, sw=2))
        p.append(text(x, yaxis + (28 if side > 0 else -18), lab, size=14, color=INK, bold=True))
        ny = yaxis + (74 if side > 0 else -72)
        b, bw, bh = textbox(x, ny, note, size=11.5, fill=BG, stroke=col, color=INK)
        p.append(b)

    # дуга «три роки до друку»: від 1956 (xs[2]) до 1959 (xs[3])
    xa, xb = xs[2], xs[3]
    p.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 4"/>'
             % (xa, yaxis + 8, xa + 25, yaxis + 42, xb - 25, yaxis + 42, xb, yaxis + 8, POS))
    p.append(text((xa + xb) / 2, yaxis + 40, "три роки", size=12, color=POS, bold=True))

    # підсумковий рядок унизу
    b, bw, bh = textbox(W / 2, 322,
                        "Задум — мить (≈ 20 хв, без олівця й паперу).  Друк — аж за три роки.\n"
                        "Осяяння коштує хвилини; довести його до людей — роки.",
                        size=12.5, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Двадцять хвилин задуму — і три роки до публікації")


if __name__ == "__main__":
    fig_relax()
    fig_greedy()
    fig_trace()
    fig_timeline()
    print("OK figs")
