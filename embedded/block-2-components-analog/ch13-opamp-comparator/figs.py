# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 13 — «Операційний підсилювач і компаратор» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Підписи посекційно (Рис. C.S.N); для історії до розділу —
секція 0 (Рис. 13.0.N). Допоміжні функції скопійовано з попередніх розділів.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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


def _ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=2):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return circle(cx, cy, r, "none", color, w) + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


def _sine(ox, oy, w, amp, cycles, col, wv=2.4, phase=0.0):
    pts = []
    for j in range(0, int(w) + 1):
        t = j / w
        y = oy - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((ox + j, y))
    return _poly(pts, col, wv)


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


def coil_h(cx, cy, length, turns=5, ry=18, col=COPP):
    x0 = cx - length / 2
    dx = length / turns
    s = ""
    for i in range(turns + 1):
        s += f'<ellipse cx="{x0+i*dx:.1f}" cy="{cy:.1f}" rx="6" ry="{ry}" fill="none" stroke="{col}" stroke-width="2"/>\n'
    return s, (x0, x0 + length)


# ── допоміжне для §11.2 ──────────────────────────────────────────────────────
def _diode_h(cx, cy, size=12, right=True, col=INK):
    if right:
        t = f'<path d="M {cx-size},{cy-size} L {cx-size},{cy+size} L {cx+size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
        t += line(cx + size * 0.8, cy - size, cx + size * 0.8, cy + size, col, 2.5)
    else:
        t = f'<path d="M {cx+size},{cy-size} L {cx+size},{cy+size} L {cx-size*0.8:.1f},{cy} Z" fill="#dfe7f0" stroke="{col}" stroke-width="1.6"/>\n'
        t += line(cx - size * 0.8, cy - size, cx - size * 0.8, cy + size, col, 2.5)
    return t


def _bjt_sym(cx, cy, npn=True):
    t = line(cx - 44, cy, cx, cy, INK, 2)
    t += line(cx, cy - 28, cx, cy + 28, INK, 3)
    t += line(cx, cy - 9, cx + 30, cy - 32, INK, 2) + line(cx + 30, cy - 32, cx + 30, cy - 56, INK, 2)
    t += line(cx, cy + 9, cx + 30, cy + 32, INK, 2) + line(cx + 30, cy + 32, cx + 30, cy + 56, INK, 2)
    if npn:
        t += arrow(cx + 8, cy + 15, cx + 28, cy + 31, INK, 2)
    else:
        t += arrow(cx + 28, cy + 31, cx + 8, cy + 15, INK, 2)
    return t


# ── хелпер: горизонтальний конденсатор (дві пластини) ────────────────────────
def _cap_h(cx, cy, gap=7, plate=13, col=INK):
    return (line(cx - gap, cy - plate, cx - gap, cy + plate, col, 2.4)
            + line(cx + gap, cy - plate, cx + gap, cy + plate, col, 2.4))


def _clip_sine(ox, oy, w, amp, cycles, col, lo=-1.0, hi=1.0, phase=0.0, wv=2.4):
    """Синусоїда, зрізана знизу (lo) та згори (hi) — у частках амплітуди."""
    pts = []
    for j in range(0, int(w) + 1):
        v = math.sin(2 * math.pi * cycles * (j / w) + phase)
        v = max(lo, min(hi, v))
        pts.append((ox + j, oy - amp * v))
    return _poly(pts, col, wv)


# ── хелпер: спрощений символ N-канального MOSFET ─────────────────────────────
def _mosfet_sym(cx, cy, pch=False):
    t = line(cx - 44, cy, cx - 22, cy, INK, 2)          # затвор (лід)
    t += line(cx - 22, cy - 22, cx - 22, cy + 22, INK, 2.4)   # пластина затвора
    t += line(cx - 12, cy - 22, cx - 12, cy + 22, INK, 2.4)   # канал (ізол. зазор)
    t += line(cx - 12, cy - 16, cx + 24, cy - 16, INK, 2) + line(cx + 24, cy - 16, cx + 24, cy - 44, INK, 2)  # стік
    t += line(cx - 12, cy + 16, cx + 24, cy + 16, INK, 2) + line(cx + 24, cy + 16, cx + 24, cy + 44, INK, 2)  # витік
    if pch:
        t += arrow(cx + 4, cy, cx - 12, cy, INK, 1.8)   # стрілка назовні (p-канал)
    else:
        t += arrow(cx - 12, cy, cx + 4, cy, INK, 1.8)   # стрілка всередину (n-канал)
    return t


# ── хелпер: символ операційного підсилювача (трикутник) ──────────────────────
def _opamp_sym(cx, cy, w=70, h=64):
    t = f'<path d="M {cx-w/2:.0f},{cy-h/2:.0f} L {cx-w/2:.0f},{cy+h/2:.0f} L {cx+w/2:.0f},{cy:.0f} Z" fill="#fbfbfb" stroke="{INK}" stroke-width="1.8"/>\n'
    t += text(cx - w / 2 + 11, cy - h / 4 + 5, "−", 14, BLUE, "middle", "bold")
    t += text(cx - w / 2 + 11, cy + h / 4 + 5, "+", 12, RED, "middle", "bold")
    return t


# ── Рис. 13.0.1 — таймлайн ───────────────────────────────────────────────────
def fig13_t1_timeline():
    W, H = 920, 230
    s = header(W, H)
    s += text(W / 2, 30, "Родовід операційного підсилювача", 17, INK, "middle", "bold")
    boxes = [
        ("1941 · Сварцел", ["схема ОП", "(директор M9)"], "#fdf1dc"),
        ("1947 · Рагаццині", ["назва:", "«операційний»"], "#fdf1dc"),
        ("1952 · Філбрик", ["K2-W —", "ламповий модуль"], "#fdf1dc"),
        ("1964–65 · Відлар", ["µA702/709 —", "мікросхема"], "#e9eefb"),
        ("1968 · Фуллагар", ["µA741 —", "«просто працює»"], LGRN),
        ("сьогодні", ["універсальна", "цеглинка"], LGRN),
    ]
    bw, gap, by, bh = 138, 10, 84, 96
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 16 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 9.5, INK, "middle", "bold")
        border = "#d8b46a" if fill == "#fdf1dc" else "#9bb0c2"
        s += rect(bx, by, bw, bh, fill, border, 1.5, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 40 + k * 22, ln, 10, INK, "middle")
        if i < len(boxes) - 1:
            s += arrow(bx + bw + 1, by + bh / 2, bx + bw + gap - 1, by + bh / 2, GREY, 1.8)
    s += text(W / 2, H - 12, "Народжений рахувати — і поступово стиснутий від ящика ламп до копійчаної мікросхеми, що працює відразу.",
              10.5, GREY, "middle", style="italic")
    save("fig-13-0-1-timeline.svg", s)


# ── Рис. 13.0.2 — народжений рахувати ────────────────────────────────────────
def fig13_t2_born_to_compute():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Народжений рахувати: ОП наводить зенітку (M9, 1941)", 14.5, INK, "middle", "bold")
    s += _frame(40, 60, 150, 150, "радар")
    s += _poly([(115, 150), (93, 108), (137, 108)], INK, 2)
    s += arrow(115, 106, 115, 78, BLUE, 2) + text(115, 176, "SCR-584", 8.5, INK, "middle")
    s += arrow(196, 130, 244, 130, GREY, 2.2)
    s += _frame(252, 60, 196, 150, "обчислювач (ОП)")
    s += _opamp_sym(348, 118, 66, 56)
    s += text(350, 176, "рахує, КУДИ", 9.5, INK, "middle", "bold") + text(350, 193, "летітиме ціль", 9.5, INK, "middle")
    s += arrow(454, 130, 502, 130, GREY, 2.2)
    s += _frame(510, 60, 170, 150, "гармата")
    s += line(560, 185, 625, 120, INK, 4) + circle(560, 185, 8, "#cfd6dd", INK, 1.6)
    s += text(595, 200, "наведена в упередження", 8, INK, "middle")
    s += text(W / 2, H - 14, "Поки снаряд летить, ціль зміщується. ОП у реальному часі обчислював майбутню точку — і гармата била туди.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-0-2-born-to-compute.svg", s)


# ── Рис. 13.0.3 — аналоговий обчислювач ──────────────────────────────────────
def fig13_t3_analog_computer():
    W, H = 720, 310
    s = header(W, H)
    s += text(W / 2, 30, "Що означає «операційний»: ОП розв'язує рівняння", 15, INK, "middle", "bold")
    s += rect(260, 62, 200, 54, "#eef2f6", "#9bb0c2", 1.3, 8)
    s += text(360, 84, "величини → напруги", 10.5, INK, "middle", "bold")
    s += text(360, 102, "(швидкість, висота, сила)", 8.5, GREY, "middle")
    ops = [("Σ", "складає"), ("−", "віднімає"), ("∫", "інтегрує"), ("d/dt", "диференціює")]
    for i, (sym, name) in enumerate(ops):
        x = 100 + i * 165
        s += _opamp_sym(x, 180, 58, 50)
        s += text(x - 4, 185, sym, 13, GREEN, "middle", "bold")
        s += text(x, 224, name, 9.5, INK, "middle", "bold")
    s += text(360, 256, "з'єднані ОП «проживають» те саме рівняння, що й реальна система", 10, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Напруги в схемі поводяться так само, як рух снаряда чи коливання моста. Розв'язок зчитують вольтметром.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-0-3-analog-computer.svg", s)


# ── Рис. 13.0.4 — ламповий K2-W ──────────────────────────────────────────────
def fig13_t4_k2w_tube():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 30, "K2-W: перший товарний ОП (Філбрик, 1952)", 15, INK, "middle", "bold")
    s += text(340, 68, "октальний модуль", 9, GREY, "middle")
    s += rect(250, 78, 180, 152, "#1b1b1b", INK, 1.6, 10)
    for tx in (305, 375):
        s += _ellipse(tx, 132, 22, 40, "#eef2f6", GREY, 1.6)
        s += _poly([(tx, 110), (tx - 7, 126), (tx + 7, 142), (tx - 7, 158)], RED, 1.6)
    s += text(340, 198, "2 × лампа 12AX7", 10, "#dfe7f0", "middle", "bold")
    s += text(340, 216, "(двотріоди)", 8.5, "#9bb0c2", "middle")
    s += rect(470, 110, 162, 92, LGRN, GREEN, 1.5, 8)
    s += text(551, 140, "$22", 22, GREEN, "middle", "bold")
    s += text(551, 168, "перший ОП,", 10, INK, "middle")
    s += text(551, 186, "який можна купити", 10, INK, "middle")
    s += text(W / 2, H - 14, "Готова «чорна скринька»: купив, вставив у панельку — і будуй свій аналоговий обчислювач.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-0-4-k2w-tube.svg", s)


