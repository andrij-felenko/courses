# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 10.1 — «Топології перетворювачів» (Модуль 10).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються по темах
(Рис. М.Р.Т.k) у тексті; для історії до розділу — тема 0 (Рис. 10.1.0.k).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+) / гаряче
BLUE  = "#1f47b5"   # від'ємний (−) / холодне
GREEN = "#1f8a3b"   # поле / акцент-успіх
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
AMBER = "#caa24a"   # акцент-міф / увага
COPP  = "#b5763a"   # мідь (обмотки)
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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


def coil_v(x, y0, y1, loops, r=9, color=COPP, w=2.4, side=1):
    """Вертикальна обмотка: loops півкіл, що випинаються вбік side (+1 праворуч)."""
    seg = (y1 - y0) / loops
    d = f'M {x:.1f} {y0:.1f} '
    sweep = 1 if side > 0 else 0
    for i in range(loops):
        yb = y0 + seg * (i + 1)
        d += f'A {r:.1f} {seg/2:.1f} 0 0 {sweep} {x:.1f} {yb:.1f} '
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"/>\n'


def coil_h(x0, x1, y, loops=4, r=10, color=COPP, w=2.6):
    """Горизонтальна обмотка (символ котушки): loops півкіл, що випинаються вгору."""
    seg = (x1 - x0) / loops
    d = f'M {x0:.1f} {y:.1f} '
    for i in range(loops):
        xb = x0 + seg * (i + 1)
        d += f'A {seg/2:.1f} {r:.1f} 0 0 1 {xb:.1f} {y:.1f} '
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"/>\n'


def poly(points, color=INK, w=2.4, dash=None):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def polygon(points, fill, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    op = f' fill-opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<polygon points="{pts}" fill="{fill}"{op}/>\n'


def cap_v(x, ytop, ybot, color=INK, w=3):
    """Конденсатор (дві пластини) вертикально на проводі x між ytop..ybot."""
    ym = (ytop + ybot) / 2
    return (line(x, ytop, x, ym - 6, color, 2)
            + line(x - 15, ym - 6, x + 15, ym - 6, color, w)
            + line(x - 15, ym + 6, x + 15, ym + 6, color, w)
            + line(x, ym + 6, x, ybot, color, 2))


def diode_up(x, ytop, ybot, color=INK):
    """Діод вістрям угору (струм тече знизу вгору) на проводі x."""
    ym = (ytop + ybot) / 2
    return (line(x, ybot, x, ym + 11, color, 2)
            + f'<path d="M {x-11} {ym+11} L {x+11} {ym+11} L {x} {ym-11} Z" '
              f'fill="none" stroke="{color}" stroke-width="2"/>\n'
            + line(x - 11, ym - 11, x + 11, ym - 11, color, 2.6)
            + line(x, ym - 11, x, ytop, color, 2))


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 10.1.0.1 — таймлайн історії імпульсного живлення ────────────────────
def fig_timeline():
    W, H = 920, 940
    s = header(W, H)
    s += text(W / 2, 40, "Імпульсне живлення: довга низка, у якій Apple — пізній вузол", 21,
              INK, "middle", "bold")
    s += text(W / 2, 62,
              "перемикання струму існувало за десятиліття до 1977-го; справжній тригер — дешевий швидкий транзистор",
              12.5, GREY, "middle", style="italic")
    spine = 232
    top, bot = 96, H - 70
    s += line(spine, top, spine, bot, GREY, 3)
    # (рік, хто, що, акцент-важливе, акцент-міф)
    nodes = [
        ("1930-ті", "Вібратор у радіоприймачі", "Механічний переривач кришить 6 В на пульсації → трансформатор → B+ для ламп", False, False),
        ("1958", "IBM 704 · Pioneer Magnetics", "Перші комутаційні регулятори — ще на тиратронах (лампах)", False, False),
        ("1959", "General Electric", "Опублікована рання схема напівпровідникового стабілізатора-перемикача", False, False),
        ("1962", "Telstar · Minuteman", "Космос і ракети: кожен грам дорогий → ефективність важливіша за простоту", True, False),
        ("1966–67", "Tektronix · RO Associates", "Портативний осцилограф; перший 20-кГц імпульсний БЖ як готовий товар", False, False),
        ("кін. 1960-х", "Швидкі високовольтні транзистори", "Motorola, SSPI, Siemens-Edison-Swan: дешевий ключ — ОСЬ де справжня революція", True, False),
        ("1969–71", "DEC PDP-11/20 · HP 2100A", "Імпульсне живлення входить у серійні міні-комп'ютери", False, False),
        ("1975", "IBM 5100 · HP 2640A", "Імпульсні БЖ — уже ~8% ринку, за два роки до Apple II", False, False),
        ("1976", "SG1524 (Р. Маммано)", "Перша мікросхема ШІМ-керування — оце справді змінює зручність розробки", True, False),
        ("1976", "Boschert, 80 Вт", "Безвентиляторний flyback у серії — той самий клас, що буде в Apple", False, False),
        ("1977", "Apple II · Род Голт", "Акуратний 38-Вт flyback. Гарний інженерно — але ПІЗНІЙ у низці, не її початок", False, True),
    ]
    n = len(nodes)
    for i, (yr, who, q, hot, myth) in enumerate(nodes):
        y = top + 22 + (bot - top - 44) * i / (n - 1)
        if myth:
            s += circle(spine, y, 11, "#fff", AMBER, 3.2)
            s += circle(spine, y, 5, AMBER, AMBER, 0)
            col = INK
        elif hot:
            s += circle(spine, y, 8.5, "#fff", GREEN, 3)
            col = INK
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.4)
            col = INK
        s += text(spine - 22, y + 5, yr, 13, GREY, "end", "bold")
        s += text(spine + 26, y - 4, who, 15.5, (RED if myth else (GREEN if hot else col)),
                  "start", "bold")
        s += text(spine + 26, y + 15, q, 12.5, col, "start", style="italic")
    # легенда-висновок унизу
    ly = bot + 30
    s += circle(spine - 150, ly - 4, 8.5, "#fff", GREEN, 3)
    s += text(spine - 134, ly, "ключовий поштовх", 12.5, INK, "start")
    s += circle(spine + 20, ly - 4, 11, "#fff", AMBER, 3.2)
    s += circle(spine + 20, ly - 4, 5, AMBER, AMBER, 0)
    s += text(spine + 38, ly, "вузол, який міф видає за «початок»", 12.5, INK, "start")
    s += text(W / 2, H - 16,
              "«Кожен комп'ютер копіює дизайн Голта» — міф: і топології, і ринок існували задовго до Apple II",
              12.5, RED, "middle", style="italic")
    save("fig-10-0-1-timeline.svg", s)


# ── Рис. 10.1.0.2 — електромеханічний вібратор як предок ─────────────────────
def fig_vibrator():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 36, "Вібратор: механічний предок усіх імпульсних БЖ (~1930-ті)", 21,
              INK, "middle", "bold")
    s += text(W / 2, 58,
              "перерви постійний струм → трансформуй → випрями. Тут ключ механічний; згодом його замінить транзистор",
              12.5, GREY, "middle", style="italic")

    yb = 250  # базова лінія схеми

    # ── 1. Батарея 6 В ──
    bx = 70
    s += line(bx, yb - 34, bx, yb + 34, INK, 2)            # довга пластина (+)
    s += line(bx + 14, yb - 18, bx + 14, yb + 18, INK, 5)  # коротка пластина (−)
    s += text(bx + 3, yb - 46, "+", 17, RED, "middle", "bold")
    s += text(bx + 14, yb + 60, "6 В", 14, INK, "middle", "bold")
    s += text(bx + 14, yb + 78, "акумулятор", 12, GREY, "middle")
    s += line(bx + 14, yb, 150, yb, INK, 2)                # провід до вузла

    # ── 2. Вібратор (магніт + якір + контакти) ──
    vx = 215
    s += rect(vx - 52, yb - 96, 132, 192, "none", FAINT, 2, 12)
    s += text(vx + 14, yb - 106, "ВІБРАТОР", 13, INK, "middle", "bold")
    # котушка електромагніту
    s += coil_v(vx - 34, yb - 40, yb + 40, 5, r=8, color=COPP, w=2.6, side=-1)
    s += text(vx - 54, yb + 70, "магніт", 11.5, GREY, "middle")
    # якір-пружина (вертикальна пластина)
    ay = yb
    s += line(vx + 8, yb - 70, vx + 8, yb + 70, INK, 3)    # пружна пластина
    s += text(vx + 8, yb + 88, "якір+пружина", 11.5, GREY, "middle")
    # два контакти (верхній/нижній)
    s += circle(vx + 30, yb - 38, 4, RED, RED, 0)
    s += circle(vx + 30, yb + 38, 4, BLUE, BLUE, 0)
    s += line(vx + 8, yb - 38, vx + 30, yb - 38, INK, 2)
    s += line(vx + 8, yb + 38, vx + 30, yb + 38, INK, 2)
    # стрілка «тягне–вертає»
    s += arrow(vx - 18, yb - 8, vx + 2, yb - 8, INK, 1.8)
    s += text(vx - 8, yb - 18, "≈100 Гц", 10.5, GREY, "middle", style="italic")

    # ── 3. Трансформатор (крок угору) ──
    tx = 470
    # провід від контактів до первинної (середній відвід)
    s += line(vx + 30, yb - 38, tx - 70, yb - 38, INK, 2)
    s += line(vx + 30, yb + 38, tx - 70, yb + 38, INK, 2)
    s += line(150, yb, tx - 70, yb, INK, 2)               # середній відвід ← батарея
    # осердя
    s += rect(tx - 6, yb - 86, 12, 172, FAINT, INK, 2)
    s += text(tx, yb - 98, "осердя", 11, GREY, "middle")
    # первинна (менше витків, ліворуч)
    s += coil_v(tx - 22, yb - 64, yb + 64, 6, r=10, color=COPP, w=2.6, side=-1)
    s += line(tx - 70, yb - 38, tx - 22, yb - 38, COPP, 2)
    s += line(tx - 70, yb + 38, tx - 22, yb + 38, COPP, 2)
    s += line(tx - 70, yb, tx - 22, yb, COPP, 2)          # середній відвід
    s += text(tx - 40, yb + 100, "первинна", 11.5, GREY, "middle")
    # вторинна (більше витків, праворуч)
    s += coil_v(tx + 22, yb - 78, yb + 78, 11, r=11, color=COPP, w=2.6, side=1)
    s += text(tx + 40, yb + 100, "вторинна ×30", 11.5, GREEN, "middle", "bold")
    # нижній кінець вторинної → спільний нуль (замикаємо контур випрямляча)
    s += line(tx + 22, yb + 78, tx + 22, yb + 120, INK, 2)

    # ── 4. Випрямляч ──
    rx = 660
    s += line(tx + 22, yb - 78, rx, yb - 78, COPP, 2)
    s += line(rx, yb - 78, rx, yb - 30, INK, 2)
    # діод-трикутник
    s += f'<path d="M {rx-12} {yb-30} L {rx+12} {yb-30} L {rx} {yb-8} Z" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += line(rx - 12, yb - 8, rx + 12, yb - 8, INK, 2.6)
    s += line(rx, yb - 8, rx, yb + 18, INK, 2)
    s += text(rx + 30, yb - 18, "випрямляч", 12, INK, "middle")
    s += text(rx + 30, yb - 4, "(лампа або", 10.5, GREY, "middle")
    s += text(rx + 30, yb + 10, "синхр. контакти)", 10.5, GREY, "middle")

    # ── 5. Фільтр + вихід B+ ──
    ox = 800
    s += line(rx, yb + 18, ox, yb + 18, INK, 2)
    s += line(ox, yb + 18, ox, yb - 40, INK, 2)
    # конденсатор фільтра
    s += line(ox - 16, yb + 40, ox + 16, yb + 40, INK, 3)
    s += line(ox - 16, yb + 52, ox + 16, yb + 52, INK, 3)
    s += line(ox, yb + 18, ox, yb + 40, INK, 2)
    s += line(ox, yb + 52, ox, yb + 80, INK, 2)
    s += text(ox + 30, yb + 50, "фільтр", 11.5, GREY, "middle")
    # вихід
    s += circle(ox, yb - 40, 5, RED, RED, 0)
    s += text(ox, yb - 54, "B+ ≈ 250 В", 14, RED, "middle", "bold")
    s += text(ox, yb + 96, "до ламп", 11.5, GREY, "middle")

    # зворотний провід (земля)
    s += line(bx + 14, yb + 34, bx + 14, yb + 120, INK, 2)
    s += line(bx + 14, yb + 120, ox, yb + 120, INK, 2)
    s += line(ox, yb + 80, ox, yb + 120, INK, 2)
    s += text((bx + ox) / 2, yb + 136, "спільний нуль", 11, GREY, "middle")

    # підсумкова стрічка
    s += rect(60, H - 52, W - 120, 34, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 30,
              "Той самий ланцюг «переривай → трансформуй → випрямляй» живе в кожному сучасному імпульсному БЖ — лише ключ тепер транзистор, а частота в тисячі разів вища",
              12.5, INK, "middle")
    save("fig-10-0-2-vibrator.svg", s)


# ── Рис. 10.1.1.1 — спільне ядро всіх топологій ──────────────────────────────
def fig_core():
    W, H = 920, 450
    s = header(W, H)
    s += text(W / 2, 34, "Спільне ядро всіх імпульсних топологій: перемикач + котушка + конденсатор",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "buck, boost, buck-boost — лише різні способи під'єднати ту саму котушку",
              13, GREY, "middle", style="italic")
    yr = 200           # рівень верхнього проводу
    yg = 330           # земля
    # Vвх
    s += plus(95, yr, 11, RED)
    s += text(95, yr - 26, "Vвх", 15, INK, "middle", "bold")
    s += line(95, yr + 11, 95, yg, INK, 2)         # вхід до землі (джерело)
    s += line(95, yr, 175, yr, INK, 2)
    # ключ S
    s += rect(175, yr - 26, 86, 52, "#eef3fb", BLUE, 2, 8)
    s += text(218, yr - 3, "ключ S", 14, BLUE, "middle", "bold")
    s += text(218, yr + 15, "ВКЛ / ВИКЛ", 11, BLUE, "middle")
    s += line(261, yr, 300, yr, INK, 2)
    # вузол перемикання SW + повертальний шлях (діод)
    sx = 300
    s += circle(sx, yr, 4, INK, INK, 0)
    s += text(sx, yr - 22, "вузол", 11, GREY, "middle")
    s += text(sx, yr - 9, "перемикання", 11, GREY, "middle")
    s += diode_up(sx, yr, yg)
    s += text(sx - 64, (yr + yg) / 2 + 4, "повертальний", 11, GREY, "middle")
    s += text(sx - 64, (yr + yg) / 2 + 18, "шлях (діод/", 11, GREY, "middle")
    s += text(sx - 64, (yr + yg) / 2 + 32, "2-й ключ)", 11, GREY, "middle")
    # котушка (підсвічена зеленим) — зірка схеми
    s += rect(330, yr - 34, 150, 50, "#eef8ef", GREEN, 2, 10)
    s += coil_h(345, 465, yr, loops=4, r=12, color=GREEN, w=3)
    s += text(405, yr + 34, "КОТУШКА — переносить енергію", 12.5, GREEN, "middle", "bold")
    s += line(480, yr, 560, yr, INK, 2)
    # вихідний конденсатор
    s += circle(560, yr, 4, INK, INK, 0)
    s += cap_v(560, yr, yg, INK, 3)
    s += text(560, yr - 18, "C", 14, INK, "middle", "bold")
    s += text(560, yr - 4, "тримає", 10.5, GREY, "middle")
    # навантаження
    s += line(560, yr, 660, yr, INK, 2)
    s += rect(645, yr + 10, 30, 64, "none", INK, 2)
    s += text(660, yr + 48, "наван-", 10.5, GREY, "middle")
    s += line(660, yr + 74, 660, yg, INK, 2)
    s += text(700, yr - 8, "Vвих", 15, RED, "start", "bold")
    # земля
    s += line(95, yg, 660, yg, INK, 2)
    for gx in (95, 660):
        s += line(gx, yg, gx, yg, INK, 2)
    s += text(W / 2, yg + 22, "спільний нуль", 11, GREY, "middle")
    # підсумкова стрічка
    s += rect(70, H - 52, W - 140, 34, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 30,
              "Жоден елемент не гасить напругу в тепло: ключ лише рубає вхід на імпульси, а котушка й конденсатор енергію зберігають і віддають",
              12.5, INK, "middle")
    save("fig-10-1-1-core.svg", s)


# ── Рис. 10.1.1.2 — котушка як маховик струму ────────────────────────────────
def fig_inductor():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому в серці саме КОТУШКА, а не резистор", 19, INK, "middle", "bold")
    # ліва панель: опір зміні струму
    s += rect(40, 60, 400, 320, "none", FAINT, 2, 12)
    s += text(240, 86, "Опір зміні струму:  V = L · (di/dt)", 14.5, INK, "middle", "bold")
    s += coil_h(120, 240, 130, loops=4, r=11, color=COPP, w=3)
    s += arrow(80, 130, 118, 130, INK, 2)
    s += text(95, 118, "I", 13, INK, "middle", "bold")
    s += text(300, 134, "котушка", 12, GREY, "middle")
    # графік i(t)
    gx0, gy0 = 90, 340
    s += arrow(gx0, gy0, gx0, 200, INK, 1.8)        # вісь i
    s += arrow(gx0, gy0, 400, gy0, INK, 1.8)        # вісь t
    s += text(gx0 - 8, 206, "i", 12, INK, "end", "bold")
    s += text(404, gy0 + 4, "t", 12, INK, "start", "bold")
    s += poly([(gx0, gy0), (380, 224)], GREEN, 3)   # лінійне наростання
    s += text(300, 250, "нахил = V/L", 12, GREEN, "middle", "bold")
    s += text(240, 366, "стала напруга → струм РОСТЕ лінійно, не стрибком", 12, INK, "middle")
    # права панель: запас енергії
    s += rect(480, 60, 400, 320, "none", FAINT, 2, 12)
    s += text(680, 86, "Запас енергії:  E = ½ · L · I²", 14.5, INK, "middle", "bold")
    # котушка з полем
    s += coil_h(600, 760, 170, loops=5, r=13, color=COPP, w=3)
    for dy in (0, 1, 2):
        rr = 26 + dy * 16
        s += f'<ellipse cx="680" cy="170" rx="{rr}" ry="{rr*0.62:.0f}" fill="none" stroke="{GREEN}" stroke-width="1.6"/>\n'
    s += text(680, 230, "магнітне поле = запас енергії", 12, GREEN, "middle", "bold")
    # маховик-аналогія
    s += circle(680, 300, 30, "none", INK, 2.4)
    s += circle(680, 300, 5, INK, INK, 0)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        s += line(680 + 8 * math.cos(rad), 300 + 8 * math.sin(rad),
                  680 + 27 * math.cos(rad), 300 + 27 * math.sin(rad), GREY, 2)
    s += text(680, 366, "котушка = маховик для струму: розганяй і гальмуй поступово", 11.5, INK, "middle")
    # низ
    s += rect(70, H - 42, W - 140, 30, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22,
              "Резистор цю енергію спалив би в тепло; котушка її ЗБЕРІГАЄ і повертає — тому переносити енергію можна майже без втрат",
              12, INK, "middle")
    save("fig-10-1-2-inductor.svg", s)


