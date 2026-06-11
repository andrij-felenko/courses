# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ВСТАВКИ §1.10.3c — «Іскровий проміжок і газовий розрядник (GDT)».
ОКРЕМИЙ скрипт (не головний figs.py розділу), з УНІКАЛЬНИМИ іменами файлів у ./img/.
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з розділів модуля (за §9 — кожен скрипт самодостатній).
Нумерація фігур: Рис. 1.10.3c.k.
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
PURPLE = "#7a3fb0"
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
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})" stroke-linecap="round"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{r}{d}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = '"Consolas","SF Mono",monospace' if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="{fill}" stroke="{color}" stroke-width="{w}"{d} stroke-linejoin="round"/>\n'


def zigzag(x1, y1, x2, y2, n=6, amp=6, color=ORANGE, w=2.4):
    """Іскра/блискавка: ламана лінія між двома точками."""
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux  # нормаль
    pts = [(x1, y1)]
    for i in range(1, n):
        t = i / n
        off = amp if (i % 2 == 0) else -amp
        bx = x1 + dx * t + nx * off
        by = y1 + dy * t + ny * off
        pts.append((bx, by))
    pts.append((x2, y2))
    return polyline(pts, color=color, w=w)


# ─────────────────────────────────────────────────────────────────────────
# Рис. 1.10.3c.1 — два пристрої поруч: відкритий іскровий проміжок vs GDT,
# і де вони стоять (лінія → земля), плюс «вольт-секундна» суть.
# ─────────────────────────────────────────────────────────────────────────
def fig_devices():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Один принцип — два корпуси: іскра в повітрі та іскра в запаяній колбі",
              size=18, anchor="middle", weight="bold")

    # ── ЛІВА панель: відкритий іскровий проміжок ─────────────────────────
    lx = 40
    s += rect(lx, 55, 410, 270, fill="#fbfbfb", stroke=FAINT, sw=1.5, rx=10)
    s += text(lx + 205, 80, "Іскровий проміжок (spark gap)", size=15, anchor="middle", weight="bold")
    s += text(lx + 205, 100, "просто два електроди в повітрі", size=12.5, anchor="middle",
              color=GREY, style="italic")

    # два вістря назустріч
    ex = lx + 205
    eyt, eyb = 135, 255
    gap_t, gap_b = 172, 218
    # верхній електрод (лінія, +)
    s += line(ex, eyt, ex, gap_t, color=INK, w=8)
    s += line(ex - 16, gap_t, ex + 16, gap_t, color=INK, w=3)  # верхня площинка вістря (трикутник)
    s += f'<path d="M {ex-14:.1f},{gap_t:.1f} L {ex+14:.1f},{gap_t:.1f} L {ex:.1f},{gap_t+10:.1f} Z" fill="{INK}"/>\n'
    # нижній електрод (земля)
    s += line(ex, gap_b, ex, eyb, color=INK, w=8)
    s += f'<path d="M {ex-14:.1f},{gap_b:.1f} L {ex+14:.1f},{gap_b:.1f} L {ex:.1f},{gap_b-10:.1f} Z" fill="{INK}"/>\n'
    # іскра в проміжку
    s += zigzag(ex, gap_t + 10, ex, gap_b - 10, n=5, amp=7, color=ORANGE, w=3)

    # підписи виводів
    s += line(ex, eyt, lx + 60, eyt, color=RED, w=2.5)
    s += circle(lx + 60, eyt, 4, fill=RED, stroke=RED)
    s += text(lx + 54, eyt - 8, "лінія / антена", size=12.5, color=RED, anchor="end")
    s += line(ex, eyb, lx + 60, eyb, color=BLUE, w=2.5)
    s += circle(lx + 60, eyb, 4, fill=BLUE, stroke=BLUE)
    s += text(lx + 54, eyb + 16, "земля", size=12.5, color=BLUE, anchor="end")

    s += text(ex + 28, gap_t + 12, "зазор", size=12, color=ORANGE)
    s += text(ex + 28, gap_t + 28, "(повітря)", size=11, color=GREY)

    s += text(lx + 205, 300, "Дешево, грубо. Працює, але іскрить на повітрі,", size=11.5,
              anchor="middle", color=INK)
    s += text(lx + 205, 316, "псується, ловить пил і вологу.", size=11.5, anchor="middle", color=INK)

    # ── ПРАВА панель: GDT ────────────────────────────────────────────────
    rx0 = 490
    s += rect(rx0, 55, 410, 270, fill="#fbfbfb", stroke=FAINT, sw=1.5, rx=10)
    s += text(rx0 + 205, 80, "Газовий розрядник (GDT)", size=15, anchor="middle", weight="bold")
    s += text(rx0 + 205, 100, "той самий зазор, але в запаяній колбі з газом", size=12.5,
              anchor="middle", color=GREY, style="italic")

    # колба (циліндр)
    cbx, cby, cbw, cbh = rx0 + 110, 130, 190, 110
    s += rect(cbx, cby, cbw, cbh, fill="#eef4ff", stroke=INK, sw=2.5, rx=14)
    # два дискові електроди всередині
    s += rect(cbx + 18, cby + 20, 22, cbh - 40, fill=GREY, stroke=INK, sw=2, rx=3)
    s += rect(cbx + cbw - 40, cby + 20, 22, cbh - 40, fill=GREY, stroke=INK, sw=2, rx=3)
    # газ + розряд між дисками
    s += text(cbx + cbw / 2, cby + 24, "Ne / Ar", size=11, anchor="middle", color=PURPLE,
              style="italic")
    s += zigzag(cbx + 42, cby + cbh / 2, cbx + cbw - 42, cby + cbh / 2, n=6, amp=8,
                color=ORANGE, w=3)
    # тьмяне світіння газу
    s += f'<ellipse cx="{cbx+cbw/2:.1f}" cy="{cby+cbh/2:.1f}" rx="48" ry="22" fill="{ORANGE}" opacity="0.12"/>\n'

    # виводи
    s += line(cbx, cby + cbh / 2, rx0 + 60, cby + cbh / 2, color=RED, w=3)
    s += circle(rx0 + 60, cby + cbh / 2, 4, fill=RED, stroke=RED)
    s += text(rx0 + 54, cby + cbh / 2 - 8, "лінія", size=12.5, color=RED, anchor="end")
    s += line(cbx + cbw, cby + cbh / 2, rx0 + 360, cby + cbh / 2, color=BLUE, w=3)
    s += circle(rx0 + 360, cby + cbh / 2, 4, fill=BLUE, stroke=BLUE)
    s += text(rx0 + 366, cby + cbh / 2 - 8, "земля", size=12.5, color=BLUE, anchor="start")

    s += text(rx0 + 205, 300, "Газ і тиск підібрані під потрібну напругу спрацювання;", size=11.5,
              anchor="middle", color=INK)
    s += text(rx0 + 205, 316, "герметично, без зносу від повітря. Тримає тисячі ампер.", size=11.5,
              anchor="middle", color=INK)

    # ── НИЖНІЙ блок: де стоїть (схема) ────────────────────────────────────
    by = 360
    s += rect(40, by - 8, 860, 95, fill="none", stroke=FAINT, sw=1.5, rx=10)
    s += text(60, by + 14, "Де стоїть: ПОПЕРЕК (паралельно) між лінією та землею — у нормі «нікого нема»",
              size=13.5, weight="bold")

    # лінійка: джерело сплеску → вузол → навантаження ; GDT вниз на землю
    ay = by + 55
    s += text(70, ay - 18, "сплеск", size=12, color=ORANGE, anchor="middle")
    s += zigzag(70, ay - 12, 70, ay, n=3, amp=4, color=ORANGE, w=2.2)
    s += line(70, ay, 760, ay, color=INK, w=3)  # лінія
    s += circle(420, ay, 4.5, fill=INK, stroke=INK)  # вузол
    # GDT-символ (два трикутники назустріч у колі) вниз
    gy1, gy2 = ay + 8, ay + 38
    s += line(420, ay, 420, gy1, color=INK, w=2.5)
    s += circle(420, (gy1 + gy2) / 2, 15, fill="#eef4ff", stroke=INK, sw=2)
    s += f'<path d="M {408:.1f},{(gy1+gy2)/2-6:.1f} L {420:.1f},{(gy1+gy2)/2-6:.1f} L {414:.1f},{(gy1+gy2)/2:.1f} Z" fill="{INK}"/>\n'
    s += f'<path d="M {420:.1f},{(gy1+gy2)/2+6:.1f} L {432:.1f},{(gy1+gy2)/2+6:.1f} L {426:.1f},{(gy1+gy2)/2:.1f} Z" fill="{INK}"/>\n'
    s += line(420, gy2, 420, gy2 + 12, color=BLUE, w=2.5)
    # символ землі
    s += line(404, gy2 + 12, 436, gy2 + 12, color=BLUE, w=3)
    s += line(410, gy2 + 17, 430, gy2 + 17, color=BLUE, w=2.5)
    s += line(415, gy2 + 22, 425, gy2 + 22, color=BLUE, w=2)
    s += text(444, (gy1 + gy2) / 2 + 4, "GDT", size=12.5, weight="bold")
    # навантаження
    s += rect(745, ay - 18, 30, 36, fill="#fff", stroke=INK, sw=2, rx=3)
    s += text(800, ay + 4, "схема,", size=12, anchor="start")
    s += text(800, ay + 20, "яку бережемо", size=12, anchor="start")

    s += footer()
    with open(os.path.join(OUT, "fig-r10-s3c-1-spark-gdt-devices.svg"), "w", encoding="utf-8") as f:
        f.write(s)


