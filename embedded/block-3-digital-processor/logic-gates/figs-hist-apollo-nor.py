# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до §3.2.3 —
«Комп'ютер „Аполлона“ з одного вентиля: NOR, що літав на Місяць» (Модуль 3, Розділ 3.2).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/. Імена файлів мають власний префікс
`fig-15-s3-hist-apollo-*`, щоб не конфліктувати з фігурами тем розділу (fig-15-3-*).

Стиль (AUTHORING §9): білий фон; «1»/істина/high червоний, «0»/хибність/low синій;
поле/висновок зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів історії до теми — Рис. 3.2.3i.k.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (та сама, що в figs.py розділу) ──────────────────────────────────
RED   = "#c0271e"   # «1» / істина / high
BLUE  = "#1f47b5"   # «0» / хибність / low
GREEN = "#1f8a3b"   # дійсне / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
PAPER = "#fafafa"
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


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# гліф NOR (OR-форма з кружком-інверсією) — допоміжний, для діаграм
def gate_nor(x, y, w=58, h=46, fill=PAPER, stroke=INK, sw=2):
    r = h / 2
    body = (f'<path d="M {x},{y-r} Q {x+w*0.55},{y-r} {x+w},{y} '
            f'Q {x+w*0.55},{y+r} {x},{y+r} Q {x+w*0.28},{y} {x},{y-r} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')
    body += circle(x + w + 6, y, 6, "#fff", stroke, sw)
    return body


# ───────────────────────────────────────────────────────────────────────────
# Рис. 3.2.3i.1 — людський ланцюг рішення: ставка на новий чип → один тип
# вентиля → 60 % виробництва ІС у США → Block I/II → Місяць
# ───────────────────────────────────────────────────────────────────────────
def fig_decision():
    W, H = 960, 560
    s = header(W, H)
    s += text(W / 2, 36, "Як ставка на один-єдиний вентиль довела людину до Місяця",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "лабораторія приладобудування MIT, 1961–1969: чим менше типів деталей — тим менше того, що відмовить",
              12.5, GREY, "middle", style="italic")

    spine = 150
    xs = [126, 306, 486, 666, 846]
    yrs = ["1961", "1962", "1963", "1964–66", "1969"]
    heads = ["Задача", "Ризикована ставка", "Попит", "Дві версії", "Місяць"]
    cols = [INK, RED, AMBER, GREEN, GREEN]
    # хребет
    s += line(86, spine, 906, spine, FAINT, 3)
    for x, yr, hd, c in zip(xs, yrs, heads, cols):
        s += circle(x, spine, 8, c, c, 0)
        s += text(x, spine - 22, yr, 14, c, "middle", "bold")
        s += text(x, spine + 28, hd, 13.5, INK, "middle", "bold")

    # картки під кожним вузлом
    def card(cx, lines, hcol):
        bw, bh = 168, 196
        bx, by = cx - bw / 2, spine + 44
        out = rect(bx, by, bw, bh, "#ffffff", hol_or_ink(hol := hcol), 2, 9)
        yy = by + 26
        for ln, sz, col, wt in lines:
            out += text(cx, yy, ln, sz, col, "middle", wt)
            yy += 20 if sz <= 12.5 else 23
        return out

    def hol_or_ink(c):
        return c

    s += card(xs[0], [
        ("Навігація «Аполлона»", 12.5, INK, "bold"),
        ("має рахувати курс", 12, INK, "normal"),
        ("на борту — сама,", 12, INK, "normal"),
        ("без зв'язку із Землею.", 12, INK, "normal"),
        ("", 6, INK, "normal"),
        ("Ціна збою —", 12, BLUE, "normal"),
        ("життя екіпажу.", 12, BLUE, "bold"),
    ], INK)

    s += card(xs[1], [
        ("Інтегральна схема —", 12.5, RED, "bold"),
        ("ще зовсім нова", 12, INK, "normal"),
        ("й неперевірена.", 12, INK, "normal"),
        ("MIT усе одно", 12, INK, "normal"),
        ("ставить на неї —", 12, INK, "normal"),
        ("і лише на ОДИН тип:", 12, INK, "bold"),
        ("3-вхідний NOR.", 12.5, RED, "bold"),
    ], RED)

    s += card(xs[2], [
        ("За оцінкою (перевірити),", 11.5, INK, "normal"),
        ("1963-го програма", 12, INK, "normal"),
        ("з'їдала близько", 12, INK, "normal"),
        ("60 % усіх", 12, AMBER, "bold"),
        ("інтегральних схем,", 12, AMBER, "bold"),
        ("вироблених у США.", 12, INK, "normal"),
    ], AMBER)

    s += card(xs[3], [
        ("Block I:", 12.5, INK, "bold"),
        ("≈ 4100 чипів,", 12, INK, "normal"),
        ("по 1 вентилю NOR.", 12, INK, "normal"),
        ("", 6, INK, "normal"),
        ("Block II:", 12.5, GREEN, "bold"),
        ("≈ 2800 чипів,", 12, INK, "normal"),
        ("по 2 NOR у кожному.", 12, INK, "normal"),
    ], GREEN)

    s += card(xs[4], [
        ("20 липня 1969:", 12.5, GREEN, "bold"),
        ("комп'ютер садить", 12, INK, "normal"),
        ("«Орел» на Місяць.", 12, INK, "normal"),
        ("", 6, INK, "normal"),
        ("Жодного збою", 12, GREEN, "bold"),
        ("обладнання", 12, GREEN, "normal"),
        ("в жодному польоті.", 12, GREEN, "normal"),
    ], GREEN)

    return s


