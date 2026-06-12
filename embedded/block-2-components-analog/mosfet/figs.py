# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 12 — «Польовий транзистор (MOSFET)» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Підписи посекційно (Рис. C.S.N); для історії до розділу —
секція 0 (Рис. 12.0.N). Допоміжні функції скопійовано з попередніх розділів.
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


# ── Рис. 12.0.1 — таймлайн із прогалиною ─────────────────────────────────────
def fig_t1_timeline():
    W, H = 920, 240
    s = header(W, H)
    s += text(W / 2, 32, "Найдовша пауза в електроніці: ідея 1925 → прилад 1959", 17, INK, "middle", "bold")
    boxes = [
        (20, "1925 · Лілієнфельд", ["ідея польового", "транзистора"], "#fdf1dc"),
        (185, "1934 · Гайль", ["подає заявку", "(патент 1935)"], "#fdf1dc"),
        (560, "1959 · Аталла й Кан", ["перший робочий", "MOSFET"], LGRN),
        (725, "сьогодні", ["найпоширеніший", "прилад на Землі"], LGRN),
    ]
    bw, by, bh = 150, 84, 96
    for bx, lab, lines, fill in boxes:
        s += text(bx + bw / 2, by - 8, lab, 10.5, INK, "middle", "bold")
        border = "#9bb0c2" if fill == LGRN else "#d8b46a"
        s += rect(bx, by, bw, bh, fill, border, 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 40 + k * 22, ln, 11, INK, "middle")
    gx0, gx1 = 345, 552
    s += rect(gx0, by + 18, gx1 - gx0, bh - 36, "#f6eef0", "#d8a0a0", 1.4, 8)
    s += text((gx0 + gx1) / 2, by + bh / 2 - 4, "≈ 25 років тиші", 12.5, RED, "middle", "bold")
    s += text((gx0 + gx1) / 2, by + bh / 2 + 16, "поверхня все псувала", 10, INK, "middle")
    s += arrow(170, by + bh / 2, 183, by + bh / 2, GREY, 2)
    s += arrow(337, by + bh / 2, 343, by + bh / 2, GREY, 2)
    s += arrow(553, by + bh / 2, 558, by + bh / 2, GREY, 2)
    s += arrow(710, by + bh / 2, 723, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14, "Правильну ідею тридцять років не вдавалося втілити — бракувало чистого матеріалу й знань про поверхню.",
              11, GREY, "middle", style="italic")
    save("fig-12-0-1-timeline.svg", s)


# ── Рис. 12.0.2 — ідея польового керування ───────────────────────────────────
def fig_t2_lilienfeld_idea():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 30, "Задум Лілієнфельда (1925): керувати струмом полем", 16, INK, "middle", "bold")
    s += rect(180, 205, 360, 42, "#e3edfb", INK, 1.8) + text(360, 231, "напівпровідник — канал", 11, INK, "middle")
    s += line(120, 226, 180, 226, INK, 2.4) + text(150, 214, "джерело", 9.5, INK, "middle")
    s += line(540, 226, 600, 226, INK, 2.4) + text(572, 214, "стік", 9.5, INK, "middle")
    s += arrow(200, 272, 520, 272, RED, 2.2) + text(360, 290, "струм", 10, RED, "middle", "bold")
    s += rect(255, 120, 210, 24, "#f3e3c8", COPP, 1.8) + text(360, 137, "затвор — заряджена пластина", 10.5, INK, "middle", "bold")
    for i in range(5):
        s += text(285 + i * 30, 113, "+", 12, RED, "middle", "bold")
    for i in range(5):
        x = 290 + i * 35
        s += arrow(x, 146, x, 201, BLUE, 1.8, "4 3")
    s += text(500, 176, "поле", 11, BLUE, "start", "bold")
    s += text(W / 2, H - 12, "Заряд на затворі полем керує струмом у каналі — без жодного дотику. Принцип усіх польових транзисторів.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-0-2-lilienfeld-idea.svg", s)


# ── Рис. 12.0.3 — поверхневі стани ───────────────────────────────────────────
def fig_t3_surface_states():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 30, "Чому не виходило: пастки на поверхні екранують поле", 15.5, INK, "middle", "bold")
    s += rect(220, 78, 280, 22, "#f3e3c8", COPP, 1.8) + text(360, 94, "затвор", 10.5, INK, "middle", "bold")
    for i in range(6):
        s += text(250 + i * 40, 72, "+", 12, RED, "middle", "bold")
    for i in range(6):
        x = 250 + i * 40
        s += arrow(x, 102, x, 172, BLUE, 1.8)
    s += rect(200, 176, 320, 20, "#f6eef0", "#d8a0a0", 1.4)
    for i in range(13):
        cx0 = 214 + i * 24
        s += circle(cx0, 186, 5, "#fbecec", RED, 1.4) + line(cx0 - 2.5, 186, cx0 + 2.5, 186, RED, 1.4)
    s += text(360, 165, "поверхневі стани (пастки) ловлять заряд", 9.5, RED, "middle", "bold")
    s += rect(180, 196, 360, 84, "#eef2f6", INK, 1.6) + text(360, 244, "канал — поля не відчув, керування немає", 11, INK, "middle")
    s += text(W / 2, H - 12, "Обірвані зв'язки на поверхні перехоплюють поле затвора, мов заземлена сітка. Ідея правильна — фізика поверхні її душить.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-0-3-surface-states.svg", s)


# ── Рис. 12.0.4 — оксид вгамовує поверхню ────────────────────────────────────
def fig_t4_oxide_fix():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Прийом Аталли: шар скла (SiO₂) вгамовує поверхню", 15, INK, "middle", "bold")

    def panel(ox, title, fixed):
        t = _frame(ox, 52, 300, 240, title)
        gx = ox + 150
        t += rect(gx - 90, 74, 180, 18, "#f3e3c8", COPP, 1.6) + text(gx, 87, "затвор +", 9.5, INK, "middle", "bold")
        if fixed:
            t += rect(gx - 100, 150, 200, 16, "#fff3b0", SUN, 1.6) + text(gx, 162, "SiO₂ — скло", 9, INK, "middle", "bold")
            for i in range(5):
                x = gx - 72 + i * 36
                t += arrow(x, 94, x, 202, BLUE, 1.8)
            t += rect(ox + 30, 202, 240, 58, "#e9f6ee", GREEN, 1.6) + text(gx, 235, "канал відчув поле ✓", 10.5, GREEN, "middle", "bold")
            t += text(gx, 282, "поле проходить", 10, GREEN, "middle", "bold")
        else:
            for i in range(5):
                x = gx - 72 + i * 36
                t += arrow(x, 94, x, 150, BLUE, 1.8)
            t += rect(ox + 30, 150, 240, 18, "#f6eef0", "#d8a0a0", 1.3)
            for i in range(9):
                cx0 = ox + 48 + i * 26
                t += circle(cx0, 159, 4.5, "#fbecec", RED, 1.3) + line(cx0 - 2.2, 159, cx0 + 2.2, 159, RED, 1.3)
            t += text(gx, 142, "пастки", 9, RED, "middle", "bold")
            t += rect(ox + 30, 168, 240, 92, "#eef2f6", INK, 1.5) + text(gx, 218, "канал — поля нема ✗", 10.5, RED, "middle", "bold")
            t += text(gx, 282, "поле гасне", 10, RED, "middle", "bold")
        return t

    s += panel(40, "гола поверхня", False)
    s += panel(380, "поверхня під SiO₂", True)
    s += text(W / 2, H - 8, "Те саме скло заодно стало ідеальним ізолятором затвора — струму в нього не тече зовсім.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-0-4-oxide-fix.svg", s)


# ── Рис. 12.0.5 — будова першого MOSFET ──────────────────────────────────────
def fig_t5_first_mosfet():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 28, "Перший MOSFET (1959): метал – оксид – напівпровідник", 15, INK, "middle", "bold")
    s += rect(150, 210, 430, 86, "#e3edfb", INK, 1.8) + text(365, 282, "S — кремній (напівпровідник)", 11, INK, "middle")
    s += rect(160, 210, 80, 34, "#cfd6dd", INK, 1.5) + text(200, 231, "джерело n+", 8.5, INK, "middle")
    s += rect(490, 210, 80, 34, "#cfd6dd", INK, 1.5) + text(530, 231, "стік n+", 8.5, INK, "middle")
    s += rect(238, 192, 254, 18, "#fff3b0", SUN, 1.6) + text(365, 205, "O — оксид SiO₂ (ізолятор)", 9.5, INK, "middle", "bold")
    s += rect(258, 164, 214, 22, "#cfd6dd", INK, 1.6) + text(365, 179, "M — метал (затвор)", 10, INK, "middle", "bold")
    s += rect(240, 210, 250, 8, "#cdeccd", GREEN, 1.2) + text(365, 250, "↑ канал відчиняється полем ↑", 9.5, GREEN, "middle", "bold")
    s += line(365, 140, 365, 164, INK, 2) + text(365, 132, "+U", 11, RED, "middle", "bold")
    for x in (320, 365, 410):
        s += arrow(x, 186, x, 208, BLUE, 1.7, "3 2")
    s += text(118, 176, "M", 15, GREY, "middle", "bold")
    s += text(118, 202, "O", 15, SUN, "middle", "bold")
    s += text(118, 255, "S", 15, BLUE, "middle", "bold")
    s += text(W / 2, H - 10, "Поле металевого затвора крізь тонке скло притягує носії й відчиняє канал «джерело → стік» — без струму в затвор.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-0-5-first-mosfet.svg", s)


# ── Рис. 12.0.6 — спадок і еміграція ─────────────────────────────────────────
def fig_t6_legacy():
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 30, "Один прилад, зібраний усім світом", 16, INK, "middle", "bold")
    cards = [
        (40, "Львів", "ідея", "Лілієнфельд"),
        (240, "Єгипет", "матеріал (SiO₂)", "Аталла"),
        (440, "Корея", "втілення", "Кан"),
    ]
    cw = 170
    for cx0, place, role, who in cards:
        s += rect(cx0, 64, cw, 78, "#fdf1dc", "#d8b46a", 1.6, 8)
        s += text(cx0 + cw / 2, 88, place, 13, INK, "middle", "bold")
        s += text(cx0 + cw / 2, 110, role, 11, RED, "middle", "bold")
        s += text(cx0 + cw / 2, 130, who, 10.5, INK, "middle")
        s += arrow(cx0 + cw / 2, 144, W / 2, 194, GREY, 1.8)
    s += rect(W / 2 - 110, 196, 220, 46, LGRN, GREEN, 1.8, 8) + text(W / 2, 225, "MOSFET", 18, GREEN, "middle", "bold")
    s += rect(W / 2 - 300, 258, 600, 48, "#eef2f6", "#c9d3dc", 1.3, 8)
    s += text(W / 2, 278, "≈ 13 секстильйонів штук — найпоширеніший прилад в історії", 11.5, INK, "middle", "bold")
    s += text(W / 2, 296, "основа всієї цифрової техніки через КМОН-логіку", 10.5, GREY, "middle")
    save("fig-12-0-6-legacy.svg", s)


# ── Рис. 12.1.1 — струм vs поле ──────────────────────────────────────────────
def fig121_current_vs_field():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Дві педалі: струм керує струмом / поле керує струмом", 15, INK, "middle", "bold")
    s += _frame(40, 52, 300, 238, "біполярний — керує СТРУМ")
    s += _bjt_sym(170, 170, True)
    s += arrow(96, 170, 122, 170, GREEN, 2.4) + text(94, 158, "Ib", 11, GREEN, "end", "bold")
    s += text(150, 250, "малий струм бази", 9.5, GREEN, "middle", "bold")
    s += line(200, 114, 200, 94, INK, 2) + text(200, 86, "+V", 10, RED, "middle", "bold")
    s += arrow(200, 94, 200, 112, RED, 3) + text(248, 150, "Ic", 12, RED, "start", "bold")
    s += text(150, 272, "тече весь час, поки відкрито", 9, INK, "middle")
    s += _frame(380, 52, 300, 238, "польовий — керує ПОЛЕ")
    s += _mosfet_sym(520, 170)
    s += text(450, 158, "Vgs", 11, GREEN, "end", "bold") + arrow(452, 170, 474, 170, GREEN, 2.0, "3 2")
    s += text(500, 250, "напруга, струм ≈ 0", 9.5, GREEN, "middle", "bold")
    s += line(544, 126, 544, 96, INK, 2) + text(544, 88, "+V", 10, RED, "middle", "bold")
    s += arrow(544, 96, 544, 124, RED, 3) + text(580, 150, "ID", 12, RED, "start", "bold")
    s += text(500, 272, "тримати — задарма", 9, INK, "middle")
    save("fig-12-1-1-current-vs-field.svg", s)


# ── Рис. 12.1.2 — аналогія крана ─────────────────────────────────────────────
def fig121_valve_analogy():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Кран, що його тримає рука — і кран, що його тримає поле", 14.5, INK, "middle", "bold")

    def panel(ox, hand):
        t = _frame(ox, 52, 300, 240, "тримають рукою (струм)" if hand else "тримає поле (задарма)")
        t += line(ox + 20, 210, ox + 280, 210, "#9bb0c2", 2)
        t += line(ox + 20, 250, ox + 280, 250, "#9bb0c2", 2)
        t += arrow(ox + 40, 230, ox + 118, 230, BLUE, 3) + text(ox + 80, 224, "струм", 9, BLUE, "middle", "bold")
        t += arrow(ox + 190, 230, ox + 270, 230, BLUE, 3)
        t += line(ox + 150, 190, ox + 150, 210, INK, 4)
        t += rect(ox + 138, 178, 24, 12, "#cfd6dd", INK, 1.4)
        if hand:
            t += line(ox + 150, 178, ox + 150, 122, INK, 2)
            t += circle(ox + 150, 113, 12, "#f3e3c8", COPP, 2) + text(ox + 150, 117, "рука", 7.5, INK, "middle")
            t += arrow(ox + 182, 150, ox + 182, 122, RED, 2.2) + text(ox + 198, 140, "тягне", 9, RED, "start", "bold")
            t += text(ox + 150, 285, "відпустив — зачинився", 9.5, RED, "middle", "bold")
        else:
            for i in range(5):
                t += text(ox + 118 + i * 16, 116, "+", 12, RED, "middle", "bold")
            t += rect(ox + 110, 122, 80, 14, "#f3e3c8", COPP, 1.4) + text(ox + 150, 133, "затвор", 8, INK, "middle")
            for i in range(3):
                t += arrow(ox + 130 + i * 20, 138, ox + 130 + i * 20, 176, BLUE, 1.6, "3 2")
            t += text(ox + 150, 285, "поле тримає само — задарма", 9.5, GREEN, "middle", "bold")
        return t

    s += panel(40, True)
    s += panel(380, False)
    s += text(W / 2, H - 8, "Біполярним крути весь час (струм); польовий постав полем — і він тримається сам.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-1-2-valve-analogy.svg", s)


# ── Рис. 12.1.3 — три виводи ─────────────────────────────────────────────────
def fig121_three_terminals():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Три виводи: затвор керує каналом «витік → стік»", 15, INK, "middle", "bold")
    s += _frame(40, 52, 360, 238, "польовий транзистор")
    s += _mosfet_sym(180, 170)
    s += text(122, 174, "затвор G", 10.5, GREEN, "end", "bold")
    s += line(204, 126, 250, 126, INK, 1.8) + text(256, 130, "стік D", 10, INK, "start", "bold")
    s += line(204, 214, 250, 214, INK, 1.8) + text(256, 218, "витік S", 10, INK, "start", "bold")
    s += arrow(300, 138, 300, 202, RED, 2.6) + text(316, 174, "струм", 9.5, RED, "start", "bold")
    s += text(170, 252, "Vgs керує, струму в затвор ≈ 0", 9.5, GREEN, "middle", "bold")
    s += _frame(420, 52, 260, 238, "відповідність до BJT")
    pairs = [("затвор G", "база"), ("стік D", "колектор"), ("витік S", "емітер")]
    y = 96
    for a, b in pairs:
        s += rect(436, y, 110, 34, LBLUE, "#9bb0c2", 1.3) + text(491, y + 22, a, 10.5, INK, "middle", "bold")
        s += text(556, y + 23, "~", 14, GREY, "middle", "bold")
        s += rect(566, y, 100, 34, LRED, "#d8a0a0", 1.3) + text(616, y + 22, b, 10.5, INK, "middle")
        y += 50
    s += text(550, 260, "…але керування зовсім інше", 9.5, GREY, "middle", style="italic")
    save("fig-12-1-3-three-terminals.svg", s)


# ── Рис. 12.1.4 — затвор як конденсатор ──────────────────────────────────────
def fig121_gate_capacitor():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Затвор + канал = конденсатор (між ними ізолятор)", 15, INK, "middle", "bold")
    s += rect(210, 90, 300, 26, "#cfd6dd", INK, 1.8) + text(360, 107, "затвор (метал)", 10.5, INK, "middle", "bold")
    for i in range(7):
        s += text(240 + i * 40, 84, "+", 12, RED, "middle", "bold")
    s += rect(210, 120, 300, 16, "#fff3b0", SUN, 1.6) + text(360, 132, "ізолятор (скло)", 9, INK, "middle")
    for i in range(6):
        s += arrow(250 + i * 38, 116, 250 + i * 38, 152, BLUE, 1.7)
    s += rect(210, 140, 300, 40, "#e3edfb", INK, 1.8) + text(360, 196, "канал (напівпровідник)", 10.5, INK, "middle")
    for i in range(9):
        cx0 = 240 + i * 32
        s += circle(cx0, 160, 6, "#dfe7f0", BLUE, 1.4) + line(cx0 - 3, 160, cx0 + 3, 160, BLUE, 1.5)
    s += text(360, 232, "поле згущує носії → канал відкривається", 10, GREEN, "middle", "bold")
    s += rect(140, 256, 440, 36, "#eef2f6", "#c9d3dc", 1.3, 6)
    s += text(360, 279, "заряджений конденсатор у спокої струму НЕ тече → затвор нічого не споживає", 9.5, INK, "middle", "bold")
    save("fig-12-1-4-gate-capacitor.svg", s)


# ── Рис. 12.1.5 — у затвор струм не тече ─────────────────────────────────────
def fig121_no_gate_current():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Той самий ключ на 1 А: ціна керування", 15, INK, "middle", "bold")
    s += _frame(40, 52, 300, 238, "біполярний")
    s += _bjt_sym(160, 165, True)
    s += arrow(86, 165, 116, 165, RED, 2.6) + text(150, 150, "Ib = 10 мА", 11, RED, "middle", "bold")
    s += text(150, 235, "весь час у базу!", 10, RED, "middle", "bold")
    s += text(150, 262, "Rвх: сотні Ом", 10, INK, "middle")
    s += text(150, 282, "(вантажить джерело)", 8.5, GREY, "middle")
    s += _frame(380, 52, 300, 238, "польовий")
    s += _mosfet_sym(500, 165)
    s += text(440, 150, "струм затвора ≈ 0", 10.5, GREEN, "middle", "bold")
    s += arrow(428, 165, 452, 165, GREEN, 2.0, "3 2")
    s += text(500, 235, "постав напругу — і все", 10, GREEN, "middle", "bold")
    s += text(500, 262, "Rвх: трильйони Ом", 10, INK, "middle")
    s += text(500, 282, "(майже не вантажить)", 8.5, GREY, "middle")
    save("fig-12-1-5-no-gate-current.svg", s)


# ── Рис. 12.1.6 — чому це змінює все ─────────────────────────────────────────
def fig121_why_it_matters():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Чому «керування полем» змінило все", 16, INK, "middle", "bold")
    cards = [
        ("майже 0 Вт", ["на керування", "в спокої"]),
        ("Rвх велетенський", ["не вантажить", "джерело сигналу"]),
        ("мільярди на чипі", ["бо в спокої не", "тягнуть струму"]),
    ]
    cw, gap = 200, 28
    for i, (head, lines) in enumerate(cards):
        x = 40 + i * (cw + gap)
        s += rect(x, 64, cw, 110, LGRN, GREEN, 1.6, 8)
        s += text(x + cw / 2, 96, head, 13, GREEN, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(x + cw / 2, 124 + k * 22, ln, 10.5, INK, "middle")
    s += arrow(W / 2, 184, W / 2, 214, GREY, 2.4)
    s += rect(W / 2 - 220, 216, 440, 44, "#eef2f6", "#c9d3dc", 1.3, 8)
    s += text(W / 2, 236, "цифрова епоха: мільярди ключів у процесорі", 11.5, INK, "middle", "bold")
    s += text(W / 2, 253, "(КМОН-логіка — §12.9)", 10, GREY, "middle")
    save("fig-12-1-6-why-it-matters.svg", s)


# ── Рис. 12.2.1 — розріз MOSFET ──────────────────────────────────────────────
def fig122_cross_section():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 28, "Розріз n-канального MOSFET", 16, INK, "middle", "bold")
    s += rect(120, 206, 480, 118, "#eaf0e8", INK, 1.8) + text(360, 300, "p-підкладка (тіло)", 12, INK, "middle", "bold")
    s += rect(140, 206, 120, 46, "#cfd9ea", BLUE, 1.6) + text(200, 233, "витік n⁺", 10, INK, "middle", "bold")
    s += rect(460, 206, 120, 46, "#cfd9ea", BLUE, 1.6) + text(520, 233, "стік n⁺", 10, INK, "middle", "bold")
    s += rect(260, 206, 200, 10, "#f6f0d0", "#d8b46a", 1.2)
    s += text(360, 246, "канал тут наводить поле", 9, "#9a7b2e", "middle", "bold")
    s += rect(262, 190, 196, 14, "#fff3b0", SUN, 1.6) + text(360, 201, "оксид SiO₂", 8.5, INK, "middle", "bold")
    s += rect(272, 164, 176, 24, "#cfd6dd", INK, 1.6) + text(360, 180, "затвор", 10, INK, "middle", "bold")
    s += line(360, 140, 360, 164, INK, 2) + text(360, 132, "G (затвор)", 10, INK, "middle", "bold")
    s += line(200, 206, 200, 150, INK, 1.6) + line(200, 150, 150, 150, INK, 1.6) + text(146, 154, "S", 11, INK, "end", "bold")
    s += line(520, 206, 520, 150, INK, 1.6) + line(520, 150, 580, 150, INK, 1.6) + text(584, 154, "D", 11, INK, "start", "bold")
    s += line(360, 324, 360, 344, INK, 1.6) + text(360, 357, "B (підкладка)", 10, INK, "middle", "bold")
    save("fig-12-2-1-cross-section.svg", s)


# ── Рис. 12.2.2 — стовпчик M-O-S ─────────────────────────────────────────────
def fig122_mos_stack():
    W, H = 600, 330
    s = header(W, H)
    s += text(W / 2, 30, "Серцевина — стовпчик M-O-S = конденсатор", 15, INK, "middle", "bold")
    cx = 300
    s += rect(cx - 130, 80, 260, 46, "#cfd6dd", INK, 1.8) + text(cx, 108, "M — метал (затвор)", 12, INK, "middle", "bold")
    for i in range(7):
        s += text(cx - 110 + i * 36, 74, "+", 12, RED, "middle", "bold")
    s += rect(cx - 130, 130, 260, 18, "#fff3b0", SUN, 1.8) + text(cx, 143, "O — оксид (тонке скло)", 10, INK, "middle", "bold")
    for i in range(6):
        s += arrow(cx - 100 + i * 40, 126, cx - 100 + i * 40, 164, BLUE, 1.8)
    s += rect(cx - 130, 152, 260, 70, "#e3edfb", INK, 1.8) + text(cx, 210, "S — напівпровідник (Si)", 12, INK, "middle", "bold")
    for i in range(7):
        x0 = cx - 108 + i * 36
        s += circle(x0, 172, 6, "#dfe7f0", BLUE, 1.4) + line(x0 - 3, 172, x0 + 3, 172, BLUE, 1.5)
    s += text(cx, 256, "= конденсатор: 2 обкладки + діелектрик", 11.5, GREEN, "middle", "bold")
    s += text(cx, 282, "у спокої струму не тече; поле керує каналом", 10, GREY, "middle", style="italic")
    save("fig-12-2-2-mos-stack.svg", s)


# ── Рис. 12.2.3 — стан «вимкнено» ────────────────────────────────────────────
def fig122_off_state():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Без затвора: n–p–n = два зустрічні діоди → струм перекрито", 14, INK, "middle", "bold")
    s += rect(120, 150, 480, 90, "#eaf0e8", INK, 1.8) + text(360, 224, "p", 13, INK, "middle", "bold")
    s += rect(140, 150, 120, 46, "#cfd9ea", BLUE, 1.6) + text(200, 178, "n⁺ витік", 10, INK, "middle", "bold")
    s += rect(460, 150, 120, 46, "#cfd9ea", BLUE, 1.6) + text(520, 178, "n⁺ стік", 10, INK, "middle", "bold")
    s += line(260, 150, 260, 196, RED, 2.4) + text(285, 142, "перехід 1", 8.5, RED, "middle")
    s += line(460, 150, 460, 196, RED, 2.4) + text(435, 142, "перехід 2", 8.5, RED, "middle")
    s += text(360, 268, "еквівалент:", 10, INK, "middle", "bold")
    s += line(250, 292, 300, 292, INK, 2)
    s += _diode_h(312, 292, 12, True, INK)
    s += line(324, 292, 396, 292, INK, 2)
    s += _diode_h(408, 292, 12, False, INK)
    s += line(420, 292, 470, 292, INK, 2)
    s += text(232, 296, "S", 10, INK, "end", "bold") + text(488, 296, "D", 10, INK, "start", "bold")
    s += text(360, 316, "хоч куди прикладай — один діод завжди зворотний", 9, GREY, "middle", style="italic")
    save("fig-12-2-3-off-state.svg", s)


