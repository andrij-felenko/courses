#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 44 (Модуль 7) — чистий Python, без залежностей.
Запуск:  python figs.py    →    кладе *.svg у ./img/

Стиль (єдиний для курсу; спільні допоміжні функції копіюються у кожен chNN/figs.py):
  білий фон; «+» червоний, «−» синій; поле — зелене; стрілки через marker;
  шрифт sans-serif. Підписи фігур у тексті — посекційно «Рис. C.S.N».
"""

import os
import math
import random

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


def sat(cx, cy, s=1.0, col=INK):
    """Маленький супутник: корпус + дві панелі."""
    o = rect(cx - 9 * s, cy - 7 * s, 18 * s, 14 * s, fill="white", stroke=col,
             sw=1.4, rx=3)
    o += rect(cx - 26 * s, cy - 5 * s, 13 * s, 10 * s, fill=BOX1, stroke=col,
              sw=1.2, rx=2)
    o += rect(cx + 13 * s, cy - 5 * s, 13 * s, 10 * s, fill=BOX1, stroke=col,
              sw=1.2, rx=2)
    return o


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.0.1 — Інверсія: від Доплера супутника до твоєї позиції
# ════════════════════════════════════════════════════════════════════════════
def fig_inversion():
    W, H = 940, 470
    s = header(W, H)
    s += title(W, "Осяяння 1957 року: переверни задачу — і супутник скаже, де ТИ",
               "відома точка + Доплер → орбіта супутника;  переверни — і відома орбіта + Доплер → твоя точка")

    def panel(px, head, known_sat, hi):
        o = rect(px, 78, 410, 300, fill="white", stroke=INK, sw=1.4, rx=12)
        o += text(px + 205, 72, head, size=12.5, weight="bold", anchor="middle")
        # Земля (дуга внизу)
        o += f'<path d="M {px+20} 360 Q {px+205} 300 {px+390} 360" fill="{GND}" stroke="{GREEN}" stroke-width="1.6"/>\n'
        # супутник на дузі орбіти
        ox, oy = px + 250, 150
        o += f'<path d="M {px+40} 200 Q {px+250} 90 {px+380} 210" fill="none" stroke="{MUTE}" stroke-width="1.2" stroke-dasharray="5,4"/>\n'
        o += sat(ox, oy, 1.0, BLUE if known_sat else AMBER)
        o += text(ox, oy - 26, "супутник", size=10.5, anchor="middle",
                  fill=BLUE if known_sat else AMBER, weight="bold")
        o += text(ox, oy - 12, "(орбіта відома)" if known_sat else "(орбіта відома)",
                  size=9, anchor="middle", fill=MUTE)
        # станція/приймач на землі
        sx, sy = px + 120, 330
        o += circle(sx, sy, 7, fill=AMBER if not known_sat else GREEN,
                    stroke=INK, sw=1.4)
        o += text(sx, sy + 22, "станція (відома)" if known_sat else "ТИ (невідомо!)",
                  size=10.5, anchor="middle",
                  fill=GREEN if known_sat else RED, weight="bold")
        # промінь супутник→станція з доплерівськими хвилями
        o += line(ox, oy + 10, sx + 4, sy - 8, stroke=INK, w=1.4)
        # хвилі (стиснуті/розтягнуті)
        for k, rr in enumerate([16, 28, 44, 64]):
            o += circle(ox, oy, rr, fill="none", stroke=BLUE, sw=1.0,
                        opacity=0.5)
        o += text(px + 205, hi, "Доплер: тон вищий → нижчий", size=10.5,
                  anchor="middle", fill=BLUE, italic=True)
        return o

    s += panel(40, "ПРЯМА задача (що вміли)", True, 366)
    s += panel(490, "ОБЕРНЕНА задача (ідея!)", False, 366)
    # стрілка-переворот між панелями
    s += text(470, 200, "⇄", size=30, anchor="middle", fill=RED, weight="bold")
    s += text(470, 226, "переверни", size=10, anchor="middle", fill=RED)

    s += text(W / 2, H - 14,
              "Учені APL вистежили «біп» Супутника за Доплером — і зрозуміли: якщо орбіту "
              "знати наперед, той самий Доплер видасть невідому позицію приймача. Так народилась супутникова навігація.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.0.2 — Трилатерація в часі: чому потрібні 4 супутники
# ════════════════════════════════════════════════════════════════════════════
def fig_trilateration():
    W, H = 940, 500
    s = header(W, H)
    s += title(W, "Як працює GPS: не карта, а годинник — трилатерація в часі",
               "відстань = швидкість світла × час польоту сигналу; перетин сфер дає точку")

    cxr, cyr = 360, 285   # приймач
    sats = [(150, 150, "S1"), (560, 130, "S2"), (300, 440, "S3")]
    cols = [BLUE, GREEN, AMBER]
    for (sxp, syp, nm), col in zip(sats, cols):
        d = math.hypot(cxr - sxp, cyr - syp)
        s += circle(sxp, syp, d, fill="none", stroke=col, sw=1.3, opacity=0.55,
                    dash="6,5")
        s += sat(sxp, syp, 0.95, col)
        s += text(sxp, syp - 24, nm, size=11, anchor="middle", weight="bold",
                  fill=col)
        # промінь до приймача з підписом відстані
        mx, my = (sxp + cxr) / 2, (syp + cyr) / 2
        s += line(sxp, syp, cxr, cyr, stroke=col, w=1.0, opacity=0.6)
        s += text(mx, my - 4, "c·t", size=10, fill=col, weight="bold")

    s += circle(cxr, cyr, 8, fill=RED, stroke=INK, sw=1.6)
    s += text(cxr, cyr + 24, "приймач (ТИ)", size=11.5, anchor="middle",
              weight="bold", fill=RED)

    # пояснювальна панель праворуч
    s += rect(640, 96, 280, 230, fill=PANEL, stroke=INK, sw=1.4, rx=11)
    s += lines(656, 124, [
        "Кожен супутник шле:",
        "«я ТУТ, і зараз час T».",
        "",
        "Приймач міряє запізнення",
        "сигналу → відстань c·t →",
        "сфера навколо супутника.",
        "",
        "Перетин сфер = позиція.",
    ], size=11.5, lh=22)

    s += rect(640, 338, 280, 120, fill=BOX3, stroke=AMBER, sw=1.5, rx=11)
    s += text(780, 364, "Чому 4, а не 3?", size=12.5, weight="bold",
              anchor="middle", fill=AMBER)
    s += lines(656, 386, [
        "3 сфери дають x, y, z.",
        "Але годинник приймача —",
        "дешевий, не атомний.",
        "4-й супутник розв'язує ще",
        "й похибку його годинника.",
    ], size=11, lh=15)

    s += text(W / 2, H - 12,
              "GPS міряє не відстань лінійкою, а ЧАС — тому все тримається на "
              "неймовірно точних годинниках.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.0.3 — Релятивістська поправка: чому годинники налаштовують повільніше
# ════════════════════════════════════════════════════════════════════════════
def fig_relativity():
    W, H = 940, 480
    s = header(W, H)
    s += title(W, "Без Ейнштейна GPS брехав би на ~10 км щодоби",
               "годинник на орбіті йде інакше; поправку зашито в систему")

    # Земля
    s += circle(180, 300, 90, fill=SKY, stroke=BLUE, sw=1.6)
    s += text(180, 305, "Земля", size=12, anchor="middle", weight="bold",
              fill=BLUE)
    # орбіта + супутник
    s += circle(180, 300, 200, fill="none", stroke=MUTE, sw=1.0, dash="5,5")
    s += sat(180, 100, 1.1, INK)
    s += text(180, 70, "GPS-супутник", size=11, anchor="middle", weight="bold")
    s += text(180, 132, "висота ~20 000 км · ~14 000 км/год", size=9.5,
              anchor="middle", fill=MUTE)

    # два ефекти
    s += rect(430, 90, 470, 70, fill="#fff0f0", stroke=RED, sw=1.6, rx=11)
    s += text(450, 116, "Загальна відносність (висота, слабша гравітація):",
              size=12, weight="bold", fill=RED)
    s += text(450, 140, "годинник ПРИСКОРЮЄТЬСЯ    →   +45 мкс/добу", size=12,
              family="Consolas, monospace", fill=INK)

    s += rect(430, 176, 470, 70, fill="#eff4ff", stroke=BLUE, sw=1.6, rx=11)
    s += text(450, 202, "Спеціальна відносність (велика швидкість):", size=12,
              weight="bold", fill=BLUE)
    s += text(450, 226, "годинник СПОВІЛЬНЮЄТЬСЯ  →   −7 мкс/добу", size=12,
              family="Consolas, monospace", fill=INK)

    s += rect(430, 262, 470, 56, fill=PANEL, stroke=INK, sw=1.7, rx=11)
    s += text(665, 296, "Разом:  +45 − 7  =  +38 мкс/добу", size=14,
              anchor="middle", weight="bold", family="Consolas, monospace")

    s += rect(430, 334, 470, 60, fill="#fff5e6", stroke=AMBER, sw=1.7, rx=11)
    s += text(665, 358, "Без поправки: ~10 км помилки ЩОДОБИ", size=12.5,
              anchor="middle", weight="bold", fill=AMBER)
    s += text(665, 380, "(хибно вже за 2 хв)", size=11, anchor="middle",
              fill=INK)

    s += rect(60, 410, 840, 44, fill=BOX2, stroke=GREEN, sw=1.6, rx=11)
    s += text(480, 437,
              "Рішення: годинник супутника НАВМИСНО налаштовують іти повільніше ще на Землі "
              "(10.229 999 995 43 МГц замість 10.23 МГц) — на орбіті він піде «правильно».",
              size=11.5, anchor="middle", weight="bold", fill=INK)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.0.4 — Selective Availability: мить, коли GPS став точним (2000)
# ════════════════════════════════════════════════════════════════════════════
def fig_sa():
    W, H = 940, 460
    s = header(W, H)
    s += title(W, "1 травня 2000: мить, коли GPS став точним для всіх",
               "військові навмисно «загрублювали» цивільний сигнал; його вимкнули — і точність стрибнула вдесятеро")

    def target(px, head, spread, col, note):
        cx, cy = px + 175, 250
        o = rect(px, 80, 350, 330, fill="white", stroke=INK, sw=1.4, rx=12)
        o += text(px + 175, 74, head, size=12.5, weight="bold", anchor="middle")
        for rr, lab in [(120, ""), (80, ""), (40, "")]:
            o += circle(cx, cy, rr, fill="none", stroke=MUTE, sw=1.0,
                        opacity=0.5)
        # хрест — справжня позиція
        o += line(cx - 14, cy, cx + 14, cy, stroke=GREEN, w=1.6)
        o += line(cx, cy - 14, cx, cy + 14, stroke=GREEN, w=1.6)
        # точки вимірів
        for _ in range(34):
            a = random.uniform(0, 2 * math.pi)
            r = abs(random.gauss(0, spread))
            o += circle(cx + r * math.cos(a), cy + r * math.sin(a), 2.6,
                        fill=col, stroke="none")
        o += text(px + 175, 392, note, size=11, anchor="middle", fill=col,
                  weight="bold")
        return o

    random.seed(7)
    s += target(40, "SA увімкнено (до)", 46, RED, "розкид ~100 м")
    s += target(550, "SA вимкнено (після)", 9, GREEN, "розкид ~10–20 м")
    s += text(470, 250, "→", size=34, anchor="middle", fill=INK, weight="bold")

    s += text(W / 2, H - 12,
              "Саме після цього GPS став достатньо точним для автомобілів, телефонів — і дронів "
              "із «поверненням додому». Зелений хрест — справжня позиція.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.1.1 — Сенсорний набір апарата (карта чуттів)
# ════════════════════════════════════════════════════════════════════════════
def fig_suite():
    W, H = 960, 520
    s = header(W, H)
    s += title(W, "Чуття апарата: який давач що міряє",
               "кожен меряє ОДНУ фізичну величину — частково й неідеально")

    # апарат у центрі (квадрокоптер згори)
    cx, cy = 480, 270
    arms = [(-58, -58), (58, -58), (-58, 58), (58, 58)]
    for dx, dy in arms:
        s += line(cx, cy, cx + dx, cy + dy, stroke=INK, w=3.0)
        s += circle(cx + dx, cy + dy, 13, fill=PANEL, stroke=INK, sw=1.5)
    s += circle(cx, cy, 22, fill="#e3effb", stroke=INK, sw=1.7)
    s += text(cx, cy + 4, "апарат", size=10.5, anchor="middle", weight="bold")

    boxes = [
        (40, 78, "IMU (гіро + акселерометр)", "прискорення, кутова швидкість",
         BLUE, (cx - 50, cy - 40)),
        (680, 78, "Магнітометр", "поле Землі → курс (північ)", GREEN,
         (cx + 50, cy - 40)),
        (40, 248, "Барометр", "тиск повітря → висота", AMBER, (cx - 60, cy)),
        (680, 248, "GNSS-приймач", "положення, швидкість (з неба)", BLUE,
         (cx + 60, cy)),
        (360, 438, "Давач живлення", "напруга, струм → заряд", RED,
         (cx, cy + 50)),
    ]
    for bx, by, nm, what, col, (ax, ay) in boxes:
        s += line(bx + 120 if bx < 400 else (bx + 120), by + 39, ax, ay,
                  stroke=MUTE, w=1.2, dash="4,3")
        s += rect(bx, by, 240, 78, fill="white", stroke=col, sw=1.7, rx=11)
        s += text(bx + 120, by + 32, nm, size=12.5, weight="bold",
                  anchor="middle", fill=col)
        s += text(bx + 120, by + 56, what, size=11, anchor="middle", fill=INK)

    s += text(W / 2, H - 14,
              "Жоден давач сам не дає «стану» апарата — їх зливають разом (Розділ 43). "
              "Тут — лише хто що відчуває.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.1.2 — Який давач що оцінює (давач → стан)
# ════════════════════════════════════════════════════════════════════════════
def fig_state():
    W, H = 960, 500
    s = header(W, H)
    s += title(W, "Який давач у що вкладається: кожна частина стану — з кількох джерел",
               "саме тому потрібен фьюжн: одна величина підпирається кількома давачами")
    sensors = [(110, "IMU", BLUE), (190, "Магнітометр", GREEN),
               (270, "Барометр", AMBER), (350, "GNSS", BLUE),
               (430, "Давач живлення", RED)]
    states = [(110, "Орієнтація (крен/тангаж/курс)"), (190, "Висота"),
              (270, "Положення"), (350, "Швидкість"), (430, "Енергія / здоров'я")]
    sx, swid = 70, 250
    tx, twid = 640, 250
    for y, nm, col in sensors:
        s += rect(sx, y - 26, swid, 52, fill="white", stroke=col, sw=1.6, rx=10)
        s += text(sx + swid / 2, y + 5, nm, size=12.5, weight="bold",
                  anchor="middle", fill=col)
    for y, nm in states:
        s += rect(tx, y - 26, twid, 52, fill=PANEL, stroke=INK, sw=1.5, rx=10)
        s += text(tx + twid / 2, y + 5, nm, size=12, weight="bold",
                  anchor="middle")
    links = [(0, 0, BLUE), (0, 2, BLUE), (0, 3, BLUE),     # IMU
             (1, 0, GREEN),                                 # маг → орієнтація
             (2, 1, AMBER),                                 # баро → висота
             (3, 1, BLUE), (3, 2, BLUE), (3, 3, BLUE),      # GNSS
             (4, 4, RED)]                                   # живлення
    for si, ti, col in links:
        y1 = sensors[si][0]
        y2 = states[ti][0]
        s += line(sx + swid, y1, tx, y2, stroke=col, w=1.4, opacity=0.65)

    s += text(W / 2, H - 14,
              "Орієнтація, висота й положення живляться кількома давачами одразу — "
              "звідси й сила фьюжну: давачі підстраховують одне одного.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.1.3 — Абсолютні проти відносних давачів
# ════════════════════════════════════════════════════════════════════════════
def fig_absrel():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Глибока вісь: відносні (швидкі, дрейфують) проти абсолютних (стабільні, повільні)",
               "фьюжн бере швидкість одних і стабільність інших")
    # графік
    s += rect(50, 88, 540, 300, fill="white", stroke=INK, sw=1.3, rx=10)
    s += line(70, 380, 575, 380, stroke=MUTE, w=1.2, marker="arr")
    s += text(575, 374, "час", size=10, anchor="end", fill=MUTE)
    yt = 250
    s += line(70, yt, 568, yt, stroke=GREEN, w=1.3, dash="6,4")
    s += text(74, yt - 6, "істинне значення", size=10, fill=GREEN)
    # відносний (дрейфує вгору)
    rel = [(76, 250), (150, 245), (220, 234), (300, 214), (380, 186),
           (460, 154), (566, 120)]
    s += poly(rel, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(500, 110, "відносний → дрейф", size=10.5, fill=RED, weight="bold")
    # абсолютний (шумний навколо істини)
    random.seed(11)
    for x in range(90, 560, 30):
        s += circle(x, yt + random.uniform(-26, 26), 3, fill=BLUE, stroke="none")
    s += text(140, 330, "абсолютний → шум, але без дрейфу", size=10.5,
              fill=BLUE, weight="bold")
    # злитий
    fus = [(76, 250), (160, 249), (260, 251), (360, 249), (460, 250), (566, 250)]
    s += poly(fus, fill="none", stroke=GREEN, sw=2.6, closed=False)
    s += text(300, 238, "фьюжн → і швидко, і без дрейфу", size=10.5, fill=GREEN,
              weight="bold")

    # категорії праворуч
    s += rect(620, 100, 300, 84, fill="#fff0f0", stroke=RED, sw=1.6, rx=11)
    s += text(770, 126, "ВІДНОСНІ", size=13, weight="bold", anchor="middle",
              fill=RED)
    s += text(770, 148, "швидкі, але дрейфують", size=11, anchor="middle")
    s += text(770, 170, "IMU · барометр", size=11.5, anchor="middle",
              weight="bold", family="Consolas, monospace")
    s += rect(620, 200, 300, 84, fill="#eff4ff", stroke=BLUE, sw=1.6, rx=11)
    s += text(770, 226, "АБСОЛЮТНІ", size=13, weight="bold", anchor="middle",
              fill=BLUE)
    s += text(770, 248, "стабільні, але повільні/шумні", size=11,
              anchor="middle")
    s += text(770, 270, "GNSS · магнітометр", size=11.5, anchor="middle",
              weight="bold", family="Consolas, monospace")
    s += rect(620, 300, 300, 70, fill=BOX2, stroke=GREEN, sw=1.7, rx=11)
    s += text(770, 326, "ФЬЮЖН (Розділ 43/46)", size=12.5, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(770, 348, "найкраще з обох світів", size=11, anchor="middle")

    s += text(W / 2, H - 12,
              "Це — головний принцип усього бортового відчуття: швидке, що пливе, "
              "тримають повільним, що не пливе.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.1.4 — Довідкова таблиця давачів
# ════════════════════════════════════════════════════════════════════════════
def fig_table():
    W, H = 980, 500
    s = header(W, H)
    s += title(W, "Давачі апарата: що міряє, у чому сильний, у чому слабкий",
               "довідкова карта — її ланки ми розкриємо в наступних темах")
    cols = [(30, 175, "Давач"), (205, 250, "Міряє"),
            (455, 250, "Сила"), (705, 245, "Слабкість")]
    for x, w, h_ in cols:
        s += rect(x, 78, w, 34, fill=INK, stroke=INK, rx=7)
        s += text(x + 12, 101, h_, size=12, fill="white", weight="bold")
    rows = [
        ("IMU (гіро + акс)", "прискорення, кут. швидкість", "швидкий, завжди є",
         "кут спливає (інтеграл)", BLUE),
        ("Магнітометр", "напрям поля Землі", "абсолютний курс",
         "плутає залізо/струми", GREEN),
        ("Барометр", "тиск повітря", "швидка висота",
         "дрейф із погодою/вітром", AMBER),
        ("GNSS-приймач", "положення, швидкість", "прив'язка до Землі",
         "повільний, треба небо", BLUE),
        ("Давач живлення", "напруга, струм", "заряд і потужність",
         "не навігація — виживання", RED),
        ("Додаткові", "пітот · далекомір · опт. потік", "вузькі задачі точно",
         "за потреби, не завжди є", MUTE),
    ]
    y = 112
    rh = 58
    for nm, meas, strg, weak, col in rows:
        s += rect(30, y, 175, rh, fill="white", stroke=col, sw=1.3)
        s += text(42, y + 34, nm, size=11.5, weight="bold", fill=col)
        s += rect(205, y, 250, rh, fill="#fafafa", stroke=MUTE, sw=1.0)
        s += text(217, y + 34, meas, size=11, fill=INK)
        s += rect(455, y, 250, rh, fill="#f3fbf5", stroke=MUTE, sw=1.0)
        s += text(467, y + 34, strg, size=11, fill=INK)
        s += rect(705, y, 245, rh, fill="#fff5f5", stroke=MUTE, sw=1.0)
        s += text(717, y + 34, weak, size=11, fill=INK)
        y += rh
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.2.1 — Акселерометр міряє «питому силу», а не прискорення тіла
# ════════════════════════════════════════════════════════════════════════════
def fig_specificforce():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Підступність акселерометра: він міряє «питому силу», а не рух",
               "у спокої бачить g (звідси нахил), у вільному падінні — нуль")

    def sensor(cx, cy, arrow_dy, label):
        o = rect(cx - 34, cy - 34, 68, 68, fill="white", stroke=INK, sw=1.6,
                 rx=8)
        # підвіс + пробна маса
        o += line(cx, cy - 34, cx, cy - 12, stroke=MUTE, w=1.2)
        o += line(cx, cy + 12, cx, cy + 34, stroke=MUTE, w=1.2)
        o += circle(cx, cy, 11, fill=PANEL, stroke=INK, sw=1.4)
        return o

    panels = [
        (160, "У спокої на столі", -1, "+1 g", "опора штовхає вгору → читає g"),
        (480, "У вільному падінні", 0, "0", "нічого не тисне → читає нуль"),
        (800, "Нахилений (спокій)", -1, "проєкції g", "звідси абсолютний крен/тангаж"),
    ]
    for cx, head, sign, rd, sub in panels:
        cy = 175
        s += text(cx, 90, head, size=12.5, weight="bold", anchor="middle")
        if head.startswith("Нахилений"):
            s += f'<g transform="rotate(22 {cx} {cy})">\n'
            s += sensor(cx, cy, sign, rd)
            s += '</g>\n'
            # стрілка g вниз + проєкція
            s += line(cx, cy - 50, cx, cy + 56, stroke=GREEN, w=1.4, dash="3,3")
            s += line(cx, cy, cx + 30, cy + 30, stroke=RED, w=2.4, marker="arrR")
        else:
            s += sensor(cx, cy, sign, rd)
            if sign != 0:
                s += line(cx, cy - 6, cx, cy - 70, stroke=RED, w=2.6,
                          marker="arrR")
            else:
                s += circle(cx, cy - 50, 5, fill=RED, stroke="none")
        # підлога/стіл
        if head.startswith("У спокої"):
            s += line(cx - 50, cy + 38, cx + 50, cy + 38, stroke=INK, w=2.2)
        s += text(cx, cy + 70, "читає: " + rd, size=12, anchor="middle",
                  weight="bold", fill=RED)
        s += text(cx, cy + 90, sub, size=10.5, anchor="middle", fill=MUTE)

    s += rect(60, 360, 840, 64, fill=BOX3, stroke=AMBER, sw=1.5, rx=11)
    s += lines(80, 384, [
        "Акселерометр міряє «питому силу» — НЕ прискорення тіла. У спокої він «бачить» вектор g і дає абсолютний нахил.",
        "Але під час РОЗГОНУ прискорення домішується до g, і нахил уже не відрізнити від руху — тому потрібен гіроскоп і фьюжн.",
    ], size=11.5, lh=20)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.2.2 — Гравітація дає крен і тангаж, але не курс → потрібен компас
# ════════════════════════════════════════════════════════════════════════════
def fig_yaw():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому самого IMU мало для курсу: гравітація «не бачить» yaw",
               "нахил (крен/тангаж) міняє проєкцію g — поворот навколо вертикалі ні")

    # Панель A: крен/тангаж (вид збоку)
    s += rect(40, 80, 280, 300, fill="white", stroke=INK, sw=1.3, rx=11)
    s += text(180, 104, "Крен / тангаж — видно ✓", size=12.5, weight="bold",
              anchor="middle", fill=GREEN)
    ax, ay = 180, 230
    s += f'<g transform="rotate(20 {ax} {ay})">\n'
    s += rect(ax - 70, ay - 12, 140, 24, fill=BOX1, stroke=BLUE, sw=1.6, rx=6)
    s += '</g>\n'
    s += line(ax, ay - 70, ax, ay + 80, stroke=GREEN, w=1.6, dash="4,3",
              marker="arrG")
    s += text(ax + 12, ay + 80, "g", size=12, fill=GREEN, weight="bold")
    s += text(180, 350, "апарат нахилився → проєкція g змінилась", size=10,
              anchor="middle", fill=INK)

    # Панель B: yaw (вид згори)
    s += rect(340, 80, 280, 300, fill="white", stroke=INK, sw=1.3, rx=11)
    s += text(480, 104, "Курс (yaw) — НЕ видно ✗", size=12.5, weight="bold",
              anchor="middle", fill=RED)
    bx, by = 480, 230
    s += f'<g transform="rotate(35 {bx} {by})">\n'
    s += rect(bx - 60, by - 22, 120, 44, fill=BOX1, stroke=BLUE, sw=1.6, rx=8)
    s += poly([(bx + 60, by), (bx + 40, by - 10), (bx + 40, by + 10)],
              fill=BLUE, stroke=BLUE)
    s += '</g>\n'
    s += circle(bx, by, 13, fill="white", stroke=GREEN, sw=1.8)
    s += circle(bx, by, 3, fill=GREEN, stroke="none")
    s += text(bx, by + 30, "g — у площину (⊙), не змінюється", size=10,
              anchor="middle", fill=GREEN)
    s += text(480, 350, "апарат повернувся → для g нічого не змінилось", size=10,
              anchor="middle", fill=INK)

    # Панель C: компас
    s += rect(640, 80, 280, 300, fill="white", stroke=INK, sw=1.3, rx=11)
    s += text(780, 104, "Курс дає магнітометр", size=12.5, weight="bold",
              anchor="middle", fill=AMBER)
    cx2, cy2 = 780, 230
    s += circle(cx2, cy2, 64, fill="#fffdf5", stroke=AMBER, sw=1.6)
    s += text(cx2, cy2 - 48, "Пн", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += line(cx2, cy2 + 40, cx2, cy2 - 40, stroke=RED, w=2.6, marker="arrR")
    s += text(780, 350, "стрілка — по горизонтальному полю Землі", size=10,
              anchor="middle", fill=INK)

    s += text(W / 2, H - 16,
              "Гравітація вертикальна, тож обертання навколо вертикалі їй «невидиме». "
              "Курс закриває магнітометр — тому в IMU-наборі він обов'язковий.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.2.3 — Барометр: тиск падає з висотою
# ════════════════════════════════════════════════════════════════════════════
def fig_baroprofile():
    W, H = 940, 480
    s = header(W, H)
    s += title(W, "Барометр: міряє тиск, а тиск падає з висотою",
               "≈ 1 гПа на кожні 8 м біля землі (≈ 12 Па/м); MEMS-сенсор ловить ~10 см")

    ox, oy = 120, 400          # початок осей
    pw, ph = 560, 300
    s += line(ox, oy, ox, oy - ph - 10, stroke=INK, w=1.6, marker="arr")
    s += line(ox, oy, ox + pw + 10, oy, stroke=INK, w=1.6, marker="arr")
    s += text(ox - 10, oy - ph - 6, "висота", size=11, anchor="end",
              weight="bold")
    s += text(ox + pw + 6, oy + 18, "тиск →", size=11, anchor="end",
              weight="bold")

    # крива p(h) = 1013 * exp(-h/8400); h: 0..6000 м
    pts = []
    for i in range(0, 61):
        h = i * 100
        p = 1013 * math.exp(-h / 8400.0)
        px = ox + (1013 - p) / 1013 * pw * 1.6
        py = oy - (h / 6000.0) * ph
        pts.append((px, py))
    s += poly(pts, fill="none", stroke=BLUE, sw=2.6, closed=False)

    # позначки
    s += circle(pts[0][0], pts[0][1], 5, fill=GREEN, stroke=INK, sw=1.2)
    s += text(pts[0][0] + 10, pts[0][1] + 4, "рівень моря ≈ 1013 гПа", size=11,
              fill=GREEN, weight="bold")
    # градієнт біля землі
    s += line(ox, oy - 40, ox + 70, oy - 40, stroke=AMBER, w=1.4)
    s += text(ox + 80, oy - 36, "≈ 1 гПа / 8 м  (≈ 12 Па/м)", size=11,
              fill=AMBER, weight="bold")

    # сенсор + Торрічеллі/Паскаль
    s += rect(710, 96, 200, 110, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += lines(724, 122, ["MEMS-барометр:", "міряє абсолютний тиск,",
                          "роздільність кілька Па", "→ ~10 см висоти."],
               size=11, lh=20)
    s += rect(710, 224, 200, 120, fill=BOX3, stroke=AMBER, sw=1.4, rx=10)
    s += lines(724, 250, ["1643 — Торрічеллі:", "ртутний барометр.",
                          "1648, Пюї-де-Дом:", "довели, що вище —", "тиск нижчий."],
               size=11, lh=20)

    s += text(W / 2, H - 12,
              "Барометр дає не висоту, а тиск; висоту з нього РАХУЮТЬ. Тому він "
              "чудовий на коротких масштабах, але без якоря пливе.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.2.4 — Барометр дрейфує з погодою (відносний давач)
# ════════════════════════════════════════════════════════════════════════════
def fig_barodrift():
    W, H = 940, 440
    s = header(W, H)
    s += title(W, "Чому барометр — відносний: погода зсуває «висоту»",
               "справжня висота стала, а тиск повзе з фронтом — і барометр «бачить» рух, якого нема")

    ox, oy = 90, 350
    s += line(ox, oy, ox + 760, oy, stroke=INK, w=1.4, marker="arr")
    s += text(ox + 760, oy + 18, "час (години)", size=11, anchor="end")
    s += line(ox, oy, ox, 90, stroke=INK, w=1.4, marker="arr")
    s += text(ox - 8, 96, "висота", size=11, anchor="end", weight="bold")

    yt = 240
    s += line(ox, yt, ox + 740, yt, stroke=GREEN, w=2.2, dash="7,4")
    s += text(ox + 200, yt - 8, "справжня висота (апарат рівно)", size=11,
              fill=GREEN, weight="bold")

    # баро-висота дрейфує (повільна хвиля)
    pts = []
    for i in range(0, 75):
        x = ox + i * 10
        y = yt - 70 * math.sin(i / 24.0) - 18 * math.sin(i / 7.0)
        pts.append((x, y))
    s += poly(pts, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(ox + 470, 120, "висота за барометром", size=11, fill=RED,
              weight="bold")
    s += line(ox + 360, yt, ox + 360, yt - 70, stroke=MUTE, w=1.2, dash="3,3")
    s += text(ox + 368, yt - 40, "фронт зсунув тиск", size=10, fill=MUTE)
    s += text(ox + 368, yt - 26, "→ «десятки метрів» хибно", size=10, fill=MUTE)

    s += text(W / 2, H - 12,
              "Висновок: барометр незамінний для ШВИДКОЇ висоти, але абсолютну "
              "прив'язку дає GNSS чи далекомір. Знову «відносне × абсолютне».",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.2.5 — Вібрація — головний ворог IMU
# ════════════════════════════════════════════════════════════════════════════
def fig_vibration():
    W, H = 940, 440
    s = header(W, H)
    s += title(W, "Вібрація — головний ворог IMU (і як її приборкати)",
               "тряска моторів забиває акселерометр; рятують ізоляція й фільтр")

    def panel(px, head, hcol, noisy):
        o = rect(px, 84, 400, 250, fill="white", stroke=hcol, sw=1.6, rx=12)
        o += text(px + 200, 110, head, size=12.5, weight="bold",
                  anchor="middle", fill=hcol)
        # мотор
        o += circle(px + 60, 175, 22, fill=PANEL, stroke=INK, sw=1.5)
        o += text(px + 60, 180, "мотор", size=9, anchor="middle")
        # IMU
        o += rect(px + 250, 158, 90, 36, fill=BOX1, stroke=BLUE, sw=1.5, rx=6)
        o += text(px + 295, 181, "IMU", size=11, anchor="middle", weight="bold",
                  fill=BLUE)
        # сигнал-трейс
        base = 270
        pts = []
        for i in range(0, 70):
            x = px + 30 + i * 5.2
            if noisy:
                y = base - 16 * math.sin(i / 2.0) - random.uniform(-14, 14)
            else:
                y = base - 14 * math.sin(i / 6.0)
            pts.append((x, y))
        o += poly(pts, fill="none", stroke=(RED if noisy else GREEN), sw=1.8,
                  closed=False)
        return o

    random.seed(5)
    s += panel(40, "Жорстко прикручений — шум", RED, True)
    s += text(240, 350, "тряска забиває сигнал; високі частоти ще й", size=10.5,
              anchor="middle", fill=INK)
    s += text(240, 366, "аліасять (Розділ 26) у смугу корисного", size=10.5,
              anchor="middle", fill=INK)
    s += panel(500, "На демпферах + ФНЧ — чисто", GREEN, False)
    s += text(700, 350, "м'який монтаж гасить тряску,", size=10.5,
              anchor="middle", fill=INK)
    s += text(700, 366, "фільтр прибирає рештки → чистий сигнал", size=10.5,
              anchor="middle", fill=INK)

    s += text(W / 2, H - 10,
              "Тому IMU ніколи не прикручують намертво: м'який монтаж + цифровий "
              "фільтр — обов'язкова частина «відчуття».",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.3.1 — Що в сигналі: код + навігаційне повідомлення; кореляція → дальність
# ════════════════════════════════════════════════════════════════════════════
def fig_signal():
    W, H = 960, 510
    s = header(W, H)
    s += title(W, "Що насправді в сигналі GNSS — і як приймач міряє дальність",
               "супутник шле код + навігаційне повідомлення; приймач совгає свою копію коду до збігу")

    s += sat(480, 96, 1.1, BLUE)
    s += text(480, 64, "супутник", size=11, anchor="middle", weight="bold",
              fill=BLUE)

    def bits(x, y, seq, sq=15, fills=None, stroke=INK):
        o = ""
        for i, b in enumerate(seq):
            f = (stroke if b else "white")
            o += rect(x + i * sq, y, sq, sq, fill=f, stroke=stroke, sw=1.0,
                      rx=0)
        return o

    SEQ = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0]
    s += bits(345, 150, SEQ, stroke=BLUE)
    s += text(480, 200, "PRN-код (унікальний для супутника) + навігаційне повідомлення",
              size=11, anchor="middle", fill=INK)

    s += rect(250, 220, 460, 96, fill=PANEL, stroke=INK, sw=1.4, rx=11)
    s += text(270, 244, "Навігаційне повідомлення містить:", size=12,
              weight="bold")
    s += lines(270, 266, [
        "• ефемериди — точна орбіта ЦЬОГО супутника (де він зараз)",
        "• альманах — грубі орбіти ВСІХ супутників  • поправки годинника  • здоров'я",
    ], size=11, lh=18)

    # кореляція
    s += text(140, 360, "Як міряється дальність (кореляція):", size=12.5,
              weight="bold")
    s += text(150, 392, "приходить:", size=11, anchor="start", fill=MUTE)
    s += bits(260, 380, SEQ, sq=13, stroke=BLUE)
    s += text(150, 424, "своя копія:", size=11, anchor="start", fill=MUTE)
    s += bits(286, 412, SEQ, sq=13, stroke=GREEN)
    s += line(260, 446, 286, 446, stroke=RED, w=2.0, marker="arrR")
    s += text(330, 462, "зсув Δt = час польоту сигналу  →  дальність = c · Δt",
              size=11.5, fill=RED, weight="bold")

    s += text(W / 2, H - 12,
              "Приймач знає форму коду наперед; величина зсуву, на якому копія "
              "збігається з прийнятим, і є час польоту.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.3.2 — Псевдодальність: годинник приймача зсуває всі дальності однаково
# ════════════════════════════════════════════════════════════════════════════
def fig_pseudorange():
    W, H = 940, 480
    s = header(W, H)
    s += title(W, "Псевдодальність: чому потрібен саме ЧЕТВЕРТИЙ супутник",
               "дешевий годинник приймача додає однакову похибку до всіх дальностей")
    sats = [(150, 110), (390, 90), (610, 110), (820, 150)]
    rx, ry = 470, 330
    for i, (sxp, syp) in enumerate(sats, 1):
        s += sat(sxp, syp, 0.9, BLUE)
        s += line(sxp, syp + 8, rx, ry - 8, stroke=MUTE, w=1.2)
        mx, my = (sxp + rx) / 2, (syp + ry) / 2
        s += text(mx, my, f"ρ{i}", size=12, fill=INK, weight="bold")
    s += circle(rx, ry, 9, fill=RED, stroke=INK, sw=1.6)
    s += text(rx, ry + 24, "приймач", size=11, anchor="middle", weight="bold",
              fill=RED)

    s += rect(60, 372, 820, 64, fill=BOX3, stroke=AMBER, sw=1.5, rx=11)
    s += text(80, 396, "ρᵢ = (справжня відстань до Satᵢ)  +  c · Δt        "
              "← той самий Δt для ВСІХ супутників",
              size=12.5, weight="bold", family="Consolas, monospace", fill=INK)
    s += text(80, 420, "4 супутники → 4 рівняння → 4 невідомі: x, y, z  і  Δt "
              "(похибка годинника приймача).",
              size=12, fill=INK)
    s += text(W / 2, H - 10,
              "Тому «псевдо»-дальність: вона завищена на невідоме c·Δt. Четвертий "
              "супутник якраз і дає рівняння, щоб цей зсув знайти й відняти.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.3.3 — Чому фікс не миттєвий: холодний / теплий / гарячий старт
# ════════════════════════════════════════════════════════════════════════════
def fig_ttff():
    W, H = 940, 470
    s = header(W, H)
    s += title(W, "Чому перший фікс не миттєвий: що приймач мусить дізнатися",
               "час до першого фікса (TTFF) залежить від того, що вже відомо")
    rows = [
        ("Холодний старт", "не знає нічого", "знайти супутники + ефемериди (+ альманах)",
         "~30–60 с,  до 12.5 хв на повний альманах", RED, 760),
        ("Теплий старт", "є альманах і груба позиція/час", "лише свіжі ефемериди",
         "~30–45 с", AMBER, 300),
        ("Гарячий старт", "усе свіже з нещодавна", "майже нічого",
         "~0.5–20 с", GREEN, 120),
    ]
    y = 90
    for nm, knows, needs, t, col, barw in rows:
        s += rect(40, y, 470, 96, fill="white", stroke=col, sw=1.7, rx=11)
        s += text(58, y + 26, nm, size=13.5, weight="bold", fill=col)
        s += text(58, y + 50, "знає: " + knows, size=11, fill=INK)
        s += text(58, y + 72, "мусить: " + needs, size=11, fill=INK)
        # часова смуга
        s += rect(540, y + 30, barw * 0.46, 34, fill=col, stroke="none",
                  opacity=0.6, rx=6)
        s += rect(540, y + 30, 372, 34, fill="none", stroke=MUTE, sw=1.0, rx=6)
        s += text(550, y + 52, t, size=11.5, weight="bold", fill=INK)
        y += 116
    s += text(W / 2, H - 16,
              "Ефемериди дійсні ~2 год, альманах — тижні. Ось чому свіжовключений "
              "апарат «думає» довше, ніж той, що нещодавно вже ловив супутники.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.3.4 — Геометрія важить: HDOP
# ════════════════════════════════════════════════════════════════════════════
def fig_dop():
    W, H = 940, 470
    s = header(W, H)
    s += title(W, "Не лише скільки супутників, а й ЯК вони розкидані: HDOP",
               "широкий розкид по небу — точний фікс; супутники купкою — розмитий")

    def sky(px, head, sats, ex, ey, col, note):
        cx, cy = px + 190, 250
        o = text(px + 190, 96, head, size=12.5, weight="bold", anchor="middle",
                 fill=col)
        o += circle(cx, cy, 130, fill="#f7fbff", stroke=BLUE, sw=1.4)
        o += circle(cx, cy, 4, fill=MUTE, stroke="none")
        o += text(cx, cy - 138, "небо (вид угору)", size=9.5, anchor="middle",
                  fill=MUTE)
        for ang, rad in sats:
            x = cx + rad * math.cos(math.radians(ang))
            y = cy + rad * math.sin(math.radians(ang))
            o += sat(x, y, 0.55, INK)
        # еліпс похибки в приймачі
        o += f'<ellipse cx="{cx}" cy="{cy}" rx="{ex}" ry="{ey}" fill="{col}" fill-opacity="0.35" stroke="{col}" stroke-width="1.6"/>\n'
        o += text(px + 190, 400, note, size=11, anchor="middle", fill=col,
                  weight="bold")
        return o

    good = [(20, 115), (90, 120), (160, 110), (230, 118), (300, 112)]
    bad = [(60, 110), (75, 118), (90, 105), (50, 95), (80, 85)]
    s += sky(30, "Добра геометрія — низький HDOP", good, 16, 14, GREEN,
             "розкид широкий → мала кругла похибка")
    s += sky(530, "Погана геометрія — високий HDOP", bad, 14, 60, RED,
             "усі в кутку → велика витягнута похибка")

    s += text(W / 2, H - 14,
              "Тому апарат чекає не лише на «≥4 супутники», а й на ДОБРУ геометрію "
              "(низький HDOP) — інакше фікс є, та точність кепська.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.3.5 — Похибки й драбина точності
# ════════════════════════════════════════════════════════════════════════════
def fig_errors():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Звідки похибки — і як спуститися від метрів до сантиметрів",
               "атмосфера й відбиття псують сигнал; корекції їх прибирають")

    s += rect(40, 90, 380, 300, fill="white", stroke=INK, sw=1.4, rx=12)
    s += text(230, 116, "Джерела похибки", size=13, weight="bold",
              anchor="middle")
    errs = [("Іоносфера / тропосфера", "сигнал гальмується — найбільша", RED),
            ("Багатопроменевість", "відбиття від будівель, землі", AMBER),
            ("Орбіта й годинник супутника", "невеликі, але є", BLUE),
            ("Шум приймача", "найменша", MUTE)]
    yy = 140
    for nm, d, col in errs:
        s += rect(60, yy, 340, 52, fill="white", stroke=col, sw=1.3, rx=8)
        s += text(74, yy + 22, nm, size=11.5, weight="bold", fill=col)
        s += text(74, yy + 40, d, size=10.5, fill=INK)
        yy += 60

    # драбина точності
    s += text(690, 116, "Драбина точності", size=13, weight="bold",
              anchor="middle")
    steps = [("Звичайний GNSS", "~3–5 м", 470, 150, "#fde2e2", RED),
             ("+ SBAS (WAAS/EGNOS)", "~1–2 м", 540, 220, "#fff0d8", AMBER),
             ("+ RTK (база + фаза несучої)", "~1–3 см", 610, 290, "#d8f3e0",
              GREEN)]
    for nm, acc, x, y, fill, col in steps:
        s += rect(x, y, 320, 56, fill=fill, stroke=col, sw=1.6, rx=10)
        s += text(x + 14, y + 24, nm, size=12, weight="bold", fill=col)
        s += text(x + 14, y + 44, "точність " + acc, size=11.5, fill=INK)
    s += text(690, 366, "↓ що нижче — то точніше", size=11, anchor="middle",
              fill=MUTE, italic=True)

    s += text(W / 2, H - 12,
              "Багатосмуговий (L1/L5) і багатосузір'яний приймач сам собою точніший: "
              "більше супутників і менший вплив іоносфери.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.4.1 — Щіткований проти безщіткового мотора
# ════════════════════════════════════════════════════════════════════════════
def fig_brushed():
    W, H = 960, 500
    s = header(W, H)
    s += title(W, "Чому дрони літають на безщіткових моторах",
               "щітки прибрали: обмотки переїхали на статор, комутацію робить електроніка")

    def housing(cx, cy):
        return circle(cx, cy, 96, fill="white", stroke=INK, sw=2.0)

    # ── ЩІТКОВАНИЙ (ліворуч) ──
    cx, cy = 240, 250
    s += text(240, 100, "Щіткований (brushed)", size=13.5, weight="bold",
              anchor="middle", fill=AMBER)
    s += housing(cx, cy)
    # магніти статора (зовні)
    s += rect(cx - 22, cy - 92, 44, 22, fill="#fde0e0", stroke=RED, sw=1.3, rx=4)
    s += text(cx, cy - 76, "N", size=12, anchor="middle", weight="bold",
              fill=RED)
    s += rect(cx - 22, cy + 70, 44, 22, fill="#e0e6fd", stroke=BLUE, sw=1.3,
              rx=4)
    s += text(cx, cy + 86, "S", size=12, anchor="middle", weight="bold",
              fill=BLUE)
    # ротор з обмотками
    s += circle(cx, cy, 48, fill=BOX1, stroke=BLUE, sw=1.6)
    s += text(cx, cy - 4, "обмотки", size=10.5, anchor="middle", weight="bold")
    s += text(cx, cy + 12, "на РОТОРІ", size=10, anchor="middle", fill=BLUE)
    # щітки + колектор
    s += line(cx - 96, cy, cx - 50, cy, stroke=INK, w=3)
    s += line(cx + 96, cy, cx + 50, cy, stroke=INK, w=3)
    s += text(cx - 96, cy - 8, "щітка", size=9.5, anchor="middle", fill=MUTE)
    s += text(cx + 96, cy - 8, "щітка", size=9.5, anchor="middle", fill=MUTE)
    s += lines(120, 380, ["щітки труться, іскрять і зношуються;",
                          "обмежують оберти й потужність."], size=11, lh=17,
               fill=INK)

    # ── БЕЗЩІТКОВИЙ (праворуч) ──
    cx2, cy2 = 700, 250
    s += text(700, 100, "Безщітковий (BLDC)", size=13.5, weight="bold",
              anchor="middle", fill=GREEN)
    # дзвін-ротор із магнітами (зовні)
    s += circle(cx2, cy2, 96, fill="white", stroke=INK, sw=2.0)
    for k in range(8):
        a = math.radians(k * 45)
        mx = cx2 + 82 * math.cos(a)
        my = cy2 + 82 * math.sin(a)
        col = RED if k % 2 == 0 else BLUE
        s += circle(mx, my, 11, fill=("#fde0e0" if k % 2 == 0 else "#e0e6fd"),
                    stroke=col, sw=1.2)
        s += text(mx, my + 4, "N" if k % 2 == 0 else "S", size=9,
                  anchor="middle", fill=col, weight="bold")
    # статор з 3 фазами (всередині, нерухомий)
    s += circle(cx2, cy2, 50, fill=BOX2, stroke=GREEN, sw=1.6)
    for k, lab in enumerate(["A", "B", "C"]):
        a = math.radians(90 + k * 120)
        s += text(cx2 + 30 * math.cos(a), cy2 + 30 * math.sin(a) + 4, lab,
                  size=12, anchor="middle", weight="bold", fill=GREEN)
    s += text(cx2, cy2 + 64, "обмотки на СТАТОРІ", size=9.5, anchor="middle",
              fill=GREEN)
    s += text(cx2, cy2 - 70, "магніти на дзвоні-роторі", size=9, anchor="middle",
              fill=MUTE)
    # ESC
    s += rect(820, 220, 110, 60, fill=PANEL, stroke=INK, sw=1.4, rx=8)
    s += text(875, 246, "ESC", size=12, anchor="middle", weight="bold")
    s += text(875, 264, "комутує", size=9.5, anchor="middle", fill=MUTE)
    s += line(796, 250, 818, 250, stroke=INK, w=1.6, marker="arr")
    s += lines(580, 380, ["без щіток → без зносу й іскор;",
                          "ефективний, велика питома потужність;",
                          "комутацію робить електроніка (ESC)."], size=11,
               lh=17, fill=INK)

    s += text(W / 2, H - 14,
              "Ідея проста: те, що крутилось і терлось (обмотки + щітки), зробили "
              "нерухомим, а перемикання струму віддали транзисторам.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.4.2 — Три фази й обертове магнітне поле
# ════════════════════════════════════════════════════════════════════════════
def fig_phases():
    W, H = 960, 510
    s = header(W, H)
    s += title(W, "Три фази створюють обертове поле, за яким женеться ротор",
               "обмотки A, B, C вмикають по черзі — сумарне поле «крутиться», магніти слідують")

    cx, cy = 250, 220
    s += circle(cx, cy, 120, fill="#fbfbfd", stroke=INK, sw=1.8)
    # 3 котушки
    coils = [(90, "A", RED), (210, "B", GREEN), (330, "C", BLUE)]
    for ang, lab, col in coils:
        a = math.radians(ang)
        x = cx + 95 * math.cos(a)
        y = cy + 95 * math.sin(a)
        s += circle(x, y, 22, fill="white", stroke=col, sw=1.8)
        s += text(x, y + 5, lab, size=14, anchor="middle", weight="bold",
                  fill=col)
    # сумарне поле (стрілка) у певний момент
    fang = math.radians(150)
    s += line(cx, cy, cx + 70 * math.cos(fang), cy + 70 * math.sin(fang),
              stroke=AMBER, w=3.0, marker="arr")
    s += text(cx + 88 * math.cos(fang), cy + 88 * math.sin(fang), "поле",
              size=11, anchor="middle", fill=AMBER, weight="bold")
    # ротор-магніт (стрілка N-S) слідує за полем
    s += line(cx - 36 * math.cos(fang), cy - 36 * math.sin(fang),
              cx + 36 * math.cos(fang), cy + 36 * math.sin(fang),
              stroke=INK, w=8)
    s += text(cx, cy + 145, "ротор (магніти) женеться за полем", size=10.5,
              anchor="middle", fill=INK)
    # стрілка обертання
    s += text(cx + 92, cy - 92, "↻", size=26, fill=GREEN, weight="bold")

    # 3 синусоїди праворуч
    px, py, pw, ph = 470, 130, 440, 200
    s += line(px, py + ph / 2, px + pw, py + ph / 2, stroke=MUTE, w=1.0)
    s += text(px - 6, py - 4, "струм у фазах", size=11, anchor="start",
              weight="bold")
    cols = [RED, GREEN, BLUE]
    for ph_i, col in enumerate(cols):
        pts = []
        for i in range(0, 89):
            x = px + i / 88 * pw
            y = (py + ph / 2) - 70 * math.sin(2 * math.pi * i / 88
                                              - ph_i * 2 * math.pi / 3)
            pts.append((x, y))
        s += poly(pts, fill="none", stroke=col, sw=2.0, closed=False)
    s += text(px + pw + 4, py + ph / 2, "час", size=10, anchor="start",
              fill=MUTE)
    s += text(px, py + ph + 24, "A · B · C зсунуті на 120° — їхня сума й дає поле, що рівномірно обертається",
              size=10.5, fill=INK)

    s += rect(470, 372, 440, 60, fill=BOX3, stroke=AMBER, sw=1.4, rx=10)
    s += lines(486, 396, ["«Безколекторний» = синхронний мотор: ротор крутиться",
                          "точно в такт із полем, яке малює електроніка."],
               size=11, lh=18)

    s += text(W / 2, H - 12,
              "Скільки разів за оберт перемкнути фази — задають магнітні полюси ротора; "
              "більше полюсів → більший момент, менші оберти.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.4.3 — KV: компроміс швидкість/момент
# ════════════════════════════════════════════════════════════════════════════
def fig_kv():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "KV — головна цифра мотора: оберти на вольт (на холостому)",
               "високий KV — швидко й слабкий момент; низький — повільно й сильний")

    s += line(120, 250, 840, 250, stroke=INK, w=2.0, marker="arr")
    s += text(120, 280, "низький KV", size=12, weight="bold", fill=GREEN)
    s += text(820, 280, "високий KV", size=12, weight="bold", anchor="end",
              fill=RED)
    s += text(480, 280, "KV (об/хв на вольт)", size=11, anchor="middle",
              fill=MUTE)

    # дві приклади-картки
    s += rect(120, 90, 320, 130, fill="#eafaef", stroke=GREEN, sw=1.7, rx=12)
    s += text(280, 116, "~400 KV — низький", size=13, weight="bold",
              anchor="middle", fill=GREEN)
    s += lines(140, 142, ["повільно, але сильний момент",
                          "→ великі гвинти, важкий апарат",
                          "(підйомні, вантажні дрони)"], size=11.5, lh=20)
    s += rect(540, 90, 320, 130, fill="#fff0f0", stroke=RED, sw=1.7, rx=12)
    s += text(700, 116, "~2400 KV — високий", size=13, weight="bold",
              anchor="middle", fill=RED)
    s += lines(560, 142, ["швидко, але слабкий момент",
                          "→ малі гвинти, легкий апарат",
                          "(гоночні дрони)"], size=11.5, lh=20)

    s += line(280, 220, 280, 244, stroke=GREEN, w=1.5, marker="arrG")
    s += line(700, 220, 700, 244, stroke=RED, w=1.5, marker="arrR")

    s += rect(120, 320, 720, 96, fill=PANEL, stroke=INK, sw=1.4, rx=11)
    s += text(140, 346, "Холості оберти ≈ KV × напруга:", size=12.5,
              weight="bold")
    s += text(140, 372, "напр. 900 KV × 14.8 В ≈ 13 300 об/хв (без навантаження)",
              size=12, family="Consolas, monospace", fill=INK)
    s += text(140, 398, "Момент і KV — обернені: що вищий KV, то менший момент на ампер.",
              size=11.5, fill=INK)

    s += text(W / 2, H - 12,
              "Тому мотор добирають у парі з гвинтом і напругою: KV, гвинт і число "
              "банок батареї мусять пасувати одне до одного.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.4.4 — Зворотна ЕРС самообмежує швидкість
# ════════════════════════════════════════════════════════════════════════════
def fig_backemf():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Зворотна ЕРС: чому мотор сам не розганяється безмежно",
               "магніти, що крутяться, наводять напругу ПРОТИ живлення (Ленц, Розділ 8)")

    # схема ліворуч
    s += rect(60, 110, 330, 250, fill="white", stroke=INK, sw=1.4, rx=12)
    s += text(225, 134, "Електрична картина", size=12.5, weight="bold",
              anchor="middle")
    s += text(110, 180, "V", size=14, weight="bold", fill=RED)
    s += line(130, 180, 200, 180, stroke=INK, w=1.6)
    s += text(165, 170, "R (обмотка)", size=10, anchor="middle", fill=MUTE)
    s += rect(200, 168, 50, 24, fill=PANEL, stroke=INK, sw=1.2, rx=3)
    s += text(290, 180, "E (зв. ЕРС)", size=11, fill=BLUE, weight="bold")
    s += line(250, 180, 300, 180, stroke=INK, w=1.6)
    s += rect(70, 250, 300, 90, fill="#f3f7ff", stroke=BLUE, sw=1.3, rx=9)
    s += text(90, 274, "струм (момент):", size=11.5, weight="bold")
    s += text(90, 300, "I = (V − E) / R", size=14, family="Consolas, monospace",
              weight="bold", fill=INK)
    s += text(90, 324, "E зростає зі швидкістю → I падає", size=11, fill=INK)

    # графік праворуч
    ox, oy = 470, 350
    s += line(ox, oy, ox + 420, oy, stroke=INK, w=1.4, marker="arr")
    s += text(ox + 420, oy + 18, "швидкість", size=11, anchor="end")
    s += line(ox, oy, ox, 120, stroke=INK, w=1.4, marker="arr")
    s += text(ox - 8, 126, "напруга", size=11, anchor="end", weight="bold")
    s += line(ox, 160, ox + 400, 160, stroke=RED, w=1.6, dash="6,4")
    s += text(ox + 8, 152, "V (живлення)", size=11, fill=RED, weight="bold")
    s += line(ox, oy, ox + 360, 160, stroke=BLUE, w=2.6)
    s += text(ox + 250, 250, "E = зворотна ЕРС ∝ швидкість", size=11,
              fill=BLUE, weight="bold")
    s += circle(ox + 360, 160, 6, fill=GREEN, stroke=INK, sw=1.4)
    s += text(ox + 300, 138, "холостий хід: E ≈ V → I ≈ 0", size=10.5,
              fill=GREEN, weight="bold")
    # навантаження
    s += line(ox + 180, oy, ox + 180, 250, stroke=MUTE, w=1.0, dash="3,3")
    s += text(ox + 184, 270, "під навантаженням:", size=10, fill=MUTE)
    s += text(ox + 184, 284, "повільніше → E менша →", size=10, fill=MUTE)
    s += text(ox + 184, 298, "більший струм → більший момент", size=10,
              fill=MUTE)

    s += text(W / 2, H - 12,
              "Тому мотор саморегулюється: важче навантаження — нижчі оберти, нижча "
              "E, більший струм і момент. Швидкість задає напруга, момент — струм.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.4.5 — Безсенсорна комутація через зворотну ЕРС + проблема старту
# ════════════════════════════════════════════════════════════════════════════
def fig_sensorless():
    W, H = 940, 470
    s = header(W, H)
    s += title(W, "Як ESC «знає», коли перемикати: слухає зворотну ЕРС",
               "дві фази під струмом, третя «вільна» — її напруга підказує положення ротора")

    # Y-схема трьох фаз
    cx, cy = 250, 240
    ends = [(90, "A", RED, True), (210, "B", GREEN, True), (330, "C", BLUE, False)]
    s += circle(cx, cy, 6, fill=INK, stroke="none")
    for ang, lab, col, driven in ends:
        a = math.radians(ang)
        x = cx + 120 * math.cos(a)
        y = cy + 120 * math.sin(a)
        dash = None if driven else "6,4"
        s += line(cx, cy, x, y, stroke=col, w=3.0 if driven else 2.0, dash=dash)
        s += circle(x, y, 18, fill="white", stroke=col, sw=1.8)
        s += text(x, y + 5, lab, size=13, anchor="middle", weight="bold",
                  fill=col)
        tag = "+ струм" if (driven and lab == "A") else ("− струм" if driven else "ВІЛЬНА")
        s += text(x + (40 if x > cx else -40), y, tag, size=10,
                  anchor="middle", fill=col, weight="bold")
    s += text(cx, cy + 170, "у кожен момент: 2 фази під струмом, 1 вільна",
              size=11, anchor="middle", fill=INK)

    # графік зв. ЕРС на вільній фазі
    ox, oy = 560, 230
    s += rect(520, 110, 390, 240, fill="white", stroke=INK, sw=1.3, rx=11)
    s += text(715, 134, "Напруга на вільній фазі (C)", size=12, weight="bold",
              anchor="middle")
    s += line(ox, oy, ox + 320, oy, stroke=MUTE, w=1.0)
    pts = []
    for i in range(0, 65):
        x = ox + i * 5
        y = oy - 60 * math.sin(2 * math.pi * i / 64)
        pts.append((x, y))
    s += poly(pts, fill="none", stroke=BLUE, sw=2.2, closed=False)
    s += circle(ox + 160, oy, 6, fill=RED, stroke=INK, sw=1.4)
    s += text(ox + 160, oy + 30, "перетин нуля", size=10.5, anchor="middle",
              fill=RED, weight="bold")
    s += text(ox + 160, oy + 46, "→ тут перемкнути фази", size=10.5,
              anchor="middle", fill=RED)

    s += rect(520, 366, 390, 70, fill="#fff0f0", stroke=RED, sw=1.4, rx=10)
    s += text(540, 390, "Проблема старту:", size=11.5, weight="bold", fill=RED)
    s += lines(540, 410, ["на місці ротор не рухається → зворотної ЕРС нема →",
                          "ESC мусить «штовхати» наосліп, поки мотор не розкрутиться."],
               size=10.5, lh=15)

    s += text(W / 2, H - 12,
              "Тому деякі мотори мають окремі давачі Холла — але більшість дронових "
              "ESC обходяться зворотною ЕРС (дешевше, без дротів).",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.5.1 — Три роботи ESC (між контролером і мотором)
# ════════════════════════════════════════════════════════════════════════════
def fig_esc_jobs():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Регулятор обертів (ESC): три роботи між контролером і мотором",
               "приймає команду газу — і живить, комутує та регулює трифазний мотор")

    s += rect(40, 175, 150, 100, fill=BOX2, stroke=GREEN, sw=1.7, rx=11)
    s += lines(115, 215, ["Політний", "контролер"], size=12, anchor="middle",
               lh=18, weight="bold", fill=GREEN)
    s += text(115, 258, "(газ кожному)", size=9.5, anchor="middle", fill=MUTE)

    s += rect(300, 100, 350, 270, fill="white", stroke=INK, sw=1.9, rx=13)
    s += text(475, 128, "ESC", size=15, weight="bold", anchor="middle")
    s += text(475, 146, "крихітний комп'ютер (прошивка BLHeli / AM32)", size=9.5,
              anchor="middle", fill=MUTE)
    jobs = [("1. Силові ключі", "3-фазний інвертор (6 MOSFET) — м'язи", BLUE),
            ("2. Комутація", "коли перемикати — за зворотною ЕРС", AMBER),
            ("3. Регулювання", "ШІМ-шпаруватість за командою газу", GREEN)]
    yy = 162
    for nm, d, col in jobs:
        s += rect(318, yy, 314, 62, fill="white", stroke=col, sw=1.4, rx=9)
        s += text(332, yy + 24, nm, size=12, weight="bold", fill=col)
        s += text(332, yy + 46, d, size=10.5, fill=INK)
        yy += 70

    s += rect(760, 175, 160, 100, fill=BOX1, stroke=BLUE, sw=1.7, rx=11)
    s += lines(840, 215, ["BLDC", "мотор"], size=12, anchor="middle", lh=18,
               weight="bold", fill=BLUE)

    s += line(190, 225, 298, 225, stroke=GREEN, w=2.2, marker="arrG")
    s += text(244, 214, "команда", size=10, anchor="middle", fill=GREEN)
    s += line(652, 210, 758, 210, stroke=INK, w=2.2, marker="arr")
    s += text(705, 200, "3 фази", size=10, anchor="middle", fill=INK)
    s += line(758, 248, 652, 248, stroke=AMBER, w=1.8, marker="arrB")
    s += text(705, 264, "зворотна ЕРС", size=9.5, anchor="middle", fill=AMBER)

    s += text(W / 2, H - 14,
              "Контролер не торкається фаз мотора — він лише каже ESC «скільки газу», "
              "а вся силова брудна робота лишається в ESC.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.5.2 — Трифазний інвертор: 6 MOSFET (три півмости)
# ════════════════════════════════════════════════════════════════════════════
def fig_inverter():
    W, H = 960, 510
    s = header(W, H)
    s += title(W, "Силова частина ESC: трифазний інвертор із 6 MOSFET",
               "три півмости (Розділ 12) по черзі підмикають фази до «+» і «−» батареї")

    s += line(90, 120, 690, 120, stroke=RED, w=3.0)
    s += text(70, 124, "+", size=18, anchor="middle", weight="bold", fill=RED)
    s += line(90, 430, 690, 430, stroke=BLUE, w=3.0)
    s += text(70, 434, "−", size=18, anchor="middle", weight="bold", fill=BLUE)
    s += text(710, 120, "батарея", size=11, fill=RED, anchor="start")

    mx, my = 810, 275
    phases = [(220, "A", True), (390, "B", False), (560, "C", None)]
    for x, lab, active in phases:
        hs_on = active is True
        ls_on = active is False
        s += rect(x - 34, 160, 68, 50, fill=("#d8f3e0" if hs_on else "white"),
                  stroke=(GREEN if hs_on else INK), sw=1.6, rx=7)
        s += text(x, 182, "HS", size=11, anchor="middle", weight="bold")
        s += text(x, 198, "MOSFET", size=8, anchor="middle", fill=MUTE)
        s += line(x, 120, x, 160, stroke=INK, w=1.6)
        s += rect(x - 34, 340, 68, 50, fill=("#d8f3e0" if ls_on else "white"),
                  stroke=(GREEN if ls_on else INK), sw=1.6, rx=7)
        s += text(x, 362, "LS", size=11, anchor="middle", weight="bold")
        s += text(x, 378, "MOSFET", size=8, anchor="middle", fill=MUTE)
        s += line(x, 390, x, 430, stroke=INK, w=1.6)
        # середня точка → фаза → мотор
        s += line(x, 210, x, 340, stroke=MUTE, w=1.4)
        s += circle(x, 275, 4, fill=INK, stroke="none")
        s += text(x + 11, 268, lab, size=13, weight="bold", anchor="start",
                  fill=INK)
        s += line(x, 275, mx - 44, my, stroke=INK, w=1.3, opacity=0.7)

    # мотор (Y) праворуч
    s += circle(mx, my, 44, fill=BOX1, stroke=BLUE, sw=1.7)
    s += text(mx, my + 5, "мотор", size=11, anchor="middle", weight="bold",
              fill=BLUE)

    # керування затворами
    s += rect(120, 450, 250, 44, fill=PANEL, stroke=INK, sw=1.3, rx=8)
    s += text(245, 477, "МК ESC керує затворами (вмик/вимик)", size=11,
              anchor="middle", weight="bold")

    s += text(W / 2, H - 8,
              "Зараз показано один крок: HS фази A та LS фази B відкриті — струм "
              "тече A→мотор→B, а фаза C «вільна» (на ній і слухають зворотну ЕРС).",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.5.3 — Сигнал FC→ESC: від аналогового PWM до цифрового DShot
# ════════════════════════════════════════════════════════════════════════════
def fig_protocols():
    W, H = 980, 500
    s = header(W, H)
    s += title(W, "Як контролер каже ESC «газ»: від аналогового PWM до цифрового DShot",
               "старий спосіб — ширина імпульсу; новий — цифровий пакет із перевіркою")

    # PWM (зверху)
    s += text(60, 100, "PWM (сервоформат) — аналоговий", size=12.5,
              weight="bold", fill=AMBER)
    bx, by = 60, 150
    s += line(bx, by, bx + 360, by, stroke=MUTE, w=1.0)
    s += poly([(bx, by), (bx + 40, by), (bx + 40, by - 40), (bx + 150, by - 40),
               (bx + 150, by), (bx + 360, by)], fill="none", stroke=AMBER,
              sw=2.2, closed=False)
    s += line(bx + 40, by + 14, bx + 150, by + 14, stroke=INK, w=1.2,
              marker="arr")
    s += line(bx + 150, by + 14, bx + 40, by + 14, stroke=INK, w=1.2,
              marker="arr")
    s += text(bx + 95, by + 30, "ширина 1000–2000 µs = газ", size=10.5,
              anchor="middle", fill=INK)
    s += lines(460, 122, ["повільно, дрижить, чутливий до шуму,",
                          "треба калібрувати діапазон газу.",
                          "(OneShot/Multishot — те саме, лише коротше/швидше)"],
               size=11, lh=18, fill=INK)

    # DShot (знизу)
    s += text(60, 252, "DShot — цифровий пакет", size=12.5, weight="bold",
              fill=GREEN)
    fx, fy = 60, 280
    groups = [(11, "11 біт — газ (0…2047)", BLUE),
              (1, "тлм", AMBER), (4, "4 біти — CRC", GREEN)]
    cell = 38
    x = fx
    for n, lab, col in groups:
        s += rect(x, fy, cell * n, 44, fill=("#eef2ff" if col == BLUE else
                  ("#fff5e6" if col == AMBER else "#eafaef")), stroke=col,
                  sw=1.6, rx=6)
        for k in range(1, n):
            s += line(x + k * cell, fy, x + k * cell, fy + 44, stroke=col,
                      w=0.6, opacity=0.4)
        s += text(x + cell * n / 2, fy + 64, lab, size=10.5, anchor="middle",
                  fill=col, weight="bold")
        x += cell * n
    s += text(fx, fy - 10, "16-бітний кадр:", size=11, weight="bold")
    s += lines(640, 274, ["точний, без калібрування;",
                          "CRC ловить спотворення → ESC тримає",
                          "останнє чинне значення (без стрибка);",
                          "несе телеметрію; DShot150/300/600 — швидкість."],
               size=11, lh=18, fill=INK)

    s += text(W / 2, H - 16,
              "Цифровий протокол прибрав болячки аналогового: ні калібрування, ні "
              "дрижання — лише числа з контрольною сумою.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.5.4 — Зворотний зв'язок і захист ESC
# ════════════════════════════════════════════════════════════════════════════
def fig_esc_telem():
    W, H = 940, 460
    s = header(W, H)
    s += title(W, "Сучасний ESC не лише крутить — він і доповідає, і захищає",
               "телеметрія назад у контролер + власні запобіжники")

    s += rect(60, 150, 180, 90, fill="white", stroke=INK, sw=1.7, rx=11)
    s += text(150, 190, "ESC", size=14, weight="bold", anchor="middle")
    s += text(150, 212, "+ прошивка", size=10, anchor="middle", fill=MUTE)
    s += rect(700, 150, 180, 90, fill=BOX2, stroke=GREEN, sw=1.7, rx=11)
    s += lines(790, 190, ["Політний", "контролер"], size=12, anchor="middle",
               lh=18, weight="bold", fill=GREEN)

    s += line(240, 180, 698, 180, stroke=BLUE, w=2.0, marker="arrB")
    s += text(470, 168, "телеметрія (bidirectional DShot чи окремий дріт):",
              size=11, anchor="middle", weight="bold", fill=BLUE)
    s += text(470, 205, "оберти (RPM) · струм · напруга · температура", size=12,
              anchor="middle", fill=INK, weight="bold")

    s += rect(120, 290, 320, 120, fill="#fff0f0", stroke=RED, sw=1.6, rx=12)
    s += text(280, 316, "Власні запобіжники", size=12.5, weight="bold",
              anchor="middle", fill=RED)
    s += lines(140, 340, ["• струмова межа",
                          "• теплове вимкнення при перегріві",
                          "• виявлення зриву/застрягання"], size=11.5, lh=22)

    s += rect(500, 290, 340, 120, fill="#eef6ff", stroke=BLUE, sw=1.6, rx=12)
    s += text(670, 316, "Зброєння (arming)", size=12.5, weight="bold",
              anchor="middle", fill=BLUE)
    s += lines(520, 340, ["• мотор крутиться лише після «озброєння»",
                          "• низький газ на старті — обов'язково",
                          "• захист від випадкового запуску"], size=11.5, lh=22)

    s += text(W / 2, H - 12,
              "Оберти з ESC ще й чистять давачі (RPM-фільтр), а телеметрія дає "
              "контролеру знати про здоров'я кожного мотора (місток до 44.7).",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.6.1 — Усередині серво: міні-контур зі зворотним зв'язком
# ════════════════════════════════════════════════════════════════════════════
def fig_servo():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Серво — це маленький замкнений контур: командуєш КУТ, не швидкість",
               "усередині мотор + редуктор + давач кута + схема, що тримає задану позицію")

    # корпус серво
    s += rect(60, 110, 470, 250, fill="#fbfbfd", stroke=INK, sw=1.8, rx=12)
    s += text(295, 134, "серворушій (servo)", size=12, weight="bold",
              anchor="middle")

    # вхід ШІМ
    s += text(70, 196, "ШІМ →", size=11, weight="bold", fill=GREEN)
    s += text(70, 212, "бажаний кут", size=10, fill=GREEN)
    # Σ порівняти
    s += circle(170, 200, 20, fill="white", stroke=INK, sw=1.6)
    s += text(170, 205, "Σ", size=16, anchor="middle", weight="bold")
    s += line(132, 200, 150, 200, stroke=GREEN, w=1.8, marker="arrG")
    # мотор
    s += rect(230, 178, 80, 44, fill=BOX1, stroke=BLUE, sw=1.5, rx=8)
    s += text(270, 204, "мотор", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    s += line(190, 200, 228, 200, stroke=RED, w=1.8, marker="arrR")
    s += text(209, 190, "похибка", size=8.5, anchor="middle", fill=RED)
    # редуктор
    s += rect(340, 178, 86, 44, fill=PANEL, stroke=INK, sw=1.5, rx=8)
    s += text(383, 204, "редуктор", size=10.5, anchor="middle", weight="bold")
    s += line(310, 200, 338, 200, stroke=INK, w=1.6, marker="arr")
    # вихідний вал + качалка
    s += circle(470, 200, 16, fill="white", stroke=INK, sw=1.6)
    s += line(470, 200, 506, 176, stroke=INK, w=4)
    s += line(426, 200, 454, 200, stroke=INK, w=1.6, marker="arr")
    s += text(486, 230, "вал (качалка)", size=9.5, anchor="middle", fill=INK)
    # зворотний зв'язок (потенціометр)
    s += line(470, 216, 470, 330, stroke=AMBER, w=1.6)
    s += line(470, 330, 170, 330, stroke=AMBER, w=1.6)
    s += line(170, 330, 170, 222, stroke=AMBER, w=1.6, marker="arrB")
    s += text(320, 322, "потенціометр міряє СПРАВЖНІЙ кут вала", size=10.5,
              anchor="middle", fill=AMBER, weight="bold")

    # контраст мотор vs серво
    s += rect(560, 130, 360, 210, fill=BOX3, stroke=AMBER, sw=1.6, rx=12)
    s += text(740, 156, "Мотор vs Серво", size=13, weight="bold",
              anchor="middle", fill=AMBER)
    s += lines(580, 186, [
        "МОТОР: командуєш ШВИДКІСТЬ —",
        "крутиться безперервно (тяга).",
        "",
        "СЕРВО: командуєш КУТ —",
        "повертає вал у позицію й ТРИМАЄ.",
        "",
        "Це той самий зворотний зв'язок,",
        "що в ПІД із Розділу 34 — лише в залізі.",
    ], size=11, lh=20)

    s += text(W / 2, H - 14,
              "Схема щомиті порівнює заданий кут із виміряним і підкручує мотор, "
              "поки різниця не зникне, — крихітний автопілот для одного вала.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.6.2 — Сигнал серво: ширина імпульсу = кут
# ════════════════════════════════════════════════════════════════════════════
def fig_servo_signal():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Сигнал серво: ширина імпульсу задає кут (класичний RC-стандарт)",
               "період ~20 мс (≈50 Гц); 1000 µs — один край, 1500 — центр, 2000 — інший")

    cases = [(160, 1.0, -45, "1000 µs", "один край"),
             (480, 1.5, 0, "1500 µs", "центр"),
             (800, 2.0, 45, "2000 µs", "інший край")]
    for cx, ms, ang, lab, sub in cases:
        # імпульс
        by = 150
        s += line(cx - 110, by, cx + 110, by, stroke=MUTE, w=1.0)
        pw = ms * 40
        s += poly([(cx - 90, by), (cx - 90 + 10, by), (cx - 90 + 10, by - 46),
                   (cx - 90 + 10 + pw, by - 46), (cx - 90 + 10 + pw, by),
                   (cx + 100, by)], fill="none", stroke=BLUE, sw=2.2,
                  closed=False)
        s += text(cx, by + 22, lab, size=12, anchor="middle", weight="bold",
                  fill=BLUE)
        # серво-кут
        sy = 300
        s += circle(cx, sy, 44, fill="#fbfbfd", stroke=INK, sw=1.5)
        a = math.radians(ang - 90)
        s += line(cx, sy, cx + 60 * math.cos(a), sy + 60 * math.sin(a),
                  stroke=RED, w=4, marker="arrR")
        s += text(cx, sy + 70, f"{ang:+d}°  ({sub})", size=11.5,
                  anchor="middle", weight="bold")

    s += text(W / 2, H - 16,
              "Той самий 1–2 мс RC-сигнал слухає і простий ESC (44.5) — це "
              "десятиліттями спільна «мова» виконавчих механізмів моделей.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.6.3 — Від серво до поверхні: качалка й тяга
# ════════════════════════════════════════════════════════════════════════════
def fig_linkage():
    W, H = 940, 450
    s = header(W, H)
    s += title(W, "Як оберт серво стає відхиленням керма: качалка й тяга",
               "серво повертає важіль → тяга штовхає кермо → поверхня відхиляється")

    # серво ліворуч
    s += rect(80, 220, 90, 70, fill=BOX1, stroke=BLUE, sw=1.6, rx=8)
    s += text(125, 260, "серво", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    # важіль серво (горн)
    hx, hy = 170, 240
    s += circle(hx, hy, 6, fill=INK, stroke="none")
    s += line(hx, hy, hx + 8, hy - 40, stroke=INK, w=4)
    armtop = (hx + 8, hy - 40)
    s += text(150, 200, "качалка серво", size=9.5, fill=INK)

    # крило з кермом праворуч (вид збоку)
    s += poly([(560, 250), (740, 250), (740, 268), (560, 268)], fill="#eef2ff",
              stroke=INK, sw=1.5)
    s += text(650, 244, "крило", size=10, anchor="middle", fill=MUTE)
    # шарнір
    hinge = (740, 259)
    s += circle(hinge[0], hinge[1], 4, fill=RED, stroke="none")
    s += text(752, 250, "шарнір", size=9, fill=RED)
    # кермо (нейтраль)
    s += poly([(740, 252), (810, 252), (810, 266), (740, 266)], fill="#dbe6ff",
              stroke=BLUE, sw=1.5)
    s += text(792, 286, "кермо", size=10, anchor="middle", fill=BLUE)
    # кермо відхилене (вгору й вниз — пунктир)
    s += line(740, 259, 808, 232, stroke=GREEN, w=2.0, dash="5,4")
    s += line(740, 259, 808, 286, stroke=GREEN, w=2.0, dash="5,4")
    s += text(842, 230, "↑ відхилення", size=10, fill=GREEN)
    s += text(842, 290, "↓ відхилення", size=10, fill=GREEN)
    # качалка керма
    chx, chy = 748, 252
    s += line(chx, chy, chx + 6, chy - 36, stroke=INK, w=3)
    chtop = (chx + 6, chy - 36)
    s += text(770, 210, "качалка керма", size=9.5, fill=INK)
    # тяга (пушрод)
    s += line(armtop[0], armtop[1], chtop[0], chtop[1], stroke=AMBER, w=3)
    s += text((armtop[0] + chtop[0]) / 2, armtop[1] - 12, "тяга (пушрод)",
              size=10.5, anchor="middle", fill=AMBER, weight="bold")

    s += rect(80, 330, 780, 56, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += lines(98, 354, [
        "Довжина качалок задає «передачу»: довша качалка серво або коротша качалка керма — більший хід поверхні (throw).",
        "Налаштування ходу й нейтралі (трим) — частина узгодження сигналу з механікою конкретного апарата.",
    ], size=11, lh=20)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.6.4 — Вихідний каскад: від бажаного руху до сигналів виконавцям
# ════════════════════════════════════════════════════════════════════════════
def fig_outputs():
    W, H = 980, 500
    s = header(W, H)
    s += title(W, "Вихідний каскад: бажаний рух → мікшер → сигнал кожному виконавцю",
               "мотори (через ESC) і серво — однакові «виходи»; узгодження = масштаб, реверс, трим")

    # бажаний рух
    s += rect(50, 130, 200, 220, fill=BOX2, stroke=GREEN, sw=1.7, rx=12)
    s += text(150, 156, "Бажаний рух", size=12.5, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(150, 174, "(від керування, 43.1)", size=9.5, anchor="middle",
              fill=MUTE)
    for i, t_ in enumerate(["крен (roll)", "тангаж (pitch)", "курс (yaw)",
                            "загальна тяга"]):
        s += rect(68, 192 + i * 38, 164, 30, fill="white", stroke=GREEN,
                  sw=1.2, rx=7)
        s += text(150, 212 + i * 38, t_, size=11, anchor="middle")

    # мікшер
    s += rect(330, 170, 180, 140, fill=BOX3, stroke=AMBER, sw=1.8, rx=12)
    s += text(420, 220, "МІКШЕР", size=15, weight="bold", anchor="middle",
              fill=AMBER)
    s += text(420, 244, "розкладає за", size=10.5, anchor="middle")
    s += text(420, 260, "геометрією апарата", size=10.5, anchor="middle")
    s += line(250, 240, 328, 240, stroke=INK, w=2.0, marker="arr")

    # виходи
    outs = [(150, "вихід 1 → ESC → мотор", BLUE),
            (210, "вихід 2 → ESC → мотор", BLUE),
            (270, "вихід 3 → серво (елерон)", GREEN),
            (330, "вихід 4 → серво (кермо)", GREEN)]
    s += line(510, 240, 590, 240, stroke=INK, w=2.0, marker="arr")
    for y, t_, col in outs:
        s += rect(590, y - 22, 350, 44, fill="white", stroke=col, sw=1.4, rx=9)
        s += text(606, y - 2, t_, size=11, weight="bold", fill=col)
        s += text(606, y + 15, "узгодження: масштаб · реверс · трим · failsafe",
                  size=9, fill=MUTE)

    s += text(W / 2, H - 16,
              "Приклад мікшування: у «літаючого крила» елевони = елерон + тангаж, "
              "змішані на два серво. Мотори й серво для контролера — просто «виходи».",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.7.1 — Єдині точки відмови (SPOF)
# ════════════════════════════════════════════════════════════════════════════
def fig_spof():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Перше питання надійності: де ЄДИНІ точки відмови?",
               "знайди частини, чия одна поломка валить усе, — і прибери або продублюй їх")

    s += rect(50, 92, 420, 280, fill="#fff0f0", stroke=RED, sw=1.8, rx=12)
    s += text(260, 120, "Часто ЄДИНІ (SPOF)", size=13.5, weight="bold",
              anchor="middle", fill=RED)
    s += text(260, 138, "одна відмова — падає все", size=10, anchor="middle",
              fill=MUTE)
    for i, t_ in enumerate(["Батарея (зазвичай одна)",
                            "Політний контролер (один)",
                            "Регулятор живлення логіки",
                            "Головний джгут / роз'єм"]):
        s += rect(72, 158 + i * 50, 376, 38, fill="white", stroke=RED, sw=1.2,
                  rx=8)
        s += text(86, 182 + i * 50, "✗  " + t_, size=12, fill=INK)

    s += rect(490, 92, 420, 280, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 120, "Зазвичай ДУБЛЮЮТЬ", size=13.5, weight="bold",
              anchor="middle", fill=GREEN)
    s += text(700, 138, "відмова однієї — система живе", size=10,
              anchor="middle", fill=MUTE)
    for i, t_ in enumerate(["IMU  ×2–3 (голосування, 43.2)",
                            "Компас  ×2 · GNSS  ×1–2",
                            "Мотори: 6–8 замість 4",
                            "Топ-системи: 2 контролери / 2 живлення"]):
        s += rect(512, 158 + i * 50, 376, 38, fill="white", stroke=GREEN,
                  sw=1.2, rx=8)
        s += text(526, 182 + i * 50, "✓  " + t_, size=12, fill=INK)

    s += text(W / 2, H - 18,
              "Парадокс: дублювання додає й ваги, і нових деталей, що можуть зламатися. "
              "Тому дублюють не все підряд, а саме вузькі місця — під ставки місії.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.7.2 — Втрата мотора: квадро проти гекса/окто
# ════════════════════════════════════════════════════════════════════════════
def fig_motorloss():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому серйозні апарати беруть 6–8 моторів, а не 4",
               "квадрокоптер не переживає втрати мотора; гекса/окто — переживає")

    def rotor(cx, cy, n, failed_idx, ok):
        o = circle(cx, cy, 16, fill=PANEL, stroke=INK, sw=1.6)
        for k in range(n):
            a = math.radians(90 + k * 360 / n)
            ex, ey = cx + 92 * math.cos(a), cy + 92 * math.sin(a)
            bad = (k == failed_idx)
            o2 = line(cx, cy, ex, ey, stroke=(RED if bad else INK),
                      w=2.6, dash=("4,3" if bad else None))
            o2 += circle(ex, ey, 16, fill=("#fde0e0" if bad else "#eafaef"),
                         stroke=(RED if bad else GREEN), sw=1.8)
            if bad:
                o2 += line(ex - 9, ey - 9, ex + 9, ey + 9, stroke=RED, w=2.2)
                o2 += line(ex - 9, ey + 9, ex + 9, ey - 9, stroke=RED, w=2.2)
            o += o2
        return o

    # квадро
    s += text(245, 100, "Квадрокоптер (4 мотори)", size=13, weight="bold",
              anchor="middle", fill=RED)
    s += rect(60, 116, 370, 250, fill="#fff7f7", stroke=RED, sw=1.4, rx=12)
    s += rotor(245, 220, 4, 1, False)
    s += text(245, 332, "4 мотори = 4 керовані величини.", size=11,
              anchor="middle", fill=INK)
    s += text(245, 350, "Втратив один — нема запасу → падіння.", size=11,
              anchor="middle", fill=RED, weight="bold")

    # гекса/окто
    s += text(715, 100, "Гекса / окто (6–8 моторів)", size=13, weight="bold",
              anchor="middle", fill=GREEN)
    s += rect(530, 116, 370, 250, fill="#f4fbf6", stroke=GREEN, sw=1.4, rx=12)
    s += rotor(715, 220, 6, 2, True)
    s += text(715, 332, "Зайві мотори дають запас тяги й керування.", size=11,
              anchor="middle", fill=INK)
    s += text(715, 350, "Втратив один — летить далі, сідає контрольовано.",
              size=11, anchor="middle", fill=GREEN, weight="bold")

    s += text(W / 2, H - 16,
              "Та сама логіка резервування, що для давачів (43.2), — лише тепер для "
              "виконавців: зайвий мотор коштує ваги, та рятує апарат.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.7.3 — Виявити → вирішити → деградувати
# ════════════════════════════════════════════════════════════════════════════
def fig_fail_pipeline():
    W, H = 980, 460
    s = header(W, H)
    s += title(W, "Поведінка за відмови: виявити → вирішити → деградувати",
               "не можна зреагувати на відмову, якої не помітив, — тому виявлення найважливіше")

    cols = [
        (40, "1. ВИЯВИТИ", BLUE,
         ["перехресна перевірка давачів", "(не згодні між собою?)",
          "телеметрія ESC (мотор став?)", "watchdog (код завис?)",
          "моніторинг струму й температури"]),
        (370, "2. ВИРІШИТИ", AMBER,
         ["який failsafe доречний:", "• перейти на резерв",
          "• повернутись додому (RTL)", "• сісти / планувати",
          "• роззброїти (на землі)"]),
        (700, "3. ДЕГРАДУВАТИ", GREEN,
         ["виконати реакцію:", "втратити трохи можливостей,",
          "а не впасти повністю.", "Зашито заздалегідь (43.2),",
          "а не вигадано в аварії."]),
    ]
    for x, head, col, items in cols:
        s += rect(x, 96, 250, 280, fill="white", stroke=col, sw=1.8, rx=12)
        s += text(x + 125, 126, head, size=13.5, weight="bold", anchor="middle",
                  fill=col)
        s += lines(x + 18, 160, items, size=11, lh=24)
    for x in (290, 620):
        s += line(x, 236, x + 80, 236, stroke=INK, w=2.4, marker="arr")

    s += text(W / 2, H - 16,
              "Добра система не «ламається» — вона помічає негаразд, обирає наперед "
              "задану реакцію й м'яко втрачає частину можливостей.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 44.7.4 — Драбина деградації проти обриву
# ════════════════════════════════════════════════════════════════════════════
def fig_degrade():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Мета — драбина деградації, а не обрив",
               "добра система втрачає по сходинці; крихка — від повної справності одразу до краху")

    s += text(250, 96, "Добра система: драбина", size=13, weight="bold",
              anchor="middle", fill=GREEN)
    steps = [(70, 130, "повна справність"),
             (160, 190, "втратив давач → на резерв"),
             (250, 250, "втратив GNSS → безпечний режим / посадка"),
             (340, 310, "втратив мотор (гекса) → сісти"),
             (430, 370, "безпечна зупинка")]
    prev = None
    for x, y, lab in steps:
        s += rect(x, y, 150, 26, fill="#eafaef", stroke=GREEN, sw=1.5, rx=6)
        if prev:
            s += line(prev[0] + 150, prev[1] + 26, x, y, stroke=GREEN, w=2.0)
        s += text(x + 8, y + 18, lab, size=9.5, fill=INK)
        prev = (x, y)
    s += text(250, 430, "кожна відмова — лише крок униз, апарат живий", size=10.5,
              anchor="middle", fill=GREEN)

    # обрив
    s += text(740, 96, "Крихка система: обрив", size=13, weight="bold",
              anchor="middle", fill=RED)
    s += rect(640, 130, 200, 30, fill="#fff0f0", stroke=RED, sw=1.6, rx=7)
    s += text(740, 150, "повна справність", size=11, anchor="middle")
    s += line(740, 162, 740, 360, stroke=RED, w=3.0, marker="arrR")
    s += text(756, 270, "одна відмова", size=11, fill=RED, weight="bold")
    s += rect(660, 366, 160, 40, fill=RED, stroke=RED, rx=8)
    s += text(740, 391, "КРАХ", size=15, anchor="middle", weight="bold",
              fill="white")

    s += text(W / 2, H - 14,
              "Усе з цього розділу служить одній меті: щоб апарат ішов донизу сходами, "
              "а не падав з обриву від першої ж поломки.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-44-0-1-inversion.svg":     fig_inversion,
    "fig-44-0-2-trilateration.svg": fig_trilateration,
    "fig-44-0-3-relativity.svg":    fig_relativity,
    "fig-44-0-4-sa.svg":            fig_sa,
    "fig-44-1-1-suite.svg":         fig_suite,
    "fig-44-1-2-state.svg":         fig_state,
    "fig-44-1-3-absrel.svg":        fig_absrel,
    "fig-44-1-4-table.svg":         fig_table,
    "fig-44-2-1-specificforce.svg": fig_specificforce,
    "fig-44-2-2-yaw.svg":           fig_yaw,
    "fig-44-2-3-baroprofile.svg":   fig_baroprofile,
    "fig-44-2-4-barodrift.svg":     fig_barodrift,
    "fig-44-2-5-vibration.svg":     fig_vibration,
    "fig-44-3-1-signal.svg":        fig_signal,
    "fig-44-3-2-pseudorange.svg":   fig_pseudorange,
    "fig-44-3-3-ttff.svg":          fig_ttff,
    "fig-44-3-4-dop.svg":           fig_dop,
    "fig-44-3-5-errors.svg":        fig_errors,
    "fig-44-4-1-brushed.svg":       fig_brushed,
    "fig-44-4-2-phases.svg":        fig_phases,
    "fig-44-4-3-kv.svg":            fig_kv,
    "fig-44-4-4-backemf.svg":       fig_backemf,
    "fig-44-4-5-sensorless.svg":    fig_sensorless,
    "fig-44-5-1-jobs.svg":          fig_esc_jobs,
    "fig-44-5-2-inverter.svg":      fig_inverter,
    "fig-44-5-3-protocols.svg":     fig_protocols,
    "fig-44-5-4-telemetry.svg":     fig_esc_telem,
    "fig-44-6-1-servo.svg":         fig_servo,
    "fig-44-6-2-signal.svg":        fig_servo_signal,
    "fig-44-6-3-linkage.svg":       fig_linkage,
    "fig-44-6-4-outputs.svg":       fig_outputs,
    "fig-44-7-1-spof.svg":          fig_spof,
    "fig-44-7-2-motorloss.svg":     fig_motorloss,
    "fig-44-7-3-pipeline.svg":      fig_fail_pipeline,
    "fig-44-7-4-ladder.svg":        fig_degrade,
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
