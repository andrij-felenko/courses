# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 42 — «Радіозв'язок системи: керування, телеметрія, MAVLink» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; борт/повітря синє, земля зелена, протокол/повідомлення бурштин,
команда червона. Підписи посекційно; історія — секція 0 (42.0.N).
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
AMBER = "#b08900"
SPARK = "#e8b53a"
METAL = "#9a9aa0"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fbf3df"
LGREY = "#f3f3f3"
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
        f'  <marker id="aAmb" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", AMBER: "aAmb"}


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


def _poly(pts, color, w):
    return ('<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            + f'" fill="none" stroke="{color}" stroke-width="{w}"/>\n')


def sine(x0, y0, length, amp, periods, color, w=2.4, phase=0.0):
    pts = []
    n = max(60, int(length / 2))
    for i in range(n + 1):
        t = i / n
        x = x0 + t * length
        y = y0 - amp * math.sin(2 * math.pi * periods * t + phase)
        pts.append((x, y))
    return _poly(pts, color, w)


def _drone(cx, cy, sc=1.0, col=BLUE):
    s = line(cx - 26 * sc, cy - 14 * sc, cx + 26 * sc, cy + 14 * sc, col, 3)
    s += line(cx - 26 * sc, cy + 14 * sc, cx + 26 * sc, cy - 14 * sc, col, 3)
    for dx, dy in [(-26, -14), (26, -14), (-26, 14), (26, 14)]:
        s += circle(cx + dx * sc, cy + dy * sc, 9 * sc, "none", col, 2)
    s += rect(cx - 8 * sc, cy - 6 * sc, 16 * sc, 12 * sc, LBLUE, col, 1.6, 2)
    return s


def _tower(cx, base, h, col=GREEN):
    s = line(cx, base, cx, base - h, METAL, 3)
    s += line(cx - 8, base - h - 4, cx + 8, base - h - 4, METAL, 3)
    for r in (10, 18, 26):
        s += f'<path d="M {cx-r},{base-h-10} A {r} {r} 0 0 1 {cx+r},{base-h-10}" fill="none" stroke="{col}" stroke-width="1.3"/>\n'
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ============================================================================
#  Історія до Розділу 42 — MAVLink і відкриті дрони (секція 0)
# ============================================================================

# ── Рис. 42.0.1 — таймлайн ───────────────────────────────────────────────────
def figh_timeline():
    W, H = 960, 640
    s = header(W, H)
    s += text(W / 2, 36, "Як аспірант із Цюриха дав дронам спільну мову", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "MAVLink став стандартом не наказом, а тому, що відкриту спільноту його підхопила",
              12, GREY, "middle", style="italic")
    spine = 300
    top, bot = 92, H - 24
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("2007", "DIY Drones + ArduCopter", "Кріс Андерсон засновує спільноту; Жорді Муньйос пише автопілот на Arduino", "comm"),
        ("2008", "Проєкт у ETH Zürich", "Лоренц Маєр будує дрон із комп'ютерним зором для змагань MAV", "px4"),
        ("2009", "MAVLink і ArduPilot 1.0", "Маєр випускає MAVLink; Муньйос — ArduPilot 1.0. Дві гілки, одна мова", "px4"),
        ("2011", "PX4 і Pixhawk", "Перебудова з нуля: народжуються PX4 і відкрите залізо Pixhawk (ETH + 3DR)", "px4"),
        ("2011–12", "Тридж і pymavlink", "Ендрю Тридджелл вибухово розвиває ArduPilot, пише pymavlink і MAVProxy", "comm"),
        ("2014", "Dronecode Foundation", "MAVLink, PX4, QGroundControl — під дахом Linux Foundation", "comm"),
        ("сьогодні", "MAVLink — лінгва франка", "Нею «розмовляють» PX4, ArduPilot і тисячі апаратів по всьому світу", "win"),
    ]
    n = len(nodes)
    for i, (yr, who, q, kind) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        if kind == "win":
            s += circle(spine, y, 9, "#fff", GREEN, 3)
            s += circle(spine, y, 4, GREEN, GREEN, 0)
            wc = GREEN
        elif kind == "px4":
            s += circle(spine, y, 7.5, "#fff", BLUE, 2.8)
            wc = BLUE
        else:
            s += rect(spine - 7, y - 7, 14, 14, "#fff", AMBER, 2.4, 3)
            wc = AMBER
        s += text(spine - 22, y + 5, yr, 12, GREY, "end", "bold")
        s += text(spine + 26, y - 2, who, 14.5, wc, "start", "bold")
        s += text(spine + 26, y + 18, q, 10.8, INK, "start", style="italic")
    save("fig-42-0-1-timeline.svg", s)


# ── Рис. 42.0.2 — проблема: спільна мова ─────────────────────────────────────
def figh_problem():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Проблема: дрон і земля мусять багато про що «домовлятися»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "висота, GPS, батарея, команди — десятки видів повідомлень через вузький шумний радіоканал",
              11, GREY, "middle", style="italic")
    s += _drone(180, 170, 1.3, BLUE)
    s += text(180, 230, "борт (дрон)", 11, BLUE, "middle", "bold")
    s += _tower(740, 250, 70, GREEN)
    s += text(740, 270, "земля (станція)", 11, GREEN, "middle", "bold")
    msgs = ["висота й кути", "координати GPS", "заряд батареї", "режим польоту", "→ команди керування"]
    y = 120
    for m in msgs:
        col = RED if m.startswith("→") else AMBER
        s += text(460, y, m, 11, col, "middle", "bold")
        y += 26
    s += arrow(230, 160, 700, 160, AMBER, 1.6, "5 4")
    s += arrow(700, 185, 230, 185, RED, 1.6, "5 4")
    s += rect(60, 300, W - 120, 50, LAMB, AMBER, 1.4, 9)
    s += text(W / 2, 324, "Потрібна спільна МОВА: компактна (мало байтів), надійна (з перевіркою), стандартна (зрозуміла всім).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 343, "Саме таку мову — MAVLink — і створив Лоренц Маєр зі своєю командою.", 10.5, GREY, "middle", style="italic")
    save("fig-42-0-2-problem.svg", s)


# ── Рис. 42.0.3 — ідея MAVLink ───────────────────────────────────────────────
def figh_mavlink_idea():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Ідея MAVLink: крихітні пакети з контролем", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожне повідомлення — короткий кадр відомого типу з контрольною сумою (це з Розділу 35!)",
              11, GREY, "middle", style="italic")
    fields = [("STX", BLUE, 60), ("довж.", GREY, 70), ("№", GREY, 50), ("sys/comp", GREY, 100),
              ("ID", AMBER, 60), ("дані (payload)", LAMB, 240), ("CRC", GREEN, 70)]
    x = 90
    y = 130
    for nm, col, w_ in fields:
        fill = col if col in (LAMB,) else ("#eef2fb" if col == BLUE else ("#eef6ef" if col == GREEN else ("#fbf3df" if col == AMBER else "#f4f4f4")))
        s += rect(x, y, w_, 56, fill, (col if col != LAMB else AMBER), 1.8)
        s += text(x + w_ / 2, y + 33, nm, 10.5, INK, "middle", "bold")
        x += w_
    s += text(95, y - 12, "старт", 9, BLUE, "start")
    s += text(x - 35, y - 12, "перевірка", 9, GREEN, "middle")
    s += text(360, y + 84, "тип повідомлення (heartbeat, attitude, GPS…) → приймач знає, як читати дані",
              10.5, INK, "middle", "bold")
    s += rect(60, 286, W - 120, 44, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 310, "Кадр + ID + CRC — точно ті самі ідеї, що ми будували для UART у Розділі 35. MAVLink — їх зрілий нащадок.",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 326, "Детально розберемо структуру в §42.5.", 9.5, GREY, "middle", style="italic")
    save("fig-42-0-3-mavlink-idea.svg", s)


# ── Рис. 42.0.4 — «випадковий» стандарт ──────────────────────────────────────
def figh_by_accident():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Несподіванка: світовий стандарт виник «між іншим»", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "Маєр хотів зовсім іншого — а інструмент, зроблений мимохідь, став головним спадком",
              11, GREY, "middle", style="italic")
    # головна мета
    s += rect(60, 92, 380, 200, "#fbfbfb", BLUE, 1.8, 10)
    s += text(250, 120, "ГОЛОВНА мета", 12.5, BLUE, "middle", "bold")
    s += text(250, 150, "дрон із комп'ютерним зором,", 11, INK, "middle")
    s += text(250, 170, "що сам літає в приміщенні", 11, INK, "middle")
    s += text(250, 196, "(для змагань MAV)", 10, GREY, "middle", style="italic")
    s += _drone(250, 240, 1.1, BLUE)
    # побічний інструмент
    s += rect(480, 92, 380, 200, "#fbfbfb", GREEN, 1.8, 10)
    s += text(670, 120, "побічні інструменти", 12, GREEN, "middle", "bold")
    s += text(670, 148, "MAVLink і QGroundControl —", 11, INK, "middle")
    s += text(670, 168, "зроблені, ЩОБ підтримати", 11, INK, "middle")
    s += text(670, 188, "головний проєкт", 11, INK, "middle")
    s += text(670, 224, "★ саме вони стали", 11.5, GREEN, "middle", "bold")
    s += text(670, 244, "світовим стандартом", 11.5, GREEN, "middle", "bold")
    s += arrow(445, 192, 475, 192, INK, 2.2)
    s += text(W / 2, 322, "Урок: відкриті стандарти часто народжуються не як «продукт», а як зручний інструмент, що його підхопили всі.",
              10.5, INK, "middle", "bold")
    save("fig-42-0-4-by-accident.svg", s)


# ── Рис. 42.0.5 — колективний винахід ────────────────────────────────────────
def figh_collective():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 34, "Відкриті дрони — праця спільноти, а не одного героя", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "дві паралельні гілки автопілотів, одна спільна мова — і десятки людей за кожною",
              11.5, GREY, "middle", style="italic")
    people = [
        ("Лоренц Маєр", "Швейцарія, ETH", "MAVLink, PX4, Pixhawk, QGC", BLUE),
        ("Жорді Муньйос", "3DR", "ArduCopter / ArduPilot 1.0", GREEN),
        ("Кріс Андерсон", "DIY Drones / 3DR", "спільнота, що все почала", AMBER),
        ("Ендрю Тридджелл", "ArduPilot", "pymavlink, MAVProxy (§42.7)", RED),
    ]
    cw, ch = 215, 110
    x0, y0 = 28, 90
    for i, (nm, org, what, col) in enumerate(people):
        cx = x0 + i * (cw + 8)
        s += rect(cx, y0, cw, ch, "#fbfbfb", col, 1.8, 10)
        s += text(cx + cw / 2, y0 + 28, nm, 12.5, col, "middle", "bold")
        s += text(cx + cw / 2, y0 + 47, org, 9.5, GREY, "middle", style="italic")
        words = what.split()
        ln, yy = "", y0 + 70
        for wd in words:
            if len(ln) + len(wd) > 24:
                s += text(cx + cw / 2, yy, ln.strip(), 9.6, INK, "middle")
                ln, yy = "", yy + 15
            ln += wd + " "
        s += text(cx + cw / 2, yy, ln.strip(), 9.6, INK, "middle")
    # дві гілки → одна мова
    s += rect(120, 230, 300, 56, LBLUE, BLUE, 1.5, 9)
    s += text(270, 254, "PX4 (Маєр)", 11.5, BLUE, "middle", "bold")
    s += text(270, 274, "гілка ETH Zürich", 9.5, GREY, "middle")
    s += rect(540, 230, 300, 56, LGRN, GREEN, 1.5, 9)
    s += text(690, 254, "ArduPilot (Муньйос, Тридж)", 11, GREEN, "middle", "bold")
    s += text(690, 274, "гілка DIY Drones / 3DR", 9.5, GREY, "middle")
    s += arrow(420, 258, 480, 300, INK, 2)
    s += arrow(540, 258, 480, 300, INK, 2)
    s += rect(360, 300, 240, 40, LAMB, AMBER, 1.6, 8)
    s += text(480, 325, "спільна мова: MAVLink", 12, AMBER, "middle", "bold")
    s += text(W / 2, 372, "MAVLink став універсальним саме тому, що його прийняли ОБИДВІ гілки — це сила відкритого стандарту.",
              10.5, INK, "middle", "bold")
    save("fig-42-0-5-collective.svg", s)


