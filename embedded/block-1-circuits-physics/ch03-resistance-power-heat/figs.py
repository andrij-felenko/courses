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


# ═════════════════════════════════════════════════════════════════════════════
# Тема 1.3.8 — Запобіжники й самовідновні PTC
# ═════════════════════════════════════════════════════════════════════════════
HEAT = "#e0792a"
AMBR = "#caa24a"


def fig38_overcurrent():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Надструм — тиха пожежа: коротке замикання й тепло I²R", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "замкнеш накоротко — опір падає, струм злітає, а тепло росте як квадрат струму",
              11.5, GREY, "middle", style="italic")

    def panel(x, short):
        out = rect(x, 86, 360, 268, "none", FAINT, 1.6, 12)
        out += text(x + 180, 110, ("КОРОТКЕ ЗАМИКАННЯ" if short else "Норма"),
                    13.5, (RED if short else GREEN), "middle", "bold")
        bx, by = x + 50, 220
        out += text(bx, by - 34, "5 В", 12, INK, "middle", "bold")
        out += line(bx - 11, by - 22, bx + 11, by - 22, RED, 3)
        out += line(bx - 7, by - 8, bx + 7, by - 8, BLUE, 4)
        wy = by - 50
        out += line(bx, wy, x + 300, wy, INK, 3)
        out += line(x + 300, wy, x + 300, by + 6, INK, 3)
        out += line(bx, by + 6, x + 300, by + 6, INK, 3)
        out += line(bx, by - 22, bx, wy, INK, 3)
        out += line(bx, by - 8, bx, by + 6, INK, 3)
        if short:
            out += line(bx + 18, wy, x + 296, wy, HEAT, 5)
            out += text(x + 300 + 6, wy - 16, "перемичка", 10.5, RED, "middle", "bold")
            out += text(x + 180, by + 40, "I ≈ 10 А (велетенський)", 12, RED, "middle", "bold")
            out += text(x + 180, by + 60, "P = I²R → дріт розжарюється, плавиться", 11, RED, "middle", "bold")
        else:
            out += rect(x + 288, wy + 8, 24, 38, "#fff7e0", AMBR, 2, 4)
            out += text(x + 180, by + 40, "I = 0.5 А (за призначенням)", 12, GREEN, "middle", "bold")
            out += text(x + 180, by + 60, "тепло помірне, усе ціле", 11, GREEN, "middle")
        return out

    s += panel(40, False)
    s += panel(420, True)
    s += text(W / 2, 378, "Захист має відчути цей надструм і обірвати чи обмежити його, перш ніж щось загориться.",
              11.5, INK, "middle", "bold")
    save("fig-3-8-1-overcurrent.svg", s)


def fig38_fuse_anatomy():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Запобіжник: навмисно найслабша ланка, що перегорає першою", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "тонкий легкоплавкий дротик у корпусі: надструм його плавить — і коло рветься",
              11.5, GREY, "middle", style="italic")

    def fuse(x, y, blown):
        out = rect(x, y - 16, 24, 32, "#cfd3d8", "#888888", 2, 3)
        out += rect(x + 200, y - 16, 24, 32, "#cfd3d8", "#888888", 2, 3)
        out += rect(x + 24, y - 18, 176, 36, "none", "#9bbcd0", 2, 6)
        if blown:
            out += line(x + 24, y, x + 100, y, "#7a5a3a", 2.4)
            out += line(x + 148, y, x + 200, y, "#7a5a3a", 2.4)
            out += polyline([(x + 100, y), (x + 108, y - 9), (x + 116, y + 7), (x + 124, y)], HEAT, 2)
            out += text(x + 112, y - 18, "розрив", 10.5, RED, "middle", "bold")
        else:
            out += line(x + 24, y, x + 200, y, "#b06a2a", 2.8)
        return out

    s += text(200, 108, "ЦІЛИЙ (проводить)", 12.5, GREEN, "middle", "bold")
    s += fuse(88, 158, False)
    s += text(200, 196, "дротик-елемент тонкий і легкоплавкий", 10.5, GREY, "middle", style="italic")
    s += text(600, 108, "ПЕРЕГОРІВ (розрив)", 12.5, RED, "middle", "bold")
    s += fuse(488, 158, True)
    s += text(600, 196, "надструм розплавив його → коло розімкнене", 10.5, GREY, "middle", style="italic")
    s += rect(60, 244, W - 120, 76, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 268, "Запобіжник — найслабша, найгарячіша точка кола. За норми він холодний;", 11.5, INK, "middle", "bold")
    s += text(W / 2, 288, "за надструму його I²R-тепло (§1.3.6) плавить дротик — і коло рветься, перш ніж згорить щось дорожче.",
              11.5, INK, "middle")
    s += text(W / 2, 308, "Перегорів — міняють на новий тієї самої марки (одноразовий).", 10.5, GREY, "middle", style="italic")
    save("fig-3-8-2-fuse-anatomy.svg", s)


def fig38_time_current():
    W, H = 780, 420
    s = header(W, H)
    s += text(W / 2, 34, "Часострумова характеристика: що більший надструм, то швидше рве", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "невелике перевантаження тримається довго; велике коротке замикання — майже миттєво",
              11.5, GREY, "middle", style="italic")
    ox, oy, ax1, ayt = 110, 340, 720, 100
    s += arrow(ox, oy, ax1, oy, INK, 2)
    s += arrow(ox, oy, ox, ayt - 6, INK, 2)
    s += text(ax1, oy + 24, "струм (× номінал)", 12, INK, "middle", "bold")
    s += text(ox - 8, ayt - 10, "час до перегоряння", 11.5, INK, "start", "bold")
    pts = []
    for i in range(0, 101):
        xf = 1.0 + i / 100.0 * 8.0
        t = 1.0 / ((xf - 0.9) ** 2.2)
        px = ox + (xf - 1.0) / 8.0 * (ax1 - ox)
        py = oy - min(t, 6.0) / 6.0 * (oy - ayt)
        pts.append((px, py))
    s += polyline(pts, RED, 2.8)
    for xf, lab in ((1, "1×"), (2, "2×"), (5, "5×"), (8, "8×")):
        px = ox + (xf - 1) / 8.0 * (ax1 - ox)
        s += line(px, oy, px, oy + 5, INK, 1.5)
        s += text(px, oy + 22, lab, 11, GREY, "middle")
    s += text(ox + 60, ayt + 24, "номінал: тримає вічно", 10.5, GREEN, "start", "bold")
    s += text(ax1 - 30, oy - 48, "коротке: рве за мс", 10.5, RED, "end", "bold")
    s += rect(60, H - 42, W - 120, 28, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 23, "Тому запобіжник не «спрацьовує рівно на номіналі»: терпить короткі кидки, але рве сталий надструм.",
              11, INK, "middle", "bold")
    save("fig-3-8-3-time-current.svg", s)


def fig38_fast_slow():
    W, H = 780, 400
    s = header(W, H)
    s += text(W / 2, 34, "Швидкі (F) і повільні (T): і чому винен пусковий кидок", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "багато навантажень дають короткий кидок струму при ввімкненні — він безпечний",
              11.5, GREY, "middle", style="italic")
    ox, oy, ax1 = 90, 300, 700
    s += arrow(ox, oy, ax1, oy, INK, 2)
    s += arrow(ox, oy, ox, 150, INK, 2)
    s += text(ax1, oy + 22, "час", 12, INK, "middle", "bold")
    s += text(ox - 6, 144, "струм", 12, INK, "start", "bold")
    rated = oy - 70
    s += line(ox, rated, ax1, rated, GREY, 1.4, "5 4")
    s += text(ax1 - 4, rated - 6, "номінал", 10.5, GREY, "end")
    s += polyline([(ox + 10, oy), (ox + 30, oy - 150), (ox + 70, oy - 150),
                   (ox + 95, rated + 6), (ax1 - 10, rated + 6)], BLUE, 2.6)
    s += text(ox + 70, oy - 162, "пусковий кидок (коротко)", 10.5, BLUE, "middle", "bold")
    s += text(ax1 - 60, rated - 14, "робочий струм", 10.5, BLUE, "end")
    s += text(120, 116, "Швидкий (F): зреагував би на кидок → хибно перегорить", 11, RED, "start", "bold")
    s += text(120, 134, "Повільний (T): перечекає кидок, але рве СТАЛИЙ надструм", 11, GREEN, "start", "bold")
    s += rect(60, H - 42, W - 120, 28, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 23, "F — для чутливої електроніки без кидків; T (літера «Т») — для моторів, БЖ та інших із пусковим струмом.",
              11, INK, "middle", "bold")
    save("fig-3-8-4-fast-slow.svg", s)


def fig38_ptc_mechanism():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Самовідновний PTC: провідні ланцюжки в полімері, що рвуться від тепла", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "холодний — частинки торкаються (малий опір); нагрівся — полімер розбух, ланцюжки розірвалися",
              11, GREY, "middle", style="italic")

    def block(x, hot):
        out = rect(x, 100, 210, 120, ("#fbece9" if hot else "#eef5ef"), (RED if hot else GREEN), 2, 8)
        out += text(x + 105, 90, ("ГАРЯЧИЙ → високий опір" if hot else "Холодний → малий опір"),
                    11.5, (RED if hot else GREEN), "middle", "bold")
        for r in range(3):
            cyy = 128 + r * 28
            for c in range(5):
                cx = (x + 24 + c * 42 + (4 if r % 2 else -4)) if hot else (x + 26 + c * 38)
                if (not hot) and c < 4:
                    out += line(cx + 6, cyy, cx + 32, cyy, INK, 1.8)
                out += circle(cx, cyy, 6, "#555555", "#222222", 1.2)
        out += text(x + 105, 238, ("ланцюжки розірвані → струм майже спинено" if hot else "ланцюжки зімкнені → струм тече"),
                    9.5, (RED if hot else GREEN), "middle")
        return out

    s += block(60, False)
    s += block(320, True)
    s += arrow(276, 160, 314, 160, HEAT, 2.6)
    s += text(295, 150, "тепло", 9.5, HEAT, "middle", "bold")
    gx0, gy0, gx1, gyt = 580, 210, 770, 108
    s += arrow(gx0, gy0, gx1, gy0, INK, 2)
    s += arrow(gx0, gy0, gx0, gyt - 6, INK, 2)
    s += text(gx1, gy0 + 20, "темп.", 11, INK, "middle", "italic")
    s += text(gx0 - 6, gyt - 8, "опір R", 11, INK, "start", "bold")
    s += polyline([(gx0 + 5, gy0 - 10), (gx0 + 90, gy0 - 16), (gx0 + 115, gy0 - 28),
                   (gx0 + 126, gyt + 10), (gx1 - 5, gyt + 6)], RED, 2.6)
    s += text(gx0 + 120, gyt + 30, "стрибок R", 9.5, RED, "start", "bold")
    s += text((gx0 + gx1) / 2, gy0 + 40, "PTC: опір стрибає вгору при нагріві", 9.5, GREY, "middle", style="italic")
    save("fig-3-8-5-ptc-mechanism.svg", s)


def fig38_ptc_cycle():
    W, H = 780, 380
    s = header(W, H)
    s += text(W / 2, 34, "Цикл PTC: спрацював — тримає — зняли живлення — сам скинувся", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "на відміну від запобіжника, PTC не міняють: охолов — і знову проводить",
              11.5, GREY, "middle", style="italic")
    ox, oy, ax1 = 80, 250, 700
    s += arrow(ox, oy, ax1, oy, INK, 2)
    s += arrow(ox, oy, ox, 110, INK, 2)
    s += text(ax1, oy + 22, "час", 12, INK, "middle", "bold")
    s += text(ox - 6, 104, "струм", 12, INK, "start", "bold")
    s += polyline([(ox + 10, oy - 40), (ox + 130, oy - 40), (ox + 150, oy - 150), (ox + 175, oy - 150),
                   (ox + 200, oy - 18), (ox + 360, oy - 18), (ox + 380, oy), (ox + 470, oy),
                   (ox + 490, oy - 40), (ax1 - 10, oy - 40)], RED, 2.6)
    s += text(ox + 70, oy - 50, "норма", 10, GREEN, "middle", "bold")
    s += text(ox + 162, oy - 160, "коротке: кидок", 9.5, RED, "middle", "bold")
    s += text(ox + 280, oy - 26, "спрацював: лише цівка («тримає»)", 9.5, "#c98a00", "middle", "bold")
    s += text(ox + 425, oy - 28, "зняли живлення", 9.5, GREY, "middle")
    s += text(ax1 - 60, oy - 50, "охолов → знову проводить", 9.5, GREEN, "end", "bold")
    s += rect(60, H - 42, W - 120, 28, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 23, "Поки тримає, PTC сам себе гріє цівкою струму (засувка); знімеш напругу — він остигне й відновиться.",
              11, INK, "middle", "bold")
    save("fig-3-8-6-ptc-cycle.svg", s)


