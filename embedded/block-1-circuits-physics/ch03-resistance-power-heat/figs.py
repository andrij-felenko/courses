# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 3 — «Опір, потужність і тепло» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: історія до розділу — секція 0 (Рис. 3.0.N); теми — Рис. 3.M.k.
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


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def heatwaves(cx, cy, n=3, color=ORANGE):
    out = ""
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * 12
        out += f'<path d="M {x},{cy} q 5,-8 0,-16 q -5,-8 0,-16" fill="none" stroke="{color}" stroke-width="1.8"/>\n'
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 3.0.1 — млинок Джоуля: робота → тепло ───────────────────────────────
def fig_joule_paddle():
    W, H = 800, 420
    s = header(W, H)
    s += text(W / 2, 36, "Млинок Джоуля: робота перетворюється на тепло", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "падаюча гиря крутить лопаті у воді — і вода нагрівається на точно визначену величину",
              12, GREY, "middle", style="italic")
    # бак з водою
    s += rect(220, 170, 220, 170, "#dceaf2", "#5b87a6", 2.4, 6)
    s += rect(224, 230, 212, 106, "#bfe0ef", "none", 0)
    s += text(330, 320, "вода", 12, "#3a6a86", "middle", "bold")
    # вал і лопаті
    s += line(330, 120, 330, 300, INK, 3)
    for yy in (250, 285):
        s += line(300, yy, 360, yy, INK, 3)
        s += line(300, yy - 8, 300, yy + 8, INK, 2)
        s += line(360, yy - 8, 360, yy + 8, INK, 2)
    s += f'<path d="M 318,210 a 14,14 0 1 1 18,8" fill="none" stroke="{GREEN}" stroke-width="2" marker-end="url(#aGreen)"/>\n'
    s += text(385, 200, "крутиться", 11, GREEN, "start", "bold")
    # блок (шків)
    s += circle(560, 120, 18, "#eee", INK, 2.4)
    s += circle(560, 120, 3, INK, INK, 1)
    s += line(330, 120, 542, 120, INK, 2)
    # гиря
    s += line(560, 138, 560, 250, INK, 2)
    s += rect(540, 250, 40, 40, "#cdd5da", INK, 2, 4)
    s += text(560, 274, "гиря", 10.5, INK, "middle", "bold")
    s += arrow(605, 250, 605, 300, RED, 2.6)
    s += text(625, 280, "падає", 11, RED, "start", "bold")
    # термометр
    s += line(410, 180, 410, 300, INK, 2)
    s += circle(410, 308, 9, "#fdd", RED, 2)
    s += line(410, 300, 410, 230, RED, 4)
    s += text(430, 210, "T↑", 13, RED, "start", "bold")
    s += rect(120, 366, W - 240, 44, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 388, "Виміряний зв'язок «робота ↔ тепло» довів: тепло — це форма ЕНЕРГІЇ, а не рідина.",
              12, INK, "middle", "bold")
    s += text(W / 2, 404, "Так народилося збереження енергії — і одиниця джоуль.", 11, GREY, "middle", style="italic")
    save("fig-3-0-1-joule-paddle.svg", s)


# ── Рис. 3.0.2 — теплород проти енергії ──────────────────────────────────────
def fig_caloric_vs_energy():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що таке тепло: стара й нова відповідь", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "Джоуль поховав «теплород»-рідину: тепло виявилося рухом, тобто енергією", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # стара — теплород
    s += text(205, 102, "стара думка: «теплород»", 13, RED, "middle", "bold")
    s += circle(140, 200, 36, "#fdeeee", RED, 2)
    s += text(140, 205, "гаряче", 11, RED, "middle", "bold")
    s += circle(290, 200, 36, "#eef2fb", BLUE, 2)
    s += text(290, 205, "холодне", 11, BLUE, "middle", "bold")
    for yy in (188, 200, 212):
        s += arrow(178, yy, 252, yy, ORANGE, 1.8)
    s += text(215, 250, "невидима РІДИНА", 11, ORANGE, "middle", "bold")
    s += text(215, 268, "перетікає з гарячого", 10.5, GREY, "middle", style="italic")
    s += text(215, 300, "(не зв'язана з рухом)", 10.5, GREY, "middle", style="italic")
    # нова — енергія
    s += text(615, 102, "Джоуль: тепло — це РУХ", 13, GREEN, "middle", "bold")
    s += circle(615, 200, 50, "#fff3e8", ORANGE, 2)
    spots = [(595, 180), (635, 185), (610, 215), (640, 215), (585, 210), (625, 165), (655, 200)]
    for i, (ax, ay) in enumerate(spots):
        s += circle(ax, ay, 6, "#cdd5da", INK, 1.4)
        a = (i * 51) % 360
        s += arrow(ax, ay, ax + 14 * math.cos(math.radians(a)), ay + 14 * math.sin(math.radians(a)), INK, 1.2)
    s += text(615, 280, "молекули шалено рухаються —", 11, INK, "middle", "bold")
    s += text(615, 298, "це і є тепло (різновид енергії)", 10.5, GREY, "middle", style="italic")
    save("fig-3-0-2-caloric-vs-energy.svg", s)


# ── Рис. 3.0.3 — Ом × Джоуль → потужність і тепло ────────────────────────────
def fig_ohm_joule_chain():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 36, "Дві цеглини Розділу 3: Ом і Джоуль", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "закон струму (Ом) і закон тепла (Джоуль) разом дають потужність і нагрів кіл", 12, GREY, "middle", style="italic")
    # Ом
    s += rect(60, 110, 280, 110, "#f4f7f4", INK, 2, 12)
    s += text(200, 138, "ОМ (1827)", 14, INK, "middle", "bold")
    s += text(200, 172, "I = V / R", 24, INK, "middle", "bold")
    s += text(200, 200, "закон струму (відкинули — Гл.2)", 11, GREY, "middle", style="italic")
    # Джоуль
    s += rect(480, 110, 280, 110, "#fff3e8", ORANGE, 2, 12)
    s += text(620, 138, "ДЖОУЛЬ (1841)", 14, ORANGE, "middle", "bold")
    s += text(620, 172, "тепло ∝ I²·R·t", 21, INK, "middle", "bold")
    s += text(620, 200, "струм у опорі → тепло", 11, GREY, "middle", style="italic")
    s += arrow(340, 165, 478, 165, INK, 2.4)
    s += text(410, 152, "+", 18, INK, "middle", "bold")
    # результат
    s += rect(220, 260, 380, 70, "#eef7f0", GREEN, 2, 12)
    s += text(410, 288, "= потужність P = V·I  і  джоулеве тепло", 14.5, INK, "middle", "bold")
    s += text(410, 312, "усе, що рахуватимемо в Розділі 3", 11.5, GREY, "middle", style="italic")
    s += arrow(200, 222, 360, 258, INK, 2)
    s += arrow(620, 222, 460, 258, ORANGE, 2)
    save("fig-3-0-3-ohm-joule-chain.svg", s)