# ── Рис. 10.1.1.3 — дві фази: + напруга, потім − напруга ─────────────────────
def fig_phases():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Дві фази: котушка бачить спершу «+», потім «−» напругу", 19,
              INK, "middle", "bold")

    def panel(x0, title, tcol, vlabel, vcol, ramp_up, note):
        out = rect(x0, 64, 390, 300, "none", FAINT, 2, 12)
        out += text(x0 + 195, 90, title, 14.5, tcol, "middle", "bold")
        yr, yg = 150, 300
        # джерело/повертання
        out += line(x0 + 40, yr, x0 + 120, yr, INK, 2)
        if ramp_up:
            out += rect(x0 + 40, yr - 16, 28, 32, "#eef3fb", BLUE, 2, 5)  # замкнений ключ
            out += line(x0 + 46, yr, x0 + 62, yr, BLUE, 3)
            out += text(x0 + 54, yr - 24, "ключ ВКЛ", 10.5, BLUE, "middle")
        else:
            out += text(x0 + 54, yr - 24, "ключ ВИКЛ", 10.5, GREY, "middle")
            out += line(x0 + 40, yr, x0 + 56, yr - 12, GREY, 2)            # розімкнений
            out += diode_up(x0 + 54, yr, yg)
        # котушка
        out += coil_h(x0 + 130, x0 + 250, yr, loops=4, r=11, color=COPP, w=3)
        out += text(x0 + 190, yr - 22, vlabel, 13, vcol, "middle", "bold")
        out += line(x0 + 250, yr, x0 + 330, yr, INK, 2)
        out += line(x0 + 330, yr, x0 + 330, yg, INK, 2)
        out += cap_v(x0 + 330, yr, yg, INK, 2.6)
        out += line(x0 + 40, yg, x0 + 330, yg, INK, 2)
        out += line(x0 + 40, yr, x0 + 40, yg, INK, 2)
        # стрілка струму
        ay = yr + 40
        if ramp_up:
            out += arrow(x0 + 190, ay + 18, x0 + 190, ay - 4, GREEN, 3)
            out += text(x0 + 215, ay + 8, "струм РОСТЕ", 12, GREEN, "start", "bold")
        else:
            out += arrow(x0 + 190, ay - 4, x0 + 190, ay + 18, RED, 3)
            out += text(x0 + 215, ay + 8, "струм СПАДАЄ", 12, RED, "start", "bold")
        out += text(x0 + 195, 350, note, 11.5, INK, "middle")
        return out

    s += panel(40, "ФАЗА ВКЛ", BLUE, "Vл = +Von", GREEN, True,
               "накопичує «+ вольт-секунди»")
    s += panel(490, "ФАЗА ВИКЛ", GREY, "Vл = −Voff", RED, False,
               "віддає «− вольт-секунди» через діод")
    # центральний цикл
    s += text(W / 2, 210, "↻", 30, INK, "middle", "bold")
    s += rect(70, H - 42, W - 140, 30, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 22,
              "Питання всієї теми: скільки кожної напруги? Відповідь дає один закон — вольт-секундний баланс",
              12, INK, "middle")
    save("fig-10-1-3-phases.svg", s)


# ── Рис. 10.1.1.4 — вольт-секундний баланс (центральна фігура) ───────────────
def fig_voltsec():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 34, "Вольт-секундний баланс — закон, спільний для всіх топологій", 19,
              INK, "middle", "bold")
    x0, x1 = 110, 770
    T = 300
    D = 0.35
    p1u = x0 + T * D            # кінець ВКЛ у періоді 1
    p1 = x0 + T                 # кінець періоду 1
    p2u = p1 + T * D
    p2 = p1 + T
    # ── верхній графік: напруга на котушці ──
    base = 180
    top = base - 74
    bot = base + 42
    s += text(x0 - 18, base - 70, "Vл", 13, INK, "end", "bold")
    s += arrow(x0, base + 60, x0, base - 84, INK, 1.6)
    s += arrow(x0, base, x1 + 20, base, INK, 1.6)
    s += text(x1 + 22, base + 4, "t", 12, INK, "start", "bold")
    # площі (період 1): + зелена, − червона
    s += polygon([(x0, base), (x0, top), (p1u, top), (p1u, base)], "#bfe6c6")
    s += polygon([(p1u, base), (p1u, bot), (p1, bot), (p1, base)], "#f1c4c0")
    s += polygon([(p1, base), (p1, top), (p2u, top), (p2u, base)], "#bfe6c6")
    s += polygon([(p2u, base), (p2u, bot), (p2, bot), (p2, base)], "#f1c4c0")
    # контур напруги
    s += poly([(x0, top), (p1u, top), (p1u, bot), (p1, bot), (p1, top),
               (p2u, top), (p2u, bot), (p2, bot), (p2, base)], INK, 2.6)
    s += text((x0 + p1u) / 2, top - 8, "+Von", 12.5, GREEN, "middle", "bold")
    s += text((p1u + p1) / 2, bot + 16, "−Voff", 12.5, RED, "middle", "bold")
    # ширини D·T і (1−D)·T
    s += line(x0, base + 54, p1u, base + 54, GREEN, 1.4)
    s += text((x0 + p1u) / 2, base + 68, "D·T", 11, GREEN, "middle", "bold")
    s += line(p1u, base + 54, p1, base + 54, RED, 1.4)
    s += text((p1u + p1) / 2, base + 68, "(1−D)·T", 11, RED, "middle", "bold")
    # рівняння (між заголовком і графіком)
    s += rect(x0, 52, x1 - x0 + 20, 34, "#f6f6f6", GREY, 1.4, 8)
    s += text((x0 + x1) / 2, 74,
              "сталий режим:  площа(+) = площа(−)   ⇒   Von · D·T = Voff · (1−D)·T   ⇒   середня Vл = 0",
              13.5, INK, "middle", "bold")
    # ── нижній графік: струм котушки ──
    cbase = 430
    chi = cbase - 46
    clo = cbase + 22
    s += text(x0 - 18, cbase - 40, "iл", 13, INK, "end", "bold")
    s += arrow(x0, cbase + 50, x0, cbase - 70, INK, 1.6)
    s += arrow(x0, cbase + 22, x1 + 20, cbase + 22, INK, 1.6)
    s += text(x1 + 22, cbase + 26, "t", 12, INK, "start", "bold")
    # трикутна хвиля, що повертається до того самого рівня
    s += poly([(x0, clo), (p1u, chi), (p1, clo), (p2u, chi), (p2, clo)], COPP, 3)
    s += line(x0, clo, x1, clo, GREY, 1.4, dash="5,5")
    s += text(x1 - 8, clo + 18, "той самий рівень щоцикл", 11, GREY, "end", style="italic")
    s += text((x0 + p1u) / 2, chi - 8, "росте", 11, GREEN, "middle")
    s += text((p1u + p1) / 2, chi - 8, "спадає", 11, RED, "middle")
    # дужка періоду
    s += line(x0, cbase + 38, p1, cbase + 38, INK, 1.4)
    s += text((x0 + p1) / 2, cbase + 52, "період T", 11, INK, "middle", "bold")
    # підсумок
    s += rect(70, H - 46, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 25,
              "Струм періодичний — за цикл повертається до себе, тобто Δi = 0. Це й означає: «+ вольт-секунди» точно гасять «−». Звідси випливає коефіцієнт перетворення будь-якої топології",
              12, INK, "middle")
    save("fig-10-1-4-voltsec.svg", s)


# ── Рис. 10.1.1.5 — чому баланс мусить виконуватися (інакше — розгін) ─────────
def fig_runaway():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 34, "Чому баланс — закон, а не побажання", 19, INK, "middle", "bold")
    x0, x1 = 110, 840
    T = 130
    D = 0.4

    def saw(y_at_start, drift):
        """Точки трикутної хвилі на 5 періодів зі зсувом середнього на drift/цикл."""
        pts = []
        lvl = y_at_start
        x = x0
        for k in range(5):
            pts.append((x, lvl))
            pts.append((x + T * D, lvl - 26))
            lvl = lvl - drift
            pts.append((x + T, lvl))
            x += T
        return pts

    # (а) збалансовано
    yb = 150
    s += text(x0, yb - 56, "Збалансовано: середня Vл = 0", 13, GREEN, "start", "bold")
    s += arrow(x0, yb + 30, x0, yb - 40, INK, 1.5)
    s += arrow(x0, yb, x1, yb, INK, 1.5)
    s += poly(saw(yb - 6, 0), COPP, 2.6)
    s += line(x0, yb - 6, x1 - 30, yb - 6, GREEN, 1.4, dash="6,5")
    s += text(x1 - 6, yb - 12, "струм стоїть", 11, GREEN, "end", style="italic")
    # (б) дисбаланс
    yc = 330
    s += text(x0, yc - 86, "Дисбаланс (+ вольт-секунди переважають): струм повзе вгору щоцикл",
              13, RED, "start", "bold")
    s += arrow(x0, yc + 30, x0, yc - 76, INK, 1.5)
    s += arrow(x0, yc, x1, yc, INK, 1.5)
    s += poly(saw(yc - 6, 16), COPP, 2.6)
    s += poly([(x0, yc - 6), (x1 - 40, yc - 6 - 16 * 4.2)], RED, 1.6, dash="6,5")
    s += text(x1 - 6, yc - 78, "→ насичення, аварія", 11, RED, "end", "bold")
    # підсумок
    s += rect(70, H - 46, W - 140, 32, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 25,
              "Будь-який надлишок вольт-секунд накопичується, доки щось не згорить. Тому сталий режим самобалансується, а зворотний зв'язок лише підправляє D, коли вхід чи навантаження пливуть",
              11.5, INK, "middle")
    save("fig-10-1-5-runaway.svg", s)


# ── Рис. 10.1.1.6 — один закон відмикає всі топології ────────────────────────
def fig_map():
    W, H = 920, 460
    s = header(W, H)
    s += text(W / 2, 34, "Один закон — усі топології", 19, INK, "middle", "bold")
    # хаб
    hx, hy = 250, 230
    s += rect(hx - 150, hy - 50, 300, 100, "#eef8ef", GREEN, 2.4, 14)
    s += text(hx, hy - 16, "ВОЛЬТ-СЕКУНДНИЙ", 15, GREEN, "middle", "bold")
    s += text(hx, hy + 6, "БАЛАНС", 15, GREEN, "middle", "bold")
    s += text(hx, hy + 30, "Von·ton = Voff·toff", 13, INK, "middle")

    def box(x, y, title, tcol, lines, solved):
        out = rect(x, y, 300, 86, "#eef8ef" if solved else "#f6f6f6",
                   GREEN if solved else GREY, 2, 10)
        mark = "✓ тут" if solved else "🔒 далі"
        out += text(x + 14, y + 24, title, 14, tcol, "start", "bold")
        out += text(x + 286, y + 24, mark, 12, (GREEN if solved else GREY), "end", "bold")
        for i, ln in enumerate(lines):
            out += text(x + 14, y + 46 + i * 18, ln, 11.5, INK, "start")
        return out

    bx = 600
    s += box(bx, 70, "buck (знижує)", INK,
             ["ВКЛ: Vл = Vвх−Vвих;  ВИКЛ: Vл = −Vвих", "⇒ Vвих = D · Vвх   (звірка з §7.4.2)"], True)
    s += box(bx, 190, "boost (підвищує)", INK,
             ["той самий закон, інша розкладка", "→ Розділ 10.1.3"], False)
    s += box(bx, 310, "buck-boost", INK,
             ["і вгору, і вниз від входу", "→ Розділ 10.1.4"], False)
    # стрілки від хаба
    for ty in (113, 233, 353):
        s += arrow(hx + 150, hy, bx - 6, ty, GREEN if ty == 113 else GREY, 2.2)
    # підпис
    s += rect(70, H - 46, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 25,
              "Тут застосуємо закон до buck (відомого з §7.4.2); boost і buck-boost відмикають наступні теми тим самим ключем",
              12, INK, "middle")
    save("fig-10-1-6-map.svg", s)


def mosfet_box(x, y, w, h, label, sub, color=BLUE):
    out = rect(x, y, w, h, "#eef3fb", color, 2, 8)
    out += text(x + w / 2, y + h / 2 - 2, label, 13, color, "middle", "bold")
    out += text(x + w / 2, y + h / 2 + 15, sub, 10.5, color, "middle")
    return out


# ── Рис. 10.1.2.1 — пульсація струму котушки ─────────────────────────────────
def fig_ripple():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Пульсація струму котушки: трикутник на тлі навантаження", 18,
              INK, "middle", "bold")
    # формула
    s += rect(70, 48, W - 140, 30, "#f6f6f6", GREY, 1.4, 8)
    s += text(W / 2, 68, "ΔI = (Vвх − Vвих) · tвкл / L = (Vвх − Vвих) · D / (L · f)", 14,
              INK, "middle", "bold")
    ox, oy = 90, 320
    s += arrow(ox, oy + 8, ox, 100, INK, 1.6)
    s += arrow(ox, oy, 830, oy, INK, 1.6)
    s += text(ox - 8, 108, "iл", 12, INK, "end", "bold")
    s += text(832, oy + 4, "t", 12, INK, "start", "bold")
    dc = 232
    hi, lo = 192, 272
    s += line(ox, dc, 720, dc, GREY, 1.5, dash="6,5")
    s += text(726, dc + 4, "Iнаван", 12, GREY, "start", "bold")
    s += text(726, dc + 19, "(середнє)", 10, GREY, "start")
    T = 252
    D = 0.42
    pts = [(ox, lo)]
    x = ox
    for k in range(2):
        pts.append((x + T * D, hi))
        pts.append((x + T, lo))
        x += T
    s += poly(pts, COPP, 3)
    # ΔI double-arrow на піку
    px = ox + T * D
    s += arrow(px + 60, hi, px + 60, lo, INK, 1.6)
    s += arrow(px + 60, lo, px + 60, hi, INK, 1.6)
    s += text(px + 70, (hi + lo) / 2 + 4, "ΔI", 13, INK, "start", "bold")
    # нахили
    s += text(ox + 30, lo - 18, "+(Vвх−Vвих)/L", 11, GREEN, "start", "bold")
    s += text(ox + T * D + 16, hi + 30, "−Vвих/L", 11, RED, "start", "bold")
    # tвкл / tвикл дужки
    s += line(ox, lo + 18, ox + T * D, lo + 18, GREEN, 1.4)
    s += text(ox + T * D / 2, lo + 32, "tвкл", 10.5, GREEN, "middle", "bold")
    s += line(ox + T * D, lo + 18, ox + T, lo + 18, RED, 1.4)
    s += text(ox + T * D + (T - T * D) / 2, lo + 32, "tвикл", 10.5, RED, "middle", "bold")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 21,
              "Більший L або вища частота f → менша ΔI. У CCM пульсація не залежить від навантаження — вона лиш гойдається навколо середнього струму",
              11.5, INK, "middle")
    save("fig-10-2-1-ripple.svg", s)


# ── Рис. 10.1.2.2 — CCM / межа / DCM ─────────────────────────────────────────
def fig_ccm_dcm():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Три режими: безперервний (CCM), межа, переривчастий (DCM)", 18,
              INK, "middle", "bold")

    def panel(x0, title, tcol, dc, touch, dcm):
        out = rect(x0, 58, 270, 250, "none", FAINT, 2, 10)
        out += text(x0 + 135, 82, title, 13.5, tcol, "middle", "bold")
        bx, by = x0 + 30, 270        # вісь
        out += arrow(bx, by + 6, bx, 100, INK, 1.4)
        out += arrow(bx, by, x0 + 250, by, INK, 1.4)
        out += text(bx - 8, 108, "iл", 11, INK, "end", "bold")
        amp = 38
        T = 64
        if not dcm:
            hi = by - dc - amp
            lo = by - dc + amp
            pts = [(bx, lo)]
            x = bx
            for k in range(3):
                pts.append((x + T * 0.4, hi))
                pts.append((x + T, lo))
                x += T
            out += poly(pts, COPP, 2.6)
            if touch:
                out += line(bx, by, x0 + 230, by, GREEN, 1.3, dash="4,4")
                out += text(x0 + 135, by - 4, "торкається 0", 10, GREEN, "middle", style="italic")
        else:
            # DCM: росте, падає до 0, лежить на 0
            hi = by - dc - amp
            pts = []
            x = bx
            for k in range(3):
                pts.append((x, by))
                pts.append((x + T * 0.3, hi))
                pts.append((x + T * 0.62, by))
                pts.append((x + T, by))   # лежить на нулі
                x += T
            out += poly(pts, COPP, 2.6)
            out += text(x0 + 150, by - 4, "лежить на 0", 10, RED, "middle", style="italic")
        return out

    s += panel(20, "CCM (важке навантаження)", GREEN, 70, False, False)
    s += panel(325, "МЕЖА: Iнаван = ΔI/2", AMBER, 38, True, False)
    s += panel(630, "DCM (легке навантаження)", RED, 0, False, True)
    # інсет Vвих(Iнаван)
    ix, iy = 120, 360
    s += text(W / 2, 338, "Наслідок для виходу:", 13, INK, "middle", "bold")
    s += arrow(ix, iy + 40, ix, iy - 30, INK, 1.5)
    s += arrow(ix, iy + 40, ix + 360, iy + 40, INK, 1.5)
    s += text(ix - 8, iy - 26, "Vвих", 11, INK, "end", "bold")
    s += text(ix + 362, iy + 44, "Iнаван", 11, INK, "start", "bold")
    s += line(ix + 150, iy, ix + 360, iy, GREEN, 2.6)             # CCM плато
    s += poly([(ix + 20, iy - 24), (ix + 80, iy - 10), (ix + 150, iy)], RED, 2.6)  # DCM росте
    s += line(ix + 150, iy + 40, ix + 150, iy - 30, GREY, 1.2, dash="4,4")
    s += text(ix + 150, iy + 54, "межа", 10, AMBER, "middle", "bold")
    s += text(ix + 255, iy - 8, "CCM: Vвих = D·Vвх (рівно)", 11, GREEN, "middle", "bold")
    s += text(ix + 70, iy - 32, "DCM: Vвих росте", 11, RED, "middle", "bold")
    s += rect(70, H - 38, W - 140, 26, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 20,
              "Діод не пропускає від'ємний струм: щойно навантаження падає нижче ΔI/2, струм лягає на нуль — і Vвих = D·Vвх більше не діє",
              11.5, INK, "middle")
    save("fig-10-2-2-ccm-dcm.svg", s)


