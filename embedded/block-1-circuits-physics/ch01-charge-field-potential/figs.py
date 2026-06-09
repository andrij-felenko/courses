# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 1 — «Заряд, електричне поле й потенціал» (Модуль 1).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 1.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+)
BLUE  = "#1f47b5"   # від'ємний (−)
GREEN = "#1f8a3b"   # поле
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
AMBER = "#caa24a"   # бурштин
GLASS = "#a9c8dd"   # скло
SILK  = "#d8b24a"   # шовк
HEMP  = "#b08a5a"   # конопляна нитка
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


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.0.1 — вертикальний таймлайн «ланцюг питань» ───────────────────────
def fig_timeline():
    W, H = 840, 880
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: від бурштину до поля", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "кожен крок — нове питання, що штовхало науку далі (сірим — теми з власною історією)",
              12.5, GREY, "middle", style="italic")
    spine = 168
    top, bot = 100, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("~600 до н.е.", "Фалес / Thales", "Чому потертий бурштин (ἤλεκτρον) притягує соломинку?", False),
        ("1600", "Гілберт / Gilbert", "Це те саме, що магніт? — Ні: «electrica» — окремий клас тіл", False),
        ("1663", "фон Геріке / von Guericke", "Чи можна цю силу робити машиною? — сірчана куля, перші іскри", False),
        ("1729", "Грей / Gray", "Сила сидить у тілі чи може текти? — провідник проти ізолятора", False),
        ("1733", "дю Фе / du Fay", "Чому одне притягує, інше відштовхує? — ДВА роди електрики", False),
        ("1745", "Лейденська банка", "Чи можна накопичити її в банку? — заряд і удар (→ Розділ 7)", True),
        ("1752", "Франклін / Franklin", "Один флюїд: + і −; заряд зберігається; блискавка — теж він", False),
        ("1785", "Кулон / Coulomb", "Скільки саме? — закон сили в числах (→ історія §1.2)", True),
        ("1800", "Вольта / Volta", "Звідки СТАЛИЙ потік, а не іскра? — батарея, «вольт» (→ §1.5)", True),
        ("1831", "Фарадей / Faraday", "Що тягнеться крізь порожнечу між тілами? — ПОЛЕ (→ §1.3)", True),
    ]
    n = len(nodes)
    for i, (yr, who, q, faint) in enumerate(nodes):
        y = top + 26 + (bot - top - 48) * i / (n - 1)
        col = GREY if faint else INK
        if i == 6:  # Франклін — акцент
            s += circle(spine, y, 10, RED, RED, 3)
            s += circle(spine, y, 10, "none", "#fff", 0)
            s += circle(spine, y, 9.5, "none", RED, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 20, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 24, y - 3, who, 15.5, (RED if i == 6 else col), "start", "bold")
        s += text(spine + 24, y + 16, q, 12.5, col, "start", style="italic")
    save("fig-1-0-1-timeline.svg", s)


# ── Рис. 1.0.2 — два роди електрики (дю Фе) ──────────────────────────────────
def fig_dufay():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 36, "Два роди електрики (дю Фе, 1733)", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "скляна (+, vitreous) і смоляна (−, resinous): однакові — відштовхуються, різні — притягуються",
              12.5, GREY, "middle", style="italic")

    def panel(cx, left, right, attract, caption, result):
        out = rect(cx - 118, 86, 236, 250, "none", FAINT, 2, 14)
        cy = 188
        gap = 52
        lx, rx = cx - gap, cx + gap
        for px, sign in ((lx, left), (rx, right)):
            col = RED if sign == "+" else BLUE
            out += circle(px, cy, 22, "#fff", col, 2.6)
            out += (plus(px, cy, 11, col) if sign == "+" else minus(px, cy, 11, col))
        ay = cy + 52
        if attract:
            out += arrow(lx - 18, ay, lx + 14, ay, INK, 2.4)
            out += arrow(rx + 18, ay, rx - 14, ay, INK, 2.4)
        else:
            out += arrow(lx + 18, ay, lx - 16, ay, INK, 2.4)
            out += arrow(rx - 18, ay, rx + 16, ay, INK, 2.4)
        out += text(cx, ay + 34, result, 14.5, (GREEN if attract else INK), "middle", "bold")
        out += text(cx, 118, caption, 13, INK, "middle", "bold")
        return out

    s += panel(166, "+", "+", False, "скло — скло", "відштовхування")
    s += panel(410, "−", "−", False, "смола — смола", "відштовхування")
    s += panel(654, "+", "−", True, "скло — смола", "притягування")
    s += text(W / 2, 412,
              "Через ~15 років Франклін перейменує ці «роди» на + та − одного флюїду.",
              13, GREY, "middle", style="italic")
    save("fig-1-0-2-dufay.svg", s)


# ── Рис. 1.0.3 — конвенція знаку Франкліна vs реальність ─────────────────────
def fig_franklin():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 36, "Здогад Франкліна й напрямок струму", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "Франклін навмання назвав «скляний» стан додатним — і не вгадав, що рухається в металі",
              12.5, GREY, "middle", style="italic")

    # клеми
    bx, wy = 120, 200
    s += rect(70, wy - 44, 50, 88, "#fbecec", RED, 2.5, 8)
    s += plus(95, wy, 13, RED)
    s += rect(W - 120, wy - 44, 50, 88, "#e9eefb", BLUE, 2.5, 8)
    s += minus(W - 95, wy, 13, BLUE)
    s += text(95, wy - 54, "клема +", 13, RED, "middle", "bold")
    s += text(W - 95, wy - 54, "клема −", 13, BLUE, "middle", "bold")

    # провід
    x0, x1 = 132, W - 132
    s += line(x0, wy - 16, x1, wy - 16, INK, 3)
    s += line(x0, wy + 16, x1, wy + 16, INK, 3)
    s += rect(x0, wy - 16, x1 - x0, 32, "#fafafa", "none", 0)

    # умовний струм (червоний, + → −, зверху)
    s += arrow(x0 + 60, wy - 40, x1 - 60, wy - 40, RED, 3)
    s += text(W / 2, wy - 50, "умовний струм  I :  + → −   (конвенція Франкліна)", 14.5, RED, "middle", "bold")

    # електрони (сині дроблення, − → +, всередині)
    for i in range(6):
        ex = x0 + 70 + i * (x1 - x0 - 140) / 5
        s += minus(ex, wy, 8, BLUE, 2)
    s += arrow(x1 - 60, wy + 40, x0 + 60, wy + 40, BLUE, 3)
    s += text(W / 2, wy + 58, "насправді течуть електрони  e⁻ :  − → +", 14.5, BLUE, "middle", "bold")

    s += rect(70, 330, W - 140, 66, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 356, "🔧 Тому в кожному даташиті «струм» іде від + до −,",
              13.5, INK, "middle", "bold")
    s += text(W / 2, 378, "хоч носії заряду в дроті рухаються навпаки. Цей знак ми тягнемо з 1752 року.",
              13.5, INK, "middle")
    save("fig-1-0-3-franklin.svg", s)


# ── Рис. 1.0.4 — Грей: заряд тече вздовж лінії (провідник vs ізолятор) ────────
def fig_gray():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 36, "Грей, 1729: електрика може текти на відстань", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "конопляна нитка проводить заряд; та лише шовкові (ізоляційні) підвіси не дають йому стекти в землю",
              12.5, GREY, "middle", style="italic")

    # балка зверху
    beam_y = 96
    s += rect(70, beam_y - 12, W - 140, 16, "#efe7d6", "#b9a77e", 2, 4)
    s += text(W / 2, beam_y - 18, "дерев'яна балка (опора)", 12.5, GREY, "middle", style="italic")

    thread_y = 250
    # шовкові петлі-ізолятори
    for sx in (250, 560):
        s += line(sx, beam_y + 4, sx, thread_y, SILK, 3)
        s += circle(sx, thread_y, 9, "none", SILK, 3)
    s += text(250, beam_y + 26, "шовк — ІЗОЛЯТОР", 12.5, SILK, "middle", "bold")
    s += text(560, beam_y + 26, "шовк — ІЗОЛЯТОР", 12.5, SILK, "middle", "bold")

    # натерта скляна трубка — джерело заряду (зліва)
    s += rect(96, thread_y - 16, 70, 32, GLASS, "#5b87a6", 2.5, 14)
    s += plus(120, thread_y, 9, RED, 2)
    s += plus(142, thread_y, 9, RED, 2)
    s += text(131, thread_y - 26, "натерта скляна трубка", 12.5, INK, "middle", "bold")
    s += text(131, thread_y + 36, "(джерело заряду)", 12, GREY, "middle", style="italic")

    # конопляна нитка — провідник
    s += line(166, thread_y, 690, thread_y, HEMP, 4)
    s += text(408, thread_y - 12, "конопляна нитка — ПРОВІДНИК", 13.5, HEMP, "middle", "bold")
    # заряд біжить уздовж
    s += arrow(300, thread_y - 30, 470, thread_y - 30, RED, 2.6)
    s += text(385, thread_y - 38, "заряд біжить", 12, RED, "middle", style="italic")

    # на дальньому кінці — притягання клаптиків
    s += line(690, thread_y, 690, thread_y + 40, HEMP, 4)
    s += circle(690, thread_y + 52, 10, "#fff", INK, 2)
    s += plus(690, thread_y + 52, 5, RED, 1.8)
    for i, fy in enumerate((thread_y + 78, thread_y + 90, thread_y + 84)):
        fx = 690 + (i - 1) * 16
        s += rect(fx - 5, fy, 10, 6, "#f0e9c8", "#b8a76a", 1.2, 1)
    s += arrow(690, thread_y + 74, 690, thread_y + 64, INK, 2)
    s += text(720, thread_y + 56, "за метри від джерела", 12.5, INK, "start", "bold")
    s += text(720, thread_y + 74, "нитка притягує клаптики —", 12, INK, "start")
    s += text(720, thread_y + 90, "електрика дісталася кінця", 12, INK, "start")

    # земля
    gy = H - 26
    s += line(70, gy, W - 70, gy, GREY, 2)
    for gx in range(80, W - 70, 22):
        s += line(gx, gy, gx - 8, gy + 10, GREY, 1.4)
    s += text(W / 2, H - 6, "земля (якби підвіс був звичайним мотузком — заряд стік би сюди й зник)",
              11.5, GREY, "middle", style="italic")
    save("fig-1-0-4-gray.svg", s)


def _cluster(cx, cy, pluses, minuses, cols=4, dx=26, dy=26, r=8):
    """Сітка з pluses (+) і minuses (−) символів навколо (cx,cy)."""
    out = ""
    items = ["+"] * pluses + ["-"] * minuses
    n = len(items)
    rows = (n + cols - 1) // cols
    for i, sym in enumerate(items):
        rr, cc = i // cols, i % cols
        row_n = cols if (rr < rows - 1) else (n - cols * (rows - 1))
        px = cx - (row_n - 1) * dx / 2 + cc * dx
        py = cy - (rows - 1) * dy / 2 + rr * dy
        out += plus(px, py, r, RED, 2) if sym == "+" else minus(px, py, r, BLUE, 2)
    return out


# ── Рис. 1.1.1 — атом і нейтральність ────────────────────────────────────────
def fig11_atom():
    W, H = 790, 470
    s = header(W, H)
    s += text(W / 2, 36, "Атом: чому звичайна речовина нейтральна", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "стільки ж протонів (+), скільки електронів (−) → сумарний заряд нуль",
              12.5, GREY, "middle", style="italic")
    cx, cy = 250, 258
    s += circle(cx, cy, 138, "none", FAINT, 1.6)
    s += circle(cx, cy, 96, "none", FAINT, 1.6)
    nuc = [(-13, -7, "p"), (13, -7, "p"), (0, 13, "p"), (-13, 11, "n"), (13, 11, "n"), (0, -17, "n")]
    for dx, dy, t in nuc:
        if t == "p":
            s += circle(cx + dx, cy + dy, 12, "#fbecec", RED, 2)
            s += text(cx + dx, cy + dy + 5, "+", 15, RED, "middle", "bold")
        else:
            s += circle(cx + dx, cy + dy, 12, "#ededed", GREY, 2)
            s += text(cx + dx, cy + dy + 4, "n", 11, GREY, "middle", "bold")
    for r, a in ((138, 200), (138, 340), (96, 70)):
        ex = cx + r * math.cos(math.radians(a))
        ey = cy + r * math.sin(math.radians(a))
        s += minus(ex, ey, 11, BLUE)
    s += text(cx, cy + 168, "ядро: протони (+) і нейтрони (n)", 12.5, INK, "middle", "bold")
    s += text(cx, cy + 186, "майже вся маса тут; заряд міцно зв'язаний", 11.5, GREY, "middle", style="italic")
    s += text(cx + 150, cy - 120, "електрони (−)", 12.5, BLUE, "middle", "bold")
    s += text(cx + 150, cy - 104, "легкі, рухливі", 11.5, GREY, "middle", style="italic")
    lx = 470
    s += text(lx, 160, "Підрахунок заряду", 16, INK, "start", "bold")
    s += text(lx, 190, "3 протони", 14, RED, "start")
    s += text(lx + 250, 190, "+3e", 14, RED, "end")
    s += text(lx, 214, "3 нейтрони", 14, GREY, "start")
    s += text(lx + 250, 214, "0", 14, GREY, "end")
    s += text(lx, 238, "3 електрони", 14, BLUE, "start")
    s += text(lx + 250, 238, "−3e", 14, BLUE, "end")
    s += line(lx, 252, lx + 250, 252, INK, 1.5)
    s += text(lx, 278, "сума", 14.5, GREEN, "start", "bold")
    s += text(lx + 250, 278, "0", 14.5, GREEN, "end", "bold")
    s += rect(lx, 306, 252, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(lx + 12, 332, "Заряд протона й електрона", 12.5, INK, "start")
    s += text(lx + 12, 352, "рівні за величиною й протилежні:", 12.5, INK, "start")
    s += text(lx + 12, 374, "+e та −e,  e = елементарний заряд.", 12.5, INK, "start", "bold")
    s += text(lx + 12, 392, "Зайвий / відсутній e → тіло заряджене.", 11.5, GREY, "start", style="italic")
    save("fig-1-1-1-atom.svg", s)


# ── Рис. 1.1.2 — зарядка = перехід електронів ────────────────────────────────
def fig11_transfer():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "Як тіло заряджається: переходять ЕЛЕКТРОНИ", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "натирання не створює заряд — воно лише переганяє електрони з тіла на тіло",
              12.5, GREY, "middle", style="italic")
    # БЕФОР
    s += text(70, 96, "ДО тертя", 14, INK, "start", "bold")
    s += rect(150, 104, 150, 96, "#fafafa", INK, 2, 12)
    s += rect(470, 104, 150, 96, "#fafafa", INK, 2, 12)
    s += _cluster(225, 152, 4, 4)
    s += _cluster(545, 152, 4, 4)
    s += text(225, 220, "тіло A — нейтральне", 12.5, INK, "middle")
    s += text(545, 220, "тіло B — нейтральне", 12.5, INK, "middle")
    s += text(385, 145, "тертя", 13, INK, "middle", "bold")
    s += line(335, 152, 360, 152, INK, 2)
    s += line(410, 152, 435, 152, INK, 2)
    s += text(385, 162, "⇄", 16, INK, "middle")
    # АФТЕР
    s += text(70, 286, "ПІСЛЯ", 14, INK, "start", "bold")
    s += rect(150, 294, 150, 96, "#fdf4f4", RED, 2.4, 12)
    s += rect(470, 294, 150, 96, "#f3f5fd", BLUE, 2.4, 12)
    s += _cluster(225, 342, 4, 2)
    s += _cluster(545, 342, 4, 6)
    s += arrow(360, 318, 432, 318, BLUE, 2.6)
    s += text(396, 308, "2 e⁻", 12.5, BLUE, "middle", "bold")
    s += text(225, 410, "A втратило 2 e⁻  →  заряд +2e", 12.5, RED, "middle", "bold")
    s += text(545, 410, "B набуло 2 e⁻  →  заряд −2e", 12.5, BLUE, "middle", "bold")
    s += text(W / 2, 446, "Оце і є «два роди» дю Фе: надлишок (−) і нестача (+) електронів. Сумарно заряд не змінився.",
              12.5, GREY, "middle", style="italic")
    save("fig-1-1-2-transfer.svg", s)


