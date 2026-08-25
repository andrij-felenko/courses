# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-016 — RGB-світлодіод».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED = "#c0392b"
GRN = "#27ae60"
BLU = "#2457d6"


def led_symbol(x_top, y_top, x_bot, y_bot, color):
    """Схематичний світлодіод (трикутник-діод + дві стрілки випромінювання)
    вертикально від (x_top,y_top) до (x_bot,y_bot). Анод угорі, катод унизу."""
    out = []
    cx = x_top
    # вивід зверху до трикутника
    out.append(line(cx, y_top, cx, y_top + 14, color=INK, sw=1.8))
    ay = y_top + 14
    by = y_bot - 14
    midy = (ay + by) / 2
    # трикутник (вершина донизу — напрям струму), сторона 22
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="1.6"/>'
               % (cx - 12, ay + 4, cx + 12, ay + 4, cx, midy + 4, color, INK))
    # смужка катода
    out.append(line(cx - 12, midy + 4, cx + 12, midy + 4, color=INK, sw=2.2))
    # вивід донизу
    out.append(line(cx, midy + 4, cx, y_bot, color=INK, sw=1.8))
    # дві стрілочки випромінювання (вбік-угору)
    for k in range(2):
        sx = cx + 14 + k * 9
        sy = ay + 8 + k * 8
        out.append(arrow(sx, sy, sx + 16, sy - 12, color=color, sw=1.5))
    return out


