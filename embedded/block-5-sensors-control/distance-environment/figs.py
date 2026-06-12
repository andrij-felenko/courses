# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 29 — «Вимірювання відстані й оточення» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле/хвилі зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N); для історії до розділу — секція 0 (Рис. 29.0.N).
Спільні допоміжні функції скопійовано зі стилю Розділу 28.
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
HOT   = "#e8702a"
WATER = "#2b6ea3"
WATERF = "#dceaf5"
STEEL = "#6f7e8c"
GOLD  = "#caa24a"
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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
    if weight == "italic":
        weight, style = "normal", "italic"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def dot(cx, cy, r=5, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def polygon(pts, fill=INK, stroke="none", sw=1):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("  saved", name)


# ── історичні помічники: хвилі, кажан, корабель, субмарина ───────────────────

def swaves(cx, cy, direction=0, n=3, r0=16, dr=15, color=GREEN, spread=46, w=1.8, dash=None):
    """Концентричні дуги-хвилі, що відкриваються в напрямку `direction` (градуси)."""
    s = ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    for i in range(n):
        r = r0 + i * dr
        a0 = math.radians(direction - spread)
        a1 = math.radians(direction + spread)
        x0 = cx + r * math.cos(a0)
        y0 = cy + r * math.sin(a0)
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)
        s += (f'<path d="M {x0:.1f},{y0:.1f} A {r:.1f},{r:.1f} 0 0 1 {x1:.1f},{y1:.1f}" '
              f'fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n')
    return s


def bat(cx, cy, sc=1.0, color=INK):
    body = f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{4*sc:.1f}" ry="{8*sc:.1f}" fill="{color}"/>\n'
    lw = polygon([(cx - 3 * sc, cy - 4 * sc), (cx - 26 * sc, cy - 11 * sc),
                  (cx - 18 * sc, cy), (cx - 26 * sc, cy + 8 * sc),
                  (cx - 3 * sc, cy + 3 * sc)], fill=color)
    rw = polygon([(cx + 3 * sc, cy - 4 * sc), (cx + 26 * sc, cy - 11 * sc),
                  (cx + 18 * sc, cy), (cx + 26 * sc, cy + 8 * sc),
                  (cx + 3 * sc, cy + 3 * sc)], fill=color)
    ears = (polygon([(cx - 2 * sc, cy - 8 * sc), (cx - 4 * sc, cy - 13 * sc), (cx, cy - 9 * sc)], fill=color)
            + polygon([(cx + 2 * sc, cy - 8 * sc), (cx + 4 * sc, cy - 13 * sc), (cx, cy - 9 * sc)], fill=color))
    return lw + rw + body + ears


def ship(cx, cy, sc=1.0, color=STEEL):
    hull = polygon([(cx - 46 * sc, cy), (cx + 46 * sc, cy), (cx + 34 * sc, cy + 16 * sc),
                    (cx - 34 * sc, cy + 16 * sc)], fill=color)
    deck = rect(cx - 16 * sc, cy - 18 * sc, 32 * sc, 18 * sc, fill="#9aa6b2", stroke=color, sw=1)
    funnel = rect(cx - 4 * sc, cy - 30 * sc, 10 * sc, 14 * sc, fill=color, stroke="none")
    return hull + deck + funnel


def submarine(cx, cy, sc=1.0, color=STEEL):
    body = f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{40*sc:.1f}" ry="{12*sc:.1f}" fill="{color}"/>\n'
    tower = rect(cx - 6 * sc, cy - 22 * sc, 14 * sc, 12 * sc, fill=color, stroke="none")
    peri = line(cx + 2 * sc, cy - 22 * sc, cx + 2 * sc, cy - 30 * sc, color, 2)
    return body + tower + peri


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 29 — від кажанів до сонара (секція 0)
# ════════════════════════════════════════════════════════════════════════════

def fig_spallanzani():
    """Рис. 29.0.1 — осліплений кажан літає, оглухлий врізається."""
    w, h = 700, 330
    s = header(w, h)
    s += text(w / 2, 28, "Дослід Спалланцані: кажан орієнтується вухами, а не очима",
              15, INK, "middle", "bold")
    for k, (title, ok) in enumerate([("осліплений — літає", True), ("оглухлий — врізається", False)]):
        x0 = 30 + k * 350
        s += rect(x0, 50, 320, 250, fill="#fbfbfb", stroke=(GREEN if ok else RED), sw=1.5, rx=8)
        s += text(x0 + 160, 72, title, 13, (GREEN if ok else RED), "middle", "bold")
        # перешкоди (стовпи)
        for px in (x0 + 90, x0 + 200, x0 + 270):
            s += line(px, 110, px, 270, GREY, 4)
        if ok:
            # звивистий шлях, що оминає
            s += poly([(x0 + 30, 160), (x0 + 70, 140), (x0 + 110, 175), (x0 + 160, 150),
                       (x0 + 230, 180), (x0 + 290, 150)], GREEN, 2.2, dash="2,3")
            s += bat(x0 + 70, 140, 1.0, INK)
            # очі закреслені
            s += text(x0 + 70, 118, "✕ очі", 10, RED, "middle", "bold")
            s += text(x0 + 160, 230, "вуха чують відлуння → оминає", 10.5, GREEN, "middle", "italic")
        else:
            # прямий шлях у стовп
            s += poly([(x0 + 30, 160), (x0 + 86, 160)], RED, 2.2, dash="2,3")
            s += bat(x0 + 70, 160, 1.0, INK)
            s += text(x0 + 95, 150, "✕ вуха", 10, RED, "middle", "bold")
            # «зірка» удару об стовп
            s += text(x0 + 90, 140, "✸", 20, RED, "middle", "bold")
            s += text(x0 + 160, 230, "без слуху — наосліп у перешкоду", 10.5, RED, "middle", "italic")
    s += text(w / 2, 320, "1790-ті: факт є, а механізм («беззвучний» крик) лишився загадкою на 150 років",
              11, GREY, "middle", "italic")
    save("fig-29-0-1-spallanzani.svg", s)


def fig_echo_ranging():
    """Рис. 29.0.2 — принцип ехолокації: d = v·t/2."""
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 28, "Принцип відлуння: відстань зі швидкості й часу",
              15, INK, "middle", "bold")
    ex, ey = 90, 150
    tx = 560
    # випромінювач
    s += rect(50, 128, 40, 44, fill="#eef6ef", stroke=GREEN, sw=1.6, rx=4)
    s += text(70, 200, "джерело", 10.5, INK, "middle", "bold")
    # ціль (стіна)
    s += rect(tx, 90, 20, 120, fill="#eee", stroke=INK, sw=1.5)
    s += text(tx + 10, 228, "ціль", 10.5, INK, "middle", "bold")
    # імпульс туди
    s += swaves(ex + 8, ey, 0, 3, 18, 16, GREEN, 40)
    s += arrow(150, 122, 520, 122, GREEN, 2.2)
    s += text(330, 112, "імпульс  →  (час t/2)", 11, GREEN, "middle", "bold")
    # відлуння назад
    s += swaves(tx - 4, ey, 180, 3, 18, 16, BLUE, 40)
    s += arrow(520, 178, 150, 178, BLUE, 2.2)
    s += text(330, 196, "відлуння  ←  (час t/2)", 11, BLUE, "middle", "bold")
    # відстань
    s += line(70, 250, tx + 10, 250, INK, 1.4)
    s += line(70, 244, 70, 256, INK, 1.4)
    s += line(tx + 10, 244, tx + 10, 256, INK, 1.4)
    s += text((70 + tx) / 2, 268, "відстань d", 11.5, INK, "middle", "bold")
    s += text(w / 2, 292, "повний шлях = 2d → d = v · t / 2   (v — швидкість хвилі)",
              13, INK, "middle", "bold")
    save("fig-29-0-2-echo-ranging.svg", s)


def fig_langevin_sonar():
    """Рис. 29.0.3 — сонар Ланжевена: п'єзокварц, імпульс, відлуння від субмарини."""
    w, h = 700, 360
    s = header(w, h)
    s += text(w / 2, 26, "Сонар Ланжевена (1917): п'єзокварц шле ультразвук, ловить відлуння",
              13.5, INK, "middle", "bold")
    sea = 90
    s += rect(0, sea, w, h - sea, fill=WATERF, stroke="none")
    s += line(0, sea, w, sea, WATER, 2)
    # хвилі моря
    s += poly([(x, sea + 4 * math.sin(x / 26)) for x in range(0, w, 6)], WATER, 1.2)
    # корабель
    s += ship(180, sea, 1.1, STEEL)
    # п'єзо-перетворювач під кораблем
    s += rect(166, sea + 6, 28, 14, fill=GOLD, stroke="#9a7a1e", sw=1.4, rx=2)
    s += text(180, sea + 40, "п'єзокварц", 10.5, "#9a7a1e", "middle", "bold")
    s += text(180, sea + 54, "(ефект Кюрі, §28.3)", 9.5, GREY, "middle", "italic")
    # імпульс униз-вправо до субмарини
    sub_x, sub_y = 520, 250
    s += swaves(190, sea + 22, 35, 3, 20, 16, GREEN, 30)
    s += arrow(210, sea + 34, sub_x - 50, sub_y - 16, GREEN, 2.2)
    s += text(330, 175, "імпульс ультразвуку", 10.5, GREEN, "middle", "bold")
    # субмарина
    s += submarine(sub_x, sub_y, 1.0, STEEL)
    s += text(sub_x, sub_y + 28, "субмарина", 10.5, INK, "middle", "bold")
    # відлуння назад
    s += swaves(sub_x - 40, sub_y, 200, 3, 16, 14, BLUE, 30)
    s += arrow(sub_x - 60, sub_y - 8, 215, sea + 44, BLUE, 2.2)
    s += text(360, 300, "відлуння ← час → дальність (d = v·t/2, v ≈ 1500 м/с у воді)",
              11.5, BLUE, "middle", "bold")
    save("fig-29-0-3-langevin-sonar.svg", s)


