# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.10.2a — «Від схеми до маски: place & route і GDSII».
Окремий скрипт (за AUTHORING §9 не чіпаємо головний figs.py розділу). Чистий Python, без залежностей.
Вивід → ./img/ з УНІКАЛЬНИМИ іменами (префікс fig-3-10-2a-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; стрілки через marker; sans-serif.
Нумерація підписів — Рис. 3.10.2a.k.
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
PURPLE = "#7a3ea8"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", PURPLE: "aPurple", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill="none", stroke=INK, w=2, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{w}" fill-opacity="{opacity}"/>\n')


def write(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)


# ──────────────────────────────────────────────────────────────────────────
# Рис. 3.10.2a.1 — Конвеєр EDA: від RTL до GDSII, де саме сидять place & route
# ──────────────────────────────────────────────────────────────────────────
def fig_flow():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 28, "Конвеєр EDA: текст логіки → геометрія → набір масок",
              size=17, anchor="middle", weight="bold")

    # горизонтальний ланцюжок етапів
    stages = [
        ("RTL\n(Verilog/VHDL)", "що робить логіка", FAINT, INK),
        ("Синтез\n(synthesis)", "→ нетлист зі стандартних\nкомірок", "#eef2fb", BLUE),
        ("Floorplan", "де блоки, живлення,\nкільце контактів", "#eef2fb", BLUE),
        ("Розміщення\n(placement)", "кожна комірка → (x, y)", "#fdf0e2", ORANGE),
        ("Трасування\n(routing)", "дроти між виводами\nпо шарах металу", "#fdf0e2", ORANGE),
        ("Перевірки\nDRC / LVS / STA", "правила, відповідність,\nтаймінг", "#eef2fb", BLUE),
        ("GDSII / OASIS", "багатошарова\nгеометрія", "#e9f6ec", GREEN),
    ]
    n = len(stages)
    bw, bh = 100, 78
    gap = (W - 40 - n * bw) / (n - 1)
    x0, y0 = 20, 96
    centers = []
    for i, (title, sub, fill, edge) in enumerate(stages):
        x = x0 + i * (bw + gap)
        s += rect(x, y0, bw, bh, fill=fill, stroke=edge, sw=2.2, rx=8)
        # заголовок (до 2 рядків)
        for j, ln in enumerate(title.split("\n")):
            s += text(x + bw / 2, y0 + 24 + j * 16, ln, size=13.5,
                      anchor="middle", weight="bold", color=edge)
        centers.append((x + bw / 2, y0, x + bw / 2, y0 + bh, x, x + bw))
        # підпис під блоком (до 3 рядків)
        for j, ln in enumerate(sub.split("\n")):
            s += text(x + bw / 2, y0 + bh + 18 + j * 14, ln, size=11,
                      anchor="middle", color=GREY)
        if i > 0:
            px = x0 + (i - 1) * (bw + gap) + bw
            s += arrow(px + 4, y0 + bh / 2, x - 4, y0 + bh / 2, color=INK, w=2)

    # рамка «place & route» довкола двох помаранчевих етапів
    pr_x1 = centers[3][4] - 12
    pr_x2 = centers[4][5] + 12
    s += rect(pr_x1, y0 - 16, pr_x2 - pr_x1, bh + 78, fill="none",
              stroke=ORANGE, sw=2.2, rx=10)
    s += text((pr_x1 + pr_x2) / 2, y0 - 24, "place & route (P&R)",
              size=13.5, anchor="middle", weight="bold", color=ORANGE)

    # нижня частина: що додає кожен великий етап (три «знімки»)
    sy = 248
    s += text(W / 2, sy - 4, "Що з'являється на кожному великому кроці",
              size=14, anchor="middle", weight="bold", color=GREY)

    # 1) нетлист (граф комірок без координат)
    ax, ay, aw, ah = 40, sy + 14, 230, 170
    s += rect(ax, ay, aw, ah, fill="#fafbff", stroke=BLUE, sw=1.6, rx=8)
    s += text(ax + aw / 2, ay + 22, "Нетлист (після синтезу)", size=13,
              anchor="middle", weight="bold", color=BLUE)
    s += text(ax + aw / 2, ay + 40, "комірки + з'єднання, БЕЗ координат",
              size=11, anchor="middle", color=GREY)
    nodes = [(ax + 50, ay + 80, "AND"), (ax + 150, ay + 70, "DFF"),
             (ax + 70, ay + 135, "OR"), (ax + 175, ay + 130, "INV")]
    for (nx, ny, lbl) in nodes:
        s += rect(nx - 26, ny - 15, 52, 28, fill="#eef2fb", stroke=BLUE, sw=1.6, rx=5)
        s += text(nx, ny + 4, lbl, size=11.5, anchor="middle", color=BLUE)
    # довільні зв'язки (логічні, не геометричні)
    s += line(nodes[0][0] + 26, nodes[0][1], nodes[1][0] - 26, nodes[1][1], color=GREY, w=1.5)
    s += line(nodes[0][0], nodes[0][1] + 13, nodes[2][0], nodes[2][1] - 15, color=GREY, w=1.5)
    s += line(nodes[1][0], nodes[1][1] + 13, nodes[3][0], nodes[3][1] - 15, color=GREY, w=1.5)
    s += line(nodes[2][0] + 26, nodes[2][1], nodes[3][0] - 26, nodes[3][1], color=GREY, w=1.5)

    # 2) розміщення (ті самі комірки лягли в рядки)
    bx, by, bw2, bh2 = 300, sy + 14, 230, 170
    s += rect(bx, by, bw2, bh2, fill="#fffaf3", stroke=ORANGE, sw=1.6, rx=8)
    s += text(bx + bw2 / 2, by + 22, "Розміщення (placement)", size=13,
              anchor="middle", weight="bold", color=ORANGE)
    s += text(bx + bw2 / 2, by + 40, "кожна комірка отримала (x, y) у рядку",
              size=11, anchor="middle", color=GREY)
    rows_y = [by + 70, by + 105, by + 140]
    for ry in rows_y:
        s += line(bx + 16, ry + 14, bx + bw2 - 16, ry + 14, color=FAINT, w=8)
    placed = [(bx + 40, rows_y[0], "AND"), (bx + 150, rows_y[0], "DFF"),
              (bx + 60, rows_y[1], "OR"), (bx + 120, rows_y[2], "INV")]
    for (nx, ny, lbl) in placed:
        s += rect(nx - 24, ny, 48, 28, fill="#fdf0e2", stroke=ORANGE, sw=1.6, rx=4)
        s += text(nx, ny + 19, lbl, size=11, anchor="middle", color=ORANGE)

    # 3) трасування + GDSII (дроти по шарах, прямі кути)
    cx, cy, cw, ch = 560, sy + 14, 260, 170
    s += rect(cx, cy, cw, ch, fill="#f4fbf6", stroke=GREEN, sw=1.6, rx=8)
    s += text(cx + cw / 2, cy + 22, "Трасування → GDSII", size=13,
              anchor="middle", weight="bold", color=GREEN)
    s += text(cx + cw / 2, cy + 40, "дроти прокладено по шарах металу",
              size=11, anchor="middle", color=GREY)
    rows_y2 = [cy + 70, cy + 140]
    for ry in rows_y2:
        s += line(cx + 16, ry + 14, cx + cw - 16, ry + 14, color=FAINT, w=8)
    cells2 = [(cx + 50, rows_y2[0], "AND"), (cx + 175, rows_y2[0], "DFF"),
              (cx + 80, rows_y2[1], "INV")]
    for (nx, ny, lbl) in cells2:
        s += rect(nx - 24, ny, 48, 28, fill="#e9f6ec", stroke=GREEN, sw=1.6, rx=4)
        s += text(nx, ny + 19, lbl, size=11, anchor="middle", color=GREEN)
    # дріт AND (верхній рядок) → INV (нижній рядок), двома шарами:
    # горизонталь (синій метал) + вертикаль (червоний метал), стики = перехідники (via)
    vx = cx + 130
    s += line(cells2[0][0] + 24, cells2[0][1] + 8, vx, cells2[0][1] + 8, color=BLUE, w=2.6)
    s += line(vx, cells2[0][1] + 8, vx, cells2[2][1] + 8, color=RED, w=2.6)
    s += line(vx, cells2[2][1] + 8, cells2[2][0] + 24, cells2[2][1] + 8, color=BLUE, w=2.6)
    s += circle(vx, cells2[0][1] + 8, 3.4, fill=INK, stroke=INK, w=1)
    s += circle(vx, cells2[2][1] + 8, 3.4, fill=INK, stroke=INK, w=1)
    s += text(cx + cw - 12, cy + ch - 10, "─ метал гор.  │ метал верт.  • перехідник (via)",
              size=10, anchor="end", color=GREY)

    s += footer()
    write("fig-3-10-2a-1-flow.svg", s)


