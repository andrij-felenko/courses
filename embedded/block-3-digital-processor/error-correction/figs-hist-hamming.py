# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 3.9 — «Коди виявлення
й корекції помилок» (Модуль 3): Річард Геммінг і питання «якщо машина бачить
помилку — чому не виправить?».

ОКРЕМИЙ скрипт лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи історії до розділу — секція 0 (Рис. 3.9.0.k → файли fig-r09-0-k-*).
Допоміжні функції — копія спільних із рештою розділів, щоб вигляд був єдиний.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


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


# ── проста «постать» (голова + плечі) для портретних карток ─────────────────
def _person(cx, cy, col):
    out = circle(cx, cy, 12, "#ffffff", col, 2.4)
    out += path(f"M{cx-18},{cy+30} Q{cx},{cy+10} {cx+18},{cy+30}", "none", col, 2.4)
    return out


# ── одна клітинка-біт (квадрат із символом усередині) ───────────────────────
def _bit(cx, cy, label, fill, stroke, w=22, txtcol=None):
    s = rect(cx - w, cy - w, 2 * w, 2 * w, fill, stroke, 1.8, 4)
    s += text(cx, cy + 6, label, 16, txtcol or stroke, "middle", "bold")
    return s


# ═══════════ Рис. 3.9.0.1 — таймлайн: від досади до коду й закону ════════════
def fig_timeline():
    W, H = 900, 742
    s = header(W, H)
    s += text(W / 2, 38, "Від суботньої досади до коду, що сам себе лагодить", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "релейна машина бачила помилку, але лиш зупинялася — Геммінг спитав, чому вона не виправить її сама",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 100, H - 26
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1946", "Геммінг приходить у Bell Labs",
         "Математик із Манхеттенського проєкту сідає в один кабінет із Клодом Шенноном — батьком теорії інформації", False),
        ("кінець 1940-х", "релейна машина по вихідних",
         "Геммінг рахує на Bell Model V; та бачить свою помилку — і у вихідні, коли нема операторів, просто КИДАЄ задачу", False),
        ("1947", "питання, з якого все почалось",
         "«Чорт забирай, якщо машина бачить помилку — ЧОМУ вона не може знайти її місце й виправити?»", True),
        ("1948", "Шеннон уже цитує код Геммінга",
         "У «Математичній теорії зв'язку» Шеннон описує код [7,4] і прямо приписує його Геммінгу (внутрішня записка 1947-го)", False),
        ("1949", "паралельно — Марсель Голей",
         "Голей друкує «Notes on digital coding» у Proc. IRE — на РІК раніше за статтю Геммінга; та сама ідея, інша рука", False),
        ("1950", "велика стаття нарешті виходить",
         "«Error Detecting and Error Correcting Codes», Bell System Technical Journal: код, відстань і метрика Геммінга", False),
        ("1968", "премія Тюрінга",
         "Третій в історії лауреат премії Тюрінга; «відстань Геммінга» давно стала стандартним терміном", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, hl) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        if hl:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if hl else INK), "start", "bold")
        for j, ln in enumerate(_wrap(q, 62)):
            s += text(spine + 26, y + 18 + j * 17, ln, 12, INK, "start", style="italic")
    save("fig-r09-0-1-timeline.svg", s)


