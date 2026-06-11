# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 11 — «Біполярний транзистор (BJT)» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Підписи посекційно (Рис. C.S.N); для історії до розділу —
секція 0 (Рис. 11.0.N). Допоміжні функції скопійовано з попередніх розділів.
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


def _tube(cx, cy, rx=46, ry=66):
    """Скляна колба лампи з ниткою розжарення й пластиною."""
    s = _ellipse(cx, cy, rx, ry, "#eef2f6", INK, 1.8)
    s += _poly([(cx, cy - 34), (cx - 10, cy - 16), (cx + 10, cy + 4), (cx - 10, cy + 24), (cx, cy + 40)], RED, 2)
    s += line(cx + 16, cy - 30, cx + 16, cy + 30, INK, 2.5)  # пластина (анод)
    s += line(cx, cy + ry, cx, cy + ry + 14, INK, 2)
    return s


# ── Рис. 11.0.1 — таймлайн ───────────────────────────────────────────────────
def fig_t1_timeline():
    W, H = 900, 210
    s = header(W, H)
    s += text(W / 2, 32, "Від лампи до мільярдів транзисторів на нігтику", 17, INK, "middle", "bold")
    boxes = [
        ("до 1947 · лампа", ["велика, гаряча,", "крихка"], "#fbfbfb"),
        ("1947 · Бардін, Браттейн", ["точковий", "транзистор"], "#fdf1dc"),
        ("1948 · Шоклі", ["плоскісний", "(практичний)"], "#fdf1dc"),
        ("1950–60-ті", ["мікросхема —", "багато на чипі"], "#fbfbfb"),
        ("сьогодні", ["мільярди", "на нігтику"], LGRN),
    ]
    bw, gap, by, bh = 156, 18, 80, 92
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 20 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 10.5, INK, "middle", "bold")
        border = "#9bb0c2" if fill == LGRN else ("#d8b46a" if fill == "#fdf1dc" else "#c9d3dc")
        s += rect(bx, by, bw, bh, fill, border, 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 38 + k * 22, ln, 11, INK, "middle")
        if i < len(boxes) - 1:
            ax = bx + bw
            s += arrow(ax + 2, by + bh / 2, ax + gap - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Один прилад замінив лампу — і, зменшуючись, дав цифрову епоху.", 11, GREY, "middle", style="italic")
    save("fig-11-0-1-timeline.svg", s)


# ── Рис. 11.0.2 — проблема лампи ─────────────────────────────────────────────
def fig_t2_tube_problem():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Лампа правила електронікою — але була вузьким місцем", 15.5, INK, "middle", "bold")
    s += _frame(40, 56, 300, 210, "електронна лампа")
    s += _tube(150, 150)
    s += text(150, 250, "нитка розжарення у вакуумі", 9, INK, "middle")
    s += text(238, 110, "− гаряча", 10.5, RED, "start", "bold")
    s += text(238, 132, "− велика", 10.5, RED, "start", "bold")
    s += text(238, 154, "− крихка", 10.5, RED, "start", "bold")
    s += text(238, 176, "− ненажерлива", 10.5, RED, "start", "bold")
    s += _frame(380, 56, 300, 210, "комп'ютер тих років")
    for j in range(5):
        for i in range(8):
            s += _ellipse(410 + i * 30, 100 + j * 28, 7, 11, "#eef2f6", GREY, 1)
    s += text(530, 250, "тисячі ламп — і часто перегоряли", 9, INK, "middle")
    s += text(W / 2, H - 10, "Велике, гаряче, ненадійне: на лампах електроніка не могла ні зменшитися, ні подешевшати.",
              10, GREY, "middle", style="italic")
    save("fig-11-0-2-tube-problem.svg", s)


# ── Рис. 11.0.3 — перший транзистор ──────────────────────────────────────────
def fig_t3_point_contact():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Перший транзистор (1947): германій і два золоті контакти", 14.5, INK, "middle", "bold")
    # германієва пластина
    s += rect(120, 200, 220, 40, "#cfd6dd", INK, 1.8)
    s += text(230, 256, "пластина германію", 9.5, INK, "middle")
    # пластиковий клин із двома контактами
    s += f'<path d="M 190,90 L 270,90 L 232,198 L 228,198 Z" fill="#e7dcc0" stroke="{INK}" stroke-width="1.4"/>\n'
    s += text(230, 80, "пластиковий клин", 9, INK, "middle")
    # два золоті контакти до пластини, дуже близько
    s += line(222, 150, 224, 198, SUN, 2.4) + line(238, 150, 236, 198, SUN, 2.4)
    s += circle(224, 198, 2.5, SUN, SUN) + circle(236, 198, 2.5, SUN, SUN)
    s += text(300, 150, "два золоті контакти", 9, COPP, "start", "bold")
    s += text(300, 165, "(дуже близько)", 8.5, GREY, "start")
    # підсилення: малий сигнал → великий
    s += line(400, 150, 470, 150, GREY, 1)
    s += _sine(400, 150, 70, 8, 2, BLUE, 2)
    s += text(435, 120, "слабкий вхід", 9, BLUE, "middle")
    s += arrow(480, 150, 520, 150, GREEN, 2.2)
    s += line(530, 150, 660, 150, GREY, 1)
    s += _sine(530, 150, 130, 34, 2, RED, 2.4)
    s += text(595, 100, "сильний вихід (до ×100)", 9, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Напруга на одному контакті керує струмом крізь інший — твердотільне підсилення, без жодної лампи.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-0-3-point-contact.svg", s)


# ── Рис. 11.0.4 — суперництво ────────────────────────────────────────────────
def fig_t4_rivalry():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Винахід і розкол: хто що зробив", 16, INK, "middle", "bold")
    s += rect(290, 56, 140, 40, "#eef2f6", "#9bb0c2", 1.4, 8)
    s += text(360, 81, "група Bell Labs", 11, INK, "middle", "bold")
    s += arrow(330, 96, 230, 130, GREY, 1.8)
    s += arrow(390, 96, 500, 130, GREY, 1.8)
    s += rect(70, 134, 280, 72, "#fdf1dc", "#d8b46a", 1.4, 8)
    s += text(210, 158, "Бардін + Браттейн", 12, INK, "middle", "bold")
    s += text(210, 178, "точковий транзистор", 10, INK, "middle")
    s += text(210, 196, "грудень 1947 — перший", 9, GREY, "middle")
    s += rect(400, 134, 250, 72, "#fdf1dc", "#d8b46a", 1.4, 8)
    s += text(525, 158, "Шоклі", 12, INK, "middle", "bold")
    s += text(525, 178, "плоскісний транзистор", 10, INK, "middle")
    s += text(525, 196, "1948 — практичний", 9, GREY, "middle")
    # тріщина між ними
    s += _poly([(372, 130), (360, 150), (375, 170), (362, 200)], RED, 2, dash="4,3")
    s += text(360, 232, "суперництво розкололо команду; Бардін згодом пішов із Bell Labs",
              9.5, GREY, "middle", style="italic")
    s += text(360, 252, "Нобелівську премію 1956 року дали всім трьом", 10, INK, "middle", "bold")
    save("fig-11-0-4-rivalry.svg", s)


# ── Рис. 11.0.5 — спадок ─────────────────────────────────────────────────────
def fig_t5_legacy():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Від однієї лампи до мільярдів транзисторів", 16, INK, "middle", "bold")
    # лампа (велика)
    s += _tube(110, 150, 34, 50)
    s += text(110, 222, "лампа", 10, INK, "middle", "bold")
    s += text(110, 238, "1 шт., велика", 8.5, GREY, "middle")
    s += arrow(160, 150, 230, 150, GREY, 2.2)
    # транзистор (малий)
    s += rect(255, 130, 40, 40, "#eef2f6", INK, 1.5)
    s += text(275, 155, "Т", 14, INK, "middle", "bold")
    s += text(275, 222, "транзистор", 10, INK, "middle", "bold")
    s += text(275, 238, "малий, холодний", 8.5, GREY, "middle")
    s += arrow(310, 150, 380, 150, GREY, 2.2)
    # мікросхема (крихітна, багато)
    s += rect(405, 120, 90, 70, "#1f3a6b", "#16294d", 1.5, 4)
    for j in range(4):
        for i in range(6):
            s += rect(414 + i * 13, 128 + j * 15, 9, 9, "none", "#6f86b8", 0.8)
    s += text(450, 222, "мікросхема", 10, INK, "middle", "bold")
    s += text(450, 238, "мільярди на чипі", 8.5, GREY, "middle")
    s += arrow(505, 150, 560, 150, GREY, 2.2)
    s += text(640, 145, "уся цифрова", 10.5, GREEN, "middle", "bold")
    s += text(640, 162, "епоха", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Менший, холодніший, дешевший — і його можна штампувати мільйонами. Так транзистор створив Кремнієву долину.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-0-5-legacy.svg", s)


# ── Рис. 11.1.1 — аналогія крана ─────────────────────────────────────────────
def fig11_valve_analogy():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Кран: легкий поворот руки керує потужним потоком", 15.5, INK, "middle", "bold")
    s += rect(80, 150, 560, 60, "#eaf1fb", "#9bb0c2", 1.4)
    s += circle(360, 180, 38, "#dfe7f0", INK, 2)
    s += line(360, 142, 360, 100, INK, 3) + circle(360, 96, 9, "#d9c9a8", INK, 2)
    s += arrow(388, 100, 362, 100, GREEN, 2)
    s += text(396, 100, "легкий поворот", 10, GREEN, "start", "bold")
    s += text(396, 115, "(малий вплив)", 9, GREY, "start")
    for yy in (168, 192):
        s += arrow(95, yy, 320, yy, BLUE, 3)
        s += arrow(400, yy, 626, yy, BLUE, 3)
    s += text(180, 238, "потужний потік (велика сила)", 10, BLUE, "middle", "bold")
    s += text(W / 2, H - 12, "Воду жене тиск у трубі, рука лише керує. Транзистор робить те саме зі струмом.",
              10, GREY, "middle", style="italic")
    save("fig-11-1-1-valve-analogy.svg", s)


# ── Рис. 11.1.2 — мале керує великим ─────────────────────────────────────────
def fig11_small_controls_large():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 30, "Слабкий сигнал на керувальному виводі править великим струмом", 13.5, INK, "middle", "bold")
    s += rect(290, 110, 120, 100, "#eef2f6", INK, 2, 8)
    s += text(350, 165, "транзистор", 11, INK, "middle", "bold")
    s += line(350, 70, 350, 110, INK, 3) + text(350, 60, "від джерела", 9, INK, "middle")
    s += arrow(350, 80, 350, 108, BLUE, 3)
    s += line(350, 210, 350, 250, INK, 3) + text(350, 266, "до навантаження", 9, INK, "middle")
    s += arrow(350, 212, 350, 248, BLUE, 3)
    s += text(420, 160, "великий струм", 10, BLUE, "start", "bold")
    s += line(232, 160, 290, 160, INK, 2) + arrow(250, 160, 288, 160, GREEN, 2)
    s += text(228, 160, "керування", 10, GREEN, "end", "bold")
    s += text(228, 176, "(слабкий сигнал)", 8.5, GREY, "end")
    s += text(W / 2, H - 10, "Три виводи: два для головного струму, третій — керувальний. Назви й нутро — у §11.2–11.3.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-1-2-small-controls-large.svg", s)


# ── Рис. 11.1.3 — підсилення ─────────────────────────────────────────────────
def fig11_amplify():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Підсилення: слабкий вхід → сильна копія", 15.5, INK, "middle", "bold")
    s += line(70, 150, 170, 150, GREY, 1) + _sine(70, 150, 100, 12, 2, BLUE, 2)
    s += text(120, 116, "слабкий вхід", 9.5, BLUE, "middle", "bold")
    s += arrow(180, 150, 230, 150, INK, 2)
    s += rect(235, 118, 130, 64, "#eef2f6", INK, 2, 8)
    s += text(300, 144, "транзистор", 10.5, INK, "middle", "bold")
    s += text(300, 164, "+ живлення", 9.5, RED, "middle", "bold")
    s += arrow(370, 150, 420, 150, INK, 2)
    s += line(430, 150, 645, 150, GREY, 1) + _sine(430, 150, 210, 46, 2, RED, 2.6)
    s += text(535, 90, "сильна копія (та сама форма)", 9.5, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Транзистор ліпить за слабким зразком потужну копію; енергію бере з живлення.",
              10, GREY, "middle", style="italic")
    save("fig-11-1-3-amplify.svg", s)


# ── Рис. 11.1.4 — перемикання ────────────────────────────────────────────────
def fig11_switch():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Перемикання: малий сигнал вмикає/вимикає великий струм", 14.5, INK, "middle", "bold")
    s += _frame(40, 56, 300, 190, "сигнал = 1 → увімкнено")
    s += rect(150, 120, 80, 60, "#e7f3ea", GREEN, 1.6, 6) + text(190, 155, "відкрито", 10, GREEN, "middle", "bold")
    s += arrow(80, 150, 148, 150, GREEN, 3) + arrow(232, 150, 300, 150, GREEN, 3)
    s += text(190, 206, "великий струм тече", 9.5, GREEN, "middle")
    s += _frame(380, 56, 300, 190, "сигнал = 0 → вимкнено")
    s += rect(490, 120, 80, 60, "#fbeeee", RED, 1.6, 6) + text(530, 155, "закрито", 10, RED, "middle", "bold")
    s += line(420, 150, 490, 150, INK, 2) + line(478, 138, 490, 162, RED, 2.5) + line(490, 138, 478, 162, RED, 2.5)
    s += text(530, 206, "струму нема", 9.5, RED, "middle")
    save("fig-11-1-4-switch.svg", s)


# ── Рис. 11.1.5 — активний проти пасивного ───────────────────────────────────
def fig11_active_vs_passive():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Пасивний лише реагує; активний керує потужністю джерела", 13.5, INK, "middle", "bold")
    s += _frame(40, 56, 300, 200, "пасивні (R, L, C, діод)")
    s += line(60, 132, 168, 132, GREY, 1) + _sine(60, 132, 100, 22, 2, BLUE, 2)
    s += text(110, 100, "вхід", 9, BLUE, "middle")
    s += arrow(175, 132, 210, 132, INK, 2)
    s += line(218, 132, 320, 132, GREY, 1) + _sine(218, 132, 100, 14, 2, BLUE, 2)
    s += text(268, 100, "вихід ≤ вхід", 9, GREY, "middle")
    s += text(190, 238, "віддає не більше, ніж дістав", 9.5, GREY, "middle")
    s += _frame(380, 56, 300, 200, "активний (транзистор)")
    s += line(400, 138, 495, 138, GREY, 1) + _sine(400, 138, 88, 9, 2, BLUE, 2)
    s += text(444, 110, "слабкий вхід", 8.5, BLUE, "middle")
    s += arrow(500, 138, 533, 138, INK, 2)
    s += line(543, 138, 660, 138, GREY, 1) + _sine(543, 138, 112, 30, 2, RED, 2.4)
    s += text(600, 94, "потужний вихід", 9, RED, "middle", "bold")
    s += text(530, 210, "живлення", 9.5, RED, "middle", "bold")
    s += arrow(530, 222, 530, 200, RED, 2)
    s += text(530, 240, "зайву потужність дає джерело", 8.5, GREY, "middle")
    save("fig-11-1-5-active-vs-passive.svg", s)


# ── Рис. 11.1.6 — реле, лампа, транзистор ────────────────────────────────────
def fig11_vs_relay_tube():
    W, H = 740, 280
    s = header(W, H)
    s += text(W / 2, 28, "Та сама робота: реле, лампа, транзистор", 15.5, INK, "middle", "bold")
    s += _frame(30, 60, 220, 180, "реле")
    cl, _ = coil_h(90, 130, 60, 5, 12)
    s += cl
    s += line(150, 110, 150, 150, INK, 2) + line(150, 150, 176, 126, INK, 2) + circle(150, 150, 3, INK, INK)
    s += text(140, 206, "рухомі контакти", 9, INK, "middle")
    s += text(140, 223, "повільне, зношується", 8.5, RED, "middle")
    s += _frame(270, 60, 200, 180, "лампа")
    s += _tube(370, 138, 30, 46)
    s += text(370, 212, "гаряча, велика, крихка", 8.5, RED, "middle")
    s += _frame(490, 60, 220, 180, "транзистор")
    s += rect(560, 112, 80, 55, "#eef2f6", INK, 2, 6) + text(600, 145, "Т", 16, INK, "middle", "bold")
    s += text(600, 206, "малий, холодний, швидкий", 8.5, GREEN, "middle")
    s += text(600, 223, "складаний мільйонами", 8.5, GREEN, "middle")
    save("fig-11-1-6-vs-relay-tube.svg", s)


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


# ── Рис. 11.2.1 — сендвіч ────────────────────────────────────────────────────
def fig21_sandwich():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 30, "BJT — сендвіч із трьох шарів: NPN і PNP", 16, INK, "middle", "bold")

    def bar(y, layers, title):
        t = text(110, y + 36, title, 12, INK, "end", "bold")
        x = 130
        for w_, lab, fill in layers:
            t += rect(x, y, w_, 60, fill, INK, 1.6)
            t += text(x + w_ / 2, y + 37, lab, 15, INK, "middle", "bold")
            x += w_
        return t

    s += bar(80, [(160, "n", LBLUE), (60, "p", LRED), (160, "n", LBLUE)], "NPN")
    s += text(210, 168, "емітер (E)", 9.5, INK, "middle")
    s += text(320, 168, "база (B)", 9.5, RED, "middle")
    s += text(430, 168, "колектор (C)", 9.5, INK, "middle")
    s += bar(210, [(160, "p", LRED), (60, "n", LBLUE), (160, "p", LRED)], "PNP")
    s += text(W / 2, H - 12, "Дві n (чи p) області з тонким протилежним шаром між ними. Центральна база — дуже тонка.",
              10, GREY, "middle", style="italic")
    save("fig-11-2-1-sandwich.svg", s)


# ── Рис. 11.2.2 — три виводи ─────────────────────────────────────────────────
def fig21_terminals():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Три області несиметричні — кожна під свою роль", 15, INK, "middle", "bold")
    s += rect(120, 110, 110, 90, "#bcd0f0", INK, 1.8)
    s += text(175, 152, "емітер", 11, INK, "middle", "bold")
    s += text(175, 170, "n⁺ (сильно)", 9, INK, "middle")
    s += rect(230, 110, 22, 90, "#f6d4d4", INK, 1.8)
    s += rect(252, 110, 200, 90, "#e3edfb", INK, 1.8)
    s += text(352, 152, "колектор", 11, INK, "middle", "bold")
    s += text(352, 170, "n (великий)", 9, INK, "middle")
    s += arrow(175, 92, 175, 108, GREY, 1.6)
    s += text(175, 84, "упорскує носії", 9, INK, "middle")
    s += arrow(241, 250, 241, 202, RED, 1.6)
    s += text(241, 264, "база: кермо (тонка!)", 9, RED, "middle", "bold")
    s += arrow(352, 92, 352, 108, GREY, 1.6)
    s += text(352, 84, "збирає + відводить тепло", 9, INK, "middle")
    s += text(W / 2, H - 12, "Емітер сильно легований, база тонка й слабка, колектор великий. Поміняти емітер із колектором не можна.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-2-2-terminals.svg", s)


# ── Рис. 11.2.3 — два переходи ───────────────────────────────────────────────
def fig21_two_junctions():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Два PN-переходи зі спільною базою: B-E і B-C", 15, INK, "middle", "bold")
    s += rect(130, 86, 150, 58, LBLUE, INK, 1.6) + text(205, 121, "n (E)", 12, INK, "middle", "bold")
    s += rect(280, 86, 48, 58, LRED, INK, 1.6) + text(304, 121, "p (B)", 10.5, INK, "middle", "bold")
    s += rect(328, 86, 150, 58, LBLUE, INK, 1.6) + text(403, 121, "n (C)", 12, INK, "middle", "bold")
    s += line(280, 80, 280, 150, RED, 1.4, dash="4,3") + text(280, 168, "перехід B-E", 9, RED, "middle")
    s += line(328, 80, 328, 150, RED, 1.4, dash="4,3") + text(360, 168, "перехід B-C", 9, RED, "middle")
    s += text(W / 2, 214, "≈ два діоди спина до спини (спільний анод — база)", 10, INK, "middle", "bold")
    bx = 360
    s += line(bx, 232, bx, 252, INK, 2) + text(bx, 268, "база", 9, INK, "middle")
    s += _diode_h(bx - 55, 232, 12, False)
    s += _diode_h(bx + 55, 232, 12, True)
    s += line(bx - 43, 232, bx, 232, INK, 2) + line(bx, 232, bx + 43, 232, INK, 2)
    s += text(bx - 90, 236, "E", 10, INK, "end", "bold") + text(bx + 90, 236, "C", 10, INK, "start", "bold")
    s += line(bx - 67, 232, bx - 90, 232, INK, 2) + line(bx + 67, 232, bx + 90, 232, INK, 2)
    save("fig-11-2-3-two-junctions.svg", s)


# ── Рис. 11.2.4 — не два діоди ───────────────────────────────────────────────
def fig21_not_two_diodes():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Два окремі діоди ≠ транзистор: уся річ у тонкій спільній базі", 13.5, INK, "middle", "bold")
    s += _frame(40, 60, 300, 200, "два окремі діоди")
    s += _diode_h(120, 150, 13, True)
    s += _diode_h(262, 150, 13, False)
    s += line(135, 150, 247, 150, INK, 2)
    s += text(190, 182, "бази товсті, роз'єднані", 9, RED, "middle")
    s += text(190, 202, "носії не переходять", 9, RED, "middle")
    s += text(190, 226, "транзистора немає", 10, RED, "middle", "bold")
    s += _frame(380, 60, 300, 200, "справжній BJT")
    s += rect(420, 120, 90, 50, LBLUE, INK, 1.5) + text(465, 150, "n (E)", 10, INK, "middle")
    s += rect(510, 120, 14, 50, LRED, INK, 1.5)
    s += rect(524, 120, 110, 50, LBLUE, INK, 1.5) + text(579, 150, "n (C)", 10, INK, "middle")
    s += text(517, 110, "тонка база", 8.5, RED, "middle", "bold")
    s += arrow(465, 182, 575, 182, GREEN, 2)
    s += text(530, 202, "носії пролітають наскрізь", 8.5, GREEN, "middle")
    save("fig-11-2-4-not-two-diodes.svg", s)


# ── Рис. 11.2.5 — символи ────────────────────────────────────────────────────
def fig21_symbols():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 30, "Символи NPN і PNP: напрямок стрілки на емітері", 15, INK, "middle", "bold")
    for cx, npn, title in [(200, True, "NPN"), (500, False, "PNP")]:
        s += text(cx, 82, title, 13, INK, "middle", "bold")
        s += _bjt_sym(cx, 160, npn)
        s += text(cx - 48, 164, "Б", 10, INK, "end", "bold")
        s += text(cx + 36, 108, "К", 10, INK, "start", "bold")
        s += text(cx + 36, 220, "Е", 10, INK, "start", "bold")
    s += text(200, 250, "стрілка назовні", 10, GREEN, "middle", "bold")
    s += text(200, 266, "(Not Pointing iN)", 9, GREY, "middle")
    s += text(500, 250, "стрілка всередину", 10, BLUE, "middle", "bold")
    save("fig-11-2-5-symbols.svg", s)


