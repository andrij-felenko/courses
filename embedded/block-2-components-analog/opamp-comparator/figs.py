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


# ── §13.10 Що всередині ОП: диференційна пара (Рис. 2.8.10.k) ────────────────
def _isrc(cx, cy, r=15, lab="I"):
    t = circle(cx, cy, r, "#ffffff", INK, 2)
    t += arrow(cx, cy + r - 3, cx, cy - r + 3, INK, 2)
    t += text(cx + r + 8, cy + 4, lab, 11, INK, "start", "bold")
    return t


def fig1310_open_box():
    W, H = 720, 296
    s = header(W, H)
    s += text(W / 2, 30, "Відкриваємо «чорну скриньку»: усередині — три каскади", 15.5, INK, "middle", "bold")
    s += _opamp_sym(150, 150, 90, 80)
    s += text(150, 232, "ідеальна модель", 10, GREY, "middle")
    s += line(100, 130, 122, 130, BLUE, 2) + line(100, 170, 122, 170, RED, 2)
    s += line(195, 150, 226, 150, INK, 2)
    s += arrow(248, 150, 322, 150, GREY, 2.4) + text(285, 138, "відкриємо", 9, GREY, "middle", "bold")
    stages = [("вхідний", ["диф. пара", "(2 транзистори)"], LBLUE),
              ("підсилення", ["велике", "підсилення"], "#fff3e0"),
              ("вихідний", ["буфер", "(сильний струм)"], LGRN)]
    x0, bw, gap = 350, 112, 12
    for i, (t1, lines, col) in enumerate(stages):
        bx = x0 + i * (bw + gap)
        s += rect(bx, 110, bw, 84, col, "#9bb0c2", 1.5, 8)
        s += text(bx + bw / 2, 134, t1, 11, INK, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, 156 + k * 17, ln, 9.5, INK, "middle")
        if i < 2:
            s += arrow(bx + bw, 152, bx + bw + gap, 152, INK, 2)
    s += text(W / 2, 232, "ті самі транзистори цього модуля, лише зібрані з розумом", 9.5, GREY, "middle", style="italic")
    save("fig-13-10-1-open-box.svg", s)


def fig1310_diff_pair():
    W, H = 560, 404
    s = header(W, H)
    s += text(W / 2, 28, "Серце ОП: диференційна пара", 16, INK, "middle", "bold")
    vY, gY, cy = 70, 344, 200
    s += line(120, vY, 440, vY, RED, 2) + text(116, vY + 4, "+V", 10, RED, "end", "bold")
    s += line(120, gY, 440, gY, INK, 1.6) + text(116, gY + 4, "−V", 10, INK, "end", "bold")
    q1x, q2x = 235, 360
    s += _bjt_sym(q1x, cy) + _bjt_sym(q2x, cy)
    for x in (q1x + 30, q2x + 30):
        s += line(x, cy - 56, x, cy - 80, INK, 2)
        s += rect(x - 12, cy - 112, 24, 32, "#fff", INK, 1.5, 3) + text(x, cy - 92, "R", 9, INK, "middle", "bold")
        s += line(x, cy - 112, x, vY, INK, 2)
    s += circle(q2x + 30, cy - 70, 3, GREEN, GREEN) + text(q2x + 46, cy - 66, "вихід", 9.5, GREEN, "start", "bold")
    s += line(q1x + 30, cy + 56, q1x + 30, cy + 86, INK, 2) + line(q2x + 30, cy + 56, q2x + 30, cy + 86, INK, 2)
    s += line(q1x + 30, cy + 86, q2x + 30, cy + 86, INK, 2)
    tx = (q1x + 30 + q2x + 30) / 2
    s += line(tx, cy + 86, tx, cy + 102, INK, 2) + _isrc(tx, cy + 120, 16, "хвіст")
    s += line(tx, cy + 136, tx, gY, INK, 2)
    s += text(tx + 4, cy + 156, "сталий струм", 8.5, INK, "middle")
    s += circle(q1x - 44, cy, 3, BLUE, BLUE) + text(q1x - 52, cy + 4, "− вхід", 9.5, BLUE, "end", "bold")
    s += circle(q2x - 44, cy, 3, RED, RED) + text(q2x - 52, cy + 4, "+ вхід", 9.5, RED, "end", "bold")
    s += text(W / 2, H - 10, "Два однакові транзистори ділять між собою сталий струм «хвоста»; хто з входів вищий — той бере більше.",
              9, GREY, "middle", style="italic")
    save("fig-13-10-2-diff-pair.svg", s)


def fig1310_steering():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Як пара «віднімає»: вищий вхід забирає більше хвоста", 14.5, INK, "middle", "bold")

    def panel(ox, title, leftbig):
        t = _frame(ox, 52, 300, 218, title)
        midx = ox + 150
        t += _isrc(midx, 232, 14, "I")
        t += line(midx, 218, midx, 200, INK, 2) + circle(midx, 200, 3, INK, INK)
        lx, rx = ox + 78, ox + 222
        t += line(midx, 200, lx, 200, INK, 2) + line(lx, 200, lx, 150, INK, 2)
        t += line(midx, 200, rx, 200, INK, 2) + line(rx, 200, rx, 150, INK, 2)
        t += rect(lx - 22, 110, 44, 40, "#eef2f7", "#9bb0c2", 1.4, 5) + text(lx, 134, "Q1", 10, INK, "middle", "bold")
        t += rect(rx - 22, 110, 44, 40, "#eef2f7", "#9bb0c2", 1.4, 5) + text(rx, 134, "Q2", 10, INK, "middle", "bold")
        if leftbig:
            t += arrow(lx, 110, lx, 78, GREEN, 4.5) + arrow(rx, 110, rx, 94, GREY, 1.6)
            t += text(lx, 70, "більше", 9, GREEN, "middle", "bold") + text(rx, 86, "менше", 8.5, GREY, "middle")
            t += text(midx, 256, "вхід Q1 вищий → перекіс", 10, INK, "middle", "bold")
        else:
            t += arrow(lx, 110, lx, 90, GREY, 2.2) + arrow(rx, 110, rx, 90, GREY, 2.2)
            t += text(midx, 256, "входи рівні → порівну", 10, INK, "middle", "bold")
        return t
    s += panel(24, "рівновага", False)
    s += panel(372, "перекіс", True)
    s += text(W / 2, H - 8, "Сталий хвіст не змінюється — змінюється лише, кому з двох дістанеться більша частка струму.",
              9, GREY, "middle", style="italic")
    save("fig-13-10-3-steering.svg", s)


def fig1310_cmrr():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Чому «диференційна»: спільне відкидає, різницю підсилює", 14, INK, "middle", "bold")

    def panel(ox, title, common):
        t = _frame(ox, 52, 300, 218, title)
        midx = ox + 150
        if common:
            t += arrow(ox + 72, 196, ox + 72, 120, SUN, 3) + arrow(ox + 228, 196, ox + 228, 120, SUN, 3)
            t += text(ox + 72, 210, "↑ обидва", 8.5, SUN, "middle", "bold") + text(ox + 228, 210, "↑ обидва", 8.5, SUN, "middle", "bold")
            t += text(midx, 102, "поділ хвоста НЕ змінився", 9.5, INK, "middle", "bold")
            t += rect(midx - 46, 130, 92, 32, LGRN, GREEN, 1.5, 6) + text(midx, 151, "вихід = 0", 12, GREEN, "middle", "bold")
            t += text(midx, 250, "синфазна завада — відкинута", 9.5, GREEN, "middle", "bold")
        else:
            t += arrow(ox + 72, 196, ox + 72, 120, RED, 3) + arrow(ox + 228, 120, ox + 228, 196, BLUE, 3)
            t += text(ox + 72, 210, "↑ один", 8.5, RED, "middle", "bold") + text(ox + 228, 110, "↓ інший", 8.5, BLUE, "middle", "bold")
            t += rect(midx - 46, 138, 92, 32, LRED, RED, 1.5, 6) + text(midx, 159, "вихід ↑↑", 12, RED, "middle", "bold")
            t += text(midx, 250, "різницю — підсилює", 9.5, RED, "middle", "bold")
        return t
    s += panel(24, "синфазно (обидва разом)", True)
    s += panel(372, "різниця", False)
    s += text(W / 2, H - 8, "Шум, наведений на обидва входи однаково, не зрушує поділ струму — і зникає. Лишається сама різниця.",
              9, GREY, "middle", style="italic")
    save("fig-13-10-4-cmrr.svg", s)


