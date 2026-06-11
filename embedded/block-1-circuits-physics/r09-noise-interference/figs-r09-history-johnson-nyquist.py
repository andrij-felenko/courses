# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 1.9 —
«Джонсон і Найквіст: шум як властивість матерії» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: історія до розділу — секція 0 → Рис. 1.9.0.N.
"""
import os
import math
import random

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
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange", PURPLE: "aPurple"}


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


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 1.9 — Джонсон і Найквіст.  Рис. 1.9.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.0.1 — як народжувалося відкриття: лінія часу ─────────────────────
def fig_timeline():
    W, H = 1000, 440
    s = header(W, H)
    s += text(W / 2, 30, "Як шум перестав бути дефектом приладу й став законом природи",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "від броунівського руху до точної формули — півстоліття, що зійшлися у двох статтях 1928 року",
              11.5, GREY, "middle", style="italic")

    ax, ay, aw = 70, 250, 860
    s += line(ax, ay, ax + aw, ay, INK, 2.2)
    s += polygon([(ax + aw, ay), (ax + aw - 14, ay - 6), (ax + aw - 14, ay + 6)], INK)
    s += text(ax + aw + 6, ay + 5, "час", 11.5, INK, "start", "bold")

    # (частка, дата, рядок1, рядок2, колір, вгору?)
    events = [
        (0.05, "1827", "Роберт Браун", "пилок безперервно тремтить", GREY, True),
        (0.215, "1905-06", "Ейнштейн, Смолуховський", "тремтіння = тепловий рух молекул", GREEN, False),
        (0.40, "1918", "Вальтер Шотткі", "передбачає шум у лампах (теорія)", PURPLE, True),
        (0.605, "1926-28", "Джон Джонсон", "ВИМІРЯВ шум у резисторі", RED, False),
        (0.79, "1928", "Гаррі Найквіст", "ПОЯСНИВ його термодинамікою", BLUE, True),
        (0.955, "1951", "Каллен, Велтон", "флуктуація-дисипація (загальний закон)", ORANGE, False),
    ]
    for frac, date, l1, l2, col, up in events:
        x = ax + aw * frac
        s += circle(x, ay, 6.5, col, col, 1)
        if up:
            s += line(x, ay - 6, x, ay - 40, col, 1.4, "4,3")
            box_y = ay - 40 - 58
            s += rect(x - 84, box_y, 168, 54, "#ffffff", col, 1.5, 8)
            s += text(x, box_y + 17, date, 11.5, col, "middle", "bold")
            s += text(x, box_y + 33, l1, 10, INK, "middle", "bold")
            s += text(x, box_y + 47, l2, 8.6, GREY, "middle")
        else:
            s += line(x, ay + 6, x, ay + 40, col, 1.4, "4,3")
            box_y = ay + 40
            s += rect(x - 84, box_y, 168, 54, "#ffffff", col, 1.5, 8)
            s += text(x, box_y + 17, date, 11.5, col, "middle", "bold")
            s += text(x, box_y + 33, l1, 10, INK, "middle", "bold")
            s += text(x, box_y + 47, l2, 8.6, GREY, "middle")

    # підсвітити пару Джонсон+Найквіст
    gx0 = ax + aw * 0.605
    gx1 = ax + aw * 0.79
    s += line(gx0, ay + 132, gx1, ay + 132, RED, 1.8)
    s += line(gx0, ay + 127, gx0, ay + 137, RED, 1.8)
    s += line(gx1, ay + 127, gx1, ay + 137, RED, 1.8)
    s += text((gx0 + gx1) / 2, ay + 150, "експеримент + теорія = «шум Джонсона—Найквіста»",
              10.5, RED, "middle", "bold")
    save("fig-r09-hist-1-timeline.svg", s)


# ── Рис. 1.9.0.2 — що бачив Джонсон: резистор як власне джерело напруги ───────
def fig_what_johnson_saw():
    W, H = 980, 430
    s = header(W, H)
    s += text(W / 2, 30, "Що побачив Джонсон: навіть «мертвий» резистор сам видає напругу",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "жодної батареї в колі — лише шматок металу при кімнатній температурі, а вольтметр уже тремтить",
              11, GREY, "middle", style="italic")

    # ── ЛІВА панель: ідеалізація — резистор «німий» ──
    s += rect(40, 74, 410, 322, "#f7f7f7", GREY, 1.6, 12)
    s += text(245, 100, "Як гадали доти: R при I=0 — німий", 12.5, GREY, "middle", "bold")
    # резистор-зигзаг
    rx0, ry = 120, 175
    zig = [(rx0, ry)]
    for i in range(6):
        zig.append((rx0 + 14 + i * 18, ry - (12 if i % 2 == 0 else -12)))
    zig.append((rx0 + 14 + 6 * 18, ry))
    s += polyline(zig, INK, 2.6)
    s += line(rx0 - 34, ry, rx0, ry, INK, 2.6)
    s += line(rx0 + 14 + 6 * 18, ry, rx0 + 14 + 6 * 18 + 34, ry, INK, 2.6)
    s += text(rx0 + 50, ry - 26, "R", 14, INK, "middle", "bold", "italic")
    # плаский вольтметр
    s += circle(245, 290, 30, "#ffffff", GREY, 2)
    s += text(245, 296, "V", 15, GREY, "middle", "bold")
    s += line(rx0 - 34, ry, 86, 290, GREY, 2)
    s += line(86, 290, 215, 290, GREY, 2)
    s += line(rx0 + 14 + 6 * 18 + 34, ry, 404, 290, GREY, 2)
    s += line(404, 290, 275, 290, GREY, 2)
    # пряма лінія на «екрані»
    s += line(150, 358, 340, 358, GREY, 2.2)
    s += text(245, 380, "очікувано: рівно нуль", 10.5, GREY, "middle")

    # ── ПРАВА панель: реальність — тремтлива напруга ──
    s += rect(506, 74, 434, 322, "#eef2fb", BLUE, 1.8, 12)
    s += text(723, 100, "Насправді: на R сама собою тремтить напруга", 12.5, BLUE, "middle", "bold")
    rx1 = 586
    zig = [(rx1, ry)]
    for i in range(6):
        zig.append((rx1 + 14 + i * 18, ry - (12 if i % 2 == 0 else -12)))
    zig.append((rx1 + 14 + 6 * 18, ry))
    s += polyline(zig, INK, 2.6)
    s += line(rx1 - 34, ry, rx1, ry, INK, 2.6)
    s += line(rx1 + 14 + 6 * 18, ry, rx1 + 14 + 6 * 18 + 34, ry, INK, 2.6)
    s += text(rx1 + 50, ry - 26, "R", 14, INK, "middle", "bold", "italic")
    # хаотичні рухи всередині — стрілочки в різні боки
    random.seed(7)
    for _ in range(7):
        cx = rx1 + 18 + random.uniform(0, 90)
        cy = ry + random.uniform(-7, 7)
        a = random.uniform(0, 2 * math.pi)
        s += arrow(cx, cy, cx + 12 * math.cos(a), cy + 12 * math.sin(a), RED, 1.3)
    s += text(rx1 + 50, ry + 34, "хаотичний тепловий рух електронів", 9.5, RED, "middle", "bold")
    # тремтливий вольтметр (uV)
    s += circle(723, 290, 30, "#ffffff", BLUE, 2)
    s += text(723, 296, "µV", 13, BLUE, "middle", "bold")
    s += line(rx1 - 34, ry, 552, 290, BLUE, 2)
    s += line(552, 290, 693, 290, BLUE, 2)
    s += line(rx1 + 14 + 6 * 18 + 34, ry, 894, 290, BLUE, 2)
    s += line(894, 290, 753, 290, BLUE, 2)
    # шумова доріжка на «екрані»
    random.seed(3)
    pts = []
    for i in range(96):
        x = 560 + i * 3.7
        y = 358 + random.uniform(-16, 16)
        pts.append((x, y))
    s += polyline(pts, RED, 1.6)
    s += text(723, 384, "тонкий, але невпинний «трав'яний» шум", 10.5, BLUE, "middle", "bold")

    save("fig-r09-hist-2-johnson.svg", s)


# ── Рис. 1.9.0.3 — анатомія формули Найквіста: що від чого залежить ───────────
def fig_nyquist_formula():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 30, "Формула Найквіста: чотири множники — і жодного «номера деталі»",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "тепловий шум залежить лише від температури, опору й смуги — не від матеріалу чи бренду резистора",
              11, GREY, "middle", style="italic")

    # центральна формула
    fy = 120
    s += text(W / 2, fy, "Vшум(rms)  =  √( 4 · k · T · R · B )", 27, INK, "middle", "bold")

    # підписи-виноски до кожного символу
    def callout(x_sym, label1, label2, col, dy):
        sy = fy + 14
        ey = fy + dy
        s_loc = line(x_sym, sy, x_sym, ey - 14, col, 1.4, "4,3")
        s_loc += rect(x_sym - 96, ey - 14, 192, 56, "#ffffff", col, 1.6, 8)
        s_loc += text(x_sym, ey + 6, label1, 11, col, "middle", "bold")
        s_loc += text(x_sym, ey + 24, label2, 9.6, GREY, "middle")
        return s_loc

    # приблизні x під символами k, T, R, B
    s += callout(395, "k — стала Больцмана", "міст до температури; 1.38×10⁻²³", PURPLE, 95)
    s += callout(452, "T — абсолютна t°, K", "гарячіше → гучніше; вимкнути не можна", RED, 175)
    s += callout(510, "R — опір, Ω", "більший R → більший шум напруги", ORANGE, 95)
    s += callout(566, "B — смуга, Гц", "ширша смуга → більше шуму", GREEN, 175)

    # нижня смужка-висновок
    s += rect(120, 350, 720, 56, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 372, "Шум росте як √(T·R·B): щоб удвічі тихіше — учетверо вужча смуга, або вчетверо менший опір, або вчетверо холодніше.",
              11, INK, "middle", "bold")
    s += text(W / 2, 393, "Це фундаментальна межа: вона не залежить від того, чий резистор і з чого зроблений.",
              10.5, GREEN, "middle", "bold")
    save("fig-r09-hist-3-formula.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_what_johnson_saw()
    fig_nyquist_formula()
    print("done.")