# ── Рис. 42.0.6 — сила відкритості ───────────────────────────────────────────
def figh_open():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Чому «відкрите» змінило все", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "відкритий протокол + відкрите залізо + відкритий код = будь-хто може будувати й поєднувати",
              11, GREY, "middle", style="italic")
    cards = [
        ("📡", "Відкритий протокол", "MAVLink опублікований — будь-який пристрій може «заговорити» з будь-яким.", AMBER),
        ("🔧", "Відкрите залізо й код", "Pixhawk і PX4/ArduPilot вільні — їх вивчають, повторюють, удосконалюють.", BLUE),
        ("🌍", "Ціла екосистема", "Хобі, наука, сільське госп., картографія, рятування — і доступ для всіх.", GREEN),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 86, 270, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, ico, 23, INK, "middle")
        s += text(x + 135, 154, title, 12.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 184
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
        x += 290
    save("fig-42-0-6-open.svg", s)


# ── Рис. 42.0.7 — що з цього лишилось ────────────────────────────────────────
def figh_legacy():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Що лишилось — і куди веде нас розділ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "MAVLink — спільна мова дронів; цей розділ навчить нею користуватися",
              11.5, GREY, "middle", style="italic")
    steps = [
        ("§42.5", "структура пакета MAVLink", "heartbeat, ID, CRC", BLUE),
        ("§42.6", "читати потік і слати команди", "розмова з автопілотом", GREEN),
        ("§42.7", "pymavlink — автоматизація", "місток до бортового комп'ютера", AMBER),
    ]
    x = 50
    for tag, title, sub, col in steps:
        s += rect(x, 90, 270, 150, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 122, tag, 13, col, "middle", "bold")
        words = title.split()
        ln, yy = "", 150
        for wd in words:
            if len(ln) + len(wd) > 22:
                s += text(x + 135, yy, ln.strip(), 11.5, INK, "middle", "bold")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 11.5, INK, "middle", "bold")
        s += text(x + 135, 216, sub, 9.8, GREY, "middle", style="italic")
        x += 290
    s += text(W / 2, 300, "Спадок аспірантського проєкту: відкритий стандарт, яким сьогодні «розмовляють» дрони всього світу.",
              10.5, INK, "middle", "bold")
    save("fig-42-0-7-legacy.svg", s)


# ============================================================================
#  §42.1 — Канали керування й телеметрії (дві ролі)
# ============================================================================

# ── Рис. 42.1.1 — дві (три) радіолінії ───────────────────────────────────────
def fig11_two_links():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 34, "Радіозв'язок дрона — це не одна лінія, а кілька ролей", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "керування «віжки» вгору, телеметрія «панель приладів» вниз, інколи ще й відео",
              11, GREY, "middle", style="italic")
    s += _drone(200, 170, 1.5, BLUE)
    s += text(200, 235, "борт (дрон)", 11, BLUE, "middle", "bold")
    s += _tower(760, 270, 80, GREEN)
    s += text(760, 290, "пульт / станція", 11, GREEN, "middle", "bold")
    # керування (вгору)
    s += arrow(700, 130, 250, 130, RED, 2.4)
    s += text(470, 118, "КЕРУВАННЯ: команди вгору (низька затримка!)", 11, RED, "middle", "bold")
    # телеметрія (вниз)
    s += arrow(250, 175, 700, 175, AMBER, 2.4)
    s += text(470, 198, "ТЕЛЕМЕТРІЯ: стан вниз + налаштування вгору", 11, AMBER, "middle", "bold")
    # відео (вниз)
    s += arrow(250, 220, 700, 220, BLUE, 2.0, "4 3")
    s += text(470, 243, "ВІДЕО (FPV): картинка вниз, широка смуга", 10.5, BLUE, "middle", "bold")
    s += rect(60, 300, W - 120, 60, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 324, "Кожна лінія має СВОЇ вимоги — тому їх часто розділяють (різні смуги, різні модулі).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 344, "У цьому розділі головна героїня — лінія телеметрії, бо саме нею «розмовляє» MAVLink.",
              10.5, GREY, "middle", style="italic")
    save("fig-42-1-1-two-links.svg", s)


# ── Рис. 42.1.2 — лінія керування ────────────────────────────────────────────
def fig12_control():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Лінія керування: «віжки» апарата", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "несе команди пілота чи автопілота — мало даних, але блискавично й надійно",
              11.5, GREY, "middle", style="italic")
    # пульт зі стіками
    s += rect(90, 120, 150, 90, "#fbfbfb", GREEN, 1.8, 8)
    s += circle(130, 165, 14, "none", INK, 2)
    s += circle(130, 165, 4, INK, INK, 0)
    s += circle(200, 165, 14, "none", INK, 2)
    s += circle(200, 165, 4, INK, INK, 0)
    s += text(165, 230, "стіки → канали", 10, INK, "middle", "bold")
    s += arrow(245, 165, 360, 165, RED, 2.4)
    s += text(300, 150, "негайно", 9.5, RED, "middle", "bold")
    s += _drone(450, 165, 1.2, BLUE)
    props = [("низька затримка", "запізнена команда = аварія"),
             ("висока надійність", "втрата = failsafe"),
             ("мало даних", "лише положення стіків/режим")]
    y = 130
    for t, d in props:
        s += circle(560, y - 4, 4, RED, RED, 0)
        s += text(576, y, t, 11.5, RED, "start", "bold")
        s += text(576, y + 16, d, 9.5, GREY, "start")
        y += 48
    s += rect(60, 296, W - 120, 36, LRED, RED, 1.3, 8)
    s += text(W / 2, 319, "Лінія керування «священна»: якщо вона впала — спрацьовує безпечний режим (RTL / посадка).",
              11, INK, "middle", "bold")
    save("fig-42-1-2-control.svg", s)


# ── Рис. 42.1.3 — лінія телеметрії ───────────────────────────────────────────
def fig13_telemetry():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Лінія телеметрії: «панель приладів» і двостороння розмова", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "стан апарата вниз, налаштування й команди вгору — багато даних, терпить затримку",
              11, GREY, "middle", style="italic")
    s += _drone(170, 160, 1.2, BLUE)
    # вниз — стан
    s += arrow(220, 140, 600, 110, AMBER, 2.2)
    s += text(420, 96, "вниз: висота, GPS, батарея, кути, режим", 10.5, AMBER, "middle", "bold")
    # вгору — налаштування
    s += arrow(600, 180, 220, 200, GREEN, 2.2)
    s += text(420, 222, "вгору: місія, параметри, команди", 10.5, GREEN, "middle", "bold")
    # станція
    s += rect(620, 110, 150, 110, "#fbfbfb", GREEN, 1.8, 8)
    s += text(695, 134, "наземна", 10.5, GREEN, "middle", "bold")
    s += text(695, 150, "станція", 10.5, GREEN, "middle", "bold")
    s += line(635, 165, 755, 165, FAINT, 1)
    s += text(695, 184, "карта + прилади", 9, GREY, "middle")
    s += text(695, 202, "(QGroundControl)", 9, GREY, "middle")
    s += rect(60, 280, W - 120, 52, LAMB, AMBER, 1.4, 9)
    s += text(W / 2, 304, "Терпить сотні мілісекунд затримки: це не «віжки», а інформація й налаштування.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 323, "★ Саме тут живе MAVLink — спільна мова цієї розмови.", 10.5, AMBER, "middle", "bold")
    save("fig-42-1-3-telemetry.svg", s)


# ── Рис. 42.1.4 — лінія відео ────────────────────────────────────────────────
def fig14_video():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Третя лінія: відео (FPV)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "одностороння картинка вниз; найширша смуга, часто окремий діапазон (5.8 ГГц)",
              11.5, GREY, "middle", style="italic")
    s += _drone(180, 150, 1.2, BLUE)
    s += rect(150, 175, 60, 26, "#2b2b2b", INK, 1.4, 3)
    s += text(180, 192, "камера", 9, "#fff", "middle")
    # широкий потік вниз
    s += f'<path d="M 230,150 L 700,120 L 700,190 L 230,175 Z" fill="#e9eefb" stroke="{BLUE}" stroke-width="1.6"/>\n'
    s += text(460, 142, "суцільний відеопотік (широка смуга)", 11, BLUE, "middle", "bold")
    # окуляри/екран
    s += rect(710, 135, 130, 50, "#fbfbfb", GREEN, 1.8, 8)
    s += text(775, 165, "окуляри/екран", 10, GREEN, "middle", "bold")
    s += rect(60, 230, W - 120, 76, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 254, "Відео не несе керування й телеметрії — лише картинку. Тому йому дають окремий діапазон,",
              11, INK, "middle", "bold")
    s += text(W / 2, 274, "щоб широка смуга відео не «забивала» вузькі, але критичні лінії керування й телеметрії.",
              10.5, INK, "middle")
    s += text(W / 2, 295, "Пам'ятаєш колову поляризацію (§41.4)? Вона саме для FPV — щоб не пропадати в маневрах.",
              9.5, GREY, "middle", style="italic")
    save("fig-42-1-4-video.svg", s)


# ── Рис. 42.1.5 — навіщо розділяти ───────────────────────────────────────────
def fig15_why_separate():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо розділяти лінії (і часто — діапазони)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у кожної ролі — свої вимоги; окремі смуги дають їх оптимізувати й не заважати одна одній",
              11, GREY, "middle", style="italic")
    cards = [
        ("⚡", "Різні вимоги", "Керуванню — затримка; телеметрії — дані; відео — смуга. Один канал усе не потягне.", AMBER),
        ("📻", "Різні діапазони", "Керування 2.4 / 900 / 433 МГц, телеметрія 433/915, відео 5.8 ГГц — не глушать одне одного.", BLUE),
        ("🛟", "Безпека", "Критичну лінію керування ізолюють, щоб збій відео чи телеметрії її не зачепив.", RED),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 86, 270, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, ico, 23, INK, "middle")
        s += text(x + 135, 154, title, 12.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 184
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
        x += 290
    save("fig-42-1-5-why-separate.svg", s)


# ── Рис. 42.1.6 — порівняння вимог ───────────────────────────────────────────
def fig16_requirements():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Три ролі — три набори вимог", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "видно, чому їх не зливають в одне: вимоги майже протилежні",
              11.5, GREY, "middle", style="italic")
    cols = ["", "Керування", "Телеметрія", "Відео"]
    rows = [
        ("затримка", "критична (мс)", "терпить (×100 мс)", "помірна"),
        ("надійність", "найвища", "висока", "середня"),
        ("обсяг даних", "малий", "середній", "великий"),
        ("напрям", "вгору", "у два боки", "вниз"),
    ]
    x0, y0 = 70, 84
    ws = [150, 220, 230, 180]
    colcols = [INK, RED, AMBER, BLUE]
    cx = x0
    for h, w_, cc in zip(cols, ws, colcols):
        s += rect(cx, y0, w_, 34, "#f0f0f0", GREY, 1.3)
        s += text(cx + w_ / 2, y0 + 23, h, 11.5, cc, "middle", "bold")
        cx += w_
    yy = y0 + 34
    for r in rows:
        cx = x0
        for j, (val, w_) in enumerate(zip(r, ws)):
            s += rect(cx, yy, w_, 42, "#fff" if j else "#fafafa", "#e2e2e2", 1)
            s += text(cx + (12 if j == 0 else w_ / 2), yy + 27, val, 10.5,
                      (INK if j == 0 else colcols[j]), ("start" if j == 0 else "middle"),
                      ("bold" if j == 0 else "normal"))
            cx += w_
        yy += 42
    save("fig-42-1-6-requirements.svg", s)


# ── Рис. 42.1.7 — сучасне злиття ─────────────────────────────────────────────
def fig17_convergence():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Сучасний поворот: керування й телеметрія в одній лінії", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "нові системи (ExpressLRS, Crossfire) шлють телеметрію назад тим самим лінком керування",
              11, GREY, "middle", style="italic")
    # стара схема
    s += rect(60, 90, 380, 180, "#fbfbfb", GREY, 1.6, 10)
    s += text(250, 116, "класично: окремі лінки", 11.5, INK, "middle", "bold")
    s += arrow(120, 150, 380, 150, RED, 2)
    s += text(250, 140, "керування", 9.5, RED, "middle", "bold")
    s += arrow(380, 185, 120, 185, AMBER, 2)
    s += text(250, 205, "телеметрія (окремий модуль)", 9, AMBER, "middle")
    s += text(250, 240, "два радіо, дві антени", 9.5, GREY, "middle", style="italic")
    # нова схема
    s += rect(480, 90, 380, 180, "#fbfbfb", GREEN, 1.6, 10)
    s += text(670, 116, "сучасно: один лінк, два боки", 11, GREEN, "middle", "bold")
    s += arrow(540, 160, 800, 160, RED, 2)
    s += text(670, 150, "керування вгору", 9.5, RED, "middle", "bold")
    s += arrow(800, 185, 540, 185, AMBER, 2)
    s += text(670, 205, "телеметрія вниз — тим самим радіо", 9, AMBER, "middle")
    s += text(670, 240, "одне радіо; MAVLink може йти й тут", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 300, "Технології зливаються, але ДВІ РОЛІ — «віжки» й «панель» — лишаються концептуально різними.",
              11, INK, "middle", "bold")
    save("fig-42-1-7-convergence.svg", s)


