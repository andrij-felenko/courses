# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 33 — «Інерціальні давачі: MEMS» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Поточний файл покриває історичну вставку (Рис. 33.0.k): кремнієва мікромеханіка,
подушка безпеки як «вбивча задача», ADXL50, ефект масштабу, поширення, урок.
Спільні помічники — у стилі Розділів 28–32.
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
GOLD  = "#caa24a"
PURP  = "#9a4ea8"
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


def _pt(x0, y0, w, ht, xv, uv):
    return (x0 + xv * w, y0 - uv * ht)


def _plot_path(x0, y0, w, ht, pts_norm, color, sw=2.4, dash=None):
    return poly([_pt(x0, y0, w, ht, xv, uv) for (xv, uv) in pts_norm], color, sw, dash=dash)


def axes(x0, y0, w, ht, color=INK):
    return arrow(x0, y0, x0, y0 - ht, color, 1.6) + arrow(x0, y0, x0 + w, y0, color, 1.6)


# ════════════════════════════════════════════════════════════════════════════
#  §33.0 Історія — MEMS і подушка безпеки
# ════════════════════════════════════════════════════════════════════════════

def fig_silicon_machining():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Кремній як механічний матеріал: машина в чипі", 13.5, INK, "middle", "bold")
    s += text(130, 64, "1) шари на пластині", 10, INK, "middle", "bold")
    s += rect(60, 80, 140, 20, fill="#cfe0f5", stroke=INK, sw=1)
    s += rect(60, 100, 140, 14, fill="#f0e0c0", stroke=INK, sw=1)
    s += rect(60, 114, 140, 26, fill="#d8d8d8", stroke=INK, sw=1)
    s += text(206, 93, "структурний", 8, GREY, "start")
    s += text(206, 110, "жертовний", 8, "#9a7a1e", "start")
    s += text(206, 130, "підкладка", 8, GREY, "start")
    s += arrow(300, 110, 352, 110, INK, 2)
    s += text(326, 100, "травлення", 8, GREY, "middle", "italic")
    s += text(525, 64, "2) жертовний шар геть → деталь вільна", 10, INK, "middle", "bold")
    bx, by = 470, 112
    s += poly([(bx - 50, by), (bx - 62, by - 7), (bx - 74, by + 7), (bx - 82, by)], GREEN, 1.6)
    s += poly([(bx + 80, by), (bx + 92, by - 7), (bx + 104, by + 7), (bx + 116, by)], GREEN, 1.6)
    s += rect(bx - 88, by - 10, 6, 20, fill=INK)
    s += rect(bx + 116, by - 10, 6, 20, fill=INK)
    s += rect(bx, by - 12, 80, 24, fill="#cfe0f5", stroke=BLUE, sw=1.5, rx=3)
    s += text(bx + 40, by + 4, "вантаж", 8.5, BLUE, "middle", "bold")
    s += text(bx + 40, by - 22, "підвішений, рухається", 8, GREEN, "middle", "italic")
    s += text(w / 2, 178, "ті самі методи, що й для мікросхем (літографія, травлення) — але виточують МЕХАНІЗМ", 10, GREY, "middle", "italic")
    s += text(w / 2, 212, "механіка + електроніка на одному кремнієвому кристалі = MEMS", 10.5, INK, "middle", "bold")
    save("fig-33-0-1-silicon-machining.svg", s)


def fig_airbag():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "«Вбивча задача»: датчик удару для подушки безпеки", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 180, 360, 130
    s += axes(x0, y0, pw + 10, ph + 10)
    s += text(x0 + pw + 6, y0 + 18, "час", 9, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "гальмування (g)", 9, INK, "end", "bold")
    pts = []
    for k in range(201):
        x = k / 200.0
        if 0.45 < x < 0.6:
            v = 0.85 * math.exp(-((x - 0.52) ** 2) / 0.0015)
        else:
            v = 0.05 * abs(math.sin(x * 30))
        pts.append((x, v))
    s += _plot_path(x0, y0, pw, ph, pts, RED, 2.2)
    s += text(x0 + 0.52 * pw, y0 - 0.95 * ph, "УДАР!", 10, RED, "middle", "bold")
    s += arrow(444, 110, 500, 110, INK, 2)
    s += text(472, 98, "спрацювання", 8, GREY, "middle", "italic")
    s += circle(582, 120, 42, fill="#eef7ef", stroke=GREEN, w=2)
    s += text(582, 116, "подушка", 10, GREEN, "middle", "bold")
    s += text(582, 132, "надулась", 9, GREEN, "middle", "bold")
    s += text(w / 2, 252, "різкий сплеск від'ємного прискорення → акселерометр ловить → подушка за мілісекунди", 9, GREY, "middle", "italic")
    s += text(w / 2, 274, "десятки млн машин × кілька датчиків = гарантований масовий ринок", 10, INK, "middle", "bold")
    save("fig-33-0-2-airbag.svg", s)


def fig_adxl50():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "ADXL50: машина й мозок на одному чипі", 13, INK, "middle", "bold")
    s += rect(60, 62, 420, 186, fill="#fbfbfb", stroke=INK, sw=1.8, rx=8)
    s += text(270, 54, "кремнієвий кристал", 9, GREY, "middle", "italic")
    cx, cy = 200, 150
    s += poly([(cx - 50, cy), (cx - 62, cy - 7), (cx - 74, cy + 7), (cx - 82, cy)], GREEN, 1.5)
    s += poly([(cx + 50, cy), (cx + 62, cy - 7), (cx + 74, cy + 7), (cx + 82, cy)], GREEN, 1.5)
    s += rect(cx - 50, cy - 16, 100, 32, fill="#cfe0f5", stroke=BLUE, sw=1.5, rx=3)
    s += text(cx, cy + 4, "вантаж-проба", 8.5, BLUE, "middle", "bold")
    s += text(cx, cy - 26, "на пружинках", 8, GREEN, "middle", "italic")
    for dx in (-40, -20, 0, 20, 40):
        s += line(cx + dx, cy + 16, cx + dx, cy + 34, BLUE, 2)
    for dx in (-30, -10, 10, 30):
        s += line(cx + dx, cy + 50, cx + dx, cy + 34, INK, 2)
    s += text(cx, cy + 64, "ємнісні гребінці", 8.5, INK, "middle", "italic")
    s += arrow(284, 150, 328, 150, INK, 1.6)
    s += rect(330, 112, 130, 76, fill="#eef7ef", stroke=GREEN, sw=1.5, rx=6)
    s += text(395, 140, "електроніка", 9.5, GREEN, "middle", "bold")
    s += text(395, 157, "зчитує ємність", 8, GREY, "middle", "italic")
    s += text(395, 173, "+ самотест", 8, GREY, "middle", "italic")
    s += arrow(480, 150, 540, 150, INK, 2)
    s += text(548, 155, "прискорення", 10, INK, "start", "bold")
    s += text(w / 2, 268, "прискорення зсуває вантаж → міняється ємність гребінців → електроніка це читає", 9.5, GREY, "middle", "italic")
    save("fig-33-0-3-adxl50.svg", s)


def fig_scale():
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Доброчесне коло масштабу", 14, INK, "middle", "bold")
    nodes = [("подушки|обов'язкові", 360, 80, "#9a7a1e"),
             ("масове|виробництво", 558, 165, BLUE),
             ("ціна й розмір|падають", 360, 250, GREEN),
             ("давач —|всюди", 162, 165, PURP)]
    for (lbl, x, y, col) in nodes:
        s += circle(x, y, 52, fill="#fbfbfb", stroke=col, w=2)
        parts = lbl.split("|")
        for j, p in enumerate(parts):
            s += text(x, y - 3 + j * 16, p, 10, col, "middle", "bold")
    s += arrow(408, 108, 518, 142, INK, 1.8)
    s += arrow(546, 210, 410, 238, INK, 1.8)
    s += arrow(312, 238, 176, 210, INK, 1.8)
    s += arrow(204, 122, 316, 92, INK, 1.8)
    s += text(w / 2, 282, "кожне нове застосування ще збільшує об'єм — і ще збиває ціну", 9.5, GREY, "middle", "italic")
    save("fig-33-0-4-scale.svg", s)