# ── Рис. 1.1.3 — квантування заряду ──────────────────────────────────────────
def fig11_quantization():
    W, H = 810, 400
    s = header(W, H)
    s += text(W / 2, 36, "Заряд квантований: лише цілі порції e", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "будь-який вільний заряд = N · e, де N — ціле; проміжних значень не буває",
              12.5, GREY, "middle", style="italic")
    axisY = 196
    x0, x1 = 80, W - 80
    s += line(x0, axisY, x1, axisY, INK, 2.4)
    unit = (x1 - x0) / 7.0
    mid = (x0 + x1) / 2
    for N in range(-3, 4):
        tx = mid + N * unit
        s += line(tx, axisY - 7, tx, axisY + 7, INK, 2)
        col = RED if N > 0 else (BLUE if N < 0 else INK)
        s += circle(tx, axisY - 30, 7, col, col, 1.5)
        lbl = "0" if N == 0 else f"{N:+d}e"
        s += text(tx, axisY + 28, lbl, 13.5, col, "middle", "bold")
    # заборонене проміжне
    fx = mid + 1.5 * unit
    s += circle(fx, axisY - 30, 7, "none", GREY, 1.6)
    s += line(fx - 5, axisY - 35, fx + 5, axisY - 25, RED, 2)
    s += line(fx - 5, axisY - 25, fx + 5, axisY - 35, RED, 2)
    s += text(fx, axisY - 46, "+1.5e — не існує", 11.5, RED, "middle", "bold")
    # значення e
    s += rect(80, 250, 360, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(96, 278, "Елементарний заряд:", 13.5, INK, "start", "bold")
    s += text(96, 304, "e = 1.602 × 10⁻¹⁹ Кл", 15, INK, "start", "bold")
    s += text(96, 330, "заряд електрона = −e, протона = +e", 12.5, GREY, "start")
    # кварки
    s += rect(460, 250, W - 540, 96, "#fafafa", GREY, 1.6, 10)
    s += text(476, 278, "А кварки? Мають ⅓ та ⅔ e,", 12.5, INK, "start", "bold")
    s += text(476, 302, "але «замкнені» в частинках —", 12.5, INK, "start")
    s += text(476, 326, "вільно їх не виділити. Тож для нас", 12.5, INK, "start")
    s += text(476, 348, "крок заряду завжди e.", 12.5, INK, "start", "bold")
    save("fig-1-1-3-quantization.svg", s)


# ── Рис. 1.1.4 — збереження заряду ───────────────────────────────────────────
def fig11_conservation():
    W, H = 800, 360
    s = header(W, H)
    s += text(W / 2, 36, "Збереження заряду: бухгалтерія завжди сходиться", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "у замкненій системі сумарний заряд не змінюється — хай що відбувається всередині",
              12.5, GREY, "middle", style="italic")

    def sysbox(x, label):
        out = rect(x, 110, 250, 150, "none", INK, 2, 12)
        out += f'<rect x="{x}" y="110" width="250" height="150" rx="12" fill="none" stroke="{GREY}" stroke-width="2" stroke-dasharray="7 5"/>\n'
        out += text(x + 125, 100, label, 13.5, INK, "middle", "bold")
        return out

    s += sysbox(70, "ДО процесу")
    s += sysbox(480, "ПІСЛЯ процесу")
    s += _cluster(150, 170, 5, 3, cols=4, dx=28, dy=30, r=9)
    s += _cluster(640, 185, 5, 3, cols=5, dx=30, dy=34, r=9)
    s += text(195, 250, "Σq = +2e", 15, GREEN, "middle", "bold")
    s += text(605, 250, "Σq = +2e", 15, GREEN, "middle", "bold")
    s += arrow(335, 185, 470, 185, INK, 2.6)
    s += text(402, 172, "тертя, розряд,", 12, INK, "middle")
    s += text(402, 206, "хім. реакція…", 12, INK, "middle")
    s += text(W / 2, 312, "Заряди лише перерозподілилися. Скільки + з'явилося — стільки ж − залишилося деінде:",
              12.5, GREY, "middle", style="italic")
    s += text(W / 2, 332, "заряд неможливо створити з нічого чи знищити. Це знадобиться в законі Кірхгофа (§4.2).",
              12.5, GREY, "middle", style="italic")
    save("fig-1-1-4-conservation.svg", s)


# ── Рис. 1.1.5 — масштаб кулона й майже-баланс речовини ───────────────────────
def fig11_scale():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 36, "Скільки це — кулон? І чому речовина «майже» нейтральна", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "звичайна матерія тримає гігантські + і −, що гасяться майже точно",
              12.5, GREY, "middle", style="italic")
    # твін-бари
    bx, base, bw = 150, 330, 70
    s += rect(bx, base - 210, bw, 210, "#fbecec", RED, 2, 4)
    s += rect(bx + 110, base - 208, bw, 208, "#e9eefb", BLUE, 2, 4)
    s += text(bx + bw / 2, base + 22, "+Q", 15, RED, "middle", "bold")
    s += text(bx + 110 + bw / 2, base + 22, "−Q", 15, BLUE, "middle", "bold")
    s += text(bx + 95, base - 230, "≈ 10⁷ Кл кожного", 12.5, INK, "middle", "bold")
    s += line(bx - 14, base, bx + 200, base, INK, 1.6)
    s += text(bx + 95, base + 46, "склянка води", 12.5, INK, "middle", "bold")
    s += text(bx + 95, base + 64, "гасяться до ≈ 0", 12, GREY, "middle", style="italic")
    s += text(bx + 95, base + 92, "Те, що ми звемо «зарядом», —", 12, GREEN, "middle")
    s += text(bx + 95, base + 110, "крихітний дисбаланс цих гігантів.", 12, GREEN, "middle", "bold")
    # шкала величин
    lx = 470
    s += text(lx, 110, "Порядки величини заряду", 16, INK, "start", "bold")
    rows = [
        ("1 електрон", "1.6 × 10⁻¹⁹ Кл", BLUE),
        ("статична іскра (відчув)", "~ 10⁻⁶ Кл  (мкКл)", INK),
        ("1 кулон", "= 6.24 × 10¹⁸ електронів", RED),
        ("розряд блискавки", "~ 15 Кл", INK),
    ]
    yy = 150
    for name, val, col in rows:
        s += circle(lx + 6, yy - 5, 4, col, col, 1)
        s += text(lx + 22, yy, name, 13.5, INK, "start", "bold")
        s += text(lx + 22, yy + 20, val, 13, col, "start")
        yy += 56
    s += text(lx, yy + 6, "1 Кл — велетенська порція: майже ніколи", 12, GREY, "start", style="italic")
    s += text(lx, yy + 24, "не зустрінеться як «вільний» статичний заряд.", 12, GREY, "start", style="italic")
    save("fig-1-1-5-scale.svg", s)


# ── Рис. 1.1.6 — провідник vs ізолятор при зарядці ───────────────────────────
def fig11_cond_insul():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 36, "Куди дівається заряд: провідник vs ізолятор", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "у провіднику носії вільні й розповзаються; в ізоляторі — лишаються на місці",
              12.5, GREY, "middle", style="italic")
    # провідник
    cx, cy = 220, 220
    s += circle(cx, cy, 84, "#f5f7f9", "#7a93a8", 2.4)
    for a in range(0, 360, 45):
        ex = cx + 84 * math.cos(math.radians(a))
        ey = cy + 84 * math.sin(math.radians(a))
        s += minus(ex, ey, 9, BLUE, 2)
    s += text(cx, cy + 4, "метал", 13, "#7a93a8", "middle", "bold")
    s += text(cx, cy + 118, "ПРОВІДНИК", 14.5, INK, "middle", "bold")
    s += text(cx, cy + 138, "заряд рівномірно по поверхні", 12, GREY, "middle", style="italic")
    # ізолятор
    rx, ry = 560, 220
    s += rect(rx - 110, ry - 26, 220, 52, "#f7f4f0", "#b9986a", 2.4, 14)
    s += _cluster(rx - 70, ry, 0, 6, cols=3, dx=20, dy=20, r=8)
    s += text(rx + 36, ry + 5, "пластик", 13, "#b9986a", "middle", "bold")
    s += text(rx, ry + 78, "ІЗОЛЯТОР", 14.5, INK, "middle", "bold")
    s += text(rx, ry + 98, "заряд застряг там, де з'явився", 12, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "Тому метал треба тримати за ізольовану ручку, а наелектризований пластик «плямистий».",
              12, GREY, "middle", style="italic")
    save("fig-1-1-6-conductor-insulator.svg", s)


