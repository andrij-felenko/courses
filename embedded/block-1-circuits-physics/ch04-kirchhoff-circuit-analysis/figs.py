# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4 — «Закони Кірхгофа й аналіз кіл» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: історія до розділу — секція 0 (Рис. 4.0.N); теми — Рис. 4.M.k.
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
    """Вертикальна батарея на осі cx, центр cy; + довга тонка, − коротка товста."""
    out = line(cx - 16, cy - 8, cx + 16, cy - 8, INK, 3)
    out += line(cx - 9, cy + 8, cx + 9, cy + 8, INK, 5)
    if label:
        lx = cx - 22 if anchor == "end" else cx + 22
        out += text(lx, cy + 4, label, 11.5, INK, anchor, "bold")
    return out


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 4 — Кірхгоф: узагальнення Ома.  Рис. 4.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 4.0.1 — один контур (Ом) проти мережі (треба Кірхгоф) ───────────────
def fig_ohm_vs_network():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 30, "Один резистор Ому до снаги — а ціла мережа?", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "закон Ома сам розв'язує простий контур, але застрягає на розгалуженнях",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 74, W / 2, H - 56, FAINT, 1.4, "4,5")

    # ── ліворуч: простий контур ──
    s += text(225, 98, "Простий контур — Ом сам дає раду", 13.5, INK, "middle", "bold")
    s += _battery(110, 190, "V")
    s += line(110, 130, 110, 182, INK, 2.4)
    s += line(110, 198, 110, 250, INK, 2.4)
    s += line(110, 130, 350, 130, COPPER, 2.6)
    s += _resistor(150, 130, 60, 20, "R₁")
    s += _resistor(250, 130, 60, 20, "R₂")
    s += line(350, 130, 350, 250, INK, 2.4)
    s += line(110, 250, 350, 250, COPPER, 2.6)
    s += arrow(180, 250, 140, 250, RED, 2)
    s += rect(120, 290, 230, 52, "#eef7f0", GREEN, 1.8, 10)
    s += text(235, 312, "I = V / (R₁ + R₂)", 15, GREEN, "middle", "bold")
    s += text(235, 332, "один струм, один крок", 10.5, GREY, "middle", style="italic")

    # ── праворуч: мережа ──
    s += text(650, 98, "Розгалуження — Ом сам застрягає", 13.5, INK, "middle", "bold")
    s += _battery(500, 195, "V", "start")
    s += line(500, 135, 500, 187, INK, 2.4)
    s += line(500, 203, 500, 255, INK, 2.4)
    s += line(500, 135, 790, 135, COPPER, 2.6)     # верхня шина (вузол A)
    s += line(500, 255, 790, 255, COPPER, 2.6)     # нижня шина (вузол B)
    s += circle(560, 135, 4, INK, INK, 1)
    s += text(560, 124, "вузол A", 10, INK, "middle", "bold")
    s += circle(560, 255, 4, INK, INK, 1)
    s += text(560, 274, "вузол B", 10, INK, "middle", "bold")
    for bx, lab in [(620, "R₁"), (700, "R₂"), (780, "R₃")]:
        s += _vresistor(bx, 165, 225, lab)
        s += line(bx, 135, bx, 165, COPPER, 2.2)
        s += line(bx, 225, bx, 255, COPPER, 2.2)
        s += text(bx - 16, 200, "I?", 11, RED, "end", "bold", "italic")
    s += rect(520, 300, 300, 56, "#fbecea", RED, 1.8, 10)
    s += text(670, 322, "Куди й скільки тече в кожній гілці?", 12, INK, "middle", "bold")
    s += text(670, 340, "Сам закон Ома не скаже — потрібні правила Кірхгофа.", 10, GREY, "middle", style="italic")
    save("fig-4-0-1-ohm-vs-network.svg", s)


# ── Рис. 4.0.2 — перший закон (KCL): струми у вузлі ───────────────────────────
def fig_kcl():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 32, "Перший закон Кірхгофа (KCL): струми у вузлі", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "скільки заряду втікає у вузол — стільки й витікає; він не накопичується",
              12, GREY, "middle", style="italic")

    nx, ny = 410, 200
    # «труби» — світлі товсті смуги
    s += line(150, ny, nx, ny, "#cfe0f0", 16)            # вхід
    s += line(nx, ny, 640, ny - 90, "#cfe0f0", 16)       # вихід 1 (вгору-праворуч)
    s += line(nx, ny, 640, ny + 90, "#cfe0f0", 16)       # вихід 2 (вниз-праворуч)
    # струми (стрілки)
    s += arrow(150, ny, 300, ny, BLUE, 3)
    s += text(225, ny - 16, "I = 6 А", 13, BLUE, "middle", "bold")
    s += arrow(nx + 30, ny - 20, 600, ny - 78, BLUE, 3)
    s += text(560, ny - 92, "I₁ = 4 А", 12.5, BLUE, "middle", "bold")
    s += arrow(nx + 30, ny + 20, 600, ny + 78, BLUE, 3)
    s += text(560, ny + 98, "I₂ = 2 А", 12.5, BLUE, "middle", "bold")
    s += circle(nx, ny, 9, INK, INK, 1)
    s += text(nx, ny + 30, "вузол", 11, INK, "middle", "bold")

    s += rect(220, 300, 380, 52, "#eaf0fb", BLUE, 2, 12)
    s += text(410, 332, "ΣI_вх = ΣI_вих :   6 А = 4 А + 2 А", 16, BLUE, "middle", "bold")
    s += text(W / 2, H - 8, "Як трійник у водогоні: що влилося, те й розтеклося. Це — збереження заряду.",
              11, GREY, "middle", style="italic")
    save("fig-4-0-2-kcl.svg", s)


# ── Рис. 4.0.3 — другий закон (KVL): напруги в контурі ───────────────────────
def fig_kvl():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 32, "Другий закон Кірхгофа (KVL): напруги в контурі", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "обійди контур і повернися — сума підйомів дорівнює сумі спадів",
              12, GREY, "middle", style="italic")

    # контур
    s += _battery(110, 250, "")
    s += text(82, 254, "+12 В", 11.5, RED, "end", "bold")
    s += line(110, 180, 110, 242, INK, 2.4)
    s += line(110, 258, 110, 320, INK, 2.4)
    s += line(110, 180, 470, 180, COPPER, 2.6)
    s += _resistor(210, 180, 70, 22, "R₁")
    s += text(245, 150, "−7 В", 11.5, BLUE, "middle", "bold")
    s += line(470, 180, 470, 320, INK, 2.4)
    s += _resistor(470, 250, 70, 22, "")           # на правій стороні (горизонтальний бокс на вузлі)
    s += rect(458, 214, 24, 72, "#fff", INK, 2, 3)  # вертикальний R₂
    s += text(500, 254, "R₂", 12.5, INK, "start", "bold", "italic")
    s += text(500, 274, "−5 В", 11.5, BLUE, "start", "bold")
    s += line(110, 320, 470, 320, COPPER, 2.6)
    # напрямок обходу
    s += arrow(270, 180, 330, 180, INK, 1.8)
    s += text(300, 170, "обхід", 10, GREY, "middle", style="italic")
    s += text(290, 338, "почали тут — і сюди ж повернулись", 10, GREY, "middle", style="italic")

    # інсет: прогулянка пагорбом
    ix, iy = 600, 250
    s += rect(560, 150, 230, 150, "#f6f8fc", GREY, 1.4, 10)
    s += text(675, 172, "як прогулянка по колу:", 11, INK, "middle", "bold")
    s += line(580, 270, 770, 270, FAINT, 1.3, "3,3")          # рівень старту
    s += polyline([(590, 270), (620, 230), (650, 205), (690, 215), (730, 250), (760, 270)], GREEN, 2.4)
    s += circle(590, 270, 4, GREEN, GREEN, 1)
    s += circle(760, 270, 4, GREEN, GREEN, 1)
    s += text(675, 292, "вертаєшся на ту саму висоту → Δ = 0", 9.5, GREY, "middle", style="italic")

    s += rect(150, 358, 520, 46, "#eaf0fb", BLUE, 2, 10)
    s += text(410, 380, "обхід контуру:  +12 − 7 − 5 = 0   (Σпідйомів = Σспадів)", 14.5, BLUE, "middle", "bold")
    s += text(410, 398, "потенціал однозначний — це збереження енергії", 10, GREY, "middle", style="italic")
    save("fig-4-0-3-kvl.svg", s)