# ── Рис. 12.2.4 — тонкий оксид ───────────────────────────────────────────────
def fig122_thin_oxide():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Чому оксид надтонкий: E = U / d", 16, INK, "middle", "bold")
    s += rect(180, 90, 360, 30, "#cfd6dd", INK, 1.8) + text(360, 110, "затвор", 11, INK, "middle", "bold")
    s += rect(180, 124, 360, 16, "#fff3b0", SUN, 1.8)
    s += rect(180, 144, 360, 40, "#e3edfb", INK, 1.8) + text(360, 170, "канал (Si)", 11, INK, "middle")
    s += line(560, 124, 560, 140, INK, 1.4)
    s += arrow(560, 132, 560, 123, INK, 1.4) + arrow(560, 132, 560, 141, INK, 1.4)
    s += text(575, 137, "d ≈ 5 нм", 10, INK, "start", "bold")
    s += text(168, 110, "U", 12, RED, "end", "bold") + text(168, 168, "0", 11, INK, "end")
    s += rect(120, 210, 480, 70, LGRN, GREEN, 1.5, 8)
    s += text(360, 238, "E = U / d = 3 В / 5 нм ≈ 600 МВ/м", 15, GREEN, "middle", "bold")
    s += text(360, 264, "тонкий шар → величезне поле за скромної напруги", 10.5, INK, "middle")
    save("fig-12-2-4-thin-oxide.svg", s)


# ── Рис. 12.2.5 — чотири виводи + вбудований діод ────────────────────────────
def fig122_four_terminals():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Чотири виводи; тіло з'єднують із витоком", 15, INK, "middle", "bold")
    s += _mosfet_sym(250, 150)
    s += text(190, 154, "затвор G", 10, GREEN, "end", "bold")
    s += line(274, 106, 340, 106, INK, 1.8) + text(346, 110, "стік D", 10.5, INK, "start", "bold")
    s += line(274, 194, 340, 194, INK, 1.8) + text(346, 198, "витік S", 10.5, INK, "start", "bold")
    s += text(250, 238, "тіло (B) → з'єднане з витоком", 10, GREEN, "middle", "bold")
    bx = 540
    s += rect(bx - 120, 70, 240, 168, "#fbfbfb", "#d8a0a0", 1.4, 8)
    s += text(bx, 92, "вбудований діод", 11, RED, "middle", "bold")
    s += text(bx, 110, "тіло(p) – стік(n⁺)", 9, GREY, "middle")
    s += line(bx, 210, bx, 178, INK, 2) + text(bx, 224, "витік / тіло", 8.5, INK, "middle")
    s += f'<path d="M {bx-12},178 L {bx+12},178 L {bx},158 Z" fill="#fbecec" stroke="{RED}" stroke-width="1.6"/>\n'
    s += line(bx - 12, 154, bx + 12, 154, RED, 2.6)
    s += line(bx, 154, bx, 132, INK, 2) + text(bx, 126, "стік", 8.5, INK, "middle")
    save("fig-12-2-5-four-terminals.svg", s)


# ── Рис. 12.2.6 — планарний процес ───────────────────────────────────────────
def fig122_planar():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "MOSFET не збирають — його друкують шарами на пластині", 14.5, INK, "middle", "bold")
    s += circle(170, 165, 95, "#eef2f6", GREY, 2)
    for r in range(6):
        for c in range(6):
            x = 110 + c * 24
            y = 105 + r * 24
            if (x + 9 - 170) ** 2 + (y + 9 - 165) ** 2 < 84 * 84:
                s += rect(x, y, 18, 18, "#e3edfb", "#9bb0c2", 1)
    s += text(170, 282, "пластина: мільйони чипів відразу", 10, INK, "middle")
    s += line(258, 140, 360, 108, GREY, 1, "3 3") + line(258, 190, 360, 252, GREY, 1, "3 3")
    s += rect(360, 100, 320, 158, "#ffffff", "#c9d3dc", 1.4, 8)
    s += text(520, 120, "один транзистор = кілька плоских шарів", 10.5, INK, "middle", "bold")
    s += rect(420, 134, 200, 22, "#cfd6dd", INK, 1.4) + text(520, 149, "затвор", 9, INK, "middle")
    s += rect(420, 156, 200, 12, "#fff3b0", SUN, 1.4) + text(520, 166, "оксид", 8, INK, "middle")
    s += rect(420, 168, 200, 40, "#eaf0e8", INK, 1.4) + text(520, 192, "кремній (з n⁺ ділянками)", 9, INK, "middle")
    s += text(520, 230, "наносять і витравлюють, як друк", 9.5, GREEN, "middle", "bold")
    s += text(520, 248, "→ мільярди на чипі", 10, GREEN, "middle", "bold")
    save("fig-12-2-6-planar.svg", s)


# ── Рис. 12.3.1 — три стадії ─────────────────────────────────────────────────
def fig123_three_stages():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 28, "Як росте напруга затвора: нема каналу → збіднення → інверсія", 15, INK, "middle", "bold")

    def panel(ox, title, gate_lbl, stage):
        t = text(ox + 130, 54, title, 12, INK, "middle", "bold")
        t += rect(ox + 20, 150, 220, 78, "#eaf0e8", INK, 1.5)
        t += rect(ox + 28, 150, 52, 30, "#cfd9ea", BLUE, 1.3) + text(ox + 54, 169, "n⁺", 9, INK, "middle", "bold")
        t += rect(ox + 180, 150, 52, 30, "#cfd9ea", BLUE, 1.3) + text(ox + 206, 169, "n⁺", 9, INK, "middle", "bold")
        t += rect(ox + 80, 138, 100, 8, "#fff3b0", SUN, 1.2)
        t += rect(ox + 88, 120, 84, 16, "#cfd6dd", INK, 1.3) + text(ox + 130, 132, "затвор " + gate_lbl, 8, INK, "middle", "bold")
        if stage == 0:
            for i in range(5):
                t += text(ox + 92 + i * 20, 166, "+", 11, RED, "middle", "bold")
            t += text(ox + 130, 248, "повно дірок — каналу нема", 8.5, INK, "middle")
        elif stage == 1:
            t += rect(ox + 80, 150, 100, 20, "#f3eef6", "#b9a0c8", 1.1)
            for i in range(5):
                t += text(ox + 92 + i * 20, 165, "–", 10, "#7a5b9a", "middle", "bold")
            t += text(ox + 130, 248, "дірки пішли — збіднення", 8.5, INK, "middle")
        else:
            t += rect(ox + 80, 150, 100, 10, "#cfe0f5", BLUE, 1.2)
            for i in range(7):
                cx0 = ox + 88 + i * 15
                t += circle(cx0, 155, 4, "#dfe7f0", BLUE, 1.2) + line(cx0 - 2, 155, cx0 + 2, 155, BLUE, 1.2)
            t += text(ox + 130, 248, "електронний канал — відкрито!", 8.5, GREEN, "middle", "bold")
        return t

    s += panel(20, "Vgs = 0", "0В", 0)
    s += panel(310, "мала Vgs (< Vth)", "+", 1)
    s += panel(600, "Vgs > Vth", "++", 2)
    s += text(W / 2, H - 12, "Поле спершу розчищає поверхню від дірок (збіднення), а далі стягує електрони й творить канал (інверсія).",
              10, GREY, "middle", style="italic")
    save("fig-12-3-1-three-stages.svg", s)


# ── Рис. 12.3.2 — інверсійний шар ────────────────────────────────────────────
def fig123_inversion_layer():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Інверсія: поле стягує електрони, p-поверхня стає n-каналом", 14.5, INK, "middle", "bold")
    s += rect(120, 170, 480, 110, "#eaf0e8", INK, 1.8) + text(360, 262, "p-підкладка (дірки в глибині)", 11, INK, "middle")
    s += rect(140, 170, 110, 40, "#cfd9ea", BLUE, 1.6) + text(195, 194, "n⁺ витік", 9.5, INK, "middle", "bold")
    s += rect(470, 170, 110, 40, "#cfd9ea", BLUE, 1.6) + text(525, 194, "n⁺ стік", 9.5, INK, "middle", "bold")
    s += rect(250, 150, 220, 12, "#fff3b0", SUN, 1.6) + text(360, 160, "оксид", 8, INK, "middle")
    s += rect(260, 120, 200, 24, "#cfd6dd", INK, 1.6) + text(360, 136, "затвор +", 10.5, INK, "middle", "bold")
    for i in range(7):
        s += text(280 + i * 28, 114, "+", 12, RED, "middle", "bold")
    for i in range(6):
        s += arrow(285 + i * 32, 148, 285 + i * 32, 172, BLUE, 1.6)
    s += rect(250, 170, 220, 12, "#cfe0f5", BLUE, 1.6)
    for i in range(11):
        cx0 = 262 + i * 18
        s += circle(cx0, 176, 4.5, "#dfe7f0", BLUE, 1.3) + line(cx0 - 2.3, 176, cx0 + 2.3, 176, BLUE, 1.3)
    s += text(360, 202, "інверсійний шар = канал (місток витік→стік)", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Електрони, стягнуті полем до поверхні, утворюють тонкий n-шар, що сполучає два n⁺-береги. Це і є канал.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-3-2-inversion-layer.svg", s)


# ── Рис. 12.3.3 — передатна крива ────────────────────────────────────────────
def fig123_threshold_transfer():
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 28, "Передатна крива: струм стоку від напруги затвора", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 110, 250, 420, 180
    s += _axes(ox, oy, ww, hh, "Vgs", "ID")
    vth_x = ox + 150
    pts = []
    for j in range(0, 421, 6):
        x = ox + j
        if x < vth_x:
            y = oy - 2
        else:
            f = (x - vth_x) / (ox + ww - vth_x)
            y = oy - 2 - (hh - 20) * f * f
        pts.append((x, y))
    s += _poly(pts, RED, 2.6)
    s += line(vth_x, oy, vth_x, oy - hh - 6, GREY, 1.3, "4 3")
    s += text(vth_x, oy + 20, "Vth", 11, INK, "middle", "bold")
    s += text(ox + 60, oy + 20, "закрито", 10, BLUE, "middle", "bold")
    s += text(ox + 330, oy + 20, "відкрито", 10, GREEN, "middle", "bold")
    s += text(ox + 340, oy - 128, "струм швидко росте", 9.5, RED, "middle")
    s += text(vth_x - 6, oy - 16, "трохи нижче — підпороговий хвіст", 8, GREY, "end", style="italic")
    save("fig-12-3-3-threshold-transfer.svg", s)


# ── Рис. 12.3.4 — перевищення порогу ─────────────────────────────────────────
def fig123_overdrive():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 28, "Перевищення порогу (Vgs − Vth) керує товщиною каналу", 14.5, INK, "middle", "bold")
    panels = [("трохи > Vth", 5, "великий опір", RED), ("помірно", 11, "середній", SUN), ("значно > Vth", 18, "малий опір", GREEN)]
    for i, (title, th, rlab, col) in enumerate(panels):
        ox = 30 + i * 245
        s += text(ox + 110, 58, title, 11.5, INK, "middle", "bold")
        s += rect(ox + 10, 150, 200, 70, "#eaf0e8", INK, 1.5)
        s += rect(ox + 10, 132, 200, 8, "#fff3b0", SUN, 1.2)
        s += rect(ox + 30, 116, 160, 14, "#cfd6dd", INK, 1.3) + text(ox + 110, 127, "затвор", 8.5, INK, "middle")
        s += rect(ox + 10, 150, 200, th, "#cfe0f5", BLUE, 1.3)
        s += text(ox + 110, 150 + th + 22, "канал", 9, BLUE, "middle", "bold")
        s += rect(ox + 60, 244, 100, 28, "#ffffff", col, 1.5, 6) + text(ox + 110, 262, rlab, 9.5, col, "middle", "bold")
    s += text(W / 2, H - 6, "Більше перевищення → густіший електронний шар → менший опір каналу.", 10, GREY, "middle", style="italic")
    save("fig-12-3-4-overdrive.svg", s)


# ── Рис. 12.3.5 — логічного рівня vs звичайний ───────────────────────────────
def fig123_logic_level():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Та сама напруга 5 В: логічного рівня vs звичайний", 15, INK, "middle", "bold")

    def panel(ox, title, vth, over, th, rlab, col, hot):
        t = _frame(ox, 52, 300, 238, title)
        t += text(ox + 150, 84, "Vgs = 5 В,  Vth = %s В" % vth, 11, INK, "middle", "bold")
        t += text(ox + 150, 104, "перевищення = %s В" % over, 10.5, col, "middle", "bold")
        t += rect(ox + 60, 150, 180, 60, "#eaf0e8", INK, 1.5)
        t += rect(ox + 60, 134, 180, 8, "#fff3b0", SUN, 1.2)
        t += rect(ox + 80, 120, 140, 12, "#cfd6dd", INK, 1.3) + text(ox + 150, 130, "затвор 5В", 8, INK, "middle")
        t += rect(ox + 60, 150, 180, th, "#cfe0f5", BLUE, 1.3)
        t += text(ox + 150, 232, rlab, 10.5, col, "middle", "bold")
        t += text(ox + 150, 256, ("гріється" if hot else "холодний"), 10, col, "middle", "bold")
        return t

    s += panel(40, "логічного рівня", "1.5", "3.5", 16, "канал налитий → малий R", GREEN, False)
    s += panel(380, "звичайний", "4", "1", 4, "канал ледь живий → великий R", RED, True)
    s += text(W / 2, H - 8, "Звіряй потрібну Vgs (і криву Rds(on)–Vgs) з тим, що дає твоє керування.", 9.5, GREY, "middle", style="italic")
    save("fig-12-3-5-logic-level.svg", s)


# ── Рис. 12.3.6 — гребля-поріг ───────────────────────────────────────────────
def fig123_dam_analogy():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Поріг як гребля: рівень води (Vgs) проти гребеня (Vth)", 14.5, INK, "middle", "bold")

    def panel(ox, title, flows):
        t = _frame(ox, 52, 300, 220, title)
        ground = 244
        crest = 150
        dl = ox + 145
        dr = ox + 155
        t += line(ox + 24, crest, ox + 276, crest, GREY, 1, "5 3") + text(ox + 276, crest - 3, "Vth", 9, GREY, "end", "bold")
        if not flows:
            t += rect(ox + 24, 178, dl - (ox + 24), ground - 178, "#cfe0f5", BLUE, 1)
            t += rect(dr, 228, (ox + 276) - dr, ground - 228, "#cfe0f5", BLUE, 1)
            t += text(ox + 84, 170, "рівень", 8.5, BLUE, "middle", "bold")
            t += text(ox + 150, 98, "нижче гребеня — нема потоку", 9.5, RED, "middle", "bold")
        else:
            t += rect(ox + 24, 128, dl - (ox + 24), ground - 128, "#cfe0f5", BLUE, 1)
            t += rect(dr, 196, (ox + 276) - dr, ground - 196, "#cfe0f5", BLUE, 1)
            t += arrow(ox + 138, 136, ox + 168, 150, BLUE, 2.4)
            t += text(ox + 150, 98, "перелився — тече", 9.5, GREEN, "middle", "bold")
        t += rect(dl, crest, dr - dl, ground - crest, "#cdbfa8", INK, 1.4)
        t += text(ox + 150, ground + 16, "гребля", 8.5, INK, "middle")
        return t

    s += panel(40, "Vgs < Vth — закрито", False)
    s += panel(380, "Vgs > Vth — відкрито", True)
    s += text(W / 2, H - 8, "Нижче гребеня потоку нема; вище — потекло, і що вищий рівень, то рясніший потік (менший опір).",
              9.5, GREY, "middle", style="italic")
    save("fig-12-3-6-dam-analogy.svg", s)


# ── Рис. 12.4.1 — будова NMOS vs PMOS ────────────────────────────────────────
def fig124_nmos_vs_pmos_structure():
    W, H = 860, 300
    s = header(W, H)
    s += text(W / 2, 28, "NMOS і PMOS у розрізі: усі типи дзеркально перевернуті", 15, INK, "middle", "bold")

    def cross(ox, title, sub_lbl, sub_fill, sd_lbl, sd_fill, gate_sign, chan_fill, chan_sign, chan_col, chan_note):
        t = text(ox + 180, 56, title, 13, INK, "middle", "bold")
        t += rect(ox + 20, 150, 320, 90, sub_fill, INK, 1.7) + text(ox + 180, 224, sub_lbl, 11, INK, "middle", "bold")
        t += rect(ox + 32, 150, 80, 34, sd_fill, INK, 1.4) + text(ox + 72, 171, sd_lbl, 9.5, INK, "middle", "bold")
        t += rect(ox + 248, 150, 80, 34, sd_fill, INK, 1.4) + text(ox + 288, 171, sd_lbl, 9.5, INK, "middle", "bold")
        t += rect(ox + 112, 138, 136, 8, "#fff3b0", SUN, 1.2)
        t += rect(ox + 124, 118, 112, 16, "#cfd6dd", INK, 1.4) + text(ox + 180, 130, "затвор " + gate_sign, 9, INK, "middle", "bold")
        t += rect(ox + 112, 150, 136, 10, chan_fill, chan_col, 1.3)
        for i in range(7):
            t += text(ox + 122 + i * 18, 159, chan_sign, 9, chan_col, "middle", "bold")
        t += text(ox + 180, 256, chan_note, 9.5, chan_col, "middle", "bold")
        return t

    s += cross(20, "NMOS", "p-підкладка", "#eaf0e8", "n⁺", "#cfd9ea", "+", "#cfe0f5", "–", BLUE, "канал з електронів")
    s += cross(460, "PMOS", "n-підкладка", "#eef1f8", "p⁺", "#f3e2e2", "–", "#fbeaea", "+", RED, "канал із дірок")
    s += text(W / 2, H - 12, "Однакова будова — протилежні знаки: p↔n, електрони↔дірки, + затвор ↔ − затвор.",
              10, GREY, "middle", style="italic")
    save("fig-12-4-1-nmos-vs-pmos-structure.svg", s)


# ── Рис. 12.4.2 — полярність вмикання ────────────────────────────────────────
def fig124_turn_on_polarity():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Полярність вмикання: NMOS — затвор угору, PMOS — униз", 14.5, INK, "middle", "bold")
    s += _frame(40, 52, 300, 220, "NMOS — вмикає додатна Vgs")
    s += _mosfet_sym(170, 150, False)
    s += text(118, 154, "затвор", 9.5, GREEN, "end", "bold")
    s += arrow(210, 250, 210, 206, GREEN, 2.4) + text(228, 234, "Vgs > 0", 11, GREEN, "start", "bold")
    s += text(190, 266, "затвор ВИЩЕ за витік", 9, INK, "middle")
    s += _frame(380, 52, 300, 220, "PMOS — вмикає від'ємна Vgs")
    s += _mosfet_sym(510, 150, True)
    s += text(458, 154, "затвор", 9.5, BLUE, "end", "bold")
    s += arrow(550, 206, 550, 250, BLUE, 2.4) + text(568, 234, "Vgs < 0", 11, BLUE, "start", "bold")
    s += text(530, 266, "затвор НИЖЧЕ за витік", 9, INK, "middle")
    s += text(W / 2, H - 6, "NMOS вмикають, піднімаючи напругу затвора; PMOS — опускаючи.", 9.5, GREY, "middle", style="italic")
    save("fig-12-4-2-turn-on-polarity.svg", s)


# ── Рис. 12.4.3 — символи ────────────────────────────────────────────────────
def fig124_symbols():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Умовні позначення NMOS і PMOS", 15, INK, "middle", "bold")
    s += _frame(40, 52, 300, 220, "NMOS (стрілка всередину)")
    s += _mosfet_sym(170, 150, False)
    s += line(194, 106, 250, 106, INK, 1.6) + text(256, 110, "стік D", 9.5, INK, "start", "bold")
    s += line(194, 194, 250, 194, INK, 1.6) + text(256, 198, "витік S", 9.5, INK, "start", "bold")
    s += text(118, 154, "затвор G", 9.5, INK, "end", "bold")
    s += text(170, 252, "типово знизу (S → земля)", 9, GREEN, "middle", "bold")
    s += _frame(380, 52, 300, 220, "PMOS (стрілка назовні)")
    s += _mosfet_sym(510, 150, True)
    s += line(534, 106, 590, 106, INK, 1.6) + text(596, 110, "стік D", 9.5, INK, "start", "bold")
    s += line(534, 194, 590, 194, INK, 1.6) + text(596, 198, "витік S", 9.5, INK, "start", "bold")
    s += text(458, 154, "затвор G", 9.5, INK, "end", "bold")
    s += text(510, 252, "типово згори (S → +V)", 9, BLUE, "middle", "bold")
    s += text(W / 2, H - 6, "Стрілка показує напрям p-n переходу підкладки — як у діода.", 9.5, GREY, "middle", style="italic")
    save("fig-12-4-3-symbols.svg", s)


# ── Рис. 12.4.4 — рухливість ─────────────────────────────────────────────────
def fig124_mobility():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Електрони прудкіші за дірки (~×3) → NMOS проводить краще", 14, INK, "middle", "bold")
    base = 232
    s += rect(140, base - 150, 90, 150, "#cfe0f5", BLUE, 1.5) + text(185, base - 160, "електрони", 11, BLUE, "middle", "bold")
    s += text(185, base + 20, "~1400", 11, INK, "middle", "bold") + text(185, base + 36, "(NMOS)", 9, GREY, "middle")
    s += rect(330, base - 50, 90, 50, "#fbeaea", RED, 1.5) + text(375, base - 60, "дірки", 11, RED, "middle", "bold")
    s += text(375, base + 20, "~470", 11, INK, "middle", "bold") + text(375, base + 36, "(PMOS)", 9, GREY, "middle")
    s += text(280, base - 110, "рухливість, см²/(В·с)", 9.5, GREY, "middle", style="italic")
    s += rect(480, 70, 210, 156, "#eef2f6", "#c9d3dc", 1.3, 8)
    s += text(585, 96, "наслідок:", 11, INK, "middle", "bold")
    s += text(585, 120, "n-канал — менший опір", 10, INK, "middle")
    s += text(585, 138, "на ту саму площу", 10, INK, "middle")
    s += text(585, 168, "PMOS роблять у 2–3×", 9.5, RED, "middle", "bold")
    s += text(585, 186, "більшим, щоб зрівняти", 9.5, RED, "middle")
    s += text(585, 212, "→ силові ключі: n-канал", 9.5, GREEN, "middle", "bold")
    save("fig-12-4-4-mobility.svg", s)


# ── Рис. 12.4.5 — сильний/кволий бік ─────────────────────────────────────────
def fig124_strong_weak():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Кожен сильний у свій бік", 15.5, INK, "middle", "bold")
    s += _frame(40, 52, 300, 220, "NMOS")
    s += line(70, 96, 310, 96, RED, 1.4) + text(70, 90, "+V", 8.5, RED, "start", "bold")
    s += line(70, 244, 310, 244, INK, 1.4) + text(70, 258, "земля", 8.5, INK, "start")
    s += text(190, 130, "кволий «1»", 9.5, RED, "middle") + text(190, 146, "(застрягає на +V−Vth)", 8, GREY, "middle")
    s += arrow(190, 170, 190, 236, GREEN, 3) + text(206, 210, "сильний «0»", 10, GREEN, "start", "bold")
    s += _frame(380, 52, 300, 220, "PMOS")
    s += line(410, 96, 650, 96, RED, 1.4) + text(410, 90, "+V", 8.5, RED, "start", "bold")
    s += line(410, 244, 650, 244, INK, 1.4) + text(410, 258, "земля", 8.5, INK, "start")
    s += arrow(530, 230, 530, 110, GREEN, 3) + text(546, 180, "сильна «1»", 10, GREEN, "start", "bold")
    s += text(530, 224, "кволий «0»", 9.5, RED, "middle")
    s += text(W / 2, H - 6, "NMOS добре садить до землі, PMOS добре тягне до +V — тому кожен у свій бік.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-4-5-strong-weak.svg", s)


# ── Рис. 12.4.6 — комплементарна пара ────────────────────────────────────────
def fig124_complementary():
    W, H = 600, 350
    s = header(W, H)
    s += text(W / 2, 30, "Комплементарна пара: PMOS угорі, NMOS унизу", 14.5, INK, "middle", "bold")
    cx = 300
    s += line(150, 70, 450, 70, RED, 2) + text(144, 74, "+V", 11, RED, "end", "bold")
    s += line(150, 300, 450, 300, INK, 1.6) + text(144, 304, "GND", 10, INK, "end", "bold")
    s += rect(cx - 55, 96, 110, 56, "#f3e2e2", RED, 1.6, 6) + text(cx, 120, "PMOS", 12, RED, "middle", "bold")
    s += text(cx, 140, "тягне до +V", 8.5, INK, "middle")
    s += line(cx, 70, cx, 96, INK, 2)
    s += rect(cx - 55, 218, 110, 56, "#eaf0e8", GREEN, 1.6, 6) + text(cx, 242, "NMOS", 12, GREEN, "middle", "bold")
    s += text(cx, 262, "тягне до землі", 8.5, INK, "middle")
    s += line(cx, 274, cx, 300, INK, 2)
    s += line(cx, 152, cx, 218, INK, 2) + circle(cx, 185, 3, INK, INK)
    s += line(cx, 185, cx + 120, 185, INK, 2) + text(cx + 126, 189, "вихід", 10, INK, "start", "bold")
    s += line(cx - 55, 124, cx - 130, 124, INK, 1.6)
    s += line(cx - 55, 246, cx - 130, 246, INK, 1.6)
    s += line(cx - 130, 124, cx - 130, 246, INK, 1.6)
    s += line(cx - 130, 185, cx - 180, 185, INK, 2) + text(cx - 186, 189, "вхід", 10, INK, "end", "bold")
    s += text(W / 2, 334, "У кожному стані відкритий лише один із пари: вихід — чистий «0» або «1», без наскрізного струму.",
              9, GREY, "middle", style="italic")
    save("fig-12-4-6-complementary.svg", s)