# ── Рис. 1.1.7 — трибоелектричний ряд ────────────────────────────────────────
def fig11_tribo():
    W, H = 770, 520
    s = header(W, H)
    s += text(W / 2, 36, "Трибоелектричний ряд: хто стане + , а хто −", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "потерті, верхній у списку віддає електрони (стає +), нижній — забирає (стає −)",
              12.5, GREY, "middle", style="italic")
    bar_x, bar_w = 150, 70
    top, bot = 92, 470
    seg = (bot - top) / 12
    materials = [
        ("хутро, шкіра", RED), ("скло", RED), ("нейлон", RED), ("вовна", "#c66"),
        ("шовк", "#c88"), ("папір", GREY), ("бавовна (≈ нейтр.)", GREY),
        ("сталь (≈ нейтр.)", GREY), ("гума", "#88c"), ("бурштин, смола", BLUE),
        ("ПВХ", BLUE), ("тефлон (ПТФЕ)", BLUE),
    ]
    # кольорова стрічка сегментами
    for i in range(12):
        y = top + i * seg
        t = i / 11.0
        if t < 0.5:
            r = int(192 + (138 - 192) * (t / 0.5)); g = int(39 + (138 - 39) * (t / 0.5)); b = int(30 + (138 - 30) * (t / 0.5))
        else:
            tt = (t - 0.5) / 0.5
            r = int(138 + (31 - 138) * tt); g = int(138 + (71 - 138) * tt); b = int(138 + (181 - 138) * tt)
        s += rect(bar_x, y, bar_w, seg + 0.6, f"rgb({r},{g},{b})", "none", 0)
    s += rect(bar_x, top, bar_w, bot - top, "none", INK, 1.8, 0)
    s += plus(bar_x + bar_w / 2, top - 4, 11, RED)
    s += minus(bar_x + bar_w / 2, bot + 6, 11, BLUE)
    s += text(bar_x - 10, top + 6, "віддає e⁻", 12, RED, "end", "bold")
    s += text(bar_x - 10, bot - 2, "забирає e⁻", 12, BLUE, "end", "bold")
    for i, (name, col) in enumerate(materials):
        y = top + (i + 0.5) * seg + 4
        s += line(bar_x + bar_w, y - 4, bar_x + bar_w + 16, y - 4, GREY, 1.2)
        s += text(bar_x + bar_w + 22, y, name, 13.5, col, "start", "bold" if col in (RED, BLUE) else "normal")
    s += rect(470, 150, 250, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(482, 178, "Перевірка історією:", 13, INK, "start", "bold")
    s += text(482, 204, "скло — вгорі → стає +", 13, RED, "start")
    s += text(482, 228, "бурштин — внизу → стає −", 13, BLUE, "start")
    s += text(482, 256, "саме «скляна» й «смоляна»", 12.5, GREY, "start", style="italic")
    s += text(482, 274, "електрики дю Фе (Рис. 1.0.2).", 12.5, GREY, "start", style="italic")
    save("fig-1-1-7-triboelectric.svg", s)


# ── Рис. 1.1.8 — заземлення ──────────────────────────────────────────────────
def fig11_ground():
    W, H = 780, 380
    s = header(W, H)
    s += text(W / 2, 36, "Заземлення: зрівняти тіло з нескінченним резервуаром", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "зайві електрони стікають у землю — і тіло стає нейтральним",
              12.5, GREY, "middle", style="italic")
    # тіло з надлишком електронів
    s += rect(120, 110, 150, 90, "#f3f5fd", BLUE, 2.4, 12)
    s += _cluster(195, 155, 0, 5, cols=5, dx=24, dy=24, r=8)
    s += text(195, 100, "заряджене тіло (−)", 12.5, INK, "middle", "bold")
    # провід до землі
    s += line(195, 200, 195, 270, INK, 2.4)
    # символ землі
    gy = 270
    s += line(160, gy, 230, gy, INK, 3)
    s += line(172, gy + 12, 218, gy + 12, INK, 3)
    s += line(183, gy + 24, 207, gy + 24, INK, 3)
    s += arrow(210, 215, 210, 262, BLUE, 2.4)
    s += text(248, 240, "e⁻ стікають", 12.5, BLUE, "start", "bold")
    s += text(195, gy + 46, "ЗЕМЛЯ", 12.5, INK, "middle", "bold")
    # після
    s += arrow(330, 175, 410, 175, INK, 2.6)
    s += text(370, 165, "після", 12, INK, "middle")
    s += rect(440, 110, 150, 90, "#fafafa", INK, 2.4, 12)
    s += _cluster(515, 155, 3, 3, cols=3, dx=26, dy=28, r=8)
    s += text(515, 100, "нейтральне", 12.5, GREEN, "middle", "bold")
    s += rect(440, 240, 300, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(456, 268, "Земля — практично нескінченний", 12.5, INK, "start")
    s += text(456, 290, "резервуар заряду. «Заземлити» =", 12.5, INK, "start")
    s += text(456, 312, "зрівняти потенціал тіла з нею", 12.5, INK, "start", "bold")
    s += text(456, 330, "(детально про GND — далі в курсі).", 11.5, GREY, "start", style="italic")
    save("fig-1-1-8-grounding.svg", s)


# ── Рис. 1.1.9 — поляризація: чому нейтральне притягується ────────────────────
def fig11_polarization():
    W, H = 810, 380
    s = header(W, H)
    s += text(W / 2, 36, "Чому потертий бурштин підіймає НЕЙТРАЛЬНУ соломинку", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "відповідь на найперше питання (Фалес): заряди в нейтральному тілі трохи зміщуються",
              12.5, GREY, "middle", style="italic")
    # заряджена паличка (+)
    rod_x = 150
    s += rect(rod_x - 26, 120, 52, 170, "#fdf4f4", RED, 2.4, 12)
    for yy in (150, 185, 220, 255):
        s += plus(rod_x, yy, 10, RED, 2)
    s += text(rod_x, 108, "заряджене (+)", 12.5, RED, "middle", "bold")
    # нейтральна соломинка з розділеними зарядами
    sx = 520
    s += rect(sx - 70, 165, 140, 80, "#fafafa", INK, 2.2, 12)
    s += _cluster(sx - 44, 205, 0, 3, cols=1, dx=10, dy=26, r=8)
    s += _cluster(sx + 44, 205, 3, 0, cols=1, dx=10, dy=26, r=8)
    s += text(sx, 150, "нейтральна соломинка (сумарно 0)", 12.5, INK, "middle", "bold")
    s += text(sx - 44, 262, "ближче: −", 12, BLUE, "middle", "bold")
    s += text(sx + 44, 262, "далі: +", 12, RED, "middle", "bold")
    # сили: сильне притягання ближньої сторони, слабше відштовхування дальньої
    s += arrow(sx - 78, 195, rod_x + 40, 195, BLUE, 3)
    s += text((sx - 78 + rod_x + 40) / 2, 186, "притягання (сильніше)", 12, BLUE, "middle", "bold")
    s += arrow(sx + 70, 228, sx + 150, 228, RED, 2)
    s += text(sx + 110, 248, "відштовх. (слабше)", 11.5, RED, "middle")
    s += rect(150, 318, W - 300, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 340, "Ближча сторона взаємодіє сильніше → сумарно тіло ПРИТЯГУЄТЬСЯ,",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 360, "хоч саме воно нейтральне. Так замкнувся ланцюг питань із Рис. 1.0.1.",
              12.5, GREY, "middle", style="italic")
    save("fig-1-1-9-polarization.svg", s)


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


# ── Рис. 1.2.1 — закон Кулона: напрямок і модуль ─────────────────────────────
def fig12_law():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Закон Кулона: сила між двома точковими зарядами", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "уздовж прямої, що їх з'єднує; рівні за модулем і протилежні (3-й закон Ньютона)",
              12.5, GREY, "middle", style="italic")

    def pair(cy, s2, attract, label):
        out = ""
        lx, rx = 220, 470
        # розмір r
        out += line(lx, cy + 44, rx, cy + 44, GREY, 1.4)
        out += line(lx, cy + 38, lx, cy + 50, GREY, 1.4)
        out += line(rx, cy + 38, rx, cy + 50, GREY, 1.4)
        out += text((lx + rx) / 2, cy + 62, "r", 14, GREY, "middle", "bold", "italic")
        # заряди
        out += circle(lx, cy, 20, "#fdf4f4", RED, 2.6)
        out += plus(lx, cy, 11, RED)
        c2 = RED if s2 == "+" else BLUE
        out += circle(rx, cy, 20, "#fdf4f4" if s2 == "+" else "#f3f5fd", c2, 2.6)
        out += (plus(rx, cy, 11, c2) if s2 == "+" else minus(rx, cy, 11, c2))
        out += text(lx, cy - 30, "q₁", 14, RED, "middle", "bold")
        out += text(rx, cy - 30, "q₂", 14, c2, "middle", "bold")
        # сили
        if attract:
            out += arrow(lx + 24, cy, lx + 78, cy, INK, 3)
            out += arrow(rx - 24, cy, rx - 78, cy, INK, 3)
        else:
            out += arrow(lx - 24, cy, lx - 78, cy, INK, 3)
            out += arrow(rx + 24, cy, rx + 78, cy, INK, 3)
        out += text(lx + (28 if attract else -52), cy - 12, "F", 14, INK, "middle", "bold", "italic")
        out += text(rx + (-28 if attract else 52), cy - 12, "F", 14, INK, "middle", "bold", "italic")
        out += text(560, cy - 6, label, 13.5, (GREEN if attract else INK), "start", "bold")
        out += text(560, cy + 14, "(різнойменні)" if attract else "(однойменні)", 12, GREY, "start", style="italic")
        return out

    s += pair(150, "+", False, "відштовхування")
    s += pair(270, "−", True, "притягання")
    # формула
    s += rect(150, 332, W - 300, 72, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 360, "F = k · |q₁ · q₂| / r²", 19, INK, "middle", "bold")
    s += text(W / 2, 388, "k = 1/(4·π·ε₀) ≈ 8.99 × 10⁹ Н·м²/Кл²    ·    ε₀ ≈ 8.854 × 10⁻¹² Кл²/(Н·м²)",
              12.5, GREY, "middle")
    save("fig-1-2-1-coulomb-law.svg", s)


# ── Рис. 1.2.2 — закон оберненого квадрата ───────────────────────────────────
def fig12_inverse_square():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому 1/r²: сила розбавляється геометрією", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "вплив розходиться навсібіч і розмазується по сфері площею 4·π·r²",
              12.5, GREY, "middle", style="italic")
    # ЛІВО: геометрія розбавлення
    px, py = 70, 250
    s += circle(px, py, 9, RED, RED, 1)
    s += plus(px, py, 5, "#fff", 1.2)
    for a in range(-40, 41, 16):
        ex = px + 250 * math.cos(math.radians(a))
        ey = py + 250 * math.sin(math.radians(a))
        s += line(px, py, ex, ey, FAINT, 1.3)
    for r, lab in ((110, "r"), (220, "2r")):
        s += f'<path d="M {px + r * math.cos(math.radians(-42)):.1f},{py + r * math.sin(math.radians(-42)):.1f} A {r},{r} 0 0 1 {px + r * math.cos(math.radians(42)):.1f},{py + r * math.sin(math.radians(42)):.1f}" fill="none" stroke="{INK}" stroke-width="2"/>\n'
        s += text(px + r * math.cos(0) + 6, py - r * 0.72, lab, 13, INK, "start", "bold", "italic")
    s += text(px + 60, py + 96, "та сама «кількість сили»,", 11.5, GREY, "start")
    s += text(px + 60, py + 112, "та вчетверо більша площа", 11.5, GREY, "start")
    s += text(px + 60, py + 128, "при 2r  →  вчетверо слабше", 11.5, INK, "start", "bold")
    # ПРАВО: крива F(r)
    gx0, gx1 = 470, 800
    gy_top, gy_bot = 110, 330
    s += arrow(gx0, gy_bot, gx1 + 6, gy_bot, INK, 2)   # вісь r
    s += arrow(gx0, gy_bot, gx0, gy_top - 6, INK, 2)   # вісь F
    s += text(gx1 + 4, gy_bot + 22, "r", 14, INK, "middle", "bold", "italic")
    s += text(gx0 - 16, gy_top, "F", 14, INK, "middle", "bold", "italic")
    # крива 1/r², r від 1 до 4
    rmin, rmax = 1.0, 4.0
    pts = []
    N = 80
    for i in range(N + 1):
        r = rmin + (rmax - rmin) * i / N
        f = 1.0 / (r * r)
        px2 = gx0 + (r - rmin) / (rmax - rmin) * (gx1 - gx0)
        py2 = gy_bot - f * (gy_bot - gy_top)
        pts.append((px2, py2))
    s += polyline(pts, RED, 2.8)
    for r, lab in ((1, "F₀"), (2, "F₀/4"), (3, "F₀/9")):
        f = 1.0 / (r * r)
        px2 = gx0 + (r - rmin) / (rmax - rmin) * (gx1 - gx0)
        py2 = gy_bot - f * (gy_bot - gy_top)
        s += line(px2, gy_bot, px2, py2, GREY, 1.2, "4 3")
        s += line(gx0, py2, px2, py2, GREY, 1.2, "4 3")
        s += circle(px2, py2, 4, RED, RED, 1)
        s += text(px2, gy_bot + 20, ("r₀" if r == 1 else f"{r}r₀"), 12.5, INK, "middle", "bold")
        s += text(gx0 + 6, py2 - 6, lab, 12.5, RED, "start", "bold")
    s += text((gx0 + gx1) / 2, gy_top - 14, "подвоїти r → сила падає в 4 рази", 12.5, INK, "middle", "bold")
    save("fig-1-2-2-inverse-square.svg", s)


# ── Рис. 1.2.3 — принцип суперпозиції ────────────────────────────────────────
def fig12_superposition():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 34, "Суперпозиція: сили просто додаються (векторно)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "сумарна сила на заряд — векторна сума сил від кожного іншого окремо",
              12.5, GREY, "middle", style="italic")
    q0 = (380, 330)
    q1 = (230, 130)
    q2 = (530, 130)
    # заряди-джерела
    for (qx, qy), lab in ((q1, "q₁ +"), (q2, "q₂ +")):
        s += circle(qx, qy, 19, "#fdf4f4", RED, 2.6)
        s += plus(qx, qy, 10, RED)
        s += text(qx, qy - 28, lab, 13.5, RED, "middle", "bold")
    # тест-заряд
    s += circle(q0[0], q0[1], 19, "#fdf4f4", RED, 2.6)
    s += plus(q0[0], q0[1], 10, RED)
    s += text(q0[0], q0[1] + 34, "q₀ +  (на нього діють сили)", 13, INK, "middle", "bold")

    def away(src, length, color, lab):
        dx, dy = q0[0] - src[0], q0[1] - src[1]
        L = math.hypot(dx, dy)
        ex, ey = q0[0] + dx / L * length, q0[1] + dy / L * length
        return arrow(q0[0], q0[1], ex, ey, color, 3), (ex, ey)

    a1, e1 = away(q1, 120, BLUE, "F₁")
    a2, e2 = away(q2, 120, BLUE, "F₂")
    s += a1 + a2
    s += text(e1[0] - 16, e1[1] + 6, "F₁", 14, BLUE, "middle", "bold", "italic")
    s += text(e2[0] + 16, e2[1] + 6, "F₂", 14, BLUE, "middle", "bold", "italic")
    # рівнодійна (сума векторів) — паралелограм
    rx = (e1[0] - q0[0]) + (e2[0] - q0[0])
    ry = (e1[1] - q0[1]) + (e2[1] - q0[1])
    s += line(e1[0], e1[1], q0[0] + rx, q0[1] + ry, GREY, 1.4, "5 4")
    s += line(e2[0], e2[1], q0[0] + rx, q0[1] + ry, GREY, 1.4, "5 4")
    s += arrow(q0[0], q0[1], q0[0] + rx, q0[1] + ry, GREEN, 3.4)
    s += text(q0[0] + rx + 16, q0[1] + ry + 4, "F = F₁ + F₂", 14, GREEN, "start", "bold")
    save("fig-1-2-3-superposition.svg", s)


# ── Рис. 1.2.4 — електрика проти гравітації ──────────────────────────────────
def fig12_gravity():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Електрична сила проти гравітації (два протони)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "обидві — закон 1/r², але електрична нечувано сильніша",
              12.5, GREY, "middle", style="italic")
    # два протони з силами
    lx, rx, cy = 180, 360, 140
    for px in (lx, rx):
        s += circle(px, cy, 18, "#fdf4f4", RED, 2.6)
        s += plus(px, cy, 10, RED)
    s += text(lx, cy - 28, "p⁺", 13.5, RED, "middle", "bold")
    s += text(rx, cy - 28, "p⁺", 13.5, RED, "middle", "bold")
    s += arrow(lx - 16, cy, lx - 70, cy, RED, 3.2)
    s += arrow(rx + 16, cy, rx + 70, cy, RED, 3.2)
    s += text(270, cy - 36, "F електр. (відштовх., велика)", 12, RED, "middle", "bold")
    s += arrow(lx + 20, cy + 30, lx + 44, cy + 30, BLUE, 1.6)
    s += arrow(rx - 20, cy + 30, rx - 44, cy + 30, BLUE, 1.6)
    s += text(270, cy + 52, "F гравіт. (притяг., мізерна)", 11.5, BLUE, "middle")
    # лог-шкала прірви
    ax0, ax1, ay = 90, W - 60, 300
    s += line(ax0, ay, ax1, ay, INK, 2)
    for d in range(0, 37, 9):
        tx = ax0 + d / 36.0 * (ax1 - ax0)
        s += line(tx, ay - 6, tx, ay + 6, INK, 1.6)
        s += text(tx, ay + 24, f"10{_sup(d)}", 12, GREY, "middle", "bold")
    s += circle(ax0, ay, 6, BLUE, BLUE, 1)
    s += text(ax0, ay - 16, "F_g", 12.5, BLUE, "middle", "bold")
    s += circle(ax1, ay, 6, RED, RED, 1)
    s += text(ax1, ay - 16, "F_e", 12.5, RED, "middle", "bold")
    s += text(W / 2, ay - 44, "F_e / F_g ≈ 1.2 × 10³⁶", 18, INK, "middle", "bold")
    s += text(W / 2, H - 16, "Гравітація бере гору лише на великих масштабах — бо велика речовина майже нейтральна.",
              12, GREY, "middle", style="italic")
    save("fig-1-2-4-electric-vs-gravity.svg", s)


def _sup(n):
    sup = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
           "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    return "".join(sup[c] for c in str(n))


# ── Рис. 1.2.5 — середовище послаблює силу ───────────────────────────────────
def fig12_medium():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Середовище послаблює силу: діелектрична проникність", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "у середовищі сила менша в εr разів: F = F₀ / εr",
              12.5, GREY, "middle", style="italic")

    def panel(x, title, eps, flen, fill, note):
        out = rect(x, 92, 300, 150, fill, GREY, 1.8, 12)
        out += text(x + 150, 84, title, 14, INK, "middle", "bold")
        lx, rx, cy = x + 70, x + 210, 150
        out += circle(lx, cy, 16, "#fdf4f4", RED, 2.4)
        out += plus(lx, cy, 9, RED)
        out += circle(rx, cy, 16, "#f3f5fd", BLUE, 2.4)
        out += minus(rx, cy, 9, BLUE)
        out += arrow(lx + 20, cy, lx + 20 + flen, cy, INK, 3)
        out += arrow(rx - 20, cy, rx - 20 - flen, cy, INK, 3)
        out += text(x + 150, cy + 44, note, 12.5, INK, "middle", "bold")
        out += text(x + 150, cy + 64, f"εr = {eps}", 13, GREEN, "middle", "bold")
        return out

    s += panel(60, "вакуум", "1", 46, "#fafafa", "повна сила F₀")
    s += panel(440, "вода", "≈ 80", 6, "#eef4f7", "сила ~ у 80 разів менша")
    s += text(W / 2, 300, "Відносна проникність εr (vacuum 1 · повітря ≈ 1.0006 · скло 4–8 · вода ≈ 80):",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 322, "що більше εr, то сильніше середовище «екранує» заряди одне від одного.",
              12.5, GREY, "middle", style="italic")
    s += text(W / 2, 352, "Саме тому в k стоїть ε₀ — проникність порожнечі: вона задає «силу» взаємодії у вакуумі.",
              12, GREY, "middle", style="italic")
    save("fig-1-2-5-medium-permittivity.svg", s)


def arc(cx, cy, r, a0, a1, color=INK, w=2, sweep=0):
    """Дуга кола (кути у градусах, екранні координати з y-up через −sin)."""
    x0 = cx + r * math.cos(math.radians(a0)); y0 = cy - r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1)); y1 = cy - r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    return f'<path d="M {x0:.1f},{y0:.1f} A {r},{r} 0 {large} {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>\n'


