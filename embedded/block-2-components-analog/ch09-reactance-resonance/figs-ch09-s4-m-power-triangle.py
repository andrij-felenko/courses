# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.3.4m (друга):
«Активна, реактивна й повна потужність: P, Q, S, cosφ».

Не чіпає головний figs.py розділу. Унікальні імена файлів: fig-9-4m2-*.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; шрифт sans-serif;
стрілки через marker. Допоміжні функції скопійовано з figs.py розділу 9.
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
COPP  = "#b5732e"
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


def _fillpoly(pts, fill, stroke="none", wv=0, opacity=1.0):
    op = f' fill-opacity="{opacity}"' if opacity != 1.0 else ""
    st = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" fill="{fill}"{op}{st}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ---------------------------------------------------------------------------
# Рис. 2.3.4m.2 (перша у вставці) — трикутник потужностей P, Q, S, cosφ
# ---------------------------------------------------------------------------
def fig_power_triangle():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "Трикутник потужностей: S — гіпотенуза, P і Q — катети",
              16, INK, "middle", "bold")

    # Геометрія: прямий кут у вершині біля P-кінця.
    ox, oy = 110, 330            # початок (лівий нижній кут) — джерело
    P = 360.0                    # активна (горизонталь)
    Q = 230.0                    # реактивна (вертикаль угору)
    ax, ay = ox + P, oy          # вершина прямого кута (правий нижній)
    tx, ty = ax, oy - Q          # верхня вершина

    # Катет P (активна) — зелений, горизонтальний
    s += arrow(ox, oy, ax, ay, GREEN, 3)
    # Катет Q (реактивна) — синій, вертикальний угору
    s += arrow(ax, oy, tx, ty, BLUE, 3)
    # Гіпотенуза S (повна) — чорна, з початку до верхньої вершини
    s += arrow(ox, oy, tx, ty, INK, 3.2)

    # Прямий кут
    qs = 16
    s += _poly([(ax - qs, ay), (ax - qs, ay - qs), (ax, ay - qs)], INK, 1.6)

    # Дуга кута φ біля джерела
    phi = math.atan2(Q, P)
    rr = 72
    pts = []
    for k in range(0, 25):
        a = phi * k / 24
        pts.append((ox + rr * math.cos(a), oy - rr * math.sin(a)))
    s += _poly(pts, RED, 2.2)
    s += text(ox + rr * math.cos(phi / 2) + 20, oy - rr * math.sin(phi / 2) + 6,
              "φ", 18, RED, "middle", "bold")

    # Підпис P (під горизонтальним катетом)
    s += text((ox + ax) / 2, oy + 34, "P  —  активна (W)", 15, GREEN, "middle", "bold")
    s += text((ox + ax) / 2, oy + 54, "робить роботу, гріє, крутить вал", 12.5, GREY, "middle")
    # Підпис Q (праворуч від вертикального катета, у вільній смузі до формул)
    s += text(ax + 14, (oy + ty) / 2 - 8, "Q — реактивна (VAR)", 15, BLUE, "start", "bold")
    s += text(ax + 14, (oy + ty) / 2 + 12, "гойдає поле туди-сюди,", 12.5, GREY, "start")
    s += text(ax + 14, (oy + ty) / 2 + 30, "роботи не робить", 12.5, GREY, "start")
    # Підпис S — у відкритій зоні над гіпотенузою, лівий верх
    s += text(150, 150, "S — повна потужність (VA)", 15, INK, "start", "bold")
    s += text(150, 170, "те, що реально тягнеться", 12.5, GREY, "start")
    s += text(150, 187, "з мережі (струм × напруга)", 12.5, GREY, "start")
    s += arrow(225, 193, (ox + tx) / 2 - 4, (oy + ty) / 2 - 4, GREY, 1.6)

    # Джерело — маленьке коло
    s += circle(ox, oy, 5, INK, INK, 0)

    # Формули — правий нижній кут, окремий блок, нічого не перекриває
    bx, by, bw, bh = 560, 248, 300, 150
    s += rect(bx, by, bw, bh, LGRN, FAINT, 1.5, 10)
    s += text(bx + 20, by + 32, "S² = P² + Q²", 17, INK, "start", "bold")
    s += text(bx + 20, by + 62, "cos φ = P / S", 15, GREEN, "start", "bold")
    s += text(bx + 168, by + 62, "sin φ = Q / S", 15, BLUE, "start", "bold")
    s += line(bx + 20, by + 80, bx + bw - 20, by + 80, FAINT, 1.4)
    s += text(bx + 20, by + 104, "S = U·I   (RMS)", 14, INK, "start")
    s += text(bx + 20, by + 128, "P = U·I·cos φ", 14, INK, "start")
    s += text(bx + 168, by + 128, "Q = U·I·sin φ", 14, INK, "start")

    save("fig-9-4m2-1-power-triangle.svg", s)


