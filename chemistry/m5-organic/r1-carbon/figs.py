# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 5.1 — «Карбон і його ланцюги» (Модуль 5).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §8): білий фон, sans-serif; атоми-кульки — C темно-сіра,
H біла з сірим контуром, O червона, N синя; зв'язки — сірі лінії.
Хелпери скопійовані (розділи не діляться файлами).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e9e9e9"
GREEN = "#1f8a3b"
C_FILL = "#454545"
C_LINE = "#2a2a2a"
H_FILL = "#ffffff"
H_LINE = "#9a9a9a"
O_FILL = "#d9483c"
O_LINE = "#9f2c22"
N_FILL = "#2c52b0"
N_LINE = "#1c3576"
BOND  = "#7c7c7c"
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#aInk)"/>\n')


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


def poly(points, color=INK, w=2, fill="none", close=True):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + (" Z" if close else "")
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"/>\n'


def hexagon(cx, cy, r, fill="none", stroke=INK, w=2):
    pts = [(cx + r * math.cos(math.radians(60 * k - 90)),
            cy + r * math.sin(math.radians(60 * k - 90))) for k in range(6)]
    return poly(pts, stroke, w, fill)


def bond(x1, y1, x2, y2, w=4):
    return line(x1, y1, x2, y2, BOND, w)


def atom(cx, cy, kind, r=14):
    spec = {"C": (C_FILL, C_LINE, "C", "#fff"), "H": (H_FILL, H_LINE, "H", INK),
            "O": (O_FILL, O_LINE, "O", "#fff"), "N": (N_FILL, N_LINE, "N", "#fff")}
    fill, ln, lab, lc = spec[kind]
    rr = r if kind != "H" else r * 0.66
    s = circle(cx, cy, rr, fill, ln, 1.8)
    s += text(cx, cy + rr * 0.36, lab, rr * 0.95, lc, "middle", "bold")
    return s


def double_bond(x1, y1, x2, y2, w=3.4, gap=4.2):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    px, py = -dy / L * gap, dx / L * gap
    return (line(x1 + px, y1 + py, x2 + px, y2 + py, BOND, w)
            + line(x1 - px, y1 - py, x2 - px, y2 - py, BOND, w))


def zigzag(x0, y0, n, dx=26, amp=12, r=12):
    """Скелет-ланцюг із n Карбонів; повертає svg."""
    pts = [(x0 + i * dx, y0 + (-amp if i % 2 else amp)) for i in range(n)]
    s = ""
    for i in range(n - 1):
        s += bond(*pts[i], *pts[i + 1])
    for x, y in pts:
        s += atom(x, y, "C", r)
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 5.1.1-1 — чотири руки + ланцюг/розгалуження/кільце ───────────────────
def fig_skeletons():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 30, "Карбон: чотири руки — і вміння братися за себе", 21, INK, "middle", "bold")
    s += text(W / 2, 52, "ланцюги, розгалуження, кільця — усе з того самого атома", 12.5, GREY, "middle", style="italic")

    # легенда — один C з чотирма руками (метан)
    cx, cy = 150, 150
    s += text(150, 92, "чотири руки", 14, INK, "middle", "bold")
    hs = [(cx - 40, cy - 34), (cx + 40, cy - 34), (cx - 40, cy + 34), (cx + 40, cy + 34)]
    for hx, hy in hs:
        s += bond(cx, cy, hx, hy)
    s += atom(cx, cy, "C", 17)
    for hx, hy in hs:
        s += atom(hx, hy, "H", 14)
    s += text(150, 232, "(валентність 4)", 11.5, GREY, "middle", style="italic")

    # три скелети
    base = 320
    # (a) ланцюг
    chain = [(360, base + 12), (400, base - 12), (440, base + 12), (480, base - 12)]
    for i in range(len(chain) - 1):
        s += bond(*chain[i], *chain[i + 1])
    for x, y in chain:
        s += atom(x, y, "C", 13)
    s += text(420, base + 60, "ланцюг", 13.5, INK, "middle", "bold")

    # (b) розгалуження
    bx = 600
    main = [(bx - 30, base + 12), (bx + 10, base - 12), (bx + 50, base + 12)]
    for i in range(len(main) - 1):
        s += bond(*main[i], *main[i + 1])
    s += bond(bx + 10, base - 12, bx + 10, base - 52)
    for x, y in main:
        s += atom(x, y, "C", 13)
    s += atom(bx + 10, base - 52, "C", 13)
    s += text(bx + 10, base + 60, "розгалуження", 13.5, INK, "middle", "bold")

    # (c) кільце (шестикутник)
    rx, ry, rr = 790, base - 4, 36
    ring = [(rx + rr * math.cos(math.radians(60 * k - 90)),
             ry + rr * math.sin(math.radians(60 * k - 90))) for k in range(6)]
    for i in range(6):
        s += bond(*ring[i], *ring[(i + 1) % 6])
    for x, y in ring:
        s += atom(x, y, "C", 12)
    s += text(rx, base + 60, "кільце", 13.5, INK, "middle", "bold")

    save("fig-5-1-1-1-skeletons.svg", s)


