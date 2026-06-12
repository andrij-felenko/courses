# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до теми 1.9.8 —
«Телефон проти телеграфу: як Белл запатентував звивання (1881)» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py
розділу та figs-r09-history-johnson-nyquist.py не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: історія до теми 1.9.8 → Рис. 1.9.8і.N.
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
PURPLE = "#7a3fae"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange"}


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


# Хвиля «гулу» — джерело завади (тонка синусоїда в рамці)
def _hum(x0, y0, w, h, color=ORANGE, cycles=3.0, lw=2.2):
    pts = []
    n = 120
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        y = y0 - (h / 2) * math.sin(2 * math.pi * cycles * t)
        pts.append((x, y))
    return polyline(pts, color, lw)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до теми 1.9.8 — вита пара.  Рис. 1.9.8і.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.8і.1 — чому звивання гасить наводку (геометрія патенту) ──────────
def fig_twist_cancels():
    W, H = 1000, 540
    s = header(W, H)
    s += text(W / 2, 30, "Серце патенту 1881 року: звивання зрівнює два проводи перед завадою",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "наводка діє сильніше на ближчий провід; звивання раз у раз міняє їх місцями — тож сумарно дістається порівну",
              11.5, GREY, "middle", style="italic")

    # --- джерело завади (спільне для обох панелей): зверху ---
    src_y = 96
    s += rect(70, src_y - 22, 860, 40, fill="#fff6ec", stroke=ORANGE, sw=1.6, rx=8)
    s += _hum(120, src_y - 2, 250, 22, ORANGE, 4.0, 2.0)
    s += text(390, src_y + 3, "джерело завади:  трамвайний фідер / силова лінія / сусідня пара",
              13, ORANGE, "start", "bold")
    s += text(390, src_y + 18, "(змінне поле наводить напругу — тим більшу, чим ближчий провід)",
              10.5, GREY, "start", style="italic")

    # ── ЛІВА панель: прямі проводи (погано) ──────────────────────────────────
    lx0, lx1 = 95, 430
    yA, yB = 250, 300            # провід A (ближчий), провід B (дальший)
    s += text((lx0 + lx1) / 2, 150, "Два прямі проводи", 15.5, RED, "middle", "bold")

    # стрілки наводки (вниз), різної довжини → нерівний вплив
    for fx in range(lx0 + 30, lx1, 70):
        s += arrow(fx, src_y + 24, fx, yA - 8, ORANGE, 2.0)          # сильніше до A
        s += arrow(fx + 18, src_y + 24, fx + 18, yB - 8, GREY, 1.4, dash="3,4")  # слабше до B

    s += line(lx0, yA, lx1, yA, RED, 3)
    s += line(lx0, yB, lx1, yB, BLUE, 3)
    s += text(lx0 - 6, yA + 4, "A", 13, RED, "end", "bold")
    s += text(lx0 - 6, yB + 4, "B", 13, BLUE, "end", "bold")
    s += text(lx1 + 8, yA + 4, "+++", 13, ORANGE, "start", "bold")
    s += text(lx1 + 8, yB + 4, "+", 12, GREY, "start", "bold")

    # підсумок різниці
    s += rect(lx0, 340, lx1 - lx0, 92, fill="#fdeceb", stroke=RED, sw=1.4, rx=8)
    s += text((lx0 + lx1) / 2, 363, "A весь час ближчий → ловить більше",
              12.5, INK, "middle", "bold")
    s += text((lx0 + lx1) / 2, 384, "наводка на A  ≠  наводка на B", 13, RED, "middle", "bold")
    s += text((lx0 + lx1) / 2, 408, "різниця (саме її «чує» телефон)", 11, GREY, "middle")
    s += text((lx0 + lx1) / 2, 425, "велика  →  гучний гул", 13.5, RED, "middle", "bold")

    # ── ПРАВА панель: звита пара (добре) ─────────────────────────────────────
    rx0, rx1 = 570, 905
    ymid = 275
    amp = 25
    s += text((rx0 + rx1) / 2, 150, "Та сама пара, але звита", 15.5, GREEN, "middle", "bold")

    # дві переплетені синусоїди (A червона, B синя) — у протифазі
    nA, nB = [], []
    cyc = 3.0
    npts = 160
    for i in range(npts + 1):
        t = i / npts
        x = rx0 + t * (rx1 - rx0)
        ph = 2 * math.pi * cyc * t
        nA.append((x, ymid - amp * math.sin(ph)))
        nB.append((x, ymid + amp * math.sin(ph)))
    s += polyline(nA, RED, 3)
    s += polyline(nB, BLUE, 3)
    s += text(rx0 - 6, ymid - amp + 2, "A", 13, RED, "end", "bold")
    s += text(rx0 - 6, ymid + amp + 6, "B", 13, BLUE, "end", "bold")

    # стрілки наводки (однакові) + позначки «+/−» на сегментах, де провід угорі
    for k, fx in enumerate(range(rx0 + 28, rx1, 56)):
        s += arrow(fx, src_y + 24, fx, ymid - amp - 12, ORANGE, 1.8)
        # хто зараз угорі (ближче) — A чи B — чергується
        top_is_A = (math.sin(2 * math.pi * cyc * ((fx - rx0) / (rx1 - rx0))) < 0)
        lab = "A↑" if top_is_A else "B↑"
        col = RED if top_is_A else BLUE
        s += text(fx, ymid - amp - 16, lab, 9.5, col, "middle", "bold")

    # підсумок
    s += rect(rx0, 340, rx1 - rx0, 92, fill="#eef7f0", stroke=GREEN, sw=1.4, rx=8)
    s += text((rx0 + rx1) / 2, 363, "по черзі ближчий то A, то B → ловлять порівну",
              12, INK, "middle", "bold")
    s += text((rx0 + rx1) / 2, 384, "наводка на A  ≈  наводка на B", 13, GREEN, "middle", "bold")
    s += text((rx0 + rx1) / 2, 408, "різниця майже зникає", 11, GREY, "middle")
    s += text((rx0 + rx1) / 2, 425, "мало  →  тиша в слухавці", 13.5, GREEN, "middle", "bold")

    # роздільник
    s += line(500, 145, 500, 432, FAINT, 1.6, dash="4,6")

    s += text(W / 2, 470, "Білл не вигадав нової фізики — він використав геометрію: однаковий зовнішній вплив на обидва проводи",
              12, INK, "middle")
    s += text(W / 2, 488, "сам собою «віднімається», бо телефон реагує лише на РІЗНИЦЮ напруг між проводами пари.",
              12, INK, "middle")
    save("fig-r09-s8i-1-twist-cancels.svg", s)


