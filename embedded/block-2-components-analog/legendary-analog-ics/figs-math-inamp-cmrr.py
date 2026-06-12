# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 2.12.7m — «Чому саме три ОП: підсилення
інструментального підсилювача й CMRR» (Модуль 2, Розділ 2.12).

Окремий скрипт вставки (НЕ головний figs.py розділу). Чистий Python без
залежностей. Вивід → ./img/ із УНІКАЛЬНИМИ іменами (префікс inamp-).
Допоміжні функції скопійовано зі стилю Розділу 13 (AUTHORING §9):
білий фон; '+' червоний, '−' синій; стрілки через marker; шрифт sans-serif.
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
LYEL  = "#fbf6e6"
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


def dot(cx, cy, r=3.4, col=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def opamp_sym(cx, cy, w=66, h=58, plus_top=False, label=None):
    """Трикутник ОП вершиною вправо. plus_top — '+' зверху чи знизу."""
    t = (f'<path d="M {cx-w/2:.0f},{cy-h/2:.0f} L {cx-w/2:.0f},{cy+h/2:.0f} '
         f'L {cx+w/2:.0f},{cy:.0f} Z" fill="#fbfbfb" stroke="{INK}" stroke-width="1.8"/>\n')
    top_sym, bot_sym = ("+", "−") if plus_top else ("−", "+")
    top_col, bot_col = (RED, BLUE) if plus_top else (BLUE, RED)
    t += text(cx - w / 2 + 12, cy - h / 4 + 5, top_sym, 15, top_col, "middle", "bold")
    t += text(cx - w / 2 + 12, cy + h / 4 + 5, bot_sym, 15, bot_col, "middle", "bold")
    if label:
        t += text(cx - 2, cy + 5, label, 13, GREY, "middle", "bold")
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.12.7m.1 — топологія «три ОП»: два буфери + Rg, потім різницевий каскад
# ─────────────────────────────────────────────────────────────────────────────
def fig_topology():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 26, "Інструментальний підсилювач: три ОП", 17, INK, "middle", "bold")

    yt, yb = 120, 320     # верхня й нижня шини (виходи буферів)

    # рамки каскадів (малюємо першими — як підкладку)
    s += rect(150, 64, 230, 312, "none", GREEN, 1.4, 10)
    s += text(160, 84, "1) буфери + Rg: усе підсилення", 12, GREEN, "start", "bold")
    s += rect(398, 96, 320, 280, "none", BLUE, 1.4, 10)
    s += text(408, 116, "2) різницевий каскад: ріже синфазне", 12, BLUE, "start", "bold")

    # ── входи ──
    s += text(36, yt + 4, "V₊", 16, RED, "start", "bold")
    s += text(36, yb + 4, "V₋", 16, BLUE, "start", "bold")
    s += arrow(58, yt, 100, yt, RED, 2)
    s += arrow(58, yb, 100, yb, BLUE, 2)

    # ── буфери A1 (верх), A2 (низ) ──
    a1x, a2x = 210, 210
    s += opamp_sym(a1x, yt, 70, 60, plus_top=True, label="A1")
    s += opamp_sym(a2x, yb, 70, 60, plus_top=False, label="A2")
    s += line(100, yt, a1x - 35, yt - 15, RED, 2)   # V+ → «+» A1 (верх)
    s += line(100, yb, a2x - 35, yb + 15, BLUE, 2)  # V− → «+» A2 (низ)

    # виходи буферів на шини
    s += line(a1x + 35, yt, 470, yt, INK, 2)
    s += line(a2x + 35, yb, 470, yb, INK, 2)
    s += text(a1x + 42, yt - 9, "Va", 13, INK, "start", "bold")
    s += text(a2x + 42, yb + 18, "Vb", 13, INK, "start", "bold")

    # ── мережа підсилення R — R_g — R на вертикалі xg ──
    xg = 320
    inv1y, inv2y = yt + 15, yb - 15        # інвертуючі входи буферів
    nT, nB = 176, 264                       # вузли: верхній (=інв.А1), нижній (=інв.А2)

    def res_v(cy, h, lab, col=INK):
        r = rect(xg - 9, cy - h / 2, 18, h, "#ffffff", col, 1.8, 3)
        r += text(xg + 15, cy + 5, lab, 13, col, "start", "bold")
        return r

    # верхня шина Va спускається на xg і входить у верхній R
    s += dot(xg, yt)
    s += line(xg, yt, xg, 126, INK, 2)
    s += res_v(140, 28, "R")                 # верхній R: Va → вузол nT
    s += line(xg, 154, xg, nT, INK, 2)
    s += dot(xg, nT)
    s += res_v(220, 40, "Rg", GREEN)         # Rg між вузлами
    s += line(xg, nT, xg, 200, INK, 2)
    s += line(xg, 240, xg, nB, INK, 2)
    s += dot(xg, nB)
    s += res_v(300, 28, "R")                 # нижній R: вузол nB → Vb
    s += line(xg, nB, xg, 286, INK, 2)
    s += line(xg, 314, xg, yb, INK, 2)
    s += dot(xg, yb)

    # відведення вузлів на інвертуючі входи буферів (ліворуч)
    s += line(a1x - 35, inv1y, 250, inv1y, INK, 2)
    s += line(250, inv1y, 250, nT, INK, 2)
    s += line(250, nT, xg, nT, INK, 2)
    s += line(a2x - 35, inv2y, 250, inv2y, INK, 2)
    s += line(250, inv2y, 250, nB, INK, 2)
    s += line(250, nB, xg, nB, INK, 2)

    # ── різницевий каскад A3 ──
    a3x, a3y = 590, 216
    inv3y, non3y = a3y - 15, a3y + 15

    def res_h(cx, cy, lab, w=40):
        r = rect(cx - w / 2, cy - 9, w, 18, "#ffffff", INK, 1.8, 3)
        r += text(cx, cy - 13, lab, 12, INK, "middle", "bold")
        return r

    # Va → R₁ → «−» A3
    s += dot(470, yt)
    s += line(470, yt, 470, inv3y, INK, 2)
    s += line(470, inv3y, 488, inv3y, INK, 2)
    s += res_h(515, inv3y, "R₁")
    s += line(535, inv3y, a3x - 36, inv3y, INK, 2)
    s += dot(498, inv3y)

    # Vb → R₁ → «+» A3
    s += dot(470, yb)
    s += line(470, yb, 470, non3y, INK, 2)
    s += line(470, non3y, 488, non3y, INK, 2)
    s += res_h(515, non3y, "R₁")
    s += line(535, non3y, a3x - 36, non3y, INK, 2)
    s += dot(498, non3y)

    # дільник R₂ з «+» на землю
    s += line(498, non3y, 498, 300, INK, 2)
    s += rect(498 - 9, 300, 18, 30, "#ffffff", INK, 1.8, 3)
    s += text(514, 320, "R₂", 12, INK, "start", "bold")
    s += line(498, 330, 498, 348, INK, 2)
    s += line(486, 348, 510, 348, INK, 2.4)
    s += line(490, 353, 506, 353, INK, 2.0)
    s += line(494, 358, 502, 358, INK, 1.6)

    # ОП A3 і вихід
    s += opamp_sym(a3x, a3y, 72, 62, plus_top=False, label="A3")
    s += line(a3x + 36, a3y, 670, a3y, INK, 2)
    s += dot(652, a3y)
    s += arrow(670, a3y, 724, a3y, INK, 2)
    s += text(712, a3y - 12, "Vout", 14, INK, "middle", "bold")
    # зворотний зв'язок R₂: вихід → «−» A3
    s += line(652, a3y, 652, 150, INK, 2)
    s += line(652, 150, 498, 150, INK, 2)
    s += rect((498 + 652) / 2 - 20, 141, 40, 18, "#ffffff", INK, 1.8, 3)
    s += text((498 + 652) / 2, 136, "R₂", 12, INK, "middle", "bold")
    s += line(498, 150, 498, inv3y, INK, 2)

    # формула-підсумок
    s += rect(150, 392, 484, 36, LYEL, "#d8c98a", 1.4, 8)
    s += text(168, 415, "G = (1 + 2R/Rg) · (R₂/R₁)   — підсилення задає один резистор Rg", 14, INK, "start", "bold")

    save("inamp-topology.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.12.7m.2 — синфазне проти диференційного: що каскад робить із кожним
# ─────────────────────────────────────────────────────────────────────────────
def fig_cm_vs_dm():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 26, "Два сигнали на одному вході: що з ними робить in-amp", 16, INK, "middle", "bold")

    # ── ліва панель: диференційний сигнал ──
    bx = 60
    s += rect(bx, 56, 300, 280, "none", "#c9d3dc", 1.4, 10)
    s += text(bx + 150, 78, "Корисний (диференційний) сигнал", 13, GREEN, "middle", "bold")
    # два дроти з малими протифазними коливаннями на спільному п'єдесталі
    base = 150
    s += text(bx + 18, base - 70, "V₊", 13, RED, "start", "bold")
    s += text(bx + 18, base + 78, "V₋", 13, BLUE, "start", "bold")
    # синусоїди (мала амплітуда, протифаза) на п'єдесталі base
    def small_sine(ox, oy, w, amp, cycles, col, phase=0.0, wv=2.2):
        pts = [(ox + j, oy - amp * math.sin(2 * math.pi * cycles * (j / w) + phase))
               for j in range(int(w) + 1)]
        return _poly(pts, col, wv)
    s += line(bx + 40, base - 40, bx + 250, base - 40, GREY, 1.2, "4 4")  # рівень V+ сер.
    s += line(bx + 40, base + 40, bx + 250, base + 40, GREY, 1.2, "4 4")  # рівень V- сер.
    s += small_sine(bx + 40, base - 40, 210, 18, 1.4, RED, 0.0)
    s += small_sine(bx + 40, base + 40, 210, 18, 1.4, BLUE, math.pi)
    s += text(bx + 150, base + 100, "різниця V₊−V₋ ≠ 0", 12, GREEN, "middle", "bold")
    s += arrow(bx + 150, base + 108, bx + 150, base + 126, GREEN, 2)
    s += rect(bx + 60, base + 130, 180, 28, LGRN, GREEN, 1.4, 6)
    s += text(bx + 150, base + 149, "× велике G", 13, GREEN, "middle", "bold")

    # ── права панель: синфазна завада ──
    cx0 = 410
    s += rect(cx0, 56, 290, 280, "none", "#c9d3dc", 1.4, 10)
    s += text(cx0 + 145, 78, "Завада (синфазна): однакова на обох", 13, RED, "middle", "bold")
    s += text(cx0 + 18, base - 6, "V₊", 13, RED, "start", "bold")
    s += text(cx0 + 18, base + 18, "V₋", 13, BLUE, "start", "bold")
    # обидва дроти гойдаються РАЗОМ (синфазно), велика амплітуда
    s += small_sine(cx0 + 40, base + 4, 200, 36, 1.0, RED, 0.0, 2.6)
    s += small_sine(cx0 + 40, base - 4, 200, 36, 1.0, BLUE, 0.0, 2.0)
    s += text(cx0 + 145, base + 100, "різниця V₊−V₋ ≈ 0", 12, RED, "middle", "bold")
    s += arrow(cx0 + 145, base + 108, cx0 + 145, base + 126, RED, 2)
    s += rect(cx0 + 45, base + 130, 200, 28, LRED, RED, 1.4, 6)
    s += text(cx0 + 145, base + 149, "× майже нуль (÷ CMRR)", 12.5, RED, "middle", "bold")

    save("inamp-cm-vs-dm.svg", s)


if __name__ == "__main__":
    fig_topology()
    fig_cm_vs_dm()
    print("done")
