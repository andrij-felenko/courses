# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 5 — «Еквівалентні схеми: Тевенін, Нортон, суперпозиція» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: історія до розділу — секція 0 (Рис. 5.0.N); теми — Рис. 5.M.k.
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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange"}


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


def _resistor(x, y, w=70, h=24, label="R"):
    out = rect(x, y - h / 2, w, h, "#fff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 8, label, 12.5, INK, "middle", "bold", "italic")
    return out


def _vresistor(cx, y0, y1, label="", lside="start"):
    out = rect(cx - 12, y0, 24, y1 - y0, "#fff", INK, 2, 3)
    if label:
        lx = cx + 18 if lside == "start" else cx - 18
        out += text(lx, (y0 + y1) / 2 + 4, label, 11.5, INK, lside, "bold", "italic")
    return out


def _battery(cx, cy, label="", anchor="end"):
    """Вертикальна батарея на осі cx, центр cy; + довга тонка, − коротка товста."""
    out = line(cx - 16, cy - 8, cx + 16, cy - 8, INK, 3)
    out += line(cx - 9, cy + 8, cx + 9, cy + 8, INK, 5)
    if label:
        lx = cx - 22 if anchor == "end" else cx + 22
        out += text(lx, cy + 4, label, 11.5, INK, anchor, "bold")
    return out


def _isource(cx, cy, label="", anchor="end"):
    """Джерело струму: коло зі стрілкою вгору."""
    out = circle(cx, cy, 18, "#fff", INK, 2)
    out += arrow(cx, cy + 11, cx, cy - 11, INK, 2.2)
    if label:
        lx = cx - 26 if anchor == "end" else cx + 26
        out += text(lx, cy + 4, label, 11.5, INK, anchor, "bold")
    return out


def _term(x, y, label, lside="start"):
    out = circle(x, y, 4, "#fff", INK, 2)
    lx = x + 10 if lside == "start" else x - 10
    out += text(lx, y + 4, label, 12, INK, lside, "bold")
    return out


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 5 — Тевенін і Нортон.  Рис. 5.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 5.0.1 — «чорна скринька»: вигляд із двох клем ───────────────────────
def fig_blackbox():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Погляд із двох клем: складне коло — як «чорна скринька»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "навантаженню байдуже, що всередині — важливі лише дві вихідні клеми", 12, GREY, "middle", style="italic")
    # ліворуч: заплутана мережа
    s += rect(70, 100, 240, 200, "#f6f8fc", GREY, 1.6, 10)
    s += _battery(120, 200, "")
    s += line(120, 130, 120, 192, INK, 2)
    s += line(120, 208, 120, 270, INK, 2)
    s += line(120, 130, 270, 130, COPPER, 2)
    s += _resistor(150, 130, 50, 16, "")
    s += _vresistor(210, 150, 250, "")
    s += line(210, 130, 210, 150, COPPER, 2)
    s += line(210, 250, 210, 270, COPPER, 2)
    s += _resistor(230, 130, 50, 16, "")
    s += _vresistor(270, 150, 250, "")
    s += line(270, 130, 270, 150, COPPER, 2)
    s += line(120, 270, 270, 270, COPPER, 2)
    s += line(270, 250, 270, 270, COPPER, 2)
    s += text(190, 318, "багато джерел і опорів", 11, GREY, "middle", style="italic")
    s += line(290, 160, 330, 160, INK, 2)
    s += line(290, 240, 330, 240, INK, 2)
    s += _term(330, 160, "A")
    s += _term(330, 240, "B", "end")
    # стрілка
    s += arrow(360, 200, 430, 200, INK, 2.6)
    s += text(395, 188, "із клем", 9.5, GREY, "middle", style="italic")
    # праворуч: чорна скринька
    s += rect(450, 130, 200, 140, "#1b1b1b", INK, 2, 12)
    s += text(550, 195, "?", 40, "#fff", "middle", "bold")
    s += text(550, 230, "чорна скринька", 12, "#fff", "middle", "bold")
    s += line(650, 160, 700, 160, INK, 2)
    s += line(650, 240, 700, 240, INK, 2)
    s += _term(700, 160, "A")
    s += _term(700, 240, "B")
    s += text(550, 300, "Те, що навантаження «бачить», можна описати дуже просто — двома числами.",
              11, INK, "middle", "bold")
    save("fig-5-0-1-blackbox.svg", s)


# ── Рис. 5.0.2 — два еквіваленти: Тевенін і Нортон ───────────────────────────
def fig_thevenin_norton():
    W, H = 860, 390
    s = header(W, H)
    s += text(W / 2, 30, "Дві прості заміни будь-якої мережі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "Тевенін (1883): джерело напруги + опір послідовно;  Нортон (1926): джерело струму + опір паралельно",
              11.5, GREY, "middle", style="italic")
    # Тевенін
    s += text(210, 96, "Еквівалент Тевеніна", 13.5, BLUE, "middle", "bold")
    s += _battery(110, 235, "")
    s += text(86, 232, "V_th", 11, RED, "end", "bold")
    s += line(110, 170, 110, 227, INK, 2.2)
    s += line(110, 243, 110, 300, INK, 2.2)
    s += line(110, 170, 200, 170, COPPER, 2.2)
    s += _resistor(200, 170, 70, 20, "R_th")
    s += line(270, 170, 330, 170, COPPER, 2.2)
    s += line(110, 300, 330, 300, COPPER, 2.2)
    s += line(330, 170, 330, 185, INK, 2.2)
    s += line(330, 285, 330, 300, INK, 2.2)
    s += _term(330, 185, "A")
    s += _term(330, 285, "B")
    # Нортон
    s += text(640, 96, "Еквівалент Нортона", 13.5, GREEN, "middle", "bold")
    s += _isource(560, 235, "I_n")
    s += line(560, 170, 560, 217, INK, 2.2)
    s += line(560, 253, 560, 300, INK, 2.2)
    s += line(560, 170, 660, 170, COPPER, 2.2)
    s += line(560, 300, 660, 300, COPPER, 2.2)
    s += _vresistor(660, 195, 275, "R_n")
    s += line(660, 170, 660, 195, COPPER, 2.2)
    s += line(660, 275, 660, 300, COPPER, 2.2)
    s += line(660, 170, 740, 170, COPPER, 2.2)
    s += line(660, 300, 740, 300, COPPER, 2.2)
    s += line(740, 170, 740, 185, INK, 2.2)
    s += line(740, 285, 740, 300, INK, 2.2)
    s += _term(740, 185, "A")
    s += _term(740, 285, "B")
    # двоїстість
    s += rect(250, 330, 360, 46, "#eef7f0", INK, 1.6, 10)
    s += text(430, 352, "одне й те саме:  V_th = I_n · R_n,   R_th = R_n", 13, INK, "middle", "bold")
    s += text(430, 370, "Тевенін ↔ Нортон — повні дзеркала", 10, GREY, "middle", style="italic")
    save("fig-5-0-2-thevenin-norton.svg", s)


# ── Рис. 5.0.3 — реальна батарея = ЕРС + внутрішній опір ─────────────────────
def fig_real_battery():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Реальна батарея — це і є еквівалент Тевеніна", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "ідеальна ЕРС ε + внутрішній опір r; під навантаженням напруга на клемах просідає",
              12, GREY, "middle", style="italic")
    # пунктирна «батарея»
    s += rect(80, 110, 250, 200, "none", GREY, 1.6, 12)
    s += text(205, 130, "реальна батарея", 11, GREY, "middle", "bold", "italic")
    s += _battery(140, 230, "")
    s += text(116, 227, "ε", 13, RED, "end", "bold")
    s += line(140, 165, 140, 222, INK, 2.2)
    s += line(140, 238, 140, 290, INK, 2.2)
    s += line(140, 165, 210, 165, COPPER, 2.2)
    s += _resistor(210, 165, 60, 18, "r")
    s += line(270, 165, 310, 165, COPPER, 2.2)
    s += line(140, 290, 310, 290, COPPER, 2.2)
    # клеми
    s += line(310, 165, 360, 165, INK, 2.2)
    s += line(310, 290, 360, 290, INK, 2.2)
    s += _term(360, 165, "+")
    s += _term(360, 290, "−", "end")
    # навантаження
    s += _vresistor(440, 195, 260, "R_нав")
    s += line(360, 165, 440, 165, COPPER, 2.2)
    s += line(440, 165, 440, 195, COPPER, 2.2)
    s += line(360, 290, 440, 290, COPPER, 2.2)
    s += line(440, 260, 440, 290, COPPER, 2.2)
    s += arrow(395, 165, 425, 165, RED, 2)
    s += text(410, 153, "I", 10.5, RED, "middle", "bold", "italic")
    s += rect(540, 120, 290, 170, "#f6f8fc", INK, 1.6, 12)
    s += text(685, 148, "Без навантаження:", 12, INK, "middle", "bold")
    s += text(685, 168, "на клемах рівно ε (ЕРС)", 11, GREY, "middle")
    s += text(685, 198, "Під навантаженням:", 12, INK, "middle", "bold")
    s += text(685, 218, "V = ε − I·r  <  ε  (просідає)", 11.5, RED, "middle", "bold")
    s += text(685, 246, "що менший r, то «міцніша»", 10.5, GREY, "middle", style="italic")
    s += text(685, 264, "батарея під навантаженням", 10.5, GREY, "middle", style="italic")
    save("fig-5-0-3-real-battery.svg", s)