# ── Рис. 1.2і.1 — крутильні терези Кулона ────────────────────────────────────
def fig_coulomb_torsion():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Крутильні терези Кулона: нитка як ваги для сили", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "тонка нитка закручується на кут θ, точно пропорційний до сили відштовхування кульок",
              12.5, GREY, "middle", style="italic")
    cx, cy, R = 250, 262, 150
    s += circle(cx, cy, R, "none", FAINT, 2)
    for a in range(0, 360, 15):
        x1 = cx + (R - 8) * math.cos(math.radians(a)); y1 = cy - (R - 8) * math.sin(math.radians(a))
        x2 = cx + R * math.cos(math.radians(a)); y2 = cy - R * math.sin(math.radians(a))
        s += line(x1, y1, x2, y2, GREY, 1)
    s += circle(cx, cy, 5, INK, INK, 1)
    s += line(cx, cy, cx + R, cy, GREY, 1.4, "5 4")
    s += text(cx + R + 8, cy + 4, "спокій", 11.5, GREY, "start", style="italic")
    aA, aB = 38, 6
    Ax = cx + R * math.cos(math.radians(aA)); Ay = cy - R * math.sin(math.radians(aA))
    Bx = cx + R * math.cos(math.radians(aB)); By = cy - R * math.sin(math.radians(aB))
    cwx = cx + R * math.cos(math.radians(aA + 180)); cwy = cy - R * math.sin(math.radians(aA + 180))
    s += line(cwx, cwy, Ax, Ay, INK, 2.5)
    s += circle(cwx, cwy, 9, "#eee", GREY, 2)
    s += text(cwx - 2, cwy + 20, "противага", 11, GREY, "middle")
    s += circle(Ax, Ay, 13, "#fdf4f4", RED, 2.4); s += plus(Ax, Ay, 7, RED, 2)
    s += text(Ax + 12, Ay - 12, "A", 14, RED, "start", "bold")
    s += circle(Bx, By, 13, "#fdf4f4", RED, 2.4); s += plus(Bx, By, 7, RED, 2)
    s += text(Bx + 16, By + 8, "B (нерухома)", 11.5, RED, "start", "bold")
    s += arrow(Bx - 2, By - 8, Ax + 2, Ay + 10, INK, 2.4)
    s += text((Ax + Bx) / 2 - 40, (Ay + By) / 2 + 4, "відштовх.", 11, INK, "start", "bold")
    s += arc(cx, cy, 46, aB, aA, GREEN, 2.2)
    tlx = cx + 62 * math.cos(math.radians((aA + aB) / 2)); tly = cy - 62 * math.sin(math.radians((aA + aB) / 2))
    s += text(tlx + 4, tly + 4, "θ", 16, GREEN, "start", "bold", "italic")
    s += text(cx, cy + R + 32, "вид згори: θ між «спокоєм» і відхиленою голкою", 12, INK, "middle", "bold")
    # бічний вид
    ix = 600
    s += rect(ix, 96, 150, 300, "#fbfbfb", "#bbbbbb", 1.6, 8)
    s += rect(ix + 55, 100, 40, 16, "#eeeeee", INK, 1.6, 3)
    s += text(ix + 75, 90, "головка (крутить нитку)", 10.5, INK, "middle", "bold")
    s += line(ix + 75, 116, ix + 75, 300, INK, 1.6)
    s += text(ix + 82, 210, "нитка", 11, INK, "start", style="italic")
    s += line(ix + 28, 300, ix + 122, 300, INK, 2.5)
    s += circle(ix + 28, 300, 8, "#eeeeee", GREY, 2)
    s += circle(ix + 122, 300, 9, "#fdf4f4", RED, 2); s += plus(ix + 122, 300, 5, RED, 1.6)
    s += text(ix + 75, 330, "коромисло з кульками", 10.5, INK, "middle")
    s += text(ix + 75, 378, "(вид збоку)", 11, GREY, "middle", style="italic")
    save("fig-1-2i-1-torsion.svg", s)


# ── Рис. 1.2і.2 — здогад Прістлі (порожнина → 1/r²) ──────────────────────────
def fig_priestley():
    W, H = 800, 450
    s = header(W, H)
    s += text(W / 2, 34, "Здогад Прістлі: порожнеча всередині → закон 1/r²", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "у зарядженій порожнистій кулі всередині немає ні заряду, ні сили — а це можливо лише при оберненому квадраті",
              12, GREY, "middle", style="italic")
    cx, cy, R = 330, 262, 150
    s += circle(cx, cy, R, "none", "#7a93a8", 6)
    for a in range(0, 360, 30):
        x = cx + R * math.cos(math.radians(a)); y = cy - R * math.sin(math.radians(a))
        s += plus(x, y, 7, RED, 1.8)
    s += text(cx, cy - R - 14, "заряд лише на ЗОВНІШНІЙ поверхні", 12.5, RED, "middle", "bold")
    tx, ty = cx - 50, cy
    s += circle(tx, ty, 11, "#f3f5fd", BLUE, 2.2); s += minus(tx, ty, 6, BLUE, 1.8)
    s += text(tx - 4, ty + 28, "пробний заряд", 11.5, INK, "middle", "bold")
    # ближча стінка (мала площа) ліворуч, дальша (велика) праворуч
    nearx, h1 = cx - R, 22
    farx, h2 = cx + R, 44
    s += line(nearx, cy - h1, nearx, cy + h1, GREEN, 5)
    s += line(farx, cy - h2, farx, cy + h2, GREEN, 5)
    for dy in (-1, 1):
        s += line(tx, ty, nearx, cy + dy * h1, GREY, 1.2, "4 3")
        s += line(tx, ty, farx, cy + dy * h2, GREY, 1.2, "4 3")
    s += text(nearx - 6, cy - h1 - 8, "r₁", 13, INK, "end", "bold", "italic")
    s += text(farx + 6, cy - h2 - 8, "r₂ = 2r₁", 13, INK, "start", "bold", "italic")
    s += text(nearx - 6, cy + h1 + 18, "мала площа,", 10.5, INK, "end")
    s += text(nearx - 6, cy + h1 + 32, "велика сила", 10.5, INK, "end")
    s += text(farx + 6, cy + h2 + 18, "площа ×4,", 10.5, INK, "start")
    s += text(farx + 6, cy + h2 + 32, "сила ÷4", 10.5, INK, "start")
    s += rect(cx - 150, H - 64, 300, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(cx, H - 46, "площа ∝ r²,  сила ∝ 1/r²  →  внески ТОЧНО гасяться", 12.5, INK, "middle", "bold")
    s += text(cx, H - 28, "Ньютон довів: нуль усередині буває рівно для 1/r²", 11.5, GREY, "middle", style="italic")
    save("fig-1-2i-2-priestley.svg", s)


# ── Рис. 1.2і.3 — поділ заряду навпіл дотиком ────────────────────────────────
def fig_charge_halving():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Хитрість Кулона: ділити заряд навпіл дотиком", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "торкнути заряджену кулю до однакової незарядженої — заряд ділиться точно навпіл; так задають відомі частки q, не вимірюючи його",
              11.5, GREY, "middle", style="italic")
    cy = 188

    def ball(x, label, sub, charged=True):
        col = RED if charged else GREY
        fill = "#fdf4f4" if charged else "#fafafa"
        out = circle(x, cy, 30, fill, col, 2.6)
        out += text(x, cy + 6, label, 15, col, "middle", "bold")
        out += text(x, cy + 50, sub, 12, GREY, "middle")
        return out

    s += text(145, cy - 50, "1) торкаються", 12, INK, "middle", "bold")
    s += ball(110, "q", "A")
    s += ball(180, "0", "B", charged=False)
    s += arrow(232, cy, 300, cy, INK, 2.4)
    s += text(395, cy - 50, "2) розійшлися", 12, INK, "middle", "bold")
    s += ball(360, "q/2", "A")
    s += ball(430, "q/2", "B")
    s += arrow(482, cy, 548, cy, INK, 2.4)
    s += text(515, cy - 30, "B → нова", 10.5, INK, "middle")
    s += text(515, cy - 16, "куля C", 10.5, INK, "middle")
    s += text(645, cy - 50, "3) повторили", 12, INK, "middle", "bold")
    s += ball(610, "q/4", "B")
    s += ball(680, "q/4", "C")
    s += text(W / 2, 312, "Так дістають точні q/2, q/4, q/8 … — і підтверджують F ∝ q₁·q₂, не знаючи абсолютного заряду.",
              12.5, INK, "middle", "bold")
    save("fig-1-2i-3-charge-halving.svg", s)


# ── трасувальник ліній поля (чисельне інтегрування напрямку E) ────────────────
def _field_at(px, py, charges):
    Ex = Ey = 0.0
    for cx, cy, q in charges:
        dx, dy = px - cx, py - cy
        r2 = dx * dx + dy * dy
        if r2 < 1e-6:
            continue
        r = math.sqrt(r2)
        e = q / r2
        Ex += e * dx / r
        Ey += e * dy / r
    return Ex, Ey


def _trace(px, py, charges, sign, bounds, ds=2.5, steps=1400):
    x0, y0, x1, y1 = bounds
    pts = [(px, py)]
    for _ in range(steps):
        Ex, Ey = _field_at(px, py, charges)
        m = math.hypot(Ex, Ey)
        if m < 1e-9:
            break
        px += sign * ds * Ex / m
        py += sign * ds * Ey / m
        pts.append((px, py))
        if any(math.hypot(px - cx, py - cy) < 7 for cx, cy, q in charges):
            break
        if px < x0 or px > x1 or py < y0 or py > y1:
            break
    return pts


def field_lines(charges, bounds, n_per_plus=14, color=GREEN, w=1.8):
    out = ""
    for cx, cy, q in charges:
        if q <= 0:
            continue
        for k in range(n_per_plus):
            a = 2 * math.pi * k / n_per_plus + 0.2
            sx, sy = cx + 9 * math.cos(a), cy + 9 * math.sin(a)
            pts = _trace(sx, sy, charges, +1, bounds)
            if len(pts) > 4:
                out += polyline(pts, color, w)
                i = int(len(pts) * 0.42)
                if i + 4 < len(pts):
                    out += arrow(pts[i][0], pts[i][1], pts[i + 4][0], pts[i + 4][1], color, w)
    return out


def _src_plus(x, y, r=18):
    return circle(x, y, r, "#fdf4f4", RED, 2.6) + plus(x, y, r * 0.55, RED)


def _src_minus(x, y, r=18):
    return circle(x, y, r, "#f3f5fd", BLUE, 2.6) + minus(x, y, r * 0.55, BLUE)


# ── Рис. 1.3.1 — дія на відстані проти поля ──────────────────────────────────
def fig13_action_vs_field():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Загадка дії на відстані — і відповідь: поле", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "як один заряд відчуває інший крізь порожнечу? Поле — локальний посередник",
              12.5, GREY, "middle", style="italic")
    s += line(W / 2, 80, W / 2, H - 30, FAINT, 1.5)
    # ліворуч: дія на відстані
    s += text(205, 100, "дія на відстані (?)", 14.5, INK, "middle", "bold")
    s += _src_plus(120, 250); s += text(120, 250 - 28, "q₁", 13, RED, "middle", "bold")
    s += _src_plus(300, 250); s += text(300, 250 - 28, "q₂", 13, RED, "middle", "bold")
    s += line(138, 250, 282, 250, GREY, 1.6, "6 5")
    s += text(210, 235, "?", 30, RED, "middle", "bold")
    s += text(205, 320, "Ньютона бентежило: між тілами —", 12, INK, "middle")
    s += text(205, 338, "порожнеча. Що ж передає силу?", 12, INK, "middle")
    # праворуч: поле
    s += text(615, 100, "через поле", 14.5, GREEN, "middle", "bold")
    q1 = (520, 250)
    for a in range(0, 360, 30):
        ex = q1[0] + 86 * math.cos(math.radians(a)); ey = q1[1] + 86 * math.sin(math.radians(a))
        s += arrow(q1[0] + 20 * math.cos(math.radians(a)), q1[1] + 20 * math.sin(math.radians(a)), ex, ey, GREEN, 1.6)
    s += _src_plus(q1[0], q1[1]); s += text(q1[0], q1[1] - 28, "q₁", 13, RED, "middle", "bold")
    s += _src_plus(700, 250); s += text(700, 250 - 28, "q₂", 13, RED, "middle", "bold")
    s += arrow(722, 250, 762, 250, RED, 2.6)
    s += text(742, 240, "F", 13, RED, "middle", "bold", "italic")
    s += text(615, 320, "q₁ заповнює простір полем усюди;", 12, INK, "middle")
    s += text(615, 338, "q₂ реагує на поле САМЕ у своїй точці.", 12, INK, "middle")
    save("fig-1-3-1-action-vs-field.svg", s)


# ── Рис. 1.3.2 — означення поля E = F/q ──────────────────────────────────────
def fig13_definition():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Напруженість поля: E = F / q (сила на одиницю заряду)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "E — властивість точки простору; вона однакова, хоч який пробний заряд туди вмістити",
              12.5, GREY, "middle", style="italic")

    def cell(x, qlab, flen, force_lab):
        out = rect(x, 86, 300, 170, "#fafafa", GREY, 1.6, 12)
        # фонове однорідне поле E (зелені стрілки)
        for yy in (110, 150, 190, 230):
            out += arrow(x + 20, yy, x + 90, yy, GREEN, 1.5)
        out += text(x + 55, 104, "E", 12, GREEN, "middle", "bold", "italic")
        # пробний заряд із силою
        cy = 170
        out += circle(x + 150, cy, 16, "#fdf4f4", RED, 2.4) + plus(x + 150, cy, 9, RED)
        out += text(x + 150, cy - 24, qlab, 13, RED, "middle", "bold")
        out += arrow(x + 168, cy, x + 168 + flen, cy, RED, 3)
        out += text(x + 168 + flen / 2, cy - 10, force_lab, 13, RED, "middle", "bold", "italic")
        return out

    s += cell(50, "+q", 50, "F = qE")
    s += cell(470, "+2q", 100, "2qE")
    s += rect(50, 286, W - 100, 66, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 312, "Подвоївся заряд — подвоїлася сила, але E те саме.", 13.5, INK, "middle", "bold")
    s += text(W / 2, 334, "E = F/q  ·  напрямок E = напрямок сили на ДОДАТНИЙ заряд  ·  одиниця Н/Кл",
              12.5, GREY, "middle")
    save("fig-1-3-2-definition.svg", s)


# ── Рис. 1.3.3 — поле точкового заряду + правила ліній ───────────────────────
def fig13_point_charge():
    W, H = 820, 450
    s = header(W, H)
    s += text(W / 2, 34, "Поле точкового заряду: радіальне, E = k·Q/r²", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "від + лінії виходять назовні, у − входять; чим далі, тим слабше (1/r²)",
              12.5, GREY, "middle", style="italic")
    # + ліворуч
    cxp, cyp = 215, 235
    for a in range(0, 360, 30):
        s += arrow(cxp + 22 * math.cos(math.radians(a)), cyp + 22 * math.sin(math.radians(a)),
                   cxp + 110 * math.cos(math.radians(a)), cyp + 110 * math.sin(math.radians(a)), GREEN, 1.7)
    s += _src_plus(cxp, cyp)
    s += text(cxp, cyp + 145, "додатний: поле НАЗОВНІ", 12.5, INK, "middle", "bold")
    # − праворуч
    cxn, cyn = 605, 235
    for a in range(0, 360, 30):
        s += arrow(cxn + 110 * math.cos(math.radians(a)), cyn + 110 * math.sin(math.radians(a)),
                   cxn + 24 * math.cos(math.radians(a)), cyn + 24 * math.sin(math.radians(a)), GREEN, 1.7)
    s += _src_minus(cxn, cyn)
    s += text(cxn, cyn + 145, "від'ємний: поле ВСЕРЕДИНУ", 12.5, INK, "middle", "bold")
    # правила ліній
    s += rect(60, H - 56, W - 120, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 31, "лінії поля: від + до − · дотична = напрямок сили на +q · густина ∝ |E| · ніколи не перетинаються",
              12, INK, "middle", "bold")
    save("fig-1-3-3-point-charge.svg", s)


# ── Рис. 1.3.4 — поле диполя (+ і −) ─────────────────────────────────────────
def fig13_dipole():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Поле диполя: лінії течуть від + до −", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна лінія починається на додатному заряді й закінчується на від'ємному",
              12.5, GREY, "middle", style="italic")
    charges = [(290, 240, 1.0), (490, 240, -1.0)]
    s += field_lines(charges, (40, 80, 740, 420), n_per_plus=16)
    s += _src_plus(290, 240); s += text(290, 240 - 26, "+", 15, RED, "middle", "bold")
    s += _src_minus(490, 240); s += text(490, 240 - 26, "−", 15, BLUE, "middle", "bold")
    save("fig-1-3-4-dipole.svg", s)


