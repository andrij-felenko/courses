# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.7.6a — «Відкритий тулчейн: Yosys → nextpnr →
бітстрім для iCE40».

ОКРЕМИЙ генератор лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python без залежностей. Вивід → ./img/.
Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — §3.7.6a.k → файли fig-r07-s6a-k-*.

Фігури:
  fig-r07-s6a-1-pipeline.svg  — конвеєр інструментів: що кожен крок З'ЇДАЄ і що ВИДАЄ
  fig-r07-s6a-2-placeroute.svg— що насправді роблять place&route: нетліст → фізична сітка
  fig-r07-s6a-3-anneal.svg    — серце алгоритму: відпал (swap → Δвартість → прийняти/відкинути)
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
VIOL  = "#7a3ea8"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", AMBER: "aAmber", VIOL: "aViol"}


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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Фігура 1: конвеєр інструментів — що кожен крок З'ЇДАЄ і що ВИДАЄ ───────────
def fig1_pipeline():
    W, H = 880, 560
    b = header(W, H)
    b += text(W/2, 30, "Відкритий конвеєр: чотири окремі інструменти, кожен зі своїм входом і виходом",
              17, INK, "middle", "bold")

    # Колонка етапів: вхідний артефакт (зверху) → інструмент (рамка) → вихідний артефакт
    stages = [
        ("Verilog (.v)", "опис заліза\n(§3.7.5)", VIOL,
         "Yosys", "СИНТЕЗ", "звести опис\nдо LUT і тригерів", GREEN),
        ("нетліст (.json)", "граф із LUT,\nтригерів, зв'язків", GREEN,
         "nextpnr", "РОЗМІЩЕННЯ +\nТРАСУВАННЯ", "посадити на сітку\nчипа, протягти дроти", BLUE),
        ("ASCII-розкладка\n(.asc)", "що в якій клітинці\nі куди йдуть дроти", BLUE,
         "icepack", "ПАКУВАННЯ", "у двійковий\nбітстрім", AMBER),
        ("бітстрім (.bin)", "конфіг для\nкомірок чипа", AMBER,
         "iceprog", "ПРОШИВКА", "залити у флеш\nпо USB", RED),
    ]

    n = len(stages)
    colw = (W - 60) / n
    tool_y = 250
    tool_h = 96
    art_top_y = 90
    art_h = 70
    out_y = tool_y + tool_h + 40

    tool_centers = []
    for i, (a_nm, a_sub, a_col, t_nm, t_phase, t_role, t_col) in enumerate(stages):
        cx = 30 + colw * i + colw / 2

        # вхідний артефакт (для першого — справжній вхід; для решти = вихід попереднього,
        # тож малюємо лише для першого, інші стрілкою «успадковуються»)
        if i == 0:
            ax, ay, aw = cx - 78, art_top_y, 156
            b += rect(ax, ay, aw, art_h, "#faf5ff", a_col, 2, 8)
            for k, ln in enumerate(a_nm.split("\n")):
                b += mono(cx, ay + 22 + k*15, ln, 13, a_col, "middle", "bold")
            for k, ln in enumerate(a_sub.split("\n")):
                b += text(cx, ay + 40 + k*12, ln, 9.5, GREY, "middle")
            b += arrow(cx, ay + art_h, cx, tool_y, GREY, 2)

        # інструмент
        tx, ty, tw = cx - 78, tool_y, 156
        b += rect(tx, ty, tw, tool_h, "#ffffff", t_col, 2.6, 10)
        b += rect(tx, ty, tw, 26, t_col, t_col, 0, 10)
        b += text(cx, ty + 18, t_nm, 14, "#ffffff", "middle", "bold")
        ph = t_phase.split("\n")
        py = ty + 44 if len(ph) > 1 else ty + 48
        for ln in ph:
            b += text(cx, py, ln, 11, t_col, "middle", "bold")
            py += 14
        ry = ty + tool_h - 22 if len(t_role.split("\n")) > 1 else ty + tool_h - 12
        for ln in t_role.split("\n"):
            b += text(cx, ry, ln, 9.5, GREY, "middle")
            ry += 11
        tool_centers.append((cx, tx, tw))

        # вихідний артефакт (його назва = вхідний артефакт наступного етапу)
        ox, oy, ow = cx - 78, out_y, 156
        b += rect(ox, oy, ow, art_h, "#f6f6f6", t_col, 1.8, 8)
        out_name = stages[i+1][0] if i+1 < n else "бітстрім у чипі"
        out_sub = stages[i+1][1] if i+1 < n else "FPGA піднялася,\nDONE=1 (§3.7.1c)"
        b += arrow(cx, ty + tool_h, cx, oy, GREY, 2)
        for k, ln in enumerate(out_name.split("\n")):
            b += mono(cx, oy + 22 + k*15, ln, 13, t_col, "middle", "bold")
        for k, ln in enumerate(out_sub.split("\n")):
            b += text(cx, oy + 40 + k*12, ln, 9.5, GREY, "middle")

        # коротка дугова стрілка «передачі» від виходу до наступного інструмента
        if i < n - 1:
            nx = 30 + colw * (i + 1) + colw / 2          # центр наступної колонки
            ymid = (oy + art_h + tool_y) / 2 + 18
            b += path(f"M {ox + ow:.1f} {oy + art_h/2:.1f} "
                      f"Q {(ox + ow + nx - 78)/2:.1f} {ymid:.1f} {nx - 78:.1f} {tool_y + tool_h/2:.1f}",
                      GREY, 1.6, dash="4,4")

    # підпис-висновок
    b += line(40, H - 92, W - 40, H - 92, FAINT, 1)
    b += text(W/2, H - 66,
              "Жоден крок не «магія»: кожен бере текстовий файл і пише наступний — усе можна відкрити й прочитати.",
              12.5, INK, "middle")
    b += text(W/2, H - 42,
              "Те, що у фірмовому пакеті сховано в одній кнопці «Generate Bitstream», тут — чотири прозорі утиліти.",
              12.5, GREEN, "middle", "bold")
    b += text(W/2, H - 20,
              "Це конкретне втілення загального потоку теми §3.7.6: синтез → розміщення → трасування → бітстрім.",
              11.5, GREY, "middle", style="italic")
    save("fig-r07-s6a-1-pipeline.svg", b)