# ── 1. Внутрішня схема KY-016: 3 світлодіоди в одному корпусі, спільний катод ──
def fig_ky016_schematic():
    W, H = 940, 500
    f = [text(W / 2, 30, "Що всередині KY-016: три світлодіоди в одному корпусі, спільний катод, по резистору на колір",
              size=14.5, bold=True)]

    bx, by, bw, bh = 90, 66, 760, 330
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 22, "плата KY-016", size=11, bold=True, color=MUTED, anchor="start"))

    # три вхідні піни-аноди зверху: R, G, B (на платі — типово 150 Ом на всіх трьох)
    pin_y = by + 44
    cols = [("R", RED, bx + bw * 0.24, "150 Ом"),
            ("G", GRN, bx + bw * 0.44, "150 Ом"),
            ("B", BLU, bx + bw * 0.64, "150 Ом")]
    # спільна шина катода (низ)
    cath_y = by + bh - 46
    f.append(line(cols[0][2] - 20, cath_y, cols[2][2] + 20, cath_y, color=INK, sw=2.4))

    for lab, col, cx, rlab in cols:
        # контактний майданчик пін
        f.append(circle(cx, pin_y, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(cx, pin_y - 12, lab, size=13, bold=True, color=col))
        # резистор (прямокутник) під піном
        rt = pin_y + 14
        f.append(rect(cx - 15, rt, 30, 30, fill=BG, stroke=INK, sw=1.6, rx=3))
        f.append(text(cx + 24, rt + 19, rlab, size=10, color=MUTED, anchor="start"))
        f.append(line(cx, pin_y + 6, cx, rt, color=col, sw=1.8))
        # світлодіод під резистором до катодної шини
        f.extend(led_symbol(cx, rt + 30, cx, cath_y, col))

    # мітка спільного катода
    f.append(circle((cols[0][2] + cols[2][2]) / 2, cath_y + 34, 6, fill=BG, stroke=NEG, sw=2.2))
    f.append(line((cols[0][2] + cols[2][2]) / 2, cath_y, (cols[0][2] + cols[2][2]) / 2, cath_y + 28,
                  color=NEG, sw=1.8))
    f.append(text((cols[0][2] + cols[2][2]) / 2, cath_y + 52, "−  (спільний катод → GND)",
                  size=12, bold=True, color=NEG))

    # пояснювальний блок праворуч
    b, _, _ = textbox(bx + bw - 150, by + bh / 2 - 4,
                      "Три кристали\nчервоний · зелений · синій\nв одному 5-мм корпусі.\n"
                      "Катоди зведені разом —\nце «−». Аноди виведено\nокремо: R, G, B.",
                      size=10.5, fill="#eef1f5", stroke=INK)
    f.append(b)

    b, _, _ = textbox(W / 2, 458,
                      "Резистори вже на платі: підключай R/G/B прямо до пінів МК, окремі не потрібні.\n"
                      "Спільний катод: колір світиться, коли на його пін подано «+», а «−» сидить на землі.",
                      size=11, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky016-schematic.svg"), W, H, *f)


# ── 2. Підключення пін-у-пін: KY-016 ↔ МК, три PWM-піни + GND ─────────────────
def fig_ky016_wiring():
    W, H = 940, 470
    f = [text(W / 2, 30, "Підключення KY-016: три кольорові піни — на PWM-виходи, спільний «−» — на GND",
              size=14.5, bold=True)]

    mx, my, mw, mh = 70, 96, 250, 250
    f.append(rect(mx, my, mw, mh, fill="#fff8e6", stroke=INK, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-016", size=15, bold=True, color=INK))
    f.append(text(mx + mw / 2, my + 47, "RGB-світлодіод", size=10, color=MUTED))
    pads = [("R", RED, my + 92), ("G", GRN, my + 132), ("B", BLU, my + 172), ("−", NEG, my + 212)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=13, bold=True, color=col, anchor="end"))

    bx, by, bw, bh = 600, 96, 270, 250
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("D9 ~", RED, by + 92, "PWM-вихід"),
            ("D10 ~", GRN, by + 132, "PWM-вихід"),
            ("D11 ~", BLU, by + 172, "PWM-вихід"),
            ("GND", NEG, by + 212, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    b, _, _ = textbox(W / 2, 410,
                      "R, G, B — на піни з тильдою «~» (апаратний PWM): яскравість кожного кольору задає analogWrite.\n"
                      "Спільний «−» — на GND. Резистори на платі вже є, тож 5-вольтові піни підключаються напряму.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky016-wiring.svg"), W, H, *f)


# ── 3. Адитивне змішування: R+G+B у кольорі; кут PWM → відтінок ────────────────
def fig_color_mixing():
    W, H = 940, 470
    f = [text(W / 2, 30, "Адитивне змішування: три яскравості R·G·B складаються у мільйони відтінків",
              size=14.5, bold=True)]

    # три кола, що перетинаються (класична діаграма RGB)
    cxs = 300
    cy = 210
    r = 92
    d = 62  # зсув центрів від спільної точки
    import math as _m
    centers = [
        (cxs, cy - d, RED, "Ч"),                       # червоний угорі
        (cxs - d * 0.87, cy + d * 0.5, GRN, "З"),      # зелений ліворуч-низ
        (cxs + d * 0.87, cy + d * 0.5, BLU, "С"),      # синій праворуч-низ
    ]
    # напівпрозорі кола зі змішуванням «screen»
    f.append('<g style="mix-blend-mode:screen">')
    for (ccx, ccy, col, _) in centers:
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.72"/>'
                 % (ccx, ccy, r, col))
    f.append('</g>')
    # обведення кіл, щоб межі читалися
    for (ccx, ccy, col, _) in centers:
        f.append(circle(ccx, ccy, r, fill="none", stroke=col, sw=1.4))

    # підписи чистих кольорів зовні
    f.append(text(cxs, cy - d - r - 10, "червоний", size=11, bold=True, color=RED))
    f.append(text(cxs - d * 0.87 - r - 6, cy + d * 0.5 + 4, "зелений", size=11, bold=True, color=GRN, anchor="end"))
    f.append(text(cxs + d * 0.87 + r + 6, cy + d * 0.5 + 4, "синій", size=11, bold=True, color=BLU, anchor="start"))
    # центр — білий
    f.append(text(cxs, cy + 24, "усі троє → білий", size=10, bold=True, color=INK))

    # права колонка — таблиця «яскравості → колір»
    tx = 600
    rows = [
        ("255, 0, 0", RED, "червоний"),
        ("0, 255, 0", GRN, "зелений"),
        ("0, 0, 255", BLU, "синій"),
        ("255, 255, 0", "#e6b800", "жовтий (Ч+З)"),
        ("0, 255, 255", "#17a2b8", "блакитний (З+С)"),
        ("255, 0, 255", "#b52dbb", "пурпуровий (Ч+С)"),
        ("255, 255, 255", "#dddddd", "білий (усі)"),
        ("0, 0, 0", "#222222", "вимкнено"),
    ]
    f.append(text(tx, 78, "analogWrite(R, G, B)  →  колір", size=11.5, bold=True, color=INK, anchor="start"))
    ry = 98
    for code, sw_col, name in rows:
        f.append(rect(tx, ry, 26, 22, fill=sw_col, stroke=INK, sw=1.2, rx=4))
        f.append(text(tx + 36, ry + 16, code, size=10.5, color=INK, anchor="start"))
        f.append(text(tx + 150, ry + 16, name, size=10.5, color=MUTED, anchor="start"))
        ry += 30

    b, _, _ = textbox(cxs, 430,
                      "Кожен колір має 256 рівнів яскравості (0…255 через PWM).\n"
                      "256 × 256 × 256 ≈ 16.7 млн комбінацій — звідси «повнокольоровий».",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "color-mixing.svg"), W, H, *f)


# ── 4. RGB як 3-вимірний куб яскравостей (для math-вставки) ───────────────────
def fig_rgb_cube():
    """Одиничний куб (R,G,B). Осі — три яскравості; вершини — чисті кольори
    й вторинні суміші; діагональ 0→1 — сіра вісь; точка всередині — довільний
    колір. Ізометрична проєкція."""
    W, H = 940, 560
    f = [text(W / 2, 30, "Простір кольорів KY-016 — куб трьох яскравостей (R, G, B)",
              size=14.5, bold=True)]

    # ── ізометрія: 3D (u,v,w)∈[0,1] → 2D екран ────────────────────────────────
    ox, oy = 300, 420          # екранна позиція початку (0,0,0)
    sx = 210                   # масштаб уздовж R (праворуч-вниз)
    ax_r = (sx * 0.94, sx * 0.34)     # напрям осі R (червоний): праворуч-вниз
    ax_g = (sx * 0.94, -sx * 0.34)    # напрям осі G (зелений): праворуч-вгору
    ax_b = (0.0, -sx * 1.0)           # напрям осі B (синій): вгору

    def P(r, g, b):
        return (ox + r * ax_r[0] + g * ax_g[0] + b * ax_b[0],
                oy + r * ax_r[1] + g * ax_g[1] + b * ax_b[1])

    # вершини куба
    V = {(r, g, b): P(r, g, b) for r in (0, 1) for g in (0, 1) for b in (0, 1)}

    # ребра (пари вершин, що різняться однією координатою)
    def edges():
        seen = []
        verts = list(V.keys())
        for a in verts:
            for c in verts:
                if a < c and sum(1 for i in range(3) if a[i] != c[i]) == 1:
                    seen.append((a, c))
        return seen

    for a, c in edges():
        x1, y1 = V[a]; x2, y2 = V[c]
        f.append(line(x1, y1, x2, y2, color="#9aa3ad", sw=1.4))

    # сіра діагональ (0,0,0)→(1,1,1)
    x1, y1 = V[(0, 0, 0)]; x2, y2 = V[(1, 1, 1)]
    f.append(line(x1, y1, x2, y2, color=INK, sw=2.0, dash="5,4"))

    # кольорові кружки на вершинах
    vcol = {
        (0, 0, 0): ("#222222", "чорний 0,0,0", "end", -14, 4),
        (1, 0, 0): (RED, "червоний 255,0,0", "start", 12, 8),
        (0, 1, 0): (GRN, "зелений 0,255,0", "start", 12, 0),
        (0, 0, 1): (BLU, "синій 0,0,255", "middle", 0, -14),
        (1, 1, 0): ("#e6b800", "жовтий", "start", 12, 4),
        (0, 1, 1): ("#17a2b8", "блакитний", "start", 12, 4),
        (1, 0, 1): ("#b52dbb", "пурпуровий", "start", 12, 4),
        (1, 1, 1): ("#e9e9e9", "білий 255,255,255", "start", 12, -6),
    }
    for v, (col, lab, anc, dx, dy) in vcol.items():
        x, y = V[v]
        f.append(circle(x, y, 8, fill=col, stroke=INK, sw=1.5))
        f.append(text(x + dx, y + dy, lab, size=10.5, bold=True,
                      color=col if col not in ("#e9e9e9", "#e6b800") else INK, anchor=anc))

    # довільна точка всередині — приклад «теплий помаранчевий» (1, .35, 0)
    px, py = P(1.0, 0.35, 0.05)
    f.append(circle(px, py, 6, fill="#ff7a1a", stroke=INK, sw=1.4))
    f.append(text(px + 10, py + 16, "(255, 90, 0)", size=10, color=INK, anchor="start"))

    # підписи осей біля початку
    xr, yr = P(1, 0, 0); f.append(text(xr + 6, yr + 22, "R →", size=12, bold=True, color=RED, anchor="start"))
    xg, yg = P(0, 1, 0); f.append(text(xg + 6, yg - 10, "G →", size=12, bold=True, color=GRN, anchor="start"))
    xb, yb = P(0, 0, 1); f.append(text(xb - 26, yb + 6, "↑ B", size=12, bold=True, color=BLU, anchor="end"))

    # пояснення — у нижньому-правому куті, ПОЗА кубом (щоб ребра не різали напис)
    b, _, _ = textbox(772, 492,
                      "Кожен колір — точка (R, G, B)\nу кубі 256×256×256.\n"
                      "Вершини — чисті кольори\nй попарні суміші.\n"
                      "Пунктир 0→білий — сіра вісь R=G=B.",
                      size=10.5, fill="#eef1f5", stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "rgb-cube.svg"), W, H, *f)


