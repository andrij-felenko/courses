# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.11.8m
«Оцінка RC-снабера: від струму навантаження до номіналів».

Не чіпає головний figs.py розділу. Унікальні імена файлів у ./img/:
  fig-r11-s8m-1-dvdt.svg     — чому симістор самовмикається: dv/dt комутації
  fig-r11-s8m-2-design.svg   — RC проти LC: демпфування і номінали

Чистий Python, без залежностей (AUTHORING §9). Стиль: білий фон, sans-serif,
'+' червоний, '−' синій, поле зелене, стрілки через marker.
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LYEL  = "#fbf3df"
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: резистор зиґзаґом, конденсатор двома пластинами ────────────────
def res_h(x0, y, length, n=6, amp=7, col=INK):
    seg = length / (n + 1)
    pts = [(x0, y), (x0 + seg / 2, y)]
    x = x0 + seg / 2
    for i in range(n):
        x += seg
        pts.append((x, y - amp if i % 2 == 0 else y + amp))
    pts.append((x0 + length - seg / 2, y))
    pts.append((x0 + length, y))
    return _poly(pts, col, 2.2)


def cap_v(cx, cy, gap=8, plate=18, col=INK):
    s = line(cx - plate / 2, cy - gap, cx + plate / 2, cy - gap, col, 2.6)
    s += line(cx - plate / 2, cy + gap, cx + plate / 2, cy + gap, col, 2.6)
    return s


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 2.11.8m.1 — чому симістор самовмикається: dv/dt комутації
# ══════════════════════════════════════════════════════════════════════════════
def fig1():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 26, "Комутація індуктивного навантаження: чому напруга стрибає різко",
              16, INK, "middle", "bold")

    # осі: вісь часу спільна для струму й напруги на симісторі
    ox, oy = 70, 250
    axw, axh = 620, 150
    s += line(ox, oy - axh - 18, ox, oy + 120, INK, 1.6)        # вертикальна
    s += arrow(ox, oy, ox + axw + 16, oy, INK, 1.8)             # вісь часу
    s += text(ox + axw + 20, oy + 5, "t", 14, INK, "start", "bold")

    # момент комутації (струм через нуль)
    xc = ox + 300
    s += line(xc, oy - axh - 14, xc, oy + 96, GREY, 1.4, "5,4")
    s += text(xc, oy + 114, "струм навантаження = 0  →  симістор замикається",
              12.5, GREY, "middle", "italic")

    # --- струм навантаження I (синусоїда, відстає по фазі) ---
    def cur(j):
        t = j / axw
        return oy - 36 * math.sin(2 * math.pi * 1.0 * t - 0.0)
    pts = []
    for j in range(0, int(axw) + 1):
        # тільки до моменту комутації — потім струм = 0
        if ox + j <= xc:
            pts.append((ox + j, cur(j)))
    s += _poly(pts, COPP, 2.6)
    # після комутації струм нуль (лежить на осі)
    s += line(xc, oy, ox + axw, oy, COPP, 2.6, "2,3")
    s += text(ox + 120, oy + 30, "струм через симістор  I(t)", 13, COPP, "middle", "bold")

    # --- напруга на симісторі ---
    # до комутації — майже нуль (відкритий ключ), після — миттєво з'являється
    # реаплікована напруга мережі (бо струм і напруга не в фазі на L)
    s += line(ox, oy - 4, xc, oy - 4, GREEN, 2.6)
    # різкий фронт угору в момент комутації
    yhi = oy - axh
    s += line(xc, oy - 4, xc + 4, yhi + 6, RED, 3.0)
    # далі повільний спад косинусом (реаплікована напруга мережі)
    pts2 = []
    for j in range(0, int(ox + axw - xc)):
        x = xc + j
        frac = j / (axw)
        y = (yhi + 6) + (oy - 30 - (yhi + 6)) * (1 - math.cos(2 * math.pi * 0.9 * frac)) * 0.5
        pts2.append((x, y))
    s += _poly(pts2, GREEN, 2.6)
    s += text(xc + 150, yhi - 6, "напруга на симісторі  V(t)", 13, GREEN, "middle", "bold")

    # позначка крутого фронту = dv/dt
    s += arrow(xc + 26, yhi + 30, xc + 7, yhi + 12, RED, 1.8)
    s += text(xc + 30, yhi + 40, "крутий фронт", 12.5, RED, "start", "bold")
    s += text(xc + 30, yhi + 56, "dV/dt — внутрішня", 12, RED, "start")
    s += text(xc + 30, yhi + 70, "ємність затвора", 12, RED, "start")
    s += text(xc + 30, yhi + 84, "знову відкриває ключ!", 12, RED, "start", "bold")

    # позначка з демпфованим фронтом (зі снабером) — пунктир, м'яка дуга
    pts3 = []
    for j in range(0, 150):
        x = xc + j
        # експоненційний м'який підйом RC-снабера
        y = (oy - 4) - (axh - 30) * (1 - math.exp(-j / 55.0))
        pts3.append((x, y))
    s += _poly(pts3, BLUE, 2.4, "6,4")
    s += text(xc + 95, oy - 8, "зі снабером:", 12, BLUE, "start", "bold")
    s += text(xc + 95, oy + 7, "пологий підйом", 12, BLUE, "start")

    # підпис осей значень
    s += text(ox - 8, yhi + 4, "+V", 12, INK, "end")
    s += text(ox - 8, oy + 4, "0", 12, INK, "end")

    # нижній висновок
    s += text(W / 2, H - 10,
              "На L струм і напруга не в фазі: коли струм падає до нуля, напруга мережі вже велика — і виникає миттєво.",
              12.5, INK, "middle", "italic")
    save("fig-r11-s8m-1-dvdt.svg", s)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 2.11.8m.2 — RC проти LC: демпфування і номінали
