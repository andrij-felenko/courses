#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 45 (Модуль 7) — чистий Python, без залежностей.
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
# Рис. 45.0.1 — Чому саме літій: найлегший і найенергійніший
# ════════════════════════════════════════════════════════════════════════════
def fig_whylithium():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому весь портативний світ працює саме на літії",
               "найлегший метал і найохочіший віддати електрон → найбільше енергії на кілограм")

    # картка літію
    s += rect(60, 100, 200, 200, fill=BOX1, stroke=BLUE, sw=1.9, rx=14)
    s += text(160, 140, "3", size=14, anchor="middle", fill=MUTE)
    s += text(160, 200, "Li", size=58, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(160, 240, "літій", size=15, anchor="middle", weight="bold")
    s += text(160, 272, "найлегший метал", size=11, anchor="middle", fill=MUTE)
    s += lines(60, 330, ["• 3-й елемент таблиці — дуже легкий",
                         "• найсильніше «тисне» віддати електрон",
                         "  → найвища можлива напруга й енергія",
                         "• плата: дуже реактивний (горить, боїться води)"],
               size=11.5, lh=22)

    # стовпчики питомої енергії
    s += text(620, 120, "Питома енергія (Вт·год на кг)", size=12.5,
              weight="bold", anchor="middle")
    bars = [("Свинцево-кислотний", 35, MUTE),
            ("Нікель-метал-гідрид", 80, AMBER),
            ("Літій-іонний", 250, GREEN)]
    bx, by, bmax, bw = 470, 150, 250, 360
    for i, (nm, val, col) in enumerate(bars):
        y = by + i * 56
        s += text(470, y - 4, nm, size=11, fill=INK)
        s += rect(470, y, val / bmax * bw, 28, fill=col, stroke="none",
                  opacity=0.75, rx=5)
        s += rect(470, y, bw, 28, fill="none", stroke=MUTE, sw=1.0, rx=5)
        s += text(470 + val / bmax * bw + 8, y + 20, f"~{val}", size=12,
                  weight="bold", fill=col)
    s += text(470, by + 3 * 56 + 4,
              "(для масштабу: бензин ~12 000 — але то не електрика й не заряджається назад)",
              size=10, fill=MUTE)

    s += text(W / 2, H - 14,
              "Більше енергії на грам — це довший політ, менша вага й сама "
              "можливість портативної електроніки. Тому літій переміг.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.0.2 — Три цеглинки, три лауреати
# ════════════════════════════════════════════════════════════════════════════
def fig_threemen():
    W, H = 980, 490
    s = header(W, H)
    s += title(W, "Три внески, три лауреати: як збирали літій-іонний акумулятор",
               "кожен додав свою цеглинку — Нобелівська премія з хімії 2019 на трьох")

    cards = [
        (40, "Віттінгем", "Exxon, ~1976", BLUE,
         ["катод TiS₂ + анод", "із літій-металу;", "перший перезаряджуваний,",
          "але ~2 В і НЕБЕЗПЕЧНИЙ", "(літій-метал → пожежі)"]),
        (290, "Гуденаф", "Oxford, 1980", GREEN,
         ["катод LiCoO₂", "→ ПОДВОЇВ напругу", "до ~4 В:", "удвічі більше енергії"]),
        (540, "Йосіно", "1985", AMBER,
         ["анод із вуглецю (графіт)", "замість літій-металу", "→ БЕЗПЕЧНО;",
          "перший придатний Li-ion"]),
        (790, "Sony", "1991", RED,
         ["перший КОМЕРЦІЙНИЙ", "літій-іонний акумулятор", "→ бум телефонів,",
          "ноутбуків, дронів"]),
    ]
    for x, nm, when, col, body in cards:
        s += rect(x, 96, 200, 220, fill="white", stroke=col, sw=1.8, rx=12)
        s += text(x + 100, 124, nm, size=14, weight="bold", anchor="middle",
                  fill=col)
        s += text(x + 100, 144, when, size=10.5, anchor="middle", fill=MUTE)
        s += lines(x + 14, 172, body, size=10.5, lh=18)
    for x in (240, 490, 740):
        s += line(x, 206, x + 50, 206, stroke=INK, w=2.2, marker="arr")

    s += rect(120, 350, 740, 64, fill=BOX3, stroke=AMBER, sw=1.6, rx=12)
    s += lines(140, 376, [
        "Урок історії: великий винахід — це РЕЛЕ внесків, а не осяяння одинака.",
        "А Джон Гуденаф отримав Нобеля у 97 років — найстарший лауреат в історії.",
    ], size=12, lh=22, weight="bold")

    s += text(W / 2, H - 14,
              "Небезпечний літій-метал → потужний катод → безпечний вуглецевий анод "
              "→ товар. Без усіх трьох не було б ні телефона, ні дрона.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.0.3 — Як працює: «крісло-гойдалка» (інтеркаляція)
# ════════════════════════════════════════════════════════════════════════════
def fig_rockingchair():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Чому він ПЕРЕЗАРЯДЖУВАНИЙ: «крісло-гойдалка» іонів літію",
               "іони Li⁺ снують між електродами, ковзаючи в шари, не руйнуючи їх (інтеркаляція)")

    # катод (ліворуч) і анод (праворуч) — шаруваті
    def electrode(x, label, sub, col):
        o = rect(x, 130, 130, 230, fill="#f7f9ff", stroke=col, sw=1.8, rx=8)
        for k in range(6):
            o += line(x + 10, 150 + k * 36, x + 120, 150 + k * 36, stroke=col,
                      w=1.4, opacity=0.5)
        o += text(x + 65, 384, label, size=12.5, weight="bold", anchor="middle",
                  fill=col)
        o += text(x + 65, 402, sub, size=10, anchor="middle", fill=MUTE)
        return o

    s += electrode(120, "КАТОД", "LiCoO₂ (Гуденаф)", RED)
    s += electrode(710, "АНОД", "графіт (Йосіно)", BLUE)
    # електроліт
    s += rect(260, 130, 440, 230, fill="#eef6ff", stroke=MUTE, sw=1.2, rx=8,
              dash="5,4")
    s += text(480, 150, "електроліт (провідник для іонів Li⁺)", size=11,
              anchor="middle", fill=MUTE)
    # іони, що снують
    for k in range(5):
        s += circle(330 + k * 70, 250, 9, fill=GREEN, stroke=INK, sw=1.0)
        s += text(330 + k * 70, 254, "Li⁺", size=8, anchor="middle",
                  fill="white", weight="bold")
    # стрілки заряд/розряд
    s += line(360, 215, 600, 215, stroke=AMBER, w=2.4, marker="arr")
    s += text(480, 206, "ЗАРЯД: Li⁺ → до анода", size=11, anchor="middle",
              fill=AMBER, weight="bold")
    s += line(600, 290, 360, 290, stroke=GREEN, w=2.4, marker="arrG")
    s += text(480, 308, "РОЗРЯД: Li⁺ → до катода (живить апарат)", size=11,
              anchor="middle", fill=GREEN, weight="bold")
    # зовнішнє коло (електрони)
    s += line(185, 130, 185, 90, stroke=INK, w=1.6)
    s += line(185, 90, 775, 90, stroke=INK, w=1.6)
    s += line(775, 90, 775, 130, stroke=INK, w=1.6, marker="arr")
    s += text(480, 82, "електрони — зовнішнім колом (струм у навантаження)",
              size=10.5, anchor="middle", fill=INK)

    s += text(W / 2, H - 14,
              "Іони лиш «ковзають» у шари електрода й назад, не руйнуючи його, — "
              "тому цикл можна повторювати сотні разів. У цьому й уся хитрість.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.0.4 — Чому дрон — це здебільшого батарея
# ════════════════════════════════════════════════════════════════════════════
def fig_dronebattery():
    W, H = 940, 460
    s = header(W, H)
    s += title(W, "Чому дрон — це здебільшого батарея (і чому це його слабке місце)",
               "питома енергія літію зробила політ можливим — але батарея лишилась SPOF (44.7)")

    # стовпчик ваги дрона
    s += text(220, 110, "Вага типового дрона", size=12.5, weight="bold",
              anchor="middle")
    parts = [("Батарея", 42, GREEN), ("Рама й мотори", 30, BLUE),
             ("Гвинти, ESC", 16, AMBER), ("Електроніка, корисне", 12, MUTE)]
    y = 140
    for nm, pct, col in parts:
        h = pct * 4.2
        s += rect(120, y, 200, h, fill=col, stroke="white", sw=1.5,
                  opacity=0.78, rx=3)
        s += text(220, y + h / 2 + 4, f"{nm} — {pct}%", size=11,
                  anchor="middle", fill="white", weight="bold")
        y += h
    s += text(220, y + 22, "найбільший шматок — енергія", size=10.5,
              anchor="middle", fill=GREEN, italic=True)

    # трикутник компромісу
    s += text(680, 110, "Компроміс батареї", size=12.5, weight="bold",
              anchor="middle")
    s += poly([(680, 150), (560, 330), (800, 330)], fill="#fff7ef",
              stroke=AMBER, sw=1.7)
    s += text(680, 142, "енергія (політ)", size=11, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(545, 350, "потужність", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(560, 366, "(C-rate)", size=9.5, anchor="middle", fill=MUTE)
    s += text(815, 350, "безпека", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += text(815, 366, "(пожежа)", size=9.5, anchor="middle", fill=MUTE)
    s += text(680, 260, "не можна мати", size=10.5, anchor="middle", fill=INK)
    s += text(680, 276, "все одразу", size=10.5, anchor="middle", fill=INK)

    s += text(W / 2, H - 14,
              "Безколекторний мотор + ESC + літієва батарея — та трійця, на якій "
              "злетіла дронова епоха; і батарея в ній — водночас серце й найслабша ланка.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.1.1 — Одна батарея, багато напруг
# ════════════════════════════════════════════════════════════════════════════
def fig_rails():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Одна батарея — багато напруг: навіщо перетворювачі",
               "батарея дає одну напругу (та ще й плавну); апарату треба кілька стабільних")

    s += rect(50, 170, 180, 130, fill=BOX2, stroke=GREEN, sw=1.9, rx=12)
    s += text(140, 206, "Батарея 4S", size=14, weight="bold", anchor="middle",
              fill=GREEN)
    s += text(140, 230, "~14.8 В", size=13, anchor="middle")
    s += text(140, 252, "(12–16.8 В", size=10.5, anchor="middle", fill=MUTE)
    s += text(140, 268, "під час розряду)", size=10.5, anchor="middle",
              fill=MUTE)

    # пряме живлення моторів
    s += line(230, 200, 600, 130, stroke=RED, w=2.2, marker="arrR")
    s += rect(600, 108, 310, 48, fill="#fff0f0", stroke=RED, sw=1.5, rx=9)
    s += text(616, 130, "Мотори / ESC: сира батарея", size=12, weight="bold",
              fill=RED)
    s += text(616, 148, "(потужно, напруга може плавати)", size=9.5, fill=MUTE)

    # перетворювач
    s += rect(320, 200, 160, 120, fill=PANEL, stroke=INK, sw=1.8, rx=11)
    s += lines(400, 250, ["Перетворювачі", "напруги"], size=12.5,
               anchor="middle", lh=20, weight="bold")
    s += line(230, 250, 318, 250, stroke=INK, w=2.0, marker="arr")

    rails = [(190, "5 В", "логіка / контролер", BLUE),
             (250, "3.3 В", "давачі (чисто!)", GREEN),
             (310, "12 В", "камера / підвіс", AMBER)]
    for y, v, what, col in rails:
        s += line(480, 260, 600, y + 14, stroke=col, w=1.8, marker="arr")
        s += rect(600, y, 310, 40, fill="white", stroke=col, sw=1.5, rx=9)
        s += text(616, y + 26, v, size=13, weight="bold", fill=col)
        s += text(680, y + 26, "— " + what, size=11, fill=INK)

    s += text(W / 2, H - 16,
              "Кожна шина — окремий перетворювач. Питання лише ЯК перетворювати: "
              "спалюючи зайве в тепло чи переносячи енергію ощадно.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.1.2 — Лінійний стабілізатор: різницю — у тепло
# ════════════════════════════════════════════════════════════════════════════
def fig_linear():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Лінійний стабілізатор: простий і тихий, але спалює різницю в тепло",
               "прохідний транзистор гасить надлишок напруги — і та потужність стає теплом")

    s += text(110, 250, "Vвх", size=14, weight="bold", fill=RED)
    s += text(110, 270, "16 В", size=11, fill=INK)
    s += line(140, 255, 360, 255, stroke=INK, w=2.4)
    # прохідний транзистор
    s += rect(360, 215, 130, 80, fill=BOX1, stroke=BLUE, sw=1.8, rx=10)
    s += lines(425, 248, ["прохідний", "транзистор"], size=11, anchor="middle",
               lh=16, weight="bold")
    s += text(425, 286, "падає (Vвх−Vвих)", size=9.5, anchor="middle",
              fill=MUTE)
    # тепло вгору
    for k in range(3):
        x = 395 + k * 30
        s += f'<path d="M {x} 210 q 8 -14 0 -28 q -8 -14 0 -28" fill="none" stroke="{RED}" stroke-width="1.8"/>\n'
    s += text(425, 150, "(Vвх−Vвих)·I → ТЕПЛО", size=12.5, anchor="middle",
              weight="bold", fill=RED)
    # вихід
    s += line(490, 255, 720, 255, stroke=INK, w=2.4)
    s += text(740, 250, "Vвих", size=14, weight="bold", fill=GREEN)
    s += text(740, 270, "5 В", size=11, fill=INK)

    s += rect(120, 330, 360, 92, fill=PANEL, stroke=INK, sw=1.4, rx=11)
    s += text(140, 356, "ККД = Vвих / Vвх", size=14, weight="bold",
              family="Consolas, monospace")
    s += text(140, 384, "16 В → 5 В:  ККД ≈ 5/16 ≈ 31%", size=12,
              family="Consolas, monospace", fill=INK)
    s += text(140, 408, "решта 69% — у тепло", size=11.5, fill=RED)

    s += rect(520, 330, 340, 92, fill=BOX3, stroke=AMBER, sw=1.4, rx=11)
    s += text(540, 356, "Коли все ж лінійний?", size=12, weight="bold",
              fill=AMBER)
    s += lines(540, 378, ["• малий перепад, малий струм",
                          "• потрібна ТИША (давачі, аналог)"], size=11, lh=20)

    s += text(W / 2, H - 12,
              "Чим більший перепад напруги й струм, тим більше тепла лінійний "
              "просто марнує. Для батареї це розкіш.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.1.3 — Імпульсний перетворювач: енергію — пакетами
# ════════════════════════════════════════════════════════════════════════════
def fig_switching():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Імпульсний перетворювач: не палить різницю, а ПЕРЕНОСИТЬ енергію",
               "ключ ріже вхід, котушка й конденсатор запасають і згладжують — ККД 85–95%")

    s += text(70, 235, "Vвх", size=13, weight="bold", fill=RED)
    s += line(100, 240, 180, 240, stroke=INK, w=2.2)
    blocks = [(180, "КЛЮЧ", "MOSFET ріже", BLUE),
              (350, "КОТУШКА", "запасає енергію", AMBER),
              (520, "ДІОД", "замикає струм", GREEN),
              (660, "КОНД.", "згладжує", BLUE)]
    for x, nm, sub, col in blocks:
        s += rect(x, 205, 120, 70, fill="white", stroke=col, sw=1.7, rx=10)
        s += text(x + 60, 235, nm, size=12, weight="bold", anchor="middle",
                  fill=col)
        s += text(x + 60, 256, sub, size=9.5, anchor="middle", fill=MUTE)
        if x != 660:
            s += line(x + 120, 240, x + (170 if x != 520 else 140), 240,
                      stroke=INK, w=2.0, marker="arr")
    s += line(780, 240, 850, 240, stroke=INK, w=2.2, marker="arr")
    s += text(875, 235, "Vвих", size=13, weight="bold", fill=GREEN)

    s += rect(300, 310, 360, 56, fill=BOX2, stroke=GREEN, sw=1.7, rx=12)
    s += text(480, 344, "ККД ≈ 85–95%  (майже без тепла)", size=14,
              anchor="middle", weight="bold", fill=GREEN)

    s += text(W / 2, 400,
              "Уміє і знижувати (buck), і підвищувати (boost) напругу — на відміну "
              "від лінійного, що тільки знижує.",
              size=11.5, anchor="middle", fill=INK)
    s += text(W / 2, H - 14,
              "Як саме ці чотири деталі творять диво — розберемо в наступній "
              "темі (45.2). Тут головне: енергія не згоряє, а передається.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.1.4 — ККД і тепло: лінійний проти імпульсного
# ════════════════════════════════════════════════════════════════════════════
def fig_efficiency():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "ККД і тепло: чому для батареї беруть імпульсний",
               "лінійний втрачає тим більше, чим глибший перепад; імпульсний — майже стало")

    ox, oy = 90, 360
    s += line(ox, oy, ox + 360, oy, stroke=INK, w=1.4, marker="arr")
    s += line(ox, oy, ox, 110, stroke=INK, w=1.4, marker="arr")
    s += text(ox + 360, oy + 18, "Vвих / Vвх →", size=10.5, anchor="end")
    s += text(ox - 8, 116, "ККД", size=11, anchor="end", weight="bold")
    s += text(ox - 8, oy + 4, "0", size=9, anchor="end", fill=MUTE)
    s += text(ox - 8, 130, "100%", size=9, anchor="end", fill=MUTE)
    # імпульсний ~90% сталий
    s += line(ox, 150, ox + 340, 150, stroke=GREEN, w=2.6)
    s += text(ox + 180, 142, "імпульсний ~90%", size=11, fill=GREEN,
              weight="bold", anchor="middle")
    # лінійний: η = Vout/Vin (діагональ)
    s += line(ox, oy, ox + 340, 132, stroke=RED, w=2.6)
    s += text(ox + 250, 250, "лінійний = Vвих/Vвх", size=11, fill=RED,
              weight="bold")
    # точка прикладу 5/16
    px = ox + 0.31 * 340
    s += circle(px, oy - 0.31 * (oy - 132), 5, fill=RED, stroke=INK, sw=1.2)
    s += line(px, oy, px, oy + 6, stroke=MUTE, w=1.0)
    s += text(px, oy + 20, "16→5В", size=9, anchor="middle", fill=MUTE)

    # стовпчики втрат
    s += text(700, 130, "Приклад: 16 В → 5 В @ 1 А", size=12, weight="bold",
              anchor="middle")
    s += text(560, 168, "втрата в тепло:", size=11, fill=INK)
    s += rect(560, 180, 300, 40, fill="#fde2e2", stroke=RED, sw=1.4, rx=8)
    s += text(572, 205, "лінійний:  ~11 Вт", size=12.5, weight="bold", fill=RED,
              family="Consolas, monospace")
    s += rect(560, 232, 110, 40, fill="#d8f3e0", stroke=GREEN, sw=1.4, rx=8)
    s += text(572, 257, "імпульс.: ~1 Вт", size=12.5, weight="bold",
              fill=GREEN, family="Consolas, monospace")
    s += lines(560, 308, ["Висновок: для глибокого перепаду й помітного струму",
                          "— імпульсний; лінійний — для малих чистих шин."],
               size=11, lh=20, weight="bold")

    s += text(W / 2, H - 12,
              "Тепло — ворог (Розділу 3, 44): кожен змарнований ват треба ще й "
              "відвести, а на дроні зайвого тепла й ваги нема куди дівати.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.2.1 — Бак-перетворювач: дві фази
# ════════════════════════════════════════════════════════════════════════════
def fig_buckphases():
    W, H = 980, 470
    s = header(W, H)
    s += title(W, "Бак-перетворювач: дві фази качають енергію від входу до виходу",
               "ключ ВКЛ — котушка запасає енергію; ключ ВИКЛ — котушка віддає її через діод")

    def panel(ox, on, head):
        g, dim = GREEN, "#cdd0d5"
        ay, by = 168, 380
        xVin, xSw, xA, xB, lx = ox + 55, ox + 145, ox + 230, ox + 400, ox + 458
        o = text(ox + 240, 92, head, size=13, weight="bold", anchor="middle",
                 fill=(g if on else AMBER))
        o += rect(ox + 15, 105, 460, 320, fill="white", stroke=MUTE, sw=1.0,
                  rx=10)
        # Vin
        o += rect(ox + 35, 150, 40, 92, fill=BOX2, stroke=GREEN, sw=1.4, rx=6)
        o += text(xVin, 200, "Vвх", size=10.5, anchor="middle", weight="bold",
                  fill=GREEN)
        # Vin -> switch
        o += line(ox + 75, ay, xSw - 28, ay, stroke=(g if on else dim),
                  w=3 if on else 2)
        # switch
        o += rect(xSw - 28, ay - 18, 56, 36, fill=("#d8f3e0" if on else "white"),
                  stroke=(g if on else INK), sw=1.6, rx=7)
        o += text(xSw, ay + 5, "ВКЛ" if on else "ВИКЛ", size=10,
                  anchor="middle", weight="bold", fill=(g if on else AMBER))
        o += text(xSw, ay - 26, "ключ", size=9, anchor="middle", fill=MUTE)
        o += line(xSw + 28, ay, xA, ay, stroke=(g if on else dim),
                  w=3 if on else 2)
        o += circle(xA, ay, 3.5, fill=INK, stroke="none")
        o += text(xA, ay - 12, "A", size=10, anchor="middle", weight="bold")
        # inductor A->B
        o += coil(xA + 8, xA + 100, ay, 4, col=AMBER)
        o += text(xA + 54, ay - 16, "котушка L", size=9.5, anchor="middle",
                  fill=AMBER, weight="bold")
        o += line(xA + 100, ay, xB, ay, stroke=g, w=3)
        o += circle(xB, ay, 3.5, fill=INK, stroke="none")
        o += text(xB, ay - 12, "B", size=10, anchor="middle", weight="bold")
        o += line(xB, ay, lx, ay, stroke=g, w=3)
        o += text(lx + 4, ay - 8, "Vвих", size=10.5, weight="bold", fill=GREEN)
        # capacitor
        cx = xB + 25
        o += line(cx, ay, cx, 252, stroke=g, w=2)
        o += line(cx - 15, 254, cx + 15, 254, stroke=INK, w=3)
        o += line(cx - 15, 264, cx + 15, 264, stroke=INK, w=3)
        o += line(cx, 266, cx, by, stroke=g, w=2)
        o += text(cx + 20, 262, "C", size=10.5, weight="bold")
        # load
        o += rect(lx - 13, 250, 26, 60, fill="white", stroke=INK, sw=1.4, rx=4)
        o += text(lx, 285, "R", size=10.5, anchor="middle", weight="bold")
        o += line(lx, ay, lx, 250, stroke=g, w=2)
        o += line(lx, 310, lx, by, stroke=g, w=2)
        # bottom rail
        o += line(xVin, 242, xVin, by, stroke=g, w=2)
        o += line(xVin, by, lx, by, stroke=g, w=2)
        # diode at A (conducts in phase 2)
        dcol = dim if on else g
        o += line(xA, by, xA, 304, stroke=dcol, w=3 if not on else 2)
        o += poly([(xA - 8, 304), (xA + 8, 304), (xA, 290)], fill="white",
                  stroke=dcol, sw=1.5)
        o += line(xA - 10, 290, xA + 10, 290, stroke=dcol, w=2.4)
        o += line(xA, 290, xA, ay + 4, stroke=dcol, w=3 if not on else 2)
        o += text(xA - 13, 300, "діод", size=9, anchor="end", fill=dcol)
        o += text(xA + 13, 300, "пропускає" if not on else "закритий", size=8.5,
                  fill=(g if not on else MUTE))
        o += text(ox + 240, 410,
                  "струм у котушці ↑ росте" if on else "струм у котушці ↓ спадає",
                  size=10.5, anchor="middle", fill=AMBER, weight="bold")
        return o

    s += panel(0, True, "Фаза 1 — ключ ВКЛ")
    s += panel(490, False, "Фаза 2 — ключ ВИКЛ")
    s += text(W / 2, H - 12,
              "Конденсатор тримає Vвих рівним між фазами; так енергія йде пакетами "
              "входу → вихід, майже не гріючи компонентів.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.2.2 — Струм котушки: трикутна хвиля; Vвих = Vвх × D
# ════════════════════════════════════════════════════════════════════════════
def fig_inductorcurrent():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Струм котушки — трикутна хвиля; шпаруватість задає напругу",
               "росте, поки ключ ВКЛ; спадає, поки ВИКЛ; середнє = струм навантаження")
    ox, oy = 90, 340
    s += line(ox, oy, ox + 540, oy, stroke=INK, w=1.4, marker="arr")
    s += text(ox + 540, oy + 18, "час", size=10.5, anchor="end")
    s += line(ox, oy, ox, 110, stroke=INK, w=1.4, marker="arr")
    s += text(ox - 8, 116, "струм у котушці", size=10.5, anchor="end",
              weight="bold")

    T, ton = 160, 64
    lo, hi = oy - 50, oy - 150
    # фазне тло (перший період)
    s += rect(ox, 120, ton, oy - 120, fill=GREEN, opacity=0.08, stroke="none")
    s += text(ox + ton / 2, 136, "ВКЛ", size=9, anchor="middle", fill=GREEN,
              weight="bold")
    s += rect(ox + ton, 120, T - ton, oy - 120, fill=AMBER, opacity=0.10,
              stroke="none")
    s += text(ox + ton + (T - ton) / 2, 136, "ВИКЛ", size=9, anchor="middle",
              fill=AMBER, weight="bold")
    # трикутна хвиля
    pts = [(ox, lo)]
    x = ox
    for _ in range(3):
        pts.append((x + ton, hi))
        x += T
        pts.append((x, lo))
    s += poly(pts, fill="none", stroke=AMBER, sw=2.6, closed=False)
    # середнє
    avg = (lo + hi) / 2
    s += line(ox, avg, x, avg, stroke=GREEN, w=1.6, dash="6,4")
    s += text(ox + 8, avg - 6, "середнє = струм навантаження", size=10,
              fill=GREEN)
    # пульсація
    s += line(x + 16, lo, x + 16, hi, stroke=MUTE, w=1.0)
    s += text(x + 22, avg + 4, "пульсація", size=9, fill=MUTE)

    s += rect(640, 130, 280, 90, fill=PANEL, stroke=INK, sw=1.3, rx=11)
    s += text(780, 162, "Vвих = Vвх × D", size=16, anchor="middle",
              weight="bold", family="Consolas, monospace")
    s += text(780, 190, "D = частка часу «ВКЛ»", size=11.5, anchor="middle")
    s += text(780, 208, "(шпаруватість, Розділ 25)", size=10, anchor="middle",
              fill=MUTE)

    s += text(W / 2, H - 12,
              "Більша шпаруватість D (довше «ВКЛ») → вища Vвих. Саме нею керують "
              "вихідною напругою.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.2.3 — Шпаруватість задає напругу + зворотний зв'язок
# ════════════════════════════════════════════════════════════════════════════
def fig_duty():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Шпаруватість → напруга, а зворотний зв'язок тримає її сталою",
               "контролер міряє вихід і підкручує D — це той самий контур із Розділу 34")
    cases = [(0.31, "5 В", GREEN), (0.5, "8 В", AMBER), (0.75, "12 В", RED)]
    for i, (d, v, col) in enumerate(cases):
        y = 110 + i * 78
        s += text(70, y + 18, f"D = {d:g}", size=12, weight="bold",
                  family="Consolas, monospace")
        bx, bw = 180, 300
        s += line(bx, y + 40, bx + bw, y + 40, stroke=MUTE, w=1.0)
        # PWM меандр
        per = 60
        for k in range(int(bw / per)):
            x0 = bx + k * per
            w_on = per * d
            s += poly([(x0, y + 40), (x0, y + 8), (x0 + w_on, y + 8),
                       (x0 + w_on, y + 40), (x0 + per, y + 40)], fill="none",
                      stroke=col, sw=2.0, closed=False)
        s += line(bx + bw + 10, y + 24, bx + bw + 60, y + 24, stroke=INK,
                  w=2.0, marker="arr")
        s += rect(bx + bw + 64, y + 6, 90, 38, fill="white", stroke=col,
                  sw=1.6, rx=8)
        s += text(bx + bw + 109, y + 30, "Vвих " + v, size=12, anchor="middle",
                  weight="bold", fill=col)
    s += text(180, 100, "(при Vвх = 16 В)", size=10, fill=MUTE)

    # контур зворотного зв'язку
    s += rect(120, 360, 720, 76, fill=BOX1, stroke=BLUE, sw=1.6, rx=12)
    s += text(140, 386, "Зворотний зв'язок:", size=12, weight="bold",
              fill=BLUE)
    s += text(140, 410, "виміряти Vвих → порівняти з ціллю → підкрутити D → "
              "знову виміряти  (тримає вихід рівним, хоч би як стрибав вхід чи струм)",
              size=11, fill=INK)
    s += text(W / 2, H - 8,
              "Без зворотного зв'язку це був би просто «різак»; із ним — точний "
              "стабілізатор напруги.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.2.4 — Синхронний випрямляч і boost (підвищення)
# ════════════════════════════════════════════════════════════════════════════
def fig_syncboost():
    W, H = 980, 460
    s = header(W, H)
    s += title(W, "Дві важливі варіації: менше втрат і підвищення напруги",
               "діод → другий MOSFET (ефективніше); інша схема → boost (вища напруга)")

    s += rect(40, 90, 440, 320, fill="white", stroke=GREEN, sw=1.6, rx=12)
    s += text(260, 118, "Синхронний випрямляч", size=13, weight="bold",
              anchor="middle", fill=GREEN)
    s += lines(64, 152, [
        "Діод завжди має падіння ~0.5 В —", "а на великому струмі це втрати й тепло.",
        "", "Замінюємо діод другим MOSFET (низьким):",
        "у нього опір мілліоми → майже без втрат.", "",
        "Два ключі по черзі: верхній «качає»,",
        "нижній «замикає». ККД ще вищий.",
    ], size=11, lh=22)
    s += rect(64, 360, 392, 34, fill="#eafaef", stroke=GREEN, sw=1.2, rx=8)
    s += text(260, 382, "так зроблено майже всі сучасні перетворювачі дрона",
              size=10.5, anchor="middle", weight="bold", fill=GREEN)

    s += rect(500, 90, 440, 320, fill="white", stroke=AMBER, sw=1.6, rx=12)
    s += text(720, 118, "Boost — підвищення напруги", size=13, weight="bold",
              anchor="middle", fill=AMBER)
    s += lines(524, 152, [
        "Інша розкладка тих самих деталей.",
        "Ключ накачує котушку, а коли рветься —",
        "її «брикання» (викид напруги, Розділ 8.5)",
        "ДОДАЄТЬСЯ до входу.", "",
        "Тому boost робить Vвих ВИЩУ за Vвх —", "чого лінійний не вміє в принципі.",
    ], size=11, lh=22)
    s += rect(524, 360, 392, 34, fill="#fff5e6", stroke=AMBER, sw=1.2, rx=8)
    s += text(720, 382, "те саме «брикання» котушки, що псувало ключі, — тут на користь",
              size=10, anchor="middle", weight="bold", fill=AMBER)

    s += text(W / 2, H - 10,
              "Усе це — комбінації ключа, котушки, діода й конденсатора; міняється "
              "лише схема їхнього з'єднання.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.3.1 — Дерево живлення
# ════════════════════════════════════════════════════════════════════════════
def fig_powertree():
    W, H = 980, 500
    s = header(W, H)
    s += title(W, "Живлення апарата — це дерево шин від однієї батареї",
               "від кореня (батареї) гілки розходяться через перетворювачі до кожного навантаження")

    # батарея-корінь
    s += rect(40, 210, 130, 80, fill=BOX2, stroke=GREEN, sw=1.9, rx=11)
    s += text(105, 244, "Батарея", size=13, weight="bold", anchor="middle",
              fill=GREEN)
    s += text(105, 266, "4S ~14.8 В", size=11, anchor="middle")

    def node(x, y, w, h, lab, sub, col, fill="white"):
        o = rect(x, y - h / 2, w, h, fill=fill, stroke=col, sw=1.6, rx=9)
        o += text(x + w / 2, y - 2, lab, size=11.5, weight="bold",
                  anchor="middle", fill=col)
        if sub:
            o += text(x + w / 2, y + 16, sub, size=9.5, anchor="middle",
                      fill=MUTE)
        return o

    # гілка 1: мотори (сира батарея)
    s += line(170, 235, 300, 110, stroke=RED, w=2.6, marker="arrR")
    s += node(300, 110, 200, 56, "ESC ×4 → мотори", "сира батарея, великий струм",
              RED, "#fff0f0")

    # гілка 2: buck 5В
    s += line(170, 250, 300, 250, stroke=INK, w=2.2, marker="arr")
    s += node(300, 250, 130, 54, "Buck → 5 В", "головна шина", BLUE, BOX1)
    s += line(430, 235, 560, 200, stroke=INK, w=1.8, marker="arr")
    s += node(560, 200, 180, 48, "Контролер, приймач", "", INK)
    s += line(430, 262, 540, 300, stroke=INK, w=1.8, marker="arr")
    s += node(540, 300, 120, 48, "LDO → 3.3 В", "тихо", GREEN, BOX2)
    s += line(660, 300, 760, 300, stroke=INK, w=1.8, marker="arr")
    s += node(760, 300, 160, 48, "Давачі (чисто)", "", GREEN)

    # гілка 3: buck 12В
    s += line(170, 270, 300, 400, stroke=INK, w=2.2, marker="arr")
    s += node(300, 400, 130, 54, "Buck → 12 В", "", AMBER, BOX3)
    s += line(430, 400, 560, 400, stroke=INK, w=1.8, marker="arr")
    s += node(560, 400, 180, 48, "Камера / підвіс", "", AMBER)

    s += text(W / 2, H - 14,
              "Часто все це збирають на платі розподілу живлення (PDB). Кожна гілка "
              "має свій струмовий ліміт; відмова в корені валить усі гілки нижче (44.7).",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.3.2 — Кидок струму й анти-іскра
# ════════════════════════════════════════════════════════════════════════════
def fig_inrush():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Кидок струму при під'єднанні батареї — і чому з'являється іскра",
               "порожні конденсатори жадібно заряджаються миттєво → величезний пік струму")

    ox, oy = 90, 330
    s += line(ox, oy, ox + 460, oy, stroke=INK, w=1.4, marker="arr")
    s += text(ox + 460, oy + 18, "час", size=10.5, anchor="end")
    s += line(ox, oy, ox, 100, stroke=INK, w=1.4, marker="arr")
    s += text(ox - 8, 106, "струм входу", size=10.5, anchor="end",
              weight="bold")
    s += line(ox, oy, ox + 6, oy, stroke=INK, w=1.0)
    s += text(ox - 8, oy + 4, "0", size=9, anchor="end", fill=MUTE)
    # без захисту: гострий пік
    s += poly([(ox + 4, oy), (ox + 6, 120), (ox + 30, oy - 30),
               (ox + 80, oy - 8), (ox + 200, oy - 6)], fill="none", stroke=RED,
              sw=2.6, closed=False)
    s += text(ox + 30, 110, "без захисту: величезний пік → ІСКРА", size=10.5,
              fill=RED, weight="bold")
    # з анти-іскрою: пологий
    s += poly([(ox + 4, oy), (ox + 60, oy - 70), (ox + 160, oy - 30),
               (ox + 300, oy - 8), (ox + 430, oy - 6)], fill="none",
              stroke=GREEN, sw=2.6, closed=False)
    s += text(ox + 230, oy - 60, "з анти-іскрою: пологий заряд", size=10.5,
              fill=GREEN, weight="bold")

    s += rect(620, 120, 310, 230, fill=PANEL, stroke=INK, sw=1.4, rx=12)
    s += text(775, 148, "Чому й чим лікують", size=12.5, weight="bold",
              anchor="middle")
    s += lines(640, 176, [
        "Конденсатори на вході (45.2) при",
        "вмиканні порожні — і тягнуть струм,",
        "як коротке замикання, аж поки",
        "не зарядяться. Звідси спалах на",
        "контактах роз'єму.",
        "",
        "Лікують резистором передзаряду чи",
        "«анти-іскровим» роз'ємом, що пускає",
        "перші струми через опір.",
    ], size=10.5, lh=19)

    s += text(W / 2, H - 12,
              "Тому LiPo при під'єднанні часто «стріляє» іскрою — і тому серйозні "
              "збірки беруть анти-іскрові роз'єми чи м'який старт.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.3.3 — Послідовність увімкнення шин
# ════════════════════════════════════════════════════════════════════════════
def fig_sequencing():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Послідовність увімкнення: деяким чіпам шини треба в правильному порядку",
               "не всі рейки можна вмикати разом — інколи порядок критичний")
    ox = 130
    rails = [(150, "ядро 1.8 В", BLUE, 70),
             (250, "вв/в 3.3 В", GREEN, 150),
             (350, "периферія 5 В", AMBER, 230)]
    s += line(ox, 390, ox + 700, 390, stroke=INK, w=1.4, marker="arr")
    s += text(ox + 700, 408, "час", size=10.5, anchor="end")
    for y, nm, col, t0 in rails:
        s += text(ox - 10, y + 5, nm, size=11, anchor="end", weight="bold",
                  fill=col)
        # сходинка напруги, що піднімається в момент t0
        x0 = ox + t0
        s += poly([(ox, y + 30), (x0, y + 30), (x0 + 30, y - 12),
                   (ox + 690, y - 12)], fill="none", stroke=col, sw=2.4,
                  closed=False)
        s += line(x0 + 15, y + 34, x0 + 15, 390, stroke=col, w=1.0, dash="3,3",
                  opacity=0.5)
    s += text(ox + 70, 405, "1-ша", size=9, anchor="middle", fill=BLUE)
    s += text(ox + 150, 420, "2-га", size=9, anchor="middle", fill=GREEN)
    s += text(ox + 230, 405, "3-тя", size=9, anchor="middle", fill=AMBER)

    s += rect(ox + 470, 110, 300, 150, fill=BOX3, stroke=AMBER, sw=1.4, rx=11)
    s += text(ox + 620, 136, "Навіщо порядок", size=12, weight="bold",
              anchor="middle", fill=AMBER)
    s += lines(ox + 488, 162, [
        "Подаси не в тому порядку —", "і чіп може «защемити» (latch-up),",
        "перегрітись чи зависнути.", "",
        "Тому ставлять контролер", "послідовності, що вмикає рейки",
        "одна за одною, з паузами.",
    ], size=10.5, lh=18)

    s += text(W / 2, H - 14,
              "Те саме — і при вимкненні (часто у зворотному порядку). Для простих "
              "апаратів про це дбають готові мікросхеми живлення.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.3.4 — Заземлення: зіркова земля проти петлі
# ════════════════════════════════════════════════════════════════════════════
def fig_grounding():
    W, H = 980, 470
    s = header(W, H)
    s += title(W, "Заземлення: чому сильний струм мотора «шумить» у давачі",
               "спільна земля → струм мотора створює напругу, яку давач бачить як шум")

    # НЕПРАВИЛЬНО
    s += rect(40, 90, 440, 320, fill="#fff7f7", stroke=RED, sw=1.6, rx=12)
    s += text(260, 116, "НЕПРАВИЛЬНО: спільна земля", size=12.5, weight="bold",
              anchor="middle", fill=RED)
    s += text(90, 170, "− батареї", size=10, anchor="middle", fill=INK)
    s += circle(90, 185, 5, fill=INK, stroke="none")
    # спільний провід землі
    s += line(90, 185, 420, 185, stroke=INK, w=4)
    s += text(255, 175, "один спільний провід землі (має опір)", size=9.5,
              anchor="middle", fill=MUTE)
    # мотор — великий струм
    s += rect(180, 220, 90, 44, fill="#fde2e2", stroke=RED, sw=1.5, rx=7)
    s += text(225, 247, "мотор", size=10.5, anchor="middle", weight="bold")
    s += line(225, 220, 225, 185, stroke=RED, w=3, marker="arrR")
    s += text(258, 210, "великий струм", size=9, fill=RED)
    # давач — на тому ж проводі, далі
    s += rect(330, 220, 90, 44, fill="white", stroke=BLUE, sw=1.5, rx=7)
    s += text(375, 247, "давач", size=10.5, anchor="middle", weight="bold",
              fill=BLUE)
    s += line(375, 220, 375, 185, stroke=BLUE, w=1.6)
    s += text(255, 320, "струм мотора × опір проводу = напруга,", size=10.5,
              anchor="middle", fill=RED)
    s += text(255, 338, "яку давач «бачить» як шум (ground bounce)", size=10.5,
              anchor="middle", fill=RED, weight="bold")

    # ПРАВИЛЬНО
    s += rect(500, 90, 440, 320, fill="#f4fbf6", stroke=GREEN, sw=1.6, rx=12)
    s += text(720, 116, "ПРАВИЛЬНО: зіркова земля", size=12.5, weight="bold",
              anchor="middle", fill=GREEN)
    s += circle(720, 300, 6, fill=INK, stroke="none")
    s += text(720, 322, "одна спільна точка («зірка»)", size=9.5,
              anchor="middle", fill=MUTE)
    s += rect(560, 180, 90, 44, fill="#fde2e2", stroke=RED, sw=1.5, rx=7)
    s += text(605, 207, "мотор", size=10.5, anchor="middle", weight="bold")
    s += line(605, 224, 714, 298, stroke=RED, w=3)
    s += rect(790, 180, 90, 44, fill="white", stroke=BLUE, sw=1.5, rx=7)
    s += text(835, 207, "давач", size=10.5, anchor="middle", weight="bold",
              fill=BLUE)
    s += line(835, 224, 726, 298, stroke=BLUE, w=1.6)
    s += text(720, 356, "окремі шляхи сходяться в одній точці —", size=10.5,
              anchor="middle", fill=GREEN)
    s += text(720, 374, "струм мотора не тече через землю давача", size=10.5,
              anchor="middle", fill=GREEN, weight="bold")

    s += text(W / 2, H - 14,
              "Тому сильнострумову («брудну») землю моторів розводять окремо від "
              "тихої землі давачів, зводячи їх в одній точці біля батареї.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.4.1 — Напруга комірки й рахунок S
# ════════════════════════════════════════════════════════════════════════════
def fig_cells():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Напруга комірки й рахунок «S»: послідовно — більше вольтів",
               "одна комірка ~3.7 В (3.0 порожня … 4.2 повна); 4 послідовно (4S) → ~14.8 В")

    # шкала однієї комірки
    bx, btop, bbot = 130, 130, 380
    s += rect(bx - 28, btop, 56, bbot - btop, fill="#f3f7ff", stroke=BLUE,
              sw=1.6, rx=8)
    s += text(bx, btop - 12, "одна комірка", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    for v, y, lab, col in [(4.2, btop + 6, "4.2 В — повна", GREEN),
                           (3.7, (btop + bbot) / 2, "3.7 В — номінал", INK),
                           (3.0, bbot - 6, "3.0 В — порожня (нижче — шкода)", RED)]:
        s += line(bx - 28, y, bx + 28, y, stroke=col, w=1.6)
        s += text(bx + 36, y + 4, lab, size=10.5, fill=col, weight="bold")

    # 4S стек
    sx = 560
    s += text(sx, 116, "4 комірки послідовно (4S)", size=12, weight="bold",
              anchor="middle")
    for k in range(4):
        y = 140 + k * 52
        s += rect(sx - 70, y, 140, 44, fill="#eef2ff", stroke=BLUE, sw=1.4,
                  rx=7)
        s += text(sx, y + 28, "3.7 В", size=12, anchor="middle", weight="bold")
        if k < 3:
            s += line(sx, y + 44, sx, y + 52, stroke=INK, w=2)
    s += line(sx + 90, 140, sx + 90, 140 + 4 * 52 - 8, stroke=INK, w=1.4)
    s += text(sx + 150, 240, "= 14.8 В", size=16, weight="bold", fill=GREEN)
    s += text(sx + 150, 264, "(16.8 повна,", size=10.5, fill=MUTE)
    s += text(sx + 150, 280, "12 порожня)", size=10.5, fill=MUTE)

    s += rect(130, 410, 700, 0, fill="none", stroke="none")
    s += text(W / 2, H - 16,
              "Послідовно (S) додають напругу, паралельно (P) — ємність. «4S2P» = "
              "4 в ряд × 2 паралельно: і вольти, і запас.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.4.2 — Ємність (заряд) проти енергії
# ════════════════════════════════════════════════════════════════════════════
def fig_capacity_energy():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Ємність ≠ енергія: mAh — це заряд, Вт·год — це паливо",
               "час польоту визначає ЕНЕРГІЯ (Вт·год), а не самі лиш mAh")

    s += rect(50, 100, 400, 150, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(250, 128, "Ємність — це ЗАРЯД", size=13, weight="bold",
              anchor="middle", fill=BLUE)
    s += text(250, 158, "5000 mAh = 5 А·год", size=14, anchor="middle",
              family="Consolas, monospace")
    s += text(250, 184, "= 5 А впродовж 1 години", size=11.5, anchor="middle")
    s += text(250, 206, "(або 10 А за 30 хв тощо)", size=10.5, anchor="middle",
              fill=MUTE)
    s += text(250, 232, "— але НЕ каже, скільки енергії!", size=11, fill=RED,
              anchor="middle", weight="bold")

    s += rect(510, 100, 400, 150, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(710, 128, "Енергія — це ПАЛИВО", size=13, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(710, 158, "Вт·год = В × А·год", size=14, anchor="middle",
              family="Consolas, monospace")
    s += text(710, 184, "14.8 В × 5 А·год = 74 Вт·год", size=12.5,
              anchor="middle", family="Consolas, monospace", weight="bold")
    s += text(710, 212, "ОЦЕ й визначає час польоту", size=11.5,
              anchor="middle", fill=GREEN, weight="bold")

    s += rect(120, 290, 720, 96, fill="#fff5e6", stroke=AMBER, sw=1.5, rx=12)
    s += text(140, 316, "Чому це важливо:", size=12, weight="bold", fill=AMBER)
    s += lines(140, 340, [
        "Дві батареї по 5000 mAh, але одна 4S (74 Вт·год), друга 6S (111 Вт·год) —",
        "у другої в 1.5 раза більше енергії за тих самих «mAh». Порівнювати треба Вт·год, а не mAh.",
    ], size=11.5, lh=22)

    s += text(W / 2, H - 14,
              "Запам'ятай: mAh — половина правди; повну дає лише добуток на напругу.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.4.3 — Крива розряду
# ════════════════════════════════════════════════════════════════════════════
def fig_dischargecurve():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Крива розряду: напруга не лінійна — повна, плато, тоді обрив",
               "тому «вольти ≠ відсотки»; під навантаженням крива ще й просідає нижче")

    ox, oy = 110, 360
    pw, ph = 640, 250
    s += line(ox, oy, ox + pw + 10, oy, stroke=INK, w=1.4, marker="arr")
    s += text(ox + pw + 6, oy + 20, "розряджено →", size=10.5, anchor="end")
    s += line(ox, oy, ox, oy - ph - 10, stroke=INK, w=1.4, marker="arr")
    s += text(ox - 8, oy - ph - 4, "В / комірку", size=10.5, anchor="end",
              weight="bold")
    # рівні
    def vy(v):
        return oy - (v - 3.0) / (4.3 - 3.0) * ph
    for v, lab, col in [(4.2, "4.2 повна", GREEN), (3.7, "3.7 номінал", INK),
                        (3.5, "3.5 — сідай!", AMBER),
                        (3.0, "3.0 — далі шкода", RED)]:
        s += line(ox, vy(v), ox + pw, vy(v), stroke=col, w=1.0, dash="4,4",
                  opacity=0.5)
        s += text(ox + pw + 8, vy(v) + 4, lab, size=10, fill=col,
                  weight="bold")
    # крива без навантаження
    nl = [(0, 4.2), (8, 4.1), (25, 3.9), (55, 3.78), (78, 3.66), (90, 3.5),
          (98, 3.2), (100, 3.0)]
    pts = [(ox + p / 100 * pw, vy(v)) for p, v in nl]
    s += poly(pts, fill="none", stroke=BLUE, sw=2.8, closed=False)
    s += text(ox + 150, vy(4.05), "без навантаження", size=10.5, fill=BLUE,
              weight="bold")
    # під навантаженням (нижче через просадку)
    ld = [(0, 3.95), (8, 3.85), (25, 3.7), (55, 3.6), (78, 3.48), (90, 3.32),
          (98, 3.05), (100, 2.9)]
    pts2 = [(ox + p / 100 * pw, vy(v)) for p, v in ld]
    s += poly(pts2, fill="none", stroke=RED, sw=2.2, closed=False, opacity=0.8)
    s += text(ox + 360, vy(3.45), "під газом (просідає)", size=10.5, fill=RED,
              weight="bold")
    # «коліно»
    s += circle(ox + 0.9 * pw, vy(3.5), 5, fill=AMBER, stroke=INK, sw=1.2)
    s += text(ox + 0.9 * pw, vy(3.5) - 14, "коліно", size=9, anchor="middle",
              fill=AMBER)

    s += text(W / 2, H - 12,
              "Більшу частину розряду напруга майже стоїть (плато), а наприкінці "
              "різко падає — тому за вольтами важко вгадати точний залишок.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.4.4 — Заряд (SoC) і безпечне вікно
# ════════════════════════════════════════════════════════════════════════════
def fig_soc():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Скільки лишилось і де межа: безпечне вікно розряду",
               "не висаджуй нижче ~3.0 В/комірку — це шкодить «полицям» (з історії розділу)")

    # вертикальна шкала-вікно
    gx, gtop, gbot = 130, 100, 380
    zones = [(4.2, 3.7, "#d8f3e0", GREEN, "робоча зона (повна → номінал)"),
             (3.7, 3.5, "#fff0d8", AMBER, "час сідати"),
             (3.5, 3.0, "#fde2e2", RED, "сідай НЕГАЙНО"),
             (3.0, 2.8, "#e9c9c9", "#7a1f1f", "нижче — незворотна шкода")]

    def gy(v):
        return gbot - (v - 2.8) / (4.2 - 2.8) * (gbot - gtop)
    s += rect(gx - 40, gtop, 80, gbot - gtop, fill="white", stroke=INK, sw=1.6,
              rx=8)
    for vhi, vlo, fill, col, lab in zones:
        s += rect(gx - 38, gy(vhi), 76, gy(vlo) - gy(vhi), fill=fill,
                  stroke="none")
        s += text(gx + 52, (gy(vhi) + gy(vlo)) / 2 + 4, lab, size=10.5,
                  fill=col, weight="bold")
        s += text(gx, gy(vhi) + 14, f"{vhi:g} В", size=9, anchor="middle",
                  fill=MUTE)

    # методи оцінки
    s += rect(540, 110, 380, 110, fill=BOX1, stroke=BLUE, sw=1.5, rx=11)
    s += text(730, 136, "За напругою (грубо)", size=12, weight="bold",
              anchor="middle", fill=BLUE)
    s += lines(560, 160, ["просто, але плато й просадка під газом",
                          "роблять оцінку приблизною;",
                          "у повітрі під навантаженням «бреше» вниз"],
               size=10.5, lh=18)
    s += rect(540, 240, 380, 110, fill=BOX2, stroke=GREEN, sw=1.5, rx=11)
    s += text(730, 266, "Лічба кулонів (точніше)", size=12, weight="bold",
              anchor="middle", fill=GREEN)
    s += lines(560, 290, ["інтегруємо спожитий струм (давач із 44.1)",
                          "→ скільки А·год пішло;",
                          "точніше, але треба знати початковий заряд"],
               size=10.5, lh=18)

    s += text(W / 2, H - 14,
              "На практиці апарат садять на ~3.5 В/комірку із запасом — щоб і не "
              "зіпсувати акумулятор, і мати дрібку на маневр перед посадкою.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.5.1 — C-rate: нормована мова струму
# ════════════════════════════════════════════════════════════════════════════
def fig_crate():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "C-rate: нормована мова струму",
               "1C — струм, що спорожнить пакет за 1 годину;  I = C-rate × ємність")
    # --- battery + formula (left) ---
    bx = 60
    s += rect(bx, 120, 175, 96, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += rect(bx + 175, 150, 10, 36, fill=GREEN, stroke=GREEN, sw=1, rx=2)
    s += text(bx + 87, 152, "4S LiPo", size=13, anchor="middle", weight="bold")
    s += text(bx + 87, 178, "5000 mAh", size=17, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(bx + 87, 200, "= 5 А·год (Q)", size=12, anchor="middle", fill=MUTE)
    s += rect(bx, 250, 200, 70, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(bx + 100, 280, "I = C-rate × Q", size=16, anchor="middle",
              weight="bold")
    s += text(bx + 100, 303, "Q = 5 А·год", size=12, anchor="middle", fill=MUTE)
    # --- ladder C -> A (middle) ---
    lx = 320
    s += text(lx, 104, "C-rate", size=12, weight="bold", fill=MUTE)
    s += text(lx + 205, 104, "= струм", size=12, weight="bold", fill=MUTE)
    rows = [("0.5C", "2.5 А", "за 2 год — м'яко", GREEN),
            ("1C", "5 А", "за 1 годину", GREEN),
            ("10C", "50 А", "звичайний політ", AMBER),
            ("50C", "250 А", "стеля за наклейкою", RED)]
    yy = 120
    for c, a, note, col in rows:
        s += rect(lx, yy, 96, 44, fill="white", stroke=col, sw=1.8, rx=9)
        s += text(lx + 48, yy + 29, c, size=16, anchor="middle", weight="bold",
                  fill=col)
        s += line(lx + 100, yy + 22, lx + 150, yy + 22, stroke=INK, w=1.6,
                  marker="arr")
        s += text(lx + 158, yy + 29, a, size=16, weight="bold")
        s += text(lx + 240, yy + 28, note, size=10.5, fill=MUTE)
        yy += 58
    # --- insight (right) ---
    ix = 648
    s += rect(ix, 120, 252, 232, fill=BOX1, stroke=BLUE, sw=1.6, rx=12)
    s += text(ix + 126, 146, "Навіщо нормувати?", size=13, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(ix + 126, 172, "Ті самі 10 А — це:", size=11.5, anchor="middle")
    s += rect(ix + 18, 188, 216, 52, fill="white", stroke=GREEN, sw=1.4, rx=8)
    s += text(ix + 126, 210, "5000 mAh → 2C", size=13, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(ix + 126, 230, "(прогулянка)", size=10.5, anchor="middle",
              fill=MUTE)
    s += rect(ix + 18, 252, 216, 52, fill="white", stroke=RED, sw=1.4, rx=8)
    s += text(ix + 126, 274, "1300 mAh → ~7.7C", size=13, anchor="middle",
              weight="bold", fill=RED)
    s += text(ix + 126, 294, "(на межі)", size=10.5, anchor="middle", fill=MUTE)
    s += text(ix + 126, 330, "C-rate каже навантаженість", size=10.5,
              anchor="middle", fill=BLUE)
    s += text(ix + 126, 345, "незалежно від розміру", size=10.5, anchor="middle",
              fill=BLUE)
    s += text(W / 2, H - 14,
              "«50C» на наклейці = 50 × ємність = заявлена виробником стеля струму "
              "(тут 250 А; реальна межа часто нижча).", size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.5.2 — Внутрішній опір і просадка
# ════════════════════════════════════════════════════════════════════════════
def fig_internalresistance():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Внутрішній опір: чому напруга провалюється під струмом",
               "реальна батарея = ідеальне джерело EMF + малий послідовний опір Rвн")
    L, Rr, T, Bm = 120, 430, 150, 280
    my = (T + Bm) / 2
    s += rect(70, 120, 360, 195, fill=BOX2, stroke=GREEN, sw=1.4, rx=12,
              dash="6,5")
    s += text(86, 140, "БАТАРЕЯ (модель)", size=10.5, fill=GREEN, weight="bold")
    # source
    s += circle(L, my, 28, fill="white", stroke=GREEN, sw=2.0)
    s += text(L, my - 3, "EMF", size=11, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(L, my + 13, "16.0 В", size=10, anchor="middle", fill=GREEN)
    # top wire + resistor zigzag
    s += line(L, my - 28, L, T, stroke=INK, w=1.8)
    s += line(L, T, 220, T, stroke=INK, w=1.8)
    zig = [(220, T)]
    xx = 220
    for i in range(6):
        xx += 14
        zig.append((xx, T - 11 if i % 2 == 0 else T + 11))
    zig.append((304, T))
    s += poly(zig, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(262, T - 22, "Rвн", size=12, anchor="middle", weight="bold",
              fill=RED)
    s += line(304, T, Rr, T, stroke=INK, w=1.8)
    s += circle(Rr, T, 4.5, fill=RED, stroke=RED)
    s += text(Rr + 12, T - 6, "+", size=16, weight="bold", fill=RED)
    # current arrow
    s += line(150, T, 200, T, stroke=RED, w=2.0, marker="arrR")
    s += text(176, T - 10, "I", size=12, anchor="middle", weight="bold", fill=RED)
    # load box
    s += rect(Rr - 35, T + 22, 70, 70, fill=BOX1, stroke=BLUE, sw=1.6, rx=9)
    s += text(Rr, T + 52, "мотори", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(Rr, T + 70, "100 А", size=12, anchor="middle", weight="bold",
              fill=BLUE)
    s += line(Rr, T, Rr, T + 22, stroke=INK, w=1.8)
    s += line(Rr, T + 92, Rr, Bm, stroke=INK, w=1.8)
    s += circle(Rr, Bm, 4.5, fill=BLUE, stroke=BLUE)
    s += text(Rr + 12, Bm + 8, "−", size=16, weight="bold", fill=BLUE)
    s += line(Rr, Bm, L, Bm, stroke=INK, w=1.8)
    s += line(L, Bm, L, my + 28, stroke=INK, w=1.8)
    # --- math (right) ---
    mx = 500
    s += rect(mx, 110, 410, 68, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(mx + 205, 140, "Vклем = EMF − I × Rвн", size=17,
              anchor="middle", weight="bold")
    s += text(mx + 205, 162, "напруга на клемах = рушій − провал на опорі",
              size=10.5, anchor="middle", fill=MUTE)
    s += rect(mx, 194, 198, 96, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(mx + 99, 218, "у спокої  I≈0", size=12, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(mx + 99, 248, "Vклем = 16.0 В", size=15, anchor="middle",
              weight="bold")
    s += text(mx + 99, 272, "повна напруга", size=10, anchor="middle", fill=MUTE)
    s += rect(mx + 212, 194, 198, 96, fill=BOX3, stroke=AMBER, sw=1.5, rx=10)
    s += text(mx + 311, 218, "під газом  I=100 А", size=12, anchor="middle",
              weight="bold", fill=AMBER)
    s += text(mx + 311, 244, "Vпр=100×0.012=1.2 В", size=11.5, anchor="middle")
    s += text(mx + 311, 272, "Vклем = 14.8 В", size=15, anchor="middle",
              weight="bold", fill=RED)
    s += rect(mx, 302, 410, 56, fill="#fde2e2", stroke=RED, sw=1.5, rx=10)
    s += text(mx + 205, 326, "P = I²·Rвн = 100²×0.012 = 120 Вт", size=14,
              anchor="middle", weight="bold", fill=RED)
    s += text(mx + 205, 346,
              "ця потужність гріє пакет ЗСЕРЕДИНИ (тому батарея тепла)",
              size=10.5, anchor="middle", fill="#7a1f1f")
    s += text(W / 2, H - 12,
              "Малий Rвн (свіжий, теплий) — мала просадка й мало тепла; великий "
              "Rвн (старий, холодний) — навпаки.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.5.3 — Просадка під газом (часова діаграма)
# ════════════════════════════════════════════════════════════════════════════
def fig_sag():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Просадка під газом: ривок струму — провал напруги",
               "напруга падає на I·Rвн і вертається; втомлена/холодна провалюється глибше")
    ox, ow = 90, 770
    # top: throttle / current
    t1, t1h = 78, 88
    s += text(ox - 10, t1 - 8, "газ / струм", size=11.5, fill=MUTE,
              weight="bold")
    s += rect(ox, t1, ow, t1h, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)
    base, pk = t1 + t1h - 20, t1 + 16
    thr = [(ox, base), (ox + 150, base), (ox + 150, pk), (ox + 320, pk),
           (ox + 320, base), (ox + 470, base), (ox + 470, pk), (ox + 560, pk),
           (ox + 560, base), (ox + ow, base)]
    s += poly(thr, fill="none", stroke=INK, sw=2.2, closed=False)
    s += text(ox + 235, pk - 4, "ривок газу", size=10.5, anchor="middle")
    s += text(ox + 515, pk - 4, "ривок", size=10.5, anchor="middle")
    # bottom: terminal voltage
    v0, vh = 222, 188
    s += text(ox - 10, v0 - 8, "напруга на клемах", size=11.5, fill=MUTE,
              weight="bold")
    s += rect(ox, v0, ow, vh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)

    def vy(v):
        return v0 + (16.8 - v) / (16.8 - 12.0) * vh
    for vv in [16.8, 15.6, 14.4, 13.2, 12.0]:
        s += line(ox, vy(vv), ox + ow, vy(vv), stroke="#eef0f2", w=1)
        s += text(ox - 12, vy(vv) + 4, f"{vv:g}", size=9, anchor="end",
                  fill=MUTE)
    s += line(ox, vy(13.2), ox + ow, vy(13.2), stroke=RED, w=1.6, dash="7,5")
    s += text(ox + ow - 4, vy(13.2) - 6, "поріг failsafe (3.3 В/комірку)",
              size=10, anchor="end", fill=RED, weight="bold")
    rest = 16.0
    hp = [(ox, vy(rest)), (ox + 150, vy(rest)), (ox + 150, vy(rest - 1.2)),
          (ox + 320, vy(rest - 1.2)), (ox + 320, vy(rest)), (ox + 470, vy(rest)),
          (ox + 470, vy(rest - 1.2)), (ox + 560, vy(rest - 1.2)),
          (ox + 560, vy(rest)), (ox + ow, vy(rest))]
    s += poly(hp, fill="none", stroke=GREEN, sw=2.4, closed=False)
    s += text(ox + 332, vy(rest - 1.2) + 16, "здорова: малий провал", size=10.5,
              fill=GREEN, weight="bold")
    rest2 = 15.4
    tp = [(ox, vy(rest2)), (ox + 150, vy(rest2)), (ox + 150, vy(rest2 - 3.0)),
          (ox + 320, vy(rest2 - 3.0)), (ox + 320, vy(rest2)),
          (ox + 470, vy(rest2)), (ox + 470, vy(rest2 - 3.0)),
          (ox + 560, vy(rest2 - 3.0)), (ox + 560, vy(rest2)), (ox + ow, vy(rest2))]
    s += poly(tp, fill="none", stroke=RED, sw=2.4, closed=False, opacity=0.85)
    s += text(ox + 175, vy(rest2 - 3.0) - 8,
              "втомлена/холодна: дно нижче порога → brownout/failsafe",
              size=10.5, fill=RED, weight="bold")
    s += text(W / 2, H - 12,
              "Дно ривка = Vспокою − I·Rвн. Що більший Rвн (старість, "
              "холод), то глибше дно — і легше проскочити поріг.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.5.4 — Скільки «C» треба: вибір під пік струму
# ════════════════════════════════════════════════════════════════════════════
def fig_chooseC():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Скільки «C» треба: під пік струму, із запасом",
               "Cмін = пік струму ÷ ємність; бери з запасом на просадку, тепло й старіння")
    mx = 70
    s += text(mx + 70, 100, "пік струму моторів", size=11.5, fill=MUTE,
              weight="bold", anchor="middle")
    for i in range(4):
        yy = 120 + i * 42
        s += circle(mx + 18, yy + 14, 13, fill=BOX1, stroke=BLUE, sw=1.6)
        s += text(mx + 18, yy + 19, "M", size=11, anchor="middle", weight="bold",
                  fill=BLUE)
        s += text(mx + 42, yy + 19, "~25 А", size=12, weight="bold")
    s += line(200, 130, 200, 262, stroke=MUTE, w=1.6)
    s += line(200, 196, 248, 196, stroke=MUTE, w=1.6, marker="arr")
    s += text(300, 190, "Σ ≈ 100 А", size=16, anchor="middle", weight="bold",
              fill=RED)
    s += text(300, 211, "піковий струм", size=10.5, anchor="middle", fill=MUTE)
    # formula
    s += rect(360, 150, 300, 84, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(510, 180, "Cмін = пік ÷ ємність", size=15, anchor="middle",
              weight="bold")
    s += text(510, 208, "= 100 А ÷ 5 А·год = 20C", size=14, anchor="middle",
              weight="bold", fill=RED)
    s += text(510, 258, "…але «впритул» не беруть →", size=11.5,
              anchor="middle", fill=MUTE)
    # zones
    zx, zw = 700, 228
    zones = [("< 20C  замало", "#fde2e2", RED,
              ["просадка, перегрів,", "здуття, коротке життя"]),
             ("≈ 50C  саме те", "#d8f3e0", GREEN,
              ["запас на просадку,", "тепло, ресурс"]),
             ("≫ 50C  забагато", PANEL, MUTE,
              ["зайва вага й ціна —", "без користі"])]
    yy = 108
    for lab, fill, col, note in zones:
        s += rect(zx, yy, zw, 86, fill=fill, stroke=col, sw=1.7, rx=10)
        s += text(zx + zw / 2, yy + 26, lab, size=13, anchor="middle",
                  weight="bold", fill=col)
        s += lines(zx + 16, yy + 48, note, size=10.5, lh=16, fill=INK)
        yy += 100
    s += text(W / 2, H - 12,
              "Бери C удвічі-втричі понад мінімум: апарат падає від провалів на "
              "піках, а не від середнього струму.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.6.1 — Заряд CC/CV: дві фази
# ════════════════════════════════════════════════════════════════════════════
def fig_cccv():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Заряд CC/CV: спершу струмом, тоді напругою",
               "CC — сталий струм до 4.2 В/комірку; CV — стала напруга, струм спадає до ~C/10")
    ox, ow = 95, 690
    xd = ox + 290
    # voltage band
    vy0, vh = 88, 120
    s += rect(ox, vy0, ow, vh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)
    s += text(ox - 12, vy0 + 14, "В", size=11, anchor="end", fill=MUTE,
              weight="bold")

    def vY(v):
        return vy0 + vh - (v - 3.5) / (4.35 - 3.5) * (vh - 24)
    for vv in [3.7, 4.0, 4.2]:
        s += line(ox, vY(vv), ox + ow, vY(vv), stroke="#eef0f2", w=1)
        s += text(ox - 4, vY(vv) + 4, f"{vv}", size=8.5, anchor="end", fill=MUTE)
    s += line(ox, vY(4.2), ox + ow, vY(4.2), stroke=RED, w=1.3, dash="6,4")
    s += poly([(ox, vY(3.7)), (xd, vY(4.2)), (ox + ow, vY(4.2))], fill="none",
              stroke=GREEN, sw=2.6, closed=False)
    s += text(ox + 130, vY(3.78), "напруга росте", size=10.5, fill=GREEN,
              weight="bold")
    s += text(xd + 120, vY(4.2) - 8, "тримається 4.2 В", size=10.5, fill=GREEN,
              weight="bold")
    # current band
    iy0, ih = 232, 120
    s += rect(ox, iy0, ow, ih, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)
    s += text(ox - 12, iy0 + 14, "I", size=11, anchor="end", fill=MUTE,
              weight="bold")

    def iY(fr):
        return iy0 + ih - fr * (ih - 24)
    ipts = [(ox, iY(1.0)), (xd, iY(1.0))]
    for k in range(25):
        x = xd + (ox + ow - xd) * k / 24
        ipts.append((x, iY(0.1 + 0.9 * math.exp(-3.0 * k / 24))))
    s += poly(ipts, fill="none", stroke=RED, sw=2.6, closed=False)
    s += line(ox, iY(0.1), ox + ow, iY(0.1), stroke=MUTE, w=1.1, dash="4,4")
    s += text(ox + 8, iY(0.1) - 6, "C/10 — поріг кінця", size=9.5, fill=MUTE)
    s += text(ox + 120, iY(1.0) + 16, "струм сталий (1C)", size=10.5, fill=RED,
              weight="bold")
    s += text(xd + 110, iY(0.5), "струм спадає", size=10.5, fill=RED,
              weight="bold")
    # divider + phase labels
    s += line(xd, vy0, xd, iy0 + ih, stroke=MUTE, w=1.4, dash="6,5")
    s += text((ox + xd) / 2, 76, "ФАЗА CC (сталий струм)", size=12,
              anchor="middle", weight="bold", fill=BLUE)
    s += text((xd + ox + ow) / 2, 76, "ФАЗА CV (стала напруга)", size=12,
              anchor="middle", weight="bold", fill=RED)
    s += text(ox + ow / 2, iy0 + ih + 22, "час →", size=11, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 12,
              "CC швидко наповнює до межі 4.2 В; CV безпечно «дотискає», поки "
              "струм не впаде до ~C/10.", size=11.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.6.2 — Баланс банок
# ════════════════════════════════════════════════════════════════════════════
def fig_balance():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Баланс: пакет міцний, як найслабша банка",
               "послідовні комірки дрейфують; балансир вирівнює їх через окремий роз'єм")
    cw, ch, gap = 40, 120, 8
    span = 4 * cw + 3 * gap

    def pack(x0, vals, head, headcol):
        out = text(x0 + span / 2, 84, head, size=13, anchor="middle",
                   weight="bold", fill=headcol)
        for i, v in enumerate(vals):
            cx = x0 + i * (cw + gap)
            out += rect(cx, 104, cw, ch, fill="white", stroke=INK, sw=1.5, rx=5)
            fr = max(0.0, min(1.0, (v - 3.0) / (4.2 - 3.0)))
            fh = (ch - 6) * fr
            lag = (v == min(vals) and min(vals) < max(vals) - 0.01)
            out += rect(cx + 3, 104 + ch - 3 - fh, cw - 6, fh,
                        fill=("#fad4d4" if lag else "#cdeed8"), stroke="none",
                        rx=3)
            out += text(cx + cw / 2, 104 + ch + 18, f"{v:.2f}", size=10.5,
                        anchor="middle", weight="bold",
                        fill=(RED if lag else INK))
            out += line(cx + cw / 2, 104, cx + cw / 2, 92, stroke=MUTE, w=1.1)
        out += line(x0 + cw / 2, 92, x0 + 3 * (cw + gap) + cw / 2, 92,
                    stroke=MUTE, w=1.4)
        out += text(x0 + span / 2, 250, "4 банки послідовно (4S)", size=10,
                    anchor="middle", fill=MUTE)
        return out
    s += pack(70, [4.20, 4.20, 4.05, 4.20], "ДО балансу", RED)
    s += text(70 + span / 2, 268, "найслабша (4.05) впреться в межу першою",
              size=10, anchor="middle", fill=RED)
    s += pack(560, [4.20, 4.20, 4.20, 4.20], "ПІСЛЯ балансу", GREEN)
    s += text(560 + span / 2, 268, "усі рівні — пакет віддає все", size=10,
              anchor="middle", fill=GREEN)
    s += line(330, 164, 540, 164, stroke=INK, w=2.0, marker="arr")
    s += text(435, 152, "балансир вирівнює", size=11, anchor="middle",
              weight="bold")
    s += text(435, 184, "(зціджує надлишок", size=10, anchor="middle", fill=MUTE)
    s += text(435, 200, "із повніших банок)", size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 30,
              "Заряд тече крізь усі комірки по черзі: коли найслабша дійшла "
              "4.2 В, заряд треба спинити —", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "інакше вона перезарядиться. Балансир зціджує надлишок із "
              "повніших, доки відсталі не наздоженуть.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.6.3 — BMS: вартовий батареї
# ════════════════════════════════════════════════════════════════════════════
def fig_bms():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "BMS: вартовий, що стереже кожну межу",
               "вийшов за поріг — BMS вимикає: понапруга, недонапруга, надструм, перегрів")
    s += rect(380, 150, 200, 150, fill=BOX1, stroke=BLUE, sw=2.0, rx=14)
    s += text(480, 198, "BMS", size=22, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(480, 224, "захист + баланс", size=11.5, anchor="middle", fill=BLUE)
    s += text(480, 256, "стежить за кожною", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(480, 270, "коміркою, струмом, t°", size=9.5, anchor="middle",
              fill=MUTE)
    guards = [
        (150, 116, "ПОНАПРУГА", "банка > 4.25 В", "→ обрізає заряд", RED),
        (150, 246, "НЕДОНАПРУГА", "банка < 3.0 В", "→ обрізає розряд", AMBER),
        (660, 116, "НАДСТРУМ", "I > межі / коротке", "→ вимикає миттєво", RED),
        (660, 246, "ПЕРЕГРІВ", "t° > ~60 °C", "→ вимикає", AMBER)]
    for gx, gy, h, c1, c2, col in guards:
        s += rect(gx, gy, 150, 90, fill="white", stroke=col, sw=1.7, rx=10)
        s += text(gx + 75, gy + 24, h, size=12, anchor="middle", weight="bold",
                  fill=col)
        s += text(gx + 75, gy + 46, c1, size=10, anchor="middle")
        s += text(gx + 75, gy + 66, c2, size=10, anchor="middle", fill=MUTE)
        if gx < 480:
            s += line(300, gy + 45, 380, gy + 45, stroke=col, w=1.4, dash="4,3")
        else:
            s += line(660, gy + 45, 580, gy + 45, stroke=col, w=1.4, dash="4,3")
    s += text(W / 2, H - 30,
              "На дроні «голий» LiPo часто покладається на failsafe польотного "
              "контролера (низька напруга),", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "а в серйозних Li-ion пакетах стоїть справжній BMS, що сам обриває "
              "коло на будь-якому порушенні.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.6.4 — Як заряджати на практиці
# ════════════════════════════════════════════════════════════════════════════
def fig_chargepractice():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Як заряджати на практиці",
               "балансирний зарядник, ≤1C, зберігання ~3.8 В, у вогнетривкому мішку")
    s += rect(60, 122, 150, 100, fill=PANEL, stroke=INK, sw=1.7, rx=12)
    s += text(135, 152, "балансирний", size=12, anchor="middle", weight="bold")
    s += text(135, 172, "зарядник", size=12, anchor="middle", weight="bold")
    s += text(135, 198, "CC/CV, ≤1C", size=11, anchor="middle", fill=MUTE)
    s += line(210, 150, 300, 150, stroke=RED, w=2.2, marker="arrR")
    s += text(255, 142, "силові", size=9.5, anchor="middle", fill=RED)
    s += line(210, 192, 300, 192, stroke=BLUE, w=2.0, marker="arrB")
    s += text(255, 208, "баланс", size=9.5, anchor="middle", fill=BLUE)
    s += rect(304, 110, 150, 124, fill="#fff5e6", stroke=AMBER, sw=2.0, rx=12,
              dash="6,4")
    s += text(379, 102, "вогнетривкий мішок", size=10, anchor="middle",
              fill=AMBER, weight="bold")
    s += rect(326, 138, 106, 72, fill=BOX2, stroke=GREEN, sw=1.6, rx=8)
    s += text(379, 168, "пакет", size=12, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(379, 188, "4S LiPo", size=10.5, anchor="middle", fill=GREEN)
    s += rect(508, 96, 196, 250, fill="#eafaef", stroke=GREEN, sw=1.6, rx=12)
    s += text(606, 120, "РОБИ", size=14, anchor="middle", weight="bold",
              fill=GREEN)
    s += lines(524, 148, ["✓ струм ≤1C", "✓ баланс щоразу",
                          "✓ зберігай на ~3.8 В", "✓ у вогнетривкому мішку",
                          "✓ будь поряд, дивись", "✓ дай прохолонути"],
               size=10.5, lh=31, fill=INK)
    s += rect(724, 96, 196, 250, fill="#fde2e2", stroke=RED, sw=1.6, rx=12)
    s += text(822, 120, "НЕ РОБИ", size=14, anchor="middle", weight="bold",
              fill=RED)
    s += lines(740, 148, ["✗ не перезаряджай", "✗ не заряджай здуту",
                          "✗ не нижче 0 °C", "✗ не лишай без нагляду",
                          "✗ не проколюй", "✗ не «в нуль» на зберігання"],
               size=10.5, lh=31, fill=INK)
    s += text(W / 2, H - 14,
              "Літій не пробачає недбалості при заряді: надлишок енергії при "
              "аварії виходить вогнем, що його не «придушити» — треба тривало охолоджувати водою.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.7.1 — Бюджет енергії: формула
# ════════════════════════════════════════════════════════════════════════════
def fig_budget():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Бюджет енергії: час польоту = запас ÷ витрата",
               "корисну енергію (Вт·год) ділимо на середню потужність (Вт) → тривалість")
    stages = [
        (60, "Повна енергія", "5 А·год × 14.8 В", "= 74 Вт·год", GREEN, BOX2),
        (300, "× корисних ~80%", "(не в нуль!)", "≈ 59 Вт·год", AMBER, BOX3),
        (540, "÷ витрата", "÷ 300 Вт", "(середня)", BLUE, BOX1),
        (780, "= час", "≈ 0.20 год", "≈ 12 хв", RED, "#fde2e2")]
    by, bw, bh = 150, 150, 120
    for i, (x, h, a, b, col, fill) in enumerate(stages):
        s += rect(x, by, bw, bh, fill=fill, stroke=col, sw=1.8, rx=12)
        s += text(x + bw / 2, by + 32, h, size=13, anchor="middle",
                  weight="bold", fill=col)
        s += text(x + bw / 2, by + 66, a, size=12.5, anchor="middle",
                  weight="bold")
        s += text(x + bw / 2, by + 92, b, size=12, anchor="middle", fill=MUTE)
        if i < 3:
            s += line(x + bw + 6, by + bh / 2, x + 234, by + bh / 2,
                      stroke=INK, w=2.0, marker="arr")
    s += rect(260, 300, 440, 56, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(480, 334, "t = E_корисна ÷ P_середня", size=17, anchor="middle",
              weight="bold")
    s += text(W / 2, H - 14,
              "Рахуй у ВАТ-ГОДИНАХ, не в mAh: лише вони з'єднують запас із "
              "витратою.", size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.7.2 — Куди йдуть ватти: бюджет потужності
# ════════════════════════════════════════════════════════════════════════════
def fig_powertable():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Куди йдуть ватти: мотори майже все",
               "у бюджеті потужності зависання моторів домінує; решта — крихти, та теж рахуються")
    items = [("Мотори (зависання)", 270, GREEN), ("Відеопередавач", 10, BLUE),
             ("Бортовий комп'ютер", 10, AMBER), ("Серво / підвіс", 7, "#9333ea"),
             ("ПК + давачі + RX", 3, MUTE)]
    total = sum(v for _, v, _ in items)
    ox, oy, maxw = 250, 104, 520
    s += text(ox - 10, oy - 14, "система", size=11, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ox + 10, oy - 14, "потужність →", size=11, fill=MUTE,
              weight="bold")
    yy = oy
    for name, v, col in items:
        s += text(ox - 10, yy + 20, name, size=11.5, anchor="end")
        w = maxw * v / total
        s += rect(ox, yy, max(w, 3), 30, fill=col, stroke="none", rx=4)
        s += text(ox + max(w, 3) + 8, yy + 21, f"{v} Вт", size=11.5,
                  weight="bold", fill=col)
        s += text(ox + max(w, 3) + 58, yy + 21, f"({100 * v // total}%)",
                  size=10, fill=MUTE)
        yy += 44
    s += line(ox, yy + 4, ox + maxw, yy + 4, stroke=INK, w=1.2)
    s += text(ox - 10, yy + 30, "РАЗОМ", size=12, anchor="end", weight="bold")
    s += text(ox, yy + 30, f"≈ {total} Вт — це й ділить корисну енергію на час",
              size=12, weight="bold")
    s += text(W / 2, H - 14,
              "Мотори — ~90% витрати, тож час польоту найперше визначає вага й "
              "ефективність тяги; решту теж не ігноруй.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.7.3 — Більша батарея ≠ довший політ
# ════════════════════════════════════════════════════════════════════════════
def fig_weightspiral():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Більша батарея ≠ довший політ",
               "зайва вага батареї сама потребує тяги — є оптимум, за яким час падає")
    ox, oy, ow, oh = 110, 100, 740, 250
    s += line(ox, oy, ox, oy + oh, stroke=INK, w=1.5)
    s += line(ox, oy + oh, ox + ow, oy + oh, stroke=INK, w=1.5)
    s += text(ox - 10, oy + 6, "час", size=11, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ox - 10, oy + 20, "польоту", size=11, anchor="end", fill=MUTE)
    s += text(ox + ow, oy + oh + 22, "вага (ємність) батареї →", size=11,
              anchor="end", fill=MUTE, weight="bold")
    pts = []
    for k in range(101):
        f = k / 100
        pts.append((f, (f ** 0.6) * math.exp(-1.3 * f)))
    ymax = max(y for _, y in pts)
    sp = [(ox + f * ow, oy + oh - (y / ymax) * (oh - 20)) for f, y in pts]
    s += poly(sp, fill="none", stroke=GREEN, sw=2.8, closed=False)
    fopt = max(pts, key=lambda p: p[1])[0]
    s += line(ox + fopt * ow, oy + oh, ox + fopt * ow, oy + 20, stroke=MUTE,
              w=1.2, dash="5,4")
    s += circle(ox + fopt * ow, oy + 20, 5, fill=AMBER, stroke=INK, sw=1.2)
    s += text(ox + fopt * ow, oy + 8, "оптимум", size=11, anchor="middle",
              weight="bold", fill=AMBER)
    s += text(ox + 70, oy + oh - 26, "мала: мало енергії", size=10.5, fill=MUTE)
    s += text(ox + ow - 20, oy + 54, "завелика:", size=10.5, anchor="end",
              fill=RED)
    s += text(ox + ow - 20, oy + 70, "сама себе несе", size=10.5, anchor="end",
              fill=RED)
    s += text(W / 2, H - 14,
              "Додав батарею — додав і вагу, яку треба тримати в повітрі. За "
              "оптимумом приріст енергії вже не окупає зайвих грамів.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 45.7.4 — Резерв і повернення (RTL)
# ════════════════════════════════════════════════════════════════════════════
def fig_reserve():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Резерв і повернення: не плануй на 100%",
               "ділимо запас на місію + резерв (дорога додому, посадка, вітер, старіння)")
    s += text(W / 2, 100,
              "Польотний контролер рахує спожиті mAh (лічба кулонів, давач "
              "живлення 44.1) і стежить за порогом", size=10.5, anchor="middle",
              fill=MUTE, italic=True)
    gx, gy, gw, gh = 80, 150, 800, 70
    segs = [(0.62, "#cdeed8", GREEN, "МІСІЯ", "корисна робота"),
            (0.20, "#dbeafe", BLUE, "ДОДОМУ", "дорога назад"),
            (0.12, "#fff0d8", AMBER, "ПОСАДКА", "+ запас на вітер"),
            (0.06, "#fde2e2", RED, "НЗ", "не чіпати")]
    x = gx
    for fr, fill, col, lab, sub in segs:
        w = gw * fr
        s += rect(x, gy, w, gh, fill=fill, stroke=col, sw=1.6, rx=0)
        s += text(x + w / 2, gy + 30, lab, size=12, anchor="middle",
                  weight="bold", fill=col)
        s += text(x + w / 2, gy + 50, sub, size=9, anchor="middle", fill=MUTE)
        x += w
    s += rect(gx, gy, gw, gh, fill="none", stroke=INK, sw=1.6, rx=0)
    s += text(gx, gy - 12, "100% корисної енергії", size=11, fill=MUTE,
              weight="bold")
    s += text(gx + gw, gy - 12, "0%", size=11, anchor="end", fill=MUTE,
              weight="bold")
    xt = gx + gw * 0.62
    s += line(xt, gy + gh, xt, gy + gh + 32, stroke=RED, w=2.0, marker="arrR")
    s += text(xt, gy + gh + 50, "тут контролер вмикає «ДОДОМУ» (RTL)", size=11,
              anchor="middle", weight="bold", fill=RED)
    s += text(xt, gy + gh + 68,
              "коли лишилось рівно стільки, щоб долетіти й сісти", size=10,
              anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Тверде правило: сідай із 20–30% у запасі. «До нуля» не літають — "
              "там і найгірша просадка, і смерть батареї.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-45-0-1-whylithium.svg":    fig_whylithium,
    "fig-45-0-2-threemen.svg":      fig_threemen,
    "fig-45-0-3-rockingchair.svg":  fig_rockingchair,
    "fig-45-0-4-dronebattery.svg":  fig_dronebattery,
    "fig-45-1-1-rails.svg":         fig_rails,
    "fig-45-1-2-linear.svg":        fig_linear,
    "fig-45-1-3-switching.svg":     fig_switching,
    "fig-45-1-4-efficiency.svg":    fig_efficiency,
    "fig-45-2-1-buckphases.svg":    fig_buckphases,
    "fig-45-2-2-inductorcurrent.svg": fig_inductorcurrent,
    "fig-45-2-3-duty.svg":          fig_duty,
    "fig-45-2-4-syncboost.svg":     fig_syncboost,
    "fig-45-3-1-powertree.svg":     fig_powertree,
    "fig-45-3-2-inrush.svg":        fig_inrush,
    "fig-45-3-3-sequencing.svg":    fig_sequencing,
    "fig-45-3-4-grounding.svg":     fig_grounding,
    "fig-45-4-1-cells.svg":         fig_cells,
    "fig-45-4-2-capacity-energy.svg": fig_capacity_energy,
    "fig-45-4-3-dischargecurve.svg": fig_dischargecurve,
    "fig-45-4-4-soc.svg":           fig_soc,
    "fig-45-5-1-crate.svg":         fig_crate,
    "fig-45-5-2-internalresistance.svg": fig_internalresistance,
    "fig-45-5-3-sag.svg":           fig_sag,
    "fig-45-5-4-chooseC.svg":       fig_chooseC,
    "fig-45-6-1-cccv.svg":          fig_cccv,
    "fig-45-6-2-balance.svg":       fig_balance,
    "fig-45-6-3-bms.svg":           fig_bms,
    "fig-45-6-4-chargepractice.svg": fig_chargepractice,
    "fig-45-7-1-budget.svg":        fig_budget,
    "fig-45-7-2-powertable.svg":    fig_powertable,
    "fig-45-7-3-weightspiral.svg":  fig_weightspiral,
    "fig-45-7-4-reserve.svg":       fig_reserve,
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