# ── Рис. 10.1.2.3 — пульсація вихідної напруги ───────────────────────────────
def fig_vripple():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Пульсація вихідної напруги: дві складові", 18, INK, "middle", "bold")
    # струм у конденсатор (трикутник навколо 0)
    ox = 90
    s += text(ox - 20, 80, "iC", 12, INK, "end", "bold")
    s += text(W / 2, 80, "змінна частина струму котушки тече в конденсатор", 11.5, GREY, "middle", style="italic")
    base1 = 120
    s += line(ox, base1, 720, base1, GREY, 1.3)
    T = 252
    pts = [(ox, base1 + 22)]
    x = ox
    for k in range(2):
        pts.append((x + T * 0.42, base1 - 22))
        pts.append((x + T, base1 + 22))
        x += T
    s += poly(pts, COPP, 2.6)
    # ── напруга: ємнісна (парабола) + ESR (трикутник) ──
    base2 = 300
    s += text(ox - 20, base2, "Vвих", 12, INK, "end", "bold")
    s += line(ox, base2, 720, base2, GREY, 1.3, dash="6,5")
    # ємнісна складова (плавна хвиля)
    cappts = []
    for i in range(0, 505, 5):
        xx = ox + i
        ph = (i % T) / T
        # інтеграл трикутника → парабола; апроксимуємо синусоїдою малою
        yy = base2 - 14 * math.sin(2 * math.pi * ph)
        cappts.append((xx, yy))
    s += poly(cappts, BLUE, 2.2)
    s += text(600, base2 - 22, "ємнісна: ΔV ≈ ΔI/(8·f·C)", 11.5, BLUE, "start", "bold")
    # ESR складова (трикутник, у фазі зі струмом) — зміщена нижче
    base3 = 380
    s += text(ox - 20, base3, "+ESR", 12, INK, "end", "bold")
    s += line(ox, base3, 720, base3, GREY, 1.3, dash="6,5")
    epts = [(ox, base3 + 12)]
    x = ox
    for k in range(2):
        epts.append((x + T * 0.42, base3 - 12))
        epts.append((x + T, base3 + 12))
        x += T
    s += poly(epts, RED, 2.4)
    s += text(600, base3 - 18, "ESR: ΔV = ΔI · ESR", 11.5, RED, "start", "bold")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18,
              "Повна пульсація = ємнісна + на ESR. З керамікою ESR крихітний; з електролітом часто домінує саме він (детально — у Розділі 10.2.4)",
              11, INK, "middle")
    save("fig-10-2-3-vripple.svg", s)


# ── Рис. 10.1.2.4 — асинхронний проти синхронного buck ───────────────────────
def fig_sync():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Синхронний випрямляч: діод → нижній MOSFET", 18, INK, "middle", "bold")

    def buck(x0, title, tcol, sync):
        out = rect(x0, 58, 380, 250, "none", FAINT, 2, 10)
        out += text(x0 + 190, 82, title, 13.5, tcol, "middle", "bold")
        yr, yg = 170, 270
        out += plus(x0 + 30, yr, 9, RED)
        out += text(x0 + 30, yr - 22, "Vвх", 12, INK, "middle", "bold")
        out += line(x0 + 30, yr + 9, x0 + 30, yg, INK, 2)
        out += line(x0 + 30, yr, x0 + 70, yr, INK, 2)
        # верхній ключ
        out += mosfet_box(x0 + 70, yr - 20, 70, 40, "верхній", "MOSFET", BLUE)
        sx = x0 + 175
        out += line(x0 + 140, yr, sx, yr, INK, 2)
        out += circle(sx, yr, 3.5, INK, INK, 0)
        # нижній елемент
        if sync:
            out += mosfet_box(sx - 35, yr + 36, 70, 40, "нижній", "MOSFET", GREEN)
            out += line(sx, yr, sx, yr + 36, INK, 2)
            out += line(sx, yr + 76, sx, yg, INK, 2)
            out += text(sx, yg + 18, "втрати: I²·Rds(on)  ⟵ мізер", 11, GREEN, "middle", "bold")
        else:
            out += diode_up(sx, yr, yg)
            out += text(sx, yg + 18, "втрати: Vf·I ≈ 0.4 В × I", 11, RED, "middle", "bold")
        # котушка + вихід
        out += coil_h(sx + 14, sx + 110, yr, loops=4, r=9, color=COPP, w=2.6)
        out += line(sx + 110, yr, x0 + 340, yr, INK, 2)
        out += cap_v(x0 + 340, yr, yg, INK, 2.4)
        out += line(x0 + 30, yg, x0 + 340, yg, INK, 2)
        out += text(x0 + 355, yr - 6, "Vвих", 12, RED, "start", "bold")
        return out

    s += buck(20, "Асинхронний (з діодом)", RED, False)
    s += buck(520, "Синхронний (2 ключі)", GREEN, True)
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38,
              "Діод завжди падає ~0.4–0.7 В: при низькому Vвих і великому струмі це з'їдає помітний відсоток ККД і гріється.",
              11.5, INK, "middle")
    s += text(W / 2, H - 22,
              "MOSFET з Rds(on) у кілька мОм падає майже нічого (§2.7.5) — тож сучасні buck майже всі синхронні.",
              11.5, INK, "middle")
    save("fig-10-2-4-sync.svg", s)


# ── Рис. 10.1.2.5 — мертвий час і наскрізний струм ───────────────────────────
def fig_deadtime():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Мертвий час: чому два ключі ніколи не відкривають разом", 18,
              INK, "middle", "bold")
    ox = 150
    T = 200
    rows = [("верхній ключ", 100, BLUE, True), ("нижній ключ", 190, GREEN, False)]
    for name, y, col, hs in rows:
        s += text(ox - 14, y + 4, name, 12, col, "end", "bold")
        s += line(ox, y + 18, 820, y + 18, GREY, 1.2)   # рівень 0
        # імпульси: верхній ВКЛ перші 40%, нижній — решта, з мертвим часом
        x = ox
        for k in range(2):
            if hs:
                a, b = x + 8, x + T * 0.42
            else:
                a, b = x + T * 0.50, x + T - 8
            s += poly([(a, y + 18), (a, y - 14), (b, y - 14), (b, y + 18)], col, 2.6)
            x += T
    # мертві зони (заштриховані)
    x = ox
    for k in range(2):
        for (a, b) in [(x + T * 0.42, x + T * 0.50), (x + T - 8, x + T + 8)]:
            s += polygon([(a, 82), (b, 82), (b, 226), (a, 226)], "#f1c4c0", 0.5)
    s += text(ox + T * 0.46, 250, "мертвий час", 10.5, RED, "middle", "bold")
    s += arrow(ox + T * 0.46, 244, ox + T * 0.46, 228, RED, 1.4)
    # під час мертвого часу струм несе вбудований діод
    s += text(ox, 290, "У мертвий час струм котушки несе вбудований діод нижнього MOSFET", 12,
              INK, "start")
    s += text(ox, 308, "(короткочасно — тому надовго лишати його не можна: гріється).", 11, GREY, "start")
    # попередження про shoot-through
    s += rect(70, H - 70, W - 140, 54, "#fbe9e7", RED, 1.6, 8)
    s += text(W / 2, H - 50, "⚠ Перекриття = наскрізний струм (shoot-through):", 12.5, RED, "middle", "bold")
    s += text(W / 2, H - 33,
              "якщо обидва ключі відкриються водночас — це коротке замикання входу на землю крізь них.",
              11.5, INK, "middle")
    s += text(W / 2, H - 18,
              "Замалий мертвий час → вигорання; завеликий → зайві втрати на діоді. Драйвер тримає баланс (§2.7.7).",
              11.5, INK, "middle")
    save("fig-10-2-5-deadtime.svg", s)


# ── Рис. 10.1.2.6 — поведінка на легкому навантаженні ────────────────────────
def fig_lightload():
    W, H = 920, 450
    s = header(W, H)
    s += text(W / 2, 32, "Легке навантаження: три способи поводитися", 18, INK, "middle", "bold")

    def panel(x0, title, tcol, kind, note):
        out = rect(x0, 56, 280, 250, "none", FAINT, 2, 10)
        out += text(x0 + 140, 80, title, 13, tcol, "middle", "bold")
        bx, by = x0 + 26, 200
        out += arrow(bx, by + 40, bx, 110, INK, 1.4)
        out += arrow(bx, by, x0 + 262, by, INK, 1.4)
        out += text(bx - 8, 118, "iл", 11, INK, "end", "bold")
        out += text(x0 + 264, by + 4, "t", 11, INK, "start", "bold")
        T = 70
        if kind == "ccm":      # струм заходить у мінус
            pts = [(bx, by + 18)]
            x = bx
            for k in range(3):
                pts.append((x + T * 0.4, by - 30))
                pts.append((x + T, by + 18))
                x += T
            out += poly(pts, COPP, 2.5)
            out += polygon([(bx, by), (x0 + 240, by), (x0 + 240, by + 22), (bx, by + 22)], "#f1c4c0", 0.45)
            out += text(x0 + 140, by + 34, "струм у мінус — марна циркуляція", 9.5, RED, "middle", "bold")
        elif kind == "dcm":    # емуляція діода
            x = bx
            pts = []
            for k in range(3):
                pts.append((x, by))
                pts.append((x + T * 0.3, by - 34))
                pts.append((x + T * 0.6, by))
                pts.append((x + T, by))
                x += T
            out += poly(pts, COPP, 2.5)
            out += text(x0 + 140, by + 22, "вимикає нижній на нулі (як діод)", 9.5, GREEN, "middle", "bold")
        else:                  # pfm — пачки
            x = bx
            for burst in range(2):
                for k in range(2):
                    out += poly([(x, by), (x + T * 0.3, by - 34), (x + T * 0.6, by)], COPP, 2.5)
                    x += T * 0.6
                x += T * 1.4   # сон
            out += line(bx, by, x0 + 240, by, GREY, 1.1)
            out += text(x0 + 140, by + 22, "пачка імпульсів → довгий сон", 9.5, BLUE, "middle", "bold")
        out += text(x0 + 140, 296, note, 9.5, INK, "middle")
        return out

    s += panel(20, "Forced-PWM (CCM)", RED, "ccm", "стала частота, але втрати на циркуляції")
    s += panel(320, "Емуляція діода (DCM)", GREEN, "dcm", "немає від'ємного струму")
    s += panel(620, "PFM / пропуск імпульсів", BLUE, "pfm", "майже нема перемикань → ощадно")
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38,
              "Синхронний ключ, на відміну від діода, пропускає струм В ОБИДВА боки — тож на легкому навантаженні в CCM струм даремно циркулює.",
              11, INK, "middle")
    s += text(W / 2, H - 22,
              "Емуляція діода прибирає цю втрату; PFM (пропуск імпульсів) додатково вимикає перемикання у сні — звідси висока ефективність у спокої.",
              11, INK, "middle")
    save("fig-10-2-6-lightload.svg", s)


# ── Рис. 10.1.2.7 — ККД від навантаження: PWM проти PFM ──────────────────────
def fig_efficiency():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "ККД від навантаження: forced-PWM проти авто-PFM", 18, INK, "middle", "bold")
    ox, oy = 110, 330
    s += arrow(ox, oy + 8, ox, 80, INK, 1.6)
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += text(ox - 10, 88, "ККД", 12, INK, "end", "bold")
    s += text(822, oy + 4, "Iнаван", 12, INK, "start", "bold")
    # рівні ККД
    for eff, yy in [("90%", 120), ("70%", 200), ("50%", 280)]:
        s += line(ox, yy, 800, yy, FAINT, 1.2)
        s += text(ox - 8, yy + 4, eff, 10.5, GREY, "end")
    # вісь навантаження (лог-підписи)
    labels = ["1 мА", "10 мА", "100 мА", "1 А", "3 А"]
    xs = [ox + 40 + i * 175 for i in range(5)]
    for lx, lb in zip(xs, labels):
        s += line(lx, oy, lx, oy + 5, GREY, 1.2)
        s += text(lx, oy + 20, lb, 10.5, GREY, "middle")
    # PWM: провисає на легкому навантаженні
    pwm = [(xs[0], 290), (xs[1], 235), (xs[2], 160), (xs[3], 122), (xs[4], 132)]
    s += poly(pwm, RED, 3)
    s += text(xs[3] + 8, 112, "forced-PWM", 12, RED, "start", "bold")
    # PFM: тримається на легкому
    pfm = [(xs[0], 150), (xs[1], 132), (xs[2], 126), (xs[3], 124), (xs[4], 138)]
    s += poly(pfm, BLUE, 3, dash="2,0")
    s += text(xs[0] + 2, 140, "авто-PFM", 12, BLUE, "start", "bold")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 21,
              "У спокої (малий струм) виграє PFM — менше перемикань. Під чисте живлення радіо/АЦП беруть forced-PWM: стала частота, передбачувані завади",
              11, INK, "middle")
    save("fig-10-2-7-efficiency.svg", s)


def diode_right(x0, x1, y, color=INK, blocked=False):
    """Діод вістрям праворуч (струм зліва направо) на проводі y між x0..x1."""
    xm = (x0 + x1) / 2
    c = GREY if blocked else color
    out = (line(x0, y, xm - 11, y, c, 2)
           + f'<path d="M {xm-11} {y-11} L {xm-11} {y+11} L {xm+11} {y} Z" '
             f'fill="none" stroke="{c}" stroke-width="2"/>\n'
           + line(xm + 11, y - 11, xm + 11, y + 11, c, 2.6)
           + line(xm + 11, y, x1, y, c, 2))
    if blocked:
        out += line(xm - 16, y - 16, xm + 16, y + 16, RED, 2.4)
    return out


def boost_panel(x0, title, tcol, on):
    out = rect(x0, 64, 400, 280, "none", FAINT, 2, 10)
    out += text(x0 + 200, 88, title, 13.5, tcol, "middle", "bold")
    yr, yg = 170, 300
    # Vвх
    out += plus(x0 + 30, yr, 9, RED)
    out += text(x0 + 30, yr - 22, "Vвх", 12, INK, "middle", "bold")
    out += line(x0 + 30, yr + 9, x0 + 30, yg, INK, 2)
    out += line(x0 + 30, yr, x0 + 55, yr, INK, 2)
    # котушка
    out += coil_h(x0 + 55, x0 + 160, yr, loops=4, r=10, color=COPP, w=2.8)
    sw = x0 + 195
    out += line(x0 + 160, yr, sw, yr, INK, 2)
    out += circle(sw, yr, 3.5, INK, INK, 0)
    out += text(x0 + 110, yr - 18, "Vл = " + ("+Vвх" if on else "Vвх−Vвих"),
                12, (GREEN if on else RED), "middle", "bold")
    # ключ униз до землі
    if on:
        out += line(sw, yr, sw, yg, BLUE, 3)            # замкнено
        out += text(sw - 30, (yr + yg) / 2, "ключ", 11, BLUE, "middle", "bold")
        out += text(sw - 30, (yr + yg) / 2 + 15, "ВКЛ", 11, BLUE, "middle", "bold")
    else:
        out += line(sw, yr, sw, yr + 28, GREY, 2)
        out += line(sw, yr + 28, sw + 18, yr + 14, GREY, 2.4)   # розімкнено
        out += line(sw, yr + 44, sw, yg, GREY, 2)
        out += text(sw - 30, (yr + yg) / 2 + 8, "ВИКЛ", 11, GREY, "middle", "bold")
    # діод до виходу
    out += diode_right(sw, x0 + 320, yr, GREEN, blocked=on)
    out += text(x0 + 285, yr - 16, "діод", 11, (GREY if on else GREEN), "middle")
    # вихід
    out += circle(x0 + 320, yr, 3.5, INK, INK, 0)
    out += cap_v(x0 + 320, yr, yg, INK, 2.6)
    out += line(x0 + 320, yr, x0 + 360, yr, INK, 2)
    out += rect(x0 + 358, yr + 12, 22, 50, "none", INK, 1.8)   # навантаження
    out += line(x0 + 369, yr + 62, x0 + 369, yg, INK, 2)
    out += text(x0 + 372, yr - 6, "Vвих", 12, RED, "start", "bold")
    out += line(x0 + 30, yg, x0 + 369, yg, INK, 2)
    # струмовий шлях
    if on:
        out += arrow(x0 + 95, yr + 14, x0 + 120, yr + 14, GREEN, 2.4)
        out += text(x0 + 150, yr + 40, "котушка запасає; вихід живить лише C", 10.5, INK, "middle")
    else:
        out += arrow(x0 + 240, yr - 14, x0 + 270, yr - 14, GREEN, 2.4)
        out += text(x0 + 200, yr + 40, "струм преться крізь діод; Vл додається до Vвх", 10.5, INK, "middle")
    return out


# ── Рис. 10.1.3.1 — дві фази boost ───────────────────────────────────────────
def fig_boost_phases():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Boost: накопичити в котушці, тоді «підкинути» до входу", 18,
              INK, "middle", "bold")
    s += boost_panel(20, "ФАЗА ВКЛ (ключ замкнено)", BLUE, True)
    s += boost_panel(500, "ФАЗА ВИКЛ (ключ розімкнено)", GREY, False)
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 21,
              "Секрет підвищення — те саме «брикання» котушки (§2.2.5): різке розмикання дає на ній викид напруги, що ДОДАЄТЬСЯ до Vвх",
              11.5, INK, "middle")
    save("fig-10-3-1-phases.svg", s)