# ──────────────────────────────────────────────────────────────────────────
# Рис. 3.10.2a.2 — Placement як оптимізація: довжина дроту й перевантаження
# ──────────────────────────────────────────────────────────────────────────
def fig_placement():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 26, "Розміщення — це оптимізація: коротші дроти, рівномірне навантаження",
              size=16, anchor="middle", weight="bold")

    def grid(ox, oy, title, color):
        out = rect(ox, oy, 300, 300, fill="#ffffff", stroke=INK, sw=1.8, rx=6)
        out += text(ox + 150, oy - 10, title, size=14, anchor="middle",
                    weight="bold", color=color)
        # рядки стандартних комірок (тонкі смуги)
        for r in range(6):
            ry = oy + 26 + r * 46
            out += line(ox + 14, ry, ox + 286, ry, color=FAINT, w=10)
        return out

    # ---- ЛІВО: погане розміщення (зв'язані комірки далеко) ----
    lx, ly = 50, 86
    s += grid(lx, ly, "Погане розміщення", RED)
    # три комірки одного ланцюга, рознесені по кутах
    A = (lx + 50, ly + 26)
    B = (lx + 240, ly + 118)
    C = (lx + 70, ly + 256)
    for (p, lbl, col) in [(A, "A", ORANGE), (B, "B", ORANGE), (C, "C", ORANGE)]:
        s += rect(p[0] - 24, p[1], 48, 26, fill="#fdf0e2", stroke=col, sw=1.8, rx=4)
        s += text(p[0], p[1] + 18, lbl, size=12, anchor="middle", color=col)
    # довгі дроти (манхеттенські, прямі кути), позначити довжину
    def mh(p, q, color, w=2.6, dash=None):
        midx = q[0]
        return (line(p[0], p[1] + 13, midx, p[1] + 13, color, w, dash) +
                line(midx, p[1] + 13, midx, q[1] + 13, color, w, dash))
    s += mh(A, B, RED)
    s += mh(B, C, RED)
    s += text(lx + 150, ly + 320, "сумарна довжина дротів ВЕЛИКА → більші затримки",
              size=11.5, anchor="middle", color=RED)

    # ---- ПРАВО: гарне розміщення (зв'язані поруч) ----
    rx0, ry0 = 470, 86
    s += grid(rx0, ry0, "Гарне розміщення", GREEN)
    A2 = (rx0 + 90, ry0 + 118)
    B2 = (rx0 + 170, ry0 + 118)
    C2 = (rx0 + 130, ry0 + 164)
    for (p, lbl, col) in [(A2, "A", ORANGE), (B2, "B", ORANGE), (C2, "C", ORANGE)]:
        s += rect(p[0] - 24, p[1], 48, 26, fill="#fdf0e2", stroke=col, sw=1.8, rx=4)
        s += text(p[0], p[1] + 18, lbl, size=12, anchor="middle", color=col)
    s += line(A2[0] + 24, A2[1] + 13, B2[0] - 24, B2[1] + 13, color=GREEN, w=2.6)
    s += line(B2[0], B2[1] + 26, B2[0], C2[1] + 6, color=GREEN, w=2.6)
    s += line(B2[0], C2[1] + 6, C2[0] + 24, C2[1] + 13, color=GREEN, w=2.6)
    s += text(rx0 + 150, ry0 + 320, "сумарна довжина дротів МАЛА → швидше й щільніше",
              size=11.5, anchor="middle", color=GREEN)

    # стрілка-перехід «оптимізуємо»
    s += arrow(lx + 305, ly + 150, rx0 - 8, ry0 + 150, color=PURPLE, w=2.6)
    s += text((lx + 305 + rx0) / 2, ly + 138, "цільова функція ↓",
              size=12.5, anchor="middle", weight="bold", color=PURPLE)
    s += text((lx + 305 + rx0) / 2, ly + 168,
              "≈ Σ довжин + штраф за перевантаження",
              size=10.5, anchor="middle", color=PURPLE)

    s += footer()
    write("fig-3-10-2a-2-placement.svg", s)


