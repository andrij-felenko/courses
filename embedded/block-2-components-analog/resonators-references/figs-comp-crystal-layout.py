# -*- coding: utf-8 -*-
"""
Генератор SVG для вставки 🔌 §2.10.5c «Кварц на платі: корпуси HC-49 і SMD 3225,
навантажувальні C, чому впритул до чипа» (Модуль 2, Розділ 2.10).

Окремий скрипт вставки — НЕ чіпає головний figs.py розділу.
Чистий Python без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами:
  fig-r10-5c-1-packages.svg   — два корпуси кварцу (HC-49 THT vs SMD 3225)
  fig-r10-5c-2-layout.svg     — підключення + компонування (XTAL_IN/OUT, 2×C, земля)

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле/виділення зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції — у стилі розділів 7–9.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
COPP  = "#b5732e"
METAL = "#9aa0a6"   # метал корпусу HC-49 / кришка SMD
CERAM = "#d9c9a3"   # керамічна основа SMD
QTZ   = "#bcd7e6"   # кварцова пластинка
LGRN  = "#eef6ef"
LBLU  = "#e9eefb"
LGRY  = "#f1f1f1"
PAD   = "#c8a24a"   # контактний майданчик / золото
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREEN: "aGreen", GREY: "aGrey", RED: "aRed"}


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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def cap(cx, cy, color=INK, w=2):
    """Вертикальний конденсатор (дві пластини), центр у (cx,cy), вивід зверху/знизу."""
    s = ""
    s += line(cx, cy - 16, cx, cy - 5, color, w)
    s += line(cx - 11, cy - 5, cx + 11, cy - 5, color, w)
    s += line(cx - 11, cy + 5, cx + 11, cy + 5, color, w)
    s += line(cx, cy + 5, cx, cy + 16, color, w)
    return s


def gnd(cx, cy, color=INK, w=2):
    """Символ землі, верхня точка у (cx,cy)."""
    s = ""
    s += line(cx, cy, cx, cy + 8, color, w)
    s += line(cx - 13, cy + 8, cx + 13, cy + 8, color, w)
    s += line(cx - 8, cy + 13, cx + 8, cy + 13, color, w)
    s += line(cx - 3, cy + 18, cx + 3, cy + 18, color, w)
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 2.10.5c.1 — два корпуси кварцу
# ════════════════════════════════════════════════════════════════════════════
def fig_packages():
    W, H = 720, 380
    s = header(W, H)
    s += text(W / 2, 30, "Два корпуси того самого кварцу", 18, INK, "middle", "bold")

    # ── ліворуч: HC-49 (THT), розріз ─────────────────────────────────────────
    cx = 185
    s += text(cx, 64, "HC-49  ·  наскрізний (THT)", 15, INK, "middle", "bold")

    # металевий бочонок (овальний верх) — розріз
    can_x, can_y, can_w, can_h = cx - 80, 84, 160, 150
    # тіло
    s += (f'<path d="M {can_x},{can_y+30} '
          f'Q {can_x},{can_y} {can_x+80},{can_y} '
          f'Q {can_x+160},{can_y} {can_x+160},{can_y+30} '
          f'L {can_x+160},{can_y+can_h} L {can_x},{can_y+can_h} Z" '
          f'fill="{METAL}" stroke="{INK}" stroke-width="2"/>\n')
    # внутрішня порожнина
    s += rect(can_x + 16, can_y + 22, can_w - 32, can_h - 34, fill="#ffffff", stroke=GREY, sw=1, rx=6)
    # кварцова пластинка всередині
    s += rect(cx - 34, can_y + 42, 68, 60, fill=QTZ, stroke=BLUE, sw=2, rx=3)
    s += text(cx, can_y + 78, "кварц", 12, BLUE, "middle")
    # пружні тримачі
    s += line(cx - 34, can_y + 72, cx - 52, can_y + 72, METAL, 3)
    s += line(cx + 34, can_y + 72, cx + 52, can_y + 72, METAL, 3)
    s += circle(cx - 52, can_y + 72, 3, fill=METAL, stroke=INK, w=1)
    s += circle(cx + 52, can_y + 72, 3, fill=METAL, stroke=INK, w=1)
    s += text(cx, can_y - 6, "герметичний метал. корпус", 11, GREY, "middle")

    # дротяні ніжки THT
    leg_y = can_y + can_h
    for lx in (cx - 40, cx + 40):
        s += line(lx, leg_y, lx, leg_y + 56, COPP, 4)
    s += text(cx, leg_y + 50, "дротяні виводи", 12, COPP, "middle")
    # лінія плати
    s += line(cx - 95, leg_y + 40, cx + 95, leg_y + 40, FAINT, 8)

    # габарити
    s += text(cx, can_y + can_h + 4 - can_h - 4, "", 1)  # noop, тримаємо структуру
    s += text(cx - 92, can_y + 75, "≈13 мм", 11, GREY, "middle")

    # ── праворуч: SMD 3225 (вид зверху + збоку) ──────────────────────────────
    dx = 540
    s += text(dx, 64, "SMD 3225  ·  поверхневий", 15, INK, "middle", "bold")
    s += text(dx, 82, "3.2 × 2.5 мм", 12, GREY, "middle")

    # вид зверху (керамічна ванночка з 4 майданчиками)
    bx, by, bw, bh = dx - 78, 96, 156, 108
    s += rect(bx, by, bw, bh, fill=CERAM, stroke=INK, sw=2, rx=8)
    s += rect(bx + 14, by + 14, bw - 28, bh - 28, fill="#ffffff", stroke=GREY, sw=1, rx=5)
    # кварцова пластинка
    s += rect(dx - 36, by + 30, 72, 48, fill=QTZ, stroke=BLUE, sw=2, rx=3)
    s += text(dx, by + 58, "кварц", 12, BLUE, "middle")
    # чотири кутові майданчики
    pads = [(bx, by, "1"), (bx + bw - 26, by, "4"),
            (bx, by + bh - 22, "2"), (bx + bw - 26, by + bh - 22, "3")]
    for (px, py, _n) in pads:
        s += rect(px, py, 26, 22, fill=PAD, stroke=INK, sw=1, rx=3)
    # помітити робочі (діагональ 1–3) і глухі (2–4)
    s += text(bx + 13, by - 6, "вивід", 11, RED, "middle")
    s += text(bx + bw - 13, by + bh + 16, "вивід", 11, RED, "middle")
    s += text(bx + bw - 13, by - 6, "GND", 11, BLUE, "middle")
    s += text(bx + 13, by + bh + 16, "GND", 11, BLUE, "middle")
    # діагональ робочих виводів
    s += line(bx + 13, by + 11, bx + bw - 13, by + bh - 11, RED, 1.4, dash="4 3")

    s += text(dx, by + bh + 44, "2 майданчики по діагоналі — виводи,", 12, INK, "middle")
    s += text(dx, by + bh + 62, "2 — на «землю» (міцність + екран)", 12, INK, "middle")

    # дрібніші родичі
    s += text(W / 2, H - 16, "Дрібніші родичі тієї ж сім'ї:  3225 → 2520 → 2016 → 1612  (менший корпус — нижча Q)",
              12, GREY, "middle")
    s += footer()
    with open(os.path.join(OUT, "fig-r10-5c-1-packages.svg"), "w", encoding="utf-8") as f:
        f.write(s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 2.10.5c.2 — підключення + компонування
# ════════════════════════════════════════════════════════════════════════════
def fig_layout():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 30, "Підключення кварцу й чому впритул до чипа", 18, INK, "middle", "bold")

    # охоронний полігон землі (фон під вузлом)
    gx, gy, gw, gh = 250, 70, 320, 250
    s += rect(gx, gy, gw, gh, fill=LGRN, stroke=GREEN, sw=1.5, rx=10, )
    s += text(gx + gw - 8, gy + 18, "суцільна земля + охоронне кільце", 12, GREEN, "end", style="italic")

    # ── чип ліворуч ──────────────────────────────────────────────────────────
    chx, chy, chw, chh = 70, 150, 120, 120
    s += rect(chx, chy, chw, chh, fill=LBLU, stroke=INK, sw=2, rx=6)
    s += text(chx + chw / 2, chy + 50, "чип", 16, INK, "middle", "bold")
    s += text(chx + chw / 2, chy + 70, "(інвертор Пірса)", 11, GREY, "middle")

    # ніжки XTAL_IN (верх) і XTAL_OUT (низ)
    pin_in_y = chy + 30
    pin_out_y = chy + 90
    s += line(chx + chw, pin_in_y, chx + chw + 24, pin_in_y, INK, 2)
    s += line(chx + chw, pin_out_y, chx + chw + 24, pin_out_y, INK, 2)
    s += text(chx + chw - 6, pin_in_y - 8, "XTAL_IN", 12, INK, "end", "bold")
    s += text(chx + chw - 6, pin_out_y + 18, "XTAL_OUT", 12, INK, "end", "bold")

    # вузли підключення
    node_in_x = chx + chw + 24      # 218
    node_out_x = chx + chw + 24
    # вертикальні шини до кварцу
    xtal_left = 300
    xtal_right = 420
    # верхня лінія (IN) до лівого виводу кварцу
    s += line(node_in_x, pin_in_y, xtal_left, pin_in_y, INK, 2)
    # нижня лінія (OUT): через послідовний резистор Rs
    rsx = node_out_x + 34
    s += line(node_out_x, pin_out_y, rsx - 16, pin_out_y, INK, 2)
    s += rect(rsx - 16, pin_out_y - 8, 32, 16, fill="#ffffff", stroke=INK, sw=2)
    s += text(rsx, pin_out_y - 14, "Rs", 11, INK, "middle", "bold")
    s += line(rsx + 16, pin_out_y, xtal_right, pin_out_y, INK, 2)

    # кварц посередині (між двома виводами, вертикальний)
    qmid_y = (pin_in_y + pin_out_y) / 2
    # ліве плече вниз до кварцу
    s += line(xtal_left, pin_in_y, xtal_left, qmid_y - 22, INK, 2)
    s += line(xtal_right, pin_out_y, xtal_right, qmid_y + 22, INK, 2)
    # символ кварцу: прямокутник між двома пластинами
    qx = (xtal_left + xtal_right) / 2
    s += line(xtal_left, qmid_y - 22, qx - 24, qmid_y - 22, INK, 2)
    s += line(qx + 24, qmid_y + 22, xtal_right, qmid_y + 22, INK, 2)
    # пластини + тіло
    s += line(qx - 24, qmid_y - 34, qx - 24, qmid_y - 10, INK, 2)
    s += line(qx + 24, qmid_y + 10, qx + 24, qmid_y + 34, INK, 2)
    s += rect(qx - 12, qmid_y - 34, 24, 68, fill=QTZ, stroke=INK, sw=2, rx=2)
    s += line(qx, qmid_y - 34, qx, qmid_y - 22, INK, 2)
    s += line(qx, qmid_y + 22, qx, qmid_y + 34, INK, 2)
    s += text(qx + 40, qmid_y + 4, "кварц", 13, BLUE, "start", "bold")

    # навантажувальні конденсатори: від кожного виводу на землю
    cap_in_x = xtal_left
    cap_out_x = xtal_right
    cap_y = 300
    # від лівого виводу вниз
    s += line(cap_in_x, pin_in_y, cap_in_x, cap_y - 16, INK, 2)
    s += cap(cap_in_x, cap_y, INK, 2)
    s += gnd(cap_in_x, cap_y + 16, GREEN, 2)
    s += text(cap_in_x - 18, cap_y + 4, "C", 14, INK, "end", "bold")
    # від правого виводу вниз
    s += line(cap_out_x, pin_out_y, cap_out_x, cap_y - 16, INK, 2)
    s += cap(cap_out_x, cap_y, INK, 2)
    s += gnd(cap_out_x, cap_y + 16, GREEN, 2)
    s += text(cap_out_x + 18, cap_y + 4, "C", 14, INK, "start", "bold")

    # вузлові точки
    for (nx, ny) in [(xtal_left, pin_in_y), (xtal_right, pin_out_y)]:
        s += circle(nx, ny, 3, fill=INK, stroke=INK, w=1)

    # «упритул»: стрілка короткої доріжки
    s += arrow(node_in_x + 4, pin_in_y - 26, xtal_left - 4, pin_in_y - 26, GREEN, 2)
    s += text((node_in_x + xtal_left) / 2, pin_in_y - 32, "коротко", 11, GREEN, "middle", style="italic")

    # ── формула CL праворуч ──────────────────────────────────────────────────
    fx, fy = 590, 150
    s += rect(fx - 8, fy - 28, 130, 150, fill=LGRY, stroke=GREY, sw=1, rx=8)
    s += text(fx + 57, fy - 8, "що бачить кварц", 12, INK, "middle", "bold")
    s += text(fx, fy + 18, "дві C → послідовно", 12, INK, "start")
    s += text(fx + 57, fy + 44, "C/2", 16, BLUE, "middle", "bold")
    s += text(fx, fy + 72, "CL = C/2 + Cₛ", 14, INK, "start", "bold")
    s += text(fx, fy + 96, "Cₛ ≈ 3–5 пФ", 12, GREY, "start")
    s += text(fx, fy + 114, "(ніжки, доріжки)", 11, GREY, "start")

    # застереження знизу
    s += text(W / 2, H - 16,
              "Під вузлом кварцу — лише земля; швидкі/тактові доріжки під ним не проводять.",
              12, RED, "middle", style="italic")
    s += footer()
    with open(os.path.join(OUT, "fig-r10-5c-2-layout.svg"), "w", encoding="utf-8") as f:
        f.write(s)


if __name__ == "__main__":
    fig_packages()
    fig_layout()
    print("OK: fig-r10-5c-1-packages.svg, fig-r10-5c-2-layout.svg ->", OUT)