def fig_timeline():
    """Рис. 29.0.4 — ланцюг: природа → Спалланцані → Фессенден → Ланжевен → давач."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 28, "Ланцюг відлуння: від кажанів до ультразвукового давача",
              15, INK, "middle", "bold")
    y = 130
    s += line(40, y, 680, y, INK, 2)
    items = [
        ("природа", "кажани — ехолокація", GREEN, -1),
        ("1790-ті", "Спалланцані: загадка", INK, 1),
        ("1914", "Фессенден: айсберг", WATER, -1),
        ("1917", "Ланжевен: сонар (п'єзо)", "#9a7a1e", 1),
        ("1944", "Гріффін: «ехолокація»", GREEN, -1),
        ("сьогодні", "давач trigger/echo", BLUE, 1),
    ]
    xs = [70, 190, 320, 450, 575, 680]
    for (yr, lbl, col, side), x in zip(items, xs):
        s += dot(x, y, 6, col)
        ly = y - 42 if side < 0 else y + 30
        s += text(x, ly, yr, 12, col, "middle", "bold")
        s += text(x, ly + (16 if side < 0 else 16), lbl, 9.5, INK, "middle")
        s += line(x, y, x, ly + (24 if side < 0 else -10), col, 1, dash="2,2")
    s += text(w / 2, 228, "природа винайшла перша; ми наздоганяли 150 років, а втілили за роки війни",
              11, GREY, "middle", "italic")
    save("fig-29-0-4-timeline.svg", s)


def clock(cx, cy, r=12, color=INK):
    return (circle(cx, cy, r, "#fff", color, 1.6)
            + line(cx, cy, cx, cy - r * 0.6, color, 1.4)
            + line(cx, cy, cx + r * 0.45, cy, color, 1.4))


def burst(x0, y0, w, amp, cycles=8, color=GREEN, sw=1.6):
    pts = []
    N = cycles * 8
    for i in range(N + 1):
        t = i / N
        env = math.sin(math.pi * t)
        pts.append((x0 + w * t, y0 - amp * env * math.sin(2 * math.pi * cycles * t)))
    return poly(pts, color, sw)


def cone(ax, ay, length, half_deg, direction=0, color=GREEN, sw=1.5, dash="5,4"):
    out = ""
    d = math.radians(direction)
    a = math.radians(half_deg)
    for sgn in (+1, -1):
        ang = d + sgn * a
        out += line(ax, ay, ax + length * math.cos(ang), ay + length * math.sin(ang),
                    color, sw, dash=dash)
    # дуга на кінці
    x1 = ax + length * math.cos(d - a)
    y1 = ay + length * math.sin(d - a)
    x2 = ax + length * math.cos(d + a)
    y2 = ay + length * math.sin(d + a)
    out += (f'<path d="M {x1:.1f},{y1:.1f} A {length:.1f},{length:.1f} 0 0 1 {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-dasharray="{dash}"/>\n')
    return out


def transducer(cx, cy, w=26, h=40, color=GREEN):
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#eef6ef", stroke=color, sw=1.6, rx=3)
            + line(cx - w / 2 + 4, cy, cx + w / 2 - 4, cy, color, 1.2))


def _pt(x0, y0, w, ht, xv, uv):
    return (x0 + xv * w, y0 - uv * ht)


def _plot_path(x0, y0, w, ht, pts_norm, color, sw=2.4, dash=None):
    return poly([_pt(x0, y0, w, ht, xv, uv) for (xv, uv) in pts_norm], color, sw, dash=dash)


def axes(x0, y0, w, ht, color=INK):
    return arrow(x0, y0, x0, y0 - ht, color, 1.6) + arrow(x0, y0, x0 + w, y0, color, 1.6)


# ════════════════════════════════════════════════════════════════════════════
#  §29.1 Як виміряти відстань без дотику
# ════════════════════════════════════════════════════════════════════════════

def fig_methods():
    w, h = 720, 256
    s = header(w, h)
    s += text(w / 2, 26, "Три способи перетворити відстань на сигнал",
              15.5, INK, "middle", "bold")
    px = [18, 258, 498]
    pw, py, ph = 204, 50, 184
    titles = ["час польоту", "тріангуляція", "яскравість відбиття"]
    subs = ["час → відстань", "кут → відстань", "сила відлуння → відстань"]
    cols = [GREEN, BLUE, GOLD]
    for i in range(3):
        x = px[i]
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=cols[i], sw=1.5, rx=8)
        s += text(x + pw / 2, py + 22, titles[i], 13, cols[i], "middle", "bold")
        s += text(x + pw / 2, py + ph - 12, subs[i], 11, INK, "middle", "italic")
        cy = py + 112
        em = x + 24
        tg = x + pw - 30
        if i == 0:      # ToF
            s += rect(x + 14, cy - 14, 18, 28, fill="#eef6ef", stroke=GREEN, sw=1.4)
            s += rect(tg, cy - 24, 14, 48, fill="#eee", stroke=INK, sw=1.3)
            s += swaves(x + 34, cy, 0, 2, 14, 13, GREEN, 38)
            s += arrow(x + 50, cy - 8, tg - 4, cy - 8, GREEN, 1.8)
            s += arrow(tg - 4, cy + 10, x + 50, cy + 10, BLUE, 1.8)
            s += clock(x + pw / 2, py + 150, 11, INK)
        elif i == 1:    # triangulation
            s += rect(x + 14, cy + 10, 16, 22, fill="#eef4fb", stroke=BLUE, sw=1.4)
            s += rect(x + 14, cy - 30, 10, 26, fill="#fff", stroke=INK, sw=1.2)  # detector strip
            s += rect(tg - 4, cy - 18, 12, 36, fill="#eee", stroke=INK, sw=1.3)
            s += arrow(x + 30, cy + 16, tg - 6, cy - 6, BLUE, 1.8)   # out
            s += arrow(tg - 6, cy - 6, x + 24, cy - 18, RED, 1.8)    # back at angle
            s += text(x + pw / 2, py + 150, "кут θ", 11, RED, "middle", "bold")
        else:           # intensity
            s += rect(x + 14, cy - 12, 18, 24, fill="#fbf3e2", stroke=GOLD, sw=1.4)
            s += rect(tg, cy - 22, 14, 44, fill="#eee", stroke=INK, sw=1.3)
            s += arrow(x + 34, cy, tg - 4, cy, GOLD, 1.8)
            s += line(tg - 4, cy + 8, x + 36, cy + 8, "#d9b25a", 5)   # товсте = яскраво
            s += text(x + pw / 2, py + 150, "ближче → яскравіше", 10, GOLD, "middle", "bold")
    save("fig-29-1-1-methods.svg", s)


def fig_tof_timescale():
    w, h = 700, 290
    s = header(w, h)
    s += text(w / 2, 26, "Час польоту: звук дає мілісекунди, світло — наносекунди",
              14.5, INK, "middle", "bold")
    # схема d=vt/2
    s += rect(60, 70, 26, 40, fill="#eef6ef", stroke=GREEN, sw=1.5)
    s += text(73, 128, "давач", 10, INK, "middle", "bold")
    s += rect(560, 64, 18, 56, fill="#eee", stroke=INK, sw=1.4)
    s += text(569, 138, "ціль (1 м)", 10, INK, "middle", "bold")
    s += arrow(96, 84, 552, 84, GREEN, 2)
    s += text(320, 76, "імпульс →", 10.5, GREEN, "middle", "bold")
    s += arrow(552, 100, 96, 100, BLUE, 2)
    s += text(320, 116, "← відлуння", 10.5, BLUE, "middle", "bold")
    # часові смуги
    s += text(70, 178, "звук (343 м/с):", 12, INK, "start", "bold")
    s += rect(230, 166, 360, 18, fill="#cfe0cf", stroke=GREEN, sw=1.2)
    s += text(410, 180, "t ≈ 5.83 мс", 12, GREEN, "middle", "bold")
    s += text(70, 218, "світло (3·10⁸):", 12, INK, "start", "bold")
    s += rect(230, 206, 6, 18, fill="#cfd9f3", stroke=BLUE, sw=1.2)
    s += text(300, 220, "t ≈ 6.67 нс  (майже у 10⁶ разів швидше)", 12, BLUE, "start", "bold")
    s += text(w / 2, 262, "повільний звук міряє простий таймер; швидке світло — наносекундна електроніка",
              11, GREY, "middle", "italic")
    save("fig-29-1-2-tof-timescale.svg", s)


def fig_triangulation():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Тріангуляція: близька ціль дає крутий кут, далека — пологий",
              14, INK, "middle", "bold")
    # випромінювач
    ex, ey = 90, 250
    s += rect(70, ey - 6, 30, 18, fill="#eef4fb", stroke=BLUE, sw=1.5)
    s += text(85, ey + 28, "випром.", 10, INK, "middle", "bold")
    # приймач (лінійка) над випромінювачем — база
    s += rect(72, ey - 70, 14, 44, fill="#fff", stroke=INK, sw=1.4)
    s += text(60, ey - 48, "приймач", 10, INK, "end", "bold")
    s += line(100, ey, 100, ey - 48, GREY, 1.2, dash="3,3")
    s += text(116, ey - 24, "база b", 10, GREY, "start", "italic")
    # промінь випромінювача
    near = (380, 150)
    far = (600, 90)
    s += arrow(100, ey, far[0] - 14, far[1] + 6, BLUE, 1.8)
    s += rect(near[0] - 8, near[1] - 14, 14, 40, fill="#eee", stroke=GREEN, sw=1.5)
    s += text(near[0], near[1] - 22, "близька", 10, GREEN, "middle", "bold")
    s += rect(far[0] - 8, far[1] - 14, 14, 40, fill="#eee", stroke=RED, sw=1.5)
    s += text(far[0], far[1] - 22, "далека", 10, RED, "middle", "bold")
    # відбиті промені під різними кутами на приймач
    s += arrow(near[0] - 2, near[1], 86, ey - 58, GREEN, 1.8)        # крутий
    s += arrow(far[0] - 2, far[1], 86, ey - 44, RED, 1.8)           # пологий
    s += text(330, 250, "положення плями на приймачі → кут → відстань", 11, INK, "middle", "bold")
    s += text(w / 2, 300, "далі ціль — менша зміна кута на метр → гірша роздільність удалині",
              11, GREY, "middle", "italic")
    save("fig-29-1-3-triangulation.svg", s)


def fig_carriers():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Носій сигналу: звук, світло, радіо — різні сильні боки",
              15, INK, "middle", "bold")
    cols = [
        ("ультразвук", GREEN, ["≈ 343 м/с", "промінь широкий", "глухне на м'якому", "дешевий"]),
        ("світло (ІЧ/лазер)", GOLD, ["≈ 3·10⁸ м/с", "промінь вузький", "плутає сонце/скло", "точний"]),
        ("радіо (радар)", BLUE, ["≈ 3·10⁸ м/с", "крізь туман/пил", "складний", "далекий"]),
    ]
    labels = ["швидкість", "промінь", "слабкість", "сила"]
    x0, y0 = 30, 50
    lw, cw, rh = 110, 190, 40
    s += rect(x0, y0, lw, rh, fill="#eef1f6", stroke=GREY, sw=1)
    for j, (name, col, _d) in enumerate(cols):
        s += rect(x0 + lw + j * cw, y0, cw, rh, fill="#eef1f6", stroke=GREY, sw=1)
        s += text(x0 + lw + j * cw + cw / 2, y0 + 24, name, 12.5, col, "middle", "bold")
    for r, lab in enumerate(labels):
        yy = y0 + rh * (r + 1)
        s += rect(x0, yy, lw, rh, fill="#fafafa", stroke=GREY, sw=0.8)
        s += text(x0 + 10, yy + 24, lab, 11.5, INK, "start", "bold")
        for j, (_n, col, data) in enumerate(cols):
            s += rect(x0 + lw + j * cw, yy, cw, rh, fill="#fff", stroke=GREY, sw=0.8)
            s += text(x0 + lw + j * cw + cw / 2, yy + 24, data[r], 11, INK, "middle")
    save("fig-29-1-4-carriers.svg", s)


def fig_target():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Ворог далекоміра: ціль, що не вертає відлуння",
              15, INK, "middle", "bold")
    cases = [
        ("тверда пласка", True, "вертає ✓", GREEN),
        ("м'яка", False, "поглинає", RED),
        ("похила", False, "відбиває вбік", RED),
        ("прозора", False, "пропускає", RED),
    ]
    pw, py, ph = 162, 52, 180
    for i, (title, ok, note, col) in enumerate(cases):
        x = 18 + i * 174
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, title, 12, col, "middle", "bold")
        cy = py + 96
        em = x + 26
        s += rect(x + 14, cy - 12, 16, 24, fill="#eef6ef", stroke=GREEN, sw=1.3)
        s += arrow(x + 32, cy, x + 118, cy, GREEN, 1.8)
        if i == 0:
            s += rect(x + 120, cy - 26, 12, 52, fill="#cfd6de", stroke=INK, sw=1.4)
            s += arrow(x + 118, cy + 10, x + 34, cy + 10, BLUE, 1.8)
        elif i == 1:
            s += rect(x + 120, cy - 26, 16, 52, fill="#e7d9c8", stroke="#b08a5a", sw=1.4)
            s += text(x + 128, cy + 4, "≋", 16, "#b08a5a", "middle", "bold")
        elif i == 2:
            s += polygon([(x + 116, cy - 30), (x + 134, cy - 16), (x + 122, cy + 28),
                          (x + 104, cy + 14)], fill="#cfd6de", stroke=INK, sw=1)
            s += arrow(x + 122, cy - 4, x + pw - 6, cy - 30, BLUE, 1.6)
        else:
            s += rect(x + 120, cy - 26, 12, 52, fill="#dceaf5", stroke=BLUE, sw=1.2)
            s += arrow(x + 118, cy, x + pw - 8, cy, GREEN, 1.6, dash="3,3")
        s += text(x + pw / 2, py + ph - 12, note, 11, col, "middle", "bold")
    save("fig-29-1-5-target.svg", s)


def fig_dist_compare():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Способи виміру відстані поряд — мапа вибору",
              15, INK, "middle", "bold")
    cols = [
        ("УЗ-ToF", GREEN, ["до ~5 м", "рівна", "широкий", "м'які цілі", "дешево"]),
        ("лазер-ToF", BLUE, ["до сотень м", "рівна", "вузький", "сонце, скло", "дорожче"]),
        ("ІЧ-тріангул.", GOLD, ["до ~1 м", "падає вдалині", "вузький", "далекі цілі", "дешево"]),
        ("радар", "#9a4ea8", ["до км", "рівна", "сектор", "складність", "дорого"]),
    ]
    labels = ["дальність", "роздільність", "промінь", "спотикається", "ціна"]
    x0, y0 = 24, 48
    lw, cw, rh = 116, 142, 32
    s += rect(x0, y0, lw, rh, fill="#eef1f6", stroke=GREY, sw=1)
    for j, (name, col, _d) in enumerate(cols):
        s += rect(x0 + lw + j * cw, y0, cw, rh, fill="#eef1f6", stroke=GREY, sw=1)
        s += text(x0 + lw + j * cw + cw / 2, y0 + 21, name, 12, col, "middle", "bold")
    for r, lab in enumerate(labels):
        yy = y0 + rh * (r + 1)
        s += rect(x0, yy, lw, rh, fill="#fafafa", stroke=GREY, sw=0.8)
        s += text(x0 + 8, yy + 21, lab, 11, INK, "start", "bold")
        for j, (_n, col, data) in enumerate(cols):
            s += rect(x0 + lw + j * cw, yy, cw, rh, fill="#fff", stroke=GREY, sw=0.8)
            s += text(x0 + lw + j * cw + cw / 2, yy + 21, data[r], 10.5, INK, "middle")
    save("fig-29-1-6-compare.svg", s)


def wave(x0, y0, w, amp, cycles=3, phase=0.0, color=GREEN, sw=2):
    pts = []
    N = cycles * 16
    for i in range(N + 1):
        t = i / N
        pts.append((x0 + w * t, y0 - amp * math.sin(2 * math.pi * cycles * t + phase)))
    return poly(pts, color, sw)


def laser(cx, cy, w=26, h=34, color=RED):
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#fbf2f1", stroke=color, sw=1.6, rx=3)
            + polygon([(cx + w / 2, cy - 5), (cx + w / 2 + 10, cy), (cx + w / 2, cy + 5)], fill=color))


# ════════════════════════════════════════════════════════════════════════════
#  §29.2 Час польоту (ToF): звук
# ════════════════════════════════════════════════════════════════════════════

def fig_cycle():
    w, h = 700, 270
    s = header(w, h)
    s += text(w / 2, 26, "Цикл ультразвукового виміру: пакет → відлуння → час",
              15, INK, "middle", "bold")
    s += transducer(80, 140)
    s += text(80, 188, "перетворювач", 10.5, INK, "middle", "bold")
    s += text(80, 202, "(п'єзо, ≈ 40 кГц)", 9.5, GREY, "middle", "italic")
    s += rect(560, 96, 18, 90, fill="#eee", stroke=INK, sw=1.4)
    s += text(569, 204, "ціль", 10.5, INK, "middle", "bold")
    s += burst(110, 116, 90, 14, 8, GREEN, 1.6)
    s += arrow(205, 116, 552, 116, GREEN, 2)
    s += text(360, 106, "пакет →", 11, GREEN, "middle", "bold")
    s += arrow(552, 160, 110, 160, BLUE, 2)
    s += text(360, 178, "← відлуння", 11, BLUE, "middle", "bold")
    s += line(80, 224, 569, 224, INK, 1.2)
    s += line(80, 218, 80, 230, INK, 1.2)
    s += line(569, 218, 569, 230, INK, 1.2)
    s += text(324, 244, "d = v · t / 2     (v ≈ 343 м/с)", 13, INK, "middle", "bold")
    save("fig-29-2-1-cycle.svg", s)


def fig_trigger_echo():
    w, h = 700, 290
    s = header(w, h)
    s += text(w / 2, 26, "Сигнали trigger і echo: ширина echo = час польоту",
              14.5, INK, "middle", "bold")
    x0, xe = 120, 660
    rows = [("trigger", 80), ("пакет", 150), ("echo", 230)]
    for (lbl, y) in rows:
        s += line(x0, y, xe, y, FAINT, 1)
        s += text(x0 - 10, y - 18, lbl, 11.5, INK, "end", "bold")
    # trigger: короткий імпульс
    s += poly([(x0, 80), (160, 80), (160, 56), (185, 56), (185, 80), (xe, 80)], INK, 2)
    s += text(172, 48, "«пни»", 9.5, INK, "middle", "italic")
    # пакет: 8 коливань одразу після trigger
    s += burst(200, 150, 70, 16, 8, GREEN, 1.6)
    s += text(235, 124, "8 коливань 40 кГц", 9.5, GREEN, "middle", "italic")
    # echo: широкий імпульс
    e0, e1 = 200, 520
    s += poly([(x0, 230), (e0, 230), (e0, 200), (e1, 200), (e1, 230), (xe, 230)], BLUE, 2.2)
    s += line(e0, 246, e1, 246, RED, 1.6)
    s += line(e0, 240, e0, 252, RED, 1.6)
    s += line(e1, 240, e1, 252, RED, 1.6)
    s += text((e0 + e1) / 2, 266, "t = час польоту → /58 = см", 12, RED, "middle", "bold")
    save("fig-29-2-2-trigger-echo.svg", s)


def fig_beam_cone():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Промінь — конус: відповідає найближча ціль у секторі",
              14.5, INK, "middle", "bold")
    ax, ay = 90, 160
    s += transducer(80, 160, 24, 50, GREEN)
    s += cone(102, 160, 520, 16, 0, GREEN, 1.4)
    s += text(330, 96, "конус 15–30°", 11, GREEN, "middle", "bold")
    # дві цілі в конусі
    near = (340, 150)
    far = (560, 200)
    s += rect(near[0], near[1] - 22, 14, 44, fill="#eee", stroke=GREEN, sw=1.6)
    s += text(near[0] + 7, near[1] - 30, "ближча", 10, GREEN, "middle", "bold")
    s += rect(far[0], far[1] - 18, 14, 36, fill="#eee", stroke=RED, sw=1.5)
    s += text(far[0] + 7, far[1] + 32, "дальша", 10, RED, "middle", "bold")
    s += arrow(108, 156, near[0] - 4, near[1] - 4, GREEN, 1.8)
    s += arrow(near[0] - 4, near[1] + 6, 108, 166, GREEN, 1.8)
    s += text(330, 250, "давач чує найближчу (її відлуння — перше); точне положення вбік не розрізняє",
              10.5, INK, "middle", "italic")
    save("fig-29-2-3-beam-cone.svg", s)


def fig_range_window():
    w, h = 700, 230
    s = header(w, h)
    s += text(w / 2, 26, "Робоче вікно: сліпа зона зблизька, тайм-аут удалині",
              14.5, INK, "middle", "bold")
    y = 120
    x0, xe = 90, 660
    s += transducer(70, y, 22, 44, GREEN)
    s += line(x0, y, xe, y, INK, 2)
    s += arrow(xe - 30, y, xe + 4, y, INK, 2)
    s += text(xe, y + 22, "відстань", 11, INK, "middle", "bold")
    # сліпа зона
    b1 = 150
    s += rect(x0, y - 18, b1 - x0, 36, fill="#f3d9d9", stroke=RED, sw=1.2)
    s += text((x0 + b1) / 2, y - 26, "сліпа зона", 10.5, RED, "middle", "bold")
    s += text((x0 + b1) / 2, y + 34, "≈ 2 см", 9.5, RED, "middle", "italic")
    # робоче вікно
    b2 = 540
    s += rect(b1, y - 18, b2 - b1, 36, fill="#d8efd8", stroke=GREEN, sw=1.2)
    s += text((b1 + b2) / 2, y - 26, "робоче вікно (чесний вимір)", 11, GREEN, "middle", "bold")
    # поза діапазоном
    s += rect(b2, y - 18, xe - b2, 36, fill="#eee", stroke=GREY, sw=1.2)
    s += text((b2 + xe) / 2, y - 26, "тайм-аут", 10.5, GREY, "middle", "bold")
    s += text((b2 + xe) / 2, y + 34, "відлуння кволе", 9.5, GREY, "middle", "italic")
    save("fig-29-2-4-range-window.svg", s)


def fig_single_dual():
    w, h = 700, 270
    s = header(w, h)
    s += text(w / 2, 26, "Один перетворювач (шле й слухає) проти двох окремих",
              14.5, INK, "middle", "bold")
    # ліво — один
    s += rect(30, 50, 310, 200, fill="#fbf2f1", stroke=RED, sw=1.4, rx=8)
    s += text(185, 72, "один кристал", 13, RED, "middle", "bold")
    s += transducer(110, 150, 26, 56, INK)
    s += arrow(126, 134, 280, 134, GREEN, 1.8)
    s += arrow(280, 166, 126, 166, BLUE, 1.8)
    s += text(210, 124, "шле", 10, GREEN, "middle", "bold")
    s += text(210, 184, "слухає (по черзі)", 10, BLUE, "middle", "bold")
    s += text(185, 232, "дзвенить → більша сліпа зона", 10.5, RED, "middle", "italic")
    # право — два
    s += rect(360, 50, 310, 200, fill="#f1f7f1", stroke=GREEN, sw=1.4, rx=8)
    s += text(515, 72, "два окремі", 13, GREEN, "middle", "bold")
    s += transducer(420, 120, 22, 40, GREEN)
    s += text(420, 100, "TX", 10, GREEN, "middle", "bold")
    s += transducer(420, 190, 22, 40, BLUE)
    s += text(420, 222, "RX", 10, BLUE, "middle", "bold")
    s += arrow(434, 112, 620, 112, GREEN, 1.8)
    s += arrow(620, 198, 434, 198, BLUE, 1.8)
    s += text(540, 156, "одночасно → менша сліпа зона", 10, INK, "middle", "italic")
    save("fig-29-2-5-single-dual.svg", s)


def fig_temperature():
    w, h = 640, 300
    s = header(w, h)
    s += text(w / 2, 26, "Швидкість звуку росте з температурою: v ≈ 331 + 0.6·T",
              14, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 250, 470, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "v, м/с", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "T, °C", 11, INK, "middle", "bold")
    # пряма v=331..355 на 0..40 → нормуємо v у [0.1..0.9]
    def vnorm(v):
        return (v - 325) / 40.0
    pts = [(t / 40, vnorm(331 + 0.6 * t)) for t in range(0, 41, 4)]
    s += _plot_path(x0, y0, pw, ph, pts, RED, 2.6)
    # зашите 343
    s += _plot_path(x0, y0, pw, ph, [(0, vnorm(343)), (1, vnorm(343))], GREY, 1.6, dash="6,4")
    s += text(*(_pt(x0, y0, pw, ph, 0.6, vnorm(343) + 0.05)), "зашите 343", 10, GREY, "start", "italic")
    for t in (0, 20, 40):
        p = _pt(x0, y0, pw, ph, t / 40, vnorm(331 + 0.6 * t))
        s += dot(p[0], p[1], 4, RED)
        s += text(p[0], p[1] - 8, f"{331+0.6*t:.0f}", 9.5, RED, "middle", "bold")
        s += text(_pt(x0, y0, pw, ph, t / 40, 0)[0], y0 + 16, f"{t}°", 9.5, INK, "middle")
    # похибка при 0°C
    pa = _pt(x0, y0, pw, ph, 0.03, vnorm(343))
    pb = _pt(x0, y0, pw, ph, 0.03, vnorm(331))
    s += line(pa[0], pa[1], pb[0], pb[1], BLUE, 2)
    s += text(pb[0] + 8, (pa[1] + pb[1]) / 2, "похибка ≈ 3.6 %", 10, BLUE, "start", "bold")
    save("fig-29-2-6-temperature.svg", s)


def fig_pitfalls():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Три біди ультразвуку: чужий пінг, привид, м'яка ціль",
              14.5, INK, "middle", "bold")
    px = [18, 258, 498]
    pw, py, ph = 204, 50, 188
    titles = ["перехресна завада", "багаторазове відлуння", "м'яка ціль"]
    cols = [RED, GOLD, BLUE]
    for i in range(3):
        x = px[i]
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=cols[i], sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, titles[i], 12, cols[i], "middle", "bold")
        cy = py + 110
        if i == 0:
            s += transducer(x + 36, cy, 18, 36, GREEN)
            s += transducer(x + 36, cy + 54, 18, 36, RED)
            s += arrow(x + 46, cy - 6, x + pw - 20, cy - 30, GREEN, 1.6)
            s += arrow(x + 46, cy + 48, x + pw - 20, cy + 6, RED, 1.6)
            s += text(x + pw / 2, py + ph - 12, "чують пінги один одного", 10, RED, "middle", "italic")
        elif i == 1:
            s += transducer(x + 30, cy, 16, 34, GREEN)
            s += line(x + 40, cy, x + 150, cy + 40, GOLD, 1.6)
            s += line(x + 150, cy + 40, x + 60, cy + 70, GOLD, 1.6)
            s += line(x + 24, py + ph - 30, x + pw - 16, py + ph - 30, GREY, 4)
            s += text(x + pw / 2, py + ph - 12, "пізній «привид» від підлоги", 10, GOLD, "middle", "italic")
        else:
            s += transducer(x + 30, cy, 16, 34, GREEN)
            s += arrow(x + 40, cy, x + 130, cy, GREEN, 1.8)
            s += rect(x + 132, cy - 24, 18, 48, fill="#e7d9c8", stroke="#b08a5a", sw=1.4)
            s += text(x + 141, cy + 4, "≋", 16, "#b08a5a", "middle", "bold")
            s += text(x + pw / 2, py + ph - 12, "поглинає — відлуння нема", 10, BLUE, "middle", "italic")
    save("fig-29-2-7-pitfalls.svg", s)


def lens(cx, cy, ry=22, color=BLUE):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="6" ry="{ry:.1f}" fill="#dceaf5" stroke="{color}" stroke-width="1.6"/>\n'


def sun(cx, cy, r=16, color=GOLD):
    s = circle(cx, cy, r, "#fdf3d6", color, 2)
    for k in range(8):
        a = math.radians(k * 45)
        s += line(cx + (r + 3) * math.cos(a), cy + (r + 3) * math.sin(a),
                  cx + (r + 10) * math.cos(a), cy + (r + 10) * math.sin(a), color, 1.6)
    return s


def photodet(cx, cy, w=20, h=28, color=BLUE):
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#eef4fb", stroke=color, sw=1.6, rx=3)
            + text(cx, cy + 4, "PD", 9, color, "middle", "bold"))


def camera(cx, cy, w=40, h=30, color=INK):
    return (rect(cx - w / 2, cy - h / 2, w, h, fill="#eef1f6", stroke=color, sw=1.6, rx=3)
            + circle(cx + w / 2 - 6, cy, 6, "#fff", color, 1.4))


# ════════════════════════════════════════════════════════════════════════════
#  §29.3 Час польоту: світло / лазер
# ════════════════════════════════════════════════════════════════════════════

def fig_light_tof():
    w, h = 700, 270
    s = header(w, h)
    s += text(w / 2, 26, "Світловий ToF: до цілі за метр — лічені наносекунди",
              14.5, INK, "middle", "bold")
    s += laser(80, 140, 28, 40, RED)
    s += text(80, 190, "лазер (ІЧ)", 10.5, INK, "middle", "bold")
    s += rect(580, 96, 16, 90, fill="#eee", stroke=INK, sw=1.4)
    s += text(588, 204, "ціль", 10.5, INK, "middle", "bold")
    s += arrow(100, 124, 574, 124, RED, 2.4)
    s += text(340, 114, "спалах світла →", 11, RED, "middle", "bold")
    s += arrow(574, 156, 100, 156, BLUE, 2.2)
    s += text(340, 176, "← відлуння", 11, BLUE, "middle", "bold")
    s += text(330, 224, "d = c · t / 2     (c ≈ 3·10⁸ м/с)", 13, INK, "middle", "bold")
    s += rect(470, 198, 210, 40, fill="#fff7e6", stroke=GOLD, sw=1.2, rx=5)
    s += text(575, 214, "1 м → 6.67 нс", 11, "#9a7a1e", "middle", "bold")
    s += text(575, 230, "1 см → 67 пс", 11, "#9a7a1e", "middle", "bold")
    save("fig-29-3-1-light-tof.svg", s)


def fig_direct_phase():
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Дві дороги світлового ToF: прямий час чи фаза",
              15, INK, "middle", "bold")
    # ліво — прямий
    s += rect(24, 48, 330, 232, fill="#fbf2f1", stroke=RED, sw=1.4, rx=8)
    s += text(189, 70, "прямий (імпульсний)", 13, RED, "middle", "bold")
    s += line(50, 120, 330, 120, FAINT, 1)
    s += line(50, 210, 330, 210, FAINT, 1)
    s += poly([(50, 120), (90, 120), (90, 98), (104, 98), (104, 120), (330, 120)], RED, 2)
    s += poly([(50, 210), (230, 210), (230, 188), (244, 188), (244, 210), (330, 210)], BLUE, 2)
    s += text(70, 92, "спалах", 9.5, RED, "middle")
    s += text(244, 182, "відлуння", 9.5, BLUE, "middle")
    s += arrow(97, 235, 237, 235, INK, 1.6)
    s += text(167, 250, "Δt → відстань", 10.5, INK, "middle", "bold")
    s += text(189, 272, "далеко, складна електроніка", 10, GREY, "middle", "italic")
    # право — фазовий
    s += rect(366, 48, 330, 232, fill="#eef4fb", stroke=BLUE, sw=1.4, rx=8)
    s += text(531, 70, "непрямий (фазовий)", 13, BLUE, "middle", "bold")
    s += wave(386, 120, 290, 18, 4, 0, GREEN, 2)
    s += text(531, 96, "вихід (мерехтить)", 9.5, GREEN, "middle")
    s += wave(386, 200, 290, 18, 4, 1.6, BLUE, 2)
    s += text(531, 232, "відлуння — зсунуте за фазою φ", 9.5, BLUE, "middle")
    s += text(531, 272, "ближче, проста електроніка", 10, GREY, "middle", "italic")
    save("fig-29-3-2-direct-phase.svg", s)


def fig_phase_wrap():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Фаза кодує відстань, але після 2π «заплутується»",
              14.5, INK, "middle", "bold")
    s += wave(60, 110, 470, 22, 5, 0, GREEN, 2)
    s += text(70, 80, "вихід", 10.5, GREEN, "start", "bold")
    s += wave(60, 180, 470, 22, 5, 1.4, BLUE, 2)
    s += text(70, 150, "відлуння (зсув φ)", 10.5, BLUE, "start", "bold")
    s += arrow(90, 210, 116, 210, RED, 1.6)
    s += text(150, 214, "φ → d = c·φ/(4πf)", 11, RED, "start", "bold")
    # коло фази
    cx, cy = 600, 150
    s += circle(cx, cy, 44, "#fff", INK, 1.6)
    s += arrow(cx, cy, cx + 30, cy - 30, RED, 2)
    s += text(cx, cy - 54, "фаза по колу", 9.5, INK, "middle", "bold")
    s += text(cx, cy + 64, "2π → обнуляється", 9.5, RED, "middle", "italic")
    s += text(w / 2, 270, "однозначно лише до c/(2f);  10 МГц → 15 м, далі «1 м» і «16 м» не різнить",
              11.5, INK, "middle", "bold")
    save("fig-29-3-3-phase-wrap.svg", s)


def fig_source_detector():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Світловий тракт: джерело (ІЧ-світло/лазер) → ціль → приймач",
              14, INK, "middle", "bold")
    s += laser(90, 130, 30, 42, RED)
    s += text(90, 184, "джерело (ІЧ)", 10.5, INK, "middle", "bold")
    s += text(90, 198, "світлодіод / лазер", 9, GREY, "middle", "italic")
    s += rect(560, 90, 16, 90, fill="#eee", stroke=INK, sw=1.4)
    s += text(568, 198, "ціль", 10, INK, "middle", "bold")
    s += arrow(112, 112, 554, 112, RED, 2.2)
    s += arrow(554, 150, 230, 150, BLUE, 2.2)
    # приймач
    s += rect(150, 132, 36, 40, fill="#eef4fb", stroke=BLUE, sw=1.6, rx=3)
    s += text(168, 152, "PD", 11, BLUE, "middle", "bold")
    s += text(168, 192, "приймач", 10, INK, "middle", "bold")
    s += rect(250, 196, 420, 40, fill="#fbfbfb", stroke=FAINT, sw=1, rx=5)
    s += text(460, 212, "слабке/швидке відлуння → лавинний фотодіод (APD) чи лічильник фотонів (SPAD)",
              10, INK, "middle", "italic")
    s += text(460, 228, "усе — на p-n переході з §28.3", 9.5, GREY, "middle", "italic")
    save("fig-29-3-4-source-detector.svg", s)


def fig_reflectivity():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Світловий ToF залежить від поверхні: фотонів має вернутись досить",
              13.5, INK, "middle", "bold")
    cases = [("біле (90 %)", GREEN, "далеко ✓"), ("чорне", RED, "близько / зрив"),
             ("дзеркало", RED, "відбиває вбік"), ("скло", BLUE, "пропускає")]
    pw, py, ph = 162, 52, 184
    for i, (title, col, note) in enumerate(cases):
        x = 18 + i * 174
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, title, 12, col, "middle", "bold")
        cy = py + 100
        s += laser(x + 26, cy, 20, 30, RED)
        s += arrow(x + 40, cy, x + 116, cy, RED, 1.8)
        if i == 0:
            s += rect(x + 118, cy - 26, 12, 52, fill="#f4f4f4", stroke=INK, sw=1.4)
            for k in range(4):
                s += arrow(x + 116, cy - 12 + k * 8, x + 40, cy - 12 + k * 8, BLUE, 1.3)
        elif i == 1:
            s += rect(x + 118, cy - 26, 14, 52, fill="#2a2a2a", stroke=INK, sw=1.2)
            s += arrow(x + 116, cy, x + 96, cy, BLUE, 1.2)
        elif i == 2:
            s += polygon([(x + 116, cy - 28), (x + 132, cy - 16), (x + 120, cy + 28),
                          (x + 104, cy + 16)], fill="#cfe0f3", stroke=INK, sw=1)
            s += arrow(x + 122, cy - 4, x + pw - 6, cy - 28, BLUE, 1.5)
        else:
            s += rect(x + 118, cy - 26, 12, 52, fill="#dceaf5", stroke=BLUE, sw=1.2)
            s += arrow(x + 116, cy, x + pw - 8, cy, RED, 1.5, dash="3,3")
        s += text(x + pw / 2, py + ph - 12, note, 11, col, "middle", "bold")
    save("fig-29-3-5-reflectivity.svg", s)


def fig_lidar():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Сканований промінь будує хмару точок — LiDAR",
              15, INK, "middle", "bold")
    cx, cy = 140, 200
    s += circle(cx, cy, 18, "#eef4fb", BLUE, 1.8)
    s += text(cx, cy + 4, "ToF", 10, BLUE, "middle", "bold")
    s += text(cx, cy + 40, "LiDAR", 11, INK, "middle", "bold")
    # контур стін/предметів — набір точок
    outline = ([(360, 70 + i * 6) for i in range(0, 18)]
               + [(360 - i * 6, 70) for i in range(0, 30)]
               + [(180 + i * 7, 320) for i in range(0, 40) if 180 + i * 7 < 470])
    wall = [(560, 90 + i * 9) for i in range(0, 22)]
    # промені до кількох точок
    targets = [(360, 90), (360, 180), (300, 70), (200, 70), (470, 300), (560, 150), (560, 250)]
    for (tx, ty) in targets:
        s += line(cx, cy, tx, ty, GREEN, 1, dash="4,4")
    for (tx, ty) in outline + wall:
        s += dot(tx, ty, 2.4, RED)
    s += text(420, 300, "тисячі точок → 3D-карта оточення", 11, INK, "middle", "italic")
    save("fig-29-3-6-lidar.svg", s)


def fig_us_vs_light():
    w, h = 660, 300
    s = header(w, h)
    s += text(w / 2, 26, "Звук проти світла: коли що", 15.5, INK, "middle", "bold")
    labels = ["швидкодія", "дальність", "промінь", "роздільність", "чутл. до цілі", "до повітря", "ціна"]
    cols = [
        ("ультразвук", GREEN, ["повільно", "до ~5 м", "широкий конус", "груба", "колір — ок", "темп.! ", "дешево"]),
        ("світло (ToF)", BLUE, ["миттєво", "до сотень м", "вузький", "тонка", "темне/скло — зле", "чисте — ок", "дорожче"]),
    ]
    x0, y0 = 24, 48
    lw, cw, rh = 150, 230, 32
    s += rect(x0, y0, lw, rh, fill="#eef1f6", stroke=GREY, sw=1)
    for j, (name, col, _d) in enumerate(cols):
        s += rect(x0 + lw + j * cw, y0, cw, rh, fill="#eef1f6", stroke=GREY, sw=1)
        s += text(x0 + lw + j * cw + cw / 2, y0 + 21, name, 12.5, col, "middle", "bold")
    for r, lab in enumerate(labels):
        yy = y0 + rh * (r + 1)
        s += rect(x0, yy, lw, rh, fill="#fafafa", stroke=GREY, sw=0.8)
        s += text(x0 + 10, yy + 21, lab, 11.5, INK, "start", "bold")
        for j, (_n, col, data) in enumerate(cols):
            s += rect(x0 + lw + j * cw, yy, cw, rh, fill="#fff", stroke=GREY, sw=0.8)
            s += text(x0 + lw + j * cw + cw / 2, yy + 21, data[r], 11, INK, "middle")
    save("fig-29-3-7-compare.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §29.4 Тріангуляція
# ════════════════════════════════════════════════════════════════════════════

def fig_tri_geometry():
    w, h = 700, 320
    s = header(w, h)
    s += text(w / 2, 26, "Тріангуляція: відстань із кута, під яким вернувся промінь",
              14.5, INK, "middle", "bold")
    ex, ey = 90, 180
    lx, ly = 90, 250            # приймач нижче на базу b
    s += laser(ex, ey, 26, 34, RED)
    s += text(ex, ey - 26, "ІЧ-світлодіод", 10, INK, "middle", "bold")
    s += lens(lx, ly, 20, BLUE)
    s += text(lx - 16, ly + 30, "лінза+PSD", 10, BLUE, "middle", "bold")
    s += line(ex, ey + 18, ex, ly - 18, GREY, 1.2, dash="3,3")
    s += text(ex - 14, (ey + ly) / 2, "база b", 9.5, GREY, "end", "italic")
    # промінь
    s += arrow(108, ey, 620, ey, RED, 1.8, dash="5,4")
    s += text(360, ey - 8, "промінь →", 10, RED, "middle", "bold")
    # цілі
    near = (350, ey)
    far = (560, ey)
    s += rect(near[0], near[1] - 26, 12, 52, fill="#eee", stroke=GREEN, sw=1.6)
    s += text(near[0] + 6, near[1] - 32, "ближча", 10, GREEN, "middle", "bold")
    s += rect(far[0], far[1] - 22, 12, 44, fill="#eee", stroke="#c0271e", sw=1.5)
    s += text(far[0] + 6, far[1] + 32, "дальша", 10, "#c0271e", "middle", "bold")
    # відбиті промені до лінзи
    s += arrow(near[0], near[1] + 6, lx + 4, ly - 6, GREEN, 1.8)
    s += arrow(far[0], far[1] + 6, lx + 6, ly - 4, "#c0271e", 1.8)
    # плями на PSD (за лінзою)
    s += line(lx, ly, lx - 26, ly + 14, GREEN, 1.6)
    s += line(lx, ly, lx - 26, ly + 2, "#c0271e", 1.6)
    s += dot(lx - 26, ly + 14, 3.5, GREEN)
    s += dot(lx - 26, ly + 2, 3.5, "#c0271e")
    s += text(lx - 30, ly + 30, "пляма: близько ≠ далеко", 9.5, INK, "end", "italic")
    s += text(w / 2, 308, "положення плями кодує кут, а кут — відстань · часу міряти не треба",
              11, GREY, "middle", "italic")
    save("fig-29-4-1-geometry.svg", s)


def fig_similar_triangles():
    w, h = 640, 300
    s = header(w, h)
    s += text(w / 2, 26, "Подібні трикутники: d = f · b / x", 15, INK, "middle", "bold")
    # великий трикутник
    ox, oy = 90, 240
    tgt = (560, 110)
    s += line(ox, oy, ox, oy - 70, INK, 2)            # база b
    s += text(ox - 12, oy - 35, "b", 13, INK, "end", "bold")
    s += line(ox, oy, tgt[0], tgt[1], GREEN, 2)        # гіпотенуза до цілі
    s += line(ox, oy - 70, tgt[0], tgt[1], GREEN, 2)
    s += line(ox, oy, tgt[0], oy, INK, 1.4, dash="4,3")  # відстань d
    s += text((ox + tgt[0]) / 2, oy + 20, "відстань d", 12, INK, "middle", "bold")
    s += rect(tgt[0], tgt[1] - 10, 12, oy - tgt[1] + 10, fill="#eee", stroke=INK, sw=1.3)
    s += text(tgt[0] + 6, tgt[1] - 16, "ціль", 10, INK, "middle", "bold")
    # малий трикутник (інсет)
    sx, sy = 150, 150
    s += rect(120, 90, 130, 90, fill="#fbfbfb", stroke=FAINT, sw=1, rx=6)
    s += text(185, 106, "усередині давача", 9.5, GREY, "middle", "italic")
    s += line(135, 165, 135, 140, INK, 1.6)
    s += text(128, 154, "x", 11, INK, "end", "bold")
    s += line(135, 165, 235, 165, INK, 1.6)
    s += text(185, 178, "f", 11, INK, "middle", "bold")
    s += line(135, 140, 235, 165, BLUE, 1.6)
    s += text(w / 2, 280, "d / b = f / x   ⇒   d = f · b / x   (обернено: d ∝ 1/x)",
              13, INK, "middle", "bold")
    save("fig-29-4-2-similar-triangles.svg", s)


def fig_tri_anatomy():
    w, h = 700, 250
    s = header(w, h)
    s += text(w / 2, 26, "Будова ІЧ-далекоміра: світлодіод, лінза, позиційний приймач",
              13.5, INK, "middle", "bold")
    s += rect(40, 80, 150, 120, fill="#fbfbfb", stroke=GREY, sw=1.3, rx=8)
    s += text(115, 70, "давач", 10, GREY, "middle", "italic")
    s += laser(75, 120, 22, 30, RED)
    s += text(75, 152, "ІЧ-LED", 9.5, RED, "middle", "bold")
    s += text(75, 165, "мерехтить", 8.5, GREY, "middle", "italic")
    s += lens(155, 160, 20, BLUE)
    s += text(155, 192, "лінза+PSD", 9, BLUE, "middle", "bold")
    s += rect(560, 70, 16, 130, fill="#eee", stroke=INK, sw=1.4)
    s += text(568, 214, "ціль", 10, INK, "middle", "bold")
    s += arrow(95, 112, 552, 112, RED, 2, dash="5,4")
    s += text(330, 102, "мерехтливий промінь →", 10, RED, "middle", "bold")
    s += arrow(556, 150, 175, 160, BLUE, 2)
    s += text(360, 178, "← відбита пляма крізь лінзу", 10, BLUE, "middle", "bold")
    s += text(w / 2, 234, "мерехтіння → синхронне детектування відсіює стале денне світло",
              11, GREY, "middle", "italic")
    save("fig-29-4-3-anatomy.svg", s)


def fig_tri_nonlinear():
    w, h = 660, 300
    s = header(w, h)
    s += text(w / 2, 26, "Вихід — гіпербола (d ∝ 1/x), а коло нуля ще й немонотонний",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 250, 480, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "вихід", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "відстань d", 11, INK, "middle", "bold")
    # гіпербола: для d від 0.08..1, вихід ~ 1/d (норм.)
    pts = [(d, min(0.95, 0.09 / d)) for d in [0.1 + 0.02 * i for i in range(0, 46)]]
    s += _plot_path(x0, y0, pw, ph, pts, GREEN, 2.6)
    # немонотонний завиток коло нуля (d дуже мале → крива повертає вниз)
    turn = [(0.02, 0.4), (0.05, 0.7), (0.09, 0.9)]
    s += _plot_path(x0, y0, pw, ph, turn, RED, 2.6)
    s += text(*(_pt(x0, y0, pw, ph, 0.04, 0.5)), "поворот!", 10, RED, "start", "bold")
    # дві відстані — один вихід
    yval = 0.7
    s += _plot_path(x0, y0, pw, ph, [(0, yval), (0.5, yval)], GREY, 1.2, dash="4,3")
    s += dot(*_pt(x0, y0, pw, ph, 0.05, yval), 4, RED)
    s += dot(*_pt(x0, y0, pw, ph, 0.13, yval), 4, GREEN)
    s += text(*(_pt(x0, y0, pw, ph, 0.2, yval + 0.04)), "один вихід — дві відстані", 10, RED, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.55, 0.5)), "далеко → крива майже пласка", 10, GREEN, "start", "italic")
    s += text(w / 2, 288, "треба калібрувати (§28.6) і шанувати мінімальну дальність", 11, INK, "middle", "italic")
    save("fig-29-4-4-nonlinear.svg", s)


def fig_tri_resolution():
    w, h = 680, 270
    s = header(w, h)
    s += text(w / 2, 26, "Роздільність тане з відстанню: рівні Δd → дедалі менший зсув плями",
              13, INK, "middle", "bold")
    # шкала відстані з рівними кроками
    y = 110
    x0, xe = 80, 640
    s += line(x0, y, xe, y, INK, 2)
    s += arrow(xe - 30, y, xe + 4, y, INK, 2)
    s += text(xe, y + 22, "відстань d", 11, INK, "middle", "bold")
    s += laser(60, y, 20, 28, RED)
    for i, d in enumerate([0.5, 1.0, 1.5, 2.0]):
        x = x0 + d * 270
        s += line(x, y - 8, x, y + 8, INK, 1.6)
        s += text(x, y + 22, f"{d:.1f}", 9.5, INK, "middle")
    # зсув плями на детекторі (внизу): для тих самих d рівними кроками, але плями ~1/d
    py = 220
    s += line(x0, py, x0 + 300, py, BLUE, 2)
    s += text(x0 - 6, py + 4, "PSD:", 10, BLUE, "end", "bold")
    base = 0.0
    for d in [0.5, 1.0, 1.5, 2.0]:
        xp = x0 + (1.0 / d) * 150
        s += dot(xp, py, 4, BLUE)
        s += text(xp, py - 10, f"{d:.1f}", 8.5, BLUE, "middle")
    s += text(x0 + 200, py + 24, "далекі цілі тиснуться разом → їх не різнити", 10, BLUE, "start", "italic")
    s += text(w / 2, 256, "похибка росте ≈ як d²  →  тріангуляція — давач близької дії", 11.5, INK, "middle", "bold")
    save("fig-29-4-5-resolution.svg", s)


def fig_tri_variants():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Родичі тріангуляції: стереозір і структуроване світло",
              14.5, INK, "middle", "bold")
    # ліво — стерео
    s += rect(24, 50, 330, 210, fill="#eef4fb", stroke=BLUE, sw=1.4, rx=8)
    s += text(189, 72, "стереозір (пасивно)", 13, BLUE, "middle", "bold")
    s += camera(80, 130, 40, 30, INK)
    s += camera(80, 200, 40, 30, INK)
    s += line(80, 145, 80, 185, GREY, 1.2, dash="3,3")
    s += text(60, 168, "база", 9, GREY, "end", "italic")
    s += rect(300, 150, 16, 50, fill="#eee", stroke=INK, sw=1.4)
    s += arrow(102, 130, 298, 158, GREEN, 1.6)
    s += arrow(102, 200, 298, 192, "#c0271e", 1.6)
    s += text(189, 248, "зсув об'єкта між кадрами (паралакс) → глибина", 9.5, INK, "middle", "italic")
    # право — структуроване світло
    s += rect(366, 50, 330, 210, fill="#fbf2f1", stroke=RED, sw=1.4, rx=8)
    s += text(531, 72, "структуроване світло (активно)", 12.5, RED, "middle", "bold")
    s += laser(420, 150, 26, 36, RED)
    s += text(420, 192, "проєктор візерунка", 9, INK, "middle", "bold")
    # викривлений візерунок на об'єкті
    s += polygon([(560, 110), (600, 120), (600, 210), (560, 200)], fill="#eee", stroke=INK, sw=1.2)
    for k in range(5):
        yy = 120 + k * 18
        s += line(560, yy, 600, yy + 6, RED, 1.4)
    s += arrow(440, 150, 556, 150, RED, 1.6, dash="4,3")
    s += text(531, 248, "візерунок спотворюється на рельєфі → карта глибини", 9.5, INK, "middle", "italic")
    save("fig-29-4-6-variants.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §29.5 Відбиття й поглинання
# ════════════════════════════════════════════════════════════════════════════

def fig_fates():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Чотири долі зондувального променя", 15, INK, "middle", "bold")
    cases = [("відбився назад", GREEN, "давач бачить ✓"), ("поглинувся", RED, "темне / м'яке"),
             ("пройшов наскрізь", BLUE, "прозоре"), ("відбився вбік", GOLD, "гладке під кутом")]
    pw, py, ph = 168, 52, 178
    for i, (title, col, note) in enumerate(cases):
        x = 18 + i * 174
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, title, 11.5, col, "middle", "bold")
        cy = py + 100
        s += laser(x + 24, cy, 18, 26, INK)
        s += arrow(x + 36, cy, x + 110, cy, INK, 1.8)
        if i == 0:
            s += rect(x + 112, cy - 24, 12, 48, fill="#f4f4f4", stroke=INK, sw=1.4)
            s += arrow(x + 110, cy + 8, x + 38, cy + 8, GREEN, 1.8)
        elif i == 1:
            s += rect(x + 112, cy - 24, 14, 48, fill="#2a2a2a", stroke=INK, sw=1.2)
            s += text(x + 119, cy + 30, "→ тепло", 8.5, RED, "middle", "italic")
        elif i == 2:
            s += rect(x + 112, cy - 24, 12, 48, fill="#dceaf5", stroke=BLUE, sw=1.2)
            s += arrow(x + 124, cy, x + pw - 8, cy, BLUE, 1.6, dash="3,3")
        else:
            s += polygon([(x + 110, cy - 26), (x + 126, cy - 14), (x + 116, cy + 26),
                          (x + 100, cy + 14)], fill="#cfd6de", stroke=INK, sw=1)
            s += arrow(x + 120, cy - 6, x + pw - 4, cy - 28, GOLD, 1.8)
        s += text(x + pw / 2, py + ph - 12, note, 10, col, "middle", "bold")
    save("fig-29-5-1-fates.svg", s)


def fig_reflection_types():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Дзеркальне, розсіяне і зворотне відбиття", 15, INK, "middle", "bold")
    titles = ["дзеркальне", "розсіяне (матове)", "зворотне (ретро)"]
    notes = ["в один бік", "навсібіч — частина завжди назад", "точно до джерела"]
    cols = [RED, GREEN, BLUE]
    pw, py, ph = 224, 52, 184
    for i in range(3):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=cols[i], sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, titles[i], 12.5, cols[i], "middle", "bold")
        sx, sy = x + pw / 2, py + 130
        s += line(sx - 50, sy, sx + 50, sy, INK, 3)   # поверхня
        s += arrow(sx - 60, sy - 60, sx, sy, INK, 1.8)  # падаючий
        if i == 0:
            s += arrow(sx, sy, sx + 60, sy - 60, RED, 1.8)  # один відбитий
        elif i == 1:
            for dx in (-55, -25, 0, 28, 56):
                s += arrow(sx, sy, sx + dx, sy - 58, GREEN, 1.3)
        else:
            s += arrow(sx, sy, sx - 60, sy - 60, BLUE, 1.8)  # назад до джерела
        s += text(x + pw / 2, py + ph - 12, notes[i], 10, INK, "middle", "italic")
    save("fig-29-5-2-reflection-types.svg", s)


def fig_ir_vs_visible():
    w, h = 660, 250
    s = header(w, h)
    s += text(w / 2, 26, "Колір для ока ≠ відбивність для давача", 15, INK, "middle", "bold")
    # ліво — видиме око бачить темне
    s += text(180, 60, "у видимому світлі", 12, INK, "middle", "bold")
    s += rect(120, 80, 120, 90, fill="#2a2a2a", stroke=INK, sw=1.4)
    s += text(180, 130, "темне", 12, "#fff", "middle", "bold")
    s += circle(180, 200, 14, "#fff", INK, 1.6)
    s += dot(180, 200, 5, INK)
    s += text(180, 232, "око: «чорне»", 10.5, INK, "middle", "italic")
    # право — ІЧ-давач бачить світле
    s += text(480, 60, "в інфрачервоному", 12, INK, "middle", "bold")
    s += rect(420, 80, 120, 90, fill="#f0ead0", stroke=INK, sw=1.4)
    s += text(480, 130, "світле для ІЧ", 11, "#9a7a1e", "middle", "bold")
    s += laser(480, 200, 22, 26, RED)
    s += text(480, 232, "давач: «яскраве»", 10.5, RED, "middle", "italic")
    s += text(330, 124, "та сама", 10, GREY, "middle", "italic")
    s += text(330, 138, "поверхня!", 10, GREY, "middle", "bold")
    save("fig-29-5-3-ir-vs-visible.svg", s)


def fig_ir_obstacle():
    w, h = 660, 240
    s = header(w, h)
    s += text(w / 2, 26, "ІЧ-відбивач: світлодіод і приймач поряд — близька ціль вертає світло",
              13.5, INK, "middle", "bold")
    s += laser(80, 110, 24, 32, RED)
    s += text(80, 150, "ІЧ-LED", 10, RED, "middle", "bold")
    s += photodet(80, 165, 22, 30, BLUE)
    s += text(40, 165, "приймач", 10, BLUE, "end", "bold")
    s += rect(470, 70, 16, 130, fill="#e8e0cf", stroke="#9a7a1e", sw=1.5)
    s += text(478, 214, "перешкода (близько)", 10, INK, "middle", "bold")
    s += arrow(104, 100, 462, 100, RED, 2)
    s += text(290, 90, "ІЧ-промінь →", 10, RED, "middle", "bold")
    s += arrow(462, 150, 104, 168, BLUE, 2)
    s += text(290, 184, "← відбиток на приймач", 10, BLUE, "middle", "bold")
    save("fig-29-5-4-ir-obstacle.svg", s)


def fig_ambient():
    w, h = 700, 280
    s = header(w, h)
    s += text(w / 2, 26, "Стороннє світло заливає приймач; модуляція й віднімання тла рятують",
              13, INK, "middle", "bold")
    s += sun(120, 80, 18, GOLD)
    s += text(120, 116, "сонце (рівне ІЧ)", 10, "#9a7a1e", "middle", "bold")
    s += photodet(330, 170, 30, 40, BLUE)
    s += text(330, 214, "приймач", 10, BLUE, "middle", "bold")
    # рівне тло
    for dx in (-10, 0, 10):
        s += arrow(135 + dx, 96, 320, 158, GOLD, 1.2)
    # мерехтливий світлодіод
    s += laser(120, 200, 22, 26, RED)
    s += text(120, 236, "ІЧ-LED (мерехтить)", 9.5, RED, "middle", "bold")
    s += burst(144, 195, 160, 10, 6, RED, 1.4)
    s += arrow(150, 200, 312, 184, RED, 1.6)
    # вихід приймача
    s += rect(430, 100, 250, 150, fill="#fbfbfb", stroke=FAINT, sw=1, rx=6)
    s += text(555, 120, "приймач бачить:", 10.5, INK, "middle", "bold")
    s += line(450, 150, 660, 150, GOLD, 3)
    s += text(555, 142, "рівне тло (відкинути)", 9.5, "#9a7a1e", "middle")
    s += burst(450, 200, 210, 12, 6, RED, 1.6)
    s += text(555, 232, "тільки мерехтіння → корисний сигнал", 9.5, RED, "middle", "bold")
    save("fig-29-5-5-ambient.svg", s)


def fig_acoustic():
    w, h = 680, 250
    s = header(w, h)
    s += text(w / 2, 26, "Звук відбивається за стрибком акустичного опору",
              14.5, INK, "middle", "bold")
    # тверда — сильне відлуння
    s += rect(20, 50, 320, 180, fill="#f1f7f1", stroke=GREEN, sw=1.4, rx=8)
    s += text(180, 70, "тверда щільна (стіна)", 12, GREEN, "middle", "bold")
    s += transducer(70, 140, 22, 40, GREEN)
    s += rect(280, 90, 16, 100, fill="#cfd6de", stroke=INK, sw=1.5)
    s += arrow(86, 122, 272, 122, GREEN, 2)
    s += arrow(272, 158, 86, 158, GREEN, 2)
    s += text(180, 210, "великий стрибок опору → сильне відлуння", 9.5, INK, "middle", "italic")
    # м'яка — поглинання
    s += rect(360, 50, 300, 180, fill="#fbf2f1", stroke=RED, sw=1.4, rx=8)
    s += text(510, 70, "м'яка пориста (поролон)", 12, RED, "middle", "bold")
    s += transducer(410, 140, 22, 40, GREEN)
    s += rect(600, 90, 18, 100, fill="#e7d9c8", stroke="#b08a5a", sw=1.5)
    s += text(609, 140, "≋", 16, "#b08a5a", "middle", "bold")
    s += arrow(426, 130, 594, 130, GREEN, 2)
    s += text(510, 210, "опір близький до повітря → звук в'язне", 9.5, INK, "middle", "italic")
    save("fig-29-5-6-acoustic.svg", s)


def fig_line_edge():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Відбивний контраст: лінієвод, давач краю, близькість",
              14.5, INK, "middle", "bold")
    titles = ["лінієвод", "давач краю (прірва)", "близькість"]
    cols = [INK, RED, GREEN]
    pw, py, ph = 224, 52, 196
    for i in range(3):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=cols[i], sw=1.4, rx=8)
        s += text(x + pw / 2, py + 22, titles[i], 12.5, cols[i], "middle", "bold")
        s += laser(x + pw / 2, py + 70, 22, 26, RED)
        if i == 0:
            s += rect(x + 20, py + 150, pw - 40, 20, fill="#f4f4f4", stroke=INK, sw=1)
            s += rect(x + pw / 2 - 16, py + 150, 32, 20, fill="#2a2a2a", stroke="none")
            s += arrow(x + pw / 2, py + 84, x + pw / 2, py + 148, RED, 1.6)
            s += text(x + pw / 2, py + ph - 10, "чорна лінія = провал відбиття", 9, INK, "middle", "italic")
        elif i == 1:
            s += rect(x + 20, py + 150, (pw - 40) / 2, 20, fill="#f4f4f4", stroke=INK, sw=1)
            s += arrow(x + 48, py + 84, x + 48, py + 148, GREEN, 1.6)
            s += arrow(x + pw - 56, py + 84, x + pw - 56, py + 130, RED, 1.4, dash="3,3")
            s += text(x + pw - 56, py + 118, "нема дна", 8.5, RED, "middle", "bold")
            s += text(x + pw / 2, py + ph - 10, "край: відбиток зник → стоп", 9, RED, "middle", "italic")
        else:
            s += rect(x + pw / 2 - 8, py + 120, 16, 50, fill="#e8e0cf", stroke="#9a7a1e", sw=1.4)
            s += arrow(x + pw / 2, py + 84, x + pw / 2, py + 118, GREEN, 1.6)
            s += text(x + pw / 2, py + ph - 10, "є відбиток → щось поряд", 9, GREEN, "middle", "italic")
    save("fig-29-5-7-line-edge.svg", s)


def person(cx, cy, sc=1.0, color=HOT):
    head = circle(cx, cy - 18 * sc, 7 * sc, color, color, 1)
    body = polygon([(cx - 9 * sc, cy + 22 * sc), (cx - 6 * sc, cy - 8 * sc),
                    (cx + 6 * sc, cy - 8 * sc), (cx + 9 * sc, cy + 22 * sc)], fill=color)
    return head + body


# ════════════════════════════════════════════════════════════════════════════
#  §29.6 Похибки вимірювання відстані
# ════════════════════════════════════════════════════════════════════════════

def fig_err_taxonomy():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Шість родин похибок відстані — за джерелом",
              15, INK, "middle", "bold")
    fam = [("ціль", RED, "колір, м'якість, скло"), ("геометрія", GOLD, "кут, конус, межі"),
           ("середовище", GREEN, "температура, туман"), ("засвітка/завади", BLUE, "сонце, чужі пінги"),
           ("багатопроменевість", "#9a4ea8", "привиди манівцем"), ("електроніка", INK, "поріг, годинник")]
    bw, bh = 218, 84
    gap = 12
    x0 = (w - 3 * bw - 2 * gap) / 2
    for i, (name, col, note) in enumerate(fam):
        r, c = divmod(i, 3)
        x = x0 + c * (bw + gap)
        y = 52 + r * (bh + 16)
        s += rect(x, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.6, rx=8)
        s += text(x + bw / 2, y + 32, name, 13, col, "middle", "bold")
        s += text(x + bw / 2, y + 56, note, 11, INK, "middle", "italic")
    save("fig-29-6-1-taxonomy.svg", s)


def fig_cone_trap():
    w, h = 700, 280
    s = header(w, h)
    s += text(w / 2, 26, "Пастки геометрії: конус чує найближче; похиле відбиває вбік",
              13.5, INK, "middle", "bold")
    # ліво — дрібничка затуляє стіну
    s += rect(24, 48, 330, 210, fill="#fbf7ee", stroke=GOLD, sw=1.4, rx=8)
    s += text(189, 70, "дрібничка затуляє стіну", 12, "#9a7a1e", "middle", "bold")
    s += transducer(60, 160, 22, 40, GREEN)
    s += cone(76, 160, 270, 16, 0, GREEN, 1.2)
    s += rect(170, 145, 12, 30, fill="#eee", stroke=RED, sw=1.5)
    s += text(176, 138, "дрібне", 9, RED, "middle", "bold")
    s += rect(330, 100, 12, 120, fill="#cfd6de", stroke=INK, sw=1.5)
    s += text(330, 234, "справжня стіна", 9.5, INK, "middle", "bold")
    s += arrow(168, 168, 84, 168, RED, 1.6)
    s += text(189, 250, "чує дрібне, «не бачить» стіни", 9.5, INK, "middle", "italic")
    # право — похила
    s += rect(366, 48, 330, 210, fill="#fbf2f1", stroke=RED, sw=1.4, rx=8)
    s += text(531, 70, "похила поверхня", 12, RED, "middle", "bold")
    s += transducer(410, 150, 22, 40, GREEN)
    s += polygon([(560, 100), (600, 120), (575, 210), (535, 190)], fill="#cfd6de", stroke=INK, sw=1.2)
    s += arrow(426, 140, 556, 140, GREEN, 1.8)
    s += arrow(566, 132, 660, 90, RED, 1.8)
    s += text(531, 234, "промінь відбився вбік → промах", 9.5, INK, "middle", "italic")
    save("fig-29-6-2-cone-trap.svg", s)


def fig_multipath():
    w, h = 700, 290
    s = header(w, h)
    s += text(w / 2, 26, "Багатопроменевість: відлуння манівцем читається дальшим",
              14, INK, "middle", "bold")
    s += transducer(70, 110, 22, 40, GREEN)
    s += rect(540, 70, 14, 90, fill="#eee", stroke=INK, sw=1.5)
    s += text(547, 178, "ціль (1.0 м)", 10, INK, "middle", "bold")
    # прямий шлях
    s += arrow(86, 100, 534, 100, GREEN, 1.6, dash="4,3")
    s += text(300, 90, "прямий (слабкий/закритий)", 9.5, GREEN, "middle", "italic")
    # підлога
    s += line(40, 230, 660, 230, GREY, 4)
    s += text(80, 248, "підлога", 9.5, GREY, "middle", "italic")
    # манівець через підлогу
    s += arrow(86, 128, 330, 226, "#9a4ea8", 2)
    s += arrow(330, 226, 536, 130, "#9a4ea8", 2)
    s += text(330, 210, "манівець (довший)", 10, "#9a4ea8", "middle", "bold")
    s += text(w / 2, 274, "довший шлях → давач читає 1.3 м (привид, завжди ДАЛЬШИЙ)",
              12, "#9a4ea8", "middle", "bold")
    save("fig-29-6-3-multipath.svg", s)


def fig_threshold_walk():
    w, h = 660, 300
    s = header(w, h)
    s += text(w / 2, 26, "«Прогулянка» порога: слабке відлуння перетинає поріг пізніше",
              13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 90, 250, 480, 190
    s += axes(x0, y0, pw + 12, ph + 12)
    s += text(x0 - 8, y0 - ph - 4, "амплітуда", 11, INK, "end", "bold")
    s += text(x0 + pw + 8, y0 + 18, "час →", 11, INK, "middle", "bold")
    # поріг
    thr = 0.45
    s += _plot_path(x0, y0, pw, ph, [(0, thr), (1, thr)], RED, 1.6, dash="6,4")
    s += text(x0 + pw - 4, _pt(x0, y0, pw, ph, 1, thr)[1] - 6, "поріг", 10, RED, "end", "bold")
    # сильне відлуння — круте, перетинає рано
    strong = [(t / 30, min(0.92, 1.4 * (t / 30))) for t in range(0, 31)]
    s += _plot_path(x0, y0, pw, ph, strong, GREEN, 2.4)
    # слабке — пологе, перетинає пізно
    weak = [(t / 30, min(0.55, 0.62 * (t / 30))) for t in range(0, 31)]
    s += _plot_path(x0, y0, pw, ph, weak, BLUE, 2.4)
    s += text(*(_pt(x0, y0, pw, ph, 0.6, 0.85)), "сильне", 10, GREEN, "start", "bold")
    s += text(*(_pt(x0, y0, pw, ph, 0.72, 0.5)), "слабке", 10, BLUE, "start", "bold")
    # точки перетину порога
    ts = thr / 1.4
    tw = thr / 0.62
    s += dot(*_pt(x0, y0, pw, ph, ts, thr), 4, GREEN)
    s += dot(*_pt(x0, y0, pw, ph, tw, thr), 4, BLUE)
    s += line(_pt(x0, y0, pw, ph, ts, thr)[0], y0, _pt(x0, y0, pw, ph, ts, thr)[0], _pt(x0, y0, pw, ph, ts, thr)[1], GREEN, 1, dash="2,2")
    s += line(_pt(x0, y0, pw, ph, tw, thr)[0], y0, _pt(x0, y0, pw, ph, tw, thr)[0], _pt(x0, y0, pw, ph, tw, thr)[1], BLUE, 1, dash="2,2")
    s += text(w / 2, 288, "слабке засікається пізніше → читається ДАЛЬШИМ (відбивність лізе у відстань)",
              10.5, INK, "middle", "italic")
    save("fig-29-6-4-threshold-walk.svg", s)


def fig_err_classes():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Класифікуй, тоді лікуй: три кошики похибок", 15, INK, "middle", "bold")
    cols = [("систематичне", RED, "зсув, прогулянка, нелінійність", "калібрування / компенсація"),
            ("випадкове", BLUE, "шум, тремтіння", "усереднення / фільтр"),
            ("грубий викид", "#9a4ea8", "привид, пропуск, стрибок", "відсів (медіана, межі)")]
    pw, py, ph = 224, 52, 160
    for i, (name, col, ex, fix) in enumerate(cols):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=col, sw=1.5, rx=8)
        s += text(x + pw / 2, py + 28, name, 13.5, col, "middle", "bold")
        s += text(x + pw / 2, py + 64, ex, 11, INK, "middle", "italic")
        s += line(x + 20, py + 84, x + pw - 20, py + 84, FAINT, 1)
        s += text(x + pw / 2, py + 108, "лік:", 10.5, GREY, "middle", "bold")
        s += text(x + pw / 2, py + 128, fix, 11, col, "middle", "bold")
    save("fig-29-6-5-classes.svg", s)


def fig_mitigations():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Чотири щити надійного далекоміра", 15, INK, "middle", "bold")
    titles = ["медіана", "межі здорового глузду", "довіра за сигналом", "фьюжн"]
    notes = ["вбиває викиди", "відсіює неможливе", "кволе = не вірю", "давачі прикривають"]
    cols = [GREEN, GOLD, BLUE, "#9a4ea8"]
    pw, py, ph = 166, 52, 188
    for i in range(4):
        x = 14 + i * 176
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=cols[i], sw=1.4, rx=8)
        s += text(x + pw / 2, py + 24, titles[i], 11.5, cols[i], "middle", "bold")
        cy = py + 110
        if i == 0:
            pts = [(0, 0), (1, -4), (2, 2), (3, 26), (4, -2), (5, 3), (6, -3)]
            s += poly([(x + 16 + p[0] * 20, cy + p[1]) for p in pts], GREY, 1.4)
            s += poly([(x + 16 + p[0] * 20, cy + min(p[1], 4)) for p in pts], GREEN, 2)
            s += text(x + 76, cy - 22, "пік прибрано", 8.5, GREEN, "middle", "bold")
        elif i == 1:
            s += line(x + 20, cy, x + 70, cy - 6, GREEN, 2)
            s += arrow(x + 70, cy - 6, x + 130, cy - 52, RED, 1.8)
            s += text(x + 110, cy - 30, "✗ стрибок", 8.5, RED, "middle", "bold")
        elif i == 2:
            s += burst(x + 18, cy - 4, 60, 14, 4, GREEN, 1.6)
            s += burst(x + 90, cy - 4, 60, 4, 4, RED, 1.4)
            s += text(x + 48, cy + 26, "сильне ✓", 8, GREEN, "middle")
            s += text(x + 120, cy + 26, "кволе ✗", 8, RED, "middle")
        else:
            s += transducer(x + 40, cy - 8, 16, 26, GREEN)
            s += laser(x + 110, cy - 8, 18, 24, RED)
            s += arrow(x + 50, cy + 16, x + 100, cy + 16, INK, 1.4)
            s += text(x + 83, cy + 36, "звук+оптика", 8, INK, "middle")
        s += text(x + pw / 2, py + ph - 12, notes[i], 9.5, INK, "middle", "italic")
    save("fig-29-6-6-mitigations.svg", s)


def fig_err_table():
    w, h = 700, 300
    s = header(w, h)
    s += text(w / 2, 26, "Похибка → причина → лік (шпаргалка)", 15, INK, "middle", "bold")
    rows = [
        ("«не бачить» цілі", "м'яка / похила / прозора", "інша фізика, ретрорефлектор"),
        ("показ дальший", "привид (багатопроменевість)", "медіана, межі, вузький промінь"),
        ("темне = дальше", "прогулянка порога", "поправка за амплітудою"),
        ("повзе з теплом", "швидкість звуку (T)", "термокомпенсація"),
        ("сліпне на сонці", "ІЧ-засвітка", "модуляція, фільтр, віднімання"),
        ("дикий стрибок", "збій / викид", "перевірка на здоровий глузд"),
    ]
    x0, y0 = 24, 48
    c = [0, 200, 430]
    cw = [200, 230, 246]
    rh = 36
    head = ["похибка", "причина", "лік"]
    s += rect(x0, y0, sum(cw), rh, fill="#eef1f6", stroke=GREY, sw=1)
    for j in range(3):
        s += text(x0 + c[j] + 10, y0 + 23, head[j], 12, INK, "start", "bold")
    for r, row in enumerate(rows):
        yy = y0 + rh * (r + 1)
        col = [RED, "#9a4ea8", RED, GREEN, BLUE, GOLD][r]
        s += rect(x0, yy, sum(cw), rh, fill="#ffffff", stroke=GREY, sw=0.8)
        s += text(x0 + c[0] + 10, yy + 23, row[0], 11, col, "start", "bold")
        s += text(x0 + c[1] + 10, yy + 23, row[1], 10.5, INK, "start")
        s += text(x0 + c[2] + 10, yy + 23, row[2], 10.5, INK, "start")
    save("fig-29-6-7-table.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §29.7 Інші давачі оточення: рух, температура/вологість, газ
# ════════════════════════════════════════════════════════════════════════════

def fig_pir_principle():
    w, h = 700, 290
    s = header(w, h)
    s += text(w / 2, 26, "PIR: тепле тіло, лінза Френеля з зонами, піроелемент",
              14, INK, "middle", "bold")
    # тепле тіло
    s += person(580, 150, 1.4, HOT)
    s += text(580, 200, "тепле тіло (ІЧ)", 10.5, HOT, "middle", "bold")
    s += swaves(556, 150, 180, 3, 16, 14, HOT, 36)
    # зони (лінза Френеля)
    lx, ly = 200, 150
    for k in range(-3, 4):
        ang = math.radians(k * 9)
        s += line(lx, ly, lx + 320 * math.cos(ang), ly + 320 * math.sin(ang), FAINT, 1)
    s += text(360, 90, "зони лінзи Френеля", 10.5, GREY, "middle", "italic")
    # лінза
    s += f'<path d="M {lx+16},{ly-46} A 50,50 0 0 1 {lx+16},{ly+46}" fill="none" stroke="{BLUE}" stroke-width="2"/>\n'
    s += text(lx + 30, ly + 64, "лінза", 10, BLUE, "middle", "bold")
    # піроелемент
    s += rect(lx - 40, ly - 24, 34, 48, fill="#f0e6e6", stroke=RED, sw=1.6, rx=3)
    s += text(lx - 23, ly - 2, "+", 15, RED, "middle", "bold")
    s += text(lx - 23, ly + 16, "−", 15, BLUE, "middle", "bold")
    s += text(lx - 23, ly + 40, "піроелемент", 10, RED, "middle", "bold")
    s += text(lx - 23, ly + 54, "(заряд від ΔT)", 9, GREY, "middle", "italic")
    save("fig-29-7-1-pir-principle.svg", s)


def fig_pir_motion():
    w, h = 680, 280
    s = header(w, h)
    s += text(w / 2, 26, "PIR бачить рух, а не присутність", 15, INK, "middle", "bold")
    # ліво — рух → сплески
    s += rect(24, 48, 320, 200, fill="#f1f7f1", stroke=GREEN, sw=1.4, rx=8)
    s += text(184, 70, "рухається → сплески", 12, GREEN, "middle", "bold")
    s += axes(60, 210, 260, 110, GREY)
    pts = [(0.0, 0.5), (0.12, 0.5), (0.18, 0.9), (0.26, 0.2), (0.34, 0.8), (0.42, 0.3),
           (0.5, 0.75), (0.58, 0.35), (0.7, 0.5), (1.0, 0.5)]
    s += _plot_path(60, 210, 260, 100, pts, GREEN, 2.2)
    s += text(184, 232, "перетин зон → змінний сигнал", 9.5, INK, "middle", "italic")
    # право — нерухомо → згасання
    s += rect(360, 48, 296, 200, fill="#fbf2f1", stroke=RED, sw=1.4, rx=8)
    s += text(508, 70, "завмер → згасає", 12, RED, "middle", "bold")
    s += axes(396, 210, 240, 110, GREY)
    dec = [(0.0, 0.5), (0.06, 0.9), (0.12, 0.7), (0.2, 0.62), (0.35, 0.55),
           (0.6, 0.51), (1.0, 0.5)]
    s += _plot_path(396, 210, 240, 100, dec, RED, 2.2)
    s += text(508, 232, "сталий потік тепла → сигнал у нуль", 9.5, INK, "middle", "italic")
    save("fig-29-7-2-pir-motion.svg", s)


def fig_humidity():
    w, h = 640, 250
    s = header(w, h)
    s += text(w / 2, 26, "Ємнісний давач вологості: полімер вбирає воду → C росте",
              13.5, INK, "middle", "bold")
    # дві обкладки з полімером
    cx = 280
    s += line(cx - 40, 90, cx - 40, 190, INK, 4)
    s += line(cx + 40, 90, cx + 40, 190, INK, 4)
    s += rect(cx - 36, 92, 72, 96, fill="#cfe3f7", stroke=BLUE, sw=1, rx=2)
    s += text(cx, 130, "полімер", 11, BLUE, "middle", "bold")
    # молекули води
    for (dx, dy) in [(-18, -20), (10, 0), (-6, 24), (20, 28), (4, -28), (-22, 8)]:
        s += text(cx + dx, 145 + dy, "H₂O", 9, "#1f6ea3", "middle", "bold")
    s += text(cx - 60, 210, "обкладка", 10, INK, "middle")
    s += text(cx + 60, 210, "обкладка", 10, INK, "middle")
    # стрілка ε↑ → C↑
    s += arrow(380, 140, 470, 140, GREEN, 2)
    s += text(540, 134, "ε ↑  →  C ↑", 14, GREEN, "middle", "bold")
    s += text(540, 158, "(§28.2)", 10, GREY, "middle", "italic")
    s += text(w / 2, 234, "вологе повітря → більше води в полімері → більша ємність",
              11, INK, "middle", "italic")
    save("fig-29-7-3-humidity.svg", s)


def fig_gas_types():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Три фізики газових давачів", 15, INK, "middle", "bold")
    titles = ["MOX (метал-оксид)", "електрохімічний", "NDIR (ІЧ-поглинання)"]
    notes = ["підігрітий R(газ)", "газ → струм", "газ поглинає ІЧ"]
    cols = [RED, GREEN, BLUE]
    pw, py, ph = 224, 52, 188
    for i in range(3):
        x = 16 + i * 232
        s += rect(x, py, pw, ph, fill="#fbfbfb", stroke=cols[i], sw=1.4, rx=8)
        s += text(x + pw / 2, py + 24, titles[i], 12, cols[i], "middle", "bold")
        cy = py + 110
        if i == 0:
            s += rect(x + 50, cy - 14, 120, 28, fill="#f0d9d9", stroke=RED, sw=1.4, rx=3)
            s += text(x + pw / 2, cy + 4, "оксид + нагрів", 10, RED, "middle", "bold")
            s += text(x + pw / 2, cy + 40, "R змінюється", 10, INK, "middle", "italic")
        elif i == 1:
            s += rect(x + 60, cy - 18, 100, 40, fill="#eef6ef", stroke=GREEN, sw=1.4, rx=4)
            s += text(x + pw / 2, cy + 4, "комірка", 10, GREEN, "middle", "bold")
            s += arrow(x + 160, cy, x + pw - 20, cy, GREEN, 1.8)
            s += text(x + pw / 2, cy + 42, "струм ∝ газ", 10, INK, "middle", "italic")
        else:
            s += laser(x + 36, cy, 18, 24, RED)
            s += rect(x + 80, cy - 16, 70, 32, fill="#eef4fb", stroke=BLUE, sw=1.3)
            s += text(x + 115, cy + 4, "газ", 9, BLUE, "middle")
            s += photodet(x + 180, cy, 18, 28, BLUE)
            s += arrow(x + 54, cy, x + 78, cy, RED, 1.6)
            s += arrow(x + 152, cy, x + 169, cy, BLUE, 1.6)
            s += text(x + pw / 2, cy + 42, "поглинання → ppm", 9.5, INK, "middle", "italic")
        s += text(x + pw / 2, py + ph - 12, notes[i], 10, cols[i], "middle", "bold")
    save("fig-29-7-4-gas-types.svg", s)


def fig_selectivity():
    w, h = 660, 260
    s = header(w, h)
    s += text(w / 2, 26, "Неселективний давач: реагує на багато газів — не каже, який",
              13.5, INK, "middle", "bold")
    cx, cy = 430, 150
    s += rect(cx - 36, cy - 26, 72, 52, fill="#f0d9d9", stroke=RED, sw=1.6, rx=4)
    s += text(cx, cy + 4, "MOX", 13, RED, "middle", "bold")
    gases = ["чадний газ", "спирт", "водень", "дим", "пара"]
    for i, g in enumerate(gases):
        gy = 70 + i * 34
        s += text(70, gy + 4, g, 11, INK, "start", "bold")
        s += arrow(180, gy, cx - 40, cy - 18 + i * 9, GREY, 1.4)
    s += arrow(cx + 40, cy, cx + 130, cy, RED, 2)
    s += text(cx + 170, cy - 6, "сигнал ↑", 12, RED, "middle", "bold")
    s += text(cx + 170, cy + 12, "(але який газ?)", 10, GREY, "middle", "italic")
    s += text(w / 2, 244, "усі дають подібне зростання → перехресна чутливість, фальшиві тривоги",
              10.5, INK, "middle", "italic")
    save("fig-29-7-5-selectivity.svg", s)


def fig_framework():
    w, h = 720, 220
    s = header(w, h)
    s += text(w / 2, 28, "Будь-який давач оточення — у рамці Розділу 28",
              15, INK, "middle", "bold")
    boxes = [("незнайомий\nдавач", GREY), ("клас\n§28.2–28.3", GREEN),
             ("характеристика\n§28.4", BLUE), ("дрейф, шум\n§28.5", RED),
             ("калібр. + вхід\n§28.6–28.7", "#9a4ea8"), ("надійне\nчисло", INK)]
    bw, bh, y = 104, 64, 100
    gap = (w - 40 - 6 * bw) / 5
    for i, (lbl, col) in enumerate(boxes):
        x = 20 + i * (bw + gap)
        s += rect(x, y, bw, bh, fill="#fbfbfb", stroke=col, sw=1.6, rx=8)
        a, b = lbl.split("\n")
        s += text(x + bw / 2, y + 27, a, 10.5, col, "middle", "bold")
        s += text(x + bw / 2, y + 44, b, 10, col, "middle", "bold")
        if i < 5:
            s += arrow(x + bw + 2, y + bh / 2, x + bw + gap - 2, y + bh / 2, INK, 1.8)
    s += text(w / 2, 200, "та сама послідовність питань — на кожен новий давач",
              11.5, GREY, "middle", "italic")
    save("fig-29-7-6-framework.svg", s)


if __name__ == "__main__":
    fig_spallanzani()
    fig_echo_ranging()
    fig_langevin_sonar()
    fig_timeline()
    # §29.1 Як виміряти відстань без дотику
    fig_methods()
    fig_tof_timescale()
    fig_triangulation()
    fig_carriers()
    fig_target()
    fig_dist_compare()
    # §29.2 Час польоту: звук
    fig_cycle()
    fig_trigger_echo()
    fig_beam_cone()
    fig_range_window()
    fig_single_dual()
    fig_temperature()
    fig_pitfalls()
    # §29.3 Час польоту: світло / лазер
    fig_light_tof()
    fig_direct_phase()
    fig_phase_wrap()
    fig_source_detector()
    fig_reflectivity()
    fig_lidar()
    fig_us_vs_light()
    # §29.4 Тріангуляція
    fig_tri_geometry()
    fig_similar_triangles()
    fig_tri_anatomy()
    fig_tri_nonlinear()
    fig_tri_resolution()
    fig_tri_variants()
    # §29.5 Відбиття й поглинання
    fig_fates()
    fig_reflection_types()
    fig_ir_vs_visible()
    fig_ir_obstacle()
    fig_ambient()
    fig_acoustic()
    fig_line_edge()
    # §29.6 Похибки вимірювання відстані
    fig_err_taxonomy()
    fig_cone_trap()
    fig_multipath()
    fig_threshold_walk()
    fig_err_classes()
    fig_mitigations()
    fig_err_table()
    # §29.7 Інші давачі оточення
    fig_pir_principle()
    fig_pir_motion()
    fig_humidity()
    fig_gas_types()
    fig_selectivity()
    fig_framework()
    print("OK — фігури Розділу 29 (історія + §29.1–§29.7) згенеровано в", OUT)