# ── Фігура 2: що роблять place & route — нетліст → фізична сітка ──────────────
def fig2_placeroute():
    W, H = 880, 520
    b = header(W, H)
    b += text(W/2, 28, "Серце nextpnr: абстрактний нетліст лягає на фізичну сітку чипа",
              17, INK, "middle", "bold")

    # ── Ліворуч: нетліст (логічний граф) ──
    b += text(200, 64, "1. Нетліст від Yosys", 14, GREEN, "middle", "bold")
    b += text(200, 82, "(що з чим з'єднано — без географії)", 10, GREY, "middle", style="italic")

    # вузли графа
    nodes = {
        "A": (90, 130, "LUT", VIOL),
        "B": (90, 230, "LUT", VIOL),
        "C": (210, 180, "LUT", VIOL),
        "D": (210, 300, "DFF", BLUE),
        "E": (330, 230, "LUT", VIOL),
    }
    edges = [("A", "C"), ("B", "C"), ("C", "E"), ("C", "D"), ("D", "E")]
    for a, c in edges:
        x1, y1 = nodes[a][0], nodes[a][1]
        x2, y2 = nodes[c][0], nodes[c][1]
        b += line(x1, y1, x2, y2, GREY, 1.6)
    for k, (x, y, lab, col) in nodes.items():
        b += circle(x, y, 22, "#fff", col, 2.2)
        b += text(x, y - 1, lab, 11, col, "middle", "bold")
        b += text(x, y + 12, k, 9, GREY, "middle")

    # стрілка-перехід
    b += arrow(380, 230, 470, 230, INK, 2.6)
    b += text(425, 218, "place", 11, INK, "middle", "bold")
    b += text(425, 244, "& route", 11, INK, "middle", "bold")

    # ── Праворуч: фізична сітка плиток iCE40 ──
    gx, gy = 500, 95
    cols, rows = 6, 6
    cell = 52
    b += text(gx + cols*cell/2, 64, "2. Фізична сітка плиток iCE40", 14, BLUE, "middle", "bold")
    b += text(gx + cols*cell/2, 82, "(кожна клітинка — реальне місце на кристалі, §3.7.4)", 10, GREY, "middle", style="italic")

    # плитки
    for r in range(rows):
        for c in range(cols):
            x = gx + c*cell
            y = gy + r*cell
            b += rect(x, y, cell-6, cell-6, "#fcfcfc", FAINT, 1.2, 4)
    # межова рамка
    b += rect(gx-4, gy-4, cols*cell, rows*cell, "none", INK, 1.6, 6)

    # «посаджені» вузли у конкретні плитки (placement)
    placed = {
        "A": (0, 1, VIOL), "B": (0, 3, VIOL),
        "C": (2, 2, VIOL), "D": (3, 4, BLUE), "E": (4, 2, VIOL),
    }
    centers = {}
    for k, (c, r, col) in placed.items():
        x = gx + c*cell + (cell-6)/2
        y = gy + r*cell + (cell-6)/2
        centers[k] = (x, y)
        b += rect(gx + c*cell, gy + r*cell, cell-6, cell-6, "#fff",
                  col, 2.2, 4)
        b += text(x, y - 1, placed_label(k), 10, col, "middle", "bold")
        b += text(x, y + 12, k, 8, GREY, "middle")

    # «протягнуті» дроти (routing) — ламані по каналах між плитками
    def route(a, c, col):
        x1, y1 = centers[a]
        x2, y2 = centers[c]
        midx = (x1 + x2) / 2
        return polyline([(x1, y1), (midx, y1), (midx, y2), (x2, y2)], col, 2.2)
    b += route("A", "C", GREEN)
    b += route("B", "C", GREEN)
    b += route("C", "E", RED)
    b += route("C", "D", GREEN)
    b += route("D", "E", AMBER)

    # легенда під сіткою
    ly = gy + rows*cell + 26
    b += text(gx + cols*cell/2, ly, "Розміщення — який вузол у яку плитку; трасування — якими каналами тягнуться дроти.",
              11, INK, "middle")
    b += text(gx + cols*cell/2, ly + 18, "Довгий звивистий дріт = більша затримка (звідси і критичний шлях, §3.7.7).",
              11, GREY, "middle", style="italic")

    # нижня смуга з двома підзадачами
    by = H - 96
    b += rect(70, by, 360, 64, "#f0fff2", GREEN, 1.8, 8)
    b += text(250, by + 22, "Розміщення (placement)", 12, GREEN, "middle", "bold")
    b += text(250, by + 42, "куди сісти кожному LUT/DFF, щоб пов'язані", 10, INK, "middle")
    b += text(250, by + 56, "були поруч — інакше дроти довгі", 10, INK, "middle")

    b += rect(W - 430, by, 360, 64, "#f4f7ff", BLUE, 1.8, 8)
    b += text(W - 250, by + 22, "Трасування (routing)", 12, BLUE, "middle", "bold")
    b += text(W - 250, by + 42, "провести всі зв'язки наявними каналами,", 10, INK, "middle")
    b += text(W - 250, by + 56, "не зіткнувшись — дротів обмаль", 10, INK, "middle")
    save("fig-r07-s6a-2-placeroute.svg", b)


