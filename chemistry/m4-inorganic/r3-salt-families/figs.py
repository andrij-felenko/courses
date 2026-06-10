# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.3 — «Оксиди, солі та карта неорганіки» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; заряд «+» червоний, «−» синій;
O червона, метали сіро-фіолетові; усі підписи українською.
Спільні хелпери скопійовані (розділи не діляться файлами).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED    = "#c0271e"
BLUE   = "#1f47b5"
GREEN  = "#1f8a3b"
INK    = "#1b1b1b"
GREY   = "#8a8a8a"
FAINT  = "#e9e9e9"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
MET_FILL = "#8a7fae"
RUST   = "#a6552f"
SAND   = "#d8b25a"
H_FILL = "#ffffff"
H_LINE = "#9a9a9a"
CL_FILL = "#3f9e54"
WATER  = "#cfe6f5"
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=1.6):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(points, color=INK, w=2, fill="none"):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<path d="{d} Z" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round"/>\n')


def ball(cx, cy, r, fill, stroke, label=None, lsize=12, lcolor="#ffffff"):
    s = circle(cx, cy, r, fill, stroke, 1.8)
    if label:
        s += text(cx, cy + lsize * 0.36, label, lsize, lcolor, "middle", "bold")
    return s


def plus(cx, cy, size=6, color=RED, w=2.4):
    return (line(cx - size, cy, cx + size, cy, color, w)
            + line(cx, cy - size, cx, cy + size, color, w))


def minus(cx, cy, size=6, color=BLUE, w=2.4):
    return line(cx - size, cy, cx + size, cy, color, w)


def h_plus(cx, cy, r=9):
    return ball(cx, cy, r, H_FILL, H_LINE, "H", 12, INK) + text(cx + r + 1, cy - r + 3, "+", 12, RED, "start", "bold")


def oh_minus(cx, cy, scale=1.0):
    ro, rh = 12 * scale, 7 * scale
    hx, hy = cx + 15 * scale, cy - 9 * scale
    s = line(cx, cy, hx, hy, H_LINE, 2.5)
    s += ball(cx, cy, ro, O_FILL, O_LINE, "O", 12 * scale, "#fff")
    s += ball(hx, hy, rh, H_FILL, H_LINE)
    s += text(cx - ro - 2, cy + 4, "−", 14 * scale, BLUE, "middle", "bold")
    return s


def watermol(cx, cy, scale=1.0):
    ro, rh, b = 12 * scale, 7 * scale, 20 * scale
    a, half = math.radians(90), math.radians(53)
    h1 = (cx + b * math.cos(a - half), cy + b * math.sin(a - half))
    h2 = (cx + b * math.cos(a + half), cy + b * math.sin(a + half))
    s = line(cx, cy, h1[0], h1[1], H_LINE, 3) + line(cx, cy, h2[0], h2[1], H_LINE, 3)
    s += ball(cx, cy, ro, O_FILL, O_LINE, "O", 12 * scale, "#fff")
    s += ball(h1[0], h1[1], rh, H_FILL, H_LINE) + ball(h2[0], h2[1], rh, H_FILL, H_LINE)
    return s


def _beaker(x, y, w, h, rb=16):
    return (f'<path d="M{x:.1f},{y:.1f} L{x:.1f},{y + h - rb:.1f} '
            f'Q{x:.1f},{y + h:.1f} {x + rb:.1f},{y + h:.1f} '
            f'L{x + w - rb:.1f},{y + h:.1f} Q{x + w:.1f},{y + h:.1f} {x + w:.1f},{y + h - rb:.1f} '
            f'L{x + w:.1f},{y:.1f}" fill="none" stroke="{INK}" stroke-width="2.4"/>\n')


