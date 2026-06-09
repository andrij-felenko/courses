# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 6 — «Мова схем і вимірювання» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: історія до розділу — секція 0 (Рис. 6.0.N); теми — Рис. 6.M.k.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange"}


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


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _resistor(x, y, w=70, h=24, label="R"):
    out = rect(x, y - h / 2, w, h, "#fff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 8, label, 12.5, INK, "middle", "bold", "italic")
    return out


def _vresistor(cx, y0, y1, label="", lside="start"):
    out = rect(cx - 12, y0, 24, y1 - y0, "#fff", INK, 2, 3)
    if label:
        lx = cx + 18 if lside == "start" else cx - 18
        out += text(lx, (y0 + y1) / 2 + 4, label, 11.5, INK, lside, "bold", "italic")
    return out


def _battery(cx, cy, label="", anchor="end"):
    out = line(cx - 16, cy - 8, cx + 16, cy - 8, INK, 3)
    out += line(cx - 9, cy + 8, cx + 9, cy + 8, INK, 5)
    if label:
        lx = cx - 22 if anchor == "end" else cx + 22
        out += text(lx, cy + 4, label, 11.5, INK, anchor, "bold")
    return out


def _meter(cx, cy, letter, col=INK, r=24):
    out = circle(cx, cy, r, "#fff", col, 2.4)
    out += text(cx, cy + r * 0.28, letter, r * 0.95, col, "middle", "bold")
    return out


def _needle(cx, cy, deg, length, color=RED):
    a = math.radians(deg - 90)
    ex, ey = cx + length * math.cos(a), cy + length * math.sin(a)
    return line(cx, cy, ex, ey, color, 2.6) + circle(cx, cy, 3, color, color, 1)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 6 — гальванометр і вимірювальні прилади.  Рис. 6.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 6.0.1 — дослід Ерстеда ──────────────────────────────────────────────
def fig_oersted():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Іскра всього: струм відхиляє магнітну стрілку (Ерстед, 1820)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "виявилось, що електрика й магнетизм пов'язані — і це дало спосіб «побачити» струм",
              11.5, GREY, "middle", style="italic")
    # без струму
    s += text(210, 100, "Без струму", 13, GREY, "middle", "bold")
    s += line(110, 130, 310, 130, "#9aa7b4", 4)
    s += text(330, 134, "дріт", 10, GREY, "start")
    s += circle(210, 210, 46, "#f6f8fc", GREY, 1.6)
    s += polygon([(210, 168), (218, 210), (210, 252), (202, 210)], "#bcbcbc")
    s += polygon([(210, 168), (218, 210), (210, 210)], RED)
    s += text(210, 274, "стрілка вздовж (Пн–Пд)", 10, GREY, "middle", style="italic")
    # зі струмом
    s += text(620, 100, "Зі струмом", 13, RED, "middle", "bold")
    s += line(520, 130, 720, 130, "#9aa7b4", 4)
    s += arrow(580, 130, 660, 130, RED, 2.4)
    s += text(620, 118, "I", 11, RED, "middle", "bold", "italic")
    s += circle(620, 210, 46, "#fdecea", RED, 1.6)
    s += polygon([(578, 210), (620, 202), (662, 210), (620, 218)], "#bcbcbc")
    s += polygon([(578, 210), (620, 202), (620, 210)], RED)
    s += text(620, 274, "стрілка повертається ПОПЕРЕК", 10, RED, "middle", "bold")
    s += rect(140, 300, W - 280, 44, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 327, "Що більший струм — то сильніше відхилення. Ось він, перший спосіб ВИМІРЯТИ струм.",
              12, INK, "middle", "bold")
    save("fig-6-0-1-oersted.svg", s)


# ── Рис. 6.0.2 — рамковий гальванометр ───────────────────────────────────────
def fig_galvanometer():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Рамковий гальванометр: струм → поворот → стрілка", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "рамка зі струмом у полі магніту повертається; пружина врівноважує — кут показує струм",
              11, GREY, "middle", style="italic")
    # принцип ліворуч: магніт + рамка
    s += rect(110, 150, 40, 110, "#fdecea", RED, 2, 6)
    s += text(130, 210, "N", 16, RED, "middle", "bold")
    s += rect(300, 150, 40, 110, "#eaf0fb", BLUE, 2, 6)
    s += text(320, 210, "S", 16, BLUE, "middle", "bold")
    s += rect(195, 165, 60, 80, "#fff7e6", "#caa64a", 2.2, 4)
    s += text(225, 210, "рамка", 10, INK, "middle", "bold")
    s += arrow(225, 250, 225, 290, ORANGE, 2.2)
    s += text(225, 305, "струм I", 10, ORANGE, "middle", "bold")
    s += _circ_arrow(225, 205, 56, GREEN, -120, 60, 2.2)
    s += text(225, 130, "поворот", 10, GREEN, "middle", "bold")
    s += text(225, 340, "поле магніту × струм = обертальний момент", 9.5, GREY, "middle", style="italic")
    # циферблат праворуч
    cx, cy = 600, 250
    s += rect(490, 120, 220, 180, "#f6f8fc", INK, 1.8, 12)
    for d in range(-60, 61, 20):
        a = math.radians(d - 90)
        x1, y1 = cx + 80 * math.cos(a), cy + 80 * math.sin(a)
        x2, y2 = cx + 92 * math.cos(a), cy + 92 * math.sin(a)
        s += line(x1, y1, x2, y2, INK, 1.6)
    s += _needle(cx, cy, 28, 88, RED)
    s += text(cx, cy + 28, "0", 10, GREY, "middle")
    s += text(cx, 150, "шкала", 11, INK, "middle", "bold")
    s += text(cx, cy + 46, "кут ∝ струму", 10, GREY, "middle", style="italic")
    save("fig-6-0-2-galvanometer.svg", s)


# ── Рис. 6.0.3 — три прилади з гальванометра ─────────────────────────────────
def fig_three_meters():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "З гальванометра — амперметр, вольтметр, омметр", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "той самий чутливий механізм + проста добавка = три прилади (а разом — мультиметр)",
              11, GREY, "middle", style="italic")
    # амперметр: G + шунт
    s += text(160, 96, "Амперметр", 12.5, INK, "middle", "bold")
    s += _meter(160, 150, "G", GREEN, 20)
    s += line(110, 150, 140, 150, INK, 2)
    s += line(180, 150, 210, 150, INK, 2)
    s += line(110, 150, 110, 200, INK, 2)
    s += line(210, 150, 210, 200, INK, 2)
    s += rect(135, 192, 50, 16, "#d7d2c4", INK, 1.8, 3)
    s += text(160, 224, "+ ШУНТ (малий R, ∥)", 9.5, RED, "middle", "bold")
    s += text(160, 240, "для великих струмів (§4.7)", 9, GREY, "middle", style="italic")
    # вольтметр: G + послідовний R
    s += text(430, 96, "Вольтметр", 12.5, INK, "middle", "bold")
    s += line(360, 150, 390, 150, INK, 2)
    s += _resistor(390, 150, 50, 14, "")
    s += line(440, 150, 470, 150, INK, 2)
    s += _meter(495, 150, "G", GREEN, 20)
    s += line(515, 150, 545, 150, INK, 2)
    s += text(430, 224, "+ дод. R (великий, послід.)", 9.5, BLUE, "middle", "bold")
    s += text(430, 240, "V = I·R: міряє напругу", 9, GREY, "middle", style="italic")
    # омметр: G + батарея + R
    s += text(710, 96, "Омметр", 12.5, INK, "middle", "bold")
    s += _meter(680, 150, "G", GREEN, 20)
    s += line(700, 150, 730, 150, INK, 2)
    s += _battery(755, 150, "")
    s += line(660, 150, 660, 190, INK, 2)
    s += line(755, 162, 755, 190, INK, 2)
    s += line(660, 190, 755, 190, INK, 2)
    s += _term(660, 150, "")
    s += text(710, 224, "+ батарея + відомий R", 9.5, ORANGE, "middle", "bold")
    s += text(710, 240, "міряє опір (за струмом)", 9, GREY, "middle", style="italic")
    s += rect(180, 286, W - 360, 50, "#eef7f0", GREEN, 1.8, 10)
    s += text(W / 2, 308, "Три прилади в одному корпусі — це МУЛЬТИМЕТР (колись «AVO»: Ampere–Volt–Ohm).",
              12, INK, "middle", "bold")
    s += text(W / 2, 326, "Едвард Вестон зробив такі прилади точними й портативними (кінець 1880-х).",
              10, GREY, "middle", style="italic")
    save("fig-6-0-3-three-meters.svg", s)


def _term(x, y, label, lside="start"):
    out = circle(x, y, 4, "#fff", INK, 2)
    if label:
        lx = x + 10 if lside == "start" else x - 10
        out += text(lx, y + 4, label, 11, INK, lside, "bold")
    return out


# ── Рис. 6.0.4 — прилад завжди втручається в коло ────────────────────────────
def fig_loading():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Будь-який прилад трохи втручається в коло", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "тому амперметр роблять малоомним (послідовно), а вольтметр — високоомним (паралельно)",
              11, GREY, "middle", style="italic")
    # амперметр послідовно
    s += text(210, 100, "Амперметр — ПОСЛІДОВНО", 12.5, INK, "middle", "bold")
    s += line(90, 150, 120, 150, COPPER, 2.2)
    s += _meter(150, 150, "A", RED, 20)
    s += line(170, 150, 230, 150, COPPER, 2.2)
    s += _vresistor(230, 130, 190, "R", "start")
    s += line(90, 150, 90, 210, INK, 2.2)
    s += line(230, 190, 230, 210, INK, 2.2)
    s += line(90, 210, 230, 210, COPPER, 2.2)
    s += _battery(90, 180, "")
    s += text(210, 250, "мусить мати МАЛИЙ опір,", 10.5, RED, "middle", "bold")
    s += text(210, 268, "щоб не зменшити струм, який міряє", 10, GREY, "middle", style="italic")
    # вольтметр паралельно
    s += text(620, 100, "Вольтметр — ПАРАЛЕЛЬНО", 12.5, INK, "middle", "bold")
    s += line(500, 150, 560, 150, COPPER, 2.2)
    s += _vresistor(560, 130, 190, "R", "end")
    s += line(560, 190, 620, 190, COPPER, 2.2)
    s += line(500, 150, 500, 210, INK, 2.2)
    s += _battery(500, 180, "")
    s += line(500, 210, 620, 210, COPPER, 2.2)
    s += line(620, 150, 620, 210, COPPER, 2.2)
    s += _meter(690, 160, "V", BLUE, 20)
    s += line(620, 150, 690, 150, INK, 2)
    s += line(690, 150, 690, 140, INK, 2)
    s += line(620, 190, 690, 190, INK, 2)
    s += line(690, 180, 690, 190, INK, 2)
    s += text(620, 250, "мусить мати ВЕЛИКИЙ опір,", 10.5, BLUE, "middle", "bold")
    s += text(620, 268, "щоб не відбирати струм (§4.6)", 10, GREY, "middle", style="italic")
    s += rect(150, 300, W - 300, 44, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 327, "Виміряти — означає трохи змінити. Добрий прилад змінює якомога менше.",
              12, INK, "middle", "bold")
    save("fig-6-0-4-loading.svg", s)


def _circ_arrow(cx, cy, r, color, a0_deg, a1_deg, w=2.6):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} 1 {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


# ════════════════════════════════════════════════════════════════════════════
#  §6.1 — Навіщо принципова схема.  Рис. 6.1.k
# ════════════════════════════════════════════════════════════════════════════

def _led(x, y, size=22, color=INK, down=False):
    """Світлодіод: трикутник + катодна риска + дві стрілки світла. Горизонтальний (праворуч) або вертикальний (вниз)."""
    if not down:
        o = polygon([(x, y - size / 2), (x, y + size / 2), (x + size, y)], "#fff7e6", color, 2)
        o += line(x + size, y - size / 2, x + size, y + size / 2, color, 2.4)
        o += arrow(x + size * 0.4, y - size * 0.7, x + size * 0.7, y - size * 1.1, ORANGE, 1.6)
        o += arrow(x + size * 0.7, y - size * 0.6, x + size, y - size, ORANGE, 1.6)
    else:
        o = polygon([(x - size / 2, y), (x + size / 2, y), (x, y + size)], "#fff7e6", color, 2)
        o += line(x - size / 2, y + size, x + size / 2, y + size, color, 2.4)
        o += arrow(x + size * 0.7, y + size * 0.4, x + size * 1.1, y + size * 0.7, ORANGE, 1.6)
        o += arrow(x + size * 0.6, y + size * 0.7, x + size, y + size, ORANGE, 1.6)
    return o


# ── Рис. 6.1.1 — макет проти схеми ───────────────────────────────────────────
def fig61_photo_vs_schematic():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Те саме коло: плутанина дротів — і чиста схема", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "принципова схема показує ГОЛОВНЕ — що з чим з'єднано, відкинувши зайве",
              11.5, GREY, "middle", style="italic")
    # ліворуч: «макет»
    s += text(210, 96, "Як це виглядає наживо", 12.5, INK, "middle", "bold")
    s += rect(90, 120, 240, 180, "#eae6d8", "#b9b29a", 2, 10)
    for i in range(14):
        for j in range(5):
            s += circle(120 + i * 15, 150 + j * 30, 1.6, GREY, "none", 0)
    # компоненти й плутані дроти
    s += rect(150, 150, 40, 14, RED, INK, 1, 3)
    s += rect(230, 210, 14, 40, "#444", INK, 1, 3)
    s += polyline([(120, 165), (180, 200), (250, 160), (300, 210)], "#d23", 2.4)
    s += polyline([(140, 250), (200, 180), (270, 240), (310, 170)], "#27d", 2.4)
    s += polyline([(160, 280), (240, 150)], "#2a2", 2.4)
    s += text(210, 322, "де що — здогадайся…", 10.5, GREY, "middle", style="italic")
    # праворуч: схема
    s += text(640, 96, "Принципова схема", 12.5, GREEN, "middle", "bold")
    s += line(540, 150, 540, 260, INK, 2.2)
    s += _battery(540, 205, "")
    s += text(518, 208, "3 В", 10, RED, "end", "bold")
    s += line(540, 150, 700, 150, COPPER, 2.2)
    s += _resistor(590, 150, 60, 18, "R")
    s += line(700, 150, 740, 150, COPPER, 2.2)
    s += line(740, 150, 740, 175, COPPER, 2.2)
    s += _led(740, 195, 20, INK, down=True)
    s += line(740, 215, 740, 260, COPPER, 2.2)
    s += line(540, 260, 740, 260, COPPER, 2.2)
    s += text(640, 322, "одразу видно: батарея → R → світлодіод", 10.5, GREEN, "middle", "bold")
    save("fig-6-1-1-photo-vs-schematic.svg", s)