def fig_everywhere():
    w, h = 740, 270
    s = header(w, h)
    s += text(w / 2, 26, "З машини — у все: MEMS у споживчій електроніці", 13, INK, "middle", "bold")
    cx, cy = 130, 150
    s += circle(cx, cy, 54, fill="#eef3fb", stroke=BLUE, w=2.4)
    s += text(cx, cy - 6, "дешевий", 11, BLUE, "middle", "bold")
    s += text(cx, cy + 12, "MEMS-IMU", 11, BLUE, "middle", "bold")
    apps = [("смартфон", "поворот екрана, кроки"),
            ("дрон", "утримання в повітрі"),
            ("ігри (Wii)", "керування рухом"),
            ("фітнес-браслет", "лічильник кроків"),
            ("стабілізатор", "гасіння тремтіння")]
    bx, bw, bh, y0 = 330, 360, 34, 52
    for i, (t1, t2) in enumerate(apps):
        y = y0 + i * 40
        s += arrow(cx + 54, cy, bx - 6, y + bh / 2, GREY, 1.3)
        s += rect(bx, y, bw, bh, fill="#fbfbfb", stroke=PURP, sw=1.4, rx=6)
        s += text(bx + 12, y + 22, t1, 11, PURP, "start", "bold")
        s += text(bx + bw - 12, y + 22, t2, 9, GREY, "end", "italic")
    save("fig-33-0-5-everywhere.svg", s)


