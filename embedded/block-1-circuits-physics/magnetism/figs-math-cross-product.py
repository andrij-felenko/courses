# -*- coding: utf-8 -*-
"""
Фігури для 🧮-вставки «Векторний добуток: математика правил правої і лівої руки»
(до теми 1.8.7). Розділ 8, Модуль 1. Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — самодостатність), щоб НЕ чіпати головний скрипт.
УНІКАЛЬНІ імена SVG: fig-8-7m-*.svg. Нумерація підписів: Рис. 1.8.7m.k.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED    = "#c0271e"
BLUE   = "#1f47b5"
GREEN  = "#1f8a3b"
INK    = "#1b1b1b"
GREY   = "#8a8a8a"
FAINT  = "#e4e4e4"
COPPER = "#cf8b5e"
IRON   = "#9aa3ad"
ORANGE = "#e08030"
PURPLE = "#7a3fb0"
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", PURPLE: "aPurple"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    op = f' fill-opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<polygon points="{pts}" fill="{fill}"{op} stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.4, marker=None, dash=None):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n')


def current_out(cx, cy, r=10, color=ORANGE, w=2.4):
    out = circle(cx, cy, r, "#ffffff", color, w)
    out += circle(cx, cy, 2.4, color, color, 1)
    return out


def current_in(cx, cy, r=10, color=ORANGE, w=2.4):
    d = r * 0.62
    out = circle(cx, cy, r, "#ffffff", color, w)
    out += line(cx - d, cy - d, cx + d, cy + d, color, w)
    out += line(cx - d, cy + d, cx + d, cy - d, color, w)
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.7m.1 — Геометрія a × b: паралелограм площі |a||b|sinθ; напрям ⊥ за правою рукою.
# ─────────────────────────────────────────────────────────────────────────────
def fig_geometry():
    W, H = 760, 470
    s = header(W, H)

    # спільний початок векторів
    ox, oy = 230, 330

    # вектор a — вправо-вниз у площині (як «горизонтальна» сторона)
    ax, ay = ox + 250, oy + 12
    # вектор b — вправо-вгору (друга сторона паралелограма)
    bx, by = ox + 120, oy - 175

    # паралелограм: O, a, a+b, b
    abx, aby = ax + (bx - ox), ay + (by - oy)
    s += polygon([(ox, oy), (ax, ay), (abx, aby), (bx, by)],
                 fill=GREEN, opacity=0.13)

    # прямий кут між c і площиною — символічно: піднята стрілка c з точки O
    # вектор c = a × b: «угору» з площини (перпендикуляр), малюємо вертикально вгору
    cx, cy = ox, oy - 235
    s += arrow(ox, oy, cx, cy, PURPLE, 3.4)
    s += text(cx - 8, cy - 8, "c = a × b", 17, PURPLE, "end", "bold")
    s += text(cx - 8, cy + 13, "(⊥ до площини)", 12.5, PURPLE, "end", style="italic")

    # сторони паралелограма (повтор контуру жирніше для верхньої/правої)
    s += line(ax, ay, abx, aby, GREY, 1.6, "5,4")
    s += line(bx, by, abx, aby, GREY, 1.6, "5,4")

    # вектори a і b
    s += arrow(ox, oy, ax, ay, RED, 3.4)
    s += arrow(ox, oy, bx, by, BLUE, 3.4)
    s += text(ax + 8, ay + 6, "a", 19, RED, "start", "bold")
    s += text(bx - 6, by - 6, "b", 19, BLUE, "end", "bold")

    # кут θ між a і b — дуга біля початку
    a_a = math.degrees(math.atan2(ay - oy, ax - ox))
    a_b = math.degrees(math.atan2(by - oy, bx - ox))
    s += arc(ox, oy, 52, a_a, a_b, INK, 1.8)
    s += text(ox + 60, oy - 36, "θ", 16, INK, "middle", "bold")

    # позначка площі всередині паралелограма
    mx = (ox + abx) / 2
    my = (oy + aby) / 2
    s += text(mx + 18, my + 6, "площа = |a||b| sin θ", 14.5, GREEN, "middle", "bold")
    s += text(mx + 18, my + 26, "= |a × b|", 14, GREEN, "middle", style="italic")

    # ── права рука: пальці a→b, великий палець → c ──
    px = 560
    s += rect(px - 20, 60, 220, 250, "#fafafa", FAINT, 1.5, 10)
    s += text(px + 90, 84, "Права рука", 15.5, INK, "middle", "bold")
    s += text(px + 90, 104, "(права система координат)", 11.5, GREY, "middle", style="italic")
    # схематична долоня: великий палець вгору, пальці згинаються a→b
    hx, hy = px + 90, 230
    # долоня
    s += rect(hx - 26, hy - 4, 52, 60, "#f3e2d0", COPPER, 1.6, 8)
    # великий палець — угору (= c)
    s += arrow(hx - 26, hy + 6, hx - 26, hy - 70, PURPLE, 3.2)
    s += text(hx - 30, hy - 74, "c", 15, PURPLE, "end", "bold")
    # пальці згинаються: дуга від a до b
    s += arc(hx + 6, hy + 4, 34, -150, -20, INK, 2.6, marker="aInk")
    s += text(hx + 46, hy - 6, "a → b", 13, INK, "start", "bold")
    s += text(px - 12, 300, "пальці женуть a у бік b,", 11.5, INK, "start")
    s += text(px - 12, 316 - 4, "великий палець → c", 11.5, INK, "start")

    s += text(W / 2, 36, "Векторний добуток c = a × b", 19, INK, "middle", "bold")
    save("fig-8-7m-1-cross-geometry.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.7m.2 — Застосування: F = I·L × B. Три взаємно ⊥ вектори + права/ліва рука.
# ─────────────────────────────────────────────────────────────────────────────
def fig_lorentz():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 34, "Сила на провідник: F = I·L × B", 19, INK, "middle", "bold")

    # ── ліва частина: тривимірна трійка осей L, B, F ──
    ox, oy = 215, 250
    # B — вправо (поле, зелене)
    s += arrow(ox, oy, ox + 175, oy, GREEN, 3.4)
    s += text(ox + 182, oy + 6, "B", 18, GREEN, "start", "bold")
    s += text(ox + 182, oy + 24, "(поле)", 11.5, GREEN, "start", style="italic")
    # L (струм) — у глибину/вгору-вправо (орандж), малюємо як вісь «від нас» під кутом
    lx, ly = ox + 95, oy - 130
    s += arrow(ox, oy, lx, ly, ORANGE, 3.4)
    s += text(lx + 6, ly - 4, "L (I)", 17, ORANGE, "start", "bold")
    s += text(lx + 6, ly + 14, "(напрям струму)", 11, ORANGE, "start", style="italic")
    # F — вгору-вліво (перпендикуляр, фіолетовий)
    fx, fy = ox - 120, oy - 95
    s += arrow(ox, oy, fx, fy, PURPLE, 3.6)
    s += text(fx - 6, fy - 4, "F", 18, PURPLE, "end", "bold")
    s += text(fx - 6, fy + 14, "(сила)", 11.5, PURPLE, "end", style="italic")

    # прямі кути — маленькі квадратики біля початку (символічно три ⊥)
    s += polyline([(ox + 22, oy), (ox + 22, oy - 12), (ox + 10, oy - 12)], GREY, 1.4)

    s += text(ox + 20, oy + 70, "три вектори — взаємно ⊥", 13.5, INK, "middle", style="italic")
    s += text(ox + 20, oy + 90, "|F| = B·I·L·sin θ", 14.5, INK, "middle", "bold")

    # ── права частина: дві руки — права (фізика) і ліва (мнемоніка) ──
    bx = 540
    s += rect(bx - 30, 60, 250, 300, "#fafafa", FAINT, 1.5, 10)

    # верх: права рука — векторний добуток (як у фізиці)
    s += text(bx + 95, 86, "Права рука: I → B дає F", 13.5, INK, "middle", "bold")
    hx, hy = bx + 95, 150
    s += rect(hx - 24, hy - 4, 48, 46, "#f3e2d0", COPPER, 1.6, 8)
    s += arrow(hx - 24, hy + 4, hx - 24, hy - 50, PURPLE, 3.0)   # великий → F
    s += text(hx - 28, hy - 54, "F", 13.5, PURPLE, "end", "bold")
    s += arc(hx + 4, hy, 26, -150, -20, INK, 2.4, marker="aInk")
    s += text(hx + 36, hy - 6, "I→B", 11.5, INK, "start", "bold")

    # лінія-роздільник
    s += line(bx - 20, 210, bx + 210, 210, FAINT, 1.4)

    # низ: ліва рука (BIF / «правило лівої руки»: B у долоню, пальці — I, великий — F)
    s += text(bx + 95, 238, "Ліва рука (мнемоніка BIF)", 13.5, INK, "middle", "bold")
    hx2, hy2 = bx + 95, 310
    # долоня обернена до нас (поле «входить» у долоню)
    s += rect(hx2 - 24, hy2 - 30, 48, 46, "#dfeede", GREEN, 1.6, 8)
    s += current_in(hx2, hy2 - 7, 9, GREEN, 2.0)            # B у долоню
    s += arrow(hx2 + 24, hy2, hx2 + 70, hy2, ORANGE, 2.8)   # пальці → I
    s += text(hx2 + 74, hy2 + 5, "I", 13.5, ORANGE, "start", "bold")
    s += arrow(hx2, hy2 - 30, hx2, hy2 - 74, PURPLE, 3.0)   # великий → F
    s += text(hx2 - 4, hy2 - 78, "F", 13.5, PURPLE, "end", "bold")
    s += text(bx + 95, 348, "B у долоню · пальці I · великий F", 10.5, GREY, "middle", style="italic")

    save("fig-8-7m-2-lorentz-hands.svg", s)


if __name__ == "__main__":
    fig_geometry()
    fig_lorentz()
    print("done.")