# ── Рис. 6.1.2 — три рівні опису ─────────────────────────────────────────────
def fig61_three_views():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 30, "Три рівні опису кола", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "від загального задуму до фізичної плати — кожен рівень для свого", 12, GREY, "middle", style="italic")
    # блок-схема
    s += text(150, 96, "Блок-схема", 12.5, BLUE, "middle", "bold")
    for i, lab in enumerate(["Жив-\nлення", "МК", "Давач"]):
        s += rect(70 + i * 60, 130, 50, 44, "#eaf0fb", BLUE, 1.8, 8)
        s += text(95 + i * 60, 156, lab.replace("\n", ""), 9.5, INK, "middle", "bold")
        if i < 2:
            s += arrow(120 + i * 60, 152, 130 + i * 60, 152, INK, 1.8)
    s += text(150, 210, "що з чим у цілому", 9.5, GREY, "middle", style="italic")
    s += arrow(290, 152, 330, 152, INK, 2.4)
    # принципова схема
    s += text(490, 96, "Принципова схема", 12.5, GREEN, "middle", "bold")
    s += line(400, 130, 400, 190, INK, 2)
    s += _battery(400, 160, "")
    s += line(400, 130, 470, 130, COPPER, 2)
    s += _resistor(420, 130, 44, 14, "R")
    s += line(470, 130, 470, 190, INK, 2)
    s += _vresistor(470, 145, 178, "")
    s += line(400, 190, 470, 190, COPPER, 2)
    s += text(490, 210, "точні компоненти й зв'язки", 9.5, GREY, "middle", style="italic")
    s += arrow(560, 152, 600, 152, INK, 2.4)
    # друкована плата
    s += text(740, 96, "Друкована плата", 12.5, INK, "middle", "bold")
    s += rect(650, 120, 180, 90, "#1f6f3b", "#0c3a1e", 2, 8)
    for px, py in [(680, 145), (720, 170), (770, 140), (800, 185), (700, 195)]:
        s += circle(px, py, 4, "#d9c36a", "#9c8a3a", 1)
    s += polyline([(680, 145), (720, 145), (720, 170)], "#d9c36a", 2)
    s += polyline([(770, 140), (800, 140), (800, 185)], "#d9c36a", 2)
    s += text(740, 232, "як це лежить на платі", 9.5, GREY, "middle", style="italic")
    s += rect(120, 256, W - 240, 40, "#f6f8fc", INK, 1.4, 10)
    s += text(W / 2, 281, "Принципова схема — посередині: вона про ЛОГІКУ кола, а не про задум загалом чи фізичне розташування.",
              11, INK, "middle", "bold")
    save("fig-6-1-2-three-views.svg", s)


# ── Рис. 6.1.3 — важливі зв'язки, не розташування ────────────────────────────
def fig61_topology():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Схема — про зв'язки, не про розташування", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "те саме коло, накреслене двічі по-різному, — одна й та сама схема (як топологія §4.1)",
              11, GREY, "middle", style="italic")
    # вигляд 1
    s += line(110, 120, 110, 230, INK, 2.2)
    s += _battery(110, 175, "")
    s += line(110, 120, 280, 120, COPPER, 2.2)
    s += _resistor(160, 120, 60, 16, "R₁")
    s += line(280, 120, 280, 230, INK, 2.2)
    s += _vresistor(280, 145, 205, "R₂", "start")
    s += line(110, 230, 280, 230, COPPER, 2.2)
    s += text(195, 270, "вигляд 1", 11, GREY, "middle", style="italic")
    s += text(410, 165, "≡", 32, INK, "middle", "bold")
    # вигляд 2 (інша форма, ті самі зв'язки)
    s += line(560, 120, 760, 120, COPPER, 2.2)
    s += _resistor(600, 120, 60, 16, "R₁")
    s += line(560, 120, 560, 230, INK, 2.2)
    s += _battery(560, 175, "")
    s += line(760, 120, 760, 230, INK, 2.2)
    s += _vresistor(760, 145, 205, "R₂", "end")
    s += line(560, 230, 760, 230, COPPER, 2.2)
    s += text(660, 270, "вигляд 2", 11, GREY, "middle", style="italic")
    s += text(W / 2, 300, "Доки з'єднання ті самі — це одне коло; малювати можна як зручно.", 11, INK, "middle", "bold")
    save("fig-6-1-3-topology.svg", s)


# ── Рис. 6.1.4 — анатомія схеми ──────────────────────────────────────────────
def fig61_anatomy():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Анатомія принципової схеми", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "із чого вона складається: символи, лінії-дроти, вузли, позначення й номінали",
              11.5, GREY, "middle", style="italic")
    # коло
    s += line(180, 150, 180, 280, INK, 2.4)
    s += _battery(180, 215, "")
    s += text(158, 218, "BT1", 10, INK, "end", "bold")
    s += text(158, 234, "3 В", 9, GREY, "end")
    s += line(180, 150, 420, 150, COPPER, 2.4)
    s += _resistor(250, 150, 70, 20, "")
    s += text(285, 128, "R1", 10.5, INK, "middle", "bold")
    s += text(285, 186, "330 Ω", 9.5, GREY, "middle")
    s += circle(420, 150, 4, INK, INK, 1)          # вузол
    s += line(420, 150, 540, 150, COPPER, 2.4)
    s += line(420, 150, 420, 280, COPPER, 2.4)
    s += _led(540, 170, 22, INK, down=True)
    s += text(566, 188, "VD1", 10, INK, "start", "bold")
    s += line(540, 150, 540, 170, COPPER, 2.4)
    s += line(540, 192, 540, 280, COPPER, 2.4)
    s += line(180, 280, 540, 280, COPPER, 2.4)
    # друга гілка від вузла
    s += _vresistor(420, 175, 255, "")
    s += text(444, 215, "R2", 10, INK, "start", "bold")
    # виноски
    s += arrow(300, 250, 270, 168, GREY, 1.4)
    s += text(305, 258, "символ компонента", 10, INK, "start", "bold")
    s += arrow(360, 110, 340, 148, GREY, 1.4)
    s += text(360, 104, "лінія = дріт (з'єднання)", 10, INK, "start", "bold")
    s += arrow(470, 110, 424, 146, GREY, 1.4)
    s += text(470, 104, "вузол (точка з'єднання)", 10, INK, "start", "bold")
    s += arrow(150, 120, 175, 148, GREY, 1.4)
    s += text(60, 116, "позначення +", 10, INK, "start", "bold")
    s += text(60, 130, "номінал", 10, INK, "start", "bold")
    s += rect(120, 320, W - 240, 40, "#f6f8fc", INK, 1.4, 10)
    s += text(W / 2, 345, "Позначення (R1, BT1, VD1) + номінали (330 Ω, 3 В) роблять схему однозначною для будь-кого.",
              10.5, INK, "middle", "bold")
    save("fig-6-1-4-anatomy.svg", s)