# ── Рис. 1.3.5 — два однойменні заряди (нейтральна точка) ─────────────────────
def fig13_like():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Два однойменні заряди: лінії розштовхуються", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "посередині є точка, де поля гасяться повністю — нейтральна точка (E = 0)",
              12.5, GREY, "middle", style="italic")
    charges = [(290, 240, 1.0), (490, 240, 1.0)]
    s += field_lines(charges, (40, 80, 740, 420), n_per_plus=16)
    s += _src_plus(290, 240); s += _src_plus(490, 240)
    s += line(390, 232, 390, 248, RED, 2.5); s += line(382, 240, 398, 240, RED, 2.5)
    s += text(390, 220, "E = 0", 12.5, RED, "middle", "bold")
    s += text(390, 410, "нейтральна точка", 12, INK, "middle", style="italic")
    save("fig-1-3-5-like-charges.svg", s)


# ── Рис. 1.3.6 — однорідне поле ──────────────────────────────────────────────
def fig13_uniform():
    W, H = 780, 400
    s = header(W, H)
    s += text(W / 2, 34, "Однорідне поле: однакове в кожній точці", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "між двома протилежно зарядженими пластинами лінії паралельні й рівномірні",
              12.5, GREY, "middle", style="italic")
    top, bot = 110, 320
    s += line(140, top, 640, top, RED, 4)
    s += line(140, bot, 640, bot, BLUE, 4)
    for x in range(170, 641, 75):
        s += plus(x, top - 16, 8, RED, 2)
        s += minus(x, bot + 16, 8, BLUE, 2)
    for x in range(180, 631, 65):
        s += arrow(x, top + 8, x, bot - 8, GREEN, 2)
    s += text(390, top - 34, "+  пластина", 13, RED, "middle", "bold")
    s += text(390, bot + 40, "−  пластина", 13, BLUE, "middle", "bold")
    s += text(660, (top + bot) / 2, "E", 15, GREEN, "start", "bold", "italic")
    s += text(390, H - 16, "усередині E скрізь однакове; помітна нерівномірність лишається тільки скраю",
              12, GREY, "middle", style="italic")
    save("fig-1-3-6-uniform-field.svg", s)


# ── Рис. 1.3.7 — поле згущується біля вістря ─────────────────────────────────
def fig13_sharp_points():
    W, H = 800, 400
    s = header(W, H)
    s += text(W / 2, 34, "Поле згущується біля вістря", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "на гострих кінцях лінії поля густішають → там найсильніше E і першим б'є розряд",
              12.5, GREY, "middle", style="italic")
    cx, cy = 330, 230
    s += f'<path d="M {cx - 90},{cy - 60} Q {cx - 150},{cy} {cx - 90},{cy + 60} L {cx + 170},{cy} Z" fill="#eef2f5" stroke="#5b87a6" stroke-width="2.6"/>\n'
    for a in (-70, -35, 0, 35, 70, 110, 180, 250):
        s += plus(cx - 60 + 20 * math.cos(math.radians(a)), cy + 30 * math.sin(math.radians(a)), 6, RED, 1.6)
    s += text(cx - 70, cy + 95, "заряджений провідник", 12, "#5b87a6", "middle", "bold")
    # густі стрілки біля вістря (праворуч)
    tip = (cx + 170, cy)
    for d in (-34, -22, -11, 0, 11, 22, 34):
        s += arrow(tip[0], tip[1], tip[0] + 70 * math.cos(math.radians(d)), tip[1] + 70 * math.sin(math.radians(d)), GREEN, 1.9)
    s += text(tip[0] + 78, cy - 36, "густо → СИЛЬНЕ E", 12.5, GREEN, "start", "bold")
    s += text(tip[0] + 78, cy - 18, "(тут пробій/корона)", 11.5, INK, "start")
    # рідкі стрілки на тупому боці (ліворуч)
    for a in (150, 180, 210):
        sx = cx - 60 + 75 * math.cos(math.radians(a)); sy = cy + 60 * math.sin(math.radians(a))
        s += arrow(sx, sy, sx + 40 * math.cos(math.radians(a)), sy + 40 * math.sin(math.radians(a)), GREEN, 1.6)
    s += text(cx - 150, cy + 60, "рідко →", 12, GREEN, "middle", "bold")
    s += text(cx - 150, cy + 78, "слабке E", 12, GREEN, "middle")
    s += text(W / 2, H - 14, "Тому громовідвід роблять гострим, а високовольтні деталі — округлими, без задирок.",
              12, GREY, "middle", style="italic")
    save("fig-1-3-7-sharp-points.svg", s)


# ── Рис. 1.3і.1 — шлях Фарадея ───────────────────────────────────────────────
def fig_faraday_journey():
    W, H = 830, 560
    s = header(W, H)
    s += text(W / 2, 36, "Шлях Фарадея: від палітурні до основи фізики", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "людина майже без математики дала фізиці її найматематичніше поняття", 12.5, GREY, "middle", style="italic")
    spine, top, bot = 210, 96, H - 26
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1791", "народився в бідній родині коваля під Лондоном"),
        ("1805", "підмайстер палітурника — і жадібно читає книжки, які оправляє"),
        ("1812", "потрапляє на лекції Гемфрі Деві; ретельно конспектує й оправляє нотатки"),
        ("1813", "надсилає нотатки Деві — і стає лаборантом Королівського інституту"),
        ("1831", "відкриває електромагнітну індукцію: рух магніту народжує струм"),
        ("1845", "вводить поняття «поле» й лінії сили — мовою картинок, без формул"),
        ("1860-ті", "Максвелл перекладає його лінії в рівняння — народжується польова фізика"),
    ]
    n = len(nodes)
    for i, (yr, txt) in enumerate(nodes):
        y = top + 24 + (bot - top - 40) * i / (n - 1)
        hot = i in (5,)  # акцент на «поле»
        s += circle(spine, y, 9 if hot else 7, (GREEN if hot else "#fff"), (GREEN if hot else INK), 3 if hot else 2.6)
        s += text(spine - 20, y + 5, yr, 13, GREY, "end", "bold")
        s += text(spine + 24, y + 5, txt, 13.5, (GREEN if hot else INK), "start", "bold" if hot else "normal")
    save("fig-1-3i-1-journey.svg", s)


# ── Рис. 1.3і.2 — лінії сили (ошурки) ────────────────────────────────────────
def fig_lines_of_force():
    W, H = 780, 470
    s = header(W, H)
    s += text(W / 2, 36, "Лінії сили: Фарадей побачив реальним те, що інші мали за порожнечу", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "залізні ошурки довкола магніту шикуються в криві — для Фарадея це карта справжнього стану простору",
              12, GREY, "middle", style="italic")
    N = (300, 258, 1.0); S = (478, 258, -1.0)
    s += field_lines([N, S], (40, 92, 740, 440), n_per_plus=18, color="#9aa0a6", w=1.5)
    # брусок-магніт
    s += rect(288, 240, 100, 36, "#f4d6d2", RED, 2, 4)
    s += rect(388, 240, 102, 36, "#d2dcf4", BLUE, 2, 4)
    s += text(338, 263, "N", 17, RED, "middle", "bold")
    s += text(439, 263, "S", 17, BLUE, "middle", "bold")
    s += rect(60, H - 52, W - 120, 36, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, H - 28, "ту саму ідею ліній, що пронизують простір, Фарадей застосував і до зарядів — це і є лінії електричного поля (§1.3)",
              11.5, INK, "middle", "bold")
    save("fig-1-3i-2-lines-of-force.svg", s)


# ── Рис. 1.3і.3 — від картинки Фарадея до рівнянь Максвелла ───────────────────
def fig_faraday_maxwell():
    W, H = 830, 340
    s = header(W, H)
    s += text(W / 2, 36, "Як наочна картинка стала фундаментом", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "Максвелл переклав лінії сили Фарадея в рівняння — і з них випало світло", 12.5, GREY, "middle", style="italic")
    # бокс 1 — Фарадей
    s += rect(40, 100, 230, 160, "#fafafa", INK, 2, 12)
    s += text(155, 126, "Фарадей (1830–40-ві)", 13.5, INK, "middle", "bold")
    for k in range(4):
        yy = 150 + k * 22
        s += f'<path d="M 70,{yy} Q 155,{yy - 16} 240,{yy}" fill="none" stroke="{GREEN}" stroke-width="1.8"/>\n'
    s += text(155, 252, "лінії сили: картина без формул", 11.5, GREY, "middle", style="italic")
    # стрілка
    s += arrow(278, 180, 332, 180, INK, 2.6)
    s += text(305, 168, "переклад", 11, INK, "middle", "bold")
    # бокс 2 — Максвелл
    s += rect(340, 100, 230, 160, "#f4f7f4", GREEN, 2, 12)
    s += text(455, 126, "Максвелл (1860-ті)", 13.5, INK, "middle", "bold")
    s += text(455, 162, "∇·E = ρ/ε₀", 14, INK, "middle", "bold")
    s += text(455, 188, "∇×E = −∂B/∂t", 14, INK, "middle", "bold")
    s += text(455, 214, "рівняння поля", 11.5, GREY, "middle", style="italic")
    s += text(455, 240, "(картину — у математику)", 11, GREY, "middle", style="italic")
    # стрілка
    s += arrow(578, 180, 632, 180, INK, 2.6)
    # бокс 3 — світло/радіо
    s += rect(640, 100, 150, 160, "#fff7ef", "#c89b5a", 2, 12)
    s += text(715, 126, "звідси:", 13, INK, "middle", "bold")
    wave = "M 656,176 "
    for k in range(1, 60):
        xx = 656 + k * 2.0; yy = 176 - 16 * math.sin(k * 0.5)
        wave += f"L {xx:.1f},{yy:.1f} "
    s += f'<path d="{wave}" fill="none" stroke="{RED}" stroke-width="2"/>\n'
    s += text(715, 212, "світло — хвиля поля", 11.5, INK, "middle", "bold")
    s += text(715, 234, "→ радіо, уся", 11, GREY, "middle")
    s += text(715, 250, "електродинаміка", 11, GREY, "middle")
    save("fig-1-3i-3-faraday-to-maxwell.svg", s)


VIOLET = "#8a52c0"  # еквіпотенціалі


def dcircle(cx, cy, r, color, w=1.6, dash="6 4"):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>\n'


# ── Рис. 1.4.1 — робота переміщення заряду в полі ────────────────────────────
def fig14_work():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Робота над зарядом у полі: W = F·d = qE·d", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "коли заряд рухається під дією сили, передається енергія", 12.5, GREY, "middle", style="italic")

    def band(y, title, with_field):
        out = ""
        for x in (160, 260, 360, 460, 560):
            out += arrow(x, y, x + 50, y, GREEN, 1.5)
        out += text(150, y - 28, "E", 12, GREEN, "end", "bold", "italic")
        out += text(150, y + 4, title, 12.5, INK, "end", "bold")
        # заряд і переміщення
        if with_field:  # рух ЗА полем
            x1, x2 = 220, 480
            out += circle(x1, y, 15, "#fdf4f4", RED, 2.4) + plus(x1, y, 8, RED)
            out += arrow(x1 + 18, y, x2 - 18, y, INK, 2.6)
            out += circle(x2, y, 15, "#fdf4f4", RED, 2.4) + plus(x2, y, 8, RED)
            out += text(350, y - 14, "d", 13, INK, "middle", "bold", "italic")
            out += text(640, y - 6, "поле виконує роботу +qEd;", 11.5, INK, "start")
            out += text(640, y + 12, "заряд РОЗГАНЯЄТЬСЯ (PE→KE)", 11.5, INK, "start", "bold")
        else:  # рух ПРОТИ поля
            x1, x2 = 480, 220
            out += circle(x1, y, 15, "#fdf4f4", RED, 2.4) + plus(x1, y, 8, RED)
            out += arrow(x1 - 18, y, x2 + 18, y, INK, 2.6)
            out += circle(x2, y, 15, "#fdf4f4", RED, 2.4) + plus(x2, y, 8, RED)
            out += text(350, y - 14, "d", 13, INK, "middle", "bold", "italic")
            out += text(640, y - 6, "ти виконуєш роботу qEd;", 11.5, INK, "start")
            out += text(640, y + 12, "ЗАПАСАЄТЬСЯ енергія (PE↑)", 11.5, INK, "start", "bold")
        return out

    s += band(150, "рух за полем →", True)
    s += band(300, "рух проти поля ←", False)
    s += text(W / 2, 405, "Поле — консервативне: робота залежить лише від початку й кінця, а не від шляху (як у гравітації).",
              12, GREY, "middle", style="italic")
    save("fig-1-4-1-work.svg", s)


# ── Рис. 1.4.2 — точна аналогія: висота в гравітації ↔ потенціал ──────────────
def fig14_gravity_analogy():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Точна аналогія: висота (гравітація) ↔ потенціал (поле)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "підняти — запасти енергію; відпустити — вона переходить у рух", 12.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 56, FAINT, 1.5)
    # ЛІВО: гравітація
    s += text(205, 96, "ГРАВІТАЦІЯ", 14, INK, "middle", "bold")
    s += line(80, 330, 330, 330, "#b9a77e", 3)  # земля
    s += f'<path d="M 110,330 L 250,150 L 330,330 Z" fill="#eef2e4" stroke="#9bb06a" stroke-width="2"/>\n'  # гора
    s += circle(250, 150, 13, "#ddd", INK, 2)
    s += text(250, 130, "m", 12, INK, "middle", "bold", "italic")
    s += arrow(250, 168, 250, 320, GREY, 1.6, "5 4")
    s += text(266, 250, "h", 14, INK, "start", "bold", "italic")
    s += arrow(60, 360, 60, 320, BLUE, 2)
    s += text(60, 378, "g", 12, BLUE, "middle", "bold", "italic")
    s += text(205, 360, "PE = m·g·h", 14, INK, "middle", "bold")
    s += text(205, 392, "відпустиш → котиться вниз, PE→KE", 11.5, GREY, "middle", style="italic")
    # ПРАВО: електрика
    s += text(615, 96, "ПОЛЕ", 14, GREEN, "middle", "bold")
    for yy in (140, 180, 220, 260, 300):
        s += arrow(470, yy, 520, yy, GREEN, 1.4)
    s += text(460, 130, "E", 12, GREEN, "end", "bold", "italic")
    s += circle(700, 150, 13, "#fdf4f4", RED, 2.4) + plus(700, 150, 8, RED)
    s += arrow(700, 168, 700, 300, GREY, 1.6, "5 4")
    s += text(716, 240, "d", 14, INK, "start", "bold", "italic")
    s += text(615, 360, "PE = q·E·d", 14, INK, "middle", "bold")
    s += text(615, 392, "відпустиш → лине за полем, PE→KE", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 30, "відповідність: висота h ↔ потенціал;  m·g ↔ q·E.  Розрив аналогії: заряд буває ДВОХ знаків (− «падає вгору»).",
              11.5, INK, "middle", "bold")
    save("fig-1-4-2-gravity-analogy.svg", s)


# ── Рис. 1.4.3 — профіль потенціалу: горб (+) і яма (−) ───────────────────────
def fig14_potential_profile():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 34, "Потенціал як висота: горб (+) і яма (−)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "V = k·Q/r — потенціал точкового заряду; далеко V → 0", 12.5, GREY, "middle", style="italic")

    def subplot(gx0, sign, label):
        gx1 = gx0 + 320
        cx = (gx0 + gx1) / 2
        baseY, topY, botY = 230, 110, 350
        out = line(gx0, baseY, gx1, baseY, GREY, 1.3, "4 3")
        out += text(gx1 + 2, baseY + 4, "V=0", 10.5, GREY, "start")
        out += arrow(cx, botY, cx, topY, INK, 1.5)
        out += text(cx + 6, topY + 4, "V", 12, INK, "start", "bold", "italic")
        col = RED if sign > 0 else BLUE
        K = 3600.0
        for branch in (-1, 1):
            pts = []
            for i in range(0, 150):
                dx = branch * (5 + i * 1.05)
                xx = cx + dx
                if xx < gx0 + 6 or xx > gx1 - 6:
                    break
                V = K / abs(dx)
                yy = baseY - sign * V
                yy = max(topY + 6, min(botY - 6, yy))
                pts.append((xx, yy))
            if len(pts) > 2:
                out += polyline(pts, col, 2.6)
        if sign > 0:
            out += plus(cx, baseY, 9, RED)
        else:
            out += minus(cx, baseY, 9, BLUE)
        out += text(cx, botY + 24, label, 12.5, INK, "middle", "bold")
        return out

    s += subplot(60, +1, "+ заряд: ГОРБ (інші + скочуються геть)")
    s += subplot(440, -1, "− заряд: ЯМА (інші + зсуваються всередину)")
    save("fig-1-4-3-potential-profile.svg", s)