def fig38_fuse_vs_ptc():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 34, "Запобіжник чи PTC — що коли обрати", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "одноразова точність проти багаторазового самовідновлення", 11.5, GREY, "middle", style="italic")

    def colm(x, title, c, rows):
        out = rect(x, 86, 340, 232, "#fafafa", c, 1.8, 12)
        out += text(x + 170, 112, title, 14, c, "middle", "bold")
        yy = 146
        for r in rows:
            out += text(x + 18, yy, "•  " + r, 11.5, INK, "start")
            yy += 28
        return out

    s += colm(40, "Запобіжник (одноразовий)", RED, [
        "повністю РОЗМИКАЄ коло",
        "точний, велика відключна здатність",
        "перегорів → заміна вручну",
        "мережа, авто, потужні кола, великі КЗ"])
    s += colm(400, "Самовідновний PTC", GREEN, [
        "ОБМЕЖУЄ струм до цівки (не рве вщент)",
        "сам скидається, коли остигне",
        "повільніший, менш точний, менші струми",
        "USB, акумулятори, мотори, часті збої"])
    s += text(W / 2, 342, "А ще є автомат (circuit breaker) — багаторазовий механічний вимикач для щитків.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-8-7-fuse-vs-ptc.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Тема 1.3.9 — Тепловий опір і радіатор
# ═════════════════════════════════════════════════════════════════════════════

def fig39_heat_must_go():
    W, H = 800, 400
    s = header(W, H)
    s += text(W / 2, 34, "Куди подіти ват: тепло мусить кудись текти, інакше деталь згорить", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "спожита потужність стає теплом (§1.3.6); воно гріє кристал, аж поки той не гине (~150 °C)",
              11, GREY, "middle", style="italic")
    cx, cy = 230, 220
    s += rect(cx - 60, cy - 40, 120, 80, "#2b2b2b", INK, 2, 6)
    s += text(cx, cy + 5, "кристал", 13, "#ffffff", "middle", "bold")
    s += arrow(cx - 130, cy, cx - 62, cy, RED, 3)
    s += text(cx - 95, cy - 12, "P (ват)", 12, RED, "middle", "bold")
    for ddx in (-20, 0, 20):
        s += arrow(cx + ddx, cy - 42, cx + ddx, cy - 66, HEAT, 2)
    s += text(cx, cy - 76, "тепло", 11, HEAT, "middle", "bold")
    tx = 540
    s += rect(tx - 12, 120, 24, 190, "#ffffff", INK, 2, 12)
    s += circle(tx, 318, 20, "#ffffff", INK, 2)
    s += rect(tx - 6, 150, 12, 168, RED, "none", 0)
    s += circle(tx, 318, 14, RED, "none", 0)
    s += line(tx - 30, 140, tx - 12, 140, RED, 2)
    s += text(tx - 36, 144, "150 °C — кристал гине", 10.5, RED, "end", "bold")
    s += line(tx - 30, 280, tx - 12, 280, GREEN, 2)
    s += text(tx - 36, 284, "робоча зона", 10.5, GREEN, "end")
    s += text(tx, 112, "T росте", 11, RED, "middle", "bold")
    s += rect(60, H - 42, W - 120, 28, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 23, "Питання теми: наскільки нагріється деталь за даної потужності — і як це тепло відвести?",
              11, INK, "middle", "bold")
    save("fig-3-9-1-heat-must-go.svg", s)


def fig39_thermal_ohm():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Тепловий опір — як електричний: ΔT = P·Rθ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "перепад температур ↔ напруга; потік тепла (ват) ↔ струм; °C/Вт ↔ оми",
              11.5, GREY, "middle", style="italic")
    s += rect(50, 90, 340, 210, "#fafafa", GREY, 1.6, 12)
    s += text(220, 114, "Електричне", 13.5, BLUE, "middle", "bold")
    s += text(220, 152, "V = I · R", 19, INK, "middle", "bold")
    s += text(220, 184, "струм I тече крізь опір R,", 11.5, INK, "middle")
    s += text(220, 202, "на ньому падає напруга V", 11.5, INK, "middle")
    s += rect(170, 226, 100, 28, "none", INK, 2, 4)
    s += arrow(118, 240, 168, 240, BLUE, 2.4)
    s += text(140, 230, "I", 12, BLUE, "middle", "bold")
    s += text(220, 276, "V — різниця потенціалів", 10.5, GREY, "middle", style="italic")
    s += rect(430, 90, 340, 210, "#fbece9", RED, 1.6, 12)
    s += text(600, 114, "Теплове", 13.5, RED, "middle", "bold")
    s += text(600, 152, "ΔT = P · Rθ", 19, INK, "middle", "bold")
    s += text(600, 184, "тепло P тече крізь опір Rθ,", 11.5, INK, "middle")
    s += text(600, 202, "на ньому падає температура ΔT", 11.5, INK, "middle")
    s += rect(550, 226, 100, 28, "none", INK, 2, 4)
    s += arrow(498, 240, 548, 240, HEAT, 2.4)
    s += text(520, 230, "P", 12, HEAT, "middle", "bold")
    s += text(600, 276, "ΔT — різниця температур (°C)", 10.5, GREY, "middle", style="italic")
    s += text(410, 180, "↔", 22, INK, "middle", "bold")
    save("fig-3-9-2-thermal-ohm.svg", s)


def fig39_thermal_chain():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Тепловий шлях — це опори послідовно: від кристала до повітря", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "Rθ(j→a) = Rθ(j→корпус) + Rθ(корпус→радіатор) + Rθ(радіатор→повітря)",
              11.5, GREY, "middle", style="italic")
    y = 190
    s += line(80, y, 740, y, INK, 2)
    nodes = [(120, "кристал", "T_j (гарячий)", RED), (320, "корпус", "", INK),
             (520, "радіатор", "", INK), (720, "повітря", "T_a", GREEN)]
    for nx, lab, t2, col in nodes:
        s += circle(nx, y, 6, col, col, 1.5)
        s += text(nx, y - 16, lab, 11.5, col, "middle", "bold")
        if t2:
            s += text(nx, y - 32, t2, 10.5, col, "middle", "bold")
    res = [(220, "Rθ j-c", "корпус"), (420, "Rθ c-s", "паста/прокладка"), (620, "Rθ s-a", "→ повітря")]
    for rx, lab, sub in res:
        s += rect(rx - 30, y - 12, 60, 24, "#ffffff", INK, 2, 3)
        s += text(rx, y + 30, lab, 11, INK, "middle", "bold")
        s += text(rx, y + 46, sub, 9.5, GREY, "middle")
    s += arrow(80, y - 52, 740, y - 52, HEAT, 2.4)
    s += text(410, y - 62, "потік тепла P (ват) — однаковий уздовж шляху", 11, HEAT, "middle", "bold")
    s += rect(60, H - 58, W - 120, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 36, "T_j = T_a + P·Rθ(j→a). Опори додаються — тож кожна ланка (надто погана паста!) додає градусів.",
              11, INK, "middle", "bold")
    s += text(W / 2, H - 18, "Хочеш холодніший кристал — зменшуй сумарний Rθ: краща паста, більший радіатор, обдув.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-9-3-thermal-chain.svg", s)


def fig39_heatsink_rescue():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Радіатор рятує: той самий ват, а кристал — холодний", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "5 Вт, повітря 25 °C: без радіатора 125 °C (на межі), з радіатором — безпечно",
              11.5, GREY, "middle", style="italic")

    def panel(x, sink):
        out = rect(x, 90, 360, 270, "none", FAINT, 1.6, 12)
        out += text(x + 180, 114, ("З радіатором" if sink else "Без радіатора"),
                    13.5, (GREEN if sink else RED), "middle", "bold")
        cx, cy = x + 110, 210
        if sink:
            for i in range(7):
                out += line(cx - 42 + i * 14, cy - 26, cx - 42 + i * 14, cy - 70, "#8a949e", 3)
            out += line(cx - 44, cy - 26, cx + 44, cy - 26, "#8a949e", 4)
            out += text(cx, cy - 80, "ребра радіатора", 9.5, GREY, "middle")
        out += rect(cx - 40, cy - 26, 80, 52, "#2b2b2b", INK, 2, 5)
        out += text(cx, cy + 4, "5 Вт", 12, "#ffffff", "middle", "bold")
        if sink:
            out += text(x + 180, cy + 70, "Rθ ≈ 8 °C/Вт", 12.5, INK, "middle", "bold")
            out += text(x + 180, cy + 92, "T = 25 + 5×8 = 65 °C ✓", 13, GREEN, "middle", "bold")
        else:
            out += text(x + 180, cy + 70, "Rθ ≈ 20 °C/Вт", 12.5, INK, "middle", "bold")
            out += text(x + 180, cy + 92, "T = 25 + 5×20 = 125 °C ✗", 13, RED, "middle", "bold")
        return out

    s += panel(40, False)
    s += panel(420, True)
    s += text(W / 2, 384, "Радіатор не «холодить» магічно — він зменшує Rθ(радіатор→повітря), і той самий ват дає менший перепад.",
              11, INK, "middle", "bold")
    save("fig-3-9-4-heatsink-rescue.svg", s)


def fig39_tim():
    W, H = 800, 360
    s = header(W, H)
    s += text(W / 2, 34, "Термопаста: вигнати повітря зі стику (повітря — поганий провідник тепла)", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "мікрозазори між корпусом і радіатором повні повітря; паста їх заповнює й різко знижує Rθ",
              11, GREY, "middle", style="italic")

    def panel(x, paste):
        out = rect(x, 90, 340, 230, "none", FAINT, 1.6, 12)
        out += text(x + 170, 114, ("З пастою — добре" if paste else "Сухий стик — погано"),
                    13, (GREEN if paste else RED), "middle", "bold")
        out += rect(x + 40, 140, 260, 28, "#2b2b2b", INK, 1.6, 3)
        out += text(x + 170, 158, "корпус деталі", 10, "#ffffff", "middle")
        out += rect(x + 40, 210, 260, 28, "#8a949e", INK, 1.6, 3)
        out += text(x + 170, 228, "радіатор", 10, "#ffffff", "middle")
        if paste:
            out += rect(x + 40, 168, 260, 42, "#cdb89a", "#a07a3a", 1.2, 0)
            out += text(x + 170, 193, "паста заповнила зазори → тепло йде", 9.5, GREEN, "middle", "bold")
        else:
            out += rect(x + 40, 168, 260, 42, "#eef3f7", "#bbccdd", 1, 0)
            for i in range(6):
                out += polyline([(x + 50 + i * 42, 168), (x + 62 + i * 42, 189), (x + 74 + i * 42, 168)], "#99bbcc", 1.4)
            out += text(x + 170, 193, "повітряні кишені → тепло застрягає", 9.5, RED, "middle", "bold")
        return out

    s += panel(40, False)
    s += panel(420, True)
    s += text(W / 2, 344, "Паста не «проводить краще за метал» — вона лише виганяє повітря; тому її кладуть ТОНКО.",
              11, INK, "middle", "bold")
    save("fig-3-9-5-tim.svg", s)


