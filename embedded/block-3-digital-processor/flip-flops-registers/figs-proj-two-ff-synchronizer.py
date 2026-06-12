# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.3.8a — «Двотригерний синхронізатор».
Окремий генератор (головний figs.py НЕ чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-16-8a-1-pipeline.svg  — конвеєр FF1→FF2: перший «гасить» метастабільність
                              за цілий період, другий зчитує вже чистий рівень
  fig-16-8a-2-recipe.svg    — рецепт у прошивці/HDL: 1 біт → два тригери;
                              багато біт → рукостискання/FIFO/Грей; головна
                              пастка — НЕ розгалужувати вихід першого тригера
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: символ D-тригера (прямокутник + трикутник такту) ──────────────
def dff(x, y, w, h, title, sub=None, fill="#f4f7ff", stroke=BLUE):
    """D-тригер як блок: ліворуч вхід D, праворуч вихід Q, знизу — клиночок CLK."""
    out = rect(x, y, w, h, fill, stroke, 2, 8)
    out += text(x + w / 2, y + h / 2 - 4, title, 15, stroke, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + h / 2 + 16, sub, 11, GREY, "middle")
    # позначки виводів
    out += text(x + 6, y + 18, "D", 12, INK, "start", "bold")
    out += text(x + w - 6, y + 18, "Q", 12, INK, "end", "bold")
    # клиночок входу такту (трикутник) на нижній грані
    cxm = x + w / 2
    out += polyline([(cxm - 8, y + h), (cxm, y + h - 12), (cxm + 8, y + h)], stroke, 2)
    return out


# ── Фігура 1: конвеєр FF1→FF2 (часова діаграма «гасіння» метастабільності) ───
def fig1_pipeline():
    W, H = 820, 560
    b = header(W, H)
    b += text(W / 2, 30, "Два тригери поспіль: перший приймає удар, другий бачить уже чистий рівень",
              17, INK, "middle", "bold")

    # ── верхня смуга: схема потоку даних ────────────────────────────────────
    yblk = 70
    # асинхронне джерело
    b += rect(40, yblk, 120, 70, "#fff7ec", AMBER, 2, 8)
    b += text(100, yblk + 26, "асинхронний", 13, AMBER, "middle", "bold")
    b += text(100, yblk + 44, "сигнал", 13, AMBER, "middle", "bold")
    b += text(100, yblk + 60, "(не знає такту)", 10, GREY, "middle")

    # FF1
    fx1 = 250
    b += dff(fx1, yblk, 120, 70, "FF1", "буфер удару")
    # FF2
    fx2 = 460
    b += dff(fx2, yblk, 120, 70, "FF2", "чистий вихід", "#eef7ee", GREEN)
    # логіка
    b += rect(670, yblk, 110, 70, "#eef7ee", GREEN, 2, 8)
    b += text(725, yblk + 32, "синхронна", 13, GREEN, "middle", "bold")
    b += text(725, yblk + 50, "логіка", 13, GREEN, "middle", "bold")

    # стрілки потоку
    b += arrow(160, yblk + 35, fx1, yblk + 35, AMBER, 2.2)
    b += arrow(fx1 + 120, yblk + 35, fx2, yblk + 35, INK, 2.2)
    b += text((fx1 + 120 + fx2) / 2, yblk + 24, "м1", 12, RED, "middle", "bold")
    b += text((fx1 + 120 + fx2) / 2, yblk + 58, "(може дзвеніти)", 9, RED, "middle")
    b += arrow(fx2 + 120, yblk + 35, 670, yblk + 35, GREEN, 2.2)
    b += text((fx2 + 120 + 670) / 2, yblk + 24, "м2", 12, GREEN, "middle", "bold")

    # спільний такт під трьома тригерами
    yclk = yblk + 110
    b += line(fx1 + 60, yblk + 82, fx1 + 60, yclk, GREY, 1.6)
    b += line(fx2 + 60, yblk + 82, fx2 + 60, yclk, GREY, 1.6)
    b += line(fx1 + 60, yclk, fx2 + 60, yclk, GREY, 1.6)
    b += text(fx1 + 60, yclk + 16, "спільний такт CLK", 11, GREY, "middle")

    # ── нижня частина: часова діаграма ──────────────────────────────────────
    x0, x1 = 150, 770
    edges = [x0 + 70 + i * 165 for i in range(4)]   # фронти такту 0..3
    base = 230

    def track(y, label):
        out = text(x0 - 12, y + 5, label, 13, INK, "end", "bold")
        for ex in edges:
            out += line(ex, y - 26, ex, y + 26, FAINT, 1)
        return out

    # лінії фронтів через усі доріжки + підписи фронтів
    ylo, yhi = base, base + 240
    for i, ex in enumerate(edges):
        b += line(ex, ylo - 30, ex, yhi + 8, FAINT, 1)
        b += text(ex, ylo - 36, f"фронт {i}", 10, GREY, "middle")

    # CLK
    yCLK = base
    b += track(yCLK, "CLK")
    pts = [(x0, yCLK + 14)]
    for ex in edges:
        pts += [(ex, yCLK + 14), (ex, yCLK - 14), (ex + 22, yCLK - 14), (ex + 22, yCLK + 14)]
    pts += [(x1, yCLK + 14)]
    b += polyline(pts, INK, 2.2)

    # асинхронний вхід: міняється МІЖ фронтами, але край припадає майже на фронт 1
    yA = base + 70
    b += track(yA, "вхід")
    ach = edges[1] - 4     # зміна майже точно на фронті 1 — найгірший випадок
    b += polyline([(x0, yA + 14), (ach, yA + 14), (ach, yA - 14), (x1, yA - 14)], AMBER, 2.4)
    b += text(ach, yA - 22, "край майже на фронті 1", 10, AMBER, "middle")
    b += arrow(ach, yA - 18, ach, yA - 4, AMBER, 1.6)

    # вихід FF1: на фронті 1 ловить край → метастабільний «дзвін», що згасає до фронту 2
    yQ1 = base + 145
    b += track(yQ1, "Q1")
    # до фронту 1 — низький; на фронті 1 — невизначена зона (дзвін), далі високий
    b += polyline([(x0, yQ1 + 14), (edges[1], yQ1 + 14)], BLUE, 2.4)
    # зона невизначеності між фронтом 1 і фронтом 2
    b += rect(edges[1], yQ1 - 16, edges[2] - edges[1], 32, "#fdecec", RED, 1.4, 4)
    # «дзвін» — затухаюча хвиля всередині зони
    ring = [(edges[1], yQ1)]
    span_r = edges[2] - edges[1]
    for k in range(1, 60):
        t = k / 60.0
        amp = 13 * math.exp(-3.2 * t)
        ring.append((edges[1] + t * span_r * 0.62, yQ1 - amp * math.sin(12 * t)))
    ring.append((edges[1] + span_r * 0.62, yQ1 - 14))
    b += polyline(ring, RED, 2.0)
    b += polyline([(edges[1] + span_r * 0.62, yQ1 - 14), (edges[2], yQ1 - 14)], BLUE, 2.4)
    b += text((edges[1] + edges[2]) / 2, yQ1 + 30, "цілий період на «прийти до тями»", 10, RED, "middle")
    b += arrow(edges[1] + 8, yQ1 - 22, edges[1] + 4, yQ1 - 8, RED, 1.4)
    b += text(edges[1] + 10, yQ1 - 26, "удар: можлива метастабільність", 10, RED, "start")

    # вихід FF2: зчитує Q1 на фронті 2 — там уже чисто; видає чистий рівень
    yQ2 = base + 218
    b += track(yQ2, "Q2")
    b += polyline([(x0, yQ2 + 14), (edges[2], yQ2 + 14), (edges[2], yQ2 - 14), (x1, yQ2 - 14)], GREEN, 2.6)
    b += text(edges[2], yQ2 - 22, "фронт 2: Q1 уже визначений → чистий 1", 10, GREEN, "middle")
    b += circle(edges[2], yQ2 - 14, 3.5, GREEN, GREEN, 1)

    b += text(W / 2, yhi + 36, "FF1 поглинає метастабільність і має цілий період CLK, щоб згаснути; "
                               "FF2 зчитує його вже чистим.",
              13, GREEN, "middle", "bold")
    save("fig-16-8a-1-pipeline.svg", b)


# ── Фігура 2: рецепт у прошивці/HDL — 1 біт vs багато біт, головна пастка ────
def fig2_recipe():
    W, H = 820, 540
    b = header(W, H)
    b += text(W / 2, 30, "Рецепт інженера: що заводити двома тригерами, а що — ні",
              17, INK, "middle", "bold")

    # ── ліва колонка: ОДИН біт → два тригери (можна) ─────────────────────────
    lx = 40
    b += rect(lx, 60, 360, 200, "#eef7ee", GREEN, 2, 10)
    b += text(lx + 180, 86, "ОДИН біт рівня/прапорця", 15, GREEN, "middle", "bold")
    b += text(lx + 180, 108, "(кнопка, готовність, дозвіл)", 11, GREY, "middle")
    # маленький конвеєр
    b += dff(lx + 40, 130, 90, 60, "FF1")
    b += dff(lx + 210, 130, 90, 60, "FF2", None, "#eef7ee", GREEN)
    b += arrow(lx + 10, 160, lx + 40, 160, AMBER, 2)
    b += arrow(lx + 130, 160, lx + 210, 160, INK, 2)
    b += arrow(lx + 300, 160, lx + 340, 160, GREEN, 2)
    b += text(lx + 180, 218, "два тригери поспіль — і все.", 12, GREEN, "middle", "bold")
    b += text(lx + 180, 238, "дешево, надійно, MTBF — роки/століття", 11, GREY, "middle")

    # ── права колонка: БАГАТО біт → НЕ два тригери ───────────────────────────
    rx = 420
    b += rect(rx, 60, 360, 200, "#fdecec", RED, 2, 10)
    b += text(rx + 180, 86, "БАГАТО біт (число, лічильник)", 15, RED, "middle", "bold")
    b += text(rx + 180, 108, "поодинці синхронізувати НЕ можна", 11, GREY, "middle")
    # шина 4 біт у 4 пари тригерів → різнобій
    bits_in = ["1", "0", "1", "1"]
    bits_out = ["1", "1", "0", "1"]   # «приїхали» в різні такти → безглуздя
    for i, (a, q) in enumerate(zip(bits_in, bits_out)):
        bx = rx + 30 + i * 82
        b += rect(bx, 132, 34, 26, "#fff", AMBER, 1.6, 4)
        b += text(bx + 17, 151, a, 14, AMBER, "middle", "bold")
        b += arrow(bx + 17, 162, bx + 17, 184, GREY, 1.6)
        col = RED if a != q else BLUE
        b += rect(bx, 186, 34, 26, "#fff", col, 1.6, 4)
        b += text(bx + 17, 205, q, 14, col, "middle", "bold")
    b += text(rx + 180, 232, "біти ловлять різні фронти → проміжне сміття", 11, RED, "middle")
    b += text(rx + 180, 250, "треба: рукостискання · FIFO · код Грея (CDC)", 11, RED, "middle", "bold")

    # ── низ: головна пастка реалізації ───────────────────────────────────────
    py = 300
    b += rect(40, py, 740, 96, "#fff7ec", AMBER, 2, 10)
    b += text(60, py + 26, "Головна пастка на МК/FPGA:", 14, AMBER, "start", "bold")
    b += text(60, py + 48, "вихід ПЕРШОГО тригера (Q1) — «брудний». Його не можна розгалужувати "
                           "в логіку, ні в який", 12, INK, "start")
    b += text(60, py + 66, "інший тригер. Уся схема читає ЛИШЕ вихід ДРУГОГО (Q2). Інакше "
                           "метастабільність «розповзеться».", 12, INK, "start")
    b += text(60, py + 86, "І ще: обидва тригери — в ОДНОМУ тактовому домені приймача, поряд, "
                           "без логіки між ними.", 12, GREEN, "start", "bold")

    # ── зовсім низ: важіль MTBF ──────────────────────────────────────────────
    qy = 416
    b += text(W / 2, qy, "Чим більше «запасу часу» (slack) до фронту FF2 — тим експоненційно "
                         "більший MTBF:", 13, INK, "middle")
    b += text(W / 2, qy + 24, "MTBF = e^(t_r / τ) / ( f_clk · f_data · T_w )",
              16, GREEN, "middle", "bold")
    b += text(W / 2, qy + 46, "хочеш надійніше за тих самих частот — додай ТРЕТІЙ тригер "
                              "(ще один цілий період на згасання).",
              12, GREY, "middle", style="italic")
    save("fig-16-8a-2-recipe.svg", b)


if __name__ == "__main__":
    fig1_pipeline()
    fig2_recipe()
    print("ch16-s8-a-two-ff-synchronizer figures done.")