def fig1310_three_stages():
    W, H = 740, 300
    s = header(W, H)
    s += text(W / 2, 28, "Три каскади — три ідеальні риси ОП", 16, INK, "middle", "bold")
    stages = [
        ("вхід: диф. пара", ["високий вхідний опір", "+ реагує на різницю"], LBLUE),
        ("підсилення", ["величезне", "підсилення A"], "#fff3e0"),
        ("вихід: буфер", ["низький", "вихідний опір"], LGRN),
    ]
    x0, bw, gap = 40, 210, 20
    for i, (t1, props, col) in enumerate(stages):
        bx = x0 + i * (bw + gap)
        s += rect(bx, 80, bw, 58, col, "#9bb0c2", 1.6, 8)
        s += text(bx + bw / 2, 115, t1, 13, INK, "middle", "bold")
        if i < 2:
            s += arrow(bx + bw, 109, bx + bw + gap, 109, INK, 2.2)
        s += arrow(bx + bw / 2, 140, bx + bw / 2, 174, GREY, 1.8)
        s += rect(bx + 10, 176, bw - 20, 68, "#f6f8fb", "#c9d3dc", 1.2, 6)
        for k, ln in enumerate(props):
            s += text(bx + bw / 2, 204 + k * 20, ln, 10.5, INK, "middle", "bold")
    s += text(W / 2, H - 12, "«Ідеальний ОП» з §2.8.1 — це і є ці три каскади: вхід нічого не вантажить, середина шалено підсилює, вихід тягне струм.",
              9, GREY, "middle", style="italic")
    save("fig-13-10-5-three-stages.svg", s)


def fig1310_limits():
    W, H = 720, 332
    s = header(W, H)
    s += text(W / 2, 28, "Звідки беруться вади реального ОП (§2.8.9)", 15, INK, "middle", "bold")
    s += rect(40, 92, 150, 150, "#eef2f7", "#7f93a8", 1.6, 8)
    s += text(115, 150, "реальні", 12, INK, "middle", "bold")
    s += text(115, 170, "транзистори", 12, INK, "middle", "bold")
    s += text(115, 190, "всередині", 11, GREY, "middle")
    causes = [
        ("неідеальна пара транзисторів", "→ напруга зсуву (offset)", 86),
        ("входи беруть трохи струму", "→ вхідний струм зсуву", 140),
        ("хвіст заряджає ємність не миттєво", "→ швидкість наростання (SR)", 194),
        ("ємність навмисне зрізає підсилення", "→ скінченна смуга", 248),
    ]
    for cause, eff, y in causes:
        s += arrow(190, 167, 268, y + 8, GREY, 1.6)
        s += rect(270, y - 10, 424, 36, "#f6f8fb", "#c9d3dc", 1.2, 6)
        s += text(284, y + 4, cause, 10, INK, "start", "bold")
        s += text(284, y + 19, eff, 9.5, RED, "start")
    s += text(W / 2, H - 10, "Кожна «вада» з §2.8.9 — це слід реального транзистора всередині. Магії нема — є інженерія.",
              9, GREY, "middle", style="italic")
    save("fig-13-10-6-limits.svg", s)


# ── §13.11 LDO зсередини (Рис. 2.8.11.k) ────────────────────────────────────
def fig1311_architecture():
    W, H = 720, 350
    s = header(W, H)
    s += text(W / 2, 28, "LDO зсередини: клапан-транзистор під наглядом ОП", 15.5, INK, "middle", "bold")
    y = 92
    s += text(40, y + 5, "Vin", 11, RED, "end", "bold") + line(44, y, 110, y, RED, 2)
    s += rect(110, y - 28, 150, 56, "#fff3e0", COPP, 1.8, 8)
    s += text(185, y - 4, "транзистор-клапан", 9.5, INK, "middle", "bold") + text(185, y + 13, "(прохідний)", 8.5, GREY, "middle")
    s += arrow(260, y, 462, y, INK, 2.4)
    s += circle(470, y, 3, INK, INK) + text(470, y - 12, "Vout", 11, GREEN, "middle", "bold")
    s += line(470, y, 540, y, INK, 2) + rect(540, y - 20, 46, 40, "#fff", INK, 1.5, 4) + text(563, y + 4, "наван.", 8.5, INK, "middle")
    s += line(470, y, 470, 152, INK, 1.6)
    s += rect(430, 152, 80, 54, "#eef2f7", "#9bb0c2", 1.5, 6) + text(470, 173, "дільник", 9.5, INK, "middle", "bold") + text(470, 190, "R1 / R2", 9, INK, "middle")
    s += line(470, 206, 470, 300, INK, 1.6)
    s += rect(250, 232, 150, 68, LBLUE, BLUE, 1.6, 8) + text(325, 260, "ОП — звіряє", 11, INK, "middle", "bold") + text(325, 280, "відвід із Vref", 9.5, INK, "middle")
    s += arrow(430, 266, 400, 266, INK, 2)
    s += rect(60, 248, 80, 40, "#e9f3e9", GREEN, 1.5, 6) + text(100, 272, "Vref", 11, GREEN, "middle", "bold")
    s += arrow(140, 268, 250, 268, GREEN, 2) + text(195, 258, "еталон", 8, GREEN, "middle")
    s += line(325, 232, 325, 132, INK, 2) + line(325, 132, 185, 132, INK, 2) + arrow(185, 132, 185, 122, INK, 2)
    s += text(345, 175, "керує клапаном", 8.5, GREEN, "start", "bold")
    s += text(W / 2, H - 12, "Петля: ОП порівнює частку Vout із еталоном Vref і підкручує клапан так, щоб вони збіглися.",
              9, GREY, "middle", style="italic")
    save("fig-13-11-1-architecture.svg", s)


def _box2(cx, cy, w, h, l1, l2, fill, col):
    t = rect(cx - w / 2, cy - h / 2, w, h, fill, col, 1.6, 8)
    t += text(cx, cy - 3, l1, 10, INK, "middle", "bold")
    t += text(cx, cy + 13, l2, 9.5, INK, "middle")
    return t


def fig1311_feedback():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 28, "Від'ємний зв'язок тримає Vout: самовиправлення", 15, INK, "middle", "bold")
    nodes = [
        (350, 80, "Vout просів", "(зросло навант.)", LRED, RED),
        (548, 180, "відвід < Vref", "ОП це бачить", LBLUE, BLUE),
        (350, 282, "ОП дужче", "відкрив клапан", LGRN, GREEN),
        (152, 180, "Vout повернувся", "до норми", "#fff3e0", COPP),
    ]
    for cx, cy, l1, l2, fill, col in nodes:
        s += _box2(cx, cy, 168, 52, l1, l2, fill, col)
    s += arrow(420, 96, 500, 156, GREY, 2.2)
    s += arrow(520, 214, 420, 262, GREY, 2.2)
    s += arrow(280, 262, 190, 214, GREY, 2.2)
    s += arrow(184, 152, 286, 100, GREY, 2.2)
    s += text(350, 182, "та сама петля,", 10, INK, "middle", "bold")
    s += text(350, 200, "що термостат §2.8.2", 9.5, GREY, "middle")
    s += text(W / 2, H - 12, "Будь-яке відхилення Vout сама схема й гасить — точно як від'ємний зв'язок у підсилювачі.",
              9, GREY, "middle", style="italic")
    save("fig-13-11-2-feedback.svg", s)


def fig1311_noninv_disguise():
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 28, "LDO — це неінвертуючий підсилювач, лише вхід = Vref", 14.5, INK, "middle", "bold")
    s += _opamp_sym(250, 150, 84, 70)
    s += rect(70, 168, 70, 36, "#e9f3e9", GREEN, 1.5, 6) + text(105, 190, "Vref", 11, GREEN, "middle", "bold")
    s += line(140, 186, 208, 168, GREEN, 1.8)
    s += text(196, 134, "+", 12, RED, "middle", "bold")
    s += text(196, 176, "−", 12, BLUE, "middle", "bold")
    # вихід -> прохідний транзистор -> Vout
    s += line(292, 150, 330, 150, INK, 2)
    s += _mosfet_sym(366, 150, pch=True)
    s += line(390, 106, 390, 80, RED, 2) + text(390, 72, "Vin", 9.5, RED, "middle", "bold")
    s += line(390, 194, 390, 230, INK, 2) + circle(390, 230, 3, INK, INK) + text(404, 226, "Vout", 11, GREEN, "start", "bold")
    # дільник
    s += line(390, 230, 470, 230, INK, 1.6) + line(470, 230, 470, 150, INK, 1.6)
    s += rect(458, 110, 24, 28, "#fff", INK, 1.4, 3) + text(490, 126, "R1", 9, INK, "start", "bold")
    s += line(470, 110, 470, 86, INK, 1.6)
    s += rect(458, 168, 24, 28, "#fff", INK, 1.4, 3) + text(490, 186, "R2", 9, INK, "start", "bold")
    s += line(470, 196, 470, 250, INK, 1.6) + line(420, 250, 520, 250, INK, 1.4) + text(524, 254, "GND", 8.5, INK, "start")
    # відвід -> «−»
    s += circle(470, 150, 3, INK, INK)
    s += line(470, 150, 208, 168, BLUE, 1.4, "4 3")
    s += rect(230, 268, 300, 36, "#f6f8fb", "#c9d3dc", 1.2, 6)
    s += text(380, 290, "Vout = Vref · (1 + R1/R2)", 13, INK, "middle", "bold")
    save("fig-13-11-3-noninv-disguise.svg", s)