# ── Рис. 6.1.5 — чим хороша схема ────────────────────────────────────────────
def fig61_benefits():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Чому інженери говорять схемами", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "принципова схема — універсальна мова електроніки", 12, GREY, "middle", style="italic")
    items = [("Універсальна", "будь-який інженер світу її прочитає", BLUE, 160),
             ("Стисла", "ціла плата — на одному аркуші", GREEN, 410),
             ("Розкриває суть", "видно ФУНКЦІЮ, а не купу дротів", ORANGE, 660),
             ("Зручна спільно", "легко ділитися, аналізувати, шукати помилку", RED, 285),
             ("Готова до аналізу", "вузли й контури — як у Розділах 4–5", INK, 535)]
    for name, note, col, x in items[:3]:
        s += rect(x - 110, 90, 220, 90, "#f6f8fc", col, 1.8, 12)
        s += text(x, 122, name, 13, col, "middle", "bold")
        s += text(x, 150, note, 10, GREY, "middle")
    for name, note, col, x in items[3:]:
        s += rect(x - 110, 196, 220, 90, "#f6f8fc", col, 1.8, 12)
        s += text(x, 228, name, 13, col, "middle", "bold")
        s += text(x, 256, note, 9.5, GREY, "middle")
    save("fig-6-1-5-benefits.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.2 — Умовні позначення компонентів.  Рис. 6.2.k
# ════════════════════════════════════════════════════════════════════════════

def _s_res_box(cx, cy):
    o = line(cx - 30, cy, cx - 22, cy, INK, 2) + rect(cx - 22, cy - 9, 44, 18, "#fff", INK, 2, 2)
    return o + line(cx + 22, cy, cx + 30, cy, INK, 2)


def _s_res_zig(cx, cy):
    o = line(cx - 30, cy, cx - 20, cy, INK, 2)
    pts = [(cx - 20, cy)]
    for i, (dx, dy) in enumerate([(-14, -9), (-8, 9), (-2, -9), (4, 9), (10, -9), (16, 9)]):
        pts.append((cx + dx, cy + dy))
    pts += [(cx + 20, cy), (cx + 30, cy)]
    return o + polyline(pts, INK, 2)


def _s_cap(cx, cy):
    o = line(cx - 30, cy, cx - 5, cy, INK, 2) + line(cx - 5, cy - 12, cx - 5, cy + 12, INK, 2.4)
    o += line(cx + 5, cy - 12, cx + 5, cy + 12, INK, 2.4) + line(cx + 5, cy, cx + 30, cy, INK, 2)
    return o


def _s_cap_pol(cx, cy):
    o = line(cx - 30, cy, cx - 5, cy, INK, 2) + line(cx - 5, cy - 12, cx - 5, cy + 12, INK, 2.4)
    o += f'<path d="M {cx+7},{cy-12} Q {cx+1},{cy} {cx+7},{cy+12}" fill="none" stroke="{INK}" stroke-width="2.4"/>\n'
    o += line(cx + 7, cy, cx + 30, cy, INK, 2) + text(cx - 11, cy - 9, "+", 11, RED, "middle", "bold")
    return o


def _s_ind(cx, cy):
    o = line(cx - 30, cy, cx - 18, cy, INK, 2)
    for i in range(4):
        bx = cx - 18 + i * 9
        o += f'<path d="M {bx},{cy} q 4.5,-9 9,0" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    return o + line(cx + 18, cy, cx + 30, cy, INK, 2)


def _s_pot(cx, cy):
    return _s_res_box(cx, cy) + arrow(cx, cy + 17, cx, cy + 3, INK, 2)


def _s_diode(cx, cy):
    o = line(cx - 30, cy, cx - 10, cy, INK, 2)
    o += polygon([(cx - 10, cy - 11), (cx - 10, cy + 11), (cx + 8, cy)], "#fff", INK, 2)
    o += line(cx + 8, cy - 11, cx + 8, cy + 11, INK, 2.6) + line(cx + 8, cy, cx + 30, cy, INK, 2)
    return o


def _s_zener(cx, cy):
    o = line(cx - 30, cy, cx - 10, cy, INK, 2)
    o += polygon([(cx - 10, cy - 11), (cx - 10, cy + 11), (cx + 8, cy)], "#fff", INK, 2)
    o += polyline([(cx + 2, cy - 14), (cx + 8, cy - 11), (cx + 8, cy + 11), (cx + 14, cy + 14)], INK, 2.4)
    return o + line(cx + 8, cy, cx + 30, cy, INK, 2)


def _s_led_sym(cx, cy):
    o = _s_diode(cx, cy)
    o += arrow(cx + 2, cy - 13, cx + 8, cy - 20, ORANGE, 1.6)
    o += arrow(cx + 9, cy - 12, cx + 15, cy - 19, ORANGE, 1.6)
    return o


def _s_npn(cx, cy):
    o = circle(cx, cy, 16, "#fff", INK, 1.8) + line(cx - 24, cy, cx - 8, cy, INK, 2)
    o += line(cx - 8, cy - 9, cx - 8, cy + 9, INK, 2.6)
    o += line(cx - 8, cy - 4, cx + 9, cy - 12, INK, 2) + line(cx + 9, cy - 12, cx + 9, cy - 24, INK, 2)
    o += line(cx - 8, cy + 4, cx + 9, cy + 12, INK, 2) + line(cx + 9, cy + 12, cx + 9, cy + 24, INK, 2)
    o += polygon([(cx + 3, cy + 6), (cx + 9, cy + 12), (cx + 1, cy + 13)], INK)
    return o


def _s_pnp(cx, cy):
    o = circle(cx, cy, 16, "#fff", INK, 1.8) + line(cx - 24, cy, cx - 8, cy, INK, 2)
    o += line(cx - 8, cy - 9, cx - 8, cy + 9, INK, 2.6)
    o += line(cx - 8, cy - 4, cx + 9, cy - 12, INK, 2) + line(cx + 9, cy - 12, cx + 9, cy - 24, INK, 2)
    o += line(cx - 8, cy + 4, cx + 9, cy + 12, INK, 2) + line(cx + 9, cy + 12, cx + 9, cy + 24, INK, 2)
    o += polygon([(cx - 8, cy + 4), (cx - 1, cy + 3), (cx - 2, cy + 11)], INK)
    return o


def _s_mosfet(cx, cy):
    o = line(cx - 24, cy, cx - 11, cy, INK, 2) + line(cx - 11, cy - 13, cx - 11, cy + 13, INK, 2)
    o += line(cx - 4, cy - 13, cx - 4, cy + 13, INK, 2.6)
    o += line(cx - 4, cy - 9, cx + 11, cy - 9, INK, 2) + line(cx + 11, cy - 9, cx + 11, cy - 24, INK, 2)
    o += line(cx - 4, cy + 9, cx + 11, cy + 9, INK, 2) + line(cx + 11, cy + 9, cx + 11, cy + 24, INK, 2)
    o += arrow(cx - 4, cy, cx + 6, cy, INK, 1.6)
    return o


def _s_cell(cx, cy):
    o = line(cx - 30, cy, cx - 4, cy, INK, 2) + line(cx - 4, cy - 13, cx - 4, cy + 13, INK, 2)
    o += line(cx + 4, cy - 7, cx + 4, cy + 7, INK, 4) + line(cx + 4, cy, cx + 30, cy, INK, 2)
    o += text(cx - 10, cy - 10, "+", 10, RED, "middle", "bold")
    return o


def _s_battery(cx, cy):
    o = line(cx - 30, cy, cx - 12, cy, INK, 2) + line(cx - 12, cy - 13, cx - 12, cy + 13, INK, 2)
    o += line(cx - 5, cy - 7, cx - 5, cy + 7, INK, 4) + line(cx + 3, cy - 13, cx + 3, cy + 13, INK, 2)
    o += line(cx + 10, cy - 7, cx + 10, cy + 7, INK, 4) + line(cx + 10, cy, cx + 30, cy, INK, 2)
    return o


def _s_dc(cx, cy):
    o = circle(cx, cy, 15, "#fff", INK, 2) + line(cx - 8, cy - 3, cx + 8, cy - 3, INK, 2)
    o += line(cx - 8, cy + 4, cx + 8, cy + 4, INK, 1.2, "3,2")
    return o + line(cx - 30, cy, cx - 15, cy, INK, 2) + line(cx + 15, cy, cx + 30, cy, INK, 2)


def _s_ac(cx, cy):
    o = circle(cx, cy, 15, "#fff", INK, 2)
    o += f'<path d="M {cx-9},{cy} q 4.5,-9 9,0 q 4.5,9 9,0" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    return o + line(cx - 30, cy, cx - 15, cy, INK, 2) + line(cx + 15, cy, cx + 30, cy, INK, 2)


def _s_isrc(cx, cy):
    o = circle(cx, cy, 15, "#fff", INK, 2) + arrow(cx, cy + 8, cx, cy - 8, INK, 2)
    return o + line(cx - 30, cy, cx - 15, cy, INK, 2) + line(cx + 15, cy, cx + 30, cy, INK, 2)


def _s_switch(cx, cy):
    o = line(cx - 30, cy, cx - 12, cy, INK, 2) + circle(cx - 12, cy, 3, INK, INK, 1)
    o += line(cx - 12, cy, cx + 10, cy - 14, INK, 2.2) + circle(cx + 12, cy, 3, INK, INK, 1)
    return o + line(cx + 12, cy, cx + 30, cy, INK, 2)


def _s_button(cx, cy):
    o = line(cx - 30, cy, cx - 12, cy, INK, 2) + circle(cx - 12, cy, 3, INK, INK, 1)
    o += circle(cx + 12, cy, 3, INK, INK, 1) + line(cx - 13, cy - 11, cx + 13, cy - 11, INK, 2.2)
    o += line(cx, cy - 11, cx, cy - 20, INK, 2) + line(cx + 12, cy, cx + 30, cy, INK, 2)
    return o


def _s_fuse(cx, cy):
    o = line(cx - 30, cy, cx - 18, cy, INK, 2) + rect(cx - 18, cy - 7, 36, 14, "#fff", INK, 2, 7)
    o += line(cx - 18, cy, cx + 18, cy, INK, 1.6) + line(cx + 18, cy, cx + 30, cy, INK, 2)
    return o


def _s_ground(cx, cy):
    o = line(cx, cy - 18, cx, cy, INK, 2) + line(cx - 13, cy, cx + 13, cy, INK, 2.4)
    o += line(cx - 8, cy + 5, cx + 8, cy + 5, INK, 2.4) + line(cx - 3, cy + 10, cx + 3, cy + 10, INK, 2.4)
    return o


def _s_lamp(cx, cy):
    o = circle(cx, cy, 14, "#fff", INK, 2) + line(cx - 10, cy - 10, cx + 10, cy + 10, INK, 1.8)
    o += line(cx - 10, cy + 10, cx + 10, cy - 10, INK, 1.8)
    return o + line(cx - 30, cy, cx - 14, cy, INK, 2) + line(cx + 14, cy, cx + 30, cy, INK, 2)


def _s_speaker(cx, cy):
    o = rect(cx - 16, cy - 8, 10, 16, "#fff", INK, 2, 1)
    o += polygon([(cx - 6, cy - 8), (cx - 6, cy + 8), (cx + 12, cy + 17), (cx + 12, cy - 17)], "#fff", INK, 2)
    return o + line(cx - 30, cy, cx - 16, cy, INK, 2)


def _s_motor(cx, cy):
    o = circle(cx, cy, 15, "#fff", INK, 2) + text(cx, cy + 5, "M", 14, INK, "middle", "bold")
    return o + line(cx - 30, cy, cx - 15, cy, INK, 2) + line(cx + 15, cy, cx + 30, cy, INK, 2)


def _s_antenna(cx, cy):
    o = line(cx, cy + 16, cx, cy - 6, INK, 2) + line(cx, cy - 6, cx - 13, cy - 19, INK, 2)
    return o + line(cx, cy - 6, cx + 13, cy - 19, INK, 2)


def _grid(items, x0, y0, cols, cw=230, ch=120):
    o = ""
    for i, (fn, lab) in enumerate(items):
        r, c = divmod(i, cols)
        cx = x0 + c * cw + cw / 2
        cy = y0 + r * ch + ch / 2
        o += rect(cx - cw / 2 + 6, cy - ch / 2 + 6, cw - 12, ch - 12, "#f6f8fc", "#dcdcdc", 1.4, 8)
        o += fn(cx, cy - 12)
        o += text(cx, cy + ch / 2 - 14, lab, 10.5, INK, "middle", "bold")
    return o


# ── Рис. 6.2.1 — пасивні компоненти ──────────────────────────────────────────
def fig62_passives():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Абетка схеми (1): пасивні компоненти", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "резистор, конденсатор, котушка — символи, які зустрінете найчастіше", 12, GREY, "middle", style="italic")
    items = [(_s_res_box, "Резистор (IEC)"), (_s_res_zig, "Резистор (ANSI)"), (_s_pot, "Потенціометр"),
             (_s_cap, "Конденсатор"), (_s_cap_pol, "Електролітичний C (+)"), (_s_ind, "Котушка / дросель")]
    s += _grid(items, 60, 80, 3, 233, 130)
    save("fig-6-2-1-passives.svg", s)


# ── Рис. 6.2.2 — напівпровідники ─────────────────────────────────────────────
def fig62_semiconductors():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Абетка схеми (2): напівпровідники", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "діод проводить в один бік; транзистор — керований ключ/підсилювач", 12, GREY, "middle", style="italic")
    items = [(_s_diode, "Діод"), (_s_led_sym, "Світлодіод"), (_s_zener, "Стабілітрон"),
             (_s_npn, "Транзистор NPN"), (_s_pnp, "Транзистор PNP"), (_s_mosfet, "Польовий (MOSFET)")]
    s += _grid(items, 60, 80, 3, 233, 130)
    save("fig-6-2-2-semiconductors.svg", s)


# ── Рис. 6.2.3 — джерела й комутація ─────────────────────────────────────────
def fig62_sources_switches():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Абетка схеми (3): джерела й комутація", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "звідки береться енергія і чим коло вмикають та боронять", 12, GREY, "middle", style="italic")
    items = [(_s_cell, "Гальв. елемент"), (_s_battery, "Батарея"), (_s_dc, "Джерело DC"), (_s_ac, "Джерело AC"),
             (_s_isrc, "Джерело струму"), (_s_switch, "Вимикач"), (_s_button, "Кнопка"), (_s_fuse, "Запобіжник")]
    s += _grid(items, 50, 80, 4, 190, 130)
    save("fig-6-2-3-sources-switches.svg", s)


# ── Рис. 6.2.4 — «земля» й навантаження ──────────────────────────────────────
def fig62_ground_io():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Абетка схеми (4): «земля» та навантаження", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "спільна точка відліку й типові споживачі", 12, GREY, "middle", style="italic")
    items = [(_s_ground, "«Земля» (GND)"), (_s_lamp, "Лампа"), (_s_motor, "Мотор"),
             (_s_speaker, "Динамік"), (_s_antenna, "Антена")]
    s += _grid(items, 60, 90, 3, 233, 120)
    s += rect(120, 320, W - 240, 34, "#eef7f0", GREEN, 1.5, 8)
    s += text(W / 2, 342, "Символ «землі» — спільна точка відліку напруг; докладно про неї — у §6.4.",
              11, INK, "middle", "bold")
    save("fig-6-2-4-ground-io.svg", s)


# ── Рис. 6.2.5 — два стандарти ───────────────────────────────────────────────
def fig62_two_standards():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Два стандарти позначень — не лякайтеся", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "європейський (IEC) і американський (ANSI) символи означають те саме",
              12, GREY, "middle", style="italic")
    s += rect(90, 90, 300, 150, "#eaf0fb", BLUE, 1.6, 12)
    s += text(240, 116, "Резистор", 12.5, BLUE, "middle", "bold")
    s += _s_res_box(180, 160)
    s += text(180, 188, "IEC (прямокутник)", 9.5, GREY, "middle")
    s += _s_res_zig(310, 160)
    s += text(310, 188, "ANSI (зигзаг)", 9.5, GREY, "middle")
    s += text(240, 222, "те саме — резистор", 10, INK, "middle", "bold")
    s += rect(430, 90, 300, 150, "#eef7f0", GREEN, 1.6, 12)
    s += text(580, 116, "Конденсатор", 12.5, GREEN, "middle", "bold")
    s += _s_cap(520, 160)
    s += text(520, 188, "неполярний", 9.5, GREY, "middle")
    s += _s_cap_pol(650, 160)
    s += text(650, 188, "полярний (+)", 9.5, GREY, "middle")
    s += text(580, 222, "стежте за полярністю!", 10, RED, "middle", "bold")
    s += text(W / 2, 280, "Звикайте до обох наборів: у книжках і програмах трапляються і ті, і ті.",
              11, GREY, "middle", style="italic")
    save("fig-6-2-5-two-standards.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.3 — Вузли, з'єднання й перетини.  Рис. 6.3.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 6.3.1 — крапка = з'єднання ──────────────────────────────────────────
def fig63_dot_vs_cross():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Крапка вирішує все: з'єднано чи ні", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "жирна крапка на перетині = дроти з'єднані; немає крапки = просто перетинаються",
              11.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 50, FAINT, 1.4, "4,5")
    s += text(210, 110, "Із крапкою — З'ЄДНАНО", 13.5, GREEN, "middle", "bold")
    s += line(110, 200, 310, 200, INK, 2.4)
    s += line(210, 145, 210, 255, INK, 2.4)
    s += circle(210, 200, 6.5, INK, INK, 1)
    s += text(210, 290, "одна спільна точка (вузол)", 11, GREEN, "middle", "bold")
    s += text(610, 110, "Без крапки — НЕ з'єднано", 13.5, RED, "middle", "bold")
    s += line(510, 200, 710, 200, INK, 2.4)
    s += line(610, 145, 610, 255, INK, 2.4)
    s += text(610, 290, "дроти йдуть повз — різні вузли", 11, RED, "middle", "bold")
    save("fig-6-3-1-dot-vs-cross.svg", s)


# ── Рис. 6.3.2 — як показують перетин ────────────────────────────────────────
def fig63_hop():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 30, "Три способи показати перетин дротів", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "з'єднання — крапкою; непоєднаний перетин — просто навхрест або «містком»",
              11.5, GREY, "middle", style="italic")
    cy = 190
    # 1: з'єднання (крапка)
    s += text(160, 110, "З'єднано", 12.5, GREEN, "middle", "bold")
    s += line(80, cy, 240, cy, INK, 2.4)
    s += line(160, cy - 50, 160, cy + 50, INK, 2.4)
    s += circle(160, cy, 6.5, INK, INK, 1)
    s += text(160, 270, "крапка", 10, GREY, "middle")
    # 2: непоєднаний (навхрест)
    s += text(430, 110, "Не з'єднано (сучасно)", 12.5, RED, "middle", "bold")
    s += line(350, cy, 510, cy, INK, 2.4)
    s += line(430, cy - 50, 430, cy + 50, INK, 2.4)
    s += text(430, 270, "просто навхрест", 10, GREY, "middle")
    # 3: непоєднаний (місток)
    s += text(700, 110, "Не з'єднано («місток»)", 12.5, RED, "middle", "bold")
    s += line(700, cy - 50, 700, cy + 50, INK, 2.4)
    s += line(620, cy, 692, cy, INK, 2.4)
    s += f'<path d="M {692},{cy} A 8 8 0 0 1 {708},{cy}" fill="none" stroke="{INK}" stroke-width="2.4"/>\n'
    s += line(708, cy, 780, cy, INK, 2.4)
    s += text(700, 270, "дріт «перестрибує»", 10, GREY, "middle")
    save("fig-6-3-2-hop.svg", s)


