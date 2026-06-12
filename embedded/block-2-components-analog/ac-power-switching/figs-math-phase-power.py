# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.11.4m
«Потужність від кута відсікання: інтеграл півхвилі».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

УНІКАЛЬНІ імена файлів (fig-r11-4m-*), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи — Рис. 2.11.4m.k.
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
#  Рис. 2.11.4m.1 — півхвиля, кут запуску α, провідна ділянка [α, π],
#  площа під v² = потужність. Наочно показуємо інтеграл sin²θ.
# ─────────────────────────────────────────────────────────────────────────────
def fig1_halfwave_integral():
    W, H = 760, 410
    s = header(W, H)
    s += text(W / 2, 30, "Фазове відсікання півхвилі та площа під v²", 16, INK, "middle", "bold")

    # дві системи координат: зверху напруга v(θ)=sin θ, знизу потужність v²=sin²θ
    ox = 90
    plot_w = 560
    # верхня панель: v(θ)
    oy1 = 150
    amp1 = 78
    # нижня панель: v²(θ)
    oy2 = 360
    amp2 = 150

    alpha = math.pi / 2.0  # кут запуску 90°

    def X(th):
        return ox + plot_w * th / math.pi

    # підпис панелей
    s += text(ox - 60, oy1 - amp1 - 6, "v(θ)", 13, INK, "start", "bold")
    s += text(ox - 60, oy2 - amp2 - 6, "v² ∝ p(θ)", 13, INK, "start", "bold")

    # ---- верхня панель: осі ----
    s += line(ox, oy1, ox + plot_w + 18, oy1, INK, 1.6)  # вісь θ
    s += arrow(ox, oy1, ox, oy1 - amp1 - 26, INK, 1.6)
    # повна синусоїда (пунктир — «що було б без відсікання»)
    full = [(X(th), oy1 - amp1 * math.sin(th)) for th in [i * math.pi / 120 for i in range(121)]]
    s += _path(full, GREY, 1.8, dash="5,4")
    # провідна частина [α, π] — суцільна червона
    cond = [(X(th), oy1 - amp1 * math.sin(th))
            for th in [alpha + (math.pi - alpha) * i / 80 for i in range(81)]]
    s += _path(cond, RED, 2.8)
    # відсічена частина 0..α лежить на нулі (ключ закритий)
    s += line(ox, oy1, X(alpha), oy1, BLUE, 3.2)
    # вертикаль запуску
    s += line(X(alpha), oy1 + 6, X(alpha), oy1 - amp1 - 8, AMBER, 2, dash="4,3")
    s += text(X(alpha), oy1 - amp1 - 14, "запуск α", 12, AMBER, "middle", "bold")
    # позначки θ
    s += text(ox, oy1 + 20, "0", 12, INK, "middle")
    s += text(X(math.pi / 2), oy1 + 20, "90°", 12, INK, "middle")
    s += text(X(math.pi), oy1 + 20, "180°", 12, INK, "middle")
    s += text(ox + plot_w + 22, oy1 + 5, "θ = ωt", 12, INK, "start", "bold")
    s += text(X(0.32), oy1 + 36, "ключ закритий", 11, BLUE, "middle")
    s += text(X(2.35), oy1 + 36, "ключ відкритий", 11, RED, "middle")

    # ---- нижня панель: осі та площа sin²θ ----
    s += line(ox, oy2, ox + plot_w + 18, oy2, INK, 1.6)
    s += arrow(ox, oy2, ox, oy2 - amp2 - 22, INK, 1.6)
    # повна крива sin²θ (пунктир)
    full2 = [(X(th), oy2 - amp2 * math.sin(th) ** 2) for th in [i * math.pi / 120 for i in range(121)]]
    s += _path(full2, GREY, 1.6, dash="5,4")
    # ЗАЛИТА площа під sin²θ на [α, π] = потужність, що дісталась навантаженню
    afill = [(X(alpha), oy2)]
    afill += [(X(th), oy2 - amp2 * math.sin(th) ** 2)
              for th in [alpha + (math.pi - alpha) * i / 80 for i in range(81)]]
    afill += [(X(math.pi), oy2)]
    s += _area(afill, LRED, RED, 2.4)
    # вертикаль α
    s += line(X(alpha), oy2 + 6, X(alpha), oy2 - amp2 - 6, AMBER, 2, dash="4,3")
    # підписи площі
    s += text(X(2.45), oy2 - 52, "площа =", 12, RED, "middle", "bold")
    s += text(X(2.45), oy2 - 34, "потужність", 12, RED, "middle", "bold")
    s += text(ox, oy2 + 20, "0", 12, INK, "middle")
    s += text(X(math.pi / 2), oy2 + 20, "90°", 12, INK, "middle")
    s += text(X(math.pi), oy2 + 20, "180°", 12, INK, "middle")
    s += text(ox + plot_w + 22, oy2 + 5, "θ", 12, INK, "start", "bold")

    # формула інтеграла збоку
    s += text(ox + plot_w - 4, oy2 - amp2 + 6, "∫ sin²θ dθ", 13, INK, "end", "bold", "italic")

    save("fig-r11-4m-1-halfwave-integral.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  Рис. 2.11.4m.2 — крива P(α)/P_повна від кута запуску; ключові точки
#  0°→100 %, 45°→91 %, 90°→50 %, 135°→9 %, 180°→0 %, симетрія навколо (90°,50%).
# ─────────────────────────────────────────────────────────────────────────────
def frac(alpha):
    # P(α)/P_full = 1 − α/π + sin(2α)/(2π)
    return 1.0 - alpha / math.pi + math.sin(2 * alpha) / (2 * math.pi)


def fig2_power_curve():
    W, H = 720, 470
    s = header(W, H)
    s += text(W / 2, 30, "Частка потужності від кута запуску (резистивне навантаження)", 15, INK, "middle", "bold")

    ox, oy = 95, 410
    plot_w = 540
    plot_h = 330

    def X(deg):
        return ox + plot_w * deg / 180.0

    def Y(f):
        return oy - plot_h * f

    # сітка по горизонталях (0..100 %)
    for p in range(0, 101, 25):
        y = Y(p / 100.0)
        s += line(ox, y, ox + plot_w, y, FAINT, 1.2)
        s += text(ox - 10, y + 4, f"{p}%", 12, GREY, "end")
    # сітка по вертикалях
    for d in range(0, 181, 45):
        x = X(d)
        s += line(x, oy, x, Y(1.0), FAINT, 1.2)
        s += text(x, oy + 22, f"{d}°", 12, GREY, "middle")

    # осі
    s += arrow(ox, oy, ox, Y(1.0) - 18, INK, 1.8)
    s += arrow(ox, oy, ox + plot_w + 18, oy, INK, 1.8)
    s += text(ox - 58, Y(0.5) - 60, "P / P_повна", 13, INK, "start", "bold")
    s += text(ox + plot_w + 22, oy + 5, "кут запуску α", 12, INK, "start", "bold")

    # крива
    pts = []
    for i in range(0, 181):
        a = math.radians(i)
        pts.append((X(i), Y(frac(a))))
    s += _path(pts, RED, 3.0)

    # лінія симетрії 50 %
    s += line(ox, Y(0.5), ox + plot_w, Y(0.5), BLUE, 1.4, dash="6,4")
    s += line(X(90), oy, X(90), Y(1.0), BLUE, 1.4, dash="6,4")
    s += text(X(90) + 6, Y(1.0) + 2, "вісь симетрії", 11, BLUE, "start")

    # ключові точки
    def dot(deg, label, dx=8, dy=-8, anch="start"):
        a = math.radians(deg)
        f = frac(a)
        x, y = X(deg), Y(f)
        out = circle(x, y, 4.5, RED, INK, 1.6)
        out += text(x + dx, y + dy, label, 12, INK, anch, "bold")
        return out

    s += dot(0, "0° → 100%", 10, 6, "start")
    s += dot(45, "45° → 91%", 10, -6, "start")
    s += dot(90, "90° → 50%", 12, -10, "start")
    s += dot(135, "135° → 9%", -10, 18, "end")
    s += dot(180, "180° → 0%", -10, -8, "end")

    # пояснювальна нотатка про нелінійність
    s += text(ox + 14, Y(0.97), "пологий початок:", 11, GREY, "start", "italic")
    s += text(ox + 14, Y(0.97) + 16, "мала затримка майже не гасить", 11, GREY, "start", "italic")
    s += text(X(150), Y(0.30), "крутий хвіст:", 11, GREY, "start", "italic")
    s += text(X(150), Y(0.30) + 16, "лампа гасне різко", 11, GREY, "start", "italic")

    save("fig-r11-4m-2-power-curve.svg", s)


if __name__ == "__main__":
    fig1_halfwave_integral()
    fig2_power_curve()
    print("done")