def _liquid(x, y, w, h, fill, rb=16):
    return (f'<path d="M{x:.1f},{y:.1f} L{x:.1f},{y + h - rb:.1f} '
            f'Q{x:.1f},{y + h:.1f} {x + rb:.1f},{y + h:.1f} '
            f'L{x + w - rb:.1f},{y + h:.1f} Q{x + w:.1f},{y + h:.1f} {x + w:.1f},{y + h - rb:.1f} '
            f'L{x + w:.1f},{y:.1f} Z" fill="{fill}" stroke="none"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── іконки оксидів ───────────────────────────────────────────────────────────
def ic_rust(cx, cy):
    s = ""
    for dx, dy, r, c in [(-14, 2, 13, "#8a3f22"), (6, -6, 12, RUST), (12, 8, 11, "#c06a3a"),
                         (-4, 12, 9, "#8a3f22"), (0, 0, 10, "#b65c33")]:
        s += circle(cx + dx, cy + dy, r, c, "none", 0)
    return s


def ic_gas(cx, cy, label):
    s = ""
    for dx, dy, r in [(-16, 4, 16), (0, -8, 18), (16, 4, 16), (0, 8, 16)]:
        s += circle(cx + dx, cy + dy, r, "#e2eaf0", "#bcc8d2", 1.4)
    s += text(cx, cy + 5, label, 13, "#5b6b78", "middle", "bold")
    return s


def ic_lump(cx, cy, fill, oc, label=None):
    s = poly([(cx - 20, cy + 6), (cx - 14, cy - 12), (cx + 4, cy - 16),
              (cx + 20, cy - 4), (cx + 16, cy + 14), (cx - 8, cy + 16)], oc, 1.6, fill)
    if label:
        s += text(cx, cy + 4, label, 12, INK, "middle", "bold")
    return s


def ic_sand(cx, cy):
    s = ""
    pts = [(-16, 8), (-8, -2), (0, 6), (8, -4), (16, 6), (-12, 14),
           (4, 14), (12, 14), (-4, 2), (0, 14)]
    for dx, dy in pts:
        s += circle(cx + dx, cy + dy, 3.6, SAND, "#a98a3f", 1)
    return s


def cloud(cx, cy):
    s = ""
    for dx, dy, r in [(-34, 4, 20), (-12, -8, 24), (16, -6, 22), (34, 6, 18), (0, 10, 22)]:
        s += circle(cx + dx, cy + dy, r, "#dbe3ea", "#b4c0c9", 1.4)
    s += rect(cx - 50, cy + 8, 100, 14, "#dbe3ea", "none", 0)
    return s


# ── Рис. 4.3.1-1 — кисень обіймає все → оксиди ───────────────────────────────
def fig_oxides():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 32, "Кисень обіймає майже все — і виходить оксид", 21, INK, "middle", "bold")
    s += text(W / 2, 54, "залізо, вуглець, кальцій, силіцій — речовини різні, а хід один: щось + кисень",
              12.5, GREY, "middle", style="italic")

    # центр — кисень
    s += circle(424, 240, 22, O_FILL, O_LINE, 1.8)
    s += circle(456, 240, 22, O_FILL, O_LINE, 1.8)
    s += text(440, 245, "O₂", 16, "#fff", "middle", "bold")
    s += text(440, 292, "кисень", 14, INK, "middle", "bold")

    spokes = [(170, 150, "залізо → іржа", "rust"),
              (710, 150, "вуглець → CO₂", "gas"),
              (170, 330, "кальцій → вапно", "lump"),
              (710, 330, "силіцій → пісок", "sand")]
    for px, py, label, kind in spokes:
        ex = 420 if px < 440 else 460
        ey = 222 if py < 240 else 258
        s += arrow(ex + (px - ex) * 0.12, ey + (py - ey) * 0.12,
                   px + (440 - px) * 0.14, py + (240 - py) * 0.06, INK, 2.2)
        if kind == "rust":
            s += ic_rust(px, py)
        elif kind == "gas":
            s += ic_gas(px, py, "CO₂")
        elif kind == "lump":
            s += ic_lump(px, py, "#eef0ef", "#b7bdc2", "CaO")
        else:
            s += ic_sand(px, py)
        s += text(px, py + 44, label, 13.5, INK, "middle", "bold")
    s += text(W / 2, 420, "усе це — оксиди: елемент, що обійняв Оксиген", 13, GREEN, "middle", "bold")
    save("fig-4-3-1-1-oxides.svg", s)