# ── Рис. 6.3.3 — уникайте двозначності ───────────────────────────────────────
def fig63_ambiguous():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Уникайте двозначного 4-перехрестя", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "крапка на схрещенні чотирьох дротів читається погано — чи її не загубили?",
              11.5, GREY, "middle", style="italic")
    # ліворуч: 4-way з крапкою (погано)
    s += text(210, 110, "Так — двозначно", 13, RED, "middle", "bold")
    s += line(110, 200, 310, 200, INK, 2.4)
    s += line(210, 145, 210, 255, INK, 2.4)
    s += circle(210, 200, 6.5, INK, INK, 1)
    s += text(210, 290, "одна крапка на 4 дроти — ризик помилки", 10, RED, "middle")
    s += text(415, 200, "→", 30, INK, "middle", "bold")
    # праворуч: два Т (добре)
    s += text(630, 110, "Краще — два Т-з'єднання", 13, GREEN, "middle", "bold")
    s += line(530, 180, 730, 180, INK, 2.4)
    s += line(580, 180, 580, 255, INK, 2.4)
    s += circle(580, 180, 6, INK, INK, 1)
    s += line(530, 220, 730, 220, INK, 2.4)
    s += line(680, 220, 680, 145, INK, 2.4)
    s += circle(680, 220, 6, INK, INK, 1)
    s += text(630, 290, "кожне з'єднання однозначне", 10, GREEN, "middle", "bold")
    save("fig-6-3-3-ambiguous.svg", s)


# ── Рис. 6.3.4 — вузол = одна точка ──────────────────────────────────────────
def fig63_node():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Вузол — одна електрична точка, хоч як розкидана", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "усі виводи, сполучені дротом, — той самий вузол з одним потенціалом (як §4.1)",
              11.5, GREY, "middle", style="italic")
    # зелена шина = один вузол
    s += line(120, 130, 700, 130, GREEN, 4)
    for x in (180, 320, 460, 600):
        s += line(x, 130, x, 170, GREEN, 3)
        s += rect(x - 14, 170, 28, 40, "#fff", INK, 2, 3)
        s += circle(x, 130, 5, GREEN, GREEN, 1)
    s += line(120, 130, 120, 110, GREEN, 3)
    s += circle(120, 110, 5, GREEN, GREEN, 1)
    s += text(120, 100, "А", 12, GREEN, "middle", "bold")
    s += text(W / 2, 250, "Хоч до вузла А під'єднано чотири деталі в різних місцях —", 11.5, INK, "middle", "bold")
    s += text(W / 2, 272, "це ОДНА точка кола (один потенціал), бо все сполучено суцільним дротом.",
              11, GREY, "middle", style="italic")
    save("fig-6-3-4-node.svg", s)


# ── Рис. 6.3.5 — іменовані ланцюги ───────────────────────────────────────────
def _nettag(x, y, name, color=INK, left=False):
    w = 52
    if left:
        o = polygon([(x, y), (x - 10, y - 9), (x - w, y - 9), (x - w, y + 9), (x - 10, y + 9)], "#eef2fb", color, 1.6)
        o += text(x - w / 2 - 4, y + 4, name, 10.5, color, "middle", "bold")
    else:
        o = polygon([(x, y), (x + 10, y - 9), (x + w, y - 9), (x + w, y + 9), (x + 10, y + 9)], "#eef2fb", color, 1.6)
        o += text(x + w / 2 + 4, y + 4, name, 10.5, color, "middle", "bold")
    return o


def fig63_net_labels():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 30, "Іменовані ланцюги: з'єднання без дроту", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "однакова назва (мітка) означає одне коло — навіть якщо лінії не з'єднані",
              11.5, GREY, "middle", style="italic")
    # ліворуч: деталь із виводом +5В
    s += rect(120, 120, 60, 70, "#fff", INK, 2, 4)
    s += text(150, 160, "U1", 11, INK, "middle", "bold")
    s += line(180, 140, 230, 140, COPPER, 2.2)
    s += _nettag(230, 140, "+5В", RED)
    s += line(180, 175, 230, 175, COPPER, 2.2)
    s += _nettag(230, 175, "GND", BLUE)
    # праворуч: інша деталь із тими ж мітками
    s += rect(640, 120, 60, 70, "#fff", INK, 2, 4)
    s += text(670, 160, "U2", 11, INK, "middle", "bold")
    s += line(590, 140, 640, 140, COPPER, 2.2)
    s += _nettag(590, 140, "+5В", RED, left=True)
    s += line(590, 175, 640, 175, COPPER, 2.2)
    s += _nettag(590, 175, "GND", BLUE, left=True)
    # стрілки зв'язку
    s += arrow(296, 140, 528, 140, RED, 1.6, "5,4")
    s += text(410, 128, "та сама назва → з'єднано", 10, RED, "middle", "bold")
    s += arrow(296, 175, 528, 175, BLUE, 1.6, "5,4")
    s += rect(150, 240, W - 300, 60, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 264, "Так схему не захаращують довгими лініями: «+5В» тут і «+5В» там — це одне коло.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 286, "Особливо зручно для живлення (+5В, GND) і шин сигналів (напр. SDA, SCL).",
              10.5, GREY, "middle", style="italic")
    save("fig-6-3-5-net-labels.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.5 — Як читати схему.  Рис. 6.5.k
# ════════════════════════════════════════════════════════════════════════════

def _mcu_circuit():
    """Наскрізний приклад: МК, кнопка з підтяжкою на вході, LED з резистором на виході, розв'язувальний C."""
    o = line(80, 110, 740, 110, RED, 3)
    o += line(80, 300, 740, 300, INK, 3)
    o += _s_ground(120, 302)
    o += rect(330, 170, 150, 90, "#eef2fb", BLUE, 2, 8)
    o += text(405, 206, "МК", 15, BLUE, "middle", "bold")
    o += text(405, 228, "(контролер)", 9, INK, "middle")
    o += line(405, 170, 405, 110, COPPER, 2)
    o += line(405, 260, 405, 300, COPPER, 2)
    # ліворуч: підтяжка + кнопка
    o += line(200, 110, 200, 150, COPPER, 2)
    o += _vresistor(200, 150, 185, "")
    o += text(176, 170, "R↑", 9.5, INK, "end", "bold")
    o += line(200, 185, 200, 205, COPPER, 2)
    o += circle(200, 205, 3.5, INK, INK, 1)
    o += line(200, 205, 330, 205, COPPER, 2)
    o += text(258, 197, "вхід", 9, GREY, "middle")
    o += line(200, 205, 200, 224, COPPER, 2)
    o += circle(200, 226, 3, INK, INK, 1)
    o += circle(200, 252, 3, INK, INK, 1)
    o += line(187, 216, 213, 216, INK, 2.2)
    o += line(200, 216, 200, 209, INK, 2)
    o += line(200, 252, 200, 300, COPPER, 2)
    o += text(228, 244, "кнопка", 9, GREY, "start")
    # розв'язувальний конденсатор
    o += line(300, 110, 300, 182, COPPER, 2)
    o += line(286, 182, 314, 182, INK, 2.4)
    o += line(286, 192, 314, 192, INK, 2.4)
    o += line(300, 192, 300, 300, COPPER, 2)
    o += text(320, 190, "C", 9.5, INK, "start", "bold")
    # праворуч: вихід + R + LED
    o += line(480, 205, 510, 205, COPPER, 2)
    o += _resistor(510, 205, 55, 16, "")
    o += text(537, 195, "R", 9.5, INK, "middle", "bold")
    o += line(565, 205, 630, 205, COPPER, 2)
    o += text(525, 196, "вихід", 9, GREY, "middle")
    o += line(630, 205, 630, 226, COPPER, 2)
    o += polygon([(616, 226), (644, 226), (630, 248)], "#fff7e6", INK, 2)
    o += line(616, 248, 644, 248, INK, 2.4)
    o += arrow(636, 230, 644, 222, ORANGE, 1.4)
    o += line(630, 248, 630, 300, COPPER, 2)
    o += text(662, 240, "LED", 9.5, INK, "start", "bold")
    return o


# ── Рис. 6.5.1 — рецепт читання ──────────────────────────────────────────────
def fig65_recipe():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Рецепт читання будь-якої схеми", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "не хапайтеся за все одразу — рухайтеся за п'ятьма кроками", 12, GREY, "middle", style="italic")
    steps = [("1", "Живлення й земля", "знайди +V (угорі) і GND (внизу) — зорієнтуйся", RED),
             ("2", "Блоки", "виділи частини й що кожна РОБИТЬ", BLUE),
             ("3", "Потік сигналу", "простеж шлях: вхід → обробка → вихід", GREEN),
             ("4", "Вузол за вузлом", "читай з'єднання по одному, «зафарбовуючи» вузли", ORANGE),
             ("5", "Номінали", "звір значення — вони підказують призначення", INK)]
    yy = 92
    for n, t, d, col in steps:
        s += circle(95, yy + 24, 17, col, INK, 2)
        s += text(95, yy + 29, n, 14, "#fff", "middle", "bold")
        s += rect(125, yy, 660, 50, "#f6f8fc", col, 1.6, 10)
        s += text(145, yy + 22, t, 13, INK, "start", "bold")
        s += text(145, yy + 41, d, 11, GREY, "start")
        yy += 58
    save("fig-6-5-1-recipe.svg", s)


# ── Рис. 6.5.2 — спершу живлення ─────────────────────────────────────────────
def fig65_power_first():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Крок 1: спершу знайди живлення й землю", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "плюсова шина вгорі, земля внизу — це каркас, на якому тримається вся схема",
              11.5, GREY, "middle", style="italic")
    s += _mcu_circuit()
    s += text(760, 110, "+5 В", 12, RED, "end", "bold")
    s += text(560, 296, "GND", 12, INK, "end", "bold")
    s += arrow(770, 130, 745, 113, RED, 1.8)
    s += text(W / 2, 340, "Зорієнтувавшись по живленню, далі легко читати, що між шинами.", 11, GREY, "middle", style="italic")
    save("fig-6-5-2-power-first.svg", s)


# ── Рис. 6.5.3 — потік сигналу ───────────────────────────────────────────────
def fig65_signal_flow():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Крок 3: простеж сигнал зліва направо", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "вхід → обробка → вихід: так читається призначення кола", 12, GREY, "middle", style="italic")
    blocks = [(160, "ВХІД", "кнопка / давач", BLUE), (410, "ОБРОБКА", "контролер", GREEN),
              (660, "ВИХІД", "світлодіод / мотор", ORANGE)]
    for x, t, d, col in blocks:
        s += rect(x - 100, 130, 200, 90, "#f6f8fc", col, 2, 12)
        s += text(x, 168, t, 14, col, "middle", "bold")
        s += text(x, 192, d, 11, INK, "middle")
    s += arrow(265, 175, 305, 175, INK, 2.6)
    s += arrow(515, 175, 555, 175, INK, 2.6)
    s += text(285, 162, "сигнал", 9, GREY, "middle", style="italic")
    s += text(535, 162, "дія", 9, GREY, "middle", style="italic")
    s += text(W / 2, 270, "Більшість схем читаються як розповідь: щось приходить, обробляється, щось відбувається.",
              11, GREY, "middle", style="italic")
    save("fig-6-5-3-signal-flow.svg", s)


# ── Рис. 6.5.4 — упізнавані патерни ──────────────────────────────────────────
def fig65_patterns():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Крок 4: упізнавайте знайомі патерни", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "кілька «слів» схемної мови трапляються знову й знову", 12, GREY, "middle", style="italic")
    # дільник
    s += rect(60, 80, 350, 150, "#f6f8fc", INK, 1.4, 10)
    s += text(235, 104, "Дільник напруги", 12, BLUE, "middle", "bold")
    s += text(120, 130, "+V", 9.5, RED, "middle", "bold")
    s += line(120, 136, 120, 150, INK, 2)
    s += _vresistor(120, 150, 175, "")
    s += circle(120, 185, 3, GREEN, GREEN, 1)
    s += line(120, 185, 160, 185, COPPER, 2)
    s += text(172, 189, "V_вих", 9, GREEN, "start", "bold")
    s += line(120, 175, 120, 185, INK, 2)
    s += _vresistor(120, 185, 215, "")
    s += line(120, 215, 120, 222, INK, 2)
    s += _s_ground(120, 222)
    s += text(290, 165, "ділить напругу;", 9.5, GREY, "middle")
    s += text(290, 181, "читати давачі (§4.6)", 9.5, GREY, "middle")
    # струмообмеження
    s += rect(420, 80, 350, 150, "#f6f8fc", INK, 1.4, 10)
    s += text(595, 104, "Струмообмежувальний R", 12, GREEN, "middle", "bold")
    s += line(480, 150, 510, 150, COPPER, 2)
    s += _resistor(510, 150, 50, 14, "R")
    s += line(560, 150, 585, 150, COPPER, 2)
    s += polygon([(585, 140), (585, 160), (605, 150)], "#fff7e6", INK, 2)
    s += line(605, 140, 605, 160, INK, 2.4)
    s += line(605, 150, 640, 150, COPPER, 2)
    s += text(620, 178, "перед LED", 9.5, GREY, "middle")
    s += text(595, 200, "тримає струм безпечним (§3.7)", 9.5, GREY, "middle")
    # підтяжка
    s += rect(60, 245, 350, 145, "#f6f8fc", INK, 1.4, 10)
    s += text(235, 269, "Підтяжка (pull-up)", 12, ORANGE, "middle", "bold")
    s += text(120, 294, "+V", 9.5, RED, "middle", "bold")
    s += line(120, 300, 120, 312, INK, 2)
    s += _vresistor(120, 312, 342, "")
    s += line(120, 342, 120, 352, INK, 2)
    s += circle(120, 352, 3, INK, INK, 1)
    s += line(120, 352, 165, 352, COPPER, 2)
    s += text(177, 356, "→ вхід", 9, GREY, "start")
    s += text(300, 330, "тримає вхід у «1»,", 9.5, GREY, "middle")
    s += text(300, 346, "доки кнопка не притисне до «0»", 9.5, GREY, "middle")
    # розв'язка
    s += rect(420, 245, 350, 145, "#f6f8fc", INK, 1.4, 10)
    s += text(595, 269, "Розв'язувальний C", 12, RED, "middle", "bold")
    s += text(540, 294, "+V", 9.5, RED, "middle", "bold")
    s += line(540, 300, 540, 322, COPPER, 2)
    s += line(526, 322, 554, 322, INK, 2.4)
    s += line(526, 330, 554, 330, INK, 2.4)
    s += line(540, 330, 540, 352, COPPER, 2)
    s += _s_ground(540, 354)
    s += text(640, 322, "біля живлення мікросхеми;", 9.5, GREY, "middle")
    s += text(640, 338, "згладжує стрибки напруги", 9.5, GREY, "middle")
    save("fig-6-5-4-patterns.svg", s)


