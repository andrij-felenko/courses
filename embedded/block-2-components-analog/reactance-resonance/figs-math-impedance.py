# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки до теми 2.3.4 —
«Імпеданс Z як узагальнений закон Ома» (Модуль 2, Розділ 2.3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-9-4m-imp-*), головний figs.py розділу не чіпаємо.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано з
figs.py розділу (єдиний вигляд між розділами).
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def arc(cx, cy, r, a0, a1, col=INK, wv=2, dash=None):
    """Дуга від кута a0 до a1 (градуси, мат. напрям: проти годинникової вгору)."""
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy - r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy - r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 0 if a1 > a0 else 1
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {x0:.1f},{y0:.1f} A {r:.1f},{r:.1f} 0 {large} {sweep} '
            f'{x1:.1f},{y1:.1f}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n')


# ── Рис. 2.3.4m.1 — три чорні скриньки, один закон I = V/Z ───────────────────
def fig_blackboxes():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Один закон для трьох елементів: I = V / Z", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "змінюється лише вміст Z — алгебра кола та сама, що й з резисторами",
              14.5, GREY, "middle")

    boxes = [
        (150, RED,   "R",  "Z_R = R",          "дійсне",        "фаза 0°",        LRED),
        (440, GREEN, "C",  "Z_C = 1 / (jωC)",  "1/(ωC),  −j",   "I веде +90°",    LGRN),
        (730, BLUE,  "L",  "Z_L = jωL",        "ωL,  +j",       "I відстає −90°", LBLUE),
    ]
    by, bw, bh = 150, 150, 120
    for cx, col, lab, zexpr, modnote, phnote, fillc in boxes:
        bx = cx - bw / 2
        # скринька
        s += rect(bx, by, bw, bh, fillc, col, 2.4, 10)
        s += text(cx, by + 46, lab, 30, col, "middle", "bold")
        s += text(cx, by + 78, "чорна скринька", 12.5, GREY, "middle")
        s += text(cx, by + 98, "(для синусоїди)", 12.5, GREY, "middle")
        # V згори (через елемент)
        s += text(cx, by - 40, "V", 17, INK, "middle", "bold")
        s += line(bx + 20, by - 24, bx + bw - 20, by - 24, INK, 1.6, "3 3")
        s += line(bx + 20, by - 28, bx + 20, by - 8, INK, 1.6)
        s += line(bx + bw - 20, by - 28, bx + bw - 20, by - 8, INK, 1.6)
        # I знизу (крізь елемент) — стрілка
        s += arrow(bx - 6, by + bh + 26, bx + bw + 6, by + bh + 26, col, 2.6)
        s += text(cx, by + bh + 20, "I", 17, col, "middle", "bold")
        # формула Z під підписами
        s += rect(bx - 6, by + bh + 42, bw + 12, 64, "#ffffff", FAINT, 1.4, 8)
        s += text(cx, by + bh + 65, zexpr, 17, INK, "middle", "bold")
        s += text(cx, by + bh + 87, "|Z| = " + modnote, 13, INK, "middle")
        s += text(cx, by + bh + 103, phnote, 12.5, col, "middle")

    # нижній рядок-висновок
    s += text(W / 2, H - 16,
              "Послідовні Z додаються · паралельні — як обернені · дільник напруги той самий: усе з Модуля 1 переноситься на змінний струм",
              13, INK, "middle", "italic")
    save("fig-9-4m-imp-1-blackboxes.svg", s)


