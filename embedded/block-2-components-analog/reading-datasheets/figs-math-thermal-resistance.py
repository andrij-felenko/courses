# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки r09-s4-m-thermal-resistance (до теми 2.9.4).
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс r09-4m-...), щоб не зачіпати головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки marker; sans-serif.
"""
import os

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


# ── елементи схеми ────────────────────────────────────────────────────────────
def res_v(cx, cy, h, col=INK, w=2.4):
    """Вертикальний резистор (зигзаг) висотою h, центр (cx,cy). Вертає вивідні y."""
    top = cy - h / 2
    bot = cy + h / 2
    n = 6
    seg = (bot - top) / n
    pts = [(cx, top)]
    for i in range(n):
        x = cx + (8 if i % 2 == 0 else -8)
        pts.append((x, top + seg * (i + 0.5)))
    pts.append((cx, bot))
    return _poly(pts, col, w), (top, bot)


def cap_v(cx, cy, col=INK, w=2.6, gap=8, plate=20):
    """Вертикальний конденсатор: дві горизонтальні пластини. Центр (cx,cy)."""
    s = line(cx - plate, cy - gap / 2, cx + plate, cy - gap / 2, col, w)
    s += line(cx - plate, cy + gap / 2, cx + plate, cy + gap / 2, col, w)
    return s


def isource(cx, cy, r=18, col=RED, w=2.4):
    """Джерело струму: коло зі стрілкою вгору."""
    s = circle(cx, cy, r, "none", col, w)
    s += arrow(cx, cy + r * 0.55, cx, cy - r * 0.55, col, w)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.9.4m.1 — теплова RC-модель + словник аналогій (тепло ↔ електрика)
# ─────────────────────────────────────────────────────────────────────────────
def fig1():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Теплова RC-модель: P як струм, Rθ як опір, ΔT як напруга",
              17, INK, "middle", "bold")

    # ── ліва панель: еквівалентна схема ──
    px, py, pw, ph = 30, 52, 360, 392
    s += rect(px, py, pw, ph, "#ffffff", "#c9d3dc", 1.4, 8)
    s += text(px + pw / 2, py + 22, "Еквівалентна схема", 13, INK, "middle", "bold")

    railx_l = px + 70     # ліва шина (вузол кристала)
    railx_r = px + 250    # права шина (земля = повітря, Tamb)
    top_y = py + 60
    bot_y = py + 330

    # джерело струму P між шинами (зліва)
    src_y = (top_y + bot_y) / 2
    s += isource(railx_l, src_y, 20, RED, 2.4)
    s += line(railx_l, top_y, railx_l, src_y - 20, RED, 2.2)
    s += line(railx_l, src_y + 20, railx_l, bot_y, RED, 2.2)
    s += text(railx_l - 30, src_y + 5, "P", 16, RED, "middle", "bold")
    s += text(railx_l - 30, src_y + 24, "(Вт)", 11, RED, "middle")

    # верхній вузол — кристал Tj
    s += line(railx_l, top_y, railx_r, top_y, INK, 2.2)
    s += circle(railx_l, top_y, 3.4, INK, INK, 1)
    s += circle(railx_r, top_y, 3.4, INK, INK, 1)
    s += text(railx_r + 8, top_y - 8, "Tj  (кристал)", 13, RED, "start", "bold")

    # резистор Rθ (зверху) + конденсатор Cθ (паралельно) між Tj і Tamb
    rx = railx_r
    rbody, (rt, rb) = res_v(rx, (top_y + bot_y) / 2, 150, INK, 2.4)
    s += line(rx, top_y, rx, rt, INK, 2.2)
    s += rbody
    s += line(rx, rb, rx, bot_y, INK, 2.2)
    s += text(rx + 16, (top_y + bot_y) / 2 - 6, "Rθ", 16, INK, "start", "bold")
    s += text(rx + 16, (top_y + bot_y) / 2 + 12, "(°C/Вт)", 11, GREY, "start")

    # конденсатор Cθ — окрема гілка праворуч від Rθ
    cx2 = rx + 95
    cmid = (top_y + bot_y) / 2
    s += line(railx_r, top_y, cx2, top_y, INK, 2.0)   # верхній відвід до Cθ
    s += line(cx2, top_y, cx2, cmid - 5, GREEN, 2.2)
    s += cap_v(cx2, cmid, GREEN, 2.6, 9, 18)
    s += line(cx2, cmid + 5, cx2, bot_y, GREEN, 2.2)
    s += line(railx_r, bot_y, cx2, bot_y, INK, 2.0)   # нижній відвід
    s += text(cx2 + 14, cmid - 6, "Cθ", 15, GREEN, "start", "bold")
    s += text(cx2 + 14, cmid + 11, "(Дж/°C)", 11, GREEN, "start")

    # нижня шина — повітря Tamb (земля)
    s += line(railx_l, bot_y, cx2, bot_y, INK, 2.2)
    s += circle(railx_l, bot_y, 3.4, INK, INK, 1)
    # символ землі
    gx, gy = railx_l, bot_y
    s += line(gx, gy, gx, gy + 14, INK, 2.2)
    s += line(gx - 14, gy + 14, gx + 14, gy + 14, INK, 2.4)
    s += line(gx - 9, gy + 19, gx + 9, gy + 19, INK, 2.2)
    s += line(gx - 4, gy + 24, gx + 4, gy + 24, INK, 2.0)
    s += text(gx, gy + 42, "Tamb  (повітря)", 12, BLUE, "middle", "bold")

    # підпис перепаду ΔT
    s += text(px + pw / 2, py + ph - 8, "ΔT = Tj − Tamb = P · Rθ", 13, INK, "middle", "bold")

    # ── права панель: словник аналогій ──
    qx, qy, qw, qh = 412, 52, 318, 392
    s += rect(qx, qy, qw, qh, "#ffffff", "#c9d3dc", 1.4, 8)
    s += text(qx + qw / 2, qy + 22, "Словник: тепло ↔ електрика", 13, INK, "middle", "bold")

    # шапка таблиці
    c1 = qx + 22
    c2 = qx + 150
    c3 = qx + 240
    hy = qy + 50
    s += text(c1, hy, "тепловий світ", 12, INK, "start", "bold")
    s += text(c2, hy, "↔", 14, GREY, "middle", "bold")
    s += text(c3, hy, "електричний", 12, INK, "start", "bold")
    s += line(qx + 14, hy + 8, qx + qw - 14, hy + 8, FAINT, 1.4)

    rows = [
        ("потужність P (Вт)", "струм I (А)", RED),
        ("перепад ΔT (°C)", "напруга V (В)", BLUE),
        ("тепл. опір Rθ (°C/Вт)", "опір R (Ом)", INK),
        ("тепл. ємність Cθ", "ємність C (Ф)", GREEN),
        ("стала τ = Rθ·Cθ", "стала τ = R·C", GREY),
    ]
    ry = hy + 34
    for left, right, col in rows:
        s += text(c1, ry, left, 12.5, col, "start")
        s += text(c2, ry, "↔", 13, GREY, "middle")
        s += text(c3, ry, right, 12.5, col, "start")
        ry += 30

    # закон Ома обома мовами
    by = ry + 6
    s += line(qx + 14, by - 14, qx + qw - 14, by - 14, FAINT, 1.4)
    s += rect(qx + 18, by, qw - 36, 44, LRED, "#e3b7b3", 1.2, 6)
    s += text(qx + qw / 2, by + 19, "ΔT = P · Rθ", 15, RED, "middle", "bold")
    s += text(qx + qw / 2, by + 37, "(як V = I · R)", 12, GREY, "middle")

    by2 = by + 60
    s += rect(qx + 18, by2, qw - 36, 44, LBLUE, "#b9c6e8", 1.2, 6)
    s += text(qx + qw / 2, by2 + 19, "Tj = Tamb + P · Rθ", 15, BLUE, "middle", "bold")
    s += text(qx + qw / 2, by2 + 37, "(температура кристала)", 11, GREY, "middle")

    save("fig-r09-4m-1-thermal-rc.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.9.4m.2 — крива derating як геометрія Tj = Tamb + P·Rθ
# ─────────────────────────────────────────────────────────────────────────────
def fig2():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 30, "Крива derating — це той самий закон Tj = Tamb + P · Rθ",
              17, INK, "middle", "bold")

    ox, oy = 95, 360       # початок осей (лівий низ)
    aw, ah = 560, 280      # довжина осей

    # осі
    s += arrow(ox, oy, ox, oy - ah - 12, INK, 2)
    s += arrow(ox, oy, ox + aw + 14, oy, INK, 2)
    s += text(ox - 14, oy - ah - 20, "P", 14, INK, "middle", "bold")
    s += text(ox - 14, oy - ah - 4, "(Вт)", 10, GREY, "middle")
    s += text(ox + aw + 16, oy + 18, "Tamb (°C)", 13, INK, "start", "bold")

    # температурна шкала: 0..150 °C
    Tmax = 150.0
    Tj = 150.0       # макс. температура кристала
    Tbreak = 25.0    # до цієї точки — повна потужність (поличка)
    Pmax = 220.0     # px-висота повної потужності
    def TX(T):  return ox + aw * (T / Tmax)
    def PY(P):  return oy - ah * (P / 280.0)   # 280 px = верх осі

    # сітка по X
    for T in (0, 25, 50, 75, 100, 125, 150):
        x = TX(T)
        s += line(x, oy, x, oy - ah, FAINT, 1)
        s += text(x, oy + 18, str(T), 11, GREY, "middle")

    # поличка повної потужності до Tbreak
    yfull = PY(Pmax)
    s += line(TX(0), yfull, TX(Tbreak), yfull, RED, 3)
    # похила лінія derating: від (Tbreak, Pmax) до (Tj, 0)
    s += line(TX(Tbreak), yfull, TX(Tj), oy, RED, 3)

    # підпис повної потужності
    s += line(TX(0), yfull, ox, yfull, GREY, 1.2, "3,3")
    s += text(ox - 8, yfull + 4, "Pmax", 12, RED, "end", "bold")

    # точка зламу
    s += circle(TX(Tbreak), yfull, 4, RED, RED, 1)
    s += text(TX(Tbreak) + 6, yfull - 8, "повна потужність", 11.5, RED, "start", "bold")
    s += text(TX(Tbreak) + 6, yfull + 8, "до 25 °C", 11, GREY, "start")

    # точка Tj(max) на осі
    s += circle(TX(Tj), oy, 4, RED, RED, 1)
    s += text(TX(Tj) - 4, oy - 10, "Tj(max)=150 °C", 11.5, RED, "end", "bold")
    s += text(TX(Tj) - 4, oy + 18, "P→0", 11, GREY, "middle")

    # нахил = −1/Rθ: трикутник на похилій
    xa, xb = TX(70), TX(105)
    ya = oy - ah * ((Pmax * (Tj - 70) / (Tj - Tbreak)) / 280.0)
    yb = oy - ah * ((Pmax * (Tj - 105) / (Tj - Tbreak)) / 280.0)
    s += line(xa, ya, xb, ya, BLUE, 1.8)             # ΔTamb
    s += line(xb, ya, xb, yb, BLUE, 1.8)             # ΔP
    s += text((xa + xb) / 2, ya + 16, "ΔTamb", 11, BLUE, "middle", "bold")
    s += text(xb + 6, (ya + yb) / 2, "ΔP", 11, BLUE, "start", "bold")
    s += text((xa + xb) / 2 + 70, (ya + yb) / 2 + 6,
              "нахил = −1 / Rθ", 13, BLUE, "start", "bold")

    # робоча точка: приклад Tamb=85, читаємо дозволену P
    Twork = 85.0
    Pwork = Pmax * (Tj - Twork) / (Tj - Tbreak)
    xw = TX(Twork)
    yw = oy - ah * (Pwork / 280.0)
    s += line(xw, oy, xw, yw, GREEN, 1.6, "4,3")
    s += line(ox, yw, xw, yw, GREEN, 1.6, "4,3")
    s += circle(xw, yw, 4.5, "#ffffff", GREEN, 2.2)
    s += text(xw, oy + 18, "85", 11, GREEN, "middle", "bold")
    s += text(ox - 8, yw + 4, "Pдоз", 11.5, GREEN, "end", "bold")
    s += text(xw + 8, yw - 8, "тут можна лише стільки", 11, GREEN, "start", "bold")

    save("fig-r09-4m-2-derating.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done.")