# ── Рис. 12.5.1 — Rds(on) як резистор ────────────────────────────────────────
def fig125_on_resistance():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Відкритий MOSFET = маленький резистор Rds(on)", 15, INK, "middle", "bold")
    s += _mosfet_sym(160, 160)
    s += text(160, 232, "відкритий (Vgs > Vth)", 9.5, GREEN, "middle", "bold")
    s += text(106, 164, "G", 10, INK, "end", "bold")
    s += text(192, 118, "D", 10, INK, "start", "bold") + text(192, 210, "S", 10, INK, "start", "bold")
    s += text(286, 154, "≈", 20, GREY, "middle", "bold")
    s += text(470, 96, "D", 11, INK, "middle", "bold")
    s += line(470, 104, 470, 130, INK, 2)
    s += rect(444, 130, 52, 70, "#fff7e6", COPP, 1.8) + text(470, 170, "Rds(on)", 10, INK, "middle", "bold")
    s += line(470, 200, 470, 226, INK, 2) + text(470, 242, "S", 11, INK, "middle", "bold")
    s += arrow(545, 110, 545, 222, RED, 2.6) + text(561, 168, "Id", 11, RED, "start", "bold")
    s += text(410, 162, "Vds =", 10, INK, "end") + text(410, 179, "Id·Rds(on)", 9.5, INK, "end", "bold")
    s += text(W / 2, H - 12, "«Увімкнено» = через маленький резистор, а не ідеальне коротке. Весь струм навантаження тече крізь Rds(on).",
              9.5, GREY, "middle", style="italic")
    save("fig-12-5-1-on-resistance.svg", s)


# ── Рис. 12.5.2 — P = Id²·Rds(on) ────────────────────────────────────────────
def fig125_power_heat():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Грійка ключа: P = Id² · Rds(on)", 16, INK, "middle", "bold")
    s += rect(90, 66, 540, 64, LGRN, GREEN, 1.6, 8)
    s += text(360, 108, "P = Id² · Rds(on)", 23, GREEN, "middle", "bold")
    rows = [("Id = 10 А,   Rds(on) = 5 мОм", False),
            ("Vds = Id·Rds(on) = 10 · 0.005 = 0.05 В   (50 мВ)", False),
            ("P = Id²·Rds(on) = 100 · 0.005 = 0.5 Вт   (холодний)", True)]
    y = 168
    for r, b in rows:
        s += text(360, y, r, 13, INK if not b else GREEN, "middle", "bold" if b else "normal")
        y += 32
    s += text(W / 2, H - 12, "Менший Rds(on) → менший спад → менша грійка. Тому за нього й воюють виробники.",
              10, GREY, "middle", style="italic")
    save("fig-12-5-2-power-heat.svg", s)


# ── Рис. 12.5.3 — втрати BJT vs MOSFET ───────────────────────────────────────
def fig125_bjt_vs_mosfet_loss():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Втрати від струму: біполярний (лінійно) vs MOSFET (квадратично)", 13.5, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 270, 520, 200
    s += _axes(ox, oy, ww, hh, "Id", "P")
    xmax, ymax = 80.0, 24.0

    def X(i):
        return ox + (i / xmax) * ww

    def Y(p):
        return oy - (p / ymax) * hh

    s += _poly([(X(i), Y(0.3 * i)) for i in range(0, 81, 4)], RED, 2.6)
    s += _poly([(X(i), Y(0.005 * i * i)) for i in range(0, 70, 3)], BLUE, 2.6)
    s += circle(X(60), Y(18), 4, INK, INK) + line(X(60), oy, X(60), Y(18), GREY, 1, "4 3")
    s += text(X(60), oy + 18, "60 А", 10, INK, "middle", "bold")
    s += text(X(74), Y(0.3 * 74) - 4, "біполярний", 10, RED, "middle", "bold")
    s += text(X(48), Y(0.005 * 48 * 48) - 12, "MOSFET", 10, BLUE, "middle", "bold")
    s += text(X(26), oy - 26, "тут MOSFET холодніший", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "До ~60 А MOSFET виграє; квадрат Id² наздоганяє лише за дуже великих струмів.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-5-3-bjt-vs-mosfet-loss.svg", s)


# ── Рис. 12.5.4 — Rds(on) від Vgs ────────────────────────────────────────────
def fig125_overdrive_sets_r():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Rds(on) залежить від напруги затвора Vgs", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 250, 480, 180

    def Rn(f):
        return 0.08 + 0.92 * math.exp(-5.0 * f)

    s += _axes(ox, oy, ww, hh, "Vgs", "Rds(on)")
    s += _poly([(ox + (i / 80) * ww, oy - Rn(i / 80) * hh) for i in range(81)], BLUE, 2.6)
    for vg, lbl, col in [(5, "5 В (МК)", RED), (10, "10 В", GREEN)]:
        f = vg / 12.0
        x = ox + f * ww
        y = oy - Rn(f) * hh
        s += line(x, oy, x, y, GREY, 1, "4 3") + circle(x, y, 4, col, col)
        s += text(x, oy + 18, lbl, 9.5, col, "middle", "bold")
    s += text(ox + ww - 8, oy - Rn(0.95) * hh - 10, "полиця (мін. R)", 9, GREEN, "end")
    s += text(W / 2, H - 10, "Більше Vgs → товщий канал → менший Rds(on). Даташит дає мінімум при високій Vgs; при 5 В буде більше.",
              9, GREY, "middle", style="italic")
    save("fig-12-5-4-overdrive-sets-r.svg", s)


# ── Рис. 12.5.5 — компроміс площі й напруги ──────────────────────────────────
def fig125_voltage_tradeoff():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Що задає Rds(on): площа кремнію та клас напруги", 14.5, INK, "middle", "bold")
    s += rect(60, 78, 280, 150, "#eef6ef", GREEN, 1.5, 8)
    s += text(200, 104, "більша площа кремнію", 11, GREEN, "middle", "bold")
    s += text(200, 128, "= багато каналів паралельно", 9.5, INK, "middle")
    s += arrow(200, 146, 200, 186, GREEN, 2.6) + text(200, 208, "Rds(on) ↓", 13, GREEN, "middle", "bold")
    s += text(200, 224, "(але дорожче, більший корпус)", 8.5, GREY, "middle")
    s += rect(380, 78, 280, 150, "#fbeeee", RED, 1.5, 8)
    s += text(520, 104, "вищий клас напруги", 11, RED, "middle", "bold")
    s += text(520, 128, "= товста дрейфова область", 9.5, INK, "middle")
    s += arrow(520, 146, 520, 186, RED, 2.6) + text(520, 208, "Rds(on) ↑", 13, RED, "middle", "bold")
    s += text(520, 224, "(не бери надмірний запас!)", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Тому низькоомні MOSFET великі й дорогі, а високовольтні мають вищий опір. Бери напругу з розумним запасом.",
              9, GREY, "middle", style="italic")
    save("fig-12-5-5-voltage-tradeoff.svg", s)


# ── Рис. 12.5.6 — Rds(on) від температури ────────────────────────────────────
def fig125_temperature():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Rds(on) росте з температурою (≈ ×2 у спеку)", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 250, 480, 180
    s += _axes(ox, oy, ww, hh, "T, °C", "Rds(on)")

    def X(tc):
        return ox + (tc / 175.0) * ww

    def Y(r):
        return oy - (r / 2.4) * hh

    s += _poly([(X(tc), Y(1.0 + 0.008 * (tc - 25))) for tc in range(0, 176, 5)], RED, 2.6)
    for tc, rr in [(25, 1.0), (150, 2.0)]:
        s += circle(X(tc), Y(rr), 4, INK, INK) + line(X(tc), oy, X(tc), Y(rr), GREY, 1, "4 3")
    s += text(X(25), oy + 18, "25°", 9.5, INK, "middle", "bold") + text(X(150), oy + 18, "150°", 9.5, INK, "middle", "bold")
    s += text(X(25) - 6, Y(1.0) - 6, "×1", 9, INK, "end", "bold") + text(X(150) + 6, Y(2.0) - 6, "×2", 9, RED, "start", "bold")
    s += text(ox + ww - 8, oy - hh + 18, "позитивний", 9.5, GREEN, "end", "bold")
    s += text(ox + ww - 8, oy - hh + 34, "темп. коефіцієнт", 9, GREEN, "end")
    s += text(W / 2, H - 10, "Гарячіший MOSFET бере менше струму → паралельні самі вирівнюються, розгону немає. Рахуй на гарячий опір.",
              9, GREY, "middle", style="italic")
    save("fig-12-5-6-temperature.svg", s)


# ── Рис. 12.6.1 — low-side ключ ──────────────────────────────────────────────
def fig126_low_side_switch():
    W, H = 680, 360
    s = header(W, H)
    s += text(W / 2, 28, "Ключ нижнього плеча на N-каналі", 16, INK, "middle", "bold")
    TOP, GND = 64, 320
    s += line(120, TOP, 560, TOP, RED, 2) + text(114, TOP + 4, "+V", 11, RED, "end", "bold")
    s += line(120, GND, 560, GND, INK, 1.6) + text(114, GND + 4, "GND", 10, INK, "end", "bold")
    s += _mosfet_sym(400, 210, False)
    dx = 424
    s += rect(dx - 40, 92, 80, 40, "#ffffff", INK, 1.6)
    s += text(dx + 50, 116, "навантаження", 9.5, INK, "start")
    s += line(dx, TOP, dx, 92, INK, 2) + line(dx, 132, dx, 166, INK, 2)
    s += line(dx, 254, dx, GND, INK, 2)
    s += text(150, 214, "МК", 10, GREEN, "end", "bold")
    s += line(160, 210, 250, 210, INK, 2)
    s += rect(250, 198, 54, 24, "#ffffff", INK, 1.6) + text(277, 214, "Rg", 10, INK, "middle", "bold")
    s += line(304, 210, 356, 210, INK, 2)
    s += circle(330, 210, 3, INK, INK) + line(330, 210, 330, 250, INK, 2)
    s += rect(316, 250, 28, 42, "#ffffff", INK, 1.6) + text(330, 276, "Rпд", 9, INK, "middle", "bold")
    s += line(330, 292, 330, GND, INK, 2)
    s += text(277, 191, "десятки–сотні Ом", 7.5, GREY, "middle")
    s += text(360, 280, "десятки кОм", 7.5, GREY, "start")
    s += text(W / 2, H - 12, "Високий рівень на затворі → канал відкритий → струм крізь навантаження на землю. Низький → вимкнено.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-6-1-low-side-switch.svg", s)


# ── Рис. 12.6.2 — резистор затвора + підтяжка ────────────────────────────────
def fig126_gate_resistor_pulldown():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Дві деталі біля затвора", 15.5, INK, "middle", "bold")
    s += rect(60, 130, 80, 44, LBLUE, "#9bb0c2", 1.4, 6) + text(100, 156, "МК", 12, INK, "middle", "bold")
    s += line(140, 152, 210, 152, INK, 2)
    s += rect(210, 140, 60, 24, "#ffffff", INK, 1.6) + text(240, 156, "Rg", 11, INK, "middle", "bold")
    s += line(270, 152, 360, 152, INK, 2)
    s += line(360, 124, 360, 180, INK, 3) + text(372, 152, "затвор", 9.5, INK, "start", "bold")
    s += circle(320, 152, 3, INK, INK) + line(320, 152, 320, 210, INK, 2)
    s += rect(306, 210, 28, 44, "#ffffff", INK, 1.6) + text(320, 236, "Rпд", 9, INK, "middle", "bold")
    s += line(320, 254, 320, 280, INK, 2) + line(282, 280, 358, 280, INK, 1.5) + text(364, 284, "GND", 8.5, INK, "start")
    s += rect(430, 72, 250, 68, "#fff7e6", COPP, 1.3, 6)
    s += text(555, 94, "Rg — обмежує кидок струму", 10, INK, "middle", "bold")
    s += text(555, 112, "у мить перемикання", 9.5, INK, "middle")
    s += text(555, 128, "(+ плавний пуск)", 9, GREY, "middle")
    s += rect(430, 166, 250, 78, "#eef6ef", GREEN, 1.3, 6)
    s += text(555, 188, "Rпд — тримає затвор у 0,", 10, GREEN, "middle", "bold")
    s += text(555, 206, "поки МК ще не керує", 9.5, INK, "middle")
    s += text(555, 224, "(проти плаваючого затвора)", 9, GREY, "middle")
    s += arrow(370, 96, 428, 100, GREY, 1.5)
    s += arrow(338, 200, 428, 200, GREY, 1.5)
    save("fig-12-6-2-gate-resistor-pulldown.svg", s)


# ── Рис. 12.6.3 — плаваючий затвор ───────────────────────────────────────────
def fig126_floating_gate():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Плаваючий затвор: чому потрібна підтяжка", 15, INK, "middle", "bold")

    def panel(ox, title, pulled):
        t = _frame(ox, 52, 300, 222, title)
        t += rect(ox + 30, 108, 64, 36, LBLUE, "#9bb0c2", 1.3, 5) + text(ox + 62, 130, "МК", 10, INK, "middle", "bold")
        t += text(ox + 62, 160, "(старт: не керує)", 8, GREY, "middle")
        t += line(ox + 94, 126, ox + 170, 126, INK, 1.8)
        t += line(ox + 170, 102, ox + 170, 150, INK, 3) + text(ox + 182, 126, "затвор", 9, INK, "start")
        if pulled:
            t += circle(ox + 150, 126, 3, INK, INK) + line(ox + 150, 126, ox + 150, 198, GREEN, 2)
            t += rect(ox + 136, 198, 28, 34, "#ffffff", GREEN, 1.5) + text(ox + 150, 220, "Rпд", 8, GREEN, "middle", "bold")
            t += line(ox + 150, 232, ox + 150, 248, GREEN, 2)
            t += text(ox + 150, 264, "затвор = 0 → ВИМКНЕНО", 9.5, GREEN, "middle", "bold")
        else:
            t += text(ox + 150, 184, "?", 24, RED, "middle", "bold")
            t += text(ox + 150, 214, "затвор тримає випадковий заряд", 8.5, RED, "middle")
            t += text(ox + 150, 250, "→ може ввімкнутися саме", 9.5, RED, "middle", "bold")
        return t

    s += panel(40, "без підтяжки — небезпечно", False)
    s += panel(380, "з підтяжкою — надійно", True)
    s += text(W / 2, H - 8, "Поки ніжка МК у високоомному стані, лише підтяжний резистор тримає ключ вимкненим.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-6-3-floating-gate.svg", s)


# ── Рис. 12.6.4 — гасний діод ────────────────────────────────────────────────
def fig126_flyback():
    W, H = 680, 350
    s = header(W, H)
    s += text(W / 2, 26, "Гасний діод на навантаженні (вбудований тут не рятує)", 13.5, INK, "middle", "bold")
    TOP, GND = 66, 312
    s += line(120, TOP, 580, TOP, RED, 2) + text(114, TOP + 4, "+V", 11, RED, "end", "bold")
    s += line(120, GND, 580, GND, INK, 1.6) + text(114, GND + 4, "GND", 10, INK, "end", "bold")
    s += _mosfet_sym(360, 206, False)
    dx = 384
    s += rect(dx - 44, 92, 88, 40, "#ffffff", INK, 1.6) + text(dx, 108, "мотор", 9.5, INK, "middle", "bold") + text(dx, 123, "(L)", 8.5, INK, "middle")
    s += line(dx, TOP, dx, 92, INK, 2) + line(dx, 132, dx, 162, INK, 2)
    fbx = 490
    s += line(dx, 146, fbx, 146, INK, 1.6) + line(fbx, 146, fbx, 122, INK, 1.6)
    s += f'<path d="M {fbx-10},122 L {fbx+10},122 L {fbx},104 Z" fill="#dfe7f0" stroke="{INK}" stroke-width="1.5"/>\n'
    s += line(fbx - 10, 100, fbx + 10, 100, INK, 2.6) + line(fbx, 100, fbx, TOP, INK, 1.6)
    s += text(fbx + 14, 116, "гасний діод", 9.5, GREEN, "start", "bold") + text(fbx + 14, 131, "(катод до +V)", 8.5, GREY, "start")
    s += line(dx, 250, dx, GND, INK, 2)
    s += line(316, 206, 180, 206, INK, 1.8) + text(174, 210, "затвор ← МК", 9.5, GREEN, "end", "bold")
    s += arrow(300, 252, 342, 224, RED, 1.6)
    s += text(150, 262, "вбудований діод (витік→стік)", 9, RED, "start", "bold")
    s += text(150, 278, "при викиді на стоці ЗАКРИТИЙ", 8.5, INK, "start")
    s += text(W / 2, H - 8, "Викид котушки задирає стік угору; вбудований діод для цього закритий — тож зовнішній гасний обов'язковий.",
              9, GREY, "middle", style="italic")
    save("fig-12-6-4-flyback.svg", s)


# ── Рис. 12.6.5 — верхнє плече PMOS ──────────────────────────────────────────
def fig126_high_side_pmos():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 26, "Нижнє плече (NMOS) і верхнє плече (PMOS)", 14.5, INK, "middle", "bold")

    def panel(ox, title, pch):
        t = _frame(ox, 50, 300, 250, title)
        TOP, GND = 78, 280
        t += line(ox + 40, TOP, ox + 260, TOP, RED, 1.8) + text(ox + 34, TOP + 4, "+V", 9, RED, "end", "bold")
        t += line(ox + 40, GND, ox + 260, GND, INK, 1.4) + text(ox + 34, GND + 4, "GND", 8.5, INK, "end")
        cx = ox + 175
        if not pch:
            t += rect(cx - 26, TOP + 14, 52, 30, "#ffffff", INK, 1.4) + text(cx, TOP + 33, "наван.", 8, INK, "middle")
            t += line(cx, TOP, cx, TOP + 14, INK, 1.6)
            t += _mosfet_sym(cx - 24, 200, False)
            t += line(cx, TOP + 44, cx, 156, INK, 1.6)
            t += line(cx, 244, cx, GND, INK, 1.6)
            t += text(cx - 72, 198, "ввімк:", 8.5, GREEN, "end", "bold") + text(cx - 72, 212, "затвор=1", 8.5, GREEN, "end")
        else:
            t += _mosfet_sym(cx - 24, 130, True)
            t += line(cx, TOP, cx, 86, INK, 1.6)
            t += rect(cx - 26, GND - 44, 52, 30, "#ffffff", INK, 1.4) + text(cx, GND - 25, "наван.", 8, INK, "middle")
            t += line(cx, 174, cx, GND - 44, INK, 1.6)
            t += line(cx, GND - 14, cx, GND, INK, 1.6)
            t += text(cx - 72, 128, "ввімк:", 8.5, GREEN, "end", "bold") + text(cx - 72, 142, "затвор=0", 8.5, GREEN, "end")
        return t

    s += panel(40, "нижнє плече — NMOS", False)
    s += panel(380, "верхнє плече — PMOS", True)
    s += text(W / 2, H - 8, "Розриваєш землю — NMOS, вмикає високий рівень. Розриваєш +V — PMOS, вмикає притягування затвора до землі.",
              9, GREY, "middle", style="italic")
    save("fig-12-6-5-high-side-pmos.svg", s)


# ── Рис. 12.6.6 — MOSFET-ключ vs біполярний ──────────────────────────────────
def fig126_vs_bjt():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 26, "Ключ: біполярний vs MOSFET", 15.5, INK, "middle", "bold")

    def panel(ox, title, is_mos):
        t = _frame(ox, 50, 300, 230, title)
        TOP, GND = 76, 256
        cx = ox + 175
        t += line(ox + 40, TOP, ox + 260, TOP, RED, 1.7) + text(ox + 34, TOP + 4, "+V", 9, RED, "end", "bold")
        t += line(ox + 40, GND, ox + 260, GND, INK, 1.4) + text(ox + 34, GND + 4, "GND", 8.5, INK, "end")
        t += rect(cx - 26, TOP + 12, 52, 28, "#ffffff", INK, 1.4) + text(cx, TOP + 30, "наван.", 8, INK, "middle")
        t += line(cx, TOP, cx, TOP + 12, INK, 1.5)
        if is_mos:
            t += _mosfet_sym(cx - 24, 180, False)
            t += line(cx, TOP + 40, cx, 136, INK, 1.5) + line(cx, 224, cx, GND, INK, 1.5)
            t += line(cx - 68, 180, cx - 110, 180, INK, 1.6)
            t += rect(cx - 150, 169, 40, 22, "#ffffff", INK, 1.5) + text(cx - 130, 184, "Rg", 9, INK, "middle", "bold")
            t += line(cx - 150, 180, ox + 30, 180, INK, 1.5) + text(ox + 26, 184, "МК", 8.5, GREEN, "end", "bold")
            t += text(cx, 212, "напруга, струму нема", 8, GREEN, "middle", "bold")
        else:
            t += _bjt_sym(cx - 30, 180, True)
            t += line(cx, TOP + 40, cx, 124, INK, 1.5) + line(cx, 236, cx, GND, INK, 1.5)
            t += line(cx - 74, 180, cx - 110, 180, INK, 1.6)
            t += rect(cx - 150, 169, 40, 22, "#ffffff", INK, 1.5) + text(cx - 130, 184, "Rб", 9, INK, "middle", "bold")
            t += line(cx - 150, 180, ox + 30, 180, INK, 1.5) + text(ox + 26, 184, "МК", 8.5, GREEN, "end", "bold")
            t += text(cx, 212, "струм Ib весь час", 8, RED, "middle", "bold")
        return t

    s += panel(40, "біполярний (BJT)", False)
    s += panel(380, "польовий (MOSFET)", True)
    s += text(W / 2, H - 8, "BJT: резистор бази під струм Ib. MOSFET: малий резистор затвора + підтяжка, струму керування нема.",
              9, GREY, "middle", style="italic")
    save("fig-12-6-6-vs-bjt.svg", s)


# ── Рис. 12.7.1 — заряд затвора (відерце) ────────────────────────────────────
def fig127_gate_charge():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Заряд затвора Qg: «відерце», яке наповнюють і спорожнюють", 14.5, INK, "middle", "bold")

    def bucket(ox, title, fill_frac, lbl):
        t = text(ox + 90, 72, title, 12, INK, "middle", "bold")
        t += f'<path d="M {ox+40},100 L {ox+140},100 L {ox+128},220 L {ox+52},220 Z" fill="#ffffff" stroke="{INK}" stroke-width="1.8"/>\n'
        top = 220 - 116 * fill_frac
        t += f'<path d="M {ox+55},220 L {ox+125},220 L {ox+125},{top:.0f} L {ox+55},{top:.0f} Z" fill="{BLUE}" stroke="none" opacity="0.45"/>\n'
        t += text(ox + 90, 240, lbl, 9.5, INK, "middle", "bold")
        return t

    s += bucket(50, "вимкнено", 0.05, "затвор порожній")
    s += bucket(290, "наповнюємо Qg", 0.5, "заряджається")
    s += bucket(530, "увімкнено", 0.95, "затвор повний")
    s += arrow(202, 160, 280, 160, GREEN, 2.4) + text(241, 148, "+Qg", 10, GREEN, "middle", "bold")
    s += arrow(442, 160, 520, 160, GREEN, 2.4) + text(481, 148, "+Qg", 10, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Увімкнути = наповнити затвор зарядом Qg; вимкнути = спорожнити. Qg (нКл) — паспортна «місткість відерця».",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7-1-gate-charge.svg", s)


# ── Рис. 12.7.2 — час перемикання ────────────────────────────────────────────
def fig127_switch_time():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Час перемикання ≈ Qg / струм у затвор", 15.5, INK, "middle", "bold")
    s += text(W / 2, 58, "Qg = 30 нКл", 12, INK, "middle", "bold")
    s += text(70, 110, "ніжка МК:  4 мА", 11, INK, "start", "bold")
    s += rect(70, 122, 560, 30, "#fbeaea", RED, 1.4)
    s += text(350, 142, "t = 30 нКл / 4 мА = 7.5 мкс  (повільно)", 11, RED, "middle", "bold")
    s += text(70, 192, "драйвер затвора:  1 А", 11, INK, "start", "bold")
    s += rect(70, 204, 14, 30, "#eef6ef", GREEN, 1.4)
    s += text(120, 224, "t = 30 нКл / 1 А = 30 нс  (миттєво)", 11, GREEN, "start", "bold")
    s += text(W / 2, H - 12, "Та сама ємність, у 250 разів різний струм → у 250 разів різний час. Для швидких схем потрібен драйвер.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7-2-switch-time.svg", s)


