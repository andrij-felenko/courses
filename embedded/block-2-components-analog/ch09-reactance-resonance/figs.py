# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 9 — «Реактивність, фази й резонанс» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи посекційно (Рис. C.S.N);
для історії до розділу — секція 0 (Рис. 9.0.N). Допоміжні функції скопійовано
з попередніх розділів (єдиний вигляд).
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


def cap_sym(cx, cy, half=14, gap=9, col=INK):
    s = line(cx - gap / 2, cy - half, cx - gap / 2, cy + half, col, 2.6)
    s += line(cx + gap / 2, cy - half, cx + gap / 2, cy + half, col, 2.6)
    return s, cx - gap / 2, cx + gap / 2


def _peak(ox, oy, w, h, fc_frac, width, col, wv=2.6):
    """Дзвоноподібна крива резонансу: пік на fc_frac від ширини."""
    pts = []
    for j in range(0, 121):
        f = j / 120
        a = math.exp(-((f - fc_frac) / width) ** 2)
        pts.append((ox + f * w, oy - a * h))
    return _poly(pts, col, wv)


# ── Рис. 9.0.1 — таймлайн ────────────────────────────────────────────────────
def fig_timeline():
    W, H = 880, 600
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: як навчилися «ловити» одну частоту", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "від гойдалки до налаштованого радіо (сірим — кількісний зміст Розділу 9)",
              12.5, GREY, "middle", style="italic")
    spine = 220
    top, bot = 96, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("здавна", "Механічний резонанс", "Гойдалка, камертон, келих — відгук лише на «свою» ноту", False, False),
        ("1842", "Генрі / Henry", "Розряд лейденської банки СМИКАЄТЬСЯ туди-сюди — він коливальний", False, False),
        ("1853", "Кельвін / Kelvin", "Довів: коло L+C гойдається з частотою, заданою L і C", False, True),
        ("1887", "Герц / Hertz", "Резонансний приймач озивається лише в резонансі з передавачем", False, False),
        ("1900", "Лодж, Марконі", "Налаштовані контури → кожна станція на своїй частоті", False, False),
        ("Розділ 9", "Реактивність і резонанс", "Чому опір C і L залежить від частоти; f₀; добротність", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 58) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, (INK if not dest else GREY), "start", style="italic")
    save("fig-9-0-1-timeline.svg", s)


# ── Рис. 9.0.2 — механічний резонанс ─────────────────────────────────────────
def fig_mechanical_resonance():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Резонанс: відгук лише на «свою» частоту", 19, INK, "middle", "bold")
    # гойдалка
    s += _frame(40, 70, 320, 230, "гойдалка — штовхай у такт")
    px, py = 200, 100
    s += line(120, py, 280, py, INK, 3)  # перекладина
    # дві мотузки + сидіння під кутом
    ang = math.radians(20)
    bx, by = px + 110 * math.sin(ang), py + 110 * math.cos(ang)
    s += line(px - 8, py, bx - 8, by, GREY, 2)
    s += line(px + 8, py, bx + 8, by, GREY, 2)
    s += rect(bx - 16, by, 32, 10, "#caa46e", "#9c7b46", 1.4, 2)
    s += arrow(bx - 50, by - 6, bx - 16, by - 6, RED, 2.4)
    s += text(bx - 60, by - 16, "поштовх у такт", 10.5, RED, "end", "bold")
    s += text(200, 290, "розмах росте лише на власній частоті", 10.5, GREY, "middle", style="italic")
    # крива резонансу
    s += _frame(400, 70, 320, 230, "відгук від частоти")
    ox, oy, w, h = 440, 270, 240, 170
    s += _axes(ox, oy, w, h, "частота", "розмах")
    s += _peak(ox, oy, w, h, 0.5, 0.1, GREEN)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h, GREY, 1.2, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12.5, GREEN, "middle", "bold")
    s += text(ox + 0.5 * w, oy - h - 2, "власна частота", 10.5, GREEN, "middle", "bold")
    save("fig-9-0-2-mechanical-resonance.svg", s)


# ── Рис. 9.0.3 — LC-коливання (електричний маятник) ──────────────────────────
def fig_lc_oscillation():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Електричний маятник: енергія гойдається між C і L", 18, INK, "middle", "bold")
    # LC-контур
    s += _frame(40, 70, 300, 250, "коливальний контур")
    cx, cy = 190, 180
    cs, lx, rx = cap_sym(150, cy, 30, 16)
    s += cs
    coil, (cl, cr) = coil_h(230, cy, 70, 5, 20)
    s += coil
    s += line(150 - 4.5, cy - 30, 150 - 4.5, cy - 60, INK, 2)
    s += line(150 + 4.5, cy + 30, 150 + 4.5, cy + 60, INK, 2)
    s += line(150 - 4.5, cy - 60, cl, cy - 60, INK, 2)
    s += line(cl, cy - 60, cl, cy - 20, INK, 2)
    s += line(150 + 4.5, cy + 60, cr, cy + 60, INK, 2)
    s += line(cr, cy + 60, cr, cy + 20, INK, 2)
    s += text(150, cy + 90, "C", 13, RED, "middle", "bold")
    s += text(230, cy + 90, "L", 13, COPP, "middle", "bold")
    s += text(190, 300, "поле C ↔ поле L, туди-сюди", 10.5, GREY, "middle", style="italic")
    # синус V(t)
    s += _frame(370, 70, 390, 250, "напруга гойдається в часі")
    ox, oy, w, h = 400, 195, 330, 100
    s += line(ox, oy, ox + w, oy, GREY, 1.4)
    s += arrow(ox, oy + 0, ox, oy - h - 10, INK, 1.6) if False else ""
    pts = [(ox + j, oy - h * math.sin(j / w * math.pi * 4)) for j in range(0, int(w) + 1)]
    s += _poly(pts, GREEN, 2.4)
    s += text(400 + 195, 300, "власна частота f₀ задана L і C", 10.5, GREY, "middle", style="italic")
    s += rect(60, H - 40, W - 120, 26, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 21, "Конденсатор-пружина (½CV²) + котушка-маса (½LI²) = маятник, що гойдається.",
              11.5, INK, "middle", "bold")
    save("fig-9-0-3-lc-oscillation.svg", s)


# ── Рис. 9.0.4 — вибірковість ────────────────────────────────────────────────
def fig_tuning_selectivity():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Налаштований контур вихоплює одну станцію з багатьох", 17.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 280, 560, 200
    s += _axes(ox, oy, w, h, "частота", "сигнал / відгук")
    # станції (вертикальні лінії)
    stations = [0.18, 0.35, 0.52, 0.68, 0.85]
    for i, f in enumerate(stations):
        hh = h * (0.55 + 0.1 * ((i * 37) % 4) / 3)
        col = GREEN if abs(f - 0.52) < 0.01 else GREY
        s += line(ox + f * w, oy, ox + f * w, oy - hh, col, 3)
    # крива резонансу на одній станції
    s += _peak(ox, oy, w, h, 0.52, 0.06, GREEN, 2.4)
    s += text(ox + 0.52 * w, oy - h - 2, "вибрано", 11.5, GREEN, "middle", "bold")
    s += text(ox + 0.85 * w, oy - h * 0.45, "придушено", 10.5, GREY, "middle")
    s += text(W / 2, H - 14, "Контур бурхливо відгукується лише на свою частоту — це вибірковість.",
              11.5, GREY, "middle", style="italic")
    save("fig-9-0-4-tuning-selectivity.svg", s)


# ── Рис. 9.0.5 — радіо до й після налаштування ───────────────────────────────
def fig_marconi_before_after():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Радіо до й після налаштованих контурів", 19, INK, "middle", "bold")
    # до — широкі горби, що перекриваються
    s += _frame(40, 70, 330, 230, "до: какофонія")
    ox, oy, w, h = 70, 270, 270, 150
    s += line(ox, oy, ox + w, oy, GREY, 1.4)
    for fc in (0.3, 0.55):
        pts = [(ox + f * w, oy - h * 0.8 * math.exp(-((f - fc) / 0.22) ** 2)) for f in [j / 120 for j in range(121)]]
        s += _poly(pts, RED, 2)
    s += text(205, 250, "широкі іскрові передавачі глушать одне одного", 9.5, RED, "middle", style="italic")
    # після — вузькі піки
    s += _frame(400, 70, 330, 230, "після: окремі канали")
    ox2 = 430
    s += line(ox2, oy, ox2 + w, oy, GREY, 1.4)
    for fc in (0.2, 0.4, 0.6, 0.8):
        pts = [(ox2 + f * w, oy - h * 0.85 * math.exp(-((f - fc) / 0.04) ** 2)) for f in [j / 160 for j in range(161)]]
        s += _poly(pts, GREEN, 2)
    s += text(565, 250, "кожна станція на своїй частоті", 9.5, GREEN, "middle", style="italic")
    save("fig-9-0-5-marconi-before-after.svg", s)


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


# ── Рис. 9.1.1 — що таке частота ─────────────────────────────────────────────
def fig11_ac_frequency():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 34, "Частота: вища частота — швидші зміни сигналу", 19, INK, "middle", "bold")
    # низька частота
    s += _frame(40, 70, 320, 230, "низька частота")
    ox, oy, w, a = 60, 185, 280, 75
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, a, 1.5, BLUE)
    s += text(200, 290, "пологі нахили — міняється мляво", 10.5, GREY, "middle", style="italic")
    # висока частота
    s += _frame(400, 70, 320, 230, "висока частота")
    ox2 = 420
    s += line(ox2, oy, ox2 + w, oy, GREY, 1.2)
    s += _sine(ox2, oy, w, a, 5, RED)
    s += text(560, 290, "круті нахили — міняється швидко", 10.5, GREY, "middle", style="italic")
    s += rect(60, H - 30, W - 120, 1, "none", "none", 0)
    s += text(W / 2, H - 12, "Та сама амплітуда; «крутість» зміни (dV/dt, di/dt) і відчувають C та L.",
              11, INK, "middle", "bold")
    save("fig-9-1-1-ac-frequency.svg", s)


# ── Рис. 9.1.2 — Xc спадає з частотою ────────────────────────────────────────
def fig11_cap_vs_freq():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Реактивність конденсатора Xc спадає з частотою", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 290, 520, 210
    s += _axes(ox, oy, w, h, "частота f", "Xc")
    pts = []
    for j in range(4, int(w) + 1):
        f = j / w
        y = oy - min(h * 0.95, h * 0.06 / f)
        pts.append((ox + j, y))
    s += _poly(pts, RED, 2.8)
    s += text(ox + 30, oy - h * 0.9, "f → 0: ∞", 12.5, RED, "start", "bold")
    s += text(ox + 30, oy - h * 0.78, "(блокує)", 10.5, GREY, "start")
    s += text(ox + w - 10, oy - h * 0.12, "висока f: мала", 11.5, RED, "end", "bold")
    s += text(ox + w - 10, oy + 0, "(пропускає)", 10.5, GREY, "end")
    s += text(W / 2, H - 12, "Конденсатор «любить» швидке: що вища частота, то легше пропускає.",
              11, GREY, "middle", style="italic")
    save("fig-9-1-2-cap-vs-freq.svg", s)


# ── Рис. 9.1.3 — чому: i = C·dV/dt ───────────────────────────────────────────
def fig11_why_cap():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому: струм конденсатора — це швидкість зміни напруги", 17, INK, "middle", "bold")
    ox, oy, w = 90, 175, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 70, 2, BLUE)
    s += text(ox + w + 6, oy, "V", 13, BLUE, "start", "bold")
    s += _sine(ox, oy, w, 70, 2, RED, phase=math.pi / 2)
    s += text(ox + w + 6, oy - 60, "i = C·dV/dt", 12.5, RED, "start", "bold")
    s += text(W / 2, 290, "Струм (червоний) великий там, де напруга міняється найшвидше (крутий схил).",
              11, INK, "middle", "bold")
    s += text(W / 2, 312, "Вища частота → крутіші схили → більший струм → менша протидія.",
              11, GREY, "middle", style="italic")
    save("fig-9-1-3-why-cap.svg", s)


# ── Рис. 9.1.4 — XL росте з частотою ─────────────────────────────────────────
def fig11_coil_vs_freq():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Реактивність котушки XL росте з частотою", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 290, 520, 210
    s += _axes(ox, oy, w, h, "частота f", "XL")
    s += _poly([(ox, oy), (ox + w, oy - h * 0.92)], COPP, 2.8)
    s += text(ox + 20, oy - 14, "f → 0: 0", 12, COPP, "start", "bold")
    s += text(ox + 20, oy - 2, "(дріт)", 10.5, GREY, "start")
    s += text(ox + w - 10, oy - h * 0.92 - 4, "висока f: велика", 11.5, COPP, "end", "bold")
    s += text(ox + w - 10, oy - h * 0.8, "(блокує)", 10.5, GREY, "end")
    s += text(W / 2, H - 12, "Котушка «любить» повільне — точне дзеркало конденсатора.",
              11, GREY, "middle", style="italic")
    save("fig-9-1-4-coil-vs-freq.svg", s)


# ── Рис. 9.1.5 — чому: V = L·di/dt ───────────────────────────────────────────
def fig11_why_coil():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому: напруга котушки — це швидкість зміни струму", 17, INK, "middle", "bold")
    ox, oy, w = 90, 175, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 70, 2, COPP)
    s += text(ox + w + 6, oy, "i", 13, COPP, "start", "bold")
    s += _sine(ox, oy, w, 70, 2, BLUE, phase=math.pi / 2)
    s += text(ox + w + 6, oy - 60, "V = L·di/dt", 12.5, BLUE, "start", "bold")
    s += text(W / 2, 290, "Напруга (синій) велика там, де струм міняється найшвидше (крутий схил).",
              11, INK, "middle", "bold")
    s += text(W / 2, 312, "Вища частота → крутіші схили → більша напруга → більша протидія.",
              11, GREY, "middle", style="italic")
    save("fig-9-1-5-why-coil.svg", s)


# ── Рис. 9.1.6 — реактивність проти опору ────────────────────────────────────
def fig11_reactance_vs_resistance():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 34, "Реактивність ≠ опір: дві відмінності", 19, INK, "middle", "bold")
    # опір
    s += _frame(40, 70, 320, 230, "опір R")
    ox, oy, w, h = 70, 250, 250, 150
    s += _axes(ox, oy, w, h, "f", "R")
    s += line(ox, oy - h * 0.55, ox + w, oy - h * 0.55, INK, 2.6)
    s += text(ox + w / 2, oy - h * 0.68, "сталий із частотою", 10.5, INK, "middle", "bold")
    for k in range(3):
        xx = 150 + k * 22
        s += f'<path d="M {xx},120 q 5,-10 10,0 q 5,10 10,0" fill="none" stroke="{RED}" stroke-width="1.6"/>\n'
    s += text(205, 108, "гріється", 10, RED, "middle", "bold")
    # реактивність
    s += _frame(400, 70, 320, 230, "реактивність X")
    ox2 = 430
    s += _axes(ox2, oy, w, h, "f", "X")
    pts = [(ox2 + j, oy - min(h * 0.9, h * 0.06 / (j / w))) for j in range(5, int(w) + 1)]
    s += _poly(pts, GREEN, 2.4)
    s += text(ox2 + w / 2, oy - h * 0.8, "залежить від f", 10.5, GREEN, "middle", "bold")
    s += arrow(560, 120, 590, 120, GREEN, 1.8)
    s += arrow(590, 135, 560, 135, GREEN, 1.8)
    s += text(620, 130, "енергія", 9.5, GREEN, "start")
    s += text(620, 143, "туди-сюди", 9.5, GREY, "start")
    s += text(W / 2, H - 12, "Обидві — в омах, але X залежить від частоти й не витрачає енергії.",
              11, INK, "middle", "bold")
    save("fig-9-1-6-reactance-vs-resistance.svg", s)


# ── Рис. 9.1.7 — дзеркальні близнюки ─────────────────────────────────────────
def fig11_mirror():
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 34, "Дзеркало: Xc спадає, XL росте — і перетинаються", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 300, 520, 220
    s += _axes(ox, oy, w, h, "частота f", "реактивність")
    # Xc спадає
    pts = [(ox + j, oy - min(h * 0.95, h * 0.16 / (j / w))) for j in range(5, int(w) + 1)]
    s += _poly(pts, RED, 2.6)
    # XL росте
    s += _poly([(ox, oy), (ox + w, oy - h * 0.95)], COPP, 2.6)
    s += text(ox + w - 6, oy - h * 0.2, "Xc (конденсатор)", 11.5, RED, "end", "bold")
    s += text(ox + w - 6, oy - h * 0.86, "XL (котушка)", 11.5, COPP, "end", "bold")
    # точка перетину ~ де 0.16/f = 0.95*f/w... approx mark
    fx = ox + 0.41 * w
    fy = oy - h * 0.39
    s += circle(fx, fy, 5, GREEN, GREEN, 0)
    s += line(fx, oy, fx, fy, GREY, 1.2, dash="4,4")
    s += text(fx, oy + 18, "f₀", 12.5, GREEN, "middle", "bold")
    s += text(fx + 70, fy - 14, "тут — резонанс (§9.5)", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Конденсатор пропускає високі частоти, котушка — низькі. Разом → фільтри й резонанс.",
              11, GREY, "middle", style="italic")
    save("fig-9-1-7-mirror.svg", s)