def fig39_modes():
    W, H = 800, 360
    s = header(W, H)
    s += text(W / 2, 34, "Три шляхи тепла: теплопровідність, конвекція, випромінювання", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "до радіатора тепло йде провідністю; від ребер — конвекцією; трохи — випромінюванням",
              11, GREY, "middle", style="italic")
    cx, cy = 400, 240
    s += rect(cx - 180, cy, 360, 16, "#8a949e", INK, 2, 0)
    for i in range(11):
        s += line(cx - 170 + i * 34, cy, cx - 170 + i * 34, cy - 44, "#8a949e", 3)
    s += rect(cx - 30, cy + 16, 60, 24, "#2b2b2b", INK, 2, 3)
    s += text(cx, cy + 33, "деталь", 9.5, "#ffffff", "middle")
    s += arrow(cx, cy + 16, cx, cy + 2, HEAT, 2.4)
    s += text(cx + 72, cy + 28, "1. теплопровідність", 11, INK, "start", "bold")
    s += text(cx + 72, cy + 42, "(крізь метал у радіатор)", 9.5, GREY, "start")
    for xx in (cx - 120, cx - 50, cx + 40, cx + 120):
        s += arrow(xx, cy - 46, xx, cy - 78, GREEN, 2)
    s += text(cx, cy - 92, "2. конвекція (нагріте повітря тікає вгору)", 11, GREEN, "middle", "bold")
    s += text(cx - 250, cy - 26, "3. випромінювання", 10.5, "#a06a00", "start", "bold")
    s += text(cx - 250, cy - 12, "(ІЧ; мале за низьких T)", 9.5, GREY, "start")
    s += rect(60, H - 40, W - 120, 26, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 22, "Радіатор б'є саме по конвекції: ребра дають велику площу, а вентилятор підсилює відведення.",
              11, INK, "middle", "bold")
    save("fig-3-9-6-modes.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Компонентна вставка до теми 1.3.3 — Дроти
# ═════════════════════════════════════════════════════════════════════════════

def fig_wires():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Дроти як деталь: переріз, AWG, допустимий струм", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "товщина задає і опір (R=ρL/A, §1.3.3), і допустимий струм; багатожильний — гнучкіший",
              11, GREY, "middle", style="italic")
    # ── Панель A: суцільний vs багатожильний ──
    s += rect(40, 86, 360, 290, "none", FAINT, 1.6, 12)
    s += text(220, 110, "Суцільний vs багатожильний", 13, INK, "middle", "bold")
    s += circle(140, 188, 36, "#d9a066", "#a06a2a", 2)
    s += text(140, 240, "суцільний", 12, INK, "middle", "bold")
    s += text(140, 256, "тримає форму, дешевий", 9.5, GREY, "middle")
    s += text(140, 270, "ламається від частих згинів", 9.5, RED, "middle")
    bx, by = 300, 188
    s += circle(bx, by, 38, "none", "#a06a2a", 2)
    for a in range(0, 360, 60):
        s += circle(bx + 18 * math.cos(math.radians(a)), by + 18 * math.sin(math.radians(a)), 8, "#d9a066", "#a06a2a", 1.2)
    s += circle(bx, by, 8, "#d9a066", "#a06a2a", 1.2)
    s += text(bx, 240, "багатожильний", 12, INK, "middle", "bold")
    s += text(bx, 256, "гнучкий, стійкий до вібрації", 9.5, GREEN, "middle")
    s += text(220, 300, "Чому гнучкіший: тонка жилка гнеться легко (напруга згину ∝ товщині),", 9, INK, "middle")
    s += text(220, 314, "а жилки в пучку ще й ковзають одна повз одну.", 9, INK, "middle")
    s += text(220, 338, "(для гвинтових клем багатожильний обтискають у наконечник-ферулу)", 8.5, GREY, "middle", style="italic")
    # ── Панель B: AWG / струм ──
    s += rect(420, 86, 360, 290, "none", FAINT, 1.6, 12)
    s += text(600, 110, "Калібр (AWG) і застосування", 13, INK, "middle", "bold")
    s += text(600, 130, "менший номер AWG = товщий дріт = більший струм", 9.5, GREY, "middle", style="italic")
    rows = [("AWG 22", "0.33 мм²", "сигнали, дрібне живлення", 8),
            ("AWG 18", "0.82 мм²", "живлення приладів", 12),
            ("AWG 14", "2.1 мм²", "побутова розетка (~15 А)", 18),
            ("AWG 10", "5.3 мм²", "потужні лінії (~30 А)", 26)]
    yy = 158
    for name, area, use, d in rows:
        s += circle(472, yy, d / 2, "#d9a066", "#a06a2a", 1.4)
        s += text(500, yy - 4, name, 11.5, INK, "start", "bold")
        s += text(500, yy + 11, area + "  ·  " + use, 9.5, GREY, "start")
        yy += 46
    s += text(600, 348, "Допустимий струм залежить ще й від ізоляції, обдуву й пучкування;", 8.5, GREY, "middle", style="italic")
    s += text(600, 360, "тонший дріт — іще й більший опір і просадка напруги (R=ρL/A).", 8.5, GREY, "middle", style="italic")
    save("fig-3-3c-1-wires.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Історія до теми 1.3.4 — Полювання на нитку
# ═════════════════════════════════════════════════════════════════════════════

def fig_filament_timeline():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Полювання на нитку: не «один геній», а ланцюг рук у різних країнах", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "практичну лампу зробили колективно — і вугільну, і вольфрамову нитку шукали роками",
              11, GREY, "middle", style="italic")
    y = 156
    s += line(70, y, W - 70, y, INK, 2.4)
    s += text(70, y - 10, "1870", 10.5, GREY, "start")
    s += text(W - 70, y - 10, "1915", 10.5, GREY, "end")

    def X(yr):
        return 70 + (yr - 1870) / (1915 - 1870) * (W - 140)

    marks = [(1872, True, "1872", "Лодигін · Росія", "рання лампа (вугільні", "стрижні; ще не практична)", "#1f47b5"),
             (1880, False, "1879–80", "Едісон (США) + Свон (Брит.)", "практична ВУГІЛЬНА лампа", "(бамбук / целюлоза), паралельно", "#1f8a3b"),
             (1904, True, "1904", "Юст і Ганаман · Австро-Уг.", "перша ВОЛЬФРАМОВА нитка", "(але крихка)", "#7a52c0"),
             (1910, False, "1910", "Кулидж · GE, США", "ПЛАСТИЧНИЙ вольфрам →", "сучасна лампа", "#c98a00")]
    for yr, below, lab, who, l1, l2, col in marks:
        mx = X(yr)
        s += circle(mx, y, 6, col, col, 1.5)
        if below:
            s += text(mx, y + 22, lab, 11, col, "middle", "bold")
            s += text(mx, y + 40, who, 10.5, INK, "middle", "bold")
            s += text(mx, y + 55, l1, 9, GREY, "middle")
            s += text(mx, y + 68, l2, 9, GREY, "middle")
        else:
            s += text(mx, y - 56, lab, 11, col, "middle", "bold")
            s += text(mx, y - 40, who, 10.5, INK, "middle", "bold")
            s += text(mx, y - 25, l1, 9, GREY, "middle")
            s += text(mx, y - 12, l2, 9, GREY, "middle")
    s += rect(60, H - 46, W - 120, 32, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 26, "Едісонів геній — не сама нитка, а ціла СИСТЕМА під неї; вольфрам же став практичним аж у Кулиджа.",
              10.5, INK, "middle", "bold")
    save("fig-3-4i-1-filament-timeline.svg", s)


def fig_carbon_vs_tungsten():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому переміг вольфрам: найвища температура плавлення", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "нитка світить тим яскравіше, чим гарячіша; вольфрам терпить найбільший жар, не випаровуючись",
              11, GREY, "middle", style="italic")

    def colm(x, title, c, rows, t_lab):
        out = rect(x, 90, 340, 240, "#fafafa", c, 1.8, 12)
        out += text(x + 170, 114, title, 13.5, c, "middle", "bold")
        yy = 148
        for r in rows:
            out += text(x + 20, yy, "•  " + r, 10.5, INK, "start")
            yy += 26
        out += text(x + 170, 302, t_lab, 11.5, c, "middle", "bold")
        return out

    s += colm(40, "Вугільна нитка (рання)", "#7a5a3a", [
        "дешева, перша в історії",
        "випаровується → чорнить колбу",
        "коротке життя, тьмяне жовте світло",
        "не дає розжаритись надто сильно"], "робоча ~1800 °C")
    s += colm(420, "Вольфрамова нитка (сучасна)", "#1f8a3b", [
        "найвища серед металів т. плавлення",
        "терпить більший жар, повільно випаровується",
        "яскравіше, біліше світло, довше життя",
        "тонкий міцний дріт (після Кулиджа)"], "плавиться ~3422 °C")
    s += text(W / 2, 360, "Розжарена нитка — це опір під струмом (§1.3.6), що працює майже на межі плавлення.",
              10.5, INK, "middle", "bold")
    save("fig-3-4i-2-carbon-vs-tungsten.svg", s)


def fig_brittle_vs_ductile():
    W, H = 800, 360
    s = header(W, H)
    s += text(W / 2, 34, "Прорив Кулиджа: крихкий вольфрам став пластичним дротом", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "Юст і Ганаман дали вольфрам, та крихкий; Кулидж навчився тягти його в тонку гнучку нитку",
              11, GREY, "middle", style="italic")
    s += rect(40, 90, 360, 230, "#fbece9", RED, 1.6, 12)
    s += text(220, 114, "Крихкий (1904)", 13.5, RED, "middle", "bold")
    s += line(90, 182, 200, 182, "#888888", 5)
    s += polyline([(200, 182), (210, 168), (218, 196)], "#888888", 4)
    s += line(232, 182, 350, 182, "#888888", 5)
    s += text(220, 158, "ламається при згинанні", 10.5, RED, "middle", "bold")
    s += text(220, 252, "крихкий вольфрам не витягнеш", 10, INK, "middle")
    s += text(220, 268, "у тонку нитку — лампа недовговічна", 10, INK, "middle")
    s += rect(420, 90, 360, 230, "#eef5ef", GREEN, 1.6, 12)
    s += text(600, 114, "Пластичний (Кулидж, 1910)", 13, GREEN, "middle", "bold")
    s += line(460, 182, 560, 182, "#888888", 8)
    s += rect(560, 168, 20, 28, "#cfe0ef", "#5b87a6", 2, 3)
    s += text(575, 158, "алмазна фільєра", 9, "#3a6b86", "middle", "bold")
    s += line(580, 182, 736, 182, "#888888", 2)
    s += arrow(700, 182, 740, 182, INK, 2)
    s += text(660, 204, "тягнуть у тонесенький дріт", 10.5, GREEN, "middle", "bold")
    s += text(600, 252, "гнучкий вольфрам → тонка спіраль,", 10, INK, "middle")
    s += text(600, 268, "яскрава й довговічна лампа", 10, INK, "middle")
    s += text(W / 2, 344, "Саме ця «пластична» технологія (тягнути крізь алмаз) і зробила вольфрамову лампу масовою.",
              10.5, INK, "middle", "bold")
    save("fig-3-4i-3-brittle-vs-ductile.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Компонентна вставка до теми 1.3.4 — NTC проти кидка струму
# ═════════════════════════════════════════════════════════════════════════════

def fig_ntc_inrush():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "NTC проти кидка струму: холодний опір гасить старт", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "термістор NTC холодним має великий опір (на відміну від металів §1.3.4) — і вгамовує пусковий кидок",
              10.5, GREY, "middle", style="italic")
    # ── Панель A: R(T) NTC ──
    s += rect(40, 86, 360, 290, "none", FAINT, 1.6, 12)
    s += text(220, 110, "Опір NTC падає з нагрівом", 13, INK, "middle", "bold")
    ox, oy, ax1, ayt = 90, 330, 372, 140
    s += arrow(ox, oy, ax1, oy, INK, 1.8)
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8)
    s += text(ax1, oy + 20, "темп.", 11, INK, "middle", "italic")
    s += text(ox - 6, ayt - 8, "опір R", 11, INK, "start", "bold")
    pts = []
    for i in range(0, 61):
        xf = i / 60.0
        r = math.exp(-3.2 * xf)
        pts.append((ox + xf * (ax1 - ox), oy - r * (oy - ayt)))
    s += polyline(pts, "#1f47b5", 2.8)
    s += text(ox + 30, ayt + 22, "холодний:", 10, "#1f47b5", "start", "bold")
    s += text(ox + 30, ayt + 36, "великий R", 10, "#1f47b5", "start", "bold")
    s += text(ax1 - 14, oy - 22, "гарячий: малий R", 10, "#1f47b5", "end", "bold")
    s += text(220, 356, "(метал і PTC — навпаки: R росте з T, §1.3.4)", 9.5, GREY, "middle", style="italic")
    # ── Панель B: кидок струму ──
    s += rect(420, 86, 360, 290, "none", FAINT, 1.6, 12)
    s += text(600, 110, "Кидок струму при ввімкненні", 13, INK, "middle", "bold")
    bx, by, bx1, byt = 470, 330, 752, 140
    s += arrow(bx, by, bx1, by, INK, 1.8)
    s += arrow(bx, by, bx, byt - 6, INK, 1.8)
    s += text(bx1, by + 20, "час", 11, INK, "middle", "italic")
    s += text(bx - 6, byt - 8, "струм", 11, INK, "start", "bold")
    s += polyline([(bx + 8, by), (bx + 14, byt + 4), (bx + 42, by - 30), (bx1 - 10, by - 30)], RED, 2.6)
    s += text(bx + 56, byt + 22, "без NTC: велетенський кидок", 9.5, RED, "start", "bold")
    s += polyline([(bx + 8, by), (bx + 22, by - 60), (bx + 64, by - 34), (bx1 - 10, by - 30)], GREEN, 2.6)
    s += text(bx1 - 10, by - 46, "з NTC: кидок приборкано", 9.5, GREEN, "end", "bold")
    s += text(600, 356, "Нагрівшись, NTC втрачає опір і майже не заважає роботі.", 9.5, INK, "middle", "bold")
    save("fig-3-4c-1-ntc-inrush.svg", s)