def _resistor(x, y, w=70, h=24, label="R"):
    out = rect(x, y - h / 2, w, h, "#fff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 8, label, 13, INK, "middle", "bold", "italic")
    return out


# ── Рис. 3.1.1 — означення опору R = V/I ─────────────────────────────────────
def fig31_resistance_def():
    W, H = 820, 390
    s = header(W, H)
    s += text(W / 2, 34, "Опір: скільки напруги треба на одиницю струму", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "R = V/I — наскільки сильно елемент опирається струмові; одиниця — ом (Ом = В/А)", 12, GREY, "middle", style="italic")
    # резистор у дроті
    s += line(120, 150, 250, 150, COPPER, 3)
    s += _resistor(250, 150, 90, 28, "R")
    s += line(340, 150, 470, 150, COPPER, 3)
    s += arrow(160, 150, 200, 150, RED, 2.4)
    s += text(180, 138, "I", 12, RED, "middle", "bold", "italic")
    s += line(250, 110, 250, 90, BLUE, 1.6, "3 3")
    s += line(340, 110, 340, 90, BLUE, 1.6, "3 3")
    s += line(250, 95, 340, 95, BLUE, 1.6)
    s += text(295, 86, "напруга V на ньому", 11, BLUE, "middle", "bold")
    # формула
    s += rect(520, 110, 240, 90, "#f4f7f4", GREEN, 1.8, 12)
    s += text(640, 150, "R = V / I", 24, INK, "middle", "bold")
    s += text(640, 182, "провідність G = 1/R (сименс)", 11.5, GREY, "middle")
    # порівняння
    s += text(230, 240, "великий R", 12, RED, "middle", "bold")
    s += line(120, 270, 200, 270, COPPER, 2.4)
    s += _resistor(200, 270, 60, 24, "")
    s += line(260, 270, 340, 270, COPPER, 2.4)
    s += arrow(150, 270, 165, 270, RED, 2)
    s += text(230, 300, "багато V → ледь-ледь I (важко пхати)", 10.5, INK, "middle")
    s += text(600, 240, "малий R", 12, GREEN, "middle", "bold")
    s += line(490, 270, 570, 270, COPPER, 2.4)
    s += _resistor(570, 270, 60, 24, "")
    s += line(630, 270, 710, 270, COPPER, 2.4)
    s += arrow(500, 270, 560, 270, RED, 2.8)
    s += text(600, 300, "мало V → великий I (легко)", 10.5, INK, "middle")
    s += text(W / 2, 360, "Опір — це «жорсткість» елемента для струму: що більший R, то важче проштовхнути струм.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-1-1-resistance-def.svg", s)


# ── Рис. 3.1.2 — аналогія вузької труби ──────────────────────────────────────
def fig31_narrow_pipe():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Опір — як вузьке місце в трубі", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "вузька труба гальмує потік: щоб прогнати ту саму воду, потрібен більший тиск", 12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 26, FAINT, 1.5)
    # широка
    s += text(205, 100, "широка (малий опір)", 12.5, GREEN, "middle", "bold")
    s += rect(90, 150, 230, 50, "#dceaf2", "#5b87a6", 2, 4)
    for dx in (130, 200, 270):
        s += arrow(dx - 18, 175, dx + 22, 175, "#2b7", 2.6)
    s += text(205, 230, "легкий потік (струм)", 11, INK, "middle")
    # вузька
    s += text(615, 100, "вузька (великий опір)", 12.5, RED, "middle", "bold")
    s += rect(500, 150, 80, 50, "#dceaf2", "#5b87a6", 2, 4)
    s += f'<path d="M 580,150 L 620,168 L 700,168 L 740,150" fill="none" stroke="#5b87a6" stroke-width="2.4"/>\n'
    s += f'<path d="M 580,200 L 620,182 L 700,182 L 740,200" fill="none" stroke="#5b87a6" stroke-width="2.4"/>\n'
    s += arrow(540, 175, 575, 175, "#2b7", 2)
    s += arrow(645, 175, 670, 175, "#2b7", 1.6)
    s += text(615, 230, "той самий потік — лише з більшим тиском", 10.5, INK, "middle")
    s += rect(150, 270, W - 300, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 294, "тиск ↔ напруга · потік ↔ струм · вузькість ↔ опір", 12.5, INK, "middle", "bold")
    s += text(W / 2, 308, "(чим вужче — тим більший опір — тим більше тиску треба на той самий потік)", 10, GREY, "middle", style="italic")
    save("fig-3-1-2-narrow-pipe.svg", s)


# ── Рис. 3.1.3 — звідки опір: зіткнення + матеріал і форма ───────────────────
def fig31_mechanism():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Звідки опір: зіткнення (§2.9), матеріал і форма", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "опір — це усереднена «складність» руху електронів крізь решітку", 12, GREY, "middle", style="italic")
    # зіткнення
    s += rect(60, 100, 230, 120, "#fff", "#ddd", 1.6, 10)
    s += text(175, 124, "зіткнення з решіткою", 11.5, INK, "middle", "bold")
    for cx in (110, 160, 210, 260):
        s += circle(cx, 175, 11, "#fde0d6", COPPER, 1.5)
        s += text(cx, 179, "+", 9, COPPER, "middle", "bold")
    s += polyline([(80, 175), (130, 162), (155, 188), (200, 165), (245, 185), (275, 168)], BLUE, 1.8)
    for bx in (130, 200):
        for a in range(0, 360, 60):
            s += line(bx, 162 if bx == 130 else 165, bx + 7 * math.cos(math.radians(a)), (162 if bx == 130 else 165) + 7 * math.sin(math.radians(a)), RED, 1)
    s += text(175, 210, "що частіші — то більший R", 10.5, GREY, "middle", style="italic")
    # залежності
    s += rect(330, 100, 430, 120, "#f4f7f4", GREEN, 1.6, 10)
    s += text(545, 124, "R залежить від:", 12.5, INK, "middle", "bold")
    s += text(350, 150, "• матеріалу (ρ) — «гладкість» решітки (§2.10)", 11.5, INK, "start")
    s += text(350, 174, "• довжини L — довше → більше зіткнень → R↑", 11.5, INK, "start")
    s += text(350, 198, "• перерізу A — товще → просторіше → R↓", 11.5, INK, "start")
    s += rect(150, 250, W - 300, 64, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 276, "Повну формулу R = ρ·L/A складемо у §3.3.", 13, INK, "middle", "bold")
    s += text(W / 2, 298, "Тут головне: опір — це кількісна міра того механізму зіткнень, що ми бачили в §2.9.",
              11, GREY, "middle", style="italic")
    save("fig-3-1-3-mechanism.svg", s)


# ── Рис. 3.1.4 — резистор як компонент ───────────────────────────────────────
def fig31_resistor_component():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Резистор: навмисний, керований опір", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "часто опір додають спеціально — щоб обмежити струм чи задати напругу", 12, GREY, "middle", style="italic")
    # символ
    s += text(200, 100, "символ на схемі", 12, INK, "middle", "bold")
    s += line(90, 150, 140, 150, INK, 2.4)
    s += polyline([(140, 150), (150, 138), (170, 162), (190, 138), (210, 162), (230, 138), (250, 162), (260, 150)], INK, 2.4)
    s += line(260, 150, 310, 150, INK, 2.4)
    s += text(200, 180, "(або прямокутник)", 10.5, GREY, "middle", style="italic")
    # реальний резистор
    s += text(610, 100, "реальний резистор", 12, INK, "middle", "bold")
    s += line(470, 150, 520, 150, "#999", 3)
    s += rect(520, 132, 180, 36, "#e8cfa8", "#b89060", 2, 14)
    for bx, bc in ((545, "#5a3a26"), (565, RED), (585, ORANGE), (640, "#caa23a")):
        s += rect(bx, 132, 8, 36, bc, "none", 0)
    s += line(700, 150, 750, 150, "#999", 3)
    s += text(610, 195, "кольорові смужки = номінал в омах", 10.5, GREY, "middle", style="italic")
    s += rect(120, 230, W - 240, 80, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 256, "Навіщо навмисний опір:", 12.5, INK, "middle", "bold")
    s += text(W / 2, 278, "• обмежити струм (резистор до світлодіода)   • задати напругу (дільник, далі)", 11.5, INK, "middle")
    s += text(W / 2, 298, "• перетворити струм на тепло (нагрівачі)   • «підтягнути» вхід (pull-up, далі)", 11.5, INK, "middle")
    save("fig-3-1-4-resistor-component.svg", s)


# ── Рис. 3.2.1 — три форми закону Ома + трикутник ────────────────────────────
def fig32_three_forms():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Закон Ома: три форми однієї рівності", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "що шукаєш — те й закрий у трикутнику VIR", 12, GREY, "middle", style="italic")
    # трикутник
    cx, ty, by = 200, 100, 250
    s += f'<path d="M {cx},{ty} L {cx-90},{by} L {cx+90},{by} Z" fill="#f4f7f4" stroke="{INK}" stroke-width="2.2"/>\n'
    s += line(cx - 58, 198, cx + 58, 198, INK, 1.8)
    s += line(cx, 198, cx, by, INK, 1.8)
    s += text(cx, 178, "V", 26, RED, "middle", "bold")
    s += text(cx - 38, 235, "I", 24, GREEN, "middle", "bold")
    s += text(cx + 38, 235, "R", 24, BLUE, "middle", "bold")
    s += text(cx, 290, "закрий шукане — побачиш формулу", 11, GREY, "middle", style="italic")
    # три бокси
    boxes = [("шукаємо I", "I = V / R", GREEN), ("шукаємо V", "V = I · R", RED), ("шукаємо R", "R = V / I", BLUE)]
    for i, (lab, f, col) in enumerate(boxes):
        y = 110 + i * 66
        s += rect(420, y, 340, 54, "#fafafa", col, 1.8, 10)
        s += text(450, y + 32, lab, 12.5, col, "start", "bold")
        s += text(620, y + 34, f, 19, INK, "middle", "bold")
    save("fig-3-2-1-three-forms.svg", s)


# ── Рис. 3.2.2 — лінійність омічного елемента ────────────────────────────────
def fig32_linearity():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Омічний елемент: I пропорційний V (пряма через нуль)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "графік I(V) — пряма; її нахил і є провідність 1/R", 12, GREY, "middle", style="italic")
    gx0, gy0, gx1, gy1 = 110, 330, 700, 100
    s += arrow(gx0, gy0, gx1 + 10, gy0, INK, 2)
    s += arrow(gx0, gy0, gx0, gy1 - 6, INK, 2)
    s += text(gx1 + 12, gy0 + 4, "V", 14, INK, "start", "bold", "italic")
    s += text(gx0 - 12, gy1, "I", 14, INK, "end", "bold", "italic")
    # дві прямі
    s += line(gx0, gy0, gx1 - 30, gy1 + 20, GREEN, 2.8)
    s += text(gx1 - 30, gy1 + 8, "малий R", 12, GREEN, "start", "bold")
    s += text(gx1 - 30, gy1 + 24, "(крутий нахил)", 10.5, GREY, "start")
    s += line(gx0, gy0, gx1, gy0 - 90, "#8a52c0", 2.8)
    s += text(gx1 - 6, gy0 - 96, "великий R", 12, "#8a52c0", "end", "bold")
    s += text(gx1 - 6, gy0 - 80, "(пологий)", 10.5, GREY, "end")
    s += rect(150, 348, W - 300, 26, "#eef7f0", GREEN, 1.4, 8)
    s += text(W / 2, 366, "удвічі більша напруга → удвічі більший струм (R сталий)", 11.5, INK, "middle", "bold")
    save("fig-3-2-2-linearity.svg", s)


# ── Рис. 3.2.3 — омічний проти неомічного ────────────────────────────────────
def fig32_ohmic_nonohmic():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Омічний — пряма; неомічний — крива", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у діода й лампи опір «пливе» — їхні ВАХ не прямі", 12, GREY, "middle", style="italic")
    gx0, gy0, gx1, gy1 = 110, 320, 720, 100
    s += arrow(gx0, gy0, gx1 + 10, gy0, INK, 2)
    s += arrow(gx0, gy0, gx0, gy1 - 6, INK, 2)
    s += text(gx1 + 12, gy0 + 4, "V", 14, INK, "start", "bold", "italic")
    s += text(gx0 - 12, gy1, "I", 14, INK, "end", "bold", "italic")
    span = gx1 - gx0 - 40
    h = gy0 - gy1 - 20
    # омічний — пряма
    s += line(gx0, gy0, gx0 + span, gy0 - h * 0.8, INK, 2.6)
    s += text(gx0 + span, gy0 - h * 0.8 - 6, "омічний (резистор)", 11.5, INK, "end", "bold")
    # діод — поріг, тоді різко
    pts = []
    for i in range(0, 101):
        v = i / 100.0
        cur = 0.0 if v < 0.45 else (v - 0.45) ** 2 * 5.5
        cur = min(cur, 1.0)
        pts.append((gx0 + v * span, gy0 - cur * h))
    s += polyline(pts, RED, 2.6)
    s += text(gx0 + 0.62 * span, gy1 + 30, "діод", 11.5, RED, "middle", "bold")
    s += text(gx0 + 0.45 * span, gy0 + 16, "поріг", 10, RED, "middle")
    # лампа — сублінійна (загинається)
    pts2 = []
    for i in range(0, 101):
        v = i / 100.0
        cur = (v ** 0.55) * 0.62
        pts2.append((gx0 + v * span, gy0 - cur * h))
    s += polyline(pts2, ORANGE, 2.6)
    s += text(gx0 + span, gy0 - 0.62 * h + 4, "лампа (R↑ з нагрівом)", 11.5, ORANGE, "end", "bold")
    save("fig-3-2-3-ohmic-nonohmic.svg", s)


# ── Рис. 3.2.4 — струмообмежувальний резистор для світлодіода ─────────────────
def fig32_led_resistor():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Класика: резистор, що береже світлодіод", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "резистор бере на себе зайву напругу, щоб струм був безпечним", 12, GREY, "middle", style="italic")
    L, R, T, B = 150, 560, 110, 270
    # джерело 5 В
    s += line(L, T, L, 175, INK, 2.4)
    s += line(L, 205, L, B, INK, 2.4)
    s += line(L - 16, 175, L + 16, 175, INK, 3)
    s += line(L - 9, 191, L + 9, 191, INK, 5)
    s += line(L - 16, 194, L + 16, 194, INK, 3)
    s += line(L - 9, 210, L + 9, 210, INK, 5)
    s += text(L - 30, 185, "5 В", 12, INK, "end", "bold")
    # резистор зверху
    s += line(L, T, 290, T, INK, 2.4)
    s += _resistor(290, T, 80, 24, "R")
    s += line(370, T, R, T, INK, 2.4)
    # світлодіод праворуч
    s += line(R, T, R, 150, INK, 2.4)
    s += f'<path d="M {R-15},155 L {R+15},155 L {R},185 Z" fill="#fdeeee" stroke="{RED}" stroke-width="2"/>\n'
    s += line(R - 15, 185, R + 15, 185, RED, 3)
    s += arrow(R + 20, 160, R + 34, 150, RED, 1.6)
    s += text(R + 40, 178, "LED", 11, RED, "start", "bold")
    s += text(R + 40, 194, "~2 В", 10.5, GREY, "start")
    s += line(R, 185, R, B, INK, 2.4)
    s += line(L, B, R, B, INK, 2.4)
    s += arrow(210, T, 250, T, RED, 2.2)
    s += text(230, T - 12, "I = 10 мА", 11, RED, "middle", "bold")
    # розрахунок
    s += rect(610, 110, 200, 150, "#f4f7f4", GREEN, 1.8, 12)
    s += text(710, 136, "розрахунок R", 12.5, INK, "middle", "bold")
    s += text(626, 164, "на R падає:", 11, GREY, "start")
    s += text(626, 184, "5 − 2 = 3 В", 13, INK, "start", "bold")
    s += text(626, 212, "R = U_R / I", 12, GREY, "start")
    s += text(626, 234, "= 3 / 0.01 = 300 Ом", 13.5, GREEN, "start", "bold")
    save("fig-3-2-4-led-resistor.svg", s)


