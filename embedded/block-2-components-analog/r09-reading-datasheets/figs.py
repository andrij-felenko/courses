# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 2.9 — «Як читати даташит» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Підписи посекційно (Рис. 2.9.S.N). Допоміжні функції
скопійовано з попередніх розділів.
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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


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


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


def _docpage(x, y, w, h, fill="#ffffff", fold=18):
    """Аркуш документа із загнутим кутом."""
    s = (f'<path d="M {x},{y} L {x + w - fold},{y} L {x + w},{y + fold} '
         f'L {x + w},{y + h} L {x},{y + h} Z" fill="{fill}" stroke="#9bb0c2" stroke-width="1.6"/>\n')
    s += (f'<path d="M {x + w - fold},{y} L {x + w - fold},{y + fold} L {x + w},{y + fold}" '
          f'fill="none" stroke="#9bb0c2" stroke-width="1.4"/>\n')
    return s


# ── Рис. 2.9.1.1 — компонент і його паспорт ──────────────────────────────────
def fig191_passport():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 32, "Даташит — паспорт компонента", 17, INK, "middle", "bold")
    # компонент (мікросхема)
    s += rect(70, 130, 130, 90, "#eef2f7", "#7f93a8", 2, 8)
    s += text(135, 168, "компонент", 12, INK, "middle", "bold")
    s += text(135, 188, "(чип, діод…)", 9.5, GREY, "middle")
    for i in range(4):
        s += line(70, 145 + i * 18, 56, 145 + i * 18, INK, 2)
        s += line(200, 145 + i * 18, 214, 145 + i * 18, INK, 2)
    s += arrow(230, 175, 300, 175, GREY, 2.4) + text(265, 162, "питання?", 9, GREY, "middle", "bold")
    # даташит
    s += _docpage(330, 96, 200, 168)
    s += text(430, 122, "DATASHEET", 12, INK, "middle", "bold")
    s += line(350, 132, 510, 132, FAINT, 1.4)
    for i, lab in enumerate(["параметри", "рейтинги", "розпіновка", "графіки", "застосування"]):
        s += text(352, 154 + i * 21, "• " + lab, 10, INK, "start")
    s += text(560, 150, "єдине", 11, GREEN, "start", "bold") + text(560, 168, "джерело", 11, GREEN, "start", "bold")
    s += text(560, 186, "правди", 11, GREEN, "start", "bold")
    s += text(W / 2, H - 14, "Виробник публікує офіційний документ — усе, що треба знати, щоб застосувати прилад правильно й не спалити.",
              10, GREY, "middle", style="italic")
    save("fig-r09-1-1-passport.svg", s)


def fig191_map():
    W, H = 560, 470
    s = header(W, H)
    s += text(W / 2, 30, "Карта даташита: що де лежить", 16, INK, "middle", "bold")
    secs = [
        ("Назва · можливості · опис", "що це й навіщо (вітрина)", "#fdf1dc"),
        ("Розпіновка · корпус", "де яка ніжка", LBLUE),
        ("Absolute Maximum Ratings", "межа знищення — не переходь (§2.9.2)", LRED),
        ("Recommended Operating", "де працювати насправді (§2.9.2)", "#fff3e0"),
        ("Electrical Characteristics", "параметри min/typ/max (§2.9.3)", LGRN),
        ("Typical Performance — графіки", "залежності від темп., струму (§2.9.4)", LBLUE),
        ("Опис роботи · блок-схема", "як воно влаштоване всередині", "#f3e9f3"),
        ("Application — типові схеми", "як підключити по-людськи", LGRN),
        ("Корпус · маркування · замовлення", "механіка й коди (§2.9.5)", "#fff3e0"),
    ]
    y, bw, bh = 52, 470, 40
    for i, (t1, t2, col) in enumerate(secs):
        yy = y + i * (bh + 6)
        s += rect(46, yy, bw, bh, col, "#9bb0c2", 1.3, 5)
        s += text(60, yy + 18, t1, 11, INK, "start", "bold")
        s += text(60, yy + 33, t2, 9, GREY, "start")
    s += text(W / 2, H - 10, "Зверху — «що це», далі — межі й параметри, наприкінці — механіка. Скрізь однакова логіка.",
              9, GREY, "middle", style="italic")
    save("fig-r09-1-2-map.svg", s)


def fig191_firstpage():
    W, H = 620, 380
    s = header(W, H)
    s += text(W / 2, 30, "Перша сторінка: вітрина приладу", 16, INK, "middle", "bold")
    s += _docpage(60, 56, 500, 300)
    s += text(86, 90, "OP-AMP «XYZ123»", 16, INK, "start", "bold")
    s += text(86, 110, "Малошумний rail-to-rail операційний підсилювач", 10, GREY, "start")
    s += line(80, 122, 540, 122, FAINT, 1.4)
    s += text(86, 146, "Features (можливості):", 11, INK, "start", "bold")
    for i, ln in enumerate(["• смуга 10 МГц", "• зсув < 1 мВ", "• живлення 1.8…5.5 В", "• rail-to-rail вхід/вихід"]):
        s += text(96, 166 + i * 18, ln, 9.5, INK, "start")
    s += text(330, 146, "Опис:", 11, INK, "start", "bold")
    s += text(330, 166, "коротко, що це й куди", 9.5, GREY, "start")
    s += text(330, 182, "ставлять. Часто —", 9.5, GREY, "start")
    s += text(330, 198, "оптимістичний тон реклами.", 9.5, GREY, "start")
    # pinout thumbnail
    s += rect(330, 222, 110, 96, "#eef2f7", "#9bb0c2", 1.4, 5) + text(385, 240, "розпіновка", 8.5, INK, "middle", "bold")
    for i in range(4):
        s += line(330, 256 + i * 14, 318, 256 + i * 14, INK, 1.6)
        s += line(440, 256 + i * 14, 452, 256 + i * 14, INK, 1.6)
    s += text(86, 250, "Тут вирішуєш одне:", 10, INK, "start", "bold")
    s += text(86, 268, "«це взагалі той", 9.5, INK, "start")
    s += text(86, 284, "компонент, що мені", 9.5, INK, "start")
    s += text(86, 300, "треба?» Деталі — далі.", 9.5, INK, "start")
    s += text(W / 2, H - 12, "Перша сторінка — короткий портрет: назва, ключові цифри, опис, ескіз розпіновки. Швидко відсіяти «не те».",
              9, GREY, "middle", style="italic")
    save("fig-r09-1-3-firstpage.svg", s)


def fig191_jump():
    W, H = 700, 350
    s = header(W, H)
    s += text(W / 2, 30, "Не читай поспіль — стрибай до потрібного", 15.5, INK, "middle", "bold")
    pairs = [
        ("«Це той компонент?»", "→ перша сторінка", "#fdf1dc"),
        ("«Як підключити?»", "→ розпіновка", LBLUE),
        ("«Що його не вб'є?»", "→ Absolute Maximum", LRED),
        ("«Конкретне число?»", "→ таблиця Electrical Char.", LGRN),
        ("«Як зміниться в спеку?»", "→ графіки Typical Perf.", LBLUE),
        ("«Як зібрати схему?»", "→ Application Info", LGRN),
    ]
    y, bw, bh = 60, 600, 38
    for i, (q, a, col) in enumerate(pairs):
        yy = y + i * (bh + 6)
        s += rect(50, yy, 290, bh, "#ffffff", "#c9d3dc", 1.3, 5) + text(64, yy + 24, q, 11, INK, "start", "bold")
        s += rect(360, yy, 290, bh, col, "#9bb0c2", 1.3, 5) + text(374, yy + 24, a, 11, INK, "start", "bold")
        s += arrow(342, yy + bh / 2, 358, yy + bh / 2, GREY, 2)
    s += text(W / 2, H - 12, "Даташит на 40 сторінок не читають від кірки до кірки — у нього заходять із конкретним питанням.",
              9, GREY, "middle", style="italic")
    save("fig-r09-1-4-jump.svg", s)


def fig191_tones():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Три голоси даташита: хто й навіщо говорить", 15, INK, "middle", "bold")
    cards = [
        (40, "вітрина", "Перша сторінка", ["реклама:", "найкращі цифри,", "оптимістичний тон"], "#fff3e0", SUN),
        (268, "застереження", "Absolute Maximum", ["юридичне «ми попередили»:", "перейдеш — сам винен,", "гарантії знято"], LRED, RED),
        (496, "статистика", "min / typ / max", ["«typ» — не обіцянка,", "а типове; гарантують", "лише min і max"], LGRN, GREEN),
    ]
    for x, tag, title, lines, fill, col in cards:
        s += rect(x, 60, 184, 196, fill, col, 1.6, 8)
        s += text(x + 92, 84, tag.upper(), 9, col, "middle", "bold")
        s += text(x + 92, 108, title, 12, INK, "middle", "bold")
        s += line(x + 20, 120, x + 164, 120, "#ffffff", 1.4)
        for k, ln in enumerate(lines):
            s += text(x + 92, 146 + k * 22, ln, 9.5, INK, "middle")
    s += text(W / 2, H - 12, "Даташит водночас продає прилад і захищає виробника. Тон сторінки підказує, наскільки їй вірити.",
              9.5, GREY, "middle", style="italic")
    save("fig-r09-1-5-tones.svg", s)


