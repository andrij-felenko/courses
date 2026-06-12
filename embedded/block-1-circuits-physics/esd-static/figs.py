# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 1.10 — «Електростатика на практиці: іскри,
блискавка й ESD» (Модуль 1). Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація підписів — за темою: Рис. 1.10.M.k  ↔  імена файлів fig-1-10-M-k-*.svg.
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
PURPLE = "#7a3ea8"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", GREY: "aGrey", PURPLE: "aPurple"}


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


def path(d, color=INK, w=2.4, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def plus(x, y, r=8, color=RED, w=2.6):
    return (line(x - r, y, x + r, y, color, w) + line(x, y - r, x, y + r, color, w))


def minus(x, y, r=8, color=BLUE, w=2.6):
    return line(x - r, y, x + r, y, color, w)


def _resistor_h(x, y, w=70, h=22, label="", lab_col=INK):
    """Горизонтальний резистор-прямокутник із підписом зверху."""
    out = rect(x, y - h / 2, w, h, "#fff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 7, label, 12, lab_col, "middle", "bold")
    return out


def _zigzag(x1, y1, x2, y2, n=7, amp=10, color=INK, w=2.0):
    """Зигзаг (резистор/пружина) між двома точками вздовж осі x."""
    pts = [(x1, y1)]
    for i in range(1, n):
        t = i / n
        xx = x1 + (x2 - x1) * t
        yy = y1 + (y2 - y1) * t + (amp if i % 2 else -amp)
        pts.append((xx, yy))
    pts.append((x2, y2))
    return polyline(pts, color, w)


def _spark(x1, y1, x2, y2, color=ORANGE, w=2.6, jag=5, seed=1):
    """Ламана «іскра» між двома точками (детермінований псевдовипадковий злам)."""
    pts = [(x1, y1)]
    n = jag
    rnd = seed * 1.0
    dx, dy = (x2 - x1), (y2 - y1)
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length      # нормаль
    for i in range(1, n):
        t = i / n
        rnd = (rnd * 9301 + 49297) % 233280
        off = (rnd / 233280.0 - 0.5) * 18.0
        px = x1 + dx * t + nx * off
        py = y1 + dy * t + ny * off
        pts.append((px, py))
    pts.append((x2, y2))
    return polyline(pts, color, w)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.1 — Кіловольти з нічого: трибоелектрика.  Рис. 1.10.1.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.1.1 — механізм контактної електризації (контакт → розрив) ───────
def fig_contact_charging():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Звідки беруться кіловольти: контакт двох поверхонь і розрив",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "при контакті частина електронів переходить на «жадібніший» матеріал; розрив фіксує дисбаланс",
              11.5, GREY, "middle", style="italic")

    panels = [
        (90, "1. ДО контакту", "обидва нейтральні", "neutral"),
        (385, "2. КОНТАКТ", "електрони переходять", "contact"),
        (685, "3. РОЗРИВ", "заряд застряг: + і −", "separated"),
    ]
    for x0, title, sub, kind in panels:
        s += rect(x0, 86, 220, 250, "#fcfcfc", FAINT, 1.6, 12)
        s += text(x0 + 110, 110, title, 13.5, INK, "middle", "bold")
        s += text(x0 + 110, 128, sub, 10.5, GREY, "middle", style="italic")
        ay = 230
        # дві поверхні
        if kind == "neutral":
            ax, bx = x0 + 40, x0 + 130
            for bxx, col in ((ax, INK), (bx, INK)):
                s += rect(bxx, ay - 50, 50, 100, "#f4f4f4", col, 2, 5)
            for k in range(3):
                s += plus(ax + 16, ay - 28 + k * 28, 6)
                s += minus(ax + 36, ay - 28 + k * 28, 6)
                s += plus(bx + 16, ay - 28 + k * 28, 6)
                s += minus(bx + 36, ay - 28 + k * 28, 6)
            s += text(x0 + 65, ay + 74, "A", 12, INK, "middle", "bold")
            s += text(x0 + 155, ay + 74, "B", 12, INK, "middle", "bold")
        elif kind == "contact":
            ax, bx = x0 + 62, x0 + 112
            s += rect(ax, ay - 50, 50, 100, "#f4f4f4", INK, 2, 5)
            s += rect(bx, ay - 50, 50, 100, "#eef2fb", BLUE, 2, 5)
            # стрілки переходу електронів A→B
            for k in range(3):
                yy = ay - 28 + k * 28
                s += arrow(ax + 40, yy, bx + 12, yy, BLUE, 2.0)
            s += text(x0 + 110, ay + 74, "e⁻ →", 12, BLUE, "middle", "bold")
            s += text(x0 + 110, ay + 92, "межа контакту", 9, GREY, "middle")
        else:
            ax, bx = x0 + 30, x0 + 140
            s += rect(ax, ay - 50, 50, 100, "#fdecea", RED, 2, 5)   # A втратив e → +
            s += rect(bx, ay - 50, 50, 100, "#eef2fb", BLUE, 2, 5)  # B набув e → −
            for k in range(3):
                s += plus(ax + 25, ay - 28 + k * 28, 7)
                s += minus(bx + 25, ay - 28 + k * 28, 7)
            s += text(x0 + 55, ay + 74, "A: +", 12, RED, "middle", "bold")
            s += text(x0 + 165, ay + 74, "B: −", 12, BLUE, "middle", "bold")
        # стрілка-перехід між панелями
    s += arrow(312, 210, 380, 210, INK, 2.6)
    s += arrow(607, 210, 680, 210, INK, 2.6)

    s += text(W / 2, 372, "Тертя нічого не «створює» — воно лише множить площу контактів і кількість циклів контакт↔розрив.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 394, "Розрив діелектриків не дає електронам стекти назад — тому заряд лишається й напруга злітає.",
              11, GREY, "middle")
    save("fig-1-10-1-1-contact-charging.svg", s)


# ── Рис. 1.10.1.2 — побутові й настільні джерела статики (каталог) ────────────
def fig_everyday_sources():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Де народжується статика в побуті й на робочому столі",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "усі ці сцени — один механізм: контакт різнорідних матеріалів і розрив (Рис. 1.10.1.1)",
              11.5, GREY, "middle", style="italic")

    cards = [
        (60, 80, "Хода по килиму", "підошва ↔ синтетичний ворс", "≈ 10–15 кВ", RED),
        (340, 80, "Крісло на коліщатах", "одяг ↔ оббивка при вставанні", "≈ 5–18 кВ", RED),
        (620, 80, "Зняти светр", "вовна/синтетика ↔ сорочка", "≈ 6–12 кВ", RED),
        (60, 270, "Відліпити скотч / плівку", "клейка стрічка ↔ підкладка", "≈ 8–15 кВ", ORANGE),
        (340, 270, "Витерти пластик ганчіркою", "корпус ↔ суха тканина", "≈ 6–12 кВ", ORANGE),
        (620, 270, "Дістати плату з пакета", "PCB ↔ звичайний поліетилен", "≈ 5–20 кВ", ORANGE),
    ]
    for x, y, t1, t2, kv, col in cards:
        s += rect(x, y, 260, 160, "#fcfcfc", col, 1.8, 12)
        s += text(x + 130, y + 30, t1, 14, INK, "middle", "bold")
        s += text(x + 130, y + 52, t2, 10.5, GREY, "middle")
        # піктограма-«заряджене тіло» з + угорі
        cxp = x + 130
        s += circle(cxp, y + 96, 22, "#fdecea", col, 2)
        for a in (-50, 0, 50):
            ar = math.radians(a - 90)
            s += plus(cxp + 22 * math.cos(ar), y + 96 + 22 * math.sin(ar), 5)
        s += rect(x + 70, y + 128, 120, 22, "#fff", col, 1.4, 8)
        s += text(x + 130, y + 143, kv, 12, col, "middle", "bold")

    s += text(W / 2, 452, "Сухе повітря й синтетика підсилюють кожен випадок: немає вологи, що стікала б заряд (деталі — §1.10.8).",
              11.5, INK, "middle", "bold")
    save("fig-1-10-1-2-everyday-sources.svg", s)