# ── Рис. 3.7m.1 — геометричні сходи рядів E ──────────────────────────────────
def fig_eseries_ladder():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чому номінали ростуть геометрично: ряди E", 19, INK, "middle", "bold")
    s += text(W / 2, 51, "на логарифмічній осі рівні відношення = рівні проміжки; тісніший допуск — більше значень",
              11, GREY, "middle", style="italic")
    xl, xr = 110, 800

    def px(v):
        return xl + (math.log10(v) - 1) * (xr - xl)

    E6 = [10, 15, 22, 33, 47, 68, 100]
    E12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82, 100]
    E24 = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39,
           43, 47, 51, 56, 62, 68, 75, 82, 91, 100]
    for name, series, y, lab in [("E6 (±20%)", E6, 120, True),
                                 ("E12 (±10%)", E12, 200, True),
                                 ("E24 (±5%)", E24, 280, False)]:
        s += line(xl, y, xr, y, "#bbbbbb", 1.6)
        s += text(xl - 14, y + 4, name, 11, INK, "end", "bold")
        for v in series:
            x = px(v)
            h = 16 if lab else 10
            s += line(x, y, x, y - h, GREEN, 2)
            if lab:
                s += text(x, y - 22, str(v), 9.5, INK, "middle", "bold")
    s += text(px(10), 318, "10", 11, GREY, "middle", "bold")
    s += text(px(100), 318, "100", 11, GREY, "middle", "bold")
    s += text(W / 2, 318, "одна декада (×10)", 10.5, GREY, "middle", style="italic")
    s += rect(120, 336, W - 240, 30, "#f4f7f4", GREEN, 1.4, 10)
    s += text(W / 2, 356, "Крок = ×10^(1/n):   E6 ×1.47   ·   E12 ×1.21   ·   E24 ×1.10   ·   E96 ×1.024",
              12, INK, "middle", "bold")
    save("fig-3-7m-1-eseries-ladder.svg", s)


# ── Рис. 3.7m.2 — крок підігнано під допуск (смуги стуляються) ────────────────
def fig_eseries_tiling():
    W, H = 820, 350
    s = header(W, H)
    s += text(W / 2, 30, "Крок підігнано під допуск: сусідні смуги стуляються", 18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "смуга ±допуск кожного номіналу накриває ділянку осі; разом вони покривають усе",
              11, GREY, "middle", style="italic")
    xl, xr = 80, 780
    vlo, vhi = 9.0, 20.0

    def px(v):
        return xl + (v - vlo) / (vhi - vlo) * (xr - xl)

    def band_row(y, vals, tol, color, fill, label):
        out = text(xl - 8, y + 4, label, 11, INK, "end", "bold")
        for v in vals:
            x0, x1 = px(v * (1 - tol)), px(v * (1 + tol))
            out += rect(x0, y - 18, x1 - x0, 36, fill, color, 1.4, 4)
            out += line(px(v), y - 18, px(v), y + 18, color, 1.8)
            out += text(px(v), y - 26, str(v), 10, INK, "middle", "bold")
        return out

    s += band_row(135, [10, 12, 15, 18], 0.10, "#1f8a3b", "#e7f3ea", "E12  ±10%")
    s += band_row(245, [10, 11, 12, 13, 15, 16, 18], 0.05, "#1f47b5", "#e9eefb", "E24  ±5%")
    s += rect(70, H - 56, W - 140, 42, "#fff8ee", "#c9a227", 1.5, 10)
    s += text(W / 2, H - 38, "Відношення сусідів 10^(1/n) ≈ (1+допуск)/(1−допуск): для ±10% це 1.22 ≈ E12, для ±5% — 1.10 ≈ E24.",
              11, INK, "middle", "bold")
    s += text(W / 2, H - 20, "Тісніший допуск → вужчі смуги → потрібно більше значень, щоб накрити вісь без діри.",
              10.5, GREY, "middle", style="italic")
    save("fig-3-7m-2-eseries-tiling.svg", s)


# ── Рис. 3.9m.1 — теплова RC-модель і крива нагріву ──────────────────────────
def fig_thermal_rc():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Теплова RC-модель: нагрів як заряджання конденсатора", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "тепловий потік ~ струм, температура ~ напруга, Rθ ~ опір, теплова маса Cθ ~ ємність",
              10.5, GREY, "middle", style="italic")
    s += line(430, 72, 430, H - 20, FAINT, 1.5)
    s += rect(150, 150, 150, 70, "#fbe3df", "#c0271e", 2, 8)
    s += text(225, 182, "деталь", 12, INK, "middle", "bold")
    s += text(225, 203, "T (температура)", 10, GREY, "middle")
    s += arrow(70, 185, 148, 185, RED, 2.6)
    s += text(96, 172, "P", 13, RED, "middle", "bold")
    s += text(104, 205, "тепло", 9.5, GREY, "middle")
    s += arrow(300, 168, 388, 138, ORANGE, 2.4)
    s += text(360, 126, "Rθ → повітря", 10, "#a06a00", "middle", "bold")
    s += rect(175, 250, 100, 42, "#eef2fb", "#1f47b5", 2, 6)
    s += text(225, 270, "Cθ = m·c", 11, "#1f47b5", "middle", "bold")
    s += text(225, 285, "теплова маса", 8.5, GREY, "middle")
    s += arrow(225, 220, 225, 248, "#1f47b5", 2)
    s += text(225, 320, "маса вбирає тепло — T не стрибає вмить", 9.5, INK, "middle", "bold")
    ox, oy, axr, ayt = 480, 300, 820, 110
    s += arrow(ox, oy, axr, oy, INK, 1.8)
    s += text(axr, oy + 20, "час t", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8)
    s += text(ox - 6, ayt - 10, "T", 12, INK, "start", "bold")
    Tss = 140
    s += line(ox, Tss, axr - 10, Tss, "#bbbbbb", 1.5, "5 4")
    s += text(axr - 12, Tss - 8, "T_пов + P·Rθ", 9.5, GREY, "end", "bold")
    span = axr - 30 - ox
    tau = 70.0
    pts = [(ox + i / 100.0 * span, oy - (oy - Tss) * (1 - math.exp(-(i / 100.0 * span) / tau))) for i in range(101)]
    s += polyline(pts, GREEN, 2.8)
    s += line(ox + tau, oy, ox + tau, oy - (oy - Tss) * 0.63, "#1f47b5", 1.4, "3 3")
    s += text(ox + tau, oy + 16, "τ", 12, "#1f47b5", "middle", "bold")
    s += text(ox + tau + 6, oy - (oy - Tss) * 0.63 - 6, "63% за τ = Rθ·Cθ", 9, "#1f47b5", "start", "bold")
    s += text(ox + span * 0.62, Tss + 24, "≈5τ — практично усталена", 9.5, GREEN, "middle", "bold")
    save("fig-3-9m-1-thermal-rc.svg", s)


# ── Рис. 3.9m.2 — короткий імпульс проти тривалої потужності ──────────────────
def fig_pulse_vs_steady():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чому короткий імпульс не страшний", 18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "за t « τ теплова маса не встигає нагрітися: важить ЕНЕРГІЯ P·t, а не потужність",
              10.5, GREY, "middle", style="italic")
    ox, oy, axr, ayt = 90, 300, 820, 110
    s += arrow(ox, oy, axr, oy, INK, 1.8)
    s += text(axr, oy + 20, "час t", 11, INK, "middle", "italic")
    s += arrow(ox, oy, ox, ayt - 6, INK, 1.8)
    s += text(ox - 6, ayt - 10, "T", 12, INK, "start", "bold")
    Tss = 140
    s += line(ox, Tss, axr - 10, Tss, "#bbbbbb", 1.4, "5 4")
    s += text(axr - 12, Tss - 8, "ΔT = P·Rθ (повна, усталена)", 9.5, GREY, "end", "bold")
    span = axr - 30 - ox
    tau = 80.0
    sus = [(ox + i / 100.0 * span, oy - (oy - Tss) * (1 - math.exp(-(i / 100.0 * span) / tau))) for i in range(101)]
    s += polyline(sus, GREEN, 2.6)
    s += text(ox + span * 0.6, Tss + 22, "тривала P → повний нагрів", 10, GREEN, "middle", "bold")
    pw = 0.18 * tau
    pulse = [(ox, oy)]
    for i in range(1, 101):
        tt = i / 100.0 * span
        if tt < pw:
            T = oy - (oy - Tss) * (1 - math.exp(-tt / tau))
        else:
            T = oy - (oy - Tss) * (1 - math.exp(-pw / tau)) * math.exp(-(tt - pw) / (tau * 1.4))
        pulse.append((ox + tt, T))
    s += polyline(pulse, "#1f47b5", 2.6)
    s += line(ox + pw, oy, ox + pw, oy - 7, "#1f47b5", 1.5)
    s += text(ox + 150, oy - 24, "короткий імпульс t « τ →", 9.5, "#1f47b5", "start", "bold")
    s += text(ox + 150, oy - 11, "ΔT ≈ P·t / Cθ (ледь тепло)", 9.5, "#1f47b5", "start", "bold")
    s += rect(90, H - 44, W - 180, 32, "#f4f7f4", GREEN, 1.5, 10)
    s += text(W / 2, H - 23, "Тому деталь терпить кидок у рази понад норму на мить: це I²t запобіжника (§1.3.8) і пусковий кидок (§1.3.4).",
              10.5, INK, "middle", "bold")
    save("fig-3-9m-2-pulse-vs-steady.svg", s)


# ── Рис. 3.9c.1 — тепловий шлях як стос Rθ-деталей ───────────────────────────
def fig_thermal_stack():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 30, "Тепловий шлях як стос деталей: від кристала до повітря", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "кожна ланка має свій тепловий опір Rθ; вони стоять послідовно (§1.3.9), і кожну «купуєш» окремо",
              10.5, GREY, "middle", style="italic")
    cx = 300
    w = 300
    x = cx - w / 2
    for label, y, h, fill, col in [
        ("Кристал (junction)", 72, 44, "#fbe3df", "#c0271e"),
        ("Корпус деталі (case)", 140, 40, "#eef2fb", "#1f47b5"),
        ("Термоінтерфейс — паста чи прокладка", 200, 26, "#fff3e0", ORANGE),
        ("Радіатор (heat sink)", 252, 60, "#eef5ef", GREEN),
        ("Повітря (ambient)", 340, 40, "#eaf3f7", "#5b87a6"),
    ]:
        s += rect(x, y, w, h, fill, col, 2, 6)
        s += text(cx, y + h / 2 + 5, label, 11.5 if h > 30 else 10, INK, "middle", "bold")
    rx = cx + w / 2 + 20
    for yy, sym, what, src in [
        (128, "Rθ jc", "кристал→корпус", "з даташита деталі"),
        (213, "Rθ cs", "корпус→радіатор", "визначає термоінтерфейс"),
        (326, "Rθ sa", "радіатор→повітря", "з даташита радіатора; ↓ з обдувом"),
    ]:
        s += text(rx, yy + 2, sym, 12, "#c0271e", "start", "bold")
        s += text(rx + 56, yy - 2, what, 10, INK, "start", "bold")
        s += text(rx + 56, yy + 11, src, 9, GREY, "start", style="italic")
    s += arrow(x - 26, 80, x - 26, 372, "#c0271e", 3)
    s += text(x - 40, 226, "тепло", 10.5, "#c0271e", "middle", "bold")
    s += rect(120, H - 44, W - 240, 32, "#f4f7f4", GREEN, 1.5, 10)
    s += text(W / 2, H - 23, "Rθ(заг.) = Rθjc + Rθcs + Rθsa (послідовно);  перегрів ΔT = P · Rθ(заг.)  (§1.3.9).",
              11.5, INK, "middle", "bold")
    save("fig-3-9c-1-thermal-stack.svg", s)