# ============================================================================
#  §42.2 — RC-лінк: канали, прив'язка, протоколи приймача
# ============================================================================

def _stick(cx, cy, dx, dy, col=INK):
    s = circle(cx, cy, 26, "#fbfbfb", col, 2)
    s += line(cx - 26, cy, cx + 26, cy, FAINT, 1)
    s += line(cx, cy - 26, cx, cy + 26, FAINT, 1)
    s += circle(cx + dx, cy + dy, 7, col, col, 0)
    return s


# ── Рис. 42.2.1 — стіки стають каналами ──────────────────────────────────────
def fig21_channels():
    W, H = 920, 370
    s = header(W, H)
    s += text(W / 2, 34, "Як рух стіків стає «каналами»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна вісь стіка → окреме число (зазвичай 1000–2000 мкс, центр 1500) → це й є канал",
              11, GREY, "middle", style="italic")
    s += _stick(150, 150, -10, 12, GREEN)
    s += text(150, 200, "лівий стік", 10, INK, "middle", "bold")
    s += text(150, 216, "газ / нишпорення", 9, GREY, "middle")
    s += _stick(320, 150, 12, -8, GREEN)
    s += text(320, 200, "правий стік", 10, INK, "middle", "bold")
    s += text(320, 216, "крен / тангаж", 9, GREY, "middle")
    s += arrow(360, 150, 430, 150, INK, 2.2)
    # канали-бари
    chans = [("CH1 газ", 0.3), ("CH2 крен", 0.6), ("CH3 тангаж", 0.45), ("CH4 нишп.", 0.5), ("CH5 режим", 0.9)]
    bx, by = 460, 100
    for i, (nm, v) in enumerate(chans):
        y = by + i * 30
        s += text(bx - 6, y + 12, nm, 9.5, INK, "end")
        s += rect(bx, y, 280, 16, "#f0f0f0", GREY, 1)
        s += rect(bx, y, 280 * v, 16, "#cdeccd", GREEN, 1.2)
        s += text(bx + 290, y + 12, f"{1000 + int(v*1000)}", 9.5, GREEN, "start", "bold")
    s += text(bx + 140, by + 165, "мкс", 9, GREY, "middle")
    s += rect(60, 300, W - 120, 50, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 324, "Передавач пакує ВСІ канали в один кадр і шле в ефір; приймач розпаковує й віддає польотному контролеру.",
              11, INK, "middle", "bold")
    s += text(W / 2, 343, "4 основні канали (газ, крен, тангаж, нишпорення) + допоміжні (режими, підвіс, тощо).", 10, GREY, "middle", style="italic")
    save("fig-42-2-1-channels.svg", s)


# ── Рис. 42.2.2 — повний ланцюг RC ───────────────────────────────────────────
def fig22_chain():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Повний ланцюг керування: від стіка до мотора", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "пульт → радіолінк → приймач → польотний контролер → мотори",
              11.5, GREY, "middle", style="italic")
    blocks = [
        ("Пульт (TX)", "стіки → канали → кадр", GREEN),
        ("Радіолінк", "стрибки по діапазону", AMBER),
        ("Приймач (RX)", "розпаковує канали", BLUE),
        ("Контролер (FC)", "змішує → мотори", RED),
    ]
    x = 50
    bw = 195
    y = 130
    for i, (nm, sub, col) in enumerate(blocks):
        s += rect(x, y, bw, 80, "#fbfbfb", col, 1.8, 8)
        s += text(x + bw / 2, y + 34, nm, 12.5, col, "middle", "bold")
        s += text(x + bw / 2, y + 56, sub, 9.5, GREY, "middle")
        if i < len(blocks) - 1:
            lab = "ефір" if i == 0 else ("SBUS/CRSF" if i == 2 else "")
            s += arrow(x + bw + 2, y + 40, x + bw + 14, y + 40, INK, 2)
            if i == 1:
                for k in range(3):
                    s += f'<path d="M {x+bw+2},{y+40} q 6,-8 12,0" fill="none" stroke="{AMBER}" stroke-width="1.4"/>\n'
            if lab:
                s += text(x + bw + 8, y + 30, lab, 8.5, GREY, "start", style="italic")
        x += bw + 16
    s += rect(60, 252, W - 120, 50, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 276, "Між приймачем і контролером — окремий «протокол приймача» (PWM / PPM / SBUS / CRSF), про який нижче.",
              11, INK, "middle", "bold")
    s += text(W / 2, 294, "А пульт із приймачем пов'язує одноразова «прив'язка» (binding).", 10, GREY, "middle", style="italic")
    save("fig-42-2-2-chain.svg", s)


# ── Рис. 42.2.3 — прив'язка (binding) ────────────────────────────────────────
def fig23_binding():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Прив'язка (binding): щоб пульт і приймач «впізнавали» одне одного", 16.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одноразово задають спільний унікальний ключ і послідовність стрибків — і пара говорить лише між собою",
              10.5, GREY, "middle", style="italic")
    # пара 1
    s += rect(90, 100, 120, 60, "#eef6ef", GREEN, 1.8, 6)
    s += text(150, 136, "пульт A", 11, GREEN, "middle", "bold")
    s += rect(330, 100, 120, 60, "#e9eefb", BLUE, 1.8, 6)
    s += text(390, 136, "приймач A", 10.5, BLUE, "middle", "bold")
    s += arrow(212, 120, 328, 120, GREEN, 2)
    s += arrow(328, 140, 212, 140, BLUE, 2)
    s += text(270, 92, "свій ключ + хоп-послідовність", 9, INK, "middle", "bold")
    # пара 2 поряд — не заважає
    s += rect(90, 190, 120, 60, "#fbf3df", AMBER, 1.8, 6)
    s += text(150, 226, "пульт B", 11, AMBER, "middle", "bold")
    s += rect(330, 190, 120, 60, "#fbf3df", AMBER, 1.8, 6)
    s += text(390, 226, "приймач B", 10.5, AMBER, "middle", "bold")
    s += arrow(212, 220, 328, 220, AMBER, 2)
    s += text(270, 268, "інший ключ — інша пара", 9, GREY, "middle")
    # пояснення
    s += rect(500, 96, 360, 160, LGREY, GREY, 1.3, 9)
    s += text(680, 122, "Що дає прив'язка:", 11, INK, "middle", "bold")
    for i, t in enumerate(["• пара спілкується лише між собою", "• десятки пілотів поряд не заважають", "• спирається на стрибки частоти (§40.5)", "• роблять раз: кнопкою, перемичкою", "  або bind-фразою"]):
        s += text(516, 148 + i * 22, t, 10, INK, "start")
    save("fig-42-2-3-binding.svg", s)


# ── Рис. 42.2.4 — PWM проти PPM ──────────────────────────────────────────────
def fig24_pwm_ppm():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Старі протоколи приймача: PWM і PPM", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "PWM — окремий дріт на кожен канал; PPM — усі канали один за одним по ОДНОМУ дроту",
              11, GREY, "middle", style="italic")
    # PWM
    s += text(60, 100, "PWM (по дроту на канал):", 11, BLUE, "start", "bold")
    for i in range(3):
        y = 120 + i * 40
        s += text(70, y + 16, f"CH{i+1}", 9, INK, "start")
        w_ = [40, 24, 32][i]
        s += line(120, y + 20, 120, y, INK, 1.8)
        s += line(120, y, 120 + w_, y, INK, 1.8)
        s += line(120 + w_, y, 120 + w_, y + 20, INK, 1.8)
        s += line(120 + w_, y + 20, 260, y + 20, INK, 1.8)
        s += text(280, y + 16, "1000–2000 мкс", 8.5, GREY, "start")
    s += text(180, 250, "багато дротів", 9.5, RED, "middle", "bold")
    # PPM
    s += text(500, 100, "PPM (усе по одному дроту):", 11, GREEN, "start", "bold")
    x = 520
    y = 160
    s += line(500, y + 20, 520, y + 20, INK, 1.8)
    for w_ in (40, 24, 32, 30, 44):
        s += line(x, y + 20, x, y, INK, 1.8)
        s += line(x, y, x + 6, y, INK, 1.8)
        s += line(x + 6, y, x + 6, y + 20, INK, 1.8)
        s += line(x + 6, y + 20, x + 6 + w_, y + 20, INK, 1.8)
        x += 6 + w_
    s += text(660, 250, "один дріт, до ~8 каналів", 9.5, GREEN, "middle", "bold")
    s += rect(60, 290, W - 120, 36, LGREY, GREY, 1.3, 8)
    s += text(W / 2, 313, "Обидва — аналогові за духом і застарілі; сучасні приймачі віддають канали ЦИФРОВО (далі).",
              11, INK, "middle", "bold")
    save("fig-42-2-4-pwm-ppm.svg", s)


# ── Рис. 42.2.5 — SBUS і CRSF ────────────────────────────────────────────────
def fig25_sbus_crsf():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Сучасні цифрові протоколи: SBUS і CRSF", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усі канали — цифровим серійним потоком одним дротом; це послідовний зв'язок із Розділу 35",
              11, GREY, "middle", style="italic")
    s += rect(60, 90, 380, 200, "#fbfbfb", BLUE, 1.8, 10)
    s += text(250, 116, "SBUS (Futaba)", 12.5, BLUE, "middle", "bold")
    for i, t in enumerate(["• інвертований UART, 100 000 бод", "• до 16 каналів в одному кадрі", "• де-факто стандарт приймачів", "• односторонній (канали вниз)"]):
        s += text(80, 146 + i * 28, t, 10.5, INK, "start")
    s += sine(80, 270, 320, 0, 0, BLUE, 0)
    s += rect(480, 90, 380, 200, "#fbfbfb", GREEN, 1.8, 10)
    s += text(670, 116, "CRSF (Crossfire / ELRS)", 11.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• швидкий UART, 420 000 бод", "• канали ВНИЗ + телеметрія ВГОРУ", "• наднизька затримка", "• мова сучасних ELRS-лінків"]):
        s += text(500, 146 + i * 28, t, 10.5, INK, "start")
    s += rect(60, 300, W - 120, 26, LBLUE, BLUE, 1.2, 7)
    s += text(W / 2, 318, "Це той самий послідовний UART (Розділ 35), тільки на службі керування — кадр, біти, швидкість.",
              10.5, INK, "middle", "bold")
    save("fig-42-2-5-sbus-crsf.svg", s)


# ── Рис. 42.2.6 — сучасні RC-системи ─────────────────────────────────────────
def fig26_systems():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Сучасні RC-системи: чим лінкують сьогодні", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "відкриті й фірмові; головний компроміс — дальність (900 МГц) проти смуги (2.4 ГГц)",
              11, GREY, "middle", style="italic")
    rows = [
        ("ExpressLRS (ELRS)", "відкритий, на LoRa", "далеко, наднизька затримка", GREEN),
        ("TBS Crossfire/Tracer", "фірмовий, CRSF", "далекобійний, надійний", BLUE),
        ("FrSky / Spektrum / Futaba", "класичні 2.4 ГГц", "масові, з власними протоколами", AMBER),
    ]
    y = 88
    for nm, kind, note, col in rows:
        s += rect(60, y, 360, 60, "#fbfbfb", col, 1.6, 9)
        s += text(80, y + 26, nm, 12, col, "start", "bold")
        s += text(80, y + 46, kind, 10, GREY, "start")
        s += arrow(425, y + 30, 455, y + 30, INK, 1.6)
        s += rect(460, y, 400, 60, "#f7f7f7", col, 1.3, 9)
        s += text(480, y + 35, note, 11, INK, "start")
        y += 72
    s += text(W / 2, 312, "900 МГц бере далі й крізь перешкоди (§39.4); 2.4 ГГц дає більше каналів і даних. Обирай під задачу.",
              10.5, GREY, "middle", style="italic")
    save("fig-42-2-6-systems.svg", s)


