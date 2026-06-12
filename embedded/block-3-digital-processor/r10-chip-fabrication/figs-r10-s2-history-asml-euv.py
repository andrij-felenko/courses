# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до теми 3.10.2 — «Фотолітографія»
(Розділ 3.10 «Як народжується чіп», Модуль 3): ASML і EUV — світло 13.5 нм
з олов'яної плазми й чому це найскладніша машина у виробництві.

ОКРЕМИЙ скрипт лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи історії до теми — секція «h»: Рис. 3.10.2h.k → файли fig-r10-s2h-k-*.
Допоміжні функції — копія спільних із рештою розділів, щоб вигляд був єдиний.
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
AMBER = "#caa24a"
PURPLE = "#6a3da0"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill="none", stroke=INK, w=2):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ═══════════ Рис. 3.10.2h.1 — таймлайн довгого шляху EUV ════════════════════
def fig_timeline():
    W, H = 940, 760
    s = header(W, H)
    s += text(W / 2, 38, "Довгий шлях EUV: від однієї ідеї 1986-го до фабрики 2019-го",
              20, INK, "middle", "bold")
    s += text(W / 2, 60, "понад тридцять років, мільярди доларів і коаліція лабораторій та фірм — щоб надрукувати схему світлом 13.5 нм",
              12, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 24
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("сер. 1980-х", "Кіношіта (NTT, Японія) висуває ідею",
         "Хіроо Кіношіта (Hiroo Kinoshita) пропонує літографію в м'якому рентгені; 1986-го вперше фокусує EUV-зображення дзеркалами", BLUE),
        ("1980-ті", "Андервуд і Барбі — перші багатошарові дзеркала",
         "Джим Андервуд (Jim Underwood) і Трой Барбі (Troy Barbee) роблять перші Mo/Si-дзеркала, що взагалі відбивають EUV — без них ідея мертва", BLUE),
        ("сер. 1980-х", "Bell Labs пробує плазмове джерело",
         "Оберт Вуд (Obert Wood) і Білл Сілфваст (Bill Silfvast) запускають лазерну плазму як джерело EUV; Рік Фрімен пізніше вводить сам термін «EUV-літографія»", BLUE),
        ("1992–94", "Intel і нацлабораторії США беруться всерйоз",
         "Intel вкладає сотні мільйонів; Лівермор, Сандія, Берклі (Livermore, Sandia, Berkeley) ведуть дослідження під DARPA/DOE", AMBER),
        ("1997", "консорціум EUV-LLC",
         "Intel збирає коаліцію (AMD, Motorola, IBM, Micron) і фінансує нацлабораторії — переносить науку ближче до виробництва", AMBER),
        ("кінець 1990-х", "ASML бере EUV у роботу",
         "Європейська ASML робить ставку на EUV як наступника DUV; партнерство з Zeiss по оптиці й Cymer по джерелу світла", GREEN),
        ("2012", "Zeiss віддає ASML першу штатну оптику",
         "Карл Цайс (Zeiss) розв'язує найстрашнішу задачу — дзеркала такої гладкості, що оптика перестає бути головним бар'єром", GREEN),
        ("2013", "ASML купує Cymer; джерело пробиває 10 Вт",
         "Cymer додає попередній імпульс, що розплескує краплю олова, — і потужність нарешті росте; у травні ASML купує Cymer", GREEN),
        ("2018–2019", "EUV у серійному виробництві",
         "Перші чіпи масово друкують на EUV (Samsung, TSMC). Понад 30 років роботи дають робочу машину", GREEN),
    ]
    n = len(nodes)
    for i, (yr, who, q, col) in enumerate(nodes):
        y = top + 26 + (bot - top - 52) * i / (n - 1)
        win = ("серійн" in who) or ("Cymer" in who and "купує" in who)
        if win:
            s += circle(spine, y, 11, "#fff", GREEN, 0)
            s += circle(spine, y, 10, "none", GREEN, 3.2)
            s += circle(spine, y, 4.5, GREEN, GREEN, 1)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 14.5, col, "start", "bold")
        for j, ln in enumerate(_wrap(q, 70)):
            s += text(spine + 26, y + 16 + j * 16, ln, 11.5, INK, "start", style="italic")
    save("fig-r10-s2h-1-timeline.svg", s)


