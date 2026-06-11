# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для алгоритмічної вставки 2.10.6a
«Виміряти власний дрейф: порівняння з точнішим джерелом, накопичення різниці».
Чистий Python, без сторонніх залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-r10-s6a-…), щоб не зачіпати головний figs.py розділу
та інші вставки (порівн. fig-10-6m-… у ppm-math).

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з попередніх скриптів модуля.
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aSun" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{SUN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", BLUE: "aBlue", SUN: "aSun"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round" '
            f'marker-end="url(#{m})"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    r = f' rx="{rx}"' if rx else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"'
            f'{r} fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = '"Consolas","Courier New",monospace' if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family={fam!r} '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linecap="round" stroke-linejoin="round"/>\n')


def save(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Рис. 2.10.6a.1 — принцип: рахуємо такти ВЛАСНОГО кварцу за ворота,
# відкриті ТОЧНИМ джерелом (1 с від GPS). Що довша хвіртка — то точніший ppm.
# ---------------------------------------------------------------------------
def fig1():
    W, H = 760, 486
    s = header(W, H)
    s += text(W / 2, 28, "Ворота від точного джерела, лічба — від свого кварцу", 17, INK, "middle", "bold")

    # --- верхня частина: дві хвилі і вікно лічби ---
    # вісь часу
    xL, xR = 70, W - 40
    # ВОРОТА (від точного джерела): прямокутне вікно
    gate_y = 86
    gx0, gx1 = 150, 560
    s += text(xL, gate_y - 22, "ТОЧНЕ джерело: відмірює рівно 1.000000 с", 13, GREEN, "start", "bold")
    s += rect(gx0, gate_y, gx1 - gx0, 34, fill=LGRN, stroke=GREEN, sw=2, rx=4)
    s += text((gx0 + gx1) / 2, gate_y + 22, "ВОРОТА відкриті (gate)", 13, GREEN, "middle", "bold")
    s += arrow(gx0, gate_y + 50, gx1, gate_y + 50, GREEN, 1.6)
    s += arrow(gx1, gate_y + 50, gx0, gate_y + 50, GREEN, 1.6)
    s += text((gx0 + gx1) / 2, gate_y + 66, "T_gate (опорна секунда)", 12, GREEN, "middle", style="italic")

    # ВЛАСНИЙ кварц: меандр, рахуємо фронти всередині воріт
    osc_y = 200
    s += text(xL, osc_y - 14, "ТВІЙ кварц 16 МГц: лічильник рахує фронти", 13, BLUE, "start", "bold")
    # намалюємо умовний меандр (символічно ~12 періодів)
    n = 12
    per = (xR - xL) / n
    pts = []
    yhi, ylo = osc_y + 6, osc_y + 30
    x = xL
    lvl = ylo
    pts.append((x, lvl))
    for i in range(n * 2):
        nxt = x + per / 2
        pts.append((nxt, lvl))
        lvl = yhi if lvl == ylo else ylo
        pts.append((nxt, lvl))
        x = nxt
    s += polyline(pts, BLUE, 2)
    # підсвітити вікно лічби на меандрі
    s += rect(gx0, osc_y + 2, gx1 - gx0, 34, fill="none", stroke=GREEN, sw=1.6, dash="5 4", rx=3)
    # «тики» лічильника всередині
    cnt = 0
    xx = gx0
    while xx < gx1:
        if xx >= xL:
            s += line(xx, osc_y + 2, xx, osc_y - 2, GREEN, 1.4)
        xx += per
        cnt += 1
    s += text((gx0 + gx1) / 2, osc_y + 56,
              "N = скільки фронтів вмістилось у ворота", 12, INK, "middle")

    # --- нижня частина: формула + таблиця «довша хвіртка → дрібніший крок» ---
    fy = 296
    s += line(50, fy - 18, W - 40, fy - 18, FAINT, 1.5)
    s += text(60, fy + 4, "f_виміряна = N / T_gate     →     похибка = (f_вим − f_номінал) / f_номінал", 14, INK, "start", mono=True)
    s += text(60, fy + 26, "роздільність = ±1 такт за все вікно: фіксована невизначеність / T_gate", 13, GREY, "start", mono=True)

    # таблиця: фіксована невизначеність старт/стоп (±1 такт 16 МГц = 62.5 нс)
    # розмазується по воротах → крок у ppm = 62.5нс / T_gate
    f0 = 16e6
    tick_s = 1.0 / f0  # 62.5 нс
    rows = [
        ("1 с", 1.0),
        ("10 с", 10.0),
        ("100 с", 100.0),
    ]
    ty = fy + 62
    cx_g = 95
    cx_step = 300
    cx_note = 480
    s += text(cx_g, ty, "ворота", 12, GREY, "start", "bold")
    s += text(cx_step, ty, "крок у ppm", 12, GREY, "start", "bold")
    s += text(cx_note, ty, "що бачимо", 12, GREY, "start", "bold")
    ty += 8
    s += line(85, ty, W - 75, ty, FAINT, 1.2)
    ty += 26
    notes = ["вже дрібніше за дрейф кварцу",
             "впевнено ловимо одиниці ppm",
             "доходимо до часток ppm"]
    cols = [SUN, BLUE, GREEN]
    for (g_lab, g_t), note, col in zip(rows, notes, cols):
        step_ppm = (tick_s / g_t) * 1e6  # фіксований ±1 такт за ворота → ppm
        s += text(cx_g, ty, g_lab, 16, col, "start", "bold")
        s += text(cx_step, ty, f"≈ {step_ppm:.4g} ppm", 15, INK, "start", mono=True)
        s += text(cx_note, ty, note, 13, GREY, "start")
        ty += 29

    s += text(W / 2, H - 12,
              "Свого таймера для лічби мало — він сам бреше. Ворота МУСЯТЬ приходити ззовні, від точнішого джерела.",
              12.5, GREY, "middle", style="italic")
    s += footer()
    save("fig-r10-s6a-1-gated-count.svg", s)


# ---------------------------------------------------------------------------
# Рис. 2.10.6a.2 — накопичення різниці: дві «годинникові» лінії розходяться,
# накопичена помилка росте лінійно; її нахил = ppm. Довге спостереження
# витягує крихітний дрейф із шуму одного відліку.
# ---------------------------------------------------------------------------
def fig2():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 28, "Накопичення різниці: маленький ppm за довгий час стає видимим", 16.5, INK, "middle", "bold")

    # осі: X = час спостереження (год), Y = накопичена різниця (с)
    ox, oy = 90, 330          # початок координат
    ax_w, ax_h = W - 150, 250
    s += arrow(ox, oy, ox + ax_w, oy, INK, 2)            # X
    s += arrow(ox, oy, ox, oy - ax_h, INK, 2)            # Y
    s += text(ox + ax_w, oy + 28, "час спостереження", 13, GREY, "end")
    s += text(ox + ax_w, oy + 44, "(години)", 12, GREY, "end")
    s += text(ox - 60, oy - ax_h + 6, "накопичена", 12, GREY, "start")
    s += text(ox - 60, oy - ax_h + 22, "різниця Δt", 12, GREY, "start")

    hours_max = 24.0
    # масштаб Y: підберемо так, щоб найбільший дрейф (50 ppm) майже дійшов до верху
    # 50 ppm за 24 год = 50e-6 * 24*3600 = 4.32 с
    dt_max = 50e-6 * hours_max * 3600 * 1.08
    def xof(h):
        return ox + h / hours_max * ax_w
    def yof(dt):
        return oy - dt / dt_max * ax_h

    # сітка X
    for h in (0, 6, 12, 18, 24):
        x = xof(h)
        s += line(x, oy, x, oy + 5, INK, 1.6)
        s += text(x, oy + 20, f"{h}", 12, INK, "middle")
    # сітка Y (секунди)
    for dt in (0, 1, 2, 3, 4):
        y = yof(dt)
        s += line(ox - 5, y, ox, y, INK, 1.6)
        s += text(ox - 12, y + 4, f"{dt} с", 12, INK, "end")
        if dt:
            s += line(ox, y, ox + ax_w, y, FAINT, 1)

    # три прямі: нахил = ppm. Δt = ppm*1e-6 * (h*3600)
    lines = [
        (50, SUN,  "+50 ppm (дешевий кварц)"),
        (20, BLUE, "+20 ppm (хороший кварц)"),
        (2,  GREEN, "+2 ppm (TCXO)"),
    ]
    for ppm, col, lab in lines:
        pts = [(xof(h), yof(ppm * 1e-6 * h * 3600)) for h in (0, hours_max)]
        s += polyline(pts, col, 2.6)
        # підпис біля кінця
        xe, ye = pts[-1]
        if ppm == 50:
            s += text(xe - 6, ye + 4, lab, 12.5, col, "end", "bold")
        elif ppm == 20:
            s += text(xe - 6, ye + 16, lab, 12.5, col, "end", "bold")
        else:
            s += text(xe - 6, ye - 8, lab, 12.5, col, "end", "bold")

    # маркер: один «миттєвий» відлік потопає в шумі (хмарка точок біля початку),
    # а нахил довгої лінії — чистий
    import random
    random.seed(7)
    for _ in range(40):
        hh = random.uniform(0.05, 1.0)
        true_dt = 20e-6 * hh * 3600
        noise = random.gauss(0, 0.06)   # ±60 мс джиттер одного відліку
        s += circle(xof(hh), yof(true_dt + noise), 1.8, fill=GREY, stroke="none")
    s += text(xof(2.0), yof(0.55), "один короткий замір", 11.5, GREY, "start", style="italic")
    s += text(xof(2.0), yof(0.55) + 15, "тоне в джиттері", 11.5, GREY, "start", style="italic")
    s += arrow(xof(2.0), yof(0.55) + 6, xof(0.7), yof(0.3), GREY, 1.3)

    # формула нахилу
    s += rect(xof(8.5), yof(4.25), 250, 52, fill="#ffffff", stroke=FAINT, sw=1.4, rx=6)
    s += text(xof(8.5) + 12, yof(4.25) + 21, "нахил = Δt / Δспостереження", 13, INK, "start", mono=True)
    s += text(xof(8.5) + 12, yof(4.25) + 41, "ppm = нахил × 10⁶", 13, RED, "start", "bold", mono=True)

    s += text(W / 2, H - 10,
              "Знак каже напрям: лінія вгору — кварц спішить (швидший за еталон), униз — відстає.",
              12.5, GREY, "middle", style="italic")
    s += footer()
    save("fig-r10-s6a-2-accumulate.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done")