# ── Рис. 3.9c.2 — електрична ізоляція кріплення (TO-220) ──────────────────────
def fig_isolation_mount():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 30, "Електрична ізоляція: підступ корпуса TO-220", 18, INK, "middle", "bold")
    s += text(W / 2, 51, "металева пластина деталі часто з'єднана з виводом (колектор/сток), а радіатор спільний — тож потрібна ізоляція",
              10, GREY, "middle", style="italic")
    cx = 470
    s += rect(cx - 150, 300, 300, 50, "#eef5ef", GREEN, 2, 6)
    s += text(cx, 330, "радіатор (часто заземлений / спільний)", 11, INK, "middle", "bold")
    s += rect(cx - 130, 282, 260, 16, "#fff3e0", ORANGE, 2, 3)
    s += text(cx, 294, "ізолювальна прокладка (слюда/кераміка/силікон) + паста", 8.5, INK, "middle", "bold")
    s += rect(cx - 90, 250, 180, 32, "#cdd5da", INK, 2, 4)
    s += text(cx, 270, "пластина деталі (TO-220)", 10, INK, "middle", "bold")
    s += rect(cx - 70, 200, 140, 50, "#2a2a2a", "#101010", 2, 6)
    s += text(cx, 230, "корпус деталі", 11, "#f0f0f0", "middle", "bold")
    s += rect(cx - 8, 150, 16, 150, "#9a9a9a", INK, 1.6, 2)
    s += rect(cx - 14, 250, 28, 50, "#fff3e0", ORANGE, 1.6, 2)
    s += text(cx, 142, "гвинт", 10, INK, "middle", "bold")
    s += text(cx + 150, 252, "ізолювальна втулка", 9.5, "#a06a00", "start", "bold")
    s += text(cx + 150, 266, "довкола гвинта", 9, GREY, "start")
    s += rect(70, 150, 150, 96, "#fafafa", GREY, 1.4, 8)
    s += text(145, 176, "крізь прокладку:", 11, INK, "middle", "bold")
    s += text(145, 204, "тепло ✓", 14, GREEN, "middle", "bold")
    s += text(145, 230, "струм ✗", 14, "#c0271e", "middle", "bold")
    s += rect(110, H - 40, W - 220, 28, "#fff8ee", ORANGE, 1.4, 10)
    s += text(W / 2, H - 21, "Прокладка пропускає тепло, але не струм; втулка ізолює гвинт. Забудеш — радіатор замкне вивід.",
              11, INK, "middle", "bold")
    save("fig-3-9c-2-isolation-mount.svg", s)


# ── Рис. 3.8і.1 — таймлайн народження запобіжника ────────────────────────────
def fig_fuse_timeline():
    W, H = 940, 300
    s = header(W, H)
    s += text(W / 2, 32, "Народження запобіжника: від телеграфу до Едісона й далі", 19, INK, "middle", "bold")
    s += text(W / 2, 53, "ідея «найслабшої ланки» визрівала десятиліттями й у різних руках",
              11, GREY, "middle", style="italic")
    y = 150
    s += line(60, y, 900, y, "#bbbbbb", 2.5)
    for x, yr, l1, l2, col in [
        (95, "1864", "телеграф: запобіжний", "дротик від блискавки (Бреге)", "#1f47b5"),
        (300, "1882", "система Едісона (Pearl St):", "запобіжники в складі", "#1f8a3b"),
        (490, "1890", "патент Едісона на", "запобіжний блок (US 438 305)", "#1f8a3b"),
        (670, "~1900", "гвинтовий «пробковий»", "запобіжник (цоколь Едісона)", INK),
        (855, "1940", "NEC забороняє цоколь", "Едісона → Type S", "#c0271e"),
    ]:
        s += circle(x, y, 7, col, col, 2)
        s += line(x, y - 7, x, y - 32, "#cccccc", 1.4)
        s += text(x, y - 38, yr, 13, col, "middle", "bold")
        s += text(x, y + 28, l1, 9.5, INK, "middle", "bold")
        s += text(x, y + 42, l2, 9, GREY, "middle")
    save("fig-3-8i-1-fuse-timeline.svg", s)


# ── Рис. 3.8і.2 — ідея найслабшої ланки ──────────────────────────────────────
def fig_fuse_weak_link():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 32, "Ідея: навмисно найслабша ланка, що гине першою", 18.5, INK, "middle", "bold")
    s += text(W / 2, 53, "тонкий запобіжний дротик розплавиться раніше, ніж постраждає цінне — апаратура чи проводка",
              10.5, GREY, "middle", style="italic")
    y = 200
    s += rect(70, y - 30, 90, 60, "#eef2fb", "#1f47b5", 2, 8)
    s += text(115, y - 2, "джерело", 11, INK, "middle", "bold")
    s += text(115, y + 16, "/ лінія", 10, GREY, "middle")
    s += line(160, y, 300, y, INK, 3)
    s += rect(300, y - 14, 150, 28, "#fff", "#8a8a8a", 1.6, 5)
    s += polyline([(308, y), (330, y - 6), (352, y + 6), (374, y - 6), (396, y + 6), (442, y)], "#c0271e", 1.6)
    s += text(375, y - 26, "тонкий запобіжний дротик", 9.5, "#c0271e", "middle", "bold")
    s += text(375, y + 30, "(найслабша ланка)", 9.5, GREY, "middle", style="italic")
    s += line(450, y, 600, y, INK, 3)
    s += rect(600, y - 34, 160, 68, "#eef5ef", GREEN, 2, 8)
    s += text(680, y - 8, "цінне:", 11, INK, "middle", "bold")
    s += text(680, y + 10, "апаратура,", 10, GREY, "middle")
    s += text(680, y + 26, "проводка, дім", 10, GREY, "middle")
    s += text(375, y - 70, "надструм / блискавка / коротке", 11, "#c0271e", "middle", "bold")
    s += arrow(375, y - 58, 375, y - 30, RED, 2.4)
    s += rect(110, y + 70, W - 220, 58, "#fff8ee", ORANGE, 1.5, 10)
    s += text(W / 2, y + 92, "Дротик плавиться й РОЗМИКАЄ коло — перш ніж жар устигне зіпсувати решту.", 11.5, INK, "middle", "bold")
    s += text(W / 2, y + 112, "Так у телеграфі рятували апаратуру від блискавки, а в освітленні — будинок від пожежі.",
              10, GREY, "middle", style="italic")
    save("fig-3-8i-2-weak-link.svg", s)


# ── Рис. 3.8і.3 — монетка за запобіжником і відповідь Type S ──────────────────
def fig_fuse_penny_tamper():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як людська кмітливість перемагала захист — і відповідь Type S", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "цоколь Едісона брав запобіжник будь-якого номіналу — тож «вічно перегорає» лікували монеткою",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 72, W / 2, H - 26, FAINT, 1.5)
    # ЛІВОРУЧ: монетка → пожежа
    s += text(225, 96, "Стара халепа: «монетка за запобіжником»", 12, "#c0271e", "middle", "bold")
    s += circle(225, 168, 40, "#f0e2c0", "#a98a00", 2.5)
    s += circle(225, 168, 27, "#d9b24a", "#a98a00", 1.8)
    s += text(225, 173, "1¢", 14, "#7a5e12", "middle", "bold")
    s += text(225, 228, "мідна монета замикає коло", 10, INK, "middle", "bold")
    s += text(225, 244, "замість перегорілого запобіжника", 9.5, GREY, "middle", style="italic")
    s += text(225, 286, "→ захисту НЕМА", 12, "#c0271e", "middle", "bold")
    s += text(225, 312, "перевантаження → пожежа", 11, "#c0271e", "middle", "bold")
    # ПРАВОРУЧ: Type S
    s += text(655, 96, "Відповідь: цоколь Type S", 12, "#1f8a3b", "middle", "bold")
    s += circle(655, 168, 40, "#e7f3ea", GREEN, 2.5)
    s += circle(655, 168, 22, "#fff", GREEN, 1.8)
    s += text(655, 173, "2A", 12, "#1f8a3b", "middle", "bold")
    s += text(655, 228, "різьба під ОДИН номінал", 10, INK, "middle", "bold")
    s += text(655, 244, "більший не вкрутиш; перехідник не вийняти", 9, GREY, "middle", style="italic")
    s += text(655, 286, "→ пере-«жирнити» не можна", 12, "#1f8a3b", "middle", "bold")
    s += text(655, 312, "(NEC забороняє старий цоколь, 1940)", 9.5, GREY, "middle", style="italic")
    save("fig-3-8i-3-penny-tamper.svg", s)


# ── Рис. 3.8c.1 — форм-фактори запобіжників ──────────────────────────────────
def fig_fuse_formfactors():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 30, "Запобіжники: основні форм-фактори", 19, INK, "middle", "bold")
    s += text(W / 2, 51, "та сама ідея «найслабшої ланки» — у різних корпусах під різні задачі",
              11, GREY, "middle", style="italic")
    cyt = 130
    # 1) скляний картридж 5×20
    cx = 150
    s += rect(cx - 60, cyt - 16, 120, 32, "#eaf3f7", "#7fa8bd", 2, 6)
    s += rect(cx - 70, cyt - 16, 11, 32, "#c7c7c7", INK, 1.5, 2)
    s += rect(cx + 59, cyt - 16, 11, 32, "#c7c7c7", INK, 1.5, 2)
    s += polyline([(cx - 56, cyt), (cx - 30, cyt - 7), (cx - 8, cyt + 7),
                   (cx + 14, cyt - 7), (cx + 36, cyt + 7), (cx + 56, cyt)], "#c0271e", 1.8)
    s += text(cx, cyt + 44, "скляний 5×20 мм", 12, INK, "middle", "bold")
    s += text(cx, cyt + 61, "видно нитку; мала відкл. здатність", 9, GREY, "middle", style="italic")
    # 2) керамічний
    cx = 380
    s += rect(cx - 60, cyt - 16, 120, 32, "#efe6d6", "#b59b6a", 2, 6)
    s += rect(cx - 70, cyt - 16, 11, 32, "#c7c7c7", INK, 1.5, 2)
    s += rect(cx + 59, cyt - 16, 11, 32, "#c7c7c7", INK, 1.5, 2)
    s += text(cx, cyt + 4, "пісок", 9, "#9a8050", "middle", style="italic")
    s += text(cx, cyt + 44, "керамічний (з піском)", 12, INK, "middle", "bold")
    s += text(cx, cyt + 61, "велика відкл. здатність (мережа)", 9, GREY, "middle", style="italic")
    # 3) ножовий авто
    cx = 600
    s += rect(cx - 34, cyt - 30, 68, 40, "#e6b800", "#a98a00", 2, 5)
    s += line(cx - 20, cyt + 10, cx - 20, cyt + 40, "#9a9a9a", 5)
    s += line(cx + 20, cyt + 10, cx + 20, cyt + 40, "#9a9a9a", 5)
    s += text(cx, cyt - 6, "ATO", 10, INK, "middle", "bold")
    s += text(cx, cyt + 61, "ножовий (авто)", 12, INK, "middle", "bold")
    s += text(cx, cyt + 78, "колір = номінал; 12 В", 9, GREY, "middle", style="italic")
    # 4) SMD
    cx = 775
    s += rect(cx - 30, cyt - 12, 60, 26, "#2a2a2a", "#101010", 2, 4)
    s += text(cx, cyt + 6, "2A", 10, "#f0f0f0", "middle", "bold")
    s += text(cx, cyt + 44, "SMD (на плату)", 12, INK, "middle", "bold")
    s += text(cx, cyt + 61, "крихітний, для друк. плат", 9, GREY, "middle", style="italic")
    s += rect(70, 282, W - 140, 48, "#f4f7f4", GREEN, 1.5, 10)
    s += text(W / 2, 302, "Корпус добирають під струм, напругу, місце монтажу — і під потрібну відключну здатність:",
              11, INK, "middle", "bold")
    s += text(W / 2, 320, "скло показує нитку, та гасить лише мале коротке; кераміка з піском приборкує велике.",
              10, GREY, "middle", style="italic")
    save("fig-3-8c-1-fuse-formfactors.svg", s)