# ── Рис. 42.2.7 — failsafe приймача ──────────────────────────────────────────
def fig27_failsafe():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Що робить приймач, коли сигнал зник: failsafe", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "лінія керування «священна» (§42.1): на втрату сигналу приймач має заздалегідь заданий план",
              10.5, GREY, "middle", style="italic")
    # сигнал є → зник
    s += text(230, 96, "сигнал є", 11, GREEN, "middle", "bold")
    s += line(120, 150, 340, 150, GREEN, 2.4)
    s += text(230, 170, "канали оновлюються", 9.5, GREY, "middle")
    s += text(230, 230, "✗ сигнал зник", 11, RED, "middle", "bold")
    s += line(120, 200, 230, 200, GREY, 2, "4 3")
    s += line(244, 194, 256, 206, RED, 2.4)
    s += line(244, 206, 256, 194, RED, 2.4)
    s += arrow(360, 175, 430, 175, INK, 2.4)
    # реакції
    opts = [("утримати останнє", "коротка втрата"), ("вимкнути газ", "не «полетіти геть»"), ("задані значення", "→ RTL / посадка")]
    bx = 460
    for i, (t, d) in enumerate(opts):
        y = 110 + i * 56
        s += rect(bx, y, 400, 46, ("#eef6ef" if i == 2 else "#f7f7f7"), (GREEN if i == 2 else GREY), 1.4, 8)
        s += text(bx + 16, y + 20, t, 11.5, (GREEN if i == 2 else INK), "start", "bold")
        s += text(bx + 16, y + 38, d, 9.5, GREY, "start")
    s += text(W / 2, 304, "Правильний failsafe (через MAVLink/контролер) — повернення додому чи м'яка посадка, а не падіння.",
              10.5, INK, "middle", "bold")
    save("fig-42-2-7-failsafe.svg", s)


# ============================================================================
#  §42.3 — Телеметрія: двосторонній потік (air/ground модулі)
# ============================================================================

def _module(x, y, w, h, lab, col):
    s = rect(x, y, w, h, "#fbfbfb", col, 1.8, 6)
    s += line(x + w / 2, y, x + w / 2, y - 22, METAL, 3)
    s += line(x + w / 2 - 6, y - 22, x + w / 2 + 6, y - 26, METAL, 2.4)
    s += text(x + w / 2, y + h / 2 + 4, lab, 10.5, col, "middle", "bold")
    return s


# ── Рис. 42.3.1 — air/ground пара ────────────────────────────────────────────
def fig31_air_ground():
    W, H = 940, 350
    s = header(W, H)
    s += text(W / 2, 34, "Лінія телеметрії — це ПАРА радіомодулів", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "один модуль на борту (air), другий на землі (ground); разом — бездротовий «провід»",
              11.5, GREY, "middle", style="italic")
    s += _drone(180, 150, 1.4, BLUE)
    s += _module(150, 200, 60, 36, "air", BLUE)
    s += _tower(770, 250, 60, GREEN) if False else ""
    s += rect(720, 150, 130, 90, "#fbfbfb", GREEN, 1.8, 8)
    s += text(785, 130, "ноутбук / станція", 10, GREEN, "middle", "bold")
    s += line(785, 150, 785, 120, FAINT, 1)
    s += _module(755, 250, 60, 36, "ground", GREEN)
    # радіолінк
    s += arrow(215, 215, 750, 250, AMBER, 2.2, "5 4")
    s += arrow(750, 268, 215, 233, BLUE, 2.2, "5 4")
    s += text(480, 200, "радіолінк (433 / 868 / 915 МГц)", 11, AMBER, "middle", "bold")
    s += rect(60, 300, W - 120, 40, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 324, "Два модулі утворюють прозорий «бездротовий UART»: байти, що входять з одного боку, виходять з іншого.",
              11, INK, "middle", "bold")
    save("fig-42-3-1-air-ground.svg", s)


# ── Рис. 42.3.2 — прозорий міст ──────────────────────────────────────────────
def fig32_bridge():
    W, H = 940, 320
    s = header(W, H)
    s += text(W / 2, 34, "Прозорий серійний міст: наче бездротовий UART-кабель", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "контролер і станція «думають», що з'єднані дротом; насправді між ними радіо",
              11, GREY, "middle", style="italic")
    blocks = [
        ("Контролер (FC)", "UART", BLUE),
        ("air модуль", "радіо", AMBER),
        ("ground модуль", "USB", AMBER),
        ("Станція (GCS)", "MAVLink", GREEN),
    ]
    x = 50
    bw = 190
    y = 120
    for i, (nm, port, col) in enumerate(blocks):
        s += rect(x, y, bw, 70, "#fbfbfb", col, 1.8, 8)
        s += text(x + bw / 2, y + 32, nm, 12, col, "middle", "bold")
        s += text(x + bw / 2, y + 52, port, 9.5, GREY, "middle")
        if i < len(blocks) - 1:
            if i == 1:
                s += text(x + bw + 8, y + 26, "(((", 12, AMBER, "start", "bold")
                s += text(x + bw + 8, y + 52, ")))", 12, AMBER, "start", "bold")
            s += arrow(x + bw + 2, y + 35, x + bw + 14, y + 35, INK, 2)
            s += arrow(x + bw + 14, y + 48, x + bw + 2, y + 48, GREY, 1.6)
        x += bw + 16
    s += rect(60, 230, W - 120, 70, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 254, "MAVLink тече цією трубою наскрізь. Радіо «не знає», що несе, — для нього це просто потік байтів.",
              11, INK, "middle", "bold")
    s += text(W / 2, 276, "Тому ту саму телеметрію можна пустити й через USB, і через Wi-Fi/Bluetooth — труба змінюється, мова ні.",
              10, GREY, "middle", style="italic")
    save("fig-42-3-2-bridge.svg", s)


# ── Рис. 42.3.3 — що тече в потоці ───────────────────────────────────────────
def fig33_stream():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що тече вниз: потік MAVLink-повідомлень", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "різні повідомлення йдуть зі своєю частотою — серце (heartbeat) рідко, кути часто",
              11, GREY, "middle", style="italic")
    msgs = [
        ("HEARTBEAT", "«я живий», тип, режим, armed", "~1 Гц", RED),
        ("ATTITUDE", "крен, тангаж, нишпорення", "~10–50 Гц", BLUE),
        ("GLOBAL_POSITION_INT", "координати, висота", "~5 Гц", GREEN),
        ("SYS_STATUS", "батарея, стан давачів", "~2 Гц", AMBER),
        ("VFR_HUD", "швидкість, висота, набір", "~10 Гц", BLUE),
    ]
    y = 100
    for nm, desc, rate, col in msgs:
        s += rect(70, y, 250, 38, "#fbfbfb", col, 1.6, 6)
        s += text(82, y + 24, nm, 11, col, "start", "bold")
        s += text(340, y + 24, desc, 11, INK, "start")
        s += rect(700, y + 6, 90, 26, "#f0f0f0", GREY, 1, 5)
        s += text(745, y + 24, rate, 10.5, INK, "middle", "bold")
        s += arrow(325, y + 19, 335, y + 19, GREY, 1.4)
        y += 48
    s += rect(60, 338, W - 120, 1, "none", "none", 0)
    s += text(W / 2, 332, "Кожен тип — на своїй «частоті потоку» (stream rate), яку можна налаштувати під вузький канал.",
              10, GREY, "middle", style="italic")
    save("fig-42-3-3-stream.svg", s)


# ── Рис. 42.3.4 — двосторонність ─────────────────────────────────────────────
def fig34_bidirectional():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 34, "Це РОЗМОВА, а не мовлення: потік у два боки", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вниз — стан апарата; вгору — команди, параметри, завантаження місії",
              11.5, GREY, "middle", style="italic")
    s += _drone(150, 170, 1.3, BLUE)
    s += rect(740, 120, 140, 110, "#fbfbfb", GREEN, 1.8, 8)
    s += text(810, 110, "станція (GCS)", 10, GREEN, "middle", "bold")
    # вниз
    s += arrow(720, 130, 210, 130, AMBER, 2.4)
    s += text(465, 116, "ВНИЗ: телеметрія (висота, GPS, батарея, режим)", 10.5, AMBER, "middle", "bold")
    # вгору
    s += arrow(210, 220, 720, 220, GREEN, 2.4)
    s += text(465, 243, "ВГОРУ: команди, параметри, місія, RC-override", 10.5, GREEN, "middle", "bold")
    s += rect(60, 280, W - 120, 50, LAMB, AMBER, 1.4, 9)
    s += text(W / 2, 304, "Та сама лінія несе обидва боки: апарат звітує, людина (чи код) керує й налаштовує.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 322, "Саме двосторонність робить телеметрію місцем для MAVLink — мови запитів і відповідей.",
              10, GREY, "middle", style="italic")
    save("fig-42-3-4-bidirectional.svg", s)


# ── Рис. 42.3.5 — SiK-радіо ──────────────────────────────────────────────────
def fig35_sik():
    W, H = 940, 320
    s = header(W, H)
    s += text(W / 2, 34, "Класика телеметрії: SiK-радіо (3DR / RFD900)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "дві однакові платки з антенами — найпоширеніший спосіб пустити MAVLink по радіо",
              11, GREY, "middle", style="italic")
    for cx, lab in [(250, "air (на дроні)"), (690, "ground (на USB)")]:
        s += rect(cx - 70, 110, 140, 70, "#1f3a1f", GREEN, 1.6, 6)
        s += line(cx + 70, 130, cx + 110, 100, METAL, 3)
        s += rect(cx - 50, 130, 40, 30, "#3a5a3a", "#9ec99e", 1)
        s += text(cx, 152, "Si chip", 8, "#cfe8cf", "middle")
        s += text(cx, 200, lab, 10.5, GREEN, "middle", "bold")
    s += arrow(330, 145, 610, 145, AMBER, 2.2, "5 4")
    s += arrow(610, 160, 330, 160, BLUE, 2.2, "5 4")
    s += rect(60, 226, W - 120, 80, LGREY, GREY, 1.3, 9)
    s += text(W / 2, 250, "Відкрита прошивка SiK; діапазон 433 / 868 / 915 МГц; стрибки частоти (FHSS, §40.5); ~100 мВт; дальність — кілометри.",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 272, "Серійна швидкість зазвичай 57600 бод. Сильніший варіант — RFD900 на десятки км.", 10, INK, "middle")
    s += text(W / 2, 292, "Підключив air до телеметрійного UART контролера, ground — у USB ноутбука, і MAVLink «полетів».", 9.5, GREY, "middle", style="italic")
    save("fig-42-3-5-sik.svg", s)


# ── Рис. 42.3.6 — топології підключення ──────────────────────────────────────
def fig36_topologies():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 34, "Як іще довезти MAVLink до станції", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "труба буває різна — мова (MAVLink) лишається тією самою",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("Телеметрійне радіо", "SiK / RFD900", "класика, кілометри", AMBER),
        ("USB-кабель", "на столі/стенді", "налагодження поряд", BLUE),
        ("Wi-Fi / Bluetooth", "ESP32-міст, TCP/UDP", "MAVLink по мережі (§38)", GREEN),
        ("Спільно з RC", "CRSF-телеметрія (ELRS)", "один лінк на все", RED),
    ]
    x = 40
    for nm, sub, note, col in cards:
        s += rect(x, 86, 215, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 107, 118, nm, 12, col, "middle", "bold")
        s += rect(x + 30, 134, 154, 30, "#fff", col, 1.3, 6)
        s += text(x + 107, 154, sub, 10, INK, "middle", "bold")
        words = note.split()
        ln, yy = "", 192
        for wd in words:
            if len(ln) + len(wd) > 20:
                s += text(x + 107, yy, ln.strip(), 9.8, GREY, "middle")
                ln, yy = "", yy + 16
            ln += wd + " "
        s += text(x + 107, yy, ln.strip(), 9.8, GREY, "middle")
        x += 223
    s += text(W / 2, 312, "Окремий випадок — бортовий комп'ютер просто поряд із контролером (без радіо), про це §42.7.",
              10.5, INK, "middle", "bold")
    save("fig-42-3-6-topologies.svg", s)


# ── Рис. 42.3.7 — наземна станція ────────────────────────────────────────────
def fig37_gcs():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 34, "Людський кінець лінії: наземна станція (GCS)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "QGroundControl чи Mission Planner читають MAVLink і показують «панель приладів» + дають керувати",
              10.5, GREY, "middle", style="italic")
    # екран
    s += rect(120, 90, 700, 210, "#101418", INK, 2, 8)
    # карта
    s += rect(140, 110, 380, 170, "#1c2a1c", "#33502f", 1.4, 4)
    s += text(330, 130, "карта + маршрут", 10, "#9ec99e", "middle")
    # шлях
    s += _poly([(170, 250), (240, 200), (330, 230), (430, 170), (490, 190)], SPARK, 2)
    for px, py in [(170, 250), (330, 230), (490, 190)]:
        s += circle(px, py, 4, SPARK, SPARK, 0)
    # HUD-панель
    s += rect(540, 110, 260, 170, "#15191d", "#2a3340", 1.4, 4)
    s += text(670, 132, "ПРИЛАДИ (HUD)", 10, "#8fb7ff", "middle", "bold")
    for i, (k, v) in enumerate([("висота", "42 м"), ("швидк.", "8 м/с"), ("батарея", "78 %"), ("режим", "AUTO"), ("GPS", "3D fix, 12 sat")]):
        s += text(560, 158 + i * 24, k, 9.5, "#9aa", "start")
        s += text(780, 158 + i * 24, v, 9.5, "#cfe", "end", "bold")
    s += rect(60, 308, W - 120, 1, "none", "none", 0)
    s += text(W / 2, 322, "GCS — це програма, що «розуміє» MAVLink: малює стан, шле команди, завантажує місії. Людина говорить із дроном через неї.",
              10, GREY, "middle", style="italic")
    save("fig-42-3-7-gcs.svg", s)


