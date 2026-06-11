# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки до теми 2.9.3
«Min/typ/max як статистика: розкид партії і чому "typ" ніхто не гарантує».

Чистий Python без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r09-3m-…), щоб не перетинатися з головним figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; sans-serif.
Допоміжні функції скопійовано з figs.py розділу.
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", GREY: "aGrey"}


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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _gauss(x, mu, sig):
    return math.exp(-((x - mu) ** 2) / (2 * sig * sig))


def _bell_pts(ox, oy, x0, x1, mu, sig, amp, n=160):
    """Точки дзвона в екранних координатах для діапазону параметра [x0,x1]."""
    pts = []
    for i in range(n + 1):
        xv = x0 + (x1 - x0) * i / n
        sx = ox + (xv - x0) / (x1 - x0) * (x1 - x0)  # масштаб задається ззовні
        pts.append((xv, _gauss(xv, mu, sig)))
    return pts


# ─────────────────────────────────────────────────────────────────────────
# Рис. 2.9.3m.1 — нормальний розкид партії: typ = центр, min/max = краї,
# запас схеми як «скільки сигм» від центру.
# ─────────────────────────────────────────────────────────────────────────
def fig_distribution():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Розкид параметра в партії: «typ» — центр, гарантія — краї",
              17, INK, "middle", "bold")

    ox, oy = 90, 320          # початок осей (лівий низ кривої)
    pw, ph = 580, 215         # ширина/висота поля кривої
    mu = 0.0                  # центр у «сигмах»
    sig = 1.0
    lo, hi = -4.2, 4.2        # діапазон по осі в сигмах

    def X(z):
        return ox + (z - lo) / (hi - lo) * pw

    def Yc(val):              # val у [0..1] від піка
        return oy - val * ph

    peak = _gauss(mu, mu, sig)

    # вісь параметра
    s += arrow(ox - 10, oy, ox + pw + 24, oy, INK, 2)
    s += text(ox + pw + 28, oy + 5, "значення параметра", 13, INK, "start", "bold")

    # межі min/max як вертикалі (± ~3.2σ — типовий гарантований край)
    zmin, zmax = -3.2, 3.2
    for z, lab in ((zmin, "min"), (zmax, "max")):
        s += line(X(z), oy, X(z), Yc(_gauss(z, mu, sig) / peak), GREEN, 2.4, "5,4")
        s += text(X(z), oy + 22, lab, 14, GREEN, "middle", "bold")
    # зелена смуга «гарантовано» під віссю
    s += rect(X(zmin), oy + 30, X(zmax) - X(zmin), 16, LGRN, GREEN, 1.4, 4)
    s += text((X(zmin) + X(zmax)) / 2, oy + 42, "гарантовано: КОЖЕН прилад тут",
              12.5, GREEN, "middle", "bold")

    # дзвін: заливка хвостів (за межами) — світло-червоним
    body_pts = []
    n = 220
    for i in range(n + 1):
        z = lo + (hi - lo) * i / n
        body_pts.append((X(z), Yc(_gauss(z, mu, sig) / peak)))
    # повна крива
    area = f'<path d="M {ox},{oy} ' + " ".join(f"L {x:.1f},{y:.1f}" for x, y in body_pts) + f' L {ox + pw},{oy} Z" fill="{LBLUE}" stroke="none"/>\n'
    s += area
    s += '<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in body_pts) + f'" fill="none" stroke="{BLUE}" stroke-width="2.6"/>\n'

    # центральна лінія typ
    s += line(X(mu), oy, X(mu), Yc(1.0), SUN, 2.6)
    s += text(X(mu), Yc(1.0) - 10, "typ", 15, "#a9781a", "middle", "bold")
    s += text(X(mu), Yc(1.0) - 26, "(центр / найімовірніше)", 11.5, "#a9781a", "middle")

    # позначки ±1σ, ±2σ під кривою
    for z in (-2, -1, 1, 2):
        s += line(X(z), oy, X(z), oy + 6, GREY, 1.6)
        s += text(X(z), oy + 17, f"{'+' if z > 0 else '−'}{abs(z)}σ", 11, GREY, "middle")

    # дужка «запас від центру до краю» зверху
    yb = Yc(1.0) - 46
    s += line(X(mu), yb, X(zmax), yb, RED, 1.8)
    s += line(X(mu), yb, X(mu), yb + 8, RED, 1.8)
    s += line(X(zmax), yb, X(zmax), yb + 8, RED, 1.8)
    s += text((X(mu) + X(zmax)) / 2, yb - 8, "запас typ→max ≈ 3σ", 12.5, RED, "middle", "bold")

    # пояснювальний рядок
    s += text(ox - 10, H - 14,
              "Вужчі min/max  =  менше σ (точніший процес)  АБО  відбір кращих екземплярів = дорожче",
              12.5, INK, "start")
    save("fig-r09-3m-1-distribution.svg", s)