# ---------------------------------------------------------------------------
# Рис. 2.3.4m.2 (друга) — миттєва потужність p(t) = u·i при різних φ
# ---------------------------------------------------------------------------
def _sine(ox, oy, w, amp, ph, col, wv=2.4, n=240, k=1):
    pts = []
    for j in range(n + 1):
        t = j / n
        y = amp * math.sin(2 * math.pi * k * t + ph)
        pts.append((ox + t * w, oy - y))
    return _poly(pts, col, wv)


def fig_instant_power():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 28, "Миттєва потужність p = u·i: чому Q гойдається, а P лишається",
              16, INK, "middle", "bold")

    # Три колонки: (лівий край, підпис, зсув фаз)
    cols = [(70,  "φ = 0°  (резистор)",              0.0),
            (305, "φ = 60°  (реальне коло)",         math.radians(60)),
            (540, "φ = 90°  (чиста реактивність)",   math.radians(90))]
    colw = 220
    top = 68
    midu = 150         # нульова вісь для u, i
    midp = 350         # нульова вісь для p
    amp = 44
    psc = 62           # масштаб p

    for ox, title, ph in cols:
        # осі
        s += line(ox, midu, ox + colw, midu, FAINT, 1.4)
        s += line(ox, midp, ox + colw, midp, FAINT, 1.4)
        s += line(ox, top, ox, midp + 70, FAINT, 1.4)
        s += text(ox + colw / 2, 54, title, 13.5, INK, "middle", "bold")
        s += text(ox - 6, midu - 56, "u, i", 12, GREY, "start")
        s += text(ox - 6, midp - 78, "p", 12, GREY, "start")

        # u (синій) — опорна; i (червоний) — зсунена на φ
        s += _sine(ox, midu, colw, amp, 0.0, BLUE, 2.2)
        s += _sine(ox, midu, colw, amp, ph, RED, 2.2)

        # p(t) = sin(2πt)·sin(2πt+φ), у відносних одиницях [-1..1]
        n = 240
        pts = []
        vals = []
        for j in range(n + 1):
            t = j / n
            p = math.sin(2 * math.pi * t) * math.sin(2 * math.pi * t + ph)
            pts.append((ox + t * colw, midp - p * psc))
            vals.append(p)
        # заливка площі вертикальними смужками: зелена де p>0 (бере), червона де p<0 (віддає)
        for j in range(n):
            x = ox + (j + 0.5) / n * colw
            p = vals[j]
            col = LGRN if p >= 0 else LRED
            s += line(x, midp, x, midp - p * psc, col, colw / n + 0.6)
        # крива p
        s += _poly(pts, INK, 2.0)
        # середній рівень P = ½·cos φ
        Pavg = 0.5 * math.cos(ph)
        ya = midp - Pavg * psc
        s += line(ox, ya, ox + colw, ya, GREEN, 2.4, "6 4")
        if abs(Pavg) > 0.02:
            s += text(ox + colw - 4, ya - 8, "сер. P", 13, GREEN, "end", "bold")
        else:
            s += text(ox + colw - 4, midp - 8, "сер. P = 0", 13, GREEN, "end", "bold")

    # легенда
    ly = 432
    s += line(70, ly, 100, ly, BLUE, 2.4);  s += text(106, ly + 4, "u(t)", 13, BLUE, "start", "bold")
    s += line(150, ly, 180, ly, RED, 2.4);  s += text(186, ly + 4, "i(t)", 13, RED, "start", "bold")
    s += line(228, ly, 258, ly, INK, 2.4);  s += text(264, ly + 4, "p = u·i", 13, INK, "start", "bold")
    s += line(348, ly, 378, ly, GREEN, 2.4, "6 4"); s += text(384, ly + 4, "середнє = P", 13, GREEN, "start", "bold")
    s += rect(516, ly - 9, 16, 12, LGRN, FAINT, 1); s += text(537, ly + 2, "бере енергію", 12.5, GREY, "start")
    s += rect(648, ly - 9, 16, 12, LRED, FAINT, 1); s += text(669, ly + 2, "віддає назад", 12.5, GREY, "start")

    s += text(W / 2, 458,
              "Середнє p за період = P. Більший φ — менше P; при 90° зелена й червона площі рівні, P = 0.",
              12.5, GREY, "middle")
    save("fig-9-4m2-2-instant-power.svg", s)


if __name__ == "__main__":
    fig_power_triangle()
    fig_instant_power()
    print("done")