# ============================================================================
#  §42.4 — Затримка й надійність (чому критично)
# ============================================================================

# ── Рис. 42.4.1 — звідки береться затримка ───────────────────────────────────
def fig41_latency_chain():
    W, H = 940, 320
    s = header(W, H)
    s += text(W / 2, 34, "Затримка складається з усього ланцюга", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "від команди до дії минає час на кожній ланці — і він додається",
              11.5, GREY, "middle", style="italic")
    steps = [("зчитати\nстік", BLUE), ("закодувати\nкадр", BLUE), ("радіо:\nкадр+хопи+\nретраї", RED),
             ("розкодувати", GREEN), ("цикл FC", GREEN), ("реакція\nмотора", AMBER)]
    x = 40
    bw = 132
    y = 110
    for i, (nm, col) in enumerate(steps):
        s += rect(x, y, bw, 70, "#fbfbfb", col, 1.7, 7)
        for k, part in enumerate(nm.split("\n")):
            s += text(x + bw / 2, y + 26 + k * 15, part, 9.8, col, "middle", "bold")
        if i < len(steps) - 1:
            s += arrow(x + bw + 1, y + 35, x + bw + 13, y + 35, INK, 2)
        x += bw + 14
    s += line(40, 200, x - 14, 200, INK, 1.6)
    s += line(40, 195, 40, 205, INK, 1.6)
    s += line(x - 14, 195, x - 14, 205, INK, 1.6)
    s += text((40 + x - 14) / 2, 220, "сумарна затримка (десятки–сотні мс)", 11, INK, "middle", "bold")
    s += rect(60, 250, W - 120, 50, LRED, RED, 1.3, 9)
    s += text(W / 2, 274, "Радіоланка — найзмінніша: кадр, стрибки, перевідправлення. Що гірший канал, то більше ретраїв → більша затримка.",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 292, "Ціль FPV-керування — менше ~30 мс; понад ~100 мс летіти вже важко.", 9.5, GREY, "middle", style="italic")
    save("fig-42-4-1-latency-chain.svg", s)


# ── Рис. 42.4.2 — затримка в контурі = нестабільність ────────────────────────
def fig42_feedback():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому затримка небезпечна: запізнення в контурі", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "пілот (чи автопілот) у петлі зворотного зв'язку; запізнена реакція розгойдує апарат",
              11, GREY, "middle", style="italic")
    # петля
    cx, cy = 230, 180
    nodes = [("команда", cx, cy - 70, RED), ("апарат діє", cx + 90, cy, BLUE),
             ("спостерігаєш", cx, cy + 70, GREEN), ("коригуєш", cx - 90, cy, AMBER)]
    for nm, nx, ny, col in nodes:
        s += rect(nx - 50, ny - 16, 100, 32, "#fbfbfb", col, 1.6, 6)
        s += text(nx, ny + 5, nm, 10, col, "middle", "bold")
    s += arrow(cx + 40, cy - 62, cx + 70, cy - 26, INK, 1.8)
    s += arrow(cx + 70, cy + 26, cx + 40, cy + 62, INK, 1.8)
    s += arrow(cx - 40, cy + 62, cx - 70, cy + 26, INK, 1.8)
    s += arrow(cx - 70, cy - 26, cx - 40, cy - 62, INK, 1.8)
    s += text(cx, cy + 4, "⏱ затримка", 9.5, RED, "middle", "bold")
    # графік розгойдування
    s += text(640, 100, "мала затримка → стабільно", 10, GREEN, "middle", "bold")
    s += sine(470, 140, 340, 16, 3, GREEN, 2)
    s += text(640, 210, "велика затримка → розгойдування", 10, RED, "middle", "bold")
    pts = []
    for i in range(141):
        t = i / 140
        amp = 6 + t * 40
        pts.append((470 + t * 340, 260 - amp * math.sin(2 * math.pi * 3 * t)))
    s += _poly(pts, RED, 2)
    s += rect(60, 300, W - 120, 30, LGREY, GREY, 1.3, 7)
    s += text(W / 2, 320, "Запізнена корекція приходить «не туди» — апарат перелітає ціль і коливається дедалі сильніше.",
              10.5, INK, "middle", "bold")
    save("fig-42-4-2-feedback.svg", s)


# ── Рис. 42.4.3 — надійність: пакети губляться ───────────────────────────────
def fig43_reliability():
    W, H = 940, 320
    s = header(W, H)
    s += text(W / 2, 34, "Надійність: частина пакетів не доходить", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "радіо ненадійне (§38, §40.7); CRC (§35) ловить спотворені — їх відкидають",
              11, GREY, "middle", style="italic")
    y = 150
    states = [1, 1, 0, 1, 2, 1, 1, 0, 1, 1]  # 1=ok, 0=lost, 2=corrupt
    x = 90
    for st in states:
        if st == 1:
            s += rect(x, y, 50, 36, "#eef6ef", GREEN, 1.6, 4)
            s += text(x + 25, y + 23, "OK", 10, GREEN, "middle", "bold")
        elif st == 0:
            s += rect(x, y, 50, 36, "#f4f4f4", GREY, 1.4, 4, )
            s += text(x + 25, y + 24, "—", 14, GREY, "middle", "bold")
        else:
            s += rect(x, y, 50, 36, "#fbecec", RED, 1.6, 4)
            s += text(x + 25, y + 24, "✗", 13, RED, "middle", "bold")
        x += 58
    s += text(90, y - 16, "потік пакетів →", 10, INK, "start", "bold")
    s += text(90, y + 64, "OK — дійшов;   — загублено;   ✗ — спотворено (CRC відкинув)", 10.5, GREY, "start")
    s += rect(60, 232, W - 120, 70, LAMB, AMBER, 1.3, 9)
    s += text(W / 2, 256, "Надійність = частка пакетів, що дійшли правильними. На краю дальності вона падає.",
              11, INK, "middle", "bold")
    s += text(W / 2, 278, "Питання не «чи губляться» (губляться завжди), а «що з цим робити» — і відповідь різна для різних даних.",
              10, GREY, "middle", style="italic")
    save("fig-42-4-3-reliability.svg", s)


# ── Рис. 42.4.4 — дві стратегії ──────────────────────────────────────────────
def fig44_strategies():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дві стратегії проти втрат — для різних даних", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "керування жертвує надійністю заради швидкості; команди — навпаки",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 86, 400, 210, "#fbfbfb", RED, 1.8, 10)
    s += text(260, 112, "Керування / телеметрія-потік", 11.5, RED, "middle", "bold")
    s += text(260, 138, "НЕ перевідправляти", 12, INK, "middle", "bold")
    for i, t in enumerate(["• шлемо безперервно, часто", "• загубився кадр — береться наступний", "• перевідправлення було б ЗАПІЗНІЛИМ", "• втратив зовсім → failsafe"]):
        s += text(80, 166 + i * 26, t, 10.3, INK, "start")
    s += text(260, 282, "пріоритет — затримка", 10.5, RED, "middle", "bold")
    s += rect(480, 86, 400, 210, "#fbfbfb", GREEN, 1.8, 10)
    s += text(680, 112, "Команди / параметри / місія", 11.5, GREEN, "middle", "bold")
    s += text(680, 138, "підтвердження + повтор", 12, INK, "middle", "bold")
    for i, t in enumerate(["• надіслав команду → чекаю ACK", "• нема ACK → надсилаю ще раз", "• місію вантажать пункт за пунктом", "• затримка тут не страшна"]):
        s += text(500, 166 + i * 26, t, 10.3, INK, "start")
    s += text(680, 282, "пріоритет — надійність", 10.5, GREEN, "middle", "bold")
    save("fig-42-4-4-strategies.svg", s)


# ── Рис. 42.4.5 — компроміс затримка↔надійність ──────────────────────────────
def fig45_tradeoff():
    W, H = 940, 320
    s = header(W, H)
    s += text(W / 2, 34, "Компроміс: перевідправлення купує надійність ціною затримки", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "не можна мати одразу й максимум надійності, і мінімум затримки — обирай під дані",
              11, GREY, "middle", style="italic")
    ox, oy = 150, 250
    axw, axh = 640, 170
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh, INK, 2)
    s += text(ox + axw, oy + 22, "надійність →", 11, INK, "end", "bold")
    s += text(ox - 12, oy - axh + 4, "затримка", 11, INK, "end", "bold")
    pts = []
    for i in range(81):
        t = i / 80
        x = ox + t * axw
        y = oy - (t ** 2) * axh
        pts.append((x, y))
    s += _poly(pts, AMBER, 2.6)
    s += circle(ox + 0.2 * axw, oy - (0.2 ** 2) * axh, 5, RED, RED, 0)
    s += text(ox + 0.2 * axw, oy - (0.2 ** 2) * axh - 12, "керування: 0 повторів", 9.5, RED, "middle", "bold")
    s += circle(ox + 0.9 * axw, oy - (0.9 ** 2) * axh, 5, GREEN, GREEN, 0)
    s += text(ox + 0.9 * axw - 10, oy - (0.9 ** 2) * axh - 10, "місія: повтори до успіху", 9.5, GREEN, "end", "bold")
    s += text(W / 2, 304, "Кожен повтор додає коло «надіслав-почекав-ще раз» — більше надійності, але більше часу.",
              10.5, INK, "middle", "bold")
    save("fig-42-4-5-tradeoff.svg", s)


# ── Рис. 42.4.6 — дальність б'є по обох ───────────────────────────────────────
def fig46_range():
    W, H = 940, 320
    s = header(W, H)
    s += text(W / 2, 34, "Край дальності псує і затримку, і надійність", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "слабшає сигнал (§40.6) → росте втрата пакетів → більше ретраїв → лінк «гусне» й рветься",
              10.5, GREY, "middle", style="italic")
    ox, oy = 130, 250
    axw, axh = 680, 170
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh, INK, 2)
    s += text(ox + axw, oy + 22, "відстань →", 11, INK, "end", "bold")
    s += text(ox - 12, oy - axh + 4, "втрата пакетів", 10.5, INK, "end", "bold")
    pts = []
    for i in range(81):
        t = i / 80
        y = oy - (t ** 3) * axh
        pts.append((ox + t * axw, y))
    s += _poly(pts, RED, 2.6)
    # зона запасу
    s += line(ox + 0.6 * axw, oy, ox + 0.6 * axw, oy - axh, GREEN, 1.6, "5 4")
    s += text(ox + 0.6 * axw, oy - axh - 4, "межа з добрим запасом (§40.6)", 9.5, GREEN, "middle", "bold")
    s += text(ox + 0.3 * axw, oy - 30, "тут лінк здоровий", 9.5, GREEN, "middle")
    s += text(ox + 0.85 * axw, oy - 120, "тут уже рветься", 9.5, RED, "middle", "bold")
    s += text(W / 2, 304, "Тому запас на завмирання (§40.6) — не розкіш: він тримає і низьку затримку, і надійність далеко від межі.",
              10.5, INK, "middle", "bold")
    save("fig-42-4-6-range.svg", s)


# ── Рис. 42.4.7 — що таке «лінк втрачено» ────────────────────────────────────
def fig47_link_lost():
    W, H = 940, 330
    s = header(W, H)
    s += text(W / 2, 34, "Коли лінк вважати втраченим — і що тоді", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нема серцебиття (HEARTBEAT) кілька секунд → «лінк втрачено» → failsafe",
              11, GREY, "middle", style="italic")
    ox = 90
    y = 150
    s += line(ox, y, ox + 760, y, FAINT, 1)
    s += text(ox, y - 30, "HEARTBEAT кожну секунду:", 10, INK, "start", "bold")
    beats = [1, 1, 1, 1, 0, 0, 0]
    for i, b in enumerate(beats):
        x = ox + 40 + i * 95
        if b:
            s += line(x, y, x, y - 40, GREEN, 3)
            s += circle(x, y - 40, 4, GREEN, GREEN, 0)
        else:
            s += line(x, y, x, y - 16, RED, 2, "3 3")
            s += line(x - 6, y - 22, x + 6, y - 10, RED, 2)
            s += line(x - 6, y - 10, x + 6, y - 22, RED, 2)
    s += text(ox + 40 + 5 * 95, y + 24, "тиша…", 10, RED, "middle", "bold")
    s += line(ox + 40 + 3.5 * 95, y + 40, ox + 40 + 6 * 95, y + 40, RED, 1.6)
    s += text(ox + 40 + 4.7 * 95, y + 56, "таймаут (напр. 2–3 с)", 9.5, RED, "middle", "bold")
    s += arrow(ox + 700, y, ox + 740, y, INK, 2) if False else ""
    s += rect(60, 250, W - 120, 70, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 274, "Реакція: автопілот сам виконує failsafe — повернення додому (RTL) чи м'яка посадка.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 296, "Головна думка: у реальному часі «правильно, але запізно» = неправильно. Дані керування мають дедлайн.",
              10, GREY, "middle", style="italic")
    save("fig-42-4-7-link-lost.svg", s)


