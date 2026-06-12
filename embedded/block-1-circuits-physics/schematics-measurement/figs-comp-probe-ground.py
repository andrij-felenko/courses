# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки §1.6.8 «Земля щупа — це земля розетки».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-6-8c-probe-ground-*.svg), щоб не зачепити головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів — Рис. 1.6.8c.k (продовження 🔌-серії до теми 1.6.8 після CAT-вставки).
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
COPPER = "#cf8b5e"
ORANGE = "#e08030"
YELLOW = "#f4c430"
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
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange"}


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


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def earth_symbol(x, y, color=INK, s=1.0):
    """Символ захисної землі (три спадні риски)."""
    out = line(x, y, x, y + 10 * s, color, 2.2)
    out += line(x - 13 * s, y + 10 * s, x + 13 * s, y + 10 * s, color, 2.4)
    out += line(x - 8 * s, y + 15 * s, x + 8 * s, y + 15 * s, color, 2.4)
    out += line(x - 3.5 * s, y + 20 * s, x + 3.5 * s, y + 20 * s, color, 2.4)
    return out


def signal_gnd(x, y, color=INK, s=1.0):
    """Символ сигнальної землі (трикутник зі смужок)."""
    out = line(x, y, x, y + 8 * s, color, 2)
    out += polygon([(x - 11 * s, y + 8 * s), (x + 11 * s, y + 8 * s), (x, y + 20 * s)],
                   fill="none", stroke=color, sw=2)
    return out


def spark(cx, cy, color=RED, s=1.0):
    """Зірочка-іскра."""
    pts = []
    import math as _m
    for i in range(16):
        ang = i * _m.pi / 8
        r = (12 if i % 2 == 0 else 5) * s
        pts.append((cx + r * _m.cos(ang), cy + r * _m.sin(ang)))
    return polygon(pts, fill=color)


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ───────────────────────── Рис. 1.6.8c.4 — механізм аварії ─────────────────────────
def fig_short():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 26, "Чому «крокодил» на «гарячій» точці = коротке через осцилограф",
              size=16, anchor="middle", weight="bold")

    # ── досліджуваний пристрій: мережевий блок без розв'язки (hot chassis) ──
    dx, dy, dw, dh = 60, 70, 270, 250
    s += rect(dx, dy, dw, dh, fill="#fff6f3", stroke=RED, sw=2, rx=8)
    s += text(dx + dw / 2, dy + 22, "Пристрій від мережі без розв'язки",
              size=13.5, anchor="middle", weight="bold", color=RED)
    s += text(dx + dw / 2, dy + 40, "(дешевий БЖ, інвертор, TRIAC-димер)",
              size=11.5, anchor="middle", color=GREY, style="italic")

    # розетка 230 В зліва (L / N)
    lx = dx + 26
    s += text(lx - 4, dy + 78, "L  ~230 В", size=12, color=INK, weight="bold")
    s += text(lx - 4, dy + 150, "N", size=12, color=INK, weight="bold")
    s += line(lx, dy + 84, lx, dy + 144, INK, 2.4)        # L шина
    s += circle(lx, dy + 84, 3.2, fill=INK, stroke=INK)
    s += circle(lx, dy + 144, 3.2, fill=INK, stroke=INK)

    # випрямляч → внутрішня «земля» приладу, що НЕ збігається із землею мережі
    rgx = dx + 110
    s += rect(rgx, dy + 90, 60, 48, fill="#ffffff", stroke=INK, sw=1.8, rx=4)
    s += text(rgx + 30, dy + 112, "≈", size=18, anchor="middle", color=INK)
    s += text(rgx + 30, dy + 130, "вузол", size=10, anchor="middle", color=GREY)
    s += line(lx, dy + 84, rgx, dy + 100, INK, 2.2)
    s += line(lx, dy + 144, rgx, dy + 128, INK, 2.2)

    # внутрішній «нуль» приладу — плаваюча точка, потенціал відносно землі мережі ~115 В
    nodex, nodey = dx + 230, dy + 150
    s += line(rgx + 60, dy + 114, nodex, dy + 114, INK, 2.4)
    s += line(nodex, dy + 114, nodex, nodey, INK, 2.4)
    s += circle(nodex, nodey, 5.5, fill=YELLOW, stroke=INK, w=2)
    s += text(nodex + 10, nodey - 6, "«нуль» приладу", size=11.5, color=INK, weight="bold")
    s += text(nodex + 10, nodey + 10, "плаває: ≈ +115 В", size=11.5, color=RED, weight="bold")
    s += text(nodex + 10, nodey + 26, "відносно землі мережі", size=10.5, color=GREY)

    # ── осцилограф справа ──
    ox, oy, ow, oh = 540, 70, 170, 150
    s += rect(ox, oy, ow, oh, fill="#f3f6ff", stroke=BLUE, sw=2, rx=8)
    s += text(ox + ow / 2, oy + 22, "Осцилограф", size=13.5, anchor="middle", weight="bold", color=BLUE)
    # екран
    s += rect(ox + 18, oy + 34, ow - 36, 60, fill="#0c1430", stroke=INK, sw=1.5, rx=4)
    s += polyline([(ox + 24, oy + 80), (ox + 50, oy + 80), (ox + 50, oy + 48),
                   (ox + 96, oy + 48), (ox + 96, oy + 80), (ox + 132, oy + 80)],
                  color="#46d27a", w=2)
    # вхід BNC: центр (червоний щуп) і екран = земля приладу = земля мережі
    s += text(ox + ow / 2, oy + 116, "земля каналу = корпус", size=10.5, anchor="middle", color=INK)
    s += text(ox + ow / 2, oy + 132, "= захисна земля розетки", size=10.5, anchor="middle", color=GREEN, weight="bold")

    # ── щупи від осцилографа до пристрою ──
    # червоний (центр): на нульовий вузол приладу — це коректний бік
    s += arrow(ox + 18, oy + 70, nodex + 6, nodey, RED, 2.6)
    s += text(ox - 8, oy + 58, "червоний", size=11, anchor="end", color=RED, weight="bold")

    # «крокодил» (земля щупа) — помилково на «гарячу» точку
    cgx, cgy = dx + 110, dy + 100  # клемимо на верхню (мережеву) шину приладу
    s += line(ox + 22, oy + 92, ox + 22, 360, GREEN, 3)
    s += line(ox + 22, 360, cgx - 16, 360, GREEN, 3)
    s += arrow(cgx - 16, 360, rgx, dy + 102, GREEN, 3)
    s += text(ox + 30, 354, "«крокодил» (земля щупа) ➜ помилково на мережеву точку",
              size=11.5, color=GREEN, weight="bold")

    # ── фатальний контур: через корпус → захисну землю розетки → назад у мережу ──
    eax, eay = ox + ow / 2, 250
    s += line(ox + ow / 2, oy + oh, eax, eay, GREEN, 3)
    s += earth_symbol(eax, eay, color=GREEN, s=1.1)
    s += text(eax + 22, eay + 10, "захисна земля (PE)", size=11.5, color=GREEN, weight="bold")
    s += text(eax + 22, eay + 26, "розетки → нейтраль мережі", size=10.5, color=GREY)

    # стрілки контуру короткого
    s += spark(rgx + 2, dy + 100, color=RED, s=1.3)
    s += text(W / 2, 420, "Контур: «гаряча» точка → крокодил → корпус → захисна земля → нейтраль мережі",
              size=12.5, anchor="middle", color=RED, weight="bold")
    s += text(W / 2, 442, "опір контуру ≈ 0 → струм у сотні ампер: згоряє слід щупа, вхід, а то й сам прилад",
              size=12, anchor="middle", color=INK)
    s += text(W / 2, 460, "(а якщо плаває не прилад, а пристрій — під напругою опиняється корпус осцилографа)",
              size=10.5, anchor="middle", color=GREY, style="italic")

    save("fig-6-8c-probe-ground-1-short.svg", s + footer())