def fig1311_heat():
    W, H = 700, 330
    s = header(W, H)
    s += text(W / 2, 28, "«Лінійний» = клапан гасить надлишок у тепло", 15.5, INK, "middle", "bold")
    bx, by, bw = 150, 70, 90
    full = 210
    s += rect(bx, by, bw, full, "#eef2f7", "#9bb0c2", 1.4, 4)
    vout_h = 120
    s += rect(bx, by + (full - vout_h), bw, vout_h, LGRN, GREEN, 1.6, 0)
    s += text(bx + bw / 2, by + full - vout_h / 2, "Vout", 12, GREEN, "middle", "bold")
    s += rect(bx, by, bw, full - vout_h, LRED, RED, 1.6, 0)
    s += text(bx + bw / 2, by + (full - vout_h) / 2 - 8, "Vin − Vout", 10, RED, "middle", "bold")
    s += text(bx + bw / 2, by + (full - vout_h) / 2 + 8, "падає на клапані", 8.5, RED, "middle")
    s += text(bx + bw / 2, by - 8, "Vin", 11, RED, "middle", "bold")
    s += rect(330, 96, 330, 70, LRED, "#d8a0a0", 1.3, 6)
    s += text(495, 120, "втрати = (Vin − Vout) · I → тепло", 11, RED, "middle", "bold")
    s += text(495, 144, "ККД ≈ Vout / Vin — менший за більшої різниці", 10, INK, "middle")
    s += rect(330, 182, 330, 76, "#eef6ef", GREEN, 1.3, 6)
    s += text(495, 204, "«dropout» — найменша різниця Vin−Vout,", 10, INK, "middle", "bold")
    s += text(495, 224, "за якої LDO ще тримає вихід", 10, INK, "middle")
    s += text(495, 244, "(LDO = Low DropOut — мала)", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Простий і тихий, але гарячий: усю різницю напруг помножену на струм LDO віддає теплом.",
              9, GREY, "middle", style="italic")
    save("fig-13-11-4-heat.svg", s)


def fig1311_reference():
    W, H = 640, 312
    s = header(W, H)
    s += text(W / 2, 28, "Опорна напруга: незмінний еталон, з яким усе звіряють", 14, INK, "middle", "bold")
    ox, oy, pw, ph = 90, 250, 430, 180
    s += _axes(ox, oy, pw, ph, "температура", "Vref")
    yb = oy - ph * 0.5
    s += line(ox, yb, ox + pw, yb, GREEN, 2.8)
    s += text(ox + pw - 6, yb - 10, "бандгап ≈ 1.2 В (рівно)", 10, GREEN, "end", "bold")
    s += _poly([(ox, oy - ph * 0.78), (ox + pw, oy - ph * 0.22)], GREY, 2.2, "5 4")
    s += text(ox + pw - 6, oy - ph * 0.22 + 14, "наївне джерело — пливе", 9.5, GREY, "end")
    s += text(W / 2, H - 26, "«Бандгап» хитро складає два протилежні температурні нахили в один рівний — стала напруга.",
              9.5, INK, "middle")
    s += text(W / 2, H - 10, "Без сталого еталона нічого було б тримати: уся точність LDO міряється від нього.",
              9, GREY, "middle", style="italic")
    save("fig-13-11-5-reference.svg", s)


def fig1311_known_blocks():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Ти вже знаєш усі деталі LDO", 16, INK, "middle", "bold")
    parts = [
        ("прохідний транзистор", "§2.6 / §2.7", LBLUE),
        ("операційний підсилювач", "§2.8.1–2.8.4", "#fff3e0"),
        ("від'ємний зв'язок", "§2.8.2", LGRN),
        ("опорна напруга (зенер/бандгап)", "§2.5", "#f3e9f3"),
        ("дільник напруги", "§1.3", "#e9f3f3"),
    ]
    y0 = 78
    for i, (name, ref, col) in enumerate(parts):
        y = y0 + i * 44
        s += rect(120, y, 300, 36, col, "#9bb0c2", 1.4, 6) + text(270, y + 22, name, 10.5, INK, "middle", "bold")
        s += text(440, y + 22, ref, 10, GREEN, "start", "bold")
    s += text(W / 2, H - 14, "Стабілізатор — не новий прилад, а знайомі цеглинки в одній петлі зворотного зв'язку.",
              9.5, GREY, "middle", style="italic")
    save("fig-13-11-6-known-blocks.svg", s)


# ── 🔌 вставка до 2.8.11: модуль стабілізатора (Рис. 2.8.11c.k) ──────────────
def fig1311c_module():
    W, H = 700, 338
    s = header(W, H)
    s += text(W / 2, 28, "Плата стабілізатора: чип + два конденсатори", 15, INK, "middle", "bold")
    gndY = 274
    s += rect(286, 106, 128, 98, "#f4dcc4", COPP, 1.3, 8)
    s += text(350, 198, "мідь — тепловідвід", 8, COPP, "middle")
    s += rect(300, 120, 100, 60, "#eef2f7", "#7f93a8", 1.8, 6)
    s += text(350, 144, "LDO-чип", 11, INK, "middle", "bold") + text(350, 162, "(увесь §2.8.11)", 8.5, GREY, "middle")
    s += line(210, 150, 300, 150, RED, 2) + text(204, 154, "Vin", 10, RED, "end", "bold") + text(296, 140, "IN", 8, RED, "end")
    s += line(400, 150, 540, 150, GREEN, 2) + text(548, 154, "Vout", 10, GREEN, "start", "bold") + text(404, 140, "OUT", 8, GREEN, "start")
    s += line(350, 180, 350, gndY, INK, 1.6)
    s += line(180, gndY, 560, gndY, INK, 1.6) + text(174, gndY + 4, "GND", 9, INK, "end")
    # вхідний конденсатор
    s += circle(250, 150, 3, INK, INK) + line(250, 150, 250, 214, INK, 1.6)
    s += line(238, 214, 262, 214, INK, 2.6) + line(238, 222, 262, 222, INK, 2.6) + line(250, 222, 250, gndY, INK, 1.6)
    s += text(232, 202, "Cвх", 8.5, INK, "end", "bold")
    # вихідний конденсатор
    s += circle(470, 150, 3, INK, INK) + line(470, 150, 470, 214, INK, 1.6)
    s += line(458, 214, 482, 214, INK, 2.6) + line(458, 222, 482, 222, INK, 2.6) + line(470, 222, 470, gndY, INK, 1.6)
    s += text(488, 204, "Cвих", 8.5, RED, "start", "bold") + text(488, 218, "(стійкість!)", 7.5, RED, "start", "bold")
    s += text(W / 2, H - 12, "Усередині — повний LDO з теми. Зовні лишаються вхідний і вихідний конденсатори та мідь під чипом.",
              9, GREY, "middle", style="italic")
    save("fig-13-11c-1-module.svg", s)


def fig1311c_fixed_vs_adj():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 26, "Два класи: фіксований і регульований", 15, INK, "middle", "bold")
    s += _frame(30, 50, 320, 214, "фіксований (AMS1117-клас)")
    s += rect(110, 104, 160, 64, "#eef2f7", "#7f93a8", 1.6, 6)
    s += text(190, 130, "вихід 3.3 чи 5 В", 10.5, INK, "middle", "bold") + text(190, 150, "дільник — усередині", 9, GREY, "middle")
    s += text(190, 196, "3 ноги: IN · GND · OUT", 10, INK, "middle", "bold")
    s += text(190, 218, "увімкнув — і працює", 9, GREY, "middle")
    s += text(190, 244, "та dropout ~1.1 В, споживає ~5 мА", 8.5, RED, "middle")
    s += _frame(370, 50, 320, 214, "регульований (LM317-клас)")
    s += rect(420, 100, 130, 52, "#eef2f7", "#7f93a8", 1.6, 6) + text(485, 130, "ADJ-чип", 10.5, INK, "middle", "bold")
    s += line(550, 126, 590, 126, GREEN, 2) + text(596, 130, "Vout", 9, GREEN, "start", "bold")
    s += line(590, 126, 590, 150, INK, 1.5) + rect(578, 150, 24, 24, "#fff", INK, 1.4, 3) + text(610, 166, "R1", 8.5, INK, "start", "bold")
    s += line(590, 174, 590, 188, INK, 1.5) + circle(590, 188, 3, INK, INK) + line(485, 188, 590, 188, INK, 1.4) + line(485, 152, 485, 188, INK, 1.4)
    s += text(520, 184, "ADJ", 8, INK, "middle")
    s += rect(578, 192, 24, 24, "#fff", INK, 1.4, 3) + text(610, 208, "R2", 8.5, INK, "start", "bold")
    s += line(590, 216, 590, 236, INK, 1.5) + text(590, 250, "GND", 8, INK, "middle")
    s += text(500, 234, "Vout задають два резистори", 9.5, INK, "middle", "bold")
    save("fig-13-11c-2-fixed-vs-adj.svg", s)


