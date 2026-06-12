# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.9.4m
«Derating-графіки: інтерполяція і правило запасу» (Розділ 2.9, Модуль 2).

Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r09-4m-…), щоб не перетинатися з головним figs.py розділу.
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREY: "aGrey", GREEN: "aGreen"}


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


# ── Рис. 2.9.4m.1 — derating-крива з зламом і лінійною інтерполяцією ─────────
def fig_curve():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 30, "Derating-крива потужності: злам і лінійна інтерполяція", 15.5, INK, "middle", "bold")

    ox, oy = 96, 350           # початок осей
    pw, ph = 540, 280          # довжина осей
    Tmin, Tmax = 0, 175        # шкала температури
    Pmax = 1.0                 # 100 %

    def xT(T):
        return ox + pw * (T - Tmin) / (Tmax - Tmin)

    def yP(p):
        return oy - ph * p / Pmax

    # осі
    s += arrow(ox, oy, ox, oy - ph - 16, INK, 2)
    s += arrow(ox, oy, ox + pw + 16, oy, INK, 2)
    s += text(ox + pw + 20, oy + 4, "Tᴄ (°C)", 12, INK, "start", "bold")
    s += text(ox - 70, oy - ph - 4, "P_доп / P₂₅", 12, INK, "start", "bold")

    # сітка по X
    for T in range(0, 176, 25):
        s += line(xT(T), oy, xT(T), oy + 5, INK, 1.2)
        s += text(xT(T), oy + 19, str(T), 9.5, INK, "middle")
    # сітка по Y (у відсотках)
    for p in (0, 25, 50, 75, 100):
        yy = yP(p / 100.0)
        s += line(ox - 5, yy, ox, yy, INK, 1.2)
        s += text(ox - 10, yy + 4, f"{p}%", 9.5, INK, "end")
        s += line(ox, yy, ox + pw, yy, FAINT, 1)

    # derating-крива: плато до 25°C (100%), лінійний спад до 0 при 150°C
    Tknee, Tmaxj = 25, 150
    s += _poly([(xT(Tmin), yP(1.0)), (xT(Tknee), yP(1.0))], GREEN, 3)
    s += _poly([(xT(Tknee), yP(1.0)), (xT(Tmaxj), yP(0.0))], GREEN, 3)
    s += _poly([(xT(Tmaxj), yP(0.0)), (xT(Tmax), yP(0.0))], GREY, 2, "4 4")
    # точки зламу
    s += circle(xT(Tknee), yP(1.0), 4, GREEN, "#fff", 2)
    s += circle(xT(Tmaxj), yP(0.0), 4, RED, "#fff", 2)
    s += text(xT(Tknee) + 6, yP(1.0) - 8, "злам 25 °C", 9.5, GREEN, "start", "bold")
    s += text(xT(Tmaxj) - 6, yP(0.0) - 10, "Tj(max) 150 °C → 0 %", 9.5, RED, "end", "bold")

    # дві відомі точки даташита: 85°C і 100°C
    def Pcurve(T):
        if T <= Tknee:
            return 1.0
        if T >= Tmaxj:
            return 0.0
        return (Tmaxj - T) / (Tmaxj - Tknee)

    for T, col in ((85, BLUE), (100, BLUE)):
        s += circle(xT(T), yP(Pcurve(T)), 3.6, BLUE, "#fff", 1.8)
    s += text(xT(85) - 4, yP(Pcurve(85)) - 10, "52 %", 9, BLUE, "middle", "bold")
    s += text(xT(100) + 4, yP(Pcurve(100)) - 10, "40 %", 9, BLUE, "middle", "bold")

    # цільова інтерполяція при 92°C
    Tq = 92
    Pq = Pcurve(Tq)
    s += line(xT(Tq), oy, xT(Tq), yP(Pq), SUN, 1.8, "4 3")
    s += line(ox, yP(Pq), xT(Tq), yP(Pq), SUN, 1.8, "4 3")
    s += circle(xT(Tq), yP(Pq), 4.5, SUN, "#fff", 2.2)
    s += text(xT(Tq), oy + 34, "твоя Tᴄ = 92 °C", 9.5, SUN, "middle", "bold")
    s += text(xT(Tq) + 8, yP(Pq) + 4, f"≈ {Pq*100:.0f} %", 10, SUN, "start", "bold")

    s += text(W / 2, H - 12, "Між двома відомими точками крива пряма — значення для проміжної температури беруть лінійною інтерполяцією.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4m-1-curve.svg", s)


