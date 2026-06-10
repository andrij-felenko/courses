# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 4.2 — «Кислоти й основи» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; заряд «+» червоний, «−» синій;
атоми-кульки — H біла з сірим контуром тощо; усі підписи українською.
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
H_FILL = "#ffffff"
H_LINE = "#9a9a9a"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
MET_FILL = "#8a7fae"
FAT    = "#caa24a"
WATER  = "#cfe6f5"
BANDBL = "#eaf4fb"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen"}


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


def plus(cx, cy, size=6, color=RED, w=2.4):
    return (line(cx - size, cy, cx + size, cy, color, w)
            + line(cx, cy - size, cx, cy + size, color, w))


def minus(cx, cy, size=6, color=BLUE, w=2.4):
    return line(cx - size, cy, cx + size, cy, color, w)


def ball(cx, cy, r, fill, stroke, label=None, lsize=12, lcolor="#ffffff"):
    s = circle(cx, cy, r, fill, stroke, 1.8)
    if label:
        s += text(cx, cy + lsize * 0.36, label, lsize, lcolor, "middle", "bold")
    return s


def poly(points, color=INK, w=2, fill="none"):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>\n')


def h_plus(cx, cy, r=8):
    """Іон Гідрогену H⁺ — біла кулька H з червоним плюсом."""
    return ball(cx, cy, r, H_FILL, H_LINE, "H", 11, INK) + text(cx + r + 1, cy - r + 3, "+", 12, RED, "start", "bold")


def oh_minus(cx, cy, scale=1.0):
    """Гідроксид-іон OH⁻ — O (червона) + H (біла), загальний заряд «−»."""
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


def wavy(x0, y0, length, color=FAT, w=3.5, amp=5, n=3, direction=-1):
    pts = []
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        pts.append((x0 + direction * length * t, y0 + amp * math.sin(t * n * 2 * math.pi)))
    return poly(pts, color, w)


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


# ── Рис. 4.2.1-1 — спільний секрет: різні кислоти → той самий H⁺ ─────────────
def fig_secret():
    W, H = 880, 452
    s = header(W, H)
    s += text(W / 2, 32, "Спільний секрет кислот: усі віддають той самий H⁺", 21, INK, "middle", "bold")
    s += text(W / 2, 54,
              "оцет, лимон, шлунок — молекули різні, а в воду летить однаковий H⁺ (голий протон)",
              12.5, GREY, "middle", style="italic")

    # водна смуга
    s += rect(40, 320, 800, 92, BANDBL, "none", 0, 12)
    s += text(W / 2, 402, "у воді плаває однаковий H⁺ — Гідроген, що згубив свій єдиний електрон",
              12.5, "#3a6f95", "middle", style="italic")

    acids = [(180, "оцет", "оцтова кислота", "#cfe3df", "#8fb0a9"),
             (440, "лимон", "лимонна кислота", "#f3e1b6", "#c6ab6a"),
             (700, "шлунок", "хлоридна, HCl", "#f1d2db", "#c891a2")]
    my = 178
    for mx, name, sci, col, oc in acids:
        s += text(mx, 110, name, 16, INK, "middle", "bold")
        s += text(mx, 128, sci, 11.5, GREY, "middle", style="italic")
        s += ellipse(mx, my, 50, 31, col, oc, 2)
        s += text(mx - 6, my + 5, "решта", 12.5, "#555", "middle", style="italic")
        # приєднаний H
        hx, hy = mx + 40, my + 24
        s += line(mx + 20, my + 16, hx, hy, H_LINE, 2.5)
        s += ball(hx, hy, 11, H_FILL, H_LINE, "H", 13, INK)
        # H зривається у воду
        s += arrow(hx + 4, hy + 12, hx + 4, 312, RED, 2.4)
        s += h_plus(mx + 44, 356)
    # ще вільні H⁺ у смузі
    for x, y in [(110, 372), (250, 350), (330, 384), (560, 350), (610, 384), (770, 366), (840 - 60, 350)]:
        s += h_plus(x, y)
    save("fig-4-2-1-1-secret.svg", s)


