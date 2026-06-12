# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.12.5m
«Bandgap у числах: як −2 мВ/°C діода компенсували різницею ΔVbe»
(Розділ 2.12 — Легендарні аналогові ІМС).

Не чіпає головний figs.py розділу: УНІКАЛЬНІ імена файлів у ./img/.
Чистий Python без залежностей. Стиль — AUTHORING §9 (білий фон, sans-serif,
'+' червоний, '−' синій, стрілки через marker). Допоміжні функції скопійовано
з figs.py сусідніх розділів для єдиного вигляду.

Вивід:
  img/fig-r12-5m-1-cancel.svg      — складання двох нахилів у пласку лінію ~1.2 В
  img/fig-r12-5m-2-deltavbe.svg    — звідки береться ΔVbe: два переходи, ln(N)
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


# ───────────────────────────────────────────────────────────────────────────
# Рис. 2.12.5m.1 — Складання нахилів: CTAT VBE + PTAT M·ΔVbe = пласка лінія ~1.2 В
# ───────────────────────────────────────────────────────────────────────────
def fig_cancel():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Два протилежні нахили дають пласку напругу", 17, INK, "middle", "bold")

    # Осі графіка
    ox, oy = 95, 360          # початок осей (лівий-низ)
    gw, gh = 560, 280         # ширина/висота поля
    top = oy - gh

    # вісь напруги (V) і температури (T)
    s += arrow(ox, oy, ox, top - 6, INK, 2)
    s += arrow(ox, oy, ox + gw + 6, oy, INK, 2)
    s += text(ox - 10, top - 12, "напруга, В", 13, INK, "end")
    s += text(ox + gw + 6, oy + 24, "температура →", 13, INK, "end")

    # Температурний діапазон умовно −40…+125 °C по горизонталі
    t_lo, t_hi = -40.0, 125.0
    def tx(t):
        return ox + gw * (t - t_lo) / (t_hi - t_lo)

    # Вертикаль напруги: показуємо 0…1.4 В
    v_lo, v_hi = 0.0, 1.40
    def vy(v):
        return oy - gh * (v - v_lo) / (v_hi - v_lo)

    # сітка по температурі
    for t in (-40, 0, 25, 75, 125):
        x = tx(t)
        s += line(x, oy, x, top, FAINT, 1)
        s += text(x, oy + 18, f"{t}", 11, GREY, "middle")
    s += text(tx(25), oy + 34, "°C", 11, GREY, "middle")

    # горизонтальні рівні напруги
    for v, lab in ((0.0, "0"), (0.6, "0.6"), (1.2, "1.2")):
        y = vy(v)
        s += line(ox, y, ox + gw, y, FAINT, 1)
        s += text(ox - 8, y + 4, lab, 11, GREY, "end")

    # VBE(T): CTAT, ≈ −2 мВ/°C, опорно VBE(25°C)=0.65 В
    vbe25 = 0.65
    slope_vbe = -0.002          # В/°C
    pv = [(tx(t), vy(vbe25 + slope_vbe * (t - 25))) for t in range(-40, 126, 5)]
    s += _poly(pv, BLUE, 2.8)
    s += text(tx(125) + 6, vy(vbe25 + slope_vbe * (125 - 25)) + 4, "VBE", 13, BLUE, "start", "bold")
    s += text(tx(-40) + 6, vy(vbe25 + slope_vbe * (-40 - 25)) - 10, "−2 мВ/°C  (CTAT)", 12, BLUE, "start")

    # M·ΔVbe(T): PTAT, проходить крізь 0 В при 0 К — на цьому відрізку росте.
    # Нахил підбираємо так, щоб точно скасувати −2 мВ/°C: +2 мВ/°C.
    slope_ptat = +0.002
    # значення M·ΔVbe при 25 °C = Vbg − VBE(25) = 1.205 − 0.65 = 0.555 В
    ptat25 = 1.205 - vbe25
    pp = [(tx(t), vy(ptat25 + slope_ptat * (t - 25))) for t in range(-40, 126, 5)]
    s += _poly(pp, RED, 2.8)
    s += text(tx(125) + 6, vy(ptat25 + slope_ptat * (125 - 25)) + 4, "M·ΔVbe", 13, RED, "start", "bold")
    s += text(tx(-40) + 6, vy(ptat25 + slope_ptat * (-40 - 25)) + 18, "+2 мВ/°C  (PTAT)", 12, RED, "start")

    # Сума: VBE + M·ΔVbe = 1.205 В — горизонтальна лінія
    psum = [(tx(t), vy(vbe25 + ptat25)) for t in range(-40, 126, 5)]
    s += _poly(psum, GREEN, 3.4)
    s += text(tx(70), vy(1.205) - 12, "VBE + M·ΔVbe ≈ 1.2 В", 14, GREEN, "middle", "bold")
    s += text(tx(70), vy(1.205) - 30, "нахил ≈ 0", 12, GREEN, "middle")

    # вертикальна підказка про складання при 25 °C
    xs = tx(25)
    s += line(xs, vy(0), xs, vy(vbe25), BLUE, 1.4, "4 3")
    s += line(xs, vy(vbe25), xs, vy(1.205), RED, 1.4, "4 3")

    # легенда-висновок
    s += rect(ox + 12, top + 6, 250, 46, "#ffffff", "#c9d3dc", 1.2, 6)
    s += text(ox + 24, top + 26, "падаюче + зростаюче =", 12, INK, "start")
    s += text(ox + 24, top + 43, "стале (нахили скоротилися)", 12, INK, "start", "bold")

    save("fig-r12-5m-1-cancel.svg", s)