# ── Рис. 9.2.1 — формула Xc ──────────────────────────────────────────────────
def fig21_formula():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 36, "Реактивний опір конденсатора", 20, INK, "middle", "bold")
    cy = 150
    s += text(150, cy, "Xc", 34, INK, "middle", "bold")
    s += text(205, cy, "=", 30, INK, "middle")
    s += text(300, cy - 18, "1", 30, INK, "middle", "bold")
    s += line(250, cy + 2, 470, cy + 2, INK, 2.4)
    s += text(300, cy + 34, "2 · π · f · C", 26, INK, "middle", "bold")
    # анотації
    s += arrow(390, cy + 70, 390, cy + 44, RED, 1.8)
    s += text(390, cy + 90, "↑ частота → ↓ Xc", 12.5, RED, "middle", "bold")
    s += arrow(450, cy + 70, 450, cy + 44, BLUE, 1.8)
    s += text(470, cy + 108, "↑ ємність → ↓ Xc", 12.5, BLUE, "middle", "bold")
    s += text(300, cy + 60, "2πf = ω", 12.5, GREY, "middle", style="italic")
    s += rect(110, 250, W - 220, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 272, "І частота, і ємність — у знаменнику: обидві зменшують реактивність.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 291, "Вимірюється в омах; на DC (f=0) Xc → ∞ (блокує).", 11, GREY, "middle", style="italic")
    save("fig-9-2-1-formula.svg", s)


# ── Рис. 9.2.2 — звідки ω = 2πf ──────────────────────────────────────────────
def fig21_where_omega():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Звідки 2π: фаза «крутиться» по колу", 19, INK, "middle", "bold")
    # фазове коло
    ccx, ccy, r = 150, 170, 70
    s += circle(ccx, ccy, r, "none", INK, 2)
    ang = math.radians(50)
    px, py = ccx + r * math.cos(ang), ccy - r * math.sin(ang)
    s += line(ccx, ccy, px, py, RED, 2.4)
    s += circle(px, py, 4, RED, RED, 0)
    s += arrow(ccx + r + 4, ccy - 10, ccx + r + 4, ccy + 10, GREY, 1.6)
    s += text(ccx, ccy + r + 22, "1 оберт = 2π = 1 коливання", 10.5, INK, "middle", "bold")
    # проєкція в синус
    ox, oy, w = 260, 170, 380
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, r, 2, RED)
    s += line(px, py, ox, py, GREY, 1.2, dash="3,3")
    s += text(ox + w / 2, oy + 60, "ω = 2π·f  (радіан за секунду)", 13, INK, "middle", "bold")
    s += rect(60, H - 56, W - 120, 42, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 38, "i = C·dV/dt → амплітуда струму = C·ω·V₀ → Xc = V₀/I₀ = 1/(ωC).",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 21, "Звідси і множник 2π, і обернена залежність від f та C.", 10.5, GREY, "middle", style="italic")
    save("fig-9-2-2-where-omega.svg", s)


# ── Рис. 9.2.3 — закон Ома для конденсатора ──────────────────────────────────
def fig21_ohm_for_cap():
    W, H = 700, 250
    s = header(W, H)
    s += text(W / 2, 34, "Xc працює як опір у законі Ома (для амплітуд)", 18, INK, "middle", "bold")
    # резистор
    s += text(200, 90, "резистор", 13, GREY, "middle", "bold")
    s += text(200, 135, "V = I · R", 24, INK, "middle", "bold")
    s += text(200, 165, "R — стала", 11, GREY, "middle", style="italic")
    s += line(360, 80, 360, 200, FAINT, 2)
    # конденсатор
    s += text(520, 90, "конденсатор", 13, GREEN, "middle", "bold")
    s += text(520, 135, "V = I · Xc", 24, INK, "middle", "bold")
    s += text(520, 165, "Xc залежить від f", 11, GREY, "middle", style="italic")
    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Рахуємо так само, як резистор, — лише Xc перераховуємо для кожної частоти.",
              12, INK, "middle", "bold")
    save("fig-9-2-3-ohm-for-cap.svg", s)


# ── Рис. 9.2.4 — Xc(f) ───────────────────────────────────────────────────────
def fig21_vs_freq():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Xc спадає з частотою (для 1 мкФ)", 19, INK, "middle", "bold")
    ox, oy, w, h = 110, 290, 520, 210
    s += _axes(ox, oy, w, h, "частота (лог)", "Xc (лог)")
    s += _poly([(ox + 20, oy - h * 0.92), (ox + w - 10, oy - h * 0.08)], RED, 2.8)
    pts = [(0.12, 0.8, "50 Гц: 3.2 кОм"), (0.45, 0.5, "1 кГц: 159 Ом"), (0.82, 0.16, "1 МГц: 0.16 Ом")]
    for fx, fy, lab in pts:
        x, y = ox + fx * w, oy - fy * h
        s += circle(x, y, 4.5, RED, RED, 0)
        s += text(x + 8, y - 6, lab, 10.5, INK, "start", "bold")
    s += text(ox + 10, oy - h - 2, "пряма в лог-лог осях", 10.5, GREY, "start", style="italic")
    save("fig-9-2-4-vs-freq.svg", s)


# ── Рис. 9.2.5 — Xc від ємності ──────────────────────────────────────────────
def fig21_vs_c():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 34, "На тій самій частоті: більша C — менша Xc", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 270, 520, 190
    s += _axes(ox, oy, w, h, "ємність C", "Xc")
    pts = []
    for j in range(6, int(w) + 1):
        c = j / w
        pts.append((ox + j, oy - min(h * 0.95, h * 0.07 / c)))
    s += _poly(pts, BLUE, 2.8)
    s += circle(ox + 0.1 * w, oy - h * 0.7, 4.5, BLUE, BLUE, 0)
    s += text(ox + 0.1 * w + 8, oy - h * 0.7 - 6, "1 мкФ: 3.2 кОм", 10.5, INK, "start", "bold")
    s += circle(ox + 0.7 * w, oy - h * 0.1, 4.5, BLUE, BLUE, 0)
    s += text(ox + 0.7 * w + 8, oy - h * 0.1 - 6, "100 мкФ: 32 Ом", 10.5, INK, "start", "bold")
    s += text(W / 2, H - 12, "(на 50 Гц) Тому згладжувальні конденсатори беруть великими.",
              11, GREY, "middle", style="italic")
    save("fig-9-2-5-vs-c.svg", s)


# ── Рис. 9.2.6 — Xc 1мкФ через увесь діапазон ────────────────────────────────
def fig21_worked_scale():
    W, H = 760, 250
    s = header(W, H)
    s += text(W / 2, 34, "Реактивність 1 мкФ: від ∞ до часток ома", 19, INK, "middle", "bold")
    x0, x1, y = 90, 690, 150
    s += line(x0, y, x1, y, INK, 2.4)
    marks = [(0.04, "0 Гц", "∞", RED), (0.28, "50 Гц", "3.2 кОм", INK),
             (0.52, "1 кГц", "159 Ом", INK), (0.78, "1 МГц", "0.16 Ом", GREEN)]
    for fx, fl, xl, col in marks:
        x = x0 + fx * (x1 - x0)
        s += line(x, y - 7, x, y + 7, INK, 2)
        s += text(x, y - 14, fl, 11.5, INK, "middle", "bold")
        s += text(x, y + 28, xl, 12.5, col, "middle", "bold")
    s += arrow(x0 + 40, y + 50, x1 - 40, y + 50, GREY, 1.6)
    s += text((x0 + x1) / 2, y + 44, "частота росте →   Xc падає", 11, GREY, "middle", style="italic")
    s += text(W / 2, H - 16, "Та сама деталь: блокує постійне, майже коротить високочастотне.",
              11, INK, "middle", "bold")
    save("fig-9-2-6-worked-scale.svg", s)


# ── Рис. 9.3.1 — формула XL ──────────────────────────────────────────────────
def fig31_formula():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 36, "Реактивний опір котушки", 20, INK, "middle", "bold")
    cy = 140
    s += text(180, cy, "XL", 34, INK, "middle", "bold")
    s += text(240, cy, "=", 30, INK, "middle")
    s += text(330, cy, "2 · π · f · L", 30, INK, "middle", "bold")
    s += text(470, cy, "= ω·L", 22, GREY, "middle")
    s += arrow(300, cy + 50, 300, cy + 18, RED, 1.8)
    s += text(300, cy + 70, "↑ частота → ↑ XL", 12.5, RED, "middle", "bold")
    s += arrow(400, cy + 50, 400, cy + 18, BLUE, 1.8)
    s += text(400, cy + 88, "↑ індуктивність → ↑ XL", 12.5, BLUE, "middle", "bold")
    s += rect(110, 230, W - 220, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 252, "І частота, і індуктивність — у ЧИСЕЛЬНИКУ (на відміну від Xc): обидві її піднімають.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 271, "В омах; на DC (f=0) XL = 0 (дріт).", 11, GREY, "middle", style="italic")
    save("fig-9-3-1-formula.svg", s)


# ── Рис. 9.3.2 — звідки XL = ωL ──────────────────────────────────────────────
def fig31_where_omega():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 34, "Звідки XL = ωL: напруга котушки ∝ швидкості зміни струму", 16.5, INK, "middle", "bold")
    ox, oy, w = 90, 150, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 65, 2, COPP)
    s += text(ox + w + 6, oy, "i", 13, COPP, "start", "bold")
    s += _sine(ox, oy, w, 65, 2, BLUE, phase=math.pi / 2)
    s += text(ox + w + 6, oy - 55, "V = L·di/dt", 12, BLUE, "start", "bold")
    s += rect(60, H - 80, W - 120, 64, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 58, "i = I₀·sin(ωt) → амплітуда напруги = L·ω·I₀ → XL = V₀/I₀ = ω·L.",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 40, "Дзеркало конденсатора: там швидка напруга давала струм (Xc=1/ωC),",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 24, "тут швидкий струм дає напругу (XL = ωL).", 10.5, GREY, "middle", style="italic")
    save("fig-9-3-2-where-omega.svg", s)


# ── Рис. 9.3.3 — закон Ома для котушки ───────────────────────────────────────
def fig31_ohm_for_coil():
    W, H = 700, 240
    s = header(W, H)
    s += text(W / 2, 34, "XL працює як опір у законі Ома (для амплітуд)", 18, INK, "middle", "bold")
    s += text(200, 90, "резистор", 13, GREY, "middle", "bold")
    s += text(200, 135, "V = I · R", 24, INK, "middle", "bold")
    s += line(360, 75, 360, 195, FAINT, 2)
    s += text(520, 90, "котушка", 13, COPP, "middle", "bold")
    s += text(520, 135, "V = I · XL", 24, INK, "middle", "bold")
    s += text(520, 162, "XL росте з f", 11, GREY, "middle", style="italic")
    s += rect(60, H - 42, W - 120, 28, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 23, "Рахуємо як резистор — лише XL перераховуємо для кожної частоти.",
              12, INK, "middle", "bold")
    save("fig-9-3-3-ohm-for-coil.svg", s)


# ── Рис. 9.3.4 — XL(f) ───────────────────────────────────────────────────────
def fig31_vs_freq():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "XL росте з частотою (для 10 мГн)", 19, INK, "middle", "bold")
    ox, oy, w, h = 110, 290, 520, 210
    s += _axes(ox, oy, w, h, "частота", "XL")
    s += _poly([(ox, oy), (ox + w, oy - h * 0.92)], COPP, 2.8)
    pts = [(0.05, 0.05, "50 Гц: 3 Ом"), (0.5, 0.46, "1 кГц: 63 Ом"), (0.9, 0.83, "1 МГц: 63 кОм")]
    for fx, fy, lab in pts:
        x, y = ox + fx * w, oy - fy * h
        s += circle(x, y, 4.5, COPP, COPP, 0)
        s += text(x + 8, y - 6, lab, 10.5, INK, "start", "bold")
    s += text(ox + 20, oy - 16, "f=0: XL=0 (дріт)", 10.5, GREY, "start")
    save("fig-9-3-4-vs-freq.svg", s)


# ── Рис. 9.3.5 — XL від індуктивності ────────────────────────────────────────
def fig31_vs_l():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 34, "На тій самій частоті: більша L — більша XL", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 270, 520, 190
    s += _axes(ox, oy, w, h, "індуктивність L", "XL")
    s += _poly([(ox, oy), (ox + w, oy - h * 0.9)], COPP, 2.8)
    s += circle(ox + 0.12 * w, oy - h * 0.108, 4.5, COPP, COPP, 0)
    s += text(ox + 0.12 * w + 8, oy - h * 0.108 - 6, "10 мГн: 63 Ом", 10.5, INK, "start", "bold")
    s += circle(ox + 0.85 * w, oy - h * 0.76, 4.5, COPP, COPP, 0)
    s += text(ox + 0.85 * w + 6, oy - h * 0.76 - 6, "100 мГн: 630 Ом", 10.5, INK, "end", "bold")
    s += text(W / 2, H - 12, "(на 1 кГц) Тому для придушення низьких частот беруть більші дроселі.",
              11, GREY, "middle", style="italic")
    save("fig-9-3-5-vs-l.svg", s)


# ── Рис. 9.3.6 — дзеркало Xc/XL ──────────────────────────────────────────────
def fig31_mirror():
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 34, "Дзеркало: Xc спадає, XL росте — і перетинаються", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 300, 520, 220
    s += _axes(ox, oy, w, h, "частота f", "реактивність")
    pts = [(ox + j, oy - min(h * 0.95, h * 0.16 / (j / w))) for j in range(5, int(w) + 1)]
    s += _poly(pts, RED, 2.6)
    s += _poly([(ox, oy), (ox + w, oy - h * 0.95)], COPP, 2.6)
    s += text(ox + w - 6, oy - h * 0.2, "Xc = 1/(2πfC)", 11.5, RED, "end", "bold")
    s += text(ox + w - 6, oy - h * 0.86, "XL = 2πfL", 11.5, COPP, "end", "bold")
    fx, fy = ox + 0.41 * w, oy - h * 0.39
    s += circle(fx, fy, 5, GREEN, GREEN, 0)
    s += line(fx, oy, fx, fy, GREY, 1.2, dash="4,4")
    s += text(fx, oy + 18, "f₀", 12.5, GREEN, "middle", "bold")
    s += text(fx + 90, fy - 12, "Xc = XL → резонанс (§9.5)", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Конденсатор пропускає високі частоти, котушка — низькі. Разом → фільтри й резонанс.",
              11, GREY, "middle", style="italic")
    save("fig-9-3-6-mirror.svg", s)


# ── Рис. 9.4.1 — резистор: у фазі ────────────────────────────────────────────
def fig41_resistor_inphase():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 34, "Резистор: струм і напруга в фазі (0°)", 19, INK, "middle", "bold")
    ox, oy, w = 90, 160, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 75, 2, BLUE)
    s += _sine(ox, oy, w, 60, 2, RED)
    s += text(ox + w + 6, oy - 60, "V", 13, BLUE, "start", "bold")
    s += text(ox + w + 6, oy - 45, "I", 13, RED, "start", "bold")
    s += line(ox + 65, oy - 75, ox + 65, oy + 40, GREY, 1, dash="3,3")
    s += text(W / 2, H - 40, "Піки збігаються, нулі збігаються — зсув нуль.", 12, INK, "middle", "bold")
    s += text(W / 2, H - 22, "Лише тут елемент справді споживає потужність (гріється).", 11, GREY, "middle", style="italic")
    save("fig-9-4-1-resistor-inphase.svg", s)


# ── Рис. 9.4.2 — конденсатор: струм веде ─────────────────────────────────────
def fig41_cap_leads():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 34, "Конденсатор: струм випереджає напругу на 90°", 18, INK, "middle", "bold")
    ox, oy, w = 90, 160, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 75, 2, BLUE)
    s += _sine(ox, oy, w, 65, 2, RED, phase=math.pi / 2)
    s += text(ox + w + 6, oy - 30, "V", 13, BLUE, "start", "bold")
    s += text(ox + w + 6, oy + 14, "I", 13, RED, "start", "bold")
    s += arrow(ox + 130, oy - 95, ox + 65, oy - 95, RED, 2)
    s += text(ox + 150, oy - 92, "струм веде", 11, RED, "start", "bold")
    s += text(W / 2, H - 22, "ICE: у Capacitor I (струм) перед E (напругою). Струм прибуває першим.",
              11.5, INK, "middle", "bold")
    save("fig-9-4-2-cap-leads.svg", s)


