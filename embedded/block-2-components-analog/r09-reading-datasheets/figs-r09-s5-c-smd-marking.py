# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки r09-s5-c-smd-marking (до теми 2.9.5).
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс r09-5c-...), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки marker; sans-serif.
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
LGREY = "#f3f3f3"
LSUN  = "#fbf3df"
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = "Consolas, 'Courier New', monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
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


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.9.5c.1 — анатомія SOT-23 з кодом + чому «маркування ≠ part number»
# ─────────────────────────────────────────────────────────────────────────────
def fig1():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Корпус крихітний — назву не вмістити, тож пишуть КОД",
              17, INK, "middle", "bold")

    # ── ліва панель: малюнок SOT-23 (вид зверху) з трьома ніжками ──
    px, py, pw, ph = 28, 52, 330, 360
    s += rect(px, py, pw, ph, "#ffffff", "#c9d3dc", 1.4, 8)
    s += text(px + pw / 2, py + 22, "SOT-23 (вид зверху), ~3 × 1.3 мм", 13, INK, "middle", "bold")

    # тіло корпусу
    bx, by, bw, bh = px + 90, py + 70, 150, 110
    s += rect(bx, by, bw, bh, "#2a2a2a", "#000000", 2, 6)
    # маркування на корпусі
    s += text(bx + bw / 2, by + bh / 2 + 9, "A7W", 30, "#f2f2f2", "middle", "bold", mono=True)

    # ніжки: 1 і 2 знизу, 3 зверху (стандартна геометрія SOT-23)
    legc = "#c9a24a"
    # pin1 (низ-ліво)
    s += rect(bx + 18, by + bh, 22, 16, legc, "#7a6020", 1.4, 2)
    s += text(bx + 29, by + bh + 34, "1", 13, INK, "middle", "bold")
    # pin2 (низ-право)
    s += rect(bx + bw - 40, by + bh, 22, 16, legc, "#7a6020", 1.4, 2)
    s += text(bx + bw - 29, by + bh + 34, "2", 13, INK, "middle", "bold")
    # pin3 (верх-центр)
    s += rect(bx + bw / 2 - 11, by - 16, 22, 16, legc, "#7a6020", 1.4, 2)
    s += text(bx + bw / 2, by - 24, "3", 13, INK, "middle", "bold")

    # підпис: повна назва не влізла
    s += text(px + pw / 2, py + 250,
              "повна назва — десятки символів,", 12.5, GREY, "middle")
    s += text(px + pw / 2, py + 270,
              "а на корпус влазить 2–3.", 12.5, GREY, "middle")
    s += rect(px + 24, py + 286, pw - 48, 56, LSUN, "#e3d09a", 1.2, 6)
    s += text(px + pw / 2, py + 308, "Тому код «A7W» — це НЕ", 12.5, INK, "middle", "bold")
    s += text(px + pw / 2, py + 326, "part number, а лише його псевдонім.", 12.5, INK, "middle", "bold")

    # ── права панель: код → (виробник + family) → part number ──
    qx, qy, qw, qh = 380, 52, 352, 360
    s += rect(qx, qy, qw, qh, "#ffffff", "#c9d3dc", 1.4, 8)
    s += text(qx + qw / 2, qy + 22, "Чому код неоднозначний", 13, INK, "middle", "bold")

    # центральний код
    cbx = qx + qw / 2
    s += rect(cbx - 45, qy + 44, 90, 40, "#2a2a2a", "#000000", 2, 6)
    s += text(cbx, qy + 70, "A7W", 22, "#f2f2f2", "middle", "bold", mono=True)

    # три стрілки до трьох різних значень (різні виробники)
    rows = [
        ("виробник X", "BAW56  (здвоєний діод)", BLUE),
        ("виробник Y", "транзистор PNP", RED),
        ("виробник Z", "щось третє", GREY),
    ]
    yy = qy + 130
    for label, val, col in rows:
        s += arrow(cbx, qy + 86, qx + 60, yy - 14, col, 1.8)
        s += rect(qx + 56, yy - 12, qw - 84, 36, LGREY, "#d0d0d0", 1.2, 5)
        s += text(qx + 68, yy + 4, label + ":", 12, col, "start", "bold")
        s += text(qx + 68, yy + 20, val, 12.5, INK, "start")
        yy += 56

    s += rect(qx + 20, qy + qh - 56, qw - 40, 42, LRED, "#e3b7b3", 1.2, 6)
    s += text(qx + qw / 2, qy + qh - 38,
              "Той самий код — у різних фірм РІЗНЕ.", 12, RED, "middle", "bold")
    s += text(qx + qw / 2, qy + qh - 22,
              "Спершу впізнай виробника й корпус.", 11.5, INK, "middle")

    save("fig-r09-5c-1-sot23-code.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.9.5c.2 — алгоритм декодування «A7W»: код → корпус → таблиця → part №
# ─────────────────────────────────────────────────────────────────────────────
def fig2():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Як за «A7W» дійти до компонента: ланцюжок кроків",
              17, INK, "middle", "bold")

    # 5 кроків зверху вниз — стрічка
    steps = [
        ("1", "Зчитай код точно", "A7W  (велике A, цифра 7, велике W).\nКрапка/риска = ключ до орієнтації та піна 1.", BLUE),
        ("2", "Зафіксуй корпус", "SOT-23, 3 ніжки. Корпус звужує пошук:\nкод чинний лише в межах свого корпусу.", GREEN),
        ("3", "Знайди виробника", "Логотип/закупівля/контекст плати.\nКод A7W у різних фірм означає різне.", SUN),
        ("4", "Шукай у таблиці кодів", "«SMD codebook» або marking-таблиця в даташиті:\nрядок A7W → ім'я приладу.", INK),
        ("5", "Звір по даташиту", "Відкрий даташит знайденого приладу,\nзвір корпус, ніжки й функцію — щоб не помилитись.", RED),
    ]
    bx, bw = 40, 680
    y = 56
    bh = 66
    gap = 14
    for num, title, body, col in steps:
        s += rect(bx, y, bw, bh, "#ffffff", col, 1.8, 8)
        # номер у кружку
        s += circle(bx + 30, y + bh / 2, 18, col, col, 1)
        s += text(bx + 30, y + bh / 2 + 6, num, 18, "#ffffff", "middle", "bold")
        s += text(bx + 60, y + 24, title, 15, col, "start", "bold")
        for i, ln in enumerate(body.split("\n")):
            s += text(bx + 60, y + 44 + i * 17, ln, 12.5, INK, "start")
        # стрілка вниз до наступного
        if num != "5":
            s += arrow(bx + bw / 2, y + bh + 1, bx + bw / 2, y + bh + gap - 1, GREY, 2)
        y += bh + gap

    save("fig-r09-5c-2-decode-steps.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done.")