# ── Рис. 13.0.5 — стискання ──────────────────────────────────────────────────
def fig13_t5_shrinking():
    W, H = 760, 280
    s = header(W, H)
    s += text(W / 2, 30, "Стискання ОП: лампа → мікросхема → «вставив і працює»", 14.5, INK, "middle", "bold")
    s += rect(50, 90, 90, 110, "#1b1b1b", INK, 1.5, 8)
    s += _ellipse(80, 132, 12, 28, "#eef2f6", "#9bb0c2", 1.4) + _ellipse(110, 132, 12, 28, "#eef2f6", "#9bb0c2", 1.4)
    s += text(95, 222, "лампа (K2-W)", 9.5, INK, "middle", "bold") + text(95, 238, "Філбрик 1952", 8.5, GREY, "middle")
    s += arrow(150, 145, 200, 145, GREY, 2.2)
    s += rect(215, 110, 90, 70, "#2b2b2b", INK, 1.5, 4)
    for i in range(4):
        s += line(205, 122 + i * 15, 215, 122 + i * 15, INK, 1.4) + line(305, 122 + i * 15, 315, 122 + i * 15, INK, 1.4)
    s += text(260, 150, "µA702/709", 8.5, "#dfe7f0", "middle", "bold")
    s += text(260, 222, "мікросхема", 9.5, INK, "middle", "bold") + text(260, 238, "Відлар 1964–65", 8.5, GREY, "middle")
    s += arrow(325, 145, 375, 145, GREY, 2.2)
    s += _opamp_sym(440, 145, 70, 60)
    s += text(556, 132, "µA741 — вставив,", 11, GREEN, "start", "bold")
    s += text(556, 152, "замкнув зв'язок —", 11, GREEN, "start", "bold")
    s += text(556, 172, "і ВОНО ПРАЦЮЄ", 11, GREEN, "start", "bold")
    s += text(440, 222, "Фуллагар 1968", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Від ящика ламп — до копійчаної мікросхеми з вбудованою корекцією, що працює відразу.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-0-5-shrinking.svg", s)


# ── Рис. 13.0.6 — той, що вижив ──────────────────────────────────────────────
def fig13_t6_survivor():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Іронія долі: обчислювач помер, ОП вижив", 15, INK, "middle", "bold")
    s += rect(50, 70, 260, 150, "#f0f0f0", GREY, 1.4, 8)
    s += text(180, 96, "аналоговий обчислювач", 11, GREY, "middle", "bold")
    s += text(180, 118, "(рідний дім ОП)", 9, GREY, "middle")
    s += text(180, 152, "програв цифровому", 10, GREY, "middle")
    s += text(180, 172, "комп'ютерові — зник", 10, GREY, "middle")
    s += line(70, 80, 290, 210, RED, 2.4) + line(290, 80, 70, 210, RED, 2.4)
    s += _opamp_sym(420, 145, 64, 56)
    uses = ["підсилює", "фільтрує", "порівнює", "буферизує"]
    for i, u in enumerate(uses):
        s += arrow(452, 145, 508, 100 + i * 30, GREEN, 1.8)
        s += text(514, 104 + i * 30, u, 10, INK, "start", "bold")
    s += text(420, 200, "ОП — живий і всюди", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Математику забрала цифра — та світ лишився аналоговим на краях, і там ОП незамінний.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-0-6-survivor.svg", s)


# ── Рис. 13.8.1 — два пороги ──────────────────────────────────────────────────
def fig138_two_thresholds():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Гістерезис: два пороги замість одного", 15.5, INK, "middle", "bold")
    ox, ww = 80, 520
    iy = 120
    vh_y, vl_y = iy - 20, iy + 20
    s += rect(ox, vh_y, ww, vl_y - vh_y, "#fbf3e0", "#e0c98a", 0.8)
    s += _poly([(ox, iy + 55), (ox + ww * 0.5, iy - 55), (ox + ww, iy + 55)], BLUE, 2.4)
    s += line(ox, vh_y, ox + ww, vh_y, RED, 1.5, "5 4") + text(ox + ww + 6, vh_y, "VH (верхній)", 8.5, RED, "start", "bold")
    s += line(ox, vl_y, ox + ww, vl_y, GREEN, 1.5, "5 4") + text(ox + ww + 6, vl_y + 4, "VL (нижній)", 8.5, GREEN, "start", "bold")
    s += text(ox + ww * 0.24, iy + 44, "вгору: фліп на VH ▲", 8.5, RED, "middle", "bold")
    s += text(ox + ww * 0.76, iy + 44, "униз: фліп на VL ▼", 8.5, GREEN, "middle", "bold")
    s += text(ox + ww * 0.5, iy, "мертва зона (пам'ять)", 8.5, "#9a7b2e", "middle", "bold")
    s += text(W / 2, H - 12, "Угору вихід перекидається на VH, униз — на VL; між ними тримає стан. Зазор гасить дребезг.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-8-1-two-thresholds.svg", s)


# ── Рис. 13.8.2 — додатний зв'язок ────────────────────────────────────────────
def fig138_positive_feedback():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 30, "Реалізація: додатний зв'язок на вхід «+»", 14.5, INK, "middle", "bold")
    cx, cy = 300, 160
    s += _opamp_sym(cx, cy, 110, 96)
    s += line(cx - 55, cy - 24, cx - 150, cy - 24, INK, 2) + text(cx - 156, cy - 20, "сигнал", 9.5, INK, "end", "bold")
    s += line(cx - 55, cy + 24, cx - 110, cy + 24, INK, 2) + circle(cx - 110, cy + 24, 3, INK, INK)
    outx = cx + 55
    s += line(outx, cy, outx + 150, cy, INK, 2) + text(outx + 156, cy + 4, "вихід", 10, INK, "start", "bold")
    s += circle(outx + 90, cy, 3, INK, INK)
    s += line(outx + 90, cy, outx + 90, cy + 90, RED, 2.2) + line(outx + 90, cy + 90, cx - 110, cy + 90, RED, 2.2)
    s += line(cx - 110, cy + 90, cx - 110, cy + 24, RED, 2.2) + arrow(cx - 110, cy + 60, cx - 110, cy + 26, RED, 2.2)
    s += text((outx + 90 + cx - 110) / 2, cy + 102, "ДОДАТНИЙ зв'язок (на «+»)", 9.5, RED, "middle", "bold")
    s += text(cx - 108, cy + 12, "поріг рухається з виходом", 8, RED, "start")
    s += text(W / 2, H - 12, "Вихід підмішується в поріг: пішов угору — поріг піднявся; униз — опустився. Звідси два рівні.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-8-2-positive-feedback.svg", s)


# ── Рис. 13.8.3 — петля передатної кривої ─────────────────────────────────────
def fig138_transfer_loop():
    W, H = 680, 310
    s = header(W, H)
    s += text(W / 2, 28, "Передатна крива з петлею (гістерезис)", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 110, 200, 440, 120
    s += _axes(ox, oy, ww, hh, "вхід", "вихід")
    vl_x, vh_x = ox + 0.35 * ww, ox + 0.65 * ww
    hi_y, lo_y = oy - hh, oy - 6
    s += _poly([(ox, lo_y), (vh_x, lo_y), (vh_x, hi_y), (ox + ww, hi_y)], RED, 2.6)
    s += _poly([(ox + ww, hi_y), (vl_x, hi_y), (vl_x, lo_y), (ox, lo_y)], BLUE, 2.6)
    s += line(vl_x, oy, vl_x, oy - hh - 6, GREY, 1, "4 3") + text(vl_x, oy + 18, "VL", 9, GREEN, "middle", "bold")
    s += line(vh_x, oy, vh_x, oy - hh - 6, GREY, 1, "4 3") + text(vh_x, oy + 18, "VH", 9, RED, "middle", "bold")
    s += text(ox + 0.5 * ww, hi_y - 12, "↑ угору на VH", 8.5, RED, "middle", "bold")
    s += text(ox + 0.5 * ww, lo_y + 16, "↓ униз на VL", 8.5, BLUE, "middle", "bold")
    s += text((vl_x + vh_x) / 2, (hi_y + lo_y) / 2, "петля", 10, INK, "middle", "bold")
    s += text(W / 2, H - 10, "Шлях «туди» і «назад» різний — між ними петля. Її ширина — глибина гістерезису, незбіжність — «пам'ять».",
              9, GREY, "middle", style="italic")
    save("fig-13-8-3-transfer-loop.svg", s)


# ── Рис. 13.8.4 — гасить дребезг ──────────────────────────────────────────────
def fig138_kills_chatter():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Гістерезис проти дребезгу: вихід чистий", 15, INK, "middle", "bold")
    ox, ww = 80, 520
    iy = 110
    vh, vl = iy - 10, iy + 10
    s += rect(ox, vh, ww, vl - vh, "#fbf3e0", "#e0c98a", 0.8)
    s += text(ox - 10, iy, "сигнал", 9, INK, "end", "bold")
    pts = []
    for j in range(0, int(ww) + 1, 4):
        t = j / ww
        y = (iy + 20 - 40 * t) + 6 * math.sin(2 * math.pi * 9 * t) + 4 * math.sin(2 * math.pi * 23 * t)
        pts.append((ox + j, y))
    s += _poly(pts, BLUE, 2)
    s += line(ox, vh, ox + ww, vh, RED, 1.3, "4 3") + text(ox + ww + 6, vh, "VH", 8.5, RED, "start", "bold")
    s += line(ox, vl, ox + ww, vl, GREEN, 1.3, "4 3") + text(ox + ww + 6, vl + 4, "VL", 8.5, GREEN, "start", "bold")
    oy2 = 220
    s += text(ox - 10, oy2, "вихід", 9, INK, "end", "bold")
    cpts = []
    state = False
    prev = None
    for j in range(0, int(ww) + 1, 4):
        t = j / ww
        sig = (iy + 20 - 40 * t) + 6 * math.sin(2 * math.pi * 9 * t) + 4 * math.sin(2 * math.pi * 23 * t)
        if not state and sig < vh:
            state = True
        if state and sig > vl:
            state = False
        y = oy2 - 26 if state else oy2 + 26
        if prev is not None and prev != y:
            cpts.append((ox + j, prev))
            cpts.append((ox + j, y))
        cpts.append((ox + j, y))
        prev = y
    s += _poly(cpts, GREEN, 2.4)
    s += text(W / 2, H - 12, "Той самий шумний сигнал — але вихід один раз чисто перекинувся й тримається. Дребезг зник.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-8-4-kills-chatter.svg", s)


# ── Рис. 13.8.5 — термостат ───────────────────────────────────────────────────
def fig138_thermostat():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Термостат: гістерезис, який ви знаєте", 15, INK, "middle", "bold")
    ox, ww = 80, 520
    iy = 120
    y19, y21 = iy + 24, iy - 24
    s += rect(ox, y21, ww, y19 - y21, "#eef2f6", "#c9d3dc", 0.8)
    s += text(ox - 10, iy, "T", 10, INK, "end", "bold")
    s += _poly([(ox + j, iy - 32 * math.sin(2 * math.pi * 2 * (j / ww))) for j in range(0, int(ww) + 1, 4)], RED, 2.4)
    s += line(ox, y21, ox + ww, y21, INK, 1.3, "5 4") + text(ox + ww + 6, y21, "21° вимкн.", 8.5, BLUE, "start", "bold")
    s += line(ox, y19, ox + ww, y19, INK, 1.3, "5 4") + text(ox + ww + 6, y19 + 4, "19° увімкн.", 8.5, RED, "start", "bold")
    s += text(ox + ww / 2, iy, "мертва зона 19–21°", 9, GREY, "middle", "bold")
    s += text(W / 2, H - 12, "Гріє до 21°, вимикається; знов гріє лише з 19°. Два пороги — і котел не брязкає на межі 20°.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-8-5-thermostat.svg", s)


# ── Рис. 13.8.6 — тригер Шмітта + історія ─────────────────────────────────────
def fig138_schmitt():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Тригер Шмітта: від нервів кальмара (Шмітт, 1934)", 14, INK, "middle", "bold")
    cx, cy = 160, 150
    s += f'<path d="M {cx-50},{cy-44} L {cx-50},{cy+44} L {cx+50},{cy} Z" fill="#fbfbfb" stroke="{INK}" stroke-width="1.8"/>\n'
    s += line(cx - 28, cy + 8, cx - 8, cy + 8, INK, 1.6) + line(cx - 8, cy + 8, cx - 8, cy - 8, INK, 1.6) + line(cx - 8, cy - 8, cx + 12, cy - 8, INK, 1.6)
    s += line(cx - 50, cy, cx - 90, cy, INK, 1.8) + text(cx - 96, cy + 4, "вхід", 9, INK, "end")
    s += line(cx + 50, cy, cx + 90, cy, INK, 1.8) + text(cx + 96, cy + 4, "вихід", 9, INK, "start")
    s += text(cx, cy + 72, "символ тригера Шмітта", 8.5, GREY, "middle")
    s += rect(330, 70, 360, 172, "#fff7e6", COPP, 1.4, 8)
    s += text(510, 96, "Отто Шмітт, 1934", 12, "#b5732e", "middle", "bold")
    s += text(510, 122, "вивчав нерв кальмара —", 10, INK, "middle")
    s += text(510, 140, "як він «спрацьовує» все-або-нічого", 9.5, INK, "middle")
    s += text(510, 168, "→ відтворив це електронікою", 10, GREEN, "middle", "bold")
    s += text(510, 192, "→ заклав біоміметику", 10, GREEN, "middle", "bold")
    s += text(510, 218, "(запозичення ідей у природи)", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Жива клітина підказала інженерам одну з найкорисніших схем: поріг + пам'ять = чисте перемикання.",
              9, GREY, "middle", style="italic")
    save("fig-13-8-6-schmitt.svg", s)


# ── Рис. 13.7.1 — компаратор ──────────────────────────────────────────────────
def fig137_comparator_basic():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 30, "Компаратор: котра напруга більша?", 16, INK, "middle", "bold")
    cx, cy = 280, 150
    s += _opamp_sym(cx, cy, 110, 96)
    s += line(cx - 55, cy - 24, cx - 140, cy - 24, INK, 2) + text(cx - 146, cy - 20, "V₊", 11, RED, "end", "bold")
    s += line(cx - 55, cy + 24, cx - 140, cy + 24, INK, 2) + text(cx - 146, cy + 28, "V₋", 11, BLUE, "end", "bold")
    s += line(cx + 55, cy, cx + 130, cy, INK, 2) + text(cx + 136, cy + 4, "вихід", 10, INK, "start", "bold")
    s += rect(440, 96, 220, 110, "#fbfbfb", "#c9d3dc", 1.3, 8)
    s += text(550, 124, "V₊ > V₋ →", 11, INK, "middle", "bold")
    s += text(550, 144, "вихід ВИСОКИЙ ▲", 11, GREEN, "middle", "bold")
    s += line(460, 160, 640, 160, FAINT, 1)
    s += text(550, 180, "V₊ < V₋ →", 11, INK, "middle", "bold")
    s += text(550, 200, "вихід НИЗЬКИЙ ▼", 11, BLUE, "middle", "bold")
    s += text(W / 2, H - 12, "Вихід — повністю на одній із рейок, залежно лише від того, котрий вхід переважив. Відповідь «так/ні».",
              9.5, GREY, "middle", style="italic")
    save("fig-13-7-1-comparator-basic.svg", s)


# ── Рис. 13.7.2 — розімкнений = компаратор ────────────────────────────────────
def fig137_open_loop():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 28, "Розімкнений ОП — це й є компаратор", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 120, 160, 420, 100
    midx = ox + ww / 2
    s += arrow(ox, oy, ox + ww + 14, oy, INK, 2) + text(ox + ww + 18, oy + 4, "V₊−V₋", 10, INK, "start", "bold")
    s += arrow(midx, oy + hh + 10, midx, oy - hh - 10, INK, 2) + text(midx + 8, oy - hh - 12, "Vout", 10, INK, "start", "bold")
    s += _poly([(ox, oy + hh), (midx - 5, oy + hh), (midx + 5, oy - hh), (ox + ww, oy - hh)], RED, 2.8)
    s += line(ox, oy - hh, ox + ww, oy - hh, GREY, 1, "4 3") + text(ox + ww + 2, oy - hh, "+рейка", 8.5, GREEN, "start", "bold")
    s += line(ox, oy + hh, ox + ww, oy + hh, GREY, 1, "4 3") + text(ox + ww + 2, oy + hh + 4, "−рейка", 8.5, BLUE, "start", "bold")
    s += text(midx + 90, oy - 30, "майже вертикальна сходинка", 9, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Велетенське A без зворотного зв'язку = чистий поріг: трохи «+» більший — вихід угорі, і навпаки.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-7-2-open-loop.svg", s)


# ── Рис. 13.7.3 — поріг ───────────────────────────────────────────────────────
def fig137_threshold():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Сигнал перетинає поріг — вихід перекидається", 14.5, INK, "middle", "bold")
    ox, ww = 80, 520
    iy = 110
    s += text(ox - 10, iy, "сигнал", 9, INK, "end", "bold")
    s += _sine(ox, iy, ww, 36, 2, BLUE, 2.4)
    thy = iy - 12
    s += line(ox, thy, ox + ww, thy, RED, 1.6, "5 4") + text(ox + ww + 6, thy, "поріг", 9, RED, "start", "bold")
    oy2 = 220
    s += text(ox - 10, oy2, "вихід", 9, INK, "end", "bold")
    pts = []
    prev = None
    for j in range(0, int(ww) + 1, 4):
        v = 36 * math.sin(2 * math.pi * 2 * (j / ww))
        y = oy2 - 26 if v > 12 else oy2 + 26
        if prev is not None and prev != y:
            pts.append((ox + j, prev))
            pts.append((ox + j, y))
        pts.append((ox + j, y))
        prev = y
    s += _poly(pts, GREEN, 2.4)
    s += line(ox, oy2 - 26, ox + ww, oy2 - 26, FAINT, 1) + text(ox + ww + 6, oy2 - 26, "1", 9, GREEN, "start", "bold")
    s += line(ox, oy2 + 26, ox + ww, oy2 + 26, FAINT, 1) + text(ox + ww + 6, oy2 + 30, "0", 9, BLUE, "start", "bold")
    s += text(W / 2, H - 12, "Поки сигнал вище порога — вихід «1»; нижче — «0». Плавна хвиля стала чітким «вище/нижче».",
              9.5, GREY, "middle", style="italic")
    save("fig-13-7-3-threshold.svg", s)


# ── Рис. 13.7.4 — детектор темряви ────────────────────────────────────────────
def fig137_light_detector():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Детектор темряви: фоторезистор vs поріг → ліхтар", 14, INK, "middle", "bold")
    s += line(70, 66, 70, 92, RED, 2) + text(70, 60, "+5В", 8.5, RED, "middle", "bold")
    s += rect(56, 92, 28, 38, "#fff", SUN, 1.6) + text(98, 108, "фоторез.", 8, INK, "start", "bold")
    s += line(70, 130, 70, 146, INK, 2) + circle(70, 146, 3, INK, INK)
    s += rect(56, 146, 28, 38, "#fff", INK, 1.4) + text(98, 168, "20к", 8, INK, "start")
    s += line(70, 184, 70, 206, INK, 2) + line(52, 206, 88, 206, INK, 1.4)
    cx, cy = 300, 146
    s += _opamp_sym(cx, cy, 88, 78)
    s += line(70, 146, 240, 146, INK, 2) + line(240, 146, 240, cy + 19, INK, 2) + line(240, cy + 19, cx - 44, cy + 19, INK, 2)
    s += text(170, 138, "сигнал", 8, INK, "middle")
    s += line(cx - 44, cy - 19, 210, cy - 19, INK, 2) + text(206, cy - 16, "2.5В", 9, RED, "end", "bold") + text(180, cy - 32, "поріг", 7.5, GREY, "middle")
    s += line(cx + 44, cy, cx + 90, cy, INK, 2)
    s += rect(cx + 90, cy - 10, 30, 20, "#fff", INK, 1.3) + text(cx + 105, cy + 4, "R", 8, INK, "middle")
    s += line(cx + 120, cy, cx + 150, cy, INK, 2)
    s += f'<path d="M {cx+150},{cy-10} L {cx+150},{cy+10} L {cx+168},{cy} Z" fill="#fff3b0" stroke="{INK}" stroke-width="1.4"/>\n'
    s += line(cx + 168, cy - 10, cx + 168, cy + 10, INK, 2) + text(cx + 200, cy - 14, "ліхтар", 9, INK, "start", "bold")
    s += line(cx + 168, cy, cx + 200, cy, INK, 2) + line(cx + 200, cy, cx + 200, cy + 30, INK, 2) + line(cx + 182, cy + 30, cx + 218, cy + 30, INK, 1.4)
    s += text(W / 2, H - 12, "Стемніло → опір фоторезистора зріс → напруга впала нижче 2.5 В → вихід перекинувся → ліхтар світить.",
              9, GREY, "middle", style="italic")
    save("fig-13-7-4-light-detector.svg", s)


# ── Рис. 13.7.5 — застосування ────────────────────────────────────────────────
def fig137_applications():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Компаратор усюди, де порівнюють рівні", 15.5, INK, "middle", "bold")
    apps = [
        ("світло / темрява", "нічник, авто-фари"),
        ("поріг темпер.", "увімкнути вентилятор"),
        ("розряд батареї", "«батарея сідає»"),
        ("перехід нуля", "синус → прямокутник"),
        ("вхід АЦП", "аналог → цифра"),
    ]
    cw = 132
    for i, (head, sub) in enumerate(apps):
        x = 25 + i * (cw + 5)
        s += rect(x, 70, cw, 140, "#eef2f6", "#9bb0c2", 1.4, 8)
        s += text(x + cw / 2, 100, head, 10, INK, "middle", "bold")
        s += line(x + 12, 116, x + cw - 12, 116, FAINT, 1)
        s += text(x + cw / 2, 150, sub, 8.5, GREY, "middle")
        s += text(x + cw / 2, 188, "«вище/нижче»", 8.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Скрізь те саме: чи перетнула величина свій поріг. Просте рішення «так/ні» — і ціла автоматика.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-7-5-applications.svg", s)


# ── Рис. 13.7.6 — дребезг ─────────────────────────────────────────────────────
def fig137_chatter_problem():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Проблема дребезгу: шум біля порога", 15, INK, "middle", "bold")
    ox, ww = 80, 520
    iy = 110
    thy = iy
    oy2 = 220
    s += rect(ox + 0.34 * ww, 64, 0.32 * ww, 200, "#fbeaea", "#e0c4c4", 1, 4)
    s += text(ox - 10, iy, "сигнал", 9, INK, "end", "bold")
    pts = []
    for j in range(0, int(ww) + 1, 4):
        t = j / ww
        y = (iy + 20 - 40 * t) + 6 * math.sin(2 * math.pi * 9 * t) + 4 * math.sin(2 * math.pi * 23 * t)
        pts.append((ox + j, y))
    s += _poly(pts, BLUE, 2)
    s += line(ox, thy, ox + ww, thy, RED, 1.6, "5 4") + text(ox + ww + 6, thy, "поріг", 9, RED, "start", "bold")
    s += text(ox - 10, oy2, "вихід", 9, INK, "end", "bold")
    cpts = []
    prev = None
    for j in range(0, int(ww) + 1, 4):
        t = j / ww
        sig = (iy + 20 - 40 * t) + 6 * math.sin(2 * math.pi * 9 * t) + 4 * math.sin(2 * math.pi * 23 * t)
        y = oy2 - 26 if sig < thy else oy2 + 26
        if prev is not None and prev != y:
            cpts.append((ox + j, prev))
            cpts.append((ox + j, y))
        cpts.append((ox + j, y))
        prev = y
    s += _poly(cpts, RED, 2.2)
    s += text(ox + 0.5 * ww, 286, "↑ дребезг: вихід скаче туди-сюди ↑", 9, RED, "middle", "bold")
    save("fig-13-7-6-chatter-problem.svg", s)


# ── Рис. 13.6.1 — суматор ─────────────────────────────────────────────────────
def fig136_summer():
    W, H = 700, 310
    s = header(W, H)
    s += text(W / 2, 28, "Суматор: кілька входів у віртуальну землю", 15, INK, "middle", "bold")
    cx, cy = 430, 160
    s += _opamp_sym(cx, cy, 96, 86)
    nx, ny = cx - 48, cy - 22
    s += circle(nx, ny, 3, INK, INK) + text(nx - 6, ny + 18, "0В", 8, GREEN, "end", "bold")
    for k, yy in enumerate([ny - 44, ny, ny + 44]):
        s += text(90, yy + 4, "V%d" % (k + 1), 9.5, INK, "end", "bold")
        s += line(98, yy, 170, yy, INK, 1.8)
        s += rect(170, yy - 10, 48, 20, "#fff", INK, 1.4) + text(194, yy + 4, "R%d" % (k + 1), 8.5, INK, "middle", "bold")
        s += line(218, yy, nx, yy, INK, 1.8)
    s += line(nx, ny - 44, nx, ny + 44, INK, 1.8)
    s += line(cx - 48, cy + 22, cx - 80, cy + 22, INK, 1.8) + line(cx - 80, cy + 22, cx - 80, cy + 42, INK, 1.8)
    for k, wd in enumerate([14, 9, 4]):
        s += line(cx - 80 - wd / 2, cy + 44 + k * 4, cx - 80 + wd / 2, cy + 44 + k * 4, INK, 1.8)
    outx = cx + 48
    s += line(outx, cy, outx + 100, cy, INK, 1.8) + text(outx + 106, cy + 4, "Vout", 10, INK, "start", "bold")
    s += circle(outx + 50, cy, 3, INK, INK)
    s += line(outx + 50, cy, outx + 50, ny - 62, INK, 1.8) + line(outx + 50, ny - 62, nx, ny - 62, INK, 1.8)
    s += rect(nx + 40, ny - 72, 48, 20, "#fff", INK, 1.4) + text(nx + 64, ny - 58, "Rf", 8.5, INK, "middle", "bold")
    s += line(nx, ny - 62, nx, ny - 44, INK, 1.8)
    s += rect(120, 252, 460, 40, LGRN, GREEN, 1.4, 8)
    s += text(350, 278, "Vout = − Rf·( V1/R1 + V2/R2 + V3/R3 )", 13, GREEN, "middle", "bold")
    save("fig-13-6-1-summer.svg", s)


# ── Рис. 13.6.2 — струми додаються ────────────────────────────────────────────
def fig136_currents_add():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 30, "Струми входів складаються у віртуальній землі", 14.5, INK, "middle", "bold")
    nx, ny = 320, 155
    s += circle(nx, ny, 7, "#fff3b0", SUN, 2)
    s += text(nx, ny + 32, "віртуальна земля (0 В)", 9.5, "#9a7b2e", "middle", "bold")
    for lab, dy in [("I1", -60), ("I2", 0), ("I3", 60)]:
        s += arrow(150, ny + dy, nx - 14, ny + dy // 2, GREEN, 2.2)
        s += text(120, ny + dy + 4, lab, 10, GREEN, "end", "bold")
    s += arrow(nx + 14, ny, 470, ny, RED, 2.6) + text(420, ny - 12, "I1+I2+I3", 10, RED, "middle", "bold")
    s += text(500, ny + 4, "крізь Rf → Vout", 9.5, INK, "start", "bold")
    s += rect(160, 226, 360, 40, "#eef2f6", "#c9d3dc", 1.3, 8)
    s += text(340, 251, "закон Кірхгофа: струми у вузлі додаються", 11, INK, "middle", "bold")
    s += text(W / 2, H - 10, "Кожен вхід ллє свій струм незалежно; природа складає їх у вузлі. Так ОП і «додає» напруги.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-6-2-currents-add.svg", s)


# ── Рис. 13.6.3 — мікшер ──────────────────────────────────────────────────────
def fig136_mixer():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 30, "Аудіомікшер: суматор зводить канали", 15, INK, "middle", "bold")
    chans = [("мікрофон", "гучно (мала R)"), ("гітара", "середньо"), ("синтезатор", "тихо (велика R)")]
    cx, cy = 470, 150
    s += _opamp_sym(cx, cy, 90, 80)
    nx, ny = cx - 45, cy - 20
    for k, (name, vol) in enumerate(chans):
        yy = 92 + k * 50
        s += rect(50, yy - 16, 100, 32, "#eef2f6", "#9bb0c2", 1.3, 5) + text(100, yy - 1, name, 8.5, INK, "middle", "bold") + text(100, yy + 12, vol, 6.5, GREY, "middle")
        s += line(150, yy, 210, yy, INK, 1.6)
        s += rect(210, yy - 9, 40, 18, "#fff", INK, 1.3) + text(230, yy + 4, "R", 8, INK, "middle", "bold")
        s += line(250, yy, 340, yy, INK, 1.4)
    s += line(340, 92, 340, 192, INK, 1.6) + line(340, ny, nx, ny, INK, 1.6) + circle(340, ny, 3, INK, INK)
    s += line(cx - 45, cy + 20, cx - 70, cy + 20, INK, 1.4) + line(cx - 70, cy + 20, cx - 70, cy + 38, INK, 1.4)
    for k, wd in enumerate([12, 7, 3]):
        s += line(cx - 70 - wd / 2, cy + 40 + k * 3.5, cx - 70 + wd / 2, cy + 40 + k * 3.5, INK, 1.4)
    s += line(cx + 45, cy, cx + 70, cy, INK, 1.6) + circle(cx + 70, cy, 3, INK, INK)
    s += line(cx + 70, cy, cx + 70, ny - 30, INK, 1.4) + line(cx + 70, ny - 30, nx, ny - 30, INK, 1.4) + line(nx, ny - 30, nx, ny, INK, 1.4)
    s += text(cx + 36, ny - 40, "Rf", 8, INK, "middle", "bold")
    s += line(cx + 70, cy, cx + 120, cy, INK, 1.8) + text(cx + 126, cy + 4, "суміш", 10, GREEN, "start", "bold")
    s += text(W / 2, H - 12, "Кожен канал — через свій резистор (свою «гучність»); вихід — їхня зважена суміш.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-6-3-mixer.svg", s)


# ── Рис. 13.6.4 — різницевий ──────────────────────────────────────────────────
def fig136_difference():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Різницевий підсилювач", 16, INK, "middle", "bold")
    cx, cy = 400, 150
    s += _opamp_sym(cx, cy, 96, 86)
    nx, ny = cx - 48, cy - 22
    px, py = cx - 48, cy + 22
    s += text(90, ny + 4, "V1", 9.5, INK, "end", "bold") + line(98, ny, 160, ny, INK, 1.8)
    s += rect(160, ny - 10, 46, 20, "#fff", INK, 1.4) + text(183, ny + 4, "R1", 8.5, INK, "middle", "bold")
    s += line(206, ny, nx, ny, INK, 1.8) + circle(nx, ny, 3, INK, INK)
    outx = cx + 48
    s += line(outx, cy, outx + 100, cy, INK, 1.8) + text(outx + 106, cy + 4, "Vout", 10, INK, "start", "bold")
    s += circle(outx + 50, cy, 3, INK, INK)
    s += line(outx + 50, cy, outx + 50, ny - 54, INK, 1.8) + line(outx + 50, ny - 54, nx, ny - 54, INK, 1.8)
    s += rect(nx + 40, ny - 64, 46, 20, "#fff", INK, 1.4) + text(nx + 63, ny - 50, "Rf", 8.5, INK, "middle", "bold")
    s += line(nx, ny - 54, nx, ny, INK, 1.8)
    s += text(90, py + 4, "V2", 9.5, INK, "end", "bold") + line(98, py, 160, py, INK, 1.8)
    s += rect(160, py - 10, 46, 20, "#fff", INK, 1.4) + text(183, py + 4, "R1", 8.5, INK, "middle", "bold")
    s += line(206, py, px, py, INK, 1.8) + circle(px, py, 3, INK, INK)
    s += line(px, py, px, py + 44, INK, 1.8) + rect(px - 23, py + 44, 46, 20, "#fff", INK, 1.4) + text(px, py + 58, "R2", 8.5, INK, "middle", "bold")
    s += line(px, py + 64, px, py + 82, INK, 1.8) + line(px - 20, py + 82, px + 20, py + 82, INK, 1.5) + text(px, py + 96, "GND", 7.5, INK, "middle")
    s += rect(430, 198, 250, 44, LGRN, GREEN, 1.4, 8)
    s += text(555, 225, "Vout = (Rf/R1)(V2−V1)", 12.5, GREEN, "middle", "bold")
    save("fig-13-6-4-difference.svg", s)


# ── Рис. 13.6.5 — придушення синфазного ───────────────────────────────────────
def fig136_common_mode_reject():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Придушення синфазного: спільне геть, різницю — в підсилення", 13, INK, "middle", "bold")
    cx, cy = 360, 150
    s += _opamp_sym(cx, cy, 96, 84)
    s += text(cx - 58, cy - 18, "3.0 В", 10, INK, "end", "bold") + line(cx - 48, cy - 22, cx - 110, cy - 22, INK, 1.6)
    s += text(cx - 58, cy + 26, "3.1 В", 10, INK, "end", "bold") + line(cx - 48, cy + 22, cx - 110, cy + 22, INK, 1.6)
    s += line(cx + 48, cy, cx + 120, cy, INK, 1.8) + text(cx + 126, cy + 4, "Vout", 10, INK, "start", "bold")
    s += rect(60, 200, 280, 70, "#f6eef0", "#d8a0a0", 1.3, 8)
    s += text(200, 224, "спільне ~3 В", 11, RED, "middle", "bold")
    s += text(200, 248, "→ ВІДКИНУТО (0)", 10.5, RED, "middle", "bold")
    s += rect(380, 200, 280, 70, "#eef6ef", GREEN, 1.3, 8)
    s += text(520, 224, "різниця 0.1 В × 10", 11, GREEN, "middle", "bold")
    s += text(520, 248, "→ Vout = 1.0 В", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Великі однакові 3 В зникли; підсилилася лише корисна різниця 0.1 В.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-6-5-common-mode-reject.svg", s)


# ── Рис. 13.6.6 — вимірювальний підсилювач ────────────────────────────────────
def fig136_instrumentation():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Вимірювальний підсилювач: 2 буфери + різницевий", 14, INK, "middle", "bold")
    s += text(60, 108, "V2", 10, INK, "end", "bold")
    s += _opamp_sym(150, 110, 60, 50)
    s += text(150, 150, "буфер", 8, INK, "middle")
    s += text(60, 213, "V1", 10, INK, "end", "bold")
    s += _opamp_sym(150, 210, 60, 50)
    s += text(150, 250, "буфер", 8, INK, "middle")
    s += line(70, 118, 122, 118, INK, 1.6) + line(70, 202, 122, 202, INK, 1.6)
    s += arrow(182, 110, 320, 132, GREY, 1.8) + arrow(182, 210, 320, 182, GREY, 1.8)
    s += rect(330, 112, 170, 90, "#eef6ef", GREEN, 1.5, 8)
    s += text(415, 142, "різницевий", 11, GREEN, "middle", "bold")
    s += text(415, 164, "підсилювач", 11, GREEN, "middle", "bold")
    s += text(415, 186, "(V2 − V1)·G", 9.5, INK, "middle")
    s += line(500, 157, 580, 157, INK, 1.8) + text(586, 161, "Vout", 10, INK, "start", "bold")
    s += text(150, 78, "велетенський вхід — не вантажить давач", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Буфери дають велетенський вхід (для слабких давачів), різницевий — точне віднімання й CMRR. Золотий стандарт.",
              8.5, GREY, "middle", style="italic")
    save("fig-13-6-6-instrumentation.svg", s)


# ── Рис. 13.5.1 — повторювач ──────────────────────────────────────────────────
def fig135_follower():
    W, H = 620, 290
    s = header(W, H)
    s += text(W / 2, 30, "Повторювач напруги (буфер)", 16, INK, "middle", "bold")
    cx, cy = 300, 150
    s += _opamp_sym(cx, cy, 110, 96)
    s += line(cx - 55, cy + 24, cx - 150, cy + 24, INK, 2) + text(cx - 156, cy + 28, "Vin", 11, INK, "end", "bold")
    outx = cx + 55
    s += line(outx, cy, outx + 120, cy, INK, 2) + text(outx + 126, cy + 4, "Vout", 11, INK, "start", "bold")
    s += circle(outx + 60, cy, 3, INK, INK)
    s += line(outx + 60, cy, outx + 60, cy - 80, GREEN, 2.2) + line(outx + 60, cy - 80, cx - 90, cy - 80, GREEN, 2.2)
    s += line(cx - 90, cy - 80, cx - 90, cy - 24, GREEN, 2.2) + arrow(cx - 90, cy - 52, cx - 90, cy - 26, GREEN, 2.2)
    s += circle(cx - 90, cy - 24, 3, INK, INK)
    s += text((outx + 60 + cx - 90) / 2, cy - 90, "вихід прямо на «−» (без резисторів)", 9, GREEN, "middle", "bold")
    s += rect(160, 235, 300, 40, LGRN, GREEN, 1.4, 8)
    s += text(310, 261, "Vout = Vin   (підсилення ×1)", 13, GREEN, "middle", "bold")
    save("fig-13-5-1-follower.svg", s)


# ── Рис. 13.5.2 — навіщо буфер ────────────────────────────────────────────────
def fig135_why_buffer():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Цінність буфера — у перетворенні опорів", 15, INK, "middle", "bold")
    cx, cy = 360, 150
    s += _opamp_sym(cx, cy, 96, 84)
    s += rect(40, 110, 230, 90, "#eef6ef", GREEN, 1.4, 8)
    s += text(155, 134, "ВХІД", 11, GREEN, "middle", "bold")
    s += text(155, 156, "велетенський опір", 9.5, INK, "middle")
    s += text(155, 174, "струм ≈ 0", 9.5, INK, "middle")
    s += text(155, 190, "не вантажить джерело", 9, GREY, "middle")
    s += line(270, cy + 18, cx - 48, cy + 18, INK, 1.6)
    s += rect(460, 110, 230, 90, "#fbeeef", RED, 1.4, 8)
    s += text(575, 134, "ВИХІД", 11, RED, "middle", "bold")
    s += text(575, 156, "нульовий опір (жорсткий)", 9.5, INK, "middle")
    s += text(575, 174, "струму скільки треба", 9.5, INK, "middle")
    s += text(575, 190, "живить навантаження", 9, GREY, "middle")
    s += line(cx + 48, cy, 460, cy, INK, 1.6)
    s += text(cx, cy + 64, "Vout = Vin", 11, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Та сама напруга — але вхід нічого не бере, а вихід усе віддає. Це й є розв'язка опорів.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-5-2-why-buffer.svg", s)


# ── Рис. 13.5.3 — проблема навантаження ───────────────────────────────────────
def fig135_loading_problem():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Проблема навантаження: напруга просідає", 15, INK, "middle", "bold")
    s += line(120, 70, 120, 100, RED, 2) + text(120, 64, "+5В", 9.5, RED, "middle", "bold")
    s += rect(106, 100, 28, 44, "#fff", INK, 1.5) + text(150, 122, "10к", 9, INK, "start")
    s += line(120, 144, 120, 160, INK, 2) + circle(120, 160, 3, INK, INK)
    s += rect(106, 160, 28, 44, "#fff", INK, 1.5) + text(150, 182, "10к", 9, INK, "start")
    s += line(120, 204, 120, 230, INK, 2) + line(95, 230, 145, 230, INK, 1.5) + text(120, 244, "GND", 8, INK, "middle")
    s += line(120, 160, 360, 160, INK, 2) + text(240, 150, "2.5 В?", 10, INK, "middle", "bold")
    s += rect(360, 138, 50, 44, "#fbeeef", RED, 1.5, 4) + text(385, 164, "1к", 10, INK, "middle", "bold")
    s += text(385, 124, "навантаження", 8.5, INK, "middle")
    s += line(385, 182, 385, 210, INK, 2) + line(360, 210, 410, 210, INK, 1.5) + text(385, 224, "GND", 8, INK, "middle")
    s += rect(470, 120, 220, 80, "#fbeeef", RED, 1.4, 8)
    s += text(580, 146, "просіло!", 12, RED, "middle", "bold")
    s += text(580, 172, "2.5 В → 0.42 В", 13, RED, "middle", "bold")
    s += text(580, 192, "(дільник не тримає струму)", 8.5, GREY, "middle")
    s += text(W / 2, H - 10, "Важке навантаження висмоктало струм — і кволий дільник не втримав напруги.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-5-3-loading-problem.svg", s)


# ── Рис. 13.5.4 — буфер лікує ─────────────────────────────────────────────────
def fig135_buffer_fixes():
    W, H = 760, 290
    s = header(W, H)
    s += text(W / 2, 28, "Буфер між ними — і напруга тримається", 15, INK, "middle", "bold")
    s += line(70, 70, 70, 96, RED, 2) + text(70, 64, "+5В", 9, RED, "middle", "bold")
    s += rect(56, 96, 28, 40, "#fff", INK, 1.4) + text(98, 116, "10к", 8.5, INK, "start")
    s += line(70, 136, 70, 150, INK, 2) + circle(70, 150, 3, INK, INK)
    s += rect(56, 150, 28, 40, "#fff", INK, 1.4) + text(98, 170, "10к", 8.5, INK, "start")
    s += line(70, 190, 70, 214, INK, 2) + line(50, 214, 90, 214, INK, 1.4)
    s += text(70, 230, "2.5 В (тримає)", 8.5, GREEN, "middle", "bold")
    s += line(70, 150, 230, 150, INK, 2) + line(230, 150, 230, 170, INK, 2) + line(230, 170, 255, 170, INK, 2)
    cx, cy = 300, 150
    s += _opamp_sym(cx, cy, 90, 80)
    s += line(cx + 45, cy, cx + 85, cy, INK, 2) + circle(cx + 85, cy, 3, INK, INK)
    s += line(cx + 85, cy, cx + 85, cy - 66, GREEN, 1.8) + line(cx + 85, cy - 66, 235, cy - 66, GREEN, 1.8) + line(235, cy - 66, 235, cy - 20, GREEN, 1.8)
    s += text(cx, cy + 58, "буфер ×1", 9, INK, "middle", "bold")
    s += line(cx + 85, cy, 560, cy, INK, 2) + text(470, 140, "2.5 В", 10, GREEN, "middle", "bold")
    s += rect(560, 128, 50, 44, "#eef6ef", GREEN, 1.5, 4) + text(585, 154, "1к", 10, INK, "middle", "bold")
    s += line(585, 172, 585, 200, INK, 2) + line(560, 200, 610, 200, INK, 1.4)
    s += text(640, 150, "→ дістає 2.5 В", 9.5, GREEN, "start", "bold")
    s += text(W / 2, H - 10, "Дільник не навантажений (тримає 2.5 В); буфер живить навантаження з жорсткого виходу (теж 2.5 В).",
              9, GREY, "middle", style="italic")
    save("fig-13-5-4-buffer-fixes.svg", s)


# ── Рис. 13.5.5 — числа ───────────────────────────────────────────────────────
def fig135_divider_example():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Опорні 2.5 В: напряму проти буфера", 15, INK, "middle", "bold")
    s += _frame(40, 54, 300, 210, "напряму (без буфера)")
    s += text(190, 86, "дільник 10к/10к, +5В", 10, INK, "middle")
    s += text(190, 108, "навантаження 1 кОм", 10, INK, "middle")
    s += rect(80, 128, 220, 52, "#fbeeef", RED, 1.4, 6)
    s += text(190, 150, "2.5 В  →  0.42 В", 13, RED, "middle", "bold")
    s += text(190, 170, "обвалилося!", 9.5, RED, "middle", "bold")
    s += text(190, 212, "дільник не тримає струму", 9, INK, "middle")
    s += _frame(380, 54, 300, 210, "із буфером")
    s += text(530, 86, "той самий дільник", 10, INK, "middle")
    s += text(530, 108, "+ повторювач + навантаж.", 10, INK, "middle")
    s += rect(420, 128, 220, 52, "#eef6ef", GREEN, 1.4, 6)
    s += text(530, 150, "2.5 В  →  2.5 В", 13, GREEN, "middle", "bold")
    s += text(530, 170, "тримається!", 9.5, GREEN, "middle", "bold")
    s += text(530, 212, "струм 2.5 мА дає буфер", 9, INK, "middle")
    s += text(W / 2, H - 10, "Те саме джерело, та сама напруга — буфер просто розв'язав його від навантаження.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-5-5-divider-example.svg", s)


# ── Рис. 13.5.6 — vs емітерний повторювач ─────────────────────────────────────
def fig135_vs_emitter_follower():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Буфер на ОП = ідеальний емітерний повторювач", 14.5, INK, "middle", "bold")
    s += _frame(40, 54, 300, 210, "емітерний повторювач (§11.7)")
    s += _bjt_sym(170, 150, True)
    s += text(190, 212, "вхід ~великий, вихід ~малий", 8.5, INK, "middle")
    s += text(190, 230, "підсилення ≈ 1", 10, INK, "middle", "bold")
    s += _frame(380, 54, 300, 210, "буфер на ОП")
    s += _opamp_sym(520, 150, 90, 80)
    s += line(520 + 45, 150, 520 + 75, 150, INK, 1.8) + line(520 + 75, 150, 520 + 75, 110, GREEN, 1.6) + line(520 + 75, 110, 520 - 45, 110, GREEN, 1.6) + line(520 - 45, 110, 520 - 45, 130, GREEN, 1.6)
    s += text(520, 212, "вхід велетенський, вихід жорсткий", 8.5, INK, "middle")
    s += text(520, 230, "підсилення = 1 (рівно)", 10, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Та сама робота — розв'язка опорів. Але ОП робить її точніше: рівно ×1, вхід більший, вихід жорсткіший.",
              9, GREY, "middle", style="italic")
    save("fig-13-5-6-vs-emitter-follower.svg", s)


# ── Рис. 13.4.1 — інвертуючий ─────────────────────────────────────────────────
def fig134_inverting():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Інвертуючий підсилювач", 16, INK, "middle", "bold")
    cx, cy = 380, 150
    s += _opamp_sym(cx, cy, 100, 90)
    nx, ny = cx - 50, cy - 22
    s += circle(nx, ny, 3, INK, INK)
    s += text(70, ny + 4, "Vin", 10, INK, "end", "bold")
    s += line(78, ny, 150, ny, INK, 2)
    s += rect(150, ny - 11, 54, 22, "#ffffff", INK, 1.5) + text(177, ny + 4, "Rin", 9, INK, "middle", "bold")
    s += line(204, ny, nx, ny, INK, 2)
    s += line(cx - 50, cy + 22, cx - 86, cy + 22, INK, 2) + line(cx - 86, cy + 22, cx - 86, cy + 44, INK, 2)
    for k, wd in enumerate([16, 10, 5]):
        s += line(cx - 86 - wd / 2, cy + 46 + k * 4, cx - 86 + wd / 2, cy + 46 + k * 4, INK, 2)
    outx = cx + 50
    s += line(outx, cy, outx + 120, cy, INK, 2) + text(outx + 126, cy + 4, "Vout", 10, INK, "start", "bold")
    s += circle(outx + 60, cy, 3, INK, INK)
    s += line(outx + 60, cy, outx + 60, ny - 58, INK, 2) + line(outx + 60, ny - 58, nx, ny - 58, INK, 2)
    s += rect(nx + 50, ny - 69, 54, 22, "#ffffff", INK, 1.5) + text(nx + 77, ny - 54, "Rf", 9, INK, "middle", "bold")
    s += line(nx, ny - 58, nx, ny, INK, 2)
    s += rect(60, 232, 280, 44, LGRN, GREEN, 1.4, 8)
    s += text(200, 260, "підсилення = − Rf / Rin", 13, GREEN, "middle", "bold")
    s += text(W - 170, 250, "перевертає знак", 10, RED, "middle", "bold")
    s += text(W - 170, 270, "Zin = Rin (помірний)", 9.5, INK, "middle")
    save("fig-13-4-1-inverting.svg", s)


# ── Рис. 13.4.2 — неінвертуючий ───────────────────────────────────────────────
def fig134_non_inverting():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Неінвертуючий підсилювач", 16, INK, "middle", "bold")
    cx, cy = 360, 140
    s += _opamp_sym(cx, cy, 100, 90)
    s += line(cx - 50, cy + 22, cx - 160, cy + 22, INK, 2) + text(cx - 166, cy + 26, "Vin", 10, INK, "end", "bold")
    nx, ny = cx - 50, cy - 22
    s += circle(nx, ny, 3, INK, INK)
    s += line(nx, ny, nx - 70, ny, INK, 2)
    s += rect(nx - 126, ny - 11, 54, 22, "#ffffff", INK, 1.5) + text(nx - 99, ny + 4, "Rg", 9, INK, "middle", "bold")
    s += line(nx - 126, ny, nx - 150, ny, INK, 2) + line(nx - 150, ny, nx - 150, ny + 24, INK, 2)
    for k, wd in enumerate([16, 10, 5]):
        s += line(nx - 150 - wd / 2, ny + 26 + k * 4, nx - 150 + wd / 2, ny + 26 + k * 4, INK, 2)
    outx = cx + 50
    s += line(outx, cy, outx + 120, cy, INK, 2) + text(outx + 126, cy + 4, "Vout", 10, INK, "start", "bold")
    s += circle(outx + 60, cy, 3, INK, INK)
    s += line(outx + 60, cy, outx + 60, ny - 58, INK, 2) + line(outx + 60, ny - 58, nx, ny - 58, INK, 2)
    s += rect(nx + 50, ny - 69, 54, 22, "#ffffff", INK, 1.5) + text(nx + 77, ny - 54, "Rf", 9, INK, "middle", "bold")
    s += line(nx, ny - 58, nx, ny, INK, 2)
    s += rect(60, 232, 280, 44, LGRN, GREEN, 1.4, 8)
    s += text(200, 260, "підсилення = 1 + Rf / Rg", 13, GREEN, "middle", "bold")
    s += text(W - 150, 250, "зберігає знак", 10, GREEN, "middle", "bold")
    s += text(W - 150, 270, "Zin — велетенський", 9.5, INK, "middle")
    save("fig-13-4-2-non-inverting.svg", s)


# ── Рис. 13.4.3 — виведення неінвертуючого ────────────────────────────────────
def fig134_non_inverting_derivation():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Виведення неінвертуючого за правилами", 15, INK, "middle", "bold")
    cx, cy = 250, 150
    s += _opamp_sym(cx, cy, 96, 86)
    s += line(cx - 48, cy + 22, cx - 140, cy + 22, INK, 2) + text(cx - 146, cy + 26, "Vin", 10, RED, "end", "bold")
    s += text(cx - 92, cy + 8, "V₊=Vin", 8.5, RED, "middle", "bold")
    nx, ny = cx - 48, cy - 22
    s += text(cx - 92, cy - 36, "V₋=Vin", 8.5, BLUE, "middle", "bold")
    s += line(nx, ny, nx - 60, ny, INK, 2) + rect(nx - 114, ny - 11, 50, 22, "#fff", INK, 1.4) + text(nx - 89, ny + 4, "Rg", 8.5, INK, "middle", "bold")
    s += line(nx - 114, ny, nx - 134, ny, INK, 2) + line(nx - 134, ny, nx - 134, ny + 22, INK, 2)
    for k, wd in enumerate([14, 9, 4]):
        s += line(nx - 134 - wd / 2, ny + 24 + k * 4, nx - 134 + wd / 2, ny + 24 + k * 4, INK, 2)
    outx = cx + 48
    s += line(outx, cy, outx + 50, cy, INK, 2) + circle(outx + 30, cy, 3, INK, INK) + text(outx + 36, cy + 16, "Vout", 9, INK, "start", "bold")
    s += line(outx + 30, cy, outx + 30, ny - 50, INK, 2) + line(outx + 30, ny - 50, nx, ny - 50, INK, 2)
    s += rect(nx + 40, ny - 61, 50, 22, "#fff", INK, 1.4) + text(nx + 65, ny - 46, "Rf", 8.5, INK, "middle", "bold")
    s += line(nx, ny - 50, nx, ny, INK, 2)
    s += rect(430, 70, 270, 160, "#fbfbfb", "#c9d3dc", 1.3, 8)
    eqs = ["V₊ = Vin", "V₋ = V₊ = Vin", "V₋ = Vout·Rg/(Rg+Rf)", "→ Vin = Vout·Rg/(Rg+Rf)"]
    y = 98
    for e in eqs:
        s += text(450, y, e, 11, INK, "start", "bold" if e.startswith("→") else "normal")
        y += 28
    s += rect(450, 192, 232, 30, LGRN, GREEN, 1.4, 6)
    s += text(566, 212, "Vout/Vin = 1 + Rf/Rg", 12, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Сигнал на «+» задає V₋ через віртуальне коротке; дільник пов'язує V₋ із Vout. Прирівняли — готово.",
              9, GREY, "middle", style="italic")
    save("fig-13-4-3-non-inverting-derivation.svg", s)


# ── Рис. 13.4.4 — порівняння ──────────────────────────────────────────────────
def fig134_comparison():
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 30, "Інвертуючий проти неінвертуючого", 16, INK, "middle", "bold")
    cols = [(40, 200, "риса"), (240, 250, "інвертуючий"), (490, 230, "неінвертуючий")]
    y0 = 54
    for x, w, lab in cols:
        s += rect(x, y0, w, 30, "#eef2f6", "#c9d3dc", 1.2)
        s += text(x + w / 2, y0 + 20, lab, 11.5, INK, "middle", "bold")
    rows = [
        ("знак", "перевертає (−)", "зберігає (+)"),
        ("підсилення", "−Rf/Rin", "1 + Rf/Rg"),
        ("найменше", "будь-яке (<1 можна)", "≥ 1 (не послабиш)"),
        ("вхідний опір", "помірний (= Rin)", "велетенський"),
        ("сигнал заходить", "на «−» крізь Rin", "прямо на «+»"),
    ]
    y = y0 + 30
    for name, a, b in rows:
        s += rect(cols[0][0], y, cols[0][1], 42, "#fbfbfb", "#d7dee5", 1)
        s += text(cols[0][0] + 12, y + 27, name, 11, INK, "start", "bold")
        s += rect(cols[1][0], y, cols[1][1], 42, "#fbeeef", "#e0c4c4", 1)
        s += text(cols[1][0] + 12, y + 27, a, 10.5, INK, "start")
        s += rect(cols[2][0], y, cols[2][1], 42, "#eef6ef", "#c4d6c4", 1)
        s += text(cols[2][0] + 12, y + 27, b, 10.5, INK, "start")
        y += 42
    s += text(W / 2, y + 22, "Дві схеми — два інструменти: вибір диктують знак і вхідний опір.", 10, GREY, "middle", style="italic")
    save("fig-13-4-4-comparison.svg", s)


# ── Рис. 13.4.5 — коли яку ────────────────────────────────────────────────────
def fig134_when_each():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Коли яку схему брати", 16, INK, "middle", "bold")
    s += rect(40, 64, 320, 200, "#eef6ef", GREEN, 1.5, 8)
    s += text(200, 90, "НЕІНВЕРТУЮЧИЙ", 12, GREEN, "middle", "bold")
    s += text(200, 110, "(не вантажити джерело)", 9, GREY, "middle")
    for k, it in enumerate(["слабкі давачі (мікрофон, термопара)", "високоомні джерела", "входи АЦП", "коли знак має лишитися"]):
        s += circle(62, 134 + k * 30, 3, GREEN, GREEN) + text(78, 138 + k * 30, it, 9.5, INK, "start")
    s += rect(380, 64, 300, 200, "#fbeeef", RED, 1.5, 8)
    s += text(530, 90, "ІНВЕРТУЮЧИЙ", 12, RED, "middle", "bold")
    s += text(530, 110, "(віртуальна земля)", 9, GREY, "middle")
    for k, it in enumerate(["суматор / мікшер", "струм→напруга (фотодіод)", "послаблення (<1)", "коли перевертання ок"]):
        s += circle(402, 134 + k * 30, 3, RED, RED) + text(418, 138 + k * 30, it, 9.5, INK, "start")
    s += text(W / 2, H - 12, "Часто вирішує вхідний опір: не можна вантажити — неінвертуючий; потрібна земля — інвертуючий.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-4-5-when-each.svg", s)


# ── Рис. 13.4.6 — числа ───────────────────────────────────────────────────────
def fig134_worked():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Та сама величина ×10 — двома схемами", 15, INK, "middle", "bold")
    s += _frame(40, 54, 300, 210, "інвертуючий")
    s += text(190, 86, "Rin=1к, Rf=10к", 11, INK, "middle", "bold")
    s += text(190, 110, "−Rf/Rin = −10", 11, RED, "middle", "bold")
    s += text(190, 144, "Vin = +0.5 В", 10.5, INK, "middle")
    s += rect(80, 162, 220, 44, "#fbeeef", RED, 1.4, 6)
    s += text(190, 188, "Vout = −5.0 В", 13, RED, "middle", "bold")
    s += text(190, 232, "Zin = 1 кОм · перевернуто", 9, INK, "middle")
    s += _frame(380, 54, 300, 210, "неінвертуючий")
    s += text(530, 86, "Rg=1к, Rf=9к", 11, INK, "middle", "bold")
    s += text(530, 110, "1+Rf/Rg = 10", 11, GREEN, "middle", "bold")
    s += text(530, 144, "Vin = +0.5 В", 10.5, INK, "middle")
    s += rect(420, 162, 220, 44, "#eef6ef", GREEN, 1.4, 6)
    s += text(530, 188, "Vout = +5.0 В", 13, GREEN, "middle", "bold")
    s += text(530, 232, "Zin велетенський · той самий знак", 8.5, INK, "middle")
    s += text(W / 2, H - 10, "×10 в обох — але різний знак, різний вхідний опір і різні резистори (10 проти 9).",
              9.5, GREY, "middle", style="italic")
    save("fig-13-4-6-worked.svg", s)


# ── Рис. 13.3.1 — два золоті правила ──────────────────────────────────────────
def fig133_two_rules():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Два золоті правила розрахунку ОП", 16, INK, "middle", "bold")
    s += rect(40, 66, 320, 180, "#eef6ef", GREEN, 1.5, 10)
    s += text(200, 92, "Правило 1", 13, GREEN, "middle", "bold")
    s += text(200, 114, "у входи струм НЕ тече", 11, INK, "middle", "bold")
    s += _opamp_sym(150, 178, 80, 70)
    s += text(96, 164, "−", 12, BLUE, "start", "bold") + text(96, 198, "+", 11, RED, "start", "bold")
    s += text(122, 152, "0", 10, GREEN, "middle", "bold") + arrow(106, 162, 119, 162, GREEN, 1.6, "3 2")
    s += text(258, 180, "(∞ вхідний опір)", 9, GREY, "middle")
    s += rect(380, 66, 300, 180, "#eef6ef", GREEN, 1.5, 10)
    s += text(530, 92, "Правило 2", 13, GREEN, "middle", "bold")
    s += text(530, 114, "V₋ = V₊", 14, INK, "middle", "bold")
    s += _opamp_sym(495, 178, 80, 70)
    s += text(441, 164, "V₋", 10, BLUE, "end", "bold") + text(441, 200, "V₊", 10, RED, "end", "bold")
    s += text(468, 182, "=", 14, GREEN, "middle", "bold")
    s += text(595, 180, "(під від'ємним ЗЗ)", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Запам'ятайте ці два рядки — і будь-яка схема на ОП розрахується за кілька дій.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-3-1-two-rules.svg", s)


# ── Рис. 13.3.2 — віртуальне коротке ──────────────────────────────────────────
def fig133_virtual_short():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 30, "Віртуальне коротке: рівна напруга, але без дроту", 14.5, INK, "middle", "bold")
    cx, cy = 320, 150
    s += _opamp_sym(cx, cy, 120, 104)
    s += line(cx - 60, cy - 28, cx - 150, cy - 28, INK, 2) + text(cx - 156, cy - 24, "V₋", 12, BLUE, "end", "bold")
    s += line(cx - 60, cy + 28, cx - 150, cy + 28, INK, 2) + text(cx - 156, cy + 32, "V₊", 12, RED, "end", "bold")
    s += line(cx + 60, cy, cx + 140, cy, INK, 2) + text(cx + 146, cy + 4, "вихід", 10, INK, "start", "bold")
    s += line(cx - 110, cy - 28, cx - 110, cy + 28, GREEN, 1.8, "4 3")
    s += text(cx - 95, cy + 5, "≈", 16, GREEN, "middle", "bold")
    s += text(cx - 110, cy - 42, "однакова напруга", 9, GREEN, "middle", "bold")
    s += rect(440, 100, 220, 100, "#fbfbfb", "#c9d3dc", 1.3, 8)
    s += text(550, 124, "✓ V₋ = V₊  (напруга)", 10, GREEN, "middle", "bold")
    s += text(550, 148, "✗ струму між ними — 0", 10, RED, "middle", "bold")
    s += text(550, 172, "✗ дроту немає", 10, RED, "middle", "bold")
    s += text(W / 2, H - 12, "«Коротке» лише за напругою. Рівність тримає не дріт, а зворотний зв'язок.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-3-2-virtual-short.svg", s)


# ── Рис. 13.3.3 — віртуальна земля ────────────────────────────────────────────
def fig133_virtual_ground():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 30, "Віртуальна земля: «+» на 0 В → «−» теж на 0 В", 14.5, INK, "middle", "bold")
    cx, cy = 320, 150
    s += _opamp_sym(cx, cy, 120, 104)
    s += line(cx - 60, cy + 28, cx - 150, cy + 28, INK, 2)
    s += line(cx - 150, cy + 28, cx - 150, cy + 58, INK, 2)
    for k, wd in enumerate([20, 13, 7]):
        s += line(cx - 150 - wd / 2, cy + 60 + k * 5, cx - 150 + wd / 2, cy + 60 + k * 5, INK, 2)
    s += text(cx - 150, cy + 92, "«+» → земля (0 В)", 9, RED, "middle", "bold")
    s += line(cx - 60, cy - 28, cx - 150, cy - 28, INK, 2) + text(cx - 156, cy - 24, "«−»", 11, BLUE, "end", "bold")
    s += circle(cx - 110, cy - 28, 14, "none", GREEN, 1.8)
    s += text(cx - 110, cy - 50, "0 В", 11, GREEN, "middle", "bold")
    s += text(cx - 110, cy - 66, "(віртуальна земля)", 8.5, GREEN, "middle", "bold")
    s += line(cx + 60, cy, cx + 140, cy, INK, 2) + text(cx + 146, cy + 4, "вихід", 10, INK, "start", "bold")
    s += text(W / 2, H - 12, "Вузол «−» сидить на нулі без дроту до землі — його там тримає ОП. Зручно рахувати струми.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-3-3-virtual-ground.svg", s)


# ── Рис. 13.3.4 — виведення інвертуючого ──────────────────────────────────────
def fig133_inverting_derivation():
    W, H = 720, 310
    s = header(W, H)
    s += text(W / 2, 28, "Інвертуючий підсилювач: вивід за правилами", 14.5, INK, "middle", "bold")
    cx, cy = 400, 165
    s += _opamp_sym(cx, cy, 100, 92)
    nx, ny = cx - 50, cy - 23
    s += circle(nx, ny, 3, INK, INK)
    s += text(nx - 8, ny - 9, "0 В", 8.5, GREEN, "end", "bold")
    s += text(120, ny + 4, "Vin", 10, INK, "end", "bold")
    s += line(128, ny, 200, ny, INK, 2)
    s += rect(200, ny - 11, 56, 22, "#ffffff", INK, 1.5) + text(228, ny + 4, "Rin", 9.5, INK, "middle", "bold")
    s += line(256, ny, nx, ny, INK, 2)
    s += arrow(292, ny, 332, ny, GREEN, 2) + text(312, ny - 9, "Iin", 9, GREEN, "middle", "bold")
    s += line(cx - 50, cy + 23, cx - 90, cy + 23, INK, 2) + line(cx - 90, cy + 23, cx - 90, cy + 47, INK, 2)
    for k, wd in enumerate([16, 10, 5]):
        s += line(cx - 90 - wd / 2, cy + 49 + k * 4, cx - 90 + wd / 2, cy + 49 + k * 4, INK, 2)
    outx = cx + 50
    s += line(outx, cy, outx + 90, cy, INK, 2) + text(outx + 96, cy + 4, "Vout", 10, INK, "start", "bold")
    s += line(outx + 50, cy, outx + 50, ny - 60, INK, 2)
    s += line(outx + 50, ny - 60, nx, ny - 60, INK, 2)
    s += rect(nx + 70, ny - 71, 56, 22, "#ffffff", INK, 1.5) + text(nx + 98, ny - 56, "Rf", 9.5, INK, "middle", "bold")
    s += line(nx, ny - 60, nx, ny, INK, 2)
    s += arrow(nx + 8, ny - 60, nx + 36, ny - 60, GREEN, 2) + text(nx + 46, ny - 69, "Iin", 9, GREEN, "middle")
    s += rect(150, 250, 420, 42, LGRN, GREEN, 1.4, 8)
    s += text(360, 277, "Vout / Vin = − Rf / Rin", 15, GREEN, "middle", "bold")
    save("fig-13-3-4-inverting-derivation.svg", s)


# ── Рис. 13.3.5 — рецепт ──────────────────────────────────────────────────────
def fig133_recipe():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Рецепт розрахунку схеми на ОП", 16, INK, "middle", "bold")
    steps = [
        ("1", "перевір: зв'язок ВІД'ЄМНИЙ (на «−»)", "#fbeeef"),
        ("2", "постав V₋ = V₊  (віртуальне коротке)", "#eef6ef"),
        ("3", "у входи струм не тече (правило 1)", "#eef6ef"),
        ("4", "запиши струми: закон Ома + Кірхгоф", "#eef6ef"),
        ("5", "розв'яжи — 2–3 рядки", "#eef6ef"),
    ]
    y = 70
    for num, txt, fill in steps:
        s += circle(90, y + 18, 14, "#eef2f6", INK, 1.4) + text(90, y + 23, num, 12, INK, "middle", "bold")
        s += rect(120, y, 480, 38, fill, "#c9d3dc", 1.3, 6)
        s += text(140, y + 24, txt, 11.5, INK, "start", "bold")
        y += 46
    s += text(W / 2, H - 12, "Перший крок — найважливіший: без від'ємного зв'язку решта правил не діють.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-3-5-recipe.svg", s)


# ── Рис. 13.3.6 — лише з від'ємним ЗЗ ─────────────────────────────────────────
def fig133_only_with_feedback():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Правила діють ЛИШЕ з від'ємним зворотним зв'язком", 14, INK, "middle", "bold")
    s += _frame(40, 54, 300, 200, "є від'ємний ЗЗ")
    s += _opamp_sym(170, 150, 84, 74)
    s += line(212, 150, 250, 150, INK, 2) + circle(236, 150, 3, INK, INK)
    s += line(236, 150, 236, 96, GREEN, 2) + line(236, 96, 100, 96, GREEN, 2) + line(100, 96, 100, 132, GREEN, 2) + arrow(100, 114, 100, 134, GREEN, 2)
    s += text(190, 202, "V₋ = V₊ ✓  → правила діють", 9.5, GREEN, "middle", "bold")
    s += _frame(380, 54, 300, 200, "нема зв'язку (або на «+»)")
    s += _opamp_sym(510, 150, 84, 74)
    s += line(552, 150, 640, 150, INK, 2) + text(646, 154, "+Vs", 10, RED, "end", "bold")
    s += text(566, 130, "на рейці", 9, RED, "middle", "bold")
    s += text(530, 202, "V₋ ≠ V₊ ✗  → це компаратор", 9.5, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Перший крок будь-якого аналізу — поглянути, куди йде петля. На «−» — підсилювач; інакше — інша історія.",
              9, GREY, "middle", style="italic")
    save("fig-13-3-6-only-with-feedback.svg", s)


# ── Рис. 13.2.1 — петля зворотного зв'язку ───────────────────────────────────
def fig132_feedback_loop():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 30, "Від'ємний зворотний зв'язок: вихід → на вхід «−»", 14.5, INK, "middle", "bold")
    cx, cy = 300, 160
    s += _opamp_sym(cx, cy, 110, 96)
    s += line(cx - 55, cy - 24, cx - 150, cy - 24, INK, 2) + text(cx - 156, cy - 20, "−", 13, BLUE, "end", "bold")
    s += line(cx - 55, cy + 24, cx - 150, cy + 24, INK, 2) + text(cx - 156, cy + 28, "+", 12, RED, "end", "bold")
    s += text(cx - 110, cy + 46, "вхід", 9, GREY, "middle")
    outx = cx + 55
    s += line(outx, cy, outx + 150, cy, INK, 2) + text(outx + 156, cy + 4, "вихід", 10.5, INK, "start", "bold")
    s += circle(outx + 90, cy, 3, INK, INK)
    s += line(outx + 90, cy, outx + 90, cy - 90, GREEN, 2.2)
    s += line(outx + 90, cy - 90, cx - 110, cy - 90, GREEN, 2.2)
    s += arrow(cx - 110, cy - 90, cx - 110, cy - 26, GREEN, 2.2)
    s += circle(cx - 110, cy - 24, 3, INK, INK)
    s += text((outx + 90 + cx - 110) / 2, cy - 100, "зворотний зв'язок (частина виходу)", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Якщо вихід підскочить — більше повернеться на «−» — це штовхне вихід назад. Контур сам гасить відхилення.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-2-1-feedback-loop.svg", s)


# ── Рис. 13.2.2 — самобалансування ───────────────────────────────────────────
def fig132_self_balance():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 30, "Рівновага: ОП тримає V₋ = V₊", 16, INK, "middle", "bold")
    cx, cy = 280, 150
    s += _opamp_sym(cx, cy, 120, 100)
    s += line(cx - 60, cy - 26, cx - 140, cy - 26, INK, 2) + text(cx - 146, cy - 22, "V₋", 12, BLUE, "end", "bold")
    s += line(cx - 60, cy + 26, cx - 140, cy + 26, INK, 2) + text(cx - 146, cy + 30, "V₊", 12, RED, "end", "bold")
    s += line(cx + 60, cy, cx + 150, cy, INK, 2) + text(cx + 156, cy + 4, "вихід", 10.5, INK, "start", "bold")
    s += text(cx - 95, cy + 5, "≈", 22, GREEN, "middle", "bold")
    s += text(cx + 92, cy - 70, "вихід стає таким,", 10, INK, "middle")
    s += text(cx + 92, cy - 52, "щоб V₋ = V₊", 11, GREEN, "middle", "bold")
    s += rect(440, 172, 220, 82, "#eef6ef", GREEN, 1.4, 8)
    s += text(550, 198, "ОП «робить що завгодно»", 9.5, INK, "middle", "bold")
    s += text(550, 218, "зі своїм виходом,", 9.5, INK, "middle")
    s += text(550, 236, "аби зрівняти входи", 9.5, INK, "middle")
    s += text(W / 2, H - 10, "Велетенське A не дасть різниці входів бути помітною — тож у рівновазі вони майже рівні.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-2-2-self-balance.svg", s)


# ── Рис. 13.2.3 — від'ємний проти додатного ──────────────────────────────────
def fig132_negative_vs_positive():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Знак входу вирішує: «−» вгамовує, «+» розганяє", 14.5, INK, "middle", "bold")
    s += _frame(40, 54, 300, 210, "зв'язок на «−» — стабільно")
    s += _opamp_sym(160, 150, 86, 76)
    s += text(124, 134, "−", 11, BLUE, "start", "bold") + text(124, 172, "+", 10, RED, "start", "bold")
    s += line(203, 150, 250, 150, INK, 2) + circle(232, 150, 3, INK, INK)
    s += line(232, 150, 232, 90, GREEN, 2) + line(232, 90, 90, 90, GREEN, 2) + line(90, 90, 90, 131, GREEN, 2) + arrow(90, 110, 90, 133, GREEN, 2)
    s += text(170, 196, "вихід застигає в рівновазі", 9, GREEN, "middle", "bold")
    s += _frame(380, 54, 300, 210, "зв'язок на «+» — лавина")
    s += _opamp_sym(500, 150, 86, 76)
    s += text(464, 134, "−", 11, BLUE, "start", "bold") + text(464, 172, "+", 10, RED, "start", "bold")
    s += line(543, 150, 590, 150, INK, 2) + circle(572, 150, 3, INK, INK)
    s += line(572, 150, 572, 212, RED, 2) + line(572, 212, 430, 212, RED, 2) + line(430, 212, 430, 169, RED, 2) + arrow(430, 191, 430, 167, RED, 2)
    s += text(510, 240, "вихід летить на рейку й залипає", 9, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Та сама схема, інший вхід для зв'язку — і поведінка протилежна: рівновага проти лавини.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-2-3-negative-vs-positive.svg", s)


# ── Рис. 13.2.4 — обмін підсилення на точність ───────────────────────────────
def fig132_gain_for_precision():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Обмін: велетенське хитке A → точне підсилення", 15, INK, "middle", "bold")
    s += rect(60, 70, 240, 150, "#fbeeef", RED, 1.5, 10)
    s += text(180, 96, "розімкнене A", 12, RED, "middle", "bold")
    s += text(180, 124, "велетенське (×10⁵…10⁶)", 9.5, INK, "middle")
    s += text(180, 150, "АЛЕ «плаває»:", 9.5, RED, "middle", "bold")
    s += text(180, 170, "екземпляр, t°, частота", 9, INK, "middle")
    s += text(180, 200, "→ непридатне для точності", 8.5, GREY, "middle", style="italic")
    s += arrow(308, 145, 360, 145, GREEN, 3) + text(334, 130, "ЗЗ", 10, GREEN, "middle", "bold")
    s += rect(370, 70, 290, 150, "#eef6ef", GREEN, 1.5, 10)
    s += text(515, 96, "замкнене підсилення", 12, GREEN, "middle", "bold")
    s += text(515, 124, "скромне (напр. ×10)", 9.5, INK, "middle")
    s += text(515, 150, "зате ТОЧНЕ й СТАБІЛЬНЕ:", 9.5, GREEN, "middle", "bold")
    s += text(515, 170, "задане резисторами", 9, INK, "middle")
    s += text(515, 200, "→ передбачуване, як скеля", 8.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 12, "Віддаємо більшість підсилення в петлю — а здобуваємо точність, яку дають дешеві резистори.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-2-4-gain-for-precision.svg", s)


# ── Рис. 13.2.5 — резистори правлять ─────────────────────────────────────────
def fig132_resistors_set_gain():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "A гуляє вдвічі — підсилення схеми майже не змінюється", 14, INK, "middle", "bold")
    s += text(180, 74, "власне A приладу:", 10, INK, "middle", "bold")
    s += rect(110, 100, 50, 110, "#fbeaea", RED, 1.4) + text(135, 226, "100k", 9, INK, "middle")
    s += rect(200, 90, 50, 120, "#fbeaea", RED, 1.4) + text(225, 226, "200k", 9, INK, "middle")
    s += text(180, 248, "(плаває)", 8.5, RED, "middle", "bold")
    s += text(520, 74, "підсилення схеми:", 10, INK, "middle", "bold")
    s += line(380, 150, 660, 150, GREEN, 3)
    s += circle(420, 150, 4, GREEN, GREEN) + circle(520, 150, 4, GREEN, GREEN) + circle(620, 150, 4, GREEN, GREEN)
    s += text(520, 138, "≈ 10  (стабільне)", 11, GREEN, "middle", "bold")
    s += text(520, 182, "тримають резистори, не A", 9.5, INK, "middle")
    s += text(520, 210, "надлишок A → тугіше V₋=V₊", 9, GREY, "middle", style="italic")
    s += text(W / 2, H - 12, "Поки A «достатньо велетенське», зворотний зв'язок ковтає всі його коливання. Резистори правлять.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-2-5-resistors-set-gain.svg", s)


# ── Рис. 13.2.6 — термостат ──────────────────────────────────────────────────
def fig132_thermostat():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "«Термостат для напруги»: ОП вирівнює входи", 15, INK, "middle", "bold")
    cx, cy = 300, 150
    s += _opamp_sym(cx, cy, 110, 96)
    s += line(cx - 55, cy - 24, cx - 160, cy - 24, INK, 2) + text(cx - 166, cy - 20, "фактичне («−»)", 9.5, BLUE, "end", "bold")
    s += line(cx - 55, cy + 24, cx - 160, cy + 24, INK, 2) + text(cx - 166, cy + 28, "бажане («+»)", 9.5, RED, "end", "bold")
    s += line(cx + 55, cy, cx + 130, cy, INK, 2) + text(cx + 136, cy + 4, "вихід", 10, INK, "start", "bold")
    s += circle(cx + 90, cy, 3, INK, INK)
    s += line(cx + 90, cy, cx + 90, cy - 86, GREEN, 2) + line(cx + 90, cy - 86, cx - 130, cy - 86, GREEN, 2)
    s += arrow(cx - 130, cy - 86, cx - 130, cy - 26, GREEN, 2) + circle(cx - 130, cy - 24, 3, INK, INK)
    s += rect(498, 95, 196, 110, "#eef2f6", "#9bb0c2", 1.3, 8)
    s += text(596, 120, "як термостат:", 10.5, INK, "middle", "bold")
    s += text(596, 142, "ставиш t°,", 9.5, INK, "middle")
    s += text(596, 160, "він гріє / не гріє,", 9.5, INK, "middle")
    s += text(596, 178, "аби збіглося", 9.5, INK, "middle")
    s += text(W / 2, H - 12, "Ти задаєш бажане — ОП жене вихід туди, де фактичне зрівняється з бажаним. І тримає.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-2-6-thermostat.svg", s)