# ── Рис. 1.4.4 — еквіпотенціалі й поле ───────────────────────────────────────
def fig14_equipotentials():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 34, "Еквіпотенціалі: лінії однакового потенціалу", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "поле перпендикулярне до них і вказує «вниз» — від більшого V до меншого", 12.5, GREY, "middle", style="italic")
    cx, cy = 350, 250
    for r, lab in ((58, "V₁"), (108, "V₂"), (162, "V₃")):
        s += dcircle(cx, cy, r, VIOLET, 1.8)
        s += text(cx, cy - r - 6, lab, 12, VIOLET, "middle", "bold")
    for a in range(0, 360, 30):
        s += arrow(cx + 20 * math.cos(math.radians(a)), cy + 20 * math.sin(math.radians(a)),
                   cx + 200 * math.cos(math.radians(a)), cy + 200 * math.sin(math.radians(a)), GREEN, 1.5)
    s += _src_plus(cx, cy)
    s += text(cx, cy + 200, "V₁ > V₂ > V₃ (потенціал спадає назовні)", 12.5, INK, "middle", "bold")
    s += rect(560, 150, 200, 120, "#fbf7ff", VIOLET, 1.6, 10)
    s += text(660, 176, "— — еквіпотенціаль", 12, VIOLET, "middle", "bold")
    s += text(660, 200, "(однаковий V)", 11.5, GREY, "middle")
    s += text(660, 226, "→ лінія поля", 12, GREEN, "middle", "bold")
    s += text(660, 250, "завжди ⊥ еквіпотенціалі", 11, GREY, "middle")
    save("fig-1-4-4-equipotentials.svg", s)


# ── Рис. 1.4.5 — різниця потенціалів і опорний нуль ──────────────────────────
def fig14_potential_difference():
    W, H = 800, 420
    s = header(W, H)
    s += text(W / 2, 34, "Має сенс лише РІЗНИЦЯ потенціалів", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "напруга = V_A − V_B; нуль обираємо самі (як рівень моря для висоти)", 12.5, GREY, "middle", style="italic")
    base = 330
    s += line(90, base, 710, base, "#b9a77e", 2)
    # стовпчик A (високий) і B (нижчий)
    s += rect(180, base - 200, 70, 200, "#fdeeee", RED, 2, 4)
    s += rect(420, base - 110, 70, 110, "#fdeeee", RED, 2, 4)
    s += text(215, base - 212, "A", 14, RED, "middle", "bold")
    s += text(455, base - 122, "B", 14, RED, "middle", "bold")
    s += text(215, base + 18, "V_A", 13, INK, "middle", "bold")
    s += text(455, base + 18, "V_B", 13, INK, "middle", "bold")
    # ΔV
    s += line(300, base - 200, 300, base - 110, INK, 1.4)
    s += arrow(300, base - 110, 300, base - 198, INK, 2)
    s += arrow(300, base - 200, 300, base - 112, INK, 2)
    s += text(316, base - 155, "ΔV = V_A − V_B", 13, INK, "start", "bold")
    s += text(316, base - 137, "(напруга)", 11.5, GREY, "start", style="italic")
    # опорний нуль — земля
    s += line(560, base, 620, base, INK, 2.4)
    s += line(570, base + 8, 610, base + 8, INK, 2.4)
    s += line(578, base + 16, 602, base + 16, INK, 2.4)
    s += text(590, base - 10, "0 В", 12.5, INK, "middle", "bold")
    s += text(590, base + 40, "опорний нуль", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 16, "Зсунь «нуль» куди завгодно — V_A і V_B зміняться, але їхня РІЗНИЦЯ лишиться тією самою.",
              12, GREY, "middle", style="italic")
    save("fig-1-4-5-potential-difference.svg", s)


# ── Рис. 1.4.6 — однорідне поле: V лінійний, E = ΔV/d ────────────────────────
def fig14_field_potential_graph():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "В однорідному полі потенціал спадає лінійно: E = ΔV/d", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "крутість спаду потенціалу і є напруженість поля", 12.5, GREY, "middle", style="italic")
    xL, xR = 150, 640
    # пластини
    s += line(xL, 92, xL, 200, RED, 4)
    s += line(xR, 92, xR, 200, BLUE, 4)
    s += text(xL, 84, "+ пластина", 12.5, RED, "middle", "bold")
    s += text(xR, 84, "− пластина", 12.5, BLUE, "middle", "bold")
    for yy in (118, 146, 174):
        s += arrow(xL + 8, yy, xR - 8, yy, GREEN, 1.8)
    s += text((xL + xR) / 2, 110, "E", 12, GREEN, "middle", "bold", "italic")
    # графік V(x)
    axB = 410
    s += arrow(xL, axB, xR + 20, axB, INK, 1.8)
    s += text(xR + 24, axB + 4, "x", 13, INK, "start", "bold", "italic")
    s += arrow(xL, axB, xL, 250, INK, 1.8)
    s += text(xL - 10, 256, "V", 13, INK, "end", "bold", "italic")
    Vtop = 270
    s += polyline([(xL, Vtop), (xR, axB)], RED, 2.8)
    s += line(xL, Vtop, xL, axB, GREY, 1.2, "4 3")
    s += text(xL - 8, Vtop + 4, "V_макс", 12, RED, "end", "bold")
    s += text(xR + 4, axB - 6, "0", 12, INK, "start", "bold")
    # d
    s += line(xL, axB + 14, xR, axB + 14, GREY, 1.4)
    s += line(xL, axB + 8, xL, axB + 20, GREY, 1.4)
    s += line(xR, axB + 8, xR, axB + 20, GREY, 1.4)
    s += text((xL + xR) / 2, axB + 30, "d (відстань між пластинами)", 12, GREY, "middle", "bold")
    s += text((xL + xR) / 2, 340, "нахил = E = ΔV/d", 13.5, RED, "middle", "bold")
    save("fig-1-4-6-field-potential.svg", s)


# ── Рис. 1.5.1 — означення вольта: 1 Кл × 1 В = 1 Дж ──────────────────────────
def fig15_volt_definition():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 36, "Головна думка: 1 вольт = 1 джоуль на кулон", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "вольт каже, скільки енергії несе КОЖЕН кулон заряду", 12.5, GREY, "middle", style="italic")
    # сходинка потенціалу
    s += rect(90, 130, 150, 18, "#fdeeee", RED, 2, 3)
    s += text(165, 124, "V = 1 В", 13, RED, "middle", "bold")
    s += rect(90, 300, 150, 18, "#e9eefb", BLUE, 2, 3)
    s += text(165, 336, "V = 0", 13, BLUE, "middle", "bold")
    s += rect(150, 150, 40, 26, "#fff", INK, 2, 4)
    s += text(170, 168, "1 Кл", 11.5, INK, "middle", "bold")
    s += arrow(170, 178, 170, 296, INK, 2.6)
    s += text(196, 240, "падає на 1 В", 12, INK, "start")
    # енергія
    s += f'<path d="M150,300 l 8,-10 l 4,8 l 8,-12 l 4,10 l 6,-8" fill="none" stroke="{RED}" stroke-width="2"/>\n'
    s += text(170, 332, "1 Дж", 13, RED, "middle", "bold")
    # рівняння
    s += rect(330, 150, 440, 150, "#f4f7f4", GREEN, 1.8, 12)
    s += text(550, 205, "1 Кл  ×  1 В  =  1 Дж", 24, INK, "middle", "bold")
    s += text(550, 250, "1 В  ≡  1 Дж / Кл", 20, GREEN, "middle", "bold")
    s += text(550, 282, "(вольт — це енергія на одиницю заряду)", 12.5, GREY, "middle", style="italic")
    save("fig-1-5-1-volt-definition.svg", s)


# ── Рис. 1.5.2 — вольт інтенсивний: енергія/заряд стала ───────────────────────
def fig15_intensive():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 36, "Вольт не залежить від кількості заряду", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "та сама напруга 1.5 В: більше заряду — більше енергії, але джоулів НА КУЛОН — порівну",
              12.5, GREY, "middle", style="italic")

    def col(x, qC, eJ, label):
        out = rect(x, 92, 300, 230, "#fafafa", GREY, 1.6, 12)
        out += text(x + 150, 118, "джерело 1.5 В", 12.5, RED, "middle", "bold")
        out += rect(x + 60, 140, 180, 16, "#fdeeee", RED, 1.6, 3)
        out += text(x + 150, 184, qC, 16, INK, "middle", "bold")
        out += arrow(x + 150, 196, x + 150, 250, INK, 2.4)
        out += text(x + 150, 276, eJ, 15, RED, "middle", "bold")
        out += text(x + 150, 306, label, 12, GREY, "middle", style="italic")
        return out

    s += col(50, "1 Кл", "→ 1.5 Дж", "1.5 Дж ÷ 1 Кл = 1.5 В")
    s += col(470, "10 Кл", "→ 15 Дж", "15 Дж ÷ 10 Кл = 1.5 В")
    s += text(W / 2, 350, "Енергія масштабується із зарядом — а відношення енергія/заряд (це й є напруга) лишається 1.5 В.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 374, "Тому напруга — «інтенсивна» величина: вона характеризує джерело, а не порцію заряду.",
              12, GREY, "middle", style="italic")
    save("fig-1-5-2-intensive.svg", s)


# ── Рис. 1.5.3 — водяна аналогія: напруга = тиск/висота ───────────────────────
def fig15_water_analogy():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 36, "Водяна аналогія: напруга — це «висота» (енергія на заряд)", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "висота баку задає енергію кожної краплі; ширина потоку — то вже струм (далі, Розділ 2)",
              12, GREY, "middle", style="italic")
    # опора + бак
    s += line(150, 360, 150, 150, "#aaa", 4)
    s += rect(110, 110, 130, 60, "#d9ecf5", "#5b87a6", 2, 4)
    s += rect(110, 130, 130, 40, "#bfe0ef", "none", 0)
    s += text(175, 100, "бак (джерело)", 12, INK, "middle", "bold")
    # висота
    s += arrow(80, 360, 80, 140, GREEN, 2)
    s += text(64, 250, "h", 15, GREEN, "middle", "bold", "italic")
    s += text(60, 270, "↕ напруга", 11, GREEN, "middle", "bold")
    s += line(60, 360, 250, 360, "#b9a77e", 2)
    # труба з потоком
    s += line(175, 170, 175, 345, "#5b87a6", 8)
    s += line(175, 345, 360, 345, "#5b87a6", 8)
    for dx in (210, 250, 290, 330):
        s += arrow(dx, 345, dx + 18, 345, "#2b7", 2)
    s += text(300, 330, "потік = струм (Розд. 2)", 11.5, "#2b7", "middle", "bold")
    # права частина — відповідність
    s += rect(470, 110, 300, 240, "#f4f7f4", GREEN, 1.6, 12)
    s += text(620, 138, "Відповідність", 14, INK, "middle", "bold")
    rows = [("висота / тиск", "напруга  (Дж/Кл)"),
            ("маса води, що тече", "заряд, що тече"),
            ("витрата (л/с)", "струм (далі)"),
            ("вузька труба гальмує", "опір (далі)")]
    yy = 168
    for a, b in rows:
        s += text(486, yy, a, 12.5, INK, "start")
        s += text(620, yy, "→", 12.5, GREY, "middle")
        s += text(640, yy, b, 12.5, GREEN, "start", "bold")
        yy += 30
    s += text(620, yy + 8, "Межа аналогії: заряд буває двох знаків,", 11, GREY, "middle", style="italic")
    s += text(620, yy + 24, "а «висота» води — лише одного.", 11, GREY, "middle", style="italic")
    save("fig-1-5-3-water-analogy.svg", s)


# ── Рис. 1.5.4 — драбина реальних напруг ─────────────────────────────────────
def fig15_everyday_voltages():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 36, "Драбина реальних напруг — і скільки це Дж на кулон", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "кожен вольт = один джоуль, що його несе кожен кулон заряду", 12, GREY, "middle", style="italic")
    x = 300
    s += line(x, 92, x, 430, INK, 2.5)
    items = [
        ("≈ 1 мВ", "сигнал давача, термопара", BLUE),
        ("1.5 В", "лужний елемент (AA)", INK),
        ("3.7 В", "літій-іонний акумулятор", INK),
        ("5 В", "USB-живлення", INK),
        ("12 В", "автомобільна бортова мережа", INK),
        ("230 В", "побутова мережа (небезпечно!)", RED),
        ("кВ — МВ", "ЛЕП, розряд блискавки", RED),
    ]
    n = len(items)
    for i, (v, what, col) in enumerate(items):
        y = 110 + (430 - 110) * i / (n - 1)
        s += line(x - 7, y, x + 7, y, INK, 2)
        s += text(x - 16, y + 5, v, 14, col, "end", "bold")
        s += text(x + 18, y + 5, what, 13, col, "start", "bold" if col == RED else "normal")
    s += text(x - 16, 96, "менше", 10.5, GREY, "end", style="italic")
    s += text(x - 16, 446, "більше Дж/Кл", 10.5, GREY, "end", style="italic")
    save("fig-1-5-4-everyday-voltages.svg", s)


# ── Рис. 1.5.5 — батарея як насос енергії ────────────────────────────────────
def fig15_battery_pump():
    W, H = 800, 400
    s = header(W, H)
    s += text(W / 2, 36, "Джерело — це насос: піднімає кожен кулон на ΔV", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "запасає qΔV у заряді всередині, а коло потім «спускає» його з користю",
              12, GREY, "middle", style="italic")
    # контур
    L, R, T, B = 200, 600, 120, 320
    # батарея ліворуч
    s += line(L, T, L, B, INK, 2.5)
    s += line(L - 16, 200, L + 16, 200, RED, 3)      # довга риска +
    s += line(L - 10, 216, L + 10, 216, BLUE, 4)     # коротка −
    s += text(L - 40, 205, "+", 16, RED, "middle", "bold")
    s += text(L - 40, 232, "−", 16, BLUE, "middle", "bold")
    s += arrow(L, 250, L, 170, GREEN, 3)
    s += text(L - 70, 215, "насос", 12, GREEN, "middle", "bold")
    s += text(L + 8, 150, "+qΔV запасає", 11.5, GREEN, "start", "bold")
    # верх, право (споживач), низ
    s += line(L, T, R, T, INK, 2.5)
    s += rect(R - 30, 190, 60, 60, "#fff7ef", "#c89b5a", 2.4, 6)
    s += text(R, 224, "спожи-", 11, INK, "middle", "bold")
    s += text(R, 238, "вач", 11, INK, "middle", "bold")
    s += line(R, T, R, 190, INK, 2.5)
    s += line(R, 250, R, B, INK, 2.5)
    s += line(L, B, R, B, INK, 2.5)
    s += text(R + 12, 215, "−qΔV у діло", 11.5, "#c89b5a", "start", "bold")
    # напрямок обходу
    s += arrow(330, T, 380, T, INK, 2)
    s += text(400, 200, "ΔV", 16, INK, "middle", "bold", "italic")
    s += text(400, 300, "(струм і коло — Розділ 2)", 11, GREY, "middle", style="italic")
    s += text(W / 2, H - 16, "Напруга джерела = на скільки джоулів на кулон воно піднімає заряд.",
              12.5, INK, "middle", "bold")
    save("fig-1-5-5-battery-pump.svg", s)