# ═══════════ Рис. 3.10.2h.2 — фізика джерела світла ════════════════════════
def fig_source():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 36, "Як народжується світло 13.5 нм: крапля олова під подвійним пострілом лазера",
              19, INK, "middle", "bold")
    s += text(W / 2, 58, "ні лампи, ні лазера на 13.5 нм не існує — світло «викрешують» з плазми олова десятки тисяч разів за секунду",
              11.5, GREY, "middle", style="italic")

    # горизонтальна вісь часу / руху краплі
    lane = 160
    s += line(70, lane, 870, lane, FAINT, 1.6, "4 4")
    s += text(70, 96, "Один цикл — і так ~50 000 разів за секунду:", 13, INK, "start", "bold")

    # стадія 1: летить крапля
    x1 = 165
    s += text(x1, lane + 70, "1. летить крапля", 12.5, INK, "middle", "bold")
    s += circle(x1, lane, 13, "#dfe3ea", BLUE, 2)
    s += text(x1, lane + 4, "Sn", 11, BLUE, "middle", "bold")
    s += arrow(x1 - 38, lane, x1 - 18, lane, INK, 2)
    s += text(x1, lane + 92, "розплавлене олово,", 10.5, GREY, "middle")
    s += text(x1, lane + 107, "крапля ~25–30 мкм", 10.5, GREY, "middle")

    # стадія 2: попередній імпульс розплескує
    x2 = 400
    s += text(x2, lane + 70, "2. попередній імпульс", 12.5, RED, "middle", "bold")
    # тонкий лазерний промінь зліва
    s += arrow(x2 - 120, lane, x2 - 26, lane, RED, 2.4)
    s += text(x2 - 73, lane - 10, "слабкий", 9.5, RED, "middle")
    # розплесканий «млинець»
    s += path(f"M{x2-22},{lane} Q{x2},{lane-9} {x2+22},{lane} Q{x2},{lane+9} {x2-22},{lane} Z",
              "#dfe3ea", BLUE, 2)
    s += text(x2, lane + 92, "крапля стає пласким", 10.5, GREY, "middle")
    s += text(x2, lane + 107, "«млинцем» — більша ціль", 10.5, GREY, "middle")

    # стадія 3: головний імпульс -> плазма -> EUV
    x3 = 680
    s += text(x3, lane + 70, "3. головний імпульс CO₂", 12.5, RED, "middle", "bold")
    s += arrow(x3 - 130, lane, x3 - 30, lane, RED, 3.4)
    s += text(x3 - 80, lane - 10, "потужний", 9.5, RED, "middle")
    # плазмова куля
    s += circle(x3, lane, 22, "#fff3d6", AMBER, 0)
    s += circle(x3, lane, 16, "#ffe8a8", AMBER, 0)
    s += circle(x3, lane, 9, "#fff", AMBER, 0)
    # промені EUV навсібіч
    for a in range(0, 360, 30):
        rad = math.radians(a)
        s += line(x3 + 22 * math.cos(rad), lane + 22 * math.sin(rad),
                  x3 + 40 * math.cos(rad), lane + 40 * math.sin(rad), AMBER, 2)
    s += text(x3, lane + 92, "плазма ~ десятки тисяч °C", 10.5, GREY, "middle")
    s += text(x3, lane + 107, "світить на 13.5 нм (EUV)", 10.5, AMBER, "middle", )

    # стрілки переходів між стадіями
    s += arrow(x1 + 60, lane - 36, x2 - 60, lane - 36, GREY, 1.8)
    s += arrow(x2 + 70, lane - 36, x3 - 70, lane - 36, GREY, 1.8)

    # нижній пояснювальний блок
    by = lane + 150
    s += rect(70, by, W - 140, 92, "#fbf7ee", AMBER, 1.6, 10)
    s += text(90, by + 26, "Чому так дивно, а не просто «увімкнути лампу»?", 13, INK, "start", "bold")
    for i, t in enumerate([
        "• На 13.5 нм НЕ світить жодна лампа й жоден лазер: цю довжину хвилі доводиться добувати з гарячої плазми.",
        "• Один CO₂-лазер мегаватного класу влучає в КОЖНУ краплю; попередній імпульс спершу розплескує її, щоб віддача світла зросла.",
        "• Лише ~кілька відсотків енергії лазера стає корисним EUV — решта йде в тепло. Звідси гігантські лазер і охолодження.",
    ]):
        s += text(90, by + 48 + i * 17, t, 11, INK, "start")
    save("fig-r10-s2h-2-source.svg", s)


