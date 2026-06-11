# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки до теми 2.11.6
«Народження SSR: від ртутних контакторів до оптосимістора» (Модуль 2).
Чистий Python, без залежностей. НЕ чіпає головний figs.py розділу.
Вивід → ./img/ з УНІКАЛЬНИМИ іменами fig-11-6i-hist-*.svg
(секція 6 = історія до теми 6).

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
LGREY = "#f1f1f1"
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
# Рис. 2.11.6i.1 — естафета компонентів, що зійшлися в SSR
#   Bell Labs SCR (1956) + GE triac (~1963) + оптопара → Crydom/IR (1971/1972)
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 30, "SSR не винайшли — його зібрали з готових цеглинок",
              17, INK, "middle", "bold")

    # вісь часу
    ax_y = 250
    s += line(70, ax_y, 850, ax_y, GREY, 2.4)
    for xx in (70, 850):
        s += line(xx, ax_y - 6, xx, ax_y + 6, GREY, 2.4)

    # дві ери: механічна комутація vs твердотільна
    s += rect(70, ax_y - 4, 330, 8, LGREY, GREY, 1.0, 4)
    s += rect(450, ax_y - 4, 400, 8, LBLUE, BLUE, 1.0, 4)
    s += text(235, ax_y + 70, "МЕХАНІЧНА КОМУТАЦІЯ  (контакти, ртуть)",
              12.5, "#6a6a6a", "middle", "bold")
    s += text(650, ax_y + 70, "ТВЕРДОТІЛЬНА КОМУТАЦІЯ  (кремній + світло)",
              12.5, BLUE, "middle", "bold")

    def node(cx, year, title, lines, col, up=True):
        out = circle(cx, ax_y, 6, col, col, 1)
        block = [title] + lines
        n = len(block)
        if up:
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

    s += node(135, "до 1950-х", "реле й контактори:",
              ["котушка тягне контакт;", "ртутний контактор —", "ртуть замість металу"], "#6a6a6a", up=True)
    s += node(330, "1956", "SCR у Bell Labs:",
              ["кремнієва защіпка", "(одна півхвиля)"], RED, up=False)
    s += node(470, "~1963", "Triac (GE):",
              ["защіпка на ОБИДВІ", "півхвилі — ключ для AC"], GREEN, up=True)
    s += node(610, "~1960-ті", "оптопара:",
              ["світлодіод + фото-", "приймач = розв'язка"], SUN, up=False)
    s += node(770, "1971/72", "Crydom (у складі",
              ["International Rectifier):", "перший SSR — і серія,", "що стала стандартом"], BLUE, up=True)

    s += text(W / 2, H - 14,
              "Triac дав безконтактний ключ для змінного струму, оптопара — гальванічну розв'язку; "
              "Crydom поєднала їх в один корпус.",
              12, GREY, "middle", "italic")
    save("fig-11-6i-hist-timeline.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.11.6i.2 — три покоління «реле»: EMR → ртутний контактор → SSR
#   Що замінили: рухомий контакт → ртуть → промінь світла + симістор
# ─────────────────────────────────────────────────────────────────────────────
def fig_three_relays():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 30, "Три способи замкнути коло командою — і що в кожному «зношується»",
              16, INK, "middle", "bold")

    colx = [165, 460, 755]
    boxw, boxh = 230, 250
    boxy = 60
    for x in colx:
        s += rect(x - boxw / 2, boxy, boxw, boxh, "#ffffff", GREY, 1.4, 8)

    # ── (1) Електромеханічне реле ──
    cx = colx[0]
    s += text(cx, boxy + 26, "Електромеханічне", 14, INK, "middle", "bold")
    s += text(cx, boxy + 44, "реле / контактор", 14, INK, "middle", "bold")
    # котушка
    coil_x = cx - 60
    for i in range(4):
        s += circle(coil_x, boxy + 80 + i * 16, 8, "none", COPP, 2)
    s += text(coil_x - 18, boxy + 78, "котушка", 11, COPP, "end")
    # якір + контакт
    piv = (cx + 6, boxy + 90)
    s += line(piv[0], piv[1], cx + 60, boxy + 120, INK, 3)        # рухомий важіль
    s += circle(piv[0], piv[1], 3.5, INK, INK, 1)
    s += circle(cx + 58, boxy + 122, 4, RED, RED, 1)              # рухомий контакт
    s += line(cx + 30, boxy + 150, cx + 80, boxy + 150, INK, 3)   # нерухомий контакт
    s += circle(cx + 55, boxy + 150, 4, INK, "none", 0)
    s += text(cx, boxy + 188, "метал б'є по металу", 11.5, INK, "middle")
    s += text(cx, boxy + 210, "зношується:", 12, RED, "middle", "bold")
    s += text(cx, boxy + 228, "контакти — іскра,", 11.5, RED, "middle")
    s += text(cx, boxy + 244, "дребезг, обгорання", 11.5, RED, "middle")

    # ── (2) Ртутний контактор ──
    cx = colx[1]
    s += text(cx, boxy + 26, "Ртутний контактор", 14, INK, "middle", "bold")
    s += text(cx, boxy + 44, "(mercury relay)", 12, GREY, "middle", "italic")
    # скляна трубка з ртуттю
    tx, ty, tw, th = cx - 22, boxy + 64, 44, 120
    s += rect(tx, ty, tw, th, "#ffffff", INK, 1.6, 10)
    s += rect(tx + 2, ty + th - 46, tw - 4, 44, "#cfcfd6", GREY, 1, 8)  # калюжа ртуті
    s += text(cx, ty + th - 20, "Hg", 14, "#5a5a66", "middle", "bold")
    # залізний плунжер
    s += rect(cx - 7, ty + 22, 14, 30, "#9a9aa2", INK, 1.2, 3)
    s += text(cx + 30, ty + 36, "плунжер", 10.5, GREY, "start")
    s += text(cx, boxy + 196, "ртуть змочує контакт —", 11.5, INK, "middle")
    s += text(cx, boxy + 212, "немає іскри й дребезгу,", 11.5, GREEN, "middle")
    s += text(cx, boxy + 230, "великі струми; але отруйна,", 11.5, RED, "middle")
    s += text(cx, boxy + 246, "боїться нахилу й морозу", 11.5, RED, "middle")

    # ── (3) SSR ──
    cx = colx[2]
    s += text(cx, boxy + 26, "Твердотільне реле (SSR)", 13.5, BLUE, "middle", "bold")
    # світлодіод
    ledx = cx - 62
    s += rect(ledx - 16, boxy + 70, 32, 26, LSUN, SUN, 1.4, 4)
    s += text(ledx, boxy + 88, "LED", 10.5, "#9a7a1e", "middle", "bold")
    # промінь
    s += arrow(ledx + 18, boxy + 83, cx + 6, boxy + 83, SUN, 2.2)
    s += text((ledx + cx) / 2 + 2, boxy + 72, "світло", 10.5, "#9a7a1e", "middle")
    # фотоприймач + симістор
    s += rect(cx + 8, boxy + 66, 60, 34, LGRN, GREEN, 1.4, 4)
    s += _wrap(cx + 38, boxy + 82, ["фото +", "симістор"], 10, GREEN, "middle", 12)
    s += text(cx, boxy + 130, "розрив — це повітря", 11.5, INK, "middle")
    s += text(cx, boxy + 148, "(гальванічна розв'язка)", 11, GREY, "middle")
    s += text(cx, boxy + 178, "нема рухомих частин:", 12, GREEN, "middle", "bold")
    s += text(cx, boxy + 196, "тихо, без іскри, мільйони", 11.5, GREEN, "middle")
    s += text(cx, boxy + 212, "циклів; але гріється і", 11.5, RED, "middle")
    s += text(cx, boxy + 228, "має струм витоку у «вимк.»", 11.5, RED, "middle")

    # стрілки еволюції
    s += arrow(colx[0] + boxw / 2 + 4, boxy + boxh / 2, colx[1] - boxw / 2 - 4, boxy + boxh / 2, GREY, 2)
    s += arrow(colx[1] + boxw / 2 + 4, boxy + boxh / 2, colx[2] - boxw / 2 - 4, boxy + boxh / 2, GREY, 2)

    s += text(W / 2, H - 14,
              "Спільне завдання — замкнути силове коло слабкою командою; різниця — у тому, що саме рухається й що зношується.",
              12, GREY, "middle", "italic")
    save("fig-11-6i-hist-three-relays.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_three_relays()
    print("done.")