# ── Рис. 1.9.8і.2 — три епохи лінії: від землі-повернення до звивання ─────────
def fig_three_eras():
    W, H = 1020, 560
    s = header(W, H)
    s += text(W / 2, 30, "Три епохи дроту: чому телефону довелося робити те, без чого телеграф жив",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "телеграф терпів наводку, телефон — ні; розв'язком став симетричний металевий контур, а далі — звивання й транспозиція",
              11.5, GREY, "middle", style="italic")

    panels = [
        # (x0, заголовок, рік-підпис, колір рамки)
        (40,  "1  Телеграф: один дріт + земля", "робить, бо сигнал грубий (так/ні)", GREY),
        (368, "2  Металевий контур (2 дроти)", "Карті, кінець 1880-х · кабель Белла 1881", BLUE),
        (696, "3  Звивання + транспозиція", "по всій мережі — до ~1900", GREEN),
    ]
    pw = 286
    for x0, title, sub, col in panels:
        s += rect(x0, 86, pw, 250, fill="#fcfcfc", stroke=col, sw=1.8, rx=10)
        s += text(x0 + pw / 2, 110, title, 13.5, col, "middle", "bold")
        s += text(x0 + pw / 2, 128, sub, 10, GREY, "middle", style="italic")

    # --- джерело завади над усіма (гул 50 Гц / трамвай) ---
    s += _hum(60, 158, 900, 18, ORANGE, 9.0, 1.6)
    s += text(500, 150, "наводка (трамвай, силова лінія, сусідні дроти)", 10.5, ORANGE, "middle", style="italic")

    # ── Панель 1: один дріт + земля ──────────────────────────────────────────
    x0 = 40
    yw = 215
    s += arrow(x0 + 60, 178, x0 + 60, yw - 8, ORANGE, 1.8)
    s += arrow(x0 + 150, 178, x0 + 150, yw - 8, ORANGE, 1.8)
    s += arrow(x0 + 230, 178, x0 + 230, yw - 8, ORANGE, 1.8)
    s += line(x0 + 30, yw, x0 + 256, yw, RED, 3)        # сигнальний дріт
    s += text(x0 + 30, yw - 8, "сигнальний дріт", 10, RED, "start")
    # земля
    gy = 300
    s += line(x0 + 30, gy, x0 + 256, gy, COPPER, 3)
    for gx in range(x0 + 45, x0 + 250, 26):
        s += line(gx, gy, gx - 8, gy + 12, COPPER, 1.6)
    s += text(x0 + pw / 2, gy + 28, "ЗЕМЛЯ — другий «провід»", 11, COPPER, "middle", "bold")
    # вертикальні стики дріт↔прилад↔земля
    s += line(x0 + 40, yw, x0 + 40, gy, INK, 1.6)
    s += line(x0 + 246, yw, x0 + 246, gy, INK, 1.6)
    s += text(x0 + pw / 2, 250, "велика петля «дріт — земля»", 10.5, RED, "middle", "bold")
    s += text(x0 + pw / 2, 266, "= велика антена для завад", 10.5, RED, "middle")

    # ── Панель 2: металевий контур (дві прямі) ───────────────────────────────
    x0 = 368
    yA, yB = 215, 250
    s += arrow(x0 + 70, 178, x0 + 70, yA - 8, ORANGE, 1.8)
    s += arrow(x0 + 160, 178, x0 + 160, yA - 8, ORANGE, 1.8)
    s += arrow(x0 + 230, 178, x0 + 230, yA - 8, ORANGE, 1.8)
    s += line(x0 + 30, yA, x0 + 256, yA, RED, 3)
    s += line(x0 + 30, yB, x0 + 256, yB, BLUE, 3)
    s += text(x0 + 26, yA + 4, "A", 11, RED, "end", "bold")
    s += text(x0 + 26, yB + 4, "B", 11, BLUE, "end", "bold")
    s += text(x0 + pw / 2, 290, "сигнал «туди й назад» по двох дротах", 10.5, BLUE, "middle", "bold")
    s += text(x0 + pw / 2, 308, "землю викинуто з петлі →", 10.5, INK, "middle")
    s += text(x0 + pw / 2, 324, "гул різко спадає, але A ще ближчий за B", 10, GREY, "middle", style="italic")

    # ── Панель 3: звита пара + транспозиція ──────────────────────────────────
    x0 = 696
    ymid = 232
    amp = 18
    s += arrow(x0 + 70, 178, x0 + 70, ymid - amp - 10, ORANGE, 1.8)
    s += arrow(x0 + 160, 178, x0 + 160, ymid - amp - 10, ORANGE, 1.8)
    s += arrow(x0 + 230, 178, x0 + 230, ymid - amp - 10, ORANGE, 1.8)
    aa, bb = [], []
    cyc = 4.0
    npts = 140
    for i in range(npts + 1):
        t = i / npts
        x = (x0 + 30) + t * 226
        ph = 2 * math.pi * cyc * t
        aa.append((x, ymid - amp * math.sin(ph)))
        bb.append((x, ymid + amp * math.sin(ph)))
    s += polyline(aa, RED, 2.6)
    s += polyline(bb, BLUE, 2.6)
    s += text(x0 + pw / 2, 285, "проводи раз у раз міняються місцями", 10.5, GREEN, "middle", "bold")
    s += text(x0 + pw / 2, 303, "у кабелі — звивання (Белл, 1881)", 10, INK, "middle")
    s += text(x0 + pw / 2, 319, "на стовпах — транспозиція відкритих ліній", 10, INK, "middle")

    # --- нижня смуга: рушій 1890-х (щоб не сплутати з 1881) ---
    by = 376
    s += rect(40, by, 942, 96, fill="#fff6ec", stroke=ORANGE, sw=1.6, rx=10)
    s += text(60, by + 24, "Що змусило перейти на симетрію по всій мережі — 1890-ті, а не 1881:",
              13, ORANGE, "start", "bold")
    s += text(60, by + 46,
              "електричні трамваї й силові мережі залили землю зворотними струмами — і однопровідні телефони з поверненням через",
              11, INK, "start")
    s += text(60, by + 63,
              "ґрунт затопило гулом. Саме тоді (а не в рік патенту) телефонні компанії масово перейшли на металеві контури,",
              11, INK, "start")
    s += text(60, by + 80,
              "звиті в кабелях і транспоновані на відкритих лініях. Патент 1881 р. був про кабельну геометрію — рушій 1890-х окремий.",
              11, INK, "start")

    s += text(W / 2, 500, "Стрілка історії: один дріт + земля (досить телеграфу)  →  два дроти (металевий контур)  →  звивання/транспозиція (симетрія в дії)",
              11.5, INK, "middle")
    s += text(W / 2, 520, "Телефон ніс слабкий неперервний голос — тому пройшов цей шлях першим; цифрові шини потім успадкували саму ідею.",
              11, GREY, "middle", style="italic")
    save("fig-r09-s8i-2-three-eras.svg", s)


if __name__ == "__main__":
    fig_twist_cancels()
    fig_three_eras()
    print("done.")