# ── Рис. 5.0.4 — часова лінія відкриття ──────────────────────────────────────
def fig_timeline():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 30, "Як народилася ідея еквівалента", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "двічі-тричі незалежно — ознака по-справжньому глибокої думки", 12, GREY, "middle", style="italic")
    y = 150
    s += line(80, y, 800, y, INK, 2.4)
    marks = [(150, "1853", "Гельмгольц", "попередник теореми", BLUE),
             (390, "1883", "Тевенен", "інженер телеграфу (Франція):\nджерело напруги + опір", RED),
             (650, "1926", "Нортон і Маєр", "Bell Labs (США) й Німеччина:\nджерело струму + опір", GREEN)]
    for x, yr, who, what, col in marks:
        s += line(x, y - 8, x, y + 8, col, 2.4)
        s += circle(x, y, 6, col, col, 1)
        s += text(x, y - 20, yr, 14, col, "middle", "bold")
        s += text(x, y + 34, who, 12.5, INK, "middle", "bold")
        parts = what.split("\n")
        for i, p in enumerate(parts):
            s += text(x, y + 54 + i * 16, p, 10, GREY, "middle")
    s += rect(150, 252, W - 300, 48, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 274, "Те, що кілька людей дійшли до цього незалежно, — знак, що ідея «дозріла»",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 292, "(як свого часу збереження енергії). Абстракція «чорної скриньки» виявилася універсальною.",
              10, GREY, "middle", style="italic")
    save("fig-5-0-4-timeline.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §5.1 — Реальне джерело: внутрішній опір.  Рис. 5.1.k
# ════════════════════════════════════════════════════════════════════════════

def _vi_axes(ox, oy, w, h):
    o = arrow(ox, oy, ox, oy - h, INK, 1.8)
    o += arrow(ox, oy, ox + w, oy, INK, 1.8)
    o += text(ox - 6, oy - h + 2, "V", 10.5, INK, "end", "bold")
    o += text(ox + w + 2, oy + 4, "I", 10.5, INK, "start", "bold")
    return o


# ── Рис. 5.1.1 — ідеальне vs реальне джерело ─────────────────────────────────
def fig51_ideal_vs_real():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Ідеальне джерело vs реальне", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "ідеальне тримає напругу за будь-якого струму; реальне — просідає під навантаженням",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 40, FAINT, 1.4, "4,5")
    # ── ідеальне ──
    s += text(215, 100, "Ідеальне", 14, GREEN, "middle", "bold")
    s += _battery(110, 175, "")
    s += text(86, 172, "V", 11, RED, "end", "bold")
    s += line(110, 145, 110, 167, INK, 2)
    s += line(110, 183, 110, 205, INK, 2)
    s += line(110, 145, 160, 145, COPPER, 2)
    s += line(110, 205, 160, 205, COPPER, 2)
    s += _term(160, 145, "+")
    s += _term(160, 205, "−", "end")
    s += _vi_axes(120, 330, 170, 80)
    s += line(120, 280, 280, 280, GREEN, 2.6)
    s += text(200, 270, "V = стала", 10, GREEN, "middle", "bold")
    # ── реальне ──
    s += text(645, 100, "Реальне (ε + r)", 14, RED, "middle", "bold")
    s += _battery(520, 175, "")
    s += text(498, 172, "ε", 12, RED, "end", "bold")
    s += line(520, 145, 520, 167, INK, 2)
    s += line(520, 183, 520, 205, INK, 2)
    s += line(520, 145, 565, 145, COPPER, 2)
    s += _resistor(565, 145, 50, 16, "r")
    s += line(615, 145, 650, 145, COPPER, 2)
    s += line(520, 205, 650, 205, COPPER, 2)
    s += _term(650, 145, "+")
    s += _term(650, 205, "−", "end")
    s += _vi_axes(560, 330, 200, 80)
    s += line(560, 268, 740, 322, RED, 2.6)
    s += text(690, 262, "V спадає з I", 10, RED, "middle", "bold")
    save("fig-5-1-1-ideal-vs-real.svg", s)


# ── Рис. 5.1.2 — модель: ε послідовно з r ────────────────────────────────────
def fig51_internal_r():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Модель реального джерела: ε послідовно з r", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "напруга на клемах = ЕРС мінус спад на внутрішньому опорі", 12, GREY, "middle", style="italic")
    s += rect(80, 110, 250, 200, "none", GREY, 1.6, 12)
    s += text(205, 132, "джерело", 11, GREY, "middle", "bold", "italic")
    s += _battery(140, 235, "")
    s += text(116, 232, "ε", 13, RED, "end", "bold")
    s += line(140, 170, 140, 227, INK, 2.2)
    s += line(140, 243, 140, 290, INK, 2.2)
    s += line(140, 170, 210, 170, COPPER, 2.2)
    s += _resistor(210, 170, 60, 18, "r")
    s += text(240, 150, "спад I·r", 10, BLUE, "middle", "bold")
    s += line(270, 170, 310, 170, COPPER, 2.2)
    s += line(140, 290, 310, 290, COPPER, 2.2)
    s += line(310, 170, 360, 170, INK, 2.2)
    s += line(310, 290, 360, 290, INK, 2.2)
    s += _term(360, 170, "+")
    s += _term(360, 290, "−", "end")
    s += _vresistor(440, 200, 260, "R_нав")
    s += line(360, 170, 440, 170, COPPER, 2.2)
    s += line(440, 170, 440, 200, COPPER, 2.2)
    s += line(360, 290, 440, 290, COPPER, 2.2)
    s += line(440, 260, 440, 290, COPPER, 2.2)
    s += arrow(395, 170, 425, 170, RED, 2)
    s += text(410, 158, "I", 10.5, RED, "middle", "bold", "italic")
    s += rect(540, 150, 250, 90, "#eef7f0", GREEN, 2, 12)
    s += text(665, 186, "V_клем = ε − I·r", 16, GREEN, "middle", "bold")
    s += text(665, 216, "що більший струм — то нижча напруга", 10, GREY, "middle", style="italic")
    save("fig-5-1-2-internal-r.svg", s)


# ── Рис. 5.1.3 — вольт-амперна характеристика ────────────────────────────────
def fig51_vi_characteristic():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Вольт-амперна характеристика джерела", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "пряма від ЕРС (холостий хід) до струму короткого замикання; нахил = −r", 12, GREY, "middle", style="italic")
    ox, oy = 130, 330
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += text(ox - 8, 92, "V", 12, INK, "end", "bold")
    s += arrow(ox, oy, 720, oy, INK, 2)
    s += text(724, oy + 4, "I", 12, INK, "start", "bold")
    # характеристика джерела
    eps_y, isc_x = 120, 640
    s += line(ox, eps_y, isc_x, oy, RED, 3)
    s += circle(ox, eps_y, 5, RED, RED, 1)
    s += text(ox - 10, eps_y - 6, "ε", 14, RED, "end", "bold")
    s += text(ox + 60, eps_y - 6, "холостий хід (I=0): V = ε", 10.5, RED, "start", "bold")
    s += circle(isc_x, oy, 5, RED, RED, 1)
    s += text(isc_x, oy + 20, "I_кз = ε/r", 11, RED, "middle", "bold")
    s += text(isc_x - 8, oy - 12, "коротке (V=0)", 9.5, GREY, "end", style="italic")
    s += text(420, 210, "нахил = −r", 11.5, RED, "middle", "bold", "italic")
    # навантажувальна пряма R (через початок)
    s += line(ox, oy, 600, 150, GREEN, 2.2, "5,4")
    s += text(560, 140, "лінія навантаження R", 10, GREEN, "middle", "bold")
    # робоча точка (перетин)
    px, py = 360, 222
    s += circle(px, py, 6, INK, "#fff", 2.5)
    s += line(px, py, px, oy, GREY, 1.2, "3,3")
    s += line(px, py, ox, py, GREY, 1.2, "3,3")
    s += text(px + 10, py - 8, "робоча точка", 10, INK, "start", "bold")
    s += text(W / 2, H - 12, "Перетин характеристики джерела й лінії навантаження — реальні V та I у колі.",
              10.5, GREY, "middle", style="italic")
    save("fig-5-1-3-vi-characteristic.svg", s)


# ── Рис. 5.1.4 — як виміряти r ───────────────────────────────────────────────
def fig51_measure_r():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Як виміряти внутрішній опір r", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "дві робочі точки дають r = зміна напруги / зміна струму", 12, GREY, "middle", style="italic")
    s += rect(70, 90, 360, 230, "#f6f8fc", INK, 1.5, 12)
    s += text(250, 116, "Метод двох точок", 12.5, INK, "middle", "bold")
    s += text(90, 146, "1. Без навантаження (I≈0):", 11, INK, "start", "bold")
    s += text(110, 166, "вольтметр показує V₀ ≈ ε", 10.5, GREY, "start")
    s += text(90, 196, "2. З відомим навантаженням:", 11, INK, "start", "bold")
    s += text(110, 216, "потекло I, напруга впала до V", 10.5, GREY, "start")
    s += rect(90, 236, 320, 44, "#eef7f0", GREEN, 2, 10)
    s += text(250, 263, "r = (V₀ − V) / I", 16, GREEN, "middle", "bold")
    # приклад
    s += rect(470, 90, 320, 230, "#f6f8fc", INK, 1.5, 12)
    s += text(630, 116, "Приклад", 12.5, INK, "middle", "bold")
    s += text(490, 148, "V₀ = 1.50 В  (холостий хід)", 12, INK, "start")
    s += text(490, 176, "під навантаженням 10 Ω:", 12, INK, "start")
    s += text(510, 200, "I = 0.14 А,  V = 1.43 В", 12, INK, "start")
    s += line(490, 216, 770, 216, FAINT, 1.3)
    s += text(630, 244, "r = (1.50 − 1.43)/0.14", 12.5, INK, "middle", "bold")
    s += rect(540, 258, 180, 40, "#eef7f0", GREEN, 2, 10)
    s += text(630, 284, "r ≈ 0.5 Ω", 16, GREEN, "middle", "bold")
    save("fig-5-1-4-measure-r.svg", s)


# ── Рис. 5.1.5 — приклади внутрішнього опору ─────────────────────────────────
def fig51_examples():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Внутрішній опір у житті", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "малий r — «міцне» джерело (великий струм без просідання); великий r — кволе",
              12, GREY, "middle", style="italic")
    items = [("Автоакумулятор", "r ≈ 0.005 Ω", "крутить стартер сотнями ампер", GREEN, 150),
             ("Свіжа батарейка AA", "r ≈ 0.2 Ω", "тримає звичайне навантаження", GREEN, 370),
             ("Стара батарейка", "r ≈ 2–5 Ω", "просідає, «мертва» під струмом", ORANGE, 590),
             ("Літієва «таблетка»", "r ≈ 10 Ω", "лише слабкі споживачі", RED, 805)]
    for name, rv, note, col, x in items:
        s += rect(x - 95, 100, 190, 140, "#f6f8fc", col, 1.8, 12)
        s += text(x, 128, name, 12, INK, "middle", "bold")
        s += rect(x - 70, 142, 140, 32, "#fff", col, 1.6, 8)
        s += text(x, 164, rv, 13, col, "middle", "bold")
        s += text(x, 198, note, 9.5, GREY, "middle")
        s += text(x, 216, "", 9, GREY, "middle")
    s += rect(120, 300, W - 240, 50, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 322, "Максимальний струм джерела — ε/r. Малий r → величезний можливий струм (і небезпека к.з.);",
              11, INK, "middle", "bold")
    s += text(W / 2, 340, "великий r → джерело саме себе обмежує, але «не тягне» потужних споживачів.",
              10.5, GREY, "middle", style="italic")
    save("fig-5-1-5-examples.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §5.2 — Принцип суперпозиції.  Рис. 5.2.k
# ════════════════════════════════════════════════════════════════════════════

def _3br(ox, oy, left_on, right_on, v1="V₁", v2="V₂", i3=None):
    """Триглкове коло: ліва (V₁,R₁), середня (R₃), права (V₂,R₂); ground знизу."""
    o = line(ox, oy, ox + 160, oy, COPPER, 2)           # верх (вузол A)
    o += line(ox, oy + 130, ox + 160, oy + 130, COPPER, 2)  # низ (земля)
    # ліва гілка
    if left_on:
        o += line(ox, oy, ox, oy + 22, INK, 2)
        o += _battery(ox, oy + 38, "")
        o += text(ox - 12, oy + 42, v1, 10.5, RED, "end", "bold")
        o += line(ox, oy + 54, ox, oy + 70, INK, 2)
    else:
        o += line(ox, oy, ox, oy + 70, COPPER, 2)
        o += text(ox - 12, oy + 40, "(КЗ)", 9, GREY, "end", "italic")
    o += _vresistor(ox, oy + 70, oy + 110, "R₁", "end")
    o += line(ox, oy + 110, ox, oy + 130, INK, 2)
    # середня
    o += line(ox + 80, oy, ox + 80, oy + 45, COPPER, 2)
    o += _vresistor(ox + 80, oy + 45, oy + 95, "R₃")
    o += line(ox + 80, oy + 95, ox + 80, oy + 130, COPPER, 2)
    if i3:
        o += arrow(ox + 80, oy + 60, ox + 80, oy + 84, GREEN, 2.4)
        o += text(ox + 96, oy + 76, i3, 10.5, GREEN, "start", "bold")
    # права гілка
    if right_on:
        o += line(ox + 160, oy, ox + 160, oy + 22, INK, 2)
        o += _battery(ox + 160, oy + 38, "")
        o += text(ox + 172, oy + 42, v2, 10.5, RED, "start", "bold")
        o += line(ox + 160, oy + 54, ox + 160, oy + 70, INK, 2)
    else:
        o += line(ox + 160, oy, ox + 160, oy + 70, COPPER, 2)
        o += text(ox + 172, oy + 40, "(КЗ)", 9, GREY, "start", "italic")
    o += _vresistor(ox + 160, oy + 70, oy + 110, "R₂")
    o += line(ox + 160, oy + 110, ox + 160, oy + 130, INK, 2)
    o += circle(ox + 80, oy, 4, INK, INK, 1)
    o += text(ox + 80, oy - 8, "A", 11, INK, "middle", "bold")
    return o


# ── Рис. 5.2.1 — ідея суперпозиції ───────────────────────────────────────────
def fig52_idea():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 30, "Суперпозиція: складне коло — як сума простих", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "відгук від кількох джерел = сума відгуків від кожного джерела окремо",
              12, GREY, "middle", style="italic")
    s += _3br(70, 110, True, True)
    s += text(150, 280, "обидва джерела", 11, INK, "middle", "bold")
    s += text(285, 175, "=", 28, INK, "middle", "bold")
    s += _3br(330, 110, True, False)
    s += text(410, 280, "лише V₁ (V₂ → КЗ)", 11, INK, "middle", "bold")
    s += text(545, 175, "+", 28, INK, "middle", "bold")
    s += _3br(590, 110, False, True)
    s += text(670, 280, "лише V₂ (V₁ → КЗ)", 11, INK, "middle", "bold")
    s += text(W / 2, 330, "Струми (і напруги) від кожного джерела рахують окремо, тоді додають — бо коло ЛІНІЙНЕ.",
              11, GREY, "middle", style="italic")
    save("fig-5-2-1-idea.svg", s)


# ── Рис. 5.2.2 — як «вимкнути» джерело ───────────────────────────────────────
def fig52_turn_off():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Як «вимкнути» джерело на час розрахунку", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "джерело напруги → нуль вольтів = коротке замикання; джерело струму → нуль ампер = розрив",
              11.5, GREY, "middle", style="italic")
    # напруга → КЗ
    s += text(180, 100, "Джерело напруги → КЗ (дріт)", 12.5, BLUE, "middle", "bold")
    s += _battery(110, 175, "")
    s += text(86, 172, "V", 11, RED, "end", "bold")
    s += line(110, 145, 110, 167, INK, 2)
    s += line(110, 183, 110, 205, INK, 2)
    s += arrow(150, 175, 210, 175, INK, 2.4)
    s += line(250, 145, 250, 205, INK, 3)
    s += text(250, 225, "дріт (0 В)", 10, GREY, "middle", "bold")
    # струм → розрив
    s += text(600, 100, "Джерело струму → розрив", 12.5, GREEN, "middle", "bold")
    s += _isource(520, 175, "I")
    s += arrow(560, 175, 620, 175, INK, 2.4)
    s += line(660, 145, 660, 168, INK, 3)
    s += line(660, 182, 660, 205, INK, 3)
    s += circle(660, 168, 3, "#fff", INK, 2)
    s += circle(660, 182, 3, "#fff", INK, 2)
    s += text(660, 225, "розрив (0 А)", 10, GREY, "middle", "bold")
    s += rect(140, 270, W - 280, 50, "#f6f8fc", INK, 1.5, 10)
    s += text(W / 2, 292, "«Вимкнути» джерело — це не прибрати його, а замінити на його нульовий стан:",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 310, "напругу на нуль (дріт), струм на нуль (розрив). Внутрішні опори лишаються!",
              10.5, GREY, "middle", style="italic")
    save("fig-5-2-2-turn-off.svg", s)