def _wire(x, y, length, rad, fill=COPPER, stroke="#9c6b48"):
    out = rect(x, y - rad, length, 2 * rad, fill, "none", 0)
    out += line(x, y - rad, x + length, y - rad, stroke, 2)
    out += line(x, y + rad, x + length, y + rad, stroke, 2)
    out += f'<ellipse cx="{x+length}" cy="{y}" rx="6" ry="{rad}" fill="#e0a878" stroke="{stroke}" stroke-width="2"/>\n'
    out += f'<ellipse cx="{x}" cy="{y}" rx="6" ry="{rad}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>\n'
    return out


# ── Рис. 3.3.1 — формула R = ρ·L/A ───────────────────────────────────────────
def fig33_formula():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Від чого залежить опір: R = ρ · L / A", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "матеріал, довжина й переріз дроту разом задають його опір", 12, GREY, "middle", style="italic")
    # дріт
    s += _wire(150, 160, 360, 30)
    s += line(150, 210, 510, 210, INK, 1.6)
    s += line(150, 204, 150, 216, INK, 1.6)
    s += line(510, 204, 510, 216, INK, 1.6)
    s += text(330, 228, "довжина L", 12, INK, "middle", "bold")
    s += circle(560, 160, 30, "#fde0d6", "#9c6b48", 2)
    s += text(560, 165, "A", 14, "#5a3a26", "middle", "bold")
    s += text(560, 210, "переріз A", 11.5, INK, "middle", "bold")
    s += text(330, 120, "матеріал: питомий опір ρ", 11.5, GREEN, "middle", "bold")
    # формула
    s += rect(120, 270, W - 240, 70, "#f4f7f4", GREEN, 1.8, 12)
    s += text(W / 2, 300, "R = ρ · L / A", 22, INK, "middle", "bold")
    s += text(W / 2, 326, "ρ — матеріал (§2.10) · L↑ → R↑ (прямо) · A↑ → R↓ (обернено)",
              12, GREY, "middle", style="italic")
    save("fig-3-3-1-formula.svg", s)


# ── Рис. 3.3.2 — вплив довжини й перерізу ────────────────────────────────────
def fig33_length_area():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Довжина — прямо, переріз — обернено", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "удвічі довший — удвічі більший опір; удвічі товщий — удвічі менший", 12, GREY, "middle", style="italic")
    # довжина
    s += text(210, 100, "ДОВЖИНА", 13, INK, "middle", "bold")
    s += _wire(80, 150, 120, 18)
    s += text(140, 180, "L → R", 12, INK, "middle", "bold")
    s += _wire(80, 230, 260, 18)
    s += text(210, 260, "2L → 2R  (як два послідовно)", 11.5, RED, "middle", "bold")
    # переріз
    s += line(W / 2, 90, W / 2, 290, FAINT, 1.5)
    s += text(615, 100, "ПЕРЕРІЗ", 13, INK, "middle", "bold")
    s += _wire(520, 150, 180, 12)
    s += text(610, 178, "A → R", 12, INK, "middle", "bold")
    s += _wire(520, 235, 180, 24)
    s += text(610, 280, "2A → R/2  (як два паралельно)", 11.5, GREEN, "middle", "bold")
    s += rect(150, 320, W - 300, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 342, "Увага: переріз ∝ діаметру², тож удвічі тонший дріт (½ діаметра) → A менша вчетверо → R більший у 4 рази.",
              11, INK, "middle", "bold")
    save("fig-3-3-2-length-area.svg", s)


# ── Рис. 3.3.3 — калібр дроту (AWG) ──────────────────────────────────────────
def fig33_awg():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Калібр дроту (AWG): товщий — менший опір, більший струм", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "більший номер AWG = тонший дріт; кожні ~3 кроки удвічі міняють переріз", 12, GREY, "middle", style="italic")
    items = [("10 AWG", 26, "~30 А", "товстий"),
             ("14 AWG", 18, "~15 А", ""),
             ("18 AWG", 12, "~7 А", ""),
             ("22 AWG", 8, "~3 А", ""),
             ("28 AWG", 5, "~0.7 А", "тонкий")]
    x0 = 110
    for i, (g, r, cur, note) in enumerate(items):
        x = x0 + i * 145
        s += circle(x, 170, r, COPPER, "#9c6b48", 2)
        s += text(x, 215, g, 13, INK, "middle", "bold")
        s += text(x, 235, cur, 12, GREEN, "middle", "bold")
        if note:
            s += text(x, 255, note, 11, GREY, "middle", style="italic")
    s += arrow(110, 290, 700, 290, INK, 2)
    s += text(120, 312, "товщий — менший R — більший струм", 11.5, GREEN, "start", "bold")
    s += text(700, 312, "тонший — більший R", 11.5, RED, "end", "bold")
    save("fig-3-3-3-awg.svg", s)


# ── Рис. 3.3.4 — падіння напруги на довгому дроті ────────────────────────────
def fig33_voltage_drop():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Падіння напруги на довгому дроті", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "сам дріт має опір; на довгому тонкому дроті частина напруги «губиться» (I·R)", 12, GREY, "middle", style="italic")
    # джерело
    s += line(110, 120, 110, 220, INK, 2.4)
    s += line(94, 160, 126, 160, INK, 3); s += line(101, 176, 119, 176, INK, 5)
    s += text(90, 150, "12 В", 11.5, INK, "end", "bold")
    # довгі дроти (з опором)
    s += line(110, 120, 250, 120, COPPER, 3)
    s += _resistor(250, 120, 70, 18, "")
    s += text(285, 100, "R_дроту", 10.5, RED, "middle", "bold")
    s += line(320, 120, 600, 120, COPPER, 3)
    s += line(110, 220, 600, 220, COPPER, 3)
    s += text(420, 108, "довгий тонкий дріт", 11, GREY, "middle", style="italic")
    # навантаження
    s += rect(600, 130, 44, 80, "#fff7ef", "#c89b5a", 2.2, 6)
    s += text(622, 175, "при-", 10.5, INK, "middle")
    s += text(622, 190, "лад", 10.5, INK, "middle")
    s += line(600, 120, 600, 130, INK, 2.4); s += line(600, 210, 600, 220, INK, 2.4)
    s += text(680, 165, "дістає < 12 В", 12, RED, "start", "bold")
    s += arrow(160, 120, 200, 120, RED, 2.2)
    s += text(180, 138, "I", 11, RED, "middle", "bold", "italic")
    s += rect(120, 270, W - 240, 50, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 292, "Тонкий довгий дріт = великий R → велике падіння I·R → прилад «недоїдає», а дріт гріється.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 310, "Тому для довгих ліній і великих струмів беруть товстий дріт (малий R).",
              11, GREY, "middle", style="italic")
    save("fig-3-3-4-voltage-drop.svg", s)


# ── Рис. 3.4.1 — R(T): закон і дві поведінки ─────────────────────────────────
def fig34_rt_law():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Опір залежить від температури: R(T) = R₀·[1 + α·(T−T₀)]", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "метал: R росте з нагрівом (α>0, PTC); напівпровідник: падає (α<0, NTC)", 12, GREY, "middle", style="italic")
    gx0, gx1, gy0, gy1 = 110, 560, 320, 110
    s += arrow(gx0, gy0, gx1 + 10, gy0, INK, 2)
    s += arrow(gx0, gy0, gx0, gy1 - 6, INK, 2)
    s += text(gx1 + 12, gy0 + 4, "T", 13, INK, "start", "bold", "italic")
    s += text(gx0 - 12, gy1, "R", 13, INK, "end", "bold", "italic")
    s += line(gx0 + 20, gy0 - 40, gx1 - 20, gy1 + 40, RED, 2.8)
    s += text(gx1 - 20, gy1 + 28, "метал (PTC)", 12, RED, "end", "bold")
    pts = [(gx0 + 20 + i * 5, gy1 + 40 + 200 * math.exp(-i / 16.0)) for i in range(0, 87)]
    s += polyline(pts, "#8a52c0", 2.8)
    s += text(gx0 + 150, gy0 - 26, "напівпровідник (NTC)", 12, "#8a52c0", "start", "bold")
    s += rect(600, 130, 200, 160, "#f4f7f4", GREEN, 1.6, 12)
    s += text(700, 156, "α — темп. коеф.", 12, INK, "middle", "bold")
    s += text(616, 182, "мідь: ≈ +0.004 /°C", 11.5, RED, "start")
    s += text(616, 204, "(тобто +0.4% на °C)", 10.5, GREY, "start")
    s += text(616, 232, "термістор NTC:", 11.5, "#8a52c0", "start")
    s += text(616, 252, "сильний від'ємний α", 10.5, GREY, "start")
    s += text(616, 280, "R₀ — опір за T₀", 11, INK, "start")
    save("fig-3-4-1-rt-law.svg", s)


# ── Рис. 3.4.2 — холодна vs гаряча нитка ─────────────────────────────────────
def fig34_filament():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Холодна нитка — малий опір → кидок струму", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у лампи розжарення гарячий опір у ~10–15 разів більший за холодний", 12, GREY, "middle", style="italic")
    # стовпчики опору
    s += text(200, 100, "опір нитки", 12.5, INK, "middle", "bold")
    s += rect(140, 250, 60, 40, "#eef2fb", BLUE, 2, 4)
    s += text(170, 274, "холодна", 10.5, BLUE, "middle", "bold")
    s += text(170, 306, "R ≈ 30 Ом", 11, INK, "middle")
    s += rect(250, 130, 60, 160, "#fdeeee", RED, 2, 4)
    s += text(280, 210, "гаряча", 10.5, RED, "middle", "bold")
    s += text(280, 306, "R ≈ 450 Ом", 11, INK, "middle")
    # струм
    s += text(610, 100, "струм при 230 В", 12.5, INK, "middle", "bold")
    s += rect(680, 130, 60, 160, "#fdeeee", RED, 2, 4)
    s += text(710, 210, "кидок", 10.5, RED, "middle", "bold")
    s += text(710, 306, "≈ 7.7 А", 11, RED, "middle", "bold")
    s += rect(560, 250, 60, 40, "#eef7f0", GREEN, 2, 4)
    s += text(590, 274, "робочий", 10, GREEN, "middle", "bold")
    s += text(590, 306, "≈ 0.5 А", 11, INK, "middle")
    s += text(W / 2, H - 14, "Тому лампи розжарення найчастіше перегорають саме при ввімкненні — від кидка струму.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-4-2-filament.svg", s)


