# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 2 — «Напруга, струм і провідність» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з Розділу 1 (за §9 — кожен розділ самодостатній).
Нумерація: історія до розділу — секція 0 (Рис. 2.0.N); теми — Рис. 2.M.k.
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
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _zig(x, y, steps, sx, sy):
    """Зигзаг від (x,y): список (dx,dy) кроків, масштаб sx,sy."""
    pts = [(x, y)]
    for dx, dy in steps:
        x += dx * sx
        y += dy * sy
        pts.append((x, y))
    return pts


# ── Рис. 2.0.1 — закон Ома: відкинутий, потім визнаний ───────────────────────
def fig_ohm_story():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 36, "Закон Ома: спершу відкинутий, згодом — наріжний камінь", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "проста залежність, яку німецька академія зустріла зневагою", 12.5, GREY, "middle", style="italic")
    # сам закон
    s += rect(80, 86, 300, 120, "#f4f7f4", GREEN, 1.8, 12)
    s += text(230, 132, "I = V / R", 30, INK, "middle", "bold")
    s += text(230, 166, "більша напруга → більший струм", 12, GREY, "middle")
    s += text(230, 186, "більший опір → менший струм", 12, GREY, "middle")
    # доля
    s += rect(430, 86, 310, 120, "#fafafa", GREY, 1.6, 12)
    s += text(585, 112, "Чому відкинули?", 13.5, INK, "middle", "bold")
    s += text(446, 138, "• панувала «натурфілософія»:", 11.5, INK, "start")
    s += text(446, 158, "  істину шукали в умогляді,", 11.5, INK, "start")
    s += text(446, 178, "  а не в дослідах і формулах", 11.5, INK, "start")
    s += text(446, 198, "• Ом утратив посаду вчителя", 11.5, RED, "start", "bold")
    # таймлайн визнання
    ty = 270
    s += line(110, ty, 710, ty, GREY, 2.5)
    nodes = [("1827", "публікує закон —", "зневага", RED),
             ("1833", "роки забуття,", "бідність", GREY),
             ("1841", "медаль Коплі —", "визнання!", GREEN),
             ("1881", "одиниця «ом» (Ω)", "у його честь", INK)]
    for i, (yr, a, b, col) in enumerate(nodes):
        x = 150 + i * 187
        s += circle(x, ty, 7, "#fff", col, 2.6)
        s += text(x, ty - 16, yr, 13, col, "middle", "bold")
        s += text(x, ty + 26, a, 11, INK, "middle")
        s += text(x, ty + 42, b, 11, col, "middle", "bold")
    s += text(W / 2, H - 12, "Урок: дослід і математика перемогли умогляд — але часом на це йдуть десятиліття.",
              12, GREY, "middle", style="italic")
    save("fig-2-0-1-ohm-story.svg", s)


# ── Рис. 2.0.2 — катодний промінь Томсона: відкриття електрона ────────────────
def fig_thomson_crt():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 36, "Промінь Томсона (1897): носій струму — електрон", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "катодні промені відхиляються до «+» пластини → вони ВІД'ЄМНІ", 12.5, GREY, "middle", style="italic")
    # трубка
    s += rect(70, 150, 680, 150, "none", GREY, 2, 40)
    # катод
    s += line(95, 185, 95, 265, BLUE, 5)
    s += text(95, 320, "катод (−)", 12, BLUE, "middle", "bold")
    s += text(150, 320, "анод", 11, INK, "middle")
    s += line(165, 200, 165, 250, INK, 2)
    s += circle(165, 225, 14, "none", INK, 1.6)
    # пластини відхилення
    s += line(360, 168, 470, 168, RED, 4)
    s += text(415, 160, "+ пластина", 11.5, RED, "middle", "bold")
    s += line(360, 282, 470, 282, BLUE, 4)
    s += text(415, 300, "− пластина", 11.5, BLUE, "middle", "bold")
    # промінь: прямий, тоді вигин угору (до +)
    pts = [(180, 225), (360, 225)]
    for i in range(1, 30):
        x = 360 + i * 12
        y = 225 - (i * 12) ** 2 * 0.0016
        if x > 745:
            break
        pts.append((x, y))
    s += polyline(pts, GREEN, 2.8)
    s += text(300, 214, "катодний промінь", 11, GREEN, "middle", "bold")
    # екран
    s += line(748, 150, 748, 300, "#cdaa3a", 6)
    sx, sy = pts[-1]
    s += circle(sx + 4, sy, 6, "#9acd3a", "#6a9a1a", 1.6)
    s += text(770, sy, "пляма", 10.5, INK, "start")
    s += rect(70, 330, W - 140, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 352, "Частинки ~2000× легші за атом водню — «атом електрики».", 12.5, INK, "middle", "bold")
    s += text(W / 2, 370, "Нарешті стало відомо, ЩО саме тече в дроті. І воно від'ємне — тож рух проти умовного струму (Розд.1).",
              11.5, GREY, "middle", style="italic")
    save("fig-2-0-2-thomson-crt.svg", s)


# ── Рис. 2.0.3 — модель Друде: електронний газ і дрейф ───────────────────────
def fig_drude_model():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 34, "Модель Друде (1900): електронний «газ» серед іонів", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "вільні електрони шалено снують і б'ються об іони решітки (це опір)", 12.5, GREY, "middle", style="italic")

    def lattice(x0, y0):
        out = ""
        for r in range(4):
            for c in range(5):
                out += circle(x0 + c * 66, y0 + r * 56, 13, "#fde0d6", COPPER, 1.8)
                out += text(x0 + c * 66, y0 + r * 56 + 4, "+", 12, COPPER, "middle", "bold")
        return out

    # панель A — без поля
    s += text(220, 96, "без поля: хаос, дрейфу нема", 12.5, INK, "middle", "bold")
    s += lattice(70, 130)
    pa = _zig(95, 150, [(2, 1), (1.5, -2), (2, 1.5), (-1, 2), (2.5, -1), (1, 2), (2, -1.5)], 22, 20)
    s += polyline(pa, BLUE, 2)
    s += minus(pa[-1][0], pa[-1][1], 7, BLUE, 1.8)
    pa2 = _zig(120, 290, [(1.5, -1.5), (2, 1), (-1, -2), (2.5, 1.5), (1, -2)], 22, 20)
    s += polyline(pa2, BLUE, 2)
    s += minus(pa2[-1][0], pa2[-1][1], 7, BLUE, 1.8)

    # панель B — з полем
    s += text(620, 96, "з полем: той самий хаос + ДРЕЙФ", 12.5, INK, "middle", "bold")
    s += lattice(470, 130)
    # поле E праворуч; електрони дрейфують ліворуч
    for yy in (118, 322):
        s += arrow(486, yy, 770, yy, GREEN, 1.6)
    s += text(628, 110, "E →", 12, GREEN, "middle", "bold")
    pb = _zig(760, 150, [(-2, 1), (-1.5, -2), (-2, 1.5), (-2.5, 2), (-2, -1), (-2.5, 1.5), (-2, -1.5)], 22, 20)
    s += polyline(pb, BLUE, 2.2)
    s += minus(pb[-1][0], pb[-1][1], 7, BLUE, 1.8)
    s += arrow(745, 360, 520, 360, BLUE, 2.6)
    s += text(632, 350, "повільний дрейф електронів (−) ←", 11, BLUE, "middle", "bold")
    s += text(632, 384, "умовний струм → праворуч", 11, RED, "middle", "bold")
    s += text(W / 2, H - 8, "Зіткнення з іонами гальмують дрейф — звідси опір; нагрів решітки — звідси тепло.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-0-3-drude-model.svg", s)


# ── Рис. 2.1.1 — означення струму: заряд через переріз за секунду ─────────────
def fig21_current_definition():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Струм — це заряд, що проходить переріз за секунду", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "лічимо кулони, що перетинають уявну площину впоперек дроту, за одиницю часу", 12, GREY, "middle", style="italic")
    # дріт
    wy, x0, x1 = 200, 110, 600
    s += line(x0, wy - 26, x1, wy - 26, COPPER, 3)
    s += line(x0, wy + 26, x1, wy + 26, COPPER, 3)
    s += rect(x0, wy - 26, x1 - x0, 52, "#fdf3ec", "none", 0)
    # переріз
    s += line(355, wy - 44, 355, wy + 44, INK, 2, "6 4")
    s += text(355, wy - 52, "переріз", 12, INK, "middle", "bold")
    # заряди, що рухаються (умовно +)
    for cx in (180, 250, 320, 420, 490):
        s += circle(cx, wy, 9, "#fdf4f4", RED, 2)
        s += plus(cx, wy, 5, RED, 1.6)
    s += arrow(150, wy + 70, 560, wy + 70, RED, 2.6)
    s += text(355, wy + 90, "умовний струм  I  →", 13, RED, "middle", "bold")
    s += arrow(560, wy - 70, 150, wy - 70, BLUE, 1.8)
    s += text(355, wy - 76, "(електрони ←)", 11.5, BLUE, "middle")
    # формула
    s += rect(630, 150, 160, 110, "#f4f7f4", GREEN, 1.8, 12)
    s += text(710, 188, "I = ΔQ / Δt", 17, INK, "middle", "bold")
    s += text(710, 218, "кулони за", 12, GREY, "middle")
    s += text(710, 236, "секунду", 12, GREY, "middle")
    save("fig-2-1-1-current-definition.svg", s)


# ── Рис. 2.1.2 — ампер: 1 А = 1 Кл/с ─────────────────────────────────────────
def fig21_ampere():
    W, H = 800, 330
    s = header(W, H)
    s += text(W / 2, 36, "Одиниця струму — ампер: 1 А = 1 кулон за секунду", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "якщо переріз щосекунди перетинає 1 Кл заряду — це струм 1 ампер", 12, GREY, "middle", style="italic")
    # годинниковий тік
    s += text(200, 120, "1 Кл", 16, RED, "middle", "bold")
    s += rect(160, 130, 80, 40, "#fdf4f4", RED, 2, 8)
    s += plus(200, 150, 9, RED)
    s += arrow(250, 150, 360, 150, INK, 2.6)
    s += text(305, 136, "за 1 с", 12, INK, "middle", "bold")
    s += line(380, 110, 380, 200, INK, 2, "6 4")
    s += text(380, 100, "переріз", 11, INK, "middle")
    # рівняння
    s += rect(450, 110, 300, 90, "#f4f7f4", GREEN, 1.8, 12)
    s += text(600, 150, "1 А = 1 Кл/с", 24, INK, "middle", "bold")
    s += text(600, 182, "одиниця названа на честь Ампера", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 250, "Звідси й заряд: Q = I · t. Струм 2 А за 1 хв переносить 2 × 60 = 120 Кл.",
              13, INK, "middle", "bold")
    s += text(W / 2, 280, "А «мА·год» на батареї (Розд.1) — це теж заряд: струм × час.", 12, GREY, "middle", style="italic")
    save("fig-2-1-2-ampere.svg", s)


# ── Рис. 2.1.3 — водяна аналогія струму ──────────────────────────────────────
def fig21_water_flow():
    W, H = 800, 330
    s = header(W, H)
    s += text(W / 2, 36, "Водяна аналогія: струм — це витрата потоку", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "скільки води (заряду) проходить через переріз за секунду", 12, GREY, "middle", style="italic")
    # труба
    py, x0, x1 = 170, 110, 620
    s += line(x0, py - 24, x1, py - 24, "#5b87a6", 3)
    s += line(x0, py + 24, x1, py + 24, "#5b87a6", 3)
    s += rect(x0, py - 24, x1 - x0, 48, "#dceaf2", "none", 0)
    for dx in (160, 240, 320, 420, 520):
        s += arrow(dx, py, dx + 40, py, "#2b7", 2.4)
    s += line(370, py - 40, 370, py + 40, INK, 2, "6 4")
    s += text(370, py - 48, "переріз", 11.5, INK, "middle", "bold")
    s += text(365, py + 70, "витрата (л/с)  ↔  струм (Кл/с)", 14, INK, "middle", "bold")
    s += rect(650, 120, 130, 100, "#f4f7f4", GREEN, 1.6, 10)
    s += text(715, 146, "з §1.5:", 12, INK, "middle", "bold")
    s += text(715, 170, "висота → напруга", 11.5, INK, "middle")
    s += text(715, 192, "потік → струм", 11.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 16, "Велика напруга при тонкій цівці й мала при потужному потоці — різні речі.",
              12, GREY, "middle", style="italic")
    save("fig-2-1-3-water-flow.svg", s)


# ── Рис. 2.1.4 — драбина типових струмів ─────────────────────────────────────
def fig21_magnitudes():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 36, "Драбина типових струмів", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "від мікроампер давачів до кілоампер блискавки", 12, GREY, "middle", style="italic")
    x = 300
    s += line(x, 92, x, 400, INK, 2.5)
    items = [
        ("~ нА–мкА", "витоки, входи мікросхем", BLUE),
        ("~ 1–20 мА", "світлодіод, логічний вихід", INK),
        ("~ 0.1–2 А", "Wi-Fi-передача, серво", INK),
        ("~ 1–10 А", "двигун, потужне живлення", INK),
        ("~ 30 кА", "розряд блискавки", RED),
    ]
    n = len(items)
    for i, (v, what, col) in enumerate(items):
        y = 110 + (400 - 110) * i / (n - 1)
        s += line(x - 7, y, x + 7, y, INK, 2)
        s += text(x - 16, y + 5, v, 14, col, "end", "bold")
        s += text(x + 18, y + 5, what, 13, col, "start", "bold" if col == RED else "normal")
    s += text(x - 16, 96, "менше", 10.5, GREY, "end", style="italic")
    s += text(x - 16, 418, "більше Кл/с", 10.5, GREY, "end", style="italic")
    save("fig-2-1-4-magnitudes.svg", s)


# ── Рис. 2.1.5 — амперметр вмикають послідовно ───────────────────────────────
def fig21_ammeter_series():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 36, "Як виміряти струм: амперметр — ПОСЛІДОВНО", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "струм має протекти крізь прилад, тож його вмикають у розрив кола", 12, GREY, "middle", style="italic")
    L, R, T, B = 180, 600, 110, 290
    # батарея ліворуч
    s += line(L, T, L, B, INK, 2.4)
    s += line(L - 15, 185, L + 15, 185, RED, 3)
    s += line(L - 9, 202, L + 9, 202, BLUE, 4)
    s += text(L - 30, 190, "+", 14, RED, "middle", "bold")
    s += text(L - 30, 214, "−", 14, BLUE, "middle", "bold")
    # верх з амперметром у розриві
    s += line(L, T, 330, T, INK, 2.4)
    s += circle(370, T, 22, "#eef5ff", INK, 2.4)
    s += text(370, T + 6, "A", 17, INK, "middle", "bold")
    s += line(392, T, R, T, INK, 2.4)
    s += text(370, T - 32, "амперметр", 12, INK, "middle", "bold")
    # навантаження праворуч
    s += rect(R - 18, 165, 36, 60, "#fff7ef", "#c89b5a", 2.2, 5)
    s += text(R + 36, 198, "наван-", 11, INK, "middle")
    s += text(R + 36, 212, "таження", 11, INK, "middle")
    s += line(R, T, R, 165, INK, 2.4)
    s += line(R, 225, R, B, INK, 2.4)
    s += line(L, B, R, B, INK, 2.4)
    # струм
    for px in (250, 470):
        s += arrow(px, T, px + 24, T, RED, 2.2)
    s += text(290, B + 26, "весь струм кола тече крізь амперметр", 12, RED, "middle", "bold")
    # порівняння
    s += rect(120, 320, W - 240, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 343, "Порівняйте: вольтметр вмикають ПАРАЛЕЛЬНО (між двома точками, §1.4),",
              12, INK, "middle", "bold")
    s += text(W / 2, 360, "а амперметр — послідовно, бо міряє те, що крізь нього протікає.", 11.5, GREY, "middle", style="italic")
    save("fig-2-1-5-ammeter-series.svg", s)


# ── Рис. 2.2.1 — умовний струм проти руху електронів ─────────────────────────
def fig22_two_directions():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Два напрямки одного струму", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "умовний струм іде + → −, а електрони — навпаки; це ОДИН і той самий струм", 12, GREY, "middle", style="italic")
    L, R, T, B = 170, 620, 130, 290
    # батарея
    s += line(L, T, L, B, INK, 2.4)
    s += line(L - 16, 195, L + 16, 195, RED, 3)
    s += line(L - 10, 213, L + 10, 213, BLUE, 4)
    s += text(L - 34, 200, "+", 15, RED, "middle", "bold")
    s += text(L - 34, 224, "−", 15, BLUE, "middle", "bold")
    # навантаження
    s += rect(R - 20, 175, 40, 60, "#fff7ef", "#c89b5a", 2.2, 5)
    s += text(R + 40, 208, "наван-", 11, INK, "middle")
    s += text(R + 40, 222, "таження", 11, INK, "middle")
    # дроти
    s += line(L, T, R, T, INK, 2.4)
    s += line(R, T, R, 175, INK, 2.4)
    s += line(R, 235, R, B, INK, 2.4)
    s += line(L, B, R, B, INK, 2.4)
    # умовний струм (червоний, за годинниковою з +)
    s += arrow(300, T, 360, T, RED, 2.8)
    s += arrow(R, 250, R, 280, RED, 2.8)
    s += arrow(460, B, 400, B, RED, 2.8)
    s += text(395, T - 12, "умовний струм  I :  + → −", 13, RED, "middle", "bold")
    # електрони (сині, навпаки)
    for px in (250, 410):
        s += minus(px, T, 7, BLUE, 1.8)
    s += arrow(360, T + 22, 300, T + 22, BLUE, 2)
    s += text(395, B + 26, "електрони  e⁻ :  − → +  (у дротах навпаки)", 12.5, BLUE, "middle", "bold")
    s += text(W / 2, H - 16, "Усередині джерела «насос» жене заряд від − до +, у зовнішньому колі — навпаки.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-2-1-two-directions.svg", s)


# ── Рис. 2.2.2 — еквівалентність: − ліворуч = + праворуч ─────────────────────
def fig22_equivalence():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Чому знак носія не важливий", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "від'ємний заряд ліворуч і додатний праворуч дають ОДНАКОВИЙ струм", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 36, FAINT, 1.5)

    def panel(cx, sign, movedir, label):
        out = line(cx - 130, 200, cx + 130, 200, COPPER, 3)
        out += line(cx - 130, 240, cx + 130, 240, COPPER, 3)
        out += rect(cx - 130, 200, 260, 40, "#fdf3ec", "none", 0)
        out += line(cx, 184, cx, 256, INK, 2, "5 4")
        out += text(cx, 176, "переріз", 10.5, INK, "middle")
        col = RED if sign == "+" else BLUE
        bx = cx - 40 if movedir > 0 else cx + 40
        out += circle(bx, 220, 13, "#fdf4f4" if sign == "+" else "#f3f5fd", col, 2.2)
        out += (plus(bx, 220, 7, col) if sign == "+" else minus(bx, 220, 7, col))
        ex = bx + movedir * 60
        out += arrow(bx + movedir * 16, 220, ex, 220, col, 2.4)
        out += text(cx, 290, label, 12.5, INK, "middle", "bold")
        out += text(cx, 312, "→ струм праворуч", 12.5, GREEN, "middle", "bold")
        return out

    s += panel(210, "-", -1, "− заряд рухається ЛІВОРУЧ")
    s += panel(610, "+", +1, "+ заряд рухається ПРАВОРУЧ")
    s += text(W / 2, 110, "однаковий результат", 13, INK, "middle", "bold")
    save("fig-2-2-2-equivalence.svg", s)