# ── Рис. 3.8c.2 — маркування й шкала швидкості ───────────────────────────────
def fig_fuse_markings():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 30, "Що написано на корпусі — і шкала швидкості", 19, INK, "middle", "bold")
    s += text(W / 2, 51, "номінальний струм ≠ струм спрацювання; плюс напруга, відключна здатність і літера швидкості",
              10.5, GREY, "middle", style="italic")
    cx, cyt = 200, 120
    s += text(cx, cyt - 34, "маркування на корпусі", 10.5, INK, "middle", "bold")
    s += rect(cx - 72, cyt - 18, 144, 36, "#eaf3f7", "#7fa8bd", 2, 6)
    s += rect(cx - 83, cyt - 18, 12, 36, "#c7c7c7", INK, 1.5, 2)
    s += rect(cx + 71, cyt - 18, 12, 36, "#c7c7c7", INK, 1.5, 2)
    s += text(cx, cyt + 5, "T 2A 250V", 15, INK, "middle", "bold")
    bx, bw = 372, 458
    yb = 90
    for title, desc, col in [
        ("Номінальний струм (2A)", "несе вічно; рве при ~2× і вище (крива §1.3.8)", "#1f47b5"),
        ("Номінальна напруга (250V)", "максимум, який безпечно розірве; ≥ напруги кола", "#1f8a3b"),
        ("Відключна здатність", "найбільше коротке, яке згасить без вибуху", "#c0271e"),
    ]:
        s += rect(bx, yb, bw, 46, "#fafafa", col, 1.5, 8)
        s += text(bx + 12, yb + 20, title, 12, col, "start", "bold")
        s += text(bx + 12, yb + 38, desc, 10, INK, "start")
        yb += 56
    sy = 312
    s += text(W / 2, sy - 22, "Літера швидкості (та сама крива §1.3.8, різна стрімкість):", 12, INK, "middle", "bold")
    x0, step = 200, 115
    s += line(x0 - 24, sy, x0 + 4 * step + 24, sy, "#bbbbbb", 2)
    for i, l in enumerate(["FF", "F", "M", "T", "TT"]):
        x = x0 + i * step
        s += circle(x, sy, 16, "#fff", INK, 2)
        s += text(x, sy + 5, l, 12, INK, "middle", "bold")
    s += text(x0 - 24, sy + 36, "швидкі → напівпровідники", 10.5, "#1f47b5", "middle", "bold")
    s += text(x0 + 4 * step + 24, sy + 36, "повільні → пускові кидки (мотори, БЖ)", 10.5, "#c0271e", "middle", "bold")
    save("fig-3-8c-2-fuse-markings.svg", s)


# ── Рис. 3.7c.1 (shunt) — шунт міряє струм за спадом напруги ──────────────────
def fig_shunt_sense():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 30, "Шунт: міряємо струм за крихітним спадом напруги", 18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "малий відомий опір у розрив кола; спад на ньому V = I·R, звідси струм I = V/R",
              11, GREY, "middle", style="italic")
    y = 170
    s += line(70, y, 330, y, INK, 3)
    s += line(490, y, 760, y, INK, 3)
    s += rect(330, y - 16, 160, 32, "#eef2fb", "#1f47b5", 2.2, 6)
    s += text(410, y + 5, "R_шунт = 1 мΩ", 12.5, "#1f47b5", "middle", "bold")
    s += arrow(150, y, 250, y, RED, 3)
    s += text(200, y - 12, "I = 10 А", 13, RED, "middle", "bold")
    s += arrow(560, y, 660, y, RED, 3)
    # вольтметр над шунтом
    vx, vy = 410, y - 78
    s += circle(vx, vy, 24, "#fff", INK, 2.2)
    s += text(vx, vy + 5, "V", 15, INK, "middle", "bold")
    s += text(vx + 34, vy + 4, "= 10 мВ", 12.5, INK, "start", "bold")
    s += line(vx - 17, vy + 17, 350, y - 16, INK, 1.8)
    s += line(vx + 17, vy + 17, 470, y - 16, INK, 1.8)
    s += rect(205, y + 50, W - 410, 58, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, y + 73, "I = V / R = 10 мВ / 1 мΩ = 10 А", 14, INK, "middle", "bold")
    s += text(W / 2, y + 95, "малий опір → майже не заважає колу (мала вставна R і втрата I²R)",
              10.5, GREY, "middle", style="italic")
    save("fig-3-7c-1-shunt-sense.svg", s)


# ── Рис. 3.7c.2 (shunt) — 4-провідне підключення Кельвіна ─────────────────────
def fig_kelvin_4wire():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 30, "Чому в шунта 4 проводи: підключення Кельвіна", 18.5, INK, "middle", "bold")
    s += text(W / 2, 51, "розділяємо шлях струму й шлях вимірювання — і опір проводів та контактів випадає з результату",
              10.5, GREY, "middle", style="italic")
    s += line(W / 2, 70, W / 2, H - 84, FAINT, 1.5)
    # ===== ЛІВОРУЧ: 2 проводи (з помилкою) =====
    s += text(240, 92, "2 проводи — з помилкою", 13, RED, "middle", "bold")
    yl = 210
    s += line(60, yl, 150, yl, INK, 3)
    s += rect(150, yl - 10, 36, 20, "#fdecea", RED, 1.6, 3)
    s += text(168, yl - 16, "R_лід", 8.5, RED, "middle", "bold")
    s += rect(206, yl - 14, 118, 28, "#eef2fb", "#1f47b5", 2, 5)
    s += text(265, yl + 4, "R_шунт", 11, "#1f47b5", "middle", "bold")
    s += rect(324, yl - 10, 36, 20, "#fdecea", RED, 1.6, 3)
    s += text(342, yl - 16, "R_лід", 8.5, RED, "middle", "bold")
    s += line(360, yl, 430, yl, INK, 3)
    s += arrow(95, yl, 132, yl, RED, 2.6)
    s += text(110, yl - 12, "I", 12, RED, "middle", "bold")
    vy = 128
    s += circle(255, vy, 22, "#fff", INK, 2)
    s += text(255, vy + 5, "V", 14, INK, "middle", "bold")
    s += line(150, yl - 14, 150, vy, INK, 1.8)
    s += line(150, vy, 233, vy, INK, 1.8)
    s += line(360, yl - 14, 360, vy, INK, 1.8)
    s += line(360, vy, 277, vy, INK, 1.8)
    # ===== ПРАВОРУЧ: 4 проводи (Кельвін) =====
    s += text(650, 92, "4 проводи (Кельвін) — точно", 13, GREEN, "middle", "bold")
    yr = 210
    xc = 650
    s += line(486, yr, 588, yr, INK, 3)
    s += rect(588, yr - 14, 124, 28, "#eef2fb", "#1f47b5", 2, 5)
    s += text(650, yr + 4, "R_шунт", 11, "#1f47b5", "middle", "bold")
    s += line(712, yr, 818, yr, INK, 3)
    s += arrow(520, yr, 558, yr, RED, 2.6)
    s += text(536, yr - 12, "I", 12, RED, "middle", "bold")
    s += arrow(742, yr, 800, yr, RED, 2.6)
    s += text(650, yr + 32, "сила (force): несе струм", 9.5, RED, "middle", "bold")
    s += circle(xc, vy, 22, "#fff", INK, 2)
    s += text(xc, vy + 5, "V", 14, INK, "middle", "bold")
    s += line(606, yr - 14, 606, vy, "#1f8a3b", 1.8)
    s += line(606, vy, xc - 22, vy, "#1f8a3b", 1.8)
    s += line(694, yr - 14, 694, vy, "#1f8a3b", 1.8)
    s += line(694, vy, xc + 22, vy, "#1f8a3b", 1.8)
    s += text(xc, 170, "сенс (sense): майже без струму", 9.5, GREEN, "middle", "bold")
    # ===== пояснення внизу =====
    s += rect(40, 312, 398, 66, "#fdecea", RED, 1.4, 8)
    s += text(239, 334, "Вольтметр бачить спад на проводах І шунті —", 10.5, INK, "middle", "bold")
    s += text(239, 352, "завищує. При 1 мΩ навіть 0.3 мΩ контактів = +30 %.", 10.5, INK, "middle", "bold")
    s += rect(442, 312, 398, 66, "#e7f3ea", GREEN, 1.4, 8)
    s += text(641, 334, "Сенсорні проводи майже без струму → без спаду", 10.5, INK, "middle", "bold")
    s += text(641, 352, "в них. Вольтметр бачить ЛИШЕ опір шунта.", 10.5, INK, "middle", "bold")
    save("fig-3-7c-2-kelvin-4wire.svg", s)


# ── Рис. 3.7c.1 — кольоровий код резистора (4 кільця) ─────────────────────────
def fig_color_bands():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 32, "Як прочитати резистор: кольорові кільця", 19, INK, "middle", "bold")
    s += text(W / 2, 53, "4 кільця: цифра · цифра · множник · допуск (кільце допуску стоїть скраю, трохи окремо)",
              11, GREY, "middle", style="italic")
    # ── резистор ──
    cy = 112
    s += line(180, cy, 322, cy, "#9a9a9a", 6)
    s += line(558, cy, 700, cy, "#9a9a9a", 6)
    s += rect(320, cy - 32, 240, 64, "#efe2c8", "#b8a37a", 2, 16)
    for bx, col in [(360, "#7a4a1e"), (404, "#1b1b1b"), (448, "#c0271e")]:
        s += rect(bx - 9, cy - 31, 18, 62, col, "none", 0)
    s += rect(521, cy - 31, 18, 62, "#c9a227", "none", 0)
    # ролі над кільцями
    s += text(360, cy - 44, "цифра 1", 10, INK, "middle", "bold")
    s += text(404, cy - 58, "цифра 2", 10, INK, "middle", "bold")
    s += text(448, cy - 44, "множник", 10, INK, "middle", "bold")
    s += text(530, cy - 58, "допуск", 10, INK, "middle", "bold")
    s += line(404, cy - 52, 404, cy - 33, GREY, 1)
    s += line(530, cy - 52, 530, cy - 33, GREY, 1)
    # значення під кільцями
    s += text(360, cy + 56, "1", 14, "#7a4a1e", "middle", "bold")
    s += text(404, cy + 56, "0", 14, INK, "middle", "bold")
    s += text(448, cy + 56, "×100", 12, "#c0271e", "middle", "bold")
    s += text(530, cy + 56, "±5%", 12, "#9a7d1a", "middle", "bold")
    # приклад
    s += rect(150, 188, W - 300, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 213, "коричневий·чорний·червоний·золотий → 1 0 ×100 = 1000 Ω = 1 кΩ, ±5%",
              13, INK, "middle", "bold")
    # ── легенда кольорів ──
    s += text(W / 2, 260, "Колір → цифра (той самий колір як множник 10^цифра)", 12, INK, "middle", "bold")
    leg = [("0", "#1b1b1b", "#fff", "чорн."), ("1", "#7a4a1e", "#fff", "кор."),
           ("2", "#c0271e", "#fff", "черв."), ("3", "#e08030", "#000", "оранж."),
           ("4", "#e6c100", "#000", "жовт."), ("5", "#1f8a3b", "#fff", "зел."),
           ("6", "#1f47b5", "#fff", "син."), ("7", "#7a3fb0", "#fff", "фіол."),
           ("8", "#8a8a8a", "#000", "сір."), ("9", "#f2f2f2", "#000", "біл.")]
    x0, w, gap = 64, 44, 28
    for i, (d, col, tc, nm) in enumerate(leg):
        x = x0 + i * (w + gap)
        s += rect(x, 277, w, 28, col, "#c9c9c9", 1.2, 4)
        s += text(x + w / 2, 297, d, 15, tc, "middle", "bold")
        s += text(x + w / 2, 320, nm, 9.5, GREY, "middle")
    # золото/срібло + примітки
    s += rect(80, 342, W - 160, 34, "#fff8ee", "#c9a227", 1.6, 10)
    s += text(W / 2, 364, "Золоте кільце: множник ×0.1 або допуск ±5%.   Срібне: ×0.01 або ±10%.",
              12, INK, "middle", "bold")
    s += text(W / 2, 400, "5 кілець (точні резистори): цифра · цифра · цифра · множник · допуск.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 422, "Напрям читання: кільце допуску — скраю; читають від протилежного краю.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 448, "Якщо кольори стерлися чи сумнівні (кор./черв./оранж. при поганому світлі) — виміряй омметром (§1.6).",
              10.5, GREY, "middle", style="italic")
    save("fig-3-7c-1-color-bands.svg", s)


# ── Рис. 3.7c.2 — SMD-коди резисторів ────────────────────────────────────────
def fig_smd_codes():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 32, "SMD-резистори: цифрові коди", 19, INK, "middle", "bold")
    s += text(W / 2, 53, "На крихітних SMD немає кілець — номінал друкують числовим кодом", 11, GREY, "middle", style="italic")

    def chip(cx, cy, code, title, decode, result):
        out = text(cx, cy - 44, title, 11, GREEN, "middle", "bold")
        out += rect(cx - 58, cy - 30, 116, 60, "#2a2a2a", "#101010", 2, 8)
        out += text(cx, cy + 9, code, 22, "#f4f4f4", "middle", "bold")
        out += text(cx, cy + 58, decode, 12, INK, "middle", "bold")
        out += text(cx, cy + 80, result, 12.5, "#c0271e", "middle", "bold")
        return out

    s += chip(210, 132, "472", "3 цифри: 2 цифри + нулі-множник",
              "47 × 10² (два нулі)", "= 4700 Ω = 4.7 кΩ")
    s += chip(610, 132, "4701", "4 цифри (точні): 3 цифри + множник",
              "470 × 10¹ (один нуль)", "= 4700 Ω = 4.7 кΩ")
    s += chip(210, 288, "4R7", "літера R = десяткова кома",
              "4R7 → 4.7 Ω    ·    R47 → 0.47 Ω", "(R стоїть на місці коми)")
    s += chip(610, 288, "000", "нуль = перемичка",
              "000 або 0 → перемичка", "= 0 Ω (просто дротик)")
    s += line(W / 2, 82, W / 2, H - 52, FAINT, 1.4)
    s += rect(70, H - 46, W - 140, 32, "#f4f7f4", GREEN, 1.4, 10)
    s += text(W / 2, H - 25, "Код дає НОМІНАЛ; справжнє значення — у межах допуску, а напевне скаже лише омметр (§1.6).",
              11.5, INK, "middle", "bold")
    save("fig-3-7c-2-smd-codes.svg", s)