# ── Рис. 12.7.3 — плато Міллера ──────────────────────────────────────────────
def fig127_miller_plateau():
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 28, "Напруга затвора в міру заряду: плато Міллера", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 100, 250, 460, 180
    s += _axes(ox, oy, ww, hh, "заряд Qg →", "Vgs")
    p1x, p2x = ox + 0.25 * ww, ox + 0.65 * ww
    pl_y = oy - 0.45 * hh
    s += _poly([(ox, oy), (p1x, pl_y), (p2x, pl_y), (ox + ww, oy - 0.92 * hh)], BLUE, 2.8)
    s += line(p1x, pl_y, p2x, pl_y, RED, 2.8)
    s += text((p1x + p2x) / 2, pl_y - 12, "плато Міллера", 10.5, RED, "middle", "bold")
    s += text((p1x + p2x) / 2, pl_y + 20, "(стік перемикає напругу)", 8.5, GREY, "middle")
    s += text(ox + 0.13 * ww, oy - 0.30 * hh, "поріг", 8.5, INK, "middle")
    s += text(ox + ww - 8, oy - 0.92 * hh + 4, "повністю", 8.5, GREEN, "end", "bold")
    s += text(W / 2, H - 10, "Більшість заряду (і часу) переходу йде на плато Міллера — там MOSFET найдовше «напіввідкритий».",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7-3-miller-plateau.svg", s)


# ── Рис. 12.7.4 — втрати на перемикання ──────────────────────────────────────
def fig127_switching_loss():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Втрати на перемикання: V та I перекриваються", 14.5, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 250, 520, 180
    s += _axes(ox, oy, ww, hh, "час →", "")
    t0, t1 = ox + 0.30 * ww, ox + 0.55 * ww
    s += _poly([(ox, oy - 0.8 * hh), (t0, oy - 0.8 * hh), (t1, oy - 0.05 * hh), (ox + ww, oy - 0.05 * hh)], BLUE, 2.4)
    s += text(ox + 0.14 * ww, oy - 0.87 * hh, "Vds", 10, BLUE, "middle", "bold")
    s += _poly([(ox, oy - 0.06 * hh), (t0, oy - 0.06 * hh), (t1, oy - 0.78 * hh), (ox + ww, oy - 0.78 * hh)], RED, 2.4)
    s += text(ox + 0.86 * ww, oy - 0.85 * hh, "Id", 10, RED, "middle", "bold")
    s += f'<path d="M {t0:.0f},{oy} L {(t0+t1)/2:.0f},{oy-0.5*hh:.0f} L {t1:.0f},{oy} Z" fill="#fde9c8" stroke="{SUN}" stroke-width="1.4"/>\n'
    s += text((t0 + t1) / 2, oy - 0.5 * hh - 10, "спалах P=V·I", 9.5, "#b5732e", "middle", "bold")
    s += line(t0, oy, t0, oy - hh - 6, GREY, 1, "3 3") + line(t1, oy, t1, oy - hh - 6, GREY, 1, "3 3")
    s += text((t0 + t1) / 2, oy + 18, "перехід", 9, INK, "middle", "bold")
    s += text(W / 2, H - 10, "Лише в коротку мить переходу напруга й струм є водночас — це й є втрата. Швидше → вужче → менше.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7-4-switching-loss.svg", s)


# ── Рис. 12.7.5 — втрати від частоти ─────────────────────────────────────────
def fig127_loss_vs_frequency():
    W, H = 680, 320
    s = header(W, H)
    s += text(W / 2, 28, "Втрати від частоти: провідні + на перемикання", 14.5, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 250, 460, 180
    s += _axes(ox, oy, ww, hh, "частота f →", "втрати P")
    cond = 0.30 * hh
    s += line(ox, oy - cond, ox + ww, oy - cond, BLUE, 2.4, "6 3")
    s += text(ox + ww - 8, oy - cond - 8, "провідні (Rds(on))", 9, BLUE, "end", "bold")
    s += _poly([(ox + (i / 40) * ww, oy - (i / 40) * 0.62 * hh) for i in range(41)], RED, 2.4)
    s += text(ox + 0.5 * ww, oy - 0.18 * hh, "на перемикання (∝ f)", 9, RED, "middle", "bold")
    s += _poly([(ox + (i / 40) * ww, oy - cond - (i / 40) * 0.62 * hh) for i in range(41)], GREEN, 2.8)
    s += text(ox + ww - 8, oy - cond - 0.62 * hh - 6, "сумарні", 9.5, GREEN, "end", "bold")
    s += text(W / 2, H - 10, "За низьких частот керує Rds(on); за високих верх беруть втрати на перемикання (Qg, швидкість).",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7-5-loss-vs-frequency.svg", s)


# ── Рис. 12.7.6 — драйвер затвора ────────────────────────────────────────────
def fig127_gate_driver():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Драйвер затвора: слабкий сигнал → потужні імпульси струму", 14, INK, "middle", "bold")
    s += rect(60, 120, 90, 50, LBLUE, "#9bb0c2", 1.4, 6) + text(105, 150, "МК", 13, INK, "middle", "bold")
    s += line(150, 145, 220, 145, INK, 1.4) + text(185, 132, "слабкий", 8, GREY, "middle")
    s += f'<path d="M 220,108 L 320,145 L 220,182 Z" fill="#eef6ef" stroke="{GREEN}" stroke-width="1.8"/>\n'
    s += text(256, 150, "драйвер", 9.5, GREEN, "middle", "bold")
    s += line(320, 145, 426, 145, GREEN, 5) + text(373, 130, "ампери!", 9.5, GREEN, "middle", "bold")
    s += _mosfet_sym(470, 145, False)
    s += text(484, 104, "великий", 9, INK, "middle") + text(484, 196, "MOSFET", 9.5, INK, "middle", "bold")
    s += text(373, 160, "(заряд і розряд)", 8, GREY, "middle")
    s += rect(560, 108, 142, 80, "#fbfbfb", "#c9d3dc", 1.2, 6)
    s += text(631, 132, "швидко наповнює", 9, INK, "middle")
    s += text(631, 150, "й спорожняє Qg", 9, INK, "middle")
    s += text(631, 174, "→ малі втрати", 9, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Сам МК не подужає амперних кидків у затвор; драйвер — це підсилювач струму спеціально для нього.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7-6-gate-driver.svg", s)


# ── Рис. 12.8.1 — корінь відмінності ─────────────────────────────────────────
def fig128_core_difference():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 30, "Корінь усього: керування струмом vs полем", 15.5, INK, "middle", "bold")
    s += _frame(40, 56, 300, 200, "біполярний — керує СТРУМ")
    s += _bjt_sym(180, 150, True)
    s += arrow(106, 150, 132, 150, RED, 2.6) + text(102, 138, "Ib", 10, RED, "end", "bold")
    s += text(190, 202, "струм у базу — весь час", 9.5, RED, "middle", "bold")
    s += text(190, 226, "(педаль тиснеш безперервно)", 8.5, GREY, "middle")
    s += _frame(380, 56, 300, 200, "польовий — керує ПОЛЕ")
    s += _mosfet_sym(520, 150, False)
    s += text(450, 138, "Vgs", 10, GREEN, "end", "bold") + arrow(452, 150, 474, 150, GREEN, 2.0, "3 2")
    s += text(530, 202, "напруга — струму нема", 9.5, GREEN, "middle", "bold")
    s += text(530, 226, "(перемикач тримається сам)", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Уся решта відмінностей — лише наслідки цього одного: струм проти поля.",
              10, GREY, "middle", style="italic")
    save("fig-12-8-1-core-difference.svg", s)


# ── Рис. 12.8.2 — порівняльна таблиця ────────────────────────────────────────
def fig128_comparison_table():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Біполярний проти польового — віч-на-віч", 16, INK, "middle", "bold")
    cols = [(40, 230, "риса"), (270, 270, "BJT (біполярний)"), (540, 240, "MOSFET (польовий)")]
    y0 = 54
    for x, w, lab in cols:
        s += rect(x, y0, w, 30, "#eef2f6", "#c9d3dc", 1.2)
        s += text(x + w / 2, y0 + 20, lab, 11.5, INK, "middle", "bold")
    rows = [
        ("керування", "струм бази (весь час)", "напруга затвора (нема)"),
        ("вхідний опір", "невеликий", "величезний"),
        ("спад відкритого", "сталий ~0.3 В", "Id·Rds(on), часто менший"),
        ("втрати vs струм", "лінійні (Vce·I)", "квадратичні (I²·R)"),
        ("температура", "схильний до розгону", "самобаланс, паралелиться"),
        ("швидкість", "заряд носіїв у базі", "заряд затвора Qg"),
        ("обв'язка", "резистор бази", "затвор + підтяжка, лог. рівень"),
    ]
    y = y0 + 30
    for name, b, m in rows:
        s += rect(cols[0][0], y, cols[0][1], 40, "#fbfbfb", "#d7dee5", 1)
        s += text(cols[0][0] + 12, y + 25, name, 11, INK, "start", "bold")
        s += rect(cols[1][0], y, cols[1][1], 40, "#fbeeef", "#e0c4c4", 1)
        s += text(cols[1][0] + 12, y + 25, b, 10.5, INK, "start")
        s += rect(cols[2][0], y, cols[2][1], 40, "#eef6ef", "#c4d6c4", 1)
        s += text(cols[2][0] + 12, y + 25, m, 10.5, INK, "start")
        y += 40
    s += text(W / 2, y + 22, "Перший рядок — корінь (струм/поле); решта — його наслідки.", 10, GREY, "middle", style="italic")
    save("fig-12-8-2-comparison-table.svg", s)


# ── Рис. 12.8.3 — коли який ──────────────────────────────────────────────────
def fig128_when_each():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 30, "Коли який: дві вотчини", 16, INK, "middle", "bold")
    s += rect(40, 60, 340, 230, "#eef6ef", GREEN, 1.5, 8)
    s += text(210, 86, "MOSFET (майже завжди)", 12, GREEN, "middle", "bold")
    mos = ["силове перемикання (мотори, ключі)", "цифрова логіка (КМОН)", "батарейні: нульова потужн. керув.",
           "високий вхідний опір (буфери)", "масове/інтегроване — млрд на чипі"]
    y = 116
    for it in mos:
        s += circle(62, y - 4, 3, GREEN, GREEN) + text(78, y, it, 9.5, INK, "start")
        y += 32
    s += rect(400, 60, 320, 230, "#fbeeef", RED, 1.5, 8)
    s += text(560, 86, "BJT (аналогові ніші)", 12, RED, "middle", "bold")
    bjt = ["дзеркала струмів, опорні джерела", "температурні давачі (Vbe)", "малошумні / узгоджені пари",
           "точний аналог (вища крутість gm)", "дрібні дешеві ключі під рукою"]
    y = 116
    for it in bjt:
        s += circle(422, y - 4, 3, RED, RED) + text(438, y, it, 9.5, INK, "start")
        y += 32
    s += text(W / 2, H - 12, "А багато аналогових задач узяв на себе операційник (Розділ 13).",
              9.5, GREY, "middle", style="italic")
    save("fig-12-8-3-when-each.svg", s)


# ── Рис. 12.8.4 — дерево рішень ──────────────────────────────────────────────
def fig128_decision_flow():
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 30, "Дерево вибору транзистора", 16, INK, "middle", "bold")
    rows = [
        ("Перемикати потужне навантаження?", "MOSFET (лог. рівня)", GREEN),
        ("Цифрова логіка / економність?", "MOSFET (КМОН)", GREEN),
        ("Точний аналог: дзеркало, опора, пара?", "BJT / операційник", RED),
        ("Просто ввімкнути світлодіод / реле?", "байдуже", GREY),
    ]
    y = 76
    for q, a, col in rows:
        s += rect(70, y, 380, 44, "#fbfbfb", "#c9d3dc", 1.3, 6)
        s += text(88, y + 27, q, 11, INK, "start", "bold")
        s += arrow(458, y + 22, 486, y + 22, col, 2.2)
        s += rect(494, y, 196, 44, "#ffffff", col, 1.5, 6)
        s += text(592, y + 27, a, 10.5, col, "middle", "bold")
        y += 58
    s += text(W / 2, H - 14, "Корінь правила: силу й цифру — польовому; точний дрібний аналог — біполярному.",
              10, GREY, "middle", style="italic")
    save("fig-12-8-4-decision-flow.svg", s)


# ── Рис. 12.8.5 — та сама задача ─────────────────────────────────────────────
def fig128_same_task():
    W, H = 720, 310
    s = header(W, H)
    s += text(W / 2, 28, "Та сама задача: увімкнути мотор 2 А", 15.5, INK, "middle", "bold")
    s += _frame(40, 54, 300, 210, "біполярним")
    s += text(190, 88, "β=100 → Ib ≈ 20 мА", 11, INK, "middle", "bold")
    s += text(190, 108, "(тече весь час)", 8.5, GREY, "middle")
    s += text(190, 138, "Vce(sat) ≈ 0.3 В", 11, INK, "middle")
    s += rect(80, 158, 220, 46, "#fbeeef", RED, 1.4, 6)
    s += text(190, 178, "спад 0.3 В · 2 А", 10, INK, "middle")
    s += text(190, 196, "≈ 0.6 Вт + база", 12, RED, "middle", "bold")
    s += text(190, 238, "гарячіше", 10, RED, "middle", "bold")
    s += _frame(380, 54, 300, 210, "MOSFET-ом")
    s += text(530, 88, "струм затвора ≈ 0", 11, INK, "middle", "bold")
    s += text(530, 108, "(тримається задарма)", 8.5, GREY, "middle")
    s += text(530, 138, "Rds(on) ≈ 20 мОм", 11, INK, "middle")
    s += rect(420, 158, 220, 46, "#eef6ef", GREEN, 1.4, 6)
    s += text(530, 178, "P = I²·Rds = 4·0.02", 10, INK, "middle")
    s += text(530, 196, "≈ 0.08 Вт", 12, GREEN, "middle", "bold")
    s += text(530, 238, "холодний", 10, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Для перемикання MOSFET явно кращий: холодніший і не марнує струму на керування.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-8-5-same-task.svg", s)


# ── Рис. 12.8.6 — дуга подій + IGBT/BiCMOS ───────────────────────────────────
def fig128_history_arc_igbt():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 30, "Дуга подій і напарники", 16, INK, "middle", "bold")
    s += text(120, 78, "1947", 12, INK, "middle", "bold") + text(120, 98, "BJT — панує", 10, RED, "middle", "bold")
    s += arrow(190, 90, 330, 90, GREY, 2)
    s += text(430, 78, "1959 → 1970-ті", 11, INK, "middle", "bold") + text(430, 98, "MOSFET → КМОН → бере цифру й силу", 9.5, GREEN, "middle", "bold")
    s += arrow(620, 90, 690, 90, GREY, 2)
    s += text(745, 78, "сьогодні", 11, INK, "middle", "bold") + text(745, 98, "співіснують", 9.5, INK, "middle")
    s += rect(80, 138, 330, 122, "#fff7e6", COPP, 1.5, 8)
    s += text(245, 162, "IGBT — гібрид", 12, "#b5732e", "middle", "bold")
    s += text(245, 186, "затвор як у MOSFET (керує напруга)", 9.5, INK, "middle")
    s += text(245, 206, "+ вихід як у BJT (малий спад)", 9.5, INK, "middle")
    s += text(245, 232, "надпотужне: е-авто, плити, зварка", 9, GREY, "middle")
    s += rect(450, 138, 290, 122, "#eef2f6", "#9bb0c2", 1.5, 8)
    s += text(595, 162, "BiCMOS — на одному чипі", 11, BLUE, "middle", "bold")
    s += text(595, 186, "MOSFET — логіка (щільно)", 9, INK, "middle")
    s += text(595, 206, "BJT — точний аналог поряд", 9, INK, "middle")
    s += text(595, 232, "розподіл праці, не війна", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Біполярний відступив в аналогову твердиню; для надпотужного — IGBT, що поєднав обох.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-8-6-history-arc-igbt.svg", s)


# ── Рис. 12.9.1 — інвертор КМОН ──────────────────────────────────────────────
def fig129_inverter():
    W, H = 560, 360
    s = header(W, H)
    s += text(W / 2, 30, "Інвертор КМОН (вентиль НЕ)", 16, INK, "middle", "bold")
    cx = 290
    s += line(150, 72, 430, 72, RED, 2) + text(144, 76, "+V", 11, RED, "end", "bold")
    s += line(150, 312, 430, 312, INK, 1.6) + text(144, 316, "GND", 10, INK, "end", "bold")
    s += rect(cx - 58, 100, 116, 58, "#f3e2e2", RED, 1.7, 6) + text(cx, 126, "PMOS", 13, RED, "middle", "bold")
    s += text(cx, 145, "(тягне до +V)", 8.5, INK, "middle")
    s += line(cx, 72, cx, 100, INK, 2)
    s += rect(cx - 58, 226, 116, 58, "#eaf0e8", GREEN, 1.7, 6) + text(cx, 252, "NMOS", 13, GREEN, "middle", "bold")
    s += text(cx, 271, "(тягне до землі)", 8.5, INK, "middle")
    s += line(cx, 284, cx, 312, INK, 2)
    s += line(cx, 158, cx, 226, INK, 2) + circle(cx, 192, 3.5, INK, INK)
    s += line(cx, 192, cx + 130, 192, INK, 2) + text(cx + 136, 196, "вихід", 11, INK, "start", "bold")
    s += line(cx - 58, 129, cx - 120, 129, INK, 1.6)
    s += line(cx - 58, 255, cx - 120, 255, INK, 1.6)
    s += line(cx - 120, 129, cx - 120, 255, INK, 1.6)
    s += line(cx - 120, 192, cx - 180, 192, INK, 2) + text(cx - 186, 196, "вхід", 11, INK, "end", "bold")
    s += text(W / 2, H - 12, "Вхід керує обома затворами; вихід — між стоками. Вихід завжди протилежний входові.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9-1-inverter.svg", s)


# ── Рис. 12.9.2 — два стани ──────────────────────────────────────────────────
def fig129_two_states():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 28, "Два стани інвертора", 16, INK, "middle", "bold")

    def panel(ox, in_val, out_val, p_on, n_on):
        t = _frame(ox, 52, 300, 240, "вхід = %s  →  вихід = %s" % (in_val, out_val))
        cx = ox + 150
        t += line(ox + 50, 82, ox + 250, 82, RED, 1.6) + text(ox + 44, 86, "+V", 8.5, RED, "end", "bold")
        t += line(ox + 50, 272, ox + 250, 272, INK, 1.4) + text(ox + 44, 276, "0", 8.5, INK, "end")
        t += rect(cx - 50, 102, 100, 44, "#f3e2e2" if p_on else "#f0f0f0", RED if p_on else GREY, 1.6, 5)
        t += text(cx, 122, "PMOS", 10.5, RED if p_on else GREY, "middle", "bold") + text(cx, 138, "відкр." if p_on else "закр.", 8, INK, "middle")
        t += line(cx, 82, cx, 102, INK, 1.6)
        t += rect(cx - 50, 200, 100, 44, "#eaf0e8" if n_on else "#f0f0f0", GREEN if n_on else GREY, 1.6, 5)
        t += text(cx, 220, "NMOS", 10.5, GREEN if n_on else GREY, "middle", "bold") + text(cx, 236, "відкр." if n_on else "закр.", 8, INK, "middle")
        t += line(cx, 244, cx, 272, INK, 1.6)
        t += line(cx, 146, cx, 200, INK, 2) + circle(cx, 173, 3, INK, INK)
        outcol = RED if out_val == "1" else GREEN
        t += line(cx, 173, cx + 96, 173, outcol, 2.4) + text(cx + 102, 177, out_val, 13, outcol, "start", "bold")
        if n_on:
            t += text(cx, 262, "вихід → земля", 8.5, GREEN, "middle", "bold")
        else:
            t += text(cx, 96, "вихід → +V", 8.5, RED, "middle", "bold")
        return t

    s += panel(40, "1", "0", False, True)
    s += panel(380, "0", "1", True, False)
    s += text(W / 2, H - 10, "Відкритий завжди рівно один транзистор пари — той, що тягне вихід у потрібний бік.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9-2-two-states.svg", s)


# ── Рис. 12.9.3 — нема статичного струму ─────────────────────────────────────
def fig129_no_static_current():
    W, H = 560, 340
    s = header(W, H)
    s += text(W / 2, 30, "Магія: у спокої наскрізного струму немає", 14.5, INK, "middle", "bold")
    cx = 250
    s += line(120, 72, 380, 72, RED, 2) + text(114, 76, "+V", 11, RED, "end", "bold")
    s += line(120, 300, 380, 300, INK, 1.6) + text(114, 304, "GND", 10, INK, "end", "bold")
    s += rect(cx - 52, 100, 104, 50, "#eef6ef", GREEN, 1.6, 6) + text(cx, 122, "відкритий", 9.5, GREEN, "middle", "bold") + text(cx, 138, "(проводить)", 8, INK, "middle")
    s += line(cx, 72, cx, 100, INK, 2)
    s += rect(cx - 52, 222, 104, 50, "#fbeeef", RED, 1.6, 6) + text(cx, 244, "ЗАКРИТИЙ", 9.5, RED, "middle", "bold") + text(cx, 260, "(перекриває)", 8, INK, "middle")
    s += line(cx, 272, cx, 300, INK, 2)
    s += line(cx, 150, cx, 222, INK, 2)
    s += line(cx - 18, 247, cx + 18, 271, RED, 3) + line(cx - 18, 271, cx + 18, 247, RED, 3)
    s += circle(cx, 186, 3, INK, INK) + line(cx, 186, cx + 110, 186, INK, 2) + text(cx + 116, 190, "вихід", 10, INK, "start", "bold")
    s += text(cx - 132, 186, "I ≈ 0", 16, GREEN, "middle", "bold")
    s += arrow(cx - 96, 186, cx - 60, 186, GREEN, 2, "3 2")
    s += text(W / 2, H - 12, "Один транзистор пари завжди закритий → шлях +V→земля перекрито → тримати стан задарма.",
              9, GREY, "middle", style="italic")
    save("fig-12-9-3-no-static-current.svg", s)


# ── Рис. 12.9.4 — динамічне споживання ───────────────────────────────────────
def fig129_dynamic_power():
    W, H = 680, 300
    s = header(W, H)
    s += text(W / 2, 28, "Споживання — лише при перемиканні: P = C·V²·f", 14.5, INK, "middle", "bold")
    ox, oy, ww = 70, 150, 420
    seg = ww / 6
    levels = [1, 0, 1, 0, 1, 0, 1]
    ylow, yhigh = oy, oy - 50
    path = [(ox, yhigh if levels[0] else ylow)]
    for i in range(1, 7):
        x2 = ox + seg * i
        path.append((x2, yhigh if levels[i - 1] else ylow))
        path.append((x2, yhigh if levels[i] else ylow))
    s += _poly(path, BLUE, 2.4)
    s += text(ox - 8, oy - 50, "вихід", 9, BLUE, "end", "bold")
    sy = oy + 70
    s += line(ox, sy, ox + ww, sy, GREY, 1)
    for i in range(1, 7):
        x2 = ox + seg * i
        s += _poly([(x2 - 6, sy), (x2, sy - 34), (x2 + 6, sy)], RED, 2.2)
    s += text(ox - 8, sy, "струм", 9, RED, "end", "bold")
    s += text(ox + ww / 2, sy + 24, "сплески лише на перемиканнях; між ними — нуль", 9, INK, "middle")
    s += rect(W - 178, 62, 150, 72, LGRN, GREEN, 1.4, 8)
    s += text(W - 103, 90, "P = C·V²·f", 15, GREEN, "middle", "bold")
    s += text(W - 103, 116, "статика ≈ 0", 9.5, INK, "middle")
    s += text(W / 2, H - 10, "Між перемиканнями струму нема; енергія йде лише на перезаряд ємностей. Менше V і C, нижче f — холодніше.",
              8.5, GREY, "middle", style="italic")
    save("fig-12-9-4-dynamic-power.svg", s)


# ── Рис. 12.9.5 — вентиль І-НЕ ───────────────────────────────────────────────
def fig129_nand_gate():
    W, H = 560, 380
    s = header(W, H)
    s += text(W / 2, 28, "Вентиль І-НЕ (NAND) на КМОН", 15.5, INK, "middle", "bold")
    s += line(120, 64, 440, 64, RED, 2) + text(114, 68, "+V", 11, RED, "end", "bold")
    s += line(120, 340, 440, 340, INK, 1.6) + text(114, 344, "GND", 10, INK, "end", "bold")
    s += text(300, 86, "PMOS паралельно", 8.5, RED, "middle", "bold")
    s += rect(200, 96, 80, 40, "#f3e2e2", RED, 1.5, 5) + text(240, 121, "P(A)", 9.5, RED, "middle", "bold")
    s += rect(320, 96, 80, 40, "#f3e2e2", RED, 1.5, 5) + text(360, 121, "P(B)", 9.5, RED, "middle", "bold")
    s += line(240, 64, 240, 96, INK, 1.5) + line(360, 64, 360, 96, INK, 1.5)
    s += line(240, 136, 240, 168, INK, 1.5) + line(360, 136, 360, 168, INK, 1.5) + line(240, 168, 360, 168, INK, 1.5)
    s += circle(300, 168, 3.5, INK, INK) + line(300, 168, 470, 168, INK, 2) + text(476, 172, "вихід", 10, INK, "start", "bold")
    s += line(300, 168, 300, 200, INK, 2)
    s += rect(260, 200, 80, 40, "#eaf0e8", GREEN, 1.5, 5) + text(300, 225, "N(A)", 9.5, GREEN, "middle", "bold")
    s += line(300, 240, 300, 264, INK, 1.5)
    s += rect(260, 264, 80, 40, "#eaf0e8", GREEN, 1.5, 5) + text(300, 289, "N(B)", 9.5, GREEN, "middle", "bold")
    s += line(300, 304, 300, 340, INK, 1.5)
    s += text(412, 252, "NMOS", 9, GREEN, "middle", "bold") + text(412, 268, "послідовно", 8.5, GREEN, "middle")
    s += text(W / 2, H - 12, "Нуль на виході лише коли A=1 І B=1 (обидва NMOS провідні). Інакше PMOS тягне вихід в одиницю.",
              8.5, GREY, "middle", style="italic")
    save("fig-12-9-5-nand-gate.svg", s)


# ── Рис. 12.9.6 — від пари до процесора ──────────────────────────────────────
def fig129_gates_to_cpu():
    W, H = 820, 260
    s = header(W, H)
    s += text(W / 2, 30, "Від однієї пари до процесора", 16, INK, "middle", "bold")
    stages = [
        ("PMOS+NMOS", "комплементарна пара", LBLUE),
        ("інвертор / І-НЕ", "вентиль", "#eef6ef"),
        ("суматори, тригери", "логічні блоки", "#fff7e6"),
        ("процесор", "млрд вентилів", LGRN),
    ]
    bw, gap, by = 170, 30, 84
    for i, (head, sub, fill) in enumerate(stages):
        x = 30 + i * (bw + gap)
        s += rect(x, by, bw, 90, fill, "#9bb0c2", 1.5, 8)
        s += text(x + bw / 2, by + 40, head, 12, INK, "middle", "bold")
        s += text(x + bw / 2, by + 64, sub, 9.5, GREY, "middle")
        if i < 3:
            s += arrow(x + bw + 4, by + 45, x + bw + gap - 4, by + 45, GREEN, 2.4)
    s += text(W / 2, H - 16, "Уся цифрова техніка — це комплементарна пара PMOS+NMOS, повторена незліченно багато разів.",
              10, GREY, "middle", style="italic")
    save("fig-12-9-6-gates-to-cpu.svg", s)


# ── Рис. 12.9і.1 — проґавлений геній ─────────────────────────────────────────
def fig129i_ignored_genius():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 32, "Парадокс КМОН: геніально — і забуто на 20 років", 15.5, INK, "middle", "bold")
    s += rect(50, 76, 300, 150, "#eef6ef", GREEN, 1.6, 10)
    s += text(200, 104, "1963: винайдено", 12, GREEN, "middle", "bold")
    s += text(200, 134, "у спокої споживає", 10.5, INK, "middle")
    s += text(200, 160, "×1 000 000", 20, GREEN, "middle", "bold")
    s += text(200, 184, "менше за біполярну логіку", 9.5, INK, "middle")
    s += text(200, 208, "(шість порядків!)", 9, GREY, "middle")
    s += arrow(355, 150, 435, 150, GREY, 2.4) + text(395, 140, "і все ж…", 9.5, INK, "middle")
    s += rect(440, 76, 280, 150, "#f6eef0", "#d8a0a0", 1.6, 10)
    s += text(580, 104, "світ не помітив", 12, RED, "middle", "bold")
    s += text(580, 138, "«надто повільно,", 10.5, INK, "middle")
    s += text(580, 160, "нікому не треба»", 10.5, INK, "middle")
    s += text(580, 196, "20 років у тіні", 13, RED, "middle", "bold")
    s += text(W / 2, H - 14, "Правильна ідея чекала не приладу, а застосування — доби, коли тепло й батарея стануть важливішими за темп.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9i-1-ignored-genius.svg", s)