# ── Рис. 2.2.3 — умовний струм на схемі ──────────────────────────────────────
def fig22_schematic():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Умовний струм на схемі: з + крізь коло у −", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "стрілка діода / світлодіода завжди вказує напрямок умовного струму", 12, GREY, "middle", style="italic")
    L, R, T, B = 150, 650, 120, 300
    # батарея-елемент
    s += line(L, T, L, 185, INK, 2.4)
    s += line(L, 235, L, B, INK, 2.4)
    s += line(L - 20, 185, L + 20, 185, INK, 3)        # довга (+)
    s += line(L - 11, 200, L + 11, 200, INK, 5)        # коротка (−)
    s += line(L - 20, 205, L + 20, 205, INK, 3)
    s += line(L - 11, 220, L + 11, 220, INK, 5)
    s += text(L - 32, 180, "+", 14, RED, "middle", "bold")
    s += text(L - 32, 230, "−", 14, BLUE, "middle", "bold")
    # верхній дріт + резистор
    s += line(L, T, 300, T, INK, 2.4)
    s += rect(300, T - 12, 90, 24, "#fff", INK, 2, 3)
    s += text(345, T - 18, "R", 13, INK, "middle", "bold", "italic")
    s += line(390, T, R, T, INK, 2.4)
    # правий бік: світлодіод (трикутник + катод)
    s += line(R, T, R, 165, INK, 2.4)
    s += f'<path d="M {R-16},170 L {R+16},170 L {R},200 Z" fill="#fdeeee" stroke="{RED}" stroke-width="2"/>\n'
    s += line(R - 16, 200, R + 16, 200, RED, 3)
    s += arrow(R + 22, 176, R + 36, 166, RED, 1.6)
    s += arrow(R + 26, 184, R + 40, 174, RED, 1.6)
    s += text(R + 44, 192, "LED", 11.5, RED, "start", "bold")
    s += line(R, 200, R, B, INK, 2.4)
    # нижній дріт
    s += line(L, B, R, B, INK, 2.4)
    # умовний струм (за годинниковою)
    s += arrow(210, T, 250, T, RED, 2.6)
    s += arrow(R, 250, R, 285, RED, 2.6)
    s += arrow(440, B, 400, B, RED, 2.6)
    s += text(230, T - 22, "I", 14, RED, "middle", "bold", "italic")
    s += text(W / 2, H - 18, "Струм виходить з «+», проходить R і LED (за стрілкою), вертається в «−».",
              12, INK, "middle", "bold")
    save("fig-2-2-3-schematic.svg", s)


# ── Рис. 2.2.4 — дірки в напівпровіднику ─────────────────────────────────────
def fig22_holes():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Бонус: у напівпровідниках конвенція буквально правильна", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "там струм несуть «дірки» — вони рухаються як ДОДАТНІ заряди, точно за умовним струмом", 12, GREY, "middle", style="italic")
    # ряд атомів з однією діркою
    y = 180
    xs = [150, 230, 310, 390, 470, 550, 630]
    holei = 3
    for i, x in enumerate(xs):
        s += circle(x, y, 22, "#eef2f5", "#9aa7b0", 1.8)
        if i == holei:
            s += circle(x, y, 9, "none", RED, 2, )
            s += plus(x, y, 5, RED, 1.6)
            s += text(x, y - 34, "дірка (+)", 11.5, RED, "middle", "bold")
        else:
            s += minus(x, y, 8, BLUE, 1.8)
    s += text(390, y + 50, "електрон зліва перестрибує у дірку →", 12, INK, "middle")
    s += arrow(xs[holei] - 30, y + 30, xs[holei] - 6, y + 30, BLUE, 2)
    s += text(390, y + 80, "...і дірка ніби зсувається ПРАВОРУЧ, як додатний заряд", 12, RED, "middle", "bold")
    s += arrow(xs[holei] + 6, y - 50, xs[holei] + 70, y - 50, RED, 2.4)
    s += text(xs[holei] + 38, y - 58, "рух дірки = умовний струм", 11, RED, "middle", "bold")
    s += rect(150, 320, W - 300, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 343, "Тобто Франклін «угадав» — для додатних носіїв (дірок) струм реально йде в бік умовного.",
              12, INK, "middle", "bold")
    s += text(W / 2, 360, "Докладно про дірки й напівпровідники — Розділ 10.", 11, GREY, "middle", style="italic")
    save("fig-2-2-4-holes.svg", s)


# ── Рис. 2.3.1 — електронне «море» в металі ──────────────────────────────────
def fig23_electron_sea():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Метал: нерухомі іони у «морі» вільних електронів", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен атом віддає у спільний фонд ~1 електрон; їх ~10²⁸–10²⁹ на кубометр", 12, GREY, "middle", style="italic")
    # іони решітки
    for r in range(4):
        for c in range(6):
            x = 140 + c * 105
            y = 120 + r * 70
            s += circle(x, y, 16, "#fde0d6", COPPER, 1.8)
            s += plus(x, y, 7, COPPER, 1.6)
    # вільні електрони між ними
    es = [(195, 155), (300, 150), (405, 165), (510, 152), (615, 158),
          (245, 225), (350, 215), (455, 230), (560, 220), (660, 225),
          (190, 290), (300, 295), (405, 285), (510, 298), (615, 288), (665, 195)]
    for i, (x, y) in enumerate(es):
        s += minus(x, y, 7, BLUE, 1.8)
        a = (i * 53) % 360
        s += line(x, y, x + 12 * math.cos(math.radians(a)), y + 12 * math.sin(math.radians(a)), BLUE, 1, )
    s += rect(120, 330, 280, 44, "#fde7e0", COPPER, 1.6, 8)
    s += plus(150, 352, 7, COPPER, 1.6)
    s += text(260, 356, "іони решітки (нерухомі, +)", 12, INK, "middle", "bold")
    s += rect(440, 330, 280, 44, "#eef2fb", BLUE, 1.6, 8)
    s += minus(470, 352, 7, BLUE, 1.8)
    s += text(585, 356, "вільні електрони (рухливі, −)", 12, INK, "middle", "bold")
    save("fig-2-3-1-electron-sea.svg", s)


# ── Рис. 2.3.2 — теплова метушня проти дрейфу ────────────────────────────────
def fig23_thermal_vs_drift():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Швидкий хаос — і повільний дрейф поверх нього", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "теплова швидкість величезна, але безладна; поле додає крихітний напрямлений зсув", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # ЛІВО — без поля
    s += text(210, 100, "без поля: хаос, нуль зсуву", 12.5, INK, "middle", "bold")
    start = (130, 230)
    p = _zig(start[0], start[1], [(2, -2), (2, 3), (3, -1), (-2, 3), (3, 2), (-1, -3),
                                  (3, -2), (-2, -2), (3, 2), (-3, 1), (2, -3)], 18, 16)
    s += polyline(p, BLUE, 1.8)
    s += circle(start[0], start[1], 5, BLUE, BLUE, 1)
    s += circle(p[-1][0], p[-1][1], 5, "#fff", BLUE, 2)
    s += text(210, 320, "повернувся майже туди ж", 11.5, GREY, "middle", style="italic")
    s += text(210, 340, "(теплова швидкість ~10⁵–10⁶ м/с)", 11, GREY, "middle")
    # ПРАВО — з полем
    s += text(610, 100, "з полем: хаос + ДРЕЙФ", 12.5, INK, "middle", "bold")
    for yy in (120, 320):
        s += arrow(470, yy, 760, yy, GREEN, 1.5)
    s += text(615, 112, "E →", 11.5, GREEN, "middle", "bold")
    start2 = (740, 230)
    p2 = _zig(start2[0], start2[1], [(-3, -2), (-2, 3), (-3, -1), (-2, 3), (-3, 2), (-2, -3),
                                     (-3, -2), (-2, 2), (-3, 2), (-2, 1), (-3, -2)], 18, 16)
    s += polyline(p2, BLUE, 1.8)
    s += circle(start2[0], start2[1], 5, BLUE, BLUE, 1)
    s += circle(p2[-1][0], p2[-1][1], 5, "#fff", BLUE, 2)
    s += arrow(start2[0], 300, p2[-1][0], 300, BLUE, 2.4)
    s += text(610, 340, "повільно зсунувся ліворуч (проти E)", 11.5, BLUE, "middle", "bold")
    s += text(610, 360, "(дрейф ~0.1 мм/с)", 11, GREY, "middle")
    save("fig-2-3-2-thermal-vs-drift.svg", s)


# ── Рис. 2.3.3 — формула струму I = n·A·v·e ─────────────────────────────────
def fig23_drift_formula():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Струм зсередини: I = n · A · v · e", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за секунду переріз перетинають усі електрони зі «стовпчика» довжиною v", 12, GREY, "middle", style="italic")
    wy, x0, x1 = 175, 110, 560
    s += line(x0, wy - 30, x1, wy - 30, COPPER, 3)
    s += line(x0, wy + 30, x1, wy + 30, COPPER, 3)
    s += rect(x0, wy - 30, x1 - x0, 60, "#fdf3ec", "none", 0)
    # стовпчик довжиною v·t
    s += rect(400, wy - 30, 120, 60, "#dfeaf0", "#7aa0b5", 1.6, 0)
    s += line(520, wy - 44, 520, wy + 44, INK, 2, "5 4")
    s += text(520, wy - 52, "переріз A", 11, INK, "middle", "bold")
    for ex in (420, 450, 480, 510):
        s += minus(ex, wy, 6, BLUE, 1.6)
    s += arrow(430, wy + 46, 510, wy + 46, BLUE, 2)
    s += text(460, wy + 62, "v (дрейф)", 11, BLUE, "middle", "bold")
    s += text(460, wy - 44, "стовпчик за 1 с", 10.5, INK, "middle")
    # формула
    s += rect(600, 120, 190, 130, "#f4f7f4", GREEN, 1.8, 12)
    s += text(695, 152, "I = n·A·v·e", 18, INK, "middle", "bold")
    s += text(610, 180, "n — електронів/м³", 11.5, INK, "start")
    s += text(610, 200, "A — переріз", 11.5, INK, "start")
    s += text(610, 220, "v — дрейф", 11.5, INK, "start")
    s += text(610, 240, "e — заряд електрона", 11.5, INK, "start")
    s += text(W / 2, H - 18, "Густина струму J = I/A = n·v·e — струм на одиницю перерізу (важлива для добору дроту).",
              12, INK, "middle", "bold")
    save("fig-2-3-3-drift-formula.svg", s)


# ── Рис. 2.3.4 — наскільки повільний дрейф ───────────────────────────────────
def fig23_drift_slow():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дрейф — повільніший за равлика", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "окремий електрон повз би метром дроту ГОДИНАМИ — а лампа спалахує миттєво", 12, GREY, "middle", style="italic")
    x0, x1, ay = 90, 740, 180
    s += line(x0, ay, x1, ay, INK, 2.5)
    # лог-шкала м/с від 1e-4 до 1e8
    items = [(-4, "дрейф електрона", "~10⁻⁴ м/с", BLUE),
             (-3, "равлик", "~10⁻³", GREY),
             (0, "пішохід", "~1", INK),
             (1.5, "авто", "~30", INK),
             (8, "поле / сигнал", "~10⁸ м/с", RED)]
    for e, name, val, col in items:
        x = x0 + (e + 4) / 12.0 * (x1 - x0)
        s += line(x, ay - 7, x, ay + 7, INK, 2)
        s += circle(x, ay, 6, col, col, 1)
        s += text(x, ay - 16, name, 11.5, col, "middle", "bold")
        s += text(x, ay + 26, val, 11, col, "middle")
    s += text(x0, ay + 50, "повільніше", 10.5, GREY, "start", style="italic")
    s += text(x1, ay + 50, "швидше (логарифмічна шкала, м/с)", 10.5, GREY, "end", style="italic")
    s += rect(150, 250, W - 300, 60, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 276, "Парадокс: носії повзуть, а ввімкнення — миттєве.", 13, INK, "middle", "bold")
    s += text(W / 2, 296, "Розгадка — не в швидкості електронів, а в полі. Про це — у §2.4.", 12, GREY, "middle", style="italic")
    save("fig-2-3-4-drift-slow.svg", s)


# ── Рис. 2.4.1 — три швидкості ───────────────────────────────────────────────
def fig24_three_speeds():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Три різні швидкості — не плутаймо їх", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "лампу вмикає не рух електронів, а поле, що мчить дротом", 12.5, GREY, "middle", style="italic")

    def box(x, title, speed, r1, r2, hot):
        col = GREEN if hot else "#9aa7b0"
        fill = "#eef7f0" if hot else "#fafafa"
        out = rect(x, 100, 240, 190, fill, col, 2.4 if hot else 1.6, 12)
        out += text(x + 120, 134, title, 14.5, (GREEN if hot else INK), "middle", "bold")
        out += text(x + 120, 178, speed, 21, INK, "middle", "bold")
        out += text(x + 120, 214, r1, 11.5, GREY, "middle")
        out += text(x + 120, 232, r2, 11.5, GREY, "middle")
        if hot:
            out += text(x + 120, 264, "← ось що світить", 12, GREEN, "middle", "bold")
        return out

    s += box(40, "ДРЕЙФ електронів", "~10⁻⁴ м/с", "повзе; переносить", "заряд по дроту", False)
    s += box(290, "ТЕПЛОВА метушня", "~10⁵ м/с", "швидко, але", "хаотично — нікуди", False)
    s += box(540, "ПОЛЕ / СИГНАЛ", "~10⁸ м/с", "мчить уздовж дроту", "майже як світло", True)
    s += text(W / 2, H - 16, "Перша й друга — про рух електронів; вмикання лампи — це третя, поширення поля.",
              12, INK, "middle", "bold")
    save("fig-2-4-1-three-speeds.svg", s)


# ── Рис. 2.4.2 — труба, вже повна кульок ─────────────────────────────────────
def fig24_full_pipe():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Чому миттєво: труба вже повна", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "штовхни кульку зліва — справа вилітає інша вмить, хоч жодна не пробігла трубу", 12, GREY, "middle", style="italic")
    py, x0, x1 = 175, 120, 690
    s += line(x0, py - 22, x1, py - 22, "#7a93a8", 3)
    s += line(x0, py + 22, x1, py + 22, "#7a93a8", 3)
    for i in range(14):
        s += circle(x0 + 24 + i * 46, py, 16, "#eef2f5", "#5b87a6", 1.6)
    # поштовх зліва
    s += arrow(70, py, 118, py, RED, 3)
    s += text(80, py - 30, "штовх", 12, RED, "middle", "bold")
    # вилітає справа
    s += circle(x1 + 30, py, 16, "#fde8e8", RED, 2)
    s += arrow(x1 + 4, py, x1 + 12, py, RED, 2.4)
    s += text(x1 + 30, py - 30, "вмить!", 12.5, RED, "middle", "bold")
    s += text(W / 2, py + 70, "біг не кулька, а ПОШТОВХ — пружна хвиля крізь увесь ряд", 13, INK, "middle", "bold")
    s += rect(150, 290, W - 300, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 312, "Так само дріт уже повний електронів по всій довжині;", 12.5, INK, "middle", "bold")
    s += text(W / 2, 330, "вмикач — це «поштовх» (поле), що пробігає дротом майже миттєво.", 12, GREY, "middle", style="italic")
    save("fig-2-4-2-full-pipe.svg", s)


# ── Рис. 2.4.3 — поле поширюється дротом ─────────────────────────────────────
def fig24_field_propagates():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що насправді біжить: фронт поля", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "замикаєш вмикач — поле мчить дротом ~10⁸ м/с і зрушує ВСІ електрони майже разом", 12, GREY, "middle", style="italic")
    wy, x0, x1 = 150, 110, 710
    # вмикач
    s += line(x0, wy, x0 + 40, wy, INK, 2.6)
    s += line(x0 + 40, wy, x0 + 70, wy - 16, INK, 2.6)
    s += text(x0 + 35, wy - 28, "вмикач", 11, INK, "middle", "bold")
    # дріт
    s += line(x0 + 70, wy, x1, wy, COPPER, 3)
    # лампа
    s += circle(x1 + 26, wy, 20, "#fff7d6", "#caa23a", 2.4)
    s += line(x1 + 14, wy - 8, x1 + 38, wy + 8, "#caa23a", 1.6)
    s += line(x1 + 14, wy + 8, x1 + 38, wy - 8, "#caa23a", 1.6)
    s += text(x1 + 26, wy + 40, "лампа", 11, INK, "middle", "bold")
    # фронт поля
    front = 540
    s += line(front, wy - 50, front, wy + 50, GREEN, 3)
    s += arrow(front, wy - 40, front + 70, wy - 40, GREEN, 2.6)
    s += text(front + 30, wy - 50, "фронт поля ~10⁸ м/с", 12, GREEN, "start", "bold")
    # електрони з крихітним дрейфом по всій довжині
    for ex in range(170, 700, 70):
        s += minus(ex, wy, 6, BLUE, 1.6)
        s += arrow(ex + 8, wy + 22, ex + 20, wy + 22, BLUE, 1.4)
    s += text(380, wy + 50, "усі електрони ледь зрушили — але ВЖЕ дрейфують (струм скрізь)", 11.5, BLUE, "middle", "bold")
    s += text(W / 2, H - 14, "За наносекунди фронт сягає лампи — струм тече по всьому колу, і вона світить.",
              12, INK, "middle", "bold")
    save("fig-2-4-3-field-propagates.svg", s)


# ── Рис. 2.4.4 — енергія тече в полі навколо дротів ──────────────────────────
def fig24_energy_in_field():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Глибша правда: енергія тече в полі, не в електронах", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "повільні електрони лише задають шлях; енергію несе поле в просторі НАВКОЛО дротів", 12, GREY, "middle", style="italic")
    # джерело
    s += line(120, 120, 120, 240, INK, 2.4)
    s += line(104, 165, 136, 165, RED, 3)
    s += line(110, 182, 130, 182, BLUE, 4)
    s += text(96, 170, "дже-", 10.5, INK, "end")
    s += text(96, 184, "рело", 10.5, INK, "end")
    # два провідники
    s += line(120, 120, 660, 120, COPPER, 3)
    s += text(390, 110, "+ провідник", 11, RED, "middle", "bold")
    s += line(120, 240, 660, 240, COPPER, 3)
    s += text(390, 256, "− провідник (зворотний)", 11, BLUE, "middle", "bold")
    # навантаження
    s += rect(660, 150, 36, 60, "#fff7ef", "#c89b5a", 2.2, 5)
    s += line(660, 120, 678, 150, INK, 2.4)
    s += line(660, 240, 678, 210, INK, 2.4)
    s += text(720, 184, "наван-", 11, INK, "start")
    s += text(720, 198, "таження", 11, INK, "start")
    # поле в просторі між провідниками — енергопотік
    s += rect(150, 130, 480, 100, "#eef7f0", "none", 0)
    for ex in range(190, 631, 80):
        s += arrow(ex, 180, ex + 44, 180, GREEN, 2.2)
    s += text(390, 200, "потік енергії в ПОЛІ →", 12.5, GREEN, "middle", "bold")
    # повільні електрони
    for ex in (220, 340, 460, 560):
        s += minus(ex, 120, 5, BLUE, 1.4)
        s += minus(ex, 240, 5, BLUE, 1.4)
    s += text(W / 2, H - 12, "Несподівано, та правда: енергія йде простором між дротами, а дроти лише «спрямовують» її.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-4-4-energy-in-field.svg", s)


def _lamp(cx, cy, r=18, col="#caa23a"):
    out = circle(cx, cy, r, "#fff7d6", col, 2.4)
    out += line(cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7, col, 1.6)
    out += line(cx - r * 0.7, cy + r * 0.7, cx + r * 0.7, cy - r * 0.7, col, 1.6)
    return out


def _ammeter(cx, cy, reading):
    out = circle(cx, cy, 20, "#eef5ff", INK, 2.2)
    out += text(cx, cy + 6, "A", 15, INK, "middle", "bold")
    out += text(cx, cy - 30, reading, 12, GREEN, "middle", "bold")
    return out


