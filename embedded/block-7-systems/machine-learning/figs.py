#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 50 (Модуль 7) — чистий Python, без залежностей.
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
# Рис. 50.0.1 — Весни й зими ШІ
# ════════════════════════════════════════════════════════════════════════════
def fig_ai_winters():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Весни й зими штучного інтелекту",
               "галузь двічі злітала на надіях і двічі провалювалася в «зиму»; нейромережі весь час вважали глухим кутом")
    ax, ay = 70, 358
    s += rect(250, 138, 130, 220, fill="#eef2f7", stroke="none")
    s += rect(560, 138, 130, 220, fill="#eef2f7", stroke="none")
    s += text(315, 156, "1-а зима", size=8.5, anchor="middle", fill="#64748b",
              weight="bold")
    s += text(625, 156, "2-а зима", size=8.5, anchor="middle", fill="#64748b",
              weight="bold")
    s += line(ax, ay, ax + 840, ay, stroke=INK, w=1.4, marker="arr")
    s += text(ax + 838, ay + 22, "час →", size=9.5, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ax - 6, 132, "↑ гроші / надії", size=9, fill=MUTE, weight="bold")
    miles = [(180, 196, "1956", "Дартмут:", "народження ШІ", GREEN, True),
             (315, 330, "~1974", "перша", "зима", RED, False),
             (470, 206, "1980-ті", "експертні", "системи", AMBER, True),
             (625, 332, "~1987", "друга", "зима", RED, False),
             (870, 150, "2012+", "глибоке", "навчання", GREEN, True)]
    pts = [(90, 332), (180, 196), (315, 330), (470, 206), (625, 332),
           (770, 250), (870, 150)]
    s += poly(pts, fill="none", stroke=BLUE, sw=2.6, closed=False)
    for x, y, yr, d1, d2, col, up in miles:
        s += circle(x, y, 6, fill=col, stroke=INK, sw=1.3)
        ty = y - 50 if up else y + 16
        s += text(x, ty, yr, size=11, anchor="middle", weight="bold", fill=col)
        s += text(x, ty + 15, d1, size=8.6, anchor="middle", fill=MUTE)
        s += text(x, ty + 27, d2, size=8.6, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "А Джеффрі Гінтон усі ці роки тримався нейромереж — попри глузування "
              "й безгрошів'я. Зрештою виявився правий.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.0.2 — Гінтон: сорок років проти течії
# ════════════════════════════════════════════════════════════════════════════
def fig_hinton_persistence():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Гінтон: сорок років проти течії",
               "коли всі махнули рукою на нейромережі, він уперто шліфував їх — і дочекався, поки його учні довели його правоту")
    ax, ay = 100, 240
    s += line(ax, ay, ax + 780, ay, stroke="#cbd5e1", w=2.4)
    miles = [("1986", "Зворотне поширення", ["стаття в Nature:", "багатошарові ожили"], BLUE),
             ("2006", "Глибокі мережі довіри", ["оживив саме", "«глибоке навчання»"], BLUE),
             ("2012", "AlexNet (його учні)", ["перемога на ImageNet", "— світовий злам"], GREEN),
             ("2018", "Премія Тюрінга", ["«Нобель", "інформатики»"], AMBER),
             ("2024", "Нобель із фізики", ["за нейромережі", "(з Гопфілдом)"], GREEN)]
    n = len(miles)
    step = 780 / (n - 1)
    for i, (yr, t, d, col) in enumerate(miles):
        x = ax + i * step
        s += circle(x, ay, 9, fill=col, stroke=INK, sw=1.5)
        up = (i % 2 == 0)
        if up:
            s += line(x, ay - 9, x, ay - 40, stroke=col, w=1.2)
            s += text(x, ay - 80, yr, size=13, anchor="middle", weight="bold",
                      fill=col)
            s += text(x, ay - 62, t, size=9.4, anchor="middle", weight="bold")
            s += text(x, ay - 48, d[0], size=8, anchor="middle", fill=MUTE)
        else:
            s += line(x, ay + 9, x, ay + 40, stroke=col, w=1.2)
            s += text(x, ay + 58, yr, size=13, anchor="middle", weight="bold",
                      fill=col)
            s += text(x, ay + 76, t, size=9.4, anchor="middle", weight="bold")
            s += text(x, ay + 90, d[0], size=8, anchor="middle", fill=MUTE)
    s += rect(120, 360, 720, 60, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 384,
              "Більшу частину кар'єри він сперечався з усією галуззю — і виявився правий.",
              size=10.5, anchor="middle", weight="bold", fill=BLUE)
    s += text(480, 404,
              "Тому Гінтона (поряд із Бенжіо й Лекуном) звуть «хрещеним батьком» глибокого навчання.",
              size=9.3, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.0.3 — Чому зими, і чому інакше
# ════════════════════════════════════════════════════════════════════════════
def fig_why_winters():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Чому приходять зими — і чому цього разу інакше",
               "зима = забагато обіцянок → замало результату → обвал грошей; а злет 2012-го дали три речі, яких бракувало")
    s += rect(50, 104, 410, 304, fill="#fbfbfd", stroke=RED, sw=1.8, rx=12)
    s += text(255, 128, "ЦИКЛ РОЗЧАРУВАННЯ", size=11, anchor="middle",
              weight="bold", fill=RED)
    cyc = ["надмірні обіцянки («скоро як людина»)", "шумиха, потік грошей",
           "результат не дотягує", "розчарування, недовіра", "обвал фінансування → ЗИМА"]
    for i, c in enumerate(cyc):
        y = 158 + i * 46
        col = RED if i == 4 else "#475569"
        s += rect(80, y, 350, 34, fill=("#fde2e2" if i == 4 else PANEL),
                  stroke=col, sw=1.2, rx=7)
        s += text(255, y + 22, c, size=9.4, anchor="middle",
                  weight=("bold" if i == 4 else "normal"),
                  fill=(RED if i == 4 else INK))
        if i < 4:
            s += line(255, y + 34, 255, y + 46, stroke=MUTE, w=1.3,
                      marker="arr")
    s += rect(500, 104, 410, 304, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(705, 128, "ЧОМУ 2012-Й — ІНШИЙ", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(705, 156, "ідея (нейромережі) була та сама —", size=9.6,
              anchor="middle")
    s += text(705, 172, "нарешті зійшлися УМОВИ:", size=9.6, anchor="middle",
              weight="bold")
    ing = [("ДАНІ", "ImageNet: мільйони мічених фото", BLUE),
           ("ОБЧИСЛЕННЯ", "GPU: тисячі ядер для згорток", AMBER),
           ("ГЛИБИНА", "багато шарів + кращі прийоми", GREEN)]
    for i, (t, d, col) in enumerate(ing):
        y = 196 + i * 56
        s += rect(525, y, 360, 46, fill="white", stroke=col, sw=1.5, rx=8)
        s += text(545, y + 20, t, size=10.5, weight="bold", fill=col)
        s += text(545, y + 37, d, size=8.6, fill=MUTE)
    s += text(705, 392, "не нова ідея — нові умови", size=9.5, anchor="middle",
              fill="#15803d", weight="bold", italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.0.4 — Дорожня карта Розділу 50
# ════════════════════════════════════════════════════════════════════════════
def fig_roadmap_ml():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Куди ми йдемо: від «вчитися з даних» до «нейромережа на чипі»",
               "що таке ML → дві фази → нейрон і шар → як вчиться → CNN → дані й узагальнення → TinyML → де рахувати → межі")

    def card(x, y, num, l1, l2, col):
        o = rect(x, y, 160, 84, fill=PANEL, stroke=col, sw=1.7, rx=10)
        o += rect(x, y, 48, 84, fill=col, stroke="none", rx=10, opacity=0.16)
        o += text(x + 24, y + 47, num, size=12, anchor="middle", weight="bold",
                  fill=col)
        o += text(x + 58, y + 36, l1, size=9.3)
        o += text(x + 58, y + 54, l2, size=9.3)
        return o
    r1 = [(40, "50.1", "що таке", "ML"), (220, "50.2", "навчання /", "вивід"),
          (400, "50.3", "нейрон", "і шар"), (580, "50.4", "як вчиться", "(градієнт)"),
          (760, "50.5", "CNN для", "зображень")]
    c1 = [BLUE, BLUE, AMBER, AMBER, GREEN]
    for k, (x, num, l1, l2) in enumerate(r1):
        s += card(x, 128, num, l1, l2, c1[k])
        if k < 4:
            s += line(x + 160, 170, x + 180, 170, stroke=INK, w=1.6,
                      marker="arr")
    s += line(840, 212, 840, 288, stroke=INK, w=1.6, marker="arr")
    r2 = [(760, "50.6", "дані,", "узагальнення"), (540, "50.7", "TinyML,", "квантування"),
          (320, "50.8", "де", "рахувати"), (100, "50.9", "межі,", "етика")]
    c2 = [GREEN, GREEN, BLUE, AMBER]
    for k, (x, num, l1, l2) in enumerate(r2):
        s += card(x, 290, num, l1, l2, c2[k])
        if k < 3:
            s += line(x, 332, x - 40, 332, stroke=INK, w=1.6, marker="arr")
    s += text(620, 304, "📜 50.5: окрема історія Лекуна й CNN", size=8.5,
              anchor="start", fill=MUTE)
    s += rect(40, 392, 880, 60, fill="#eef2ff", stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 416,
              "Дев'ять кроків від «машина вчиться з прикладів» до навченої мережі, що працює на бортовому чипі.",
              size=10.5, anchor="middle", weight="bold")
    s += text(480, 437,
              "Тут глибоке навчання з 49.7 нарешті відкривають зсередини — і саджають на апарат.",
              size=9.6, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.1.1 — Переворот: правила ↔ дані
# ════════════════════════════════════════════════════════════════════════════
def fig_rules_vs_data():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Переворот: замість правил — приклади",
               "класичне: дані + ПРАВИЛА → відповіді; машинне навчання: дані + ВІДПОВІДІ (приклади) → правило (модель)")
    s += rect(50, 108, 400, 250, fill="#fbfbfd", stroke=BLUE, sw=1.8, rx=12)
    s += text(250, 132, "КЛАСИЧНЕ ПРОГРАМУВАННЯ", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += rect(78, 162, 116, 38, fill=PANEL, stroke=INK, sw=1.2, rx=7)
    s += text(136, 186, "дані", size=10, anchor="middle", weight="bold")
    s += rect(78, 210, 116, 42, fill="#dbeafe", stroke=BLUE, sw=1.4, rx=7)
    s += text(136, 228, "ПРАВИЛА", size=9.5, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(136, 243, "(пише людина)", size=7.4, anchor="middle", fill=MUTE)
    s += line(198, 206, 240, 206, stroke=INK, w=1.6, marker="arr")
    s += rect(246, 185, 78, 42, fill="#1e293b", stroke=INK, sw=1.2, rx=7)
    s += text(285, 210, "машина", size=9, anchor="middle", fill="white")
    s += line(328, 206, 368, 206, stroke=INK, w=1.6, marker="arr")
    s += rect(372, 185, 70, 42, fill=BOX2, stroke=GREEN, sw=1.4, rx=7)
    s += text(407, 210, "відповіді", size=8.6, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(250, 296, "людина пише ПРАВИЛО, машина його виконує", size=9,
              anchor="middle", fill=MUTE)
    s += text(250, 324, "добре, коли правило можна сформулювати", size=9,
              anchor="middle", fill=MUTE)
    s += rect(510, 108, 400, 250, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(710, 132, "МАШИННЕ НАВЧАННЯ", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += rect(536, 162, 112, 38, fill=PANEL, stroke=INK, sw=1.2, rx=7)
    s += text(592, 186, "дані", size=10, anchor="middle", weight="bold")
    s += rect(536, 210, 112, 42, fill=BOX2, stroke=GREEN, sw=1.4, rx=7)
    s += text(592, 228, "ВІДПОВІДІ", size=9.3, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(592, 243, "(приклади)", size=7.4, anchor="middle", fill=MUTE)
    s += line(652, 206, 690, 206, stroke=INK, w=1.6, marker="arr")
    s += rect(694, 184, 78, 44, fill="#1e293b", stroke=INK, sw=1.2, rx=7)
    s += text(733, 202, "машина", size=9, anchor="middle", fill="white")
    s += text(733, 216, "вчиться", size=8, anchor="middle", fill="#94a3b8")
    s += line(776, 206, 814, 206, stroke=INK, w=1.6, marker="arr")
    s += rect(818, 184, 84, 44, fill="#dbeafe", stroke=BLUE, sw=1.4, rx=7)
    s += text(860, 202, "ПРАВИЛО", size=8.4, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(860, 217, "(модель)", size=7.4, anchor="middle", fill=MUTE)
    s += text(710, 296, "людина дає ПРИКЛАДИ, машина виводить правило", size=9,
              anchor="middle", fill=MUTE)
    s += text(710, 324, "рятує, коли правило сформулювати НЕ вийде", size=9,
              anchor="middle", fill="#15803d", weight="bold")
    s += text(W / 2, H - 14,
              "Те, що було ВХОДОМ (правила), стає ВИХОДОМ: машина пише правило "
              "сама, дивлячись на приклади.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.1.2 — Де правила безсилі
# ════════════════════════════════════════════════════════════════════════════
def fig_where_rules_fail():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Де правила безсилі — а приклади є",
               "є задачі, де правило написати легко (арифметика, сортування), і де неможливо (впізнати кота, почерк, голос)")
    s += rect(50, 108, 400, 300, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(250, 132, "ПРАВИЛО НАПИСАТИ ЛЕГКО", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(80, 168, ["• 2 + 2 = 4 (арифметика)",
                         "• посортувати числа за зростанням",
                         "• «якщо напруга < 3.3 В — тривога»",
                         "• «якщо темно — увімкнути світло»"], size=10, lh=30)
    s += rect(80, 300, 340, 84, fill="white", stroke=GREEN, sw=1.3, rx=9)
    s += text(250, 326, "→ звичайний код (49.6)", size=10.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(250, 348, "чітке, дешеве, зрозуміле;", size=9, anchor="middle",
              fill=MUTE)
    s += text(250, 366, "машинне навчання тут зайве", size=9, anchor="middle",
              fill=MUTE)
    s += rect(510, 108, 400, 300, fill="#fef2f2", stroke=RED, sw=1.8, rx=12)
    s += text(710, 132, "ПРАВИЛО НАПИСАТИ НЕМОЖЛИВО", size=11, anchor="middle",
              weight="bold", fill=RED)
    s += lines(540, 168, ["• «це КІТ» — а які правила? вуха? хутро?",
                          "• «це цифра 7» — мільйон почерків",
                          "• «це слово ‘привіт’» — голоси, акценти",
                          "• «це перешкода попереду»"], size=10, lh=30)
    s += rect(540, 300, 340, 84, fill="white", stroke=RED, sw=1.3, rx=9)
    s += text(710, 324, "правила нема — зате ПРИКЛАДІВ безліч", size=9.5,
              anchor="middle", weight="bold", fill=RED)
    s += text(710, 346, "→ показати приклади й НАВЧИТИ модель", size=9.5,
              anchor="middle", weight="bold", fill=BLUE)
    s += text(710, 366, "саме тут сяє машинне навчання", size=9,
              anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.1.3 — Три роди навчання
# ════════════════════════════════════════════════════════════════════════════
def fig_three_kinds():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Три роди навчання",
               "з учителем (приклади з відповідями); без учителя (без відповідей → структура); з підкріпленням (спроба + винагорода)")
    cards = [("З УЧИТЕЛЕМ", "supervised", BLUE,
              ["приклади З відповідями", "(кіт / пес — підписані)",
               "→ вчить вхід → вихід", "класифікація, регресія",
               "★ наші детектори (49.7)"]),
             ("БЕЗ УЧИТЕЛЯ", "unsupervised", AMBER,
              ["приклади БЕЗ відповідей", "→ знайти структуру сам",
               "групувати схоже,", "ловити аномалії",
               "(напр. дивну поведінку)"]),
             ("З ПІДКРІПЛЕННЯМ", "reinforcement", GREEN,
              ["діяти → винагорода / кара", "→ покращити стратегію",
               "вчитися спробами", "(летіти, балансувати)",
               "як шашки Семюела (§10)"])]
    for i, (t, en, col, rows) in enumerate(cards):
        x = 50 + i * 290
        s += rect(x, 108, 270, 300, fill=PANEL, stroke=col, sw=1.9, rx=12)
        s += rect(x, 108, 270, 40, fill=col, stroke="none", rx=11, opacity=0.15)
        s += text(x + 135, 128, t, size=12, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 135, 143, en, size=8.5, anchor="middle", fill=MUTE,
                  italic=True)
        s += lines(x + 20, 178, rows, size=9.6, lh=26)
    s += text(W / 2, H - 14,
              "Для нашого дрона головне — навчання З УЧИТЕЛЕМ: підписані приклади "
              "вчать модель упізнавати ціль.", size=10.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.1.4 — Серце ML — дані
# ════════════════════════════════════════════════════════════════════════════
def fig_data_is_heart():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Серце машинного навчання — дані; модель тоді узагальнює",
               "модель учиться на тренувальних прикладах, тоді УЗАГАЛЬНЮЄ на нові, небачені; яка дата — така й модель")
    s += text(230, 116, "НАВЧАННЯ: припасуватися до прикладів", size=10,
              anchor="middle", weight="bold")
    for i in range(4):
        x = 76 + i * 44
        s += rect(x, 134, 38, 30, fill="#1e293b", stroke=INK, sw=0.8)
        s += rect(x, 134, 38, 8, fill=GREEN, stroke="none", opacity=0.5)
    s += text(164, 182, "мічені приклади", size=8.5, anchor="middle", fill=MUTE)
    s += line(262, 150, 302, 150, stroke=INK, w=1.6, marker="arr")
    s += rect(308, 128, 112, 44, fill=BOX1, stroke=BLUE, sw=1.5, rx=8)
    s += text(364, 155, "МОДЕЛЬ", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(710, 116, "УЗАГАЛЬНЕННЯ: відповідь на НОВЕ", size=10,
              anchor="middle", weight="bold")
    s += rect(540, 128, 80, 44, fill="#1e293b", stroke=INK, sw=1)
    s += text(580, 154, "новий вхід", size=8, anchor="middle", fill="white")
    s += line(624, 150, 662, 150, stroke=INK, w=1.6, marker="arr")
    s += rect(668, 128, 104, 44, fill=BOX1, stroke=BLUE, sw=1.5, rx=8)
    s += text(720, 155, "МОДЕЛЬ", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    s += line(776, 150, 814, 150, stroke=INK, w=1.6, marker="arr")
    s += rect(818, 128, 92, 44, fill=BOX2, stroke=GREEN, sw=1.4, rx=8)
    s += text(864, 150, "відповідь", size=8.5, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(864, 164, "(передбачення)", size=7, anchor="middle", fill=MUTE)
    s += rect(60, 220, 840, 82, fill="#fffbeb", stroke=AMBER, sw=1.5, rx=11)
    s += text(480, 244,
              "Модель не краща за свої дані: «сміття на вході → сміття на виході»",
              size=11, anchor="middle", weight="bold", fill="#92400e")
    s += lines(110, 266,
               ["• вузькі чи упереджені приклади → вузька, упереджена модель (бачила лише денні фото — вночі осліпне);",
                "• дані мають ПРЕДСТАВЛЯТИ реальність, де модель працюватиме (докладніше — узагальнення, 50.6)."],
               size=9.5, lh=20)
    s += text(W / 2, H - 14,
              "Машинне навчання — не магія: це припасування до прикладів плюс "
              "узагальнення на схоже. Поза баченим воно кволе.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.2.1 — Дві фази
# ════════════════════════════════════════════════════════════════════════════
def fig_two_phases():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Дві фази життя моделі: навчання й вивід",
               "навчання — модель ЗМІНЮЄТЬСЯ під дані (важко, раз); вивід — модель ЗАМОРОЖЕНА, лише відповідає (легко, щоразу)")
    s += rect(50, 104, 400, 300, fill="#fbfbfd", stroke=AMBER, sw=1.9, rx=12)
    s += text(250, 127, "НАВЧАННЯ", size=12.5, anchor="middle", weight="bold",
              fill="#b06b00")
    s += text(250, 143, "(модель змінюється)", size=8.5, anchor="middle",
              fill=MUTE)
    s += rect(78, 166, 104, 48, fill=PANEL, stroke=INK, sw=1.2, rx=7)
    s += text(130, 187, "дані", size=10, anchor="middle", weight="bold")
    s += text(130, 202, "+ мітки", size=8.4, anchor="middle", fill=MUTE)
    s += line(184, 190, 222, 190, stroke=INK, w=1.6, marker="arr")
    s += rect(226, 162, 162, 56, fill="#fff5e6", stroke=AMBER, sw=1.6, rx=8)
    s += text(307, 184, "модель підкручує", size=9, anchor="middle",
              weight="bold")
    s += text(307, 201, "ВАГИ ↻", size=10.5, anchor="middle", weight="bold",
              fill="#b06b00")
    s += text(307, 234, "↻ повторювати по всіх даних", size=8, anchor="middle",
              fill=MUTE)
    s += line(250, 244, 250, 268, stroke=INK, w=1.5, marker="arr")
    s += rect(150, 270, 200, 48, fill=BOX2, stroke=GREEN, sw=1.6, rx=9)
    s += text(250, 290, "навчена МОДЕЛЬ", size=10.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(250, 306, "(файл ваг)", size=8, anchor="middle", fill=MUTE)
    s += text(250, 344, "важко · раз · потужні машини (GPU / хмара)", size=9,
              anchor="middle", fill=MUTE)
    s += rect(510, 104, 400, 300, fill="#eafaef", stroke=GREEN, sw=1.9, rx=12)
    s += text(710, 127, "ВИВІД (інференс)", size=12.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(710, 143, "(модель заморожена)", size=8.5, anchor="middle",
              fill=MUTE)
    s += rect(534, 196, 92, 50, fill="#1e293b", stroke=INK, sw=1.2, rx=7)
    s += text(580, 225, "новий вхід", size=8.4, anchor="middle", fill="white")
    s += line(630, 221, 666, 221, stroke=INK, w=1.6, marker="arr")
    s += rect(670, 194, 110, 54, fill=BOX1, stroke=BLUE, sw=1.6, rx=8)
    s += text(725, 214, "МОДЕЛЬ", size=10.5, anchor="middle", weight="bold",
              fill=BLUE)
    s += poly([(714, 234), (714, 228), (728, 228), (728, 234)], fill="none",
              stroke=INK, sw=1.3, closed=False)
    s += rect(710, 234, 22, 12, fill="#94a3b8", stroke=INK, sw=0.8, rx=2)
    s += text(745, 243, "заморожено", size=7.4, anchor="start", fill=MUTE)
    s += line(784, 221, 820, 221, stroke=INK, w=1.6, marker="arr")
    s += rect(824, 196, 78, 50, fill=BOX2, stroke=GREEN, sw=1.5, rx=8)
    s += text(863, 225, "відповідь", size=8.4, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(710, 300, "ваги НЕ міняються — лише читаються", size=9,
              anchor="middle", fill=MUTE)
    s += text(710, 344, "легко · щоразу · на пристрої (борт)", size=9,
              anchor="middle", fill=MUTE)
    s += line(352, 294, 506, 224, stroke=INK, w=1.4, marker="arr", dash="4,3")
    s += text(432, 250, "розгорнути", size=8, anchor="middle", fill=MUTE,
              weight="bold")
    s += text(W / 2, H - 14,
              "Натренуй РАЗ (важко) — застосовуй БЕЗЛІЧ разів (легко). Дрон майже "
              "завжди робить лише вивід.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.2.2 — Що тече: вперед і назад
# ════════════════════════════════════════════════════════════════════════════
def fig_whats_flowing():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Що тече в кожній фазі: вперед — і назад",
               "вивід — лише прохід ВПЕРЕД (вхід → відповідь); навчання додає прохід НАЗАД: виміряти похибку й підправити ваги")

    def layers(y, col):
        out = ""
        for i in range(3):
            x = 250 + i * 90
            out += rect(x, y - 22, 44, 44, fill=PANEL, stroke=col, sw=1.4, rx=6)
        return out
    s += text(70, 122, "ВИВІД — лише ВПЕРЕД", size=11, weight="bold",
              fill="#15803d")
    s += rect(70, 146, 84, 44, fill="#1e293b", stroke=INK, sw=1.1, rx=6)
    s += text(112, 172, "вхід", size=9, anchor="middle", fill="white")
    s += layers(168, GREEN)
    s += line(156, 168, 248, 168, stroke=INK, w=1.5, marker="arr")
    for i in range(2):
        s += line(294 + i * 90, 168, 338 + i * 90, 168, stroke=INK, w=1.5,
                  marker="arr")
    s += line(472, 168, 516, 168, stroke=INK, w=1.5, marker="arr")
    s += rect(520, 146, 96, 44, fill=BOX2, stroke=GREEN, sw=1.4, rx=6)
    s += text(568, 172, "відповідь", size=8.6, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(740, 168, "ваги НЕ міняються", size=10, anchor="middle",
              fill=MUTE, weight="bold")
    s += line(60, 224, 900, 224, stroke="#e5e7eb", w=1)
    s += text(70, 256, "НАВЧАННЯ — ВПЕРЕД + НАЗАД", size=11, weight="bold",
              fill="#b06b00")
    s += rect(70, 280, 84, 44, fill="#1e293b", stroke=INK, sw=1.1, rx=6)
    s += text(112, 306, "вхід", size=9, anchor="middle", fill="white")
    s += layers(302, AMBER)
    s += line(156, 302, 248, 302, stroke=INK, w=1.5, marker="arr")
    for i in range(2):
        s += line(294 + i * 90, 302, 338 + i * 90, 302, stroke=INK, w=1.5,
                  marker="arr")
    s += line(472, 302, 516, 302, stroke=INK, w=1.5, marker="arr")
    s += rect(520, 280, 96, 44, fill=PANEL, stroke=INK, sw=1.2, rx=6)
    s += text(568, 300, "передба-", size=8, anchor="middle")
    s += text(568, 313, "чення", size=8, anchor="middle")
    s += text(700, 286, "порівняти", size=8.5, anchor="middle", fill=MUTE)
    s += rect(656, 295, 90, 30, fill="#fde2e2", stroke=RED, sw=1.3, rx=6)
    s += text(701, 314, "ПОХИБКА", size=9, anchor="middle", weight="bold",
              fill=RED)
    s += text(701, 280, "↑ vs мітка", size=8, anchor="middle", fill=MUTE)
    s += line(656, 348, 250, 348, stroke=RED, w=1.8, marker="arrR")
    s += text(453, 366, "← прохід НАЗАД: підправити ВАГИ (↻ багато разів, епохи)",
              size=9, anchor="middle", fill=RED, weight="bold")
    s += rect(150, 392, 660, 50, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 414,
              "Вивід — це лише ПОЛОВИНА навчання (прохід уперед). Саме прохід "
              "НАЗАД (50.4) і є «вчитися».", size=10.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(480, 432, "тому вивід і дешевший за навчання", size=9,
              anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.2.3 — Асиметрія
# ════════════════════════════════════════════════════════════════════════════
def fig_asymmetry_cost():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Велика асиметрія: де й скільки коштує",
               "навчання — години-тижні, ферма GPU, увесь набір, гора енергії, РАЗ; вивід — мілісекунди, один чип, лише модель, ЩОКАДРУ")
    s += rect(330, 110, 280, 36, fill="#fff5e6", stroke=AMBER, sw=1.4, rx=7)
    s += text(470, 133, "НАВЧАННЯ", size=12, anchor="middle", weight="bold",
              fill="#b06b00")
    s += rect(630, 110, 280, 36, fill="#eafaef", stroke=GREEN, sw=1.4, rx=7)
    s += text(770, 133, "ВИВІД", size=12, anchor="middle", weight="bold",
              fill="#15803d")
    rows = [("час", "тижні (один раз)", "мілісекунди (щоразу)"),
            ("залізо", "ферма GPU / хмара", "один чип на борту"),
            ("дані", "увесь набір прикладів", "лише новий вхід"),
            ("енергія", "величезна", "мала"),
            ("як часто", "РАЗ (чи зрідка)", "ПОСТІЙНО")]
    y = 154
    for crit, tr, inf in rows:
        s += text(60, y + 25, crit, size=10.5, weight="bold")
        s += rect(330, y, 280, 42, fill=PANEL, stroke="#e5e7eb", sw=1, rx=6)
        s += text(470, y + 26, tr, size=9.6, anchor="middle", fill="#b06b00")
        s += rect(630, y, 280, 42, fill="#f6fef9", stroke="#e5e7eb", sw=1, rx=6)
        s += text(770, y + 26, inf, size=9.6, anchor="middle", fill="#15803d")
        y += 50
    s += rect(60, y + 6, 850, 36, fill=BOX1, stroke=BLUE, sw=1.4, rx=9)
    s += text(485, y + 29,
              "Тренуй там, де потужно (хмара); застосовуй там, де треба (апарат). Звідси й уся архітектура — 50.8.",
              size=10.5, anchor="middle", weight="bold", fill=BLUE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.2.4 — На апараті
# ════════════════════════════════════════════════════════════════════════════
def fig_on_drone():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Що це означає для апарата: возиш заморожену модель",
               "на борт ставлять ГОТОВУ модель; апарат лише робить вивід щокадру; щоб покращити — перенавчають у хмарі й перевстановлюють")
    s += rect(300, 108, 360, 78, fill="#fff5e6", stroke=AMBER, sw=1.8, rx=12)
    s += text(480, 132, "ХМАРА / ДАТА-ЦЕНТР — НАВЧАННЯ", size=10.5,
              anchor="middle", weight="bold", fill="#b06b00")
    s += text(480, 154, "гори даних + GPU підганяють ваги", size=9,
              anchor="middle", fill=MUTE)
    s += text(480, 172, "→ виходить навчена модель (файл ваг)", size=9,
              anchor="middle", fill=INK)
    s += line(480, 188, 480, 226, stroke=INK, w=2, marker="arr")
    s += text(560, 210, "розгорнути модель", size=8.6, anchor="start",
              fill=MUTE, weight="bold")
    s += rect(300, 228, 360, 92, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(480, 252, "АПАРАТ — ВИВІД ЩОКАДРУ", size=10.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(480, 274, "заморожена модель: прохід уперед на кадрі", size=9,
              anchor="middle", fill=MUTE)
    s += text(480, 292, "у польоті НЕ вчиться — лише застосовує", size=9,
              anchor="middle", fill=INK)
    s += text(480, 310, "(і вивід теж коштує — оптимізуй, 50.7)", size=8.5,
              anchor="middle", fill="#15803d")
    s += line(300, 274, 190, 274, stroke=MUTE, w=1.5, dash="5,4")
    s += line(190, 274, 190, 147, stroke=MUTE, w=1.5, dash="5,4")
    s += line(190, 147, 298, 147, stroke=MUTE, w=1.5, dash="5,4", marker="arr")
    s += text(150, 212, "щоб", size=8.5, anchor="middle", fill=MUTE)
    s += text(150, 226, "покращити:", size=8.5, anchor="middle", fill=MUTE,
              weight="bold")
    s += text(150, 244, "зібрати нові", size=8, anchor="middle", fill=MUTE)
    s += text(150, 256, "дані →", size=8, anchor="middle", fill=MUTE)
    s += text(150, 270, "перенавчити", size=8, anchor="middle", fill=MUTE)
    s += rect(120, 340, 720, 64, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 362, "Модель = заморожене знання", size=11, anchor="middle",
              weight="bold")
    s += lines(150, 382,
               ["• статична після навчання: щоб змінити поведінку — перенавчають у хмарі й перевстановлюють (повільний цикл);",
                "• дані лишаються в хмарі — на борт їде ЛИШЕ модель (ваги), а не приклади, на яких училися."],
               size=9.4, lh=19)
    s += text(W / 2, H - 12,
              "Тому збій моделі не «полагодити на льоту»: це не баг у коді, а "
              "межі того, на чому її навчили.", size=10, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.3.1 — Штучний нейрон
# ════════════════════════════════════════════════════════════════════════════
def fig_neuron():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Штучний нейрон: зважена сума плюс «вмикач»",
               "входи множаться на ваги, додаються (+ зсув), результат проходить крізь активацію → вихід; ваги — те, що мережа ВИВЧАЄ")
    inp = [("x₁", 168), ("x₂", 228), ("x₃", 288)]
    ws = ["w₁", "w₂", "w₃"]
    sx, sy = 360, 228
    for (lab, y), w in zip(inp, ws):
        s += line(126, y, sx - 30, sy, stroke=BLUE, w=1.6, marker="arrB")
        s += text((126 + sx - 30) / 2 - 4, (y + sy) / 2 - 5, w, size=9.5,
                  fill=BLUE, weight="bold")
    for lab, y in inp:
        s += circle(108, y, 18, fill="#1e293b", stroke=INK, sw=1.3)
        s += text(108, y + 5, lab, size=11, anchor="middle", fill="white")
    s += circle(sx, sy, 30, fill=PANEL, stroke=INK, sw=1.6)
    s += text(sx, sy + 8, "Σ", size=20, anchor="middle", weight="bold")
    s += text(sx, sy + 52, "+ зсув b", size=9, anchor="middle", fill=MUTE)
    s += line(sx + 30, sy, 446, sy, stroke=INK, w=1.6, marker="arr")
    s += rect(450, sy - 32, 92, 64, fill="#eafaef", stroke=GREEN, sw=1.6, rx=8)
    s += line(460, sy + 18, 496, sy + 18, stroke=GREEN, w=2.2)
    s += line(496, sy + 18, 532, sy - 16, stroke=GREEN, w=2.2)
    s += text(496, sy + 42, "активація", size=8.4, anchor="middle",
              fill="#15803d", weight="bold")
    s += line(544, sy, 596, sy, stroke=INK, w=1.6, marker="arr")
    s += circle(622, sy, 23, fill=BOX2, stroke=GREEN, sw=1.6)
    s += text(622, sy + 4, "вихід", size=8.4, anchor="middle", weight="bold",
              fill="#15803d")
    s += rect(680, 150, 230, 150, fill=PANEL, stroke=INK, sw=1.2, rx=10)
    s += text(795, 174, "навіяно живим нейроном:", size=9, anchor="middle",
              weight="bold")
    s += lines(702, 198, ["• дендрити → входи", "• тіло клітини → сума",
                          "• аксон → вихід", "Та насправді це —",
                          "просто арифметика."], size=9, lh=19)
    s += rect(120, 328, 720, 52, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 360, "вихід = активація( w₁·x₁ + w₂·x₂ + w₃·x₃ + b )",
              size=14, anchor="middle", weight="bold", fill=BLUE)
    s += text(W / 2, H - 14,
              "Один нейрон — це зважена сума входів, пропущена крізь активацію. "
              "Уся «магія» — у вагах, що їх мережа ВИВЧАЄ.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.3.2 — Ваги і зсув
# ════════════════════════════════════════════════════════════════════════════
def fig_weights_bias():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Ваги і зсув: що нейрон ВИВЧАЄ",
               "вага каже, наскільки ВАЖЛИВИЙ кожен вхід; зсув посуває поріг спрацювання; саме їх підкручує навчання (50.4)")
    s += rect(50, 108, 420, 300, fill="#fbfbfd", stroke=BLUE, sw=1.8, rx=12)
    s += text(260, 132, "ВАГА = важливість входу", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    bars = [("вхід A", 0.9, GREEN, "дуже важливий"),
            ("вхід B", 0.15, "#94a3b8", "майже не важить"),
            ("вхід C", -0.7, RED, "рахується ПРОТИ")]
    for i, (lab, w, col, note) in enumerate(bars):
        y = 168 + i * 70
        s += text(76, y + 16, lab, size=10, weight="bold")
        s += line(180, y + 12, 180, y + 12, stroke=INK, w=1)
        s += rect(180, y, 2, 24, fill=INK, stroke="none")
        bw = abs(w) * 180
        x0 = 182 if w > 0 else 182 - bw
        s += rect(x0, y + 4, bw, 16, fill=col, stroke="none", rx=3)
        s += text(372, y + 16, f"вага {w:+.1f}", size=9.5, anchor="end",
                  fill=col, weight="bold")
        s += text(260, y + 36, note, size=8.4, anchor="middle", fill=MUTE)
    s += rect(490, 108, 420, 300, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 132, "ЗСУВ b = посуває поріг", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(520, 166, ["більший зсув → нейронові ЛЕГШЕ",
                          "«спрацювати»; менший → важче.",
                          "Це наче ручка чутливості."], size=10, lh=24)
    s += rect(520, 250, 360, 138, fill="white", stroke=GREEN, sw=1.5, rx=10)
    s += text(700, 276, "Ваги + зсуви = ПАРАМЕТРИ", size=11.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(542, 300, ["• навчена модель — це просто НАБІР",
                          "  цих чисел (мільйони у великих);",
                          "• навчання (50.4) і є їх підбором,",
                          "  щоб модель менше помилялась."], size=9.4, lh=21)
    s += text(W / 2, H - 14,
              "Ваги й зсув — це і є «знання» нейрона. Дай ті самі входи, та зміни "
              "ваги — і рішення буде інше.", size=10.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.3.3 — Активація й нелінійність
# ════════════════════════════════════════════════════════════════════════════
def fig_activation():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Активація: чому без «згину» мережа безсила",
               "без активації стос нейронів — це знов одна пряма (XOR не взяти); активація (ReLU, сигмоїда) ГНЕ відгук")
    s += rect(50, 104, 420, 308, fill="#fbfbfd", stroke=BLUE, sw=1.8, rx=12)
    s += text(260, 128, "дві популярні активації", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    # ReLU
    ox, oy = 90, 232
    s += line(ox, oy, ox + 150, oy, stroke=INK, w=1.2)
    s += line(ox + 60, oy - 70, ox + 60, oy + 16, stroke=INK, w=1.2)
    s += line(ox + 10, oy, ox + 60, oy, stroke=GREEN, w=2.6)
    s += line(ox + 60, oy, ox + 140, oy - 70, stroke=GREEN, w=2.6)
    s += text(ox + 75, oy + 34, "ReLU: max(0, x)", size=9, anchor="middle",
              weight="bold")
    s += text(ox + 75, oy + 48, "нуль, далі прямо (швидко)", size=8,
              anchor="middle", fill=MUTE)
    # sigmoid
    sx0, sy0 = 280, 232
    s += line(sx0, sy0, sx0 + 150, sy0, stroke=INK, w=1.2)
    s += line(sx0 + 75, sy0 - 70, sx0 + 75, sy0 + 16, stroke=INK, w=1.2)
    sig = []
    for k in range(31):
        xx = -6 + 12 * k / 30
        yv = 1 / (1 + math.exp(-xx))
        sig.append((sx0 + 75 + xx * 11, sy0 - yv * 62))
    s += poly(sig, fill="none", stroke=AMBER, sw=2.6, closed=False)
    s += text(sx0 + 75, sy0 + 34, "сигмоїда: тисне у 0…1", size=9,
              anchor="middle", weight="bold")
    s += text(sx0 + 75, sy0 + 48, "плавний «вмикач»", size=8, anchor="middle",
              fill=MUTE)
    s += rect(490, 104, 420, 308, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 128, "нащо потрібна нелінійність", size=11, anchor="middle",
              weight="bold", fill="#15803d")

    def xorbox(x, ok, lab):
        out = rect(x, 156, 180, 150, fill="#0f172a", stroke=INK, sw=1.2)
        gx, gy, g = x + 40, 280, 90
        for px, py, c in [(0, 0, BLUE), (1, 1, BLUE), (0, 1, RED), (1, 0, RED)]:
            out += circle(gx + px * g, gy - py * g, 9, fill=c, stroke="white",
                          sw=1.3)
        if ok:
            out += poly([(gx - 8, gy - 0.28 * g), (gx + 0.5 * g, gy - 0.6 * g),
                         (gx + g + 8, gy - 0.28 * g)], fill="none",
                        stroke="#22c55e", sw=2.4, closed=False)
            out += poly([(gx - 8, gy - 0.72 * g), (gx + 0.5 * g, gy - 0.4 * g),
                         (gx + g + 8, gy - 0.72 * g)], fill="none",
                        stroke="#22c55e", sw=2.4, closed=False)
        else:
            out += line(gx - 8, gy - 0.85 * g, gx + g + 8, gy + 0.05 * g,
                        stroke=RED, w=2.4, dash="6,4")
        out += text(x + 90, 322, lab, size=9, anchor="middle", weight="bold",
                    fill=("#15803d" if ok else RED))
        return out
    s += xorbox(516, False, "лише пряма ✗ (XOR)")
    s += xorbox(714, True, "зі згином ✓")
    s += text(700, 352, "без активації багато шарів = одна пряма;", size=9,
              anchor="middle", fill=MUTE)
    s += text(700, 368, "активація ГНЕ межу → складні візерунки", size=9,
              anchor="middle", fill="#15803d", weight="bold")
    s += text(W / 2, H - 14,
              "Активація — це нелінійність. Без неї мережа вміє лише прямі межі "
              "(XOR з 50.0 не взяти); з нею — будь-які.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.3.4 — Нейрон → шар → мережа
# ════════════════════════════════════════════════════════════════════════════
def fig_layers():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Нейрон → шар → мережа",
               "шар — багато нейронів пліч-о-пліч (ті самі входи, свої ваги); стос шарів і є нейромережа; глибші шари — складніші ознаки")
    cols = [(150, 3), (330, 4), (510, 4), (690, 2)]
    cy = 224

    def nodes(x, n):
        return [(x, cy + (i - (n - 1) / 2) * 52) for i in range(n)]
    pos = [nodes(x, n) for x, n in cols]
    for a in range(len(pos) - 1):
        for (x1, y1) in pos[a]:
            for (x2, y2) in pos[a + 1]:
                s += line(x1 + 16, y1, x2 - 16, y2, stroke="#d4d4d8", w=0.8)
    colsc = [BLUE, AMBER, AMBER, GREEN]
    for ci, layer in enumerate(pos):
        for (x, y) in layer:
            s += circle(x, y, 16, fill="white", stroke=colsc[ci], sw=2)
    s += text(150, 122, "вхідний", size=9.5, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(420, 122, "приховані шари", size=9.5, anchor="middle",
              weight="bold", fill="#b06b00")
    s += text(690, 122, "вихідний", size=9.5, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(420, 360, "«глибока» мережа = багато шарів", size=10,
              anchor="middle", fill=MUTE, weight="bold")
    s += rect(60, 384, 840, 56, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 405,
              "Шар із m нейронів по n входів = m·n ваг + m зсувів → у великих мережах це МІЛЬЙОНИ параметрів (49.9, 50.7).",
              size=9.8, anchor="middle", weight="bold")
    s += text(480, 425,
              "Глибші шари будують усе складніші ознаки: краї → форми → об'єкти (49.7) — рукотворна луна зорової кори.",
              size=9.4, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.4.1 — Похибка
# ════════════════════════════════════════════════════════════════════════════
def fig_loss():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Похибка: одне число «наскільки модель помиляється»",
               "порівнюємо передбачення моделі з правильними відповідями; різниця згортається в ОДНЕ число — похибку; мета — зробити її малою")
    s += text(108, 142, "приклад", size=9.5, weight="bold")
    s += text(250, 142, "модель каже", size=9.5, weight="bold", fill=BLUE)
    s += text(400, 142, "правильно", size=9.5, weight="bold", fill="#15803d")
    s += text(540, 142, "промах", size=9.5, weight="bold", fill=RED)
    rows = [("кіт?", "0.2", "1.0", "великий"), ("пес?", "0.9", "1.0", "малий"),
            ("кіт?", "0.7", "0.0", "великий"), ("пес?", "0.85", "1.0", "малий")]
    y = 162
    for ex, pred, corr, miss in rows:
        s += text(108, y + 16, ex, size=10)
        s += text(250, y + 16, pred, size=10, fill=BLUE, weight="bold")
        s += text(400, y + 16, corr, size=10, fill="#15803d", weight="bold")
        col = RED if miss == "великий" else "#94a3b8"
        s += text(540, y + 16, miss, size=9.5, fill=col, weight="bold")
        s += line(100, y + 26, 600, y + 26, stroke="#eef0f2", w=0.8)
        y += 36
    s += line(616, 228, 676, 228, stroke=INK, w=1.8, marker="arr")
    s += text(648, 216, "згорнути", size=8, anchor="middle", fill=MUTE)
    s += rect(688, 192, 212, 72, fill="#fde2e2", stroke=RED, sw=1.8, rx=11)
    s += text(794, 218, "ПОХИБКА", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += text(794, 244, "= 0.83", size=16, anchor="middle", weight="bold",
              fill=RED)
    s += text(794, 286, "велика → дуже неправильно", size=8.4, anchor="middle",
              fill=MUTE)
    s += rect(688, 308, 212, 40, fill=BOX2, stroke=GREEN, sw=1.5, rx=9)
    s += text(794, 333, "мета навчання: → 0", size=10.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(W / 2, H - 14,
              "Похибка (функція втрат) стискає всі промахи в одне число. Уся "
              "наука навчання — зробити це число якомога меншим.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.4.2 — Градієнтний спуск
# ════════════════════════════════════════════════════════════════════════════
def fig_gradient_descent():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Градієнтний спуск: котитися з гори похибки",
               "уяви похибку як рельєф над значеннями ваг; градієнт — нахил (куди вгору); крок УНИЗ (проти градієнта) — і так до низини")
    ox, w = 110, 740

    def ly(t):
        loss = (t - 0.6) ** 2 * 1.3
        return 360 - (0.47 - loss) / 0.47 * 210

    s += line(ox, 360, ox + w, 360, stroke=INK, w=1.3, marker="arr")
    s += text(ox + w, 382, "значення ваги →", size=9.5, anchor="end",
              fill=MUTE, weight="bold")
    s += text(ox - 6, 138, "↑ похибка", size=9.5, fill=MUTE, weight="bold")
    curve = [(ox + (k / 60) * w, ly(k / 60)) for k in range(61)]
    s += poly(curve, fill="none", stroke=BLUE, sw=2.6, closed=False)
    steps = [0.07, 0.20, 0.32, 0.43, 0.51, 0.565, 0.595]
    for i, t in enumerate(steps):
        x, yv = ox + t * w, ly(t)
        s += circle(x, yv, 7, fill=(GREEN if i == len(steps) - 1 else AMBER),
                    stroke=INK, sw=1.2)
        if i < len(steps) - 1:
            t2 = steps[i + 1]
            s += line(x + 6, yv + 4, ox + t2 * w - 6, ly(t2) - 2, stroke=RED,
                      w=1.5, marker="arrR")
    s += text(ox + 0.10 * w, ly(0.07) - 16, "старт", size=9, anchor="middle",
              fill=MUTE, weight="bold")
    s += text(ox + 0.30 * w, ly(0.32) - 30, "градієнт = нахил;", size=9,
              fill=RED, weight="bold")
    s += text(ox + 0.30 * w, ly(0.32) - 18, "крок ПРОТИ нього (вниз)", size=9,
              fill=RED, weight="bold")
    s += circle(ox + 0.6 * w, ly(0.6), 9, fill=GREEN, stroke=INK, sw=1.4)
    s += text(ox + 0.6 * w, ly(0.6) + 26, "низина = найменша похибка",
              size=9.5, anchor="middle", fill="#15803d", weight="bold")
    s += text(ox + 0.6 * w, ly(0.6) + 40, "= найкращі ваги", size=9.5,
              anchor="middle", fill="#15803d")
    s += text(W / 2, H - 14,
              "Наче спускатися з гори в тумані, мацаючи схил: куди вниз — туди й "
              "крок. Так мережа підбирає ваги, що менше помиляються.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.4.3 — Темп навчання
# ════════════════════════════════════════════════════════════════════════════
def fig_learning_rate():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Темп навчання: який крок униз",
               "крок замалий — повзе вічно; завеликий — перестрибує низину й розгойдується; саме враз — упевнено сходить")

    def bowl(x0, lab, kind, col):
        cx, base, ww = x0 + 130, 330, 230

        def by(t):
            return base - (0.25 - (t - 0.5) ** 2) / 0.25 * 150
        out = text(cx, 124, lab, size=10.5, anchor="middle", weight="bold",
                   fill=col)
        cu = [(x0 + 15 + (k / 40) * (ww - 30), by(k / 40)) for k in range(41)]
        out += poly(cu, fill="none", stroke="#94a3b8", sw=2, closed=False)
        if kind == "small":
            ts = [0.10, 0.135, 0.165, 0.19, 0.21]
        elif kind == "good":
            ts = [0.10, 0.24, 0.37, 0.46, 0.5]
        else:
            ts = [0.12, 0.86, 0.07, 0.93, 0.03]
        for i, t in enumerate(ts):
            x = x0 + 15 + t * (ww - 30)
            out += circle(x, by(t), 6, fill=col, stroke=INK, sw=1)
            if i < len(ts) - 1:
                t2 = ts[i + 1]
                x2 = x0 + 15 + t2 * (ww - 30)
                out += line(x, by(t) - 8, x2, by(t2) - 8, stroke=col, w=1.2,
                            marker=("arrR" if col == RED else None))
        return out
    s += bowl(40, "замалий — повзе", "small", AMBER)
    s += bowl(360, "саме враз — сходить", "good", GREEN)
    s += bowl(680, "завеликий — розгойдує", "big", RED)
    s += rect(120, 360, 720, 56, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += text(480, 382,
              "Темп навчання (розмір кроку) — ключова ручка тренування: замалий гає час, завеликий руйнує спуск.",
              size=10.2, anchor="middle", weight="bold", fill=BLUE)
    s += text(480, 402,
              "Тому його підбирають — це «гіперпараметр», який задають ДО навчання.",
              size=9.3, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.4.4 — Цикл навчання
# ════════════════════════════════════════════════════════════════════════════
def fig_training_loop():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Цикл навчання: вперед → похибка → назад → крок",
               "прогнати вперед → виміряти похибку → зворотним поширенням порахувати градієнт для КОЖНОЇ ваги → ступити вниз → повторити (епохи)")
    boxes = [("1. ВПЕРЕД", "передбачити", BLUE),
             ("2. ПОХИБКА", "проти мітки", RED),
             ("3. НАЗАД", "зворотне поширення", AMBER),
             ("4. ОНОВИТИ", "крок ваг униз", GREEN)]
    xs = [40, 270, 500, 730]
    bw = 190
    for i, (t, d, col) in enumerate(boxes):
        x = xs[i]
        s += rect(x, 156, bw, 70, fill="#0f172a", stroke=col, sw=1.9, rx=9)
        s += text(x + bw / 2, 184, t, size=11, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + bw / 2, 205, d, size=8.6, anchor="middle", fill="#cbd5e1")
        if i < 3:
            s += line(x + bw, 191, x + bw + 14, 191, stroke=INK, w=1.8,
                      marker="arr")
    s += line(825, 228, 825, 262, stroke=INK, w=1.7)
    s += line(825, 262, 135, 262, stroke=INK, w=1.7)
    s += line(135, 262, 135, 230, stroke=INK, w=1.7, marker="arr")
    s += text(480, 256, "↻ повторювати по всіх прикладах багато разів (епохи)",
              size=9.5, anchor="middle", weight="bold", fill=MUTE)
    s += text(200, 312, "похибка з кожною епохою падає:", size=10,
              anchor="middle", weight="bold")
    ox, oy = 120, 412
    s += line(ox, oy, ox + 250, oy, stroke=INK, w=1.2, marker="arr")
    s += line(ox, oy, ox, oy - 90, stroke=INK, w=1.2, marker="arr")
    s += text(ox + 250, oy + 16, "епохи →", size=8, anchor="end", fill=MUTE)
    s += text(ox - 4, oy - 92, "похибка", size=8, anchor="end", fill=MUTE)
    lc = [(ox + k * 25, oy - 84 * math.exp(-k * 0.45)) for k in range(11)]
    s += poly(lc, fill="none", stroke=GREEN, sw=2.4, closed=False)
    s += rect(430, 320, 480, 104, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(670, 344, "Зворотне поширення — двигун кроку 3", size=10.5,
              anchor="middle", weight="bold")
    s += lines(452, 366,
               ["• воно ефективно рахує градієнт для КОЖНОЇ ваги —",
                "  пускаючи похибку НАЗАД крізь шари (Гінтон, 1986);",
                "• апарат цього НЕ робить: навчання — у хмарі (50.2),",
                "  на борт їде вже готова модель."], size=9, lh=17.5)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.5.1 — Чому звичайна мережа давиться
# ════════════════════════════════════════════════════════════════════════════
def fig_why_not_dense():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Чому звичайна мережа давиться зображенням",
               "повноз'єднана: КОЖЕН піксель тягне зв'язок до КОЖНОГО нейрона → мільйони ваг; та ще й не впізнає ту саму річ в іншому куті")
    s += rect(50, 108, 420, 300, fill="#fef2f2", stroke=RED, sw=1.8, rx=12)
    s += text(260, 132, "ВИБУХ ВАГ", size=11, anchor="middle", weight="bold",
              fill=RED)
    img = [170 + i * 22 for i in range(6)]
    neu = [168 + i * 30 for i in range(5)]
    for iy in img:
        for ny in neu:
            s += line(96, iy, 349, ny, stroke="#fca5a5", w=0.4)
    for iy in img:
        s += rect(80, iy - 8, 16, 16, fill="#94a3b8", stroke="none")
    for ny in neu:
        s += circle(360, ny, 11, fill="white", stroke=RED, sw=1.4)
    s += text(255, 300, "кожен піксель → кожен нейрон", size=9,
              anchor="middle", fill=MUTE)
    s += rect(86, 318, 348, 74, fill="white", stroke=RED, sw=1.3, rx=9)
    s += text(260, 340, "кадр 200×200×3 = 120 000 входів", size=9.5,
              anchor="middle", weight="bold")
    s += text(260, 359, "× 1000 нейронів = 120 000 000 ваг!", size=10.5,
              anchor="middle", weight="bold", fill=RED)
    s += text(260, 380, "один шар — і вже не влазить", size=8.5,
              anchor="middle", fill=MUTE)
    s += rect(510, 108, 400, 300, fill="#fffbeb", stroke=AMBER, sw=1.8, rx=12)
    s += text(710, 132, "НЕ ДІЛИТЬ ЗНАННЯ ЗА ПОЗИЦІЄЮ", size=10.5,
              anchor="middle", weight="bold", fill="#b06b00")
    s += rect(540, 156, 160, 110, fill="#1e293b", stroke=INK, sw=1.2)
    s += circle(576, 191, 14, fill="#f59e0b", stroke="none")
    s += rect(720, 156, 160, 110, fill="#1e293b", stroke=INK, sw=1.2)
    s += circle(844, 241, 14, fill="#f59e0b", stroke="none")
    s += text(710, 284, "той самий кіт — у різних кутах", size=9,
              anchor="middle", fill=MUTE)
    s += text(710, 304, "для повноз'єднаної це ДВА різні входи:", size=9,
              anchor="middle", fill="#b06b00", weight="bold")
    s += text(710, 320, "вона вчить кожну позицію наново", size=9,
              anchor="middle", fill=MUTE)
    s += text(710, 358, "→ марнує і ваги, і приклади", size=9.5,
              anchor="middle", fill="#b06b00", weight="bold")
    s += text(W / 2, H - 14,
              "Зображення ламають звичайну мережу: забагато зв'язків і жодного "
              "спільного знання між позиціями. Потрібен інший підхід.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.5.2 — Згортковий шар
# ════════════════════════════════════════════════════════════════════════════
def fig_conv_layer():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Згортковий шар: одне навчене ядро ковзає всюди",
               "замість зв'язку від кожного пікселя — мале ЯДРО (49.3) ковзає кадром (ті самі ваги скрізь) і будує мапу ознак")
    s += text(150, 116, "вхід (кадр)", size=9.5, anchor="middle",
              weight="bold")
    gx, gy, c = 70, 132, 26
    for r in range(6):
        for col in range(6):
            v = 150 if not (1 <= r <= 3 and 1 <= col <= 3) else 90
            s += rect(gx + col * c, gy + r * c, c, c, fill=f"rgb({v},{v},{v})",
                      stroke="#cbd5e1", sw=0.5)
    s += rect(gx + c, gy + c, 3 * c, 3 * c, fill="none", stroke=RED, sw=2.2)
    s += text(300, 200, "⊙", size=20, anchor="middle", weight="bold")
    s += text(345, 116, "ядро (вивчене)", size=9.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += _kernel3(322, 158, [["·", "·", "·"], ["·", "·", "·"], ["·", "·", "·"]],
                  BLUE, 30)
    s += text(450, 200, "=", size=20, anchor="middle", weight="bold")
    s += text(560, 116, "мапа ознак", size=9.5, anchor="middle", weight="bold")
    fx, fy, fc = 490, 150, 30
    for r in range(4):
        for col in range(4):
            hot = (r == 1 and col == 1)
            s += rect(fx + col * fc, fy + r * fc, fc, fc,
                      fill=("#22c55e" if hot else "#0f172a"),
                      stroke="#1e293b", sw=0.6)
    s += text(560, 286, "де ця ознака є (спалах)", size=8.5, anchor="middle",
              fill=MUTE)
    s += rect(640, 150, 280, 60, fill=BOX2, stroke=GREEN, sw=1.5, rx=9)
    s += text(780, 172, "СПІЛЬНІ ВАГИ", size=10, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(780, 192, "одне маленьке ядро на весь кадр → мало ваг", size=8.2,
              anchor="middle", fill=MUTE)
    s += rect(640, 222, 280, 60, fill=BOX1, stroke=BLUE, sw=1.5, rx=9)
    s += text(780, 244, "ІНВАРІАНТНІСТЬ ДО ЗСУВУ", size=10, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(780, 264, "ту саму ознаку знаходимо будь-де", size=8.2,
              anchor="middle", fill=MUTE)
    s += rect(120, 320, 720, 64, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 344, "Ключове: ядро тут — ВИВЧЕНЕ (градієнтним спуском, 50.4), а не рукотворне (Собель, 49.4).",
              size=10.2, anchor="middle", weight="bold")
    s += text(480, 366, "Мережа сама винаходить, які ознаки шукати — від простих країв до складних візерунків.",
              size=9.3, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 12,
              "Згортка в мережі = мале спільне ядро, що ковзає кадром. Звідси й "
              "мало ваг, і байдужість до позиції.", size=10.3, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.5.3 — Пулінг
# ════════════════════════════════════════════════════════════════════════════
def fig_pooling():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Пулінг: стиснути мапу й стерпіти зсув",
               "беремо максимум у кожному віконці (2×2) → мапа меншає вдвічі; дешевше, і дрібний зсув ознаки вже не збиває")
    grid = [[1, 0, 2, 3], [4, 6, 1, 2], [3, 1, 0, 5], [2, 2, 7, 1]]
    gx, gy, c = 150, 150, 56
    quad = ["#dbeafe", "#fde68a", "#bbf7d0", "#fecaca"]
    for r in range(4):
        for col in range(4):
            qi = (r // 2) * 2 + (col // 2)
            s += rect(gx + col * c, gy + r * c, c, c, fill=quad[qi],
                      stroke=INK, sw=0.8)
            s += text(gx + col * c + c / 2, gy + r * c + c * 0.64,
                      str(grid[r][col]), size=14, anchor="middle",
                      weight="bold")
    s += text(gx + 2 * c, 140, "мапа ознак 4×4", size=9.5, anchor="middle",
              weight="bold")
    s += line(gx + 4 * c + 14, gy + 2 * c, gx + 4 * c + 70, gy + 2 * c,
              stroke=INK, w=1.8, marker="arr")
    s += text(gx + 4 * c + 42, gy + 2 * c - 12, "макс", size=9,
              anchor="middle", weight="bold")
    s += text(gx + 4 * c + 42, gy + 2 * c + 24, "2×2", size=9, anchor="middle",
              fill=MUTE)
    ox = gx + 4 * c + 90
    res = [[6, 3], [3, 7]]
    for r in range(2):
        for col in range(2):
            qi = r * 2 + col
            s += rect(ox + col * c, gy + 28 + r * c, c, c, fill=quad[qi],
                      stroke=INK, sw=1.2)
            s += text(ox + col * c + c / 2, gy + 28 + r * c + c * 0.64,
                      str(res[r][col]), size=16, anchor="middle",
                      weight="bold", fill=RED)
    s += text(ox + c, 140, "→ 2×2 (максимум кожного)", size=9.5,
              anchor="middle", weight="bold")
    s += rect(120, 380, 720, 36, fill=BOX1, stroke=BLUE, sw=1.4, rx=9)
    s += text(480, 403,
              "+ менше даних (дешевше й швидше) · + стійкість: дрібний зсув ознаки в межах віконця нічого не міняє.",
              size=10, anchor="middle", weight="bold", fill=BLUE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.5.4 — Стос CNN
# ════════════════════════════════════════════════════════════════════════════
def fig_cnn_stack():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Стос CNN: від країв до об'єктів",
               "згортка → ReLU → пулінг, і так багато разів: мапи меншають і глибшають; перші шари — краї, глибші — об'єкти; наприкінці повноз'єднані → відповідь")
    stages = [("кадр", BLUE, 100, 3), ("згортка+ReLU\n+пулінг", AMBER, 80, 6),
              ("згортка\n+пулінг", AMBER, 56, 10), ("повноз'єднані", GREEN, 0, 0),
              ("вихід:\nклас / рамки", GREEN, 0, 0)]
    xs = [40, 230, 430, 620, 800]
    cy = 200
    for i, (t, col, sz, nmaps) in enumerate(stages):
        x = xs[i]
        if sz > 0:
            for k in range(min(nmaps, 6)):
                s += rect(x + k * 5, cy - sz / 2 + k * 3, sz, sz,
                          fill="#0f172a", stroke=col, sw=1.2, rx=4)
        else:
            s += rect(x, cy - 40, 120, 80, fill=PANEL, stroke=col, sw=1.7,
                      rx=8)
        cxp = x + (sz / 2 + 14 if sz > 0 else 60)
        for j, ln in enumerate(t.split("\n")):
            s += text(cxp, cy + 80 + j * 14, ln, size=8.8, anchor="middle",
                      weight="bold", fill=col)
        if i < 4:
            ax = x + (sz + 28 if sz > 0 else 120)
            s += line(ax, cy, xs[i + 1] - 6, cy, stroke=INK, w=1.6,
                      marker="arr")
    s += text(140, 150, "мапи меншають, та їх БІЛЬШЕ (глибше)", size=8.6,
              anchor="middle", fill=MUTE)
    s += rect(60, 320, 840, 98, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 344, "Ієрархія ознак: що глибше — то складніше", size=11,
              anchor="middle", weight="bold")
    hx = [200, 480, 760]
    hlab = [("перші шари", "КРАЇ, плями", BLUE),
            ("середні", "форми, частини", AMBER),
            ("глибокі", "цілі об'єкти", GREEN)]
    for i, (a, b, col) in enumerate(hlab):
        s += text(hx[i], 372, a, size=9.5, anchor="middle", weight="bold",
                  fill=col)
        s += text(hx[i], 390, b, size=9.5, anchor="middle")
        if i < 2:
            s += text((hx[i] + hx[i + 1]) / 2, 384, "→", size=14,
                      anchor="middle", weight="bold", fill=MUTE)
    s += text(480, 410,
              "Це і є детектор з 49.7, відкритий зсередини — рукотворна луна зорової кори (Г'юбел–Візел).",
              size=9, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.s5.1 — Мільйон почерків
# ════════════════════════════════════════════════════════════════════════════
def fig_lecun_handwriting():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Мільйон почерків: задача, де правила безсилі",
               "той самий «7» можна написати тисячею способів; жодне рукотворне правило їх не охопить — зате прикладів безліч")

    def seven(x, y, sl, cb, curve):
        w, h = 38, 56
        if curve:
            pts = [(x, y + 6), (x + w * 0.3, y - 4), (x + w * 0.7, y - 2),
                   (x + w, y + 2), (x + w * 0.45 + sl, y + h)]
        else:
            pts = [(x, y), (x + w, y), (x + w * 0.45 + sl, y + h)]
        out = poly(pts, fill="none", stroke=INK, sw=3, closed=False)
        if cb:
            out += line(x + w * 0.42 + sl * 0.5, y + h * 0.52,
                        x + w * 0.74 + sl * 0.5, y + h * 0.48, stroke=INK,
                        w=2.4)
        return out
    variants = [(110, -2, False, False), (230, 8, True, False),
                (350, 0, False, True), (470, 12, False, False),
                (590, -6, True, True), (710, 5, True, False),
                (820, 2, False, False)]
    for x, sl, cb, cu in variants:
        s += seven(x, 158, sl, cb, cu)
    s += text(W / 2, 252, "усе це — той самий «7»", size=11, anchor="middle",
              weight="bold")
    s += rect(120, 290, 720, 110, fill="#fef2f2", stroke=RED, sw=1.6, rx=11)
    s += text(480, 314, "Правило для «сімки» не напишеш", size=12,
              anchor="middle", weight="bold", fill=RED)
    s += lines(150, 338,
               ["• нахил, петельки, риска посередині, кривий верх — варіантів безліч, і кожен почерк інший;",
                "• зате ПРИКЛАДІВ — гори: мільйони підписаних конвертів і чеків. Класична задача для машинного навчання (50.1):",
                "  не формалізувати правило, а показати приклади й НАВЧИТИ модель."], size=9.6, lh=21)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.s5.2 — Бракована ланка
# ════════════════════════════════════════════════════════════════════════════
def fig_lecun_missing_piece():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Бракована ланка: навчити згортку",
               "неокогнітрон (50.5) мав форму, та не вмів добре вчитися; Лекун додав зворотне поширення (50.4) і реальні дані — і згортка ОЖИЛА")
    s += rect(40, 130, 250, 190, fill=PANEL, stroke=AMBER, sw=1.8, rx=12)
    s += text(165, 156, "Неокогнітрон (1980)", size=11, anchor="middle",
              weight="bold", fill="#b06b00")
    s += lines(60, 184, ["+ форма правильна:", "  згортка + пулінг (50.5)",
                         "− та вчити НЕ вміли", "  як слід", "  (без зручного навчання)"],
               size=9.6, lh=24)
    s += text(312, 230, "+", size=26, anchor="middle", weight="bold",
              fill=MUTE)
    s += rect(335, 130, 250, 190, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(460, 156, "Внесок Лекуна (1989)", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(355, 184, ["+ зворотне поширення", "  (50.4) тренує ядра",
                          "+ спільні ваги (49.3)", "+ реальні дані пошти",
                          "  (індекси з конвертів)"], size=9.6, lh=24)
    s += text(607, 230, "=", size=26, anchor="middle", weight="bold",
              fill=MUTE)
    s += rect(630, 130, 290, 190, fill=BOX2, stroke=GREEN, sw=2, rx=12)
    s += text(775, 156, "Навчена згорткова мережа", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(650, 184, ["• сама вчить ядра з прикладів", "  (не рукотворні, не випадкові);",
                          "• працює на СПРАВЖНІХ,", "  неохайних почерках;",
                          "• перша CNN, що по-справжньому", "  запрацювала."], size=9.4, lh=20)
    s += text(W / 2, 358,
              "Архітектуру дав Фукусіма; Лекун додав те, чого бракувало, — спосіб НАВЧАТИ її на реальних даних.",
              size=10.5, anchor="middle", weight="bold")
    s += text(W / 2, 380,
              "Так згорткова мережа вперше перетворилася з гарної ідеї на робочий інструмент.",
              size=9.6, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.s5.3 — LeNet читає цифру
# ════════════════════════════════════════════════════════════════════════════
def fig_lenet_pipeline():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "LeNet читає цифру",
               "вхідний образ → згортки й пулінги → відповідь «це 7» з упевненістю; перша згорткова мережа, що працювала по-справжньому")
    s += rect(60, 150, 110, 130, fill="#0f172a", stroke=INK, sw=1.3)
    s += poly([(88, 178), (140, 178), (104, 256)], fill="none", stroke="white",
              sw=5, closed=False)
    s += line(98, 216, 124, 213, stroke="white", w=4)
    s += text(115, 300, "вхід: образ цифри", size=9, anchor="middle",
              fill=MUTE)
    s += line(174, 215, 210, 215, stroke=INK, w=1.7, marker="arr")
    stages = [(220, 84, 4), (330, 64, 8), (440, 44, 12)]
    for x, sz, n in stages:
        for k in range(min(n, 5)):
            s += rect(x + k * 5, 215 - sz / 2 + k * 3, sz, sz, fill="#1e293b",
                      stroke=AMBER, sw=1.1, rx=3)
    s += text(360, 300, "згортки + пулінги (50.5)", size=9, anchor="middle",
              fill=MUTE)
    s += line(515, 215, 551, 215, stroke=INK, w=1.7, marker="arr")
    s += rect(556, 165, 80, 100, fill=PANEL, stroke=GREEN, sw=1.6, rx=8)
    s += text(596, 200, "повно-", size=9, anchor="middle")
    s += text(596, 214, "з'єднані", size=9, anchor="middle")
    s += line(640, 215, 676, 215, stroke=INK, w=1.7, marker="arr")
    s += text(800, 150, "вихід: 10 цифр", size=9.5, anchor="middle",
              weight="bold")
    bx, by = 686, 268
    vals = [0.01, 0.0, 0.02, 0.01, 0.0, 0.0, 0.01, 0.98, 0.01, 0.0]
    for d in range(10):
        h = vals[d] * 90
        col = GREEN if d == 7 else "#cbd5e1"
        s += rect(bx + d * 21, by - h, 15, h, fill=col, stroke="none")
        s += text(bx + d * 21 + 7, by + 13, str(d), size=8, anchor="middle",
                  fill=("#15803d" if d == 7 else MUTE),
                  weight=("bold" if d == 7 else "normal"))
    s += text(bx + 7 * 21 + 7, by - 100, "«7» 0.98", size=10, anchor="middle",
              fill="#15803d", weight="bold")
    s += text(W / 2, H - 14,
              "Та сама архітектура, що в 49.7 ловить людей і авто, вперше навчилася читати рукописну цифру.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.s5.4 — Тихий тріумф
# ════════════════════════════════════════════════════════════════════════════
def fig_lecun_production():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Тихий тріумф у роки «зими»: пошта й чеки",
               "задовго до AlexNet, у самісіньку «зиму ШІ», CNN Лекуна щодня читала поштові індекси й банківські чеки")
    s += rect(70, 120, 380, 150, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(260, 146, "ПОШТА: індекси на конвертах", size=11,
              anchor="middle", weight="bold", fill=BLUE)
    s += lines(94, 174, ["• сортування листів за рукописним",
                         "  поштовим індексом (US Postal);",
                         "• перша реальна робота нейромережі,",
                         "  навченої зворотним поширенням (1989)."], size=9.5,
               lh=22)
    s += rect(510, 120, 380, 150, fill=BOX2, stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 146, "БАНКИ: суми на чеках", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(534, 174, ["• читання рукописних сум на чеках",
                          "  у банкоматах і банках (LeNet);",
                          "• за словами Лекуна, наприкінці 1990-х —",
                          "  чимала частка всіх чеків у США."], size=9.5, lh=22)
    s += rect(70, 296, 820, 56, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += line(110, 324, 850, 324, stroke=INK, w=1.5, marker="arr")
    for x, lab in [(150, "1989\nіндекси"), (340, "1998\nLeNet-5"),
                   (560, "роки «зими»"), (820, "2012\nAlexNet")]:
        s += circle(x, 324, 5, fill=(GREEN if "2012" not in lab else AMBER),
                    stroke=INK, sw=1)
        for j, ln in enumerate(lab.split("\n")):
            s += text(x, 316 + j * 11 - (8 if len(lab.split(chr(10))) > 1 else 0),
                      ln, size=7.6, anchor="middle", fill=MUTE)
    s += text(480, 378,
              "CNN заробляла на життя ще за 20+ років до тріумфу AlexNet — тихо, у роки, коли в нейромережі мало хто вірив.",
              size=10, anchor="middle", weight="bold")
    s += text(480, 400,
              "А набір рукописних цифр MNIST Лекуна став головною «лінійкою» машинного навчання на десятиліття.",
              size=9.3, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 12,
              "Детектор, що нині на твоєму дроні впізнає ціль, — прямий нащадок цього скромного читача поштових індексів.",
              size=10, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.6.1 — Три підгонки
# ════════════════════════════════════════════════════════════════════════════
def fig_overfit_underfit():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Узагальнення проти зубріння: три підгонки",
               "недонавчання — модель надто проста (мимо суті); добра підгонка — ловить тренд; перенавчання — зазубрює кожну точку (й шум)")
    data = [(0.07, 0.30), (0.18, 0.48), (0.30, 0.38), (0.42, 0.62),
            (0.54, 0.52), (0.66, 0.74), (0.78, 0.66), (0.90, 0.86)]

    def panel(x0, lab, kind, col, note):
        out = rect(x0, 116, 270, 232, fill="#fbfbfd", stroke=col, sw=1.8, rx=12)
        out += text(x0 + 135, 138, lab, size=11, anchor="middle",
                    weight="bold", fill=col)
        px, py, pw, ph = x0 + 32, 322, 206, 150
        out += line(px, py, px + pw, py, stroke="#cbd5e1", w=1)
        out += line(px, py, px, py - ph, stroke="#cbd5e1", w=1)
        if kind == "under":
            out += line(px, py - 0.40 * ph, px + pw, py - 0.66 * ph, stroke=col,
                        w=2.8)
        elif kind == "good":
            cu = [(px + t * pw, py - (0.32 + 0.5 * t + 0.05 *
                   math.sin(t * 6)) * ph) for t in [i / 30 for i in range(31)]]
            out += poly(cu, fill="none", stroke=col, sw=2.8, closed=False)
        else:
            out += poly([(px + dx * pw, py - dy * ph) for dx, dy in data],
                        fill="none", stroke=col, sw=2.4, closed=False)
        for dx, dy in data:
            out += circle(px + dx * pw, py - dy * ph, 4, fill="#1e293b",
                          stroke="white", sw=1)
        out += text(x0 + 135, 340, note, size=9, anchor="middle", fill=MUTE)
        return out
    s += panel(40, "НЕДОНАВЧАННЯ", "under", AMBER, "надто просто — мимо суті")
    s += panel(345, "ДОБРА ПІДГОНКА", "good", GREEN, "ловить закономірність")
    s += panel(650, "ПЕРЕНАВЧАННЯ", "over", RED, "зазубрило точки й шум")
    s += text(W / 2, H - 14,
              "Мета — не пройти крізь кожну точку, а вловити ЗАКОНОМІРНІСТЬ, щоб "
              "правильно відповісти на НОВЕ.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.6.2 — Зубрити чи розуміти
# ════════════════════════════════════════════════════════════════════════════
def fig_memorize_vs_learn():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Зубрить чи розуміє: симптом перенавчання",
               "перенавчена модель — мов учень, що завчив відповіді минулих іспитів: блискуче на баченому, провал на новому")
    s += rect(60, 116, 400, 250, fill="#fbfbfd", stroke=INK, sw=1.6, rx=12)
    s += text(260, 142, "точність перенавченої моделі", size=11,
              anchor="middle", weight="bold")
    base = 330
    s += line(110, base, 430, base, stroke=INK, w=1.2)
    s += rect(150, base - 170, 70, 170, fill=GREEN, stroke=INK, sw=1, rx=4,
              opacity=0.85)
    s += text(185, base - 178, "99%", size=12, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(185, base + 16, "на ТРЕНУВАЛЬНИХ", size=8.6, anchor="middle",
              weight="bold")
    s += text(185, base + 30, "(бачене)", size=8, anchor="middle", fill=MUTE)
    s += rect(320, base - 104, 70, 104, fill=RED, stroke=INK, sw=1, rx=4,
              opacity=0.8)
    s += text(355, base - 112, "60%", size=12, anchor="middle", weight="bold",
              fill=RED)
    s += text(355, base + 16, "на НОВИХ", size=8.6, anchor="middle",
              weight="bold")
    s += text(355, base + 30, "(небачене)", size=8, anchor="middle", fill=MUTE)
    s += line(225, base - 150, 315, base - 84, stroke=RED, w=1.4, dash="4,3")
    s += text(272, base - 128, "РОЗРИВ", size=9, anchor="middle", fill=RED,
              weight="bold")
    s += rect(500, 116, 400, 250, fill=PANEL, stroke=BLUE, sw=1.6, rx=12)
    s += text(700, 142, "як учень перед іспитом", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(524, 174, ["• ЗАВЧИВ відповіді минулих білетів",
                          "  → блищить на тих самих питаннях,",
                          "  але плаває на нових;",
                          "• РОЗУМІЄ предмет",
                          "  → відповість і на небачене."], size=10, lh=26)
    s += rect(524, 312, 352, 40, fill=BOX2, stroke=GREEN, sw=1.4, rx=8)
    s += text(700, 337, "велика різниця «бачене ↔ нове» = перенавчання",
              size=10, anchor="middle", weight="bold", fill="#15803d")
    s += text(W / 2, H - 14,
              "Висока точність на тренувальних даних нічого не варта сама по "
              "собі — важить лише точність на НОВОМУ.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.6.3 — Train / val / test
# ════════════════════════════════════════════════════════════════════════════
def fig_train_val_test():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Як чесно виміряти: тренувальний / валідаційний / тестовий",
               "на тренувальному вчаться; на валідаційному підбирають налаштування й ловлять перенавчання; тестовий чіпають РАЗ")
    parts = [("ТРЕНУВАЛЬНИЙ", 0.66, BLUE, "на ньому модель ВЧИТЬСЯ (50.4)"),
             ("ВАЛІДА-\nЦІЙНИЙ", 0.17, AMBER, "тут підбирають налаштування й ловлять перенавчання"),
             ("ТЕСТОВИЙ", 0.17, GREEN, "чіпають РАЗ наприкінці — чесна оцінка")]
    x = 70
    for lab, frac, col, role in parts:
        w = frac * 820
        s += rect(x, 116, w, 44, fill=col, stroke=INK, sw=1.2, rx=6,
                  opacity=0.85)
        ly = 132 if "\n" not in lab else 128
        for j, ln in enumerate(lab.split("\n")):
            s += text(x + w / 2, ly + j * 12, ln, size=9.5, anchor="middle",
                      weight="bold", fill="white")
        s += text(x + w / 2, 178, role, size=7.8, anchor="middle", fill=MUTE)
        x += w
    s += rect(70, 196, 820, 30, fill="#fde2e2", stroke=RED, sw=1.4, rx=8)
    s += text(480, 216,
              "ЗОЛОТЕ ПРАВИЛО: НІКОЛИ не оцінюй на тих даних, на яких училася модель — інакше міряєш зубріння, а не вміння.",
              size=9.6, anchor="middle", weight="bold", fill=RED)
    ox, oy = 150, 410
    s += line(ox, oy, ox + 360, oy, stroke=INK, w=1.3, marker="arr")
    s += line(ox, oy, ox, oy - 130, stroke=INK, w=1.3, marker="arr")
    s += text(ox + 360, oy + 16, "епохи →", size=8.5, anchor="end", fill=MUTE)
    s += text(ox - 6, oy - 132, "похибка", size=8.5, anchor="end", fill=MUTE)
    tr = [(ox + k * 33, oy - 12 - 110 * math.exp(-k * 0.5)) for k in range(11)]
    s += poly(tr, fill="none", stroke=BLUE, sw=2.4, closed=False)
    s += text(ox + 350, tr[-1][1] - 6, "тренувальна ↓", size=8.5, anchor="end",
              fill=BLUE, weight="bold")
    vl = [(ox + k * 33, oy - 40 - 70 * math.exp(-k * 0.6) + max(0, k - 4) * 9)
          for k in range(11)]
    s += poly(vl, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(ox + 350, vl[-1][1] + 2, "валідаційна", size=8.5, anchor="end",
              fill=RED, weight="bold")
    kmin = min(range(11), key=lambda k: vl[k][1])
    s += circle(vl[kmin][0], vl[kmin][1], 6, fill="none", stroke=GREEN, sw=2.2)
    s += text(vl[kmin][0], vl[kmin][1] - 14, "рання зупинка", size=8,
              anchor="middle", fill="#15803d", weight="bold")
    s += rect(560, 290, 340, 120, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(730, 314, "Що каже розрив кривих", size=10.5, anchor="middle",
              weight="bold")
    s += lines(580, 336,
               ["• тренувальна похибка все падає (модель",
                "  зубрить дедалі краще);",
                "• валідаційна спершу падає, тоді РОСТЕ —",
                "  ось і почалося перенавчання;",
                "• спинись там, де валідаційна найменша."],
               size=8.8, lh=15.5)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.6.4 — Ліки й дані-цар
# ════════════════════════════════════════════════════════════════════════════
def fig_cures():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Ліки від перенавчання — і головне правило",
               "більше різноманітних даних, простіша модель, регуляризація/dropout, аугментація, рання зупинка")
    cures = [("більше ДАНИХ", "найсильніші ліки (50.1)", GREEN),
             ("простіша модель", "менше параметрів — менше що зубрити", BLUE),
             ("dropout / регуляризація", "глушити зайву складність", AMBER),
             ("аугментація", "відбити / обрізати / підсвітити → більше прикладів", BLUE),
             ("рання зупинка", "спинись на мінімумі валідації (50.6.3)", GREEN)]
    for i, (t, d, col) in enumerate(cures):
        y = 120 + i * 46
        s += rect(50, y, 470, 40, fill=PANEL, stroke=col, sw=1.5, rx=8)
        s += circle(72, y + 20, 6, fill=col, stroke="none")
        s += text(90, y + 18, t, size=10.5, weight="bold", fill=col)
        s += text(90, y + 32, d, size=8.4, fill=MUTE)
    s += text(720, 138, "аугментація: один кадр → багато", size=9.5,
              anchor="middle", weight="bold")
    labs = ["оригінал", "відбито", "темніше", "обрізано"]
    for k in range(4):
        x = 560 + (k % 2) * 170
        yy = 156 + (k // 2) * 90
        s += rect(x, yy, 150, 72, fill="#1e293b", stroke=INK, sw=1)
        s += circle(x + 55 + (k == 1) * 40, yy + 36, 16,
                    fill=("#5a6472" if k == 2 else "#f59e0b"), stroke="none")
        if k == 3:
            s += rect(x, yy, 150, 72, fill="none", stroke=GREEN, sw=2,
                      dash="4,3")
        s += text(x + 75, yy + 86, labs[k], size=8, anchor="middle", fill=MUTE)
    s += rect(50, 392, 850, 50, fill="#fffbeb", stroke=AMBER, sw=1.6, rx=10)
    s += text(480, 414,
              "ДАНІ — ЦАР: представницькі, РІЗНОМАНІТНІ приклади важать понад усе (50.1).",
              size=11, anchor="middle", weight="bold", fill="#92400e")
    s += text(480, 432,
              "Для дрона — знімай і вдень, і вночі, і в різних місцях: інакше модель «бачитиме» лише свою лабораторію.",
              size=9.4, anchor="middle", fill="#92400e")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.7.1 — Прірва
# ════════════════════════════════════════════════════════════════════════════
def fig_gap():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Прірва: велика модель — крихітний пристрій",
               "навчена модель — мільйони ваг, мегабайти, важкі обчислення; мікроконтролер — кілобайти, мегагерци, мілівати")
    s += rect(60, 130, 330, 230, fill="#fef2f2", stroke=RED, sw=1.9, rx=12)
    s += text(225, 158, "НАВЧЕНА МОДЕЛЬ", size=12, anchor="middle",
              weight="bold", fill=RED)
    s += lines(92, 192, ["• мільйони параметрів", "• десятки МБ (ваги float32)",
                         "• важкий вивід", "  (мільйони множень)"], size=10.5,
               lh=30)
    s += text(225, 332, "завелика, щоб улізти", size=9.5, anchor="middle",
              fill=MUTE, italic=True)
    s += poly([(482, 130), (468, 172), (496, 210), (466, 252), (492, 300),
               (476, 360)], fill="none", stroke="#cbd5e1", sw=2.4,
              closed=False)
    s += text(480, 170, "не", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += text(480, 186, "влазить!", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += text(480, 268, "→ СТИСНУТИ", size=10, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(480, 283, "модель", size=10, anchor="middle", weight="bold",
              fill=BLUE)
    s += rect(570, 130, 330, 230, fill="#fffbeb", stroke=AMBER, sw=1.9, rx=12)
    s += text(735, 158, "МІКРОКОНТРОЛЕР", size=12, anchor="middle",
              weight="bold", fill="#b06b00")
    s += lines(602, 192, ["• кілобайти RAM", "• мегагерци",
                          "• мілівати", "• часто без підтримки float"], size=10.5,
               lh=30)
    s += text(735, 332, "усе крихітне (49.9)", size=9.5, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Між навченою моделлю й бортовим чипом — прірва в тисячі разів. "
              "TinyML наводить через неї міст.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.7.2 — Квантування
# ════════════════════════════════════════════════════════════════════════════
def fig_quantization():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Квантування: 32-бітні ваги → 8-бітні",
               "замість точного 32-бітного дробу зберігаємо вагу 8 бітами (256 рівнів): вчетверо менше, швидше, точність майже не страждає")
    s += rect(60, 128, 300, 92, fill="#fef2f2", stroke=RED, sw=1.5, rx=10)
    s += text(210, 152, "32-бітний float", size=10.5, anchor="middle",
              weight="bold", fill=RED)
    s += text(210, 182, "0.31428571…", size=15, anchor="middle", weight="bold")
    s += text(210, 204, "4 байти на число", size=8.5, anchor="middle",
              fill=MUTE)
    s += line(364, 174, 420, 174, stroke=INK, w=1.8, marker="arr")
    s += text(392, 164, "округлити", size=8, anchor="middle", fill=MUTE)
    s += text(392, 188, "до рівня", size=8, anchor="middle", fill=MUTE)
    s += rect(426, 128, 300, 92, fill="#eafaef", stroke=GREEN, sw=1.5, rx=10)
    s += text(576, 152, "8-бітне ціле", size=10.5, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(576, 182, "80  (з 0…255)", size=15, anchor="middle",
              weight="bold")
    s += text(576, 204, "1 байт на число", size=8.5, anchor="middle",
              fill=MUTE)
    s += text(770, 158, "= вчетверо", size=11, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(770, 176, "менше", size=11, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(W / 2, 250,
              "діапазон ваг ділять на 256 рівнів; кожну вагу «клацають» у найближчий:",
              size=9.5, anchor="middle", fill=MUTE)
    rx, ry, rw = 120, 290, 720
    s += line(rx, ry, rx + rw, ry, stroke=INK, w=1.4)
    for k in range(33):
        x = rx + k * (rw / 32)
        s += line(x, ry - 5, x, ry + 5, stroke="#94a3b8", w=1)
    fxv = rx + rw * 0.31
    s += line(fxv, ry - 22, fxv, ry, stroke=RED, w=1.6)
    s += text(fxv, ry - 28, "0.314…", size=8, anchor="middle", fill=RED)
    sxv = rx + rw * 0.3125
    s += circle(sxv, ry, 5, fill=GREEN, stroke=INK, sw=1)
    s += text(sxv + 60, ry + 20, "найближчий рівень", size=8, anchor="middle",
              fill="#15803d")
    s += rect(120, 322, 720, 58, fill=BOX1, stroke=BLUE, sw=1.4, rx=10)
    s += lines(150, 344,
               ["• ×4 менше (8 біт замість 32) → менше пам'яті й місця на чипі;",
                "• швидше: цілочисельна арифметика (МК часто й не має float-блоку), а точність падає ледь-ледь."],
               size=9.4, lh=18)
    s += text(W / 2, H - 14,
              "Та сама ідея, що в JPEG (48.2): згрубити дрібниці, яких не "
              "помітно, заради величезного виграшу в розмірі.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.7.3 — Скриня прийомів
# ════════════════════════════════════════════════════════════════════════════
def fig_shrink_toolbox():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Скриня прийомів: як ужати модель",
               "квантування (8 біт), менша архітектура (MobileNet), прорідження (викинути зайві ваги), дистиляція (учень копіює вчителя)")
    cards = [("КВАНТУВАННЯ", ["32→8 біт: ×4 менше,", "швидше (50.7.2)"], GREEN, "q"),
             ("МЕНША АРХІТЕКТУРА", ["MobileNet тощо:", "менше й дешевше шарів"], BLUE, "a"),
             ("ПРОРІДЖЕННЯ", ["викинути ваги ≈0 (їх", "багато) → рідша, менша"], AMBER, "p"),
             ("ДИСТИЛЯЦІЯ", ["малий «учень» копіює", "велике «вчителя»"], RED, "d")]
    for i, (t, rows, col, kind) in enumerate(cards):
        x = 50 + (i % 2) * 460
        y = 116 + (i // 2) * 138
        s += rect(x, y, 430, 120, fill=PANEL, stroke=col, sw=1.8, rx=12)
        s += text(x + 22, y + 32, t, size=12, weight="bold", fill=col)
        s += text(x + 22, y + 60, rows[0], size=10)
        s += text(x + 22, y + 80, rows[1], size=10)
        vx, vy = x + 330, y + 60
        if kind == "q":
            s += rect(vx, vy - 36, 16, 48, fill=RED, stroke="none")
            s += rect(vx + 40, vy - 4, 16, 16, fill=GREEN, stroke="none")
        elif kind == "a":
            for k in range(3):
                s += rect(vx + k * 16, vy - 20 - k * 4, 12, 40 + k * 8,
                          fill=BLUE, stroke="none", opacity=0.5)
        elif kind == "p":
            for r in range(3):
                for c in range(3):
                    on = not ((r + c) % 2 == 0 and r != c)
                    s += rect(vx + c * 16, vy - 24 + r * 16, 12, 12,
                              fill=(AMBER if on else "#e5e7eb"), stroke="none")
        else:
            s += circle(vx, vy - 6, 18, fill="none", stroke=RED, sw=2)
            s += line(vx + 20, vy - 6, vx + 38, vy - 6, stroke=INK, w=1.5,
                      marker="arr")
            s += circle(vx + 54, vy - 6, 9, fill="none", stroke=GREEN, sw=2)
    s += rect(50, 396, 850, 46, fill="#fffbeb", stroke=AMBER, sw=1.5, rx=10)
    s += text(480, 416,
              "Їх СКЛАДАЮТЬ разом: квантована, проріджена MobileNet після дистиляції влазить навіть у мікроконтролер,",
              size=9.6, anchor="middle", weight="bold", fill="#92400e")
    s += text(480, 432, "віддаючи лише дрібку точності за величезний виграш у розмірі й швидкості.",
              size=9.2, anchor="middle", fill="#92400e")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.7.4 — Конвеєр TinyML
# ════════════════════════════════════════════════════════════════════════════
def fig_tinyml_pipeline():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Конвеєр TinyML: від хмари до мікроконтролера",
               "натренувати (хмара, float32) → конвертувати й квантувати (TFLite Micro) → розгорнути крихітну модель на МК → вивід за мілівати")
    st = [("ХМАРА", ["навчити модель", "(float32, 50.2)"], AMBER),
          ("КОНВЕРТУВАТИ", ["+ квантувати", "(TFLite Micro)"], BLUE),
          ("МК / edge", ["крихітна модель,", "вивід за мВт"], GREEN)]
    xs = [70, 380, 690]
    for i, (t, rows, col) in enumerate(st):
        x = xs[i]
        s += rect(x, 130, 200, 92, fill=PANEL, stroke=col, sw=1.9, rx=11)
        s += text(x + 100, 158, t, size=12, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 100, 182, rows[0], size=9.3, anchor="middle")
        s += text(x + 100, 200, rows[1], size=9.3, anchor="middle", fill=MUTE)
        if i < 2:
            s += line(x + 200, 176, x + 308, 176, stroke=INK, w=2,
                      marker="arr")
    s += text(W / 2, 268, "що вже бігає на крихітних чипах:", size=10.5,
              anchor="middle", weight="bold")
    ex = [("слово-команда", "«прокинься»"), ("жест руки", "вгору / вниз"),
          ("простий детектор", "є людина / нема")]
    for i, (a, b) in enumerate(ex):
        x = 90 + i * 270
        s += rect(x, 286, 230, 60, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
        s += text(x + 115, 310, a, size=10, anchor="middle", weight="bold",
                  fill="#15803d")
        s += text(x + 115, 330, b, size=8.6, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 30,
              "TinyML несе машинне навчання навіть на найдрібніші чипи — за мілівати, без хмари й мережі.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "А де саме рахувати — на МК, бортовому комп'ютері чи в хмарі — "
              "розважимо в наступній темі (50.8).", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.8.1 — Три місця
# ════════════════════════════════════════════════════════════════════════════
def fig_three_places():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Три місця для обчислень",
               "МК на польотному контролері (крихітний, миттєвий); бортовий комп'ютер (потужний); хмара (безмежна, та з лагом і потрібен зв'язок)")
    tiers = [("МК (контролер)", RED, ["КБ · МГц · мВт", "миттєво, на борту",
                                      "TinyML (50.7): слово,", "жест, класифікація"]),
             ("БОРТОВИЙ КОМП'ЮТЕР", AMBER, ["ГБ · GPU / прискорювач",
                                            "низький лаг, на борту",
                                            "справжні CNN (49.7):", "детектор, трекінг"]),
             ("ХМАРА / ЗЕМЛЯ", BLUE, ["безмежна потужність", "та 100+ мс мережі",
                                      "потрібен зв'язок (48.6)", "важке, навчання"])]
    for i, (t, col, rows) in enumerate(tiers):
        x = 50 + i * 300
        s += rect(x, 118, 280, 208, fill=PANEL, stroke=col, sw=1.9, rx=12)
        s += rect(x, 118, 280, 36, fill=col, stroke="none", rx=10, opacity=0.15)
        s += text(x + 140, 141, t, size=11, anchor="middle", weight="bold",
                  fill=col)
        s += lines(x + 24, 180, rows, size=9.6, lh=26)
        if i < 2:
            s += text(x + 290, 222, "→", size=22, anchor="middle",
                      weight="bold", fill=MUTE)
    s += line(80, 372, 880, 372, stroke=INK, w=1.4)
    s += text(110, 392, "більше потужності →", size=10, fill=BLUE,
              weight="bold")
    s += text(850, 392, "← менший лаг, ← автономність", size=10, anchor="end",
              fill="#15803d", weight="bold")
    s += text(W / 2, 414,
              "що далі від апарата — то більше потужності, але більший лаг і менша автономність",
              size=10, anchor="middle", weight="bold")
    s += text(W / 2, H - 14,
              "Немає «найкращого» місця — є придатне під задачу. Ближче до "
              "апарата — швидше й автономніше, та слабше.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.8.2 — Що з чим торгуємо
# ════════════════════════════════════════════════════════════════════════════
def fig_tradeoff_axes():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Що з чим торгуємо",
               "потужність росте від МК до хмари — та разом росте затримка й падає автономність; вага й приватність теж важать")
    cols = [("МК", 430, RED), ("БОРТОВИЙ", 610, AMBER), ("ХМАРА", 790, BLUE)]
    for name, cx, col in cols:
        s += rect(cx - 80, 110, 160, 32, fill=PANEL, stroke=col, sw=1.3, rx=6)
        s += text(cx, 131, name, size=11, anchor="middle", weight="bold",
                  fill=col)
    rows = [("потужність", "мала", "велика", "безмежна", [RED, AMBER, GREEN]),
            ("затримка", "миттєва", "низька (мс)", "мережева (100+ мс)",
             [GREEN, GREEN, RED]),
            ("автономність", "повна", "повна", "лише зі зв'язком",
             [GREEN, GREEN, RED]),
            ("вага / енергія", "дрібка", "вати + грами", "поза бортом",
             [GREEN, AMBER, GREEN]),
            ("приватність", "на борту", "на борту", "дані йдуть геть",
             [GREEN, GREEN, RED])]
    y = 152
    for crit, a, b, c, cc in rows:
        s += text(70, y + 24, crit, size=10.5, weight="bold")
        for val, col, (name, cx, _) in zip([a, b, c], cc, cols):
            s += rect(cx - 80, y, 160, 40, fill=("#eafaef" if col == GREEN else
                      ("#fff5e6" if col == AMBER else "#fde2e2")),
                      stroke="#e5e7eb", sw=1, rx=6)
            s += text(cx, y + 25, val, size=9.2, anchor="middle", fill=col,
                      weight="bold")
        y += 48
    s += text(W / 2, H - 14,
              "Що далі від апарата — то потужніше, та дорожче за латентністю й "
              "автономністю. Обирай під вимоги задачі.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.8.3 — Золоте правило
# ════════════════════════════════════════════════════════════════════════════
def fig_golden_rule_compute():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Золоте правило розподілу",
               "критичне за часом і керування — НА БОРТУ (ніколи в хмарі); важке й не термінове — у хмару; обірваний зв'язок не сміє завалити апарат")
    s += rect(360, 116, 240, 58, fill=PANEL, stroke=INK, sw=1.6, rx=10)
    s += text(480, 140, "Критично за ЧАСОМ", size=11, anchor="middle",
              weight="bold")
    s += text(480, 159, "чи для керування?", size=11, anchor="middle",
              weight="bold")
    s += line(424, 174, 304, 210, stroke=GREEN, w=1.8, marker="arrG")
    s += text(338, 196, "ТАК", size=10, fill="#15803d", weight="bold")
    s += rect(106, 214, 300, 96, fill=BOX2, stroke=GREEN, sw=1.8, rx=11)
    s += text(256, 238, "→ НА БОРТУ", size=12, anchor="middle", weight="bold",
              fill="#15803d")
    s += lines(126, 260, ["• МК — для дрібного й керування",
                          "• бортовий комп'ютер — для важкого зору",
                          "• миттєво, без мережі, автономно"], size=9.2, lh=17)
    s += line(536, 174, 656, 210, stroke=BLUE, w=1.8, marker="arrB")
    s += text(626, 196, "НІ", size=10, fill=BLUE, weight="bold")
    s += rect(554, 214, 300, 96, fill=BOX1, stroke=BLUE, sw=1.8, rx=11)
    s += text(704, 238, "→ МОЖНА В ХМАРУ", size=12, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(574, 260, ["• навчання моделей (50.2)",
                          "• важкий аналіз, побудова карт",
                          "• логи, не термінове — офлайн"], size=9.2, lh=17)
    s += rect(90, 332, 780, 80, fill="#fef2f2", stroke=RED, sw=1.9, rx=11)
    s += text(480, 358, "СМЕРТНИЙ ГРІХ: контур керування через хмару", size=12,
              anchor="middle", weight="bold", fill=RED)
    s += lines(132, 380,
               ["зник зв'язок (вийшов з покриття, завада — 48.6) — і апарат лишається БЕЗ керування й падає.",
                "Усе, від чого залежить політ, мусить рахуватися НА БОРТУ й працювати навіть без мережі."],
               size=9.4, lh=18)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.8.4 — Гібрид на практиці
# ════════════════════════════════════════════════════════════════════════════
def fig_hybrid_drone():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Гібрид на практиці: кожній задачі — свій рівень",
               "польотний контролер (МК): керування + TinyML; бортовий комп'ютер: зір у реальному часі → MAVLink; хмара: навчання й аналіз")
    s += rect(50, 114, 590, 286, fill="#f0fdf4", stroke=GREEN, sw=1.7, rx=12)
    s += text(345, 136, "НА БОРТУ (реальний час, без мережі)", size=10.5,
              anchor="middle", weight="bold", fill="#15803d")
    s += rect(78, 156, 250, 118, fill=BOX3, stroke=AMBER, sw=1.7, rx=10)
    s += text(203, 180, "ПОЛЬОТНИЙ КОНТРОЛЕР (МК)", size=9.4, anchor="middle",
              weight="bold", fill="#b06b00")
    s += lines(96, 204, ["• керування, стабілізація",
                         "• завжди-ввімкнений TinyML", "  (слово, жест) — 50.7"],
               size=9, lh=19)
    s += rect(362, 156, 250, 118, fill=BOX1, stroke=BLUE, sw=1.7, rx=10)
    s += text(487, 180, "БОРТОВИЙ КОМП'ЮТЕР", size=9.4, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(380, 204, ["• детектор / трекінг у", "  реальному часі (49.7)",
                          "• кут → MAVLink контролеру"], size=9, lh=19)
    s += line(362, 256, 330, 256, stroke=INK, w=1.8, marker="arr")
    s += text(345, 300, "кут (MAVLink, 49.8)", size=7.6, anchor="middle",
              fill=BLUE, weight="bold")
    s += text(345, 384, "усе, від чого залежить політ — тут; працює й без зв'язку",
              size=8.6, anchor="middle", fill=MUTE)
    s += rect(686, 168, 224, 150, fill=PANEL, stroke=MUTE, sw=1.7, rx=12,
              dash="6,4")
    s += text(798, 192, "ХМАРА / ЗЕМЛЯ", size=10.5, anchor="middle",
              weight="bold")
    s += text(798, 208, "(поза польотним контуром)", size=7.6, anchor="middle",
              fill=MUTE)
    s += lines(704, 230, ["• навчання моделей (50.2)", "• аналіз логів і відео",
                          "• побудова карт", "— не термінове, офлайн"],
               size=8.8, lh=18)
    s += line(642, 240, 682, 240, stroke=MUTE, w=1.6, dash="5,4", marker="arr")
    s += text(662, 230, "коли є", size=7, anchor="middle", fill=MUTE)
    s += text(662, 256, "зв'язок", size=7, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Розклади задачі по рівнях: миттєве й критичне — на борту; важке й "
              "не термінове — у хмару. Так робить і дрон, і марсохід.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.9.1 — Чесні межі
# ════════════════════════════════════════════════════════════════════════════
def fig_limits():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чесні межі: що машинне навчання НЕ вміє",
               "це зіставлення взірців, а не РОЗУМІННЯ; воно крихке поза баченим, зв'язане даними й без жодних гарантій")
    cards = [("НЕ РОЗУМІЄ", RED, ["зіставляє взірці, а не осягає",
                                  "сенс; ні здорового глузду,", "ні «навіщо» (50.1, 49.7)"]),
             ("КРИХКЕ", AMBER, ["поза тренуванням хибить і",
                                "ВПЕВНЕНО бреше (Розумний", "Ганс, підказки — 50.6)"]),
             ("ЗВ'ЯЗАНЕ ДАНИМИ", BLUE, ["не краще за свої приклади;",
                                        "справді нове чи рідкісне", "не подужає (50.1)"]),
             ("БЕЗ ГАРАНТІЙ", RED, ["імовірнісне, «чорна скриня»:",
                                    "нема доказу правильності,", "важко знати ЧОМУ (49.7)"])]
    for i, (t, col, rows) in enumerate(cards):
        x = 50 + (i % 2) * 460
        y = 116 + (i // 2) * 150
        s += rect(x, y, 430, 130, fill=PANEL, stroke=col, sw=1.8, rx=12)
        s += text(x + 22, y + 34, t, size=12.5, weight="bold", fill=col)
        s += lines(x + 22, y + 62, rows, size=9.6, lh=22)
    s += text(W / 2, H - 14,
              "Це потужний інструмент із чіткими межами — не розум і не магія. "
              "Знати межі — частина вміння ним користуватись.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.9.2 — Етика
# ════════════════════════════════════════════════════════════════════════════
def fig_ethics():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Етика: відповідальність за зрячий апарат",
               "упередженість даних, приватність (дрон = стеження), безпека (упевнено-хибна модель + літальний апарат), подвійне призначення")
    cards = [("УПЕРЕДЖЕНІСТЬ", AMBER, ["перекошені дані → несправед-",
                                       "лива чи небезпечна модель;", "збирай чесно (50.6)"]),
             ("ПРИВАТНІСТЬ", BLUE, ["зрячий дрон — потужне", "стеження; поважай право",
                                    "людей і закон"]),
             ("БЕЗПЕКА", RED, ["упевнено-хибна модель керує",
                               "польотом → запобіжники,", "людський нагляд, фолбек"]),
             ("ПОДВІЙНЕ ПРИЗНАЧЕННЯ", GREEN, ["те саме — на добро (порятунок,",
                                              "агро, огляд) чи на зло;", "вибір за інженером"])]
    for i, (t, col, rows) in enumerate(cards):
        x = 50 + (i % 2) * 460
        y = 116 + (i // 2) * 150
        s += rect(x, y, 430, 130, fill=PANEL, stroke=col, sw=1.8, rx=12)
        s += text(x + 22, y + 34, t, size=12, weight="bold", fill=col)
        s += lines(x + 22, y + 62, rows, size=9.6, lh=22)
    s += text(W / 2, H - 14,
              "Дати апарату очі — велика сила. Відповідальність за те, що він "
              "ними робить, лежить на тобі, а не на моделі.", size=10.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.9.3 — Практичні кроки
# ════════════════════════════════════════════════════════════════════════════
def fig_practical_steps():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Практичні кроки: як почати",
               "класика перед нейромережею; готова модель + донавчання; добрі різноманітні дані + чесна перевірка; запобіжники; ітеруй")
    steps = [("1", "Найдешевший метод спершу", "класика (поріг, Хаф — 49.6) перед нейромережею", GREEN),
             ("2", "Готова модель + перенесення", "бери натреновану й донавчи під себе; не з нуля", BLUE),
             ("3", "Добрі різноманітні дані", "+ чесний тестовий набір (50.6); знімай в усіх умовах", AMBER),
             ("4", "Запобіжники й аварійні режими", "ML не керує польотом сама; нагляд людини, фолбек", RED),
             ("5", "Простий → виміряй → покращ", "ітеруй малими кроками; стеж за бюджетом (49.9, 50.7)", BLUE)]
    for i, (n, t, d, col) in enumerate(steps):
        y = 114 + i * 48
        s += circle(82, y + 18, 15, fill=col, stroke=INK, sw=1.3)
        s += text(82, y + 23, n, size=13, anchor="middle", weight="bold",
                  fill="white")
        s += text(112, y + 13, t, size=10.5, weight="bold", fill=col)
        s += text(112, y + 31, d, size=9, fill=MUTE)
    s += rect(50, 372, 860, 48, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(480, 391, "інструменти, з якими це роблять:", size=9.5,
              anchor="middle", weight="bold")
    s += text(480, 409,
              "OpenCV (класика) · TensorFlow / PyTorch + TFLite (ML) · ArduPilot + MAVLink (інтеграція) · Raspberry Pi / Jetson (залізо)",
              size=8.8, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 50.9.4 — Підсумок Модуля 7
# ════════════════════════════════════════════════════════════════════════════
def fig_module_recap():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Куди ти прийшов: весь Модуль 7",
               "від сирого кадру до навченої моделі, що бачить, розуміє й діє на апараті — відповідально")
    stages = [("ВІДЕО", "Розділи 47–48", ["зняти кадр (сенсор)",
               "→ стиснути (DCT, кодеки)", "→ доправити (радіо/мережа)"], BLUE),
              ("ЗОР", "Розділ 49", ["піксель → межі → об'єкти",
               "→ детектор (класика/нейро)", "→ трекінг → керування"], AMBER),
              ("НАВЧАННЯ", "Розділ 50", ["вчитися з даних → тренувати",
               "→ CNN → стиснути (TinyML)", "→ запустити на пристрої"], GREEN)]
    for i, (t, sub, rows, col) in enumerate(stages):
        x = 50 + i * 300
        s += rect(x, 116, 280, 178, fill=PANEL, stroke=col, sw=1.9, rx=12)
        s += rect(x, 116, 280, 42, fill=col, stroke="none", rx=10, opacity=0.16)
        s += text(x + 140, 137, t, size=13, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 140, 151, sub, size=8, anchor="middle", fill=MUTE)
        s += lines(x + 20, 186, rows, size=9.3, lh=24)
        if i < 2:
            s += text(x + 290, 205, "→", size=22, anchor="middle",
                      weight="bold", fill=MUTE)
    s += rect(80, 318, 800, 78, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(480, 346, "Машина навчилася БАЧИТИ, РОЗУМІТИ й ДІЯТИ", size=13,
              anchor="middle", weight="bold", fill="#15803d")
    s += text(480, 372,
              "від світла на сенсорі — до рішення, що замикає керування апаратом. Тепер — користуйся цим мудро.",
              size=9.6, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Це й була мета Модуля 7: дати апарату очі — і розум, щоб ними "
              "скористатися.", size=10.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-50-0-1-ai-winters.svg": fig_ai_winters,
    "fig-50-0-2-hinton-persistence.svg": fig_hinton_persistence,
    "fig-50-0-3-why-winters.svg": fig_why_winters,
    "fig-50-0-4-roadmap.svg":   fig_roadmap_ml,
    "fig-50-1-1-rules-vs-data.svg": fig_rules_vs_data,
    "fig-50-1-2-where-rules-fail.svg": fig_where_rules_fail,
    "fig-50-1-3-three-kinds.svg": fig_three_kinds,
    "fig-50-1-4-data-is-heart.svg": fig_data_is_heart,
    "fig-50-2-1-two-phases.svg": fig_two_phases,
    "fig-50-2-2-whats-flowing.svg": fig_whats_flowing,
    "fig-50-2-3-asymmetry-cost.svg": fig_asymmetry_cost,
    "fig-50-2-4-on-drone.svg":  fig_on_drone,
    "fig-50-3-1-neuron.svg":    fig_neuron,
    "fig-50-3-2-weights-bias.svg": fig_weights_bias,
    "fig-50-3-3-activation.svg": fig_activation,
    "fig-50-3-4-layers.svg":    fig_layers,
    "fig-50-4-1-loss.svg":      fig_loss,
    "fig-50-4-2-gradient-descent.svg": fig_gradient_descent,
    "fig-50-4-3-learning-rate.svg": fig_learning_rate,
    "fig-50-4-4-training-loop.svg": fig_training_loop,
    "fig-50-5-1-why-not-dense.svg": fig_why_not_dense,
    "fig-50-5-2-conv-layer.svg": fig_conv_layer,
    "fig-50-5-3-pooling.svg":   fig_pooling,
    "fig-50-5-4-cnn-stack.svg": fig_cnn_stack,
    "fig-50-s5-1-handwriting.svg": fig_lecun_handwriting,
    "fig-50-s5-2-missing-piece.svg": fig_lecun_missing_piece,
    "fig-50-s5-3-lenet.svg":    fig_lenet_pipeline,
    "fig-50-s5-4-production.svg": fig_lecun_production,
    "fig-50-6-1-overfit-underfit.svg": fig_overfit_underfit,
    "fig-50-6-2-memorize-vs-learn.svg": fig_memorize_vs_learn,
    "fig-50-6-3-train-val-test.svg": fig_train_val_test,
    "fig-50-6-4-cures.svg":     fig_cures,
    "fig-50-7-1-gap.svg":       fig_gap,
    "fig-50-7-2-quantization.svg": fig_quantization,
    "fig-50-7-3-shrink-toolbox.svg": fig_shrink_toolbox,
    "fig-50-7-4-tinyml-pipeline.svg": fig_tinyml_pipeline,
    "fig-50-8-1-three-places.svg": fig_three_places,
    "fig-50-8-2-tradeoff-axes.svg": fig_tradeoff_axes,
    "fig-50-8-3-golden-rule.svg": fig_golden_rule_compute,
    "fig-50-8-4-hybrid-drone.svg": fig_hybrid_drone,
    "fig-50-9-1-limits.svg":    fig_limits,
    "fig-50-9-2-ethics.svg":    fig_ethics,
    "fig-50-9-3-practical-steps.svg": fig_practical_steps,
    "fig-50-9-4-module-recap.svg": fig_module_recap,
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