# ── Рис. 12.9і.2 — двоє винахідників ─────────────────────────────────────────
def fig129i_two_inventors():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 32, "Двоє з Fairchild, 1963", 16, INK, "middle", "bold")

    def card(ox, name, eng, role, origin):
        t = rect(ox, 64, 280, 130, "#fbfbfb", "#9bb0c2", 1.5, 10)
        t += circle(ox + 44, 104, 22, "#eef2f6", GREY, 1.6)
        t += text(ox + 78, 96, name, 13, INK, "start", "bold")
        t += text(ox + 78, 114, eng, 9.5, GREY, "start", "italic")
        t += text(ox + 20, 150, role, 9.5, INK, "start")
        t += text(ox + 20, 172, origin, 9, GREY, "start")
        return t

    s += card(40, "Френк Ванласс", "Frank Wanlass", "«євангеліст MOS»,", "інженер-будівничий · США")
    s += card(400, "Чіхтан Са", "Chih-Tang Sah", "фізик напівпровідників,", "нар. 1932 у Пекіні · кит.-амер.")
    s += arrow(180, 198, 320, 242, GREY, 2)
    s += arrow(540, 198, 400, 242, GREY, 2)
    s += rect(280, 242, 160, 40, LGRN, GREEN, 1.6, 8) + text(360, 267, "КМОН · 1963", 13, GREEN, "middle", "bold")
    s += text(W / 2, H - 8, "Стаття 1963 року написана ними двома. Кредит — обом, не загубивши нікого.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9i-2-two-inventors.svg", s)


# ── Рис. 12.9і.3 — чому зігнорували ──────────────────────────────────────────
def fig129i_why_overlooked():
    W, H = 720, 290
    s = header(W, H)
    s += text(W / 2, 30, "Чому зігнорували: повільно й нестабільно", 15, INK, "middle", "bold")
    s += text(190, 70, "швидкодія (1963)", 11, INK, "middle", "bold")
    s += rect(90, 86, 200, 26, "#fbeaea", RED, 1.4) + text(190, 104, "MOSFET — ×100 повільніший", 9, RED, "middle", "bold")
    s += rect(90, 122, 26, 26, "#eef6ef", GREEN, 1.4) + text(130, 140, "біполярний", 9, GREEN, "start", "bold")
    s += rect(360, 80, 320, 80, "#fff7e6", COPP, 1.3, 8)
    s += text(520, 104, "+ нестабільність:", 11, "#b5732e", "middle", "bold")
    s += text(520, 126, "характеристики «плавали»", 9.5, INK, "middle")
    s += text(520, 144, "з часом і температурою", 9.5, INK, "middle")
    s += rect(120, 188, 480, 56, "#f6eef0", "#d8a0a0", 1.3, 8)
    s += text(360, 210, "промисловість гналася за швидкістю", 11, INK, "middle", "bold")
    s += text(360, 230, "— і економність КМОН тоді не оцінила", 10, INK, "middle")
    s += text(W / 2, H - 10, "Перевагу КМОН (мале споживання) тоді ніхто не цінував; ваду (повільність) бачили всі.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9i-3-why-overlooked.svg", s)


# ── Рис. 12.9і.4 — знайшла дім ───────────────────────────────────────────────
def fig129i_found_its_home():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 32, "Перший дім КМОН: там, де економність > швидкість", 14.5, INK, "middle", "bold")
    s += rect(110, 90, 110, 110, "#eef2f6", INK, 1.6, 14)
    s += circle(165, 140, 38, "#ffffff", INK, 1.6) + text(165, 146, "12:00", 12, INK, "middle", "bold")
    s += text(165, 222, "електронний", 9.5, INK, "middle") + text(165, 238, "годинник (~1974)", 9.5, INK, "middle", "bold")
    s += rect(290, 90, 100, 130, "#eef2f6", INK, 1.6, 10)
    s += rect(305, 102, 70, 22, "#dfe7f0", GREY, 1)
    for r in range(3):
        for c in range(3):
            s += rect(305 + c * 24, 132 + r * 26, 18, 18, "#ffffff", GREY, 1)
    s += text(340, 240, "калькулятор", 9.5, INK, "middle", "bold")
    s += rect(450, 96, 230, 120, "#eef6ef", GREEN, 1.5, 10)
    s += text(565, 124, "роки від однієї", 11, GREEN, "middle", "bold")
    s += text(565, 144, "батарейки-таблетки", 11, GREEN, "middle", "bold")
    s += text(565, 174, "КМОН-логіка + РК-екран", 9.5, INK, "middle")
    s += text(565, 192, "споживають майже нічого", 9.5, INK, "middle")
    s += text(W / 2, H - 12, "Годиннику не треба рекордної швидкості — треба роками жити від крихітної батареї. Це КМОН і вміла.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9i-4-found-its-home.svg", s)


# ── Рис. 12.9і.5 — потім стала швидкою ───────────────────────────────────────
def fig129i_then_got_fast():
    W, H = 760, 290
    s = header(W, H)
    s += text(W / 2, 30, "Як цікавинка перемогла все: два кроки", 15.5, INK, "middle", "bold")
    s += rect(40, 72, 330, 140, "#eef2f6", "#9bb0c2", 1.5, 10)
    s += text(205, 98, "крок 1 (кін. 1970-х)", 11, BLUE, "middle", "bold")
    s += text(205, 124, "дрібніша літографія +", 10, INK, "middle")
    s += text(205, 142, "кремнієвий затвор", 10, INK, "middle")
    s += text(205, 168, "→ КМОН стала ще й ШВИДКОЮ", 9.5, GREEN, "middle", "bold")
    s += text(205, 190, "(Масухара, Hitachi, 1978)", 8.5, GREY, "middle")
    s += rect(400, 72, 330, 140, "#fff7e6", COPP, 1.5, 10)
    s += text(565, 98, "крок 2 (1980-ті →)", 11, "#b5732e", "middle", "bold")
    s += text(565, 124, "мільйони вентилів →", 10, INK, "middle")
    s += text(565, 142, "вирішує СУМАРНЕ ТЕПЛО", 10, INK, "middle")
    s += text(565, 168, "→ майже нульовий спокій КМОН", 9.5, GREEN, "middle", "bold")
    s += text(565, 190, "став безальтернативним", 9.5, GREEN, "middle", "bold")
    s += arrow(372, 142, 398, 142, GREY, 2.4)
    s += text(W / 2, H - 12, "Спершу КМОН наздогнала за швидкістю, потім теплова стіна зробила її єдиним виходом.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9i-5-then-got-fast.svg", s)


# ── Рис. 12.9і.6 — урок ──────────────────────────────────────────────────────
def fig129i_lesson():
    W, H = 760, 290
    s = header(W, H)
    s += text(W / 2, 30, "Двічі та сама схема: ідея чекає, поки світ дозріє", 14.5, INK, "middle", "bold")

    def track(y, label, t1, l1, t2, l2, wait):
        t = text(60, y - 8, label, 11, INK, "start", "bold")
        t += circle(150, y + 18, 7, "#fdf1dc", "#d8b46a", 1.6) + text(150, y + 42, t1, 10, INK, "middle", "bold") + text(150, y + 58, l1, 8.5, GREY, "middle")
        t += line(160, y + 18, 560, y + 18, GREY, 1.6, "5 4")
        t += text(360, y + 8, wait, 9.5, RED, "middle", "bold")
        t += circle(570, y + 18, 7, "#eef6ef", GREEN, 1.6) + text(570, y + 42, t2, 10, INK, "middle", "bold") + text(570, y + 58, l2, 8.5, GREY, "middle")
        return t

    s += track(78, "польовий транзистор:", "1925", "ідея (Лілієнфельд)", "1959", "втілення", "чекав МАТЕРІАЛІВ — 34 роки")
    s += track(178, "КМОН:", "1963", "винахід (Ванласс, Са)", "1980-ті", "визнання", "чекала ПОТРЕБИ — ~20 років")
    s += text(W / 2, H - 12, "Правильна думка не пропадає — вона лежить, аж поки світ її потребуватиме.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-9i-6-lesson.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
#  §12.10 — H-міст (тема 2.7.10)
# ═════════════════════════════════════════════════════════════════════════════
def _motor(cx, cy, r=24, lab="M"):
    s = circle(cx, cy, r, "#fbfbfb", INK, 2)
    s += text(cx, cy + 6, lab, 16, INK, "middle", "bold")
    return s


def _sw(x, y, on=False, lab=""):
    """Ключ-прямокутник: зелений=відкритий, сірий=закритий."""
    col = GREEN if on else "#b8bcc0"
    fill = LGRN if on else "#f0f1f2"
    s = rect(x - 22, y - 16, 44, 32, fill, col, 2, 5)
    s += text(x, y + 5, lab, 12, INK, "middle", "bold")
    if on:
        s += text(x, y - 22, "ВІДКР", 7.5, GREEN, "middle", "bold")
    return s


def fig1210_need():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 30, "Один ключ крутить мотор лише в один бік", 17, INK, "middle", "bold")
    # ліворуч: один ключ
    s += _frame(40, 56, 320, 230, "один ключ (§2.7.6)")
    s += line(120, 90, 280, 90, RED, 2) + text(112, 94, "+V", 10, RED, "end", "bold")
    s += _motor(200, 130, 22)
    s += line(200, 90, 200, 108, INK, 2) + line(200, 152, 200, 180, INK, 2)
    s += _sw(200, 200, True, "Q")
    s += line(200, 216, 200, 250, INK, 2)
    s += line(120, 250, 280, 250, INK, 1.6) + text(112, 254, "GND", 9, INK, "end", "bold")
    s += arrow(232, 130, 232, 108, BLUE, 1.8) + text(244, 124, "струм", 9, BLUE, "start", "bold")
    s += text(200, 278, "тільки вперед ▶", 11, GREEN, "middle", "bold")
    # праворуч: потрібно назад
    s += _frame(400, 56, 320, 230, "а щоб НАЗАД?")
    s += _motor(560, 150, 30)
    s += arrow(560, 120, 560, 100, GREEN, 2.2) + text(575, 110, "вперед: струм →", 9.5, GREEN, "start", "bold")
    s += arrow(560, 180, 560, 200, RED, 2.2) + text(575, 192, "назад: струм ←", 9.5, RED, "start", "bold")
    s += text(560, 250, "треба ПЕРЕВЕРНУТИ напрямок", 10.5, INK, "middle", "bold")
    s += text(560, 268, "струму крізь мотор", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "Простий ключ лише вмикає й вимикає; змінити напрямок обертання він не може. Для цього потрібні чотири ключі.",
              10, GREY, "middle", style="italic")
    save("fig-12-10-1-need.svg", s)


def _hbridge(ox, oy, q1, q2, q3, q4, motor_lab="M", flow=None):
    """Малює H-міст. q1..q4 — стани (True=відкр). flow: 'fwd'/'rev'/None."""
    w, h = 260, 220
    topL, topR = ox + 50, ox + w - 50
    s = ""
    # шини
    s += line(ox, oy, ox + w, oy, RED, 2)                       # +V зверху
    s += line(ox, oy + h, ox + w, oy + h, INK, 1.6)             # GND знизу
    # верхні ключі (high-side)
    s += line(topL, oy, topL, oy + 30, INK, 1.6)
    s += _sw(topL, oy + 50, q1, "Q1")
    s += line(topR, oy, topR, oy + 30, INK, 1.6)
    s += _sw(topR, oy + 50, q2, "Q2")
    # нижні ключі (low-side)
    s += _sw(topL, oy + h - 50, q3, "Q3")
    s += line(topL, oy + h - 30, topL, oy + h, INK, 1.6)
    s += _sw(topR, oy + h - 50, q4, "Q4")
    s += line(topR, oy + h - 30, topR, oy + h, INK, 1.6)
    # мотор-перекладина
    s += line(topL, oy + 66, topL, oy + h / 2, INK, 1.6)
    s += line(topR, oy + 66, topR, oy + h / 2, INK, 1.6)
    s += line(topL, oy + h - 66, topL, oy + h / 2, INK, 1.6)
    s += line(topR, oy + h - 66, topR, oy + h / 2, INK, 1.6)
    s += line(topL, oy + h / 2, topL + 30, oy + h / 2, INK, 1.6)
    s += line(topR, oy + h / 2, topR - 30, oy + h / 2, INK, 1.6)
    s += _motor((topL + topR) / 2, oy + h / 2, 24, motor_lab)
    if flow == "fwd":
        s += arrow(topL + 32, oy + h / 2 - 12, topR - 32, oy + h / 2 - 12, GREEN, 2.4)
    elif flow == "rev":
        s += arrow(topR - 32, oy + h / 2 + 12, topL + 32, oy + h / 2 + 12, RED, 2.4)
    s += text(ox - 6, oy + 4, "+V", 9.5, RED, "end", "bold")
    s += text(ox - 6, oy + h + 4, "GND", 9, INK, "end", "bold")
    return s


def fig1210_hbridge():
    W, H = 720, 380
    s = header(W, H)
    s += text(W / 2, 30, "H-міст: чотири ключі у формі літери H", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "два верхні (high-side) + два нижні (low-side); мотор — перекладина посередині",
              11.5, GREY, "middle", style="italic")
    s += _hbridge(230, 90, False, False, False, False)
    # підписи
    s += text(150, 150, "верхні\n(до +V)", 10, RED, "middle", "bold")
    s += text(150, 145, "верхні ключі", 9.5, RED, "middle", "bold")
    s += text(150, 160, "(high-side)", 9, GREY, "middle")
    s += text(150, 250, "нижні ключі", 9.5, BLUE, "middle", "bold")
    s += text(150, 265, "(low-side)", 9, GREY, "middle")
    s += text(610, 200, "мотор —", 10, INK, "middle", "bold")
    s += text(610, 216, "перекладина «H»", 9.5, GREY, "middle")
    s += text(W / 2, H - 14, "Звідси й назва: схема справді схожа на літеру H, де мотор — горизонтальна риска, а ключі — чотири кінці.",
              10, GREY, "middle", style="italic")
    save("fig-12-10-2-hbridge.svg", s)


def fig1210_directions():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 30, "Напрямок задає ДІАГОНАЛЬ відкритих ключів", 17, INK, "middle", "bold")
    s += _hbridge(60, 80, True, False, False, True, flow="fwd")
    s += text(190, 320, "Q1 + Q4 → струм зліва направо → ВПЕРЕД ▶", 10.5, GREEN, "middle", "bold")
    s += _hbridge(440, 80, False, True, True, False, flow="rev")
    s += text(570, 320, "Q2 + Q3 → струм справа наліво → НАЗАД ◀", 10.5, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Одна діагональ женеться струм в один бік, інша — у протилежний. Мотор крутиться туди, куди тече струм.",
              10, GREY, "middle", style="italic")
    save("fig-12-10-3-directions.svg", s)


def fig1210_four_states():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 28, "Чотири корисні стани H-моста", 17.5, INK, "middle", "bold")
    cards = [
        (30, "ВПЕРЕД", "Q1 + Q4", GREEN, ["діагональ 1 відкрита", "струм →, мотор крутиться"]),
        (240, "НАЗАД", "Q2 + Q3", RED, ["діагональ 2 відкрита", "струм ←, інший бік"]),
        (450, "ГАЛЬМО", "Q3 + Q4", COPP, ["обидва нижні замкнені", "мотор закорочено — гальмує"]),
        (660, "ВИБІГ", "усі закриті", GREY, ["мотор від'єднано", "крутиться за інерцією"]),
    ]
    for x, name, keys, col, lines in cards:
        s += rect(x, 60, 150, 240, "#fbfbfb", col, 2, 10)
        s += text(x + 75, 88, name, 13, col, "middle", "bold")
        s += text(x + 75, 110, keys, 11, INK, "middle", "bold")
        s += line(x + 16, 122, x + 134, 122, "#eee", 1)
        s += _motor(x + 75, 165, 22)
        for k, ln in enumerate(lines):
            s += text(x + 75, 220 + k * 22, ln, 9.5, GREY, "middle")
    s += text(W / 2, H - 14, "Той самий міст і вмикає вперед/назад, і гальмує (закоротивши мотор), і відпускає на вибіг — усе чотирма ключами.",
              10.5, GREY, "middle", style="italic")
    save("fig-12-10-4-four-states.svg", s)


def fig1210_halfbridges():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 30, "H-міст = два півмости", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "кожен півміст — верхній + нижній ключ зі спільним виходом до одного кінця мотора",
              11, GREY, "middle", style="italic")
    # лівий півміст
    s += _frame(70, 80, 200, 240, "лівий півміст")
    s += line(110, 110, 230, 110, RED, 2)
    s += _sw(170, 145, True, "Q1")
    s += circle(170, 185, 4, INK, INK) + text(190, 189, "вихід A", 9, GREEN, "start", "bold")
    s += line(170, 161, 170, 209, INK, 1.6)
    s += _sw(170, 230, False, "Q3")
    s += line(170, 246, 170, 290, INK, 1.6) + line(110, 290, 230, 290, INK, 1.6)
    # правий
    s += _frame(510, 80, 200, 240, "правий півміст")
    s += line(550, 110, 670, 110, RED, 2)
    s += _sw(610, 145, False, "Q2")
    s += circle(610, 185, 4, INK, INK) + text(560, 189, "вихід B", 9, RED, "end", "bold")
    s += line(610, 161, 610, 209, INK, 1.6)
    s += _sw(610, 230, True, "Q4")
    s += line(610, 246, 610, 290, INK, 1.6) + line(550, 290, 670, 290, INK, 1.6)
    # мотор між виходами
    s += line(190, 185, 280, 185, INK, 1.8)
    s += _motor(390, 185, 26)
    s += line(420, 185, 590, 185, INK, 1.8)
    s += text(390, 230, "мотор між виходами A і B", 9.5, GREY, "middle")
    s += text(W / 2, H - 12, "Кожен півміст сам тягне свій кінець мотора до «+» або до землі; різниця між виходами A і B і є напруга на моторі.",
              10, GREY, "middle", style="italic")
    save("fig-12-10-5-halfbridges.svg", s)


def fig1210_shoot_through():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 28, "Смертельна заборона: наскрізний струм (shoot-through)", 16, INK, "middle", "bold")
    # ліворуч: заборонено
    s += _frame(40, 56, 340, 260, "НІКОЛИ: обидва ключі плеча відкриті")
    s += line(120, 90, 300, 90, RED, 2) + text(112, 94, "+V", 10, RED, "end", "bold")
    s += _sw(210, 130, True, "Q1")
    s += _sw(210, 230, True, "Q3")
    s += line(210, 146, 210, 214, RED, 4)
    s += line(120, 290, 300, 290, INK, 1.6) + text(112, 294, "GND", 9, INK, "end", "bold")
    s += line(210, 90, 210, 114, INK, 1.6) + line(210, 246, 210, 290, INK, 1.6)
    s += _poly([(238, 150), (252, 142), (260, 158), (272, 146)], "#ff7a00", 2.4)
    s += text(300, 175, "пряме коротке", 10, RED, "start", "bold")
    s += text(300, 191, "замикання +V на GND", 9, GREY, "start")
    s += text(210, 312, "миттєвий згубний струм → ключі гинуть", 9.5, "#9a2b22", "middle", "bold")
    # праворуч: мертвий час
    s += _frame(420, 56, 360, 260, "рятунок: «мертвий час» (dead time)")
    ox, oy, w = 450, 150, 300
    # Q1 спадає
    s += text(445, 110, "Q1:", 9.5, INK, "end", "bold")
    s += _poly([(ox, oy - 80), (ox + 110, oy - 80), (ox + 120, oy - 50), (ox + 300, oy - 50)], GREEN, 2.4)
    # Q3 росте пізніше
    s += text(445, 190, "Q3:", 9.5, INK, "end", "bold")
    s += _poly([(ox, oy + 20), (ox + 150, oy + 20), (ox + 160, oy - 10), (ox + 300, oy - 10)], BLUE, 2.4)
    # зона мертвого часу
    s += rect(ox + 110, oy - 90, 50, 130, "#fff3e0", "#e0a32e", 1.2, 3)
    s += text(ox + 135, oy + 58, "обидва", 8.5, COPP, "middle", "bold")
    s += text(ox + 135, oy + 72, "закриті", 8.5, COPP, "middle", "bold")
    s += text(ox + 150, oy - 105, "мертвий час", 9.5, COPP, "middle", "bold")
    s += text(610, oy + 90, "перш ніж відкрити один — повністю закрий інший", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Між перемиканнями плеча роблять паузу, коли ОБИДВА ключі закриті, — інакше на мить виходить коротке замикання.",
              10, GREY, "middle", style="italic")
    save("fig-12-10-6-shoot-through.svg", s)


def fig1210_pwm_speed():
    W, H = 800, 360
    s = header(W, H)
    s += text(W / 2, 28, "Напрямок — діагоналлю, швидкість — ШІМ", 17, INK, "middle", "bold")
    # напрямок
    s += _frame(40, 56, 320, 260, "напрямок: яка діагональ")
    s += text(200, 90, "Q1+Q4 → вперед", 11, GREEN, "middle", "bold")
    s += text(200, 116, "Q2+Q3 → назад", 11, RED, "middle", "bold")
    s += _motor(200, 180, 32)
    s += arrow(168, 180, 130, 180, RED, 2)
    s += arrow(232, 180, 270, 180, GREEN, 2)
    s += text(200, 250, "обертання слідує за струмом", 9.5, GREY, "middle")
    s += text(200, 272, "крізь мотор", 9.5, GREY, "middle")
    # швидкість
    s += _frame(400, 56, 360, 260, "швидкість: шпаруватість ШІМ")
    ox, oy, w = 430, 150, 300
    for k, (duty, lab, yo) in enumerate(((0.8, "80% → швидко", 0), (0.3, "30% → повільно", 90))):
        yy = oy - 40 + yo
        s += line(ox, yy, ox + w, yy, FAINT, 1)
        pts = [(ox, yy)]
        x = ox
        per = 60
        while x < ox + w - per:
            pts += [(x, yy), (x, yy - 34), (x + per * duty, yy - 34), (x + per * duty, yy), (x + per, yy)]
            x += per
        s += _poly(pts, BLUE if k == 0 else COPP, 2.2)
        s += text(ox + w + 4, yy - 16, lab, 9.5, INK, "start", "bold")
    s += text(580, oy + 95, "що більша частка «увімкнено» — то вища", 9, GREY, "middle")
    s += text(580, oy + 109, "середня напруга й швидкість мотора", 9, GREY, "middle")
    s += text(W / 2, H - 12, "Швидко вмикаючи й вимикаючи діагональ (ШІМ), регулюють середню напругу — отже, і швидкість, не гріючи нічого.",
              10, GREY, "middle", style="italic")
    save("fig-12-10-7-pwm-speed.svg", s)


# ── 🔌 вставка до 2.7.10: плата драйвера H-моста (Рис. 2.7.10c.k) ─────────────
def fig1210c_board_anatomy():
    W, H = 790, 392
    s = header(W, H)
    s += text(W / 2, 30, "Плата драйвера мотора: один чип ховає весь H-міст", 17, INK, "middle", "bold")
    # МК ліворуч
    s += _frame(28, 122, 150, 150, "логіка / МК")
    s += text(103, 170, "3.3 – 5 В", 12, INK, "middle")
    s += text(103, 196, "кілька мА", 11, GREY, "middle")
    # чип у центрі
    cx0, cy0, cw, ch = 250, 92, 272, 232
    s += rect(cx0, cy0, cw, ch, "#eef2f7", "#7f93a8", 2.2, 10)
    s += text(cx0 + cw / 2, cy0 + 24, "мікросхема-драйвер", 14, INK, "middle", "bold")
    inside = [
        "2 півмости = 4 MOSFET-ключі",
        "драйвери затворів (і верхніх!)",
        "логіка напрямку + мертвий час",
        "захист: струм · перегрів · КЗ",
    ]
    for i, ln in enumerate(inside):
        yy = cy0 + 58 + i * 40
        s += rect(cx0 + 18, yy - 18, cw - 36, 30, "#ffffff", "#c9d3dc", 1.4, 6)
        s += text(cx0 + cw / 2, yy + 2, ln, 11.5, INK, "middle")
    # входи МК → чип
    for i, lab in enumerate(["IN1", "IN2", "EN (ШІМ)"]):
        yy = 158 + i * 36
        s += arrow(178, yy, cx0, yy, INK, 2)
        s += text(214, yy - 6, lab, 10, INK, "middle", "bold")
    # живлення мотора зверху
    s += arrow(cx0 + cw / 2, 60, cx0 + cw / 2, cy0, RED, 2.4)
    s += text(cx0 + cw / 2, 52, "+VM (живлення мотора, 6–36 В)", 11, RED, "middle", "bold")
    # GND знизу
    s += line(cx0 + cw / 2, cy0 + ch, cx0 + cw / 2, cy0 + ch + 16, INK, 1.6)
    s += line(cx0 + cw / 2 - 60, cy0 + ch + 16, cx0 + cw / 2 + 60, cy0 + ch + 16, INK, 1.6)
    s += text(cx0 + cw / 2, cy0 + ch + 32, "GND", 10, INK, "middle", "bold")
    # виходи → мотор
    s += arrow(cx0 + cw, 158, 600, 158, INK, 2) + text(560, 150, "OUT1", 10.5, INK, "middle", "bold")
    s += arrow(cx0 + cw, 258, 600, 258, INK, 2) + text(560, 250, "OUT2", 10.5, INK, "middle", "bold")
    s += line(600, 158, 690, 158, INK, 2) + line(690, 158, 690, 178, INK, 2)
    s += line(600, 258, 690, 258, INK, 2) + line(690, 258, 690, 238, INK, 2)
    s += _motor(690, 208, 30)
    s += text(W / 2, H - 14,
              "Усе, що в темі збирали з ключів, гасних діодів і драйверів затвора, тут — в одному корпусі: лишаються логічні входи й два дроти до мотора.",
              10, GREY, "middle", style="italic")
    save("fig-12-10c-1-board-anatomy.svg", s)