# ── Рис. 2.5.1 — струм однаковий уздовж кола ─────────────────────────────────
def fig25_same_current():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Струм однаковий скрізь — нічого не «з'їдається»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "амперметр показує те саме до лампи, після лампи й у зворотному дроті", 12, GREY, "middle", style="italic")
    L, R, T, B = 160, 660, 120, 300
    # батарея
    s += line(L, T, L, 185, INK, 2.4)
    s += line(L, 235, L, B, INK, 2.4)
    s += line(L - 18, 185, L + 18, 185, INK, 3)
    s += line(L - 10, 202, L + 10, 202, INK, 5)
    s += line(L - 18, 205, L + 18, 205, INK, 3)
    s += line(L - 10, 222, L + 10, 222, INK, 5)
    s += text(L - 30, 182, "+", 13, RED, "middle", "bold")
    s += text(L - 30, 228, "−", 13, BLUE, "middle", "bold")
    # верх: A1 — лампа
    s += line(L, T, 270, T, INK, 2.4)
    s += _ammeter(300, T, "0.5 А")
    s += line(330, T, 430, T, INK, 2.4)
    s += _lamp(470, T)
    s += text(470, T - 30, "лампа", 11, INK, "middle", "bold")
    s += line(510, T, R, T, INK, 2.4)
    # право
    s += line(R, T, R, B, INK, 2.4)
    # низ: A2
    s += line(L, B, 360, B, INK, 2.4)
    s += _ammeter(420, B, "0.5 А")
    s += line(480, B, R, B, INK, 2.4)
    # струм
    s += arrow(210, T, 250, T, RED, 2.4)
    s += arrow(560, T, 600, T, RED, 2.4)
    s += arrow(560, B, 520, B, RED, 2.4)
    s += text(W / 2, H - 16, "Скільки заряду за секунду входить у лампу — стільки й виходить (збереження заряду, Розд.1).",
              12, INK, "middle", "bold")
    save("fig-2-5-1-same-current.svg", s)


# ── Рис. 2.5.2 — нестислива вода в петлі ─────────────────────────────────────
def fig25_water_loop():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Як вода в замкненій петлі: витрата однакова скрізь", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "навіть у вузькому місці потік той самий — там падає ТИСК, а не витрата", 12, GREY, "middle", style="italic")
    L, R, T, B = 150, 670, 120, 300
    # труба-петля (подвійні лінії — спрощено одинарними товстими)
    s += line(L, T, R, T, "#5b87a6", 6)
    s += line(L, B, 330, B, "#5b87a6", 6)
    s += line(430, B, R, B, "#5b87a6", 6)
    s += line(L, T, L, B, "#5b87a6", 6)
    s += line(R, T, R, B, "#5b87a6", 6)
    # насос
    s += circle(L, 210, 26, "#dceaf2", "#5b87a6", 2.4)
    s += f'<path d="M {L-10},204 a 10,10 0 1 1 8,12" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += text(L, 250, "насос", 11, INK, "middle", "bold")
    # вузьке місце (навантаження)
    s += f'<path d="M 330,{B-14} L 360,{B-3} L 400,{B-3} L 430,{B-14}" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += f'<path d="M 330,{B+14} L 360,{B+3} L 400,{B+3} L 430,{B+14}" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += text(380, B + 34, "вузьке місце", 11, INK, "middle", "bold")
    s += text(380, B + 50, "(= навантаження)", 10.5, GREY, "middle", style="italic")
    # витрата однакова
    for x, lbl in ((250, "5 л/с"), (560, "5 л/с"), (380, "5 л/с")):
        yy = T if x != 380 else B
        s += arrow(x - 18, yy, x + 22, yy, "#2b7", 2.4)
        s += text(x, yy - 14 if yy == T else yy + 0, lbl, 11.5, "#2b7", "middle", "bold")
    s += text(380, 150, "та сама витрата по всій петлі", 12.5, INK, "middle", "bold")
    s += rect(150, 326, W - 300, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 351, "Потік (= струм) однаковий скрізь; у вузькому місці падає тиск (= напруга).",
              12, INK, "middle", "bold")
    save("fig-2-5-2-water-loop.svg", s)


# ── Рис. 2.5.3 — струм проходить, енергія витрачається ───────────────────────
def fig25_current_vs_energy():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Витрачається ЕНЕРГІЯ, а не струм", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "через лампу проходить стільки ж заряду — але кожен кулон віддає їй енергію", 12, GREY, "middle", style="italic")
    wy = 200
    s += line(110, wy, 320, wy, COPPER, 3)
    s += _lamp(390, wy, 30)
    s += text(390, wy + 52, "лампа", 12, INK, "middle", "bold")
    s += line(460, wy, 710, wy, COPPER, 3)
    # кулон до лампи — високий стовпчик енергії
    s += circle(250, wy, 16, "#fdf4f4", RED, 2.2)
    s += plus(250, wy, 8, RED)
    s += rect(238, wy - 80, 24, 60, "#fde8e8", RED, 1.6, 3)
    s += text(250, wy - 88, "багато", 10.5, RED, "middle", "bold")
    s += arrow(266, wy, 320, wy, RED, 2.4)
    # кулон після лампи — низький стовпчик
    s += circle(540, wy, 16, "#fdf4f4", RED, 2.2)
    s += plus(540, wy, 8, RED)
    s += rect(528, wy - 40, 24, 20, "#fde8e8", RED, 1.6, 3)
    s += text(540, wy - 48, "мало", 10.5, RED, "middle", "bold")
    s += arrow(556, wy, 610, wy, RED, 2.4)
    s += text(250, wy + 34, "той самий кулон", 11, INK, "middle")
    s += text(540, wy + 34, "той самий кулон", 11, INK, "middle")
    # підписи
    s += rect(150, 300, 250, 56, "#eef7f0", GREEN, 1.6, 10)
    s += text(275, 322, "СТРУМ", 13, GREEN, "middle", "bold")
    s += text(275, 342, "2 Кл/с увійшло = 2 Кл/с вийшло", 11, INK, "middle")
    s += rect(430, 300, 250, 56, "#fdf4f4", RED, 1.6, 10)
    s += text(555, 322, "ЕНЕРГІЯ", 13, RED, "middle", "bold")
    s += text(555, 342, "багато увійшло, мало вийшло", 11, INK, "middle")
    save("fig-2-5-3-current-vs-energy.svg", s)


# ── Рис. 2.5.4 — послідовна гірлянда ─────────────────────────────────────────
def fig25_series_string():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Послідовно: один струм на всіх", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "крізь усі елементи тече той самий струм; один резистор задає його для всіх", 12, GREY, "middle", style="italic")
    L, R, T, B = 150, 670, 120, 290
    # батарея
    s += line(L, T, L, 180, INK, 2.4)
    s += line(L, 210, L, B, INK, 2.4)
    s += line(L - 16, 180, L + 16, 180, INK, 3)
    s += line(L - 9, 196, L + 9, 196, INK, 5)
    s += line(L - 16, 199, L + 16, 199, INK, 3)
    s += line(L - 9, 213, L + 9, 213, INK, 5)
    # резистор на верхньому дроті
    s += line(L, T, 250, T, INK, 2.4)
    s += rect(250, T - 11, 70, 22, "#fff", INK, 2, 3)
    s += text(285, T - 18, "R", 12, INK, "middle", "bold", "italic")
    s += line(320, T, R, T, INK, 2.4)
    # три світлодіоди на правому/нижньому
    s += line(R, T, R, B, INK, 2.4)
    leds = [(R, 150), (R, 205)]
    for (lx, ly) in leds:
        s += f'<path d="M {lx-14},{ly-12} L {lx-14},{ly+12} L {lx+12},{ly} Z" fill="#fdeeee" stroke="{RED}" stroke-width="1.8"/>\n'
        s += line(lx + 12, ly - 12, lx + 12, ly + 12, RED, 2.4)
    s += line(L, B, 430, B, INK, 2.4)
    s += f'<path d="M 430,{B-14} L 430,{B+14} L 456,{B} Z" fill="#fdeeee" stroke="{RED}" stroke-width="1.8"/>\n'
    s += line(456, B - 14, 456, B + 14, RED, 2.4)
    s += line(456, B, R, B, INK, 2.4)
    s += text(560, B + 22, "3 світлодіоди послідовно", 11.5, RED, "middle", "bold")
    # струм
    for (px, py, dx) in ((200, T, 1), (560, T, 1), (300, B, -1)):
        s += arrow(px, py, px + dx * 40, py, RED, 2.4)
    s += text(W / 2, T - 40, "I — однаковий у R і в кожному світлодіоді", 12.5, INK, "middle", "bold")
    s += rect(150, 312, W - 300, 38, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 336, "Розрив у будь-якому місці гасить усе коло (як стара ялинкова гірлянда).",
              12, INK, "middle", "bold")
    save("fig-2-5-4-series-string.svg", s)


# ── Рис. 2.6.1 — причинний ланцюг: напруга → струм ───────────────────────────
def fig26_causal_chain():
    W, H = 840, 320
    s = header(W, H)
    s += text(W / 2, 34, "Причина й наслідок: напруга породжує струм", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ланцюг причин біжить ліворуч-праворуч; струм — наслідок, не причина", 12, GREY, "middle", style="italic")
    boxes = [
        ("ЕРС\nджерела", "#fff7ef", "#c89b5a"),
        ("НАПРУГА U\n(різниця V)", "#f3eefb", "#8a52c0"),
        ("ПОЛЕ E\nв дроті", "#eef7f0", GREEN),
        ("СИЛА\nqE на e⁻", "#fdeeee", RED),
        ("ДРЕЙФ\nv", "#eef2fb", BLUE),
        ("СТРУМ\nI", "#eef5ff", INK),
    ]
    bw, gap, y = 116, 18, 150
    x = 18
    cxs = []
    for i, (lab, fill, col) in enumerate(boxes):
        s += rect(x, y, bw, 70, fill, col, 2, 10)
        parts = lab.split("\n")
        s += text(x + bw / 2, y + 30, parts[0], 13, col, "middle", "bold")
        s += text(x + bw / 2, y + 50, parts[1], 11, INK, "middle")
        cxs.append((x, x + bw))
        x += bw + gap
    for i in range(len(boxes) - 1):
        s += arrow(cxs[i][1] + 1, y + 35, cxs[i + 1][0] - 1, y + 35, INK, 2.2)
    s += text(W / 2, 250, "«спричиняє»  →  на кожному кроці", 12.5, INK, "middle", "bold")
    s += text(W / 2, 278, "Прибери напругу — зникне й усе праворуч від неї: струму не стане.", 12, GREY, "middle", style="italic")
    save("fig-2-6-1-causal-chain.svg", s)


# ── Рис. 2.6.2 — поле всередині дроту жене дрейф ─────────────────────────────
def fig26_field_in_wire():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Як напруга діє: поле вздовж дроту", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "різниця потенціалів на кінцях створює поле в дроті, а воно штовхає електрони", 12, GREY, "middle", style="italic")
    wy, x0, x1 = 175, 150, 670
    # клеми
    s += rect(100, wy - 40, 44, 80, "#fbecec", RED, 2.4, 8)
    s += plus(122, wy, 12, RED)
    s += rect(W - 144, wy - 40, 44, 80, "#e9eefb", BLUE, 2.4, 8)
    s += minus(W - 122, wy, 12, BLUE)
    s += text(122, wy - 50, "вищий V", 11, RED, "middle", "bold")
    s += text(W - 122, wy - 50, "нижчий V", 11, BLUE, "middle", "bold")
    # дріт
    s += line(x0, wy - 18, x1, wy - 18, COPPER, 3)
    s += line(x0, wy + 18, x1, wy + 18, COPPER, 3)
    s += rect(x0, wy - 18, x1 - x0, 36, "#fdf3ec", "none", 0)
    # поле в дроті
    for ex in range(200, 640, 90):
        s += arrow(ex, wy - 36, ex + 50, wy - 36, GREEN, 1.8)
    s += text(410, wy - 50, "поле E вздовж дроту (від + до −)", 12, GREEN, "middle", "bold")
    # електрони з силою/дрейфом
    for ex in range(210, 640, 80):
        s += minus(ex, wy, 6, BLUE, 1.6)
    s += arrow(560, wy + 36, 230, wy + 36, BLUE, 2.4)
    s += text(410, wy + 52, "сила qE → дрейф електронів (проти E)", 12, BLUE, "middle", "bold")
    s += rect(120, 290, W - 240, 56, "#f4f7f4", "#8a52c0", 1.6, 10)
    s += text(W / 2, 312, "У статиці провідник — еквіпотенціаль, поля нема (§1.6).", 12, INK, "middle", "bold")
    s += text(W / 2, 332, "Коли ж тече струм, уздовж дроту лишається мале поле — воно й підтримує дрейф.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-6-2-field-in-wire.svg", s)


# ── Рис. 2.6.3 — сталий струм проти короткого ────────────────────────────────
def fig26_sustained_vs_transient():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому струму потрібна ПІДТРИМАНА напруга", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "статичний заряд штовхне струм лише на мить; ЕРС тримає різницю — струм сталий", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # ЛІВО — конденсатор
    s += text(205, 100, "заряджений конденсатор", 12.5, INK, "middle", "bold")
    s += line(150, 130, 150, 190, RED, 4)
    s += line(170, 130, 170, 190, BLUE, 4)
    s += plus(150, 160, 7, RED, 1.6); s += minus(170, 160, 7, BLUE, 1.6)
    s += line(150, 130, 120, 130, INK, 2); s += line(120, 130, 120, 210, INK, 2)
    s += line(170, 130, 260, 130, INK, 2); s += line(260, 130, 260, 210, INK, 2)
    s += line(120, 210, 260, 210, INK, 2)
    s += _lamp(190, 210, 12)
    # графік I(t) — спад
    gx, gy = 130, 330
    s += arrow(gx, gy, gx + 150, gy, INK, 1.6)
    s += arrow(gx, gy, gx, gy - 70, INK, 1.6)
    s += text(gx + 150, gy + 14, "t", 11, INK, "start", "bold", "italic")
    s += text(gx - 8, gy - 64, "I", 11, INK, "end", "bold", "italic")
    pts = [(gx + i * 3, gy - 60 * math.exp(-i / 14.0)) for i in range(0, 50)]
    s += polyline(pts, RED, 2.4)
    s += text(gx + 90, gy - 40, "спадає до 0", 11, RED, "start", "bold")
    s += text(205, 360, "короткий поштовх — і все", 11.5, GREY, "middle", style="italic")
    # ПРАВО — батарея
    s += text(610, 100, "батарея (ЕРС)", 12.5, GREEN, "middle", "bold")
    s += line(540, 130, 540, 190, INK, 2)
    s += line(525, 145, 555, 145, INK, 3); s += line(533, 160, 547, 160, INK, 5)
    s += line(525, 163, 555, 163, INK, 3); s += line(533, 178, 547, 178, INK, 5)
    s += line(540, 130, 510, 130, INK, 2); s += line(510, 130, 510, 210, INK, 2)
    s += line(540, 190, 660, 190, INK, 2); s += line(660, 130, 660, 210, INK, 2)
    s += line(540, 130, 660, 130, INK, 2)
    s += line(510, 210, 660, 210, INK, 2)
    s += _lamp(585, 210, 12)
    gx2, gy2 = 530, 330
    s += arrow(gx2, gy2, gx2 + 150, gy2, INK, 1.6)
    s += arrow(gx2, gy2, gx2, gy2 - 70, INK, 1.6)
    s += text(gx2 + 150, gy2 + 14, "t", 11, INK, "start", "bold", "italic")
    s += text(gx2 - 8, gy2 - 64, "I", 11, INK, "end", "bold", "italic")
    s += line(gx2, gy2 - 45, gx2 + 145, gy2 - 45, GREEN, 2.6)
    s += text(gx2 + 75, gy2 - 52, "сталий", 11, GREEN, "middle", "bold")
    s += text(610, 360, "струм тримається, поки є ЕРС", 11.5, GREY, "middle", style="italic")
    save("fig-2-6-3-sustained-vs-transient.svg", s)


# ── Рис. 2.6.4 — ЕРС: джерело-насос ──────────────────────────────────────────
def fig26_emf():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "ЕРС: «насос», що тримає напругу", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "джерело знов і знов піднімає кожен кулон на потенціал, поки коло його «спускає»", 12, GREY, "middle", style="italic")
    L, R, T, B = 200, 620, 110, 290
    # джерело-насос ліворуч
    s += rect(L - 34, 150, 68, 100, "#fff7ef", "#c89b5a", 2.4, 10)
    s += arrow(L, 244, L, 158, "#c89b5a", 3.2)
    s += text(L, 140, "ЕРС ℰ", 14, "#c89b5a", "middle", "bold")
    s += text(L, 270, "насос", 11, INK, "middle", "bold")
    # контур
    s += line(L, T, R, T, INK, 2.4)
    s += line(L, B, R, B, INK, 2.4)
    s += line(L, 150, L, T, INK, 2.4)
    s += line(L, 250, L, B, INK, 2.4)
    s += rect(R - 18, 170, 36, 60, "#fde8e8", RED, 2.2, 5)
    s += text(R + 36, 204, "наван-", 11, INK, "middle")
    s += line(R, T, R, 170, INK, 2.4)
    s += line(R, 230, R, B, INK, 2.4)
    # обхід
    s += arrow(370, T, 430, T, RED, 2.6)
    s += text(400, T - 12, "кулон з енергією →", 11.5, RED, "middle", "bold")
    s += arrow(430, B, 370, B, BLUE, 2.6)
    s += text(400, B + 22, "← віддав енергію, вертається", 11.5, BLUE, "middle", "bold")
    s += rect(150, 312, W - 300, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 337, "ЕРС — це не «сила», а енергія на заряд (вольти), яку джерело ДОДАЄ; під навантаженням на клемах трохи менше (Розд.5).",
              11, INK, "middle", "bold")
    save("fig-2-6-4-emf.svg", s)


def _battery(x, ytop, ybot):
    cy = (ytop + ybot) / 2
    out = line(x, ytop, x, cy - 16, INK, 2.4)
    out += line(x, cy + 16, x, ybot, INK, 2.4)
    out += line(x - 16, cy - 16, x + 16, cy - 16, INK, 3)
    out += line(x - 9, cy - 1, x + 9, cy - 1, INK, 5)
    out += line(x - 16, cy + 1, x + 16, cy + 1, INK, 3)
    out += line(x - 9, cy + 16, x + 9, cy + 16, INK, 5)
    out += text(x - 28, cy - 12, "+", 13, RED, "middle", "bold")
    out += text(x - 28, cy + 20, "−", 13, BLUE, "middle", "bold")
    return out


# ── Рис. 2.7.1 — замкнене проти розімкненого ─────────────────────────────────
def fig27_closed_vs_open():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Струм тече лише по неперервній петлі", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "замкни коло — лампа світить; розірви будь-де — струму нема", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 26, FAINT, 1.5)

    def loop(x0, closed):
        L, R, T, B = x0, x0 + 210, 120, 280
        out = _battery(L, T, B)
        out += line(L, T, R, T, INK, 2.4)
        # лампа праворуч-зверху
        cx, cy = R, 165
        col = "#caa23a"
        fill = "#fff2b0" if closed else "#f0f0f0"
        out += circle(cx, cy, 18, fill, col if closed else "#aaa", 2.4)
        out += line(cx - 12, cy - 12, cx + 12, cy + 12, col if closed else "#aaa", 1.6)
        out += line(cx - 12, cy + 12, cx + 12, cy - 12, col if closed else "#aaa", 1.6)
        if closed:
            for a in range(0, 360, 45):
                out += line(cx + 22 * math.cos(math.radians(a)), cy + 22 * math.sin(math.radians(a)),
                            cx + 30 * math.cos(math.radians(a)), cy + 30 * math.sin(math.radians(a)), col, 1.6)
        out += line(R, T, R, cy - 18, INK, 2.4)
        out += line(R, cy + 18, R, B, INK, 2.4)
        # вмикач на нижньому дроті
        out += line(L, B, x0 + 80, B, INK, 2.4)
        if closed:
            out += line(x0 + 80, B, x0 + 120, B, INK, 2.4)
        else:
            out += line(x0 + 80, B, x0 + 115, B - 24, INK, 2.4)
            out += text(x0 + 100, B + 24, "розрив → повна U тут", 10.5, RED, "middle", "bold")
        out += line(x0 + 120, B, R, B, INK, 2.4)
        out += text(x0 + 100, B - (34 if closed else 40), "вмикач", 10.5, INK, "middle", "bold")
        if closed:
            out += arrow(x0 + 70, T, x0 + 110, T, RED, 2.4)
            out += arrow(R, 230, R, 265, RED, 2.4)
        return out

    s += loop(120, True)
    s += text(225, 104, "ЗАМКНЕНЕ: струм тече, лампа світить", 12, GREEN, "middle", "bold")
    s += loop(500, False)
    s += text(605, 104, "РОЗІМКНЕНЕ: струму нема, темно", 12, RED, "middle", "bold")
    save("fig-2-7-1-closed-vs-open.svg", s)