# ── Рис. 10.1.3.2 — коефіцієнт Vвих/Vвх = 1/(1−D) ────────────────────────────
def fig_boost_ratio():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Коефіцієнт boost: Vвих / Vвх = 1 / (1 − D)", 18, INK, "middle", "bold")
    ox, oy = 110, 350
    s += arrow(ox, oy + 6, ox, 80, INK, 1.6)
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += text(ox - 10, 88, "Vвих/Vвх", 12, INK, "end", "bold")
    s += text(822, oy + 4, "D", 12, INK, "start", "bold")
    # сітка по y (1..6)
    def Y(r): return oy - (r - 1) * 48
    for r in range(1, 7):
        s += line(ox, Y(r), 800, Y(r), FAINT, 1)
        s += text(ox - 8, Y(r) + 4, f"{r}×", 10.5, GREY, "end")
    def X(d): return ox + d * 760
    for d in (0, 0.25, 0.5, 0.75):
        s += line(X(d), oy, X(d), oy + 5, GREY, 1.2)
        s += text(X(d), oy + 20, f"{d:.2f}", 10.5, GREY, "middle")
    # крива 1/(1-D), кліп на 6×
    pts = []
    d = 0.0
    while d <= 0.84:
        r = 1.0 / (1.0 - d)
        if r > 6:
            break
        pts.append((X(d), Y(r)))
        d += 0.02
    s += poly(pts, GREEN, 3)
    s += line(X(0.84), oy, X(0.84), 90, RED, 1.4, dash="5,5")
    s += text(X(0.84) + 6, 110, "D→1 ⇒ Vвих→∞", 11, RED, "start", "bold")
    s += text(X(0.86) + 6, 130, "(реально ~5–10×:", 10, GREY, "start")
    s += text(X(0.86) + 6, 144, "паразити обмежують)", 10, GREY, "start")
    # точки-орієнтири
    for d, r, lab in [(0, 1, "D=0 → 1×"), (0.5, 2, "0.5 → 2×"), (0.67, 3, "0.67 → 3×"), (0.8, 5, "0.8 → 5×")]:
        s += circle(X(d), Y(r), 4, GREEN, GREEN, 0)
        s += text(X(d) + 8, Y(r) - 6, lab, 10.5, INK, "start", "bold")
    s += rect(70, H - 38, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 20,
              "Vвих ЗАВЖДИ ≥ Vвх: навіть при D=0 вихід дорівнює входу (через котушку й діод). Знизити напругу boost не вміє в принципі",
              11, INK, "middle")
    save("fig-10-3-2-ratio.svg", s)


# ── Рис. 10.1.3.3 — вхід безперервний, вихід імпульсний ──────────────────────
def fig_boost_currents():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "У boost усе навпаки до buck: вхід гладкий, вихід рваний", 18,
              INK, "middle", "bold")
    ox = 100
    T = 240
    # вхідний/котушковий струм — безперервний трикутник
    s += text(ox - 16, 95, "iвх=iл", 11, INK, "end", "bold")
    b1 = 150
    s += line(ox, b1, 720, b1, GREY, 1.2)
    pts = [(ox, b1 + 18)]
    x = ox
    for k in range(2):
        pts.append((x + T * 0.5, b1 - 18))
        pts.append((x + T, b1 + 18))
        x += T
    s += poly(pts, COPP, 2.8)
    s += text(726, b1, "безперервний", 11, GREEN, "start", "bold")
    s += text(726, b1 + 15, "(добре для входу/EMI)", 9.5, GREY, "start")
    # струм у вихід (діод) — імпульсами лише у фазі ВИКЛ
    s += text(ox - 16, 240, "iдіод", 11, INK, "end", "bold")
    b2 = 290
    s += line(ox, b2, 720, b2, GREY, 1.2)
    x = ox
    for k in range(2):
        # нуль під час ВКЛ (перша половина), імпульс під час ВИКЛ
        s += line(x, b2, x + T * 0.5, b2, COPP, 2.8)
        s += poly([(x + T * 0.5, b2), (x + T * 0.5, b2 - 30), (x + T, b2 - 18), (x + T, b2)], COPP, 2.8)
        x += T
    s += text(726, b2, "імпульсами", 11, RED, "start", "bold")
    s += text(726, b2 + 15, "(лише у фазі ВИКЛ)", 9.5, GREY, "start")
    s += text(ox + 120, b2 + 34, "вихідний конденсатор працює важче — бере весь рваний струм", 11, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 21,
              "Збереження потужності: Iвх = Iвих/(1−D) — котушка несе ВЕСЬ вхідний струм, більший за вихідний. Її добирають саме під цей струм",
              11, INK, "middle")
    save("fig-10-3-3-currents.svg", s)


# ── Рис. 10.1.3.4 — прозорість для КЗ ────────────────────────────────────────
def fig_boost_short():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Небезпека boost: вхід завжди з'єднаний з виходом", 18, INK, "middle", "bold")
    yr, yg = 180, 320
    ox = 90
    s += plus(ox, yr, 10, RED)
    s += text(ox, yr - 24, "Vвх", 13, INK, "middle", "bold")
    s += line(ox, yr + 10, ox, yg, INK, 2)
    s += line(ox, yr, ox + 30, yr, RED, 3)
    # котушка (червоний шлях)
    s += coil_h(ox + 30, ox + 160, yr, loops=4, r=11, color=RED, w=3)
    sw = ox + 210
    s += line(ox + 160, yr, sw, yr, RED, 3)
    s += circle(sw, yr, 4, INK, INK, 0)
    # ключ ВИМКНЕНИЙ
    s += line(sw, yr, sw, yr + 26, GREY, 2)
    s += line(sw, yr + 26, sw + 18, yr + 12, GREY, 2.4)
    s += line(sw, yr + 44, sw, yg, GREY, 2)
    s += text(sw, yg + 18, "ключ ВИМКНЕНО", 11, GREY, "middle", "bold")
    # діод (червоний шлях)
    s += diode_right(sw, sw + 130, yr, RED, blocked=False)
    s += text(sw + 65, yr - 16, "діод", 11, RED, "middle")
    vout = sw + 130
    s += circle(vout, yr, 4, INK, INK, 0)
    s += line(vout, yr, vout + 60, yr, RED, 3)
    # КЗ на виході
    s += line(vout + 60, yr, vout + 60, yg, RED, 3)
    s += text(vout + 60, yr - 22, "КЗ!", 15, RED, "middle", "bold")
    s += f'<path d="M {vout+48} {yr+30} L {vout+66} {yr+50} L {vout+54} {yr+50} L {vout+72} {yr+74}" fill="none" stroke="{RED}" stroke-width="2.6"/>\n'
    s += line(ox, yg, vout + 60, yg, INK, 2)
    # велика стрілка струму вздовж шляху
    s += arrow(ox + 70, yr - 30, ox + 140, yr - 30, RED, 3)
    s += text(ox + 250, yr - 34, "струм тече Vвх → котушка → діод → КЗ, попри вимкнений ключ", 11.5, RED, "start", "bold")
    s += rect(70, H - 70, W - 140, 54, "#fbe9e7", RED, 1.6, 8)
    s += text(W / 2, H - 50, "Шлях Vвх → котушка → діод → вихід існує ЗАВЖДИ — його не розриває жоден ключ контролера.", 11.5, INK, "middle", "bold")
    s += text(W / 2, H - 33, "Тому boost: не вміє Vвих < Vвх · не гасить КЗ на виході вимиканням ключа · б'є інрашем при старті (Vвих=0).", 11, INK, "middle")
    s += text(W / 2, H - 17, "Контролер тут безсилий — захист має стояти ОКРЕМО.", 11, RED, "middle", "bold")
    save("fig-10-3-4-short.svg", s)


# ── Рис. 10.1.3.5 — що з цим робити (зовнішній захист) ───────────────────────
def fig_boost_fixes():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Що з цим робити: захист додають ЗЗОВНІ", 18, INK, "middle", "bold")

    def card(x0, icon, title, body):
        out = rect(x0, 64, 270, 200, "#f6f9fc", BLUE, 1.8, 12)
        out += text(x0 + 135, 100, icon, 24, INK, "middle", "bold")
        out += text(x0 + 135, 132, title, 13, BLUE, "middle", "bold")
        for i, ln in enumerate(body):
            out += text(x0 + 135, 162 + i * 20, ln, 11, INK, "middle")
        return out

    s += card(20, "⎓→| |", "Послідовний роз'єднувач",
              ["окремий MOSFET-ключ", "після виходу — фізично", "рве шлях на КЗ і в спокої"])
    s += card(325, "⏚", "Запобіжник / ліміт",
              ["запобіжник чи eFuse", "на вході обмежує струм", "коли все інше не встигло"])
    s += card(630, "╱", "М'який старт",
              ["плавно піднімати вихід", "(ramp / NTC) проти", "інрашу при увімкненні"])
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38,
              "Boost сам по собі вихід не захистить. Багато boost-мікросхем мають вбудований роз'єднувальний MOSFET і захист від КЗ —",
              11, INK, "middle")
    s += text(W / 2, H - 22,
              "якщо його нема, послідовний ключ, запобіжник і м'який старт доводиться ставити самотужки.",
              11, INK, "middle")
    save("fig-10-3-5-fixes.svg", s)


def sw_open(x, y0, y1, color=GREY, label=None):
    """Розімкнений ключ вертикально між y0..y1."""
    ym = (y0 + y1) / 2
    out = (line(x, y0, x, ym - 12, color, 2)
           + line(x, ym + 12, x, y1, color, 2)
           + line(x, ym - 12, x + 16, ym - 2, color, 2.4)
           + circle(x, ym - 12, 2.5, color, color, 0)
           + circle(x, ym + 12, 2.5, color, color, 0))
    if label:
        out += text(x - 14, ym + 3, label, 11, color, "end", "bold")
    return out


def sw_closed(x, y0, y1, color=BLUE, label=None):
    """Замкнений ключ вертикально між y0..y1."""
    ym = (y0 + y1) / 2
    out = line(x, y0, x, y1, color, 3)
    if label:
        out += text(x - 14, ym + 3, label, 11, color, "end", "bold")
    return out


# ── Рис. 10.1.4.1 — проблема: батарея перетинає ціль ─────────────────────────
def fig_bb_problem():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Проблема: напруга батареї перетинає вихідну ціль", 18,
              INK, "middle", "bold")
    ox, oy = 90, 330
    s += arrow(ox, oy + 6, ox, 70, INK, 1.6)
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += text(ox - 8, 78, "В", 12, INK, "end", "bold")
    s += text(822, oy + 4, "розряд →", 11, GREY, "start")
    def Y(v): return oy - (v - 2.8) * 150   # 2.8..4.4 В
    for v in (3.0, 3.3, 3.7, 4.2):
        s += line(ox, Y(v), 800, Y(v), FAINT, 1)
        s += text(ox - 8, Y(v) + 4, f"{v:.1f}", 10, GREY, "end")
    # крива розряду LiPo
    disc = [(0, 4.2), (0.06, 3.95), (0.2, 3.8), (0.5, 3.65), (0.75, 3.5), (0.88, 3.3), (0.96, 3.05), (1.0, 2.9)]
    pts = [(ox + d * 700, Y(v)) for d, v in disc]
    s += poly(pts, COPP, 3)
    # ціль 3.3 В
    s += line(ox, Y(3.3), 800, Y(3.3), GREEN, 2.2, dash="7,5")
    s += text(806, Y(3.3) + 4, "ціль 3.3 В", 12, GREEN, "start", "bold")
    # точка перетину
    xc = ox + 0.88 * 700
    s += circle(xc, Y(3.3), 5, AMBER, AMBER, 0)
    s += line(xc, oy, xc, Y(3.3), GREY, 1.2, dash="4,4")
    # зони
    s += text(ox + 230, Y(3.95), "Vбат > ціль → треба ЗНИЖУВАТИ (buck)", 12, BLUE, "middle", "bold")
    s += text(xc + 60, Y(3.05), "Vбат < ціль →", 11.5, RED, "middle", "bold")
    s += text(xc + 60, Y(3.05) + 16, "ПІДВИЩУВАТИ (boost)", 11.5, RED, "middle", "bold")
    s += rect(70, H - 38, W - 140, 26, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 20,
              "Одна банка LiPo сповзає 4.2 → 3.0 В і перетинає 3.3 В: на початку треба знижувати, в кінці — підвищувати. Чистий buck чи boost не впорається",
              11, INK, "middle")
    save("fig-10-4-1-problem.svg", s)


# ── Рис. 10.1.4.2 — інвертувальний buck-boost: дві фази ──────────────────────
def fig_bb_inverting():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Інвертувальний buck-boost: котушка — єдиний місток", 18,
              INK, "middle", "bold")

    def panel(x0, title, tcol, on):
        out = rect(x0, 60, 400, 280, "none", FAINT, 2, 10)
        out += text(x0 + 200, 84, title, 13, tcol, "middle", "bold")
        yr, yg = 150, 290
        nodeX = x0 + 180
        # Vвх + ключ
        out += plus(x0 + 30, yr, 9, RED)
        out += text(x0 + 30, yr - 22, "Vвх", 12, INK, "middle", "bold")
        out += line(x0 + 30, yr + 9, x0 + 30, yg, INK, 2)
        out += line(x0 + 30, yr, x0 + 90, yr, INK, 2)
        if on:
            out += sw_closed(x0 + 110, yr - 18, yr + 18, BLUE)
            out += text(x0 + 110, yr - 26, "ВКЛ", 10.5, BLUE, "middle", "bold")
            out += line(x0 + 90, yr, x0 + 110, yr, INK, 2)
            out += line(x0 + 110, yr, nodeX, yr, INK, 2)
        else:
            out += sw_open(x0 + 110, yr - 18, yr + 18, GREY)
            out += text(x0 + 110, yr - 26, "ВИКЛ", 10.5, GREY, "middle", "bold")
            out += line(x0 + 90, yr, x0 + 110, yr, INK, 2)
        out += circle(nodeX, yr, 3.5, INK, INK, 0)
        # котушка вниз до землі
        out += coil_v(nodeX, yr + 6, yg - 6, 4, r=9, color=COPP, w=2.8, side=1)
        out += text(nodeX - 26, (yr + yg) / 2, "L", 13, COPP, "middle", "bold")
        out += line(nodeX, yg - 6, nodeX, yg, INK, 2)
        # діод до виходу (катод у nodeX)
        dy = yr
        out += diode_right(nodeX, x0 + 300, dy, (GREY if on else GREEN), blocked=on)
        # вихід (від'ємний)
        vout = x0 + 300
        out += circle(vout, yr, 3.5, INK, INK, 0)
        out += cap_v(vout, yr, yg, INK, 2.4)
        out += line(vout, yr, x0 + 350, yr, INK, 2)
        out += text(x0 + 352, yr - 6, "−Vвих", 12, BLUE, "start", "bold")
        out += line(x0 + 30, yg, vout, yg, INK, 2)
        # струм
        if on:
            out += arrow(nodeX - 14, yr + 36, nodeX - 14, yr + 70, GREEN, 2.4)
            out += text(x0 + 200, yg + 16, "котушка запасає; вхід і вихід РОЗ'ЄДНАНІ", 10.5, INK, "middle")
        else:
            out += arrow(x0 + 250, yr - 14, x0 + 215, yr - 14, GREEN, 2.4)
            out += text(x0 + 200, yg + 16, "котушка віддає у вихід — той стає ВІД'ЄМНИМ", 10.5, INK, "middle")
        return out

    s += panel(20, "ФАЗА ВКЛ", BLUE, True)
    s += panel(500, "ФАЗА ВИКЛ", GREY, False)
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 21,
              "Вхід і вихід ніколи не з'єднані напряму — усю енергію переносить лише котушка. Платою за універсальність є інверсія: вихід виходить ВІД'ЄМНИМ",
              11, INK, "middle")
    save("fig-10-4-2-inverting.svg", s)


# ── Рис. 10.1.4.3 — коефіцієнт |Vвих|/Vвх = D/(1−D) ──────────────────────────
def fig_bb_ratio():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Інвертувальний коефіцієнт: |Vвих|/Vвх = D/(1−D)", 18,
              INK, "middle", "bold")
    ox, oy = 110, 340
    s += arrow(ox, oy + 6, ox, 80, INK, 1.6)
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += text(ox - 10, 88, "|Vвих|/Vвх", 11.5, INK, "end", "bold")
    s += text(822, oy + 4, "D", 12, INK, "start", "bold")
    def Y(r): return oy - r * 52
    for r in range(0, 5):
        s += line(ox, Y(r), 800, Y(r), FAINT, 1)
        s += text(ox - 8, Y(r) + 4, f"{r}×", 10.5, GREY, "end")
    def X(d): return ox + d * 760
    for d in (0, 0.25, 0.5, 0.75):
        s += line(X(d), oy, X(d), oy + 5, GREY, 1.2)
        s += text(X(d), oy + 20, f"{d:.2f}", 10.5, GREY, "middle")
    pts = []
    d = 0.0
    while d <= 0.82:
        r = d / (1 - d)
        if r > 4.2:
            break
        pts.append((X(d), Y(r)))
        d += 0.02
    s += poly(pts, GREEN, 3)
    # межа D=0.5 (одиниця)
    s += line(X(0.5), oy, X(0.5), Y(1), GREY, 1.3, dash="5,5")
    s += line(ox, Y(1), X(0.5), Y(1), GREY, 1.3, dash="5,5")
    s += circle(X(0.5), Y(1), 4.5, AMBER, AMBER, 0)
    s += text(X(0.5) + 8, Y(1) - 8, "D=0.5 → 1× (як вхід)", 11, AMBER, "start", "bold")
    s += text(X(0.28), Y(0.35) - 6, "D<0.5: знижує", 11, BLUE, "middle", "bold")
    s += text(X(0.66), Y(2.2), "D>0.5: підвищує", 11, RED, "middle", "bold")
    s += rect(70, H - 38, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 20,
              "Одна топологія покриває і «вниз», і «вгору» — рівно те, що треба батареї, яка перетинає ціль. Ціна — від'ємна полярність виходу",
              11, INK, "middle")
    save("fig-10-4-3-ratio.svg", s)