def fig1210c_pinout_wiring():
    W, H = 790, 366
    s = header(W, H)
    s += text(W / 2, 30, "Як підключити: логічний бік і силовий бік — спільна земля", 16, INK, "middle", "bold")
    bx, by, bw, bh = 300, 80, 180, 210
    s += rect(bx, by, bw, bh, "#eef2f7", "#7f93a8", 2.2, 10)
    s += text(bx + bw / 2, by + bh / 2 - 6, "драйвер", 14, INK, "middle", "bold")
    s += text(bx + bw / 2, by + bh / 2 + 14, "мотора", 14, INK, "middle", "bold")
    # ліві піни (логіка)
    for lab, yy, col in [("VCC", 110, GREEN), ("IN1", 150, INK), ("IN2", 190, INK),
                          ("EN", 230, INK), ("GND", 280, GREEN)]:
        s += line(bx - 16, yy, bx, yy, col, 2)
        s += circle(bx - 16, yy, 3, col, col, 1)
        s += text(bx + 8, yy + 4, lab, 11, INK, "start", "bold")
    # праві піни (силові)
    for lab, yy, col in [("VM", 110, RED), ("OUT1", 160, INK), ("OUT2", 200, INK), ("GND", 280, GREEN)]:
        s += line(bx + bw, yy, bx + bw + 16, yy, col, 2)
        s += circle(bx + bw + 16, yy, 3, col, col, 1)
        s += text(bx + bw - 8, yy + 4, lab, 11, INK, "end", "bold")
    # МК ліворуч
    s += _frame(28, 150, 150, 140, "МК")
    s += text(103, 214, "3.3 / 5 В", 11, INK, "middle")
    # VCC (зелений) — живлення логіки
    s += line(103, 150, 103, 110, GREEN, 2) + arrow(103, 110, bx - 16, 110, GREEN, 2)
    # керування (INK)
    s += arrow(178, 150, bx - 16, 150, INK, 2)
    s += arrow(178, 190, bx - 16, 190, INK, 2)
    s += arrow(178, 230, bx - 16, 230, INK, 2)
    s += text(238, 138, "напрямок", 9, INK, "middle")
    s += text(232, 246, "ШІМ → швидкість", 9, INK, "middle")
    # спільна земля (зелена пунктирна шина)
    s += line(103, 290, 103, 318, GREEN, 2, "4 3")
    s += line(bx - 16, 280, bx - 16, 318, GREEN, 2, "4 3")
    s += line(bx + bw + 16, 280, bx + bw + 16, 318, GREEN, 2, "4 3")
    s += line(103, 318, bx + bw + 16, 318, GREEN, 2, "4 3")
    s += text((103 + bx + bw + 16) / 2, 336, "спільна земля — обов'язково з'єднати!", 10.5, GREEN, "middle", "bold")
    # живлення мотора (червоне) праворуч згори
    s += rect(560, 86, 200, 50, "#fbecec", "#d8a0a0", 1.6, 8)
    s += text(660, 108, "+ живлення мотора", 11, RED, "middle", "bold")
    s += text(660, 124, "(акумулятор, окремо)", 9.5, INK, "middle")
    s += arrow(560, 110, bx + bw + 18, 110, RED, 2.4)
    # мотор праворуч знизу
    s += _motor(660, 215, 34)
    s += arrow(bx + bw + 16, 160, 626, 160, INK, 2)
    s += line(626, 160, 660, 160, INK, 2) + line(660, 160, 660, 181, INK, 2)
    s += arrow(bx + bw + 16, 200, 600, 200, INK, 2)
    s += line(600, 200, 600, 249, INK, 2) + line(600, 249, 660, 249, INK, 2)
    s += text(W / 2, H - 8,
              "IN1/IN2 задають напрямок, EN (ШІМ) — швидкість; логіку й мотор живлять окремо, але землю з'єднують в одну точку.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-10c-2-pinout-wiring.svg", s)


# ── 🧮 вставка до 2.7.3: квадратичний закон Id(Vgs) (Рис. 2.7.3m.k) ───────────
def fig123m_square_law():
    W, H = 580, 400
    s = header(W, H)
    s += text(W / 2, 30, "Передатна крива — це парабола (Vgs − Vth)²", 16, INK, "middle", "bold")
    ox, oy, pw, ph = 90, 330, 410, 250
    s += _axes(ox, oy, pw, ph, "Vgs", "Id")
    vth_f = 0.26
    xth = ox + pw * vth_f
    span = 1.0 - vth_f
    # нульова поличка до порога
    s += _poly([(ox, oy), (xth, oy)], BLUE, 2.8)
    # парабола після порога
    pts = []
    for j in range(0, 101):
        f = j / 100.0
        x = xth + pw * span * f
        y = oy - ph * 0.9 * f * f
        pts.append((x, y))
    s += _poly(pts, RED, 2.8)
    # поріг
    s += line(xth, oy, xth, oy + 8, INK, 1.6)
    s += text(xth, oy + 24, "Vth", 12, INK, "middle", "bold")
    s += text((ox + xth) / 2, oy - 12, "канал закрито", 9.5, BLUE, "middle")
    s += text((ox + xth) / 2, oy - 26, "Id ≈ 0", 9.5, BLUE, "middle")
    # рівні кроки Vgs → дедалі більші кроки Id
    for f in (0.45, 0.7, 0.95):
        x = xth + pw * span * f
        y = oy - ph * 0.9 * f * f
        s += line(x, oy, x, y, GREEN, 1.3, "4 3")
        s += line(ox, y, x, y, GREEN, 1.3, "4 3")
        s += circle(x, y, 3, RED, RED, 1)
    s += text(ox + pw * 0.60, oy - ph * 0.52, "Id = ½·k·(Vgs − Vth)²", 13, RED, "middle", "bold")
    s += text(ox + pw * 0.60, oy - ph * 0.52 + 20, "рівні кроки Vgs →", 10, GREEN, "middle")
    s += text(ox + pw * 0.60, oy - ph * 0.52 + 35, "дедалі більші кроки Id", 10, GREEN, "middle")
    save("fig-12-3m-1-square-law.svg", s)


def fig123m_output_family():
    W, H = 600, 400
    s = header(W, H)
    s += text(W / 2, 30, "Звідки в даташиті сімейство кривих Id(Vds)", 15.5, INK, "middle", "bold")
    ox, oy, pw, ph = 80, 330, 400, 252
    s += _axes(ox, oy, pw, ph, "Vds", "Id")
    k = 1.0
    vovs = [1, 2, 3, 4]
    maxId = 0.5 * k * max(vovs) ** 2
    vdmax = 5.0
    cols = [BLUE, GREEN, SUN, RED]
    for idx, vov in enumerate(vovs):
        idsat = 0.5 * k * vov * vov
        pts = []
        for j in range(0, 101):
            vds = vdmax * j / 100.0
            Id = k * (vov * vds - 0.5 * vds * vds) if vds < vov else idsat
            x = ox + pw * (vds / vdmax)
            y = oy - ph * 0.92 * (Id / maxId)
            pts.append((x, y))
        s += _poly(pts, cols[idx], 2.6)
        ylab = oy - ph * 0.92 * (idsat / maxId)
        s += text(ox + pw + 6, ylab + 4, f"Vov={vov}", 10, cols[idx], "start", "bold")
        # позначка коліна (Vds = Vov)
        s += circle(ox + pw * (vov / vdmax), ylab, 3, cols[idx], "#ffffff", 1.6)
    s += text(ox + pw * 0.52, oy - ph - 2,
              "висота поличок росте як квадрат → проміжки нерівні", 10, INK, "middle", style="italic")
    s += text(ox + pw * 0.30, oy - ph * 0.20, "коліно: Vds = Vov", 9.5, GREY, "middle")
    save("fig-12-3m-2-output-family.svg", s)


# ── 🧮 вставка до 2.7.7: заряд затвора Qg (Рис. 2.7.7m.k) ────────────────────
def fig127m_gate_charge_curve():
    W, H = 580, 384
    s = header(W, H)
    s += text(W / 2, 28, "Крива заряду затвора: чому в даташиті — нанокулони", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 96, 300, 414, 230
    s += _axes(ox, oy, pw, ph, "Qg (нКл)", "Vgs")
    xQgs = ox + 0.30 * pw
    xPl2 = ox + 0.60 * pw
    xEnd = ox + 0.86 * pw
    yPlat = oy - 0.36 * ph
    yDrive = oy - 0.90 * ph
    s += _poly([(ox, oy), (xQgs, yPlat), (xPl2, yPlat), (xEnd, yDrive)], RED, 3)
    yth = oy - 0.24 * ph
    s += line(ox, yth, xEnd, yth, GREY, 1.3, "5 4") + text(ox - 6, yth + 4, "Vth", 11, GREY, "end")
    s += line(ox, yPlat, xPl2, yPlat, GREY, 1.2, "3 3") + text(ox - 6, yPlat + 4, "Vpl", 11, GREY, "end")
    s += line(ox, yDrive, xEnd, yDrive, GREY, 1.2, "3 3") + text(ox - 6, yDrive + 4, "Vdr", 11, GREY, "end")
    for xx in (xQgs, xPl2, xEnd):
        s += line(xx, oy, xx, oy + 6, INK, 1.4)

    def _brak(x0, x1, y, lab, col):
        t = line(x0, y, x1, y, col, 1.8)
        t += line(x0, y - 4, x0, y + 4, col, 1.8) + line(x1, y - 4, x1, y + 4, col, 1.8)
        t += text((x0 + x1) / 2, y + 15, lab, 10, col, "middle", "bold")
        return t
    s += _brak(ox, xQgs, oy + 22, "Qgs", BLUE)
    s += _brak(xQgs, xPl2, oy + 22, "Qgd (Міллер)", GREEN)
    s += _brak(ox, xEnd, oy + 46, "Qg (повний)", RED)
    s += text((xQgs + xPl2) / 2, yPlat - 10, "плато: Vds падає, Vgs стоїть", 9, GREEN, "middle")
    save("fig-12-7m-1-gate-charge-curve.svg", s)


def fig127m_nonlinear_cap():
    W, H = 580, 360
    s = header(W, H)
    s += text(W / 2, 28, "Ємність затвора не стала — тому беруть заряд, а не фаради", 14, INK, "middle", "bold")
    ox, oy, pw, ph = 92, 286, 418, 206
    s += _axes(ox, oy, pw, ph, "Vds", "C")
    ptsC, ptsI = [], []
    for j in range(1, 101):
        vds = 5.0 * j / 100.0
        crss = 1.0 / math.sqrt(vds + 0.05)
        x = ox + pw * (vds / 5.0)
        ptsC.append((x, oy - ph * 0.92 * min(crss, 5.0) / 5.0))
        ptsI.append((x, oy - ph * 0.92 * min(2.6 + 0.7 * crss, 5.0) / 5.0))
    s += _poly(ptsI, BLUE, 2.6)
    s += _poly(ptsC, RED, 2.6)
    s += text(ox + pw * 0.46, 150, "Ciss (вхідна)", 10, BLUE, "start", "bold")
    s += text(ox + pw * 0.20, 212, "Crss (Міллерова)", 10, RED, "start", "bold")
    s += text(W / 2, H - 30, "Біля малих Vds Crss різко зростає — звідси й Міллерове плато.", 9.5, INK, "middle")
    s += text(W / 2, H - 14, "Одне число C не годиться; інтеграл ∫C·dV дає зручний Qg (нКл).", 9.5, INK, "middle", style="italic")
    save("fig-12-7m-2-nonlinear-cap.svg", s)


# ── 🔌 вставка до 2.7.2: паразитний body-діод (Рис. 2.7.2c.k) ────────────────
def fig122c_body_diode():
    W, H = 500, 332
    s = header(W, H)
    s += text(W / 2, 28, "Вбудований body-діод: перехід тіло–стік", 16, INK, "middle", "bold")
    cx, cy = 170, 175
    s += _mosfet_sym(cx, cy)
    s += text(cx + 24, cy - 54, "стік", 10.5, INK, "middle", "bold")
    s += text(cx + 24, cy + 62, "витік", 10.5, INK, "middle", "bold")
    s += text(cx - 50, cy - 8, "затвор", 10, INK, "end")
    # тіло з'єднане з витоком
    s += text(cx + 6, cy + 40, "тіло↔витік", 8.5, GREY, "middle")
    # body-діод: вертикальний, катод (риска) угорі = стік
    dx = cx + 80
    s += line(cx + 24, cy - 44, dx, cy - 44, INK, 1.8) + line(dx, cy - 44, dx, cy - 12, INK, 1.8)
    s += line(cx + 24, cy + 44, dx, cy + 44, INK, 1.8) + line(dx, cy + 44, dx, cy + 12, INK, 1.8)
    s += f'<path d="M {dx-11},{cy+12} L {dx+11},{cy+12} L {dx:.0f},{cy-10} Z" fill="#fbecec" stroke="{INK}" stroke-width="1.6"/>\n'
    s += line(dx - 13, cy - 12, dx + 13, cy - 12, INK, 2.6)
    s += text(dx + 18, cy - 2, "body-", 10.5, RED, "start", "bold")
    s += text(dx + 18, cy + 12, "діод", 10.5, RED, "start", "bold")
    s += arrow(dx + 46, cy + 30, dx + 46, cy - 26, BLUE, 2)
    s += text(dx + 52, cy + 4, "тече", 9, BLUE, "start")
    s += text(W / 2, H - 38, "Тіло (p) з'єднане з витоком; між тілом і стоком — p-n перехід.", 10, INK, "middle")
    s += text(W / 2, H - 20, "Він проводить, коли стік стає мінусовим відносно витоку (Vds < 0).", 10, INK, "middle", style="italic")
    save("fig-12-2c-1-body-diode.svg", s)


def fig122c_reverse_block():
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 26, "Хиба body-діода: один ключ не тримає зворотний струм", 15, INK, "middle", "bold")
    midy = 150

    def _offbox(x, lab="OFF"):
        return rect(x, midy - 20, 54, 40, "#f0f1f2", "#b8bcc0", 2, 5) + text(x + 27, midy + 4, lab, 10.5, GREY, "middle", "bold")
    # ── лівий: один ключ протікає ──
    s += _frame(30, 50, 300, 252, "один ключ — протікає")
    s += _offbox(150)
    s += line(70, midy, 150, midy, INK, 2) + line(204, midy, 300, midy, INK, 2)
    s += text(64, midy + 4, "вхід", 10, INK, "end") + text(308, midy + 4, "вузол", 10, INK, "start")
    # нижня вітка з діодом (провідний назад)
    s += line(110, midy, 110, midy + 56, INK, 1.7) + line(244, midy, 244, midy + 56, INK, 1.7)
    s += line(110, midy + 56, 244, midy + 56, INK, 1.7)
    s += _diode_h(177, midy + 56, 12, right=False, col=RED)
    s += arrow(250, midy + 80, 104, midy + 80, RED, 2)
    s += text(177, midy + 100, "струм тече назад крізь діод", 9, RED, "middle", "bold")
    # ── правий: два спина-до-спини тримають ──
    s += _frame(390, 50, 300, 252, "два спина-до-спини — тримає")
    s += _offbox(470) + _offbox(566)
    s += line(410, midy, 470, midy, INK, 2) + line(524, midy, 566, midy, INK, 2) + line(620, midy, 660, midy, INK, 2)
    s += text(524, midy - 28, "спільний витік", 8.5, INK, "middle")
    # два діоди, що дивляться навстріч
    s += line(440, midy, 440, midy + 56, INK, 1.7) + line(524, midy, 524, midy + 56, INK, 1.7)
    s += line(440, midy + 56, 524, midy + 56, INK, 1.7)
    s += _diode_h(482, midy + 56, 11, right=True, col=INK)
    s += line(566, midy, 566, midy + 56, INK, 1.7) + line(650, midy, 650, midy + 56, INK, 1.7)
    s += line(566, midy + 56, 650, midy + 56, INK, 1.7)
    s += _diode_h(608, midy + 56, 11, right=False, col=INK)
    s += text(545, midy + 80, "✗", 16, GREEN, "middle", "bold")
    s += text(545, midy + 100, "два діоди навстріч — глухо в обидва боки", 9, GREEN, "middle", "bold")
    save("fig-12-2c-2-reverse-block.svg", s)


# ── 🔌 вставка до 2.7.4: P-канальний load switch (Рис. 2.7.4c.k) ─────────────
def fig124c_load_switch():
    W, H = 740, 410
    s = header(W, H)
    s += text(W / 2, 28, "Високобічний ключ живлення на P-MOSFET", 16, INK, "middle", "bold")
    vY, gY = 70, 366
    s += line(110, vY, 540, vY, RED, 2) + text(104, vY + 4, "+Vin", 10.5, RED, "end", "bold")
    s += line(110, gY, 540, gY, INK, 1.6) + text(454, gY + 16, "GND", 9.5, INK, "middle", "bold")
    # головний P-MOS
    pcx, pcy = 430, 176
    s += _mosfet_sym(pcx, pcy, pch=True)
    s += line(pcx + 24, pcy - 44, pcx + 24, vY, INK, 2)
    s += line(pcx + 24, pcy + 44, pcx + 24, 262, INK, 2)
    s += text(pcx + 34, pcy - 30, "S", 10, INK, "start", "bold")
    s += text(pcx + 34, pcy + 36, "D", 10, INK, "start", "bold")
    s += text(pcx + 44, pcy - 52, "P-MOS", 10, RED, "start", "bold")
    # навантаження
    s += rect(pcx, 262, 48, 46, "#ffffff", INK, 1.6)
    s += text(pcx + 24, 286, "наван-", 9, INK, "middle") + text(pcx + 24, 299, "таження", 9, INK, "middle")
    s += line(pcx + 24, 308, pcx + 24, gY, INK, 2)
    # вузол затвора + підтяжка до витоку
    gnx = 340
    s += line(pcx - 44, pcy, gnx, pcy, INK, 2) + circle(gnx, pcy, 3, INK, INK)
    s += text(gnx - 6, pcy - 10, "G", 10, INK, "end", "bold")
    s += line(gnx, 120, gnx, pcy, INK, 2)
    s += rect(gnx - 14, 96, 28, 24, "#ffffff", INK, 1.6) + text(gnx, 112, "Rпу", 9, INK, "middle", "bold")
    s += line(gnx, 96, gnx, vY, INK, 2)
    # драйвер n-ключ Q2
    qcx, qcy = 316, 278
    s += _mosfet_sym(qcx, qcy, pch=False)
    s += line(gnx, pcy, gnx, qcy - 44, INK, 2)
    s += line(qcx + 24, qcy + 44, qcx + 24, gY, INK, 2)
    s += text(qcx + 34, qcy + 36, "Q2", 10, INK, "start", "bold")
    s += text(qcx + 30, qcy - 50, "n-ключ", 9, INK, "start")
    # логічний вхід → затвор Q2
    s += rect(118, qcy - 22, 84, 44, LBLUE, "#9bb0c2", 1.4, 6) + text(160, qcy + 4, "лог. вхід", 10, INK, "middle", "bold")
    s += line(202, qcy, qcx - 44, qcy, INK, 2)
    s += text(W / 2, H - 14, "лог. 1 → Q2 відкрив → затвор P-MOS донизу → P-MOS відкрив (Vgs ≈ −Vin) → живлення є.",
              10, GREEN, "middle", "bold")
    save("fig-12-4c-1-load-switch.svg", s)


def fig124c_gate_limit():
    W, H = 700, 296
    s = header(W, H)
    s += text(W / 2, 26, "Високе Vin: затвор P-MOS треба берегти", 15.5, INK, "middle", "bold")
    s += _frame(30, 50, 300, 218, "небезпека: Vin = 24 В")
    s += text(180, 92, "затвор тягнемо до 0 В", 10, INK, "middle")
    s += text(180, 118, "Vgs = 0 − 24 = −24 В", 12.5, RED, "middle", "bold")
    s += text(180, 146, "межа затвора ≈ ±20 В", 10, INK, "middle")
    s += text(180, 178, "✗ пробій оксиду затвора", 11, RED, "middle", "bold")
    s += text(180, 204, "(тонкий ізолятор §2.7.2)", 9, GREY, "middle")
    s += _frame(370, 50, 300, 218, "захист: обмежити Vgs")
    s += text(520, 90, "стабілітрон З↔В або", 10, GREEN, "middle", "bold")
    s += text(520, 108, "дільник у колі затвора", 10, GREEN, "middle", "bold")
    s += text(520, 138, "тримають |Vgs| ≈ 10–12 В", 11, INK, "middle")
    s += text(520, 172, "✓ затвор цілий,", 11, GREEN, "middle", "bold")
    s += text(520, 190, "P-MOS усе одно повністю відкритий", 9.5, INK, "middle")
    s += text(520, 216, "(досить ~10 В перевищення)", 9, GREY, "middle")
    save("fig-12-4c-2-gate-limit.svg", s)


# ── 🔌 вставка до 2.7.6: logic-level MOSFET (Рис. 2.7.6c.k) ──────────────────
def fig126c_rds_vs_vgs():
    W, H = 600, 394
    s = header(W, H)
    s += text(W / 2, 28, "Опір відкритого каналу залежить від напруги затвора", 14.5, INK, "middle", "bold")
    ox, oy, pw, ph = 84, 322, 436, 250
    s += _axes(ox, oy, pw, ph, "Vgs (В)", "Rds(on)")
    vmax = 8.0

    def curve(vth, a, col):
        pts = []
        for j in range(0, 161):
            vgs = vmax * j / 160.0
            ov = vgs - vth
            R = 1.0 if ov <= a else max(0.05, min(1.0, a / ov))
            pts.append((ox + pw * (vgs / vmax), oy - ph * 0.9 * R))
        return _poly(pts, col, 2.8)
    s += curve(3.8, 1.6, RED)
    s += curve(1.3, 0.5, GREEN)
    s += text(ox + pw * 0.82, oy - ph * 0.62, "звичайний", 10.5, RED, "middle", "bold")
    s += text(ox + pw * 0.58, oy - ph * 0.22, "логічного", 10.5, GREEN, "middle", "bold")
    s += text(ox + pw * 0.58, oy - ph * 0.22 + 15, "рівня", 10.5, GREEN, "middle", "bold")
    for v, lab in ((3.3, "3.3 В"), (5.0, "5 В")):
        x = ox + pw * (v / vmax)
        s += line(x, oy, x, oy - ph * 0.96, BLUE, 1.3, "5 4")
        s += text(x, oy + 18, lab, 10, BLUE, "middle", "bold")
    s += text(W / 2, H - 26, "При 5 В логічний уже холодний (малий Rds), а звичайний — ледь прочинений і гарячий.", 9.5, INK, "middle")
    s += text(W / 2, H - 10, "Дивись у даташиті Rds(on) саме при ТВОЇЙ Vgs.", 9.5, INK, "middle", style="italic")
    save("fig-12-6c-1-rds-vs-vgs.svg", s)


def fig126c_families():
    W, H = 690, 296
    s = header(W, H)
    s += text(W / 2, 28, "Три класи: чи відкриється від твоєї логіки", 15.5, INK, "middle", "bold")
    y0, rh = 54, 54
    s += rect(40, y0, 610, 34, "#eef2f7", "#7f93a8", 1.6, 6)
    s += text(60, y0 + 22, "клас приладу", 11, INK, "start", "bold")
    s += text(430, y0 + 22, "повне Vgs", 10.5, INK, "middle", "bold")
    s += text(515, y0 + 22, "від 3.3 В", 10.5, INK, "middle", "bold")
    s += text(605, y0 + 22, "від 5 В", 10.5, INK, "middle", "bold")
    rows = [
        ("звичайний (IRF540-клас)", "≈10 В", ("✗", RED), ("✗", RED)),
        ("лог. рівня, потужний (IRLZ44-клас)", "≈4.5 В", ("△", SUN), ("✓", GREEN)),
        ("лог. рівня, дрібний (AO3400-клас)", "≈2.5 В", ("✓", GREEN), ("✓", GREEN)),
    ]
    for i, (name, vg, c33, c5) in enumerate(rows):
        ry = y0 + 34 + i * rh
        s += rect(40, ry, 610, rh, "#ffffff", "#c9d3dc", 1.2, 0)
        s += text(60, ry + rh / 2 + 5, name, 10.5, INK, "start", "bold")
        s += text(430, ry + rh / 2 + 5, vg, 11, INK, "middle")
        s += text(515, ry + rh / 2 + 7, c33[0], 15, c33[1], "middle", "bold")
        s += text(605, ry + rh / 2 + 7, c5[0], 15, c5[1], "middle", "bold")
    s += text(W / 2, H - 12, "△ — відкриється, але перевір Rds(on) при 3.3 В: деякі «логічні» все одно хочуть ~4.5 В.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-6c-2-families.svg", s)