# ── Рис. 4.3.1-2 — оксид у воді обирає табір (+ кислий дощ) ───────────────────
def fig_oxide_split():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Оксид у воді обирає табір — і чому дощ кислуватий", 20, INK, "middle", "bold")

    # ліва панель — метал → основа
    s += rect(36, 64, 384, 336, "#eef3fb", "#cfdcef", 1.5, 14)
    s += text(228, 92, "ОКСИД МЕТАЛУ", 15, BLUE, "middle", "bold")
    s += ic_lump(132, 150, MET_FILL, "#6f6394")
    s += text(132, 182, "вапно (CaO)", 12, INK, "middle", "bold")
    s += text(300, 150, "+ вода", 14, INK, "middle", "bold")
    s += arrow(228, 198, 228, 244, BLUE, 2.6)
    s += rect(96, 250, 264, 50, "#e2ebfb", BLUE, 1.6, 10)
    s += text(228, 281, "OH⁻  →  ОСНОВА (луг)", 15, BLUE, "middle", "bold")
    s += text(228, 340, "метал через кисень веде до лугу", 12, "#3a4f93", "middle", style="italic")

    # права панель — неметал → кислота (+ дощ)
    s += rect(460, 64, 384, 336, "#fdeef0", "#f1d6d6", 1.5, 14)
    s += text(652, 92, "ОКСИД НЕМЕТАЛУ", 15, RED, "middle", "bold")
    s += ic_gas(560, 150, "CO₂")
    s += text(730, 150, "+ вода", 14, INK, "middle", "bold")
    s += arrow(652, 198, 652, 226, RED, 2.6)
    s += rect(520, 232, 264, 44, "#fbe2e5", RED, 1.6, 10)
    s += text(652, 260, "H⁺  →  КИСЛОТА", 15, RED, "middle", "bold")
    # дощ
    s += cloud(652, 312)
    for dx in (-30, -10, 10, 30, 0, -20, 20):
        s += line(652 + dx, 332, 652 + dx - 3, 348, BLUE, 2)
    s += text(652, 372, "навіть чистий дощ ≈ pH 5,5", 12.5, "#9b4b45", "middle", "bold")

    s += line(440, 80, 440, 392, GREY, 1.2, dash="4 4")
    s += text(W / 2, H - 16,
              "оксиди — батьки обох таборів: метал дає основу, неметал — кислоту",
              12.5, GREY, "middle", style="italic")
    save("fig-4-3-1-2-oxide-split.svg", s)


# ── Рис. 4.3.2-1 — нейтралізація: кислота + основа → сіль + вода ──────────────
def fig_neutralize():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 30, "Нейтралізація: дві їдкі речовини → сіль і вода", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "H⁺ і OH⁻ гаснуть у воду, а партнери Na⁺ і Cl⁻ лишаються й стають сіллю",
              12.5, GREY, "middle", style="italic")

    # ліва склянка — кислота + основа разом
    s += text(180, 92, "кислота + основа разом", 13.5, INK, "middle", "bold")
    s += _liquid(60, 104, 240, 210, WATER)
    s += h_plus(118, 168)
    s += ball(186, 156, 14, CL_FILL, "#2c7a40")
    s += minus(186, 156, 5, BLUE)
    s += text(210, 150, "Cl⁻", 11.5, INK, "start", "bold")
    s += ball(120, 250, 15, MET_FILL, "#6f6394")
    s += plus(120, 250, 5, RED)
    s += text(96, 248, "Na⁺", 11.5, INK, "end", "bold")
    s += oh_minus(196, 250, 0.95)
    s += _beaker(60, 104, 240, 210)

    # центр — стрілка + рівняння
    s += arrow(316, 200, 556, 200, INK, 3)
    s += text(436, 184, "нейтралізація", 13.5, GREEN, "middle", "bold")
    s += text(436, 224, "H⁺ + OH⁻ → H₂O", 13, BLUE, "middle", "bold")
    s += text(436, 244, "Na⁺ + Cl⁻ → сіль", 13, RED, "middle", "bold")

    # права склянка — сіль + вода
    s += text(700, 92, "сіль + вода", 13.5, INK, "middle", "bold")
    s += _liquid(580, 104, 240, 210, WATER)
    s += watermol(660, 168, 1.0)
    s += text(660, 210, "вода", 11.5, INK, "middle")
    s += ball(694, 256, 15, MET_FILL, "#6f6394")
    s += plus(694, 256, 5, RED)
    s += ball(722, 256, 14, CL_FILL, "#2c7a40")
    s += minus(722, 256, 5, BLUE)
    s += text(708, 292, "кухонна сіль", 11.5, INK, "middle", "bold")
    s += _beaker(580, 104, 240, 210)

    s += text(W / 2, 404, "дві речовини, якими лякають, разом — те, чим солять суп",
              12.5, GREY, "middle", style="italic")
    save("fig-4-3-2-1-neutralize.svg", s)