# ── Рис. 11.2.6 — NPN проти PNP ──────────────────────────────────────────────
def fig21_npn_vs_pnp():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "NPN і PNP — доповняльна пара з оберненою полярністю", 14, INK, "middle", "bold")
    s += _frame(40, 56, 300, 200, "NPN")
    s += _bjt_sym(150, 156, True)
    s += text(205, 120, "+ на колекторі", 10, RED, "start", "bold")
    s += text(205, 150, "носії: електрони", 9.5, INK, "start")
    s += text(205, 180, "швидший, поширеніший", 9, GREEN, "start")
    s += _frame(380, 56, 300, 200, "PNP")
    s += _bjt_sym(490, 156, False)
    s += text(545, 120, "− на колекторі", 10, BLUE, "start", "bold")
    s += text(545, 150, "носії: дірки", 9.5, INK, "start")
    s += text(545, 180, "обернена полярність", 9, INK, "start")
    save("fig-11-2-6-npn-vs-pnp.svg", s)


# ── Рис. 11.3.1 — налаштування зміщень ───────────────────────────────────────
def fig31_biasing():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Активний режим: B-E відкрито (пряме), B-C замкнено (зворотне)", 13.5, INK, "middle", "bold")
    s += rect(140, 110, 140, 70, LBLUE, INK, 1.8) + text(210, 152, "n (E)", 13, INK, "middle", "bold")
    s += rect(280, 110, 28, 70, LRED, INK, 1.8) + text(294, 200, "p (B)", 10, INK, "middle", "bold")
    s += rect(308, 110, 200, 70, LBLUE, INK, 1.8) + text(408, 152, "n (C)", 13, INK, "middle", "bold")
    s += line(210, 110, 210, 98, INK, 1.5) + text(210, 92, "−", 13, BLUE, "middle", "bold")
    s += line(294, 110, 294, 98, INK, 1.5) + text(294, 92, "+", 13, RED, "middle", "bold")
    s += line(408, 110, 408, 98, INK, 1.5) + text(408, 92, "+ (сильно)", 11, RED, "middle", "bold")
    s += text(252, 78, "пряме B-E (~0.7 В): відкрито", 9, GREEN, "middle", "bold")
    s += text(408, 78, "зворотне B-C: замкнено", 9, BLUE, "middle", "bold")
    s += text(W / 2, H - 12, "Один перехід відкрили, другий замкнули — і саме поле замкненого B-C ловитиме носії.",
              10, GREY, "middle", style="italic")
    save("fig-11-3-1-biasing.svg", s)


# ── Рис. 11.3.2 — упорскування ───────────────────────────────────────────────
def fig31_injection():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Емітер упорскує повінь електронів у тонку базу", 15, INK, "middle", "bold")
    s += rect(120, 100, 160, 80, LBLUE, INK, 1.8) + text(200, 148, "емітер (n⁺)", 11, INK, "middle", "bold")
    s += rect(280, 100, 30, 80, LRED, INK, 1.8) + text(295, 200, "база (p, тонка)", 9, INK, "middle")
    s += rect(310, 100, 180, 80, LBLUE, INK, 1.8) + text(400, 148, "колектор", 11, INK, "middle")
    for k in range(6):
        y = 114 + k * 11
        s += circle(248 - (k % 3) * 16, y, 4, BLUE, BLUE)
        s += arrow(258, y, 300, y, BLUE, 1.4) if k % 2 == 0 else ""
    s += text(200, 90, "багато електронів →", 9.5, BLUE, "middle", "bold")
    s += text(W / 2, H - 12, "Прямо зміщений перехід відкриває шлюз: сильний емітер жене в базу велику кількість електронів.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-3-2-injection.svg", s)


# ── Рис. 11.3.3 — проліт крізь базу ──────────────────────────────────────────
def fig31_cross_base():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Тонку базу електрони проскакують у колектор; ~1% рекомбінує", 13, INK, "middle", "bold")
    s += rect(120, 100, 150, 80, LBLUE, INK, 1.8) + text(195, 148, "E", 13, INK, "middle", "bold")
    s += rect(270, 100, 26, 80, LRED, INK, 1.8)
    s += rect(296, 100, 200, 80, LBLUE, INK, 1.8) + text(396, 148, "C", 13, INK, "middle", "bold")
    s += text(283, 200, "тонка база", 9, RED, "middle", "bold")
    for k in range(5):
        y = 118 + k * 12
        s += circle(178, y, 3.5, BLUE, BLUE)
        s += arrow(188, y, 440, y, BLUE, 1.6)
    s += text(415, 92, "≈99% у колектор", 9.5, GREEN, "middle", "bold")
    s += circle(283, 150, 3.5, BLUE, BLUE)
    s += line(289, 144, 297, 156, RED, 2) + line(297, 144, 289, 156, RED, 2)
    s += line(283, 206, 283, 180, RED, 1.4)
    s += text(283, 222, "~1% гине тут", 9, RED, "middle", "bold")
    save("fig-11-3-3-cross-base.svg", s)


# ── Рис. 11.3.4 — струм бази ─────────────────────────────────────────────────
def fig31_base_current():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Струм бази — поповнення дірок, що згинули на рекомбінацію", 13, INK, "middle", "bold")
    s += rect(120, 110, 150, 70, LBLUE, INK, 1.8) + text(195, 150, "E", 12, INK, "middle", "bold")
    s += rect(270, 110, 26, 70, LRED, INK, 1.8)
    s += rect(296, 110, 200, 70, LBLUE, INK, 1.8) + text(396, 150, "C", 12, INK, "middle", "bold")
    s += arrow(180, 145, 470, 145, BLUE, 3)
    s += text(370, 132, "великий струм колектора", 9, BLUE, "middle", "bold")
    s += line(283, 110, 283, 78, INK, 2) + arrow(283, 82, 283, 108, GREEN, 2)
    s += text(283, 70, "малий струм бази", 9, GREEN, "middle", "bold")
    s += text(283, 230, "поповнює дірки, що рекомбінували", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Тонка база → мало рекомбінації → крихітний струм бази. Він і є кермо.",
              10, GREY, "middle", style="italic")
    save("fig-11-3-4-base-current.svg", s)


# ── Рис. 11.3.5 — Ic ≈ β·Ib ──────────────────────────────────────────────────
def fig31_ic_ib_ratio():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 28, "Мале керує великим: Ic ≈ β·Ib", 16, INK, "middle", "bold")
    s += text(118, 152, "Ie", 12, INK, "end", "bold")
    s += arrow(125, 150, 248, 150, BLUE, 4)
    s += circle(250, 150, 3, INK, INK)
    s += arrow(258, 148, 470, 118, BLUE, 3.4) + text(480, 114, "Ic (велике)", 11, BLUE, "start", "bold")
    s += arrow(258, 156, 420, 212, GREEN, 1.6) + text(430, 216, "Ib (крихітне)", 10, GREEN, "start", "bold")
    s += text(360, 258, "Ie = Ic + Ib    ·    Ic ≈ β·Ib    (β ≈ 100)", 12.5, INK, "middle", "bold")
    save("fig-11-3-5-ic-ib-ratio.svg", s)


# ── Рис. 11.3.6 — турнікет ───────────────────────────────────────────────────
def fig31_turnstile():
    W, H = 720, 280
    s = header(W, H)
    s += text(W / 2, 28, "Турнікет: крихітне керування пропускає великий потік", 14, INK, "middle", "bold")
    s += rect(330, 90, 16, 110, "#dfe7f0", INK, 2)
    s += line(338, 120, 300, 120, INK, 2.5) + line(338, 140, 300, 140, INK, 2.5)
    for k in range(10):
        x = 120 + (k % 5) * 30
        y = 112 + (k // 5) * 30
        s += circle(x, y, 6, "#cdd6df", INK, 1)
    s += arrow(252, 150, 326, 150, BLUE, 3)
    s += text(200, 202, "великий потік (струм колектора)", 9.5, BLUE, "middle", "bold")
    s += arrow(360, 150, 470, 150, BLUE, 3)
    s += line(338, 108, 338, 92, INK, 1.5)
    s += arrow(396, 100, 360, 100, GREEN, 2)
    s += text(402, 100, "легке керування", 10, GREEN, "start", "bold")
    s += text(402, 115, "(струм бази)", 9, GREY, "start")
    s += text(W / 2, H - 12, "Контролер керує натовпом крихітним зусиллям. Транзистор — той самий турнікет для струму.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-3-6-turnstile.svg", s)


# ── Рис. 11.4.1 — означення β ────────────────────────────────────────────────
def fig41_beta_def():
    W, H = 700, 280
    s = header(W, H)
    s += text(W / 2, 30, "β = Ic / Ib: транзистор множить струм бази на β", 15, INK, "middle", "bold")
    s += text(120, 150, "Ib", 12, GREEN, "end", "bold")
    s += arrow(128, 150, 232, 150, GREEN, 2)
    s += text(180, 134, "1 мА", 9, GREEN, "middle")
    s += rect(235, 110, 120, 90, "#eef2f6", INK, 2, 8)
    s += text(295, 150, "× β", 16, INK, "middle", "bold")
    s += text(295, 172, "(≈100)", 9, GREY, "middle")
    s += arrow(358, 150, 558, 150, BLUE, 4)
    s += text(566, 154, "Ic", 12, BLUE, "start", "bold")
    s += text(470, 132, "100 мА", 10, BLUE, "middle", "bold")
    s += text(W / 2, H - 14, "Ic = β·Ib. Емітер несе суму обох: Ie = Ic + Ib ≈ Ic.", 11, GREY, "middle", style="italic")
    save("fig-11-4-1-beta-def.svg", s)


# ── Рис. 11.4.2 — розкид β ───────────────────────────────────────────────────
def fig41_beta_spread():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "β — не лінія, а широка смуга (розкид між екземплярами)", 14, INK, "middle", "bold")
    ox, oy, w, h = 90, 250, 500, 190
    s += _axes(ox, oy, w, h, "екземпляри (той самий тип)", "β")
    s += rect(ox + 10, oy - h * 0.85, w - 20, h * 0.55, "#fdf1dc", "#d8b46a", 1.2)
    s += text(ox + w * 0.5, oy - h * 0.55, "типовий діапазон β", 10, "#9c6a16", "middle", "bold")
    pts = [(0.1, 0.4), (0.2, 0.72), (0.3, 0.36), (0.45, 0.62), (0.55, 0.8), (0.65, 0.46), (0.78, 0.66), (0.9, 0.55)]
    for fx, fy in pts:
        s += circle(ox + w * fx, oy - h * fy, 5, BLUE, BLUE)
    s += text(ox + w + 2, oy - h * 0.85, "400", 9, GREY, "start")
    s += text(ox + w + 2, oy - h * 0.3, "50", 9, GREY, "start")
    s += text(W / 2, H - 12, "Однакові за маркою транзистори мають дуже різне β. Тому в даташиті — діапазон, не одне число.",
              10, GREY, "middle", style="italic")
    save("fig-11-4-2-beta-spread.svg", s)


# ── Рис. 11.4.3 — β vs Ic ────────────────────────────────────────────────────
def fig41_beta_vs_ic():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "β залежить від струму колектора: пік посередині", 14, INK, "middle", "bold")
    ox, oy, w, h = 90, 250, 500, 190
    s += _axes(ox, oy, w, h, "струм колектора Ic (лог)", "β")
    pts = []
    for i in range(101):
        t = i / 100
        y = 0.25 + 0.65 * math.exp(-((t - 0.5) / 0.28) ** 2)
        pts.append((ox + w * t, oy - h * y))
    s += _poly(pts, BLUE, 2.8)
    s += text(ox + w * 0.5, oy - h * 0.96, "пік", 9.5, BLUE, "middle", "bold")
    s += text(ox + w * 0.12, oy - h * 0.2, "мало", 9, GREY, "middle")
    s += text(ox + w * 0.88, oy - h * 0.2, "мало", 9, GREY, "middle")
    s += text(W / 2, H - 12, "На дуже малих і дуже великих струмах β нижче. «β = 100» — завжди за певних умов.",
              10, GREY, "middle", style="italic")
    save("fig-11-4-3-beta-vs-ic.svg", s)


# ── Рис. 11.4.4 — даташит ────────────────────────────────────────────────────
def fig41_datasheet():
    W, H = 680, 280
    s = header(W, H)
    s += text(W / 2, 30, "hFE у даташиті: діапазон за вказаних умов", 15, INK, "middle", "bold")
    s += rect(150, 78, 380, 110, "#fbfbfb", "#9bb0c2", 1.4, 6)
    s += line(150, 114, 530, 114, "#c9d3dc", 1)
    s += text(190, 102, "параметр", 10, INK, "start", "bold")
    s += text(345, 102, "умови", 10, INK, "middle", "bold")
    s += text(478, 102, "min–typ–max", 10, INK, "middle", "bold")
    s += text(190, 152, "hFE", 13, INK, "start", "bold")
    s += text(345, 152, "Ic=2 мА, Uce=5 В", 9.5, INK, "middle")
    s += text(478, 152, "110 – 290 – 800", 11, RED, "middle", "bold")
    s += arrow(470, 210, 478, 170, GREEN, 1.6)
    s += text(462, 224, "для розрахунку — мінімум (110)", 9.5, GREEN, "end", "bold")
    s += text(W / 2, H - 10, "Завжди дивіться на умови (Ic, Uce) і беріть мінімум для надійності.", 10, GREY, "middle", style="italic")
    save("fig-11-4-4-datasheet.svg", s)


# ── Рис. 11.4.5 — розрахунок кола ────────────────────────────────────────────
def fig41_worked():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Розрахунок: Ib = Ic/β задає резистор бази", 14.5, INK, "middle", "bold")
    s += _bjt_sym(360, 170, True)
    s += line(200, 170, 316, 170, INK, 2)
    s += rect(238, 158, 60, 24, "#ffffff", INK, 1.6) + text(268, 174, "Rб", 10, INK, "middle", "bold")
    s += text(192, 174, "5 В", 10, INK, "end", "bold")
    s += text(268, 150, "≈4.3 кОм", 9, GREY, "middle")
    s += text(268, 202, "Ib = 1 мА", 9, GREEN, "middle", "bold")
    s += line(390, 114, 390, 82, INK, 2) + text(390, 74, "+ живлення", 9, INK, "middle")
    s += rect(420, 120, 24, 34, "#ffffff", INK, 1.4) + text(454, 140, "навантаження", 9, INK, "start")
    s += line(390, 114, 420, 114, INK, 2) + line(432, 120, 432, 114, INK, 2)
    s += text(360, 252, "Ic = 100 мА", 10, BLUE, "middle", "bold")
    s += line(390, 226, 390, 260, INK, 2) + text(390, 274, "земля", 9, INK, "middle")
    s += text(W / 2, H - 8, "Ic=100 мА, β=100 → Ib=1 мА → Rб=(5−0.7)/1мА ≈ 4.3 кОм.", 10.5, INK, "middle", "bold")
    save("fig-11-4-5-worked.svg", s)


# ── Рис. 11.4.6 — запас за β ─────────────────────────────────────────────────
def fig41_design_margin():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Не покладайся на точне β: бери мінімум і додавай запас", 14, INK, "middle", "bold")
    ox, oy = 130, 230
    s += line(ox - 20, oy, ox + 430, oy, INK, 1.4)
    s += rect(ox, oy - 38, 90, 38, "#e7f3ea", GREEN, 1.4)
    s += text(ox + 45, oy + 16, "β=100: 1 мА", 9, INK, "middle")
    s += rect(ox + 150, oy - 64, 90, 64, "#fdf1dc", "#d8b46a", 1.4)
    s += text(ox + 195, oy + 16, "β=40: 2.5 мА", 9, INK, "middle")
    s += rect(ox + 300, oy - 92, 90, 92, "#e9eefb", BLUE, 1.4)
    s += text(ox + 345, oy + 16, "подаємо 3 мА", 9, BLUE, "middle", "bold")
    s += text(ox + 345, oy - 102, "запас!", 10, GREEN, "middle", "bold")
    s += text(ox + 45, oy - 48, "треба", 8.5, GREY, "middle")
    s += text(ox + 195, oy - 74, "треба", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Подавши струм бази із запасом, відкриєш транзистор за будь-якого β — схема не залежить від розкиду.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-4-6-design-margin.svg", s)


# ── Рис. 11.5.1 — три режими ─────────────────────────────────────────────────
def fig51_three_modes():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Три режими BJT за станом двох переходів", 15.5, INK, "middle", "bold")
    rows = [("ВІДСІЧКА", "B-E і B-C закриті", "Ic ≈ 0", "ключ ВИМК.", "#fbeeee", RED),
            ("АКТИВНИЙ", "B-E відкр., B-C закр.", "Ic = β·Ib", "підсилювач", "#fdf1dc", "#9c6a16"),
            ("НАСИЧЕННЯ", "обидва відкриті", "Uce ≈ 0.2 В", "ключ УВІМК.", "#e7f3ea", GREEN)]
    y = 66
    for nm, bias, ic, use, fill, col in rows:
        s += rect(50, y, 620, 62, fill, "#9bb0c2", 1.3, 8)
        s += text(130, y + 38, nm, 13, col, "middle", "bold")
        s += line(210, y + 8, 210, y + 54, "#c9d3dc", 1)
        s += text(330, y + 26, bias, 10, INK, "middle")
        s += text(330, y + 46, ic, 10.5, INK, "middle", "bold")
        s += line(450, y + 8, 450, y + 54, "#c9d3dc", 1)
        s += text(560, y + 38, use, 11, col, "middle", "bold")
        y += 74
    save("fig-11-5-1-three-modes.svg", s)


def _mode_panel(s, title, base_lbl, base_col, ic_lbl, ic_col, equiv, eq_col, cx=340):
    s += _bjt_sym(cx, 160, True)
    s += line(200, 160, cx - 44, 160, INK, 2)
    s += text((200 + cx - 44) / 2, 144, base_lbl, 10, base_col, "middle", "bold")
    s += line(cx + 30, 104, cx + 30, 74, INK, 2) + text(cx + 30, 66, "+", 11, INK, "middle", "bold")
    s += line(cx + 30, 216, cx + 30, 250, INK, 2) + text(cx + 30, 264, "земля", 8.5, INK, "middle")
    s += text(cx + 70, 156, ic_lbl, 11.5, ic_col, "start", "bold")
    s += text(560, 118, equiv, 10.5, eq_col, "middle", "bold")
    return s


# ── Рис. 11.5.2 — відсічка ───────────────────────────────────────────────────
def fig51_cutoff():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 28, "Відсічка: транзистор закритий (розімкнений ключ)", 14.5, INK, "middle", "bold")
    s = _mode_panel(s, "", "Ib = 0", RED, "Ic ≈ 0", RED, "≈ розімкнено", RED)
    s += line(515, 150, 545, 150, INK, 2) + line(560, 150, 588, 132, INK, 2) + circle(560, 150, 3, INK, INK)
    s += text(W / 2, H - 12, "Бази не живимо — колектора нема. Транзистор як розімкнений вимикач: стан «0».",
              10, GREY, "middle", style="italic")
    save("fig-11-5-2-cutoff.svg", s)