# ─────────────────────────────────────────────────────────────────────────
# Рис. 2.9.3m.2 — біннінг: одна широка партія, розрізана на сорти.
# ─────────────────────────────────────────────────────────────────────────
def fig_binning():
    W, H = 760, 420
    s = header(W, H)
    s += text(W / 2, 30, "Біннінг: один процес — кілька сортів за тим самим номером",
              17, INK, "middle", "bold")

    ox, oy = 80, 300
    pw, ph = 600, 190
    lo, hi = -4.2, 4.2
    mu, sig = 0.0, 1.0

    def X(z):
        return ox + (z - lo) / (hi - lo) * pw

    def Yc(val):
        return oy - val * ph

    peak = _gauss(mu, mu, sig)
    n = 240
    crv = [(X(lo + (hi - lo) * i / n),
            Yc(_gauss(lo + (hi - lo) * i / n, mu, sig) / peak),
            lo + (hi - lo) * i / n) for i in range(n + 1)]

    # вісь
    s += arrow(ox - 10, oy, ox + pw + 24, oy, INK, 2)
    s += text(ox + pw + 28, oy + 5, "напруга зсуву Vos", 13, INK, "start", "bold")

    # три зони: precision (центр |z|<1), standard (|z|<2.6), брак (хвости)
    zp, zs = 1.0, 2.6

    def band(z0, z1, fill):
        pts = [(X(z0), oy)]
        for x, y, z in crv:
            if z0 - 1e-6 <= z <= z1 + 1e-6:
                pts.append((x, y))
        pts.append((X(z1), oy))
        return f'<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f' Z" fill="{fill}" stroke="none"/>\n'

    # хвости (брак / нижчий сорт) — сірим
    s += band(-hi, -zs, FAINT)
    s += band(zs, hi, FAINT)
    # стандарт — світло-синій (бокові частини між zp і zs)
    s += band(-zs, -zp, LBLUE)
    s += band(zp, zs, LBLUE)
    # прецизійний — світло-зелений центр
    s += band(-zp, zp, LGRN)

    # крива зверху
    s += '<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y, _ in crv) + f'" fill="none" stroke="{INK}" stroke-width="2.4"/>\n'

    # роздільні вертикалі
    for z in (-zs, -zp, zp, zs):
        s += line(X(z), oy, X(z), Yc(_gauss(z, mu, sig) / peak), GREY, 1.6, "4,4")

    # підписи сортів під віссю
    s += rect(X(-zp), oy + 12, X(zp) - X(-zp), 18, LGRN, GREEN, 1.4, 4)
    s += text(0.5 * (X(-zp) + X(zp)), oy + 25, "ПРЕЦИЗІЙНИЙ  ±0.5 мВ", 12, GREEN, "middle", "bold")
    s += rect(X(-zs), oy + 36, X(zs) - X(-zs), 18, "none", BLUE, 1.4, 4)
    s += text(0.5 * (X(-zs) + X(zs)), oy + 49, "СТАНДАРТНИЙ  ±3 мВ (увесь зелений + синій)", 12, BLUE, "middle", "bold")

    # хвости — підпис
    s += text(X(-zs) - 8, oy - 4, "відбраковано", 11, GREY, "end")
    s += text(X(zs) + 8, oy - 4, "відбраковано", 11, GREY, "start")

    # стрілки-винесення «дорожче / дешевше»
    s += text(0.5 * (X(-zp) + X(zp)), Yc(1.0) - 14, "дорого", 12.5, "#a9781a", "middle", "bold")
    s += arrow(X(zp) + 6, Yc(0.55), X(zs) - 6, Yc(0.55), GREY, 1.8)
    s += text(0.5 * (X(zp) + X(zs)) + 4, Yc(0.55) - 8, "дешевше", 11.5, GREY, "middle")

    s += text(ox - 10, H - 16,
              "Сортування коштує: «typ» однакове в усіх сортів, але гарантований край (max) — різний.",
              12.5, INK, "start")
    save("fig-r09-3m-2-binning.svg", s)


if __name__ == "__main__":
    fig_distribution()
    fig_binning()
    print("done")