# ──────────────────────────────────────────────────────────────────────────
# Рис. 3.10.2a.3 — GDSII: один чіп = стос шарів-полігонів = стос масок
# ──────────────────────────────────────────────────────────────────────────
def fig_gdsii():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 26, "GDSII: чіп описаний як полігони на шарах — кожен шар стає маскою",
              size=15.5, anchor="middle", weight="bold")

    # ---- ЛІВО: GDSII як ієрархія (cell → polygon на layer/datatype) ----
    lx, ly = 36, 64
    s += text(lx, ly, "Що всередині GDSII (спрощено):", size=13, weight="bold", color=INK)
    lines = [
        ("STRUCTURE  cpu_top", INK, "bold"),
        ("  SREF  alu_cell   @(0,0)", GREY, "normal"),
        ("  SREF  alu_cell   @(12,0)   ← повтор", PURPLE, "normal"),
        ("  STRUCTURE  alu_cell", INK, "bold"),
        ("    BOUNDARY  layer=ACTIVE  [полігон]", GREEN, "normal"),
        ("    BOUNDARY  layer=POLY    [полігон]", RED, "normal"),
        ("    BOUNDARY  layer=METAL1  [полігон]", BLUE, "normal"),
        ("    PATH      layer=METAL2  [дріт]", ORANGE, "normal"),
    ]
    yy = ly + 26
    for (t, col, wt) in lines:
        s += mono(lx + 6, yy, t, size=12.5, color=col, weight=wt)
        yy += 22
    s += text(lx + 6, yy + 8,
              "координати в нанометрах; одна комірка —",
              size=11, color=GREY)
    s += text(lx + 6, yy + 24,
              "багато разів через посилання (ієрархія, без копій).",
              size=11, color=GREY)

    # ---- ПРАВО: розрізаний «стос» шарів, кожен → окрема маска ----
    layers = [
        ("ACTIVE",  GREEN,  "#e9f6ec"),
        ("POLY",    RED,    "#fbeae8"),
        ("CONTACT", GREY,   "#efefef"),
        ("METAL1",  BLUE,   "#eef2fb"),
        ("VIA1",    PURPLE, "#f1eafa"),
        ("METAL2",  ORANGE, "#fdf0e2"),
    ]
    ox, oy = 470, 76
    pw, ph = 224, 38
    dx, dy = 20, 28   # косий зсув для «3D»-стосу
    n = len(layers)
    # підпис стосу праворуч від origin, над верхнім шаром
    s += text(ox + pw - dx * (n - 1) + 4, oy - 12, "стос шарів = опис кристала",
              size=12.5, color=INK, weight="bold")
    # малюємо знизу вгору, щоб верхні перекривали
    for i in range(n - 1, -1, -1):
        name, edge, fill = layers[i]
        x = ox + i * dx
        y = oy + i * dy
        # паралелограм-пластина
        pts = [(x, y), (x + pw, y), (x + pw - dx, y + ph), (x - dx, y + ph)]
        s += polygon(pts, fill=fill, stroke=edge, w=1.8, opacity=0.96)
        # кілька «вікон» (полігонів) на шарі — щоб було видно геометрію
        for k in range(3):
            wxx = x + 26 + k * 58
            s += rect(wxx, y + 9, 30, ph - 18, fill="#ffffff", stroke=edge, sw=1.6)
        # назва шару — на лівому краю пластини (не виходить за полотно)
        s += text(x - dx - 6, y + ph - 11, name, size=11.5, color=edge,
                  weight="bold", anchor="end")

    stack_bottom = oy + (n - 1) * dy + ph
    # одна «маска» внизу + стрілка «кожен шар → окрема фотомаска»
    mcx, mcy = ox + pw / 2 + 10, stack_bottom + 64
    s += arrow(ox + pw / 2 + 10, stack_bottom + 8, mcx, mcy - 26, color=INK, w=2)
    s += text(mcx + 14, stack_bottom + 30, "кожен шар → окрема фотомаска",
              size=12, color=INK, anchor="start")
    # значок маски (скляна пластина з непрозорим візерунком)
    s += rect(mcx - 52, mcy - 18, 104, 34, fill="#f3f3f3", stroke=INK, sw=1.8, rx=3)
    for k in range(4):
        s += rect(mcx - 44 + k * 24, mcy - 11, 12, 20, fill=INK, stroke="none", sw=0)
    s += text(mcx, mcy + 30, "фотомаска (reticle)", size=11, color=GREY, anchor="middle")

    s += text(W / 2, H - 12,
              "Маски по черзі друкують світлом на пластину (фотолітографія §3.10.2) — шар за шаром (§3.10.3).",
              size=11.5, anchor="middle", color=GREY)

    s += footer()
    write("fig-3-10-2a-3-gdsii.svg", s)


if __name__ == "__main__":
    fig_flow()
    fig_placement()
    fig_gdsii()
    print("OK ->", OUT)
