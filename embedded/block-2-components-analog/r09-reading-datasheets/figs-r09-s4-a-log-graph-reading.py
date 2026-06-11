# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки 2.9.4a
«Зчитати число з графіка правильно: логарифмічні осі й сітка декад»
(Розділ 2.9, Модуль 2).

Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r09-4a-…), щоб не перетинатися з головним figs.py розділу
й іншими вставками.
Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
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
MIDGR = "#cfcfcf"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 2.9.4a.1 — сітка декад: чому «на око посередині» бреше ───────────────
def fig_decade_grid():
    W, H = 740, 430
    s = header(W, H)
    s += text(W / 2, 28, "Логарифмічна вісь: «на око посередині» ≠ середнє арифметичне",
              15.5, INK, "middle", "bold")

    ox, oy = 92, 350           # початок осей
    pw, ph = 560, 290          # довжина осей
    decs = 2                   # дві декади: 1 … 100
    base = 1.0                 # нижній край = 1

    def xPix(t):               # t — частка ширини [0..1]
        return ox + pw * t

    def yLog(v):               # значення v (1..100) → координата по вертикалі
        u = math.log10(v) - math.log10(base)
        return oy - ph * u / decs

    # осі
    s += arrow(ox, oy, ox, oy - ph - 16, INK, 2)
    s += arrow(ox, oy, ox + pw + 16, oy, INK, 2)
    s += text(ox + pw + 20, oy + 4, "вхідна величина", 11, INK, "start", "bold")
    s += text(ox - 78, oy - ph - 2, "вихід (лог. вісь)", 11, INK, "start", "bold")

    # головні лінії декад: 1, 10, 100
    for v in (1, 10, 100):
        yy = yLog(v)
        s += line(ox, yy, ox + pw, yy, MIDGR, 1.4)
        s += line(ox - 6, yy, ox, yy, INK, 1.6)
        s += text(ox - 12, yy + 4, str(v), 11, INK, "end", "bold")
    # проміжні лінії сітки декади (2..9 у кожній) — нерівномірні!
    for d in (1, 10):
        for k in range(2, 10):
            v = d * k
            if v > 100:
                continue
            yy = yLog(v)
            s += line(ox, yy, ox + pw, yy, FAINT, 1)
            s += text(ox - 12, yy + 3.5, str(v), 7.5, GREY, "end")

    # геометрична середина між 1 і 100 = 10 (на лог-осі — рівно посередині)
    ymid_geo = yLog(10)
    s += line(ox, ymid_geo, ox + pw, ymid_geo, GREEN, 2, "5 3")
    s += circle(ox + pw * 0.5, ymid_geo, 5, GREEN, "#fff", 2.4)
    s += text(ox + pw * 0.5, ymid_geo - 12, "геометрична середина = 10", 10.5, GREEN, "middle", "bold")
    s += text(ox + pw * 0.5, ymid_geo - 26, "(√(1·100) — рівно посередині декад)", 9, GREEN, "middle")

    # «на око» арифметична середина 50.5 ≈ 50 — куди тягне зір
    ymid_ar = yLog(50)
    s += line(ox, ymid_ar, ox + pw, ymid_ar, RED, 1.8, "3 3")
    s += text(ox + pw + 4, ymid_ar + 4, "50 — а НЕ тут", 9.5, RED, "start", "bold")

    # підсвітити: половина висоти графіка
    yhalf = (yLog(1) + yLog(100)) / 2
    s += arrow(ox + pw * 0.18, yLog(1) - 2, ox + pw * 0.18, yhalf + 2, BLUE, 1.6)
    s += arrow(ox + pw * 0.18, yLog(100) + 2, ox + pw * 0.18, yhalf - 2, BLUE, 1.6)
    s += text(ox + pw * 0.18 + 8, (yLog(1) + yhalf) / 2 + 4, "пів-висоти", 8.5, BLUE, "start")

    s += text(W / 2, H - 12,
              "Рівні відстані на лог-осі = рівні МНОЖЕННЯ, не додавання. Середина двох сусідніх ліній — їх ДОБУТОК під коренем.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4a-1-decade-grid.svg", s)