# ── Рис. 4.3.2-2 — сода + оцет: газ виходить, лишається солона вода ───────────
def fig_soda_vinegar():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 32, "Сода + оцет: куди зникли обидва?", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "шипіння — це газ, що виходить; кисле й лужне знищили одне одного",
              12.5, GREY, "middle", style="italic")

    bx, by, bw, bh = 280, 150, 200, 210
    # вливання
    s += text(380, 96, "сода + оцет", 14, INK, "middle", "bold")
    s += arrow(380, 104, 380, 132, INK, 2.2)
    # рідина
    s += _liquid(bx, by + 40, bw, bh - 40, WATER)
    # бульбашки в рідині
    bubbles = [(40, 150), (75, 120), (120, 160), (150, 110), (95, 175), (60, 90),
               (135, 135), (110, 95), (45, 120), (160, 150)]
    for dx, dy in bubbles:
        s += circle(bx + dx, by + dy, 5.5, "#eaf6fb", "#bcd6e6", 1.2)
    # піна над вінцями
    foam = [(-10, 38), (10, 30), (35, 36), (60, 28), (90, 36), (120, 30),
            (150, 36), (175, 32), (200, 40), (25, 22), (75, 20), (130, 20), (180, 24)]
    for dx, dy in foam:
        s += circle(bx + dx, by + dy, 13, "#f1f8fc", "#cfe0ec", 1.4)
    # газ угору
    for dx in (40, 100, 160):
        s += arrow(bx + dx, by + 8, bx + dx, by - 28, "#7aa0b5", 2)
    s += text(bx + bw / 2, by - 36, "CO₂ ↑", 14, "#5b7d90", "middle", "bold")
    s += _beaker(bx, by, bw, bh)

    s += text(W / 2, by + bh + 30, "оцет + сода  →  сіль + вода + CO₂↑", 15, INK, "middle", "bold")
    s += text(W / 2, by + bh + 52, "гострий запах оцту й сода зникли — стали сіллю у воді",
              12.5, GREY, "middle", style="italic")
    save("fig-4-3-2-2-soda-vinegar.svg", s)


def box(cx, top, w, h, title, example, fill, border, tcol=INK):
    s = rect(cx - w / 2, top, w, h, fill, border, 1.8, 12)
    s += text(cx, top + 24, title, 14.5, tcol, "middle", "bold")
    if example:
        s += text(cx, top + 44, example, 11.5, GREY, "middle", style="italic")
    return s


def chip(cx, cy, w, h, label, fill, border, tcol=INK):
    s = rect(cx - w / 2, cy - h / 2, w, h, fill, border, 1.8, 10)
    s += text(cx, cy + 5, label, 13, tcol, "middle", "bold")
    return s