# ── Рис. 1.10.1.3 — трибоелектричний ряд + «відстань = сила» ──────────────────
def fig_triboelectric_series():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Трибоелектричний ряд: хто стане «+», а хто «−»",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "що далі матеріали один від одного в ряду, то більший заряд дає їх контакт і розрив",
              11.5, GREY, "middle", style="italic")

    items = [
        ("повітря, людська шкіра", RED),
        ("скло, волосся", RED),
        ("нейлон, вовна", RED),
        ("шовк, папір", INK),
        ("бавовна (≈ нейтральна)", GREY),
        ("дерево, бурштин", BLUE),
        ("гума, поліестер", BLUE),
        ("ПВХ, поліетилен", BLUE),
        ("тефлон (PTFE)", BLUE),
    ]
    x0, y0, step = 250, 95, 38
    s += text(x0 - 30, y0 - 18, "віддає e⁻ → заряджається +", 11, RED, "end", "bold")
    for i, (name, col) in enumerate(items):
        y = y0 + i * step
        s += rect(x0, y - 15, 300, 30, "#fcfcfc", col, 1.6, 7)
        s += text(x0 + 150, y + 5, name, 12.5, col, "middle", "bold")
    s += text(x0 - 30, y0 + (len(items) - 1) * step + 22, "забирає e⁻ → заряджається −",
              11, BLUE, "end", "bold")
    # шкала-стрілка зліва
    s += arrow(x0 - 22, y0 - 8, x0 - 22, y0 + (len(items) - 1) * step + 8, GREY, 2.0)

    # ілюстрація «далека пара = сильно»
    bx = x0 + 340
    s += rect(bx, 100, 300, 150, "#eef7f0", GREEN, 1.6, 10)
    s += text(bx + 150, 124, "Далека пара — сильна електризація", 11.5, GREEN, "middle", "bold")
    s += text(bx + 150, 144, "волосся (верх) × тефлон (низ)", 10, INK, "middle")
    s += circle(bx + 70, 195, 26, "#fdecea", RED, 2)
    for a in (-45, 0, 45):
        ar = math.radians(a - 90)
        s += plus(bx + 70 + 26 * math.cos(ar), 195 + 26 * math.sin(ar), 6)
    s += circle(bx + 230, 195, 26, "#eef2fb", BLUE, 2)
    for a in (135, 180, 225):
        ar = math.radians(a - 90)
        s += minus(bx + 230 + 26 * math.cos(ar), 195 + 26 * math.sin(ar), 6)
    s += text(bx + 150, 200, "сильне", 11, GREEN, "middle", "bold")

    s += rect(bx, 270, 300, 150, "#f4f6f9", GREY, 1.6, 10)
    s += text(bx + 150, 294, "Близька пара — слабка електризація", 11.5, GREY, "middle", "bold")
    s += text(bx + 150, 314, "бавовна × папір (поряд у ряду)", 10, INK, "middle")
    s += circle(bx + 70, 365, 26, "#fafafa", GREY, 2)
    s += plus(bx + 70, 365, 5, GREY)
    s += circle(bx + 230, 365, 26, "#fafafa", GREY, 2)
    s += minus(bx + 230, 365, 5, GREY)
    s += text(bx + 150, 370, "ледь-ледь", 11, GREY, "middle", "bold")

    s += text(W / 2, 452, "Це той самий ряд, що в §1.1.1 — тут ним користуються, щоб обрати безпечні матеріали для столу й одягу.",
              11, INK, "middle", "bold")
    save("fig-1-10-1-3-triboelectric-series.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.2 — Тіло як накопичувач заряду.  Рис. 1.10.2.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.2.1 — тіло+взуття+підлога = конденсатор ─────────────────────────
def fig_body_capacitor():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 30, "Тіло як обкладинка конденсатора відносно землі",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "людина, ізольована підошвою й сухою підлогою, тримає заряд на ємності ≈ 100–200 пФ",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: схематична людина на підлозі ──
    px = 220
    # голова + тулуб
    s += circle(px, 120, 26, "#fdecea", RED, 2.2)
    s += polygon([(px - 34, 150), (px + 34, 150), (px + 26, 300), (px - 26, 300)], "#fdecea", RED, 2.2)
    for k in range(4):
        s += plus(px - 14 + (k % 2) * 28, 175 + (k // 2) * 40, 7)
    s += plus(px, 120, 7)
    s += text(px, 110, "+Q", 12, RED, "middle", "bold")
    # ноги/взуття
    s += rect(px - 26, 300, 22, 36, "#444", INK, 1.6, 3)
    s += rect(px + 4, 300, 22, 36, "#444", INK, 1.6, 3)
    s += text(px + 64, 322, "підошва (ізолятор)", 10, GREY, "start")
    # підлога
    s += rect(60, 340, 360, 26, "#e9e2d4", INK, 1.8)
    s += text(240, 357, "підлога / земля (друга обкладинка)", 10.5, INK, "middle", "bold")
    # «зазор» діелектрика — підошва
    s += line(px - 30, 336, px + 30, 336, GREEN, 2.0, "4,3")
    s += arrow(px + 40, 336, px + 40, 318, GREEN, 1.6)
    s += arrow(px + 40, 336, px + 40, 354, GREEN, 1.6)
    s += text(px + 46, 348, "d", 11, GREEN, "start", "bold", "italic")

    # ── праворуч: еквівалентна схема C та формула Q=CV ──
    bx = 520
    s += rect(bx, 92, 360, 274, "#fcfcfc", FAINT, 1.6, 12)
    s += text(bx + 180, 116, "Еквівалент: заряджений конденсатор", 12.5, INK, "middle", "bold")
    # верхня обкладинка (тіло)
    cx = bx + 180
    s += line(cx - 70, 160, cx + 70, 160, RED, 4)
    s += text(cx + 86, 164, "тіло", 11, RED, "start", "bold")
    for k in range(3):
        s += plus(cx - 40 + k * 40, 148, 6)
    # нижня обкладинка (земля)
    s += line(cx - 70, 210, cx + 70, 210, INK, 4)
    for k in range(3):
        s += minus(cx - 40 + k * 40, 222, 6)
    # символ землі
    s += line(cx, 210, cx, 240, INK, 2.2)
    s += line(cx - 22, 240, cx + 22, 240, INK, 2.4)
    s += line(cx - 14, 248, cx + 14, 248, INK, 2.4)
    s += line(cx - 7, 256, cx + 7, 256, INK, 2.4)
    s += text(cx - 86, 188, "C ≈ 100 пФ", 12.5, INK, "end", "bold", "italic")
    # формула
    s += rect(bx + 30, 286, 300, 64, "#eef2fb", BLUE, 1.6, 9)
    s += text(bx + 180, 310, "Q = C · V", 15, BLUE, "middle", "bold", "italic")
    s += text(bx + 180, 334, "ту саму статику тіло «несе» як напругу V", 10, INK, "middle")

    s += text(W / 2, 396, "Ємність мала (пікофаради), тож навіть крихітний заряд (нанокулони) дає кіловольти: V = Q/C.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 418, "Це фізична основа моделі людського тіла (HBM) — числа в §1.10.2 (вставка 🧮).",
              10.5, GREY, "middle")
    save("fig-1-10-2-1-body-capacitor.svg", s)


# ── Рис. 1.10.2.2 — драбина напруг: відчуття проти порога загибелі чипа ───────
def fig_voltage_ladder():
    W, H = 900, 520
    s = header(W, H)
    s += text(W / 2, 30, "Скільки вольтів ти носиш — і де межа відчуття та межа смерті чипа",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "людина відчуває розряд лише від ~3 кВ; найчутливіші компоненти гинуть від десятків–сотень вольт",
              11.5, GREY, "middle", style="italic")

    # вертикальна логарифмічна шкала напруг
    ax, ytop, ybot = 360, 100, 470
    s += arrow(ax, ybot, ax, ytop - 6, INK, 2.4)
    s += text(ax, ytop - 16, "V (лог)", 11, INK, "middle", "bold")

    # позиції в декадах: 10 .. 30000 В
    def yat(v):
        lo, hi = math.log10(10), math.log10(30000)
        f = (math.log10(v) - lo) / (hi - lo)
        return ybot - f * (ybot - ytop)

    for v, lab in [(10, "10 В"), (100, "100 В"), (1000, "1 кВ"), (10000, "10 кВ"), (30000, "30 кВ")]:
        y = yat(v)
        s += line(ax - 6, y, ax + 6, y, INK, 1.6)
        s += text(ax - 12, y + 4, lab, 10.5, INK, "end", "bold")

    # ЛІВОРУЧ — пороги загибелі компонентів (червона зона «небезпечно й непомітно»)
    left = [
        (30, "MOSFET-затвор, ВЧ-входи", RED),
        (100, "багато КМОН-входів", RED),
        (250, "типові логічні ІМС", ORANGE),
        (2000, "стійкіші входи з захистом", GREEN),
    ]
    for v, lab, col in left:
        y = yat(v)
        s += line(ax - 6, y, 150, y, col, 1.4, "4,3")
        s += circle(ax - 6, y, 3.4, col, col, 1)
        s += rect(30, y - 14, 230, 26, "#fff", col, 1.5, 7)
        s += text(145, y + 4, lab, 10.5, col, "middle", "bold")
    s += text(145, ytop - 6, "← гине КОМПОНЕНТ", 11.5, RED, "middle", "bold")

    # ПРАВОРУЧ — пороги людського сприйняття
    right = [
        (3000, "ледь відчутно (поколювання)", INK),
        (5000, "чути «клац», видно іскру", INK),
        (10000, "відчутний укол", INK),
        (20000, "болісно, іскра ~ кілька мм", INK),
    ]
    for v, lab, col in right:
        y = yat(v)
        s += line(ax + 6, y, 560, y, GREY, 1.4, "4,3")
        s += circle(ax + 6, y, 3.4, GREEN, GREEN, 1)
        s += rect(560, y - 14, 300, 26, "#eef7f0", GREEN, 1.5, 7)
        s += text(710, y + 4, lab, 10.5, INK, "middle", "bold")
    s += text(710, ytop - 6, "ВІДЧУВАЄ людина →", 11.5, GREEN, "middle", "bold")

    # «сліпа зона»
    yb1, yb2 = yat(3000), yat(30)
    s += rect(150, yb1, 4, yb2 - yb1, RED, RED, 0)
    s += text(W / 2, 500, "Між ~30 В і ~3000 В — «сліпа зона»: розряд уже вбиває чип, а ти ще нічого не відчуваєш. Тому статику не «ловлять» відчуттям.",
              11.5, RED, "middle", "bold")
    save("fig-1-10-2-2-voltage-ladder.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.3 — Пробій повітря: іскра, корона й вістря.  Рис. 1.10.3.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.3.1 — лавина: вільний електрон вибиває нові (іонізація) ─────────
def fig_avalanche():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 30, "Чому повітря раптом «пробиває»: електронна лавина",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "сильне поле розганяє вільний електрон так, що він вибиває з молекули новий — і їх число лавинно росте",
              11.5, GREY, "middle", style="italic")

    # дві пластини (катод − ліворуч, анод + праворуч)
    lx, rx, ay = 110, 810, 215
    s += rect(lx - 22, ay - 110, 22, 220, "#eef2fb", BLUE, 2)
    s += rect(rx, ay - 110, 22, 220, "#fdecea", RED, 2)
    s += text(lx - 11, ay + 132, "−", 18, BLUE, "middle", "bold")
    s += text(rx + 11, ay + 132, "+", 18, RED, "middle", "bold")
    s += text(lx - 11, ay - 122, "катод", 10, BLUE, "middle", "bold")
    s += text(rx + 11, ay - 122, "анод", 10, RED, "middle", "bold")
    # поле
    for yy in (ay - 80, ay - 40, ay, ay + 40, ay + 80):
        s += arrow(lx + 4, yy, rx - 4, yy, FAINT, 1.2)
    s += text(W / 2, ay - 96, "поле E", 10.5, GREEN, "middle", "bold", "italic")

    # лавина: дерево електронів, що множаться
    levels = [(150, 1), (300, 2), (450, 4), (600, 7), (740, 11)]
    prev = [(lx + 10, ay)]
    for (xx, cnt) in levels:
        ys = [ay + (i - (cnt - 1) / 2.0) * (170.0 / max(cnt, 1)) for i in range(cnt)]
        for y in ys:
            s += circle(xx, y, 5.5, "#eef2fb", BLUE, 1.6)
            s += minus(xx, y, 3.5, BLUE, 1.8)
        # з'єднати з попереднім рівнем (із найближчого)
        for y in ys:
            py = min(prev, key=lambda p: abs(p[1] - y))
            s += arrow(py[0] + 6, py[1], xx - 6, y, BLUE, 1.2)
        # позитивний іон лишається (червоний +)
        if cnt > 1:
            s += plus(xx - 24, ys[0] - 16, 4, RED, 1.8)
        prev = [(xx, y) for y in ys]

    s += text(W / 2, 360, "1 → 2 → 4 → 8 …: за частки наносекунди ниткою біжить мільярд носіїв — це й є струм іскри.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 382, "Поріг — близько 3 кВ на кожен міліметр сухого повітря за нормальних умов (≈ 3 кВ/мм = 3 МВ/м).",
              11, GREY, "middle")
    save("fig-1-10-3-1-avalanche.svg", s)


# ── Рис. 1.10.3.2 — 3 кВ/мм: зазор проти пробивної напруги ────────────────────
def fig_breakdown_gap():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Правило ≈ 3 кВ/мм: який зазор пробиває яка напруга",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "лінійна оцінка для рівних електродів у сухому повітрі: довжина іскри ≈ напруга / 3 кВ",
              11.5, GREY, "middle", style="italic")

    # графік V(d) лінійний
    ax, ay, aw, ah = 110, 320, 660, 230
    s += arrow(ax, ay, ax + aw + 12, ay, INK, 2.0)
    s += arrow(ax, ay, ax, ay - ah - 12, INK, 2.0)
    s += text(ax + aw + 8, ay + 22, "зазор d, мм", 11, INK, "middle", "bold")
    s += text(ax - 8, ay - ah - 18, "пробивна напруга, кВ", 11, INK, "start", "bold")

    # сітка + лінія V = 3·d
    dmax = 10.0
    vmax = 30.0
    for d in range(0, 11, 2):
        x = ax + aw * d / dmax
        s += line(x, ay, x, ay + 6, INK, 1.4)
        s += text(x, ay + 22, str(d), 10, INK, "middle")
    for v in range(0, 31, 6):
        y = ay - ah * v / vmax
        s += line(ax - 6, y, ax, y, INK, 1.4)
        s += text(ax - 10, y + 4, str(v), 10, INK, "end")
    s += polyline([(ax, ay), (ax + aw, ay - ah)], RED, 3.0)
    s += text(ax + aw - 6, ay - ah + 18, "V ≈ 3 кВ/мм · d", 12.5, RED, "end", "bold", "italic")

    # маркери: іскра від тіла, свічка запалювання тощо
    pts = [(0.3, "поколювання пальцем\n~1 кВ → ~0.3 мм", GREEN),
           (2.0, "відчутна іскра 6 кВ\n→ ~2 мм", ORANGE),
           (6.0, "20 кВ статики\n→ ~6–7 мм", RED)]
    for d, lab, col in pts:
        x = ax + aw * d / dmax
        v = 3.0 * d
        y = ay - ah * v / vmax
        s += circle(x, y, 4.5, col, col, 1)
        s += line(x, y, x + 14, y - 34, col, 1.2, "3,3")
        for i, ln in enumerate(lab.split("\n")):
            s += text(x + 18, y - 36 + i * 13, ln, 9.5, col, "start", "bold")

    s += text(W / 2, 372, "Правило грубе (рівні електроди, нормальні умови) — біля вістря пробій починається набагато раніше (нижче).",
              11, GREY, "middle")
    save("fig-1-10-3-2-breakdown-gap.svg", s)


# ── Рис. 1.10.3.3 — згущення заряду на вістрі → корона й громовідвід ──────────
def fig_point_corona():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Чому вістря: заряд згущується на гострому, і поле там найсильніше",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "на провіднику заряд тим густіший, чим менший радіус кривини — біля кінчика поле б'є першим",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: куля проти вістря, густина заряду ──
    # куля
    s += circle(170, 170, 50, "#fafafa", INK, 2)
    for a in range(0, 360, 30):
        ar = math.radians(a)
        s += plus(170 + 50 * math.cos(ar), 170 + 50 * math.sin(ar), 5)
    s += text(170, 248, "велика куля:", 11, INK, "middle", "bold")
    s += text(170, 264, "заряд рідкий, поле слабке", 9.5, GREY, "middle")

    # крапля з вістрям (грушоподібний провідник)
    cx2 = 360
    s += path(f"M {cx2-46} 150 A 46 46 0 1 0 {cx2+46} 150 "
              f"L {cx2+12} 70 L {cx2-12} 70 Z", INK, 2, "#fafafa")
    # рідкі + на тілі, густі на вістрі
    for a in (210, 250, 290, 330):
        ar = math.radians(a)
        s += plus(cx2 + 46 * math.cos(ar), 170 + 46 * math.sin(ar), 5)
    for k in range(5):
        s += plus(cx2 - 8 + k * 4, 78 + (k % 2) * 6, 4)
    s += text(cx2, 248, "вістря:", 11, RED, "middle", "bold")
    s += text(cx2, 264, "заряд згущується на кінчику", 9.5, RED, "middle")
    # корона біля вістря
    for a in range(-60, 61, 30):
        ar = math.radians(a - 90)
        s += line(cx2, 70, cx2 + 30 * math.cos(ar), 70 + 30 * math.sin(ar), PURPLE, 1.6)
    s += text(cx2 + 60, 60, "корона", 10.5, PURPLE, "start", "bold")

    s += line(470, 80, 470, 300, FAINT, 1.6)

    # ── праворуч: громовідвід на будинку ──
    bx = 560
    # будинок
    s += polygon([(bx, 300), (bx, 200), (bx + 90, 150), (bx + 180, 200), (bx + 180, 300)],
                 "#f4efe6", INK, 2)
    # щогла-вістря
    tipx = bx + 90
    s += line(tipx, 150, tipx, 80, GREY, 3)
    s += polygon([(tipx - 5, 82), (tipx + 5, 82), (tipx, 64)], GREY, INK, 1)
    # хмара
    s += path(f"M {bx+40} 70 q 20 -30 55 -16 q 25 -26 55 -2 q 28 -6 24 22 q 8 22 -22 22 "
              f"L {bx+60} 96 q -30 0 -20 -26 Z", BLUE, 1.6, "#eef2fb")
    for k in range(4):
        s += minus(bx + 60 + k * 24, 92, 6)
    s += text(bx + 110, 56, "хмара (−)", 10, BLUE, "middle", "bold")
    # корона/розряд із вістря в хмару
    s += _spark(tipx, 64, bx + 96, 92, PURPLE, 2.4, jag=6, seed=7)
    # провід заземлення
    s += polyline([(tipx, 150), (bx + 180, 230), (bx + 200, 300)], COPPER, 2.6)
    s += text(bx + 210, 290, "до землі", 10, COPPER, "start", "bold")
    # земля
    s += rect(bx - 10, 300, 240, 18, "#e9e2d4", INK, 1.6)
    s += text(bx + 90, 340, "Громовідвід гострий навмисно:", 11, INK, "middle", "bold")
    s += text(bx + 90, 356, "сильне поле на кінчику стікає заряд тихою короною", 9.5, GREY, "middle")
    s += text(bx + 90, 372, "або приймає удар на себе — поле біля вістря з §1.1.3", 9.5, GREY, "middle")

    s += text(W / 2, 410, "Той самий механізм шкодить у роботі: гострі виводи й кромки концентрують поле — звідти й починається ESD-пробій.",
              11, INK, "middle", "bold")
    save("fig-1-10-3-3-point-corona.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.4 — Блискавка.  Рис. 1.10.4.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.4.1 — розділення зарядів у грозовій хмарі ───────────────────────
def fig_cloud_charge():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Як хмара стає велетенським конденсатором",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "висхідні потоки тягнуть угору легкі крижинки (+), важка крупа (−) осідає — заряди розходяться по висоті",
              11.5, GREY, "middle", style="italic")

    # контур хмари
    s += path("M 200 110 q 40 -60 110 -34 q 50 -52 120 -8 q 70 -24 96 40 "
              "q 60 10 40 70 q 30 56 -40 60 L 230 308 q -80 4 -70 -56 "
              "q -60 -6 -30 -70 q -30 -60 30 -84 Z", GREY, 2, "#eef1f6")

    # верх (+)
    for x in range(250, 600, 48):
        s += plus(x, 120, 7)
    s += text(W / 2, 100, "верх хмари: + (крижані кристали, висхідний потік)", 11.5, RED, "middle", "bold")
    # середина (−)
    for x in range(250, 600, 48):
        s += minus(x, 250, 7)
    s += text(W / 2, 285, "низ хмари: − (важка крупа осідає)", 11.5, BLUE, "middle", "bold")
    # маленька кишеня + унизу (типова структура)
    s += plus(420, 300, 6, RED)
    s += text(470, 305, "мала кишеня +", 9, RED, "start")

    # земля з наведеним +
    s += rect(80, 400, 740, 22, "#e9e2d4", INK, 1.8)
    for x in range(160, 760, 60):
        s += plus(x, 388, 6)
    s += text(W / 2, 440, "Земля під хмарою наводиться додатно (−низ хмари притягує +): між ними наростає поле.",
              11.5, INK, "middle", "bold")
    # стрілки поля вниз
    for x in (260, 420, 580):
        s += arrow(x, 320, x, 380, GREEN, 1.6)
    s += text(640, 350, "поле росте до пробою", 10, GREEN, "start", "bold", "italic")
    s += text(W / 2, 460, "Це той самий механізм розділення заряду тертям (§1.1.1, §1.10.1) — лише в масштабі кілометрів.",
              10.5, GREY, "middle")
    save("fig-1-10-4-1-cloud-charge.svg", s)


# ── Рис. 1.10.4.2 — лідер і зворотний удар (стадії розряду) ───────────────────
def fig_leader_stroke():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Стадії удару: ступінчастий лідер вниз — і яскравий зворотний удар угору",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "слабкий канал намацує шлях сходинками; коли він торкається землі, нагору б'є головний струм",
              11.5, GREY, "middle", style="italic")

    panels = [
        (70, "1. Ступінчастий лідер", "тьмяний канal намацує шлях\nсходинками вниз (≈50 м)", "leader"),
        (390, "2. Зустрічний стример", "із землі (вістря, дерева)\nросте назустріч +канал", "streamer"),
        (710, "3. Зворотний удар", "канал замкнувся — нагору б'є\nяскравий струм (десятки кА)", "return"),
    ]
    for x0, title, sub, kind in panels:
        s += rect(x0, 80, 220, 300, "#fcfcfc", FAINT, 1.6, 12)
        s += text(x0 + 110, 104, title, 12.5, INK, "middle", "bold")
        for i, ln in enumerate(sub.split("\n")):
            s += text(x0 + 110, 122 + i * 14, ln.replace("canal", "канал"), 9.3, GREY, "middle")
        # хмара зверху
        s += path(f"M {x0+30} 168 q 20 -26 55 -14 q 28 -22 55 -2 q 26 -6 22 20 "
                  f"L {x0+50} 192 q -28 0 -20 -24 Z", BLUE, 1.4, "#eef2fb")
        for k in range(3):
            s += minus(x0 + 55 + k * 26, 188, 5)
        # земля
        s += rect(x0 + 10, 348, 200, 16, "#e9e2d4", INK, 1.6)
        gx = x0 + 110
        if kind == "leader":
            # ступінчастий пунктир вниз
            ys = [(x0 + 100, 192), (x0 + 116, 230), (x0 + 96, 262), (x0 + 120, 296), (x0 + 102, 330)]
            s += polyline(ys, PURPLE, 2.2, "5,4")
            s += circle(x0 + 102, 330, 4, PURPLE, PURPLE, 1)
            s += text(x0 + 150, 250, "слабкий\n(тьмяний)", 9, PURPLE, "start", "bold")
        elif kind == "streamer":
            ys = [(x0 + 100, 192), (x0 + 116, 230), (x0 + 96, 262), (x0 + 120, 296), (x0 + 108, 320)]
            s += polyline(ys, PURPLE, 2.2, "5,4")
            # зустрічний стример від землі
            s += polyline([(x0 + 108, 348), (x0 + 116, 332), (x0 + 108, 320)], RED, 2.4)
            s += plus(x0 + 120, 338, 5, RED)
            s += text(x0 + 132, 344, "+ із землі", 8.5, RED, "start", "bold")
        else:
            # яскравий товстий канал
            s += _spark(gx + 6, 192, gx, 348, ORANGE, 5.0, jag=7, seed=3)
            s += _spark(gx + 6, 192, gx, 348, "#ffd27a", 2.0, jag=7, seed=3)
            s += arrow(gx + 40, 320, gx + 24, 230, RED, 2.6)
            s += text(gx + 46, 290, "струм\nугору", 9, RED, "start", "bold")
        # стрілка-перехід
    s += arrow(296, 230, 386, 230, INK, 2.4)
    s += arrow(616, 230, 706, 230, INK, 2.4)

    s += text(W / 2, 404, "Те, що ми бачимо як спалах, — це зворотний удар: розряд того самого «хмара ↔ земля» конденсатора з Рис. 1.10.4.1.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 426, "Блискавка й іскра з пальця — одне явище: пробій повітря (§1.10.3). Різниця лише в запасеному заряді й енергії.",
              10.5, GREY, "middle")
    save("fig-1-10-4-2-leader-stroke.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.5 — Приховані ESD-пошкодження.  Рис. 1.10.5.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.5.1 — масштаб: тонкий підзатворний оксид проти 3 кВ/мм ──────────
def fig_thin_oxide():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 30, "Чому чип такий тендітний: ізолятор завтовшки в десятки атомів",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "підзатворний оксид сучасного транзистора — кілька нанометрів; його пробиває вже кілька вольт",
              11.5, GREY, "middle", style="italic")

    # ліворуч: розріз MOS-структури з тонким оксидом
    bx = 120
    s += text(bx + 130, 92, "Розріз: затвор — оксид — кремній", 12, INK, "middle", "bold")
    s += rect(bx, 110, 260, 34, "#cfd6e6", BLUE, 2)        # затвор (метал/полікремній)
    s += text(bx + 130, 132, "затвор (gate)", 11, BLUE, "middle", "bold")
    s += rect(bx, 144, 260, 12, "#ffe3b0", ORANGE, 1.6)    # оксид — тонесенький
    s += text(bx + 270, 152, "оксид ≈ 2–10 нм", 10.5, ORANGE, "start", "bold")
    s += rect(bx, 156, 260, 70, "#e9e9e9", INK, 2)         # кремній
    s += text(bx + 130, 196, "кремній (підкладка)", 11, INK, "middle", "bold")
    # збільшувальна винесена «лінза» на оксид
    s += line(bx + 200, 150, bx + 250, 270, GREY, 1.2, "3,3")
    s += line(bx + 220, 150, bx + 130, 270, GREY, 1.2, "3,3")
    s += rect(bx + 40, 270, 210, 90, "#fffaf0", ORANGE, 1.6, 8)
    s += text(bx + 145, 292, "у масштабі атомів:", 10.5, ORANGE, "middle", "bold")
    for k in range(9):
        s += circle(bx + 70 + k * 14, 320, 5, "#ffd27a", ORANGE, 1.2)
    s += text(bx + 145, 348, "~ кілька десятків шарів атомів", 9.5, INK, "middle")

    # праворуч: порівняння пробивної напруги
    rx = 560
    s += rect(rx, 100, 320, 270, "#fcfcfc", FAINT, 1.6, 12)
    s += text(rx + 160, 124, "Те саме поле 3 кВ/мм — інша товщина", 11.5, INK, "middle", "bold")
    rows = [("повітря 1 мм", 3000, "≈ 3000 В", GREEN),
            ("папір 0.1 мм", 1000, "≈ 1000 В", INK),
            ("оксид 5 нм", 1, "≈ кілька В!", RED)]
    y = 160
    for lab, _, vlab, col in rows:
        s += text(rx + 24, y + 4, lab, 11, col, "start", "bold")
        s += text(rx + 296, y + 4, vlab, 11.5, col, "end", "bold")
        s += line(rx + 24, y + 16, rx + 296, y + 16, FAINT, 1.2)
        y += 56
    s += rect(rx + 24, 318, 272, 40, "#fdecea", RED, 1.6, 8)
    s += text(rx + 160, 343, "5 нм пробиває вже ~5 В — а тіло несе тисячі",
              10.5, RED, "middle", "bold")

    s += text(W / 2, 400, "Поле «вольт на товщину» однакове за фізикою — але коли товщина в нанометрах, безпечних вольтів лишаються одиниці.",
              11, INK, "middle", "bold")
    save("fig-1-10-5-1-thin-oxide.svg", s)


# ── Рис. 1.10.5.2 — катастрофа проти латентного пошкодження (ванна відмов) ────
def fig_latent_damage():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Дві долі чипа після розряду: миттєва смерть або тиха деградація",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "сильний удар убиває одразу; слабкий лишає прихований дефект, що відмовить пізніше — у полі",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: дві гілки ──
    s += rect(60, 86, 380, 150, "#fdecea", RED, 1.8, 12)
    s += text(250, 110, "КАТАСТРОФІЧНИЙ збій", 13, RED, "middle", "bold")
    s += text(250, 132, "оксид пробитий наскрізь / провідник випарувано", 10, INK, "middle")
    s += text(250, 152, "чип мертвий ОДРАЗУ — видно на тесті", 10.5, RED, "middle", "bold")
    # піктограма пробитого оксиду
    s += rect(150, 168, 200, 14, "#ffe3b0", ORANGE, 1.4)
    s += _spark(250, 168, 250, 182, RED, 2.4, jag=4, seed=2)
    s += text(250, 204, "наскрізна дірка", 9.5, RED, "middle", "bold")

    s += rect(60, 256, 380, 150, "#fff7e6", ORANGE, 1.8, 12)
    s += text(250, 280, "ЛАТЕНТНЕ (приховане) пошкодження", 12.5, ORANGE, "middle", "bold")
    s += text(250, 302, "оксид лише ослаблений, доріжка підтоплена", 10, INK, "middle")
    s += text(250, 322, "тест проходить ✓ — а ресурс уже з'їдено", 10.5, ORANGE, "middle", "bold")
    s += rect(150, 338, 200, 14, "#ffe3b0", ORANGE, 1.4)
    s += line(220, 345, 280, 345, RED, 2.0, "3,2")
    s += text(250, 374, "мікротріщина — відмова через тижні/місяці", 9.5, RED, "middle", "bold")

    # ── праворуч: крива відмов у часі (рання «дитяча смертність») ──
    ax, ay, aw, ah = 540, 350, 350, 220
    s += arrow(ax, ay, ax + aw + 12, ay, INK, 2.0)
    s += arrow(ax, ay, ax, ay - ah - 12, INK, 2.0)
    s += text(ax + aw + 8, ay + 22, "час служби", 10.5, INK, "middle", "bold")
    s += text(ax - 6, ay - ah - 18, "інтенсивність відмов", 10.5, INK, "start", "bold")
    # нормальна «ванна» — бліда
    norm = []
    for i in range(101):
        t = i / 100.0
        y = 0.18 + 0.7 * math.exp(-t * 9) + 0.6 * (t ** 4)
        norm.append((ax + aw * t, ay - ah * min(y, 1.0) * 0.62))
    s += polyline(norm, GREY, 2.0, "5,4")
    s += text(ax + aw - 8, ay - ah * 0.50, "норма", 10, GREY, "end", "bold")
    # з латентними дефектами — вища рання частина
    dmg = []
    for i in range(101):
        t = i / 100.0
        y = 0.3 + 1.5 * math.exp(-t * 5) + 0.6 * (t ** 4)
        dmg.append((ax + aw * t, ay - ah * min(y, 1.05) * 0.62))
    s += polyline(dmg, RED, 2.8)
    s += text(ax + 90, ay - ah * 0.80, "з латентним ESD", 10.5, RED, "middle", "bold")
    # зона ранніх відмов
    s += rect(ax, ay - ah, aw * 0.32, ah, "#fdecea", "none", 0)
    s += text(ax + aw * 0.16, ay + 38, "ранні («дитячі») відмови ↑", 10, RED, "middle", "bold")

    s += text(W / 2, 426, "Найковарніше — латентний дефект: контроль на виході його не ловить, і пристрій помирає вже в користувача.",
              11.5, INK, "middle", "bold")
    save("fig-1-10-5-2-latent-damage.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.6 — Антистатичне робоче місце.  Рис. 1.10.6.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.6.1 — заземлений робочий стіл: спільна точка й шляхи стікання ───
def fig_esd_bench():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 30, "Антистатичне робоче місце: усе стікає в одну спільну точку",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "браслет, мат і виріб з'єднані з тією самою землею, тож між ними не буває різниці потенціалів",
              11.5, GREY, "middle", style="italic")

    # мат на столі
    s += rect(120, 300, 560, 26, "#3f6f5f", INK, 2, 4)
    s += text(400, 317, "розсіювальний (dissipative) настільний мат", 11, "#eaf3ee", "middle", "bold")
    # майстер (рука) + браслет
    s += circle(220, 150, 26, "#fdecea", RED, 2)
    s += polygon([(196, 176), (244, 176), (236, 300), (204, 300)], "#fde9e9", RED, 2)
    s += rect(232, 232, 40, 16, "#888", INK, 1.6, 3)      # браслет
    s += text(252, 226, "браслет", 9.5, INK, "middle", "bold")
    # виток шнура браслета (спіраль натяком)
    s += polyline([(272, 240), (300, 250), (286, 262), (312, 270), (298, 282), (330, 290)], INK, 1.8)
    # виріб (плата) на маті
    s += rect(430, 268, 120, 32, "#244", GREEN, 2, 4)
    s += text(490, 288, "виріб (PCB)", 10.5, "#dff0e6", "middle", "bold")

    # спільна точка заземлення (common point) праворуч
    cpx, cpy = 760, 300
    s += circle(cpx, cpy, 10, "#fff", INK, 2.4)
    s += text(cpx, cpy - 18, "спільна точка", 10.5, INK, "middle", "bold")
    s += text(cpx, cpy - 4, "(common)", 9, GREY, "middle")

    # резистори 1 МОм у кожному шляху
    # шлях браслета
    s += line(330, 290, 470, 240, INK, 2)
    s += _resistor_h(478, 240, 60, 20, "1 МОм", RED)
    s += line(538, 240, 700, 270, INK, 2)
    s += text(560, 224, "шлях браслета", 9.5, INK, "start", "bold")
    # шлях мата
    s += line(680, 313, 705, 305, INK, 2)
    s += _resistor_h(610, 360, 60, 20, "1 МОм", RED)
    s += line(560, 360, 350, 326, INK, 2)
    s += line(670, 360, 705, 312, INK, 2)
    s += text(540, 384, "шлях мата", 9.5, INK, "start", "bold")
    # шлях обладнання (PE розетки) — без 1 МОм (силова земля)
    s += line(cpx, cpy + 10, cpx, 400, GREEN, 2.6)
    # символ землі
    s += line(cpx - 26, 400, cpx + 26, 400, GREEN, 2.6)
    s += line(cpx - 17, 408, cpx + 17, 408, GREEN, 2.6)
    s += line(cpx - 8, 416, cpx + 8, 416, GREEN, 2.6)
    s += text(cpx + 34, 408, "земля (PE розетки)", 10, GREEN, "start", "bold")

    # пояснення 1 МОм
    s += rect(60, 430, 520, 30, "#eef2fb", BLUE, 1.4, 8)
    s += text(70, 450, "Навіщо 1 МОм: він стікає статику повільно й безпечно, але обмежує струм при випадковому дотику до фази.",
              10.5, INK, "start", "bold")
    s += rect(596, 430, 350, 30, "#eef7f0", GREEN, 1.4, 8)
    s += text(606, 450, "Виняток — корпус приладу: він на «твердій» землі без 1 МОм (захист людини).",
              9.8, INK, "start", "bold")
    save("fig-1-10-6-1-esd-bench.svg", s)


# ── Рис. 1.10.6.2 — навіщо саме 1 МОм: дві вимоги тягнуть у різні боки ─────────
def fig_one_megohm():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 30, "Чому всюди 1 МОм: компроміс між стіканням статики й безпекою людини",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "замалий опір — небезпечно для людини; завеликий — статика не встигає стікати; 1 МОм влучає між",
              11.5, GREY, "middle", style="italic")

    # ліва вимога
    s += rect(60, 90, 360, 130, "#fdecea", RED, 1.8, 12)
    s += text(240, 116, "Якби 0 Ом (пряме заземлення)", 12.5, RED, "middle", "bold")
    s += text(240, 140, "дотик до фази 230 В → крізь людину", 10.5, INK, "middle")
    s += text(240, 160, "I = 230 В / (опір тіла) → десятки мА", 11, RED, "middle", "bold")
    s += text(240, 182, "смертельно небезпечно (з §1.2.13)", 10.5, RED, "middle", "bold")
    s += text(240, 202, "потрібен послідовний опір!", 10, INK, "middle", style="italic")

    # права вимога
    s += rect(500, 90, 360, 130, "#fff7e6", ORANGE, 1.8, 12)
    s += text(680, 116, "Якби 1 ГОм (майже ізолятор)", 12.5, ORANGE, "middle", "bold")
    s += text(680, 140, "стала часу τ = R·C завелика", 10.5, INK, "middle")
    s += text(680, 160, "статика стікає надто повільно", 11, ORANGE, "middle", "bold")
    s += text(680, 182, "заряд встигає накопичитись і стрельнути", 10.5, ORANGE, "middle")
    s += text(680, 202, "потрібен НЕзавеликий опір!", 10, INK, "middle", style="italic")

    # компроміс посередині знизу
    s += arrow(240, 222, 430, 270, RED, 2.2)
    s += arrow(680, 222, 490, 270, ORANGE, 2.2)
    s += rect(330, 274, 260, 96, "#eef7f0", GREEN, 2.0, 12)
    s += text(460, 300, "1 МОм — золота середина", 13, GREEN, "middle", "bold")
    s += text(460, 324, "дотик до 230 В → I ≈ 0.23 мА (безпечно)", 10.5, INK, "middle")
    s += text(460, 344, "τ = 1 МОм · 100 пФ = 0.1 мс (стікає швидко)", 10.5, INK, "middle")
    s += text(460, 362, "часто це 1 МОм у браслеті + ще 1 МОм у маті", 9.5, GREY, "middle")

    s += text(W / 2, 396, "Той самий резистор 1 МОм виконує дві ролі: повільно знімає заряд і рятує людину при випадковому дотику до напруги.",
              11, INK, "middle", "bold")
    save("fig-1-10-6-2-one-megohm.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.7 — Пакування й транспортування.  Рис. 1.10.7.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.7.1 — розсіювальний проти екранувального пакета ─────────────────
def fig_bags():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Три класи пакувань: антистатичне, розсіювальне, екранувальне",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "що від чого захищає — залежить від того, чи проводить плівка й чи має вона суцільний екран",
              11.5, GREY, "middle", style="italic")

    cards = [
        (50, "Рожевий «антистатик»", "antistatic", "#f9d6e0", RED,
         ["не електризується сам", "(низька трибоелектрика)", "НЕ екранує від поля!", "для НЕчутливого / вторинне"]),
        (340, "Чорний розсіювальний", "dissipative", "#d7d7d7", INK,
         ["проводить помалу по поверхні", "вирівнює заряд на собі", "екран слабкий", "лотки, піна, мати"]),
        (640, "Сріблястий екранувальний", "shield", "#cfe0ea", BLUE,
         ["метал. шар = клітка Фарадея", "не пускає поле всередину", "+ розсіювальний шар", "ОСНОВНИЙ для ІМС"]),
    ]
    for x0, title, kind, fill, col, notes in cards:
        s += rect(x0, 84, 250, 250, "#fcfcfc", col, 1.8, 12)
        s += text(x0 + 125, 108, title, 12.5, col, "middle", "bold")
        # пакет із платою
        s += rect(x0 + 55, 130, 140, 90, fill, col, 2, 6)
        s += rect(x0 + 90, 158, 70, 34, "#244", GREEN, 1.6, 3)
        s += text(x0 + 125, 180, "ІМС", 9, "#dff0e6", "middle", "bold")
        # зовнішня загроза: іскра/поле ззовні
        s += _spark(x0 + 20, 175, x0 + 53, 175, ORANGE, 2.2, jag=4, seed=5)
        if kind == "shield":
            # металевий шар блокує
            s += rect(x0 + 53, 132, 4, 86, BLUE, BLUE, 0)
            s += text(x0 + 30, 240, "поле НЕ проходить ✓", 9.5, GREEN, "start", "bold")
        else:
            # поле проходить до плати
            s += _spark(x0 + 57, 175, x0 + 90, 175, ORANGE, 1.8, jag=3, seed=6)
            s += text(x0 + 30, 240, "поле проходить ✗", 9.5, RED, "start", "bold")
        # нотатки
        for i, n in enumerate(notes):
            mark = "•"
            c = INK
            if "НЕ" in n or "✗" in n:
                c = RED
            if "ОСНОВНИЙ" in n or "Фарадея" in n:
                c = GREEN
            s += text(x0 + 18, 260 + i * 16, f"{mark} {n}", 9.2, c, "start",
                      "bold" if c != INK else "normal")

    s += text(W / 2, 360, "Ключова пастка: рожевий «антистатик» лише не іскрить сам — він НЕ є екраном. Чутливу ІМС возять у сріблястому екранувальному пакеті.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 384, "Екранувальний пакет працює, лише поки закритий: відкритий — це вже не клітка Фарадея (§1.1.8).",
              10.5, GREY, "middle")
    s += text(W / 2, 414, "Транспортна тара (тубуси, котушки, лотки) — з розсіювального пластику, щоб виводи не електризувались під час тряски.",
              10.5, GREY, "middle")
    save("fig-1-10-7-1-bags.svg", s)