# ── Рис. 10.1.4.4 — неінвертувальний 4-ключовий buck-boost ───────────────────
def fig_bb_fourswitch():
    W, H = 920, 460
    s = header(W, H)
    s += text(W / 2, 32, "Неінвертувальний 4-ключовий buck-boost: відповідь батареї", 18,
              INK, "middle", "bold")
    yr, yg = 150, 280
    ox = 120
    # Vвх
    s += plus(ox, yr, 9, RED)
    s += text(ox, yr - 22, "Vвх", 12, INK, "middle", "bold")
    s += line(ox, yr + 9, ox, yg, INK, 2)
    # ліве плече: S1 (Vвх→A), S2 (A→gnd)
    ax = ox + 90
    s += line(ox, yr, ax, yr, INK, 2)
    s += mosfet_box(ax - 28, yr - 46, 56, 30, "S1", "", BLUE)
    s += line(ax, yr - 16, ax, yr, INK, 2)
    s += circle(ax, yr, 3.5, INK, INK, 0)
    s += mosfet_box(ax - 28, yr + 20, 56, 30, "S2", "", BLUE)
    s += line(ax, yr, ax, yr + 20, INK, 2)
    s += line(ax, yr + 50, ax, yg, INK, 2)
    s += text(ax, yg + 16, "ліве плече", 10, GREY, "middle")
    # котушка A→B
    bx = ax + 250
    s += coil_h(ax + 14, bx - 14, yr, loops=5, r=10, color=COPP, w=2.8)
    s += text((ax + bx) / 2, yr - 18, "одна котушка", 11, COPP, "middle", "bold")
    s += circle(bx, yr, 3.5, INK, INK, 0)
    # праве плече: S3 (B→Vвих), S4 (B→gnd)
    s += mosfet_box(bx - 28, yr - 46, 56, 30, "S3", "", GREEN)
    s += line(bx, yr - 16, bx, yr, INK, 2)
    s += mosfet_box(bx - 28, yr + 20, 56, 30, "S4", "", GREEN)
    s += line(bx, yr, bx, yr + 20, INK, 2)
    s += line(bx, yr + 50, bx, yg, INK, 2)
    s += text(bx, yg + 16, "праве плече", 10, GREY, "middle")
    # вихід
    s += line(bx, yr - 46, bx, yr - 60, INK, 2)
    s += line(bx, yr - 60, bx + 120, yr - 60, INK, 2)
    s += line(bx + 120, yr - 60, bx + 120, yg, INK, 2)
    s += cap_v(bx + 120, yr - 60, yg, INK, 2.4)
    s += text(bx + 124, yr - 64, "+Vвих", 12, RED, "start", "bold")
    s += line(ox, yg, bx + 120, yg, INK, 2)
    # три режими
    modes = [
        ("Vвх > Vвих → BUCK: S3 завжди ВКЛ, S4 ВИКЛ; перемикає ліве плече", BLUE),
        ("Vвх < Vвих → BOOST: S1 завжди ВКЛ, S2 ВИКЛ; перемикає праве плече", RED),
        ("Vвх ≈ Vвих → змішаний: усі чотири працюють злагоджено", GREEN),
    ]
    for i, (m, c) in enumerate(modes):
        s += text(ox - 30, 330 + i * 22, "• " + m, 11.5, c, "start", "bold")
    s += rect(70, H - 38, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 20,
              "Чотири ключі й одна котушка: вихід ДОДАТНИЙ, тієї ж полярності. Саме це дає стабільні 3.3 В з банки, що сповзає 4.2 → 3.0 В",
              11, INK, "middle")
    save("fig-10-4-4-fourswitch.svg", s)


# ── Рис. 10.1.4.5 — SEPIC якісно ─────────────────────────────────────────────
def fig_bb_sepic():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "SEPIC: вгору/вниз, додатний вихід — і рве постійний шлях", 18,
              INK, "middle", "bold")
    yr, yg = 160, 300
    ox = 90
    s += plus(ox, yr, 9, RED)
    s += text(ox, yr - 22, "Vвх", 12, INK, "middle", "bold")
    s += line(ox, yr + 9, ox, yg, INK, 2)
    # L1
    s += coil_h(ox + 14, ox + 130, yr, loops=4, r=9, color=COPP, w=2.6)
    s += text(ox + 72, yr - 16, "L1", 11, COPP, "middle", "bold")
    nx = ox + 130
    s += circle(nx, yr, 3.5, INK, INK, 0)
    # ключ униз
    s += line(nx, yr, nx, yr + 24, BLUE, 2)
    s += mosfet_box(nx - 28, yr + 24, 56, 30, "ключ", "", BLUE)
    s += line(nx, yr + 54, nx, yg, INK, 2)
    # звʼязувальний конденсатор Cs (послідовний) — рве постійний струм
    csx = nx + 70
    s += line(nx, yr, csx - 16, yr, INK, 2)
    s += line(csx - 16, yr - 16, csx - 16, yr + 16, RED, 3.4)
    s += line(csx + 4, yr - 16, csx + 4, yr + 16, RED, 3.4)
    s += text(csx - 6, yr - 26, "Cs", 12, RED, "middle", "bold")
    s += text(csx - 6, yr - 40, "рве пост. шлях", 9.5, RED, "middle", "bold")
    ny = csx + 4
    s += line(csx + 4, yr, ny + 50, yr, INK, 2)
    midY = ny + 50
    s += circle(midY, yr, 3.5, INK, INK, 0)
    # L2 від вузла Y до землі
    s += coil_v(midY, yr + 6, yg - 6, 4, r=8, color=COPP, w=2.6, side=1)
    s += text(midY - 24, (yr + yg) / 2, "L2", 11, COPP, "middle", "bold")
    s += line(midY, yg - 6, midY, yg, INK, 2)
    # діод до виходу
    s += diode_right(midY, midY + 120, yr, GREEN, blocked=False)
    vout = midY + 120
    s += circle(vout, yr, 3.5, INK, INK, 0)
    s += cap_v(vout, yr, yg, INK, 2.4)
    s += text(vout + 6, yr - 6, "+Vвих", 12, RED, "start", "bold")
    s += line(ox, yg, vout, yg, INK, 2)
    # плюси/мінуси
    s += text(ox, yg + 40, "✓ і знижує, і підвищує   ✓ додатний вихід   ✓ Cs блокує постійний струм → справжнє вимкнення й захист від КЗ",
              11.5, GREEN, "start", "bold")
    s += text(ox, yg + 60, "✗ дві котушки + конденсатор → більше деталей і складніше налаштування",
              11.5, RED, "start", "bold")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18,
              "Послідовний Cs — головна відмінність від boost: він не пропускає постійний струм, тож прозорості для КЗ тут НЕМАЄ",
              11, INK, "middle")
    save("fig-10-4-5-sepic.svg", s)


# ── Рис. 10.1.4.6 — порівняння топологій ─────────────────────────────────────
def fig_bb_compare():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Чотири топології поряд: хто що вміє", 18, INK, "middle", "bold")
    cols = ["топологія", "знижує", "підвищує", "полярність", "рве шлях\n(захист КЗ)", "складність"]
    cx = [60, 250, 360, 470, 610, 770]
    cw = [190, 110, 110, 140, 160, 130]
    y0 = 64
    rh = 46
    # шапка
    s += rect(cx[0], y0, sum(cw), rh, "#eef3fb", BLUE, 1.6, 6)
    for i, c in enumerate(cols):
        parts = c.split("\n")
        for j, p in enumerate(parts):
            s += text(cx[i] + cw[i] / 2, y0 + 22 + j * 14 - (len(parts) - 1) * 7, p, 11.5, BLUE, "middle", "bold")
    rows = [
        ("buck", "✓", "✗", "+", "✓ (ключ рве)", "проста"),
        ("boost", "✗", "✓", "+", "✗ (прозорий!)", "проста"),
        ("інверт. buck-boost", "✓", "✓", "−", "✓", "середня"),
        ("4-ключ. buck-boost", "✓", "✓", "+", "✓", "складна"),
        ("SEPIC", "✓", "✓", "+", "✓ (Cs рве)", "складна"),
    ]
    for r, row in enumerate(rows):
        yy = y0 + rh + r * rh
        fill = "#ffffff" if r % 2 == 0 else "#f6f6f6"
        s += rect(cx[0], yy, sum(cw), rh, fill, FAINT, 1, 0)
        for i, val in enumerate(row):
            col = INK
            if i in (1, 2, 3, 4):
                col = GREEN if val.startswith("✓") or val == "+" else (RED if val.startswith("✗") or val == "−" else INK)
            w = "bold" if i == 0 else "normal"
            s += text(cx[i] + cw[i] / 2, yy + 28, val, 11.5, col, "middle", w)
    s += text(W / 2, H - 18,
              "boost — єдиний «прозорий» для КЗ; решта вміють розірвати шлях. За універсальність (вгору+вниз+додатний) платять складністю",
              11, GREY, "middle", style="italic")
    save("fig-10-4-6-compare.svg", s)


def fcap(x, ytop, ybot, vtop, vbot, color=INK, hot=False):
    """Вертикальний конденсатор із підписами напруг на пластинах."""
    ym = (ytop + ybot) / 2
    c = GREEN if hot else color
    out = (line(x, ytop, x, ym - 7, c, 2)
           + line(x - 18, ym - 7, x + 18, ym - 7, c, 3.4)
           + line(x - 18, ym + 7, x + 18, ym + 7, c, 3.4)
           + line(x, ym + 7, x, ybot, c, 2))
    out += text(x + 24, ym - 3, vtop, 11, color, "start", "bold")
    out += text(x + 24, ym + 17, vbot, 11, color, "start", "bold")
    return out


# ── Рис. 10.1.5.1 — подвоювач напруги ────────────────────────────────────────
def fig_cp_doubler():
    W, H = 920, 450
    s = header(W, H)
    s += text(W / 2, 32, "Подвоювач: летючий конденсатор заряджають, тоді ставлять НА вхід", 17.5,
              INK, "middle", "bold")

    def panel(x0, title, tcol, charge):
        out = rect(x0, 60, 400, 290, "none", FAINT, 2, 10)
        out += text(x0 + 200, 84, title, 13, tcol, "middle", "bold")
        yr, yg = 150, 300
        out += plus(x0 + 30, yr, 9, RED)
        out += text(x0 + 30, yr - 22, "Vвх", 12, INK, "middle", "bold")
        out += line(x0 + 30, yr + 9, x0 + 30, yg, INK, 2)
        cfx = x0 + 160
        if charge:
            # фаза зарядки: Cf через Vвх
            out += line(x0 + 30, yr, cfx, yr, GREEN, 2.6)
            out += fcap(cfx, yr, yr + 90, "+Vвх", "0", INK, hot=True)
            out += line(cfx, yr + 90, cfx, yg, GREEN, 2.6)
            out += line(cfx, yg, x0 + 30, yg, GREEN, 2.6)
            out += text(cfx - 70, yr + 45, "Cf", 13, COPP, "middle", "bold")
            out += text(cfx + 70, yr + 110, "заряд до Vвх", 10.5, GREEN, "middle", "bold")
            # вихід відрізаний
            out += text(x0 + 320, yr - 6, "Cвих живить", 10, GREY, "middle")
            out += text(x0 + 320, yr + 8, "лише навантаж.", 10, GREY, "middle")
        else:
            # фаза помпи: низ Cf піднято до Vвх, верх → у вихід
            out += line(x0 + 30, yr, cfx, yr + 90, GREEN, 2.6)   # Vвх → низ Cf
            out += fcap(cfx, yr - 60, yr + 30, "= 2·Vвх", "Vвх", INK, hot=True)
            out += line(cfx, yr - 60, x0 + 300, yr - 60, GREEN, 2.6)
            out += text(cfx - 70, yr - 15, "Cf", 13, COPP, "middle", "bold")
            out += text(cfx + 10, yr + 70, "низ піднято до Vвх", 10.5, GREEN, "middle", "bold")
            out += line(x0 + 30, yg, x0 + 300, yg, INK, 2)
        # вихідний конденсатор + навантаження
        ox2 = x0 + 300
        oytop = yr - 60 if not charge else yr
        out += line(ox2, oytop, ox2, yr, INK, 2) if not charge else ""
        out += circle(ox2, yr, 3.5, INK, INK, 0)
        out += cap_v(ox2, yr, yg, INK, 2.4)
        out += line(ox2, yr, ox2 + 40, yr, INK, 2)
        out += rect(ox2 + 38, yr + 12, 20, 46, "none", INK, 1.8)
        out += line(ox2 + 48, yr + 58, ox2 + 48, yg, INK, 2)
        out += text(ox2 + 4, yr - 16, "≈2·Vвх", 11.5, RED, "start", "bold")
        out += line(x0 + 30, yg, ox2, yg, INK, 2)
        return out

    s += panel(20, "ФАЗА 1: зарядка", BLUE, True)
    s += panel(500, "ФАЗА 2: помпа", GREEN, False)
    s += rect(70, H - 42, W - 140, 30, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 28, "Жодної котушки — лише конденсатори й ключі. Cf заряджається до Vвх, потім його «садять» на Vвх,", 11.5, INK, "middle")
    s += text(W / 2, H - 14, "і його верхня пластина опиняється на 2·Vвх — цей рівень і передається у вихідний конденсатор", 11.5, INK, "middle")
    save("fig-10-5-1-doubler.svg", s)


# ── Рис. 10.1.5.2 — інвертор (−Vвх) ──────────────────────────────────────────
def fig_cp_inverter():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Інвертор: зарядити до Vвх, перевернути → −Vвх", 17.5, INK, "middle", "bold")

    def panel(x0, title, tcol, charge):
        out = rect(x0, 60, 400, 280, "none", FAINT, 2, 10)
        out += text(x0 + 200, 84, title, 13, tcol, "middle", "bold")
        yr, yg = 140, 290
        out += plus(x0 + 30, yr, 9, RED)
        out += text(x0 + 30, yr - 22, "Vвх", 12, INK, "middle", "bold")
        out += line(x0 + 30, yr + 9, x0 + 30, yg, INK, 2)
        cfx = x0 + 150
        if charge:
            out += line(x0 + 30, yr, cfx, yr, GREEN, 2.6)
            out += fcap(cfx, yr, yr + 90, "+Vвх", "0", INK, hot=True)
            out += line(cfx, yr + 90, cfx, yg, GREEN, 2.6)
            out += line(cfx, yg, x0 + 30, yg, GREEN, 2.6)
            out += text(cfx - 70, yr + 45, "Cf", 13, COPP, "middle", "bold")
            out += text(cfx + 70, yr + 110, "заряд до Vвх", 10.5, GREEN, "middle", "bold")
        else:
            # перевертаємо: верх Cf → земля, низ Cf → вихід (−Vвх)
            out += line(cfx, yr, cfx, yg - 40, GREEN, 2.6)
            out += line(cfx, yg - 40, x0 + 60, yg - 40, GREEN, 2.6)
            out += line(x0 + 60, yg - 40, x0 + 60, yg, GREEN, 2.6)  # верх → земля
            out += fcap(cfx, yr, yr + 90, "0 (земля)", "−Vвх", INK, hot=True)
            out += line(cfx, yr + 90, x0 + 300, yr + 90, GREEN, 2.6)  # низ → вихід
            out += text(cfx - 70, yr + 45, "Cf", 13, COPP, "middle", "bold")
            out += text(cfx + 20, yr - 14, "перевернуто", 10.5, GREEN, "middle", "bold")
        # вихід (від'ємний)
        ox2 = x0 + 300
        oy = yr + 90 if not charge else yr + 45
        out += circle(ox2, oy, 3.5, INK, INK, 0) if not charge else ""
        out += cap_v(ox2, yr + 45, yg, INK, 2.4)
        out += text(ox2 + 6, yr + 40, "≈ −Vвх", 11.5, BLUE, "start", "bold")
        out += line(x0 + 30, yg, ox2, yg, INK, 2)
        return out

    s += panel(20, "ФАЗА 1: зарядка", BLUE, True)
    s += panel(500, "ФАЗА 2: переворот", GREEN, False)
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Зарядивши Cf до Vвх і перевернувши його (верх — на землю, низ — у вихід), дістаємо −Vвх.", 11.5, INK, "middle")
    s += text(W / 2, H - 22, "Це класична схема «−5 В із +5 В» — детальніше у вставці 🔌 про помпи ICL7660-класу.", 11, INK, "middle")
    save("fig-10-5-2-inverter.svg", s)


# ── Рис. 10.1.5.3 — заряд пакетами й струмовий ліміт ─────────────────────────
def fig_cp_current():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Струм помпи — це заряд, перенесений пакетами", 18, INK, "middle", "bold")
    s += rect(70, 50, W - 140, 32, "#f6f6f6", GREY, 1.4, 8)
    s += text(W / 2, 71, "Iвих = Q · f = Cf · ΔV · f      (заряд пакета × скільки пакетів за секунду)", 14,
              INK, "middle", "bold")
    # конвеєр пакетів від входу до виходу
    s += text(150, 130, "ВХІД", 13, INK, "middle", "bold")
    s += text(750, 130, "ВИХІД", 13, INK, "middle", "bold")
    y = 200
    s += rect(110, y - 30, 90, 80, "#eef3fb", BLUE, 2, 8)
    s += rect(700, y - 30, 90, 80, "#fbe9e7", RED, 2, 8)
    for i in range(4):
        x = 230 + i * 110
        s += rect(x, y - 16, 50, 32, "#eef8ef", GREEN, 2, 6)
        s += text(x + 25, y + 5, "Q", 14, GREEN, "middle", "bold")
        s += arrow(x - 18, y, x - 2, y, INK, 2)
    s += arrow(672, y, 698, y, INK, 2)
    s += text(W / 2, y + 60, "кожен цикл переносить пакет Q = Cf·ΔV; за секунду таких пакетів f", 12, GREY, "middle")
    s += rect(70, H - 56, W - 140, 40, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 38, "Звідси головне обмеження помпи: більше струму → треба більший Cf або вища частота f.", 11.5, INK, "middle")
    s += text(W / 2, H - 22, "Тому charge pump — для МАЛИХ струмів (міліампери–сотні мА), не для силового живлення.", 11.5, INK, "middle")
    save("fig-10-5-3-current.svg", s)