# ── Рис. 4.3.3-1 — карта неорганіки ──────────────────────────────────────────
def fig_map():
    W, H = 900, 490
    s = header(W, H)
    s += text(W / 2, 30, "Карта неорганіки: дві дзеркальні сходи, що сходяться на солі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "кожна стрілка — знайома реакція; шкільні «ланцюжки» — просто маршрути нею",
              12.5, GREY, "middle", style="italic")

    LX, RX, bw, bh = 230, 670, 220, 60
    tops = [104, 196, 288]
    LT, LB = "#eef3fb", "#9fb6e0"
    RT, RB = "#fdeef0", "#e0a9a9"

    s += text(LX, 88, "МЕТАЛИ → ОСНОВИ", 13, BLUE, "middle", "bold")
    s += text(RX, 88, "НЕМЕТАЛИ → КИСЛОТИ", 13, RED, "middle", "bold")

    s += box(LX, tops[0], bw, bh, "метал", "кальцій", LT, LB, BLUE)
    s += box(LX, tops[1], bw, bh, "основний оксид", "вапно · CaO", LT, LB, BLUE)
    s += box(LX, tops[2], bw, bh, "основа", "гашене вапно · Ca(OH)₂", LT, LB, BLUE)
    s += box(RX, tops[0], bw, bh, "неметал", "вуглець", RT, RB, RED)
    s += box(RX, tops[1], bw, bh, "кислотний оксид", "CO₂", RT, RB, RED)
    s += box(RX, tops[2], bw, bh, "кислота", "вугільна кислота", RT, RB, RED)

    for top in tops[:2]:
        s += arrow(LX, top + bh, LX, top + 92, INK, 2.2)
        s += arrow(RX, top + bh, RX, top + 92, INK, 2.2)
    s += text(LX + 16, tops[0] + bh + 22, "+ кисень", 12, INK, "start", "bold")
    s += text(LX + 16, tops[1] + bh + 22, "+ вода", 12, INK, "start", "bold")
    s += text(RX + 16, tops[0] + bh + 22, "+ кисень", 12, INK, "start", "bold")
    s += text(RX + 16, tops[1] + bh + 22, "+ вода", 12, INK, "start", "bold")

    # сіль внизу
    salt_top = 400
    s += box(450, salt_top, 280, 66, "СІЛЬ  ( + вода )", "крейда · кухонна сіль", "#eef7ef", GREEN, GREEN)
    s += arrow(LX, tops[2] + bh, 410, salt_top + 4, INK, 2.4)
    s += arrow(RX, tops[2] + bh, 490, salt_top + 4, INK, 2.4)
    s += text(450, 378, "кислота + основа → нейтралізація", 12.5, GREEN, "middle", "bold")
    save("fig-4-3-3-1-map.svg", s)


# ── Рис. 4.3.3-2 — ланцюжок як маршрут ───────────────────────────────────────
def fig_route():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 30, "«Ланцюжок перетворень» — це маршрут картою", 20, INK, "middle", "bold")

    cxs = [110, 320, 530, 740]
    LT, LB = "#eef3fb", "#9fb6e0"
    RT, RB = "#fdeef0", "#e0a9a9"

    def route(cy, chips, labels, fill, border, tcol, tag, tagcol):
        out = text(60, cy - 38, tag, 12.5, tagcol, "start", "bold")
        for i, c in enumerate(chips):
            out += chip(cxs[i], cy, 160, 46, c, fill, border, tcol)
        for i in range(3):
            x1, x2 = cxs[i] + 80, cxs[i + 1] - 80
            out += arrow(x1, cy, x2, cy, INK, 2.2)
            out += text((x1 + x2) / 2, cy - 12, labels[i], 11, INK, "middle", "bold")
        return out

    s += route(120, ["кальцій", "вапно · CaO", "гашене вапно", "сіль · CaCl₂"],
               ["+ кисень", "+ вода", "+ кислота"], LT, LB, BLUE, "ліві сходи (метал)", BLUE)
    s += route(225, ["сірка", "сірчистий газ · SO₂", "сірчиста кислота", "сіль"],
               ["+ кисень", "+ вода", "+ луг"], RT, RB, RED, "праві сходи (неметал)", RED)

    s += text(W / 2, 292, "ті самі три кроки — лівими чи правими сходами; бачиш карту — не зубриш",
              12.5, GREY, "middle", style="italic")
    save("fig-4-3-3-2-route.svg", s)


if __name__ == "__main__":
    fig_oxides()
    fig_oxide_split()
    fig_neutralize()
    fig_soda_vinegar()
    fig_map()
    fig_route()