def _loop(cx, cy, r, color, label, steps, conv):
    out = ""
    for i in range(0, 360, 12):
        a0 = math.radians(i)
        a1 = math.radians(i + 8)
        out += line(cx + r * math.cos(a0), cy + r * math.sin(a0), cx + r * math.cos(a1), cy + r * math.sin(a1), color, 2.4)
    # стрілка напрямку
    aa = math.radians(-50)
    out += arrow(cx + r * math.cos(aa - 0.18), cy + r * math.sin(aa - 0.18),
                 cx + r * math.cos(aa), cy + r * math.sin(aa), color, 2.4)
    angs = [-90, -10, 90, 170]
    for (txt, ang) in zip(steps, angs):
        x = cx + (r + 4) * math.cos(math.radians(ang))
        y = cy + (r + 4) * math.sin(math.radians(ang))
        ax = "middle"
        out += rect(x - 60, y - 16, 120, 32, "#fff", color, 1.6, 8)
        out += text(x, y + 4, txt, 10.5, INK, ax, "bold")
    out += text(cx, cy + 4, label, 12.5, color, "middle", "bold")
    out += text(cx, cy + 22, conv, 10, GREY, "middle", style="italic")
    return out


# ── Рис. 3.4.3 — теплова втеча (NTC) ─────────────────────────────────────────
def fig34_runaway():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Теплова втеча (NTC): небезпечний зворотний зв'язок", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нагрів знижує опір — і струм росте ще більше, аж до руйнування", 12, GREY, "middle", style="italic")
    s += _loop(380, 230, 110, RED, "РОЗГІН ↑",
               ["струм I ↑", "нагрів I²R ↑", "опір R ↓ (NTC)", "ще більший I ↑"], "(без межі)")
    s += text(W / 2, H - 18, "Тому потужні напівпровідники й NTC-кола боронять від перегріву (радіатори, обмеження струму).",
              11, GREY, "middle", style="italic")
    save("fig-3-4-3-runaway.svg", s)