# ── Рис. 2.7.2 — глухий кут проти петлі ──────────────────────────────────────
def fig27_dead_end():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Чому потрібна петля: заряду нема куди дітися", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у глухому куті заряд нагромаджується й сам себе гальмує; у петлі — вертається й тече", 11.5, GREY, "middle", style="italic")
    # глухий кут
    s += text(150, 108, "глухий кут:", 12.5, RED, "start", "bold")
    s += _battery(150, 130, 200)
    s += line(150, 130, 470, 130, COPPER, 3)
    s += line(470, 130, 470, 165, COPPER, 3)
    s += line(440, 165, 500, 165, INK, 3)  # тупик
    for px in (440, 458, 476, 494):
        s += plus(px, 178, 6, RED, 1.6)
    s += text(560, 150, "заряд громадиться,", 11.5, RED, "start", "bold")
    s += text(560, 168, "поле відштовхує наступних —", 11.5, INK, "start")
    s += text(560, 186, "потік спиняється за мить", 11.5, INK, "start")
    s += line(150, 200, 470, 200, COPPER, 3)  # нижній (нікуди)
    s += line(470, 165, 470, 200, COPPER, 3)
    # петля
    s += text(150, 250, "петля:", 12.5, GREEN, "start", "bold")
    s += _battery(150, 270, 330)
    s += line(150, 270, 470, 270, COPPER, 3)
    s += line(470, 270, 470, 330, COPPER, 3)
    s += line(150, 330, 470, 330, COPPER, 3)
    s += arrow(290, 270, 330, 270, RED, 2.2)
    s += arrow(330, 330, 290, 330, RED, 2.2)
    s += text(560, 292, "заряд вертається до джерела —", 11.5, GREEN, "start", "bold")
    s += text(560, 310, "потік кружляє безперервно", 11.5, INK, "start")
    save("fig-2-7-2-dead-end.svg", s)


# ── Рис. 2.7.3 — нормально / розрив / коротке ────────────────────────────────
def fig27_three_states():
    W, H = 840, 340
    s = header(W, H)
    s += text(W / 2, 34, "Три стани кола: норма, розрив, коротке", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "опір вирішує все: помірний струм, нуль струму чи небезпечний надлишок", 12, GREY, "middle", style="italic")

    def mini(x0, title, tcol, body, foot, footcol):
        L, R, T, B = x0, x0 + 180, 110, 240
        out = rect(x0 - 10, 92, 210, 200, "#fafafa", "#ddd", 1.4, 10)
        out += text(x0 + 90, 112, title, 13, tcol, "middle", "bold")
        out += _battery(L, T + 16, B)
        out += line(L, T + 16, R, T + 16, INK, 2)
        out += line(L, B, R, B, INK, 2)
        out += line(R, T + 16, R, B, INK, 2)
        out += body(R, (T + 16 + B) / 2)
        out += text(x0 + 90, 268, foot, 11.5, footcol, "middle", "bold")
        return out

    def normal(rx, ry):
        return rect(rx - 9, ry - 26, 18, 52, "#fff", INK, 2, 3) + text(rx + 22, ry + 4, "R", 12, INK, "start", "bold", "italic")

    def openbreak(rx, ry):
        return (line(rx, ry - 26, rx, ry - 6, INK, 2) + line(rx, ry + 6, rx, ry + 26, INK, 2)
                + line(rx - 10, ry - 6, rx + 6, ry - 18, RED, 2)
                + text(rx + 14, ry + 4, "✕", 15, RED, "start", "bold"))

    def short(rx, ry):
        return line(rx, ry - 26, rx, ry + 26, RED, 4)

    s += mini(70, "НОРМАЛЬНО", GREEN, normal, "R помірний → I помірний", INK)
    s += mini(330, "РОЗРИВ (open)", INK, openbreak, "R = ∞ → I = 0", RED)
    s += mini(590, "КОРОТКЕ (short)", RED, short, "R ≈ 0 → I величезний!", RED)
    save("fig-2-7-3-three-states.svg", s)


# ── Рис. 2.7.4 — спільний зворотний шлях (земля) ─────────────────────────────
def fig27_ground_return():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Зворотний шлях часто спільний: «земля» / корпус", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "в авто один дріт іде до споживача, а назад струм вертається крізь металевий кузов", 11.5, GREY, "middle", style="italic")
    # кузов як шина
    s += rect(120, 230, W - 240, 24, "#dfe3e6", "#9aa7b0", 2, 4)
    s += text(W / 2, 246, "металевий кузов (спільна «земля», зворотний провід)", 11.5, "#5a6670", "middle", "bold")
    # акумулятор
    s += _battery(180, 120, 230)
    s += text(180, 108, "акумулятор", 11, INK, "middle", "bold")
    s += line(180, 230, 180, 218, INK, 2.2)  # − до кузова
    s += text(150, 215, "−", 12, BLUE, "middle", "bold")
    # один дріт до фари
    s += line(180, 120, 620, 120, RED, 2.6)
    s += text(400, 110, "один сигнальний дріт (+)", 11.5, RED, "middle", "bold")
    s += _lamp(620, 140, 18)
    s += text(620, 110, "фара", 11, INK, "middle", "bold")
    s += line(620, 158, 620, 230, INK, 2.2)  # назад через кузов
    s += text(648, 200, "назад крізь кузов", 11, "#5a6670", "start")
    # стрілки струму
    s += arrow(300, 120, 340, 120, RED, 2.2)
    s += arrow(360, 242, 320, 242, RED, 2.2)
    s += text(W / 2, H - 14, "Петля все одно замкнена — просто половину шляху грає корпус. Економія на дротах.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-7-4-ground-return.svg", s)


# ── Рис. 2.8.1 — три класи матеріалів ────────────────────────────────────────
def fig28_three_classes():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 34, "Три класи: різниця — в кількості вільних носіїв", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "проводить струм те, у чому є вільні заряди, яким є куди рухатися", 12, GREY, "middle", style="italic")

    def panel(x0, title, tcol, free, examples, note):
        out = rect(x0, 90, 250, 230, "#fafafa", "#ddd", 1.6, 12)
        out += text(x0 + 125, 116, title, 14.5, tcol, "middle", "bold")
        # іони решітки
        for r in range(2):
            for c in range(4):
                ix = x0 + 50 + c * 50
                iy = 150 + r * 46
                out += circle(ix, iy, 12, "#fde0d6", COPPER, 1.5)
                out += text(ix, iy + 4, "+", 10, COPPER, "middle", "bold")
        # вільні електрони
        spots = [(x0 + 78, 175), (x0 + 130, 200), (x0 + 175, 168), (x0 + 100, 215),
                 (x0 + 150, 220), (x0 + 200, 195)]
        for i in range(free):
            out += minus(spots[i][0], spots[i][1], 6, BLUE, 1.6)
        out += text(x0 + 125, 264, examples, 12, INK, "middle", "bold")
        out += text(x0 + 125, 286, note, 11, GREY, "middle", style="italic")
        return out

    s += panel(20, "ПРОВІДНИК", GREEN, 6, "мідь, срібло, алюміній", "багато вільних носіїв")
    s += panel(295, "ІЗОЛЯТОР", RED, 0, "скло, пластик, гума", "вільних носіїв ~нема")
    s += panel(570, "НАПІВПРОВІДНИК", "#8a52c0", 2, "кремній, германій", "мало — але КЕРОВАНО")
    s += text(W / 2, H - 14, "Метал — повний електронів «океан»; ізолятор — порожньо; напівпровідник — кілька, і їх можна додати.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-8-1-three-classes.svg", s)


# ── Рис. 2.8.2 — зв'язані проти вільних електронів ───────────────────────────
def fig28_bound_vs_free():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Звідки беруться вільні носії", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "у провіднику валентні електрони відриваються; в ізоляторі — міцно зв'язані", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # провідник
    s += text(205, 102, "провідник", 13, GREEN, "middle", "bold")
    for c in range(3):
        cx = 110 + c * 90
        s += circle(cx, 200, 22, "#fde0d6", COPPER, 1.8)
        s += text(cx, 205, "+", 14, COPPER, "middle", "bold")
    for (ex, ey) in [(150, 165), (230, 175), (290, 160), (130, 235), (210, 240), (280, 230), (185, 200)]:
        s += minus(ex, ey, 6, BLUE, 1.6)
    s += text(205, 285, "електрони відірвані — гуляють вільно", 11.5, INK, "middle", "bold")
    s += text(205, 304, "(спільне «море», §2.3)", 11, GREY, "middle", style="italic")
    # ізолятор
    s += text(615, 102, "ізолятор", 13, RED, "middle", "bold")
    for c in range(3):
        cx = 520 + c * 90
        s += circle(cx, 200, 22, "#eef2f5", "#9aa7b0", 1.8)
        s += text(cx, 205, "+", 14, "#9aa7b0", "middle", "bold")
        # електрони на орбіті, зв'язані
        for a in (0, 120, 240):
            s += minus(cx + 22 * math.cos(math.radians(a)), 200 + 22 * math.sin(math.radians(a)), 5, BLUE, 1.4)
        s += circle(cx, 200, 22, "none", "#cdd5da", 1, )
    s += text(615, 285, "електрони міцно тримаються атомів —", 11.5, INK, "middle", "bold")
    s += text(615, 304, "вільних нема, проводити нічим", 11, GREY, "middle", style="italic")
    save("fig-2-8-2-bound-vs-free.svg", s)


# ── Рис. 2.8.3 — енергетичні зони й щілина ───────────────────────────────────
def fig28_band_gap():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Глибше «чому»: енергетична щілина", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "щоб проводити, електрон має стрибнути у вищу (порожню) зону — через заборонену щілину", 11.5, GREY, "middle", style="italic")
    # вісь енергії
    s += arrow(60, 360, 60, 100, INK, 1.8)
    s += text(46, 110, "енергія", 11, INK, "end", style="italic")

    def col(cx, name, gap, jumped):
        baseY = 350
        vb_h = 56
        cb_h = 56
        vb_top = baseY - vb_h
        cb_bot = vb_top - gap
        cb_top = cb_bot - cb_h
        out = rect(cx - 70, vb_top, 140, vb_h, "#cfd6e8", "#7a87a8", 1.6)
        out += text(cx, vb_top + 34, "валентна", 11, INK, "middle", "bold")
        out += text(cx, vb_top + 50, "(повна)", 9.5, GREY, "middle")
        out += rect(cx - 70, cb_top, 140, cb_h, "#eef5ff", "#9ab0d0", 1.6)
        out += text(cx, cb_top + 30, "провідності", 11, INK, "middle", "bold")
        out += text(cx, cb_top + 46, "(порожня)", 9.5, GREY, "middle")
        if gap > 4:
            out += f'<path d="M {cx-70},{cb_bot} L {cx+70},{cb_bot} L {cx+70},{vb_top} L {cx-70},{vb_top}" fill="#fbeeee" stroke="none"/>\n'
            out += rect(cx - 70, cb_bot, 140, vb_top - cb_bot, "#fbeeee", RED, 1, "4 3")
            out += text(cx, (cb_bot + vb_top) / 2 + 4, "щілина", 10.5, RED, "middle", "bold")
        # електрони у валентній
        for i in range(5):
            out += minus(cx - 50 + i * 25, vb_top + 16, 5, BLUE, 1.4)
        # стрибнули в зону провідності
        for i in range(jumped):
            out += minus(cx - 30 + i * 30, cb_top + 16, 5, BLUE, 1.4)
            out += arrow(cx - 30 + i * 30, vb_top + 6, cx - 30 + i * 30, cb_bot + 6, GREEN, 1.4)
        out += text(cx, 378, name, 13, INK, "middle", "bold")
        return out

    s += col(210, "метал: щілини нема", 0, 0)
    s += text(210, 96, "зони стикаються →", 10.5, GREEN, "middle", "bold")
    s += text(210, 110, "електрони вільні", 10.5, GREEN, "middle")
    s += col(440, "напівпровідник: мала щілина", 34, 2)
    s += text(440, 96, "дехто перестрибує", 10.5, "#8a52c0", "middle", "bold")
    s += text(440, 110, "(тепло, світло)", 10.5, GREY, "middle")
    s += col(680, "ізолятор: велика щілина", 90, 0)
    s += text(680, 96, "стрибнути нікому", 10.5, RED, "middle", "bold")
    save("fig-2-8-3-band-gap.svg", s)


# ── Рис. 2.8.4 — діапазон питомого опору ─────────────────────────────────────
def fig28_resistivity_scale():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Питомий опір: найширший діапазон з усіх властивостей", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "від міді до кварцу — близько 24 порядків величини (Ом·м)", 12, GREY, "middle", style="italic")
    x0, x1, ay = 90, 740, 180
    s += line(x0, ay, x1, ay, INK, 2.5)
    # шкала від 10^-8 до 10^16 (24 декади)
    items = [(-8, "срібло, мідь", "10⁻⁸", GREEN),
             (-6, "ніхром", "10⁻⁶", INK),
             (3, "кремній (чистий)", "~10³", "#8a52c0"),
             (10, "скло", "10¹⁰", INK),
             (16, "кварц", "10¹⁶", RED)]
    for e, name, val, col in items:
        x = x0 + (e + 8) / 24.0 * (x1 - x0)
        s += line(x, ay - 7, x, ay + 7, INK, 2)
        s += circle(x, ay, 6, col, col, 1)
        s += text(x, ay - 16, name, 11, col, "middle", "bold")
        s += text(x, ay + 26, val, 11, col, "middle", "bold")
    s += text(x0, ay + 52, "ПРОВІДНИКИ", 11, GREEN, "start", "bold")
    s += text((x0 + x1) / 2, ay + 52, "напівпровідники", 11, "#8a52c0", "middle", "bold")
    s += text(x1, ay + 52, "ІЗОЛЯТОРИ", 11, RED, "end", "bold")
    s += rect(150, 250, W - 300, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 274, "Жодна інша звичайна властивість не змінюється так сильно між матеріалами.", 12, INK, "middle", "bold")
    s += text(W / 2, 294, "Напівпровідники сидять посередині — і їхній опір можна зсувати керовано.", 11.5, GREY, "middle", style="italic")
    save("fig-2-8-4-resistivity-scale.svg", s)


def _burst(cx, cy, r=10, color=RED):
    out = ""
    for a in range(0, 360, 45):
        out += line(cx, cy, cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), color, 1.6)
    return out


def _ion(cx, cy, r=13, jitter=0):
    out = circle(cx, cy, r, "#fde0d6", COPPER, 1.6)
    out += text(cx, cy + 4, "+", 11, COPPER, "middle", "bold")
    if jitter:
        for a in (45, 135, 225, 315):
            out += line(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)),
                        cx + (r + jitter) * math.cos(math.radians(a)), cy + (r + jitter) * math.sin(math.radians(a)),
                        "#caa", 1.2)
    return out


# ── Рис. 2.9.1 — механізм опору: розгін–зіткнення–скидання ───────────────────
def fig29_collision_mechanism():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Опір — це зіткнення: розгін → удар → скидання", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "поле розганяє електрон, та зіткнення з іонами щоразу гасять набутий дрейф", 12, GREY, "middle", style="italic")
    # поле
    s += arrow(120, 100, 700, 100, GREEN, 2)
    s += text(410, 90, "поле E →", 12, GREEN, "middle", "bold")
    # іони
    xs = [180, 320, 460, 600]
    for x in xs:
        s += _ion(x, 250)
    # шлях електрона зі зіткненнями
    path = [(120, 210), (250, 195), (250, 195), (390, 230), (390, 230), (530, 200), (530, 200), (670, 235)]
    pts = [(120, 210), (245, 192), (255, 198), (385, 232), (395, 226), (528, 198), (538, 204), (672, 236)]
    s += polyline(pts, BLUE, 2)
    s += minus(672, 236, 6, BLUE, 1.6)
    for (bx, by) in [(250, 195), (390, 230), (530, 200)]:
        s += _burst(bx, by, 11, RED)
    s += text(180, 300, "розгін", 11, GREEN, "middle", "bold")
    s += text(320, 175, "удар!", 11, RED, "middle", "bold")
    s += text(460, 300, "знову розгін", 11, GREEN, "middle", "bold")
    s += rect(150, 318, W - 300, 36, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 341, "Поле штовхає безперервно, зіткнення гальмують — звідси СТАЛИЙ дрейф і ОПІР.",
              12, INK, "middle", "bold")
    save("fig-2-9-1-collision-mechanism.svg", s)


# ── Рис. 2.9.2 — на чому розсіюються електрони ───────────────────────────────
def fig29_what_scatters():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Розсіюють ВІДХИЛЕННЯ від ідеалу, а не сама решітка", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "досконала холодна решітка електрон пропускає; гальмують коливання й домішки", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # ліва — ідеальна
    s += text(205, 102, "ідеальна холодна решітка", 12.5, GREEN, "middle", "bold")
    for r in range(2):
        for c in range(4):
            s += _ion(110 + c * 60, 170 + r * 60)
    s += arrow(80, 200, 360, 200, BLUE, 2.4)
    s += minus(360, 200, 6, BLUE, 1.6)
    s += text(205, 300, "електрон ковзає вільно", 11.5, INK, "middle", "bold")
    s += text(205, 320, "(низький опір)", 11, GREY, "middle", style="italic")
    # права — реальна
    s += text(615, 102, "реальна решітка", 12.5, RED, "middle", "bold")
    for r in range(2):
        for c in range(4):
            ix = 520 + c * 60
            iy = 170 + r * 60
            if r == 0 and c == 2:
                s += circle(ix, iy, 13, "#e0e8d0", "#7a9a4a", 2)  # домішка
                s += text(ix, iy + 4, "X", 10, "#5a7a2a", "middle", "bold")
            else:
                s += _ion(ix + (3 if (r + c) % 2 else -3), iy, 13, jitter=4)
    # зигзаг розсіювання
    s += polyline([(490, 200), (560, 185), (590, 215), (640, 175), (690, 210), (740, 190)], BLUE, 2)
    s += minus(740, 190, 6, BLUE, 1.6)
    for (bx, by) in [(560, 185), (640, 175)]:
        s += _burst(bx, by, 9, RED)
    s += text(615, 300, "коливання решітки + домішки", 11.5, INK, "middle", "bold")
    s += text(615, 320, "розсіюють електрон (опір)", 11, GREY, "middle", style="italic")
    save("fig-2-9-2-what-scatters.svg", s)


