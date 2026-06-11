# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для вставки 🔌 §1.7.6c — «Розетка: фаза, нуль, захисний провідник і 230 В RMS».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (префікс fig-7-6c-).
НЕ чіпає головний figs.py розділу. Стиль (AUTHORING §9): білий фон; '+' червоний,
'−' синій; поле зелене; sans-serif. Хелпери скопійовано з figs.py розділу (самодостатність).
"""
import os
import math

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
YELLOWGREEN = "#9aa81f"
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


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.7.6c.1 — розетка зсередини: три провідники (L/N/PE), куди йдуть і чому
# ─────────────────────────────────────────────────────────────────────────────
def fig1_socket_pinout():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Розетка зсередини: три провідники й куди вони йдуть",
              17, INK, "middle", "bold")

    # --- зліва: схематична розетка з трьома затискачами ------------------------
    fx, fy = 175, 250          # центр лицьової панелі
    s += circle(fx, fy, 108, "#f4f4f4", INK, 2.5)        # корпус розетки
    s += circle(fx, fy, 78, "#fbfbfb", GREY, 1.6)        # заглиблення
    # два штепсельні отвори (L і N) — симетрично
    holeL = (fx - 34, fy + 8)
    holeN = (fx + 34, fy + 8)
    s += rect(holeL[0] - 6, holeL[1] - 20, 12, 40, "#fff", INK, 2, 3)
    s += rect(holeN[0] - 6, holeN[1] - 20, 12, 40, "#fff", INK, 2, 3)
    # захисний контакт (PE) — пелюстки збоку (Schuko-тип)
    s += rect(fx - 70, fy - 6, 16, 12, YELLOWGREEN, INK, 1.6, 2)
    s += rect(fx + 54, fy - 6, 16, 12, YELLOWGREEN, INK, 1.6, 2)
    s += text(fx, fy + 92, "лицьовий бік (Schuko-тип)", 12.5, GREY, "middle", "normal", "italic")
    # підписи отворів
    s += text(holeL[0], holeL[1] - 28, "L", 14, RED, "middle", "bold")
    s += text(holeN[0], holeN[1] - 28, "N", 14, BLUE, "middle", "bold")
    s += text(fx - 62, fy - 14, "PE", 12, GREEN, "middle", "bold")
    s += text(fx + 62, fy - 14, "PE", 12, GREEN, "middle", "bold")

    # три кольорові «хвости» проводів, що виходять праворуч до колонки призначень
    cx0 = 300
    # L (коричневий) — від лівого отвору
    s += line(holeL[0], holeL[1] + 20, holeL[0], 392, COPPER, 5)
    s += line(holeL[0], 392, cx0, 392, COPPER, 5)
    # N (синій)
    s += line(holeN[0], holeN[1] + 20, holeN[0], 416, BLUE, 5)
    s += line(holeN[0], 416, cx0, 416, BLUE, 5)
    # PE (жовто-зелений) — від бічних пелюсток
    s += line(fx + 62, fy + 6, fx + 62, 368, YELLOWGREEN, 5)
    s += line(fx + 62, 368, cx0, 368, YELLOWGREEN, 5)

    # --- праворуч: три рядки-призначення ---------------------------------------
    rx = cx0 + 18
    rows = [
        (368, YELLOWGREEN, "PE — захисний (protective earth)", "жовто-зелений",
         "до контуру заземлення; у нормі струму не несе"),
        (392, COPPER, "L — фаза (line, «гаряча»)", "коричневий / чорний",
         "несе 230 В RMS відносно землі; рве запобіжник"),
        (416, BLUE, "N — нуль (neutral)", "синій",
         "зворотний провід; ≈0 В відносно землі"),
    ]
    for y, col, name, colour, note in rows:
        s += circle(rx - 6, y, 7, col, INK, 1.4)
        s += text(rx + 10, y - 4, name, 14, INK, "start", "bold")
        s += text(rx + 10, y + 13, colour + " · " + note, 11.5, GREY, "start")

    # рамка-нагадування: на двоконтактних вилках PE немає
    bx, by, bw, bh = rx + 8, 300, 300, 44
    s += rect(bx, by, bw, bh, "#fff", GREY, 1.4, 6)
    s += text(bx + 12, by + 18, "Двоконтактна вилка (клас II)", 12.5, INK, "start", "bold")
    s += text(bx + 12, by + 35, "PE не підключають — захист дає подвійна ізоляція ▱",
              11.5, GREY, "start")

    # верхня підказка над розеткою
    s += text(rx, 70, "Контакти однакові на вигляд — різні за роллю:", 13, INK, "start", "bold")
    s += text(rx, 90, "не плутай їх місцями, інакше корпус приладу стане «гарячим».",
              11.8, GREY, "start", "normal", "italic")

    save("fig-7-6c-1-socket-pinout.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.7.6c.2 — що означає «230 В»: RMS vs амплітуда vs розмах на синусоїді
# ─────────────────────────────────────────────────────────────────────────────
def fig2_rms_levels():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Що насправді означає «230 В» у розетці", 17, INK, "middle", "bold")

    # система координат
    ox, oy = 90, 205          # початок осі (нуль напруги)
    axw = 520                 # довжина осі часу
    amp = 150                 # пікселів на амплітуду (325 В)
    s += line(ox, oy, ox + axw, oy, INK, 2)                  # вісь часу
    s += arrow(ox + axw, oy, ox + axw + 18, oy, INK, 2)
    s += text(ox + axw + 22, oy + 5, "t", 14, INK, "start", "bold", "italic")
    s += line(ox, oy + amp + 22, ox, oy - amp - 22, INK, 2)  # вісь напруги
    s += arrow(ox, oy - amp - 22, ox, oy - amp - 40, INK, 2)
    s += text(ox - 10, oy - amp - 30, "v", 14, INK, "end", "bold", "italic")

    # синусоїда 1.75 періоду
    cycles = 1.75
    n = 200
    pts = []
    for i in range(n + 1):
        frac = i / n
        x = ox + frac * axw
        y = oy - amp * math.sin(2 * math.pi * cycles * frac)
        pts.append((x, y))
    s += polyline(pts, RED, 2.8)

    # рівні: +Vpk, +Vrms, -Vrms, -Vpk
    vrms = amp / math.sqrt(2)
    # лінія піка +325
    s += line(ox, oy - amp, ox + axw, oy - amp, GREY, 1.4, "6 5")
    s += line(ox, oy + amp, ox + axw, oy + amp, GREY, 1.4, "6 5")
    # лінія RMS +-230
    s += line(ox, oy - vrms, ox + axw, oy - vrms, GREEN, 1.8, "3 4")
    s += line(ox, oy + vrms, ox + axw, oy + vrms, GREEN, 1.8, "3 4")

    # підписи рівнів праворуч
    lx = ox + axw - 4
    s += text(lx, oy - amp - 8, "+Vₚₖ ≈ +325 В  (амплітуда)", 12.5, INK, "end", "bold")
    s += text(lx, oy + amp + 18, "−Vₚₖ ≈ −325 В", 12.5, INK, "end", "bold")
    s += text(lx, oy - vrms - 7, "+230 В RMS  (діюче)", 12.5, GREEN, "end", "bold")
    s += text(lx, oy + vrms + 16, "−230 В RMS", 12.5, GREEN, "end", "bold")
    s += text(ox + 8, oy - 8, "0 В", 12, GREY, "start")

    # подвійна стрілка розмаху (peak-to-peak) ліворуч від осі
    ppx = ox - 34
    s += arrow(ppx, oy - amp, ppx, oy + amp, BLUE, 1.8)
    s += arrow(ppx, oy + amp, ppx, oy - amp, BLUE, 1.8)
    s += text(ppx - 6, oy - amp - 6, "розмах", 11.5, BLUE, "end", "bold")
    s += text(ppx - 6, oy + amp + 16, "≈650 Вₚₚ", 11.5, BLUE, "end", "bold")

    # формула-зв'язок унизу
    by = H - 30
    s += rect(40, by - 24, W - 80, 44, "#f6f6f6", GREY, 1.3, 6)
    s += text(W / 2, by - 5,
              "Vₚₖ = Vrms · √2 = 230 · 1.414 ≈ 325 В     Vₚₚ = 2·Vₚₖ ≈ 650 В",
              13.5, INK, "middle", "bold")
    s += text(W / 2, by + 13,
              "«230 В» — це RMS: стільки ж тепла, скільки дали б 230 В постійних",
              11.8, GREY, "middle", "normal", "italic")

    save("fig-7-6c-2-rms-levels.svg", s)


if __name__ == "__main__":
    fig1_socket_pinout()
    fig2_rms_levels()
    print("done:", OUT)