# ── Рис. 4.2.1-2 — сильна vs слабка кислота ──────────────────────────────────
def _acid_unit(cx, cy, released, col="#d9d2e6", oc="#8a7fae"):
    s = ellipse(cx, cy, 16, 11, col, oc)
    if released:
        s += minus(cx, cy, 5, BLUE)
        s += h_plus(cx + 26, cy - 1, 7)
    else:
        s += line(cx + 13, cy + 4, cx + 23, cy + 9, H_LINE, 2)
        s += ball(cx + 26, cy + 11, 8, H_FILL, H_LINE, "H", 10, INK)
    return s


def fig_strong_weak():
    W, H = 780, 432
    s = header(W, H)
    s += text(W / 2, 32, "Сила кислоти — наскільки охоче вона віддає H⁺", 20, INK, "middle", "bold")

    bw, bh, by = 200, 212, 86
    for x0, title, units, cap, capcol in [
        (70, "сильна кислота",
         [(45, 60, 1), (120, 56, 1), (40, 112, 1), (118, 116, 1), (52, 168, 1), (126, 168, 1), (86, 138, 0)],
         "майже всі віддали H⁺", RED),
        (430, "слабка кислота",
         [(45, 60, 0), (120, 56, 0), (40, 112, 1), (118, 116, 0), (52, 168, 1), (126, 168, 0), (86, 138, 0)],
         "віддали лиш дрібку", INK),
    ]:
        cx = x0 + bw / 2
        s += text(cx, by - 12, title, 16, INK, "middle", "bold")
        s += _liquid(x0, by, bw, bh, WATER)
        for dx, dy, rel in units:
            s += _acid_unit(x0 + dx, by + dy, rel)
        s += _beaker(x0, by, bw, bh)
        s += text(cx, by + bh + 26, cap, 14, capcol, "middle", "bold")

    # легенда
    s += _acid_unit(150, 372, 0)
    s += text(210, 377, "ціла молекула (H при ній)", 12, INK, "start")
    s += _acid_unit(430, 372, 1)
    s += text(510, 377, "віддала H⁺ (лишився «−»)", 12, INK, "start")
    s += text(W / 2, H - 8,
              "річ не в кількості налитого, а в охоті віддавати: шлунковий сік — сильна, оцет і лимон — слабкі",
              12.5, GREY, "middle", style="italic")
    save("fig-4-2-1-2-strong-weak.svg", s)


# ── Рис. 4.2.2-1 — дзеркало: кислота → H⁺, основа → OH⁻ ──────────────────────
def fig_mirror():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 32, "Дзеркало кислот: основи дають OH⁻", 21, INK, "middle", "bold")
    s += text(W / 2, 54,
              "кислота пускає у воду H⁺, основа — протилежний OH⁻; зустрівшись, вони гаснуть у воду",
              12.5, GREY, "middle", style="italic")

    # ліва панель — кислота
    s += rect(36, 78, 300, 300, "#fdeeee", "#f1d6d6", 1.5, 14)
    s += text(186, 104, "КИСЛОТА", 16, RED, "middle", "bold")
    s += text(186, 122, "віддає H⁺", 12.5, "#9b4b45", "middle", style="italic")
    s += ellipse(150, 178, 46, 27, "#f1d2db", "#c891a2", 2)
    s += text(150, 182, "решта", 12, "#666", "middle", style="italic")
    s += line(178, 192, 196, 204, H_LINE, 2.4)
    s += ball(199, 207, 10, H_FILL, H_LINE, "H", 12, INK)
    s += arrow(206, 216, 214, 244, RED, 2.2)
    for x, y in [(90, 250), (150, 268), (110, 320), (210, 300), (270, 258), (300, 330), (240, 348)]:
        s += h_plus(x, y, 8)

    # права панель — основа
    s += rect(544, 78, 300, 300, "#eef1fb", "#cfd8f2", 0, 14)
    s += text(694, 104, "ОСНОВА · луг", 16, BLUE, "middle", "bold")
    s += text(694, 122, "віддає OH⁻", 12.5, "#3a4f93", "middle", style="italic")
    s += ball(612, 168, 15, MET_FILL, "#6f6394")
    s += plus(612, 168, 6, RED)
    s += text(612, 150, "Na⁺", 12.5, INK, "middle", "bold")
    s += oh_minus(672, 178)
    s += text(708, 150, "їдкий натр: Na⁺ + OH⁻", 11.5, "#3a4f93", "middle", style="italic")
    for x, y in [(584, 264), (648, 280), (600, 330), (712, 300), (770, 262), (760, 336), (690, 350)]:
        s += oh_minus(x, y, 0.78)

    # центр — зустріч у воду
    s += text(440, 120, "зустріч", 12.5, GREEN, "middle", "bold")
    s += watermol(440, 200)
    s += arrow(392, 196, 420, 206, RED, 2.2)
    s += arrow(488, 196, 460, 206, BLUE, 2.2)
    s += text(440, 286, "H⁺ + OH⁻ → H₂O", 15, GREEN, "middle", "bold")
    s += text(440, 306, "протилежності гаснуть у воду", 11.5, GREY, "middle", style="italic")
    save("fig-4-2-2-1-mirror.svg", s)