# ══════════════════════════════════════════════════════════════════════════════
def fig2():
    W, H = 770, 470
    s = header(W, H)
    s += text(W / 2, 26, "Снабер = R + C проти індуктивності навантаження: демпфування",
              16, INK, "middle", "bold")

    # ── ліворуч: маленька схема ──
    bx, by, bw, bh = 36, 56, 256, 268
    s += rect(bx, by, bw, bh, "#fcfdff", "#c9d3dc", 1.4, 8)
    s += text(bx + bw / 2, by - 8, "де стоїть снабер", 12.5, INK, "middle", "bold")

    # координати кола: лівий стояк (джерело + L), правий стояк (TRIAC + снабер)
    xL = bx + 46          # лівий провід
    xT = bx + 132         # стояк симістора
    xS = bx + 206         # стояк снабера
    yTop = by + 40        # верхня шина
    yBot = by + 232       # нижня шина

    # джерело мережі
    sy = by + 150
    s += circle(xL, sy, 20, "none", INK, 1.8)
    s += text(xL, sy + 6, "~", 22, INK, "middle", "bold")
    s += text(xL, sy + 40, "мережа", 12, INK, "middle")
    s += text(xL, sy + 54, "230 В", 11.5, GREY, "middle")
    s += line(xL, sy - 20, xL, yTop, INK, 2)
    s += line(xL, sy + 20, xL, yBot, INK, 2)

    # верхня шина до котушки
    s += line(xL, yTop, xT, yTop, INK, 2)
    # котушка навантаження (вертикальна, дужки) на стояку симістора
    cy0 = yTop
    for i in range(4):
        s += f'<path d="M {xT-2},{cy0+i*15:.0f} a 7.5 7.5 0 0 1 0 15" fill="none" stroke="{COPP}" stroke-width="2.4"/>\n'
    yLb = cy0 + 4 * 15
    s += text(xT + 12, cy0 + 18, "L навант.", 12, COPP, "start", "bold")
    s += text(xT + 12, cy0 + 33, "(мотор,", 11, COPP, "start")
    s += text(xT + 12, cy0 + 47, "клапан)", 11, COPP, "start")

    # симістор блоком
    ty = yLb + 40
    s += line(xT, yLb, xT, ty - 18, INK, 2)
    s += rect(xT - 20, ty - 18, 40, 36, LYEL, INK, 1.8, 4)
    s += text(xT, ty + 4, "TRIAC", 11, INK, "middle", "bold")
    s += line(xT, ty + 18, xT, yBot, INK, 2)
    # нижня шина
    s += line(xL, yBot, xS, yBot, INK, 2)

    # снабер: вертикальна гілка R(зверху)+C(знизу) між верхньою шиною симістора і низом
    yMid = (yLb + by + 40) / 2 + 6
    # від верхнього вузла симістора (над блоком) праворуч до стояка снабера
    yTopNode = yLb            # вузол над симістором
    s += line(xT, yTopNode, xS, yTopNode, BLUE, 2)
    # резистор (вертикальний) — намалюємо зиґзаґом по вертикалі
    rA, rB = yTopNode + 6, yTopNode + 56
    seg = (rB - rA) / 7
    zz = [(xS, rA)]
    yy = rA + seg / 2
    zz.append((xS, yy))
    for i in range(6):
        yy += seg
        zz.append((xS - 7 if i % 2 == 0 else xS + 7, yy))
    zz.append((xS, rB - seg / 2))
    zz.append((xS, rB))
    s += _poly(zz, BLUE, 2.2)
    s += text(xS + 14, (rA + rB) / 2 + 4, "R", 13, BLUE, "start", "bold")
    # конденсатор (дві пластини) нижче резистора
    cC = rB + 26
    s += line(xS, rB, xS, cC - 7, BLUE, 2)
    s += line(xS - 13, cC - 7, xS + 13, cC - 7, BLUE, 2.6)
    s += line(xS - 13, cC + 7, xS + 13, cC + 7, BLUE, 2.6)
    s += text(xS + 14, cC + 4, "C", 13, BLUE, "start", "bold")
    s += line(xS, cC + 7, xS, yBot, BLUE, 2)
    s += text(xS, by + bh - 12, "снабер ∥ симістор", 12, BLUE, "middle", "bold")

    # ── праворуч: осцилограма напруги на ключі ──
    ox, oy = 372, 318
    axw, axh = 348, 210
    topY = oy - axh - 6
    s += arrow(ox, oy, ox, topY - 8, INK, 1.8)
    s += arrow(ox, oy, ox + axw + 14, oy, INK, 1.8)
    s += text(ox + axw + 16, oy + 5, "t", 14, INK, "start", "bold")
    s += text(ox + 2, topY - 14, "V на симісторі", 12.5, INK, "start", "bold")

    # Vпік на 0.42 висоти, 2·Vпік на 0.84 — лишаємо headroom зверху
    Vpk = axh * 0.42
    yV = oy - Vpk
    y2 = oy - 2 * Vpk
    s += line(ox, yV, ox + axw, yV, GREY, 1.1, "4,4")
    s += text(ox + axw, yV + 14, "Vпік ≈ 325 В", 11.5, GREY, "end")
    s += line(ox, y2, ox + axw, y2, "#d9a3c4", 1.3, "3,4")
    s += text(ox + axw, y2 - 5, "2·Vпік — небезпека пробою", 11, "#a0418a", "end", "italic")

    # крива 1: БЕЗ снабера — недемпфований дзвін навколо Vпік (overshoot до ~2Vпік)
    pts = []
    for j in range(int(axw)):
        t = j / 20.0
        env = math.exp(-j / 320.0)
        v = Vpk * (1 - env * math.cos(t))
        pts.append((ox + j, oy - v))
    s += _poly(pts, RED, 2.4)
    s += text(ox + 175, topY + 6, "без снабера: різкий фронт + дзвін до 2·Vпік",
              11.5, RED, "middle", "bold")

    # крива 2: ЗІ снабером (критично демпфовано) — м'який вихід без перельоту
    pts2 = []
    for j in range(int(axw)):
        x = j / 26.0
        v = Vpk * (1 - math.exp(-x) * (1 + x))
        pts2.append((ox + j, oy - v))
    s += _poly(pts2, BLUE, 2.8)
    s += text(ox + 232, yV + 30, "зі снабером: пологий фронт,",
              11.5, BLUE, "middle", "bold")
    s += text(ox + 232, yV + 44, "без перельоту", 11.5, BLUE, "middle", "bold")

    # позначка початкового стрибка i·R на синій кривій
    s += arrow(ox + 62, oy - 64, ox + 8, oy - 24, BLUE, 1.6)
    s += text(ox + 66, oy - 66, "стартовий стрибок ≈ I·R", 11.5, BLUE, "start", "bold")
    s += text(ox + 66, oy - 52, "(тому R не роблять великим)", 11, BLUE, "start")

    # внизу — формули номіналів
    fy = H - 60
    s += rect(372, fy - 18, 360, 58, LBLUE, "#c9d3dc", 1.2, 6)
    s += text(380, fy, "C ≈ I / (dV/dt)доп        R ≈ 2ζ·√(L/C)", 13.5, INK, "start", "bold")
    s += text(380, fy + 18, "P(R) ≈ C·Vпік²·f   (тепло перезаряду щопівперіоду)",
              12, INK, "start")

    save("fig-r11-s8m-2-design.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done")
