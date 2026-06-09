# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 10 — «Діод і PN-перехід» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Підписи посекційно (Рис. C.S.N); для історії до розділу —
секція 0 (Рис. 10.0.N). Допоміжні функції скопійовано з попередніх розділів
(єдиний вигляд).
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def _ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=2):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return circle(cx, cy, r, "none", color, w) + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


def _sine(ox, oy, w, amp, cycles, col, wv=2.4, phase=0.0):
    pts = []
    for j in range(0, int(w) + 1):
        t = j / w
        y = oy - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((ox + j, y))
    return _poly(pts, col, wv)


def _halfwave(ox, oy, w, amp, cycles, col, wv=2.6):
    pts = []
    for j in range(0, int(w) + 1):
        t = j / w
        v = math.sin(2 * math.pi * cycles * t)
        y = oy - amp * max(0.0, v)
        pts.append((ox + j, y))
    return _poly(pts, col, wv)


# ── Рис. 10.0.1 — таймлайн (ланцюг питань) ───────────────────────────────────
def fig_timeline():
    W, H = 880, 250
    s = header(W, H)
    s += text(W / 2, 34, "Ланцюг питань: як камінь став клапаном для струму", 19, INK, "middle", "bold")
    boxes = [
        ("1874 · Браун", ["Камінь пропускає", "струм лише", "в один бік?"], "#fbfbfb"),
        ("1894–1906 · котячий вус", ["Кристал", "ловить радіо?"], "#fbfbfb"),
        ("~1910–1930 · лампа", ["Чому крихкий", "кристал", "закинули?"], "#fbfbfb"),
        ("1939 · Рассел Ол", ["Чистий кремній:", "межа всередині"], "#fbfbfb"),
        ("Розділ 10", ["Однобічний клапан", "— діод і", "PN-перехід"], LGRN),
    ]
    bw, gap, by, bh = 150, 20, 92, 100
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 18 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 11.5, INK, "middle", "bold")
        border = "#9bb0c2" if fill == LGRN else "#c9d3dc"
        s += rect(bx, by, bw, bh, fill, border, 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 34 + k * 20, ln, 11.5, INK, "middle")
        if i < len(boxes) - 1:
            ax = bx + bw
            s += arrow(ax + 2, by + bh / 2, ax + gap - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14, "Кожен щабель — нове питання. Сірим — те, що стане змістом Розділу 10.",
              11, GREY, "middle", style="italic")
    save("fig-10-0-1-timeline.svg", s)


# ── Рис. 10.0.2 — котячий вус ────────────────────────────────────────────────
def fig_cat_whisker():
    W, H = 780, 330
    s = header(W, H)
    s += text(W / 2, 30, "Котячий вус: кристал пропускає струм в один бік", 18, INK, "middle", "bold")
    # тримач і кристал
    s += rect(120, 215, 110, 26, "#d9c9a8", INK, 1.6, 4)
    s += text(175, 233, "тримач", 9.5, INK, "middle")
    cr = "M 135,215 L 150,182 L 172,190 L 190,176 L 208,196 L 215,215 Z"
    s += f'<path d="{cr}" fill="#b9bfc6" stroke="{INK}" stroke-width="1.8"/>\n'
    s += text(175, 208, "галеніт", 10, INK, "middle", "bold")
    # котячий вус (пружний дріт) до точки контакту
    s += _poly([(300, 95), (285, 120), (250, 120), (225, 150), (196, 178)], COPP, 2)
    s += circle(196, 178, 3, COPP, COPP)
    s += text(312, 98, "котячий вус", 10.5, COPP, "start", "bold")
    s += text(312, 113, "(тонкий дріт)", 9.5, GREY, "start")
    s += arrow(258, 168, 205, 179, GREY, 1.6)
    s += text(260, 165, "точковий контакт", 9.5, INK, "start")
    # виводи
    s += line(120, 228, 80, 228, INK, 2)
    s += line(80, 228, 80, 150, INK, 2)
    s += line(300, 95, 300, 70, INK, 2)
    s += text(78, 142, "до навушника", 9.5, GREY, "start")
    # праворуч — випрямлення
    ox = 430
    s += text(ox + 130, 78, "вхід: змінний сигнал з антени", 10.5, INK, "middle", "bold")
    s += line(ox, 120, ox + 260, 120, GREY, 1)
    s += _sine(ox, 120, 260, 30, 3, BLUE, 2.4)
    s += arrow(ox + 130, 162, ox + 130, 206, GREEN, 2.2)
    s += text(ox + 140, 188, "кристал-клапан", 10, GREEN, "start", "bold")
    s += text(ox + 130, 236, "вихід: струм лише в один бік", 10.5, INK, "middle", "bold")
    s += line(ox, 300, ox + 260, 300, GREY, 1)
    s += _halfwave(ox, 300, 260, 46, 3, RED, 2.6)
    save("fig-10-0-2-cat-whisker.svg", s)


# ── Рис. 10.0.3 — лампа проти кристала ───────────────────────────────────────
def fig_tube_vs_crystal():
    W, H = 780, 300
    s = header(W, H)
    s += text(W / 2, 28, "Лампа підсилює, але гаряча; кристал холодний, та не підсилює", 16, INK, "middle", "bold")
    # ліва панель — лампа
    s += _frame(40, 60, 330, 210, "Електронна лампа (тріод)")
    s += _ellipse(150, 150, 46, 66, "#eef2f6", INK, 1.8)
    s += _poly([(150, 120), (140, 135), (160, 150), (140, 165), (155, 180)], RED, 2)
    s += line(150, 84, 150, 104, INK, 2)
    s += text(150, 238, "розжарена нитка у вакуумі,", 9.5, INK, "middle")
    s += text(150, 253, "крихка скляна колба", 9.5, INK, "middle")
    s += text(228, 122, "+ підсилює", 11.5, GREEN, "start", "bold")
    s += text(228, 150, "− гаряча", 11, RED, "start", "bold")
    s += text(228, 172, "− крихка", 11, RED, "start", "bold")
    s += text(228, 194, "− їсть струм", 11, RED, "start", "bold")
    # права панель — кристал
    s += _frame(410, 60, 330, 210, "Кристал + котячий вус")
    s += rect(470, 196, 80, 22, "#d9c9a8", INK, 1.4, 3)
    s += f'<path d="M 480,196 L 492,172 L 510,179 L 525,168 L 540,196 Z" fill="#b9bfc6" stroke="{INK}" stroke-width="1.6"/>\n'
    s += _poly([(560, 112), (545, 132), (520, 137), (500, 162), (508, 178)], COPP, 1.8)
    s += circle(508, 178, 2.6, COPP, COPP)
    s += text(508, 238, "крихітний кристал,", 9.5, INK, "middle")
    s += text(508, 253, "тонкий дріт", 9.5, INK, "middle")
    s += text(590, 122, "+ холодний", 11, GREEN, "start", "bold")
    s += text(590, 144, "+ простий", 11, GREEN, "start", "bold")
    s += text(590, 172, "− не підсилює", 11, RED, "start", "bold")
    s += text(590, 194, "− примхливий", 11, RED, "start", "bold")
    save("fig-10-0-3-tube-vs-crystal.svg", s)


# ── Рис. 10.0.4 — Ол і PN-перехід ────────────────────────────────────────────
def fig_ohl_junction():
    W, H = 780, 330
    s = header(W, H)
    s += text(W / 2, 28, "1939: Рассел Ол і випадковий PN-перехід у кремнії", 18, INK, "middle", "bold")
    # сонце й промені
    s += circle(110, 78, 15, "#fce9c0", SUN, 2)
    s += text(110, 104, "світло", 10.5, COPP, "middle", "bold")
    for k in range(4):
        s += line(165 + k * 88, 66, 192 + k * 88, 128, SUN, 2)
    # кремнієвий брусок: p | n
    s += rect(180, 132, 180, 66, LRED, INK, 1.8)
    s += rect(360, 132, 180, 66, LBLUE, INK, 1.8)
    s += line(360, 132, 360, 198, INK, 2, dash="5,4")
    s += text(270, 176, "p", 22, RED, "middle", "bold")
    s += text(450, 176, "n", 22, BLUE, "middle", "bold")
    s += text(270, 150, "надлишок дірок", 8.5, GREY, "middle")
    s += text(450, 150, "надлишок електронів", 8.5, GREY, "middle")
    s += arrow(360, 232, 360, 202, INK, 1.8)
    s += text(360, 248, "PN-перехід (природна межа у зливку)", 11, INK, "middle", "bold")
    # контакти й вимірювальна петля знизу
    s += rect(176, 192, 12, 10, INK, INK, 1)
    s += rect(532, 192, 12, 10, INK, INK, 1)
    s += line(182, 202, 182, 286, INK, 2)
    s += line(182, 286, 344, 286, INK, 2)
    s += circle(360, 286, 16, "#ffffff", INK, 1.8)
    s += text(360, 290, "мкА", 9, INK, "middle", "bold")
    s += line(376, 286, 538, 286, INK, 2)
    s += line(538, 286, 538, 202, INK, 2)
    # анотація
    s += text(W - 28, 150, "Під світлом", 11, GREEN, "end", "bold")
    s += text(W - 28, 166, "сам з'являється струм", 11, GREEN, "end", "bold")
    s += text(W - 28, 184, "(фотоефект →", 9.5, GREY, "end")
    s += text(W - 28, 197, "сонячний елемент)", 9.5, GREY, "end")
    save("fig-10-0-4-ohl-junction.svg", s)


# ── Рис. 10.0.5 — однобічний клапан ──────────────────────────────────────────
def fig_one_way_valve():
    W, H = 780, 300
    s = header(W, H)
    s += text(W / 2, 28, "Суть діода: однобічний клапан для струму", 18, INK, "middle", "bold")

    def diode(cx, cy, col):
        t = f'<path d="M {cx-14},{cy-13} L {cx-14},{cy+13} L {cx+10},{cy} Z" fill="{col}" stroke="{col}" stroke-width="1.5"/>\n'
        t += line(cx + 10, cy - 14, cx + 10, cy + 14, col, 3)
        return t

    # ── ліва панель: пряме ──
    s += _frame(40, 56, 330, 200, "Пряме зміщення: струм тече")
    s += line(95, 130, 150, 130, INK, 2)
    s += diode(165, 130, GREEN)
    s += line(180, 130, 305, 130, INK, 2)
    s += line(305, 130, 305, 215, INK, 2)
    s += line(305, 215, 95, 215, INK, 2)
    s += line(95, 215, 95, 130, INK, 2)
    # батарея на лівій стійці (+ зверху)
    s += line(82, 162, 108, 162, INK, 3)
    s += line(88, 176, 102, 176, INK, 2)
    s += text(116, 160, "+", 13, RED, "start", "bold")
    s += text(116, 184, "−", 13, BLUE, "start", "bold")
    # струм за годинниковою (зелені стрілки)
    s += arrow(95, 152, 95, 134, GREEN, 2)
    s += arrow(215, 130, 255, 130, GREEN, 2)
    s += arrow(305, 175, 305, 205, GREEN, 2)
    s += arrow(255, 215, 210, 215, GREEN, 2)
    s += text(200, 245, "струм тече", 13, GREEN, "middle", "bold")
    # ── права панель: зворотне ──
    bx = 410
    s += _frame(bx, 56, 330, 200, "Зворотне зміщення: струм заблоковано")
    s += line(bx + 55, 130, bx + 110, 130, INK, 2)
    s += diode(bx + 125, 130, RED)
    s += line(bx + 140, 130, bx + 265, 130, INK, 2)
    s += line(bx + 265, 130, bx + 265, 215, INK, 2)
    s += line(bx + 265, 215, bx + 55, 215, INK, 2)
    s += line(bx + 55, 215, bx + 55, 130, INK, 2)
    # батарея перевернута (− зверху)
    s += line(bx + 42, 162, bx + 68, 162, INK, 2)
    s += line(bx + 48, 176, bx + 62, 176, INK, 3)
    s += text(bx + 76, 160, "−", 13, BLUE, "start", "bold")
    s += text(bx + 76, 184, "+", 13, RED, "start", "bold")
    # перекреслений шлях (червоне «стоп»)
    s += line(bx + 175, 112, bx + 205, 148, RED, 3)
    s += line(bx + 205, 112, bx + 175, 148, RED, 3)
    s += text(bx + 160, 245, "струму немає", 13, RED, "middle", "bold")
    save("fig-10-0-5-one-way-valve.svg", s)


# ── допоміжне для §10.1 ──────────────────────────────────────────────────────
_SUP = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def _sup(n):
    return "".join(_SUP[c] for c in str(n))


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


# ── Рис. 10.1.1 — шкала питомого опору ───────────────────────────────────────
def fig11_resistivity_spectrum():
    W, H = 840, 270
    s = header(W, H)
    s += text(W / 2, 32, "Питомий опір: провідники, напівпровідники, ізолятори", 17, INK, "middle", "bold")
    x0, x1, e0, e1, ax_y = 80, 780, -8, 14, 190

    def X(e):
        return x0 + (e - e0) / (e1 - e0) * (x1 - x0)

    bands = [(-8, -2, "#e7f3ea", GREEN, "провідники"),
             (-2, 6, "#fdf1dc", SUN, "напівпровідники"),
             (6, 14, "#eaeefb", BLUE, "ізолятори")]
    for a, b, fill, bc, lab in bands:
        s += rect(X(a), 130, X(b) - X(a), 36, fill, bc, 1.2)
        s += text((X(a) + X(b)) / 2, 153, lab, 11.5, bc, "middle", "bold")
    s += arrow(x0 - 10, ax_y, x1 + 14, ax_y, INK, 2)
    s += text(x1 + 16, ax_y + 4, "ρ, Ом·м", 12, INK, "start", "bold")
    for e in range(-8, 15, 2):
        s += line(X(e), ax_y - 4, X(e), ax_y + 4, INK, 1.4)
    for e in (-8, -4, 0, 4, 8, 12):
        s += text(X(e), ax_y + 20, "10" + _sup(e), 10.5, INK, "middle")

    def mk(e, lab, col):
        t = line(X(e), 112, X(e), ax_y, col, 1.6, dash="3,3")
        t += circle(X(e), 112, 4, col, col)
        t += text(X(e), 104, lab, 11, col, "middle", "bold")
        return t

    s += mk(-8, "мідь", GREEN)
    s += mk(0, "германій", "#9c6a16")
    s += mk(3, "кремній", "#9c6a16")
    s += mk(12, "скло", BLUE)
    s += text(W / 2, H - 16, "Логарифмічна шкала: кожен крок — у 10 разів. Від міді до скла — двадцять порядків.",
              11, GREY, "middle", style="italic")
    save("fig-10-1-1-resistivity-spectrum.svg", s)


