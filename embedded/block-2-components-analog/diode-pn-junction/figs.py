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


# ═════════════════════════════════════════════════════════════════════════════
#  §10.10 — Оптопара й гальванічна розв'язка (тема 2.5.10)
# ═════════════════════════════════════════════════════════════════════════════
def _phototrans(cx, cy, r=26, col=INK):
    """Фототранзистор: коло з NPN-символом і двома фотонами в базу."""
    s = circle(cx, cy, r, "#ffffff", col, 2)
    bx = cx - r * 0.35
    s += line(bx, cy - r * 0.5, bx, cy + r * 0.5, col, 2.6)            # база-планка
    s += line(bx, cy - r * 0.22, cx + r * 0.5, cy - r * 0.55, col, 2)  # колектор
    s += line(bx, cy + r * 0.22, cx + r * 0.5, cy + r * 0.55, col, 2)  # емітер
    # стрілка емітера
    ex, ey = cx + r * 0.5, cy + r * 0.55
    s += f'<path d="M {ex:.1f},{ey:.1f} L {ex-9:.1f},{ey-2:.1f} L {ex-5:.1f},{ey-9:.1f} Z" fill="{col}"/>\n'
    return s


def fig5a10_1_need():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Дві «землі», які не можна з'єднувати дротом", 18, INK, "middle", "bold")
    # ліве коло
    s += _frame(40, 70, 300, 210, "бік мікроконтролера (5 В, тиха земля)")
    s += rect(90, 150, 90, 50, "#eef6ef", GREEN, 1.6, 6) + text(135, 180, "MCU", 12, INK, "middle", "bold")
    s += text(135, 250, "земля A", 11, BLUE, "middle", "bold")
    # праве коло
    s += _frame(480, 70, 300, 210, "бік мережі (сотні вольт, «брудна» земля)")
    s += rect(580, 150, 110, 50, "#fbecec", RED, 1.6, 6) + text(635, 180, "230 В ~", 12, RED, "middle", "bold")
    s += text(635, 250, "земля B", 11, BLUE, "middle", "bold")
    # небезпечний дріт
    s += line(180, 175, 580, 175, RED, 2.4, dash="7,5")
    s += text(380, 165, "прямий дріт", 11, RED, "middle", "bold")
    # перекреслення
    s += line(360, 150, 400, 200, RED, 4) + line(400, 150, 360, 200, RED, 4)
    s += text(W / 2, H - 14, "З'єднати мідь = пустити сотні вольт у логіку й завадні петлі по «землях». Потрібен зв'язок БЕЗ струму.",
              11, GREY, "middle", style="italic")
    save("fig-10-10-1-need.svg", s)


def fig5a10_2_inside():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 30, "Оптопара зсередини: світло замість дроту", 18, INK, "middle", "bold")
    # корпус
    s += rect(150, 70, 540, 230, "#f4f1ea", "#b8a98a", 1.8, 10)
    s += text(420, 92, "непрозорий корпус (світло не виходить назовні)", 10.5, "#9c6a16", "middle", style="italic")
    # ізоляційний бар'єр посередині
    bxm = 420
    s += line(bxm, 110, bxm, 286, "#9bb0c2", 2, dash="4,5")
    s += rect(bxm - 26, 150, 52, 96, "#eef3fb", "#9bb0c2", 1.2)
    s += text(bxm, 270, "прозорий ізолятор", 9, "#5b6b7a", "middle")
    # лівий бік — світлодіод
    s += text(285, 120, "вхід", 12, GREEN, "middle", "bold")
    s += _diode_h(300, 190, 14, True, RED)
    s += text(300, 224, "світлодіод", 10, RED, "middle", "bold")
    s += line(200, 190, 286, 190, INK, 2) + line(314, 190, 360, 190, INK, 2)
    s += line(200, 190, 200, 250, INK, 2) + text(190, 165, "A", 11, INK, "end", "bold")
    s += line(360, 190, 360, 250, INK, 2) + text(372, 165, "K", 11, INK, "start", "bold")
    s += line(180, 250, 360, 250, INK, 2)
    # фотони через бар'єр
    for k in range(3):
        s += _photon(352, 175 + k * 12, bxm + 38, 175 + k * 12, SUN, 3.0, 2)
    # правий бік — фототранзистор
    s += _phototrans(540, 190, 26, INK)
    s += text(540, 234, "фототранзистор", 10, INK, "middle", "bold")
    s += line(560, 172, 620, 172, INK, 2) + line(620, 172, 620, 250, INK, 2) + text(632, 150, "C", 11, INK, "start", "bold")
    s += line(560, 208, 620, 208, INK, 2) + line(620, 208, 620, 250, INK, 2) + text(632, 230, "E", 11, INK, "start", "bold")
    s += text(540, 120, "вихід", 12, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Струм у світлодіоді → світло → фотострум у транзисторі. Сигнал перейшов, а міді між боками НЕМАЄ.",
              11, GREY, "middle", style="italic")
    save("fig-10-10-2-inside.svg", s)


def fig5a10_3_ctr():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 30, "CTR: скільки виходу дає вхід", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "коефіцієнт передачі струму CTR = I_C / I_F  (у PC817-класу ≈ 50…600 %)",
              12, GREY, "middle", style="italic")
    # вхідний бік
    s += line(70, 120, 70, 250, INK, 2) + text(60, 120, "+5 В", 10, RED, "end", "bold")
    s += rect(54, 150, 32, 16, "#ffffff", INK, 1.5) + text(110, 162, "R1", 11, INK, "start", "bold")
    s += text(150, 150, "I_F = (5−1.2)/R1", 10.5, INK, "start")
    s += text(150, 168, "візьмемо 10 мА", 10.5, GREEN, "start", "bold")
    s += _diode_h(70, 200, 11, False, RED)
    s += arrow(70, 215, 70, 245, GREEN, 2) + text(80, 234, "I_F", 11, GREEN, "start", "bold")
    s += text(70, 270, "вхід", 11, INK, "middle", "bold")
    # бар'єр
    s += line(300, 90, 300, 300, "#9bb0c2", 2, dash="4,5")
    s += text(300, 314, "ізоляція", 9.5, "#5b6b7a", "middle")
    # вихідний бік
    s += line(560, 110, 560, 150, INK, 2) + text(560, 100, "+V_OUT", 10, RED, "middle", "bold")
    s += rect(544, 150, 32, 16, "#ffffff", INK, 1.5) + text(600, 162, "R_C (навантаження)", 10.5, INK, "start")
    s += _phototrans(560, 215, 24, INK)
    s += arrow(560, 178, 560, 192, GREEN, 2)
    s += line(560, 239, 560, 280, INK, 2) + text(560, 296, "вихід", 11, INK, "middle", "bold")
    s += text(620, 215, "I_C ≈ CTR·I_F", 11.5, INK, "start", "bold")
    s += text(620, 233, "при CTR=200%:", 10, GREY, "start")
    s += text(620, 249, "I_C ≈ 20 мА", 11, GREEN, "start", "bold")
    s += text(W / 2, H - 12, "Резистори рахують ОКРЕМО з кожного боку; CTR гуляє від партії й падає з роками — беруть запас.",
              11, GREY, "middle", style="italic")
    save("fig-10-10-3-ctr.svg", s)


def fig5a10_4_isolation():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Бар'єр ізоляції: кіловольти, які не пройдуть", 18, INK, "middle", "bold")
    # бар'єр
    s += rect(386, 70, 48, 230, "#eef3fb", "#9bb0c2", 1.6, 6)
    s += text(410, 60, "ізоляційний бар'єр", 10.5, "#5b6b7a", "middle", "bold")
    s += text(410, 180, "≈ 5 кВ", 15, RED, "middle", "bold")
    s += text(410, 200, "витримує", 10, GREY, "middle")
    # ліворуч — небезпечний бік
    s += rect(70, 110, 250, 150, "#fbecec", RED, 1.6, 8)
    s += text(195, 100, "первинний бік (небезпека)", 10.5, RED, "middle", "bold")
    s += text(195, 160, "230 В ~", 16, RED, "middle", "bold")
    s += text(195, 195, "мережа, мотор, нагрівач", 10, GREY, "middle")
    s += _photon(322, 185, 384, 185, SUN, 3, 2)
    # праворуч — безпечний бік
    s += rect(500, 110, 250, 150, "#eef6ef", GREEN, 1.6, 8)
    s += text(625, 100, "вторинний бік (людина, USB)", 10.5, "#1f6e33", "middle", "bold")
    s += text(625, 160, "3.3 В", 16, "#1f6e33", "middle", "bold")
    s += text(625, 195, "контролер, ноутбук, ти", 10, GREY, "middle")
    s += text(W / 2, H - 12, "Світло переносить сигнал, а напруга лишається по свій бік стіни. Пробою немає — є гальванічна розв'язка.",
              11, GREY, "middle", style="italic")
    save("fig-10-10-4-isolation.svg", s)