# ── Рис. 1.10.7.2 — тара для виводів: тубус, котушка стрічки, лоток ────────────
def fig_carriers():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 30, "Транспортна тара: щоб виводи не терлися й не електризувались",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "форма тари тримає компоненти нерухомо; матеріал — розсіювальний, щоб тертя не родило заряд",
              11.5, GREY, "middle", style="italic")

    # тубус для DIP
    s += text(170, 92, "Тубус (туба) для DIP", 12, INK, "middle", "bold")
    s += rect(60, 110, 220, 36, "#d7d7d7", INK, 2, 6)
    for k in range(5):
        s += rect(74 + k * 40, 116, 26, 24, "#333", INK, 1.4, 2)
    s += text(170, 168, "мікросхеми лежать у ряд, не торкаючись", 9.5, GREY, "middle")

    # котушка стрічки (tape & reel)
    s += text(490, 92, "Стрічка на котушці (tape & reel)", 12, INK, "middle", "bold")
    s += circle(420, 150, 44, "#fafafa", INK, 2)
    s += circle(420, 150, 12, "#fff", INK, 1.6)
    # стрічка з кишеньками
    s += rect(470, 138, 200, 24, "#d7d7d7", INK, 2)
    for k in range(7):
        s += rect(478 + k * 26, 142, 14, 16, "#333", INK, 1, 2)
    for k in range(7):
        s += circle(482 + k * 26, 150, 1.6, "#fff", INK, 0.8)
    s += text(560, 188, "SMD у кишеньках, накрито плівкою", 9.5, GREY, "middle")

    # лоток (tray / JEDEC)
    s += text(780, 92, "Лоток (tray)", 12, INK, "middle", "bold")
    s += rect(700, 110, 160, 90, "#3f6f5f", INK, 2, 6)
    for r in range(2):
        for c in range(3):
            s += rect(716 + c * 48, 124 + r * 40, 36, 28, "#244", GREEN, 1.4, 3)
    s += text(780, 220, "для QFP/BGA — кожен у комірці", 9.5, GREY, "middle")

    s += rect(120, 250, 680, 80, "#eef7f0", GREEN, 1.6, 10)
    s += text(460, 276, "Спільна ідея всієї тари", 12.5, GREEN, "middle", "bold")
    s += text(460, 300, "1) механічно: компонент не совається, виводи не труться один об одного й об стінки;",
              10.5, INK, "middle")
    s += text(460, 320, "2) електрично: матеріал розсіювальний (не діелектрик), тож тертя під час перевезення не накопичує заряд.",
              10.5, INK, "middle")
    save("fig-1-10-7-2-carriers.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.10.8 — Вологість і матеріали.  Рис. 1.10.8.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.10.8.1 — волога плівка на поверхні стікає заряд ────────────────────
def fig_humidity_film():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 30, "Чому волога рятує: тонка плівка води робить поверхні трохи провідними",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "за високої вологості на всьому осідає мікроплівка води з іонами — заряд стікає сам, не встигаючи накопичитись",
              11.5, GREY, "middle", style="italic")

    # ліворуч: суха поверхня — заряд застряг
    s += rect(80, 110, 320, 220, "#fffaf0", ORANGE, 1.8, 12)
    s += text(240, 134, "Сухе повітря (RH ≈ 20%)", 13, ORANGE, "middle", "bold")
    s += rect(120, 250, 240, 22, "#e0d6c2", INK, 1.8)
    s += text(240, 266, "пластикова поверхня", 9.5, INK, "middle")
    for k in range(7):
        s += plus(140 + k * 35, 238, 6)
    s += text(240, 210, "заряд сидить на місці —", 10.5, ORANGE, "middle", "bold")
    s += text(240, 226, "стікати нема куди", 10.5, ORANGE, "middle")
    s += text(240, 300, "напруга росте до кіловольтів", 10, RED, "middle", "bold")

    # праворуч: волога поверхня — плівка стікає заряд
    s += rect(520, 110, 320, 220, "#eef7f6", GREEN, 1.8, 12)
    s += text(680, 134, "Вологе повітря (RH ≈ 60%)", 13, GREEN, "middle", "bold")
    s += rect(560, 250, 240, 22, "#e0d6c2", INK, 1.8)
    # плівка води
    s += rect(560, 244, 240, 7, "#bfe0ea", BLUE, 1.2)
    s += text(680, 266, "пластик + плівка води з іонами", 9.5, INK, "middle")
    # заряд розтікається і стікає вбік
    for k in range(3):
        s += plus(600 + k * 30, 238, 5)
    s += arrow(660, 247, 790, 247, BLUE, 1.8)
    s += text(805, 251, "стік", 9.5, BLUE, "start", "bold")
    s += text(680, 210, "плівка проводить помалу —", 10.5, GREEN, "middle", "bold")
    s += text(680, 226, "заряд розтікається й іде", 10.5, GREEN, "middle")
    s += text(680, 300, "напруга лишається низькою", 10, GREEN, "middle", "bold")

    s += text(W / 2, 372, "Волога не «нейтралізує» заряд хімічно — вона дає йому повільний шлях стекти (поверхнева провідність зростає).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 394, "Тому взимку в опаленому приміщенні (сухе повітря) статики найбільше — повертаємось до цього на графіку нижче.",
              10.5, GREY, "middle")
    save("fig-1-10-8-1-humidity-film.svg", s)