def fig_lesson():
    w, h = 760, 240
    s = header(w, h)
    s += text(w / 2, 26, "Як технологія стає масовою", 14.5, INK, "middle", "bold")
    y = 130
    s += line(50, y, 710, y, INK, 2)
    s += arrow(694, y, 722, y, INK, 2)
    events = [(150, "1982", "винахід", "«Кремній як механічний|матеріал» (Петерсен)", BLUE),
              (390, "1990-ті", "вбивча задача", "обов'язкові подушки|безпеки → ринок", "#9a7a1e"),
              (620, "2000-ні", "всюдисущість", "телефони, дрони, ігри|— давач за копійки", GREEN)]
    for (x, yr, t1, t2, col) in events:
        s += dot(x, y, 7, col)
        s += line(x, y - 6, x, y - 30, col, 1.4, dash="3,3")
        s += text(x, y - 50, yr, 13, col, "middle", "bold")
        s += text(x, y - 34, t1, 10, INK, "middle", "bold")
        s += line(x, y + 6, x, y + 24, col, 1.4, dash="3,3")
        for j, p in enumerate(t2.split("|")):
            s += text(x, y + 42 + j * 14, p, 8.5, GREY, "middle", "italic")
    s += text(w / 2, 214, "винахід сам не змінює світ — його витягує масова потреба, що оплачує серію", 10, GREY, "middle", "italic")
    save("fig-33-0-6-lesson.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §33.1 MEMS: машини розміром із порошинку
# ════════════════════════════════════════════════════════════════════════════

def fig_mems_scale():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Машина розміром із порошинку", 14, INK, "middle", "bold")
    s += circle(200, 150, 80, fill="#f5f0e0", stroke=GOLD, w=2)
    s += text(200, 250, "волосина (~70 мкм) у розрізі", 10, "#9a7a1e", "middle", "bold")
    mx, my = 200, 150
    s += poly([(mx - 22, my), (mx - 30, my - 5), (mx - 38, my + 5), (mx - 44, my)], GREEN, 1.2)
    s += poly([(mx + 22, my), (mx + 30, my - 5), (mx + 38, my + 5), (mx + 44, my)], GREEN, 1.2)
    s += rect(mx - 22, my - 10, 44, 20, fill="#cfe0f5", stroke=BLUE, sw=1.2, rx=2)
    s += text(mx, my + 4, "MEMS", 7.5, BLUE, "middle", "bold")
    s += text(470, 90, "для масштабу:", 10.5, INK, "start", "bold")
    s += text(470, 116, "• волосина  ~70 мкм", 10, GREY, "start")
    s += text(470, 138, "• порошинка  ~10–50 мкм", 10, GREY, "start")
    s += text(470, 160, "• MEMS-деталь  одиниці-десятки мкм", 10, GREY, "start")
    s += text(470, 188, "= справжня механіка,", 10, INK, "start", "bold")
    s += text(470, 206, "   тільки в тисячі разів дрібніша", 10, INK, "start", "bold")
    save("fig-33-1-1-scale.svg", s)


def fig_micromachining():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Поверхнева мікрообробка: нанести → сформувати → звільнити", 12.5, INK, "middle", "bold")

    def stack(x, y, sacrificial, released, lbl):
        out = text(x + 90, y - 48, lbl, 10, INK, "middle", "bold")
        out += rect(x, y, 180, 22, fill="#d8d8d8", stroke=INK, sw=1)
        out += text(x + 90, y + 16, "підкладка", 8, GREY, "middle")
        if sacrificial:
            out += rect(x, y - 14, 180, 14, fill="#f0e0c0", stroke=INK, sw=1)
            out += text(x + 90, y - 4, "жертовний", 7.5, "#9a7a1e", "middle")
        if released:
            out += rect(x + 20, y - 30, 38, 12, fill=INK)
            out += rect(x + 122, y - 30, 38, 12, fill=INK)
            out += rect(x + 50, y - 27, 80, 9, fill="#cfe0f5", stroke=BLUE, sw=1)
            out += text(x + 90, y - 34, "вільно звисає", 7.5, GREEN, "middle", "italic")
        elif sacrificial:
            out += rect(x + 40, y - 28, 100, 14, fill="#cfe0f5", stroke=BLUE, sw=1)
            out += text(x + 90, y - 18, "структурний", 7.5, BLUE, "middle")
        return out

    s += stack(60, 175, True, False, "1) жертовний шар")
    s += stack(270, 175, True, False, "2) структурний + форма")
    # step 2 needs the structural drawn; redo with structural:
    s += rect(310, 147, 100, 14, fill="#cfe0f5", stroke=BLUE, sw=1)
    s += text(360, 157, "структурний", 7.5, BLUE, "middle")
    s += stack(480, 175, False, True, "3) розчинити жертовний")
    s += arrow(244, 155, 266, 155, INK, 1.8)
    s += arrow(454, 155, 476, 155, INK, 1.8)
    s += text(w / 2, 244, "усе тими ж літографією й травленням, що й чипи → тисячі давачів на пластині", 9.5, GREY, "middle", "italic")
    save("fig-33-1-2-micromachining.svg", s)


def fig_proof_mass():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Серце MEMS: інерційна маса на пружинках", 13.5, INK, "middle", "bold")
    cx, cy = 360, 140
    s += rect(cx - 180, cy - 14, 16, 28, fill=INK)
    s += rect(cx + 164, cy - 14, 16, 28, fill=INK)

    def spring(x0, x1, y, col):
        n = 5
        pts = [(x0, y)]
        for i in range(1, n):
            xx = x0 + (x1 - x0) * i / n
            yy = y + (8 if i % 2 else -8)
            pts.append((xx, yy))
        pts.append((x1, y))
        return poly(pts, col, 1.8)

    s += spring(cx - 164, cx - 70, cy, GREEN)
    s += spring(cx + 70, cx + 164, cy, GREEN)
    s += rect(cx - 70, cy - 34, 140, 68, fill="#cfe0f5", stroke=BLUE, sw=2, rx=4)
    s += text(cx, cy + 5, "маса m", 13, BLUE, "middle", "bold")
    s += text(cx - 117, cy - 22, "пружина", 8, GREEN, "middle", "italic")
    s += text(cx + 117, cy - 22, "пружина", 8, GREEN, "middle", "italic")
    s += arrow(cx, cy + 62, cx + 80, cy + 62, RED, 2.2)
    s += text(cx + 88, cy + 66, "прискорення → сила", 10, RED, "start", "bold")
    s += arrow(cx, cy - 48, cx + 30, cy - 48, GREY, 1.4)
    s += text(cx + 34, cy - 45, "зсув ∝ силі", 9, GREY, "start", "italic")
    s += text(w / 2, 240, "F = ma зрівноважена пружиною → зсув маси прямо пропорційний прискоренню", 9.5, GREY, "middle", "italic")
    save("fig-33-1-3-proof-mass.svg", s)


def fig_comb():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Ємнісні гребінці: зсув маси міняє ємність", 13.5, INK, "middle", "bold")
    cx, cy = 360, 150
    s += rect(cx - 160, cy - 70, 320, 20, fill="#cfe0f5", stroke=BLUE, sw=1.5, rx=3)
    s += text(cx, cy - 57, "рухома маса", 9, BLUE, "middle", "bold")
    for i in range(-4, 5):
        x = cx + i * 32
        s += line(x, cy - 50, x, cy + 10, BLUE, 3)
    s += rect(cx - 160, cy + 50, 320, 20, fill="#e0e0e0", stroke=INK, sw=1.5, rx=3)
    s += text(cx, cy + 63, "нерухомі електроди", 9, INK, "middle", "bold")
    for i in range(-4, 5):
        x = cx + i * 32 + 16
        s += line(x, cy + 50, x, cy - 10, INK, 3)
    s += text(cx + 152, cy - 4, "C", 11, RED, "start", "bold")
    s += text(w / 2, 240, "кожна пара пальців — конденсатор; зсув міняє зазори → ємність; диференційно для чутливості", 9, GREY, "middle", "italic")
    s += text(w / 2, 262, "сотні пальців складають крихітний сигнал у помітний", 9.5, INK, "middle", "bold")
    save("fig-33-1-4-comb.svg", s)


def fig_platform():
    w, h = 740, 260
    s = header(w, h)
    s += text(w / 2, 26, "Одна технологія MEMS → ціла родина давачів", 13, INK, "middle", "bold")
    cx, cy = 130, 140
    s += circle(cx, cy, 56, fill="#eef7ef", stroke=GREEN, w=2.4)
    s += text(cx, cy - 6, "кремнієва", 10.5, GREEN, "middle", "bold")
    s += text(cx, cy + 12, "мікромеханіка", 10.5, GREEN, "middle", "bold")
    items = [("акселерометр", "маса від прискорення"),
             ("гіроскоп", "Коріоліс на вібрації"),
             ("давач тиску", "прогин мембрани"),
             ("мікрофон", "мембрана від звуку")]
    bx, bw, bh, y0 = 340, 370, 40, 52
    for i, (t1, t2) in enumerate(items):
        y = y0 + i * 44
        s += arrow(cx + 56, cy, bx - 6, y + bh / 2, GREEN, 1.3)
        s += rect(bx, y, bw, bh, fill="#fbfbfb", stroke=PURP, sw=1.4, rx=6)
        s += text(bx + 14, y + 25, t1, 11, PURP, "start", "bold")
        s += text(bx + bw - 14, y + 25, t2, 9, GREY, "end", "italic")
    save("fig-33-1-5-platform.svg", s)


def fig_mems_limits():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Сила й межі MEMS", 14.5, INK, "middle", "bold")
    s += rect(40, 52, 300, 40, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=8)
    s += text(190, 77, "СИЛА", 13, GREEN, "middle", "bold")
    s += rect(380, 52, 300, 40, fill="#fdf6f5", stroke=RED, sw=1.8, rx=8)
    s += text(530, 77, "МЕЖІ", 13, RED, "middle", "bold")
    strong = ["крихітні розміри", "копійчана ціна (пакетно)", "інтеграція з електронікою", "низьке енергоспоживання"]
    limits = ["слабкий сигнал → шум", "температурний дрейф", "зсув нуля (розкид)", "крихкість до ударів"]
    for i, (a, b) in enumerate(zip(strong, limits)):
        y = 120 + i * 34
        s += text(60, y, "✓ " + a, 11, INK, "start")
        s += text(400, y, "✗ " + b, 11, INK, "start")
    s += text(w / 2, 256, "кожна межа — тема §33.5; усі разом — причина фьюжну (§33.6)", 10, GREY, "middle", "italic")
    save("fig-33-1-6-strengths.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §33.2 Акселерометр: міряти прискорення
# ════════════════════════════════════════════════════════════════════════════

def fig_accel_operation():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Як працює акселерометр: прискорення зсуває масу", 13.5, INK, "middle", "bold")
    s += rect(120, 90, 300, 110, fill="none", stroke=INK, sw=1.5, rx=6)
    s += text(270, 84, "корпус давача", 9, GREY, "middle", "italic")
    s += arrow(120, 72, 200, 72, RED, 2.4)
    s += text(208, 76, "прискорення a →", 10, RED, "start", "bold")
    cx, cy = 290, 148
    s += poly([(150, cy), (165, cy - 7), (180, cy + 7), (195, cy)], GREEN, 1.6)
    s += poly([(cx + 60, cy), (cx + 75, cy - 7), (cx + 90, cy + 7), (cx + 105, cy)], GREEN, 1.6)
    s += rect(cx - 40, cy - 24, 80, 48, fill="#cfe0f5", stroke=BLUE, sw=1.8, rx=4)
    s += text(cx, cy + 4, "маса", 11, BLUE, "middle", "bold")
    s += arrow(cx, cy - 34, cx - 26, cy - 34, GREY, 1.4)
    s += text(cx - 30, cy - 30, "зсув", 8.5, GREY, "end", "italic")
    s += arrow(440, 148, 510, 148, INK, 2)
    s += text(518, 153, "a = k · зсув", 12, INK, "start", "bold")
    s += text(w / 2, 230, "інерція лишає масу позаду → зсув ∝ прискоренню → ємнісний зчитувач дає число", 9.5, GREY, "middle", "italic")
    save("fig-33-2-1-accel-operation.svg", s)


def fig_gravity_quirk():
    w, h = 740, 290
    s = header(w, h)
    s += text(w / 2, 26, "Дивина гравітації: у спокої акселерометр показує 1g, не 0", 12, INK, "middle", "bold")
    cases = [(130, "спокій на столі", "читає 1g", "стіл штовхає масу вгору", GREEN),
             (370, "вільне падіння", "читає 0", "нема опори — маса вільна", "#9a7a1e"),
             (610, "розгін угору a", "читає 1g + a", "опора тисне сильніше", BLUE)]
    for (x, title, reading, why, col) in cases:
        s += rect(x - 50, 92, 100, 80, fill="#fbfbfb", stroke=INK, sw=1.5, rx=6)
        s += text(x, 82, title, 10, col, "middle", "bold")
        s += rect(x - 22, 120, 44, 24, fill="#cfe0f5", stroke=BLUE, sw=1.2, rx=3)
        s += text(x, 136, "m", 9, BLUE, "middle", "bold")
        s += text(x, 196, reading, 12, col, "middle", "bold")
        s += text(x, 216, why, 8.5, GREY, "middle", "italic")
    s += text(w / 2, 250, "акселерометр НЕ відрізняє гравітацію від прискорення (принцип еквівалентності, Айнштайн)", 9, INK, "middle", "bold")
    s += text(w / 2, 272, "тож міряє не «координатне» прискорення, а власне (силу опори): спокій = опора проти g = 1g", 8.5, GREY, "middle", "italic")
    save("fig-33-2-2-gravity-quirk.svg", s)


def fig_tilt():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Нахил: вектор гравітації показує, де «низ»", 13.5, INK, "middle", "bold")
    cx, cy = 280, 140
    th = 25 * math.pi / 180
    ct, st = math.cos(th), math.sin(th)

    def rot(dx, dy):
        return (cx + dx * ct - dy * st, cy + dx * st + dy * ct)

    corners = [rot(-70, -30), rot(70, -30), rot(70, 30), rot(-70, 30)]
    s += polygon(corners, "#eef3fb", BLUE, 2)
    s += text(cx, cy + 4, "давач", 10, BLUE, "middle", "bold")
    xax = rot(96, 0)
    s += arrow(cx, cy, xax[0], xax[1], INK, 1.8)
    s += text(xax[0] + 8, xax[1] + 4, "X", 10, INK, "start", "bold")
    zax = rot(0, -92)
    s += arrow(cx, cy, zax[0], zax[1], INK, 1.8)
    s += text(zax[0] - 8, zax[1] - 2, "Z", 10, INK, "end", "bold")
    s += arrow(cx, cy, cx, cy + 92, RED, 2.2)
    s += text(cx + 6, cy + 88, "g (де «низ»)", 10, RED, "start", "bold")
    s += text(cx - 34, cy + 34, "θ", 11, GREEN, "middle", "bold")
    s += rect(470, 90, 230, 92, fill="#fbfbfb", stroke=GREEN, sw=1.5, rx=8)
    s += text(585, 116, "кут нахилу θ:", 10, GREEN, "middle", "bold")
    s += text(585, 142, "θ = atan2(aX, aZ)", 12, INK, "middle", "bold")
    s += text(585, 164, "з проєкцій g на осі давача", 8.5, GREY, "middle", "italic")
    s += text(w / 2, 258, "у спокої сталий вектор g завжди вказує вниз → за його проєкцією на осі знаємо нахил", 9.5, GREY, "middle", "italic")
    save("fig-33-2-3-tilt.svg", s)


def fig_mixed():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Біда: гравітація й рух у показі перемішані", 13, INK, "middle", "bold")
    x0, yc, pw = 70, 150, 580
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.0)

    def grav(x):
        return 0.5

    def motion(x):
        return 0.35 * math.sin(2 * math.pi * 4 * x) * math.exp(-((x - 0.5) ** 2) / 0.05)

    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * grav(k / 300.0)) for k in range(301)], "#caa24a", 1.6, dash="6,3")
    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * motion(k / 300.0)) for k in range(301)], BLUE, 1.4)
    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * (grav(k / 300.0) + motion(k / 300.0))) for k in range(301)], RED, 2.2)
    s += text(x0 + 10, yc - 40, "гравітація (стала)", 9, "#9a7a1e", "start", "bold")
    s += text(x0 + 0.38 * pw, yc + 52, "рух (динаміка)", 9, BLUE, "start", "bold")
    s += text(x0 + 0.74 * pw, yc - 48, "показ = СУМА", 9.5, RED, "start", "bold")
    s += text(w / 2, 236, "показ = гравітація + лінійне прискорення разом; без додаткових даних їх не розділити", 9.5, GREY, "middle", "italic")
    save("fig-33-2-4-mixed.svg", s)


