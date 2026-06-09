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
    print("OK — Розділ 9 (історія + §9.1–§9.7) згенеровано в", OUT)
