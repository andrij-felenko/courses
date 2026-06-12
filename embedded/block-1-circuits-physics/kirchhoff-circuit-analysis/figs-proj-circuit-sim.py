# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для ⚙️-вставки §1.4.8a «Симулятор кіл (CircuitJS-клас)».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами fig-4-8a-sim-*.
Головного figs.py розділу НЕ чіпає (§9: окремий скрипт зі своїми хелперами).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів — за темою-вставкою: Рис. 1.4.8a.k.
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
PANEL = "#f4f6f9"
AMBER = "#e08030"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", AMBER: "aAmber"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def res_h(x, y, w, label=None, color=INK):
    """Горизонтальний резистор-зигзаг від (x,y) завширшки w."""
    n = 6
    seg = w / (n + 2)
    s = line(x, y, x + seg, y, color)
    px, py = x + seg, y
    up = True
    for _ in range(n):
        nx = px + seg
        ny = y - 7 if up else y + 7
        s += line(px, py, nx, ny, color)
        px, py = nx, ny
        up = not up
    s += line(px, py, px + seg, y, color)
    s += line(px + seg, y, x + w, y, color)
    if label:
        s += text(x + w / 2, y - 13, label, 14, color, "middle", "bold")
    return s


def battery(x, y):
    """Маленька батарея-джерело (вертикальна), плюс зверху."""
    s = line(x - 11, y - 4, x + 11, y - 4, INK, 3)   # довга — +
    s += line(x - 6, y + 4, x + 6, y + 4, INK, 2)    # коротка — −
    s += text(x + 16, y - 3, "+", 15, RED, "start", "bold")
    s += text(x + 16, y + 13, "−", 15, BLUE, "start", "bold")
    return s


def dot(cx, cy, r=3.4, fill=INK):
    return circle(cx, cy, r, fill=fill, stroke="none", w=0)


# ───────────────────────── Рис. 1.4.8a.1 — цикл «перевір до паяння» ─────────────────────────
def fig_loop():
    W, H = 720, 430
    s = header(W, H)
    s += text(W / 2, 30, "Симулятор як «нульова ітерація»: спіймати помилку на екрані, а не на платі",
              17, INK, "middle", "bold")

    # Чотири кроки циклу по колу + центр.
    cx, cy = 360, 250
    steps = [
        (360, 120, "1. Намалювати", "перенести схему\nз §1.4.8 у вікно", GREEN),
        (560, 250, "2. Запустити", "симулятор розв'язує\nрівняння Кірхгофа", BLUE),
        (360, 380, "3. Зміряти", "клік на елемент:\nV, I, P миттєво", AMBER),
        (160, 250, "4. Звірити", "збігається з ручним\nрозрахунком?", RED),
    ]
    # стрілки циклу між боксами
    order = [(0, 1), (1, 2), (2, 3), (3, 0)]
    bw, bh = 168, 78
    centers = [(x, y) for (x, y, *_rest) in steps]
    for a, b in order:
        ax, ay = centers[a]
        bx, by = centers[b]
        # вкоротити до країв
        dx, dy = bx - ax, by - ay
        d = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / d, dy / d
        sx, sy = ax + ux * 95, ay + uy * 52
        ex, ey = bx - ux * 95, by - uy * 52
        s += arrow(sx, sy, ex, ey, GREY, 2.4)

    for (x, y, t, sub, col) in steps:
        s += rect(x - bw / 2, y - bh / 2, bw, bh, fill=PANEL, stroke=col, sw=2.4, rx=11)
        s += text(x, y - 12, t, 16, col, "middle", "bold")
        for i, ln in enumerate(sub.split("\n")):
            s += text(x, y + 8 + i * 17, ln, 12.5, INK, "middle")

    # центр — головна думка
    s += text(cx, cy - 8, "ціна помилки", 13, GREY, "middle")
    s += text(cx, cy + 12, "тут ≈ 0", 18, INK, "middle", "bold")
    s += text(cx, cy + 32, "(а на платі — час і деталі)", 11.5, GREY, "middle")

    # підпис «назад до §1.4.8»
    s += text(W / 2, H - 12,
              "Цикл крутять, доки числа не зійдуться — і лише тоді беруться за паяльник.",
              13, GREY, "middle", "normal", "italic")
    s += footer()
    open(os.path.join(OUT, "fig-4-8a-sim-1-verify-loop.svg"), "w", encoding="utf-8").write(s)