# ── Рис. 10.1.2 — ґратка кремнію ─────────────────────────────────────────────
def fig11_silicon_lattice():
    W, H = 620, 400
    s = header(W, H)
    s += text(W / 2, 32, "Кремній: кожен атом ділить електрони з чотирма сусідами", 16, INK, "middle", "bold")
    xs, ys, r = [170, 310, 450], [108, 212, 316], 22
    pts = {}
    for j, yy in enumerate(ys):
        for i, xx in enumerate(xs):
            pts[(i, j)] = (xx, yy)

    def bond(p, q):
        (x1, y1), (x2, y2) = pts[p], pts[q]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        ox, oy = -uy * 3, ux * 3
        ax, ay = x1 + ux * r, y1 + uy * r
        bx, by = x2 - ux * r, y2 - uy * r
        t = line(ax + ox, ay + oy, bx + ox, by + oy, INK, 1.6)
        t += line(ax - ox, ay - oy, bx - ox, by - oy, INK, 1.6)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        t += circle(mx + ox * 1.7, my + oy * 1.7, 3, BLUE, BLUE)
        t += circle(mx - ox * 1.7, my - oy * 1.7, 3, BLUE, BLUE)
        return t

    for j in range(3):
        for i in range(3):
            if i < 2:
                s += bond((i, j), (i + 1, j))
            if j < 2:
                s += bond((i, j), (i, j + 1))
    for (i, j), (xx, yy) in pts.items():
        s += circle(xx, yy, r, "#eef2f6", INK, 2)
        s += text(xx, yy + 5, "Si", 13, INK, "middle", "bold")
    s += text(W / 2, H - 30, "Спрощено у 2D. Сині крапки — спільні електрони у зв'язках.", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "У холодному кристалі всі електрони зайняті — вільних носіїв немає.", 10.5, GREY, "middle", style="italic")
    save("fig-10-1-2-silicon-lattice.svg", s)


# ── Рис. 10.1.3 — розірваний зв'язок ─────────────────────────────────────────
def fig11_broken_bond():
    W, H = 640, 330
    s = header(W, H)
    s += text(W / 2, 30, "Тепло чи світло розриває зв'язок — народжується вільний носій", 15.5, INK, "middle", "bold")
    ax, ay, r = [160, 320, 480], 195, 24

    def dbond(x1, x2, y, both=True):
        a, b = x1 + r, x2 - r
        t = line(a, y - 3, b, y - 3, INK, 1.6) + line(a, y + 3, b, y + 3, INK, 1.6)
        mx = (a + b) / 2
        t += circle(mx, y - 9, 3, BLUE, BLUE)
        if both:
            t += circle(mx, y + 9, 3, BLUE, BLUE)
        return t, mx

    b0, _ = dbond(ax[0], ax[1], ay, True)
    s += b0
    b1, mx1 = dbond(ax[1], ax[2], ay, False)
    s += b1
    # порожнеча на місці зниклого електрона
    s += circle(mx1, ay + 9, 5, "none", RED, 1.6)
    s += text(mx1, ay + 34, "порожнеча", 9.5, RED, "middle", "bold")
    s += text(mx1, ay + 47, "(дірка — §10.2)", 9, GREY, "middle")
    # вільний електрон полетів
    s += arrow(mx1, ay + 6, mx1 + 58, ay - 68, BLUE, 2)
    s += circle(mx1 + 58, ay - 68, 5, BLUE, BLUE)
    s += text(mx1 + 66, ay - 72, "вільний електрон", 10, BLUE, "start", "bold")
    # вхід енергії
    s += circle(mx1 - 12, 78, 13, "#fce9c0", SUN, 2)
    s += text(mx1 - 12, 62, "тепло / світло", 10, COPP, "middle", "bold")
    s += line(mx1 - 12, 92, mx1, ay - 4, SUN, 2)
    for x in ax:
        s += circle(x, ay, r, "#eef2f6", INK, 2)
        s += text(x, ay + 5, "Si", 13, INK, "middle", "bold")
    save("fig-10-1-3-broken-bond.svg", s)


# ── Рис. 10.1.4 — енергетична щілина ─────────────────────────────────────────
def fig11_energy_gap():
    W, H = 860, 330
    s = header(W, H)
    s += text(W / 2, 30, "Енергетична щілина: що менша, то легше звільнити електрон", 16, INK, "middle", "bold")

    def panel(px, title, gap, jumped, note, tcol):
        bw, vy, bh = 170, 250, 28
        cy = vy - gap - bh
        t = text(px + bw / 2, 58, title, 13, tcol, "middle", "bold")
        t += rect(px, vy, bw, bh, "#e9eefb", BLUE, 1.4)
        t += text(px + bw / 2, vy + bh + 15, "зв'язані (валентна)", 9, GREY, "middle")
        t += rect(px, cy, bw, bh, "#e7f3ea", GREEN, 1.4)
        t += text(px + bw / 2, cy - 7, "вільні (провідність)", 9, GREY, "middle")
        for k in range(5):
            t += circle(px + 24 + k * 33, vy + bh / 2, 3.5, BLUE, BLUE)
        for k in range(jumped):
            t += circle(px + 55 + k * 60, cy + bh / 2, 3.5, GREEN, GREEN)
            t += arrow(px + 55 + k * 60, vy + bh / 2 - 4, px + 55 + k * 60, cy + bh / 2 + 6, SUN, 1.6)
        if gap >= 10:
            t += line(px + bw + 6, cy + bh, px + bw + 6, vy, INK, 1.2)
        t += text(px + bw + 10, (cy + bh + vy) / 2 + 4, note, 9.5, tcol, "start", "bold")
        return t

    s += panel(50, "Провідник", 2, 0, "немає", GREEN)
    s += panel(340, "Напівпровідник", 32, 2, "≈1.1 еВ", "#9c6a16")
    s += panel(630, "Ізолятор", 86, 0, "≈5.5 еВ", BLUE)
    s += text(W / 2, H - 14, "Сині електрони сидять у валентній зоні; щоб стати вільними (зелені), мусять подолати щілину.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-1-4-energy-gap.svg", s)


# ── Рис. 10.1.5 — опір і температура ─────────────────────────────────────────
def fig11_temp_dependence():
    W, H = 680, 330
    s = header(W, H)
    s += text(W / 2, 30, "Опір і температура: метал і напівпровідник — протилежно", 16, INK, "middle", "bold")
    ox, oy, w, h = 90, 270, 500, 200
    s += _axes(ox, oy, w, h, "температура", "опір R")
    metal = [(ox + w * (i / 40), oy - h * (0.22 + 0.5 * (i / 40))) for i in range(41)]
    s += _poly(metal, BLUE, 2.8)
    s += text(ox + w * 0.72, oy - h * (0.22 + 0.5 * 0.72) - 12, "метал ↑", 11.5, BLUE, "middle", "bold")
    semi = [(ox + w * (i / 60), oy - h * (0.95 * math.exp(-3.2 * (i / 60)) + 0.03)) for i in range(61)]
    s += _poly(semi, GREEN, 2.8)
    s += text(ox + w * 0.44, oy - h * 0.52, "напівпровідник ↓", 11.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Метал гарячим проводить гірше (опір росте); напівпровідник — краще: тепло звільняє носії.",
              10, GREY, "middle", style="italic")
    save("fig-10-1-5-temp-dependence.svg", s)


# ── Рис. 10.1.6 — керована провідність ───────────────────────────────────────
def fig11_controllable():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 32, "Провідність кремнію — ручка, яку крутять чотири важелі", 16.5, INK, "middle", "bold")
    bx, by, bw = 150, 215, 400
    s += line(bx, by, bx + bw, by, INK, 3)
    s += text(bx - 8, by + 5, "ізолятор", 10.5, BLUE, "end", "bold")
    s += text(bx + bw + 8, by + 5, "провідник", 10.5, GREEN, "start", "bold")
    kx = bx + bw * 0.5
    s += circle(kx, by, 11, "#fdf1dc", SUN, 2.5)
    s += text(kx, by + 26, "кремній", 11, "#9c6a16", "middle", "bold")
    s += arrow(kx - 34, by, kx - 14, by, GREY, 1.6)
    s += arrow(kx + 34, by, kx + 14, by, GREY, 1.6)
    for lab, lx in [("температура", 195), ("світло", 305), ("домішки", 415), ("напруга", 520)]:
        s += text(lx, 120, lab, 10.5, INK, "middle", "bold")
        s += arrow(lx, 128, kx, by - 14, SUN, 1.7)
    s += text(W / 2, H - 16, "Мідь і скло такої ручки не мають: вони назавжди «так» і «ні».",
              11, GREY, "middle", style="italic")
    save("fig-10-1-6-controllable.svg", s)


# ── допоміжне для §10.2 (носії та іони) ──────────────────────────────────────
def el(x, y):
    return circle(x, y, 7, BLUE, BLUE) + line(x - 3.5, y, x + 3.5, y, "#ffffff", 1.6)


def ho(x, y):
    return (circle(x, y, 7, "#ffffff", RED, 2)
            + line(x - 3, y, x + 3, y, RED, 1.4) + line(x, y - 3, x, y + 3, RED, 1.4))


def ion_p(x, y):
    return (circle(x, y, 8, "none", "#d2b8b5", 1.4)
            + line(x - 3.5, y, x + 3.5, y, "#d2b8b5", 1.4) + line(x, y - 3.5, x, y + 3.5, "#d2b8b5", 1.4))


def ion_n(x, y):
    return circle(x, y, 8, "none", "#b6c0d2", 1.4) + line(x - 3.5, y, x + 3.5, y, "#b6c0d2", 1.4)


def _bond2(x1, y1, x2, y2, r, dots=2):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    ox, oy = -uy * 3, ux * 3
    ax, ay = x1 + ux * r, y1 + uy * r
    bx, by = x2 - ux * r, y2 - uy * r
    t = line(ax + ox, ay + oy, bx + ox, by + oy, INK, 1.6) + line(ax - ox, ay - oy, bx - ox, by - oy, INK, 1.6)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    if dots >= 1:
        t += circle(mx + ox * 1.7, my + oy * 1.7, 3, BLUE, BLUE)
    if dots >= 2:
        t += circle(mx - ox * 1.7, my - oy * 1.7, 3, BLUE, BLUE)
    return t, (mx - ox * 1.7, my - oy * 1.7)


# ── Рис. 10.2.1 — рух дірки ──────────────────────────────────────────────────
def fig21_hole_motion():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Дірка рухається, коли електрони перестрибують у неї", 16.5, INK, "middle", "bold")
    s += text(W / 2, 56, "електрон стрибає в один бік — дірка пливе в інший", 11.5, GREY, "middle", style="italic")
    xs = [120 + k * 80 for k in range(7)]

    def row(y, holek, lab):
        t = rect(xs[0] - 24, y - 20, xs[-1] - xs[0] + 48, 40, "#f6f7f9", "#d6dde4", 1, 8)
        t += text(xs[0] - 46, y + 5, lab, 11, GREY, "middle", "bold")
        for k, x in enumerate(xs):
            t += ho(x, y) if k == holek else el(x, y)
        return t

    s += row(120, 4, "крок 1")
    s += row(215, 3, "крок 2")
    s += arrow(xs[3] + 14, 120, xs[4] - 14, 120, GREEN, 2)
    s += text((xs[3] + xs[4]) / 2, 106, "стриб", 9, GREEN, "middle", "bold")
    s += arrow(xs[4], 138, xs[3], 197, RED, 1.8, dash="3,3")
    s += text(xs[6] + 14, 120, "→", 14, GREEN, "start", "bold")
    s += text(xs[6] + 14, 215, "←", 14, RED, "start", "bold")
    s += el(560, 270)
    s += text(575, 274, "електрон (−)", 10, INK, "start")
    s += ho(660, 270)
    s += text(640, 274, "дірка (+)", 10, INK, "end")
    save("fig-10-2-1-hole-motion.svg", s)


# ── Рис. 10.2.2 — пара електрон–дірка ────────────────────────────────────────
def fig21_electron_hole_pair():
    W, H = 620, 300
    s = header(W, H)
    s += text(W / 2, 30, "У чистому кремнії носії народжуються парами", 16.5, INK, "middle", "bold")
    a1, a2, ay, r = 220, 400, 185, 24
    bnd, (hx, hy) = _bond2(a1, ay, a2, ay, r, dots=1)
    s += bnd
    # вільний електрон полетів угору
    s += arrow((a1 + a2) / 2, ay - 12, 360, 100, BLUE, 2)
    s += el(360, 96)
    s += text(372, 92, "вільний електрон (−)", 10.5, BLUE, "start", "bold")
    # дірка на місці зниклого електрона
    s += ho(hx, hy)
    s += text(hx, ay + 40, "дірка (+)", 10.5, RED, "middle", "bold")
    # енергія
    s += circle(200, 100, 13, "#fce9c0", SUN, 2)
    s += text(200, 84, "тепло", 10, COPP, "middle", "bold")
    s += line(200, 114, (a1 + a2) / 2 - 6, ay - 10, SUN, 2)
    for x in (a1, a2):
        s += circle(x, ay, r, "#eef2f6", INK, 2)
        s += text(x, ay + 5, "Si", 13, INK, "middle", "bold")
    s += text(W / 2, H - 16, "Один розірваний зв'язок дає рівно один електрон і рівно одну дірку.",
              11, GREY, "middle", style="italic")
    save("fig-10-2-2-electron-hole-pair.svg", s)


# ── Рис. 10.2.3 — n-тип (донор) ──────────────────────────────────────────────
def fig21_n_type():
    W, H = 620, 350
    s = header(W, H)
    s += text(W / 2, 30, "n-тип: донор дає зайвий вільний електрон", 17, INK, "middle", "bold")
    cx, cy, r = 310, 190, 24
    nb = [(310, 100), (310, 280), (190, 190), (430, 190)]
    for (x, y) in nb:
        b, _ = _bond2(cx, cy, x, y, r, dots=2)
        s += b
    # 5-й електрон — вільний, біля донора
    s += circle(372, 150, 16, "none", BLUE, 1.3, )
    s += el(372, 150)
    s += arrow(388, 142, 420, 120, BLUE, 1.8)
    s += text(424, 118, "5-й електрон →", 10.5, BLUE, "start", "bold")
    s += text(424, 132, "вільний (−)", 10, BLUE, "start")
    # атоми
    for (x, y) in nb:
        s += circle(x, y, r, "#eef2f6", INK, 2)
        s += text(x, y + 5, "Si", 12.5, INK, "middle", "bold")
    s += circle(cx, cy, r, "#fde7e6", RED, 2.2)
    s += text(cx, cy + 5, "P", 14, RED, "middle", "bold")
    s += text(cx, H - 32, "Фосфор (P) — 5 валентних електронів: чотири у зв'язках, п'ятий зайвий.",
              11, GREY, "middle", style="italic")
    s += text(cx, H - 16, "Донор: додає вільний електрон без дірки.", 11, GREY, "middle", style="italic")
    save("fig-10-2-3-n-type.svg", s)