# ============================================================================
#  §42.5 — MAVLink: структура пакета (heartbeat; повідомлення; ID; CRC)
# ============================================================================

def _frame(x, y, fields, scale=1.0):
    """fields: list of (label, sublabel, width, color)."""
    s = ""
    cx = x
    for lab, sub, w_, col in fields:
        fill = ("#eef2fb" if col == BLUE else ("#eef6ef" if col == GREEN else
                ("#fbf3df" if col == AMBER else ("#fbecec" if col == RED else "#f4f4f4"))))
        s += rect(cx, y, w_, 52 * scale, fill, col, 1.8, 3)
        s += text(cx + w_ / 2, y + 22 * scale, lab, 10.5, col, "middle", "bold")
        if sub:
            s += text(cx + w_ / 2, y + 40 * scale, sub, 8.5, GREY, "middle")
        cx += w_
    return s


# ── Рис. 42.5.1 — кадр MAVLink v1 ────────────────────────────────────────────
def fig51_packet():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Кадр MAVLink (v1): з чого складається пакет", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "невеликий заголовок + корисні дані + контрольна сума — зрілий нащадок пакета з Розділу 35",
              11, GREY, "middle", style="italic")
    fields = [
        ("STX", "0xFE", 70, BLUE),
        ("LEN", "довж.", 70, GREY),
        ("SEQ", "№", 60, GREY),
        ("SYS", "хто", 70, AMBER),
        ("COMP", "вузол", 80, AMBER),
        ("MSG ID", "тип", 90, RED),
        ("PAYLOAD", "дані (0–255 Б)", 280, GREEN),
        ("CRC", "2 Б", 80, BLUE),
    ]
    s += _frame(50, 120, fields)
    s += text(85, 110, "старт", 9, BLUE, "start")
    s += text(880, 110, "перевірка", 9, BLUE, "end")
    s += text(530, 192, "↑ корисні дані повідомлення (формат залежить від MSG ID)", 10, GREEN, "middle", "bold")
    s += rect(60, 230, W - 120, 70, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 254, "Заголовок (6 Б) + дані + CRC (2 Б). Усе двійкове, компактне — спроєктовано під вузький радіоканал.",
              11, INK, "middle", "bold")
    s += text(W / 2, 276, "Це точно той самий принцип, що ми будували для UART у §35.6: старт, довжина, дані, контрольна сума.",
              10, GREY, "middle", style="italic")
    save("fig-42-5-1-packet.svg", s)


# ── Рис. 42.5.2 — роль кожного поля ──────────────────────────────────────────
def fig52_fields():
    W, H = 960, 340
    s = header(W, H)
    s += text(W / 2, 34, "Що робить кожне поле заголовка", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен байт — з чіткою роллю; разом вони дають надійний, адресований, типізований пакет",
              11, GREY, "middle", style="italic")
    rows = [
        ("STX", "стартовий маркер — «тут починається пакет» (0xFE)", BLUE),
        ("LEN", "довжина даних — скільки байтів payload далі", GREY),
        ("SEQ", "лічильник — за розривами видно загублені пакети (§42.4)", GREY),
        ("SYS / COMP", "адреса — який апарат і який його вузол (як у §36)", AMBER),
        ("MSG ID", "тип повідомлення — heartbeat? attitude? GPS?", RED),
        ("PAYLOAD", "самі дані — поля залежать від типу", GREEN),
        ("CRC", "контрольна сума — чи не зіпсувалось (§35)", BLUE),
    ]
    y = 86
    for nm, desc, col in rows:
        s += rect(70, y, 150, 32, "#fbfbfb", col, 1.6, 5)
        s += text(145, y + 21, nm, 11, col, "middle", "bold")
        s += text(238, y + 21, desc, 11, INK, "start")
        y += 36
    save("fig-42-5-2-fields.svg", s)


# ── Рис. 42.5.3 — HEARTBEAT ──────────────────────────────────────────────────
def fig53_heartbeat():
    W, H = 960, 340
    s = header(W, H)
    s += text(W / 2, 34, "Найголовніше повідомлення: HEARTBEAT (ID 0)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«я живий» раз на секунду — кожна MAVLink-система мусить його слати",
              11.5, GREY, "middle", style="italic")
    s += circle(160, 170, 50, LRED, RED, 2)
    s += text(160, 166, "♥", 30, RED, "middle", "bold")
    s += text(160, 240, "~1 Гц", 11, RED, "middle", "bold")
    # поля payload
    s += text(300, 100, "що несе HEARTBEAT:", 12, INK, "start", "bold")
    fields = [("type", "тип апарата (квад, літак…)"), ("autopilot", "PX4 / ArduPilot…"),
              ("base_mode + custom_mode", "режим польоту"), ("system_status", "стан (armed?)"),
              ("mavlink_version", "версія протоколу")]
    y = 130
    for f, d in fields:
        s += circle(310, y - 4, 3.5, GREEN, GREEN, 0)
        s += text(326, y, f, 11, GREEN, "start", "bold")
        s += text(540, y, "— " + d, 10.5, INK, "start")
        y += 30
    s += rect(60, 286, W - 120, 44, LGRN, GREEN, 1.3, 9)
    s += text(W / 2, 310, "За HEARTBEAT станція ВИЯВЛЯЄ апарат, бачить його тип і режим — і ловить ВТРАТУ лінка (§42.4).",
              11, INK, "middle", "bold")
    save("fig-42-5-3-heartbeat.svg", s)


# ── Рис. 42.5.4 — ID і визначення (XML) ──────────────────────────────────────
def fig54_xml():
    W, H = 960, 330
    s = header(W, H)
    s += text(W / 2, 34, "Звідки беруться типи: визначення в XML → код", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "кожне повідомлення описане в XML (ID, ім'я, поля); з нього автоматично роблять код (C, Python)",
              10.5, GREY, "middle", style="italic")
    # XML блок
    s += rect(70, 90, 360, 200, "#1b1f24", INK, 1.5, 8)
    xml = ['<message id="30" name="ATTITUDE">', '  <field type="uint32_t" name="time"/>',
           '  <field type="float" name="roll"/>', '  <field type="float" name="pitch"/>',
           '  <field type="float" name="yaw"/>', '</message>']
    for i, ln in enumerate(xml):
        s += text(86, 118 + i * 26, ln, 10, "#9ec9ff" if "message" in ln else "#cfe8cf", "start")
    s += text(250, 308, "common.xml / ardupilotmega.xml (діалекти)", 9.5, GREY, "middle", style="italic")
    s += arrow(440, 190, 510, 190, INK, 2.4)
    s += text(475, 178, "генерує", 9, INK, "middle", "bold")
    # код
    s += rect(525, 110, 370, 160, "#fbfbfb", GREEN, 1.6, 8)
    s += text(710, 134, "автозгенерований кодек", 11, GREEN, "middle", "bold")
    for i, t in enumerate(["• бібліотеки для C, Python (pymavlink)…", "• пакують/розпаковують поля", "• ти не пишеш розбір руками", "• обидві сторони — з тих самих XML"]):
        s += text(545, 162 + i * 26, t, 10.3, INK, "start")
    save("fig-42-5-4-xml.svg", s)


# ── Рис. 42.5.5 — CRC і CRC_EXTRA ────────────────────────────────────────────
def fig55_crc():
    W, H = 960, 330
    s = header(W, H)
    s += text(W / 2, 34, "CRC + CRC_EXTRA: ловить і спотворення, і неузгодженість версій", 16.5, INK, "middle", "bold")
    s += text(W / 2, 56, "контрольна сума рахується ще й по «відбитку» структури повідомлення — хитрий запобіжник",
              10.5, GREY, "middle", style="italic")
    s += _frame(90, 110, [("заголовок+дані", "", 360, GREY), ("+CRC_EXTRA", "відбиток типу", 180, AMBER)], 0.9)
    s += arrow(640, 130, 700, 130, INK, 2.2)
    s += rect(705, 110, 170, 48, "#eef2fb", BLUE, 1.8, 6)
    s += text(790, 140, "CRC (2 Б)", 12, BLUE, "middle", "bold")
    s += text(270, 200, "CRC_EXTRA — байт, похідний від полів повідомлення", 10.5, AMBER, "middle", "bold")
    s += rect(60, 226, W - 120, 80, LGRN, GREEN, 1.3, 9)
    s += text(W / 2, 250, "Якщо в двох сторін РІЗНІ визначення повідомлення (різні версії XML) — CRC не зійдеться,",
              11, INK, "middle", "bold")
    s += text(W / 2, 270, "і пакет відкинуть. Тобто CRC ловить і радіошум (§35), і «розмову різними діалектами».",
              11, INK, "middle", "bold")
    s += text(W / 2, 292, "Геніально просто: одна перевірка стереже одразу цілісність і сумісність.", 10, GREY, "middle", style="italic")
    save("fig-42-5-5-crc.svg", s)


# ── Рис. 42.5.6 — адресація SYS/COMP ─────────────────────────────────────────
def fig56_addressing():
    W, H = 960, 330
    s = header(W, H)
    s += text(W / 2, 34, "Адресація: хто кому (SYS / COMP)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "одна лінія, багато апаратів і вузлів — кожен має адресу (як на шині §36)",
              11.5, GREY, "middle", style="italic")
    # апарат 1
    s += _drone(190, 150, 1.1, BLUE)
    s += text(190, 205, "SYS 1 (дрон №1)", 10, BLUE, "middle", "bold")
    comps = [("автопілот", "COMP 1"), ("підвіс", "COMP 154"), ("камера", "COMP 100")]
    for i, (nm, cid) in enumerate(comps):
        s += rect(360, 100 + i * 50, 180, 38, "#fbfbfb", AMBER, 1.5, 6)
        s += text(450, 118 + i * 50, nm, 10.5, INK, "middle", "bold")
        s += text(450, 132 + i * 50, cid, 9, AMBER, "middle")
    s += text(450, 92, "вузли всередині апарата", 9.5, GREY, "middle")
    # станція
    s += rect(640, 130, 150, 60, "#fbfbfb", GREEN, 1.6, 8)
    s += text(715, 165, "станція\n(SYS 255)", 10, GREEN, "middle", "bold") if False else ""
    s += text(715, 158, "станція", 11, GREEN, "middle", "bold")
    s += text(715, 176, "SYS 255", 9.5, GREEN, "middle")
    s += arrow(560, 155, 635, 155, GREY, 1.6)
    s += rect(60, 250, W - 120, 56, LAMB, AMBER, 1.3, 9)
    s += text(W / 2, 274, "SYS = який апарат, COMP = який його вузол. Так на одній лінії вживаються кілька дронів і пристроїв,",
              11, INK, "middle", "bold")
    s += text(W / 2, 294, "і кожне повідомлення знає, від кого воно й кому. Точно як адреси на шині I2C (§36).",
              10, GREY, "middle", style="italic")
    save("fig-42-5-6-addressing.svg", s)