# ── Рис. 3.5m.1 — мапа одиниць: Дж / Вт·год / кВт·год / мА·год ────────────────
def fig_energy_units():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 34, "Арифметика енергії: джоуль, ват-година, мА·год", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "енергія = потужність × час; а мА·год — це заряд (струм×час), не енергія",
              11.5, GREY, "middle", style="italic")

    def box(x, y, w, h, title, sub, fill, stroke):
        out = rect(x, y, w, h, fill, stroke, 2, 10)
        out += text(x + w / 2, y + 27, title, 14.5, INK, "middle", "bold")
        if sub:
            out += text(x + w / 2, y + 47, sub, 11, GREY, "middle")
        return out

    # ── ЕНЕРГІЯ: рядок одиниць ──
    s += text(W / 2, 96, "ЕНЕРГІЯ  (потужність × час)", 13, GREEN, "middle", "bold")
    y1 = 112
    s += box(60, y1, 170, 66, "Джоуль (Дж)", "= Вт·с — одиниця СІ", "#eef5ef", GREEN)
    s += box(335, y1, 170, 66, "Ват-год (Вт·год)", "= 3600 Дж", "#eef5ef", GREEN)
    s += box(610, y1, 170, 66, "кіловат-год", "= 1000 Вт·год = 3.6 МДж", "#eef5ef", GREEN)
    s += arrow(232, y1 + 33, 333, y1 + 33, INK, 2.2)
    s += text(282, y1 + 22, "×3600", 11, INK, "middle", "bold")
    s += arrow(507, y1 + 33, 608, y1 + 33, INK, 2.2)
    s += text(558, y1 + 22, "×1000", 11, INK, "middle", "bold")

    # ── ЗАРЯД (не енергія!) ──
    y2 = 250
    s += box(60, y2, 196, 66, "мА·год / А·год", "заряд = струм × час", "#fbece9", RED)
    s += text(158, y2 - 10, "ЦЕ ЗАРЯД — не енергія!", 12, RED, "middle", "bold")
    # міст: заряд × напругу → енергія (Вт·год)
    s += arrow(258, y2 + 6, 392, y1 + 62, INK, 2.4)
    s += text(300, 232, "× напругу V", 12, "#b06a00", "start", "bold")
    s += text(300, 300, "А·год × В = Вт·год", 11, INK, "start", "bold")

    # ── середня потужність ──
    s += rect(486, y2, 294, 66, "#f3f7f3", GREEN, 1.8, 12)
    s += text(633, y2 + 26, "Середня потужність", 12.5, INK, "middle", "bold")
    s += text(633, y2 + 48, "P_сер = енергія ÷ час", 13.5, INK, "middle", "bold")

    # ── підсумковий рядок ──
    s += rect(60, H - 56, W - 120, 34, "#fff8ee", ORANGE, 1.6, 10)
    s += text(W / 2, H - 35, "Час роботи від батареї = (її енергія, Вт·год) ÷ (середня потужність споживача, Вт).",
              12, INK, "middle", "bold")
    save("fig-3-5m-1-energy-units.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Тема 1.3.10 — Три шляхи тепла: кондукція, конвекція, випромінювання
# (Рис. 3.10.k)
# ═════════════════════════════════════════════════════════════════════════════

def _arc_wave(x, y, color, n=3, dx=11, amp=15):
    """Хвилі ІЧ-випромінювання: кілька дуг, що розходяться."""
    out = ""
    for i in range(n):
        xx = x + i * dx
        out += f'<path d="M {xx},{y-amp} Q {xx+8},{y} {xx},{y+amp}" fill="none" stroke="{color}" stroke-width="1.8"/>\n'
    return out


# ── Рис. 3.10.1 — три механізми як три фізичні картини ───────────────────────
def fig310_three_mechanisms():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 32, "Три — і тільки три — способи перенести тепло", 21, INK, "middle", "bold")
    s += text(W / 2, 54, "у кожного свій носій і свій закон; усе тепло у Всесвіті йде однією з цих трьох доріг",
              12, GREY, "middle", style="italic")
    colW = (W - 80) / 3
    x0 = 40
    # 1. КОНДУКЦІЯ — естафета коливань у твердому тілі
    cx = x0 + colW * 0.5
    s += rect(x0 + 10, 80, colW - 20, 300, "#fff6ef", HEAT, 1.8, 12)
    s += text(cx, 106, "КОНДУКЦІЯ", 14.5, HEAT, "middle", "bold")
    s += text(cx, 124, "conduction · крізь речовину", 10.5, GREY, "middle", style="italic")
    for i in range(5):
        ax = x0 + 40 + i * 38
        col = RED if i == 0 else (ORANGE if i <= 2 else BLUE)
        s += circle(ax, 180, 12, "#fde0d6" if i <= 2 else "#eef2fb", col, 1.8)
        s += text(ax, 184, "+", 9, col, "middle", "bold")
        for a in range(0, 360, 90):
            rr = (10 - i * 1.8)
            rr = max(rr, 2)
            s += line(ax, 180, ax + rr * math.cos(math.radians(a)), 180 + rr * math.sin(math.radians(a)), col, 1.2)
        if i < 4:
            s += arrow(ax + 13, 180, ax + 25, 180, INK, 1.3)
    s += text(cx, 212, "гаряче →→→ холодне", 10.5, INK, "middle", "bold")
    s += text(cx, 230, "атоми «штовхають» сусідів", 10, GREY, "middle", style="italic")
    s += rect(x0 + 30, 252, colW - 60, 40, "#fff", HEAT, 1.4, 8)
    s += text(cx, 270, "Q/t = k · A · ΔT / L", 14, INK, "middle", "bold")
    s += text(cx, 286, "(закон Фур'є)", 9.5, GREY, "middle", style="italic")
    s += text(cx, 320, "тверде тіло, що не рухається:", 10, INK, "middle")
    s += text(cx, 336, "кристал деталі, корпус,", 10, INK, "middle")
    s += text(cx, 352, "паста, тіло радіатора", 10, INK, "middle")
    # 2. КОНВЕКЦІЯ — рідина/газ виносить тепло
    cx = x0 + colW * 1.5
    s += rect(x0 + 10 + colW, 80, colW - 20, 300, "#eef7f0", GREEN, 1.8, 12)
    s += text(cx, 106, "КОНВЕКЦІЯ", 14.5, GREEN, "middle", "bold")
    s += text(cx, 124, "convection · потоком плину", 10.5, GREY, "middle", style="italic")
    s += rect(cx - 26, 196, 52, 22, "#cdd5da", INK, 1.6, 3)
    s += text(cx, 211, "гаряче", 9, INK, "middle")
    for dxp in (-40, -14, 14, 40):
        s += arrow(cx + dxp, 192, cx + dxp, 150, GREEN, 2)
        s += circle(cx + dxp, 150, 5, "#cfeccd", GREEN, 1.4)
    s += text(cx, 140, "нагріте легшає → тікає вгору", 10, GREEN, "middle", "bold")
    for dxp in (-52, 52):
        s += arrow(cx + dxp, 226, cx + dxp, 250, BLUE, 1.6, "3 3")
    s += text(cx, 268, "холодне підтікає знизу", 10, BLUE, "middle")
    s += rect(x0 + 30 + colW, 282, colW - 60, 40, "#fff", GREEN, 1.4, 8)
    s += text(cx, 300, "Q/t = h · A · ΔT", 14, INK, "middle", "bold")
    s += text(cx, 316, "(закон Ньютона; h залежить від обдуву)", 9, GREY, "middle", style="italic")
    s += text(cx, 348, "ребра радіатора → повітря;", 10, INK, "middle")
    s += text(cx, 364, "вентилятор підсилює h у рази", 10, INK, "middle")
    # 3. ВИПРОМІНЮВАННЯ — ІЧ-світло крізь порожнечу
    cx = x0 + colW * 2.5
    s += rect(x0 + 10 + 2 * colW, 80, colW - 20, 300, "#fdf3e0", "#a06a00", 1.8, 12)
    s += text(cx, 106, "ВИПРОМІНЮВАННЯ", 13.5, "#a06a00", "middle", "bold")
    s += text(cx, 124, "radiation · ІЧ-світлом", 10.5, GREY, "middle", style="italic")
    s += circle(cx, 185, 26, "#fde6c2", "#a06a00", 2)
    s += text(cx, 190, "T", 15, "#a06a00", "middle", "bold", "italic")
    for a in range(0, 360, 45):
        bx = cx + 30 * math.cos(math.radians(a))
        by = 185 + 30 * math.sin(math.radians(a))
        s += _arc_wave(bx, by - 6, "#d08a1e", 2, 8, 9)
    s += text(cx, 250, "будь-яке тіло світить в ІЧ", 10, INK, "middle", "bold")
    s += text(cx, 266, "(не треба ні дотику, ні повітря)", 10, GREY, "middle", style="italic")
    s += rect(x0 + 30 + 2 * colW, 282, colW - 60, 40, "#fff", "#a06a00", 1.4, 8)
    s += text(cx, 300, "Q/t = ε · σ · A · T⁴", 13.5, INK, "middle", "bold")
    s += text(cx, 316, "(Стефан—Больцман; круто росте з T)", 9, GREY, "middle", style="italic")
    s += text(cx, 348, "за низьких T електроніки — мало;", 10, INK, "middle")
    s += text(cx, 364, "нитка, Сонце, жар — головний шлях", 10, INK, "middle")
    save("fig-3-10-1-three-mechanisms.svg", s)


# ── Рис. 3.10.2 — кондукція: закон Фур'є й тепло-електрична аналогія ──────────
def fig310_conduction():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 32, "Кондукція: закон Фур'є — точний близнюк R = ρ·L/A", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "тепловий потік крізь брусок тим більший, чим коротший і товщий шлях і чим «гладший» матеріал",
              12, GREY, "middle", style="italic")
    # брусок із градієнтом
    bx, by, bw, bh = 120, 110, 360, 70
    # заливка-градієнт від гарячого (червоний) до холодного (синій) смугами
    nseg = 18
    for i in range(nseg):
        t = i / (nseg - 1)
        r = int(0xc0 + (0x1f - 0xc0) * t)
        g = int(0x27 + (0x47 - 0x27) * t)
        b = int(0x1e + (0xb5 - 0x1e) * t)
        col = f"#{r:02x}{g:02x}{b:02x}"
        s += rect(bx + i * bw / nseg, by, bw / nseg + 1, bh, col, "none", 0)
    s += rect(bx, by, bw, bh, "none", INK, 2, 4)
    s += text(bx - 10, by + 30, "T_гар", 12, RED, "end", "bold")
    s += text(bx - 10, by + 46, "(гаряче)", 9.5, GREY, "end")
    s += text(bx + bw + 10, by + 30, "T_хол", 12, BLUE, "start", "bold")
    s += text(bx + bw + 10, by + 46, "(холодне)", 9.5, GREY, "start")
    s += arrow(bx + 40, by - 16, bx + bw - 40, by - 16, HEAT, 2.6)
    s += text(bx + bw / 2, by - 24, "потік тепла Q/t", 11.5, HEAT, "middle", "bold")
    # розміри
    s += line(bx, by + bh + 14, bx + bw, by + bh + 14, INK, 1.4)
    s += line(bx, by + bh + 9, bx, by + bh + 19, INK, 1.4)
    s += line(bx + bw, by + bh + 9, bx + bw, by + bh + 19, INK, 1.4)
    s += text(bx + bw / 2, by + bh + 30, "довжина шляху L", 11, INK, "middle", "bold")
    s += text(bx + bw + 70, by + bh / 2 + 4, "переріз A", 10.5, INK, "start")
    # формула
    s += rect(560, 100, 270, 90, "#fff6ef", HEAT, 1.8, 12)
    s += text(695, 130, "Q/t = k · A · ΔT / L", 17, INK, "middle", "bold")
    s += text(695, 158, "k — теплопровідність матеріалу", 10.5, GREY, "middle")
    s += text(695, 176, "(Вт/(м·°C)); ΔT = T_гар − T_хол", 10, GREY, "middle")
    # аналогія
    s += rect(60, 230, W - 120, 70, "#f4f7f4", GREEN, 1.8, 12)
    s += text(W / 2, 256, "Та сама геометрія, що в електриці — лише величини інші:", 13, INK, "middle", "bold")
    s += text(245, 284, "ел. опір:   R = ρ · L / A", 13, BLUE, "middle", "bold")
    s += text(W / 2, 284, "↔", 18, INK, "middle", "bold")
    s += text(625, 284, "тепловий опір:   Rθ = L / (k · A)", 13, HEAT, "middle", "bold")
    # таблиця k
    s += text(W / 2, 332, "Теплопровідність k (більше — краще проводить тепло):", 12, INK, "middle", "bold")
    items = [("мідь", "≈400", GREEN), ("алюміній", "≈200", GREEN), ("сталь", "≈50", INK),
             ("термопаста", "1–10", ORANGE), ("пластик", "≈0.2", RED), ("повітря", "≈0.025", RED)]
    bw2 = (W - 120) / len(items)
    for i, (nm, kv, col) in enumerate(items):
        x = 60 + i * bw2
        s += rect(x + 4, 348, bw2 - 8, 50, "#fff", col, 1.5, 8)
        s += text(x + bw2 / 2, 368, nm, 11, INK, "middle", "bold")
        s += text(x + bw2 / 2, 388, kv, 12, col, "middle", "bold")
    save("fig-3-10-2-conduction.svg", s)