# ── Рис. 4.2.2-2 — чому луг слизький: розбирає жир на мило ────────────────────
def _fat(cx, cy, joined=True):
    """Молекула жиру: вертикальний кістяк (гліцерин) + 3 хвилясті хвости."""
    s = line(cx, cy - 44, cx, cy + 44, "#7a6f8f", 6)
    for dy in (-36, 0, 36):
        if joined:
            s += wavy(cx - 4, cy + dy, 92, FAT, 3.5)
        else:
            s += wavy(cx - 26, cy + dy, 80, FAT, 3.5)
            s += circle(cx - 26, cy + dy, 5, "#e7d3a0", "#a98a3f", 1.4)
    s += text(cx, cy - 56, "гліцерин", 11.5, "#5b5170", "middle")
    return s


def fig_slippery():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому луг слизький і небезпечний: він розбирає жир", 20, INK, "middle", "bold")
    s += text(W / 2, 54,
              "OH⁻ розриває молекулу жиру на розчинні шматки — буквально робить мило",
              12.5, GREY, "middle", style="italic")

    # ліворуч — цілий жир + OH⁻ наступає
    s += text(150, 110, "жир", 14, INK, "middle", "bold")
    s += text(150, 126, "(на шкірі — шкірне сало)", 11, GREY, "middle", style="italic")
    s += _fat(190, 220, joined=True)
    s += oh_minus(280, 220, 0.85)
    s += arrow(262, 220, 232, 220, BLUE, 2.4)
    s += text(286, 250, "OH⁻", 12, BLUE, "middle", "bold")

    # стрілка процесу
    s += arrow(330, 220, 470, 220, INK, 3)
    s += text(400, 204, "OH⁻ розриває", 12.5, INK, "middle", style="italic")

    # праворуч — розламаний жир = мило
    s += _fat(560, 220, joined=False)
    for x, y in [(636, 168), (664, 230), (628, 286)]:
        s += wavy(x, y, 70, FAT, 3.5)
        s += circle(x, y, 6, "#e7d3a0", "#a98a3f", 1.6)
    s += text(700, 300, "мило (розчинне)", 12.5, INK, "middle", "bold")

    s += text(W / 2, 372,
              "слизькість — це твій шкірний жир, що на дотику стає милом; сильний луг робить це по живому",
              12.5, GREY, "middle", style="italic")
    save("fig-4-2-2-2-slippery.svg", s)


_PH_COLORS = ["#b71c1c", "#d32f2f", "#e64a19", "#f57c00", "#f9a825", "#cddc39",
              "#9ccc65", "#43a047", "#26a69a", "#0097a7", "#1976d2", "#3949ab",
              "#5e35b1", "#7b1fa2", "#4a148c"]