# ── Рис. 2.9.4m.2 — правило запасу: робоча точка під кривою ──────────────────
def fig_margin():
    W, H = 720, 410
    s = header(W, H)
    s += text(W / 2, 30, "Правило запасу: робоча точка нижче derating-кривої", 15.5, INK, "middle", "bold")

    ox, oy = 84, 338
    pw, ph = 560, 270
    Tmin, Tmax = 0, 175

    def xT(T):
        return ox + pw * (T - Tmin) / (Tmax - Tmin)

    def yP(p):
        return oy - ph * p / 1.0

    s += arrow(ox, oy, ox, oy - ph - 16, INK, 2)
    s += arrow(ox, oy, ox + pw + 16, oy, INK, 2)
    s += text(ox + pw + 20, oy + 4, "Tᴄ (°C)", 12, INK, "start", "bold")
    s += text(ox - 58, oy - ph - 4, "P / P₂₅", 12, INK, "start", "bold")

    for T in range(0, 176, 25):
        s += line(xT(T), oy, xT(T), oy + 5, INK, 1.2)
        s += text(xT(T), oy + 19, str(T), 9.5, INK, "middle")
    for p in (0, 25, 50, 75, 100):
        yy = yP(p / 100.0)
        s += text(ox - 10, yy + 4, f"{p}%", 9.5, INK, "end")
        s += line(ox, yy, ox + pw, yy, FAINT, 1)

    Tknee, Tmaxj = 25, 150

    def Pc(T):
        if T <= Tknee:
            return 1.0
        if T >= Tmaxj:
            return 0.0
        return (Tmaxj - T) / (Tmaxj - Tknee)

    # повна derating-крива = абсолютна стеля
    full = [(xT(0), yP(1.0)), (xT(Tknee), yP(1.0)), (xT(Tmaxj), yP(0.0))]
    s += _poly(full, RED, 2.8)
    s += _poly([(xT(Tmaxj), yP(0.0)), (xT(Tmax), yP(0.0))], GREY, 2, "4 4")
    s += text(xT(Tknee) + 6, yP(1.0) - 8, "derating-крива = стеля (НЕ переходь)", 9.5, RED, "start", "bold")

    # лінія робочого запасу = 0.7 × крива
    K = 0.7
    work = [(xT(0), yP(K * 1.0)), (xT(Tknee), yP(K * 1.0)), (xT(Tmaxj), yP(0.0))]
    s += _poly(work, GREEN, 2.8, "6 4")
    s += text(xT(60), yP(K * Pc(60)) - 26, "робоча межа = 70 % від кривої", 9.5, GREEN, "start", "bold")

    # зона безпеки (під зеленою) — світло-зелена заливка трикутника
    poly_pts = f"{xT(0):.1f},{oy:.1f} {xT(0):.1f},{yP(K):.1f} {xT(Tknee):.1f},{yP(K):.1f} {xT(Tmaxj):.1f},{oy:.1f}"
    s += f'<polygon points="{poly_pts}" fill="{LGRN}" stroke="none" opacity="0.7"/>\n'
    s += text(xT(40), oy - 26, "тут проєктуй", 10, GREEN, "middle", "bold")

    # робоча точка: Tc=92, P=22% (виразно під зеленою 70%-лінією ≈ 32 %)
    Tq, Pq = 92, 0.22
    s += circle(xT(Tq), yP(Pq), 5, INK, "#fff", 2.4)
    s += text(xT(Tq) + 8, yP(Pq) + 4, "робоча точка", 9.5, INK, "start", "bold")
    s += text(xT(Tq) + 8, yP(Pq) + 18, "(92 °C, 22 %)", 9, INK, "start")

    # стрілка запасу від точки до зеленої лінії
    s += arrow(xT(Tq), yP(Pq), xT(Tq), yP(K * Pc(Tq)), GREEN, 1.8)
    s += text(xT(Tq) - 8, (yP(Pq) + yP(K * Pc(Tq))) / 2, "запас", 8.5, GREEN, "end")

    s += text(W / 2, H - 12, "Спершу опусти стелю за температурою (червона), тоді візьми 70–80 % від неї (зелена). Робоча точка — нижче.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4m-2-margin.svg", s)


if __name__ == "__main__":
    fig_curve()
    fig_margin()
    print("OK — фігури вставки 2.9.4m згенеровано в", OUT)