def fig_3axis():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Три осі: вектор прискорення розкладений по X, Y, Z", 12.5, INK, "middle", "bold")
    cx, cy = 210, 150
    s += arrow(cx, cy, cx + 90, cy, RED, 2)
    s += text(cx + 96, cy + 4, "X", 11, RED, "start", "bold")
    s += arrow(cx, cy, cx, cy - 90, GREEN, 2)
    s += text(cx - 4, cy - 96, "Z", 11, GREEN, "end", "bold")
    s += arrow(cx, cy, cx - 60, cy + 50, BLUE, 2)
    s += text(cx - 66, cy + 58, "Y", 11, BLUE, "start", "bold")
    s += arrow(cx, cy, cx + 40, cy + 60, INK, 2.4)
    s += text(cx + 44, cy + 66, "g", 11, INK, "start", "bold")
    s += rect(420, 90, 270, 120, fill="#fbfbfb", stroke=INK, sw=1.4, rx=8)
    s += text(555, 114, "вихід (3 числа):", 10, INK, "middle", "bold")
    s += text(440, 140, "X:  +0.20 g", 11, RED, "start")
    s += text(440, 162, "Y:  −0.15 g", 11, BLUE, "start")
    s += text(440, 184, "Z:  +0.97 g", 11, GREEN, "start")
    s += text(575, 150, "діапазон ±2…±16 g", 9, GREY, "start", "italic")
    s += text(575, 170, "одиниці: g або м/с²", 9, GREY, "start", "italic")
    s += text(w / 2, 246, "три осі дають повний вектор; у спокої довжина = 1g, напрямок задає вертикаль", 9.5, GREY, "middle", "italic")
    save("fig-33-2-5-3axis.svg", s)