# ───────────────────────── Рис. 1.6.8c.5 — три правильні шляхи ─────────────────────────
def fig_solutions():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 26, "Як поміряти «гарячу» точку безпечно — і чого НЕ робити",
              size=16, anchor="middle", weight="bold")

    col_w = 240
    xs = [30, 290, 540]
    cy, ch = 50, 250

    # ── 1. Диференційний щуп ──
    x = xs[0]
    s += rect(x, cy, col_w, ch, fill="#f2fbf4", stroke=GREEN, sw=2, rx=8)
    s += text(x + col_w / 2, cy + 24, "Диференційний щуп", size=14, anchor="middle", weight="bold", color=GREEN)
    s += text(x + col_w / 2, cy + 42, "(зшито з §2.11.9)", size=11, anchor="middle", color=GREY, style="italic")
    # два входи + / −, віднімач, вихід на BNC землею приладу
    px = x + 40
    s += circle(px, cy + 90, 4, fill=RED, stroke=RED)
    s += circle(px, cy + 130, 4, fill=BLUE, stroke=BLUE)
    s += text(px - 8, cy + 86, "+", size=15, anchor="end", color=RED, weight="bold")
    s += text(px - 8, cy + 138, "−", size=15, anchor="end", color=BLUE, weight="bold")
    s += line(px, cy + 90, px + 35, cy + 90, RED, 2.2)
    s += line(px, cy + 130, px + 35, cy + 130, BLUE, 2.2)
    s += polygon([(px + 35, cy + 74), (px + 35, cy + 146), (px + 95, cy + 110)],
                 fill="#ffffff", stroke=INK, sw=2)
    s += text(px + 58, cy + 114, "−", size=18, anchor="middle", color=INK)
    s += line(px + 95, cy + 110, px + 130, cy + 110, INK, 2.4)
    s += arrow(px + 130, cy + 110, px + 150, cy + 110, INK, 2.4)
    s += text(px + 150, cy + 106, "BNC", size=10.5, color=INK)
    s += text(x + col_w / 2, cy + 175, "міряє РІЗНИЦЮ двох точок;", size=11.5, anchor="middle", color=INK)
    s += text(x + col_w / 2, cy + 192, "обидва входи — високоомні,", size=11.5, anchor="middle", color=INK)
    s += text(x + col_w / 2, cy + 209, "землі мережі не торкаються", size=11.5, anchor="middle", color=GREEN, weight="bold")
    s += text(x + col_w / 2, cy + 232, "✔ верхній ключ, мережа, ½-міст", size=11, anchor="middle", color=GREEN, weight="bold")

    # ── 2. Розв'язувальний трансформатор на пристрій ──
    x = xs[1]
    s += rect(x, cy, col_w, ch, fill="#f2fbf4", stroke=GREEN, sw=2, rx=8)
    s += text(x + col_w / 2, cy + 24, "Розв'язати ПРИСТРІЙ", size=14, anchor="middle", weight="bold", color=GREEN)
    s += text(x + col_w / 2, cy + 42, "трансформатором 1:1", size=11, anchor="middle", color=GREY, style="italic")
    # дві котушки + сердечник
    cxs = x + 70
    cys = cy + 100
    for k in range(4):
        s += f'<path d="M {cxs} {cys + k*16} a 8 8 0 0 1 0 16" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    for k in range(4):
        s += f'<path d="M {cxs + 40} {cys + k*16} a 8 8 0 0 0 0 16" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += line(cxs + 18, cys - 6, cxs + 18, cys + 70, GREY, 2)
    s += line(cxs + 22, cys - 6, cxs + 22, cys + 70, GREY, 2)
    s += text(cxs - 14, cys - 12, "мережа", size=10.5, anchor="middle", color=INK)
    s += text(cxs + 54, cys - 12, "пристрій", size=10.5, anchor="middle", color=INK)
    s += text(x + col_w / 2, cy + 192, "пристрій тепер «плаває»,", size=11.5, anchor="middle", color=INK)
    s += text(x + col_w / 2, cy + 209, "нема жорсткого зв'язку із землею", size=11.5, anchor="middle", color=GREEN, weight="bold")
    s += text(x + col_w / 2, cy + 232, "✔ землю щупа вже можна чіпляти", size=11, anchor="middle", color=GREEN, weight="bold")

    # ── 3. Розв'язаний осцилограф ──
    x = xs[2]
    s += rect(x, cy, col_w, ch, fill="#f2fbf4", stroke=GREEN, sw=2, rx=8)
    s += text(x + col_w / 2, cy + 24, "Розв'язаний осцилограф", size=14, anchor="middle", weight="bold", color=GREEN)
    s += text(x + col_w / 2, cy + 42, "акумуляторний / батарейний", size=11, anchor="middle", color=GREY, style="italic")
    s += rect(x + 60, cy + 80, 120, 70, fill="#ffffff", stroke=BLUE, sw=2, rx=6)
    s += rect(x + 72, cy + 92, 96, 34, fill="#0c1430", stroke=INK, sw=1.2, rx=3)
    s += polyline([(x + 78, cy + 118), (x + 100, cy + 118), (x + 100, cy + 100),
                   (x + 140, cy + 100), (x + 140, cy + 118), (x + 162, cy + 118)],
                  color="#46d27a", w=1.8)
    # батарея
    s += line(x + 96, cy + 158, x + 96, cy + 168, INK, 2)
    s += line(x + 86, cy + 168, x + 106, cy + 168, INK, 3)
    s += line(x + 90, cy + 174, x + 102, cy + 174, INK, 2)
    s += text(x + 120, cy + 172, "🔋 без шнура в розетку", size=10.5, color=INK)
    s += text(x + col_w / 2, cy + 200, "нема корпусного зв'язку", size=11.5, anchor="middle", color=INK)
    s += text(x + col_w / 2, cy + 217, "із землею мережі", size=11.5, anchor="middle", color=GREEN, weight="bold")
    s += text(x + col_w / 2, cy + 238, "✔ портативні скопи, USB у ноут на акумуляторі", size=10, anchor="middle", color=GREEN, weight="bold")

    # ── анти-рішення внизу ──
    ay = cy + ch + 30
    s += rect(30, ay, W - 60, 64, fill="#fff6f3", stroke=RED, sw=2, rx=8)
    s += spark(58, ay + 32, color=RED, s=1.0)
    s += text(82, ay + 26, "НІКОЛИ: висмикнути/перерізати штир захисної землі осцилографа («підняти землю»)",
              size=13, color=RED, weight="bold")
    s += text(82, ay + 47, "Так і справді нема контуру короткого — але тоді ВЕСЬ корпус приладу опиняється під «гарячим»",
              size=11.5, color=INK)
    s += text(82, ay + 63, "потенціалом: смертельна пастка для рук. Розв'язують ПРИСТРІЙ або беруть диф-щуп, землю приладу не чіпають.",
              size=11.5, color=INK)

    save("fig-6-8c-probe-ground-2-solutions.svg", s + footer())


if __name__ == "__main__":
    fig_short()
    fig_solutions()
    print("done")