# ── Рис. 9.4.3 — котушка: струм відстає ──────────────────────────────────────
def fig41_coil_lags():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 34, "Котушка: струм відстає від напруги на 90°", 18, INK, "middle", "bold")
    ox, oy, w = 90, 160, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 75, 2, BLUE)
    s += _sine(ox, oy, w, 65, 2, RED, phase=-math.pi / 2)
    s += text(ox + w + 6, oy - 30, "V", 13, BLUE, "start", "bold")
    s += text(ox + w + 6, oy + 14, "I", 13, RED, "start", "bold")
    s += arrow(ox + 65, oy + 95, ox + 130, oy + 95, RED, 2)
    s += text(ox + 150, oy + 98, "струм відстає", 11, RED, "start", "bold")
    s += text(W / 2, H - 22, "ELI: у котушці (L) E (напруга) перед I (струмом). Струм приходить пізніше.",
              11.5, INK, "middle", "bold")
    save("fig-9-4-3-coil-lags.svg", s)


# ── Рис. 9.4.4 — чому 90° ────────────────────────────────────────────────────
def fig41_why_90():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 34, "Чому 90°: нахил синуса — теж синус, зсунений на чверть", 16.5, INK, "middle", "bold")
    ox, oy, w = 90, 170, 520
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    s += _sine(ox, oy, w, 75, 2, BLUE)
    s += _sine(ox, oy, w, 65, 2, GREEN, phase=math.pi / 2)
    s += text(ox + w + 6, oy - 30, "сигнал", 11, BLUE, "start", "bold")
    s += text(ox + w + 6, oy + 16, "нахил", 11, GREEN, "start", "bold")
    # відмітка: на нулі сигналу нахил максимальний
    zx = ox + w / 4
    s += line(zx, oy, zx, oy - 75, GREY, 1, dash="3,3")
    s += text(zx, oy + 18, "тут сигнал=0,", 9.5, GREY, "middle")
    s += text(zx, oy + 30, "нахил max", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 16, "Похідна синуса максимальна на його нулях → зсунена на 90°.",
              11.5, INK, "middle", "bold")
    save("fig-9-4-4-why-90.svg", s)


# ── Рис. 9.4.5 — мнемоніка ELI the ICE man ───────────────────────────────────
def fig41_eli_ice():
    W, H = 700, 280
    s = header(W, H)
    s += text(W / 2, 36, "Мнемоніка: ELI the ICE man", 20, INK, "middle", "bold")
    # ELI
    s += rect(60, 80, 280, 140, "#dbe3f7", BLUE, 1.8, 12)
    s += text(200, 112, "котушка (L)", 13, INK, "middle", "bold")
    s += text(200, 156, "E  L  I", 30, INK, "middle", "bold")
    s += arrow(165, 178, 235, 178, BLUE, 2)
    s += text(200, 200, "E (напруга) → веде", 12, BLUE, "middle", "bold")
    # ICE
    s += rect(360, 80, 280, 140, "#f7dada", RED, 1.8, 12)
    s += text(500, 112, "конденсатор (C)", 13, INK, "middle", "bold")
    s += text(500, 156, "I  C  E", 30, INK, "middle", "bold")
    s += arrow(465, 178, 535, 178, RED, 2)
    s += text(500, 200, "I (струм) → веде", 12, RED, "middle", "bold")
    s += text(W / 2, H - 16, "Літера компонента — посередині; хто стоїть першим, той і випереджає.",
              11, GREY, "middle", style="italic")
    save("fig-9-4-5-eli-ice.svg", s)


# ── Рис. 9.4.6 — фазори ──────────────────────────────────────────────────────
def fig41_phasors():
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 34, "Фазори: опір і реактивності під прямим кутом", 18, INK, "middle", "bold")
    cx, cy = 350, 200
    s += line(cx - 160, cy, cx + 160, cy, GREY, 1.4)
    s += line(cx, cy - 120, cx, cy + 120, GREY, 1.4)
    # R горизонтально
    s += arrow(cx, cy, cx + 140, cy, INK, 3)
    s += text(cx + 150, cy + 4, "R (0°)", 13, INK, "start", "bold")
    # XL вгору
    s += arrow(cx, cy, cx, cy - 110, COPP, 3)
    s += text(cx + 6, cy - 116, "XL (+90°)", 13, COPP, "start", "bold")
    # Xc вниз
    s += arrow(cx, cy, cx, cy + 110, RED, 3)
    s += text(cx + 6, cy + 124, "Xc (−90°)", 13, RED, "start", "bold")
    # Z діагональ
    s += arrow(cx, cy, cx + 110, cy - 80, GREEN, 2.4, dash="5,4")
    s += text(cx + 116, cy - 84, "Z = √(R²+X²)", 12, GREEN, "start", "bold")
    s += text(W / 2, H - 30, "XL і Xc протилежні — можуть гаситися (резонанс).", 11.5, INK, "middle", "bold")
    s += text(W / 2, H - 14, "R і X перпендикулярні — складаються за теоремою Піфагора (імпеданс).",
              11, GREY, "middle", style="italic")
    save("fig-9-4-6-phasors.svg", s)


# ── Рис. 9.4.7 — реактивність не гріється ────────────────────────────────────
def fig41_no_power():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Зсув 90° → середня потужність нуль", 19, INK, "middle", "bold")
    ox, oy, w = 90, 175, 540
    s += line(ox, oy, ox + w, oy, GREY, 1.2)
    # V і I (90° зсув)
    s += _sine(ox, oy, w, 45, 2, BLUE, wv=1.6)
    s += _sine(ox, oy, w, 45, 2, RED, wv=1.6, phase=math.pi / 2)
    # потужність P = V·i (подвійна частота, навколо нуля) — заштрихована
    pts = []
    for j in range(0, int(w) + 1):
        t = j / w
        p = math.sin(2 * math.pi * 2 * t) * math.cos(2 * math.pi * 2 * t)
        pts.append((ox + j, oy - p * 95))
    s += _poly(pts, GREEN, 2.6)
    s += text(ox + w + 6, oy - 40, "V", 11, BLUE, "start", "bold")
    s += text(ox + w + 6, oy - 24, "I", 11, RED, "start", "bold")
    s += text(ox + w + 6, oy + 4, "P=V·i", 11, GREEN, "start", "bold")
    s += text(ox + w * 0.25, oy - 80, "+", 18, GREEN, "middle", "bold")
    s += text(ox + w * 0.5, oy + 80, "−", 18, GREEN, "middle", "bold")
    s += text(W / 2, H - 18, "Потужність половину часу додатна (бере енергію), половину — від'ємна (віддає). Середнє = 0.",
              11.5, INK, "middle", "bold")
    save("fig-9-4-7-no-power.svg", s)


# ── Рис. 9.5.1 — Xc = XL на f₀ ───────────────────────────────────────────────
def fig51_crossing():
    W, H = 700, 360
    s = header(W, H)
    s += text(W / 2, 34, "Резонанс — там, де Xc = XL", 19, INK, "middle", "bold")
    ox, oy, w, h = 110, 300, 520, 220
    s += _axes(ox, oy, w, h, "частота f", "реактивність")
    pts = [(ox + j, oy - min(h * 0.95, h * 0.16 / (j / w))) for j in range(5, int(w) + 1)]
    s += _poly(pts, RED, 2.6)
    s += _poly([(ox, oy), (ox + w, oy - h * 0.95)], COPP, 2.6)
    s += text(ox + w - 6, oy - h * 0.2, "Xc", 12.5, RED, "end", "bold")
    s += text(ox + w - 6, oy - h * 0.86, "XL", 12.5, COPP, "end", "bold")
    fx, fy = ox + 0.41 * w, oy - h * 0.39
    s += circle(fx, fy, 6, GREEN, GREEN, 0)
    s += line(fx, oy, fx, fy, GREY, 1.2, dash="4,4")
    s += text(fx, oy + 18, "f₀", 13, GREEN, "middle", "bold")
    s += text(fx + 70, fy - 16, "Xc = XL → гасяться", 11.5, GREEN, "middle", "bold")
    s += text(ox + 0.2 * w, oy - h * 0.7, "ємнісно", 11, RED, "middle", style="italic")
    s += text(ox + 0.78 * w, oy - h * 0.7, "індуктивно", 11, COPP, "middle", style="italic")
    save("fig-9-5-1-crossing.svg", s)


# ── Рис. 9.5.2 — формула f₀ ──────────────────────────────────────────────────
def fig51_f0_formula():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 36, "Резонансна частота", 20, INK, "middle", "bold")
    cy = 140
    s += text(160, cy, "f₀", 32, INK, "middle", "bold")
    s += text(210, cy, "=", 28, INK, "middle")
    s += text(310, cy - 18, "1", 28, INK, "middle", "bold")
    s += line(255, cy + 2, 470, cy + 2, INK, 2.4)
    s += text(360, cy + 34, "2π · √(L·C)", 24, INK, "middle", "bold")
    s += arrow(360, cy + 70, 360, cy + 44, GREEN, 1.8)
    s += text(360, cy + 90, "↑ L·C → ↓ f₀ (повільніше гойдання)", 12, GREEN, "middle", "bold")
    s += rect(110, 232, W - 220, 48, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 254, "Залежить ТІЛЬКИ від добутку L·C — ні від опору, ні від амплітуди.",
              12, INK, "middle", "bold")
    s += text(W / 2, 272, "Під коренем: щоб подвоїти f₀, треба зменшити L·C вчетверо.", 10.5, GREY, "middle", style="italic")
    save("fig-9-5-2-f0-formula.svg", s)


# ── Рис. 9.5.3 — аналогія гойдалки ───────────────────────────────────────────
def fig51_swing_analogy():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Контур має власну частоту — як гойдалка", 19, INK, "middle", "bold")
    # гойдалка
    s += _frame(40, 70, 300, 210, "штовхай у такт f₀")
    px, py = 190, 95
    s += line(120, py, 260, py, INK, 3)
    ang = math.radians(22)
    bx, by = px + 100 * math.sin(ang), py + 100 * math.cos(ang)
    s += line(px - 7, py, bx - 7, by, GREY, 2)
    s += line(px + 7, py, bx + 7, by, GREY, 2)
    s += circle(bx, by + 8, 12, "#caa46e", "#9c7b46", 1.6)
    s += arrow(bx - 48, by, bx - 14, by, RED, 2.2)
    s += text(190, 268, "розмах росте лише на власній частоті", 10, GREY, "middle", style="italic")
    # крива резонансу
    s += _frame(400, 70, 300, 210, "відгук контуру")
    ox, oy, w, h = 440, 260, 240, 165
    s += _axes(ox, oy, w, h, "частота", "відгук")
    s += _peak(ox, oy, w, h, 0.5, 0.08, GREEN)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h, GREY, 1.2, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12.5, GREEN, "middle", "bold")
    save("fig-9-5-3-swing-analogy.svg", s)


# ── Рис. 9.5.4 — енергія гойдається між C і L ────────────────────────────────
def fig51_energy_slosh():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 34, "Енергія гойдається між полем C і полем L (на f₀)", 18, INK, "middle", "bold")
    phases = [("1", "уся в C", "E-поле", RED), ("2", "тече в L", "струм", COPP),
              ("3", "уся в L", "B-поле", COPP), ("4", "назад у C", "E-поле", RED)]
    for i, (n, t1, t2, col) in enumerate(phases):
        x = 40 + i * 180
        s += _frame(x, 70, 160, 180, "фаза " + n)
        cs, lx, rx = cap_sym(x + 50, 150, 22, 12)
        s += cs
        coil, (cl, cr) = coil_h(x + 110, 150, 44, 4, 14)
        s += coil
        s += line(x + 50 - 6, 122, x + 50 - 6, 110, INK, 1.6)
        s += line(x + 50 - 6, 110, cl, 110, INK, 1.6)
        s += line(cl, 110, cl, 136, INK, 1.6)
        s += line(x + 50 + 6, 178, x + 50 + 6, 190, INK, 1.6)
        s += line(x + 50 + 6, 190, cr, 190, INK, 1.6)
        s += line(cr, 190, cr, 164, INK, 1.6)
        if i in (0, 3):
            s += plus(x + 50 - 6, 140, 6, RED, 1.6)
            s += minus(x + 50 - 6, 162, 6, BLUE, 1.6)
        if i in (1, 2):
            s += arrow(cl, 150, cr, 150, COPP, 2)
        s += text(x + 80, 230, t1, 11, INK, "middle", "bold")
        s += text(x + 80, 246, t2, 9.5, col, "middle")
    s += text(W / 2, H - 8, "Пружина (C) ↔ маса (L): електричний маятник, що гойдається з частотою f₀.",
              10.5, GREY, "middle", style="italic")
    save("fig-9-5-4-energy-slosh.svg", s)


# ── Рис. 9.5.5 — послідовний резонанс ────────────────────────────────────────
def fig51_series_resonance():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 34, "Послідовний LC: на f₀ — мінімум опору, макс. струм", 17.5, INK, "middle", "bold")
    # схема
    s += line(70, 110, 110, 110, INK, 2)
    cs, lx, rx = cap_sym(125, 110, 16, 10)
    s += cs
    s += line(rx, 110, 175, 110, INK, 2)
    coil, (cl, cr) = coil_h(220, 110, 80, 5, 16)
    s += coil
    s += line(cr, 110, 320, 110, INK, 2)
    s += text(125, 138, "C", 11, INK, "middle", "bold")
    s += text(220, 138, "L", 11, INK, "middle", "bold")
    # Z(f): провал на f₀
    ox, oy, w, h = 380, 270, 300, 170
    s += _axes(ox, oy, w, h, "f", "|Z|")
    pts = []
    for j in range(0, int(w) + 1):
        f = j / w
        z = 0.15 + 0.8 * abs(f - 0.5) / 0.5
        pts.append((ox + j, oy - z * h))
    s += _poly(pts, BLUE, 2.6)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - 0.15 * h, GREY, 1.2, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12, GREEN, "middle", "bold")
    s += text(ox + 0.5 * w, oy - 0.15 * h - 8, "мінімум", 10.5, GREEN, "middle", "bold")
    save("fig-9-5-5-series-resonance.svg", s)


# ── Рис. 9.5.6 — паралельний резонанс ────────────────────────────────────────
def fig51_parallel_resonance():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 34, "Паралельний LC («бак»): на f₀ — максимум опору", 17.5, INK, "middle", "bold")
    # схема — бак
    s += line(80, 110, 80, 200, INK, 2)
    cs, lx, rx = cap_sym(130, 155, 22, 12)
    s += line(80, 110, 130, 110, INK, 2)
    s += line(130, 110, 130, 133, INK, 2)
    s += line(130, 177, 130, 200, INK, 2)
    s += line(80, 200, 130, 200, INK, 2)
    s += cs
    coil, (cl, cr) = coil_h(220, 155, 44, 4, 26)
    s += line(80, 110, 220, 110, INK, 2) if False else ""
    s += line(130, 110, 220, 110, INK, 2)
    s += line(220, 110, 220, 129, INK, 2)
    s += coil
    s += line(220, 181, 220, 200, INK, 2)
    s += line(130, 200, 220, 200, INK, 2)
    # циркулюючий струм
    s += f'<path d="M 150,140 A 40 30 0 1 1 200,140" fill="none" stroke="{GREEN}" stroke-width="1.8" marker-end="url(#aGreen)"/>\n'
    s += text(175, 120, "струм циркулює", 9.5, GREEN, "middle", "bold")
    s += text(175, 222, "C∥L", 11, INK, "middle", "bold")
    # Z(f): пік
    ox, oy, w, h = 380, 280, 300, 180
    s += _axes(ox, oy, w, h, "f", "|Z|")
    s += _peak(ox, oy, w, h, 0.5, 0.08, RED, 2.6)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h, GREY, 1.2, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12, GREEN, "middle", "bold")
    s += text(ox + 0.5 * w, oy - h - 2, "максимум", 10.5, RED, "middle", "bold")
    save("fig-9-5-6-parallel-resonance.svg", s)