BRASS = "#c9a23a"
ZINC = "#c2c8cc"
COPPER = "#cf8b5e"


# ── Рис. 1.5і.1 — жаб'яча лапка Гальвані ──────────────────────────────────────
def fig_galvani_frog():
    W, H = 800, 440
    s = header(W, H)
    s += text(W / 2, 34, "Гальвані, 1780-ті: чому смикається лапка мертвої жаби?", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "контакт двох металів через тканину — і мертвий м'яз скорочується", 12.5, GREY, "middle", style="italic")
    # залізна опора
    s += rect(470, 90, 26, 300, "#cfd3d6", "#8a8f93", 2, 2)
    s += text(483, 80, "залізна огорожа", 12, "#6b7075", "middle", "bold")
    # латунний гачок
    s += f'<path d="M470,150 q-40,-6 -52,18" fill="none" stroke="{BRASS}" stroke-width="5"/>\n'
    s += text(360, 138, "латунний гачок", 12, BRASS, "middle", "bold")
    # лапка: стегно + гомілка + ступня
    s += f'<path d="M418,168 L398,250 L452,322" fill="none" stroke="#caa98f" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>\n'
    s += circle(452, 322, 9, "#caa98f", "#a98", 2)
    s += text(372, 250, "нерв + м'яз", 12, INK, "end", "bold")
    # дотик ступні до заліза → петля
    s += line(452, 322, 470, 322, "#caa98f", 6)
    # «смикання»
    for dx in (0, 1, 2):
        s += f'<path d="M{462 + dx * 10},300 q12,8 6,22" fill="none" stroke="{RED}" stroke-width="1.6"/>\n'
    s += text(540, 300, "смик!", 13, RED, "start", "bold")
    # петля струму
    s += text(300, 300, "латунь → тканина → залізо", 12, INK, "middle", "bold")
    s += text(300, 318, "= замкнена петля двох металів", 11.5, GREY, "middle", style="italic")
    # тлумачення Гальвані
    s += rect(70, 360, W - 140, 56, "#fafafa", GREY, 1.6, 10)
    s += text(W / 2, 384, "Гальвані: електрика захована в самій тканині — «тваринна електрика».", 13, INK, "middle", "bold")
    s += text(W / 2, 404, "Тіло — наче крихітна лейденська банка, що зберігає життєву силу.", 12, GREY, "middle", style="italic")
    save("fig-1-5i-1-galvani-frog.svg", s)


# ── Рис. 1.5і.2 — суть суперечки: джерело — тканина чи метали? ────────────────
def fig_source_dispute():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 34, "Суть суперечки: де народжується електрика?", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "у самій тканині (Гальвані) — чи на стику двох різних металів (Вольта)?", 12.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 40, FAINT, 1.5)
    # ЛІВО — Гальвані
    s += text(205, 100, "ГАЛЬВАНІ", 15, INK, "middle", "bold")
    s += circle(205, 220, 54, "#fde8e8", RED, 2.4)
    s += f'<path d="M188,205 l10,-14 l5,10 l9,-15 l5,12 l8,-10" fill="none" stroke="{RED}" stroke-width="2.4"/>\n'
    s += text(205, 232, "тканина", 13, RED, "middle", "bold")
    s += text(205, 300, "джерело — сам м'яз", 12.5, INK, "middle", "bold")
    s += text(205, 320, "(«тваринна електрика»)", 11.5, GREY, "middle", style="italic")
    # ПРАВО — Вольта
    s += text(615, 100, "ВОЛЬТА", 15, GREEN, "middle", "bold")
    s += rect(545, 175, 30, 90, ZINC, "#8a8f93", 2, 3)
    s += rect(655, 175, 30, 90, COPPER, "#9c6b48", 2, 3)
    s += rect(575, 205, 80, 30, "#dfeaf0", "#7aa0b5", 1.6, 4)
    s += text(560, 165, "метал A", 11, INK, "middle", "bold")
    s += text(670, 165, "метал B", 11, INK, "middle", "bold")
    s += text(615, 224, "волога", 10.5, "#5b87a6", "middle")
    s += f'<path d="M600,250 l8,-12 l4,9 l7,-12 l4,10" fill="none" stroke="{GREEN}" stroke-width="2.4"/>\n'
    s += text(615, 300, "джерело — стик металів", 12.5, INK, "middle", "bold")
    s += text(615, 320, "жаба лише ЧУТЛИВИЙ прилад", 11.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 18, "Вирішальний крок Вольти: прибрати жабу зовсім — і струм лишається. Отже, джерело — метали.",
              12, INK, "middle", "bold")
    save("fig-1-5i-2-source-dispute.svg", s)


# ── Рис. 1.5і.3 — вольтів стовп ──────────────────────────────────────────────
def fig_voltaic_pile():
    W, H = 780, 480
    s = header(W, H)
    s += text(W / 2, 34, "Вольтів стовп (1800): перше джерело СТАЛОГО струму", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "стопка пар «цинк–мідь», переткана тканиною в розсолі; напруги пар додаються", 12, GREY, "middle", style="italic")
    cx = 250
    top = 96
    bw = 150
    y = top
    zh, ch, clh = 20, 20, 12
    units = 4
    cell_top = y
    for i in range(units):
        s += rect(cx - bw / 2, y, bw, zh, ZINC, "#8a8f93", 1.6, 2)
        s += text(cx, y + 14, "Zn (цинк)", 11, INK, "middle", "bold"); y += zh
        s += rect(cx - bw / 2, y, bw, clh, "#e8dcc0", "#c4b48c", 1.4, 2)
        s += text(cx, y + 10, "розсіл", 9.5, "#8a7a52", "middle"); y += clh
        s += rect(cx - bw / 2, y, bw, ch, COPPER, "#9c6b48", 1.6, 2)
        s += text(cx, y + 14, "Cu (мідь)", 11, "#5a3a26", "middle", "bold"); y += ch
        if i == 0:
            s += line(cx + bw / 2 + 12, cell_top, cx + bw / 2 + 12, y, INK, 1.6)
            s += line(cx + bw / 2 + 6, cell_top, cx + bw / 2 + 12, cell_top, INK, 1.6)
            s += line(cx + bw / 2 + 6, y, cx + bw / 2 + 12, y, INK, 1.6)
            s += text(cx + bw / 2 + 20, (cell_top + y) / 2 - 6, "один", 11.5, INK, "start", "bold")
            s += text(cx + bw / 2 + 20, (cell_top + y) / 2 + 10, "елемент", 11.5, INK, "start", "bold")
        y += 4
    # клеми
    s += line(cx, top, cx - 120, top, RED, 2.4)
    s += line(cx - 120, top, cx - 120, 250, RED, 2.4)
    s += text(cx - 134, top - 4, "+", 16, RED, "middle", "bold")
    s += line(cx, y - 4, cx - 120, y - 4, BLUE, 2.4)
    s += line(cx - 120, y - 4, cx - 120, 252, BLUE, 2.4)
    s += text(cx - 134, y + 6, "−", 16, BLUE, "middle", "bold")
    s += rect(cx - 138, 250, 36, 28, "#fff", INK, 1.6, 4)
    s += text(cx - 120, 268, "I", 14, INK, "middle", "bold", "italic")
    s += text(cx - 120, 296, "сталий струм", 11, INK, "middle", "bold")
    # підпис
    s += rect(440, 110, 300, 260, "#f4f7f4", GREEN, 1.6, 12)
    s += text(590, 138, "Чому це революція", 14, INK, "middle", "bold")
    facts = [
        "• раніше: лише іскра (статика,",
        "  лейденська банка) — мить — і все",
        "• стовп дає БЕЗПЕРЕРВНИЙ потік,",
        "  скільки треба",
        "• за тижні: розклад води струмом;",
        "  далі — Деві, Ерстед, Ампер, Ом,",
        "  Фарадей — уся електрична доба",
        "• Наполеон зробив Вольту графом",
    ]
    yy = 168
    for f in facts:
        s += text(456, yy, f, 12, INK, "start"); yy += 24
    save("fig-1-5i-3-voltaic-pile.svg", s)


# ── Рис. 1.5і.4 — хто переміг і чому обидва імена живуть ──────────────────────
def fig_legacy_names():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Хто мав рацію — і чому живуть обидва імена", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "Вольта виграв суперечку; та й Гальвані вхопив зерно правди", 12.5, GREY, "middle", style="italic")
    # Вольта
    s += rect(50, 86, 340, 230, "#f4f7f4", GREEN, 1.8, 12)
    s += text(220, 114, "ВОЛЬТА — переміг", 15, GREEN, "middle", "bold")
    s += text(220, 144, "батарея = ХІМІЯ різних металів,", 12.5, INK, "middle")
    s += text(220, 164, "а не «життєва сила»", 12.5, INK, "middle")
    s += text(220, 198, "→ одиниця  ВОЛЬТ (В)", 15, INK, "middle", "bold")
    s += text(220, 236, "«тваринна електрика» у тому", 11.5, GREY, "middle", style="italic")
    s += text(220, 252, "значенні була хибна", 11.5, GREY, "middle", style="italic")
    # Гальвані
    s += rect(430, 86, 340, 230, "#fafafa", RED, 1.8, 12)
    s += text(600, 114, "ГАЛЬВАНІ — теж не дарма", 15, RED, "middle", "bold")
    s += text(600, 144, "нерви й м'язи СПРАВДІ працюють", 12.5, INK, "middle")
    s += text(600, 164, "на електриці (біоелектрика)", 12.5, INK, "middle")
    s += text(600, 198, "→ гальванічний, гальванометр,", 13, INK, "middle", "bold")
    s += text(600, 218, "гальванізація;  ЕКГ / ЕЕГ", 13, INK, "middle", "bold")
    s += text(600, 252, "його правда відкрилась пізніше", 11.5, GREY, "middle", style="italic")
    s += rect(120, 336, W - 240, 46, "#fff7ef", "#c89b5a", 1.6, 10)
    s += text(W / 2, 358, "Іронія долі: «гальванічний елемент» — це і є батарея.", 13, INK, "middle", "bold")
    s += text(W / 2, 376, "Ім'я переможеного Гальвані стоїть на винаході переможця Вольти.", 11.5, GREY, "middle", style="italic")
    save("fig-1-5i-4-legacy-names.svg", s)


# ── Рис. 1.6.1 — той самий заряд двома мовами ────────────────────────────────
def fig16_two_descriptions():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Той самий заряд — два описи: поле E і потенціал V", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "одна реальність простору, дві мови — векторна й скалярна", 12.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # ЛІВО — поле
    cxl, cyl = 210, 235
    for a in range(0, 360, 30):
        s += arrow(cxl + 20 * math.cos(math.radians(a)), cyl + 20 * math.sin(math.radians(a)),
                   cxl + 110 * math.cos(math.radians(a)), cyl + 110 * math.sin(math.radians(a)), GREEN, 1.6)
    s += _src_plus(cxl, cyl)
    s += text(210, 110, "мовою ПОЛЯ  E", 14.5, GREEN, "middle", "bold")
    s += text(210, 372, "вектор у кожній точці", 12.5, INK, "middle", "bold")
    s += text(210, 392, "напрямок + величина · Н/Кл = В/м", 11.5, GREY, "middle", style="italic")
    # ПРАВО — потенціал
    cxr, cyr = 610, 235
    for r, v in ((50, "9 В"), (95, "4.5 В"), (150, "3 В")):
        s += dcircle(cxr, cyr, r, VIOLET, 1.8)
        s += text(cxr, cyr - r - 5, v, 11.5, VIOLET, "middle", "bold")
    s += _src_plus(cxr, cyr)
    s += text(610, 110, "мовою ПОТЕНЦІАЛУ  V", 14.5, VIOLET, "middle", "bold")
    s += text(610, 372, "одне число в кожній точці", 12.5, INK, "middle", "bold")
    s += text(610, 392, "лише величина · Дж/Кл = В", 11.5, GREY, "middle", style="italic")
    save("fig-1-6-1-two-descriptions.svg", s)


# ── Рис. 1.6.2 — топографічна аналогія ───────────────────────────────────────
def fig16_topo_map():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Як топографічна карта: висота (V) і схил (E)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "еквіпотенціалі — це ізолінії висоти; поле — стрілки найкрутішого спуску",
              12.5, GREY, "middle", style="italic")
    cx, cy = 300, 250
    radii = [26, 58, 100, 152]
    labs = ["вершина", "", "", "підніжжя"]
    for i, r in enumerate(radii):
        s += dcircle(cx, cy, r, VIOLET, 1.8)
    s += text(cx, cy + 6, "+", 16, RED, "middle", "bold")
    s += text(cx, cy - radii[-1] - 8, "ізолінії = еквіпотенціалі (однакове V)", 12, VIOLET, "middle", "bold")
    # стрілки спуску (поле) — назовні
    for a in range(20, 360, 45):
        s += arrow(cx + 20 * math.cos(math.radians(a)), cy + 20 * math.sin(math.radians(a)),
                   cx + 175 * math.cos(math.radians(a)), cy + 175 * math.sin(math.radians(a)), GREEN, 1.6)
    # позначки крутості
    s += text(cx + 38, cy + 4, "круто", 10.5, INK, "middle", "bold")
    s += text(cx + 38, cy + 16, "(велике E)", 9.5, GREY, "middle")
    s += text(cx - 130, cy - 120, "лінії густі → круто → велике E", 11.5, INK, "start")
    s += text(cx - 130, cy + 130, "лінії рідкі → пологіше → мале E", 11.5, INK, "start")
    # пояснення праворуч
    s += rect(560, 130, 240, 200, "#f4f7f4", GREEN, 1.6, 12)
    s += text(680, 158, "Читаємо карту", 14, INK, "middle", "bold")
    s += text(576, 188, "• ізолінія = однаковий потенціал", 12, INK, "start")
    s += text(576, 212, "• що ближчі ізолінії —", 12, INK, "start")
    s += text(588, 230, "то крутіший схил (більше E)", 12, INK, "start")
    s += text(576, 256, "• стрілка спуску ⊥ ізолініям", 12, INK, "start")
    s += text(576, 280, "• кулька котиться вниз —", 12, INK, "start")
    s += text(588, 298, "за полем, від високого V", 12, INK, "start")
    s += circle(cx + 12, cy - radii[0] - 6, 7, "#ddd", INK, 1.6)
    save("fig-1-6-2-topo-map.svg", s)