# ── Рис. 13.1.1 — символ і виводи ────────────────────────────────────────────
def fig131_symbol_pins():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 32, "Операційний підсилювач: входи, вихід, живлення", 15, INK, "middle", "bold")
    cx, cy = 300, 160
    s += _opamp_sym(cx, cy, 130, 110)
    s += line(cx - 65, cy - 28, cx - 150, cy - 28, INK, 2) + text(cx - 156, cy - 24, "вхід −", 10.5, BLUE, "end", "bold")
    s += line(cx - 65, cy + 28, cx - 150, cy + 28, INK, 2) + text(cx - 156, cy + 32, "вхід +", 10.5, RED, "end", "bold")
    s += text(cx - 150, cy - 44, "(інвертуючий)", 8, GREY, "end")
    s += text(cx - 150, cy + 48, "(неінвертуючий)", 8, GREY, "end")
    s += line(cx + 65, cy, cx + 150, cy, INK, 2) + text(cx + 156, cy + 4, "вихід", 10.5, INK, "start", "bold")
    s += line(cx - 20, cy - 38, cx - 20, cy - 92, RED, 1.8) + text(cx - 20, cy - 100, "+Vs", 9.5, RED, "middle", "bold")
    s += line(cx - 20, cy + 38, cx - 20, cy + 92, BLUE, 1.8) + text(cx - 20, cy + 106, "−Vs", 9.5, BLUE, "middle", "bold")
    s += rect(470, 130, 192, 60, LGRN, GREEN, 1.5, 8)
    s += text(566, 165, "Vout = A·(V₊−V₋)", 13, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Підсилює різницю входів на велетенське A. Живлення (±Vs) задає межі, у яких гойдається вихід.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-1-1-symbol-pins.svg", s)


# ── Рис. 13.1.2 — підсилювач різниці ─────────────────────────────────────────
def fig131_differential():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "ОП підсилює різницю, а спільне — відкидає", 15, INK, "middle", "bold")

    def panel(ox, title, v1, v2, out, col):
        t = _frame(ox, 54, 300, 210, title)
        cx, cy = ox + 150, 150
        t += _opamp_sym(cx, cy, 96, 84)
        t += text(cx - 44, cy - 20, v1, 10, INK, "start")
        t += text(cx - 44, cy + 26, v2, 10, INK, "start")
        t += line(cx + 48, cy, cx + 110, cy, INK, 2)
        t += text(cx + 116, cy + 4, out, 12, col, "start", "bold")
        return t

    s += panel(40, "входи РІЗНІ", "−: 0 В", "+: 1 мВ", "× A", GREEN)
    s += panel(380, "входи ОДНАКОВІ", "−: 5 В", "+: 5 В", "0", RED)
    s += text(W / 2, H - 12, "Зліва є різниця (1 мВ) → велике підсилення. Справа входи однакові (різниці нема) → нуль, хай навіть по 5 В.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-1-2-differential.svg", s)


