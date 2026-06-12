# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до теми 1.9.4 —
«Гул у слухавці: як телефоністи воювали з силовими лініями» (Модуль 1, Розділ 1.9).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: історія до теми 1.9.4 → Рис. 1.9.4і.N.
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
#  Історія до теми 1.9.4 — телефон vs силова лінія.  Рис. 1.9.4і.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.4і.1 — два шляхи наводки + чому однопровідна лінія беззахисна ─────
def fig_two_couplings():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Силова лінія вгорі — телефонна внизу: двома шляхами вона нав'язує свій 50/60-герцовий ритм",
              17, INK, "middle", "bold")
    s += text(W / 2, 51, "електричне поле наводить заряд (ємнісно), магнітне поле наводить струм у петлі (індуктивно)",
              11, GREY, "middle", style="italic")

    # силовий провід (зверху)
    px0, px1, py = 90, 910, 110
    s += line(px0, py, px1, py, ORANGE, 4)
    s += text(px0 - 8, py - 12, "силова лінія ~", 12, ORANGE, "start", "bold")
    s += text(px1, py - 12, "I(t), 50/60 Гц", 11.5, ORANGE, "end", "bold")
    # позначки змінного струму вздовж проводу
    for fx in (0.30, 0.55, 0.80):
        x = px0 + (px1 - px0) * fx
        s += text(x, py - 11, "→ ~ →", 10.5, ORANGE, "middle")

    # ── ЛІВА половина: ємнісний (електростатичний) зв'язок ──
    s += rect(70, 150, 410, 280, "#f3faf4", GREEN, 1.6, 12)
    s += text(275, 176, "1) Електричне поле — ємнісний зв'язок", 13, GREEN, "middle", "bold")
    # лінії поля від силового проводу до телефонного (зелені пунктири з '+')
    tly = 360
    for fx in (0.18, 0.30, 0.42):
        x = 70 + 410 * fx
        s += line(x, py + 6, x, tly - 6, GREEN, 1.5, "5,4")
        s += polygon([(x, tly - 6), (x - 4, tly - 16), (x + 4, tly - 16)], GREEN)
    s += text(150, 250, "E", 15, GREEN, "middle", "bold", "italic")
    s += text(290, 244, "поле штовхає заряд", 10, GREEN, "middle")
    s += text(290, 258, "на телефонний провід", 10, GREEN, "middle")
    # телефонний провід (один) внизу лівої панелі
    s += line(95, tly, 455, tly, COPPER, 3.4)
    s += text(95, tly + 20, "телефонний провід", 10.5, COPPER, "start", "bold")
    # наведений '+' заряд
    for fx in (0.20, 0.32, 0.44):
        x = 70 + 410 * fx
        s += circle(x, tly, 5.5, "#ffffff", RED, 1.6)
        s += text(x, tly + 3.5, "+", 11, RED, "middle", "bold")
    s += text(420, tly + 20, "наведений заряд", 9.5, RED, "end")

    # ── ПРАВА половина: індуктивний (магнітний) зв'язок ──
    s += rect(520, 150, 410, 280, "#eef2fb", BLUE, 1.8, 12)
    s += text(725, 176, "2) Магнітне поле — індуктивний зв'язок", 13, BLUE, "middle", "bold")
    # кружечки магнітного поля навколо силового проводу (×/•)
    for fx in (0.16, 0.30, 0.44, 0.58):
        x = 520 + 410 * fx
        s += circle(x, py, 15, "none", BLUE, 1.3)
        s += text(x, py + 4, "×", 11, BLUE, "middle", "bold")
    s += text(725, py + 34, "B(t) охоплює петлю внизу", 10, BLUE, "middle", "bold")
    # телефонна ПЕТЛЯ (два дроти + замикання) — підкреслюємо площу
    lx0, lx1, lyA, lyB = 565, 885, 330, 392
    s += line(lx0, lyA, lx1, lyA, COPPER, 3)
    s += line(lx0, lyB, lx1, lyB, COPPER, 3)
    s += line(lx0, lyA, lx0, lyB, COPPER, 3)
    s += line(lx1, lyA, lx1, lyB, COPPER, 3)
    # заштрихувати площу петлі
    s += rect(lx0, lyA, lx1 - lx0, lyB - lyA, "#dfe7fa", "none", 0)
    s += line(lx0, lyA, lx1, lyA, COPPER, 3)  # перемалювати верх над заливкою
    s += line(lx0, lyB, lx1, lyB, COPPER, 3)
    s += line(lx0, lyA, lx0, lyB, COPPER, 3)
    s += line(lx1, lyA, lx1, lyB, COPPER, 3)
    s += text(725, (lyA + lyB) / 2 + 4, "площа петлі A", 10.5, BLUE, "middle", "bold")
    # наведений струм по петлі (стрілки)
    s += arrow(lx0 + 40, lyA, lx0 + 120, lyA, RED, 1.8)
    s += arrow(lx1 - 40, lyB, lx1 - 120, lyB, RED, 1.8)
    s += text(725, lyB + 20, "наведений струм у петлі  (∝ площі × швидкості зміни B)", 9.5, RED, "middle", "bold")

    save("fig-r09-s4i-1-two-couplings.svg", s)