# ── Рис. 10.1.5.4 — вихідний опір, просадка, ККД ─────────────────────────────
def fig_cp_droop():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Помпа = ідеальне джерело n·Vвх із вихідним опором", 18, INK, "middle", "bold")
    # ліворуч — еквівалентна схема
    s += rect(40, 60, 380, 300, "none", FAINT, 2, 10)
    s += text(230, 84, "Еквівалент", 13, INK, "middle", "bold")
    yr, yg = 180, 320
    s += circle(110, yr, 26, "none", INK, 2.4)
    s += text(110, yr - 4, "n·Vвх", 11.5, INK, "middle", "bold")
    s += text(110, yr + 12, "ідеал", 9, GREY, "middle")
    s += line(110, yr - 26, 110, 130, INK, 2)
    s += line(110, 130, 200, 130, INK, 2)
    # Rout
    s += rect(200, 116, 90, 28, "#fbe9e7", RED, 2, 5)
    s += text(245, 134, "Rвих≈1/(Cf·f)", 10.5, RED, "middle", "bold")
    s += line(290, 130, 350, 130, INK, 2)
    s += line(350, 130, 350, yg, INK, 2)
    s += cap_v(350, 130, yg, INK, 2.2)
    s += text(355, 120, "Vвих", 11.5, RED, "start", "bold")
    s += line(110, yr + 26, 110, yg, INK, 2)
    s += line(110, yg, 350, yg, INK, 2)
    s += text(230, yg + 22, "Vвих = n·Vвх − Iвих·Rвих", 12.5, INK, "middle", "bold")
    # праворуч — просадка й ККД
    s += rect(460, 60, 420, 300, "none", FAINT, 2, 10)
    s += text(670, 84, "Просадка під навантаженням", 13, INK, "middle", "bold")
    ox, oy = 510, 300
    s += arrow(ox, oy + 6, ox, 110, INK, 1.5)
    s += arrow(ox, oy, 850, oy, INK, 1.5)
    s += text(ox - 8, 118, "Vвих", 11, INK, "end", "bold")
    s += text(852, oy + 4, "Iвих", 11, INK, "start", "bold")
    s += line(ox, 130, 850, 130, FAINT, 1.2)
    s += text(ox + 6, 124, "n·Vвх (ідеал, без струму)", 10.5, GREY, "start")
    s += poly([(ox, 130), (840, 250)], RED, 3)
    s += text(700, 210, "падає з Iвих", 11, RED, "middle", "bold")
    s += text(670, oy + 26, "ККД ≈ Vвих / (n·Vвх): далеко від ідеалу — палить, як лінійний",
              11, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 21,
              "Помпа ефективна, лише коли вихід близький до n·Vвх. Хочете проміжну напругу — зайве палиться, як у лінійного стабілізатора (§7.4.1)",
              11, INK, "middle")
    save("fig-10-5-4-droop.svg", s)


# ── Рис. 10.1.5.5 — драбина коефіцієнтів і де брати ──────────────────────────
def fig_cp_ratios():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Що вміє помпа і коли її брати", 18, INK, "middle", "bold")
    s += text(W / 2, 64, "Досяжні коефіцієнти (більше конденсаторів → більше варіантів):", 12.5, INK, "middle", "bold")
    chips = [("×½", BLUE), ("×1", GREY), ("×1.5", BLUE), ("×2", RED), ("×3", RED), ("−1", BLUE)]
    n = len(chips)
    for i, (lab, c) in enumerate(chips):
        x = 110 + i * 120
        s += rect(x, 84, 96, 44, "#f6f9fc", c, 2, 10)
        s += text(x + 48, 112, lab, 16, c, "middle", "bold")
    # коли брати / коли ні
    s += rect(40, 156, 410, 180, "#eef8ef", GREEN, 1.8, 10)
    s += text(245, 182, "✓ Брати, коли:", 13, GREEN, "middle", "bold")
    for i, ln in enumerate([
        "немає місця/бажання на котушку (мала, тиха, дешева)",
        "струм малий: мА — сотні мА",
        "зсув ЖК-дисплея, від'ємна шина для ОП,",
        "напруга програмування flash, bootstrap-затвор",
    ]):
        s += text(60, 210 + i * 26, "• " + ln, 11, INK, "start")
    s += rect(470, 156, 410, 180, "#fbe9e7", RED, 1.8, 10)
    s += text(675, 182, "✗ Не брати, коли:", 13, RED, "middle", "bold")
    for i, ln in enumerate([
        "потрібен помітний струм / потужність",
        "потрібен високий ККД на проміжній напрузі",
        "→ тут виграють перетворювачі з котушкою",
        "  (buck / boost / buck-boost із попередніх тем)",
    ]):
        s += text(490, 210 + i * 26, "• " + ln, 11, INK, "start")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18,
              "Помпа — нішевий інструмент для малих допоміжних шин без котушки; силову роботу лишають котушковим топологіям",
              11, INK, "middle")
    save("fig-10-5-5-ratios.svg", s)


def xfmr(cx, ytop, ybot, hot_prim=False, hot_sec=False, gap=True):
    """Трансформатор/спарена котушка: дві обмотки, осердя, точки фази (флайбек — на протилежних кінцях)."""
    out = line(cx - 4, ytop, cx - 4, ybot, GREY, 2.6)
    out += line(cx + 4, ytop, cx + 4, ybot, GREY, 2.6)
    if gap:  # повітряний зазор
        ym = (ytop + ybot) / 2
        out += line(cx - 8, ym, cx + 8, ym, "#ffffff", 5)
        out += text(cx, ym + 4, "⟂", 9, GREY, "middle")
    out += coil_v(cx - 24, ytop, ybot, 5, r=11, color=(GREEN if hot_prim else COPP), w=2.6, side=-1)
    out += coil_v(cx + 24, ytop, ybot, 5, r=11, color=(GREEN if hot_sec else COPP), w=2.6, side=1)
    out += circle(cx - 36, ytop + 10, 3, INK, INK, 0)   # точка первинної — згори
    out += circle(cx + 36, ybot - 10, 3, INK, INK, 0)   # точка вторинної — знизу (флайбек)
    return out


# ── Рис. 10.1.6.1 — гальванічна розв'язка ────────────────────────────────────
def fig_fb_isolation():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Гальванічна розв'язка: дві сторони без спільного дроту", 18,
              INK, "middle", "bold")
    # бар'єр
    bx = W / 2
    s += line(bx, 60, bx, 350, RED, 2, dash="8,6")
    s += text(bx, 76, "БАР'ЄР", 12, RED, "middle", "bold")
    s += text(bx, 92, "ІЗОЛЯЦІЇ", 12, RED, "middle", "bold")
    # первинна сторона
    s += rect(40, 110, 360, 200, "#fbe9e7", RED, 1.6, 10)
    s += text(220, 136, "ПЕРВИННА сторона", 13.5, RED, "middle", "bold")
    s += text(220, 158, "небезпечна: напр., мережа 230 В", 11.5, INK, "middle")
    s += text(220, 250, "своя «земля»", 11, GREY, "middle")
    s += line(150, 268, 290, 268, INK, 2)
    s += line(165, 276, 275, 276, INK, 2)
    s += line(180, 284, 260, 284, INK, 2)
    # вторинна сторона
    s += rect(520, 110, 360, 200, "#eef8ef", GREEN, 1.6, 10)
    s += text(700, 136, "ВТОРИННА сторона", 13.5, GREEN, "middle", "bold")
    s += text(700, 158, "безпечна: 5 В, можна торкатися", 11.5, INK, "middle")
    s += text(700, 250, "своя «земля» (інша!)", 11, GREY, "middle")
    s += line(630, 268, 770, 268, INK, 2)
    s += line(645, 276, 755, 276, INK, 2)
    s += line(660, 284, 740, 284, INK, 2)
    # лише магнітний зв'язок крізь бар'єр
    s += xfmr(bx, 150, 240, gap=True)
    s += text(bx, 262, "лише магнітний зв'язок", 10.5, COPP, "middle", "bold")
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Між сторонами немає електричного дроту — енергію передає лише магнітне поле в трансформаторі.", 11.5, INK, "middle")
    s += text(W / 2, H - 22, "Навіщо: безпека (торкатися 5 В від мережі 230 В), розрив контурів землі, різні опорні рівні.", 11.5, INK, "middle")
    save("fig-10-6-1-isolation.svg", s)


# ── Рис. 10.1.6.2 — дві фази flyback (запасти / відпустити) ──────────────────
def fig_fb_phases():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Flyback: запасти в осерді, тоді «відпустити» у вторинну", 18,
              INK, "middle", "bold")

    def panel(x0, title, tcol, on):
        out = rect(x0, 58, 400, 300, "none", FAINT, 2, 10)
        out += text(x0 + 200, 82, title, 13, tcol, "middle", "bold")
        yr, yg = 150, 300
        cx = x0 + 200
        # первинна сторона
        out += plus(x0 + 30, yr, 9, RED)
        out += text(x0 + 30, yr - 22, "Vвх", 11.5, INK, "middle", "bold")
        out += line(x0 + 30, yr + 9, x0 + 30, yg, INK, 2)
        out += line(x0 + 30, yr, cx - 24, yr, GREEN if on else INK, 2.4)
        out += line(cx - 24, yg, x0 + 30, yg, INK, 2)
        # ключ на первинній (низ обмотки до землі)
        if on:
            out += sw_closed(cx - 24, yr + 92, yg, BLUE)
            out += text(cx - 70, yg - 18, "ключ ВКЛ", 10, BLUE, "middle", "bold")
        else:
            out += sw_open(cx - 24, yr + 92, yg, GREY)
            out += text(cx - 70, yg - 18, "ключ ВИКЛ", 10, GREY, "middle", "bold")
        # трансформатор
        out += xfmr(cx, yr, yr + 92, hot_prim=on, hot_sec=not on, gap=True)
        # вторинна сторона: діод + вихід
        out += diode_right(cx + 24, cx + 110, yr, (GREY if on else GREEN), blocked=on)
        out += circle(cx + 110, yr, 3.5, INK, INK, 0)
        out += cap_v(cx + 110, yr, yr + 92, INK, 2.2)
        out += line(cx + 110, yr, cx + 150, yr, INK, 2)
        out += line(cx + 24, yr + 92, cx + 110, yr + 92, INK, 2)
        out += text(cx + 120, yr - 6, "Vвих", 11.5, RED, "start", "bold")
        # підпис фази
        if on:
            out += text(x0 + 200, yg + 26, "осердя НАБИРАЄ енергію; діод закритий (точки протилежні)", 10, INK, "middle")
        else:
            out += text(x0 + 200, yg + 26, "енергія «відлітає» у вторинну → діод відкритий → у вихід", 10, INK, "middle")
        return out

    s += panel(20, "ФАЗА ВКЛ", BLUE, True)
    s += panel(500, "ФАЗА ВИКЛ (flyback)", GREEN, False)
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 28, "Це не звичайний трансформатор (що передає миттєво), а спарена котушка (§2.2.6): осердя ЗАПАСАЄ енергію у фазі ВКЛ", 11, INK, "middle")
    s += text(W / 2, H - 14, "і ВІДДАЄ її у вторинну у фазі ВИКЛ. По суті — buck-boost, розрізаний на дві обмотки заради ізоляції", 11, INK, "middle")
    save("fig-10-6-2-phases.svg", s)


# ── Рис. 10.1.6.3 — важіль коефіцієнта витків ───────────────────────────────
def fig_fb_turns():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Два важелі напруги: витки й шпаруватість", 18, INK, "middle", "bold")
    s += rect(60, 50, W - 120, 32, "#f6f6f6", GREY, 1.4, 8)
    s += text(W / 2, 71, "Vвих = Vвх · (Ns/Np) · D/(1−D)", 15, INK, "middle", "bold")
    # важіль 1: витки
    s += rect(60, 100, 360, 130, "#eef3fb", BLUE, 1.8, 10)
    s += text(240, 126, "Важіль 1: коефіцієнт витків Ns/Np", 12.5, BLUE, "middle", "bold")
    s += text(240, 150, "груба шкала — задається конструкцією", 11, INK, "middle")
    s += text(240, 174, "мало витків вторинної → велике зниження", 11, INK, "middle")
    s += text(240, 196, "(325 В мережі → 5 В одним трансформатором)", 10.5, GREY, "middle")
    # важіль 2: D
    s += rect(480, 100, 360, 130, "#eef8ef", GREEN, 1.8, 10)
    s += text(660, 126, "Важіль 2: шпаруватість D", 12.5, GREEN, "middle", "bold")
    s += text(660, 150, "тонке підстроювання — задається контролером", 11, INK, "middle")
    s += text(660, 174, "тримає вихід сталим, поки вхід плаває", 11, INK, "middle")
    s += text(660, 196, "(той самий зворотний звʼязок, що скрізь)", 10.5, GREY, "middle")
    # приклад
    s += rect(120, 260, 660, 90, "#fbf7ec", AMBER, 1.6, 10)
    s += text(W / 2, 286, "Приклад: мережа 230 В ~ → випрямлено ≈ 325 В →  Ns/Np ≈ 1/16, D ≈ 0.3  →  ≈ 5 В", 12.5, INK, "middle", "bold")
    s += text(W / 2, 310, "Витки роблять основне зниження ×16, шпаруватість лише підправляє й стабілізує.", 11, INK, "middle")
    s += text(W / 2, 332, "Це перевага flyback: майже будь-яке відношення напруг — підбором витків.", 11, INK, "middle")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18, "Коефіцієнт витків — додатковий важіль, якого не мали buck/boost: ним беруть будь-яке відношення, навіть величезне", 11, INK, "middle")
    save("fig-10-6-3-turns.svg", s)


# ── Рис. 10.1.6.4 — зворотний зв'язок крізь бар'єр ───────────────────────────
def fig_fb_feedback():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Зворотний зв'язок теж мусить перетнути бар'єр — не дротом", 18,
              INK, "middle", "bold")
    bx = W / 2
    s += line(bx, 60, bx, 330, RED, 2, dash="8,6")
    s += text(bx, 76, "бар'єр", 11, RED, "middle", "bold")
    # первинна: контролер
    s += rect(70, 110, 300, 90, "#fbe9e7", RED, 1.6, 10)
    s += text(220, 140, "КОНТРОЛЕР", 13, RED, "middle", "bold")
    s += text(220, 162, "(на первинній стороні)", 11, INK, "middle")
    s += text(220, 184, "крутить шпаруватість ключа", 10.5, GREY, "middle")
    # вторинна: вихід + опорна
    s += rect(550, 110, 300, 90, "#eef8ef", GREEN, 1.6, 10)
    s += text(700, 140, "ВИХІД 5 В + еталон", 13, GREEN, "middle", "bold")
    s += text(700, 162, "(на вторинній стороні)", 11, INK, "middle")
    s += text(700, 184, "міряє, чи тримається напруга", 10.5, GREY, "middle")
    # оптопара через бар'єр
    s += rect(bx - 70, 230, 140, 80, "#fff7e6", AMBER, 1.8, 10)
    s += text(bx, 252, "ОПТОПАРА", 11.5, AMBER, "middle", "bold")
    # світлодіод (secondary) → фототранзистор (primary): світло через бар'єр
    s += text(bx + 36, 280, "LED", 9.5, GREEN, "middle")
    s += text(bx - 36, 280, "фото", 9.5, RED, "middle")
    s += arrow(bx + 22, 292, bx - 22, 292, AMBER, 2.4)
    s += text(bx, 304, "світло", 9, AMBER, "middle", "bold")
    # звʼязки
    s += arrow(700, 200, bx + 30, 234, GREEN, 2)
    s += arrow(bx - 30, 270, 300, 250, RED, 2)
    s += line(220, 200, 220, 250, RED, 2)
    s += line(220, 250, 290, 250, RED, 2)
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Дротом з'єднати вихід із контролером не можна — це зруйнувало б ізоляцію. Сигнал переносить СВІТЛО в оптопарі", 11.5, INK, "middle")
    s += text(W / 2, H - 22, "(або окрема допоміжна обмотка). Так регулювання перетинає бар'єр, а електричної з'єднаності не виникає.", 11, INK, "middle")
    save("fig-10-6-4-feedback.svg", s)


# ── Рис. 10.1.6.5 — мережевий адаптер цілком ─────────────────────────────────
def fig_fb_adapter():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Мережевий адаптер: 230 В ~ → ізольовані 5 В (кожна зарядка)", 17.5,
              INK, "middle", "bold")
    y = 170
    # блоки ланцюга
    blocks = [
        (60, "230 В ~", "розетка", RED),
        (200, "міст +\nконденс.", "≈325 В =", RED),
        (370, "FLYBACK", "ключ+транс", BLUE),
        (560, "діод +\nконденс.", "5 В", GREEN),
        (710, "5 В", "USB-вихід", GREEN),
    ]
    for x, t, sub, c in blocks:
        s += rect(x, y - 36, 110, 72, "#f6f9fc", c, 1.8, 8)
        for j, ln in enumerate(t.split("\n")):
            s += text(x + 55, y - 6 + j * 16 - (t.count(chr(10))) * 8, ln, 12, c, "middle", "bold")
        s += text(x + 55, y + 52, sub, 10, GREY, "middle")
    for x in (170, 310, 480, 670):
        s += arrow(x, y, x + 30, y, INK, 2)
    # бар'єр через flyback + оптопара
    bx = 480
    s += line(bx, 70, bx, 300, RED, 2, dash="8,6")
    s += text(bx, 86, "бар'єр", 10.5, RED, "middle", "bold")
    s += text(220, 250, "ПЕРВИННА (небезпечно)", 11.5, RED, "middle", "bold")
    s += text(700, 250, "ВТОРИННА (безпечно)", 11.5, GREEN, "middle", "bold")
    # оптопара зворотного звʼязку
    s += rect(415, 280, 130, 40, "#fff7e6", AMBER, 1.6, 8)
    s += text(480, 304, "оптопара (ЗЗ)", 10.5, AMBER, "middle", "bold")
    s += arrow(605, 206, 545, 290, GREEN, 1.8)
    s += arrow(415, 300, 360, 240, RED, 1.8)
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Мережу випрямляють у ≈325 В, flyback переганяє їх крізь трансформатор в ізольовані 5 В, оптопара тримає рівень.", 11, INK, "middle")
    s += text(W / 2, H - 22, "Це нутрощі майже кожного зарядного «кубика». Детальний розбір плати — у вставці 🔌 «Мережевий адаптер зсередини».", 11, INK, "middle")
    save("fig-10-6-5-adapter.svg", s)