# ── Рис. 4.0.4 — масштаб Кірхгофа: спектроскопія й склад Сонця ────────────────
def fig_kirchhoff_legacy():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 32, "Не лише кола: Кірхгоф прочитав склад Сонця", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "з Бунзеном вони відкрили спектроскопію — і нові елементи, і «чорне тіло»",
              12, GREY, "middle", style="italic")

    # джерело + щілина + призма + спектр
    s += circle(80, 180, 16, "#fff3c0", ORANGE, 2)
    s += text(80, 215, "світло", 10, INK, "middle", "bold")
    s += line(96, 180, 180, 180, "#d9b94a", 4)               # промінь
    s += polygon([(180, 150), (180, 210), (245, 195)], "#dbe6f5", BLUE, 1.6)  # призма
    s += text(212, 232, "призма", 10, INK, "middle", "bold")
    # дисперсія — кольоровий спектр
    cols = ["#c0271e", "#e08030", "#f4c020", "#1f8a3b", "#1f47b5", "#7b3fa0"]
    sx = 470
    for i, c in enumerate(cols):
        s += line(245, 178, sx, 120 + i * 24, c, 2)          # розкладені промені
    bx = 560
    for i, c in enumerate(cols):
        s += rect(bx + i * 40, 130, 40, 90, c, "none", 0)
    s += rect(bx, 130, 240, 90, "none", INK, 1.5)
    # фраунгоферові лінії
    for lx in (bx + 70, bx + 140, bx + 195):
        s += line(lx, 130, lx, 220, "#111111", 2.4)
    s += text(bx + 120, 240, "спектр із темними лініями", 10.5, INK, "middle", "bold")
    s += text(bx + 120, 256, "кожна лінія — «відбиток» елемента", 9.5, GREY, "middle", style="italic")

    s += rect(70, 296, W - 140, 64, "#f6f8fc", INK, 1.4, 12)
    s += text(W / 2, 318, "Та сама строгість, що дала закони кіл, прочитала по лініях склад Сонця",
              12, INK, "middle", "bold")
    s += text(W / 2, 340, "і відкрила цезій та рубідій; а закон випромінювання Кірхгофа й термін «чорне тіло» стали зерном квантової фізики.",
              10.5, GREY, "middle", style="italic")
    save("fig-4-0-4-kirchhoff-legacy.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.1 — Вузли, гілки, контури: мова кіл.  Рис. 4.1.k
# ════════════════════════════════════════════════════════════════════════════

def _circ_arrow(cx, cy, r, color, a0_deg, a1_deg, w=2.6):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} 1 {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def _canon_circuit():
    """Канонічне коло з 2 контурами: V, R₁, R₂, R₃; вузли A, B, C."""
    o = line(130, 140, 130, 330, INK, 2.4)
    o += _battery(130, 235, "V", "start")
    o += line(130, 140, 290, 140, COPPER, 2.4)
    o += line(290, 140, 350, 140, COPPER, 2.4)
    o += _resistor(350, 140, 90, 20, "R₁")
    o += line(440, 140, 520, 140, COPPER, 2.4)
    o += _vresistor(290, 180, 290, "R₃")
    o += line(290, 140, 290, 180, COPPER, 2.2)
    o += line(290, 290, 290, 330, COPPER, 2.2)
    o += _vresistor(520, 180, 290, "R₂", "end")
    o += line(520, 140, 520, 180, COPPER, 2.2)
    o += line(520, 290, 520, 330, COPPER, 2.2)
    o += line(130, 330, 520, 330, COPPER, 2.4)
    o += circle(290, 140, 5, "#fff", INK, 2)
    o += circle(520, 140, 5, "#fff", INK, 2)
    o += circle(290, 330, 5, "#fff", INK, 2)
    o += text(290, 126, "A", 12.5, INK, "middle", "bold")
    o += text(520, 126, "B", 12.5, INK, "middle", "bold")
    o += text(196, 352, "C (нижня шина)", 10.5, INK, "middle", "bold")
    return o


# ── Рис. 4.1.1 — вузли, гілки, контури на схемі ──────────────────────────────
def fig41_node_branch_loop():
    W, H = 810, 430
    s = header(W, H)
    s += text(W / 2, 30, "Мова кіл: вузли, гілки, контури", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "три слова, якими описують будь-яку схему", 12, GREY, "middle", style="italic")
    s += _canon_circuit()
    s += _circ_arrow(208, 238, 30, GREEN, -55, 205, 2.6)
    s += text(208, 243, "1", 13, GREEN, "middle", "bold")
    s += _circ_arrow(405, 238, 30, BLUE, -55, 205, 2.6)
    s += text(405, 243, "2", 13, BLUE, "middle", "bold")
    lx = 590
    s += rect(lx - 15, 112, 210, 196, "#f6f8fc", INK, 1.4, 10)
    s += circle(lx + 4, 142, 5, "#fff", INK, 2)
    s += text(lx + 22, 146, "Вузол", 13, INK, "start", "bold")
    s += text(lx + 22, 163, "точка з'єднання (A, B, C)", 9.5, GREY, "start")
    s += rect(lx - 4, 188, 18, 12, "#fff", INK, 1.6, 2)
    s += text(lx + 22, 198, "Гілка", 13, INK, "start", "bold")
    s += text(lx + 22, 215, "елемент між вузлами", 9.5, GREY, "start")
    s += text(lx + 22, 229, "(V, R₁, R₂, R₃)", 9.5, GREY, "start")
    s += _circ_arrow(lx + 5, 258, 9, GREEN, -50, 210, 2)
    s += text(lx + 22, 262, "Контур", 13, INK, "start", "bold")
    s += text(lx + 22, 279, "замкнений шлях (1, 2)", 9.5, GREY, "start")
    save("fig-4-1-1-node-branch-loop.svg", s)


# ── Рис. 4.1.2 — що таке «той самий вузол» ───────────────────────────────────
def fig41_same_node():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Що таке «той самий вузол»", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "усі точки, з'єднані суцільним дротом, — це ОДИН вузол з одним потенціалом",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 56, FAINT, 1.4, "4,5")
    ny = 165
    s += line(110, ny, 410, ny, GREEN, 3)
    s += line(220, ny, 220, 115, GREEN, 3)
    s += line(320, ny, 320, 215, GREEN, 3)
    for px, py in [(110, ny), (220, 115), (320, 215), (410, ny)]:
        s += circle(px, py, 6, GREEN, GREEN, 1)
    s += text(260, 250, "усі ці точки — ОДИН вузол", 12.5, GREEN, "middle", "bold")
    s += text(260, 268, "(з'єднані дротом → однаковий потенціал)", 10.5, GREY, "middle", style="italic")
    s += circle(560, 165, 6, GREEN, GREEN, 1)
    s += text(560, 145, "вузол X", 10, GREEN, "middle", "bold")
    s += line(566, 165, 600, 165, COPPER, 2.4)
    s += _resistor(600, 165, 70, 20, "R")
    s += line(670, 165, 706, 165, COPPER, 2.4)
    s += circle(706, 165, 6, ORANGE, ORANGE, 1)
    s += text(706, 145, "вузол Y", 10, ORANGE, "middle", "bold")
    s += text(636, 250, "а елемент (резистор, лампа…)", 11, INK, "middle")
    s += text(636, 268, "РОЗДІЛЯЄ на два різні вузли", 11, ORANGE, "middle", "bold")
    s += text(W / 2, H - 16, "Правило: подумки «стягни» всі суцільні дроти — скільки лишилось точок, стільки й вузлів.",
              11, GREY, "middle", style="italic")
    save("fig-4-1-2-same-node.svg", s)


# ── Рис. 4.1.3 — послідовно й паралельно мовою вузлів ────────────────────────
def fig41_series_parallel_topo():
    W, H = 820, 350
    s = header(W, H)
    s += text(W / 2, 30, "Послідовно й паралельно — мовою вузлів", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "послідовно = спільна гілка; паралельно = спільні два вузли",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 74, W / 2, H - 40, FAINT, 1.4, "4,5")
    # послідовно
    s += text(215, 100, "Послідовно", 14, INK, "middle", "bold")
    s += line(80, 175, 120, 175, COPPER, 2.4)
    s += arrow(92, 175, 112, 175, RED, 2)
    s += _resistor(120, 175, 70, 20, "R₁")
    s += line(190, 175, 235, 175, COPPER, 2.4)
    s += circle(212, 175, 4, INK, INK, 1)
    s += _resistor(235, 175, 70, 20, "R₂")
    s += line(305, 175, 345, 175, COPPER, 2.4)
    s += text(215, 215, "одна гілка → той самий струм I", 11, RED, "middle", "bold")
    s += text(215, 233, "крізь обидва резистори", 10.5, GREY, "middle", style="italic")
    # паралельно
    s += text(615, 100, "Паралельно", 14, INK, "middle", "bold")
    s += circle(505, 175, 5, INK, INK, 1)
    s += circle(725, 175, 5, INK, INK, 1)
    s += line(505, 135, 505, 215, COPPER, 2.4)
    s += line(725, 135, 725, 215, COPPER, 2.4)
    s += line(505, 135, 545, 135, COPPER, 2.4)
    s += _resistor(545, 135, 70, 18, "R₁")
    s += line(615, 135, 725, 135, COPPER, 2.4)
    s += line(505, 215, 545, 215, COPPER, 2.4)
    s += _resistor(545, 215, 70, 18, "R₂")
    s += line(615, 215, 725, 215, COPPER, 2.4)
    s += line(470, 175, 505, 175, COPPER, 2.4)
    s += line(725, 175, 760, 175, COPPER, 2.4)
    s += text(615, 258, "ті самі два вузли → та сама напруга V", 11, BLUE, "middle", "bold")
    s += text(615, 276, "на обох резисторах", 10.5, GREY, "middle", style="italic")
    save("fig-4-1-3-series-parallel-topo.svg", s)


# ── Рис. 4.1.4 — топологія важливіша за «географію» ──────────────────────────
def fig41_topology_vs_geometry():
    W, H = 820, 350
    s = header(W, H)
    s += text(W / 2, 30, "Важливо, ЩО з'єднано, а не як накреслено", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "та сама петля V–R₁–R₂ у двох виглядах — електрично вони тотожні",
              12, GREY, "middle", style="italic")
    # ліворуч: R₁ зверху, R₂ праворуч
    s += _battery(100, 230, "V", "start")
    s += line(100, 150, 100, 222, INK, 2.4)
    s += line(100, 238, 100, 310, INK, 2.4)
    s += line(100, 150, 330, 150, COPPER, 2.4)
    s += _resistor(150, 150, 70, 20, "R₁")
    s += _vresistor(330, 190, 270, "R₂", "end")
    s += line(330, 150, 330, 190, COPPER, 2.2)
    s += line(330, 270, 330, 310, COPPER, 2.2)
    s += line(100, 310, 330, 310, COPPER, 2.4)
    s += text(215, 335, "вигляд 1", 11, GREY, "middle", style="italic")
    # ≡
    s += text(415, 235, "≡", 34, INK, "middle", "bold")
    # праворуч: обидва резистори на верхній шині
    s += _battery(500, 230, "V", "start")
    s += line(500, 150, 500, 222, INK, 2.4)
    s += line(500, 238, 500, 310, INK, 2.4)
    s += line(500, 150, 540, 150, COPPER, 2.4)
    s += _resistor(540, 150, 70, 20, "R₁")
    s += line(610, 150, 645, 150, COPPER, 2.4)
    s += circle(627, 150, 4, INK, INK, 1)
    s += _resistor(645, 150, 70, 20, "R₂")
    s += line(715, 150, 740, 150, COPPER, 2.4)
    s += line(740, 150, 740, 310, INK, 2.4)
    s += line(500, 310, 740, 310, COPPER, 2.4)
    s += text(620, 335, "вигляд 2", 11, GREY, "middle", style="italic")
    save("fig-4-1-4-topology-vs-geometry.svg", s)


# ── Рис. 4.1.5 — порахуймо вузли, гілки, контури ─────────────────────────────
def fig41_count():
    W, H = 810, 430
    s = header(W, H)
    s += text(W / 2, 30, "Порахуймо: вузли, гілки, контури", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "скільки незалежних контурів? відповідь дає формула L = B − N + 1",
              12, GREY, "middle", style="italic")
    s += _canon_circuit()
    s += rect(590, 120, 200, 214, "#f6f8fc", INK, 1.4, 10)
    s += text(690, 150, "N = 3 вузли", 14, INK, "middle", "bold")
    s += text(690, 169, "A, B, C", 10, GREY, "middle")
    s += text(690, 199, "B = 4 гілки", 14, INK, "middle", "bold")
    s += text(690, 218, "V, R₁, R₂, R₃", 10, GREY, "middle")
    s += line(610, 236, 770, 236, FAINT, 1.4)
    s += text(690, 262, "L = B − N + 1", 14.5, GREEN, "middle", "bold")
    s += text(690, 284, "= 4 − 3 + 1 = 2", 14, GREEN, "middle", "bold")
    s += text(690, 304, "незалежні контури", 10, GREY, "middle")
    s += text(690, 324, "(споріднено з формулою Ейлера)", 9, GREY, "middle", style="italic")
    save("fig-4-1-5-count.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до §4.1 — Ейлер і сім мостів Кенігсберга.  Рис. 4.1і.N
# ════════════════════════════════════════════════════════════════════════════

def _bow(x1, y1, x2, y2, bow=0.0, color=INK, w=2.4):
    """Дуга між двома точками з вигином bow (px) перпендикулярно до хорди."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    px, py = -dy / L, dx / L
    cx, cy = mx + px * bow, my + py * bow
    return (f'<path d="M {x1:.1f} {y1:.1f} Q {cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"/>\n')


# ── Рис. 4.1і.1 — карта семи мостів ──────────────────────────────────────────
def fig_seven_bridges():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 30, "Сім мостів Кенігсберга (1736)", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "чи можна пройти кожним мостом рівно раз і повернутися на початок?",
              12, GREY, "middle", style="italic")
    LAND, WATER, BR = "#e8d9b8", "#cfe0f0", "#b9b9b9"
    # вода
    s += rect(60, 150, 740, 158, WATER, "#9bb8d0", 1.5, 8)
    s += text(95, 230, "р. Прегель", 11, "#5b7fa0", "start", "bold", "italic")
    # береги
    s += rect(60, 92, 740, 58, LAND, "#b89a5e", 1.6, 6)
    s += text(78, 122, "A — північний берег", 12, INK, "start", "bold")
    s += rect(60, 308, 740, 58, LAND, "#b89a5e", 1.6, 6)
    s += text(78, 342, "B — південний берег", 12, INK, "start", "bold")
    # острови
    s += rect(300, 205, 175, 48, LAND, "#b89a5e", 1.6, 10)
    s += text(387, 233, "C (острів)", 12, INK, "middle", "bold")
    s += rect(590, 200, 120, 58, LAND, "#b89a5e", 1.6, 10)
    s += text(650, 233, "D", 13, INK, "middle", "bold")
    # мости (7)
    def bridge(x, y0, y1):
        return rect(x - 9, y0, 18, y1 - y0, BR, "#8f8f8f", 1.4, 4)

    def hbridge(x0, x1, y):
        return rect(x0, y - 9, x1 - x0, 18, BR, "#8f8f8f", 1.4, 4)

    s += bridge(345, 150, 205)   # A–C 1
    s += bridge(430, 150, 205)   # A–C 2
    s += bridge(345, 253, 308)   # B–C 1
    s += bridge(430, 253, 308)   # B–C 2
    s += bridge(650, 150, 200)   # A–D
    s += bridge(650, 258, 308)   # B–D
    s += hbridge(475, 590, 229)  # C–D
    s += text(W / 2, H - 14, "Сім мостів, чотири землі (A, B, C, D). Спробуйте — і переконаєтесь, що не виходить.",
              11, GREY, "middle", style="italic")
    save("fig-4-1i-1-seven-bridges.svg", s)


# ── Рис. 4.1і.2 — від мапи до графа ──────────────────────────────────────────
def fig_bridges_to_graph():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Ейлерів стрибок: від мапи до графа", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "викинути відстані й форму — лишити тільки що-з-чим-з'єднано",
              12, GREY, "middle", style="italic")
    edges = [("A", "C", 16), ("A", "C", -16), ("B", "C", 16), ("B", "C", -16),
             ("A", "D", 0), ("B", "D", 0), ("C", "D", 0)]
    Lpos = {"A": (230, 110), "B": (230, 320), "C": (150, 215), "D": (320, 215)}
    Rpos = {"A": (630, 110), "B": (630, 320), "C": (550, 215), "D": (720, 215)}
    # ліворуч: землі-блоби з товстими мостами
    for a, b, bw in edges:
        s += _bow(*Lpos[a], *Lpos[b], bw, BR if False else "#b9b9b9", 7)
    for k, (x, y) in Lpos.items():
        s += rect(x - 26, y - 18, 52, 36, "#e8d9b8", "#b89a5e", 1.6, 9)
        s += text(x, y + 5, k, 13, INK, "middle", "bold")
    s += text(230, 372, "землі + мости (мапа)", 11, GREY, "middle", style="italic")
    # стрілка
    s += arrow(388, 215, 452, 215, INK, 2.4)
    s += text(420, 200, "лишаємо", 9.5, GREY, "middle", style="italic")
    s += text(420, 240, "зв'язки", 9.5, GREY, "middle", style="italic")
    # праворуч: граф (вершини-точки, ребра-лінії)
    for a, b, bw in edges:
        s += _bow(*Rpos[a], *Rpos[b], bw, INK, 2.2)
    for k, (x, y) in Rpos.items():
        s += circle(x, y, 13, BLUE, INK, 2)
        s += text(x, y + 4, k, 12, "#fff", "middle", "bold")
    s += text(630, 372, "вершини + ребра (граф)", 11, GREY, "middle", style="italic")
    s += rect(70, 300, 300, 56, "#eef7f0", GREEN, 1.6, 10)
    s += text(220, 322, "Землі → точки (вершини),", 11.5, INK, "middle", "bold")
    s += text(220, 340, "мости → лінії (ребра). Так постала теорія графів.", 10.5, GREY, "middle", style="italic")
    save("fig-4-1i-2-bridges-to-graph.svg", s)


# ── Рис. 4.1і.3 — доказ неможливості: парність степенів ──────────────────────
def fig_even_odd():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Чому це неможливо: рахунок парності", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "проходячи землю наскрізь, витрачаєш 2 мости — тож потрібне ПАРНЕ їх число",
              12, GREY, "middle", style="italic")
    # вершини зі степенями (усі непарні)
    verts = [("A", 230, 120, 3), ("B", 230, 300, 3), ("C", 150, 210, 5), ("D", 330, 210, 3)]
    edges = [("A", "C", 16), ("A", "C", -16), ("B", "C", 16), ("B", "C", -16),
             ("A", "D", 0), ("B", "D", 0), ("C", "D", 0)]
    P = {k: (x, y) for k, x, y, d in verts}
    for a, b, bw in edges:
        s += _bow(*P[a], *P[b], bw, "#c9c9c9", 2)
    for k, x, y, d in verts:
        s += circle(x, y, 16, RED, INK, 2)
        s += text(x, y + 5, str(d), 14, "#fff", "middle", "bold")
        s += text(x, y - 24, k, 12, INK, "middle", "bold")
    s += text(240, 360, "степінь = число мостів; усі чотири НЕПАРНІ (3, 3, 5, 3)", 11, RED, "middle", "bold")
    # правило + вердикт
    s += rect(470, 96, 360, 120, "#f6f8fc", INK, 1.5, 12)
    s += text(650, 122, "Правило Ейлера", 13.5, INK, "middle", "bold")
    s += text(490, 148, "• обхід із поверненням можливий, лише", 11, INK, "start")
    s += text(505, 165, "якщо КОЖНА вершина має парний степінь;", 11, INK, "start")
    s += text(490, 188, "• допустимо щонайбільше 2 непарні", 11, INK, "start")
    s += text(505, 205, "(і то лише як старт та фініш).", 11, INK, "start")
    s += rect(470, 232, 360, 70, "#fbecea", RED, 2, 12)
    s += text(650, 258, "Тут непарних аж ЧОТИРИ.", 14, RED, "middle", "bold")
    s += text(650, 282, "Отже, пройти кожним мостом раз — НЕМОЖЛИВО.", 11.5, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Ейлер довів це, не перебираючи маршрути, — самим рахунком парності. У цьому й сила графа.",
              11, GREY, "middle", style="italic")
    save("fig-4-1i-3-even-odd.svg", s)


# ── Рис. 4.1і.4 — електричне коло теж граф ───────────────────────────────────
def fig_circuit_is_graph():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Електричне коло — теж граф", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "вузли = вершини, гілки = ребра; тому топологія §4.1 — це Ейлерова ідея",
              12, GREY, "middle", style="italic")
    # граф канонічного кола: A,B,C; A–C двічі (V,R₃), A–B (R₁), B–C (R₂)
    P = {"A": (250, 150), "B": (500, 150), "C": (375, 300)}
    s += _bow(*P["A"], *P["C"], 34, INK, 2.2)
    s += _bow(*P["A"], *P["C"], -34, INK, 2.2)
    s += _bow(*P["A"], *P["B"], 0, INK, 2.2)
    s += _bow(*P["B"], *P["C"], 0, INK, 2.2)
    s += text(255, 235, "V", 12, RED, "middle", "bold", "italic")
    s += text(360, 230, "R₃", 12, INK, "middle", "bold", "italic")
    s += text(375, 138, "R₁", 12, INK, "middle", "bold", "italic")
    s += text(458, 235, "R₂", 12, INK, "middle", "bold", "italic")
    for k, (x, y) in P.items():
        s += circle(x, y, 15, BLUE, INK, 2)
        s += text(x, y + 5, k, 13, "#fff", "middle", "bold")
    s += rect(560, 150, 230, 120, "#eef7f0", GREEN, 1.6, 12)
    s += text(675, 176, "N = 3 вершини (вузли)", 12, INK, "middle", "bold")
    s += text(675, 198, "B = 4 ребра (гілки)", 12, INK, "middle", "bold")
    s += text(675, 228, "L = B − N + 1 = 2", 14, GREEN, "middle", "bold")
    s += text(675, 250, "(незалежні контури)", 10, GREY, "middle", style="italic")
    s += text(W / 2, H - 12, "Та сама формула, що рахує контури кола, виросла з мостів Кенігсберга.",
              11, GREY, "middle", style="italic")
    save("fig-4-1i-4-circuit-is-graph.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.2 — Закон струмів Кірхгофа (KCL).  Рис. 4.2.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 4.2.1 — баланс струмів у вузлі ──────────────────────────────────────
def fig42_node_balance():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Закон струмів: що втікає у вузол — те й витікає", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "сума вхідних струмів дорівнює сумі вихідних", 12, GREY, "middle", style="italic")
    nx, ny = 400, 195
    # входи (ліворуч)
    s += arrow(170, 150, nx - 12, ny - 8, BLUE, 3)
    s += text(210, 138, "I₁ = 5 А", 12.5, BLUE, "middle", "bold")
    s += arrow(170, 245, nx - 12, ny + 8, BLUE, 3)
    s += text(210, 263, "I₂ = 3 А", 12.5, BLUE, "middle", "bold")
    # виходи (праворуч)
    s += arrow(nx + 12, ny - 8, 640, 135, GREEN, 3)
    s += text(660, 130, "I₃ = 4 А", 12.5, GREEN, "start", "bold")
    s += arrow(nx + 14, ny, 650, ny, GREEN, 3)
    s += text(660, ny + 4, "I₄ = 3 А", 12.5, GREEN, "start", "bold")
    s += arrow(nx + 12, ny + 8, 640, 255, GREEN, 3)
    s += text(660, 260, "I₅ = 1 А", 12.5, GREEN, "start", "bold")
    s += circle(nx, ny, 9, INK, INK, 1)
    s += text(nx, ny - 22, "вузол", 11, INK, "middle", "bold")
    s += rect(150, 300, W - 300, 62, "#eaf0fb", BLUE, 1.8, 12)
    s += text(W / 2, 324, "ΣI_вх = ΣI_вих :   5 + 3  =  4 + 3 + 1  =  8 А", 14.5, BLUE, "middle", "bold")
    s += text(W / 2, 348, "те саме як ΣI = 0 :   +5 + 3 − 4 − 3 − 1 = 0", 12, GREY, "middle", style="italic")
    save("fig-4-2-1-node-balance.svg", s)


# ── Рис. 4.2.2 — чому: заряд не накопичується ────────────────────────────────
def fig42_charge_no_pileup():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Чому це так: заряд не накопичується у вузлі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "у вузлі нема де зберігати заряд — тож будь-якої миті вхід = вихід",
              12, GREY, "middle", style="italic")
    nx, ny = 360, 185
    s += line(150, ny, nx, ny, "#cfe0f0", 16)
    s += line(nx, ny, 560, 130, "#cfe0f0", 16)
    s += line(nx, ny, 560, 240, "#cfe0f0", 16)
    s += arrow(160, ny, 300, ny, BLUE, 3)
    s += arrow(nx + 20, ny - 14, 520, 138, BLUE, 3)
    s += arrow(nx + 20, ny + 14, 520, 232, BLUE, 3)
    # заряди-плюсики, що пливуть
    for px in (210, 250, 290):
        s += text(px, ny - 22, "＋", 12, RED, "middle", "bold")
    s += circle(nx, ny, 9, INK, INK, 1)
    s += text(nx, ny + 34, "вузол: ємності нема", 11, INK, "middle", "bold")
    # перекреслене «накопичення»
    s += circle(nx, ny, 30, "none", RED, 2)
    s += line(nx - 22, ny + 22, nx + 22, ny - 22, RED, 2)
    s += rect(120, 290, W - 240, 56, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 312, "Заряд зберігається (його не стає більше чи менше) і йому нема де осісти у вузлі —",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 330, "тому скільки втекло, стільки тієї ж миті й витікає. Це і є перший закон.",
              11, GREY, "middle", style="italic")
    save("fig-4-2-2-charge-no-pileup.svg", s)


# ── Рис. 4.2.3 — знаки: вхід + / вихід − ─────────────────────────────────────
def fig42_sign_convention():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Знаки: домовляємось і пишемо ΣI = 0", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "вхідні струми беремо зі знаком «+», вихідні — зі знаком «−»",
              12, GREY, "middle", style="italic")
    nx, ny = 330, 185
    s += arrow(160, ny, nx - 12, ny, BLUE, 3)
    s += text(225, ny - 12, "I₁", 13, BLUE, "middle", "bold", "italic")
    s += text(225, 150, "+ (вхід)", 10.5, BLUE, "middle", "bold")
    s += arrow(nx + 12, ny - 6, 500, 120, GREEN, 3)
    s += text(470, 112, "I₂", 13, GREEN, "middle", "bold", "italic")
    s += text(420, 150, "− (вихід)", 10.5, GREEN, "middle", "bold")
    s += arrow(nx + 12, ny + 6, 500, 250, GREEN, 3)
    s += text(470, 258, "I₃", 13, GREEN, "middle", "bold", "italic")
    s += text(420, 222, "− (вихід)", 10.5, GREEN, "middle", "bold")
    s += circle(nx, ny, 9, INK, INK, 1)
    s += rect(560, 130, 230, 110, "#f6f8fc", INK, 1.6, 12)
    s += text(675, 160, "+I₁ − I₂ − I₃ = 0", 16, INK, "middle", "bold")
    s += text(675, 190, "знак — це наш вибір;", 11, GREY, "middle", style="italic")
    s += text(675, 208, "головне — застосувати", 11, GREY, "middle", style="italic")
    s += text(675, 226, "його до всіх однаково", 11, GREY, "middle", style="italic")
    save("fig-4-2-3-sign-convention.svg", s)


# ── Рис. 4.2.4 — приклад: знайти невідомий струм ─────────────────────────────
def fig42_find_unknown():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: знайти невідомий струм у вузлі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "три струми відомі — четвертий дає закон струмів", 12, GREY, "middle", style="italic")
    nx, ny = 320, 190
    s += arrow(160, ny, nx - 12, ny, BLUE, 3)
    s += text(225, ny - 12, "5 А (вх)", 11.5, BLUE, "middle", "bold")
    s += arrow(nx + 12, ny - 6, 500, 120, GREEN, 3)
    s += text(515, 116, "2 А", 11.5, GREEN, "start", "bold")
    s += arrow(nx + 12, ny + 6, 500, 260, GREEN, 3)
    s += text(515, 264, "1.5 А", 11.5, GREEN, "start", "bold")
    s += arrow(nx + 14, ny, 500, ny, RED, 3)
    s += text(515, ny + 4, "Iₓ = ?", 12.5, RED, "start", "bold")
    s += circle(nx, ny, 9, INK, INK, 1)
    s += rect(560, 110, 230, 150, "#f6f8fc", INK, 1.6, 12)
    s += text(675, 138, "Iₓ = 5 − 2 − 1.5", 14, INK, "middle", "bold")
    s += rect(585, 158, 180, 40, "#eef7f0", GREEN, 2, 10)
    s += text(675, 184, "Iₓ = 1.5 А", 17, GREEN, "middle", "bold")
    s += text(675, 222, "додатний знак →", 11, GREY, "middle", style="italic")
    s += text(675, 240, "напрямок угадано вірно", 11, GREY, "middle", style="italic")
    save("fig-4-2-4-find-unknown.svg", s)


# ── Рис. 4.2.5 — не лише вузол: будь-яка замкнена межа ────────────────────────
def fig42_supernode():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Не лише вузол: будь-яка замкнена межа", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "сума струмів, що перетинають будь-яку замкнену лінію, дорівнює нулю",
              12, GREY, "middle", style="italic")
    # «хмара» — частина кола
    s += rect(300, 130, 230, 150, "#f3f6fb", BLUE, 2, 70)
    s += text(415, 200, "будь-яка", 12.5, INK, "middle", "bold")
    s += text(415, 220, "частина кола", 12.5, INK, "middle", "bold")
    s += text(415, 250, "(скільки завгодно вузлів)", 10, GREY, "middle", style="italic")
    s += line(300, 130, 530, 280, "none", 0)
    s += text(415, 116, "межа (уявна замкнена лінія)", 10.5, BLUE, "middle", style="italic")
    # струми, що перетинають межу
    s += arrow(170, 175, 300, 175, BLUE, 3)
    s += text(220, 162, "Iₐ = 6 А", 12, BLUE, "middle", "bold")
    s += arrow(530, 165, 660, 140, GREEN, 3)
    s += text(685, 134, "I_b = 4 А", 12, GREEN, "start", "bold")
    s += arrow(530, 235, 660, 260, GREEN, 3)
    s += text(685, 264, "I_c = 2 А", 12, GREEN, "start", "bold")
    s += rect(150, 312, W - 300, 50, "#eaf0fb", BLUE, 1.8, 10)
    s += text(W / 2, 334, "Iₐ = I_b + I_c :   6 = 4 + 2 А", 14, BLUE, "middle", "bold")
    s += text(W / 2, 352, "що ввійшло в область, те й вийшло — хоч би що було всередині.", 10.5, GREY, "middle", style="italic")
    save("fig-4-2-5-supernode.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.3 — Закон напруг Кірхгофа (KVL).  Рис. 4.3.k
# ════════════════════════════════════════════════════════════════════════════

def _loop_circuit():
    """Контур: джерело +12 В (ліворуч), R₁ згори (−7 В), R₂ праворуч (−5 В)."""
    o = line(130, 150, 130, 320, INK, 2.4)
    o += _battery(130, 235, "")
    o += text(104, 232, "12 В", 11.5, RED, "end", "bold")
    o += line(130, 150, 520, 150, COPPER, 2.4)
    o += _resistor(230, 150, 80, 20, "R₁")
    o += text(270, 124, "−7 В", 11, BLUE, "middle", "bold")
    o += rect(508, 200, 24, 70, "#fff", INK, 2, 3)
    o += line(520, 150, 520, 200, COPPER, 2.2)
    o += line(520, 270, 520, 320, COPPER, 2.2)
    o += text(548, 230, "R₂", 12, INK, "start", "bold", "italic")
    o += text(548, 250, "−5 В", 11, BLUE, "start", "bold")
    o += line(130, 320, 520, 320, COPPER, 2.4)
    return o


# ── Рис. 4.3.1 — баланс напруг у контурі ─────────────────────────────────────
def fig43_kvl_statement():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Закон напруг: підйоми = спади по контуру", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "обійди петлю — і сума всіх змін напруги дорівнює нулю", 12, GREY, "middle", style="italic")
    s += _loop_circuit()
    s += _circ_arrow(325, 235, 34, INK, -50, 210, 2)
    s += text(325, 240, "обхід", 10, GREY, "middle", style="italic")
    s += rect(600, 150, 200, 130, "#eaf0fb", BLUE, 1.8, 12)
    s += text(700, 178, "Σпідйомів = Σспадів", 12.5, INK, "middle", "bold")
    s += text(700, 202, "12 = 7 + 5", 16, BLUE, "middle", "bold")
    s += line(620, 218, 780, 218, FAINT, 1.4)
    s += text(700, 242, "або ΣV = 0:", 11.5, INK, "middle", "bold")
    s += text(700, 264, "+12 − 7 − 5 = 0", 14, BLUE, "middle", "bold")
    save("fig-4-3-1-kvl-statement.svg", s)


# ── Рис. 4.3.2 — сходинки потенціалу ─────────────────────────────────────────
def fig43_potential_walk():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 30, "Обхід контуру як «сходинки потенціалу»", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "піднявся на джерелі, опустився на резисторах — і повернувся на ТОЙ САМИЙ рівень",
              12, GREY, "middle", style="italic")
    base = 350      # 0 В
    sc = 18.0       # px на вольт
    s += arrow(90, base + 6, 90, 110, INK, 2)
    s += text(86, 104, "потенціал", 11, INK, "end")
    s += arrow(90, base, 760, base, INK, 2)
    s += text(764, base + 4, "обхід", 11, INK, "start")
    # рівні
    for v in (0, 5, 12):
        y = base - v * sc
        s += line(110, y, 740, y, FAINT, 1.2, "3,3")
        s += text(104, y + 4, f"{v} В", 10, GREY, "end")
    yA, yB, yC = base, base - 12 * sc, base - 5 * sc
    # горизонталі
    s += line(130, yA, 230, yA, GREY, 2)
    s += line(230, yB, 430, yB, GREY, 2)
    s += line(430, yC, 630, yC, GREY, 2)
    s += line(630, yA, 730, yA, GREY, 2)
    # підйом / спади
    s += arrow(230, yA, 230, yB, GREEN, 3)
    s += text(244, (yA + yB) / 2, "+12 В (джерело)", 11, GREEN, "start", "bold")
    s += arrow(430, yB, 430, yC, RED, 3)
    s += text(444, (yB + yC) / 2, "−7 В (R₁)", 11, RED, "start", "bold")
    s += arrow(630, yC, 630, yA, RED, 3)
    s += text(644, (yC + yA) / 2, "−5 В (R₂)", 11, RED, "start", "bold")
    # старт/фініш
    s += circle(130, yA, 5, INK, INK, 1)
    s += text(130, yA + 22, "старт", 10.5, INK, "middle", "bold")
    s += circle(730, yA, 5, GREEN, GREEN, 1)
    s += text(700, yA + 22, "фініш — той самий рівень", 10.5, GREEN, "middle", "bold")
    save("fig-4-3-2-potential-walk.svg", s)


# ── Рис. 4.3.3 — знаки обходу ────────────────────────────────────────────────
def fig43_sign_convention():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Знаки: оберіть напрямок обходу й тримайтесь його", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "джерело з «−» на «+» — підйом (+); резистор за струмом — спад (−)",
              12, GREY, "middle", style="italic")
    s += _loop_circuit()
    s += _circ_arrow(325, 235, 34, INK, -50, 210, 2)
    s += text(325, 240, "обхід", 10, GREY, "middle", style="italic")
    s += text(150, 300, "+ (підйом)", 10.5, GREEN, "middle", "bold")
    s += text(270, 178, "− (спад)", 10.5, RED, "middle", "bold")
    s += text(470, 235, "− (спад)", 10.5, RED, "start", "bold")
    s += rect(600, 150, 200, 130, "#f6f8fc", INK, 1.6, 12)
    s += text(700, 176, "Правило знаків", 12.5, INK, "middle", "bold")
    s += text(615, 200, "• джерело −→+ : +", 11, GREEN, "start", "bold")
    s += text(615, 222, "• джерело +→− : −", 11, RED, "start", "bold")
    s += text(615, 244, "• резистор за I : −", 11, RED, "start", "bold")
    s += text(615, 266, "• проти I : +", 11, GREEN, "start", "bold")
    save("fig-4-3-3-sign-convention.svg", s)


# ── Рис. 4.3.4 — приклад: знайти невідому напругу ────────────────────────────
def fig43_find_unknown():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: знайти невідому напругу в контурі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "джерело й частина спадів відомі — решту дає закон напруг", 12, GREY, "middle", style="italic")
    # коло
    s += line(130, 140, 130, 300, INK, 2.4)
    s += _battery(130, 220, "")
    s += text(104, 218, "12 В", 11.5, RED, "end", "bold")
    s += line(130, 140, 470, 140, COPPER, 2.4)
    s += _resistor(230, 140, 80, 20, "R₁")
    s += text(270, 116, "8 В", 11, BLUE, "middle", "bold")
    s += rect(458, 180, 24, 80, "#fff", INK, 2, 3)
    s += line(470, 140, 470, 180, COPPER, 2.2)
    s += line(470, 260, 470, 300, COPPER, 2.2)
    s += text(498, 215, "R₂", 12, INK, "start", "bold", "italic")
    s += text(498, 235, "Vₓ = ?", 12, RED, "start", "bold")
    s += line(130, 300, 470, 300, COPPER, 2.4)
    s += _circ_arrow(300, 220, 30, INK, -50, 210, 2)
    # розрахунок
    s += rect(560, 140, 230, 130, "#f6f8fc", INK, 1.6, 12)
    s += text(675, 168, "+12 − 8 − Vₓ = 0", 14, INK, "middle", "bold")
    s += rect(590, 188, 170, 40, "#eef7f0", GREEN, 2, 10)
    s += text(675, 214, "Vₓ = 4 В", 17, GREEN, "middle", "bold")
    s += text(675, 250, "решта напруги припадає на R₂", 10, GREY, "middle", style="italic")
    save("fig-4-3-4-find-unknown.svg", s)


# ── Рис. 4.3.5 — послідовні резистори ділять напругу ─────────────────────────
def fig43_series_divider():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Наслідок: послідовні резистори ділять напругу", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "більший опір — більший спад; напруга ділиться пропорційно опорам",
              12, GREY, "middle", style="italic")
    # коло
    s += line(120, 140, 120, 300, INK, 2.4)
    s += _battery(120, 220, "")
    s += text(96, 218, "12 В", 11, RED, "end", "bold")
    s += line(120, 140, 430, 140, COPPER, 2.4)
    s += _resistor(190, 140, 80, 20, "R₁ = 2 кΩ")
    s += text(230, 116, "8 В", 11, BLUE, "middle", "bold")
    s += rect(418, 180, 24, 80, "#fff", INK, 2, 3)
    s += line(430, 140, 430, 180, COPPER, 2.2)
    s += line(430, 260, 430, 300, COPPER, 2.2)
    s += text(458, 212, "R₂ = 1 кΩ", 11, INK, "start", "bold", "italic")
    s += text(458, 232, "4 В", 11, BLUE, "start", "bold")
    s += line(120, 300, 430, 300, COPPER, 2.4)
    # пропорційна смуга
    s += text(610, 140, "Поділ 12 В:", 12, INK, "middle", "bold")
    s += rect(560, 155, 100, 90, "#cfe0f0", BLUE, 1.6, 4)
    s += text(610, 205, "R₁: 8 В", 12, INK, "middle", "bold")
    s += rect(560, 245, 100, 45, "#dcead8", GREEN, 1.6, 4)
    s += text(610, 273, "R₂: 4 В", 12, INK, "middle", "bold")
    s += text(610, 308, "2 : 1 опори → 2 : 1 напруги", 10, GREY, "middle", style="italic")
    s += rect(690, 165, 110, 120, "#fffdf2", ORANGE, 1.5, 10)
    s += text(745, 190, "Vᵢ = V·Rᵢ/ΣR", 12, INK, "middle", "bold")
    s += text(745, 218, "8 = 12·2/3", 11, GREY, "middle")
    s += text(745, 238, "4 = 12·1/3", 11, GREY, "middle")
    s += text(745, 268, "(подільник, §4.6)", 9.5, GREY, "middle", style="italic")
    save("fig-4-3-5-series-divider.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.4 — Послідовне з'єднання.  Рис. 4.4.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 4.4.1 — два визначальні факти ───────────────────────────────────────
def fig44_series_two_facts():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Послідовно: струм один, напруги додаються", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "два визначальні факти — прямі наслідки законів Кірхгофа", 12, GREY, "middle", style="italic")
    s += line(110, 150, 110, 300, INK, 2.4)
    s += _battery(110, 225, "")
    s += text(84, 222, "V", 12, RED, "end", "bold")
    s += line(110, 150, 710, 150, COPPER, 2.4)
    s += _resistor(170, 150, 70, 20, "R₁")
    s += text(205, 128, "V₁", 11, BLUE, "middle", "bold")
    s += _resistor(330, 150, 70, 20, "R₂")
    s += text(365, 128, "V₂", 11, BLUE, "middle", "bold")
    s += _resistor(490, 150, 70, 20, "R₃")
    s += text(525, 128, "V₃", 11, BLUE, "middle", "bold")
    s += line(710, 150, 710, 300, INK, 2.4)
    s += line(110, 300, 710, 300, COPPER, 2.4)
    for ax in (130, 290, 450, 610):
        s += arrow(ax, 150, ax + 22, 150, RED, 2)
    s += text(648, 168, "I — один і той самий", 11, RED, "start", "bold")
    s += rect(150, 330, 520, 42, "#eaf0fb", BLUE, 1.6, 10)
    s += text(410, 356, "①  струм I — однаковий у кожному     ②  V = V₁ + V₂ + V₃", 13, INK, "middle", "bold")
    save("fig-4-4-1-series-two-facts.svg", s)


# ── Рис. 4.4.2 — чому опори додаються ────────────────────────────────────────
def fig44_req_derivation():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Чому опори додаються: R_екв = R₁ + R₂ + R₃", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "спільний струм + закон Ома на кожному → опори складаються", 12, GREY, "middle", style="italic")
    s += line(90, 150, 90, 280, INK, 2.2)
    s += _battery(90, 215, "")
    s += text(68, 212, "V", 10.5, RED, "end", "bold")
    s += line(90, 150, 340, 150, COPPER, 2.2)
    s += _resistor(130, 150, 52, 16, "R₁")
    s += _resistor(210, 150, 52, 16, "R₂")
    s += _resistor(290, 150, 48, 16, "R₃")
    s += line(340, 150, 340, 280, INK, 2.2)
    s += line(90, 280, 340, 280, COPPER, 2.2)
    s += arrow(108, 150, 128, 150, RED, 1.8)
    s += text(108, 138, "I", 10, RED, "middle", "bold", "italic")
    s += rect(400, 100, 390, 180, "#f6f8fc", INK, 1.6, 12)
    s += text(420, 132, "спільний струм I (однаковий скрізь)", 12, INK, "start")
    s += text(420, 162, "V₁ = I·R₁,   V₂ = I·R₂,   V₃ = I·R₃", 12.5, INK, "start", "bold")
    s += text(420, 196, "V = V₁ + V₂ + V₃ = I·(R₁+R₂+R₃)", 12.5, INK, "start", "bold")
    s += rect(420, 218, 350, 44, "#eef7f0", GREEN, 2, 10)
    s += text(595, 246, "R_екв = R₁ + R₂ + R₃", 15, GREEN, "middle", "bold")
    save("fig-4-4-2-req-derivation.svg", s)


# ── Рис. 4.4.3 — три резистори = один еквівалентний ──────────────────────────
def fig44_equivalent():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 30, "Три послідовні резистори = один еквівалентний", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "для джерела немає різниці — важить лише сума опорів", 12, GREY, "middle", style="italic")
    s += line(70, 150, 100, 150, COPPER, 2.4)
    s += _resistor(100, 150, 50, 18, "R₁")
    s += _resistor(165, 150, 50, 18, "R₂")
    s += _resistor(230, 150, 50, 18, "R₃")
    s += line(280, 150, 320, 150, COPPER, 2.4)
    s += text(195, 200, "100 + 220 + 330 Ω", 11, GREY, "middle", style="italic")
    s += text(410, 162, "≡", 36, INK, "middle", "bold")
    s += line(500, 150, 560, 150, COPPER, 2.4)
    s += _resistor(560, 150, 120, 30, "")
    s += text(620, 150 + 4, "R_екв = 650 Ω", 12.5, INK, "middle", "bold")
    s += line(680, 150, 740, 150, COPPER, 2.4)
    s += rect(150, 250, W - 300, 50, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 272, "Послідовне з'єднання ЗАВЖДИ збільшує опір:", 12.5, INK, "middle", "bold")
    s += text(W / 2, 290, "R_екв більший за будь-який окремий резистор у ланцюжку.", 10.5, GREY, "middle", style="italic")
    save("fig-4-4-3-equivalent.svg", s)


# ── Рис. 4.4.4 — приклад розрахунку ──────────────────────────────────────────
def fig44_worked():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: розрахувати послідовне коло", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "R₁=100, R₂=220, R₃=330 Ω під 12 В — знайти струм і спади", 12, GREY, "middle", style="italic")
    s += line(100, 140, 100, 290, INK, 2.4)
    s += _battery(100, 215, "")
    s += text(76, 212, "12 В", 11, RED, "end", "bold")
    s += line(100, 140, 430, 140, COPPER, 2.4)
    s += _resistor(140, 140, 70, 18, "R₁")
    s += _resistor(240, 140, 70, 18, "R₂")
    s += _resistor(345, 140, 70, 18, "R₃")
    s += line(430, 140, 430, 290, INK, 2.4)
    s += line(100, 290, 430, 290, COPPER, 2.4)
    s += arrow(118, 140, 138, 140, RED, 1.8)
    s += rect(470, 96, 320, 200, "#f6f8fc", INK, 1.6, 12)
    rows = ["R_екв = 100+220+330 = 650 Ω",
            "I = V / R_екв = 12 / 650 ≈ 18.5 мА",
            "V₁ = I·R₁ ≈ 1.85 В",
            "V₂ = I·R₂ ≈ 4.07 В",
            "V₃ = I·R₃ ≈ 6.08 В"]
    yy = 128
    for r in rows:
        s += text(488, yy, r, 12.5, INK, "start", "bold" if r.startswith("R_екв") or r.startswith("I =") else "normal")
        yy += 30
    s += rect(488, 262, 284, 26, "#eef7f0", GREEN, 1.6, 8)
    s += text(630, 280, "перевірка: 1.85+4.07+6.08 ≈ 12 В ✓", 11, GREEN, "middle", "bold")
    save("fig-4-4-4-worked.svg", s)


# ── Рис. 4.4.5 — де це працює ────────────────────────────────────────────────
def fig44_applications():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Де працює послідовне з'єднання", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "обмеження струму, складання опорів — і слабке місце ланцюжка", 12, GREY, "middle", style="italic")
    # 1) струмообмежувальний резистор + LED
    s += text(150, 92, "Обмеження струму", 12.5, INK, "middle", "bold")
    s += line(70, 130, 110, 130, COPPER, 2.2)
    s += _resistor(110, 130, 56, 18, "R")
    s += line(166, 130, 200, 130, COPPER, 2.2)
    s += polygon([(200, 120), (200, 142), (222, 131)], INK)
    s += line(222, 118, 222, 144, INK, 2.6)
    s += line(222, 130, 250, 130, COPPER, 2.2)
    s += text(150, 175, "R послідовно з LED", 10, GREY, "middle")
    s += text(150, 191, "тримає струм у нормі", 10, GREY, "middle")
    # 2) гірлянда: одна згасла — всі темні
    s += text(490, 92, "Гірлянда (слабке місце)", 12.5, INK, "middle", "bold")
    bx = 360
    s += line(bx, 130, 620, 130, "#bdbdbd", 2)
    for i in range(6):
        cx = bx + 24 + i * 40
        col = "#bdbdbd"
        s += circle(cx, 130, 9, col, "#8f8f8f", 1.5)
        if i == 3:
            s += line(cx - 7, 123, cx + 7, 137, RED, 2.4)
            s += line(cx - 7, 137, cx + 7, 123, RED, 2.4)
    s += text(490, 168, "одна лампа перегоріла —", 10, RED, "middle", "bold")
    s += text(490, 184, "коло розірване, усі згасли", 10, GREY, "middle", style="italic")
    # 3) послідовні резистори = довший
    s += text(740, 92, "Як один довший", 12.5, INK, "middle", "bold")
    s += rect(666, 122, 50, 16, COPPER, "#9c6b48", 1.4, 3)
    s += rect(720, 122, 50, 16, COPPER, "#9c6b48", 1.4, 3)
    s += text(742, 158, "=", 16, INK, "middle", "bold")
    s += rect(666, 176, 104, 16, COPPER, "#9c6b48", 1.4, 3)
    s += text(740, 214, "довше → більший опір", 10, GREY, "middle")
    s += text(740, 230, "(R = ρL/A, §3.3)", 9.5, GREY, "middle", style="italic")
    s += rect(120, 300, W - 240, 50, "#f6f8fc", INK, 1.4, 10)
    s += text(W / 2, 322, "Послідовно ставлять, щоб обмежити струм, скласти опір чи напругу —",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 340, "та пам'ятають: розрив у будь-якій ланці гасить усе коло.", 10.5, GREY, "middle", style="italic")
    save("fig-4-4-5-applications.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.5 — Паралельне з'єднання.  Рис. 4.5.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 4.5.1 — два визначальні факти ───────────────────────────────────────
def fig45_two_facts():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Паралельно: напруга одна, струми додаються", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "два визначальні факти — знову наслідки законів Кірхгофа", 12, GREY, "middle", style="italic")
    s += line(110, 150, 110, 310, INK, 2.4)
    s += _battery(110, 230, "")
    s += text(84, 227, "V", 12, RED, "end", "bold")
    s += line(110, 150, 660, 150, COPPER, 2.4)
    s += line(110, 310, 660, 310, COPPER, 2.4)
    s += arrow(150, 150, 210, 150, RED, 2.4)
    s += text(180, 138, "I", 11, RED, "middle", "bold", "italic")
    for cx, lab, ci in [(280, "R₁", "I₁"), (430, "R₂", "I₂"), (580, "R₃", "I₃")]:
        s += _vresistor(cx, 196, 264, lab)
        s += line(cx, 150, cx, 196, COPPER, 2.2)
        s += line(cx, 264, cx, 310, COPPER, 2.2)
        s += arrow(cx, 168, cx, 188, GREEN, 2)
        s += text(cx + 16, 178, ci, 10.5, GREEN, "start", "bold")
    s += line(632, 150, 632, 310, BLUE, 1.4, "4,3")
    s += text(648, 232, "V", 12, BLUE, "start", "bold")
    s += rect(150, 332, 520, 40, "#eaf0fb", BLUE, 1.6, 10)
    s += text(410, 357, "①  напруга V — однакова на кожній гілці     ②  I = I₁ + I₂ + I₃", 12.5, INK, "middle", "bold")
    save("fig-4-5-1-parallel-two-facts.svg", s)


# ── Рис. 4.5.2 — чому провідності додаються ──────────────────────────────────
def fig45_conductance_add():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Чому додаються провідності: 1/R_екв = Σ 1/Rᵢ", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "спільна напруга + закон Ома на кожній гілці → складаються 1/R", 12, GREY, "middle", style="italic")
    s += line(80, 150, 80, 270, INK, 2.2)
    s += _battery(80, 210, "")
    s += line(80, 150, 300, 150, COPPER, 2.2)
    s += line(80, 270, 300, 270, COPPER, 2.2)
    for cx in (170, 230, 290):
        s += _vresistor(cx, 180, 240, "")
        s += line(cx, 150, cx, 180, COPPER, 2)
        s += line(cx, 240, cx, 270, COPPER, 2)
    s += rect(380, 96, 410, 190, "#f6f8fc", INK, 1.6, 12)
    s += text(400, 128, "спільна напруга V (на кожній гілці)", 12, INK, "start")
    s += text(400, 158, "I₁ = V/R₁,   I₂ = V/R₂,   I₃ = V/R₃", 12.5, INK, "start", "bold")
    s += text(400, 192, "I = I₁+I₂+I₃ = V·(1/R₁+1/R₂+1/R₃)", 12, INK, "start", "bold")
    s += rect(400, 214, 370, 56, "#eef7f0", GREEN, 2, 10)
    s += text(585, 238, "1/R_екв = 1/R₁ + 1/R₂ + 1/R₃", 13.5, GREEN, "middle", "bold")
    s += text(585, 258, "провідності G = 1/R просто додаються", 10, GREY, "middle", style="italic")
    save("fig-4-5-2-conductance-add.svg", s)


# ── Рис. 4.5.3 — зручні випадки ──────────────────────────────────────────────
def fig45_shortcuts():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Два зручні випадки на щодень", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "для двох резисторів і для кількох однакових — без дробів", 12, GREY, "middle", style="italic")
    s += line(W / 2, 80, W / 2, H - 70, FAINT, 1.4, "4,5")
    # дві штуки
    s += text(215, 104, "Два резистори", 13.5, INK, "middle", "bold")
    s += rect(110, 130, 210, 60, "#f6f8fc", INK, 1.5, 10)
    s += text(215, 165, "R_екв = R₁·R₂ / (R₁+R₂)", 13.5, INK, "middle", "bold")
    s += text(215, 220, "«добуток на суму»", 11, GREY, "middle", style="italic")
    s += text(215, 250, "6 Ω ∥ 3 Ω = 18/9 = 2 Ω", 13, GREEN, "middle", "bold")
    # n однакових
    s += text(610, 104, "n однакових", 13.5, INK, "middle", "bold")
    s += rect(505, 130, 210, 60, "#f6f8fc", INK, 1.5, 10)
    s += text(610, 165, "R_екв = R / n", 14, INK, "middle", "bold")
    s += text(610, 220, "поділи на кількість", 11, GREY, "middle", style="italic")
    s += text(610, 250, "три по 100 Ω = 33.3 Ω", 13, GREEN, "middle", "bold")
    s += rect(170, 296, W - 340, 44, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 322, "Паралельне з'єднання ЗАВЖДИ зменшує опір: R_екв менший за найменший із них.",
              12, INK, "middle", "bold")
    save("fig-4-5-3-shortcuts.svg", s)


# ── Рис. 4.5.4 — струм ділиться обернено до опору ────────────────────────────
def fig45_current_divider():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Струм ділиться обернено: менший опір — більший струм", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "ширша «труба» пропускає більший потік — так і менший опір бере більший струм",
              12, GREY, "middle", style="italic")
    # вхідний струм
    s += arrow(90, 200, 170, 200, RED, 3)
    s += text(125, 186, "I = 9 А", 12, RED, "middle", "bold")
    s += circle(180, 200, 5, INK, INK, 1)
    # гілка 1 — товста труба (малий опір, великий струм)
    s += line(180, 200, 320, 140, "#cfe0f0", 22)
    s += arrow(210, 188, 320, 142, BLUE, 3)
    s += _resistor(330, 132, 70, 22, "R₁ = 3 Ω")
    s += text(470, 130, "I₁ = 6 А", 12, BLUE, "start", "bold")
    # гілка 2 — тонка труба (великий опір, малий струм)
    s += line(180, 200, 320, 260, "#cfe0f0", 12)
    s += arrow(214, 212, 320, 258, BLUE, 2.4)
    s += _resistor(330, 250, 70, 18, "R₂ = 6 Ω")
    s += text(470, 250, "I₂ = 3 А", 12, BLUE, "start", "bold")
    s += rect(560, 150, 230, 110, "#f6f8fc", INK, 1.6, 12)
    s += text(675, 176, "I₁ = I · R₂/(R₁+R₂)", 12.5, INK, "middle", "bold")
    s += text(675, 200, "= 9 · 6/9 = 6 А", 12, GREY, "middle")
    s += text(675, 226, "менший опір (3 Ω) бере", 10.5, INK, "middle")
    s += text(675, 242, "удвічі більший струм", 10.5, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Зверніть увагу: у формулі частки опір «чужої» гілки — поділ ОБЕРНЕНИЙ (подільник струму, §4.7).",
              10.5, GREY, "middle", style="italic")
    save("fig-4-5-4-current-divider.svg", s)


# ── Рис. 4.5.5 — де це працює: домашня проводка ──────────────────────────────
def fig45_applications():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Де працює паралельне: уся домашня проводка", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "прилади ввімкнені паралельно: кожен на повній напрузі й незалежний",
              12, GREY, "middle", style="italic")
    s += line(90, 110, 90, 250, INK, 2.4)
    s += _battery(90, 180, "")
    s += text(66, 177, "230 В", 10.5, RED, "end", "bold")
    s += line(90, 110, 800, 110, COPPER, 2.6)
    s += line(90, 250, 800, 250, COPPER, 2.6)

    def lamp(cx, on, label, sw_open=False):
        o = line(cx, 110, cx, 150, COPPER, 2.2)
        if sw_open:
            o += line(cx, 150, cx + 14, 138, INK, 2.4)   # вимикач розімкнений
            o += circle(cx, 150, 3, INK, INK, 1)
            o += circle(cx, 162, 3, INK, INK, 1)
            o += line(cx, 162, cx, 178, COPPER, 2.2)
            cy = 200
        else:
            cy = 180
        fill = "#ffe88a" if on else "#dcdcdc"
        o += circle(cx, cy, 18, fill, INK, 2)
        o += line(cx - 12, cy - 12, cx + 12, cy + 12, INK, 1.4)
        o += line(cx - 12, cy + 12, cx + 12, cy - 12, INK, 1.4)
        o += line(cx, cy + 18, cx, 250, COPPER, 2.2)
        o += text(cx, 280, label, 10.5, INK, "middle", "bold")
        o += text(cx, 296, "230 В" if True else "", 9.5, GREY, "middle")
        return o

    s += lamp(230, True, "лампа")
    s += lamp(400, True, "холодильник")
    s += lamp(570, False, "світло (вимкнено)", sw_open=True)
    s += lamp(740, True, "зарядка")
    s += rect(150, 316, W - 300, 38, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 340, "Вимкнув одне — інші працюють далі (на відміну від послідовної гірлянди §4.4).",
              11.5, INK, "middle", "bold")
    save("fig-4-5-5-applications.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.6 — Дільник напруги.  Рис. 4.6.k
# ════════════════════════════════════════════════════════════════════════════

def _ground(x, y):
    o = line(x, y, x, y + 8, INK, 2)
    o += line(x - 14, y + 8, x + 14, y + 8, INK, 2)
    o += line(x - 9, y + 13, x + 9, y + 13, INK, 2)
    o += line(x - 4, y + 18, x + 4, y + 18, INK, 2)
    return o


def _divider(x, ytop, V_lbl, r1, r2, vout_lbl, tapcol=GREEN):
    """Вертикальний дільник: V_lbl згори, R₁, відвід, R₂, земля."""
    o = text(x, ytop - 8, V_lbl, 11, RED, "middle", "bold")
    o += line(x, ytop, x, ytop + 18, INK, 2.2)
    o += _vresistor(x, ytop + 18, ytop + 78, r1)
    tap = ytop + 96
    o += line(x, ytop + 78, x, tap, COPPER, 2.2)
    o += circle(x, tap, 4, tapcol, tapcol, 1)
    o += line(x, tap, x, ytop + 114, COPPER, 2.2)
    o += _vresistor(x, ytop + 114, ytop + 174, r2)
    o += line(x, ytop + 174, x, ytop + 196, INK, 2.2)
    o += _ground(x, ytop + 196)
    o += arrow(x + 12, tap, x + 46, tap, tapcol, 2)
    o += text(x + 50, tap + 4, vout_lbl, 11, tapcol, "start", "bold")
    return o, tap


# ── Рис. 4.6.1 — формула дільника ────────────────────────────────────────────
def fig46_divider_formula():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Дільник напруги: V_вих = V · R₂/(R₁+R₂)", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "два послідовні резистори, а напругу знімають із середньої точки", 12, GREY, "middle", style="italic")
    s += _divider(230, 110, "V_вх = 10 В", "R₁", "R₂", "V_вих")[0]
    s += rect(430, 120, 360, 180, "#f6f8fc", INK, 1.6, 12)
    s += text(610, 150, "той самий струм крізь обидва:", 11.5, INK, "middle")
    s += text(610, 174, "I = V / (R₁ + R₂)", 13.5, INK, "middle", "bold")
    s += text(610, 206, "а знімаємо спад на R₂:", 11.5, INK, "middle")
    s += text(610, 230, "V_вих = I · R₂", 13.5, INK, "middle", "bold")
    s += rect(450, 250, 320, 40, "#eef7f0", GREEN, 2, 10)
    s += text(610, 276, "V_вих = V · R₂ / (R₁ + R₂)", 14.5, GREEN, "middle", "bold")
    save("fig-4-6-1-divider-formula.svg", s)


# ── Рис. 4.6.2 — як вибрати частку ───────────────────────────────────────────
def fig46_choose_ratio():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Частка залежить від відношення опорів", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "V_вих = V · R₂/(R₁+R₂): більший R₂ — ближче до повної напруги", 12, GREY, "middle", style="italic")
    cases = [(150, "R₁ = R₂", "5 В", "½ — порівну"),
             (410, "R₁ мал., R₂ вел.", "7.5 В", "ближче до V"),
             (670, "R₁ вел., R₂ мал.", "2.5 В", "ближче до 0")]
    for x, top, vo, note in cases:
        s += _divider(x, 96, "10 В", "R₁", "R₂", vo)[0]
        s += text(x, 330, top, 11, INK, "middle", "bold")
        s += text(x, 348, note, 10, GREY, "middle", style="italic")
    save("fig-4-6-2-choose-ratio.svg", s)


# ── Рис. 4.6.3 — потенціометр як регульований дільник ────────────────────────
def fig46_potentiometer():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Потенціометр — регульований дільник", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "крутиш ручку — повзунок ділить опір, і V_вих плавно йде від 0 до V",
              12, GREY, "middle", style="italic")
    # доріжка потенціометра (вертикальний прямокутник)
    px = 230
    s += text(px, 92, "V = 10 В", 11, RED, "middle", "bold")
    s += line(px, 100, px, 120, INK, 2.2)
    s += rect(px - 18, 120, 36, 150, "#fff", INK, 2, 4)
    s += line(px, 270, px, 290, INK, 2.2)
    s += _ground(px, 290)
    # повзунок
    wy = 185
    s += polygon([(px + 18, wy), (px + 40, wy - 9), (px + 40, wy + 9)], INK)
    s += line(px + 40, wy, px + 80, wy, GREEN, 2.4)
    s += text(px + 84, wy + 4, "V_вих", 11, GREEN, "start", "bold")
    s += arrow(px + 30, 150, px + 30, 230, GREY, 1.6, "3,3")
    s += text(px + 36, 200, "рух", 9.5, GREY, "start", style="italic")
    # еквівалент
    s += text(560, 110, "= два опори, що міняються:", 12, INK, "middle", "bold")
    s += _divider(560, 130, "V", "верх", "низ", "V_вих")[0]
    s += text(560, 340, "повзунок угорі → V_вих ↑;  унизу → V_вих ↓", 10.5, GREY, "middle", style="italic")
    save("fig-4-6-3-potentiometer.svg", s)


# ── Рис. 4.6.4 — ефект навантаження ──────────────────────────────────────────
def fig46_loading():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Підступ: під навантаженням дільник «просідає»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "приєднане навантаження стає паралельним до R₂ — і V_вих падає",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 40, FAINT, 1.4, "4,5")
    # без навантаження
    s += text(210, 100, "Без навантаження", 13, GREEN, "middle", "bold")
    s += _divider(210, 120, "10 В", "10к", "10к", "5.0 В")[0]
    # з навантаженням
    s += text(600, 100, "З навантаженням 10к", 13, RED, "middle", "bold")
    out = _divider(560, 120, "10 В", "10к", "10к", "")[0]
    s += out
    tap = 120 + 96
    s += line(560, tap, 660, tap, COPPER, 2.2)
    s += rect(648, tap - 30, 24, 60, "#fff", INK, 2, 3)
    s += text(686, tap, "R_н = 10к", 10.5, INK, "start", "bold")
    s += text(686, tap + 16, "(навантаження)", 9, GREY, "start", style="italic")
    s += line(660, tap + 30, 660, tap + 70, INK, 2.2)
    s += _ground(660, tap + 70)
    s += text(560 + 50, tap + 4, "3.33 В", 12, RED, "start", "bold")
    s += rect(120, 350, W - 240, 42, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 376, "Дільник — не джерело! R₂∥R_н = 5к → V_вих = 10·5/15 = 3.33 В. Бери R₁,R₂ малими або буфер.",
              11, INK, "middle", "bold")
    save("fig-4-6-4-loading.svg", s)


# ── Рис. 4.6.5 — давач як дільник ────────────────────────────────────────────
def fig46_sensor():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Дільник читає давач: термістор → напруга", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "опір давача змінюється з умовами — і дільник перетворює це на напругу для АЦП",
              12, GREY, "middle", style="italic")
    px = 220
    s += text(px, 92, "V = 5 В", 11, RED, "middle", "bold")
    s += line(px, 100, px, 118, INK, 2.2)
    # термістор: резистор зі стрілкою
    s += _vresistor(px, 118, 178, "")
    s += line(px - 24, 182, px + 24, 114, ORANGE, 2)   # стрілка-«змінний»
    s += polygon([(px + 24, 114), (px + 16, 116), (px + 22, 124)], ORANGE)
    s += text(px - 30, 150, "термістор R_t", 10.5, INK, "end", "bold")
    tap = 196
    s += line(px, 178, px, tap, COPPER, 2.2)
    s += circle(px, tap, 4, GREEN, GREEN, 1)
    s += line(px, tap, px, 214, COPPER, 2.2)
    s += _vresistor(px, 214, 274, "R")
    s += line(px, 274, px, 292, INK, 2.2)
    s += _ground(px, 292)
    s += arrow(px + 12, tap, px + 70, tap, GREEN, 2.2)
    s += text(px + 76, tap + 4, "V_вих", 11, GREEN, "start", "bold")
    # АЦП
    s += rect(440, tap - 26, 110, 52, "#eef2fb", BLUE, 2, 8)
    s += text(495, tap - 4, "АЦП", 13, BLUE, "middle", "bold")
    s += text(495, tap + 14, "мікроконтролера", 9, INK, "middle")
    s += arrow(360, tap, 438, tap, INK, 2)
    s += rect(600, 150, 200, 110, "#f6f8fc", INK, 1.5, 12)
    s += text(700, 176, "холодніше → R_t ↑", 11, INK, "middle", "bold")
    s += text(700, 198, "→ V_вих змінюється", 11, INK, "middle")
    s += text(700, 226, "контролер зчитує", 10.5, GREY, "middle", style="italic")
    s += text(700, 244, "напругу й знає умову", 10.5, GREY, "middle", style="italic")
    save("fig-4-6-5-sensor.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.7 — Дільник струму.  Рис. 4.7.k
# ════════════════════════════════════════════════════════════════════════════

def _two_branch(ax, bx, y, r1lbl, r2lbl, i1lbl, i2lbl):
    """Дві паралельні гілки між вузлами ax і bx на висоті y."""
    o = circle(ax, y, 4, INK, INK, 1) + circle(bx, y, 4, INK, INK, 1)
    o += line(ax, y, ax, y - 60, COPPER, 2.2) + line(ax, y - 60, ax + 70, y - 60, COPPER, 2.2)
    o += _resistor(ax + 70, y - 60, 80, 20, r1lbl)
    o += line(ax + 150, y - 60, bx, y - 60, COPPER, 2.2) + line(bx, y - 60, bx, y, COPPER, 2.2)
    o += line(ax, y, ax, y + 60, COPPER, 2.2) + line(ax, y + 60, ax + 70, y + 60, COPPER, 2.2)
    o += _resistor(ax + 70, y + 60, 80, 20, r2lbl)
    o += line(ax + 150, y + 60, bx, y + 60, COPPER, 2.2) + line(bx, y + 60, bx, y, COPPER, 2.2)
    o += arrow(ax + 30, y - 60, ax + 62, y - 60, BLUE, 2.2) + text(ax + 40, y - 72, i1lbl, 11, BLUE, "middle", "bold")
    o += arrow(ax + 30, y + 60, ax + 62, y + 60, BLUE, 2.2) + text(ax + 40, y + 78, i2lbl, 11, BLUE, "middle", "bold")
    return o


# ── Рис. 4.7.1 — формула дільника струму ─────────────────────────────────────
def fig47_formula():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Дільник струму: I₁ = I · R₂/(R₁+R₂)", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "струм у вузлі ділиться між паралельними гілками — обернено до опорів", 12, GREY, "middle", style="italic")
    ax, bx, y = 180, 520, 200
    s += arrow(95, y, ax - 4, y, RED, 3)
    s += text(135, y - 14, "I", 12, RED, "middle", "bold", "italic")
    s += _two_branch(ax, bx, y, "R₁", "R₂", "I₁", "I₂")
    s += arrow(bx + 4, y, 600, y, RED, 3)
    s += text(575, y - 14, "I", 12, RED, "middle", "bold", "italic")
    s += rect(625, 116, 180, 160, "#f6f8fc", INK, 1.6, 12)
    s += text(715, 146, "I₁ = I · R₂/(R₁+R₂)", 11.5, INK, "middle", "bold")
    s += text(715, 172, "I₂ = I · R₁/(R₁+R₂)", 11.5, INK, "middle", "bold")
    s += rect(645, 192, 140, 70, "#fbecea", RED, 1.6, 8)
    s += text(715, 214, "Увага: у формулі для I₁", 9.5, RED, "middle", "bold")
    s += text(715, 230, "стоїть R₂ — опір", 9.5, RED, "middle", "bold")
    s += text(715, 246, "ЧУЖОЇ гілки!", 9.5, RED, "middle", "bold")
    save("fig-4-7-1-current-divider-formula.svg", s)


# ── Рис. 4.7.2 — через провідності ───────────────────────────────────────────
def fig47_conductance():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Зрозуміліше — через провідності: Iₖ = I · Gₖ/ΣG", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "струм ділиться ПРЯМО пропорційно провідності гілки (G = 1/R)", 12, GREY, "middle", style="italic")
    s += arrow(70, 200, 130, 200, RED, 3)
    s += text(100, 186, "I", 12, RED, "middle", "bold", "italic")
    s += circle(150, 200, 4, INK, INK, 1)
    s += line(150, 150, 150, 250, INK, 2.2)
    s += line(360, 150, 360, 250, INK, 2.2)
    s += circle(360, 200, 4, INK, INK, 1)
    s += arrow(360, 200, 420, 200, RED, 3)
    branches = [(150, "G₁ велике", 4.5), (200, "G₂", 3), (250, "G₃ мале", 1.8)]
    for yy, lab, wdt in [(160, "G₁ — велике", 5), (200, "G₂", 3), (240, "G₃ — мале", 1.6)]:
        s += line(150, yy, 230, yy, COPPER, 2)
        s += _resistor(230, yy, 60, 14, "")
        s += line(290, yy, 360, yy, COPPER, 2)
        s += arrow(168, yy, 196, yy, BLUE, wdt)
        s += text(330, yy - 12, lab, 9.5, INK, "middle", "bold")
    s += rect(470, 130, 320, 150, "#f6f8fc", INK, 1.6, 12)
    s += text(630, 158, "G = 1/R  (провідність)", 12, INK, "middle", "bold")
    s += text(630, 186, "більша G гілки — більший", 11, INK, "middle")
    s += text(630, 202, "її струм", 11, INK, "middle")
    s += rect(490, 218, 280, 44, "#eef7f0", GREEN, 2, 10)
    s += text(630, 245, "Iₖ = I · Gₖ / (G₁+G₂+…)", 13.5, GREEN, "middle", "bold")
    save("fig-4-7-2-conductance.svg", s)


# ── Рис. 4.7.3 — приклад ─────────────────────────────────────────────────────
def fig47_worked():
    W, H = 820, 350
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: 12 А діляться у 2 Ω ∥ 4 Ω", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "менший опір забирає більший струм", 12, GREY, "middle", style="italic")
    ax, bx, y = 170, 430, 190
    s += arrow(90, y, ax - 4, y, RED, 3)
    s += text(125, y - 14, "12 А", 11.5, RED, "middle", "bold")
    s += _two_branch(ax, bx, y, "2 Ω", "4 Ω", "I₁", "I₂")
    s += arrow(bx + 4, y, 500, y, RED, 3)
    s += rect(540, 110, 250, 160, "#f6f8fc", INK, 1.6, 12)
    s += text(665, 140, "I₁ = 12·4/(2+4) = 8 А", 12.5, INK, "middle", "bold")
    s += text(665, 168, "I₂ = 12·2/(2+4) = 4 А", 12.5, INK, "middle", "bold")
    s += line(560, 184, 770, 184, FAINT, 1.4)
    s += text(665, 208, "перевірка: 8 + 4 = 12 А ✓", 11.5, GREEN, "middle", "bold")
    s += text(665, 240, "менший опір (2 Ω) — удвічі", 10, GREY, "middle", style="italic")
    s += text(665, 256, "більший струм (8 А)", 10, GREY, "middle", style="italic")
    save("fig-4-7-3-worked.svg", s)


# ── Рис. 4.7.4 — шунт амперметра ─────────────────────────────────────────────
def fig47_shunt():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Класика: шунт амперметра", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "малий шунт відводить більшість струму — прилад міряє відому частку, і діапазон ширшає",
              12, GREY, "middle", style="italic")
    ax, bx, y = 200, 560, 200
    s += arrow(100, y, ax - 4, y, RED, 3)
    s += text(140, y - 14, "I = 10 А", 11.5, RED, "middle", "bold")
    s += circle(ax, y, 4, INK, INK, 1)
    s += circle(bx, y, 4, INK, INK, 1)
    # верх: прилад (мала частка)
    s += line(ax, y, ax, y - 60, COPPER, 2.2)
    s += line(ax, y - 60, ax + 120, y - 60, COPPER, 2.2)
    s += circle(ax + 150, y - 60, 22, "#eef2fb", BLUE, 2.2)
    s += text(ax + 150, y - 54, "A", 16, BLUE, "middle", "bold")
    s += line(ax + 172, y - 60, bx, y - 60, COPPER, 2.2)
    s += line(bx, y - 60, bx, y, COPPER, 2.2)
    s += arrow(ax + 30, y - 60, ax + 56, y - 60, GREEN, 2)
    s += text(ax + 70, y - 74, "мала частка (через прилад)", 9.5, GREEN, "start", "bold")
    # низ: шунт (більшість)
    s += line(ax, y, ax, y + 60, COPPER, 2.2)
    s += line(ax, y + 60, ax + 120, y + 60, COPPER, 2.2)
    s += rect(ax + 120, y + 50, 100, 20, "#d7d2c4", INK, 2.4, 3)
    s += text(ax + 170, y + 64, "ШУНТ", 10.5, INK, "middle", "bold")
    s += line(ax + 220, y + 60, bx, y + 60, COPPER, 2.2)
    s += line(bx, y + 60, bx, y, COPPER, 2.2)
    s += arrow(ax + 30, y + 60, ax + 60, y + 60, RED, 4)
    s += text(ax + 80, y + 80, "більшість струму (через малий опір шунта)", 9.5, RED, "start", "bold")
    s += arrow(bx + 4, y, 660, y, RED, 3)
    s += rect(150, 312, W - 300, 42, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 338, "Шунт у паралель робить із чутливого приладу амперметр на великі струми — за дільником струму.",
              11, INK, "middle", "bold")
    save("fig-4-7-4-shunt.svg", s)


# ── Рис. 4.7.5 — двоїстість двох дільників ───────────────────────────────────
def fig47_dual():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Два дільники — дзеркало одне одного", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "дільник напруги (послідовний) ↔ дільник струму (паралельний)", 12, GREY, "middle", style="italic")
    x0, x1, x2 = 70, 300, 560
    s += rect(x1, 80, 250, 40, "#eaf0fb", BLUE, 1.6, 8)
    s += text(x1 + 125, 106, "Дільник НАПРУГИ", 12.5, BLUE, "middle", "bold")
    s += rect(x2, 80, 240, 40, "#fbecea", RED, 1.6, 8)
    s += text(x2 + 120, 106, "Дільник СТРУМУ", 12.5, RED, "middle", "bold")
    rows = [("з'єднання", "послідовне", "паралельне"),
            ("що спільне", "струм", "напруга"),
            ("що ділиться", "напруга (прямо до R)", "струм (обернено до R)"),
            ("формула", "V₂ = V·R₂/(R₁+R₂)", "I₁ = I·R₂/(R₁+R₂)"),
            ("більша частка —", "більшому опору", "меншому опору")]
    yy = 150
    for a, b, c in rows:
        s += text(x0 + 10, yy, a, 11.5, INK, "start", "bold")
        s += text(x1 + 125, yy, b, 11, INK, "middle")
        s += text(x2 + 120, yy, c, 11, INK, "middle")
        s += line(x0, yy + 14, 800, yy + 14, FAINT, 1)
        yy += 44
    s += text(W / 2, H - 14, "Знаєш один — знаєш обидва: поміняй місцями струм↔напругу, опір↔провідність.",
              11, GREY, "middle", style="italic")
    save("fig-4-7-5-dual.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §4.8 — Як розв'язувати коло: метод і приклади.  Рис. 4.8.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 4.8.1 — інструментарій розділу ────────────────────────────────────────
def fig48_toolkit():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Інструментарій: усе, чим розв'язують коло", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "чотири інструменти Розділу 4 працюють разом", 12, GREY, "middle", style="italic")
    cx, cy = 410, 215
    tools = [(195, 130, "Закон Ома", "V = I·R", BLUE),
             (625, 130, "Послідовно / паралельно", "R_екв = ΣR  ·  1/R_екв = Σ1/R", GREEN),
             (195, 300, "Закон струмів (KCL)", "ΣI = 0  у вузлі", RED),
             (625, 300, "Закон напруг (KVL)", "ΣV = 0  у контурі", ORANGE)]
    for x, y, t, f, c in tools:
        s += line(cx, cy, x, y, FAINT, 1.6)
    s += rect(cx - 95, cy - 32, 190, 64, "#1b1b1b", INK, 2, 14)
    s += text(cx, cy - 4, "РОЗВ'ЯЗАТИ", 14, "#fff", "middle", "bold")
    s += text(cx, cy + 18, "КОЛО", 14, "#fff", "middle", "bold")
    for x, y, t, f, c in tools:
        s += rect(x - 130, y - 30, 260, 60, "#f6f8fc", c, 2, 12)
        s += text(x, y - 6, t, 12.5, c, "middle", "bold")
        s += text(x, y + 16, f, 11, INK, "middle", "bold")
    save("fig-4-8-1-toolkit.svg", s)


def _mini_ladder(ox, oy, mid, eqlabel):
    """Компактна сходинка згортання: [V]–[R1]–[пара або один блок]. mid — список міток вертикальних блоків."""
    o = line(ox, oy, ox, oy + 90, INK, 2)
    o += line(ox - 8, oy + 36, ox + 8, oy + 36, INK, 2.4)
    o += line(ox - 5, oy + 50, ox + 5, oy + 50, INK, 3.4)
    o += line(ox, oy, ox + 30, oy, COPPER, 2)
    o += rect(ox + 30, oy - 9, 44, 18, "#fff", INK, 1.8, 3)
    o += text(ox + 52, oy - 14, "R₁", 9.5, INK, "middle", "bold", "italic")
    nx = ox + 74
    o += line(nx, oy, nx + 20 + (len(mid) - 1) * 34, oy, COPPER, 2)
    for i, m in enumerate(mid):
        vx = nx + 20 + i * 34
        o += rect(vx - 9, oy + 18, 18, 44, "#fff", INK, 1.8, 3)
        o += line(vx, oy, vx, oy + 18, COPPER, 1.8)
        o += line(vx, oy + 62, vx, oy + 90, COPPER, 1.8)
        o += text(vx, oy + 44, m, 8.5, INK, "middle", "bold", "italic")
    o += line(ox, oy + 90, nx + 20 + (len(mid) - 1) * 34, oy + 90, COPPER, 2)
    o += text(ox + 60, oy + 116, eqlabel, 10, INK, "middle", "bold")
    return o


# ── Рис. 4.8.2 — згортання крок за кроком ────────────────────────────────────
def fig48_reduction():
    W, H = 880, 320
    s = header(W, H)
    s += text(W / 2, 30, "Стратегія 1: згортати, поки не лишиться один опір", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "паралельні й послідовні групи по черзі замінюють еквівалентом", 12, GREY, "middle", style="italic")
    s += _mini_ladder(70, 110, ["R₂", "R₃"], "1) ціле коло")
    s += text(330, 170, "→", 28, INK, "middle", "bold")
    s += _mini_ladder(380, 110, ["R₂₃"], "2) R₂∥R₃ = R₂₃")
    s += text(610, 170, "→", 28, INK, "middle", "bold")
    # фінальна стадія — лише джерело + один опір
    ox, oy = 670, 110
    s += line(ox, oy, ox, oy + 90, INK, 2)
    s += line(ox - 8, oy + 36, ox + 8, oy + 36, INK, 2.4)
    s += line(ox - 5, oy + 50, ox + 5, oy + 50, INK, 3.4)
    s += line(ox, oy, ox + 110, oy, COPPER, 2)
    s += rect(ox + 40, oy - 12, 60, 24, "#eef7f0", GREEN, 2, 4)
    s += text(ox + 70, oy - 18, "R_екв", 10, GREEN, "middle", "bold", "italic")
    s += line(ox + 110, oy, ox + 110, oy + 90, INK, 2)
    s += line(ox, oy + 90, ox + 110, oy + 90, COPPER, 2)
    s += text(ox + 55, oy + 116, "3) R₁+R₂₃ = R_екв", 10, GREEN, "middle", "bold")
    s += rect(120, 268, W - 240, 40, "#eaf0fb", BLUE, 1.6, 10)
    s += text(W / 2, 293, "Далі: повний струм I = V/R_екв, а тоді «розгортають» назад — дільниками знаходять спади й гілкові струми.",
              11, INK, "middle", "bold")
    save("fig-4-8-2-reduction.svg", s)


# ── Рис. 4.8.3 — приклад згортанням ──────────────────────────────────────────
def fig48_reduction_worked():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Приклад згортанням: R₁ послідовно з (R₂∥R₃)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "12 В, R₁=100, R₂=200, R₃=200 Ω", 12, GREY, "middle", style="italic")
    s += line(110, 130, 110, 300, INK, 2.4)
    s += _battery(110, 215, "")
    s += text(86, 212, "12 В", 11, RED, "end", "bold")
    s += line(110, 130, 250, 130, COPPER, 2.2)
    s += _resistor(170, 130, 60, 18, "R₁=100")
    s += line(250, 130, 430, 130, COPPER, 2.2)
    s += _vresistor(330, 160, 270, "R₂=200")
    s += line(330, 130, 330, 160, COPPER, 2)
    s += line(330, 270, 330, 300, COPPER, 2)
    s += _vresistor(430, 160, 270, "R₃=200", "end")
    s += line(430, 130, 430, 160, COPPER, 2)
    s += line(430, 270, 430, 300, COPPER, 2)
    s += line(110, 300, 430, 300, COPPER, 2.2)
    s += arrow(128, 130, 150, 130, RED, 1.8)
    s += rect(500, 96, 300, 230, "#f6f8fc", INK, 1.6, 12)
    rows = ["R₂∥R₃ = 200·200/400 = 100 Ω",
            "R_екв = R₁ + 100 = 200 Ω",
            "I = V/R_екв = 12/200 = 60 мА",
            "V на R₁ = 0.06·100 = 6 В",
            "V на парі = 12 − 6 = 6 В",
            "I₂ = I₃ = 6/200 = 30 мА"]
    yy = 126
    for r in rows:
        bold = r.startswith("R_екв") or r.startswith("I =")
        s += text(518, yy, r, 12, INK, "start", "bold" if bold else "normal")
        yy += 30
    s += rect(518, 300, 264, 22, "#eef7f0", GREEN, 1.5, 6)
    s += text(650, 316, "перевірка: 30+30 = 60 мА ✓", 10.5, GREEN, "middle", "bold")
    save("fig-4-8-3-reduction-worked.svg", s)


# ── Рис. 4.8.4 — коли не згортається: два джерела ────────────────────────────
def fig48_two_source():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Стратегія 2: систематичні рівняння (коли не згортається)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "два джерела — послідовно/паралельно не спрощуються; пишемо KCL + KVL", 12, GREY, "middle", style="italic")
    # коло: V1 ліворуч, V2 праворуч, R1 верх-ліво, R2 верх-право, R3 середина
    s += line(90, 150, 90, 300, INK, 2.4)
    s += _battery(90, 225, "")
    s += text(66, 222, "V₁", 11, RED, "end", "bold")
    s += line(90, 150, 410, 150, COPPER, 2.2)
    s += _resistor(150, 150, 60, 16, "R₁")
    s += _vresistor(250, 180, 270, "R₃")
    s += line(250, 150, 250, 180, COPPER, 2)
    s += line(250, 270, 250, 300, COPPER, 2)
    s += _resistor(320, 150, 60, 16, "R₂")
    s += line(410, 150, 410, 300, INK, 2.4)
    s += _battery(410, 225, "", "start")
    s += text(434, 222, "V₂", 11, RED, "start", "bold")
    s += line(90, 300, 410, 300, COPPER, 2.2)
    s += _circ_arrow(170, 235, 26, INK, -50, 200, 1.8)
    s += text(170, 240, "Iₐ", 11, INK, "middle", "bold", "italic")
    s += _circ_arrow(330, 235, 26, INK, -50, 200, 1.8)
    s += text(330, 240, "I_b", 11, INK, "middle", "bold", "italic")
    s += rect(480, 110, 320, 200, "#f6f8fc", INK, 1.6, 12)
    s += text(640, 138, "Контурні струми Iₐ, I_b:", 12, INK, "middle", "bold")
    s += text(498, 168, "контур A:  V₁ = Iₐ·R₁ + (Iₐ−I_b)·R₃", 11, INK, "start")
    s += text(498, 194, "контур B:  V₂ = I_b·R₂ + (I_b−Iₐ)·R₃", 11, INK, "start")
    s += line(498, 212, 782, 212, FAINT, 1.3)
    s += text(640, 236, "дві рівності — дві невідомі;", 11, GREY, "middle", style="italic")
    s += text(640, 254, "розв'язуєш систему — маєш струми", 11, GREY, "middle", style="italic")
    s += text(640, 284, "(скільки контурів — стільки рівнянь, §4.1)", 10, GREY, "middle", style="italic")
    save("fig-4-8-4-two-source.svg", s)


# ── Рис. 4.8.5 — рецепт і перевірки ──────────────────────────────────────────
def fig48_recipe():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 30, "Рецепт розрахунку й самоперевірки", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "порядок дій для будь-якого кола — і як перевірити себе", 12, GREY, "middle", style="italic")
    steps = [("1", "Спрости", "згорни послідовні (ΣR) і паралельні (Σ1/R) групи"),
             ("2", "Повний струм", "I = V / R_екв від джерела"),
             ("3", "Розгорни назад", "дільниками знайди спади й гілкові струми"),
             ("4", "Не згортається?", "признач струми, напиши KCL+KVL+Ом, розв'яжи систему")]
    yy = 90
    for n, t, d in steps:
        s += circle(110, yy + 16, 16, BLUE, INK, 2)
        s += text(110, yy + 21, n, 14, "#fff", "middle", "bold")
        s += rect(140, yy, 640, 50, "#f6f8fc", INK, 1.4, 10)
        s += text(158, yy + 21, t, 13, INK, "start", "bold")
        s += text(158, yy + 39, d, 11, GREY, "start")
        yy += 64
    s += rect(110, yy + 4, 670, 70, "#eef7f0", GREEN, 1.8, 12)
    s += text(445, yy + 28, "Перевір себе:", 12.5, GREEN, "middle", "bold")
    s += text(445, yy + 48, "• одиниці сходяться?   • KCL у вузлах і KVL у контурах виконуються?   • порядок величин розумний?",
              10.5, INK, "middle")
    save("fig-4-8-5-recipe.svg", s)


# ═══ Тема 4.9 — Міст Вітстона ═══════════════════════════════════════════════
def _rbox(cx, cy, label, color=INK, w=50, h=22):
    out = rect(cx - w / 2, cy - h / 2, w, h, "#ffffff", color, 2, 5)
    out += text(cx, cy + 5, label, 12, color, "middle", "bold")
    return out


def _gnd(x, y, col=INK):
    out = ""
    for i, wd in enumerate([24, 15, 7]):
        out += line(x - wd, y + i * 5, x + wd, y + i * 5, col, 2)
    return out


def fig49_anatomy():
    W, H = 820, 450
    s = header(W, H)
    s += text(W / 2, 32, "Міст Вітстона: діамант із чотирьох опорів = два дільники", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "напруга подається згори донизу, а детектор порівнює середні точки двох дільників",
              10.5, GREY, "middle", style="italic")
    T = (400, 130); A = (250, 255); B = (550, 255); Bo = (400, 380)
    for p, q in [(T, A), (A, Bo), (T, B), (B, Bo)]:
        s += line(p[0], p[1], q[0], q[1], INK, 2.4)
    s += _rbox((T[0] + A[0]) / 2 - 8, (T[1] + A[1]) / 2, "R₁", "#1f47b5")
    s += _rbox((A[0] + Bo[0]) / 2 - 8, (A[1] + Bo[1]) / 2, "R₂", "#1f47b5")
    s += _rbox((T[0] + B[0]) / 2 + 8, (T[1] + B[1]) / 2, "R₃", "#1f8a3b")
    s += _rbox((B[0] + Bo[0]) / 2 + 8, (B[1] + Bo[1]) / 2, "R₄", "#1f8a3b")
    s += line(T[0], T[1], T[0], 74, INK, 2.4)
    s += circle(T[0], 74, 4, RED, RED, 1)
    s += text(T[0] + 12, 70, "+V", 13, RED, "start", "bold")
    s += line(Bo[0], Bo[1], Bo[0], 414, INK, 2.4)
    s += _gnd(Bo[0], 414)
    s += circle(A[0], A[1], 4, INK, INK, 1)
    s += text(A[0] - 16, A[1] + 5, "A", 13, "#a000a0", "middle", "bold")
    s += circle(B[0], B[1], 4, INK, INK, 1)
    s += text(B[0] + 16, B[1] + 5, "B", 13, "#a000a0", "middle", "bold")
    s += line(A[0] + 10, A[1], 372, A[1], INK, 2)
    s += line(428, B[1], B[0] - 10, B[1], INK, 2)
    s += circle(400, A[1], 26, "#fff", INK, 2.2)
    s += text(400, A[1] + 6, "G", 16, INK, "middle", "bold")
    s += text(400, A[1] + 46, "детектор (нуль-індикатор)", 10, GREY, "middle", style="italic")
    s += text(170, 300, "V_A = V·R₂/(R₁+R₂)", 10, "#1f47b5", "middle", "bold")
    s += text(630, 300, "V_B = V·R₄/(R₃+R₄)", 10, "#1f8a3b", "middle", "bold")
    s += text(168, 185, "лівий дільник", 10.5, "#1f47b5", "middle", "bold")
    s += text(632, 185, "правий дільник", 10.5, "#1f8a3b", "middle", "bold")
    save("fig-4-9-1-bridge-anatomy.svg", s)


def fig49_balance():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 32, "Умова балансу: коли детектор показує нуль", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "детектор мовчить, щойно зрівняються частки двох дільників — а не самі опори",
              10.5, GREY, "middle", style="italic")
    # дві вертикальні гілки
    xL, xR = 250, 610
    yT, yA, yB_, yG = 110, 235, 235, 235
    for xx, r1, r2, col in [(xL, "R₁", "R₂", "#1f47b5"), (xR, "R₃", "R₄", "#1f8a3b")]:
        s += line(xx, 90, xx, 360, INK, 2.2)
        s += _rbox(xx, 160, r1, col)
        s += _rbox(xx, 300, r2, col)
        s += circle(xx, yA, 4, INK, INK, 1)
    s += text(xL, 80, "+V", 12, RED, "middle", "bold")
    s += text(xR, 80, "+V", 12, RED, "middle", "bold")
    s += _gnd(xL, 366); s += _gnd(xR, 366)
    s += text(xL - 18, yA + 5, "A", 13, "#a000a0", "end", "bold")
    s += text(xR + 18, yA + 5, "B", 13, "#a000a0", "start", "bold")
    # детектор
    s += line(xL + 8, yA, 405, yA, INK, 2)
    s += line(455, yA, xR - 8, yA, INK, 2)
    s += circle(430, yA, 24, "#fff", INK, 2.2)
    s += text(430, yA + 6, "G", 15, INK, "middle", "bold")
    s += text(xL - 30, 235 + 70, "V_A = V·R₂/(R₁+R₂)", 9.5, "#1f47b5", "middle", "bold")
    s += text(xR + 30, 235 + 70, "V_B = V·R₄/(R₃+R₄)", 9.5, "#1f8a3b", "middle", "bold")
    s += rect(150, H - 58, W - 300, 42, "#eef7f0", GREEN, 1.8, 10)
    s += text(W / 2, H - 38, "Баланс (G = 0):  V_A = V_B  ⟺  R₁/R₂ = R₃/R₄  ⟺  R₁·R₄ = R₂·R₃", 13, INK, "middle", "bold")
    s += text(W / 2, H - 21, "V випадає з умови — баланс залежить лише від ВІДНОШЕНЬ плечей.", 10, GREY, "middle", style="italic")
    save("fig-4-9-2-balance.svg", s)


def fig49_null():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 32, "Нуль-метод: ловимо рівновагу, а не показ приладу", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "крути відоме плече, доки стрілка не стане рівно на 0 — тоді важать лише відношення опорів",
              10.5, GREY, "middle", style="italic")
    T = (330, 120); A = (200, 235); B = (460, 235); Bo = (330, 350)
    for p, q in [(T, A), (A, Bo), (T, B), (B, Bo)]:
        s += line(p[0], p[1], q[0], q[1], INK, 2.4)
    s += _rbox((T[0] + A[0]) / 2 - 8, (T[1] + A[1]) / 2, "R₁", "#1f47b5")
    s += _rbox((A[0] + Bo[0]) / 2 - 8, (A[1] + Bo[1]) / 2, "R₂", "#1f47b5")
    s += _rbox((T[0] + B[0]) / 2 + 8, (T[1] + B[1]) / 2, "R₃", "#1f8a3b")
    # регульоване плече R4
    s += _rbox((B[0] + Bo[0]) / 2 + 8, (B[1] + Bo[1]) / 2, "R₄", "#c0271e")
    s += arrow((B[0] + Bo[0]) / 2 - 14, (B[1] + Bo[1]) / 2 + 22, (B[0] + Bo[0]) / 2 + 26, (B[1] + Bo[1]) / 2 - 14, "#c0271e", 2)
    s += text((B[0] + Bo[0]) / 2 + 40, (B[1] + Bo[1]) / 2 + 6, "крутимо", 9.5, "#c0271e", "start", "bold")
    s += line(T[0], T[1], T[0], 84, INK, 2.2); s += text(T[0] + 12, 80, "+V", 12, RED, "start", "bold")
    s += line(Bo[0], Bo[1], Bo[0], 380, INK, 2.2); s += _gnd(Bo[0], 380)
    # детектор зі стрілкою на 0
    s += line(A[0] + 10, A[1], 302, A[1], INK, 2)
    s += line(358, A[1], B[0] - 10, A[1], INK, 2)
    s += circle(330, A[1], 28, "#fff", INK, 2.2)
    s += line(330, A[1], 330, A[1] - 20, "#c0271e", 2.4)  # стрілка вгору = 0
    s += text(330, A[1] + 16, "0", 11, INK, "middle", "bold")
    s += text(312, A[1] - 24, "−", 10, GREY, "start"); s += text(344, A[1] - 24, "+", 10, GREY, "start")
    # пояснення
    s += rect(560, 110, 260, 220, "#f7f7f7", GREY, 1.5, 10)
    s += text(690, 134, "У точці нуля:", 12, INK, "middle", "bold")
    s += text(580, 162, "• джерело V не важить", 10.5, INK, "start")
    s += text(580, 186, "• точність приладу не важить", 10.5, INK, "start")
    s += text(580, 210, "  (треба лише впіймати 0)", 9.5, GREY, "start")
    s += text(580, 238, "• важать ЛИШЕ відношення", 10.5, INK, "start")
    s += text(580, 262, "  опорів — а їх роблять", 9.5, GREY, "start")
    s += text(580, 278, "  дуже точними", 9.5, GREY, "start")
    s += text(690, 312, "Звідси й висока точність", 10, GREEN, "middle", "bold")
    save("fig-4-9-3-null-method.svg", s)


def fig49_measure():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 32, "Вимірювання невідомого опору: X = R · (P/Q)", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "два «плеча відношення» P і Q, один зразковий R — і невідоме X читається з балансу",
              10.5, GREY, "middle", style="italic")
    T = (300, 120); A = (180, 230); B = (420, 230); Bo = (300, 340)
    for p, q in [(T, A), (A, Bo), (T, B), (B, Bo)]:
        s += line(p[0], p[1], q[0], q[1], INK, 2.4)
    s += _rbox((T[0] + A[0]) / 2 - 8, (T[1] + A[1]) / 2, "X (?)", "#c0271e")
    s += _rbox((A[0] + Bo[0]) / 2 - 8, (A[1] + Bo[1]) / 2, "R", "#1f47b5")
    s += _rbox((T[0] + B[0]) / 2 + 8, (T[1] + B[1]) / 2, "P", "#1f8a3b")
    s += _rbox((B[0] + Bo[0]) / 2 + 8, (B[1] + Bo[1]) / 2, "Q", "#1f8a3b")
    s += line(T[0], T[1], T[0], 86, INK, 2.2); s += text(T[0] + 12, 82, "+V", 12, RED, "start", "bold")
    s += line(Bo[0], Bo[1], Bo[0], 366, INK, 2.2); s += _gnd(Bo[0], 366)
    s += line(A[0] + 10, 230, 274, 230, INK, 2); s += line(326, 230, B[0] - 10, 230, INK, 2)
    s += circle(300, 230, 24, "#fff", INK, 2.2); s += text(300, 236, "G", 15, INK, "middle", "bold")
    # панель формул
    s += rect(520, 100, 300, 230, "#f7f7f7", GREY, 1.5, 10)
    s += text(670, 126, "У балансі X/R = P/Q:", 12.5, INK, "middle", "bold")
    s += text(540, 158, "X = R · (P/Q)", 15, "#c0271e", "start", "bold")
    s += line(540, 176, 800, 176, FAINT, 1.4)
    s += text(540, 200, "Приклад (P:Q = 1:1):", 11, INK, "start", "bold")
    s += text(556, 222, "крутимо R до балансу → R = 470 Ω", 10, GREY, "start")
    s += text(556, 240, "X = 470 · 1 = 470 Ω", 11.5, "#1f8a3b", "start", "bold")
    s += text(540, 270, "Зміни P:Q на 10:1 —", 11, INK, "start", "bold")
    s += text(556, 290, "той самий R міряє вдесятеро", 10, GREY, "start")
    s += text(556, 306, "більший діапазон (X = 10·R).", 10, GREY, "start")
    save("fig-4-9-4-measure-unknown.svg", s)


def fig49_sensor():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 32, "Міст як підсилювач різниці: крихітна ΔR → читабельний сигнал", 17.5, INK, "middle", "bold")
    s += text(W / 2, 53, "одне плече — датчик; у спокої міст збалансований, а зміна ΔR збиває баланс і дає вихід",
              10.5, GREY, "middle", style="italic")
    # ліворуч: міст із датчиком
    T = (240, 120); A = (140, 225); B = (340, 225); Bo = (240, 330)
    for p, q in [(T, A), (A, Bo), (T, B), (B, Bo)]:
        s += line(p[0], p[1], q[0], q[1], INK, 2.2)
    s += _rbox((T[0] + A[0]) / 2 - 7, (T[1] + A[1]) / 2, "R", "#8a8a8a", 42, 20)
    s += _rbox((A[0] + Bo[0]) / 2 - 7, (A[1] + Bo[1]) / 2, "R", "#8a8a8a", 42, 20)
    s += _rbox((T[0] + B[0]) / 2 + 7, (T[1] + B[1]) / 2, "R", "#8a8a8a", 42, 20)
    s += _rbox((B[0] + Bo[0]) / 2 + 7, (B[1] + Bo[1]) / 2, "R+ΔR", "#c0271e", 56, 20)
    s += text((B[0] + Bo[0]) / 2 + 64, (B[1] + Bo[1]) / 2 + 4, "датчик", 9.5, "#c0271e", "start", "bold")
    s += line(T[0], T[1], T[0], 88, INK, 2); s += text(T[0] + 10, 84, "+V", 11, RED, "start", "bold")
    s += line(Bo[0], Bo[1], Bo[0], 356, INK, 2); s += _gnd(Bo[0], 356)
    s += line(A[0] + 9, 225, 214, 225, INK, 1.8); s += line(266, 225, B[0] - 9, 225, INK, 1.8)
    s += circle(240, 225, 23, "#fff", INK, 2); s += text(240, 231, "V_out", 10.5, INK, "middle", "bold")
    s += text(240, 372, "V_out ≈ (V/4)·(ΔR/R)", 11.5, "#c0271e", "middle", "bold")
    # праворуч: чому не простий дільник
    s += line(470, 86, 470, H - 24, FAINT, 1.5)
    s += text(665, 96, "Чому міст, а не простий дільник?", 12, INK, "middle", "bold")
    # plain divider bar: big baseline + tiny wiggle
    s += text(560, 130, "простий дільник:", 10.5, "#8a8a8a", "middle", "bold")
    s += rect(510, 142, 100, 90, "#eef2fb", "#1f47b5", 1.6, 4)
    s += text(560, 192, "≈ V/2", 12, "#1f47b5", "middle", "bold")
    s += rect(510, 138, 100, 6, "#c0271e", "none", 0)
    s += text(560, 250, "величезна стала +", 9.5, GREY, "middle")
    s += text(560, 264, "крихітна змінка згори", 9.5, GREY, "middle")
    s += text(560, 282, "→ важко вирізнити", 9.5, "#c0271e", "middle", "bold")
    # bridge: zero baseline
    s += text(775, 130, "міст:", 10.5, GREEN, "middle", "bold")
    s += line(720, 232, 830, 232, "#bbbbbb", 1.4, "4 3")
    s += text(840, 232, "0", 10, GREY, "start", "bold")
    s += rect(745, 200, 60, 32, "#c0271e", "none", 0, 2)
    s += text(775, 256, "база віднята —", 9.5, GREY, "middle")
    s += text(775, 270, "лишилась сама ΔR", 9.5, GREEN, "middle", "bold")
    s += text(775, 288, "→ підсилюй та читай", 9.5, GREEN, "middle", "bold")
    save("fig-4-9-5-sensor-bridge.svg", s)


def fig49_apps():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 32, "Де живе міст: датчики, що міряють опором", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "усе, що змінює опір від впливу, вмикають у плече мосту — і дістають напругу-сигнал",
              10.5, GREY, "middle", style="italic")
    # тензодатчик / ваги
    s += rect(60, 110, 220, 120, "#fafafa", GREY, 1.5, 10)
    s += text(170, 134, "Тензодатчик (ваги)", 12, INK, "middle", "bold")
    s += rect(95, 165, 150, 14, "#cdd5da", INK, 1.6, 3)
    s += polyline([(120, 165), (135, 159), (150, 171), (165, 159), (180, 171), (195, 165)], "#c0271e", 1.6)
    s += arrow(170, 150, 170, 163, INK, 2)
    s += text(170, 205, "вага → деформація → ΔR", 9.5, GREY, "middle")
    s += text(170, 221, "→ напруга (load cell)", 9.5, "#1f8a3b", "middle", "bold")
    # температура
    s += rect(320, 110, 220, 120, "#fafafa", GREY, 1.5, 10)
    s += text(430, 134, "Температура", 12, INK, "middle", "bold")
    s += circle(430, 178, 22, "#fff3e8", ORANGE, 2)
    s += text(430, 184, "RTD", 11, ORANGE, "middle", "bold")
    s += text(430, 205, "тепло → ΔR (RTD/термістор,", 9.5, GREY, "middle")
    s += text(430, 221, "§1.3.4) → напруга", 9.5, "#1f8a3b", "middle", "bold")
    # тиск
    s += rect(580, 110, 220, 120, "#fafafa", GREY, 1.5, 10)
    s += text(690, 134, "Тиск", 12, INK, "middle", "bold")
    s += polyline([(645, 185), (665, 178), (690, 174), (715, 178), (735, 185)], "#1f47b5", 2)
    s += line(645, 195, 735, 195, INK, 1.6)
    s += text(690, 205, "прогин мембрани → ΔR", 9.5, GREY, "middle")
    s += text(690, 221, "→ напруга", 9.5, "#1f8a3b", "middle", "bold")
    s += rect(90, 262, W - 180, 70, "#eef7f0", GREEN, 1.8, 12)
    s += text(W / 2, 286, "Чверть-, напів- і повний міст: 1, 2 чи 4 активні плеча.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 308, "Більше активних плечей → більший сигнал; протилежні пари ще й гасять вплив температури.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 324, "Тому міст — стандартний «передній край» майже кожного резистивного датчика.", 10, INK, "middle", "bold")
    save("fig-4-9-6-applications.svg", s)


# ═══ 🔌 Вставка до 4.1 — макетна плата зсередини ════════════════════════════
def _bb_holes(xs, y, r=4):
    out = ""
    for x in xs:
        out += circle(x, y, r, "#ffffff", "#9aa0a6", 1.3)
    return out


def fig_breadboard_internals():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Макетна плата зсередини: які гнізда вже з'єднані", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "приховані металеві смужки заздалегідь з'єднують певні гнізда — їх треба знати напам'ять",
              10.5, GREY, "middle", style="italic")
    cols = [230, 320, 410, 500, 590, 680]
    railxs = list(range(210, 701, 30))
    # верхні шини
    s += line(200, 84, 710, 84, "#c0271e", 2)
    s += line(200, 104, 710, 104, "#1f47b5", 2)
    s += _bb_holes(railxs, 84); s += _bb_holes(railxs, 104)
    s += text(192, 88, "+", 14, "#c0271e", "end", "bold")
    s += text(192, 108, "−", 14, "#1f47b5", "end", "bold")
    s += text(724, 84, "шина + (вся довжина)", 9.5, "#c0271e", "start", "bold")
    s += text(724, 104, "шина − (вся довжина)", 9.5, "#1f47b5", "start", "bold")
    # верхній блок a-e
    for y, lab in zip([150, 170, 190, 210, 230], ["a", "b", "c", "d", "e"]):
        s += _bb_holes(cols, y)
        s += text(cols[0] - 34, y + 4, lab, 10, GREY, "middle")
        s += text(cols[-1] + 34, y + 4, lab, 10, GREY, "middle")
    hx = cols[1]
    s += rect(hx - 16, 142, 32, 96, "none", "#1f8a3b", 2.2, 8)
    s += line(hx, 150, hx, 230, "#1f8a3b", 2.4)
    s += text(hx, 130, "1 вузол", 9.5, "#1f8a3b", "middle", "bold")
    s += text(cols[3], 130, "сусідній — інший вузол", 9, GREY, "middle")
    # канавка
    s += line(200, 250, 710, 250, FAINT, 1.4, "6 4")
    s += line(200, 272, 710, 272, FAINT, 1.4, "6 4")
    s += text(W / 2, 266, "◄ центральна канавка: верх і низ НЕ з'єднані ►", 10, "#a06a00", "middle", "bold")
    # нижній блок f-j
    for y, lab in zip([292, 312, 332, 352, 372], ["f", "g", "h", "i", "j"]):
        s += _bb_holes(cols, y)
        s += text(cols[0] - 34, y + 4, lab, 10, GREY, "middle")
        s += text(cols[-1] + 34, y + 4, lab, 10, GREY, "middle")
    # нижні шини
    s += line(200, 398, 710, 398, "#c0271e", 2)
    s += line(200, 418, 710, 418, "#1f47b5", 2)
    s += _bb_holes(railxs, 398); s += _bb_holes(railxs, 418)
    s += text(192, 402, "+", 14, "#c0271e", "end", "bold")
    s += text(192, 422, "−", 14, "#1f47b5", "end", "bold")
    s += rect(120, H - 40, W - 240, 30, "#f4f7f4", GREEN, 1.4, 10)
    s += text(W / 2, H - 20, "Стовпчик із 5 гнізд = один вузол · сусідні стовпці незалежні · шини тягнуться вздовж · канавка розділяє верх і низ.",
              9.5, INK, "middle", "bold")
    save("fig-4-1c-1-breadboard-internals.svg", s)


def fig_breadboard_chip():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Мікросхема сідає верхи на канавку — і split-шина-пастка", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "канавка для того й є: ліві ніжки окремо від правих, кожна — у свій стовпець-вузол",
              10.5, GREY, "middle", style="italic")
    # ── ЛІВОРУЧ: чип на канавці ──
    cols = [210, 270, 330, 390]
    for y in [120, 140, 160, 180]:
        s += _bb_holes(cols, y)
    for y in [250, 270, 290, 310]:
        s += _bb_holes(cols, y)
    s += rect(cols[0] - 20, 192, (cols[-1] - cols[0]) + 40, 46, "#2a2a2a", "#101010", 2, 5)
    s += circle((cols[0] + cols[-1]) / 2, 196, 5, "#2a2a2a", "#666", 1.2)
    s += text((cols[0] + cols[-1]) / 2, 220, "DIP-чип", 11, "#f0f0f0", "middle", "bold")
    for x in cols:
        s += line(x, 192, x, 182, "#9a9a9a", 2)
        s += line(x, 238, x, 248, "#9a9a9a", 2)
    s += text(cols[0] - 28, 215, "канавка", 9, "#a06a00", "end", "bold")
    s += text(300, 120 - 18, "кожна ніжка → свій стовпець → свій вузол", 9.5, "#1f8a3b", "middle", "bold")
    s += text(300, 345, "ліва половина ніжок ≠ права (їх ділить канавка)", 9.5, GREY, "middle", style="italic")
    # ── ПРАВОРУЧ: split-rail пастка ──
    s += line(470, 80, 470, H - 24, FAINT, 1.5)
    s += text(670, 96, "Пастка: розрив шини посередині", 12, "#c0271e", "middle", "bold")
    s += line(520, 150, 600, 150, "#c0271e", 3)
    s += line(620, 150, 820, 150, "#c0271e", 3)
    s += text(610, 138, "✂", 13, "#c0271e", "middle", "bold")
    s += _bb_holes(list(range(530, 821, 30)), 150)
    s += text(670, 178, "на багатьох платах шина живлення", 9.5, INK, "middle")
    s += text(670, 194, "РОЗІРВАНА посередині —", 9.5, "#c0271e", "middle", "bold")
    s += text(670, 210, "половина плати лишається без живлення!", 9.5, INK, "middle")
    s += rect(520, 236, 300, 70, "#eef7f0", GREEN, 1.6, 10)
    s += text(670, 260, "Рятунок: перемичкою з'єднати", 10.5, INK, "middle", "bold")
    s += text(670, 278, "обидві половини шини —", 10.5, INK, "middle", "bold")
    s += text(670, 294, "або спершу продзвонити мультиметром.", 9.5, GREY, "middle", style="italic")
    save("fig-4-1c-2-chip-and-rails.svg", s)


# ═══ 📜 Історія до 4.9 — Крісті й Вітстон ═══════════════════════════════════
def fig_cw_timeline():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 30, "Міст, названий не за винахідником", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "діамант Крісті (1833) став «мостом Вітстона» — і в цьому винна радше історія, ніж люди",
              10.5, GREY, "middle", style="italic")
    y = 150
    s += line(70, y, 830, y, "#bbbbbb", 2.5)
    for x, yr, l1, l2, col in [
        (150, "1833", "Крісті: «діамантовий»", "метод (у статті про магнетизм)", "#1f47b5"),
        (420, "1843", "Вітстон: розвинув для", "вимірювання опору; вказав Крісті", "#1f8a3b"),
        (740, "далі", "назва прилипла до Вітстона;", "переклади викинули Крісті", "#c0271e"),
    ]:
        s += circle(x, y, 7, col, col, 2)
        s += line(x, y - 7, x, y - 34, "#cccccc", 1.4)
        s += text(x, y - 40, yr, 13, col, "middle", "bold")
        s += text(x, y + 28, l1, 9.5, INK, "middle", "bold")
        s += text(x, y + 42, l2, 9, GREY, "middle")
    save("fig-4-9i-1-cw-timeline.svg", s)


def fig_cw_two_men():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Дві заслуги різного роду", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "«мати й опублікувати ідею» — одне, «зробити корисним і знаменитим» — інше; обидва справжні",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 30, FAINT, 1.5)
    s += circle(225, 140, 40, "#eef2fb", "#1f47b5", 2.5); s += text(225, 147, "SHC", 14, "#1f47b5", "middle", "bold")
    s += text(225, 198, "Семюел Гантер Крісті", 12, INK, "middle", "bold")
    s += text(225, 216, "(1784–1865)", 9.5, GREY, "middle")
    s += text(225, 244, "ВИНАЙШОВ діамантовий метод", 10, "#1f47b5", "middle", "bold")
    s += text(225, 262, "(1833) — та сховав його в", 9.5, INK, "middle")
    s += text(225, 276, "статті про магнетизм, тож", 9.5, INK, "middle")
    s += text(225, 290, "метод лишився непоміченим.", 9.5, INK, "middle")
    s += text(225, 320, "«мав і опублікував ідею»", 9.5, GREY, "middle", style="italic")
    s += circle(635, 140, 40, "#eef7f0", "#1f8a3b", 2.5); s += text(635, 147, "CW", 14, "#1f8a3b", "middle", "bold")
    s += text(635, 198, "Чарльз Вітстон", 12, INK, "middle", "bold")
    s += text(635, 216, "(1802–1875)", 9.5, GREY, "middle")
    s += text(635, 244, "РОЗВИНУВ його (1843) для", 10, "#1f8a3b", "middle", "bold")
    s += text(635, 262, "точного вимірювання опору", 9.5, INK, "middle")
    s += text(635, 276, "й чесно вказав на Крісті —", 9.5, INK, "middle")
    s += text(635, 290, "та назва прилипла до нього.", 9.5, INK, "middle")
    s += text(635, 320, "«зробив корисним і відомим»", 9.5, GREY, "middle", style="italic")
    save("fig-4-9i-2-two-men.svg", s)


# ═══ 🧮 Вставка до 4.9 — чутливість мосту ═══════════════════════════════════
def fig_bridge_linearization():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Чутливість мосту: лінеаризація біля балансу", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "чверть-міст: точний вихід трохи гнеться, та біля балансу він майже прямий — (V/4)(ΔR/R)",
              10.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 110, 330, 640, 90

    def px(x):
        return ox + (x / 0.3) * (axr - 30 - ox)

    def py(y):
        return oy - (y / 0.08) * (oy - ayt)

    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "ΔR/R", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8); s += text(ox - 8, ayt - 10, "V_вих/V", 10, INK, "start", "bold")
    s += line(px(0), py(0), px(0.3), py(0.075), "#1f47b5", 2.4, "5 4")
    s += text(px(0.3), py(0.075) - 6, "лінійно: (V/4)·(ΔR/R)", 10, "#1f47b5", "end", "bold")
    pts = [(px(i / 100.0 * 0.3), py((i / 100.0 * 0.3) / (2 * (2 + i / 100.0 * 0.3)))) for i in range(101)]
    s += polyline(pts, "#c0271e", 2.6)
    s += text(px(0.3) + 4, py(0.0652) + 6, "точно", 10, "#c0271e", "start", "bold")
    for xv in [0.1, 0.2, 0.3]:
        s += line(px(xv), oy - 4, px(xv), oy + 4, INK, 1.2)
        s += text(px(xv), oy + 20, "%d%%" % int(xv * 100), 9, GREY, "middle")
    s += rect(668, 108, 184, 204, "#f7f7f7", GREY, 1.4, 10)
    s += text(760, 132, "Біля нуля", 11, INK, "middle", "bold")
    s += text(686, 156, "точне ≈ лінійне:", 9.5, INK, "start")
    s += text(686, 176, "|V_вих| ≈ (V/4)·(ΔR/R)", 10, "#1f8a3b", "start", "bold")
    s += text(686, 204, "Нелінійність ~ (ΔR/R)/2:", 9.5, INK, "start")
    s += text(700, 226, "0.1 % → 0.05 % похибки", 9.5, INK, "start", "bold")
    s += text(700, 244, "2 %   → 1 %", 9.5, INK, "start", "bold")
    s += text(686, 274, "Тому датчик тримають", 9, GREY, "start")
    s += text(686, 288, "біля балансу.", 9, GREY, "start")
    save("fig-4-9m-1-bridge-linearization.svg", s)


def fig_bridge_configs():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чверть-, напів- і повний міст: чутливість і лінійність", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "більше активних плечей — більший сигнал; протилежні пари ще й роблять вихід точно лінійним",
              10.5, GREY, "middle", style="italic")
    y = 108
    for name, arms, formula, note, mult, col in [
        ("Чверть-міст", "1 активне плече", "V_вих = (V/4)·(ΔR/R)", "нелінійність ~(ΔR/R)/2", 1, "#1f47b5"),
        ("Напівміст", "2 плеча (протилежні)", "V_вих = (V/2)·(ΔR/R)", "×2; нелінійність гаситься", 2, "#e08030"),
        ("Повний міст", "4 активні плеча", "V_вих = V·(ΔR/R)", "×4; ТОЧНО лінійний", 4, "#1f8a3b"),
    ]:
        s += rect(60, y, 760, 72, "#fafafa", "#cccccc", 1.4, 8)
        s += text(80, y + 30, name, 13, col, "start", "bold")
        s += text(80, y + 52, arms, 9.5, GREY, "start")
        s += text(296, y + 30, formula, 12, INK, "start", "bold")
        s += text(296, y + 52, note, 9.5, GREY, "start")
        s += rect(600, y + 24, mult * 48, 24, col, col, 0, 4)
        s += text(600 + mult * 48 + 10, y + 41, "×%d" % mult, 11, col, "start", "bold")
        y += 86
    save("fig-4-9m-2-bridge-configs.svg", s)


# ═══ 📜 Історія до 4.8 — контурні струми Максвелла ══════════════════════════
def fig_branch_vs_mesh():
    W, H = 880, 412
    s = header(W, H)
    s += text(W / 2, 30, "Чому контурні струми Максвелла: менше рівнянь", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "те саме коло двома методами — гілкові струми проти контурних",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 58, FAINT, 1.5)

    def circuit(ox):
        L, R, T, B = ox + 40, ox + 330, 120, 296
        out = rect(L, T, R - L, B - T, "none", INK, 2, 0)
        out += line((L + R) / 2, T, (L + R) / 2, B, INK, 2)
        out += text(L - 4, 196, "V₁", 10, "#c0271e", "end", "bold")
        out += text(R + 4, 196, "V₂", 10, "#c0271e", "start", "bold")
        return out, L, R, T, B, (L + R) / 2

    def loopcur(cx, cy, lab):
        out = circle(cx, cy, 22, "none", "#1f8a3b", 2)
        out += polyline([(cx - 5, cy - 26), (cx + 4, cy - 22), (cx - 5, cy - 18)], "#1f8a3b", 2)
        out += text(cx, cy + 5, lab, 12, "#1f8a3b", "middle", "bold")
        return out

    s += text(225, 96, "Гілкові струми", 12, "#1f47b5", "middle", "bold")
    c, L, R, T, B, mx = circuit(50)
    s += c
    s += text((L + mx) / 2, T - 8, "i₁", 11, "#1f47b5", "middle", "bold")
    s += text(mx + 12, (T + B) / 2, "i₃", 11, "#1f47b5", "middle", "bold")
    s += text((mx + R) / 2, T - 8, "i₂", 11, "#1f47b5", "middle", "bold")
    s += rect(95, 316, 300, 58, "#eef2fb", "#1f47b5", 1.5, 8)
    s += text(245, 339, "3 гілкові струми (i₁, i₂, i₃):", 10, INK, "middle", "bold")
    s += text(245, 358, "1 рівняння KCL + 2 KVL = 3 рівняння", 10, INK, "middle", "bold")
    s += text(655, 96, "Контурні струми (Максвелл)", 12, "#1f8a3b", "middle", "bold")
    c2, L2, R2, T2, B2, mx2 = circuit(480)
    s += c2
    s += loopcur((L2 + mx2) / 2, (T2 + B2) / 2, "Iₐ")
    s += loopcur((mx2 + R2) / 2, (T2 + B2) / 2, "I_b")
    s += rect(525, 316, 300, 58, "#eef7f0", "#1f8a3b", 1.5, 8)
    s += text(675, 339, "2 контурні струми (Iₐ, I_b):", 10, INK, "middle", "bold")
    s += text(675, 358, "KCL — сам собою; лише 2 KVL = 2 рівняння", 10, INK, "middle", "bold")
    s += text(W / 2, H - 16, "Менше невідомих → менше рівнянь → швидший розв'язок руками.",
              10.5, "#1f8a3b", "middle", "bold")
    save("fig-4-8i-1-branch-vs-mesh.svg", s)


def fig_cyclic_kcl():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Хитрість Максвелла: контурний струм сам задовольняє KCL", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "замкнений контурний струм входить у кожен вузол і виходить із нього — тож KCL не треба писати",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 30, FAINT, 1.5)
    s += text(225, 100, "Контурний струм крізь вузол", 11, INK, "middle", "bold")
    s += circle(225, 200, 8, INK, INK, 1)
    s += arrow(110, 200, 210, 200, "#1f8a3b", 2.6); s += text(150, 188, "Iₐ входить", 9.5, "#1f8a3b", "middle", "bold")
    s += arrow(240, 200, 340, 200, "#1f8a3b", 2.6); s += text(300, 188, "Iₐ виходить", 9.5, "#1f8a3b", "middle", "bold")
    s += text(225, 234, "те саме Iₐ → втікає = витікає", 10, INK, "middle", "bold")
    s += text(225, 256, "→ KCL виконано АВТОМАТИЧНО", 10.5, "#1f8a3b", "middle", "bold")
    s += text(225, 290, "тому пишемо лише KVL по контурах", 9.5, GREY, "middle", style="italic")
    s += text(655, 100, "Скільки рівнянь? Бери менше", 11, INK, "middle", "bold")
    s += rect(520, 124, 320, 214, "#f7f7f7", GREY, 1.5, 10)
    s += text(540, 150, "• контурний метод: L = B−N+1 рівнянь", 10, "#1f8a3b", "start", "bold")
    s += text(540, 172, "• вузловий метод: N−1 рівнянь", 10, "#1f47b5", "start", "bold")
    s += text(540, 198, "Бери той, де менше — для різних кіл", 10, INK, "start")
    s += text(552, 214, "виграшним буває різний метод.", 10, GREY, "start")
    s += text(540, 244, "Іронія часу: руками часто виграє", 10, INK, "start", "bold")
    s += text(552, 260, "контурний (менше рівнянь), а", 10, GREY, "start")
    s += text(540, 282, "машини беруть вузловий / MNA —", 10, INK, "start", "bold")
    s += text(552, 298, "його легше скласти з netlist (§1.4.8).", 9.5, GREY, "start")
    save("fig-4-8i-2-cyclic-kcl.svg", s)


# ═══ ⚙️ Вставка до 4.8 — MNA / SPICE ════════════════════════════════════════
def fig_mna_stamping():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 30, "Як SPICE будує матрицю: «штампування» елементів", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "кожен елемент незалежно додає свій фіксований внесок у матрицю провідностей G",
              10.5, GREY, "middle", style="italic")
    s += text(200, 96, "Резистор R між вузлами 1 і 2", 11, INK, "middle", "bold")
    s += circle(120, 168, 18, "#eef2fb", "#1f47b5", 2); s += text(120, 173, "1", 12, INK, "middle", "bold")
    s += circle(290, 168, 18, "#eef2fb", "#1f47b5", 2); s += text(290, 173, "2", 12, INK, "middle", "bold")
    s += line(138, 168, 170, 168, INK, 2); s += line(240, 168, 272, 168, INK, 2)
    s += rect(170, 156, 70, 24, "#fff", "#8a8a8a", 2, 4); s += text(205, 173, "R", 11, INK, "middle", "bold")
    s += text(205, 208, "провідність g = 1/R", 10, GREY, "middle")
    s += text(200, 248, "додає у G чотири внески:", 10.5, INK, "middle", "bold")
    s += text(200, 272, "(1,1) += g    (2,2) += g", 11, "#1f8a3b", "middle", "bold")
    s += text(200, 292, "(1,2) −= g    (2,1) −= g", 11, "#c0271e", "middle", "bold")
    s += line(W / 2, 80, W / 2, H - 28, FAINT, 1.5)
    s += text(675, 96, "Матриця провідностей G", 11, INK, "middle", "bold")
    gx, gy, cw = 615, 132, 72
    for j, l in enumerate(["1", "2"]):
        s += text(gx + cw * j + cw / 2, gy - 8, l, 11, GREY, "middle", "bold")
    for i, l in enumerate(["1", "2"]):
        s += text(gx - 16, gy + cw * i + cw / 2 + 5, l, 11, GREY, "middle", "bold")
    cells = {(0, 0): "+g", (1, 1): "+g", (0, 1): "−g", (1, 0): "−g"}
    for i in range(2):
        for j in range(2):
            col = "#1f8a3b" if i == j else "#c0271e"
            s += rect(gx + cw * j, gy + cw * i, cw, cw, "#fafafa", "#cccccc", 1.2, 0)
            s += text(gx + cw * j + cw / 2, gy + cw * i + cw / 2 + 6, cells[(i, j)], 15, col, "middle", "bold")
    s += text(675, gy + 2 * cw + 30, "Кожен резистор «штампує» цей хрест;", 9.5, INK, "middle", "bold")
    s += text(675, gy + 2 * cw + 46, "уся матриця збирається з netlist сама.", 9.5, GREY, "middle", style="italic")
    save("fig-4-8a-1-mna-stamping.svg", s)


def fig_mna_augment():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 30, "MNA: джерело напруги додає зайвий рядок і стовпець", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "ідеальне джерело задає V, але його струм невідомий — тож його роблять зайвою змінною",
              10.5, GREY, "middle", style="italic")
    gx, gy, cw = 120, 122, 78
    rows = [["g₁", "−g₁", "1"], ["−g₁", "g₁+g₂", "0"], ["1", "0", "0"]]
    for i in range(3):
        for j in range(3):
            border = (i == 2 or j == 2)
            s += rect(gx + cw * j, gy + cw * i, cw, cw, "#eef2fb" if border else "#fafafa", "#cccccc", 1.2, 0)
            s += text(gx + cw * j + cw / 2, gy + cw * i + cw / 2 + 5, rows[i][j], 12, INK, "middle", "bold")
    s += line(gx + cw * 2, gy - 4, gx + cw * 2, gy + cw * 3 + 4, "#1f47b5", 2)
    s += line(gx - 4, gy + cw * 2, gx + cw * 3 + 4, gy + cw * 2, "#1f47b5", 2)
    s += text(gx + cw, gy - 24, "вузлові рівняння (KCL)", 9.5, GREY, "middle")
    s += text(gx + cw * 2 + cw / 2, gy - 24, "джерело", 9, "#1f47b5", "middle", "bold")
    vx = gx + cw * 3 + 34
    for i, lab, col in [(0, "V₁", INK), (1, "V₂", INK), (2, "I_V", "#1f47b5")]:
        s += text(vx, gy + cw * i + cw / 2 + 5, lab, 13, col, "middle", "bold")
    s += text(vx + 34, gy + cw * 1 + cw / 2 + 5, "=", 16, INK, "middle", "bold")
    for i, lab, col in [(0, "0", INK), (1, "0", INK), (2, "Vs", "#1f47b5")]:
        s += text(vx + 70, gy + cw * i + cw / 2 + 5, lab, 13, col, "middle", "bold")
    s += rect(560, 150, 300, 176, "#eef7f0", GREEN, 1.5, 10)
    s += text(710, 176, "Збірка → [ G  B ; C  D ]", 11, INK, "middle", "bold")
    s += text(580, 202, "• G — вузлові провідності;", 10, INK, "start")
    s += text(580, 220, "• рядок/стовпець на кожне", 10, INK, "start")
    s += text(592, 236, "джерело напруги (струм I_V).", 10, GREY, "start")
    s += text(580, 262, "• «висячий» вузол → матриця", 10, "#c0271e", "start", "bold")
    s += text(592, 278, "вироджена; SPICE додає крихітну", 9.5, INK, "start")
    s += text(592, 292, "провідність gmin на землю.", 9.5, GREY, "start")
    s += text(580, 316, "Далі — метод Гаусса (§1.4.8m).", 10, "#1f8a3b", "start", "bold")
    save("fig-4-8a-2-mna-augment.svg", s)


# ═══ 🧮 Вставка до 4.8 — метод Гаусса ═══════════════════════════════════════
def fig_gauss_elimination():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "Метод Гаусса: зводимо систему до трикутної", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "прямий хід виключає змінні стовпець за стовпцем; зворотний — підставляє знизу вгору",
              10.5, GREY, "middle", style="italic")

    def mat(x, y, rows):
        cw, rh = 30, 28
        nc = len(rows[0])
        out = rect(x - 8, y - 8, cw * nc + 28, rh * 3 + 16, "#fff", "#bbbbbb", 1.4, 6)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                out += text(x + cw * j + cw / 2, y + rh * i + rh / 2 + 5, val, 12,
                            INK if j < 3 else "#1f47b5", "middle", "bold")
        out += line(x + cw * 3 + 6, y - 6, x + cw * 3 + 6, y + rh * 3 + 6, "#888", 1.4)
        return out

    s += mat(70, 108, [["1", "1", "1", "6"], ["2", "3", "−1", "5"], ["1", "−1", "2", "5"]])
    s += mat(372, 108, [["1", "1", "1", "6"], ["0", "1", "−3", "−7"], ["0", "−2", "1", "−1"]])
    s += mat(674, 108, [["1", "1", "1", "6"], ["0", "1", "−3", "−7"], ["0", "0", "−5", "−15"]])
    s += arrow(222, 150, 366, 150, INK, 2)
    s += text(294, 138, "R2−2R1", 9, "#c0271e", "middle", "bold")
    s += text(294, 166, "R3−R1", 9, "#c0271e", "middle", "bold")
    s += arrow(524, 150, 668, 150, INK, 2)
    s += text(596, 138, "R3+2R2", 9, "#c0271e", "middle", "bold")
    s += text(772, 210, "трикутна!", 10, "#1f8a3b", "middle", "bold")
    s += rect(120, 256, 660, 126, "#eef7f0", GREEN, 1.6, 10)
    s += text(140, 282, "Зворотний хід (знизу вгору):", 12, INK, "start", "bold")
    s += text(152, 308, "−5z = −15   →   z = 3", 12, "#1f47b5", "start", "bold")
    s += text(152, 332, "y − 3·3 = −7   →   y = 2", 12, "#1f47b5", "start", "bold")
    s += text(152, 356, "x + 2 + 3 = 6   →   x = 1", 12, "#1f47b5", "start", "bold")
    s += text(566, 326, "Розв'язок:", 11, INK, "start", "bold")
    s += text(566, 350, "(x, y, z) = (1, 2, 3)", 13, "#1f8a3b", "start", "bold")
    save("fig-4-8m-1-gauss.svg", s)


def fig_gauss_pivoting():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Підступ півота: нуль чи мале число на діагоналі", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "щоб ділити на діагональний елемент (півот), він має бути не нулем — і краще найбільшим",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 28, FAINT, 1.5)
    s += text(225, 96, "Нуль на діагоналі → переставити рядки", 11, "#c0271e", "middle", "bold")
    s += rect(125, 118, 90, 68, "none", "#bbb", 1.4, 6)
    s += text(150, 142, "0", 13, "#c0271e", "middle", "bold"); s += text(190, 142, "2", 13, INK, "middle", "bold")
    s += text(150, 170, "3", 13, INK, "middle", "bold"); s += text(190, 170, "1", 13, INK, "middle", "bold")
    s += text(170, 205, "на 0 не поділиш!", 9.5, "#c0271e", "middle", "bold")
    s += arrow(232, 152, 292, 152, "#1f8a3b", 2.2)
    s += text(262, 140, "переставити", 8.5, "#1f8a3b", "middle", "bold")
    s += rect(335, 118, 90, 68, "none", "#bbb", 1.4, 6)
    s += text(360, 142, "3", 13, INK, "middle", "bold"); s += text(400, 142, "1", 13, INK, "middle", "bold")
    s += text(360, 170, "0", 13, INK, "middle", "bold"); s += text(400, 170, "2", 13, INK, "middle", "bold")
    s += text(380, 205, "тепер півот = 3", 9.5, "#1f8a3b", "middle", "bold")
    s += text(665, 96, "Ціна й де працює", 11, INK, "middle", "bold")
    s += rect(500, 116, 332, 188, "#f7f7f7", GREY, 1.5, 10)
    s += text(518, 144, "• Мале число теж зле: ділення на", 10, INK, "start")
    s += text(530, 160, "нього роздуває похибки округлення.", 10, GREY, "start")
    s += text(518, 184, "• Тому беруть НАЙБІЛЬШИЙ доступний", 10, INK, "start")
    s += text(530, 200, "півот (часткове впорядкування).", 10, GREY, "start")
    s += text(518, 228, "• Складність O(N³) — головна ціна", 10, INK, "start", "bold")
    s += text(530, 244, "розрахунку великого кола.", 10, GREY, "start")
    s += text(518, 272, "• Саме це робить SPICE, склавши", 10, INK, "start")
    s += text(530, 288, "матрицю кола (§1.4.8).", 10, GREY, "start")
    save("fig-4-8m-2-pivoting.svg", s)


# ═══ ⚙️ Вставка до 4.6 — добір пари E24 ═════════════════════════════════════
def fig_divider_search():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Добір пари E24 під заданий дільник", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "треба V_вих=3.3 В із 5 В: ідеальне R1/R2 ≈ 0.515, та беремо лише значення ряду E24",
              10.5, GREY, "middle", style="italic")
    ox, oy, axr = 100, 175, 800

    def vx(v):
        return ox + (v - 3.0) / (3.6 - 3.0) * (axr - ox)

    s += line(ox, oy, axr, oy, INK, 1.8)
    s += text(axr, oy - 12, "V_вих, В", 10, INK, "end", "italic")
    for v in [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6]:
        s += line(vx(v), oy - 5, vx(v), oy + 5, INK, 1.4)
        s += text(vx(v), oy + 22, "%.1f" % v, 9, GREY, "middle")
    s += line(vx(3.3), oy - 42, vx(3.3), oy, "#1f8a3b", 2, "4 3")
    s += text(vx(3.3), oy - 48, "ціль 3.3 В", 10, "#1f8a3b", "middle", "bold")
    for vo in [3.333, 3.311, 3.235, 3.366, 3.313]:
        col = "#c0271e" if abs(vo - 3.3) < 0.02 else "#1f47b5"
        s += circle(vx(vo), oy - 60, 5, col, col, 1)
    s += circle(vx(3.311), oy - 60, 8, "none", "#c0271e", 2.4)
    s += text(vx(3.311) - 4, oy - 74, "найкраще: 5.1k/10k → 3.31 В", 9.5, "#c0271e", "middle", "bold")
    s += rect(120, 250, 620, 124, "#f7f7f7", GREY, 1.4, 10)
    s += text(140, 274, "Кандидати (R1 / R2 → V_вих, похибка):", 11, INK, "start", "bold")
    y = 298
    for r, vo, e in [("10k / 20k", "3.333 В", "+1.0 %"), ("5.1k / 10k", "3.311 В", "+0.3 %"),
                     ("5.6k / 11k", "3.313 В", "+0.4 %"), ("3.3k / 6.8k", "3.366 В", "+2.0 %")]:
        s += text(150, y, r, 10, INK, "start")
        s += text(330, y, vo, 10, "#1f47b5", "start")
        s += text(470, y, e, 10, GREY, "start")
        y += 20
    s += text(150, y + 2, "→ перебираємо пари ряду й беремо мінімум похибки.", 10, "#1f8a3b", "start", "bold")
    save("fig-4-6a-1-divider-search.svg", s)


def fig_divider_algorithm():
    import math
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Алгоритм: для кожного R2 «прилипни» до найближчого E24", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "замість сліпого перебору N² пар — N разів знайди найближче значення ряду (двійковий пошук)",
              10.5, GREY, "middle", style="italic")
    ox, axr, y = 90, 800, 150
    s += line(ox, y, axr, y, INK, 1.8)
    vals = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47]

    def lx(v):
        return ox + (math.log10(v) - 1) / (math.log10(47) - 1) * (axr - ox)

    for v in vals:
        s += line(lx(v), y - 5, lx(v), y + 5, INK, 1.3)
        s += text(lx(v), y + 20, str(v), 8, GREY, "middle")
    s += line(lx(23.0), y - 44, lx(23.0), y, "#c0271e", 2, "4 3")
    s += text(lx(23.0), y - 50, "R1_ідеал = ціль · R2 = 23.0", 9.5, "#c0271e", "middle", "bold")
    s += circle(lx(22), y, 7, "none", "#1f8a3b", 2.4)
    s += arrow(lx(23.0), y - 20, lx(22), y - 9, "#1f8a3b", 2)
    s += text(lx(22) - 4, y - 28, "найближче: 22", 9.5, "#1f8a3b", "middle", "bold")
    s += rect(120, 238, 620, 124, "#eef7f0", GREEN, 1.6, 10)
    s += text(140, 264, "Пастка МК: без FPU не ділимо — порівнюємо ЦІЛИМИ навхрест:", 10.5, INK, "start", "bold")
    s += text(150, 288, "замість  R1/R2 ?= R1ц/R2ц   →   R1·R2ц ?= R2·R1ц  (без ділення)", 10.5, "#1f47b5", "start", "bold")
    s += text(150, 312, "Увага на переповнення: 1МΩ·1МΩ = 10¹² > 2³² — рахуй у 64 бітах.", 10, INK, "start")
    s += text(150, 336, "Складність O(N log N); таблиця ряду ≈ 300 байт у флеші.", 10, GREY, "start")
    save("fig-4-6a-2-divider-algorithm.svg", s)


# ═══ 🔌 Вставка до 4.6 — потенціометр і тример ══════════════════════════════
def fig_pot_modes():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 30, "Потенціометр: три виводи, два режими", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "доріжка опору з рухомим повзунком — або дільник (3 виводи), або змінний опір (2)",
              10.5, GREY, "middle", style="italic")
    tx0, tx1, ty = 280, 600, 110
    s += rect(tx0, ty - 11, tx1 - tx0, 22, "#efe2c8", "#b8a37a", 2, 4)
    s += circle(tx0, ty, 5, "#1f47b5", "#1f47b5", 1); s += text(tx0, ty + 28, "1", 11, INK, "middle", "bold")
    s += circle(tx1, ty, 5, "#1f47b5", "#1f47b5", 1); s += text(tx1, ty + 28, "3", 11, INK, "middle", "bold")
    wx = tx0 + 0.6 * (tx1 - tx0)
    s += line(wx, ty - 12, wx, ty - 42, "#c0271e", 2.4)
    s += polyline([(wx - 7, ty - 24), (wx, ty - 11), (wx + 7, ty - 24)], "#c0271e", 2)
    s += circle(wx, ty - 46, 5, "#c0271e", "#c0271e", 1)
    s += text(wx, ty - 56, "2 (повзунок)", 10, "#c0271e", "middle", "bold")
    s += text((tx0 + tx1) / 2, ty + 52, "повний опір R між 1 і 3; повзунок 2 ділить його на дві частини",
              9.5, GREY, "middle", style="italic")
    s += line(W / 2, 188, W / 2, H - 18, FAINT, 1.5)
    # ── режим дільника ──
    s += text(228, 206, "Режим ДІЛЬНИКА (потенціометр)", 11, "#1f47b5", "middle", "bold")
    s += text(228, 224, "задіяні всі 3 виводи", 9.5, GREY, "middle")
    cx, cy = 210, 300
    s += rect(cx - 16, cy - 44, 32, 88, "#efe2c8", "#b8a37a", 2, 4)
    s += line(cx, cy - 44, cx, cy - 68, INK, 2); s += text(cx, cy - 74, "+V", 11, RED, "middle", "bold")
    s += line(cx, cy + 44, cx, cy + 64, INK, 2); s += _gnd(cx, cy + 64)
    s += line(cx + 16, cy, cx + 56, cy, "#c0271e", 2.4)
    s += polyline([(cx + 8, cy - 7), (cx + 16, cy), (cx + 8, cy + 7)], "#c0271e", 2)
    s += text(cx + 62, cy + 4, "V_вих", 11, "#c0271e", "start", "bold")
    s += text(228, cy + 86, "кінці → V і GND, повзунок → вихід", 9, GREY, "middle", style="italic")
    # ── режим реостата ──
    s += text(632, 206, "Режим РЕОСТАТА (змінний опір)", 11, "#1f8a3b", "middle", "bold")
    s += text(632, 224, "повзунок + один кінець", 9.5, GREY, "middle")
    cx = 612
    s += rect(cx - 16, cy - 44, 32, 88, "#efe2c8", "#b8a37a", 2, 4)
    s += line(cx, cy + 44, cx, cy + 64, INK, 2); s += text(cx, cy + 80, "вивід A", 9.5, INK, "middle", "bold")
    s += line(cx + 16, cy, cx + 44, cy, "#1f8a3b", 2.4)
    s += polyline([(cx + 8, cy - 7), (cx + 16, cy), (cx + 8, cy + 7)], "#1f8a3b", 2)
    s += line(cx + 44, cy, cx + 44, cy - 56, "#1f8a3b", 2)
    s += line(cx, cy - 44, cx, cy - 56, INK, 2); s += line(cx, cy - 56, cx + 44, cy - 56, INK, 2, "3 3")
    s += text(cx + 24, cy - 66, "вивід B", 9.5, INK, "middle", "bold")
    s += text(632, cy + 86, "повзунок зведено з кінцем → змінний R", 9, GREY, "middle", style="italic")
    save("fig-4-6c-1-pot-modes.svg", s)


def fig_pot_tapers():
    W, H = 860, 390
    s = header(W, H)
    s += text(W / 2, 30, "Характеристика доріжки й форм-фактори", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "як вихід залежить від повороту (лінійна чи логарифмічна) і в яких корпусах буває пот",
              10.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 90, 300, 400, 108
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 20, "поворот", 10, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8); s += text(ox - 6, ayt - 10, "вихід", 10, INK, "start", "bold")
    s += line(ox, oy, axr - 20, ayt, "#1f47b5", 2.6)
    s += text(axr - 24, ayt + 6, "лінійна (B)", 10, "#1f47b5", "end", "bold")
    pts = [(ox + (i / 100.0) * (axr - 20 - ox), oy - (oy - ayt) * ((i / 100.0) ** 2.5)) for i in range(101)]
    s += polyline(pts, "#c0271e", 2.6)
    s += text(ox + 46, oy - 36, "логарифмічна (A)", 10, "#c0271e", "start", "bold")
    s += text(ox + 46, oy - 22, "для гучності", 9, GREY, "start", style="italic")
    s += line(470, 80, 470, H - 26, FAINT, 1.5)
    s += text(665, 100, "Форм-фактори", 12, INK, "middle", "bold")
    s += circle(560, 158, 26, "#eef2fb", "#1f47b5", 2); s += line(560, 158, 560, 138, INK, 2.4)
    s += text(560, 203, "панельний", 10, INK, "middle", "bold"); s += text(560, 218, "(ручка)", 9, GREY, "middle")
    s += rect(645, 138, 40, 40, "#fafafa", GREY, 1.6, 4)
    s += line(657, 158, 673, 158, INK, 2.4); s += line(665, 150, 665, 166, INK, 2.4)
    s += text(665, 203, "тример", 10, INK, "middle", "bold"); s += text(665, 218, "(викруткою, раз)", 9, GREY, "middle")
    s += rect(745, 133, 16, 55, "#eef2fb", "#1f47b5", 1.6, 3); s += rect(739, 148, 28, 12, "#cdd5da", INK, 1.4, 2)
    s += text(753, 203, "повзунковий", 10, INK, "middle", "bold"); s += text(753, 218, "(фейдер)", 9, GREY, "middle")
    s += rect(500, 248, 330, 112, "#f7f7f7", GREY, 1.4, 10)
    s += text(665, 272, "Лінійна (B) — для вимірювань і керування.", 9.5, INK, "middle", "bold")
    s += text(665, 290, "Логарифмічна (A) — для гучності (вухо", 9.5, INK, "middle")
    s += text(665, 304, "чує наростання звуку логарифмічно).", 9.5, INK, "middle")
    s += text(665, 330, "Матеріали: вуглець (дешево), кермет", 9, GREY, "middle")
    s += text(665, 344, "(тримери), провідний пластик (тихо).", 9, GREY, "middle")
    save("fig-4-6c-2-taper-types.svg", s)


# ═══ 🧮 Вставка до 4.6 — як складаються допуски ═════════════════════════════
def fig_tolerance_divider():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Похибка дільника з реальних резисторів", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "кожен резистор має допуск ±t — як він просочується у вихід V_вих?",
              10.5, GREY, "middle", style="italic")
    x = 175
    s += line(x, 92, x, 286, INK, 2.2)
    s += rect(x - 26, 118, 52, 46, "#eef2fb", "#1f47b5", 2, 6)
    s += text(x, 140, "R₁", 12, "#1f47b5", "middle", "bold")
    s += text(x, 156, "±t", 9, GREY, "middle")
    s += circle(x, 190, 4, INK, INK, 1)
    s += text(x + 16, 194, "V_вих", 11, INK, "start", "bold")
    s += rect(x - 26, 216, 52, 46, "#eef2fb", "#1f47b5", 2, 6)
    s += text(x, 238, "R₂", 12, "#1f47b5", "middle", "bold")
    s += text(x, 254, "±t", 9, GREY, "middle")
    s += text(x, 84, "+V", 11, RED, "middle", "bold")
    s += _gnd(x, 286)
    s += text(x, 318, "k = R₂/(R₁+R₂)", 11, INK, "middle", "bold")
    s += rect(355, 90, 475, 256, "#f7f7f7", GREY, 1.5, 10)
    s += text(592, 118, "Відносна похибка частки k:", 12, INK, "middle", "bold")
    s += text(375, 150, "dk/k = [R₁/(R₁+R₂)] · (ε₂ − ε₁)", 13.5, "#c0271e", "start", "bold")
    s += text(375, 174, "де ε — відносне відхилення кожного R.", 10, GREY, "start")
    s += line(375, 190, 812, 190, FAINT, 1.4)
    s += text(375, 212, "Головне: важить РІЗНИЦЯ ε₂ − ε₁,", 11, INK, "start", "bold")
    s += text(375, 230, "а не сума — бо обидва R стоять у відношенні.", 10, GREY, "start")
    s += text(375, 262, "Гірший випадок (|ε₂ − ε₁| = 2t):", 11, INK, "start", "bold")
    s += text(392, 286, "|dV_вих / V_вих| ≈ (1 − k) · 2t", 13, "#1f8a3b", "start", "bold")
    s += text(375, 318, "Напр., навпіл (k=0.5) із ±1% → гірше ±1 %.", 10, GREY, "start")
    save("fig-4-6m-1-tolerance-divider.svg", s)


def fig_worst_vs_matched():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Гірший випадок, статистика й узгоджена пара", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "приклад: дільник навпіл (k=0.5) із резисторів «±1%» — наскільки точний вихід?",
              10.5, GREY, "middle", style="italic")
    x0, y, scale = 80, 112, 470
    for lab, val, frac, col in [
        ("Гірший випадок (ε₂=+t, ε₁=−t)", "±1.0 %", 1.0, "#c0271e"),
        ("Статистика (RSS, незалежні)", "≈ ±0.7 %", 0.71, "#e08030"),
        ("Узгоджена пара (ε₁ ≈ ε₂)", "≈ 0 %", 0.05, "#1f8a3b"),
    ]:
        s += text(x0, y - 6, lab, 11, INK, "start", "bold")
        bw = scale * frac if frac > 0.02 else 12
        s += rect(x0, y + 4, bw, 30, col, col, 0, 4)
        s += text(x0 + bw + 12, y + 25, val, 12.5, col, "start", "bold")
        y += 78
    s += rect(70, H - 84, W - 140, 60, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, H - 60, "Висновок: для дільника важить не абсолютний допуск, а УЗГОДЖЕНІСТЬ резисторів.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, H - 40, "Однакове відхилення (та сама партія / збірка-масив) і однаковий дрейф температури — скорочуються.",
              10, GREY, "middle", style="italic")
    save("fig-4-6m-2-worst-vs-matched.svg", s)


# ═══ ⚙️ Вставка до 4.1 — обхід графа (DFS/BFS) ══════════════════════════════
def fig_graph_spanning_tree():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Кістякове дерево й хорди: звідки беруться незалежні контури", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "обхід графа будує дерево без петель; кожна «зайва» гілка-хорда замикає рівно один контур",
              10.5, GREY, "middle", style="italic")
    n1 = (170, 150); n2 = (380, 150); n3 = (380, 330); n4 = (170, 330)
    s += line(n1[0], n1[1], n2[0], n2[1], "#1f8a3b", 3)
    s += line(n2[0], n2[1], n3[0], n3[1], "#1f8a3b", 3)
    s += line(n3[0], n3[1], n4[0], n4[1], "#1f8a3b", 3)
    s += line(n4[0], n4[1], n1[0], n1[1], "#c0271e", 2.6, "7 5")
    s += line(n1[0], n1[1], n3[0], n3[1], "#c0271e", 2.6, "7 5")
    s += text(275, 138, "a", 11, "#1f8a3b", "middle", "bold")
    s += text(398, 240, "b", 11, "#1f8a3b", "middle", "bold")
    s += text(275, 350, "c", 11, "#1f8a3b", "middle", "bold")
    s += text(150, 240, "d", 11, "#c0271e", "middle", "bold")
    s += text(292, 250, "e", 11, "#c0271e", "middle", "bold")
    for n, lab in [(n1, "1"), (n2, "2"), (n3, "3"), (n4, "4")]:
        s += circle(n[0], n[1], 19, "#eef2fb", "#1f47b5", 2.2)
        s += text(n[0], n[1] + 5, lab, 13, INK, "middle", "bold")
    s += line(470, 116, 510, 116, "#1f8a3b", 3)
    s += text(520, 120, "гілка дерева (N−1 = 3): без петель", 10, INK, "start", "bold")
    s += line(470, 146, 510, 146, "#c0271e", 2.6, "7 5")
    s += text(520, 150, "хорда (B−N+1 = 2): замикає контур", 10, INK, "start", "bold")
    s += rect(470, 182, 362, 156, "#f7f7f7", GREY, 1.5, 10)
    s += text(488, 208, "Кожна хорда + шлях по дереву між її", 10, INK, "start")
    s += text(488, 224, "кінцями = один фундаментальний контур:", 10, INK, "start")
    s += text(488, 250, "• хорда d (4–1) → контур 1-2-3-4", 10, "#c0271e", "start", "bold")
    s += text(488, 270, "• хорда e (1–3) → контур 1-2-3", 10, "#c0271e", "start", "bold")
    s += text(488, 298, "Разом L = 2 незалежні контури —", 10, "#1f8a3b", "start", "bold")
    s += text(488, 316, "рівно B − N + 1 із §1.4.1.", 10, GREY, "start")
    save("fig-4-1a-1-spanning-tree.svg", s)


def fig_dfs_vs_bfs():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 30, "Два способи обходу: вглиб (DFS) і вшир (BFS)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "обидва відвідують усі вузли по разу за O(N+B); на МК — ітеративно, не рекурсією",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 50, FAINT, 1.5)

    def graph(ox):
        a = (ox + 60, 130); b = (ox + 180, 130); c = (ox + 180, 250); d = (ox + 60, 250)
        out = ""
        for p, q in [(a, b), (b, c), (c, d), (d, a), (a, c)]:
            out += line(p[0], p[1], q[0], q[1], "#cccccc", 2)
        for n, lab in [(a, "1"), (b, "2"), (c, "3"), (d, "4")]:
            out += circle(n[0], n[1], 16, "#eef2fb", "#1f47b5", 2)
            out += text(n[0], n[1] + 5, lab, 11, INK, "middle", "bold")
        return out

    s += text(225, 98, "DFS — вглиб (стек, LIFO)", 12, "#1f47b5", "middle", "bold")
    s += graph(135)
    s += text(225, 292, "порядок: 1 → 2 → 3 → 4 (углиб, тоді назад)", 9.5, INK, "middle", "bold")
    s += text(225, 313, "стек: кладемо сусідів, беремо з вершини", 9, GREY, "middle", style="italic")
    s += text(655, 98, "BFS — вшир (черга, FIFO)", 12, "#1f8a3b", "middle", "bold")
    s += graph(565)
    s += text(655, 292, "порядок: 1 → (2, 3) → 4 (рівнями)", 9.5, INK, "middle", "bold")
    s += text(655, 313, "черга: беремо з початку, додаємо в кінець", 9, GREY, "middle", style="italic")
    s += rect(110, H - 44, W - 220, 30, "#fff8ee", ORANGE, 1.4, 10)
    s += text(W / 2, H - 24, "На мікроконтролері — ЯВНИЙ стек/черга в пам'яті, а не рекурсія: глибокий граф переповнив би стек МК.",
              10, INK, "middle", "bold")
    save("fig-4-1a-2-dfs-vs-bfs.svg", s)


# ═══ 🧮 Вставка до 4.1 — графи й матриця інцидентності ══════════════════════
def fig_graphs_incidence():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 30, "Коло — це граф: вузли, гілки й матриця інцидентності", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "відкинь номінали — лишиться топологія: які вузли з'єднані якими гілками й у який бік",
              10.5, GREY, "middle", style="italic")
    # ── ЛІВОРУЧ: граф ──
    s += text(220, 92, "граф кола (3 вузли, 3 гілки)", 11.5, INK, "middle", "bold")
    A = (150, 185); B = (330, 185); G = (240, 310)
    for n in (A, B, G):
        s += circle(n[0], n[1], 20, "#eef2fb", "#1f47b5", 2.2)
    s += text(A[0], A[1] + 5, "A", 13, INK, "middle", "bold")
    s += text(B[0], B[1] + 5, "B", 13, INK, "middle", "bold")
    s += text(G[0], G[1] + 5, "0", 13, INK, "middle", "bold")
    s += arrow(G[0] - 8, G[1] - 16, A[0] - 2, A[1] + 20, "#c0271e", 2.2)
    s += text(160, 255, "b_s", 11, "#c0271e", "middle", "bold")
    s += arrow(A[0] + 22, A[1], B[0] - 22, B[1], "#1f8a3b", 2.2)
    s += text(240, 172, "b₁", 11, "#1f8a3b", "middle", "bold")
    s += arrow(B[0] - 2, B[1] + 20, G[0] + 8, G[1] - 16, "#1f47b5", 2.2)
    s += text(320, 255, "b₂", 11, "#1f47b5", "middle", "bold")
    s += text(240, 360, "(джерело + два резистори — один контур)", 9.5, GREY, "middle", style="italic")
    # ── ПРАВОРУЧ: матриця інцидентності ──
    s += text(660, 92, "матриця інцидентності A", 11.5, INK, "middle", "bold")
    s += text(660, 109, "рядок = вузол · стовпець = гілка", 9.5, GREY, "middle", style="italic")
    lx, ly = 545, 124
    lcw, dcw, hh, dh = 58, 62, 28, 38
    cols = ["b_s", "b₁", "b₂"]
    rows = ["A", "B", "0"]
    vals = [["−1", "+1", "0"], ["0", "−1", "+1"], ["+1", "0", "−1"]]
    for j, c in enumerate(cols):
        s += text(lx + lcw + dcw * j + dcw / 2, ly + 18, c, 11, INK, "middle", "bold")
    for i, r in enumerate(rows):
        s += text(lx + lcw / 2, ly + hh + dh * i + dh / 2 + 5, r, 11, INK, "middle", "bold")
    for i in range(3):
        for j in range(3):
            cx = lx + lcw + dcw * j
            cy = ly + hh + dh * i
            fill = "#fff7e6" if j == 1 else "#ffffff"
            col = "#c0271e" if vals[i][j] == "+1" else ("#1f47b5" if vals[i][j] == "−1" else GREY)
            s += rect(cx, cy, dcw, dh, fill, "#cccccc", 1.1, 0)
            s += text(cx + dcw / 2, cy + dh / 2 + 5, vals[i][j], 13, col, "middle", "bold")
    s += rect(lx + lcw, ly + hh, dcw * 3, dh * 3, "none", GREY, 1.6, 0)
    s += text(660, ly + hh + dh * 3 + 26, "стовпець b₁ (підсвічено): +1 при A, −1 при B", 9.5, "#a06a00", "middle", "bold")
    s += text(660, ly + hh + dh * 3 + 40, "у кожному стовпці один +1 і один −1: гілка з'єднує два вузли", 9, GREY, "middle", style="italic")
    save("fig-4-1m-1-graph-incidence.svg", s)


def fig_graphs_kcl():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 30, "KCL — це просто A·i = 0", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "добуток матриці інцидентності на вектор струмів дає закон струмів Кірхгофа в кожному вузлі",
              10.5, GREY, "middle", style="italic")
    s += text(230, 96, "A · i = 0   (кожен рядок — один вузол)", 12.5, INK, "middle", "bold")
    y = 138
    for lab, eq, note, col in [
        ("вузол A:", "−i_s + i₁ = 0", "→ i₁ = i_s", "#c0271e"),
        ("вузол B:", "−i₁ + i₂ = 0", "→ i₂ = i₁", "#1f8a3b"),
        ("вузол 0:", "+i_s − i₂ = 0", "(залежний)", "#8a8a8a"),
    ]:
        s += text(70, y, lab, 11, INK, "start", "bold")
        s += text(168, y, eq, 12, col, "start", "bold")
        s += text(322, y, note, 10.5, GREY, "start")
        y += 34
    s += rect(60, y - 4, 388, 50, "#eef7f0", GREEN, 1.6, 8)
    s += text(254, y + 16, "Рядків три, та незалежних лише N−1 = 2:", 10.5, INK, "middle", "bold")
    s += text(254, y + 33, "рядок вузла 0 — сума двох інших (опорний вузол).", 9.5, GREY, "middle", style="italic")
    s += line(478, 80, 478, H - 26, FAINT, 1.5)
    s += text(685, 100, "А контури — це KVL: B·v = 0", 12, INK, "middle", "bold")
    s += text(685, 126, "Скільки незалежних контурів?", 10.5, INK, "middle", "bold")
    s += rect(575, 142, 220, 54, "#eef2fb", "#1f47b5", 1.8, 10)
    s += text(685, 166, "L = B − N + 1", 15, "#1f47b5", "middle", "bold")
    s += text(685, 186, "(формула Ейлера, §1.4.1)", 9.5, GREY, "middle", style="italic")
    s += text(685, 224, "Приклад: B=3, N=3 → L = 1 контур", 10.5, "#1f8a3b", "middle", "bold")
    s += text(685, 262, "Так і комп'ютер будує рівняння кола:", 10, INK, "middle", "bold")
    s += text(685, 280, "A·i=0 (KCL) + B·v=0 (KVL) + закон Ома", 9.5, GREY, "middle")
    s += text(685, 296, "→ система рівнянь, яку він розв'язує.", 9.5, GREY, "middle")
    save("fig-4-1m-2-kcl-loops.svg", s)


if __name__ == "__main__":
    fig_ohm_vs_network()
    fig_kcl()
    fig_kvl()
    fig_kirchhoff_legacy()
    # §4.1 Вузли, гілки, контури
    fig41_node_branch_loop()
    fig41_same_node()
    fig41_series_parallel_topo()
    fig41_topology_vs_geometry()
    fig41_count()
    # Історія до §4.1 — Ейлер і мости
    fig_seven_bridges()
    fig_bridges_to_graph()
    fig_even_odd()
    fig_circuit_is_graph()
    # §4.2 Закон струмів (KCL)
    fig42_node_balance()
    fig42_charge_no_pileup()
    fig42_sign_convention()
    fig42_find_unknown()
    fig42_supernode()
    # §4.3 Закон напруг (KVL)
    fig43_kvl_statement()
    fig43_potential_walk()
    fig43_sign_convention()
    fig43_find_unknown()
    fig43_series_divider()
    # §4.4 Послідовне з'єднання
    fig44_series_two_facts()
    fig44_req_derivation()
    fig44_equivalent()
    fig44_worked()
    fig44_applications()
    # §4.5 Паралельне з'єднання
    fig45_two_facts()
    fig45_conductance_add()
    fig45_shortcuts()
    fig45_current_divider()
    fig45_applications()
    # §4.6 Дільник напруги
    fig46_divider_formula()
    fig46_choose_ratio()
    fig46_potentiometer()
    fig46_loading()
    fig46_sensor()
    # §4.7 Дільник струму
    fig47_formula()
    fig47_conductance()
    fig47_worked()
    fig47_shunt()
    fig47_dual()
    # §4.8 Як розв'язувати коло
    fig48_toolkit()
    fig48_reduction()
    fig48_reduction_worked()
    fig48_two_source()
    fig48_recipe()
    # §4.9 Міст Вітстона
    fig49_anatomy()
    fig49_balance()
    fig49_null()
    fig49_measure()
    fig49_sensor()
    fig49_apps()
    # §4.1 вставка (🧮) — графи й матриця інцидентності
    fig_graphs_incidence()
    fig_graphs_kcl()
    # §4.1 вставка (🔌) — макетна плата
    fig_breadboard_internals()
    fig_breadboard_chip()
    # §4.1 вставка (⚙️) — обхід графа
    fig_graph_spanning_tree()
    fig_dfs_vs_bfs()
    # §4.6 вставка (🧮) — складання допусків
    fig_tolerance_divider()
    fig_worst_vs_matched()
    # §4.6 вставка (🔌) — потенціометр і тример
    fig_pot_modes()
    fig_pot_tapers()
    # §4.6 вставка (⚙️) — добір пари E24
    fig_divider_search()
    fig_divider_algorithm()
    # §4.8 вставка (🧮) — метод Гаусса
    fig_gauss_elimination()
    fig_gauss_pivoting()
    # §4.8 вставка (⚙️) — MNA / SPICE
    fig_mna_stamping()
    fig_mna_augment()
    # §4.8 історія (📜) — контурні струми Максвелла
    fig_branch_vs_mesh()
    fig_cyclic_kcl()
    # §4.9 вставка (🧮) — чутливість мосту
    fig_bridge_linearization()
    fig_bridge_configs()
    # §4.9 історія (📜) — Крісті й Вітстон
    fig_cw_timeline()
    fig_cw_two_men()
    print("OK — фігури Розділу 4 (повна, +§4.9 міст) згенеровано в", OUT)