# ───────────────── Рис. 1.4.8a.2 — що показує симулятор (анатомія вікна) ─────────────────
def fig_window():
    W, H = 720, 470
    s = header(W, H)
    s += text(W / 2, 28, "Що показує симулятор: ті самі величини Кірхгофа — наочно й одразу",
              16.5, INK, "middle", "bold")

    # ── ліворуч: «полотно» з колом і рухомими точками струму ──
    s += rect(28, 52, 392, 388, fill=PANEL, stroke=GREY, sw=1.6, rx=10)
    s += text(40, 74, "полотно (drag-and-drop)", 12.5, GREY, "start", "normal", "italic")

    # коло: джерело зліва, два послідовні резистори згори, дільник
    L, R = 95, 360
    TOP, BOT = 130, 360
    # рамка проводів
    s += line(L, TOP, R, TOP, INK, 2.4)      # верх
    s += line(L, BOT, R, BOT, INK, 2.4)      # низ
    s += line(L, TOP, L, BOT, INK, 2.4)      # ліва (джерело)
    s += line(R, TOP, R, BOT, INK, 2.4)      # права
    # джерело по лівій стороні
    s += battery(L, (TOP + BOT) / 2)
    s += text(L - 16, (TOP + BOT) / 2 + 5, "12 В", 12.5, INK, "end")
    # два резистори згори (R1 послідовно)
    s += res_h(150, TOP, 80, "R₁ 100Ω")
    s += res_h(255, TOP, 80, "R₂ 200Ω")
    # середня точка-вузол (вихід дільника)
    midx = 242
    s += dot(midx, TOP, 4, GREEN)
    s += text(midx, TOP - 20, "вузол A", 11.5, GREEN, "middle", "bold")
    # рухомі «точки струму» (анімація → тут статичні кружечки)
    for fx in (118, 198, 300, 345):
        s += dot(fx, TOP, 3, AMBER)
    for fx in (140, 230, 320):
        s += dot(fx, BOT, 3, AMBER)
    s += dot(L, 175, 3, AMBER)
    s += dot(L, 315, 3, AMBER)
    s += text(225, BOT + 22, "рухомі точки = струм (густина ∝ I)", 11.5, AMBER, "middle")

    # ── праворуч: панель замірів ──
    px = 452
    s += rect(px, 52, 240, 388, fill="#ffffff", stroke=INK, sw=1.6, rx=10)
    s += text(px + 120, 74, "клік на елемент →", 13, INK, "middle", "bold")
    s += text(px + 120, 90, "панель замірів", 12, GREY, "middle")
    s += line(px + 14, 100, px + 226, 100, FAINT, 1.4)

    rows = [
        ("Напруга вузла A", "U(A) = 8.00 В", BLUE, "= V·R₂/(R₁+R₂)"),
        ("Струм гілки", "I = 40.0 мА", AMBER, "однаковий усюди (KCL)"),
        ("Спад на R₁", "V₁ = 4.00 В", INK, "I·R₁ (закон Ома)"),
        ("Потужність R₂", "P₂ = 320 мВт", RED, "I²·R — гріється?"),
        ("Σ спадів у контурі", "= 12.00 В  ✓", GREEN, "= джерело (KVL)"),
    ]
    yy = 122
    for (name, val, col, note) in rows:
        s += text(px + 16, yy, name, 12.5, INK, "start")
        s += text(px + 16, yy + 19, val, 15, col, "start", "bold")
        s += text(px + 16, yy + 36, note, 11, GREY, "start", "normal", "italic")
        s += line(px + 14, yy + 48, px + 226, yy + 48, FAINT, 1.2)
        yy += 64

    # стрілка-привʼязка від вузла А до панелі
    s += arrow(midx + 6, TOP + 6, px - 6, 132, GREEN, 1.8, "4,3")

    s += text(W / 2, H - 10,
              "Симулятор не вигадує фізики — він просто показує те, що ви порахували б руками за §1.4.8.",
              12.5, GREY, "middle", "normal", "italic")
    s += footer()
    open(os.path.join(OUT, "fig-4-8a-sim-2-what-it-shows.svg"), "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    fig_loop()
    fig_window()
    print("OK: fig-4-8a-sim-1-verify-loop.svg, fig-4-8a-sim-2-what-it-shows.svg")