# ── Рис. 2.9.3 — звідки нагрів ───────────────────────────────────────────────
def fig29_heat():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Куди дівається енергія: у тепло", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "поле дає електрону енергію, зіткнення віддає її решітці — та сильніше коливається = нагрів", 11.5, GREY, "middle", style="italic")
    # поле дає енергію
    s += arrow(120, 180, 260, 180, GREEN, 2.6)
    s += text(190, 168, "робота поля", 11, GREEN, "middle", "bold")
    s += minus(290, 180, 8, BLUE, 1.8)
    s += text(290, 158, "електрон набирає", 10.5, INK, "middle")
    s += text(290, 205, "енергію руху", 10.5, INK, "middle")
    # зіткнення з іоном
    s += arrow(312, 180, 400, 180, BLUE, 2.4)
    s += _burst(430, 180, 14, RED)
    s += _ion(430, 180, 16)
    s += text(430, 145, "удар", 11, RED, "middle", "bold")
    # іон гріється
    for a in (200, 230, 320, 350):
        s += line(430 + 18 * math.cos(math.radians(a)), 180 + 18 * math.sin(math.radians(a)),
                  430 + 30 * math.cos(math.radians(a)), 180 + 30 * math.sin(math.radians(a)), "#e08030", 2)
    s += text(560, 175, "→ іон коливається", 12, "#e08030", "start", "bold")
    s += text(560, 195, "сильніше = ТЕПЛО", 12, "#e08030", "start", "bold")
    s += rect(140, 270, W - 280, 60, "#fff3e8", "#e08030", 1.6, 10)
    s += text(W / 2, 294, "Електрична енергія перетворюється на тепло на кожному зіткненні.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 314, "Це джоулеве тепло; скільки саме (I²R) — порахуємо в Розділі 3.", 11.5, GREY, "middle", style="italic")
    save("fig-2-9-3-heat.svg", s)


# ── Рис. 2.9.4 — опір росте з температурою ───────────────────────────────────
def fig29_temperature():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Гарячіше → більше коливань → більший опір", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у металі нагрів розхитує решітку, зіткнень більшає — опір зростає", 12, GREY, "middle", style="italic")
    # холодна
    s += text(180, 100, "холодний метал", 12, BLUE, "middle", "bold")
    for r in range(2):
        for c in range(3):
            s += _ion(120 + c * 60, 150 + r * 55)
    s += arrow(95, 178, 290, 178, BLUE, 2.2)
    s += minus(290, 178, 6, BLUE, 1.6)
    s += text(180, 255, "коливання слабкі →", 11, INK, "middle")
    s += text(180, 273, "зіткнень мало → опір малий", 11, INK, "middle", "bold")
    # гаряча
    s += text(490, 100, "гарячий метал", 12, RED, "middle", "bold")
    for r in range(2):
        for c in range(3):
            s += _ion(430 + c * 60 + (5 if (r + c) % 2 else -5), 150 + r * 55, 13, jitter=6)
    s += polyline([(400, 178), (455, 162), (485, 192), (540, 165), (590, 190)], BLUE, 2)
    s += minus(590, 190, 6, BLUE, 1.6)
    for (bx, by) in [(455, 162), (540, 165)]:
        s += _burst(bx, by, 8, RED)
    s += text(490, 255, "коливання сильні →", 11, INK, "middle")
    s += text(490, 273, "зіткнень багато → опір більший", 11, INK, "middle", "bold")
    # графік R(T)
    gx, gy = 640, 300
    s += arrow(gx, gy, gx + 130, gy, INK, 1.6)
    s += arrow(gx, gy, gx, gy - 90, INK, 1.6)
    s += text(gx + 130, gy + 14, "T", 11, INK, "start", "bold", "italic")
    s += text(gx - 8, gy - 84, "R", 11, INK, "end", "bold", "italic")
    s += line(gx + 6, gy - 12, gx + 120, gy - 78, RED, 2.6)
    s += text(gx + 70, gy - 70, "метал", 10.5, RED, "middle", "bold")
    save("fig-2-9-4-temperature.svg", s)


# ── Рис. 2.10.1 — опір R проти питомого опору ρ ──────────────────────────────
def fig210_R_vs_rho():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Опір R залежить від форми; питомий опір ρ — лише від матеріалу", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "два шматки тієї самої міді мають різний R, але однаковий ρ", 12, GREY, "middle", style="italic")
    # товстий короткий
    s += rect(120, 150, 160, 60, COPPER, "#9c6b48", 2, 6)
    s += text(200, 185, "мідь", 13, "#5a3a26", "middle", "bold")
    s += text(200, 132, "товстий, короткий", 11.5, INK, "middle", "bold")
    s += text(200, 230, "малий R", 13, GREEN, "middle", "bold")
    s += text(200, 250, "ρ = 1.7×10⁻⁸ Ом·м", 11, "#9c6b48", "middle")
    # тонкий довгий
    s += rect(420, 168, 300, 24, COPPER, "#9c6b48", 2, 6)
    s += text(570, 184, "мідь", 12, "#5a3a26", "middle", "bold")
    s += text(570, 150, "тонкий, довгий", 11.5, INK, "middle", "bold")
    s += text(570, 220, "великий R", 13, RED, "middle", "bold")
    s += text(570, 240, "ρ = 1.7×10⁻⁸ Ом·м (той самий!)", 11, "#9c6b48", "middle")
    s += rect(120, 290, W - 240, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 312, "ρ — це «характер» матеріалу (як густина): однаковий для будь-якого шматка міді.", 12, INK, "middle", "bold")
    s += text(W / 2, 332, "R — це опір конкретної деталі: залежить і від ρ, і від довжини та перерізу (R = ρ·L/A, Розд.3).",
              11, GREY, "middle", style="italic")
    save("fig-2-10-1-r-vs-rho.svg", s)


# ── Рис. 2.10.2 — таблиця питомих опорів ─────────────────────────────────────
def fig210_resistivity_table():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Питомий опір поширених матеріалів (20 °C)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "менший ρ — кращий провідник; одиниця — Ом·метр", 12, GREY, "middle", style="italic")
    rows = [
        ("срібло", "1.6 × 10⁻⁸", GREEN, "найкращий провідник, дорогий"),
        ("мідь", "1.7 × 10⁻⁸", GREEN, "стандарт для дротів"),
        ("золото", "2.2 × 10⁻⁸", GREEN, "не кородує — контакти"),
        ("алюміній", "2.7 × 10⁻⁸", GREEN, "легкий, дешевий — ЛЕП"),
        ("залізо", "1.0 × 10⁻⁷", INK, "гірше за мідь"),
        ("ніхром", "1.1 × 10⁻⁶", "#e08030", "сплав для нагрівачів"),
        ("графіт", "~1 × 10⁻⁵", "#e08030", "провідний неметал"),
    ]
    s += line(80, 92, W - 80, 92, "#ddd", 1.4)
    s += text(95, 84, "матеріал", 11, GREY, "start", "bold")
    s += text(330, 84, "ρ, Ом·м", 11, GREY, "middle", "bold")
    s += text(470, 84, "де застосовують", 11, GREY, "start", "bold")
    y = 118
    for name, val, col, note in rows:
        s += circle(95, y - 4, 5, col, col, 1)
        s += text(110, y, name, 14, col, "start", "bold")
        s += text(330, y, val, 13, INK, "middle", "bold")
        s += text(470, y, note, 12, GREY, "start")
        s += line(80, y + 12, W - 80, y + 12, "#eee", 1)
        y += 38
    s += text(W / 2, H - 14, "Для контрасту: скло ~10¹⁰, кварц ~10¹⁶ Ом·м — на 18 порядків більше (§2.8).",
              11.5, RED, "middle", style="italic")
    save("fig-2-10-2-resistivity-table.svg", s)


# ── Рис. 2.10.3 — залежність від температури (PTC vs NTC) ────────────────────
def fig210_tempco():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Вплив температури: метал ↑, напівпровідник ↓", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у металі ρ росте з нагрівом (PTC), у напівпровіднику — падає (NTC)", 12, GREY, "middle", style="italic")
    gx0, gx1, gy0, gy1 = 110, 700, 320, 110
    s += arrow(gx0, gy0, gx1 + 10, gy0, INK, 2)
    s += arrow(gx0, gy0, gx0, gy1 - 6, INK, 2)
    s += text(gx1 + 14, gy0 + 4, "T", 13, INK, "start", "bold", "italic")
    s += text(gx0 - 12, gy1, "ρ", 13, INK, "end", "bold", "italic")
    # метал — лінійно вгору
    s += line(gx0 + 20, gy0 - 30, gx1 - 20, gy1 + 30, RED, 2.8)
    s += text(gx1 - 40, gy1 + 50, "метал (PTC, α > 0)", 12.5, RED, "end", "bold")
    s += text(gx1 - 40, gy1 + 68, "ρ = ρ₀[1 + α(T−T₀)]", 11.5, GREY, "end")
    # напівпровідник — спадна крива
    pts = [(gx0 + 20 + i * 6, gy1 + 20 + 200 * math.exp(-i / 18.0)) for i in range(0, 95)]
    s += polyline(pts, "#8a52c0", 2.8)
    s += text(gx0 + 180, gy0 - 26, "напівпровідник (NTC, α < 0)", 12.5, "#8a52c0", "start", "bold")
    s += rect(120, 340, W - 240, 30, "#f4f7f4", GREEN, 1.4, 8)
    s += text(W / 2, 360, "Мідь: ~+0.4% на кожен °C. Терморезистор NTC: різко падає — звідси давачі температури.",
              11.5, INK, "middle", "bold")
    save("fig-2-10-3-tempco.svg", s)


# ── Рис. 2.10.4 — кидок струму лампи розжарення ──────────────────────────────
def fig210_inrush():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Практика PTC: кидок струму лампи розжарення", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "холодна нитка має малий опір → у перші миті струм великий, тоді спадає", 12, GREY, "middle", style="italic")
    # стани нитки
    s += circle(170, 160, 30, "#eef2f5", "#9aa7b0", 2.2)
    s += text(170, 165, "❄", 18, BLUE, "middle")
    s += text(170, 210, "холодна нитка", 11.5, BLUE, "middle", "bold")
    s += text(170, 228, "малий R", 11, INK, "middle")
    s += arrow(215, 160, 285, 160, INK, 2.4)
    s += text(250, 145, "увімкнули", 10.5, INK, "middle", "bold")
    s += circle(330, 160, 30, "#fff2b0", "#caa23a", 2.4)
    s += text(330, 165, "☀", 18, "#e08030", "middle")
    s += text(330, 210, "гаряча нитка", 11.5, RED, "middle", "bold")
    s += text(330, 228, "великий R", 11, INK, "middle")
    # графік I(t)
    gx0, gx1, gy0, gy1 = 440, 740, 250, 110
    s += arrow(gx0, gy0, gx1 + 10, gy0, INK, 1.8)
    s += arrow(gx0, gy0, gx0, gy1 - 6, INK, 1.8)
    s += text(gx1 + 12, gy0 + 14, "t", 12, INK, "start", "bold", "italic")
    s += text(gx0 - 8, gy1, "I", 12, INK, "end", "bold", "italic")
    pts = [(gx0 + 4, gy1 + 10)]
    for i in range(1, 100):
        t = i / 99.0
        I = 0.25 + 0.75 * math.exp(-t * 5)
        pts.append((gx0 + 4 + t * (gx1 - gx0 - 8), gy0 - I * (gy0 - gy1)))
    s += polyline(pts, RED, 2.8)
    s += text(gx0 + 30, gy1 + 4, "кидок", 11, RED, "start", "bold")
    s += line(gx0, gy0 - 0.25 * (gy0 - gy1), gx1, gy0 - 0.25 * (gy0 - gy1), GREY, 1.2, "4 3")
    s += text(gx1 - 10, gy0 - 0.25 * (gy0 - gy1) - 6, "робочий струм", 10.5, GREY, "end", style="italic")
    s += text(W / 2, H - 12, "Тому лампи розжарення часто перегорають саме при ввімкненні — від кидка струму.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-10-4-inrush.svg", s)


def _carrier(cx, cy, sign, r=12):
    col = RED if sign == "+" else BLUE
    fill = "#fdf4f4" if sign == "+" else "#f3f5fd"
    out = circle(cx, cy, r, fill, col, 2)
    out += (plus(cx, cy, r * 0.5, col, 1.8) if sign == "+" else minus(cx, cy, r * 0.5, col, 1.8))
    return out


# ── Рис. 2.11.1 — зоопарк носіїв заряду ──────────────────────────────────────
def fig211_carriers_zoo():
    W, H = 840, 350
    s = header(W, H)
    s += text(W / 2, 34, "Струм — це рух заряду, хоч би що його несло", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "носієм може бути не лише електрон: іони, дірки, суміш — усе дає струм", 12, GREY, "middle", style="italic")

    def box(x0, title, carriers):
        out = rect(x0, 90, 195, 200, "#fafafa", "#ddd", 1.6, 12)
        out += text(x0 + 97, 116, title, 13.5, INK, "middle", "bold")
        cy = 175
        for i, (sym) in enumerate(carriers):
            cx = x0 + 50 + (i % 3) * 50
            cyy = cy + (i // 3) * 44
            if sym == "e":
                out += minus(cx, cyy, 10, BLUE, 1.8)
            elif sym == "+":
                out += _carrier(cx, cyy, "+", 11)
            elif sym == "-":
                out += _carrier(cx, cyy, "-", 11)
            elif sym == "h":
                out += circle(cx, cyy, 10, "none", RED, 2)
                out += plus(cx, cyy, 5, RED, 1.4)
        return out

    s += box(20, "МЕТАЛ", ["e", "e", "e", "e", "e"])
    s += text(117, 270, "вільні електрони (−)", 11, BLUE, "middle", "bold")
    s += box(232, "ЕЛЕКТРОЛІТ", ["+", "-", "+", "-", "+", "-"])
    s += text(330, 270, "іони + і −", 11, INK, "middle", "bold")
    s += box(444, "ПЛАЗМА", ["e", "+", "e", "+", "e", "+"])
    s += text(542, 270, "електрони + іони", 11, INK, "middle", "bold")
    s += box(656, "НАПІВПРОВІДНИК", ["e", "h", "e", "h"])
    s += text(754, 270, "електрони + дірки", 11, INK, "middle", "bold")
    s += text(W / 2, 320, "Скрізь — той самий струм (Кл/с), просто заряд несуть різні «вантажники».",
              11.5, GREY, "middle", style="italic")
    save("fig-2-11-1-carriers-zoo.svg", s)


# ── Рис. 2.11.2 — іонна провідність в електроліті ────────────────────────────
def fig211_electrolyte():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Електроліт: струм несуть іони (обидва знаки)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "сіль у воді розпадається на іони; + пливуть до «−», − до «+» — обидва дають струм", 11.5, GREY, "middle", style="italic")
    # посудина
    s += rect(180, 130, 460, 200, "#dceaf2", "#7aa0b5", 2, 8)
    # електроди
    s += rect(210, 110, 24, 200, "#fbecec", RED, 2.4, 4)
    s += text(222, 100, "+ анод", 11, RED, "middle", "bold")
    s += rect(586, 110, 24, 200, "#e9eefb", BLUE, 2.4, 4)
    s += text(598, 100, "− катод", 11, BLUE, "middle", "bold")
    # іони
    for (ix, iy) in [(320, 180), (420, 210), (500, 175), (360, 250), (470, 270)]:
        s += _carrier(ix, iy, "+", 12)
        s += arrow(ix + 14, iy, ix + 44, iy, RED, 1.6)  # + до катода (праворуч)
    for (ix, iy) in [(370, 200), (450, 240), (520, 215), (320, 290)]:
        s += _carrier(ix, iy, "-", 12)
        s += arrow(ix - 14, iy, ix - 44, iy, BLUE, 1.6)  # − до анода (ліворуч)
    s += text(410, 165, "Na⁺ →", 11, RED, "middle", "bold")
    s += text(410, 320, "← Cl⁻", 11, BLUE, "middle", "bold")
    # зовнішнє коло
    s += line(222, 110, 222, 80, INK, 2)
    s += line(598, 110, 598, 80, INK, 2)
    s += line(222, 80, 598, 80, INK, 2)
    s += text(410, 74, "(зовні струм несуть електрони по дроту)", 11, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "Чиста вода майже не проводить (іонів мало); сіль, кислота чи луг — додають іони.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-11-2-electrolyte.svg", s)


# ── Рис. 2.11.3 — плазма ─────────────────────────────────────────────────────
def fig211_plasma():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Плазма: іонізований газ — «четвертий стан»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "газ, у якому електрони відірвані від атомів — проводить і електронами, і іонами", 11.5, GREY, "middle", style="italic")
    # розрядна трубка
    s += rect(150, 140, 520, 90, "#fbe8ff", "#b06fc0", 2.4, 45)
    s += line(150, 185, 120, 185, INK, 3)
    s += line(670, 185, 700, 185, INK, 3)
    s += text(110, 185, "+", 14, RED, "end", "bold")
    s += text(710, 185, "−", 14, BLUE, "start", "bold")
    # суміш носіїв
    spots = [(220, 170), (290, 200), (360, 165), (430, 205), (500, 170), (560, 200),
             (255, 205), (325, 168), (395, 200), (465, 168), (530, 205), (600, 170)]
    for i, (ix, iy) in enumerate(spots):
        if i % 2 == 0:
            s += minus(ix, iy, 7, BLUE, 1.6)
        else:
            s += _carrier(ix, iy, "+", 9)
    s += text(410, 130, "вільні електрони (−) + іони (+) разом", 12, INK, "middle", "bold")
    # приклади
    s += rect(120, 270, W - 240, 56, "#fff7ef", "#c89b5a", 1.6, 10)
    s += text(W / 2, 293, "Де буває: блискавка · неонова й люмінесцентна лампа · електрична дуга · іскра · полум'я · Сонце.",
              12, INK, "middle", "bold")
    s += text(W / 2, 313, "Усюди газ іонізовано — і він проводить струм.", 11, GREY, "middle", style="italic")
    save("fig-2-11-3-plasma.svg", s)


# ── Рис. 2.11.4 — тіло як іонний провідник ───────────────────────────────────
def fig211_body():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Тіло людини проводить — іонами солоної рідини", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "усередині ми — солона вода; шкіра суха має великий опір, мокра — малий", 11.5, GREY, "middle", style="italic")
    # силует
    cx = 410
    s += circle(cx, 130, 24, "#fde7df", "#caa", 2)  # голова
    s += rect(cx - 34, 156, 68, 110, "#fde7df", "#caa", 2, 14)  # тулуб
    s += line(cx - 34, 175, cx - 130, 215, "#fde7df", 14)  # ліва рука
    s += line(cx + 34, 175, cx + 130, 215, "#fde7df", 14)  # права рука
    s += line(cx - 18, 266, cx - 30, 340, "#fde7df", 14)  # ноги
    s += line(cx + 18, 266, cx + 30, 340, "#fde7df", 14)
    # іони всередині
    for (ix, iy) in [(cx - 12, 190), (cx + 12, 210), (cx, 230), (cx - 10, 250)]:
        s += _carrier(ix, iy, "+", 8)
        s += _carrier(ix + 22, iy + 8, "-", 8)
    s += text(cx, 295, "усередині — іони (солона рідина)", 10.5, INK, "middle", "bold")
    # шлях струму
    s += arrow(cx - 130, 215, cx - 60, 200, RED, 2.6)
    s += arrow(cx + 60, 200, cx + 130, 215, RED, 2.6)
    s += text(cx - 130, 240, "вхід", 11, RED, "middle", "bold")
    s += text(cx + 130, 240, "вихід", 11, RED, "middle", "bold")
    s += text(cx, 360, "струм крізь тіло — небезпечний (§2.13)", 11.5, RED, "middle", "bold")
    # опір шкіри
    s += rect(60, 130, 170, 90, "#f4f7f4", INK, 1.4, 8)
    s += text(145, 152, "опір шкіри", 12, INK, "middle", "bold")
    s += text(145, 174, "суха: ~100 кОм", 11.5, GREEN, "middle")
    s += text(145, 194, "мокра: ~1 кОм", 11.5, RED, "middle", "bold")
    s += text(145, 212, "(тому й небезпечно)", 10, GREY, "middle", style="italic")
    s += rect(W - 230, 130, 170, 90, "#f4f7f4", INK, 1.4, 8)
    s += text(W - 145, 152, "усередині —", 12, INK, "middle", "bold")
    s += text(W - 145, 174, "добрий провідник", 11.5, INK, "middle")
    s += text(W - 145, 194, "(іони крові,", 11, GREY, "middle")
    s += text(W - 145, 210, "тканин)", 11, GREY, "middle")
    save("fig-2-11-4-body.svg", s)


# ── Рис. 2.11і.1 — дисоціація: іони існують до струму ─────────────────────────
def fig_dissociation():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Зухвала ідея Арреніуса: іони існують у розчині ще ДО струму", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "сіль розпадається на іони вже від розчинення; струм їх не створює, а лише рухає", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # ліворуч — стара думка
    s += text(205, 102, "стара думка", 13, RED, "middle", "bold")
    for (x, y) in [(140, 170), (250, 200), (180, 250), (290, 160)]:
        s += circle(x, y, 13, "#eee", "#999", 1.8)
        s += circle(x + 22, y, 13, "#e0e8d0", "#7a9a4a", 1.8)
        s += text(x + 11, y - 22, "NaCl", 10, INK, "middle", "bold")
    s += text(205, 300, "молекули цілі, поки не пройде струм", 11, INK, "middle", "bold")
    s += text(205, 320, "(струм нібито «розриває» їх)", 10.5, GREY, "middle", style="italic")
    # праворуч — Арреніус
    s += text(615, 102, "Арреніус", 13, GREEN, "middle", "bold")
    for (x, y) in [(540, 165), (640, 200), (590, 255), (690, 165)]:
        s += _carrier(x, y, "+", 12)
        s += text(x, y - 20, "Na⁺", 9.5, RED, "middle", "bold")
    for (x, y) in [(580, 200), (680, 250), (520, 240), (650, 290)]:
        s += _carrier(x, y, "-", 12)
        s += text(x, y - 20, "Cl⁻", 9.5, BLUE, "middle", "bold")
    s += text(615, 320, "уже розділені — струм лише рухає їх", 11, INK, "middle", "bold")
    save("fig-2-11i-1-dissociation.svg", s)