# ── Рис. 10.1.6.6 — викид витоку й снабер ────────────────────────────────────
def fig_fb_snubber():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Платня за неідеальний зв'язок: викид індуктивності витоку", 18,
              INK, "middle", "bold")
    ox, oy = 110, 300
    s += arrow(ox, oy + 6, ox, 80, INK, 1.6)
    s += arrow(ox, oy, 840, oy, INK, 1.6)
    s += text(ox - 8, 88, "напруга", 11, INK, "end", "bold")
    s += text(842, oy + 4, "t", 12, INK, "start", "bold")
    s += text(ox + 4, oy + 20, "на стоці ключа", 10.5, GREY, "start")
    # рівень Vвх
    s += line(ox, 240, 820, 240, FAINT, 1.2)
    s += text(826, 244, "Vвх", 10.5, GREY, "start")
    # відбита напруга (плато)
    s += line(ox, 180, 820, 180, FAINT, 1.2)
    s += text(826, 184, "Vвх+відбита", 10.5, GREY, "start")
    # форма без снабера: викид
    s += poly([(ox, 240), (300, 240), (300, 110), (340, 175), (560, 180), (560, 240), (820, 240)], RED, 3)
    s += text(330, 100, "ВИКИД витоку!", 12, RED, "start", "bold")
    s += text(330, 118, "може пробити ключ", 10, RED, "start")
    # форма зі снабером: підрізано
    s += poly([(ox, 242), (300, 242), (300, 168), (560, 178), (560, 242), (820, 242)], GREEN, 2.4, dash="6,4")
    s += text(590, 165, "зі снабером — підрізано", 11, GREEN, "start", "bold")
    s += rect(70, H - 70, W - 140, 54, "#fbf7ec", AMBER, 1.6, 8)
    s += text(W / 2, H - 50, "Обмотки зчеплені не на 100%: частина енергії сидить в індуктивності витоку. При вимиканні ключа їй нема куди подітися —", 11, INK, "middle")
    s += text(W / 2, H - 34, "і вона б'є викидом напруги на стоку ключа, здатним його пробити.", 11, INK, "middle")
    s += text(W / 2, H - 18, "Рятунок — снабер (RCD-ланка чи TVS), що поглинає цей викид. Без нього flyback живе недовго.", 11, RED, "middle", "bold")
    save("fig-10-6-6-snubber.svg", s)


def diamond(cx, cy, w, h, label, color=INK, sub=None):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
    out = polygon(pts, "#fbf7ec")
    out += poly(pts + [pts[0]], color, 2)
    out += text(cx, cy + (0 if sub else 4), label, 11.5, color, "middle", "bold")
    if sub:
        out += text(cx, cy + 16, sub, 9.5, GREY, "middle")
    return out


def topobox(x, y, w, h, label, color, sub=None):
    out = rect(x, y, w, h, "#eef8ef", color, 2, 8)
    out += text(x + w / 2, y + (h / 2 + 2 if not sub else h / 2 - 5), label, 12.5, color, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + h / 2 + 13, sub, 9.5, INK, "middle")
    return out


# ── Рис. 10.1.7.1 — дерево рішень ────────────────────────────────────────────
def fig_sel_tree():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "Дерево вибору топології: п'ять питань до рішення", 18, INK, "middle", "bold")
    # старт
    s += rect(400, 50, 140, 34, "#eef3fb", BLUE, 2, 8)
    s += text(470, 72, "Потрібен DC-DC", 12, BLUE, "middle", "bold")
    s += arrow(470, 84, 470, 104, INK, 1.8)
    # Q1 ізоляція
    s += diamond(470, 132, 230, 56, "Потрібна ізоляція?", INK, "(мережа / безпека)")
    s += arrow(585, 132, 770, 132, GREEN, 2)
    s += text(660, 122, "ТАК", 11, GREEN, "middle", "bold")
    s += topobox(770, 108, 150, 52, "FLYBACK", RED, "<100 Вт; більше — forward/міст")
    s += arrow(470, 160, 470, 192, INK, 1.8)
    s += text(490, 182, "НІ", 11, RED, "start", "bold")
    # Q2 напрямок
    s += rect(360, 192, 220, 40, "#fff", INK, 2, 8)
    s += text(470, 217, "Vвих відносно Vвх?", 12.5, INK, "middle", "bold")
    # 4 гілки
    outs = [
        (90, "завжди нижче", "BUCK", BLUE, "(синхронний — ККД)"),
        (290, "завжди вище", "BOOST", RED, "(стереже КЗ!)"),
        (500, "гуляє навколо", "BUCK-BOOST", GREEN, "(4-ключовий, +вихід)"),
        (720, "потрібна −", "ІНВЕРТ. b-b", BLUE, "(від'ємний вихід)"),
    ]
    for x, cond, topo, c, sub in outs:
        s += arrow(470, 232, x + 75, 286, GREY, 1.6)
        s += text(x + 75, 270, cond, 10, GREY, "middle", style="italic")
        s += topobox(x, 290, 150, 50, topo, c, sub)
    # charge pump — окремий випадок
    s += rect(60, 380, 820, 56, "#fff7e6", AMBER, 1.8, 10)
    s += text(110, 404, "АБО:", 13, AMBER, "start", "bold")
    s += text(470, 400, "малий струм (мА) + проста кратність (×2, −1, ½) + без котушки", 12, INK, "middle", "bold")
    s += text(470, 420, "→ CHARGE PUMP (на конденсаторах)", 12, AMBER, "middle", "bold")
    # примітка про захист
    s += rect(60, 452, 820, 56, "#fbe9e7", RED, 1.6, 10)
    s += text(470, 476, "⚠ boost не захищає власний вихід від КЗ: треба захист — додай послідовний роз'єднувач", 11.5, INK, "middle")
    s += text(470, 496, "або візьми SEPIC (він рве постійний шлях). Для мережі ізоляція — НЕ опція, а вимога безпеки.", 11.5, INK, "middle")
    save("fig-10-7-1-tree.svg", s)


# ── Рис. 10.1.7.2 — карта потужність × перетворення ──────────────────────────
def fig_sel_map():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Де живе кожна топологія: потужність × тип перетворення", 18, INK, "middle", "bold")
    ox, oy = 130, 360
    s += arrow(ox, oy, 860, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 70, INK, 1.6)
    s += text(862, oy + 4, "потужність →", 11, INK, "start", "bold")
    s += text(ox - 10, 66, "перетворення", 11, INK, "end", "bold")
    # x-підписи (лог потужність)
    for i, lb in enumerate(["мВт", "Вт", "10 Вт", "100 Вт", "кВт"]):
        x = ox + 60 + i * 160
        s += line(x, oy, x, oy + 5, GREY, 1)
        s += text(x, oy + 20, lb, 10, GREY, "middle")
    # y-смуги
    bands = [("підвищення", 110), ("≈ вхід / вниз-вгору", 175), ("зниження", 240), ("інверсія", 305)]
    for lb, y in bands:
        s += line(ox, y, 850, y, FAINT, 1)
        s += text(ox - 8, y + 4, lb, 9.5, GREY, "end")

    def region(x, y, w, h, lab, c):
        s2 = rect(x, y, w, h, "#ffffff", c, 2, 8)
        s2 += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c}" fill-opacity="0.10"/>\n'
        s2 += text(x + w / 2, y + h / 2 + 4, lab, 11.5, c, "middle", "bold")
        return s2
    s += region(ox + 20, 285, 150, 40, "charge pump", AMBER)      # інверсія/малі
    s += region(ox + 20, 90, 150, 40, "charge pump ×2", AMBER)
    s += region(ox + 180, 222, 330, 36, "BUCK (синхр.)", BLUE)
    s += region(ox + 180, 92, 280, 36, "BOOST", RED)
    s += region(ox + 180, 157, 300, 36, "BUCK-BOOST", GREEN)
    s += region(ox + 300, 285, 230, 36, "інверт. b-b", BLUE)
    s += region(ox + 520, 130, 200, 150, "FLYBACK", "#9b59b6")
    s += region(ox + 600, 90, 130, 230, "forward/міст", "#7d3cb5")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 21,
              "Помпа — лівий нижній кут (мала потужність); котушкові buck/boost/buck-boost — середина; ізольовані — праворуч, від flyback до мостів зі зростанням потужності",
              10.5, INK, "middle")
    save("fig-10-7-2-map.svg", s)


# ── Рис. 10.1.7.3 — впізнати топологію на платі ──────────────────────────────
def fig_sel_recognize():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Як упізнати топологію на платі", 18, INK, "middle", "bold")
    rows = [
        ("котушка + 1 діод Шотткі", "асинхронний buck або boost", BLUE),
        ("котушка + 2 MOSFET (чи power-stage)", "СИНХРОННИЙ buck/boost (ККД)", GREEN),
        ("2 котушки + конденсатор між ними", "SEPIC (вгору/вниз, +вихід)", GREEN),
        ("трансформатор + оптопара", "ІЗОЛЬОВАНИЙ (flyback) — мережа/безпека", RED),
        ("лише 2–3 однакові конденсатори, без котушки", "charge pump (мала допоміжна шина)", AMBER),
        ("велика котушка + контролер + щільні C", "силова шина — головний перетворювач", BLUE),
    ]
    y = 70
    for i, (cue, verdict, c) in enumerate(rows):
        yy = y + i * 56
        s += rect(50, yy, 400, 46, "#f6f9fc", GREY, 1.4, 8)
        s += text(70, yy + 28, cue, 11.5, INK, "start", "bold")
        s += arrow(456, yy + 23, 496, yy + 23, INK, 2)
        s += rect(500, yy, 370, 46, "#eef8ef", c, 1.8, 8)
        s += text(520, yy + 28, verdict, 11.5, c, "start", "bold")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18, "Найгаласливіший куток (котушка + ключі + щільні конденсатори) — це вузол перемикання; його тримають компактним", 11, INK, "middle")
    save("fig-10-7-3-recognize.svg", s)


# ── Рис. 10.1.7.4 — вторинні рішення (після вибору сім'ї) ────────────────────
def fig_sel_secondary():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Сім'ю обрано — лишаються вторинні осі вибору", 18, INK, "middle", "bold")
    axes = [
        ("Випрямляч", "діод (асинхр.)", "MOSFET (синхр.)", "дешево / простіше", "ККД на струмі"),
        ("Легке навантаж.", "forced-PWM", "авто-PFM", "чисті завади", "автономність у сні"),
        ("Реалізація", "дискрет", "інтегр. модуль", "гнучко / дешевше", "просто / швидко"),
        ("Частота", "нижча", "вища", "менші втрати", "менші котушка й C"),
    ]
    y = 64
    for i, (name, a, b, ta, tb) in enumerate(axes):
        yy = y + i * 84
        s += text(60, yy + 28, name, 12.5, INK, "start", "bold")
        s += rect(200, yy, 260, 48, "#eef3fb", BLUE, 1.8, 8)
        s += text(330, yy + 21, a, 12, BLUE, "middle", "bold")
        s += text(330, yy + 38, ta, 9.5, GREY, "middle")
        s += text(480, yy + 28, "⇄", 18, INK, "middle", "bold")
        s += rect(500, yy, 260, 48, "#eef8ef", GREEN, 1.8, 8)
        s += text(630, yy + 21, b, 12, GREEN, "middle", "bold")
        s += text(630, yy + 38, tb, 9.5, GREY, "middle")
        s += text(800, yy + 28, "← компроміс →", 9.5, GREY, "middle", style="italic")
    save("fig-10-7-4-secondary.svg", s)


# ── Рис. 10.1.7.5 — порівняння компромісів ───────────────────────────────────
def fig_sel_tradeoffs():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Порівняння за компромісами (більше ● — більше виражено)", 17.5,
              INK, "middle", "bold")
    cols = ["топологія", "простота", "ціна↓", "ККД", "потужн.", "розмір↓", "тиша"]
    cx = [60, 250, 360, 460, 560, 670, 790]
    rows = [
        ("buck (синхр.)", 4, 4, 5, 4, 4, 3),
        ("boost", 4, 4, 4, 3, 4, 2),
        ("buck-boost (4кл.)", 2, 2, 4, 3, 3, 3),
        ("charge pump", 5, 5, 2, 1, 5, 4),
        ("flyback", 2, 3, 3, 4, 2, 2),
    ]
    y0 = 64
    s += rect(40, y0, 850, 34, "#eef3fb", BLUE, 1.6, 6)
    for i, c in enumerate(cols):
        s += text(cx[i] + (0 if i == 0 else 24), y0 + 22, c, 11.5, BLUE, "start" if i == 0 else "middle", "bold")
    for r, row in enumerate(rows):
        yy = y0 + 40 + r * 50
        s += rect(40, yy, 850, 44, "#ffffff" if r % 2 == 0 else "#f6f6f6", FAINT, 1, 0)
        s += text(cx[0], yy + 27, row[0], 11.5, INK, "start", "bold")
        for i in range(1, 7):
            val = row[i]
            for d in range(5):
                fill = INK if d < val else "#dcdcdc"
                s += circle(cx[i] + 24 - 36 + d * 9, yy + 23, 3.2, fill, fill, 0)
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18, "Помпа виграє в простоті/розмірі, програє в потужності/ККД; flyback дає ізоляцію ціною складності; buck — універсальна робоча конячка", 10.5, INK, "middle")
    save("fig-10-7-5-tradeoffs.svg", s)


# ── Рис. 10.1.7.6 — типові пастки ────────────────────────────────────────────
def fig_sel_pitfalls():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Типові пастки вибору — чого не робити", 18, INK, "middle", "bold")
    pits = [
        ("boost «захистить» вихід", "ні — він прозорий для КЗ; додай роз'єднувач"),
        ("charge pump на реальний струм", "ні — це мА; для потужності бери котушку"),
        ("мережа без ізоляції", "смертельно — для 230 В лише flyback/ізольовані"),
        ("котушка boost під вихідний струм", "ні — рахуй під ВХІДНИЙ (більший) струм"),
        ("flyback без снабера", "ключ згорить від викиду витоку"),
        ("помпа на проміжну напругу", "палить, як лінійний; узгодь кратність"),
    ]
    for i, (bad, fix) in enumerate(pits):
        col = i % 2
        row = i // 2
        x = 50 + col * 440
        y = 70 + row * 108
        s += rect(x, y, 410, 92, "#fbe9e7", RED, 1.6, 10)
        s += text(x + 20, y + 30, "✗ " + bad, 12.5, RED, "start", "bold")
        s += line(x + 20, y + 44, x + 390, y + 44, FAINT, 1)
        s += text(x + 20, y + 66, fix, 11, INK, "start")
    save("fig-10-7-6-pitfalls.svg", s)


def fig_m7_cascade():
    """Вставка 🧮 до 10.1.7 — множення ККД каскадів проти одного перетворювача."""
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "ККД ланцюга = добуток ККД каскадів (не сума!)", 18, INK, "middle", "bold")

    def node(x, y, pct, color):
        s2 = circle(x, y, 26, "#ffffff", color, 2.4)
        s2 += text(x, y + 5, pct, 13, color, "middle", "bold")
        return s2

    def stage(x, y, eta, lab):
        s2 = rect(x, y - 20, 90, 40, "#eef3fb", BLUE, 1.8, 7)
        s2 += text(x + 45, y - 1, lab, 11, BLUE, "middle", "bold")
        s2 += text(x + 45, y + 14, f"η={eta}", 10, INK, "middle")
        return s2

    # рядок 1 — каскад
    y1 = 130
    s += text(70, y1 - 60, "Каскад buck + LDO:", 13, INK, "start", "bold")
    s += node(110, y1, "100%", INK)
    s += line(136, y1, 200, y1, INK, 2)
    s += stage(200, y1, "0.92", "buck→5В")
    s += line(290, y1, 360, y1, INK, 2)
    s += node(390, y1, "92%", GREEN)
    s += line(416, y1, 480, y1, INK, 2)
    s += stage(480, y1, "0.66", "LDO→3.3В")
    s += line(570, y1, 640, y1, INK, 2)
    s += node(672, y1, "61%", RED)
    # втрати в тепло
    s += arrow(245, y1 + 22, 245, y1 + 50, RED, 2)
    s += text(245, y1 + 64, "−8% тепло", 9.5, RED, "middle")
    s += arrow(525, y1 + 22, 525, y1 + 50, RED, 2)
    s += text(525, y1 + 64, "−31% тепло (LDO палить різницю!)", 9.5, RED, "middle")
    s += text(770, y1 + 5, "→ 61%", 14, RED, "start", "bold")
    s += text(770, y1 + 22, "0.92×0.66", 10, GREY, "start")

    # рядок 2 — один перетворювач
    y2 = 300
    s += text(70, y2 - 50, "Один buck:", 13, INK, "start", "bold")
    s += node(110, y2, "100%", INK)
    s += line(136, y2, 260, y2, INK, 2)
    s += stage(260, y2, "0.90", "buck 12→3.3В")
    s += line(350, y2, 640, y2, INK, 2)
    s += node(672, y2, "90%", GREEN)
    s += arrow(305, y2 + 22, 305, y2 + 42, RED, 2)
    s += text(305, y2 + 56, "−10% тепло", 9.5, RED, "middle")
    s += text(770, y2 + 5, "→ 90%", 14, GREEN, "start", "bold")

    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "Один добрий перетворювач (90%) б'є каскад buck+LDO (61%): зайвий каскад — особливо лінійний — з'їдає десятки відсотків", 10.5, INK, "middle")
    save("fig-10-7m1-cascade.svg", s)