# ── Рис. 5.2.3 — приклад по кроках ───────────────────────────────────────────
def fig52_worked():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: струм у R₃ через суперпозицію", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "V₁=8 В, V₂=4 В, усі R=4 Ω — знайти струм у середній гілці", 12, GREY, "middle", style="italic")
    s += _3br(60, 100, True, False, i3="I′")
    s += text(140, 256, "крок 1: лише V₁", 11, INK, "middle", "bold")
    s += text(150, 274, "I′ ≈ 0.67 А", 11, GREEN, "middle", "bold")
    s += text(300, 165, "+", 26, INK, "middle", "bold")
    s += _3br(345, 100, False, True, i3="I″")
    s += text(425, 256, "крок 2: лише V₂", 11, INK, "middle", "bold")
    s += text(435, 274, "I″ ≈ 0.33 А", 11, GREEN, "middle", "bold")
    s += text(585, 165, "=", 26, INK, "middle", "bold")
    s += rect(630, 120, 220, 150, "#eef7f0", GREEN, 2, 12)
    s += text(740, 150, "крок 3: додаємо", 12.5, INK, "middle", "bold")
    s += text(740, 184, "I = I′ + I″", 14, INK, "middle", "bold")
    s += text(740, 212, "= 0.67 + 0.33", 12.5, GREY, "middle")
    s += rect(670, 224, 140, 34, "#fff", GREEN, 1.8, 8)
    s += text(740, 247, "I = 1.0 А", 16, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Кожне джерело «тягне» свою частку струму; повний струм — їхня алгебрична сума.",
              11, GREY, "middle", style="italic")
    save("fig-5-2-3-worked.svg", s)


# ── Рис. 5.2.4 — потужність НЕ додається ─────────────────────────────────────
def fig52_power_not_add():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Обережно: потужність НЕ суперпонується", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "струми й напруги додаються, а потужність — ні, бо P = I²R нелінійна",
              12, GREY, "middle", style="italic")
    # струм додається
    s += text(230, 96, "Струм — додається ✓", 13, GREEN, "middle", "bold")
    s += rect(120, 120, 60, 40, "#dcead8", GREEN, 1.6, 6)
    s += text(150, 145, "I′=2 А", 11, INK, "middle", "bold")
    s += text(205, 145, "+", 16, INK, "middle", "bold")
    s += rect(230, 120, 60, 40, "#dcead8", GREEN, 1.6, 6)
    s += text(260, 145, "I″=1 А", 11, INK, "middle", "bold")
    s += text(315, 145, "=", 16, INK, "middle", "bold")
    s += rect(340, 120, 70, 40, "#cfe0f0", BLUE, 1.6, 6)
    s += text(375, 145, "I=3 А", 12, INK, "middle", "bold")
    # потужність не додається
    s += text(230, 206, "Потужність — НІ ✗", 13, RED, "middle", "bold")
    s += text(120, 235, "P′ = 2²R", 11, INK, "start", "bold")
    s += text(120, 255, "P″ = 1²R", 11, INK, "start", "bold")
    s += text(120, 283, "P′+P″ = 5R", 12, GREY, "start", "bold")
    s += text(300, 270, "але справжня:", 11, INK, "middle")
    s += rect(390, 250, 130, 40, "#fbecea", RED, 1.8, 8)
    s += text(455, 275, "P = 3²R = 9R", 12.5, RED, "middle", "bold")
    s += text(300, 300, "9R ≠ 5R !", 13, RED, "middle", "bold")
    s += rect(560, 120, 240, 170, "#f6f8fc", INK, 1.5, 12)
    s += text(680, 150, "Чому?", 12.5, INK, "middle", "bold")
    s += text(680, 178, "Суперпозиція діє лише для", 10.5, INK, "middle")
    s += text(680, 195, "ЛІНІЙНИХ величин (∝ I).", 10.5, INK, "middle")
    s += text(680, 220, "Потужність ∝ I² — нелінійна,", 10.5, RED, "middle", "bold")
    s += text(680, 237, "тож її рахують уже з", 10.5, INK, "middle")
    s += text(680, 254, "повного струму (I=3 А),", 10.5, INK, "middle")
    s += text(680, 271, "а не складають частки.", 10.5, INK, "middle")
    save("fig-5-2-4-power-not-add.svg", s)


# ── Рис. 5.2.5 — рецепт і межі ───────────────────────────────────────────────
def fig52_recipe():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Рецепт суперпозиції та її межі", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "проста процедура — але лише для лінійних кіл", 12, GREY, "middle", style="italic")
    steps = [("1", "Лиши одне джерело", "решту «вимкни» (V→КЗ, I→розрив)"),
             ("2", "Розв'яжи це коло", "знайди потрібний струм/напругу від цього джерела"),
             ("3", "Повтори для кожного", "по черзі для всіх джерел"),
             ("4", "Додай", "алгебрична сума часток — повний відгук")]
    yy = 86
    for n, t, d in steps:
        s += circle(95, yy + 15, 15, BLUE, INK, 2)
        s += text(95, yy + 20, n, 13, "#fff", "middle", "bold")
        s += rect(122, yy, 360, 48, "#f6f8fc", INK, 1.4, 10)
        s += text(138, yy + 20, t, 12.5, INK, "start", "bold")
        s += text(138, yy + 38, d, 10.5, GREY, "start")
        yy += 60
    s += rect(510, 86, 290, 240, "#fff3e8", ORANGE, 1.6, 12)
    s += text(655, 114, "Межі застосування", 12.5, ORANGE, "middle", "bold")
    s += text(528, 144, "• ТІЛЬКИ лінійні кола", 11, INK, "start", "bold")
    s += text(540, 162, "(резистори, джерела;", 10, GREY, "start")
    s += text(540, 178, "без діодів, транзисторів)", 10, GREY, "start")
    s += text(528, 206, "• потужність НЕ додається", 11, RED, "start", "bold")
    s += text(540, 224, "(P ∝ I² — нелінійна)", 10, GREY, "start")
    s += text(528, 252, "• внутрішні опори джерел", 11, INK, "start", "bold")
    s += text(540, 270, "лишаються на місці", 10, GREY, "start")
    s += text(528, 298, "Зате будь-яке число джерел", 10.5, GREEN, "start", "bold")
    s += text(540, 314, "стає легким — по одному.", 10, GREY, "start")
    save("fig-5-2-5-recipe.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §5.3 — Теорема Тевеніна.  Рис. 5.3.k
# ════════════════════════════════════════════════════════════════════════════

def _thevenin(ox, oy, vlabel="V_th", rlabel="R_th", talab=("A", "B")):
    """Еквівалент Тевеніна: V послідовно з R, дві клеми праворуч."""
    o = _battery(ox, oy + 45, "")
    o += text(ox - 22, oy + 49, vlabel, 10.5, RED, "end", "bold")
    o += line(ox, oy, ox, oy + 37, INK, 2.2)
    o += line(ox, oy + 53, ox, oy + 90, INK, 2.2)
    o += line(ox, oy, ox + 36, oy, COPPER, 2.2)
    o += _resistor(ox + 36, oy, 60, 18, rlabel)
    o += line(ox + 96, oy, ox + 140, oy, COPPER, 2.2)
    o += line(ox, oy + 90, ox + 140, oy + 90, COPPER, 2.2)
    o += line(ox + 140, oy, ox + 140, oy + 18, INK, 2.2)
    o += line(ox + 140, oy + 72, ox + 140, oy + 90, INK, 2.2)
    o += _term(ox + 140, oy + 18, talab[0])
    o += _term(ox + 140, oy + 72, talab[1])
    return o


# ── Рис. 5.3.1 — формулювання теореми ────────────────────────────────────────
def fig53_statement():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Теорема Тевеніна: мережа = джерело + опір", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "будь-яку лінійну мережу з двох клем замінюють одним джерелом напруги й одним опором",
              11.5, GREY, "middle", style="italic")
    s += rect(90, 110, 220, 150, "#f6f8fc", GREY, 1.8, 12)
    s += text(200, 175, "будь-яка лінійна", 12.5, INK, "middle", "bold")
    s += text(200, 195, "мережа", 12.5, INK, "middle", "bold")
    s += text(200, 222, "(джерела + опори)", 10, GREY, "middle", style="italic")
    s += line(310, 150, 350, 150, INK, 2.2)
    s += line(310, 220, 350, 220, INK, 2.2)
    s += _term(350, 150, "A")
    s += _term(350, 220, "B")
    s += text(420, 178, "≡", 34, INK, "middle", "bold")
    s += _thevenin(520, 130)
    s += text(770, 185, "просто!", 12, GREEN, "middle", "bold", "italic")
    save("fig-5-3-1-statement.svg", s)


# ── Рис. 5.3.2 — що таке V_th і R_th ─────────────────────────────────────────
def fig53_vth_rth():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Два числа: V_th (холостий хід) і R_th (джерела вимкнено)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "V_th — напруга на розімкнених клемах; R_th — опір мережі з вимкненими джерелами",
              11.5, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 40, FAINT, 1.4, "4,5")
    # V_th
    s += text(215, 100, "V_th = напруга холостого ходу", 12.5, RED, "middle", "bold")
    s += rect(90, 120, 150, 130, "#f6f8fc", GREY, 1.6, 10)
    s += text(165, 190, "мережа", 11, INK, "middle", "bold")
    s += line(240, 150, 300, 150, INK, 2)
    s += line(240, 230, 300, 230, INK, 2)
    s += circle(300, 190, 22, "#fff", RED, 2.2)
    s += text(300, 196, "V", 15, RED, "middle", "bold")
    s += line(300, 168, 300, 150, INK, 2)
    s += line(300, 212, 300, 230, INK, 2)
    s += text(360, 186, "клеми РОЗІМКНЕНІ", 10, GREY, "middle", "bold")
    s += text(360, 202, "(навантаження нема)", 9.5, GREY, "middle", style="italic")
    # R_th
    s += text(645, 100, "R_th = опір при вимкнених джерелах", 12, GREEN, "middle", "bold")
    s += rect(520, 120, 150, 130, "#eef7f0", GREEN, 1.6, 10)
    s += text(595, 184, "мережа,", 11, INK, "middle", "bold")
    s += text(595, 200, "джерела → 0", 10, GREEN, "middle", "bold")
    s += line(670, 150, 730, 150, INK, 2)
    s += line(670, 230, 730, 230, INK, 2)
    s += circle(730, 190, 22, "#fff", GREEN, 2.2)
    s += text(730, 196, "Ω", 15, GREEN, "middle", "bold")
    s += line(730, 168, 730, 150, INK, 2)
    s += line(730, 212, 730, 230, INK, 2)
    s += text(790, 192, "міряємо", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "Два виміри (чи розрахунки) — і вся мережа описана. Як саме їх знаходити — у §5.5.",
              11, GREY, "middle", style="italic")
    save("fig-5-3-2-vth-rth.svg", s)


# ── Рис. 5.3.3 — сила: легко міняти навантаження ─────────────────────────────
def fig53_swap_loads():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Навіщо це: одне коло — будь-яке навантаження", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "маючи V_th і R_th, вихід для будь-якого R_нав — це простий дільник",
              12, GREY, "middle", style="italic")
    s += _thevenin(80, 120, "V_th", "R_th")
    s += text(150, 240, "еквівалент", 10.5, GREY, "middle", style="italic")
    s += arrow(240, 165, 300, 165, INK, 2.4)
    s += rect(320, 110, 480, 120, "#f6f8fc", INK, 1.4, 12)
    s += text(560, 134, "V_вих = V_th · R_нав/(R_нав + R_th)", 13.5, INK, "middle", "bold")
    loads = [("R_нав = R_th", "½ V_th"), ("R_нав ≫ R_th", "≈ V_th"), ("R_нав ≪ R_th", "≈ 0")]
    xx = 400
    for rl, vo in loads:
        s += text(xx, 172, rl, 11, INK, "middle", "bold")
        s += text(xx, 192, "→", 12, GREY, "middle")
        s += text(xx, 212, vo, 12, GREEN, "middle", "bold")
        xx += 160
    s += text(W / 2, 290, "Один раз знайшов V_th, R_th — і десятки навантажень рахуєш миттєво, без усієї мережі.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Саме тому еквівалент Тевеніна — улюблений інструмент інженера.", 10.5, GREY, "middle", style="italic")
    save("fig-5-3-3-swap-loads.svg", s)