# ───────────────────────────────────────────────────────────────────────────
# Рис. 3.2.3i.2 — піраміда: уся машина виростає з одного NOR
# ───────────────────────────────────────────────────────────────────────────
def fig_pyramid():
    W, H = 980, 580
    s = header(W, H)
    s += text(W / 2, 36, "Уся машина — з однієї цеглинки: NOR знизу доверху",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "універсальність вентиля з §3.2.3, доведена не на папері, а в кремнії, що полетів",
              12.5, GREY, "middle", style="italic")

    # рівні піраміди (знизу — фундамент, угорі — машина)
    levels = [
        ("Бортовий комп'ютер «Аполлона» (AGC)", GREEN, "Block II: ≈ 2800 чипів = ≈ 5600 вентилів NOR"),
        ("Регістри · суматор · АЛП · керування", INK, "арифметика й пам'ять стану з тих самих вентилів"),
        ("Тригери й комбінаційні блоки", INK, "комірки пам'яті та логіка рішень"),
        ("NOT · AND · OR — зібрані з NOR", BLUE, "будь-яка булева операція (Де Морган, §3.2.3)"),
        ("Один 3-вхідний вентиль NOR", RED, "Y = ‾(A + B + C) — єдина «цеглинка» всієї машини"),
    ]
    n = len(levels)
    top_y = 100
    band = 80
    cx = W / 2
    half_top, half_bot = 130, 360
    for i, (title, col, sub) in enumerate(levels):
        # ширина смуги звужується догори (i=0 угорі — найвужча)
        t_up = i / n
        t_dn = (i + 1) / n
        hw_up = half_top + (half_bot - half_top) * t_up
        hw_dn = half_top + (half_bot - half_top) * t_dn
        y0 = top_y + i * band
        y1 = y0 + band - 12
        pts = [(cx - hw_up, y0), (cx + hw_up, y0),
               (cx + hw_dn, y1), (cx - hw_dn, y1)]
        fill = "#ffffff"
        s += f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" stroke="{col}" stroke-width="2.4"/>\n'
        s += text(cx, y0 + 30, title, 15, col, "middle", "bold")
        s += text(cx, y0 + 50, sub, 12, INK, "middle", style="italic")

    bot_y = top_y + n * band - 12
    # стрілка «будується вгору» — вертикально в лівому полі, поза пірамідою
    ax = cx - half_bot - 34
    s += arrow(ax, bot_y, ax, top_y - 2, GREEN, 2.6)
    s += text(ax - 6, (top_y + bot_y) / 2 - 8, "складається", 12.5, GREEN, "end", "bold")
    s += text(ax - 6, (top_y + bot_y) / 2 + 9, "вгору", 12.5, GREEN, "end", "bold")

    # примітка справа — у правому полі, в межах канви
    nx = cx + half_bot + 18
    s += text(nx, bot_y - 30, "вузький верх ⇒", 12, GREY, "start", "normal")
    s += text(nx, bot_y - 13, "мало типів", 12, GREY, "start", "normal")
    s += text(nx, bot_y + 4, "деталей, легше", 12, GREY, "start", "normal")
    s += text(nx, bot_y + 21, "все перевірити", 12, GREY, "start", "normal")

    return s


