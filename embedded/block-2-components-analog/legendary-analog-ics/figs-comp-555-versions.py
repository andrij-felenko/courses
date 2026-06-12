# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки до теми 2.12.2 —
«NE555 і TLC555: біполярна проти CMOS-версії» (Модуль 2, Розділ 12, тема 2).

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
ОКРЕМИЙ скрипт: НЕ чіпає головний figs.py розділу й інші скрипти.
Імена SVG унікальні (префікс fig-r12-s2c-*), секція підписів — 2.12.2c.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано
з figs.py розділу 12 (єдиний вигляд між розділами).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
LGREY = "#f2f2f2"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{s}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Рис. 2.12.2c.1 — Дві версії того самого таймера: біполярна проти CMOS.
# Дві колонки-«картки» з ключовими цифрами + спільна цоколівка зверху.
# ---------------------------------------------------------------------------
def fig_two_families():
    W, H = 920, 470
    body = header(W, H)
    body += text(W / 2, 32, "Та сама схема, два процеси: біполярний NE555 і CMOS TLC555",
                 size=19, anchor="middle", weight="bold")

    # Спільна нагадка: однакова цоколівка DIP-8 (один корпус для обох)
    body += text(W / 2, 58, "однакова цоколівка DIP-8, однакові режими — різнить внутрішній транзистор",
                 size=13, anchor="middle", style="italic", color=GREY)

    cards = [
        # x0, заголовок, колір, рядки (мітка, значення)
        (60, "NE555 — біполярний (1972)", RED, LRED, [
            ("Транзистори всередині", "біполярні (BJT)"),
            ("Живлення VCC", "4.5 … 16 В"),
            ("Власний струм спокою", "≈ 3 … 6 мА"),
            ("Робоча частота (стеля)", "≈ 0.5 МГц"),
            ("Вихідний струм", "до ±200 мА"),
            ("Кидок при перемиканні", "великий (десятки мА)"),
            ("Мінімум живлення", "≈ 4.5 В"),
        ]),
        (490, "TLC555 — CMOS (1980-ті)", BLUE, LBLUE, [
            ("Транзистори всередині", "польові (MOSFET)"),
            ("Живлення VCC", "2 … 15 В"),
            ("Власний струм спокою", "≈ 0.17 … 0.25 мА"),
            ("Робоча частота (стеля)", "≈ 2 МГц"),
            ("Вихідний струм", "до +10 / −100 мА"),
            ("Кидок при перемиканні", "малий"),
            ("Мінімум живлення", "≈ 2 В (живиться від 2×AA)"),
        ]),
    ]

    cw, ch = 370, 372
    cy = 78
    for x0, title, col, light, rows in cards:
        body += rect(x0, cy, cw, ch, fill="#ffffff", stroke=col, sw=2.5, rx=12)
        body += rect(x0, cy, cw, 40, fill=light, stroke=col, sw=2.5, rx=12)
        body += rect(x0, cy + 26, cw, 14, fill=light, stroke="none")
        body += text(x0 + cw / 2, cy + 26, title, size=16, anchor="middle",
                     weight="bold", color=col)
        ry = cy + 70
        for lab, val in rows:
            body += text(x0 + 18, ry, lab, size=13.5, color=INK)
            body += text(x0 + cw - 18, ry, val, size=13.5, anchor="end",
                         weight="bold", color=col)
            body += line(x0 + 14, ry + 14, x0 + cw - 14, ry + 14, color=FAINT, w=1)
            ry += 44

    # підпис-висновок
    body += text(W / 2, H - 16,
                 "CMOS-версія платить тим самим: у ~20 разів менший власний струм, нижчий поріг "
                 "живлення й тихіше перемикання — ціною слабшого виходу.",
                 size=12.5, anchor="middle", style="italic", color=GREY)
    return body + footer()