# ── Рис. 5.3.4 — приклад: дільник → Тевенін ──────────────────────────────────
def fig53_worked():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: дільник 12 В, R₁=R₂=10к → еквівалент", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "V_th = напруга відводу (6 В); R_th = R₁∥R₂ = 5 кΩ", 12, GREY, "middle", style="italic")
    # дільник
    s += text(150, 92, "Початкове коло", 12, INK, "middle", "bold")
    s += text(110, 118, "12 В", 11, RED, "middle", "bold")
    s += line(110, 126, 110, 144, INK, 2)
    s += _vresistor(110, 144, 184, "R₁=10к", "end")
    tap = 200
    s += line(110, 184, 110, tap, COPPER, 2)
    s += circle(110, tap, 4, GREEN, GREEN, 1)
    s += line(110, tap, 110, 216, COPPER, 2)
    s += _vresistor(110, 216, 256, "R₂=10к", "end")
    s += line(110, 256, 110, 280, INK, 2)
    s += line(110, 280, 150, 280, INK, 2)
    s += line(110, 126, 150, 126, INK, 2)
    s += arrow(110 + 8, tap, 175, tap, GREEN, 2)
    s += text(180, tap + 4, "A", 11, INK, "start", "bold")
    s += text(180, 280 + 4, "B", 11, INK, "start", "bold")
    s += line(110, 280, 175, 280, INK, 2)
    s += circle(175, 280, 4, "#fff", INK, 2)
    s += circle(175, tap, 4, "#fff", INK, 2)
    s += text(300, 200, "≡", 30, INK, "middle", "bold")
    # еквівалент
    s += text(520, 92, "Еквівалент Тевеніна", 12, BLUE, "middle", "bold")
    s += _thevenin(420, 150, "6 В", "5 кΩ")
    s += rect(640, 150, 200, 110, "#eef7f0", GREEN, 2, 12)
    s += text(740, 180, "V_th = 6 В", 13, INK, "middle", "bold")
    s += text(740, 206, "(холостий хід дільника)", 9.5, GREY, "middle", style="italic")
    s += text(740, 232, "R_th = 10к∥10к = 5 кΩ", 12.5, INK, "middle", "bold")
    save("fig-5-3-4-worked.svg", s)


# ── Рис. 5.3.5 — реальне джерело = Тевенін ───────────────────────────────────
def fig53_real_source():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Усе знайоме — це вже Тевенін", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "реальна батарея (ε + r) і вихід дільника — окремі випадки еквівалента Тевеніна",
              11.5, GREY, "middle", style="italic")
    s += _thevenin(110, 110, "ε", "r")
    s += text(180, 232, "реальна батарея:", 11, INK, "middle", "bold")
    s += text(180, 250, "V_th = ε,  R_th = r", 11, GREEN, "middle", "bold")
    s += _thevenin(480, 110, "V_th", "R₁∥R₂")
    s += text(550, 232, "вихід дільника (§4.6):", 11, INK, "middle", "bold")
    s += text(550, 250, "R_th = R₁∥R₂", 11, GREEN, "middle", "bold")
    s += rect(120, 282, W - 240, 30, "#f6f8fc", INK, 1.4, 8)
    s += text(W / 2, 302, "Усюди, де є «джерело + внутрішній опір», ви вже маєте справу з еквівалентом Тевеніна.",
              11, INK, "middle", "bold")
    save("fig-5-3-5-real-source.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §5.4 — Теорема Нортона: двоїстість.  Рис. 5.4.k
# ════════════════════════════════════════════════════════════════════════════

def _norton(ox, oy, ilabel="I_n", rlabel="R_n", talab=("A", "B")):
    """Еквівалент Нортона: джерело струму паралельно з R, дві клеми праворуч."""
    o = _isource(ox, oy + 45, ilabel)
    o += line(ox, oy, ox, oy + 27, INK, 2.2)
    o += line(ox, oy + 63, ox, oy + 90, INK, 2.2)
    o += line(ox, oy, ox + 140, oy, COPPER, 2.2)
    o += line(ox, oy + 90, ox + 140, oy + 90, COPPER, 2.2)
    o += _vresistor(ox + 70, oy + 18, oy + 72, rlabel)
    o += line(ox + 70, oy, ox + 70, oy + 18, COPPER, 2.2)
    o += line(ox + 70, oy + 72, ox + 70, oy + 90, COPPER, 2.2)
    o += line(ox + 140, oy, ox + 140, oy + 18, INK, 2.2)
    o += line(ox + 140, oy + 72, ox + 140, oy + 90, INK, 2.2)
    o += _term(ox + 140, oy + 18, talab[0])
    o += _term(ox + 140, oy + 72, talab[1])
    return o


# ── Рис. 5.4.1 — формулювання теореми Нортона ────────────────────────────────
def fig54_statement():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Теорема Нортона: мережа = джерело струму + опір", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "дзеркало Тевеніна: джерело струму I_n паралельно з опором R_n",
              11.5, GREY, "middle", style="italic")
    s += rect(90, 110, 220, 150, "#f6f8fc", GREY, 1.8, 12)
    s += text(200, 178, "будь-яка лінійна", 12.5, INK, "middle", "bold")
    s += text(200, 198, "мережа", 12.5, INK, "middle", "bold")
    s += line(310, 150, 350, 150, INK, 2.2)
    s += line(310, 220, 350, 220, INK, 2.2)
    s += _term(350, 150, "A")
    s += _term(350, 220, "B")
    s += text(420, 178, "≡", 34, INK, "middle", "bold")
    s += _norton(520, 130)
    s += text(770, 185, "теж просто!", 11.5, GREEN, "middle", "bold", "italic")
    save("fig-5-4-1-statement.svg", s)


# ── Рис. 5.4.2 — I_n і R_n ───────────────────────────────────────────────────
def fig54_in_rn():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Два числа Нортона: I_n (коротке) і R_n (= R_th)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "I_n — струм через ЗАМКНЕНІ клеми; R_n — той самий опір, що й у Тевеніна",
              11.5, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 40, FAINT, 1.4, "4,5")
    # I_n
    s += text(215, 100, "I_n = струм короткого замикання", 12, RED, "middle", "bold")
    s += rect(90, 120, 150, 130, "#f6f8fc", GREY, 1.6, 10)
    s += text(165, 190, "мережа", 11, INK, "middle", "bold")
    s += line(240, 150, 300, 150, INK, 2)
    s += line(240, 230, 300, 230, INK, 2)
    s += circle(300, 190, 20, "#fff", RED, 2.2)
    s += text(300, 196, "A", 14, RED, "middle", "bold")
    s += line(300, 170, 300, 150, INK, 2)
    s += line(300, 210, 300, 230, INK, 2)
    s += text(360, 184, "клеми ЗАМКНЕНІ", 10, GREY, "middle", "bold")
    s += text(360, 200, "(дріт; міряємо струм)", 9.5, GREY, "middle", style="italic")
    # R_n
    s += text(645, 100, "R_n = опір при вимкнених джерелах", 11.5, GREEN, "middle", "bold")
    s += rect(520, 120, 150, 130, "#eef7f0", GREEN, 1.6, 10)
    s += text(595, 184, "мережа,", 11, INK, "middle", "bold")
    s += text(595, 200, "джерела → 0", 10, GREEN, "middle", "bold")
    s += line(670, 150, 730, 150, INK, 2)
    s += line(670, 230, 730, 230, INK, 2)
    s += circle(730, 190, 20, "#fff", GREEN, 2.2)
    s += text(730, 196, "Ω", 14, GREEN, "middle", "bold")
    s += line(730, 170, 730, 150, INK, 2)
    s += line(730, 210, 730, 230, INK, 2)
    s += text(W / 2, H - 14, "R_n = R_th — той самий опір. Різниця лише в тому, що міряємо: струм (Нортон) чи напругу (Тевенін).",
              10.5, GREY, "middle", style="italic")
    save("fig-5-4-2-in-rn.svg", s)


# ── Рис. 5.4.3 — перетворення джерел ─────────────────────────────────────────
def fig54_transformation():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Перетворення джерел: Тевенін ↔ Нортон", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "одне й те саме коло у двох виглядах — переходять одне в одне за V = I·R",
              12, GREY, "middle", style="italic")
    s += text(180, 96, "Тевенін", 13, BLUE, "middle", "bold")
    s += _thevenin(110, 130, "V_th", "R")
    s += text(640, 96, "Нортон", 13, GREEN, "middle", "bold")
    s += _norton(560, 130, "I_n", "R")
    s += text(W / 2, 175, "↔", 34, INK, "middle", "bold")
    s += rect(300, 250, 220, 90, "#eef7f0", INK, 1.8, 12)
    s += text(410, 278, "V_th = I_n · R", 14, INK, "middle", "bold")
    s += text(410, 304, "I_n = V_th / R", 14, INK, "middle", "bold")
    s += text(410, 328, "опір R — той самий", 10, GREY, "middle", style="italic")
    save("fig-5-4-3-transformation.svg", s)


# ── Рис. 5.4.4 — коли який зручніший ─────────────────────────────────────────
def fig54_when():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Коли який зручніший", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "вони рівносильні — обирають за тим, що простіше складати", 12, GREY, "middle", style="italic")
    s += rect(80, 90, 330, 210, "#eaf0fb", BLUE, 1.8, 12)
    s += text(245, 118, "Тевенін зручний коли…", 13, BLUE, "middle", "bold")
    s += text(100, 150, "• елементи йдуть ПОСЛІДОВНО", 11, INK, "start", "bold")
    s += text(100, 176, "• цікавить НАПРУГА на навантаженні", 11, INK, "start")
    s += text(100, 202, "• джерело «напругове» (батарея,", 11, INK, "start")
    s += text(115, 220, "блок живлення)", 11, INK, "start")
    s += text(245, 262, "напруга + послідовний опір", 10.5, GREY, "middle", style="italic")
    s += rect(440, 90, 330, 210, "#eef7f0", GREEN, 1.8, 12)
    s += text(605, 118, "Нортон зручний коли…", 13, GREEN, "middle", "bold")
    s += text(460, 150, "• елементи йдуть ПАРАЛЕЛЬНО", 11, INK, "start", "bold")
    s += text(460, 176, "• цікавить СТРУМ у гілці", 11, INK, "start")
    s += text(460, 202, "• джерело «струмове» (давач,", 11, INK, "start")
    s += text(475, 220, "транзистор як джерело струму)", 11, INK, "start")
    s += text(605, 262, "струм + паралельний опір", 10.5, GREY, "middle", style="italic")
    save("fig-5-4-4-when.svg", s)


# ── Рис. 5.4.5 — приклад перетворення ────────────────────────────────────────
def fig54_worked():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Приклад: Тевенін 6 В / 5 кΩ → Нортон", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "той самий вузол (вихід дільника §5.3) у формі Нортона", 12, GREY, "middle", style="italic")
    s += _thevenin(90, 120, "6 В", "5к")
    s += text(160, 240, "Тевенін", 11, BLUE, "middle", "bold")
    s += text(330, 175, "→", 30, INK, "middle", "bold")
    s += _norton(400, 120, "1.2 мА", "5к")
    s += text(470, 240, "Нортон", 11, GREEN, "middle", "bold")
    s += rect(620, 120, 180, 110, "#eef7f0", GREEN, 2, 12)
    s += text(710, 148, "I_n = V_th/R_th", 12, INK, "middle", "bold")
    s += text(710, 170, "= 6/5000", 11.5, GREY, "middle")
    s += text(710, 190, "= 1.2 мА", 13, GREEN, "middle", "bold")
    s += text(710, 216, "R_n = 5 кΩ (те саме)", 11, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Перевірка: холостий хід Нортона = I_n·R_n = 1.2 мА · 5 кΩ = 6 В = V_th ✓",
              10.5, GREY, "middle", style="italic")
    save("fig-5-4-5-worked.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §5.5 — Як знайти Vth, Rth.  Рис. 5.5.k
# ════════════════════════════════════════════════════════════════════════════

def _example(ox, oy, src_on=True):
    """Приклад: 12 В, R₁=6 послідовно, R₂=3 до землі; клеми праворуч у (ox+170, oy) і (ox+170, oy+110)."""
    o = line(ox, oy, ox, oy + 110, INK, 2)
    if src_on:
        o = ""
        o += line(ox, oy, ox, oy + 47, INK, 2)
        o += _battery(ox, oy + 55, "")
        o += line(ox, oy + 63, ox, oy + 110, INK, 2)
        o += text(ox - 12, oy + 59, "12В", 9.5, RED, "end", "bold")
    else:
        o = line(ox, oy, ox, oy + 110, INK, 2)
        o += text(ox - 12, oy + 59, "(КЗ)", 8.5, GREY, "end", "italic")
    o += line(ox, oy, ox + 28, oy, COPPER, 2)
    o += _resistor(ox + 28, oy, 50, 14, "R₁=6")
    o += line(ox + 78, oy, ox + 120, oy, COPPER, 2)
    o += circle(ox + 120, oy, 3, INK, INK, 1)
    o += _vresistor(ox + 120, oy + 27, oy + 83, "R₂=3", "end")
    o += line(ox + 120, oy, ox + 120, oy + 27, COPPER, 2)
    o += line(ox + 120, oy + 83, ox + 120, oy + 110, COPPER, 2)
    o += line(ox, oy + 110, ox + 120, oy + 110, COPPER, 2)
    o += line(ox + 120, oy, ox + 170, oy, INK, 2)
    o += line(ox + 120, oy + 110, ox + 170, oy + 110, INK, 2)
    return o


# ── Рис. 5.5.1 — три способи знайти R_th ─────────────────────────────────────
def fig55_three_methods():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Три способи знайти R_th (і V_th)", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "V_th — завжди напруга холостого ходу; а R_th дістають по-різному", 12, GREY, "middle", style="italic")
    rows = [("1", "R_th = V_th / I_кз", "поділити напругу холостого ходу на струм короткого", "універсальний", BLUE),
            ("2", "вимкнути джерела → згорнути", "джерела в нуль, далі звичайне послідовно/паралельно", "для незалежних джерел", GREEN),
            ("3", "пробне джерело", "джерела off; подати V_проб, виміряти I → R = V/I", "для залежних джерел", ORANGE)]
    yy = 92
    for n, t, d, when, col in rows:
        s += circle(95, yy + 26, 17, col, INK, 2)
        s += text(95, yy + 31, n, 14, "#fff", "middle", "bold")
        s += rect(125, yy, 660, 70, "#f6f8fc", col, 1.6, 10)
        s += text(145, yy + 26, t, 13.5, INK, "start", "bold")
        s += text(145, yy + 48, d, 11, GREY, "start")
        s += text(770, yy + 26, when, 10, col, "end", "bold", "italic")
        yy += 84
    save("fig-5-5-1-three-methods.svg", s)


# ── Рис. 5.5.2 — спосіб 1: холостий хід + коротке ────────────────────────────
def fig55_oc_sc():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Спосіб 1: холостий хід і коротке замикання", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "виміряй (порахуй) V_th розімкнутим, I_кз замкнутим — і R_th = V_th/I_кз",
              11.5, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, 250, FAINT, 1.4, "4,5")
    # холостий хід
    s += text(210, 98, "Клеми РОЗІМКНЕНІ → V_th", 11.5, RED, "middle", "bold")
    s += _example(110, 130)
    s += circle(310, 185, 18, "#fff", RED, 2.2)
    s += text(310, 191, "V", 13, RED, "middle", "bold")
    s += line(310, 167, 310, 130, INK, 2)
    s += line(310, 203, 310, 240, INK, 2)
    s += text(345, 186, "V_th = 4 В", 11, RED, "start", "bold")
    # коротке
    s += text(640, 98, "Клеми ЗАМКНЕНІ → I_кз", 11.5, GREEN, "middle", "bold")
    s += _example(540, 130)
    s += line(710, 130, 745, 130, INK, 2)
    s += circle(745, 185, 18, "#fff", GREEN, 2.2)
    s += text(745, 191, "A", 13, GREEN, "middle", "bold")
    s += line(745, 167, 745, 130, INK, 2)
    s += line(745, 203, 745, 240, INK, 2)
    s += line(710, 240, 745, 240, INK, 2)
    s += text(760, 150, "I_кз = 2 А", 10.5, GREEN, "start", "bold")
    s += rect(250, 290, 360, 50, "#eef7f0", GREEN, 2, 12)
    s += text(430, 320, "R_th = V_th / I_кз = 4/2 = 2 Ω", 15, GREEN, "middle", "bold")
    save("fig-5-5-2-oc-sc.svg", s)


