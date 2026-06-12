# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки 🔌 до теми 1.9.7 —
«Коаксіал і екранований сигнальний кабель: будова й де заземлювати екран» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: вставка 🔌 до теми 1.9.7 → секція 7c → Рис. 1.9.7c.N.
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


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 до теми 1.9.7 — екранований кабель.  Рис. 1.9.7c.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.7c.1 — будова коаксіалу: зрізаний шар за шаром + чому поле сидить усередині ──
def fig_coax_anatomy():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Коаксіал зсередини: чотири шари — і екран, що замикає поле в собі",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "сигнал біжить центральною жилою, повертається екраном; між ними — увесь струм і все поле",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: ступінчастий зріз кабелю (телескоп шарів) ──
    bx, by = 40, 78
    s += rect(bx, by, 470, 348, "#f8f8f8", GREY, 1.4, 12)
    s += text(bx + 235, by + 24, "Зріз: кожен шар відкриває наступний", 12.5, INK, "middle", "bold")

    cy = by + 195            # вісь кабелю
    x0 = bx + 28             # лівий край (повний переріз)
    seg = 84                 # довжина «сходинки» кожного шару

    # радіуси шарів (від зовнішнього до центрального)
    r_jacket = 92
    r_shield = 74
    r_diel = 56
    r_core = 16

    # 1) зовнішня оболонка (jacket) — повний відрізок зліва
    s += rect(x0, cy - r_jacket, seg, 2 * r_jacket, "#33363b", "#222", 1, 6)
    # 2) екран-обплетення (braid) — відкривається після оболонки
    x1 = x0 + seg
    s += rect(x1, cy - r_shield, seg, 2 * r_shield, COPPER, "#9c5f33", 1, 4)
    # штрихування «косичка» обплетення
    for i in range(7):
        xx = x1 + 6 + i * 11
        s += line(xx, cy - r_shield + 3, xx + 9, cy + r_shield - 3, "#9c5f33", 1)
        s += line(xx + 9, cy - r_shield + 3, xx, cy + r_shield - 3, "#9c5f33", 1)
    # 3) діелектрик — відкривається після екрана
    x2 = x1 + seg
    s += rect(x2, cy - r_diel, seg, 2 * r_diel, "#f1ece0", "#cbbf9e", 1, 4)
    # 4) центральна жила — до самого кінця
    x3 = x2 + seg
    x_end = x3 + seg + 8
    s += rect(x2, cy - r_core, x_end - x2, 2 * r_core, COPPER, "#9c5f33", 1, 3)

    # торцеві кільця (щоб читалось як циліндр)
    s += ellipse(x0, cy, 7, r_jacket, "#26282c", "#111", 1)
    s += ellipse(x1, cy, 6, r_shield, "#b06a39", "#9c5f33", 1)
    s += ellipse(x2, cy, 5, r_diel, "#e7e0cd", "#cbbf9e", 1)
    s += ellipse(x_end, cy, 4, r_core, "#b06a39", "#9c5f33", 1)

    # виноски-підписи до шарів
    s += line(x0 + seg / 2, cy - r_jacket, x0 + seg / 2, by + 40, "#33363b", 1, "3,3")
    s += text(x0 + seg / 2, by + 36, "оболонка", 10, "#33363b", "middle", "bold")
    s += text(x0 + seg / 2, by + 48, "(ізоляція)", 8.6, GREY, "middle")

    s += line(x1 + seg / 2, cy - r_shield, x1 + seg / 2, by + 64, "#9c5f33", 1, "3,3")
    s += text(x1 + seg / 2, by + 60, "ЕКРАН", 10.5, "#9c5f33", "middle", "bold")
    s += text(x1 + seg / 2, by + 72, "обплетення/фольга", 8.4, GREY, "middle")

    s += line(x2 + seg / 2, cy + r_diel, x2 + seg / 2, by + 330, "#a99a6e", 1, "3,3")
    s += text(x2 + seg / 2, by + 344, "діелектрик", 10, "#8a7b4e", "middle", "bold")

    s += line(x3 + seg / 2, cy + r_core, x3 + seg / 2, by + 312, "#9c5f33", 1, "3,3")
    s += text(x3 + 14, by + 326, "центральна жила (сигнал)", 10, "#9c5f33", "middle", "bold")

    # ── ПРАВА панель: переріз з полем, замкненим між жилою й екраном ──
    px, py = 528, 78
    s += rect(px, py, 432, 348, "#eef2fb", BLUE, 1.6, 12)
    s += text(px + 216, py + 24, "Переріз: усе поле — між жилою та екраном", 12.5, BLUE, "middle", "bold")

    ccx, ccy = px + 216, py + 188
    R_sh = 118
    R_di = 96
    R_co = 20

    # екран (кільце)
    s += circle(ccx, ccy, R_sh, "none", COPPER, 9)
    s += circle(ccx, ccy, R_sh + 6, "none", "#9c5f33", 1)
    s += circle(ccx, ccy, R_sh - 6, "none", "#9c5f33", 1)
    # діелектрик
    s += circle(ccx, ccy, R_di, "#f6f2e6", "#cbbf9e", 1)
    # центральна жила
    s += circle(ccx, ccy, R_co, COPPER, "#9c5f33", 1.5)
    s += text(ccx, ccy + 5, "+", 20, RED, "middle", "bold")

    # радіальні лінії поля від жили до екрана (всередину)
    for k in range(12):
        a = k * math.pi / 6
        rx0 = ccx + (R_co + 3) * math.cos(a)
        ry0 = ccy + (R_co + 3) * math.sin(a)
        rx1 = ccx + (R_di - 4) * math.cos(a)
        ry1 = ccy + (R_di - 4) * math.sin(a)
        s += arrow(rx0, ry0, rx1, ry1, RED, 1.4)

    # знаки «−» на внутрішньому боці екрана (повернений заряд)
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 6
        mx = ccx + (R_di + 6) * math.cos(a)
        my = ccy + (R_di + 6) * math.sin(a)
        s += text(mx, my + 4, "−", 15, BLUE, "middle", "bold")

    # «нуль зовні»
    s += text(ccx, py + 330, "Зовні екрана поля немає → сусід нічого не наводить",
              10.5, GREEN, "middle", "bold")
    s += text(ccx + R_sh + 4, ccy - R_sh + 4, "екран", 9.5, "#9c5f33", "start", "bold")

    save("fig-r09-s7c-1-coax-anatomy.svg", s)