# ── §2.9.2 Absolute Maximum vs Recommended (Рис. 2.9.2.k) ───────────────────
def fig192_two_tables():
    W, H = 720, 362
    s = header(W, H)
    s += text(W / 2, 28, "Дві таблиці меж: знищення проти роботи", 16, INK, "middle", "bold")
    s += rect(40, 60, 320, 252, LRED, RED, 1.8, 8)
    s += text(200, 86, "ABSOLUTE MAXIMUM", 12.5, RED, "middle", "bold")
    s += text(200, 104, "межа знищення — НЕ переходь", 9, INK, "middle")
    rows1 = [("Живлення", "6 В"), ("Напруга входу", "−0.3…Vcc+0.3"), ("Струм ніжки", "±40 мА"), ("Темп. кристала", "150 °C")]
    for i, (k, v) in enumerate(rows1):
        y = 134 + i * 38
        s += text(56, y, k, 10.5, INK, "start") + text(344, y, v, 10.5, RED, "end", "bold")
        s += line(56, y + 12, 344, y + 12, "#e0bcbc", 1)
    s += text(200, 300, "перейшов — прилад мертвий або скалічений", 8.5, RED, "middle", "bold")
    s += rect(380, 60, 300, 252, LGRN, GREEN, 1.8, 8)
    s += text(530, 86, "RECOMMENDED OPERATING", 10.5, GREEN, "middle", "bold")
    s += text(530, 104, "де працювати насправді", 9, INK, "middle")
    rows2 = [("Живлення", "1.8…5.5 В"), ("Темп. роботи", "−40…85 °C")]
    for i, (k, v) in enumerate(rows2):
        y = 142 + i * 38
        s += text(396, y, k, 10.5, INK, "start") + text(664, y, v, 10.5, GREEN, "end", "bold")
        s += line(396, y + 12, 664, y + 12, "#bcd8c4", 1)
    s += text(530, 248, "тут гарантовані ВСІ параметри", 9.5, GREEN, "middle", "bold")
    s += text(530, 268, "з таблиці Electrical Characteristics", 8.5, INK, "middle")
    s += text(W / 2, H - 12, "Absolute Maximum — «не зруйнуй». Recommended — «працюй тут». Це РІЗНІ таблиці з різним сенсом.",
              9, GREY, "middle", style="italic")
    save("fig-r09-2-1-two-tables.svg", s)


def fig192_cliff():
    W, H = 700, 330
    s = header(W, H)
    s += text(W / 2, 28, "Прірва між «працює» і «гине»: напруга живлення", 15, INK, "middle", "bold")
    ox, oy, pw = 80, 232, 560
    s += arrow(ox, oy, ox + pw + 14, oy, INK, 2) + text(ox + pw + 18, oy + 4, "Vcc (В)", 10.5, INK, "start", "bold")

    def xV(v):
        return ox + pw * v / 7.0
    for v in range(0, 8):
        s += line(xV(v), oy, xV(v), oy + 5, INK, 1.2) + text(xV(v), oy + 18, str(v), 9, INK, "middle")
    s += rect(xV(1.8), oy - 90, xV(5.5) - xV(1.8), 90, LGRN, GREEN, 1.4, 0)
    s += text((xV(1.8) + xV(5.5)) / 2, oy - 52, "Recommended", 10.5, GREEN, "middle", "bold")
    s += text((xV(1.8) + xV(5.5)) / 2, oy - 34, "усе гарантовано", 8.5, INK, "middle")
    s += rect(xV(5.5), oy - 90, xV(6) - xV(5.5), 90, "#fff3e0", SUN, 1.4, 0)
    s += text((xV(5.5) + xV(6)) / 2, oy - 100, "прірва", 8.5, SUN, "middle", "bold")
    s += line(xV(6), oy - 112, xV(6), oy, RED, 2.4, "5 4") + text(xV(6) + 4, oy - 118, "Abs Max 6 В", 9.5, RED, "start", "bold")
    s += rect(xV(6), oy - 90, xV(7) - xV(6), 90, LRED, RED, 1.4, 0)
    s += text((xV(6) + xV(7)) / 2, oy - 48, "руйну-", 8.5, RED, "middle", "bold") + text((xV(6) + xV(7)) / 2, oy - 34, "вання", 8.5, RED, "middle", "bold")
    s += text(W / 2, H - 30, "У зеленому — усе як обіцяно. У жовтій прірві — може й працює, та НІЧОГО не гарантовано.", 9.5, INK, "middle")
    s += text(W / 2, H - 12, "За червоною межею прилад псується — часто НЕЗВОРОТНО, навіть від короткого дотику.", 9, GREY, "middle", style="italic")
    save("fig-r09-2-2-cliff.svg", s)


def fig192_why_gap():
    W, H = 700, 296
    s = header(W, H)
    s += text(W / 2, 28, "Навіщо прірва: запас на реальність", 16, INK, "middle", "bold")
    reasons = [
        ("Розкид партії", "екземпляри різні; край гарантують з запасом"),
        ("Температура", "у спеку межі стискаються — потрібен буфер"),
        ("Старіння", "прилад слабшає з роками"),
        ("Надійність", "робота біля межі вкорочує життя, хай і «працює»"),
    ]
    for i, (k, v) in enumerate(reasons):
        y = 66 + i * 50
        s += rect(56, y, 196, 38, LBLUE, "#9bb0c2", 1.4, 6) + text(154, y + 24, k, 11, INK, "middle", "bold")
        s += arrow(254, y + 19, 286, y + 19, GREY, 2)
        s += text(298, y + 24, v, 10, INK, "start")
    s += text(W / 2, H - 12, "Recommended — це Abs Max мінус запас на все це. Жити треба в зеленому, а не «майже на межі».",
              9, GREY, "middle", style="italic")
    save("fig-r09-2-3-why-gap.svg", s)


def fig192_transient():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Підступ: коротка піка вбиває, хоч середнє в нормі", 14.5, INK, "middle", "bold")
    ox, oy, pw, ph = 80, 222, 560, 150
    s += _axes(ox, oy, pw, ph, "час", "напруга")
    absY = oy - ph * 0.82
    s += line(ox, absY, ox + pw, absY, RED, 1.6, "5 4") + text(ox + pw - 4, absY - 8, "Abs Max", 9.5, RED, "end", "bold")
    pts = []
    for j in range(0, 281):
        t = j / 280.0
        v = 0.35 + 0.72 * math.exp(-((t - 0.45) ** 2) / 0.0006)
        pts.append((ox + pw * t, oy - ph * 0.9 * min(v, 1.0)))
    s += _poly(pts, BLUE, 2.4)
    s += circle(ox + pw * 0.45, absY - 6, 5, RED, "#ffffff", 2) + text(ox + pw * 0.45, absY - 18, "піка > межі!", 8.5, RED, "middle", "bold")
    s += text(ox + pw * 0.52, oy - ph * 0.22, "середнє — низьке й безпечне…", 9, INK, "start")
    s += text(W / 2, H - 12, "Сплеск (вмикання, ESD, гаряче підключення) на мить переростає Abs Max — і прилад мертвий, хоч решту часу все гаразд.",
              8.5, GREY, "middle", style="italic")
    save("fig-r09-2-4-transient.svg", s)


def fig192_params():
    W, H = 700, 322
    s = header(W, H)
    s += text(W / 2, 28, "Що зазвичай стоїть у Absolute Maximum", 16, INK, "middle", "bold")
    items = [
        ("Напруга живлення", "найбільше Vcc"),
        ("Напруга на входах", "часто −0.3…Vcc+0.3 В (інакше — латч-ап)"),
        ("Струм через ніжку", "скільки витримає вивід"),
        ("Потужність / темп. кристала Tj", "межа нагріву (§2.7.5)"),
        ("Температура зберігання", "ширша за робочу"),
        ("ESD", "стійкість до статичного розряду"),
    ]
    for i, (k, v) in enumerate(items):
        y = 64 + i * 40
        s += rect(50, y, 260, 30, "#fdeeee", "#d8a0a0", 1.3, 5) + text(64, y + 20, k, 10.5, INK, "start", "bold")
        s += text(326, y + 20, v, 9.5, INK, "start")
    s += text(W / 2, H - 12, "Жодну з цих меж не можна переходити навіть на мить. Особливо підступна — напруга входу проти рейок живлення.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-2-5-params.svg", s)


def fig192_rule():
    W, H = 680, 280
    s = header(W, H)
    s += text(W / 2, 28, "Правило проєктування: цілься в серцевину", 15.5, INK, "middle", "bold")
    s += rect(60, 70, 560, 152, LRED, RED, 1.6, 8)
    s += text(340, 92, "Absolute Maximum — НІКОЛИ не торкайся", 11, RED, "middle", "bold")
    s += rect(112, 108, 456, 98, "#fff3e0", SUN, 1.5, 8)
    s += text(340, 130, "прірва — «може й живе», не гарантовано", 10, "#b07d1e", "middle", "bold")
    s += rect(172, 146, 336, 52, LGRN, GREEN, 1.6, 8)
    s += text(340, 176, "Recommended + запас — ТУТ проєктуй", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 14, "Цілься в зелену серцевину із запасом; жовте лиши на аварії; червоного не торкайся ніколи.",
              9, GREY, "middle", style="italic")
    save("fig-r09-2-6-rule.svg", s)