def fig_c6_adapter():
    """Вставка 🔌 до 10.1.6 — мережевий адаптер: блок-схема плати з бар'єром і небезпекою."""
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 30, "Мережевий адаптер зсередини: карта плати й де небезпечно", 17.5,
              INK, "middle", "bold")
    bx = 590   # бар'єр
    # зони
    s += f'<rect x="40" y="58" width="{bx-50}" height="300" rx="10" fill="{RED}" fill-opacity="0.06"/>\n'
    s += f'<rect x="{bx+10}" y="58" width="{880-bx}" height="300" rx="10" fill="{GREEN}" fill-opacity="0.07"/>\n'
    s += line(bx, 64, bx, 350, RED, 2, dash="8,6")
    s += text(bx, 80, "бар'єр", 11, RED, "middle", "bold")
    s += text(170, 78, "ПЕРВИННА — під мережею (СМЕРТЕЛЬНО)", 12, RED, "middle", "bold")
    s += text(745, 78, "ВТОРИННА — безпечна", 12, GREEN, "middle", "bold")
    y = 175
    blocks = [
        (70, "~230 В", "розетка", RED),
        (185, "запоб.+NTC", "захист/інраш", RED),
        (300, "EMI-фільтр", "X-cap, дросель", RED),
        (415, "міст+bulk", "≈325 В =", RED),
        (525, "flyback чип", "+ трансф.", BLUE),
        (660, "діод+Cвих", "випрямляч", GREEN),
        (775, "5 В", "USB", GREEN),
    ]
    for x, t, sub, c in blocks:
        s += rect(x, y - 30, 100, 60, "#ffffff", c, 1.8, 7)
        s += text(x + 50, y - 4, t, 11.5, c, "middle", "bold")
        s += text(x + 50, y + 14, sub, 9, GREY, "middle")
    for x in (170, 285, 400, 510, 645, 760):
        s += arrow(x, y, x + 14, y, INK, 2)
    # снабер на первинній
    s += rect(500, 90, 80, 30, "#fbf7ec", AMBER, 1.5, 6)
    s += text(540, 110, "снабер", 10, AMBER, "middle", "bold")
    s += line(540, 120, 555, 145, AMBER, 1.6)
    # bulk тримає заряд — попередження
    s += text(465, y + 48, "⚠ bulk тримає", 9.5, RED, "middle", "bold")
    s += text(465, y + 61, "заряд після", 9.5, RED, "middle")
    s += text(465, y + 74, "вимкнення!", 9.5, RED, "middle")
    # оптопара через бар'єр
    s += rect(bx - 60, 250, 120, 36, "#fff7e6", AMBER, 1.6, 8)
    s += text(bx, 272, "оптопара (ЗЗ)", 10.5, AMBER, "middle", "bold")
    s += arrow(700, 206, bx + 35, 252, GREEN, 1.6)
    s += arrow(bx - 35, 270, 560, 206, RED, 1.6)
    # Y-конденсатор через бар'єр
    s += rect(bx - 40, 305, 80, 30, "#eef3fb", BLUE, 1.4, 6)
    s += text(bx, 325, "Y-cap", 10, BLUE, "middle", "bold")
    s += text(bx, 348, "(тихо «зшиває» землі, малий витік)", 9, GREY, "middle")
    s += rect(70, H - 40, W - 140, 28, "#fbe9e7", RED, 1.5, 8)
    s += text(W / 2, H - 23, "НІКОЛИ не міряйте первинну під напругою «масовою» землею осцилографа: вона під мережею. І розряджайте bulk перед роботою.", 11, INK, "middle")
    save("fig-10-6c1-adapter.svg", s)


def fig_c5_icl7660():
    """Вставка 🔌 до 10.1.5 — помпа ICL7660-класу: розпіновка й обвʼязка."""
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 30, "Помпа ICL7660-класу: −5 В із +5 В трьома конденсаторами", 17.5,
              INK, "middle", "bold")
    vcc, gnd = 86, 360
    # рейки
    s += line(120, vcc, 760, vcc, RED, 2)
    s += text(120, vcc - 8, "+5 В", 12, RED, "start", "bold")
    s += line(120, gnd, 760, gnd, INK, 2)
    s += text(120, gnd + 18, "земля", 11, GREY, "start")
    # чип
    cx0, cy0, cw, ch = 380, 150, 180, 160
    s += rect(cx0, cy0, cw, ch, "#eef3fb", BLUE, 2, 6)
    s += text(cx0 + cw / 2, cy0 + ch / 2 - 6, "ICL7660-", 13, BLUE, "middle", "bold")
    s += text(cx0 + cw / 2, cy0 + ch / 2 + 12, "клас", 13, BLUE, "middle", "bold")
    s += f'<path d="M {cx0+cw/2-10} {cy0} A 10 10 0 0 0 {cx0+cw/2+10} {cy0}" fill="none" stroke="{BLUE}" stroke-width="1.5"/>\n'
    # піни ліворуч (1-4) і праворуч (8-5)
    lp = [(1, "NC"), (2, "CAP+"), (3, "GND"), (4, "CAP−")]
    rp = [(8, "V+"), (7, "OSC"), (6, "LV"), (5, "VOUT")]
    ys = [cy0 + 26 + i * 36 for i in range(4)]
    for (num, name), y in zip(lp, ys):
        s += line(cx0, y, cx0 - 18, y, INK, 2)
        s += circle(cx0 - 18, y, 2.5, INK, INK, 0)
        s += text(cx0 + 6, y + 4, f"{num} {name}", 10, INK, "start", "bold")
    for (num, name), y in zip(rp, ys):
        s += line(cx0 + cw, y, cx0 + cw + 18, y, INK, 2)
        s += circle(cx0 + cw + 18, y, 2.5, INK, INK, 0)
        s += text(cx0 + cw - 6, y + 4, f"{name} {num}", 10, INK, "end", "bold")
    y1, y2, y3, y4 = ys  # CAP+ at y2, GND at y3, CAP− at y4; V+ y1, OSC y2, LV y3, VOUT y4
    # V+ (pin8) → +5 В
    s += line(cx0 + cw + 18, y1, 700, y1, INK, 2)
    s += line(700, y1, 700, vcc, INK, 2)
    # GND (pin3) → земля
    s += line(cx0 - 18, y3, 300, y3, INK, 2)
    s += line(300, y3, 300, gnd, INK, 2)
    # летючий конденсатор C1 між CAP+ (y2) і CAP− (y4)
    fx = cx0 - 70
    s += line(cx0 - 18, y2, fx, y2, COPP, 2)
    s += line(cx0 - 18, y4, fx, y4, COPP, 2)
    s += line(fx, y2, fx, (y2 + y4) / 2 - 8, COPP, 2)
    s += line(fx - 16, (y2 + y4) / 2 - 8, fx + 16, (y2 + y4) / 2 - 8, COPP, 3.2)
    s += line(fx - 16, (y2 + y4) / 2 + 8, fx + 16, (y2 + y4) / 2 + 8, COPP, 3.2)
    s += line(fx, (y2 + y4) / 2 + 8, fx, y4, COPP, 2)
    s += text(fx - 24, (y2 + y4) / 2 + 4, "C1", 12, COPP, "end", "bold")
    s += text(fx, y4 + 22, "летючий", 10, GREY, "middle")
    # LV (pin6, y3) → земля
    s += line(cx0 + cw + 18, y3, 660, y3, INK, 2)
    s += line(660, y3, 660, gnd, INK, 2)
    s += text(672, y3 + 4, "LV→GND", 9, GREY, "start")
    # VOUT (pin5, y4) → −5 В + резервуарний C2
    s += line(cx0 + cw + 18, y4, 720, y4, BLUE, 2.4)
    s += circle(720, y4, 3, INK, INK, 0)
    s += line(720, y4, 720, (y4 + gnd) / 2 - 8, BLUE, 2)
    s += line(720 - 16, (y4 + gnd) / 2 - 8, 720 + 16, (y4 + gnd) / 2 - 8, BLUE, 3.2)
    s += line(720 - 16, (y4 + gnd) / 2 + 8, 720 + 16, (y4 + gnd) / 2 + 8, BLUE, 3.2)
    s += line(720, (y4 + gnd) / 2 + 8, 720, gnd, BLUE, 2)
    s += text(744, (y4 + gnd) / 2 + 4, "C2", 12, BLUE, "start", "bold")
    s += line(720, y4, 800, y4, BLUE, 2.4)
    s += text(806, y4 + 4, "−5 В", 13, BLUE, "start", "bold")
    # вхідний розвʼязувальний C3
    s += line(170, vcc, 170, (vcc + gnd) / 2 - 8, GREY, 2)
    s += line(170 - 14, (vcc + gnd) / 2 - 8, 170 + 14, (vcc + gnd) / 2 - 8, GREY, 3)
    s += line(170 - 14, (vcc + gnd) / 2 + 8, 170 + 14, (vcc + gnd) / 2 + 8, GREY, 3)
    s += line(170, (vcc + gnd) / 2 + 8, 170, gnd, GREY, 2)
    s += text(146, (vcc + gnd) / 2 + 4, "C3", 11, GREY, "end", "bold")
    s += text(170, gnd + 18, "розвʼязка входу", 9.5, GREY, "middle")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 17, "Уся схема: чип + летючий C1 + резервуарний C2 (+ розвʼязка C3). Жодного коду — подав +5 В, на VOUT зʼявилось ≈ −5 В", 10.5, INK, "middle")
    save("fig-10-5c1-icl7660.svg", s)


def fig_c2_loss():
    """Вставка 🔌 до 10.1.2 — втрати діод проти нижнього MOSFET у числах."""
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 30, "Втрати на нижньому елементі: діод проти MOSFET", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "приклад: buck 12 В → 1.2 В, 10 А (D=0.1 → нижній елемент працює 90% циклу)",
              11.5, GREY, "middle", style="italic")
    base = 320
    s += line(120, base, 720, base, INK, 1.6)
    sc = 64   # px на ват

    def bar(x, watts, color, top1, top2, formula, val):
        h = watts * sc
        s2 = rect(x, base - h, 120, h, "#ffffff", color, 2, 4)
        s2 += f'<rect x="{x}" y="{base-h:.0f}" width="120" height="{h:.0f}" rx="4" fill="{color}" fill-opacity="0.16"/>\n'
        s2 += text(x + 60, base - h - 12, val, 14, color, "middle", "bold")
        s2 += text(x + 60, base + 22, top1, 12.5, color, "middle", "bold")
        s2 += text(x + 60, base + 40, top2, 10.5, GREY, "middle")
        s2 += text(x + 60, base + 58, formula, 10, INK, "middle")
        return s2

    s += bar(190, 3.6, RED, "Асинхронний", "(діод Шотткі)", "Vf·I·(1−D) = 0.4·10·0.9", "3.6 Вт")
    s += bar(530, 0.5, GREEN, "Синхронний", "(нижній MOSFET)", "I²·Rds·(1−D) = 100·0.005·0.9", "0.45 Вт")
    # стрілка-порівняння
    s += text(420, base - 130, "×7", 22, INK, "middle", "bold")
    s += text(420, base - 105, "менше", 11, GREY, "middle")
    # ефективність
    s += rect(150, 92, 200, 40, "#fbe9e7", RED, 1.6, 8)
    s += text(250, 117, "ККД ≈ 77 %", 14, RED, "middle", "bold")
    s += rect(500, 92, 200, 40, "#eef8ef", GREEN, 1.6, 8)
    s += text(600, 117, "ККД ≈ 96 %", 14, GREEN, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 17, "При низькому Vвих і великому струмі діод палить помітну частку потужності; MOSFET з Rds(on) кілька мОм — майже ні", 10.5, INK, "middle")
    save("fig-10-2c1-loss.svg", s)


def fig_m2_tradeoff():
    """Вставка 🧮 до 10.1.2 — компроміс пульсації ΔI проти індуктивності L."""
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 32, "Вибір L: пульсація ΔI ∝ 1/L — шукаємо вікно 30–40 %", 18, INK, "middle", "bold")
    ox, oy = 110, 340
    s += arrow(ox, oy + 6, ox, 80, INK, 1.6)
    s += arrow(ox, oy, 800, oy, INK, 1.6)
    s += text(ox - 10, 88, "ΔI, % Imax", 11, INK, "end", "bold")
    s += text(802, oy + 4, "L", 12, INK, "start", "bold")
    def Y(p): return oy - p * 4.6        # відсотки
    def X(l): return ox + l * 62          # мкГ
    for p in (20, 30, 40, 60, 80):
        s += line(ox, Y(p), 780, Y(p), FAINT, 1)
        s += text(ox - 8, Y(p) + 4, f"{p}%", 9.5, GREY, "end")
    # цільова смуга 30–40%
    s += f'<rect x="{ox}" y="{Y(40)}" width="670" height="{Y(30)-Y(40):.0f}" fill="{GREEN}" fill-opacity="0.13"/>\n'
    s += text(720, (Y(30) + Y(40)) / 2 + 4, "ціль", 11, GREEN, "middle", "bold")
    # крива ΔI = k/L (k підібрано так, щоб 35% при L≈6.8)
    k = 35 * 6.8
    pts = []
    l = 1.6
    while l <= 11.5:
        p = k / l
        if p <= 86:
            pts.append((X(l), Y(p)))
        l += 0.2
    s += poly(pts, RED, 3)
    # вікно L (де крива в смузі)
    l_hi = k / 30     # L при 30%
    l_lo = k / 40     # L при 40%
    s += line(X(l_lo), oy, X(l_lo), Y(40), GREY, 1.3, dash="4,4")
    s += line(X(l_hi), oy, X(l_hi), Y(30), GREY, 1.3, dash="4,4")
    s += text((X(l_lo) + X(l_hi)) / 2, oy + 20, f"L ≈ {l_lo:.1f}–{l_hi:.1f} мкГ", 11, INK, "middle", "bold")
    # підписи країв
    s += text(X(2.4), Y(72), "малий L:", 11, RED, "start", "bold")
    s += text(X(2.4), Y(72) + 16, "велика пульсація →", 10, INK, "start")
    s += text(X(2.4), Y(72) + 30, "насичення, RMS-втрати,", 10, INK, "start")
    s += text(X(2.4), Y(72) + 44, "велике Cвих", 10, INK, "start")
    s += text(X(8.6), Y(26), "великий L:", 11, BLUE, "start", "bold")
    s += text(X(8.6), Y(26) + 16, "громіздко, дорого,", 10, INK, "start")
    s += text(X(8.6), Y(26) + 30, "високий DCR, млявіша", 10, INK, "start")
    s += text(X(8.6), Y(26) + 44, "реакція", 10, INK, "start")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 17, "30–40 % — компроміс: дрібнішу пульсацію оплачуєш об'ємом котушки, більшу — піковим струмом і втратами", 10.5, INK, "middle")
    save("fig-10-2m1-tradeoff.svg", s)


def fig_m1_area():
    """Вставка 🧮 до 10.1.1 — формальне інтегрування напруги котушки в buck."""
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 32, "Інтеграл напруги котушки за період buck = 0", 18, INK, "middle", "bold")
    x0, x1 = 110, 560
    T = x1 - x0
    D = 0.31
    pu = x0 + T * D
    base = 200
    top = base - 88      # +(Vвх−Vвих), високий
    bot = base + 40      # −Vвих, низький
    s += text(x0 - 18, base - 84, "Vл", 13, INK, "end", "bold")
    s += arrow(x0, base + 60, x0, base - 100, INK, 1.6)
    s += arrow(x0, base, x1 + 30, base, INK, 1.6)
    s += text(x1 + 32, base + 4, "t", 12, INK, "start", "bold")
    # площі
    s += polygon([(x0, base), (x0, top), (pu, top), (pu, base)], "#bfe6c6")
    s += polygon([(pu, base), (pu, bot), (x1, bot), (x1, base)], "#f1c4c0")
    s += poly([(x0, top), (pu, top), (pu, bot), (x1, bot), (x1, base)], INK, 2.6)
    s += text((x0 + pu) / 2, top - 8, "+(Vвх−Vвих)", 12, GREEN, "middle", "bold")
    s += text((pu + x1) / 2, bot + 16, "−Vвих", 12, RED, "middle", "bold")
    # ширини
    s += line(x0, base + 52, pu, base + 52, GREEN, 1.4)
    s += text((x0 + pu) / 2, base + 66, "D·T", 11, GREEN, "middle", "bold")
    s += line(pu, base + 52, x1, base + 52, RED, 1.4)
    s += text((pu + x1) / 2, base + 66, "(1−D)·T", 11, RED, "middle", "bold")
    # алгебра праворуч
    bx = 600
    s += rect(bx, 96, 244, 210, "#f6f6f6", GREY, 1.4, 10)
    lines = [
        "∫₀ᵀ Vл dt = 0",
        "",
        "(Vвх−Vвих)·D·T",
        "   − Vвих·(1−D)·T = 0",
        "",
        "(Vвх−Vвих)·D = Vвих·(1−D)",
        "Vвх·D = Vвих",
        "",
        "⇒  D = Vвих / Vвх",
    ]
    for i, ln in enumerate(lines):
        w = "bold" if (i == 0 or ln.startswith("⇒")) else "normal"
        col = GREEN if ln.startswith("⇒") else INK
        s += text(bx + 16, 124 + i * 21, ln, 12.5, col, "start", w)
    s += text(W / 2, H - 18, "Зелена площа = червона площа: середня напруга на котушці нульова — звідси й коефіцієнт",
              11, GREY, "middle", style="italic")
    save("fig-10-1m1-area.svg", s)


if __name__ == "__main__":
    # історія до розділу
    fig_timeline()
    fig_vibrator()
    # вставка 🧮 до 10.1.1
    fig_m1_area()
    # вставка 🧮 до 10.1.2
    fig_m2_tradeoff()
    # вставка 🔌 до 10.1.2
    fig_c2_loss()
    # вставка 🔌 до 10.1.5
    fig_c5_icl7660()
    # вставка 🔌 до 10.1.6
    fig_c6_adapter()
    # вставка 🧮 до 10.1.7
    fig_m7_cascade()
    # тема 10.1.1
    fig_core()
    fig_inductor()
    fig_phases()
    fig_voltsec()
    fig_runaway()
    fig_map()
    # тема 10.1.2
    fig_ripple()
    fig_ccm_dcm()
    fig_vripple()
    fig_sync()
    fig_deadtime()
    fig_lightload()
    fig_efficiency()
    # тема 10.1.3
    fig_boost_phases()
    fig_boost_ratio()
    fig_boost_currents()
    fig_boost_short()
    fig_boost_fixes()
    # тема 10.1.4
    fig_bb_problem()
    fig_bb_inverting()
    fig_bb_ratio()
    fig_bb_fourswitch()
    fig_bb_sepic()
    fig_bb_compare()
    # тема 10.1.5
    fig_cp_doubler()
    fig_cp_inverter()
    fig_cp_current()
    fig_cp_droop()
    fig_cp_ratios()
    # тема 10.1.6
    fig_fb_isolation()
    fig_fb_phases()
    fig_fb_turns()
    fig_fb_feedback()
    fig_fb_adapter()
    fig_fb_snubber()
    # тема 10.1.7
    fig_sel_tree()
    fig_sel_map()
    fig_sel_recognize()
    fig_sel_secondary()
    fig_sel_tradeoffs()
    fig_sel_pitfalls()
    print("done r01 figures")