# ── Рис. 2.3.4m.2 — трикутник Z = R + jX і його хід із частотою ──────────────
def fig_triangle():
    W, H = 880, 540
    s = header(W, H)
    s += text(W / 2, 32, "Імпеданс як стрілка Z = R + jX: модуль і фаза в одному числі",
              20, INK, "middle", "bold")

    # ── ЛІВА панель: трикутник імпедансу ──
    ox, oy = 90, 400                 # початок координат
    axw, axh = 290, 290
    s += text(ox + 145, 70, "Трикутник імпедансу", 15.5, INK, "middle", "bold")
    # осі: Re (R) і Im (X)
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh, INK, 2)
    s += text(ox + axw + 6, oy + 16, "Re  (R)", 13, INK, "start", "bold")
    s += text(ox - 6, oy - axh - 8, "Im  (X)", 13, INK, "middle", "bold")
    s += text(ox - 10, oy + 18, "0", 12.5, GREY, "end")

    R = 200.0   # px
    X = 165.0   # px (індуктивний, вгору)
    # катет R (по дійсній осі)
    s += line(ox, oy, ox + R, oy, RED, 3)
    s += text(ox + R / 2, oy + 22, "R", 16, RED, "middle", "bold")
    s += text(ox + R / 2, oy + 40, "опір", 12, RED, "middle")
    # катет X (вертикальний) від кінця R
    s += line(ox + R, oy, ox + R, oy - X, BLUE, 3)
    s += text(ox + R + 12, oy - X / 2, "X = ωL − 1/(ωC)", 13.5, BLUE, "start", "bold")
    s += text(ox + R + 12, oy - X / 2 + 17, "реактивність", 11.5, BLUE, "start")
    # гіпотенуза Z
    s += arrow(ox, oy, ox + R, oy - X, GREEN, 3.2)
    s += text(ox + R * 0.5 - 14, oy - X * 0.5 - 10, "Z", 18, GREEN, "end", "bold")
    s += text(ox + R * 0.5 - 14, oy - X * 0.5 + 7, "|Z|=√(R²+X²)", 12.5, GREEN, "end")
    # кут φ
    s += arc(ox, oy, 50, 0, math.degrees(math.atan2(X, R)), INK, 2)
    s += text(ox + 60, oy - 14, "φ", 16, INK, "start", "normal", "italic")
    s += text(ox + 58, oy + 1, "= arctg(X/R)", 12, INK, "start")
    # прямий кут
    s += rect(ox + R - 12, oy - 12, 12, 12, "none", GREY, 1.4)

    # ── ПРАВА панель: Z(f) ходить із частотою → насіння H(jω) ──
    px, py = 530, 300               # початок: посередині по висоті, щоб X<0 і X>0 влізли
    paw, pah_up, pah_dn = 290, 160, 160
    s += text(px + 130, 70, "Z залежить від частоти", 15.5, INK, "middle", "bold")
    s += arrow(px, py, px + paw, py, INK, 2)                 # Re →
    s += arrow(px, py, px, py - pah_up, INK, 2)              # +Im ↑
    s += arrow(px, py, px, py + pah_dn, INK, 2)              # −Im ↓
    s += text(px + paw + 6, py + 16, "Re  (R)", 13, INK, "start", "bold")
    s += text(px - 6, py - pah_up - 8, "Im  (X)", 13, INK, "middle", "bold")
    s += text(px - 10, py + 18, "0", 12.5, GREY, "end")
    # вертикальна напрямна R = const (послідовний RLC: R фіксований)
    Rpx = 150.0
    s += line(px + Rpx, py - pah_up + 8, px + Rpx, py + pah_dn - 8, GREY, 1.6, "5 4")
    s += text(px + Rpx, py - pah_up - 2, "R = const", 12, GREY, "middle")
    # три стрілки Z для f<f0, f=f0, f>f0 (Xv додатне = вгору)
    states = [
        (-105.0, BLUE,  "f < f₀", "ємнісний (X<0)"),
        (0.0,    GREEN, "f = f₀", "X=0: Z=R"),
        (105.0,  RED,   "f > f₀", "індуктивний (X>0)"),
    ]
    for Xv, col, lab, note in states:
        ty = py - Xv
        s += arrow(px, py, px + Rpx, ty, col, 2.8)
        s += text(px + Rpx + 10, ty + (5 if Xv != 0 else -4), lab, 13, col, "start", "bold")
        s += text(px + Rpx + 10, ty + (21 if Xv < 0 else -19 if Xv > 0 else 12), note, 11, col, "start")
    # підпис-стрілка ходу вгору (зростання частоти)
    s += arrow(px + Rpx + 95, py + 70, px + Rpx + 95, py - 70, GREY, 1.8)
    s += text(px + Rpx + 100, py + 2, "f ↗", 12, GREY, "start")

    s += text(W / 2, H - 16,
              "Кінчик Z повзе по вертикалі R=const зі зміною f — а Z(ω) у дільнику й дає передавальну функцію H(jω) (§2.4.2)",
              13, INK, "middle", "italic")
    save("fig-9-4m-imp-2-triangle.svg", s)


if __name__ == "__main__":
    fig_blackboxes()
    fig_triangle()
    print("done.")
