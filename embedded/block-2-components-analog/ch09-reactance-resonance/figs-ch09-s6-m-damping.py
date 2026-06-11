# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.3.6m — «Коливання з демпфуванням».
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-9-6md-*).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано
з figs.py розділу (єдиний вигляд).
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


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


def spring(x0, y0, x1, y1, coils=7, amp=10, col=INK, w=2):
    """Пружина-зигзаг між двома точками (вертикальна або горизонтальна)."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length      # уздовж
    nx, ny = -uy, ux                        # упоперек
    lead = length * 0.14
    pts = [(x0, y0), (x0 + ux * lead, y0 + uy * lead)]
    body = length - 2 * lead
    n = coils * 2
    for i in range(1, n):
        t = lead + body * i / n
        side = amp if i % 2 == 1 else -amp
        pts.append((x0 + ux * t + nx * side, y0 + uy * t + ny * side))
    pts.append((x0 + ux * (length - lead), y0 + uy * (length - lead)))
    pts.append((x1, y1))
    return _poly(pts, col, w)


def dashpot(cx, cy, x1, y1, col=INK, w=2):
    """Демпфер (поршень у циліндрі) уздовж відрізка (cx,cy)->(x1,y1)."""
    dx, dy = x1 - cx, y1 - cy
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    s = ""
    # шток зверху
    s += line(cx, cy, cx + ux * length * 0.34, cy + uy * length * 0.34, col, w)
    # поршень
    px, py = cx + ux * length * 0.34, cy + uy * length * 0.34
    s += line(px + nx * 13, py + ny * 13, px - nx * 13, py - ny * 13, col, w + 0.6)
    # циліндр (три стінки)
    bx, by = cx + ux * length, cy + uy * length        # дно
    s += line(px + nx * 16, py + ny * 16, bx + nx * 16, by + ny * 16, col, w)
    s += line(px - nx * 16, py - ny * 16, bx - nx * 16, by - ny * 16, col, w)
    s += line(bx + nx * 16, by + ny * 16, bx - nx * 16, by - ny * 16, col, w)
    return s


# ── Рис. 2.3.6m.1 — три режими відгуку на поштовх ────────────────────────────
def fig_three_regimes():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Три режими: як система повертається в спокій після поштовху",
              20, INK, "middle", "bold")
    s += text(W / 2, 58, "відгук на ступінчастий поштовх залежно від коефіцієнта демпфування ζ",
              12.5, GREY, "middle", style="italic")

    ox, oy = 90, H - 64
    w, h = W - 190, H - 150
    s += _axes(ox, oy, w, h, "час t", "відгук")
    # рівень усталення (ціль = 1)
    yset = oy - h * 0.72
    s += line(ox, yset, ox + w, yset, GREY, 1.4, "5 4")
    s += text(ox + w + 16, yset + 4, "ціль", 12, GREY, "start")

    N = 260
    tmax = 13.0

    def curve(zeta, col, wv=2.6, dash=None):
        pts = []
        for j in range(N + 1):
            t = tmax * j / N
            if zeta < 1.0:
                wd = math.sqrt(1 - zeta * zeta)
                y = 1 - math.exp(-zeta * t) * (math.cos(wd * t) + (zeta / wd) * math.sin(wd * t))
            elif abs(zeta - 1.0) < 1e-6:
                y = 1 - math.exp(-t) * (1 + t)
            else:
                r = math.sqrt(zeta * zeta - 1)
                s1 = -zeta + r
                s2 = -zeta - r
                # y(0)=0, y(inf)=1: коефіцієнти партикулярного розкладу
                a1 = s2 / (s1 - s2)
                a2 = -s1 / (s1 - s2)
                y = 1 + a1 * math.exp(s1 * t) + a2 * math.exp(s2 * t)
            pts.append((ox + w * j / N, oy - (oy - yset) * y))
        return _poly(pts, col, wv, dash)

    # перегасований (ζ=2.2) — повільно, без перельоту
    s += curve(2.2, GREEN, 2.6)
    # критичний (ζ=1) — найшвидше без перельоту
    s += curve(1.0, INK, 3.0)
    # недогасований (ζ=0.18) — дзвенить
    s += curve(0.18, RED, 2.6)

    # легенда
    lx, ly = ox + w - 250, oy - h + 6
    s += rect(lx - 12, ly - 18, 262, 86, "#fff", FAINT, 1.4, 8)
    s += line(lx, ly, lx + 26, ly, RED, 2.6)
    s += text(lx + 32, ly + 4, "ζ < 1  недогасований — перельоти, дзвін", 12.5, RED, "start")
    s += line(lx, ly + 24, lx + 26, ly + 24, INK, 3.0)
    s += text(lx + 32, ly + 28, "ζ = 1  критичний — найшвидше без дзвону", 12.5, INK, "start")
    s += line(lx, ly + 48, lx + 26, ly + 48, GREEN, 2.6)
    s += text(lx + 32, ly + 52, "ζ > 1  перегасований — мляво, без дзвону", 12.5, GREEN, "start")

    # підписи на кривих
    s += text(ox + 150, yset - 64, "перельоти", 12, RED, "middle", style="italic")
    s += text(ox + w - 80, oy - 18, "повільно повзе", 12, GREEN, "middle", style="italic")
    return s


# ── Рис. 2.3.6m.2 — маса–пружина–демпфер ↔ RLC ───────────────────────────────
def fig_spring_damper():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 36, "Маса–пружина–демпфер ↔ послідовний RLC: той самий маятник",
              20, INK, "middle", "bold")
    s += text(W / 2, 58, "механічна система й електричний контур описуються однаковим рівнянням",
              12.5, GREY, "middle", style="italic")

    # ── ліворуч: механіка ──
    cx = 215
    top = 96
    s += line(cx - 110, top, cx + 110, top, INK, 4)          # стеля
    for i in range(9):
        xx = cx - 100 + i * 25
        s += line(xx, top, xx - 9, top - 12, GREY, 1.6)      # штрихування стелі

    mass_y = 320
    mass_h = 74
    # пружина ліворуч, демпфер праворуч
    s += spring(cx - 42, top, cx - 42, mass_y - mass_h / 2, 8, 13, BLUE, 2.2)
    s += dashpot(cx + 42, top, cx + 42, mass_y - mass_h / 2, RED, 2.2)
    s += text(cx - 86, (top + mass_y) / 2, "пружина", 12.5, BLUE, "middle", style="italic")
    s += text(cx - 86, (top + mass_y) / 2 + 16, "k = 1/C", 12.5, BLUE, "middle", "bold")
    s += text(cx + 92, (top + mass_y) / 2, "демпфер", 12.5, RED, "middle", style="italic")
    s += text(cx + 92, (top + mass_y) / 2 + 16, "b = R", 12.5, RED, "middle", "bold")

    # маса
    s += rect(cx - 60, mass_y - mass_h / 2, 120, mass_h, LGRN, GREEN, 2.4, 6)
    s += text(cx, mass_y - 4, "маса m", 15, INK, "middle", "bold")
    s += text(cx, mass_y + 16, "= L", 13.5, GREEN, "middle", "bold")
    # стрілка зміщення
    s += arrow(cx, mass_y + mass_h / 2 + 8, cx, mass_y + mass_h / 2 + 48, INK, 2)
    s += text(cx + 8, mass_y + mass_h / 2 + 36, "зміщення x  ↔  заряд q", 12.5, INK, "start")

    # ── праворуч: RLC ──
    bx = 600
    by = 150
    bw = 220
    bh = 230
    # прямокутна петля RLC
    s += line(bx, by, bx + bw, by, INK, 2.4)          # верх
    s += line(bx, by, bx, by + bh, INK, 2.4)          # ліво
    s += line(bx + bw, by, bx + bw, by + bh, INK, 2.4)  # право
    s += line(bx, by + bh, bx + bw, by + bh, INK, 2.4)  # низ
    # котушка на верхній стороні
    s += rect(bx + bw / 2 - 34, by - 12, 68, 24, "#fff", COPP, 0)
    for i in range(5):
        s += f'<ellipse cx="{bx + bw/2 - 24 + i*12:.1f}" cy="{by:.1f}" rx="5" ry="11" fill="none" stroke="{COPP}" stroke-width="2"/>\n'
    s += text(bx + bw / 2, by - 22, "L  (= маса)", 13, GREEN, "middle", "bold")
    # конденсатор на правій стороні
    s += rect(bx + bw - 12, by + bh / 2 - 16, 24, 32, "#fff", "#fff", 0)
    s += line(bx + bw - 11, by + bh / 2 - 16, bx + bw + 11, by + bh / 2 - 16, INK, 2.8)
    s += line(bx + bw - 11, by + bh / 2 + 16, bx + bw + 11, by + bh / 2 + 16, INK, 2.8)
    s += text(bx + bw + 18, by + bh / 2 - 6, "C", 13, BLUE, "start", "bold")
    s += text(bx + bw + 18, by + bh / 2 + 12, "(= 1/k)", 11.5, BLUE, "start")
    # резистор на лівій стороні (зигзаг)
    rseg = []
    ry0 = by + bh / 2 - 26
    for i in range(7):
        side = 9 if i % 2 == 0 else -9
        rseg.append((bx + side, ry0 + i * 8.6))
    s += line(bx, by + bh / 2 - 34, bx, ry0, INK, 2.4)
    s += _poly(rseg, RED, 2.4)
    s += line(bx, ry0 + 6 * 8.6, bx, by + bh / 2 + 34, INK, 2.4)
    s += text(bx - 14, by + bh / 2, "R", 13, RED, "end", "bold")
    s += text(bx - 14, by + bh / 2 + 18, "(= демпфер)", 11.5, RED, "end")
    # струм
    s += arrow(bx + 40, by + bh, bx + 90, by + bh, GREEN, 2)
    s += text(bx + bw / 2, by + bh + 22, "струм i  ↔  швидкість v", 12.5, INK, "middle")

    # ── рівняння внизу ──
    eqy = 446
    s += rect(70, eqy - 26, W - 140, 46, "#fff", FAINT, 1.4, 8)
    s += text(W / 2, eqy - 4, "m·x¨ + b·x˙ + k·x = 0      ↔      L·q¨ + R·q˙ + (1/C)·q = 0",
              16, INK, "middle", "bold")
    s += text(W / 2, eqy + 15, "однакова форма → однакові ζ, ω₀ і три режими", 12.5, GREY, "middle", style="italic")
    return s


# ── Рис. 2.3.6m.3 — числова вісь ζ і зв'язок із Q ────────────────────────────
def fig_zeta_axis():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 36, "Вісь демпфування ζ і дзеркальна вісь добротності Q",
              20, INK, "middle", "bold")
    s += text(W / 2, 58, "ζ = 1/(2Q): більше демпфування — менша добротність (і навпаки)",
              12.5, GREY, "middle", style="italic")

    ox = 70
    w = W - 150
    yz = 150
    # вісь ζ
    s += arrow(ox, yz, ox + w + 14, yz, INK, 2)
    s += text(ox + w + 18, yz + 5, "ζ", 15, INK, "start", "bold")

    zmax = 2.4
    def zx(z):
        return ox + w * min(z, zmax) / zmax

    # зони
    s += rect(ox, yz - 30, zx(1.0) - ox, 30, LRED, "none", 0)
    s += rect(zx(1.0), yz - 30, zx(zmax) - zx(1.0), 30, LGRN, "none", 0)
    s += text((ox + zx(1.0)) / 2, yz - 38, "ζ < 1  недогасований (дзвенить)", 12.5, RED, "middle", "bold")
    s += text((zx(1.0) + zx(zmax)) / 2, yz - 38, "ζ > 1  перегасований", 12.5, GREEN, "middle", "bold")

    for z, lab, col in [(0.0, "0", INK), (0.18, "0.18", RED), (0.5, "0.5", RED),
                        (0.707, "0.707", BLUE), (1.0, "1  крит.", INK), (2.0, "2", GREEN)]:
        x = zx(z)
        s += line(x, yz - 6, x, yz + 6, col, 2.2)
        s += text(x, yz + 22, lab, 12, col, "middle", "bold" if z in (1.0, 0.707) else "normal")
    s += circle(zx(1.0), yz, 6, "#fff", INK, 2.4)

    # критична точка — підпис
    s += text(zx(1.0), yz + 44, "↑ критичне демпфування — межа дзвону", 12, INK, "middle", style="italic")
    s += text(zx(0.707), yz + 62, "ζ = 1/√2 ≈ 0.707 → Q ≈ 0.71: «максимально пласка» межа (АЧХ, §2.4)",
              11.5, BLUE, "middle", style="italic")

    # формула зв'язку
    fy = 300
    s += rect(70, fy - 26, W - 140, 44, "#fff", FAINT, 1.4, 8)
    s += text(W / 2, fy - 2, "ζ = 1 / (2Q)        Q = 1 / (2ζ)        Q = 1 → ζ = 0.5",
              16, INK, "middle", "bold")
    s += text(W / 2, fy + 16, "висока Q (гострий резонанс, §2.3.6) = мале ζ (слабке демпфування, довгий дзвін)",
              12, GREY, "middle", style="italic")
    return s


if __name__ == "__main__":
    save("fig-9-6md-1-three-regimes.svg", fig_three_regimes())
    save("fig-9-6md-2-spring-damper.svg", fig_spring_damper())
    save("fig-9-6md-3-zeta-axis.svg", fig_zeta_axis())
    print("done.")