# ─────────────────────────────────────────────────────────────────────────
# Рис. 1.10.3c.2 — поведінка в часі: дотле спрацювання тримає високу напругу,
# після пробою «складається» до напруги дуги (crowbar), і проблема follow-current.
# ─────────────────────────────────────────────────────────────────────────
def fig_behaviour():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 28, "Чому GDT — це «лом» (crowbar): спрацював — і коротить сплеск на землю",
              size=18, anchor="middle", weight="bold")

    # осі: напруга на затисках GDT у часі
    ox, oy = 90, 330        # початок осей
    axw, axh = 760, 250
    s += arrow(ox, oy, ox, oy - axh, color=INK, w=2)        # V вгору
    s += arrow(ox, oy, ox + axw, oy, color=INK, w=2)        # t вправо
    s += text(ox - 12, oy - axh + 4, "U на GDT", size=13, anchor="end", weight="bold")
    s += text(ox + axw, oy + 22, "час", size=13, anchor="middle")

    # рівні
    y_spark = oy - 210     # напруга спрацювання (sparkover) ~ висока
    y_arc = oy - 45        # напруга дуги (arc) ~ низька, десятки В
    y_dc = oy - 95         # «тлійний» рівень / робоча зона (умовно)
    # пунктири рівнів
    s += line(ox, y_spark, ox + axw, y_spark, color=RED, w=1.4, dash="5 5")
    s += text(ox + axw, y_spark - 8, "напруга спрацювання (sparkover) ~ сотні В…кВ",
              size=12, anchor="end", color=RED)
    s += line(ox, y_arc, ox + axw, y_arc, color=GREEN, w=1.4, dash="5 5")
    s += text(ox + axw, y_arc + 18, "напруга дуги (arc) ~ 10…30 В — ось чому захищає",
              size=12, anchor="end", color=GREEN)

    # крива напруги на GDT
    # 1) до пробою повторює сплеск, що росте; 2) на sparkover — гострий пік; 3) обвал до arc;
    # 4) тримає arc, поки тече струм; 5) гасне → повертається у відкритий стан
    x0 = ox + 10
    x_break = ox + 230
    x_arc_end = ox + 560
    x_recover = ox + 640
    curve = [(x0, oy - 6)]
    # ростуча передня частина (сплеск, поки GDT ще «відкритий»)
    n = 22
    for i in range(1, n + 1):
        t = i / n
        x = x0 + (x_break - x0) * t
        # сплеск росте, поки GDT ще «відкритий»: експоненційне наближення до піку
        y = (oy - 6) + (y_spark - (oy - 6)) * (t ** 1.7)
        curve.append((x, y))
    s += polyline(curve, color=BLUE, w=3)
    # гострий обвал до напруги дуги
    s += polyline([(x_break, y_spark), (x_break + 18, y_arc)], color=BLUE, w=3)
    # тримання дуги (трохи нерівне)
    s += polyline([(x_break + 18, y_arc), (x_arc_end, y_arc)], color=BLUE, w=3)
    # відновлення (струм згас, GDT знову відкритий — напруга вільно зростає/падає за лінією)
    s += polyline([(x_arc_end, y_arc), (x_recover, oy - 70), (ox + axw - 20, oy - 60)],
                  color=BLUE, w=3, dash="2 4")

    # підписи фаз
    s += text((x0 + x_break) / 2, oy - 8, "1. сплеск росте,", size=12.5, anchor="middle", color=BLUE)
    s += text((x0 + x_break) / 2, oy + 8, "GDT ще «не бачить»", size=11.5, anchor="middle", color=GREY)

    s += circle(x_break, y_spark, 5, fill=RED, stroke=RED)
    s += text(x_break + 8, y_spark - 14, "2. пробій газу", size=12.5, color=RED, weight="bold")

    s += arrow(x_break + 40, (y_spark + y_arc) / 2 - 10, x_break + 24, (y_spark + y_arc) / 2 + 18,
               color=INK, w=1.8)
    s += text(x_break + 46, (y_spark + y_arc) / 2, "3. напруга «складається»", size=12, color=INK)
    s += text(x_break + 46, (y_spark + y_arc) / 2 + 16, "(crowbar — коротке на землю)", size=11,
              color=GREY)

    s += text((x_break + x_arc_end) / 2, y_arc - 12, "4. тримає дугу, поки тече струм", size=12.5,
              anchor="middle", color=GREEN)

    s += text(x_recover + 30, oy - 95, "5. струм згас →", size=12, color=GREY)
    s += text(x_recover + 30, oy - 80, "GDT знову відкритий", size=12, color=GREY)

    # рамка-попередження про follow current
    wx, wy, ww, wh = ox + 250, oy - 245, 470, 64
    s += rect(wx, wy, ww, wh, fill="#fff6f4", stroke=RED, sw=1.6, rx=8)
    s += text(wx + 12, wy + 22, "Пастка: коли GDT \"закоротив\", за сплеском у дугу може", size=12.5,
              color=RED, weight="bold")
    s += text(wx + 12, wy + 42, "піти струм самого джерела (follow current). У мережі його", size=12.5,
              color=RED)
    s += text(wx + 12, wy + 58, "мусить обірвати запобіжник чи послідовний елемент.", size=12.5,
              color=RED)

    s += footer()
    with open(os.path.join(OUT, "fig-r10-s3c-2-gdt-crowbar.svg"), "w", encoding="utf-8") as f:
        f.write(s)


if __name__ == "__main__":
    fig_devices()
    fig_behaviour()
    print("OK: written to", OUT)
