#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 48 (Модуль 7) — чистий Python, без залежностей.
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
# Рис. 48.0.1 — Картинка як сума хвиль
# ════════════════════════════════════════════════════════════════════════════
def fig_dct_waves():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Картинка як сума хвиль: ідея перетворення",
               "будь-який клаптик зображення можна скласти з простих візерунків-хвиль — від плавних до дрібних")
    s += text(150, 116, "клаптик зображення", size=11, anchor="middle",
              weight="bold")
    px, py, ps = 92, 132, 120
    for r in range(6):
        for c in range(6):
            v = max(0, min(255, 200 - 15 * r - 8 * c))
            s += rect(px + c * (ps / 6), py + r * (ps / 6), ps / 6 + 1,
                      ps / 6 + 1, fill=f"rgb({v},{v},{v})", stroke="none")
    s += rect(px, py, ps, ps, fill="none", stroke=INK, sw=1.5)
    s += text(px + ps + 22, py + ps / 2 + 6, "=", size=20, anchor="middle",
              weight="bold")
    bx = 290
    for i, (lab, sub, freq, wt, col) in enumerate([
            ("плавний", "(низька частота)", 0, "×велика", GREEN),
            ("середній", "", 1, "×середня", AMBER),
            ("дрібний", "(висока частота)", 3, "×мала ≈0", RED)]):
        x = bx + i * 215
        for r in range(6):
            for c in range(6):
                v = max(0, min(255, int(128 + 100 * math.cos((c + 0.5) * math.pi * freq / 6))))
                s += rect(x + c * 16, 140 + r * 16, 17, 17,
                          fill=f"rgb({v},{v},{v})", stroke="none")
        s += rect(x, 140, 96, 96, fill="none", stroke=col, sw=1.6)
        s += text(x + 48, 252, lab, size=9.5, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 48, 265, sub, size=8.5, anchor="middle", fill=MUTE)
        s += text(x + 48, 285, wt, size=10, anchor="middle", weight="bold",
                  fill=col)
        if i < 2:
            s += text(x + 108, 190, "+", size=18, anchor="middle",
                      weight="bold")
    s += text(W / 2, H - 30,
              "Перетворення (DCT) каже, СКІЛЬКИ кожного візерунка в клаптику — "
              "тобто розкладає його на «частоти».", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Плавних візерунків зазвичай багато, дрібних — мало: природні "
              "картинки переважно гладкі.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.0.2 — Чому це стискає
# ════════════════════════════════════════════════════════════════════════════
def fig_dct_compress():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Чому це стискає: лишаємо кілька, відкидаємо решту",
               "після DCT майже вся «енергія» — у кількох низькочастотних числах; дрібні (високочастотні) ≈ 0")
    gx, gy, cell = 110, 132, 30
    for r in range(8):
        for c in range(8):
            v = int(255 * (1 - math.exp(-(r + c) * 0.6)))
            s += rect(gx + c * cell, gy + r * cell, cell - 2, cell - 2,
                      fill=f"rgb({v},{v},{v})", stroke="#e5e7eb", sw=0.6)
    s += rect(gx, gy, 8 * cell, 8 * cell, fill="none", stroke=INK, sw=1.4)
    s += text(gx + 4 * cell, gy - 12, "коефіцієнти DCT (8×8)", size=11,
              anchor="middle", weight="bold")
    s += text(gx - 8, gy + 18, "низькі", size=9, anchor="end", fill=MUTE)
    s += text(gx - 8, gy + 8 * cell - 6, "↓ високі", size=9, anchor="end",
              fill=MUTE)
    s += circle(gx + cell, gy + cell, 16, fill="none", stroke=GREEN, sw=2.2)
    s += text(gx + cell + 30, gy + cell + 4, "← тут уся «суть»", size=10,
              fill="#15803d", weight="bold")
    s += text(gx + 5.5 * cell, gy + 6 * cell, "майже нулі", size=10,
              anchor="middle", fill=RED)
    s += text(gx + 5.5 * cell, gy + 6.7 * cell, "(викидаємо)", size=9,
              anchor="middle", fill=RED)
    s += text(745, 120, "лишаємо кілька великих чисел →", size=11,
              anchor="middle", weight="bold")
    s += rect(620, 140, 110, 110, fill="#dbeafe", stroke=BLUE, sw=1.6, rx=4)
    s += text(675, 200, "оригінал", size=10, anchor="middle", weight="bold")
    s += text(745, 200, "≈", size=20, anchor="middle", weight="bold")
    s += rect(760, 140, 110, 110, fill="#dbeafe", stroke=GREEN, sw=1.6, rx=4)
    s += text(815, 198, "відновлено", size=10, anchor="middle", weight="bold")
    s += text(815, 213, "з кількох чисел", size=8.5, anchor="middle", fill=MUTE)
    s += rect(620, 280, 250, 72, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(745, 306, "було 64 числа → стало кілька", size=10.5,
              anchor="middle", weight="bold", fill="#15803d")
    s += text(745, 326, "і око майже не бачить різниці", size=10,
              anchor="middle", fill=MUTE)
    s += text(745, 343, "(бо викинули лише дрібне)", size=9, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 14,
              "Це й є стиснення «з утратами»: відкидаємо ті частоти, яких "
              "природа дає мало, а око й не помічає.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.0.3 — Шлях ідеї Ахмеда
# ════════════════════════════════════════════════════════════════════════════
def fig_dct_ahmed():
    W, H = 960, 430
    s = header(W, H)
    s += title(W, "«Надто проста» ідея, що стиснула цифровий світ",
               "Насір Ахмед запропонував DCT 1972 року; грант відмовили як «надто просте» — а воно стало всюди")
    ty = 200
    s += line(90, ty, 880, ty, stroke=INK, w=2, marker="arr")
    for x, yr, h, sub, col in [
            (150, "1972", "Ахмед пропонує DCT", "NSF: «надто просто»", RED),
            (340, "1974", "стаття з Натараджаном і Рао", "робочий алгоритм", BLUE),
            (570, "1992", "основа JPEG", "далі — MPEG, H.26x", GREEN),
            (800, "сьогодні", "у кожному фото й відео", "телефон, дрон, стрім", "#b06b00")]:
        s += line(x, ty - 18, x, ty - 6, stroke=MUTE, w=1)
        s += circle(x, ty, 7, fill=AMBER, stroke=INK, sw=1.4)
        s += text(x, ty - 40, yr, size=11, anchor="middle", weight="bold",
                  fill=col)
        s += text(x, ty - 24, h, size=9.5, anchor="middle", weight="bold")
        s += text(x, ty + 26, sub, size=9, anchor="middle", fill=MUTE)
    s += rect(220, 300, 520, 66, fill=BOX3, stroke=AMBER, sw=1.4, rx=10)
    s += text(480, 326, "Один рецензент відкинув ідею як «надто просту».",
              size=11.5, anchor="middle", weight="bold")
    s += text(480, 348,
              "Та саме ця простота й зробила DCT найуживанішим перетворенням в історії техніки.",
              size=10.5, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.0.4 — DCT усюди
# ════════════════════════════════════════════════════════════════════════════
def fig_dct_everywhere():
    W, H = 960, 420
    s = header(W, H)
    s += title(W, "Та сама хвильова цеглинка — у кожному кадрі",
               "DCT — двигун усередині JPEG, MPEG, H.264; кожне фото й відеокадр на твоєму апараті стискає вона")
    s += rect(390, 158, 180, 92, fill=BOX3, stroke=AMBER, sw=2.2, rx=12)
    s += text(480, 192, "DCT (1972)", size=15, anchor="middle", weight="bold",
              fill="#b06b00")
    s += text(480, 214, "пікселі → частоти", size=10.5, anchor="middle",
              fill=MUTE)
    s += text(480, 232, "→ викинути дрібне", size=10.5, anchor="middle",
              fill=MUTE)
    for nm, sub, x, y in [("JPEG", "(фото)", 110, 120),
                          ("MPEG / H.264", "(відео)", 110, 252),
                          ("FPV-стрім", "дрона", 810, 120),
                          ("записаний", "політ", 810, 252)]:
        tx = 388 if x < 480 else 572
        s += line(x + (80 if x < 480 else -80), y, tx, 204, stroke=AMBER,
                  w=1.6, marker="arr", opacity=0.8)
        s += rect(x - 80, y - 26, 160, 54, fill="white", stroke=BLUE, sw=1.6,
                  rx=10)
        s += text(x, y - 4, nm, size=12, anchor="middle", weight="bold",
                  fill=BLUE)
        s += text(x, y + 13, sub, size=9.5, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Розклади на хвилі, відкинь ті, яких мало й яких око не бачить, — "
              "і пожежний шланг (47.5) влазить у вузьку трубу.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.1.1 — Прірва
# ════════════════════════════════════════════════════════════════════════════
def fig_the_gap():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Прірва: сире відео не влазить у канал чи картку",
               "потік із камери — гігабіти за секунду, а реальна труба — десятки мегабіт; розрив у сотні разів")
    s += rect(80, 130, 200, 150, fill="#fde2e2", stroke=RED, sw=2.0, rx=12)
    s += text(180, 160, "СИРЕ ВІДЕО", size=13, anchor="middle", weight="bold",
              fill=RED)
    s += text(180, 188, "1080p · 30 fps", size=11, anchor="middle")
    s += text(180, 214, "≈ 1.5 Гбіт/с", size=16, anchor="middle", weight="bold",
              fill=RED)
    s += text(180, 236, "(187 МБ щосекунди)", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(180, 262, "пожежний шланг (47.5)", size=9.5, anchor="middle",
              fill=MUTE, italic=True)
    s += line(286, 205, 360, 205, stroke=INK, w=3, marker="arr")
    s += rect(380, 150, 230, 112, fill=PANEL, stroke=INK, sw=1.6, rx=10)
    s += text(495, 174, "реальна «труба»:", size=11, anchor="middle",
              weight="bold")
    s += lines(400, 198, ["• радіо FPV: ~10–50 Мбіт/с",
                          "• Wi-Fi / мережа: десятки–сотні",
                          "• SD-картка: швидка, та малий обсяг"], size=10,
               lh=20)
    s += rect(660, 150, 230, 112, fill="#fff0d8", stroke=AMBER, sw=2.0, rx=12)
    s += text(775, 184, "РОЗРИВ", size=14, anchor="middle", weight="bold",
              fill="#b06b00")
    s += text(775, 216, "×100–1000", size=20, anchor="middle", weight="bold",
              fill=RED)
    s += text(775, 240, "стільки треба «втиснути»", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 40,
              "Сире відео в сотні разів більше за те, що можна реально передати "
              "чи зберегти.", size=12, anchor="middle", weight="bold")
    s += text(W / 2, H - 18,
              "Вихід один: СТИСНУТИ — викинути все, без чого можна обійтися. "
              "Питання лише, що саме викинути.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.1.2 — Три роди надлишку
# ════════════════════════════════════════════════════════════════════════════
def fig_redundancy():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чому стиснення можливе: відео страшенно надлишкове",
               "у сирому відео тонни повторів — а повтор не треба зберігати двічі; три роди надлишку")
    s += rect(70, 110, 270, 262, fill="white", stroke=BLUE, sw=1.8, rx=12)
    s += text(205, 136, "ПРОСТОРОВИЙ", size=12.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(205, 152, "(у межах кадру)", size=9.5, anchor="middle", fill=MUTE)
    for r in range(8):
        for c in range(8):
            v = max(0, 200 - 9 * r - 6 * c)
            s += rect(110 + c * 20, 170 + r * 16, 20, 16,
                      fill=f"rgb({v},{v},{v})", stroke="none")
    s += text(205, 322, "сусідні пікселі майже однакові", size=9.5,
              anchor="middle", fill=MUTE)
    s += text(205, 342, "→ опиши пляму, не кожну точку", size=9.5,
              anchor="middle", weight="bold", fill=BLUE)
    s += text(205, 360, "(DCT, тема 48.2)", size=9, anchor="middle", fill=MUTE)
    s += rect(355, 110, 270, 262, fill="white", stroke=GREEN, sw=1.8, rx=12)
    s += text(490, 136, "ЧАСОВИЙ", size=12.5, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(490, 152, "(між кадрами)", size=9.5, anchor="middle", fill=MUTE)
    for i, dx in enumerate([0, 18]):
        fx = 380 + i * 120
        s += rect(fx, 174, 100, 80, fill="#dbeafe", stroke=INK, sw=1.2, rx=4)
        s += circle(fx + 30 + dx, 214, 10, fill=AMBER, stroke=INK, sw=1)
        s += text(fx + 50, 268, f"кадр {i + 1}", size=9, anchor="middle",
                  fill=MUTE)
    s += text(490, 322, "сусідні кадри майже однакові", size=9.5,
              anchor="middle", fill=MUTE)
    s += text(490, 342, "→ зберігай лише те, що ЗМІНИЛОСЬ", size=9.5,
              anchor="middle", weight="bold", fill="#15803d")
    s += text(490, 360, "(міжкадрове, тема 48.3)", size=9, anchor="middle",
              fill=MUTE)
    s += rect(640, 110, 250, 262, fill="white", stroke=AMBER, sw=1.8, rx=12)
    s += text(765, 136, "ПЕРЦЕПТИВНИЙ", size=12.5, anchor="middle",
              weight="bold", fill="#b06b00")
    s += text(765, 152, "(око не бачить)", size=9.5, anchor="middle", fill=MUTE)
    s += circle(765, 196, 18, fill="white", stroke=INK, sw=1.6)
    s += circle(765, 196, 7, fill=INK, stroke="none")
    s += lines(662, 232, ["око слабке до:", "• дрібного кольору (47.3)",
                          "• тонкої деталі/шуму (47.4)"], size=10, lh=19)
    s += text(765, 322, "що око й не помітить —", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(765, 342, "→ можна сміливо ВИКИНУТИ", size=9.5, anchor="middle",
              weight="bold", fill="#b06b00")
    s += text(765, 360, "(стиснення «з утратами»)", size=9, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 14,
              "Стиснення — це полювання на надлишок: усе, що повторюється чи "
              "непомітне, зберігати не варто.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.1.3 — Без утрат vs з утратами
# ════════════════════════════════════════════════════════════════════════════
def fig_lossless_vs_lossy():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Без утрат чи з утратами: дві стратегії",
               "без утрат — точна копія, та стиск скромний; з утратами — викидаємо непомітне, стиск у рази більший")
    s += rect(70, 120, 380, 150, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(260, 148, "БЕЗ УТРАТ (lossless)", size=13, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(92, 174, ["• точно відновлює оригінал (як zip)",
                         "• лише пакує повтори розумніше",
                         "• стиск скромний: ~2× для зображень"], size=10.5,
               lh=22)
    s += text(260, 252, "де треба ТОЧНІСТЬ: код, текст, медкадри", size=10,
              anchor="middle", fill=MUTE)
    s += rect(510, 120, 380, 150, fill="#eafaef", stroke=GREEN, sw=1.8, rx=12)
    s += text(700, 148, "З УТРАТАМИ (lossy)", size=13, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(532, 174, ["• свідомо викидає непомітне (DCT)",
                          "• відновлене ≈ оригінал, не точно",
                          "• стиск великий: 10–100× і більше"], size=10.5,
               lh=22)
    s += text(700, 252, "де важить РОЗМІР: фото, відео, FPV", size=10,
              anchor="middle", fill=MUTE)
    s += text(170, 308, "наочно (умовно):", size=10.5, weight="bold")
    s += rect(170, 320, 600, 22, fill="#e5e7eb", stroke="none", rx=4)
    s += text(778, 336, "сире", size=10, fill=MUTE)
    s += rect(170, 348, 300, 18, fill=BLUE, stroke="none", rx=4, opacity=0.7)
    s += text(478, 362, "без утрат ~½", size=10, fill=BLUE, weight="bold")
    s += rect(170, 372, 40, 18, fill=GREEN, stroke="none", rx=4, opacity=0.8)
    s += text(218, 386, "з утратами ~1/20", size=10, fill="#15803d",
              weight="bold")
    s += text(W / 2, H - 14,
              "Відео майже завжди стискають З УТРАТАМИ: інакше пожежний шланг не "
              "приборкати. Питання — скільки якості віддати.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.1.4 — Пиши лише нове
# ════════════════════════════════════════════════════════════════════════════
def fig_principle():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Головний принцип: зберігай лише НОВЕ",
               "не пиши те, що можна передбачити з уже відомого; пиши тільки несподіванку — звідси й уся вигода")
    s += rect(80, 130, 200, 112, fill=BOX1, stroke=BLUE, sw=1.7, rx=11)
    s += text(180, 158, "ПЕРЕДБАЧЕННЯ", size=12, anchor="middle", weight="bold",
              fill=BLUE)
    s += lines(180 - 70, 182, ["з уже відомого:", "сусідні пікселі,",
                               "попередній кадр"], size=10, lh=17, anchor="start")
    s += text(310, 182, "−", size=20, anchor="middle", weight="bold")
    s += rect(340, 130, 180, 112, fill=PANEL, stroke=INK, sw=1.7, rx=11)
    s += text(430, 158, "РЕАЛЬНІСТЬ", size=12, anchor="middle", weight="bold")
    s += text(430, 186, "що насправді", size=10, anchor="middle", fill=MUTE)
    s += text(430, 202, "в кадрі", size=10, anchor="middle", fill=MUTE)
    s += text(548, 182, "=", size=20, anchor="middle", weight="bold")
    s += rect(575, 130, 200, 112, fill="#eafaef", stroke=GREEN, sw=1.9, rx=11)
    s += text(675, 158, "НЕСПОДІВАНКА", size=12, anchor="middle", weight="bold",
              fill="#15803d")
    s += lines(675 - 70, 182, ["лише різниця —", "мала, добре", "стискається"],
               size=10, lh=17, anchor="start")
    s += text(805, 182, "→ це й", size=10, fill=MUTE)
    s += text(805, 197, "пишемо", size=10, fill=MUTE, weight="bold")
    s += rect(150, 288, 660, 70, fill="#fff0d8", stroke=AMBER, sw=1.5, rx=10)
    s += text(480, 312,
              "Типові стиски: фото JPEG ~10×, відео H.264 ~50–200× (бо ще й кадри схожі між собою).",
              size=11, anchor="middle", weight="bold")
    s += text(480, 334,
              "Саме тому 1.5-гігабітний потік (47.5) ужимається до десятків мегабіт — і влазить у канал.",
              size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Передбач відоме, запиши лише несподіване — це й є душа всякого "
              "стиснення, від DCT до міжкадрового.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.2.1 — Конвеєр JPEG
# ════════════════════════════════════════════════════════════════════════════
def fig_jpeg_pipeline():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Конвеєр JPEG: як стиснути один кадр",
               "ріжемо на блоки 8×8 → DCT (на частоти) → квантування (округлити, тут утрати) → зигзаг + пакування")
    steps = [("кадр", "ріжемо на", "блоки 8×8", BLUE),
             ("DCT", "пікселі →", "частоти", AMBER),
             ("кванту-", "вання", "(утрати!)", RED),
             ("зигзаг +", "паку-", "вання", GREEN),
             ("крихітний", "файл", "", INK)]
    x = 70
    for i, (a, b, c, col) in enumerate(steps):
        s += rect(x, 160, 150, 110, fill="white", stroke=col, sw=1.8, rx=11)
        s += text(x + 75, 192, a, size=12.5, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 75, 214, b, size=10.5, anchor="middle")
        s += text(x + 75, 232, c, size=10.5, anchor="middle", fill=MUTE)
        if i < 4:
            s += line(x + 152, 215, x + 168, 215, stroke=INK, w=2.2,
                      marker="arr")
        x += 172
    s += text(70 + 2 * 172 + 75, 290, "↑ ТУТ губимо (з утратами)", size=10,
              anchor="middle", fill=RED, weight="bold")
    s += text(70 + 3 * 172 + 75, 290, "↑ лише пакуємо (без утрат)", size=10,
              anchor="middle", fill="#15803d")
    s += rect(150, 330, 660, 56, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 354,
              "Уся «магія» — у квантуванні: воно й викидає непомітне, і дає головний стиск.",
              size=11.5, anchor="middle", weight="bold")
    s += text(480, 374,
              "Решта — чесна перепаковка (DCT нічого не втрачає, зигзаг і пакування теж).",
              size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Кожен блок 8×8 проходить конвеєр незалежно — тому JPEG так і "
              "ділить кадр на квадратики.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.2.2 — Квантування
# ════════════════════════════════════════════════════════════════════════════
def fig_jpeg_quantize():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Квантування: тут і ховаються стиснення й утрати",
               "коефіцієнти DCT ділять на таблицю й округлюють — високі частоти стають нулями")

    def coef(r, c):
        return int(120 * math.exp(-(r + c) * 0.55) * (1 if (r + c) % 2 == 0 else -1))

    def quant(r, c):
        return int(round(coef(r, c) / (2 + (r + c) * 3)))

    def grid(x0, y0, title_, valfn, col):
        out = text(x0 + 105, y0 - 10, title_, size=11, anchor="middle",
                   weight="bold", fill=col)
        for r in range(6):
            for c in range(6):
                v = valfn(r, c)
                out += rect(x0 + c * 35, y0 + r * 30, 33, 28, fill="white",
                            stroke="#e5e7eb", sw=0.8)
                out += text(x0 + c * 35 + 16, y0 + r * 30 + 19, str(v),
                            size=8.5, anchor="middle",
                            fill=(INK if v != 0 else "#cbd5e1"))
        out += rect(x0, y0, 6 * 35 - 2, 6 * 30 - 2, fill="none", stroke=col,
                    sw=1.4)
        return out
    s += grid(70, 132, "коефіцієнти DCT", coef, BLUE)
    s += line(282, 200, 332, 200, stroke=INK, w=2, marker="arr")
    s += text(307, 184, "÷ таблиця", size=10, anchor="middle", weight="bold")
    s += text(307, 222, "+ округлити", size=10, anchor="middle", weight="bold")
    s += grid(360, 132, "після квантування", quant, GREEN)
    s += text(700, 175, "майже все = 0", size=12, anchor="middle",
              weight="bold", fill=RED)
    s += text(700, 195, "(особливо високі частоти)", size=9.5, anchor="middle",
              fill=MUTE)
    s += lines(700 - 90, 228, ["грубіше ділення →", "більше нулів →"], size=10.5,
               lh=18, anchor="start")
    s += text(700, 266, "менший файл, та блочніше", size=10.5, anchor="middle",
              weight="bold", fill="#b06b00")
    s += rect(600, 290, 200, 56, fill=BOX3, stroke=AMBER, sw=1.5, rx=10)
    s += text(700, 314, "це і є «ЯКІСТЬ»", size=12, anchor="middle",
              weight="bold", fill="#b06b00")
    s += text(700, 332, "у налаштуваннях JPEG", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 14,
              "Квантування — єдиний крок «з утратами»: воно зануляє дрібні "
              "частоти, яких око не бачить, і цим стискає найдужче.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.2.3 — Зигзаг
# ════════════════════════════════════════════════════════════════════════════
def fig_jpeg_zigzag():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Зигзаг: вишикувати нулі в чергу",
               "коефіцієнти читають зигзагом від низьких частот до високих — тоді всі нулі збираються в хвіст")
    gx, gy, cell = 110, 122, 34
    for r in range(8):
        for c in range(8):
            nz = (r + c) <= 2
            s += rect(gx + c * cell, gy + r * cell, cell - 2, cell - 2,
                      fill="#dbeafe" if nz else "white", stroke="#e5e7eb",
                      sw=0.8)
            if not nz:
                s += text(gx + c * cell + 15, gy + r * cell + 20, "0", size=9,
                          anchor="middle", fill="#cbd5e1")
    order = []
    for sd in range(15):
        cells = [(r, sd - r) for r in range(8) if 0 <= sd - r < 8]
        if sd % 2 == 0:
            cells = cells[::-1]
        order += cells
    pts = [(gx + c * cell + cell / 2 - 1, gy + r * cell + cell / 2 - 1)
           for r, c in order]
    s += poly(pts, fill="none", stroke=RED, sw=1.6, closed=False)
    s += circle(pts[0][0], pts[0][1], 4, fill=GREEN, stroke=INK, sw=1)
    s += text(gx + 4 * cell, gy - 12, "8×8 коефіцієнти + зигзаг", size=11,
              anchor="middle", weight="bold")
    s += text(gx + 2 * cell, gy + 8 * cell + 16, "низькі (суть)", size=9.5,
              anchor="middle", fill=BLUE)
    s += text(gx + 6 * cell, gy + 8 * cell + 16, "→ високі (нулі)", size=9.5,
              anchor="middle", fill=MUTE)
    s += text(620, 152, "вийде послідовність:", size=11, weight="bold")
    s += rect(610, 166, 300, 38, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6)
    s += text(760, 190, "120, −69, 40, 8, −3, 0,0,…,0", size=11,
              anchor="middle", weight="bold")
    s += lines(610, 236, ["→ довгий хвіст нулів пакують",
                          "  «кодом довжин серій» (RLE)",
                          "→ а тоді — кодом Гаффмана",
                          "  (оптимально, без утрат)"], size=10.5, lh=19)
    s += rect(610, 322, 300, 30, fill=BOX2, stroke=GREEN, sw=1.4, rx=8)
    s += text(760, 342, "64 числа → кілька байтів", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(W / 2, H - 14,
              "Зигзаг недарма: він жене нулі в один хвіст, який пакується майже "
              "задарма. Звідси й величезний стиск.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.2.4 — Артефакти JPEG
# ════════════════════════════════════════════════════════════════════════════
def fig_jpeg_artifacts():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Ручка якості й артефакти JPEG",
               "сильніше стиснення — менший файл, та видно блоки 8×8 і «дзвін» біля різких меж")

    def scene(x0, label, blocky, col, size_txt):
        out = text(x0 + 90, 110, label, size=12, anchor="middle", weight="bold",
                   fill=col)
        out += rect(x0, 124, 180, 150, fill="#0f172a", stroke=INK, sw=1.4, rx=4)
        if not blocky:
            out += circle(x0 + 90, 199, 50, fill="#93c5fd", stroke="none")
        else:
            for r in range(6):
                for c in range(6):
                    cx, cy = x0 + 15 + c * 25, 134 + r * 23
                    if ((cx - (x0 + 90)) ** 2 + (cy - 199) ** 2) ** 0.5 < 56:
                        v = max(60, 210 - int(((cx - (x0 + 90)) ** 2 + (cy - 199) ** 2) ** 0.5 * 1.4))
                        out += rect(cx, cy, 24, 22, fill=f"rgb({v},{min(255, v + 40)},255)",
                                    stroke="#1e293b", sw=0.5)
        out += text(x0 + 90, 292, size_txt, size=11, anchor="middle",
                    weight="bold", fill=col)
        return out
    s += scene(120, "ВИСОКА якість", False, GREEN, "великий файл, гладко")
    s += scene(420, "НИЗЬКА якість", True, RED, "малий файл, видно БЛОКИ 8×8")
    s += rect(660, 124, 230, 150, fill="#fde2e2", stroke=RED, sw=1.5, rx=11)
    s += text(775, 150, "артефакти стиснення", size=11, anchor="middle",
              weight="bold", fill=RED)
    s += lines(676, 174, ["• «блочність»: межі 8×8", "  квадратиків стають видні",
                          "• «дзвін» (ringing): хвильки", "  біля різких контурів",
                          "• колір ще й «розмазаний»", "  (chroma subsampling)"],
               size=9.5, lh=17)
    s += rect(120, 320, 720, 56, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 344,
              "Для машинного бачення (49) артефакти небезпечні: блочність і дзвін творять фальшиві «краї» й кольори,",
              size=10.5, anchor="middle", weight="bold")
    s += text(480, 363,
              "яких у сцені нема. Тому для зору не тиснуть надміру — або беруть менш стиснений потік.",
              size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "«Якість» JPEG — це грубість квантування: ти сам вирішуєш, скільки "
              "блочності стерпіти заради меншого файлу.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.3.1 — Сусідні кадри схожі
# ════════════════════════════════════════════════════════════════════════════
def fig_frames_similar():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Сусідні кадри майже однакові — шли лише різницю",
               "за 1/30 секунди світ майже не змінюється; навіщо слати весь кадр, коли рухається дрібка?")

    def frame(x0, label, bx):
        out = text(x0 + 90, 110, label, size=12, anchor="middle", weight="bold")
        out += rect(x0, 124, 180, 120, fill="#1e293b", stroke=INK, sw=1.4, rx=4)
        out += rect(x0 + 4, 200, 172, 40, fill="#334155", stroke="none")
        out += circle(x0 + 150, 150, 14, fill="#fbbf24", stroke="none")
        out += circle(x0 + bx, 185, 11, fill="#60a5fa", stroke="none")
        return out
    s += frame(70, "кадр N", 40)
    s += text(262, 188, "→", size=20, anchor="middle", weight="bold")
    s += frame(282, "кадр N+1", 70)
    s += text(560, 110, "РІЗНИЦЯ (що змінилось)", size=12, anchor="middle",
              weight="bold", fill=GREEN)
    s += rect(470, 124, 180, 120, fill="#0f172a", stroke=GREEN, sw=1.8, rx=4)
    s += circle(470 + 40, 185, 11, fill="none", stroke=RED, sw=1.5)
    s += circle(470 + 70, 185, 11, fill="#60a5fa", stroke="none", opacity=0.8)
    s += text(560, 262, "майже все ЧОРНЕ (нуль) — змінилась лиш дрібка",
              size=10, anchor="middle", fill=MUTE)
    s += line(660, 184, 700, 184, stroke=INK, w=2, marker="arr")
    s += rect(710, 150, 180, 70, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(800, 176, "слати лише це", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += text(800, 196, "→ у рази менше даних", size=10, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 30,
              "Замість цілого кадру щоразу — лише те, що відрізняється від "
              "попереднього. Це часовий надлишок (48.1).", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Так відео ужимається не в десятки (як JPEG), а в СОТНІ разів.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.3.2 — I-кадри й P-кадри
# ════════════════════════════════════════════════════════════════════════════
def fig_iframe_pframe():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "I-кадри й P-кадри: опорний знімок плюс зміни",
               "I — повний кадр (як JPEG); P — лише зміна від попереднього (крихітний); послідовність I-P-P-P…")
    seq = [("I", 1.0, GREEN), ("P", 0.22, BLUE), ("P", 0.16, BLUE),
           ("P", 0.25, BLUE), ("P", 0.14, BLUE), ("P", 0.20, BLUE),
           ("I", 1.0, GREEN), ("P", 0.18, BLUE)]
    x0, step, base, maxh = 90, 98, 300, 150
    s += text(x0 + 3.5 * step, 132, "група кадрів (GOP): I-P-P-P-…-I", size=12,
              anchor="middle", weight="bold")
    for i, (t, frac, col) in enumerate(seq):
        x = x0 + i * step
        h = maxh * frac
        s += rect(x, base - h, 60, h, fill=col, stroke=INK, sw=1.3, rx=4,
                  opacity=0.7)
        s += text(x + 30, base + 20, t, size=15, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + 30, base - h - 8, "повний" if t == "I" else "зміна",
                  size=8.5, anchor="middle", fill=MUTE)
        if i < len(seq) - 1:
            s += line(x + 62, base + 14, x + step - 2, base + 14, stroke=MUTE,
                      w=1.2, marker="arr")
    s += text(x0 + 30, base + 46, "↑ опора (велика)", size=9.5, anchor="middle",
              fill="#15803d", weight="bold")
    s += text(x0 + 3 * step + 30, base + 46, "P крихітні (лише різниці)",
              size=9.5, anchor="middle", fill=BLUE, weight="bold")
    s += rect(150, 360, 660, 56, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 384,
              "I-кадр — самодостатній (як JPEG), великий. P-кадри спираються на попередній — крихітні.",
              size=10.5, anchor="middle", weight="bold")
    s += text(480, 403,
              "Бітрейт «стрибає» на кожному I-кадрі — звідси й поштовхи затримки на вузькому каналі.",
              size=9.5, anchor="middle", fill=MUTE)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.3.3 — Компенсація руху
# ════════════════════════════════════════════════════════════════════════════
def fig_motion():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Компенсація руху: «блок переїхав» замість «новий блок»",
               "кодувальник помічає, що шматок просто зсунувся — пише вектор руху + крихітну поправку")
    s += text(180, 110, "кадр N", size=12, anchor="middle", weight="bold")
    s += rect(90, 124, 180, 150, fill="#1e293b", stroke=INK, sw=1.4, rx=4)
    s += rect(110, 150, 40, 40, fill="#f59e0b", stroke="white", sw=1.4)
    s += text(130, 175, "блок", size=9, anchor="middle", fill="white",
              weight="bold")
    s += line(280, 199, 396, 199, stroke=INK, w=1.5, marker="arr")
    s += text(490, 110, "кадр N+1", size=12, anchor="middle", weight="bold")
    s += rect(400, 124, 180, 150, fill="#1e293b", stroke=INK, sw=1.4, rx=4)
    s += rect(420, 150, 40, 40, fill="none", stroke="#64748b", sw=1.2,
              dash="4,3")
    s += rect(470, 200, 40, 40, fill="#f59e0b", stroke="white", sw=1.4)
    s += line(440, 170, 488, 218, stroke=RED, w=2.2, marker="arrR")
    s += text(545, 200, "вектор", size=9, fill=RED, weight="bold")
    s += text(545, 213, "руху", size=9, fill=RED, weight="bold")
    s += rect(640, 150, 260, 130, fill=BOX2, stroke=GREEN, sw=1.6, rx=11)
    s += text(770, 176, "що зберігаємо:", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(660, 200, ["• вектор руху: «+5, +5»", "  (кілька байтів!)",
                          "• крихітна поправка-залишок",
                          "  (що не збіглося після зсуву)"], size=10, lh=19)
    s += text(W / 2, H - 30,
              "Не «ось новий блок» (дорого), а «візьми старий і посунь сюди» "
              "(дешево). Це й є компенсація руху —", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "найрозумніша частина відеостиснення: вона ловить рух камери й "
              "об'єктів майже задарма.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.3.4 — Розмазування й I-кадри
# ════════════════════════════════════════════════════════════════════════════
def fig_propagation():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Чому потрібні періодичні I-кадри",
               "втратив P-кадр — помилка «розмазується» по наступних, аж доки I-кадр не скине все наново")
    seq = ["I", "P", "P", "P", "P", "P", "I", "P", "P"]
    x0, step, y, corrupt = 80, 96, 200, 2
    for i, t in enumerate(seq):
        x = x0 + i * step
        if t == "I":
            err = 0
        elif i == corrupt:
            err = 0.28
        elif corrupt < i < 6:
            err = min(1.0, (i - corrupt) * 0.28)
        else:
            err = 0
        col = GREEN if t == "I" else (RED if err > 0 else BLUE)
        s += rect(x, y - 50, 64, 64, fill="#1e293b", stroke=col, sw=2.0, rx=5)
        for k in range(int(err * 8) + (1 if err > 0 else 0)):
            s += rect(x + 6 + (k * 7) % 52, y - 44 + (k * 9) % 52, 8, 8,
                      fill="#f87171", stroke="none", opacity=0.8)
        s += text(x + 32, y + 30, t, size=13, anchor="middle", weight="bold",
                  fill=col)
        if i == corrupt:
            s += text(x + 32, y - 58, "✗ збій", size=9, anchor="middle",
                      fill=RED, weight="bold")
        if i == 6:
            s += text(x + 32, y - 58, "✓ скид", size=9, anchor="middle",
                      fill=GREEN, weight="bold")
        if i < len(seq) - 1:
            s += line(x + 66, y - 18, x + step - 2, y - 18, stroke=MUTE, w=1)
    s += text(x0 + 4 * step, y + 56, "помилка наростає (розмазується) →",
              size=10, anchor="middle", fill=RED, weight="bold")
    s += text(x0 + 6 * step + 32, y + 56, "I чистить", size=10, anchor="middle",
              fill="#15803d", weight="bold")
    s += rect(120, 320, 720, 70, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 346,
              "Що рідші I-кадри — то менший бітрейт, але довше «гоїться» збій (артефакти тримаються до I).",
              size=10.5, anchor="middle", weight="bold")
    s += text(480, 368,
              "Тому в FPV часто роблять I-кадри частими (швидше відновлення) або всі кадри I (без розмазування).",
              size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Ось чому цифрове FPV «розмазується» при завадах (47.6): ланцюг "
              "P-кадрів несе помилку, доки не прийде I.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.4.1 — MJPEG vs H.264
# ════════════════════════════════════════════════════════════════════════════
def fig_mjpeg_vs_h264():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "MJPEG проти H.264: дві філософії кодека",
               "MJPEG — кожен кадр окремий JPEG (усі I); H.264 — I + P + B з компенсацією руху")

    def row(y, label, sub, types, col_lab):
        out = text(70, y - 4, label, size=14, weight="bold", fill=col_lab)
        out += text(70, y + 14, sub, size=9, fill=MUTE)
        x = 240
        for t, frac, col in types:
            out += rect(x, y - 30, 56, 50, fill="#1e293b", stroke=col, sw=1.8,
                        rx=4)
            out += text(x + 28, y + 1, t, size=14, anchor="middle",
                        weight="bold", fill=col)
            out += rect(x + 4, y + 30, 8 + 48 * frac, 8, fill=col, stroke="none",
                        opacity=0.8, rx=3)
            x += 84
        return out
    s += row(155, "MJPEG", "(усі — повні I)", [("I", 1, GREEN)] * 7, BLUE)
    s += text(610, 200,
              "кожен кадр самостійний → стійко, низький лаг, просто; та ВЕЛИКО (стиск ~JPEG)",
              size=10, anchor="middle", fill="#15803d")
    s += row(310, "H.264", "(I+P+B, рух)",
             [("I", 1, GREEN), ("P", 0.22, BLUE), ("P", 0.16, BLUE),
              ("B", 0.10, "#9333ea"), ("P", 0.20, BLUE), ("P", 0.14, BLUE),
              ("I", 1, GREEN)], "#b06b00")
    s += text(610, 355,
              "P/B крихітні (лише зміни) → дуже КОМПАКТНО; та складно, лаг, крихко (залежність)",
              size=10, anchor="middle", fill="#b06b00")
    s += text(W / 2, H - 14,
              "Той самий DCT усередині — різниця в тому, чи використати ще й "
              "СХОЖІСТЬ КАДРІВ.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.4.2 — Компроміси
# ════════════════════════════════════════════════════════════════════════════
def fig_codec_tradeoffs():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Компроміси: за все платиться",
               "MJPEG виграє простотою, затримкою, стійкістю; H.264 — стиском (а отже, смугою й місцем)")
    s += rect(430, 110, 250, 34, fill=BOX1, stroke=BLUE, sw=1.2, rx=6)
    s += text(555, 132, "MJPEG", size=12, anchor="middle", weight="bold",
              fill=BLUE)
    s += rect(690, 110, 250, 34, fill=BOX3, stroke=AMBER, sw=1.2, rx=6)
    s += text(815, 132, "H.264", size=12, anchor="middle", weight="bold",
              fill="#b06b00")
    rows = [("стиск / розмір файлу", "✗ слабкий (~10×)", "✓ потужний (50–200×)"),
            ("затримка (лаг)", "✓ низька (просто)", "✗ вища (кодувати важче)"),
            ("стійкість до завад", "✓ кожен кадр окремий", "✗ збій «розмазується»"),
            ("обчислення / енергія", "✓ легко (як JPEG)", "✗ важко (рух, B)"),
            ("простота / монтаж", "✓ кожен кадр — ключ", "✗ декодувати ланцюг")]
    y = 152
    for crit, mj, h2 in rows:
        s += text(72, y + 27, crit, size=10.5, weight="bold")
        s += rect(430, y, 250, 44,
                  fill=("#eafaef" if mj.startswith("✓") else "#fde2e2"),
                  stroke="#e5e7eb", sw=1, rx=6)
        s += text(555, y + 27, mj, size=9.5, anchor="middle",
                  fill=("#15803d" if mj.startswith("✓") else RED))
        s += rect(690, y, 250, 44,
                  fill=("#eafaef" if h2.startswith("✓") else "#fde2e2"),
                  stroke="#e5e7eb", sw=1, rx=6)
        s += text(815, y + 27, h2, size=9.5, anchor="middle",
                  fill=("#15803d" if h2.startswith("✓") else RED))
        y += 52
    s += text(W / 2, H - 14,
              "Нема «кращого» — є придатний під задачу: MJPEG за стійкість і "
              "простоту, H.264 за компактність.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.4.3 — Де що ставлять
# ════════════════════════════════════════════════════════════════════════════
def fig_codec_where():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Де що ставлять",
               "MJPEG — де важить стійкість, проста обробка, незалежні кадри; H.264 — де дорога смуга й місце")
    s += rect(70, 120, 390, 250, fill=BOX1, stroke=BLUE, sw=1.9, rx=12)
    s += text(265, 148, "MJPEG / intra-only", size=13.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(92, 178, ["• МАШИННЕ БАЧЕННЯ (49): кожен кадр",
                         "  незалежний, без артефактів передбач.",
                         "• низьколатентний стійкий FPV",
                         "• прості/дешеві камери, реєстратори",
                         "• коли треба легко різати/гортати",
                         "  (кожен кадр — ключовий)"], size=10.5, lh=24)
    s += rect(500, 120, 390, 250, fill=BOX3, stroke=AMBER, sw=1.9, rx=12)
    s += text(695, 148, "H.264 / H.265 / AV1", size=13.5, anchor="middle",
              weight="bold", fill="#b06b00")
    s += lines(522, 178, ["• ЗАПИС польоту (місце на картці)",
                          "• стрім по мережі / у хмару",
                          "• HD-FPV у вузькому каналі (DJI тощо)",
                          "• будь-де, де смуга й пам'ять дорогі,",
                          "  а обчислень і дрібки лагу не шкода",
                          "• споживче відео загалом"], size=10.5, lh=24)
    s += text(W / 2, H - 14,
              "Машинне бачення любить MJPEG (чисті незалежні кадри); передача й "
              "запис — H.264. Часто на дроні — обидва, для різних потоків.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.4.4 — Драбина кодеків
# ════════════════════════════════════════════════════════════════════════════
def fig_codec_ladder():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Драбина кодеків: щораз тісніше, та складніше",
               "MJPEG → H.264 → H.265/AV1: кожне покоління тисне вдвічі краще, але вимагає вдвічі більше обчислень")
    bx = [120, 330, 540, 750]
    labels = [("MJPEG", "усі I (~10×)", "просто", GREEN),
              ("H.264 (2003)", "I+P+B (~50–200×)", "складніше", BLUE),
              ("H.265 (2013)", "≈×2 до H.264", "важче + роялті", AMBER),
              ("AV1 (2018)", "≈H.265, БЕЗ роялті", "найважче", GREEN)]
    base = 360
    for i, (t, sub, note, col) in enumerate(labels):
        x = bx[i]
        h = 80 + i * 55
        s += rect(x, base - h, 160, h, fill=col, stroke=INK, sw=1.6, rx=8,
                  opacity=0.18)
        s += rect(x, base - h, 160, 4, fill=col, stroke="none")
        s += text(x + 80, base - h + 24, t, size=12, anchor="middle",
                  weight="bold", fill=col)
        s += text(x + 80, base - h + 42, sub, size=9, anchor="middle")
        s += text(x + 80, base - h + 58, note, size=8.5, anchor="middle",
                  fill=MUTE)
    s += line(105, base, 930, base, stroke=INK, w=1.5)
    s += text(110, base + 18, "стиск →", size=10, fill=MUTE, weight="bold")
    s += text(930, base + 18, "більше обчислень →", size=10, anchor="end",
              fill=MUTE, weight="bold")
    s += text(W / 2, H - 14,
              "«Закон» кодеків: кожне покоління ~вдвічі компактніше, та ~вдвічі "
              "ненажерливіше до обчислень. На дроні це впирається в чип і затримку.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.5.1 — Трикутник компромісу
# ════════════════════════════════════════════════════════════════════════════
def fig_trilemma():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Трикутник компромісу: якість ↔ бітрейт ↔ затримка",
               "три ручки тягнуть одна одну — задаси дві, третя визначиться сама; усіх трьох найкращих не буває")
    A, B, C = (300, 170), (120, 390), (480, 390)
    s += poly([A, B, C], fill="#eef2ff", stroke=INK, sw=2.2, closed=True)
    s += circle(A[0], A[1], 7, fill=GREEN, stroke=INK, sw=1.3)
    s += circle(B[0], B[1], 7, fill=BLUE, stroke=INK, sw=1.3)
    s += circle(C[0], C[1], 7, fill=AMBER, stroke=INK, sw=1.3)
    s += text(300, 154, "ЯКІСТЬ", size=13, anchor="middle", weight="bold",
              fill="#15803d")
    s += text(108, 412, "БІТРЕЙТ", size=13, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(492, 412, "ЗАТРИМКА", size=13, anchor="middle", weight="bold",
              fill="#b06b00")
    s += text(300, 300, "обери 2 —", size=11.5, anchor="middle", weight="bold")
    s += text(300, 317, "третя слідом", size=11.5, anchor="middle",
              weight="bold")
    s += rect(560, 140, 360, 300, fill=PANEL, stroke=INK, sw=1.4, rx=12)
    s += text(740, 168, "правило трьох ручок", size=12, anchor="middle",
              weight="bold")

    def rule(y, col, head, body):
        o = circle(584, y - 4, 6, fill=col, stroke=INK, sw=1)
        o += text(600, y, head, size=10.5, weight="bold", fill=col)
        o += text(600, y + 17, body, size=9.8, fill=INK)
        return o
    s += rule(204, GREEN, "Хочеш ЯКІСТЬ?", "плати бітрейтом або затримкою")
    s += rule(258, BLUE, "Канал тисне БІТРЕЙТ?", "ріж якість або додай буфер (лаг)")
    s += rule(312, AMBER, "Треба мала ЗАТРИМКА?", "стиск гірший → якість чи біти")
    s += rect(584, 350, 312, 72, fill="#eef2ff", stroke=BLUE, sw=1.3, rx=9)
    s += text(740, 372, "Найчастіше канал ЗАДАЄ бітрейт,", size=10,
              anchor="middle", weight="bold")
    s += text(740, 390, "і тоді ти торгуєш якість ↔ затримку:", size=10,
              anchor="middle")
    s += text(740, 408, "тонший стиск — краще, але повільніше.", size=10,
              anchor="middle", fill=MUTE)
    s += text(W / 2, H - 16,
              "Це не вада техніки, а закон: біти, краса й миттєвість не бувають "
              "найкращими разом.", size=11, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.5.2 — Крива «біти за якість» (rate-distortion)
# ════════════════════════════════════════════════════════════════════════════
def fig_rate_distortion():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Біти за якість: крива з насиченням",
               "квантування (48.2) — головна ручка: грубше → менше біт і гірше; тонше → більше біт; вище — все менший зиск")
    ox, oy, ey = 130, 370, 120
    s += line(ox, oy, 890, oy, stroke=INK, w=1.6, marker="arr")
    s += line(ox, oy, ox, ey, stroke=INK, w=1.6, marker="arr")
    s += text(885, oy + 22, "бітрейт (Мбіт/с) →", size=10.5, anchor="end",
              fill=MUTE, weight="bold")
    s += text(ox + 6, ey - 6, "↑ якість", size=10.5, fill=MUTE, weight="bold")
    pts = [(130, 370), (175, 312), (235, 262), (315, 222), (415, 194),
           (535, 174), (680, 162), (840, 156)]
    s += poly(pts, fill="none", stroke=BLUE, sw=2.8, closed=False)
    s += circle(175, 312, 5, fill=RED, stroke=INK, sw=1)
    s += text(192, 314, "мало біт: блочно, артефакти (48.2)", size=9.5, fill=RED)
    s += circle(315, 222, 6.5, fill=GREEN, stroke=INK, sw=1.3)
    s += text(332, 214, "«коліно»: розумний вибір", size=10, fill="#15803d",
              weight="bold")
    s += text(332, 230, "(найбільше якості за біт)", size=9, fill="#15803d")
    s += circle(680, 162, 5, fill=MUTE, stroke=INK, sw=1)
    s += text(680, 140, "багато біт: зиск дрібніє", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(680, 152, "(око вже не бачить різниці)", size=8.5,
              anchor="middle", fill=MUTE)
    s += rect(560, 250, 336, 104, fill="#f8fafc", stroke=INK, sw=1.3, rx=10)
    s += text(728, 274, "CBR ↔ VBR: дві стратегії бітрейту", size=10.5,
              anchor="middle", weight="bold")
    s += lines(578, 296, ["• CBR (сталий): біти фіксовані, якість",
                          "  гуляє — для вузького каналу/ефіру",
                          "• VBR (змінний): якість фіксована, біти",
                          "  стрибають — для запису (на каналі",
                          "  треба буфер → затримка)"], size=9.3, lh=15.5)
    s += text(W / 2, H - 14,
              "Перша половина біт дає майже всю якість; решта — лише шліфує. "
              "Тому коліно кривої — найвигідніша точка.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.5.3 — Звідки береться затримка (glass-to-glass)
# ════════════════════════════════════════════════════════════════════════════
def fig_latency_pipeline():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Звідки береться затримка: від скла до скла",
               "захоплення → кодування → буфер → канал → буфер → декодування → екран; кожна ланка додає мілісекунди")
    stages = [("Сенсор", ["захоплення"], BLUE),
              ("Кодек", ["рух, B-кадри,", "lookahead"], AMBER),
              ("Буфер TX", ["згладити", "сплески"], AMBER),
              ("Канал", ["радіо /", "мережа"], BLUE),
              ("Буфер RX", ["згладити", "джитер"], AMBER),
              ("Декодер", ["зібрати", "ланцюг"], BLUE),
              ("Екран", ["показ"], GREEN)]
    n, x0, bw, gap = len(stages), 40, 110, 18
    for i, (t, dl, col) in enumerate(stages):
        x = x0 + i * (bw + gap)
        s += rect(x, 150, bw, 92, fill="#0f172a", stroke=col, sw=1.9, rx=8)
        s += text(x + bw / 2, 175, t, size=11.5, anchor="middle",
                  weight="bold", fill=col)
        for j, d in enumerate(dl):
            s += text(x + bw / 2, 200 + j * 15, d, size=8.8, anchor="middle",
                      fill="#cbd5e1")
        if i < n - 1:
            s += line(x + bw, 196, x + bw + gap, 196, stroke=MUTE, w=1.6,
                      marker="arr")
    s += text(x0 + 1.5 * (bw + gap), 268, "↑ фіксовані ланки", size=9,
              anchor="middle", fill=BLUE)
    s += text(x0 + 2.0 * (bw + gap), 284, "↑ де ховається лаг (кодек + буфери)",
              size=9.5, anchor="middle", fill="#b06b00", weight="bold")
    s += rect(80, 310, 800, 100, fill="#fef9c3", stroke=AMBER, sw=1.5, rx=11)
    s += text(W / 2, 332, "Щоб зрізати затримку — жертвують стиском:", size=11,
              anchor="middle", weight="bold", fill="#92400e")
    s += lines(150, 354, ["• B-кадри геть (не чекати «майбутніх» кадрів)",
                          "• intra-важко / малий GOP (менше залежностей)"],
               size=9.8, lh=18)
    s += lines(540, 354, ["• малий буфер (терпіти джитер, не копити лаг)",
                          "• проста (швидка) обробка замість «розумної»"],
               size=9.8, lh=18)
    s += text(W / 2, H - 14,
              "B-кадри й буфери дають кращий стиск, але «думають» наперед — а це "
              "час. Менша затримка завжди коштує стиску.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.5.4 — Три апарати, три кути
# ════════════════════════════════════════════════════════════════════════════
def fig_profiles():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Три апарати — три кути трикутника",
               "гонка тягне за затримку, далекобій — за бітрейт/дальність, кінозйомка — за якість; кожен жертвує рештою")
    cards = [
        ("ГОНОЧНИЙ FPV", RED, "цар — ЗАТРИМКА (<30 мс)",
         ["• миттєвість понад усе", "• жертва: чіткість, дальність",
          "• intra-важко, малий буфер", "• аналог або DJI low-latency",
          "  (720p120, <28 мс)"]),
        ("ДАЛЕКОБІЙ / HD-лінк", BLUE, "тиск — БІТРЕЙТ / ДАЛЬНІСТЬ",
         ["• канал вузький на відстані", "• тисне сильно (H.265)",
          "• терпить десятки мс лагу", "• якість — під залишок смуги",
          "• приклад: HD-FPV на дальності"]),
        ("КІНОЗЙОМКА / ЗАПИС", GREEN, "цар — ЯКІСТЬ",
         ["• не наживо → лаг байдужий", "• B-кадри, великий буфер",
          "• VBR, високий бітрейт", "• макс. деталь і колір",
          "• пишемо на картку (48.4)"]),
    ]
    cw, x0, gap = 280, 40, 20
    for i, (t, col, king, rows) in enumerate(cards):
        x = x0 + i * (cw + gap)
        s += rect(x, 120, cw, 300, fill=PANEL, stroke=col, sw=2.0, rx=12)
        s += rect(x, 120, cw, 38, fill=col, stroke="none", rx=10, opacity=0.16)
        s += text(x + cw / 2, 144, t, size=13, anchor="middle", weight="bold",
                  fill=col)
        s += text(x + cw / 2, 180, king, size=10.5, anchor="middle",
                  weight="bold")
        s += lines(x + 20, 210, rows, size=10, lh=24)
    s += text(W / 2, H - 16,
              "Той самий кодек, різні налаштування: «найкращого» нема — є "
              "налаштований під місію апарата.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.6.1 — Дві дороги (аналог vs цифра)
# ════════════════════════════════════════════════════════════════════════════
def fig_two_paths():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Дві дороги з борту на землю",
               "аналог — відео просто на радіохвилі (миттєво, грубо); цифра — стиснений потік пакетами (HD, та з лагом)")

    def lane(y, label, col, boxes, hop_after, note):
        out = text(48, y - 52, label, size=12.5, weight="bold", fill=col)
        bw, bh, x = 138, 54, 48
        for i, txt in enumerate(boxes):
            if i > 0:
                g = 64 if (i - 1) == hop_after else 18
                if (i - 1) == hop_after:
                    cxm = x + g / 2
                    out += text(cxm, y - 14, ")))", size=13, anchor="middle",
                                weight="bold", fill=col)
                    out += text(cxm, y - 3, "ефір", size=8, anchor="middle",
                                fill=col)
                    out += line(x, y, x + g, y, stroke=col, w=1.7, marker="arr")
                else:
                    out += line(x, y, x + g, y, stroke=MUTE, w=1.4, marker="arr")
                x += g
            out += rect(x, y - bh / 2, bw, bh, fill="#0f172a", stroke=col,
                        sw=1.7, rx=7)
            parts = txt.split("|")
            for j, ln in enumerate(parts):
                out += text(x + bw / 2, y + 5 + (j - (len(parts) - 1) / 2) * 14,
                            ln, size=8.8, anchor="middle", fill="#e2e8f0")
            x += bw
        out += text(48, y + 50, note, size=9.5, fill=MUTE)
        return out
    s += lane(155, "АНАЛОГОВЕ FPV", BLUE,
              ["Камера", "Відеосигнал|яскр.+синхро", "Модулятор|5.8 ГГц",
               "Демодул.|+ окуляри"], 2,
              "без стиску, без пакетів → майже нульова затримка; та грубо й односторонньо")
    s += lane(330, "ЦИФРОВА МЕРЕЖА", AMBER,
              ["Камера", "Стиск|H.264", "Пакети", "Радіо / IP",
               "Збір+декод|+ екран"], 3,
              "HD, шифрування, маршрут в інтернет; та лаг (кодек+буфер) і складність")
    s += text(W / 2, H - 14,
              "Аналог кладе відео ПРОСТО на хвилю; цифра спершу стискає й "
              "пакетує. Звідси й усі їхні відмінності.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.6.2 — Аналогове FPV
# ════════════════════════════════════════════════════════════════════════════
def fig_analog_fpv():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Аналогове FPV: відео просто на несучій хвилі",
               "композитний відеосигнал (яскравість+синхро, як у 47) модулює радіонесучу ~5.8 ГГц; приймач демодулює — й на окуляри")
    boxes = ["Камера", "Композитне|відео", "Модулятор|несуча 5.8 ГГц",
             "Приймач|демодулятор", "Окуляри"]
    bw, bh, y, x = 150, 50, 138, 26
    hop_after = 2
    for i, t in enumerate(boxes):
        if i > 0:
            g = 60 if (i - 1) == hop_after else 14
            if (i - 1) == hop_after:
                cxm = x + g / 2
                s += text(cxm, y - 12, ")))", size=12, anchor="middle",
                          weight="bold", fill=BLUE)
                s += text(cxm, y - 1, "ефір", size=7.5, anchor="middle",
                          fill=BLUE)
                s += line(x, y, x + g, y, stroke=BLUE, w=1.7, marker="arr")
            else:
                s += line(x, y, x + g, y, stroke=MUTE, w=1.4, marker="arr")
            x += g
        s += rect(x, y - bh / 2, bw, bh, fill="#0f172a", stroke=BLUE, sw=1.7,
                  rx=7)
        parts = t.split("|")
        for j, ln in enumerate(parts):
            s += text(x + bw / 2, y + 5 + (j - (len(parts) - 1) / 2) * 14, ln,
                      size=8.8, anchor="middle", fill="#e2e8f0")
        x += bw
    # composite-video waveform inset
    s += rect(60, 190, 330, 70, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=8)
    s += text(225, 208, "сигнал одного рядка: синхро + яскравість", size=9,
              anchor="middle", weight="bold")
    wf = [(78, 240), (96, 240), (96, 252), (118, 252), (118, 226), (140, 220),
          (162, 232), (184, 218), (206, 228), (228, 220), (250, 230),
          (272, 222), (294, 232), (316, 226), (338, 240), (372, 240)]
    s += poly(wf, fill="none", stroke=BLUE, sw=1.8, closed=False)
    # 5.8 GHz channel band
    s += rect(420, 190, 480, 70, fill="#eef2ff", stroke=BLUE, sw=1.3, rx=8)
    s += text(660, 208, "діапазон 5.8 ГГц · ~40 каналів (пілоти ділять ефір)",
              size=9.5, anchor="middle", weight="bold")
    for k in range(10):
        cx = 444 + k * 46
        col = RED if k == 4 else "#94a3b8"
        s += rect(cx, 224, 30, 22, fill=(col if k == 4 else "#cbd5e1"),
                  stroke="#64748b", sw=0.8, rx=3, opacity=0.9)
    s += text(444 + 4 * 46 + 15, 238, "твій", size=8, anchor="middle",
              fill="white", weight="bold")
    # pros / cons
    s += rect(60, 296, 410, 116, fill="#eafaef", stroke=GREEN, sw=1.6, rx=11)
    s += text(265, 318, "за що люблять", size=11, anchor="middle",
              weight="bold", fill="#15803d")
    s += lines(80, 340, ["• майже нульова затримка (нема кодека/буфера)",
                         "• плавне згасання на краю дальності",
                         "• просто й дешево; легко ділити канали"], size=9.8,
               lh=22)
    s += rect(490, 296, 410, 116, fill="#fde2e2", stroke=RED, sw=1.6, rx=11)
    s += text(695, 318, "чим платять", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += lines(510, 340, ["• низька роздільність, шум, завади",
                          "• односторонньо, без шифрування",
                          "• фіксована смуга каналу (не HD)"], size=9.8, lh=22)
    s += text(W / 2, H - 14,
              "Аналог не стискає й не пакетує — просто кладе відеохвилю на "
              "несучу. Звідси і його миттєвість, і його грубість.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.6.3 — Плавно vs обрив
# ════════════════════════════════════════════════════════════════════════════
def fig_graceful_vs_cliff():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Плавно чи з обриву: як гасне картинка на краю дальності",
               "аналог тьмяніє поступово (сніг, та ще летиш); цифра тримається ідеально — і раптом обривається в стоп-кадр")
    ox, oy, top = 110, 350, 110
    s += line(ox, oy, 770, oy, stroke=INK, w=1.6, marker="arr")
    s += line(ox, oy, ox, top, stroke=INK, w=1.6, marker="arr")
    s += text(765, oy + 22, "слабшання сигналу / відстань →", size=10,
              anchor="end", fill=MUTE, weight="bold")
    s += text(ox + 6, top - 4, "↑ якість картинки", size=10, fill=MUTE,
              weight="bold")
    dig = [(110, 134), (330, 134), (450, 138), (485, 150), (505, 348)]
    s += poly(dig, fill="none", stroke=AMBER, sw=2.8, closed=False)
    ana = [(110, 150), (210, 164), (320, 194), (430, 234), (540, 280),
           (650, 320), (745, 344)]
    s += poly(ana, fill="none", stroke=BLUE, sw=2.8, closed=False)
    s += text(150, 126, "ЦИФРА — з обриву", size=11, fill="#b06b00",
              weight="bold")
    s += circle(505, 250, 5, fill=RED, stroke=INK, sw=1)
    s += text(520, 246, "«обрив»: ідеально… і раптом", size=9.5, fill=RED,
              weight="bold")
    s += text(520, 260, "стоп-кадр / розсип квадратів", size=9.5, fill=RED,
              weight="bold")
    s += text(300, 210, "АНАЛОГ — плавно", size=11, fill=BLUE, weight="bold")
    s += text(610, 300, "сніг росте, але видно", size=9.5, fill=BLUE)
    s += text(620, 314, "→ є запас і попередження", size=9.5, fill=BLUE)
    # thumbnails: frozen-blocks (digital) and snow (analog)
    s += rect(540, 150, 50, 36, fill="#0f172a", stroke=RED, sw=1.4, rx=3)
    for bx, by, bc in [(545, 155, "#ef4444"), (565, 155, "#3b82f6"),
                       (545, 170, "#22c55e"), (567, 168, "#eab308")]:
        s += rect(bx, by, 18, 14, fill=bc, stroke="none", opacity=0.8)
    s += rect(690, 300, 50, 36, fill="#0f172a", stroke=BLUE, sw=1.4, rx=3)
    for i in range(26):
        dx = 693 + (i * 37) % 44
        dy = 303 + (i * 53) % 30
        s += rect(dx, dy, 2, 2, fill="#e2e8f0", stroke="none")
    s += rect(110, 378, 740, 64, fill="#fffbeb", stroke=AMBER, sw=1.4, rx=10)
    s += text(480, 400,
              "Сучасні цифрові системи пом'якшують обрив: адаптивний бітрейт "
              "(падає якість, не зв'язок) і FEC (відновлення втрат).", size=10,
              anchor="middle", weight="bold", fill="#92400e")
    s += text(480, 420,
              "Та сам обрив нікуди не дівається — за порогом декодер просто не "
              "збере кадр. Тому в цифрі важливо знати, де «обрив».", size=9.5,
              anchor="middle", fill="#92400e")
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.6.4 — Пакети й мережа
# ════════════════════════════════════════════════════════════════════════════
def fig_packets_network():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Цифрова мережа: відео як потік пакетів",
               "стиснений потік ріжуть на пакети (номер + заголовок); втрата пакета — збій до наступного I-кадру (48.3)")
    s += text(70, 118, "стиснений бітпотік (48.4):", size=10.5, weight="bold")
    s += rect(70, 126, 360, 22, fill="#1e293b", stroke=INK, sw=1, rx=4)
    s += text(250, 141, "…011010110100011101001…", size=10, anchor="middle",
              fill="#93c5fd")
    s += line(250, 150, 250, 178, stroke=MUTE, w=1.2, marker="arr")
    s += text(330, 168, "ріжемо на пакети", size=9.5, fill=MUTE)
    pk = [("#1", GREEN), ("#2", GREEN), ("#3", RED), ("#4", GREEN), ("P", AMBER)]
    x = 70
    for lbl, col in pk:
        s += rect(x, 186, 64, 40, fill="#0f172a", stroke=col, sw=1.8, rx=6)
        s += rect(x, 186, 64, 12, fill=col, stroke="none", opacity=0.30)
        s += text(x + 32, 211, lbl, size=12, anchor="middle", weight="bold",
                  fill=col)
        x += 74
    s += text(70 + 2 * 74 + 32, 242, "✗ загубився", size=8.5, anchor="middle",
              fill=RED, weight="bold")
    s += text(70 + 4 * 74 + 32, 242, "FEC: латає", size=8.5, anchor="middle",
              fill="#b06b00", weight="bold")
    s += text(70, 262, "кожен пакет = номер + заголовок (адреса) + шматок відео",
              size=9.5, fill=MUTE)
    s += rect(500, 116, 400, 152, fill=PANEL, stroke=INK, sw=1.3, rx=10)
    s += text(700, 138, "наживо → UDP, не TCP", size=11, anchor="middle",
              weight="bold")
    s += lines(518, 160, ["• UDP: шлемо й не перепитуємо — спізнілий",
                          "  кадр уже непотрібний (краще пропустити)",
                          "• TCP: гарантує доставку, та перепити =",
                          "  затримка → для відео наживо погано",
                          "• втрати латає FEC (надлишок) — без",
                          "  зворотного запиту, тож без зайвого лагу"],
               size=9.3, lh=17)
    s += rect(70, 300, 405, 116, fill=BOX1, stroke=BLUE, sw=1.7, rx=11)
    s += text(272, 322, "локальний радіолінк (точка-точка)", size=10.5,
              anchor="middle", weight="bold", fill=BLUE)
    s += lines(90, 344, ["• OcuSync / HDZero / Walksnail",
                         "• борт ↔ пульт напряму",
                         "• малий лаг, та обмежена дальність"], size=9.8,
               lh=21)
    s += rect(495, 300, 405, 116, fill=BOX3, stroke=AMBER, sw=1.7, rx=11)
    s += text(697, 322, "IP-мережа (LTE/5G → інтернет)", size=10.5,
              anchor="middle", weight="bold", fill="#b06b00")
    s += lines(515, 344, ["• відео в хмару й будь-куди (BVLOS)",
                          "• багато апаратів, далеко за обрій",
                          "• та лаг мережі й залежність від покриття"],
               size=9.8, lh=21)
    s += text(W / 2, H - 14,
              "Пакети дають HD, шифрування й маршрут хоч на інший континент — "
              "ціною затримки та «обриву» при втратах.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.7.1 — Бітрейт під стелею смуги
# ════════════════════════════════════════════════════════════════════════════
def fig_bitrate_vs_bandwidth():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Пропускна здатність: бітрейт мусить улізти під стелю",
               "канал несе обмежено біт/с, і ця «стеля» падає з відстанню; відеобітрейт має йти ПІД нею, з запасом — інакше затори й втрати")
    ox, oy, top = 110, 370, 120
    s += poly([(110, 160), (820, 340), (820, 370), (110, 370)], fill="#dbeafe",
              stroke="none", closed=True)
    s += poly([(465, 250), (820, 250), (820, 340)], fill="#fecaca",
              stroke="none", closed=True)
    s += line(ox, oy, 850, oy, stroke=INK, w=1.6, marker="arr")
    s += line(ox, oy, ox, top, stroke=INK, w=1.6, marker="arr")
    s += text(845, oy + 22, "відстань / завади →", size=10, anchor="end",
              fill=MUTE, weight="bold")
    s += text(ox + 6, top - 4, "↑ біт/с", size=10, fill=MUTE, weight="bold")
    s += line(110, 160, 820, 340, stroke=BLUE, w=2.8)
    s += text(150, 148, "стеля = доступна смуга", size=10, fill=BLUE,
              weight="bold")
    s += text(150, 163, "(падає з відстанню/завадами)", size=8.5, fill=BLUE)
    s += line(110, 250, 820, 250, stroke=RED, w=2.2)
    s += text(118, 242, "сталий бітрейт", size=9.5, fill=RED, weight="bold")
    s += circle(465, 250, 5, fill=RED, stroke=INK, sw=1)
    s += text(470, 238, "тут бітрейт переріс смугу", size=9.5, fill=RED,
              weight="bold")
    s += text(690, 296, "ЗАТОРИ · ВТРАТИ", size=11, anchor="middle", fill=RED,
              weight="bold")
    s += line(110, 178, 820, 356, stroke=GREEN, w=2.4)
    s += text(210, 205, "адаптивний (повзе під стелею)", size=9.5, fill="#15803d",
              weight="bold")
    s += text(W / 2, H - 14,
              "Золоте правило: бітрейт — нижче найгіршої смуги, із запасом. "
              "Адаптивний кодек сам сповзає за стелею; аналог цього не вміє.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.7.2 — Втрата пакета
# ════════════════════════════════════════════════════════════════════════════
def fig_packet_loss():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Коли пакет зникає",
               "пакети гублять зіткнення, слабкий сигнал, затори, переповнення буфера; втрата відеопакета — збій до наступного I-кадру (48.3)")
    causes = ["зіткнення", "слабкий сигнал", "затор у каналі", "переповнений буфер"]
    x = 70
    for c in causes:
        s += rect(x, 116, 180, 34, fill="#fef2f2", stroke=RED, sw=1.2, rx=7)
        s += text(x + 90, 138, c, size=10, anchor="middle", fill=RED,
                  weight="bold")
        x += 200
    pk = [1, 1, 0, 1, 1, 1]
    x0 = 300
    for i, ok in enumerate(pk):
        x = x0 + i * 60
        if ok:
            s += rect(x, 182, 46, 30, fill="#0f172a", stroke=BLUE, sw=1.6, rx=5)
            s += text(x + 23, 202, "#" + str(i + 1), size=9, anchor="middle",
                      fill="#93c5fd")
        else:
            s += rect(x, 182, 46, 30, fill="none", stroke=RED, sw=1.6, rx=5,
                      dash="4,3")
            s += text(x + 23, 204, "✗", size=15, anchor="middle", fill=RED,
                      weight="bold")
    s += text(x0 + 2 * 60 + 23, 228, "загублено", size=8.5, anchor="middle",
              fill=RED, weight="bold")
    s += text(300, 248, "→ збій у картинці, доки не прийде I-кадр (48.3)",
              size=9.5, fill=MUTE)
    resp = [("FEC — надлишок", GREEN,
             ["шлемо зайві пакети,", "приймач сам відновить", "загублене",
              "ПЛАТА: смуга"]),
            ("ARQ — перепит", AMBER,
             ["просимо надіслати", "пакет ще раз", "(зворотний запит)",
              "ПЛАТА: затримка"]),
            ("Терпіти", RED,
             ["лишаємо збій,", "ловимо наступний", "I-кадр",
              "ПЛАТА: якість"])]
    x = 70
    for t, col, rows in resp:
        s += rect(x, 278, 270, 150, fill=PANEL, stroke=col, sw=1.8, rx=11)
        s += text(x + 135, 302, t, size=11.5, anchor="middle", weight="bold",
                  fill=col)
        s += lines(x + 24, 328, rows, size=10, lh=24)
        x += 300
    s += text(W / 2, H - 14,
              "Втрату гасять смугою (FEC), затримкою (перепит) або якістю "
              "(терпіти) — задарма пакет не повернеш.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.7.3 — Джитер і буфер
# ════════════════════════════════════════════════════════════════════════════
def fig_jitter_buffer():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Джитер і буфер: згладити нерівний прихід",
               "пакети шлють рівно, та мережа доправляє їх нерівно (джитер); буфер тримає кілька — щоб відтворення йшло гладко")
    s += text(60, 150, "Надіслано (рівно):", size=10.5, weight="bold")
    for i in range(8):
        s += rect(250 + i * 70, 138, 16, 24, fill=BLUE, stroke=INK, sw=1, rx=3)
    s += text(60, 220, "Прийшло (джитер):", size=10.5, weight="bold")
    jit = [250, 268, 332, 374, 442, 506, 560, 642]
    for x in jit:
        s += rect(x, 208, 16, 24, fill=AMBER, stroke=INK, sw=1, rx=3)
    s += text(730, 222, "нерівно!", size=9.5, fill="#b06b00", weight="bold")
    s += rect(360, 256, 240, 40, fill=PANEL, stroke=GREEN, sw=1.8, rx=8)
    s += text(480, 281, "БУФЕР тримає кілька пакетів", size=10, anchor="middle",
              weight="bold", fill="#15803d")
    s += line(480, 234, 480, 254, stroke=MUTE, w=1.4, marker="arr")
    s += line(480, 298, 480, 320, stroke=MUTE, w=1.4, marker="arr")
    s += text(60, 342, "Відтворення (знов рівно):", size=10.5, weight="bold")
    for i in range(8):
        s += rect(250 + i * 70, 330, 16, 24, fill=GREEN, stroke=INK, sw=1, rx=3)
    s += text(W / 2, H - 30,
              "Буфер всотує нерівність приходу — на виході знов рівний, гладкий "
              "потік.", size=11, anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Ціна — кілька кадрів затримки: пакет чекає в черзі, доки надійде "
              "його мить.", size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 48.7.4 — Глибина буфера: компроміс
# ════════════════════════════════════════════════════════════════════════════
def fig_buffer_tradeoff():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Глибина буфера: гладко чи миттєво",
               "малий буфер — мала затримка, та смикається й губить на джитері; великий — гладко й стійко, та лаг; обирай під місію")
    s += rect(110, 180, 740, 30, fill="#e2e8f0", stroke=INK, sw=1.2, rx=15)
    s += text(112, 166, "малий буфер", size=10.5, weight="bold", fill=RED)
    s += text(848, 166, "великий буфер", size=10.5, anchor="end", weight="bold",
              fill=BLUE)
    s += text(150, 234, "← менша затримка", size=9.5, fill=RED, weight="bold")
    s += text(810, 234, "більша гладкість →", size=9.5, anchor="end", fill=BLUE,
              weight="bold")
    pts = [(200, "Гонка / FPV", "крихітний буфер", "<мс лаг, ризик смикання", RED),
           (480, "Перегляд / стрім", "середній буфер", "гладко, лаг терпимо", AMBER),
           (760, "Хмара / запис", "великий буфер", "дуже гладко, лаг байдужий", BLUE)]
    for x, t, a, b, col in pts:
        s += circle(x, 195, 8, fill=col, stroke=INK, sw=1.3)
        s += line(x, 203, x, 270, stroke=col, w=1.2)
        s += rect(x - 110, 270, 220, 98, fill=PANEL, stroke=col, sw=1.7, rx=11)
        s += text(x, 294, t, size=11, anchor="middle", weight="bold", fill=col)
        s += text(x, 318, a, size=9.8, anchor="middle")
        s += text(x, 340, b, size=9, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Це той самий компроміс, що в 48.5 — буфер просто інший бік ручки "
              "«затримка». Гонка ріже буфер до нуля; хмара його не шкодує.",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-48-0-1-waves.svg":     fig_dct_waves,
    "fig-48-0-2-compress.svg":  fig_dct_compress,
    "fig-48-0-3-ahmed.svg":     fig_dct_ahmed,
    "fig-48-0-4-everywhere.svg": fig_dct_everywhere,
    "fig-48-1-1-the-gap.svg":   fig_the_gap,
    "fig-48-1-2-redundancy.svg": fig_redundancy,
    "fig-48-1-3-lossless-vs-lossy.svg": fig_lossless_vs_lossy,
    "fig-48-1-4-principle.svg": fig_principle,
    "fig-48-2-1-pipeline.svg":  fig_jpeg_pipeline,
    "fig-48-2-2-quantize.svg":  fig_jpeg_quantize,
    "fig-48-2-3-zigzag.svg":    fig_jpeg_zigzag,
    "fig-48-2-4-artifacts.svg": fig_jpeg_artifacts,
    "fig-48-3-1-frames-similar.svg": fig_frames_similar,
    "fig-48-3-2-iframe-pframe.svg": fig_iframe_pframe,
    "fig-48-3-3-motion.svg":    fig_motion,
    "fig-48-3-4-propagation.svg": fig_propagation,
    "fig-48-4-1-mjpeg-vs-h264.svg": fig_mjpeg_vs_h264,
    "fig-48-4-2-tradeoffs.svg": fig_codec_tradeoffs,
    "fig-48-4-3-where.svg":     fig_codec_where,
    "fig-48-4-4-codec-ladder.svg": fig_codec_ladder,
    "fig-48-5-1-trilemma.svg":  fig_trilemma,
    "fig-48-5-2-rate-distortion.svg": fig_rate_distortion,
    "fig-48-5-3-latency.svg":   fig_latency_pipeline,
    "fig-48-5-4-profiles.svg":  fig_profiles,
    "fig-48-6-1-two-paths.svg": fig_two_paths,
    "fig-48-6-2-analog-fpv.svg": fig_analog_fpv,
    "fig-48-6-3-graceful-vs-cliff.svg": fig_graceful_vs_cliff,
    "fig-48-6-4-packets-network.svg": fig_packets_network,
    "fig-48-7-1-bitrate-vs-bandwidth.svg": fig_bitrate_vs_bandwidth,
    "fig-48-7-2-packet-loss.svg": fig_packet_loss,
    "fig-48-7-3-jitter-buffer.svg": fig_jitter_buffer,
    "fig-48-7-4-buffer-tradeoff.svg": fig_buffer_tradeoff,
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