# ── §2.9.3 Min/typ/max і умови (Рис. 2.9.3.k) ───────────────────────────────
def fig193_table():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Таблиця Electrical Characteristics", 16, INK, "middle", "bold")
    cols = [("Параметр", 50, 200), ("Умови", 250, 150), ("Min", 400, 70), ("Typ", 470, 70), ("Max", 540, 70), ("Од.", 610, 60)]
    y0, rh = 56, 40
    s += rect(46, y0, 624, 36, "#eef2f7", "#7f93a8", 1.5, 6)
    for name, x, w in cols:
        col = GREEN if name in ("Min", "Max") else (SUN if name == "Typ" else INK)
        s += text(x + 8, y0 + 23, name, 11, col, "start", "bold")
    rows = [
        ("Напруга зсуву Vos", "Vcc=5В, 25°C", "—", "0.5", "3", "мВ"),
        ("Струм спокою Iq", "без навантаж.", "—", "0.9", "1.5", "мА"),
        ("Смуга GBW", "—", "8", "10", "—", "МГц"),
        ("Rds(on)", "Vgs=10В", "—", "18", "25", "мОм"),
    ]
    for i, r in enumerate(rows):
        yy = y0 + 36 + i * rh
        s += rect(46, yy, 624, rh, "#ffffff", "#c9d3dc", 1.1, 0)
        for (name, x, w), val in zip(cols, r):
            col = GREEN if name in ("Min", "Max") and val != "—" else INK
            wt = "bold" if name in ("Min", "Max") and val != "—" else "normal"
            s += text(x + 8, yy + 25, val, 10, col, "start", wt)
    s += text(W / 2, H - 12, "Кожен параметр має min/typ/max і — найважливіше — стовпець УМОВ. Число без умов нічого не варте.",
              9, GREY, "middle", style="italic")
    save("fig-r09-3-1-table.svg", s)


def fig193_distribution():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "«typ» — це центр розкиду партії, а не обіцянка", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 90, 250, 520, 170
    s += arrow(ox, oy, ox + pw + 12, oy, INK, 2) + text(ox + pw + 16, oy + 4, "параметр", 10, INK, "start", "bold")
    cx = ox + pw * 0.5
    sig = pw * 0.13
    pts = []
    for j in range(0, 261):
        x = ox + pw * j / 260
        v = math.exp(-((x - cx) ** 2) / (2 * sig * sig))
        pts.append((x, oy - ph * 0.9 * v))
    s += _poly(pts, BLUE, 2.6)
    xmin, xmax = cx - 2.6 * sig, cx + 2.6 * sig
    s += line(xmin, oy, xmin, oy - ph * 0.5, GREEN, 1.8, "5 4") + text(xmin, oy + 18, "min", 10, GREEN, "middle", "bold")
    s += line(xmax, oy, xmax, oy - ph * 0.5, GREEN, 1.8, "5 4") + text(xmax, oy + 18, "max", 10, GREEN, "middle", "bold")
    s += line(cx, oy, cx, oy - ph * 0.92, SUN, 1.8, "3 3") + text(cx, oy + 18, "typ", 10, SUN, "middle", "bold")
    s += text(cx, oy - ph - 2, "усі випущені прилади — між min і max (гарантовано)", 9.5, GREEN, "middle", "bold")
    s += text(cx, oy - ph * 0.45, "твій — будь-де", 9, INK, "middle")
    s += text(cx, oy - ph * 0.45 + 14, "тут", 9, INK, "middle")
    s += text(W / 2, H - 12, "Гарантують лише краї (min, max); «typ» — найімовірніше значення, але саме твій екземпляр може мати інше.",
              9, GREY, "middle", style="italic")
    save("fig-r09-3-2-distribution.svg", s)


def fig193_design():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Розраховуй на гарантований край, а не на «typ»", 15, INK, "middle", "bold")
    s += _frame(28, 52, 320, 222, "розрахунок на «typ» — підведе")
    s += text(188, 78, "заклався на typ —", 9.5, INK, "middle")
    s += text(188, 94, "а частина партії гірша", 9.5, RED, "middle", "bold")
    ox, oy, pw = 60, 200, 256
    cx = ox + pw * 0.42
    sig = pw * 0.14
    pts = []
    for j in range(0, 201):
        x = ox + pw * j / 200
        pts.append((x, oy - 70 * math.exp(-((x - cx) ** 2) / (2 * sig * sig))))
    s += _poly(pts, BLUE, 2.2)
    s += line(cx, oy, cx, oy - 78, SUN, 1.6, "3 3") + text(cx, oy + 16, "typ", 8.5, SUN, "middle", "bold")
    s += line(ox + pw * 0.72, oy - 80, ox + pw * 0.72, oy, RED, 1.6) + text(ox + pw * 0.85, oy - 40, "ці —", 8.5, RED, "middle", "bold") + text(ox + pw * 0.85, oy - 26, "за межу", 8.5, RED, "middle")
    s += _frame(372, 52, 320, 222, "розрахунок на гарантований край — надійно")
    s += text(532, 78, "заклався на max (чи min) —", 9.5, INK, "middle")
    s += text(532, 94, "уся партія в безпеці", 9.5, GREEN, "middle", "bold")
    ox2 = 404
    cx2 = ox2 + pw * 0.42
    pts2 = []
    for j in range(0, 201):
        x = ox2 + pw * j / 200
        pts2.append((x, oy - 70 * math.exp(-((x - cx2) ** 2) / (2 * sig * sig))))
    s += _poly(pts2, BLUE, 2.2)
    s += line(ox2 + pw * 0.92, oy - 80, ox2 + pw * 0.92, oy, GREEN, 1.8) + text(ox2 + pw * 0.92, oy + 16, "max", 8.5, GREEN, "middle", "bold")
    s += text(ox2 + pw * 0.5, oy - 90, "уся крива — лівіше межі ✓", 8.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 10, "Заклавшись на «typ», ти проектуєш під половину приладів. Гарантований край покриває кожен.",
              9, GREY, "middle", style="italic")
    save("fig-r09-3-3-design.svg", s)


def fig193_conditions():
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Те саме число — лише для СВОЇХ умов", 16, INK, "middle", "bold")
    s += rect(70, 80, 250, 130, LGRN, GREEN, 1.6, 8)
    s += text(195, 108, "Rds(on)", 13, INK, "middle", "bold")
    s += text(195, 138, "20 мОм", 20, GREEN, "middle", "bold")
    s += text(195, 168, "@ Vgs=10В, 25 °C", 10, INK, "middle")
    s += text(195, 190, "(умови з даташита)", 8.5, GREY, "middle")
    s += rect(390, 80, 250, 130, LRED, RED, 1.6, 8)
    s += text(515, 108, "той самий Rds(on)", 12, INK, "middle", "bold")
    s += text(515, 138, "≈ 40 мОм", 20, RED, "middle", "bold")
    s += text(515, 168, "@ Vgs=10В, 125 °C", 10, INK, "middle")
    s += text(515, 190, "(у спеку — удвічі!)", 8.5, RED, "middle")
    s += arrow(326, 145, 384, 145, GREY, 2.2) + text(355, 132, "нагрів", 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Той самий параметр під іншими умовами (темп., напруга, струм) — інше число. Завжди звіряй умови зі своїми.",
              9, GREY, "middle", style="italic")
    save("fig-r09-3-4-conditions.svg", s)


def fig193_which_column():
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Який край небезпечний — залежить від параметра", 14.5, INK, "middle", "bold")
    items = [
        ("Напруга зсуву, шум, струм спокою", "MAX", "менше — добре, боїшся великого"),
        ("Підсилення, вихідний струм, смуга", "MIN", "більше — добре, боїшся малого"),
        ("Dropout, вхідний струм, витік", "MAX", "хочеш якнайменше"),
        ("Поріг увімкнення (інколи)", "MIN і MAX", "важать обидва краї"),
    ]
    for i, (k, c, why) in enumerate(items):
        y = 64 + i * 48
        col = RED if "MAX" in c and "MIN" not in c else (BLUE if c == "MIN" else INK)
        s += rect(50, y, 340, 38, "#ffffff", "#c9d3dc", 1.3, 6) + text(64, y + 24, k, 10, INK, "start")
        s += rect(410, y, 90, 38, LRED if col == RED else (LBLUE if col == BLUE else "#f3f3f3"), col, 1.4, 6)
        s += text(455, y + 24, c, 11, col, "middle", "bold")
        s += text(516, y + 24, why, 8.5, GREY, "start")
    s += text(W / 2, H - 12, "Дивись на той край, де ховається біда: для одних параметрів це max, для інших — min.",
              9, GREY, "middle", style="italic")
    save("fig-r09-3-5-which-column.svg", s)


def fig193_recipe():
    W, H = 700, 220
    s = header(W, H)
    s += text(W / 2, 30, "Рецепт читання рядка таблиці", 16, INK, "middle", "bold")
    steps = [
        ("1", "Знайди параметр", "пошуком по назві", LBLUE),
        ("2", "Знайди СВОЇ умови", "потрібний рядок / інтерполяція", "#fff3e0"),
        ("3", "Читай ГАРАНТОВАНУ колонку", "min або max — гірший бік", LGRN),
    ]
    bw, gap, y = 200, 16, 70
    for i, (n, t1, t2, col) in enumerate(steps):
        x = 40 + i * (bw + gap)
        s += rect(x, y, bw, 80, col, "#9bb0c2", 1.5, 8)
        s += circle(x + 24, y + 26, 13, "#fff", INK, 1.6) + text(x + 24, y + 31, n, 13, INK, "middle", "bold")
        s += text(x + 44, y + 31, t1, 11, INK, "start", "bold")
        s += text(x + 14, y + 58, t2, 9, INK, "start")
        if i < 2:
            s += arrow(x + bw, y + 40, x + bw + gap, y + 40, INK, 2)
    s += text(W / 2, H - 12, "Параметр → свої умови → гарантований край. Три кроки — і число в руках, якому можна вірити.",
              9, GREY, "middle", style="italic")
    save("fig-r09-3-6-recipe.svg", s)