# ───────────────────────────────────────────────────────────────────────────
# Рис. 2.12.5m.2 — Звідки ΔVbe: два переходи з різною щільністю струму, ln(N)
# ───────────────────────────────────────────────────────────────────────────
def _bjt(cx, cy, label, sub, scale=1.0, area_n=1):
    """Спрощене NPN-позначення (коло + три виводи), area_n — умовна площа."""
    r = 26 * scale
    s = circle(cx, cy, r, "#ffffff", INK, 2)
    # база (зліва), колектор (зверху), емітер (знизу зі стрілкою назовні)
    s += line(cx - r, cy, cx - r - 22, cy, INK, 2)               # база
    s += line(cx - r - 8, cy - 12, cx - r - 8, cy + 12, INK, 3)  # «пластина» бази
    s += line(cx - r - 8, cy - 6, cx + 4, cy - r * 0.62, INK, 2)  # до колектора
    s += line(cx + 4, cy - r * 0.62, cx + 4, cy - r - 18, INK, 2)
    s += arrow(cx - r - 8, cy + 6, cx + 4, cy + r * 0.62, INK, 2)  # емітер зі стрілкою
    s += line(cx + 4, cy + r * 0.62, cx + 4, cy + r + 18, INK, 2)
    s += text(cx, cy - r - 26, label, 14, INK, "middle", "bold")
    s += text(cx, cy + r + 34, sub, 12, GREY, "middle")
    return s


def fig_deltavbe():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "ΔVbe народжується з різної щільності струму", 17, INK, "middle", "bold")

    # Два транзистори
    q1x, q2x, qy = 175, 175, 150
    # Q1 — площа ×1, той самий струм I
    s += _bjt(q1x, qy, "Q1", "площа ×1", 1.0)
    # Q2 — площа ×N (більший), той самий струм I  → нижча щільність
    s += _bjt(q2x, qy + 175, "Q2", "площа ×N", 1.0)

    # струмові джерела зверху — однакові I
    for cx, cy, lab in ((q1x + 4, qy - 95, "I"), (q2x + 4, qy + 175 - 95, "I")):
        s += circle(cx, cy, 16, "#ffffff", GREEN, 2)
        s += arrow(cx, cy + 9, cx, cy + 9 + 24, GREEN, 2)
        s += text(cx + 22, cy + 4, lab, 13, GREEN, "start", "bold")
        s += text(cx + 22, cy + 20, "(однаковий)", 11, GREY, "start")

    # підписи VBE кожного
    s += text(q1x - 70, qy + 4, "VBE1", 13, BLUE, "end", "bold")
    s += text(q2x - 70, qy + 175 + 4, "VBE2", 13, BLUE, "end", "bold")
    s += text(q1x - 70, qy + 22, "більша", 11, GREY, "end")
    s += text(q2x - 70, qy + 175 + 22, "менша", 11, GREY, "end")

    # Велика дужка/стрілка: різниця VBE
    bx = 360
    s += arrow(bx, qy, bx, qy + 175, RED, 2)
    s += arrow(bx, qy + 175, bx, qy, RED, 2)
    s += text(bx + 14, (qy + qy + 175) / 2 - 6, "ΔVbe = VBE1 − VBE2", 14, RED, "start", "bold")

    # формула-блок праворуч
    fx, fy = bx + 14, (qy + qy + 175) / 2 + 24
    s += rect(fx, fy, 360, 150, LRED, "#e6b9b6", 1.4, 8)
    s += text(fx + 18, fy + 30, "ΔVbe = U_T · ln(N)", 17, INK, "start", "bold")
    s += text(fx + 18, fy + 56, "U_T = kT/q ≈ 26 мВ  (за 300 К)", 13, INK, "start")
    s += text(fx + 18, fy + 80, "N — відношення щільностей струму", 12, GREY, "start")
    s += text(fx + 18, fy + 100, "N = 8  →  ΔVbe ≈ 26·ln8 ≈ 54 мВ", 13, INK, "start")
    s += text(fx + 18, fy + 124, "PTAT: росте прямо з T  (+слабкий нахил)", 12, RED, "start", "bold")

    # нижня підказка
    s += text(W / 2, H - 14,
              "Один VBE — велике падіння (CTAT). Їхня РІЗНИЦЯ — мала, чиста й PTAT.",
              13, INK, "middle")

    save("fig-r12-5m-2-deltavbe.svg", s)


if __name__ == "__main__":
    fig_cancel()
    fig_deltavbe()
    print("done.")