def fig5a10_5_speed():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Ціна простоти — швидкість", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "фототранзистор накопичує заряд у базі — фронти «розпливаються»", 12, GREY, "middle", style="italic")
    # вхід — різкий меандр
    s += text(120, 90, "вхід (різкий меандр):", 11, INK, "start", "bold")
    ox, oy = 120, 150
    pts = []
    for k in range(3):
        x0 = ox + k * 150
        pts += [(x0, oy), (x0, oy - 40), (x0 + 75, oy - 40), (x0 + 75, oy), (x0 + 150, oy)]
    s += _poly(pts, BLUE, 2.4)
    # вихід — заокруглений
    s += text(120, 230, "вихід фототранзистора (затягнутий):", 11, INK, "start", "bold")
    oy2 = 300
    pts2 = []
    for j in range(0, 451):
        x = ox + j
        ph = (j % 150) / 150.0
        kbit = (j // 150)
        # цільовий рівень
        hi = 40
        if ph < 0.5:
            v = hi * (1 - math.exp(-ph / 0.12))
        else:
            v = hi * math.exp(-(ph - 0.5) / 0.12)
        pts2.append((x, oy2 - v))
    s += _poly(pts2, RED, 2.6)
    s += text(620, 150, "типово:", 11, INK, "start", "bold")
    s += text(620, 170, "одиниці–", 10.5, INK, "start")
    s += text(620, 186, "десятки кГц", 10.5, INK, "start", "bold")
    s += text(620, 286, "швидкі:", 11, GREEN, "start", "bold")
    s += text(620, 306, "логічний вихід,", 10, "#1f6e33", "start")
    s += text(620, 322, "фотодіод+підсил.", 10, "#1f6e33", "start")
    save("fig-10-10-5-speed.svg", s)


def fig5a10_6_family():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Сім'я розв'язки: світлом, полем, ємністю", 17.5, INK, "middle", "bold")
    cards = [
        (40, "оптопара", ["світлодіод →", "фотоприймач", "(ця тема)"], LGRN, GREEN),
        (250, "трансформатор", ["магнітне поле", "(§2.2.6)", "лише для змінного"], LBLUE, BLUE),
        (460, "ємнісна / RF", ["сигнал крізь", "малу ємність", "цифрові ізолятори"], "#f6f0e6", COPP),
        (670, "де треба", ["мережа↔логіка,", "USB↔прилад,", "медицина, ПЛК"], "#f4eef6", "#7a4e8a"),
    ]
    for x, title, lines, fill, bc in cards:
        s += rect(x, 80, 170, 170, fill, bc, 1.8, 10)
        s += text(x + 85, 108, title, 12.5, INK, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(x + 85, 140 + k * 24, ln, 10.5, INK, "middle")
    s += text(W / 2, H - 14, "Спільна ідея — передати сигнал, не передаючи струму. Оптопара робить це світлом і живе в мільярдах пристроїв.",
              11, GREY, "middle", style="italic")
    save("fig-10-10-6-family.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.5.8 — Сімейства діодів (Рис. 2.5.8c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig8c1_workhorses():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 28, "Три робочі конячки, які варто знати напам'ять", 17.5, INK, "middle", "bold")
    cards = [
        (30, "1N4148", "сигнальний / швидкий", LBLUE, BLUE,
         ["100 В · ~200 мА", "відновлення ~4 нс", "логіка, перемикання,", "малі сигнали, «АБО»"]),
        (310, "1N400x", "випрямний 1 А", LRED, RED,
         ["1 А · 50…1000 В", "повільний (мережа 50 Гц)", "x = напруга:", "4001=50В … 4007=1000В"]),
        (590, "1N581x", "Шотткі 1 А", LGRN, GREEN,
         ["падіння ~0.4 В", "5817=20В · 5819=40В", "імпульсні БЖ,", "сонячні панелі, ВЧ"]),
    ]
    for x, name, role, fill, bc, lines in cards:
        s += rect(x, 60, 250, 310, fill, bc, 2, 12)
        s += text(x + 125, 92, name, 18, INK, "middle", "bold")
        s += text(x + 125, 114, role, 11.5, bc, "middle", "bold")
        s += line(x + 20, 128, x + 230, 128, "#cccccc", 1)
        for k, ln in enumerate(lines):
            s += text(x + 125, 158 + k * 30, ln, 11.5, INK, "middle")
    s += text(W / 2, H - 14, "Менш потужні — 1N5400 (3 А випрямний), 1N5822 (Шотткі 3 А); для SMD — SS14/SS34, BAT54.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-8c-1-workhorses.svg", s)


def fig8c2_marking():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 28, "Як читати: смужка — катод; корпус — натяк на струм", 16.5, INK, "middle", "bold")
    # ── вивідний DO-41 зі смужкою ──
    s += _frame(40, 60, 380, 300, "вивідний (THT)")
    y = 130
    s += line(90, y, 150, y, INK, 2.5)
    s += rect(150, y - 16, 90, 32, "#3a3a3a", INK, 1.6, 5)
    s += line(228, y - 16, 228, y + 16, "#dddddd", 4)   # смужка-катод
    s += line(240, y, 300, y, INK, 2.5)
    s += text(195, y - 26, "1N4007", 11, "#dddddd", "middle", "bold")
    s += text(140, y + 34, "анод", 10, INK, "middle")
    s += text(255, y + 34, "катод (смужка!)", 10, BLUE, "middle", "bold")
    s += arrow(228, y + 44, 228, y + 22, BLUE, 1.6)
    s += text(230, 250, "корпуси за струмом:", 11, INK, "start", "bold")
    s += text(230, 274, "DO-35 (скло) — сигнальні 1N4148", 10, GREY, "start")
    s += text(230, 296, "DO-41 — 1 А (1N400x, 1N581x)", 10, GREY, "start")
    s += text(230, 318, "DO-201 / металеві — десятки А", 10, GREY, "start")
    s += text(230, 340, "смужка завжди = катод", 10, BLUE, "start", "bold")
    # ── SMD ──
    s += _frame(450, 60, 370, 300, "поверхневий (SMD)")
    s += rect(540, 110, 100, 44, "#3a3a3a", INK, 1.6, 4)
    s += line(632, 110, 632, 154, "#dddddd", 5)
    s += text(580, 138, "S4", 12, "#dddddd", "middle", "bold")
    s += text(590, 96, "смужка — катод", 9.5, BLUE, "middle", "bold")
    s += text(635, 168, "SS14", 10, INK, "middle", "bold")
    s += text(635, 100, "", 9, GREY, "middle")
    s += text(635, 200, "коди дрібні:", 10.5, INK, "middle", "bold")
    rows = ("SS14 — Шотткі 40 В 1 А (SMA)", "BAT54 — Шотткі 30 В (SOT-23)",
            "1N4148 → SOD-123 теж є", "корпус: SOD-123 < SMA < SMB < SMC")
    for k, r in enumerate(rows):
        s += text(635, 226 + k * 26, r, 9.5, GREY, "middle")
    s += text(W / 2, H - 10, "Два головні числа в даташиті (§2.5.5): прямий струм I_F і зворотна напруга V_R — обидва з запасом.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-8c-2-marking.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.5.10 — Оптопара PC817-класу (Рис. 2.5.10c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig10c1_pc817_calc():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 28, "PC817 у цифровому ключі: рахуємо обидва боки в числах", 16.5, INK, "middle", "bold")
    # ── корпус DIP-4 ──
    bx, by = 70, 90
    s += rect(bx, by, 150, 130, "#2b2b2b", INK, 2, 8)
    s += circle(bx + 16, by + 16, 5, "none", "#aaa", 1.4)  # крапка вивід 1
    s += text(bx + 75, by + 60, "PC817", 14, "#dddddd", "middle", "bold")
    s += text(bx + 75, by + 80, "DIP-4", 10, "#aaaaaa", "middle")
    for k, lab in ((0, "1 анод"), (1, "2 катод")):
        s += line(bx, by + 35 + k * 50, bx - 26, by + 35 + k * 50, INK, 2)
        s += text(bx - 30, by + 39 + k * 50, lab, 9, RED if k == 0 else BLUE, "end", "bold")
    for k, lab in ((0, "колектор 4"), (1, "емітер 3")):
        s += line(bx + 150, by + 35 + k * 50, bx + 176, by + 35 + k * 50, INK, 2)
        s += text(bx + 180, by + 39 + k * 50, lab, 9, INK, "start", "bold")
    s += text(bx + 75, by + 150, "крапка/зріз = вивід 1 (анод)", 9, GREY, "middle", style="italic")
    # ── розрахунок вхід ──
    s += _frame(300, 70, 250, 320, "ВХІД (світлодіод)")
    s += text(425, 96, "сигнал 3.3 В → засвітити LED", 9.5, INK, "middle")
    s += text(425, 124, "U_F ≈ 1.2 В, хочемо I_F = 10 мА", 10, INK, "middle")
    s += text(425, 156, "R1 = (3.3 − 1.2)/10мА", 11.5, GREEN, "middle", "bold")
    s += text(425, 176, "≈ 210 Ом → беремо 220 Ом", 11.5, GREEN, "middle", "bold")
    s += text(425, 212, "(той самий обмежувач, що", 9, GREY, "middle")
    s += text(425, 228, "у звичайного LED, §2.5.7)", 9, GREY, "middle")
    s += text(425, 268, "запас: реальний I_F беруть", 9.5, "#9c6a16", "middle")
    s += text(425, 284, "БІЛЬШИМ, ніж теоретично треба", 9.5, "#9c6a16", "middle")
    s += text(425, 300, "— бо CTR падає з роками", 9.5, "#9c6a16", "middle")
    # ── розрахунок вихід ──
    s += _frame(580, 70, 250, 320, "ВИХІД (фототранзистор)")
    s += text(705, 96, "треба насичення (повне «вкл»)", 9.5, INK, "middle")
    s += text(705, 124, "CTR_min = 80% (ранг A)", 10, INK, "middle")
    s += text(705, 144, "I_C(дост.) ≈ 0.8·10мА = 8 мА", 10.5, RED, "middle", "bold")
    s += text(705, 176, "R_C при вих. 5 В:", 10, INK, "middle")
    s += text(705, 196, "R_C > 5В/8мА ≈ 620 Ом", 11.5, GREEN, "middle", "bold")
    s += text(705, 216, "→ беремо 1 кОм (з запасом)", 11, GREEN, "middle", "bold")
    s += text(705, 252, "на R_C падає майже все →", 9.5, GREY, "middle")
    s += text(705, 268, "транзистор насичений → чіткий", 9.5, GREY, "middle")
    s += text(705, 284, "логічний 0 на виході", 9.5, GREY, "middle")
    s += text(705, 320, "інверсія: LED горить → вихід 0", 9.5, "#7a4e8a", "middle", "bold")
    s += text(W / 2, H - 10, "Два боки рахують ОКРЕМО (різні землі!): вхід — як LED, вихід — як ключ-транзистор у насиченні.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-10c-1-pc817-calc.svg", s)


def fig10c2_ranks_family():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 28, "Ранги CTR, сімейство й швидкі родичі", 17, INK, "middle", "bold")
    # ── ранги CTR ──
    s += _frame(40, 56, 380, 180, "ранг CTR — літера в назві")
    rows = (("PC817A", "80…160 %", GREEN), ("PC817B", "130…260 %", COPP),
            ("PC817C", "200…400 %", BLUE), ("PC817D", "300…600 %", "#7a4e8a"))
    for i, (n, r, c) in enumerate(rows):
        yy = 92 + i * 32
        s += text(70, yy, n, 12, c, "start", "bold")
        s += text(200, yy, r, 11.5, INK, "start")
        s += rect(300, yy - 12, min(int(r.split("…")[1].rstrip(" %")) / 6, 100), 14, c, "none", 0)
    s += text(230, 224, "без літери — увесь діапазон 50…600 %", 9, GREY, "middle", style="italic")
    # ── сімейство ──
    s += _frame(440, 56, 380, 180, "скільки каналів у корпусі")
    fam = (("PC817", "1 канал"), ("PC827", "2 канали"), ("PC847", "4 канали"))
    for i, (n, c) in enumerate(fam):
        x = 470 + i * 120
        s += rect(x, 96, 90, 70, LGRN, GREEN, 1.6, 8)
        s += text(x + 45, 126, n, 12, INK, "middle", "bold")
        s += text(x + 45, 148, c, 10, GREY, "middle")
    s += text(630, 220, "однакова комірка, більше пар в одному корпусі", 9, GREY, "middle", style="italic")
    # ── швидкість ──
    s += _frame(40, 256, 780, 120, "коли фототранзистора замало — швидкі цифрові")
    s += text(430, 284, "PC817-клас: смуга ~80 кГц (фототранзистор повільний, §2.5.10)", 11, INK, "middle")
    s += text(430, 312, "потрібні сотні кБіт/Мбіт → 6N137 / TLP-клас:", 11, "#1f6e33", "middle", "bold")
    s += text(430, 332, "усередині фотодіод + підсилювач-формувач, логічний вихід, мегагерци", 10, GREY, "middle")
    s += text(430, 358, "для зв'язку (ізольований UART/SPI) беруть саме їх, а не PC817", 9.5, GREY, "middle", style="italic")
    save("fig-10-10c-2-ranks-family.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.5.8 — TVS-діоди (Рис. 2.5.8c.3–4)
# ═════════════════════════════════════════════════════════════════════════════
def fig8c3_tvs_action():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 28, "TVS на вході: відвести удар повз чутливе коло", 17, INK, "middle", "bold")
    # схема
    y = 110
    s += circle(70, y, 6, INK, INK, 0)
    s += text(70, y - 18, "роз'єм", 10.5, INK, "middle", "bold")
    s += line(76, y, 200, y, INK, 2.4)
    s += circle(200, y, 4, INK, INK, 0)
    # TVS до землі (символ — двонапрямлений Зенер, тут однонапр.)
    s += line(200, y, 200, y + 36, INK, 2)
    # символ Зенера (загнуті кінці катода)
    s += f'<path d="M 186,{y+58} L 214,{y+58} L 200,{y+38} Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.6"/>\n'
    s += line(186, y + 58, 214, y + 58, INK, 2.4)
    s += line(186, y + 58, 182, y + 64, INK, 2.2) + line(214, y + 58, 218, y + 52, INK, 2.2)
    s += text(228, y + 52, "TVS", 11, RED, "start", "bold")
    s += line(200, y + 58, 200, y + 92, INK, 2)
    s += line(176, y + 92, 224, y + 92, INK, 2.4)  # земля
    s += line(184, y + 99, 216, y + 99, INK, 1.8) + line(192, y + 105, 208, y + 105, INK, 1.4)
    s += line(200, y, 330, y, INK, 2.4)
    s += rect(330, y - 28, 120, 56, "#eef6ef", GREEN, 1.8, 8)
    s += text(390, y - 2, "чутливе", 11.5, "#1f6e33", "middle", "bold")
    s += text(390, y + 16, "коло (MCU)", 10, "#1f6e33", "middle")
    s += arrow(150, y - 40, 196, y - 4, "#9c6a16", 1.8)
    s += text(150, y - 46, "удар ESD / викид", 10.5, "#9c6a16", "middle", "bold")
    # осцилограма до/після
    ox, oy, w = 510, 250, 320
    s += _frame(490, 150, 360, 230, "")
    s += line(ox, oy, ox + w, oy, INK, 1.4)
    s += line(ox, oy, ox, oy - 120, INK, 1.4) + text(ox - 6, oy - 124, "U", 10, INK, "middle", "bold")
    # вхідний сплеск (висока голка)
    s += _poly([(ox, oy - 10), (ox + 90, oy - 10), (ox + 100, oy - 110), (ox + 108, oy - 10), (ox + w, oy - 10)], "#bbbbbb", 1.6, dash="4,3")
    s += text(ox + 130, oy - 100, "без TVS: голка кВ", 9.5, GREY, "start")
    # затиснутий рівень
    s += line(ox, oy - 40, ox + w, oy - 40, RED, 1.4, dash="5,4")
    s += text(ox + w - 4, oy - 46, "V_CL (затискання)", 9.5, RED, "end", "bold")
    s += _poly([(ox, oy - 10), (ox + 90, oy - 10), (ox + 96, oy - 40), (ox + 110, oy - 40), (ox + 116, oy - 10), (ox + w, oy - 10)], GREEN, 2.6)
    s += text(ox + 150, oy - 26, "з TVS: зрізано до безпечного", 9.5, "#1f6e33", "start", "bold")
    s += text(W / 2, H - 12, "У нормі TVS мовчить (зворотно). Перенапруга — миттєво пробивається й зливає удар у землю.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-8c-3-tvs-action.svg", s)


def fig8c4_tvs_params():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 28, "TVS ≠ Зенер: інша роль, інші числа", 17, INK, "middle", "bold")
    # ── ВАХ із параметрами ──
    ox, oy, w, h = 70, 250, 320, 200
    s += _frame(50, 56, 380, 320, "зворотна гілка TVS")
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w, oy + 16, "U", 10, INK, "middle", "bold")
    s += line(ox, oy, ox, oy - h, INK, 1.4) + text(ox - 6, oy - h - 4, "I", 10, INK, "middle", "bold")
    pts = []
    for j in range(0, 201):
        x = j / 200.0
        U = x
        I = 0.02 * math.exp((U - 0.55) * 12) + (1.6 * (U - 0.78) if U > 0.78 else 0)
        pts.append((ox + U * w, oy - min(I, 1.0) * h))
    s += _poly(pts, RED, 2.6)
    for U, lab, col in ((0.45, "V_WM", GREEN), (0.62, "V_BR", COPP), (0.86, "V_CL", RED)):
        s += line(ox + U * w, oy, ox + U * w, oy - h, FAINT, 1)
        s += text(ox + U * w, oy + 16, lab, 10, col, "middle", "bold")
    s += text(ox + 0.16 * w, oy - 0.7 * h, "тут\nмовчить", 9, GREEN, "middle")
    s += text(ox + 0.45 * w, oy - 14, "робоча", 8.5, GREEN, "middle")
    s += text(ox + 0.62 * w, oy - 14, "пробій", 8.5, COPP, "middle")
    s += text(ox + 0.86 * w, oy - 14, "затиск", 8.5, RED, "middle")
    # ── порівняння + типи ──
    s += _frame(460, 56, 360, 150, "TVS проти Зенера")
    s += text(640, 84, "Зенер: тримає напругу довго,", 10.5, INK, "middle")
    s += text(640, 102, "малий струм (стабілізатор)", 10.5, INK, "middle")
    s += text(640, 128, "TVS: коротко гасить ПОТУЖНИЙ удар", 10.5, RED, "middle", "bold")
    s += text(640, 146, "(кіловати на мікросекунди, мала ємність)", 9.5, GREY, "middle")
    s += text(640, 176, "паспорт: P_PPM 400/600 Вт, V_WM, V_CL", 10, INK, "middle", "bold")
    s += _frame(460, 226, 360, 150, "однонапрямлений / двонапрямлений")
    s += text(640, 254, "однонапр. — для DC-ліній (катод до +)", 10, INK, "middle")
    s += text(640, 276, "двонапр. — для знакозмінних / сигнальних", 10, INK, "middle")
    s += text(640, 304, "+ послідовний опір/запобіжник: TVS гасить", 10, "#9c6a16", "middle", "bold")
    s += text(640, 322, "КОРОТКЕ; тривале мусить рвати запобіжник", 9.5, "#9c6a16", "middle")
    s += text(640, 350, "для USB/HDMI — НИЗЬКОЄМНІСНІ TVS", 10, "#1f6e33", "middle", "bold")
    save("fig-10-8c-4-tvs-params.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  ⚙️ Вставка до §2.5.7 — Charlieplexing (Рис. 2.5.7a.k)
# ═════════════════════════════════════════════════════════════════════════════
def _led_arrow(x1, y1, x2, y2, col, lit=False):
    """Маленький LED уздовж відрізка, вістрям до (x2,y2)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    sz = 8
    wire = GREEN if lit else "#aab0b6"
    s = line(x1, y1, mx - ux * sz, my - uy * sz, wire, 3 if lit else 1.6)
    s += line(mx + ux * sz, my + uy * sz, x2, y2, wire, 3 if lit else 1.6)
    fill = "#ffe9a0" if lit else "#dfe7f0"
    b1 = (mx - ux * sz + px * sz, my - uy * sz + py * sz)
    b2 = (mx - ux * sz - px * sz, my - uy * sz - py * sz)
    tip = (mx + ux * sz, my + uy * sz)
    s += f'<path d="M {b1[0]:.1f},{b1[1]:.1f} L {b2[0]:.1f},{b2[1]:.1f} L {tip[0]:.1f},{tip[1]:.1f} Z" fill="{fill}" stroke="{INK}" stroke-width="1.3"/>\n'
    s += line(tip[0] + px * sz, tip[1] + py * sz, tip[0] - px * sz, tip[1] - py * sz, INK, 2.2)
    if lit:
        s += arrow(mx + px * 6, my + py * 6, mx + px * 18, my + py * 18, SUN, 1.5)
    return s


def fig7a1_principle():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 28, "Charlieplexing: 3 ніжки → 6 світлодіодів", 17.5, INK, "middle", "bold")
    s += text(W / 2, 50, "секрети: LED світить в один бік (§2.5.7) + ніжка має ТРИ стани (HIGH / LOW / Hi-Z)",
              11.5, GREY, "middle", style="italic")
    # три вузли трикутником
    A = (180, 120); B = (120, 320); C = (440, 250)
    nodes = (("A", A, "HIGH (+)", RED), ("B", B, "LOW (0)", BLUE), ("C", C, "Hi-Z (відкл.)", GREY))
    # пари антипаралельних LED: між кожними двома вузлами — двоє LED
    def pair(P, Q, lit_pq):
        # зміщення, щоб дві стрілки не злилися
        dx, dy = Q[0] - P[0], Q[1] - P[1]
        L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; px, py = -uy, ux
        o = 9
        s2 = _led_arrow(P[0] + px * o, P[1] + py * o, Q[0] + px * o, Q[1] + py * o, INK, lit_pq)   # P→Q
        s2 += _led_arrow(Q[0] - px * o, Q[1] - py * o, P[0] - px * o, P[1] - py * o, INK, False)    # Q→P
        return s2
    s += pair(A, B, True)    # A→B світиться
    s += pair(B, C, False)
    s += pair(A, C, False)
    for lab, P, st, col in nodes:
        s += circle(P[0], P[1], 16, "#ffffff", col, 2.4)
        s += text(P[0], P[1] + 5, lab, 14, col, "middle", "bold")
        s += text(P[0], P[1] - 24, st, 10.5, col, "middle", "bold")
    s += text(300, 150, "горить лише LED A→B", 11, "#1f6e33", "start", "bold")
    s += text(300, 168, "(A штовхає, B приймає)", 9.5, GREY, "start")
    # пояснення праворуч
    s += _frame(560, 70, 280, 330, "що з рештою")
    s += text(700, 100, "A→B: відкритий, СВІТИТЬ", 10.5, "#1f6e33", "middle", "bold")
    s += text(700, 128, "B→A (антипаралельний):", 10, INK, "middle")
    s += text(700, 144, "зворотно зміщений — мовчить", 9.5, GREY, "middle")
    s += text(700, 174, "усі LED до ніжки C:", 10, INK, "middle")
    s += text(700, 190, "C у Hi-Z — шляху нема, темні", 9.5, GREY, "middle")
    s += line(580, 214, 820, 214, "#ddd", 1)
    s += text(700, 238, "щоб засвітити інший LED —", 10, INK, "middle")
    s += text(700, 254, "інша трійка станів ніжок", 10, INK, "middle")
    s += text(700, 282, "одночасно світить ОДИН", 10.5, "#9c6a16", "middle", "bold")
    s += text(700, 298, "(або один — швидка розгортка)", 9.5, GREY, "middle")
    s += text(700, 330, "обмежувальні резистори —", 9.5, GREY, "middle")
    s += text(700, 346, "обов'язкові (на ніжку чи в плече)", 9.5, GREY, "middle")
    s += text(700, 376, "ідея — Чарлі Аллен, Maxim, ~1995", 9, GREY, "middle", style="italic")
    save("fig-10-7a-1-principle.svg", s)


def fig7a2_scale():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 28, "Чому n·(n−1): кожна впорядкована пара ніжок — свій LED", 16.5, INK, "middle", "bold")
    # таблиця
    s += _frame(50, 60, 360, 250, "масштаб")
    s += text(110, 92, "ніжки n", 11, INK, "middle", "bold")
    s += text(250, 92, "LED = n·(n−1)", 11, INK, "middle", "bold")
    rows = ((2, 2), (3, 6), (4, 12), (5, 20), (8, 56), (12, 132))
    for i, (n, leds) in enumerate(rows):
        yy = 122 + i * 28
        s += text(110, yy, str(n), 12, BLUE, "middle", "bold")
        s += text(250, yy, str(leds), 12, RED, "middle", "bold")
    s += text(230, 300, "проти n виходів = n LED у «лоб»", 9.5, GREY, "middle", style="italic")
    # розгортка в часі
    s += _frame(440, 60, 400, 250, "як показати багато: розгортка в часі")
    ox, oy, w = 470, 200, 340
    s += line(ox, oy, ox + w, oy, INK, 1.3) + text(ox + w, oy + 16, "t", 10, INK, "start", "bold")
    for k in range(6):
        x = ox + 10 + k * 55
        s += rect(x, oy - 50, 14, 50, "#ffe9a0" if k % 1 == 0 else "#eee", INK, 1.2)
        s += text(x + 7, oy + 16, f"L{k+1}", 8.5, GREY, "middle")
    s += text(640, 120, "по одному, дуже швидко —", 10.5, INK, "middle", "bold")
    s += text(640, 138, "око зливає в суцільну картинку", 10, GREY, "middle")
    s += text(640, 250, "платня: кожен світить лише 1/N часу", 10, "#9c6a16", "middle", "bold")
    s += text(640, 268, "→ більший піковий струм для яскравості", 9.5, GREY, "middle")
    s += text(640, 290, "(той самий ШІМ-принцип, що в §2.5.7)", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 16, "Так десяток ніжок керує сотнею світлодіодів — годинники, брелоки, LED-кільця там, де ніжок обмаль.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-7a-2-scale.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.5.7 — Світлодіоди на практиці (Рис. 2.5.7c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig7c1_rgb_white():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 28, "Білий і RGB: два способи дістати «не моноколір»", 17, INK, "middle", "bold")
    # ── ліворуч: білий = синій + люмінофор ──
    s += _frame(40, 60, 360, 300, "білий світлодіод")
    s += rect(90, 120, 120, 90, "#1f47b5", INK, 1.6, 8)
    s += text(150, 170, "синій", 12, "#ffffff", "middle", "bold")
    s += text(150, 188, "кристал GaN", 9.5, "#cdd8f5", "middle")
    s += rect(90, 110, 120, 14, "#e7c64a", "#9c6a16", 1.2, 4)
    s += text(150, 102, "шар люмінофора (жовтий)", 9, "#7a5510", "middle")
    s += _photon(150, 110, 150, 78, SUN, 3, 2)
    s += text(150, 64, "= біле світло", 11, INK, "middle", "bold")
    # шкала колірної температури
    s += text(220, 250, "колірна температура:", 10.5, INK, "start", "bold")
    grad = [("#ffd9a0", "теплий 2700K"), ("#fff2dd", "нейтр. 4000K"), ("#dceaff", "холодн. 6500K")]
    for i, (c, lab) in enumerate(grad):
        s += rect(70 + i * 100, 270, 90, 26, c, "#999", 1)
        s += text(115 + i * 100, 287, lab.split()[0], 9, INK, "middle", "bold")
        s += text(115 + i * 100, 314, lab.split()[1], 8.5, GREY, "middle")
    s += text(220, 344, "CRI — наскільки чесно передає кольори", 9, GREY, "start", style="italic")
    # ── праворуч: RGB = три кристали ──
    s += _frame(440, 60, 360, 300, "RGB світлодіод")
    for i, (c, lab) in enumerate((("#c0271e", "R"), ("#1f8a3b", "G"), ("#1f47b5", "B"))):
        s += rect(490 + i * 80, 110, 56, 56, c, INK, 1.4, 6)
        s += text(518 + i * 80, 144, lab, 16, "#ffffff", "middle", "bold")
    s += text(620, 190, "3 кристали в одному корпусі", 10, GREY, "middle")
    s += text(620, 208, "(спільний анод або катод)", 9.5, GREY, "middle")
    s += text(620, 240, "ШІМ кожного → будь-який колір", 10.5, INK, "middle", "bold")
    s += text(620, 268, "адресовані (WS2812-клас):", 10, "#7a4e8a", "middle", "bold")
    s += text(620, 286, "драйвер усередині, один", 9.5, "#7a4e8a", "middle")
    s += text(620, 302, "провід даних на ланцюг", 9.5, "#7a4e8a", "middle")
    s += text(620, 340, "змішування в оці, а не в світлі", 9, GREY, "middle", style="italic")
    save("fig-10-7c-1-rgb-white.svg", s)


def fig7c2_resistor_vs_driver():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Резистор чи драйвер струму: чим яскравіший LED, тим важливіше", 16, INK, "middle", "bold")
    # ── ліворуч: резистор ──
    s += _frame(40, 56, 360, 300, "резистор-обмежувач (просто й дешево)")
    y = 130
    s += line(80, y, 120, y, INK, 2) + text(70, y, "+", 12, RED, "end", "bold")
    s += rect(120, y - 9, 50, 18, "#fff", INK, 1.5) + text(145, y - 16, "R", 10, INK, "middle", "bold")
    s += line(170, y, 210, y, INK, 2)
    s += _diode_h(225, y, 11, True, RED)
    s += arrow(229, y - 14, 237, y - 26, SUN, 1.5)
    s += line(240, y, 280, y, INK, 2) + text(290, y, "−", 12, BLUE, "end", "bold")
    s += text(220, 200, "+ копійка, годиться для індикаторів", 10, "#1f6e33", "middle")
    s += text(220, 224, "− марнує енергію на R", 10, "#9c6a16", "middle")
    s += text(220, 248, "− струм пливе: U_F падає з нагрівом", 10, "#9c6a16", "middle")
    s += text(220, 268, "   (−2 мВ/°C, §2.5.5) → струм росте", 9, GREY, "middle")
    s += text(220, 300, "робочий струм беруть НЕ максимальний:", 10, INK, "middle", "bold")
    s += text(220, 320, "індикатор 2–10 мА, не «20 мА бо можна»", 9.5, GREY, "middle")
    # ── праворуч: драйвер струму ──
    s += _frame(440, 56, 360, 300, "стабілізатор струму (драйвер)")
    s += rect(560, 110, 120, 56, "#eef6ef", GREEN, 1.8, 8)
    s += text(620, 134, "тримає I", 12, "#1f6e33", "middle", "bold")
    s += text(620, 152, "сталим", 11, "#1f6e33", "middle")
    s += line(560, 138, 520, 138, INK, 2) + text(512, 138, "+", 12, RED, "end", "bold")
    s += line(680, 138, 700, 138, INK, 2) + line(700, 138, 700, 180, INK, 2)
    s += _diode_h(700, 195, 10, False, RED)
    s += arrow(690, 188, 682, 176, SUN, 1.4)
    s += line(700, 210, 700, 240, INK, 2) + text(700, 256, "LED", 9.5, INK, "middle", "bold")
    s += text(620, 290, "+ та сама яскравість при будь-якій", 10, "#1f6e33", "middle")
    s += text(620, 308, "   напрузі й температурі", 10, "#1f6e33", "middle")
    s += text(620, 330, "потрібен потужним LED і освітленню", 10, INK, "middle", "bold")
    save("fig-10-7c-2-resistor-vs-driver.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.5.6 — Діодний міст як компонент (Рис. 2.5.6c.k)
# ═════════════════════════════════════════════════════════════════════════════
def _diode_diag(x1, y1, x2, y2, col=INK):
    """Діод уздовж відрізка, вістрям до (x2,y2)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    sz = 9
    b1 = (mx - ux * sz + px * sz, my - uy * sz + py * sz)
    b2 = (mx - ux * sz - px * sz, my - uy * sz - py * sz)
    tip = (mx + ux * sz, my + uy * sz)
    s = line(x1, y1, x2, y2, col, 1.6)
    s += f'<path d="M {b1[0]:.1f},{b1[1]:.1f} L {b2[0]:.1f},{b2[1]:.1f} L {tip[0]:.1f},{tip[1]:.1f} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.4"/>\n'
    s += line(tip[0] + px * sz, tip[1] + py * sz, tip[0] - px * sz, tip[1] - py * sz, col, 2.2)
    return s


def fig6c1_bridge_pkg():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 28, "Чотири діоди в одному корпусі: міст як готова деталь", 17, INK, "middle", "bold")
    # ── ромб усередині ──
    cx, cy, r = 230, 200, 80
    top = (cx, cy - r); bot = (cx, cy + r); lft = (cx - r, cy); rgt = (cx + r, cy)
    # вузли: лівий і правий — AC; верх — +, низ — −
    s += _diode_diag(lft[0], lft[1], top[0], top[1])   # лівий-AC → +
    s += _diode_diag(bot[0], bot[1], lft[0], lft[1])   # − → лівий-AC
    s += _diode_diag(rgt[0], rgt[1], top[0], top[1])   # правий-AC → +
    s += _diode_diag(bot[0], bot[1], rgt[0], rgt[1])   # − → правий-AC
    for (px, py) in (top, bot, lft, rgt):
        s += circle(px, py, 3.5, INK, INK)
    s += text(top[0], top[1] - 12, "+", 16, RED, "middle", "bold")
    s += text(bot[0], bot[1] + 22, "−", 16, BLUE, "middle", "bold")
    s += text(lft[0] - 16, lft[1] + 5, "~", 18, INK, "middle", "bold")
    s += text(rgt[0] + 14, rgt[1] + 5, "~", 18, INK, "middle", "bold")
    s += text(cx, cy + r + 56, "усередині — звичний ромб із §2.5.6", 10, GREY, "middle", style="italic")
    # ── корпус праворуч ──
    bx, by = 480, 110
    s += rect(bx, by, 150, 150, "#2b2b2b", INK, 2, 12)
    s += text(bx + 75, by + 60, "BRIDGE", 13, "#dddddd", "middle", "bold")
    s += text(bx + 75, by + 82, "KBP / GBU /", 10, "#bbbbbb", "middle")
    s += text(bx + 75, by + 98, "DB / KBPC…", 10, "#bbbbbb", "middle")
    s += circle(bx + 18, by + 18, 6, "none", "#888", 1.6)  # отвір під гвинт
    for k, lab, col in ((0, "~", INK), (1, "+", RED), (2, "~", INK), (3, "−", BLUE)):
        lx = bx + 20 + k * 37
        s += line(lx, by + 150, lx, by + 178, INK, 2)
        s += text(lx, by + 196, lab, 13, col, "middle", "bold")
    s += text(bx + 75, by + 230, "4 виводи: ~ ~ + −", 10.5, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Маркування на корпусі: дві ~ — до джерела змінного, + і − — до згладжувального конденсатора.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-6c-1-bridge-pkg.svg", s)


def fig6c2_drop_heat():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Ціна зручності: завжди ДВА діоди в дорозі", 17, INK, "middle", "bold")
    cx, cy, r = 180, 180, 70
    top = (cx, cy - r); bot = (cx, cy + r); lft = (cx - r, cy); rgt = (cx + r, cy)
    # підсвітити активну пару (напр. лівий-AC → + та − → правий-AC)
    s += line(lft[0], lft[1], top[0], top[1], GREEN, 5)
    s += line(bot[0], bot[1], rgt[0], rgt[1], GREEN, 5)
    s += _diode_diag(lft[0], lft[1], top[0], top[1])
    s += _diode_diag(bot[0], bot[1], lft[0], lft[1])
    s += _diode_diag(rgt[0], rgt[1], top[0], top[1])
    s += _diode_diag(bot[0], bot[1], rgt[0], rgt[1])
    for (px, py) in (top, bot, lft, rgt):
        s += circle(px, py, 3.2, INK, INK)
    s += text(top[0], top[1] - 10, "+", 14, RED, "middle", "bold")
    s += text(bot[0], bot[1] + 20, "−", 14, BLUE, "middle", "bold")
    s += text(cx, cy + r + 40, "зелене — шлях струму цієї півхвилі", 9.5, "#1f6e33", "middle", style="italic")
    # формули
    bx = 400
    s += _frame(bx, 70, 400, 110, "")
    s += text(bx + 200, 98, "падіння: 2 × U_F ≈ 1.4 В (Si)", 12.5, RED, "middle", "bold")
    s += text(bx + 200, 124, "Шотткі-міст (§2.5.8): ≈ 0.6 В", 11, "#1f6e33", "middle")
    s += text(bx + 200, 150, "тепло: P ≈ 2·U_F·I_сер  (§1.3.5)", 12, "#9c6a16", "middle", "bold")
    # приклад тепла
    s += _frame(bx, 200, 400, 150, "приклад: I_сер = 2 А")
    s += text(bx + 200, 228, "P ≈ 1.4 В · 2 А ≈ 2.8 Вт тепла", 12.5, INK, "middle", "bold")
    s += text(bx + 200, 254, "→ міст помітно гріється,", 11, GREY, "middle")
    s += text(bx + 200, 272, "корпус KBPC/GBPC — на радіатор", 11, GREY, "middle")
    s += text(bx + 200, 300, "+ кидок при ввімкненні: розряджений", 10.5, "#9c6a16", "middle")
    s += text(bx + 200, 318, "конденсатор = коротке → пік I_FSM", 10.5, "#9c6a16", "middle")
    s += text(W / 2, H - 10, "Два діоди замість одного: удвічі більша втрата напруги й удвічі більше тепла, ніж у однопівперіодного.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-6c-2-drop-heat.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  📜 Історія до §2.5.7 — Блакитний світлодіод (Рис. 2.5.7i.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig7i1_timeline():
    W, H = 920, 270
    s = header(W, H)
    s += text(W / 2, 32, "Тридцять років до синього — і світло змінилося", 18, INK, "middle", "bold")
    boxes = [
        ("1960-ті", ["червоний і зелений", "світлодіоди готові", "(§2.5.7)"], "#fbfbfb"),
        ("1960–80-ті", ["синій НЕ дається:", "GaN не вміють ні", "вирощувати, ні легувати"], "#fbeeee"),
        ("1986 · Нагоя", ["Акасакі й Амано:", "якісний GaN", "на сапфірі"], LGRN),
        ("1989 · Нагоя", ["вони ж: p-тип GaN", "(магній + промінь)", "— остання цеглина"], LGRN),
        ("1993–94 · Nichia", ["Накамура: ЯСКРАВИЙ", "синій на InGaN —", "у виробництво"], LBLUE),
        ("2014", ["Нобель з фізики", "трьом — за світло,", "що змінило побут"], "#f4eef6"),
    ]
    bw, gap, by, bh = 138, 14, 88, 116
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 14 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 10.5, INK, "middle", "bold")
        s += rect(bx, by, bw, bh, fill, "#c9d3dc", 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 32 + k * 21, ln, 10, INK, "middle")
        if i < len(boxes) - 1:
            ax = bx + bw
            s += arrow(ax + 1, by + bh / 2, ax + gap - 1, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Червоний світив із 1960-х; на синій — найенергійніший видимий фотон — пішло ще тридцять років.",
              11, GREY, "middle", style="italic")
    save("fig-10-7i-6-blue-timeline.svg", s)


def fig7i2_why_hard():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чому синій був такий важкий — і навіщо він потрібен", 17.5, INK, "middle", "bold")
    # дві перешкоди
    s += _frame(40, 60, 360, 180, "дві стіни на шляху GaN")
    s += text(220, 88, "1. Виростити якісний кристал GaN", 11, INK, "middle", "bold")
    s += text(220, 108, "— ґратка не сідала рівно на підкладку", 9.5, GREY, "middle")
    s += text(220, 124, "(розв'язок: буферний шар на сапфірі)", 9.5, "#1f6e33", "middle")
    s += line(70, 142, 370, 142, "#ddd", 1)
    s += text(220, 166, "2. Зробити p-тип GaN (дірки)", 11, INK, "middle", "bold")
    s += text(220, 186, "— легований магнієм GaN не провадив", 9.5, GREY, "middle")
    s += text(220, 202, "(розв'язок: промінь / відпал активує Mg)", 9.5, "#1f6e33", "middle")
    s += text(220, 226, "обидві — у §2.5.2–2.5.3, лише для GaN", 9, GREY, "middle", style="italic")
    # навіщо синій → білий
    s += _frame(440, 60, 360, 180, "навіщо саме синій")
    s += rect(490, 110, 70, 60, "#1f47b5", INK, 1.6, 6)
    s += text(525, 145, "синій", 10.5, "#fff", "middle", "bold")
    s += rect(490, 100, 70, 12, "#e7c64a", "#9c6a16", 1.2, 3)
    s += text(525, 92, "+ люмінофор", 9, "#7a5510", "middle")
    s += arrow(565, 140, 615, 140, GREEN, 2.2)
    s += circle(660, 140, 26, "#fffbe8", SUN, 2)
    s += text(660, 145, "БІЛЕ", 11, "#9c6a16", "middle", "bold")
    s += text(620, 196, "синій + жовтий люмінофор = біле світло", 9.5, GREY, "middle")
    s += text(620, 212, "(того самого трюку, що в §2.5.7)", 9, GREY, "middle", style="italic")
    s += text(W / 2, 280, "Без синього не зібрати білий: червоний і зелений були, а третьої — найенергійнішої — фарби бракувало.",
              11, INK, "middle", "bold")
    s += text(W / 2, 306, "саме тому Нобель відзначив не «ще один колір», а ключ до енергоощадного освітлення.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-7i-7-why-hard.svg", s)


def fig7i3_three():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Троє лауреатів: хто що зробив — чесно", 18, INK, "middle", "bold")
    cards = [
        (40, "Ісаму Акасакі", "Хіросі Амано", "Університет Нагої, Японія",
         ["заклали ФУНДАМЕНТ:", "• якісний кристал GaN (1986)", "• p-тип GaN (1989)", "— без цього синього не було б"], LGRN, GREEN),
        (430, "Сюдзі Накамура", "", "Nichia → США (UC Santa Barbara)",
         ["довів до ЯСКРАВОГО й СЕРІЇ:", "• InGaN-структури (1993–94)", "• промислова технологія", "• згодом — гучний суд із Nichia"], LBLUE, BLUE),
    ]
    for x, n1, n2, aff, lines, fill, bc in cards:
        s += rect(x, 60, 350, 220, fill, bc, 2, 12)
        s += text(x + 175, 90, n1, 14, INK, "middle", "bold")
        if n2:
            s += text(x + 175, 112, "+ " + n2, 13, INK, "middle", "bold")
        s += text(x + 175, 132 if n2 else 114, aff, 10, bc, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(x + 20, 158 + k * 24, ln, 10.5, INK, "start")
    s += text(W / 2, H - 14, "Нобель 2014 — усім трьом. Тема назвала лише Накамуру; справедливо згадати й піонерів із Нагої.",
              11, GREY, "middle", style="italic")
    save("fig-10-7i-8-three.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  📜 Історія до §2.5.1 — Кремній проти германію (Рис. 2.5.1i.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig1i1_timeline():
    W, H = 900, 260
    s = header(W, H)
    s += text(W / 2, 32, "Перегони матеріалів: германій стартував, кремній переміг", 18, INK, "middle", "bold")
    boxes = [
        ("1947 · Bell Labs", ["перший транзистор", "— ГЕРМАНІЙ", "(Бардін, Браттейн)"], LBLUE),
        ("поч. 1950-х", ["германій панує:", "легше очистити,", "але «тече» й гріється"], "#fbfbfb"),
        ("січ. 1954 · Bell", ["Танненбаум:", "Si у лабораторії —", "без продажу"], "#fbfbfb"),
        ("трав. 1954 · TI", ["Тіл: перший", "КОМЕРЦІЙНИЙ", "кремнієвий"], LGRN),
        ("1959 · Fairchild", ["оксид SiO₂ +", "планарний процес", "→ кремній назавжди"], LGRN),
    ]
    bw, gap, by, bh = 156, 18, 86, 110
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 16 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 11, INK, "middle", "bold")
        border = "#9bb0c2" if fill == LGRN else "#c9d3dc"
        s += rect(bx, by, bw, bh, fill, border, 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 32 + k * 21, ln, 11, INK, "middle")
        if i < len(boxes) - 1:
            ax = bx + bw
            s += arrow(ax + 2, by + bh / 2, ax + gap - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14, "Той самий PN-перехід — лише матеріал інший; саме матеріал і вирішив, на чому стоятиме вся електроніка.",
              11, GREY, "middle", style="italic")
    save("fig-10-1i-1-timeline.svg", s)


def fig1i2_ge_vs_si():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Германій проти кремнію: чому переміг «пісок»", 18, INK, "middle", "bold")
    rows = [
        ("щілина (§2.5.1)", "0.66 еВ — вузька", "1.12 еВ — ширша", False),
        ("робоча температура", "до ~75 °C («тече»)", "до ~150–175 °C", True),
        ("зворотний витік", "помітний", "малий", True),
        ("рідний оксид", "GeO₂ — нестабільний", "SiO₂ — стабільний ізолятор", True),
        ("планарний процес / ІС", "складно", "природний (маска SiO₂)", True),
        ("поширеність", "рідкісний", "пісок — 2-й у корі", True),
        ("пряме падіння (§2.5.5)", "~0.3 В — нижче", "~0.7 В — вище", False),
    ]
    x0, xg, xs, y0, dy = 60, 350, 600, 90, 42
    s += text(x0, y0 - 12, "властивість", 11, INK, "start", "bold")
    s += text(xg, y0 - 12, "ГЕРМАНІЙ", 12.5, COPP, "middle", "bold")
    s += text(xs, y0 - 12, "КРЕМНІЙ", 12.5, BLUE, "middle", "bold")
    for i, (prop, ge, si, si_win) in enumerate(rows):
        y = y0 + 14 + i * dy
        if i % 2 == 0:
            s += rect(40, y - 16, 740, dy - 4, "#f6f8fb", "none", 0)
        s += text(x0, y + 4, prop, 10.5, INK, "start")
        s += text(xg, y + 4, ge, 10.5, INK, "middle")
        s += text(xs, y + 4, si, 11, "#1f6e33" if si_win else INK, "middle", "bold" if si_win else "normal")
    s += text(W / 2, H - 16, "Германій давав нижче падіння й вищі частоти — та кремній виграв стабільністю, оксидом і ціною.",
              11, GREY, "middle", style="italic")
    save("fig-10-1i-2-ge-vs-si.svg", s)


def fig1i3_dayton():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Фокус Тіла в Дейтоні, 1954: гаряча олія", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "«мої колеги кажуть, що кремнієві транзистори — справа далекого майбутнього…»",
              11.5, GREY, "middle", style="italic")
    # дві склянки гарячої олії
    def beaker(ox, lab, col, dead):
        # склянка
        s2 = _poly([(ox, 130), (ox, 250), (ox + 110, 250), (ox + 110, 130)], INK, 2)
        s2 += rect(ox + 4, 170, 102, 78, "#f3e2b8", "none", 0)  # олія
        s2 += text(ox + 55, 120, "гаряча олія", 10, "#9c6a16", "middle")
        # транзистор у олії
        s2 += rect(ox + 44, 195, 22, 30, "#3a3a3a", INK, 1.4, 3)
        s2 += line(ox + 50, 225, ox + 50, 245, INK, 1.4)
        s2 += line(ox + 60, 225, ox + 60, 245, INK, 1.4)
        s2 += text(ox + 55, 280, lab, 11, col, "middle", "bold")
        # динамік/сигнал
        if dead:
            s2 += text(ox + 55, 305, "✕ замовк", 12, RED, "middle", "bold")
            s2 += _poly([(ox + 20, 100), (ox + 90, 100)], GREY, 2, dash="4,3")
        else:
            s2 += text(ox + 55, 305, "♪ працює далі", 12, "#1f6e33", "middle", "bold")
            s2 += _sine(ox + 18, 100, 74, 14, 3, GREEN, 2.2)
        return s2
    s += beaker(150, "германієвий", COPP, True)
    s += beaker(540, "кремнієвий", BLUE, False)
    s += text(W / 2, 342, "«…а в мене їх кілька в кишені»: занурені в гарячу олію — германій замовк, кремній грав далі.",
              11, GREY, "middle", style="italic")
    save("fig-10-1i-3-dayton.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  ⚙️ Вставка до §2.5.5 — Діод як термометр (Рис. 2.5.5a.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig5a1_method():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 28, "Метод: сталий струм + вимір U_F = термометр", 17, INK, "middle", "bold")
    # ── схема ──
    s += _frame(40, 56, 360, 320, "схема вимірювання")
    # джерело струму
    s += circle(120, 150, 26, "#eef6ef", GREEN, 1.8)
    s += text(120, 146, "I", 14, "#1f6e33", "middle", "bold")
    s += text(120, 162, "ст.", 9, "#1f6e33", "middle")
    s += text(120, 110, "сталий струм", 9.5, "#1f6e33", "middle", "bold")
    s += text(120, 200, "(напр. 100 мкА)", 9, GREY, "middle")
    s += line(120, 176, 120, 230, INK, 2)
    s += line(120, 230, 240, 230, INK, 2)
    # діод-давач
    s += _diode_h(240, 230, 12, False, RED)
    s += text(240, 262, "діод-давач", 9.5, RED, "middle", "bold")
    s += text(240, 278, "(на гарячому об'єкті)", 9, GREY, "middle")
    s += line(240, 230, 320, 230, INK, 2)
    s += line(320, 230, 320, 300, INK, 2)
    s += line(120, 300, 320, 300, INK, 2)
    s += line(180, 124, 180, 124, INK, 0)
    # вольтметр через діод
    s += circle(290, 150, 22, "#fff", INK, 1.6)
    s += text(290, 155, "U", 13, INK, "middle", "bold")
    s += line(228, 230, 228, 150, BLUE, 1.4, dash="4,3")
    s += line(228, 150, 268, 150, BLUE, 1.4, dash="4,3")
    s += line(312, 150, 320, 150, BLUE, 1.4, dash="4,3") + line(320, 150, 320, 230, BLUE, 1.4, dash="4,3")
    s += text(290, 122, "вимір U_F", 9, BLUE, "middle", "bold")
    # ── графік ──
    ox, oy, w, h = 470, 330, 330, 240
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w, oy + 18, "T, °C", 10, INK, "start", "bold")
    s += line(ox, oy, ox, oy - h, INK, 1.4) + text(ox - 6, oy - h - 4, "U_F", 10, INK, "middle", "bold")
    s += _poly([(ox + 10, oy - h + 20), (ox + w - 10, oy - 30)], RED, 2.6)
    # дві точки калібрування
    s += circle(ox + 50, oy - h + 32, 5, BLUE, BLUE, 0)
    s += text(ox + 50, oy - h + 18, "0 °C (лід)", 9, BLUE, "middle", "bold")
    s += circle(ox + w - 60, oy - 44, 5, COPP, COPP, 0)
    s += text(ox + w - 60, oy - 58, "100 °C (окріп)", 9, COPP, "middle", "bold")
    s += text(ox + w / 2 + 30, oy - h / 2 + 10, "нахил −2 мВ/°C", 11, RED, "middle", "bold")
    s += text(ox + w / 2, oy + 36, "майже пряма; дві точки задають калібрування", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 10, "T = T_кал − (U_F − U_кал)/(2 мВ/°C). Струм МУСИТЬ бути сталим — інакше U_F попливе й від струму.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-5a-1-method.svg", s)


def fig5a2_dvbe():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 28, "Трюк точності ΔV_BE: різниця за двох струмів не залежить від екземпляра", 15.5, INK, "middle", "bold")
    # дві ВАХ-точки на напівлог
    ox, oy, w, h = 70, 300, 340, 220
    s += _frame(50, 56, 380, 300, "два струми — дві напруги")
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w, oy + 16, "U_F", 10, INK, "middle", "bold")
    s += line(ox, oy, ox, oy - h, INK, 1.4) + text(ox - 6, oy - h - 4, "log I", 10, INK, "middle", "bold")
    nUT = 0.0259
    def Y(U):
        return oy - (U / 0.8) * h
    s += line(ox + 0.2 * w, Y(0.2), ox + 0.95 * w, Y(0.76), COPP, 2.6)
    for U, I, col in ((0.55, "I₁", GREEN), (0.61, "I₂ = 10·I₁", RED)):
        s += line(ox + (U / 0.8) * w, oy, ox + (U / 0.8) * w, Y(U), col, 1.3, dash="4,3")
        s += line(ox, Y(U), ox + (U / 0.8) * w, Y(U), col, 1.3, dash="4,3")
        s += text(ox + (U / 0.8) * w, oy + 16, I, 10, col, "middle", "bold")
    xa = ox + (0.55 / 0.8) * w
    xb = ox + (0.61 / 0.8) * w
    s += arrow(xa, oy - h - 6, xb, oy - h - 6, INK, 2) + arrow(xb, oy - h - 6, xa, oy - h - 6, INK, 2)
    s += text((xa + xb) / 2, oy - h - 12, "ΔU", 11, INK, "middle", "bold")
    # формула
    s += _frame(460, 56, 380, 300, "чому це точно")
    s += text(650, 92, "ΔU = n·U_T·ln(I₂/I₁)", 14, RED, "middle", "bold")
    s += text(650, 124, "U_T = kT/q  (§2.5.5.m)", 11.5, INK, "middle")
    s += text(650, 156, "при I₂/I₁ = 10:", 11, INK, "middle")
    s += text(650, 178, "ΔU = n·ln10·(kT/q)", 12.5, GREEN, "middle", "bold")
    s += text(650, 210, "ΔU ПРОПОРЦІЙНА абсолютній T!", 11.5, "#1f6e33", "middle", "bold")
    s += text(650, 238, "і НЕ залежить від Is, зміщення,", 10.5, GREY, "middle")
    s += text(650, 254, "екземпляра — лише від відношення струмів", 10.5, GREY, "middle")
    s += text(650, 288, "≈ 0.2 мВ/°C на пару — мало, але", 10, "#9c6a16", "middle")
    s += text(650, 304, "ідеально передбачувано, без калібрування", 10, "#9c6a16", "middle")
    s += text(650, 332, "так міряють T процесори й точні давачі", 10, INK, "middle", "bold")
    s += text(W / 2, H - 10, "Звичайний U_F треба калібрувати під екземпляр; ΔU за двох струмів — абсолютний термометр із фізики.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-5a-2-dvbe.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🧮 Вставка до §2.5.6 — Пульсації після випрямляча (Рис. 2.5.6m.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig6m1_ripple_derive():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 28, "Звідки формула: трикутна пилка розряду", 17.5, INK, "middle", "bold")
    ox, oy, w, h = 80, 300, 660, 210
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w + 6, oy + 4, "t", 11, INK, "start", "bold")
    s += line(ox, oy, ox, oy - h - 10, INK, 1.4) + text(ox - 6, oy - h - 14, "U", 11, INK, "middle", "bold")
    # горби випрямленого входу (пунктир)
    per = 150
    hb = []
    for j in range(0, int(w) + 1):
        t = j / per
        v = abs(math.sin(math.pi * t))
        hb.append((ox + j, oy - 40 - v * (h - 50)))
    s += _poly(hb, GREY, 1.4, dash="4,4")
    s += text(ox + 60, oy - h - 2, "горби з моста (пунктир)", 9.5, GREY, "start")
    # напруга на C: швидкий заряд до піку, лінійний спад
    top = oy - 40 - (h - 50)
    drop = 46
    cp = []
    for k in range(0, 5):
        x0 = ox + k * per + per * 0.5
        # спад
        cp.append((x0, top))
        cp.append((x0 + per * 0.8, top + drop))
        # швидкий заряд назад до піку
        cp.append((x0 + per, top))
    s += _poly([(ox, top)] + cp, RED, 2.8)
    # позначка ΔU і Δt
    xa = ox + per * 0.5
    s += line(xa - 30, top, ox + w, top, GREEN, 1, dash="3,3")
    s += line(xa - 30, top + drop, ox + w, top + drop, GREEN, 1, dash="3,3")
    s += arrow(ox + 40, top, ox + 40, top + drop, GREEN, 2)
    s += arrow(ox + 40, top + drop, ox + 40, top, GREEN, 2)
    s += text(ox + 48, top + drop / 2 + 4, "ΔU = пульсація", 10.5, GREEN, "start", "bold")
    x1, x2 = ox + per * 1.5, ox + per * 2.5
    s += arrow(x1, oy - 16, x2, oy - 16, BLUE, 2) + arrow(x2, oy - 16, x1, oy - 16, BLUE, 2)
    s += text((x1 + x2) / 2, oy - 22, "Δt ≈ 1/f_пульс", 10.5, BLUE, "middle", "bold")
    s += _frame(470, 56, 320, 96, "")
    s += text(630, 82, "заряд стікає струмом I за час Δt:", 11, INK, "middle")
    s += text(630, 108, "ΔU = I·Δt/C = I /(f·C)", 13.5, RED, "middle", "bold")
    s += text(630, 134, "(трикутне наближення розряду)", 9.5, GREY, "middle")
    s += text(W / 2, H - 10, "Поки пульсація мала, спад майже прямий — лінійне наближення точне (бо Δt « RC).",
              10.5, GREY, "middle", style="italic")
    save("fig-10-6m-1-ripple-derive.svg", s)