# ── Рис. 42.5.7 — v1 проти v2 ────────────────────────────────────────────────
def fig57_v1_v2():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "MAVLink v1 і v2: що додала нова версія", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "v2 (старт 0xFD) сумісна за духом, але зручніша й безпечніша",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 86, 400, 200, "#fbfbfb", GREY, 1.6, 10)
    s += text(260, 112, "v1 (0xFE)", 12.5, INK, "middle", "bold")
    for i, t in enumerate(["• ID типу — 1 байт (до 256 типів)", "• простий заголовок 6 Б + CRC", "• без автентифікації", "• payload завжди повний"]):
        s += text(80, 142 + i * 30, t, 10.5, INK, "start")
    s += rect(500, 86, 400, 200, "#fbfbfb", GREEN, 1.6, 10)
    s += text(700, 112, "v2 (0xFD)", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• ID типу — 24 біти (мільйони!)", "• прапорці сумісності", "• підпис (signing) — захист від підробки", "• обрізання нулів payload → коротше"]):
        s += text(520, 142 + i * 30, t, 10.5, INK, "start")
    s += text(W / 2, 306, "Ідея незмінна — кадр з ID і CRC; v2 лише розширює простір типів, додає безпеку й трохи економить ефір.",
              10.5, INK, "middle", "bold")
    save("fig-42-5-7-v1-v2.svg", s)


# ============================================================================
#  §42.6 — Читання потоку й надсилання команд
# ============================================================================

# ── Рис. 42.6.1 — цикл приймання ─────────────────────────────────────────────
def fig61_receive():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Читання потоку: байти → парсер → готові повідомлення", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "приймач збирає кадри з потоку байтів і віддає вже розкладені поля — реагуй на них у циклі",
              10.5, GREY, "middle", style="italic")
    blocks = [("потік байтів", "…FE 09 00…", GREY), ("парсер MAVLink", "збирає кадри", AMBER),
              ("повідомлення", "msg.roll, msg.lat", GREEN), ("твоя реакція", "цикл подій", BLUE)]
    x = 50
    bw = 200
    y = 110
    for i, (nm, sub, col) in enumerate(blocks):
        s += rect(x, y, bw, 70, "#fbfbfb", col, 1.8, 8)
        s += text(x + bw / 2, y + 32, nm, 12, col, "middle", "bold")
        s += text(x + bw / 2, y + 53, sub, 9.5, GREY, "middle")
        if i < len(blocks) - 1:
            s += arrow(x + bw + 2, y + 35, x + bw + 18, y + 35, INK, 2)
        x += bw + 20
    s += rect(60, 222, W - 120, 82, "#1b1f24", INK, 1.5, 9)
    code = ["master.wait_heartbeat()              # 1) дочекатися апарата",
            "msg = master.recv_match('ATTITUDE')  # 2) узяти повідомлення",
            "print(msg.roll, msg.pitch, msg.yaw)  # 3) працювати з полями"]
    for i, ln in enumerate(code):
        s += text(80, 246 + i * 20, ln, 11, "#cfe8cf", "start")
    save("fig-42-6-1-receive.svg", s)


# ── Рис. 42.6.2 — запит даних ────────────────────────────────────────────────
def fig62_request():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Спершу попроси: апарат не шле все підряд", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "щоб не забивати вузький канал, потрібні повідомлення замовляють із потрібною частотою",
              10.5, GREY, "middle", style="italic")
    s += _drone(180, 160, 1.2, BLUE)
    s += text(180, 220, "апарат", 10.5, BLUE, "middle", "bold")
    s += rect(720, 130, 160, 70, "#fbfbfb", GREEN, 1.6, 8)
    s += text(800, 168, "твій код / GCS", 10.5, GREEN, "middle", "bold")
    s += arrow(720, 130, 230, 130, GREEN, 2.2)
    s += text(470, 116, "«шли ATTITUDE 10 разів/с» (SET_MESSAGE_INTERVAL)", 10, GREEN, "middle", "bold")
    s += arrow(230, 185, 720, 185, AMBER, 2.2)
    s += text(470, 205, "→ пішов потік ATTITUDE", 10, AMBER, "middle", "bold")
    s += rect(60, 240, W - 120, 64, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 264, "MAV_CMD_SET_MESSAGE_INTERVAL (v2) або REQUEST_DATA_STREAM (старий v1) — задають, ЩО і ЯК ЧАСТО слати.",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 286, "Це і є ті «частоти потоку» (stream rate) з §42.3 — тепер ти керуєш ними сам.", 10, GREY, "middle", style="italic")
    save("fig-42-6-2-request.svg", s)


# ── Рис. 42.6.3 — команда й ACK ──────────────────────────────────────────────
def fig63_command_ack():
    W, H = 960, 330
    s = header(W, H)
    s += text(W / 2, 34, "Надсилання команди: COMMAND_LONG → COMMAND_ACK", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "шлеш команду з ID і параметрами — і ЧЕКАЄШ підтвердження (це ACK із §42.4)",
              10.5, GREY, "middle", style="italic")
    s += rect(60, 110, 160, 70, "#fbfbfb", GREEN, 1.6, 8)
    s += text(140, 142, "твій код", 11, GREEN, "middle", "bold")
    s += text(140, 160, "(GCS)", 9, GREY, "middle")
    s += _drone(820, 145, 1.1, BLUE)
    s += text(820, 200, "апарат", 10, BLUE, "middle", "bold")
    s += arrow(225, 130, 760, 130, RED, 2.2)
    s += text(490, 116, "COMMAND_LONG: cmd=ARM_DISARM, param1=1", 10.5, RED, "middle", "bold")
    s += arrow(760, 170, 225, 170, GREEN, 2.2)
    s += text(490, 190, "COMMAND_ACK: result = ACCEPTED ✓", 10.5, GREEN, "middle", "bold")
    s += rect(60, 222, W - 120, 84, "#1b1f24", INK, 1.5, 9)
    code = ["master.mav.command_long_send(sys, comp,",
            "    MAV_CMD_COMPONENT_ARM_DISARM, 0, 1,0,0,0,0,0,0)  # 1 = armed",
            "ack = master.recv_match(type='COMMAND_ACK', blocking=True)"]
    for i, ln in enumerate(code):
        s += text(80, 246 + i * 20, ln, 10.5, "#cfe8cf", "start")
    save("fig-42-6-3-command-ack.svg", s)


# ── Рис. 42.6.4 — типові команди ─────────────────────────────────────────────
def fig64_commands():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Кілька найужитковіших команд", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усе це — COMMAND_LONG/INT з різними ID; апарат відповідає ACK",
              11, GREY, "middle", style="italic")
    cmds = [
        ("ARM / DISARM", "COMPONENT_ARM_DISARM", "увімкнути/вимкнути мотори", RED),
        ("Режим", "DO_SET_MODE / SET_MODE", "AUTO, LOITER, RTL…", BLUE),
        ("Зліт", "NAV_TAKEOFF", "піднятися на висоту", GREEN),
        ("Додому", "NAV_RETURN_TO_LAUNCH", "повернутися й сісти", AMBER),
    ]
    x0, y0 = 70, 88
    for i, (nm, cid, desc, col) in enumerate(cmds):
        cx = x0 + (i % 2) * 430
        cy = y0 + (i // 2) * 96
        s += rect(cx, cy, 410, 82, "#fbfbfb", col, 1.7, 9)
        s += text(cx + 18, cy + 30, nm, 13, col, "start", "bold")
        s += text(cx + 18, cy + 52, "MAV_CMD_" + cid, 10, GREY, "start")
        s += text(cx + 18, cy + 70, desc, 10.5, INK, "start")
        x0 = 70
    s += text(W / 2, 300, "⚠ Кожна така команда РЕАЛЬНО рухає апарат. Спершу — на симуляторі чи зі знятими гвинтами (далі).",
              10.5, RED, "middle", "bold")
    save("fig-42-6-4-commands.svg", s)


# ── Рис. 42.6.5 — параметри ──────────────────────────────────────────────────
def fig65_params():
    W, H = 960, 310
    s = header(W, H)
    s += text(W / 2, 34, "Читання й запис параметрів", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "налаштування апарата (сотні параметрів) теж доступні через MAVLink — з підтвердженням",
              11, GREY, "middle", style="italic")
    s += rect(60, 90, 410, 180, "#fbfbfb", BLUE, 1.6, 9)
    s += text(265, 116, "Прочитати", 12, BLUE, "middle", "bold")
    s += text(80, 146, "→ PARAM_REQUEST_READ (ім'я)", 10.5, INK, "start")
    s += text(80, 172, "→ PARAM_REQUEST_LIST (усі)", 10.5, INK, "start")
    s += text(80, 206, "← PARAM_VALUE: значення", 10.5, GREEN, "start", "bold")
    s += text(80, 232, "  (напр. WPNAV_SPEED = 500)", 9.5, GREY, "start")
    s += rect(490, 90, 410, 180, "#fbfbfb", GREEN, 1.6, 9)
    s += text(695, 116, "Записати", 12, GREEN, "middle", "bold")
    s += text(510, 146, "→ PARAM_SET (ім'я, нове значення)", 10.5, INK, "start")
    s += text(510, 180, "← PARAM_VALUE: підтвердження", 10.5, GREEN, "start", "bold")
    s += text(510, 206, "  (апарат відповідає новим значенням)", 9.5, GREY, "start")
    s += text(510, 240, "так GCS і налаштовує апарат", 9.5, GREY, "start", style="italic")
    save("fig-42-6-5-params.svg", s)


# ── Рис. 42.6.6 — завантаження місії ─────────────────────────────────────────
def fig66_mission():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Завантаження місії: рукостискання пункт за пунктом", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "маршрут вантажать надійно — з підтвердженням кожної точки (надійність важливіша за швидкість, §42.4)",
              10, GREY, "middle", style="italic")
    s += rect(60, 100, 150, 60, "#fbfbfb", GREEN, 1.6, 8)
    s += text(135, 135, "твій код", 10.5, GREEN, "middle", "bold")
    s += _drone(840, 130, 1.0, BLUE)
    seq = [("MISSION_COUNT = 3", RED, 100), ("← MISSION_REQUEST (0)", GREEN, 124),
           ("MISSION_ITEM_INT (0)", RED, 148), ("← REQUEST (1) …", GREEN, 172),
           ("… ITEM (2)", RED, 196), ("← MISSION_ACK ✓", GREEN, 220)]
    for t, col, y in seq:
        if t.startswith("←"):
            s += arrow(770, y, 230, y, col, 1.8)
            s += text(500, y - 4, t, 9.5, col, "middle", "bold")
        else:
            s += arrow(220, y, 760, y, col, 1.8)
            s += text(500, y - 4, t, 9.5, col, "middle", "bold")
    s += rect(60, 244, W - 120, 60, LAMB, AMBER, 1.3, 9)
    s += text(W / 2, 268, "Станція каже «маршрут із N точок», апарат просить їх по черзі, кожну підтверджують — і наприкінці ACK.",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 288, "Жодна точка не загубиться — це та сама «надійна» стратегія з §42.4.", 9.5, GREY, "middle", style="italic")
    save("fig-42-6-6-mission.svg", s)