# ── 🔌 вставка до 2.7.6: «ідеальний діод» (Рис. 2.7.6c.3–4) ──────────────────
def fig126c_ideal_vs_diode():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Захист від переполярності: діод vs «ідеальний діод»", 15, INK, "middle", "bold")
    # лівий: Шотткі
    s += _frame(30, 50, 300, 224, "звичайний діод (Шотткі)")
    s += line(70, 116, 120, 116, RED, 2) + text(64, 120, "+V", 9, RED, "end", "bold")
    s += _diode_h(140, 116, 14, right=True, col=INK)
    s += line(160, 116, 228, 116, INK, 2)
    s += rect(228, 98, 58, 36, "#ffffff", INK, 1.6) + text(257, 120, "наван.", 9, INK, "middle")
    s += text(178, 150, "I = 3 A", 10, INK, "middle")
    s += rect(58, 176, 244, 80, LRED, "#d8a0a0", 1.3, 6)
    s += text(180, 200, "падіння ≈ 0.4 В", 11, RED, "middle", "bold")
    s += text(180, 222, "втрати = 0.4 × 3 = 1.2 Вт", 11, RED, "middle", "bold")
    s += text(180, 244, "гарячий, ще й крав напругу", 9.5, INK, "middle")
    # правий: MOSFET
    s += _frame(370, 50, 300, 224, "ідеальний діод (MOSFET)")
    s += line(410, 116, 466, 116, RED, 2) + text(404, 120, "+V", 9, RED, "end", "bold")
    s += rect(466, 99, 60, 34, "#eef6ef", GREEN, 1.8, 5) + text(496, 120, "MOSFET", 8.5, INK, "middle", "bold")
    s += line(526, 116, 588, 116, INK, 2)
    s += rect(588, 98, 58, 36, "#ffffff", INK, 1.6) + text(617, 120, "наван.", 9, INK, "middle")
    s += text(496, 150, "Rds(on) ≈ 20 мОм", 10, INK, "middle")
    s += rect(398, 176, 244, 80, LGRN, GREEN, 1.3, 6)
    s += text(520, 200, "падіння = 3 × 0.02 = 0.06 В", 11, GREEN, "middle", "bold")
    s += text(520, 222, "втрати = 0.06 × 3 ≈ 0.18 Вт", 11, GREEN, "middle", "bold")
    s += text(520, 244, "холодний, майже без втрат", 9.5, INK, "middle")
    save("fig-12-6c-3-ideal-vs-diode.svg", s)


def fig126c_reverse_protect():
    W, H = 700, 332
    s = header(W, H)
    s += text(W / 2, 26, "P-MOS як захист: правильно — відкритий, навпаки — закритий", 14.5, INK, "middle", "bold")

    def panel(ox, title, good):
        t = _frame(ox, 50, 300, 250, title)
        cx, cy = ox + 140, 150
        t += _mosfet_sym(cx, cy, pch=True)
        t += line(cx + 24, cy - 44, cx + 24, 78, RED if good else BLUE, 2)
        t += line(cx - 44, cy, cx - 90, cy, INK, 2) + circle(cx - 90, cy, 3, INK, INK)
        t += line(cx - 90, cy, cx - 90, 252, INK, 1.6)
        t += rect(cx - 104, 196, 28, 24, "#ffffff", INK, 1.4) + text(cx - 90, 212, "Rз", 8.5, INK, "middle", "bold")
        t += text(cx - 86, cy - 6, "затвор", 8.5, INK, "start")
        if good:
            t += text(cx + 24, 70, "+12 В", 9.5, RED, "middle", "bold")
            t += text(cx + 58, cy, "Vgs = −12", 9.5, GREEN, "start", "bold")
            t += arrow(cx + 24, cy + 50, cx + 24, cy + 84, GREEN, 2.2)
            t += text(cx + 24, 288, "ВІДКРИТО → струм, падіння крихітне", 9.5, GREEN, "middle", "bold")
        else:
            t += text(cx + 24, 70, "−12 В", 9.5, BLUE, "middle", "bold")
            t += text(cx + 58, cy, "Vgs = +12", 9.5, RED, "start", "bold")
            t += text(cx + 24, cy + 66, "✗", 16, RED, "middle", "bold")
            t += text(cx + 24, 288, "ЗАКРИТО + body-діод блокує", 9.5, RED, "middle", "bold")
        return t
    s += panel(30, "правильна полярність", True)
    s += panel(370, "переплутана полярність", False)
    save("fig-12-6c-4-reverse-protect.svg", s)


# ── 🔌 вставка до 2.7.7: драйвер затвора (Рис. 2.7.7c.k) ─────────────────────
def fig127c_push_pull():
    W, H = 700, 322
    s = header(W, H)
    s += text(W / 2, 28, "Драйвер затвора зсередини: тотемний вихід", 16, INK, "middle", "bold")
    s += rect(28, 130, 98, 58, LBLUE, "#9bb0c2", 1.4, 6)
    s += text(77, 156, "лог. вхід", 10, INK, "middle", "bold") + text(77, 174, "(мА)", 9, GREY, "middle")
    s += arrow(126, 159, 198, 159, INK, 2)
    s += _frame(198, 68, 286, 214, "драйвер")
    vdy, gndy, nodex, nody = 96, 256, 340, 172
    s += line(244, vdy, 440, vdy, RED, 2) + text(340, vdy - 8, "Vdrive (10–12 В)", 10, RED, "middle", "bold")
    s += line(244, gndy, 440, gndy, INK, 1.6) + text(340, gndy + 16, "GND", 9, INK, "middle")
    s += rect(nodex - 30, vdy + 14, 60, 34, "#eef6ef", GREEN, 1.8, 5) + text(nodex, vdy + 35, "верх", 10, INK, "middle", "bold")
    s += line(nodex, vdy, nodex, vdy + 14, INK, 2) + line(nodex, vdy + 48, nodex, nody, INK, 2)
    s += rect(nodex - 30, nody + 18, 60, 34, "#e9eefb", BLUE, 1.8, 5) + text(nodex, nody + 39, "низ", 10, INK, "middle", "bold")
    s += line(nodex, nody, nodex, nody + 18, INK, 2) + line(nodex, nody + 52, nodex, gndy, INK, 2)
    s += circle(nodex, nody, 3, INK, INK)
    s += line(nodex, nody, 502, nody, INK, 2)
    s += rect(502, nody - 12, 42, 24, "#ffffff", INK, 1.6) + text(523, nody + 5, "Rg", 9, INK, "middle", "bold")
    s += line(544, nody, 598, nody, INK, 2)
    s += rect(598, nody - 26, 74, 52, "#fff7e6", COPP, 1.4, 6)
    s += text(635, nody - 4, "затвор", 9, INK, "middle", "bold") + text(635, nody + 13, "MOSFET", 8.5, INK, "middle")
    s += text(nodex + 40, vdy + 34, "наповнює ↑", 8.5, GREEN, "start", "bold")
    s += text(nodex + 40, nody + 40, "спорожняє ↓", 8.5, BLUE, "start", "bold")
    s += text(W / 2, H - 12, "Вхід вибирає: верхній ключ ллє в затвор ампери з Vdrive, нижній — зливає в землю. МК так не вміє.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-7c-1-push-pull.svg", s)


def fig127c_bootstrap():
    W, H = 720, 392
    s = header(W, H)
    s += text(W / 2, 24, "Верхній N-ключ: бутстреп дає «плаваюче» живлення затвора", 14, INK, "middle", "bold")
    busY, gndY = 66, 350
    s += line(360, busY, 680, busY, RED, 2) + text(520, busY - 8, "+Vbus (висока напруга)", 10, RED, "middle", "bold")
    s += line(220, gndY, 680, gndY, INK, 1.6) + text(656, gndY + 15, "GND", 9, INK, "middle")
    # Q_верх / Q_низ
    s += rect(526, 96, 68, 48, "#eef2f7", "#7f93a8", 1.8, 6) + text(560, 116, "Q_верх", 9.5, INK, "middle", "bold") + text(560, 132, "(N)", 8.5, GREY, "middle")
    s += line(560, busY, 560, 96, INK, 2) + line(560, 144, 560, 206, INK, 2)
    s += circle(560, 206, 3, INK, INK) + text(572, 201, "SW", 9, INK, "start", "bold")
    s += rect(526, 240, 68, 48, "#eef2f7", "#7f93a8", 1.8, 6) + text(560, 260, "Q_низ", 9.5, INK, "middle", "bold") + text(560, 276, "(N)", 8.5, GREY, "middle")
    s += line(560, 206, 560, 240, INK, 2) + line(560, 288, 560, gndY, INK, 2)
    # навантаження від SW
    s += line(560, 206, 620, 206, INK, 2)
    s += rect(620, 182, 60, 48, "#ffffff", INK, 1.6) + text(650, 202, "наван-", 8.5, INK, "middle") + text(650, 216, "таження", 8.5, INK, "middle")
    s += line(650, 230, 650, gndY, INK, 2)
    # Vdrive + бутстреп
    s += line(150, 150, 286, 150, RED, 2) + text(150, 142, "Vdrive 12 В", 9.5, RED, "start", "bold")
    s += _diode_h(312, 150, 12, right=True, col=INK) + text(312, 134, "Dbs", 8.5, INK, "middle", "bold")
    s += line(330, 150, 430, 150, INK, 2) + circle(430, 150, 3, INK, INK) + text(430, 138, "VB", 9, INK, "middle", "bold")
    # Cbs: VB -> SW
    s += line(430, 150, 430, 180, INK, 2)
    s += line(414, 184, 446, 184, INK, 2.6) + line(414, 192, 446, 192, INK, 2.6)
    s += text(458, 190, "Cbs", 8.5, INK, "start", "bold")
    s += line(430, 196, 430, 206, INK, 2) + line(430, 206, 560, 206, INK, 2)
    # HO до затвора Q_верх (від VB)
    s += line(430, 150, 430, 120, INK, 1.8) + line(430, 120, 526, 120, INK, 1.8)
    s += text(478, 112, "HO (від VB)", 8.5, GREEN, "middle", "bold")
    s += text(526, 264, "← LO (від Vdrive)", 8.5, BLUE, "end")
    # пояснення циклу
    s += rect(40, 300, 300, 76, "#f6f8fb", "#c9d3dc", 1.2, 6)
    s += text(190, 320, "Q_низ ON → SW≈0 →", 9.5, INK, "middle", "bold")
    s += text(190, 336, "Cbs заряджається від Vdrive крізь Dbs.", 9, INK, "middle")
    s += text(190, 356, "Q_верх ON → SW↑ до Vbus →", 9.5, INK, "middle", "bold")
    s += text(190, 372, "Cbs підіймає VB над шиною: є чим тримати затвор.", 8.5, INK, "middle")
    save("fig-12-7c-2-bootstrap.svg", s)


# ── ⚙️ вставка до 2.7.6: тепловий розрахунок (Рис. 2.7.6a.k) ─────────────────
def fig126a_thermal_ohm():
    W, H = 580, 424
    s = header(W, H)
    s += text(W / 2, 28, "Тепловий закон Ома: тепло тече, як струм", 16, INK, "middle", "bold")
    cx = 180
    nodes = [("кристал (Tj)", 72, LRED), ("корпус", 168, "#fff3e0"),
             ("радіатор", 264, LBLUE), ("повітря (Tamb)", 360, LGRN)]
    for lab, y, col in nodes:
        s += rect(cx - 84, y - 18, 168, 36, col, INK, 1.4, 6) + text(cx, y + 5, lab, 11, INK, "middle", "bold")
    thetas = [("θJC", 120), ("θCS", 216), ("θSA", 312)]
    for lab, y in thetas:
        s += line(cx, y - 22, cx, y - 14, INK, 1.6) + line(cx, y + 14, cx, y + 22, INK, 1.6)
        s += rect(cx - 16, y - 14, 32, 28, "#ffffff", INK, 1.6) + text(cx + 44, y + 5, lab, 11, INK, "start", "bold")
    s += arrow(cx - 116, 80, cx - 116, 352, RED, 2.4) + text(cx - 122, 220, "P (тепло)", 10, RED, "end", "bold")
    # аналогія
    s += _frame(372, 92, 188, 250, "як коло")
    s += text(466, 132, "P  ↔  струм I", 12, INK, "middle", "bold")
    s += text(466, 168, "θ  ↔  опір (°C/Вт)", 10.5, INK, "middle")
    s += text(466, 200, "ΔT ↔  напруга", 10.5, INK, "middle")
    s += rect(388, 228, 156, 86, "#f6f8fb", "#c9d3dc", 1.2, 6)
    s += text(466, 256, "ΔT = P × θ", 13, RED, "middle", "bold")
    s += text(466, 284, "Tj = Tamb", 11.5, INK, "middle", "bold")
    s += text(466, 302, "+ P · Σθ", 11.5, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Більше тепла (P) чи більший тепловий опір (θ) — гарячіший кристал. Радіатор зменшує θ.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-6a-1-thermal-ohm.svg", s)


def fig126a_verdict():
    W, H = 600, 362
    s = header(W, H)
    s += text(W / 2, 28, "Вердикт: чи треба радіатор (приклад 5 А)", 15.5, INK, "middle", "bold")
    ox, oy, ph = 120, 300, 232

    def yT(T):
        return oy - ph * (T - 25) / (160 - 25)
    s += line(ox - 10, oy, 540, oy, INK, 1.6) + text(ox - 14, oy + 4, "25°", 9, INK, "end")
    s += line(ox - 10, yT(150), 540, yT(150), RED, 1.6, "6 4") + text(544, yT(150) + 4, "150° межа", 9, RED, "start", "bold")
    s += line(ox - 10, yT(120), 540, yT(120), SUN, 1.4, "4 4") + text(544, yT(120) + 4, "120° запас", 8.5, SUN, "start")
    bars = [("без радіатора", 210, 115, RED, "P=1.5 Вт · θJA=60"), ("з радіатором", 370, 55, GREEN, "θ≈20")]
    for lab, bx, Tj, col, note in bars:
        yb = yT(Tj)
        fill = LGRN if col == GREEN else LRED
        s += rect(bx, yb, 96, oy - yb, fill, col, 1.8, 4)
        s += text(bx + 48, yb - 8, f"Tj≈{Tj}°", 11.5, col, "middle", "bold")
        s += text(bx + 48, oy + 16, lab, 10, INK, "middle", "bold")
        s += text(bx + 48, oy + 30, note, 8.5, GREY, "middle")
    s += text(W / 2, H - 10, "Без радіатора — впритул до запасу (гаряче); радіатор зрізає θ, кристал холодний. Rds(on) бери ГАРЯЧИМ.",
              9, INK, "middle", style="italic")
    save("fig-12-6a-2-verdict.svg", s)


# ── ⚙️ вставка до 2.7.10: наскрізний струм і мертвий час (Рис. 2.7.10a.k) ────
def fig1210a_deadtime_timing():
    W, H = 720, 356
    s = header(W, H)
    s += text(W / 2, 26, "Комплементарний ШІМ із мертвим часом", 16, INK, "middle", "bold")
    ox, x1 = 110, 660
    rows = [("ШІМ", 92), ("HO (верх)", 178), ("LO (низ)", 264)]
    # смуги мертвого часу (позаду)
    for xa, xb in [(250, 282), (470, 502)]:
        s += rect(xa, 64, xb - xa, 232, "#fdeeee", "none", 0, 0)
    for lab, y in rows:
        s += text(ox - 12, y + 4, lab, 10.5, INK, "end", "bold")

    def sq(y, pts, col):
        return _poly([(x, (y - 16) if hi else (y + 16)) for x, hi in pts], col, 2.6)
    s += sq(92, [(ox, False), (250, False), (250, True), (470, True), (470, False), (x1, False)], BLUE)
    s += sq(178, [(ox, False), (282, False), (282, True), (470, True), (470, False), (x1, False)], GREEN)
    s += sq(264, [(ox, True), (250, True), (250, False), (502, False), (502, True), (x1, True)], RED)
    for xc in (266, 486):
        s += text(xc, 58, "мертвий час", 8.5, RED, "middle", "bold")
        s += text(xc, 312, "обидва закриті", 8, INK, "middle")
    s += text(W / 2, H - 12, "На кожному фронті ШІМ спершу ЗАКРИВАЮТЬ один ключ, чекають паузу, аж тоді відкривають інший.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-10a-1-deadtime-timing.svg", s)


def fig1210a_tradeoff():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Мертвий час: замало небезпечно, забагато марнотратно", 15, INK, "middle", "bold")
    bx, by, bw = 80, 150, 540
    s += rect(bx, by, bw * 0.30, 42, "#fdeeee", "none", 0, 0)
    s += rect(bx + bw * 0.30, by, bw * 0.40, 42, "#eef6ef", "none", 0, 0)
    s += rect(bx + bw * 0.70, by, bw * 0.30, 42, "#fff3e0", "none", 0, 0)
    s += rect(bx, by, bw, 42, "none", INK, 1.4, 8)
    s += text(bx + bw * 0.15, by + 26, "ЗАМАЛО", 11, RED, "middle", "bold")
    s += text(bx + bw * 0.50, by + 26, "ЯКРАЗ", 11, GREEN, "middle", "bold")
    s += text(bx + bw * 0.85, by + 26, "ЗАБАГАТО", 11, SUN, "middle", "bold")
    s += arrow(bx, by + 60, bx + bw, by + 60, INK, 1.6) + text(bx + bw + 6, by + 64, "мертвий час", 9, INK, "start", "bold")
    s += text(bx + bw * 0.15, by - 18, "обидва прочинені →", 8.5, RED, "middle")
    s += text(bx + bw * 0.15, by - 5, "наскрізний струм (вибух)", 8.5, RED, "middle", "bold")
    s += text(bx + bw * 0.50, by - 10, "трохи більше за час вимикання", 8.5, GREEN, "middle", "bold")
    s += text(bx + bw * 0.85, by - 18, "довга пауза →", 8.5, SUN, "middle")
    s += text(bx + bw * 0.85, by - 5, "body-діод гріється, спотворення", 8.5, INK, "middle")
    s += text(W / 2, H - 30, "Правило: мертвий час трохи довший за найгірший час вимикання ключа (Qg, Rg, темп.).",
              9.5, INK, "middle")
    s += text(W / 2, H - 14, "На практиці — апаратний комплементарний ШІМ із програмованим мертвим часом, не дві ніжки вручну.",
              9, GREY, "middle", style="italic")
    save("fig-12-10a-2-tradeoff.svg", s)


# ── 📜 історія до §2.7.5: HEXFET (Рис. 2.7.5і.k) ─────────────────────────────
def _polyfill(pts, fill, stroke=INK, w=1.4):
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def fig125i_timeline():
    W, H = 968, 252
    s = header(W, H)
    s += text(W / 2, 30, "Шлях до масового силового MOSFET: 1959 → 1979", 17, INK, "middle", "bold")
    items = [
        (18, "1959", ["планарний MOSFET", "(Аттала, Кан) —", "заслабкий для сили"], "#fdf1dc"),
        (172, "1969", ["Hitachi VMOS", "(Японія):", "вертикальний"], LBLUE),
        (326, "1973", ["Роджерс,", "Стенфорд:", "патент VMOS"], LBLUE),
        (480, "1975", ["Siliconix:", "VMOS у", "продажу"], LBLUE),
        (634, "1977", ["HEXFET:", "Лідов і Герман,", "Стенфорд"], LGRN),
        (788, "1979", ["International", "Rectifier:", "масовий випуск"], LGRN),
    ]
    bw, by, bh = 142, 88, 110
    for bx, yr, lines, fill in items:
        s += text(bx + bw / 2, by - 8, yr, 12, INK, "middle", "bold")
        s += rect(bx, by, bw, bh, fill, "#9bb0c2", 1.5, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 30 + k * 22, ln, 10.5, INK, "middle")
    for i in range(len(items) - 1):
        s += arrow(items[i][0] + bw + 1, by + bh / 2, items[i + 1][0] - 1, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14, "Ідея вертикального силового ключа визрівала в кількох місцях; HEXFET зробив його дешевим і масовим.",
              10, GREY, "middle", style="italic")
    save("fig-12-5i-1-timeline.svg", s)


def fig125i_planar_vs_vertical():
    W, H = 720, 344
    s = header(W, H)
    s += text(W / 2, 28, "Чому для потужності — вертикально й комірками", 15.5, INK, "middle", "bold")
    # ліворуч: планарний
    s += _frame(28, 52, 312, 250, "планарний: струм по поверхні")
    s += rect(60, 150, 248, 110, "#eef2f7", "#9bb0c2", 1.4, 4)
    for lab, x in [("S", 90), ("G", 184), ("D", 278)]:
        s += rect(x - 18, 130, 36, 22, "#fff", INK, 1.4, 3) + text(x, 145, lab, 10, INK, "middle", "bold")
        s += line(x, 152, x, 150, INK, 1.4)
    s += arrow(96, 176, 272, 176, BLUE, 2.2) + text(184, 198, "довгий шлях по поверхні", 9.5, BLUE, "middle", "bold")
    s += text(184, 232, "великий опір, малий струм", 9.5, INK, "middle")
    s += text(184, 252, "— не для потужності", 9, GREY, "middle")
    # праворуч: вертикальний комірковий
    s += _frame(380, 52, 312, 250, "вертикальний: струм крізь кристал")
    s += rect(412, 110, 248, 120, "#eef2f7", "#9bb0c2", 1.4, 4)
    s += rect(412, 230, 248, 22, "#f4dcc4", COPP, 1.4, 0) + text(536, 245, "D (стік) — уся спина", 9, INK, "middle", "bold")
    for x in (452, 508, 564, 620):
        s += rect(x - 14, 90, 28, 20, "#fff", INK, 1.2, 3) + text(x, 104, "S", 8.5, INK, "middle", "bold")
        s += arrow(x, 130, x, 226, GREEN, 2)
    s += text(536, 285, "багато комірок паралельно → малий Rds(on), великий струм", 9, GREEN, "middle", "bold")
    save("fig-12-5i-2-planar-vs-vertical.svg", s)


def fig125i_hexcells():
    W, H = 640, 372
    s = header(W, H)
    s += text(W / 2, 30, "Підпис HEXFET: стільник із тисяч паралельних комірок", 14.5, INK, "middle", "bold")
    R = 33
    ox, oy = 116, 112
    sqrt3 = math.sqrt(3)
    for c in range(6):
        for r in range(4):
            cx = ox + c * 1.5 * R
            cy = oy + r * sqrt3 * R + (c % 2) * (sqrt3 / 2 * R)
            pts = [(cx + R * math.cos(math.radians(60 * k)), cy + R * math.sin(math.radians(60 * k))) for k in range(6)]
            hot = (c == 2 and r == 1)
            s += _polyfill(pts, LGRN if hot else "#f3f6f3", GREEN if hot else "#8fb39a", 1.8 if hot else 1.2)
            if hot:
                s += circle(cx, cy, 4, INK, INK)
    # виноска до підсвіченої комірки
    hx, hy = ox + 2 * 1.5 * R, oy + 1 * sqrt3 * R + 0
    s += arrow(hx + 30, hy - 40, hx + 6, hy - 6, INK, 1.6)
    s += rect(430, 96, 192, 196, "#f6f8fb", "#c9d3dc", 1.2, 6)
    s += text(526, 122, "одна комірка —", 10.5, INK, "middle", "bold")
    s += text(526, 140, "крихітний MOSFET", 10.5, INK, "middle", "bold")
    s += text(526, 168, "усі з'єднані", 9.5, INK, "middle")
    s += text(526, 184, "паралельно", 9.5, INK, "middle")
    s += text(526, 212, "паралельні опори", 9.5, GREEN, "middle", "bold")
    s += text(526, 228, "складаються в один", 9.5, GREEN, "middle")
    s += text(526, 244, "дуже малий Rds(on)", 9.5, GREEN, "middle", "bold")
    s += text(526, 272, "що щільніше — то", 9, GREY, "middle")
    s += text(526, 286, "менший опір", 9, GREY, "middle")
    save("fig-12-5i-3-hexcells.svg", s)


def fig125i_lidow_journey():
    W, H = 860, 244
    s = header(W, H)
    s += text(W / 2, 30, "Шлях Еріка Лідова — засновника International Rectifier", 16, INK, "middle", "bold")
    stops = [
        (24, "1912 · Вільнюс", ["народився в", "єврейській родині;", "тоді Рос. імперія,", "нині столиця Литви"], "#fdf1dc"),
        (236, "Берлін", ["навчання, магістр", "Технічного унів.", "1937"], LBLUE),
        (448, "1937 · Нью-Йорк", ["емігрував:", "$14 і Leica"], LGRN),
        (660, "1947 · Каліфорнія", ["заснував", "International", "Rectifier"], LGRN),
    ]
    bw, by, bh = 188, 80, 110
    for bx, lab, lines, fill in stops:
        s += text(bx + bw / 2, by - 8, lab, 11.5, INK, "middle", "bold")
        s += rect(bx, by, bw, bh, fill, "#9bb0c2", 1.5, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 28 + k * 20, ln, 10, INK, "middle")
    for i in range(len(stops) - 1):
        s += arrow(stops[i][0] + bw + 1, by + bh / 2, stops[i + 1][0] - 1, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Інженер, що допомагав євреям тікати з нацистської Німеччини; його батьки пережили Голокост.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-5i-4-lidow-journey.svg", s)


# ── §2.7.11 Верхній ключ: bootstrap, charge pump, драйвер півмоста (Рис. 2.7.11.k) ──
def _nfet_block(x, y, w, h, label, sub="(N)", fill="#eef2f7", border="#7f93a8"):
    """Простий прямокутник-ключ із підписом — як у фігурах §12.10."""
    t = rect(x, y, w, h, fill, border, 1.8, 6)
    t += text(x + w / 2, y + h / 2 - 4, label, 9.5, INK, "middle", "bold")
    if sub:
        t += text(x + w / 2, y + h / 2 + 13, sub, 8.5, GREY, "middle")
    return t


def fig1211_why_above_rail():
    """Рис. 2.7.11.1 — чому верхньому N-ключу треба Vgs відносно ВИТОКУ, що сам злітає до Vbus."""
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 26, "Верхній N-ключ: Vgs міряється від витоку, а витік злітає до шини", 14.5, INK, "middle", "bold")
    busY, gndY = 70, 320

    def panel(ox, lab, on):
        t = _frame(ox, 50, 330, 280, lab)
        cx = ox + 120
        # шина
        t += line(ox + 26, busY, ox + 304, busY, RED, 2)
        t += text(ox + 165, busY - 8, "+12 В (шина)", 9.5, RED, "middle", "bold")
        # ключ
        t += _nfet_block(cx - 34, 96, 68, 52, "верхній", "N-MOS")
        t += line(cx, busY, cx, 96, INK, 2)
        # точка витоку SW
        t += line(cx, 148, cx, 196, INK, 2) + circle(cx, 196, 3.5, INK, INK)
        t += text(cx + 12, 192, "витік (SW)", 9, INK, "start", "bold")
        # навантаження вниз
        t += line(cx, 196, cx, 220, INK, 2)
        t += rect(cx - 28, 220, 56, 44, "#ffffff", INK, 1.6) + text(cx, 246, "наван-", 8.5, INK, "middle") + text(cx, 259, "таження", 8.5, INK, "middle")
        t += line(cx, 264, cx, gndY, INK, 2)
        t += line(ox + 26, gndY, ox + 304, gndY, INK, 1.6) + text(ox + 290, gndY + 14, "0 В", 8.5, INK, "end")
        # затвор
        gx = cx + 64
        if on:
            t += plus(gx + 36, 122, 9, RED, 2)
            t += text(gx + 36, 100, "+17 В", 9.5, RED, "middle", "bold")
            t += arrow(gx + 24, 122, cx + 36, 122, RED, 2)
            t += text(cx + 4, 176, "SW ≈ 12 В", 9, GREEN, "start", "bold")
            t += rect(ox + 30, 286, 300, 38, "#eef6ef", GREEN, 1.4, 6)
            t += text(ox + 180, 303, "Vgs = 17 − 12 = +5 В  ✓ відкрито", 10.5, GREEN, "middle", "bold")
            t += text(ox + 180, 318, "затвору треба напруга ВИЩА за шину", 8.5, INK, "middle")
        else:
            t += text(gx + 36, 100, "+12 В", 9.5, BLUE, "middle", "bold")
            t += minus(gx + 36, 122, 9, BLUE, 2)
            t += arrow(gx + 24, 122, cx + 36, 122, BLUE, 2)
            t += text(cx + 4, 176, "SW → 12 В", 9, RED, "start", "bold")
            t += rect(ox + 30, 286, 300, 38, "#fdeeee", RED, 1.4, 6)
            t += text(ox + 180, 303, "Vgs = 12 − 12 = 0 В  ✗ закрито", 10.5, RED, "middle", "bold")
            t += text(ox + 180, 318, "«12 В на затвор» каналу не відкриває", 8.5, INK, "middle")
        return t

    s += panel(30, "подаємо на затвор тільки шину (12 В)", False)
    s += panel(400, "подаємо на затвор більше за шину (17 В)", True)
    s += text(W / 2, H - 6, "Витік верхнього ключа сам підіймається майже до шини — тому затвор мусить бути ще вищим, інакше Vgs = 0.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-11-1-why-above-rail.svg", s)


def fig1211_low_vs_high():
    """Рис. 2.7.11.2 — нижній ключ (опора нерухома) проти верхнього (опора плаває)."""
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 26, "Нижній ключ простий, верхній — ні: де опора Vgs", 15, INK, "middle", "bold")
    busY, gndY = 70, 270

    def panel(ox, lab, high):
        t = _frame(ox, 48, 330, 252, lab)
        cx = ox + 110
        t += line(ox + 26, busY, ox + 304, busY, RED, 2) + text(ox + 165, busY - 8, "+V", 9, RED, "middle", "bold")
        t += line(ox + 26, gndY, ox + 304, gndY, INK, 1.6) + text(ox + 290, gndY + 14, "0 В", 8.5, INK, "end")
        if high:
            # ключ зверху, навантаження знизу
            t += _nfet_block(cx - 34, 96, 68, 50, "ключ", "N")
            t += line(cx, busY, cx, 96, INK, 2)
            t += line(cx, 146, cx, 178, INK, 2) + circle(cx, 178, 3.5, INK, INK) + text(cx + 12, 174, "витік ПЛАВАЄ", 8.5, RED, "start", "bold")
            t += rect(cx - 26, 200, 52, 44, "#ffffff", INK, 1.6) + text(cx, 226, "наван.", 8.5, INK, "middle")
            t += line(cx, 178, cx, 200, INK, 2) + line(cx, 244, cx, gndY, INK, 2)
            t += text(cx + 96, 118, "опора Vgs (витік)", 8.5, RED, "middle", "bold")
            t += text(cx + 96, 134, "рухається 0…+V", 8.5, INK, "middle")
            t += rect(ox + 30, 256, 300, 36, "#fdeeee", "#e0b3b3", 1.3, 6)
            t += text(ox + 165, 278, "затвор треба піднімати НАД +V — нелегко", 9.5, RED, "middle", "bold")
        else:
            # навантаження зверху, ключ знизу
            t += rect(cx - 26, 92, 52, 44, "#ffffff", INK, 1.6) + text(cx, 118, "наван.", 8.5, INK, "middle")
            t += line(cx, busY, cx, 92, INK, 2)
            t += line(cx, 136, cx, 162, INK, 2) + circle(cx, 162, 3.5, INK, INK) + text(cx + 12, 158, "стік", 8.5, INK, "start")
            t += _nfet_block(cx - 34, 178, 68, 50, "ключ", "N")
            t += line(cx, 162, cx, 178, INK, 2)
            t += line(cx, 228, cx, gndY, INK, 2) + text(cx + 96, 250, "витік = 0 В", 8.5, GREEN, "middle", "bold")
            t += text(cx + 96, 204, "опора Vgs (витік)", 8.5, GREEN, "middle", "bold")
            t += text(cx + 96, 220, "прибита до землі", 8.5, INK, "middle")
            t += rect(ox + 30, 256, 300, 36, "#eef6ef", "#b3d2b8", 1.3, 6)
            t += text(ox + 165, 278, "5 В від МК на затворі = рівно Vgs 5 В ✓", 9.5, GREEN, "middle", "bold")
        return t

    s += panel(30, "нижнє плече (low-side)", False)
    s += panel(400, "верхнє плече (high-side)", True)
    s += text(W / 2, H - 6, "Уся складність верхнього ключа — у тому, що його витік (опора відліку Vgs) не стоїть на місці.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-11-2-low-vs-high.svg", s)