# ── 5. Гамма-крива: шпаруватість ≠ яскравість для ока ──────────────────────────
def fig_gamma():
    """Дві криві у площині (вхід 0..1 → сприйнята яскравість 0..1):
    пряма (лінійна ШІМ) і γ-крива perceived≈linear^2.2. Показано, що
    шпаруватість 50% дає оком лише ~22%."""
    W, H = 940, 520
    f = [text(W / 2, 30, "Чому шпаруватість 50 % — це не «пів-яскравості» для ока (гамма)",
              size=14.5, bold=True)]

    # система координат
    gx, gy = 130, 430        # початок (0,0)
    gw, gh = 470, 340        # ширина/висота поля
    f.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.6))         # вісь X
    f.append(line(gx, gy, gx, gy - gh, color=INK, sw=1.6))         # вісь Y
    f.append(text(gx + gw / 2, gy + 40, "шпаруватість ШІМ (вхід)", size=11.5, color=INK))
    # підпис осі Y — двома короткими рядками, лівіше за всі позначки шкали (0.50 тощо)
    f.append(text(gx - 88, gy - gh / 2, "сприйнята", size=11, color=INK))
    f.append(text(gx - 88, gy - gh / 2 + 15, "яскравість", size=11, color=INK))

    # сітка + позначки 0..1
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        X = gx + t * gw
        Y = gy - t * gh
        f.append(line(X, gy, X, gy - gh, color="#e3e7ec", sw=1.0))
        f.append(line(gx, Y, gx + gw, Y, color="#e3e7ec", sw=1.0))
        f.append(text(X, gy + 18, "%.2f" % t, size=9.5, color=MUTED))
        f.append(text(gx - 12, Y + 4, "%.2f" % t, size=9.5, color=MUTED, anchor="end"))

    # пряма (лінійна): perceived = input
    f.append(line(gx, gy, gx + gw, gy - gh, color="#9aa3ad", sw=1.8, dash="6,4"))
    # підпис у верхньому-лівому трикутнику, між сітковими лініями (не на них)
    f.append(text(gx + gw * 0.30, gy - gh * 0.86, "лінійна ШІМ", size=10, color=MUTED, anchor="end"))
    f.append(text(gx + gw * 0.30, gy - gh * 0.86 + 13, "(наївно)", size=10, color=MUTED, anchor="end"))

    # γ-крива perceived = input^2.2
    pts = []
    N = 60
    for i in range(N + 1):
        t = i / N
        p = t ** 2.2
        pts.append("%.1f,%.1f" % (gx + t * gw, gy - p * gh))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    f.append(text(gx + gw * 0.62, gy - (0.62 ** 2.2) * gh - 10,
                  "око: perceived ≈ вхід²·²", size=10.5, bold=True, color=POS, anchor="middle"))

    # маркер 50% → 22%
    X50 = gx + 0.5 * gw
    Y50 = gy - (0.5 ** 2.2) * gh
    f.append(line(X50, gy, X50, Y50, color=INK, sw=1.4, dash="3,3"))
    f.append(line(gx, Y50, X50, Y50, color=INK, sw=1.4, dash="3,3"))
    f.append(circle(X50, Y50, 5, fill=POS, stroke=INK, sw=1.4))
    # підпис маркера — вище точки, між сітковими лініями (не на y-сітці 0.25)
    f.append(text(X50 + 10, Y50 - 22, "50 % → ~22 %", size=10.5, bold=True, color=POS, anchor="start"))

    # права колонка — таблиця відповідності
    tx = 660
    f.append(text(tx, 90, "хочеш яскравість → задай ШІМ", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(tx, 108, "duty = round(255 · (L/255)^(1/2.2))", size=10.5, color=MUTED, anchor="start"))
    rows = [("0 %", "0"), ("10 %", "90"), ("25 %", "136"),
            ("50 %", "186"), ("75 %", "224"), ("100 %", "255")]
    ry = 140
    f.append(text(tx, ry, "бажана L", size=10.5, bold=True, color=INK, anchor="start"))
    f.append(text(tx + 130, ry, "duty (0…255)", size=10.5, bold=True, color=INK, anchor="start"))
    ry += 10
    f.append(line(tx, ry, tx + 250, ry, color="#c8ced6", sw=1.2))
    ry += 22
    for want, duty in rows:
        f.append(text(tx, ry, want, size=10.5, color=INK, anchor="start"))
        f.append(text(tx + 130, ry, duty, size=10.5, color=POS, anchor="start"))
        ry += 26

    b, _, _ = textbox(tx + 125, ry + 34,
                      "Щоб яскравість РОСЛА рівно на око,\n"
                      "ШІМ треба гнати по кривій, а не прямій:\n"
                      "лінійний повзунок здається «стрибком\n"
                      "на початку, застоєм у кінці».",
                      size=10, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "gamma-curve.svg"), W, H, *f)