# ── Рис. 3.4.4 — самостабілізація (PTC) ──────────────────────────────────────
def fig34_selfreg():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Самостабілізація (PTC): зворотний зв'язок-гальмо", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нагрів ПІДВИЩУЄ опір — і струм сам спадає, тримаючись безпечного рівня", 12, GREY, "middle", style="italic")
    s += _loop(380, 220, 110, GREEN, "ГАЛЬМО ↓",
               ["струм I ↑", "нагрів I²R ↑", "опір R ↑ (PTC)", "струм I ↓"], "(саме спиняється)")
    s += rect(140, 340, W - 280, 44, "#eef7f0", GREEN, 1.6, 10)
    s += text(W / 2, 362, "На цьому — самовідновні запобіжники (поліфьюз) і самообмежувальні нагрівачі:",
              11, INK, "middle", "bold")
    s += text(W / 2, 378, "перегрілося → опір зріс → струм упав → охололо. Без згоряння.", 10.5, GREY, "middle", style="italic")
    save("fig-3-4-4-selfreg.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до §3.4 — Надпровідність (Камерлінг-Оннес, 1911).  Рис. 3.4і.N
# ════════════════════════════════════════════════════════════════════════════

def _circ_arrow(cx, cy, r, color, a0_deg, a1_deg, w=3.0):
    """Дуга кола cx,cy,r від кута a0 до a1 (за годинниковою) зі стрілкою."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} 1 {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def _snow(x, y, R, color=BLUE, w=2):
    """Сніжинка-зірочка (три перехрещені лінії) — позначка холоду."""
    out = ""
    for ang in (0, 60, 120):
        a = math.radians(ang)
        dx, dy = R * math.cos(a), R * math.sin(a)
        out += line(x - dx, y - dy, x + dx, y + dy, color, w)
    return out


# ── Рис. 3.4і.1 — відкриття Оннеса: опір ртуті стрибком до нуля ───────────────
def fig_onnes_drop():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 32, "1911: опір ртуті раптово зник при 4.2 К", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "Оннес чекав плавного спаду — а опір стрибком упав до нуля",
              12.5, GREY, "middle", style="italic")

    ox, oy, top = 130, 340, 100      # початок осей (R=0) і верх поля

    def X(t):
        return ox + t * 53.0

    # осі
    s += arrow(ox, oy, 700, oy, INK, 2)
    s += arrow(ox, oy, ox, top, INK, 2)
    s += text(706, oy + 4, "T, К", 12, INK, "start")
    s += text(ox - 8, top - 6, "Опір R", 12, INK, "end")
    for t in (2, 4, 6, 8, 10):
        s += line(X(t), oy, X(t), oy + 5, INK, 1.5)
        s += text(X(t), oy + 19, str(t), 10.5, GREY, "middle")

    xc = X(4.2)
    s += line(xc, oy, xc, top + 6, GREY, 1.3, "3,4")
    s += text(xc, top - 4, "≈ 4.2 К", 11, GREY, "middle", "bold")

    # фактична крива ртуті: плавний спад → коліно
    hg = [(X(10), 150), (X(8.5), 172), (X(7), 200), (X(6), 224),
          (X(5), 256), (X(4.5), 282), (xc, 300)]
    s += polyline(hg, INK, 3.2)
    # вертикальний стрибок до нуля при Tc
    s += line(xc, 300, xc, oy, GREEN, 4)
    # надпровідна «нульова» гілка вздовж осі
    s += line(ox, oy, xc, oy, GREEN, 4)
    s += text((ox + xc) / 2, oy - 8, "R = 0  (надпровідність)", 11, GREEN, "middle", "bold")
    s += text(X(9.2), 142, "ртуть (Hg)", 11, INK, "middle", "bold")

    # виноска до стрибка
    s += arrow(xc + 86, 248, xc + 5, 292, RED, 2.2)
    s += text(xc + 92, 244, "стрибок до 0", 12.5, RED, "start", "bold")

    # альтернативи, яких чекали (пунктир), від «коліна»
    kx, ky = X(4.5), 282
    s += polyline([(kx, ky), (X(3.4), 300), (X(2), 318), (ox, oy)], BLUE, 2, "5,4")
    s += text(ox + 6, oy - 6, "чекали: плавно до 0", 10, BLUE, "start", style="italic")
    s += polyline([(kx, ky), (X(3), 288), (X(1.2), 290), (ox, 291)], GREY, 2, "2,3")
    s += text(ox + 6, 284, "або залишковий опір", 10, GREY, "start", style="italic")
    s += polyline([(kx, ky), (X(3.4), 284), (X(2.2), 268), (X(1), 232), (ox, 208)], RED, 2, "5,4")
    s += text(ox + 4, 200, "Кельвін: мав би ЗРОСТИ", 10, RED, "start", style="italic")

    s += text(W / 2, H - 14,
              "Нова, небачена властивість речовини: нижче критичної температури опір — точно нуль.",
              11, GREY, "middle", style="italic")
    save("fig-3-4i-1-onnes-drop.svg", s)


# ── Рис. 3.4і.2 — вічний струм: R = 0 не потребує джерела ─────────────────────
def fig_persistent_current():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 32, "Вічний струм: коли R = 0, коло не потребує батареї", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "у надпровідному кільці пущений струм тече роками сам — гасити його нема чому",
              12.5, GREY, "middle", style="italic")
    s += line(W / 2, 84, W / 2, H - 64, FAINT, 1.4, "4,5")

    # ── звичайне кільце (ліворуч): R > 0 ──
    cx, cy, r = 235, 240, 78
    s += circle(cx, cy, r, "none", INK, 5)
    s += _circ_arrow(cx, cy, r, RED, -45, 205, 3.2)
    # батарея вгорі (дві пластини)
    s += line(cx - 22, cy - r - 2, cx + 22, cy - r - 2, INK, 2.2)   # +  довга тонка
    s += line(cx - 12, cy - r + 8, cx + 12, cy - r + 8, INK, 4.2)   # −  коротка товста
    s += arrow(cx + 86, cy - r - 26, cx + 26, cy - r, INK, 1.8)
    s += text(cx + 92, cy - r - 30, "потрібне джерело", 11, INK, "start", "bold")
    # тепло
    s += heatwaves(cx, cy + r + 40, 3, ORANGE)
    s += text(cx, cy + r + 60, "тепло I²R — струм гасне", 11, ORANGE, "middle", "bold")
    s += text(cx, cy + 6, "R > 0", 22, INK, "middle", "bold")
    s += text(cx, 392, "Звичайне кільце: струм живе лише поки живить джерело;", 11, GREY, "middle", style="italic")
    s += text(cx, 408, "опір з’їдає енергію теплом.", 11, GREY, "middle", style="italic")

    # ── надпровідне кільце (праворуч): R = 0 ──
    dx, dy = 585, 240
    s += circle(dx, dy, r, "none", GREEN, 5)
    s += _circ_arrow(dx, dy, r, GREEN, -45, 235, 3.4)
    s += _circ_arrow(dx, dy, r, GREEN, 135, 385, 3.4)
    s += _snow(dx, dy - r, 12, BLUE, 2)
    s += text(dx, dy - r - 22, "≈ 4.2 К (рідкий гелій)", 11, BLUE, "middle", "bold")
    s += text(dx, dy + 6, "R = 0", 22, GREEN, "middle", "bold")
    s += text(dx, 392, "Надпровідне кільце: пущений струм тече роками сам —", 11, GREEN, "middle", style="italic")
    s += text(dx, 408, "немає опору, отже немає чому його гасити.", 11, GREEN, "middle", style="italic")
    save("fig-3-4i-2-persistent-current.svg", s)


# ── Рис. 3.4і.3 — де працює надпровідність (і яка ціна) ───────────────────────
def fig_super_apps():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 32, "Де працює надпровідність — і яка її ціна", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "нульовий опір → величезні струми й магнітні поля без втрат",
              12.5, GREY, "middle", style="italic")

    iy = 165
    # 1) МРТ-томограф
    c1 = 120
    s += circle(c1, iy, 44, "none", INK, 5)
    s += circle(c1, iy, 30, "none", GREY, 1.5)
    s += rect(c1 - 52, iy - 7, 104, 14, "#dbe6f5", BLUE, 2, 7)   # стіл-пацієнт крізь тунель
    s += circle(c1 - 40, iy, 9, "#dbe6f5", BLUE, 2)
    s += text(c1, 250, "МРТ-томограф", 12.5, INK, "middle", "bold")
    s += text(c1, 268, "магніти без втрат", 11, GREY, "middle")

    # 2) Маглев (ефект Мейснера)
    c2 = 350
    s += rect(c2 - 45, iy - 18, 90, 30, "#e9eef7", BLUE, 2.2, 7)  # вагон
    s += rect(c2 - 52, iy + 34, 104, 9, "#d8d8d8", GREY, 1.5, 2)  # колія
    for ax in (c2 - 28, c2, c2 + 28):
        s += arrow(ax, iy + 32, ax, iy + 16, GREEN, 2)           # левітація
    s += text(c2, 250, "Маглев", 12.5, INK, "middle", "bold")
    s += text(c2, 268, "ефект Мейснера: магніт ширяє", 11, GREY, "middle")

    # 3) Прискорювачі
    c3 = 580
    s += circle(c3, iy, 44, "none", INK, 5)
    s += _circ_arrow(c3, iy, 44, RED, -20, 150, 2.6)
    for ang in (30, 150, 270):
        a = math.radians(ang)
        s += circle(c3 + 44 * math.cos(a), iy + 44 * math.sin(a), 4.5, RED, RED, 1)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        s += line(c3 + 50 * math.cos(a), iy + 50 * math.sin(a),
                  c3 + 58 * math.cos(a), iy + 58 * math.sin(a), BLUE, 2.4)
    s += text(c3, 250, "Прискорювачі (LHC)", 12.5, INK, "middle", "bold")
    s += text(c3, 268, "магніти гнуть пучок", 11, GREY, "middle")

    # 4) Передача без втрат
    c4 = 790

    def _tower(x):
        out = line(x - 12, iy + 40, x, iy - 20, INK, 2) + line(x + 12, iy + 40, x, iy - 20, INK, 2)
        out += line(x - 7, iy + 12, x + 7, iy + 12, INK, 1.6)
        return out

    s += _tower(c4 - 30)
    s += _tower(c4 + 30)
    s += line(c4 - 30, iy - 20, c4 + 30, iy - 20, RED, 2.4)
    s += text(c4, iy - 30, "0 % втрат", 11, GREEN, "middle", "bold")
    s += text(c4, 250, "Лінії без втрат", 12.5, INK, "middle", "bold")
    s += text(c4, 268, "поки що мрія", 11, GREY, "middle")

    # застереження-смуга
    s += rect(60, 318, W - 120, 86, "#fbecea", RED, 1.8, 12)
    s += _snow(96, 348, 11, BLUE, 2)
    s += text(120, 346, "Ціна — екстремальний холод:", 13.5, RED, "start", "bold")
    s += text(120, 370, "рідкий гелій ~4 К, або «високотемпературні» надпровідники ~90 К (рідкий азот).",
              11.5, INK, "start")
    s += text(120, 390, "Кімнатної надпровідності за нормального тиску досі немає — тому застосувань і досі небагато.",
              11.5, INK, "start")
    save("fig-3-4i-3-super-apps.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §3.5 — Потужність: P = V·I  (форми I²R, V²/R).  Рис. 3.5.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.5.1 — звідки P = V·I: енергія за секунду ───────────────────────────
def fig35_power_def():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 32, "Потужність — це енергія за секунду: чому P = V·I", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "формула не з повітря — вона збирається з двох означень Розділу 1",
              12.5, GREY, "middle", style="italic")

    def card(cx, w, eq, cap, accent):
        o = rect(cx - w / 2, 86, w, 52, "#f6f8fc", accent, 2, 10)
        o += text(cx, 118, eq, 20, INK, "middle", "bold")
        o += text(cx, 156, cap, 10.5, GREY, "middle", style="italic")
        return o

    s += card(165, 220, "P = W / t", "потужність = енергія за час  [Вт = Дж/с]", INK)
    s += card(410, 190, "W = q · V", "енергія заряду в полі (Гл. 1)", RED)
    s += card(645, 190, "I = q / t", "струм = заряд за час", BLUE)

    s += arrow(410, 172, 410, 196, GREY, 1.8)
    s += text(W / 2, 216, "підставляємо  W = q·V  і групуємо  q/t = I :", 12.5, INK, "middle", style="italic")
    s += text(W / 2, 252, "P = W/t = (q·V)/t = (q/t)·V = I·V", 19, INK, "middle", "bold")

    s += rect(W / 2 - 175, 284, 350, 62, "#eef7f0", GREEN, 2.4, 14)
    s += text(W / 2, 325, "P = V · I", 30, GREEN, "middle", "bold")
    s += text(W / 2, 386,
              "Одиниця — ват (Вт):  1 Вт = 1 В × 1 А = 1 Дж/с.  Назва — на честь Джеймса Уатта.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-5-1-power-def.svg", s)


# ── Рис. 3.5.2 — три форми: P = VI = I²R = V²/R ───────────────────────────────
def fig35_three_forms():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 32, "Три обличчя однієї потужності: P = V·I = I²R = V²/R", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "підставляємо закон Ома — і дістаємо форму під ті величини, що відомі",
              12.5, GREY, "middle", style="italic")

    s += rect(W / 2 - 110, 78, 220, 56, "#eef7f0", GREEN, 2.4, 12)
    s += text(W / 2, 108, "P = V · I", 25, GREEN, "middle", "bold")
    s += text(W / 2, 150, "загальна форма — діє завжди", 11.5, GREY, "middle", style="italic")

    # ліва гілка — через V = I·R
    s += arrow(W / 2 - 72, 134, 250, 196, INK, 1.9)
    s += text(312, 166, "V = I·R", 12.5, RED, "middle", "bold")
    s += rect(110, 198, 250, 56, "#fbecea", RED, 2, 12)
    s += text(235, 232, "P = I² · R", 24, INK, "middle", "bold")
    s += text(235, 278, "коли відомі струм I та опір R", 11, GREY, "middle")
    s += text(235, 296, "(послідовне коло, нагрів дроту)", 10.5, GREY, "middle", style="italic")

    # права гілка — через I = V/R
    s += arrow(W / 2 + 72, 134, 570, 196, INK, 1.9)
    s += text(508, 166, "I = V/R", 12.5, BLUE, "middle", "bold")
    s += rect(460, 198, 250, 56, "#eaf0fb", BLUE, 2, 12)
    s += text(585, 232, "P = V² / R", 24, INK, "middle", "bold")
    s += text(585, 278, "коли відомі напруга V та опір R", 11, GREY, "middle")
    s += text(585, 296, "(на фіксованому живленні)", 10.5, GREY, "middle", style="italic")

    s += rect(W / 2 - 255, 336, 510, 46, "#fffdf2", ORANGE, 1.6, 10)
    s += text(W / 2, 358, "Усі три дають те саме число — обирай ту, де менше рахувати.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 375, "Відомі V та I → перша; струм та R → друга; напруга та R → третя.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-5-2-three-forms.svg", s)


# ── Рис. 3.5.3 — приклад: 12 В на 100 Ω, три способи → одне число ─────────────
def fig35_worked():
    W, H = 840, 360
    s = header(W, H)
    s += text(W / 2, 32, "Один приклад, три формули — одна відповідь", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "12 В на резисторі 100 Ω: рахуємо потужність трьома способами",
              12.5, GREY, "middle", style="italic")

    bx = 110
    s += line(bx, 120, bx, 240, INK, 2.4)
    s += line(bx - 16, 168, bx + 16, 168, INK, 3)
    s += line(bx - 9, 184, bx + 9, 184, INK, 5)
    s += text(bx - 22, 162, "12 В", 12, INK, "end", "bold")
    s += line(bx, 120, 250, 120, COPPER, 3)
    s += _resistor(250, 120, 80, 24, "R = 100 Ω")
    s += line(330, 120, 420, 120, COPPER, 3)
    s += line(420, 120, 420, 240, INK, 2.4)
    s += line(bx, 240, 420, 240, COPPER, 3)
    s += arrow(150, 120, 196, 120, RED, 2.2)
    s += text(173, 108, "I", 12, RED, "middle", "bold", "italic")
    s += text(265, 178, "I = V/R = 12/100 = 0.12 А", 11.5, RED, "middle", "bold")

    px = 500
    s += rect(px - 22, 92, 344, 152, "#f6f8fc", INK, 1.6, 12)
    rows = [("P = V·I", "= 12 × 0.12"), ("P = I²R", "= 0.12² × 100"), ("P = V²/R", "= 12² / 100")]
    yy = 130
    for a, b in rows:
        s += text(px, yy, a, 15, INK, "start", "bold")
        s += text(px + 96, yy, b, 13.5, GREY, "start")
        s += text(px + 286, yy, "= 1.44 Вт", 14, GREEN, "end", "bold")
        yy += 40
    s += rect(px + 80, 258, 200, 44, "#eef7f0", GREEN, 2.2, 12)
    s += text(px + 180, 286, "P = 1.44 Вт  ✓", 18, GREEN, "middle", "bold")
    s += text(W / 2, 338, "Різні формули — той самий результат: це лише три погляди на P = V·I.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-5-3-worked.svg", s)


# ── Рис. 3.5.4 — куди йде тепло: послідовно (I²R) vs паралельно (V²/R) ─────────
def fig35_choose():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 32, "Де виділяється тепло — на великому опорі чи на малому?", 19.5, INK, "middle", "bold")
    s += text(W / 2, 54, "відповідь залежить від з'єднання: що в них спільне — струм чи напруга",
              12.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 70, FAINT, 1.4, "4,5")

    # ── ліворуч: послідовно, спільний струм ──
    s += text(215, 100, "Послідовно — спільний струм I", 14, INK, "middle", "bold")
    s += line(70, 135, 70, 230, INK, 2.2)
    s += line(58, 172, 82, 172, INK, 2.6)
    s += line(63, 186, 77, 186, INK, 4.2)
    s += line(70, 135, 150, 135, COPPER, 2.6)
    s += circle(185, 135, 17, "#fbe2d2", "none", 0)            # ореол тепла R₁ (малий)
    s += _resistor(150, 135, 70, 22, "R₁ = 10 Ω")
    s += line(220, 135, 300, 135, COPPER, 2.6)
    s += circle(335, 135, 30, "#f2b3aa", "none", 0)            # ореол тепла R₂ (великий)
    s += _resistor(300, 135, 70, 22, "R₂ = 100 Ω")
    s += line(370, 135, 370, 230, INK, 2.2)
    s += line(70, 230, 370, 230, COPPER, 2.6)
    s += arrow(95, 135, 132, 135, RED, 2)
    s += text(335, 178, "гарячіше ×10", 11, RED, "middle", "bold")
    s += text(215, 322, "P = I²R, струм однаковий →", 12.5, INK, "middle", "bold")
    s += text(215, 342, "сильніше гріється БІЛЬШИЙ опір (R₂)", 12, RED, "middle", "bold")

    # ── праворуч: паралельно, спільна напруга ──
    s += text(645, 100, "Паралельно — спільна напруга V", 14, INK, "middle", "bold")
    s += line(500, 135, 500, 250, INK, 2.2)
    s += line(488, 178, 512, 178, INK, 2.6)
    s += line(493, 192, 507, 192, INK, 4.2)
    s += line(500, 135, 800, 135, COPPER, 2.6)
    s += line(500, 250, 800, 250, COPPER, 2.6)
    # гілка R₁ (малий опір — гарячий)
    s += circle(620, 192, 30, "#f2b3aa", "none", 0)
    s += rect(620 - 13, 162, 26, 60, "#fff", INK, 2, 3)
    s += line(620, 135, 620, 162, COPPER, 2.4)
    s += line(620, 222, 620, 250, COPPER, 2.4)
    s += text(620, 270, "R₁ = 10 Ω", 11, INK, "middle", "bold", "italic")
    s += text(620, 150, "гарячіше ×10", 10, RED, "middle", "bold")
    # гілка R₂ (великий опір — холодніший)
    s += circle(740, 192, 16, "#fbe2d2", "none", 0)
    s += rect(740 - 13, 162, 26, 60, "#fff", INK, 2, 3)
    s += line(740, 135, 740, 162, COPPER, 2.4)
    s += line(740, 222, 740, 250, COPPER, 2.4)
    s += text(740, 270, "R₂ = 100 Ω", 11, INK, "middle", "bold", "italic")
    s += text(645, 322, "P = V²/R, напруга однакова →", 12.5, INK, "middle", "bold")
    s += text(645, 342, "сильніше гріється МЕНШИЙ опір (R₁)", 12, RED, "middle", "bold")

    s += text(W / 2, 384, "Жодного парадоксу: дивись, що спільне. Спільний I → I²R; спільна V → V²/R.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-5-4-choose.svg", s)


# ── Рис. 3.5.5 — відчути ват: логарифмічна шкала потужностей ──────────────────
def fig35_watt_scale():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 32, "Відчути ват: скільки це — один Вт?", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "логарифмічна шкала: крок праворуч — удесятеро більша потужність",
              12.5, GREY, "middle", style="italic")
    x0, x1, y = 90, 790, 222
    pe0, pe1 = -2, 4

    def X(p):
        return x0 + (math.log10(p) - pe0) / (pe1 - pe0) * (x1 - x0)

    s += line(x0, y, x1 + 10, y, INK, 2.2)
    for p, t in [(0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"),
                 (100, "100"), (1000, "1000"), (10000, "10⁴")]:
        s += line(X(p), y - 6, X(p), y + 6, INK, 1.6)
        s += text(X(p), y + 22, t, 10.5, GREY, "middle")
    s += text(x1 + 26, y + 5, "Вт", 12, INK, "middle", "bold")

    items = [(0.06, "світлодіод", "0.06 Вт"), (0.5, "реле / резистор", "0.5 Вт"),
             (5, "USB-зарядка", "5 Вт"), (50, "ноутбук", "50 Вт"),
             (500, "пилосос", "500 Вт"), (2000, "чайник", "2 кВт")]
    for i, (p, name, val) in enumerate(items):
        xx = X(p)
        row = 150 if i % 2 == 0 else 104
        s += line(xx, y - 6, xx, row + 16, GREY, 1.4)
        s += circle(xx, y, 4, RED, RED, 1)
        s += rect(xx - 58, row - 16, 116, 32, "#f6f8fc", INK, 1.4, 8)
        s += text(xx, row - 1, name, 10.5, INK, "middle", "bold")
        s += text(xx, row + 12, val, 10, GREY, "middle")

    s += text(W / 2, H - 14,
              "Орієнтир: ват — це приблизно світлодіод-індикатор. Чайник — уже дві тисячі таких.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-5-5-watt-scale.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Історія до §3.5 — Джеймс Уатт і «кінська сила».  Рис. 3.5і.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.5і.1 — іскра Уатта: окремий конденсатор ───────────────────────────
def fig_newcomen_vs_watt():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 30, "Іскра Уатта: окремий холодильник — і втричі менше вугілля", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "Ньюкомен грів і холодив ОДИН циліндр щотакту; Уатт лишив циліндр завжди гарячим",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 74, W / 2, H - 58, FAINT, 1.4, "4,5")

    # ── ліворуч: Ньюкомен ──
    s += text(220, 96, "Машина Ньюкомена (1712)", 13.5, INK, "middle", "bold")
    s += rect(160, 340, 120, 26, "#f0d9c0", "#9c6b48", 2, 4)
    s += text(220, 357, "котел", 10.5, INK, "middle")
    s += heatwaves(220, 340, 3, ORANGE)
    s += rect(190, 150, 60, 170, "#fdeccd", INK, 2.2, 4)
    s += text(220, 140, "циліндр", 10.5, INK, "middle", "bold")
    s += line(192, 235, 248, 235, INK, 4)          # поршень
    s += line(220, 150, 220, 235, INK, 2.4)        # шток
    s += arrow(220, 338, 220, 300, ORANGE, 2.4)
    s += text(255, 300, "пара", 10, ORANGE, "start", "bold")
    s += _snow(150, 208, 8, BLUE, 2)
    s += arrow(160, 212, 190, 220, BLUE, 2.2)
    s += text(150, 232, "холодна вода", 9.5, BLUE, "middle", "bold")
    s += heatwaves(284, 250, 2, RED)
    s += _snow(290, 205, 7, BLUE, 2)
    s += text(220, 392, "Циліндр щотакту то гарячий, то холодний —", 11, GREY, "middle", style="italic")
    s += text(220, 408, "більшість вугілля йде на даремний підігрів.", 11, RED, "middle", "bold")

    # ── праворуч: Уатт ──
    s += text(645, 96, "Машина Уатта (1769)", 13.5, INK, "middle", "bold")
    s += rect(590, 340, 120, 26, "#f0d9c0", "#9c6b48", 2, 4)
    s += text(650, 357, "котел", 10.5, INK, "middle")
    s += heatwaves(650, 340, 3, ORANGE)
    s += rect(612, 150, 76, 170, "#f7c9a6", "#c0392b", 2.2, 4)   # парова сорочка (гаряча)
    s += rect(622, 158, 56, 154, "#fdeccd", INK, 1.8, 3)
    s += text(650, 140, "циліндр — завжди гарячий", 10, RED, "middle", "bold")
    s += line(624, 235, 676, 235, INK, 4)
    s += line(650, 158, 650, 235, INK, 2.4)
    s += arrow(650, 338, 650, 300, ORANGE, 2.2)
    s += rect(740, 248, 72, 60, "#dbe6f5", BLUE, 2, 6)
    s += text(776, 272, "холо-", 10, BLUE, "middle", "bold")
    s += text(776, 288, "дильник", 10, BLUE, "middle", "bold")
    s += line(688, 268, 740, 268, INK, 2.2)
    s += circle(714, 268, 5, "#fff", INK, 1.6)
    s += text(714, 254, "клапан", 8.5, GREY, "middle")
    s += _snow(776, 322, 8, BLUE, 2)
    s += text(645, 392, "Пара конденсується в окремому холодильнику,", 11, GREY, "middle", style="italic")
    s += text(645, 408, "циліндр не холоне → ≈3× менше вугілля.", 11, GREEN, "middle", "bold")
    save("fig-3-5i-1-newcomen-watt.svg", s)


def _horse(x, y, col="#8a5a3b"):
    """Схематичний кінь, мордою ліворуч; (x,y) — під передніми ногами."""
    o = rect(x - 4, y - 40, 52, 22, col, "none", 0, 9)            # тулуб
    o += line(x - 1, y - 34, x - 16, y - 56, col, 12)             # шия
    o += rect(x - 25, y - 63, 17, 12, col, "none", 0, 4)          # голова
    for lx in (2, 16, 32, 44):                                    # ноги
        o += line(x + lx, y - 20, x + lx, y, col, 4)
    o += line(x + 48, y - 34, x + 61, y - 25, col, 4)            # хвіст
    return o


# ── Рис. 3.5і.2 — звідки «кінська сила» ──────────────────────────────────────
def fig_horsepower():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 30, "Звідки «кінська сила»: Уатт зміряв коня", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "щоб продати машину, треба сказати — скількох коней вона замінить",
              12, GREY, "middle", style="italic")

    # земля
    s += line(60, 320, 470, 320, INK, 2)
    s += _horse(150, 320)
    s += text(165, 250, "кінь", 11, INK, "middle", "bold")
    s += arrow(150, 300, 105, 300, GREEN, 2.2)
    s += text(110, 288, "йде", 10, GREEN, "middle", "bold")
    # стовп із блоком
    s += line(430, 320, 430, 150, INK, 3)
    s += circle(430, 145, 10, "#fff", INK, 2.2)                  # блок
    # мотузка: від коня (ззаду) через блок до вантажу
    s += line(232, 292, 430, 152, "#b08646", 2.4)
    s += text(330, 210, "тягне", 10.5, "#8a5a3b", "middle", "bold", "italic")
    s += line(430, 138, 430, 250, "#b08646", 2.4)
    # вантаж
    s += rect(410, 250, 40, 40, "#d7d2c4", INK, 2, 4)
    s += text(430, 275, "вантаж", 9, INK, "middle", "bold")
    s += arrow(430, 296, 430, 330, BLUE, 2.2)
    s += text(456, 318, "F = вага", 10.5, BLUE, "start", "bold")

    # картка з формулою
    s += rect(508, 96, 322, 244, "#f6f8fc", INK, 1.6, 12)
    s += text(669, 128, "Потужність = сила × шлях ÷ час", 13.5, INK, "middle", "bold")
    s += text(669, 154, "P = F · d / t", 18, GREEN, "middle", "bold")
    s += line(528, 174, 810, 174, FAINT, 1.4)
    s += text(528, 198, "Уатт зміряв робочого коня й узяв", 12, INK, "start")
    s += text(528, 216, "за одиницю:", 12, INK, "start")
    s += text(669, 246, "1 к.с. = 33 000 фунт·фут / хв", 15, INK, "middle", "bold")
    s += text(669, 268, "(він округлив трохи вгору — щоб машина", 10.5, GREY, "middle", style="italic")
    s += text(669, 283, "радше перевершувала коня, ніж навпаки)", 10.5, GREY, "middle", style="italic")
    s += line(528, 298, 810, 298, FAINT, 1.4)
    s += text(669, 322, "У системі СІ:  1 к.с. ≈ 746 Вт", 14, RED, "middle", "bold")
    save("fig-3-5i-2-horsepower.svg", s)


# ── Рис. 3.5і.3 — відцентровий регулятор: зворотний зв'язок ───────────────────
def fig_watt_governor():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 30, "Регулятор Уатта: машина, що сама тримає оберти", 20, INK, "middle", "bold")
    s += text(W / 2, 52, "швидше → кулі розходяться → клапан прикриває пару → повільніше",
              12, GREY, "middle", style="italic")

    sx = 330                       # вісь шпинделя
    piv = (sx, 130)
    s += line(sx, 120, sx, 320, INK, 3)            # шпиндель
    s += circle(sx, 120, 5, INK, INK, 1)           # верхній шарнір
    # важелі з кулями (робоче положення)
    lb, rb = (250, 240), (410, 240)
    s += line(piv[0], piv[1] + 4, lb[0], lb[1], INK, 2.6)
    s += line(piv[0], piv[1] + 4, rb[0], rb[1], INK, 2.6)
    s += circle(lb[0], lb[1], 18, "#cdd6e6", INK, 2.2)
    s += circle(rb[0], rb[1], 18, "#cdd6e6", INK, 2.2)
    # розліт при розгоні (пунктир)
    s += line(piv[0], piv[1] + 4, 214, 214, GREY, 1.6, "4,3")
    s += line(piv[0], piv[1] + 4, 446, 214, GREY, 1.6, "4,3")
    s += arrow(238, 236, 210, 224, RED, 2)
    s += arrow(422, 236, 450, 224, RED, 2)
    s += text(330, 196, "кулі розходяться", 11, RED, "middle", "bold")
    # втулка
    s += rect(sx - 16, 246, 32, 14, "#f0c8a0", INK, 2, 3)
    s += line(lb[0] + 6, lb[1] - 6, sx - 16, 250, INK, 1.8)
    s += line(rb[0] - 6, rb[1] - 6, sx + 16, 250, INK, 1.8)
    s += arrow(sx + 40, 270, sx + 18, 252, INK, 1.8)
    s += text(sx + 46, 274, "втулка піднімається", 10.5, INK, "start", "bold")
    # важіль до клапана
    s += circle(560, 230, 4, INK, INK, 1)          # опора важеля
    s += line(sx + 16, 253, 620, 214, INK, 2.4)
    # паропровід із дроселем
    s += line(640, 150, 640, 330, "#9aa7b4", 6)    # труба
    s += line(620, 200, 660, 188, RED, 3)          # заслінка (прикрита)
    s += text(700, 188, "клапан пари", 11, RED, "start", "bold")
    s += text(700, 206, "(прикривається)", 9.5, GREY, "start", style="italic")
    s += arrow(640, 338, 640, 360, ORANGE, 2.2)
    s += text(640, 376, "пара від котла", 10, ORANGE, "middle", "bold")
    # привід знизу
    s += _circ_arrow(sx, 332, 16, GREEN, -40, 200, 2.4)
    s += text(sx, 366, "оберти від машини", 10, GREEN, "middle", "bold")

    # рамка зв'язку з §3.4
    s += rect(60, 92, 210, 120, "#eef7f0", GREEN, 1.6, 10)
    s += text(165, 114, "Зворотний зв'язок-", 12, GREEN, "middle", "bold")
    s += text(165, 130, "гальмо", 12, GREEN, "middle", "bold")
    s += text(165, 154, "Відхилення саме себе", 10.5, INK, "middle")
    s += text(165, 170, "гасить — як PTC у §3.4.", 10.5, INK, "middle")
    s += text(165, 194, "Прабатько автоматики.", 10, GREY, "middle", style="italic")
    save("fig-3-5i-3-governor.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §3.6 — Джоулеве тепло: чому й скільки гріється.  Рис. 3.6.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.6.1 — у чистому опорі вся потужність стає теплом ───────────────────
def fig36_all_to_heat():
    W, H = 860, 392
    s = header(W, H)
    s += text(W / 2, 32, "Джоулеве тепло: у чистому опорі ВСЯ потужність стає теплом", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "електрична енергія на опорі не «зникає» — вона цілком переходить у тепло",
              12, GREY, "middle", style="italic")
    s += rect(70, 110, 150, 60, "#eaf0fb", BLUE, 2, 10)
    s += text(145, 135, "електрична", 11, INK, "middle", "bold")
    s += text(145, 156, "P = I²R", 15, BLUE, "middle", "bold")
    s += arrow(222, 140, 300, 140, INK, 2.6)
    s += _resistor(305, 140, 90, 30, "R")
    s += heatwaves(350, 116, 4, RED)
    s += arrow(402, 140, 480, 140, RED, 2.6)
    s += rect(480, 110, 170, 60, "#fbecea", RED, 2, 10)
    s += text(565, 135, "тепло", 13, RED, "middle", "bold")
    s += text(565, 156, "усі 100 %", 14, RED, "middle", "bold")
    s += text(360, 196, "жодна частка не йде «кудись іще» — чистий опір тільки гріє", 11, GREY, "middle", style="italic")

    s += line(70, 224, W - 70, 224, FAINT, 1.4)
    s += text(W / 2, 248, "Для порівняння — де потужність ділиться між користю й теплом:", 12.5, INK, "middle", "bold")
    cols = [("резистор", "усе → тепло", RED, "(тепло — це і є робота)"),
            ("мотор", "частина → рух", GREEN, "+ тепло втрат"),
            ("світлодіод", "частина → світло", ORANGE, "+ тепло втрат")]
    for i, (name, what, col, note) in enumerate(cols):
        cx = 190 + i * 250
        s += rect(cx - 95, 268, 190, 88, "#f6f8fc", INK, 1.4, 10)
        s += text(cx, 294, name, 13, INK, "middle", "bold")
        s += text(cx, 318, what, 12, col, "middle", "bold")
        s += text(cx, 340, note, 10.5, GREY, "middle", style="italic")
    save("fig-3-6-1-all-to-heat.svg", s)


# ── Рис. 3.6.2 — тепло росте як квадрат струму ───────────────────────────────
def fig36_i_squared():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 32, "Небезпечний квадрат: вдвічі більший струм — вчетверо більше тепла", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "P = I²R: тепло росте як КВАДРАТ струму — тому надструми такі руйнівні",
              12, GREY, "middle", style="italic")
    ox, oy, topy = 110, 330, 92
    s += arrow(ox, oy, 730, oy, INK, 2)
    s += text(736, oy + 4, "струм I", 12, INK, "start")
    s += arrow(ox, oy, ox, topy, INK, 2)
    s += text(ox - 8, topy - 6, "тепло P", 12, INK, "end")
    unit = 24.0
    bw = 46
    for I, P, lab in [(1, 1, "×1"), (2, 4, "×4"), (3, 9, "×9")]:
        bx = ox + I * 150 - bw / 2
        h = P * unit
        s += rect(bx, oy - h, bw, h, "#f3b8b0" if P < 9 else "#e0695e", RED, 2, 4)
        s += text(bx + bw / 2, oy - h - 10, lab, 13, RED, "middle", "bold")
        s += text(bx + bw / 2, oy + 19, f"I = {I}", 11, GREY, "middle")
    cv = [(ox + (k / 10.0) * 150, oy - (k / 10.0) ** 2 * unit) for k in range(0, 31)]
    s += polyline(cv, INK, 2.2)
    s += text(ox + 3.05 * 150, oy - 9 * unit + 4, "P = I²R", 12, INK, "start", "bold", "italic")
    s += rect(110, 352, W - 220, 44, "#fff3e8", ORANGE, 1.6, 10)
    s += text(W / 2, 374, "Тому 10 А гріють у 100 разів дужче за 1 А.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 390, "Запобіжники, перерізи дротів і радіатори рахують саме на квадрат струму.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-6-2-i-squared.svg", s)


# ── Рис. 3.6.3 — усталена температура: вхід = вихід ──────────────────────────
def fig36_steady_state():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 32, "Чому температура зупиняється: тепло-вхід = тепло-вихід", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "тіло гріється, доки відведення тепла не зрівняється з виділенням I²R",
              12, GREY, "middle", style="italic")
    ox, oy, topy = 110, 330, 92
    s += arrow(ox, oy, 730, oy, INK, 2)
    s += text(736, oy + 4, "температура", 12, INK, "start")
    s += arrow(ox, oy, ox, topy, INK, 2)
    s += text(ox - 8, topy - 6, "потужність", 12, INK, "end")
    pin_y = oy - 150
    s += line(ox, pin_y, 700, pin_y, RED, 2.6)
    s += text(698, pin_y - 10, "виділення I²R (стале)", 11, RED, "end", "bold")
    # відведення без радіатора (пологе) і з радіатором (крутіше)
    s += line(ox, oy, 640, 100, BLUE, 2.6)
    s += text(556, 150, "відведення (саме повітря)", 11, BLUE, "middle", "bold")
    s += line(ox, oy, 430, 100, GREEN, 2.6)
    s += text(330, 150, "з радіатором", 11, GREEN, "middle", "bold")
    s += circle(456, pin_y, 5, RED, RED, 1)
    s += line(456, pin_y, 456, oy, GREY, 1.3, "3,3")
    s += text(456, oy + 19, "T₁ — гаряче", 10.5, INK, "middle", "bold")
    s += circle(319, pin_y, 5, GREEN, GREEN, 1)
    s += line(319, pin_y, 319, oy, GREY, 1.3, "3,3")
    s += text(319, oy + 19, "T₂ — прохолодніше", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 18, "Краще відведення (радіатор, обдув, площа) — та сама потужність дає НИЖЧУ температуру.",
              11, GREY, "middle", style="italic")
    save("fig-3-6-3-steady-state.svg", s)


# ── Рис. 3.6.4 — допустима потужність компонента ─────────────────────────────
def fig36_rating():
    W, H = 860, 384
    s = header(W, H)
    s += text(W / 2, 32, "Допустима потужність: межа, яку не можна переходити", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "той самий резистор на 0.25 Вт за трьох навантажень: норма, межа, згоряння",
              12, GREY, "middle", style="italic")
    cols = [("0.10 Вт", "безпечно (≈40 %)", GREEN, 2, "#ffffff"),
            ("0.25 Вт", "на самій межі (100 %)", ORANGE, 4, "#fde6d2"),
            ("0.50 Вт", "перегрів → дрейф, згоряння", RED, 7, "#f1b0a7")]
    for i, (val, note, col, waves, fill) in enumerate(cols):
        cx = 165 + i * 270
        s += heatwaves(cx, 150, waves, col)
        s += rect(cx - 60, 158, 120, 42, fill, col, 2.6, 6)
        s += text(cx, 184, "R · 0.25 Вт", 11.5, INK, "middle", "bold")
        s += text(cx, 232, val, 16, col, "middle", "bold")
        s += text(cx, 256, note, 11, INK, "middle")
    s += rect(80, 296, W - 160, 70, "#f6f8fc", INK, 1.6, 12)
    s += text(W / 2, 320, "Запас (derating): беруть номінал у 2–3 рази більший за розрахункову потужність.",
              12, INK, "middle", "bold")
    s += text(W / 2, 344, "Перевищиш межу — резистор перегрівається: спершу «попливе» опір, далі обвуглення й обрив. Деталі — у §3.7.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-6-4-rating.svg", s)


# ── Рис. 3.6.5 — тепло: друг чи ворог ────────────────────────────────────────
def fig36_friend_foe():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 32, "Те саме тепло: коли друг, а коли ворог", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "джоулеве тепло бажане в нагрівачі — і шкідливе в процесорі",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.4, "4,5")

    def col(x0, title, accent, rows):
        o = text(x0 + 150, 102, title, 14.5, accent, "middle", "bold")
        yy = 138
        for name, why in rows:
            o2 = heatwaves(x0 + 26, yy + 8, 2, accent)
            o2 += text(x0 + 52, yy, name, 12.5, INK, "start", "bold")
            o2 += text(x0 + 52, yy + 17, why, 10.3, GREY, "start", style="italic")
            o += o2
            yy += 56
        return o

    s += col(40, "Тепло — МЕТА", GREEN, [
        ("Чайник, нагрівач", "усю потужність — у тепло води/повітря"),
        ("Лампа розжарення", "нитка світить, бо розжарена струмом"),
        ("Запобіжник", "навмисно перегоряє від надструму (I²R·t)"),
        ("Паяльник", "розжарене жало плавить припій"),
    ])
    s += col(430, "Тепло — ВОРОГ", RED, [
        ("Процесор", "нагрів обмежує швидкість, треба радіатор"),
        ("Силовий дріт", "втрати I²R і пожежна небезпека"),
        ("Акумулятор", "нагрів старить і веде до теплової втечі (§3.4)"),
        ("Блок живлення", "тепло = змарнована енергія, нижчий ККД"),
    ])
    save("fig-3-6-5-friend-foe.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §3.7 — Резистор як компонент: номінал, потужність, добір.  Рис. 3.7.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.7.1 — стандартні ряди E ───────────────────────────────────────────
def fig37_eseries():
    W, H = 880, 330
    s = header(W, H)
    s += text(W / 2, 32, "Чому 220, а не 200: стандартні ряди E", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "номінали згущуються логарифмічно, щоб смужки допуску вкрили ВСЮ вісь без дір",
              12, GREY, "middle", style="italic")
    x0, x1, axy = 120, 800, 200

    def X(v):
        return x0 + (math.log10(v) - 1) * (x1 - x0)

    s += line(80, axy, 820, axy, INK, 2)
    e12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]
    for i, v in enumerate(e12):
        xa, xb = X(v * 0.9), X(v * 1.1)
        s += rect(xa, axy - 26, xb - xa, 52, "#eaf0fb" if i % 2 == 0 else "#fde9d6", "#cfcfcf", 0.6, 0)
        xv = X(v)
        s += line(xv, axy - 26, xv, axy + 26, INK, 1.4)
        s += text(xv, axy + 44 if i % 2 == 0 else axy + 60, str(v), 10.5, INK, "middle", "bold")
    for v in (10, 100):
        s += line(X(v), axy - 40, X(v), axy + 34, GREY, 1.4, "3,3")
    s += text(X(10), axy - 48, "10", 11, GREY, "middle", "bold")
    s += text(X(100), axy - 48, "100  (далі ×10)", 11, GREY, "middle", "bold")
    s += rect(80, 282, W - 160, 38, "#f6f8fc", INK, 1.4, 10)
    s += text(W / 2, 306, "E12 (±10 %) — 12 значень на декаду; E24 (±5 %) — 24, густіше. Звідси «дивні» 22, 47, 68…",
              11.5, INK, "middle", "bold")
    save("fig-3-7-1-eseries.svg", s)


# ── Рис. 3.7.2 — кольоровий код ──────────────────────────────────────────────
def fig37_colorcode():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 32, "Кольоровий код: читаємо номінал зі смужок", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "чотири смужки: дві цифри, множник, допуск", 12, GREY, "middle", style="italic")
    COL = {'black': '#1b1b1b', 'brown': '#6b4a2b', 'red': '#c0271e', 'orange': '#e08030',
           'yellow': '#f4c020', 'green': '#1f8a3b', 'blue': '#1f47b5', 'violet': '#7b3fa0',
           'grey': '#8a8a8a', 'white': '#ffffff', 'gold': '#c9a227'}
    bx, by, bw, bh = 310, 110, 260, 70
    s += line(230, by + bh / 2, bx, by + bh / 2, "#9c6b48", 4)
    s += line(bx + bw, by + bh / 2, 650, by + bh / 2, "#9c6b48", 4)
    s += rect(bx, by, bw, bh, "#e8d5a8", "#b89a5e", 2, 16)
    bands = [('red', '2'), ('red', '2'), ('brown', '×10'), ('gold', '±5%')]
    bxs = [bx + 44, bx + 84, bx + 124, bx + 208]
    for (c, lab), xb in zip(bands, bxs):
        s += rect(xb - 9, by + 4, 18, bh - 8, COL[c], "#7a7a7a", 0.6, 2)
        s += arrow(xb, by + bh + 6, xb, by + bh + 32, INK, 1.6)
        s += text(xb, by + bh + 48, lab, 12, INK, "middle", "bold")
    s += text(bx + bw / 2, by - 14, "приклад: червона · червона · коричнева · золота", 10.5, GREY, "middle", style="italic")
    s += rect(260, 232, 360, 52, "#eef7f0", GREEN, 2.2, 12)
    s += text(440, 264, "2 2 × 10 = 220 Ω, ±5 %", 20, GREEN, "middle", "bold")
    s += text(W / 2, 314, "Колір → цифра:", 12, INK, "middle", "bold")
    leg = [('black', 0), ('brown', 1), ('red', 2), ('orange', 3), ('yellow', 4),
           ('green', 5), ('blue', 6), ('violet', 7), ('grey', 8), ('white', 9)]
    cellw = 74
    startx = W / 2 - len(leg) * cellw / 2
    for i, (c, d) in enumerate(leg):
        cxx = startx + i * cellw + cellw / 2
        s += rect(cxx - 16, 328, 32, 22, COL[c], INK, 1.2, 3)
        s += text(cxx, 368, str(d), 12, INK, "middle", "bold")
    save("fig-3-7-2-colorcode.svg", s)


# ── Рис. 3.7.3 — розмір корпуса vs допустима потужність ──────────────────────
def fig37_sizes():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Більший корпус — більша допустима потужність", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "що більша поверхня, то більше тепла резистор віддасть, не перегрівшись",
              12, GREY, "middle", style="italic")
    data = [("1/8 Вт", 36, 14), ("1/4 Вт", 52, 18), ("1/2 Вт", 72, 22), ("1 Вт", 92, 28), ("2 Вт", 110, 34)]
    slots = [150, 320, 490, 655, 815]
    y = 165
    for (lab, w, h), sx in zip(data, slots):
        s += line(sx - w / 2 - 22, y, sx + w / 2 + 22, y, "#9c6b48", 3)
        s += rect(sx - w / 2, y - h / 2, w, h, "#e8d5a8", "#b89a5e", 2, h / 3)
        s += text(sx, y + h / 2 + 30, lab, 13, INK, "middle", "bold")
    s += text(W / 2, 290, "Орієнтовні розміри. Більше тепла → більший корпус (або радіатор, або менший струм).",
              11.5, GREY, "middle", style="italic")
    save("fig-3-7-3-sizes.svg", s)


# ── Рис. 3.7.4 — алгоритм добору ─────────────────────────────────────────────
def fig37_select_flow():
    W, H = 720, 520
    s = header(W, H)
    s += text(W / 2, 32, "Як дібрати резистор: п'ять кроків", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "спершу опір, потім потужність — і завжди із запасом", 12, GREY, "middle", style="italic")
    steps = [("1. Що треба", "відома напруга V і потрібний струм I", BLUE),
             ("2. Опір", "R = V / I   (закон Ома, §3.2)", INK),
             ("3. Номінал", "округлити до найближчого значення ряду E", INK),
             ("4. Потужність", "P = I²R   (скільки тепла, §3.6)", ORANGE),
             ("5. Запас і вибір", "допустима потужність у 2–3× більша (derating)", GREEN)]
    bw, bh = 460, 60
    x = (W - bw) / 2
    y = 90
    for i, (t, d, col) in enumerate(steps):
        s += rect(x, y, bw, bh, "#f6f8fc", col, 2.2, 12)
        s += text(x + 18, y + 26, t, 14, col, "start", "bold")
        s += text(x + 18, y + 47, d, 11.5, INK, "start")
        if i < len(steps) - 1:
            s += arrow(W / 2, y + bh, W / 2, y + bh + 18, INK, 2.2)
        y += bh + 30
    save("fig-3-7-4-select-flow.svg", s)


# ── Рис. 3.7.5 — приклад: резистор для світлодіода ───────────────────────────
def fig37_led_example():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "Приклад добору: резистор для світлодіода", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "живлення 5 В, світлодіод 2 В / 10 мА — який R і яка потужність?",
              12, GREY, "middle", style="italic")
    bx = 100
    s += line(bx, 120, bx, 240, INK, 2.4)
    s += line(bx - 15, 168, bx + 15, 168, INK, 3)
    s += line(bx - 8, 184, bx + 8, 184, INK, 5)
    s += text(bx - 22, 162, "5 В", 11.5, INK, "end", "bold")
    s += line(bx, 120, 200, 120, COPPER, 3)
    s += _resistor(200, 120, 70, 22, "R = ?")
    s += line(270, 120, 340, 120, COPPER, 3)
    s += f'<polygon points="340,108 340,132 366,120" fill="{INK}"/>\n'   # діод-трикутник
    s += line(366, 106, 366, 134, INK, 3)                                # катодна смужка
    s += arrow(352, 102, 360, 92, ORANGE, 1.6)
    s += arrow(361, 104, 369, 94, ORANGE, 1.6)
    s += text(353, 152, "LED 2 В", 10.5, INK, "middle", "bold")
    s += line(366, 120, 430, 120, COPPER, 3)
    s += line(430, 120, 430, 240, INK, 2.4)
    s += line(bx, 240, 430, 240, COPPER, 3)
    s += arrow(150, 120, 186, 120, RED, 2.2)
    s += text(168, 108, "I = 10 мА", 10.5, RED, "middle", "bold")

    px = 510
    s += rect(px - 20, 84, 380, 214, "#f6f8fc", INK, 1.6, 12)
    rows = [("Спад на R", "V_R = 5 − 2 = 3 В"),
            ("Опір", "R = V_R / I = 3 / 0.01 = 300 Ω"),
            ("Ряд E24", "300 Ω є точно (або 330 Ω з E12)"),
            ("Потужність", "P = I²R = 0.01² × 300 = 0.03 Вт"),
            ("Запас", "0.25 Вт ≫ 0.03 Вт — у ×8, надійно")]
    yy = 116
    for a, b in rows:
        s += text(px, yy, a + ":", 12.5, INK, "start", "bold")
        s += text(px + 104, yy, b, 12, GREY, "start")
        yy += 30
    s += rect(px + 50, 268, 270, 34, "#eef7f0", GREEN, 2.2, 10)
    s += text(px + 185, 291, "R = 300 Ω, 0.25 Вт", 16, GREEN, "middle", "bold")
    s += text(W / 2, 340, "Висновок: послідовний резистор 300 Ω на чверть вата — з величезним запасом.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-7-5-led-example.svg", s)


if __name__ == "__main__":
    # Історія
    fig_joule_paddle()
    fig_caloric_vs_energy()
    fig_ohm_joule_chain()
    # §3.1 Опір
    fig31_resistance_def()
    fig31_narrow_pipe()
    fig31_mechanism()
    fig31_resistor_component()
    # §3.2 Закон Ома
    fig32_three_forms()
    fig32_linearity()
    fig32_ohmic_nonohmic()
    fig32_led_resistor()
    # §3.3 R = ρL/A
    fig33_formula()
    fig33_length_area()
    fig33_awg()
    fig33_voltage_drop()
    # §3.4 Опір і температура
    fig34_rt_law()
    fig34_filament()
    fig34_runaway()
    fig34_selfreg()
    # Історія до §3.4 — надпровідність (Камерлінг-Оннес, 1911)
    fig_onnes_drop()
    fig_persistent_current()
    fig_super_apps()
    # §3.5 Потужність
    fig35_power_def()
    fig35_three_forms()
    fig35_worked()
    fig35_choose()
    fig35_watt_scale()
    # Історія до §3.5 — Джеймс Уатт
    fig_newcomen_vs_watt()
    fig_horsepower()
    fig_watt_governor()
    # §3.6 Джоулеве тепло
    fig36_all_to_heat()
    fig36_i_squared()
    fig36_steady_state()
    fig36_rating()
    fig36_friend_foe()
    # §3.7 Резистор як компонент
    fig37_eseries()
    fig37_colorcode()
    fig37_sizes()
    fig37_select_flow()
    fig37_led_example()
    print("OK — фігури розділу 3 (повна, +§3.7 резистор) згенеровано в", OUT)