# ── 🧮 вставка до 2.8.2: формула зворотного зв'язку (Рис. 2.8.2m.k) ──────────
def fig132m_loop():
    W, H = 700, 322
    s = header(W, H)
    s += text(W / 2, 28, "Формула зворотного зв'язку: G = A / (1 + A·β)", 15.5, INK, "middle", "bold")
    s += text(60, 124, "Vin", 11, INK, "end", "bold") + arrow(64, 120, 118, 120, INK, 2)
    s += circle(140, 120, 20, "#fff", INK, 2) + text(140, 126, "Σ", 14, INK, "middle", "bold")
    s += text(126, 102, "+", 11, RED, "middle", "bold") + text(126, 150, "−", 11, BLUE, "middle", "bold")
    s += arrow(160, 120, 230, 120, INK, 2)
    s += rect(230, 96, 90, 48, LBLUE, BLUE, 1.6, 6) + text(275, 126, "A", 16, INK, "middle", "bold")
    s += text(275, 86, "сире підсилення", 8.5, GREY, "middle")
    s += arrow(320, 120, 470, 120, INK, 2) + circle(420, 120, 3, INK, INK) + text(478, 124, "Vout", 11, GREEN, "start", "bold")
    s += line(420, 120, 420, 220, INK, 1.6) + arrow(420, 220, 322, 220, INK, 2)
    s += rect(230, 196, 90, 48, "#fff3e0", COPP, 1.6, 6) + text(275, 226, "β", 16, INK, "middle", "bold")
    s += text(275, 258, "частка звороту", 8.5, GREY, "middle")
    s += line(230, 220, 140, 220, INK, 1.6) + arrow(140, 220, 140, 142, INK, 2)
    s += rect(478, 168, 204, 98, "#f6f8fb", "#c9d3dc", 1.3, 8)
    s += text(580, 196, "G = A / (1 + A·β)", 14, INK, "middle", "bold")
    s += text(580, 226, "коли A·β ≫ 1:", 10, INK, "middle")
    s += text(580, 250, "G ≈ 1 / β", 15, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Велетенське A зникає з результату — лишається 1/β, задане самим зворотним зв'язком.",
              9, GREY, "middle", style="italic")
    save("fig-13-2m-1-loop.svg", s)


def fig132m_desens():
    W, H = 660, 358
    s = header(W, H)
    s += text(W / 2, 28, "Чому точно: велике A на «полиці» майже не впливає", 14.5, INK, "middle", "bold")
    ox, oy, pw, ph = 92, 298, 470, 244
    s += _axes(ox, oy, pw, ph, "A (сире підсилення)", "G")
    beta, Amax = 0.1, 1000.0
    target = 1 / beta
    pts = []
    for j in range(0, 201):
        A = Amax * j / 200.0
        G = A / (1 + A * beta)
        pts.append((ox + pw * (A / Amax), oy - ph * 0.9 * (G / target)))
    s += _poly(pts, BLUE, 2.8)
    ya = oy - ph * 0.9
    s += line(ox, ya, ox + pw, ya, GREEN, 1.6, "6 4") + text(ox + pw - 6, ya - 8, "G = 1/β (ціль)", 10, GREEN, "end", "bold")
    for A in (500, 1000):
        G = A / (1 + A * beta)
        s += circle(ox + pw * (A / Amax), oy - ph * 0.9 * (G / target), 3.5, RED, RED)
    s += text(ox + pw * 0.66, oy - ph * 0.56, "A удвічі більше —", 9.5, INK, "middle")
    s += text(ox + pw * 0.66, oy - ph * 0.56 + 15, "G майже те саме", 9.5, RED, "middle", "bold")
    s += text(W / 2, H - 12, "На «полиці» (велике A·β) подвоєння чи провал A зрушують G на частки відсотка. Звідси й точність.",
              9, GREY, "middle", style="italic")
    save("fig-13-2m-2-desens.svg", s)


# ── 🧮 вставка до 2.8.8: розрахунок порогів гістерезису (Рис. 2.8.8m.k) ──────
def fig138m_schmitt():
    W, H = 700, 358
    s = header(W, H)
    s += text(W / 2, 26, "Неінвертуючий тригер Шмітта: два пороги з двох резисторів", 14, INK, "middle", "bold")
    s += _opamp_sym(330, 170, 90, 74)
    s += text(38, 196, "Vin", 10, INK, "end", "bold") + line(42, 192, 96, 192, INK, 2)
    s += rect(96, 180, 44, 24, "#fff", INK, 1.5, 3) + text(118, 196, "R1", 9, INK, "middle", "bold")
    s += line(140, 192, 250, 192, INK, 2) + circle(250, 192, 3, INK, INK)
    s += line(250, 192, 285, 189, INK, 2) + text(250, 210, "вузол «+»", 8.5, INK, "middle")
    s += line(375, 170, 470, 170, INK, 2) + circle(470, 170, 3, INK, INK) + text(478, 174, "Vout", 11, GREEN, "start", "bold")
    s += line(470, 170, 470, 252, INK, 1.6) + line(250, 252, 470, 252, INK, 1.6) + line(250, 192, 250, 252, INK, 1.6)
    s += rect(338, 240, 44, 24, "#fff", INK, 1.5, 3) + text(360, 256, "R2", 9, INK, "middle", "bold")
    s += line(285, 151, 238, 151, BLUE, 2) + text(232, 155, "Vref", 10, BLUE, "end", "bold")
    s += rect(478, 206, 204, 122, "#f6f8fb", "#c9d3dc", 1.3, 8)
    s += text(580, 230, "ширина зазору:", 10, INK, "middle", "bold")
    s += text(580, 254, "ΔV = (Voh−Vol)·R1/R2", 11.5, RED, "middle", "bold")
    s += text(580, 284, "центр задає Vref", 10, INK, "middle")
    s += text(580, 306, "(опора на «−»)", 9, GREY, "middle")
    s += text(W / 2, H - 10, "Частку виходу повертають на «+» крізь R2, а R1 веде туди сигнал. Відношення R1/R2 і задає зазор.",
              9, GREY, "middle", style="italic")
    save("fig-13-8m-1-schmitt.svg", s)


def fig138m_band():
    W, H = 680, 326
    s = header(W, H)
    s += text(W / 2, 26, "Зазор і центр на прикладі: VL = 2 В, VH = 3 В", 15, INK, "middle", "bold")
    ax = 150

    def yV(v):
        return 250 - 36 * v
    s += line(ax, 258, ax, 56, INK, 2) + text(ax, 48, "Vin", 10, INK, "middle", "bold")
    for v in range(0, 6):
        s += line(ax - 5, yV(v), ax + 5, yV(v), INK, 1.4) + text(ax - 12, yV(v) + 4, f"{v}", 9, INK, "end")
    s += rect(ax + 10, yV(3), 250, yV(2) - yV(3), "#eef6ef", GREEN, 1.4, 4)
    s += line(ax, yV(3), ax + 270, yV(3), RED, 1.6, "5 4") + text(ax + 276, yV(3) + 4, "VH = 3 В (угору)", 9.5, RED, "start", "bold")
    s += line(ax, yV(2), ax + 270, yV(2), BLUE, 1.6, "5 4") + text(ax + 276, yV(2) + 4, "VL = 2 В (униз)", 9.5, BLUE, "start", "bold")
    s += line(ax, yV(2.5), ax + 150, yV(2.5), GREY, 1.2, "2 3") + text(ax + 156, yV(2.5) + 3, "центр 2.5 = Vref", 8.5, GREY, "start")
    s += text(ax + 135, (yV(2) + yV(3)) / 2 + 4, "ΔV = 1 В", 9.5, GREEN, "middle", "bold")
    s += rect(300, 214, 360, 96, "#f6f8fb", "#c9d3dc", 1.2, 8)
    s += text(480, 236, "як дібрати резистори:", 10, INK, "middle", "bold")
    s += text(480, 258, "1) ΔV > шуму (тут 1 В)", 9.5, INK, "middle")
    s += text(480, 278, "2) R1/R2 = ΔV/(Voh−Vol) = 1/5 = 0.2", 9.5, INK, "middle")
    s += text(480, 298, "3) Vref = центр = 2.5 В", 9.5, INK, "middle")
    save("fig-13-8m-2-band.svg", s)