# ---------------------------------------------------------------------------
# Рис. 2.12.2c.2 — «Голка» струму при перемиканні: наскрізний струм
# двотактного виходу. Зверху — миттєвий стан виходу, знизу — імпульс
# струму від живлення, що збігається з фронтами.
# ---------------------------------------------------------------------------
def fig_shoot_through():
    W, H = 920, 470
    body = header(W, H)
    body += text(W / 2, 30, "«Голки» струму: чому амперметр на живленні смикається на фронтах",
                 size=18.5, anchor="middle", weight="bold")

    # ---- ліворуч: двотактний (push-pull) вихідний каскад ----
    lx = 120
    body += text(lx, 64, "Вихідний каскад (двотактний)", size=14, anchor="middle", weight="bold")
    # шина +VCC
    body += line(lx - 70, 92, lx + 70, 92, color=RED, w=3)
    body += text(lx + 78, 96, "+VCC", size=13, color=RED, weight="bold")
    # шина GND
    body += line(lx - 70, 300, lx + 70, 300, color=BLUE, w=3)
    body += text(lx + 78, 304, "GND", size=13, color=BLUE, weight="bold")
    # верхній транзистор (до +)
    body += rect(lx - 26, 116, 52, 46, fill=LRED, stroke=RED, sw=2, rx=6)
    body += text(lx, 144, "верхній", size=12.5, anchor="middle", color=RED)
    body += line(lx, 92, lx, 116, color=RED, w=2)
    # нижній транзистор (до GND)
    body += rect(lx - 26, 230, 52, 46, fill=LBLUE, stroke=BLUE, sw=2, rx=6)
    body += text(lx, 258, "нижній", size=12.5, anchor="middle", color=BLUE)
    body += line(lx, 276, lx, 300, color=BLUE, w=2)
    # вузол виходу
    body += line(lx, 162, lx, 230, color=INK, w=2)
    body += circle(lx, 196, 3.5, fill=INK, stroke=INK, w=1)
    body += arrow(lx, 196, lx + 96, 196, color=INK, w=2)
    body += text(lx + 100, 200, "OUT", size=13, color=INK, weight="bold")
    # стрілка наскрізного струму (обидва прочинені на мить)
    body += arrow(lx + 40, 116 + 23, lx + 40, 230 + 23, color=GREEN, w=2.5, dash="5 4")
    body += text(lx + 46, 196, "наскрізний", size=12, color=GREEN, weight="bold")
    body += text(lx + 46, 212, "струм", size=12, color=GREEN, weight="bold")
    body += text(lx, 348, "На мить перемикання", size=12.5, anchor="middle", color=GREY)
    body += text(lx, 364, "ОБИДВА ще прочинені →", size=12.5, anchor="middle", color=GREEN, weight="bold")
    body += text(lx, 380, "коротка стежка +VCC→GND", size=12.5, anchor="middle", color=GREY)

    # ---- праворуч: осцилограма ----
    ox0, ox1 = 360, 880
    # верх: вихід OUT (прямокутник)
    yt_hi, yt_lo = 95, 150
    body += text(ox0 - 8, 78, "OUT", size=13, anchor="end", weight="bold")
    body += line(ox0, yt_lo + 16, ox1, yt_lo + 16, color=FAINT, w=1)
    edges = [ox0, ox0 + 150, ox0 + 300, ox0 + 450]
    # прямокутник: low, ↑, high, ↓, low...
    pts = [(ox0, yt_lo), (edges[1], yt_lo), (edges[1], yt_hi),
           (edges[2], yt_hi), (edges[2], yt_lo), (edges[3], yt_lo),
           (edges[3], yt_hi), (ox1, yt_hi)]
    body += polyline(pts, color=INK, w=2.5)

    # низ: струм від живлення ICC
    base = 300
    body += text(ox0 - 8, base - 60, "I від", size=12.5, anchor="end", weight="bold")
    body += text(ox0 - 8, base - 44, "живлення", size=12.5, anchor="end", weight="bold")
    body += line(ox0, base, ox1, base, color=GREY, w=1.5)
    body += text(ox1 + 6, base + 4, "t", size=13, color=GREY, style="italic")
    body += line(ox0, base, ox0, 250, color=GREY, w=1.5)
    # рівень спокою — невелика поличка
    quiet = base - 18
    body += line(ox0, quiet, ox1, quiet, color=BLUE, w=2, dash="6 4")
    body += text(ox1 - 4, quiet - 6, "струм спокою", size=11.5, anchor="end", color=BLUE)
    # голки струму на кожному фронті виходу
    for ex in edges[1:]:
        spike = [(ex - 14, quiet), (ex - 4, quiet), (ex, base - 95),
                 (ex + 4, quiet), (ex + 14, quiet)]
        body += polyline(spike, color=RED, w=2.5)
    body += text(edges[2], base - 108, "голка наскрізного струму", size=12.5,
                 anchor="middle", color=RED, weight="bold")
    # вертикальні пунктири: фронт ↔ голка
    for ex in edges[1:]:
        body += line(ex, yt_hi - 6, ex, base, color=FAINT, w=1, dash="3 4")

    body += text((ox0 + ox1) / 2, 196, "кожен фронт виходу → короткий імпульс струму від живлення",
                 size=12.5, anchor="middle", style="italic", color=GREY)

    # підпис-висновок
    body += text(W / 2, H - 16,
                 "Голки тривають десятки наносекунд, але заряджаються з шини живлення — тому їх "
                 "глушать конденсатором 100 нФ упритул до ніжок VCC–GND.",
                 size=12.5, anchor="middle", style="italic", color=GREY)
    return body + footer()


if __name__ == "__main__":
    save("fig-r12-s2c-1-ne555-vs-tlc555.svg", fig_two_families())
    save("fig-r12-s2c-2-shoot-through-spikes.svg", fig_shoot_through())
    print("done")