def fig191_find():
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Де взяти даташит — і яку версію", 16, INK, "middle", "bold")
    s += rect(60, 138, 150, 50, "#eef2f7", "#7f93a8", 1.6, 6)
    s += text(135, 162, "номер деталі", 10.5, INK, "middle", "bold") + text(135, 178, "(part number)", 8.5, GREY, "middle")
    s += arrow(210, 150, 300, 110, GREEN, 2.2)
    s += arrow(210, 176, 300, 216, RED, 2.2)
    # good source
    s += rect(300, 80, 360, 70, LGRN, GREEN, 1.5, 8)
    s += text(320, 104, "✓ сайт виробника", 11.5, GREEN, "start", "bold")
    s += text(320, 124, "офіційний, найновіша ревізія,", 9.5, INK, "start")
    s += text(320, 140, "повний, із errata", 9.5, INK, "start")
    # bad source
    s += rect(300, 190, 360, 70, LRED, RED, 1.5, 8)
    s += text(320, 214, "✗ випадковий PDF-сайт", 11.5, RED, "start", "bold")
    s += text(320, 234, "часто старий, чужий чи урізаний;", 9.5, INK, "start")
    s += text(320, 250, "буває — від підробки", 9.5, INK, "start")
    s += text(W / 2, H - 12, "Бери даташит із сайту виробника й перевіряй ревізію (дату/літеру) — стара версія може брехати про вже виправлене.",
              9, GREY, "middle", style="italic")
    save("fig-r09-1-6-find.svg", s)


# ── §2.9.4 Графіки: derating, ВАХ, температурні залежності (Рис. 2.9.4.k) ────
def fig194_why_graphs():
    """Чому графік, а не таблиця: число — точка, графік — уся крива."""
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 28, "Чому графік, а не таблиця: число — лише одна точка", 14.5, INK, "middle", "bold")
    # ліворуч — таблиця з кількома точками
    s += _frame(36, 56, 300, 224, "таблиця: кілька точок")
    rows = [("25 °C", "20 мОм"), ("85 °C", "30 мОм"), ("125 °C", "40 мОм")]
    s += rect(56, 78, 260, 30, "#eef2f7", "#7f93a8", 1.3, 5)
    s += text(70, 98, "Темп.", 10.5, INK, "start", "bold") + text(300, 98, "Rds(on)", 10.5, INK, "end", "bold")
    for i, (k, v) in enumerate(rows):
        y = 108 + i * 34
        s += rect(56, y, 260, 34, "#ffffff", "#c9d3dc", 1.1, 0)
        s += text(70, y + 22, k, 10, INK, "start") + text(300, y + 22, v, 10, INK, "end", "bold")
    s += text(186, 252, "а між ними? а при 60 °C?", 9.5, RED, "middle", "bold")
    # праворуч — графік як неперервна крива
    ox, oy, pw, ph = 410, 248, 250, 170
    s += _axes(ox, oy, pw, ph, "T (°C)", "Rds")
    pts = []
    for j in range(0, 141):
        t = j / 140.0
        # від 20 до 40 мОм нелінійно (наростає швидше у спеку)
        v = 0.18 + 0.62 * (t ** 1.4)
        pts.append((ox + pw * t, oy - ph * v))
    s += _poly(pts, BLUE, 2.6)
    for (tx, lab) in [(0.0, "25"), (0.55, "85"), (1.0, "125")]:
        s += line(ox + pw * tx, oy, ox + pw * tx, oy + 5, INK, 1.2) + text(ox + pw * tx, oy + 18, lab, 8.5, INK, "middle")
    s += text(ox + pw * 0.5, oy - ph - 4, "будь-яка точка читається", 9, GREEN, "middle", "bold")
    s += text(W / 2, H - 12, "Графік дає значення для БУДЬ-ЯКИХ умов у діапазоні, а не лише для кількох рядків таблиці.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4-1-why-graphs.svg", s)


def fig194_derating():
    """Derating-крива потужності від температури корпусу."""
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 28, "Derating: дозволена потужність падає з температурою", 14.5, INK, "middle", "bold")
    ox, oy, pw, ph = 90, 268, 540, 196
    s += _axes(ox, oy, pw, ph, "темп. корпусу Tc (°C)", "P (Вт)")
    # вісь X: 0..150 °C
    def xT(t):
        return ox + pw * t / 150.0
    def yP(p):
        return oy - ph * p / 2.2  # макс ~2 Вт
    for t in (0, 25, 50, 75, 100, 125, 150):
        s += line(xT(t), oy, xT(t), oy + 5, INK, 1.2) + text(xT(t), oy + 18, str(t), 8.5, INK, "middle")
    for p in (0.5, 1.0, 1.5, 2.0):
        s += line(ox, yP(p), ox - 5, yP(p), INK, 1.2) + text(ox - 9, yP(p) + 4, f"{p:.1f}", 8.5, INK, "end")
    # плато до 25 °C (P_max=2 Вт), потім лінійний спад до 0 при 150 °C (Tj_max)
    s += line(xT(0), yP(2.0), xT(25), yP(2.0), GREEN, 3)
    s += line(xT(25), yP(2.0), xT(150), yP(0.0), GREEN, 3)
    s += text(xT(12), yP(2.0) - 10, "плато P_max", 9, GREEN, "middle", "bold")
    s += line(xT(25), oy, xT(25), yP(2.0), GREY, 1.2, "4 3") + text(xT(25), oy + 32, "точка зламу", 8.5, GREY, "middle")
    # приклад зчитування при 100 °C
    s += line(xT(100), oy, xT(100), yP(0.8), RED, 1.6, "5 4")
    s += line(ox, yP(0.8), xT(100), yP(0.8), RED, 1.6, "5 4")
    s += circle(xT(100), yP(0.8), 4.5, RED, "#ffffff", 2)
    s += text(xT(100) + 8, yP(0.8) - 8, "при 100 °C — лише 0.8 Вт!", 9.5, RED, "start", "bold")
    s += text(xT(70), yP(1.55), "нахил =", 9, INK, "middle")
    s += text(xT(70), yP(1.55) - 14, "−1/Rθ", 9, INK, "middle", "bold")
    s += text(W / 2, H - 12, "«2 Вт» дійсні лише до точки зламу. У спеку дозволена потужність спадає по прямій аж до нуля при Tj_max.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-4-2-derating.svg", s)


def fig194_iv_curve():
    """ВАХ діода: лінійна й логарифмічна осі — одне й те саме коліно."""
    W, H = 720, 330
    s = header(W, H)
    s += text(W / 2, 26, "ВАХ діода: те саме коліно на двох осях", 15, INK, "middle", "bold")
    # ── лінійна ──
    ox, oy, pw, ph = 80, 258, 250, 180
    s += _axes(ox, oy, pw, ph, "V", "I")
    s += text(ox + pw / 2, oy - ph - 22, "лінійна вісь I", 11, INK, "middle", "bold")
    pts = []
    for j in range(0, 161):
        v = 0.95 * j / 160.0
        i = math.exp((v - 0.62) / 0.045)
        pts.append((ox + pw * v / 0.95, oy - ph * min(i, 1.0) * 0.9))
    s += _poly(pts, BLUE, 2.6)
    s += text(ox + pw * 0.66, oy - 20, "коліно", 9, INK, "middle") + text(ox + pw * 0.66, oy - 8, "≈0.7 В", 9, INK, "middle", "bold")
    s += text(ox + pw * 0.2, oy - ph * 0.75, "різкий", 8.5, GREY, "middle")
    s += text(ox + pw * 0.2, oy - ph * 0.75 + 12, "злам", 8.5, GREY, "middle")
    # ── напівлог ──
    ox2, oy2 = 420, 258
    s += _axes(ox2, oy2, pw, ph, "V", "log I")
    s += text(ox2 + pw / 2, oy2 - ph - 22, "логарифмічна вісь I", 11, INK, "middle", "bold")
    # декади сітки
    for k in range(0, 5):
        yy = oy2 - ph * (k + 0.4) / 5.0
        s += line(ox2, yy, ox2 + pw, yy, FAINT, 1) + text(ox2 - 6, yy + 4, f"10{['⁻⁶','⁻⁵','⁻⁴','⁻³','⁻²'][k]}", 8, GREY, "end")
    pts2 = []
    for j in range(5, 161):
        v = 0.95 * j / 160.0
        li = (v - 0.62) / 0.045  # лінійно в логарифмі
        yy = oy2 - ph * (0.4 + (li + 4) ) / 5.0
        if oy2 - ph - 6 < yy < oy2:
            pts2.append((ox2 + pw * v / 0.95, yy))
    s += _poly(pts2, BLUE, 2.6)
    s += text(ox2 + pw * 0.5, oy2 - ph * 0.55, "пряма!", 9.5, GREEN, "middle", "bold")
    s += text(ox2 + pw * 0.5, oy2 - ph * 0.55 + 13, "(експонента)", 8, GREEN, "middle")
    s += text(W / 2, H - 10, "Експонента на лінійній осі — різке «коліно»; на логарифмічній — пряма. Та сама ВАХ, лише інша вісь.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4-3-iv-curve.svg", s)