# ── Рис. 5.1.1-2 — катенація: лише Карбон тягне ланцюг без кінця ──────────────
def fig_catenation():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Рідкісний хист: Карбон чіпляється сам до себе без кінця", 19, INK, "middle", "bold")

    # Карбон — довгий ланцюг
    y = 110
    s += text(60, y + 5, "Карбон:", 14, INK, "start", "bold")
    xs = [180 + i * 64 for i in range(7)]
    for i in range(len(xs) - 1):
        s += bond(xs[i], y + (8 if i % 2 else -8), xs[i + 1], y + (-8 if i % 2 else 8))
    for i, x in enumerate(xs):
        s += atom(x, y + (-8 if i % 2 else 8), "C", 13)
    s += text(xs[-1] + 40, y + 5, "… і далі →", 13, GREEN, "start", "bold")

    # Оксиген — лише по двоє
    y = 200
    s += text(60, y + 5, "Оксиген:", 14, INK, "start", "bold")
    s += bond(190, y, 230, y)
    s += atom(190, y, "O", 14)
    s += atom(230, y, "O", 14)
    s += text(280, y + 5, "далі не хоче", 12.5, GREY, "start", style="italic")

    # Нітроген — лише по двоє
    y = 256
    s += text(60, y + 5, "Нітроген:", 14, INK, "start", "bold")
    s += bond(190, y, 230, y)
    s += atom(190, y, "N", 14)
    s += atom(230, y, "N", 14)
    s += text(280, y + 5, "далі не хоче", 12.5, GREY, "start", style="italic")

    s += text(W / 2, 302, "більшість елементів зчепляться по двоє — лише Карбон будує нескінченно",
              12.5, GREY, "middle", style="italic")
    save("fig-5-1-1-2-catenation.svg", s)


# ── Рис. 5.1.2-1 — драбина вуглеводнів за довжиною ────────────────────────────
def fig_ladder():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 30, "Драбина вуглеводнів: що довший ланцюг, то «важча» речовина", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "ті самі Карбон і Гідроген — лише різна довжина: газ → рідина → тверде",
              12.5, GREY, "middle", style="italic")

    # 1 — метан (з усіма Гідрогенами)
    cx, cy = 130, 158
    hs = [(cx - 34, cy - 30), (cx + 34, cy - 30), (cx - 34, cy + 30), (cx + 34, cy + 30)]
    for hx, hy in hs:
        s += bond(cx, cy, hx, hy)
    s += atom(cx, cy, "C", 16)
    for hx, hy in hs:
        s += atom(hx, hy, "H", 13)
    s += text(130, 250, "метан", 14, INK, "middle", "bold")
    s += text(130, 268, "1 Карбон · газ", 11.5, GREY, "middle")
    s += text(130, 284, "плита", 11.5, GREEN, "middle", "bold")

    # 2 — пропан (скелет)
    s += zigzag(300, 158, 3, 30, 16, 13)
    s += text(330, 250, "пропан", 14, INK, "middle", "bold")
    s += text(330, 268, "3 Карбони · газ", 11.5, GREY, "middle")
    s += text(330, 284, "балон", 11.5, GREEN, "middle", "bold")

    # 3 — бензин (скелет ~7 C)
    s += zigzag(500, 158, 7, 25, 14, 12)
    s += text(572, 250, "бензин", 14, INK, "middle", "bold")
    s += text(572, 268, "~7 Карбонів · рідина", 11.5, GREY, "middle")
    s += text(572, 284, "бак", 11.5, GREEN, "middle", "bold")

    # 4 — віск (довгий скелет)
    s += zigzag(720, 158, 11, 16, 11, 10)
    s += text(810, 250, "віск, асфальт", 14, INK, "middle", "bold")
    s += text(810, 268, "довгі ланцюги · тверде", 11.5, GREY, "middle")

    s += text(W / 2, 332, "біля кожного Карбону є Гідрогени — тут показані лише в метані",
              12, GREY, "middle", style="italic")
    save("fig-5-1-2-1-ladder.svg", s)