# ── Рис. 5.5.3 — спосіб 2: вимкнути джерела й згорнути ───────────────────────
def fig55_deactivate():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Спосіб 2: вимкнути джерела й згорнути опір", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "джерело напруги → КЗ; тоді з клем видно просто R₁∥R₂", 12, GREY, "middle", style="italic")
    s += _example(120, 120, src_on=False)
    s += text(180, 260, "джерело вимкнено (КЗ)", 10.5, GREY, "middle", style="italic")
    s += arrow(310, 175, 380, 175, INK, 2.4)
    s += text(345, 162, "дивимось", 9.5, GREY, "middle", style="italic")
    s += text(345, 192, "із клем", 9.5, GREY, "middle", style="italic")
    s += rect(420, 130, 360, 120, "#eef7f0", GREEN, 2, 12)
    s += text(600, 160, "R₁ і R₂ опиняються паралельними", 12, INK, "middle", "bold")
    s += text(600, 196, "R_th = R₁ ∥ R₂ = 6 ∥ 3", 13.5, INK, "middle", "bold")
    s += text(600, 228, "= 18/9 = 2 Ω", 14, GREEN, "middle", "bold")
    save("fig-5-5-3-deactivate.svg", s)


# ── Рис. 5.5.4 — спосіб 3: пробне джерело ────────────────────────────────────
def fig55_test_source():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Спосіб 3: пробне джерело (для залежних джерел)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "коли просте згортання не працює — подаємо пробу й ділимо",
              12, GREY, "middle", style="italic")
    s += rect(110, 110, 200, 150, "#f6f8fc", GREY, 1.8, 12)
    s += text(210, 178, "мережа,", 12, INK, "middle", "bold")
    s += text(210, 198, "власні джерела → 0", 11, GREEN, "middle", "bold")
    s += line(310, 150, 380, 150, INK, 2)
    s += line(310, 220, 380, 220, INK, 2)
    s += _term(380, 150, "A")
    s += _term(380, 220, "B", "end")
    # пробне джерело
    s += _battery(470, 185, "")
    s += text(470, 150, "V_проб", 10.5, RED, "middle", "bold")
    s += line(470, 162, 470, 158, INK, 0)
    s += line(380, 150, 470, 150, INK, 2)
    s += line(380, 220, 470, 220, INK, 2)
    s += line(470, 150, 470, 173, INK, 2)
    s += line(470, 197, 470, 220, INK, 2)
    s += arrow(415, 150, 445, 150, RED, 2)
    s += text(430, 138, "I_проб", 10, RED, "middle", "bold")
    s += rect(560, 130, 230, 110, "#eef7f0", GREEN, 2, 12)
    s += text(675, 160, "подай V_проб,", 11.5, INK, "middle", "bold")
    s += text(675, 180, "виміряй I_проб:", 11.5, INK, "middle", "bold")
    s += text(675, 212, "R_th = V_проб / I_проб", 13.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Цей спосіб працює навіть там, де є залежні джерела (підсилювачі) — їх не «вимкнути».",
              10.5, GREY, "middle", style="italic")
    save("fig-5-5-4-test-source.svg", s)


# ── Рис. 5.5.5 — повний приклад ──────────────────────────────────────────────
def fig55_worked():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Повний приклад: знаходимо еквівалент Тевеніна", 18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "12 В, R₁=6 Ω послідовно, R₂=3 Ω до землі — клеми на R₂", 12, GREY, "middle", style="italic")
    s += _example(90, 110)
    s += text(150, 248, "початкове коло", 10.5, GREY, "middle", style="italic")
    s += rect(330, 96, 250, 120, "#eaf0fb", BLUE, 1.6, 12)
    s += text(455, 122, "1) V_th — холостий хід:", 11.5, BLUE, "middle", "bold")
    s += text(455, 148, "дільник R₂/(R₁+R₂)", 11, INK, "middle")
    s += text(455, 172, "V_th = 12·3/(6+3)", 11.5, INK, "middle", "bold")
    s += text(455, 196, "= 4 В", 14, BLUE, "middle", "bold")
    s += rect(330, 232, 250, 120, "#eef7f0", GREEN, 1.6, 12)
    s += text(455, 258, "2) R_th — джерело в КЗ:", 11.5, GREEN, "middle", "bold")
    s += text(455, 284, "R₁ ∥ R₂ = 6∥3", 11.5, INK, "middle", "bold")
    s += text(455, 308, "= 2 Ω", 14, GREEN, "middle", "bold")
    s += text(455, 332, "(перевірка: V_th/I_кз=4/2=2 ✓)", 9, GREY, "middle", style="italic")
    s += text(640, 130, "Результат:", 12, INK, "middle", "bold")
    s += _thevenin(630, 160, "4 В", "2 Ω")
    save("fig-5-5-5-worked.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §5.6 — Узгодження й максимальна передача потужності.  Рис. 5.6.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 5.6.1 — питання: яке навантаження бере найбільше? ────────────────────
def fig56_question():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 30, "Питання: яке навантаження бере найбільшу потужність?", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "джерело має V_th і R_th; міняємо R_нав — і потужність у ньому змінюється",
              12, GREY, "middle", style="italic")
    s += _thevenin(110, 120, "V_th", "R_th")
    # навантаження (змінне)
    s += _vresistor(290, 150, 220, "R_нав")
    s += line(250, 138, 290, 138, COPPER, 2.2)
    s += line(290, 138, 290, 150, COPPER, 2.2)
    s += line(250, 228, 290, 228, COPPER, 2.2)
    s += line(290, 220, 290, 228, COPPER, 2.2)
    s += arrow(272, 145, 300, 225, ORANGE, 1.8)
    s += text(312, 190, "змінне", 9.5, ORANGE, "start", "italic")
    # дві крайнощі
    s += rect(400, 110, 390, 80, "#fbecea", RED, 1.6, 10)
    s += text(595, 134, "R_нав → 0 (майже КЗ):", 11.5, RED, "middle", "bold")
    s += text(595, 156, "великий струм, та напруга на ньому ≈ 0", 10.5, INK, "middle")
    s += text(595, 176, "→ потужність мала", 11, RED, "middle", "bold")
    s += rect(400, 200, 390, 80, "#eaf0fb", BLUE, 1.6, 10)
    s += text(595, 224, "R_нав → ∞ (майже розрив):", 11.5, BLUE, "middle", "bold")
    s += text(595, 246, "велика напруга, та струм ≈ 0", 10.5, INK, "middle")
    s += text(595, 266, "→ потужність теж мала", 11, BLUE, "middle", "bold")
    s += rect(150, 300, W - 300, 44, "#eef7f0", GREEN, 1.8, 10)
    s += text(W / 2, 327, "Отже, максимум — десь ПОСЕРЕДИНІ. Де саме?", 13, GREEN, "middle", "bold")
    save("fig-5-6-1-question.svg", s)


# ── Рис. 5.6.2 — крива потужності ────────────────────────────────────────────
def fig56_power_curve():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Крива потужності: максимум при R_нав = R_th", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "потужність у навантаженні піка́є рівно тоді, коли воно дорівнює опору джерела",
              11.5, GREY, "middle", style="italic")
    ox, oy, topy = 120, 330, 95
    s += arrow(ox, oy, 740, oy, INK, 2)
    s += text(744, oy + 4, "R_нав", 12, INK, "start")
    s += arrow(ox, oy, ox, topy, INK, 2)
    s += text(ox - 8, topy - 4, "P у навантаженні", 11.5, INK, "end")
    xscale = (700 - ox) / 6.0
    pscale = (oy - topy) / 0.25 * 0.92
    pts = []
    for k in range(0, 121):
        x = k / 20.0
        P = x / (x + 1) ** 2
        pts.append((ox + x * xscale, oy - P * pscale))
    s += polyline(pts, RED, 3)
    for t in (1, 2, 3, 4, 5):
        s += line(ox + t * xscale, oy, ox + t * xscale, oy + 5, INK, 1.4)
    s += text(ox + 1 * xscale, oy + 20, "R_th", 11, GREEN, "middle", "bold")
    s += text(ox + 3 * xscale, oy + 20, "3·R_th", 10, GREY, "middle")
    s += text(ox + 5 * xscale, oy + 20, "5·R_th", 10, GREY, "middle")
    px, py = ox + 1 * xscale, oy - 0.25 * pscale
    s += line(px, py, px, oy, GREEN, 1.4, "3,3")
    s += line(ox, py, px, py, GREEN, 1.4, "3,3")
    s += circle(px, py, 6, GREEN, "#fff", 2.5)
    s += text(px + 12, py - 6, "ПІК: R_нав = R_th", 12, GREEN, "start", "bold")
    s += text(ox - 8, py + 4, "P_max", 10.5, GREEN, "end", "bold")
    save("fig-5-6-2-power-curve.svg", s)


# ── Рис. 5.6.3 — P_max = V²/(4R_th) ──────────────────────────────────────────
def fig56_pmax():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "При узгодженні: P_max = V_th² / (4·R_th)", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "коли R_нав = R_th, на навантаженні падає рівно половина V_th", 12, GREY, "middle", style="italic")
    s += _thevenin(110, 110, "V_th", "R_th")
    s += _vresistor(290, 140, 210, "R_нав = R_th")
    s += line(250, 128, 290, 128, COPPER, 2.2)
    s += line(290, 128, 290, 140, COPPER, 2.2)
    s += line(250, 218, 290, 218, COPPER, 2.2)
    s += line(290, 210, 290, 218, COPPER, 2.2)
    s += rect(440, 96, 350, 200, "#eef7f0", GREEN, 1.8, 12)
    s += text(615, 126, "R_нав = R_th  (узгодження)", 12.5, INK, "middle", "bold")
    s += text(460, 158, "напруга ділиться навпіл:", 11, INK, "start")
    s += text(475, 178, "V_нав = V_th / 2", 12.5, INK, "start", "bold")
    s += text(460, 206, "струм:", 11, INK, "start")
    s += text(475, 226, "I = V_th / (2·R_th)", 12.5, INK, "start", "bold")
    s += rect(460, 244, 310, 40, "#fff", GREEN, 2, 10)
    s += text(615, 270, "P_max = V_th² / (4·R_th)", 15, GREEN, "middle", "bold")
    save("fig-5-6-3-pmax.svg", s)