# ── Рис. 2.11і.2 — від найнижчої оцінки до Нобеля ────────────────────────────
def fig_thesis_arc():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 34, "Ідея, з якої сміялися, дістала Нобеля", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "дисертацію 1884 року ледь зарахували — а за 19 років увінчали премією", 12, GREY, "middle", style="italic")
    ty = 170
    s += line(110, ty, 710, ty, GREY, 2.5)
    nodes = [("1884", "дисертація —", "найнижчий бал", RED),
             ("1880-ті", "хіміки", "глузують", GREY),
             ("1890-ті", "Оствальд, вант-Гофф —", "підтримка", INK),
             ("1903", "Нобелівська премія", "з хімії", GREEN)]
    for i, (yr, a, b, col) in enumerate(nodes):
        x = 150 + i * 187
        s += circle(x, ty, 7, "#fff", col, 2.6)
        s += text(x, ty - 16, yr, 13, col, "middle", "bold")
        s += text(x, ty + 26, a, 11, INK, "middle")
        s += text(x, ty + 42, b, 11, col, "middle", "bold")
    s += text(W / 2, H - 16, "Урок: правильна, але незвична ідея часто мусить перечекати ціле покоління скептиків.",
              12, GREY, "middle", style="italic")
    save("fig-2-11i-2-thesis-arc.svg", s)


# ── Рис. 2.11і.3 — іони всюди + полімат Арреніус ─────────────────────────────
def fig_arrhenius_legacy():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Спадок: іони всюди — і не тільки", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "поняття іона стало основою хімії, електрохімії та біології", 12, GREY, "middle", style="italic")
    cx, cy = 250, 200
    s += circle(cx, cy, 44, "#eef5ff", "#7a87a8", 2.4)
    s += text(cx, cy + 6, "ІОНИ", 16, INK, "middle", "bold")
    spokes = [("батареї", -90), ("нерви, ЕКГ", -30), ("pH, кислоти", 30),
              ("гальваніка", 90), ("розчини", 150), ("осмос", 210)]
    for name, a in spokes:
        ex = cx + 130 * math.cos(math.radians(a))
        ey = cy + 110 * math.sin(math.radians(a))
        s += line(cx + 44 * math.cos(math.radians(a)), cy + 44 * math.sin(math.radians(a)),
                  ex - 18 * math.cos(math.radians(a)), ey - 12 * math.sin(math.radians(a)), GREY, 1.4)
        s += text(ex, ey, name, 11, INK, "middle", "bold")
    # полімат
    s += rect(470, 110, 300, 180, "#f4f7f4", GREEN, 1.6, 12)
    s += text(620, 136, "Арреніус-полімат", 14, GREEN, "middle", "bold")
    s += text(486, 166, "• рівняння Арреніуса:", 12, INK, "start", "bold")
    s += text(498, 186, "швидкість реакцій від температури", 11, GREY, "start")
    s += text(486, 214, "• перше передбачення", 12, INK, "start", "bold")
    s += text(498, 234, "парникового ефекту (CO₂, 1896)", 11, GREY, "start")
    s += text(486, 262, "• Нобель з хімії, 1903", 12, INK, "start", "bold")
    save("fig-2-11i-3-legacy.svg", s)


def _sine(gx0, gx1, gymid, amp, cycles, color, w=2.6, phase=0.0):
    pts = []
    n = 180
    for i in range(n + 1):
        x = gx0 + (gx1 - gx0) * i / n
        y = gymid - amp * math.sin(2 * math.pi * cycles * i / n + phase)
        pts.append((x, y))
    return polyline(pts, color, w)


# ── Рис. 2.12.1 — DC проти AC: напрямок руху ─────────────────────────────────
def fig212_dc_vs_ac_wave():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Постійний (DC) і змінний (AC) струм", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "DC тече весь час в один бік; AC періодично МІНЯЄ напрямок", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # DC ліворуч
    s += text(205, 100, "DC — постійний", 13, GREEN, "middle", "bold")
    s += arrow(70, 160, 350, 160, INK, 1.6)
    s += arrow(70, 160, 70, 120, INK, 1.6)
    s += text(60, 124, "I", 11, INK, "end", "bold", "italic")
    s += text(355, 174, "t", 11, INK, "start", "bold", "italic")
    s += line(80, 140, 345, 140, RED, 2.8)
    s += text(210, 130, "стала лінія", 11, RED, "middle", "bold")
    s += minus(150, 230, 8, BLUE, 1.8)
    s += arrow(165, 230, 260, 230, BLUE, 2.4)
    s += text(210, 255, "електрон дрейфує в ОДИН бік", 11, INK, "middle", "bold")
    s += text(205, 300, "батарея, USB, сонячна панель, чипи", 11, GREY, "middle", style="italic")
    # AC праворуч
    s += text(615, 100, "AC — змінний", 13, "#8a52c0", "middle", "bold")
    s += arrow(480, 160, 760, 160, INK, 1.6)
    s += arrow(480, 160, 480, 120, INK, 1.6)
    s += text(470, 124, "I", 11, INK, "end", "bold", "italic")
    s += text(765, 174, "t", 11, INK, "start", "bold", "italic")
    s += _sine(490, 750, 160, 28, 2, "#8a52c0", 2.8)
    s += minus(615, 230, 8, BLUE, 1.8)
    s += arrow(630, 230, 690, 230, BLUE, 2)
    s += arrow(600, 230, 540, 230, BLUE, 2)
    s += text(615, 255, "електрон ГОЙДАЄТЬСЯ туди-сюди", 11, INK, "middle", "bold")
    s += text(615, 300, "розетка, мережа, передача, двигуни", 11, GREY, "middle", style="italic")
    save("fig-2-12-1-dc-vs-ac.svg", s)


# ── Рис. 2.12.2 — частота й період ───────────────────────────────────────────
def fig212_frequency_period():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Синусоїда: амплітуда, період, частота", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "частота f — скільки повних коливань за секунду (Гц); період T = 1/f", 12, GREY, "middle", style="italic")
    gx0, gx1, gy = 110, 740, 190
    s += line(gx0, gy, gx1, gy, GREY, 1.4, "4 3")
    s += arrow(gx0, gy, gx0, 110, INK, 1.6)
    s += text(gx0 - 10, 116, "V", 12, INK, "end", "bold", "italic")
    s += _sine(gx0, gx1, gy, 60, 2.5, "#8a52c0", 2.8)
    # амплітуда
    s += line(gx0 + 63, gy, gx0 + 63, gy - 60, RED, 1.4, "4 3")
    s += arrow(gx0 + 63, gy - 6, gx0 + 63, gy - 58, RED, 1.6)
    s += text(gx0 + 70, gy - 30, "амплітуда (пік)", 11, RED, "start", "bold")
    # період
    py = gy + 70
    s += line(gx0, py, gx0 + 252, py, INK, 1.6)
    s += line(gx0, py - 6, gx0, py + 6, INK, 1.6)
    s += line(gx0 + 252, py - 6, gx0 + 252, py + 6, INK, 1.6)
    s += text(gx0 + 126, py + 18, "період T (одне коливання)", 11.5, INK, "middle", "bold")
    s += rect(150, 290, W - 300, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 312, "Мережа: 50 Гц (Україна, Європа) або 60 Гц (США).", 12.5, INK, "middle", "bold")
    s += text(W / 2, 330, "50 Гц → T = 1/50 = 0.02 с = 20 мс на одне коливання.", 11.5, GREY, "middle", style="italic")
    save("fig-2-12-2-frequency-period.svg", s)


# ── Рис. 2.12.3 — діюче значення (RMS) ───────────────────────────────────────
def fig212_rms():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Діюче значення (RMS): «скільки це в DC»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "RMS — таке DC-значення, що гріло б так само; для синуса RMS ≈ 0.707 × пік", 12, GREY, "middle", style="italic")
    gx0, gx1, gy = 110, 700, 190
    s += line(gx0, gy, gx1, gy, GREY, 1.2, "3 3")
    s += _sine(gx0, gx1, gy, 80, 2, "#8a52c0", 2.6)
    # пік
    s += line(gx0, gy - 80, gx1, gy - 80, RED, 1.4, "5 4")
    s += text(gx1 + 4, gy - 80, "пік ≈ 325 В", 11.5, RED, "start", "bold")
    # RMS
    s += line(gx0, gy - 57, gx1, gy - 57, GREEN, 2)
    s += text(gx1 + 4, gy - 54, "RMS = 230 В", 11.5, GREEN, "start", "bold")
    s += text(gx0 + 20, gy - 64, "діюче значення", 10.5, GREEN, "start", style="italic")
    s += rect(150, 285, W - 300, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 308, "«230 В» у розетці — це RMS, а не пік. Мультиметр у режимі AC показує саме RMS.",
              12, INK, "middle", "bold")
    s += text(W / 2, 328, "Пік = RMS × √2 = 230 × 1.414 ≈ 325 В.", 11.5, GREY, "middle", style="italic")
    save("fig-2-12-3-rms.svg", s)


# ── Рис. 2.12.4 — чому AC: трансформація й мережа ────────────────────────────
def fig212_why_ac_transform():
    W, H = 840, 360
    s = header(W, H)
    s += text(W / 2, 34, "Чому AC: її легко трансформувати", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "високу напругу — для далекої передачі (малі втрати), низьку — для безпечного вжитку", 11.5, GREY, "middle", style="italic")
    y = 180

    def block(x, w, h, fill, stroke, label, sub):
        out = rect(x, y - h / 2, w, h, fill, stroke, 2, 8)
        out += text(x + w / 2, y - 4, label, 12, INK, "middle", "bold")
        out += text(x + w / 2, y + 14, sub, 10, GREY, "middle")
        return out

    s += block(40, 80, 70, "#fff7ef", "#c89b5a", "генератор", "AC, ~кВ")
    s += line(120, y, 165, y, INK, 2)
    s += block(165, 70, 70, "#f3eefb", "#8a52c0", "↑ підвищ.", "трансф.")
    s += line(235, y, 280, y, RED, 2.4)
    # лінія передачі (опори)
    s += text(360, y - 36, "ЛЕП: висока U, малий I", 11, RED, "middle", "bold")
    s += line(280, y, 480, y, RED, 2.4)
    for tx in (320, 380, 440):
        s += line(tx, y, tx - 8, y - 18, "#caa", 1.4)
        s += line(tx, y, tx + 8, y - 18, "#caa", 1.4)
        s += line(tx, y, tx, y - 26, "#caa", 1.4)
    s += line(480, y, 525, y, INK, 2)
    s += block(525, 70, 70, "#f3eefb", "#8a52c0", "↓ знижув.", "трансф.")
    s += line(595, y, 640, y, INK, 2)
    s += block(640, 90, 70, "#eef7f0", GREEN, "оселя", "AC, 230 В")
    s += rect(120, 285, W - 240, 56, "#fff7ef", "#c89b5a", 1.6, 10)
    s += text(W / 2, 308, "DC так просто не трансформуєш — тому мережа стала змінною. Це й вирішило «війну струмів».",
              12, INK, "middle", "bold")
    s += text(W / 2, 328, "У самій електроніці працює DC: адаптер перетворює мережеву AC на потрібну DC.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-12-4-why-ac.svg", s)


# ── Рис. 2.12і.1 — чому AC побила DC (втрати передачі) ───────────────────────
def fig_dc_problem():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Технічне серце суперечки: втрати в дротах", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "втрати на нагрів = I²R; вища напруга → менший струм → менші втрати на передачу", 11.5, GREY, "middle", style="italic")
    # DC — низька напруга
    s += text(120, 110, "DC Едісона: низька напруга", 12.5, RED, "start", "bold")
    s += rect(80, 130, 70, 50, "#fff7ef", "#c89b5a", 2, 6)
    s += text(115, 160, "станція", 10, INK, "middle", "bold")
    s += line(150, 155, 300, 155, RED, 4)
    s += text(225, 142, "великий I → I²R", 10.5, RED, "middle", "bold")
    s += _lamp(320, 155, 14)
    s += line(340, 155, 380, 155, INK, 1.5)
    s += f'<path d="M 385,150 l 4,10 l -8,0 z" fill="none" stroke="{RED}" stroke-width="1.5"/>\n'
    s += text(470, 155, "далі не дотягнути →", 11, RED, "start", "bold")
    s += text(470, 173, "станція щокілометра", 10.5, GREY, "start", style="italic")
    # AC — трансформація
    s += text(120, 240, "AC: трансформація", 12.5, GREEN, "start", "bold")
    s += rect(80, 260, 64, 46, "#fff7ef", "#c89b5a", 2, 6)
    s += text(112, 287, "станція", 9.5, INK, "middle", "bold")
    s += rect(150, 262, 50, 42, "#f3eefb", "#8a52c0", 2, 5)
    s += text(175, 287, "↑", 16, "#8a52c0", "middle", "bold")
    s += line(200, 283, 560, 283, GREEN, 3)
    s += text(380, 270, "висока U, малий I → крихітні втрати", 10.5, GREEN, "middle", "bold")
    s += rect(560, 262, 50, 42, "#f3eefb", "#8a52c0", 2, 5)
    s += text(585, 287, "↓", 16, "#8a52c0", "middle", "bold")
    s += _lamp(660, 283, 14)
    s += text(720, 283, "на сотні км", 11, GREEN, "start", "bold")
    s += rect(120, 330, W - 240, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 352, "DC у ті часи не вміли підвищувати в напрузі — тож він застрягав біля станції.",
              12, INK, "middle", "bold")
    s += text(W / 2, 370, "AC + трансформатор пускали струм на далекі відстані. Це й вирішило все.",
              11, GREY, "middle", style="italic")
    save("fig-2-12i-1-dc-problem.svg", s)


# ── Рис. 2.12і.2 — учасники ──────────────────────────────────────────────────
def fig_war_players():
    W, H = 840, 360
    s = header(W, H)
    s += text(W / 2, 34, "Троє проти течії: DC проти AC", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "Едісон бився за постійний струм; Вестінгауз і Тесла — за змінний", 12, GREY, "middle", style="italic")

    def col(x, name, side, scol, lines):
        out = rect(x, 86, 250, 230, "#fafafa", scol, 2, 12)
        out += text(x + 125, 114, name, 15, scol, "middle", "bold")
        out += text(x + 125, 136, side, 12, INK, "middle", "bold")
        yy = 166
        for ln in lines:
            out += text(x + 16, yy, ln, 11.5, INK, "start")
            yy += 26
        return out

    s += col(20, "ЕДІСОН", "за DC", RED,
             ["• практична лампа", "• перша мережа (1882)", "• бізнес на DC", "• брудна PR-війна:", "  лякав «смертельним AC»"])
    s += col(295, "ВЕСТІНГАУЗ", "за AC", GREEN,
             ["• промисловець", "• скупив патенти на AC", "• поставив капітал", "  на змінний струм", "• витримав тиск"])
    s += col(570, "ТЕСЛА", "за AC", "#8a52c0",
             ["• асинхронний двигун", "• багатофазна система", "  (1888)", "• технічне СЕРЦЕ AC", "• геній, помер у бідності"])
    save("fig-2-12i-2-players.svg", s)


# ── Рис. 2.12і.3 — перебіг і підсумок ────────────────────────────────────────
def fig_war_outcome():
    W, H = 840, 340
    s = header(W, H)
    s += text(W / 2, 34, "Як вирішилося — і несподіваний реванш DC", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "AC переміг публічно й технічно; та сьогодні DC частково повертається", 12, GREY, "middle", style="italic")
    ty = 160
    s += line(90, ty, 750, ty, GREY, 2.5)
    nodes = [("1882", "Едісон: перша", "DC-станція", RED),
             ("1888", "Тесла:", "двигун AC", "#8a52c0"),
             ("кін. 1880-х", "PR-війна,", "електричний стілець", GREY),
             ("1893", "Чиказька виставка —", "сяє на AC", GREEN),
             ("1895", "Ніагара → Буффало", "AC на 30 км — перемога", GREEN)]
    n = len(nodes)
    for i, (yr, a, b, col) in enumerate(nodes):
        x = 130 + i * 150
        s += circle(x, ty, 7, "#fff", col, 2.6)
        s += text(x, ty - 16, yr, 12, col, "middle", "bold")
        s += text(x, ty + 26, a, 10, INK, "middle")
        s += text(x, ty + 41, b, 10, col, "middle", "bold")
    s += rect(120, 270, W - 240, 50, "#fff7ef", "#c89b5a", 1.6, 10)
    s += text(W / 2, 292, "AC став світовим стандартом мереж. Та з сучасною силовою електронікою",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 310, "повертається HVDC (постійний струм) для наддовгих ліній — реванш на новому рівні.",
              11, GREY, "middle", style="italic")
    save("fig-2-12i-3-outcome.svg", s)


def _person(cx, cy, scale=1.0, col="#caa", fill="#fde7df"):
    h = 18 * scale
    out = circle(cx, cy - 60 * scale, h, fill, col, 2)
    out += rect(cx - 26 * scale, cy - 40 * scale, 52 * scale, 80 * scale, fill, col, 2, 12)
    out += line(cx - 26 * scale, cy - 26 * scale, cx - 100 * scale, cy + 10 * scale, fill, 11 * scale)
    out += line(cx + 26 * scale, cy - 26 * scale, cx + 100 * scale, cy + 10 * scale, fill, 11 * scale)
    out += line(cx - 14 * scale, cy + 40 * scale, cx - 24 * scale, cy + 110 * scale, fill, 11 * scale)
    out += line(cx + 14 * scale, cy + 40 * scale, cx + 24 * scale, cy + 110 * scale, fill, 11 * scale)
    return out


# ── Рис. 2.13.1 — драбина небезпечних струмів ────────────────────────────────
def fig213_current_thresholds():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 34, "Небезпечний саме СТРУМ через тіло (~мА, AC 50 Гц)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "не «скільки вольтів», а скільки міліампер пройшло крізь людину", 12, GREY, "middle", style="italic")
    x = 330
    s += line(x, 92, x, 410, INK, 2.5)
    items = [
        ("~ 1 мА", "ледь відчутно", GREEN),
        ("~ 5 мА", "боляче", GREEN),
        ("10–20 мА", "«не відпустити» — м'язи зводить", "#e08030"),
        ("30–50 мА", "ускладнене дихання", RED),
        ("100–200 мА", "ФІБРИЛЯЦІЯ серця — смертельно", RED),
        ("> 1 А", "важкі опіки, зупинка серця", RED),
    ]
    n = len(items)
    for i, (v, what, col) in enumerate(items):
        y = 112 + (410 - 112) * i / (n - 1)
        s += line(x - 7, y, x + 7, y, INK, 2)
        s += text(x - 16, y + 5, v, 14, col, "end", "bold")
        s += text(x + 18, y + 5, what, 13, col, "start", "bold")
    s += text(x - 16, 98, "безпечно", 10.5, GREEN, "end", style="italic")
    s += text(x - 16, 426, "смертельно", 10.5, RED, "end", "bold")
    save("fig-2-13-1-current-thresholds.svg", s)