# ── Рис. 11.5.3 — активний ───────────────────────────────────────────────────
def fig51_active():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 28, "Активний: Ic = β·Ib (пропорційно) — підсилювач", 14.5, INK, "middle", "bold")
    s = _mode_panel(s, "", "Ib помірний", GREEN, "Ic = β·Ib", BLUE, "пропорційно", "#9c6a16")
    s += _sine(515, 150, 90, 18, 2, "#9c6a16", 2)
    s += text(W / 2, H - 12, "B-E відкрито, B-C закрито. Струм колектора слухняно йде за струмом бази — тут підсилюють.",
              10, GREY, "middle", style="italic")
    save("fig-11-5-3-active.svg", s)


# ── Рис. 11.5.4 — насичення ──────────────────────────────────────────────────
def fig51_saturation():
    W, H = 680, 290
    s = header(W, H)
    s += text(W / 2, 28, "Насичення: відкрито навстіж, Uce≈0.2 В (замкнений ключ)", 13.5, INK, "middle", "bold")
    s = _mode_panel(s, "", "Ib великий", GREEN, "Uce ≈ 0.2 В", GREEN, "≈ замкнено", GREEN)
    s += line(515, 150, 588, 150, INK, 2)
    s += text(410, 178, "Ic = стеля кола", 9.5, INK, "start")
    s += text(W / 2, H - 12, "Обидва переходи відкриті. Струм задає коло, не β·Ib; падіння лише ~0.2 В. Стан «1».",
              10, GREY, "middle", style="italic")
    save("fig-11-5-4-saturation.svg", s)


# ── Рис. 11.5.5 — Ic(Ib) ─────────────────────────────────────────────────────
def fig51_transfer():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Ic залежно від Ib: відсічка → активний → насичення", 14, INK, "middle", "bold")
    ox, oy, w, h = 90, 250, 500, 200
    s += _axes(ox, oy, w, h, "струм бази Ib", "струм колектора Ic")
    s += _poly([(ox, oy), (ox + 30, oy), (ox + 330, oy - h * 0.82), (ox + w, oy - h * 0.82)], BLUE, 2.8)
    s += text(ox + 60, oy - 12, "відсічка", 9, GREY, "middle")
    s += text(ox + 175, oy - h * 0.46, "активний (нахил = β)", 9.5, RED, "middle", "bold")
    s += text(ox + 415, oy - h * 0.82 - 8, "насичення (стеля)", 9.5, GREEN, "middle", "bold")
    s += line(ox + 330, oy, ox + 330, oy - h * 0.82, GREY, 1, dash="3,3")
    s += text(W / 2, H - 12, "На нахилі (активний) працює підсилювач; між пласкими ділянками (відсічка/насичення) — ключ.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-5-5-transfer.svg", s)


# ── Рис. 11.5.6 — вихідні характеристики ─────────────────────────────────────
def fig51_output_curves():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Вихідні характеристики: Ic vs Uce за різних Ib", 14, INK, "middle", "bold")
    ox, oy, w, h = 90, 250, 500, 200
    s += _axes(ox, oy, w, h, "Uce", "Ic")
    subs = ["₁", "₂", "₃", "₄"]
    for k, lvl in enumerate([0.22, 0.42, 0.62, 0.82]):
        pts = []
        for i in range(101):
            vce = i / 100
            y = lvl * (1 - math.exp(-vce / 0.055))
            pts.append((ox + w * vce, oy - h * y))
        s += _poly(pts, BLUE, 2.2)
        s += text(ox + w + 4, oy - h * lvl, "Ib" + subs[k], 8.5, BLUE, "start")
    s += line(ox + w * 0.09, oy, ox + w * 0.09, oy - h, GREY, 1, dash="3,3")
    s += text(ox + w * 0.045, oy - h * 0.96, "насич.", 8, GREEN, "middle", "bold")
    s += text(ox + w * 0.55, oy - h * 0.97, "активний (полиці)", 9.5, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Плоскі полиці — активний (підсилювач); крутий злам біля Uce≈0 — насичення (ключ).",
              9.5, GREY, "middle", style="italic")
    save("fig-11-5-6-output-curves.svg", s)


# ── Рис. 11.6.1 — МК + транзистор + реле ─────────────────────────────────────
def fig62_mcu_drives_relay():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Вивід МК не тягне реле напряму — транзистор стає м'язом", 13.5, INK, "middle", "bold")
    s += rect(60, 120, 110, 80, "#eef2f6", INK, 1.8, 6)
    s += text(115, 155, "мікро-", 10, INK, "middle", "bold") + text(115, 172, "контролер", 10, INK, "middle", "bold")
    s += text(115, 214, "вивід: ~20 мА", 9, GREY, "middle")
    s += arrow(175, 160, 235, 160, GREEN, 2) + text(205, 148, "сигнал", 8.5, GREEN, "middle")
    s += rect(240, 130, 90, 60, "#eef2f6", INK, 1.8, 6) + text(285, 165, "транзистор", 9.5, INK, "middle", "bold")
    s += text(285, 210, "живлення окреме", 8.5, RED, "middle")
    s += arrow(335, 160, 398, 160, BLUE, 3) + text(366, 146, "багато струму", 8.5, BLUE, "middle", "bold")
    cl, _ = coil_h(455, 160, 60, 5, 12)
    s += cl
    s += text(455, 126, "реле / мотор", 10, COPP, "middle", "bold")
    s += text(455, 200, "десятки мА – ампери", 9, INK, "middle")
    s += text(W / 2, H - 12, "Кволий струм виводу керує базою; потужний струм навантаження транзистор бере з окремого джерела.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-6-1-mcu-drives-relay.svg", s)


# ── Рис. 11.6.2 — схема ключа ────────────────────────────────────────────────
def fig62_switch_circuit():
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 28, "Ключ на NPN (нижнє плече)", 15.5, INK, "middle", "bold")
    s += line(120, 68, 520, 68, RED, 2) + text(112, 72, "+V", 11, RED, "end", "bold")
    s += rect(370, 86, 40, 40, "#ffffff", INK, 1.6) + text(440, 110, "навантаження", 10, INK, "start")
    s += line(390, 68, 390, 86, INK, 2) + line(390, 126, 390, 124, INK, 2)
    s += _bjt_sym(360, 180, True)
    s += line(390, 236, 390, 272, INK, 2)
    s += line(120, 272, 520, 272, INK, 1.4) + text(112, 276, "GND", 10, INK, "end", "bold")
    s += line(200, 180, 316, 180, INK, 2)
    s += rect(228, 168, 56, 24, "#ffffff", INK, 1.6) + text(256, 184, "Rб", 10, INK, "middle", "bold")
    s += text(196, 184, "сигнал", 10, GREEN, "end", "bold")
    s += text(256, 158, "(від МК)", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Навантаження — між +V і колектором; емітер — на землі; база — через резистор від сигналу.",
              10, GREY, "middle", style="italic")
    save("fig-11-6-2-switch-circuit.svg", s)


# ── Рис. 11.6.3 — увімк./вимк. ───────────────────────────────────────────────
def fig62_on_off():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Дві крайні точки: «1» — насичення, «0» — відсічка", 14, INK, "middle", "bold")
    s += _frame(40, 56, 300, 200, "сигнал = 1 → УВІМКНЕНО")
    s += circle(230, 92, 13, "#fff3b0", SUN, 2) + text(230, 74, "навант.", 8.5, INK, "middle")
    s += line(230, 105, 230, 130, INK, 1.5)
    s += _bjt_sym(200, 170, True)
    s += text(120, 170, "+", 12, RED, "end", "bold") + arrow(128, 170, 154, 170, GREEN, 2)
    s += text(190, 235, "насичення: струм тече", 9.5, GREEN, "middle", "bold")
    s += _frame(380, 56, 300, 200, "сигнал = 0 → ВИМКНЕНО")
    s += circle(570, 92, 13, "#e4e4e4", "#9bb0c2", 2) + text(570, 74, "навант.", 8.5, INK, "middle")
    s += line(570, 105, 570, 130, INK, 1.5)
    s += _bjt_sym(540, 170, True)
    s += text(460, 170, "0", 12, BLUE, "end", "bold") + line(468, 170, 494, 170, INK, 2)
    s += text(530, 235, "відсічка: струму нема", 9.5, RED, "middle", "bold")
    save("fig-11-6-3-on-off.svg", s)


# ── Рис. 11.6.4 — резистор бази ──────────────────────────────────────────────
def fig62_base_resistor():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Резистор бази: β мінімальне + запас струму", 14, INK, "middle", "bold")
    steps = ["1)  Ic — потрібний струм навантаження",
             "2)  Ib(мін) = Ic / β(мін)   (мінімальне β з даташита)",
             "3)  запас:  Ib ≈ 3…10 × Ib(мін)",
             "4)  R = (U(сигналу) − 0.7) / Ib"]
    y = 78
    for st in steps:
        s += rect(80, y, 540, 40, "#fbfbfb", "#c9d3dc", 1.2, 6)
        s += text(102, y + 25, st, 12, INK, "start", "bold")
        y += 50
    s += text(W / 2, H - 12, "Приклад: реле 60 мА, β(мін)=50 → Ib(мін)=1.2 мА → ×3 → R ≈ 1.2 кОм.",
              11, INK, "middle", "bold")
    save("fig-11-6-4-base-resistor.svg", s)


# ── Рис. 11.6.5 — гасний діод ────────────────────────────────────────────────
def fig62_flyback():
    W, H = 680, 310
    s = header(W, H)
    s += text(W / 2, 28, "Індуктивне навантаження — обов'язково гасний діод", 14, INK, "middle", "bold")
    s += line(120, 66, 520, 66, RED, 2) + text(112, 70, "+V", 11, RED, "end", "bold")
    s += rect(310, 84, 50, 56, "#ffffff", INK, 1.6)
    s += text(335, 106, "реле", 10, INK, "middle", "bold") + text(335, 122, "(L)", 9, INK, "middle")
    s += line(335, 66, 335, 84, INK, 2) + line(335, 140, 335, 150, INK, 2)
    dx = 432
    s += line(dx, 66, dx, 90, INK, 2)
    s += f'<path d="M {dx-9},120 L {dx+9},120 L {dx},92 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.5"/>\n'
    s += line(dx - 9, 90, dx + 9, 90, INK, 2.2)
    s += line(dx, 120, dx, 150, INK, 2)
    s += text(dx + 14, 106, "гасний діод", 9.5, GREEN, "start", "bold")
    s += text(dx + 14, 120, "(катод до +V)", 8.5, GREY, "start")
    s += line(335, 150, dx, 150, INK, 2)
    s += _bjt_sym(305, 200, True)
    s += line(335, 150, 335, 144, INK, 2)
    s += line(335, 256, 335, 286, INK, 2)
    s += line(120, 286, 520, 286, INK, 1.4) + text(112, 290, "GND", 9, INK, "end", "bold")
    s += line(180, 200, 261, 200, INK, 2)
    s += rect(200, 188, 48, 24, "#ffffff", INK, 1.5) + text(224, 204, "Rб", 9, INK, "middle", "bold")
    s += text(176, 204, "сигнал", 9, GREEN, "end", "bold")
    s += text(W / 2, H - 10, "Гасний діод паралельно котушці зрізає сплеск при вимкненні — без нього транзистор гине.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-6-5-flyback.svg", s)


# ── Рис. 11.6.6 — нижнє/верхнє плече ──────────────────────────────────────────
def fig62_low_vs_high_side():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Нижнє плече (NPN) проти верхнього (PNP)", 14.5, INK, "middle", "bold")
    s += _frame(40, 56, 300, 200, "нижнє плече (NPN)")
    s += line(70, 80, 310, 80, RED, 1.6) + text(64, 84, "+", 9, RED, "end", "bold")
    s += rect(165, 96, 50, 34, "#e3edfb", "#9bb0c2", 1.4, 4) + text(190, 117, "навант.", 9, INK, "middle")
    s += line(190, 80, 190, 96, INK, 1.6)
    s += rect(165, 150, 50, 40, "#eef2f6", INK, 1.6, 4) + text(190, 174, "NPN", 10, INK, "middle", "bold")
    s += line(190, 130, 190, 150, INK, 1.6)
    s += line(190, 190, 190, 228, INK, 1.6) + line(70, 228, 310, 228, INK, 1.4) + text(64, 232, "GND", 8, INK, "end")
    s += text(190, 248, "комутує землю", 9, INK, "middle")
    s += _frame(380, 56, 300, 200, "верхнє плече (PNP)")
    s += line(410, 80, 650, 80, RED, 1.6) + text(404, 84, "+", 9, RED, "end", "bold")
    s += rect(505, 92, 50, 40, "#fbeeee", INK, 1.6, 4) + text(530, 116, "PNP", 10, INK, "middle", "bold")
    s += line(530, 80, 530, 92, INK, 1.6)
    s += rect(505, 152, 50, 34, "#e3edfb", "#9bb0c2", 1.4, 4) + text(530, 173, "навант.", 9, INK, "middle")
    s += line(530, 132, 530, 152, INK, 1.6)
    s += line(530, 186, 530, 228, INK, 1.6) + line(410, 228, 650, 228, INK, 1.4) + text(404, 232, "GND", 8, INK, "end")
    s += text(530, 248, "навантаження на землі", 8.5, INK, "middle")
    save("fig-11-6-6-low-vs-high-side.svg", s)


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


# ── Рис. 11.7.1 — навіщо зміщення ────────────────────────────────────────────
def fig71_bias_point():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 28, "Навіщо зміщення: тримати сигнал в активній зоні", 15.5, INK, "middle", "bold")
    # LEFT — без зміщення → зріз
    s += _frame(40, 52, 300, 250, "без зміщення → зріз")
    bx = 70
    s += line(bx, 130, bx + 244, 130, GREY, 1.2) + text(bx - 4, 134, "0", 9.5, GREY, "end")
    s += line(bx, 118, bx + 244, 118, GREY, 1.4, "5 4") + text(bx + 246, 116, "поріг ~0.6 В", 8.5, GREY, "start")
    s += _sine(bx, 130, 244, 34, 2, BLUE, 2.2)
    s += text(bx + 60, 84, "вхід  ±", 9.5, BLUE, "middle", "bold")
    # вихідний струм: тільки те, що вище порога → півхвилі
    s += line(bx, 270, bx + 244, 270, GREY, 1.2)
    s += _clip_sine(bx, 270, 244, 38, 2, RED, lo=0.0)
    s += text(bx + 90, 296, "струм колектора — зрізаний", 8.5, RED, "middle", "bold")
    # RIGHT — зі зміщенням → цілий
    s += _frame(380, 52, 300, 250, "зі зміщенням → цілий")
    rx = 410
    s += line(rx, 150, rx + 244, 150, GREY, 1.2) + text(rx - 4, 154, "0", 9.5, GREY, "end")
    s += line(rx, 108, rx + 244, 108, GREEN, 1.6, "5 4") + text(rx + 246, 106, "зміщення", 8.5, GREEN, "start")
    s += _sine(rx, 108, 244, 30, 2, BLUE, 2.2)
    s += text(rx + 60, 84, "вхід + зміщення", 9, BLUE, "middle", "bold")
    s += line(rx, 270, rx + 244, 270, GREY, 1.2)
    s += _sine(rx, 270, 244, 32, 2, RED, 2.4)
    s += text(rx + 90, 296, "струм колектора — цілий", 8.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "База проводить лише вище ~0.6 В; піднявши сигнал на зміщення, тримаємо його весь в активній зоні.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-1-bias-point.svg", s)


# ── Рис. 11.7.2 — спільний емітер ────────────────────────────────────────────
def fig71_common_emitter():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 26, "Каскад зі спільним емітером", 16, INK, "middle", "bold")
    TOP, GND = 66, 318
    s += line(110, TOP, 650, TOP, RED, 2) + text(104, TOP + 4, "+V", 11, RED, "end", "bold")
    s += line(110, GND, 650, GND, INK, 1.5) + text(104, GND + 4, "GND", 10, INK, "end", "bold")
    s += _bjt_sym(440, 200, True)
    cx_c, cy_c = 470, 144   # вузол колектора
    cx_e, cy_e = 470, 256   # емітер
    # Rc (колектор) і Re (емітер)
    s += rect(456, 92, 28, 32, "#ffffff", INK, 1.6) + text(450, 112, "Rc", 11, INK, "end", "bold")
    s += line(470, TOP, 470, 92, INK, 2) + line(470, 124, 470, cy_c, INK, 2)
    s += rect(456, 262, 28, 32, "#ffffff", INK, 1.6) + text(450, 282, "Re", 11, INK, "end", "bold")
    s += line(cx_e, cy_e, cx_e, 262, INK, 2) + line(470, 294, 470, GND, INK, 2)
    # дільник R1/R2 на базі
    nbx, nby = 300, 200
    s += line(nbx, nby, 396, nby, INK, 2) + circle(nbx, nby, 3, INK, INK)
    s += rect(286, 108, 28, 32, "#ffffff", INK, 1.6) + text(280, 128, "R1", 11, INK, "end", "bold")
    s += line(nbx, TOP, nbx, 108, INK, 2) + line(nbx, 140, nbx, nby, INK, 2)
    s += rect(286, 250, 28, 32, "#ffffff", INK, 1.6) + text(280, 270, "R2", 11, INK, "end", "bold")
    s += line(nbx, nby, nbx, 250, INK, 2) + line(nbx, 282, nbx, GND, INK, 2)
    # вхідний конденсатор зв'язку
    s += line(120, nby, 228, nby, INK, 2) + _cap_h(235, nby) + line(242, nby, nbx, nby, INK, 2)
    s += text(235, nby - 22, "Cвх", 10, BLUE, "middle", "bold")
    s += text(120, nby - 12, "вхід ~", 10, GREEN, "start", "bold")
    # вихідний конденсатор зв'язку від колектора
    s += circle(cx_c, cy_c, 3, INK, INK)
    s += line(cx_c, cy_c, 560, cy_c, INK, 2) + _cap_h(575, cy_c) + line(582, cy_c, 650, cy_c, INK, 2)
    s += text(575, cy_c - 22, "Cвих", 10, BLUE, "middle", "bold")
    s += text(650, cy_c - 12, "вихід ~", 10, RED, "end", "bold")
    s += text(W / 2, H - 10, "Дільник тримає робочу точку; конденсатори пускають сигнал, але не чіпають зміщення; Rc робить зі струму напругу.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-2-common-emitter.svg", s)


