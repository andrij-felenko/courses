# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SETTLED = "#27ae60"
FRONT   = "#e08a1e"
FAR     = "#9aa3af"
EDGEC   = "#94a3b8"
ALERT   = "#e74c3c"
BLUE    = "#2980b9"

def node(cx, cy, name, dist=None, fill=FILL, stroke=LINE, r=22):
    """Вузол-кружок із ім'ям усередині та опційним підписом зверху."""
    out = circle(cx, cy, r, fill=fill, stroke=stroke, sw=2.0)
    out += text(cx, cy + 5, name, size=14, color=INK, bold=True)
    if dist is not None:
        out += text(cx, cy - r - 7, dist, size=12, color=stroke if stroke != LINE else MUTED, bold=True)
    return out

def wedge(x1, y1, x2, y2, w=None, r1=22, r2=22, col=EDGEC, sw=2.0, dash=None):
    """Ребро між двома вузлами з відступом на радіуси."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ax, ay = x1 + ux * r1, y1 + uy * r1
    bx, by = x2 - ux * r2, y2 - uy * r2
    out = line(ax, ay, bx, by, color=col, sw=sw, dash=dash)
    if w is not None:
        mx, my = (ax + bx) / 2, (ay + by) / 2
        out += circle(mx, my, 10, fill=BG, stroke="none", sw=0)
        out += text(mx, my + 4, str(w), size=12, color=INK, bold=True)
    return out


# ── ФІГ.1 Дистанційно-векторне оновлення ──────────────────────────────────────
def fig_dv_update():
    W, H = 760, 360
    p = []

    ax, ay = 140.0, 140.0
    bx, by = 380.0, 140.0
    cx, cy = 620.0, 140.0

    p.append(wedge(ax, ay, bx, by, 2, col=INK, sw=2.2))
    p.append(wedge(bx, by, cx, cy, 3, col=BLUE, sw=2.5))

    p.append(node(ax, ay, "A", fill="#eaf7ee", stroke=SETTLED))
    p.append(node(bx, by, "B", fill="#fdf0dd", stroke=FRONT))
    p.append(node(cx, cy, "C", fill="#ebf5fb", stroke=BLUE))

    p.append(arrow(590, 95, 410, 95, color=BLUE, sw=2.0))
    p.append(text(500, 82, "вектор від C: {C:0, D:4}", size=12, color=BLUE, bold=True))

    txt_table = (
        "Вузол B обчислює нові відстані через C (вага ребра B–C = 3):\n"
        "• d(B → C) = min(поточна, 3 + 0) = 3\n"
        "• d(B → D) = min(∞, 3 + 4) = 7   [оновлено!]\n"
        "Рівняння Беллмана–Форда: d_B(X) = min_v (c(B,v) + d_v(X))"
    )
    b, bw, bh = textbox(380, 260, txt_table, size=12.5, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "dv-update.svg"), W, H, *p,
           title="Дистанційно-векторне оновлення за рівнянням Беллмана–Форда")


# ── ФІГ.2 Відлік до нескінченності ─────────────────────────────────────────────
def fig_count_to_infinity():
    W, H = 760, 400
    p = []

    ax, ay = 140.0, 120.0
    bx, by = 380.0, 120.0
    cx, cy = 620.0, 120.0

    p.append(wedge(ax, ay, bx, by, 1, col=INK, sw=2.2))
    p.append(wedge(bx, by, cx, cy, None, col=ALERT, sw=2.2, dash="4 4"))
    p.append(line(490, 110, 510, 130, color=ALERT, sw=3.0))
    p.append(line(490, 130, 510, 110, color=ALERT, sw=3.0))
    p.append(text(500, 95, "ОБРИВ", size=11, color=ALERT, bold=True))

    p.append(node(ax, ay, "A", dist="d(C)=2", fill=FILL, stroke=LINE))
    p.append(node(bx, by, "B", dist="d(C)=1", fill="#fdeae8", stroke=ALERT))
    p.append(node(cx, cy, "C", dist="d(C)=0", fill=FILL, stroke=FAR))

    txt_steps = (
        "1. Лінк B–C падає. B втрачає прямий шлях до C (d_B(C) = ∞).\n"
        "2. B бачить, що A пропонує d_A(C) = 2, і вважає: «піду до C через A!» → d_B(C) = 2 + 1 = 3.\n"
        "3. A отримує від B новий вектор d_B(C) = 3 і оновлює свій шлях: d_A(C) = 3 + 1 = 4.\n"
        "4. Зациклення продовжується: 4 → 5 → 6 ... до максимуму (в RIP: ∞ = 16 hops)."
    )
    b, bw, bh = textbox(380, 270, txt_steps, size=12.5, bold=False, fill="#fdeae8", stroke=ALERT)
    p.append(b)

    render(os.path.join(OUT, "count-to-infinity.svg"), W, H, *p,
           title="Проблема відліку до нескінченності при обриві зв'язку")


# ── ФІГ.3 Link-State затоплення та локальний Дейкстра ─────────────────────────
def fig_link_state():
    W, H = 760, 420
    p = []

    p.append(text(210, 35, "1. Затоплення LSA (Link-State)", size=14, color=INK, bold=True))
    p.append(rect(30, 55, 360, 340, fill="#f4f6f7", stroke="#d5dbdb", rx=8))

    nx, ny = 210.0, 160.0
    p.append(node(nx, ny, "A", fill="#eaf7ee", stroke=SETTLED))

    n1x, n1y = 100.0, 260.0
    n2x, n2y = 210.0, 310.0
    n3x, n3y = 320.0, 260.0

    p.append(wedge(nx, ny, n1x, n1y, col=SETTLED, sw=2.0))
    p.append(wedge(nx, ny, n2x, n2y, col=SETTLED, sw=2.0))
    p.append(wedge(nx, ny, n3x, n3y, col=SETTLED, sw=2.0))

    p.append(node(n1x, n1y, "B", fill=FILL, stroke=LINE, r=18))
    p.append(node(n2x, n2y, "C", fill=FILL, stroke=LINE, r=18))
    p.append(node(n3x, n3y, "D", fill=FILL, stroke=LINE, r=18))

    p.append(circle(nx, ny, 42, fill="none", stroke=SETTLED, sw=1.5))
    p.append(circle(nx, ny, 65, fill="none", stroke=SETTLED, sw=1.5))
    p.append(text(nx, ny - 75, "LSA від A розсилається всім", size=11, color=SETTLED, bold=True))

    p.append(text(570, 35, "2. Локальний граф і Дейкстра", size=14, color=INK, bold=True))
    p.append(rect(410, 55, 320, 340, fill="#ebf5fb", stroke="#a9cce3", rx=8))

    map_txt = (
        "Кожен роутер збирає LSA від УСІХ вузлів\n"
        "і будує ідентичну картографію G=(V,E).\n\n"
        "Після цього роутер A запускає\n"
        "алгоритм Дейкстри локально,\n"
        "обчислюючи дерево найкоротших\n"
        "шляхів від себе до всіх вершин."
    )
    b = fitbox(425, 110, 290, 230, map_txt, size=12.5, bold=False, fill="#ffffff", stroke=BLUE)
    p.append(b)

    render(os.path.join(OUT, "link-state.svg"), W, H, *p,
           title="Затоплення LSA та локальне обчислення дерева найкоротших шляхів")


# ── ФІГ.4 Path-Vector та виявлення зациклень у BGP ───────────────────────────
def fig_path_vector():
    W, H = 760, 380
    p = []

    as1x, as1y = 120.0, 130.0
    as2x, as2y = 310.0, 90.0
    as3x, as3y = 500.0, 90.0
    as4x, as4y = 310.0, 220.0

    p.append(wedge(as1x, as1y, as2x, as2y, col=INK, sw=2.2))
    p.append(wedge(as2x, as2y, as3x, as3y, col=INK, sw=2.2))
    p.append(wedge(as3x, as3y, as4x, as4y, col=INK, sw=2.2))
    p.append(wedge(as4x, as4y, as1x, as1y, col=ALERT, sw=2.2, dash="4 4"))

    p.append(node(as1x, as1y, "AS100", fill="#eaf7ee", stroke=SETTLED, r=28))
    p.append(node(as2x, as2y, "AS200", fill=FILL, stroke=LINE, r=28))
    p.append(node(as3x, as3y, "AS300", fill=FILL, stroke=LINE, r=28))
    p.append(node(as4x, as4y, "AS400", fill="#fdf0dd", stroke=FRONT, r=28))

    pv_txt = (
        "Маршрут до префікса 192.0.2.0/24 анонсується вздовж ланцюжка:\n"
        "• AS100 → AS200: path = [AS100]\n"
        "• AS200 → AS300: path = [AS200, AS100]\n"
        "• AS300 → AS400: path = [AS300, AS200, AS100]\n"
        "• AS400 спробує відправити в AS100: AS100 бачить СВІЙ номер у path → ВІДКИДАЄ"
    )
    b, bw, bh = textbox(380, 315, pv_txt, size=12.0, bold=False, fill="#fff7ee", stroke=FRONT)
    p.append(b)

    render(os.path.join(OUT, "path-vector.svg"), W, H, *p,
           title="Шляхово-векторна маршрутизація (Path-Vector) та запобігання петель")


if __name__ == "__main__":
    fig_dv_update()
    fig_count_to_infinity()
    fig_link_state()
    fig_path_vector()
    print("Figures generated successfully.")
