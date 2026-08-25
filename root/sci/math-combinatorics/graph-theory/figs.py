# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Теорія графів».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

VERT = "#eef2fb"   # заливка вершини


def vertex(cx, cy, label, r=22, sub=None):
    out = circle(cx, cy, r, fill=VERT, stroke=NEG, sw=2.2)
    out += text(cx, cy + 5, label, size=15, bold=True)
    if sub:
        out += text(cx, cy + r + 15, sub, size=11, color=MUTED)
    return out


# ── Фігура 1: кеніґсберзькі мости → граф ─────────────────────────────────────
# Першопричина всієї теорії графів. Зліва — спрощена мапа: дві береги (A знизу,
# B зверху), два острови (C ліворуч/центр — Кнайпгоф, D праворуч), сім мостів
# між ними. Справа — те саме як граф: кожна суша = вершина, кожен міст = ребро.
# Підписуємо степінь кожної вершини (скільки мостів торкається) — і відразу
# видно, що всі чотири степені непарні. А прогулянка, що проходить кожне ребро
# рівно раз, можлива тільки коли непарних вершин нуль або дві. Тому неможливо.
def fig_koenigsberg():
    W, H = 940, 470
    parts = []

    # ── ліворуч: спрощена мапа ──
    parts.append(text(225, 70, "Кеніґсберґ: чотири суші, сім мостів",
                      size=13, bold=True))

    # річка (дві смуги) — щоб видно було два береги і два острови між рукавами
    parts.append(rect(60, 150, 330, 36, fill="#dbe7f5", stroke="none", sw=0, rx=4))
    parts.append(rect(60, 300, 330, 36, fill="#dbe7f5", stroke="none", sw=0, rx=4))

    # чотири суші як підписані плями
    land = {
        "A": (225, 390),   # південний берег
        "B": (225, 110),   # північний берег
        "C": (150, 243),   # острів (Кнайпгоф)
        "D": (320, 243),   # східний острів
    }
    names = {"A": "пд. берег", "B": "пн. берег", "C": "острів", "D": "острів"}
    for k, (x, y) in land.items():
        parts.append(circle(x, y, 28, fill="#f3ede2", stroke="#b08a4f", sw=2))
        parts.append(text(x, y + 5, k, size=15, bold=True, color="#7a5a26"))
        parts.append(text(x, y + 44, names[k], size=10, color=MUTED))

    # сім мостів (лінії між сушами) — кратні ребра показують, що міст не один
    bridges = [
        ("A", "C"), ("A", "C"),   # два мости південь–острів
        ("B", "C"), ("B", "C"),   # два мости північ–острів
        ("A", "D"),               # один південь–схід
        ("B", "D"),               # один північ–схід
        ("C", "D"),               # один острів–острів
    ]
    # невеликі зсуви, щоб подвійні мости не злилися в одну лінію
    offs = {0: -10, 1: 10}
    seen = {}
    for a, b in bridges:
        key = tuple(sorted((a, b)))
        i = seen.get(key, 0); seen[key] = i + 1
        ax, ay = land[a]; bx, by = land[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        sh = offs.get(i, 0) if key in (("A", "C"), ("B", "C")) else 0
        parts.append(line(ax + nx * sh, ay + ny * sh, bx + nx * sh, by + ny * sh,
                          color="#9a7b45", sw=4))
    parts.append(text(225, 452, "сім мостів через рукави Преголі", size=10,
                      color=MUTED))

    # ── стрілка переходу ──
    parts.append(arrow(410, 250, 470, 250, color=FIELD, sw=2.6))
    parts.append(text(440, 238, "відкинь\nгеографію", size=10, color=FIELD))

    # ── праворуч: граф ──
    parts.append(text(710, 70, "Те саме як граф: суша = вершина, міст = ребро",
                      size=13, bold=True))
    G = {"A": (710, 390), "B": (710, 110), "C": (610, 243), "D": (820, 243)}
    # ребра (кратні — вигнуті в різні боки)
    def edge(a, b, bend=0):
        ax, ay = G[a]; bx, by = G[b]
        if bend == 0:
            return line(ax, ay, bx, by, color=INK, sw=2.4)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        cx, cy = mx + nx * bend, my + ny * bend
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="2.4"/>' % (ax, ay, cx, cy, bx, by, INK))
    parts.append(edge("A", "C", +26)); parts.append(edge("A", "C", -26))
    parts.append(edge("B", "C", +26)); parts.append(edge("B", "C", -26))
    parts.append(edge("A", "D")); parts.append(edge("B", "D"))
    parts.append(edge("C", "D"))
    # вершини зі степенем
    deg = {"A": 3, "B": 3, "C": 5, "D": 3}
    for k, (x, y) in G.items():
        parts.append(vertex(x, y, k))
        parts.append(text(x, y - 32, "степінь %d" % deg[k], size=11,
                          color=POS, bold=True))

    # підсумок-рамка
    parts.append(fitbox(70, H - 46, W - 140, 38,
                 "Прогулянку, що проходить кожен міст рівно раз, можна замкнути, лише коли непарних вершин нуль або дві.\n"
                 "Тут їх чотири — тому такого маршруту немає. Це й довів Ейлер.",
                 size=12.5, fill="#e9f7ef", stroke=FIELD, sw=2))

    render("img/koenigsberg.svg", W, H, *parts,
           title="Сім мостів Кеніґсберґа: як народилася теорія графів")


# ── Фігура 2: те саме ребро — багато рисунків; степінь і рукостискання ────────
# Дві ідеї разом. (1) Граф — це СПИСОК з'єднань, а не картинка: той самий граф
# можна намалювати по-різному, і це той самий граф. (2) Степінь вершини = скільки
# ребер до неї входить; якщо скласти степені всіх вершин, кожне ребро лічиться
# двічі (за обидва кінці), тож сума степенів = подвоєне число ребер.
def fig_anatomy():
    W, H = 940, 470
    parts = []

    # ── зліва: три різні рисунки одного графа (вершини 1..4, ребра однакові) ──
    parts.append(text(255, 64, "Один граф — різні рисунки", size=13, bold=True))
    E = [("1", "2"), ("2", "3"), ("3", "4"), ("4", "1"), ("2", "4")]

    def draw(pos, ox, oy):
        for a, b in E:
            ax, ay = pos[a]; bx, by = pos[b]
            parts.append(line(ox + ax, oy + ay, ox + bx, oy + by, color=INK, sw=2.2))
        for k, (x, y) in pos.items():
            parts.append(vertex(ox + x, oy + y, k, r=16))

    sq = {"1": (0, 0), "2": (110, 0), "3": (110, 110), "4": (0, 110)}
    draw(sq, 70, 100)
    parts.append(text(135, 250, "як квадрат", size=11, color=MUTED))

    dia = {"1": (55, 0), "2": (110, 70), "3": (55, 140), "4": (0, 70)}
    draw(dia, 300, 90)
    parts.append(text(355, 250, "як ромб", size=11, color=MUTED))

    ln = {"1": (0, 30), "2": (70, 0), "3": (140, 30), "4": (70, 120)}
    draw(ln, 110, 285)
    parts.append(text(180, 425, "перемішані вершини", size=11, color=MUTED))
    parts.append(fitbox(70, 440, 290, 24,
                 "Ребра ті самі → це ТОЙ САМИЙ граф.",
                 size=11, fill=FILL, stroke=LINE, sw=1.4))

    # роздільник
    parts.append(line(470, 80, 470, 440, color="#e1e1e1", sw=1.5))

    # ── справа: степінь і теорема про рукостискання ──
    parts.append(text(700, 64, "Степінь вершини й рукостискання", size=13, bold=True))
    # один граф з підписаними степенями
    P = {"1": (620, 150), "2": (790, 150), "3": (790, 300), "4": (620, 300)}
    for a, b in E:
        ax, ay = P[a]; bx, by = P[b]
        parts.append(line(ax, ay, bx, by, color=INK, sw=2.2))
    deg = {"1": 2, "2": 3, "3": 2, "4": 3}
    for k, (x, y) in P.items():
        parts.append(vertex(x, y, k, r=18))
        parts.append(text(x + (22 if x > 700 else -22), y - 22,
                          "deg=%d" % deg[k], size=11, color=POS, bold=True,
                          anchor="start" if x > 700 else "end"))

    parts.append(fitbox(560, 350, 300, 86,
                 "Степінь = скільки ребер торкаються вершини.\n"
                 "Сума степенів: 2+3+2+3 = 10.\n"
                 "Ребер 5, а 2·5 = 10 — кожне ребро лічиться двічі\n"
                 "(за обидва кінці). Тож Σ степенів = 2·(число ребер).",
                 size=11.5, fill="#eef2fb", stroke=NEG, sw=2))

    render("img/graph-anatomy.svg", W, H, *parts,
           title="Анатомія графа: вершини, ребра, степінь")


# ── Фігура 3: матриця суміжності проти списку суміжності ──────────────────────
# Як граф живе в пам'яті машини, і чому форма залежить від щільності. Ліворуч —
# граф. По центру — матриця суміжності N×N: 1 там, де вершини сполучені (місце
# завжди N², хоч ребер мало). Праворуч — список суміжності: на кожну вершину
# перелік сусідів (місце росте з числом ребер). Розріджений граф → список;
# щільний → матриця.
def fig_representations():
    W, H = 960, 450
    parts = []
    V = ["1", "2", "3", "4"]
    E = [("1", "2"), ("1", "3"), ("2", "3"), ("3", "4")]
    adj = {v: [] for v in V}
    for a, b in E:
        adj[a].append(b); adj[b].append(a)

    # ── граф ──
    parts.append(text(150, 70, "Граф", size=13, bold=True))
    P = {"1": (90, 130), "2": (210, 130), "3": (90, 270), "4": (210, 270)}
    for a, b in E:
        ax, ay = P[a]; bx, by = P[b]
        parts.append(line(ax, ay, bx, by, color=INK, sw=2.2))
    for k, (x, y) in P.items():
        parts.append(vertex(x, y, k, r=20))

    # ── матриця суміжності ──
    parts.append(text(500, 70, "Матриця суміжності (N×N)", size=13, bold=True))
    x0, y0, c = 430, 110, 40
    # заголовки стовпців/рядків
    for j, v in enumerate(V):
        parts.append(text(x0 + c / 2 + (j + 1) * c, y0 + c / 2 + 4, v, size=12,
                          bold=True, color=MUTED))
        parts.append(text(x0 + c / 2, y0 + c / 2 + (j + 1) * c + 4, v, size=12,
                          bold=True, color=MUTED))
    for i, a in enumerate(V):
        for j, b in enumerate(V):
            cx, cy = x0 + (j + 1) * c, y0 + (i + 1) * c
            one = b in adj[a]
            parts.append(rect(cx, cy, c, c, fill="#fdecea" if one else BG,
                              stroke="#cfd6dd", sw=1, rx=0))
            parts.append(text(cx + c / 2, cy + c / 2 + 5, "1" if one else "0",
                              size=13, bold=one,
                              color=POS if one else MUTED))
    parts.append(text(x0 + c * 3, y0 + c * 5 + 18,
                      "місце завжди N² — байдуже скільки ребер",
                      size=10.5, color=MUTED))

    # ── список суміжності ──
    parts.append(text(800, 70, "Список суміжності", size=13, bold=True))
    lx, ly = 700, 110
    for i, v in enumerate(V):
        y = ly + i * 46
        parts.append(textbox(lx, y, v, size=13, pad=8, min_w=34,
                             fill="#eef2fb", stroke=NEG, sw=1.8, bold=True)[0])
        parts.append(arrow(lx + 22, y, lx + 54, y, color=MUTED, sw=1.8))
        parts.append(fitbox(lx + 58, y - 16, 150, 32,
                     ", ".join(adj[v]), size=12, fill=FILL, stroke=LINE, sw=1.3))
    parts.append(text(lx + 70, ly + 4 * 46 + 6,
                      "місце росте з числом ребер", size=10.5, color=MUTED))

    parts.append(fitbox(70, H - 44, W - 140, 36,
                 "Розріджений граф (ребер мало) — бери список: пам'яті стільки, скільки ребер.\n"
                 "Щільний граф (ребер майже N²) — бери матрицю: відповідь «чи сполучені?» миттєва.",
                 size=12.5, fill="#e9f7ef", stroke=FIELD, sw=2))

    render("img/representations.svg", W, H, *parts,
           title="Граф у пам'яті: матриця суміжності проти списку суміжності")


if __name__ == "__main__":
    fig_koenigsberg()
    fig_anatomy()
    fig_representations()
    print("OK: koenigsberg, graph-anatomy, representations")
