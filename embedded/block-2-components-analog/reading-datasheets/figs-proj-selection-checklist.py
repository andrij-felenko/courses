# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки 2.9.7a
«Чеклист вибору компонента: від вимог схеми до параметричного пошуку»
(Розділ 2.9, Модуль 2).

Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r09-7a-…), щоб не перетинатися з головним figs.py розділу
(там зайнято fig-r09-7-1…7-4) та з іншими вставками.
Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREY: "aGrey", GREEN: "aGreen", BLUE: "aBlue"}


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 2.9.7a.1 — конвеєр: вимоги → жорсткі обмеження → фільтр → оцінка ────
def fig_pipeline():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 28, "Конвеєр вибору: від вимог схеми до короткого списку",
              15.5, INK, "middle", "bold")

    # чотири стовпці-етапи
    bx = 28
    bw = 168
    gap = (W - 2 * 28 - 4 * bw) / 3
    ytop = 64
    bh = 360

    cols = [
        (LBLUE, BLUE, "1. Вимоги схеми", [
            "робоча напруга 12 В",
            "струм навантаж. 0.8 А",
            "Tамб до 70 °C",
            "корпус: ручне паяння",
            "+ запас на майбутнє",
        ]),
        (LSUN, SUN, "2. Жорсткі обмеження", [
            "V(max) ≥ 12·1.5 = 18 В",
            "I(max) ≥ 0.8·2 = 1.6 А",
            "Tj(max) ≥ 70 °C +запас",
            "корпус ∈ {TO-220,",
            "  DPAK, SOT-223}",
        ]),
        (LGRN, GREEN, "3. Параметр. фільтр", [
            "база: 50 000 позицій",
            "↓ V, I, Tj, корпус",
            "↓ ціна, наявність",
            "↓ статус (не EOL)",
            "= 23 кандидати",
        ]),
        (LRED, RED, "4. Оцінка й вибір", [
            "score = запас",
            "  − штраф(ціна)",
            "  − штраф(дефіцит)",
            "сортуй ↓ score",
            "= топ-3 у даташит",
        ]),
    ]

    for i, (fill, edge, title, rows) in enumerate(cols):
        x = bx + i * (bw + gap)
        s += rect(x, ytop, bw, bh, fill, edge, 2.2, 10)
        s += rect(x, ytop, bw, 34, edge, edge, 0, 10)
        s += text(x + bw / 2, ytop + 23, title, 12.5, "#ffffff", "middle", "bold")
        yy = ytop + 64
        for r in rows:
            mono = any(c in r for c in "≥∈{}↓=")
            s += text(x + 12, yy, r, 11.5, INK, "start",
                      "normal", "italic" if not mono else "normal")
            yy += 28
        # стрілка між етапами
        if i < 3:
            ax = x + bw + 4
            s += arrow(ax, ytop + bh / 2, ax + gap - 8, ytop + bh / 2, INK, 2.6)

    # підпис-зведення знизу
    s += text(bx + 0.5 * (bw), ytop + bh + 26,
              "розмите →", 11, BLUE, "middle", "bold", "italic")
    s += text(bx + 1.5 * (bw) + gap, ytop + bh + 26,
              "число з запасом →", 11, SUN, "middle", "bold", "italic")
    s += text(bx + 2.5 * (bw) + 2 * gap, ytop + bh + 26,
              "відсіяти неможливе →", 11, GREEN, "middle", "bold", "italic")
    s += text(bx + 3.5 * (bw) + 3 * gap, ytop + bh + 26,
              "ранжувати можливе", 11, RED, "middle", "bold", "italic")
    save("fig-r09-7a-1-pipeline.svg", s)