# ── Рис. 2.9.4a.2 — алгоритм зчитування: позиція → log → значення ────────────
def fig_read_algorithm():
    W, H = 740, 430
    s = header(W, H)
    s += text(W / 2, 28, "Зчитати точку: міряємо ЧАСТКУ декади, потім підносимо 10 у степінь",
              15, INK, "middle", "bold")

    ox, oy = 92, 348
    pw, ph = 470, 280
    decs = 2
    base = 1.0

    def yLog(v):
        u = math.log10(v) - math.log10(base)
        return oy - ph * u / decs

    # осі
    s += arrow(ox, oy, ox, oy - ph - 16, INK, 2)
    s += arrow(ox, oy, ox + pw + 16, oy, INK, 2)
    s += text(ox + pw + 18, oy + 4, "x", 12, INK, "start", "bold")
    s += text(ox - 76, oy - ph - 2, "y (лог.)", 11, INK, "start", "bold")

    for v in (1, 10, 100):
        yy = yLog(v)
        s += line(ox, yy, ox + pw, yy, MIDGR, 1.4)
        s += line(ox - 6, yy, ox, yy, INK, 1.6)
        s += text(ox - 12, yy + 4, str(v), 11, INK, "end", "bold")
    for d in (1, 10):
        for k in range(2, 10):
            v = d * k
            if v > 100:
                continue
            s += line(ox, yLog(v), ox + pw, yLog(v), FAINT, 1)

    # крива (умовна спадна залежність) для антуражу
    crv = []
    for i in range(0, 41):
        t = i / 40.0
        xx = ox + pw * t
        val = 80.0 / (1 + 9 * t)      # від 80 спадає
        crv.append((xx, yLog(val)))
    s += _poly(crv, BLUE, 2.6)
    s += text(ox + pw - 6, yLog(80 / (1 + 9 * 1.0)) - 8, "крива даташита", 9.5, BLUE, "end", "bold")

    # зчитувана точка: знайшли по горизонталі x, опустили на криву
    tq = 0.30
    xq = ox + pw * tq
    vq = 80.0 / (1 + 9 * tq)          # ≈ 21.6
    yq = yLog(vq)
    s += line(xq, oy, xq, yq, SUN, 1.8, "4 3")
    s += line(ox, yq, xq, yq, SUN, 1.8, "4 3")
    s += circle(xq, yq, 5, SUN, "#fff", 2.4)
    s += text(xq, oy + 18, "твій x", 9.5, SUN, "middle", "bold")

    # вимірюємо частку декади: між 10 і 100, частка p вгору
    y10, y100 = yLog(10), yLog(100)
    s += line(ox + pw + 6, y10, ox + pw + 6, y100, GREEN, 1.6)
    s += line(ox + pw + 3, y10, ox + pw + 9, y10, GREEN, 1.6)
    s += line(ox + pw + 3, y100, ox + pw + 9, y100, GREEN, 1.6)
    s += line(ox + pw + 3, yq, ox + pw + 9, yq, RED, 2)
    p = (math.log10(vq) - 1.0)         # частка декади 10→100
    s += text(ox + pw + 14, (y10 + yq) / 2 + 4, f"p ≈ {p:.2f}", 9.5, RED, "start", "bold")
    s += text(ox + pw + 14, y100 - 4, "верх декади (100)", 8, GREEN, "start")
    s += text(ox + pw + 14, y10 + 12, "низ декади (10)", 8, GREEN, "start")

    # результат
    s += text(xq + 10, yq - 8, f"y = 10·10^{p:.2f} ≈ {vq:.0f}", 11, RED, "start", "bold")

    # формульна підказка внизу зліва
    bx, by = ox + 4, oy - ph + 8
    s += rect(bx, by, 244, 70, "#ffffff", GREY, 1.2, 6)
    s += text(bx + 10, by + 20, "p = частка декади (0…1)", 10, INK, "start")
    s += text(bx + 10, by + 39, "y = (низ декади) · 10ᵖ", 10.5, INK, "start", "bold")
    s += text(bx + 10, by + 57, "напр. декада 10→100, p=0.33 → 21.5", 8.5, GREY, "start", style="italic")

    s += text(W / 2, H - 12,
              "Спершу знаходимо, яку ЧАСТКУ декади займає точка, потім значення = (низ декади) × 10^(частка). Лінійкою — лише частку.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4a-2-read-algorithm.svg", s)


if __name__ == "__main__":
    fig_decade_grid()
    fig_read_algorithm()
    print("OK — фігури вставки 2.9.4a згенеровано в", OUT)