def fig_capabilities():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Що акселерометр може й чого не може", 13.5, INK, "middle", "bold")
    rows = [("нахил (де «низ»)", "✓ так", "коли нерухомий (сталий g)", GREEN),
            ("рух, удари, кроки", "✓ так", "динамічне прискорення", GREEN),
            ("положення (де я)", "✗ ні", "подвійне інтегрування дрейфує", RED),
            ("курс (північ)", "✗ ні", "g нічого не каже про азимут", RED)]
    y = 80
    for (cap, verdict, why, col) in rows:
        s += text(60, y, "• " + cap, 12, INK, "start", "bold")
        s += text(330, y, verdict, 12, col, "start", "bold")
        s += text(432, y, why, 9.5, GREY, "start", "italic")
        s += line(50, y + 12, 690, y + 12, FAINT, 1)
        y += 40
    s += text(w / 2, y + 8, "нахил і рух — так; положення й курс — ні → потрібні гіроскоп і магнітометр (фьюжн)", 9.5, GREY, "middle", "italic")
    save("fig-33-2-6-capabilities.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §33.3 Гіроскоп: міряти обертання
# ════════════════════════════════════════════════════════════════════════════

def fig_gyro_rate():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Гіроскоп міряє ШВИДКІСТЬ обертання (°/с), не кут", 13, INK, "middle", "bold")
    cx, cy = 175, 135
    s += circle(cx, cy, 48, fill="#eef3fb", stroke=BLUE, w=2)
    s += text(cx, cy + 4, "давач", 10, BLUE, "middle", "bold")
    arc = [(cx + 68 * math.cos(a), cy + 68 * math.sin(a)) for a in [(-2.4 + i * 0.12) for i in range(17)]]
    s += poly(arc, RED, 2.4)
    ex, ey = arc[-1]
    s += polygon([(ex, ey), (ex - 10, ey - 4), (ex - 3, ey + 9)], RED)
    s += text(cx, cy - 70, "обертання", 10, RED, "middle", "bold")
    s += arrow(cx + 70, cy, cx + 130, cy, INK, 2)
    s += rect(cx + 140, cy - 42, 260, 84, fill="#fbfbfb", stroke=INK, sw=1.4, rx=8)
    s += text(cx + 270, cy - 14, "вихід: ω = +120 °/с", 12, INK, "middle", "bold")
    s += text(cx + 270, cy + 8, "це швидкість, а не кут!", 9.5, GREY, "middle", "italic")
    s += text(cx + 270, cy + 28, "стоїть нерухомо → ω = 0", 9, GREY, "middle", "italic")
    s += text(w / 2, 230, "гіроскоп каже, ЯК ШВИДКО ви повертаєтесь, а не НА СКІЛЬКИ повернулись", 9.5, GREY, "middle", "italic")
    save("fig-33-3-1-gyro-rate.svg", s)


def fig_coriolis():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Ефект Коріоліса: обертання відхиляє вібрівну масу вбік", 12.5, INK, "middle", "bold")
    cx, cy = 300, 150
    s += rect(cx - 90, cy - 70, 180, 140, fill="none", stroke=INK, sw=1.4, rx=6)
    s += rect(cx - 30, cy - 16, 60, 32, fill="#cfe0f5", stroke=BLUE, sw=1.6, rx=4)
    s += text(cx, cy + 4, "маса", 9.5, BLUE, "middle", "bold")
    s += arrow(cx - 55, cy - 30, cx - 55, cy - 52, GREEN, 1.8)
    s += arrow(cx - 55, cy + 30, cx - 55, cy + 52, GREEN, 1.8)
    s += text(cx - 60, cy + 4, "вібрація", 8.5, GREEN, "end", "italic")
    s += text(cx, cy - 84, "обертання Ω", 10, RED, "middle", "bold")
    s += arrow(cx + 32, cy - 40, cx + 78, cy - 40, PURP, 2.2)
    s += text(cx + 82, cy - 36, "відхилення Коріоліса", 9.5, PURP, "start", "bold")
    s += rect(470, 100, 230, 90, fill="#fbfbfb", stroke=PURP, sw=1.5, rx=8)
    s += text(585, 126, "відхилення ∝ Ω", 11.5, INK, "middle", "bold")
    s += text(585, 150, "(швидкість обертання)", 9, GREY, "middle", "italic")
    s += text(585, 172, "міряють ємнісно → ω", 9.5, PURP, "middle", "bold")
    s += text(w / 2, 250, "масу постійно гойдають; коли давач обертається, сила Коріоліса штовхає її поперек —", 9, GREY, "middle", "italic")
    s += text(w / 2, 268, "і це поперечне відхилення прямо пропорційне швидкості обертання", 9, GREY, "middle", "italic")
    save("fig-33-3-2-coriolis.svg", s)


def fig_merrygoround():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Інтуїція Коріоліса: на каруселі м'яч «закручується»", 13, INK, "middle", "bold")
    cx, cy = 360, 162
    s += circle(cx, cy, 110, fill="#f7f7f0", stroke=GREY, w=2)
    arc = [(cx + 120 * math.cos(a), cy + 120 * math.sin(a)) for a in [(-1.1 + i * 0.09) for i in range(14)]]
    s += poly(arc, RED, 2)
    s += text(cx, cy - 130, "карусель обертається", 10, RED, "middle", "bold")
    s += dot(cx, cy, 5, INK)
    s += text(cx - 6, cy + 18, "кидаю прямо", 8.5, INK, "end", "italic")
    s += line(cx, cy, cx, cy - 105, GREY, 1.4, dash="5,4")
    s += text(cx - 6, cy - 96, "намір (прямо)", 8.5, GREY, "end", "italic")
    s += poly([(cx + 0.006 * t * t, cy - t) for t in range(0, 106, 4)], BLUE, 2.4)
    s += text(cx + 64, cy - 76, "насправді — крива", 9, BLUE, "start", "bold")
    s += text(w / 2, 256, "у системі, що обертається, прямий рух здається викривленим — це й «відчуває» гіроскоп", 9, GREY, "middle", "italic")
    save("fig-33-3-3-merrygoround.svg", s)


def fig_gyro_strength():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Сила гіроскопа: бачить те, що акселерометр — ні", 12.5, INK, "middle", "bold")
    items = [("незалежний від гравітації", "міряє обертання прямо, не плутає з g чи рухом", GREEN),
             ("бачить yaw (поворот навколо вертикалі)", "ту саму сліпу пляму акселерометра", GREEN),
             ("швидкий і чутливий", "ловить найрвучкіші повороти без затримки", GREEN)]
    y = 80
    for (t1, t2, col) in items:
        s += text(60, y, "✓ " + t1, 12.5, col, "start", "bold")
        s += text(82, y + 22, t2, 10, GREY, "start", "italic")
        y += 56
    s += text(w / 2, 236, "де акселерометр сліпне (рух, yaw) — гіроскоп бачить чудово", 10, INK, "middle", "bold")
    save("fig-33-3-4-gyro-strength.svg", s)


def fig_drift():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Слабкість: інтегрування зсуву → дрейф кута", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 210, 580, 150
    s += axes(x0, y0, pw + 10, ph + 10)
    s += text(x0 + pw + 6, y0 + 18, "час", 9, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "кут", 9, INK, "end", "bold")
    s += line(x0, y0, x0 + pw, y0, GREEN, 2, dash="6,3")
    s += text(x0 + 0.04 * pw, y0 - 8, "справжній кут (нерухомо): 0", 9, GREEN, "start", "bold")
    s += _plot_path(x0, y0, pw, ph, [(t / 100.0, 0.85 * (t / 100.0)) for t in range(101)], RED, 2.4)
    s += text(x0 + 0.58 * pw, y0 - 0.72 * ph, "оцінка кута «спливає»", 10, RED, "start", "bold")
    s += text(x0 + 0.58 * pw, y0 - 0.57 * ph, "= зсув · час", 9, GREY, "start", "italic")
    s += text(w / 2, 250, "навіть нерухомий гіроскоп через дрібний зсув нуля дає кут, що повільно росте без кінця", 9, GREY, "middle", "italic")
    save("fig-33-3-5-drift.svg", s)


def fig_complementary():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Дзеркало: гіроскоп і акселерометр доповнюють одне одного", 12, INK, "middle", "bold")
    s += rect(40, 52, 300, 36, fill="#eef3fb", stroke=BLUE, sw=1.6, rx=6)
    s += text(190, 75, "ГІРОСКОП", 12, BLUE, "middle", "bold")
    s += rect(380, 52, 300, 36, fill="#eef7ef", stroke=GREEN, sw=1.6, rx=6)
    s += text(530, 75, "АКСЕЛЕРОМЕТР", 12, GREEN, "middle", "bold")
    rows = [("✓ швидкий, точний у русі", "✗ повільний, бреше в русі"),
            ("✓ незалежний від гравітації", "✓ абсолютний (без дрейфу)"),
            ("✗ ДРЕЙФУЄ (інтегрування)", "✓ не дрейфує (сталий g)"),
            ("✓ бачить yaw", "✗ не бачить yaw")]
    y = 112
    for (g, a) in rows:
        s += text(50, y, g, 10.5, INK, "start")
        s += text(390, y, a, 10.5, INK, "start")
        y += 32
    s += text(w / 2, 246, "сила одного = слабкість іншого → їх зливають разом (§33.6, §34.3)", 10, INK, "middle", "bold")
    save("fig-33-3-6-complementary.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §33.4 Магнітометр: відчути сторони світу
# ════════════════════════════════════════════════════════════════════════════

def fig_mag_field():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Магнітометр міряє вектор магнітного поля → курс", 13, INK, "middle", "bold")
    cx, cy = 175, 138
    s += rect(cx - 50, cy - 40, 100, 80, fill="#eef3fb", stroke=BLUE, sw=2, rx=6)
    s += text(cx, cy + 4, "магнітометр", 9, BLUE, "middle", "bold")
    s += arrow(cx + 52, cy - 18, cx + 150, cy - 50, PURP, 2.4)
    s += text(cx + 156, cy - 52, "поле Землі B", 10, PURP, "start", "bold")
    cmx, cmy = 540, 138
    s += circle(cmx, cmy, 56, fill="#fbfbfb", stroke=INK, w=1.6)
    s += text(cmx, cmy - 40, "Пн", 9, RED, "middle", "bold")
    s += text(cmx, cmy + 48, "Пд", 9, GREY, "middle")
    s += text(cmx - 44, cmy + 4, "З", 9, GREY, "middle")
    s += text(cmx + 44, cmy + 4, "С", 9, GREY, "middle")
    s += arrow(cmx, cmy, cmx + 34, cmy - 22, RED, 2.2)
    s += text(cmx, cmy + 84, "курс (азимут)", 10, INK, "middle", "bold")
    s += text(w / 2, 232, "як компас: за напрямком поля Землі дає абсолютний курс — куди ви повернені", 9.5, GREY, "middle", "italic")
    save("fig-33-4-1-mag-field.svg", s)


def fig_earth_field():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Поле Землі занурюється в землю; курс дає ГОРИЗОНТАЛЬНА складова", 12, INK, "middle", "bold")
    gy = 195
    s += line(60, gy, 660, gy, INK, 2)
    s += text(64, gy + 18, "горизонт", 9, GREY, "start", "italic")
    fx0, fy0 = 250, 110
    s += arrow(fx0, fy0, fx0 + 180, fy0 + 80, PURP, 2.6)
    s += text(fx0 - 6, fy0 - 2, "повне поле B", 10, PURP, "end", "bold")
    s += arrow(fx0, fy0, fx0 + 180, fy0, GREEN, 2.2)
    s += text(fx0 + 186, fy0 + 4, "горизонтальна (→ курс)", 9.5, GREEN, "start", "bold")
    s += line(fx0 + 180, fy0, fx0 + 180, fy0 + 80, GREY, 1.4, dash="4,3")
    s += text(fx0 + 186, fy0 + 46, "вертикальна (нахил)", 8.5, GREY, "start", "italic")
    s += text(fx0 + 34, fy0 + 22, "кут нахилу", 8.5, PURP, "start", "italic")
    s += text(w / 2, 250, "поле «занурюється» в землю (нахил/inclination); для курсу беруть лише горизонтальну частину", 9, GREY, "middle", "italic")
    save("fig-33-4-2-earth-field.svg", s)


def fig_heading():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Курс із горизонтальних складових поля", 13.5, INK, "middle", "bold")
    cx, cy = 230, 155
    s += arrow(cx, cy, cx + 100, cy, RED, 2)
    s += text(cx + 106, cy + 4, "mX (північ давача)", 9, RED, "start", "bold")
    s += arrow(cx, cy, cx, cy - 100, GREEN, 2)
    s += text(cx - 4, cy - 106, "mY", 9, GREEN, "end", "bold")
    ang = 35 * math.pi / 180
    fx, fy = cx + 92 * math.cos(ang), cy - 92 * math.sin(ang)
    s += arrow(cx, cy, fx, fy, PURP, 2.4)
    s += text(fx + 4, fy - 4, "поле (гориз.)", 9, PURP, "start", "bold")
    s += text(cx + 46, cy - 12, "курс", 8.5, INK, "start", "italic")
    s += rect(450, 88, 244, 116, fill="#fbfbfb", stroke=PURP, sw=1.5, rx=8)
    s += text(572, 114, "курс = atan2(mY, mX)", 11.5, INK, "middle", "bold")
    s += text(572, 140, "+ нахил-компенсація (з аксель.)", 9, GREY, "middle", "italic")
    s += text(572, 162, "+ магнітне схилення", 9, GREY, "middle", "italic")
    s += text(572, 182, "(магнітна ≠ справжня північ)", 8.5, GREY, "middle", "italic")
    s += text(w / 2, 240, "кут горизонтального поля = курс; та щоб він був вірним, давач треба вирівняти", 9, GREY, "middle", "italic")
    save("fig-33-4-3-heading.svg", s)


def fig_mag_complement():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Три давачі — три орієнтири повної орієнтації", 13, INK, "middle", "bold")
    items = [("акселерометр", "→ де «низ»", "сталий вектор g (нахил)", GREEN),
             ("магнітометр", "→ де північ", "поле Землі (курс / yaw)", PURP),
             ("гіроскоп", "→ швидкі зміни", "миттєва кутова швидкість", BLUE)]
    bw, xs = 210, [30, 260, 490]
    for (x, (t1, t2, t3, col)) in zip(xs, items):
        s += rect(x, 70, bw, 120, fill="#fbfbfb", stroke=col, sw=1.8, rx=10)
        s += text(x + bw / 2, 100, t1, 12, col, "middle", "bold")
        s += text(x + bw / 2, 128, t2, 12, INK, "middle", "bold")
        s += text(x + bw / 2, 156, t3, 9, GREY, "middle", "italic")
    s += text(w / 2, 224, "низ (аксель) + північ (магніт) + швидкі зміни (гіро) = повна, надійна орієнтація", 9.5, INK, "middle", "bold")
    save("fig-33-4-4-complement.svg", s)


def fig_interference():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Біда магнітометра: будь-яке залізо й струм спотворюють поле", 12, INK, "middle", "bold")
    cx, cy = 200, 140
    s += rect(cx - 40, cy - 30, 80, 60, fill="#eef3fb", stroke=BLUE, sw=1.6, rx=5)
    s += text(cx, cy + 4, "магніт.", 9, BLUE, "middle", "bold")
    s += arrow(cx + 42, cy - 10, cx + 110, cy - 40, GREEN, 2, dash="5,3")
    s += text(cx + 116, cy - 42, "справжнє поле", 9, GREEN, "start")
    s += arrow(cx + 42, cy + 10, cx + 96, cy + 44, RED, 2.4)
    s += text(cx + 102, cy + 46, "спотворене!", 9.5, RED, "start", "bold")
    srcs = [("магніт динаміка", "#9a7a1e"), ("феритне залізо поряд", GREY), ("струм у дроті", RED), ("сталевий гвинт", GREY)]
    s += text(470, 80, "джерела спотворення:", 10, INK, "start", "bold")
    for i, (t, col) in enumerate(srcs):
        s += text(470, 106 + i * 26, "• " + t, 10, col, "start")
    s += text(w / 2, 238, "hard-iron (магніти) зсувають поле; soft-iron (залізо) спотворюють форму — і курс бреше", 9, GREY, "middle", "italic")
    save("fig-33-4-5-interference.svg", s)


def fig_calibration():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Калібрування «вісімкою»: вирівняти спотворене коло", 12.5, INK, "middle", "bold")
    bx, by = 200, 150
    s += text(bx, 70, "до калібрування", 10, RED, "middle", "bold")
    pts = [(bx + 30 + 52 * math.cos(a), by - 10 + 36 * math.sin(a)) for a in [i * 0.25 for i in range(26)]]
    s += poly(pts, RED, 2)
    s += dot(bx, by, 3, INK)
    s += text(bx, by + 76, "центр зміщений, форма овальна", 8.5, GREY, "middle", "italic")
    s += arrow(330, 150, 400, 150, INK, 2)
    s += text(365, 138, "вісімка", 8.5, GREY, "middle", "italic")
    ax, ay = 540, 150
    s += text(ax, 70, "після калібрування", 10, GREEN, "middle", "bold")
    pts2 = [(ax + 48 * math.cos(a), ay + 48 * math.sin(a)) for a in [i * 0.25 for i in range(26)]]
    s += poly(pts2, GREEN, 2)
    s += dot(ax, ay, 3, INK)
    s += text(ax, ay + 76, "коло, центр у нулі → курс вірний", 8.5, GREY, "middle", "italic")
    s += text(w / 2, 252, "обертаючи давач на всі боки, будують і виправляють спотворене поле: зсув + масштаб", 9, GREY, "middle", "italic")
    save("fig-33-4-6-calibration.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §33.5 Шум, зсув нуля, дрейф
# ════════════════════════════════════════════════════════════════════════════

def fig_three_errors():
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Три види похибки кожного давача", 14, INK, "middle", "bold")
    x0, yc, pw = 70, 150, 580
    s += line(x0, yc, x0 + pw, yc, FAINT, 1.0)
    true = 0.40
    s += line(x0, yc - true * 70, x0 + pw, yc - true * 70, GREEN, 2, dash="6,3")
    s += text(x0 + 4, yc - true * 70 - 6, "справжнє значення", 9, GREEN, "start", "bold")
    bias = 0.12

    def noise(t):
        return 0.06 * (math.sin(91 * t) + math.sin(157 * t + 1) + math.sin(213 * t + 2)) / 3

    def obs(t):
        return true + bias + 0.20 * t + noise(t)

    s += poly([(x0 + (k / 300.0) * pw, yc - 70 * obs(k / 300.0)) for k in range(301)], RED, 1.6)
    s += text(x0 + 0.5 * pw, yc - 70 * obs(0.55) - 14, "що читаємо насправді", 9.5, RED, "start", "bold")
    s += arrow(x0 + 26, yc - true * 70, x0 + 26, yc - 70 * (true + bias), "#9a7a1e", 1.6)
    s += text(x0 + 30, yc - 70 * (true + bias / 2), "зсув", 8, "#9a7a1e", "start", "bold")
    s += text(x0 + 0.84 * pw, yc - 70 * obs(0.95) + 16, "+ дрейф ↗", 8.5, PURP, "start", "italic")
    s += text(w / 2, 258, "справжнє + сталий ЗСУВ + повільний ДРЕЙФ + швидкий ШУМ = сирий показ", 9.5, GREY, "middle", "italic")
    save("fig-33-5-1-three-errors.svg", s)


def fig_err_noise():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Шум: випадкове тремтіння — усереднюється", 13.5, INK, "middle", "bold")
    x0, yc, pw = 70, 130, 580
    s += line(x0, yc, x0 + pw, yc, GREEN, 1.6, dash="6,3")
    s += text(x0 + 4, yc - 8, "справжнє (середнє)", 9, GREEN, "start", "bold")

    def noise(t):
        return 0.5 * (math.sin(91 * t) + math.sin(157 * t + 1) + math.sin(213 * t + 2) + math.sin(271 * t + 0.5)) / 4

    s += poly([(x0 + (k / 400.0) * pw, yc - 70 * noise(k / 400.0)) for k in range(401)], BLUE, 1.2)
    s += text(x0 + 0.5 * pw, yc + 60, "швидке, симетричне, нуль-середнє → фільтр прибирає (§30–32)", 9.5, GREY, "middle", "italic")
    s += text(w / 2, 226, "шум не зсуває правди — він навколо неї; усередни багато відліків, і він спаде як √N", 9.5, INK, "middle", "bold")
    save("fig-33-5-2-noise.svg", s)


def fig_err_bias():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Зсув нуля: стале зміщення — калібрується", 13.5, INK, "middle", "bold")
    x0, yc, pw = 70, 140, 580
    s += line(x0, yc, x0 + pw, yc, GREEN, 1.6, dash="6,3")
    s += text(x0 + 4, yc + 14, "справжнє: 0", 9, GREEN, "start", "bold")
    s += line(x0, yc - 50, x0 + pw, yc - 50, RED, 2.2)
    s += text(x0 + 4, yc - 56, "показ: зсунутий на сталу величину", 9, RED, "start", "bold")
    s += arrow(x0 + 0.5 * pw, yc, x0 + 0.5 * pw, yc - 50, "#9a7a1e", 1.8)
    s += arrow(x0 + 0.5 * pw, yc - 50, x0 + 0.5 * pw, yc, "#9a7a1e", 1.8)
    s += text(x0 + 0.5 * pw + 8, yc - 25, "зсув (bias)", 9.5, "#9a7a1e", "start", "bold")
    s += text(w / 2, 210, "стала помилка: гіроскоп «думає», що крутиться; акселерометр не рівно 1g", 9.5, GREY, "middle", "italic")
    s += text(w / 2, 230, "лік: виміряй у спокої й ВІДНІМИ (калібрування §28.6)", 10, INK, "middle", "bold")
    save("fig-33-5-3-bias.svg", s)


def fig_err_drift():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Дрейф: коли сам зсув повільно повзе", 13.5, INK, "middle", "bold")
    x0, yc, pw = 70, 140, 580
    s += line(x0, yc, x0 + pw, yc, GREEN, 1.6, dash="6,3")
    s += text(x0 + 4, yc + 14, "справжнє: 0", 9, GREEN, "start", "bold")

    def drift(t):
        return 0.55 * math.sin(2 * math.pi * 0.7 * t - 1) + 0.15 * math.sin(2 * math.pi * 2 * t)

    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * drift(k / 300.0) - 8) for k in range(301)], RED, 2.2)
    s += text(x0 + 0.52 * pw, yc - 60, "зсув повзе сам собою (час, температура)", 9.5, RED, "start", "bold")
    s += text(w / 2, 206, "не випадковий (фільтр не бере) і не сталий (калібрування не бере)", 9.5, GREY, "middle", "italic")
    s += text(w / 2, 228, "дрейф можна виправити ЛИШЕ зовнішнім орієнтиром → фьюжн (§33.6)", 10, INK, "middle", "bold")
    save("fig-33-5-4-drift.svg", s)