# ── Рис. 1.9.4і.2 — лінія часу «війни» + модель координації трьох множників ───
def fig_timeline_coordination():
    W, H = 1000, 500
    s = header(W, H)
    s += text(W / 2, 30, "Сорок років боротьби: від однопровідної лінії з гулом — до спільних правил",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "спершу судилися, потім сіли за стіл: завада кориться трьом множникам, і тиснути треба на всі три",
              11, GREY, "middle", style="italic")

    ax, ay, aw = 70, 210, 860
    s += line(ax, ay, ax + aw, ay, INK, 2.2)
    s += polygon([(ax + aw, ay), (ax + aw - 14, ay - 6), (ax + aw - 14, ay + 6)], INK)
    s += text(ax + aw + 6, ay + 5, "час", 11.5, INK, "start", "bold")

    # (частка, дата, рядок1, рядок2, колір, вгору?)
    events = [
        (0.04, "1880-ті", "Однопровідні лінії", "повернення через землю — усе чути", GREY, True),
        (0.205, "1881", "Белл: пара дротів", "металеве коло замість землі (патент)", COPPER, False),
        (0.37, "1889-91", "Дж. Дж. Карті", "діагноз: винна ємність; транспозиція", GREEN, True),
        (0.55, "1890-1910", "Трамваї та силові мережі", "однопровідні лінії масово гинуть", ORANGE, False),
        (0.72, "1912", "Каліфорнія, наказ №52", "комісія замість суду", PURPLE, True),
        (0.92, "1921+", "NELA + AT&T, залізниці", "спільні комітети: координація", BLUE, False),
    ]
    for frac, date, l1, l2, col, up in events:
        x = ax + aw * frac
        s += circle(x, ay, 6.5, col, col, 1)
        if up:
            s += line(x, ay - 6, x, ay - 40, col, 1.4, "4,3")
            box_y = ay - 40 - 56
            s += rect(x - 86, box_y, 172, 52, "#ffffff", col, 1.5, 8)
            s += text(x, box_y + 17, date, 11.5, col, "middle", "bold")
            s += text(x, box_y + 32, l1, 10, INK, "middle", "bold")
            s += text(x, box_y + 46, l2, 8.4, GREY, "middle")
        else:
            s += line(x, ay + 6, x, ay + 40, col, 1.4, "4,3")
            box_y = ay + 40
            s += rect(x - 86, box_y, 172, 52, "#ffffff", col, 1.5, 8)
            s += text(x, box_y + 17, date, 11.5, col, "middle", "bold")
            s += text(x, box_y + 32, l1, 10, INK, "middle", "bold")
            s += text(x, box_y + 46, l2, 8.4, GREY, "middle")

    # ── нижня смуга: модель трьох множників ──
    by = 372
    s += text(W / 2, by, "Чому завада взагалі є — добуток трьох множників (модель координації):", 12.5, INK, "middle", "bold")
    boxes = [
        (170, "Вплив", "influence", "як «брудно» шумить\nсилова лінія", ORANGE),
        (500, "Сприйнятливість", "susceptiveness", "як легко телефон\nцей шум ловить", COPPER),
        (830, "Зв'язок", "coupling", "геометрія: відстань,\nпаралельність, площа", BLUE),
    ]
    for cx, t1, t2, t3, col in boxes:
        s += rect(cx - 130, by + 16, 260, 70, "#fbfbfb", col, 1.7, 10)
        s += text(cx, by + 38, t1, 13, col, "middle", "bold")
        s += text(cx, by + 54, "(" + t2 + ")", 9.5, GREY, "middle", style="italic")
        for i, ln in enumerate(t3.split("\n")):
            s += text(cx, by + 70 + i * 12, ln, 9.2, INK, "middle")
    # знаки множення
    s += text(335, by + 56, "×", 22, INK, "middle", "bold")
    s += text(665, by + 56, "×", 22, INK, "middle", "bold")
    s += text(W / 2, by + 104, "Завада = Вплив × Сприйнятливість × Зв'язок — занулиш будь-який множник, і гул зникне.",
              10.8, GREEN, "middle", "bold")

    save("fig-r09-s4i-2-timeline-coordination.svg", s)


if __name__ == "__main__":
    fig_two_couplings()
    fig_timeline_coordination()
    print("done.")