# ── Рис. 1.10.8.2 — RH проти типової напруги статики (хода по килиму тощо) ─────
def fig_humidity_chart():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Вологість вирішує: та сама дія дає кіловольти або вольти",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "типові напруги статики від тих самих рухів — при низькій і високій відносній вологості (RH)",
              11.5, GREY, "middle", style="italic")

    ax, ay, aw, ah = 110, 330, 700, 240
    s += arrow(ax, ay, ax + aw + 12, ay, INK, 2.0)
    s += arrow(ax, ay, ax, ay - ah - 12, INK, 2.0)
    s += text(ax + aw + 6, ay + 22, "RH, %", 11, INK, "middle", "bold")
    s += text(ax - 6, ay - ah - 18, "напруга статики, кВ (лог-натяк)", 11, INK, "start", "bold")

    # вісь X: 10..80 %
    for rh in range(10, 81, 10):
        x = ax + aw * (rh - 10) / 70.0
        s += line(x, ay, x, ay + 6, INK, 1.3)
        s += text(x, ay + 22, str(rh), 10, INK, "middle")
    # вісь Y: 0..20 кВ
    for kv in range(0, 21, 4):
        y = ay - ah * kv / 20.0
        s += line(ax - 6, y, ax, y, INK, 1.3)
        s += text(ax - 10, y + 4, str(kv), 10, INK, "end")

    # три сценарії: спадні криві (V велике при сухому, мале при вологому)
    scen = [("хода по килиму", 35.0, RED),
            ("вставання з крісла", 18.0, ORANGE),
            ("хода по антистат. підлозі", 3.0, GREEN)]
    for lab, v10, col in scen:
        pts = []
        for i in range(71):
            rh = 10 + i
            # експоненційний спад із RH
            v = v10 * math.exp(-(rh - 10) / 26.0)
            x = ax + aw * (rh - 10) / 70.0
            y = ay - ah * min(v, 20.0) / 20.0
            pts.append((x, y))
        s += polyline(pts, col, 2.8)
        s += text(pts[2][0] + 6, pts[2][1] - 6, lab, 10, col, "start", "bold")

    # зони
    s += rect(ax, ay - ah, aw * (40 - 10) / 70.0, ah, "#fdecea", "none", 0)
    s += text(ax + aw * 0.12, ay - ah - 2, "сухо: НЕБЕЗПЕЧНО", 10.5, RED, "middle", "bold")
    s += rect(ax + aw * (50 - 10) / 70.0, ay - ah, aw * (80 - 50) / 70.0, ah, "#eef7f0", "none", 0)
    s += text(ax + aw * 0.78, ay - ah - 2, "волого: легше", 10.5, GREEN, "middle", "bold")

    s += text(W / 2, 392, "Практичний орієнтир: тримати RH у майстерні ~40–60%. Це не скасовує браслет і мат — лише прибирає найгірші піки.",
              11, INK, "middle", "bold")
    s += text(W / 2, 414, "Числа орієнтовні (залежать від матеріалів і взуття) — важлива сама форма: суше = у рази більша напруга.",
              10, GREY, "middle")
    save("fig-1-10-8-2-humidity-chart.svg", s)