def fig6m2_bridge_advantage():
    W, H = 840, 360
    s = header(W, H)
    s += text(W / 2, 28, "Міст удвічі кращий: подвоїв частоту — удвічі менша пульсація", 16.5, INK, "middle", "bold")

    def panel(ox, fr, lab, drop, col):
        oy, w, h = 280, 320, 150
        out = _frame(ox - 10, 60, 340, 250, lab)
        out += line(ox, oy, ox + w, oy, INK, 1.3)
        per = 320 / fr
        top = oy - h
        cp = [(ox, top)]
        x = ox
        while x < ox + w - 1:
            cp.append((x + per * 0.78, top + drop))
            cp.append((x + per, top))
            x += per
        out += _poly(cp, col, 2.6)
        # горби
        hb = []
        for j in range(0, int(w) + 1):
            t = j / per
            v = abs(math.sin(math.pi * t))
            hb.append((ox + j, oy - 20 - v * (h - 30)))
        out += _poly(hb, GREY, 1.2, dash="3,3")
        out += text(ox + w / 2, oy + 24, f"{fr} горбів/період · C однакова", 9.5, GREY, "middle")
        return out

    s += panel(40, 2, "однопівперіодний: f_пульс = 50 Гц", 70, COPP)
    s += panel(450, 4, "міст: f_пульс = 100 Гц", 35, GREEN)
    s += text(W / 2, H - 10, "Та сама ємність і струм, але вдвічі частіші горби лишають конденсатору вдвічі менше часу просісти.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-6m-2-bridge-advantage.svg", s)


