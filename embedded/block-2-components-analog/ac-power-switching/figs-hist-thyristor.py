# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки до Розділу 2.11
«Від тиратрона до тиристора» (Модуль 2). Чистий Python, без залежностей.
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
fig-11-0i-hist-*.svg (секція 0 = історія до розділу).

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділів модуля 2.
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#f8efd6"
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


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(x, y, lines, size=12.5, color=INK, anchor="middle", lh=16, weight="normal"):
    s = ""
    for i, ln in enumerate(lines):
        s += text(x, y + i * lh, ln, size, color, anchor, weight)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.11.0i.1 — хронологія: від газового тиратрона до кремнієвого тиристора
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Силова комутація: від газової лампи до кремнію",
              17, INK, "middle", "bold")

    # вісь часу
    ax_y = 250
    s += line(70, ax_y, 830, ax_y, GREY, 2.4)
    for xx in (70, 830):
        s += line(xx, ax_y - 6, xx, ax_y + 6, GREY, 2.4)

    # дві ери: вакуумно-газова (тепло, скло) vs твердотільна (кремній)
    s += rect(70, ax_y - 4, 360, 8, LSUN, SUN, 1.0, 4)
    s += rect(470, ax_y - 4, 360, 8, LBLUE, BLUE, 1.0, 4)
    s += text(250, ax_y + 64, "ЕРА ГАЗОВИХ ЛАМП  (скло, розжарений катод, ртуть)",
              12.5, "#9a7a1e", "middle", "bold")
    s += text(650, ax_y + 64, "ЕРА КРЕМНІЮ  (твердотільні ключі)",
              12.5, BLUE, "middle", "bold")

    # події: (x, рік, заголовок[, рядки], колір, угору?)
    def node(cx, year, title, lines, col, up=True):
        out = circle(cx, ax_y, 6, col, col, 1)
        block = [title] + lines
        n = len(block)
        if up:
            # текст стоїть НАД віссю, останній рядок — за 14 px від лінії, рік ще вище
            bottom = ax_y - 16
            top_line = bottom - (n - 1) * 14
            out += line(cx, ax_y - 6, cx, bottom + 4, col, 1.6, "3,3")
            out += text(cx, top_line - 14, year, 14, col, "middle", "bold")
            out += _wrap(cx, top_line, block, 11.5, INK, "middle", 14)
        else:
            ty = ax_y + 26
            out += line(cx, ax_y + 6, cx, ty - 6, col, 1.6, "3,3")
            out += text(cx, ty + 14 + n * 14 + 6, year, 14, col, "middle", "bold")
            out += _wrap(cx, ty + 14, block, 11.5, INK, "middle", 14)
        return out

    s += node(140, "~1914", "Ленгмюр і Мікл (GE):",
              ["кероване випрямлення", "в газовій лампі"], "#9a7a1e", up=True)
    s += node(300, "~1928", "Тиратрон Галла (GE):",
              ["сітка вмикає дугу —", "перший кер. ключ сили"], "#9a7a1e", up=False)
    s += node(430, "1956", "Bell Labs:",
              ["PNPN-перемикач", "(Молл, Танненбаум,", "Голді, Голоняк)"], RED, up=True)
    s += node(560, "1957", "GE, Клайд (NY):",
              ["+ третій вивід (затвор)", "SCR — Голл, Гутцвіллер", "перші 2 шт., липень"], GREEN, up=False)
    s += node(760, ">1960-ті", "тиристор витісняє",
              ["тиратрон; IEC робить", "«thyristor» = thyratron", "+ transistor"], BLUE, up=True)

    # підпис-зв'язок назви
    s += text(W / 2, H - 14,
              "Назва thyristor зшила обидві ери: «thyra» (грец. «брама/двері») від тиратрона + «-tor» від transistor",
              12, GREY, "middle", "italic")
    save("fig-11-0i-hist-timeline.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.11.0i.2 — чому PNPN «защіпується»: пара транзисторів зі зворотним зв'язком
# ─────────────────────────────────────────────────────────────────────────────
def fig_latch():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Защіпка: чотири шари = два транзистори, що тримають один одного",
              16, INK, "middle", "bold")

    # ── ЛІВОРУЧ: чотиришаровий стовпчик P-N-P-N ──
    cx = 150
    top = 70
    layer_h = 58
    layers = [("P", LRED, RED, "анод (A)"),
              ("N", LBLUE, BLUE, ""),
              ("P", LRED, RED, "затвор (G)"),
              ("N", LBLUE, BLUE, "катод (K)")]
    bw = 120
    for i, (lab, fill, edge, term) in enumerate(layers):
        y = top + i * layer_h
        s += rect(cx - bw / 2, y, bw, layer_h, fill, edge, 1.8)
        s += text(cx, y + layer_h / 2 + 6, lab, 22, edge, "middle", "bold")
        if term:
            tx = cx + bw / 2 + 14
            s += line(cx + bw / 2, y + layer_h / 2, tx, y + layer_h / 2, INK, 2)
            s += text(tx + 6, y + layer_h / 2 + 5, term, 12.5, INK, "start", "bold")
    # анодний вивід угору
    s += line(cx - bw / 2, top + layer_h / 2, cx - bw / 2 - 24, top + layer_h / 2, INK, 2)
    s += text(cx - bw / 2 - 28, top + layer_h / 2 + 5, "анод (A)", 12.5, INK, "end", "bold")
    s += text(cx, top + 4 * layer_h + 26, "чотири шари P-N-P-N", 13, INK, "middle", "bold")
    s += text(cx, top + 4 * layer_h + 46, "(три переходи)", 12, GREY, "middle")

    # стрілка «те саме, що →»
    s += arrow(cx + 130, top + 2 * layer_h, cx + 210, top + 2 * layer_h, INK, 2.4)
    s += text(cx + 170, top + 2 * layer_h - 12, "те саме, що", 12.5, INK, "middle", "italic")

    # ── ПРАВОРУЧ: два транзистори навхрест (PNP над NPN) ──
    # PNP (Q1) угорі, NPN (Q2) нижче; колектор кожного живить базу іншого.
    ax = 560  # вертикаль «анод-катод»
    ay_top = 80
    ay_bot = 350
    s += line(ax, ay_top, ax, ay_bot, INK, 2)
    s += circle(ax, ay_top, 4, INK, INK, 1)
    s += text(ax, ay_top - 10, "анод (A)  +", 13, RED, "middle", "bold")
    s += circle(ax, ay_bot, 4, INK, INK, 1)
    s += text(ax, ay_bot + 22, "катод (K)  −", 13, BLUE, "middle", "bold")

    # Q1 (PNP) — кружок
    q1x, q1y = ax, 150
    s += circle(q1x, q1y, 30, "#ffffff", RED, 2.2)
    s += text(q1x, q1y + 5, "Q1", 15, RED, "middle", "bold")
    s += text(q1x + 40, q1y - 22, "PNP", 12.5, RED, "start", "bold")
    # Q2 (NPN) — кружок
    q2x, q2y = ax, 280
    s += circle(q2x, q2y, 30, "#ffffff", BLUE, 2.2)
    s += text(q2x, q2y + 5, "Q2", 15, BLUE, "middle", "bold")
    s += text(q2x + 40, q2y + 26, "NPN", 12.5, BLUE, "start", "bold")

    # зворотний зв'язок: колектор Q1 → база Q2 і колектор Q2 → база Q1
    fbx = ax + 120
    # Q1 колектор (низ) -> Q2 база (бік)
    s += arrow(q1x + 22, q1y + 20, fbx, q1y + 20, RED, 2)
    s += line(fbx, q1y + 20, fbx, q2y - 4, RED, 2)
    s += arrow(fbx, q2y - 4, q2x + 28, q2y - 8, RED, 2)
    s += text(fbx + 8, (q1y + q2y) / 2 - 6, "струм Q1", 11.5, RED, "start", "bold")
    s += text(fbx + 8, (q1y + q2y) / 2 + 10, "→ база Q2", 11.5, RED, "start")

    # Q2 колектор (верх) -> Q1 база (бік) — лівий контур
    fbx2 = ax - 120
    s += arrow(q2x - 22, q2y - 20, fbx2, q2y - 20, BLUE, 2)
    s += line(fbx2, q2y - 20, fbx2, q1y + 4, BLUE, 2)
    s += arrow(fbx2, q1y + 4, q1x - 28, q1y + 8, BLUE, 2)
    s += text(fbx2 - 8, (q1y + q2y) / 2 - 6, "струм Q2", 11.5, BLUE, "end", "bold")
    s += text(fbx2 - 8, (q1y + q2y) / 2 + 10, "→ база Q1", 11.5, BLUE, "end")

    # затвор: імпульс у базу Q2
    gx = ax + 200
    s += arrow(gx, q2y + 36, q2x + 30, q2y + 12, GREEN, 2.4)
    s += text(gx + 4, q2y + 50, "імпульс на затвор", 12, GREEN, "start", "bold")
    s += text(gx + 4, q2y + 66, "(одна іскра — і все)", 11.5, GREEN, "start")

    # підпис-висновок
    s += text(W / 2, H - 14,
              "Кожен транзистор живить базу іншого: відкрився один — відкрив другий — той ще дужче відкрив перший. "
              "Раз спалахнувши, защіпка тримається сама.",
              12, GREY, "middle", "italic")
    save("fig-11-0i-hist-latch.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_latch()
    print("done.")