# ── Рис. 2.9.7a.2 — фільтр як коробка обмежень у просторі параметрів ─────────
def fig_filter_box():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 28, "Фільтр = коробка в просторі параметрів (тут дві осі з багатьох)",
              15, INK, "middle", "bold")

    ox, oy = 96, 360
    pw, ph = 580, 290
    Vmin, Vmax = 0, 60        # вісь напруги, В
    Imin, Imax = 0, 4.0       # вісь струму, А

    def xV(v):
        return ox + pw * (v - Vmin) / (Vmax - Vmin)

    def yI(i):
        return oy - ph * (i - Imin) / (Imax - Imin)

    # осі
    s += arrow(ox, oy, ox, oy - ph - 16, INK, 2)
    s += arrow(ox, oy, ox + pw + 16, oy, INK, 2)
    s += text(ox + pw + 20, oy + 4, "V(max), В", 11.5, INK, "start", "bold")
    s += text(ox - 78, oy - ph - 2, "I(max), А", 11.5, INK, "start", "bold")

    for v in range(0, 61, 10):
        s += line(xV(v), oy, xV(v), oy + 5, INK, 1.2)
        s += text(xV(v), oy + 19, str(v), 9.5, INK, "middle")
    for i in (0, 1, 2, 3, 4):
        s += line(ox - 5, yI(i), ox, yI(i), INK, 1.2)
        s += text(ox - 10, yI(i) + 4, f"{i:.0f}", 9.5, INK, "end")
        s += line(ox, yI(i), ox + pw, yI(i), FAINT, 1)

    # межі-вимоги: V(max) ≥ 18, I(max) ≥ 1.6  → допустима зона праворуч-вгорі
    Vreq, Ireq = 18.0, 1.6
    # явний прямокутник зони «проходить» (V≥Vreq, I≥Ireq)
    zx, zy = xV(Vreq), yI(Imax)
    zw, zh = xV(Vmax) - xV(Vreq), yI(Ireq) - yI(Imax)
    s += rect(zx, zy, zw, zh, LGRN, GREEN, 0, 0)
    # межові лінії
    s += line(xV(Vreq), oy, xV(Vreq), oy - ph, GREEN, 2.2, "6 4")
    s += line(ox, yI(Ireq), ox + pw, yI(Ireq), GREEN, 2.2, "6 4")
    s += text(xV(Vreq) + 6, oy - ph + 16, "V(max) ≥ 18 В", 10.5, GREEN, "start", "bold")
    s += text(ox + pw - 6, yI(Ireq) - 8, "I(max) ≥ 1.6 А", 10.5, GREEN, "end", "bold")
    s += text(xV(40), yI(3.2), "ПРОХОДИТЬ", 13, GREEN, "middle", "bold")
    s += text(xV(40), yI(3.2) + 17, "(є запас по обох осях)", 9.5, GREEN, "middle", style="italic")

    # точки-кандидати (V, I, label, ok?)
    cands = [
        (10, 0.5, "A", False, "замала і V, і I"),
        (20, 1.0, "B", False, "I < 1.6"),
        (30, 1.2, "C", False, "I < 1.6"),
        (24, 2.0, "D", True,  "впритул по V"),
        (40, 2.2, "E", True,  "добрий запас"),
        (55, 3.4, "F", True,  "із надлишком"),
        (12, 2.5, "G", False, "V < 18"),
    ]
    for v, i, lab, ok, note in cands:
        col = GREEN if ok else RED
        s += circle(xV(v), yI(i), 6, col, "#fff", 2.2)
        s += text(xV(v), yI(i) - 11, lab, 10.5, col, "middle", "bold")

    # позначка «впритул» — кандидат D ризиковий
    s += text(xV(24) + 9, yI(2.0) + 4, "D — впритул, без запасу", 9, SUN, "start", "bold")
    s += circle(xV(24), yI(2.0), 9, "none", SUN, 1.6)

    s += text(W / 2, H - 12,
              "Жорсткі пороги (зелені пунктири) рубають простір; що далі вгору-праворуч за порогами — то більший запас.",
              9, GREY, "middle", style="italic")
    save("fig-r09-7a-2-filter-box.svg", s)


if __name__ == "__main__":
    fig_pipeline()
    fig_filter_box()
    print("OK — фігури вставки 2.9.7a згенеровано в", OUT)
