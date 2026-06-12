# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 2.11.6c
«Твердотільне реле SSR-40DA-класу».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

УНІКАЛЬНІ імена файлів (fig-r11-6c-*), щоб не зачіпати головний figs.py розділу
й інші окремі скрипти вставок.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 2.11.6c.k.
Допоміжні функції скопійовано з figs.py попередніх розділів (єдиний вигляд).
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
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMBER = "#fdf3e0"
AMBER = "#c9881e"
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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def _path(pts, col, wv=2.4, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="{fill}" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def _area(pts, fill, stroke="none", wv=0):
    s = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ' stroke="none"'
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" '
            f'fill="{fill}"{s}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.6c.1 — що всередині SSR-40DA: керувальний бік (3–32 В DC, світлодіод),
#  оптична межа, детектор нуля, силовий TRIAC + RC-снабер, тепловідвідна підошва.
# ─────────────────────────────────────────────────────────────────────────────
def fig1_inside():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 28, "Що всередині SSR-40DA: оптична межа ділить два світи", 16, INK, "middle", "bold")

    # вертикальна оптична межа ізоляції
    xb = 360
    s += line(xb, 70, xb, 392, AMBER, 2.4, dash="7,5")
    s += text(xb, 60, "оптична розв'язка (§2.5.10)", 12, AMBER, "middle", "bold")

    # ── ЛІВИЙ бік: керування (DC) ──
    s += rect(40, 80, 300, 312, "#fbfbfb", FAINT, 1.4, 10)
    s += text(190, 102, "керувальний бік — постійний струм", 12.5, BLUE, "middle", "bold")

    # клеми 3 і 4 (вхід керування)
    s += circle(70, 150, 7, LBLUE, BLUE, 2)
    s += text(70, 138, "3 (+)", 11, RED, "middle", "bold")
    s += circle(70, 230, 7, LBLUE, BLUE, 2)
    s += text(70, 252, "4 (−)", 11, BLUE, "middle", "bold")

    # обмежувальний резистор (вбудований) + світлодіод
    s += line(77, 150, 130, 150, INK, 2)
    s += rect(130, 142, 42, 16, "#ffffff", INK, 1.8)
    s += text(151, 154, "R", 11, INK, "middle", "bold")
    s += text(151, 132, "вбуд.", 9.5, GREY, "middle")
    s += line(172, 150, 215, 150, INK, 2)
    # світлодіод (трикутник + риска) у керувальному плечі
    s += _area([(215, 142), (215, 158), (231, 150)], LRED, RED, 1.8)
    s += line(231, 142, 231, 158, RED, 2.2)
    s += arrow(236, 138, 248, 126, RED, 1.6)
    s += arrow(240, 144, 252, 132, RED, 1.6)
    s += text(223, 176, "світлодіод", 10.5, RED, "middle")
    # назад до клеми 4
    s += line(231, 150, 231, 230, INK, 2)
    s += line(231, 230, 77, 230, INK, 2)

    # підпис діапазону входу
    s += text(190, 300, "3–32 В DC · ≈ 10 мА", 12, INK, "middle", "bold")
    s += text(190, 322, "логіка / реле / ШІМ", 11, GREY, "middle", "italic")
    s += text(190, 360, "ізольовано від мережі:", 11, GREEN, "middle", "italic")
    s += text(190, 376, "МК у безпеці", 11, GREEN, "middle", "italic")

    # ── ПРАВИЙ бік: силовий (AC) ──
    s += rect(380, 80, 400, 312, "#fffdf8", FAINT, 1.4, 10)
    s += text(580, 102, "силовий бік — мережа AC", 12.5, RED, "middle", "bold")

    # фотоприймач + детектор нуля
    s += _area([(404, 142), (404, 158), (420, 150)], LRED, RED, 1.8)  # фототриак-приймач
    s += line(420, 142, 420, 158, RED, 2.2)
    s += arrow(396, 126, 405, 138, AMBER, 1.6)
    s += arrow(400, 132, 409, 144, AMBER, 1.6)
    s += text(420, 178, "фото-", 10, INK, "middle")
    s += text(420, 190, "приймач", 10, INK, "middle")

    # блок детектора нуля
    s += rect(452, 132, 92, 38, LGRN, GREEN, 1.8, 6)
    s += text(498, 148, "детектор", 10.5, GREEN, "middle", "bold")
    s += text(498, 162, "нуля", 10.5, GREEN, "middle", "bold")
    s += arrow(432, 150, 450, 150, INK, 1.8)
    s += text(498, 186, "версія «D»: вмикає", 9.5, GREY, "middle", "italic")
    s += text(498, 198, "лише біля 0 В", 9.5, GREY, "middle", "italic")

    # силовий TRIAC (символ: два зустрічні трикутники + затвор)
    tx, ty = 600, 150
    s += _area([(tx - 16, ty - 16), (tx + 16, ty - 16), (tx, ty)], "#ffffff", INK, 2)
    s += _area([(tx - 16, ty + 16), (tx + 16, ty + 16), (tx, ty)], "#ffffff", INK, 2)
    s += line(tx - 16, ty - 16, tx + 16, ty + 16, INK, 2)
    s += line(tx, ty - 28, tx, ty - 16, INK, 2)
    s += line(tx, ty + 16, tx, ty + 28, INK, 2)
    s += arrow(552, 150, tx - 18, 150, INK, 1.8)  # запуск затвора
    s += line(tx - 18, 150, tx - 18, ty + 6, INK, 2)
    s += line(tx - 18, ty + 6, tx - 6, ty + 6, INK, 2)
    s += text(tx + 30, ty + 4, "TRIAC", 11.5, INK, "start", "bold")
    s += text(tx + 30, ty + 20, "(або 2×SCR)", 10, GREY, "start")

    # RC-снабер паралельно силовому ключу
    s += line(tx, ty - 28, 690, ty - 28, GREY, 1.8)
    s += rect(684, ty - 8, 12, 26, "#ffffff", GREY, 1.6)  # R снабера
    s += text(706, ty - 2, "R", 10, GREY, "start")
    s += line(690, ty + 18, 690, ty + 30, GREY, 1.8)
    s += line(682, ty + 30, 698, ty + 30, GREY, 2.2)  # C снабера
    s += line(682, ty + 36, 698, ty + 36, GREY, 2.2)
    s += line(690, ty + 36, 690, ty + 60, GREY, 1.8)
    s += line(690, ty + 60, tx, ty + 60, GREY, 1.8)
    s += line(tx, ty + 28, tx, ty + 60, GREY, 1.8)
    s += text(720, ty + 22, "RC-снабер", 10, GREY, "start", "italic")
    s += text(720, ty + 36, "(dv/dt, §2.11.8)", 9.5, GREY, "start", "italic")

    # силові клеми 1 і 2 (вихід ~)
    s += line(tx, ty - 28, tx, 118, INK, 2)
    s += line(tx, 118, 760, 118, INK, 2)
    s += circle(760, 118, 7, LRED, RED, 2)
    s += text(760, 106, "1 ~", 11, RED, "middle", "bold")
    s += line(tx, ty + 60, tx, 360, INK, 2)
    s += line(tx, 360, 760, 360, INK, 2)
    s += circle(760, 360, 7, LRED, RED, 2)
    s += text(760, 382, "2 ~", 11, RED, "middle", "bold")
    s += text(610, 345, "навантаження + мережа 230 В", 11, RED, "middle", "italic")

    # тепловідвідна підошва (металева основа корпусу)
    s += rect(380, 404, 400, 22, "#dfe3e6", GREY, 1.6, 4)
    s += text(580, 419, "металева підошва → радіатор обов'язковий (Рис. 2.11.6c.2)", 11, INK, "middle", "bold")
    s += line(595, 392, 595, 404, GREY, 1.4, dash="3,3")

    save("fig-r11-6c-1-inside.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.6c.2 — чому радіатор: падіння ~1.2 В × струм = ват тепла, і реальний
#  безперервний струм без радіатора в рази нижчий за «40 А» на корпусі.
# ─────────────────────────────────────────────────────────────────────────────
def fig2_heat():
    W, H = 780, 460
    s = header(W, H)
    s += text(W / 2, 28, "Чому «40 А» вимагає радіатора: тепло = падіння × струм", 15.5, INK, "middle", "bold")

    ox, oy = 95, 360
    plot_w = 470
    plot_h = 290

    Imax = 40.0     # вісь струму, А
    Pmax = 60.0     # вісь потужності, Вт
    Vdrop = 1.2     # типове падіння на відкритому TRIAC, В

    def X(i):
        return ox + plot_w * i / Imax

    def Y(p):
        return oy - plot_h * p / Pmax

    # сітка горизонталі (потужність)
    for p in range(0, int(Pmax) + 1, 15):
        y = Y(p)
        s += line(ox, y, ox + plot_w, y, FAINT, 1.2)
        s += text(ox - 10, y + 4, f"{p}", 11, GREY, "end")
    s += text(ox - 58, Y(Pmax) - 14, "тепло P, Вт", 12.5, INK, "start", "bold")
    # сітка вертикалі (струм)
    for i in range(0, int(Imax) + 1, 10):
        x = X(i)
        s += line(x, oy, x, Y(Pmax), FAINT, 1.2)
        s += text(x, oy + 22, f"{i} А", 11, GREY, "middle")
    s += text(ox + plot_w + 6, oy + 5, "струм I", 12, INK, "start", "bold")

    # осі
    s += arrow(ox, oy, ox, Y(Pmax) - 16, INK, 1.8)
    s += arrow(ox, oy, ox + plot_w + 14, oy, INK, 1.8)

    # пряма P = Vdrop * I (червона) — лінійне зростання тепла
    s += _path([(X(0), Y(0)), (X(Imax), Y(Vdrop * Imax))], RED, 3.0)
    s += text(X(40), Y(Vdrop * 40) - 12, "P ≈ 1.2 В × I", 12.5, RED, "end", "bold")

    # межа розсіювання БЕЗ радіатора (горизонталь ~3 Вт)
    Pnohs = 3.0
    s += line(ox, Y(Pnohs), ox + plot_w, Y(Pnohs), BLUE, 1.8, dash="6,4")
    s += text(ox + 8, Y(Pnohs) - 6, "межа без радіатора (~3 Вт)", 11, BLUE, "start", "italic")
    # точка перетину → струм без радіатора
    i_nohs = Pnohs / Vdrop
    s += line(X(i_nohs), oy, X(i_nohs), Y(Pnohs), BLUE, 1.6, dash="3,3")
    s += circle(X(i_nohs), Y(Pnohs), 4.5, BLUE, INK, 1.6)
    s += text(X(i_nohs) + 6, oy - 6, f"≈{i_nohs:.1f} А", 11, BLUE, "start", "bold")

    # межа з великим радіатором (горизонталь ~48 Вт)
    Phs = 48.0
    s += line(ox, Y(Phs), ox + plot_w, Y(Phs), GREEN, 1.8, dash="6,4")
    s += text(ox + 8, Y(Phs) - 6, "межа з великим радіатором", 11, GREEN, "start", "italic")
    i_hs = Phs / Vdrop
    i_hs = min(i_hs, Imax)
    s += line(X(i_hs), oy, X(i_hs), Y(Phs), GREEN, 1.6, dash="3,3")
    s += circle(X(i_hs), Y(Phs), 4.5, GREEN, INK, 1.6)
    s += text(X(i_hs) - 6, oy - 6, f"аж до {Imax:.0f} А", 11, GREEN, "end", "bold")

    # позначка «40 А на корпусі» — лише з радіатором + обдувом
    s += circle(X(40), Y(Vdrop * 40), 5, RED, INK, 1.8)
    s += text(X(40) - 8, Y(Vdrop * 40) + 18, "48 Вт!", 11.5, RED, "end", "bold")

    # підсумкова рамка-висновок
    s += rect(ox + 150, Y(Pmax) + 6, 300, 70, LAMBER, AMBER, 1.6, 8)
    s += text(ox + 160, Y(Pmax) + 28, "«40 А» — лише на масивному", 11.5, INK, "start", "bold")
    s += text(ox + 160, Y(Pmax) + 44, "радіаторі з обдувом. Без радіатора", 11.5, INK, "start")
    s += text(ox + 160, Y(Pmax) + 60, "чесні лише одиниці ампер.", 11.5, INK, "start")

    save("fig-r11-6c-2-heat.svg", s)


if __name__ == "__main__":
    fig1_inside()
    fig2_heat()
    print("done")