# ── Рис. 11.7.3 — інверсія ───────────────────────────────────────────────────
def fig71_inversion():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Підсилення з інверсією: база вгору → колектор униз", 15, INK, "middle", "bold")
    # вхід
    s += _sine(60, 165, 180, 22, 1.5, BLUE, 2.4)
    s += line(60, 165, 240, 165, GREY, 1)
    s += text(150, 110, "вхід (на базі)", 10, BLUE, "middle", "bold")
    s += arrow(150, 150, 150, 128, GREEN, 2.2) + text(168, 132, "база ↑", 9.5, GREEN, "start", "bold")
    # центр: BJT з Rc до +V
    s += line(300, 92, 360, 92, RED, 2) + text(294, 96, "+V", 9.5, RED, "end", "bold")
    s += rect(316, 104, 26, 28, "#ffffff", INK, 1.5) + text(348, 122, "Rc", 9.5, INK, "start", "bold")
    s += line(329, 92, 329, 104, INK, 1.8) + line(329, 132, 329, 158, INK, 1.8)
    s += _bjt_sym(320, 186, True)
    s += line(290, 186, 276, 186, INK, 1.6) + text(272, 190, "вх.", 8.5, BLUE, "end")
    # вихід (інвертований, більший)
    s += _clip_sine(470, 165, 190, 60, 1.5, RED, phase=math.pi)
    s += line(470, 165, 660, 165, GREY, 1)
    s += text(565, 246, "вихід (з колектора)", 10, RED, "middle", "bold")
    s += arrow(565, 180, 565, 224, RED, 2.2) + text(583, 214, "колектор ↓", 9.5, RED, "start", "bold")
    s += text(W / 2, H - 10, "Більший струм сильніше «садить» напругу на Rc — тому вихід рухається протилежно до входу.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-3-inversion.svg", s)


# ── Рис. 11.7.4 — підсилення задають резистори ───────────────────────────────
def fig71_gain():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Підсилення задають резистори, а не примхливе β", 15, INK, "middle", "bold")
    # формула
    s += rect(60, 70, 300, 80, LGRN, "#9bb0c2", 1.6, 8)
    s += text(210, 104, "A  ≈  − Rc / Re", 24, GREEN, "middle", "bold")
    s += text(210, 134, "наприклад  −10 кОм / 1 кОм = −10", 11, INK, "middle")
    # від'ємний зворотний зв'язок
    s += text(210, 182, "Re дає від'ємний зворотний зв'язок:", 11, INK, "middle", "bold")
    s += text(210, 204, "трохи менше підсилення — зате стабільне", 10.5, INK, "middle")
    s += arrow(120, 226, 300, 226, BLUE, 2) + text(210, 246, "вихід коригує сам себе", 9.5, BLUE, "middle")
    # бар-чарт: β різне, A те саме
    bx, by = 430, 250
    s += text(560, 70, "β гуляє в рази…", 11, INK, "middle", "bold")
    betas = [("β=100", 60), ("β=300", 120), ("β=600", 175)]
    for i, (lab, h) in enumerate(betas):
        x = bx + i * 64
        s += rect(x, by - h, 40, h, LBLUE, BLUE, 1.4)
        s += text(x + 20, by + 16, lab, 9, INK, "middle")
    s += line(bx - 10, by - 90, bx + 200, by - 90, GREEN, 2.2, "6 4")
    s += text(bx + 205, by - 86, "A", 12, GREEN, "start", "bold")
    s += text(560, 92, "…а підсилення A — майже ні", 10, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "П'ятиразовий розкид β майже не зачіпає A — його тримають зовнішні резистори. Передбачуваність важливіша.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-4-gain.svg", s)


# ── Рис. 11.7.5 — кліпування ─────────────────────────────────────────────────
def fig71_clipping():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Завеликий сигнал упирається в межі — кліпування", 15, INK, "middle", "bold")
    for ox, title, amp, clip in [(70, "у межах → чисто", 40, False), (400, "завелике → зріз верхівок", 80, True)]:
        s += _frame(ox - 30, 52, 280, 224, title)
        cyc = 1.8
        cy = 170
        s += line(ox - 12, 96, ox + 234, 96, RED, 1.5, "5 4") + text(ox - 16, 100, "+V", 8.5, RED, "end", "bold")
        s += line(ox - 12, 244, ox + 234, 244, BLUE, 1.5, "5 4") + text(ox - 16, 248, "насич.", 8.5, BLUE, "end", "bold")
        s += line(ox - 12, cy, ox + 234, cy, GREY, 1)
        if clip:
            s += _clip_sine(ox, cy, 234, amp, cyc, RED, lo=-0.92, hi=0.92)
            s += text(ox + 110, 88, "зрізано", 9, RED, "middle", "bold")
            s += text(ox + 110, 264, "зрізано", 9, BLUE, "middle", "bold")
        else:
            s += _sine(ox, cy, 234, amp, cyc, GREEN, 2.4)
            s += text(ox + 110, 130, "цілий", 9, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Стеля — напруга живлення, підлога — насичення. Вийшов за них — верхівки плоскі, звук хрипить.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-5-clipping.svg", s)


# ── Рис. 11.7.6 — емітерний повторювач ───────────────────────────────────────
def fig71_emitter_follower():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 26, "Емітерний повторювач (буфер): A≈1, але сила є", 15.5, INK, "middle", "bold")
    TOP, GND = 66, 300
    s += line(150, TOP, 620, TOP, RED, 2) + text(144, TOP + 4, "+V", 11, RED, "end", "bold")
    s += line(150, GND, 620, GND, INK, 1.5) + text(144, GND + 4, "GND", 10, INK, "end", "bold")
    s += _bjt_sym(400, 175, True)
    # колектор прямо на +V (без Rc)
    s += line(430, 119, 430, TOP, INK, 2) + text(438, 104, "колектор → +V", 9, GREY, "start")
    # емітер → вузол виходу → Re до землі
    s += line(430, 231, 430, 246, INK, 2) + circle(430, 246, 3, INK, INK)
    s += rect(416, 256, 28, 30, "#ffffff", INK, 1.6) + text(410, 276, "Re", 11, INK, "end", "bold")
    s += line(430, 246, 430, 256, INK, 2) + line(430, 286, 430, GND, INK, 2)
    # вхід — слабке джерело
    s += rect(96, 150, 86, 54, LBLUE, "#9bb0c2", 1.4, 6)
    s += text(139, 172, "слабке", 9.5, INK, "middle") + text(139, 188, "джерело", 9.5, INK, "middle")
    s += line(182, 177, 356, 177, INK, 2) + text(250, 166, "великий Zвх", 9, GREEN, "middle", "bold")
    # вихід — важке навантаження
    s += line(430, 246, 560, 246, INK, 2) + text(498, 234, "малий Zвих", 9, RED, "middle", "bold")
    s += rect(560, 218, 96, 56, LRED, "#9bb0c2", 1.4, 6)
    s += text(608, 240, "важке", 9.5, INK, "middle") + text(608, 256, "навантаження", 9.5, INK, "middle")
    s += text(430, 168, "Uвих ≈ Uвх", 10, INK, "start", "bold")
    s += text(W / 2, H - 10, "Напруга проходить без змін, та слабке джерело тепер розгойдує важке навантаження, не просідаючи.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-6-emitter-follower.svg", s)


# ── хелпер: спрощений символ N-канального MOSFET ─────────────────────────────
def _mosfet_sym(cx, cy):
    t = line(cx - 44, cy, cx - 22, cy, INK, 2)          # затвор (лід)
    t += line(cx - 22, cy - 22, cx - 22, cy + 22, INK, 2.4)   # пластина затвора
    t += line(cx - 12, cy - 22, cx - 12, cy + 22, INK, 2.4)   # канал (ізол. зазор)
    t += line(cx - 12, cy - 16, cx + 24, cy - 16, INK, 2) + line(cx + 24, cy - 16, cx + 24, cy - 44, INK, 2)  # стік
    t += line(cx - 12, cy + 16, cx + 24, cy + 16, INK, 2) + line(cx + 24, cy + 16, cx + 24, cy + 44, INK, 2)  # витік
    t += arrow(cx - 12, cy, cx + 4, cy, INK, 1.8)        # стрілка тіла (n-канал)
    return t


# ── Рис. 11.8.1 — параметри даташита ─────────────────────────────────────────
def fig81_datasheet():
    W, H = 760, 384
    s = header(W, H)
    s += text(W / 2, 30, "Сім рядків даташита, що вирішують вибір", 16, INK, "middle", "bold")
    cols = [(56, 150, "параметр"), (206, 116, "приклад"), (322, 382, "що вирішує")]
    y = 64
    for x, w, lab in cols:
        s += rect(x, y, w, 28, "#eef2f6", "#c9d3dc", 1.2)
        s += text(x + w / 2, y + 19, lab, 11, INK, "middle", "bold")
    rows = [
        ("Ic(max)", "600 мА", "струм навантаження ×2", LRED),
        ("Vceo", "40 В", "живлення + викиди", LRED),
        ("Ptot", "0.5 Вт", "грійка P = Vce·Ic", LRED),
        ("hFE (β)", "75…300", "бери β(min)!", LGRN),
        ("Vce(sat)", "0.3 В", "менше → холодніше", LGRN),
        ("fT", "250 МГц", "швидкість перемикання", LGRN),
        ("корпус", "TO-92", "під потужність / радіатор", LGRN),
    ]
    y = 92
    for name, val, role, fill in rows:
        for x, w, _ in cols:
            s += rect(x, y, w, 36, fill, "#d7dee5", 1.1)
        s += text(cols[0][0] + 12, y + 23, name, 12, INK, "start", "bold")
        s += text(cols[1][0] + cols[1][1] / 2, y + 23, val, 12, BLUE, "middle", "bold")
        s += text(cols[2][0] + 14, y + 23, role, 11.5, INK, "start")
        y += 36
    s += text(58, y + 22, "червоні — граничні (не перевищувати)", 10.5, RED, "start", "bold")
    s += text(58, y + 40, "зелені — робочі (для розрахунку бери гірший кут: β(min), Vce(sat) max)", 10.5, GREEN, "start", "bold")
    save("fig-11-8-1-datasheet-params.svg", s)


# ── Рис. 11.8.2 — драйвер реле з числами ─────────────────────────────────────
def fig81_relay_worked():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 28, "Драйвер реле: повний розрахунок на схемі", 15.5, INK, "middle", "bold")
    TOP, GND = 70, 312
    s += line(120, TOP, 600, TOP, RED, 2) + text(114, TOP + 4, "+5 В", 11, RED, "end", "bold")
    s += line(120, GND, 600, GND, INK, 1.5) + text(114, GND + 4, "GND", 10, INK, "end", "bold")
    s += _bjt_sym(400, 200, True)
    cx_c = 430
    # котушка реле між +V і колектором
    s += rect(408, 92, 44, 44, "#fff7e6", COPP, 1.6, 4)
    s += text(430, 112, "реле", 10, INK, "middle", "bold") + text(430, 127, "5В·70мА", 8.5, INK, "middle")
    s += line(cx_c, TOP, cx_c, 92, INK, 2) + line(cx_c, 136, cx_c, 144, INK, 2)
    # гасний діод паралельно котушці (катод догори, до +V)
    dbx = 520
    s += line(cx_c, 144, dbx, 144, INK, 1.8) + line(dbx, 144, dbx, 124, INK, 1.8)
    s += f'<path d="M {dbx-9},124 L {dbx+9},124 L {dbx},108 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.5"/>\n'
    s += line(dbx - 9, 104, dbx + 9, 104, INK, 2.4)   # катод-смуга
    s += line(dbx, 104, dbx, TOP, INK, 1.8) + line(dbx, TOP, cx_c, TOP, INK, 1.8)
    s += text(dbx + 14, 116, "гасний", 9, GREEN, "start", "bold") + text(dbx + 14, 130, "діод", 9, GREEN, "start", "bold")
    # емітер на землю
    s += line(cx_c, 256, cx_c, GND, INK, 2)
    # база через резистор від МК
    s += rect(250, 188, 60, 24, "#ffffff", INK, 1.6) + text(280, 204, "Rb 560Ω", 10, INK, "middle", "bold")
    s += line(196, 200, 250, 200, INK, 2) + line(310, 200, 356, 200, INK, 2)
    s += text(190, 204, "МК", 10, GREEN, "end", "bold") + text(150, 220, "5 В", 9, GREY, "start")
    # анотації струмів
    s += text(250, 176, "Ib ≈ 7 мА", 10, GREEN, "middle", "bold")
    s += text(470, 196, "Ic = 70 мА", 10, RED, "middle", "bold")
    s += text(430, 244, "Vce(sat)≈0.3 В → P≈21 мВт (холодний)", 9.5, INK, "middle")
    save("fig-11-8-2-relay-worked.svg", s)


# ── Рис. 11.8.3 — рецепт вибору ──────────────────────────────────────────────
def fig81_selection_flow():
    W, H = 720, 452
    s = header(W, H)
    s += text(W / 2, 30, "Рецепт вибору транзистора — вісім кроків", 16, INK, "middle", "bold")
    steps = [
        ("1", "Струм навантаження Ic", "→ транзистор з Ic(max) ≥ 2·Ic", True),
        ("2", "Напруга живлення", "→ Vceo > живлення + запас (викиди!)", True),
        ("3", "β(min) з даташита", "→ Ib(min) = Ic / β(min)", False),
        ("4", "Запас на насичення", "→ Ib = (3…10)·Ib(min)", False),
        ("5", "Резистор бази", "→ Rb = (U − 0.7) / Ib", False),
        ("6", "Індуктивне навантаження?", "→ гасний діод паралельно", False),
        ("7", "Перевір грійку", "→ P = Vce(sat)·Ic < Ptot", True),
        ("8", "Корпус під потужність", "→ TO-92 / TO-220 (+радіатор)", False),
    ]
    x, w, y, bh = 130, 460, 56, 40
    for num, head, tail, check in steps:
        fill = LRED if check else "#fbfbfb"
        bord = RED if check else "#c9d3dc"
        s += circle(x - 24, y + bh / 2, 13, "#eef2f6", INK, 1.4) + text(x - 24, y + bh / 2 + 4, num, 11, INK, "middle", "bold")
        s += rect(x, y, w, bh, fill, bord, 1.4, 6)
        s += text(x + 14, y + 17, head, 11.5, INK, "start", "bold")
        s += text(x + 14, y + 33, tail, 11, INK, "start")
        if check:
            s += text(x + w + 12, y + bh / 2 + 4, "даташит", 8.5, RED, "start", "bold")
        if num != "8":
            s += arrow(x + w / 2, y + bh, x + w / 2, y + bh + 8, GREY, 2)
        y += bh + 8
    save("fig-11-8-3-selection-flow.svg", s)


# ── Рис. 11.8.4 — потужність і тепло ─────────────────────────────────────────
def fig81_power_heat():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "P = Vce·Ic: ключ холодний, підсилювач гарячий", 15, INK, "middle", "bold")

    def panel(ox, title, vce_frac, hot):
        t = _frame(ox, 54, 280, 222, title)
        bx, by, bw, bh = ox + 50, 248, 190, 150
        t2 = _axes(bx, by, bw, bh, "Vce", "Ic")
        # робоча точка
        px = bx + vce_frac * bw
        py = by - bh * (1 - vce_frac * 0.5)
        col = RED if hot else BLUE
        # прямокутник потужності = Vce·Ic
        t2 += rect(bx, py, px - bx, by - py, "#fbecec" if hot else "#e9eefb", col, 1.2)
        t2 += circle(px, py, 4, col, col)
        t2 += text((bx + px) / 2, (py + by) / 2 + 4, "P", 14, col, "middle", "bold")
        lab = "велика → гаряче 🔥" if hot else "мала → холодно"
        t2 += text(ox + 140, 268, lab, 10.5, col, "middle", "bold")
        return t + t2

    s += panel(40, "ключ (насичення)", 0.12, False)
    s += panel(400, "підсилювач (активний)", 0.5, True)
    s += text(W / 2, H - 10, "Площа сірого прямокутника — це тепло на транзисторі. У насиченні Vce крихітна, тож і тепла мало.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-8-4-power-heat.svg", s)


# ── Рис. 11.8.5 — пара Дарлінгтона ───────────────────────────────────────────
def fig81_darlington():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Пара Дарлінгтона: β = β₁·β₂ (тисячі)", 15.5, INK, "middle", "bold")
    TOP, GND = 66, 286
    s += line(150, TOP, 560, TOP, RED, 2) + text(144, TOP + 4, "+V", 11, RED, "end", "bold")
    s += _bjt_sym(300, 150, True)   # Q1
    s += _bjt_sym(410, 184, True)   # Q2
    # колектори разом до +V
    s += line(330, 94, 330, TOP, INK, 2) + line(440, 128, 440, TOP, INK, 2)
    # емітер Q1 → база Q2
    s += line(330, 206, 366, 206, INK, 2) + line(366, 206, 366, 184, INK, 2)
    # база Q1 — вхід
    s += line(256, 150, 210, 150, INK, 2) + text(204, 154, "Ib", 11, GREEN, "end", "bold")
    s += text(150, 138, "крихітна", 9, GREEN, "start")
    # емітер Q2 → навантаження/вихід
    s += line(440, 240, 440, GND, INK, 2) + line(150, GND, 560, GND, INK, 1.5) + text(144, GND + 4, "вих.", 9, INK, "end")
    s += text(460, 220, "Ic великий", 10, RED, "start", "bold")
    s += text(300, 124, "Q1", 9.5, INK, "middle") + text(410, 158, "Q2", 9.5, INK, "middle")
    # підпис ціни
    s += rect(500, 110, 196, 70, LRED, "#d8b46a", 1.3, 6)
    s += text(598, 134, "ціна: Vce(sat) ↑", 11, RED, "middle", "bold")
    s += text(598, 154, "(~0.7…1 В, два", 10, INK, "middle")
    s += text(598, 170, "переходи) → грійка", 10, INK, "middle")
    s += text(W / 2, H - 10, "Готові в одному корпусі: TIP120 (NPN), TIP125 (PNP), ULN2003 (×7 каналів).",
              9.5, GREY, "middle", style="italic")
    save("fig-11-8-5-darlington.svg", s)


# ── Рис. 11.8.6 — BJT проти MOSFET ───────────────────────────────────────────
def fig81_bjt_vs_mosfet():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 28, "BJT проти MOSFET — місток до Розділу 12", 15.5, INK, "middle", "bold")
    # заголовки колонок із символами
    s += rect(70, 50, 290, 56, LRED, "#d8a0a0", 1.4, 6)
    s += text(120, 84, "BJT", 16, RED, "middle", "bold")
    s += _bjt_sym(210, 78, True)
    s += rect(380, 50, 290, 56, LBLUE, "#9bb0c2", 1.4, 6)
    s += text(430, 84, "MOSFET", 14, BLUE, "middle", "bold")
    s += _mosfet_sym(540, 78)
    rows = [
        ("керується", "струмом бази", "напругою затвора"),
        ("тримати ввімкн.", "тече Ib весь час", "струму майже нема"),
        ("відкритий стан", "Vce(sat) ~0.2…1 В", "опір Rds(on)"),
        ("сильний струм", "гріється, Дарлінгтон", "холодніший, простіший"),
    ]
    y = 118
    for lab, a, b in rows:
        s += text(W / 2, y + 18, lab, 10, GREY, "middle", "bold")
        s += rect(70, y, 290, 30, "#fbfbfb", "#e0c4c4", 1.1)
        s += text(215, y + 20, a, 11, INK, "middle")
        s += rect(380, y, 290, 30, "#fbfbfb", "#c4d0e0", 1.1)
        s += text(525, y + 20, b, 11, INK, "middle")
        y += 40
    s += arrow(W / 2, y + 4, W / 2, y + 26, GREEN, 2.4)
    s += text(W / 2, y + 46, "сильний струм або економність → MOSFET (Розділ 12)", 11.5, GREEN, "middle", "bold")
    save("fig-11-8-6-bjt-vs-mosfet.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  📜 Історія до §2.6.1 — Зрадницька вісімка (Рис. 2.6.1i.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig1i_timeline():
    W, H = 920, 260
    s = header(W, H)
    s += text(W / 2, 32, "Як втеча восьми інженерів запустила Кремнієву долину", 18, INK, "middle", "bold")
    boxes = [
        ("1947 · Bell Labs", ["Шоклі — співавтор", "транзистора", "(Нобель 1956)"], LBLUE),
        ("1956 · Маунтін-В'ю", ["Shockley Semicond.:", "кремній приходить", "у долину"], LGRN),
        ("1957", ["восьмеро тікають", "від нестерпного", "боса"], "#fbeeee"),
        ("18.09.1957", ["Fairchild Semicond.", "(гроші — Артур Рок", "+ Fairchild Camera)"], LGRN),
        ("1959 →", ["планарний процес,", "інтегральна схема,", "потім Intel (1968)"], LBLUE),
    ]
    bw, gap, by, bh = 158, 18, 86, 112
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 16 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 11, INK, "middle", "bold")
        s += rect(bx, by, bw, bh, fill, "#c9d3dc", 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 32 + k * 21, ln, 11, INK, "middle")
        if i < len(boxes) - 1:
            s += arrow(bx + bw + 2, by + bh / 2, bx + bw + gap - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Шоклі привіз кремній у долину — і ненавмисно дав їй головний поштовх, від якого від нього пішли найкращі.",
              11, GREY, "middle", style="italic")
    save("fig-11-1i-1-timeline.svg", s)