# ── Рис. 1.10.8.3 — керування статикою в середовищі: матеріали столу/одягу ────
def fig_materials():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 30, "Керування статикою в середовищі: підлога, одяг, інструмент",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "мета — прибрати діелектрики з шляху руху людини й замінити їх розсіювальними матеріалами",
              11.5, GREY, "middle", style="italic")

    cols = [
        (60, "ПІДЛОГА / ВЗУТТЯ", GREEN,
         [("✓ антистатична плитка", GREEN),
          ("✓ розсіювальне взуття / п'яткові ремінці", GREEN),
          ("✗ синтетичний килим", RED),
          ("✗ підошва-ізолятор", RED)]),
        (350, "ОДЯГ", GREEN,
         [("✓ бавовна, ESD-халат", GREEN),
          ("✓ халат з'єднаний із землею", GREEN),
          ("✗ вовняний / флісовий светр", RED),
          ("✗ синтетика, що іскрить", RED)]),
        (640, "ІНСТРУМЕНТ", GREEN,
         [("✓ розсіювальні ручки / пінцети", GREEN),
          ("✓ заземлене жало паяльника", GREEN),
          ("✗ звичайний пластик корпусів", RED),
          ("✗ поролон/пінопласт (тертя)", RED)]),
    ]
    for x0, title, col, items in cols:
        s += rect(x0, 84, 250, 240, "#fcfcfc", FAINT, 1.6, 12)
        s += text(x0 + 125, 110, title, 12.5, INK, "middle", "bold")
        for i, (txt, c) in enumerate(items):
            s += text(x0 + 18, 142 + i * 40, txt, 10.5, c, "start", "bold")
            s += line(x0 + 18, 152 + i * 40, x0 + 232, 152 + i * 40, FAINT, 1)

    s += rect(120, 336, 700, 30, "#eef2fb", BLUE, 1.4, 8)
    s += text(460, 356, "Принцип один (§1.1.1, §1.10.1): прибрати пари «далеко в трибоелектричному ряду» зі шляху руху — і нічому буде електризуватись.",
              10.3, INK, "middle", "bold")
    save("fig-1-10-8-3-materials.svg", s)


# ════════════════════════════════════════════════════════════════════════════
def main():
    # 1.10.1
    fig_contact_charging()
    fig_everyday_sources()
    fig_triboelectric_series()
    # 1.10.2
    fig_body_capacitor()
    fig_voltage_ladder()
    # 1.10.3
    fig_avalanche()
    fig_breakdown_gap()
    fig_point_corona()
    # 1.10.4
    fig_cloud_charge()
    fig_leader_stroke()
    # 1.10.5
    fig_thin_oxide()
    fig_latent_damage()
    # 1.10.6
    fig_esd_bench()
    fig_one_megohm()
    # 1.10.7
    fig_bags()
    fig_carriers()
    # 1.10.8
    fig_humidity_film()
    fig_humidity_chart()
    fig_materials()
    print("done")


if __name__ == "__main__":
    main()