# ── Рис. 2.13.2 — I = V/R: суха vs мокра шкіра ───────────────────────────────
def fig213_ohm_skin():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Та сама напруга — різний струм: вирішує опір шкіри", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "I = V/R; при 230 В суха шкіра рятує, мокра — вбиває", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # суха
    s += text(205, 102, "СУХА шкіра", 13.5, GREEN, "middle", "bold")
    s += text(205, 134, "R ≈ 50 кОм", 13, INK, "middle", "bold")
    s += text(205, 168, "I = 230 / 50000", 12.5, INK, "middle")
    s += rect(95, 188, 220, 50, "#eef7f0", GREEN, 2, 10)
    s += text(205, 220, "≈ 4.6 мА", 18, GREEN, "middle", "bold")
    s += text(205, 270, "боляче, та зазвичай виживеш", 12, INK, "middle", "bold")
    # мокра
    s += text(615, 102, "МОКРА шкіра", 13.5, RED, "middle", "bold")
    s += text(615, 134, "R ≈ 1 кОм", 13, INK, "middle", "bold")
    s += text(615, 168, "I = 230 / 1000", 12.5, INK, "middle")
    s += rect(505, 188, 220, 50, "#fdeeee", RED, 2, 10)
    s += text(615, 220, "≈ 230 мА", 18, RED, "middle", "bold")
    s += text(615, 270, "далеко за межею фібриляції — смертельно", 11.5, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Ось чому «скільки вольтів небезпечно» — питання неповне: усе вирішує струм, а його задає опір.",
              11.5, GREY, "middle", style="italic")
    save("fig-2-13-2-ohm-skin.svg", s)


# ── Рис. 2.13.3 — шлях струму й правило однієї руки ──────────────────────────
def fig213_path():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Шлях вирішує: крізь серце — найгірше", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "рука-в-руку веде струм через груди; «однією рукою» — щоб не перетнути серце", 11.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # небезпечно — рука в руку
    s += text(205, 100, "НЕБЕЗПЕЧНО", 12.5, RED, "middle", "bold")
    s += _person(205, 200, 0.9)
    s += circle(205, 175, 7, "#fdd", RED, 1.6)
    s += text(205, 179, "♥", 11, RED, "middle")
    s += arrow(115, 195, 175, 178, RED, 2.4)
    s += arrow(235, 178, 295, 195, RED, 2.4)
    s += text(205, 300, "струм іде рука → серце → рука", 11.5, RED, "middle", "bold")
    s += text(205, 318, "(або рука → нога)", 10.5, GREY, "middle", style="italic")
    # безпечно — пташка
    s += text(615, 100, "БЕЗПЕЧНО (пташка)", 12.5, GREEN, "middle", "bold")
    s += line(500, 230, 730, 230, "#888", 4)
    s += f'<ellipse cx="615" cy="210" rx="22" ry="13" fill="#cdd" stroke="{INK}" stroke-width="1.6"/>\n'
    s += circle(635, 200, 7, "#cdd", INK, 1.4)
    s += line(608, 222, 606, 230, INK, 2)
    s += line(620, 222, 622, 230, INK, 2)
    s += text(615, 268, "обидві лапки на ОДНОМУ дроті", 11.5, GREEN, "middle", "bold")
    s += text(615, 286, "однаковий потенціал → різниці нема →", 11, INK, "middle")
    s += text(615, 302, "струму крізь пташку нема (§1.4)", 11, INK, "middle", "bold")
    save("fig-2-13-3-path.svg", s)


# ── Рис. 2.13.4 — захист: ПЗВ (RCD/GFCI) ─────────────────────────────────────
def fig213_protection():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Захист людини: ПЗВ (RCD/GFCI)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "стежить, чи стільки ж струму вертається, скільки пішло; як ні — рве коло за мілісекунди", 11.5, GREY, "middle", style="italic")
    # ПЗВ-блок
    s += rect(80, 130, 90, 110, "#eef5ff", INK, 2.2, 8)
    s += text(125, 170, "ПЗВ", 14, INK, "middle", "bold")
    s += text(125, 190, "(RCD)", 11, GREY, "middle")
    s += text(125, 215, "порівнює", 10, GREY, "middle")
    # лінія туди / назад
    s += line(170, 160, 560, 160, RED, 2.4)
    s += arrow(330, 160, 370, 160, RED, 2.2)
    s += text(360, 148, "I туди", 11, RED, "middle", "bold")
    s += line(170, 210, 560, 210, BLUE, 2.4)
    s += arrow(400, 210, 360, 210, BLUE, 2.2)
    s += text(360, 226, "I назад", 11, BLUE, "middle", "bold")
    # навантаження
    s += rect(560, 150, 40, 70, "#fff7ef", "#c89b5a", 2, 6)
    s += line(560, 160, 560, 150, INK, 2); s += line(560, 220, 560, 210, INK, 2)
    s += text(580, 250, "прилад", 11, INK, "middle")
    # витік крізь людину
    s += line(580, 220, 580, 290, "#e08030", 2.4, "5 4")
    s += _person(660, 300, 0.42)
    s += text(700, 285, "витік крізь людину", 10.5, "#e08030", "start", "bold")
    s += text(700, 301, "→ I туди ≠ I назад", 10.5, "#e08030", "start")
    s += rect(120, 318, W - 240, 36, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 341, "Помітив різницю в ~30 мА — миттю вимкнув. ПЗВ рятує ЛЮДЕЙ; запобіжник — лише прилад.",
              11.5, INK, "middle", "bold")
    save("fig-2-13-4-protection.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Математична вставка до теми 1.2.1 — Похідна I = dQ/dt
# ═════════════════════════════════════════════════════════════════════════════

def fig_derivative():
    W, H = 780, 420
    s = header(W, H)
    s += text(W / 2, 34, "Похідна: миттєвий струм — це нахил графіка Q(t)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "середній струм = ΔQ/Δt (хорда); стискаємо Δt до нуля — дістаємо dQ/dt (дотична)",
              12, GREY, "middle", style="italic")
    ox, oy = 110, 330
    s += arrow(ox, oy, 716, oy, INK, 1.8)
    s += arrow(ox, oy, ox, 96, INK, 1.8)
    s += text(706, oy + 22, "час t", 12, INK, "middle", "italic")
    s += text(ox - 6, 94, "заряд Q", 12, INK, "start", "italic")
    X = lambda t: ox + t * 98.33
    Y = lambda q: oy - q * 6.111
    s += polyline([(X(t / 10.0), Y((t / 10.0) ** 2)) for t in range(0, 61)], RED, 2.8)
    s += text(X(5.85), Y(33), "Q(t) = заряд, що пройшов", 12, RED, "end", "bold")
    P1 = (X(2), Y(4))
    P2 = (X(5), Y(25))
    # секанс (хорда) + катети ΔQ, Δt
    s += line(P1[0], P1[1], P2[0], P1[1], GREY, 1.4, "4 3")
    s += line(P2[0], P1[1], P2[0], P2[1], GREY, 1.4, "4 3")
    s += text((P1[0] + P2[0]) / 2, P1[1] + 18, "Δt", 12.5, GREY, "middle", "bold", "italic")
    s += text(P2[0] + 12, (P1[1] + P2[1]) / 2, "ΔQ", 12.5, GREY, "start", "bold", "italic")
    s += line(P1[0], P1[1], P2[0], P2[1], GREEN, 2.4)
    s += text(454, 222, "хорда: середній I = ΔQ/Δt", 11.5, GREEN, "middle", "bold")
    # дотична в точці P1
    sl = -0.2486
    s += line(P1[0] - 86, P1[1] - sl * 86, P1[0] + 152, P1[1] + sl * 152, INK, 2.4)
    s += circle(P1[0], P1[1], 4, INK, INK, 1)
    s += text(P1[0] + 156, P1[1] + sl * 152 + 4, "дотична: миттєвий I = dQ/dt", 11.5, INK, "start", "bold")
    s += text((P1[0] + P2[0]) / 2, 138, "Δt → 0:  хорда лягає на дотичну", 12.5, INK, "middle", "bold")
    s += text((P1[0] + P2[0]) / 2, 156, "де крива крутіша — там більший струм", 11, GREY, "middle", style="italic")
    save("fig-2-1m-1-derivative.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Історія до теми 1.2.1 — Ампер і 1820 рік
# ═════════════════════════════════════════════════════════════════════════════

def fig_oersted():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Дослід Ерстеда, 1820: струм відхиляє стрілку компаса", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "і то ПЕРПЕНДИКУЛЯРНО до дроту — електрика й магнетизм виявилися пов'язані",
              12, GREY, "middle", style="italic")

    def panel(cx, on, title):
        out = rect(cx - 150, 86, 300, 252, "none", FAINT, 1.6, 12)
        out += text(cx, 108, title, 13.5, INK, "middle", "bold")
        wy = 168
        out += line(cx - 120, wy, cx + 120, wy, INK, 4)
        if on:
            out += arrow(cx - 30, wy, cx + 70, wy, RED, 3)
            out += text(cx, wy - 12, "струм I тече", 12, RED, "middle", "bold")
        else:
            out += text(cx, wy - 12, "струму нема", 12, GREY, "middle")
        ccy = wy + 78
        out += circle(cx, ccy, 36, "#fafafa", INK, 1.8)
        if on:
            out += arrow(cx, ccy + 26, cx, ccy - 26, RED, 3.2)
            out += text(cx, ccy + 58, "стрілка ⟂ дроту", 11.5, RED, "middle", "bold")
        else:
            out += arrow(cx - 26, ccy, cx + 26, ccy, INK, 3.2)
            out += text(cx, ccy + 58, "стрілка вздовж (на північ)", 11, GREY, "middle")
        return out

    s += panel(230, False, "коло розімкнене")
    s += panel(590, True, "коло замкнене")
    s += text(W / 2, 376, "Уперше показано: рухомий заряд (струм) породжує магнітну дію — звідси й піде вся електродинаміка.",
              12, INK, "middle", "bold")
    save("fig-2-1i-1-oersted.svg", s)


def fig_parallel_wires():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Закон Ампера: два струми діють один на одного", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "паралельні струми притягуються; зустрічні — відштовхуються",
              12, GREY, "middle", style="italic")

    def pair(cx, same, title):
        out = rect(cx - 130, 86, 260, 252, "none", FAINT, 1.6, 12)
        out += text(cx, 108, title, 13.5, INK, "middle", "bold")
        lx, rx = cx - 44, cx + 44
        top, bot = 142, 300
        out += line(lx, top, lx, bot, INK, 4)
        out += line(rx, top, rx, bot, INK, 4)
        out += arrow(lx, bot - 18, lx, top + 18, RED, 3)
        out += (arrow(rx, bot - 18, rx, top + 18, RED, 3) if same else arrow(rx, top + 18, rx, bot - 18, RED, 3))
        out += text(lx - 13, top + 4, "I", 12, RED, "end", "bold", "italic")
        out += text(rx + 13, top + 4, "I", 12, RED, "start", "bold", "italic")
        midy = 224
        if same:
            out += arrow(lx + 10, midy, lx + 40, midy, GREEN, 2.6)
            out += arrow(rx - 10, midy, rx - 40, midy, GREEN, 2.6)
            out += text(cx, bot + 24, "притягуються", 13, GREEN, "middle", "bold")
        else:
            out += arrow(lx - 10, midy, lx - 40, midy, GREEN, 2.6)
            out += arrow(rx + 10, midy, rx + 40, midy, GREEN, 2.6)
            out += text(cx, bot + 24, "відштовхуються", 13, GREEN, "middle", "bold")
        return out

    s += pair(230, True, "однаковий напрям")
    s += pair(590, False, "протилежний напрям")
    s += text(W / 2, 376, "На силі між двома такими дротами довго трималося й офіційне означення ампера (до 2019 р.).",
              12, INK, "middle", "bold")
    save("fig-2-1i-2-parallel-wires.svg", s)


def fig_molecular_currents():
    W, H = 820, 392
    s = header(W, H)
    s += text(W / 2, 34, "Смілива ідея Ампера: магніт — це безліч колових струмів", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "усередині сусідні струми гасяться, на поверхні складаються — і ось магніт",
              12, GREY, "middle", style="italic")
    bx, by, bw, bh = 170, 118, 480, 150
    s += rect(bx, by, bw, bh, "#f4f6f9", "#8a949e", 2, 8)
    cols, rows = 8, 2
    for r in range(rows):
        for c in range(cols):
            ccx = bx + (c + 0.5) * bw / cols
            ccy = by + (r + 0.5) * bh / rows
            s += circle(ccx, ccy, 17, "none", "#9aa7b3", 1.3)
            s += arrow(ccx + 13, ccy - 7, ccx + 15, ccy + 7, RED, 1.3)  # обертання за год. стрілкою
    s += text(bx + bw / 2, by + bh + 2, "крихітні «молекулярні» колові струми (усі в один бік)", 11, GREY, "middle", style="italic")
    # сумарний поверхневий струм — зелений контур
    m = 7
    s += arrow(bx + 30, by - m, bx + bw - 30, by - m, GREEN, 2.6)
    s += arrow(bx + bw + m, by + 30, bx + bw + m, by + bh - 30, GREEN, 2.6)
    s += arrow(bx + bw - 30, by + bh + m, bx + 30, by + bh + m, GREEN, 2.6)
    s += arrow(bx - m, by + bh - 30, bx - m, by + 30, GREEN, 2.6)
    s += text(bx + bw / 2, by - 16, "сумарний поверхневий струм", 12, GREEN, "middle", "bold")
    s += text(bx - 24, by + bh / 2, "S", 18, INK, "middle", "bold")
    s += text(bx + bw + 24, by + bh / 2, "N", 18, INK, "middle", "bold")
    s += text(W / 2, H - 16, "Так Ампер звів магнетизм до руху заряду: жодних «магнітних зарядів» — лише струми.",
              12, INK, "middle", "bold")
    save("fig-2-1i-3-molecular-currents.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Математична вставка до теми 1.2.3 — Оцінка швидкості дрейфу
# ═════════════════════════════════════════════════════════════════════════════

def fig_drift_estimate():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Швидкість дрейфу «на серветці»: I = n·e·A·v", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за секунду крізь переріз проходить заряд цілого стовпчика електронів завдовжки v",
              12, GREY, "middle", style="italic")
    wx, wy, ww, wh = 90, 150, 420, 90
    s += rect(wx, wy, ww, wh, "#fbfbfb", "#b9b3a6", 2, 6)
    secx = wx + 300
    s += line(secx, wy - 14, secx, wy + wh + 14, INK, 2.4)
    s += text(secx, wy - 22, "переріз A", 12, INK, "middle", "bold")
    slabx = secx - 120
    s += rect(slabx, wy, 120, wh, "#eaf2f7", GREEN, 1.6)
    for dx, dy in [(20, 25), (55, 55), (90, 30), (35, 65), (75, 20), (100, 60), (15, 52), (60, 38)]:
        s += minus(slabx + dx, wy + dy, 6, BLUE, 1.6)
    s += arrow(slabx + 30, wy + wh + 28, slabx + 110, wy + wh + 28, GREEN, 2.6)
    s += text(slabx + 70, wy + wh + 44, "v (дрейф)", 11.5, GREEN, "middle", "bold")
    s += text(slabx + 60, wy - 10, "стовпчик довжини v·Δt", 11, GREEN, "middle", "bold")
    tx = wx + ww + 18
    s += text(tx, wy + 18, "За час Δt усі електрони", 11.5, INK, "start")
    s += text(tx, wy + 36, "зсунулись на v·Δt — крізь", 11.5, INK, "start")
    s += text(tx, wy + 54, "переріз пройшов заряд", 11.5, INK, "start")
    s += text(tx, wy + 72, "усього стовпчика:", 11.5, INK, "start")
    s += text(tx, wy + 96, "Q = n·(A·v·Δt)·e", 12.5, INK, "start", "bold")
    s += text(tx, wy + 116, "I = Q/Δt = n·e·A·v", 13, GREEN, "start", "bold")
    s += rect(70, 294, W - 140, 88, "#f4f7f4", GREEN, 1.6, 10)
    s += text(84, 316, "Оцінка (мідь, 1 А, дріт 1 мм²):", 12.5, INK, "start", "bold")
    s += text(84, 340, "v = I/(n·e·A) ≈ 1 / (10²⁹ · 1.6×10⁻¹⁹ · 10⁻⁶) ≈ 6×10⁻⁵ м/с", 13, INK, "start")
    s += text(84, 366, "≈ 0.06 мм/с — повільніше за равлика! А лампа спалахує миттєво (поле біжить, §1.2.4).",
              12, INK, "start", "bold")
    save("fig-2-3m-1-drift-estimate.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Історія до теми 1.2.4 — Трансатлантичний кабель 1858
# ═════════════════════════════════════════════════════════════════════════════

def fig_cable_route():
    W, H = 820, 388
    s = header(W, H)
    s += text(W / 2, 34, "Трансатлантичний кабель, 1858: ≈3000 км по дну океану", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "уперше Європу й Америку з'єднали «миттєвим» дротом — і виявилося, що сигнал не зовсім миттєвий",
              12, GREY, "middle", style="italic")
    wx, wy, ww, wh = 40, 150, 740, 168
    s += rect(wx, wy, ww, wh, "#eaf2f7", "#bcd3df", 1.4, 6)
    s += rect(wx, wy, 130, 64, "#e6ded0", "#b9a77e", 1.6, 0)
    s += rect(wx + ww - 130, wy, 130, 64, "#e6ded0", "#b9a77e", 1.6, 0)
    s += text(wx + 65, wy + 36, "Ірландія", 12.5, INK, "middle", "bold")
    s += text(wx + 65, wy + 52, "(Валентія)", 10.5, GREY, "middle")
    s += text(wx + ww - 65, wy + 34, "Ньюфаундленд", 11.5, INK, "middle", "bold")
    s += text(wx + ww - 65, wy + 52, "(Канада)", 10.5, GREY, "middle")
    floorY = wy + wh - 26
    pts = [(wx + 130, wy + 64)]
    for i in range(0, 25):
        x = wx + 150 + (ww - 300) * i / 24
        y = floorY + 5 * math.sin(i * 0.9)
        pts.append((x, y))
    pts.append((wx + ww - 130, wy + 64))
    s += polyline(pts, INK, 2.6)
    s += text(W / 2, floorY + 22, "кабель на дні Атлантики", 11.5, INK, "middle", "bold")
    sx = W / 2
    s += rect(sx - 52, wy - 16, 44, 16, "#cfd3d8", "#555555", 1.4, 3)
    s += rect(sx + 8, wy - 16, 44, 16, "#cfd3d8", "#555555", 1.4, 3)
    s += text(sx, wy - 22, "два кораблі зрощують кабель посеред океану", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 366, "Сигнал біжить дуже швидко — але дорогою «розмазується» й відстає (див. далі).",
              12, INK, "middle", "bold")
    save("fig-2-4i-1-cable-route.svg", s)


def fig_retardation():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому сигнал не миттєвий: кабель «розмазує» імпульс", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "різкий імпульс на вході виходить на тому кінці згладженим і запізнілим",
              12, GREY, "middle", style="italic")
    ax, ay = 80, 250
    s += line(ax, ay, ax + 210, ay, INK, 1.6)
    s += line(ax, ay, ax, ay - 130, INK, 1.6)
    s += text(ax + 100, ay + 22, "вхід (Ірландія)", 12, INK, "middle", "bold")
    s += polyline([(ax + 30, ay), (ax + 30, ay - 100), (ax + 90, ay - 100), (ax + 90, ay), (ax + 210, ay)], RED, 2.8)
    s += text(ax + 60, ay - 110, "різкий", 11, RED, "middle", "bold")
    s += arrow(ax + 218, ay - 56, ax + 332, ay - 56, INK, 2.4)
    s += text(ax + 275, ay - 68, "≈3000 км кабелю", 11.5, INK, "middle", "bold")
    bx, by = ax + 360, 250
    s += line(bx, by, bx + 230, by, INK, 1.6)
    s += line(bx, by, bx, by - 130, INK, 1.6)
    s += text(bx + 115, by + 22, "вихід (Ньюфаундленд)", 12, INK, "middle", "bold")
    pts = [(bx + i, by - 60 * math.exp(-((i - 125) / 46.0) ** 2)) for i in range(0, 231, 3)]
    s += polyline(pts, GREEN, 2.8)
    s += text(bx + 128, by - 74, "розмазаний і запізнілий", 11, GREEN, "middle", "bold")
    s += rect(70, 312, W - 140, 66, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 334, "Довгий кабель накопичує заряд уздовж себе й гальмує сигнал («ретардація»):",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 356, "затримка росте як КВАДРАТ довжини — «закон квадратів» Вільяма Томсона (Кельвіна).",
              12, INK, "middle")
    save("fig-2-4i-2-retardation.svg", s)