def fig_per_sensor():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Кожному давачу — своя головна біда", 13.5, INK, "middle", "bold")
    rows = [("Акселерометр", "шум + плутає рух із g", "абсолютний нахил (не дрейфує)", GREEN),
            ("Гіроскоп", "ДРЕЙФ (інтеграл зсуву)", "точний накоротко", BLUE),
            ("Магнітометр", "завади (залізо, струм)", "абсолютний курс", PURP)]
    y = 86
    for (nm, bad, good, col) in rows:
        s += text(60, y, nm, 12, col, "start", "bold")
        s += text(250, y - 8, "✗ " + bad, 10.5, RED, "start")
        s += text(250, y + 12, "✓ " + good, 10, GREEN, "start")
        s += line(50, y + 26, 690, y + 26, FAINT, 1)
        y += 52
    s += text(w / 2, 240, "у кожного — своя слабкість і своя сила; тому й рятує лише поєднання", 9.5, INK, "middle", "bold")
    save("fig-33-5-5-per-sensor.svg", s)


def fig_err_remedy():
    w, h = 720, 260
    s = header(w, h)
    s += text(w / 2, 26, "Кожній похибці — свої ліки", 14, INK, "middle", "bold")
    rows = [("ШУМ", "фільтрація (усереднення)", "Розділи 30–32", GREEN),
            ("ЗСУВ нуля", "калібрування (відняти)", "§28.6", BLUE),
            ("ДРЕЙФ", "зовнішній орієнтир → ФЬЮЖН", "§33.6", RED)]
    y = 86
    for (err, fix, ref, col) in rows:
        s += rect(50, y - 22, 150, 36, fill="#fbfbfb", stroke=col, sw=1.6, rx=6)
        s += text(125, y + 2, err, 12, col, "middle", "bold")
        s += arrow(206, y, 250, y, INK, 1.8)
        s += text(258, y + 2, fix, 11.5, INK, "start", "bold")
        s += text(258, y + 20, ref, 8.5, GREY, "start", "italic")
        y += 58
    s += text(w / 2, 244, "шум і зсув приборкуються поодинці; ДРЕЙФ — лише поєднанням давачів (наступна тема)", 9.5, INK, "middle", "bold")
    save("fig-33-5-6-remedy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §33.6 Чому потрібен фьюжн
# ════════════════════════════════════════════════════════════════════════════

def fig_comp_recap():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Похибки доповнюють одне одного — дзеркально", 13, INK, "middle", "bold")
    s += rect(50, 60, 290, 130, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=10)
    s += text(195, 88, "ГІРОСКОП", 12, BLUE, "middle", "bold")
    s += text(195, 114, "✓ швидкий, гладкий, точний накоротко", 9.5, GREEN, "middle")
    s += text(195, 138, "✗ ДРЕЙФУЄ надовго", 9.5, RED, "middle")
    s += text(195, 164, "= добрий на ВИСОКИХ частотах", 9, GREY, "middle", "italic")
    s += rect(380, 60, 290, 130, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=10)
    s += text(525, 88, "АКСЕЛЕРОМЕТР / МАГНІТОМЕТР", 10.5, GREEN, "middle", "bold")
    s += text(525, 114, "✓ абсолютний, без дрейфу", 9.5, GREEN, "middle")
    s += text(525, 138, "✗ шумить, бреше в русі / завадах", 9.5, RED, "middle")
    s += text(525, 164, "= добрий на НИЗЬКИХ частотах", 9, GREY, "middle", "italic")
    s += text(w / 2, 216, "сила одного — точно слабкість іншого: ідеальна пара для злиття", 10, INK, "middle", "bold")
    save("fig-33-6-1-complementary.svg", s)


def fig_fusion_idea():
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Ідея фьюжну: довіряй кожному в його силі", 13.5, INK, "middle", "bold")
    s += rect(40, 70, 200, 50, fill="#eef3fb", stroke=BLUE, sw=1.6, rx=8)
    s += text(140, 90, "гіроскоп", 11, BLUE, "middle", "bold")
    s += text(140, 108, "швидкі зміни (накоротко)", 8.5, GREY, "middle", "italic")
    s += rect(40, 150, 200, 50, fill="#eef7ef", stroke=GREEN, sw=1.6, rx=8)
    s += text(140, 170, "аксель + магніт", 11, GREEN, "middle", "bold")
    s += text(140, 188, "абсолютна правда (надовго)", 8.5, GREY, "middle", "italic")
    s += arrow(244, 95, 300, 128, INK, 1.8)
    s += arrow(244, 175, 300, 142, INK, 1.8)
    s += circle(330, 135, 28, fill="#fbfbfb", stroke=PURP, w=2)
    s += text(330, 141, "⊕", 16, PURP, "middle", "bold")
    s += text(330, 182, "злиття", 9, PURP, "middle", "bold")
    s += arrow(360, 135, 430, 135, INK, 2)
    s += rect(440, 108, 240, 54, fill="#f3eef7", stroke=PURP, sw=1.8, rx=8)
    s += text(560, 132, "оцінка орієнтації", 11, PURP, "middle", "bold")
    s += text(560, 150, "гладка + швидка + без дрейфу", 9, GREY, "middle", "italic")
    s += text(w / 2, 232, "гіроскоп веде кут миттєво; аксель/магніт повільно тягнуть його до істини — дрейф зникає", 9, GREY, "middle", "italic")
    save("fig-33-6-2-fusion-idea.svg", s)


def fig_freq_split():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Фьюжн — це частотний поділ (комплементарний фільтр)", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 70, 210, 580, 150
    s += arrow(x0, y0, x0, y0 - ph - 12, INK, 1.6)
    s += arrow(x0, y0, x0 + pw + 10, y0, INK, 1.6)
    s += text(x0 + pw + 8, y0 + 16, "частота →", 9, INK, "middle", "bold")
    s += text(x0 - 8, y0 - ph - 2, "вага", 9, INK, "end", "bold")
    s += _plot_path(x0, y0, pw, ph, [(i / 200.0, 1.0 / math.sqrt(1 + (i / 200.0 / 0.35) ** 6)) for i in range(201)], GREEN, 2.4)
    s += text(x0 + 0.06 * pw, y0 - 0.84 * ph, "аксель/магніт (НЧ)", 9.5, GREEN, "start", "bold")
    s += _plot_path(x0, y0, pw, ph, [(i / 200.0, 1.0 - 1.0 / math.sqrt(1 + (i / 200.0 / 0.35) ** 6)) for i in range(201)], BLUE, 2.4)
    s += text(x0 + 0.62 * pw, y0 - 0.84 * ph, "гіроскоп (ВЧ)", 9.5, BLUE, "start", "bold")
    s += text(w / 2, 250, "низькі частоти — від аксель/магніт (правда), високі — від гіроскопа (швидкість); разом = усе", 9, GREY, "middle", "italic")
    save("fig-33-6-3-freq-split.svg", s)


def fig_fusion_action():
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Фьюжн у дії: з двох поганих — одна гарна оцінка", 13, INK, "middle", "bold")
    x0, yc, pw = 70, 150, 580
    s += line(x0, yc, x0 + pw, yc, GREEN, 2, dash="6,3")
    s += text(x0 + 4, yc - 8, "справжній кут", 9, GREEN, "start", "bold")
    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * 0.85 * (k / 300.0)) for k in range(301)], RED, 1.8)
    s += text(x0 + 0.7 * pw, yc - 50 * 0.62, "гіро: спливає ↗", 9, RED, "start", "bold")

    def noise(t):
        return 0.28 * (math.sin(91 * t) + math.sin(157 * t + 1) + math.sin(213 * t + 2)) / 3

    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * noise(k / 300.0)) for k in range(301)], "#9bb0e0", 1.1)
    s += text(x0 + 0.04 * pw, yc + 44, "аксель: шумить", 9, BLUE, "start", "bold")
    s += poly([(x0 + (k / 300.0) * pw, yc - 50 * 0.04 * math.sin(2 * math.pi * 1.2 * k / 300.0)) for k in range(301)], PURP, 2.6)
    s += text(x0 + 0.3 * pw, yc - 22, "ФЬЮЖН: гладкий, без дрейфу", 9.5, PURP, "start", "bold")
    s += text(w / 2, 236, "гіроскоп спливає, акселерометр тремтить — а їхнє злиття тримається істини", 9.5, INK, "middle", "bold")
    save("fig-33-6-4-fusion-action.svg", s)