def fig1211_bootstrap():
    """Рис. 2.7.11.3 — бутстреп: дві фази заряду/підняття плаваючого живлення затвора."""
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 26, "Бутстреп: конденсатор-«відерце», що їздить разом із витоком", 15, INK, "middle", "bold")

    def stage(ox, title, charging):
        busY, gndY = 78, 300
        t = _frame(ox, 50, 360, 290, title)
        cx = ox + 150
        t += line(ox + 26, busY, ox + 334, busY, RED, 2) + text(ox + 70, busY - 8, "+Vbus", 9, RED, "middle", "bold")
        t += line(ox + 26, gndY, ox + 334, gndY, INK, 1.6) + text(ox + 320, gndY + 14, "GND", 8.5, INK, "end")
        # ключі
        t += _nfet_block(cx - 32, 98, 64, 46, "Q_в", "N")
        t += line(cx, busY, cx, 98, INK, 2)
        swY = 196
        t += line(cx, 144, cx, swY, INK, 2) + circle(cx, swY, 3.5, INK, INK) + text(cx - 10, swY + 4, "SW", 9, INK, "end", "bold")
        t += _nfet_block(cx - 32, 230, 64, 46, "Q_н", "N")
        t += line(cx, swY, cx, 230, INK, 2) + line(cx, 276, cx, gndY, INK, 2)
        # Vdrive низьковольтне
        vdY = 128
        t += line(ox + 26, vdY, ox + 70, vdY, "#c97b1e", 2) + text(ox + 40, vdY - 8, "Vdrv", 8.5, COPP, "middle", "bold")
        t += text(ox + 40, vdY + 16, "12 В", 8, GREY, "middle")
        # діод
        t += _diode_h(ox + 92, vdY, 11, right=True, col=INK) + text(ox + 92, vdY - 16, "Dbs", 8, INK, "middle", "bold")
        t += line(ox + 70, vdY, ox + 81, vdY, "#c97b1e", 2)
        vbX = ox + 116
        t += line(ox + 103, vdY, vbX, vdY, INK, 2) + circle(vbX, vdY, 3, INK, INK) + text(vbX - 6, vdY - 8, "VB", 8.5, INK, "end", "bold")
        # Cbs між VB і SW
        t += line(vbX, vdY, vbX, 160, INK, 2)
        t += line(vbX - 14, 164, vbX + 14, 164, INK, 2.6) + line(vbX - 14, 172, vbX + 14, 172, INK, 2.6)
        t += text(vbX - 20, 170, "Cbs", 8.5, INK, "end", "bold")
        t += line(vbX, 176, vbX, swY, INK, 2) + line(vbX, swY, cx, swY, INK, 2)
        # затвор верхнього від VB
        t += line(vbX, vdY, vbX, 110, GREEN, 1.8) + line(vbX, 110, cx - 32, 110, GREEN, 1.8)
        if charging:
            # Q_н ON: SW=0, Cbs заряджається
            t += text(cx, 253, "ON", 9, GREEN, "middle", "bold")
            t += text(cx + 8, swY - 6, "≈ 0 В", 8.5, BLUE, "start", "bold")
            t += arrow(ox + 81, vdY + 10, vbX, vdY + 10, RED, 1.8)
            t += text((ox + 81 + vbX) / 2, vdY + 24, "заряд", 8, RED, "middle", "bold")
            t += text(ox + 180, 326, "Q_н відкритий → SW=0 → Cbs набирає 12 В", 9, INK, "middle", "bold")
        else:
            # Q_в ON: SW->Vbus, VB = Vbus+12
            t += text(cx, 121, "ON", 9, GREEN, "middle", "bold")
            t += text(cx + 8, swY - 6, "≈ Vbus", 8.5, RED, "start", "bold")
            t += arrow(cx, 170, cx, swY - 6, RED, 2)
            t += plus(vbX, vdY - 28, 7, RED, 1.8) + text(vbX + 14, vdY - 26, "Vbus+12", 8.5, RED, "start", "bold")
            t += text(ox + 180, 326, "Cbs їде вгору з SW → VB вище шини → є чим тримати затвор", 8.5, INK, "middle", "bold")
        return t

    s += stage(20, "Фаза 1 — заряд (нижній ключ ON)", True)
    s += stage(440, "Фаза 2 — робота (верхній ключ ON)", False)
    s += text(W / 2, H - 6, "Cbs заряджають, поки SW унизу; коли SW злітає до шини, конденсатор підіймає VB над шиною — затвор живиться.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-11-3-bootstrap.svg", s)


def fig1211_bootstrap_limit():
    """Рис. 2.7.11.4 — слабке місце бутстрепа: без перезаряду VB «стікає», 100% не тримає."""
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Слабкість бутстрепа: «відерце» поволі стікає", 15.5, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 240, 520, 170
    s += _axes(ox, oy, ww, hh, "час", "VB − SW")
    full = oy - hh + 26
    s += line(ox, full, ox + ww, full, GREEN, 1.3, "5 4") + text(ox + ww + 16, full + 4, "12 В (повне)", 9, GREEN, "start", "bold")
    thr = oy - 46
    s += line(ox, thr, ox + ww, thr, RED, 1.3, "5 4") + text(ox + ww + 16, thr + 4, "поріг", 9, RED, "start", "bold")
    # пилкоподібна: швидкий заряд (вниз провал = перезаряд), повільне стікання вгорі
    pts = [(ox, full)]
    x = ox
    seg = 92
    for k in range(5):
        pts.append((x + seg * 0.78, thr + 14))   # стікання вниз
        pts.append((x + seg * 0.82, full))        # короткий перезаряд (SW знизу)
        x += seg
    s += _poly(pts, INK, 2.4)
    for k in range(5):
        xc = ox + k * seg + seg * 0.4
        s += text(xc, full - 8, "стікає", 8, GREY, "middle", style="italic")
    s += text(ox + ww * 0.82, oy + 18, "↑ перезаряд лише коли SW унизу", 8.5, BLUE, "middle", "bold")
    # права картка-проблема
    s += rect(ox + 40, oy - hh - 6, 280, 40, "#fdeeee", "#e0b3b3", 1.3, 6)
    s += text(ox + 180, oy - hh + 12, "100% (верхній весь час ON):", 9.5, RED, "middle", "bold")
    s += text(ox + 180, oy - hh + 28, "SW не опускається → Cbs не перезарядити → ключ згасне", 8.5, INK, "middle")
    s += text(W / 2, H - 8, "Бутстреп вимагає, щоб витік періодично падав до землі. Для постійного «ON» потрібна інша схема — зарядова помпа.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-11-4-bootstrap-limit.svg", s)


def fig1211_charge_pump():
    """Рис. 2.7.11.5 — зарядова помпа: качає заряд тактами й тримає напругу ВИЩЕ шини постійно."""
    W, H = 760, 350
    s = header(W, H)
    s += text(W / 2, 26, "Зарядова помпа: качає конденсаторами напругу вище шини — постійно", 14, INK, "middle", "bold")
    # ліва частина: дві фази «драбинки» конденсаторів
    def phase(ox, title, lift):
        t = _frame(ox, 50, 300, 232, title)
        y = 150
        t += line(ox + 30, y, ox + 70, y, RED, 2) + text(ox + 36, y - 8, "12 В", 8.5, RED, "start", "bold")
        # перемикач (стрілка такту)
        t += _diode_h(ox + 92, y, 10, right=True, col=INK)
        t += line(ox + 70, y, ox + 82, y, INK, 2)
        # C1
        c1 = ox + 120
        t += line(ox + 102, y, c1, y, INK, 2)
        t += line(c1, y, c1, y + 16, INK, 2)
        t += line(c1 - 12, y + 20, c1 + 12, y + 20, INK, 2.4) + line(c1 - 12, y + 27, c1 + 12, y + 27, INK, 2.4) + text(c1, y + 44, "C1", 8.5, INK, "middle", "bold")
        if lift:
            t += line(c1, y + 27, c1, y + 46, INK, 2)
            t += arrow(c1, y + 70, c1, y + 50, RED, 2) + text(c1 - 6, y + 64, "↑ підкидаємо низ", 8, RED, "end", "bold")
        else:
            t += line(c1, y + 27, c1, y + 60, INK, 2) + text(c1 + 8, y + 56, "низ → 0 В", 8, INK, "start")
        # D2 -> вихід
        t += _diode_h(c1 + 30, y, 10, right=True, col=INK)
        t += line(c1, y, c1 + 18, y, INK, 2)
        outx = ox + 188
        t += line(c1 + 42, y, outx, y, INK, 2) + circle(outx, y, 3, INK, INK)
        # Cout
        t += line(outx, y, outx, y + 16, INK, 2)
        t += line(outx - 12, y + 20, outx + 12, y + 20, "#7f93a8", 2.4) + line(outx - 12, y + 27, outx + 12, y + 27, "#7f93a8", 2.4) + text(outx, y + 44, "Cout", 8.5, INK, "middle", "bold")
        t += line(outx, y + 27, outx, y + 60, "#7f93a8", 2)
        t += line(outx, y, outx + 40, y, INK, 2)
        if lift:
            t += plus(outx + 50, y, 7, RED, 1.8) + text(outx + 50, y - 16, "≈ 24 В", 9, RED, "middle", "bold")
        else:
            t += text(outx + 50, y + 4, "12 В", 9, INK, "start", "bold")
        return t

    s += phase(20, "такт A: C1 заряджається до 12 В", False)
    s += phase(360, "такт B: низ C1 підкинуто → виходу +12 поверх", True)
    # нижній підсумок
    s += rect(60, 296, 640, 44, "#eef6ef", GREEN, 1.4, 8)
    s += text(380, 316, "Перекидаючи заряд із такту в такт, помпа тримає на виході напругу ВИЩУ за шину — і не падає при 100%.",
              9.5, INK, "middle", "bold")
    s += text(380, 333, "Ціна — слабкий струм (тому годиться лиш на тримання затвора, не на навантаження).",
              8.5, GREY, "middle", style="italic")
    save("fig-12-11-5-charge-pump.svg", s)


def fig1211_boot_vs_pump():
    """Рис. 2.7.11.6 — бутстреп проти зарядової помпи: коли що."""
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 30, "Бутстреп чи зарядова помпа: коли що", 16, INK, "middle", "bold")
    cols = [(40, 220, "риса"), (260, 240, "бутстреп"), (500, 220, "зарядова помпа")]
    y0 = 58
    fills = ["#eef2f6", "#eef6ef", "#e9eefb"]
    borders = ["#c9d3dc", "#b3d2b8", "#aebbe0"]
    for i, (x, w, lab) in enumerate(cols):
        s += rect(x, y0, w, 30, fills[i], borders[i], 1.2)
        s += text(x + w / 2, y0 + 20, lab, 11.5, INK, "middle", "bold")
    rows = [
        ("деталі", "1 діод + 1 конд.", "кілька конд. + такт"),
        ("звідки V над шиною", "конд. їде з витоком", "перекачка тактами"),
        ("тримає 100% ON?", "НІ — VB стікає", "ТАК — постійно"),
        ("струм у затвор", "великий (імпульс)", "малий"),
        ("де живе", "майже всі ШІМ-мости", "always-on верх. ключ"),
    ]
    y = y0 + 30
    for name, a, b in rows:
        s += rect(cols[0][0], y, cols[0][1], 38, "#fbfbfb", "#d7dee5", 1)
        s += text(cols[0][0] + 12, y + 24, name, 10.5, INK, "start", "bold")
        s += rect(cols[1][0], y, cols[1][1], 38, "#f4faf5", "#cfe4d3", 1)
        s += text(cols[1][0] + 12, y + 24, a, 10, INK, "start")
        s += rect(cols[2][0], y, cols[2][1], 38, "#f1f4fc", "#cdd6f0", 1)
        s += text(cols[2][0] + 12, y + 24, b, 10, INK, "start")
        y += 38
    s += text(W / 2, y + 22, "Здебільшого використовують бутстреп (дешевий); помпу додають, коли верхній ключ мусить стояти відкритим без пауз.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-11-6-boot-vs-pump.svg", s)


def fig1211_halfbridge_driver():
    """Рис. 2.7.11.7 — мікросхема-драйвер півмоста: HIN/LIN → HO/LO, VB/VS, бутстреп, мертвий час."""
    W, H = 780, 380
    s = header(W, H)
    s += text(W / 2, 26, "Драйвер півмоста: одна мікросхема ховає верхній ключ і мертвий час", 14, INK, "middle", "bold")
    busY, gndY = 70, 330
    # силова частина праворуч
    cx = 600
    s += line(cx - 40, busY, 740, busY, RED, 2) + text(cx + 60, busY - 8, "+Vbus", 9.5, RED, "middle", "bold")
    s += line(360, gndY, 740, gndY, INK, 1.6) + text(720, gndY + 14, "GND", 9, INK, "end")
    s += _nfet_block(cx - 34, 100, 68, 50, "Q_верх", "N")
    s += line(cx, busY, cx, 100, INK, 2)
    swY = 210
    s += line(cx, 150, cx, swY, INK, 2) + circle(cx, swY, 4, INK, INK) + text(cx + 12, swY + 4, "VS / SW", 9, INK, "start", "bold")
    s += _nfet_block(cx - 34, 250, 68, 50, "Q_низ", "N")
    s += line(cx, swY, cx, 250, INK, 2) + line(cx, 300, cx, gndY, INK, 2)
    # навантаження
    s += line(cx, swY, cx + 70, swY, INK, 2) + rect(cx + 70, swY - 22, 56, 44, "#fff", INK, 1.6) + text(cx + 98, swY + 4, "наван.", 8.5, INK, "middle")
    s += line(cx + 98, swY + 22, cx + 98, gndY, INK, 2)
    # мікросхема драйвера ліворуч
    s += _frame(60, 96, 300, 234, "мікросхема-драйвер півмоста")
    s += text(210, 120, "HIN ─┐  LIN ─┐", 11, INK, "middle", "bold")
    # входи
    s += rect(30, 150, 40, 26, LBLUE, "#9bb0c2", 1.3, 4) + text(50, 167, "ШІМ", 8.5, INK, "middle", "bold")
    s += arrow(70, 163, 100, 163, INK, 1.8)
    # блок мертвого часу
    s += rect(96, 196, 130, 40, "#fff7e6", COPP, 1.4, 6) + text(161, 213, "мертвий час", 9, INK, "middle", "bold") + text(161, 228, "+ зсув рівня", 8, GREY, "middle")
    # виходи HO/LO
    s += text(300, 150, "VB", 9, INK, "middle", "bold") + circle(300, 158, 3, INK, INK)
    s += line(300, 158, 340, 158, GREEN, 2)
    s += text(250, 178, "HO", 9.5, GREEN, "start", "bold")
    s += line(226, 196, 300, 196, GREEN, 1.8) + line(300, 196, 300, 175, GREEN, 1.8)  # внутр.
    s += line(340, 158, 340, 130, GREEN, 1.8) + line(340, 130, cx - 34, 130, GREEN, 1.8) + text(450, 122, "HO → затвор Q_верх", 8.5, GREEN, "middle", "bold")
    s += text(250, 250, "LO", 9.5, BLUE, "start", "bold")
    s += line(226, 236, 340, 236, BLUE, 1.8) + line(340, 236, 340, 275, BLUE, 1.8) + line(340, 275, cx - 34, 275, BLUE, 1.8) + text(450, 290, "LO → затвор Q_низ", 8.5, BLUE, "middle", "bold")
    # VS назад до SW
    s += text(300, 318, "VS", 9, INK, "middle", "bold") + circle(300, 308, 3, INK, INK)
    s += line(300, 236, 300, 308, INK, 1.4, "3 3")
    s += line(300, 308, 300, 320, INK, 1.4) + line(300, 320, 520, 320, INK, 1.4) + line(520, 320, 520, swY, INK, 1.4) + line(520, swY, cx, swY, INK, 1.4)
    s += text(410, 332, "VS стежить за витоком (плаває)", 8, GREY, "middle", style="italic")
    s += text(W / 2, H - 8, "HIN/LIN з МК → драйвер сам додає мертвий час, піднімає рівень і бутстрепом живить верхній ключ. Готова цеглинка.",
              9.5, GREY, "middle", style="italic")
    save("fig-12-11-7-halfbridge-driver.svg", s)


if __name__ == "__main__":
    fig_t1_timeline()
    fig_t2_lilienfeld_idea()
    fig_t3_surface_states()
    fig_t4_oxide_fix()
    fig_t5_first_mosfet()
    fig_t6_legacy()
    # §12.1 ідея польового керування
    fig121_current_vs_field()
    fig121_valve_analogy()
    fig121_three_terminals()
    fig121_gate_capacitor()
    fig121_no_gate_current()
    fig121_why_it_matters()
    # §12.2 будова MOSFET
    fig122_cross_section()
    fig122_mos_stack()
    fig122_off_state()
    fig122_thin_oxide()
    fig122_four_terminals()
    fig122_planar()
    # §12.3 поріг і канал
    fig123_three_stages()
    fig123_inversion_layer()
    fig123_threshold_transfer()
    fig123_overdrive()
    fig123_logic_level()
    fig123_dam_analogy()
    # §12.4 NMOS / PMOS
    fig124_nmos_vs_pmos_structure()
    fig124_turn_on_polarity()
    fig124_symbols()
    fig124_mobility()
    fig124_strong_weak()
    fig124_complementary()
    # §12.5 Rds(on)
    fig125_on_resistance()
    fig125_power_heat()
    fig125_bjt_vs_mosfet_loss()
    fig125_overdrive_sets_r()
    fig125_voltage_tradeoff()
    fig125_temperature()
    # §12.6 MOSFET як силовий ключ
    fig126_low_side_switch()
    fig126_gate_resistor_pulldown()
    fig126_floating_gate()
    fig126_flyback()
    fig126_high_side_pmos()
    fig126_vs_bjt()
    # §12.7 затвор як ємність
    fig127_gate_charge()
    fig127_switch_time()
    fig127_miller_plateau()
    fig127_switching_loss()
    fig127_loss_vs_frequency()
    fig127_gate_driver()
    # §12.8 BJT проти MOSFET
    fig128_core_difference()
    fig128_comparison_table()
    fig128_when_each()
    fig128_decision_flow()
    fig128_same_task()
    fig128_history_arc_igbt()
    # §12.9 CMOS
    fig129_inverter()
    fig129_two_states()
    fig129_no_static_current()
    fig129_dynamic_power()
    fig129_nand_gate()
    fig129_gates_to_cpu()
    # під-історія до §12.9 (CMOS — Ванласс і Са)
    fig129i_ignored_genius()
    fig129i_two_inventors()
    fig129i_why_overlooked()
    fig129i_found_its_home()
    fig129i_then_got_fast()
    fig129i_lesson()
    # §12.10 H-міст (тема 2.7.10)
    fig1210_need()
    fig1210_hbridge()
    fig1210_directions()
    fig1210_four_states()
    fig1210_halfbridges()
    fig1210_shoot_through()
    fig1210_pwm_speed()
    # 🔌 вставка до 2.7.10 — плата драйвера H-моста
    fig1210c_board_anatomy()
    fig1210c_pinout_wiring()
    # 🧮 вставка до 2.7.3 — квадратичний закон
    fig123m_square_law()
    fig123m_output_family()
    # 🧮 вставка до 2.7.7 — заряд затвора
    fig127m_gate_charge_curve()
    fig127m_nonlinear_cap()
    # 🔌 вставка до 2.7.2 — паразитний body-діод
    fig122c_body_diode()
    fig122c_reverse_block()
    # 🔌 вставка до 2.7.4 — P-канальний load switch
    fig124c_load_switch()
    fig124c_gate_limit()
    # 🔌 вставка до 2.7.6 — logic-level MOSFET
    fig126c_rds_vs_vgs()
    fig126c_families()
    # 🔌 вставка до 2.7.6 — «ідеальний діод»
    fig126c_ideal_vs_diode()
    fig126c_reverse_protect()
    # 🔌 вставка до 2.7.7 — драйвер затвора
    fig127c_push_pull()
    fig127c_bootstrap()
    # ⚙️ вставка до 2.7.6 — тепловий розрахунок
    fig126a_thermal_ohm()
    fig126a_verdict()
    # ⚙️ вставка до 2.7.10 — наскрізний струм і мертвий час
    fig1210a_deadtime_timing()
    fig1210a_tradeoff()
    # §12.11 Верхній ключ: bootstrap, charge pump, драйвер півмоста (тема 2.7.11)
    fig1211_why_above_rail()
    fig1211_low_vs_high()
    fig1211_bootstrap()
    fig1211_bootstrap_limit()
    fig1211_charge_pump()
    fig1211_boot_vs_pump()
    fig1211_halfbridge_driver()
    # 📜 історія до §2.7.5 — HEXFET
    fig125i_timeline()
    fig125i_planar_vs_vertical()
    fig125i_hexcells()
    fig125i_lidow_journey()
    print("OK — Розділ 12 (історія + §12.1–§12.11 + вставки + під-історія CMOS) згенеровано в", OUT)