# ── Рис. 10.2.4 — p-тип (акцептор) ───────────────────────────────────────────
def fig21_p_type():
    W, H = 620, 350
    s = header(W, H)
    s += text(W / 2, 30, "p-тип: акцептор створює дірку — брак електрона", 17, INK, "middle", "bold")
    cx, cy, r = 310, 190, 24
    full = [(310, 100), (310, 280), (190, 190)]
    for (x, y) in full:
        b, _ = _bond2(cx, cy, x, y, r, dots=2)
        s += b
    # неповний зв'язок праворуч — лише 1 електрон, на місці другого дірка
    bnd, (hx, hy) = _bond2(cx, cy, 430, 190, r, dots=1)
    s += bnd
    s += ho(hx, hy)
    s += arrow(hx + 4, hy - 12, hx + 36, hy - 36, RED, 1.8)
    s += text(hx + 40, hy - 38, "дірка (+)", 10.5, RED, "start", "bold")
    for (x, y) in full + [(430, 190)]:
        s += circle(x, y, r, "#eef2f6", INK, 2)
        s += text(x, y + 5, "Si", 12.5, INK, "middle", "bold")
    s += circle(cx, cy, r, "#e7eefb", BLUE, 2.2)
    s += text(cx, cy + 5, "B", 14, BLUE, "middle", "bold")
    s += text(cx, H - 32, "Бор (B) — 3 валентні електрони: на четвертий зв'язок електрона бракує.",
              11, GREY, "middle", style="italic")
    s += text(cx, H - 16, "Акцептор: створює дірку без вільного електрона.", 11, GREY, "middle", style="italic")
    save("fig-10-2-4-p-type.svg", s)