def fig_whitehouse_thomson():
    W, H = 820, 392
    s = header(W, H)
    s += text(W / 2, 34, "Дві школи: груба напруга проти тонкого приладу", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "Вайтгауз тиснув кіловольтами й пробив кабель; Томсон ловив найслабший сигнал — і мав рацію",
              12, GREY, "middle", style="italic")
    # ЛІВО — Вайтгауз
    s += rect(50, 86, 340, 274, "#fdf1f0", RED, 1.6, 12)
    s += text(220, 110, "Вайтгауз: груба сила", 14, RED, "middle", "bold")
    s += rect(110, 150, 80, 50, "#eeeeee", INK, 1.8, 4)
    for i in range(5):
        s += line(112, 158 + i * 9, 188, 158 + i * 9, "#b08a5a", 1.4)
    s += text(150, 222, "індукційна котушка", 10.5, INK, "middle")
    s += text(150, 238, "~2000 В", 11, INK, "middle", "bold")
    s += polyline([(220, 175), (240, 165), (232, 182), (256, 172)], "#caa24a", 2.4)
    s += line(272, 150, 272, 202, INK, 3)
    s += text(300, 168, "пробита", 11, RED, "start", "bold")
    s += text(300, 184, "ізоляція", 11, RED, "start", "bold")
    s += text(220, 300, "тиснути кіловольтами,", 11.5, INK, "middle")
    s += text(220, 318, "щоб «проштовхнути» сигнал", 11.5, INK, "middle")
    s += text(220, 340, "→ кабель загинув за тижні", 11.5, RED, "middle", "bold")
    # ПРАВО — Томсон
    s += rect(430, 86, 340, 274, "#eef5ef", GREEN, 1.6, 12)
    s += text(600, 110, "Томсон: тонкий прилад", 14, GREEN, "middle", "bold")
    s += circle(540, 185, 26, "none", INK, 2)
    s += line(528, 174, 552, 173, INK, 2.6)            # дзеркальце
    s += line(468, 150, 540, 182, "#caa24a", 1.6)      # падаючий промінь
    s += line(540, 182, 644, 150, "#caa24a", 1.6)      # відбитий промінь
    s += circle(644, 150, 4, "#caa24a", "#caa24a", 1)  # світла пляма
    s += line(652, 128, 652, 196, INK, 2)              # шкала
    s += text(540, 230, "дзеркальний гальванометр", 10.5, INK, "middle", "bold")
    s += text(600, 300, "ловити найслабший струм", 11.5, INK, "middle")
    s += text(600, 318, "крихітним відхиленням променя", 11.5, INK, "middle")
    s += text(600, 340, "→ підхід, що зрештою переміг", 11.5, GREEN, "middle", "bold")
    save("fig-2-4i-3-whitehouse-thomson.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Компонентна вставка до теми 1.2.7 — Вимикачі й кнопки
# ═════════════════════════════════════════════════════════════════════════════

def fig_switches():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Вимикачі: полюси (P) і напрямки (T) — SPST, SPDT, NO/NC", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "полюс = скільки незалежних кіл вимикач керує; напрямок = на скільки положень перемикає",
              11.5, GREY, "middle", style="italic")
    cy = 196

    def panel(x, title, sub):
        out = rect(x, 86, 180, 256, "none", FAINT, 1.6, 12)
        out += text(x + 90, 110, title, 13.5, INK, "middle", "bold")
        out += text(x + 90, 326, sub, 10.5, GREY, "middle", style="italic")
        return out

    x = 30
    s += panel(x, "SPST", "1 полюс · 1 напрямок")
    s += circle(x + 45, cy, 5, INK, INK, 1)
    s += circle(x + 135, cy, 5, INK, INK, 1)
    s += line(x + 45, cy, x + 122, cy - 34, INK, 3)
    s += text(x + 90, cy + 54, "просто увімк/вимк", 11, INK, "middle", "bold")

    x = 225
    s += panel(x, "SPDT", "1 полюс · 2 напрямки")
    s += circle(x + 40, cy, 5, INK, INK, 1)
    s += circle(x + 135, cy - 26, 5, INK, INK, 1)
    s += circle(x + 135, cy + 26, 5, INK, INK, 1)
    s += line(x + 40, cy, x + 135, cy - 26, INK, 3)
    s += text(x + 90, cy + 54, "перемикач на 2 положення", 10.5, INK, "middle", "bold")

    x = 420
    s += panel(x, "Кнопка NO", "нормально розімкнена")
    s += circle(x + 45, cy, 5, INK, INK, 1)
    s += circle(x + 135, cy, 5, INK, INK, 1)
    s += line(x + 45, cy, x + 70, cy, INK, 2.4)
    s += line(x + 110, cy, x + 135, cy, INK, 2.4)
    s += line(x + 70, cy - 16, x + 110, cy - 16, INK, 3)
    s += line(x + 90, cy - 16, x + 90, cy - 30, INK, 2)
    s += arrow(x + 90, cy - 46, x + 90, cy - 33, RED, 2)
    s += text(x + 90, cy + 54, "натиснув — ЗАМКНУВ", 10.5, GREEN, "middle", "bold")

    x = 615
    s += panel(x, "Кнопка NC", "нормально замкнена")
    s += circle(x + 45, cy, 5, INK, INK, 1)
    s += circle(x + 135, cy, 5, INK, INK, 1)
    s += line(x + 45, cy, x + 135, cy, INK, 3)
    s += line(x + 90, cy, x + 90, cy - 14, INK, 2)
    s += arrow(x + 90, cy - 32, x + 90, cy - 17, RED, 2)
    s += text(x + 90, cy + 54, "натиснув — РОЗІМКНУВ", 10.5, RED, "middle", "bold")
    save("fig-2-7c-1-switches.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Компонентна вставка до теми 1.2.11 — Гальванічна корозія
# ═════════════════════════════════════════════════════════════════════════════

def fig_galvanic_corrosion():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Гальванічна корозія: чому не можна скручувати мідь з алюмінієм", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "два різні метали + волога = крихітна батарея; менш шляхетний метал роз'їдається",
              11.5, GREY, "middle", style="italic")
    # ── Панель A: стик Al–Cu ──
    s += rect(40, 86, 440, 304, "none", FAINT, 1.6, 12)
    s += text(260, 108, "Стик Al–Cu у вологому повітрі", 13, INK, "middle", "bold")
    by, bw, bh = 184, 110, 70
    al_x, cu_x = 130, 240
    s += rect(al_x, by, bw, bh, "#d7dadd", "#9aa0a6", 2, 4)
    s += rect(cu_x, by, bw, bh, "#e6b98a", "#b07a3e", 2, 4)
    s += text(al_x + bw / 2, by + bh / 2 + 5, "Al", 17, INK, "middle", "bold")
    s += text(cu_x + bw / 2, by + bh / 2 + 5, "Cu", 17, "#7a4a16", "middle", "bold")
    s += text(al_x + bw / 2, by - 8, "алюміній (анод)", 11, RED, "middle", "bold")
    s += text(cu_x + bw / 2, by - 8, "мідь (катод)", 11, GREEN, "middle", "bold")
    s += rect(200, 156, 90, 16, "#cfe6f2", "#7fb3cf", 1.4, 6)
    s += text(245, 150, "плівка вологи (електроліт)", 10, "#3a6b86", "middle", style="italic")
    for dx in (150, 175, 200):
        s += plus(dx, 150, 5, RED, 1.6)
    s += arrow(al_x + 30, by + bh + 16, cu_x + 70, by + bh + 16, BLUE, 2.4)
    s += text((al_x + cu_x + bw) / 2, by + bh + 32, "e⁻ : Al → Cu", 12, BLUE, "middle", "bold")
    s += text(al_x + 30, by + bh + 50, "Al роз'їдається", 11, RED, "middle", "bold")
    s += text(260, 312, "роз'їдається метал, що віддає електрони (анод) — тут Al;", 10.5, INK, "middle")
    s += text(260, 328, "мідь захищена. Оксид Al ще й ізолює → стик гріється.", 10.5, INK, "middle")
    s += text(260, 350, "Без вологи реакції майже нема — суха коробка безпечніша.", 10, GREY, "middle", style="italic")
    # ── Панель B: гальванічний ряд ──
    s += rect(500, 86, 280, 304, "none", FAINT, 1.6, 12)
    s += text(640, 108, "Гальванічний ряд", 13, INK, "middle", "bold")
    bx, top, bot = 562, 150, 344
    s += line(bx, top, bx, bot, INK, 2)
    s += text(bx, top - 8, "↑ активні — анод (роз'їдаються)", 9.5, RED, "middle", "bold")
    s += text(bx + 4, bot + 18, "↓ шляхетні — катод (захищені)", 9.5, GREEN, "middle", "bold")
    items = [("Mg магній", RED), ("Zn цинк", RED), ("Al алюміній", RED), ("сталь", "#aa5577"),
             ("латунь", "#66aa66"), ("Cu мідь", GREEN), ("нержавійка", GREEN), ("золото", GREEN)]
    ys = {}
    for i, (name, col) in enumerate(items):
        y = top + (bot - top) * i / (len(items) - 1)
        ys[name] = y
        s += circle(bx, y, 4, col, col, 1)
        s += text(bx + 12, y + 4, name, 11.5, col, "start", "bold" if col in (RED, GREEN) else "normal")
    s += line(bx - 16, ys["Al алюміній"], bx - 16, ys["Cu мідь"], INK, 2)
    s += text(bx - 22, (ys["Al алюміній"] + ys["Cu мідь"]) / 2, "далеко →", 9.5, INK, "end", "bold")
    s += text(bx - 22, (ys["Al алюміній"] + ys["Cu мідь"]) / 2 + 13, "швидка корозія", 9.5, INK, "end", "bold")
    save("fig-2-11c-1-galvanic-corrosion.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Компонентна вставка до теми 1.2.13 — ПЗВ (RCD)
# ═════════════════════════════════════════════════════════════════════════════

def fig_rcd():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "ПЗВ (RCD): порівнює струм «туди» і «назад»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у справному колі вони рівні; витік у землю порушує баланс — і ПЗВ миттю розриває коло",
              11.5, GREY, "middle", style="italic")

    def panel(x, fault):
        out = rect(x, 84, 380, 322, "none", FAINT, 1.6, 12)
        out += text(x + 190, 108, ("ВИТІК (небезпека)" if fault else "Норма"), 13.5,
                    (RED if fault else GREEN), "middle", "bold")
        cy = 196
        Ly, Ny = cy - 16, cy + 16
        rx = x + 92
        out += circle(rx, cy, 30, "none", "#1f8a3b", 2.6)
        out += circle(rx, cy, 15, "none", "#1f8a3b", 1.4)
        out += text(rx, cy + 50, "давач (кільце)", 9.5, GREY, "middle", style="italic")
        loadx = x + 300
        out += line(x + 30, Ly, loadx, Ly, RED, 3)
        out += line(x + 30, Ny, loadx, Ny, BLUE, 3)
        out += text(x + 28, Ly - 8, "L", 12, RED, "start", "bold")
        out += text(x + 28, Ny + 18, "N", 12, BLUE, "start", "bold")
        out += circle(loadx, cy, 16, "#fff7e0", "#caa24a", 2)
        out += line(loadx, Ly, loadx, cy - 16, INK, 2)
        out += line(loadx, cy + 16, loadx, Ny, INK, 2)
        out += text(loadx, cy + 38, "наван-", 9.5, INK, "middle")
        out += text(loadx, cy + 50, "таження", 9.5, INK, "middle")
        out += arrow(x + 150, Ly, x + 205, Ly, RED, 2.2)
        out += arrow(x + 205, Ny, x + 150, Ny, BLUE, 2.2)
        if fault:
            lk = x + 235
            out += line(lk, Ly, lk, cy + 78, "#caa24a", 2.4)
            out += circle(lk, cy + 90, 7, "#ffffff", INK, 1.6)
            gy = cy + 106
            out += line(lk - 18, gy, lk + 18, gy, INK, 2.2)
            out += line(lk - 12, gy + 6, lk + 12, gy + 6, INK, 2.2)
            out += line(lk - 6, gy + 12, lk + 6, gy + 12, INK, 2.2)
            out += text(lk + 24, cy + 88, "витік ΔI", 10.5, "#a06a00", "start", "bold")
            out += text(x + 190, 352, "I назад < I туди → дисбаланс ΔI у кільці", 11, RED, "middle", "bold")
            out += text(x + 190, 370, "→ ПЗВ розриває коло (~30 мА, мілісекунди) ✗", 11, RED, "middle", "bold")
        else:
            out += text(x + 190, 352, "I туди = I назад → поле в кільці = 0", 11, GREEN, "middle", "bold")
            out += text(x + 190, 370, "→ не спрацьовує ✓", 11, GREEN, "middle", "bold")
        return out

    s += panel(30, False)
    s += panel(420, True)
    save("fig-2-13c-1-rcd.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Історія до теми 1.2.13 — Чарльз Далзіел
# ═════════════════════════════════════════════════════════════════════════════

def fig_shock_thresholds():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 34, "Що виміряв Далзіел: скільки струму небезпечно для людини", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "саме ці числа (а не «вольти») лежать в основі порогів ПЗВ і GFCI",
              11.5, GREY, "middle", style="italic")
    x, top, bot = 240, 100, 396
    s += line(x, top, x, bot, INK, 2.4)
    s += arrow(x, top + 4, x, top - 6, INK, 2.4)
    s += text(x, bot + 22, "0", 11, INK, "middle")
    s += text(x, top - 14, "струм крізь тіло (мА)", 11.5, INK, "middle", "bold")
    rows = [
        (0.10, "~1 мА", "відчуття (легке поколювання)", GREEN),
        (0.28, "~5 мА", "поріг GFCI (США) — захищає", GREEN),
        (0.46, "10–16 мА", "«НЕ ВІДПУСТИТИ»: м'язи зводить (Далзіел)", "#c98a00"),
        (0.61, "~30 мА", "поріг ПЗВ (Європа); важко дихати", "#c98a00"),
        (0.80, "~100 мА", "ФІБРИЛЯЦІЯ серця — смертельно (Далзіел)", RED),
        (0.94, "> 1 А", "опіки, зупинка серця", RED),
    ]
    for frac, val, desc, col in rows:
        y = bot - frac * (bot - top)
        s += line(x - 8, y, x + 8, y, INK, 2)
        s += circle(x, y, 5, col, col, 1)
        s += text(x - 16, y + 4, val, 12, col, "end", "bold")
        s += text(x + 22, y + 4, desc, 11.5, col, "start", "bold" if col != GREEN else "normal")
    s += rect(60, H - 38, W - 120, 28, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 19, "Звідси головна думка §1.2.13: вбивають МІЛІАМПЕРИ через тіло, а не самі по собі вольти.",
              11.5, INK, "middle", "bold")
    save("fig-2-13i-1-shock-thresholds.svg", s)


def fig_collective_rcd():
    W, H = 800, 372
    s = header(W, H)
    s += text(W / 2, 34, "«Далзіел винайшов ПЗВ» — спрощення: внесок був колективний", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "принцип і сам пристрій старші за Далзіела й народилися в різних країнах",
              11.5, GREY, "middle", style="italic")
    y = 156
    s += line(70, y, W - 70, y, INK, 2.4)
    s += text(70, y - 10, "1950", 10.5, GREY, "start")
    s += text(W - 70, y - 10, "1970", 10.5, GREY, "end")
    marks = [
        (0.18, True, "1955", "Анрі Рубін · ПАР", "перший практичний", "захист від витоку (копальні)", "#1f47b5"),
        (0.44, False, "1950-ті", "Бігельмаєр · Австрія", "патенти на такі", "вимикачі (досл. на собі)", "#7a52c0"),
        (0.70, True, "~1961", "Ч. Далзіел · США", "GFCI + наука про", "небезпечний струм", "#1f8a3b"),
    ]
    for frac, below, yr, who, l1, l2, col in marks:
        mx = 70 + frac * (W - 140)
        s += circle(mx, y, 6, col, col, 1.5)
        if below:
            s += text(mx, y + 24, yr, 11.5, col, "middle", "bold")
            s += text(mx, y + 42, who, 11, INK, "middle", "bold")
            s += text(mx, y + 58, l1, 9.5, GREY, "middle")
            s += text(mx, y + 72, l2, 9.5, GREY, "middle")
        else:
            s += text(mx, y - 56, yr, 11.5, col, "middle", "bold")
            s += text(mx, y - 38, who, 11, INK, "middle", "bold")
            s += text(mx, y - 22, l1, 9.5, GREY, "middle")
            s += text(mx, y - 8, l2, 9.5, GREY, "middle")
    s += rect(60, H - 64, W - 120, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 42, "Чесно розділити внески: ПРИНЦИП і пристрій — колективні, старші за Далзіела;",
              11.5, INK, "middle", "bold")
    s += text(W / 2, H - 22, "а НАУКУ про небезпечний струм і персональний GFCI дав саме Далзіел.",
              11.5, INK, "middle")
    save("fig-2-13i-2-collective-rcd.svg", s)


if __name__ == "__main__":
    # Історія до розділу
    fig_ohm_story()
    fig_thomson_crt()
    fig_drude_model()
    # §2.1 Струм — потік заряду
    fig21_current_definition()
    fig21_ampere()
    fig21_water_flow()
    fig21_magnitudes()
    fig21_ammeter_series()
    # §2.2 Напрямок струму
    fig22_two_directions()
    fig22_equivalence()
    fig22_schematic()
    fig22_holes()
    # §2.3 Море електронів і дрейф
    fig23_electron_sea()
    fig23_thermal_vs_drift()
    fig23_drift_formula()
    fig23_drift_slow()
    # §2.4 Парадокс миттєвого ввімкнення
    fig24_three_speeds()
    fig24_full_pipe()
    fig24_field_propagates()
    fig24_energy_in_field()
    # §2.5 Струм однаковий уздовж кола
    fig25_same_current()
    fig25_water_loop()
    fig25_current_vs_energy()
    fig25_series_string()
    # §2.6 Напруга — причина струму
    fig26_causal_chain()
    fig26_field_in_wire()
    fig26_sustained_vs_transient()
    fig26_emf()
    # §2.7 Замкнене коло
    fig27_closed_vs_open()
    fig27_dead_end()
    fig27_three_states()
    fig27_ground_return()
    # §2.8 Механізм провідності
    fig28_three_classes()
    fig28_bound_vs_free()
    fig28_band_gap()
    fig28_resistivity_scale()
    # §2.9 Зіткнення й нагрів
    fig29_collision_mechanism()
    fig29_what_scatters()
    fig29_heat()
    fig29_temperature()
    # §2.10 Провідність як властивість матеріалу
    fig210_R_vs_rho()
    fig210_resistivity_table()
    fig210_tempco()
    fig210_inrush()
    # §2.11 Не лише метали
    fig211_carriers_zoo()
    fig211_electrolyte()
    fig211_plasma()
    fig211_body()
    # Історія до §2.11 — Арреніус
    fig_dissociation()
    fig_thesis_arc()
    fig_arrhenius_legacy()
    # §2.12 DC vs AC
    fig212_dc_vs_ac_wave()
    fig212_frequency_period()
    fig212_rms()
    fig212_why_ac_transform()
    # Історія до §2.12 — Війна струмів
    fig_dc_problem()
    fig_war_players()
    fig_war_outcome()
    # §2.13 Струм і безпека
    fig213_current_thresholds()
    fig213_ohm_skin()
    fig213_path()
    fig213_protection()
    # §2.1 вставка — похідна I = dQ/dt
    fig_derivative()
    # §2.1 історія — Ампер і 1820 рік
    fig_oersted()
    fig_parallel_wires()
    fig_molecular_currents()
    # §2.3 вставка — оцінка швидкості дрейфу
    fig_drift_estimate()
    # §2.4 історія — трансатлантичний кабель 1858
    fig_cable_route()
    fig_retardation()
    fig_whitehouse_thomson()
    # §2.7 вставка — вимикачі й кнопки
    fig_switches()
    # §2.11 вставка — гальванічна корозія
    fig_galvanic_corrosion()
    # §2.13 вставка — ПЗВ (RCD)
    fig_rcd()
    # §2.13 історія — Чарльз Далзіел
    fig_shock_thresholds()
    fig_collective_rcd()
    print("OK — фігури розділу 2 (… + §2.13) згенеровано в", OUT)