def fig1i_eight():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "«Зрадницька вісімка» — і що з неї виросло", 18, INK, "middle", "bold")
    # вісім імен
    s += _frame(40, 56, 420, 300, "восьмеро, що пішли 1957-го")
    names = ["Роберт Нойс (Noyce)", "Гордон Мур (Moore)", "Жан Орні (Hoerni) — швейцарець",
             "Джей Ласт (Last)", "Віктор Грінич (Grinich)", "Юджин Кляйнер (Kleiner) — з Австрії",
             "Шелдон Робертс (Roberts)", "Джуліус Бланк (Blank)"]
    for k, n in enumerate(names):
        s += circle(66, 92 + k * 32, 3.5, GREEN, GREEN, 0)
        s += text(80, 96 + k * 32, n, 11.5, INK, "start")
    # спадок
    s += _frame(480, 56, 340, 300, "«Fairchildren» — спадок")
    s += text(650, 86, "Fairchild так добре вчила людей,", 10, GREY, "middle")
    s += text(650, 102, "що вони йшли робити свої компанії:", 10, GREY, "middle")
    sprouts = ["Intel (Нойс + Мур, 1968)", "AMD", "National Semiconductor",
               "Kleiner Perkins (венчурний", "  фонд Юджина Кляйнера)", "…десятки інших"]
    for k, sp in enumerate(sprouts):
        s += text(500, 138 + k * 30, "▸ " + sp if not sp.startswith("  ") else sp, 11, INK, "start", "bold" if not sp.startswith("  ") else "normal")
    s += text(650, 330, "венчурний капітал — теж звідси", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 12, "Нойс згодом співзаснував Intel і став одним з винахідників інтегральної схеми; Мур — автор «закону Мура».",
              10.5, GREY, "middle", style="italic")
    save("fig-11-1i-2-eight.svg", s)


def fig1i_irony():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 30, "Парадокс Шоклі: геній фізики, нездара керівник", 17.5, INK, "middle", "bold")
    # ліворуч — геній
    s += _frame(40, 60, 350, 220, "блискучий фізик")
    s += text(215, 92, "співавтор транзистора (Bell)", 11, "#1f6e33", "middle", "bold")
    s += text(215, 116, "Нобелівська премія 1956", 11, "#1f6e33", "middle")
    s += text(215, 140, "привіз КРЕМНІЙ у долину", 11, "#1f6e33", "middle")
    s += text(215, 164, "(звідси й назва Silicon Valley)", 9.5, GREY, "middle")
    s += text(215, 196, "теорія p-n переходу, що", 10, INK, "middle")
    s += text(215, 212, "лежить в основі цього розділу", 10, INK, "middle")
    s += text(215, 244, "★ блискучий розум", 11, GREEN, "middle", "bold")
    # праворуч — нездара
    s += _frame(430, 60, 350, 220, "нестерпний бос")
    s += text(605, 92, "«можливо, найгірший керівник", 10.5, "#9a2b22", "middle", "bold")
    s += text(605, 108, "в історії електроніки» (біограф)", 10, GREY, "middle")
    s += text(605, 134, "параноя, грубість, рейтинги,", 10, INK, "middle")
    s += text(605, 150, "перевірки на детекторі брехні", 10, INK, "middle")
    s += text(605, 176, "застряг на чотиришаровому діоді,", 10, INK, "middle")
    s += text(605, 192, "занедбавши кремнієвий транзистор", 10, INK, "middle")
    s += text(605, 224, "✕ власна компанія провалилася", 11, RED, "middle", "bold")
    s += text(W / 2, H - 14, "Найбільший його внесок у долину — мимовільний: він зібрав геніїв і так їх дістав, що ті пішли будувати майбутнє.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-1i-3-irony.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  ⚙️ Вставка до §2.6.4 — Виміряти β самому (Рис. 2.6.4a.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig4a1_two_ways():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Два способи виміряти β: швидкий і чесний", 16.5, INK, "middle", "bold")
    # ── hFE-гніздо ──
    s += _frame(40, 56, 360, 300, "1) гніздо hFE на мультиметрі")
    s += rect(110, 100, 220, 130, "#2b2b2b", INK, 1.6, 8)
    s += text(220, 124, "DMM: режим hFE", 10.5, "#dde6f5", "middle", "bold")
    s += rect(150, 144, 140, 56, "#1a1a1a", "#555", 1.2, 4)
    s += text(220, 178, "hFE  287", 16, "#7CFC9A", "middle", "bold")
    s += text(220, 220, "гнізда: E B C  (PNP / NPN)", 9, "#cdd8f5", "middle")
    s += text(220, 256, "+ швидко, нічого не паяти", 10, "#1f6e33", "middle", "bold")
    s += text(220, 280, "− міряє за ФІКСОВАНИХ умов:", 10, "#9a2b22", "middle", "bold")
    s += text(220, 298, "низька напруга, малий струм бази", 9, GREY, "middle")
    s += text(220, 320, "→ не те β, що на робочому струмі", 9.5, "#9a2b22", "middle", "bold")
    # ── дві точки ──
    s += _frame(440, 56, 360, 300, "2) «дві точки» на робочому струмі")
    # схема
    s += line(500, 90, 740, 90, RED, 2) + text(494, 94, "Vcc", 9, RED, "end", "bold")
    s += rect(640, 108, 20, 30, "#fff", INK, 1.3) + text(672, 126, "Rc", 9, INK, "start", "bold")
    s += line(650, 90, 650, 108, INK, 1.6) + line(650, 138, 650, 168, INK, 1.6)
    s += _bjt_sym(620, 196, True)
    s += line(650, 224, 650, 320, INK, 1.6) + text(650, 334, "GND", 8.5, INK, "middle")
    s += line(540, 196, 596, 196, INK, 1.6)
    s += rect(556, 184, 20, 24, "#fff", INK, 1.3) + text(566, 178, "Rb", 8.5, INK, "middle", "bold")
    s += line(500, 196, 540, 196, INK, 1.6) + text(494, 200, "Vbb", 9, INK, "end", "bold")
    s += text(620, 130, "виміряй Ic", 8.5, GREEN, "middle")
    s += text(540, 224, "виміряй Ib", 8.5, GREEN, "middle")
    s += text(620, 300, "β = Ic / Ib (на ТВОЄМУ струмі)", 10, "#1f6e33", "middle", "bold")
    s += text(W / 2, H - 12, "Гніздо hFE — для сортування «який більший»; точне β на робочій точці дає лише метод «двох точок».",
              10.5, GREY, "middle", style="italic")
    save("fig-11-4a-1-two-ways.svg", s)


def fig4a2_procedure():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Метод «двох точок»: кроки, перевірка й крива β(Ic)", 15.5, INK, "middle", "bold")
    # кроки
    s += _frame(40, 54, 380, 300, "процедура")
    steps = ["1) Rb від Vbb до бази задає Ib;",
             "    Ib = (Vbb − 0.7)/Rb  (або виміряй)",
             "2) Rc у колекторі; виміряй Vc,",
             "    тоді Ic = (Vcc − Vc)/Rc",
             "3) β = Ic / Ib",
             "4) ПЕРЕВІР: Vce = Vc має бути",
             "    помітна (кілька В) — активний режим!",
             "    Vce ≈ 0 → насичення, β занижене"]
    for k, st in enumerate(steps):
        col = "#9a2b22" if "ПЕРЕВІР" in st or "насичення" in st else INK
        s += text(62, 88 + k * 30, st, 10.5, col, "start", "bold" if st.startswith(("1)", "2)", "3)", "4)")) else "normal")
    s += text(230, 340, "Ib зручно ~таким, як у майбутній схемі", 9, GREY, "middle", style="italic")
    # крива β(Ic)
    s += _frame(440, 54, 360, 300, "повтори на кількох Ic → побачиш криву")
    ox, oy, w, h = 480, 290, 300, 180
    s += line(ox, oy, ox + w, oy, INK, 1.3) + text(ox + w, oy + 16, "Ic (лог)", 9, INK, "start")
    s += line(ox, oy, ox, oy - h - 6, INK, 1.3) + text(ox - 6, oy - h - 12, "β", 9.5, INK, "middle")
    pts = []
    for t in range(0, 101):
        x = t / 100.0
        b = 1 - 2.6 * (x - 0.55) ** 2  # пік посередині
        pts.append((ox + x * w, oy - max(b, 0.15) * h))
    s += _poly(pts, COPP, 2.4)
    s += circle(ox + 0.55 * w, oy - h, 4, RED, RED, 0)
    s += text(ox + 0.55 * w, oy - h - 8, "пік β", 9.5, RED, "middle", "bold")
    s += text(ox + 0.5 * w, oy + 34, "β провисає на малих і великих Ic (§2.6.4)", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Так ви бачите не «одне число», а реальне β саме там, де працюватиме ваша схема — і його розкид.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-4a-2-procedure.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.6.9 — Реле зсередини: контакти (Рис. 2.6.9c.3–4)
# ═════════════════════════════════════════════════════════════════════════════
def fig9c3_ratings():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 28, "Номінали контактів на корпусі — і скільки від них лишається", 15.5, INK, "middle", "bold")
    # «наклейка» на реле
    s += rect(60, 60, 300, 150, "#1f3a6b", INK, 1.6, 8)
    s += text(210, 86, "SRD-05VDC-SL-C", 11, "#dde6f5", "middle", "bold")
    s += text(210, 116, "10A 250VAC   10A 30VDC", 12, "#ffffff", "middle", "bold")
    s += text(210, 140, "7A 277VAC    10A 125VAC", 10.5, "#cdd8f5", "middle")
    s += text(210, 170, "котушка: 5 В DC", 10, "#cdd8f5", "middle")
    s += text(210, 192, "(резистивне навантаження!)", 9, "#9fb4e0", "middle", style="italic")
    # derating за типом навантаження
    s += _frame(400, 60, 400, 300, "та сама «10 А» — для РІЗНИХ навантажень")
    rows = [("резистивне (нагрівач)", "10 А", "100%", GREEN),
            ("лампа розжарення", "≈1–1.5 А", "пусковий ×10–15", "#9a2b22"),
            ("двигун", "≈3–4 А", "пусковий ×6 (LRA)", "#9a2b22"),
            ("ємнісне (БЖ, LED-драйвер)", "≈2–3 А", "кидок заряду", COPP),
            ("індуктивне AC (cos φ<1)", "менше", "дуга + викид", COPP)]
    for i, (lab, val, note, col) in enumerate(rows):
        y = 96 + i * 48
        s += text(420, y, lab, 10.5, INK, "start", "bold")
        s += text(700, y, val, 11, col, "middle", "bold")
        s += text(610, y + 16, note, 9, GREY, "start")
        if i < len(rows) - 1:
            s += line(415, y + 30, 785, y + 30, "#eee", 1)
    s += text(W / 2, H - 14, "Паспортна «10 А» — це РЕЗИСТИВНЕ навантаження; для лампи, мотора чи ємності реальна межа в рази нижча.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9c-3-ratings.svg", s)


def fig9c4_life_dc():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 26, "Ресурс, постійний струм і «змочувальний» струм", 16, INK, "middle", "bold")
    # ресурс: механічний vs електричний
    s += _frame(40, 54, 380, 300, "ресурс: два дуже різні числа")
    ox, oy, w, h = 80, 260, 300, 150
    s += line(ox, oy, ox + w, oy, INK, 1.3) + text(ox + w, oy + 16, "струм", 9.5, INK, "start")
    s += line(ox, oy, ox, oy - h - 6, INK, 1.3) + text(ox - 6, oy - h - 12, "циклів", 9.5, INK, "middle")
    # механічний — горизонталь високо
    s += line(ox, oy - h, ox + w, oy - h, BLUE, 2, dash="5,4")
    s += text(ox + w - 4, oy - h - 8, "механічний ~10–50 млн (без струму)", 9, BLUE, "end", "bold")
    # електричний — падає зі струмом
    pts = [(ox + w * t / 100, oy - (h - 20) * math.exp(-t / 30.0) - 12) for t in range(0, 101)]
    s += _poly(pts, RED, 2.4)
    s += text(ox + 0.5 * w, oy - 0.4 * h, "електричний: під номіналом", 9, RED, "middle", "bold")
    s += text(ox + 0.5 * w, oy - 0.4 * h + 14, "~100 тис. і падає зі струмом", 8.5, GREY, "middle")
    # AC vs DC + wetting
    s += _frame(440, 54, 360, 300, "дві пастки навантаження")
    s += text(620, 86, "постійний струм важчий:", 10.5, "#9a2b22", "middle", "bold")
    s += text(620, 104, "дуга не гасне на нулі (немає нуля)", 9.5, GREY, "middle")
    s += text(620, 120, "→ DC-рейтинг у рази нижчий за AC", 9.5, GREY, "middle")
    s += line(470, 142, 770, 142, "#eee", 1)
    s += text(620, 168, "малий сигнал — інша біда:", 10.5, "#9c6a16", "middle", "bold")
    s += text(620, 186, "срібні контакти заростають плівкою,", 9.5, GREY, "middle")
    s += text(620, 202, "якщо струм нижчий за «змочувальний»", 9.5, GREY, "middle")
    s += text(620, 218, "(wetting current, ~кілька мА)", 9, GREY, "middle", style="italic")
    s += text(620, 244, "для сигналів — ЗОЛОЧЕНІ контакти", 10, "#1f6e33", "middle", "bold")
    s += text(620, 262, "(золото не окислюється)", 9, GREY, "middle")
    s += text(620, 290, "матеріали: AgNi, AgSnO₂ — для сили;", 9.5, INK, "middle")
    s += text(620, 306, "Au-покриття — для слабких сигналів", 9.5, INK, "middle")
    s += text(620, 332, "велике/часте → твердотільне реле (§2.5.10)", 9.5, "#7a4e8a", "middle", "bold")
    save("fig-11-9c-4-life-dc.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  📜 Історія до §2.6.8 — Regency TR-1 і Sony (Рис. 2.6.8i.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig8i_timeline():
    W, H = 920, 250
    s = header(W, H)
    s += text(W / 2, 32, "Перший зробили в США, масовим — у Японії", 18, INK, "middle", "bold")
    boxes = [
        ("1953", ["Sony ліцензує", "транзистор у", "Western Electric"], LBLUE),
        ("лист. 1954 · США", ["Regency TR-1 —", "ПЕРШИЙ кишеньковий", "(TI + I.D.E.A.)"], LGRN),
        ("серп. 1955 · Японія", ["Sony TR-55 —", "перший японський", "приймач"], "#fbfbfb"),
        ("1957", ["Sony TR-63:", "експорт у США,", "масовий хіт"], LGRN),
        ("1960-ті →", ["радіо в кишені;", "Японія опановує", "споживчу електроніку"], LBLUE),
    ]
    bw, gap, by, bh = 158, 18, 80, 116
    for i, (lab, lines, fill) in enumerate(boxes):
        bx = 16 + i * (bw + gap)
        s += text(bx + bw / 2, by - 8, lab, 11, INK, "middle", "bold")
        s += rect(bx, by, bw, bh, fill, "#c9d3dc", 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 30 + k * 21, ln, 11, INK, "middle")
        if i < len(boxes) - 1:
            s += arrow(bx + bw + 2, by + bh / 2, bx + bw + gap - 2, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Перший транзисторний приймач — американський; та культуру «музика в кишені» створив японський маркетинг Sony.",
              11, GREY, "middle", style="italic")
    save("fig-11-8i-1-timeline.svg", s)


def fig8i_tube_vs_transistor():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 30, "Що змінив транзистор: радіо з меблів — у кишеню", 17, INK, "middle", "bold")
    # лампове
    s += _frame(40, 56, 350, 290, "лампове радіо (до 1954)")
    s += rect(120, 110, 190, 120, "#6b4a2a", "#3a2814", 2, 6)
    s += text(215, 150, "велика тумба", 11, "#f0e0c8", "middle", "bold")
    s += text(215, 172, "у вітальні", 10, "#d8c0a0", "middle")
    s += text(215, 256, "гаряче (лампи), важке, дороге", 9.5, GREY, "middle")
    s += text(215, 276, "живлення від мережі", 9.5, GREY, "middle")
    s += text(215, 300, "кілька годин від батарей", 9.5, GREY, "middle")
    s += text(215, 326, "★ слухає вся родина разом", 10.5, COPP, "middle", "bold")
    # транзисторне
    s += _frame(430, 56, 350, 290, "транзисторне (Regency TR-1, 1954)")
    s += rect(560, 120, 90, 130, "#1f3a6b", INK, 2, 8)
    s += circle(605, 165, 26, "#cdd8f5", "#16294d", 1.6)
    s += text(605, 270, "влізає в долоню / кишеню", 9.5, GREY, "middle")
    s += text(605, 290, "4 транзистори, 4 мА", 9.5, GREEN, "middle", "bold")
    s += text(605, 308, "20–30 годин від батарейки", 9.5, GREY, "middle")
    s += text(605, 332, "★ музика з тобою всюди й сама", 10.5, "#1f6e33", "middle", "bold")
    s += text(W / 2, H - 12, "Персональне, портативне радіо народило молодіжну культуру 1960-х: рок-н-рол у кишені, а не в спільній вітальні.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-8i-2-tube-vs-transistor.svg", s)