# ── Рис. 6.5.5 — наскрізний приклад ──────────────────────────────────────────
def fig65_worked():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Читаємо приклад: кнопка → МК → світлодіод", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "усі чотири патерни на одній схемі — прочитаймо її за рецептом", 11.5, GREY, "middle", style="italic")
    s += _mcu_circuit()
    # анотації
    s += arrow(150, 345, 196, 190, GREY, 1.4)
    s += text(150, 358, "R↑ тримає вхід у «1»", 9.5, INK, "middle", "bold")
    s += arrow(255, 345, 205, 250, GREY, 1.4)
    s += text(280, 358, "кнопка притискає вхід до «0»", 9.5, INK, "middle", "bold")
    s += arrow(300, 345, 300, 200, GREY, 1.4)
    s += text(330, 372, "C згладжує живлення МК", 9.5, INK, "middle", "bold")
    s += arrow(610, 345, 555, 210, GREY, 1.4)
    s += text(640, 358, "R обмежує струм LED", 9.5, INK, "middle", "bold")
    save("fig-6-5-5-worked.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.4 — «Земля» та шини живлення.  Рис. 6.4.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 6.4.1 — земля = спільний нуль ───────────────────────────────────────
def fig64_ground_reference():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "«Земля» — спільна точка відліку (0 В)", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "усі напруги на схемі міряють відносно землі; її потенціал — нуль за домовленістю",
              11.5, GREY, "middle", style="italic")
    x = 230
    s += text(x, 100, "+6 В", 11.5, RED, "middle", "bold")
    s += line(x, 108, x, 130, INK, 2.2)
    s += _vresistor(x, 130, 170, "R₁")
    s += circle(x, 180, 4, GREEN, GREEN, 1)
    s += text(x + 18, 184, "+4 В", 10.5, INK, "start", "bold")
    s += line(x, 170, x, 190, INK, 2.2)
    s += _vresistor(x, 190, 230, "R₂")
    s += circle(x, 240, 4, GREEN, GREEN, 1)
    s += text(x + 18, 244, "+2 В", 10.5, INK, "start", "bold")
    s += line(x, 230, x, 250, INK, 2.2)
    s += _vresistor(x, 250, 290, "R₃")
    s += line(x, 290, x, 310, INK, 2.2)
    s += _s_ground(x, 312)
    s += text(x, 340, "0 В", 11, GREEN, "middle", "bold")
    # пояснення
    s += rect(440, 110, 350, 200, "#f6f8fc", INK, 1.5, 12)
    s += text(615, 140, "«Напруга у вузлі» означає:", 12, INK, "middle", "bold")
    s += text(615, 162, "його потенціал ВІДНОСНО землі.", 11, GREY, "middle")
    s += text(460, 196, "• земля = 0 В (опорна точка)", 11, GREEN, "start", "bold")
    s += text(460, 222, "• «+4 В» = на 4 В вище землі", 11, INK, "start")
    s += text(460, 248, "• різниця двох вузлів — їхня", 11, INK, "start")
    s += text(475, 268, "напруга один відносно одного", 11, INK, "start")
    s += text(615, 298, "(згадайте §1.5: напруга — це різниця)", 9.5, GREY, "middle", style="italic")
    save("fig-6-4-1-ground-reference.svg", s)


# ── Рис. 6.4.2 — напруга завжди відносна ─────────────────────────────────────
def fig64_relative():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Напруга — завжди різниця: нуль обираєш сам", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "та сама батарея 9 В: куди поставиш «землю», такі й будуть числа вузлів",
              11.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 40, FAINT, 1.4, "4,5")
    # ліворуч: − на землю
    s += text(210, 104, "Земля на «−»", 13, GREEN, "middle", "bold")
    s += _battery(210, 200, "")
    s += text(186, 196, "9 В", 10.5, INK, "end", "bold")
    s += text(252, 165, "+9 В", 11, RED, "start", "bold")
    s += line(210, 232, 210, 258, INK, 2)
    s += _s_ground(210, 260)
    s += text(252, 235, "0 В", 11, GREEN, "start", "bold")
    # праворуч: + на землю
    s += text(610, 104, "Земля на «+»", 13, GREEN, "middle", "bold")
    s += _battery(610, 200, "")
    s += text(652, 165, "0 В", 11, GREEN, "start", "bold")
    s += line(610, 168, 610, 145, INK, 2)
    s += _s_ground(610, 145)
    s += text(652, 235, "−9 В", 11, BLUE, "start", "bold")
    s += text(W / 2, 320, "Різниця — завжди 9 В; змінюються лише «імена» вузлів. Тому нуль обирають там, де зручно.",
              11, INK, "middle", "bold")
    save("fig-6-4-2-relative.svg", s)


# ── Рис. 6.4.3 — шини живлення ───────────────────────────────────────────────
def fig64_rails():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Шини живлення: конвенція «згори вниз»", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "плюсову шину малюють угорі, землю — внизу; компоненти висять між ними",
              11.5, GREY, "middle", style="italic")
    s += line(110, 110, 710, 110, RED, 3.5)
    s += text(110, 100, "+5 В", 12, RED, "start", "bold")
    s += line(110, 290, 710, 290, INK, 3.5)
    s += _s_ground(160, 292)
    s += text(110, 282, "GND (0 В)", 12, INK, "start", "bold")
    # гілки між шинами
    s += line(280, 110, 280, 140, COPPER, 2)
    s += _vresistor(280, 140, 190, "R")
    s += line(280, 190, 280, 210, COPPER, 2)
    s += polygon([(266, 210), (294, 210), (280, 232)], "#fff7e6", INK, 2)
    s += line(266, 232, 294, 232, INK, 2.4)
    s += line(280, 232, 280, 290, COPPER, 2)
    s += text(310, 200, "світлодіод", 9.5, GREY, "start")
    s += line(480, 110, 480, 290, COPPER, 2)
    s += _vresistor(480, 175, 235, "наван-")
    s += rect(468, 175, 24, 60, "#fff", INK, 2, 3)
    s += text(506, 205, "U1", 10.5, INK, "start", "bold")
    s += arrow(610, 130, 610, 270, RED, 2, "5,5")
    s += text(625, 205, "струм тече вниз", 10, RED, "start", "bold")
    s += text(W / 2, 322, "Така стала розкладка робить будь-яку схему звичною з першого погляду.",
              11, GREY, "middle", style="italic")
    save("fig-6-4-3-rails.svg", s)


# ── Рис. 6.4.4 — різні «землі» ───────────────────────────────────────────────
def fig64_ground_types():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Три «землі»: не сплутайте символи", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "сигнальна (опорна 0 В), корпусна (металевий корпус), захисна (з'єднання з ґрунтом)",
              11, GREY, "middle", style="italic")
    # сигнальна
    cx = 180
    s += line(cx, 110, cx, 150, INK, 2.4)
    s += _s_ground(cx, 152)
    s += text(cx, 200, "Сигнальна", 12.5, INK, "middle", "bold")
    s += text(cx, 220, "опорний 0 В кола", 9.5, GREY, "middle")
    s += text(cx, 236, "(нею користуємось)", 9.5, GREEN, "middle", "bold")
    # корпусна
    cx = 410
    s += line(cx, 110, cx, 150, INK, 2.4)
    s += line(cx - 14, 150, cx + 14, 150, INK, 2.4)
    for i in range(4):
        s += line(cx - 12 + i * 8, 150, cx - 18 + i * 8, 160, INK, 1.8)
    s += text(cx, 200, "Корпусна (шасі)", 12.5, INK, "middle", "bold")
    s += text(cx, 220, "з'єднання з металевим", 9.5, GREY, "middle")
    s += text(cx, 236, "корпусом приладу", 9.5, GREY, "middle")
    # захисна / земля
    cx = 640
    s += line(cx, 110, cx, 150, INK, 2.4)
    s += line(cx - 16, 150, cx + 16, 150, INK, 2.6)
    s += line(cx - 10, 158, cx + 10, 158, INK, 2.6)
    s += line(cx - 4, 166, cx + 4, 166, INK, 2.6)
    s += text(cx, 200, "Захисна (Earth)", 12.5, INK, "middle", "bold")
    s += text(cx, 220, "справжнє з'єднання", 9.5, GREY, "middle")
    s += text(cx, 236, "із землею (безпека)", 9.5, GREY, "middle")
    s += rect(150, 268, W - 300, 38, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 291, "У нашій практиці «земля» — це майже завжди СИГНАЛЬНА: спільний 0 В кола.",
              11.5, INK, "middle", "bold")
    save("fig-6-4-4-ground-types.svg", s)


# ── Рис. 6.4.5 — однополярне vs двополярне ───────────────────────────────────
def fig64_split_supply():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Однополярне й двополярне живлення", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "просте коло — одна плюсова шина; для двополярних сигналів потрібен ще й «мінус»",
              11, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 40, FAINT, 1.4, "4,5")
    # однополярне
    s += text(210, 104, "Однополярне", 13, GREEN, "middle", "bold")
    s += line(110, 130, 310, 130, RED, 3)
    s += text(110, 122, "+5 В", 10.5, RED, "start", "bold")
    s += line(110, 230, 310, 230, INK, 3)
    s += _s_ground(160, 232)
    s += text(110, 222, "GND (0 В)", 10.5, INK, "start", "bold")
    s += text(210, 270, "мікроконтролери, логіка, LED", 9.5, GREY, "middle")
    # двополярне
    s += text(610, 104, "Двополярне (±)", 13, BLUE, "middle", "bold")
    s += line(510, 120, 710, 120, RED, 3)
    s += text(510, 112, "+12 В", 10.5, RED, "start", "bold")
    s += line(510, 175, 710, 175, INK, 3)
    s += _s_ground(560, 177)
    s += text(510, 167, "0 В", 10.5, INK, "start", "bold")
    s += line(510, 230, 710, 230, BLUE, 3)
    s += text(510, 247, "−12 В", 10.5, BLUE, "start", "bold")
    s += text(610, 282, "операційні підсилювачі, аудіо", 9.5, GREY, "middle")
    s += text(W / 2, 318, "Двополярне дозволяє сигналу гойдатися і вище, і нижче нуля (Модуль 2).",
              11, INK, "middle", "bold")
    save("fig-6-4-5-split-supply.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до §6.6 — Едвард Вестон і точні прилади.  Рис. 6.6і.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 6.6і.1 — портативний прилад Вестона ─────────────────────────────────
def fig_weston_meter():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Прилад Вестона: точний, портативний, із прямою шкалою", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "постійний магніт усередині — байдуже до земного поля; шкала прямо у вольтах",
              11.5, GREY, "middle", style="italic")
    # корпус приладу
    s += rect(250, 90, 320, 230, "#f0f2f5", "#9aa3ad", 2.2, 14)
    cx, cy = 410, 250
    # дуга-шкала
    for d in range(-60, 61, 15):
        a = math.radians(d - 90)
        x1, y1 = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
        x2, y2 = cx + 135 * math.cos(a), cy + 135 * math.sin(a)
        s += line(x1, y1, x2, y2, INK, 1.6)
    for d, lab in [(-60, "0"), (0, "5"), (60, "10")]:
        a = math.radians(d - 90)
        s += text(cx + 150 * math.cos(a), cy + 150 * math.sin(a) + 4, lab, 11, INK, "middle", "bold")
    s += _needle(cx, cy, 20, 130, RED)
    s += text(cx, cy - 20, "ВОЛЬТИ", 12, INK, "middle", "bold")
    # магніт усередині (натяк)
    s += rect(330, 270, 24, 36, "#fdecea", RED, 1.6, 3)
    s += text(342, 293, "N", 11, RED, "middle", "bold")
    s += rect(466, 270, 24, 36, "#eaf0fb", BLUE, 1.6, 3)
    s += text(478, 293, "S", 11, BLUE, "middle", "bold")
    s += rect(388, 276, 44, 26, "#fff7e6", "#caa64a", 1.6, 3)
    s += text(410, 293, "рамка", 8.5, INK, "middle")
    # виноски
    s += arrow(150, 150, 332, 285, GREY, 1.4)
    s += text(150, 140, "постійний магніт →", 10, INK, "start", "bold")
    s += text(150, 156, "не боїться земного поля", 9.5, GREY, "start")
    s += arrow(660, 150, 500, 195, GREY, 1.4)
    s += text(665, 146, "пряма шкала у вольтах", 10, INK, "start", "bold")
    s += text(665, 162, "→ читаєш без обчислень", 9.5, GREY, "start")
    save("fig-6-6i-1-weston-meter.svg", s)