# ── Рис. 5.1.2-2 — насичене vs ненасичене ────────────────────────────────────
def fig_saturation():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 30, "Насичене й ненасичене: де є «запасна рука»", 20, INK, "middle", "bold")

    # ліворуч — етан (насичене)
    c1, c2, y = 185, 260, 162
    s += bond(c1 + 16, y, c2 - 16, y)
    for hx, hy in [(155, 138), (155, 186), (185, 118)]:
        s += bond(c1, y, hx, hy)
        s += atom(hx, hy, "H", 12)
    for hx, hy in [(290, 138), (290, 186), (260, 118)]:
        s += bond(c2, y, hx, hy)
        s += atom(hx, hy, "H", 12)
    s += atom(c1, y, "C", 15)
    s += atom(c2, y, "C", 15)
    s += text(222, 246, "насичене — етан", 13.5, INK, "middle", "bold")
    s += text(222, 264, "усі руки тримають водень", 11.5, GREY, "middle")
    s += text(222, 280, "спокійне, не приєднує", 11.5, GREY, "middle", style="italic")

    s += line(410, 80, 410, 296, FAINT, 2, dash="5 5")

    # праворуч — етен (ненасичене)
    c1, c2, y = 560, 635, 162
    s += double_bond(c1 + 16, y, c2 - 16, y)
    for hx, hy in [(530, 138), (530, 186)]:
        s += bond(c1, y, hx, hy)
        s += atom(hx, hy, "H", 12)
    for hx, hy in [(665, 138), (665, 186)]:
        s += bond(c2, y, hx, hy)
        s += atom(hx, hy, "H", 12)
    s += atom(c1, y, "C", 15)
    s += atom(c2, y, "C", 15)
    s += text(597, 118, "подвійний зв'язок", 12, GREEN, "middle", "bold")
    # вхідний атом — «готовий приєднати»
    s += arrow(720, 214, 622, 180, GREEN, 2.2)
    s += text(742, 220, "новий атом", 11.5, GREEN, "start", "bold")
    s += text(597, 246, "ненасичене — етен", 13.5, INK, "middle", "bold")
    s += text(597, 264, "подвійний зв'язок = запасна рука", 11.5, GREY, "middle")
    s += text(597, 280, "радо приєднує нове", 11.5, GREY, "middle", style="italic")

    s += text(W / 2, 314, "насичене нічого не хоче; ненасичене розкриває подвійний зв'язок — звідси пластики",
              12, GREY, "middle", style="italic")
    save("fig-5-1-2-2-saturation.svg", s)


def _ethene(cx, cy, dbond=True):
    c1, c2 = (cx - 20, cy), (cx + 20, cy)
    s = double_bond(c1[0] + 14, cy, c2[0] - 14, cy) if dbond else bond(c1[0] + 14, cy, c2[0] - 14, cy)
    for hx, hy in [(cx - 42, cy - 22), (cx - 42, cy + 22)]:
        s += bond(c1[0], cy, hx, hy) + atom(hx, hy, "H", 10)
    for hx, hy in [(cx + 42, cy - 22), (cx + 42, cy + 22)]:
        s += bond(c2[0], cy, hx, hy) + atom(hx, hy, "H", 10)
    s += atom(c1[0], cy, "C", 14) + atom(c2[0], cy, "C", 14)
    return s