def fig8i_who_won():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 30, "Хто зробив перший — і хто виграв ринок", 17.5, INK, "middle", "bold")
    # Regency
    s += _frame(40, 60, 350, 230, "Regency TR-1 (США)")
    s += text(215, 92, "★ ПЕРШИЙ комерційний (1954)", 11, "#1f6e33", "middle", "bold")
    s += text(215, 116, "$49.95, ~150 000 проданих", 10, INK, "middle")
    s += text(215, 140, "посередня якість, новинка-іграшка", 10, GREY, "middle")
    s += text(215, 168, "TI хотіла показати ринок —", 10, INK, "middle")
    s += text(215, 184, "і показала, та сама кинула радіо", 10, INK, "middle")
    s += text(215, 214, "✕ ринок не втримали", 11, RED, "middle", "bold")
    s += text(215, 236, "(великі — RCA, Philco — відмовились", 9, GREY, "middle")
    s += text(215, 250, "робити взагалі)", 9, GREY, "middle")
    # Sony
    s += _frame(430, 60, 350, 230, "Sony (Японія)")
    s += text(605, 92, "не перша — але МАСОВА", 11, BLUE, "middle", "bold")
    s += text(605, 116, "якість + маркетинг + експорт", 10, INK, "middle")
    s += text(605, 140, "TR-63 «кишеньковий»:", 10, INK, "middle")
    s += text(605, 156, "сорочки з більшими кишенями", 9.5, GREY, "middle")
    s += text(605, 172, "для продавців — щоб «влазив»", 9.5, GREY, "middle")
    s += text(605, 202, "✓ виграла споживчий ринок", 11, "#1f6e33", "middle", "bold")
    s += text(605, 224, "— провісник японського", 9.5, GREY, "middle")
    s += text(605, 238, "домінування в електроніці", 9.5, GREY, "middle")
    s += text(W / 2, H - 12, "Урок: винайти перший — не те саме, що виграти ринок. Масовість, якість і маркетинг важать не менше за першість.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-8i-3-who-won.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.6.8 — Робочі конячки BJT (Рис. 2.6.8c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig8c1_workhorses():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 28, "Три малопотужні NPN, які варто знати напам'ять", 17, INK, "middle", "bold")
    cards = [
        (30, "2N2222 / PN2222", "універсальний, швидкий", LBLUE, BLUE,
         ["40 В · до ~0.6–0.8 А", "fT ~300 МГц", "ключ і ВЧ", "PNP-пара: 2N2907"]),
        (310, "BC547 / BC548", "сигнальний, тихий", LGRN, GREEN,
         ["45 В · 100 мА", "групи β: A / B / C", "підсилювачі, аудіо", "PNP-пара: BC557"]),
        (590, "2N3904", "загальна конячка", LRED, RED,
         ["40 В · 200 мА", "fT ~300 МГц", "ключ і підсилювач", "PNP-пара: 2N3906"]),
    ]
    for x, name, role, fill, bc, lines in cards:
        s += rect(x, 60, 250, 310, fill, bc, 2, 12)
        s += text(x + 125, 92, name, 14.5, INK, "middle", "bold")
        s += text(x + 125, 114, role, 11.5, bc, "middle", "bold")
        s += line(x + 20, 128, x + 230, 128, "#cccccc", 1)
        for k, ln in enumerate(lines):
            s += text(x + 125, 158 + k * 30, ln, 11.5, INK, "middle")
    s += text(W / 2, H - 14, "Трохи потужніші — BC337, 2N4401 (до ~0.8 А). Для кожного NPN є комплементарний PNP — зручно для пар (мости, push-pull).",
              10.5, GREY, "middle", style="italic")
    save("fig-11-8c-1-workhorses.svg", s)


def fig8c2_pinout_trap():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 26, "Головна пастка: розпіновка TO-92 РІЗНА", 17, INK, "middle", "bold")
    s += text(W / 2, 48, "вид на ПЛАСКУ грань, ніжки вниз — порядок виводів дзеркальний у двох родин",
              11, GREY, "middle", style="italic")

    def to92(ox, name, labels, col):
        # корпус-півколо пласкою гранню до глядача
        out = f'<path d="M {ox},120 A 55,55 0 0 0 {ox+110},120 L {ox+110},132 L {ox},132 Z" fill="#d9d2c4" stroke="{INK}" stroke-width="1.6"/>\n'
        out += line(ox, 120, ox + 110, 120, INK, 2)  # пласка грань
        out += text(ox + 55, 96, name, 11.5, col, "middle", "bold")
        for i, lab in enumerate(labels):
            lx = ox + 22 + i * 33
            out += line(lx, 132, lx, 175, INK, 2.4)
            out += text(lx, 192, lab, 12, INK, "middle", "bold")
        out += text(ox + 55, 214, "← пласка грань до вас", 8.5, GREY, "middle")
        return out

    s += to92(120, "BC547 / BC557 (європейські)", ["C", "B", "E"], GREEN)
    s += to92(560, "2N3904 / 2N2222 (американські)", ["E", "B", "C"], RED)
    s += text(285, 250, "колектор зліва", 9.5, GREEN, "middle", "bold")
    s += text(725, 250, "емітер зліва — ДЗЕРКАЛЬНО!", 9.5, RED, "middle", "bold")
    s += _frame(120, 270, 620, 80, "")
    s += text(430, 296, "переплутав родину — переплутав виводи: схема не працює або транзистор гине", 11, "#9a2b22", "middle", "bold")
    s += text(430, 320, "ЗАВЖДИ звіряй розпіновку з даташитом саме твого номера; суфікс A/B/C у BC — це група β (§2.6.4)", 10, GREY, "middle")
    s += text(430, 338, "SMD-еквіваленти (SOT-23): MMBT3904, MMBT2222, BC847 — ті самі кристали в корпусі для поверхні", 9.5, GREY, "middle", style="italic")
    save("fig-11-8c-2-pinout-trap.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.6.7 — Підсилювач зі спільним емітером на макетці (Рис. 2.6.7c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig7c1_breadboard_amp():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 28, "Підсилювач зі спільним емітером: номінали для макетки", 15.5, INK, "middle", "bold")
    # шини
    s += line(120, 70, 620, 70, RED, 2) + text(112, 74, "+9 В", 10, RED, "end", "bold")
    s += line(120, 380, 620, 380, INK, 1.6) + text(112, 384, "GND", 9, INK, "end", "bold")
    # транзистор у центрі
    s += _bjt_sym(360, 230, True)
    s += text(395, 205, "Q: BC547", 9.5, INK, "start", "bold")
    # дільник бази R1/R2
    s += line(330, 230, 250, 230, INK, 2) + circle(250, 230, 3, INK, INK)
    s += rect(238, 150, 24, 50, "#fff", INK, 1.4) + text(228, 175, "R1", 9, INK, "end", "bold") + text(282, 165, "47к", 8.5, GREY, "start")
    s += line(250, 150, 250, 70, INK, 2)
    s += rect(238, 260, 24, 50, "#fff", INK, 1.4) + text(228, 285, "R2", 9, INK, "end", "bold") + text(282, 290, "10к", 8.5, GREY, "start")
    s += line(250, 230, 250, 260, INK, 2) + line(250, 310, 250, 380, INK, 2)
    # Rc
    s += rect(378, 110, 24, 50, "#fff", INK, 1.4) + text(412, 135, "Rc 1к", 9, INK, "start", "bold")
    s += line(390, 110, 390, 70, INK, 2) + line(390, 160, 390, 202, INK, 2)
    # Re + Ce
    s += rect(378, 286, 24, 44, "#fff", INK, 1.4) + text(412, 312, "Re 100", 9, INK, "start", "bold")
    s += line(390, 258, 390, 286, INK, 2) + line(390, 330, 390, 380, INK, 2)
    # Ce (емітерний шунт)
    s += line(450, 290, 450, 298, INK, 2) + line(438, 298, 462, 298, INK, 2.4) + line(438, 306, 462, 306, INK, 2.4)
    s += line(450, 306, 450, 380, INK, 2) + line(390, 290, 450, 290, INK, 1.6)
    s += text(470, 304, "Ce 100µF", 8.5, GREY, "start") + text(470, 318, "(більше Av)", 8, GREY, "start")
    # C1 вхід
    s += line(180, 230, 196, 230, INK, 2) + line(196, 222, 196, 238, INK, 2.4) + line(204, 222, 204, 238, INK, 2.4)
    s += line(204, 230, 250, 230, INK, 2)
    s += text(190, 210, "C1 1µF", 8.5, GREY, "middle")
    s += circle(160, 230, 4, GREEN, GREEN, 0) + text(150, 234, "вхід", 9, GREEN, "end", "bold")
    # C2 вихід
    s += line(390, 180, 470, 180, INK, 2) + line(470, 172, 470, 188, INK, 2.4) + line(478, 172, 478, 188, INK, 2.4)
    s += line(478, 180, 540, 180, INK, 2)
    s += text(474, 160, "C2 1µF", 8.5, GREY, "middle")
    s += circle(560, 180, 4, RED, RED, 0) + text(570, 184, "вихід", 9, RED, "start", "bold")
    s += text(W / 2, H - 14, "Дільник R1/R2 задає робочу точку; Rc робить підсилення; Re стабілізує; конденсатори пускають сигнал, не чіпаючи зміщення (§2.1.6).",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7c-1-breadboard-amp.svg", s)


def fig7c2_tune_debug():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 26, "Налаштувати й перевірити: робоча точка + осцилограф", 15.5, INK, "middle", "bold")
    # перевірка робочої точки
    s += _frame(40, 54, 340, 300, "крок 1: виставити робочу точку")
    s += text(210, 84, "виміряй напругу на колекторі Vc:", 10, INK, "middle", "bold")
    s += rect(90, 100, 240, 36, "#eef6ef", GREEN, 1.4, 6)
    s += text(210, 123, "Vc ≈ половина +9 В ≈ 4.5 В  ✓", 10.5, "#1f6e33", "middle", "bold")
    s += text(210, 162, "Vc ≈ 0 → насичення (R1 завеликий):", 9.5, "#9a2b22", "middle", "bold")
    s += text(210, 178, "зменш R1 або збільш R2", 9, GREY, "middle")
    s += text(210, 206, "Vc ≈ 9 В → відсічка (R1 замалий):", 9.5, "#9a2b22", "middle", "bold")
    s += text(210, 222, "збільш R1 або зменш R2", 9, GREY, "middle")
    s += text(210, 256, "база Vb ≈ 1.5–2 В, емітер Ve ≈ Vb−0.7", 9.5, INK, "middle")
    s += text(210, 278, "(перевір мультиметром — це і є точка Q,", 9, GREY, "middle")
    s += text(210, 292, "та сама з навантажувальної прямої §2.6.7m)", 9, GREY, "middle", style="italic")
    s += text(210, 320, "усе це — БЕЗ сигналу, у спокої", 9.5, "#9c6a16", "middle", "bold")
    # осцилограф
    s += _frame(420, 54, 360, 300, "крок 2: подати сигнал, глянути вихід")
    ox, oy, w = 450, 150, 300
    s += line(ox, oy, ox + w, oy, FAINT, 1)
    pts = [(ox + j, oy - 18 * math.sin(j / w * 4 * math.pi)) for j in range(0, int(w))]
    s += _poly(pts, BLUE, 2)
    s += text(ox + w + 4, oy, "вхід", 9, BLUE, "start", "bold")
    oy2 = 250
    s += line(ox, oy2, ox + w, oy2, FAINT, 1)
    pts2 = [(ox + j, oy2 + 55 * math.sin(j / w * 4 * math.pi)) for j in range(0, int(w))]  # перевернуто й більше
    s += _poly(pts2, RED, 2.2)
    s += text(ox + w + 4, oy2, "вихід", 9, RED, "start", "bold")
    s += text(600, 300, "вихід БІЛЬШИЙ і ПЕРЕВЕРНУТИЙ:", 9.5, INK, "middle", "bold")
    s += text(600, 316, "підсилення ~10–50×, інверсія (§2.6.7)", 9, GREY, "middle")
    s += text(600, 336, "плоскі верхівки → зменш вхід (кліп)", 9, "#9a2b22", "middle", "bold")
    s += text(W / 2, H - 12, "Пастки макетки: довгі дроти ловлять фон 50 Гц, поганий контакт = тріск; коротка спільна земля рятує.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7c-2-tune-debug.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.6.6 — PNP high-side ключ (Рис. 2.6.6c.3–4)
# ═════════════════════════════════════════════════════════════════════════════
def fig6c3_low_vs_high():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Низьке плече проти верхнього — і чому PNP не слухає МК прямо", 15.5, INK, "middle", "bold")
    # low-side
    s += _frame(40, 56, 360, 300, "low-side (NPN): розриває «мінус»")
    s += line(120, 90, 320, 90, RED, 2) + text(112, 94, "+V", 10, RED, "end", "bold")
    s += rect(200, 108, 40, 40, "#fff", INK, 1.5) + text(270, 132, "навантаж.", 9.5, INK, "start")
    s += text(270, 148, "висить на +V", 8.5, "#9a2b22", "start")
    s += line(220, 90, 220, 108, INK, 2) + line(220, 148, 220, 168, INK, 2)
    s += _bjt_sym(190, 200, True)
    s += line(220, 256, 220, 286, INK, 2)
    s += line(120, 286, 320, 286, INK, 1.4) + text(112, 290, "GND", 9, INK, "end", "bold")
    s += line(110, 200, 146, 200, GREEN, 2) + text(106, 204, "МК", 9.5, GREEN, "end", "bold")
    s += text(220, 330, "вимкнене навантаження ще під +V!", 9, "#9a2b22", "middle", "bold")
    # high-side проблема
    s += _frame(440, 56, 360, 300, "high-side (PNP): розриває «плюс»")
    s += line(520, 90, 720, 90, RED, 2) + text(512, 94, "+12 В", 9.5, RED, "end", "bold")
    # PNP вгорі: емітер до +V
    s += line(600, 90, 600, 120, INK, 2)
    s += _bjt_sym(640, 150, False)  # PNP-символ
    s += text(680, 130, "PNP", 9, INK, "start", "bold")
    s += line(600, 180, 600, 220, INK, 2)
    s += rect(580, 220, 40, 40, "#fff", INK, 1.5) + text(650, 244, "навантаж.", 9.5, INK, "start")
    s += line(600, 260, 600, 286, INK, 2)
    s += line(520, 286, 720, 286, INK, 1.4) + text(512, 290, "GND", 9, INK, "end", "bold")
    # база PNP — проблема
    s += line(596, 150, 540, 150, BLUE, 2, dash="4,3") + text(536, 154, "база?", 9.5, BLUE, "end", "bold")
    s += text(620, 330, "щоб ЗАКРИТИ — базу треба підняти до +12 В,", 8.5, "#9a2b22", "middle")
    s += text(620, 344, "а МК дає лише 0–3.3 В → прямо не може!", 8.5, "#9a2b22", "middle", "bold")
    save("fig-11-6c-3-low-vs-high.svg", s)


def fig6c4_pnp_driver():
    W, H = 800, 400
    s = header(W, H)
    s += text(W / 2, 28, "Розв'язок: маленький NPN «перекладає рівень» для PNP", 15.5, INK, "middle", "bold")
    s += line(140, 70, 620, 70, RED, 2) + text(132, 74, "+12 В", 10, RED, "end", "bold")
    # PNP силовий вгорі
    s += line(440, 70, 440, 100, INK, 2)
    s += _bjt_sym(480, 130, False)
    s += text(520, 108, "PNP (силовий ключ)", 9.5, INK, "start", "bold")
    s += line(440, 160, 440, 200, INK, 2)
    s += rect(420, 200, 40, 40, "#fff", INK, 1.5) + text(490, 224, "навантаження", 9.5, INK, "start")
    s += line(440, 240, 440, 320, INK, 2)
    # база PNP: підтягувальний R до +12 і стягувальний R до NPN
    s += line(436, 130, 360, 130, INK, 2)
    s += rect(360, 90, 20, 30, "#fff", INK, 1.4) + text(345, 108, "Rпідт", 8.5, INK, "end")
    s += line(370, 90, 370, 70, INK, 2)  # підтяжка до +12
    s += line(360, 130, 300, 130, INK, 2)
    s += rect(270, 120, 30, 20, "#fff", INK, 1.4) + text(285, 158, "R", 9, INK, "middle")
    s += line(270, 130, 230, 130, INK, 2)
    # NPN малий внизу
    s += line(230, 130, 230, 175, INK, 2)
    s += _bjt_sym(200, 210, True)
    s += text(245, 188, "NPN (керує МК)", 9, INK, "start", "bold")
    s += line(230, 266, 230, 320, INK, 2)
    s += line(140, 320, 620, 320, INK, 1.4) + text(132, 324, "GND", 9, INK, "end", "bold")
    s += line(110, 210, 156, 210, GREEN, 2) + text(106, 214, "МК", 9.5, GREEN, "end", "bold")
    s += rect(120, 198, 36, 24, "#fff", INK, 1.4) + text(138, 214, "Rб", 8.5, INK, "middle")
    # пояснення
    s += _frame(560, 90, 230, 230, "логіка")
    s += text(675, 118, "МК = 1:", 10.5, "#1f6e33", "middle", "bold")
    s += text(675, 136, "NPN відкритий → стягує", 9.5, INK, "middle")
    s += text(675, 150, "базу PNP вниз → PNP ВВІМК", 9.5, INK, "middle")
    s += text(675, 178, "МК = 0:", 10.5, GREY, "middle", "bold")
    s += text(675, 196, "NPN закритий → Rпідт тримає", 9.5, INK, "middle")
    s += text(675, 210, "базу PNP на +12 → PNP ВИМК", 9.5, INK, "middle")
    s += text(675, 240, "логіка НЕ інвертована:", 10, "#7a4e8a", "middle", "bold")
    s += text(675, 256, "1 вмикає, 0 вимикає", 9.5, GREY, "middle")
    s += text(675, 284, "два транзистори — бо рівні", 9, GREY, "middle")
    s += text(675, 298, "напруг не збігаються", 9, GREY, "middle")
    s += text(W / 2, H - 12, "NPN розв'язує проблему рівня: він-бо керується від землі (МК уміє), а вже він стягує високовольтну базу PNP.",
              10, GREY, "middle", style="italic")
    save("fig-11-6c-4-pnp-driver.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.6.6 — Дарлінгтон і ULN2003 (Рис. 2.6.6c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig6c1_uln_inside():
    W, H = 840, 420
    s = header(W, H)
    s += text(W / 2, 28, "ULN2003 зсередини: 7 Дарлінгтонів + вбудовані гасні діоди", 16, INK, "middle", "bold")
    # корпус
    s += rect(120, 70, 600, 300, "#fbfbfb", "#c9d3dc", 1.8, 10)
    s += text(420, 92, "ULN2003 (один корпус)", 11, GREY, "middle", "bold")
    # шина COM з діодами
    comy = 116
    s += line(150, comy, 690, comy, RED, 2.2) + text(700, comy + 4, "COM", 10, RED, "start", "bold")
    s += text(700, comy + 18, "→ +V навант.", 8.5, GREY, "start")
    # 3 показові канали (з 7)
    for i, yy in enumerate((180, 250, 320)):
        # вхід
        s += line(130, yy, 175, yy, GREEN, 2) + text(125, yy + 4, f"IN{i+1}", 9, GREEN, "end", "bold")
        s += rect(175, yy - 9, 30, 18, "#fff", INK, 1.4) + text(190, yy + 4, "R", 8.5, INK, "middle")
        # пара Дарлінгтона (два символи спрощено)
        s += _bjt_sym(230, yy, True)
        s += text(250, yy + 30, "Дарлінгтон", 8, GREY, "middle")
        # колектор → вихід
        s += line(260, yy - 18, 600, yy - 18, INK, 2) + line(600, yy - 18, 640, yy - 18, INK, 2)
        s += text(648, yy - 14, f"OUT{i+1}", 9, INK, "start", "bold")
        s += line(260, yy + 18, 260, 360, INK, 1.6)  # емітер до землі-шини
        # flyback-діод від COM до OUT
        ddx = 600
        s += line(ddx, comy, ddx, yy - 40, INK, 1.4)
        s += f'<path d="M {ddx-7},{yy-22} L {ddx+7},{yy-22} L {ddx},{yy-42} Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.3"/>\n'
        s += line(ddx - 7, yy - 44, ddx + 7, yy - 44, INK, 1.8)
        s += line(ddx, yy - 22, ddx, yy - 18, INK, 1.4)
    s += text(420, 358, "… (усього 7 однакових каналів) …", 9.5, GREY, "middle", style="italic")
    s += line(150, 360, 690, 360, INK, 1.6) + text(700, 364, "GND (E)", 9, INK, "start", "bold")
    s += text(W / 2, H - 12, "Кожен канал — пара Дарлінгтона (велике β) з відкритим колектором; усі гасні діоди вже всередині, спільний вивід COM до +V.",
              10, GREY, "middle", style="italic")
    save("fig-11-6c-1-uln-inside.svg", s)


def fig6c2_uln_use():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Навіщо й чим: масиви навантажень, родина, межі", 16.5, INK, "middle", "bold")
    # застосування
    s += _frame(40, 56, 360, 300, "одна мікросхема — 7 навантажень")
    apps = ["• масив реле (по каналу на реле)",
            "• кроковий двигун 28BYJ-48",
            "  (класична зв'язка з ULN2003)",
            "• соленоїди, клапани",
            "• світлодіодні матриці, лампи"]
    for k, a in enumerate(apps):
        s += text(60, 92 + k * 30, a, 10.5, INK, "start")
    s += text(220, 256, "крихітний струм входу (від МК) →", 9.5, GREY, "middle")
    s += text(220, 272, "до 500 мА на канал виходу", 10, "#1f6e33", "middle", "bold")
    s += text(220, 300, "вихід — відкритий колектор:", 9.5, INK, "middle", "bold")
    s += text(220, 316, "ТЯГНЕ до землі (low-side, sink)", 9.5, GREY, "middle")
    s += text(220, 338, "IN=1 → OUT притиснуто до GND", 9.5, "#7a4e8a", "middle", "bold")
    # родина + межі
    s += _frame(440, 56, 360, 300, "родина й чим платиш")
    s += text(620, 88, "ULN2003 — 7 каналів", 10.5, INK, "middle", "bold")
    s += text(620, 106, "ULN2803 — 8 каналів", 10.5, INK, "middle", "bold")
    s += text(620, 124, "до 50 В на виході", 10, GREY, "middle")
    s += line(470, 140, 770, 140, "#ddd", 1)
    s += text(620, 164, "ціна Дарлінгтона: Vce(sat) ≈ 1 В", 10, "#9a2b22", "middle", "bold")
    s += text(620, 182, "(два переходи) → гріється на струмі", 9.5, GREY, "middle")
    s += text(620, 206, "сумарна потужність корпусу обмежена:", 10, "#9c6a16", "middle", "bold")
    s += text(620, 222, "не всі 7 каналів на повному струмі разом", 9.5, GREY, "middle")
    s += text(620, 246, "тільки low-side (до плюса не вмикає)", 9.5, GREY, "middle")
    s += text(620, 278, "сучасна заміна — MOSFET-масиви", 10, "#1f6e33", "middle", "bold")
    s += text(620, 294, "(TBD62083-клас): падіння в рази менше", 9.5, GREY, "middle")
    s += text(620, 318, "для сильнострумових і економних схем", 9.5, GREY, "middle")
    save("fig-11-6c-2-uln-use.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🧮 Вставка до §2.6.7 — Навантажувальна пряма (Рис. 2.6.7m.k)
# ═════════════════════════════════════════════════════════════════════════════
def _out_curves(ox, oy, w, h, vcc, icmax, ib_list):
    """Сімейство вихідних характеристик Ic(Vce) для кількох Ib."""
    out = ""
    for frac in ib_list:
        ic = frac * icmax
        pts = []
        for j in range(0, 121):
            v = j / 120.0 * vcc
            # різке коліно: майже вертикаль до ~0.6 В, далі полиця
            val = ic * (1 - math.exp(-v / (vcc * 0.025)))
            pts.append((ox + v / vcc * w, oy - val / icmax * h))
        out += _poly(pts, "#c7ced6", 1.8)
    return out


def fig7m1_build():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 28, "Навантажувальна пряма: де перетнулися транзистор і коло", 15.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 350, 600, 270
    vcc, icmax = 1.0, 1.0
    s += line(ox, oy, ox + w, oy, INK, 1.6) + text(ox + w, oy + 18, "Vce", 11, INK, "start", "bold")
    s += line(ox, oy, ox, oy - h - 8, INK, 1.6) + text(ox - 6, oy - h - 14, "Ic", 11, INK, "middle", "bold")
    s += _out_curves(ox, oy, w, h, vcc, icmax, [0.18, 0.36, 0.54, 0.72, 0.9])
    s += text(ox + 0.62 * w, oy - 0.86 * h, "вихідні криві транзистора (різні Ib)", 9.5, GREY, "start")
    # навантажувальна пряма: (Vcc,0) → (0, Vcc/Rc)
    s += line(ox, oy - 0.82 * h, ox + w, oy, COPP, 2.6)
    s += circle(ox + w, oy, 5, "none", COPP, 2) + text(ox + w - 6, oy + 18, "Vce=Vcc (відсічка)", 9, COPP, "end", "bold")
    s += circle(ox, oy - 0.82 * h, 5, "none", COPP, 2) + text(ox + 8, oy - 0.82 * h - 8, "Ic=Vcc/Rc (насичення)", 9, COPP, "start", "bold")
    s += text(ox + 0.5 * w, oy - 0.30 * h + 28, "навантажувальна пряма: Vce = Vcc − Ic·Rc", 10.5, COPP, "middle", "bold")
    # робоча точка Q — перетин із серединною кривою
    qx, qy = ox + 0.45 * w, oy - 0.45 * 0.82 * h
    s += circle(ox + 0.45 * w, oy - 0.41 * h, 6, RED, RED, 0)
    s += text(ox + 0.45 * w + 12, oy - 0.41 * h - 6, "Q — робоча точка", 11, RED, "start", "bold")
    s += text(ox + 0.45 * w + 12, oy - 0.41 * h + 10, "(зміщення Ib задає, на якій кривій)", 9, GREY, "start")
    s += text(W / 2, H - 12, "Транзистор каже Ic(Vce); коло каже Vce=Vcc−Ic·Rc. Де лінії перетнулися — там і «живе» транзистор у спокої.",
              10, GREY, "middle", style="italic")
    save("fig-11-7m-1-build.svg", s)


def fig7m2_q_position():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 26, "Куди ставити Q: посередині — найбільший чистий розмах", 15.5, INK, "middle", "bold")
    def panel(ox, qfrac, title, col, clip):
        oy, w, h = 250, 220, 170
        out = _frame(ox - 10, 56, 250, 250, title)
        out += line(ox, oy, ox + w, oy, INK, 1.3)
        out += line(ox, oy, ox, oy - h - 6, INK, 1.3)
        out += line(ox, oy - 0.92 * h, ox + w, oy, "#c7ced6", 2)  # навант. пряма
        qx = ox + qfrac * w
        qy = oy - (1 - qfrac) * 0.92 * h
        out += circle(qx, qy, 5, RED, RED, 0) + text(qx, qy - 10, "Q", 11, RED, "middle", "bold")
        # розмах сигналу вздовж прямої
        amp = 0.30
        lo = max(qfrac - amp, 0.02); hi = min(qfrac + amp, 0.98)
        for f, c in ((lo, GREEN), (hi, GREEN)):
            xx = ox + f * w; yy = oy - (1 - f) * 0.92 * h
            out += circle(xx, yy, 3, c, c, 0)
        out += text(ox + w / 2, oy + 22, clip, 9, col, "middle", "bold")
        return out
    s += panel(40, 0.5, "Q посередині ✓", "#1f6e33", "симетрично, без зрізів")
    s += panel(330, 0.82, "Q близько насичення", "#9a2b22", "зрізає НИЗ сигналу")
    s += panel(620, 0.18, "Q близько відсічки", "#9a2b22", "зрізає ВЕРХ сигналу")
    s += text(W / 2, H - 12, "Зміщення (bias) ставить Q; посеред прямої сигнал хитається в обидва боки на повний розмах, не впираючись у краї (пор. кліп §2.6.7).",
              10, GREY, "middle", style="italic")
    save("fig-11-7m-2-q-position.svg", s)


def fig7m3_swing():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 26, "Сигнал рухає Q вздовж прямої — а Vce коливається сильніше", 15, INK, "middle", "bold")
    ox, oy, w, h = 90, 300, 380, 230
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w, oy + 16, "Vce", 10, INK, "start", "bold")
    s += line(ox, oy, ox, oy - h, INK, 1.4) + text(ox - 6, oy - h - 4, "Ic", 10, INK, "middle", "bold")
    s += line(ox, oy - 0.9 * h, ox + w, oy, COPP, 2.4)
    # три точки: Q і ±
    for f, c, lab in ((0.5, RED, "Q"), (0.74, GREEN, "Ib↑"), (0.26, BLUE, "Ib↓")):
        xx = ox + f * w; yy = oy - (1 - f) * 0.9 * h
        s += circle(xx, yy, 5, c, c, 0) + text(xx + (8 if f < 0.7 else -8), yy - 8, lab, 9.5, c, "start" if f < 0.7 else "end", "bold")
        s += line(xx, oy, xx, yy, c, 1, dash="3,3")
    s += text(ox + 0.5 * w, oy + 30, "мала зміна Ib (вхід) ...", 9.5, INK, "middle")
    # вихідний розмах Vce
    s += arrow(ox + 0.26 * w, oy - h - 4, ox + 0.74 * w, oy - h - 4, INK, 1.6)
    s += arrow(ox + 0.74 * w, oy - h - 4, ox + 0.26 * w, oy - h - 4, INK, 1.6)
    s += text(ox + 0.5 * w, oy - h - 10, "великий розмах Vce (вихід)", 9.5, INK, "middle", "bold")
    # пояснення праворуч
    bx = 520
    s += _frame(bx, 70, 280, 210, "звідки підсилення")
    s += text(bx + 140, 100, "вхід ворушить Ib →", 11, INK, "middle", "bold")
    s += text(bx + 140, 122, "Q бігає вздовж прямої →", 11, INK, "middle")
    s += text(bx + 140, 144, "Vce гойдається широко", 11, INK, "middle")
    s += text(bx + 140, 178, "підсилення = ΔVce / ΔVвх", 11.5, RED, "middle", "bold")
    s += text(bx + 140, 206, "крутіша пряма (більший Rc)", 10, GREY, "middle")
    s += text(bx + 140, 222, "→ більший розмах Vce → більше Av", 9.5, GREY, "middle")
    s += text(bx + 140, 252, "вихід ПЕРЕВЕРНУТИЙ: Ib↑ → Vce↓", 10, "#7a4e8a", "middle", "bold")
    s += text(W / 2, H - 10, "Підсилювач і живе на цій прямій: вхід жене робочу точку туди-сюди, вихід знімають як коливання Vce.",
              10, GREY, "middle", style="italic")
    save("fig-11-7m-3-swing.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🧮 Вставка до §2.6.6 — Розрахунок резистора бази (Рис. 2.6.6m.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig6m1_two_points():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 28, "Чому в ключі НЕ беруть паспортне β: дві робочі точки", 16, INK, "middle", "bold")
    ox, oy, w, h = 90, 320, 600, 240
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w, oy + 18, "Vce", 11, INK, "start", "bold")
    s += line(ox, oy, ox, oy - h, INK, 1.4) + text(ox - 6, oy - h - 4, "Ic", 11, INK, "middle", "bold")
    # вихідні криві для кількох Ib
    for ib, lab in ((0.35, ""), (0.6, ""), (0.9, "")):
        pts = []
        for j in range(0, 121):
            v = j / 120.0
            ic = ib * (1 - math.exp(-v * 22))  # різке коліно насичення
            pts.append((ox + v * w, oy - ic * h))
        s += _poly(pts, FAINT if ib < 0.9 else "#d8d8d8", 1.8)
    # лінія навантаження
    s += line(ox, oy - 0.78 * h, ox + 0.92 * w, oy, COPP, 2, dash="6,4")
    s += text(ox + 0.7 * w, oy - 0.18 * h, "лінія навантаження", 10, COPP, "start", "bold")
    # точка А: паспортне β — ледь у насиченні / на межі
    ax, ay = ox + 0.34 * w, oy - 0.62 * h
    s += circle(ax, ay, 6, "none", RED, 2.4)
    s += text(ax + 10, ay - 8, "A: Ib = Ic/β(паспорт)", 10.5, RED, "start", "bold")
    s += text(ax + 10, ay + 8, "Vce велике → гріється", 9.5, "#9a2b22", "start")
    # точка B: примусове β=10 — глибоко в насиченні
    bx, by = ox + 0.06 * w, oy - 0.76 * h
    s += circle(bx, by, 6, GREEN, GREEN, 0)
    s += text(bx + 12, by - 6, "B: Ib = Ic/10", 10.5, "#1f6e33", "start", "bold")
    s += text(bx + 12, by + 10, "Vce(sat) ≈ 0.2 В → насичено", 9.5, "#1f6e33", "start")
    s += text(W / 2, H - 12, "Паспортне β виводить транзистор лише НА МЕЖУ насичення; для надійного «вкл» базі дають надлишок струму.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-6m-1-two-points.svg", s)


def fig6m2_forced_beta():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 28, "Примусове β: компроміс між теплом і швидкістю", 16.5, INK, "middle", "bold")
    s += text(W / 2, 52, "β_forced = Ic / Ib — навмисно беруть набагато меншим за паспортне β",
              11.5, GREY, "middle", style="italic")
    ox, oy, w = 90, 250, 640
    s += line(ox, oy, ox + w, oy, INK, 2)
    # шкала β_forced від великого (мало бази) до малого (багато бази)
    for frac, lab in ((0.05, "30"), (0.28, "20"), (0.5, "10"), (0.72, "5"), (0.95, "2")):
        x = ox + frac * w
        s += line(x, oy - 6, x, oy + 6, INK, 1.6)
        s += text(x, oy + 24, "β_forced=" + lab, 9.5, INK, "middle", "bold")
    # зони
    s += rect(ox, oy - 70, 0.30 * w, 50, LRED, RED, 1.2, 4)
    s += text(ox + 0.15 * w, oy - 50, "замало запасу:", 9.5, "#9a2b22", "middle", "bold")
    s += text(ox + 0.15 * w, oy - 34, "недонасичення, гріється", 9, GREY, "middle")
    s += rect(ox + 0.38 * w, oy - 80, 0.24 * w, 60, LGRN, GREEN, 1.4, 4)
    s += text(ox + 0.5 * w, oy - 58, "оптимум ≈ 10", 11, "#1f6e33", "middle", "bold")
    s += text(ox + 0.5 * w, oy - 40, "надійне насичення,", 9, GREY, "middle")
    s += text(ox + 0.5 * w, oy - 26, "помірний струм бази", 9, GREY, "middle")
    s += rect(ox + 0.68 * w, oy - 70, 0.30 * w, 50, "#fbf0e0", COPP, 1.2, 4)
    s += text(ox + 0.83 * w, oy - 50, "забагато бази:", 9.5, "#7a4e1d", "middle", "bold")
    s += text(ox + 0.83 * w, oy - 34, "марний струм + повільне", 9, GREY, "middle")
    s += text(ox + 0.83 * w, oy - 20, "вимикання (storage time)", 9, GREY, "middle")
    s += text(ox + 0.83 * w, oy + 70, "глибоке насичення копить", 9, "#7a4e1d", "middle")
    s += text(ox + 0.83 * w, oy + 84, "заряд бази — його довго «вимітати»", 9, GREY, "middle")
    s += text(ox + 0.15 * w, oy + 70, "база не дотискає — Vce велике,", 9, "#9a2b22", "middle")
    s += text(ox + 0.15 * w, oy + 84, "потужність Vce·Ic гріє ключ", 9, GREY, "middle")
    save("fig-11-6m-2-forced-beta.svg", s)