# ── 🧮 вставка до 2.8.9: GBW і slew rate (Рис. 2.8.9m.k) ─────────────────────
def fig139m_gbw():
    W, H = 700, 380
    s = header(W, H)
    s += text(W / 2, 28, "GBW: смуга меншає з підсиленням (GBW = G·f)", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 92, 320, 536, 252
    s += arrow(ox, oy, ox, oy - ph - 12, INK, 2) + arrow(ox, oy, ox + pw + 12, oy, INK, 2)
    s += text(ox + pw + 16, oy + 4, "частота (лог)", 10.5, INK, "start", "bold")
    s += text(ox + 2, oy - ph - 20, "підсилення (лог)", 10.5, INK, "middle", "bold")
    decs = ["1", "10", "100", "1к", "10к", "100к", "1М"]
    for i, lab in enumerate(decs):
        x = ox + pw * i / 6
        s += line(x, oy, x, oy + 5, INK, 1.2) + text(x, oy + 18, lab, 8.5, INK, "middle")
    A_top, A_bot = 0.92, 0.08

    def Afrac(d):
        return A_top - (d / 6.0) * (A_top - A_bot)
    s += _poly([(ox, oy - ph * A_top), (ox + pw, oy - ph * A_bot)], GREY, 2.4)
    s += text(ox + pw * 0.30, oy - ph * 0.74, "розімкнене A (−20 дБ/дек)", 9, GREY, "start", style="italic")
    for dec, lab in [(3, "×1000"), (4, "×100"), (5, "×10")]:
        y = oy - ph * Afrac(dec)
        xc = ox + pw * dec / 6
        s += _poly([(ox, y), (xc, y)], BLUE, 2.6)
        s += circle(xc, y, 3.5, RED, RED) + text(ox + 8, y - 6, lab, 9.5, BLUE, "start", "bold")
        s += line(xc, y, xc, oy, RED, 1.1, "3 3")
    s += text(ox + pw * 5 / 6, oy - ph * Afrac(5) - 14, "смуга = GBW/G", 9, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Що більше підсилення, то нижча частота зламу: смуга = GBW/G. Добуток підсилення на смугу сталий.",
              9, GREY, "middle", style="italic")
    save("fig-13-9m-1-gbw.svg", s)


def fig139m_slew():
    W, H = 700, 318
    s = header(W, H)
    s += text(W / 2, 26, "Швидкість наростання: великий швидкий сигнал стає трикутником", 13.5, INK, "middle", "bold")
    ox, pw, midY, amp = 60, 470, 168, 78
    s += line(ox, midY, ox + pw, midY, FAINT, 1.2)
    s += _sine(ox, midY, pw, amp, 2, GREY, 1.8)
    pts, period = [], pw / 2
    for c in range(2):
        base = ox + c * period
        pts += [(base, midY), (base + period * 0.25, midY - amp), (base + period * 0.75, midY + amp)]
    pts.append((ox + pw, midY))
    s += _poly(pts, RED, 2.8)
    s += text(ox + pw * 0.5, 70, "хочемо синус (нахил 2π·f·A)", 9.5, GREY, "middle", "bold")
    s += text(ox + pw * 0.5, 262, "виходить трикутник (нахил = SR)", 9.5, RED, "middle", "bold")
    s += rect(548, 110, 138, 110, "#f6f8fb", "#c9d3dc", 1.2, 8)
    s += text(617, 134, "межа повної", 9.5, INK, "middle", "bold")
    s += text(617, 150, "потужності:", 9.5, INK, "middle", "bold")
    s += text(617, 176, "f_max =", 10.5, INK, "middle")
    s += text(617, 196, "SR / (2π·A)", 11, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Коли крутість сигналу 2π·f·A переростає SR, вихід не встигає й рампить прямими — синус ламається в трикутник.",
              8.8, GREY, "middle", style="italic")
    save("fig-13-9m-2-slew.svg", s)


# ── 🧮 вставка до 2.8.11: розсіювання LDO (Рис. 2.8.11m.k) ───────────────────
def fig1311m_efficiency():
    W, H = 660, 350
    s = header(W, H)
    s += text(W / 2, 28, "ККД лінійного: η ≈ Vout/Vin падає з різницею", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 92, 292, 476, 232
    s += _axes(ox, oy, pw, ph, "Vin (В), Vout = 3.3 В", "ККД")
    Vout, Vmin, Vmax = 3.3, 3.3, 15.0
    pts = []
    for j in range(0, 201):
        Vin = Vmin + (Vmax - Vmin) * j / 200
        pts.append((ox + pw * (Vin - Vmin) / (Vmax - Vmin), oy - ph * 0.9 * (Vout / Vin)))
    s += _poly(pts, BLUE, 2.8)
    s += line(ox, oy - ph * 0.9, ox + pw, oy - ph * 0.9, FAINT, 1.2) + text(ox - 6, oy - ph * 0.9 + 4, "100%", 8, GREY, "end")
    for Vin, lab in [(3.6, "92%"), (5, "66%"), (12, "27%")]:
        x = ox + pw * (Vin - Vmin) / (Vmax - Vmin)
        y = oy - ph * 0.9 * (Vout / Vin)
        s += circle(x, y, 3.5, RED, RED) + text(x, y - 11, f"{Vin} В → {lab}", 8.5, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Корисно лише Vout, решта (Vin−Vout) — у тепло. Що більший вхід, то гірший ККД.",
              9, GREY, "middle", style="italic")
    save("fig-13-11m-1-efficiency.svg", s)


def fig1311m_when():
    W, H = 660, 350
    s = header(W, H)
    s += text(W / 2, 28, "Скільки тепла — і коли лінійний недоцільний", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 92, 292, 476, 232
    s += _axes(ox, oy, pw, ph, "Vin (В) · Vout=3.3 · I=0.5 А", "P (Вт)")
    Vout, I, Vmin, Vmax, Pax = 3.3, 0.5, 3.3, 15.0, 6.0
    pts = []
    for j in range(0, 201):
        Vin = Vmin + (Vmax - Vmin) * j / 200
        P = (Vin - Vout) * I
        pts.append((ox + pw * (Vin - Vmin) / (Vmax - Vmin), oy - ph * 0.9 * min(P, Pax) / Pax))
    s += _poly(pts, RED, 2.8)
    Plim = 1.0
    ylim = oy - ph * 0.9 * Plim / Pax
    s += line(ox, ylim, ox + pw, ylim, GREEN, 1.6, "6 4") + text(ox + pw - 6, ylim - 8, "межа корпусу без радіатора ≈1 Вт", 9, GREEN, "end", "bold")
    Vcross = Vout + Plim / I
    xc = ox + pw * (Vcross - Vmin) / (Vmax - Vmin)
    s += line(xc, oy, xc, ylim, GREY, 1.2, "3 3") + circle(xc, ylim, 3.5, RED, RED)
    s += text(xc, oy + 18, f"~{Vcross:.0f} В", 9, RED, "middle", "bold")
    s += text(ox + pw * 0.16, oy - ph * 0.62, "лінійний ОК", 10, GREEN, "middle", "bold")
    s += text(ox + pw * 0.74, oy - ph * 0.5, "треба радіатор", 10, RED, "middle", "bold")
    s += text(ox + pw * 0.74, oy - ph * 0.5 + 16, "або імпульсний", 10, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Вище за межу корпусу лінійний пече: або великий радіатор, або перехід на імпульсний стабілізатор.",
              9, GREY, "middle", style="italic")
    save("fig-13-11m-2-when.svg", s)


# ── 🔌 вставка до 2.8.5: буфер для високоомного джерела (Рис. 2.8.5c.k) ──────
def fig135c_problem():
    W, H = 700, 350
    s = header(W, H)
    s += text(W / 2, 28, "Високоомне джерело й АЦП: дільник не встигає зарядити", 14, INK, "middle", "bold")
    vx = 130
    s += line(vx, 70, vx, 100, RED, 2) + text(vx, 62, "+Vbat", 10, RED, "middle", "bold")
    s += rect(vx - 13, 100, 26, 34, "#fff", INK, 1.5, 3) + text(vx + 26, 120, "R1 1М", 9, INK, "start", "bold")
    s += line(vx, 134, vx, 160, INK, 2) + circle(vx, 160, 3, INK, INK)
    s += rect(vx - 13, 160, 26, 34, "#fff", INK, 1.5, 3) + text(vx + 26, 180, "R2 1М", 9, INK, "start", "bold")
    s += line(vx, 194, vx, 226, INK, 1.6) + line(vx - 26, 226, vx + 26, 226, INK, 1.4) + text(vx, 242, "GND", 8.5, INK, "middle")
    s += text(vx, 274, "опір джерела ≈ 500 кОм", 9, RED, "middle", "bold")
    s += arrow(vx, 160, 358, 160, INK, 2)
    s += _frame(360, 92, 300, 168, "вхід АЦП")
    s += line(378, 160, 426, 160, INK, 2)
    s += circle(426, 160, 3, INK, INK) + line(426, 160, 458, 144, INK, 2) + circle(464, 160, 3, INK, INK) + text(446, 132, "вибірка", 8, INK, "middle")
    s += line(464, 160, 512, 160, INK, 2)
    s += line(512, 160, 512, 188, INK, 1.6)
    s += line(500, 188, 524, 188, INK, 2.4) + line(500, 196, 524, 196, INK, 2.4) + text(532, 196, "Cвиб", 8.5, INK, "start", "bold")
    s += line(512, 196, 512, 226, INK, 1.6) + text(512, 242, "GND", 8, INK, "middle")
    s += text(512, 120, "зарядити за мить", 8.5, INK, "middle")
    s += text(W / 2, H - 14, "Через 500 кОм конденсатор вибірки заряджається надто повільно — АЦП зчитує ЗАНИЖЕНЕ число.",
              9, GREY, "middle", style="italic")
    save("fig-13-5c-1-problem.svg", s)


def fig135c_buffer_fix():
    W, H = 700, 342
    s = header(W, H)
    s += text(W / 2, 28, "Буфер між дільником і АЦП: міряємо без просідання", 14, INK, "middle", "bold")
    vx = 110
    s += line(vx, 64, vx, 92, RED, 2) + text(vx, 56, "+Vbat", 9.5, RED, "middle", "bold")
    s += rect(vx - 12, 92, 24, 30, "#fff", INK, 1.4, 3) + text(vx + 24, 110, "1М", 8.5, INK, "start", "bold")
    s += line(vx, 122, vx, 150, INK, 2) + circle(vx, 150, 3, INK, INK)
    s += rect(vx - 12, 150, 24, 30, "#fff", INK, 1.4, 3) + text(vx + 24, 168, "1М", 8.5, INK, "start", "bold")
    s += line(vx, 180, vx, 208, INK, 1.6) + line(vx - 22, 208, vx + 22, 208, INK, 1.4) + text(vx, 224, "GND", 8, INK, "middle")
    s += line(vx, 150, 250, 150, INK, 2) + line(250, 150, 260, 166, INK, 2)
    s += _opamp_sym(300, 150, 80, 66)
    s += line(340, 150, 362, 150, INK, 2) + circle(362, 150, 3, INK, INK)
    s += line(362, 150, 362, 110, INK, 1.6) + line(362, 110, 262, 110, INK, 1.6) + line(262, 110, 262, 134, INK, 1.6)
    s += arrow(362, 150, 470, 150, GREEN, 2.2) + text(416, 138, "жорсткий вихід", 8.5, GREEN, "middle", "bold")
    s += rect(470, 122, 156, 58, "#eef2f7", "#9bb0c2", 1.5, 6) + text(548, 147, "вхід АЦП", 10, INK, "middle", "bold") + text(548, 165, "Cвиб — миттєво", 8, GREY, "middle")
    s += rect(60, 252, 600, 74, "#fff7e6", COPP, 1.3, 6)
    s += text(360, 274, "граблі: вхідний струм буфера Ib на опорі джерела дає похибку Verr = Ib · Rдж", 9.5, INK, "middle", "bold")
    s += text(360, 294, "для дуже високого опору (давачі, гігаоми) бери ОП із ПОЛЬОВИМИ входами — Ib мізерний", 9.5, INK, "middle")
    s += text(360, 313, "(той самий TL072-клас із §2.8.9)", 8.5, GREY, "middle")
    save("fig-13-5c-2-buffer-fix.svg", s)


# ── 🔌 вставка до 2.8.7: компаратори-мікросхеми (Рис. 2.8.7c.k) ──────────────
def fig137c_opencoll():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 28, "Відкритий колектор: сам тягне лише до 0, «1» дає підтяжка", 14, INK, "middle", "bold")
    s += _opamp_sym(190, 172, 88, 74)
    s += line(146, 154, 110, 154, BLUE, 2) + text(104, 158, "−", 11, BLUE, "end", "bold")
    s += line(146, 190, 110, 190, RED, 2) + text(104, 194, "+", 11, RED, "end", "bold")
    s += text(160, 132, "компаратор", 9, GREY, "middle")
    s += line(234, 172, 330, 172, INK, 2) + circle(330, 172, 3, INK, INK) + text(330, 154, "вихід", 9, INK, "middle", "bold")
    s += line(330, 172, 330, 118, INK, 1.6)
    s += rect(317, 86, 26, 32, "#fff", INK, 1.5, 3) + text(352, 106, "Rпідт", 9.5, INK, "start", "bold")
    s += line(330, 86, 330, 62, RED, 2) + text(330, 54, "Vpull — обираєш сам (3.3 / 5 В)", 9.5, RED, "middle", "bold")
    s += arrow(330, 190, 330, 250, BLUE, 2.4) + text(345, 222, "тягне до 0", 9, BLUE, "start", "bold")
    s += line(310, 250, 350, 250, INK, 1.4) + text(330, 266, "GND", 8.5, INK, "middle")
    s += line(330, 172, 432, 172, INK, 2) + arrow(432, 172, 468, 172, GREEN, 2)
    s += rect(468, 148, 132, 48, LBLUE, "#9bb0c2", 1.4, 6) + text(534, 176, "МК (вхід)", 10, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Вихід лише ПРИТЯГУЄ лінію до нуля; «1» дає підтяжний резистор до обраної напруги — звідси й зсув рівня.",
              9, GREY, "middle", style="italic")
    save("fig-13-7c-1-opencoll.svg", s)


def fig137c_patterns():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "Два дарунки відкритого колектора", 15, INK, "middle", "bold")
    s += _frame(28, 50, 320, 240, "зсув рівня")
    s += _opamp_sym(108, 152, 60, 52)
    s += text(108, 112, "живлення 5 В", 8.5, GREY, "middle")
    s += line(138, 152, 190, 152, INK, 2) + circle(190, 152, 3, INK, INK)
    s += line(190, 152, 190, 112, INK, 1.4) + rect(178, 86, 24, 26, "#fff", INK, 1.4, 3) + text(208, 102, "Rпідт", 8.5, INK, "start", "bold")
    s += line(190, 86, 190, 68, RED, 2) + text(190, 62, "до 3.3 В", 9, RED, "middle", "bold")
    s += arrow(190, 152, 288, 152, GREEN, 2) + rect(288, 132, 52, 40, LBLUE, "#9bb0c2", 1.3, 5) + text(314, 156, "МК 3.3В", 8.5, INK, "middle", "bold")
    s += text(186, 220, "компаратор на 5 В, а вихід — 0…3.3 В", 8.5, INK, "middle")
    s += text(186, 238, "→ безпечно для 3.3-В входу", 8.5, GREEN, "middle", "bold")
    s += _frame(372, 50, 320, 240, "монтажне-АБО (wired-OR)")
    railx = 600
    s += line(railx, 80, railx, 244, INK, 1.8)
    s += rect(railx - 13, 80, 26, 26, "#fff", INK, 1.4, 3) + text(railx + 30, 96, "Rпідт", 8.5, INK, "start", "bold")
    s += line(railx, 62, railx, 80, RED, 2) + text(railx, 56, "Vpull", 8.5, RED, "middle", "bold")
    for i, y in enumerate((124, 172, 220)):
        s += _opamp_sym(444, y, 44, 36)
        s += line(466, y, railx, y, INK, 1.6) + circle(railx, y, 2.5, INK, INK)
        s += text(416, y + 4, f"к{i + 1}", 8, GREY, "end")
    s += text(534, 262, "хоч один тягне до 0 → лінія = 0", 8.8, INK, "middle", "bold")
    save("fig-13-7c-2-patterns.svg", s)


# ── 🔌 вставка до 2.8.9: rail-to-rail і single-supply (Рис. 2.8.9c.k) ────────
def fig139c_swing():
    W, H = 700, 352
    s = header(W, H)
    s += text(W / 2, 28, "На 3.3 В кожен вольт на вагу: корисний розмах виходу", 14.5, INK, "middle", "bold")
    y0, top = 300, 72

    def yV(v):
        return y0 - (y0 - top) * v / 3.3
    s += line(96, y0, 640, y0, INK, 1.4) + text(90, y0 + 4, "0 (GND)", 8.5, INK, "end")
    s += line(96, top, 640, top, RED, 1.4, "5 4") + text(90, top + 4, "3.3 (Vcc)", 8.5, RED, "end")
    bars = [
        ("звичайний", "(втрачає краї)", 210, 1.2, 2.0, "#fdeeee", RED),
        ("LM358-клас", "(дістає низ)", 370, 0.02, 1.8, "#fff3e0", SUN),
        ("RRIO", "(майже все)", 530, 0.05, 3.25, "#eef6ef", GREEN),
    ]
    for lab, sub, x, lo, hi, fill, col in bars:
        s += rect(x - 42, yV(hi), 84, yV(lo) - yV(hi), fill, col, 1.8, 4)
        s += text(x, yV(hi) - 7, f"{hi:.2f} В", 8.5, col, "middle", "bold")
        s += text(x, yV(lo) + 14, f"{lo:.2f} В", 8.5, col, "middle")
        s += text(x, y0 + 22, lab, 9.5, INK, "middle", "bold") + text(x, y0 + 37, sub, 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Звичайний ОП губить по вольту з кожного краю — на 3.3 В лишається кволенька смужка. RRIO дає майже всі 3.3 В.",
              9, GREY, "middle", style="italic")
    save("fig-13-9c-1-swing.svg", s)


def fig139c_single_supply():
    W, H = 700, 330
    s = header(W, H)
    s += text(W / 2, 28, "Однополярне живлення: змінний сигнал зміщують у середину", 14, INK, "middle", "bold")
    s += _frame(28, 52, 320, 226, "напряму — нижні півхвилі зрізано")
    baseY = 168
    s += line(60, baseY, 322, baseY, FAINT, 1.2) + text(54, baseY + 4, "0", 8, INK, "end")
    s += _clip_sine(60, baseY, 262, 66, 2, RED, lo=0.0, hi=1.0)
    s += text(190, 248, "нижче нуля ОП не може — зріз", 9, RED, "middle", "bold")
    s += _frame(372, 52, 320, 226, "зсув у Vcc/2 — уся хвиля вміщається")
    midR = 158
    s += line(404, midR, 666, midR, FAINT, 1.2) + text(398, midR + 4, "Vcc/2", 8, GREY, "end")
    s += _sine(404, midR, 258, 56, 2, GREEN, 2.4)
    s += text(534, 248, "сигнал гойдається довкола 1.65 В", 9, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Без мінусової шини сигнал зміщують до середини живлення (дільник + буфер) — тоді влазить уся хвиля.",
              9, GREY, "middle", style="italic")
    save("fig-13-9c-2-single-supply.svg", s)


# ── ⚙️ вставка до 2.8.6: зміщення й масштабування (Рис. 2.8.6a.k) ────────────
def fig136a_line():
    W, H = 640, 382
    s = header(W, H)
    s += text(W / 2, 28, "Будь-яке перетворення — пряма: Vout = m·Vin + b", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 112, 322, 436, 252

    def xV(v):
        return ox + pw * (v + 5) / 10

    def yV(v):
        return oy - ph * 0.86 * v / 3.3
    s += arrow(ox, oy, ox, oy - ph - 12, INK, 2) + text(ox + 4, oy - ph - 16, "Vout (В)", 10.5, INK, "start", "bold")
    s += arrow(ox, oy, ox + pw + 12, oy, INK, 2) + text(ox + pw + 16, oy + 4, "Vin (В)", 10.5, INK, "start", "bold")
    for v in (-5, 0, 5):
        lab = "0" if v == 0 else f"{v:+d}"
        s += line(xV(v), oy, xV(v), oy + 5, INK, 1.2) + text(xV(v), oy + 18, lab, 9, INK, "middle")
    for v in (3.3, 1.65):
        s += line(ox - 5, yV(v), ox + 5, yV(v), INK, 1.2) + text(ox - 10, yV(v) + 4, f"{v}", 9, INK, "end")
    s += _poly([(xV(-5), yV(0)), (xV(5), yV(3.3))], BLUE, 3)
    s += circle(xV(-5), yV(0), 4, RED, RED) + text(xV(-5) + 4, yV(0) + 20, "−5 → 0", 8.5, RED, "start", "bold")
    s += circle(xV(5), yV(3.3), 4, RED, RED) + text(xV(5) - 6, yV(3.3) - 10, "+5 → 3.3", 8.5, RED, "end", "bold")
    s += circle(xV(0), yV(1.65), 3, GREEN, GREEN) + line(ox, yV(1.65), xV(0), yV(1.65), GREEN, 1.2, "3 3")
    s += text(xV(0) + 8, yV(1.65) - 6, "зсув b = 1.65 В", 8.5, GREEN, "start", "bold")
    s += rect(xV(-4.6), yV(3.05), 156, 28, "#f6f8fb", "#c9d3dc", 1.2, 6) + text(xV(-4.6) + 78, yV(3.05) + 18, "Vout = 0.33·Vin + 1.65", 10.5, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Два кінці задають пряму: її нахил — це масштаб m, а зсув по вертикалі — b.",
              9, GREY, "middle", style="italic")
    save("fig-13-6a-1-line.svg", s)


def fig136a_circuit():
    W, H = 680, 330
    s = header(W, H)
    s += text(W / 2, 28, "Один ОП: масштаб задають резистори, зсув — опора", 14.5, INK, "middle", "bold")
    s += _opamp_sym(346, 168, 92, 78)
    # «−» вузол (опора Vref + зворотний зв'язок)
    s += line(300, 150, 250, 150, INK, 2) + circle(250, 150, 3, INK, INK)
    s += rect(190, 138, 38, 24, "#fff", INK, 1.4, 3) + text(209, 154, "R3", 8.5, INK, "middle", "bold")
    s += line(168, 150, 190, 150, INK, 2) + line(228, 150, 250, 150, INK, 2)
    s += line(110, 150, 168, 150, GREEN, 2) + text(106, 154, "Vref", 9, GREEN, "end", "bold") + text(110, 138, "1.65 В (опора)", 8, GREEN, "end")
    s += line(250, 150, 250, 104, INK, 1.4) + line(250, 104, 432, 104, INK, 1.4)
    s += rect(322, 92, 38, 24, "#fff", INK, 1.4, 3) + text(341, 108, "Rf", 8.5, INK, "middle", "bold")
    # вихід
    s += line(392, 168, 432, 168, INK, 2) + circle(432, 168, 3, INK, INK) + line(432, 104, 432, 168, INK, 1.4) + text(442, 150, "Vout", 10, INK, "start", "bold")
    # «+» вузол (сигнал через дільник)
    s += line(300, 186, 250, 186, INK, 2) + circle(250, 186, 3, INK, INK)
    s += rect(190, 174, 38, 24, "#fff", INK, 1.4, 3) + text(209, 190, "R1", 8.5, INK, "middle", "bold")
    s += line(168, 186, 190, 186, INK, 2) + line(228, 186, 250, 186, INK, 2)
    s += line(110, 186, 168, 186, INK, 2) + text(106, 190, "±5 В", 9, INK, "end", "bold")
    s += line(250, 186, 250, 224, INK, 1.4) + rect(231, 224, 38, 24, "#fff", INK, 1.4, 3) + text(250, 240, "R2", 8.5, INK, "middle", "bold")
    s += line(250, 248, 250, 272, INK, 1.4) + text(250, 286, "GND", 8, INK, "middle")
    # вихід -> АЦП
    s += arrow(432, 168, 516, 168, GREEN, 2) + rect(516, 148, 134, 40, LBLUE, "#9bb0c2", 1.4, 6) + text(583, 172, "АЦП 0…3.3 В", 9, INK, "middle", "bold")
    s += text(341, 66, "відношення резисторів → масштаб 0.33", 8.5, RED, "middle", "bold")
    s += text(583, 202, "(вихід має дістати 0 і 3.3 — RRO)", 7.5, GREY, "middle")
    save("fig-13-6a-2-circuit.svg", s)


# ── ⚙️ вставка до 2.8.8: нічник на фоторезисторі (Рис. 2.8.8a.k) ────────────
def fig138a_circuit():
    W, H = 700, 356
    s = header(W, H)
    s += text(W / 2, 28, "Нічник: фоторезистор + тригер Шмітта + ключ", 15, INK, "middle", "bold")
    vY, gY = 64, 318
    s += line(80, vY, 620, vY, RED, 2) + text(74, vY + 4, "+V", 10, RED, "end", "bold")
    s += line(80, gY, 620, gY, INK, 1.6) + text(74, gY + 4, "GND", 9, INK, "end")
    dx = 150
    s += rect(dx - 16, 92, 32, 44, "#fff7e6", COPP, 1.6, 4) + text(dx, 118, "LDR", 9, INK, "middle", "bold")
    s += line(dx, vY, dx, 92, INK, 2)
    s += line(dx, 136, dx, 180, INK, 2) + circle(dx, 180, 3, INK, INK) + text(dx - 9, 176, "N", 9, INK, "end", "bold")
    s += rect(dx - 14, 212, 28, 44, "#fff", INK, 1.5, 3) + text(dx + 24, 236, "R", 9, INK, "start", "bold")
    s += line(dx, 180, dx, 212, INK, 2) + line(dx, 256, dx, gY, INK, 1.6)
    s += text(dx, 290, "темно → N падає", 8.5, GREY, "middle")
    s += line(dx, 180, 252, 180, INK, 2)
    s += _opamp_sym(302, 180, 82, 66)
    s += text(302, 140, "тригер Шмітта", 8.5, GREY, "middle")
    s += _mosfet_sym(448, 184)
    s += line(344, 180, 404, 184, INK, 2)
    s += line(472, 140, 472, 108, INK, 2) + circle(472, 92, 16, "#fff", INK, 2)
    s += line(461, 81, 483, 103, INK, 1.6) + line(461, 103, 483, 81, INK, 1.6)
    s += line(472, 76, 472, vY, INK, 2) + text(494, 92, "лампа", 9, INK, "start", "bold")
    s += line(472, 228, 472, gY, INK, 2)
    s += text(W / 2, H - 12, "Темно → опір LDR великий → вузол N падає → тригер кидає вихід → ключ умикає лампу. Гістерезис не дає миготіти.",
              8.6, GREY, "middle", style="italic")
    save("fig-13-8a-1-circuit.svg", s)


def fig138a_behavior():
    W, H = 700, 356
    s = header(W, H)
    s += text(W / 2, 28, "Цілий день: гістерезис тримає лампу без миготіння", 14.5, INK, "middle", "bold")
    ox, oy, pw, ph = 84, 232, 556, 150
    s += _axes(ox, oy, pw, ph, "час доби →", "сигнал світла")
    pts = []
    for j in range(0, 281):
        t = j / 280.0
        v = 0.5 + 0.44 * math.cos(2 * math.pi * t) + 0.05 * math.sin(22 * math.pi * t)
        pts.append((ox + pw * t, oy - ph * 0.92 * max(0.0, min(1.0, v))))
    s += _poly(pts, SUN, 2.4)
    VH, VL = 0.5, 0.34

    def yf(v):
        return oy - ph * 0.92 * v
    s += line(ox, yf(VH), ox + pw, yf(VH), RED, 1.4, "5 4") + text(ox + pw + 4, yf(VH) + 4, "VH (вимк)", 8.5, RED, "start", "bold")
    s += line(ox, yf(VL), ox + pw, yf(VL), BLUE, 1.4, "5 4") + text(ox + pw + 4, yf(VL) + 4, "VL (вмик)", 8.5, BLUE, "start", "bold")
    # стан лампи (ON у темну середину)
    barY = oy + 40
    s += text(ox - 8, barY + 4, "лампа", 8.5, INK, "end")
    t1, t2 = 0.305, 0.695
    s += line(ox, barY, ox + pw * t1, barY, GREY, 4)
    s += line(ox + pw * t1, barY, ox + pw * t2, barY, GREEN, 6)
    s += line(ox + pw * t2, barY, ox + pw, barY, GREY, 4)
    s += text(ox + pw * 0.5, barY + 16, "УВІМК (ніч)", 8.5, GREEN, "middle", "bold")
    s += text(ox + pw * 0.12, barY + 16, "вимк", 8, GREY, "middle") + text(ox + pw * 0.88, barY + 16, "вимк", 8, GREY, "middle")
    s += text(ox + pw * 0.5, yf(0.95) + 4, "удень — ясно", 8.5, GREY, "middle")
    s += text(ox + pw * 0.5, yf(0.04) - 4, "брижі (хмари, фари) між порогами не вмикають", 8, INK, "middle")
    s += text(W / 2, H - 10, "Світло падає на сутінках, перетинає VL — лампа вмикається; вранці росте через VH — гасне. Між ними тримає.",
              8.6, GREY, "middle", style="italic")
    save("fig-13-8a-2-behavior.svg", s)


# ── 📜 історія до §2.8.2: Гарольд Блек (Рис. 2.8.2і.k) ───────────────────────
def fig132i_timeline():
    W, H = 968, 252
    s = header(W, H)
    s += text(W / 2, 30, "Дев'ять років недовіри: від ідеї (1927) до патенту (1937)", 16.5, INK, "middle", "bold")
    items = [
        (18, "1923", ["прямий зв'язок", "(feedforward) —", "надто капризний"], "#fdf1dc"),
        (190, "1927", ["пором через Гудзон:", "від'ємний", "зворотний зв'язок"], LGRN),
        (362, "1928", ["заявка на патент;", "бюро не вірить,", "що працює"], LBLUE),
        (534, "1932", ["Найквіст:", "теорія", "стійкості"], LBLUE),
        (706, "1937", ["патент видано —", "по дев'яти", "роках"], LGRN),
    ]
    bw, by, bh = 162, 88, 112
    for bx, yr, lines, fill in items:
        s += text(bx + bw / 2, by - 8, yr, 12.5, INK, "middle", "bold")
        s += rect(bx, by, bw, bh, fill, "#9bb0c2", 1.5, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 30 + k * 23, ln, 10.5, INK, "middle")
    for i in range(len(items) - 1):
        s += arrow(items[i][0] + bw + 1, by + bh / 2, items[i + 1][0] - 1, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14, "Ідея була така зухвала, що патентне бюро дев'ять років вважало її неможливою — як вічний двигун.",
              10, GREY, "middle", style="italic")
    save("fig-13-2i-1-timeline.svg", s)


def fig132i_two_ideas():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "Дві спроби Блека: прямий зв'язок і зворотний", 15, INK, "middle", "bold")
    # ліворуч: feedforward
    s += _frame(28, 50, 320, 240, "прямий зв'язок (1923)")
    s += rect(60, 110, 80, 40, LBLUE, BLUE, 1.4, 6) + text(100, 134, "підсил.", 9.5, INK, "middle", "bold")
    s += arrow(48, 130, 60, 130, INK, 2) + text(44, 134, "вх", 8.5, INK, "end")
    s += arrow(140, 130, 230, 130, INK, 2)
    s += rect(230, 110, 84, 40, "#fff3e0", COPP, 1.4, 6) + text(272, 130, "+ поправка", 9, INK, "middle", "bold")
    s += arrow(314, 130, 330, 130, INK, 2) + text(336, 134, "вих", 8.5, INK, "start")
    s += line(100, 150, 100, 190, INK, 1.4) + line(100, 190, 272, 190, INK, 1.4) + arrow(272, 190, 272, 150, INK, 1.4)
    s += text(186, 204, "виміряти спотворення → додати зворотне", 8.5, INK, "middle")
    s += text(186, 226, "працювало, та весь час «плило»:", 8.5, RED, "middle", "bold")
    s += text(186, 244, "треба було без кінця підстроювати", 8.5, RED, "middle")
    # праворуч: feedback
    s += _frame(372, 50, 320, 240, "зворотний зв'язок (1927)")
    s += circle(440, 130, 16, "#fff", INK, 2) + text(440, 136, "Σ", 13, INK, "middle", "bold")
    s += text(426, 112, "−", 10, BLUE, "middle", "bold")
    s += arrow(404, 130, 424, 130, INK, 2) + text(400, 134, "вх", 8.5, INK, "end")
    s += arrow(456, 130, 520, 130, INK, 2)
    s += rect(520, 110, 80, 40, LGRN, GREEN, 1.4, 6) + text(560, 134, "підсил.", 9.5, INK, "middle", "bold")
    s += arrow(600, 130, 632, 130, INK, 2) + text(638, 134, "вих", 8.5, INK, "start")
    s += line(620, 130, 620, 200, INK, 1.4) + line(620, 200, 440, 200, INK, 1.4) + arrow(440, 200, 440, 146, INK, 1.4)
    s += text(532, 216, "вихід повертають проти входу", 8.5, INK, "middle")
    s += text(532, 238, "сам себе виправляє — просто й твердо", 8.5, GREEN, "middle", "bold")
    save("fig-13-2i-2-two-ideas.svg", s)


def fig132i_trio():
    W, H = 720, 270
    s = header(W, H)
    s += text(W / 2, 30, "Винахід — колективний: троє з Bell Labs", 16, INK, "middle", "bold")
    people = [
        (40, "Гарольд Блек", ["1927:", "підсилювач зі", "зворотним зв'язком"], LGRN),
        (268, "Гаррі Найквіст", ["1932:", "коли він стійкий", "(теорія регенерації)"], LBLUE),
        (496, "Гендрік Боде", ["як його", "проєктувати", "(діаграми Боде)"], "#fff3e0"),
    ]
    bw, by, bh = 184, 78, 120
    for bx, name, lines, fill in people:
        s += rect(bx, by, bw, bh, fill, "#9bb0c2", 1.6, 8)
        s += text(bx + bw / 2, by + 26, name, 12, INK, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 52 + k * 20, ln, 10, INK, "middle")
    for i in range(len(people) - 1):
        s += arrow(people[i][0] + bw + 2, by + bh / 2, people[i + 1][0] - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14, "Блек дав підсилювач, Найквіст — коли він не зірветься в генерацію, Боде — як його розрахувати.",
              10, GREY, "middle", style="italic")
    save("fig-13-2i-3-trio.svg", s)


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
    # §13.10 що всередині ОП: диференційна пара
    fig1310_open_box()
    fig1310_diff_pair()
    fig1310_steering()
    fig1310_cmrr()
    fig1310_three_stages()
    fig1310_limits()
    # §13.11 LDO зсередини
    fig1311_architecture()
    fig1311_feedback()
    fig1311_noninv_disguise()
    fig1311_heat()
    fig1311_reference()
    fig1311_known_blocks()
    # 🔌 вставка до 2.8.11 — модуль стабілізатора
    fig1311c_module()
    fig1311c_fixed_vs_adj()
    # 🧮 вставка до 2.8.2 — формула зворотного зв'язку
    fig132m_loop()
    fig132m_desens()
    # 🧮 вставка до 2.8.8 — пороги гістерезису
    fig138m_schmitt()
    fig138m_band()
    # 🧮 вставка до 2.8.9 — GBW і slew rate
    fig139m_gbw()
    fig139m_slew()
    # 🧮 вставка до 2.8.11 — розсіювання LDO
    fig1311m_efficiency()
    fig1311m_when()
    # 🔌 вставка до 2.8.5 — буфер для високоомного джерела
    fig135c_problem()
    fig135c_buffer_fix()
    # 🔌 вставка до 2.8.7 — компаратори-мікросхеми
    fig137c_opencoll()
    fig137c_patterns()
    # 🔌 вставка до 2.8.9 — rail-to-rail і single-supply
    fig139c_swing()
    fig139c_single_supply()
    # ⚙️ вставка до 2.8.6 — зміщення й масштабування
    fig136a_line()
    fig136a_circuit()
    # ⚙️ вставка до 2.8.8 — нічник на фоторезисторі
    fig138a_circuit()
    fig138a_behavior()
    # 📜 історія до §2.8.2 — Гарольд Блек
    fig132i_timeline()
    fig132i_two_ideas()
    fig132i_trio()
    print("OK — Розділ 13 (історія + §13.1–§13.11 + вставки) згенеровано в", OUT)