# ── Рис. 13.1.3 — три припущення ─────────────────────────────────────────────
def fig131_ideal_assumptions():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Ідеальний ОП: три припущення", 16, INK, "middle", "bold")
    cards = [
        ("∞ підсилення", ["найменша різниця", "→ велетенський вихід"]),
        ("∞ вхідний опір", ["у входи струм", "не тече зовсім"]),
        ("0 вихідний опір", ["вихід тримає напругу", "під будь-яким навант."]),
    ]
    cw, gap = 210, 20
    for i, (head, lines) in enumerate(cards):
        x = 30 + i * (cw + gap)
        s += rect(x, 70, cw, 150, "#eef6ef", GREEN, 1.5, 10)
        s += text(x + cw / 2, 106, head, 14, GREEN, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(x + cw / 2, 142 + k * 24, ln, 10, INK, "middle")
    s += text(W / 2, H - 14, "Ці три «брехні» майже не брешуть — і роблять розрахунок схем на ОП тривіальним.",
              10, GREY, "middle", style="italic")
    save("fig-13-1-3-ideal-assumptions.svg", s)


# ── Рис. 13.1.4 — велетенське підсилення ─────────────────────────────────────
def fig131_huge_gain():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Підсилення таке велике, що крива — майже сходинка", 14.5, INK, "middle", "bold")
    ox, oy, ww, hh = 110, 158, 430, 104
    midx = ox + ww / 2
    s += arrow(ox, oy, ox + ww + 14, oy, INK, 2) + text(ox + ww + 18, oy + 4, "V₊−V₋", 11, INK, "start", "bold")
    s += arrow(midx, oy + hh + 12, midx, oy - hh - 12, INK, 2) + text(midx + 8, oy - hh - 14, "Vout", 11, INK, "start", "bold")
    s += _poly([(ox, oy + hh), (midx - 6, oy + hh), (midx + 6, oy - hh), (ox + ww, oy - hh)], RED, 2.8)
    s += line(ox, oy - hh, ox + ww, oy - hh, GREY, 1, "4 3") + text(ox + ww + 2, oy - hh, "+Vs", 9, RED, "start", "bold")
    s += line(ox, oy + hh, ox + ww, oy + hh, GREY, 1, "4 3") + text(ox + ww + 2, oy + hh + 4, "−Vs", 9, BLUE, "start", "bold")
    s += text(midx + 78, oy - 26, "нахил = A (величезний)", 9.5, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Кілька десятків мікровольтів різниці — і вихід уже на рейці. Робочої «лінійної» зони майже нема.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-1-4-huge-gain.svg", s)


# ── Рис. 13.1.5 — насичення на рейках ────────────────────────────────────────
def fig131_rails_saturate():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Вихід не вискочить за рейки живлення", 15, INK, "middle", "bold")
    ox, oy, ww = 90, 158, 480
    s += line(ox, oy, ox + ww, oy, GREY, 1)
    s += line(ox, oy - 70, ox + ww, oy - 70, RED, 1.6, "5 4") + text(ox - 6, oy - 66, "+Vs", 9.5, RED, "end", "bold")
    s += line(ox, oy + 70, ox + ww, oy + 70, BLUE, 1.6, "5 4") + text(ox - 6, oy + 74, "−Vs", 9.5, BLUE, "end", "bold")
    s += _clip_sine(ox, oy, ww, 130, 2, INK, lo=-0.538, hi=0.538)
    s += text(ox + ww / 2, oy - 92, "формула «хоче» далеко вгору ↑", 9, GREY, "middle")
    s += text(ox + ww / 2, oy + 96, "…але вихід застрягає на рейці", 9.5, INK, "middle", "bold")
    s += text(W / 2, H - 10, "Хоч би що казала формула Vout=A·ΔV, вихід гойдається лише між −Vs і +Vs і там насичується.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-1-5-rails-saturate.svg", s)


# ── Рис. 13.1.6 — потрібен зворотний зв'язок ─────────────────────────────────
def fig131_needs_feedback():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Без зворотного зв'язку ОП — компаратор, не підсилювач", 14, INK, "middle", "bold")

    def panel(ox, title, plus_bigger):
        t = _frame(ox, 54, 300, 200, title)
        cx, cy = ox + 130, 145
        t += _opamp_sym(cx, cy, 96, 84)
        t += line(cx + 48, cy, cx + 120, cy, INK, 2)
        if plus_bigger:
            t += text(cx - 46, cy - 20, "−: трохи ↓", 9, BLUE, "start")
            t += text(cx - 46, cy + 26, "+: трохи ↑", 9, RED, "start")
            t += text(cx + 126, cy + 4, "+Vs", 12, RED, "start", "bold")
            t += text(ox + 150, 232, "вихід ЗЛЕТІВ угору", 9.5, RED, "middle", "bold")
        else:
            t += text(cx - 46, cy - 20, "−: трохи ↑", 9, BLUE, "start")
            t += text(cx - 46, cy + 26, "+: трохи ↓", 9, RED, "start")
            t += text(cx + 126, cy + 4, "−Vs", 12, BLUE, "start", "bold")
            t += text(ox + 150, 232, "вихід УПАВ униз", 9.5, BLUE, "middle", "bold")
        return t

    s += panel(40, "«+» трохи більший", True)
    s += panel(380, "«−» трохи більший", False)
    s += text(W / 2, H - 10, "Найменша перевага одного входу кидає вихід на рейку. Це готовий компаратор (§13.7) — але не лінійний підсилювач.",
              9, GREY, "middle", style="italic")
    save("fig-13-1-6-needs-feedback.svg", s)


def fig139_ideal_vs_real():
    W, H = 720, 350
    s = header(W, H)
    s += text(W / 2, 28, "Ідеальний ОП проти реального", 16, INK, "middle", "bold")
    x0, y0, colw, rh = 60, 54, 600, 44
    rows = [
        ("параметр", "ідеал", "реальність"),
        ("підсилення A", "∞", "сотні тисяч"),
        ("вхідний опір", "∞", "дуже великий"),
        ("вихідний опір", "0", "малий, не 0"),
        ("зсув нуля Vos", "0", "одиниці мВ"),
        ("реакція", "миттєва", "смуга + SR"),
    ]
    c1, c2, c3 = x0 + 120, x0 + 330, x0 + 510
    for i, (a, b, c) in enumerate(rows):
        ry = y0 + i * rh
        head = (i == 0)
        fill = "#e9eefb" if head else ("#f7f9fc" if i % 2 else "#ffffff")
        s += rect(x0, ry, colw, rh, fill, "#c9d3dc", 1.2)
        s += text(c1, ry + rh / 2 + 5, a, 12.5, INK, "middle", "bold" if head else "normal")
        s += text(c2, ry + rh / 2 + 5, b, 14, INK if head else GREEN, "middle", "bold")
        s += text(c3, ry + rh / 2 + 5, c, 13, INK if head else RED, "middle", "bold")
    s += line(x0 + 240, y0, x0 + 240, y0 + len(rows) * rh, "#c9d3dc", 1)
    s += line(x0 + 420, y0, x0 + 420, y0 + len(rows) * rh, "#c9d3dc", 1)
    s += text(W / 2, H - 14, "Реальність — лише маленькі поправки до ідеалу: підсилення скінченне, зсув кілька мВ, реакція не миттєва.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-9-1-ideal-vs-real.svg", s)


def fig139_offset():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Зсув нуля: стала похибка з нічого", 16, INK, "middle", "bold")
    cx, cy = 230, 158
    s += _opamp_sym(cx, cy, 120, 100)
    lx = 95
    s += line(lx, cy - 25, cx - 60, cy - 25, INK, 2)
    s += line(lx, cy + 25, cx - 60, cy + 25, INK, 2)
    s += line(lx, cy - 25, lx, cy + 25, INK, 2)
    s += line(lx, cy, lx - 26, cy, INK, 2)
    gx = lx - 26
    s += line(gx, cy - 10, gx, cy + 10, INK, 2)
    s += line(gx - 9, cy + 10, gx + 9, cy + 10, INK, 2)
    s += line(gx - 5, cy + 14, gx + 5, cy + 14, INK, 2)
    s += line(gx - 2, cy + 18, gx + 2, cy + 18, INK, 2)
    s += text(lx + 22, cy - 38, "обидва входи однакові", 9, GREY, "middle")
    bx = (lx + cx - 60) / 2
    s += line(bx - 5, cy - 35, bx - 5, cy - 15, INK, 1.8)
    s += line(bx + 5, cy - 30, bx + 5, cy - 20, INK, 4)
    s += text(bx, cy - 47, "Vos ≈ 2 мВ", 10, RED, "middle", "bold")
    px = 420
    s += rect(px, 90, 250, 134, "#fbfbfb", "#c9d3dc", 1.3, 8)
    s += arrow(cx + 60, cy, px - 2, cy, INK, 2)
    s += text((cx + 60 + px) / 2, cy - 9, "× A", 11, INK, "middle", "bold")
    s += text(px + 125, 118, "Vos × підсилення", 12, INK, "middle", "bold")
    s += text(px + 125, 148, "2 мВ × 100 = 0.2 В", 14, RED, "middle", "bold")
    s += line(px + 20, 164, px + 230, 164, FAINT, 1)
    s += text(px + 125, 188, "стала похибка на виході", 11, INK, "middle")
    s += text(px + 125, 208, "(навіть без сигналу)", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Крихітна несиметрія входів, помножена на підсилення, осідає на виході сталою похибкою. Кусає точний постійний вимір.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-9-2-offset.svg", s)


def fig139_bandwidth():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Добуток підсилення на смугу (GBW) — сталий", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 110, 250, 470, 180
    s += _axes(ox, oy, ww, hh, "частота", "підсилення")
    flab = ["100", "1к", "10к", "100к", "1М"]
    for i, l in enumerate(flab):
        x = ox + i / 4 * ww
        s += line(x, oy, x, oy - hh, FAINT, 1)
        s += text(x, oy + 16, l, 9, GREY, "middle")
    glab = ["1", "10", "100", "1к", "10к"]
    for i, l in enumerate(glab):
        y = oy - i / 4 * hh
        s += line(ox, y, ox + ww, y, FAINT, 1)
        s += text(ox - 10, y + 4, l, 9, GREY, "end")
    s += _poly([(ox, oy - hh), (ox + ww, oy)], RED, 2.8)

    def pt(fi, gi, lab, col):
        x = ox + fi / 4 * ww
        y = oy - gi / 4 * hh
        t = circle(x, y, 4, col, col, 1)
        t += line(x, y, x, oy, GREY, 1, "3 3")
        t += line(x, y, ox, y, GREY, 1, "3 3")
        t += text(x + 7, y - 8, lab, 9.5, col, "start", "bold")
        return t

    s += pt(2, 2, "×100 → до 10 кГц", BLUE)
    s += pt(3, 1, "×10 → до 100 кГц", GREEN)
    s += text(ox + ww - 6, oy - 16, "×1 при 1 МГц = GBW", 9.5, RED, "end", "bold")
    s += text(W / 2, H - 10, "Більше підсилення — вужча смуга, і навпаки: їхній добуток сталий. Тому велике підсилення набирають кількома каскадами.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-9-3-bandwidth.svg", s)


def fig139_slew_rate():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 26, "Швидкість наростання: вихід не встигає", 15, INK, "middle", "bold")
    ox, ww = 120, 460
    s += _frame(60, 44, 580, 100, "вхід — гарна синусоїда (великий, швидкий сигнал)")
    oy1 = 100
    s += line(ox, oy1, ox + ww, oy1, FAINT, 1)
    s += _sine(ox, oy1, ww, 34, 2, BLUE, 2.6)
    s += _frame(60, 168, 580, 110, "вихід — повзе з макс. швидкістю → трикутник")
    oy2 = 226
    s += line(ox, oy2, ox + ww, oy2, FAINT, 1)
    s += _sine(ox, oy2, ww, 38, 2, GREY, 1.2)
    pts = []
    for j in range(int(ww) + 1):
        tt = j / ww
        v = (2.0 / math.pi) * math.asin(math.sin(2 * math.pi * 2 * tt))
        pts.append((ox + j, oy2 - 38 * v))
    s += _poly(pts, RED, 2.8)
    s += text(ox + ww - 4, oy2 - 46, "мала б бути синусоїда", 8.5, GREY, "end", style="italic")
    s += text(W / 2, H - 12, "Слюінг: на швидкому великому сигналі вихід вироджується у скособочений трикутник. Це межа для великих сигналів — окрема від смуги.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-9-4-slew-rate.svg", s)


def fig139_when_matters():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Яка межа кусає саме твою задачу", 16, INK, "middle", "bold")
    rows = [
        ("точний постійний вимір", "зсув Vos, вхідний струм"),
        ("високі частоти, малий сигнал", "смуга (GBW)"),
        ("швидкий великий сигнал", "швидкість (SR)"),
        ("дуже слабкий сигнал", "власний шум"),
        ("високоомне джерело", "польові входи"),
    ]
    y0, rh = 56, 50
    for i, (task, par) in enumerate(rows):
        ry = y0 + i * rh
        s += rect(70, ry, 320, 40, "#e9eefb", "#9bb0e0", 1.3, 6)
        s += text(230, ry + 25, task, 11.5, INK, "middle", "bold")
        s += arrow(395, ry + 20, 425, ry + 20, INK, 2)
        s += rect(430, ry, 230, 40, "#eef6ef", GREEN, 1.3, 6)
        s += text(545, ry + 25, par, 11.5, "#15662c", "middle", "bold")
    s += text(W / 2, H - 14, "Знаєш свою задачу — знаєш, на який рядок даташита дивитися; решту параметрів сміливо ігноруєш.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-9-5-when-matters.svg", s)


def fig139_choosing():
    W, H = 730, 330
    s = header(W, H)
    s += text(W / 2, 26, "Немає одного «найкращого» ОП — є заточені під різне", 15, INK, "middle", "bold")
    cards = [
        ("прецизійний", "мікровольтовий зсув", "OP07"),
        ("малошумний", "тихий для давачів", "—"),
        ("швидкий", "висока SR і смуга", "—"),
        ("економний", "для батарей", "—"),
        ("rail-to-rail", "вихід до самих рейок", "—"),
        ("польові входи", "крихітний вхідний струм", "TL072"),
    ]
    cw, ch = 210, 92
    xs = [35, 260, 485]
    ys = [54, 162]
    for i, (t, sub, ex) in enumerate(cards):
        cxx = xs[i % 3]
        cyy = ys[i // 3]
        s += rect(cxx, cyy, cw, ch, "#fbfbfb", COPP, 1.4, 8)
        s += text(cxx + cw / 2, cyy + 28, t, 13, "#b5732e", "middle", "bold")
        s += text(cxx + cw / 2, cyy + 52, sub, 10, INK, "middle")
        if ex != "—":
            s += text(cxx + cw / 2, cyy + 76, "напр. " + ex, 9, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Обирай за тим параметром, що важить для твоєї задачі. На «гучні» цифри в рекламі — не зважай.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-9-6-choosing.svg", s)


if __name__ == "__main__":
    fig13_t1_timeline()
    fig13_t2_born_to_compute()
    fig13_t3_analog_computer()
    fig13_t4_k2w_tube()
    fig13_t5_shrinking()
    fig13_t6_survivor()
    # §13.1 ідеальний ОП
    fig131_symbol_pins()
    fig131_differential()
    fig131_ideal_assumptions()
    fig131_huge_gain()
    fig131_rails_saturate()
    fig131_needs_feedback()
    # §13.2 від'ємний зворотний зв'язок
    fig132_feedback_loop()
    fig132_self_balance()
    fig132_negative_vs_positive()
    fig132_gain_for_precision()
    fig132_resistors_set_gain()
    fig132_thermostat()
    # §13.3 віртуальне коротке
    fig133_two_rules()
    fig133_virtual_short()
    fig133_virtual_ground()
    fig133_inverting_derivation()
    fig133_recipe()
    fig133_only_with_feedback()
    # §13.4 інвертуючий / неінвертуючий
    fig134_inverting()
    fig134_non_inverting()
    fig134_non_inverting_derivation()
    fig134_comparison()
    fig134_when_each()
    fig134_worked()
    # §13.5 повторювач (буфер)
    fig135_follower()
    fig135_why_buffer()
    fig135_loading_problem()
    fig135_buffer_fixes()
    fig135_divider_example()
    fig135_vs_emitter_follower()
    # §13.6 суматор / різницевий
    fig136_summer()
    fig136_currents_add()
    fig136_mixer()
    fig136_difference()
    fig136_common_mode_reject()
    fig136_instrumentation()
    # §13.7 компаратор
    fig137_comparator_basic()
    fig137_open_loop()
    fig137_threshold()
    fig137_light_detector()
    fig137_applications()
    fig137_chatter_problem()
    # §13.8 гістерезис / тригер Шмітта
    fig138_two_thresholds()
    fig138_positive_feedback()
    fig138_transfer_loop()
    fig138_kills_chatter()
    fig138_thermostat()
    fig138_schmitt()
    # §13.9 реальний ОП: межі
    fig139_ideal_vs_real()
    fig139_offset()
    fig139_bandwidth()
    fig139_slew_rate()
    fig139_when_matters()
    fig139_choosing()
    print("OK — Розділ 13 (історія + §13.1–§13.9) згенеровано в", OUT)
