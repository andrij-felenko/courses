#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 47 (Модуль 7) — чистий Python, без залежностей.
Запуск:  python figs.py    →    кладе *.svg у ./img/

Стиль (єдиний для курсу; спільні допоміжні функції копіюються у кожен chNN/figs.py):
  білий фон; «+» червоний, «−» синій; поле — зелене; стрілки через marker;
  шрифт sans-serif. Підписи фігур у тексті — посекційно «Рис. C.S.N».
"""

import os
import math

# ── палітра ───────────────────────────────────────────────────────────────
INK   = "#1a1a1a"
MUTE  = "#6b7280"
RED   = "#cc0000"
BLUE  = "#1f4ed8"
GREEN = "#0a8f3c"
AMBER = "#d98a00"
SKY   = "#dbeafe"
GND   = "#dcfce7"
PANEL = "#f4f4f5"
BOX1  = "#eef2ff"
BOX2  = "#eafaef"
BOX3  = "#fff5e6"
FONT  = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def header(w, h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
     viewBox="0 0 {w} {h}" font-family="{FONT}">
  <defs>
    <marker id="arr" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{INK}"/></marker>
    <marker id="arrR" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{RED}"/></marker>
    <marker id="arrB" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{BLUE}"/></marker>
    <marker id="arrG" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{GREEN}"/></marker>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" fill="white"/>
'''


def footer():
    return "</svg>\n"


def text(x, y, s, size=14, fill=INK, anchor="start", weight="normal",
         italic=False, family=None):
    st = "italic" if italic else "normal"
    fam = f' font-family="{family}"' if family else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{st}"{fam}>{esc(s)}</text>\n')


def lines(x, y, rows, size=13, fill=INK, anchor="start", lh=16, weight="normal",
          family=None):
    out = ""
    for i, r in enumerate(rows):
        out += text(x, y + i * lh, r, size=size, fill=fill, anchor=anchor,
                    weight=weight, family=family)
    return out


def line(x1, y1, x2, y2, stroke=INK, w=1.6, dash=None, marker=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{w}"{d}{m} stroke-opacity="{opacity}" '
            f'stroke-linecap="round"/>\n')


def rect(x, y, w, h, fill="white", stroke=INK, sw=1.6, rx=8, dash=None,
         opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="white", stroke=INK, sw=1.6, opacity=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def poly(pts, fill="none", stroke=INK, sw=1.6, closed=True, opacity=1.0):
    tag = "polygon" if closed else "polyline"
    p = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>\n')


def title(w, s, sub=None):
    out = text(w / 2, 30, s, size=18, anchor="middle", weight="bold")
    if sub:
        out += text(w / 2, 50, sub, size=13, anchor="middle", fill=MUTE)
    return out


def coil(x1, x2, y, n=4, col=INK):
    """Котушка: n півкіл-горбиків угору."""
    w = (x2 - x1) / n
    p = f'M {x1} {y} '
    for _ in range(n):
        p += f'q {w / 2} {-w * 0.85} {w} 0 '
    return f'<path d="{p}" fill="none" stroke="{col}" stroke-width="2.2"/>\n'


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.0.1 — Ідея сканування
# ════════════════════════════════════════════════════════════════════════════
def fig_scanning():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Ідея сканування: образ — це послідовність рядків",
               "Фарнсворт побачив рівні борозни поля — і зрозумів, як перетворити картину на сигнал")
    ix, iy, iw, ih = 80, 110, 300, 220
    s += rect(ix, iy, iw, ih, fill="#eef2ff", stroke=INK, sw=1.8, rx=6)
    s += circle(ix + iw * 0.62, iy + ih * 0.4, 38, fill=AMBER, stroke="none",
                opacity=0.7)
    for k in range(11):
        ly = iy + 12 + k * ((ih - 24) / 10)
        s += line(ix, ly, ix + iw, ly, stroke=BLUE, w=0.8, opacity=0.5)
    hy = iy + 12 + 5 * ((ih - 24) / 10)
    s += line(ix - 2, hy, ix + iw + 2, hy, stroke=RED, w=2.0, marker="arrR")
    s += text(ix + iw / 2, iy - 8, "образ", size=12, anchor="middle",
              weight="bold")
    s += text(ix + iw / 2, iy + ih + 20,
              "розбиваємо на рядки, читаємо зліва направо, згори вниз", size=10,
              anchor="middle", fill=MUTE)
    s += line(ix + iw + 15, iy + ih / 2, ix + iw + 75, iy + ih / 2, stroke=INK,
              w=2.2, marker="arr")
    s += text(ix + iw + 45, iy + ih / 2 - 10, "розгортка", size=9.5,
              anchor="middle", fill=MUTE)
    sx, sy, sw_, sh = 475, 150, 405, 140
    s += rect(sx, sy, sw_, sh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)
    s += text(sx + sw_ / 2, sy - 8, "сигнал у часі (яскравість уздовж рядка)",
              size=10.5, anchor="middle", weight="bold")
    pts = []
    for k in range(101):
        f = k / 100
        b = 0.2 + 0.7 * math.exp(-((f - 0.62) ** 2) / (2 * 0.12 ** 2))
        pts.append((sx + sw_ * f, sy + sh - 10 - b * (sh - 24)))
    s += poly(pts, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(sx + sw_ / 2, sy + sh + 22,
              "одна картина → багато рядків → один потік світло-темно",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Уся відеотехніка стоїть на цьому: двовимірний образ перетворюють "
              "на одновимірний потік, що його несе дріт чи радіо.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.0.2 — Механічне vs електронне
# ════════════════════════════════════════════════════════════════════════════
def fig_mechanical_vs_electronic():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Механічне проти електронного: чому диск програв",
               "до Фарнсворта образ розкладали дірками в диску, що крутиться; він зробив це без рухомих деталей")
    cx, cy = 250, 230
    s += circle(cx, cy, 110, fill="#f4f4f5", stroke=INK, sw=2.0)
    for k in range(16):
        a = 2 * math.pi * k / 16
        r = 40 + k * 4.2
        s += circle(cx + r * math.cos(a), cy + r * math.sin(a), 4, fill="white",
                    stroke=INK, sw=1)
    s += text(cx, cy - 128, "МЕХАНІЧНЕ ТБ", size=13, anchor="middle",
              weight="bold", fill=MUTE)
    s += text(cx, cy + 132, "диск Нипкова: дірки по спіралі,", size=10.5,
              anchor="middle", fill=MUTE)
    s += text(cx, cy + 148, "крутиться й «прорізає» образ рядками", size=10.5,
              anchor="middle", fill=MUTE)
    s += text(cx, cy + 172, "✗ повільно, грубо, тендітно", size=10.5,
              anchor="middle", fill=RED, weight="bold")
    tx, ty = 700, 230
    s += rect(tx - 90, ty - 70, 180, 140, fill=SKY, stroke=BLUE, sw=2.0, rx=14)
    s += poly([(tx - 70, ty - 40), (tx + 70, ty - 40), (tx - 70, ty - 25),
               (tx + 70, ty - 25)], fill="none", stroke=BLUE, sw=1.4,
              closed=False)
    s += text(tx, ty + 4, "пучок електронів", size=10, anchor="middle",
              fill=BLUE)
    s += text(tx, ty + 22, "сканує образ", size=10, anchor="middle", fill=BLUE)
    s += text(tx, ty - 110, "ЕЛЕКТРОННЕ ТБ", size=13, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(tx, ty + 95, "образорозкладач Фарнсворта:", size=10.5,
              anchor="middle", fill=MUTE)
    s += text(tx, ty + 111, "сканує без жодної рухомої деталі", size=10,
              anchor="middle", fill=MUTE)
    s += text(tx, ty + 135, "✓ швидко, чітко, надійно", size=10.5,
              anchor="middle", fill=GREEN, weight="bold")
    s += text(W / 2, H - 14,
              "Електрони легкі й безінерційні, тож сканують у тисячі разів "
              "швидше за будь-який диск — звідси й перемога.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.0.3 — Образорозкладач
# ════════════════════════════════════════════════════════════════════════════
def fig_image_dissector():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Як працює образорозкладач: світло → електрони → струм",
               "лінза кидає образ на фотокатод, той сипле електрони, а ті проходять крізь щілину — рядок за рядком")
    y0 = 235
    s += text(120, 120, "образ", size=11, anchor="middle", weight="bold")
    s += poly([(150, y0 - 50), (150, y0 + 50), (170, y0 + 30), (170, y0 - 30)],
              fill=SKY, stroke=BLUE, sw=1.6)
    s += text(160, y0 + 78, "лінза", size=10, anchor="middle", fill=MUTE)
    for dy in [-40, 0, 40]:
        s += line(175, y0 + dy * 0.6, 238, y0 + dy, stroke=AMBER, w=1.2)
    s += rect(240, y0 - 60, 16, 120, fill=AMBER, stroke=INK, sw=1.6, rx=3)
    s += text(248, y0 + 80, "фотокатод", size=10, anchor="middle", fill=MUTE)
    s += text(248, y0 + 94, "(світло→електрони)", size=8.5, anchor="middle",
              fill=MUTE)
    for dy in [-35, -12, 12, 35]:
        s += line(258, y0 + dy, 466, y0 + dy, stroke=BLUE, w=1.2, dash="3,3",
                  marker="arrB", opacity=0.6)
    s += text(360, y0 - 50, "«електронний образ» дрейфує", size=10,
              anchor="middle", fill=BLUE)
    s += rect(480, y0 - 70, 14, 56, fill=INK, stroke=INK)
    s += rect(480, y0 + 14, 14, 56, fill=INK, stroke=INK)
    s += text(487, y0 - 80, "діафрагма зі щілиною", size=9, anchor="middle",
              fill=MUTE)
    s += text(487, y0 + 92, "щілина", size=10, anchor="middle", fill=MUTE)
    s += line(494, y0, 600, y0, stroke=GREEN, w=2.2, marker="arrG")
    s += rect(600, y0 - 30, 92, 60, fill=BOX2, stroke=GREEN, sw=1.6, rx=8)
    s += text(646, y0 + 5, "струм", size=11, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(722, y0 - 2, "= яскравість", size=11, fill=GREEN, weight="bold")
    s += text(722, y0 + 16, "точки рядка", size=10, fill=MUTE)
    s += text(W / 2, H - 30,
              "Образ «зсувають» по щілині — і крізь неї по черзі проходять "
              "електрони від кожної точки рядка.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Скільки електронів пройшло — така там яскравість. Так картина "
              "стає струмом, що міняється в часі: відеосигналом.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.0.4 — Спадок: той самий скан
# ════════════════════════════════════════════════════════════════════════════
def fig_legacy():
    W, H = 960, 430
    s = header(W, H)
    s += title(W, "Спадок Фарнсворта: той самий скан у кожній камері",
               "сенсор дрона читає пікселі рядок за рядком — і знов виходить одновимірний потік")
    gx, gy, cell = 90, 116, 22
    s += text(gx + 5.5 * cell, gy - 12, "матриця сенсора (пікселі)", size=11,
              anchor="middle", weight="bold")
    for r in range(8):
        for c in range(11):
            s += rect(gx + c * cell, gy + r * cell, cell - 2, cell - 2,
                      fill="#eef2ff", stroke="#c7d2fe", sw=0.8)
    rr = 3
    for c in range(11):
        s += rect(gx + c * cell, gy + rr * cell, cell - 2, cell - 2, fill=RED,
                  stroke=INK, sw=0.8, opacity=0.5)
    s += line(gx, gy + rr * cell + cell / 2, gx + 11 * cell,
              gy + rr * cell + cell / 2, stroke=RED, w=1.6, marker="arrR")
    s += text(gx + 5.5 * cell, gy + 8 * cell + 16, "читаємо рядок за рядком",
              size=10, anchor="middle", fill=MUTE)
    s += line(gx + 11 * cell + 15, gy + 4 * cell, gx + 11 * cell + 70,
              gy + 4 * cell, stroke=INK, w=2.2, marker="arr")
    sx = gx + 11 * cell + 85
    s += text(sx + 150, gy - 12, "одновимірний потік пікселів", size=11,
              anchor="middle", weight="bold")
    for i in range(18):
        bh = 10 + 30 * (0.5 + 0.5 * math.sin(i * 0.9))
        s += rect(sx + i * 17, gy + 90 - bh, 14, bh, fill=BLUE, stroke="none",
                  opacity=0.7)
    s += text(sx + 150, gy + 120, "→ дріт / радіо / пам'ять", size=10.5,
              anchor="middle", fill=MUTE)
    s += rect(90, 332, 780, 52, fill=BOX3, stroke=AMBER, sw=1.4, rx=10)
    s += text(480, 354,
              "образ → рядки → потік → канал — та сама ідея, що Фарнсворт "
              "побачив у борознах поля 1921 року.", size=11, anchor="middle",
              weight="bold")
    s += text(480, 372,
              "Весь розділ — про кожну ланку цього ланцюга: від світла на "
              "пікселі до готового кадру.", size=10, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.1.1 — Фотоефект
# ════════════════════════════════════════════════════════════════════════════
def fig_photoelectric():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Фотоефект: фотон вибиває з кремнію електрон",
               "світло — потік фотонів; кожен, влучивши, вибиває вільний електрон — місток від світла до електрики")
    lx, ly = 130, 150
    s += text(130, 128, "кремній (атоми)", size=11, fill=MUTE, weight="bold")
    for r in range(4):
        for c in range(7):
            s += circle(lx + c * 70, ly + r * 52, 13, fill="#e5e7eb",
                        stroke=MUTE, sw=1.3)
    ax, ay = lx + 3 * 70, ly + 1 * 52
    s += text(ax - 150, ay - 74, "фотон (світло)", size=11, fill=AMBER,
              weight="bold")
    pp = []
    for k in range(20):
        t = k / 19
        pp.append((ax - 150 + 130 * t, ay - 58 + 42 * t + 7 * math.sin(k * 1.2)))
    s += poly(pp, fill="none", stroke=AMBER, sw=2.2, closed=False)
    s += line(pp[-1][0], pp[-1][1], ax - 14, ay - 12, stroke=AMBER, w=2.2,
              marker="arr")
    s += circle(ax, ay, 13, fill=AMBER, stroke=INK, sw=1.5)
    s += line(ax + 12, ay - 8, ax + 46, ay - 34, stroke=BLUE, w=1.8,
              marker="arrB", dash="3,2")
    s += circle(ax + 55, ay - 40, 8, fill=BLUE, stroke=INK, sw=1.4)
    s += text(ax + 55, ay - 37, "e", size=10, anchor="middle", fill="white",
              weight="bold")
    s += text(ax + 100, ay - 44, "вільний електрон", size=11, fill=BLUE,
              weight="bold")
    s += rect(250, 348, 460, 52, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(480, 372, "більше світла → більше фотонів → більше електронів",
              size=12, anchor="middle", weight="bold", fill=GREEN)
    s += text(480, 390, "(кількість електронів ∝ кількість світла)", size=10,
              anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.1.2 — Піксель як відерце
# ════════════════════════════════════════════════════════════════════════════
def fig_bucket():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Піксель — відерце для електронів",
               "фотони наповнюють «відерце» вибитими електронами; рівень = яскравість, далі заряд → напруга → число")
    bx, bt, bw, bh = 140, 110, 130, 210
    s += text(bx + bw / 2, bt - 50, "фотони ↓", size=10.5, anchor="middle",
              fill=AMBER, weight="bold")
    for xx in [bx + 20, bx + 50, bx + 80, bx + 110]:
        s += line(xx, bt - 40, xx - 6, bt - 6, stroke=AMBER, w=1.8, marker="arr")
    s += rect(bx, bt, bw, bh, fill="white", stroke=INK, sw=2.0, rx=4)
    fl = 0.6
    s += rect(bx + 4, bt + bh - (bh - 8) * fl, bw - 8, (bh - 8) * fl, fill=BLUE,
              stroke="none", opacity=0.4, rx=3)
    for dx, dy in [(30, 185), (60, 172), (92, 188), (45, 162), (82, 150),
                   (108, 178)]:
        s += circle(bx + dx, bt + dy, 4, fill=BLUE, stroke="none")
    s += text(bx + bw / 2, bt + bh - (bh - 8) * fl - 8, "рівень = яскравість",
              size=9.5, anchor="middle", fill=BLUE)
    s += text(bx + bw / 2, bt + bh + 20, "піксель = відерце", size=11,
              anchor="middle", weight="bold")
    s += line(bx + bw + 8, 215, 352, 218, stroke=INK, w=2.0, marker="arr")
    chain = [("заряд", BLUE), ("напруга", AMBER), ("АЦП", MUTE), ("число", GREEN)]
    cx = 360
    for i, (lab, col) in enumerate(chain):
        x = cx + i * 145
        s += rect(x, 190, 120, 56, fill="white", stroke=col, sw=1.8, rx=10)
        s += text(x + 60, 224, lab, size=13, anchor="middle", weight="bold",
                  fill=col)
        if i < 3:
            s += line(x + 122, 218, x + 143, 218, stroke=INK, w=2.0,
                      marker="arr")
    s += text(W / 2, H - 30,
              "Світло → електрони → заряд → напруга → число. Це число — "
              "яскравість цятки, той «світло-темно» Фарнсворта.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Відерце сліпе до кольору — лічить усі фотони підряд, тож міряє "
              "лише яскравість (колір — 47.3).", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.1.3 — Витримка
# ════════════════════════════════════════════════════════════════════════════
def fig_exposure():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Витримка: скільки тримати відерце відкритим",
               "довша витримка — більше світла, але рух розмивається; коротша — різко, та темно")

    def scene(x0, label, t_frac, fill_frac, blur, col):
        out = text(x0 + 145, 96, label, size=12.5, anchor="middle",
                   weight="bold", fill=col)
        out += text(x0, 136, "витримка:", size=10, fill=MUTE)
        out += rect(x0 + 66, 124, 214, 18, fill="#f4f4f5", stroke="#e5e7eb",
                    sw=1, rx=4)
        out += rect(x0 + 66, 124, 214 * t_frac, 18, fill=col, stroke="none",
                    rx=4, opacity=0.7)
        bx, bt, bw, bh = x0 + 40, 165, 110, 120
        out += rect(bx, bt, bw, bh, fill="white", stroke=INK, sw=1.8, rx=4)
        out += rect(bx + 4, bt + bh - (bh - 8) * fill_frac, bw - 8,
                    (bh - 8) * fill_frac, fill=BLUE, stroke="none", opacity=0.4,
                    rx=3)
        out += text(bx + bw / 2, bt + bh + 18,
                    "мало світла" if fill_frac < 0.4 else "багато світла",
                    size=10, anchor="middle", fill=MUTE)
        rx_ = x0 + 180
        out += rect(rx_, 165, 96, 120, fill="#0f172a", stroke=INK, sw=1.4, rx=6)
        if blur:
            out += rect(rx_ + 18, 208, 60, 12, fill="#e5e7eb", stroke="none",
                        rx=6, opacity=0.65)
            out += text(rx_ + 48, 302, "✗ розмито", size=9.5, anchor="middle",
                        fill=RED, weight="bold")
        else:
            out += circle(rx_ + 48, 225, 10, fill="#e5e7eb", stroke="none")
            out += text(rx_ + 48, 302, "✓ різко", size=9.5, anchor="middle",
                        fill=GREEN, weight="bold")
        return out
    s += scene(70, "КОРОТКА витримка", 0.3, 0.3, False, BLUE)
    s += scene(540, "ДОВГА витримка", 0.85, 0.85, True, AMBER)
    s += line(495, 150, 495, 300, stroke="#e5e7eb", w=1.4, dash="4,4")
    s += text(W / 2, H - 30,
              "На летючому, тремкому апараті надто довга витримка = змазаний "
              "кадр, з якого мало користі.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += text(W / 2, H - 14,
              "Тому вдень витримку коротять (рух різкий); поночі або довшать "
              "(ризик змазу), або задирають підсилення (шум, 47.4).", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.1.4 — Насичення та шум
# ════════════════════════════════════════════════════════════════════════════
def fig_saturation():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Стеля й підлога пікселя: насичення та шум",
               "відерце має повну місткість (пересвіт) і дно шуму; корисний діапазон — між ними")

    def bucket(x0, fill, state, col, note):
        bt, bw, bh = 120, 130, 210
        out = rect(x0, bt, bw, bh, fill="white", stroke=INK, sw=2.0, rx=4)
        out += rect(x0 + 4, bt + bh - 26, bw - 8, 22, fill=MUTE, stroke="none",
                    opacity=0.2, rx=3)
        fh = (bh - 8) * min(fill, 1.0)
        out += rect(x0 + 4, bt + bh - 4 - fh, bw - 8, fh, fill=col,
                    stroke="none", opacity=0.45, rx=3)
        if fill > 1.0:
            out += line(x0, bt - 4, x0 + bw, bt - 4, stroke=RED, w=2.2)
            for k in range(4):
                out += line(x0 + 18 + k * 30, bt - 20, x0 + 18 + k * 30, bt - 6,
                            stroke=RED, w=1.6, marker="arrR")
        out += text(x0 + bw / 2, bt - 28 if fill > 1 else bt - 10, state,
                    size=11.5, anchor="middle", weight="bold",
                    fill=(RED if fill > 1 else col))
        out += text(x0 + bw / 2, bt + bh + 20, note, size=9.5, anchor="middle",
                    fill=MUTE)
        return out
    s += bucket(80, 0.12, "замало (шум)", MUTE, "тоне у шумі → чорний провал")
    s += bucket(340, 0.62, "саме те", GREEN, "корисний діапазон")
    s += bucket(600, 1.3, "пересвіт", RED, "переповнення → суцільна білість")
    s += line(740, 124, 772, 124, stroke=RED, w=1.6, dash="4,3")
    s += text(776, 128, "стеля: повна місткість", size=9.5, fill=RED)
    s += line(740, 320, 772, 320, stroke=MUTE, w=1.6, dash="4,3")
    s += text(776, 324, "підлога: шум", size=9.5, fill=MUTE)
    s += text(W / 2, H - 14,
              "І пересвіт, і чорний провал — це втрачені НАЗАВЖДИ деталі: там "
              "просто нема даних (динамічний діапазон — 47.4).", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.2.1 — Матриця CMOS
# ════════════════════════════════════════════════════════════════════════════
def fig_matrix():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Матриця CMOS: мільйони відерець, адресованих як пам'ять",
               "пікселі стоять сіткою; кожен має свій підсилювач, а зчитують їх рядок за рядком по адресах")
    gx, gy, cell, ncol, nrow = 175, 105, 40, 9, 6
    active = 2
    for r in range(nrow):
        for c in range(ncol):
            f = RED if r == active else "#eef2ff"
            op = 0.32 if r == active else 1.0
            s += rect(gx + c * cell, gy + r * cell, cell - 4, cell - 4, fill=f,
                      stroke="#c7d2fe", sw=1, opacity=op)
            if r != active:
                s += circle(gx + c * cell + 18, gy + r * cell + 18, 3,
                            fill=BLUE, stroke="none", opacity=0.5)
    s += text(gx - 56, gy - 12, "вибір рядка →", size=10, anchor="end",
              fill=MUTE, weight="bold")
    for r in range(nrow):
        col = RED if r == active else MUTE
        s += line(gx - 52, gy + r * cell + 18, gx - 4, gy + r * cell + 18,
                  stroke=col, w=2.0 if r == active else 1,
                  marker="arrR" if r == active else None)
    ybot = gy + nrow * cell
    for c in range(ncol):
        s += line(gx + c * cell + 18, ybot, gx + c * cell + 18, ybot + 22,
                  stroke=MUTE, w=1)
    s += rect(gx - 4, ybot + 22, ncol * cell, 26, fill=PANEL, stroke=INK,
              sw=1.4, rx=6)
    s += text(gx + ncol * cell / 2 - 4, ybot + 39,
              "стовпцеві підсилювачі → АЦП", size=11, anchor="middle",
              weight="bold")
    s += line(gx + ncol * cell, ybot + 35, gx + ncol * cell + 56, ybot + 35,
              stroke=INK, w=2.0, marker="arr")
    s += text(gx + ncol * cell + 66, ybot + 39, "потік", size=11, fill=GREEN,
              weight="bold")
    s += lines(gx + ncol * cell + 24, gy + 28,
               ["кожен піксель —", "відерце + свій", "підсилювач"], size=10,
               lh=15, fill=MUTE)
    s += text(W / 2, H - 14,
              "CMOS адресує пікселі, мов комірки пам'яті: вмикає рядок, зчитує "
              "всі його стовпці — і так згори вниз.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.2.2 — Згортковий затвор
# ════════════════════════════════════════════════════════════════════════════
def fig_rolling_shutter():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Згортковий затвор: рядки знімаються не воднораз",
               "CMOS читає рядок за рядком згори вниз — швидкий рух чи вібрація косять кадр («желе»)")
    fx, fy, fw, fh = 110, 110, 250, 230
    s += text(fx + fw / 2, fy - 10, "ЗГОРТКОВИЙ (rolling)", size=12,
              anchor="middle", weight="bold", fill=RED)
    s += rect(fx, fy, fw, fh, fill="#0f172a", stroke=INK, sw=1.6, rx=6)
    pts = [(fx + fw * 0.4 + k * 9, fy + 15 + k * ((fh - 30) / 10))
           for k in range(11)]
    s += poly(pts, fill="none", stroke="#e5e7eb", sw=6, closed=False)
    s += text(fx + fw / 2, fy + fh + 18, "пряма щогла виходить КОСОЮ", size=10,
              anchor="middle", fill=RED)
    s += text(fx + fw + 8, fy + 8, "рядки в", size=8.5, fill=MUTE)
    s += text(fx + fw + 8, fy + 20, "різні миті ↓", size=8.5, fill=MUTE)
    for k in range(0, 11, 2):
        s += text(fx + fw + 8, fy + 18 + k * ((fh - 30) / 10) + 4,
                  f"t{k // 2}", size=8.5, fill=MUTE)
    gx2 = 560
    s += text(gx2 + fw / 2, fy - 10, "ГЛОБАЛЬНИЙ (global)", size=12,
              anchor="middle", weight="bold", fill=GREEN)
    s += rect(gx2, fy, fw, fh, fill="#0f172a", stroke=INK, sw=1.6, rx=6)
    s += line(gx2 + fw * 0.5, fy + 15, gx2 + fw * 0.5, fy + fh - 15,
              stroke="#e5e7eb", w=6)
    s += text(gx2 + fw / 2, fy + fh + 18, "усі рядки воднораз → ПРЯМА", size=10,
              anchor="middle", fill=GREEN)
    s += text(W / 2, H - 30,
              "Вібрація рами й швидкий рух під згортковим затвором дають "
              "хвилясте «желе» й косі лінії —", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "це псує не лише вигляд, а й машинне бачення (одометрію). Для "
              "нього беруть глобальний затвор.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.2.3 — Дві ручки яскравості
# ════════════════════════════════════════════════════════════════════════════
def fig_exposure_gain():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Дві ручки яскравості: витримка й підсилення",
               "витримка набирає більше світла (ризик змазу); підсилення множить сигнал уже після (ризик шуму)")
    s += rect(70, 180, 120, 100, fill="#1e293b", stroke=INK, sw=1.6, rx=6)
    s += text(130, 234, "темний", size=11, anchor="middle", fill="#e5e7eb")
    s += text(130, 300, "тьмяний кадр", size=10, anchor="middle", fill=MUTE)
    s += line(192, 200, 250, 162, stroke=BLUE, w=2.0, marker="arrB")
    s += line(192, 262, 250, 298, stroke=AMBER, w=2.0, marker="arr")
    s += rect(255, 112, 330, 96, fill=BOX1, stroke=BLUE, sw=1.7, rx=11)
    s += text(420, 136, "↑ ВИТРИМКА (довше відкрито)", size=12, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(420, 160, "більше світла в відерце → яскравіше", size=10.5,
              anchor="middle")
    s += text(420, 182, "✗ ризик: розмиє рух (змаз)", size=10.5,
              anchor="middle", fill=RED, weight="bold")
    s += rect(255, 250, 330, 96, fill=BOX3, stroke=AMBER, sw=1.7, rx=11)
    s += text(420, 274, "↑ ПІДСИЛЕННЯ (множимо сигнал)", size=12,
              anchor="middle", weight="bold", fill="#b06b00")
    s += text(420, 298, "множимо вже зчитане число", size=10.5, anchor="middle")
    s += text(420, 320, "✗ ризик: множить і ШУМ (зерно)", size=10.5,
              anchor="middle", fill=RED, weight="bold")
    s += line(587, 160, 645, 218, stroke=BLUE, w=2.0, marker="arrB")
    s += line(587, 298, 645, 240, stroke=AMBER, w=2.0, marker="arr")
    s += rect(650, 185, 120, 100, fill="#475569", stroke=INK, sw=1.6, rx=6)
    s += text(710, 239, "яскравіше", size=11, anchor="middle", fill="white")
    s += text(710, 305, "але з платою", size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Підсилення НЕ додає світла — лише розтягує наявне разом із шумом. "
              "Тому «витягнути» темний кадр без втрат не можна.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.2.4 — Компроміс експозиції
# ════════════════════════════════════════════════════════════════════════════
def fig_triangle():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Компроміс експозиції: світло × витримка × підсилення",
               "яскравість = світло сцени × час × підсилення; на летючому апараті світло дане, тож торгуєш змаз ↔ шум")
    s += rect(230, 92, 500, 48, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(480, 122, "яскравість = світло × витримка × підсилення", size=15,
              anchor="middle", weight="bold")
    s += text(480, 164,
              "сцену не змінити (світло дане) → граєш двома ручками, у кожної своя плата:",
              size=11, anchor="middle", fill=MUTE)

    def card(x0, head, headcol, rows, verdict):
        out = rect(x0, 192, 360, 152, fill="white", stroke=headcol, sw=1.8,
                   rx=12)
        out += text(x0 + 180, 220, head, size=13, anchor="middle",
                    weight="bold", fill=headcol)
        out += lines(x0 + 26, 248, rows, size=11, lh=22)
        out += rect(x0 + 20, 306, 320, 30, fill=headcol, stroke="none", rx=7,
                    opacity=0.13)
        out += text(x0 + 180, 326, verdict, size=11, anchor="middle",
                    weight="bold", fill=headcol)
        return out
    s += card(70, "ШВИДКИЙ політ / тряска", BLUE,
              ["• коротка витримка (щоб не змазати)",
               "• → бракує світла → ↑ підсилення",
               "• плата: ШУМ, зернистість"], "різко, але шумно")
    s += card(530, "ПОВІЛЬНО / стабільно", GREEN,
              ["• довша витримка (світла досить)", "• низьке підсилення",
               "• плата: ризик змазу при русі"], "чисто, та чутливо до руху")
    s += text(W / 2, H - 14,
              "На дроні майже завжди виграє коротка витримка: різкий, хай "
              "шумніший кадр кращий за яскравий мазок.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. CCD-1 — Естафета зарядів (історія 47.2)
# ════════════════════════════════════════════════════════════════════════════
def fig_ccd_bucketbrigade():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Естафета зарядів: як CCD зчитує матрицю",
               "замість підсилювача в кожному пікселі — заряд пересувають «відерце за відерцем» до одного виходу")
    y0 = 200
    n = 7
    wx0, ww, wgap = 110, 80, 14
    amts = [0.7, 0.4, 0.9, 0.5, 0.6, 0.3, 0.8]
    s += text(wx0 + 3 * (ww + wgap), y0 - 58,
              "заряд зсувається праворуч, такт за тактом →", size=10.5,
              anchor="middle", fill="#b06b00", weight="bold")
    for i in range(n):
        x = wx0 + i * (ww + wgap)
        s += poly([(x, y0 - 30), (x, y0 + 30), (x + ww, y0 + 30),
                   (x + ww, y0 - 30)], fill="white", stroke=INK, sw=1.8)
        ch_h = 44 * amts[i]
        s += rect(x + 6, y0 + 28 - ch_h, ww - 12, ch_h, fill=BLUE, stroke="none",
                  opacity=0.5, rx=2)
        if i < n - 1:
            s += line(x + ww + 1, y0 - 42, x + ww + wgap - 1, y0 - 42,
                      stroke=AMBER, w=1.8, marker="arr")
    s += text(wx0, y0 + 58, "пікселі-відерця (заряд від світла)", size=10.5,
              fill=MUTE)
    ox = wx0 + n * (ww + wgap) + 8
    s += line(ox - 8, y0, ox, y0, stroke=BLUE, w=2.2, marker="arrB")
    s += poly([(ox, y0 - 26), (ox, y0 + 26), (ox + 48, y0)], fill=BOX2,
              stroke=GREEN, sw=1.8)
    s += text(ox + 24, y0 + 48, "ОДИН", size=10.5, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(ox + 24, y0 + 63, "підсилювач", size=10, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 30,
              "Як відра в пожежній естафеті: заряд кожного пікселя по черзі "
              "передають уздовж ряду до єдиного «читача» на краю.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Один підсилювач на всіх — звідси надзвичайна РІВНІСТЬ і мала "
              "шумність, але й повільність.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. CCD-2 — CCD проти CMOS (історія 47.2)
# ════════════════════════════════════════════════════════════════════════════
def fig_ccd_vs_cmos():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Дві філософії зчитування: CCD проти CMOS",
               "CCD жене весь заряд до ОДНОГО підсилювача (рівно, тихо, повільно); CMOS дає підсилювач КОЖНОМУ")

    def grid(x0, per_pixel_amp):
        out = ""
        for r in range(3):
            for c in range(4):
                px, py = x0 + c * 34, 140 + r * 34
                out += rect(px, py, 28, 28, fill="#eef2ff", stroke="#c7d2fe",
                            sw=1)
                if per_pixel_amp:
                    out += text(px + 14, py + 19, "▲", size=9, anchor="middle",
                                fill=GREEN)
        return out
    s += text(190, 116, "CCD", size=14, anchor="middle", weight="bold",
              fill=BLUE)
    s += grid(120, False)
    s += line(120, 268, 250, 268, stroke=AMBER, w=1.6, marker="arr")
    s += text(186, 260, "увесь заряд →", size=9.5, anchor="middle",
              fill="#b06b00")
    s += poly([(252, 256), (252, 280), (284, 268)], fill=BOX2, stroke=GREEN,
              sw=1.6)
    s += text(268, 298, "1 підсилювач", size=10, anchor="middle",
              weight="bold", fill=GREEN)
    s += lines(120, 330, ["✓ дуже рівно, мало шуму", "✓ чисте наукове фото",
                          "✗ повільно, їсть струм",
                          "✗ нема випадкового доступу"], size=10.5, lh=20)
    s += text(710, 116, "CMOS", size=14, anchor="middle", weight="bold",
              fill=GREEN)
    s += grid(640, True)
    s += text(708, 290, "▲ підсилювач у КОЖНОМУ пікселі", size=10,
              anchor="middle", fill=GREEN)
    s += lines(640, 330, ["✓ швидко, дешево, малий струм",
                          "✓ адресація як пам'ять",
                          "✓ камера на чипі (Фоссум)",
                          "✗ колись — більше шуму/різнобій"], size=10.5, lh=20)
    s += line(480, 110, 480, 412, stroke="#e5e7eb", w=1.4, dash="5,4")
    s += text(W / 2, H - 14,
              "CCD правив, поки цінували якість; CMOS переміг, коли знадобилися "
              "дешевизна, швидкість і батарея — тобто на дроні.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. CCD-3 — Спадок CCD (історія 47.2)
# ════════════════════════════════════════════════════════════════════════════
def fig_ccd_legacy():
    W, H = 960, 420
    s = header(W, H)
    s += title(W, "Спадок CCD: від плівки до цифри — і до Нобеля",
               "CCD витіснив плівку й десятиліттями правив у камерах і телескопах; Нобель з фізики 2009")
    ty = 205
    s += line(90, ty, 875, ty, stroke=INK, w=2, marker="arr")
    for x, yr, h, sub in [
            (150, "1969", "Бойл і Сміт", "накидали CCD за годину"),
            (360, "1970–90-ті", "революція", "цифрове фото без плівки"),
            (570, "телескопи", "«Габбл» і Ко", "очі науки на десятиліття"),
            (780, "2009", "НОБЕЛЬ", "з фізики, за CCD")]:
        s += line(x, ty - 18, x, ty - 6, stroke=MUTE, w=1)
        s += circle(x, ty, 7, fill=AMBER, stroke=INK, sw=1.4)
        s += text(x, ty - 40, yr, size=11, anchor="middle", weight="bold",
                  fill="#b06b00")
        s += text(x, ty - 24, h, size=11, anchor="middle", weight="bold")
        s += text(x, ty + 26, sub, size=9.5, anchor="middle", fill=MUTE)
    s += rect(225, 300, 510, 62, fill=BOX3, stroke=AMBER, sw=1.4, rx=10)
    s += text(480, 324,
              "А потім прийшов дешевий швидкий CMOS (Фоссум) — і забрав масовий ринок.",
              size=11, anchor="middle", weight="bold")
    s += text(480, 345,
              "CCD лишився там, де над усе якість: великі телескопи, наукові камери.",
              size=10.5, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.3.1 — Колір додає фільтр
# ════════════════════════════════════════════════════════════════════════════
def fig_colorblind():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Піксель сліпий до кольору — то дамо йому фільтр",
               "відерце лічить усі фотони підряд (лише яскравість); щоб бачити колір, над пікселем ставлять скельце")
    RC, GC, BC = "#cc0000", "#16a34a", "#1f4ed8"
    s += text(200, 112, "БЕЗ фільтра", size=13, anchor="middle", weight="bold",
              fill=MUTE)
    for col, xx in [(RC, 165), (GC, 200), (BC, 235)]:
        s += line(xx, 140, xx - 5, 184, stroke=col, w=2.2, marker="arr")
    s += rect(150, 190, 100, 70, fill="#9ca3af", stroke=INK, sw=1.8, rx=4)
    s += text(200, 232, "усе світло", size=10.5, anchor="middle", fill="white",
              weight="bold")
    s += text(200, 286, "міряє лише ЯСКРАВІСТЬ", size=10.5, anchor="middle",
              fill=MUTE)
    s += text(200, 302, "(сірий — колір невідомий)", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(640, 112, "З кольоровим фільтром над пікселем", size=13,
              anchor="middle", weight="bold")
    for lab, col, xx in [("R", RC, 470), ("G", GC, 620), ("B", BC, 770)]:
        for pc, dx in [(RC, -16), (GC, 0), (BC, 16)]:
            s += line(xx + dx, 150, xx + dx, 178, stroke=pc, w=1.6, opacity=0.5)
        s += rect(xx - 40, 180, 80, 15, fill=col, stroke=INK, sw=1.2,
                  opacity=0.55)
        s += text(xx + 60, 192, "фільтр", size=9, fill=MUTE)
        s += line(xx, 197, xx, 214, stroke=col, w=2.4, marker="arr")
        s += rect(xx - 32, 216, 64, 56, fill=col, stroke=INK, sw=1.6, rx=4,
                  opacity=0.35)
        s += text(xx, 252, lab, size=15, anchor="middle", weight="bold",
                  fill=col)
    s += text(640, 300, "кожен ловить лише СВІЙ колір → міряє його яскравість",
              size=10.5, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Фільтр пропускає тільки свою смугу: червоний — лише червоне "
              "світло, і так далі. Так піксель стає «кольоровим».", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.3.2 — Баєрівська мозаїка
# ════════════════════════════════════════════════════════════════════════════
def _bayer_col(r, c):
    RC, GC, BC = "#cc0000", "#16a34a", "#1f4ed8"
    rr, cc = r % 2, c % 2
    if rr == 0 and cc == 0:
        return RC
    if rr == 1 and cc == 1:
        return BC
    return GC


def fig_bayer():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Баєрівська мозаїка: шахівниця кольорових фільтрів",
               "повторюваний квадрат R G / G B; зеленого вдвічі більше — бо око найгостріше до яскравості")
    gx, gy, cell, ncol, nrow = 250, 110, 36, 10, 7
    for r in range(nrow):
        for c in range(ncol):
            s += rect(gx + c * cell, gy + r * cell, cell - 2, cell - 2,
                      fill=_bayer_col(r, c), stroke="white", sw=1, opacity=0.8)
    s += rect(gx - 3, gy - 3, 2 * cell + 2, 2 * cell + 2, fill="none",
              stroke=INK, sw=2.4)
    s += text(gx + cell, gy - 12, "повторюваний 2×2", size=10, anchor="middle",
              weight="bold")
    for fill, yy, lab, w in [("#cc0000", 135, "25% R", "normal"),
                             ("#16a34a", 170, "50% G ← вдвічі!", "bold"),
                             ("#1f4ed8", 205, "25% B", "normal")]:
        s += rect(725, yy, 24, 24, fill=fill, stroke=INK, sw=1, opacity=0.8)
        s += text(757, yy + 18, lab, size=11, weight=w,
                  fill=("#15803d" if "G" in lab else INK))
    s += lines(725, 258, ["Зеленого вдвічі більше,", "бо з нього око бере",
                          "найбільше ДЕТАЛЕЙ", "(яскравість/люмінанс)"],
               size=10, lh=16, fill=MUTE)
    s += text(W / 2, H - 14,
              "Кожен піксель дістає лише ОДИН фільтр, тож міряє лише одну "
              "складову. Сира картина — мозаїка одноколірних точок.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.3.3 — Демозаїка
# ════════════════════════════════════════════════════════════════════════════
def fig_demosaic():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Демозаїка: кожен піксель знає лише один колір — решту вгадуємо",
               "червоний піксель позичає зелене й синє в сусідів; так у кожному пікселі зрештою є повний R+G+B")
    GC, BC = "#16a34a", "#1f4ed8"
    gx, gy, cell = 110, 130, 50
    for r in range(5):
        for c in range(5):
            s += rect(gx + c * cell, gy + r * cell, cell - 3, cell - 3,
                      fill=_bayer_col(r, c), stroke="white", sw=1, opacity=0.8)
    ccx = gx + 2 * cell + (cell - 3) / 2
    ccy = gy + 2 * cell + (cell - 3) / 2
    s += text(gx + 2.5 * cell, gy - 12, "цей піксель: лише R", size=10.5,
              anchor="middle", weight="bold", fill="#cc0000")
    for nr, nc, col in [(1, 2, GC), (2, 3, GC), (1, 1, BC), (3, 3, BC)]:
        nx = gx + nc * cell + (cell - 3) / 2
        ny = gy + nr * cell + (cell - 3) / 2
        s += line(nx, ny, ccx, ccy, stroke=col, w=1.6, dash="3,2", marker="arr",
                  opacity=0.85)
    s += rect(gx + 2 * cell - 2, gy + 2 * cell - 2, cell + 1, cell + 1,
              fill="none", stroke=INK, sw=2.6)
    s += text(gx + 2.5 * cell, gy + 5 * cell + 18, "позичає G і B у сусідів",
              size=10, anchor="middle", fill=MUTE)
    s += line(gx + 5 * cell + 12, gy + 2.5 * cell, gx + 5 * cell + 72,
              gy + 2.5 * cell, stroke=INK, w=2.2, marker="arr")
    s += text(gx + 5 * cell + 42, gy + 2.5 * cell - 10, "демозаїка", size=9.5,
              anchor="middle", fill=MUTE)
    rx = gx + 5 * cell + 88
    s += rect(rx, gy + 2 * cell - 32, 150, 114, fill="#a855f7", stroke=INK,
              sw=1.8, rx=8, opacity=0.45)
    s += text(rx + 75, gy + 2 * cell - 8, "повний колір", size=12,
              anchor="middle", weight="bold")
    s += lines(rx + 22, gy + 2 * cell + 14, ["R — виміряно", "G — вгадано",
                                             "B — вгадано"], size=10.5, lh=18)
    s += text(W / 2, H - 30,
              "У сирій мозаїці кожна точка має лише одну складову. Демозаїка "
              "інтерполює дві відсутні з сусідів —", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "і робить повноколірний кадр, де в кожному пікселі є R, G і B. "
              "Але дві з трьох складових — це ГАДКА.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.3.4 — Артефакти демозаїки
# ════════════════════════════════════════════════════════════════════════════
def fig_artifacts():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Ціна вгадування: менша кольорова роздільність і артефакти",
               "колір інтерполюють, тож на тонких деталях — несправжній колір, «застібка», муар")
    s += text(232, 110, "тонка деталь (край, смужки)", size=11, anchor="middle",
              weight="bold")
    for i in range(8):
        s += rect(120 + i * 28, 130, 28, 90,
                  fill="#1a1a1a" if i % 2 == 0 else "#f4f4f5", stroke="none")
    s += rect(120, 130, 224, 90, fill="none", stroke=INK, sw=1.4)
    s += text(232, 238, "після демозаїки →", size=10, anchor="middle",
              fill=MUTE)
    for i in range(8):
        s += rect(120 + i * 28, 252, 28, 90,
                  fill="#1a1a1a" if i % 2 == 0 else "#f4f4f5", stroke="none")
    for fx, fy, fc in [(150, 266, "#cc0000"), (208, 300, "#16a34a"),
                       (262, 272, "#1f4ed8"), (318, 318, "#cc0000"),
                       (180, 330, "#16a34a")]:
        s += rect(fx, fy, 16, 14, fill=fc, stroke="none", opacity=0.85)
    s += rect(120, 252, 224, 90, fill="none", stroke=RED, sw=1.6)
    s += text(232, 358, "✗ несправжній колір / «застібка» / муар", size=10,
              anchor="middle", fill=RED, weight="bold")
    s += rect(560, 130, 332, 92, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(726, 158, "RAW = сира мозаїка (до демозаїки)", size=11.5,
              anchor="middle", weight="bold")
    s += text(726, 182, "одна складова на піксель; найбільше даних,", size=10,
              anchor="middle", fill=MUTE)
    s += text(726, 200, "та треба «проявити» (демозаїка + обробка)", size=10,
              anchor="middle", fill=MUTE)
    s += rect(560, 242, 332, 100, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(726, 268, "Для машинного бачення (49)", size=11.5,
              anchor="middle", weight="bold", fill="#15803d")
    s += lines(580, 292, ["• артефакти збивають колірні пороги",
                          "  (хибний колір на межах)",
                          "• часто беруть зелений/яскравість або RAW"],
               size=10, lh=18)
    s += text(W / 2, H - 14,
              "Кольорова роздільність нижча за число мегапікселів: дві з трьох "
              "складових у точці — інтерпольована гадка.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.4.1 — Динамічний діапазон
# ════════════════════════════════════════════════════════════════════════════
def fig_dynamic_range():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Динамічний діапазон: від найтемнішого до найсвітлішого за кадр",
               "сенсор ловить лише смугу яскравостей (від шуму до насичення); ширша сцена обрізається")
    sx, st, sw_, sh = 150, 100, 80, 280
    for i in range(14):
        v = 255 - int(255 * i / 13)
        s += rect(sx, st + i * (sh / 14), sw_, sh / 14 + 1,
                  fill=f"rgb({v},{v},{v})", stroke="none")
    s += rect(sx, st, sw_, sh, fill="none", stroke=INK, sw=1.5)
    s += text(sx + sw_ / 2, st - 12, "СЦЕНА", size=11, anchor="middle",
              weight="bold")
    s += text(sx - 10, st + 12, "☀ небо", size=10, anchor="end", fill=MUTE)
    s += text(sx - 10, st + sh - 4, "тінь", size=10, anchor="end", fill=MUTE)
    wy0, wy1 = st + 72, st + sh - 50
    s += rect(sx + sw_ + 30, wy0, 50, wy1 - wy0, fill=BOX2, stroke=GREEN,
              sw=2.0, rx=6, opacity=0.4)
    s += line(sx + sw_, wy0, sx + sw_ + 30, wy0, stroke=GREEN, w=1.4, dash="4,3")
    s += line(sx + sw_, wy1, sx + sw_ + 30, wy1, stroke=GREEN, w=1.4, dash="4,3")
    s += text(sx + sw_ + 92, (wy0 + wy1) / 2 - 8, "ВІКНО сенсора", size=11,
              fill="#15803d", weight="bold")
    s += text(sx + sw_ + 92, (wy0 + wy1) / 2 + 8, "(шум → насичення)", size=9.5,
              fill=MUTE)
    s += text(sx + sw_ + 92, wy0 - 6, "↑ вище → пересвіт", size=9.5, fill=RED)
    s += text(sx + sw_ + 92, wy1 + 14, "↓ нижче → провал", size=9.5, fill=BLUE)
    lx = 640
    s += text(lx + 70, st - 12, "ширину міряють у СТОПАХ", size=11,
              anchor="middle", weight="bold")
    for i in range(7):
        yy = st + 8 + i * 30
        s += rect(lx, yy, 150, 24, fill="#dbeafe" if i % 2 else "#eef2ff",
                  stroke="#c7d2fe", sw=1)
        s += text(lx + 8, yy + 17, f"{i + 1} стоп = ×2 світла", size=9.5)
    s += text(lx + 75, st + 8 + 7 * 30 + 16,
              "у сенсора 8–12 стопів;", size=9.5, anchor="middle", fill=MUTE)
    s += text(lx + 75, st + 8 + 7 * 30 + 30,
              "сонячна сцена буває й 20", size=9.5, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Якщо сцена ширша за вікно сенсора — світле «вибілюється», темне "
              "«провалюється», і деталі там гинуть (47.1).", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.4.2 — Три джерела шуму
# ════════════════════════════════════════════════════════════════════════════
def fig_noise_types():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Шум: три джерела зерна в кадрі",
               "дробовий (саме світло випадкове), читання (електроніка), тепловий (нагрів і довга витримка)")
    x0 = 70
    s += rect(x0, 108, 270, 256, fill="white", stroke=BLUE, sw=1.9, rx=12)
    s += text(x0 + 135, 134, "ДРОБОВИЙ (фотонний)", size=12.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(x0 + 18, 156, ["саме світло прилітає", "випадковими порціями —",
                              "мало фотонів = більше зерна"], size=10, lh=16)
    s += text(x0 + 67, 226, "темно", size=9, anchor="middle", fill=MUTE)
    s += rect(x0 + 22, 232, 90, 78, fill="#0f172a", stroke=INK, sw=1, rx=4)
    for dx, dy in [(20, 18), (48, 40), (70, 22), (35, 58), (60, 64), (15, 45)]:
        s += circle(x0 + 22 + dx, 232 + dy, 2.4, fill="#e5e7eb", stroke="none")
    s += text(x0 + 203, 226, "світло", size=9, anchor="middle", fill=MUTE)
    s += rect(x0 + 158, 232, 90, 78, fill="#334155", stroke=INK, sw=1, rx=4)
    for k in range(40):
        s += circle(x0 + 165 + (k % 8) * 11, 240 + (k // 8) * 14, 1.8,
                    fill="#e5e7eb", stroke="none", opacity=0.7)
    s += text(x0 + 135, 338, "більше світла → менше відносного зерна", size=9,
              anchor="middle", fill=BLUE, weight="bold")
    x1 = 370
    s += rect(x1, 108, 230, 256, fill="white", stroke=AMBER, sw=1.9, rx=12)
    s += text(x1 + 115, 134, "ЧИТАННЯ", size=12.5, anchor="middle",
              weight="bold", fill="#b06b00")
    s += lines(x1 + 18, 156, ["електроніка додає", "трохи випадковості",
                              "щоразу при зчитуванні"], size=10, lh=16)
    fy = 252
    jit = [0, 3, -2, 4, -1, 2, -3, 1, 3, -2] * 6
    s += poly([(x1 + 20 + k * 4, fy + jit[k]) for k in range(48)], fill="none",
              stroke=AMBER, sw=1.4, closed=False)
    s += line(x1 + 20, fy + 26, x1 + 212, fy + 26, stroke=MUTE, w=1, dash="3,3")
    s += text(x1 + 115, fy + 46, "це «підлога шуму» (47.1)", size=9.5,
              anchor="middle", fill=MUTE)
    s += text(x1 + 115, 338, "сталий дріб, незалежний від світла", size=9,
              anchor="middle", fill="#b06b00", weight="bold")
    x2 = 630
    s += rect(x2, 108, 260, 256, fill="white", stroke=RED, sw=1.9, rx=12)
    s += text(x2 + 130, 134, "ТЕПЛОВИЙ (темновий)", size=12.5, anchor="middle",
              weight="bold", fill=RED)
    s += lines(x2 + 18, 156, ["нагрів сам народжує", "зайві електрони —",
                              "навіть у темряві"], size=10, lh=16)
    s += rect(x2 + 30, 230, 14, 70, fill="#fde2e2", stroke=INK, sw=1.2, rx=6)
    s += rect(x2 + 30, 270, 14, 30, fill=RED, stroke="none")
    s += circle(x2 + 37, 306, 12, fill=RED, stroke=INK, sw=1.2)
    s += rect(x2 + 70, 238, 162, 72, fill="#0f172a", stroke=INK, sw=1, rx=4)
    for dx, dy in [(22, 16), (62, 42), (112, 22), (142, 56), (40, 56),
                   (96, 50), (130, 18)]:
        s += circle(x2 + 70 + dx, 238 + dy, 2.6, fill="#fca5a5", stroke="none")
    s += text(x2 + 130, 338, "гірший на спеці й довгій витримці", size=9,
              anchor="middle", fill=RED, weight="bold")
    s += text(W / 2, H - 12,
              "Дробовий слабшає на світлі, читання сталий, тепловий росте з "
              "нагрівом — зерно невідворотне, та різне.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.4.3 — Сигнал-шум
# ════════════════════════════════════════════════════════════════════════════
def fig_snr():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Сигнал-шум: лік від зерна — БІЛЬШЕ СВІТЛА, а не підсилення",
               "SNR росте з кореня числа фотонів; підсилення множить і сигнал, і шум — отже не рятує")

    def snrbar(x0, label, sig, noise, col):
        out = text(x0 + 90, 112, label, size=12, anchor="middle", weight="bold",
                   fill=col)
        out += text(x0, 136, "сигнал", size=9, fill=MUTE)
        out += rect(x0, 140, 180, 28, fill="#e5e7eb", stroke="none", rx=4)
        out += rect(x0, 140, 180 * sig, 28, fill=col, stroke="none", rx=4)
        out += text(x0, 184, "шум", size=9, fill=MUTE)
        out += rect(x0, 188, 180, 16, fill="#e5e7eb", stroke="none", rx=4)
        out += rect(x0, 188, 180 * noise, 16, fill=RED, stroke="none", rx=4,
                    opacity=0.6)
        return out
    s += snrbar(90, "ТЕМНО (мало фотонів)", 0.30, 0.22, BLUE)
    s += text(180, 232, "низький SNR → зернисто", size=10.5, anchor="middle",
              fill=RED, weight="bold")
    s += snrbar(410, "СВІТЛО (багато фотонів)", 0.92, 0.13, GREEN)
    s += text(500, 232, "високий SNR → чисто", size=10.5, anchor="middle",
              fill="#15803d", weight="bold")
    s += rect(680, 132, 220, 92, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(790, 164, "SNR ∝ √(фотони)", size=15, anchor="middle",
              weight="bold")
    s += text(790, 190, "учетверо світла →", size=10, anchor="middle",
              fill=MUTE)
    s += text(790, 206, "удвічі чистіше", size=10, anchor="middle", fill=MUTE)
    s += rect(150, 296, 660, 86, fill=BOX3, stroke=AMBER, sw=1.6, rx=11)
    s += text(480, 322,
              "А підсилення (47.2)? Воно множить і сигнал, І шум — на ОДНЕ число.",
              size=12, anchor="middle", weight="bold")
    s += text(480, 346,
              "Тож SNR від фотонного шуму не поліпшити: кадр яскравішає, але не чистішає. Єдиний "
              "справжній лік — більше фотонів", size=10.5, anchor="middle",
              fill=MUTE)
    s += text(480, 366,
              "(більший піксель, ширша діафрагма, довша витримка, ясніша сцена).",
              size=9.5, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.4.4 — HDR
# ════════════════════════════════════════════════════════════════════════════
def fig_hdr():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "HDR: коли сцена ширша за сенсор — кілька кадрів в один",
               "короткий кадр ловить світле, довгий — темне; зливаємо — і в одному кадрі є і небо, і тінь")

    def frame(x0, t, sky, ground, note, col):
        out = text(x0 + 70, 106, t, size=11.5, anchor="middle", weight="bold",
                   fill=col)
        out += rect(x0 + 2, 124, 136, 63, fill=sky, stroke="none")
        out += rect(x0 + 2, 187, 136, 63, fill=ground, stroke="none")
        out += rect(x0, 122, 140, 130, fill="none", stroke=INK, sw=1.6, rx=6)
        out += text(x0 + 70, 270, note, size=9.5, anchor="middle", fill=MUTE)
        return out
    s += frame(70, "КОРОТКИЙ кадр", "#a5b4d8", "#000000",
               "небо добре, тінь чорна", BLUE)
    s += frame(270, "ДОВГИЙ кадр", "#ffffff", "#6b7280",
               "тінь добре, небо біле", AMBER)
    s += text(445, 192, "+", size=18, anchor="middle", weight="bold")
    s += frame(490, "ЗЛИТО (HDR)", "#7c93c4", "#5b6470",
               "і небо, і тінь видно", GREEN)
    s += line(636, 188, 686, 188, stroke=INK, w=2.4, marker="arr")
    s += rect(700, 128, 200, 132, fill=BOX2, stroke=GREEN, sw=1.5, rx=11)
    s += text(800, 154, "для машинного бачення", size=10.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(716, 178, ["вузький діапазон →", "ціль гине в блиску",
                          "неба чи в тіні;", "ширший DR / HDR →",
                          "ціль видно скрізь"], size=10, lh=17)
    s += text(W / 2, H - 30,
              "Сцена «яскраве небо + темна земля» легко перевищує діапазон "
              "сенсора. Кілька витримок, злитих в одну,", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "вкладають увесь діапазон у кадр. Та для рухомого апарата HDR "
              "складний (об'єкти зсуваються між кадрами).", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.5.1 — Роздільність
# ════════════════════════════════════════════════════════════════════════════
def fig_resolution():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Роздільність: скільки пікселів у кадрі",
               "ширина × висота = число відерець; більше пікселів — більше деталей, та й більше даних")
    bx, by = 90, 110
    res = [("4K (3840×2160)", 460, 259, "#dbeafe", "8.3 Мпк"),
           ("FHD 1080p (1920×1080)", 320, 180, "#bfdbfe", "2.1 Мпк"),
           ("HD 720p (1280×720)", 213, 120, "#93c5fd", "0.9 Мпк"),
           ("VGA (640×480)", 107, 80, "#60a5fa", "0.3 Мпк")]
    for name, w, h, col, mpx in res:
        s += rect(bx, by, w, h, fill=col, stroke=INK, sw=1.4, opacity=0.6)
    ly = 130
    for name, w, h, col, mpx in res:
        s += rect(610, ly, 18, 18, fill=col, stroke=INK, sw=1, opacity=0.6)
        s += text(636, ly + 14, f"{name} — {mpx}", size=11, weight="bold")
        ly += 32
    s += text(700, 280, "мало пікселів = грубо", size=10, anchor="middle",
              fill=MUTE)
    for bxx, byy in [(0, 0), (1, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2),
                     (0, 3), (2, 3)]:
        s += rect(672 + bxx * 14, 295 + byy * 14, 13, 13, fill="#334155",
                  stroke="none")
    s += text(840, 280, "багато = чітко", size=10, anchor="middle", fill=MUTE)
    s += text(840, 332, "A", size=46, anchor="middle", weight="bold",
              fill="#334155")
    s += text(W / 2, H - 14,
              "«Мегапікселі» — це лічильник відерець: вони дають різкість, але "
              "кожен зайвий ще й роздуває обсяг даних.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.5.2 — Частота кадрів
# ════════════════════════════════════════════════════════════════════════════
def fig_framerate():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Частота кадрів: відео — це швидкі знімки поспіль",
               "показуй ~24+ кадрів/с — і око зливає їх у рух (інерція зору); більше fps — плавніше, та й більше даних")
    fx, fy, fw, fh, n = 90, 116, 100, 80, 6
    s += text(fx + (n * (fw + 10)) / 2 - 5, fy - 20, "кадри (окремі знімки)",
              size=10.5, anchor="middle", weight="bold")
    for i in range(n):
        x = fx + i * (fw + 10)
        s += rect(x, fy, fw, fh, fill="#0f172a", stroke=INK, sw=1.4, rx=4)
        s += rect(x + 4, fy - 8, 10, 6, fill="white", stroke=MUTE, sw=0.8)
        s += rect(x + fw - 14, fy - 8, 10, 6, fill="white", stroke=MUTE, sw=0.8)
        s += circle(x + fw / 2, fy + fh / 2 + 22 * math.sin(i * 0.9), 9,
                    fill=AMBER, stroke="none")
    s += line(fx, fy + fh + 18, fx + n * (fw + 10) - 10, fy + fh + 18,
              stroke=INK, w=1.5, marker="arr")
    s += text(fx + n * (fw + 10) - 10, fy + fh + 34, "час →", size=10,
              anchor="end", fill=MUTE)
    s += text(fx + (n * (fw + 10)) / 2 - 5, fy + fh + 60,
              "→ показані швидко, зливаються в безперервний РУХ (інерція зору)",
              size=11, anchor="middle", fill=GREEN, weight="bold")
    yy = 326
    for lab, col, cnt in [("24 fps — кіно", MUTE, "24"),
                          ("30 fps — звичайне відео", BLUE, "30"),
                          ("60 fps — плавно (менша затримка/кадр)", GREEN, "60")]:
        s += text(120, yy + 4, lab, size=11, weight="bold", fill=col)
        s += text(560, yy + 4, f"{cnt} знімків щосекунди", size=10, fill=MUTE)
        yy += 24
    s += text(W / 2, H - 12,
              "Більше fps — плавніший рух і менша затримка на кадр, але стільки "
              "ж разів більше даних щосекунди.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.5.3 — Сирий потік
# ════════════════════════════════════════════════════════════════════════════
def fig_firehose():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Сирий потік: ширина × висота × канали × біти × кадри",
               "нестиснене відео — це пожежний шланг даних: 1080p30 ≈ 1.5 Гбіт/с, 4K60 ≈ 12 Гбіт/с")
    s += rect(120, 96, 720, 52, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(480, 128, "потік = Ш × В × канали × біти × кадри/с", size=16,
              anchor="middle", weight="bold")
    s += rect(90, 172, 360, 132, fill=BOX1, stroke=BLUE, sw=1.6, rx=11)
    s += text(270, 198, "1080p · 30 fps · 8 біт · RGB", size=12,
              anchor="middle", weight="bold", fill=BLUE)
    s += lines(112, 224, ["1920 × 1080 = 2.07 Мпк",
                          "× 3 канали × 8 біт = 49.8 Мбіт/кадр",
                          "× 30 кадрів/с ≈ 1.5 Гбіт/с"], size=11, lh=21)
    s += text(270, 294, "≈ 187 МБ щосекунди!", size=12, anchor="middle",
              weight="bold", fill=RED)
    s += rect(510, 172, 360, 132, fill=BOX3, stroke=AMBER, sw=1.6, rx=11)
    s += text(690, 198, "4K · 60 fps · 8 біт · RGB", size=12, anchor="middle",
              weight="bold", fill="#b06b00")
    s += lines(532, 224, ["3840 × 2160 = 8.3 Мпк",
                          "× 3 × 8 = 199 Мбіт/кадр", "× 60 ≈ 12 Гбіт/с"],
               size=11, lh=21)
    s += text(690, 294, "≈ 1.5 ГБ щосекунди!", size=12, anchor="middle",
              weight="bold", fill=RED)
    s += rect(120, 332, 720, 76, fill="#fde2e2", stroke=RED, sw=1.5, rx=10)
    s += text(480, 360,
              "А радіоканал FPV тягне одиниці-десятки Мбіт/с, SD-картка — сотні.",
              size=11.5, anchor="middle", weight="bold")
    s += text(480, 384,
              "Сире відео в тисячі разів більше — передати/зберегти його як є "
              "НЕМОЖЛИВО. Звідси стиснення (Розділ 48).", size=10.5,
              anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.5.4 — Компроміс
# ════════════════════════════════════════════════════════════════════════════
def fig_data_tradeoff():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Компроміс: роздільність × fps × якість проти ресурсів",
               "що більше даних, то більше треба смуги, пам'яті, обчислень, батареї — й тим вища затримка")
    s += rect(70, 110, 250, 150, fill=BOX1, stroke=BLUE, sw=1.7, rx=12)
    s += text(195, 136, "ХОЧЕМО більше", size=12.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(90, 162, ["↑ роздільність (деталі)",
                         "↑ частота кадрів (плавність)",
                         "↑ глибина біт (тони, колір)"], size=10.5, lh=24)
    s += line(328, 185, 388, 185, stroke=INK, w=2.4, marker="arr")
    s += text(358, 174, "=", size=16, anchor="middle", weight="bold")
    s += rect(400, 110, 250, 150, fill="#fde2e2", stroke=RED, sw=1.7, rx=12)
    s += text(525, 136, "ПЛАТИМО", size=12.5, anchor="middle", weight="bold",
              fill=RED)
    s += lines(420, 162, ["↑ смуга каналу / пам'ять",
                          "↑ обчислення (стиснення, ШІ)",
                          "↑ затримка й розряд батареї"], size=10.5, lh=24)
    s += rect(690, 110, 200, 150, fill=BOX2, stroke=GREEN, sw=1.7, rx=12)
    s += text(790, 134, "що обрати?", size=12, anchor="middle", weight="bold",
              fill="#15803d")
    s += lines(706, 158, ["FPV: низька ЗАТРИМКА", "+ плавність важливіші",
                          "за мегапікселі", "",
                          "МБ: баланс із бортовим", "обчислювачем (49.9)"],
               size=9.5, lh=15)
    s += rect(120, 300, 720, 58, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 324,
              "Сирого потоку ніхто не тягне — тож його СТИСКАЮТЬ, жертвуючи "
              "дрібкою якості заради в рази меншого обсягу.", size=11,
              anchor="middle", weight="bold")
    s += text(480, 345,
              "Як саме — наступний розділ (48). А поки: кожен піксель і кадр "
              "має ціну в бітах.", size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Роздільність і fps — не «що більше, то краще», а вибір під "
              "канал, обчислювач і задачу апарата.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.6.1 — Рядок як напруга
# ════════════════════════════════════════════════════════════════════════════
def fig_line_waveform():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Аналогове відео: яскравість — це напруга в часі",
               "один рядок розгортки — плавна напруга: вище = світліше; на початку — синхроімпульс «новий рядок»")
    ox, oy, ow, oh = 90, 120, 760, 200
    s += rect(ox, oy, ow, oh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)
    sync_y, black_y, white_y = oy + oh - 20, oy + oh - 60, oy + 30
    for yy, lab in [(white_y, "білий рівень"), (black_y, "чорний рівень"),
                    (sync_y, "рівень синхро")]:
        s += line(ox, yy, ox + ow, yy, stroke="#e5e7eb", w=1, dash="4,3")
        s += text(ox + ow + 6, yy + 4, lab, size=9, fill=MUTE)
    pts = [(ox, black_y), (ox + 10, black_y), (ox + 10, sync_y),
           (ox + 50, sync_y), (ox + 50, black_y), (ox + 72, black_y)]
    for k in range(80):
        f = k / 79
        b = 0.45 + 0.32 * math.sin(f * 8) + 0.16 * math.sin(f * 23)
        b = max(0.05, min(0.95, b))
        pts.append((ox + 82 + f * (ow - 102), black_y - b * (black_y - white_y)))
    s += poly(pts, fill="none", stroke=BLUE, sw=2.2, closed=False)
    s += text(ox + 30, sync_y + 16, "синхро-", size=9, anchor="middle",
              fill=RED, weight="bold")
    s += text(ox + 30, sync_y + 26, "імпульс", size=9, anchor="middle",
              fill=RED, weight="bold")
    s += text(ox + 460, white_y - 8, "активне відео = яскравість уздовж рядка",
              size=10.5, anchor="middle", fill=BLUE, weight="bold")
    s += text(ox + ow / 2, oy + oh + 22, "час (= положення вздовж рядка) →",
              size=10, anchor="middle", fill=MUTE)
    s += text(ox - 8, oy + 10, "напруга", size=10, anchor="end", fill=MUTE,
              weight="bold")
    s += text(W / 2, H - 14,
              "Це Фарнсвортова розгортка живцем: рядок — це напруга, що "
              "міняється в часі, а синхроімпульс розмежовує рядки.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.6.2 — Синхро
# ════════════════════════════════════════════════════════════════════════════
def fig_sync():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Синхро: як приймач не губить кадр",
               "горизонтальний синхро каже «початок рядка», вертикальний — «початок кадру»; без них картинка «їде»")
    ox = 90
    base, lo = 152, 178
    pts = [(ox, base), (ox + 6, base), (ox + 6, lo), (ox + 70, lo),
           (ox + 70, base)]
    x = ox + 90
    for i in range(7):
        pts += [(x, base), (x + 8, base), (x + 8, lo), (x + 22, lo),
                (x + 22, base)]
        for k in range(12):
            f = k / 11
            pts.append((x + 22 + f * 68, base - 8 - 10 * abs(math.sin(f * 6 + i))))
        x += 92
    s += poly(pts, fill="none", stroke=BLUE, sw=1.8, closed=False)
    s += text(ox + 38, lo + 16, "вертикальний синхро", size=9.5,
              anchor="middle", fill=RED, weight="bold")
    s += text(ox + 38, lo + 28, "(новий КАДР)", size=8.5, anchor="middle",
              fill=RED)
    s += text(ox + 330, lo + 16,
              "горизонтальні синхро (новий РЯДОК) ↑", size=9.5, anchor="middle",
              fill="#b06b00", weight="bold")
    s += text(245, 252, "ІЗ синхро", size=12, anchor="middle", weight="bold",
              fill=GREEN)
    s += rect(150, 266, 190, 122, fill="#0f172a", stroke=GREEN, sw=2, rx=6)
    for r in range(6):
        s += rect(158, 272 + r * 19, 174, 14, fill="#475569", stroke="none",
                  opacity=0.7)
    s += text(245, 404, "рядки рівно на місці", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(715, 252, "БЕЗ синхро", size=12, anchor="middle", weight="bold",
              fill=RED)
    s += rect(620, 266, 190, 122, fill="#0f172a", stroke=RED, sw=2, rx=6)
    for r in range(6):
        off = [-8, 16, -14, 8, 18, -4][r]
        s += rect(632 + off, 272 + r * 19, 150, 14, fill="#475569",
                  stroke="none", opacity=0.7)
    s += text(715, 404, "картинка «їде» й рветься", size=9.5, anchor="middle",
              fill=RED)
    s += text(W / 2, H - 14,
              "Синхроімпульси тримають розгортку приймача в такт із "
              "передавачем — без них рядки розповзаються в кашу.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.6.3 — Черезрядковість
# ════════════════════════════════════════════════════════════════════════════
def fig_interlace():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Кадри й поля: черезрядкова розгортка",
               "спершу непарні рядки (поле 1), тоді парні (поле 2) — два поля = кадр; половина смуги")

    def screen(x0, rows, label, col):
        out = text(x0 + 80, 110, label, size=12, anchor="middle", weight="bold",
                   fill=col)
        out += rect(x0, 124, 160, 150, fill="#0f172a", stroke=INK, sw=1.6, rx=6)
        for r in rows:
            out += rect(x0 + 6, 130 + r * 11, 148, 8, fill=col, stroke="none",
                        opacity=0.75)
        return out
    s += screen(80, range(0, 13, 2), "ПОЛЕ 1 (непарні)", BLUE)
    s += text(258, 205, "+", size=24, anchor="middle", weight="bold")
    s += screen(290, range(1, 13, 2), "ПОЛЕ 2 (парні)", AMBER)
    s += text(468, 205, "=", size=24, anchor="middle", weight="bold")
    s += screen(500, range(0, 13), "КАДР (усі рядки)", GREEN)
    s += rect(690, 124, 210, 150, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(795, 148, "стандарти FPV", size=11.5, anchor="middle",
              weight="bold")
    s += lines(708, 174, ["NTSC: 525 рядків,", "~30 кадрів/с (60 полів)", "",
                          "PAL: 625 рядків,", "25 кадрів/с (50 полів)"],
               size=10.5, lh=18)
    s += text(W / 2, H - 30,
              "Поля міняються вдвічі частіше за кадри — тож око бачить плавно за "
              "половини смуги. Спадок ери, коли смуга була золотом.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Сучасні сенсори знімають прогресивно (увесь кадр), але стара "
              "черезрядковість і досі живе в аналоговому FPV.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.6.4 — Аналог проти цифри
# ════════════════════════════════════════════════════════════════════════════
def fig_analog_vs_digital():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Чому аналоговий FPV досі живий: миттєвість і м'яка відмова",
               "аналог майже без затримки й гасне поступово (шум, та видно); цифра чіткіша, але з лагом і «обривом»")
    s += rect(70, 108, 380, 128, fill=BOX2, stroke=GREEN, sw=1.7, rx=12)
    s += text(260, 134, "АНАЛОГ", size=13, anchor="middle", weight="bold",
              fill="#15803d")
    s += lines(90, 160, ["✓ майже НУЛЬ затримки (сигнал = картинка)",
                         "✓ гасне ПЛАВНО: шум, та щось видно завжди",
                         "✗ нижча чіткість (SD), завади видно"], size=10.5,
               lh=22)
    s += rect(510, 108, 380, 128, fill=BOX1, stroke=BLUE, sw=1.7, rx=12)
    s += text(700, 134, "ЦИФРА (HD FPV)", size=13, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(530, 160, ["✓ чітка HD-картинка",
                          "✗ ЛАГ: кодування → передача → декодування",
                          "✗ «обрив»: за порогом — фриз/квадрати/чорне"],
               size=10.5, lh=22)
    ox, oy, ow, oh = 140, 282, 680, 122
    s += line(ox, oy, ox, oy + oh, stroke=INK, w=1.3)
    s += line(ox, oy + oh, ox + ow, oy + oh, stroke=INK, w=1.3)
    s += text(ox - 8, oy + 8, "якість", size=9.5, anchor="end", fill=MUTE)
    s += text(ox + ow, oy + oh + 18, "слабшає сигнал →", size=9.5, anchor="end",
              fill=MUTE)
    s += poly([(ox + ow * k / 60, oy + 10 + (oh - 20) * (k / 60) ** 1.4)
               for k in range(61)], fill="none", stroke=GREEN, sw=2.4,
              closed=False)
    s += text(ox + ow * 0.68, oy + oh * 0.5, "аналог: плавно гасне", size=10,
              fill="#15803d", weight="bold")
    s += poly([(ox, oy + 12), (ox + ow * 0.62, oy + 16),
               (ox + ow * 0.66, oy + oh - 8), (ox + ow, oy + oh - 8)],
              fill="none", stroke=BLUE, sw=2.4, closed=False)
    s += text(ox + ow * 0.28, oy + 26, "цифра: чітко…", size=10, fill=BLUE,
              weight="bold")
    s += text(ox + ow * 0.72, oy + oh - 22, "…тоді ОБРИВ", size=10, fill=RED,
              weight="bold")
    s += text(W / 2, H - 12,
              "Коли летиш «очима» камери, ліпше шумна, та жива картинка, ніж "
              "чиста, що зненацька замерзає. Тому гонщики довго трималися аналогу.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.7.1 — Скло-до-скла
# ════════════════════════════════════════════════════════════════════════════
def fig_glass_to_glass():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Затримка «скло-до-скла»: сума всіх кроків",
               "від фотона на сенсорі до картинки в очах кожен крок додає мілісекунди; цифра має зайві ланки")
    s += text(80, 116, "АНАЛОГ", size=12.5, weight="bold", fill="#15803d")
    x = 80
    for i, (l1, l2, ms) in enumerate([("сенсор", "+ зчитування", "~10"),
                                      ("передача", "(радіо)", "~1"),
                                      ("екран", "", "~5")]):
        s += rect(x, 128, 130, 64, fill=BOX2, stroke=GREEN, sw=1.5, rx=9)
        s += text(x + 65, 150, l1, size=10, anchor="middle", weight="bold")
        s += text(x + 65, 164, l2, size=10, anchor="middle")
        s += text(x + 65, 184, ms + " мс", size=10, anchor="middle",
                  fill="#15803d", weight="bold")
        if i < 2:
            s += line(x + 132, 160, x + 148, 160, stroke=INK, w=1.8,
                      marker="arr")
        x += 150
    s += text(x + 36, 156, "≈ 16 мс", size=15, weight="bold", fill="#15803d")
    s += text(x + 36, 176, "(майже миттєво)", size=9, fill=MUTE)
    s += text(80, 250, "ЦИФРА (HD)", size=12.5, weight="bold", fill=BLUE)
    x = 80
    for i, (l1, l2, ms) in enumerate([("сенсор", "+ зчитування", "~10"),
                                      ("кодування", "(стиснення)", "~20"),
                                      ("передача", "+ буфер", "~15"),
                                      ("декоду-", "вання", "~15"),
                                      ("екран", "", "~10")]):
        s += rect(x, 262, 118, 64, fill=BOX1, stroke=BLUE, sw=1.5, rx=9)
        s += text(x + 59, 284, l1, size=9.5, anchor="middle", weight="bold")
        s += text(x + 59, 297, l2, size=9.5, anchor="middle")
        s += text(x + 59, 316, ms + " мс", size=9.5, anchor="middle", fill=BLUE,
                  weight="bold")
        if i < 4:
            s += line(x + 120, 294, x + 134, 294, stroke=INK, w=1.6,
                      marker="arr")
        x += 134
    s += text(W / 2, 360,
              "≈ 70 мс — зайві ланки кодування/декодування додають десятки мс лагу",
              size=11, anchor="middle", fill=RED, weight="bold")
    s += text(W / 2, H - 14,
              "«Скло-до-скла» — повний час від світла на лінзі камери до світла "
              "на твоєму екрані. Кожен крок коштує мілісекунд.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.7.2 — Летиш у минулому
# ════════════════════════════════════════════════════════════════════════════
def fig_flying_the_past():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Летиш у минулому: бачиш, де апарат БУВ",
               "поки кадр дійшов, апарат уже зрушив; реагуєш на старе → перекерування й розгойдування")
    ty = 200
    s += line(80, ty, 880, ty, stroke="#e5e7eb", w=2)
    px, nx = 320, 620
    s += line(px + 14, ty - 24, nx - 18, ty - 24, stroke=RED, w=1.6, dash="4,3")
    s += text((px + nx) / 2, ty - 32, "за час затримки апарат проїхав сюди",
              size=10, anchor="middle", fill=RED)
    s += circle(px, ty, 12, fill="#9ca3af", stroke=INK, sw=1.5, opacity=0.7)
    s += text(px, ty + 34, "де апарат на ЕКРАНІ", size=10.5, anchor="middle",
              weight="bold", fill=MUTE)
    s += text(px, ty + 50, "(кадр уже застарів)", size=9.5, anchor="middle",
              fill=MUTE)
    s += poly([(nx - 14, ty - 12), (nx + 16, ty), (nx - 14, ty + 12)],
              fill=BLUE, stroke=INK, sw=1.2)
    s += text(nx, ty - 26, "де апарат НАСПРАВДІ", size=10.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += rect(120, 300, 720, 82, fill="#fde2e2", stroke=RED, sw=1.5, rx=10)
    s += text(480, 326,
              "Пілот керує по застарілій картинці → виправляє «навздогін» уже неактуальне →",
              size=11.5, anchor="middle", weight="bold")
    s += text(480, 348,
              "перекручує, апарат проскакує, і починається РОЗГОЙДУВАННЯ (перерегулювання з 34).",
              size=10.5, anchor="middle", fill=MUTE)
    s += text(480, 368,
              "На швидкості 20 м/с навіть 100 мс — це два метри наосліп.",
              size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Затримка відео — це затримка в петлі керування (хоч людиною, хоч "
              "алгоритмом): діє на минуле, не на тепер.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.7.3 — Затримка в петлі
# ════════════════════════════════════════════════════════════════════════════
def fig_loop_delay():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Затримка в петлі — ворог стійкості",
               "бачу → вирішую → дію → бачу… із затримкою кожне виправлення спізнюється й розгойдує")
    s += line(290, 162, 350, 222, stroke=INK, w=2.2, marker="arr")
    s += line(330, 274, 170, 274, stroke=INK, w=2.2, marker="arr")
    s += line(150, 222, 210, 162, stroke=RED, w=2.4, marker="arrR")
    s += rect(108, 178, 84, 22, fill="#fde2e2", stroke=RED, sw=1.4, rx=6)
    s += text(150, 193, "ЗАТРИМКА відео", size=8.5, anchor="middle", fill=RED,
              weight="bold")
    for t1, t2, nx, ny, col in [("БАЧУ", "(відео)", 250, 137, BLUE),
                                ("ВИРІШУЮ", "(керування)", 375, 252, INK),
                                ("ДІЮ", "(мотори)", 125, 252, GREEN)]:
        s += circle(nx, ny, 42, fill="white", stroke=col, sw=2.0)
        s += text(nx, ny - 2, t1, size=11, anchor="middle", weight="bold",
                  fill=col)
        s += text(nx, ny + 13, t2, size=8.5, anchor="middle", fill=MUTE)
    ox, ow = 560, 330

    def plot(y0, decay, label, col):
        out = text(ox + ow / 2, y0 - 12, label, size=10.5, anchor="middle",
                   weight="bold", fill=col)
        out += line(ox, y0, ox + ow, y0, stroke="#e5e7eb", w=1)
        out += poly([(ox + ow * k / 79,
                      y0 - 30 * math.exp(decay * k / 79) * math.cos(k / 79 * 16))
                     for k in range(80)], fill="none", stroke=col, sw=2.0,
                    closed=False)
        return out
    s += plot(175, -2.2, "мала затримка → стихає (стійко)", GREEN)
    s += plot(310, 1.0, "велика затримка → РОЗГОЙДУЄТЬСЯ", RED)
    s += text(W / 2, H - 14,
              "Та сама хвороба, що в керуванні (34) і фьюжні (46.6): затримка у "
              "зворотному зв'язку перетворює виправлення на розгойдування.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 47.7.4 — Бюджет затримки
# ════════════════════════════════════════════════════════════════════════════
def fig_latency_budget():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Бюджет затримки: що ще «летабельно»",
               "аналог ~десятки мс, цифрове HD ~десятки–сотня, стрім ~сотні (нелетабельно); менша затримка коштує якості")
    ox, oy, ow = 110, 200, 740
    s += rect(ox, oy - 46, ow * 0.28, 36, fill="#d8f3e0", stroke=GREEN, sw=1.3,
              rx=5)
    s += text(ox + ow * 0.14, oy - 22, "ЛЕТАБЕЛЬНО", size=10, anchor="middle",
              weight="bold", fill="#15803d")
    s += rect(ox + ow * 0.28, oy - 46, ow * 0.24, 36, fill="#fff0d8",
              stroke=AMBER, sw=1.3, rx=5)
    s += text(ox + ow * 0.40, oy - 22, "на межі", size=10, anchor="middle",
              weight="bold", fill="#b06b00")
    s += rect(ox + ow * 0.52, oy - 46, ow * 0.48, 36, fill="#fde2e2",
              stroke=RED, sw=1.3, rx=5)
    s += text(ox + ow * 0.76, oy - 22, "НЕЛЕТАБЕЛЬНО (керувати неможливо)",
              size=10, anchor="middle", weight="bold", fill=RED)
    s += line(ox, oy, ox + ow, oy, stroke=INK, w=2, marker="arr")
    s += text(ox + ow, oy + 24, "затримка (мс) →", size=10, anchor="end",
              fill=MUTE)
    for f, lab in [(0, "0"), (0.16, "30"), (0.33, "70"), (0.5, "150"),
                   (0.75, "300"), (1.0, "700")]:
        x = ox + ow * f
        s += line(x, oy - 5, x, oy + 5, stroke=INK, w=1.4)
        s += text(x, oy + 20, lab, size=9, anchor="middle", fill=MUTE)
    for f, l1, l2, col in [(0.10, "аналоговий", "FPV ~20–40", GREEN),
                           (0.33, "цифрове", "HD FPV ~70–130", BLUE),
                           (0.85, "телефон/стрім", "~300–700", RED)]:
        x = ox + ow * f
        s += line(x, oy, x, oy + 36, stroke=col, w=1.4, dash="3,3")
        s += circle(x, oy, 5, fill=col, stroke=INK, sw=1.2)
        s += text(x, oy + 50, l1, size=10, anchor="middle", weight="bold",
                  fill=col)
        s += text(x, oy + 65, l2, size=9.5, anchor="middle", fill=MUTE)
    s += rect(120, 330, 720, 76, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 356,
              "Менша затримка майже завжди коштує якості/чіткості (менше стиснення, простіший тракт).",
              size=11, anchor="middle", weight="bold")
    s += text(480, 378,
              "FPV обирає затримку понад роздільність. А для машинного бачення «затримка» — це час обчислень (49.9):",
              size=10, anchor="middle", fill=MUTE)
    s += text(480, 396,
              "повільний точний алгоритм у петлі гірший за швидкий простий — бо діє на застаріле.",
              size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Поріг «летабельності» — десь до ~50–100 мс; за ним керувати "
              "дедалі важче, а за ~200 — майже неможливо.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-47-0-1-scanning.svg":     fig_scanning,
    "fig-47-0-2-mechanical-vs-electronic.svg": fig_mechanical_vs_electronic,
    "fig-47-0-3-image-dissector.svg": fig_image_dissector,
    "fig-47-0-4-legacy.svg":       fig_legacy,
    "fig-47-1-1-photoelectric.svg": fig_photoelectric,
    "fig-47-1-2-bucket.svg":       fig_bucket,
    "fig-47-1-3-exposure.svg":     fig_exposure,
    "fig-47-1-4-saturation.svg":   fig_saturation,
    "fig-47-2-1-matrix.svg":       fig_matrix,
    "fig-47-2-2-rolling-shutter.svg": fig_rolling_shutter,
    "fig-47-2-3-exposure-gain.svg": fig_exposure_gain,
    "fig-47-2-4-triangle.svg":     fig_triangle,
    "fig-47-s2-1-bucketbrigade.svg": fig_ccd_bucketbrigade,
    "fig-47-s2-2-ccd-vs-cmos.svg": fig_ccd_vs_cmos,
    "fig-47-s2-3-legacy.svg":      fig_ccd_legacy,
    "fig-47-3-1-colorblind.svg":   fig_colorblind,
    "fig-47-3-2-bayer.svg":        fig_bayer,
    "fig-47-3-3-demosaic.svg":     fig_demosaic,
    "fig-47-3-4-artifacts.svg":    fig_artifacts,
    "fig-47-4-1-dynamic-range.svg": fig_dynamic_range,
    "fig-47-4-2-noise-types.svg":  fig_noise_types,
    "fig-47-4-3-snr.svg":          fig_snr,
    "fig-47-4-4-hdr.svg":          fig_hdr,
    "fig-47-5-1-resolution.svg":   fig_resolution,
    "fig-47-5-2-framerate.svg":    fig_framerate,
    "fig-47-5-3-firehose.svg":     fig_firehose,
    "fig-47-5-4-tradeoff.svg":     fig_data_tradeoff,
    "fig-47-6-1-line-waveform.svg": fig_line_waveform,
    "fig-47-6-2-sync.svg":         fig_sync,
    "fig-47-6-3-interlace.svg":    fig_interlace,
    "fig-47-6-4-analog-vs-digital.svg": fig_analog_vs_digital,
    "fig-47-7-1-glass-to-glass.svg": fig_glass_to_glass,
    "fig-47-7-2-flying-the-past.svg": fig_flying_the_past,
    "fig-47-7-3-loop-delay.svg":   fig_loop_delay,
    "fig-47-7-4-budget.svg":       fig_latency_budget,
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "img")
    os.makedirs(out, exist_ok=True)
    for name, fn in FIGS.items():
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", name)


if __name__ == "__main__":
    main()