def fig194_log_axis():
    """Як читати логарифмічну вісь: декади й нерівномірна сітка."""
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Логарифмічна вісь: сітка нерівномірна — не обманись", 14.5, INK, "middle", "bold")
    ox, oy, pw = 70, 150, 560
    s += line(ox, oy, ox + pw, oy, INK, 2)
    # три декади: 1..10..100..1000
    decades = ["1", "10", "100", "1k"]
    for d in range(4):
        x0 = ox + pw * d / 3.0
        s += line(x0, oy - 6, x0, oy + 6, INK, 2) + text(x0, oy + 24, decades[d], 11, INK, "middle", "bold")
        if d < 3:
            for m in range(2, 10):
                xm = ox + pw * (d + math.log10(m)) / 3.0
                s += line(xm, oy - 4, xm, oy + 4, GREY, 1.2)
                if m in (2, 5):
                    s += text(xm, oy + 18, str(m * (10 ** d)), 8, GREY, "middle")
    s += text(ox + pw * 0.5 / 3.0, oy - 22, "тут поділки", 8.5, RED, "middle")
    s += text(ox + pw * 0.5 / 3.0, oy - 10, "густі", 8.5, RED, "middle", "bold")
    s += text(ox + pw * 2.5 / 3.0, oy - 22, "тут — рідкі", 8.5, RED, "middle", "bold")
    s += text(W / 2, oy + 64, "Однакова відстань = множення на 10, а не додавання. Між 1 і 2 — широко, між 9 і 10 — вузько.",
              10, INK, "middle")
    s += text(W / 2, oy + 88, "Половина між «1» і «10» на осі — це НЕ 5, а ≈3.16 (√10).", 10, RED, "middle", "bold")
    s += text(W / 2, H - 12, "Дуже легко зчитати число втричі-вчетверо хибно, якщо читати лог-вісь як лінійну.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4-4-log-axis.svg", s)


def fig194_read_point():
    """Як зняти значення з кривої: вертикаль → крива → горизонталь."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Як зняти число з графіка: трьома лініями", 15, INK, "middle", "bold")
    ox, oy, pw, ph = 100, 256, 500, 190
    s += _axes(ox, oy, pw, ph, "температура", "параметр")
    # сітка
    for k in range(1, 5):
        s += line(ox, oy - ph * k / 4, ox + pw, oy - ph * k / 4, FAINT, 1)
        s += line(ox + pw * k / 4, oy, ox + pw * k / 4, oy - ph, FAINT, 1)
    pts = []
    for j in range(0, 201):
        t = j / 200.0
        v = 0.2 + 0.65 * (t ** 1.25)
        pts.append((ox + pw * t, oy - ph * v))
    s += _poly(pts, BLUE, 2.6)
    # робоча точка t=0.6
    t0 = 0.6
    v0 = 0.2 + 0.65 * (t0 ** 1.25)
    px, py = ox + pw * t0, oy - ph * v0
    s += arrow(ox + pw * t0, oy, ox + pw * t0, py + 6, RED, 2)
    s += text(ox + pw * t0, oy + 18, "1) твоя умова", 9, RED, "middle", "bold")
    s += circle(px, py, 5, RED, "#ffffff", 2) + text(px + 10, py - 8, "2) до кривої", 9, RED, "start", "bold")
    s += arrow(px, py, ox + 6, py, RED, 2)
    s += text(ox + 6, py - 8, "3) читай значення", 9, RED, "start", "bold")
    s += text(W / 2, H - 12, "Від своєї умови — вгору до кривої, тоді вбік на вісь параметра. Звіряй, лінійна вісь чи логарифмічна.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4-5-read-point.svg", s)


def fig194_curve_zoo():
    """Звіринець типових графіків даташита."""
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 26, "Типові графіки даташита: що кожен каже", 15, INK, "middle", "bold")
    cards = [
        (40, 56, "Derating потужності", "плато, тоді спад", "down"),
        (290, 56, "Rds(on) від темп.", "росте у спеку", "up"),
        (540, 56, "ВАХ (I від V)", "експонента-коліно", "exp"),
        (40, 210, "Підсилення від частоти", "падає (−20 дБ/дек)", "downlog"),
        (290, 210, "hFE від струму", "горб посередині", "hump"),
        (540, 210, "Iq від напруги", "повільно росте", "up"),
    ]
    cw, ch = 180, 120
    for x, y, t1, t2, kind in cards:
        s += _frame(x, y, cw, ch, t1)
        gx, gy, gw, gh = x + 24, y + ch - 24, cw - 44, ch - 50
        s += line(gx, gy, gx + gw, gy, INK, 1.4)
        s += line(gx, gy, gx, gy - gh, INK, 1.4)
        pts = []
        for j in range(0, 81):
            u = j / 80.0
            if kind == "down":
                v = 1.0 if u < 0.3 else max(0.0, 1.0 - (u - 0.3) / 0.7)
            elif kind == "up":
                v = 0.2 + 0.7 * u ** 1.3
            elif kind == "exp":
                v = min(1.0, math.exp((u - 0.7) / 0.08))
            elif kind == "downlog":
                v = 0.95 if u < 0.3 else max(0.05, 0.95 - (u - 0.3) * 1.3)
            elif kind == "hump":
                v = 0.25 + 0.7 * math.exp(-((u - 0.5) ** 2) / 0.04)
            else:
                v = 0.25 + 0.5 * u
            pts.append((gx + gw * u, gy - gh * v))
        s += _poly(pts, BLUE, 2.2)
        s += text(x + cw / 2, y + ch - 6, t2, 8.5, GREY, "middle")
    s += text(W / 2, H - 12, "Форма кривої зразу підказує поведінку: спад derating, ріст опору у спеку, коліно ВАХ, завал підсилення.",
              9, GREY, "middle", style="italic")
    save("fig-r09-4-6-curve-zoo.svg", s)


# ── §2.9.5 Корпуси, маркування, розпіновка (Рис. 2.9.5.k) ────────────────────
def fig195_tht_smd():
    """THT проти SMD: дві сім'ї монтажу."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Два світи корпусів: вивідний (THT) і поверхневий (SMD)", 14, INK, "middle", "bold")
    # THT — DIP із ніжками крізь плату
    s += _frame(40, 56, 300, 234, "THT — у наскрізні отвори")
    bx, by = 110, 120
    s += rect(bx, by, 160, 70, "#2a2a2a", "#000", 1.5, 4) + text(bx + 80, by + 42, "DIP-8", 13, "#fff", "middle", "bold")
    s += rect(70, by + 96, 240, 10, "#cfe0c8", GREEN, 1.2, 0) + text(190, by + 122, "плата", 9, GREEN, "middle")
    for i in range(4):
        xx = bx + 22 + i * 38
        s += line(xx, by + 70, xx, by + 112, INK, 2.4)
        s += line(bx + 22 + i * 38, by, bx + 22 + i * 38, by + 70, "#777", 6)
    s += text(190, 276, "ніжки прошивають плату наскрізь — міцно, легко паяти вручну", 8.8, INK, "middle")
    # SMD — чип на поверхні
    s += _frame(360, 56, 300, 234, "SMD — на поверхню")
    cx, cy = 440, 130
    s += rect(cx, cy, 140, 56, "#2a2a2a", "#000", 1.5, 4) + text(cx + 70, cy + 34, "SOIC", 12, "#fff", "middle", "bold")
    s += rect(400, cy + 70, 220, 10, "#cfe0c8", GREEN, 1.2, 0) + text(510, cy + 116, "плата", 9, GREEN, "middle")
    for i in range(4):
        xx = cx + 14 + i * 38
        s += rect(xx, cy + 56, 14, 16, "#bdbdbd", "#777", 1, 0)
        s += rect(xx - 4, cy + 70, 22, 6, SUN, "#a07a16", 1, 1)  # припій
    s += text(510, 276, "контакти лежать на майданчиках — дрібно, компактно, під автоскладання", 8.5, INK, "middle")
    s += text(W / 2, H - 10, "THT тримається ніжками крізь отвори; SMD припаяний до майданчиків зверху. Звідси — різні корпуси й розміри.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-5-1-tht-smd.svg", s)


