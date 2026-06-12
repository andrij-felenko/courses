# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.2.6a — «Симулятор вентилів на 100 рядків».
Окремий скрипт (головний figs.py розділу НЕ чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/ тієї ж папки розділу; імена унікальні (префікс fig-15-6a-).

Стиль (AUTHORING §9): білий фон; «1»/істина червоний, «0»/хибність синій;
поле/«дійсне» зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — як в історіях до теми: Рис. 3.2.6a.k.

Допоміжні функції — копія зі спільного стилю figs.py (за §9 копіюються в кожен скрипт).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # «1» / істина / high
BLUE  = "#1f47b5"   # «0» / хибність / low
GREEN = "#1f8a3b"   # дійсне / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── гліфи вентилів (відмітні форми; копія стилю розділу) ─────────────────────
def gate_and(x, y, w=46, h=42, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    bx = x + w - r
    return (f'<path d="M {x},{y-r} L {bx},{y-r} A {r},{r} 0 0 1 {bx},{y+r} '
            f'L {x},{y+r} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_or(x, y, w=52, h=42, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    return (f'<path d="M {x},{y-r} Q {x+w*0.55},{y-r} {x+w},{y} '
            f'Q {x+w*0.55},{y+r} {x},{y+r} Q {x+w*0.28},{y} {x},{y-r} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_xor(x, y, w=52, h=42, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    body = gate_or(x, y, w, h, fill, stroke, sw)
    arc = (f'<path d="M {x-7},{y-r} Q {x+w*0.22},{y} {x-7},{y+r}" '
           f'fill="none" stroke="{stroke}" stroke-width="{sw}"/>\n')
    return body + arc


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.2.6a.1 — нетліст: вентилі як вузли-словники, які симулятор обчислює
#   зліва направо (топологічний порядок), посилаючись на імена сигналів.
# ─────────────────────────────────────────────────────────────────────────────
def fig1_netlist():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Схема як список вузлів: симулятор іде зліва направо й рахує кожен сигнал",
              size=17, color=INK, anchor="middle", weight="bold")

    # три колонки: входи → вузли-вентилі → виходи
    s += text(95, 64, "входи (відомі)", size=13, color=GREY, anchor="middle")
    s += text(440, 64, "вузли-вентилі (обчислюються по черзі)", size=13, color=GREY, anchor="middle")
    s += text(800, 64, "виходи", size=13, color=GREY, anchor="middle")

    # входи A,B,Cin як «защіпки» зі значеннями прикладу A=1,B=1,Cin=0
    ins = [("A", 1, 110), ("B", 1, 165), ("Cin", 0, 220)]
    for name, val, yy in ins:
        col = RED if val else BLUE
        s += rect(60, yy - 16, 70, 32, fill="#fff", stroke=col, sw=2, rx=6)
        s += text(78, yy + 5, name, size=15, color=INK, anchor="middle", weight="bold", font=MONO)
        s += text(116, yy + 5, f"={val}", size=15, color=col, anchor="middle", weight="bold", font=MONO)

    # вузли як рядки-словники {op, входи} — два півсуматори + OR
    # розкладка вузлів
    nx = 300
    def node(y, label, op, a, b, val, valcol):
        out = rect(nx, y - 22, 250, 44, fill="#fbfbf7", stroke=INK, sw=1.6, rx=8)
        out += text(nx + 12, y - 4, label, size=13, color=GREEN, anchor="start", weight="bold", font=MONO)
        out += text(nx + 12, y + 15, f'{{op:"{op}", a:"{a}", b:"{b}"}}',
                    size=13.5, color=INK, anchor="start", font=MONO)
        # обчислене значення праворуч від вузла
        out += circle(nx + 250 + 22, y, 15, fill="#fff", stroke=valcol, w=2)
        out += text(nx + 250 + 22, y + 5, str(val), size=15, color=valcol, anchor="middle",
                    weight="bold", font=MONO)
        return out

    yh1s, yh1c, yh2s, yh2c, yor = 110, 175, 250, 315, 250
    # перший півсуматор (A,B)
    s += node(yh1s, "g1 = HA1.sum", "XOR", "A", "B", 0, BLUE)      # 1 xor 1 = 0
    s += node(yh1c, "g2 = HA1.carry", "AND", "A", "B", 1, RED)     # 1 and 1 = 1
    # позначка групи
    s += text(nx + 125, 86, "півсуматор 1: A + B", size=12.5, color=GREY, anchor="middle", style="italic")

    nx2 = 300
    # другий півсуматор (g1, Cin) — зсунемо нижче праворуч? тримаємо в тій же колонці нижче
    s += node(yh2s, "g3 = HA2.sum", "XOR", "g1", "Cin", 0, BLUE)   # 0 xor 0 = 0  -> Sum
    s += node(yh2c, "g4 = HA2.carry", "AND", "g1", "Cin", 0, BLUE) # 0 and 0 = 0
    s += text(nx + 125, 226, "півсуматор 2: g1 + Cin", size=12.5, color=GREY, anchor="middle", style="italic")

    # OR двох переносів -> Cout  (праворуч окремою колонкою, нижче)
    nxor = 300
    s += node(385, "g5 = Cout", "OR", "g2", "g4", 1, RED)          # 1 or 0 = 1 -> Cout
    s += text(nx + 125, 361, "об'єднання переносів", size=12.5, color=GREY, anchor="middle", style="italic")

    # стрілки залежностей: входи -> вузли; вузли -> вузли
    # A,B -> g1,g2
    for (_, _, yy) in [("A", 1, 110), ("B", 1, 165)]:
        s += arrow(132, yy, nx - 4, yh1s if yy == 110 else yh1c, color=GREY, w=1.4)
    s += arrow(132, 110, nx - 4, yh1c, color=GREY, w=1.0, dash="3,3")
    s += arrow(132, 165, nx - 4, yh1s, color=GREY, w=1.0, dash="3,3")
    # g1 -> g3,g4 ; Cin -> g3,g4
    s += arrow(nx + 250 + 22, yh1s + 12, nx - 4, yh2s, color=GREY, w=1.4)
    s += arrow(nx + 250 + 22, yh1s + 12, nx - 4, yh2c, color=GREY, w=1.0, dash="3,3")
    s += arrow(132, 220, nx - 4, yh2s + 6, color=GREY, w=1.4)
    # g2 -> g5 ; g4 -> g5
    s += arrow(nx + 250 + 22, yh1c, nx - 4, 385 - 6, color=GREY, w=1.4)
    s += arrow(nx + 250 + 22, yh2c, nx - 4, 385 + 6, color=GREY, w=1.4)

    # виходи Sum, Cout
    s += rect(760, yh2s - 16, 86, 32, fill="#fff", stroke=BLUE, sw=2, rx=6)
    s += text(772, yh2s + 5, "Sum", size=14, color=INK, anchor="start", weight="bold", font=MONO)
    s += text(836, yh2s + 5, "0", size=15, color=BLUE, anchor="middle", weight="bold", font=MONO)
    s += arrow(nx + 250 + 22 + 16, yh2s, 758, yh2s, color=BLUE, w=2)

    s += rect(760, 385 - 16, 86, 32, fill="#fff", stroke=RED, sw=2, rx=6)
    s += text(772, 385 + 5, "Cout", size=14, color=INK, anchor="start", weight="bold", font=MONO)
    s += text(838, 385 + 5, "1", size=15, color=RED, anchor="middle", weight="bold", font=MONO)
    s += arrow(nx + 250 + 22 + 16, 385, 758, 385, color=RED, w=2)

    # підсумкова нота про порядок
    s += line(40, 425, W - 40, 425, color=FAINT, w=1.5)
    s += text(W / 2, 448,
              "Порядок g1→g2→g3→g4→g5 не випадковий: кожен вузол рахують лише тоді, "
              "коли всі його входи вже відомі (топологічний порядок).",
              size=13.5, color=INK, anchor="middle", style="italic")
    save("fig-15-6a-1-netlist.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.2.6a.2 — те, що друкує програма: повна таблиця істинності суматора
#   (8 рядків) + позначений рядок прикладу A=1,B=1,Cin=0.
# ─────────────────────────────────────────────────────────────────────────────
def fig2_truthtable():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Вихід програми: симулятор сам друкує всю таблицю повного суматора",
              size=16.5, color=INK, anchor="middle", weight="bold")
    s += text(W / 2, 52, "прогнали всі 2³ = 8 комбінацій входів — і звірили з Рис. 3.2.6.3",
              size=13, color=GREY, anchor="middle", style="italic")

    # таблиця 8 рядків: A B Cin | Sum Cout
    rows = [
        (0, 0, 0, 0, 0),
        (0, 0, 1, 1, 0),
        (0, 1, 0, 1, 0),
        (0, 1, 1, 0, 1),
        (1, 0, 0, 1, 0),
        (1, 0, 1, 0, 1),
        (1, 1, 0, 0, 1),
        (1, 1, 1, 1, 1),
    ]
    x0, y0 = 150, 90
    colw = [70, 70, 80, 90, 90]   # A B Cin | Sum Cout
    rowh = 38
    heads = ["A", "B", "Cin", "Sum", "Cout"]

    # вертикальний роздільник між входами й виходами
    sep_x = x0 + colw[0] + colw[1] + colw[2]

    # заголовок
    cx = x0
    for i, hcap in enumerate(heads):
        hb_col = INK if i < 3 else GREEN
        s += text(cx + colw[i] / 2, y0 - 12, hcap, size=15, color=hb_col, anchor="middle",
                  weight="bold", font=MONO)
        cx += colw[i]
    s += text(x0 - 28, y0 - 12, "#", size=13, color=GREY, anchor="middle", font=MONO)
    s += line(x0 - 40, y0 - 2, x0 + sum(colw) + 6, y0 - 2, color=INK, w=2)
    s += line(sep_x, y0 - 30, sep_x, y0 + 8 * rowh + 4, color=GREY, w=1.6, dash="4,3")

    # рядок прикладу A=1,B=1,Cin=0 -> індекс 6
    hi = 6
    for r, (a, b, c, sm, co) in enumerate(rows):
        ytop = y0 + r * rowh
        ymid = ytop + rowh / 2 + 5
        if r == hi:
            s += rect(x0 - 40, ytop, sum(colw) + 46, rowh, fill="#fdeceb", stroke=RED, sw=1.6, rx=4)
        elif r % 2 == 1:
            s += rect(x0 - 40, ytop, sum(colw) + 46, rowh, fill="#f7f7f7", stroke="none", sw=0)
        # індекс рядка
        s += text(x0 - 28, ymid, str(r), size=12.5, color=GREY, anchor="middle", font=MONO)
        vals = [a, b, c, sm, co]
        cx = x0
        for i, v in enumerate(vals):
            col = RED if v else BLUE
            s += text(cx + colw[i] / 2, ymid, str(v), size=16, color=col, anchor="middle",
                      weight="bold", font=MONO)
            cx += colw[i]

    # підпис рядка прикладу
    yex = y0 + hi * rowh + rowh / 2 + 5
    s += text(x0 + sum(colw) + 16, yex, "← наш приклад", size=13, color=RED, anchor="start",
              weight="bold")

    # нижня нота: правило перевірки
    s += line(60, y0 + 8 * rowh + 26, W - 60, y0 + 8 * rowh + 26, color=FAINT, w=1.5)
    s += text(W / 2, y0 + 8 * rowh + 50,
              "Sum — непарність трьох бітів; Cout = 1, коли одиниць щонайменше дві ("
              "«більшість»).",
              size=13.5, color=INK, anchor="middle", style="italic")
    save("fig-15-6a-2-truthtable.svg", s)


if __name__ == "__main__":
    fig1_netlist()
    fig2_truthtable()
    print("ch15-s6-a gate-simulator figures done.")
