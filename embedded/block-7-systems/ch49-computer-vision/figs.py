#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 49 (Модуль 7) — чистий Python, без залежностей.
Запуск:  python figs.py    →    кладе *.svg у ./img/

Стиль (єдиний для курсу; спільні допоміжні функції копіюються у кожен chNN/figs.py):
  білий фон; «+» червоний, «−» синій; поле — зелене; стрілки через marker;
  шрифт sans-serif. Підписи фігур у тексті — посекційно «Рис. C.S.N».
"""

import os
import math

# ── палітра ───────────────────────────────────────────────────────────────
INK   = "#1a1a1a"
MUTE  = "#6b7280"
RED   = "#cc0000"
BLUE  = "#1f4ed8"
GREEN = "#0a8f3c"
AMBER = "#d98a00"
SKY   = "#dbeafe"
GND   = "#dcfce7"
PANEL = "#f4f4f5"
BOX1  = "#eef2ff"
BOX2  = "#eafaef"
BOX3  = "#fff5e6"
FONT  = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def header(w, h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
     viewBox="0 0 {w} {h}" font-family="{FONT}">
  <defs>
    <marker id="arr" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{INK}"/></marker>
    <marker id="arrR" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{RED}"/></marker>
    <marker id="arrB" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{BLUE}"/></marker>
    <marker id="arrG" markerWidth="9" markerHeight="9" refX="7.5" refY="4"
            orient="auto" markerUnits="userSpaceOnUse">
      <path d="M0,0 L8,4 L0,8 Z" fill="{GREEN}"/></marker>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" fill="white"/>
'''


def footer():
    return "</svg>\n"


def text(x, y, s, size=14, fill=INK, anchor="start", weight="normal",
         italic=False, family=None):
    st = "italic" if italic else "normal"
    fam = f' font-family="{family}"' if family else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{st}"{fam}>{esc(s)}</text>\n')


def lines(x, y, rows, size=13, fill=INK, anchor="start", lh=16, weight="normal",
          family=None):
    out = ""
    for i, r in enumerate(rows):
        out += text(x, y + i * lh, r, size=size, fill=fill, anchor=anchor,
                    weight=weight, family=family)
    return out


def line(x1, y1, x2, y2, stroke=INK, w=1.6, dash=None, marker=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{w}"{d}{m} stroke-opacity="{opacity}" '
            f'stroke-linecap="round"/>\n')


def rect(x, y, w, h, fill="white", stroke=INK, sw=1.6, rx=8, dash=None,
         opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="white", stroke=INK, sw=1.6, opacity=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def poly(pts, fill="none", stroke=INK, sw=1.6, closed=True, opacity=1.0):
    tag = "polygon" if closed else "polyline"
    p = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>\n')


def title(w, s, sub=None):
    out = text(w / 2, 30, s, size=18, anchor="middle", weight="bold")
    if sub:
        out += text(w / 2, 50, sub, size=13, anchor="middle", fill=MUTE)
    return out


def coil(x1, x2, y, n=4, col=INK):
    """Котушка: n півкіл-горбиків угору."""
    w = (x2 - x1) / n
    p = f'M {x1} {y} '
    for _ in range(n):
        p += f'q {w / 2} {-w * 0.85} {w} 0 '
    return f'<path d="{p}" fill="none" stroke="{col}" stroke-width="2.2"/>\n'


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.0.1 — Літо 1966-го
# ════════════════════════════════════════════════════════════════════════════
def fig_summer_1966():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Літо 1966-го: «розв'яжемо зір за канікули»",
               "у MIT гадали, що навчити машину бачити — справа на одне літо; вийшов науковий напрям на десятиліття")
    s += rect(80, 110, 300, 180, fill="#fffef7", stroke=INK, sw=1.6, rx=6)
    s += rect(80, 110, 300, 32, fill=BOX3, stroke="none", rx=6)
    s += text(230, 131, "MIT · Project MAC · AI Group", size=10,
              anchor="middle", weight="bold")
    s += text(100, 164, "THE SUMMER VISION PROJECT", size=12, weight="bold")
    s += text(100, 183, "Seymour Papert · 7 липня 1966", size=9.5, fill=MUTE)
    s += lines(100, 208, ["Мета: за літо зробити систему,",
                          "що поділить кадр на об'єкти", "й тло — і назве прості тіла.",
                          "Координує Джеральд Сассмен", "(студент) з гуртом студентів."],
               size=9.5, lh=17)
    s += line(398, 200, 466, 200, stroke=INK, w=2, marker="arr")
    s += text(700, 126, "а насправді…", size=12, anchor="middle", weight="bold",
              fill=RED)
    s += line(500, 200, 900, 200, stroke=MUTE, w=2)
    for x, lab, col in [(520, "1966\nліто", GREEN), (640, "1980-ті", AMBER),
                        (770, "2010-ті", AMBER), (885, "досі", RED)]:
        s += circle(x, 200, 5, fill=col, stroke=INK, sw=1)
        for j, ln in enumerate(lab.split("\n")):
            s += text(x, 222 + j * 13, ln, size=9, anchor="middle", fill=col,
                      weight="bold")
    s += text(700, 262, "те, що думали зробити за літо,", size=10,
              anchor="middle", fill=MUTE)
    s += text(700, 277, "будують і досі — це ціла наука", size=10,
              anchor="middle", fill=MUTE)
    s += rect(80, 320, 800, 92, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 344,
              "Чому ця історія — на початку розділу про машинне бачення?",
              size=11, anchor="middle", weight="bold")
    s += lines(118, 366,
               ["Бо це найвідоміший урок про те, що «очевидне» для людини буває страшенно важким для машини.",
                "Саме з цього невдалого літа й виріс увесь напрям, ази якого ми пройдемо в цьому розділі."],
               size=9.8, lh=18)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.0.2 — Семантична прірва
# ════════════════════════════════════════════════════════════════════════════
def fig_semantic_gap():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому здавалося легко: пастка «я ж бачу одразу»",
               "людині здається, що бачити — просто; та машині дано лише числа-пікселі, а не «це куб на столі»")
    s += rect(70, 110, 360, 250, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(250, 134, "що бачить ЛЮДИНА", size=12, anchor="middle",
              weight="bold", fill=BLUE)
    s += rect(110, 278, 280, 14, fill="#94a3b8", stroke="none")
    s += rect(152, 230, 58, 48, fill="#f59e0b", stroke=INK, sw=1.4)
    s += circle(300, 254, 25, fill="#60a5fa", stroke=INK, sw=1.4)
    s += text(181, 316, "куб", size=10, anchor="middle", weight="bold")
    s += text(300, 316, "м'яч", size=10, anchor="middle", weight="bold")
    s += text(250, 342, "«куб і м'яч на столі» — умить, без зусиль", size=9.5,
              anchor="middle", fill=MUTE)
    s += rect(530, 110, 360, 250, fill=PANEL, stroke=AMBER, sw=1.8, rx=12)
    s += text(710, 134, "що дано МАШИНІ", size=12, anchor="middle",
              weight="bold", fill="#b06b00")
    gx, gy, cell = 556, 150, 33
    vals = [[137, 140, 139, 141, 138, 142, 140, 138],
            [138, 139, 250, 251, 249, 250, 141, 139],
            [139, 251, 252, 250, 248, 250, 252, 138],
            [140, 250, 249, 251, 250, 249, 251, 141],
            [141, 139, 140, 250, 251, 250, 141, 140],
            [139, 140, 141, 139, 138, 140, 142, 139]]
    for r in range(6):
        for c in range(8):
            v = vals[r][c]
            s += text(gx + c * cell + cell / 2, gy + r * cell + 17, str(v),
                      size=8.5, anchor="middle",
                      fill=("#b06b00" if v > 200 else "#94a3b8"))
    s += rect(gx, gy, 8 * cell, 6 * cell, fill="none", stroke="#cbd5e1", sw=1)
    s += text(710, 342, "лише сітка чисел-яскравостей — і ні слова про «куб»",
              size=9.5, anchor="middle", fill=MUTE)
    s += text(480, 248, "?", size=44, anchor="middle", weight="bold", fill=RED)
    s += text(480, 392, "семантична прірва", size=12, anchor="middle",
              weight="bold", fill=RED)
    s += text(W / 2, H - 30,
              "Машина не «бачить» куб — вона має лише числа. Перетворити числа на "
              "зміст і є вся задача машинного бачення.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Те, що мозок робить непомітно, машині треба збудувати покроково — "
              "від пікселя до поняття.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.0.3 — Що замовили: ланцюг до названих тіл
# ════════════════════════════════════════════════════════════════════════════
def fig_project_goals():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Що насправді замовили: від пікселів до названих тіл",
               "поділити кадр на області (об'єкт / тло / хаос), описати їх — і назвати прості тіла на однорідному тлі")
    stages = [("кадр", ["сирий знімок", "з камери", "(vidisector)"], BLUE, 0),
              ("фігура / тло", ["відділити", "об'єкти", "від тла"], AMBER, 1),
              ("області", ["об'єкт ·", "тло ·", "хаос"], AMBER, 2),
              ("назвати", ["куб, м'яч,", "циліндр", "(прості тіла)"], GREEN, 3)]
    bw, bh, y, x0, gap = 190, 150, 150, 40, 30
    for t, rows, col, kind in stages:
        x = x0 + kind * (bw + gap)
        s += rect(x, y, bw, bh, fill="#0f172a", stroke=col, sw=2.0, rx=10)
        s += text(x + bw / 2, y + 26, t, size=12.5, anchor="middle",
                  weight="bold", fill=col)
        cx = x + bw / 2
        if kind == 0:
            for a in range(4):
                for b in range(6):
                    s += rect(cx - 30 + b * 10, y + 46 + a * 10, 9, 9,
                              fill=f"rgb({130 + (a * 7 + b * 11) % 80},"
                                   f"{130 + (a * 5 + b * 9) % 80},"
                                   f"{135 + (a * 9 + b * 7) % 70})", stroke="none")
        elif kind == 1:
            s += rect(cx - 30, y + 46, 60, 40, fill="#1e293b", stroke="none")
            s += rect(cx - 14, y + 54, 30, 26, fill="none", stroke=AMBER, sw=2,
                      dash="3,2")
        elif kind == 2:
            s += rect(cx - 30, y + 46, 60, 40, fill="#334155", stroke="none")
            s += rect(cx - 12, y + 52, 26, 28, fill="#f59e0b", stroke="white",
                      sw=1)
        else:
            s += rect(cx - 16, y + 48, 32, 34, fill="#f59e0b", stroke="white",
                      sw=1.2)
            s += text(cx, y + 70, "✓", size=15, anchor="middle", weight="bold",
                      fill="white")
        for j, ln in enumerate(rows):
            s += text(cx, y + 110 + j * 15, ln, size=9.5, anchor="middle",
                      fill="#e2e8f0")
        if kind < 3:
            s += line(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, stroke=INK,
                      w=1.8, marker="arr")
    s += rect(40, 330, 880, 72, fill="#fff5f5", stroke=RED, sw=1.4, rx=10)
    s += text(480, 354,
              "Кожна стрілка тут — окрема велика задача (і кожна стала окремою темою цього розділу).",
              size=10.5, anchor="middle", weight="bold")
    s += text(480, 377,
              "Команда думала пройти весь ланцюг за літо. Перша ж ланка — «де об'єкт, а де тло» — виявилась проваллям.",
              size=9.8, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.0.4 — Дорожня карта Розділу 49
# ════════════════════════════════════════════════════════════════════════════
def fig_roadmap():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Зір виявився не задачею, а наукою",
               "те, що думали зробити за літо, будують досі; а ми пройдемо його ази — від пікселя до керування")

    def card(x, y, num, l1, l2, col):
        o = rect(x, y, 160, 84, fill=PANEL, stroke=col, sw=1.7, rx=10)
        o += rect(x, y, 48, 84, fill=col, stroke="none", rx=10, opacity=0.16)
        o += text(x + 24, y + 47, num, size=12, anchor="middle", weight="bold",
                  fill=col)
        o += text(x + 58, y + 36, l1, size=9.5)
        o += text(x + 58, y + 54, l2, size=9.5)
        return o
    r1 = [(40, "49.1", "піксель,", "канали"), (220, "49.2", "яскравість,", "гістограма"),
          (400, "49.3", "згортки,", "фільтри"), (580, "49.4", "межі:", "Собель/Канні"),
          (760, "49.5", "пороги,", "морфологія")]
    cols1 = [BLUE, BLUE, AMBER, AMBER, AMBER]
    for k, (x, num, l1, l2) in enumerate(r1):
        s += card(x, 128, num, l1, l2, cols1[k])
        if k < 4:
            s += line(x + 160, 170, x + 180, 170, stroke=INK, w=1.6,
                      marker="arr")
    s += line(840, 212, 840, 288, stroke=INK, w=1.6, marker="arr")
    r2 = [(760, "49.6", "об'єкти:", "форма/Хаф"), (540, "49.7", "нейро-", "детектори"),
          (320, "49.8", "трекінг →", "керування"), (100, "49.9", "вартість", "обчислень")]
    cols2 = [AMBER, GREEN, GREEN, GREEN]
    for k, (x, num, l1, l2) in enumerate(r2):
        s += card(x, 290, num, l1, l2, cols2[k])
        if k < 3:
            s += line(x, 332, x - 40, 332, stroke=INK, w=1.6, marker="arr")
    s += text(620, 304, "📜 49.7: окрема історія нейромереж", size=8.5,
              anchor="start", fill=MUTE)
    s += rect(40, 392, 880, 60, fill="#eef2ff", stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 416,
              "Дев'ять кроків від голих чисел-пікселів до того, щоб «піксель став кутом» і замкнув керування.",
              size=10.5, anchor="middle", weight="bold")
    s += text(480, 437,
              "Те, що 1966-го гадали зробити за літо. Ми пройдемо ці ази по черзі.",
              size=9.8, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.1.1 — Зображення як сітка чисел
# ════════════════════════════════════════════════════════════════════════════
def fig_image_as_grid():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Зображення — це сітка чисел",
               "піксель (picture element) — атом картинки; усе зображення — матриця яскравостей, а зір — математика над нею")
    s += text(150, 108, "фото", size=11, anchor="middle", weight="bold")
    for i in range(10):
        s += rect(70, 124 + i * 12, 160, 12,
                  fill=f"rgb({100 + i * 6},{140 + i * 8},210)", stroke="none")
    s += circle(178, 150, 17, fill="#fde68a", stroke="none")
    s += rect(70, 124, 160, 120, fill="none", stroke=INK, sw=1.4)
    s += rect(150, 196, 26, 26, fill="none", stroke=RED, sw=1.8)
    s += line(176, 209, 298, 184, stroke=RED, w=1.2, dash="3,2")
    s += text(360, 108, "пікселі (зблизька)", size=11, anchor="middle",
              weight="bold")
    gx, gy, cell = 300, 124, 20
    for r in range(6):
        for c in range(6):
            v = max(0, min(255, 90 + r * 18 + c * 8))
            s += rect(gx + c * cell, gy + r * cell, cell, cell,
                      fill=f"rgb({v},{v},{v})", stroke="#cbd5e1", sw=0.4)
    s += rect(gx, gy, 120, 120, fill="none", stroke=INK, sw=1.4)
    s += line(gx + 126, gy + 60, gx + 162, gy + 60, stroke=INK, w=1.5,
              marker="arr")
    s += text(700, 108, "ті самі пікселі — числа 0…255", size=11,
              anchor="middle", weight="bold")
    nx, ny = 488, 124
    for r in range(6):
        for c in range(6):
            v = max(0, min(255, 90 + r * 18 + c * 8))
            s += rect(nx + c * 34, ny + r * 20, 34, 20, fill="white",
                      stroke="#e5e7eb", sw=0.6)
            s += text(nx + c * 34 + 17, ny + r * 20 + 14, str(v), size=8.5,
                      anchor="middle", fill=INK)
    s += rect(nx, ny, 204, 120, fill="none", stroke=INK, sw=1.2)
    s += text(150, 262, "роздільність = W×H пікселів", size=9.5,
              anchor="middle", fill=MUTE)
    s += rect(70, 296, 820, 100, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 320,
              "Кожен піксель — просто число (тут — яскравість 0…255; 0 — чорне, 255 — біле).",
              size=11, anchor="middle", weight="bold")
    s += lines(150, 344,
               ["• будь-яка операція зору (розмиття, межі, пошук) — це арифметика над цією матрицею;",
                "• адресуємо піксель як [рядок, стовпець]; зрушити, додати, порівняти — усе це дії над числами."],
               size=9.8, lh=19)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.1.2 — Канали
# ════════════════════════════════════════════════════════════════════════════
def fig_channels():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Канали: колір — це кілька сіток разом",
               "кольоровий піксель — не одне число, а кілька; RGB — три канали (R, G, B), кожен — своя сіра мапа; разом дають колір")

    def rgb_at(r, c):
        d = abs(r - 2) + abs(c - 2)
        if d <= 1:
            return (240, 150, 40)
        if d == 2:
            return (150, 100, 55)
        return (40, 42, 62)

    def grid(x, label, col, sel):
        out = text(x + 50, 120, label, size=11, anchor="middle", weight="bold",
                   fill=col)
        for r in range(5):
            for c in range(5):
                R, G, B = rgb_at(r, c)
                if sel == "R":
                    f = f"rgb({R},{R},{R})"
                elif sel == "G":
                    f = f"rgb({G},{G},{G})"
                elif sel == "B":
                    f = f"rgb({B},{B},{B})"
                else:
                    f = f"rgb({R},{G},{B})"
                out += rect(x + c * 20, 132 + r * 20, 20, 20, fill=f,
                            stroke="#cbd5e1", sw=0.4)
        out += rect(x, 132, 100, 100, fill="none", stroke=col, sw=2)
        return out
    s += grid(80, "канал R", RED, "R")
    s += text(196, 188, "+", size=20, anchor="middle", weight="bold")
    s += grid(230, "канал G", GREEN, "G")
    s += text(346, 188, "+", size=20, anchor="middle", weight="bold")
    s += grid(380, "канал B", BLUE, "B")
    s += text(496, 188, "=", size=20, anchor="middle", weight="bold")
    s += grid(590, "колір", INK, "RGB")
    s += text(640, 250, "кожен канал — «скільки» одного основного кольору (0…255)",
              size=9.5, anchor="middle", fill=MUTE)
    s += rect(80, 290, 800, 110, fill=BOX1, stroke=BLUE, sw=1.4, rx=11)
    s += text(480, 314, "Що варто запам'ятати про канали", size=11,
              anchor="middle", weight="bold", fill=BLUE)
    s += lines(110, 338,
               ["• кольорове зображення = три сірі мапи (R, G, B) одна над одною → форма H×W×3;",
                "• відтінок сірого = 1 канал (утричі менше даних — часто цього досить для форм і меж);",
                "• «глибина» 8 біт → значення 0…255 на канал; буває 10–12 біт (ширший діапазон, 47)."],
               size=9.8, lh=21)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.1.3 — Колірні простори
# ════════════════════════════════════════════════════════════════════════════
def fig_color_spaces():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Колірні простори: різні способи записати той самий колір",
               "RGB — як у сенсора й екрана; HSV — окремо тон/насиченість/яскравість; YUV — яскравість + колірність")
    s += text(W / 2, 84, "той самий піксель", size=10.5, anchor="middle",
              fill=MUTE)
    s += rect(442, 92, 76, 24, fill="rgb(240,140,20)", stroke=INK, sw=1.2, rx=5)
    s += text(W / 2, 134, "…записаний трьома способами:", size=10,
              anchor="middle", fill=MUTE)
    cols = [
        ("RGB", BLUE, [("R", "240"), ("G", "140"), ("B", "20")],
         ["адитивний; як сенсор і екран.", "Яскравість «розмазана» по всіх",
          "трьох — погано шукати колір."]),
        ("HSV", GREEN, [("H тон", "32°"), ("S насич.", "92%"), ("V яскр.", "94%")],
         ["тон ОКРЕМО від яскравості →", "знайти колір легко й стійко до",
          "світла. Найкраще для зору!"]),
        ("YUV / YCbCr", AMBER, [("Y яскр.", "178"), ("U / Cb", "−60"), ("V / Cr", "+70")],
         ["яскравість окремо від кольору →", "відео й JPEG (47.3, 48.2);",
          "око бачить Y докладніше."]),
    ]
    x0, cw, gap = 70, 270, 20
    for i, (name, col, rowsv, note) in enumerate(cols):
        x = x0 + i * (cw + gap)
        s += rect(x, 156, cw, 208, fill=PANEL, stroke=col, sw=1.9, rx=12)
        s += text(x + cw / 2, 182, name, size=13, anchor="middle",
                  weight="bold", fill=col)
        for j, (k, v) in enumerate(rowsv):
            yy = 210 + j * 28
            s += text(x + 26, yy, k, size=10.5)
            s += text(x + cw - 26, yy, v, size=11, anchor="end", weight="bold",
                      fill=col)
        s += line(x + 18, 302, x + cw - 18, 302, stroke="#e5e7eb", w=1)
        s += lines(x + 20, 320, note, size=8.8, lh=14)
    s += text(W / 2, H - 14,
              "Колір не міняється — міняється ЗАПИС. Обирай простір так, щоб "
              "задача стала легкою: HSV для кольору, сіре для форми.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.1.4 — Чому HSV для зору
# ════════════════════════════════════════════════════════════════════════════
def fig_hsv_for_vision():
    import colorsys
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому для зору беруть HSV, а не RGB",
               "знайти «помаранчевий м'яч»: у RGB світло зрушує всі три числа; у HSV тон майже не міняється")
    s += rect(60, 110, 400, 250, fill="#fef2f2", stroke=RED, sw=1.8, rx=12)
    s += text(260, 134, "у RGB — важко", size=12.5, anchor="middle",
              weight="bold", fill=RED)
    s += circle(150, 196, 30, fill="rgb(250,150,40)", stroke=INK, sw=1.2)
    s += text(150, 240, "яскраве світло", size=9, anchor="middle", fill=MUTE)
    s += text(150, 256, "R250 G150 B40", size=9.5, anchor="middle",
              weight="bold")
    s += circle(360, 196, 30, fill="rgb(120,70,18)", stroke=INK, sw=1.2)
    s += text(360, 240, "тьмяне світло", size=9, anchor="middle", fill=MUTE)
    s += text(360, 256, "R120 G70 B18", size=9.5, anchor="middle",
              weight="bold")
    s += text(260, 298, "усі три числа поповзли!", size=10, anchor="middle",
              fill=RED, weight="bold")
    s += text(260, 320, "«помаранчевий» — рухома ціль у 3D,", size=9,
              anchor="middle", fill=MUTE)
    s += text(260, 336, "яку важко задати порогом", size=9, anchor="middle",
              fill=MUTE)
    s += rect(500, 110, 400, 250, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 134, "у HSV — легко", size=12.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += circle(590, 196, 30, fill="rgb(250,150,40)", stroke=INK, sw=1.2)
    s += text(590, 240, "яскраве", size=9, anchor="middle", fill=MUTE)
    s += text(590, 256, "H32° S84 V98", size=9.5, anchor="middle",
              weight="bold")
    s += circle(810, 196, 30, fill="rgb(120,70,18)", stroke=INK, sw=1.2)
    s += text(810, 240, "тьмяне", size=9, anchor="middle", fill=MUTE)
    s += text(810, 256, "H32° S85 V47", size=9.5, anchor="middle",
              weight="bold")
    s += text(700, 298, "тон H майже не змінився!", size=10, anchor="middle",
              fill="#15803d", weight="bold")
    s += text(700, 320, "«помаранчевий» = смужка тону 20–40°", size=9,
              anchor="middle", fill=MUTE)
    s += text(700, 336, "→ один поріг, стійко до світла", size=9,
              anchor="middle", fill=MUTE)
    bx, by, seg = 250, 384, 14
    for k in range(32):
        h = k * 360 / 32
        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)
        s += rect(bx + k * seg, by, seg, 18,
                  fill=f"rgb({int(r * 255)},{int(g * 255)},{int(b * 255)})",
                  stroke="none")
    s += rect(bx, by, 32 * seg, 18, fill="none", stroke=INK, sw=1)
    s += rect(bx + 2 * seg - 1, by - 3, 2 * seg + 2, 24, fill="none",
              stroke=INK, sw=2)
    s += text(bx + 3 * seg, by + 34, "↑ смужка «помаранчевого» тону", size=9,
              anchor="middle", weight="bold")
    s += text(700, H - 14,
              "Тому колір шукають у HSV: тон тримається попри світло. RGB→HSV, "
              "узяв смужку тону — і ось ціль (49.6).", size=10, anchor="end",
              fill=MUTE, italic=True)
    s += footer()
    return s


def _hist(n, peaks, scale, floor=0.0):
    out = []
    for i in range(n):
        v = floor
        for mu, sig, amp in peaks:
            v += amp * math.exp(-((i - mu) / sig) ** 2)
        out.append(max(0.0, v) * scale)
    return out


def _clamp(v):
    return max(0, min(255, int(v)))


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.2.1 — Гістограма
# ════════════════════════════════════════════════════════════════════════════
def fig_histogram():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Гістограма: «відбиток тонів» кадру",
               "гістограма рахує, скільки пікселів кожної яскравості (0…255); за її формою видно, темний кадр чи світлий")
    cols = [("ТЕМНИЙ (недосвітло)", "тони ліворуч", [(4, 4, 1.0)], 0.5, 0),
            ("ЗБАЛАНСОВАНИЙ", "по всьому діапазону",
             [(9, 5, 0.6), (20, 6, 0.8), (27, 3, 0.3)], 1.0, 0),
            ("СВІТЛИЙ (пересвітло)", "тони праворуч", [(27, 4, 1.0)], 1.0, 95)]
    cw, x0, gap = 280, 40, 20
    for k, (lab, desc, peaks, mult, add) in enumerate(cols):
        x = x0 + k * (cw + gap)
        s += text(x + cw / 2, 104, lab, size=11, anchor="middle",
                  weight="bold")
        tx, ty, tw, th = x + 40, 118, 200, 84
        for i in range(8):
            v = _clamp((118 + i * 11) * mult + add)
            s += rect(tx, ty + i * (th / 8), tw, th / 8 + 1,
                      fill=f"rgb({_clamp(v - 30)},{_clamp(v - 8)},{_clamp(v + 22)})",
                      stroke="none")
        sv = _clamp(232 * mult + add)
        s += circle(tx + tw * 0.72, ty + th * 0.34, 12,
                    fill=f"rgb({sv},{sv},{_clamp(sv - 45)})", stroke="none")
        gv = _clamp(70 * mult + add)
        s += rect(tx, ty + th * 0.7, tw, th * 0.3,
                  fill=f"rgb({_clamp(gv - 10)},{gv},{_clamp(gv - 18)})",
                  stroke="none")
        s += rect(tx, ty, tw, th, fill="none", stroke=INK, sw=1.2)
        ox, oy, ww, hh = x + 30, 322, cw - 60, 92
        s += line(ox, oy, ox + ww, oy, stroke=INK, w=1.2)
        bars = _hist(32, peaks, hh, 0.02)
        bw = ww / 32
        for i, h in enumerate(bars):
            s += rect(ox + i * bw, oy - min(h, hh), bw - 0.4, min(h, hh),
                      fill="#64748b", stroke="none")
        s += text(ox, oy + 14, "0", size=8, fill=MUTE)
        s += text(ox + ww, oy + 14, "255", size=8, anchor="end", fill=MUTE)
        s += text(x + cw / 2, oy + 32, desc, size=9, anchor="middle",
                  fill=MUTE, weight="bold")
    s += text(W / 2, H - 14,
              "Та сама сцена за різного експонування дає три різні гістограми — "
              "форма одразу викриває проблему з тоном.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.2.2 — Яскравість і контраст
# ════════════════════════════════════════════════════════════════════════════
def fig_brightness_contrast():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Яскравість і контраст: зсунути й розтягнути гістограму",
               "вихід = a·вхід + b: додати b — яскравіше (зсув гістограми); помножити на a — контрастніше (розтяг)")
    s += rect(60, 78, 840, 34, fill=BOX1, stroke=BLUE, sw=1.3, rx=8)
    s += text(W / 2, 100,
              "вихід = a · вхід + b      —      a: контраст (нахил) · b: яскравість (зсув)",
              size=12, anchor="middle", weight="bold", fill=BLUE)
    ox, oy, sz = 95, 350, 190
    s += rect(ox, oy - sz, sz, sz, fill="#fbfbfd", stroke="#e5e7eb", sw=1)
    s += line(ox, oy, ox + sz, oy, stroke=INK, w=1.3, marker="arr")
    s += line(ox, oy, ox, oy - sz, stroke=INK, w=1.3, marker="arr")
    s += text(ox + sz / 2, oy + 20, "вхід →", size=9, anchor="middle",
              fill=MUTE)
    s += text(ox - 6, oy - sz + 2, "вихід", size=9, anchor="end", fill=MUTE)
    s += line(ox, oy, ox + sz, oy - sz, stroke=MUTE, w=1.5, dash="4,3")
    s += text(ox + sz - 6, oy - sz + 16, "a=1, b=0", size=8, anchor="end",
              fill=MUTE)
    s += line(ox, oy - 46, ox + sz - 46, oy - sz, stroke=BLUE, w=2.3)
    s += text(ox + 26, oy - 150, "+b", size=10, fill=BLUE, weight="bold")
    s += line(ox + 52, oy, ox + sz - 22, oy - sz, stroke=RED, w=2.3)
    s += text(ox + sz - 8, oy - 40, "a>1", size=10, anchor="end", fill=RED,
              weight="bold")
    s += text(ox + sz / 2, oy - sz - 8, "тонова крива", size=10,
              anchor="middle", weight="bold")
    rows = [("оригінал", [(16, 5, 1.0)], INK, 0),
            ("+ яскравість (зсув праворуч)", [(16, 5, 1.0)], BLUE, 8),
            ("× контраст (розтяг ширше)", [(16, 9, 0.7)], RED, 0)]
    for r, (lab, peaks, col, shift) in enumerate(rows):
        bx, by, bw2 = 430, 168 + r * 96, 360
        s += text(bx, by - 8, lab, size=10, weight="bold", fill=col)
        s += line(bx, by + 56, bx + bw2, by + 56, stroke=INK, w=1)
        bars = _hist(32, [(mu + shift, sig, amp) for mu, sig, amp in peaks], 54,
                     0.01)
        w2 = bw2 / 32
        for i, h in enumerate(bars):
            s += rect(bx + i * w2, by + 56 - h, w2 - 0.4, h,
                      fill=(col if col != INK else "#64748b"), stroke="none")
        s += text(bx + bw2, by + 70, "255", size=7.5, anchor="end", fill=MUTE)
    s += text(W / 2, H - 14,
              "Це «точкові» дії — над КОЖНИМ пікселем окремо, без сусідів: "
              "зсув робить яскравіше, розтяг — контрастніше.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.2.3 — Розтягнення й вирівнювання
# ════════════════════════════════════════════════════════════════════════════
def fig_stretch_equalize():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Розтягнення й вирівнювання гістограми",
               "розтягнути вузький діапазон на весь 0…255 — більше контрасту; вирівняти розподіл — проявити деталі")

    def minihist(bx, by, bw2, bars, col):
        out = line(bx, by, bx + bw2, by, stroke=INK, w=1)
        w2 = bw2 / len(bars)
        for i, h in enumerate(bars):
            out += rect(bx + i * w2, by - h, w2 - 0.4, h, fill=col,
                        stroke="none")
        return out
    s += rect(50, 96, 420, 320, fill="#fbfbfd", stroke=BLUE, sw=1.8, rx=12)
    s += text(260, 120, "РОЗТЯГНЕННЯ (нормалізація)", size=11.5,
              anchor="middle", weight="bold", fill=BLUE)
    s += text(150, 146, "до: вузько (сіро, пласко)", size=9, anchor="middle",
              fill=MUTE)
    s += minihist(70, 210, 360, _hist(32, [(15, 2.4, 1.0)], 48, 0), "#94a3b8")
    s += text(380, 200, "→", size=16, anchor="middle", weight="bold")
    s += text(150, 236, "після: на весь 0…255", size=9, anchor="middle",
              fill="#15803d", weight="bold")
    s += line(260, 250, 260, 276, stroke=INK, w=1.5, marker="arr")
    s += minihist(70, 340, 360, _hist(32, [(15, 9, 0.9)], 48, 0.04), "#3b82f6")
    s += text(260, 360, "контраст з'явився; деталі тонів — як перепади",
              size=8.6, anchor="middle", fill=MUTE)
    s += rect(490, 96, 420, 320, fill="#fbfbfd", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 120, "ВИРІВНЮВАННЯ (еквалізація)", size=11.5,
              anchor="middle", weight="bold", fill="#15803d")
    s += text(590, 146, "до: тони збиті в купу", size=9, anchor="middle",
              fill=MUTE)
    s += minihist(510, 210, 360, _hist(32, [(8, 3, 1.0)], 48, 0.01), "#94a3b8")
    s += line(700, 250, 700, 276, stroke=INK, w=1.5, marker="arr")
    s += text(700, 236, "після: розподіл ≈ рівний", size=9, anchor="middle",
              fill="#15803d", weight="bold")
    s += minihist(510, 340, 360, _hist(32, [(16, 30, 0.5)], 40, 0.55),
                  "#22c55e")
    s += text(700, 360, "деталі в тінях і світлах проявляються", size=8.6,
              anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Розтягнення дає контраст; вирівнювання вивертає приховані деталі "
              "— і те, й те нормалізує кадр перед розпізнаванням.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.2.4 — Обрізання і зір
# ════════════════════════════════════════════════════════════════════════════
def fig_clipping_vision():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Обрізання тонів — і чому гістограма важлива для зору",
               "значення за межами 0…255 «прилипають» і деталі гинуть; а рівний тон робить розпізнавання стійким до світла")
    s += rect(50, 100, 420, 300, fill="#fef2f2", stroke=RED, sw=1.8, rx=12)
    s += text(260, 124, "ОБРІЗАННЯ (clipping)", size=11.5, anchor="middle",
              weight="bold", fill=RED)
    ox, oy, ww, hh = 80, 300, 360, 120
    s += line(ox, oy, ox + ww, oy, stroke=INK, w=1.2)
    bars = _hist(32, [(15, 7, 0.30)], hh, 0.02)
    bars[0] = hh
    bars[31] = hh * 0.82
    bw = ww / 32
    for i, h in enumerate(bars):
        col = RED if (i == 0 or i == 31) else "#94a3b8"
        s += rect(ox + i * bw, oy - min(h, hh), bw - 0.4, min(h, hh), fill=col,
                  stroke="none")
    s += text(ox, oy + 16, "0 (тіні)", size=8, fill=RED, weight="bold")
    s += text(ox + ww, oy + 16, "255 (світла)", size=8, anchor="end", fill=RED,
              weight="bold")
    s += text(260, 348, "піки на краях = тони «прилипли»", size=9,
              anchor="middle", fill=RED, weight="bold")
    s += text(260, 366, "деталі за межами втрачено НАЗАВЖДИ", size=9,
              anchor="middle", fill=MUTE)
    s += text(260, 382, "(недо-/переекспозиція)", size=8.5, anchor="middle",
              fill=MUTE)
    s += rect(490, 100, 420, 300, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 124, "ЧОМУ ЦЕ ВАЖЛИВО ДЛЯ ЗОРУ", size=11.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += rect(520, 150, 110, 90, fill="#23262e", stroke=INK, sw=1.2)
    s += rect(556, 182, 40, 30, fill="#2b2f38", stroke="none")
    s += text(575, 252, "темний, плаский", size=8.5, anchor="middle",
              fill=MUTE)
    s += text(575, 266, "кадр → ціль не видно", size=8.5, anchor="middle",
              fill=MUTE)
    s += line(642, 195, 686, 195, stroke=INK, w=1.6, marker="arr")
    s += text(664, 184, "вирівняти", size=8, anchor="middle", fill="#15803d",
              weight="bold")
    s += rect(700, 150, 110, 90, fill="#3b4250", stroke=INK, sw=1.2)
    s += rect(736, 182, 40, 30, fill="#f59e0b", stroke="none")
    s += rect(732, 178, 48, 38, fill="none", stroke=GREEN, sw=2)
    s += text(755, 252, "контраст піднято →", size=8.5, anchor="middle",
              fill=MUTE)
    s += text(755, 266, "межі й ціль проявились", size=8.5, anchor="middle",
              fill="#15803d", weight="bold")
    s += text(700, 318, "тому кадр часто нормалізують ПЕРЕД", size=9.5,
              anchor="middle", weight="bold")
    s += text(700, 334, "розпізнаванням — щоб світло не збивало", size=9.5,
              anchor="middle", fill=MUTE)
    s += text(700, 350, "детектор (49.6)", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 14,
              "Гістограма — і діагноз (чи не обрізано тони), і ліки (нормалізуй "
              "перед зором). Обрізане ж не повернути.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


def _kernel3(x, y, vals, col, cell=32):
    out = ""
    for r in range(3):
        for c in range(3):
            out += rect(x + c * cell, y + r * cell, cell, cell, fill="white",
                        stroke=col, sw=1.2)
            out += text(x + c * cell + cell / 2, y + r * cell + cell * 0.66,
                        vals[r][c], size=10, anchor="middle", weight="bold",
                        fill=col)
    return out


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.3.1 — Згортка
# ════════════════════════════════════════════════════════════════════════════
def fig_convolution():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Згортка: маленьке ядро ковзає кадром",
               "над кожним пікселем кладемо сітку ваг (ядро 3×3); новий піксель = сума «вага × піксель під нею» по сусідах")
    gx, gy, cell = 55, 130, 34
    inp = [[120, 124, 130, 128, 126, 122],
           [122, 200, 205, 128, 124, 120],
           [126, 210, 215, 210, 126, 124],
           [124, 128, 212, 214, 210, 122],
           [120, 126, 130, 128, 126, 120],
           [118, 122, 126, 124, 122, 118]]
    s += text(gx + 3 * cell, 116, "вхід (яскравості)", size=10, anchor="middle",
              weight="bold")
    for r in range(6):
        for c in range(6):
            v = inp[r][c]
            s += rect(gx + c * cell, gy + r * cell, cell, cell,
                      fill=f"rgb({v},{v},{v})", stroke="#cbd5e1", sw=0.5)
            s += text(gx + c * cell + cell / 2, gy + r * cell + cell * 0.62,
                      str(v), size=8, anchor="middle",
                      fill=("white" if v < 150 else INK))
    s += rect(gx + cell, gy + cell, 3 * cell, 3 * cell, fill="none", stroke=RED,
              sw=2.4)
    win = [inp[r][c] for r in (1, 2, 3) for c in (1, 2, 3)]
    res = round(sum(win) / 9)
    s += text(345, 116, "ядро (÷9)", size=10, anchor="middle", weight="bold")
    s += text(322, 200, "⊙", size=20, anchor="middle", weight="bold")
    s += _kernel3(345, 165, [["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]],
                  BLUE, 30)
    s += text(345, 270, "(усереднення)", size=8.5, anchor="middle", fill=MUTE)
    s += text(452, 200, "=", size=20, anchor="middle", weight="bold")
    s += rect(478, 178, 64, 44, fill=BOX2, stroke=GREEN, sw=1.6, rx=8)
    s += text(510, 206, str(res), size=15, anchor="middle", weight="bold",
              fill="#15803d")
    s += line(548, 200, 580, 200, stroke=INK, w=1.6, marker="arr")
    gx2 = 600
    s += text(gx2 + 3 * cell, 116, "вихід", size=10, anchor="middle",
              weight="bold")
    for r in range(6):
        for c in range(6):
            green = (r == 2 and c == 2)
            s += rect(gx2 + c * cell, gy + r * cell, cell, cell,
                      fill=(BOX2 if green else "white"),
                      stroke=("#15803d" if green else "#e5e7eb"),
                      sw=(1.6 if green else 0.5))
            if green:
                s += text(gx2 + c * cell + cell / 2, gy + r * cell + cell * 0.64,
                          str(res), size=9, anchor="middle", weight="bold",
                          fill="#15803d")
    s += text(W / 2, H - 30,
              "Поклади ядро на 3×3 сусідів, перемнож із вагами, склади — і це "
              "новий центральний піксель.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "І так посунь ядро по КОЖНОМУ пікселю кадру. Зміни ваги — зміниш "
              "ефект (розмиття, різкість, межі).", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.3.2 — Розмиття
# ════════════════════════════════════════════════════════════════════════════
def fig_blur():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Розмиття: усереднити сусідів",
               "ядро-усереднювач: коробкове (усі ваги рівні) чи гаусове (більше ваги центру); глушить шум, та з'їдає деталі")
    s += text(150, 116, "коробкове 3×3 (÷9)", size=10.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += _kernel3(99, 132, [["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]],
                  BLUE, 34)
    s += text(150, 254, "усі ваги рівні → проста середня", size=8.4,
              anchor="middle", fill=MUTE)
    s += text(370, 116, "гаусове 3×3 (÷16)", size=10.5, anchor="middle",
              weight="bold", fill=GREEN)
    s += _kernel3(319, 132, [["1", "2", "1"], ["2", "4", "2"], ["1", "2", "1"]],
                  GREEN, 34)
    s += text(370, 254, "центру більше ваги → м'якше", size=8.4,
              anchor="middle", fill=MUTE)
    s += text(700, 116, "ефект", size=10.5, anchor="middle", weight="bold")
    nx, ny = 560, 132
    s += rect(nx, ny, 120, 96, fill="rgb(150,150,150)", stroke=INK, sw=1.2)
    for k in range(150):
        px = nx + (k * 37) % 116
        py = ny + (k * 53) % 92
        v = 70 + (k * 61) % 150
        s += rect(px, py, 3, 3, fill=f"rgb({v},{v},{v})", stroke="none")
    s += text(nx + 60, ny + 116, "шумно", size=9, anchor="middle", fill=RED,
              weight="bold")
    s += line(nx + 124, ny + 48, nx + 156, ny + 48, stroke=INK, w=1.6,
              marker="arr")
    bx = nx + 168
    for i in range(8):
        v = 138 + i * 3
        s += rect(bx, ny + i * 12, 120, 13, fill=f"rgb({v},{v},{v})",
                  stroke="none")
    s += rect(bx, ny, 120, 96, fill="none", stroke=INK, sw=1.2)
    s += text(bx + 60, ny + 116, "розмито (шум зник)", size=9, anchor="middle",
              fill="#15803d", weight="bold")
    s += rect(70, 300, 820, 96, fill=BOX1, stroke=BLUE, sw=1.3, rx=11)
    s += text(480, 324, "Навіщо розмиття", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(110, 348,
               ["• глушить ВИПАДКОВИЙ шум: сусіди усереднюються, випадкові викиди гаснуть;",
                "• прибирає дрібні деталі ПЕРЕД пошуком великих структур (часто — крок перед межами, 49.4);",
                "• плата: разом із шумом м'якшають і справжні деталі — більший радіус ядра = сильніше розмиття."],
               size=9.5, lh=21)
    s += text(W / 2, H - 8,
              "Розмиття усереднює — тому й глушить шум; та воно ж стирає дрібне. "
              "За все плата.", size=10.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.3.3 — Різкість
# ════════════════════════════════════════════════════════════════════════════
def fig_sharpen():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Різкість: підкреслити перепади",
               "ядро різкості підсилює центр і віднімає сусідів (0 −1 0 / −1 5 −1 / 0 −1 0) — підкреслює межі (а заразом і шум)")
    s += text(150, 116, "ядро різкості 3×3", size=10.5, anchor="middle",
              weight="bold", fill=RED)
    s += _kernel3(99, 134, [["0", "-1", "0"], ["-1", "5", "-1"], ["0", "-1", "0"]],
                  RED, 34)
    s += text(150, 256, "центр +5, сусіди −1: підсилити те,", size=8.4,
              anchor="middle", fill=MUTE)
    s += text(150, 270, "чим піксель різниться від околу", size=8.4,
              anchor="middle", fill=MUTE)
    s += text(150, 296, "= оригінал + (оригінал − розмите)", size=8.6,
              anchor="middle", fill=RED, weight="bold")
    ax, ay, top = 380, 360, 150
    s += rect(ax, top, 500, ay - top, fill="#fbfbfd", stroke="#e5e7eb", sw=1)
    s += line(ax, ay, ax + 500, ay, stroke=INK, w=1.3, marker="arr")
    s += line(ax, ay, ax, top, stroke=INK, w=1.3, marker="arr")
    s += text(ax + 250, ay + 20, "положення впоперек межі →", size=9,
              anchor="middle", fill=MUTE)
    s += text(ax + 4, top - 4, "↑ яскравість", size=9, fill=MUTE)
    soft = [(390, 330), (450, 328), (510, 322), (560, 300), (620, 250),
            (680, 205), (740, 178), (810, 170), (870, 168)]
    s += poly(soft, fill="none", stroke=BLUE, sw=2.4, closed=False)
    s += text(470, 318, "м'який перепад", size=9.5, fill=BLUE, weight="bold")
    sharp = [(390, 332), (470, 330), (540, 344), (575, 300), (615, 168),
             (650, 150), (700, 178), (810, 168), (870, 166)]
    s += poly(sharp, fill="none", stroke=RED, sw=2.4, closed=False)
    s += circle(540, 344, 4, fill=RED, stroke="none")
    s += text(540, 362, "недоліт", size=8, anchor="middle", fill=RED)
    s += circle(650, 150, 4, fill=RED, stroke="none")
    s += text(665, 142, "переліт («німб»)", size=8, fill=RED)
    s += text(760, 200, "після різкості:", size=9.5, fill=RED, weight="bold")
    s += text(760, 214, "крутіше + німби", size=9.5, fill=RED, weight="bold")
    s += text(W / 2, H - 14,
              "Різкість додає пікселю його ж відмінність від сусідів — тож межі "
              "«вистрілюють». Так само підсилюється й шум.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.3.4 — Галерея ядер і ціна
# ════════════════════════════════════════════════════════════════════════════
def fig_kernels_cost():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Галерея ядер і ціна згортки",
               "те саме ковзання, різні ваги — різний ефект; а ціна = k² множень на піксель, тож на МК беруть малі/розділювані ядра")
    gallery = [
        ("тотожне", [["0", "0", "0"], ["0", "1", "0"], ["0", "0", "0"]], INK,
         "нічого не міняє"),
        ("розмиття", [["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]], BLUE,
         "÷9 — усереднює"),
        ("різкість", [["0", "-1", "0"], ["-1", "5", "-1"], ["0", "-1", "0"]],
         RED, "підкреслює межі"),
        ("межі (49.4)", [["-1", "0", "1"], ["-2", "0", "2"], ["-1", "0", "1"]],
         GREEN, "перепад → контур"),
    ]
    x0, step = 70, 222
    for i, (lab, vals, col, eff) in enumerate(gallery):
        x = x0 + i * step
        s += text(x + 48, 116, lab, size=10.5, anchor="middle", weight="bold",
                  fill=col)
        s += _kernel3(x + 3, 132, vals, col, 32)
        s += text(x + 48, 248, eff, size=8.6, anchor="middle", fill=MUTE)
    s += rect(60, 288, 840, 126, fill=PANEL, stroke=INK, sw=1.4, rx=11)
    s += text(480, 312, "Ціна згортки — і як її збити", size=11,
              anchor="middle", weight="bold")
    s += lines(92, 336,
               ["• наївно: ядро k×k → k² множень-додавань на КОЖЕН піксель (3×3=9, 5×5=25, 7×7=49), та ще × W×H пікселів;",
                "• гаусове ядро РОЗДІЛЮВАНЕ: окремо прохід рядками + прохід стовпцями → 2k замість k² (для 5×5: 10 проти 25);",
                "• край кадру: ядро звисає за межу, тож пікселі доповнюють — повторити край / дзеркало / обрізати рамку."],
               size=9.5, lh=23)
    s += text(W / 2, H - 12,
              "Згортка — двигун усієї просторової обробки (і нейромереж, 49.7). "
              "На МК рятують малі та розділювані ядра.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.4.1 — Межа й градієнт
# ════════════════════════════════════════════════════════════════════════════
def fig_edge_gradient():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Межа — це різкий перепад яскравості, а градієнт його ловить",
               "там, де яскравість стрибає, похідна (градієнт) дає сплеск; рівне місце — градієнт ≈0, межа — пік")
    px, py, pw, ph = 70, 150, 200, 150
    for c in range(pw):
        d = c - pw * 0.5
        v = 50 if d < 0 else 210
        if abs(d) < 16:
            v = int(50 + 160 * (d + 16) / 32)
        s += rect(px + c, py, 1, ph, fill=f"rgb({v},{v},{v})", stroke="none")
    s += rect(px, py, pw, ph, fill="none", stroke=INK, sw=1.3)
    s += line(px + 68, py + ph / 2, px + 150, py + ph / 2, stroke=RED, w=3,
              marker="arrR")
    s += text(px + pw / 2, py - 10, "темно | світло", size=9, anchor="middle",
              fill=MUTE)
    s += text(px + pw / 2, py + ph + 20, "напрям градієнта ⊥ межі", size=9,
              anchor="middle", fill=RED, weight="bold")
    gx0, gw = 340, 540
    by = 196
    s += text(gx0, 128, "яскравість упоперек межі", size=9.5, weight="bold")
    s += line(gx0, by, gx0 + gw, by, stroke="#cbd5e1", w=1)
    bp = []
    for i in range(28):
        t = i / 27
        v = 50.0 if t < 0.5 else 210.0
        if abs(t - 0.5) < 0.09:
            v = 50 + 160 * ((t - 0.5) / 0.18 + 0.5)
        bp.append((gx0 + t * gw, by - (v - 50) / 160 * 66))
    s += poly(bp, fill="none", stroke=BLUE, sw=2.4, closed=False)
    s += text(gx0 + gw, by + 14, "x →", size=8, anchor="end", fill=MUTE)
    gy0 = 376
    s += text(gx0, 268, "градієнт (похідна) — сплеск саме на межі", size=9.5,
              weight="bold")
    s += line(gx0, gy0, gx0 + gw, gy0, stroke="#cbd5e1", w=1)
    gp = []
    for i in range(28):
        t = i / 27
        d = math.exp(-((t - 0.5) / 0.06) ** 2)
        gp.append((gx0 + t * gw, gy0 - d * 78))
    s += poly(gp, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(gx0 + gw * 0.5, gy0 - 90, "← пік = межа", size=9, anchor="middle",
              fill=RED, weight="bold")
    s += text(gx0 + gw * 0.14, gy0 - 8, "рівно → ≈0", size=8.5, fill=MUTE)
    s += text(W / 2, H - 14,
              "Межа = велике значення градієнта. Його СИЛА каже, наскільки різка "
              "межа, а НАПРЯМ — куди вона повернута.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.4.2 — Собель
# ════════════════════════════════════════════════════════════════════════════
def fig_sobel():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Собель: згортка, що оцінює градієнт",
               "Gx ловить вертикальні межі, Gy — горизонтальні; разом дають силу межі √(Gx²+Gy²) і напрям")
    s += text(150, 114, "Gx (вертикальні межі)", size=10, anchor="middle",
              weight="bold", fill=BLUE)
    s += _kernel3(99, 130, [["-1", "0", "1"], ["-2", "0", "2"], ["-1", "0", "1"]],
                  BLUE, 34)
    s += text(150, 252, "різниця «право − ліво»", size=8.4, anchor="middle",
              fill=MUTE)
    s += text(390, 114, "Gy (горизонтальні межі)", size=10, anchor="middle",
              weight="bold", fill=GREEN)
    s += _kernel3(339, 130, [["-1", "-2", "-1"], ["0", "0", "0"], ["1", "2", "1"]],
                  GREEN, 34)
    s += text(390, 252, "різниця «низ − верх»", size=8.4, anchor="middle",
              fill=MUTE)
    s += rect(560, 150, 360, 124, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(740, 174, "сила межі в кожнім пікселі:", size=10,
              anchor="middle", weight="bold")
    s += text(740, 204, "|G| = √(Gx² + Gy²)", size=14, anchor="middle",
              weight="bold", fill=RED)
    s += text(740, 234, "напрям межі = atan2(Gy, Gx)", size=10,
              anchor="middle", fill=MUTE)
    s += text(740, 256, "(куди дивиться перепад)", size=8.5, anchor="middle",
              fill=MUTE)

    def thumb(x, lab, sides):
        out = text(x + 55, 312, lab, size=9, anchor="middle", weight="bold")
        out += rect(x, 322, 110, 100, fill="#10131a", stroke=INK, sw=1)
        sx, sy, ss = x + 32, 344, 50
        b = "#f8fafc"
        if "L" in sides:
            out += line(sx, sy, sx, sy + ss, stroke=b, w=3.5)
        if "R" in sides:
            out += line(sx + ss, sy, sx + ss, sy + ss, stroke=b, w=3.5)
        if "T" in sides:
            out += line(sx, sy, sx + ss, sy, stroke=b, w=3.5)
        if "B" in sides:
            out += line(sx, sy + ss, sx + ss, sy + ss, stroke=b, w=3.5)
        if not sides:
            out += rect(sx, sy, ss, ss, fill="none", stroke="#94a3b8", sw=3)
        return out
    s += thumb(70, "вхід: квадрат", "")
    s += text(232, 372, "→", size=18, anchor="middle", weight="bold")
    s += thumb(255, "Gx: бокові", "LR")
    s += thumb(405, "Gy: верх/низ", "TB")
    s += text(572, 372, "→", size=18, anchor="middle", weight="bold")
    s += thumb(600, "|G|: повний контур", "LRTB")
    s += rect(740, 322, 170, 100, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(825, 360, "Собель — це й є", size=9.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(825, 378, "два ядра-похідні", size=9.5, anchor="middle",
              fill="#15803d")
    s += text(825, 396, "із 49.3", size=9.5, anchor="middle", fill="#15803d")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.4.3 — Конвеєр Канні
# ════════════════════════════════════════════════════════════════════════════
def fig_canny_pipeline():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Канні: конвеєр чистих, тонких, зв'язаних меж",
               "розмити → градієнт (Собель) → стоншити (немаксимуми геть) → подвійний поріг із гістерезисом (з'єднати)")
    stages = [("1. Розмиття", "Гаус глушить шум", BLUE, "blur"),
              ("2. Градієнт", "Собель: |G|, та товсто", AMBER, "grad"),
              ("3. Стоншення", "немаксимуми геть → 1 px", AMBER, "thin"),
              ("4. Гістерезис", "2 пороги: сильні + зв'язані", GREEN, "hyst")]
    bw, bh, y, x0, gap = 180, 150, 152, 40, 30
    for i, (t, d, col, kind) in enumerate(stages):
        x = x0 + i * (bw + gap)
        s += text(x + bw / 2, y - 16, t, size=10.5, anchor="middle",
                  weight="bold", fill=col)
        s += rect(x, y, bw, bh, fill="#10131a", stroke=col, sw=1.8, rx=8)
        cx, cy = x + bw / 2, y + bh / 2 - 4
        if kind == "blur":
            s += circle(cx, cy, 38, fill="none", stroke="#39414f", sw=8)
            for k in range(18):
                s += rect(x + 12 + (k * 41) % (bw - 24),
                          y + 12 + (k * 53) % (bh - 24), 2, 2, fill="#4b5563",
                          stroke="none")
        elif kind == "grad":
            s += circle(cx, cy, 38, fill="none", stroke="#e5e7eb", sw=8)
            for k in range(12):
                s += rect(x + 16 + (k * 47) % (bw - 30),
                          y + 16 + (k * 59) % (bh - 30), 4, 4, fill="#9ca3af",
                          stroke="none")
        elif kind == "thin":
            s += circle(cx, cy, 38, fill="none", stroke="#f8fafc", sw=2)
            s += rect(cx + 30, cy - 8, 12, 16, fill="#10131a", stroke="none")
        else:
            s += circle(cx, cy, 38, fill="none", stroke="#22c55e", sw=2.2)
        s += text(x + bw / 2, y + bh + 18, d, size=8.6, anchor="middle",
                  fill=MUTE)
        if i < 3:
            s += line(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, stroke=INK,
                      w=1.8, marker="arr")
    s += rect(40, 372, 880, 56, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 394,
              "Джон Канні (1986) вивів цей конвеєр як МАТЕМАТИЧНО оптимальний: добре виявити, точно локалізувати, один відгук на межу.",
              size=9.6, anchor="middle", weight="bold")
    s += text(480, 414,
              "Результат — тонкі, чисті, зв'язані контури, на яких будують усе подальше (форми, лінії — 49.6).",
              size=9.2, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.4.4 — Собель проти Канні
# ════════════════════════════════════════════════════════════════════════════
def fig_sobel_vs_canny():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Собель проти Канні: коли що брати",
               "Собель — сирий градієнт, товсто й шумно, та дешево; Канні — тонко, чисто, зв'язано, та важче")
    s += rect(60, 108, 400, 296, fill="#fbfbfd", stroke=BLUE, sw=1.8, rx=12)
    s += text(260, 132, "СОБЕЛЬ (сирий градієнт)", size=11.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += rect(175, 148, 170, 110, fill="#10131a", stroke=INK, sw=1)
    s += circle(260, 203, 40, fill="none", stroke="#e5e7eb", sw=6)
    for k in range(14):
        s += rect(185 + (k * 43) % 150, 158 + (k * 57) % 90, 3, 3,
                  fill="#9ca3af", stroke="none")
    s += lines(80, 286,
               ["+ дешево, швидко (один прохід ядром)",
                "+ годиться для МК: лінія, прості мітки",
                "− товсті межі, шум, не зв'язані",
                "− треба поріг, щоб відсікти слабке"], size=9.3, lh=23)
    s += rect(500, 108, 400, 296, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 132, "КАННІ (чистий конвеєр)", size=11.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += rect(615, 148, 170, 110, fill="#10131a", stroke=INK, sw=1)
    s += circle(700, 203, 40, fill="none", stroke="#22c55e", sw=2.2)
    s += lines(520, 286,
               ["+ тонкі, чисті, ЗВ'ЯЗАНІ контури",
                "+ основа для форм і ліній Хафа (49.6)",
                "− важче: 4 кроки, два пороги",
                "− краще на бортовому комп'ютері (49.9)"], size=9.3, lh=23)
    s += text(W / 2, H - 14,
              "Сирий градієнт (Собель) — коли треба швидко й дешево; чистий "
              "контур (Канні) — коли далі форми й об'єкти (49.6, 49.8).",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.5.1 — Поріг
# ════════════════════════════════════════════════════════════════════════════
def fig_thresholding():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Поріг: із сірого — чорно-біле",
               "піксель, яскравіший за поріг T → білий (об'єкт), темніший → чорний (тло); Оцу сам ставить T у «долину» гістограми")
    s += text(150, 114, "сіре", size=10, anchor="middle", weight="bold")
    s += rect(70, 128, 160, 140, fill="rgb(92,92,92)", stroke=INK, sw=1.2)
    s += circle(150, 198, 44, fill="rgb(205,205,205)", stroke="none")
    s += line(236, 198, 282, 198, stroke=INK, w=1.6, marker="arr")
    hx, hy, hw, hh = 292, 258, 372, 120
    s += text(hx + hw / 2, 114, "гістограма: дві купи, T у долині", size=9.5,
              anchor="middle", weight="bold")
    s += line(hx, hy, hx + hw, hy, stroke=INK, w=1.2)
    bars = _hist(40, [(9, 4, 0.9), (30, 4, 0.7)], hh, 0.02)
    bw = hw / 40
    for i, h in enumerate(bars):
        s += rect(hx + i * bw, hy - h, bw - 0.5, h, fill="#94a3b8",
                  stroke="none")
    tx = hx + 20 * bw
    s += line(tx, hy + 6, tx, hy - hh - 6, stroke=RED, w=2, dash="4,3")
    s += text(tx, hy - hh - 12, "T (Оцу)", size=9, anchor="middle", fill=RED,
              weight="bold")
    s += text(hx + 9 * bw, hy + 18, "тло → чорне", size=8.4, anchor="middle",
              fill=MUTE)
    s += text(hx + 30 * bw, hy + 18, "об'єкт → біле", size=8.4, anchor="middle",
              fill=MUTE)
    s += line(672, 198, 718, 198, stroke=INK, w=1.6, marker="arr")
    s += text(810, 114, "чорно-біле (маска)", size=10, anchor="middle",
              weight="bold")
    s += rect(730, 128, 160, 140, fill="#000000", stroke=INK, sw=1.2)
    s += circle(810, 198, 44, fill="#ffffff", stroke="none")
    s += text(W / 2, H - 14,
              "Поріг — найпростіша сегментація: кадр ділять на «об'єкт» і «тло». "
              "Оцу знаходить найкраще T сам — у долині між купами.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.5.2 — Адаптивний поріг
# ════════════════════════════════════════════════════════════════════════════
def fig_adaptive():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Коли один поріг не годиться: адаптивний поріг",
               "при нерівному світлі глобальний поріг скрізь хибить; локальний рахує T для кожної ділянки окремо")
    words = [(28, 40, 40), (76, 40, 30), (118, 40, 44), (28, 78, 30),
             (70, 78, 50), (132, 78, 38), (40, 116, 34), (86, 116, 46)]

    def panel(x, lab, kind, col):
        out = text(x + 130, 114, lab, size=10.5, anchor="middle",
                   weight="bold", fill=col)
        out += rect(x, 128, 260, 150, fill="#1a1a1a", stroke=INK, sw=1.2)
        if kind == "orig":
            for c in range(26):
                v = int(40 + 175 * (1 - c / 26))
                out += rect(x + c * 10, 128, 10, 150, fill=f"rgb({v},{v},{v})",
                            stroke="none")
            for wx, wy, ww in words:
                out += rect(x + wx, 128 + wy, ww, 12, fill="rgb(28,28,28)",
                            stroke="none")
        elif kind == "global":
            out += rect(x, 128, 132, 150, fill="white", stroke="none")
            out += rect(x + 132, 128, 128, 150, fill="black", stroke="none")
            out += text(x + 66, 206, "вибілено", size=8.5, anchor="middle",
                        fill="#777")
            out += text(x + 196, 206, "провалено", size=8.5, anchor="middle",
                        fill="#777")
        else:
            out += rect(x, 128, 260, 150, fill="white", stroke="none")
            for wx, wy, ww in words:
                out += rect(x + wx, 128 + wy, ww, 12, fill="black",
                            stroke="none")
        out += rect(x, 128, 260, 150, fill="none", stroke=INK, sw=1.2)
        return out
    s += panel(40, "оригінал (нерівне світло)", "orig", INK)
    s += panel(350, "ГЛОБАЛЬНИЙ поріг — хибить", "global", RED)
    s += panel(660, "АДАПТИВНИЙ — добре", "adaptive", GREEN)
    s += text(170, 296, "світло спадає зліва направо →", size=8.4,
              anchor="middle", fill=MUTE)
    s += rect(40, 312, 880, 92, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 336, "Чому глобальний поріг ламається", size=11,
              anchor="middle", weight="bold")
    s += lines(70, 358,
               ["• одне T на весь кадр: де яскраво — усе «об'єкт», де тінь — усе «тло»; напис гине і там, і там;",
                "• адаптивний рахує T для КОЖНОЇ ділянки з її ж околу → тінь і світло більше не збивають поділ."],
               size=9.5, lh=20)
    s += text(W / 2, H - 8,
              "Нерівне світло — головний ворог порога. Локальний поріг дивиться "
              "на окіл, тож тримається попри тіні й віньєтку.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.5.3 — Ерозія і дилатація
# ════════════════════════════════════════════════════════════════════════════
def fig_erosion_dilation():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Ерозія і дилатація: стиснути й розростити",
               "структурний елемент ковзає маскою: ерозія стискає біле (геть дрібні цятки), дилатація розростає (латає дірки)")
    s += text(150, 116, "структурний елемент", size=9.5, anchor="middle",
              weight="bold")
    s += _kernel3(99, 132, [["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]],
                  INK, 34)
    s += text(150, 258, "окіл «сусідства» (3×3)", size=8.4, anchor="middle",
              fill=MUTE)

    def mb(x, y, kind):
        out = rect(x, y, 150, 104, fill="#0f172a", stroke=INK, sw=1.2)
        cx, cy = x + 75, y + 52
        if kind == "be":
            out += circle(cx, cy, 34, fill="white", stroke="none")
            out += rect(x + 16, y + 14, 8, 8, fill="white", stroke="none")
            out += rect(x + 122, y + 82, 7, 7, fill="white", stroke="none")
        elif kind == "ae":
            out += circle(cx, cy, 27, fill="white", stroke="none")
        elif kind == "bd":
            out += circle(cx, cy, 34, fill="white", stroke="none")
            out += circle(cx, cy, 11, fill="#0f172a", stroke="none")
        else:
            out += circle(cx, cy, 41, fill="white", stroke="none")
        return out
    s += text(560, 116,
              "ЕРОЗІЯ: біле лишається, лиш якщо ВСІ сусіди білі → стискає, з'їдає цятки",
              size=9.4, anchor="middle", weight="bold", fill=BLUE)
    s += mb(330, 134, "be")
    s += text(405, 252, "до (з цятками)", size=8.3, anchor="middle", fill=MUTE)
    s += line(486, 186, 522, 186, stroke=INK, w=1.6, marker="arr")
    s += mb(532, 134, "ae")
    s += text(607, 252, "після (менше, чисто)", size=8.3, anchor="middle",
              fill=MUTE)
    s += text(560, 296,
              "ДИЛАТАЦІЯ: біле, якщо ХОЧ ОДИН сусід білий → розростає, латає дірки",
              size=9.4, anchor="middle", weight="bold", fill=GREEN)
    s += mb(330, 314, "bd")
    s += text(405, 432, "до (з діркою)", size=8.3, anchor="middle", fill=MUTE)
    s += line(486, 366, 522, 366, stroke=INK, w=1.6, marker="arr")
    s += mb(532, 314, "ad")
    s += text(607, 432, "після (більше, цілісно)", size=8.3, anchor="middle",
              fill=MUTE)
    s += rect(710, 150, 210, 250, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(815, 174, "запам'ятай", size=10.5, anchor="middle",
              weight="bold")
    s += lines(728, 200,
               ["• ерозія — «з'їдає» край", "  білого: дрібне зникає,",
                "  тонке рветься, тіла", "  роз'єднуються;",
                "• дилатація — «нарощує»", "  край: дірки й щілини",
                "  затягуються, тіла", "  зливаються."], size=9.3, lh=22)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.5.4 — Відкриття і закриття
# ════════════════════════════════════════════════════════════════════════════
def fig_opening_closing():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Відкриття і закриття: прибрати й залатати",
               "відкриття (ерозія→дилатація) прибирає цятки, не міняючи розміру; закриття (дилатація→ерозія) латає дірки, не міняючи розміру")

    def box(x, y, kind):
        out = rect(x, y, 150, 104, fill="#0f172a", stroke=INK, sw=1.2)
        cx, cy = x + 75, y + 52
        if kind == "on":
            out += circle(cx, cy, 33, fill="white", stroke="none")
            for k in range(7):
                out += rect(x + 12 + (k * 41) % 130, y + 10 + (k * 53) % 84, 6,
                            6, fill="white", stroke="none")
        elif kind == "oo":
            out += circle(cx, cy, 33, fill="white", stroke="none")
        elif kind == "cn":
            out += circle(cx, cy, 35, fill="white", stroke="none")
            out += circle(cx - 8, cy, 9, fill="#0f172a", stroke="none")
            out += circle(cx + 14, cy - 10, 6, fill="#0f172a", stroke="none")
            out += rect(cx + 20, cy + 6, 16, 16, fill="#0f172a", stroke="none")
        else:
            out += circle(cx, cy, 35, fill="white", stroke="none")
        return out
    s += rect(40, 100, 430, 224, fill="#fbfbfd", stroke=BLUE, sw=1.7, rx=12)
    s += text(255, 124, "ВІДКРИТТЯ = ерозія → дилатація", size=11,
              anchor="middle", weight="bold", fill=BLUE)
    s += box(80, 150, "on")
    s += text(155, 274, "цятки навколо", size=8.3, anchor="middle", fill=MUTE)
    s += line(238, 202, 276, 202, stroke=INK, w=1.6, marker="arr")
    s += box(290, 150, "oo")
    s += text(365, 274, "цятки геть, розмір той самий", size=8.3,
              anchor="middle", fill="#15803d")
    s += rect(490, 100, 430, 224, fill="#fbfbfd", stroke=GREEN, sw=1.7, rx=12)
    s += text(705, 124, "ЗАКРИТТЯ = дилатація → ерозія", size=11,
              anchor="middle", weight="bold", fill="#15803d")
    s += box(530, 150, "cn")
    s += text(605, 274, "дірки й щербини", size=8.3, anchor="middle", fill=MUTE)
    s += line(688, 202, 726, 202, stroke=INK, w=1.6, marker="arr")
    s += box(740, 150, "cc")
    s += text(815, 274, "залатано, розмір той самий", size=8.3,
              anchor="middle", fill="#15803d")
    s += rect(40, 340, 880, 64, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    steps = ["сіре / HSV", "поріг → маска", "морфологія", "чиста маска → 49.6"]
    bw2, x = 196, 70
    for i, st in enumerate(steps):
        s += rect(x, 352, bw2, 40, fill="white", stroke=BLUE, sw=1.3, rx=8)
        s += text(x + bw2 / 2, 376, st, size=9.5, anchor="middle",
                  weight="bold", fill=BLUE)
        if i < 3:
            s += line(x + bw2, 372, x + bw2 + 14, 372, stroke=INK, w=1.5,
                      marker="arr")
        x += bw2 + 14
    s += text(W / 2, H - 12,
              "Спершу поріг ріже кадр на чорне-біле, тоді морфологія прибирає "
              "цятки й латає дірки — і маска готова для пошуку об'єктів (49.6).",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.6.1 — Виявлення за кольором
# ════════════════════════════════════════════════════════════════════════════
def fig_color_blob():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "За кольором: маска → пляма → центр і рамка",
               "поріг у HSV (49.1) лишає лиш потрібний тон → чиста маска (49.5) → знаходимо білу пляму, її площу, центр і рамку")
    labels = ["кадр", "HSV-поріг → маска", "морфологія (49.5)",
              "пляма: центр + рамка"]

    def box(x, kind):
        bg = "#1e293b" if kind == "scene" else "#0a0d12"
        out = rect(x, 150, 180, 130, fill=bg, stroke=INK, sw=1.2)
        bcx, bcy, br = x + 92, 214, 30
        if kind == "scene":
            out += rect(x + 18, 166, 34, 30, fill="#2563eb", stroke="none")
            out += circle(x + 150, 250, 18, fill="#16a34a", stroke="none")
            out += circle(bcx, bcy, br, fill="#f59e0b", stroke="none")
        elif kind == "mask":
            out += circle(bcx, bcy, br, fill="white", stroke="none")
            out += rect(x + 24, 170, 7, 7, fill="white", stroke="none")
            out += rect(x + 150, 256, 6, 6, fill="white", stroke="none")
        elif kind == "clean":
            out += circle(bcx, bcy, br, fill="white", stroke="none")
        else:
            out += circle(bcx, bcy, br, fill="white", stroke="none")
            out += rect(bcx - br, bcy - br, 2 * br, 2 * br, fill="none",
                        stroke=GREEN, sw=2)
            out += line(bcx - 7, bcy, bcx + 7, bcy, stroke=RED, w=2)
            out += line(bcx, bcy - 7, bcx, bcy + 7, stroke=RED, w=2)
        return out
    xs = [40, 270, 500, 730]
    for i, x in enumerate(xs):
        s += box(x, ["scene", "mask", "clean", "result"][i])
        s += text(x + 90, 300, labels[i], size=9.3, anchor="middle",
                  weight="bold")
        if i < 3:
            s += line(x + 182, 215, x + 228, 215, stroke=INK, w=1.7,
                      marker="arr")
    s += rect(730, 318, 190, 86, fill=BOX2, stroke=GREEN, sw=1.4, rx=10)
    s += text(825, 340, "що дістаємо:", size=9.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(745, 358, ["• центр (cx, cy)", "• площа (скільки пікселів)",
                          "• габаритна рамка"], size=9, lh=15)
    s += text(W / 2, H - 14,
              "Колір — найдешевший сигнал: поріг у HSV, чистка маски, і пляма "
              "видає центр та рамка цілі. Тягне навіть МК.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.6.2 — Виявлення за формою
# ════════════════════════════════════════════════════════════════════════════
def fig_shape_contour():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "За формою: контур → кути → що це",
               "обвівши контур, рахуємо кути (3 → трикутник, 4 → квадрат) чи «круглість»; фільтруємо плями за площею й формою")

    def shape(x, kind, label, sub, col):
        out = rect(x, 138, 220, 172, fill="#0f172a", stroke=INK, sw=1.2)
        cx, cy = x + 110, 224
        if kind == "tri":
            pts = [(cx, cy - 52), (cx - 56, cy + 40), (cx + 56, cy + 40)]
            out += poly(pts, fill="none", stroke=col, sw=3, closed=True)
            for p in pts:
                out += circle(p[0], p[1], 5, fill=RED, stroke="white", sw=1)
        elif kind == "sq":
            pts = [(cx - 50, cy - 46), (cx + 50, cy - 46), (cx + 50, cy + 46),
                   (cx - 50, cy + 46)]
            out += poly(pts, fill="none", stroke=col, sw=3, closed=True)
            for p in pts:
                out += circle(p[0], p[1], 5, fill=RED, stroke="white", sw=1)
        else:
            out += circle(cx, cy, 52, fill="none", stroke=col, sw=3)
        out += text(x + 110, 324, label, size=11, anchor="middle",
                    weight="bold", fill=col)
        out += text(x + 110, 340, sub, size=8.6, anchor="middle", fill=MUTE)
        return out
    s += shape(60, "tri", "трикутник", "контур → 3 кути", BLUE)
    s += shape(370, "sq", "квадрат", "4 кути, ≈рівні сторони", GREEN)
    s += shape(680, "circ", "коло", "0 кутів, висока «круглість»", AMBER)
    s += rect(60, 356, 840, 64, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 378,
              "Плями ще й ФІЛЬТРУЮТЬ: за площею (відсіяти дрібне й завелике), за співвідношенням сторін (видовжене?),",
              size=9.6, anchor="middle", weight="bold")
    s += text(480, 398,
              "за «круглістю» (наскільки схоже на коло). Так із купи плям лишаються тільки потрібні.",
              size=9.3, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 12,
              "Форму впізнають за контуром: скільки в нього кутів і яка «круглість». "
              "Простий і прозорий спосіб — без жодного навчання.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.6.3 — Перетворення Хафа
# ════════════════════════════════════════════════════════════════════════════
def fig_hough():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Перетворення Хафа: голосуванням знайти лінії (і кола)",
               "кожна точка межі «голосує» за всі лінії, що крізь неї проходять; де голоси збігаються — там лінія (стійко до розривів)")
    th0, rho0 = 1.0, 20.0
    ct, st = math.cos(th0), math.sin(th0)
    xsl = [-50, -30, -10, 20, 40, 55]
    P = [(x, (rho0 - x * ct) / st) for x in xsl]
    s += text(170, 112, "точки межі (з розривами, шумом)", size=9.3,
              anchor="middle", weight="bold")
    s += rect(60, 126, 220, 154, fill="#0f172a", stroke=INK, sw=1.2)
    for (x, y) in P:
        s += circle(170 + x * 1.4, 203 - y * 1.1, 4, fill="#f8fafc",
                    stroke="none")
    for nx, ny in [(118, 168), (232, 244), (96, 246)]:
        s += circle(nx, ny, 3, fill="#64748b", stroke="none")
    s += text(490, 112, "простір (ρ, θ): кожна точка → синусоїда", size=9.3,
              anchor="middle", weight="bold")
    s += rect(340, 126, 300, 154, fill="#0f172a", stroke=INK, sw=1.2)
    for (x, y) in P:
        curve = []
        for k in range(31):
            th = math.pi * k / 30
            rho = x * math.cos(th) + y * math.sin(th)
            curve.append((340 + th / math.pi * 296 + 2, 203 - rho * 0.74))
        s += poly(curve, fill="none", stroke="#60a5fa", sw=1.3, closed=False)
    pxk = 340 + th0 / math.pi * 296 + 2
    pyk = 203 - rho0 * 0.74
    s += circle(pxk, pyk, 8, fill="none", stroke=RED, sw=2.6)
    s += text(pxk, pyk - 14, "пік = лінія", size=8.5, anchor="middle", fill=RED,
              weight="bold")
    s += text(820, 112, "пік голосів → лінія", size=9.3, anchor="middle",
              weight="bold")
    s += rect(700, 126, 220, 154, fill="#0f172a", stroke=INK, sw=1.2)
    for (x, y) in P:
        s += circle(810 + x * 1.4, 203 - y * 1.1, 4, fill="#f8fafc",
                    stroke="none")
    a = (rho0 * ct - 70 * st, rho0 * st + 70 * ct)
    b = (rho0 * ct + 70 * st, rho0 * st - 70 * ct)
    s += line(810 + a[0] * 1.4, 203 - a[1] * 1.1, 810 + b[0] * 1.4,
              203 - b[1] * 1.1, stroke=GREEN, w=2.4)
    s += rect(60, 300, 860, 104, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(490, 324, "Чому це сильно", size=11, anchor="middle",
              weight="bold")
    s += lines(90, 346,
               ["• навіть якщо лінія РОЗІРВАНА чи в шумі — голоси справжніх точок усе одно збираються в один пік;",
                "• так само ловлять КОЛА: кожна точка голосує за всі кола (центр + радіус), що крізь неї; пік у (cx, cy, r) — коло;",
                "• звідси — лінія горизонту, край злітної смуги, дорожня розмітка, круглий посадковий майданчик."],
               size=9.4, lh=21)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.6.4 — Шаблон, мітка, набір інструментів
# ════════════════════════════════════════════════════════════════════════════
def fig_template_toolbox():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "За шаблоном, за міткою — і коли що брати",
               "шаблон ковзає кадром, шукаючи збіг; спеціальні мітки (ArUco/AprilTag) дають надійний ID і позу — основа точної посадки")
    s += rect(40, 104, 280, 210, fill="#fbfbfd", stroke=BLUE, sw=1.7, rx=12)
    s += text(180, 128, "ШАБЛОН ковзає → збіг", size=10.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += rect(70, 144, 220, 130, fill="#10131a", stroke=INK, sw=1.1)
    for k in range(9):
        s += rect(86 + (k * 53) % 190, 158 + (k * 37) % 96, 12, 12,
                  fill="#334155", stroke="none")
    s += rect(150, 196, 40, 40, fill="none", stroke="#f59e0b", sw=2)
    s += rect(150, 196, 40, 40, fill="#f59e0b", stroke="none", opacity=0.2)
    s += text(170, 290, "найбільша схожість = тут", size=8.4, anchor="middle",
              fill=MUTE)
    s += rect(340, 104, 280, 210, fill="#fbfbfd", stroke=AMBER, sw=1.7, rx=12)
    s += text(480, 128, "МІТКА (ArUco / AprilTag)", size=10.5, anchor="middle",
              weight="bold", fill="#b06b00")
    mx, my, mc = 420, 150, 24
    pat = [[1, 1, 1, 1, 1], [1, 0, 0, 1, 1], [1, 1, 0, 0, 1], [1, 0, 1, 0, 1],
           [1, 1, 1, 1, 1]]
    for r in range(5):
        for c in range(5):
            s += rect(mx + c * mc, my + r * mc, mc, mc,
                      fill=("#000000" if pat[r][c] else "#ffffff"),
                      stroke="none")
    s += rect(mx, my, 5 * mc, 5 * mc, fill="none", stroke=INK, sw=1)
    s += text(480, 290, "дає ID + позу → точна посадка", size=8.6,
              anchor="middle", fill=MUTE)
    s += rect(640, 104, 280, 210, fill=PANEL, stroke=INK, sw=1.7, rx=12)
    s += text(780, 128, "який сигнал — такий метод", size=10.5, anchor="middle",
              weight="bold")
    s += lines(660, 156,
               ["• КОЛІР помітний → HSV-пляма",
                "• ГЕОМЕТРІЯ → кути / круглість",
                "• ЛІНІЇ, КОЛА → Хаф (стійко)",
                "• відомий ВЗІРЕЦЬ → шаблон",
                "• надійний маркер → ArUco /",
                "  AprilTag (посадка)"], size=9.3, lh=21)
    s += rect(656, 286, 248, 22, fill="#eafaef", stroke=GREEN, sw=1, rx=5)
    s += text(780, 301, "надто різні об'єкти → 49.7", size=9, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(W / 2, H - 14,
              "Класичні детектори дешеві, прозорі й без навчання — бери їх, коли "
              "ціль чітко задана кольором, формою чи взірцем.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.7.1 — Чому навчання, а не правило
# ════════════════════════════════════════════════════════════════════════════
def fig_why_learn():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Чому не правило, а навчання",
               "рукотворне правило (49.6) ловить просту ціль, та безсиле перед «людиною» чи «авто» — надто різні; тож детектор НАВЧАЮТЬ")
    s += rect(50, 108, 400, 250, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(250, 132, "проста ціль → рукотворне правило ✓", size=10.5,
              anchor="middle", weight="bold", fill="#15803d")
    s += circle(250, 206, 42, fill="#f59e0b", stroke=INK, sw=1.4)
    s += text(250, 270, "м'яч: ОДИН колір", size=10, anchor="middle",
              weight="bold")
    s += text(250, 290, "→ поріг у HSV і все (49.6)", size=9, anchor="middle",
              fill=MUTE)
    s += text(250, 328, "просте, дешеве, зрозуміле", size=9, anchor="middle",
              fill="#15803d")
    s += rect(510, 108, 400, 250, fill="#fef2f2", stroke=RED, sw=1.8, rx=12)
    s += text(710, 132, "мінлива ціль → правила НЕМА ✗", size=10.5,
              anchor="middle", weight="bold", fill=RED)
    for dx, sc in [(566, 1.0), (628, 0.8), (690, 1.15), (752, 0.72),
                   (812, 0.95)]:
        s += circle(dx, 182, 8 * sc, fill="#64748b", stroke="none")
        s += rect(dx - 7 * sc, 192, 14 * sc, 44 * sc, fill="#64748b",
                  stroke="none")
    s += text(710, 268, "людина: тисячі поз, одеж, ракурсів", size=9.5,
              anchor="middle", weight="bold")
    s += text(710, 288, "який єдиний «колір» чи «форма»? — жодних", size=9,
              anchor="middle", fill=MUTE)
    s += text(710, 326, "рукотворне правило тут безсиле", size=9,
              anchor="middle", fill=RED)
    s += rect(110, 376, 740, 46, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 398,
              "Розв'язок: не вигадувати правило, а показати мережі МІЛЬЙОНИ прикладів —",
              size=10, anchor="middle", weight="bold", fill=BLUE)
    s += text(480, 414,
              "хай вона САМА виведе, як виглядає «людина». Це і є навчання.",
              size=9.5, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.7.2 — Навчання проти інференсу
# ════════════════════════════════════════════════════════════════════════════
def fig_train_vs_infer():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Навчання проти інференсу: написати рецепт чи зварити за ним",
               "навчання — мільйони прикладів підганяють ваги (важко, раз, у хмарі); інференс — готова модель відповідає на кадр (на борту)")
    s += rect(50, 104, 388, 248, fill="#fbfbfd", stroke=AMBER, sw=1.8, rx=12)
    s += text(244, 128, "НАВЧАННЯ (раз, у хмарі)", size=11, anchor="middle",
              weight="bold", fill="#b06b00")
    for i in range(6):
        x = 86 + (i % 3) * 70
        y = 148 + (i // 3) * 44
        s += rect(x, y, 56, 34, fill="#1e293b", stroke=INK, sw=0.8)
        s += rect(x, y, 56, 8, fill=GREEN, stroke="none", opacity=0.4)
    s += text(244, 252, "мільйони прикладів із мітками", size=9,
              anchor="middle", fill=MUTE)
    s += text(244, 274, "↓ підганяють МІЛЬЙОНИ ваг", size=9.5, anchor="middle",
              weight="bold")
    s += text(244, 292, "↓ щоб помилка стала найменша", size=9, anchor="middle",
              fill=MUTE)
    s += text(244, 326, "важко, повільно · GPU / хмара", size=9,
              anchor="middle", weight="bold", fill="#b06b00")
    s += line(442, 220, 518, 220, stroke=INK, w=2, marker="arr")
    s += text(480, 208, "модель", size=8.5, anchor="middle", weight="bold")
    s += text(480, 240, "(файл ваг)", size=7.5, anchor="middle", fill=MUTE)
    s += rect(522, 104, 388, 248, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(716, 128, "ІНФЕРЕНС (щокадру, на борту)", size=11,
              anchor="middle", weight="bold", fill="#15803d")
    s += rect(552, 150, 84, 58, fill="#1e293b", stroke=INK, sw=1)
    s += text(594, 222, "новий кадр", size=8.5, anchor="middle", fill=MUTE)
    s += line(640, 178, 686, 178, stroke=INK, w=1.8, marker="arr")
    s += rect(692, 150, 188, 58, fill=BOX2, stroke=GREEN, sw=1.4, rx=8)
    s += text(786, 174, "готова модель", size=9, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(786, 192, "→ відповідь", size=9, anchor="middle", fill="#15803d")
    s += text(716, 252, "легше, швидко · на пристрої", size=9, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(716, 290, "рецепт пишуть РАЗ (важко);", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(716, 308, "варять за ним ЩОРАЗУ (легше)", size=9.5,
              anchor="middle", fill=MUTE)
    s += rect(110, 374, 740, 48, fill="#fffbeb", stroke=AMBER, sw=1.5, rx=10)
    s += text(480, 396,
              "ДРОН РОБИТЬ ЛИШЕ ІНФЕРЕНС: він запускає модель, яку навчив хтось інший —",
              size=10, anchor="middle", weight="bold", fill="#92400e")
    s += text(480, 412, "і не вчиться сам у польоті.", size=9.5,
              anchor="middle", fill="#92400e")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.7.3 — Вхід/вихід детектора
# ════════════════════════════════════════════════════════════════════════════
def fig_detector_io():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Що видає нейромережа-детектор: рамки, клас, упевненість",
               "кадр → навчені згортки (49.3, але ваги вивчені, не рукотворні) → список: рамка + клас + упевненість")
    s += text(150, 118, "вхід: кадр", size=10, anchor="middle", weight="bold")
    s += rect(70, 132, 160, 130, fill="#1e293b", stroke=INK, sw=1.2)
    s += circle(118, 180, 8, fill="#94a3b8", stroke="none")
    s += rect(111, 190, 14, 40, fill="#94a3b8", stroke="none")
    s += rect(158, 210, 50, 26, fill="#64748b", stroke="none")
    s += circle(170, 238, 6, fill="#334155", stroke="none")
    s += circle(198, 238, 6, fill="#334155", stroke="none")
    s += line(238, 197, 286, 197, stroke=INK, w=1.7, marker="arr")
    s += text(420, 118, "навчені згортки (CNN)", size=10, anchor="middle",
              weight="bold")
    for i in range(5):
        x = 300 + i * 32
        s += rect(x, 150, 22, 104 - i * 9, fill=BOX1, stroke=BLUE, sw=1.2)
    s += text(420, 272, "ядра ВИВЧЕНІ під час навчання", size=8.6,
              anchor="middle", fill=MUTE)
    s += text(420, 286, "(а не рукотворні, як Собель)", size=8.6,
              anchor="middle", fill=MUTE)
    s += line(470, 197, 524, 197, stroke=INK, w=1.7, marker="arr")
    s += text(720, 118, "вихід: рамки + клас + упевненість", size=10,
              anchor="middle", weight="bold")
    s += rect(560, 132, 320, 130, fill="#1e293b", stroke=INK, sw=1.2)
    s += circle(612, 182, 8, fill="#94a3b8", stroke="none")
    s += rect(605, 192, 14, 40, fill="#94a3b8", stroke="none")
    s += rect(596, 170, 40, 66, fill="none", stroke=GREEN, sw=2)
    s += text(616, 164, "людина 0.94", size=8, anchor="middle", fill="#22c55e",
              weight="bold")
    s += rect(720, 208, 50, 26, fill="#64748b", stroke="none")
    s += rect(712, 200, 66, 42, fill="none", stroke=AMBER, sw=2)
    s += text(745, 194, "авто 0.88", size=8, anchor="middle", fill=AMBER,
              weight="bold")
    s += rect(110, 300, 740, 96, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 324, "Детектор повертає СПИСОК знахідок", size=11,
              anchor="middle", weight="bold")
    s += lines(140, 348,
               ["• де — габаритна рамка; що — клас (людина, авто, …); наскільки певен — упевненість 0…1;",
                "• усередині — стос ЗГОРТОК (49.3), але їхні ядра не придумані рукою, а вивчені на прикладах;",
                "• поріг упевненості відсікає слабкі здогади (напр., лишити тільки ≥ 0.5)."],
               size=9.5, lh=21)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.7.4 — Інференс на борту: ціна
# ════════════════════════════════════════════════════════════════════════════
def fig_onboard_cost():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Інференс на борту: чим і за скільки",
               "навіть інференс — мільйони множень; потрібен спроможний чип (борткомп'ютер чи прискорювач), не голий МК; рятують малі й квантовані моделі")
    s += text(195, 116, "чим рахувати", size=10.5, anchor="middle",
              weight="bold")
    rungs = [("голий МК", "✗ не тягне детектор", RED, 70),
             ("Raspberry Pi", "кілька кадрів/с", AMBER, 120),
             ("Jetson / TPU·NPU", "реальний час", GREEN, 170)]
    base = 350
    for i, (lab, d, col, h) in enumerate(rungs):
        x = 60 + i * 110
        s += rect(x, base - h, 96, h, fill=col, stroke=INK, sw=1.4, rx=6,
                  opacity=0.2)
        s += rect(x, base - h, 96, 4, fill=col, stroke="none")
        s += text(x + 48, base - h + 22, lab, size=9, anchor="middle",
                  weight="bold", fill=col)
        s += text(x + 48, base + 16, d, size=8, anchor="middle", fill=MUTE)
    s += line(55, base, 400, base, stroke=INK, w=1.3)
    s += text(60, base + 34, "слабкий →", size=8.5, fill=MUTE)
    s += text(390, base + 34, "→ потужніший (і ненажерливіший)", size=8.5,
              anchor="end", fill=MUTE)
    s += rect(440, 128, 480, 120, fill=BOX1, stroke=BLUE, sw=1.5, rx=11)
    s += text(680, 150, "як прискорити інференс", size=10.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(460, 172,
               ["• менша модель (напр. MobileNet) — менше шарів і ваг;",
                "• квантування: ваги 8-біт замість 32 → швидше й менше;",
                "• апаратний прискорювач (TPU / NPU) робить згортки гуртом;",
                "• нижча роздільність кадру — менше пікселів рахувати."],
               size=9, lh=18)
    s += rect(440, 262, 480, 138, fill=PANEL, stroke=INK, sw=1.4, rx=11)
    s += text(680, 284, "за що любимо · чим платимо", size=10.5,
              anchor="middle", weight="bold")
    s += lines(460, 306,
               ["+ загальна: ловить різноманітні цілі, яких правилом не задаси;",
                "+ стійка до поз, ракурсів, освітлення;",
                "− треба гори даних і обчислень (навчання);",
                "− «чорна скриня»: важко знати, ЧОМУ так вирішила;",
                "− буває ВПЕВНЕНО помиляється (хибна знахідка на порожньому)."],
               size=9, lh=17.5)
    s += text(W / 2, H - 12,
              "Інференс — теж робота: для реального часу на борту потрібен "
              "спроможний чип. Скільки саме коштує — у 49.9.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.s7.1 — Гірки нейромереж
# ════════════════════════════════════════════════════════════════════════════
def fig_nn_timeline():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Гірки нейромереж: від перцептрона до AlexNet",
               "1958 захват → 1969 «зима» → 1986 воскресіння (зворотне поширення) → 1998 згорткові → 2012 прорив")
    ax, ay = 70, 400
    s += line(ax, ay, ax + 840, ay, stroke=INK, w=1.4, marker="arr")
    s += text(ax + 838, ay + 22, "час →", size=9.5, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ax - 6, 132, "↑ поступ / увага", size=9, fill=MUTE,
              weight="bold")
    miles = [(130, 300, "1958", "Перцептрон", "перша машина,", "що ВЧИТЬСЯ",
              GREEN),
             (320, 372, "1969", "«Зима»", "Мінський і Паперт:", "XOR не взяти",
              RED),
             (530, 252, "1986", "Зворотне", "поширення —", "багато шарів",
              BLUE),
             (680, 232, "1998", "LeNet", "згорткові мережі", "читають цифри",
              BLUE),
             (850, 150, "2012", "AlexNet", "глибока CNN", "виграє ImageNet",
              GREEN)]
    s += poly([(m[0], m[1]) for m in miles], fill="none", stroke="#94a3b8",
              sw=2.6, closed=False)
    for x, y, yr, nm, d1, d2, col in miles:
        s += circle(x, y, 6, fill=col, stroke=INK, sw=1.3)
        above = y > 280
        ty = y - 58 if above else y + 16
        s += text(x, ty, yr, size=11, anchor="middle", weight="bold", fill=col)
        s += text(x, ty + 15, nm, size=10, anchor="middle", weight="bold")
        s += text(x, ty + 29, d1, size=8, anchor="middle", fill=MUTE)
        s += text(x, ty + 40, d2, size=8, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Двічі нейромережі ховали як глухий кут — і двічі вони верталися. "
              "Утретє, 2012-го, вони перемогли остаточно.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.s7.2 — Стіна XOR
# ════════════════════════════════════════════════════════════════════════════
def fig_perceptron_xor():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Стіна XOR: чому одного шару замало",
               "перцептрон креслить ОДНУ пряму межу — а XOR нею не розділиш; багатошарова мережа (зі зворотним поширенням) гне межу")
    s += rect(40, 100, 280, 250, fill="#fbfbfd", stroke=INK, sw=1.5, rx=12)
    s += text(180, 124, "один нейрон (перцептрон)", size=10, anchor="middle",
              weight="bold")
    s += circle(90, 180, 9, fill=BLUE, stroke=INK, sw=1)
    s += circle(90, 240, 9, fill=BLUE, stroke=INK, sw=1)
    s += text(70, 184, "x₁", size=10, anchor="end")
    s += text(70, 244, "x₂", size=10, anchor="end")
    s += circle(190, 210, 18, fill=PANEL, stroke=INK, sw=1.4)
    s += text(190, 214, "Σ", size=14, anchor="middle", weight="bold")
    s += line(99, 182, 174, 206, stroke=MUTE, w=1.4)
    s += line(99, 238, 174, 216, stroke=MUTE, w=1.4)
    s += text(140, 188, "w₁", size=8, fill=MUTE)
    s += text(140, 240, "w₂", size=8, fill=MUTE)
    s += line(208, 210, 246, 210, stroke=INK, w=1.4, marker="arr")
    s += rect(248, 196, 44, 28, fill="white", stroke=INK, sw=1.2, rx=5)
    s += text(270, 214, "поріг", size=8, anchor="middle")
    s += text(180, 300, "зважена сума + поріг", size=9, anchor="middle",
              fill=MUTE)
    s += text(180, 316, "= ОДНА пряма межа", size=9, anchor="middle",
              weight="bold")

    def plane(x0, title_t, ok):
        out = rect(x0, 100, 280, 250, fill="#0f172a", stroke=INK, sw=1.5,
                   rx=12)
        out += text(x0 + 140, 124, title_t, size=10, anchor="middle",
                    weight="bold", fill=("#22c55e" if ok else RED))
        gx, gy, g = x0 + 70, 300, 130
        pts = [(0, 0, BLUE), (1, 1, BLUE), (0, 1, RED), (1, 0, RED)]
        for px, py, c in pts:
            out += circle(gx + px * g, gy - py * g, 11, fill=c, stroke="white",
                          sw=1.5)
        if ok:
            curve = [(gx - 10, gy - 0.30 * g), (gx + 0.5 * g, gy - 0.62 * g),
                     (gx + g + 10, gy - 0.30 * g)]
            out += poly(curve, fill="none", stroke="#22c55e", sw=2.6,
                        closed=False)
            curve2 = [(gx - 10, gy - 0.70 * g), (gx + 0.5 * g, gy - 0.38 * g),
                      (gx + g + 10, gy - 0.70 * g)]
            out += poly(curve2, fill="none", stroke="#22c55e", sw=2.6,
                        closed=False)
        else:
            out += line(gx - 10, gy - 0.85 * g, gx + g + 10, gy + 0.05 * g,
                        stroke=RED, w=2.6, dash="6,4")
        return out
    s += plane(340, "XOR: одна пряма НЕ ділить ✗", False)
    s += plane(640, "кілька шарів — межа гнеться ✓", True)
    s += text(W / 2, H - 14,
              "Сині й червоні точки XOR не розрізати однією прямою. Багато шарів "
              "(навчених зворотним поширенням, 1986) гнуть межу — і беруть її.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.s7.3 — Три інгредієнти
# ════════════════════════════════════════════════════════════════════════════
def fig_three_ingredients():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому саме 2012: три інгредієнти нарешті зійшлися",
               "ідея згорткових мереж була давно; бракувало даних і обчислень — поки не з'явилися ImageNet і GPU")
    cards = [("ДАНІ", BLUE, ["ImageNet (2009):", "мільйони мічених",
                             "фото, 1000 класів", "→ є на чому вчити"]),
             ("ОБЧИСЛЕННЯ", AMBER, ["GPU:", "тисячі ядер рахують",
                                    "згортки гуртом", "→ навчання за дні"]),
             ("АЛГОРИТМ", GREEN, ["глибока CNN +", "зворотне поширення",
                                  "+ ReLU, dropout", "→ глибше й стійкіше"])]
    xs = [70, 360, 650]
    for i, (t, col, rows) in enumerate(cards):
        x = xs[i]
        s += rect(x, 110, 220, 184, fill=PANEL, stroke=col, sw=1.9, rx=12)
        s += rect(x, 110, 220, 34, fill=col, stroke="none", rx=10,
                  opacity=0.16)
        s += text(x + 110, 133, t, size=12, anchor="middle", weight="bold",
                  fill=col)
        s += lines(x + 20, 168, rows, size=9.6, lh=23)
        if i < 2:
            s += text(xs[i] + 232, 206, "+", size=22, anchor="middle",
                      weight="bold", fill=MUTE)
        s += line(x + 110, 296, 480, 348, stroke="#cbd5e1", w=1.3)
    s += rect(360, 350, 240, 70, fill=BOX2, stroke=GREEN, sw=2.2, rx=12)
    s += text(480, 376, "усі три разом", size=10.5, anchor="middle",
              weight="bold")
    s += text(480, 402, "= AlexNet (2012)", size=14, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(150, 372,
              "сама лиш ідея чекала", size=9, anchor="middle", fill=MUTE,
              italic=True)
    s += text(150, 386, "на дані й залізо", size=9, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.s7.4 — Мить AlexNet
# ════════════════════════════════════════════════════════════════════════════
def fig_alexnet_moment():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "AlexNet, 2012: мить, коли зір став глибоким",
               "на змаганні ImageNet глибока мережа збила помилку з 26% до 15%, і відтоді машинний зір пішов у глибоке навчання")
    ox, oy, maxh = 150, 360, 250
    s += line(ox - 20, oy, 850, oy, stroke=INK, w=1.4)
    s += text(ox - 28, 132, "помилка (top-5), %", size=9, fill=MUTE,
              weight="bold")
    hy = oy - 5.0 / 30 * maxh
    s += line(ox - 20, hy, 800, hy, stroke=RED, w=1.4, dash="5,4")
    s += text(805, hy + 3, "люди ≈ 5%", size=8.5, fill=RED, weight="bold")
    bars = [("2011", "класика (не нейро)", 26.2, AMBER),
            ("2012", "AlexNet (глибока CNN)", 15.3, GREEN),
            ("2014", "ще глибше", 7.0, GREEN),
            ("2015", "нижче людини", 3.6, GREEN)]
    bw, gap = 120, 56
    for i, (yr, lab, err, col) in enumerate(bars):
        x = ox + i * (bw + gap)
        h = err / 30 * maxh
        s += rect(x, oy - h, bw, h, fill=col, stroke=INK, sw=1.2, rx=4,
                  opacity=0.85)
        s += text(x + bw / 2, oy - h - 8, f"{err}%", size=12, anchor="middle",
                  weight="bold", fill=col)
        s += text(x + bw / 2, oy + 16, yr, size=10, anchor="middle",
                  weight="bold")
        s += text(x + bw / 2, oy + 30, lab, size=7.8, anchor="middle",
                  fill=MUTE)
    x1 = ox + bw / 2
    x2 = ox + (bw + gap) + bw / 2
    s += line(x1, oy - 26.2 / 30 * maxh - 26, x2, oy - 15.3 / 30 * maxh - 26,
              stroke=RED, w=1.6, marker="arrR")
    s += text((x1 + x2) / 2, oy - 250, "−11% за рік!", size=10,
              anchor="middle", fill=RED, weight="bold")
    s += rect(60, 392, 840, 30, fill=BOX2, stroke=GREEN, sw=1.3, rx=8)
    s += text(480, 412,
              "У нашому дроні — правнуки AlexNet: ті самі навчені згортки, лише компактніші, для бортового інференсу (49.7).",
              size=10, anchor="middle", weight="bold", fill="#15803d")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.8.1 — Виявлення проти трекінгу
# ════════════════════════════════════════════════════════════════════════════
def fig_detect_vs_track():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Виявлення проти трекінгу: знайти раз, далі вести",
               "виявлення працює щокадру з нуля (дорого, може блимати й губитися); трекінг веде знайдену ціль (дешевше, з передбаченням)")
    fx = [70, 240, 410, 580, 750]
    fw, fh = 140, 90
    tgt = [(30, 1), (60, 1), (0, 0), (110, 1), (135, 1)]
    s += text(60, 118, "ВИЯВЛЕННЯ — щокадру з нуля", size=10.5, weight="bold",
              fill="#b06b00")
    for i, x in enumerate(fx):
        s += rect(x, 130, fw, fh, fill="#1e293b", stroke=INK, sw=1.1)
        tx, ok = tgt[i]
        cx = x + 20 + tx * 0.8
        s += circle(cx, 175, 11, fill="#f59e0b", stroke="none")
        if ok:
            s += rect(cx - 16, 159, 32, 32, fill="none", stroke=GREEN, sw=2)
        else:
            s += text(cx, 201, "✗ загубив", size=8, anchor="middle", fill=RED,
                      weight="bold")
        s += text(x + fw / 2, 236, f"кадр {i + 1}", size=8, anchor="middle",
                  fill=MUTE)
    s += text(60, 270, "ТРЕКІНГ — веде знайдену ціль", size=10.5,
              weight="bold", fill="#15803d")
    centers = []
    for i, x in enumerate(fx):
        s += rect(x, 282, fw, fh, fill="#0f172a", stroke=INK, sw=1.1)
        tx, ok = tgt[i]
        cx = x + 20 + tx * 0.8
        centers.append((cx, 327))
    s += poly(centers, fill="none", stroke="#60a5fa", sw=1.4, closed=False)
    for i, x in enumerate(fx):
        tx, ok = tgt[i]
        cx = x + 20 + tx * 0.8
        s += circle(cx, 327, 11, fill="#f59e0b", stroke="none")
        col = GREEN if ok else BLUE
        s += rect(cx - 16, 311, 32, 32, fill="none", stroke=col, sw=2,
                  dash=(None if ok else "4,3"))
        if not ok:
            s += text(cx, 357, "передбачив", size=7.5, anchor="middle",
                      fill=BLUE, weight="bold")
    s += text(W / 2, H - 26,
              "Виявлення дороге й блимає; трекінг веде ту саму ціль дешевше й неперервно,",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 12,
              "а коли кадр випав — ПЕРЕДБАЧАЄ положення (Кальман, 46), тож не губить.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.8.2 — Піксель → кут
# ════════════════════════════════════════════════════════════════════════════
def fig_pixel_to_angle():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Піксель → кут: де ціль відносно камери",
               "детектор дає піксель; щоб діяти, потрібен КУТ; зсув пікселя від центру в межах поля зору (FOV) → кутовий зсув")
    s += text(230, 116, "кадр із детектора", size=10, anchor="middle",
              weight="bold")
    s += rect(90, 130, 280, 175, fill="#1e293b", stroke=INK, sw=1.2)
    ccx, ccy = 230, 217
    s += line(ccx, 138, ccx, 297, stroke="#475569", w=1, dash="3,3")
    s += line(98, ccy, 362, ccy, stroke="#475569", w=1, dash="3,3")
    s += text(ccx + 30, 150, "центр", size=8, fill="#94a3b8")
    s += circle(158, ccy, 13, fill="#f59e0b", stroke="white", sw=1.4)
    s += line(ccx, ccy, 158, ccy, stroke=RED, w=1.8)
    s += text(196, 206, "зсув 120 px", size=8.5, anchor="middle", fill=RED,
              weight="bold")
    s += text(700, 116, "поле зору камери (згори)", size=10, anchor="middle",
              weight="bold")
    apex = (700, 140)
    s += poly([apex, (560, 320), (840, 320)], fill="#dbeafe", stroke=BLUE,
              sw=1.4, closed=True)
    s += line(apex[0], apex[1], 700, 320, stroke="#475569", w=1, dash="3,3")
    s += text(700, 336, "вісь камери", size=8, anchor="middle", fill=MUTE)
    s += text(700, 300, "FOV 60°", size=9, anchor="middle", fill=BLUE,
              weight="bold")
    ang = math.radians(11)
    tx2 = apex[0] - math.sin(ang) * 178
    ty2 = apex[1] + math.cos(ang) * 178
    s += line(apex[0], apex[1], tx2, ty2, stroke=RED, w=2, marker="arrR")
    s += circle(tx2, ty2, 9, fill="#f59e0b", stroke="white", sw=1.2)
    s += text(tx2 - 18, ty2 + 4, "ціль", size=8.5, anchor="end", fill=RED,
              weight="bold")
    s += text(636, 210, "≈ 11° ліворуч", size=9.5, anchor="middle", fill=RED,
              weight="bold")
    s += rect(120, 330, 720, 86, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 354, "кут ≈ (зсув у пікселях / півширина кадру) × (FOV / 2)",
              size=12, anchor="middle", weight="bold")
    s += text(480, 378,
              "точніше: кут = atan( зсув / фокусна_відстань_у_пікселях )",
              size=10, anchor="middle", fill=MUTE)
    s += text(480, 400,
              "приклад: 120 px при півширині 320 px і FOV 60° → ≈ 11° (точне число залежить від камери — її КАЛІБРУЮТЬ)",
              size=8.6, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.8.3 — Петля візуального керування
# ════════════════════════════════════════════════════════════════════════════
def fig_visual_servo_loop():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Замикання петлі: зір як датчик керування",
               "кутова похибка стає сигналом для регулятора (PID): він крутить апарат / підвіс, щоб повернути ціль у центр кадру")
    boxes = [("Камера", "кадр", BLUE), ("Виявити / вести", "49.1–49.7", BLUE),
             ("Піксель → кут", "FOV / фокус", AMBER),
             ("Регулятор PID", "по кутовій похибці", GREEN),
             ("Виконавці", "рискання · підвіс", GREEN)]
    xs = [40, 218, 396, 574, 752]
    bw = 168
    for i, (t, d, col) in enumerate(boxes):
        x = xs[i]
        s += rect(x, 160, bw, 70, fill="#0f172a", stroke=col, sw=1.8, rx=9)
        s += text(x + bw / 2, 190, t, size=10.5, anchor="middle",
                  weight="bold", fill=col)
        s += text(x + bw / 2, 210, d, size=8.4, anchor="middle", fill="#cbd5e1")
        if i < 4:
            s += line(x + bw, 195, x + bw + 10, 195, stroke=INK, w=1.8,
                      marker="arr")
    s += line(836, 232, 836, 300, stroke=INK, w=1.7)
    s += line(836, 300, 124, 300, stroke=INK, w=1.7)
    s += line(124, 300, 124, 234, stroke=INK, w=1.7, marker="arr")
    s += text(480, 292,
              "апарат повертається → ціль вертається до центру кадру → петля замикається",
              size=10, anchor="middle", fill=MUTE, weight="bold")
    s += rect(150, 330, 660, 84, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 354,
              "Зір тут — просто ще один ДАТЧИК у звичній петлі керування.", size=11,
              anchor="middle", weight="bold", fill=BLUE)
    s += lines(190, 374,
               ["• «помилка» = наскільки ціль НЕ в центрі (кутовий зсув);",
                "• регулятор (той самий PID) крутить рискання чи підвіс, доки помилка → 0."],
               size=9.5, lh=20)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.8.4 — Застосунки й затримка
# ════════════════════════════════════════════════════════════════════════════
def fig_apps_latency():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Де це працює — і чому пильнувати затримку",
               "точна посадка по мітці, стеження за ціллю, політ за лінією; та зір повільний — петля має лаг, тож м'які підсилення й передбачення")
    apps = [("точна посадка", ["мітка → кут → корекція",
                               "ArduPilot: LANDING_TARGET"], GREEN),
            ("стеження за ціллю", ["тримати ціль у центрі",
                                   "(підвіс / рискання)"], BLUE),
            ("політ за лінією", ["кут лінії → рискання",
                                 "(лінія з Хафа, 49.6)"], AMBER)]
    for i, (t, rows, col) in enumerate(apps):
        x = 50 + i * 290
        s += rect(x, 102, 270, 104, fill=PANEL, stroke=col, sw=1.8, rx=11)
        s += text(x + 135, 126, t, size=11, anchor="middle", weight="bold",
                  fill=col)
        s += lines(x + 22, 152, rows, size=9.3, lh=19)
    s += rect(50, 222, 860, 92, fill="#fffbeb", stroke=AMBER, sw=1.5, rx=11)
    s += text(480, 244, "Зір ПОВІЛЬНИЙ — петля бачить трохи минуле", size=11,
              anchor="middle", weight="bold", fill="#92400e")
    s += lines(82, 266,
               ["• інференс (49.7) і затримка тракту (48.5) додають лаг → ризик розгойдування;",
                "• лік: М'ЯКІ підсилення PID, ПЕРЕДБАЧЕННЯ між кадрами (Кальман, 46), і ЗАПАСНИЙ план, якщо ціль зникла."],
               size=9.5, lh=21)
    chain = [("Бортовий комп'ютер", "зір: детектор + трекінг", BLUE),
             ("MAVLink", "кут / координати цілі", INK),
             ("Політний контролер", "замикає петлю → мотори", GREEN)]
    x = 80
    for i, (t, d, col) in enumerate(chain):
        s += rect(x, 340, 250, 56, fill="white", stroke=col, sw=1.6, rx=9)
        s += text(x + 125, 362, t, size=10, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 125, 380, d, size=8.2, anchor="middle", fill=MUTE)
        if i < 2:
            s += line(x + 250, 368, x + 288, 368, stroke=INK, w=1.7,
                      marker="arr")
        x += 288
    s += text(W / 2, H - 12,
              "На апараті зір зазвичай живе в бортовому комп'ютері, а кут цілі "
              "йде по MAVLink у політний контролер — той і замикає петлю.",
              size=10, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.9.1 — Бюджети летючого робота
# ════════════════════════════════════════════════════════════════════════════
def fig_budgets():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Усе коштує: бюджети летючого робота",
               "кожна дія зору витрачає обчислення, пам'ять, ВАТИ й ГРАМИ — а важчий «мозок» з'їдає час польоту")
    cx, cy = 480, 226
    s += line(cx - 46, cy - 30, cx + 46, cy + 30, stroke=INK, w=3)
    s += line(cx - 46, cy + 30, cx + 46, cy - 30, stroke=INK, w=3)
    for ox, oy in [(-46, -30), (46, -30), (-46, 30), (46, 30)]:
        s += circle(cx + ox, cy + oy, 14, fill="none", stroke=INK, sw=2.4)
    s += rect(cx - 18, cy - 13, 36, 26, fill=PANEL, stroke=INK, sw=1.5, rx=4)
    s += text(cx, cy + 4, "зір", size=9, anchor="middle", weight="bold")
    chips = [("ОБЧИСЛЕННЯ", "оп/с", BLUE, 245, 118),
             ("ПАМ'ЯТЬ", "RAM", BLUE, 715, 118),
             ("ЖИВЛЕННЯ", "вати", AMBER, 168, 226),
             ("ВАГА", "грами", AMBER, 792, 226),
             ("ТЕПЛО · ГРОШІ", "°C, $", RED, 245, 334),
             ("ЗАТРИМКА", "кадр/с", GREEN, 715, 334)]
    for t, u, col, x, y in chips:
        s += line(x + (78 if x < cx else -78), y, cx + (-58 if x < cx else 58),
                  cy, stroke="#d4d4d8", w=1.1)
    for t, u, col, x, y in chips:
        s += rect(x - 80, y - 26, 160, 52, fill=PANEL, stroke=col, sw=1.7,
                  rx=10)
        s += text(x, y - 4, t, size=10, anchor="middle", weight="bold",
                  fill=col)
        s += text(x, y + 13, u, size=8.5, anchor="middle", fill=MUTE)
    s += rect(150, 392, 660, 32, fill="#fffbeb", stroke=AMBER, sw=1.4, rx=8)
    s += text(480, 412,
              "важчий і ненажерливіший «мозок» → коротший політ: зір завжди торгується з витривалістю",
              size=10, anchor="middle", weight="bold", fill="#92400e")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.9.2 — Драбина заліза
# ════════════════════════════════════════════════════════════════════════════
def fig_hardware_spectrum():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Драбина заліза: від мікроконтролера до бортового комп'ютера",
               "МК — кілобайти й мілівати (проста обробка); одноплатник (Pi) — гігабайти й вати; + прискорювач — нейромережі")
    panels = [
        ("МІКРОКОНТРОЛЕР (МК)", "STM32 / ESP32 · політний контролер",
         "КБ пам'яті · МГц · мілівати · без ОС",
         "✓ поріг, колірна пляма, лінія, малий Собель",
         "✗ нейромережі, Канні на HD, великі кадри", RED),
        ("ОДНОПЛАТНИК (Pi)", "Raspberry Pi · Linux",
         "ГБ пам'яті · ГГц, кілька ядер · вати",
         "✓ повні конвеєри: Канні, Хаф, контури, шаблон",
         "~ нейромережі — повільно без прискорювача", AMBER),
        ("SBC + ПРИСКОРЮВАЧ", "Jetson · Coral TPU · NPU",
         "GPU / NPU — згортки гуртом · десятки ват",
         "✓ нейромережі-детектори в реальному часі (49.7)",
         "− найважче, найгарячіше, найдорожче", GREEN)]
    y0, ph, gap = 106, 112, 9
    for i, (name, sub, specs, can, cant, col) in enumerate(panels):
        y = y0 + i * (ph + gap)
        s += rect(60, y, 840, ph, fill=PANEL, stroke=col, sw=1.8, rx=11)
        s += rect(60, y, 256, ph, fill=col, stroke="none", rx=11, opacity=0.13)
        s += text(188, y + 40, name, size=11.5, anchor="middle", weight="bold",
                  fill=col)
        s += text(188, y + 60, sub, size=8.6, anchor="middle", fill=MUTE)
        s += text(188, y + 86, specs, size=8.6, anchor="middle", fill=INK)
        s += text(338, y + 46, can, size=9.8, fill="#15803d", weight="bold")
        s += text(338, y + 76, cant, size=9.8, fill=RED)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.9.3 — Що скільки коштує
# ════════════════════════════════════════════════════════════════════════════
def fig_what_costs_what():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Що скільки коштує: задача → мінімальне залізо",
               "дешево (МК): поріг, пляма, лінія; середньо (Pi CPU): Канні, Хаф, контури, трекінг; важко (Pi+GPU): нейродетектор")
    tiers = [("ДЕШЕВО — тягне МК", GREEN, "для дронів — перший вибір",
              ["• поріг і морфологія (49.5)", "• колірна пляма в HSV (49.6)",
               "• стеження за лінією",
               "• малий Собель на дрібному кадрі (49.4)"]),
             ("СЕРЕДНЬО — одноплатник (CPU)", AMBER, "коли класики мало",
              ["• Канні: чисті контури (49.4)",
               "• перетворення Хафа: лінії, кола (49.6)",
               "• контури, форми, зіставлення з шаблоном",
               "• оптичний потік / трекінг (49.8)"]),
             ("ВАЖКО — одноплатник + GPU", RED, "лише з потужним чипом",
              ["• нейромережа-детектор, інференс (49.7)",
               "• сегментація, багато класів",
               "• усе, де треба «навчена» загальність"])]
    y0, bh, gap = 100, 108, 12
    for i, (t, col, note, items) in enumerate(tiers):
        y = y0 + i * (bh + gap)
        s += rect(60, y, 840, bh, fill=PANEL, stroke=col, sw=1.8, rx=11)
        s += rect(60, y, 300, bh, fill=col, stroke="none", rx=11, opacity=0.13)
        s += text(210, y + bh / 2 - 6, t, size=11, anchor="middle",
                  weight="bold", fill=col)
        s += text(210, y + bh / 2 + 14, note, size=8.6, anchor="middle",
                  fill=MUTE)
        s += lines(380, y + 26, items, size=9.4, lh=20)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 49.9.4 — Як улізти в бюджет; де що крутити
# ════════════════════════════════════════════════════════════════════════════
def fig_fitting_architecture():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Як улізти в бюджет — і де що крутити",
               "здешевлюй (менший кадр, сіре, ROI, пропуск кадрів + трекінг, квантування) і правильно розподіляй обчислення")
    s += rect(50, 104, 400, 300, fill="#fbfbfd", stroke=BLUE, sw=1.8, rx=12)
    s += text(250, 128, "ЯК ЗДЕШЕВИТИ ЗІР", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(72, 158,
               ["• менший кадр — менше пікселів рахувати",
                "• сіре: 1 канал замість 3 (49.1)",
                "• ROI: обробляй лише потрібну ділянку",
                "• пропускай кадри: детектор зрідка,",
                "  між ним — легкий трекер (49.8)",
                "• квантована / мала модель (49.7)",
                "• НАЙДЕШЕВШИЙ метод спершу: класика",
                "  (49.6) перед нейромережею (49.7)"], size=9.6, lh=28)
    s += rect(490, 104, 420, 300, fill="#fbfbfd", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 128, "ДЕ ЩО КРУТИТИ", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += rect(540, 150, 320, 52, fill=BOX3, stroke=AMBER, sw=1.5, rx=9)
    s += text(700, 170, "Політний контролер (МК)", size=10, anchor="middle",
              weight="bold")
    s += text(700, 188, "політ, стабілізація — НЕ зір", size=8.4,
              anchor="middle", fill=MUTE)
    s += rect(540, 232, 320, 52, fill=BOX1, stroke=BLUE, sw=1.5, rx=9)
    s += text(700, 252, "Бортовий комп'ютер (Pi / Jetson)", size=10,
              anchor="middle", weight="bold")
    s += text(700, 270, "зір: детектор, трекінг (49.1–49.8)", size=8.4,
              anchor="middle", fill=MUTE)
    s += rect(540, 314, 320, 52, fill=PANEL, stroke=MUTE, sw=1.5, rx=9)
    s += text(700, 334, "Земля / хмара", size=10, anchor="middle",
              weight="bold")
    s += text(700, 352, "найважче — та з лагом мережі (48.6)", size=8.4,
              anchor="middle", fill=MUTE)
    s += line(700, 232, 700, 204, stroke=INK, w=1.7, marker="arr")
    s += text(706, 220, "кут (MAVLink, 49.8)", size=7.6, anchor="start",
              fill=BLUE)
    s += line(700, 314, 700, 286, stroke=MUTE, w=1.3, marker="arr", dash="3,2")
    s += text(W / 2, H - 12,
              "Right-size: не став Jetson, де досить порога на МК — і не проси в "
              "МК нейромережі. Кожній задачі — своє залізо.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-49-0-1-summer-1966.svg": fig_summer_1966,
    "fig-49-0-2-semantic-gap.svg": fig_semantic_gap,
    "fig-49-0-3-project-goals.svg": fig_project_goals,
    "fig-49-0-4-roadmap.svg":   fig_roadmap,
    "fig-49-1-1-image-as-grid.svg": fig_image_as_grid,
    "fig-49-1-2-channels.svg":  fig_channels,
    "fig-49-1-3-color-spaces.svg": fig_color_spaces,
    "fig-49-1-4-hsv-for-vision.svg": fig_hsv_for_vision,
    "fig-49-2-1-histogram.svg": fig_histogram,
    "fig-49-2-2-brightness-contrast.svg": fig_brightness_contrast,
    "fig-49-2-3-stretch-equalize.svg": fig_stretch_equalize,
    "fig-49-2-4-clipping-vision.svg": fig_clipping_vision,
    "fig-49-3-1-convolution.svg": fig_convolution,
    "fig-49-3-2-blur.svg":      fig_blur,
    "fig-49-3-3-sharpen.svg":   fig_sharpen,
    "fig-49-3-4-kernels-cost.svg": fig_kernels_cost,
    "fig-49-4-1-edge-gradient.svg": fig_edge_gradient,
    "fig-49-4-2-sobel.svg":     fig_sobel,
    "fig-49-4-3-canny-pipeline.svg": fig_canny_pipeline,
    "fig-49-4-4-sobel-vs-canny.svg": fig_sobel_vs_canny,
    "fig-49-5-1-thresholding.svg": fig_thresholding,
    "fig-49-5-2-adaptive.svg":  fig_adaptive,
    "fig-49-5-3-erosion-dilation.svg": fig_erosion_dilation,
    "fig-49-5-4-opening-closing.svg": fig_opening_closing,
    "fig-49-6-1-color-blob.svg": fig_color_blob,
    "fig-49-6-2-shape-contour.svg": fig_shape_contour,
    "fig-49-6-3-hough.svg":     fig_hough,
    "fig-49-6-4-template-toolbox.svg": fig_template_toolbox,
    "fig-49-7-1-why-learn.svg": fig_why_learn,
    "fig-49-7-2-train-vs-infer.svg": fig_train_vs_infer,
    "fig-49-7-3-detector-io.svg": fig_detector_io,
    "fig-49-7-4-onboard-cost.svg": fig_onboard_cost,
    "fig-49-s7-1-timeline.svg": fig_nn_timeline,
    "fig-49-s7-2-perceptron-xor.svg": fig_perceptron_xor,
    "fig-49-s7-3-three-ingredients.svg": fig_three_ingredients,
    "fig-49-s7-4-alexnet-moment.svg": fig_alexnet_moment,
    "fig-49-8-1-detect-vs-track.svg": fig_detect_vs_track,
    "fig-49-8-2-pixel-to-angle.svg": fig_pixel_to_angle,
    "fig-49-8-3-visual-servo-loop.svg": fig_visual_servo_loop,
    "fig-49-8-4-apps-latency.svg": fig_apps_latency,
    "fig-49-9-1-budgets.svg":   fig_budgets,
    "fig-49-9-2-hardware-spectrum.svg": fig_hardware_spectrum,
    "fig-49-9-3-what-costs-what.svg": fig_what_costs_what,
    "fig-49-9-4-fitting-architecture.svg": fig_fitting_architecture,
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "img")
    os.makedirs(out, exist_ok=True)
    for name, fn in FIGS.items():
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", name)


if __name__ == "__main__":
    main()
