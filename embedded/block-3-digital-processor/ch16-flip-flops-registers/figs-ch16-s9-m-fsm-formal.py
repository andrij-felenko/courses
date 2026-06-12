# -*- coding: utf-8 -*-
"""
SVG-фігури для 🧮-вставки §3.3.9m — «Формалізм скінченних автоматів:
стани, входи, діаграми переходів (зв'язок із regex)».
Окремий генератор (головний figs.py НЕ чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-16-9m-1-states.svg   — діаграма переходів детектора «101»: 4 стани, дуги з мітками входу
  fig-16-9m-2-regex.svg    — як вираз 1·0·1 над алфавітом збирає той самий автомат (regex ↔ FSM)
  fig-16-9m-3-moore-mealy.svg — де живе вихід: Мур (у стані) проти Мілі (на дузі)
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # вхід/біт «1», акцент
BLUE  = "#1f47b5"   # вхід/біт «0»
GREEN = "#1f8a3b"   # висновок, «прийнято», поле
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8.2" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8.2" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8.2" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8.2" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8.2" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, dash=None, marker=None, fill="none"):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: стан-вузол (кружок); подвійний контур = приймальний/цільовий ──
def node(cx, cy, label, r=30, accept=False, color=INK, fill="#fff", sub=None):
    out = circle(cx, cy, r, fill, color, 2.2)
    if accept:
        out += circle(cx, cy, r - 5, "none", color, 2.0)   # подвійне коло
    out += text(cx, cy + (1 if not sub else -3), label, 17, color, "middle", "bold")
    if sub:
        out += text(cx, cy + 15, sub, 10, GREY, "middle")
    return out


def _pt_on_circle(cx, cy, r, ang_deg):
    a = math.radians(ang_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def edge_arc(c1, c2, r, color, label, bend=0.0, lab_off=(0, -8), lab_color=None):
    """Дуга переходу між двома станами з підписом-входом.
    bend — наскільки вигнути (0 = пряма); lab_off — зсув підпису від середини."""
    x1, y1 = c1
    x2, y2 = c2
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    ux, uy = dx / dist, dy / dist
    # точки старту/кінця — на межах кіл
    sx, sy = x1 + ux * r, y1 + uy * r
    ex, ey = x2 - ux * r, y2 - uy * r
    nx, ny = -uy, ux  # нормаль
    mx, my = (sx + ex) / 2 + nx * bend, (sy + ey) / 2 + ny * bend
    out = path(f"M {sx:.1f},{sy:.1f} Q {mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}",
               color, 2.2, marker=color)
    lx = (sx + ex) / 2 + nx * bend * 0.6 + lab_off[0]
    ly = (sy + ey) / 2 + ny * bend * 0.6 + lab_off[1]
    out += text(lx, ly, label, 14, lab_color or color, "middle", "bold")
    return out


def self_loop(cx, cy, r, color, label, top=True):
    """Петля «лишитися в тому самому стані» над/під вузлом."""
    sgn = -1 if top else 1
    sx, sy = cx - 12, cy + sgn * (r - 2)
    ex, ey = cx + 12, cy + sgn * (r - 2)
    c1x, c1y = cx - 26, cy + sgn * (r + 40)
    c2x, c2y = cx + 26, cy + sgn * (r + 40)
    out = path(f"M {sx:.1f},{sy:.1f} C {c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {ex:.1f},{ey:.1f}",
               color, 2.2, marker=color)
    out += text(cx, cy + sgn * (r + 52) + (0 if top else 6), label, 14, color, "middle", "bold")
    return out


def start_marker(cx, cy, r, color=INK):
    """Стрілка «старт» у початковий стан зліва."""
    out = arrow(cx - r - 42, cy, cx - r - 2, cy, color, 2.2)
    out += text(cx - r - 46, cy - 8, "старт", 11, GREY, "end")
    return out


# ── Фігура 1: діаграма переходів детектора «101» ─────────────────────────────
def fig1_states():
    W, H = 820, 470
    b = header(W, H)
    b += text(W / 2, 30, "Діаграма переходів: автомат, що ловить підрядок «1 0 1»",
              17, INK, "middle", "bold")
    b += text(W / 2, 52, "стани = «скільки потрібного вже зібрано»; дуги = реакція на наступний біт",
              12.5, GREY, "middle", style="italic")

    r = 34
    y = 215
    xs = [120, 320, 520, 720]
    labels = ["S0", "S1", "S2", "S3"]
    subs = ["нічого", "є «1»", "є «10»", "є «101»!"]
    accepts = [False, False, False, True]
    colors = [INK, INK, INK, GREEN]
    centers = [(x, y) for x in xs]

    # дуги «уперед» (рух до мети) — на вершині потрібний біт
    # S0 --1--> S1
    b += edge_arc(centers[0], centers[1], r, RED, "1", bend=0, lab_off=(0, -12))
    # S1 --0--> S2
    b += edge_arc(centers[1], centers[2], r, BLUE, "0", bend=0, lab_off=(0, -12))
    # S2 --1--> S3
    b += edge_arc(centers[2], centers[3], r, RED, "1", bend=0, lab_off=(0, -12))

    # дуги «назад/убік» (не той біт — частковий відкат), вигнуті знизу
    # S1 --1--> S1 (ще одна 1 — лишаємось «є 1»): петля зверху
    b += self_loop(xs[1], y, r, RED, "1", top=True)
    # S0 --0--> S0 (нулі на початку нічого не дають): петля зверху
    b += self_loop(xs[0], y, r, BLUE, "0", top=True)
    # S2 --0--> S0 (після «10» прийшов 0 → «100», скидаємось): довга дуга низом
    b += edge_arc(centers[2], centers[0], r, BLUE, "0", bend=120, lab_off=(0, 20))
    # S3 --0--> S2 (після збігу прийшов 0: хвіст «...10» знову частковий) низом, коротша
    b += edge_arc(centers[3], centers[2], r, BLUE, "0", bend=-74, lab_off=(0, 18))
    # S3 --1--> S1 (після збігу прийшла 1: лишається хвіст «1») низом
    b += edge_arc(centers[3], centers[1], r, RED, "1", bend=92, lab_off=(0, 22))

    # вузли поверх дуг
    for (cx, cy), lab, sub, acc, col in zip(centers, labels, subs, accepts, colors):
        b += node(cx, cy, lab, r, acc, col, "#eefaef" if acc else "#fff", sub)

    b += start_marker(xs[0], y, r)

    # легенда входів
    lx, ly = 90, 388
    b += rect(lx - 18, ly - 22, 300, 70, "#fbfbfb", FAINT, 1.4, 8)
    b += text(lx, ly, "вхід (наступний біт):", 12, INK, "start", "bold")
    b += line(lx, ly + 16, lx + 26, ly + 16, RED, 3)
    b += text(lx + 32, ly + 20, "1", 13, RED, "start", "bold")
    b += line(lx + 70, ly + 16, lx + 96, ly + 16, BLUE, 3)
    b += text(lx + 102, ly + 20, "0", 13, BLUE, "start", "bold")
    b += text(lx + 130, ly + 20, "подвійне коло = «знайшов»", 11, GREEN, "start")

    # прогін прикладу
    ex, ey = 430, 388
    b += rect(ex - 14, ey - 22, 360, 70, "#fbfbfb", FAINT, 1.4, 8)
    b += text(ex, ey, "Прогін «1 1 0 1»:", 12, INK, "start", "bold")
    b += text(ex, ey + 20, "S0 →1 S1 →1 S1 →0 S2 →1 S3 ✓", 13, INK, "start")
    b += text(ex, ey + 40, "на четвертому біті стан S3 — підрядок знайдено", 10.5, GREEN, "start")

    save("fig-16-9m-1-states.svg", b)


# ── Фігура 2: regex ↔ автомат (вираз 1·0·1 збирає той самий автомат) ─────────
def fig2_regex():
    W, H = 820, 470
    b = header(W, H)
    b += text(W / 2, 30, "Два описи однієї множини рядків: вираз і автомат",
              17, INK, "middle", "bold")

    # ── верх: алгебра подій над алфавітом {0,1} ──
    ax, ay = 60, 78
    b += text(ax, ay, "Алгебра подій (regex) над алфавітом Σ = {0, 1}:", 13.5, INK, "start", "bold")
    b += text(ax, ay + 26, "три цеглини — і будь-яка «регулярна» множина рядків:", 12, GREY, "start")

    # картки трьох операцій
    cards = [
        ("вибір", "a | b", "«або a, або b»", BLUE),
        ("склейка", "a · b", "«a, за ним b»", INK),
        ("повтор", "a*", "«a нуль чи більше разів»", RED),
    ]
    cw2, ch2 = 220, 64
    cy0 = ay + 44
    for i, (nm, expr, gloss, col) in enumerate(cards):
        x = ax + i * (cw2 + 18)
        b += rect(x, cy0, cw2, ch2, "#fbfbfb", col, 1.8, 9)
        b += text(x + 14, cy0 + 24, nm, 12, col, "start", "bold")
        b += text(x + 14, cy0 + 46, expr, 16, INK, "start", "bold")
        b += text(x + 96, cy0 + 46, gloss, 11, GREY, "start")

    # приклад-вираз
    ey = cy0 + ch2 + 44
    b += text(W / 2, ey - 8, "Наш приклад одним виразом — «десь у потоці стоїть 1 0 1»:",
              13, INK, "middle")
    expr = "(0 | 1)*  ·  1 · 0 · 1  ·  (0 | 1)*"
    b += rect(W / 2 - 200, ey, 400, 40, "#eef7ff", BLUE, 2, 9)
    b += text(W / 2, ey + 26, expr, 18, INK, "middle", "bold")
    b += text(W / 2 - 150, ey + 58, "будь-що спереду", 10.5, GREY, "middle")
    b += text(W / 2, ey + 58, "ядро «101»", 10.5, RED, "middle")
    b += text(W / 2 + 150, ey + 58, "будь-що позаду", 10.5, GREY, "middle")

    # ── стрілка-теорема вниз ──
    midy = ey + 92
    b += arrow(W / 2, midy, W / 2, midy + 34, GREEN, 2.6)
    b += rect(W / 2 + 14, midy + 4, 300, 30, "#eefaef", GREEN, 1.6, 8)
    b += text(W / 2 + 24, midy + 24, "теорема Кліні: вираз ⇄ автомат", 12.5, GREEN, "start", "bold")

    # ── низ: той самий автомат у лінію (компактно) ──
    ny = midy + 92
    r = 26
    xs = [150, 330, 510, 690]
    labs = ["S0", "S1", "S2", "S3"]
    accs = [False, False, False, True]
    cs = [(x, ny) for x in xs]
    b += text(110, ny - 52, "Той самий опис — як машина зі станами:", 13, INK, "start", "bold")

    b += edge_arc(cs[0], cs[1], r, RED, "1", lab_off=(0, -10))
    b += edge_arc(cs[1], cs[2], r, BLUE, "0", lab_off=(0, -10))
    b += edge_arc(cs[2], cs[3], r, RED, "1", lab_off=(0, -10))
    b += self_loop(xs[0], ny, r, BLUE, "0", top=True)
    b += self_loop(xs[1], ny, r, RED, "1", top=True)
    b += edge_arc(cs[2], cs[0], r, BLUE, "0", bend=86, lab_off=(0, 18))
    b += edge_arc(cs[3], cs[1], r, RED, "1", bend=70, lab_off=(0, 20))
    b += edge_arc(cs[3], cs[2], r, BLUE, "0", bend=-58, lab_off=(0, 16))
    for (cx, cy), lab, acc in zip(cs, labs, accs):
        b += node(cx, cy, lab, r, acc, GREEN if acc else INK, "#eefaef" if acc else "#fff")
    b += start_marker(xs[0], ny, r)

    b += text(W / 2, H - 16, "Кожен оператор виразу — це шматок графа; зірочка * стає петлею. "
                             "Опис і схема — одне й те саме.",
              12, GREY, "middle", style="italic")
    save("fig-16-9m-2-regex.svg", b)


# ── Фігура 3: Мур проти Мілі — де живе вихід ─────────────────────────────────
def fig3_moore_mealy():
    W, H = 820, 430
    b = header(W, H)
    b += text(W / 2, 30, "Де народжується вихід: Мур (у стані) проти Мілі (на дузі)",
              17, INK, "middle", "bold")

    # роздільник
    b += line(W / 2, 56, W / 2, H - 54, FAINT, 1.6, "6,6")

    r = 30

    # ── ЛІВО: Мур — вихід приписано СТАНУ ──
    b += text(205, 78, "Мур (Moore)", 15, INK, "middle", "bold")
    b += text(205, 98, "вихід = функція лише стану", 11.5, GREY, "middle")
    lx = [110, 300]
    ly = 200
    lc = [(x, ly) for x in lx]
    # два стани: A (вих 0), B (вих 1)
    b += edge_arc(lc[0], lc[1], r, RED, "1", lab_off=(0, -12))
    b += edge_arc(lc[1], lc[0], r, BLUE, "0", bend=84, lab_off=(0, 18))
    b += self_loop(lx[0], ly, r, BLUE, "0", top=True)
    b += self_loop(lx[1], ly, r, RED, "1", top=True)
    # вузли з «вбудованим» виходом
    b += circle(lx[0], ly, r, "#eef7ff", BLUE, 2.2)
    b += text(lx[0], ly - 4, "A", 17, INK, "middle", "bold")
    b += text(lx[0], ly + 14, "out 0", 11, BLUE, "middle", "bold")
    b += circle(lx[1], ly, r, "#eefaef", GREEN, 2.2)
    b += text(lx[1], ly - 4, "B", 17, INK, "middle", "bold")
    b += text(lx[1], ly + 14, "out 1", 11, GREEN, "middle", "bold")
    b += start_marker(lx[0], ly, r)
    b += text(205, 318, "Вихід «висить» на стані:", 12, INK, "middle", "bold")
    b += text(205, 338, "поки сидимо в B — на виході 1.", 11.5, GREY, "middle")
    b += text(205, 358, "Міняється лише після фронту,", 11.5, INK, "middle")
    b += text(205, 376, "разом зі станом → без глітчів.", 11.5, GREEN, "middle")

    # ── ПРАВО: Мілі — вихід приписано ПЕРЕХОДУ (дузі) ──
    b += text(615, 78, "Мілі (Mealy)", 15, INK, "middle", "bold")
    b += text(615, 98, "вихід = функція стану І входу", 11.5, GREY, "middle")
    rxs = [520, 710]
    ry = 200
    rc = [(x, ry) for x in rxs]
    # дуги з підписом «вхід / вихід»
    b += edge_arc(rc[0], rc[1], r, RED, "1 / 1", lab_off=(0, -12), lab_color=RED)
    b += edge_arc(rc[1], rc[0], r, BLUE, "0 / 0", bend=84, lab_off=(0, 18), lab_color=BLUE)
    b += self_loop(rxs[0], ry, r, BLUE, "0 / 0", top=True)
    b += self_loop(rxs[1], ry, r, RED, "1 / 1", top=True)
    b += circle(rxs[0], ry, r, "#fff", INK, 2.2)
    b += text(rxs[0], ry + 1, "P", 17, INK, "middle", "bold")
    b += circle(rxs[1], ry, r, "#fff", INK, 2.2)
    b += text(rxs[1], ry + 1, "Q", 17, INK, "middle", "bold")
    b += start_marker(rxs[0], ry, r)
    b += text(615, 318, "Вихід — на стрілці «вхід / вихід»:", 12, INK, "middle", "bold")
    b += text(615, 338, "реагує на вхід у тому ж такті", 11.5, INK, "middle")
    b += text(615, 358, "→ часто менше станів, та вихід", 11.5, GREY, "middle")
    b += text(615, 376, "може смикнутись між фронтами.", 11.5, AMBER, "middle")

    save("fig-16-9m-3-moore-mealy.svg", b)


if __name__ == "__main__":
    fig1_states()
    fig2_regex()
    fig3_moore_mealy()
    print("ch16-s9-m-fsm-formal figures done.")