def fig6m3_surge():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Зворотний бік: діод хапає струм вузькими піками", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 80, 250, 680, 150
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w + 6, oy + 4, "t", 11, INK, "start", "bold")
    s += line(ox, oy, ox, oy - h - 20, INK, 1.4) + text(ox - 6, oy - h - 24, "I", 11, INK, "middle", "bold")
    # середній струм навантаження
    s += line(ox, oy - 28, ox + w, oy - 28, BLUE, 2, dash="6,4")
    s += text(ox + w - 4, oy - 34, "середній струм навантаження I", 10, BLUE, "end", "bold")
    # вузькі піки струму діода на верхівках
    per = 150
    for k in range(0, 5):
        xc = ox + k * per + per * 0.5
        s += _poly([(xc - 18, oy), (xc - 6, oy - h), (xc + 6, oy - h), (xc + 18, oy)], RED, 2.4)
    s += text(ox + per * 0.5 + 22, oy - h + 10, "піковий струм заряду", 10, RED, "start", "bold")
    s += text(ox + per * 0.5 + 22, oy - h + 26, "I_пік ≈ I · (T/t_заряду)", 10.5, RED, "start", "bold")
    s += _frame(470, 286, 320, 80, "")
    s += text(630, 312, "до пульсації від розряду додається", 10, INK, "middle")
    s += text(630, 334, "стрибок I_пік · ESR (§2.1.5)", 11.5, "#9c6a16", "middle", "bold")
    s += text(W / 2, H - 8, "Заряд тече лише на верхівці горба — короткими сильними кидками; їх витримують і діоди, і трансформатор.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-6m-3-surge.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🧮 Вставка до §2.5.5 — Рівняння Шоклі (Рис. 2.5.5m.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig5m1_boltzmann():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чому експонента: носіїв з енергією вище бар'єра — больцманівський хвіст", 16.5, INK, "middle", "bold")

    def hill(ox, barrier_h, lab, tail_lo, col):
        oy = 300
        # бар'єр-пагорб
        pts = []
        for j in range(0, 161):
            x = j / 160.0
            y = barrier_h * math.exp(-((x - 0.5) * 4.2) ** 2)
            pts.append((ox + j * 1.4, oy - y))
        s2 = _poly(pts, INK, 2.2)
        s2 += line(ox, oy, ox + 224, oy, INK, 1.4)
        s2 += text(ox + 112, oy + 18, lab, 11.5, INK, "middle", "bold")
        # рівень бар'єра
        top = oy - barrier_h
        s2 += line(ox, top, ox + 224, top, GREY, 1, dash="4,3")
        s2 += text(ox + 228, top + 4, "бар'єр", 9.5, GREY, "start")
        # розподіл носіїв за енергією (експ. хвіст), вертикально ліворуч
        ex = ox - 14
        ept = []
        for j in range(0, 121):
            E = j / 120.0 * (barrier_h + 40)
            n = 70 * math.exp(-E / 30.0)
            ept.append((ex - n, oy - E))
        s2 += _poly(ept, col, 2)
        # заштрихований хвіст над бар'єром
        for j in range(0, 121):
            E = j / 120.0 * (barrier_h + 40)
            if E >= barrier_h:
                n = 70 * math.exp(-E / 30.0)
                s2 += line(ex, oy - E, ex - n, oy - E, col, 0.8)
        s2 += text(ex - 40, top - 8, "проходять", 9.5, col, "middle", "bold")
        return s2

    s += hill(120, 150, "бар'єр високий (U=0)", 150, BLUE)
    s += hill(470, 96, "напруга знизила на qU", 96, RED)
    s += arrow(360, 150, 446, 150, GREEN, 2)
    s += text(403, 138, "+U", 12, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Частка носіїв з енергією вище бар'єра ∝ e^(−бар'єр/kT). Напруга знижує бар'єр → струм росте ЕКСПОНЕНЦІЙНО.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-5m-1-boltzmann.svg", s)