# ── Рис. 5.6.4 — ціна узгодження: ККД лише 50% ───────────────────────────────
def fig56_efficiency():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Ціна узгодження: при R_нав = R_th ККД лише 50 %", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "максимум потужності ≠ максимум ефективності — половина гине на R_th",
              11.5, GREY, "middle", style="italic")
    ox, oy, topy = 120, 330, 95
    s += arrow(ox, oy, 740, oy, INK, 2)
    s += text(744, oy + 4, "R_нав", 12, INK, "start")
    s += arrow(ox, oy, ox, topy, INK, 2)
    xscale = (700 - ox) / 6.0
    yscale = (oy - topy)
    # потужність (нормована до піку 1)
    pp = []
    for k in range(0, 121):
        x = k / 20.0
        P = (x / (x + 1) ** 2) / 0.25
        pp.append((ox + x * xscale, oy - P * yscale * 0.92))
    s += polyline(pp, RED, 2.6)
    s += text(ox + 1.05 * xscale, oy - 0.92 * yscale - 6, "потужність (норм.)", 10.5, RED, "start", "bold")
    # ефективність x/(x+1)
    ee = []
    for k in range(0, 121):
        x = k / 20.0
        eta = x / (x + 1)
        ee.append((ox + x * xscale, oy - eta * yscale * 0.92))
    s += polyline(ee, BLUE, 2.6)
    s += text(ox + 5.1 * xscale, oy - (5 / 6) * yscale * 0.92 - 4, "ККД", 11, BLUE, "start", "bold")
    # позначка x=1
    s += line(ox + xscale, oy, ox + xscale, topy + 6, GREEN, 1.3, "3,3")
    s += text(ox + xscale, oy + 18, "R_th", 11, GREEN, "middle", "bold")
    s += circle(ox + xscale, oy - 0.5 * yscale * 0.92, 5, BLUE, "#fff", 2)
    s += text(ox + xscale + 10, oy - 0.5 * yscale * 0.92 + 4, "ККД = 50 %", 11, BLUE, "start", "bold")
    s += text(W / 2, H - 14, "Хочеш максимум ПОТУЖНОСТІ — бери R_нав=R_th (ККД 50%). Хочеш ЕФЕКТИВНІСТЬ — бери R_нав ≫ R_th.",
              10.5, GREY, "middle", style="italic")
    save("fig-5-6-4-efficiency.svg", s)


# ── Рис. 5.6.5 — коли узгоджувати, а коли ні ─────────────────────────────────
def fig56_when():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Коли узгоджувати, а коли — ні", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "узгодження — заради максимуму СИГНАЛУ; передача енергії — заради ЕФЕКТИВНОСТІ",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 90, 340, 215, "#eaf0fb", BLUE, 1.8, 12)
    s += text(240, 116, "Узгоджувати (R_нав = R_th)", 12.5, BLUE, "middle", "bold")
    s += text(90, 146, "коли цінний кожен ват СИГНАЛУ:", 11, INK, "start", "bold")
    s += text(100, 170, "• антени, радіо, ВЧ (хвильовий 50 Ω)", 10.5, INK, "start")
    s += text(100, 192, "• лінії зв'язку, узгоджувальні кола", 10.5, INK, "start")
    s += text(100, 214, "• деякі аудіокаскади", 10.5, INK, "start")
    s += text(240, 250, "ефективність 50 % — прийнятна,", 10, GREY, "middle", style="italic")
    s += text(240, 266, "бо потужності й так мало", 10, GREY, "middle", style="italic")
    s += rect(440, 90, 340, 215, "#eef7f0", GREEN, 1.8, 12)
    s += text(610, 116, "НЕ узгоджувати (R_нав ≫ R_th)", 12.5, GREEN, "middle", "bold")
    s += text(460, 146, "коли важлива ЕФЕКТИВНІСТЬ:", 11, INK, "start", "bold")
    s += text(470, 170, "• живлення приладів від мережі/батареї", 10.5, INK, "start")
    s += text(470, 192, "• усе силове: мотори, нагрівачі, USB", 10.5, INK, "start")
    s += text(470, 214, "• джерело має малий R_th («жорстке»)", 10.5, INK, "start")
    s += text(610, 250, "навантаження ≫ R_th → втрати малі,", 10, GREY, "middle", style="italic")
    s += text(610, 266, "ККД близький до 100 %", 10, GREY, "middle", style="italic")
    save("fig-5-6-5-when.svg", s)


# ═══ 🔌 Вставка до 5.6 — термінатор і атенюатор ═════════════════════════════
def _gnd3(s_x, s_y, col="#1b1b1b"):
    out = ""
    for i, wd in enumerate([12, 8, 4]):
        out += line(s_x - wd, s_y + i * 4, s_x + wd, s_y + i * 4, col, 2)
    return out


def fig_terminator():
    import math
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 30, "Термінатор: узгоджене навантаження гасить відбиття", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "кінець лінії без узгодження відбиває швидкий сигнал (дзвін); 50-Ω термінатор його поглинає",
              10, GREY, "middle", style="italic")
    s += text(170, 92, "Без термінатора (відкритий кінець)", 11, "#c0271e", "middle", "bold")
    yT = 142
    s += line(70, yT, 330, yT, INK, 3)
    s += line(330, yT - 12, 330, yT + 12, INK, 2)
    s += arrow(120, yT - 20, 180, yT - 20, "#1f8a3b", 2); s += text(150, yT - 28, "хвиля →", 8.5, "#1f8a3b", "middle", "bold")
    s += arrow(300, yT + 20, 240, yT + 20, "#c0271e", 2); s += text(278, yT + 32, "← відбита", 8.5, "#c0271e", "middle", "bold")
    pts = [(370 + i * 4, yT - 26 * math.exp(-i / 18.0) * math.sin(i / 3.0)) for i in range(0, 110)]
    s += polyline(pts, "#c0271e", 2)
    s += text(560, yT - 40, "дзвін / спотворення", 9.5, "#c0271e", "middle", "bold")
    s += text(170, 234, "З 50-Ω термінатором", 11, "#1f8a3b", "middle", "bold")
    yB = 286
    s += line(70, yB, 300, yB, INK, 3)
    s += rect(300, yB - 14, 46, 28, "#eef7f0", "#1f8a3b", 2, 4); s += text(323, yB + 5, "50Ω", 10, "#1f8a3b", "middle", "bold")
    s += line(323, yB + 14, 323, yB + 30, INK, 2); s += _gnd3(323, yB + 30)
    s += arrow(120, yB - 20, 180, yB - 20, "#1f8a3b", 2); s += text(150, yB - 28, "хвиля →", 8.5, "#1f8a3b", "middle", "bold")
    s += line(400, yB, 700, yB, "#1f8a3b", 2)
    s += text(560, yB - 14, "поглинута → чистий сигнал", 9.5, "#1f8a3b", "middle", "bold")
    s += rect(120, 352, 640, 34, "#f7f7f7", GREY, 1.4, 8)
    s += text(440, 366, "Лінія має закінчуватись опором Z₀ (50 чи 75 Ω) — інакше швидкий фронт відбивається назад.",
              9.5, INK, "middle", "bold")
    s += text(440, 381, "Термінатор на скопі: вхід 1 МΩ доповнюють 50-Ω «прохідним» (feedthrough) під ВЧ-кабель.",
              9, GREY, "middle", style="italic")
    save("fig-5-6c-1-terminator.svg", s)


def fig_attenuator():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Атенюатор: ріже рівень, зберігаючи 50 Ом з обох боків", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "це резистивний дільник (П-схема), розрахований так, щоб обидва порти лишались 50-омними",
              10, GREY, "middle", style="italic")
    s += line(80, 150, 250, 150, INK, 2)
    s += line(610, 150, 780, 150, INK, 2)
    s += line(250, 150, 330, 150, INK, 2); s += line(530, 150, 610, 150, INK, 2)
    s += rect(330, 138, 200, 24, "#fff", "#8a8a8a", 2, 5); s += text(430, 155, "послідовний R", 9.5, INK, "middle", "bold")
    for x in [250, 610]:
        s += line(x, 150, x, 208, INK, 2)
        s += rect(x - 12, 208, 24, 42, "#fff", "#8a8a8a", 1.6, 4); s += text(x, 233, "R", 9, INK, "middle", "bold")
        s += line(x, 250, x, 264, INK, 2); s += _gnd3(x, 264)
    s += text(165, 138, "50 Ω →", 9, "#1f47b5", "middle", "bold")
    s += text(700, 138, "→ 50 Ω", 9, "#1f47b5", "middle", "bold")
    s += text(430, 298, "П-схема: один послідовний + два паралельні резистори.", 9.5, GREY, "middle", style="italic")
    s += text(430, 320, "Ріже сигнал на фіксовані дБ (×10 = −20 дБ), та з обох боків — рівно 50 Ω.", 10, INK, "middle", "bold")
    s += rect(120, 340, 620, 28, "#fff8ee", ORANGE, 1.4, 8)
    s += text(430, 358, "Простий дільник зіпсував би узгодження; атенюатор спеціально тримає 50 Ω.", 9.5, INK, "middle", "bold")
    save("fig-5-6c-2-attenuator.svg", s)


# ═══ 📜 Історія до 5.6 — звідки 50 Ом ═══════════════════════════════════════
def fig_coax_three_optima():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Три оптимуми коаксіалу — і компроміс 50 Ом", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "для повітряного діелектрика різні «найкраще» лежать при різних опорах; 50 Ом — їхня золота середина",
              9.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 90, 330, 820, 102
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "хвильовий опір Z₀, Ω", 10.5, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8); s += text(ox - 6, ayt - 10, "«добре»", 9.5, INK, "start", "bold")

    def X(Z):
        return ox + (Z - 20) / 70.0 * (axr - 30 - ox)

    def Y(f):
        return oy - f * (oy - ayt)

    for Z in [20, 30, 40, 50, 60, 70, 77, 90]:
        s += line(X(Z), oy - 4, X(Z), oy + 4, INK, 1.2)
        s += text(X(Z), oy + 18, str(Z), 8.5, GREY, "middle")

    def curve(peak, col, lab):
        pts = []
        for i in range(0, 101):
            Z = 20 + i / 100.0 * 70
            f = max(0.0, 1 - ((Z - peak) / 45.0) ** 2)
            pts.append((X(Z), Y(f)))
        return polyline(pts, col, 2.4) + text(X(peak), Y(1) - 8, lab, 9, col, "middle", "bold")

    s += curve(30, "#1f8a3b", "потужність (~30)")
    s += curve(60, "#1f47b5", "напруга (~60)")
    s += curve(77, "#e08030", "низькі втрати (~77)")
    s += line(X(50), Y(1.06), X(50), oy, "#c0271e", 2, "5 4")
    s += text(X(50), Y(1.1), "50 Ω — компроміс", 10, "#c0271e", "middle", "bold")
    s += rect(150, 352, 600, 42, "#fff8ee", ORANGE, 1.4, 8)
    s += text(450, 371, "Жоден опір не дає всього: 50 Ом — середина між потужністю (30) і втратами (77),", 9.5, INK, "middle", "bold")
    s += text(450, 386, "трохи зміщена до напруги (60), бо саме пробій губить кабель.", 9, GREY, "middle", style="italic")
    save("fig-5-6i-1-coax-three-optima.svg", s)


def fig_coax_50_vs_75():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "50 Ом проти 75 Ом: два стандарти під дві потреби", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "50 Ом — баланс для ВЧ-потужності; 75 Ом — мінімум втрат для слабкого сигналу",
              10, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 28, FAINT, 1.5)
    s += circle(225, 128, 38, "#fff8ee", ORANGE, 2.5); s += text(225, 136, "50 Ω", 16, "#c0271e", "middle", "bold")
    s += text(225, 188, "Передавачі, ВЧ-потужність", 11, INK, "middle", "bold")
    s += text(225, 212, "• компроміс: потужність (30)", 9.5, INK, "middle")
    s += text(225, 228, "  + втрати (77) + напруга (60)", 9.5, INK, "middle")
    s += text(225, 248, "• кругле число для розрахунків", 9.5, GREY, "middle")
    s += text(225, 264, "• стандартні труби давали ≈51.5 Ω", 9.5, GREY, "middle")
    s += text(225, 300, "де важлива ПОТУЖНІСТЬ", 10, "#c0271e", "middle", "bold")
    s += circle(635, 128, 38, "#eef2fb", "#1f47b5", 2.5); s += text(635, 136, "75 Ω", 16, "#1f47b5", "middle", "bold")
    s += text(635, 188, "ТБ, відео, антени", 11, INK, "middle", "bold")
    s += text(635, 212, "• найменші втрати (~77 Ω)", 9.5, INK, "middle")
    s += text(635, 228, "• ≈ 73 Ω диполя — гарне", 9.5, INK, "middle")
    s += text(635, 244, "  узгодження з антеною", 9.5, INK, "middle")
    s += text(635, 264, "• сигнал слабкий — втрати головні", 9.5, GREY, "middle")
    s += text(635, 300, "де важливі НИЗЬКІ ВТРАТИ", 10, "#1f47b5", "middle", "bold")
    save("fig-5-6i-2-coax-50-vs-75.svg", s)