def fig_redundancy():
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 26, "Бонуси злиття: менше шуму й більше стійкості", 13, INK, "middle", "bold")
    s += rect(50, 64, 290, 120, fill="#eef7ef", stroke=GREEN, sw=1.8, rx=10)
    s += text(195, 92, "менше шуму", 11.5, GREEN, "middle", "bold")
    s += text(195, 118, "незалежні джерела", 9.5, GREY, "middle", "italic")
    s += text(195, 140, "усереднюються → чистіше", 9.5, INK, "middle")
    s += rect(380, 64, 290, 120, fill="#eef3fb", stroke=BLUE, sw=1.8, rx=10)
    s += text(525, 92, "більше стійкості", 11.5, BLUE, "middle", "bold")
    s += text(525, 118, "один збоїть (завада, удар)", 9.5, GREY, "middle", "italic")
    s += text(525, 140, "інші тримають оцінку", 9.5, INK, "middle")
    s += text(w / 2, 212, "кілька давачів — не лише точніше, а й надійніше: система переживає відмову одного", 9.5, INK, "middle", "bold")
    save("fig-33-6-5-redundancy.svg", s)


def fig_bridge():
    w, h = 740, 220
    s = header(w, h)
    s += text(w / 2, 26, "Місток у Розділ 34: від давачів до керування", 12.5, INK, "middle", "bold")
    blocks = [("3 давачі IMU", "аксель+гіро+магніт", GREY),
              ("ФЬЮЖН (AHRS)", "злиття → орієнтація", PURP),
              ("орієнтація", "кути / кватерніон", GREEN),
              ("ПІД-керування", "утримати, стабілізувати", BLUE)]
    bw, bh, by, xs = 160, 70, 80, [20, 200, 380, 560]
    for (x, (t1, t2, col)) in zip(xs, blocks):
        s += rect(x, by, bw, bh, fill="#fbfbfb", stroke=col, sw=1.8, rx=10)
        s += text(x + bw / 2, by + 32, t1, 11.5, col, "middle", "bold")
        s += text(x + bw / 2, by + 52, t2, 8.5, GREY, "middle", "italic")
    for i in range(3):
        s += arrow(xs[i] + bw, by + bh / 2, xs[i + 1] - 4, by + bh / 2, INK, 2)
    s += text(w / 2, 188, "саме для цього IMU й зводить три давачі — щоб дати апарату надійне чуття орієнтації", 9.5, GREY, "middle", "italic")
    save("fig-33-6-6-bridge.svg", s)