# ── Рис. 1.9.7c.2 — головне рішення: де заземлювати екран (один кінець vs обидва) ──
def fig_where_to_ground():
    W, H = 1010, 560
    s = header(W, H)
    s += text(W / 2, 30, "Головне питання екрана: заземлити з одного кінця чи з обох?",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "відповідь залежить від частоти завади — і це той самий компроміс земляної петлі, що в §1.9.6",
              11.5, GREY, "middle", style="italic")

    # допоміжне: «земля» (трикутник)
    def gnd(x, y, col=INK, sc=1.0):
        g = line(x, y, x, y + 10 * sc, col, 2)
        g += line(x - 13 * sc, y + 10 * sc, x + 13 * sc, y + 10 * sc, col, 2.4)
        g += line(x - 8 * sc, y + 15 * sc, x + 8 * sc, y + 15 * sc, col, 2)
        g += line(x - 4 * sc, y + 20 * sc, x + 4 * sc, y + 20 * sc, col, 2)
        return g

    # коробочка приладу
    def box(x, y, w, h, label, sub):
        b = rect(x, y, w, h, "#ffffff", INK, 1.8, 8)
        b += text(x + w / 2, y + h / 2 - 3, label, 12, INK, "middle", "bold")
        b += text(x + w / 2, y + h / 2 + 14, sub, 9.5, GREY, "middle")
        return b

    # ── ВЕРХНЯ панель: один кінець (single-point) ──
    ty = 70
    s += rect(30, ty, 950, 220, "#f4faf5", GREEN, 1.6, 12)
    s += text(50, ty + 24, "А. Заземлити З ОДНОГО кінця (звичайно — біля джерела)",
              13.5, GREEN, "start", "bold")

    yA = ty + 120
    s += box(70, yA - 40, 150, 80, "ДАВАЧ", "джерело сигналу")
    s += box(760, yA - 40, 150, 80, "АЦП / МК", "приймач")

    # центральна жила
    s += line(220, yA - 16, 760, yA - 16, COPPER, 3)
    s += text(490, yA - 26, "сигнал (центральна жила)", 10, "#9c5f33", "middle", "bold")
    # екран
    s += line(220, yA + 14, 760, yA + 14, GREY, 4)
    s += text(490, yA + 30, "екран", 10, GREY, "middle", "bold")
    # заземлення лише зліва
    s += line(220, yA + 14, 150, yA + 14, GREY, 4)
    s += line(150, yA + 14, 150, yA + 40, GREY, 2)
    s += gnd(150, yA + 40, GREEN)
    # правий кінець — обрив (НЕ заземлено)
    s += circle(770, yA + 14, 4, "#fff", RED, 2)
    s += text(800, yA + 14, "✗ не з'єднано", 10, RED, "start", "bold")

    # стрілка завадного струму — НЕ тече (петлі нема)
    s += text(490, yA + 56, "земляної петлі немає → струм 50 Гц екраном не біжить → нема гулу",
              10.5, GREEN, "middle", "bold")
    s += text(490, ty + 200, "Найкраще для аналогу, аудіо, повільних давачів (де головна біда — гул мережі та петлі §1.9.6)",
              10, INK, "middle", style="italic")

    # ── НИЖНЯ панель: обидва кінці (both-ends) ──
    by = ty + 240
    s += rect(30, by, 950, 220, "#eef2fb", BLUE, 1.6, 12)
    s += text(50, by + 24, "Б. Заземлити З ОБОХ кінців",
              13.5, BLUE, "start", "bold")

    yB = by + 120
    s += box(70, yB - 40, 150, 80, "ПЕРЕДАВАЧ", "ВЧ-джерело")
    s += box(760, yB - 40, 150, 80, "ПРИЙМАЧ", "ВЧ-вхід")
    s += line(220, yB - 16, 760, yB - 16, COPPER, 3)
    s += text(490, yB - 26, "сигнал (центральна жила)", 10, "#9c5f33", "middle", "bold")
    s += line(220, yB + 14, 760, yB + 14, GREY, 4)
    # заземлення з обох боків
    s += line(220, yB + 14, 150, yB + 14, GREY, 4)
    s += line(150, yB + 14, 150, yB + 40, GREY, 2)
    s += gnd(150, yB + 40, BLUE)
    s += line(760, yB + 14, 830, yB + 14, GREY, 4)
    s += line(830, yB + 14, 830, yB + 40, GREY, 2)
    s += gnd(830, yB + 40, BLUE)

    # земляна петля (струм біжить екраном) + ВЧ-завада, яку це гасить
    s += arrow(360, yB + 14, 300, yB + 14, RED, 2)
    s += arrow(620, yB + 14, 680, yB + 14, RED, 2)
    s += text(490, yB + 33, "↺ можлива петля 50 Гц (мінус)", 9.5, RED, "middle", "bold")
    # ВЧ-поле, від якого екран рятує лише при обох кінцях
    for i in range(5):
        xx = 300 + i * 100
        s += arrow(xx, yB - 58, xx, yB - 36, PURPLE, 1.4, "3,2")
    s += text(490, yB - 64, "ВЧ-наводка / магнітне поле", 9.5, PURPLE, "middle", "bold")
    s += text(490, by + 200, "Потрібно для ВЧ і магнітних завад: при обох кінцях екран замикає струм наводки в собі (плюс)",
              10, INK, "middle", style="italic")

    save("fig-r09-s7c-2-where-to-ground.svg", s)


if __name__ == "__main__":
    fig_coax_anatomy()
    fig_where_to_ground()
    print("done.")