# ═══════════ Рис. 3.9.0.2 — будні vs вихідні: корінь досади ═════════════════
def fig_weekend():
    W, H = 900, 466
    s = header(W, H)
    s += text(W / 2, 34, "Корінь досади: машина БАЧИЛА помилку, але у вихідні просто кидала задачу", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Bell Model V зупинялася на помилці й кліпала лампами — та лиш доки поряд був оператор, що міг утрутитися",
              11.5, GREY, "middle", style="italic")

    # ── будні: оператор ловить і виправляє ──
    s += rect(60, 88, 360, 300, "#f4f7f4", GREEN, 1.8, 10)
    s += text(240, 114, "Будні: поряд оператор", 14, GREEN, "middle", "bold")
    s += arrow(110, 150, 360, 150, INK, 2.4)
    s += text(120, 140, "лічба йде…", 11, INK, "start", style="italic")
    s += circle(250, 150, 9, "#fff", RED, 2.6)
    s += text(250, 154, "!", 13, RED, "middle", "bold")
    s += text(250, 178, "помилка → СТОП, кліпають лампи", 10.5, RED, "middle", "bold")
    s += text(240, 214, "оператор бачить, зупиняє,", 11, INK, "middle")
    s += text(240, 232, "виправляє й запускає далі", 11, INK, "middle")
    s += rect(150, 254, 180, 40, "#eef7ee", GREEN, 1.6, 8)
    s += text(240, 279, "робота врятована", 12.5, GREEN, "middle", "bold")
    s += text(240, 330, "людина = «жива корекція помилок»", 11, INK, "middle", "bold")
    s += text(240, 352, "але людина потрібна ПОРЯД і ЗАВЖДИ", 10.5, GREY, "middle", style="italic")

    # ── вихідні: нікого немає ──
    s += rect(480, 88, 360, 300, "#fdf4f4", RED, 1.8, 10)
    s += text(660, 114, "Вихідні: у залі нікого", 14, RED, "middle", "bold")
    s += arrow(530, 150, 780, 150, INK, 2.4)
    s += text(540, 140, "лічба йде…", 11, INK, "start", style="italic")
    s += circle(670, 150, 9, "#fff", RED, 2.6)
    s += text(670, 154, "!", 13, RED, "middle", "bold")
    s += text(660, 178, "та сама помилка — а втручатися нікому", 10.5, RED, "middle", "bold")
    s += text(660, 214, "машина не вміє виправити сама,", 11, INK, "middle")
    s += text(660, 232, "тож просто КИДАЄ задачу й бере наступну", 10.5, INK, "middle")
    s += rect(570, 254, 180, 40, "#fbecec", RED, 1.6, 8)
    s += text(660, 279, "результат — у смітник", 12.5, RED, "middle", "bold")
    s += text(660, 330, "у понеділок Геммінг бачив:", 11, INK, "middle", "bold")
    s += text(660, 352, "два вихідні лічби — змарновано дарма", 10.5, GREY, "middle", style="italic")

    s += rect(60, 404, W - 120, 50, "#fafafa", INK, 1.4, 10)
    s += text(W / 2, 426, "Звідси й народилося питання: машина ВЖЕ знає, що десь є помилка (вона ж зупиняється) —", 11.5, INK, "middle", "bold")
    s += text(W / 2, 446, "то чому б їй не знати ще й ДЕ ця помилка, і не виправити її без жодної людини в залі?", 11.5, INK, "middle", "bold")
    save("fig-r09-0-2-weekend.svg", s)