def fig6m3_derive():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 28, "Формула, приклад і перевірка", 17, INK, "middle", "bold")
    # схема міні
    s += line(120, 80, 120, 130, RED, 2) + text(112, 80, "+5 В", 10, RED, "end", "bold")
    s += rect(104, 130, 32, 16, "#fff", INK, 1.4) + text(160, 142, "навантаж. (Ic)", 9.5, INK, "start")
    s += _bjt_sym(120, 200, True)
    s += line(120, 256, 120, 286, INK, 2) + text(120, 300, "GND", 9, INK, "middle")
    s += line(40, 200, 76, 200, GREEN, 2) + text(36, 204, "Vlog", 9.5, GREEN, "end", "bold")
    s += rect(54, 188, 22, 24, "#fff", INK, 1.4)
    s += text(65, 178, "Rб", 9, INK, "middle", "bold")
    # виведення
    x = 290
    s += text(x, 86, "1)  обери β_forced ≈ 10", 12.5, INK, "start", "bold")
    s += text(x, 116, "2)  Ib = Ic / β_forced", 13, INK, "start", "bold")
    s += text(x, 150, "3)  Rб = (Vlog − Vbe) / Ib", 13.5, RED, "start", "bold")
    s += text(x, 168, "      = β_forced·(Vlog − 0.7)/Ic", 11, GREY, "start")
    s += line(x, 186, x + 480, 186, "#ddd", 1)
    s += text(x, 212, "Приклад: Ic = 100 мА, Vlog = 5 В", 12, INK, "start", "bold")
    s += text(x, 238, "Ib = 100/10 = 10 мА", 12, GREEN, "start", "bold")
    s += text(x, 262, "Rб = (5 − 0.7)/10мА = 430 Ом → 390 Ом", 12, GREEN, "start", "bold")
    s += text(x, 290, "перевір: Ib ≤ Iвиводу МК (≈20–40 мА)? ✓", 11, "#9c6a16", "start", "bold")
    s += text(x, 312, "перевір: Vce(sat) < 0.3 В у даташиті? ✓", 11, "#9c6a16", "start", "bold")
    s += text(x, 334, "не лізе → потрібен Дарлінгтон або MOSFET", 10.5, GREY, "start", style="italic")
    s += text(W / 2, H - 10, "Округляй Rб ВНИЗ (більше бази — безпечніше); але стеж, щоб струм бази не перевищив дозволений для виводу.",
              10, GREY, "middle", style="italic")
    save("fig-11-6m-3-derive.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  🔌 Вставка до §2.6.9 — Модуль реле (Рис. 2.6.9c.k)
# ═════════════════════════════════════════════════════════════════════════════
def fig9c1_module_anatomy():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 28, "Що на платі реле-модуля, крім самого реле", 17, INK, "middle", "bold")
    # ланцюг блоків
    blocks = [
        (40, "вхід IN", LGRN, GREEN, ["сигнал від", "МК (~мА)"]),
        (200, "оптопара", LBLUE, BLUE, ["ізоляція", "(§2.5.10)"]),
        (360, "транзистор", "#fbfbfb", INK, ["ключ (§2.6.6)", "або ULN"]),
        (520, "реле + діод", LRED, RED, ["котушка +", "гасний діод"]),
        (680, "клемник", "#f4eef6", "#7a4e8a", ["COM/NO/NC", "до навантаж."]),
    ]
    y = 120
    for i, (x, t, fill, bc, lines) in enumerate(blocks):
        s += rect(x, y, 140, 90, fill, bc, 1.8, 8)
        s += text(x + 70, y + 26, t, 11.5, INK, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(x + 70, y + 50 + k * 18, ln, 9.5, GREY, "middle")
        if i < len(blocks) - 1:
            s += arrow(x + 140, y + 45, x + 160, y + 45, GREY, 2)
    # додаткові деталі
    s += circle(430, 250, 9, "#fff3b0", SUN, 1.6) + text(430, 280, "LED-індикатор", 9.5, INK, "middle", "bold")
    s += text(430, 296, "(видно, що реле ввімкнене)", 9, GREY, "middle")
    s += rect(150, 240, 90, 34, "#fbfbfb", "#c9d3dc", 1.4, 4)
    s += text(195, 262, "джампер", 10, INK, "middle", "bold")
    s += text(195, 296, "живлення котушки", 9, GREY, "middle")
    s += text(195, 312, "(VCC / JD-VCC)", 8.5, GREY, "middle")
    s += text(650, 258, "роз'єм керування:", 10, INK, "middle", "bold")
    s += text(650, 276, "VCC · IN · GND", 11, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Готовий модуль — це вся схема драйвера з теми вже зібрана: ключ, діод, часто оптопара та індикатор.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9c-1-module-anatomy.svg", s)


def fig9c2_jumper_activelow():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 28, "Дві пастки модуля: джампер живлення й active-low вхід", 16, INK, "middle", "bold")
    # ── джампер ──
    s += _frame(40, 56, 400, 300, "джампер VCC ↔ JD-VCC")
    # варіант 1: разом
    s += text(240, 86, "джампер НА МІСЦІ (за умовчанням):", 10.5, INK, "middle", "bold")
    s += rect(90, 100, 60, 28, LGRN, GREEN, 1.4, 4) + text(120, 118, "VCC", 9.5, INK, "middle", "bold")
    s += rect(330, 100, 60, 28, LRED, RED, 1.4, 4) + text(360, 118, "JD-VCC", 9, INK, "middle", "bold")
    s += line(150, 114, 330, 114, INK, 3)
    s += text(240, 146, "котушка живиться від тієї ж шини,", 9.5, GREY, "middle")
    s += text(240, 162, "що й логіка → ізоляція ФІКТИВНА", 9.5, "#9a2b22", "middle", "bold")
    s += line(70, 184, 410, 184, "#ddd", 1)
    # варіант 2: окремо
    s += text(240, 210, "джампер ЗНЯТО, JD-VCC від ОКРЕМОГО джерела:", 10, INK, "middle", "bold")
    s += rect(90, 226, 60, 28, LGRN, GREEN, 1.4, 4) + text(120, 244, "VCC", 9.5, INK, "middle", "bold")
    s += rect(330, 226, 60, 28, LRED, RED, 1.4, 4) + text(360, 244, "JD-VCC", 9, INK, "middle", "bold")
    s += text(120, 272, "логіка", 9, "#1f6e33", "middle")
    s += text(360, 272, "окреме живлення котушки", 8.5, "#9a2b22", "middle")
    s += text(240, 300, "тепер оптопара справді розв'язує", 9.5, "#1f6e33", "middle", "bold")
    s += text(240, 316, "брудний бік котушки від логіки", 9.5, GREY, "middle")
    s += text(240, 340, "правда ізоляції — лише з окремим живленням", 9, "#9c6a16", "middle", style="italic")
    # ── active-low ──
    s += _frame(460, 56, 360, 300, "active-low: вмикає «0», а не «1»")
    s += text(640, 92, "багато модулів реле ввімкнено", 10.5, INK, "middle")
    s += text(640, 110, "при логічному НУЛІ на вході", 10.5, RED, "middle", "bold")
    s += text(640, 144, "IN = 0  →  реле ВВІМКНЕНО", 11, "#1f6e33", "middle", "bold")
    s += text(640, 166, "IN = 1  →  реле вимкнено", 11, GREY, "middle", "bold")
    s += text(640, 200, "чому: струм тече крізь світлодіод", 9.5, GREY, "middle")
    s += text(640, 216, "оптопари, коли вивід МК тягне його", 9.5, GREY, "middle")
    s += text(640, 232, "до землі (інверсія §2.6.7)", 9.5, GREY, "middle")
    s += text(640, 268, "пастка: реле клацає під час СКИДАННЯ", 9.5, "#9c6a16", "middle", "bold")
    s += text(640, 284, "МК (виводи ще не налаштовані → «0»)", 9, GREY, "middle")
    s += text(640, 316, "рішення: інвертувати логіку в коді", 9.5, INK, "middle", "bold")
    s += text(640, 332, "й не лякатися клацання на старті", 9, GREY, "middle")
    save("fig-11-9c-2-jumper-activelow.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  §11.9 — Реле і його драйвер (тема 2.6.9)
# ═════════════════════════════════════════════════════════════════════════════
def fig91_relay_inside():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 30, "Реле зсередини: електромагніт рухає якір, якір — контакти", 16, INK, "middle", "bold")
    # котушка-електромагніт (вертикальна, на осерді)
    cx, cy = 150, 250
    s += rect(cx - 22, cy - 70, 44, 110, "#f3e8d2", "#9c6a16", 1.4, 4)
    for i in range(6):
        s += line(cx - 22, cy - 60 + i * 20, cx + 22, cy - 60 + i * 20, COPP, 2.4)
    s += rect(cx - 6, cy - 78, 12, 126, "#cfd4d9", INK, 1.2)  # осердя
    s += text(cx, cy + 64, "котушка", 11, COPP, "middle", "bold")
    s += text(cx, cy + 80, "(електромагніт)", 9.5, GREY, "middle")
    s += line(cx - 22, cy + 40, cx - 60, cy + 40, INK, 2) + text(cx - 64, cy + 44, "+", 12, RED, "end", "bold")
    s += line(cx + 22, cy + 40, cx + 60, cy + 40, INK, 2) + text(cx + 64, cy + 44, "−", 12, BLUE, "start", "bold")
    s += text(cx, cy + 100, "керування (5/12 В DC)", 9.5, INK, "middle")
    # якір (важіль), що притягується до осердя
    ax = cx + 6
    s += line(ax, cy - 90, 430, cy - 110, INK, 4)  # якір-важіль
    s += circle(ax, cy - 90, 4, INK, INK)  # вісь
    s += arrow(ax + 30, cy - 70, ax + 14, cy - 84, RED, 1.8)
    s += text(ax + 70, cy - 56, "магніт притягує якір", 10, RED, "middle", "bold")
    # пружина
    s += _poly([(ax + 90, cy - 100), (ax + 96, cy - 112), (ax + 102, cy - 100), (ax + 108, cy - 112), (ax + 114, cy - 100)], GREEN, 2)
    s += text(ax + 102, cy - 122, "пружина (вертає назад)", 9, GREEN, "middle")
    # контакти COM / NO / NC
    comx = 430
    s += circle(comx, cy - 110, 5, INK, INK) + text(comx, cy - 124, "COM", 9.5, INK, "middle", "bold")
    s += text(comx + 8, cy - 108, "(рухомий)", 8.5, GREY, "start")
    s += circle(comx + 70, cy - 150, 5, GREEN, GREEN, 0) + text(comx + 90, cy - 150, "NO (норм. розімкн.)", 9.5, "#1f6e33", "start", "bold")
    s += circle(comx + 70, cy - 70, 5, RED, RED, 0) + text(comx + 90, cy - 70, "NC (норм. замкн.)", 9.5, "#9a2b22", "start", "bold")
    s += line(comx, cy - 110, comx + 70, cy - 72, GREY, 1.6, dash="4,3")  # у спокої — на NC
    s += line(comx, cy - 110, comx + 70, cy - 148, INK, 2)  # під струмом — на NO
    s += text(comx + 40, cy - 30, "потужні контакти:", 9.5, INK, "middle", "bold")
    s += text(comx + 40, cy - 14, "мережа, мотор, нагрівач", 9, GREY, "middle")
    s += text(W / 2, H - 14, "Слабкий струм у котушці рухає якір, той перемикає COM між NC і NO — і ці контакти комутують потужне коло.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9-1-relay-inside.svg", s)


def fig91_why_relay():
    W, H = 760, 350
    s = header(W, H)
    s += text(W / 2, 30, "Навіщо реле: розв'язати кволу логіку й потужну мережу", 16, INK, "middle", "bold")
    # бік керування
    s += rect(50, 90, 250, 180, LGRN, GREEN, 1.8, 10)
    s += text(175, 116, "бік керування", 12, "#1f6e33", "middle", "bold")
    s += text(175, 150, "5/12 В DC", 15, "#1f6e33", "middle", "bold")
    s += text(175, 178, "котушка: десятки мА", 10, GREY, "middle")
    s += text(175, 200, "тиха «логічна» земля", 10, GREY, "middle")
    s += text(175, 232, "(транзистор-драйвер тут)", 9.5, INK, "middle")
    # бар'єр
    s += rect(330, 80, 50, 200, "#eef3fb", "#9bb0c2", 1.6, 6)
    s += text(355, 70, "магнітний зв'язок,", 9, "#5b6b7a", "middle")
    s += text(355, 300, "контакти — НЕ дріт", 9, "#5b6b7a", "middle")
    s += arrow(300, 180, 330, 180, COPP, 2)
    s += arrow(380, 180, 410, 180, COPP, 2)
    # бік навантаження
    s += rect(410, 90, 300, 180, LRED, RED, 1.8, 10)
    s += text(560, 116, "бік навантаження", 12, RED, "middle", "bold")
    s += text(560, 150, "230 В ~ / мотор", 15, RED, "middle", "bold")
    s += text(560, 178, "контакти: ампери", 10, GREY, "middle")
    s += text(560, 200, "«брудна» силова земля", 10, GREY, "middle")
    s += text(560, 232, "(гальванічно відділено)", 9.5, INK, "middle")
    s += text(W / 2, H - 14, "Котушка й контакти електрично НЕ з'єднані — реле само собою дає гальванічну розв'язку (пор. оптопару §2.5.10).",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9-2-why-relay.svg", s)


def fig91_full_driver():
    W, H = 780, 420
    s = header(W, H)
    s += text(W / 2, 28, "Повна схема драйвера: усе модуля разом", 16.5, INK, "middle", "bold")
    s += line(140, 70, 600, 70, RED, 2) + text(132, 74, "+V", 11, RED, "end", "bold")
    # котушка реле
    s += rect(360, 92, 50, 70, "#f3e8d2", "#9c6a16", 1.6, 4)
    s += text(385, 122, "реле", 10, INK, "middle", "bold") + text(385, 138, "(котушка)", 8.5, GREY, "middle")
    s += line(385, 70, 385, 92, INK, 2)
    # flyback-діод
    dx = 490
    s += line(dx, 70, dx, 96, INK, 2)
    s += f'<path d="M {dx-10},128 L {dx+10},128 L {dx},98 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.6"/>\n'
    s += line(dx - 10, 96, dx + 10, 96, INK, 2.4)
    s += line(dx, 128, dx, 176, INK, 2)
    s += text(dx + 14, 110, "гасний діод (§2.5.9)", 9.5, GREEN, "start", "bold")
    s += text(dx + 14, 126, "зрізає брикання §2.2.5", 9, GREY, "start")
    s += line(385, 162, 385, 176, INK, 2)
    s += line(385, 176, dx, 176, INK, 2)
    # транзистор-ключ
    s += _bjt_sym(355, 230, True)
    s += text(420, 210, "ключ §2.6.6", 9.5, INK, "start", "bold")
    s += line(385, 176, 385, 174, INK, 2)
    s += line(385, 286, 385, 320, INK, 2)
    s += line(140, 320, 600, 320, INK, 1.4) + text(132, 324, "GND", 10, INK, "end", "bold")
    # база
    s += line(210, 230, 311, 230, INK, 2)
    s += rect(232, 218, 54, 24, "#fff", INK, 1.6) + text(259, 234, "Rб", 10, INK, "middle", "bold")
    s += rect(90, 206, 100, 48, "#eef6ef", GREEN, 1.6, 6) + text(140, 235, "MCU", 12, INK, "middle", "bold")
    s += text(140, 198, "вивід ~мА", 8.5, GREY, "middle")
    s += line(190, 230, 210, 230, GREEN, 2)
    # підписи зшивання
    s += text(W / 2, 372, "одна схема зшиває три теми: транзистор-ключ (§2.6.6) керує котушкою (§2.2.1),",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 392, "а гасний діод (§2.5.9) приборкує її викид при вимкненні (§2.2.5).",
              10.5, INK, "middle", "bold")
    save("fig-11-9-3-full-driver.svg", s)


def fig91_pickup_dropout():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 28, "Спрацювання, утримання й дребезг контактів", 16, INK, "middle", "bold")
    # струм котушки: спрацювання > утримання
    ox, oy, w = 70, 150, 300
    s += _frame(40, 60, 350, 230, "струм котушки")
    s += line(ox, oy, ox + w, oy, INK, 1.4) + text(ox + w, oy + 16, "I котушки", 9.5, INK, "start")
    s += line(ox, oy, ox, oy - 90, INK, 1.4)
    s += line(ox, oy - 70, ox + w, oy - 70, RED, 1.2, dash="5,4") + text(ox + w, oy - 74, "спрацювання", 8.5, RED, "end")
    s += line(ox, oy - 35, ox + w, oy - 35, GREEN, 1.2, dash="5,4") + text(ox + w, oy - 39, "утримання", 8.5, "#1f6e33", "end")
    s += text(ox + 20, oy + 36, "втягнути якір треба БІЛЬШИМ струмом,", 9, GREY, "start")
    s += text(ox + 20, oy + 52, "ніж утримати втягнутим (гістерезис)", 9, GREY, "start")
    s += text(ox + 150, oy - 100, "≈ у 2–3 рази", 9.5, INK, "middle", "bold")
    # дребезг
    s += _frame(410, 60, 320, 230, "контакт при замиканні")
    ox2, oy2 = 440, 160
    s += line(ox2, oy2, ox2 + 260, oy2, INK, 1.3)
    pts = [(ox2, oy2)]
    x = ox2 + 60
    for k in range(5):
        pts += [(x, oy2), (x, oy2 - 40), (x + 8, oy2 - 40), (x + 8, oy2), (x + 16, oy2)]
        x += 16 - k * 2
    pts += [(x, oy2 - 40), (ox2 + 260, oy2 - 40)]
    s += _poly(pts, COPP, 2)
    s += text(ox2 + 130, oy2 + 28, "дребезг: контакт кілька разів", 9, GREY, "middle")
    s += text(ox2 + 130, oy2 + 44, "відскакує, перш ніж замкнутись", 9, GREY, "middle")
    s += text(ox2 + 130, oy2 - 56, "у коді — антидребезг", 9, "#9c6a16", "middle", "bold")
    s += text(W / 2, H - 14, "Реле повільне (мілісекунди) і дребезжить контактами — це враховують і в живленні котушки, і в логіці.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9-4-pickup-dropout.svg", s)


def fig91_arc_snubber():
    W, H = 760, 350
    s = header(W, H)
    s += text(W / 2, 28, "Іскра на контактах — і як її гасять", 16, INK, "middle", "bold")
    # ліворуч: дуга
    s += _frame(40, 60, 330, 230, "розмикання під навантаженням")
    s += line(120, 130, 180, 130, INK, 3) + circle(180, 130, 4, INK, INK)
    s += line(230, 130, 290, 130, INK, 3) + circle(230, 130, 4, INK, INK)
    s += _poly([(184, 130), (198, 122), (208, 138), (220, 126), (228, 130)], RED, 2.2)
    s += text(205, 108, "дуга / іскра", 10, RED, "middle", "bold")
    s += text(205, 175, "розмикання струму палить контакти,", 9.5, GREY, "middle")
    s += text(205, 191, "точить їх і скорочує ресурс", 9.5, GREY, "middle")
    s += text(205, 220, "найгірше — індуктивне навантаження", 9, "#9c6a16", "middle", "bold")
    s += text(205, 236, "(моторчик: власне брикання §2.2.5)", 9, GREY, "middle")
    # праворуч: засоби
    s += _frame(410, 60, 320, 230, "гасіння")
    s += text(570, 92, "DC-навантаження:", 10.5, INK, "middle", "bold")
    s += text(570, 110, "гасний діод на навантаженні", 9.5, "#1f6e33", "middle")
    s += text(570, 140, "AC-навантаження:", 10.5, INK, "middle", "bold")
    s += text(570, 158, "RC-снабер на контактах (§2.2.5)", 9.5, "#1f6e33", "middle")
    s += text(570, 188, "правильний номінал контактів:", 10.5, INK, "middle", "bold")
    s += text(570, 206, "AC і DC рейтинги РІЗНІ (DC гірше —", 9.5, GREY, "middle")
    s += text(570, 222, "дуга не гасне на переході через нуль)", 9.5, GREY, "middle")
    s += text(570, 252, "велике/часте навантаження → SSR", 9.5, "#7a4e8a", "middle", "bold")
    s += text(W / 2, H - 14, "Контакти — найслабша ланка реле: їх беруть із запасом за струмом і гасять дугу діодом чи снабером.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9-5-arc-snubber.svg", s)


def fig91_relay_types():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 28, "Реле бувають різні: контакти, засувка, геркон", 16, INK, "middle", "bold")
    # SPST / SPDT / DPDT
    def contacts(ox, oy, kind):
        out = ""
        if kind == "SPST":
            out += circle(ox, oy, 4, INK, INK) + circle(ox + 60, oy, 4, INK, INK)
            out += line(ox, oy, ox + 50, oy - 16, INK, 2)
        elif kind == "SPDT":
            out += circle(ox, oy, 4, INK, INK)
            out += circle(ox + 60, oy - 18, 4, GREEN, GREEN, 0) + circle(ox + 60, oy + 18, 4, RED, RED, 0)
            out += line(ox, oy, ox + 54, oy + 16, INK, 2)
        else:  # DPDT
            for d in (-20, 20):
                out += circle(ox, oy + d, 4, INK, INK)
                out += circle(ox + 60, oy + d - 12, 4, GREEN, GREEN, 0) + circle(ox + 60, oy + d + 12, 4, RED, RED, 0)
                out += line(ox, oy + d, ox + 50, oy + d + 10, INK, 1.8)
        return out
    cards = [
        (40, "SPST", "1 контакт:", "просто вкл/викл"),
        (240, "SPDT", "перекидний:", "COM ↔ NO/NC"),
        (440, "DPDT", "дві групи:", "два кола разом"),
    ]
    for x, k, l1, l2 in cards:
        s += rect(x, 56, 180, 130, "#fbfbfb", "#c9d3dc", 1.4, 8)
        s += text(x + 90, 80, k, 12.5, INK, "middle", "bold")
        s += contacts(x + 40, 120, k)
        s += text(x + 90, 160, l1, 9.5, GREY, "middle")
        s += text(x + 90, 176, l2, 9.5, GREY, "middle")
    # latching + reed
    s += rect(640, 56, 150, 130, LGRN, GREEN, 1.6, 8)
    s += text(715, 80, "засувкове", 11.5, "#1f6e33", "middle", "bold")
    s += text(715, 100, "(latching)", 9.5, GREY, "middle")
    s += text(715, 126, "тримає стан", 9.5, INK, "middle")
    s += text(715, 142, "БЕЗ струму —", 9.5, INK, "middle")
    s += text(715, 158, "імпульс перемикає", 9, GREY, "middle")
    s += text(715, 176, "(економія енергії)", 9, GREY, "middle")
    s += text(W / 2, H - 40, "Окремо — герконове (reed): контакти в скляній колбі, мала котушка, швидке й чисте, але на малі струми.",
              10, GREY, "middle", style="italic")
    s += text(W / 2, H - 18, "● зелений — NO, ● червоний — NC. Більше груп контактів = більше кіл, що перемикаються одним якорем.",
              10, GREY, "middle", style="italic")
    save("fig-11-9-7-relay-types.svg", s)