# ── Рис. 9.5.7 — налаштування ────────────────────────────────────────────────
def fig51_tuning():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Змінюючи C, зсувають f₀ — це й є налаштування", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 270, 520, 190
    s += _axes(ox, oy, w, h, "частота", "відгук")
    for fc, col, dash in [(0.3, GREY, "4,4"), (0.5, GREEN, None), (0.72, GREY, "4,4")]:
        pts = []
        for j in range(0, int(w) + 1):
            f = j / w
            a = math.exp(-((f - fc) / 0.05) ** 2)
            pts.append((ox + j, oy - a * h * 0.9))
        s += _poly(pts, col, 2.6 if col == GREEN else 1.8, dash)
    s += arrow(ox + 0.3 * w, oy - h * 0.55, ox + 0.72 * w, oy - h * 0.55, INK, 1.8)
    s += text(ox + 0.5 * w, oy - h * 0.62, "крутиш C → f₀ повзе", 11, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Коли f₀ збігається з частотою станції — вона виринає гучно й чисто.",
              11, GREY, "middle", style="italic")
    save("fig-9-5-7-tuning.svg", s)


def _decay_sine(ox, oy, w, amp, cycles, k, col, wv=2.2):
    pts = []
    for j in range(0, int(w) + 1):
        t = j / w
        y = oy - amp * math.exp(-k * t) * math.sin(2 * math.pi * cycles * t)
        pts.append((ox + j, y))
    return _poly(pts, col, wv)


# ── Рис. 9.6.1 — криві для різних Q ──────────────────────────────────────────
def fig61_q_curves():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Висока Q — гострий пік; низька — розмитий", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 290, 520, 220
    s += _axes(ox, oy, w, h, "частота", "відгук")
    s += _peak(ox, oy, w, h * 0.95, 0.5, 0.03, GREEN, 2.8)
    s += _peak(ox, oy, w, h * 0.6, 0.5, 0.07, "#9c7b46", 2.4)
    s += _peak(ox, oy, w, h * 0.35, 0.5, 0.15, RED, 2.2)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h, GREY, 1, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12, GREEN, "middle", "bold")
    s += text(ox + 0.5 * w + 10, oy - h * 0.9, "висока Q", 11.5, GREEN, "start", "bold")
    s += text(ox + 0.78 * w, oy - h * 0.3, "низька Q", 11.5, RED, "start", "bold")
    s += text(W / 2, H - 12, "f₀ незмінна (її задає L·C); Q керує лише гостротою піка.",
              11, GREY, "middle", style="italic")
    save("fig-9-6-1-q-curves.svg", s)


# ── Рис. 9.6.2 — смуга й Q = f₀/Δf ───────────────────────────────────────────
def fig61_bandwidth():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Смуга Δf і добротність Q = f₀/Δf", 19, INK, "middle", "bold")
    ox, oy, w, h = 110, 290, 520, 220
    s += _axes(ox, oy, w, h, "частота", "відгук")
    s += _peak(ox, oy, w, h * 0.92, 0.5, 0.07, GREEN, 2.8)
    # рівень -3dB ~0.707
    lvl = oy - h * 0.92 * 0.707
    s += line(ox, lvl, ox + w, lvl, RED, 1.4, dash="5,4")
    s += text(ox + w, lvl - 6, "−3 дБ (0.707)", 10.5, RED, "end", "bold")
    # межі смуги (де крива = 0.707 від max): для exp(-(d/0.07)^2)=0.707 → d≈0.07·0.59
    d = 0.07 * 0.589
    s += line(ox + (0.5 - d) * w, oy, ox + (0.5 - d) * w, lvl, GREY, 1, dash="3,3")
    s += line(ox + (0.5 + d) * w, oy, ox + (0.5 + d) * w, lvl, GREY, 1, dash="3,3")
    s += arrow(ox + (0.5 - d) * w, oy - h * 0.45, ox + (0.5 + d) * w, oy - h * 0.45, INK, 1.6)
    s += arrow(ox + (0.5 + d) * w, oy - h * 0.45, ox + (0.5 - d) * w, oy - h * 0.45, INK, 1.6)
    s += text(ox + 0.5 * w, oy - h * 0.52, "Δf", 12, INK, "middle", "bold")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Q = f₀/Δf : при f₀=1 МГц і Q=100 смуга Δf=10 кГц.", 11, GREY, "middle", style="italic")
    save("fig-9-6-2-bandwidth.svg", s)


# ── Рис. 9.6.3 — Q і опір ────────────────────────────────────────────────────
def fig61_q_and_r():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 34, "Менший опір — вища Q (опір гасить, як тертя)", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 270, 520, 190
    s += _axes(ox, oy, w, h, "частота", "відгук")
    s += _peak(ox, oy, w, h * 0.92, 0.5, 0.035, GREEN, 2.6)
    s += _peak(ox, oy, w, h * 0.4, 0.5, 0.14, RED, 2.4)
    s += text(ox + 0.5 * w + 10, oy - h * 0.9, "малий R → висока Q", 11, GREEN, "start", "bold")
    s += text(ox + 0.78 * w, oy - h * 0.32, "великий R → низька Q", 10.5, RED, "start", "bold")
    s += text(W / 2, H - 12, "Q = ω₀L/R на резонансі: опір з'їдає енергію коливань і розмиває пік.",
              11, GREY, "middle", style="italic")
    save("fig-9-6-3-q-and-r.svg", s)


# ── Рис. 9.6.4 — Q як запас/втрати ───────────────────────────────────────────
def fig61_energy_def():
    W, H = 700, 280
    s = header(W, H)
    s += text(W / 2, 34, "Глибший сенс Q: запас проти втрат за цикл", 18, INK, "middle", "bold")
    cx, cy = 250, 150
    s += circle(cx, cy, 60, "#eef6ef", GREEN, 2)
    s += f'<path d="M {cx-30},{cy-45} A 55 55 0 1 1 {cx+45},{cy-30}" fill="none" stroke="{GREEN}" stroke-width="2.4" marker-end="url(#aGreen)"/>\n'
    s += text(cx, cy - 4, "запасена", 12, INK, "middle", "bold")
    s += text(cx, cy + 14, "енергія", 12, INK, "middle", "bold")
    s += arrow(cx + 60, cy, cx + 110, cy, RED, 2)
    s += text(cx + 130, cy - 4, "малі втрати", 11, RED, "start", "bold")
    s += text(cx + 130, cy + 12, "за цикл (в опорі)", 10, GREY, "start")
    s += rect(80, 220, W - 160, 44, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, 240, "Q = 2π · (запасена енергія) / (втрачена за цикл).", 12.5, INK, "middle", "bold")
    s += text(W / 2, 257, "Багато запасу, мало втрат → гострий резонанс, довгий дзвін.", 10.5, GREY, "middle", style="italic")
    save("fig-9-6-4-energy-def.svg", s)


# ── Рис. 9.6.5 — дзвін у часі ────────────────────────────────────────────────
def fig61_ringing():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Q у часі: високе дзвенить довго, низьке згасає швидко", 17, INK, "middle", "bold")
    # високе Q
    s += _frame(40, 70, 320, 210, "висока Q — дзвінкий")
    ox, oy, w = 60, 175, 280
    s += line(ox, oy, ox + w, oy, GREY, 1)
    s += _decay_sine(ox, oy, w, 75, 6, 0.5, GREEN)
    s += text(200, 262, "багато коливань після поштовху", 10, GREY, "middle", style="italic")
    # низьке Q
    s += _frame(400, 70, 280, 210, "низька Q — глухий")
    ox2 = 420
    s += line(ox2, oy, ox2 + 240, oy, GREY, 1)
    s += _decay_sine(ox2, oy, 240, 75, 6, 3.0, RED)
    s += text(540, 262, "згасає за кілька циклів", 10, GREY, "middle", style="italic")
    save("fig-9-6-5-ringing.svg", s)


# ── Рис. 9.6.6 — компроміс вибірковість/смуга ────────────────────────────────
def fig61_tradeoff():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 34, "Компроміс: гостро (вузько) чи широко", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 280, 520, 200
    s += _axes(ox, oy, w, h, "частота", "відгук")
    # смуга сигналу (прямокутник)
    s += rect(ox + 0.42 * w, oy - h * 0.7, 0.16 * w, h * 0.7, "#eef2f6", "#9bb0c2", 1.2)
    s += text(ox + 0.5 * w, oy - h * 0.74, "смуга сигналу", 9.5, INK, "middle", "bold")
    # висока Q (вузька, обрізає сигнал)
    s += _peak(ox, oy, w, h * 0.92, 0.5, 0.03, GREEN, 2.4)
    s += text(ox + 0.5 * w + 8, oy - h * 0.9, "висока Q: обрізає", 10, GREEN, "start", "bold")
    # низька Q (широка, ловить сусідів)
    s += _peak(ox, oy, w, h * 0.55, 0.5, 0.14, RED, 2.2)
    s += text(ox + 0.8 * w, oy - h * 0.35, "низька Q: ловить сусідів", 9.5, RED, "start", "bold")
    s += text(W / 2, H - 12, "Q добирають так, щоб смуга вмістила сигнал, але відсіяла сусідні частоти.",
              11, GREY, "middle", style="italic")
    save("fig-9-6-6-tradeoff.svg", s)


# ── Рис. 9.6.7 — кварц ───────────────────────────────────────────────────────
def fig61_quartz():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 34, "Кварц: добротність у тисячі разів вища за LC", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 240, 520, 160
    s += _axes(ox, oy, w, h, "частота", "відгук")
    s += _peak(ox, oy, w, h * 0.65, 0.5, 0.13, "#9c7b46", 2.4)
    s += text(ox + 0.74 * w, oy - h * 0.45, "LC (Q ~ 100)", 11, "#9c7b46", "start", "bold")
    s += _peak(ox, oy, w, h * 0.95, 0.5, 0.012, GREEN, 2.8)
    s += text(ox + 0.5 * w + 8, oy - h * 0.9, "кварц (Q ~ 10000+)", 11, GREEN, "start", "bold")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Гранично гострий, стабільний резонанс — звідси точний час годинників і процесорів.",
              11, GREY, "middle", style="italic")
    save("fig-9-6-7-quartz.svg", s)


# ── допоміжне для §9.7 (фільтри) ─────────────────────────────────────────────
def _gnd(x, y, col=INK):
    s = line(x, y, x, y + 8, col, 2)
    s += line(x - 11, y + 8, x + 11, y + 8, col, 2)
    s += line(x - 7, y + 12, x + 7, y + 12, col, 2)
    s += line(x - 3, y + 16, x + 3, y + 16, col, 2)
    return s


def _resbox(x, y, w_, h_, label="R", col=INK):
    s = rect(x, y, w_, h_, "#ffffff", col, 2)
    s += text(x + w_ / 2, y + h_ / 2 + 5, label, 13, col, "middle", "bold")
    return s


def _capgnd(cx, cy, col=INK):
    s = line(cx - 13, cy, cx + 13, cy, col, 2.6)
    s += line(cx - 13, cy + 7, cx + 13, cy + 7, col, 2.6)
    return s


def _curvef(ox, oy, w, h, yf, col, wv=2.6, n=180):
    pts = [(ox + j / n * w, oy - h * yf(j / n)) for j in range(n + 1)]
    return _poly(pts, col, wv)


def _lp(x):
    r = 10 ** ((x - 0.5) * 3)
    return 1 / math.sqrt(1 + r * r)


def _hp(x):
    r = 10 ** ((x - 0.5) * 3)
    return r / math.sqrt(1 + r * r)


def _nf(x):
    return 1 - 0.96 * math.exp(-((x - 0.5) / 0.05) ** 2)


# ── Рис. 9.7.1 — RC фільтр низьких частот ────────────────────────────────────
def fig71_rc_lowpass():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 32, "Фільтр низьких частот (RC): пропускає низ, ріже верх", 18, INK, "middle", "bold")
    yw = 150
    s += text(55, 136, "вхід", 11, GREY, "middle")
    s += circle(60, yw, 3, INK, INK)
    s += line(60, yw, 100, yw, INK, 2)
    s += _resbox(100, yw - 15, 64, 30, "R")
    s += line(164, yw, 255, yw, INK, 2)
    s += circle(255, yw, 3, INK, INK)
    s += line(255, yw, 305, yw, INK, 2)
    s += circle(305, yw, 3, INK, INK)
    s += text(312, yw + 4, "вихід", 11, GREY, "start")
    s += line(255, yw, 255, yw + 30, INK, 2)
    s += _capgnd(255, yw + 30)
    s += text(274, yw + 33, "C", 12, INK, "start", "bold")
    s += line(255, yw + 37, 255, yw + 47, INK, 2)
    s += _gnd(255, yw + 47)
    ox, oy, w, h = 400, 250, 270, 165
    s += _axes(ox, oy, w, h, "частота", "вихід")
    s += _curvef(ox, oy, w, h * 0.95, _lp, GREEN, 2.8)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h, GREY, 1, dash="4,4")
    s += text(ox + 0.5 * w, oy + 15, "fc", 11, RED, "middle", "bold")
    s += text(ox + 0.2 * w, oy - h * 0.85, "проходить", 10.5, GREEN, "middle", "bold")
    s += text(ox + 0.82 * w, oy - h * 0.18, "гаситься", 10.5, RED, "middle", "bold")
    save("fig-9-7-1-rc-lowpass.svg", s)


# ── Рис. 9.7.2 — частота зрізу ───────────────────────────────────────────────
def fig71_cutoff():
    W, H = 700, 330
    s = header(W, H)
    s += text(W / 2, 32, "Частота зрізу fc: де Xc = R, вихід = 0.707 (−3 дБ)", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 270, 500, 200
    s += _axes(ox, oy, w, h, "частота", "вихід")
    s += _curvef(ox, oy, w, h * 0.95, _lp, GREEN, 2.8)
    lvl = oy - h * 0.95 * 0.707
    s += line(ox, lvl, ox + w, lvl, RED, 1.4, dash="5,4")
    s += text(ox + w, lvl - 6, "0.707 (−3 дБ)", 10.5, RED, "end", "bold")
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, lvl, GREY, 1, dash="3,3")
    s += text(ox + 0.5 * w, oy + 16, "fc = 1/(2πRC)", 11, RED, "middle", "bold")
    s += text(ox + 0.2 * w, oy - h * 0.85, "смуга пропускання", 10.5, GREEN, "middle", "bold")
    s += text(ox + 0.84 * w, oy - h * 0.2, "спад 6 дБ/окт", 10, GREY, "middle", "bold")
    s += text(W / 2, H - 12, "На fc реактивний опір конденсатора дорівнює опору резистора.", 11, GREY, "middle", style="italic")
    save("fig-9-7-2-cutoff.svg", s)


# ── Рис. 9.7.3 — RC фільтр високих частот ────────────────────────────────────
def fig71_rc_highpass():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 32, "Фільтр високих частот (RC): дзеркало — пропускає верх", 18, INK, "middle", "bold")
    yw = 150
    s += text(55, 136, "вхід", 11, GREY, "middle")
    s += circle(60, yw, 3, INK, INK)
    s += line(60, yw, 110, yw, INK, 2)
    cs, lx, rx = cap_sym(120, yw, 13, 9)
    s += cs
    s += line(110, yw, lx, yw, INK, 2)
    s += line(rx, yw, 255, yw, INK, 2)
    s += text(120, yw - 22, "C", 12, INK, "middle", "bold")
    s += circle(255, yw, 3, INK, INK)
    s += line(255, yw, 305, yw, INK, 2)
    s += circle(305, yw, 3, INK, INK)
    s += text(312, yw + 4, "вихід", 11, GREY, "start")
    s += line(255, yw, 255, yw + 22, INK, 2)
    s += _resbox(255 - 16, yw + 22, 32, 40, "R")
    s += line(255, yw + 62, 255, yw + 70, INK, 2)
    s += _gnd(255, yw + 70)
    ox, oy, w, h = 400, 250, 270, 165
    s += _axes(ox, oy, w, h, "частота", "вихід")
    s += _curvef(ox, oy, w, h * 0.95, _hp, BLUE, 2.8)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h, GREY, 1, dash="4,4")
    s += text(ox + 0.5 * w, oy + 15, "fc", 11, RED, "middle", "bold")
    s += text(ox + 0.2 * w, oy - h * 0.18, "гаситься", 10.5, RED, "middle", "bold")
    s += text(ox + 0.82 * w, oy - h * 0.85, "проходить", 10.5, BLUE, "middle", "bold")
    save("fig-9-7-3-rc-highpass.svg", s)