# ── Рис. 5.1.3-1 — полімеризація: намистини в ланцюг ─────────────────────────
def fig_polymerize():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Як виходить пластик: намистини зшиваються в ланцюг", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "розкрий подвійний зв'язок у кожного етилену — і вони беруться за руки",
              12.5, GREY, "middle", style="italic")

    s += text(W / 2, 88, "мономери — намистини етилену (з подвійним зв'язком)", 13, INK, "middle", "bold")
    for cx in (250, 450, 650):
        s += _ethene(cx, 130, dbond=True)
    s += text(770, 135, "…", 22, GREY, "start", "bold")

    s += arrow(450, 168, 450, 212, GREEN, 2.6)
    s += text(470, 196, "подвійні зв'язки розкриваються", 12.5, GREEN, "start", "bold")

    # полімер — суцільний ланцюг
    n, x0, dx, y0, amp = 8, 250, 50, 300, 16
    pts = [(x0 + i * dx, y0 + (-amp if i % 2 else amp)) for i in range(n)]
    for i in range(n - 1):
        col = GREEN if i % 2 else BOND      # зелені — нові «защіпки» між намистинами
        s += line(*pts[i], *pts[i + 1], col, 4)
    for i, (x, y) in enumerate(pts):
        hy1, hy2 = y - 26, y + 26
        s += bond(x, y, x, hy1) + bond(x, y, x, hy2)
        s += atom(x, hy1, "H", 9) + atom(x, hy2, "H", 9)
        s += atom(x, y, "C", 12)
    # дужка однієї ланки
    s += line(pts[2][0] - 8, 356, pts[3][0] + 8, 356, INK, 1.6)
    s += line(pts[2][0] - 8, 352, pts[2][0] - 8, 356, INK, 1.6)
    s += line(pts[3][0] + 8, 352, pts[3][0] + 8, 356, INK, 1.6)
    s += text((pts[2][0] + pts[3][0]) / 2, 372, "ланка = колишня намистина", 11.5, INK, "middle", style="italic")
    s += text(740, 300, "…", 22, GREY, "start", "bold")
    s += text(150, 300, "полімер:", 13.5, GREEN, "middle", "bold")
    s += text(150, 318, "поліетилен", 12, INK, "middle", "bold")
    save("fig-5-1-3-1-polymerize.svg", s)


# ── Рис. 5.1.3-2 — чому пластик не гниє ──────────────────────────────────────
def _enzyme(cx, cy, blocked=False):
    s = poly([(cx - 14, cy - 12), (cx + 6, cy), (cx - 14, cy + 12)], GREEN, 2, "#dff0e4")
    s += text(cx - 6, cy + 28, "фермент", 10.5, GREEN, "middle", "bold")
    if blocked:
        s += line(cx - 16, cy - 14, cx + 8, cy + 14, "#c0271e", 3)
        s += line(cx + 8, cy - 14, cx - 16, cy + 14, "#c0271e", 3)
    return s


def fig_no_rot():
    W, H = 840, 340
    s = header(W, H)
    s += text(W / 2, 30, "Чому пластик не гниє", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "свої ланцюги природа ріже ферментами, а такого — не вміє", 12.5, GREY, "middle", style="italic")

    # ліворуч — природний ланцюг (кільця), його ріжуть
    s += text(210, 96, "природний ланцюг (їжа, дерево)", 13, INK, "middle", "bold")
    hx = [120, 180, 250, 310]
    for i in range(len(hx) - 1):
        gap = i == 1
        if not gap:
            s += line(hx[i] + 22, 160, hx[i + 1] - 22, 160, BOND, 4)
    for x in hx:
        s += hexagon(x, 160, 22, "#eaf3ee", "#4f9a92", 2.4)
    s += _enzyme(215, 130)
    s += line(213, 150, 213, 174, "#c0271e", 2, dash="3 3")
    s += text(210, 210, "мікроб має ножиці саме на ці ланки", 11.5, GREEN, "middle", "bold")
    s += text(210, 226, "→ ріже, ланцюг гниє", 11.5, GREY, "middle", style="italic")

    s += line(420, 80, 420, 286, FAINT, 2, dash="5 5")

    # праворуч — пластиковий ланцюг, ножиці не беруть
    s += text(620, 96, "пластиковий ланцюг", 13, INK, "middle", "bold")
    n, x0, dx, y0, amp = 7, 540, 26, 160, 13
    pts = [(x0 + i * dx, y0 + (-amp if i % 2 else amp)) for i in range(n)]
    for i in range(n - 1):
        s += bond(*pts[i], *pts[i + 1])
    for x, y in pts:
        s += atom(x, y, "C", 11)
    s += _enzyme(625, 120, blocked=True)
    s += text(620, 210, "природа таких не робила", 11.5, "#c0271e", "middle", "bold")
    s += text(620, 226, "→ різати нема чим, лежить століттями", 11.5, GREY, "middle", style="italic")

    s += text(W / 2, 312, "вихід: переробляти (плавити й формувати знову) або робити ланцюги, які мікроби ріжуть",
              12, GREY, "middle", style="italic")
    save("fig-5-1-3-2-no-rot.svg", s)


if __name__ == "__main__":
    fig_skeletons()
    fig_catenation()
    fig_ladder()
    fig_saturation()
    fig_polymerize()
    fig_no_rot()