def fig5m2_two_scales():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 28, "Та сама ВАХ двічі: коліно — це пряма в напівлог-осях", 17, INK, "middle", "bold")
    Is = 1e-12
    nUT = 0.0259
    # ліва панель — лінійна
    ox, oy, w, h = 70, 320, 300, 230
    s += _frame(ox - 20, 70, 340, 280, "лінійні осі: «коліно»")
    s += line(ox, oy, ox + w, oy, INK, 1.6)
    s += line(ox, oy, ox, oy - h, INK, 1.6)
    s += text(ox + w, oy + 18, "U", 11, INK, "middle", "bold")
    s += text(ox - 8, oy - h - 6, "I", 11, INK, "middle", "bold")
    Imax = Is * math.exp(0.75 / nUT)
    pts = []
    for j in range(0, 201):
        U = j / 200.0 * 0.78
        I = Is * (math.exp(U / nUT) - 1)
        pts.append((ox + U / 0.78 * w, oy - min(I / Imax, 1.0) * h))
    s += _poly(pts, COPP, 2.6)
    s += text(ox + 0.7 * w, oy - 0.1 * h, "≈0.7 В", 10.5, COPP, "middle", "bold")
    s += text(ox + w / 2, oy + 36, "круте «коліно» — нічого до 0.6 В", 9.5, GREY, "middle")

    # права панель — напівлог
    ox2 = 510
    s += _frame(ox2 - 20, 70, 340, 280, "напівлог (вісь I логарифмічна): ПРЯМА")
    s += line(ox2, oy, ox2 + w, oy, INK, 1.6)
    s += line(ox2, oy, ox2, oy - h, INK, 1.6)
    s += text(ox2 + w, oy + 18, "U", 11, INK, "middle", "bold")
    s += text(ox2 - 8, oy - h - 6, "log I", 11, INK, "middle", "bold")
    # декади
    for d in range(0, 7):
        yy = oy - d / 6.0 * h
        s += line(ox2, yy, ox2 + w, yy, FAINT, 1)
        s += text(ox2 - 6, yy + 4, f"10^-{12-2*d}", 8, GREY, "end")
    # пряма: log10 I = log10 Is + U/(nUT ln10)
    U1, U2 = 0.2, 0.74
    def Y(U):
        I = Is * math.exp(U / nUT)
        d = (math.log10(I) + 12) / 12.0
        return oy - d * h
    s += line(ox2 + U1 / 0.78 * w, Y(U1), ox2 + U2 / 0.78 * w, Y(U2), COPP, 2.6)
    # нахил 60 мВ/декаду
    s += line(ox2 + 0.5 * w, Y(0.47), ox2 + 0.5 * w, Y(0.47) + h / 6, GREEN, 1.6, dash="3,3")
    s += line(ox2 + 0.5 * w, Y(0.47) + h / 6, ox2 + 0.5 * w + 0.06 / 0.78 * w, Y(0.47) + h / 6, GREEN, 1.6, dash="3,3")
    s += text(ox2 + 0.5 * w + 40, Y(0.47) + h / 6 + 16, "+60 мВ", 10, GREEN, "middle", "bold")
    s += text(ox2 + 0.5 * w + 40, Y(0.47) + h / 6 + 30, "= ×10 струму", 9.5, GREEN, "middle")
    s += text(W / 2, H - 12, "log I росте ЛІНІЙНО з U: нахил рівно ln10·U_T ≈ 60 мВ на декаду струму (≈26 мВ на e-кратне).",
              10.5, GREY, "middle", style="italic")
    save("fig-10-5m-2-two-scales.svg", s)