# ── Рис. 9.7.4 — смуговий RLC ────────────────────────────────────────────────
def fig71_bandpass_rlc():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 32, "Смуговий фільтр (RLC): пропускає смугу навколо f₀", 18, INK, "middle", "bold")
    yw = 140
    s += text(48, 126, "вхід", 11, GREY, "middle")
    s += circle(55, yw, 3, INK, INK)
    s += line(55, yw, 80, yw, INK, 2)
    cl, (lx0, lx1) = coil_h(120, yw, 80, 5, 11)
    s += cl
    s += text(120, yw - 22, "L", 12, COPP, "middle", "bold")
    cs, clx, crx = cap_sym(220, yw, 13, 9)
    s += line(lx1, yw, clx, yw, INK, 2)
    s += cs
    s += text(220, yw - 20, "C", 12, INK, "middle", "bold")
    s += line(crx, yw, 290, yw, INK, 2)
    s += circle(290, yw, 3, INK, INK)
    s += text(297, yw + 4, "вихід", 11, GREY, "start")
    s += line(290, yw, 290, yw + 20, INK, 2)
    s += _resbox(290 - 16, yw + 20, 32, 38, "R")
    s += line(290, yw + 58, 290, yw + 66, INK, 2)
    s += _gnd(290, yw + 66)
    ox, oy, w, h = 410, 260, 270, 175
    s += _axes(ox, oy, w, h, "частота", "вихід")
    s += _peak(ox, oy, w, h * 0.92, 0.5, 0.08, GREEN, 2.8)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h * 0.92, GREY, 1, dash="4,4")
    s += text(ox + 0.5 * w, oy + 15, "f₀", 11, GREEN, "middle", "bold")
    s += text(ox + 0.5 * w, oy - h * 0.99, "Δf = f₀/Q", 10.5, INK, "middle", "bold")
    save("fig-9-7-4-bandpass-rlc.svg", s)


# ── Рис. 9.7.5 — режекторний ─────────────────────────────────────────────────
def fig71_notch():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 32, "Режекторний фільтр: вирізає вузьку смугу навколо f₀", 18, INK, "middle", "bold")
    ox, oy, w, h = 110, 250, 500, 180
    s += _axes(ox, oy, w, h, "частота", "вихід")
    s += _curvef(ox, oy, w, h * 0.92, _nf, RED, 2.8)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - h * 0.25, GREY, 1, dash="4,4")
    s += text(ox + 0.5 * w, oy + 16, "f₀", 11, RED, "middle", "bold")
    s += text(ox + 0.2 * w, oy - h * 0.8, "проходить", 10.5, GREEN, "middle", "bold")
    s += text(ox + 0.8 * w, oy - h * 0.8, "проходить", 10.5, GREEN, "middle", "bold")
    s += text(ox + 0.5 * w + 4, oy - h * 0.12, "провал", 9.5, RED, "start", "bold")
    s += text(W / 2, H - 12, "Дзеркало смугового: усе проходить, окрім вузької смуги навколо f₀.", 11, GREY, "middle", style="italic")
    save("fig-9-7-5-notch.svg", s)


# ── Рис. 9.7.6 — чотири типи ─────────────────────────────────────────────────
def fig71_four_types():
    W, H = 720, 430
    s = header(W, H)
    s += text(W / 2, 32, "Чотири типи фільтрів — одна ідея", 19, INK, "middle", "bold")

    def panel(px, py, fn, col, title):
        ow, oh = 260, 120
        t = _axes(px, py + oh, ow, oh, "f", "")
        if fn == "peak":
            t += _peak(px, py + oh, ow, oh * 0.9, 0.5, 0.09, col, 2.6)
        else:
            t += _curvef(px, py + oh, ow, oh * 0.9, fn, col, 2.6)
        t += text(px + ow / 2, py - 6, title, 12.5, col, "middle", "bold")
        return t

    s += panel(70, 90, _lp, GREEN, "Низьких частот (ФНЧ)")
    s += panel(390, 90, _hp, BLUE, "Високих частот (ФВЧ)")
    s += panel(70, 270, "peak", GREEN, "Смуговий (BPF)")
    s += panel(390, 270, _nf, RED, "Режекторний (notch)")
    save("fig-9-7-6-four-types.svg", s)