# ═══ 🧮 Вставка до 5.6 — максимум через похідну ═════════════════════════════
def fig_power_derivative():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Максимум через похідну: dP/dR = 0 при R = Rth", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "потужність у навантаженні росте, тоді спадає; її похідна перетинає нуль рівно в піку",
              10, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 110, 290, 780, 92
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "R / Rth", 11, INK, "middle", "italic")

    def X(r):
        return ox + r / 4.0 * (axr - 30 - ox)

    def YP(P):
        return oy - (P / 0.25) * (oy - 110)

    pts = [(X(i / 100.0 * 4), YP((i / 100.0 * 4) / (1 + i / 100.0 * 4) ** 2)) for i in range(101)]
    s += polyline(pts, "#1f8a3b", 2.8)
    s += text(X(2.3), YP(0.165), "P = Vth²·R/(R+Rth)²", 10, "#1f8a3b", "start", "bold")
    s += line(X(1), YP(0.25), X(1), oy, GREY, 1.2, "3 3")
    s += circle(X(1), YP(0.25), 5, "#1f8a3b", "#1f8a3b", 1)
    for r in [1, 2, 3, 4]:
        s += line(X(r), oy - 4, X(r), oy + 4, INK, 1.2)
        s += text(X(r), oy + 20, "Rth" if r == 1 else str(r), 9, INK if r == 1 else GREY, "middle", "bold" if r == 1 else "normal")
    s += rect(150, 314, 560, 74, "#f7f7f7", GREY, 1.4, 10)
    s += text(170, 336, "dP/dR = Vth²·(Rth − R)/(Rth + R)³", 12.5, "#c0271e", "start", "bold")
    s += text(170, 358, "= 0  ⟺  Rth − R = 0  ⟺  R = Rth.   Знак: + до піка, − після → це МАКСИМУМ.", 10, INK, "start")
    s += text(170, 380, "Підставивши R = Rth:   P_max = Vth² / (4·Rth).", 10.5, "#1f8a3b", "start", "bold")
    save("fig-5-6m-1-power-derivative.svg", s)


def fig_power_flat_top():
    import math
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Пік «пласкоголовий»; і чому потужність ≠ ефективність", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "відхилившись від Rth удвічі, втрачаєш лише ~11 % потужності; зате ефективність росте далі",
              10, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 110, 300, 780, 92
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "R / Rth (лог)", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8)

    def X(r):
        return ox + (math.log10(r) + 1) / 2.0 * (axr - 30 - ox)

    def Y(f):
        return oy - f * (oy - ayt)

    for r in [0.1, 0.25, 0.5, 1, 2, 4, 10]:
        s += line(X(r), oy - 4, X(r), oy + 4, INK, 1.2)
        s += text(X(r), oy + 20, str(r), 8.5, GREY, "middle")
    pts = [(X(10 ** (i / 100.0 * 2 - 1)), Y(4 * (10 ** (i / 100.0 * 2 - 1)) / (1 + 10 ** (i / 100.0 * 2 - 1)) ** 2)) for i in range(101)]
    s += polyline(pts, "#1f8a3b", 2.6)
    s += text(X(0.18), Y(0.52), "P/P_max", 9.5, "#1f8a3b", "start", "bold")
    pts2 = [(X(10 ** (i / 100.0 * 2 - 1)), Y((10 ** (i / 100.0 * 2 - 1)) / (1 + 10 ** (i / 100.0 * 2 - 1)))) for i in range(101)]
    s += polyline(pts2, "#1f47b5", 2.4, "6 4")
    s += text(X(5.5), Y(0.9), "ККД η = R/(R+Rth)", 9.5, "#1f47b5", "middle", "bold")
    s += circle(X(1), Y(1), 4, "#1f8a3b", "#1f8a3b", 1)
    s += circle(X(2), Y(0.889), 4, "#e08030", "#e08030", 1)
    s += circle(X(0.5), Y(0.889), 4, "#e08030", "#e08030", 1)
    s += text(X(2), Y(0.889) - 12, "89 %", 8.5, "#e08030", "middle", "bold")
    s += circle(X(1), Y(0.5), 4, "#1f47b5", "#1f47b5", 1)
    s += text(X(1) + 8, Y(0.5) + 13, "ККД 50 %", 8.5, "#1f47b5", "start", "bold")
    s += rect(150, 330, 560, 58, "#fff8ee", ORANGE, 1.4, 8)
    s += text(430, 352, "Узгодження (R=Rth) дає МАКС. ПОТУЖНІСТЬ, але ККД лише 50 %.", 10, INK, "middle", "bold")
    s += text(430, 370, "Для ефективності беруть R≫Rth (η→100 %, та потужність у навантаженні мала).", 9.5, GREY, "middle", style="italic")
    save("fig-5-6m-2-flat-top.svg", s)


# ═══ ⚙️ Вставка до 5.5 — метод двох навантажень ════════════════════════════
def fig_two_load_method():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Метод двох навантажень: дві точки задають пряму джерела", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "два відомі навантаження, дві пари (I, V) — і з прямої V = Vth − I·Rth дістаємо обидва числа",
              9.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 110, 330, 600, 90
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "струм I", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8); s += text(ox - 8, ayt - 10, "напруга V", 10, INK, "start", "bold")
    Vth, Rth = 9.0, 2.0
    Isc = Vth / Rth

    def X(I):
        return ox + I / (Isc * 1.1) * (axr - 30 - ox)

    def Y(V):
        return oy - V / (Vth * 1.1) * (oy - ayt)

    s += line(X(0), Y(Vth), X(Isc), Y(0), "#c0271e", 2, "5 4")
    for R, lab, col in [(8.0, "навант. R₁", "#1f47b5"), (3.0, "навант. R₂", "#1f8a3b")]:
        I = Vth / (Rth + R)
        V = I * R
        s += line(X(I), Y(V), X(I), oy, GREY, 1, "3 3")
        s += line(X(I), Y(V), ox, Y(V), GREY, 1, "3 3")
        s += circle(X(I), Y(V), 6, col, col, 1)
        s += text(X(I) + 8, Y(V) - 10, lab, 9, col, "start", "bold")
    s += circle(X(0), Y(Vth), 5, "#c0271e", "#c0271e", 1)
    s += text(X(0) + 8, Y(Vth) - 8, "Vth (екстрап. до I=0)", 9, "#c0271e", "start", "bold")
    s += text(X(Isc * 0.55), Y(Vth * 0.58), "нахил = −Rth", 9.5, "#c0271e", "middle", "bold")
    s += rect(628, 108, 214, 214, "#f7f7f7", GREY, 1.5, 10)
    s += text(735, 132, "Дві пари (I, V):", 11, INK, "middle", "bold")
    s += text(646, 158, "V₁ = Vth − I₁·Rth", 10, INK, "start")
    s += text(646, 178, "V₂ = Vth − I₂·Rth", 10, INK, "start")
    s += line(646, 192, 826, 192, FAINT, 1.4)
    s += text(646, 216, "Rth = (V₁−V₂)/(I₂−I₁)", 11, "#1f8a3b", "start", "bold")
    s += text(646, 240, "Vth = V₁ + I₁·Rth", 11, "#1f8a3b", "start", "bold")
    s += line(646, 254, 826, 254, FAINT, 1.4)
    s += text(646, 278, "Ні відкритих, ні замкнених", 9.5, GREY, "start")
    s += text(646, 294, "клем — лише два безпечні R.", 9.5, "#1f47b5", "start", "bold")
    save("fig-5-5a-1-two-load-method.svg", s)


def fig_two_load_mcu():
    W, H = 880, 384
    s = header(W, H)
    s += text(W / 2, 30, "Автомат на МК: два навантаження, АЦП — і еквівалент готовий", 16.5, INK, "middle", "bold")
    s += text(W / 2, 51, "мікроконтролер перемикає два відомі навантаження, читає напругу АЦП і сам рахує Vth, Rth",
              9.5, GREY, "middle", style="italic")
    s += rect(55, 150, 110, 80, "#eef2fb", "#1f47b5", 2, 8)
    s += text(110, 184, "невідоме", 10.5, INK, "middle", "bold")
    s += text(110, 204, "джерело", 10.5, INK, "middle", "bold")
    s += line(165, 190, 250, 190, INK, 2)
    s += circle(250, 190, 4, INK, INK, 1)
    s += text(205, 180, "клеми", 8.5, GREY, "middle")
    s += rect(300, 122, 150, 56, "#fff", "#8a8a8a", 1.6, 6)
    s += text(375, 145, "R₁ (легке)", 10, INK, "middle", "bold")
    s += text(375, 165, "ключ 1", 8.5, GREY, "middle")
    s += rect(300, 204, 150, 56, "#fff", "#8a8a8a", 1.6, 6)
    s += text(375, 227, "R₂ (важче)", 10, INK, "middle", "bold")
    s += text(375, 247, "ключ 2", 8.5, GREY, "middle")
    s += line(250, 190, 300, 150, INK, 1.6)
    s += line(250, 190, 300, 232, INK, 1.6)
    s += rect(540, 150, 150, 80, "#eef7f0", "#1f8a3b", 2, 8)
    s += text(615, 180, "АЦП + МК", 11, INK, "middle", "bold")
    s += text(615, 202, "читає V, керує", 8.5, GREY, "middle")
    s += text(615, 216, "ключами, рахує", 8.5, GREY, "middle")
    s += arrow(452, 190, 538, 190, "#1f8a3b", 1.8)
    s += text(495, 180, "V", 9.5, "#1f8a3b", "middle", "bold")
    s += rect(722, 150, 138, 80, "#fff8ee", ORANGE, 1.6, 8)
    s += text(791, 184, "Vth, Rth", 13, "#c0271e", "middle", "bold")
    s += text(791, 206, "(+ «здоров'я»", 8.5, GREY, "middle")
    s += text(791, 219, "батареї)", 8.5, GREY, "middle")
    s += arrow(692, 190, 720, 190, INK, 2)
    s += rect(55, 308, 805, 56, "#f7f7f7", GREY, 1.4, 8)
    s += text(68, 328, "Пастки МК: навантаження мусять давати ДОСИТЬ різні струми (інакше I₂−I₁ тоне в шумі); зачекай на",
              9, INK, "start")
    s += text(68, 346, "встановлення перед читанням; усереднюй АЦП; не коротуй (грітимеш/садитимеш джерело); Rth — знімок (заряд, t°).",
              9, INK, "start")
    save("fig-5-5a-2-two-load-mcu.svg", s)


# ═══ 🧮 Вставка до 5.2 — лінійність формально ═══════════════════════════════
def fig_linearity_properties():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 30, "Лінійність: дві властивості, що дають суперпозицію", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "адитивність f(x₁+x₂)=f(x₁)+f(x₂) і однорідність f(k·x)=k·f(x) — на прикладі прямої I=V/R",
              10, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 30, FAINT, 1.5)

    def plot(ox, oy, axr, ayt):
        out = arrow(ox, oy, axr, oy, INK, 1.6) + arrow(ox, oy, ox, ayt - 4, INK, 1.6)
        out += text(axr, oy + 18, "V", 10, INK, "middle", "italic") + text(ox - 4, ayt - 6, "I", 10, INK, "start", "bold")
        return out

    s += text(225, 96, "Адитивність", 12, "#1f47b5", "middle", "bold")
    ox, oy, axr, ayt = 90, 300, 400, 110
    s += plot(ox, oy, axr, ayt)
    s += line(ox, oy, axr - 20, ayt, "#1f8a3b", 2.4)

    def X(V):
        return ox + V / 6.0 * (axr - 30 - ox)

    def Y(I):
        return oy - I / 6.0 * (oy - ayt)

    for V, lab, col in [(2, "V₁", "#c0271e"), (3, "V₂", "#e08030"), (5, "V₁+V₂", "#1f47b5")]:
        s += line(X(V), oy, X(V), Y(V), GREY, 1, "3 3")
        s += line(ox, Y(V), X(V), Y(V), GREY, 1, "3 3")
        s += circle(X(V), Y(V), 4, col, col, 1)
        s += text(X(V), oy + 16, lab, 8.5, col, "middle", "bold")
    s += text(225, 332, "I(V₁+V₂) = I(V₁) + I(V₂)", 10, INK, "middle", "bold")
    s += text(655, 96, "Однорідність", 12, "#1f8a3b", "middle", "bold")
    ox2, oy2, axr2, ayt2 = 520, 300, 830, 110
    s += plot(ox2, oy2, axr2, ayt2)
    s += line(ox2, oy2, axr2 - 20, ayt2, "#1f8a3b", 2.4)

    def X2(V):
        return ox2 + V / 6.0 * (axr2 - 30 - ox2)

    def Y2(I):
        return oy2 - I / 6.0 * (oy2 - ayt2)

    for V, lab, col in [(2, "V", "#c0271e"), (4, "2V", "#1f47b5")]:
        s += line(X2(V), oy2, X2(V), Y2(V), GREY, 1, "3 3")
        s += line(ox2, Y2(V), X2(V), Y2(V), GREY, 1, "3 3")
        s += circle(X2(V), Y2(V), 4, col, col, 1)
        s += text(X2(V), oy2 + 16, lab, 8.5, col, "middle", "bold")
    s += text(655, 332, "I(2V) = 2·I(V) — масштаб зберігається", 10, INK, "middle", "bold")
    save("fig-5-2m-1-linearity-properties.svg", s)