# ── Рис. 3.10.3 — конвекція: природна проти примусової ───────────────────────
def fig310_convection():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 32, "Конвекція: рухоме повітря виносить тепло (а вентилятор — швидше)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "коефіцієнт h каже, наскільки бадьоро плин забирає тепло з поверхні; обдув піднімає його в рази",
              12, GREY, "middle", style="italic")
    s += line(W / 2, 76, W / 2, H - 60, FAINT, 1.5)

    def _finned(cx, base_y):
        out = rect(cx - 70, base_y, 140, 16, "#8a949e", INK, 2, 0)
        for i in range(9):
            out += line(cx - 64 + i * 16, base_y, cx - 64 + i * 16, base_y - 50, "#8a949e", 4)
        out += rect(cx - 26, base_y + 16, 52, 20, "#2b2b2b", INK, 1.8, 3)
        out += text(cx, base_y + 31, "деталь", 9, "#ffffff", "middle")
        return out

    # природна
    s += text(215, 100, "ПРИРОДНА КОНВЕКЦІЯ", 13, GREEN, "middle", "bold")
    s += text(215, 118, "повітря саме тікає вгору (повільно)", 10, GREY, "middle", style="italic")
    s += _finned(215, 250)
    for dxp in (-50, -18, 18, 50):
        s += arrow(215 + dxp, 196, 215 + dxp, 150, GREEN, 1.8)
    s += text(215, 138, "теплий струмінь угору", 9.5, GREEN, "middle")
    s += rect(120, 296, 200, 56, "#eef7f0", GREEN, 1.5, 8)
    s += text(215, 318, "h ≈ 5–25 Вт/(м²·°C)", 12.5, INK, "middle", "bold")
    s += text(215, 338, "тихо, але слабко", 10, GREY, "middle", style="italic")
    # примусова
    s += text(645, 100, "ПРИМУСОВА КОНВЕКЦІЯ", 13, RED, "middle", "bold")
    s += text(645, 118, "вентилятор жене повітря силоміць", 10, GREY, "middle", style="italic")
    s += _finned(645, 250)
    # вентилятор
    s += circle(560, 200, 22, "#eef2fb", BLUE, 2)
    for a in range(0, 360, 60):
        s += line(560, 200, 560 + 18 * math.cos(math.radians(a)), 200 + 18 * math.sin(math.radians(a)), BLUE, 2)
    s += text(560, 240, "вентилятор", 9.5, BLUE, "middle", "bold")
    for yy in (185, 200, 215):
        s += arrow(584, yy, 690, yy, RED, 2.2)
    s += text(645, 165, "потужний потік крізь ребра", 9.5, RED, "middle", "bold")
    s += rect(545, 296, 200, 56, "#fdeeee", RED, 1.5, 8)
    s += text(645, 318, "h ≈ 50–250 Вт/(м²·°C)", 12.5, INK, "middle", "bold")
    s += text(645, 338, "у рази більше → Rθ менший", 10, GREY, "middle", style="italic")
    s += text(W / 2, H - 22, "Q/t = h · A · ΔT  →  ребра дають велику A, вентилятор піднімає h: обидва множники працюють на відведення.",
              11, INK, "middle", "bold")
    save("fig-3-10-3-convection.svg", s)


# ── Рис. 3.10.4 — випромінювання: чому крива T⁴ така крута ────────────────────
def fig310_radiation():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 32, "Випромінювання ∝ T⁴: мовчазне при кімнатній T, шалене при розжаренні", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "подвоїти абсолютну температуру — означає випромінювати у 16 разів більше (2⁴); тому росте лавиною",
              12, GREY, "middle", style="italic")
    gx0, gy0, gx1, gy1 = 110, 340, 700, 96
    s += arrow(gx0, gy0, gx1 + 10, gy0, INK, 2)
    s += arrow(gx0, gy0, gx0, gy1 - 6, INK, 2)
    s += text(gx1 + 14, gy0 + 4, "T (К)", 12, INK, "start", "bold")
    s += text(gx0 - 10, gy1 - 2, "потужність випромінювання", 11, INK, "end", "bold")
    # крива T^4 (нормуємо на T=1000K → майже верх)
    Tmax = 1100.0
    span = gx1 - gx0 - 20
    h = gy0 - gy1 - 10
    pts = []
    for i in range(0, 101):
        T = i / 100.0 * Tmax
        val = (T / 1000.0) ** 4
        val = min(val, 1.25)
        pts.append((gx0 + (T / Tmax) * span, gy0 - val / 1.25 * h))
    s += polyline(pts, "#a06a00", 3.0)

    def mark(T, lab, col, dyl=0):
        x = gx0 + (T / Tmax) * span
        val = min((T / 1000.0) ** 4, 1.25)
        y = gy0 - val / 1.25 * h
        out = line(x, gy0, x, gy0 + 5, INK, 1.4)
        out += text(x, gy0 + 19, f"{T:.0f}", 10, GREY, "middle")
        out += circle(x, y, 4.5, col, col, 1)
        out += text(x + 6, y - 8 + dyl, lab, 10.5, col, "start", "bold")
        return out

    s += mark(300, "≈25 °C: плата, радіатор (майже нічого)", BLUE, 0)
    s += mark(600, "≈325 °C: дуже гаряча деталь", ORANGE, 0)
    s += mark(1000, "≈730 °C: жар, тен почервонів", RED, 0)
    # пояснення абсолютної T
    s += rect(150, 96, 300, 70, "#fdf3e0", "#a06a00", 1.6, 10)
    s += text(300, 120, "T — АБСОЛЮТНА (кельвіни):", 11.5, "#a06a00", "middle", "bold")
    s += text(300, 140, "К = °C + 273", 12, INK, "middle", "bold")
    s += text(300, 158, "нитка лампи ~2500 °C ≈ 2800 К → 2800⁴ — велетенська", 9, GREY, "middle", style="italic")
    s += rect(60, 360, W - 120, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 382, "Висновок для електроніки: при ~25–80 °C радіатор віддає теплом-провідністю й конвекцією, а не світлом.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 398, "Чорне анодування трохи додає (ε ближче до 1), та головні гравці — кондукція до радіатора й конвекція від нього.",
              10, GREY, "middle", style="italic")
    save("fig-3-10-4-radiation.svg", s)


# ── Рис. 3.10.5 — повний тепловий шлях деталі: де яка дорога ──────────────────
def fig310_full_path():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому працює радіатор: ланцюг із кондукції, тоді конвекції", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "тепло від кристала йде твердими тілами (кондукція), а з ребер зривається в повітря (конвекція + трохи ІЧ)",
              11.5, GREY, "middle", style="italic")
    y = 150
    # ланцюг вузлів
    nodes = [("кристал", "junction", RED, 95),
             ("корпус", "case", ORANGE, 235),
             ("паста", "TIM", "#a06a00", 370),
             ("радіатор", "heat sink", GREEN, 510),
             ("повітря", "ambient", BLUE, 690)]
    for nm, en, col, x in nodes:
        w = 92 if nm != "повітря" else 110
        s += rect(x - w / 2, y - 26, w, 52, "#fff", col, 2, 8)
        s += text(x, y - 4, nm, 12.5, col, "middle", "bold")
        s += text(x, y + 14, en, 9, GREY, "middle", style="italic")
    # стрілки + механізм між вузлами
    segs = [(95, 235, "кондукція", HEAT, "крізь кремній і метал"),
            (235, 370, "кондукція", HEAT, "крізь пасту (виганяє повітря)"),
            (370, 510, "кондукція", HEAT, "у тіло радіатора"),
            (510, 690, "конвекція + ІЧ", GREEN, "ребра → рухоме повітря")]
    for x1, x2, mech, col, note in segs:
        mid = (x1 + x2) / 2
        s += arrow(x1 + 50, y, x2 - 56, y, col, 2.4)
        s += text(mid, y - 36, mech, 10.5, col, "middle", "bold")
        s += text(mid, y + 38, note, 8.8, GREY, "middle", style="italic")
    # випромінювання збоку від радіатора
    s += _arc_wave(560, y + 54, "#d08a1e", 3, 10, 10)
    s += text(600, y + 70, "трохи ІЧ-випромінювання (мале за низьких T)", 9.5, "#a06a00", "start", style="italic")
    # підсумок-аналогія з §3.9
    s += rect(60, 250, W - 120, 110, "#f4f7f4", GREEN, 1.8, 12)
    s += text(W / 2, 276, "Кожна ланка — це тепловий опір Rθ (§1.3.9), і всі вони стоять ПОСЛІДОВНО:", 12.5, INK, "middle", "bold")
    s += text(W / 2, 302, "Rθ(j→корпус) + Rθ(паста) + Rθ(радіатор→повітря)  →  ΔT = P · Rθ_сум", 13, INK, "middle", "bold")
    s += text(W / 2, 330, "«Поліпшити охолодження» = зменшити котрусь ланку: кращий контакт і паста (кондукція),",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 348, "більша площа ребер і обдув (конвекція). Радіатор б'є саме по найслабшій ланці — віддачі в повітря.",
              11, GREY, "middle", style="italic")
    save("fig-3-10-5-full-path.svg", s)


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
    # §3.8 Запобіжники й самовідновні PTC
    fig38_overcurrent()
    fig38_fuse_anatomy()
    fig38_time_current()
    fig38_fast_slow()
    fig38_ptc_mechanism()
    fig38_ptc_cycle()
    fig38_fuse_vs_ptc()
    # §3.9 Тепловий опір і радіатор
    fig39_heat_must_go()
    fig39_thermal_ohm()
    fig39_thermal_chain()
    fig39_heatsink_rescue()
    fig39_tim()
    fig39_modes()
    # §3.3 вставка — дроти
    fig_wires()
    # §3.4 історія — полювання на нитку
    fig_filament_timeline()
    fig_carbon_vs_tungsten()
    fig_brittle_vs_ductile()
    # §3.4 вставка — NTC проти кидка струму
    fig_ntc_inrush()
    # §3.5 вставка (🧮) — одиниці енергії
    fig_energy_units()
    # §3.7 вставка (🔌) — маркування резисторів
    fig_color_bands()
    fig_smd_codes()
    # §3.7 вставка (🧮) — ряди E
    fig_eseries_ladder()
    fig_eseries_tiling()
    # §3.7 вставка (🔌) — шунти й Кельвін
    fig_shunt_sense()
    fig_kelvin_4wire()
    # §3.8 вставка (🔌) — запобіжник як компонент
    fig_fuse_formfactors()
    fig_fuse_markings()
    # §3.8 історія (📜) — народження запобіжника
    fig_fuse_timeline()
    fig_fuse_weak_link()
    fig_fuse_penny_tamper()
    # §3.9 вставка (🔌) — тепловий шлях
    fig_thermal_stack()
    fig_isolation_mount()
    # §3.9 вставка (🧮) — теплова RC-модель
    fig_thermal_rc()
    fig_pulse_vs_steady()

    fig310_three_mechanisms()
    fig310_conduction()
    fig310_convection()
    fig310_radiation()
    fig310_full_path()
    print("OK — фігури розділу 3 (повна, +§3.7 резистор) згенеровано в", OUT)