# ── Рис. 6.6і.2 — стабільність сплаву ────────────────────────────────────────
def fig_alloy_stability():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Таємниця точності: сплав, що не «пливе» від тепла", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "опір приладу мусить лишатися сталим; манганін майже не змінює його з температурою (§3.4)",
              11, GREY, "middle", style="italic")
    ox, oy = 130, 320
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += text(ox - 8, 92, "опір R", 11.5, INK, "end")
    s += arrow(ox, oy, 700, oy, INK, 2)
    s += text(706, oy + 4, "температура", 11.5, INK, "start")
    # звичайний метал — росте
    s += polyline([(ox, 250), (680, 130)], RED, 3)
    s += text(560, 130, "звичайний метал (мідь): R росте", 10.5, RED, "middle", "bold")
    # манганін — майже плоский
    s += polyline([(ox, 250), (680, 244)], GREEN, 3)
    s += text(560, 262, "манганін: R майже сталий", 10.5, GREEN, "middle", "bold")
    s += rect(150, 336, W - 300, 38, "#eef7f0", GREEN, 1.5, 8)
    s += text(W / 2, 359, "Прилад точний лише тоді, коли його внутрішні опори не змінюються — звідси спеціальні сплави.",
              11, INK, "middle", "bold")
    save("fig-6-6i-2-alloy-stability.svg", s)


# ── Рис. 6.6і.3 — еталон вольта ──────────────────────────────────────────────
def fig_standard_cell():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Нормальний елемент Вестона — еталон вольта", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "хімічна комірка з надзвичайно стабільною, відтворюваною напругою",
              11.5, GREY, "middle", style="italic")
    # H-подібна комірка
    s += rect(250, 120, 36, 150, "#dbe6f5", BLUE, 2, 6)
    s += rect(380, 120, 36, 150, "#dbe6f5", BLUE, 2, 6)
    s += rect(286, 230, 94, 28, "#dbe6f5", BLUE, 2, 6)
    s += rect(254, 250, 28, 18, "#c9c9c9", "#888", 1.5, 2)
    s += rect(384, 250, 28, 18, "#e8d5a8", "#b89a5e", 1.5, 2)
    s += line(268, 120, 268, 95, INK, 2)
    s += line(398, 120, 398, 95, INK, 2)
    s += _term(268, 95, "+", "end")
    s += _term(398, 95, "−")
    s += text(333, 300, "ртуть / кадмій (схематично)", 9.5, GREY, "middle", style="italic")
    s += rect(500, 120, 290, 150, "#eef7f0", GREEN, 1.8, 12)
    s += text(645, 150, "1.0183 В при 20 °C", 16, GREEN, "middle", "bold")
    s += text(520, 184, "• напруга стала роками", 11, INK, "start")
    s += text(520, 208, "• відтворювана будь-де", 11, INK, "start")
    s += text(520, 232, "• «лінійка», якою звіряли", 11, INK, "start")
    s += text(535, 252, "всі вольтметри світу", 11, INK, "start")
    save("fig-6-6i-3-standard-cell.svg", s)


# ── Рис. 6.6і.4 — спадщина Вестона ───────────────────────────────────────────
def fig_weston_legacy():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 30, "Спадщина Вестона", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "стабільні прилади та еталон, що пережили десятиліття", 12, GREY, "middle", style="italic")
    # еталон вольта
    s += rect(60, 90, 230, 180, "#f6f8fc", BLUE, 1.8, 12)
    s += text(175, 116, "Еталон вольта", 12.5, BLUE, "middle", "bold")
    s += text(175, 162, "В", 40, BLUE, "middle", "bold")
    s += text(175, 210, "визначав вольт", 10, INK, "middle", "bold")
    s += text(175, 228, "близько 70 років", 10, GREY, "middle")
    # фотоекспонометр
    s += rect(315, 90, 230, 180, "#f6f8fc", ORANGE, 1.8, 12)
    s += text(430, 116, "Фотоекспонометр", 12.5, ORANGE, "middle", "bold")
    s += rect(390, 140, 80, 60, "#fff", INK, 2, 6)
    s += circle(410, 170, 12, "#fff7e6", INK, 1.6)
    s += _needle(450, 178, 30, 22, RED)
    s += text(430, 226, "виміряти світло —", 10, INK, "middle", "bold")
    s += text(430, 244, "теж рамковий прилад", 10, GREY, "middle")
    # рамковий механізм донині
    s += rect(570, 90, 230, 180, "#f6f8fc", GREEN, 1.8, 12)
    s += text(685, 116, "Рамковий механізм", 12.5, GREEN, "middle", "bold")
    s += circle(685, 175, 34, "#fff", INK, 2)
    s += _needle(685, 188, 35, 36, RED)
    s += text(685, 232, "у кожному стрілковому", 10, INK, "middle", "bold")
    s += text(685, 250, "приладі донині", 10, GREY, "middle")
    save("fig-6-6i-4-legacy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.6 — Мультиметр: що і як він міряє.  Рис. 6.6.k
# ════════════════════════════════════════════════════════════════════════════

def _probe(x1, y1, x2, y2, color):
    o = line(x1, y1, x2, y2, color, 2.6)
    o += circle(x2, y2, 3.5, color, color, 1)
    return o


# ── Рис. 6.6.1 — огляд мультиметра ───────────────────────────────────────────
def fig66_overview():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Мультиметр: один прилад на V, A, Ω (і не тільки)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "перемикач обирає режим; щупи — червоний у «+», чорний у COM (земля)",
              11.5, GREY, "middle", style="italic")
    s += rect(300, 80, 240, 290, "#f0f2f5", "#9aa3ad", 2.2, 16)
    s += rect(330, 100, 180, 56, "#1c2b1c", INK, 2, 6)
    s += text(420, 140, "5.00 V", 26, "#7CFC7C", "middle", "bold")
    # коло-перемикач
    s += circle(420, 235, 60, "#fff", INK, 2.4)
    s += circle(420, 235, 6, INK, INK, 1)
    modes = [("V⎓", -90), ("V~", -45), ("Ω", 0), ("A", 45), ("•))", 90), ("OFF", 180)]
    for lab, deg in modes:
        a = math.radians(deg)
        lx, ly = 420 + 74 * math.cos(a), 235 + 74 * math.sin(a)
        s += text(lx, ly + 4, lab, 11, INK, "middle", "bold")
        tx, ty = 420 + 48 * math.cos(a), 235 + 48 * math.sin(a)
        s += line(420 + 14 * math.cos(a), 235 + 14 * math.sin(a), tx, ty, "#cfcfcf", 1.4)
    s += line(420, 235, 420 + 44 * math.cos(math.radians(-90)), 235 + 44 * math.sin(math.radians(-90)), RED, 3)
    # гнізда
    for jx, lab, col in [(355, "COM", INK), (420, "VΩmA", RED), (485, "10A", RED)]:
        s += circle(jx, 348, 8, "#fff", col, 2)
        s += text(jx, 368, lab, 8.5, col, "middle", "bold")
    # щупи
    s += _probe(420, 348, 660, 150, RED)
    s += text(620, 140, "червоний", 10, RED, "middle", "bold")
    s += _probe(355, 348, 150, 200, INK)
    s += text(180, 190, "чорний (COM)", 10, INK, "middle", "bold")
    save("fig-6-6-1-overview.svg", s)


# ── Рис. 6.6.2 — напругу паралельно ──────────────────────────────────────────
def fig66_voltage():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Напругу міряють ПАРАЛЕЛЬНО", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "щупи прикладають до двох точок, не розриваючи коло; прилад високоомний",
              11.5, GREY, "middle", style="italic")
    s += line(120, 140, 120, 280, INK, 2.4)
    s += _battery(120, 210, "")
    s += text(96, 207, "9 В", 10.5, INK, "end", "bold")
    s += line(120, 140, 400, 140, COPPER, 2.4)
    s += _vresistor(400, 165, 255, "R", "start")
    s += line(400, 140, 400, 165, COPPER, 2.4)
    s += line(400, 255, 400, 280, COPPER, 2.4)
    s += line(120, 280, 400, 280, COPPER, 2.4)
    # вольтметр паралельно
    s += _meter(560, 210, "V", BLUE, 26)
    s += _probe(560, 184, 405, 150, RED)
    s += _probe(560, 236, 405, 270, INK)
    s += rect(160, 300, W - 320, 34, "#eaf0fb", BLUE, 1.5, 8)
    s += text(W / 2, 322, "Високий опір вольтметра майже не відбирає струму — коло не порушено (§6.0, §4.6).",
              11, INK, "middle", "bold")
    save("fig-6-6-2-voltage.svg", s)


# ── Рис. 6.6.3 — струм послідовно ────────────────────────────────────────────
def fig66_current():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Струм міряють ПОСЛІДОВНО (розірвавши коло)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "коло розривають і вмикають прилад у розрив; він малоомний",
              11.5, GREY, "middle", style="italic")
    s += line(120, 140, 120, 280, INK, 2.4)
    s += _battery(120, 210, "")
    s += text(96, 207, "9 В", 10.5, INK, "end", "bold")
    s += line(120, 140, 300, 140, COPPER, 2.4)
    # розрив + амперметр
    s += circle(300, 140, 3, INK, INK, 1)
    s += _probe(300, 140, 380, 110, INK)
    s += _meter(430, 110, "A", RED, 24)
    s += _probe(480, 110, 560, 140, RED)
    s += circle(560, 140, 3, INK, INK, 1)
    s += line(560, 140, 660, 140, COPPER, 2.4)
    s += _vresistor(660, 165, 255, "R", "end")
    s += line(660, 140, 660, 165, COPPER, 2.4)
    s += line(660, 255, 660, 280, COPPER, 2.4)
    s += line(120, 280, 660, 280, COPPER, 2.4)
    s += text(430, 160, "увімкнено В РОЗРИВ", 10, RED, "middle", "bold")
    s += rect(150, 300, W - 300, 34, "#fff3e8", ORANGE, 1.5, 8)
    s += text(W / 2, 322, "Малий опір амперметра майже не заважає струму. Не забудьте правильне гніздо (mA чи 10A)!",
              11, INK, "middle", "bold")
    save("fig-6-6-3-current.svg", s)


# ── Рис. 6.6.4 — опір на знеструмленому ──────────────────────────────────────
def fig66_resistance():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Опір — на ЗНЕСТРУМЛЕНОМУ елементі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "живлення вимкнено, деталь краще вийняти з кола; прилад сам пускає малий струм",
              11.5, GREY, "middle", style="italic")
    s += _resistor(330, 160, 90, 26, "R = ?")
    s += line(290, 160, 330, 160, COPPER, 2.2)
    s += line(420, 160, 460, 160, COPPER, 2.2)
    s += _meter(375, 250, "Ω", GREEN, 24)
    s += _probe(355, 232, 300, 175, RED)
    s += _probe(395, 232, 450, 175, INK)
    # прозвонка
    s += rect(540, 120, 250, 130, "#eef7f0", GREEN, 1.6, 10)
    s += text(665, 146, "Режим «прозвонка» •))", 12, GREEN, "middle", "bold")
    s += text(560, 174, "пищить, якщо опір ≈ 0", 10.5, INK, "start")
    s += text(560, 196, "(є з'єднання) — швидко", 10.5, INK, "start")
    s += text(560, 218, "перевіряти дроти й доріжки", 10.5, INK, "start")
    s += rect(120, 296, W - 240, 36, "#fbecea", RED, 1.5, 8)
    s += text(W / 2, 319, "НІКОЛИ не міряйте опір на ввімкненому колі — чужа напруга зіб'є показ і може зашкодити приладу.",
              10.5, INK, "middle", "bold")
    save("fig-6-6-4-resistance.svg", s)


# ── Рис. 6.6.5 — типові помилки ──────────────────────────────────────────────
def fig66_mistakes():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Дві небезпечні помилки", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "найчастіші — і найприкріші: вони псують запобіжник або прилад",
              11.5, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 40, FAINT, 1.4, "4,5")
    # 1: амперметр у паралель
    s += text(210, 104, "Амперметр у ПАРАЛЕЛЬ", 12.5, RED, "middle", "bold")
    s += line(110, 140, 110, 250, INK, 2.2)
    s += _battery(110, 195, "")
    s += text(86, 192, "9 В", 9.5, INK, "end", "bold")
    s += line(110, 140, 250, 140, COPPER, 2.2)
    s += line(110, 250, 250, 250, COPPER, 2.2)
    s += line(250, 140, 250, 250, COPPER, 2.2)
    s += _meter(310, 195, "A", RED, 22)
    s += _probe(310, 173, 252, 145, RED)
    s += _probe(310, 217, 252, 245, INK)
    s += text(210, 285, "малий опір = майже КЗ →", 10.5, RED, "middle", "bold")
    s += text(210, 303, "величезний струм, ЗАПОБІЖНИК згоряє", 10, INK, "middle", "bold")
    # 2: омметр на живому
    s += text(610, 104, "Омметр на ЖИВОМУ колі", 12.5, RED, "middle", "bold")
    s += line(500, 140, 500, 250, INK, 2.2)
    s += _battery(500, 195, "")
    s += text(476, 192, "9 В", 9.5, INK, "end", "bold")
    s += line(500, 140, 680, 140, COPPER, 2.2)
    s += _vresistor(680, 160, 230, "R", "end")
    s += line(680, 140, 680, 160, COPPER, 2.2)
    s += line(680, 230, 680, 250, COPPER, 2.2)
    s += line(500, 250, 680, 250, COPPER, 2.2)
    s += _meter(600, 300, "Ω", GREEN, 20)
    s += _probe(582, 286, 510, 145, RED)
    s += _probe(618, 286, 680, 200, INK)
    s += text(610, 333, "чужа напруга → хибний показ, ризик шкоди", 10, RED, "middle", "bold")
    save("fig-6-6-5-mistakes.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до §6.7 — Браун і електронно-променева трубка.  Рис. 6.7і.N
# ════════════════════════════════════════════════════════════════════════════

GLOW = "#7CFC7C"


# ── Рис. 6.7і.1 — чому промінь, а не стрілка ─────────────────────────────────
def fig_why_electrons():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Чому промінь, а не стрілка: маса вирішує все", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "щоб устигати за швидким сигналом, «перо» має бути майже без маси — таким є пучок електронів",
              11, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 40, FAINT, 1.4, "4,5")
    # стрілка
    s += text(210, 100, "Механічна стрілка", 13, RED, "middle", "bold")
    s += circle(150, 230, 5, INK, INK, 1)
    s += _needle(150, 230, 35, 90, INK)
    s += circle(150 + 90 * math.cos(math.radians(35 - 90)), 230 + 90 * math.sin(math.radians(35 - 90)), 7, "#bbb", INK, 1.5)
    s += _needle(150, 230, 5, 90, "#c9c9c9")
    s += text(150, 290, "має масу й інерцію →", 10.5, RED, "middle", "bold")
    s += text(150, 308, "відстає від швидкого сигналу", 10, GREY, "middle")
    # промінь
    s += text(620, 100, "Пучок електронів", 13, GREEN, "middle", "bold")
    s += rect(470, 150, 30, 30, "#fdecea", RED, 1.6, 3)
    s += text(485, 170, "К", 11, RED, "middle", "bold")
    s += line(500, 165, 740, 230, GLOW, 2.6)
    s += circle(740, 230, 7, GLOW, GREEN, 1.5)
    s += text(620, 290, "майже без маси →", 10.5, GREEN, "middle", "bold")
    s += text(620, 308, "встигає за найшвидшим сигналом", 10, GREY, "middle")
    save("fig-6-7i-1-why-electrons.svg", s)