# ── 6. HSV → RGB: розгортка відтінку 0..360° у три канали ─────────────────────
def fig_hsv_wheel():
    """Верх: як три канали R,G,B «розгоряються/гаснуть» уздовж H=0..360°
    (три трапеції-хвилі, зсунуті на 120°). Низ: те саме, згорнуте в колесо."""
    W, H = 940, 560
    f = [text(W / 2, 30, "HSV → RGB: рівномірний обхід відтінку H розкладається у три канали",
              size=14.5, bold=True)]

    # ── графік каналів уздовж H ───────────────────────────────────────────────
    gx, gy = 90, 250
    gw, gh = 620, 150
    f.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.5))     # X (H)
    f.append(line(gx, gy, gx, gy - gh - 6, color=INK, sw=1.5)) # Y (рівень)
    f.append(text(gx + gw / 2, gy + 54, "відтінок H (градуси навколо кола)", size=11, color=INK))
    f.append(text(gx - 20, gy - gh - 2, "255", size=9.5, color=MUTED, anchor="end"))
    f.append(text(gx - 20, gy + 4, "0", size=9.5, color=MUTED, anchor="end"))

    # позначки 0,60,…,360 + назви секторів
    marks = [(0, "0°"), (60, "60°"), (120, "120°"), (180, "180°"),
             (240, "240°"), (300, "300°"), (360, "360°")]
    for deg, lab in marks:
        X = gx + deg / 360.0 * gw
        f.append(line(X, gy, X, gy + 6, color=INK, sw=1.2))
        f.append(text(X, gy + 22, lab, size=9.5, color=MUTED))

    # значення каналу за кутом (S=V=1): стандартна HSV→RGB
    def chan(h):
        import math as _m
        c = 1.0
        hp = (h % 360) / 60.0
        x = c * (1 - abs(hp % 2 - 1))
        if   hp < 1: r, g, b = c, x, 0
        elif hp < 2: r, g, b = x, c, 0
        elif hp < 3: r, g, b = 0, c, x
        elif hp < 4: r, g, b = 0, x, c
        elif hp < 5: r, g, b = x, 0, c
        else:        r, g, b = c, 0, x
        return r, g, b

    series = {RED: [], GRN: [], BLU: []}
    NH = 180
    for i in range(NH + 1):
        h = i / NH * 360.0
        r, g, b = chan(h)
        X = gx + h / 360.0 * gw
        series[RED].append((X, gy - r * gh))
        series[GRN].append((X, gy - g * gh))
        series[BLU].append((X, gy - b * gh))
    for col, pts in series.items():
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join("%.1f,%.1f" % p for p in pts), col))
    f.append(text(gx + gw + 8, series[RED][-1][1] + 4, "R", size=12, bold=True, color=RED, anchor="start"))
    f.append(text(gx + 8, series[GRN][0][1] - 6, "G", size=12, bold=True, color=GRN, anchor="start"))
    f.append(text(gx + gw * 0.66, gy - gh - 8, "B", size=12, bold=True, color=BLU, anchor="middle"))

    # смуга-веселка під віссю H (заливка секторів)
    band_y = gy + 30
    seg = 24
    for i in range(seg):
        h0 = i / seg * 360.0
        r, g, b = chan(h0 + 360.0 / seg / 2)
        col = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
        X = gx + i / seg * gw
        f.append(rect(X, band_y, gw / seg + 0.6, 12, fill=col, stroke="none", sw=0, rx=0))

    # ── колесо праворуч ───────────────────────────────────────────────────────
    wcx, wcy, wr = 810, 250, 95
    import math as _m
    steps = 72
    for i in range(steps):
        a0 = i / steps * 360.0
        a1 = (i + 1) / steps * 360.0
        r, g, b = chan(a0 + 360.0 / steps / 2)
        col = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
        # -90° щоб 0° був угорі; за годинниковою
        ra0 = _m.radians(a0 - 90)
        ra1 = _m.radians(a1 - 90)
        x0, y0 = wcx + wr * _m.cos(ra0), wcy + wr * _m.sin(ra0)
        x1, y1 = wcx + wr * _m.cos(ra1), wcy + wr * _m.sin(ra1)
        f.append('<path d="M%.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f z" '
                 'fill="%s" stroke="%s" stroke-width="0.4"/>'
                 % (wcx, wcy, x0, y0, wr, wr, x1, y1, col, col))
    f.append(circle(wcx, wcy, wr, fill="none", stroke=INK, sw=1.4))
    f.append(circle(wcx, wcy, wr * 0.42, fill=BG, stroke=INK, sw=1.2))
    f.append(text(wcx, wcy - 2, "S,V", size=11, bold=True, color=INK))
    f.append(text(wcx, wcy + 14, "= max", size=9.5, color=MUTED))
    for deg, lab in [(0, "0°/360°"), (120, "120°"), (240, "240°")]:
        ra = _m.radians(deg - 90)
        f.append(text(wcx + (wr + 22) * _m.cos(ra), wcy + (wr + 22) * _m.sin(ra) + 4,
                      lab, size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 490,
                      "На кожному з шести 60°-секторів рівно один канал наростає або спадає, "
                      "а решта тримаються на 0 чи max — тому крок по куту H дає рівномірний обхід веселки.\n"
                      "Це і є формула wheel(): три лінійні пандуси, зсунуті на 120°.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "hsv-wheel.svg"), W, H, *f)


# -- 7. Плавний перехід (fade): інтерполяція A->B по кадрах --------------------
def fig_fade_interp():
    """Як setColor крокує від кольору A до кольору B за N кадрів: три канали
    їдуть кожен своєю прямою від старту до цілі. Лінійна інтерполяція
    r(t)=rA+(rB-rA)*t і кілька проміжних кадрів як реальні відтінки."""
    W, H = 940, 520
    f = [text(W / 2, 30, "Плавний перехід A→B: кожен канал лінійно повзе від старту до цілі за N кадрів",
              size=14.5, bold=True)]

    gx, gy = 110, 400
    gw, gh = 560, 300
    f.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.6))
    f.append(line(gx, gy, gx, gy - gh, color=INK, sw=1.6))
    f.append(text(gx + gw / 2, gy + 54, "крок переходу  t = кадр / N   (0 → 1)", size=11.5, color=INK))
    f.append(text(gx - 68, gy - gh / 2 - 8, "значення", size=11, color=INK))
    f.append(text(gx - 68, gy - gh / 2 + 8, "каналу", size=11, color=INK))

    for v in (0, 64, 128, 192, 255):
        Y = gy - v / 255.0 * gh
        f.append(line(gx - 5, Y, gx, Y, color=INK, sw=1.2))
        f.append(text(gx - 12, Y + 4, str(v), size=9.5, color=MUTED, anchor="end"))
    for t, lab in ((0.0, "0"), (0.25, "¼"), (0.5, "½"), (0.75, "¾"), (1.0, "1")):
        X = gx + t * gw
        f.append(line(X, gy, X, gy + 5, color=INK, sw=1.2))
        f.append(text(X, gy + 22, lab, size=10, color=MUTED))

    A = (255, 90, 0)
    B = (0, 120, 255)
    chans = [("R", RED, A[0], B[0]), ("G", GRN, A[1], B[1]), ("B", BLU, A[2], B[2])]
    for lab, col, a, b in chans:
        x1, y1 = gx, gy - a / 255.0 * gh
        x2, y2 = gx + gw, gy - b / 255.0 * gh
        f.append(line(x1, y1, x2, y2, color=col, sw=2.6))
        f.append(circle(x1, y1, 4, fill=col, stroke=INK, sw=1.2))
        f.append(circle(x2, y2, 4, fill=col, stroke=INK, sw=1.2))
        f.append(text(gx + gw + 14, y2 + 4, lab, size=12, bold=True, color=col, anchor="start"))

    sw_y = gy + 74
    f.append(text(gx, sw_y - 6, "як це виглядає оком:", size=10, color=MUTED, anchor="start"))
    NS = 9
    for i in range(NS):
        t = i / (NS - 1)
        r = int(A[0] + (B[0] - A[0]) * t)
        g = int(A[1] + (B[1] - A[1]) * t)
        b = int(A[2] + (B[2] - A[2]) * t)
        col = "#%02x%02x%02x" % (r, g, b)
        X = gx + t * gw - 20
        f.append(rect(X, sw_y, 40, 22, fill=col, stroke=INK, sw=1.0, rx=4))
    f.append(text(gx - 6, sw_y + 16, "A", size=11, bold=True, color=INK, anchor="end"))
    f.append(text(gx + gw + 6, sw_y + 16, "B", size=11, bold=True, color=INK, anchor="start"))

    b, _, _ = textbox(802, 148,
                      "на кадрі t (0…1):\n"
                      "r = rA + (rB − rA)·t\n"
                      "g = gA + (gB − gA)·t\n"
                      "b = bA + (bB − bA)·t\n"
                      "setColor(r, g, b)",
                      size=11, fill="#eef1f5", stroke=INK)
    f.append(b)

    b, _, _ = textbox(802, 322,
                      "N кадрів × пауза = час\nпереходу. Більше кадрів —\n"
                      "плавніше; менше ніж ~1 крок\nduty на кадр око вже\nне розрізняє.",
                      size=10.5, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "fade-interp.svg"), W, H, *f)