if __name__ == "__main__":
    # §33.0 Історія — MEMS і подушка безпеки
    fig_silicon_machining()
    fig_airbag()
    fig_adxl50()
    fig_scale()
    fig_everywhere()
    fig_lesson()
    # §33.1 MEMS: машини розміром із порошинку
    fig_mems_scale()
    fig_micromachining()
    fig_proof_mass()
    fig_comb()
    fig_platform()
    fig_mems_limits()
    # §33.2 Акселерометр
    fig_accel_operation()
    fig_gravity_quirk()
    fig_tilt()
    fig_mixed()
    fig_3axis()
    fig_capabilities()
    # §33.3 Гіроскоп
    fig_gyro_rate()
    fig_coriolis()
    fig_merrygoround()
    fig_gyro_strength()
    fig_drift()
    fig_complementary()
    # §33.4 Магнітометр
    fig_mag_field()
    fig_earth_field()
    fig_heading()
    fig_mag_complement()
    fig_interference()
    fig_calibration()
    # §33.5 Шум, зсув, дрейф
    fig_three_errors()
    fig_err_noise()
    fig_err_bias()
    fig_err_drift()
    fig_per_sensor()
    fig_err_remedy()
    # §33.6 Чому потрібен фьюжн
    fig_comp_recap()
    fig_fusion_idea()
    fig_freq_split()
    fig_fusion_action()
    fig_redundancy()
    fig_bridge()
    print("OK — фігури §33.0–§33.6 згенеровано в", OUT)
