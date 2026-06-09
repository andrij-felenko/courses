#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 46 (Модуль 7) — чистий Python, без залежностей.
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
# Рис. 46.0.1 — Знати, де ти, із зачиненими очима
# ════════════════════════════════════════════════════════════════════════════
def fig_sealedbox():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Знати, де ти, із зачиненими очима",
               "герметичний апарат без вікон і зв'язку — як визначити своє положення й курс?")
    cx, cy = 480, 250
    s += rect(cx - 115, cy - 55, 230, 110, fill=PANEL, stroke=INK, sw=2.2, rx=16)
    s += text(cx, cy - 16, "ГЕРМЕТИЧНИЙ АПАРАТ", size=13, anchor="middle",
              weight="bold")
    s += text(cx, cy + 5, "субмарина · ракета · літак", size=10.5,
              anchor="middle", fill=MUTE)
    s += text(cx, cy + 28, "лише прилади всередині", size=11, anchor="middle",
              weight="bold", fill=GREEN)
    refs = [(175, 120, "зорі"), (785, 120, "орієнтир"),
            (175, 380, "радіо / GPS"), (785, 380, "карта")]
    for rx, ry, lab in refs:
        s += line(rx, ry, cx, cy, stroke="#e5e7eb", w=1.2, dash="3,4")
        s += circle(rx, ry, 34, fill="white", stroke=MUTE, sw=1.6, dash="4,3")
        s += text(rx, ry + 4, lab, size=11, anchor="middle", fill=MUTE)
        s += line(rx - 26, ry - 26, rx + 26, ry + 26, stroke=RED, w=2.4)
        s += line(rx - 26, ry + 26, rx + 26, ry - 26, stroke=RED, w=2.4)
    s += text(W / 2, H - 40,
              "Жодного зовнішнього орієнтира: ні зір, ні землі, ні радіо.",
              size=12, anchor="middle", weight="bold")
    s += text(W / 2, H - 18,
              "Відповідь — інерціальна навігація: рахувати рух за фізикою, із "
              "самих лише приладів на борту.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.0.2 — Гіроскоп і акселерометр
# ════════════════════════════════════════════════════════════════════════════
def fig_gyroaccel():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Два чуття інерції: гіроскоп і акселерометр",
               "гіроскоп тримає напрям (оберт), акселерометр міряє прискорення → інтегруємо в рух")
    # gyroscope
    gx, gy = 195, 165
    s += circle(gx, gy, 58, fill="white", stroke=INK, sw=1.8)
    s += circle(gx, gy, 40, fill=SKY, stroke=BLUE, sw=1.6)
    s += circle(gx, gy, 7, fill=BLUE, stroke=BLUE)
    s += line(gx - 56, gy, gx + 56, gy, stroke=INK, w=1.3)
    s += line(gx, gy - 56, gx, gy + 56, stroke=INK, w=1.3)
    s += text(gx, gy - 74, "ГІРОСКОП", size=13, anchor="middle", weight="bold")
    s += text(gx, gy + 84, "ротор тримає напрям", size=10.5, anchor="middle",
              fill=MUTE)
    s += text(gx, gy + 99, "→ міряє ОБЕРТ", size=10.5, anchor="middle",
              fill=MUTE)
    # accelerometer
    ax, ay = 470, 165
    s += rect(ax - 58, ay - 45, 116, 90, fill="white", stroke=INK, sw=1.8, rx=10)
    s += coil(ax - 50, ax - 18, ay, n=3, col=MUTE)
    s += rect(ax - 16, ay - 16, 34, 32, fill=AMBER, stroke=INK, sw=1.4, rx=4)
    s += text(ax + 1, ay + 6, "m", size=12, anchor="middle", weight="bold")
    s += coil(ax + 18, ax + 50, ay, n=3, col=MUTE)
    s += text(ax, ay - 74, "АКСЕЛЕРОМЕТР", size=13, anchor="middle",
              weight="bold")
    s += text(ax, ay + 84, "маса на пружинах зміщується", size=10.5,
              anchor="middle", fill=MUTE)
    s += text(ax, ay + 99, "→ міряє ПРИСКОРЕННЯ", size=10.5, anchor="middle",
              fill=MUTE)
    # IMU summary box
    s += rect(700, 120, 210, 92, fill=BOX1, stroke=BLUE, sw=1.7, rx=12)
    s += text(805, 150, "ІНЕРЦІАЛЬНИЙ БЛОК", size=12, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(805, 170, "(IMU, 44.2)", size=10.5, anchor="middle", fill=BLUE)
    s += text(805, 192, "гіро + акселерометр", size=10.5, anchor="middle",
              fill=MUTE)
    # integration chain
    chain = [("прискорення", AMBER), ("швидкість", BLUE), ("положення", GREEN)]
    cxs, cyy = [300, 540, 780], 365
    for i, (lab, col) in enumerate(chain):
        s += rect(cxs[i] - 80, cyy - 26, 160, 52, fill="white", stroke=col,
                  sw=1.8, rx=10)
        s += text(cxs[i], cyy + 5, lab, size=13, anchor="middle", weight="bold",
                  fill=col)
        if i < 2:
            s += line(cxs[i] + 82, cyy, cxs[i + 1] - 82, cyy, stroke=INK, w=2.0,
                      marker="arr")
            s += text((cxs[i] + cxs[i + 1]) / 2, cyy - 12, "∫ dt", size=12,
                      anchor="middle", weight="bold")
    s += text(W / 2, H - 16,
              "Інтегруємо прискорення раз — маємо швидкість, ще раз — положення. "
              "Це «розрахунок шляху» (dead reckoning) із самої фізики.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.0.3 — SPIRE, 1953
# ════════════════════════════════════════════════════════════════════════════
def fig_spire():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "SPIRE, 1953: переліт наосліп через континент",
               "інерціальна система Дрейпера провела бомбардувальник через усю країну — без орієнтирів")
    s += rect(120, 150, 720, 150, fill="#eef2ff", stroke="#c7d2fe", sw=1.6,
              rx=24)
    s += text(480, 142, "США — від океану до океану (~3700 км)", size=10.5,
              anchor="middle", fill=MUTE)
    ex, wx, yy = 800, 180, 225
    pts = [(ex - 12, yy), (660, 198), (540, 242), (420, 206), (wx + 14, yy)]
    for i in range(len(pts) - 1):
        mk = "arrB" if i == len(pts) - 2 else None
        s += line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                  stroke=BLUE, w=2.6, marker=mk)
    s += text(540, 228, "✈", size=18, anchor="middle", fill=BLUE)
    s += circle(ex, yy, 9, fill=GREEN, stroke=INK, sw=1.4)
    s += text(ex, yy - 20, "СТАРТ", size=11, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(ex, yy + 28, "Бедфорд,", size=10, anchor="middle")
    s += text(ex, yy + 42, "Массачусетс", size=10, anchor="middle")
    s += circle(wx, yy, 9, fill=RED, stroke=INK, sw=1.4)
    s += text(wx, yy - 20, "ФІНІШ", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += text(wx, yy + 28, "Лос-", size=10, anchor="middle")
    s += text(wx, yy + 42, "Анджелес", size=10, anchor="middle")
    s += rect(300, 330, 360, 66, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += lines(318, 354, ["Пілот вивів на курс — і передав керування системі.",
                          "SPIRE (~1200 кг) сама вела апарат 12.5 год.",
                          "Док Дрейпер летів на борту, щоб довести: працює."],
               size=10.5, lh=15)
    s += text(W / 2, H - 14,
              "Перший переліт через континент, де курс тримала тільки "
              "інерціальна навігація — без зір, радіо й землі.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.0.4 — Дрейф і виправлення
# ════════════════════════════════════════════════════════════════════════════
def fig_drift_fusion():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Дрейф і виправлення: чому одного давача замало",
               "інерціальна оцінка повзе геть від істини; зовнішній вимір вертає її назад")
    ox, oy, ow, oh = 90, 110, 780, 250
    s += line(ox, oy, ox, oy + oh, stroke=INK, w=1.4)
    s += line(ox, oy + oh, ox + ow, oy + oh, stroke=INK, w=1.4)
    s += text(ox - 8, oy + 4, "похибка", size=10.5, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ox - 8, oy + 18, "оцінки", size=10.5, anchor="end", fill=MUTE)
    s += text(ox + ow, oy + oh + 22, "час →", size=11, anchor="end", fill=MUTE,
              weight="bold")
    base = oy + oh - 20
    s += line(ox, base, ox + ow, base, stroke=GREEN, w=2.2)
    s += text(ox + ow - 4, base + 16, "істина (нульова похибка)", size=10,
              anchor="end", fill=GREEN, weight="bold")
    seg, drift_h = 150, 90
    pts = [(ox, base)]
    fixes = []
    for k in range(5):
        x1 = ox + k * seg + seg
        pts.append((x1, base - drift_h))
        if k < 4:
            fixes.append((x1, base - drift_h))
            pts.append((x1, base - 18))
    s += poly(pts, fill="none", stroke=RED, sw=2.4, closed=False)
    s += text(ox + 60, base - drift_h - 6, "інерціальна оцінка дрейфує",
              size=10.5, fill=RED, weight="bold")
    for fx, fy in fixes:
        s += line(fx, fy, fx, base - 14, stroke=BLUE, w=1.4, dash="3,3")
        s += circle(fx, base - 18, 5, fill=BLUE, stroke=INK, sw=1.2)
    s += text(ox + ow - 130, oy + 26, "● виправлення", size=10.5, fill=BLUE,
              weight="bold")
    s += text(ox + ow - 130, oy + 42, "(зорі / GPS / баро)", size=10, fill=MUTE)
    s += text(W / 2, H - 30,
              "Гіро й акселерометр точні МИТТЄВО, та їхня похибка накопичується; "
              "зовнішній давач точний, але рідкий і шумний.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Звести їх оптимально — і є сенсорний фьюжн; математику цього дав "
              "фільтр Калмана (тема 46.4).", size=11.5, anchor="middle",
              fill=INK, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.1.1 — Кожен давач — свідок зі своєю вадою
# ════════════════════════════════════════════════════════════════════════════
def fig_witnesses():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Кожен давач — свідок зі своєю вадою",
               "у кожного є що сказати — і в кожного свій сліпий кут; нікому самому довіряти не можна")
    cards = [
        (60, 90, "IMU (гіро + акселерометр)", BLUE,
         "швидкий, миттєвий, самодостатній", "ДРЕЙФУЄ — похибка росте щосекунди"),
        (490, 90, "GNSS (GPS)", GREEN,
         "абсолютна позиція, без дрейфу", "повільний, шумний, пропадає (дах, глушилка)"),
        (60, 280, "Барометр", AMBER,
         "висота будь-де, дешево", "шумить і «пливе» з погодою та вітром"),
        (490, 280, "Магнітометр", "#9333ea",
         "курс — де північ", "кривлять мотори, струми, залізо")]
    cw, ch = 410, 150
    for x, y, name, col, good, bad in cards:
        s += rect(x, y, cw, ch, fill="white", stroke=col, sw=2.0, rx=12)
        s += text(x + 18, y + 30, name, size=14, weight="bold", fill=col)
        s += line(x + 18, y + 42, x + cw - 18, y + 42, stroke="#e5e7eb", w=1)
        s += text(x + 20, y + 74, "✓", size=15, weight="bold", fill=GREEN)
        s += text(x + 44, y + 74, good, size=11.5)
        s += text(x + 20, y + 110, "✗", size=15, weight="bold", fill=RED)
        s += text(x + 44, y + 110, bad, size=11.5)
    s += text(W / 2, H - 16,
              "Покладешся на одного — успадкуєш усі його вади. Рятує лише "
              "поєднання багатьох.", size=12, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.1.2 — Слабкість одного — сила іншого
# ════════════════════════════════════════════════════════════════════════════
def fig_complementary():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Слабкість одного — сила іншого",
               "IMU точний миттєво, та дрейфує; GPS повільний, зате не накопичує дрейфу — разом покривають усе")
    colx, barw = [330, 640], 230
    s += text(colx[0] + barw / 2, 92, "МИТТЄВО (зараз)", size=12,
              anchor="middle", weight="bold", fill=MUTE)
    s += text(colx[1] + barw / 2, 92, "НАДОВГО (без дрейфу)", size=12,
              anchor="middle", weight="bold", fill=MUTE)
    rows = [("IMU", BLUE, [0.92, 0.18]), ("GNSS / GPS", GREEN, [0.25, 0.95])]
    yy = 120
    for name, col, vals in rows:
        s += text(110, yy + 34, name, size=15, weight="bold", fill=col)
        for j, v in enumerate(vals):
            bx = colx[j]
            s += rect(bx, yy, barw, 56, fill="#f4f4f5", stroke="#e5e7eb", sw=1,
                      rx=8)
            s += rect(bx, yy, max(barw * v, 10), 56, fill=col, stroke="none",
                      rx=8, opacity=0.85)
            if v > 0.6:
                s += text(bx + 16, yy + 34, "сильно", size=12, weight="bold",
                          fill="white")
            else:
                s += text(bx + max(barw * v, 10) + 10, yy + 34, "слабко",
                          size=12, weight="bold", fill=MUTE)
        yy += 90
    s += text(W / 2, yy + 8,
              "Дзеркало: де IMU сильний — GPS слабкий, і навпаки. Саме тому їх "
              "зводять разом.", size=12, anchor="middle", weight="bold")
    s += text(W / 2, H - 14,
              "Фьюжн бере від кожного сильний бік: швидку реакцію IMU й "
              "стабільну прив'язку GPS.", size=11.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.1.3 — Висота: жоден сам не годиться
# ════════════════════════════════════════════════════════════════════════════
def fig_altitude():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Висота: жоден сам не годиться, разом — точно",
               "баро шумить, GPS-висота відстає, інтеграл акселерометра дрейфує — фьюжн бере найкраще")
    ox, oy, ow, oh = 80, 95, 700, 270
    s += rect(ox, oy, ow, oh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=8)
    s += text(ox - 8, oy + 10, "висота", size=10.5, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ox + ow / 2, oy + oh + 22, "час →", size=11, anchor="middle",
              fill=MUTE)

    def truth(f):
        return 0.30 + 0.5 / (1 + math.exp(-(f - 0.4) * 12))

    def Y(val):
        return oy + oh - val * (oh - 30) - 10
    N = 100
    tp = [(ox + ow * k / N, Y(truth(k / N))) for k in range(N + 1)]
    bp = [(ox + ow * k / N,
           Y(truth(k / N) + 0.035 * math.sin(k * 1.7) + 0.025 * math.sin(k * 0.7 + 1)))
          for k in range(N + 1)]
    s += poly(bp, fill="none", stroke=AMBER, sw=1.3, closed=False, opacity=0.7)
    gp = [(ox + ow * k / N, Y(round((truth(max(0, k / N - 0.08)) - 0.04) * 12) / 12))
          for k in range(N + 1)]
    s += poly(gp, fill="none", stroke=BLUE, sw=1.4, closed=False, opacity=0.6)
    dp = [(ox + ow * k / N, Y(truth(k / N) + 0.0022 * k)) for k in range(N + 1)]
    s += poly(dp, fill="none", stroke=RED, sw=1.4, closed=False, opacity=0.6)
    s += poly(tp, fill="none", stroke=GREEN, sw=3.0, closed=False)
    leg = [("баро (шум)", AMBER), ("GPS-висота (відстає, грубо)", BLUE),
           ("акселерометр (дрейф)", RED), ("ФЬЮЖН (точно й гладко)", GREEN)]
    for i, (lab, col) in enumerate(leg):
        ly = oy + 18 + i * 22
        s += line(ox + 14, ly, ox + 34, ly, stroke=col,
                  w=3 if "ФЬЮЖН" in lab else 2)
        s += text(ox + 40, ly + 4, lab, size=9.5,
                  weight="bold" if "ФЬЮЖН" in lab else "normal")
    s += text(W / 2, H - 14,
              "Кожен окремий слід або шумить, або відстає, або тікає від істини. "
              "Зведені разом — гладка, точна висота.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.1.4 — Багато недосконалих → один стан
# ════════════════════════════════════════════════════════════════════════════
def fig_fusion_concept():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Фьюжн: багато недосконалих → одна довірена оцінка",
               "контролер не вибирає «найкращий» давач, а зводить усі покази в один стан апарата")
    ins = [("IMU", BLUE), ("GPS", GREEN), ("барометр", AMBER),
           ("магнітометр", "#9333ea")]
    for i, (nm, col) in enumerate(ins):
        y = 108 + i * 62
        s += rect(70, y, 150, 46, fill="white", stroke=col, sw=1.7, rx=9)
        s += text(145, y + 28, nm, size=13, anchor="middle", weight="bold",
                  fill=col)
        s += line(224, y + 23, 386, 222, stroke=col, w=1.6, marker="arr",
                  opacity=0.8)
    s += rect(390, 150, 180, 150, fill=BOX1, stroke=INK, sw=2.2, rx=16)
    s += text(480, 205, "ФЬЮЖН", size=18, anchor="middle", weight="bold")
    s += text(480, 230, "(оцінювач стану,", size=11, anchor="middle", fill=MUTE)
    s += text(480, 246, "напр. фільтр Калмана)", size=11, anchor="middle",
              fill=MUTE)
    s += line(572, 225, 700, 225, stroke=INK, w=2.4, marker="arr")
    s += rect(702, 150, 196, 150, fill=BOX2, stroke=GREEN, sw=2.0, rx=14)
    s += text(800, 180, "СТАН АПАРАТА", size=13, anchor="middle", weight="bold",
              fill=GREEN)
    s += lines(720, 210, ["• положення", "• швидкість",
                          "• орієнтація (нахил, курс)"], size=11.5, lh=26)
    s += text(W / 2, H - 16,
              "Одна оцінка, якій можна довіряти, — складена з багатьох, жодному "
              "з яких не можна вірити наодинці.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.2.1 — Передбачення = продовжити рух
# ════════════════════════════════════════════════════════════════════════════
def fig_predict_deadreckon():
    W, H = 960, 430
    s = header(W, H)
    s += title(W, "Передбачення: знаю стан — знаю, де буду за мить",
               "модель руху продовжує стан уперед: нове положення = старе + швидкість × Δt")
    ty = 195
    s += line(80, ty, 880, ty, stroke="#e5e7eb", w=2)
    x0, x1 = 250, 620
    s += line(x0, ty, x1, ty, stroke=GREEN, w=2.2, dash="6,5", marker="arrG")
    s += text((x0 + x1) / 2, ty - 12, "проходить v × Δt", size=11,
              anchor="middle", weight="bold", fill=GREEN)
    s += line(x0, ty - 34, x0 + 90, ty - 34, stroke=BLUE, w=2.4, marker="arrB")
    s += text(x0 + 45, ty - 42, "v", size=13, anchor="middle", weight="bold",
              fill=BLUE)
    s += circle(x0, ty, 11, fill=BLUE, stroke=INK, sw=1.6)
    s += text(x0, ty + 34, "ЗАРАЗ", size=12, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(x0, ty + 52, "положення x, швидкість v", size=10.5,
              anchor="middle", fill=MUTE)
    s += circle(x1, ty, 11, fill="white", stroke=GREEN, sw=2.4)
    s += text(x1, ty + 34, "ЗА Δt", size=12, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(x1, ty + 52, "передбачене положення", size=10.5, anchor="middle",
              fill=MUTE)
    s += rect(300, 296, 360, 56, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(480, 330, "x(t+Δt) = x(t) + v · Δt", size=17, anchor="middle",
              weight="bold")
    s += text(W / 2, H - 14,
              "Це те саме числення шляху (dead reckoning): продовжуємо рух за "
              "відомою фізикою, не чекаючи виміру.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.2.2 — Передбачення заповнює проміжки
# ════════════════════════════════════════════════════════════════════════════
def fig_predict_fillgap():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Передбачення заповнює проміжки між рідкими вимірами",
               "GPS приходить зрідка; модель малює гладку оцінку щомиті між його відліками")
    ox, oy, ow, oh = 80, 100, 800, 220
    s += rect(ox, oy, ow, oh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=8)
    s += text(ox + ow / 2, oy + oh + 24, "час →", size=11, anchor="middle",
              fill=MUTE)
    s += text(ox - 8, oy + 12, "положення", size=10.5, anchor="end", fill=MUTE,
              weight="bold")

    def path(f):
        return oy + oh - 24 - (oh - 56) * (0.12 + 0.72 * f - 0.12 * math.sin(f * 6.0))
    N = 160
    s += poly([(ox + ow * k / N, path(k / N)) for k in range(N + 1)],
              fill="none", stroke=BLUE, sw=2.4, closed=False)
    s += text(ox + 140, path(0.16) - 16, "передбачення (щомиті, гладко)",
              size=10.5, fill=BLUE, weight="bold")
    for i, k in enumerate([0.06, 0.22, 0.38, 0.54, 0.70, 0.86]):
        mx = ox + ow * k
        my = path(k) + (8 if i % 2 else -8)
        s += line(mx, my, mx, path(k), stroke=MUTE, w=1, dash="2,2")
        s += circle(mx, my, 6, fill=GREEN, stroke=INK, sw=1.3)
        s += line(mx, oy + oh, mx, oy + oh + 8, stroke="#cbd5e1", w=1)
    s += text(ox + ow - 12, oy + 22, "● вимір GPS (зрідка)", size=10.5,
              anchor="end", fill=GREEN, weight="bold")
    s += text(W / 2, H - 14,
              "Між повільними відліками GPS апарат не «сліпне»: модель веде "
              "оцінку далі, високим темпом і без ривків.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.2.3 — Невизначеність росте
# ════════════════════════════════════════════════════════════════════════════
def fig_predict_uncertainty():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Модель — наближена: певність тане з кожним кроком",
               "без свіжого виміру передбачення дрейфує, а «хмара» невпевненості розпливається")
    ox, oy, ow, oh = 90, 110, 780, 250
    s += line(ox, oy + oh, ox + ow, oy + oh, stroke=INK, w=1.4)
    s += text(ox + ow, oy + oh + 22, "час без виміру →", size=11, anchor="end",
              fill=MUTE, weight="bold")
    midy = oy + oh - 110

    def cy(f):
        return midy - 20 * math.sin(f * 2.2)

    def spread(f):
        return 8 + 90 * f
    N = 120
    top = [(ox + ow * k / N, cy(k / N) - spread(k / N)) for k in range(N + 1)]
    bot = [(ox + ow * k / N, cy(k / N) + spread(k / N)) for k in range(N + 1)]
    s += poly(top + bot[::-1], fill=RED, stroke="none", opacity=0.12,
              closed=True)
    s += poly(top, fill="none", stroke=RED, sw=1.2, closed=False, opacity=0.5)
    s += poly(bot, fill="none", stroke=RED, sw=1.2, closed=False, opacity=0.5)
    s += poly([(ox + ow * k / N, cy(k / N)) for k in range(N + 1)], fill="none",
              stroke=BLUE, sw=2.6, closed=False)
    s += circle(ox, cy(0), 6, fill=BLUE, stroke=INK, sw=1.3)
    s += text(ox + 8, cy(0) - spread(0) - 12, "щойно після виміру: певно",
              size=10.5, fill=GREEN, weight="bold")
    s += text(ox + ow - 10, cy(1) - spread(1) - 10, "довго без виміру:",
              size=10.5, anchor="end", fill=RED, weight="bold")
    s += text(ox + ow - 10, cy(1) - spread(1) + 5, "хмара розпливлась",
              size=10.5, anchor="end", fill=RED)
    s += text(W / 2, H - 14,
              "Передбачення безкоштовне, та не безкарне: щокроку додається трохи "
              "невизначеності. Тому й потрібен вимір — осадити хмару.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.2.4 — Передбачення — половина циклу
# ════════════════════════════════════════════════════════════════════════════
def fig_predict_step():
    W, H = 960, 420
    s = header(W, H)
    s += title(W, "Крок передбачення в циклі оцінювання",
               "стан зараз + модель руху (+ відомий вхід) → стан за мить; далі його виправить вимір")
    s += rect(60, 140, 170, 100, fill=BOX1, stroke=BLUE, sw=1.8, rx=12)
    s += text(145, 178, "СТАН зараз", size=13, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(145, 200, "x, v, орієнтація", size=10.5, anchor="middle",
              fill=MUTE)
    s += text(145, 218, "(+ невизначеність)", size=9.5, anchor="middle",
              fill=MUTE)
    s += line(232, 190, 320, 190, stroke=INK, w=2.0, marker="arr")
    s += rect(322, 140, 180, 100, fill=PANEL, stroke=INK, sw=1.8, rx=12)
    s += text(412, 174, "МОДЕЛЬ РУХУ", size=13, anchor="middle", weight="bold")
    s += text(412, 196, "x += v·Δt", size=11, anchor="middle", fill=MUTE)
    s += text(412, 214, "+ відомий вхід (газ, IMU)", size=9.5, anchor="middle",
              fill=MUTE)
    s += line(504, 190, 592, 190, stroke=INK, w=2.0, marker="arr")
    s += rect(594, 140, 180, 100, fill=BOX2, stroke=GREEN, sw=2.0, rx=12)
    s += text(684, 174, "СТАН за Δt", size=13, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(684, 196, "ПЕРЕДБАЧЕННЯ", size=11, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(684, 216, "(певність трохи впала)", size=9.5, anchor="middle",
              fill=MUTE)
    s += line(684, 242, 684, 296, stroke=MUTE, w=1.6, dash="5,4", marker="arr")
    s += rect(558, 298, 252, 56, fill="white", stroke=MUTE, sw=1.5, rx=10,
              dash="5,4")
    s += text(684, 322, "далі: ВИМІР виправить", size=12, anchor="middle",
              weight="bold", fill=MUTE)
    s += text(684, 342, "(зважування — тема 46.3)", size=10, anchor="middle",
              fill=MUTE)
    s += text(230, 312, "Цикл щомиті:", size=12, anchor="middle", weight="bold")
    s += text(230, 332, "передбач → виправ →", size=11, anchor="middle",
              fill=MUTE)
    s += text(230, 348, "передбач → …", size=11, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 12,
              "46.2 — це передбачення (ліва половина циклу). Корекцію виміром "
              "додамо в 46.3.", size=11.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.3.1 — Передбачення й вимір не збігаються
# ════════════════════════════════════════════════════════════════════════════
def fig_disagree():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Передбачення й вимір не збігаються — кому вірити?",
               "обидва непевні: у кожного своя «хмара»; де між ними покласти оцінку?")
    ox, oy, ow, oh = 80, 110, 800, 230
    base = oy + oh
    s += line(ox, base, ox + ow, base, stroke=INK, w=1.5)
    s += text(ox + ow, base + 22, "положення →", size=11, anchor="end",
              fill=MUTE, weight="bold")

    def bell(cx, sig, peak, col):
        pts = [(ox + ow * k / 80,
                base - peak * math.exp(-((ox + ow * k / 80 - cx) ** 2) / (2 * sig ** 2)))
               for k in range(81)]
        return (poly(pts + [(ox + ow, base), (ox, base)], fill=col,
                     stroke="none", opacity=0.10, closed=True)
                + poly(pts, fill="none", stroke=col, sw=2.4, closed=False))
    pcx, mcx = ox + 300, ox + 540
    s += bell(pcx, 60, 150, BLUE)
    s += bell(mcx, 48, 150, GREEN)
    s += line(pcx, base, pcx, base - 150, stroke=BLUE, w=1, dash="3,3")
    s += text(pcx, oy + 4, "ПЕРЕДБАЧЕННЯ", size=11.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(pcx, oy + 20, "(де гадаю бути)", size=10, anchor="middle",
              fill=MUTE)
    s += line(mcx, base, mcx, base - 150, stroke=GREEN, w=1, dash="3,3")
    s += text(mcx, oy + 4, "ВИМІР", size=11.5, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(mcx, oy + 20, "(що каже давач)", size=10, anchor="middle",
              fill=MUTE)
    s += text((pcx + mcx) / 2, base - 64, "?", size=30, anchor="middle",
              weight="bold", fill=RED)
    s += text((pcx + mcx) / 2, base - 34, "де істина?", size=10.5,
              anchor="middle", fill=RED)
    s += text(W / 2, H - 12,
              "Ширина «хмари» — це невпевненість. Вужча хмара = певніше джерело. "
              "Оцінку кладуть між ними, зважено.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.3.2 — Зважений сплав, ближче до певнішого
# ════════════════════════════════════════════════════════════════════════════
def fig_weighted_blend():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Зважений сплав: ближче до того, хто певніший",
               "оцінка лягає між передбаченням і виміром — ближче до вужчої «хмари» й вужча за обидві")

    def panel(oy, label, psig, msig, note):
        ox, ow, oh = 80, 800, 150
        base = oy + oh
        out = line(ox, base, ox + ow, base, stroke="#cbd5e1", w=1.2)
        out += text(ox + 2, oy + 14, label, size=11, weight="bold")
        pcx, mcx = ox + 300, ox + 560

        def bell(cx, sig, peak, col, sw, fop):
            pts = [(ox + ow * k / 120,
                    base - peak * math.exp(-((ox + ow * k / 120 - cx) ** 2) / (2 * sig ** 2)))
                   for k in range(121)]
            return (poly(pts + [(ox + ow, base), (ox, base)], fill=col,
                         stroke="none", opacity=fop, closed=True)
                    + poly(pts, fill="none", stroke=col, sw=sw, closed=False))
        wp, wm = 1 / psig ** 2, 1 / msig ** 2
        fcx = (wp * pcx + wm * mcx) / (wp + wm)
        fsig = (1 / (wp + wm)) ** 0.5
        out += bell(pcx, psig, 90, BLUE, 1.8, 0.07)
        out += bell(mcx, msig, 90, GREEN, 1.8, 0.07)
        out += bell(fcx, fsig, 118, RED, 2.6, 0.16)
        out += text(pcx, base - 95, "перед.", size=9.5, anchor="middle",
                    fill=BLUE)
        out += text(mcx, base - 95, "вимір", size=9.5, anchor="middle",
                    fill=GREEN)
        out += text(fcx, base - 126, "СПЛАВ", size=10.5, anchor="middle",
                    fill=RED, weight="bold")
        out += text(ox + ow - 4, oy + 16, note, size=10.5, anchor="end",
                    fill=MUTE, italic=True)
        return out
    s += panel(84, "точний вимір:", 70, 34,
               "вузька зелена → сплав тягне до виміру")
    s += panel(280, "шумний вимір:", 34, 70,
               "широка зелена → сплав лишається при передбаченні")
    s += text(W / 2, H - 12,
              "Сплав завжди вужчий (певніший) за обидві вхідні хмари — у тім і "
              "виграш злиття.", size=11.5, anchor="middle", fill=MUTE,
              italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.3.3 — Підсилення K
# ════════════════════════════════════════════════════════════════════════════
def fig_gain():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Підсилення K: наскільки слухати вимір",
               "оцінка = передбачення + K × (вимір − передбачення); K від 0 до 1 за відносною певністю")
    sx, slen, sy = 150, 660, 140
    s += line(sx, sy, sx + slen, sy, stroke=INK, w=3)
    for frac, lab in [(0, "K = 0"), (0.5, "K = 0.5"), (1, "K = 1")]:
        x = sx + slen * frac
        s += line(x, sy - 8, x, sy + 8, stroke=INK, w=2)
        s += text(x, sy + 26, lab, size=11, anchor="middle", weight="bold")
    s += text(sx, sy - 22, "лишаюсь на передбаченні", size=10.5,
              anchor="middle", fill=BLUE, weight="bold")
    s += text(sx + slen, sy - 22, "стрибаю на вимір", size=10.5,
              anchor="middle", fill=GREEN, weight="bold")
    kx = sx + slen * 0.6
    s += circle(kx, sy, 11, fill=AMBER, stroke=INK, sw=1.6)
    s += rect(150, 232, 660, 56, fill=PANEL, stroke=INK, sw=1.5, rx=10)
    s += text(480, 267, "K = σ²пер / (σ²пер + σ²вим)", size=17, anchor="middle",
              weight="bold")
    s += rect(150, 312, 320, 96, fill=BOX1, stroke=BLUE, sw=1.5, rx=10)
    s += text(310, 338, "вимір ШУМНИЙ (σ²вим велика)", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += text(310, 364, "→ K → 0", size=14, anchor="middle", weight="bold")
    s += text(310, 388, "майже ігнорую вимір", size=10, anchor="middle",
              fill=MUTE)
    s += rect(490, 312, 320, 96, fill=BOX2, stroke=GREEN, sw=1.5, rx=10)
    s += text(650, 338, "вимір ТОЧНИЙ (σ²вим мала)", size=11, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(650, 364, "→ K → 1", size=14, anchor="middle", weight="bold")
    s += text(650, 388, "стрибаю на вимір", size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 10,
              "K — це й є «підсилення Калмана»: регулятор довіри, що сам "
              "перетікає за невизначеністю.", size=11.5, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.3.4 — Певність зростає, цикл замикається
# ════════════════════════════════════════════════════════════════════════════
def fig_shrink():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Після злиття певність зростає — і цикл замикається",
               "зведена оцінка вужча за обидві вхідні; вона ж — стан для наступного передбачення")
    s += text(280, 78, "дві широкі хмари → одна вузька", size=12,
              anchor="middle", weight="bold", fill=MUTE)
    s += circle(150, 165, 44, fill=BLUE, stroke=BLUE, sw=1.5, opacity=0.16)
    s += text(150, 169, "перед.", size=10.5, anchor="middle", fill=BLUE,
              weight="bold")
    s += circle(246, 165, 40, fill=GREEN, stroke=GREEN, sw=1.5, opacity=0.16)
    s += text(246, 169, "вимір", size=10.5, anchor="middle", fill=GREEN,
              weight="bold")
    s += line(304, 165, 376, 165, stroke=INK, w=2.2, marker="arr")
    s += text(340, 153, "злиття", size=10, anchor="middle", weight="bold")
    s += circle(430, 165, 22, fill=RED, stroke=RED, sw=1.8, opacity=0.24)
    s += text(430, 169, "СПЛАВ", size=9.5, anchor="middle", fill=RED,
              weight="bold")
    s += text(430, 218, "вужче за обидві!", size=10.5, anchor="middle", fill=RED,
              weight="bold")
    s += line(545, 95, 545, 300, stroke="#e5e7eb", w=1.4, dash="4,4")
    cx = 745
    s += text(cx, 78, "і цикл замикається", size=12, anchor="middle",
              weight="bold", fill=MUTE)
    s += rect(cx - 130, 120, 120, 54, fill=BOX1, stroke=BLUE, sw=1.7, rx=10)
    s += text(cx - 70, 146, "ПЕРЕДБАЧ", size=11, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(cx - 70, 163, "(46.2)", size=9, anchor="middle", fill=MUTE)
    s += rect(cx + 10, 120, 120, 54, fill=BOX2, stroke=GREEN, sw=1.7, rx=10)
    s += text(cx + 70, 146, "КОРЕКЦІЯ", size=11, anchor="middle", weight="bold",
              fill=GREEN)
    s += text(cx + 70, 163, "(46.3)", size=9, anchor="middle", fill=MUTE)
    s += line(cx - 8, 147, cx + 8, 147, stroke=INK, w=2, marker="arr")
    s += line(cx + 70, 176, cx + 70, 226, stroke=MUTE, w=1.8)
    s += line(cx + 70, 226, cx - 70, 226, stroke=MUTE, w=1.8)
    s += line(cx - 70, 226, cx - 70, 178, stroke=MUTE, w=1.8, marker="arr")
    s += text(cx, 246, "тісніший стан → у наступне передбачення", size=9.5,
              anchor="middle", fill=MUTE)
    s += text(W / 2, H - 12,
              "Кожен оберт «передбач → виправ» робить оцінку трохи певнішою — "
              "так апарат і тримає певне відчуття себе.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


def epts(cx, cy, rx, ry, n=56, rot=0.0):
    """Точки еліпса (для «хмар» коваріації), з можливим нахилом rot (рад)."""
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot),
                    cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.4.1 — Стан і коваріація
# ════════════════════════════════════════════════════════════════════════════
def fig_state_cov():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Стан і коваріація: оцінка плюс її «хмара»",
               "фільтр веде не лише найкращу здогадку, а й її невпевненість — формальну хмару (коваріацію)")

    def case(cx, rx, ry, col, lab, sub):
        out = poly(epts(cx, 210, rx, ry), fill=col, stroke=col, sw=1.8,
                   closed=True, opacity=0.14)
        out += circle(cx, 210, 5, fill=col, stroke=INK, sw=1.3)
        out += text(cx, 210 - ry - 16, lab, size=13, anchor="middle",
                    weight="bold", fill=col)
        out += text(cx, 210 + ry + 24, sub, size=10.5, anchor="middle",
                    fill=MUTE)
        return out
    s += text(150, 116, "стан (напр. x, y)", size=11, fill=MUTE, weight="bold")
    s += case(280, 36, 28, GREEN, "ПЕВНО", "мала хмара → оцінці можна вірити")
    s += case(680, 118, 90, AMBER, "НЕПЕВНО", "велика хмара → оцінка розмита")
    s += text(W / 2, H - 16,
              "Хмара (коваріація) — рівноправна частина оцінки: фільтр завжди "
              "знає не лише «де», а й «наскільки певен».", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.4.2 — Фільтр Калмана: цикл
# ════════════════════════════════════════════════════════════════════════════
def fig_kf_cycle():
    W, H = 960, 480
    s = header(W, H)
    s += title(W, "Фільтр Калмана: два кроки, що крутяться по колу",
               "ПЕРЕДБАЧ (хмара росте, + шум руху Q) → ОНОВИ виміром (хмара меншає через K) → знову")
    s += rect(80, 130, 320, 150, fill=BOX1, stroke=BLUE, sw=2.0, rx=14)
    s += text(240, 160, "1) ПЕРЕДБАЧЕННЯ", size=14, anchor="middle",
              weight="bold", fill=BLUE)
    s += lines(104, 186, ["• стан → модель руху (x += v·Δt)",
                          "• хмара РОСТЕ: + шум руху Q",
                          "  (модель неточна → менше певності)"], size=10.5,
               lh=21)
    s += poly(epts(245, 256, 24, 13), fill=BLUE, stroke=BLUE, sw=1.3,
              closed=True, opacity=0.12)
    s += poly(epts(245, 256, 40, 21), fill="none", stroke=BLUE, sw=1.1,
              closed=True)
    s += text(300, 260, "хмара ↑", size=9.5, fill=BLUE, weight="bold")
    s += rect(560, 130, 320, 150, fill=BOX2, stroke=GREEN, sw=2.0, rx=14)
    s += text(720, 160, "2) ОНОВЛЕННЯ виміром", size=14, anchor="middle",
              weight="bold", fill=GREEN)
    s += lines(584, 186, ["• прийшов вимір; K із хмар (46.3)",
                          "• стан → ближче до виміру: + K·(різниця)",
                          "• хмара МЕНШАЄ (певність ↑)"], size=10.5, lh=21)
    s += poly(epts(720, 256, 40, 21), fill="none", stroke=GREEN, sw=1.1,
              closed=True)
    s += poly(epts(720, 256, 21, 11), fill=GREEN, stroke=GREEN, sw=1.3,
              closed=True, opacity=0.16)
    s += text(775, 260, "хмара ↓", size=9.5, fill=GREEN, weight="bold")
    s += line(400, 172, 560, 172, stroke=INK, w=2.4, marker="arr")
    s += text(480, 164, "передбачене", size=10, anchor="middle", fill=MUTE)
    s += line(560, 238, 400, 238, stroke=INK, w=2.4, marker="arr")
    s += text(480, 230, "виправлений стан", size=10, anchor="middle", fill=MUTE)
    s += text(480, 254, "→ у наступний цикл", size=9, anchor="middle", fill=MUTE)
    s += rect(300, 332, 360, 50, fill=PANEL, stroke=INK, sw=1.4, rx=10)
    s += text(480, 354, "цикл крутиться сотні разів на секунду", size=12,
              anchor="middle", weight="bold")
    s += text(480, 372, "стан + коваріація щоразу оновлюються разом", size=10,
              anchor="middle", fill=MUTE)
    s += text(W / 2, H - 14,
              "Це і весь фільтр Калмана: передбач (хмара росте) — онови виміром "
              "(хмара меншає), знов і знов, оптимально.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.4.3 — Магія коваріації (кореляція)
# ════════════════════════════════════════════════════════════════════════════
def fig_cross_correlation():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Магія коваріації: виміряв одне — підправив пов'язане",
               "нахил хмари = кореляція; вимір положення підтягує й швидкість, хоч її не міряли")
    ox, oy = 230, 360
    s += line(ox, oy, ox, 92, stroke=INK, w=1.5, marker="arr")
    s += line(ox, oy, 770, oy, stroke=INK, w=1.5, marker="arr")
    s += text(ox - 10, 98, "швидкість", size=11, anchor="end", fill=MUTE,
              weight="bold")
    s += text(770, oy + 22, "положення", size=11, anchor="end", fill=MUTE,
              weight="bold")
    cx, cy = 470, 235
    s += poly(epts(cx, cy, 150, 52, rot=-0.6), fill=BLUE, stroke=BLUE, sw=1.8,
              closed=True, opacity=0.13)
    s += text(640, 130, "хмара нахилена:", size=10.5, anchor="middle", fill=BLUE,
              weight="bold")
    s += text(640, 146, "положення й швидкість", size=10.5, anchor="middle",
              fill=BLUE)
    s += text(640, 162, "пов'язані (кореляція)", size=10.5, anchor="middle",
              fill=BLUE)
    mx = 560
    s += line(mx, 360, mx, 110, stroke=GREEN, w=2.0, dash="6,4")
    s += text(mx, 100, "вимір положення", size=10.5, anchor="middle", fill=GREEN,
              weight="bold")
    s += circle(cx, cy, 5, fill=BLUE, stroke=INK, sw=1.3)
    s += text(cx - 12, cy + 18, "було", size=10, anchor="end", fill=BLUE)
    nyy = cy - (mx - cx) * math.tan(0.6)
    s += line(cx, cy, mx, nyy, stroke=RED, w=1.4, dash="3,3")
    s += circle(mx, nyy, 6, fill=RED, stroke=INK, sw=1.4)
    s += text(mx + 12, nyy + 4, "стало", size=10, fill=RED, weight="bold")
    s += line(mx, nyy, ox, nyy, stroke=RED, w=1, dash="2,3")
    s += text(ox + 8, nyy - 8, "оновлена швидкість", size=9.5, fill=RED,
              weight="bold")
    s += text(W / 2, H - 14,
              "Бо в коваріації записано, що положення й швидкість пов'язані — "
              "тож вимір самого положення оновлює й швидкість.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.4.4 — EKF: лінеаризація
# ════════════════════════════════════════════════════════════════════════════
def fig_ekf_linearize():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "EKF: коли світ нелінійний — випрямляй у точці",
               "справжня модель крива; розширений фільтр щокроку бере дотичну в точці оцінки")
    ox, oy, ow = 110, 350, 720
    s += line(ox, oy, ox, 92, stroke=INK, w=1.4, marker="arr")
    s += line(ox, oy, ox + ow, oy, stroke=INK, w=1.4, marker="arr")
    s += text(ox - 8, 98, "вихід", size=10.5, anchor="end", fill=MUTE,
              weight="bold")
    s += text(ox + ow, oy + 22, "стан", size=10.5, anchor="end", fill=MUTE,
              weight="bold")

    def fy(f):
        return oy - 36 - 200 * (0.5 + 0.5 * math.tanh((f - 0.5) * 4))
    N = 120
    s += poly([(ox + ow * k / N, fy(k / N)) for k in range(N + 1)], fill="none",
              stroke=BLUE, sw=2.6, closed=False)
    s += text(ox + ow - 8, fy(0.9) - 12, "справжня (крива) залежність",
              size=10.5, anchor="end", fill=BLUE, weight="bold")
    f0 = 0.42
    px, py = ox + ow * f0, fy(f0)
    h = 0.01
    slope = (fy(f0 + h) - fy(f0 - h)) / (ow * 2 * h)
    x1, x2 = px - 180, px + 205
    s += line(x1, py + slope * (x1 - px), x2, py + slope * (x2 - px),
              stroke=AMBER, w=2.2, dash="7,4")
    s += text(x2 - 4, py + slope * (x2 - px) - 10,
              "дотична = лінійне наближення ТУТ", size=10, anchor="end",
              fill="#b06b00", weight="bold")
    s += circle(px, py, 6, fill=RED, stroke=INK, sw=1.4)
    s += text(px - 12, py + 22, "робоча точка (оцінка)", size=10, anchor="end",
              fill=RED, weight="bold")
    s += text(W / 2, H - 30,
              "Фільтр Калмана любить прямі, а світ кривий. EKF щокроку випрямляє "
              "криву дотичною в точці оцінки —", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "той самий трюк, що повів «Аполлон» до Місяця. Працює, поки оцінка "
              "близька до правди (далі дотична бреше).", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.5.1 — Чотири давачі, один стан
# ════════════════════════════════════════════════════════════════════════════
def fig_cast():
    W, H = 960, 470
    s = header(W, H)
    s += title(W, "Чотири давачі, один стан: хто що дає",
               "IMU веде передбачення, а баро, GNSS і магнітометр осаджують його дрейф — кожен у своїй частині")
    s += rect(360, 175, 240, 130, fill=BOX2, stroke=GREEN, sw=2.2, rx=14)
    s += text(480, 202, "ОЦІНКА СТАНУ", size=14, anchor="middle", weight="bold",
              fill=GREEN)
    s += lines(386, 226, ["• крен, тангаж (нахил)", "• курс (yaw)", "• висота",
                          "• положення, швидкість"], size=10.5, lh=19)
    s += rect(70, 200, 180, 84, fill=BOX1, stroke=BLUE, sw=2.0, rx=12)
    s += text(160, 228, "IMU", size=15, anchor="middle", weight="bold",
              fill=BLUE)
    s += text(160, 248, "гіро + акселерометр", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(160, 266, "→ ПЕРЕДБАЧЕННЯ всього", size=9.5, anchor="middle",
              fill=BLUE, weight="bold")
    s += line(252, 242, 358, 242, stroke=BLUE, w=3.0, marker="arrB")
    s += text(305, 232, "веде", size=10, anchor="middle", fill=BLUE,
              weight="bold")
    s += text(650, 150, "корекції осаджують дрейф", size=10, anchor="middle",
              fill=MUTE, italic=True)
    for cy, nm, what, col in [(95, "Магнітометр", "→ курс (yaw)", "#9333ea"),
                              (185, "Барометр", "→ висота", AMBER),
                              (275, "GNSS", "→ положення, швидкість", GREEN)]:
        s += line(698, cy + 32, 604, 240, stroke=col, w=1.8, marker="arr",
                  opacity=0.8)
        s += rect(700, cy, 200, 64, fill="white", stroke=col, sw=1.8, rx=11)
        s += text(800, cy + 27, nm, size=12.5, anchor="middle", weight="bold",
                  fill=col)
        s += text(800, cy + 47, what, size=10, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 16,
              "IMU дає швидку, гладку, та дрейфливу основу; решта — рідкі, зате "
              "стабільні «якорі» для своїх частин стану.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.5.2 — Хто що утримує
# ════════════════════════════════════════════════════════════════════════════
def fig_who_corrects():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Хто що утримує: передбачення й прив'язка",
               "кожну величину штовхає вперед IMU, а прив'язує до правди свій коректор")
    for x, h in [(250, "ВЕЛИЧИНА"), (520, "передбачає"),
                 (760, "прив'язує (корегує)")]:
        s += text(x, 108, h, size=12, anchor="middle", weight="bold", fill=MUTE)
    rows = [("крен, тангаж (нахил)", "IMU (гіро)", "акселерометр (гравітація)",
             AMBER),
            ("курс (yaw)", "IMU (гіро)", "магнітометр — єдиний!", "#9333ea"),
            ("висота", "IMU (аксел.)", "барометр (+ GNSS)", BLUE),
            ("гориз. положення, швидк.", "IMU (аксел.)", "GNSS — єдиний!",
             GREEN)]
    yy = 130
    for name, pred, corr, col in rows:
        s += rect(70, yy, 820, 62, fill="white", stroke="#e5e7eb", sw=1.4, rx=9)
        s += text(250, yy + 37, name, size=12, anchor="middle", weight="bold")
        s += text(520, yy + 37, pred, size=11, anchor="middle", fill=BLUE)
        s += rect(640, yy + 10, 240, 42, fill=col, stroke="none", rx=8,
                  opacity=0.14)
        s += text(760, yy + 37, corr, size=11, anchor="middle", weight="bold",
                  fill=col)
        yy += 74
    s += text(W / 2, H - 14,
              "Два вузькі місця: курс тримає лише магнітометр, горизонтальну "
              "позицію — лише GNSS. Відпаде — нема ким замінити.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.5.3 — Різні темпи
# ════════════════════════════════════════════════════════════════════════════
def fig_rates():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Різні темпи: передбачення часте, корекції — коли прийдуть",
               "IMU тікає сотні разів на секунду; баро, магнітометр і GNSS осаджують рідше, кожен свого часу")
    ox, ow = 220, 620
    rows = [("IMU → передбач", BLUE, 28, "сотні Гц"),
            ("Барометр", AMBER, 9, "~десятки Гц"),
            ("Магнітометр", "#9333ea", 7, "~десятки Гц"),
            ("GNSS", GREEN, 4, "~5–10 Гц")]
    yy = 120
    for name, col, n, rate in rows:
        s += text(205, yy + 6, name, size=11.5, anchor="end", weight="bold",
                  fill=col)
        s += line(ox, yy, ox + ow, yy, stroke="#e5e7eb", w=1.2)
        for i in range(n):
            x = ox + ow * (i + 0.5) / n
            s += line(x, yy - 9, x, yy + 9, stroke=col, w=1.8 if n > 10 else 2.6)
        s += text(ox + ow + 12, yy + 5, rate, size=10, fill=MUTE)
        yy += 62
    s += text(ox + ow / 2, yy + 2, "час →", size=11, anchor="middle", fill=MUTE)
    s += text(W / 2, H - 30,
              "EKF передбачає на кожному тику IMU (густо), а як прилетить відлік "
              "баро, компаса чи GPS — робить корекцію.", size=11.5,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Тому оцінка завжди свіжа й гладка (темп IMU), та водночас "
              "прив'язана до правди (рідкі, але стабільні корекції).", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.5.4 — Плавна деградація
# ════════════════════════════════════════════════════════════════════════════
def fig_failure():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Коли давач відпав: фьюжн деградує плавно",
               "GPS зник — горизонталь попливла, та нахил, курс і висота тримаються; апарат міняє режим")

    def colstate(x0, head, headcol, states):
        out = text(x0 + 150, 108, head, size=13, anchor="middle", weight="bold",
                   fill=headcol)
        yy = 135
        for nm, ok in states:
            col = GREEN if ok else RED
            out += rect(x0, yy, 300, 50, fill=col, stroke=col, sw=1.6, rx=9,
                        opacity=0.13)
            out += text(x0 + 16, yy + 30, nm, size=11.5, weight="bold")
            out += text(x0 + 284, yy + 30,
                        "✓ прив'язано" if ok else "✗ дрейфує", size=10.5,
                        anchor="end", weight="bold", fill=col)
            yy += 62
        return out
    s += colstate(70, "усе гаразд", GREEN,
                  [("нахил (крен/тангаж)", True), ("курс", True),
                   ("висота", True), ("гориз. положення", True)])
    s += colstate(590, "GPS пропав", RED,
                  [("нахил (крен/тангаж)", True), ("курс", True),
                   ("висота", True), ("гориз. положення", False)])
    s += line(388, 240, 580, 240, stroke=INK, w=2.2, marker="arr")
    s += text(485, 230, "GPS зник", size=11, anchor="middle", weight="bold",
              fill=RED)
    s += text(485, 256, "тільки горизонталь", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(485, 270, "втрачає прив'язку", size=9.5, anchor="middle",
              fill=MUTE)
    s += text(W / 2, H - 30,
              "Решта стану тримається своїми корекціями (accel, компас, баро) — "
              "апарат не «сліпо падає»: ручний летить далі, автономний саджає (EKF-failsafe).", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Тому при втраті GPS контролер сам переходить у режим без позиції "
              "(утримання висоти) — деградація сходинкою, не обвалом (44.7).",
              size=10.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.6.1 — Затримка: вимір застарілий
# ════════════════════════════════════════════════════════════════════════════
def fig_latency():
    W, H = 960, 440
    s = header(W, H)
    s += title(W, "Кожен вимір — застарілий: затримка псує фьюжн",
               "поки GPS-фікс долетів, апарат уже зрушив; вставити його як «тепер» — зіпсувати оцінку")
    ty = 230
    s += line(90, ty, 870, ty, stroke="#e5e7eb", w=2)
    px, nx = 360, 640
    s += line(px + 12, ty - 18, nx - 12, ty - 18, stroke=MUTE, w=1.4,
              dash="4,3")
    s += text((px + nx) / 2, ty - 26, "за час Δt апарат проїхав сюди →",
              size=10, anchor="middle", fill=MUTE)
    s += circle(px, ty, 9, fill=GREEN, stroke=INK, sw=1.4)
    s += text(px, ty + 30, "GPS каже: «тут»", size=11, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(px, ty + 47, "(але це було Δt тому)", size=10, anchor="middle",
              fill=MUTE)
    s += circle(nx, ty, 11, fill=BLUE, stroke=INK, sw=1.6)
    s += text(nx, ty - 24, "апарат ЗАРАЗ", size=11, anchor="middle",
              weight="bold", fill=BLUE)
    s += line(nx - 12, ty + 14, px + 14, ty + 14, stroke=RED, w=2.2,
              marker="arrR")
    s += text((px + nx) / 2, ty + 34,
              "наївно вставити «як тепер» → оцінку тягне НАЗАД (хибно)",
              size=10.5, anchor="middle", fill=RED, weight="bold")
    s += text(W / 2, H - 30,
              "Найгірший винуватець — GPS: його фікс описує, де ти був ~десяту "
              "секунди тому, поки сигнал оброблявся.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Вставиш застарілий вимір як свіжий — і позиція засмикається, "
              "«забовтається», а то й піде по колу.", size=11, anchor="middle",
              fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.6.2 — Виправ минуле, програй наперед
# ════════════════════════════════════════════════════════════════════════════
def fig_rewind():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Лік від затримки: виправ минуле, програй наперед",
               "фільтр тримає буфер минулих станів; корегує стан на момент виміру й переграє вперед")
    ty = 220
    s += line(90, ty, 870, ty, stroke=INK, w=1.5, marker="arr")
    s += text(870, ty + 22, "час →", size=11, anchor="end", fill=MUTE,
              weight="bold")
    for i, x in enumerate([160, 280, 400, 520, 640, 760]):
        col = GREEN if i == 2 else (BLUE if i > 2 else MUTE)
        s += circle(x, ty, 7, fill=col, stroke=INK, sw=1.2)
    s += text(160, ty + 28, "буфер минулих станів", fill=MUTE, size=10)
    s += text(760, ty - 22, "«зараз»", size=10.5, anchor="middle",
              weight="bold", fill=BLUE)
    s += rect(660, 92, 220, 50, fill=BOX2, stroke=GREEN, sw=1.6, rx=10)
    s += text(770, 114, "прилетів GPS-фікс", size=11, anchor="middle",
              weight="bold", fill=GREEN)
    s += text(770, 132, "із міткою часу (минуле)", size=10, anchor="middle",
              fill=MUTE)
    s += line(700, 144, 408, ty - 12, stroke=GREEN, w=1.8, dash="5,4",
              marker="arrG")
    s += text(400, ty - 20, "1) корегуємо стан НА МОМЕНТ виміру", size=10.5,
              anchor="middle", fill=GREEN, weight="bold")
    s += line(410, ty + 18, 760, ty + 18, stroke=AMBER, w=2.4, marker="arr")
    s += text(585, ty + 36, "2) переграємо вперед до «зараз»", size=10.5,
              anchor="middle", fill="#b06b00", weight="bold")
    s += text(W / 2, H - 14,
              "Саме так працює EKF в ArduPilot: завдяки буферу він фьюзить "
              "запізнілий GPS у правильний момент минулого — без ривків.",
              size=11.5, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.6.3 — Несподіванка (innovation)
# ════════════════════════════════════════════════════════════════════════════
def fig_innovation():
    W, H = 960, 450
    s = header(W, H)
    s += title(W, "Несподіванка (innovation) — пульс оцінювача",
               "вимір − передбачення: мала й коло нуля = здорово; стрибок = негаразд (давач чи розбіжність)")
    ox, oy, ow, oh = 90, 110, 780, 250
    midy = oy + oh / 2
    s += rect(ox, oy, ow, oh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=8)
    s += line(ox, midy, ox + ow, midy, stroke=INK, w=1.3)
    s += text(ox - 8, midy + 4, "0", size=10, anchor="end", fill=MUTE)
    s += text(ox - 8, oy + 14, "вимір−передбач", size=10, anchor="end",
              fill=MUTE, weight="bold")
    s += text(ox + ow, oy + oh + 22, "час →", size=11, anchor="end", fill=MUTE)
    g = 70
    s += line(ox, midy - g, ox + ow, midy - g, stroke=RED, w=1.2, dash="6,4")
    s += line(ox, midy + g, ox + ow, midy + g, stroke=RED, w=1.2, dash="6,4")
    s += text(ox + 8, midy - g - 6, "ворота (поза ними → відхилити вимір)",
              size=9.5, fill=RED)
    pts = []
    for k in range(161):
        f = k / 160
        x = ox + ow * f
        if f < 0.60:
            y = midy + 15 * math.sin(k * 1.3) + 9 * math.sin(k * 0.5 + 1)
        elif f < 0.68:
            y = midy - (f - 0.60) / 0.08 * 115
        elif f < 0.74:
            y = midy - (0.74 - f) / 0.06 * 115
        else:
            y = midy + 15 * math.sin(k * 1.3)
        pts.append((x, y))
    s += poly(pts, fill="none", stroke=BLUE, sw=2.0, closed=False)
    s += text(ox + 150, midy + 46, "здорово: мала, коло нуля", size=10.5,
              fill=GREEN, weight="bold")
    s += circle(ox + ow * 0.68, midy - 115, 5, fill=RED, stroke=INK, sw=1.2)
    s += text(ox + ow * 0.68 + 8, midy - 112,
              "стрибок: давач збрехав / розбіжність", size=10.5, fill=RED,
              weight="bold")
    s += text(W / 2, H - 30,
              "Несподіванка — найкорисніший показник здоров'я: малі — сенсори "
              "згодні з оцінкою; великі — хтось бреше.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += text(W / 2, H - 14,
              "Якщо несподіванка вилазить за «ворота», фільтр відхиляє той "
              "вимір — захист від поодинокого збою давача.", size=11,
              anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 46.6.4 — Читання логу
# ════════════════════════════════════════════════════════════════════════════
def fig_logreading():
    W, H = 960, 460
    s = header(W, H)
    s += title(W, "Читання логу: оцінювач сам звітує, де болить",
               "після дивного польоту дивись несподіванки й хмари по давачах — видно, ХТО й КОЛИ збився")
    ox, ow = 230, 470
    yy = 120
    for name, col, spike in [("GNSS", RED, True),
                             ("Магнітометр", "#9333ea", False),
                             ("Барометр", AMBER, False)]:
        s += text(215, yy + 4, name, size=11.5, anchor="end", weight="bold",
                  fill=col)
        s += rect(ox, yy - 26, ow, 52, fill="#f8fafc", stroke="#e5e7eb", sw=1,
                  rx=6)
        s += line(ox, yy, ox + ow, yy, stroke="#cbd5e1", w=1)
        npts = []
        for k in range(101):
            f = k / 100
            x = ox + ow * f
            y = yy + 10 * math.sin(k * 1.6)
            if spike and 0.52 < f < 0.60:
                y = yy - 26 * (1 - abs(f - 0.56) / 0.04)
            npts.append((x, y))
        s += poly(npts, fill="none", stroke=col, sw=1.8, closed=False)
        s += text(ox + ow + 12, yy + 4, "← СТРИБОК тут!" if spike else "спокійно ✓",
                  size=10.5, weight="bold", fill=(RED if spike else GREEN))
        yy += 78
    s += rect(230, 358, 470, 58, fill=BOX1, stroke=BLUE, sw=1.5, rx=10)
    s += text(465, 382, "Висновок: несподіванка GNSS вилетіла за ворота —",
              size=11, anchor="middle", weight="bold", fill=BLUE)
    s += text(465, 402, "винен GPS (затінення / багатопроменевість), решта чиста.",
              size=10.5, anchor="middle")
    s += text(W / 2, H - 14,
              "Не гадай «що зламалось» — спитай лог: EKF сам показує, чия "
              "несподіванка стрибнула й коли. Це й є діагностика фьюжну.",
              size=11, anchor="middle", fill=MUTE, italic=True)
    s += footer()
    return s


# ── запис ───────────────────────────────────────────────────────────────────
FIGS = {
    "fig-46-0-1-sealedbox.svg":   fig_sealedbox,
    "fig-46-0-2-gyroaccel.svg":   fig_gyroaccel,
    "fig-46-0-3-spire.svg":       fig_spire,
    "fig-46-0-4-drift-fusion.svg": fig_drift_fusion,
    "fig-46-1-1-witnesses.svg":   fig_witnesses,
    "fig-46-1-2-complementary.svg": fig_complementary,
    "fig-46-1-3-altitude.svg":    fig_altitude,
    "fig-46-1-4-fusion-concept.svg": fig_fusion_concept,
    "fig-46-2-1-deadreckon.svg":  fig_predict_deadreckon,
    "fig-46-2-2-fillgap.svg":     fig_predict_fillgap,
    "fig-46-2-3-uncertainty.svg": fig_predict_uncertainty,
    "fig-46-2-4-predict-step.svg": fig_predict_step,
    "fig-46-3-1-disagree.svg":    fig_disagree,
    "fig-46-3-2-weighted-blend.svg": fig_weighted_blend,
    "fig-46-3-3-gain.svg":        fig_gain,
    "fig-46-3-4-shrink.svg":      fig_shrink,
    "fig-46-4-1-state-cov.svg":   fig_state_cov,
    "fig-46-4-2-kf-cycle.svg":    fig_kf_cycle,
    "fig-46-4-3-cross-correlation.svg": fig_cross_correlation,
    "fig-46-4-4-ekf-linearize.svg": fig_ekf_linearize,
    "fig-46-5-1-cast.svg":        fig_cast,
    "fig-46-5-2-who-corrects.svg": fig_who_corrects,
    "fig-46-5-3-rates.svg":       fig_rates,
    "fig-46-5-4-failure.svg":     fig_failure,
    "fig-46-6-1-latency.svg":     fig_latency,
    "fig-46-6-2-rewind.svg":      fig_rewind,
    "fig-46-6-3-innovation.svg":  fig_innovation,
    "fig-46-6-4-logreading.svg":  fig_logreading,
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