# -- 8. Катод vs анод: та сама яскравість -- дзеркальна шпаруватість на піні ----
def fig_cathode_anode():
    """Одне бажане <світити на 3/4>. Спільний катод: на пін іде duty=191 (3/4 часу +).
    Спільний анод: та сама яскравість -- це duty=64 (3/4 часу -, бо колір вмикає
    низький рівень). Дві PWM-хвилі + прапорець інверсії 255-value."""
    W, H = 940, 480
    f = [text(W / 2, 30, "Спільний катод vs анод: та сама яскравість — дзеркальна шпаруватість на піні",
              size=14.5, bold=True)]

    def pwm_wave(x0, y0, w, high_frac, col):
        out = []
        periods = 3
        pw = w / periods
        amp = 34
        base = y0
        top = y0 - amp
        pts = []
        for k in range(periods):
            xs = x0 + k * pw
            hi = pw * high_frac
            pts.append((xs, base))
            pts.append((xs, top))
            pts.append((xs + hi, top))
            pts.append((xs + hi, base))
            pts.append((xs + pw, base))
        out.append(line(x0, base, x0 + w, base, color="#d0d5db", sw=1.0))
        out.append(line(x0, top, x0 + w, top, color="#d0d5db", sw=1.0))
        out.append(text(x0 - 8, base + 4, "0", size=9, color=MUTED, anchor="end"))
        out.append(text(x0 - 8, top + 4, "+", size=11, bold=True, color=MUTED, anchor="end"))
        poly = " ".join("%.1f,%.1f" % pt for pt in pts)
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, col))
        return out

    b, _, _ = textbox(W / 2, 80, "хочемо однакового: колір горить на ¾ яскравості",
                      size=12, bold=True, fill="#eef7ee", stroke=FIELD)
    f.append(b)

    lx = 120
    f.append(text(lx + 150, 132, "спільний КАТОД  (−  на GND)", size=12.5, bold=True, color=NEG))
    f.append(text(lx + 150, 152, "колір вмикає «+» на піні", size=10.5, color=MUTED))
    f.extend(pwm_wave(lx, 250, 300, 0.75, NEG))
    f.append(text(lx + 150, 284, "пін «+» три чверті часу", size=10, color=INK))
    b, _, _ = textbox(lx + 150, 336, "duty = 191  (¾ від 255)\nanalogWrite(pin, 191)",
                      size=11, fill=BG, stroke=INK)
    f.append(b)

    rx = 560
    f.append(text(rx + 150, 132, "спільний АНОД  (+  на VCC)", size=12.5, bold=True, color=POS))
    f.append(text(rx + 150, 152, "колір вмикає «−» (низький рівень)", size=10.5, color=MUTED))
    f.extend(pwm_wave(rx, 250, 300, 0.25, POS))
    f.append(text(rx + 150, 284, "пін «+» лише чверть часу", size=10, color=INK))
    b, _, _ = textbox(rx + 150, 336, "duty = 64  (= 255 − 191)\nanalogWrite(pin, 255 − 191)",
                      size=11, fill=BG, stroke=INK)
    f.append(b)

    f.append(arrow(lx + 300 + 12, 250 - 17, rx - 12, 250 - 17, color=INK, sw=2.0))
    b, _, _ = textbox(W / 2, 215, "прапорець common_anode → 255 − value",
                      size=11, bold=True, fill="#fff8e6", stroke=FIELD)
    f.append(b)

    b, _, _ = textbox(W / 2, 440,
                      "Яскравість каналу однакова — а число, що йде в analogWrite, протилежне. "
                      "Один прапорець (255 − value для анода) обслуговує обидві плати тим самим setColor.",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "cathode-anode.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ky016_schematic()
    fig_ky016_wiring()
    fig_color_mixing()
    fig_rgb_cube()
    fig_gamma()
    fig_hsv_wheel()
    fig_fade_interp()
    fig_cathode_anode()
    print("KY-016 figs done ->", IMG)