def fig5m3_temperature():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 28, "Чому падіння тане −2 мВ/°C, хоч U_T росте з температурою", 16.5, INK, "middle", "bold")
    ox, oy, w, h = 90, 310, 560, 240
    s += line(ox, oy, ox + w, oy, INK, 1.6) + text(ox + w, oy + 18, "U", 11, INK, "middle", "bold")
    s += line(ox, oy, ox, oy - h, INK, 1.6) + text(ox - 8, oy - h - 6, "I", 11, INK, "middle", "bold")
    # фіксований робочий струм
    Ifix = 0.62
    s += line(ox, oy - Ifix * h, ox + w, oy - Ifix * h, GREY, 1.2, dash="5,4")
    s += text(ox + w - 4, oy - Ifix * h - 8, "робочий струм (фіксований)", 9.5, GREY, "end")
    for Tlab, shift, col in (("25 °C", 0.70, BLUE), ("75 °C", 0.60, RED)):
        pts = []
        for j in range(0, 201):
            x = j / 200.0
            U = x * 0.95
            # коліно зсунуте: нижча T — правіше
            I = math.exp((U - shift) / 0.07)
            pts.append((ox + U / 0.95 * w, oy - min(I, 1.0) * h))
        s += _poly(pts, col, 2.6)
        s += text(ox + shift / 0.95 * w + 30, oy - 0.9 * h + (0 if col == BLUE else 20), Tlab, 11, col, "start", "bold")
    # стрілка між колінами на рівні робочого струму
    xb = ox + 0.60 * w  # 75°C
    xa = ox + 0.70 * w  # 25°C
    s += arrow(xa, oy - Ifix * h, xb, oy - Ifix * h, GREEN, 2.4)
    s += text((xa + xb) / 2, oy - Ifix * h - 12, "ΔU", 11, GREEN, "middle", "bold")
    s += _frame(430, 70, 360, 120, "")
    s += text(610, 96, "за фіксованого струму:", 11, INK, "middle", "bold")
    s += text(610, 120, "U(T) ≈ U₀ − 2 мВ/°C · ΔT", 12.5, RED, "middle", "bold")
    s += text(610, 146, "Is росте з T швидше, ніж U_T,", 10, GREY, "middle")
    s += text(610, 162, "тож коліно сповзає ВЛІВО", 10, GREY, "middle")
    s += text(W / 2, H - 10, "50° нагріву → падіння менше на ≈100 мВ. Стабільність цього дрейфу й робить діод дешевим термометром.",
              10.5, GREY, "middle", style="italic")
    save("fig-10-5m-3-temperature.svg", s)