# ── Рис. 1.6.3 — поле як нахил потенціалу: E = −dV/dx ────────────────────────
def fig16_gradient():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "Поле — це крутість потенціалу: E = −(нахил V)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "де V падає круто — там E велике; де V рівний — там E = 0", 12.5, GREY, "middle", style="italic")
    x0, x1 = 90, 740

    def Vof(t):  # t у [0,1]
        if t < 0.20:
            return 1.0
        if t < 0.40:
            return 1.0 - (t - 0.20) / 0.20 * 0.6     # круто вниз
        if t < 0.80:
            return 0.4 - (t - 0.40) / 0.40 * 0.2     # полого вниз
        return 0.2

    def Eof(t):
        if t < 0.20 or t >= 0.80:
            return 0.0
        if t < 0.40:
            return 0.6 / 0.20
        return 0.2 / 0.40

    # графік V
    vTop, vBase = 100, 210
    s += text(x0 - 14, 100, "V", 13, INK, "end", "bold", "italic")
    s += line(x0, vBase, x1 + 10, vBase, INK, 1.6)
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        px = x0 + t * (x1 - x0)
        py = vBase - Vof(t) * (vBase - vTop)
        pts.append((px, py))
    s += polyline(pts, VIOLET, 2.8)
    s += text(x1 + 14, vBase, "x", 13, INK, "start", "bold", "italic")
    s += text(x0 + 0.30 * (x1 - x0), 92, "круто", 11, RED, "middle", "bold")
    s += text(x0 + 0.60 * (x1 - x0), 150, "полого", 11, INK, "middle", "bold")
    # графік E
    eTop, eBase = 300, 410
    s += text(x0 - 14, 300, "E", 13, INK, "end", "bold", "italic")
    s += line(x0, eBase, x1 + 10, eBase, INK, 1.6)
    pts2 = []
    Emax = 3.0
    for i in range(0, 201):
        t = i / 200.0
        px = x0 + t * (x1 - x0)
        py = eBase - (Eof(t) / Emax) * (eBase - eTop)
        pts2.append((px, py))
    s += polyline(pts2, GREEN, 2.8)
    s += text(x1 + 14, eBase, "x", 13, INK, "start", "bold", "italic")
    s += text(x0 + 0.30 * (x1 - x0), eTop + 8, "велике E", 11, RED, "middle", "bold")
    s += text(x0 + 0.60 * (x1 - x0), eBase - 34, "мале E", 11, INK, "middle", "bold")
    s += text(x0 + 0.10 * (x1 - x0), eBase - 8, "E=0", 10.5, GREY, "middle")
    s += text(x0 + 0.90 * (x1 - x0), eBase - 8, "E=0", 10.5, GREY, "middle")
    s += text(W / 2, H - 16, "Поле — похідна потенціалу: крутий спад V дає велике E, рівний V — нульове.",
              12, GREY, "middle", style="italic")
    save("fig-1-6-3-gradient.svg", s)


# ── Рис. 1.6.4 — скаляр додавати легше за вектор ─────────────────────────────
def fig16_scalar_vs_vector():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 34, "Чому зручніше рахувати V: скаляр додається просто", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "потенціали — числа (додаєш і все); поля — вектори (потрібні напрямки)",
              12.5, GREY, "middle", style="italic")
    s += line(W / 2, 78, W / 2, H - 30, FAINT, 1.5)
    # ЛІВО — потенціал (скаляр)
    s += text(205, 100, "потенціал V — скаляр", 14, VIOLET, "middle", "bold")
    P = (205, 250)
    s += circle(P[0], P[1], 6, INK, INK, 1)
    s += text(P[0], P[1] + 22, "точка P", 11.5, INK, "middle", "bold")
    s += _src_plus(110, 160, 14); s += text(110, 138, "3 В", 12, RED, "middle", "bold")
    s += _src_plus(300, 160, 14); s += text(300, 138, "2 В", 12, RED, "middle", "bold")
    s += line(120, 168, P[0] - 6, P[1] - 6, GREY, 1.3, "4 3")
    s += line(292, 168, P[0] + 6, P[1] - 6, GREY, 1.3, "4 3")
    s += rect(120, 285, 170, 44, "#fbf7ff", VIOLET, 1.6, 8)
    s += text(205, 312, "V = 3 + 2 = 5 В", 15, VIOLET, "middle", "bold")
    s += text(205, 350, "просто додати числа", 12, GREY, "middle", style="italic")
    # ПРАВО — поле (вектор)
    s += text(615, 100, "поле E — вектор", 14, GREEN, "middle", "bold")
    Q = (615, 250)
    s += circle(Q[0], Q[1], 6, INK, INK, 1)
    s += _src_plus(520, 160, 14); s += _src_plus(710, 160, 14)
    e1 = (Q[0] + 70, Q[1] + 30)
    e2 = (Q[0] - 70, Q[1] + 30)
    s += arrow(Q[0], Q[1], e1[0], e1[1], GREEN, 2.6)
    s += arrow(Q[0], Q[1], e2[0], e2[1], GREEN, 2.6)
    rx = (e1[0] - Q[0]) + (e2[0] - Q[0])
    ry = (e1[1] - Q[1]) + (e2[1] - Q[1])
    s += line(e1[0], e1[1], Q[0] + rx, Q[1] + ry, GREY, 1.3, "5 4")
    s += line(e2[0], e2[1], Q[0] + rx, Q[1] + ry, GREY, 1.3, "5 4")
    s += arrow(Q[0], Q[1], Q[0] + rx, Q[1] + ry, INK, 3)
    s += text(Q[0], Q[1] + ry + 22, "E = E₁ + E₂ (векторно)", 13, INK, "middle", "bold")
    s += text(615, 350, "треба напрямки й проєкції", 12, GREY, "middle", style="italic")
    s += text(W / 2, H - 12, "Тому часто спершу рахують V (легко), а тоді дістають E як його нахил.",
              12, INK, "middle", "bold")
    save("fig-1-6-4-scalar-vs-vector.svg", s)


# ── Рис. 1.6.5 — словник: одне явище, дві мови ───────────────────────────────
def fig16_dictionary():
    W, H = 800, 420
    s = header(W, H)
    s += text(W / 2, 34, "Словник: одне явище — дві мови", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "що рядок — те саме поняття, сказане через поле і через потенціал", 12.5, GREY, "middle", style="italic")
    cx = W / 2
    s += rect(60, 78, W - 120, 300, "none", INK, 1.6, 10)
    s += line(cx, 78, cx, 378, INK, 1.6)
    s += rect(60, 78, (W - 120) / 2, 36, "#eaf5ee", "none", 0)
    s += rect(cx, 78, (W - 120) / 2, 36, "#f3eefb", "none", 0)
    s += text((60 + cx) / 2, 102, "ПОЛЕ  E", 15, GREEN, "middle", "bold")
    s += text((cx + W - 60) / 2, 102, "ПОТЕНЦІАЛ  V", 15, VIOLET, "middle", "bold")
    rows = [
        ("вектор (напрямок + величина)", "скаляр (одне число)"),
        ("сила на заряд:  F = qE", "енергія на заряд:  W = qV"),
        ("Н/Кл  =  В/м", "Дж/Кл  =  В (вольт)"),
        ("«крутість» рельєфу", "«висота» рельєфу"),
        ("E = −(нахил V)", "V = сума E вздовж шляху"),
        ("лінії поля", "еквіпотенціалі (⊥ до ліній)"),
    ]
    y = 134
    for a, b in rows:
        s += text((60 + cx) / 2, y, a, 12.5, INK, "middle")
        s += text((cx + W - 60) / 2, y, b, 12.5, INK, "middle")
        if y < 360:
            s += line(60, y + 12, W - 60, y + 12, FAINT, 1)
        y += 40
    s += text(W / 2, 404, "Дай одне з двох усюди — і друге однозначно відновлюється. Це одна реальність.",
              12.5, GREEN, "middle", "bold")
    save("fig-1-6-5-dictionary.svg", s)


def _box(x, y, w, h, title, lines, fill="#fafafa", stroke=INK, tcol=None):
    out = rect(x, y, w, h, fill, stroke, 2, 10)
    out += text(x + w / 2, y + 23, title, 14, tcol or stroke, "middle", "bold")
    yy = y + 45
    for ln in lines:
        out += text(x + w / 2, yy, ln, 11.5, INK, "middle")
        yy += 18
    return out


# ── Рис. 1.7.1 — карта понять розділу ──────────────────────────────────────────
def fig17_concept_map():
    W, H = 840, 470
    s = header(W, H)
    s += text(W / 2, 34, "Розділ 1 однією картою: як поняття випливають одне з одного", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна стрілка — питання, що вело далі", 12.5, GREY, "middle", style="italic")
    s += _box(60, 96, 230, 84, "ЗАРЯД  (§1.1)", ["дві ознаки: + і −", "квантований, зберігається"])
    s += _box(560, 92, 230, 92, "СИЛА — Кулон (§1.2)", ["F = k·q₁·q₂ / r²", "обернений квадрат"])
    s += _box(60, 300, 300, 104, "ПОЛЕ  E  (§1.3)", ["посередник сили; F = qE", "одиниця Н/Кл = В/м", "«крутість» рельєфу"], "#eaf5ee", GREEN)
    s += _box(490, 300, 300, 104, "ПОТЕНЦІАЛ V (§1.4–1.5)", ["енергія на заряд: W = qV", "ВОЛЬТ = Дж/Кл", "«висота» рельєфу"], "#f3eefb", VIOLET)
    # A → B
    s += arrow(292, 138, 556, 138, INK, 2.4)
    s += text(424, 128, "а наскільки сильно?", 12, INK, "middle", "bold")
    # B → поле/потенціал
    s += arrow(672, 186, 430, 296, INK, 2.4)
    s += text(610, 250, "що передає силу", 11.5, INK, "middle", "bold")
    s += text(610, 266, "крізь порожнечу? (§1.3)", 11.5, GREY, "middle", style="italic")
    # C ⇄ D
    s += arrow(364, 344, 486, 344, VIOLET, 2.6)
    s += arrow(486, 360, 364, 360, GREEN, 2.6)
    s += text(425, 332, "§1.6", 12, INK, "middle", "bold")
    s += text(425, 392, "одне явище", 11, GREY, "middle", style="italic")
    s += rect(120, 420, W - 240, 36, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 443, "Усе разом: заряд → змінює простір (поле / потенціал) → діє силою й енергією на інший заряд.",
              12, INK, "middle", "bold")
    save("fig-1-7-1-concept-map.svg", s)


# ── Рис. 1.7.2 — причинний ланцюг: джерело → простір → ефект ──────────────────
def fig17_causal_chain():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 34, "Одна причинна історія: джерело → простір → ефект", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "заряд не діє «через порожнечу» — він змінює простір, а той діє на інший заряд", 12, GREY, "middle", style="italic")
    # стадія 1 — джерело
    s += text(130, 100, "1. ДЖЕРЕЛО", 13.5, INK, "middle", "bold")
    s += _src_plus(130, 220, 26)
    s += text(130, 270, "заряд Q", 12.5, RED, "middle", "bold")
    # стадія 2 — простір
    s += text(430, 100, "2. УМОВА ПРОСТОРУ", 13.5, GREEN, "middle", "bold")
    cx, cy = 430, 220
    for a in range(0, 360, 45):
        s += arrow(cx + 16 * math.cos(math.radians(a)), cy + 16 * math.sin(math.radians(a)),
                   cx + 60 * math.cos(math.radians(a)), cy + 60 * math.sin(math.radians(a)), GREEN, 1.5)
    s += dcircle(cx, cy, 44, VIOLET, 1.6)
    s += _src_plus(cx, cy, 12)
    s += text(430, 300, "поле E  /  потенціал V", 12.5, INK, "middle", "bold")
    # стадія 3 — ефект
    s += text(710, 100, "3. ЕФЕКТ", 13.5, INK, "middle", "bold")
    s += _src_plus(710, 220, 18)
    s += arrow(732, 220, 786, 220, RED, 3)
    s += text(760, 205, "F = qE", 12, RED, "middle", "bold")
    s += text(710, 268, "інший заряд:", 12, INK, "middle", "bold")
    s += text(710, 286, "сила й енергія W = qV", 11.5, GREY, "middle")
    # стрілки між стадіями
    s += arrow(196, 220, 356, 220, INK, 2.6)
    s += text(276, 205, "створює", 12, INK, "middle", "bold")
    s += arrow(500, 220, 656, 220, INK, 2.6)
    s += text(578, 205, "діє на", 12, INK, "middle", "bold")
    save("fig-1-7-2-causal-chain.svg", s)


# ── Рис. 1.7.3 — місток до струму ────────────────────────────────────────────
def fig17_bridge_to_current():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 34, "Місток до Розділу 2: напруга — це готовність штовхати", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "поки заряди стоять — це статика; дай їм шлях — вони потечуть (струм)", 12, GREY, "middle", style="italic")

    def loop(x0, closed, label, note):
        out = ""
        L, R, T, B = x0, x0 + 230, 110, 270
        # батарея (ліва сторона)
        out += line(L, T, L, B, INK, 2.4)
        out += line(L - 14, 175, L + 14, 175, RED, 3)
        out += line(L - 9, 192, L + 9, 192, BLUE, 4)
        out += text(L - 28, 180, "+", 14, RED, "middle", "bold")
        out += text(L - 28, 205, "−", 14, BLUE, "middle", "bold")
        # верх із ключем
        out += line(L, T, x0 + 95, T, INK, 2.4)
        if closed:
            out += line(x0 + 95, T, x0 + 135, T, INK, 2.4)
        else:
            out += line(x0 + 95, T, x0 + 130, T - 22, INK, 2.4)  # розімкнений ключ
        out += line(x0 + 135, T, R, T, INK, 2.4)
        out += text(x0 + 115, T - 30, "ключ", 10.5, INK, "middle", "bold")
        # споживач, право, низ
        out += rect(R - 16, 165, 32, 44, "#fff7ef", "#c89b5a", 2, 5)
        out += line(R, T, R, 165, INK, 2.4)
        out += line(R, 209, R, B, INK, 2.4)
        out += line(L, B, R, B, INK, 2.4)
        if closed:
            for px in (x0 + 60, x0 + 165):
                out += arrow(px, T, px + 24, T, GREEN, 2.2)
            out += arrow(R, 235, R, 200, GREEN, 2.2)
            out += minus(x0 + 120, B, 7, BLUE, 1.6)
            out += minus(x0 + 90, T, 7, BLUE, 1.6)
        out += text(x0 + 115, B + 26, label, 12.5, (GREEN if closed else INK), "middle", "bold")
        out += text(x0 + 115, B + 44, note, 11, GREY, "middle", style="italic")
        return out

    s += loop(120, False, "розімкнено: напруга є, струму нема", "заряди «готові», але стоять")
    s += loop(490, True, "замкнено: заряд ТЕЧЕ — це струм", "→ Розділ 2")
    s += arrow(372, 200, 476, 200, INK, 3)
    s += text(424, 188, "дай шлях", 11, INK, "middle", "bold")
    save("fig-1-7-3-bridge-to-current.svg", s)


if __name__ == "__main__":
    # Історія до розділу
    fig_timeline()
    fig_dufay()
    fig_franklin()
    fig_gray()
    # §1.1 Заряд
    fig11_atom()
    fig11_transfer()
    fig11_quantization()
    fig11_conservation()
    fig11_scale()
    fig11_cond_insul()
    fig11_tribo()
    fig11_ground()
    fig11_polarization()
    # §1.2 Закон Кулона
    fig12_law()
    fig12_inverse_square()
    fig12_superposition()
    fig12_gravity()
    fig12_medium()
    # Історія до §1.2 — Кулон
    fig_coulomb_torsion()
    fig_priestley()
    fig_charge_halving()
    # §1.3 Поле
    fig13_action_vs_field()
    fig13_definition()
    fig13_point_charge()
    fig13_dipole()
    fig13_like()
    fig13_uniform()
    fig13_sharp_points()
    # Історія до §1.3 — Фарадей
    fig_faraday_journey()
    fig_lines_of_force()
    fig_faraday_maxwell()
    # §1.4 Робота, потенціальна енергія, потенціал
    fig14_work()
    fig14_gravity_analogy()
    fig14_potential_profile()
    fig14_equipotentials()
    fig14_potential_difference()
    fig14_field_potential_graph()
    # §1.5 Вольт = Дж/Кл
    fig15_volt_definition()
    fig15_intensive()
    fig15_water_analogy()
    fig15_everyday_voltages()
    fig15_battery_pump()
    # Історія до §1.5 — Вольта проти Гальвані
    fig_galvani_frog()
    fig_source_dispute()
    fig_voltaic_pile()
    fig_legacy_names()
    # §1.6 Поле й потенціал — одне явище
    fig16_two_descriptions()
    fig16_topo_map()
    fig16_gradient()
    fig16_scalar_vs_vector()
    fig16_dictionary()
    # §1.7 Зведення докупи
    fig17_concept_map()
    fig17_causal_chain()
    fig17_bridge_to_current()
    print("OK — фігури розділу 1 (… + §1.7) згенеровано в", OUT)