# ── Рис. 6.7і.2 — анатомія ЕПТ ───────────────────────────────────────────────
def fig_crt():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Електронно-променева трубка Брауна (1897)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "катод стріляє електронами, пластини відхиляють пучок, люмінофор світиться там, куди він влучив",
              10.5, GREY, "middle", style="italic")
    cy = 220
    # колба: шийка + лійка + екран
    s += rect(90, cy - 26, 90, 52, "#eef2f5", "#9aa3ad", 2, 6)
    s += polygon([(180, cy - 26), (660, cy - 95), (660, cy + 95), (180, cy + 26)], "#f3f6f9", "#9aa3ad", 2)
    s += rect(648, cy - 95, 26, 190, "#0d1f0d", "#2a4a2a", 2, 4)
    # катод (нитка) + анод
    s += line(108, cy - 10, 118, cy + 10, RED, 2)
    s += line(118, cy - 10, 108, cy + 10, RED, 2)
    s += text(135, cy - 36, "катод", 9, RED, "middle", "bold")
    s += circle(165, cy, 7, "none", INK, 1.8)
    s += text(165, cy - 36, "анод", 9, INK, "middle", "bold")
    # пучок
    s += line(165, cy, 660, cy - 40, GLOW, 2.4)
    s += circle(660, cy - 40, 6, GLOW, GREEN, 1.5)
    s += text(380, cy + 8, "пучок електронів", 9.5, GREEN, "middle", "bold")
    # вертикальні відхильні пластини (горизонтальні смуги)
    s += line(300, cy - 36, 380, cy - 36, BLUE, 3)
    s += line(300, cy + 36, 380, cy + 36, BLUE, 3)
    s += text(340, cy - 48, "відхилення ↕ (сигнал)", 8.5, BLUE, "middle", "bold")
    # горизонтальні відхильні пластини (вертикальні смуги)
    s += line(470, cy - 60, 470, cy - 20, ORANGE, 3)
    s += line(540, cy - 60, 540, cy - 20, ORANGE, 3)
    s += text(505, cy - 70, "відхилення ↔ (час)", 8.5, ORANGE, "middle", "bold")
    # екран
    s += text(700, cy, "люмінофор", 10, INK, "start", "bold")
    s += text(700, cy + 16, "(світиться)", 9, GREY, "start")
    save("fig-6-7i-2-crt.svg", s)


# ── Рис. 6.7і.3 — як ЕПТ малює V(t) ──────────────────────────────────────────
def fig_crt_draws():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Як трубка малює V(t): два відхилення разом", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "пилкоподібна розгортка тягне промінь по часу, сигнал гойдає його по напрузі",
              11, GREY, "middle", style="italic")
    # розгортка (пилка)
    s += text(150, 96, "Розгортка (час →)", 11, ORANGE, "middle", "bold")
    saw = []
    for k in range(0, 4):
        saw.append((70 + k * 60, 200))
        saw.append((70 + (k + 1) * 60 - 6, 140))
        saw.append((70 + (k + 1) * 60 - 6, 200))
    s += polyline(saw, ORANGE, 2.2)
    s += text(150, 224, "рівномірно зліва направо", 9, GREY, "middle")
    # сигнал
    s += text(150, 268, "Сигнал (напруга ↕)", 11, BLUE, "middle", "bold")
    s += _sine(70, 290, 305, 26, 2, 0, BLUE)
    # стрілка до екрана
    s += arrow(330, 200, 410, 200, INK, 2.4)
    s += text(370, 186, "разом →", 9, GREY, "middle", style="italic")
    # екран із трасою
    s += _screen(430, 110, 340, 180)
    s += _sine(440, 760, 200, 60, 2, 0, GLOW)
    s += text(600, 308, "сигнал намальовано світлом — V(t) на екрані", 10.5, GREEN, "middle", "bold")
    save("fig-6-7i-3-crt-draws.svg", s)


# ── Рис. 6.7і.4 — спадщина ЕПТ ───────────────────────────────────────────────
def fig_crt_legacy():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 30, "Та сама трубка — століття екранів", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "осцилограф, телевізор, монітор: усі вони — нащадки трубки Брауна", 11.5, GREY, "middle", style="italic")
    items = [(150, "Осцилограф", "перше застосування — бачити сигнал", BLUE),
             (430, "Телевізор", "ЕПТ-екрани понад півстоліття", GREEN),
             (710, "Монітор", "екрани комп'ютерів до епохи РК", ORANGE)]
    for x, t, d, col in items:
        s += rect(x - 110, 86, 220, 130, "#f6f8fc", col, 1.8, 12)
        s += rect(x - 70, 108, 140, 70, "#0d1f0d", "#2a4a2a", 2, 6)
        if t == "Осцилограф":
            s += _sine(x - 62, x + 62, 143, 18, 2, 0, GLOW)
        else:
            s += circle(x, 143, 16, GLOW, "none", 0)
        s += text(x, 200, t, 12.5, col, "middle", "bold")
        s += text(x, 232, d, 9.5, GREY, "middle")
    s += rect(150, 256, W - 300, 56, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 280, "Карл Браун за внесок у бездротовий телеграф здобув Нобелівську премію 1909 року (разом із Марконі);",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 298, "а його «трубка» подарувала світові і осцилограф, і телебачення.", 10, GREY, "middle", style="italic")
    save("fig-6-7i-4-legacy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.7 — Осцилограф: побачити сигнал у часі.  Рис. 6.7.k
# ════════════════════════════════════════════════════════════════════════════

TRACE = "#7CFC7C"


def _screen(x, y, w, h, divs=8):
    o = rect(x, y, w, h, "#0d1f0d", "#2a4a2a", 2, 4)
    for i in range(1, divs):
        gx = x + i * w / divs
        o += line(gx, y, gx, y + h, "#1f3a1f", 1)
    rows = max(1, round(h / (w / divs)))
    for j in range(1, rows):
        gy = y + j * h / rows
        o += line(x, gy, x + w, gy, "#1f3a1f", 1)
    return o


def _sine(x0, x1, cy, amp, cycles, phase=0.0, color=TRACE, w=2.4):
    pts = []
    n = 140
    for k in range(n + 1):
        t = k / n
        xx = x0 + t * (x1 - x0)
        yy = cy - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((xx, yy))
    return polyline(pts, color, w)


def _square(x0, x1, cyhi, cylo, cycles, color=TRACE, w=2.4):
    pts = [(x0, cyhi)]
    n = cycles * 2
    seg = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * seg
        y = cyhi if i % 2 == 0 else cylo
        pts.append((xa, y))
        pts.append((xa + seg, y))
    return polyline(pts, color, w)


# ── Рис. 6.7.1 — число проти форми ───────────────────────────────────────────
def fig67_number_vs_shape():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Мультиметр дає ЧИСЛО, осцилограф — ФОРМУ", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "багато сигналів змінюються в часі; одне число ховає, що насправді коїться",
              11.5, GREY, "middle", style="italic")
    # мультиметр
    s += text(200, 96, "Мультиметр", 13, INK, "middle", "bold")
    s += rect(110, 120, 180, 110, "#f0f2f5", "#9aa3ad", 2, 12)
    s += rect(130, 140, 140, 50, "#1c2b1c", INK, 2, 6)
    s += text(200, 174, "2.50 В", 20, "#7CFC7C", "middle", "bold")
    s += text(200, 215, "(лише середнє — і все)", 10, GREY, "middle", style="italic")
    s += text(430, 175, "→", 30, INK, "middle", "bold")
    # осцилограф
    s += text(660, 96, "Осцилограф", 13, GREEN, "middle", "bold")
    s += _screen(500, 120, 320, 150)
    s += _square(515, 805, 150, 240, 4)
    s += text(660, 292, "видно: сигнал стрибає 0↔5 В прямокутником", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 332, "Те саме коло: мультиметр показав «2.5 В», а осцилограф — що це насправді ПРЯМОКУТНІ імпульси.",
              11, GREY, "middle", style="italic")
    save("fig-6-7-1-number-vs-shape.svg", s)


# ── Рис. 6.7.2 — екран осцилографа ───────────────────────────────────────────
def fig67_screen():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Екран: напруга по вертикалі, час по горизонталі", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "це графік V(t); поділки + ручки «В/поділка» і «час/поділка» дають масштаб",
              11.5, GREY, "middle", style="italic")
    s += _screen(160, 90, 480, 210)
    s += _sine(170, 630, 195, 70, 2.5)
    s += arrow(150, 300, 150, 90, INK, 2)
    s += text(146, 84, "напруга", 11, INK, "end", "bold")
    s += arrow(160, 320, 660, 320, INK, 2)
    s += text(664, 324, "час", 11, INK, "start", "bold")
    s += rect(150, 336, 200, 34, "#eaf0fb", BLUE, 1.5, 8)
    s += text(250, 358, "В/поділка → масштаб напруги", 9.5, INK, "middle", "bold")
    s += rect(450, 336, 220, 34, "#eef7f0", GREEN, 1.5, 8)
    s += text(560, 358, "час/поділка → масштаб часу", 9.5, INK, "middle", "bold")
    save("fig-6-7-2-screen.svg", s)


# ── Рис. 6.7.3 — зчитати амплітуду й період ──────────────────────────────────
def fig67_read():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Зчитуємо амплітуду й період (звідси частота)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "рахуй поділки × масштаб: тут 1 В/под. і 1 мс/под.", 11.5, GREY, "middle", style="italic")
    ox, oy, w, h = 130, 90, 440, 200
    s += _screen(ox, oy, w, h)
    cy = oy + h / 2
    s += _sine(ox + 10, ox + w - 10, cy, 60, 2)
    # амплітуда
    s += line(ox + 50, cy, ox + 50, cy - 60, "#ffd24a", 1.6, "4,3")
    s += arrow(ox + 50, cy, ox + 50, cy - 60, "#e0a020" if False else ORANGE, 1.8)
    s += text(ox + 62, cy - 36, "ампл. = 3 под. = 3 В", 10, ORANGE, "start", "bold")
    # період
    px0 = ox + 10 + (w - 20) * 0.25
    px1 = ox + 10 + (w - 20) * 0.75
    s += line(px0, cy + 78, px1, cy + 78, "#ffd24a", 1.4, "4,3")
    s += arrow(px0, cy + 78, px1, cy + 78, ORANGE, 1.6)
    s += text((px0 + px1) / 2, cy + 95, "період T = 4 под. = 4 мс", 10, ORANGE, "middle", "bold")
    s += rect(610, 110, 200, 160, "#f6f8fc", INK, 1.5, 12)
    s += text(710, 140, "Амплітуда = 3 В", 12.5, INK, "middle", "bold")
    s += text(710, 168, "Період T = 4 мс", 12.5, INK, "middle", "bold")
    s += line(630, 184, 790, 184, FAINT, 1.3)
    s += text(710, 212, "Частота:", 11.5, INK, "middle", "bold")
    s += text(710, 236, "f = 1/T = 1/0.004", 11, GREY, "middle")
    s += rect(635, 248, 150, 16, "#eef7f0", GREEN, 1.4, 6)
    s += text(710, 261, "= 250 Гц", 12.5, GREEN, "middle", "bold")
    save("fig-6-7-3-read.svg", s)


# ── Рис. 6.7.4 — тригер: спіймати хвилю ──────────────────────────────────────
def fig67_trigger():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Синхронізація (тригер): спіймати хвилю нерухомо", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "тригер «ловить» сигнал у тій самій точці щорозу — і хвиля завмирає на екрані",
              11.5, GREY, "middle", style="italic")
    # без тригера
    s += text(220, 96, "Без тригера", 13, RED, "middle", "bold")
    s += _screen(80, 120, 280, 140)
    cy = 190
    s += _sine(90, 350, cy, 48, 2.2, 0.0, "#3a7a3a")
    s += _sine(90, 350, cy, 48, 2.2, 1.3, "#5aaa5a")
    s += _sine(90, 350, cy, 48, 2.2, 2.6, TRACE)
    s += text(220, 282, "хвиля «біжить», розмита", 10, RED, "middle", "bold")
    # з тригером
    s += text(640, 96, "З тригером", 13, GREEN, "middle", "bold")
    s += _screen(500, 120, 280, 140)
    s += _sine(510, 770, 190, 48, 2.2, 0.0, TRACE)
    s += line(500, 190, 780, 190, "#ffd24a", 1, "3,3")
    s += text(786, 193, "рівень", 8.5, "#caa020", "start")
    s += text(640, 282, "стабільна, нерухома картинка", 10, GREEN, "middle", "bold")
    s += text(W / 2, 330, "Без синхронізації періодичний сигнал «пливе»; тригер прив'язує кожен прохід до того самого рівня.",
              10.5, GREY, "middle", style="italic")
    save("fig-6-7-4-trigger.svg", s)