# ═══════════ Рис. 3.9.0.3 — стрибок: від «бачу» до «знаю де» ════════════════
def fig_detect_vs_correct():
    W, H = 900, 486
    s = header(W, H)
    s += text(W / 2, 34, "Суть ідеї: від «помилка Є» до «помилка ОТУТ»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "виявлення лиш піднімає тривогу; корекція додає стільки перевірок, що їхній «відбиток» вказує НА сам хибний біт",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: парність — детектор ──
    s += rect(60, 86, 360, 330, "#fafafa", AMBER, 1.8, 10)
    s += text(240, 112, "Один біт парності: ДЕТЕКТОР", 13.5, AMBER, "middle", "bold")
    bits = ["1", "0", "1", "1", "0", "0", "1"]
    for i, b in enumerate(bits):
        cx = 96 + i * 44
        s += _bit(cx, 162, b, "#ffffff", INK, 17)
    s += text(96 + 6 * 44, 200, "P", 12, AMBER, "middle", "bold")
    s += text(240, 226, "1 зайвий біт стежить за парністю всіх", 10.5, INK, "middle")
    # перевернувся один біт
    s += circle(96 + 3 * 44, 162, 22, "none", RED, 2.4)
    s += text(96 + 3 * 44, 196, "перевернувся", 9.5, RED, "middle", "bold")
    s += text(240, 262, "парність «не сходиться» →", 11, RED, "middle", "bold")
    s += text(240, 282, "МАШИНА ЗНАЄ: десь є помилка", 11.5, RED, "middle", "bold")
    s += rect(120, 300, 240, 44, "#fbf3e0", AMBER, 1.6, 8)
    s += text(240, 320, "але НЕ знає, у якому з бітів", 11, INK, "middle", "bold")
    s += text(240, 337, "виправити наосліп — годі", 10, GREY, "middle", style="italic")
    s += text(240, 372, "це межа простого виявлення:", 10.5, INK, "middle")
    s += text(240, 392, "тривога є — адреси немає", 10.5, GREY, "middle", style="italic")

    # стрілка-міст
    s += arrow(424, 250, 476, 250, INK, 3)
    s += text(450, 238, "крок", 10, INK, "middle", "bold")
    s += text(450, 274, "Геммінга", 10, INK, "middle", "bold")

    # ── праворуч: кілька перевірок → адреса ──
    s += rect(480, 86, 360, 330, "#f4f7f4", GREEN, 1.8, 10)
    s += text(660, 112, "Кілька перевірок: КОРЕКЦІЯ", 13.5, GREEN, "middle", "bold")
    s += text(660, 136, "кожна стежить за СВОЇМ набором бітів", 10.5, INK, "middle")
    # три перевірки як рядки прапорців
    rows = [
        ("перевірка A", [1, 1, 0, 1], "✗"),
        ("перевірка B", [0, 1, 1, 1], "✓"),
        ("перевірка C", [1, 0, 1, 1], "✗"),
    ]
    for r, (nm, mask, res) in enumerate(rows):
        y = 168 + r * 40
        col = RED if res == "✗" else GREEN
        s += text(516, y + 5, nm, 11, INK, "start", "bold")
        for c in range(4):
            cx = 636 + c * 30
            on = mask[c]
            s += circle(cx, y, 9, ("#eef7ee" if on else "#ffffff"), (GREEN if on else FAINT), 1.6)
            if on:
                s += circle(cx, y, 3, GREEN, GREEN, 0)
        s += text(786, y + 5, res, 14, col, "middle", "bold")
    s += text(660, 300, "набір «що зійшлось / що ні» — це АДРЕСА", 11, GREEN, "middle", "bold")
    s += rect(560, 314, 200, 40, "#eef7ee", GREEN, 1.6, 8)
    s += text(660, 339, "✗✓✗ → хибний саме біт №…", 11.5, INK, "middle", "bold")
    s += text(660, 378, "знаєш адресу — перевертаєш назад", 10.5, INK, "middle", "bold")
    s += text(660, 398, "один зіпсований біт ВИПРАВЛЕНО без людини", 10, GREY, "middle", style="italic")

    s += text(W / 2, 446, "Уся хитрість — не в новому атомі, а в кількості перевірок: їхній спільний «відбиток» (синдром) і є номером хибного біта.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 468, "Саме так машина дізнається не лише ЩО помилка є, а й ДЕ вона, — а отже, може виправити її сама.",
              11, GREY, "middle", style="italic")
    save("fig-r09-0-3-detect-vs-correct.svg", s)


# ═══════════ Рис. 3.9.0.4 — Геммінг(7,4): 4 дані + 3 перевірки ══════════════
def fig_hamming74():
    W, H = 900, 510
    s = header(W, H)
    s += text(W / 2, 34, "Код Геммінга (7,4): 4 біти даних + 3 біти перевірки = 7", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "три кола перевірок перекриваються так, що кожен біт даних лежить у СВОЇЙ єдиній комбінації кіл",
              11.5, GREY, "middle", style="italic")

    # три кола Венна (перевірки P1, P2, P3)
    cxA, cyA, R = 340, 250, 118
    cxB, cyB = 470, 250
    cxC, cyC = 405, 360
    s += circle(cxA, cyA, R, "none", RED, 2.2)
    s += circle(cxB, cyB, R, "none", BLUE, 2.2)
    s += circle(cxC, cyC, R, "none", GREEN, 2.2)
    s += text(cxA - 96, cyA - 96, "перевірка P1", 12, RED, "start", "bold")
    s += text(cxB + 30, cyB - 96, "перевірка P2", 12, BLUE, "start", "bold")
    s += text(cxC - 30, cyC + 104, "перевірка P3", 12, GREEN, "middle", "bold")

    # позиції бітів усередині діаграми
    # d1 — у всіх трьох (центр); d2,d3,d4 — у парах; p1,p2,p3 — у «своїх» одиничних зонах
    def b(cx, cy, lab, col, faint):
        s2 = circle(cx, cy, 17, faint, col, 1.8)
        s2 += text(cx, cy + 5, lab, 13, col, "middle", "bold")
        return s2
    s += b(405, 258, "d1", INK, "#ffffff")          # перетин усіх трьох
    s += b(405, 205, "d2", INK, "#ffffff")          # P1∩P2
    s += b(360, 312, "d3", INK, "#ffffff")          # P1∩P3
    s += b(452, 312, "d4", INK, "#ffffff")          # P2∩P3
    s += b(300, 215, "p1", RED, "#fbecec")          # лише P1
    s += b(512, 215, "p2", BLUE, "#eaf0fb")         # лише P2
    s += b(405, 410, "p3", GREEN, "#eef7ee")        # лише P3

    # права легенда
    bx = 660
    s += rect(bx - 20, 96, 260, 200, "#fafafa", INK, 1.4, 10)
    s += text(bx + 110, 120, "Як це працює", 13, INK, "middle", "bold")
    leg = [
        ("d1…d4", "4 біти ваших ДАНИХ", INK),
        ("p1,p2,p3", "3 біти ПЕРЕВІРКИ (парність кола)", INK),
        ("кожне коло", "тримає СВОЇ біти парними", INK),
    ]
    for i, (k, v, c) in enumerate(leg):
        s += text(bx - 4, 150 + i * 24, k + " —", 11.5, c, "start", "bold")
        s += text(bx - 4, 168 + i * 24, "   " + v, 11, GREY, "start")
    s += text(bx + 110, 246, "помилка в одному біті псує", 10.5, RED, "middle", "bold")
    s += text(bx + 110, 264, "РІВНО ті кола, що його містять", 10.5, RED, "middle", "bold")
    s += text(bx + 110, 282, "→ це і є його точна адреса", 10.5, GREEN, "middle", "bold")

    s += rect(bx - 20, 312, 260, 150, "#f4f7f4", GREEN, 1.4, 10)
    s += text(bx + 110, 336, "Що вміє код (7,4)", 12.5, GREEN, "middle", "bold")
    facts = [
        "• ВИПРАВЛЯЄ будь-який 1 хибний біт",
        "• ВИЯВЛЯЄ (не виправляючи) 2 хибні",
        "• ціна: 3 зайві біти на 4 корисні",
        "• 7 кодових бітів на 4 даних",
    ]
    for i, t in enumerate(facts):
        s += text(bx - 6, 362 + i * 24, t, 11, INK, "start")

    s += text(W / 2, 492, "Перекриття трьох перевірок — це і є геометрія коду: сім позицій так пов'язані, що «відбиток» помилки прямо називає винний біт.",
              11, GREY, "middle", style="italic")
    save("fig-r09-0-4-hamming74.svg", s)


# ═══════════ Рис. 3.9.0.5 — колективна атрибуція: Шеннон/Геммінг/Голей ══════
def fig_attribution():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Не «один геній», а три внески поряд — і питання, хто був перший", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "теорема Шеннона казала, що так МОЖНА; Геммінг і Голей показали, ЯК саме — майже водночас і незалежно",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("Клод Шеннон", "Claude Shannon", "ТЕОРІЯ",
         "1948: довів, що надійна передача крізь шум МОЖЛИВА — але доведення неконструктивне: воно не дає самого коду. І саме він у тій статті описав код [7,4] та приписав його Геммінгу", BLUE),
        ("Річард Геммінг", "Richard Hamming", "КОНСТРУКЦІЯ",
         "1947 — внутрішня записка, 1950 — велика стаття (друк відклали з ПАТЕНТНИХ причин). Дав готовий код, що ВИПРАВЛЯЄ біт, відстань і метрику Геммінга", RED),
        ("Марсель Голей", "Marcel J. E. Golay", "ПАРАЛЕЛЬНО",
         "1949, «Notes on digital coding» у Proc. IRE — на рік РАНІШЕ за статтю Геммінга. Узагальнив ідею (коди Голея) — інша рука прийшла до того ж незалежно", GREEN),
    ]
    cw, gap = 270, 22
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, (name, eng, role, desc, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        hl = (col == RED)
        s += rect(x, 84, cw, 300, "#fdf4f4" if hl else "#fafafa", col, 2.2 if hl else 1.6, 12)
        s += _person(x + cw / 2, 124, col)
        s += text(x + cw / 2, 192, name, 15, INK, "middle", "bold")
        s += text(x + cw / 2, 211, eng, 11.5, GREY, "middle", style="italic")
        s += rect(x + cw / 2 - 66, 226, 132, 26, col, col, 0, 13)
        s += text(x + cw / 2, 244, role, 12.5, "#ffffff", "middle", "bold")
        for j, ln in enumerate(_wrap(desc, 33)):
            s += text(x + 16, 280 + j * 18, ln, 10.8, INK, "start")
    s += text(W / 2, 416, "Код носить ім'я Геммінга по праву — та поряд стоять і теорема Шеннона, що відкрила дорогу, і Голей, який надрукував спорідненy ідею раніше.",
              11, INK, "middle", "bold")
    s += text(W / 2, 438, "Звична картина в техніці: за одним іменем на коді — кілька різних людей і різних внесків, що зійшлися в той самий короткий проміжок часу.",
              10.5, GREY, "middle", style="italic")
    save("fig-r09-0-5-attribution.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_weekend()
    fig_detect_vs_correct()
    fig_hamming74()
    fig_attribution()
    print("done:", OUT)