# ───────────────────────────────────────────────────────────────────────────
# Рис. 3.2.3i.3 — пам'ять-мотузка: програму вплітали руками, біт за бітом
# ───────────────────────────────────────────────────────────────────────────
def fig_rope():
    W, H = 900, 520
    s = header(W, H)
    s += text(W / 2, 36, "Програму не записували — її вплітали голкою, біт за бітом",
              21, INK, "middle", "bold")
    s += text(W / 2, 58, "пам'ять-мотузка (core rope): дріт КРІЗЬ осердя = 1, дріт ПОВЗ осердя = 0",
              12.5, GREY, "middle", style="italic")

    # ── ліворуч: принцип одного біта ──
    s += text(170, 92, "Один біт = як дріт минув осердя", 14, INK, "middle", "bold")
    # осердя 1 (крізь) — «1»
    c1x, c1y = 110, 150
    s += circle(c1x, c1y, 24, "#fff", INK, 2.4)
    s += line(c1x - 70, c1y, c1x + 70, c1y, RED, 3)  # дріт проходить крізь центр
    s += text(c1x, c1y - 34, "КРІЗЬ", 12.5, RED, "middle", "bold")
    s += text(c1x + 92, c1y + 5, "= 1", 17, RED, "start", "bold")
    # осердя 0 (повз) — «0»
    c0x, c0y = 110, 232
    s += circle(c0x, c0y, 24, "#fff", INK, 2.4)
    s += polyline([(c0x - 70, c0y), (c0x - 30, c0y),
                   (c0x - 30, c0y + 40), (c0x + 30, c0y + 40),
                   (c0x + 30, c0y), (c0x + 70, c0y)], BLUE, 3)  # дріт обходить осердя
    s += text(c0x, c0y - 34, "ПОВЗ", 12.5, BLUE, "middle", "bold")
    s += text(c0x + 92, c0y + 5, "= 0", 17, BLUE, "start", "bold")

    s += text(170, 312, "Кожне осердя — багато дротів;", 12, INK, "middle", "normal")
    s += text(170, 330, "одна мотузка тримала", 12, INK, "middle", "normal")
    s += text(170, 348, "≈ 36 тисяч 16-бітних слів —", 12, INK, "middle", "bold")
    s += text(170, 366, "усю прошивку польоту.", 12, INK, "middle", "normal")

    # ── праворуч: «тканина» слова (8 осердь × кілька дротів) ──
    gx0, gy0 = 380, 120
    cols = 8
    rows = 4
    dx, dy = 56, 56
    s += text(gx0 + (cols - 1) * dx / 2, gy0 - 28, "Фрагмент мотузки: рядок дротів кодує слово",
              14, INK, "middle", "bold")
    # осердя-кільця сіткою
    for r in range(rows):
        for cc in range(cols):
            cxp = gx0 + cc * dx
            cyp = gy0 + r * dy
            s += circle(cxp, cyp, 15, "#fff", GREY, 2)
    # один «дріт-слово»: проходить крізь частину кілець (1) і обходить решту (0)
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    wr = 1  # рядок, де ведемо показовий дріт
    wy = gy0 + wr * dy
    path = [(gx0 - 40, wy)]
    for cc in range(cols):
        cxp = gx0 + cc * dx
        if bits[cc]:  # крізь — лінія йде через центр
            path.append((cxp, wy))
        else:         # повз — підіймаємось над кільцем
            path.append((cxp - 16, wy))
            path.append((cxp - 16, wy - 24))
            path.append((cxp + 16, wy - 24))
            path.append((cxp + 16, wy))
    path.append((gx0 + (cols - 1) * dx + 40, wy))
    s += polyline(path, RED, 3)
    # підписи бітів під сіткою
    for cc in range(cols):
        cxp = gx0 + cc * dx
        b = bits[cc]
        s += text(cxp, gy0 + rows * dy + 6, str(b), 15,
                  RED if b else BLUE, "middle", "bold")
    s += text(gx0 + (cols - 1) * dx / 2, gy0 + rows * dy + 30,
              "цей дріт «несе» байт  1 0 1 1 0 0 1 0", 12.5, INK, "middle", style="italic")

    # ── нижня смуга: чесний підпис про людей ──
    by = 430
    s += rect(70, by, 760, 64, "#ffffff", GREEN, 2, 10)
    s += text(90, by + 26,
              "Плели мотузки вручну робітниці заводу Raytheon під Бостоном (часто — колишні ткалі);",
              12.5, INK, "start", "normal")
    s += text(90, by + 46,
              "інженери звали це «методом LOL» — та за прізвиськом стояла копітка, кількаразово перевірена праця.",
              12.5, INK, "start", "normal")
    return s


if __name__ == "__main__":
    save("fig-15-s3-hist-apollo-1-decision.svg", fig_decision())
    save("fig-15-s3-hist-apollo-2-pyramid.svg", fig_pyramid())
    save("fig-15-s3-hist-apollo-3-rope.svg", fig_rope())
    print("done.")