# ── Рис. 42.6.7 — безпека: SITL і стенд ──────────────────────────────────────
def fig67_sitl():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Спершу — безпечно: симулятор і зняті гвинти", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "команди рухають РЕАЛЬНИЙ апарат; вчися там, де помилка не коштує аварії",
              11, GREY, "middle", style="italic")
    cards = [
        ("🖥️", "SITL (симулятор)", "PX4 й ArduPilot мають віртуальний апарат: твій код керує ним без жодного заліза й ризику.", GREEN),
        ("🔧", "Стенд без гвинтів", "На реальній платі спершу пробуй зі ЗНЯТИМИ пропелерами — мотори крутяться, апарат нікуди не злетить.", BLUE),
        ("📋", "Тільки потім — політ", "Перевірив у симуляторі й на стенді — аж тоді обережний політ на відкритому, безпечному місці.", AMBER),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 84, 290, 210, "#fbfbfb", col, 2, 12)
        s += text(x + 145, 124, ico, 22, INK, "middle")
        s += text(x + 145, 152, title, 12.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 180
        for wd in words:
            if len(ln) + len(wd) > 32:
                s += text(x + 145, yy, ln.strip(), 10, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 145, yy, ln.strip(), 10, INK, "middle")
        x += 305
    save("fig-42-6-7-sitl.svg", s)


# ============================================================================
#  §42.7 — Автоматизація: pymavlink (місток до бортового комп'ютера)
# ============================================================================

# ── Рис. 42.7.1 — pymavlink ──────────────────────────────────────────────────
def fig71_pymavlink():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "pymavlink: MAVLink у Python кількома рядками", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама бібліотека, що ми вже бачили (§42.6) — згенерована з тих самих XML (§42.5)",
              10.5, GREY, "middle", style="italic")
    s += rect(60, 90, 600, 130, "#1b1f24", INK, 1.5, 9)
    code = ["from pymavlink import mavutil",
            "m = mavutil.mavlink_connection('udp:127.0.0.1:14550')",
            "m.wait_heartbeat()                # апарат на лінії",
            "while True:",
            "    msg = m.recv_match(blocking=True)   # читай усе підряд",
            "    # …реагуй, шли команди, веди логіку…"]
    for i, ln in enumerate(code):
        s += text(80, 116 + i * 18, ln, 10.5, "#cfe8cf", "start")
    s += rect(690, 90, 210, 130, "#fbfbfb", GREEN, 1.6, 9)
    s += text(795, 116, "що дає pymavlink:", 10.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• з'єднання (serial/", "  udp/tcp)", "• розбір і пакування", "• усі діалекти", "• основа MAVProxy"]):
        s += text(706, 142 + i * 16, t, 9.3, INK, "start")
    s += rect(60, 240, W - 120, 60, LGRN, GREEN, 1.3, 9)
    s += text(W / 2, 264, "pymavlink — стандартний спосіб говорити з MAVLink на Python; саме його написав Ендрю Тридджелл (історія).",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 285, "Той самий код працює і з ноутбука, і — головне — з бортового комп'ютера на самому апараті.",
              10, GREY, "middle", style="italic")
    save("fig-42-7-1-pymavlink.svg", s)


# ── Рис. 42.7.2 — бортовий комп'ютер ─────────────────────────────────────────
def fig72_companion():
    W, H = 960, 330
    s = header(W, H)
    s += text(W / 2, 34, "Бортовий комп'ютер: розум прямо на апараті", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "маленький Linux-комп'ютер поряд із контролером, з'єднаний КОРОТКИМ UART — без жодного радіо",
              10.5, GREY, "middle", style="italic")
    s += _drone(480, 130, 1.6, BLUE)
    # FC
    s += rect(330, 200, 130, 60, "#fbfbfb", RED, 1.8, 8)
    s += text(395, 226, "політний", 10.5, RED, "middle", "bold")
    s += text(395, 244, "контролер", 10.5, RED, "middle", "bold")
    # companion
    s += rect(500, 200, 150, 60, "#fbfbfb", GREEN, 1.8, 8)
    s += text(575, 222, "бортовий комп'ютер", 9.5, GREEN, "middle", "bold")
    s += text(575, 240, "Raspberry Pi / Jetson", 8.5, GREY, "middle")
    s += line(460, 230, 500, 230, INK, 3)
    s += text(480, 222, "UART", 8, INK, "middle", "bold")
    s += text(480, 282, "MAVLink по короткому дроту — швидко, надійно, без ефіру", 10, INK, "middle", "bold")
    s += rect(60, 296, W - 120, 1, "none", "none", 0)
    save("fig-42-7-2-companion.svg", s)


# ── Рис. 42.7.3 — поділ праці ────────────────────────────────────────────────
def fig73_architecture():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Поділ праці: політ окремо, розум окремо", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "контролер відповідає за політ у реальному часі; комп'ютер — за «думання»; між ними MAVLink",
              10.5, GREY, "middle", style="italic")
    s += rect(70, 90, 360, 190, "#fbfbfb", RED, 1.8, 10)
    s += text(250, 116, "Політний контролер", 12.5, RED, "middle", "bold")
    for i, t in enumerate(["• стабілізація, реальний час", "• читання давачів, мотори", "• надійність понад усе", "• проста, перевірена логіка"]):
        s += text(90, 146 + i * 28, t, 10.5, INK, "start")
    s += rect(530, 90, 360, 190, "#fbfbfb", GREEN, 1.8, 10)
    s += text(710, 116, "Бортовий комп'ютер", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• комп'ютерний зір, ШІ", "• складні рішення, маршрути", "• зв'язок (LTE, мережа)", "• важкі обчислення"]):
        s += text(550, 146 + i * 28, t, 10.5, INK, "start")
    s += arrow(430, 170, 530, 170, AMBER, 2.4)
    s += arrow(530, 200, 430, 200, AMBER, 2.4)
    s += text(480, 160, "MAVLink", 9.5, AMBER, "middle", "bold")
    s += text(W / 2, 304, "Контролер — «спинний мозок» (рефлекси польоту); комп'ютер — «головний мозок» (зір і плани).",
              10.5, INK, "middle", "bold")
    save("fig-42-7-3-architecture.svg", s)


# ── Рис. 42.7.4 — повне коло до історії ──────────────────────────────────────
def fig74_full_circle():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Повне коло: мрія Маєра нарешті здійснюється", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "MAVLink творили заради дрона з комп'ютерним зором — і тепер цей зір живе на борту",
              10.5, GREY, "middle", style="italic")
    s += rect(70, 96, 250, 150, "#fbfbfb", BLUE, 1.8, 10)
    s += text(195, 124, "2008: МЕТА", 11.5, BLUE, "middle", "bold")
    s += text(195, 150, "дрон, що сам бачить", 10, INK, "middle")
    s += text(195, 168, "і літає (зір)", 10, INK, "middle")
    s += text(195, 196, "MAVLink — лише", 9.5, GREY, "middle", style="italic")
    s += text(195, 212, "побічний інструмент", 9.5, GREY, "middle", style="italic")
    s += arrow(325, 171, 385, 171, INK, 2.4)
    s += text(355, 160, "роки", 8.5, GREY, "middle")
    s += rect(400, 96, 250, 150, "#fbfbfb", GREEN, 1.8, 10)
    s += text(525, 124, "сьогодні", 11.5, GREEN, "middle", "bold")
    s += text(525, 150, "бортовий комп'ютер +", 10, INK, "middle")
    s += text(525, 168, "pymavlink + зір/ШІ", 10, INK, "middle")
    s += text(525, 196, "= та сама автономність,", 9.5, GREEN, "middle", "bold")
    s += text(525, 212, "якої він прагнув", 9.5, GREEN, "middle", "bold")
    s += rect(680, 96, 220, 150, LAMB, AMBER, 1.6, 10)
    s += text(790, 124, "іронія долі:", 11, AMBER, "middle", "bold")
    s += text(790, 150, "«побічний» MAVLink", 9.5, INK, "middle")
    s += text(790, 168, "став тим містком,", 9.5, INK, "middle")
    s += text(790, 186, "що уможливив", 9.5, INK, "middle")
    s += text(790, 204, "початкову мрію", 9.5, INK, "middle")
    s += text(W / 2, 296, "Інструмент, зроблений «між іншим», тепер несе той самий зір, заради якого все й починалося.",
              10.5, INK, "middle", "bold")
    save("fig-42-7-4-full-circle.svg", s)


# ── Рис. 42.7.5 — сценарії автоматизації ─────────────────────────────────────
def fig75_scenarios():
    W, H = 960, 330
    s = header(W, H)
    s += text(W / 2, 34, "Що можна автоматизувати з pymavlink на борту", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "читай телеметрію, ухвалюй рішення, шли команди — без участі землі",
              11, GREY, "middle", style="italic")
    cards = [
        ("🔋", "Розумний failsafe", "сів заряд → сам шле RTL", AMBER),
        ("🎯", "Слідкування за ціллю", "зір бачить об'єкт → коригує курс", GREEN),
        ("🧱", "Геозона", "наблизився до межі → не пускає далі", RED),
        ("🗺️", "Авто-картографування", "облітає площу й знімає за планом", BLUE),
    ]
    x = 40
    for ico, title, body, col in cards:
        s += rect(x, 86, 220, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 110, 126, ico, 22, INK, "middle")
        s += text(x + 110, 154, title, 12, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 184
        for wd in words:
            if len(ln) + len(wd) > 22:
                s += text(x + 110, yy, ln.strip(), 9.8, INK, "middle")
                ln, yy = "", yy + 17
            ln += wd + " "
        s += text(x + 110, yy, ln.strip(), 9.8, INK, "middle")
        x += 230
    s += text(W / 2, 312, "Усе це — той самий цикл «читай → вирішуй → командуй» (§42.6), але на самому апараті й без людини.",
              10.5, INK, "middle", "bold")
    save("fig-42-7-5-scenarios.svg", s)


# ── Рис. 42.7.6 — екосистема й місток далі ───────────────────────────────────
def fig76_ecosystem():
    W, H = 960, 320
    s = header(W, H)
    s += text(W / 2, 34, "Куди далі: від pymavlink до великої робототехніки", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "над MAVLink виросла ціла екосистема інструментів — місток у Модуль 7 і ROS",
              11, GREY, "middle", style="italic")
    items = [
        ("MAVProxy", "командний GCS на pymavlink (Тридж)", BLUE),
        ("DroneKit / MAVSDK", "вищі рівні API для автоматизації", GREEN),
        ("MAVROS", "міст MAVLink ↔ ROS — велика робототехніка", AMBER),
    ]
    y = 92
    for nm, desc, col in items:
        s += rect(80, y, 250, 56, "#fbfbfb", col, 1.6, 9)
        s += text(205, y + 34, nm, 12.5, col, "middle", "bold")
        s += arrow(335, y + 28, 365, y + 28, INK, 1.6)
        s += rect(370, y, 510, 56, "#f7f7f7", col, 1.3, 9)
        s += text(390, y + 34, desc, 11, INK, "start")
        y += 70
    s += text(W / 2, 304, "Усе це стоїть на тому самому MAVLink, що ми розібрали. Далі — Модуль 7: ArduPilot, відео, машинне бачення.",
              10.5, INK, "middle", "bold")
    save("fig-42-7-6-ecosystem.svg", s)


# ── Рис. 42.7.7 — підсумок Модуля 6 ──────────────────────────────────────────
def fig77_module_recap():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 36, "Модуль 6 пройдено: від двох дротів до автономного апарата", 18, INK, "middle", "bold")
    s += text(W / 2, 58, "увесь шлях зв'язку — дротовий, бездротовий, радіо й системний — в одному погляді",
              11, GREY, "middle", style="italic")
    chapters = [
        ("35", "UART", "послідовно по двох дротах", GREEN),
        ("36", "I2C", "шина: адреси, такт", GREEN),
        ("37", "SPI", "швидка повнодуплексна шина", GREEN),
        ("38", "Wi-Fi / BT", "радіо на чіпі", BLUE),
        ("39", "Фізика радіо", "ЕМ-хвиля, дБ, загасання", BLUE),
        ("40", "Модуляція / бюджет", "AM-FM, Шеннон, спектр", AMBER),
        ("41", "Антени", "λ/4, патерн, 50 Ом, КСХ", AMBER),
        ("42", "MAVLink / система", "керування, телеметрія, код", RED),
    ]
    cols = 4
    cw, ch = 220, 110
    x0, y0 = 25, 86
    for i, (n, nm, sub, col) in enumerate(chapters):
        cx = x0 + (i % cols) * (cw + 8)
        cy = y0 + (i // cols) * (ch + 16)
        s += rect(cx, cy, cw, ch, "#fbfbfb", col, 1.8, 10)
        s += circle(cx + 30, cy + 32, 18, col, col, 0)
        s += text(cx + 30, cy + 38, n, 13, "#fff", "middle", "bold")
        s += text(cx + 56, cy + 38, nm, 13, col, "start", "bold")
        words = sub.split()
        ln, yy = "", cy + 66
        for wd in words:
            if len(ln) + len(wd) > 26:
                s += text(cx + cw / 2, yy, ln.strip(), 9.8, INK, "middle")
                ln, yy = "", yy + 16
            ln += wd + " "
        s += text(cx + cw / 2, yy, ln.strip(), 9.8, INK, "middle")
    s += rect(60, 366, W - 120, 44, LGRN, GREEN, 1.5, 10)
    s += text(W / 2, 391, "Тепер зв'язок — від двох дротів до автономного апарата — для тебе не магія, а зрозуміла, прорахована інженерія.",
              11, INK, "middle", "bold")
    save("fig-42-7-7-module-recap.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    figh_timeline()
    figh_problem()
    figh_mavlink_idea()
    figh_by_accident()
    figh_collective()
    figh_open()
    figh_legacy()
    # — §42.1 —
    fig11_two_links()
    fig12_control()
    fig13_telemetry()
    fig14_video()
    fig15_why_separate()
    fig16_requirements()
    fig17_convergence()
    # — §42.2 —
    fig21_channels()
    fig22_chain()
    fig23_binding()
    fig24_pwm_ppm()
    fig25_sbus_crsf()
    fig26_systems()
    fig27_failsafe()
    # — §42.3 —
    fig31_air_ground()
    fig32_bridge()
    fig33_stream()
    fig34_bidirectional()
    fig35_sik()
    fig36_topologies()
    fig37_gcs()
    # — §42.4 —
    fig41_latency_chain()
    fig42_feedback()
    fig43_reliability()
    fig44_strategies()
    fig45_tradeoff()
    fig46_range()
    fig47_link_lost()
    # — §42.5 —
    fig51_packet()
    fig52_fields()
    fig53_heartbeat()
    fig54_xml()
    fig55_crc()
    fig56_addressing()
    fig57_v1_v2()
    # — §42.6 —
    fig61_receive()
    fig62_request()
    fig63_command_ack()
    fig64_commands()
    fig65_params()
    fig66_mission()
    fig67_sitl()
    # — §42.7 —
    fig71_pymavlink()
    fig72_companion()
    fig73_architecture()
    fig74_full_circle()
    fig75_scenarios()
    fig76_ecosystem()
    fig77_module_recap()
    print("done.")