def placed_label(k):
    return "DFF" if k == "D" else "LUT"


# ── Фігура 3: серце алгоритму — імітація відпалу для розміщення ───────────────
def fig3_anneal():
    W, H = 880, 540
    b = header(W, H)
    b += text(W/2, 28, "Як nextpnr шукає гарне розміщення: імітація відпалу (simulated annealing)",
              16, INK, "middle", "bold")

    # ── Ліворуч: цикл прийняття/відкидання swap ──
    cx0 = 60
    boxw = 300
    steps = [
        ("Поміняти місцями два вузли", "(пробний swap у сітці)", VIOL, 70),
        ("Порахувати Δвартість", "вартість = довжина дротів + штраф\nза порушений таймінг", BLUE, 150),
        ("Стало краще (Δ < 0)?", "так → лишити;  ні → лишити\nз імовірністю e^(−Δ/T)", AMBER, 240),
        ("Трохи остудити: T ← α·T", "що холодніше — то рідше\nприймаємо погіршення", RED, 340),
    ]
    for nm, sub, col, y in steps:
        b += rect(cx0, y, boxw, 60, "#ffffff", col, 2.2, 9)
        b += text(cx0 + boxw/2, y + 24, nm, 12.5, col, "middle", "bold")
        for k, ln in enumerate(sub.split("\n")):
            b += text(cx0 + boxw/2, y + 42 + k*13, ln, 9.5, GREY, "middle")
    for i in range(len(steps) - 1):
        y1 = steps[i][3] + 60
        y2 = steps[i+1][3]
        b += arrow(cx0 + boxw/2, y1, cx0 + boxw/2, y2, GREY, 2)
    # петля назад нагору
    b += polyline([(cx0 + boxw/2, steps[-1][3] + 60),
                   (cx0 + boxw/2, steps[-1][3] + 80),
                   (cx0 - 22, steps[-1][3] + 80),
                   (cx0 - 22, steps[0][3] + 30),
                   (cx0, steps[0][3] + 30)], GREEN, 2)
    b += text(cx0 - 16, (steps[0][3] + steps[-1][3])/2 + 30,
              "повторити", 10, GREEN, "middle", style="italic")
    # позначка кінця
    b += text(cx0 + boxw/2, steps[-1][3] + 100,
              "…доки T не охолоне (тисячі–мільйони спроб)", 10, INK, "middle", style="italic")

    # ── Праворуч: чому приймаємо погіршення — крива «вартості» з ямами ──
    px, py, pw, ph = 470, 90, 360, 230
    b += rect(px, py, pw, ph, "#fcfcfc", FAINT, 1.4, 8)
    b += text(px + pw/2, py - 12, "Навіщо інколи приймати гірший варіант", 13, INK, "middle", "bold")
    # осі
    b += arrow(px + 16, py + ph - 24, px + pw - 12, py + ph - 24, INK, 1.6)
    b += arrow(px + 16, py + ph - 24, px + 16, py + 14, INK, 1.6)
    b += text(px + pw - 12, py + ph - 8, "розкладка", 10, GREY, "end")
    b += text(px + 22, py + 12, "вартість", 10, GREY, "start")
    # хвиляста крива з локальним і глобальним мінімумом
    pts = []
    for t in range(0, 101):
        xx = px + 16 + (pw - 40) * t / 100
        u = t / 100 * 3.0
        val = math.sin(u * 2.1) * 0.5 + 0.55 * u - 0.18 * math.sin(u * 5.0)
        yy = py + ph - 30 - val * 42
        pts.append((xx, yy))
    b += polyline(pts, INK, 2.4)
    # локальний мінімум (пастка)
    lm = pts[22]
    b += circle(lm[0], lm[1], 5, AMBER, AMBER, 1)
    b += text(lm[0], lm[1] - 12, "локальна яма", 9.5, AMBER, "middle", "bold")
    b += text(lm[0], lm[1] - 0, "(пастка)", 9, AMBER, "middle")
    # глобальний мінімум
    gm = min(pts, key=lambda p: p[1])
    b += circle(gm[0], gm[1], 5, GREEN, GREEN, 1)
    b += text(gm[0] + 4, gm[1] + 20, "справжній мінімум", 9.5, GREEN, "middle", "bold")
    # стрибок через горб
    hi = pts[33]
    b += path(f"M {lm[0]:.1f} {lm[1]:.1f} Q {(lm[0]+gm[0])/2:.1f} {hi[1]-46:.1f} {gm[0]:.1f} {gm[1]:.1f}",
              RED, 2, dash="5,4")
    b += text((lm[0]+gm[0])/2, hi[1] - 52, "інколи лізти ВГОРУ,", 9.5, RED, "middle", "bold")
    b += text((lm[0]+gm[0])/2, hi[1] - 40, "щоб вибратися з пастки", 9.5, RED, "middle")

    # внизу праворуч — складність
    by = py + ph + 28
    b += rect(px, by, pw, 96, "#fff7ec", AMBER, 1.8, 8)
    b += text(px + pw/2, by + 22, "Чому це не «миттєво»", 12.5, AMBER, "middle", "bold")
    b += text(px + 14, by + 44, "• Розміщення й трасування — NP-важкі: точного", 10.5, INK, "start")
    b += text(px + 14, by + 60, "  оптимуму за прийнятний час нема — лише добре", 10.5, INK, "start")
    b += text(px + 14, by + 76, "  наближення (відпал, евристики). Звідси й секунди–", 10.5, INK, "start")
    b += text(px + 14, by + 92, "  хвилини збірки навіть малого дизайну.", 10.5, INK, "start")

    # підпис-висновок унизу
    b += text(W/2, H - 14,
              "Та сама ідея відпалу, що в металургії: гаряче — рухається вільно, холодне — застигає у вигідній формі.",
              11.5, GREEN, "middle", "bold")
    save("fig-r07-s6a-3-anneal.svg", b)


if __name__ == "__main__":
    fig1_pipeline()
    fig2_placeroute()
    fig3_anneal()
    print("r07-s6-a-open-toolchain figures done.")