# ── Рис. 6.7.5 — що видно осцилографу ────────────────────────────────────────
def fig67_reveals():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Що бачить осцилограф, чого не бачить мультиметр", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "шум, викиди, «дзвін», повільні фронти, спотворення — усе, що усереднення ховає",
              11, GREY, "middle", style="italic")
    panels = [(70, "Шум на лінії"), (480, "Гліч (викид)")]
    # шум
    s += _screen(70, 90, 330, 110)
    pts = []
    seed = [3, -2, 4, -1, 5, -3, 2, -4, 3, -1, 4, -2, 5, -3, 2, -4, 1, -2, 3, -1]
    n = 40
    for k in range(n + 1):
        xx = 80 + (310) * k / n
        yy = 145 + (seed[k % len(seed)]) * 3
        pts.append((xx, yy))
    s += polyline(pts, TRACE, 2)
    s += text(235, 220, "Шум на лінії", 11, INK, "middle", "bold")
    # гліч
    s += _screen(480, 90, 330, 110)
    s += line(490, 170, 640, 170, TRACE, 2.2)
    s += polyline([(640, 170), (645, 110), (650, 170)], TRACE, 2.2)
    s += line(650, 170, 800, 170, TRACE, 2.2)
    s += text(645, 105, "сплеск!", 9, RED, "middle", "bold")
    s += text(645, 220, "Гліч (короткий викид)", 11, INK, "middle", "bold")
    # дзвін
    s += _screen(70, 250, 330, 100)
    s += line(80, 320, 200, 320, TRACE, 2.2)
    rp = [(200, 320), (205, 275), (215, 305), (225, 288), (235, 298), (250, 295), (390, 295)]
    s += polyline(rp, TRACE, 2.2)
    s += text(235, 366, "«Дзвін» після фронту", 10.5, INK, "middle", "bold")
    # спотворення
    s += _screen(480, 250, 330, 100)
    cy = 300
    pts = []
    for k in range(81):
        t = k / 80
        v = math.sin(2 * math.pi * 1.5 * t)
        v = max(-0.7, min(0.7, v * 1.3))      # «обрізана» (clipping)
        pts.append((490 + 310 * t, cy - v * 34))
    s += polyline(pts, TRACE, 2.2)
    s += text(645, 366, "Спотворення (обрізання)", 10.5, INK, "middle", "bold")
    save("fig-6-7-5-reveals.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §6.8 — Похибки й безпека вимірювань.  Рис. 6.8.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 6.8.1 — прилад завжди трохи спотворює ───────────────────────────────
def fig68_loading():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 30, "Прилад завжди трохи спотворює те, що міряє", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "ідеальних приладів нема: вольтметр відбирає крихту струму, амперметр додає крихту опору",
              11, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 56, FAINT, 1.4, "4,5")
    # вольтметр
    s += text(215, 100, "Вольтметр трохи ЗАНИЖУЄ", 12.5, BLUE, "middle", "bold")
    s += line(90, 135, 90, 245, INK, 2.2)
    s += _battery(90, 190, "")
    s += line(90, 135, 230, 135, COPPER, 2.2)
    s += _vresistor(230, 160, 220, "R", "start")
    s += line(230, 135, 230, 160, COPPER, 2.2)
    s += line(230, 220, 230, 245, COPPER, 2.2)
    s += line(90, 245, 230, 245, COPPER, 2.2)
    s += _meter(330, 190, "V", BLUE, 20)
    s += line(310, 178, 235, 145, BLUE, 2)
    s += line(310, 202, 235, 235, BLUE, 2)
    s += text(215, 285, "відбирає краплю струму → читає трохи менше", 9.5, GREY, "middle", style="italic")
    # амперметр
    s += text(645, 100, "Амперметр трохи ЗМЕНШУЄ струм", 12, GREEN, "middle", "bold")
    s += line(500, 135, 500, 245, INK, 2.2)
    s += _battery(500, 190, "")
    s += line(500, 135, 560, 135, COPPER, 2.2)
    s += _meter(595, 135, "A", GREEN, 18)
    s += line(613, 135, 700, 135, COPPER, 2.2)
    s += _vresistor(700, 160, 220, "R", "end")
    s += line(700, 135, 700, 160, COPPER, 2.2)
    s += line(700, 220, 700, 245, COPPER, 2.2)
    s += line(500, 245, 700, 245, COPPER, 2.2)
    s += text(645, 285, "додає краплю опору → струм трохи менший", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "Похибка зазвичай мала, та в точних вимірах її враховують (§5.1, історія розділу).",
              10.5, GREY, "middle", style="italic")
    save("fig-6-8-1-loading.svg", s)


def _dart(cx, cy, r, dots, col):
    o = circle(cx, cy, r, "none", "#bbb", 1.4)
    o += circle(cx, cy, r * 0.62, "none", "#bbb", 1.2)
    o += circle(cx, cy, r * 0.26, "none", RED, 1.6)
    for dx, dy in dots:
        o += circle(cx + dx, cy + dy, 3.2, col, col, 1)
    return o


# ── Рис. 6.8.2 — точність, влучність, роздільність ───────────────────────────
def fig68_accuracy_precision():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Точність, влучність, роздільність — це різне", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "влучний ≠ точний; а роздільність — лише дрібність поділки, не правдивість", 11, GREY, "middle", style="italic")
    s += _dart(150, 150, 56, [(-4, 3), (5, -2), (2, 6), (-2, -4)], GREEN)
    s += text(150, 230, "Точно + влучно", 11.5, GREEN, "middle", "bold")
    s += text(150, 248, "близько до істини, купно", 9, GREY, "middle")
    s += _dart(370, 150, 56, [(28, -20), (33, -16), (30, -24), (26, -18)], ORANGE)
    s += text(370, 230, "Влучно, та НЕ точно", 11.5, ORANGE, "middle", "bold")
    s += text(370, 248, "купно, але збоку (зсув)", 9, GREY, "middle")
    s += _dart(590, 150, 56, [(-30, 10), (25, -28), (5, 30), (-20, -25), (33, 12)], BLUE)
    s += text(590, 230, "Розкидано", 11.5, BLUE, "middle", "bold")
    s += text(590, 248, "ні точно, ні влучно", 9, GREY, "middle")
    s += rect(710, 96, 130, 150, "#f6f8fc", INK, 1.5, 10)
    s += text(775, 120, "Роздільність", 11, INK, "middle", "bold")
    s += text(775, 150, "5.0 В", 13, GREY, "middle")
    s += text(775, 174, "5.00 В", 14, INK, "middle", "bold")
    s += text(775, 198, "більше цифр —", 9, GREY, "middle")
    s += text(775, 212, "дрібніша поділка,", 9, GREY, "middle")
    s += text(775, 226, "та НЕ гарантія", 9, RED, "middle", "bold")
    s += text(775, 240, "правдивості", 9, RED, "middle", "bold")
    save("fig-6-8-2-accuracy-precision.svg", s)


# ── Рис. 6.8.3 — систематичні vs випадкові ───────────────────────────────────
def fig68_error_types():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Дві природи похибок", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "систематична — сталий зсув (виправити калібруванням); випадкова — розкид (зменшити усередненням)",
              10.5, GREY, "middle", style="italic")
    # систематична
    s += text(215, 100, "Систематична", 12.5, ORANGE, "middle", "bold")
    s += line(215, 120, 215, 250, GREEN, 1.6, "4,3")
    s += text(215, 268, "істина", 9, GREEN, "middle", "bold")
    for i in range(7):
        s += circle(300 + (i % 3) * 8, 140 + i * 14, 3.4, ORANGE, ORANGE, 1)
    s += arrow(250, 200, 295, 200, ORANGE, 1.8)
    s += text(330, 286, "усі зсунуті в один бік → калібрування", 9.5, GREY, "middle")
    # випадкова
    s += text(615, 100, "Випадкова", 12.5, BLUE, "middle", "bold")
    s += line(615, 120, 615, 250, GREEN, 1.6, "4,3")
    rnd = [(-22, 10), (18, -16), (-8, 24), (12, 8), (-16, -18), (24, 18), (-2, -8), (8, 28)]
    for dx, dy in rnd:
        s += circle(615 + dx, 185 + dy, 3.4, BLUE, BLUE, 1)
    s += text(615, 286, "розкид навколо істини → усереднення", 9.5, GREY, "middle")
    save("fig-6-8-3-error-types.svg", s)


def _person(x, y, col=INK):
    o = circle(x, y - 40, 10, "#fff", col, 2)
    o += line(x, y - 30, x, y, col, 2.4)
    o += line(x, y - 22, x - 16, y - 6, col, 2.2)
    o += line(x, y - 22, x + 16, y - 10, col, 2.2)
    o += line(x, y, x - 12, y + 28, col, 2.2)
    o += line(x, y, x + 12, y + 28, col, 2.2)
    return o


# ── Рис. 6.8.4 — безпека: тіло й мережа ──────────────────────────────────────
def fig68_safety_body():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Безпека передусім: струм крізь тіло вбиває", 18.5, RED, "middle", "bold")
    s += text(W / 2, 52, "мережа 230 В небезпечна; небезпечний саме СТРУМ крізь тіло (§2.13)", 11, GREY, "middle", style="italic")
    s += _person(200, 180)
    # розетка / мережа
    s += rect(360, 150, 60, 70, "#f6f8fc", INK, 2, 6)
    s += circle(378, 175, 4, INK, INK, 1)
    s += circle(402, 175, 4, INK, INK, 1)
    s += text(390, 240, "230 В", 11, RED, "middle", "bold")
    # шлях струму (заборонений)
    s += line(216, 168, 360, 175, RED, 2, "5,4")
    s += line(200, 208, 200, 320, RED, 2, "5,4")
    s += text(280, 150, "✗ небезпечний шлях", 10, RED, "middle", "bold")
    # правило однієї руки
    s += rect(500, 110, 300, 200, "#fbecea", RED, 1.8, 12)
    s += text(650, 138, "Прості правила життя", 13, RED, "middle", "bold")
    s += text(520, 168, "• НЕ торкайся живих провідників", 11, INK, "start", "bold")
    s += text(520, 194, "• «правило однієї руки»:", 11, INK, "start", "bold")
    s += text(535, 212, "другу — в кишеню, щоб струм", 10, GREY, "start")
    s += text(535, 228, "не пішов крізь серце", 10, GREY, "start")
    s += text(520, 254, "• мережу 230 В лиши фахівцям;", 11, INK, "start", "bold")
    s += text(535, 272, "учися на низькій напрузі (5 В)", 10, GREY, "start")
    s += text(520, 298, "• сумнів — вимкни живлення", 11, INK, "start", "bold")
    save("fig-6-8-4-safety-body.svg", s)


# ── Рис. 6.8.5 — безпека приладу й кола ──────────────────────────────────────
def fig68_safety_device():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Бережіть і прилад, і коло", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "кілька звичок, що рятують запобіжники, прилади та нерви", 11.5, GREY, "middle", style="italic")
    rules = [("Не перевищуй межі приладу", "категорія й макс. напруга — у паспорті"),
             ("Конденсатори тримають заряд", "після вимкнення розряди їх — інакше вдарить"),
             ("Правильні гніздо й діапазон", "струм — в А-гніздо; не міряй В у струмовому"),
             ("Цілі щупи й режим", "тріснута ізоляція щупа — небезпечна")]
    yy = 92
    for t, d in rules:
        s += circle(100, yy + 22, 14, GREEN, INK, 2)
        s += text(100, yy + 27, "✓", 14, "#fff", "middle", "bold")
        s += rect(128, yy, 660, 46, "#f6f8fc", GREEN, 1.5, 10)
        s += text(146, yy + 20, t, 12.5, INK, "start", "bold")
        s += text(146, yy + 38, d, 10, GREY, "start")
        yy += 56
    save("fig-6-8-5-safety-device.svg", s)


if __name__ == "__main__":
    fig_oersted()
    fig_galvanometer()
    fig_three_meters()
    fig_loading()
    # §6.1 Навіщо принципова схема
    fig61_photo_vs_schematic()
    fig61_three_views()
    fig61_topology()
    fig61_anatomy()
    fig61_benefits()
    # §6.2 Умовні позначення
    fig62_passives()
    fig62_semiconductors()
    fig62_sources_switches()
    fig62_ground_io()
    fig62_two_standards()
    # §6.3 Вузли, з'єднання, перетини
    fig63_dot_vs_cross()
    fig63_hop()
    fig63_ambiguous()
    fig63_node()
    fig63_net_labels()
    # §6.4 «Земля» та шини живлення
    fig64_ground_reference()
    fig64_relative()
    fig64_rails()
    fig64_ground_types()
    fig64_split_supply()
    # §6.5 Як читати схему
    fig65_recipe()
    fig65_power_first()
    fig65_signal_flow()
    fig65_patterns()
    fig65_worked()
    # §6.6 Мультиметр
    fig66_overview()
    fig66_voltage()
    fig66_current()
    fig66_resistance()
    fig66_mistakes()
    # Історія до §6.6 — Вестон
    fig_weston_meter()
    fig_alloy_stability()
    fig_standard_cell()
    fig_weston_legacy()
    # §6.7 Осцилограф
    fig67_number_vs_shape()
    fig67_screen()
    fig67_read()
    fig67_trigger()
    fig67_reveals()
    # Історія до §6.7 — Браун і ЕПТ
    fig_why_electrons()
    fig_crt()
    fig_crt_draws()
    fig_crt_legacy()
    # §6.8 Похибки й безпека
    fig68_loading()
    fig68_accuracy_precision()
    fig68_error_types()
    fig68_safety_body()
    fig68_safety_device()
    print("OK — фігури Розділу 6 (повна, +§6.8) згенеровано в", OUT)