# ── Рис. 10.2.5 — основні/неосновні носії ────────────────────────────────────
def fig21_majority_minority():
    W, H = 780, 320
    s = header(W, H)
    s += text(W / 2, 28, "n-тип і p-тип: основні носії, нерухомі іони — обидва нейтральні", 15.5, INK, "middle", "bold")
    # ліва панель n
    s += _frame(40, 56, 330, 200, "n-тип")
    cells = [(80 + (i % 4) * 75, 100 + (i // 4) * 50) for i in range(8)]
    for (x, y) in cells:
        s += ion_p(x + 18, y - 14)
        s += el(x, y)
    s += ho(300, 210)
    s += text(60, 240, "основні: електрони (−) · неосновні: дірки · іони (+)", 9.5, GREY, "start")
    # права панель p
    s += _frame(410, 56, 330, 200, "p-тип")
    cells2 = [(450 + (i % 4) * 75, 100 + (i // 4) * 50) for i in range(8)]
    for (x, y) in cells2:
        s += ion_n(x + 18, y - 14)
        s += ho(x, y)
    s += el(670, 210)
    s += text(430, 240, "основні: дірки (+) · неосновні: електрони · іони (−)", 9.5, GREY, "start")
    s += text(W / 2, H - 14, "Рухливі носії врівноважені нерухомими іонами — кожен бік нейтральний як ціле.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-2-5-majority-minority.svg", s)


# ── Рис. 10.2.6 — як мало домішки ────────────────────────────────────────────
def fig21_doping_amount():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Один атом домішки на мільйон — провідність у тисячі разів", 16, INK, "middle", "bold")
    # сітка кремнію з одним домішковим атомом
    cols, rows, x0, y0, st = 22, 8, 70, 90, 14
    for j in range(rows):
        for i in range(cols):
            x, y = x0 + i * st, y0 + j * st
            if i == 11 and j == 3:
                s += circle(x, y, 5, RED, RED)
            else:
                s += circle(x, y, 3, "#c9d3dc", "#c9d3dc")
    s += arrow(x0 + 11 * st, 70, x0 + 11 * st, y0 + 3 * st - 8, RED, 1.6)
    s += text(x0 + 11 * st, 64, "1 чужий атом", 9.5, RED, "middle", "bold")
    s += text(x0 + cols * st / 2, y0 + rows * st + 16, "решта — кремній (тут показано жменю; насправді їх мільйон)",
              9.5, GREY, "middle", style="italic")
    # стовпчики провідності
    bx = 470
    s += line(bx, 230, bx + 200, 230, INK, 1.4)
    s += rect(bx + 20, 222, 36, 8, "#dfe5ea", GREY, 1)
    s += text(bx + 38, 246, "чистий", 9.5, GREY, "middle")
    s += rect(bx + 120, 110, 36, 120, "#e7f3ea", GREEN, 1.4)
    s += text(bx + 138, 246, "легований", 9.5, GREEN, "middle", "bold")
    s += text(bx + 100, 100, "× тисячі", 11, GREEN, "middle", "bold")
    s += text(bx + 100, 80, "провідність", 10, INK, "middle", "bold")
    save("fig-10-2-6-doping-amount.svg", s)


# ── допоміжне для §10.3: смуга n|p ───────────────────────────────────────────
def _np_bar(bx, by, bw, bh):
    mid = bx + bw / 2
    s = rect(bx, by, bw / 2, bh, "#eef3fb", "#9bb0c2", 1.2)
    s += rect(mid, by, bw / 2, bh, "#fbeeee", "#c9a0a0", 1.2)
    return s, mid


# ── Рис. 10.3.1 — зустріч ────────────────────────────────────────────────────
def fig31_meet():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Момент зустрічі: ліворуч електрони (n), праворуч дірки (p)", 16, INK, "middle", "bold")
    bx, by, bw, bh = 100, 120, 520, 95
    bar, mid = _np_bar(bx, by, bw, bh)
    s += bar
    s += line(mid, by - 8, mid, by + bh + 8, INK, 1.4, dash="4,4")
    s += text(bx + 60, by - 12, "n-область", 11, BLUE, "middle", "bold")
    s += text(mid + 200, by - 12, "p-область", 11, RED, "middle", "bold")
    for i in range(10):
        x = bx + 30 + (i % 5) * 46
        y = by + 30 + (i // 5) * 38
        s += ion_p(x + 13, y - 12)
        s += el(x, y)
    for i in range(10):
        x = mid + 30 + (i % 5) * 46
        y = by + 30 + (i // 5) * 38
        s += ion_n(x + 13, y - 12)
        s += ho(x, y)
    s += text(W / 2, by + bh + 30,
              "Перепад концентрацій у мільярди разів. Бліді — нерухомі іони; кожен бік поки нейтральний.",
              10, GREY, "middle", style="italic")
    save("fig-10-3-1-meet.svg", s)


# ── Рис. 10.3.2 — дифузія й рекомбінація ─────────────────────────────────────
def fig31_diffuse_recombine():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Дифузія через межу й рекомбінація біля неї", 16.5, INK, "middle", "bold")
    bx, by, bw, bh = 100, 120, 520, 95
    bar, mid = _np_bar(bx, by, bw, bh)
    s += bar
    s += line(mid, by - 8, mid, by + bh + 8, INK, 1.4, dash="4,4")
    s += text(bx + 55, by - 12, "n", 13, BLUE, "middle", "bold")
    s += text(mid + 205, by - 12, "p", 13, RED, "middle", "bold")
    for k in range(3):
        y = by + 25 + k * 24
        s += el(bx + 70, y)
        s += arrow(bx + 82, y, mid - 22, y, BLUE, 1.6)
        s += ho(bx + bw - 70, y)
        s += arrow(bx + bw - 82, y, mid + 22, y, RED, 1.6)
    for a in range(8):
        ang = a * math.pi / 4
        s += line(mid, by + bh / 2, mid + 13 * math.cos(ang), by + bh / 2 + 13 * math.sin(ang), "#9c6a16", 1.4)
    s += text(W / 2, by + bh + 28, "Біля межі електрон і дірка зустрічаються й рекомбінують — обидва зникають.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-3-2-diffuse-recombine.svg", s)


def _depletion_base(W, H, title):
    s = header(W, H)
    s += text(W / 2, 30, title, 16, INK, "middle", "bold")
    bx, by, bw, bh = 100, 120, 520, 95
    bar, mid = _np_bar(bx, by, bw, bh)
    s += bar
    dep = 46
    s += rect(mid - dep, by, 2 * dep, bh, "#f3f0e6", "#9c6a16", 1.4)
    s += line(mid, by, mid, by + bh, INK, 1, dash="3,3")
    # далекі носії поза збідненою зоною
    for k in range(4):
        s += el(bx + 40 + (k % 2) * 30, by + 30 + (k // 2) * 36)
        s += el(bx + 110 + (k % 2) * 30, by + 30 + (k // 2) * 36)
        s += ho(bx + bw - 40 - (k % 2) * 30, by + 30 + (k // 2) * 36)
        s += ho(bx + bw - 110 - (k % 2) * 30, by + 30 + (k // 2) * 36)
    # оголені іони в збідненій зоні
    for k in range(3):
        s += ion_p(mid - dep + 14, by + 22 + k * 26)
        s += ion_p(mid - dep + 32, by + 22 + k * 26)
        s += ion_n(mid + dep - 14, by + 22 + k * 26)
        s += ion_n(mid + dep - 32, by + 22 + k * 26)
    return s, bx, by, bw, bh, mid, dep


# ── Рис. 10.3.3 — збіднена область ───────────────────────────────────────────
def fig31_depletion_region():
    s, bx, by, bw, bh, mid, dep = _depletion_base(720, 310, "Збіднена область: лишилися самі нерухомі іони")
    s += text(mid, by - 12, "збіднена область", 10.5, "#9c6a16", "middle", "bold")
    s += text(bx + 60, by + bh + 22, "ще є електрони", 9.5, BLUE, "middle")
    s += text(bx + bw - 60, by + bh + 22, "ще є дірки", 9.5, RED, "middle")
    s += text(720 / 2, by + bh + 42, "У зоні рухливих носіїв немає — лише оголені іони (+ з n-боку, − з p-боку).",
              10, GREY, "middle", style="italic")
    save("fig-10-3-3-depletion-region.svg", s)


# ── Рис. 10.3.4 — вбудоване поле ─────────────────────────────────────────────
def fig31_builtin_field():
    s, bx, by, bw, bh, mid, dep = _depletion_base(720, 320, "Вбудоване поле протидіє дифузії")
    for k in range(2):
        y = by + 30 + k * 38
        s += arrow(mid - dep + 6, y, mid + dep - 6, y, GREEN, 2.2)
    s += text(mid, by - 12, "вбудоване поле  E →", 10.5, GREEN, "middle", "bold")
    # поле жене носії назад
    s += el(mid - dep - 46, by + bh + 26)
    s += arrow(mid - dep - 34, by + bh + 26, mid - dep - 66, by + bh + 26, BLUE, 1.8)
    s += text(mid - dep - 80, by + bh + 30, "назад у n", 9.5, BLUE, "end")
    s += ho(mid + dep + 46, by + bh + 26)
    s += arrow(mid + dep + 34, by + bh + 26, mid + dep + 66, by + bh + 26, RED, 1.8)
    s += text(mid + dep + 80, by + bh + 30, "назад у p", 9.5, RED, "start")
    s += text(720 / 2, by + bh + 52, "Поле з n у p штовхає електрони назад у n, дірки — назад у p.",
              10, GREY, "middle", style="italic")
    save("fig-10-3-4-builtin-field.svg", s)


# ── Рис. 10.3.5 — потенціальний бар'єр ───────────────────────────────────────
def fig31_barrier():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 30, "Потенціальний бар'єр: пагорб через перехід", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 250, 500, 180
    s += _axes(ox, oy, w, h, "положення", "енергія електрона")
    pts = []
    for i in range(101):
        t = i / 100
        val = 0.1 + 0.8 * (1 / (1 + math.exp(-13 * (t - 0.5))))
        pts.append((ox + w * t, oy - h * val))
    s += _poly(pts, RED, 2.8)
    yL, yH = oy - h * 0.1, oy - h * 0.9
    s += line(ox + w + 4, yL, ox + w + 4, yH, INK, 1.2)
    s += text(ox + w + 10, (yL + yH) / 2, "≈0.7 В", 10, RED, "start", "bold")
    s += text(ox + w * 0.18, oy - h * 0.1 + 16, "n (низько)", 10, BLUE, "middle", "bold")
    s += text(ox + w * 0.82, oy - h * 0.9 - 8, "p (високо)", 10, RED, "middle", "bold")
    s += text(ox + w * 0.5, oy + 16, "збіднена область", 9.5, "#9c6a16", "middle", "bold")
    s += el(ox + w * 0.26, oy - h * 0.13)
    s += arrow(ox + w * 0.29, oy - h * 0.16, ox + w * 0.42, oy - h * 0.34, GREY, 1.6, dash="3,3")
    s += text(ox + w * 0.30, oy - h * 0.52, "снаги бракує", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Носій мусить «вибратися» на пагорб ≈0.7 В — і здебільшого не може.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-3-5-barrier.svg", s)


# ── Рис. 10.3.6 — рівновага ──────────────────────────────────────────────────
def fig31_equilibrium():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 30, "Рівновага: дифузія врівноважена вбудованим полем", 16, INK, "middle", "bold")
    cx, cy = W / 2, 150
    s += line(160, cy, 540, cy, INK, 2)
    s += circle(cx, cy, 11, "#f3f0e6", "#9c6a16", 2)
    s += arrow(cx - 120, cy, cx - 26, cy, GREEN, 3)
    s += text(245, cy - 18, "дифузія", 12, GREEN, "middle", "bold")
    s += text(245, cy + 26, "носії розпливаються", 9.5, GREY, "middle")
    s += arrow(cx + 120, cy, cx + 26, cy, BLUE, 3)
    s += text(W - 245, cy - 18, "вбудоване поле", 12, BLUE, "middle", "bold")
    s += text(W - 245, cy + 26, "жене назад", 9.5, GREY, "middle")
    s += text(cx, cy + 78, "баланс → сумарного струму немає", 12.5, INK, "middle", "bold")
    s += text(cx, cy + 100, "рівновага динамічна: носії ще зрідка перескакують в обидва боки",
              9.5, GREY, "middle", style="italic")
    save("fig-10-3-6-equilibrium.svg", s)


# ── допоміжне для §10.4: батарея ─────────────────────────────────────────────
def _battery(cx, cy, plus_right=True):
    if plus_right:
        s = line(cx - 7, cy - 11, cx - 7, cy + 11, INK, 2)
        s += line(cx + 7, cy - 20, cx + 7, cy + 20, INK, 3)
        s += text(cx - 17, cy + 5, "−", 14, BLUE, "middle", "bold")
        s += text(cx + 19, cy + 5, "+", 14, RED, "middle", "bold")
    else:
        s = line(cx - 7, cy - 20, cx - 7, cy + 20, INK, 3)
        s += line(cx + 7, cy - 11, cx + 7, cy + 11, INK, 2)
        s += text(cx - 19, cy + 5, "+", 14, RED, "middle", "bold")
        s += text(cx + 17, cy + 5, "−", 14, BLUE, "middle", "bold")
    return s


def _bias_bar(s, bx, by, bw, bh, dep):
    mid = bx + bw / 2
    s += rect(bx, by, bw / 2, bh, "#eef3fb", "#9bb0c2", 1.2)
    s += rect(mid, by, bw / 2, bh, "#fbeeee", "#c9a0a0", 1.2)
    s += rect(mid - dep, by, 2 * dep, bh, "#f3f0e6", "#9c6a16", 1.2)
    s += text(bx + 50, by - 10, "n", 13, BLUE, "middle", "bold")
    s += text(bx + bw - 50, by - 10, "p", 13, RED, "middle", "bold")
    return s, mid


# ── Рис. 10.4.1 — пряме зміщення ─────────────────────────────────────────────
def fig41_forward_bias():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Пряме зміщення: бар'єр падає, тече струм", 16.5, INK, "middle", "bold")
    bx, by, bw, bh = 140, 80, 440, 76
    s, mid = _bias_bar(s, bx, by, bw, bh, 14)
    cyw = by + bh / 2
    s += text(mid, by + bh + 16, "вузька збіднена зона", 9, "#9c6a16", "middle")
    for k in range(3):
        s += el(mid - 42 - k * 26, by + 25 + (k % 2) * 30)
        s += ho(mid + 42 + k * 26, by + 25 + (k % 2) * 30)
    # дроти й батарея: − до n (зліва), + до p (справа)
    s += line(bx, cyw, bx - 40, cyw, INK, 2) + line(bx - 40, cyw, bx - 40, 250, INK, 2)
    s += line(bx + bw, cyw, bx + bw + 40, cyw, INK, 2) + line(bx + bw + 40, cyw, bx + bw + 40, 250, INK, 2)
    s += line(bx - 40, 250, 300, 250, INK, 2)
    s += _battery(330, 250, True)
    s += line(360, 250, bx + bw + 40, 250, INK, 2)
    s += arrow(bx + bw + 40, 215, bx + bw + 40, cyw + 8, GREEN, 2.4)
    s += arrow(bx - 40, cyw + 8, bx - 40, 215, GREEN, 2.4)
    s += arrow(430, 250, 480, 250, GREEN, 2.4)
    s += text(W / 2, 300, "великий струм тече", 12.5, GREEN, "middle", "bold")
    save("fig-10-4-1-forward-bias.svg", s)


# ── Рис. 10.4.2 — зворотне зміщення ──────────────────────────────────────────
def fig41_reverse_bias():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Зворотне зміщення: бар'єр росте, струму немає", 16.5, INK, "middle", "bold")
    bx, by, bw, bh = 140, 80, 440, 76
    s, mid = _bias_bar(s, bx, by, bw, bh, 42)
    cyw = by + bh / 2
    s += text(mid, by + bh + 16, "широка збіднена зона", 9, "#9c6a16", "middle")
    for k in range(3):
        s += el(bx + 30 + (k % 2) * 24, by + 25 + (k // 2) * 30)
        s += ho(bx + bw - 30 - (k % 2) * 24, by + 25 + (k // 2) * 30)
    # дроти й батарея: + до n (зліва), − до p (справа)
    s += line(bx, cyw, bx - 40, cyw, INK, 2) + line(bx - 40, cyw, bx - 40, 250, INK, 2)
    s += line(bx + bw, cyw, bx + bw + 40, cyw, INK, 2) + line(bx + bw + 40, cyw, bx + bw + 40, 250, INK, 2)
    s += line(bx - 40, 250, 300, 250, INK, 2)
    s += _battery(330, 250, False)
    s += line(360, 250, bx + bw + 40, 250, INK, 2)
    # перекреслення — струму нема
    s += line(350, 235, 370, 265, RED, 3) + line(370, 235, 350, 265, RED, 3)
    s += text(W / 2, 300, "струму немає (лише мізерний витік)", 12, RED, "middle", "bold")
    save("fig-10-4-2-reverse-bias.svg", s)


# ── Рис. 10.4.3 — зсув бар'єра ───────────────────────────────────────────────
def fig41_barrier_shift():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Зовнішня напруга піднімає або знижує бар'єр", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 110, 270, 520, 190
    s += _axes(ox, oy, w, h, "положення (n → p)", "енергія")

    def hill(height, col):
        pts = [(ox + w * (i / 100),
                oy - h * (0.06 + (height - 0.06) * (1 / (1 + math.exp(-13 * ((i / 100) - 0.5))))))
               for i in range(101)]
        return _poly(pts, col, 2.6)

    s += hill(0.55, GREY)
    s += hill(0.2, GREEN)
    s += hill(0.92, RED)
    s += text(ox + w * 0.72, oy - h * 0.92 - 6, "зворотне (вищий)", 10, RED, "start", "bold")
    s += text(ox + w * 0.72, oy - h * 0.55 - 6, "спокій ≈0.7 В", 10, GREY, "start", "bold")
    s += text(ox + w * 0.72, oy - h * 0.2 - 6, "пряме (нижчий)", 10, GREEN, "start", "bold")
    s += text(ox + w * 0.12, oy - h * 0.06 + 16, "n", 11, BLUE, "middle", "bold")
    s += text(W / 2, H - 12, "Пряме знижує пагорб (струм тече), зворотне — підвищує (замкнено).",
              10.5, GREY, "middle", style="italic")
    save("fig-10-4-3-barrier-shift.svg", s)


# ── Рис. 10.4.4 — аналогія клапана ───────────────────────────────────────────
def fig41_valve_analogy():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Діод — як зворотний клапан у трубі", 16.5, INK, "middle", "bold")
    s += _frame(40, 60, 330, 200, "Пряме: клапан відкритий")
    s += rect(70, 140, 270, 40, "#eef3fb", "#9bb0c2", 1.2)
    s += line(150, 180, 176, 120, INK, 3)
    s += circle(150, 180, 3.5, INK, INK)
    for yy in (152, 168):
        s += arrow(80, yy, 332, yy, GREEN, 2.2)
    s += text(210, 205, "потік проходить", 10.5, GREEN, "middle", "bold")
    s += _frame(390, 60, 330, 200, "Зворотне: клапан закритий")
    s += rect(420, 140, 270, 40, "#fbeeee", "#c9a0a0", 1.2)
    s += line(500, 142, 500, 178, INK, 3)
    s += circle(500, 142, 3.5, INK, INK)
    s += arrow(685, 160, 522, 160, RED, 2.2)
    s += line(508, 146, 524, 162, RED, 2.5) + line(524, 146, 508, 162, RED, 2.5)
    s += text(560, 205, "потік заблоковано", 10.5, RED, "middle", "bold")
    save("fig-10-4-4-valve-analogy.svg", s)


# ── Рис. 10.4.5 — анод, катод, символ ────────────────────────────────────────
def fig41_anode_cathode():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Анод, катод і символ діода", 16.5, INK, "middle", "bold")
    cx, cy = 360, 105
    s += line(180, cy, cx - 16, cy, INK, 2.5)
    s += f'<path d="M {cx-16},{cy-22} L {cx-16},{cy+22} L {cx+12},{cy} Z" fill="#dfe7f0" stroke="{INK}" stroke-width="2"/>\n'
    s += line(cx + 12, cy - 22, cx + 12, cy + 22, INK, 3)
    s += line(cx + 12, cy, 540, cy, INK, 2.5)
    s += text(230, cy - 18, "анод (p)", 11, RED, "middle", "bold")
    s += text(495, cy - 18, "катод (n)", 11, BLUE, "middle", "bold")
    s += arrow(305, cy + 40, 415, cy + 40, GREEN, 2.2)
    s += text(360, cy + 58, "дозволений напрямок струму", 10, GREEN, "middle", "bold")
    s += rect(256, 185, 104, 32, "#fbeeee", "#c9a0a0", 1.2)
    s += text(308, 206, "p", 13, RED, "middle", "bold")
    s += rect(360, 185, 104, 32, "#eef3fb", "#9bb0c2", 1.2)
    s += text(412, 206, "n", 13, BLUE, "middle", "bold")
    s += text(360, 234, "той самий перехід: анод = p, катод = n", 9.5, GREY, "middle")
    s += rect(256, 252, 208, 26, "#3a3a3a", "#222222", 1, 4)
    s += rect(440, 252, 16, 26, "#cfcfcf", "#cfcfcf", 1, 0)
    s += text(350, 269, "реальний діод", 9.5, "#ffffff", "middle", "bold")
    s += text(448, 294, "смужка = катод", 8.5, GREY, "middle")
    save("fig-10-4-5-anode-cathode.svg", s)


# ── Рис. 10.5.1 — повна ВАХ ──────────────────────────────────────────────────
def fig51_iv_curve():
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 30, "Вольт-амперна характеристика діода", 17, INK, "middle", "bold")
    ox0, oy0 = 430, 235
    s += arrow(120, oy0, 645, oy0, INK, 2)
    s += text(652, oy0 + 4, "U", 13, INK, "start", "bold")
    s += arrow(ox0, 360, ox0, 70, INK, 2)
    s += text(ox0 - 8, 62, "I", 13, INK, "middle", "bold")
    s += text(ox0 + 8, oy0 + 16, "0", 10, GREY, "start")
    fpts = []
    V = 0.0
    while V <= 0.8001:
        f = min(1.0, math.exp((V - 0.72) / 0.045))
        fpts.append((ox0 + V * 250, oy0 - 160 * f))
        V += 0.02
    s += _poly(fpts, RED, 2.8)
    s += _poly([(ox0, oy0 + 3), (172, oy0 + 7), (152, oy0 + 22), (150, 360)], BLUE, 2.6)
    s += line(ox0 + 0.7 * 250, oy0 - 4, ox0 + 0.7 * 250, oy0 + 4, INK, 1.4)
    s += text(ox0 + 0.7 * 250 + 6, oy0 + 18, "≈0.7 В", 10, RED, "start", "bold")
    s += text(ox0 + 0.45 * 250, 96, "пряма гілка", 10.5, RED, "middle", "bold")
    s += text(245, oy0 - 12, "зворотна (≈0)", 10, BLUE, "middle", "bold")
    s += text(150, 375, "пробій", 9.5, BLUE, "middle", "bold")
    s += text(W / 2, H - 12, "Праворуч — пряма гілка (коліно ≈0.7 В), ліворуч — зворотна (≈0) і пробій. Схематично, не в масштабі.",
              10, GREY, "middle", style="italic")
    save("fig-10-5-1-iv-curve.svg", s)


# ── Рис. 10.5.2 — пряме коліно ───────────────────────────────────────────────
def fig51_forward_knee():
    W, H = 680, 340
    s = header(W, H)
    s += text(W / 2, 30, "Пряма гілка: коліно ≈0.7 В", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 110, 280, 500, 210
    s += _axes(ox, oy, w, h, "напруга U", "струм I")
    fpts = []
    V = 0.0
    while V <= 0.8001:
        f = min(1.0, math.exp((V - 0.72) / 0.045))
        fpts.append((ox + (V / 0.8) * w, oy - h * 0.95 * f))
        V += 0.01
    s += _poly(fpts, RED, 2.8)
    s += line(ox + (0.7 / 0.8) * w, oy, ox + (0.7 / 0.8) * w, oy - h * 0.62, GREY, 1, dash="4,4")
    s += text(ox + (0.7 / 0.8) * w, oy + 16, "≈0.7 В", 10.5, RED, "middle", "bold")
    s += text(ox + 0.22 * w, oy - 12, "майже 0", 9.5, GREY, "middle")
    s += text(ox + 0.9 * w, oy - h * 0.78, "стрімко", 10, RED, "middle", "bold")
    s += text(W / 2, H - 12, "До коліна струм майже непомітний; за ним зростає вибухово (експонента).",
              10, GREY, "middle", style="italic")
    save("fig-10-5-2-forward-knee.svg", s)


# ── Рис. 10.5.3 — різні матеріали ────────────────────────────────────────────
def fig51_materials():
    W, H = 680, 340
    s = header(W, H)
    s += text(W / 2, 30, "Різні діоди — різне коліно", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 280, 520, 210
    s += _axes(ox, oy, w, h, "напруга U", "струм I")
    Vmax = 2.6

    def curve(Vk, col, lab, lx):
        pts = []
        V = 0.0
        while V <= Vmax + 1e-6:
            f = min(1.0, math.exp((V - Vk) / 0.06))
            pts.append((ox + (V / Vmax) * w, oy - h * 0.92 * f))
            V += 0.02
        return _poly(pts, col, 2.6) + text(ox + (lx / Vmax) * w, oy - h * 0.85, lab, 9.5, col, "middle", "bold")

    s += curve(0.3, GREEN, "Ge ~0.3", 0.5)
    s += curve(0.7, RED, "Si ~0.7", 1.0)
    s += curve(2.0, BLUE, "LED ~2", 2.25)
    s += text(W / 2, H - 12, "Що ширша щілина — то правіше коліно: германій, кремній, світлодіод.",
              10, GREY, "middle", style="italic")
    save("fig-10-5-3-materials.svg", s)


# ── Рис. 10.5.4 — зворотний пробій ───────────────────────────────────────────
def fig51_breakdown():
    W, H = 680, 340
    s = header(W, H)
    s += text(W / 2, 30, "Зворотний пробій", 16.5, INK, "middle", "bold")
    ox0, oy0 = 560, 95
    s += arrow(600, oy0, 150, oy0, INK, 2)
    s += text(142, oy0 + 4, "−U", 12, INK, "end", "bold")
    s += arrow(ox0, oy0 - 8, ox0, 305, INK, 2)
    s += text(ox0 + 6, 314, "−I", 12, INK, "start", "bold")
    s += text(ox0 - 8, oy0 - 6, "0", 10, GREY, "end")
    s += _poly([(ox0, oy0 + 4), (262, oy0 + 9), (232, oy0 + 28), (226, 292)], RED, 2.8)
    s += line(226, oy0 - 4, 226, oy0 + 4, INK, 1.4)
    s += text(226, oy0 - 10, "V_BR", 10, RED, "middle", "bold")
    s += text(410, oy0 + 22, "мізерний витік", 9.5, GREY, "middle")
    s += text(150, 210, "струм лавиною", 10, RED, "middle", "bold")
    s += text(W / 2, H - 12, "До V_BR — лише витік; на V_BR струм раптово зростає (лавина чи тунелювання).",
              10, GREY, "middle", style="italic")
    save("fig-10-5-4-breakdown.svg", s)


# ── Рис. 10.5.5 — три моделі ─────────────────────────────────────────────────
def fig51_models():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Три моделі діода", 16.5, INK, "middle", "bold")

    def mini(px, py, title, kind, col):
        ow, oh = 180, 130
        oy = py + oh
        ox = px
        t = _axes(ox, oy, ow, oh, "U", "I")
        if kind == "ideal":
            t += _poly([(ox, oy), (ox, oy - oh * 0.92)], col, 2.8)
        elif kind == "drop":
            xk = ox + ow * 0.45
            t += _poly([(ox, oy), (xk, oy), (xk, oy - oh * 0.92)], col, 2.8)
            t += text(xk, oy + 14, "0.7 В", 9, col, "middle", "bold")
        else:
            pts = []
            V = 0.0
            while V <= 1.0001:
                f = min(1.0, math.exp((V - 0.72) / 0.05))
                pts.append((ox + ow * V * 0.9, oy - oh * 0.92 * f))
                V += 0.02
            t += _poly(pts, col, 2.8)
        t += text(ox + ow / 2, py - 6, title, 12, col, "middle", "bold")
        return t

    s += mini(50, 72, "Ідеальний", "ideal", GREEN)
    s += mini(270, 72, "Падіння 0.7 В", "drop", RED)
    s += mini(490, 72, "Реальна крива", "real", BLUE)
    s += text(W / 2, H - 14, "Від найгрубішої (ідеальний клапан) до точної (експонента) — бери просту, якої досить.",
              10, GREY, "middle", style="italic")
    save("fig-10-5-5-models.svg", s)


# ── Рис. 10.5.6 — розрахунок кола ────────────────────────────────────────────
def fig51_worked():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 30, "Розрахунок: діод 0.7 В і резистор задають струм", 15.5, INK, "middle", "bold")
    s += line(120, 110, 540, 110, INK, 2)
    s += line(540, 110, 540, 210, INK, 2)
    s += line(540, 210, 120, 210, INK, 2)
    s += line(120, 110, 120, 210, INK, 2)
    # батарея на лівій стійці, + зверху
    s += line(106, 150, 134, 150, INK, 3)
    s += line(113, 163, 127, 163, INK, 2)
    s += text(96, 146, "+", 12, RED, "middle", "bold")
    s += text(96, 172, "−", 12, BLUE, "middle", "bold")
    s += text(150, 185, "5 В", 11, INK, "start", "bold")
    # резистор зверху
    s += rect(248, 98, 96, 24, "#ffffff", INK, 1.6)
    s += text(296, 114, "R = 430 Ω", 10, INK, "middle", "bold")
    s += text(296, 88, "U_R = 4.3 В", 9.5, INK, "middle")
    # діод зверху-праворуч (вістря праворуч = струм за годинниковою)
    s += f'<path d="M 430,98 L 430,122 L 453,110 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.6"/>\n'
    s += line(453, 98, 453, 122, INK, 2.5)
    s += text(441, 140, "0.7 В", 9.5, RED, "middle", "bold")
    # струм
    s += arrow(165, 110, 205, 110, GREEN, 2)
    s += text(330, 165, "I = 10 мА", 11, GREEN, "middle", "bold")
    s += text(W / 2, 250, "U_R = 5 − 0.7 = 4.3 В   →   I = 4.3 / 430 = 10 мА", 11.5, INK, "middle", "bold")
    save("fig-10-5-6-worked.svg", s)


# ── допоміжне для §10.6 ──────────────────────────────────────────────────────
def _fullwave(ox, oy, w, amp, humps, col, wv=2.6):
    pts = [(ox + j, oy - amp * abs(math.sin(math.pi * humps * (j / w)))) for j in range(int(w) + 1)]
    return _poly(pts, col, wv)


def _ripple(ox, oy, w, amp, humps, col, wv=2.8):
    pts = []
    for j in range(int(w) + 1):
        ph = (j * humps / w) % 1.0
        v = 0.88 - 0.12 * ph
        pts.append((ox + j, oy - amp * v))
    return _poly(pts, col, wv)


def _diode_h(cx, cy, size=12, right=True, col=INK):
    if right:
        t = f'<path d="M {cx-size},{cy-size} L {cx-size},{cy+size} L {cx+size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
        t += line(cx + size * 0.8, cy - size, cx + size * 0.8, cy + size, col, 2.5)
    else:
        t = f'<path d="M {cx+size},{cy-size} L {cx+size},{cy+size} L {cx-size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
        t += line(cx - size * 0.8, cy - size, cx - size * 0.8, cy + size, col, 2.5)
    return t


def _diode_seg(ax, ay, bx, by, size=11, col=INK):
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    mx, my = (ax + bx) / 2, (ay + by) / 2
    b1 = (mx - ux * size + px * size, my - uy * size + py * size)
    b2 = (mx - ux * size - px * size, my - uy * size - py * size)
    tip = (mx + ux * size, my + uy * size)
    t = f'<path d="M {b1[0]:.1f},{b1[1]:.1f} L {b2[0]:.1f},{b2[1]:.1f} L {tip[0]:.1f},{tip[1]:.1f} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.4"/>\n'
    t += line(tip[0] + px * size, tip[1] + py * size, tip[0] - px * size, tip[1] - py * size, col, 2.4)
    return t


# ── Рис. 10.6.1 — AC проти DC ────────────────────────────────────────────────
def fig61_ac_vs_dc():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Змінний (AC) гойдається, постійний (DC) тече стало", 16, INK, "middle", "bold")
    s += _frame(40, 60, 320, 200, "змінний струм (AC)")
    s += line(70, 160, 330, 160, GREY, 1)
    s += _sine(70, 160, 260, 55, 2.5, BLUE, 2.6)
    s += text(200, 250, "міняє знак 100 разів/с", 9.5, GREY, "middle", style="italic")
    s += _frame(400, 60, 320, 200, "постійний струм (DC)")
    s += line(430, 160, 690, 160, GREY, 1)
    s += line(430, 120, 690, 120, RED, 2.8)
    s += text(560, 250, "стала, один напрямок", 9.5, GREY, "middle", style="italic")
    save("fig-10-6-1-ac-vs-dc.svg", s)


# ── Рис. 10.6.2 — однопівперіодний випрямляч ─────────────────────────────────
def fig61_halfwave():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Однопівперіодний випрямляч: один діод", 16, INK, "middle", "bold")
    # коло
    s += circle(95, 165, 22, "#ffffff", INK, 2)
    s += text(95, 171, "~", 18, INK, "middle", "bold")
    s += line(95, 143, 95, 95, INK, 2) + line(95, 95, 250, 95, INK, 2)
    s += _diode_h(165, 95, 12, True)
    s += line(250, 95, 250, 235, INK, 2)
    s += rect(238, 130, 24, 56, "#ffffff", INK, 1.6)
    s += text(268, 162, "R", 12, INK, "start", "bold")
    s += line(250, 235, 95, 235, INK, 2) + line(95, 235, 95, 187, INK, 2)
    # хвилі
    ox = 360
    s += text(ox + 150, 84, "вхід (AC)", 10, INK, "middle", "bold")
    s += line(ox, 115, ox + 300, 115, GREY, 1)
    s += _sine(ox, 115, 300, 32, 3, BLUE, 2.4)
    s += text(ox + 150, 212, "вихід (пульсуючий DC)", 10, INK, "middle", "bold")
    s += line(ox, 255, ox + 300, 255, GREY, 1)
    s += _halfwave(ox, 255, 300, 48, 3, RED, 2.6)
    save("fig-10-6-2-halfwave.svg", s)


# ── Рис. 10.6.3 — мостовий випрямляч ─────────────────────────────────────────
def fig61_bridge():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Мостовий випрямляч: чотири діоди, обидві півхвилі", 16, INK, "middle", "bold")
    L, T, R, Bo = (250, 160), (350, 90), (450, 160), (350, 230)
    for a, b in [(L, T), (R, T), (Bo, L), (Bo, R)]:
        s += line(a[0], a[1], b[0], b[1], INK, 2)
    for a, b in [(L, T), (R, T), (Bo, L), (Bo, R)]:
        s += _diode_seg(a[0], a[1], b[0], b[1], 11)
    # AC вузли (L, R) — петля джерела знизу
    s += line(L[0], L[1], 200, 160, INK, 2) + line(200, 160, 200, 300, INK, 2)
    s += line(200, 300, 330, 300, INK, 2)
    s += circle(350, 300, 18, "#ffffff", INK, 2) + text(350, 306, "~", 16, INK, "middle", "bold")
    s += line(370, 300, 500, 300, INK, 2) + line(500, 300, 500, 160, INK, 2) + line(500, 160, R[0], R[1], INK, 2)
    s += text(350, 318, "трансформатор (AC)", 9, GREY, "middle")
    # DC вузли (T=+, Bo=−) — навантаження праворуч
    s += line(T[0], T[1], T[0], 60, INK, 2) + line(T[0], 60, 600, 60, INK, 2)
    s += rect(588, 120, 24, 60, "#ffffff", INK, 1.6) + text(620, 154, "R", 12, INK, "start", "bold")
    s += line(600, 180, 600, 255, INK, 2) + line(600, 255, Bo[0], 255, INK, 2) + line(Bo[0], 255, Bo[0], Bo[1], INK, 2)
    s += text(T[0] - 12, 70, "+", 14, RED, "end", "bold")
    s += text(Bo[0] - 12, 252, "−", 14, BLUE, "end", "bold")
    s += text(W / 2, H - 10, "За кожної півхвилі відкривається своя пара діодів — а струм у навантаженні щоразу в той самий бік.",
              9.5, GREY, "middle", style="italic")
    save("fig-10-6-3-bridge.svg", s)


# ── Рис. 10.6.4 — повне проти половинного ────────────────────────────────────
def fig61_fullwave_output():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Половинне проти повного випрямлення", 16, INK, "middle", "bold")
    ox = 110
    w = 480
    s += text(ox + w / 2, 80, "однопівперіодний — горби з провалами", 10, RED, "middle", "bold")
    s += line(ox, 130, ox + w, 130, GREY, 1)
    s += _halfwave(ox, 130, w, 46, 4, RED, 2.6)
    s += text(ox + w / 2, 210, "повний (міст) — горби суцільно, удвічі частіше", 10, GREEN, "middle", "bold")
    s += line(ox, 270, ox + w, 270, GREY, 1)
    s += _fullwave(ox, 270, w, 46, 8, GREEN, 2.6)
    s += text(W / 2, H - 12, "Повне випрямлення «перевертає» від'ємні півхвилі вгору — згладити такий вихід набагато легше.",
              10, GREY, "middle", style="italic")
    save("fig-10-6-4-fullwave-output.svg", s)


# ── Рис. 10.6.5 — згладжування ───────────────────────────────────────────────
def fig61_smoothing():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Згладжувальний конденсатор заповнює провали", 16, INK, "middle", "bold")
    ox, oy, w = 110, 250, 480
    s += _axes(ox, oy, w, 200, "час", "напруга")
    # горби (бліді) і згладжена лінія (жирна)
    s += _fullwave(ox, oy, w, 150, 8, "#cdb4b1", 2.0)
    s += _ripple(ox, oy, w, 150, 8, RED, 2.8)
    s += text(ox + w * 0.5, oy - 175, "майже рівна напруга (мала брижа)", 10, RED, "middle", "bold")
    s += text(ox + w * 0.5, oy - 40, "горби випрямляча (без конденсатора)", 9, "#9c6a16", "middle")
    # конденсатор-символ збоку
    s += line(ox + w + 20, oy - 40, ox + w + 20, oy - 150, INK, 2)
    s += text(ox + w + 30, oy - 95, "C", 12, INK, "start", "bold")
    s += text(W / 2, H - 12, "Конденсатор заряджається на піках і живить навантаження в западинах — пульсація майже зникає.",
              10, GREY, "middle", style="italic")
    save("fig-10-6-5-smoothing.svg", s)


# ── допоміжне для §10.7 (світло) ─────────────────────────────────────────────
def _photon(x1, y1, x2, y2, col, amp=4.0, n=3):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    pts = []
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        bx2, by2 = x1 + dx * t, y1 + dy * t
        off = amp * math.sin(2 * math.pi * n * t)
        pts.append((bx2 + px * off, by2 + py * off))
    s = _poly(pts, col, 2.0)
    s += f'<path d="M {x2:.1f},{y2:.1f} L {x2-ux*9-px*4:.1f},{y2-uy*9-py*4:.1f} L {x2-ux*9+px*4:.1f},{y2-uy*9+py*4:.1f} Z" fill="{col}"/>\n'
    return s


def _sun(cx, cy, r=14, col=SUN):
    s = circle(cx, cy, r, "#fce9c0", col, 2)
    for k in range(8):
        a = k * math.pi / 4
        s += line(cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3),
                  cx + math.cos(a) * (r + 9), cy + math.sin(a) * (r + 9), col, 2)
    return s


# ── Рис. 10.7.1 — рекомбінація → фотон ───────────────────────────────────────
def fig71_led_recombination():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Світлодіод: рекомбінація народжує фотон", 16.5, INK, "middle", "bold")
    bx, by, bw, bh = 120, 150, 400, 80
    mid = bx + bw / 2
    s += rect(bx, by, bw / 2, bh, "#eef3fb", "#9bb0c2", 1.2)
    s += rect(mid, by, bw / 2, bh, "#fbeeee", "#c9a0a0", 1.2)
    s += line(mid, by, mid, by + bh, INK, 1, dash="3,3")
    s += text(bx + 50, by - 10, "n", 13, BLUE, "middle", "bold")
    s += text(bx + bw - 50, by - 10, "p", 13, RED, "middle", "bold")
    s += el(mid - 70, by + bh / 2)
    s += arrow(mid - 58, by + bh / 2, mid - 16, by + bh / 2, BLUE, 1.8)
    s += ho(mid + 70, by + bh / 2)
    s += arrow(mid + 58, by + bh / 2, mid + 16, by + bh / 2, RED, 1.8)
    s += text(mid, by + bh + 20, "рекомбінація", 9.5, "#9c6a16", "middle", "bold")
    s += _photon(mid, by + bh / 2 - 8, mid + 95, by - 64, SUN)
    s += text(mid + 104, by - 62, "фотон (світло)", 10.5, COPP, "start", "bold")
    s += text(W / 2, H - 14, "Прямо зміщений перехід: електрон і дірка рекомбінують, віддаючи енергію світлом.",
              10, GREY, "middle", style="italic")
    save("fig-10-7-1-led-recombination.svg", s)


# ── Рис. 10.7.2 — колір і щілина ─────────────────────────────────────────────
def fig71_color_bandgap():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 28, "Колір світлодіода задає ширина щілини", 16.5, INK, "middle", "bold")

    def panel(px, gap, col, lab):
        bw, vy, bh = 170, 250, 24
        cy = vy - gap - bh
        t = rect(px, vy, bw, bh, "#eef2f6", "#9bb0c2", 1.2)
        t += rect(px, cy, bw, bh, "#eef2f6", "#9bb0c2", 1.2)
        t += text(px + bw / 2, vy + bh + 15, "валентна", 8, GREY, "middle")
        t += text(px + bw / 2, cy - 6, "провідність", 8, GREY, "middle")
        t += circle(px + 34, cy + bh / 2, 4, GREEN, GREEN)
        t += arrow(px + 34, cy + bh + 2, px + 34, vy - 2, GREY, 1.4)
        t += _photon(px + 50, (cy + bh + vy) / 2, px + 152, (cy + bh + vy) / 2 - 42, col, 3.0, 2)
        t += text(px + bw / 2, 76, lab, 11, col, "middle", "bold")
        return t

    s += panel(40, 30, RED, "червоний (вузька)")
    s += panel(300, 52, GREEN, "зелений")
    s += panel(560, 80, BLUE, "синій (широка)")
    s += text(W / 2, H - 12, "Ширша щілина — енергійніший фотон — синіше світло (і вище пряме падіння).",
              10, GREY, "middle", style="italic")
    save("fig-10-7-2-color-bandgap.svg", s)


# ── Рис. 10.7.3 — світлодіод у схемі ─────────────────────────────────────────
def fig71_led_circuit():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Світлодіод із резистором-обмежувачем", 16, INK, "middle", "bold")
    s += line(120, 110, 540, 110, INK, 2) + line(540, 110, 540, 210, INK, 2)
    s += line(540, 210, 120, 210, INK, 2) + line(120, 110, 120, 210, INK, 2)
    s += line(106, 150, 134, 150, INK, 3) + line(113, 163, 127, 163, INK, 2)
    s += text(96, 146, "+", 12, RED, "middle", "bold") + text(96, 172, "−", 12, BLUE, "middle", "bold")
    s += text(150, 185, "5 В", 11, INK, "start", "bold")
    s += rect(240, 98, 96, 24, "#ffffff", INK, 1.6) + text(288, 114, "R = 300 Ω", 10, INK, "middle", "bold")
    s += _diode_h(440, 110, 12, True)
    s += arrow(444, 96, 452, 82, SUN, 1.6) + arrow(456, 98, 464, 84, SUN, 1.6)
    s += text(440, 140, "U_F = 2 В", 9.5, RED, "middle", "bold")
    s += arrow(165, 110, 205, 110, GREEN, 2)
    s += text(330, 168, "I = 10 мА", 11, GREEN, "middle", "bold")
    s += text(W / 2, 250, "U_R = 5 − 2 = 3 В   →   I = 3 / 300 = 10 мА", 11.5, INK, "middle", "bold")
    save("fig-10-7-3-led-circuit.svg", s)


# ── Рис. 10.7.4 — фотодіод ───────────────────────────────────────────────────
def fig71_photodiode():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Фотодіод: світло народжує струм", 16.5, INK, "middle", "bold")
    bx, by, bw, bh = 130, 150, 400, 80
    mid = bx + bw / 2
    dep = 40
    s += rect(bx, by, bw / 2, bh, "#eef3fb", "#9bb0c2", 1.2)
    s += rect(mid, by, bw / 2, bh, "#fbeeee", "#c9a0a0", 1.2)
    s += rect(mid - dep, by, 2 * dep, bh, "#f3f0e6", "#9c6a16", 1.2)
    s += text(bx + 50, by - 10, "n", 13, BLUE, "middle", "bold")
    s += text(bx + bw - 50, by - 10, "p", 13, RED, "middle", "bold")
    s += _photon(mid - 95, 72, mid, by - 2, SUN)
    s += text(mid - 101, 66, "світло", 10.5, COPP, "end", "bold")
    s += el(mid - 14, by + bh / 2)
    s += arrow(mid - 24, by + bh / 2, mid - dep - 28, by + bh / 2, BLUE, 1.8)
    s += ho(mid + 14, by + bh / 2)
    s += arrow(mid + 24, by + bh / 2, mid + dep + 28, by + bh / 2, RED, 1.8)
    s += text(mid, by + bh + 18, "пара народжується, поле розводить", 9, "#9c6a16", "middle")
    cmx = bx + bw / 2
    s += line(bx, by + bh / 2, bx - 32, by + bh / 2, INK, 2) + line(bx - 32, by + bh / 2, bx - 32, 272, INK, 2)
    s += line(bx - 32, 272, bx + bw + 32, 272, INK, 2)
    s += line(bx + bw + 32, 272, bx + bw + 32, by + bh / 2, INK, 2) + line(bx + bw + 32, by + bh / 2, bx + bw, by + bh / 2, INK, 2)
    s += circle(cmx, 272, 14, "#ffffff", INK, 1.6) + text(cmx, 277, "мкА", 9, INK, "middle", "bold")
    s += arrow(bx - 32, 244, bx - 32, 258, GREEN, 2)
    s += text(W / 2, H - 10, "Фотон народжує пару електрон–дірка; вбудоване поле розводить їх — тече фотострум.",
              10, GREY, "middle", style="italic")
    save("fig-10-7-4-photodiode.svg", s)


# ── Рис. 10.7.5 — сонячний елемент ───────────────────────────────────────────
def fig71_solar_cell():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Сонячний елемент — великий фотодіод", 16.5, INK, "middle", "bold")
    s += _sun(110, 95, 16)
    s += text(110, 130, "світло", 10, COPP, "middle", "bold")
    for k in range(5):
        s += _photon(170 + k * 38, 110, 220 + k * 38, 168, SUN, 3.0, 2)
    s += rect(200, 175, 300, 40, "#1f3a6b", "#16294d", 1.5)
    s += text(350, 200, "сонячна комірка (PN-перехід)", 10, "#ffffff", "middle", "bold")
    s += line(200, 195, 160, 195, INK, 2) + line(160, 195, 160, 252, INK, 2)
    s += line(500, 195, 540, 195, INK, 2) + line(540, 195, 540, 252, INK, 2)
    s += line(160, 252, 540, 252, INK, 2)
    s += rect(328, 240, 44, 24, "#ffffff", INK, 1.4) + text(350, 256, "навант.", 8.5, INK, "middle", "bold")
    s += arrow(160, 232, 160, 248, GREEN, 2)
    s += text(350, 285, "світло народжує струм — елемент живить навантаження", 10, GREY, "middle", style="italic")
    save("fig-10-7-5-solar-cell.svg", s)


# ── Рис. 10.7.6 — дзеркальна пара ────────────────────────────────────────────
def fig71_symmetry():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 26, "Світлодіод і фотодіод — дзеркальна пара", 16.5, INK, "middle", "bold")
    # ліва — світлодіод
    s += _frame(40, 56, 300, 200, "світлодіод: струм → світло")
    s += _battery(110, 160, True)
    s += line(80, 160, 178, 160, INK, 2)
    s += _diode_h(195, 160, 13, True)
    s += line(210, 160, 300, 160, INK, 2)
    s += arrow(200, 142, 214, 120, SUN, 1.8) + arrow(210, 144, 224, 122, SUN, 1.8)
    s += text(190, 210, "подаємо струм → світить", 9.5, GREEN, "middle", "bold")
    # права — фотодіод
    s += _frame(380, 56, 300, 200, "фотодіод: світло → струм")
    s += _diode_h(545, 160, 13, True)
    s += arrow(534, 120, 548, 142, SUN, 1.8) + arrow(544, 122, 558, 144, SUN, 1.8)
    s += line(420, 160, 531, 160, INK, 2) + line(559, 160, 640, 160, INK, 2)
    s += line(640, 160, 640, 220, INK, 2) + line(640, 220, 420, 220, INK, 2) + line(420, 220, 420, 160, INK, 2)
    s += circle(470, 160, 13, "#ffffff", INK, 1.6) + text(470, 165, "A", 10, INK, "middle", "bold")
    s += text(545, 210, "світло → виникає струм", 9.5, RED, "middle", "bold")
    save("fig-10-7-6-symmetry.svg", s)


# ── Рис. 10.7і.1 — таймлайн ──────────────────────────────────────────────────
def fig_led1_timeline():
    W, H = 900, 210
    s = header(W, H)
    s += text(W / 2, 32, "Довга дорога світлодіода: пів століття від зблиску до світла", 17, INK, "middle", "bold")
    boxes = [
        ("1907 · Раунд", ["побачив вогник", "кристала"], "#fbfbfb"),
        ("1920-ті · Лосєв", ["пояснив", "«холодне світло»"], "#fdf1dc"),
        ("1962 · Голоньяк", ["перший", "практичний LED"], "#fbfbfb"),
        ("1990-ті · Накамура", ["синій →", "біле світло"], "#fbfbfb"),
        ("сьогодні", ["світло", "всюди"], LGRN),
    ]
    bw, gap, by, bh = 156, 18, 80, 90
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 20 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 11, INK, "middle", "bold")
        border = "#9bb0c2" if fill == LGRN else ("#d8b46a" if fill == "#fdf1dc" else "#c9d3dc")
        s += rect(bx, by, bw, bh, fill, border, 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 36 + k * 22, ln, 11, INK, "middle")
        if i < len(boxes) - 1:
            ax = bx + bw
            s += arrow(ax + 2, by + bh / 2, ax + gap - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Лосєв (виділено) зрозумів це світло за десятиліття до того, як його змогли втілити.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-7i-1-timeline.svg", s)


# ── Рис. 10.7і.2 — Раунд ─────────────────────────────────────────────────────
def fig_led2_round():
    W, H = 620, 320
    s = header(W, H)
    s += text(W / 2, 30, "Раунд, 1907: вогник на кристалі карбіду кремнію", 15.5, INK, "middle", "bold")
    s += rect(220, 222, 160, 26, "#d9c9a8", INK, 1.6, 4)
    s += text(300, 240, "тримач", 9.5, INK, "middle")
    cr = "M 240,222 L 258,188 L 285,198 L 312,182 L 340,200 L 360,222 Z"
    s += f'<path d="{cr}" fill="#b9bfc6" stroke="{INK}" stroke-width="1.8"/>\n'
    s += text(300, 214, "карборунд (SiC)", 9.5, INK, "middle", "bold")
    s += _poly([(430, 92), (410, 122), (360, 132), (330, 166), (305, 186)], COPP, 2)
    s += text(442, 94, "дротик", 10, COPP, "start", "bold")
    s += _sun(305, 186, 10, SUN)
    s += text(305, 152, "вогник", 10, COPP, "middle", "bold")
    s += text(150, 150, "+10 В", 10, INK, "middle", "bold")
    s += line(150, 160, 150, 235, INK, 2) + line(150, 235, 220, 235, INK, 2)
    s += line(430, 92, 430, 72, INK, 2)
    s += text(W / 2, H - 14, "Подаємо напругу — біля контакту жевріє світло. Раунд занотував це й не став копати глибше.",
              10, GREY, "middle", style="italic")
    save("fig-10-7i-2-round.svg", s)


# ── Рис. 10.7і.3 — холодне світло ────────────────────────────────────────────
def fig_led3_cold_light():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Лосєв: світло холодне — отже, квантове", 16, INK, "middle", "bold")
    s += _frame(40, 60, 300, 200, "світить, але не гріється")
    s += rect(120, 172, 140, 24, "#b9bfc6", INK, 1.4, 3)
    s += _sun(190, 152, 13, SUN)
    s += _photon(190, 140, 252, 92, SUN, 3, 2)
    s += text(108, 120, "0°", 13, BLUE, "middle", "bold")
    s += text(190, 226, "крапля не випаровується швидше", 8.5, GREY, "middle")
    s += _frame(380, 60, 300, 200, "обернений фотоефект")
    ox, vy, cy, bw = 420, 208, 110, 180
    s += rect(ox, vy, bw, 22, "#e9eefb", BLUE, 1.3) + text(ox + bw / 2, vy + 34, "нижчий рівень", 8.5, GREY, "middle")
    s += rect(ox, cy, bw, 22, "#e7f3ea", GREEN, 1.3) + text(ox + bw / 2, cy - 6, "вищий рівень", 8.5, GREY, "middle")
    s += circle(ox + 40, cy + 11, 4, GREEN, GREEN)
    s += arrow(ox + 40, cy + 24, ox + 40, vy - 2, GREY, 1.6)
    s += _photon(ox + 54, (cy + vy) / 2, ox + 150, (cy + vy) / 2 - 28, SUN, 3, 2)
    s += text(ox + bw / 2, 262, "електрон падає → віддає квант світла", 8.5, GREY, "middle")
    save("fig-10-7i-3-cold-light.svg", s)


# ── Рис. 10.7і.4 — надто рано ────────────────────────────────────────────────
def fig_led4_too_early():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Чому відкриття застрягло на десятиліття", 16, INK, "middle", "bold")
    s += _sun(W / 2, 140, 18, SUN)
    s += text(W / 2, 180, "ідея Лосєва", 11, COPP, "middle", "bold")
    walls = [("нема квантової", "теорії", 150), ("панує лампа", "(вона підсилює)", 360),
             ("нема яскравих", "матеріалів", 570)]
    for top, bot, x in walls:
        s += rect(x - 95, 232, 190, 48, "#fbeeee", "#c9a0a0", 1.4, 6)
        s += text(x, 252, top, 10.5, RED, "middle", "bold")
        s += text(x, 270, bot, 9.5, INK, "middle")
    s += text(W / 2, H - 10, "Геніальний здогад без теорії, потреби й матеріалів лежить безплідно.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-7i-4-too-early.svg", s)


# ── Рис. 10.7і.5 — колективний внесок ────────────────────────────────────────
def fig_led5_collective():
    W, H = 900, 230
    s = header(W, H)
    s += text(W / 2, 32, "Світлодіод винайшли руки багатьох — чотири країни, пів століття", 16, INK, "middle", "bold")
    people = [("Раунд", "Британія, 1907", "побачив"), ("Лосєв", "СРСР, 1920-ті", "пояснив"),
              ("Голоньяк", "США, 1962", "утілив"), ("Накамура", "Японія, 1990-ті", "зробив білим")]
    bw, gap, by, bh = 190, 30, 92, 92
    for i, (nm, cn, act) in enumerate(people):
        bx = 30 + i * (bw + gap)
        s += rect(bx, by, bw, bh, "#f7f9fb", "#9bb0c2", 1.5, 8)
        s += text(bx + bw / 2, by + 32, nm, 13, INK, "middle", "bold")
        s += text(bx + bw / 2, by + 52, cn, 10, GREY, "middle")
        s += text(bx + bw / 2, by + 74, act, 11, GREEN, "middle", "bold")
        if i < 3:
            ax = bx + bw
            s += arrow(ax + 4, by + bh / 2, ax + gap - 4, by + bh / 2, GREY, 2.2)
    s += text(W / 2, H - 12, "Жодного «єдиного винахідника» чи «однієї нації» — ланцюг внесків через десятиліття.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-7i-5-collective.svg", s)


# ── допоміжне для §10.8 ──────────────────────────────────────────────────────
def _zener_sym(cx, cy, size=12, col=INK):
    t = f'<path d="M {cx-size},{cy-size} L {cx-size},{cy+size} L {cx+size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
    x = cx + size * 0.8
    t += _poly([(x - 4, cy - size), (x, cy - size), (x, cy + size), (x + 4, cy + size)], col, 2.5)
    t += line(cx - size - 12, cy, cx - size, cy, col, 1.8) + line(x, cy, x + 14, cy, col, 1.8)
    return t


def _zener_v(cx, cy, size=13, col=INK):
    tip = cy - size
    t = f'<path d="M {cx-size},{cy+size} L {cx+size},{cy+size} L {cx},{tip:.1f} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
    t += _poly([(cx - size, tip + 4), (cx - size, tip), (cx + size, tip), (cx + size, tip - 4)], col, 2.5)
    return t


# ── Рис. 10.8.1 — ВАХ Зенера ─────────────────────────────────────────────────
def fig81_zener_iv():
    W, H = 700, 380
    s = header(W, H)
    s += text(W / 2, 30, "ВАХ діода Зенера: керований пробій на U_Z", 16.5, INK, "middle", "bold")
    ox0, oy0 = 440, 235
    s += arrow(110, oy0, 645, oy0, INK, 2) + text(652, oy0 + 4, "U", 13, INK, "start", "bold")
    s += arrow(ox0, 360, ox0, 72, INK, 2) + text(ox0 - 8, 64, "I", 13, INK, "middle", "bold")
    fpts = []
    V = 0.0
    while V <= 0.8001:
        f = min(1.0, math.exp((V - 0.72) / 0.045))
        fpts.append((ox0 + V * 250, oy0 - 150 * f))
        V += 0.02
    s += _poly(fpts, RED, 2.8)
    vzx = 200
    s += _poly([(ox0, oy0 + 3), (vzx + 8, oy0 + 8), (vzx, oy0 + 22), (vzx, 350)], BLUE, 2.8)
    s += line(vzx, oy0 - 4, vzx, oy0 + 4, INK, 1.4)
    s += text(vzx, oy0 - 10, "U_Z", 11, BLUE, "middle", "bold")
    s += text(vzx - 10, 300, "робоча ділянка", 9.5, BLUE, "end", "bold")
    s += text(ox0 + 0.5 * 250, 92, "пряма (≈0.7 В)", 9.5, RED, "middle", "bold")
    s += _zener_sym(560, 120)
    s += text(560, 150, "символ Зенера", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Назад Зенер навмисне «ламається» на U_Z і там тримає сталу напругу — це його робочий режим.",
              10, GREY, "middle", style="italic")
    save("fig-10-8-1-zener-iv.svg", s)


# ── Рис. 10.8.2 — стабілізатор ───────────────────────────────────────────────
def fig81_zener_regulator():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Стабілізатор: R гасить надлишок, Зенер тримає U_Z", 15, INK, "middle", "bold")
    s += line(120, 100, 440, 100, INK, 2)
    s += line(120, 100, 120, 210, INK, 2) + line(120, 210, 440, 210, INK, 2)
    s += line(106, 138, 134, 138, INK, 3) + line(113, 151, 127, 151, INK, 2)
    s += text(96, 134, "+", 12, RED, "middle", "bold") + text(96, 160, "−", 12, BLUE, "middle", "bold")
    s += text(150, 175, "12 В", 10, INK, "start", "bold")
    s += rect(195, 88, 84, 24, "#ffffff", INK, 1.6) + text(237, 104, "R 345 Ω", 9.5, INK, "middle", "bold")
    # Зенер (зворотно: катод угору) у вузлі x=340
    s += line(340, 100, 340, 132, INK, 2)
    s += _zener_v(340, 150, 13)
    s += line(340, 165, 340, 210, INK, 2)
    s += text(370, 150, "U_Z = 5.1 В", 9.5, BLUE, "start", "bold")
    # навантаження праворуч
    s += line(340, 100, 440, 100, INK, 2)
    s += rect(428, 130, 24, 50, "#ffffff", INK, 1.4) + text(462, 160, "наван-", 8.5, INK, "start")
    s += text(462, 172, "таження", 8.5, INK, "start")
    s += line(440, 100, 440, 130, INK, 2) + line(440, 180, 440, 210, INK, 2)
    s += arrow(150, 100, 185, 100, GREEN, 2)
    s += text(W / 2, H - 12, "Вихід тримається ≈5.1 В; коливнеться вхід — Зенер підправить струм, а напруга лишиться.",
              10, GREY, "middle", style="italic")
    save("fig-10-8-2-zener-regulator.svg", s)


# ── Рис. 10.8.3 — перехід Шотткі ─────────────────────────────────────────────
def fig81_schottky_junction():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Шотткі: контакт метал–напівпровідник замість p–n", 15.5, INK, "middle", "bold")
    s += _frame(40, 60, 300, 200, "звичайний: p–n")
    s += rect(90, 130, 100, 50, LRED, INK, 1.4) + text(140, 160, "p", 14, RED, "middle", "bold")
    s += rect(190, 130, 100, 50, LBLUE, INK, 1.4) + text(240, 160, "n", 14, BLUE, "middle", "bold")
    s += text(190, 205, "перехід p–n (бар'єр ~0.7 В)", 9, GREY, "middle")
    s += _frame(380, 60, 300, 200, "Шотткі: метал–n")
    s += rect(430, 130, 100, 50, "#c9c9cf", INK, 1.4) + text(480, 160, "метал", 11, INK, "middle", "bold")
    s += rect(530, 130, 100, 50, LBLUE, INK, 1.4) + text(580, 160, "n", 14, BLUE, "middle", "bold")
    s += text(530, 205, "нижчий бар'єр (~0.3 В)", 9, GREY, "middle")
    save("fig-10-8-3-schottky-junction.svg", s)


# ── Рис. 10.8.4 — коліно Шотткі vs Si ────────────────────────────────────────
def fig81_schottky_iv():
    W, H = 680, 330
    s = header(W, H)
    s += text(W / 2, 30, "Пряме коліно: Шотткі ≈0.3 В проти Si ≈0.7 В", 15.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 280, 520, 210
    s += _axes(ox, oy, w, h, "напруга U", "струм I")
    Vmax = 1.0

    def curve(Vk, col, lab, lx):
        pts = []
        V = 0.0
        while V <= Vmax + 1e-6:
            f = min(1.0, math.exp((V - Vk) / 0.045))
            pts.append((ox + (V / Vmax) * w, oy - h * 0.92 * f))
            V += 0.01
        return _poly(pts, col, 2.8) + text(ox + (lx / Vmax) * w, oy - h * 0.86, lab, 10, col, "middle", "bold")

    s += curve(0.3, GREEN, "Шотткі ~0.3", 0.5)
    s += curve(0.7, RED, "Si ~0.7", 0.92)
    s += text(W / 2, H - 12, "Менше падіння — менше втрат і тепла, надто на низьких напругах і великих струмах.",
              10, GREY, "middle", style="italic")
    save("fig-10-8-4-schottky-iv.svg", s)


# ── Рис. 10.8.5 — швидкість Шотткі ───────────────────────────────────────────
def fig81_schottky_fast():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Замикання: звичайний діод має «хвіст», Шотткі — ні", 15, INK, "middle", "bold")
    ox, oy, w = 90, 150, 520
    s += text(190, 74, "звичайний діод", 10, RED, "middle", "bold")
    s += line(ox, oy, ox + w, oy, GREY, 1)
    s += _poly([(ox, oy - 40), (ox + 200, oy - 40), (ox + 210, oy + 32), (ox + 245, oy + 32), (ox + 280, oy)], RED, 2.6)
    s += text(ox + 285, oy + 40, "зворотний «хвіст»", 9, RED, "start", "bold")
    oy2 = 270
    s += text(190, 212, "Шотткі", 10, GREEN, "middle", "bold")
    s += line(ox, oy2, ox + w, oy2, GREY, 1)
    s += _poly([(ox, oy2 - 40), (ox + 200, oy2 - 40), (ox + 207, oy2), (ox + w, oy2)], GREEN, 2.6)
    s += text(ox + 235, oy2 - 12, "чистий обрив", 9, GREEN, "start", "bold")
    s += line(ox + 200, 70, ox + 200, 292, GREY, 1, dash="4,4")
    s += text(ox + 200, 64, "мить замикання", 8.5, GREY, "middle")
    save("fig-10-8-5-schottky-fast.svg", s)


# ── Рис. 10.8.6 — коли який ──────────────────────────────────────────────────
def fig81_compare():
    W, H = 720, 280
    s = header(W, H)
    s += text(W / 2, 30, "Три діоди — три ролі", 16.5, INK, "middle", "bold")
    items = [("звичайний", "випрямлення й комутація", "~0.7 В, універсальний", "#eef2f6"),
             ("Зенера", "опорна / стабільна напруга", "працює В ПРОБОЇ (U_Z)", "#fdf1dc"),
             ("Шотткі", "ефективні та швидкі кола", "~0.3 В, дуже швидкий", "#e7f3ea")]
    y = 66
    for nm, role, trait, fill in items:
        s += rect(60, y, 600, 52, fill, "#9bb0c2", 1.3, 8)
        s += text(150, y + 31, nm,13, INK, "middle", "bold")
        s += line(250, y + 8, 250, y + 44, "#c9d3dc", 1)
        s += text(455, y + 22, role, 10.5, INK, "middle")
        s += text(455, y + 40, trait, 9.5, GREY, "middle")
        y += 66
    s += text(W / 2, H - 10, "Усі троє — той самий PN-перехід (чи його родич), налаштований під конкретну задачу.",
              10, GREY, "middle", style="italic")
    save("fig-10-8-6-compare.svg", s)


# ── Рис. 10.8і.1 — ворог чи інструмент ───────────────────────────────────────
def fig_zen1_enemy_to_tool():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Той самий пробій: аварія для звичайного діода — інструмент для Зенера", 13.5, INK, "middle", "bold")
    s += _frame(40, 60, 300, 200, "звичайний діод")
    s += _diode_h(150, 135, 14, True, RED)
    for a in range(8):
        ang = a * math.pi / 4
        s += line(150, 135, 150 + 22 * math.cos(ang), 135 + 22 * math.sin(ang), RED, 2)
    s += text(190, 185, "неконтрольований пробій", 9.5, RED, "middle", "bold")
    s += text(190, 203, "→ перегрів, смерть", 9.5, RED, "middle")
    s += _frame(380, 60, 300, 200, "діод Зенера")
    s += _diode_h(480, 135, 14, True, GREEN)
    s += line(530, 118, 560, 118, GREEN, 2.6) + text(575, 122, "U_Z", 10, GREEN, "start", "bold")
    s += text(530, 185, "керований пробій", 9.5, GREEN, "middle", "bold")
    s += text(530, 203, "→ стала напруга", 9.5, GREEN, "middle")
    save("fig-10-8i-1-enemy-to-tool.svg", s)


# ── Рис. 10.8і.2 — тунелювання ───────────────────────────────────────────────
def fig_zen2_tunneling():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Ефект Зенера: електрон тунелює крізь бар'єр", 16, INK, "middle", "bold")
    s += rect(330, 95, 40, 135, "#d0d4da", INK, 1.5)
    s += text(350, 250, "бар'єр (щілина)", 9.5, INK, "middle")
    s += el(250, 162)
    s += text(250, 142, "електрон", 9, BLUE, "middle")
    s += arrow(266, 162, 470, 162, GREEN, 2.4, dash="5,4")
    s += text(480, 166, "тунелює — крізь стіну", 10, GREEN, "start", "bold")
    s += f'<path d="M 262,150 Q 350,46 442,150" fill="none" stroke="{GREY}" stroke-width="1.6" stroke-dasharray="3,3"/>\n'
    s += line(345, 72, 355, 82, RED, 2) + line(355, 72, 345, 82, RED, 2)
    s += text(350, 54, "над стіною — зась", 8.5, GREY, "middle")
    s += text(W / 2, H - 14, "Сильне поле робить бар'єр тонким — і квантовий електрон проходить наскрізь, а не над ним.",
              10, GREY, "middle", style="italic")
    save("fig-10-8i-2-tunneling.svg", s)


# ── Рис. 10.8і.3 — стеля U_Z ─────────────────────────────────────────────────
def fig_zen3_controlled():
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 28, "Зенер тримає напругу: впирається в «стелю» U_Z", 15.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 270, 500, 200
    s += _axes(ox, oy, w, h, "струм крізь діод", "напруга")
    pts = []
    for i in range(101):
        t = i / 100
        v = 0.85 * (1 - math.exp(-t * 11))
        pts.append((ox + w * t, oy - h * v))
    s += _poly(pts, BLUE, 2.8)
    s += line(ox, oy - h * 0.85, ox + w, oy - h * 0.85, GREY, 1, dash="4,4")
    s += text(ox + w, oy - h * 0.85 - 6, "U_Z (стеля)", 10, BLUE, "end", "bold")
    s += text(ox + 0.62 * w, oy - h * 0.7, "напруга майже стала", 10, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Хоч як росте струм, напруга впирається в U_Z і далі не йде — це і є стабілізація.",
              10, GREY, "middle", style="italic")
    save("fig-10-8i-3-controlled.svg", s)


# ── Рис. 10.8і.4 — два механізми ─────────────────────────────────────────────
def fig_zen4_two_mechanisms():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Два механізми під одним іменем", 16, INK, "middle", "bold")
    s += _frame(40, 60, 300, 180, "ефект Зенера (тунелювання)")
    s += rect(120, 120, 28, 80, "#d0d4da", INK, 1.4)
    s += el(95, 160)
    s += arrow(110, 160, 205, 160, GREEN, 2, dash="5,4")
    s += text(190, 215, "тонкий перехід, < 5 В", 9, GREY, "middle")
    s += _frame(380, 60, 300, 180, "лавинний пробій")
    s += el(420, 150)
    s += arrow(432, 150, 468, 142, RED, 1.8)
    s += el(478, 134)
    s += el(478, 162)
    s += arrow(488, 134, 520, 128, RED, 1.6)
    s += arrow(488, 162, 520, 170, RED, 1.6)
    for yy in (118, 140, 162, 184):
        s += el(530, yy)
    s += text(540, 215, "лавина носіїв, > 5 В", 9, GREY, "middle")
    s += text(W / 2, H - 26, "Десь біля 5.6 В обидва врівноважуються — і там стабілітрон найменше «пливе» від температури.",
              9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 10, "Більшість «зенерів» вище ~5.5 В насправді лавинні.", 9.5, INK, "middle", "bold")
    save("fig-10-8i-4-two-mechanisms.svg", s)


# ── Рис. 10.8і.5 — звідки ім'я ───────────────────────────────────────────────
def fig_zen5_naming():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Звідки ім'я: теорія, прилад і механізм — від різних людей", 14.5, INK, "middle", "bold")
    boxes = [("Зенер", "теорія тунелювання", "1934, для ізоляторів", 70),
             ("Bell Labs", "збудували прилад", "≈1950", 290),
             ("Маккей", "пояснив лавину", "1953", 510)]
    for nm, role, when, x in boxes:
        s += rect(x, 66, 180, 80, "#f7f9fb", "#9bb0c2", 1.4, 8)
        s += text(x + 90, 94, nm, 12.5, INK, "middle", "bold")
        s += text(x + 90, 114, role, 9.5, INK, "middle")
        s += text(x + 90, 132, when, 9, GREY, "middle")
        s += arrow(x + 90, 150, W / 2, 204, GREY, 1.6)
    s += rect(W / 2 - 130, 208, 260, 40, "#fdf1dc", "#d8b46a", 1.5, 8)
    s += text(W / 2, 233, "«діод Зенера»", 13, "#9c6a16", "middle", "bold")
    s += text(W / 2, H - 10, "Назва вшановує ідею-зерно — не будівничого приладу й не точний механізм.",
              10, GREY, "middle", style="italic")
    save("fig-10-8i-5-naming.svg", s)


def coil_h(cx, cy, length, turns=5, ry=18, col=COPP):
    x0 = cx - length / 2
    dx = length / turns
    s = ""
    for i in range(turns + 1):
        s += f'<ellipse cx="{x0+i*dx:.1f}" cy="{cy:.1f}" rx="6" ry="{ry}" fill="none" stroke="{col}" stroke-width="2"/>\n'
    return s, (x0, x0 + length)


# ── Рис. 10.9.1 — сплеск котушки ─────────────────────────────────────────────
def fig91_coil_spike():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Розмикання котушки → небезпечний сплеск", 16, INK, "middle", "bold")
    s += line(120, 90, 500, 90, INK, 2)
    s += line(106, 130, 134, 130, INK, 3) + line(113, 143, 127, 143, INK, 2)
    s += text(96, 126, "+", 12, RED, "middle", "bold") + text(150, 166, "живлення", 9.5, INK, "start")
    s += line(120, 90, 120, 210, INK, 2) + line(120, 210, 500, 210, INK, 2)
    cl, (x0, x1) = coil_h(260, 90, 90, 5, 12)
    s += cl
    s += text(260, 64, "котушка", 9.5, COPP, "middle", "bold")
    s += line(500, 90, 500, 138, INK, 2)
    s += circle(500, 138, 3, INK, INK)
    s += line(500, 138, 522, 116, INK, 2)
    s += circle(500, 180, 3, INK, INK)
    s += line(500, 180, 500, 210, INK, 2)
    s += text(540, 152, "ключ (розмикається)", 9, INK, "start")
    s += _poly([(500, 138), (488, 126), (498, 122), (486, 110), (500, 104)], RED, 2.5)
    s += text(470, 98, "сплеск!", 10, RED, "end", "bold")
    s += text(W / 2, H - 14, "Поле котушки, спадаючи, наводить різкий викид напруги — і він б'є по ключу.",
              10, GREY, "middle", style="italic")
    save("fig-10-9-1-coil-spike.svg", s)


# ── Рис. 10.9.2 — гасний діод ────────────────────────────────────────────────
def fig91_flyback():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Гасний діод паралельно котушці", 16, INK, "middle", "bold")
    s += line(120, 90, 500, 90, INK, 2)
    s += line(106, 130, 134, 130, INK, 3) + line(113, 143, 127, 143, INK, 2)
    s += text(96, 126, "+", 12, RED, "middle", "bold")
    s += line(120, 90, 120, 210, INK, 2) + line(120, 210, 500, 210, INK, 2)
    cl, (x0, x1) = coil_h(260, 90, 90, 5, 12)
    s += cl
    s += text(260, 64, "котушка", 9.5, COPP, "middle", "bold")
    # гасний діод паралельно котушці (нижче), вістрям до «+» (вліво)
    s += line(x0, 90, x0, 140, INK, 2) + line(x1, 90, x1, 140, INK, 2) + line(x0, 140, x1, 140, INK, 2)
    s += _diode_h((x0 + x1) / 2, 140, 11, False)
    s += text((x0 + x1) / 2, 162, "гасний діод", 9.5, GREEN, "middle", "bold")
    # ключ
    s += line(500, 90, 500, 138, INK, 2) + circle(500, 138, 3, INK, INK)
    s += line(500, 138, 522, 116, INK, 2) + circle(500, 180, 3, INK, INK) + line(500, 180, 500, 210, INK, 2)
    s += text(540, 152, "ключ", 9, INK, "start")
    s += text(W / 2, H - 14, "У нормі діод замкнений. Коли ключ розмикається — відкривається й замикає струм котушки на себе.",
              9.5, GREY, "middle", style="italic")
    save("fig-10-9-2-flyback.svg", s)


# ── Рис. 10.9.3 — дія гасного діода ──────────────────────────────────────────
def fig91_flyback_action():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Напруга на ключі при розмиканні: без діода й з діодом", 14.5, INK, "middle", "bold")
    ox, oy, w = 90, 150, 520
    s += text(180, 70, "без діода", 10, RED, "middle", "bold")
    s += line(ox, oy, ox + w, oy, GREY, 1)
    s += _poly([(ox, oy - 20), (ox + 200, oy - 20), (ox + 205, oy - 122), (ox + 214, oy - 20), (ox + w, oy - 20)], RED, 2.6)
    s += text(ox + 205, oy - 130, "сплеск (сотні В)", 9, RED, "middle", "bold")
    oy2 = 270
    s += text(190, 208, "з гасним діодом", 10, GREEN, "middle", "bold")
    s += line(ox, oy2, ox + w, oy2, GREY, 1)
    s += _poly([(ox, oy2 - 20), (ox + 200, oy2 - 20), (ox + 206, oy2 - 40), (ox + 360, oy2 - 40), (ox + w, oy2 - 22)], GREEN, 2.6)
    s += text(ox + 366, oy2 - 46, "обмежено ~живлення", 9, GREEN, "start", "bold")
    s += line(ox + 200, 60, ox + 200, 292, GREY, 1, dash="4,4")
    s += text(ox + 200, 54, "розмикання", 8.5, GREY, "middle")
    save("fig-10-9-3-flyback-action.svg", s)


# ── Рис. 10.9.4 — послідовний захисний діод ──────────────────────────────────
def fig91_rev_pol_series():
    W, H = 700, 280
    s = header(W, H)
    s += text(W / 2, 28, "Послідовний діод: захист від зворотної полярності", 15, INK, "middle", "bold")
    s += line(120, 100, 560, 100, INK, 2) + line(120, 100, 120, 200, INK, 2)
    s += line(120, 200, 560, 200, INK, 2) + line(560, 100, 560, 200, INK, 2)
    s += line(106, 140, 134, 140, INK, 3) + line(113, 153, 127, 153, INK, 2)
    s += text(96, 136, "+", 12, RED, "middle", "bold") + text(150, 178, "батарея", 9.5, INK, "start")
    s += _diode_h(300, 100, 12, True)
    s += text(300, 80, "діод", 9.5, INK, "middle", "bold")
    s += rect(548, 130, 24, 40, "#ffffff", INK, 1.5)
    s += text(542, 152, "наван-", 8.5, INK, "end") + text(542, 164, "таження", 8.5, INK, "end")
    s += arrow(170, 100, 210, 100, GREEN, 2) + text(420, 90, "струм тече", 10, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Плюс на анод — діод відкритий, схема працює (ціною ~0.7 В).", 10, GREY, "middle", style="italic")
    save("fig-10-9-4-rev-pol-series.svg", s)


# ── Рис. 10.9.5 — правильно/навпаки ──────────────────────────────────────────
def fig91_rev_pol_cases():
    W, H = 720, 280
    s = header(W, H)
    s += text(W / 2, 28, "Правильно — працює; навпаки — безпечно", 15.5, INK, "middle", "bold")
    s += _frame(40, 60, 300, 190, "правильна полярність")
    s += text(110, 144, "+", 13, RED, "middle", "bold")
    s += arrow(122, 140, 168, 140, GREEN, 2)
    s += _diode_h(190, 140, 13, True, GREEN)
    s += line(205, 140, 300, 140, GREEN, 2)
    s += text(190, 182, "діод проводить → працює", 9, GREEN, "middle", "bold")
    s += _frame(380, 60, 300, 190, "переплутана полярність")
    s += text(450, 144, "−", 13, BLUE, "middle", "bold")
    s += line(462, 140, 510, 140, INK, 2)
    s += _diode_h(530, 140, 13, True, RED)
    s += line(508, 126, 524, 154, RED, 2.5) + line(524, 126, 508, 154, RED, 2.5)
    s += text(530, 182, "діод блокує → безпечно", 9, RED, "middle", "bold")
    save("fig-10-9-5-rev-pol-cases.svg", s)


# ── Рис. 10.9.6 — обмежувальні діоди ─────────────────────────────────────────
def fig91_clamps():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Обмежувальні діоди: відводять викид у шини", 15, INK, "middle", "bold")
    s += line(120, 80, 580, 80, RED, 2) + text(112, 84, "+V", 11, RED, "end", "bold")
    s += line(120, 240, 580, 240, BLUE, 2) + text(112, 244, "0 (GND)", 10, BLUE, "end", "bold")
    nx = 350
    s += line(150, 160, nx, 160, INK, 2) + text(144, 160, "вхід", 10, INK, "end", "bold")
    s += circle(nx, 160, 3, INK, INK)
    # верхній діод (вузол → +V), вістрям угору
    s += f'<path d="M {nx-9},150 L {nx+9},150 L {nx},120 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.4"/>\n'
    s += line(nx - 9, 118, nx + 9, 118, INK, 2.4) + line(nx, 118, nx, 80, INK, 2) + line(nx, 160, nx, 150, INK, 2)
    s += text(nx + 16, 112, "відводить, якщо вище +V", 8.5, RED, "start")
    # нижній діод (GND → вузол), вістрям угору
    s += f'<path d="M {nx-9},232 L {nx+9},232 L {nx},202 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.4"/>\n'
    s += line(nx - 9, 200, nx + 9, 200, INK, 2.4) + line(nx, 200, nx, 160, INK, 2) + line(nx, 240, nx, 232, INK, 2)
    s += text(nx + 16, 214, "підтягує, якщо нижче 0", 8.5, BLUE, "start")
    s += text(W / 2, H - 12, "У нормі обидва замкнені. Викид за межі — відповідний діод притискає вхід назад до шини.",
              10, GREY, "middle", style="italic")
    save("fig-10-9-6-clamps.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 10
    fig_timeline()
    fig_cat_whisker()
    fig_tube_vs_crystal()
    fig_ohl_junction()
    fig_one_way_valve()
    # §10.1 Напівпровідник
    fig11_resistivity_spectrum()
    fig11_silicon_lattice()
    fig11_broken_bond()
    fig11_energy_gap()
    fig11_temp_dependence()
    fig11_controllable()
    # §10.2 Легування
    fig21_hole_motion()
    fig21_electron_hole_pair()
    fig21_n_type()
    fig21_p_type()
    fig21_majority_minority()
    fig21_doping_amount()
    # §10.3 PN-перехід
    fig31_meet()
    fig31_diffuse_recombine()
    fig31_depletion_region()
    fig31_builtin_field()
    fig31_barrier()
    fig31_equilibrium()
    # §10.4 Пряме й зворотне зміщення
    fig41_forward_bias()
    fig41_reverse_bias()
    fig41_barrier_shift()
    fig41_valve_analogy()
    fig41_anode_cathode()
    # §10.5 ВАХ діода
    fig51_iv_curve()
    fig51_forward_knee()
    fig51_materials()
    fig51_breakdown()
    fig51_models()
    fig51_worked()
    # §10.6 Випрямлення
    fig61_ac_vs_dc()
    fig61_halfwave()
    fig61_bridge()
    fig61_fullwave_output()
    fig61_smoothing()
    # §10.7 Світлодіод і фотодіод
    fig71_led_recombination()
    fig71_color_bandgap()
    fig71_led_circuit()
    fig71_photodiode()
    fig71_solar_cell()
    fig71_symmetry()
    # 📜 історія до §10.7 — Лосєв
    fig_led1_timeline()
    fig_led2_round()
    fig_led3_cold_light()
    fig_led4_too_early()
    fig_led5_collective()
    # §10.8 Особливі діоди
    fig81_zener_iv()
    fig81_zener_regulator()
    fig81_schottky_junction()
    fig81_schottky_iv()
    fig81_schottky_fast()
    fig81_compare()
    # 📜 історія до §10.8 — Зенер
    fig_zen1_enemy_to_tool()
    fig_zen2_tunneling()
    fig_zen3_controlled()
    fig_zen4_two_mechanisms()
    fig_zen5_naming()
    # §10.9 Захист
    fig91_coil_spike()
    fig91_flyback()
    fig91_flyback_action()
    fig91_rev_pol_series()
    fig91_rev_pol_cases()
    fig91_clamps()
    print("OK — Розділ 10 ПОВНІСТЮ (історія + §10.1–§10.9 + 2 історії до тем) згенеровано в", OUT)