def fig_linear_vs_nonlinear():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Що лінійне, а що ні — і чому потужність не складається", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "лінійне = пряма ЧЕРЕЗ НУЛЬ; зі зсувом — уже не строго лінійне; крива — зовсім ні",
              10, GREY, "middle", style="italic")

    def panel(ox, title, col, sub):
        oy, axr, ayt = 318, ox + 220, 108
        out = text(ox + 110, 90, title, 11, col, "middle", "bold")
        out += arrow(ox, oy, axr, oy, INK, 1.5) + arrow(ox, oy, ox, ayt - 4, INK, 1.5)
        out += text(ox + 110, 344, sub, 8.5, GREY, "middle")
        return out, oy, axr, ayt

    p, oy, axr, ayt = panel(70, "Лінійне: резистор I=V/R", "#1f8a3b", "пряма через нуль → суперпозиція працює")
    s += p
    s += line(70, oy, axr - 15, ayt, "#1f8a3b", 2.6)
    s += circle(70, oy, 4, "#1f8a3b", "#1f8a3b", 1)
    p2, oy2, axr2, ayt2 = panel(360, "Афінне: джерело V=ε−I·r", "#e08030", "зі зсувом: f(0)≠0 → не СТРОГО лінійне")
    s += p2
    s += line(360, ayt2 + 28, axr2 - 28, oy2, "#e08030", 2.6)
    s += circle(360, ayt2 + 28, 4, "#e08030", "#e08030", 1)
    p3, oy3, axr3, ayt3 = panel(650, "Нелінійне: діод, потужність", "#c0271e", "крива → суперпозиція НЕ працює")
    s += p3
    pts = [(650 + (i / 100.0) * 205, oy3 - (i / 100.0) ** 2 * (oy3 - ayt3)) for i in range(101)]
    s += polyline(pts, "#c0271e", 2.6)
    s += rect(120, 360, 660, 32, "#fff8ee", ORANGE, 1.4, 8)
    s += text(450, 380, "Тому НАПРУГИ й СТРУМИ складаються (лінійні), а ПОТУЖНІСТЬ P=I²R — ні (квадратична).",
              10, INK, "middle", "bold")
    save("fig-5-2m-2-linear-vs-nonlinear.svg", s)


# ═══ 🔌 Вставка до 5.1 — внутрішній опір у цифрах ═══════════════════════════
def fig_source_impedances():
    import math
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "Внутрішній опір у цифрах: від міліомів до десятків омів", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "що менший r, то «жорсткіше» джерело й більший струм воно віддасть без просідання",
              10, GREY, "middle", style="italic")
    ox, axr, y = 90, 810, 220
    s += line(ox, y, axr, y, INK, 2)

    def lx(r):
        return ox + (math.log10(r) + 3) / 5.0 * (axr - ox)

    for r, lab in [(0.001, "1 мΩ"), (0.01, "10 мΩ"), (0.1, "0.1 Ω"), (1, "1 Ω"), (10, "10 Ω"), (100, "100 Ω")]:
        s += line(lx(r), y - 5, lx(r), y + 5, INK, 1.4)
        s += text(lx(r), y + 22, lab, 9, GREY, "middle")
    for r, name, cur, col, up in [
        (0.01, "авто (свинц.)", "сотні А", "#1f8a3b", True),
        (0.04, "Li-Ion, NiMH", "кілька А", "#1f8a3b", False),
        (0.2, "AA лужна", "сотні мА", "#e08030", True),
        (0.4, "USB-кабель", "просідає", "#e08030", False),
        (1.5, "9В «крона»", "десятки мА", "#c0271e", True),
        (20.0, "CR2032", "мкА–мА", "#c0271e", False),
    ]:
        x = lx(r)
        s += circle(x, y, 6, col, col, 1)
        yy = y - 58 if up else y + 50
        s += line(x, y - 6 if up else y + 6, x, yy + (12 if up else -12), "#cccccc", 1)
        s += text(x, yy, name, 9.5, col, "middle", "bold")
        s += text(x, yy + 14, cur, 8.5, GREY, "middle")
    s += text(ox, y - 92, "◄ жорсткі (великий струм)", 10, "#1f8a3b", "start", "bold")
    s += text(axr, y - 92, "м'які (малий струм) ►", 10, "#c0271e", "end", "bold")
    s += rect(110, H - 58, W - 220, 44, "#f4f7f4", GREY, 1.4, 10)
    s += text(W / 2, H - 38, "r росте, коли батарея сідає й на холоді, — тому стара чи мерзла «помирає під навантаженням».",
              10, INK, "middle", "bold")
    s += text(W / 2, H - 22, "Імпульсному споживачеві високоомне джерело (крона, таблетка) часто треба конденсатор поряд.",
              9.5, GREY, "middle", style="italic")
    save("fig-5-1c-1-source-impedances.svg", s)


def fig_source_sag():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 30, "Просідання в дії: V = ε − I·r на реальних джерелах", 17.5, INK, "middle", "bold")
    s += text(W / 2, 51, "той самий струм по-різному просаджує джерела — усе вирішує внутрішній опір",
              10, GREY, "middle", style="italic")
    for xx, lab in [(80, "джерело"), (250, "ЕРС ε"), (350, "опір r"), (450, "струм I"),
                    (570, "спад I·r"), (700, "на клемах")]:
        s += text(xx, 96, lab, 9.5, GREY, "start" if xx == 80 else "middle", "bold")
    y = 116
    for name, eps, r, I, drop, vterm, col in [
        ("Li-Ion 18650", "3.7 В", "r=0.05 Ω", "3 А", "0.15 В", "3.55 В", "#1f8a3b"),
        ("AA лужна", "1.5 В", "r=0.25 Ω", "1 А", "0.25 В", "1.25 В", "#e08030"),
        ("9В «крона»", "9.0 В", "r=1.5 Ω", "0.3 А", "0.45 В", "8.55 В", "#e08030"),
        ("CR2032", "3.0 В", "r=20 Ω", "20 мА", "0.40 В", "2.6 В", "#c0271e"),
    ]:
        s += rect(70, y, 740, 48, "#fafafa", "#dddddd", 1.2, 6)
        s += text(80, y + 29, name, 11, col, "start", "bold")
        s += text(250, y + 29, eps, 10.5, INK, "middle")
        s += text(350, y + 29, r, 10.5, INK, "middle")
        s += text(450, y + 29, I, 10.5, INK, "middle")
        s += text(570, y + 29, drop, 10.5, "#c0271e", "middle", "bold")
        s += text(700, y + 29, vterm, 11, "#1f8a3b", "middle", "bold")
        y += 58
    s += text(W / 2, H - 20, "Мале r (Li-Ion) майже не просідає; велике r (крона, таблетка) втрачає помітну частку — звідси й вибір джерела.",
              9.5, GREY, "middle", style="italic")
    save("fig-5-1c-2-source-sag.svg", s)


# ═══ 🧮 Вставка до 5.1 — лінія навантаження ═════════════════════════════════
def fig_load_line():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 30, "Лінія навантаження: робоча точка — це перетин", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "джерело й навантаження мають спільні V та I — тож реальна точка там, де їхні характеристики перетинаються",
              9.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 110, 360, 720, 90
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "напруга V", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8); s += text(ox - 8, ayt - 10, "струм I", 11, INK, "start", "bold")
    Veps, r, RL = 10.0, 100.0, 200.0
    Isc = Veps / r

    def X(V):
        return ox + (V / 11.0) * (axr - 30 - ox)

    def Y(I):
        return oy - (I / 0.12) * (oy - ayt)

    s += line(X(Veps), Y(0), X(0), Y(Isc), "#c0271e", 2.8)
    s += line(X(0), Y(0), X(9), Y(9 / RL), "#1f47b5", 2.6)
    Vq = Isc / (1 / RL + Isc / Veps)
    Iq = Vq / RL
    s += line(X(Vq), Y(Iq), X(Vq), Y(0), GREY, 1.2, "3 3")
    s += line(X(Vq), Y(Iq), X(0), Y(Iq), GREY, 1.2, "3 3")
    s += circle(X(Vq), Y(Iq), 6, "#1f8a3b", "#1f8a3b", 1)
    s += text(X(Vq) + 12, Y(Iq) - 12, "робоча: %.1f В, %.0f мА" % (Vq, Iq * 1000), 10, "#1f8a3b", "start", "bold")
    s += circle(X(Veps), Y(0), 4, "#c0271e", "#c0271e", 1)
    s += text(X(Veps), Y(0) + 20, "ε (хол. хід)", 9.5, "#c0271e", "middle", "bold")
    s += circle(X(0), Y(Isc), 4, "#c0271e", "#c0271e", 1)
    s += text(X(0) - 8, Y(Isc), "I_кз = ε/r", 9.5, "#c0271e", "end", "bold")
    s += text(X(7.1), Y(0.08), "джерело: V = ε − I·r  (нахил −1/r)", 10, "#c0271e", "middle", "bold")
    s += text(X(8.2), Y(0.03), "навантаження R: V = I·R", 10, "#1f47b5", "middle", "bold")
    save("fig-5-1m-1-load-line.svg", s)


def fig_load_line_nonlinear():
    import math
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 30, "Сила методу: нелінійне навантаження (діод, світлодіод)", 17, INK, "middle", "bold")
    s += text(W / 2, 51, "для діода нема формули V=I·R — та перетин лінії навантаження з його кривою однаково дає робочу точку",
              9.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 110, 360, 740, 90
    s += arrow(ox, oy, axr, oy, INK, 1.8); s += text(axr, oy + 22, "напруга V", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8); s += text(ox - 8, ayt - 10, "струм I", 11, INK, "start", "bold")

    def X(V):
        return ox + (V / 5.0) * (axr - 30 - ox)

    def Y(I):
        return oy - (I / 0.05) * (oy - ayt)

    def diodeI(V):
        return max(1e-3 * (math.exp((V - 1.8) / 0.12) - 1), 0)

    pts = []
    for i in range(0, 101):
        V = i / 100.0 * 4.5
        I = diodeI(V)
        if I > 0.055:
            break
        pts.append((X(V), Y(I)))
    s += polyline(pts, "#1f8a3b", 2.8)
    s += text(X(2.55), Y(0.046), "крива світлодіода", 10, "#1f8a3b", "middle", "bold")

    def findQ(Veps, Isc):
        for i in range(1, 1000):
            V = i / 1000.0 * Veps
            if diodeI(V) >= Isc * (1 - V / Veps):
                return V, Isc * (1 - V / Veps)
        return Veps, 0.0

    s += line(X(3.0), Y(0), X(0), Y(0.045), "#c0271e", 2.4)
    s += text(X(0) - 8, Y(0.045), "I_кз", 8.5, "#c0271e", "end", "bold")
    Vq, Iq = findQ(3.0, 0.045)
    s += circle(X(Vq), Y(Iq), 6, "#c0271e", "#c0271e", 1)
    s += text(X(Vq) + 10, Y(Iq) - 12, "робоча точка", 9.5, "#c0271e", "start", "bold")
    s += line(X(3.0), Y(0), X(0), Y(0.022), "#e08030", 2.2, "6 4")
    Vq2, Iq2 = findQ(3.0, 0.022)
    s += circle(X(Vq2), Y(Iq2), 5, "#e08030", "#e08030", 1)
    s += text(X(Vq2) - 30, Y(Iq2) + 20, "більший r → точка зсувається", 9, "#e08030", "middle", "bold")
    s += rect(126, 104, 312, 82, "#eef7f0", GREEN, 1.5, 10)
    s += text(282, 128, "Змінюєш ε чи r — лінія", 10, INK, "middle", "bold")
    s += text(282, 146, "рухається, а робоча точка", 10, INK, "middle", "bold")
    s += text(282, 164, "ковзає по кривій приладу.", 10, INK, "middle", "bold")
    s += text(282, 180, "Так задають режим діодів і транзисторів.", 9, GREY, "middle", style="italic")
    save("fig-5-1m-2-nonlinear-load-line.svg", s)


if __name__ == "__main__":
    fig_blackbox()
    fig_thevenin_norton()
    fig_real_battery()
    fig_timeline()
    # §5.1 Реальне джерело
    fig51_ideal_vs_real()
    fig51_internal_r()
    fig51_vi_characteristic()
    fig51_measure_r()
    fig51_examples()
    # §5.2 Суперпозиція
    fig52_idea()
    fig52_turn_off()
    fig52_worked()
    fig52_power_not_add()
    fig52_recipe()
    # §5.3 Теорема Тевеніна
    fig53_statement()
    fig53_vth_rth()
    fig53_swap_loads()
    fig53_worked()
    fig53_real_source()
    # §5.4 Теорема Нортона
    fig54_statement()
    fig54_in_rn()
    fig54_transformation()
    fig54_when()
    fig54_worked()
    # §5.5 Як знайти Vth, Rth
    fig55_three_methods()
    fig55_oc_sc()
    fig55_deactivate()
    fig55_test_source()
    fig55_worked()
    # §5.6 Узгодження й максимальна потужність
    fig56_question()
    fig56_power_curve()
    fig56_pmax()
    fig56_efficiency()
    fig56_when()
    # §5.1 вставка (🧮) — лінія навантаження
    fig_load_line()
    fig_load_line_nonlinear()
    # §5.1 вставка (🔌) — внутрішній опір у цифрах
    fig_source_impedances()
    fig_source_sag()
    # §5.2 вставка (🧮) — лінійність формально
    fig_linearity_properties()
    fig_linear_vs_nonlinear()
    # §5.5 вставка (⚙️) — метод двох навантажень
    fig_two_load_method()
    fig_two_load_mcu()
    # §5.6 вставка (🧮) — максимум через похідну
    fig_power_derivative()
    fig_power_flat_top()
    # §5.6 історія (📜) — звідки 50 Ом
    fig_coax_three_optima()
    fig_coax_50_vs_75()
    # §5.6 вставка (🔌) — термінатор і атенюатор
    fig_terminator()
    fig_attenuator()
    print("OK — фігури Розділу 5 (повна, +§5.6 узгодження) згенеровано в", OUT)