# ── Рис. 9.7.7 — суть вибірковості ───────────────────────────────────────────
def fig71_selectivity_apps():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 32, "Суть вибірковості: з мішанини частот лишити одну смугу", 18, INK, "middle", "bold")
    by = 200
    hs = [30, 55, 20, 70, 40, 90, 35, 60, 25, 50, 45, 80, 30]
    bx = 60
    for i, hh in enumerate(hs):
        x = bx + i * 13
        s += line(x, by, x, by - hh, GREY, 2.4)
    s += line(bx - 4, by, bx + 12 * 13 + 4, by, INK, 1.4)
    s += text(bx + 78, by + 24, "вхід: усе підряд", 11, GREY, "middle")
    s += rect(300, 118, 120, 70, LGRN, GREEN, 2, 8)
    s += text(360, 148, "смуговий", 12, INK, "middle", "bold")
    s += text(360, 166, "фільтр", 12, INK, "middle", "bold")
    s += arrow(266, 153, 300, 153, INK, 2)
    s += arrow(420, 153, 458, 153, INK, 2)
    ox2 = 470
    for i, hh in enumerate(hs):
        x = ox2 + i * 13
        if 4 <= i <= 6:
            s += line(x, by, x, by - hh, GREEN, 2.6)
    s += line(ox2 - 4, by, ox2 + 12 * 13 + 4, by, INK, 1.4)
    s += text(ox2 + 78, by + 24, "вихід: одна смуга", 11, GREEN, "middle", "bold")
    save("fig-9-7-7-selectivity-apps.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  📜 історія до §9.6 — Такома-Нерроуз
# ─────────────────────────────────────────────────────────────────────────────
def fig6i1_resonance_vs_flutter():
    W, H = 840, 560
    s = header(W, H)
    s += text(W / 2, 34, "Два способи розгойдати міст: вимушений резонанс і флатер", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "резонанс вимагає ритмічного поштовху точно в такт; флатеру досить рівного вітру",
              12.5, GREY, "middle", style="italic")
    # ліва панель: резонанс
    s += _frame(50, 90, 360, 400, "РЕЗОНАНС: вимушені коливання")
    cx = 230
    s += line(cx, 120, cx, 180, INK, 2)
    s += circle(cx + 38, 196, 14, "#d9d9dd", INK, 2)
    s += line(cx, 120, cx + 38, 196 - 12, INK, 2)
    for k in range(3):
        s += arrow(140 + k * 0, 190 - k * 12, 178 + k * 0, 190 - k * 12, RED, 2)
    s += text(120, 156, "ритмічні", 11, RED, "middle", "bold")
    s += text(120, 172, "поштовхи", 11, RED, "middle", "bold")
    s += text(230, 232, "сила ззовні мусить ВЛУЧИТИ в f₀", 11.5, INK, "middle", "bold")
    # графік: амплітуда від частоти сили
    ox, oy, w, h = 90, 450, 280, 150
    s += _axes(ox, oy, w, h, "частота поштовхів", "розмах")
    pts = []
    for j in range(0, 201):
        f = j / 200.0
        a = 1.0 / math.sqrt(1 + ((f - 0.5) / 0.06) ** 2)
        pts.append((ox + f * w, oy - 0.85 * h * a))
    s += _poly(pts, RED, 2.4)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - 0.85 * h, GREY, 1.2, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f₀", 12, INK, "middle", "bold")
    s += text(ox + w / 2, oy - h - 4, "не влучив у частоту — нічого не буде", 10.5, GREY, "middle", style="italic")
    # права панель: флатер
    s += _frame(430, 90, 360, 400, "ФЛАТЕР: самозбудження")
    # рівний потік
    for k in range(4):
        s += arrow(450, 130 + k * 26, 510, 130 + k * 26, GREEN, 2)
    s += text(480, 116, "РІВНИЙ вітер, без жодного ритму", 11, GREEN, "middle", "bold")
    # профіль моста, що крутиться
    bx, by = 640, 165
    s += f'<g transform="rotate(-12 {bx} {by})">\n'
    s += rect(bx - 70, by - 8, 140, 16, "#9aa0a6", "#5c6066", 2, 3)
    s += f'</g>\n'
    s += f'<path d="M {bx + 86},{by - 30} A 40 40 0 0 1 {bx + 86},{by + 30}" fill="none" stroke="{RED}" stroke-width="2" marker-end="url(#aRed)"/>\n'
    # петля зворотного зв'язку
    fy = 250
    s += text(610, fy, "рух змінює кут атаки", 11.5, INK, "middle", "bold")
    s += arrow(610, fy + 8, 610, fy + 30, GREY, 1.6)
    s += text(610, fy + 46, "вітер дає силу В ТАКТ руху", 11.5, INK, "middle", "bold")
    s += arrow(610, fy + 54, 610, fy + 76, GREY, 1.6)
    s += text(610, fy + 92, "розмах росте → і так по колу", 11.5, "#9a2b22", "middle", "bold")
    s += f'<path d="M 730,{fy + 88} C 770,{fy + 60} 770,{fy + 20} 730,{fy - 6}" fill="none" stroke="{RED}" stroke-width="1.8" marker-end="url(#aRed)" stroke-dasharray="5,4"/>\n'
    # графік: амплітуда від швидкості вітру
    ox2, oy2 = 470, 450
    s += _axes(ox2, oy2, w, h, "швидкість вітру", "розмах")
    vcrit = 0.55
    pts = []
    for j in range(0, 201):
        v = j / 200.0
        a = 0.04 if v < vcrit else 0.04 + 0.9 * ((v - vcrit) / (1 - vcrit)) ** 1.5
        pts.append((ox2 + v * w, oy2 - 0.85 * h * min(a, 1.0)))
    s += _poly(pts, RED, 2.4)
    s += line(ox2 + vcrit * w, oy2, ox2 + vcrit * w, oy2 - 0.85 * h, GREY, 1.2, dash="4,4")
    s += text(ox2 + vcrit * w, oy2 + 18, "критична швидкість", 10.5, INK, "middle", "bold")
    s += text(ox2 + w / 2, oy2 - h - 4, "вище порога розмах росте з вітром монотонно", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 534, "у Такоми вихори зривалися з частотою ~1 Гц, а міст крутився на 0.2 Гц — «резонанс» не сходиться навіть арифметично",
              11.5, GREY, "middle", style="italic")
    save("fig-9-6i-1-resonance-vs-flutter.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  ⚙️ вставка до §9.4 — фігури Ліссажу
# ─────────────────────────────────────────────────────────────────────────────
def _liss(cx, cy, r, fx, fy, phi, col, wv=2.2):
    pts = []
    for j in range(0, 401):
        t = j / 400.0 * 2 * math.pi
        pts.append((cx + r * math.sin(fx * t), cy - r * math.sin(fy * t + phi)))
    return _poly(pts, col, wv)


def fig4a1_liss_gallery():
    W, H = 840, 480
    s = header(W, H)
    s += text(W / 2, 34, "Фаза стає формою: галерея фігур Ліссажу (однакові частоти)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "X — перший сигнал, Y — другий; форма петлі читається з одного погляду",
              12.5, GREY, "middle", style="italic")
    cells = ((0, "0°: пряма"), (math.pi / 4, "45°: похилий еліпс"), (math.pi / 2, "90°: коло"),
             (3 * math.pi / 4, "135°"), (math.pi, "180°: зворотна пряма"))
    for i, (phi, lab) in enumerate(cells):
        cx = 110 + i * 158
        cy = 180
        s += rect(cx - 62, cy - 62, 124, 124, "#fbfbfb", "#d8d8d8", 1.2, 6)
        s += line(cx - 62, cy, cx + 62, cy, FAINT, 1)
        s += line(cx, cy - 62, cx, cy + 62, FAINT, 1)
        s += _liss(cx, cy, 46, 1, 1, phi, COPP)
        s += text(cx, cy + 84, lab, 11, INK, "middle", "bold")
    # як зчитати кут
    cx, cy, r = 240, 380, 52
    s += rect(cx - 66, cy - 66, 132, 132, "#fbfbfb", "#d8d8d8", 1.2, 6)
    s += line(cx - 66, cy, cx + 66, cy, FAINT, 1)
    s += line(cx, cy - 66, cx, cy + 66, FAINT, 1)
    phi0 = math.radians(35)
    s += _liss(cx, cy, r, 1, 1, phi0, COPP)
    y0 = r * math.sin(phi0)
    s += arrow(cx + 40, cy - y0, cx + 4, cy - y0, GREEN, 1.8)
    s += line(cx, cy, cx, cy - y0, GREEN, 3)
    s += text(cx + 46, cy - y0 + 4, "Y₀ (перетин осі)", 10.5, GREEN, "start", "bold")
    s += line(cx, cy, cx, cy - r, BLUE, 1.6, dash="4,3")
    s += text(cx + 6, cy - r - 6, "B (повний розмах)", 10.5, BLUE, "start", "bold")
    s += text(520, 350, "кут читається без осцилографа-лінійки:", 13, INK, "start", "bold")
    s += text(520, 380, "sin φ = Y₀ / B", 16, GREEN, "start", "bold")
    s += text(520, 410, "напрям обходу петлі каже, ХТО випереджає:", 12, INK, "start")
    s += text(520, 428, "проти годинникової — Y попереду (ICE/ELI з §2.3.4)", 12, INK, "start")
    save("fig-9-4a-1-liss-gallery.svg", s)


def fig4a2_liss_ratios():
    W, H = 800, 400
    s = header(W, H)
    s += text(W / 2, 34, "Бонус: різні частоти малюють вузли — і їх можна порахувати", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "відношення частот = відношення кількості дотиків фігури до горизонтальної й вертикальної рамок",
              12, GREY, "middle", style="italic")
    cells = ((1, 1, "1 : 1"), (2, 1, "2 : 1"), (3, 2, "3 : 2"))
    for i, (fx, fy, lab) in enumerate(cells):
        cx = 160 + i * 240
        cy = 200
        s += rect(cx - 80, cy - 80, 160, 160, "#fbfbfb", "#d8d8d8", 1.2, 6)
        s += _liss(cx, cy, 62, fx, fy, math.pi / 2, COPP)
        s += text(cx, cy + 104, f"f_x : f_y = {lab}", 12.5, INK, "middle", "bold")
    s += text(W / 2, 348, "так до епохи частотомірів звіряли генератор з еталоном: стабільна нерухома фігура = частоти кратні точно",
              11.5, GREY, "middle", style="italic")
    save("fig-9-4a-2-liss-ratios.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  ⚙️ вставка до §9.5 — пошук резонансу свіпом
# ─────────────────────────────────────────────────────────────────────────────
def fig5a1_sweep_setup():
    W, H = 820, 540
    s = header(W, H)
    s += text(W / 2, 34, "Свіп: спитати в контуру, де його резонанс", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "крокуємо частотою, міряємо відгук — максимум і є f₀, ширина піка дає Q",
              12.5, GREY, "middle", style="italic")
    # установка
    y = 140
    s += circle(100, y, 22, "#fff", INK, 2)
    pts = [(100 - 13 + 26 * t / 100, y - 8 * math.sin(2 * math.pi * 1.5 * t / 100)) for t in range(0, 101)]
    s += _poly(pts, INK, 1.6)
    s += text(100, y + 42, "генератор", 11, INK, "middle", "bold")
    s += text(100, y + 58, "(частота керується)", 9.5, GREY, "middle")
    s += line(122, y, 170, y, INK, 2.2)
    s += rect(170, y - 9, 64, 18, "#f3f3f3", INK, 1.6)
    s += text(202, y - 16, "R великий", 10, INK, "middle", "bold")
    s += text(202, y + 30, "слабкий зв'язок:", 9.5, GREY, "middle")
    s += text(202, y + 44, "не «садити» Q", 9.5, GREY, "middle")
    s += line(234, y, 300, y, INK, 2.2)
    s += circle(300, y, 3.5, INK, INK, 0)
    # контур L||C
    cs, t_, b_ = cap_sym(300, y + 52, 13, 8)
    s += line(300, y, 300, y + 43, INK, 1.8)
    s += cs
    s += line(300, y + 61, 300, y + 100, INK, 1.8)
    for k in range(3):
        ya = y + 14 + k * 26
        s += f'<path d="M 360,{ya} A 13 13 0 0 1 360,{ya + 26}" fill="none" stroke="{COPP}" stroke-width="2.4"/>\n'
    s += line(360, y, 360, y + 14, INK, 1.8)
    s += line(300, y, 360, y, INK, 1.8)
    s += line(360, y + 92, 360, y + 100, INK, 1.8)
    s += line(300, y + 100, 360, y + 100, INK, 1.8)
    s += text(330, y + 122, "контур", 10.5, INK, "middle", "bold")
    # детектор
    s += line(360, y, 470, y, INK, 2.2)
    s += rect(470, y - 22, 140, 44, LGRN, GREEN, 1.8, 6)
    s += text(540, y - 2, "детектор амплітуди", 10.5, INK, "middle", "bold")
    s += text(540, y + 14, "(АЦП / осцилограф)", 9.5, GREY, "middle")
    s += text(700, y, "→ A[f]", 13, GREEN, "start", "bold")
    # результат свіпу
    ox, oy, w, h = 120, 470, 580, 200
    s += _axes(ox, oy, w, h, "частота f", "амплітуда A")
    f0, bw = 0.52, 0.07
    pts = []
    for j in range(0, 201):
        f = j / 200.0
        a = 1.0 / math.sqrt(1 + ((f - f0) / (bw / 2)) ** 2)
        pts.append((ox + f * w, oy - 0.88 * h * a))
    s += _poly(pts, COPP, 2.6)
    for j in range(0, 21):
        f = j / 20.0
        a = 1.0 / math.sqrt(1 + ((f - f0) / (bw / 2)) ** 2)
        s += circle(ox + f * w, oy - 0.88 * h * a, 3.2, GREEN, GREEN, 0)
    s += line(ox + f0 * w, oy, ox + f0 * w, oy - 0.88 * h, GREY, 1.2, dash="4,4")
    s += text(ox + f0 * w, oy + 20, "f₀ = argmax", 12, RED, "middle", "bold")
    lvl = 0.88 * 0.707
    s += line(ox, oy - lvl * h, ox + w, oy - lvl * h, GREY, 1.2, dash="6,5")
    s += text(ox + w + 6, oy - lvl * h + 4, "0.707·A_max", 10.5, GREY, "start")
    f1 = f0 - bw / 2
    f2 = f0 + bw / 2
    for fx in (f1, f2):
        s += line(ox + fx * w, oy - lvl * h, ox + fx * w, oy - lvl * h - 16, GREY, 1.4)
    s += text(ox + f0 * w, oy - lvl * h - 24, "Δf → Q = f₀/Δf", 11.5, INK, "middle", "bold")
    s += text(ox + 0.13 * w, oy - 0.4 * h, "зелені точки —", 10.5, GREY, "middle")
    s += text(ox + 0.13 * w, oy - 0.4 * h + 14, "кроки свіпу", 10.5, GREY, "middle")
    save("fig-9-5a-1-sweep-setup.svg", s)


def fig5a2_sweep_pitfalls():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 34, "Дві пастки свіпу: поспіх і меандр", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "контур розгойдується ~Q періодів — і чує не лише основну частоту генератора",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 360, 600, 250
    s += _axes(ox, oy, w, h, "частота f", "амплітуда")
    f0, bw = 0.6, 0.06
    # чесний пік
    pts = []
    for j in range(0, 201):
        f = j / 200.0
        a = 1.0 / math.sqrt(1 + ((f - f0) / (bw / 2)) ** 2)
        pts.append((ox + f * w, oy - 0.85 * h * a))
    s += _poly(pts, COPP, 2.6)
    s += text(ox + f0 * w + 14, oy - 0.85 * h, "повільний свіп: чесний пік", 11.5, COPP, "start", "bold")
    # розмазаний пік (швидкий свіп)
    pts = []
    for j in range(0, 201):
        f = j / 200.0
        a = 0.45 / math.sqrt(1 + ((f - (f0 + 0.05)) / (bw * 1.8)) ** 2)
        pts.append((ox + f * w, oy - 0.85 * h * a))
    s += _poly(pts, RED, 2.2, dash="6,4")
    s += text(ox + (f0 + 0.10) * w, oy - 0.32 * h, "швидкий свіп: пік нижчий,", 11, "#9a2b22", "start", "bold")
    s += text(ox + (f0 + 0.10) * w, oy - 0.32 * h + 15, "ширший і зсунутий", 11, "#9a2b22", "start", "bold")
    # гармоніка меандра
    pts = []
    fg = f0 / 3
    for j in range(0, 201):
        f = j / 200.0
        a = 0.3 / math.sqrt(1 + ((f - fg) / (bw / 2)) ** 2)
        pts.append((ox + f * w, oy - 0.85 * h * a))
    s += _poly(pts, BLUE, 2, dash="3,4")
    s += text(ox + fg * w, oy - 0.36 * h, "«привид» на f₀/3:", 11, "#27447e", "middle", "bold")
    s += text(ox + fg * w, oy - 0.36 * h + 15, "3-тя гармоніка меандра", 11, "#27447e", "middle")
    s += text(W / 2, 408, "правила: затримка на крок ≥ кількох Q/f₀; синус замість меандра (або знати про гармоніки); слабкий зв'язок",
              11.5, GREY, "middle", style="italic")
    save("fig-9-5a-2-sweep-pitfalls.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 вставка до §9.5 — RFID/NFC
# ─────────────────────────────────────────────────────────────────────────────
def fig5c1_card():
    W, H = 840, 500
    s = header(W, H)
    s += text(W / 2, 34, "Картка без батарейки: трансформатор із повітряним осердям + резонанс", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "зчитувач створює змінне поле; контур картки, настроєний у резонанс, розгойдує його до робочих вольтів",
              12, GREY, "middle", style="italic")
    # котушка зчитувача
    s += rect(70, 130, 110, 250, "#f3f3f3", INK, 1.8, 8)
    s += text(125, 118, "зчитувач", 12.5, INK, "middle", "bold")
    for k in range(5):
        ya = 160 + k * 40
        s += f'<path d="M 160,{ya} A 12 14 0 0 1 160,{ya + 40}" fill="none" stroke="{COPP}" stroke-width="2.6"/>\n'
    s += text(125, 270, "генерує", 10.5, GREY, "middle")
    s += text(125, 286, "13.56 МГц", 10.5, GREY, "middle")
    # поле — дуги
    for r in (60, 100, 140):
        s += f'<path d="M 175,{255 - r} A {r} {r} 0 0 1 175,{255 + r}" fill="none" stroke="{GREEN}" stroke-width="1.8" stroke-dasharray="6,5"/>\n'
    s += text(245, 130, "змінне магнітне поле", 11, GREEN, "middle", "bold")
    s += text(245, 146, "(ближнє: дальність ~ розмір котушки)", 9.5, GREY, "middle")
    # картка
    s += rect(380, 150, 280, 180, "#ffffff", INK, 2, 10)
    s += text(520, 138, "картка / мітка", 12.5, INK, "middle", "bold")
    # периметральна антена (3 витки)
    for m in range(3):
        s += rect(392 + m * 7, 162 + m * 7, 256 - m * 14, 156 - m * 14, "none", COPP, 2)
    # чип і конденсатор
    s += rect(495, 222, 50, 36, "#3a3a3a", INK, 1.6, 4)
    s += text(520, 245, "чип", 11, "#ffffff", "middle", "bold")
    s += text(520, 280, "конденсатор настроювання —", 9.5, GREY, "middle")
    s += text(520, 294, "усередині чипа", 9.5, GREY, "middle")
    # ланцюжок праворуч
    ax = 700
    s += text(ax, 180, "1. наведення:", 11.5, INK, "start", "bold")
    s += text(ax, 196, "мілівольти (§2.2.6)", 11, GREY, "start")
    s += text(ax, 228, "2. резонанс:", 11.5, INK, "start", "bold")
    s += text(ax, 244, "контур ×Q → вольти", 11, GREY, "start")
    s += text(ax, 276, "3. випрямляч у чипі:", 11.5, INK, "start", "bold")
    s += text(ax, 292, "живлення логіки", 11, GREY, "start")
    s += text(W / 2, 380, "числа для 13.56 МГц: кілька витків по периметру (L ≈ 1.4 мкГн) + ≈100 пФ:  f₀ = 1/(2π√(LC)) ≈ 13.6 МГц",
              12, INK, "middle", "bold")
    s += text(W / 2, 404, "сімейство 125 кГц влаштоване так само — лише більше витків і нижча частота",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 440, "без резонансу наведених мілівольтів не вистачило б: саме добротність контуру робить картку безбатарейною",
              11.5, GREY, "middle", style="italic")
    save("fig-9-5c-1-card.svg", s)


def fig5c2_load_mod():
    W, H = 800, 460
    s = header(W, H)
    s += text(W / 2, 34, "Як картка відповідає: смикає спільне поле навантаженням", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "чип ритмічно підмикає резистор до свого контуру — зчитувач бачить це у власному струмі",
              12.5, GREY, "middle", style="italic")
    # схема картки з ключем
    s += _frame(60, 90, 280, 240, "у картці")
    # контур
    for m in range(2):
        s += rect(90 + m * 6, 130 + m * 6, 110 - m * 12, 120 - m * 12, "none", COPP, 2)
    cs, t_, b_ = cap_sym(250, 165, 12, 8)
    s += line(200, 140, 250, 140, INK, 1.8)
    s += line(250, 140, 250, 157, INK, 1.8)
    s += cs
    s += line(250, 173, 250, 240, INK, 1.8)
    s += line(200, 240, 250, 240, INK, 1.8)
    # ключ + резистор від чипа
    s += rect(280, 150, 40, 24, "#3a3a3a", INK, 1.4, 3)
    s += text(300, 166, "чип", 9.5, "#ffffff", "middle", "bold")
    s += line(300, 174, 300, 196, INK, 1.6)
    s += rect(290, 196, 20, 34, "#f3f3f3", INK, 1.4)
    s += text(322, 216, "R", 11, INK, "start", "bold")
    s += line(300, 230, 300, 252, INK, 1.6)
    s += line(250, 252, 300, 252, INK, 1.6)
    s += text(200, 305, "ключ у чипі вмикає R у такт бітам:", 10.5, GREY, "middle", style="italic")
    s += text(200, 321, "контур то «важчий», то «легший»", 10.5, GREY, "middle", style="italic")
    # осцилограма зчитувача
    ox, oy, w, h = 420, 300, 330, 170
    s += text(ox + w / 2, 100, "струм у котушці ЗЧИТУВАЧА:", 12, INK, "middle", "bold")
    pts = []
    for j in range(0, 401):
        t = j / 400.0
        bit = 1 if (0.25 < t < 0.45) or (0.6 < t < 0.7) or (0.8 < t < 0.95) else 0
        amp = 0.62 - 0.16 * bit
        pts.append((ox + t * w, oy - h / 2 - amp * (h / 2) * math.sin(2 * math.pi * 26 * t)))
    s += _poly(pts, BLUE, 1.6)
    s += line(ox, oy - h / 2, ox + w, oy - h / 2, GREY, 1, dash="3,4")
    s += text(ox + w / 2, oy + 26, "просідання амплітуди = біти картки", 11.5, "#27447e", "middle", "bold")
    s += text(W / 2, 400, "це відбитий опір у дії (§2.2.6 і вставка про n²): навантаження вторинного контуру",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 420, "видно з первинного боку — картка нічого не передає, вона лише «тяжчає» і «легшає» в полі",
              12, GREY, "middle", style="italic")
    save("fig-9-5c-2-load-mod.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 вставка до §9.3 — LC/π-фільтр живлення
# ─────────────────────────────────────────────────────────────────────────────
def fig3c1_pi_filter():
    W, H = 840, 480
    s = header(W, H)
    s += text(W / 2, 34, "π-фільтр у шині живлення: брудне ліворуч, чисте праворуч", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "дросель не пускає шум уперед, конденсатори зливають його в землю з обох боків",
              12.5, GREY, "middle", style="italic")
    railY, gnd = 180, 340
    # шумне джерело
    s += rect(60, railY - 30, 130, 60, "#f3f3f3", INK, 1.8, 6)
    s += text(125, railY - 6, "перетворювач", 11.5, INK, "middle", "bold")
    s += text(125, railY + 12, "(шумить ~500 кГц)", 10, GREY, "middle")
    s += line(190, railY, 280, railY, INK, 2.4)
    # C1
    cs1, t1, b1 = cap_sym(280, railY + 50, 14, 9)
    s += line(280, railY, 280, railY + 41, INK, 2)
    s += cs1
    s += line(280, railY + 59, 280, gnd, INK, 2)
    s += text(252, railY + 54, "C₁", 12.5, INK, "end", "bold")
    s += circle(280, railY, 3.5, INK, INK, 0)
    # дросель
    s += line(280, railY, 330, railY, INK, 2.4)
    for k in range(4):
        xa = 330 + k * 28
        s += f'<path d="M {xa},{railY} A 14 13 0 0 1 {xa + 28},{railY}" fill="none" stroke="{COPP}" stroke-width="2.6"/>\n'
    s += text(386, railY - 24, "L = 10 мкГн", 12, COPP, "middle", "bold")
    s += line(442, railY, 520, railY, INK, 2.4)
    # C2
    cs2, t2, b2 = cap_sym(520, railY + 50, 14, 9)
    s += line(520, railY, 520, railY + 41, INK, 2)
    s += cs2
    s += line(520, railY + 59, 520, gnd, INK, 2)
    s += text(548, railY + 54, "C₂ = 10 мкФ", 12, INK, "start", "bold")
    s += circle(520, railY, 3.5, INK, INK, 0)
    # споживач
    s += line(520, railY, 620, railY, INK, 2.4)
    s += rect(620, railY - 30, 150, 60, LGRN, GREEN, 1.8, 6)
    s += text(695, railY - 6, "чутливий вузол", 11.5, INK, "middle", "bold")
    s += text(695, railY + 12, "(АЦП, радіо, аналог)", 10, GREY, "middle")
    s += line(60, gnd, 770, gnd, INK, 2.4)
    s += line(125, railY + 30, 125, gnd, INK, 2.2)
    s += line(695, railY + 30, 695, gnd, INK, 2.2)
    # осцилограми
    for x0, noisy, lab, col in ((215, True, "до: DC + шум", RED), (565, False, "після: чисте DC", GREEN)):
        pts = []
        for j in range(0, 61):
            t = j / 60.0
            n = 8 * math.sin(40 * t) if noisy else 0.6 * math.sin(40 * t)
            pts.append((x0 + t * 50, 120 - n))
        s += _poly(pts, col, 1.8)
        s += text(x0 + 25, 98, lab, 10.5, col, "middle", "bold")
    s += text(W / 2, 392, "для шуму 500 кГц: XL ≈ 31 Ом проти Xc ≈ 0.03 Ом — дільник давить у ~1000 разів;",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 414, "для постійного струму: XL = 0 (плюс міліоми DCR), Xc = ∞ — живлення проходить недоторканим",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 448, "π-форма: C₁ згладжує ще біля джерела, C₂ обслуговує споживача — і фільтр працює в обидва напрямки",
              11.5, GREY, "middle", style="italic")
    save("fig-9-3c-1-pi-filter.svg", s)


def fig3c2_resonance_warning():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Тінь π-фільтра: власний резонанс LC", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "нижче робочої смуги ховається f₀ = 1/(2π√(LC)) — і там фільтр може дзвеніти",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 360, 580, 250
    s += _axes(ox, oy, w, h, "частота (лог)", "пропускання")
    # крива: 1 на НЧ, пік на f0, спад далі
    f0 = 0.32
    pts = []
    for j in range(0, 201):
        f = j / 200.0
        if f < f0:
            g = 0.55 + 0.4 * math.exp(-((f - f0) ** 2) / 0.004)
        else:
            g = 0.55 * math.exp(-(f - f0) * 4.2) + 0.55 * math.exp(-((f - f0) ** 2) / 0.004) * 0.73
        pts.append((ox + f * w, oy - g * h))
    s += _poly(pts, COPP, 2.8)
    s += line(ox + f0 * w, oy, ox + f0 * w, oy - h, GREY, 1.3, dash="5,4")
    s += text(ox + f0 * w, oy + 20, "f₀", 13, RED, "middle", "bold")
    s += text(ox + f0 * w + 10, oy - 0.93 * h, "пік: добротний фільтр ПІДСИЛЮЄ", 11.5, "#9a2b22", "start", "bold")
    s += text(ox + f0 * w + 10, oy - 0.93 * h + 16, "коливання біля f₀ (стрибки навантаження!)", 11.5, "#9a2b22", "start")
    s += text(ox + 0.12 * w, oy - 0.62 * h, "DC і повільне:", 11.5, "#1f6e33", "middle", "bold")
    s += text(ox + 0.12 * w, oy - 0.62 * h + 16, "проходить", 11.5, "#1f6e33", "middle")
    s += text(ox + 0.8 * w, oy - 0.3 * h, "шум перетворювача:", 11.5, "#1f6e33", "middle", "bold")
    s += text(ox + 0.8 * w, oy - 0.3 * h + 16, "давиться", 11.5, "#1f6e33", "middle")
    s += text(W / 2, 410, "ліки — трохи втрат: електроліт із помірним ESR паралельно C₂ чи невеликий резистор гасять пік",
              12, GREY, "middle", style="italic")
    save("fig-9-3c-2-resonance-warning.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 вставка до §9.2 — ємнісний баласт
# ─────────────────────────────────────────────────────────────────────────────
def fig2c1_dropper():
    W, H = 840, 500
    s = header(W, H)
    s += text(W / 2, 34, "Ємнісний баласт: реактивність замість гасильного резистора", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "конденсатор «з'їдає» зайву напругу мережі, не виділивши ані вата тепла",
              12.5, GREY, "middle", style="italic")
    railY, gnd = 170, 330
    # мережа
    s += circle(90, (railY + gnd) / 2, 26, "#fff", INK, 2)
    pts = [(90 - 15 + 30 * t / 100, (railY + gnd) / 2 - 9 * math.sin(2 * math.pi * 1.5 * t / 100)) for t in range(0, 101)]
    s += _poly(pts, INK, 1.8)
    s += line(90, (railY + gnd) / 2 - 26, 90, railY, INK, 2.2)
    s += line(90, (railY + gnd) / 2 + 26, 90, gnd, INK, 2.2)
    s += text(90, gnd + 24, "мережа 230 В", 11.5, INK, "middle", "bold")
    s += text(90, gnd + 42, "50 Гц", 11, GREY, "middle")
    # X2-конденсатор послідовно + bleeder
    s += line(90, railY, 200, railY, INK, 2.2)
    cs, lxx, rxx = cap_sym(218, railY, 16, 10)
    s += line(200, railY, lxx, railY, INK, 2.2)
    s += cs
    s += text(218, railY - 28, "C: плівка X2, 0.47 мкФ", 11.5, INK, "middle", "bold")
    s += text(218, railY - 12, "Xc ≈ 6.8 кОм на 50 Гц", 10.5, GREY, "middle")
    # bleeder
    s += line(lxx - 18 + 6, railY, lxx - 12, railY, INK, 0.1)
    s += rect(190, railY + 26, 56, 16, "#f3f3f3", INK, 1.4)
    s += line(200, railY, 200, railY + 34, INK, 1.6)
    s += line(246, railY + 34, 256, railY + 34, INK, 0.1)
    s += line(236 + 10, railY + 34, 254, railY + 34, INK, 1.6)
    s += line(254, railY + 34, 254, railY, INK, 1.6)
    s += text(218, railY + 58, "1 МОм: розряд після вимкнення", 9.5, GREY, "middle")
    # захисний резистор
    s += line(rxx, railY, 300, railY, INK, 2.2)
    s += rect(300, railY - 9, 56, 18, "#f3f3f3", INK, 1.6)
    s += text(328, railY - 16, "47–100 Ом", 10, INK, "middle", "bold")
    s += text(328, railY + 30, "проти кидка ввімкнення", 9.5, GREY, "middle")
    s += line(356, railY, 420, railY, INK, 2.2)
    # випрямляч
    s += rect(420, railY - 24, 92, gnd - railY + 48, "#f3f3f3", INK, 1.8, 8)
    s += text(466, (railY + gnd) / 2 - 4, "випрямляч", 11.5, INK, "middle", "bold")
    s += text(466, (railY + gnd) / 2 + 14, "(міст, §2.5.6)", 10, GREY, "middle")
    s += line(90, gnd, 420, gnd, INK, 2.2)
    # LED + стабілітрон
    s += line(512, railY, 600, railY, INK, 2.2)
    s += rect(600, railY + 10, 36, 120, LGRN, GREEN, 1.8, 6)
    s += text(618, railY - 6, "LED-ланцюжок", 10.5, "#1f6e33", "middle", "bold")
    s += line(618, railY, 618, railY + 10, INK, 2)
    s += line(618, railY + 130, 618, gnd, INK, 2)
    s += rect(690, railY + 30, 26, 80, LRED, "#c98a8a", 1.6, 6)
    s += text(703, railY + 16, "стабілітрон", 9.5, "#9a2b22", "middle")
    s += line(703, railY, 703, railY + 30, INK, 1.8)
    s += line(512, railY, 703, railY, INK, 0.1)
    s += line(703, railY + 110, 703, gnd, INK, 1.8)
    s += line(512, gnd, 760, gnd, INK, 2.2)
    s += line(760, gnd, 760, gnd, INK, 0.1)
    s += text(560, railY - 18, "I ≈ 34 мА", 11.5, GREEN, "middle", "bold")
    # порівняння потужностей
    s += text(W / 2, 414, "якби гасив резистор 6.8 кОм: P = I²·R ≈ 8 Вт пічки;  конденсатор: середня потужність ≈ 0 (зсув 90°, §2.3.4)",
              12, GREY, "middle", style="italic")
    s += rect(60, 432, 720, 40, LRED, RED, 1.8, 8)
    s += text(W / 2, 457, "⚠ розв'язки від мережі НЕМАЄ: кожна точка цієї схеми — це дотик до розетки", 13, "#9a2b22", "middle", "bold")
    save("fig-9-2c-1-dropper.svg", s)


def fig2c2_no_isolation():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 34, "Чим баласт відрізняється від трансформатора: бар'єра немає", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "струм обмежений — але потенціал мережі нікуди не дівся",
              12.5, GREY, "middle", style="italic")
    # ліва панель: трансформатор
    s += _frame(50, 90, 340, 280, "блок живлення з трансформатором")
    s += line(80, 150, 160, 150, INK, 2.2)
    s += line(80, 280, 160, 280, INK, 2.2)
    s += text(95, 215, "мережа", 11, INK, "middle", "bold")
    # трансформатор: дві котушки + осердя
    for k in range(4):
        ya = 160 + k * 28
        s += f'<path d="M 170,{ya} A 11 14 0 0 1 170,{ya + 28}" fill="none" stroke="{COPP}" stroke-width="2.2"/>\n'
        s += f'<path d="M 196,{ya} A 11 14 0 0 0 196,{ya + 28}" fill="none" stroke="{COPP}" stroke-width="2.2"/>\n'
    s += line(180, 150, 180, 285, INK, 2.4)
    s += line(186, 150, 186, 285, INK, 2.4)
    s += line(160, 150, 170, 150, INK, 0.1)
    s += line(196, 160, 280, 160, INK, 2.2)
    s += line(196, 272, 280, 272, INK, 2.2)
    s += rect(280, 180, 70, 70, LGRN, GREEN, 1.8, 6)
    s += text(315, 220, "схема", 11.5, INK, "middle", "bold")
    s += line(280, 160, 315, 160, INK, 0.1)
    s += text(220, 330, "енергія йде через ПОЛЕ:", 11.5, "#1f6e33", "middle", "bold")
    s += text(220, 348, "прямого шляху до мережі немає (§2.2.6)", 11, "#1f6e33", "middle")
    # права панель: dropper
    s += _frame(420, 90, 340, 280, "ємнісний баласт")
    s += line(450, 150, 540, 150, INK, 2.2)
    cs2, l2, r2 = cap_sym(560, 150, 14, 9)
    s += line(540, 150, l2, 150, INK, 2.2)
    s += cs2
    s += line(r2, 150, 640, 150, INK, 2.2)
    s += rect(640, 180, 70, 70, LRED, "#c98a8a", 1.8, 6)
    s += text(675, 220, "схема", 11.5, INK, "middle", "bold")
    s += line(640, 150, 675, 150, INK, 2.2)
    s += line(675, 150, 675, 180, INK, 2.2)
    s += line(450, 280, 675, 280, INK, 2.2)
    s += line(675, 250, 675, 280, INK, 2.2)
    s += text(470, 215, "мережа", 11, INK, "middle", "bold")
    s += arrow(480, 300, 660, 235, RED, 2.4)
    s += text(560, 318, "провідний шлях від розетки до кожної", 11.5, "#9a2b22", "middle", "bold")
    s += text(560, 336, "точки схеми — крізь конденсатор і дроти", 11.5, "#9a2b22", "middle", "bold")
    s += text(W / 2, 404, "тому ємнісний баласт допустимий лише в повністю закритих пристроях без жодного контакту назовні",
              12, GREY, "middle", style="italic")
    save("fig-9-2c-2-no-isolation.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 вставка до §9.6 — добротність Q математично
# ─────────────────────────────────────────────────────────────────────────────
def fig6m1_energy_def():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 34, "Енергетичне означення Q: запас проти витоку за цикл", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одне число каже, яку частку своєї енергії контур губить за кожне коливання",
              12.5, GREY, "middle", style="italic")
    # бак енергії, що гойдається між C і L
    cx, cy = 240, 230
    s += circle(cx, cy, 95, LGRN, GREEN, 2.4)
    s += text(cx, cy - 14, "запасена", 13, INK, "middle", "bold")
    s += text(cx, cy + 6, "енергія W", 13, INK, "middle", "bold")
    s += text(cx, cy + 30, "(гойдається C ↔ L)", 10.5, GREY, "middle")
    # стрілки циклу
    s += f'<path d="M {cx - 60},{cy - 78} A 99 99 0 0 1 {cx + 60},{cy - 78}" fill="none" stroke="{GREEN}" stroke-width="2.2" marker-end="url(#aGreen)"/>\n'
    s += f'<path d="M {cx + 60},{cy + 78} A 99 99 0 0 1 {cx - 60},{cy + 78}" fill="none" stroke="{GREEN}" stroke-width="2.2" marker-end="url(#aGreen)"/>\n'
    # витік у R
    s += arrow(cx + 95, cy, cx + 190, cy, RED, 2.6)
    s += rect(cx + 190, cy - 22, 44, 44, LRED, RED, 1.8, 6)
    s += text(cx + 212, cy + 6, "R", 14, INK, "middle", "bold")
    s += text(cx + 142, cy - 14, "витік за період:", 11, "#9a2b22", "middle", "bold")
    s += text(cx + 142, cy + 24, "W_втрат", 11.5, "#9a2b22", "middle", "bold")
    for k in range(3):
        xx = cx + 246 + k * 10
        s += f'<path d="M {xx},{cy + 14} q 4,-7 0,-14 q -4,-7 0,-14" fill="none" stroke="{RED}" stroke-width="1.6"/>\n'
    # формули праворуч
    ax = 545
    s += text(ax, 150, "Q = 2π · W / W_втрат", 16, INK, "start", "bold")
    s += text(ax, 178, "за один період", 11.5, GREY, "start")
    s += text(ax, 216, "тобто щоперіоду контур губить", 12, INK, "start")
    s += text(ax, 236, "частку 2π/Q своєї енергії:", 12, INK, "start")
    s += text(ax, 262, "Q = 100 → 6% за коливання", 12.5, GREEN, "start", "bold")
    s += text(ax, 300, "для послідовного контуру звідси", 12, INK, "start")
    s += text(ax, 320, "виходить знайоме:", 12, INK, "start")
    s += text(ax, 348, "Q = ω₀L/R = √(L/C)/R", 14.5, INK, "start", "bold")
    s += text(W / 2, 408, "2π у означенні — для чистоти формул (частка на радіан, а не на період); Q безрозмірна",
              11.5, GREY, "middle", style="italic")
    save("fig-9-6m-1-energy-def.svg", s)


def fig6m2_ringing_q():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Q можна порахувати оком: скільки коливань живе дзвін", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "амплітуда тане як e^(−π·N/Q): до ~4% лишку минає приблизно Q коливань",
              12.5, GREY, "middle", style="italic")

    def ring(oy, qv, ncyc, col):
        ox, w, amp = 90, 640, 70
        out = line(ox, oy, ox + w, oy, GREY, 1.2)
        pts = []
        for j in range(0, 481):
            t = j / 480.0
            n = t * ncyc
            env = math.exp(-math.pi * n / qv)
            pts.append((ox + t * w, oy - amp * env * math.cos(2 * math.pi * n)))
        out += _poly(pts, col, 2)
        env_pts = [(ox + t / 100 * w, oy - amp * math.exp(-math.pi * (t / 100 * ncyc) / qv)) for t in range(0, 101)]
        out += _poly(env_pts, GREY, 1.4, dash="5,4")
        return out

    s += text(110, 96, "Q = 10:", 13, INK, "start", "bold")
    s += text(170, 96, "дзвін гасне за ~10 коливань", 12, GREY, "start")
    s += ring(170, 10, 14, BLUE)
    s += text(110, 286, "Q = 50:", 13, INK, "start", "bold")
    s += text(170, 286, "ті самі 14 коливань — а згасання ледь почалося", 12, GREY, "start")
    s += ring(360, 50, 14, GREEN)
    s += text(W / 2, 442, "звідси й вимірювання: порахуй видимі коливання дзвону — дістанеш Q (і чому при малій Q дзвону «не видно»)",
              12, GREY, "middle", style="italic")
    save("fig-9-6m-2-ringing-q.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 вставка до §9.5 — формула Томсона
# ─────────────────────────────────────────────────────────────────────────────
def fig5m1_derivation():
    W, H = 820, 480
    s = header(W, H)
    s += text(W / 2, 34, "LC-петля без джерела: рівняння пише сама схема", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "конденсатор і котушка ділять ту саму напругу й той самий струм — це і є рівняння коливань",
              12.5, GREY, "middle", style="italic")
    # схема: LC-петля
    cx = 170
    s += line(cx - 60, 130, cx + 60, 130, INK, 2.4)
    s += line(cx - 60, 130, cx - 60, 300, INK, 2.4)
    s += line(cx - 60, 300, cx + 60, 300, INK, 2.4)
    cs, _, _ = cap_sym(cx - 60, 215, 16, 10)
    s += cs
    s += text(cx - 86, 220, "C", 14, INK, "end", "bold")
    s += line(cx + 60, 130, cx + 60, 175, INK, 2.4)
    # вертикальна котушка дугами
    for k in range(4):
        ya = 175 + k * 25
        s += f'<path d="M {cx + 60},{ya} A 13 12.5 0 0 1 {cx + 60},{ya + 25}" fill="none" stroke="{COPP}" stroke-width="2.4"/>\n'
    s += line(cx + 60, 275, cx + 60, 300, INK, 2.4)
    s += text(cx + 92, 220, "L", 14, INK, "start", "bold")
    s += arrow(cx - 20, 315, cx + 20, 315, GREEN, 2.2)
    s += text(cx, 336, "той самий струм i", 11, GREEN, "middle", "bold")
    # ланцюжок виведення праворуч
    ax = 330
    s += text(ax, 130, "спільна напруга:  v_C = v_L = v", 13.5, INK, "start", "bold")
    s += text(ax, 168, "котушка:       v = L · di/dt", 13.5, INK, "start")
    s += text(ax, 200, "конденсатор:   i = −C · dv/dt   (розряджається)", 13.5, INK, "start")
    s += line(ax, 220, ax + 420, 220, GREY, 1.2)
    s += text(ax, 252, "підставимо одне в одне:", 12.5, GREY, "start", style="italic")
    s += text(ax, 284, "d²v/dt² = − v / (L·C)", 16, RED, "start", "bold")
    s += text(ax, 320, "«прискорення протилежне відхиленню» —", 12.5, INK, "start")
    s += text(ax, 340, "це рівняння гармонічних коливань;", 12.5, INK, "start")
    s += text(ax, 360, "розв'язок — синусоїда (дві похідні = поворот", 12.5, INK, "start")
    s += text(ax, 380, "на 2×90° = мінус, §2.3.4m) із  ω² = 1/(L·C)", 12.5, INK, "start")
    s += text(W / 2, 440, "f₀ = ω₀/2π = 1/(2π·√(L·C)) — формула Томсона, здобута з самої динаміки контуру",
              13.5, GREEN, "middle", "bold")
    save("fig-9-5m-1-derivation.svg", s)


def fig5m2_pendulum():
    W, H = 820, 500
    s = header(W, H)
    s += text(W / 2, 34, "Словник механіки й електрики: чому корінь і чому добуток LC", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама математика обслуговує масу на пружині й LC-контур",
              12.5, GREY, "middle", style="italic")
    # ліворуч: маса на пружині
    sx = 150
    s += line(sx - 70, 110, sx + 70, 110, INK, 3)
    zig = "M " + f"{sx},110 "
    yy = 110
    for k in range(6):
        zig += f"L {sx + (14 if k % 2 == 0 else -14)},{yy + 12} "
        yy += 12
    zig += f"L {sx},{yy + 8}"
    s += f'<path d="{zig}" fill="none" stroke="{INK}" stroke-width="2.2"/>\n'
    s += rect(sx - 36, yy + 8, 72, 54, "#d9d9dd", INK, 2, 6)
    s += text(sx, yy + 41, "m", 16, INK, "middle", "bold")
    s += arrow(sx + 56, yy + 35, sx + 56, yy + 80, GREEN, 2.2)
    s += arrow(sx + 56, yy + 35, sx + 56, yy - 10, GREEN, 2.2)
    s += text(sx + 66, yy + 38, "x", 12.5, GREEN, "start", "bold")
    s += text(sx, 348, "ω = √(k/m)", 15, INK, "middle", "bold")
    s += text(sx, 372, "важча маса чи м'якша", 11, GREY, "middle")
    s += text(sx, 388, "пружина → повільніше", 11, GREY, "middle")
    # словник посередині
    pairs = (("зміщення x", "заряд q"),
             ("швидкість v", "струм i"),
             ("сила пружини", "напруга на C"),
             ("маса m (інерція)", "індуктивність L"),
             ("жорсткість k", "1/C"),
             ("½·m·v²", "½·L·i²  (§2.2.3)"),
             ("½·k·x²", "½·q²/C  (§2.1.3)"))
    ty = 120
    for a, b in pairs:
        s += text(395, ty, a, 12.5, INK, "end")
        s += arrow(415, ty - 4, 455, ty - 4, GREY, 1.4)
        s += arrow(455, ty - 4, 415, ty - 4, GREY, 1.4)
        s += text(475, ty, b, 12.5, INK, "start")
        ty += 38
    # праворуч: LC
    lx = 700
    s += line(lx - 50, 130, lx + 50, 130, INK, 2.2)
    s += line(lx - 50, 130, lx - 50, 280, INK, 2.2)
    s += line(lx - 50, 280, lx + 50, 280, INK, 2.2)
    cs, _, _ = cap_sym(lx - 50, 205, 14, 9)
    s += cs
    s += line(lx + 50, 130, lx + 50, 165, INK, 2.2)
    for k in range(4):
        ya = 165 + k * 22
        s += f'<path d="M {lx + 50},{ya} A 12 11 0 0 1 {lx + 50},{ya + 22}" fill="none" stroke="{COPP}" stroke-width="2.2"/>\n'
    s += line(lx + 50, 253, lx + 50, 280, INK, 2.2)
    s += text(lx, 348, "ω = 1/√(L·C)", 15, INK, "middle", "bold")
    s += text(lx, 372, "більша «маса» L чи м'якша", 11, GREY, "middle")
    s += text(lx, 388, "«пружина» (більший C) → повільніше", 11, GREY, "middle")
    s += text(W / 2, 440, "підставте у механічну формулу m → L і k → 1/C — і дістанете Томсона: ω = √((1/C)/L) = 1/√(LC)",
              12.5, GREEN, "middle", "bold")
    s += text(W / 2, 464, "корінь — бо частота задається через ω², а в ω² компоненти входять симетричним добутком",
              11.5, GREY, "middle", style="italic")
    save("fig-9-5m-2-pendulum.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 вставка до §9.4 — похідні синуса й косинуса
# ─────────────────────────────────────────────────────────────────────────────
def fig4m1_slope_trace():
    W, H = 820, 560
    s = header(W, H)
    s += text(W / 2, 34, "Нахил синуса в кожній точці — це косинус", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "пройдімо по чотирьох опорних точках і простежмо, що робить дотична",
              12.5, GREY, "middle", style="italic")
    ox, w, amp = 110, 600, 85
    # верхній графік: sin із дотичними
    oy1 = 190
    s += line(ox, oy1, ox + w, oy1, GREY, 1.4)
    s += text(ox - 8, oy1 + 4, "sin", 13, RED, "end", "bold")
    pts = [(ox + t / 200 * w, oy1 - amp * math.sin(2 * math.pi * t / 200)) for t in range(0, 201)]
    s += _poly(pts, RED, 2.6)
    # дотичні в 4 точках: t=0 (нахил max+), t=кв (0), t=пів (max−), t=3кв (0)
    tang = (0.0, 0.25, 0.5, 0.75)
    for f in tang:
        x = ox + f * w
        y = oy1 - amp * math.sin(2 * math.pi * f)
        dx = 34
        sl = -amp * math.cos(2 * math.pi * f) * (2 * math.pi / w)
        s += line(x - dx, y - sl * dx, x + dx, y + sl * dx, GREEN, 2.6)
        s += circle(x, y, 4.5, RED, RED, 0)
    # нижній графік: значення нахилів = cos
    oy2 = 420
    s += line(ox, oy2, ox + w, oy2, GREY, 1.4)
    s += text(ox - 8, oy2 + 4, "нахил", 12, GREEN, "end", "bold")
    pts2 = [(ox + t / 200 * w, oy2 - amp * math.cos(2 * math.pi * t / 200)) for t in range(0, 201)]
    s += _poly(pts2, GREEN, 2.6)
    for f in tang:
        x = ox + f * w
        s += line(x, oy1 + amp + 10, x, oy2 - amp - 10, GREY, 1, dash="3,5")
        s += circle(x, oy2 - amp * math.cos(2 * math.pi * f), 4.5, GREEN, GREEN, 0)
    s += text(ox + w / 2, 530, "крива нахилів — той самий синус, зсунутий на чверть періоду ВПЕРЕД: (sin)′ = cos",
              13, INK, "middle", "bold")
    save("fig-9-4m-1-slope-trace.svg", s)


def fig4m2_circle_velocity():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Те саме з обертовою стрілкою: швидкість завжди на 90° попереду", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "і довжина вектора швидкості — ω·r: ось звідки множник ω у похідній",
              12.5, GREY, "middle", style="italic")
    cx, cy, r = 240, 250, 110
    s += circle(cx, cy, r, "none", FAINT, 1.6)
    ang = math.radians(35)
    px_, py_ = cx + r * math.cos(ang), cy - r * math.sin(ang)
    s += arrow(cx, cy, px_, py_, RED, 3)
    s += text((cx + px_) / 2 + 10, (cy + py_) / 2 + 16, "положення (r)", 11.5, RED, "start", "bold")
    # вектор швидкості: перпендикулярний, довжина ωr (намалюємо 0.8r)
    vlen = 0.8 * r
    vx = px_ + vlen * math.cos(ang + math.pi / 2)
    vy = py_ - vlen * math.sin(ang + math.pi / 2)
    s += arrow(px_, py_, vx, vy, GREEN, 3)
    s += text(vx + 6, vy - 6, "швидкість: довжина ω·r,", 11.5, GREEN, "start", "bold")
    s += text(vx + 6, vy + 10, "повернена на +90°", 11.5, GREEN, "start", "bold")
    # прямий кут
    s += rect(px_ + 10 * math.cos(ang + math.pi / 2) - 5, py_ - 10 * math.sin(ang + math.pi / 2) - 5, 10, 10, "none", GREY, 1.2)
    # висновки праворуч
    ax = 470
    s += text(ax, 150, "проєкція положення → A·sin(ωt)", 13, RED, "start", "bold")
    s += text(ax, 186, "проєкція швидкості → похідна:", 13, GREEN, "start", "bold")
    s += text(ax, 216, "та сама синусоїда, але", 12.5, INK, "start")
    s += text(ax, 236, "• амплітуда помножена на ω", 12.5, INK, "start")
    s += text(ax, 256, "• фаза зсунута на +90°", 12.5, INK, "start")
    s += text(ax, 300, "d/dt [A·sin(ωt)] = A·ω·sin(ωt + 90°)", 14, INK, "start", "bold")
    s += text(ax, 340, "що швидше обертання (вища частота) —", 12, GREY, "start", style="italic")
    s += text(ax, 358, "то більша швидкість: звідси ω", 12, GREY, "start", style="italic")
    s += text(ax, 376, "у формулах Xc = 1/(ωC) і XL = ωL", 12, GREY, "start", style="italic")
    s += text(W / 2, 436, "чотири похідні поспіль: sin → cos → −sin → −cos → sin — чотири кроки по 90°, повне коло",
              12, GREY, "middle", style="italic")
    save("fig-9-4m-2-circle-velocity.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 вставка до §9.1 — комплексні числа й фазори
# ─────────────────────────────────────────────────────────────────────────────
def fig1m1_complex_plane():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Комплексне число — стрілка; множення на j — поворот на 90°", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "одна «стрілка» тримає одразу дві величини: довжину і кут",
              12.5, GREY, "middle", style="italic")
    # ліва панель: число як стрілка
    cx, cy, sc = 210, 270, 130
    s += arrow(cx - 160, cy, cx + 160, cy, GREY, 1.6)
    s += arrow(cx, cy + 150, cx, cy - 150, GREY, 1.6)
    s += text(cx + 164, cy + 4, "дійсна вісь", 11, GREY, "start")
    s += text(cx, cy - 158, "уявна вісь (j)", 11, GREY, "middle")
    a, b = 0.8, 0.6
    zx, zy = cx + a * sc, cy - b * sc
    s += line(zx, cy, zx, zy, GREY, 1.2, dash="4,4")
    s += line(cx, zy, zx, zy, GREY, 1.2, dash="4,4")
    s += arrow(cx, cy, zx, zy, RED, 3)
    s += text(zx + 8, zy - 6, "z = a + j·b", 13, RED, "start", "bold")
    s += text(zx, cy + 16, "a", 12, INK, "middle", "bold")
    s += text(cx - 12, zy + 4, "j·b", 12, INK, "end", "bold")
    s += f'<path d="M {cx + 44},{cy} A 44 44 0 0 0 {cx + 44 * 0.8:.0f},{cy - 44 * 0.6:.0f}" fill="none" stroke="{GREEN}" stroke-width="2"/>\n'
    s += text(cx + 58, cy - 18, "кут φ", 11.5, GREEN, "start", "bold")
    s += text(cx + 30, cy - 76, "довжина r", 11.5, RED, "start", style="italic")
    s += text(210, 448, "r = √(a² + b²);  a = r·cos φ;  b = r·sin φ", 12.5, INK, "middle", "bold")
    # права панель: множення на j
    cx2 = 600
    s += arrow(cx2 - 150, cy, cx2 + 150, cy, GREY, 1.6)
    s += arrow(cx2, cy + 150, cx2, cy - 150, GREY, 1.6)
    r2 = 110
    for ang, col, lab in ((0, RED, "z"), (90, GREEN, "j·z"), (180, BLUE, "j²·z = −z")):
        rad = math.radians(ang)
        s += arrow(cx2, cy, cx2 + r2 * math.cos(rad), cy - r2 * math.sin(rad), col, 3)
        lx = cx2 + (r2 + 26) * math.cos(rad)
        ly = cy - (r2 + 26) * math.sin(rad)
        s += text(lx, ly + 5, lab, 13, col, "middle", "bold")
    s += f'<path d="M {cx2 + 60},{cy} A 60 60 0 0 0 {cx2},{cy - 60}" fill="none" stroke="{GREY}" stroke-width="1.6" stroke-dasharray="4,4"/>\n'
    s += f'<path d="M {cx2},{cy - 60} A 60 60 0 0 0 {cx2 - 60},{cy}" fill="none" stroke="{GREY}" stroke-width="1.6" stroke-dasharray="4,4"/>\n'
    s += text(600, 448, "j·z — той самий z, повернений на +90°;  j² = два повороти = −1", 12.5, INK, "middle", "bold")
    save("fig-9-1m-1-complex-plane.svg", s)


def fig1m2_phasor():
    W, H = 820, 500
    s = header(W, H)
    s += text(W / 2, 34, "Фазор: синусоїда як обертова стрілка", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "проєкція стрілки на вісь — це і є сигнал; усі стрілки кола крутяться разом",
              12.5, GREY, "middle", style="italic")
    # обертова стрілка + розгортка
    cx, cy, r = 170, 210, 90
    s += circle(cx, cy, r, "none", FAINT, 1.6)
    ang = math.radians(40)
    px_, py_ = cx + r * math.cos(ang), cy - r * math.sin(ang)
    s += arrow(cx, cy, px_, py_, RED, 3)
    s += f'<path d="M {cx + 34},{cy} A 34 34 0 0 0 {cx + 34 * math.cos(ang):.0f},{cy - 34 * math.sin(ang):.0f}" fill="none" stroke="{GREEN}" stroke-width="2"/>\n'
    s += text(cx + 44, cy - 12, "ωt + φ", 11, GREEN, "start", "bold")
    s += arrow(cx + r * 0.55, cy - r * 1.05, cx + r * 0.2, cy - r * 1.18, GREY, 1.6)
    s += text(cx + r * 0.6, cy - r * 1.1, "крутиться з частотою сигналу", 10.5, GREY, "start", style="italic")
    # проєкція праворуч у синусоїду
    ox, w = 320, 420
    s += line(px_, py_, ox, py_, GREY, 1.2, dash="4,4")
    s += _axes(ox, cy + r + 10, w, 2 * r + 20, "t", "")
    pts = [(ox + t / 160 * w, cy - r * math.cos(2 * math.pi * 1.6 * t / 160 - ang)) for t in range(0, 161)]
    s += _poly(pts, RED, 2.6)
    s += circle(ox, py_, 5, RED, RED, 0)
    s += text(ox + w - 6, cy - r - 8, "проєкція стрілки в часі = косинусоїда", 11, GREY, "end", style="italic")
    # фазорна діаграма R, L, C
    fy = 415
    s += text(120, fy - 52, "напруги на R, L, C", 12.5, INK, "middle", "bold")
    s += text(120, fy - 36, "за спільного струму I:", 12.5, INK, "middle", "bold")
    bx = 320
    s += arrow(bx, fy, bx + 120, fy, GREY, 2.4)
    s += text(bx + 126, fy + 4, "I (опора)", 11, GREY, "start", "bold")
    s += arrow(bx, fy, bx + 95, fy, COPP, 3)
    s += text(bx + 50, fy + 18, "V_R: у фазі", 11, COPP, "middle", "bold")
    s += arrow(bx, fy, bx, fy - 75, GREEN, 3)
    s += text(bx + 6, fy - 80, "V_L: +90° (випереджає)", 11, GREEN, "start", "bold")
    s += arrow(bx, fy, bx, fy + 58, BLUE, 3)
    s += text(bx + 8, fy + 56, "V_C: −90° (відстає)", 11, BLUE, "start", "bold")
    s += text(620, fy - 20, "це ті самі 90° з §2.3.4 —", 12, INK, "middle")
    s += text(620, fy - 2, "тепер вони просто множник j", 12, INK, "middle")
    s += text(620, fy + 16, "(або 1/j) перед опором", 12, INK, "middle")
    save("fig-9-1m-2-phasor.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 9 — налаштований контур
    fig_timeline()
    fig_mechanical_resonance()
    fig_lc_oscillation()
    fig_tuning_selectivity()
    fig_marconi_before_after()
    # §9.1 Реактивність
    fig11_ac_frequency()
    fig11_cap_vs_freq()
    fig11_why_cap()
    fig11_coil_vs_freq()
    fig11_why_coil()
    fig11_reactance_vs_resistance()
    fig11_mirror()
    # §9.2 Реактивність конденсатора
    fig21_formula()
    fig21_where_omega()
    fig21_ohm_for_cap()
    fig21_vs_freq()
    fig21_vs_c()
    fig21_worked_scale()
    # §9.3 Реактивність котушки
    fig31_formula()
    fig31_where_omega()
    fig31_ohm_for_coil()
    fig31_vs_freq()
    fig31_vs_l()
    fig31_mirror()
    # §9.4 Зсув фаз
    fig41_resistor_inphase()
    fig41_cap_leads()
    fig41_coil_lags()
    fig41_why_90()
    fig41_eli_ice()
    fig41_phasors()
    fig41_no_power()
    # §9.5 LC-резонанс
    fig51_crossing()
    fig51_f0_formula()
    fig51_swing_analogy()
    fig51_energy_slosh()
    fig51_series_resonance()
    fig51_parallel_resonance()
    fig51_tuning()
    # §9.6 Добротність Q і смуга
    fig61_q_curves()
    fig61_bandwidth()
    fig61_q_and_r()
    fig61_energy_def()
    fig61_ringing()
    fig61_tradeoff()
    fig61_quartz()
    # §9.7 RLC і частотна вибірковість
    fig71_rc_lowpass()
    fig71_cutoff()
    fig71_rc_highpass()
    fig71_bandpass_rlc()
    fig71_notch()
    fig71_four_types()
    fig71_selectivity_apps()
    # 🧮 вставка до §9.1 — комплексні числа й фазори
    fig1m1_complex_plane()
    fig1m2_phasor()
    # 🧮 вставка до §9.4 — похідні синуса
    fig4m1_slope_trace()
    fig4m2_circle_velocity()
    # 🧮 вставка до §9.5 — формула Томсона
    fig5m1_derivation()
    fig5m2_pendulum()
    # 🧮 вставка до §9.6 — добротність Q
    fig6m1_energy_def()
    fig6m2_ringing_q()
    # 🔌 вставка до §9.2 — ємнісний баласт
    fig2c1_dropper()
    fig2c2_no_isolation()
    # 🔌 вставка до §9.3 — LC/π-фільтр живлення
    fig3c1_pi_filter()
    fig3c2_resonance_warning()
    # 🔌 вставка до §9.5 — RFID/NFC
    fig5c1_card()
    fig5c2_load_mod()
    # ⚙️ вставка до §9.5 — пошук резонансу свіпом
    fig5a1_sweep_setup()
    fig5a2_sweep_pitfalls()
    # ⚙️ вставка до §9.4 — фігури Ліссажу
    fig4a1_liss_gallery()
    fig4a2_liss_ratios()
    # 📜 історія до §9.6 — Такома-Нерроуз
    fig6i1_resonance_vs_flutter()
    print("OK — Розділ 9 (історія + §9.1–§9.7 + вставки) згенеровано в", OUT)