def fig91_alternatives():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 28, "Три способи комутувати потужне коло слабким сигналом", 16, INK, "middle", "bold")
    cards = [
        (40, "електромеханічне реле", LGRN, GREEN,
         ["+ дешеве, ізоляція, AC і DC", "+ малий опір контактів", "− повільне, дребезг, зношується", "− клацає, котушка тягне струм"]),
        (300, "MOSFET-ключ (Розд. 2.7)", LBLUE, BLUE,
         ["+ швидкий, без механіки", "+ майже без струму керування", "− тільки DC, без ізоляції", "− спільна земля з навантаженням"]),
        (560, "твердотільне реле / SSR", "#f4eef6", "#7a4e8a",
         ["+ без механіки, ізоляція (оптопара", "  §2.5.10), тихе, довговічне", "− дорожче, гріється, є витік", "− AC-версії з нуль-переходом"]),
    ]
    for x, title, fill, bc, lines in cards:
        s += rect(x, 60, 240, 230, fill, bc, 1.8, 10)
        s += text(x + 120, 86, title, 11.5, INK, "middle", "bold")
        s += line(x + 16, 98, x + 224, 98, "#ccc", 1)
        for k, ln in enumerate(lines):
            s += text(x + 16, 124 + k * 30, ln, 9.5, INK, "start")
    s += text(W / 2, H - 14, "Електромеханічне — універсальне й дешеве; MOSFET — для швидкого DC без ізоляції; SSR — для частого AC.",
              10.5, GREY, "middle", style="italic")
    save("fig-11-9-6-alternatives.svg", s)


if __name__ == "__main__":
    fig_t1_timeline()
    fig_t2_tube_problem()
    fig_t3_point_contact()
    fig_t4_rivalry()
    fig_t5_legacy()
    # §11.1 ідея транзистора
    fig11_valve_analogy()
    fig11_small_controls_large()
    fig11_amplify()
    fig11_switch()
    fig11_active_vs_passive()
    fig11_vs_relay_tube()
    # §11.2 будова BJT
    fig21_sandwich()
    fig21_terminals()
    fig21_two_junctions()
    fig21_not_two_diodes()
    fig21_symbols()
    fig21_npn_vs_pnp()
    # §11.3 як працює
    fig31_biasing()
    fig31_injection()
    fig31_cross_base()
    fig31_base_current()
    fig31_ic_ib_ratio()
    fig31_turnstile()
    # §11.4 коефіцієнт β
    fig41_beta_def()
    fig41_beta_spread()
    fig41_beta_vs_ic()
    fig41_datasheet()
    fig41_worked()
    fig41_design_margin()
    # §11.5 режими
    fig51_three_modes()
    fig51_cutoff()
    fig51_active()
    fig51_saturation()
    fig51_transfer()
    fig51_output_curves()
    # §11.6 BJT як ключ
    fig62_mcu_drives_relay()
    fig62_switch_circuit()
    fig62_on_off()
    fig62_base_resistor()
    fig62_flyback()
    fig62_low_vs_high_side()
    # §11.7 BJT як підсилювач
    fig71_bias_point()
    fig71_common_emitter()
    fig71_inversion()
    fig71_gain()
    fig71_clipping()
    fig71_emitter_follower()
    # §11.8 практика: вибір і керування навантаженням
    fig81_datasheet()
    fig81_relay_worked()
    fig81_selection_flow()
    fig81_power_heat()
    fig81_darlington()
    fig81_bjt_vs_mosfet()
    # 🧮 вставка до §2.6.6 — розрахунок резистора бази
    fig6m1_two_points()
    fig6m2_forced_beta()
    fig6m3_derive()
    # 🧮 вставка до §2.6.7 — навантажувальна пряма
    fig7m1_build()
    fig7m2_q_position()
    fig7m3_swing()
    # 🔌 вставка до §2.6.6 — Дарлінгтон і ULN2003
    fig6c1_uln_inside()
    fig6c2_uln_use()
    # 🔌 вставка до §2.6.6 — PNP high-side ключ
    fig6c3_low_vs_high()
    fig6c4_pnp_driver()
    # 🔌 вставка до §2.6.7 — підсилювач зі спільним емітером на макетці
    fig7c1_breadboard_amp()
    fig7c2_tune_debug()
    # 🔌 вставка до §2.6.8 — робочі конячки BJT
    fig8c1_workhorses()
    fig8c2_pinout_trap()
    # 🔌 вставка до §2.6.9 — реле зсередини (контакти)
    fig9c3_ratings()
    fig9c4_life_dc()
    # ⚙️ вставка до §2.6.4 — виміряти β самому
    fig4a1_two_ways()
    fig4a2_procedure()
    # 📜 історія до §2.6.1 — зрадницька вісімка
    fig1i_timeline()
    fig1i_eight()
    fig1i_irony()
    # 📜 історія до §2.6.8 — Regency TR-1 і Sony
    fig8i_timeline()
    fig8i_tube_vs_transistor()
    fig8i_who_won()
    # 🔌 вставка до §2.6.9 — модуль реле
    fig9c1_module_anatomy()
    fig9c2_jumper_activelow()
    # §11.9 реле і його драйвер (тема 2.6.9)
    fig91_relay_inside()
    fig91_why_relay()
    fig91_full_driver()
    fig91_pickup_dropout()
    fig91_arc_snubber()
    fig91_relay_types()
    fig91_alternatives()
    print("OK — Розділ 11 (історія + §11.1–§11.9) згенеровано в", OUT)
