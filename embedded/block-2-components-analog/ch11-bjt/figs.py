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
    print("OK — Розділ 11 (історія + §11.1–§11.8) згенеровано в", OUT)