def fig195_package_zoo():
    """Галерея корпусів із масштабом."""
    W, H = 720, 340
    s = header(W, H)
    s += text(W / 2, 26, "Корпуси на одну шкалу: від DIP до QFN", 15, INK, "middle", "bold")
    items = [
        ("DIP-8", 150, 70, 8, "вивідний, 2.54 мм крок"),
        ("SOIC-8", 96, 44, 8, "SMD, паяється вручну"),
        ("SOT-23", 44, 30, 3, "крихітний, 3 ніжки"),
        ("TQFP-32", 80, 80, 32, "ніжки по 4 боках"),
        ("QFN-20", 56, 56, 0, "контакти ЗНИЗУ — лише фен"),
    ]
    x = 50
    for name, w, h, pins, note in items:
        cy = 150
        s += rect(x, cy - h / 2, w, h, "#2a2a2a", "#000", 1.4, 4)
        s += text(x + w / 2, cy + 4, name, 9.5, "#fff", "middle", "bold")
        # ніжки (схематично)
        if name == "SOT-23":
            for dx in (10, w - 10):
                s += rect(x + dx - 3, cy - h / 2 - 8, 6, 8, "#bbb", "#777", 1)
            s += rect(x + w / 2 - 3, cy + h / 2, 6, 8, "#bbb", "#777", 1)
        elif name == "QFN-20":
            s += text(x + w / 2, cy + h / 2 + 18, "(контакти знизу)", 7.5, RED, "middle", "bold")
        elif pins:
            n = min(pins // 2, 6)
            for k in range(n):
                xx = x + (w / (n + 1)) * (k + 1)
                s += rect(xx - 2.5, cy - h / 2 - 7, 5, 7, "#bbb", "#777", 1)
                s += rect(xx - 2.5, cy + h / 2, 5, 7, "#bbb", "#777", 1)
        s += text(x + w / 2, cy + h / 2 + 34, note, 7.5, GREY, "middle")
        x += w + 36
    s += text(W / 2, H - 14, "Усі в одному масштабі: той самий чип буває у великому вивідному корпусі й у мікроскопічному SMD.",
              9, GREY, "middle", style="italic")
    save("fig-r09-5-2-package-zoo.svg", s)


def fig195_pin1():
    """Де перша ніжка: ключ, крапка, фаска."""
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Перша ніжка: знайди ключ — інакше все дзеркально", 14, INK, "middle", "bold")
    # DIP з виїмкою
    s += _frame(40, 56, 200, 210, "DIP — виїмка-«ключ»")
    bx, by, bw, bh = 90, 96, 100, 130
    s += rect(bx, by, bw, bh, "#2a2a2a", "#000", 1.5, 4)
    s += f'<path d="M {bx + bw/2 - 14},{by} A 14 14 0 0 0 {bx + bw/2 + 14},{by}" fill="#0d0d0d" stroke="#000" stroke-width="1"/>\n'
    s += circle(bx + 16, by + 20, 5, RED, RED, 1)
    s += text(bx + 16, by + 40, "1", 11, "#fff", "middle", "bold")
    for i in range(4):
        s += text(bx - 10, by + 20 + i * 30, str(i + 1), 9, INK, "end")
        s += text(bx + bw + 10, by + 20 + i * 30, str(8 - i), 9, INK, "start")
    s += text(140, 252, "виїмка зверху → ніжка 1 ліворуч від неї", 8.5, INK, "middle")
    # SOIC з крапкою
    s += _frame(260, 56, 200, 210, "SMD — крапка біля піна 1")
    cx, cy, cw2, ch2 = 305, 110, 110, 90
    s += rect(cx, cy, cw2, ch2, "#2a2a2a", "#000", 1.5, 4)
    s += circle(cx + 16, cy + 16, 5, "#fff", "#fff", 1)
    s += text(cx + cw2 / 2, cy + 52, "крапка", 9, "#fff", "middle")
    s += text(360, 252, "втиснена крапка/скіс позначає перший контакт", 8.5, INK, "middle")
    # напрям нумерації
    s += _frame(480, 56, 180, 210, "далі — проти годинн.")
    nx, ny = 540, 150
    s += circle(nx, ny, 40, "none", INK, 1.6)
    s += arrow(nx - 28, ny - 28, nx - 34, ny + 6, BLUE, 2)
    s += circle(nx - 30, ny - 30, 4, RED, RED, 1) + text(nx - 30, ny - 40, "1", 10, RED, "middle", "bold")
    s += text(nx, ny + 4, "2,3,4…", 9, INK, "middle")
    s += text(570, 252, "нумерація — проти годинникової стрілки", 8, INK, "middle")
    s += text(W / 2, H - 10, "Переплутав перший пін — розвів плату дзеркально. Завжди звіряй вид: даташит малює корпус ЗВЕРХУ (top view).",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-5-3-pin1.svg", s)


def fig195_pinout():
    """Розпіновка: top view, мнемоніки сторін."""
    W, H = 640, 340
    s = header(W, H)
    s += text(W / 2, 28, "Карта розпіновки: top view 8-вивідного ОП", 15, INK, "middle", "bold")
    bx, by, bw, bh = 230, 80, 180, 200
    s += rect(bx, by, bw, bh, "#f3f5f8", "#7f93a8", 2, 8)
    s += f'<path d="M {bx + bw/2 - 16},{by} A 16 16 0 0 0 {bx + bw/2 + 16},{by}" fill="none" stroke="#7f93a8" stroke-width="2"/>\n'
    left = ["OUT1", "IN1−", "IN1+", "V−"]
    right = ["V+", "OUT2", "IN2−", "IN2+"]
    for i in range(4):
        y = by + 34 + i * 44
        s += line(bx, y, bx - 40, y, INK, 2) + circle(bx - 40, y, 4, INK, "#fff", 1.6)
        s += text(bx - 48, y - 6, str(i + 1), 9, GREY, "end") + text(bx - 48, y + 12, left[i], 9.5, INK, "end", "bold")
        yr = by + 34 + (3 - i) * 44
        s += line(bx + bw, yr, bx + bw + 40, yr, INK, 2) + circle(bx + bw + 40, yr, 4, INK, "#fff", 1.6)
        s += text(bx + bw + 48, yr - 6, str(8 - i), 9, GREY, "start") + text(bx + bw + 48, yr + 12, right[i], 9.5, INK, "start", "bold")
    s += circle(bx + 16, by + 18, 4, RED, RED, 1) + text(bx + 16, by + 38, "1", 10, INK, "middle", "bold")
    s += text(bx + bw / 2, by + bh / 2, "TOP", 13, GREY, "middle", "bold")
    s += text(bx + bw / 2, by + bh / 2 + 18, "VIEW", 13, GREY, "middle", "bold")
    s += text(W / 2, H - 28, "Живлення часто по діагоналі (V− піна 4, V+ піна 8). Той самий значок «+»/«−» — входи, не живлення!",
              9.5, INK, "middle")
    s += text(W / 2, H - 10, "Розпіновку завжди дають як вид ЗВЕРХУ; для монтажу знизу подумки віддзеркаль.",
              9, GREY, "middle", style="italic")
    save("fig-r09-5-4-pinout.svg", s)


def fig195_marking():
    """Маркування: повне на великому, код на дрібному."""
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Маркування: чим дрібніший корпус — тим коротший код", 14, INK, "middle", "bold")
    # великий корпус — повний напис
    s += _frame(40, 56, 300, 210, "великий корпус — усе видно")
    bx, by = 90, 110
    s += rect(bx, by, 200, 90, "#2a2a2a", "#000", 1.5, 6)
    s += text(bx + 100, by + 32, "LM358N", 15, "#fff", "middle", "bold")
    s += text(bx + 100, by + 56, "TI  24A1", 11, "#cfcfcf", "middle")
    s += text(bx + 100, by + 76, "(дата-код)", 8.5, "#9b9b9b", "middle")
    s += text(190, 252, "номер, виробник, дата — усе читається прямо", 8.5, INK, "middle")
    # дрібний корпус — код
    s += _frame(360, 56, 300, 210, "SOT-23 — лише код")
    cx, cy = 430, 120
    s += rect(cx, cy, 90, 60, "#2a2a2a", "#000", 1.5, 4)
    s += text(cx + 45, cy + 38, "A7W", 16, "#fff", "middle", "bold")
    s += arrow(cx + 100, cy + 30, cx + 150, cy + 30, GREY, 2)
    s += rect(cx + 155, cy, 110, 60, LGRN, GREEN, 1.4, 6)
    s += text(cx + 210, cy + 24, "таблиця кодів", 9, GREEN, "middle", "bold")
    s += text(cx + 210, cy + 44, "A7W → BAS40", 9, INK, "middle")
    s += text(510, 252, "код-загадка: розшифровуй за таблицею в даташиті", 8.3, INK, "middle")
    s += text(W / 2, H - 10, "На дрібний SMD повний напис не влазить — ставлять 2–3-символьний код, який шукають у таблиці маркування.",
              8.6, GREY, "middle", style="italic")
    save("fig-r09-5-5-marking.svg", s)


def fig195_ordering():
    """Розшифровка коду замовлення (ordering information)."""
    W, H = 700, 290
    s = header(W, H)
    s += text(W / 2, 28, "Код замовлення: один номер — багато сенсів", 15, INK, "middle", "bold")
    base = "LM358"
    parts = [
        ("LM358", "сімейство", INK, "#eef2f7"),
        ("I", "темп. сорт (−40…85)", GREEN, LGRN),
        ("D", "корпус (SOIC)", BLUE, LBLUE),
        ("R", "стрічка/котушка", SUN, "#fff3e0"),
    ]
    x = 90
    seg_y = 90
    for txt, lab, col, fill in parts:
        w = 30 + 26 * len(txt)
        s += rect(x, seg_y, w, 46, fill, col, 1.8, 6)
        s += text(x + w / 2, seg_y + 30, txt, 17, col, "middle", "bold")
        s += arrow(x + w / 2, seg_y + 56, x + w / 2, seg_y + 86, GREY, 1.8)
        s += text(x + w / 2, seg_y + 104, lab, 9, INK, "middle")
        x += w + 10
    s += text(W / 2, 210, "Один суфікс — і це вже інший корпус, інший температурний сорт чи інша фасовка.", 10, INK, "middle")
    s += text(W / 2, 232, "Замовиш не той суфікс — приїде той самий чип, але в корпусі, що не влазить у плату.", 9.5, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Таблиця Ordering Information розшифровує кожну літеру номера. Звіряй корпус і сорт ПЕРЕД замовленням.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-5-6-ordering.svg", s)


# ── §2.9.6 Дрібний шрифт: примітки, умови тестів, errata (Рис. 2.9.6.k) ───────
def fig196_footnotes():
    """Виноска міняє сенс числа."""
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Виноска — не дрібниця: вона міняє сенс числа", 14.5, INK, "middle", "bold")
    # рядок таблиці з зірочкою
    s += rect(50, 70, 600, 44, "#ffffff", "#c9d3dc", 1.3, 6)
    s += text(66, 98, "Вихідний струм", 11, INK, "start")
    s += text(360, 98, "85 мА", 13, GREEN, "middle", "bold")
    s += text(404, 88, "(1)", 10, RED, "start", "bold")
    s += text(560, 98, "@ 25 °C", 10, INK, "middle")
    s += arrow(404, 116, 404, 150, RED, 2)
    # сама виноска
    s += rect(50, 156, 600, 78, LRED, RED, 1.4, 6)
    s += text(66, 180, "(1) виміряно імпульсом 300 мкс, шпаруватість < 2 %;", 11, INK, "start", "bold")
    s += text(66, 202, "тривалий струм значно менший — див. derating (§2.9.4).", 11, INK, "start")
    s += text(66, 222, "Без виноски ти б узяв 85 мА за тривалий — і спалив прилад.", 9.5, RED, "start", "bold")
    s += text(W / 2, H - 12, "Маленький значок «(1)» біля числа веде до рядка внизу сторінки, що часто повністю змінює, як число читати.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-6-1-footnotes.svg", s)


def fig196_test_conditions():
    """Те саме число — інша умова тесту — інша правда."""
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Умови тесту: лабораторні vs твоя плата", 15, INK, "middle", "bold")
    # лабораторія
    s += _frame(40, 56, 300, 214, "як міряв виробник")
    s += text(190, 86, "θJA = 50 °C/Вт", 12, GREEN, "middle", "bold")
    items = ["• плата 4 шари", "• мідний полігон 1 дюйм²", "• нерухоме повітря", "• 25 °C"]
    for i, it in enumerate(items):
        s += text(70, 116 + i * 26, it, 10, INK, "start")
    s += text(190, 248, "ідеальні умови = найкраще число", 8.8, GREEN, "middle")
    # реальність
    s += _frame(360, 56, 300, 214, "як на твоїй платі")
    s += text(510, 86, "θJA ≈ 120 °C/Вт", 12, RED, "middle", "bold")
    items2 = ["• плата 2 шари", "• крихітний майданчик", "• у тісному корпусі", "• поряд гарячі сусіди"]
    for i, it in enumerate(items2):
        s += text(390, 116 + i * 26, it, 10, INK, "start")
    s += text(510, 248, "удвічі-втричі гірше тепловідведення", 8.8, RED, "middle", "bold")
    s += arrow(342, 150, 358, 150, GREY, 2.2)
    s += text(W / 2, H - 12, "Число дане за лабораторних умов. Твої — інші, тож реальний результат гірший. Завжди читай рядок Conditions.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-6-2-test-conditions.svg", s)


def fig196_typ_only():
    """Параметр лише як 'typ', без гарантованих меж."""
    W, H = 700, 280
    s = header(W, H)
    s += text(W / 2, 28, "Підступ дрібного шрифту: «лише typ, не гарантовано»", 14, INK, "middle", "bold")
    s += rect(50, 64, 600, 40, "#eef2f7", "#7f93a8", 1.4, 6)
    for name, x in [("Параметр", 70), ("Min", 330), ("Typ", 430), ("Max", 540)]:
        col = GREEN if name in ("Min", "Max") else (SUN if name == "Typ" else INK)
        s += text(x, 90, name, 11, col, "start", "bold")
    rows = [("Зсув Vos", "−2", "0.3", "2", False),
            ("Темп. дрейф", "—", "5", "—", True)]
    for i, (k, mn, tp, mx, only) in enumerate(rows):
        y = 104 + i * 40
        s += rect(50, y, 600, 40, LRED if only else "#fff", RED if only else "#c9d3dc", 1.4 if only else 1.1, 0)
        s += text(70, y + 26, k, 10.5, INK, "start")
        s += text(330, y + 26, mn, 10, GREEN if mn != "—" else GREY, "start", "bold" if mn != "—" else "normal")
        s += text(430, y + 26, tp, 10, SUN, "start", "bold")
        s += text(540, y + 26, mx, 10, GREEN if mx != "—" else GREY, "start", "bold" if mx != "—" else "normal")
        if only:
            s += text(620, y + 26, "← пастка", 9.5, RED, "start", "bold")
    s += text(W / 2, 222, "Другий рядок має min=max=«—»: гарантованих меж НЕМАЄ, лише typ.", 10.5, RED, "middle", "bold")
    s += text(W / 2, 244, "Таке число — суто довідкове; закладати його в розрахунок надійності не можна.", 10, INK, "middle")
    s += text(W / 2, H - 10, "Інколи важливий параметр дають без гарантій — лише «typ». Це треба помітити, а не взяти за обіцянку.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-6-3-typ-only.svg", s)


def fig196_revision():
    """Ревізія й історія змін — стара версія бреше."""
    W, H = 700, 300
    s = header(W, H)
    s += text(W / 2, 28, "Ревізія документа: стара версія може брехати", 15, INK, "middle", "bold")
    revs = [
        ("Rev A", "2019", "перший випуск", GREY, "#f0f0f0"),
        ("Rev B", "2021", "уточнено Iq", BLUE, LBLUE),
        ("Rev D", "2024", "виправлено розпіновку!", GREEN, LGRN),
    ]
    x = 70
    for tag, yr, note, col, fill in revs:
        s += rect(x, 70, 170, 90, fill, col, 1.6, 8)
        s += text(x + 85, 96, tag, 14, col, "middle", "bold")
        s += text(x + 85, 118, yr, 10, INK, "middle")
        s += text(x + 85, 140, note, 8.8, INK, "middle")
        if x < 400:
            s += arrow(x + 170, 115, x + 200, 115, GREY, 2)
        x += 200
    s += rect(70, 180, 570, 56, LRED, RED, 1.4, 6)
    s += text(86, 204, "Стара Rev A показує неправильну розпіновку.", 10.5, RED, "start", "bold")
    s += text(86, 224, "Розведеш плату по ній — і все дзеркально. Завжди бери найновішу ревізію.", 10, INK, "start")
    s += text(W / 2, H - 10, "Ревізія стоїть у кутку сторінки, історія змін — наприкінці. Скачуй найсвіжішу копію з сайту виробника.",
              8.8, GREY, "middle", style="italic")
    save("fig-r09-6-4-revision.svg", s)


def fig196_errata():
    """Errata: окремий список «прилад працює не так, як у даташиті»."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Errata: офіційний список «а отут воно бреше»", 15, INK, "middle", "bold")
    s += _docpage(60, 56, 360, 240)
    s += text(240, 84, "ERRATA · Rev 1.6", 13, RED, "middle", "bold")
    s += line(80, 96, 400, 96, FAINT, 1.4)
    bugs = [
        ("E1", "UART губить байт при wake-up"),
        ("E2", "ADC: зайвий зсув на каналі 0"),
        ("E3", "I²C зависає на clock-stretch"),
    ]
    for i, (n, d) in enumerate(bugs):
        y = 120 + i * 50
        s += circle(96, y, 11, LRED, RED, 1.6) + text(96, y + 4, n, 9.5, RED, "middle", "bold")
        s += text(116, y - 2, d, 9.8, INK, "start", "bold")
        s += text(116, y + 16, "обхід: див. опис →", 8.3, GREY, "start")
    s += rect(450, 80, 200, 90, LGRN, GREEN, 1.4, 8)
    s += text(550, 104, "обхід (workaround)", 10, GREEN, "middle", "bold")
    s += text(550, 128, "програмний прийом,", 9, INK, "middle")
    s += text(550, 146, "що оминає баг кремнію", 9, INK, "middle")
    s += text(550, 210, "Чому це критично:", 10.5, INK, "middle", "bold")
    s += text(550, 232, "«мій код правильний,", 9.3, INK, "middle")
    s += text(550, 250, "а воно не працює» —", 9.3, INK, "middle")
    s += text(550, 268, "часто це відомий errata-баг", 9.3, RED, "middle", "bold")
    s += text(W / 2, H - 10, "Errata — окремий документ помилок самого кремнію (не друкарських). Перевір його ПЕРШ ніж місяць шукати «свій» баг.",
              8.6, GREY, "middle", style="italic")
    save("fig-r09-6-5-errata.svg", s)


# ── §2.9.7 Практикум: діод, MOSFET, ОП (Рис. 2.9.7.k) ────────────────────────
def fig197_diode():
    """Практикум: ключові рядки даташита діода."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Практикум: даташит діода — що шукати", 15, INK, "middle", "bold")
    rows = [
        ("VRRM", "макс. зворотна напруга", "100 В", "abs", "щоб не пробило зворотним"),
        ("IF(av)", "тривалий прямий струм", "1 А", "rec", "скільки тягне без перегріву"),
        ("IFSM", "пік. струм (одиничний)", "30 А", "abs", "кидок при ввімкненні"),
        ("VF", "пряме падіння @ IF", "0.7 В (max 1.0)", "ec", "втрати й нагрів"),
        ("trr", "час відновлення", "4 нс / 2 мкс", "ec", "швидкий чи повільний"),
    ]
    y0 = 60
    for i, (sym, name, val, kind, why) in enumerate(rows):
        y = y0 + i * 48
        fill = LRED if kind == "abs" else (LGRN if kind == "rec" else "#eef2f7")
        col = RED if kind == "abs" else (GREEN if kind == "rec" else BLUE)
        s += rect(46, y, 120, 40, fill, col, 1.4, 6) + text(106, y + 19, sym, 12, col, "middle", "bold")
        s += text(106, y + 34, name, 7.6, INK, "middle")
        s += text(182, y + 25, val, 11, INK, "start", "bold")
        s += text(360, y + 25, why, 9.5, GREY, "start")
    s += text(W / 2, H - 24, "Червоне — Absolute Maximum (не перейди), зелене — Recommended, синє — параметр.", 9, INK, "middle")
    s += text(W / 2, H - 8, "Вибір діода: VRRM з запасом, IF під свій струм, trr — якщо комутація швидка.", 8.8, GREY, "middle", style="italic")
    save("fig-r09-7-1-diode.svg", s)


def fig197_mosfet():
    """Практикум: ключові рядки даташита MOSFET."""
    W, H = 700, 330
    s = header(W, H)
    s += text(W / 2, 28, "Практикум: даташит MOSFET — що шукати", 15, INK, "middle", "bold")
    rows = [
        ("VDS", "макс. напруга стік-витік", "60 В", "abs"),
        ("VGS", "макс. напруга затвора", "±20 В", "abs"),
        ("ID", "тривалий струм стоку", "30 А @ 25 °C", "rec"),
        ("Rds(on)", "опір відкритого @ VGS", "8 мОм @ 10 В", "ec"),
        ("VGS(th)", "поріг відкриття", "1.5…3 В", "ec"),
        ("Qg", "заряд затвора", "25 нКл", "ec"),
    ]
    y0 = 58
    for i, (sym, name, val, kind) in enumerate(rows):
        y = y0 + i * 42
        fill = LRED if kind == "abs" else (LGRN if kind == "rec" else "#eef2f7")
        col = RED if kind == "abs" else (GREEN if kind == "rec" else BLUE)
        s += rect(46, y, 130, 36, fill, col, 1.4, 6) + text(111, y + 17, sym, 12, col, "middle", "bold")
        s += text(111, y + 31, name, 7.2, INK, "middle")
        s += text(192, y + 23, val, 11, INK, "start", "bold")
    # бічна підказка про logic-level
    s += rect(420, 58, 240, 110, "#fff3e0", SUN, 1.4, 8)
    s += text(540, 82, "пастка VGS(th)", 11, "#b07d1e", "middle", "bold")
    s += text(540, 106, "поріг до 3 В НЕ означає", 9, INK, "middle")
    s += text(540, 124, "повне відкриття від 3.3 В!", 9, RED, "middle", "bold")
    s += text(540, 144, "Rds(on) дають @ 10 В —", 9, INK, "middle")
    s += text(540, 162, "звіряй криву Rds(VGS).", 9, INK, "middle")
    s += rect(420, 182, 240, 84, LGRN, GREEN, 1.4, 8)
    s += text(540, 204, "тепловий ланцюг", 10.5, GREEN, "middle", "bold")
    s += text(540, 226, "I²·Rds(on) → нагрів →", 9, INK, "middle")
    s += text(540, 244, "Rds(on) ще росте (§2.9.4)", 9, INK, "middle")
    s += text(W / 2, H - 10, "Силовий ключ: VDS і VGS — священні межі; Rds(on) і Qg — втрати; VGS(th) і крива Rds(VGS) — чи відкриється від твоєї логіки.",
              8.3, GREY, "middle", style="italic")
    save("fig-r09-7-2-mosfet.svg", s)


def fig197_opamp():
    """Практикум: ключові рядки даташита ОП."""
    W, H = 700, 320
    s = header(W, H)
    s += text(W / 2, 28, "Практикум: даташит ОП — що шукати", 15, INK, "middle", "bold")
    rows = [
        ("Vsupply", "діапазон живлення", "1.8…5.5 В", "rec", "влізе у твою шину 3.3 В?"),
        ("Vos", "напруга зсуву", "max 3 мВ", "ec", "похибка постійної складової"),
        ("Ib", "вхідний струм", "max 10 нА", "ec", "критичний для високоомних"),
        ("GBW", "добуток підс.×смуга", "min 8 МГц", "ec", "чи встигне за сигналом"),
        ("SR", "швидкість наростання", "min 5 В/мкс", "ec", "великий розмах на ВЧ"),
        ("RRIO", "rail-to-rail вх/вих", "так", "feat", "розмах від рейки до рейки"),
    ]
    y0 = 56
    for i, (sym, name, val, kind, why) in enumerate(rows):
        y = y0 + i * 41
        fill = LGRN if kind == "rec" else ("#fdf1dc" if kind == "feat" else "#eef2f7")
        col = GREEN if kind == "rec" else (SUN if kind == "feat" else BLUE)
        s += rect(46, y, 120, 35, fill, col, 1.4, 6) + text(106, y + 16, sym, 11.5, col, "middle", "bold")
        s += text(106, y + 30, name, 7.2, INK, "middle")
        s += text(180, y + 22, val, 10.5, INK, "start", "bold")
        s += text(360, y + 22, why, 9.2, GREY, "start")
    s += text(W / 2, H - 24, "Спершу живлення (влізе?), тоді — критичний для ЦІЄЇ схеми параметр: для вимірювача Vos та Ib, для звуку SR і GBW.",
              8.8, INK, "middle")
    s += text(W / 2, H - 8, "Бери гарантовані min/max (§2.9.3), а не «typ» з вітрини.", 8.8, GREY, "middle", style="italic")
    save("fig-r09-7-3-opamp.svg", s)


def fig197_workflow():
    """Єдиний маршрут читання будь-якого даташита."""
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 28, "Єдиний маршрут: від вимог схеми до рішення", 15, INK, "middle", "bold")
    steps = [
        ("1", "Перша сторінка", "це взагалі той клас?", "#fdf1dc"),
        ("2", "Abs Max", "мої напруги/струми не вб'ють? (§2.9.2)", LRED),
        ("3", "Recommended", "робоча точка всередині? (§2.9.2)", "#fff3e0"),
        ("4", "Electrical Char.", "критичний параметр по гаранту (§2.9.3)", LGRN),
        ("5", "Графіки", "як попливе в МОЇХ умовах (§2.9.4)", LBLUE),
        ("6", "Дрібний шрифт", "виноски, errata (§2.9.6)", "#f3e9f3"),
    ]
    y, bh = 58, 34
    for i, (n, t1, t2, col) in enumerate(steps):
        yy = y + i * (bh + 4)
        s += rect(50, yy, 36, bh, "#ffffff", "#9bb0c2", 1.4, 6) + text(68, yy + 23, n, 14, INK, "middle", "bold")
        s += rect(92, yy, 220, bh, col, "#9bb0c2", 1.3, 6) + text(106, yy + 22, t1, 11, INK, "start", "bold")
        s += rect(318, yy, 360, bh, "#ffffff", "#c9d3dc", 1.2, 6) + text(332, yy + 22, t2, 10, INK, "start")
        if i < 5:
            s += line(68, yy + bh, 68, yy + bh + 4, GREY, 1.4)
    s += text(W / 2, H - 12, "Той самий шлях для діода, MOSFET чи ОП — змінюється лише, який параметр на кроці 4 критичний.",
              9, GREY, "middle", style="italic")
    save("fig-r09-7-4-workflow.svg", s)


if __name__ == "__main__":
    fig191_passport()
    fig191_map()
    fig191_firstpage()
    fig191_jump()
    fig191_tones()
    fig191_find()
    # §2.9.2 Absolute Maximum vs Recommended
    fig192_two_tables()
    fig192_cliff()
    fig192_why_gap()
    fig192_transient()
    fig192_params()
    fig192_rule()
    # §2.9.3 Min/typ/max і умови
    fig193_table()
    fig193_distribution()
    fig193_design()
    fig193_conditions()
    fig193_which_column()
    fig193_recipe()
    # §2.9.4 Графіки
    fig194_why_graphs()
    fig194_derating()
    fig194_iv_curve()
    fig194_log_axis()
    fig194_read_point()
    fig194_curve_zoo()
    # §2.9.5 Корпуси, маркування, розпіновка
    fig195_tht_smd()
    fig195_package_zoo()
    fig195_pin1()
    fig195_pinout()
    fig195_marking()
    fig195_ordering()
    # §2.9.6 Дрібний шрифт
    fig196_footnotes()
    fig196_test_conditions()
    fig196_typ_only()
    fig196_revision()
    fig196_errata()
    # §2.9.7 Практикум
    fig197_diode()
    fig197_mosfet()
    fig197_opamp()
    fig197_workflow()
    print("OK — Розділ 2.9 (§2.9.1–§2.9.7) згенеровано в", OUT)