# ═══════════ Рис. 3.10.2h.3 — бюджет фотонів крізь дзеркала ════════════════
def fig_budget():
    W, H = 940, 600
    s = header(W, H)
    s += text(W / 2, 36, "Чому EUV — це лише дзеркала у вакуумі, і куди дівається 98% світла",
              19, INK, "middle", "bold")
    s += text(W / 2, 58, "EUV поглинає БУДЬ-ЩО — повітря, скло, навіть тонка плівка; тому лінз нема, а є ланцюг дзеркал, і кожне краде ~30%",
              11.5, GREY, "middle", style="italic")

    # ── ліва колонка: чому не лінзи ──
    s += rect(40, 84, 300, 250, "#f5f7fb", BLUE, 1.8, 12)
    s += text(190, 110, "Чому НЕ лінзи (як у DUV)", 13, BLUE, "middle", "bold")
    for i, t in enumerate([
        "• EUV (13.5 нм) поглинає все:",
        "   повітря, скло лінзи, вода, плівка.",
        "• Промінь крізь лінзу просто згас би.",
        "• Тому: тільки ВІДБИВАННЯ, і лише",
        "   спеціальними дзеркалами Mo/Si.",
        "• І весь шлях — у ВАКУУМІ, бо навіть",
        "   повітря з'їло б промінь.",
    ]):
        s += text(58, 134 + i * 22, t, 11, INK, "start",
                  "bold" if t.startswith("•") and ("вакуум" in t.lower() or "відбива" in t.lower()) else "normal")
    # маленька ілюстрація багатошарового дзеркала
    s += text(190, 300, "дзеркало = ~40–50 пар шарів Mo/Si", 10, GREY, "middle", style="italic")
    ym = 312
    for i in range(10):
        c = PURPLE if i % 2 == 0 else AMBER
        s += rect(120 + i * 14, ym, 12, 14, c, c, 0, 1)
    s += text(190, ym + 28, "відбиває лише ~70% навіть у теорії", 10, GREY, "middle", style="italic")

    # ── права колонка: каскад втрат ──
    bx0 = 380
    s += text(bx0 + 270, 100, "Бюджет світла: 11 відбивань поспіль", 13, INK, "middle", "bold")
    # ступінчаста «драбина» згасання
    stages = [
        ("джерело\n100%", 100.0, AMBER),
        ("4 дзеркала-\nконденсори", 24.0, BLUE),
        ("маска\n(теж дзеркало)", 17.0, RED),
        ("6 дзеркал\nпроєкції", 2.0, GREEN),
    ]
    base = 440
    bw = 120
    gap = 20
    maxh = 300
    for i, (lab, pct, col) in enumerate(stages):
        bx = bx0 + i * (bw + gap)
        bh = maxh * (pct / 100.0)
        if bh < 8:
            bh = 8
        s += rect(bx, base - bh, bw, bh, "#fff", col, 2, 6)
        s += rect(bx, base - bh, bw, min(bh, 26), col, col, 0, 6)
        s += text(bx + bw / 2, base + 22, f"{pct:g}%", 14, col, "middle", "bold")
        for j, ln in enumerate(lab.split("\n")):
            s += text(bx + bw / 2, base + 42 + j * 15, ln, 10, INK, "middle")
        if i < len(stages) - 1:
            ax = bx + bw + 2
            s += arrow(ax, base - 18, ax + gap - 4, base - 18, GREY, 2)
    s += text(bx0 + 270, base - maxh - 12,
              "кожне відбивання забирає ~30% — і втрати множаться", 10.5, GREY, "middle", style="italic")

    # підсумок-плашка
    s += rect(40, 520, W - 80, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 542,
              "Підсумок: до пластини доходить лише ~2% світла джерела —", 12, INK, "middle", "bold")
    s += text(W / 2, 560,
              "тому джерело й мусить бути таким шалено потужним, а вся машина — гігантською.", 12, INK, "middle", "bold")
    save("fig-r10-s2h-3-budget.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_source()
    fig_budget()
    print("done:", OUT)