def fig5a10_7_inout():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Два типові ввімкнення: туди й назад через стіну", 17.5, INK, "middle", "bold")

    def opto(cx, cy):
        t = rect(cx - 30, cy - 34, 60, 68, "#f4f1ea", "#b8a98a", 1.6, 6)
        t += line(cx, cy - 40, cx, cy + 40, "#9bb0c2", 1.6, dash="3,4")
        t += _diode_h(cx - 14, cy - 14, 9, True, RED)
        t += _phototrans(cx + 12, cy + 12, 14, INK)
        for k in range(2):
            t += _photon(cx - 6, cy - 8 + k * 6, cx + 4, cy + 4 + k * 6, SUN, 2, 1)
        return t

    # ліва панель: MCU → сила
    s += _frame(40, 70, 360, 250, "контролер ВМИКАЄ силу")
    s += rect(70, 150, 70, 40, "#eef6ef", GREEN, 1.5, 6) + text(105, 175, "MCU", 11, INK, "middle", "bold")
    s += text(105, 130, "вихід 3.3 В", 9.5, GREEN, "middle")
    s += line(140, 170, 175, 170, INK, 2)
    s += rect(175, 162, 26, 16, "#fff", INK, 1.4) + text(188, 150, "R", 9.5, INK, "middle", "bold")
    s += line(201, 170, 215, 170, INK, 2)
    s += opto(245, 170)
    s += rect(300, 150, 80, 40, "#fbecec", RED, 1.5, 6) + text(340, 175, "силовий", 10, RED, "middle", "bold")
    s += text(340, 130, "ключ / реле", 9.5, RED, "middle")
    s += line(275, 182, 300, 182, INK, 2)
    s += text(220, 300, "слабка логіка керує сильним колом, не торкаючись його", 9.5, GREY, "middle", style="italic")

    # права панель: сила → MCU
    s += _frame(460, 70, 360, 250, "сила ДОПОВІДАЄ контролеру")
    s += rect(490, 150, 80, 40, "#fbecec", RED, 1.5, 6) + text(530, 175, "24 В / ~", 10, RED, "middle", "bold")
    s += text(530, 130, "вхідний сигнал", 9.5, RED, "middle")
    s += line(570, 170, 600, 170, INK, 2)
    s += rect(600, 162, 24, 16, "#fff", INK, 1.4) + text(612, 150, "R", 9.5, INK, "middle", "bold")
    s += line(624, 170, 638, 170, INK, 2)
    s += opto(668, 170)
    s += rect(720, 150, 70, 40, "#eef6ef", GREEN, 1.5, 6) + text(755, 175, "MCU", 11, INK, "middle", "bold")
    s += text(755, 130, "вхід", 9.5, GREEN, "middle")
    s += line(698, 182, 720, 182, INK, 2)
    s += text(640, 300, "«брудний» сигнал бачать, не пускаючи його в логіку", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 12, "В обидва боки світлодіод — на боці джерела сигналу, фототранзистор — на боці приймача.",
              11, GREY, "middle", style="italic")
    save("fig-10-10-7-inout.svg", s)


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
    # §10.10 Оптопара й гальванічна розв'язка (тема 2.5.10)
    fig5a10_1_need()
    fig5a10_2_inside()
    fig5a10_3_ctr()
    fig5a10_4_isolation()
    fig5a10_5_speed()
    fig5a10_6_family()
    fig5a10_7_inout()
    # 🧮 вставка до §2.5.5 — рівняння Шоклі
    fig5m1_boltzmann()
    fig5m2_two_scales()
    fig5m3_temperature()
    # 🧮 вставка до §2.5.6 — пульсації після випрямляча
    fig6m1_ripple_derive()
    fig6m2_bridge_advantage()
    fig6m3_surge()
    # ⚙️ вставка до §2.5.5 — діод як термометр
    fig5a1_method()
    fig5a2_dvbe()
    # 📜 історія до §2.5.1 — кремній проти германію
    fig1i1_timeline()
    fig1i2_ge_vs_si()
    fig1i3_dayton()
    # 📜 історія до §2.5.7 — блакитний світлодіод
    fig7i1_timeline()
    fig7i2_why_hard()
    fig7i3_three()
    # 🔌 вставка до §2.5.6 — діодний міст як компонент
    fig6c1_bridge_pkg()
    fig6c2_drop_heat()
    # 🔌 вставка до §2.5.7 — світлодіоди на практиці
    fig7c1_rgb_white()
    fig7c2_resistor_vs_driver()
    # ⚙️ вставка до §2.5.7 — Charlieplexing
    fig7a1_principle()
    fig7a2_scale()
    # 🔌 вставка до §2.5.8 — сімейства діодів
    fig8c1_workhorses()
    fig8c2_marking()
    # 🔌 вставка до §2.5.8 — TVS-діоди
    fig8c3_tvs_action()
    fig8c4_tvs_params()
    # 🔌 вставка до §2.5.10 — оптопара PC817-класу
    fig10c1_pc817_calc()
    fig10c2_ranks_family()
    print("OK — Розділ 10 ПОВНІСТЮ (історія + §10.1–§10.10 + 2 історії до тем) згенеровано в", OUT)