# ── Рис. 4.2.3-1 — шкала pH ──────────────────────────────────────────────────
def fig_ph_scale():
    W, H = 880, 330
    s = header(W, H)
    s += text(W / 2, 32, "Шкала pH: кого в розчині більше — H⁺ чи OH⁻", 21, INK, "middle", "bold")

    x0, y0, cell, hbar = 70, 150, (810 - 70) / 15.0, 46

    def xat(p):
        return x0 + (p + 0.5) * cell

    # табірні підписи
    s += text(150, 74, "← більше H⁺ · кислоти", 14, RED, "middle", "bold")
    s += text(730, 74, "основи · більше OH⁻ →", 14, BLUE, "middle", "bold")

    # приклади над смугою (зі сполучними лініями)
    examples = [(1.0, "шлунковий сік", 110), (2.5, "лимон, оцет", 92),
                (7.0, "чиста вода", 110), (9.5, "сода, мило", 92),
                (13.0, "засіб для труб", 110)]
    for p, name, ly in examples:
        s += line(xat(p), ly + 6, xat(p), y0 - 2, GREY, 1.2, dash="3 3")
        s += text(xat(p), ly, name, 11.5, INK, "middle", "bold")

    # кольорова смуга
    for i in range(15):
        s += rect(x0 + i * cell, y0, cell + 0.6, hbar, _PH_COLORS[i], "none", 0)
        col = GREEN if i == 7 else INK
        wgt = "bold" if i == 7 else "normal"
        s += text(x0 + (i + 0.5) * cell, y0 + hbar + 22, str(i), 12.5, col, "middle", wgt)
    s += rect(x0, y0, 15 * cell, hbar, "none", INK, 1.4)
    s += text(xat(7), y0 + hbar + 42, "7 — нейтрально (порівну)", 12, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "сходинки круті: кожен крок — удесятеро більше чи менше H⁺",
              12, GREY, "middle", style="italic")
    save("fig-4-2-3-1-ph-scale.svg", s)


# ── Рис. 4.2.3-2 — сік червоної капусти як індикатор ─────────────────────────
def tube(cx, top, w, h, fill):
    x, rb = cx - w / 2, w / 2
    path = (f'M{x:.1f},{top:.1f} L{x:.1f},{top + h - rb:.1f} '
            f'Q{x:.1f},{top + h:.1f} {cx:.1f},{top + h:.1f} '
            f'Q{x + w:.1f},{top + h:.1f} {x + w:.1f},{top + h - rb:.1f} L{x + w:.1f},{top:.1f}')
    s = f'<path d="{path} Z" fill="{fill}" stroke="none"/>\n'
    s += f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2.2"/>\n'
    return s


def fig_cabbage():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 32, "Сік червоної капусти показує pH кольором", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "той самий відвар: що кисліше — то червоніше, що лужніше — то зеленіше",
              12.5, GREY, "middle", style="italic")

    tubes = [(110, "#c0392b", "оцет, лимон", "кисле", RED),
             (240, "#d65f86", "газована вода", "", INK),
             (370, "#7b46a6", "чиста вода", "нейтрально", GREEN),
             (500, "#356fc0", "питна сода", "", INK),
             (630, "#1f8f86", "нашатир", "лужне", BLUE),
             (760, "#94a83a", "сильний луг", "", INK)]
    for cx, col, name, camp, ccol in tubes:
        s += tube(cx, 90, 60, 150, col)
        s += text(cx, 262, name, 12, INK, "middle", "bold")
        if camp:
            s += text(cx, 282, camp, 12, ccol, "middle", "bold")
    s += text(W / 2, H - 16, "колір замість числа: домашня шкала pH зі звичайної капусти",
              12.5, GREY, "middle", style="italic")
    save("fig-4-2-3-2-cabbage.svg", s)


if __name__ == "__main__":
    fig_secret()
    fig_strong_weak()
    fig_mirror()
    fig_slippery()
    fig_ph_scale()
    fig_cabbage()
