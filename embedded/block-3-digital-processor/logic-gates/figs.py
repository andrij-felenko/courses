# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 15 — «Логічні вентилі й комбінаційні схеми» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1»/істина червоний, «0»/хибність синій;
поле/«дійсне» зелене; стрілки через marker; шрифт sans-serif. Підписи нумеруються
посекційно (Рис. C.S.N); для історії до розділу — секція 0 (Рис. 15.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # «1» / істина / high
BLUE  = "#1f47b5"   # «0» / хибність / low
GREEN = "#1f8a3b"   # дійсне / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
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


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── гліфи вентилів (відмітні форми; нарощуємо в наступних темах) ─────────────
def gate_and(x, y, w=48, h=46, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    bx = x + w - r
    return (f'<path d="M {x},{y-r} L {bx},{y-r} A {r},{r} 0 0 1 {bx},{y+r} '
            f'L {x},{y+r} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_or(x, y, w=54, h=46, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    return (f'<path d="M {x},{y-r} Q {x+w*0.55},{y-r} {x+w},{y} '
            f'Q {x+w*0.55},{y+r} {x},{y+r} Q {x+w*0.28},{y} {x},{y-r} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_not(x, y, w=40, h=42, fill="#fafafa", stroke=INK, sw=2, bubble=True):
    out = (f'<path d="M {x},{y-h/2} L {x},{y+h/2} L {x+w},{y} Z" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')
    if bubble:
        out += circle(x + w + 6, y, 6, "#fff", stroke, sw)
    return out


# ── Рис. 15.0.1 — таймлайн: від мрії «обчислити думку» до вентиля ───────────
def fig_timeline():
    W, H = 880, 770
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: чи можна РАХУВАТИ міркування?", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "від силогізмів до кремнієвого вентиля; сірим — постаті з власною історією деінде в курсі",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 100, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("~350 до н.е.", "Аристотель / Aristotle", "Чи можна впорядкувати ПРАВИЛЬНЕ міркування? — силогізми", False),
        ("~1680", "Лейбніц / Leibniz", "А чи можна його ОБЧИСЛИТИ, як числа? — мрія «calculus ratiocinator» (→ Розділ 17)", True),
        ("1847·1854", "Буль / Boole", "Логіка — це АЛГЕБРА з 0 і 1! — «Закони думки»", False),
        ("1847", "Де Морган / De Morgan", "Двоїстість: НЕ(і) = (не)АБО(не) — закони Де Моргана", False),
        ("1850–1930", "«лише курйоз»", "Алгебра логіки — гарна, та без жодного застосування", False),
        ("1937", "Шеннон / Shannon", "Реле — це і Є булева алгебра! — застосування знайдено (→ Розділ 14)", True),
        ("тепер", "вентилі / logic gates", "булеві операції, відлиті в кремній — цей розділ", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, faint) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if faint else INK
        if i == 2:  # Буль — акцент
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if i == 2 else col), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, col, "start", style="italic")
    save("fig-15-0-1-timeline.svg", s)


# ── Рис. 15.0.2 — ідея Буля: міркування → алгебра з 0 і 1 ───────────────────
def fig_idea():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Ідея Буля: звести міркування до алгебри з двома значеннями", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "змінна — це твердження, що буває лише ІСТИННИМ (1) або ХИБНИМ (0); три дії будують усе інше",
              12.5, GREY, "middle", style="italic")

    def op(x0, title, phrase, expr, rows):
        out = rect(x0, 90, 250, 300, "none", INK, 1.6, 12)
        out += text(x0 + 125, 118, title, 16, INK, "middle", "bold")
        out += text(x0 + 125, 142, phrase, 11.5, GREY, "middle", style="italic")
        out += text(x0 + 125, 174, expr, 18, RED, "middle", "bold")
        # міні-таблиця
        cw, ch = 40, 22
        tx = x0 + 125 - 1.5 * cw
        ty = 200
        heads = ["A", "B", "="]
        for c, hh in enumerate(heads):
            out += rect(tx + c * cw, ty, cw, ch, "#f3f3f3", GREY, 1.1)
            out += text(tx + c * cw + cw / 2, ty + 15, hh, 12, INK, "middle", "bold")
        for r, (a, b, q) in enumerate(rows):
            yy = ty + ch * (r + 1)
            vals = (a, b, q) if b is not None else (a, "", q)
            for c, v in enumerate(vals):
                col = (RED if v == 1 else BLUE) if v in (0, 1) else GREY
                bg = "#fdf4f4" if v == 1 else ("#f3f5fd" if v == 0 else "#fff")
                out += rect(tx + c * cw, yy, cw, ch, bg, GREY, 1.1)
                if v != "":
                    out += text(tx + c * cw + cw / 2, yy + 15, str(v), 12, col, "middle", "bold")
        return out

    s += op(60, "І  (AND)", "«A і B істинні»", "A · B",
            [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)])
    s += op(315, "АБО  (OR)", "«A або B»", "A + B",
            [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])
    s += op(570, "НЕ  (NOT)", "«не A»", "Ā",
            [(0, None, 1), (1, None, 0)])
    s += text(W / 2, 420, "Усе людське «і / або / не», уся логіка міркувань — зводиться до цих трьох дій над 0 і 1.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 442, "Це й був зухвалий здогад Буля: думка підкоряється алгебрі.", 12, GREY, "middle", style="italic")
    save("fig-15-0-2-idea.svg", s)


# ── Рис. 15.0.3 — дивна алгебра: x·x = x ────────────────────────────────────
def fig_strange():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 36, "Дивна алгебра, де x · x = x: чому значень саме два", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58, "Буль помітив: тотожність x·x = x справджується ЛИШЕ для 0 і 1 — то нехай вони й будуть значеннями логіки",
              12, GREY, "middle", style="italic")

    def col(x0, title, rows, accent):
        out = rect(x0, 92, 360, 248, "#fafafa" if not accent else "#f4f7f4",
                   INK if not accent else GREEN, 1.8, 12)
        out += text(x0 + 180, 120, title, 15, INK if not accent else GREEN, "middle", "bold")
        for i, (lhs, rhs, note) in enumerate(rows):
            yy = 156 + i * 44
            out += text(x0 + 24, yy, lhs, 15, INK, "start", "bold")
            out += text(x0 + 150, yy, "=", 15, GREY, "middle")
            out += text(x0 + 178, yy, rhs, 15, (GREEN if accent else INK), "start", "bold")
            out += text(x0 + 24, yy + 18, note, 11, GREY, "start", style="italic")
        return out

    s += col(60, "Звичайна алгебра чисел", [
        ("x · x", "x²", "будь-яке число в квадраті"),
        ("1 + 1", "2", "рахуємо кількість"),
        ("x", "будь-що", "нескінченно багато значень"),
    ], False)
    s += col(440, "Алгебра Буля (логіка)", [
        ("x · x", "x", "«істинно І істинно» = істинно"),
        ("1 + 1", "1", "«істинно АБО істинно» = істинно"),
        ("x", "0 або 1", "лише два значення"),
    ], True)
    s += text(W / 2, 372, "Саме x·x = x «відсіює» всі числа, крім 0 та 1 — і робить алгебру Буля двозначною.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 394, "Через 90 років ці 0/1 ляжуть на «розімкнено/замкнено», «низько/високо» — і стануть бітом.", 12, GREY, "middle", style="italic")
    save("fig-15-0-3-strange.svg", s)


# ── Рис. 15.0.4 — місток: булева операція → кремнієвий вентиль ──────────────
def fig_bridge():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 36, "Місток у цей розділ: кожна булева операція — це вентиль", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58, "те, що Буль писав символами на папері, ми будуватимемо транзисторами — як фізичні елементи",
              12, GREY, "middle", style="italic")

    # AND
    y1 = 150
    s += text(120, y1 + 6, "A · B", 19, RED, "end", "bold")
    s += arrow(140, y1, 250, y1, INK, 2.2)
    s += line(258, y1 - 12, 300, y1 - 12, INK, 1.8)
    s += line(258, y1 + 12, 300, y1 + 12, INK, 1.8)
    s += gate_and(300, y1)
    s += line(348, y1, 380, y1, INK, 1.8)
    s += text(470, y1 + 6, "вентиль AND («і»)", 15, INK, "start", "bold")
    # OR
    y2 = 250
    s += text(120, y2 + 6, "A + B", 19, RED, "end", "bold")
    s += arrow(140, y2, 250, y2, INK, 2.2)
    s += line(258, y2 - 12, 302, y2 - 12, INK, 1.8)
    s += line(258, y2 + 12, 302, y2 + 12, INK, 1.8)
    s += gate_or(300, y2)
    s += line(354, y2, 384, y2, INK, 1.8)
    s += text(470, y2 + 6, "вентиль OR («або»)", 15, INK, "start", "bold")
    # NOT
    y3 = 350
    s += text(120, y3 + 6, "Ā", 19, RED, "end", "bold")
    s += arrow(140, y3, 250, y3, INK, 2.2)
    s += line(280, y3, 300, y3, INK, 1.8)
    s += gate_not(300, y3)
    s += line(346, y3, 384, y3, INK, 1.8)
    s += text(470, y3 + 6, "вентиль NOT (інвертор)", 15, INK, "start", "bold")
    s += text(W / 2, 404, "Папір Буля (1854) → кремній (сьогодні). Розділ 15 — це Буль, що ожив у залізі.",
              12.5, GREEN, "middle", "bold")
    save("fig-15-0-4-bridge.svg", s)


# ── спільний помічник: таблиця істинності ───────────────────────────────────
def ttable(x, y, headers, rows, cw=40, ch=24, out_cols=(-1,)):
    out = ""
    n = len(headers)
    oc = set((i if i >= 0 else n + i) for i in out_cols)
    for c, hh in enumerate(headers):
        out += rect(x + c * cw, y, cw, ch, "#eceef0", GREY, 1.2)
        out += text(x + c * cw + cw / 2, y + ch * 0.68, hh, 12.5, INK, "middle", "bold")
    for r, row in enumerate(rows):
        yy = y + ch * (r + 1)
        for c, v in enumerate(row):
            is_out = c in oc
            col = RED if v == 1 else BLUE
            if is_out:
                bg = "#eafaef" if v == 1 else "#f3f5fd"
                tc = GREEN if v == 1 else BLUE
            else:
                bg = "#fdf4f4" if v == 1 else "#f3f5fd"
                tc = col
            out += rect(x + c * cw, yy, cw, ch, bg, GREY, 1.1)
            out += text(x + c * cw + cw / 2, yy + ch * 0.68, str(v), 12.5, tc, "middle", "bold")
    return out


# ═══════════════════════ §15.1 — Булева алгебра ══════════════════════════════
# ── Рис. 15.1.1 — що таке таблиця істинності ────────────────────────────────
def fig151_truthtable():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 36, "Таблиця істинності: повний опис логічної функції", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "перелічуємо ВСІ можливі входи й кажемо вихід для кожного — n входів дає 2ⁿ рядків",
              12.5, GREY, "middle", style="italic")
    # функція-блок
    bx, by = 120, 175
    s += rect(bx, by, 130, 90, "#eef4ff", INK, 2, 10)
    s += text(bx + 65, by + 42, "логічна", 13, INK, "middle", "bold")
    s += text(bx + 65, by + 60, "функція", 13, INK, "middle", "bold")
    s += line(bx - 50, by + 28, bx, by + 28, INK, 2)
    s += text(bx - 56, by + 32, "A", 13, INK, "end", "bold")
    s += line(bx - 50, by + 62, bx, by + 62, INK, 2)
    s += text(bx - 56, by + 66, "B", 13, INK, "end", "bold")
    s += line(bx + 130, by + 45, bx + 185, by + 45, INK, 2)
    s += text(bx + 192, by + 49, "Y", 13, GREEN, "start", "bold")
    s += text(bx + 65, by + 116, "2 входи → 4 рядки", 11.5, GREY, "middle", style="italic")
    # таблиця
    s += ttable(420, 120, ["A", "B", "Y"],
                [(0, 0, "?"), (0, 1, "?"), (1, 0, "?"), (1, 1, "?")], cw=54, ch=30)
    s += text(420 + 81, 120 + 30 * 5 + 22, "Y — будь-який стовпчик з 0/1", 11.5, GREY, "middle", style="italic")
    # масштаб
    s += rect(620, 150, 200, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(720, 176, "Скільки рядків?", 12.5, INK, "middle", "bold")
    for i, (n, r) in enumerate([("1 вхід", "2 рядки"), ("2 входи", "4 рядки"),
                                ("3 входи", "8 рядків"), ("4 входи", "16 рядків")]):
        s += text(636, 202 + i * 24, n, 12, INK, "start")
        s += text(804, 202 + i * 24, r, 12, GREEN, "end", "bold")
    save("fig-15-1-1-truthtable.svg", s)


# ── Рис. 15.1.2 — три дії: AND / OR / NOT ───────────────────────────────────
def fig151_three_ops():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 36, "Три базові дії булевої алгебри", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "усе інше будується з них; подаємо обидві нотації — інженерну (· + ‾) і математичну (∧ ∨ ¬)",
              12.5, GREY, "middle", style="italic")
    # AND
    s += text(170, 100, "AND  «і»", 15, INK, "middle", "bold")
    s += text(170, 120, "A · B   =   A ∧ B", 13, RED, "middle", "bold")
    s += ttable(110, 135, ["A", "B", "A·B"], [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)], cw=40, ch=26)
    s += text(170, 290, "1, лише коли ОБИДВА 1", 11, GREY, "middle", style="italic")
    # OR
    s += text(450, 100, "OR  «або»", 15, INK, "middle", "bold")
    s += text(450, 120, "A + B   =   A ∨ B", 13, RED, "middle", "bold")
    s += ttable(390, 135, ["A", "B", "A+B"], [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)], cw=40, ch=26)
    s += text(450, 290, "1, коли ХОЧ ОДИН 1", 11, GREY, "middle", style="italic")
    # NOT
    s += text(720, 100, "NOT  «не»", 15, INK, "middle", "bold")
    s += text(720, 120, "Ā   =   ¬A", 13, RED, "middle", "bold")
    s += ttable(680, 135, ["A", "Ā"], [(0, 1), (1, 0)], cw=44, ch=26)
    s += text(720, 240, "перевертає 0↔1", 11, GREY, "middle", style="italic")
    s += rect(70, 330, W - 140, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 354, "Будь-яку логічну функцію — хоч яку складну — можна записати лише цими трьома діями.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 374, "Саме тому вони — «алфавіт» цифрової техніки.", 12, GREY, "middle", style="italic")
    save("fig-15-1-2-three-ops.svg", s)


# ── Рис. 15.1.3 — погляд через множини (як думав Буль) ──────────────────────
def _lens(cx1, cx2, cy, r, fill):
    d = cx2 - cx1
    a = d / 2.0
    h = math.sqrt(max(r * r - a * a, 0))
    xt, yt = cx1 + a, cy - h
    xb, yb = cx1 + a, cy + h
    return (f'<path d="M {xt:.1f},{yt:.1f} A {r},{r} 0 0 1 {xb:.1f},{yb:.1f} '
            f'A {r},{r} 0 0 1 {xt:.1f},{yt:.1f} Z" fill="{fill}" stroke="none"/>\n')


def fig151_venn():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 36, "Та сама логіка через множини — як і думав Буль про «класи»", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58, "AND — це перетин, OR — об'єднання, NOT — доповнення (усе поза множиною)",
              12.5, GREY, "middle", style="italic")

    def panel(ox, title, mode):
        nonlocal s
        s += rect(ox, 90, 250, 200, "none", FAINT, 1.5, 10)
        s += text(ox + 125, 114, title, 14, INK, "middle", "bold")
        cy = 200
        c1, c2 = ox + 95, ox + 155
        r = 46
        if mode == "not":
            s += rect(ox + 18, 130, 214, 130, "#eafaef", "none", 0)
            s += circle(ox + 125, cy, r, "#ffffff", INK, 2)
            s += text(ox + 125, cy + 4, "A", 13, INK, "middle", "bold")
            s += text(ox + 40, 152, "Ā", 14, GREEN, "middle", "bold")
        else:
            if mode == "and":
                s += _lens(c1, c2, cy, r, "#cdeccf")
            else:  # or
                s += circle(c1, cy, r, "#cdeccf", "none", 0)
                s += circle(c2, cy, r, "#cdeccf", "none", 0)
            s += circle(c1, cy, r, "none", INK, 2)
            s += circle(c2, cy, r, "none", INK, 2)
            s += text(c1 - 20, cy + 4, "A", 13, INK, "middle", "bold")
            s += text(c2 + 20, cy + 4, "B", 13, INK, "middle", "bold")
        return

    panel(50, "AND = перет: A · B", "and")
    s += text(175, 305, "тільки спільне", 11, GREEN, "middle", "bold")
    panel(315, "OR = об'єдн.: A + B", "or")
    s += text(440, 305, "усе разом", 11, GREEN, "middle", "bold")
    panel(580, "NOT = поза: Ā", "not")
    s += text(705, 305, "усе, що НЕ A", 11, GREEN, "middle", "bold")
    save("fig-15-1-3-venn.svg", s)


# ── Рис. 15.1.4 — закони булевої алгебри (шпаргалка) ────────────────────────
def fig151_laws():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Закони булевої алгебри: чим спрощують вирази", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "ці тотожності — інструмент Шеннона: ними схему зводять до меншої, перш ніж паяти",
              12.5, GREY, "middle", style="italic")
    laws = [
        ("Тотожність", "A + 0 = A", "A · 1 = A"),
        ("Поглинання", "A + 1 = 1", "A · 0 = 0"),
        ("Ідемпотентність", "A + A = A", "A · A = A"),
        ("Доповнення", "A + Ā = 1", "A · Ā = 0"),
        ("Подвійне НЕ", "Ā̄ = A", ""),
        ("Комутативність", "A + B = B + A", "A · B = B · A"),
        ("Асоціативність", "A+(B+C) = (A+B)+C", "A·(B·C) = (A·B)·C"),
        ("Дистрибутивність", "A·(B+C) = A·B + A·C", "A+(B·C) = (A+B)·(A+C)"),
        ("Поглинання (абсорбц.)", "A + A·B = A", "A · (A+B) = A"),
        ("Де Морган (→ §15.3)", "‾(A·B) = Ā + B̄", "‾(A+B) = Ā · B̄"),
    ]
    x0, y0 = 70, 96
    rowh = 35
    s += rect(x0, y0, W - 140, rowh * len(laws) + 8, "none", GREY, 1.2, 8)
    for i, (name, l1, l2) in enumerate(laws):
        yy = y0 + 26 + i * rowh
        if i % 2 == 0:
            s += rect(x0, yy - 22, W - 140, rowh, "#f6f8f6", "none", 0)
        s += text(x0 + 16, yy, name, 12.5, INK, "start", "bold")
        s += text(x0 + 250, yy, l1, 13.5, INK, "start")
        if l2:
            s += text(x0 + 510, yy, l2, 13.5, INK, "start")
    s += text(x0 + 250, y0 + 26 + len(laws) * rowh + 6, "Друга дистрибутивність (A+B·C=…) — суто булева: в арифметиці чисел її НЕ буває.",
              11.5, GREY, "start", style="italic")
    save("fig-15-1-4-laws.svg", s)


# ── Рис. 15.1.5 — спрощення: три елементи → дріт ────────────────────────────
def fig151_simplify():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 36, "Навіщо алгебра: спростити схему, перш ніж її будувати", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58, "три вентилі ліворуч і простий дріт праворуч роблять ТЕ САМЕ — алгебра це доводить",
              12.5, GREY, "middle", style="italic")
    # кроки
    s += text(110, 110, "A·B + A·B̄", 16, INK, "start", "bold")
    s += text(360, 110, "= A·(B + B̄)", 15, INK, "start")
    s += text(360, 110 + 26, "[дистрибутивність]", 11, GREY, "start", style="italic")
    s += text(580, 110, "= A·1", 15, INK, "start")
    s += text(580, 110 + 26, "[доповнення B+B̄=1]", 11, GREY, "start", style="italic")
    s += text(740, 110, "= A", 16, GREEN, "start", "bold")
    s += text(740, 110 + 26, "[тотожність]", 11, GREY, "start", style="italic")
    # було: 3 елементи
    s += text(230, 185, "БУЛО: 3 вентилі", 13, INK, "middle", "bold")
    s += gate_not(150, 250, 30, 30)
    s += text(120, 254, "B", 12, INK, "end", "bold")
    s += gate_and(220, 215, 40, 34)
    s += gate_and(220, 285, 40, 34)
    s += gate_or(300, 250, 44, 38)
    s += line(110, 230, 200, 230, INK, 1.6)
    s += text(104, 234, "A", 12, INK, "end", "bold")
    s += line(186, 250, 220, 226, INK, 1.4)
    s += line(110, 300, 220, 300, INK, 1.6)
    s += text(360, 254, "→", 22, GREY, "middle")
    # стало: дріт
    s += text(560, 185, "СТАЛО: просто дріт", 13, GREEN, "middle", "bold")
    s += line(470, 250, 650, 250, GREEN, 3)
    s += text(462, 254, "A", 13, INK, "end", "bold")
    s += text(658, 254, "Y = A", 13, GREEN, "start", "bold")
    s += circle(470, 250, 3.5, GREEN, GREEN, 1)
    s += rect(70, 360, W - 140, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 385, "Менше вентилів → дешевше, швидше, менше тепла. Оце і є «спростити алгеброю» з історії Шеннона.",
              12.5, INK, "middle", "bold")
    save("fig-15-1-5-simplify.svg", s)


# ── Рис. 15.1.6 — сума добутків: будь-яка функція з трьох дій ───────────────
def fig151_sop():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 36, "Будь-яку таблицю можна записати виразом: сума добутків (SOP)", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "для кожного рядка з виходом 1 пишемо «добуток» (AND) входів, тоді з'єднуємо їх «сумою» (OR)",
              12, GREY, "middle", style="italic")
    rows = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
    s += ttable(110, 110, ["A", "B", "Y"], rows, cw=46, ch=30)
    # позначити рядки з Y=1
    terms = []
    for r, (a, b, y) in enumerate(rows):
        yy = 110 + 30 * (r + 1)
        if y == 1:
            s += rect(110, yy, 46 * 3, 30, "none", GREEN, 2)
            at = "A" if a == 1 else "Ā"
            bt = "B" if b == 1 else "B̄"
            term = f"{at}·{bt}"
            terms.append(term)
            s += text(110 + 46 * 3 + 16, yy + 20, "→  " + term, 13.5, GREEN, "start", "bold")
    # вираз
    s += text(430, 200, "беремо рядки, де Y = 1:", 12.5, INK, "start", "bold")
    s += text(430, 232, terms[0] + "   (рядок 01)", 14, GREEN, "start", "bold")
    s += text(430, 258, terms[1] + "   (рядок 10)", 14, GREEN, "start", "bold")
    s += line(430, 274, 760, 274, GREY, 1.2)
    s += text(430, 300, "Y = " + terms[0] + " + " + terms[1], 17, RED, "start", "bold")
    s += text(430, 324, "(з'єднали «сумою» OR)", 11.5, GREY, "start", style="italic")
    s += rect(70, 350, W - 140, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 374, "Висновок: AND + OR + NOT — це ПОВНИЙ набір. З них будується БУДЬ-ЯКА логічна функція.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 394, "(ця конкретна функція — «рівно один із двох» — така корисна, що має власний вентиль: XOR, §15.4)", 11, GREY, "middle", style="italic")
    save("fig-15-1-6-sop.svg", s)


# ═══════════════════════ §15.2 — Базові вентилі ══════════════════════════════
def _pin(x1, y1, x2, y2):
    return line(x1, y1, x2, y2, INK, 1.8)


def _iec(x, y, w, h, label, bubble=False):
    out = rect(x, y - h / 2, w, h, "#fafafa", INK, 2, 0)
    out += text(x + w / 2, y + 5, label, 14, INK, "middle", "bold")
    if bubble:
        out += circle(x + w + 6, y, 6, "#fff", INK, 2)
    return out


# ── Рис. 15.2.1 — символи трьох вентилів + таблиці ──────────────────────────
def fig152_symbols():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Базові вентилі: символ + поведінка (відмітні форми)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "форма символа сама підказує функцію; входи зліва, вихід справа",
              12.5, GREY, "middle", style="italic")
    # AND
    gx, gy = 150, 150
    s += _pin(gx - 42, gy - 12, gx, gy - 12)
    s += text(gx - 48, gy - 8, "A", 12, INK, "end", "bold")
    s += _pin(gx - 42, gy + 12, gx, gy + 12)
    s += text(gx - 48, gy + 16, "B", 12, INK, "end", "bold")
    s += gate_and(gx, gy)
    s += _pin(gx + 48, gy, gx + 86, gy)
    s += text(gx + 92, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 24, gy - 44, "AND (кон'юнктор)", 13, INK, "middle", "bold")
    s += text(gx + 24, gy + 48, "Y = A · B", 14, RED, "middle", "bold")
    s += ttable(gx - 26, gy + 66, ["A", "B", "Y"], [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)], cw=36, ch=24)
    # OR
    gx = 440
    s += _pin(gx - 42, gy - 12, gx + 4, gy - 12)
    s += text(gx - 48, gy - 8, "A", 12, INK, "end", "bold")
    s += _pin(gx - 42, gy + 12, gx + 4, gy + 12)
    s += text(gx - 48, gy + 16, "B", 12, INK, "end", "bold")
    s += gate_or(gx, gy)
    s += _pin(gx + 54, gy, gx + 90, gy)
    s += text(gx + 96, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 27, gy - 44, "OR (диз'юнктор)", 13, INK, "middle", "bold")
    s += text(gx + 27, gy + 48, "Y = A + B", 14, RED, "middle", "bold")
    s += ttable(gx - 20, gy + 66, ["A", "B", "Y"], [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)], cw=36, ch=24)
    # NOT
    gx = 720
    s += _pin(gx - 42, gy, gx, gy)
    s += text(gx - 48, gy + 4, "A", 12, INK, "end", "bold")
    s += gate_not(gx, gy)
    s += _pin(gx + 52, gy, gx + 88, gy)
    s += text(gx + 94, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 20, gy - 44, "NOT (інвертор)", 13, INK, "middle", "bold")
    s += text(gx + 20, gy + 48, "Y = Ā", 14, RED, "middle", "bold")
    s += ttable(gx - 4, gy + 66, ["A", "Y"], [(0, 1), (1, 0)], cw=40, ch=24)
    s += rect(70, 408, W - 140, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 432, "Запам'ятати форму: AND — пряма спинка («Д»), OR — кругла спинка й гострий ніс, NOT — трикутник з кружком.",
              12, INK, "middle", "bold")
    save("fig-15-2-1-symbols.svg", s)


# ── Рис. 15.2.2 — кружок-інверсія: буфер vs інвертор ────────────────────────
def fig152_bubble():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Кружок = інверсія: буфер, інвертор і «бульбашка» на будь-якій ніжці", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "трикутник сам по собі лише ПЕРЕДАЄ сигнал; маленький кружок у точці означає «тут перевернути»",
              12, GREY, "middle", style="italic")
    # буфер
    gx, gy = 160, 170
    s += _pin(gx - 50, gy, gx, gy)
    s += text(gx - 56, gy + 4, "A", 12, INK, "end", "bold")
    s += gate_not(gx, gy, bubble=False)
    s += _pin(gx + 40, gy, gx + 80, gy)
    s += text(gx + 86, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 20, gy - 40, "БУФЕР", 14, INK, "middle", "bold")
    s += text(gx + 20, gy + 46, "Y = A", 13, INK, "middle", "bold")
    s += text(gx + 20, gy + 66, "не змінює логіку —", 11, GREY, "middle", style="italic")
    s += text(gx + 20, gy + 82, "лише підсилює / відновлює (§14.5)", 11, GREY, "middle", style="italic")
    # інвертор
    gx = 480
    s += _pin(gx - 50, gy, gx, gy)
    s += text(gx - 56, gy + 4, "A", 12, INK, "end", "bold")
    s += gate_not(gx, gy, bubble=True)
    s += _pin(gx + 52, gy, gx + 88, gy)
    s += text(gx + 94, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += circle(gx + 46, gy, 6, "#fff", RED, 2.4)
    s += text(gx + 24, gy - 40, "ІНВЕРТОР", 14, INK, "middle", "bold")
    s += text(gx + 24, gy + 46, "Y = Ā", 13, RED, "middle", "bold")
    s += text(gx + 24, gy + 66, "той самий трикутник +", 11, GREY, "middle", style="italic")
    s += text(gx + 24, gy + 82, "кружок-інверсія на виході", 11, GREY, "middle", style="italic")
    # правило
    s += rect(700, 110, 160, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(780, 136, "Правило кружка:", 12.5, INK, "middle", "bold")
    s += text(780, 162, "кружок на ніжці", 11.5, INK, "middle")
    s += text(780, 180, "= інверсія в цій", 11.5, INK, "middle")
    s += text(780, 198, "точці.", 11.5, INK, "middle")
    s += text(780, 224, "Звідси NAND, NOR", 11, GREY, "middle", style="italic")
    s += text(780, 240, "(AND/OR + кружок,", 11, GREY, "middle", style="italic")
    s += text(780, 256, "далі §15.3).", 11, GREY, "middle", style="italic")
    save("fig-15-2-2-bubble.svg", s)


# ── Рис. 15.2.3 — два стандарти символів ────────────────────────────────────
def fig152_iec():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Два стандарти позначень — обидва трапляються в схемах і даташитах", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ліворуч — відмітні форми (ANSI/IEEE, США), праворуч — прямокутні (IEC / ДСТУ, Європа)",
              12, GREY, "middle", style="italic")
    s += text(250, 96, "Відмітні форми", 13.5, INK, "middle", "bold")
    s += text(620, 96, "Прямокутні (IEC)", 13.5, INK, "middle", "bold")
    rows = [
        ("AND", 140, lambda x, y: gate_and(x, y, 44, 38), "&", False),
        ("OR", 220, lambda x, y: gate_or(x, y, 50, 38), "≥1", False),
        ("NOT", 300, lambda x, y: gate_not(x, y, 36, 36), "1", True),
    ]
    for name, yy, gfn, lab, bub in rows:
        s += text(80, yy + 4, name, 13, INK, "start", "bold")
        # відмітна
        s += _pin(150, yy, 190, yy)
        s += gfn(190, yy)
        s += _pin(255, yy, 290, yy) if name != "OR" else _pin(260, yy, 290, yy)
        # IEC
        s += _pin(540, yy, 575, yy)
        s += _iec(575, yy, 60, 50, lab, bub)
        s += _pin(635 + (12 if bub else 0), yy, 680, yy)
    s += rect(70, 332, W - 140, 34, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 354, "У IEC-боксі функцію пише напис: & = AND, ≥1 = OR (≥1 одиниця на вході), 1 з кружком = NOT.",
              12, INK, "middle", "bold")
    save("fig-15-2-3-iec.svg", s)


# ── Рис. 15.2.4 — багатовхідні вентилі ──────────────────────────────────────
def fig152_multi():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Вентилі бувають на багато входів: 2, 3, 4, 8…", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "правило те саме: AND = 1, лише коли ВСІ входи 1; OR = 1, коли ХОЧ ОДИН вхід 1",
              12.5, GREY, "middle", style="italic")
    # 3-вх AND
    gx, gy = 200, 180
    for dy, lab in ((-20, "A"), (0, "B"), (20, "C")):
        s += _pin(gx - 50, gy + dy, gx, gy + dy)
        s += text(gx - 56, gy + dy + 4, lab, 12, INK, "end", "bold")
    s += gate_and(gx, gy, 60, 64)
    s += _pin(gx + 60, gy, gx + 96, gy)
    s += text(gx + 102, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 30, gy - 50, "3-вхідний AND", 13.5, INK, "middle", "bold")
    s += text(gx + 30, gy + 56, "Y = A · B · C", 13.5, RED, "middle", "bold")
    s += text(gx + 30, gy + 78, "1 лише за A=B=C=1", 11, GREY, "middle", style="italic")
    # 3-вх OR
    gx = 600
    for dy, lab in ((-20, "A"), (0, "B"), (20, "C")):
        s += _pin(gx - 50, gy + dy, gx + 6, gy + dy)
        s += text(gx - 56, gy + dy + 4, lab, 12, INK, "end", "bold")
    s += gate_or(gx, gy, 66, 64)
    s += _pin(gx + 66, gy, gx + 100, gy)
    s += text(gx + 106, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 33, gy - 50, "3-вхідний OR", 13.5, INK, "middle", "bold")
    s += text(gx + 33, gy + 56, "Y = A + B + C", 13.5, RED, "middle", "bold")
    s += text(gx + 33, gy + 78, "0 лише за A=B=C=0", 11, GREY, "middle", style="italic")
    s += text(W / 2, 372, "Більше входів — та сама ідея «всі / хоч один». Так одним вентилем перевіряють умову над багатьма сигналами.",
              12, GREY, "middle", style="italic")
    save("fig-15-2-4-multi.svg", s)


# ── Рис. 15.2.5 — з'єднати вентилі у вираз Y = A·B + C ──────────────────────
def fig152_wiring():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Вихід одного — вхід іншого: будуємо Y = A·B + C", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "так із вентилів складають будь-який вираз; простежмо сигнал на прикладі A=1, B=1, C=0",
              12, GREY, "middle", style="italic")
    # AND
    ax, ay = 280, 150
    s += _pin(150, ay - 12, ax, ay - 12)
    s += text(140, ay - 8, "A = 1", 12, RED, "end", "bold")
    s += _pin(150, ay + 12, ax, ay + 12)
    s += text(140, ay + 16, "B = 1", 12, RED, "end", "bold")
    s += gate_and(ax, ay, 50, 44)
    # OR
    ox, oy = 520, 220
    s += _pin(ax + 50, ay, 470, ay)
    s += _pin(470, ay, 470, oy - 12)
    s += _pin(470, oy - 12, ox + 4, oy - 12)
    s += text(420, ay - 8, "P = A·B = 1", 12, GREEN, "middle", "bold")
    s += _pin(150, oy + 12, ox + 4, oy + 12)
    s += text(140, oy + 16, "C = 0", 12, BLUE, "end", "bold")
    s += gate_or(ox, oy, 54, 46)
    s += _pin(ox + 54, oy, ox + 110, oy)
    s += text(ox + 116, oy + 4, "Y = 1", 13, GREEN, "start", "bold")
    s += text(ax + 25, ay - 40, "AND", 12, INK, "middle", "bold")
    s += text(ox + 27, oy - 40, "OR", 12, INK, "middle", "bold")
    # обчислення
    s += rect(70, 300, W - 140, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(90, 326, "Простежмо: A=1, B=1 → AND дає P = 1·1 = 1.  Далі OR: P або C = 1 або 0 = 1.  Отже Y = 1.", 12.5, INK, "start", "bold")
    s += text(90, 350, "Інший вхід: A=1, B=0 → P = 0; тоді Y = 0 або C. Так увесь вираз Y = A·B + C «оживає» в залізі.", 12, INK, "start")
    s += text(90, 374, "Саме так — з'єднуючи виходи зі входами — будують суматори, мультиплексори й усю логіку (§15.6).", 11.5, GREY, "start", style="italic")
    save("fig-15-2-5-wiring.svg", s)


# ═══════════════════ §15.3 — NAND і NOR: універсальні ════════════════════════
def gate_nand(x, y, w=48, h=46, fill="#fafafa", stroke=INK, sw=2):
    return gate_and(x, y, w, h, fill, stroke, sw) + circle(x + w + 6, y, 6, "#fff", stroke, sw)


def gate_nor(x, y, w=54, h=46, fill="#fafafa", stroke=INK, sw=2):
    return gate_or(x, y, w, h, fill, stroke, sw) + circle(x + w + 6, y, 6, "#fff", stroke, sw)


def _ibub(x, y):  # вхідний кружок-інверсія
    return circle(x, y, 5, "#fff", INK, 2)


# ── Рис. 15.3.1 — NAND і NOR: символи й таблиці ─────────────────────────────
def fig153_nand_nor():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "NAND і NOR: «перевернуті» AND та OR (кружок на виході)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "NAND = NOT-AND = ‾(A·B); NOR = NOT-OR = ‾(A+B) — просто інверсія звичних вентилів",
              12, GREY, "middle", style="italic")
    # NAND
    gx, gy = 200, 160
    s += _pin(gx - 48, gy - 12, gx, gy - 12)
    s += text(gx - 54, gy - 8, "A", 12, INK, "end", "bold")
    s += _pin(gx - 48, gy + 12, gx, gy + 12)
    s += text(gx - 54, gy + 16, "B", 12, INK, "end", "bold")
    s += gate_nand(gx, gy)
    s += _pin(gx + 60, gy, gx + 92, gy)
    s += text(gx + 98, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 27, gy - 46, "NAND", 14, INK, "middle", "bold")
    s += text(gx + 27, gy + 50, "Y = ‾(A·B)", 13.5, RED, "middle", "bold")
    s += ttable(gx - 20, gy + 68, ["A", "B", "Y"], [(0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0)], cw=38, ch=24)
    s += text(gx + 27, gy + 220, "0 лише коли ОБИДВА 1", 11, GREY, "middle", style="italic")
    # NOR
    gx = 600
    s += _pin(gx - 48, gy - 12, gx + 4, gy - 12)
    s += text(gx - 54, gy - 8, "A", 12, INK, "end", "bold")
    s += _pin(gx - 48, gy + 12, gx + 4, gy + 12)
    s += text(gx - 54, gy + 16, "B", 12, INK, "end", "bold")
    s += gate_nor(gx, gy)
    s += _pin(gx + 66, gy, gx + 96, gy)
    s += text(gx + 102, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 30, gy - 46, "NOR", 14, INK, "middle", "bold")
    s += text(gx + 30, gy + 50, "Y = ‾(A+B)", 13.5, RED, "middle", "bold")
    s += ttable(gx - 16, gy + 68, ["A", "B", "Y"], [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 0)], cw=38, ch=24)
    s += text(gx + 30, gy + 220, "1 лише коли ОБИДВА 0", 11, GREY, "middle", style="italic")
    save("fig-15-3-1-nand-nor.svg", s)


# ── Рис. 15.3.2 — закони Де Моргана = «штовхання бульбашки» ──────────────────
def fig153_demorgan():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Закони Де Моргана: інверсія перетворює AND ↔ OR", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "‾(A·B) = Ā + B̄  і  ‾(A+B) = Ā · B̄ — тому той самий вентиль можна малювати двома способами",
              12, GREY, "middle", style="italic")
    # рядок 1: NAND = OR з інвертованими входами
    y1 = 150
    s += text(110, y1 - 48, "‾(A·B) = Ā + B̄", 14, INK, "start", "bold")
    s += gate_nand(160, y1, 44, 40)
    s += _pin(120, y1 - 10, 160, y1 - 10)
    s += _pin(120, y1 + 10, 160, y1 + 10)
    s += _pin(210, y1, 240, y1)
    s += text(180, y1 + 40, "NAND", 11, INK, "middle", "bold")
    s += text(285, y1 + 6, "=", 20, GREY, "middle")
    s += gate_or(360, y1, 50, 40)
    s += _ibub(356, y1 - 10)
    s += _ibub(356, y1 + 10)
    s += _pin(316, y1 - 10, 351, y1 - 10)
    s += _pin(316, y1 + 10, 351, y1 + 10)
    s += _pin(410, y1, 440, y1)
    s += text(385, y1 + 40, "OR з інверт. входами", 11, INK, "middle", "bold")
    s += text(560, y1 + 6, "«бульбашку можна", 12, GREY, "start", style="italic")
    s += text(560, y1 + 24, "перекинути» зі входу", 12, GREY, "start", style="italic")
    s += text(560, y1 + 42, "на вихід — і AND стає OR", 12, GREY, "start", style="italic")
    # рядок 2: NOR = AND з інвертованими входами
    y2 = 300
    s += text(110, y2 - 48, "‾(A+B) = Ā · B̄", 14, INK, "start", "bold")
    s += gate_nor(160, y2, 50, 40)
    s += _pin(120, y2 - 10, 164, y2 - 10)
    s += _pin(120, y2 + 10, 164, y2 + 10)
    s += _pin(216, y2, 246, y2)
    s += text(185, y2 + 40, "NOR", 11, INK, "middle", "bold")
    s += text(285, y2 + 6, "=", 20, GREY, "middle")
    s += gate_and(360, y2, 44, 40)
    s += _ibub(356, y2 - 10)
    s += _ibub(356, y2 + 10)
    s += _pin(316, y2 - 10, 351, y2 - 10)
    s += _pin(316, y2 + 10, 351, y2 + 10)
    s += _pin(404, y2, 434, y2)
    s += text(383, y2 + 40, "AND з інверт. входами", 11, INK, "middle", "bold")
    s += text(560, y2, "Це й використовують,", 12, GREY, "start", style="italic")
    s += text(560, y2 + 18, "щоб усе звести до", 12, GREY, "start", style="italic")
    s += text(560, y2 + 36, "ОДНОГО типу вентиля.", 12, GREY, "start", style="italic")
    save("fig-15-3-2-demorgan.svg", s)


# ── Рис. 15.3.3 — будуємо NOT, AND, OR з самих лише NAND ─────────────────────
def fig153_universal():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Усе з одного: NOT, AND, OR — лише з вентилів NAND", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "тому NAND називають УНІВЕРСАЛЬНИМ: маючи його, можна побудувати геть будь-яку логіку",
              12, GREY, "middle", style="italic")
    # NOT = NAND(A,A)
    y = 130
    s += text(80, y + 4, "NOT", 14, INK, "start", "bold")
    s += _pin(150, y, 175, y)
    s += line(175, y, 175, y - 10, INK, 1.8)
    s += line(175, y, 175, y + 10, INK, 1.8)
    s += _pin(175, y - 10, 200, y - 10)
    s += _pin(175, y + 10, 200, y + 10)
    s += text(150, y - 6, "A", 11, INK, "end", "bold")
    s += gate_nand(200, y, 40, 34)
    s += _pin(252, y, 285, y)
    s += text(291, y + 4, "Ā", 12, GREEN, "start", "bold")
    s += text(420, y + 4, "обидва входи NAND з'єднати → NAND(A,A) = ‾(A·A) = Ā", 12.5, INK, "start")
    # AND = NAND + NAND-інвертор
    y = 250
    s += text(80, y + 4, "AND", 14, INK, "start", "bold")
    s += _pin(150, y - 10, 200, y - 10)
    s += _pin(150, y + 10, 200, y + 10)
    s += text(146, y - 6, "A", 11, INK, "end", "bold")
    s += text(146, y + 14, "B", 11, INK, "end", "bold")
    s += gate_nand(200, y, 40, 34)
    s += _pin(252, y, 300, y)
    s += line(300, y, 300, y - 8, INK, 1.8)
    s += line(300, y, 300, y + 8, INK, 1.8)
    s += _pin(300, y - 8, 320, y - 8)
    s += _pin(300, y + 8, 320, y + 8)
    s += gate_nand(320, y, 40, 34)
    s += _pin(372, y, 405, y)
    s += text(411, y + 4, "A·B", 12, GREEN, "start", "bold")
    s += text(470, y + 4, "NAND, тоді ще один NAND як інвертор → ‾(‾(A·B)) = A·B", 12.5, INK, "start")
    # OR = NAND трьох
    y = 380
    s += text(80, y + 4, "OR", 14, INK, "start", "bold")
    s += _pin(150, y - 30, 175, y - 30)
    s += text(146, y - 26, "A", 11, INK, "end", "bold")
    s += line(175, y - 30, 175, y - 40, INK, 1.6)
    s += line(175, y - 30, 175, y - 20, INK, 1.6)
    s += _pin(175, y - 40, 195, y - 40)
    s += _pin(175, y - 20, 195, y - 20)
    s += gate_nand(195, y - 30, 34, 26)
    s += _pin(146, y + 30, 175, y + 30)
    s += text(142, y + 34, "B", 11, INK, "end", "bold")
    s += line(175, y + 30, 175, y + 20, INK, 1.6)
    s += line(175, y + 30, 175, y + 40, INK, 1.6)
    s += _pin(175, y + 20, 195, y + 20)
    s += _pin(175, y + 40, 195, y + 40)
    s += gate_nand(195, y + 30, 34, 26)
    s += _pin(241, y - 30, 300, y - 30)
    s += line(300, y - 30, 300, y - 10, INK, 1.8)
    s += _pin(241, y + 30, 300, y + 30)
    s += line(300, y + 30, 300, y + 10, INK, 1.8)
    s += _pin(300, y - 10, 320, y - 10)
    s += _pin(300, y + 10, 320, y + 10)
    s += gate_nand(320, y, 40, 34)
    s += _pin(372, y, 405, y)
    s += text(411, y + 4, "A+B", 12, GREEN, "start", "bold")
    s += text(470, y + 4, "інвертуємо A і B, тоді NAND → ‾(Ā·B̄) = A+B (Де Морган)", 12.5, INK, "start")
    save("fig-15-3-3-universal.svg", s)


# ── Рис. 15.3.4 — навіщо: один тип комірки + NAND «рідніший» ────────────────
def fig153_why():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо універсальність: одна комірка — і простіше залізо", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "несподіванка: у КМОН «базовий» AND складніший за NAND, бо AND — це NAND + інвертор усередині",
              12, GREY, "middle", style="italic")
    # стовпчики транзисторів
    data = [("NAND", 4, GREEN), ("AND", 6, AMBER), ("NOR", 4, GREEN), ("OR", 6, AMBER)]
    x0 = 130
    base = 300
    for i, (name, ntr, col) in enumerate(data):
        x = x0 + i * 120
        hbar = ntr * 26
        s += rect(x, base - hbar, 70, hbar, "#eef7ee" if col == GREEN else "#fbf6ec", col, 2, 4)
        s += text(x + 35, base - hbar - 10, f"{ntr} тр.", 13, col, "middle", "bold")
        s += text(x + 35, base + 20, name, 13, INK, "middle", "bold")
        if name in ("AND", "OR"):
            s += text(x + 35, base + 38, "= NAND/NOR", 9.5, GREY, "middle", style="italic")
            s += text(x + 35, base + 52, "+ інвертор", 9.5, GREY, "middle", style="italic")
    s += text(x0 + 35, base - 4 * 26 - 30, "менше!", 11, GREEN, "middle", "bold")
    s += rect(640, 110, 200, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(740, 138, "Чому це перемога:", 12.5, INK, "middle", "bold")
    for i, t in enumerate(["• завод вилизує ОДНУ", "  комірку — і робить її", "  дешевою й надійною",
                           "• NAND/NOR швидші й", "  менші за AND/OR",
                           "• цілі чипи будують", "  з одного типу вентиля"]):
        s += text(656, 164 + i * 21, t, 11.5, INK, "start")
    s += text(W / 2, 350, "Тому в кремнії NAND і NOR — не «екзотика», а РІДНІ, базові вентилі; AND та OR — похідні від них (§15.5).",
              12, INK, "middle", "bold")
    save("fig-15-3-4-why.svg", s)


# ── Рис. 15.3.5 — NOR теж універсальний: подвійність і «Аполлон» ────────────
def fig153_nor_apollo():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "NOR — теж універсальний; з нього був зроблений комп'ютер «Аполлона»", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "NAND-світ і NOR-світ — дзеркальні (двоїстість Де Моргана); будь-який із них самодостатній",
              12, GREY, "middle", style="italic")
    # NOR будує NOT/OR/AND (стисло)
    s += rect(60, 86, 360, 230, "none", INK, 1.6, 10)
    s += text(240, 112, "Самих NOR досить на все:", 13, INK, "middle", "bold")
    items = [("NOT  A", "NOR(A,A) = ‾A"),
             ("OR  A+B", "NOR, тоді NOR-інвертор"),
             ("AND  A·B", "інвертувати A,B, тоді NOR")]
    for i, (a, b) in enumerate(items):
        yy = 150 + i * 44
        s += text(84, yy, a, 13, RED, "start", "bold")
        s += text(200, yy, "←  " + b, 12, INK, "start")
    s += text(240, 300, "(дзеркало того, що NAND робить через AND)", 11, GREY, "middle", style="italic")
    # Аполлон
    s += rect(450, 86, 360, 230, "#f4f7f4", GREEN, 1.6, 10)
    s += text(630, 112, "📜 Бортовий комп'ютер «Аполлона»", 12.5, INK, "middle", "bold")
    s += text(630, 138, "(AGC, 1960-ті)", 11, GREY, "middle", style="italic")
    for i, t in enumerate([
        "Логіку, що повела людину",
        "на Місяць, зібрали майже",
        "цілком з ОДНОГО типу —",
        "3-вхідного NOR (Block II:",
        "≈ 2800 чипів × 2 ≈ 5600).",
        "Менше типів деталей —",
        "максимальна надійність."]):
        s += text(472, 166 + i * 20, t, 11.5, INK, "start")
    save("fig-15-3-5-nor-apollo.svg", s)


# ═══════════════════ §15.4 — XOR і логіка порівняння ═════════════════════════
def gate_xor(x, y, w=54, h=46, fill="#fafafa", stroke=INK, sw=2):
    out = gate_or(x, y, w, h, fill, stroke, sw)
    r = h / 2
    out += (f'<path d="M {x-7},{y-r} Q {x-7+w*0.28},{y} {x-7},{y+r}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}"/>\n')
    return out


def gate_xnor(x, y, w=54, h=46, fill="#fafafa", stroke=INK, sw=2):
    return gate_xor(x, y, w, h, fill, stroke, sw) + circle(x + w + 6, y, 6, "#fff", stroke, sw)


# ── Рис. 15.4.1 — XOR і XNOR: символи й таблиці ─────────────────────────────
def fig154_xor_xnor():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "XOR («виключне або») і XNOR: різниця проти рівності", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "XOR = 1, коли входи РІЗНІ; XNOR = 1, коли входи ОДНАКОВІ — це й є логіка порівняння",
              12, GREY, "middle", style="italic")
    # XOR
    gx, gy = 200, 160
    s += _pin(gx - 50, gy - 12, gx, gy - 12)
    s += text(gx - 56, gy - 8, "A", 12, INK, "end", "bold")
    s += _pin(gx - 50, gy + 12, gx, gy + 12)
    s += text(gx - 56, gy + 16, "B", 12, INK, "end", "bold")
    s += gate_xor(gx, gy)
    s += _pin(gx + 54, gy, gx + 90, gy)
    s += text(gx + 96, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 27, gy - 46, "XOR", 14, INK, "middle", "bold")
    s += text(gx + 27, gy + 50, "Y = A ⊕ B", 13.5, RED, "middle", "bold")
    s += ttable(gx - 13, gy + 68, ["A", "B", "Y"], [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)], cw=38, ch=24)
    s += text(gx + 27, gy + 222, "1 ⇔ входи РІЗНІ", 11.5, GREY, "middle", style="italic")
    # XNOR
    gx = 600
    s += _pin(gx - 50, gy - 12, gx, gy - 12)
    s += text(gx - 56, gy - 8, "A", 12, INK, "end", "bold")
    s += _pin(gx - 50, gy + 12, gx, gy + 12)
    s += text(gx - 56, gy + 16, "B", 12, INK, "end", "bold")
    s += gate_xnor(gx, gy)
    s += _pin(gx + 66, gy, gx + 96, gy)
    s += text(gx + 102, gy + 4, "Y", 12, GREEN, "start", "bold")
    s += text(gx + 30, gy - 46, "XNOR", 14, INK, "middle", "bold")
    s += text(gx + 30, gy + 50, "Y = ‾(A ⊕ B)", 13, RED, "middle", "bold")
    s += ttable(gx - 10, gy + 68, ["A", "B", "Y"], [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)], cw=38, ch=24)
    s += text(gx + 30, gy + 222, "1 ⇔ входи РІВНІ", 11.5, GREY, "middle", style="italic")
    save("fig-15-4-1-xor-xnor.svg", s)


# ── Рис. 15.4.2 — XOR із базових вентилів (SOP) ─────────────────────────────
def fig154_from_gates():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "XOR — це сума добутків: A⊕B = Ā·B + A·B̄", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама функція «рівно один із двох», яку ми вивели сумою добутків у §15.1 — тепер вентилями",
              12, GREY, "middle", style="italic")
    # інвертори
    s += _pin(90, 130, 120, 130)
    s += text(84, 134, "A", 12, INK, "end", "bold")
    s += gate_not(120, 130, 30, 26)
    s += _pin(162, 130, 200, 130)
    s += text(176, 122, "Ā", 10, GREY, "middle")
    s += _pin(90, 270, 120, 270)
    s += text(84, 274, "B", 12, INK, "end", "bold")
    s += gate_not(120, 270, 30, 26)
    s += _pin(162, 270, 200, 270)
    s += text(176, 262, "B̄", 10, GREY, "middle")
    # розгалуження A і B напряму
    s += circle(105, 130, 3, INK, INK, 1)
    s += line(105, 130, 105, 200, INK, 1.6)
    s += line(105, 200, 200, 200, INK, 1.6)
    s += circle(105, 270, 3, INK, INK, 1)
    s += line(105, 270, 105, 230, INK, 1.6)
    s += line(105, 230, 200, 230, INK, 1.6)
    # AND1: Ā·B
    s += _pin(200, 130, 240, 130)
    s += _pin(200, 230, 240, 230)
    s += line(240, 130, 240, 168, INK, 1.6)
    s += line(240, 230, 240, 192, INK, 1.6)
    s += _pin(240, 168, 250, 168)
    s += _pin(240, 192, 250, 192)
    s += gate_and(250, 180, 44, 40)
    s += text(272, 150, "Ā·B", 11, INK, "middle", "bold")
    s += _pin(300, 180, 360, 180)
    # AND2: A·B̄
    s += _pin(200, 200, 240, 200)
    s += _pin(200, 270, 240, 270)
    s += line(240, 200, 240, 228, INK, 1.6)
    s += line(240, 270, 240, 252, INK, 1.6)
    s += _pin(240, 228, 250, 228)
    s += _pin(240, 252, 250, 252)
    s += gate_and(250, 240, 44, 40)
    s += text(272, 300, "A·B̄", 11, INK, "middle", "bold")
    s += _pin(300, 240, 360, 240)
    # OR
    s += line(360, 180, 360, 198, INK, 1.6)
    s += line(360, 240, 360, 222, INK, 1.6)
    s += _pin(360, 198, 376, 198)
    s += _pin(360, 222, 376, 222)
    s += gate_or(376, 210, 50, 44)
    s += _pin(426, 210, 470, 210)
    s += text(476, 214, "Y = A⊕B", 13, GREEN, "start", "bold")
    # еквівалент
    s += text(640, 150, "= один вентиль", 13, INK, "middle", "bold")
    s += _pin(560, 210, 600, 210)
    s += _pin(560, 186, 600, 186)
    s += gate_xor(600, 198, 50, 40)
    s += _pin(656, 198, 700, 198)
    s += text(706, 202, "XOR", 12, GREEN, "start", "bold")
    s += text(640, 250, "XOR — це «згорнутий» у один", 11, GREY, "middle", style="italic")
    s += text(640, 266, "елемент типовий блок із 5 вентилів", 11, GREY, "middle", style="italic")
    save("fig-15-4-2-from-gates.svg", s)


# ── Рис. 15.4.3 — порівняння на рівність (XNOR) ─────────────────────────────
def fig154_compare():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Логіка порівняння: чи рівні два числа? — XNOR кожного біта + AND", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "XNOR каже «біти рівні»; щоб числа були рівні, мусять збігтися ВСІ біти — тому виходи через AND",
              12, GREY, "middle", style="italic")
    bits = [(1, 1), (0, 0), (1, 1), (0, 1)]
    y0 = 110
    for i, (a, b) in enumerate(bits):
        yy = y0 + i * 64
        s += text(110, yy - 6, f"A{3-i}={a}", 12, (RED if a else BLUE), "end", "bold")
        s += text(110, yy + 14, f"B{3-i}={b}", 12, (RED if b else BLUE), "end", "bold")
        s += _pin(116, yy - 8, 150, yy - 8)
        s += _pin(116, yy + 8, 150, yy + 8)
        s += gate_xnor(150, yy, 44, 38)
        eq = 1 if a == b else 0
        s += _pin(206, yy, 250, yy)
        s += text(214, yy - 6, "рівні" if eq else "РІЗНІ", 10.5, (GREEN if eq else RED), "start", "bold")
        s += text(214, yy + 10, f"= {eq}", 10.5, (GREEN if eq else RED), "start", "bold")
        s += line(250, yy, 300, yy, INK, 1.6)
        s += line(300, yy, 300, 210, INK, 1.6) if i != 1 else line(300, yy, 300, 210, INK, 1.6)
    # 4-вх AND
    s += gate_and(330, 210, 56, 120)
    for i in range(4):
        yy = y0 + i * 64
        s += line(300, yy, 330, yy, INK, 1.6)
    s += _pin(386, 210, 440, 210)
    s += text(446, 214, "A == B ?", 13, INK, "start", "bold")
    s += text(446, 234, "тут = 0 (бо біт 0 різний)", 11, RED, "start", "bold")
    s += rect(560, 120, 290, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(705, 146, "Як читати:", 12.5, INK, "middle", "bold")
    for i, t in enumerate([
        "• кожен XNOR порівнює пару бітів",
        "• 1 = «ця пара рівна»",
        "• AND з усіх: 1 лише якщо",
        "  ВСІ пари рівні → числа рівні",
        "• тут біт 0 різниться (0≠1),",
        "  тож AND дає 0: числа НЕ рівні"]):
        s += text(576, 174 + i * 23, t, 11.5, INK, "start")
    save("fig-15-4-3-compare.svg", s)


# ── Рис. 15.4.4 — парність (XOR-ланцюг) ─────────────────────────────────────
def fig154_parity():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Парність: XOR багатьох бітів = 1, якщо кількість одиниць НЕПАРНА", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "XOR-ланцюг рахує одиниці «по модулю 2»; так роблять контрольний біт парності для виявлення помилок",
              12, GREY, "middle", style="italic")
    byte = [1, 0, 1, 1, 0, 0, 1, 1]
    x0 = 110
    yb = 110
    for i, b in enumerate(byte):
        x = x0 + i * 88
        s += rect(x, yb, 36, 32, "#fdf4f4" if b else "#f3f5fd", RED if b else BLUE, 1.6, 4)
        s += text(x + 18, yb + 22, str(b), 14, RED if b else BLUE, "middle", "bold")
    s += text(x0 + 8 * 88 + 4, yb + 22, "← байт", 12, GREY, "start")
    # XOR-ланцюг
    acc = 0
    yx = 230
    for i, b in enumerate(byte):
        x = x0 + i * 88
        s += line(x + 18, yb + 32, x + 18, yx - 20, GREY, 1.2)
        if i == 0:
            acc = b
            s += circle(x + 18, yx, 4, INK, INK, 1)
            s += text(x + 18, yx + 22, str(acc), 12, INK, "middle", "bold")
            continue
        gx = x - 26
        s += gate_xor(gx, yx, 38, 30)
        s += _pin(gx - 18, yx - 7, gx, yx - 7)
        s += _pin(gx - 18, yx + 7, gx, yx + 7)
        s += _pin(gx + 38 + 6, yx, gx + 70, yx)
        acc ^= b
        s += text(gx + 58, yx - 8, str(acc), 11.5, GREEN if i == 7 else INK, "middle", "bold")
    s += text(x0 + 7 * 88 + 60, yx + 24, "= біт парності", 12, GREEN, "start", "bold")
    s += rect(70, 300, W - 140, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 324, "У байті 10110011 одиниць п'ять (НЕПАРНО) → біт парності = 1.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 344, "Якщо при передачі один біт «перевернеться», парність зміниться — і помилку видно (§35).", 12, GREY, "middle", style="italic")
    save("fig-15-4-4-parity.svg", s)


# ── Рис. 15.4.5 — XOR як керований інвертор і детектор різниці ──────────────
def fig154_controlled():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "XOR як керований інвертор і «детектор різниці»", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "якщо один вхід — керування: B=0 пропускає A, B=1 інвертує A; а ще XOR — основа суматора (§15.6)",
              12, GREY, "middle", style="italic")

    def state(x0, bval, out_lbl, note):
        nonlocal s
        cy = 170
        s += _pin(x0, cy - 10, x0 + 40, cy - 10)
        s += text(x0 - 6, cy - 6, "A", 12, INK, "end", "bold")
        s += _pin(x0, cy + 10, x0 + 40, cy + 10)
        s += text(x0 - 6, cy + 14, f"B={bval}", 12, (RED if bval else BLUE), "end", "bold")
        s += gate_xor(x0 + 40, cy, 46, 40)
        s += _pin(x0 + 92, cy, x0 + 130, cy)
        s += text(x0 + 136, cy + 4, out_lbl, 13, GREEN, "start", "bold")
        s += text(x0 + 60, cy - 36, note, 11.5, INK, "middle", "bold")
        return

    state(120, 0, "Y = A", "B=0: пропускає")
    state(420, 1, "Y = Ā", "B=1: інвертує")
    # півсуматор-натяк
    s += rect(680, 110, 170, 180, "#f4f7f4", GREEN, 1.6, 10)
    s += text(765, 136, "Натяк наперед:", 12, INK, "middle", "bold")
    s += text(765, 158, "A ⊕ B = біт СУМИ", 12, RED, "middle", "bold")
    s += text(765, 178, "A · B = біт ПЕРЕНОСУ", 11.5, INK, "middle", "bold")
    s += text(765, 204, "разом — це додавання", 11, GREY, "middle", style="italic")
    s += text(765, 220, "двох бітів", 11, GREY, "middle", style="italic")
    s += text(765, 246, "(півсуматор —", 11, GREY, "middle", style="italic")
    s += text(765, 262, "будуємо в §15.6)", 11, GREY, "middle", style="italic")
    s += text(330, 320, "XOR «спрацьовує на різницю» — тому він і порівнює, і рахує парність, і додає.", 12, INK, "middle", "bold")
    save("fig-15-4-5-controlled.svg", s)


# ═══════════════════ §15.5 — Як з транзисторів роблять вентиль ═══════════════
def fet(x, y, kind, on=None, w=34, h=30):
    """МОН-транзистор як коробочка. Затвор зліва (у P — з кружком),
    верхній і нижній виводи — зверху/знизу. on=True/False підсвічує стан."""
    if on is True:
        col, bg = GREEN, "#eafaef"
    elif on is False:
        col, bg = GREY, "#f1f1f1"
    else:
        col = BLUE if kind == "n" else RED
        bg = "#f3f5fd" if kind == "n" else "#fdf4f4"
    out = rect(x - w / 2, y - h / 2, w, h, bg, col, 1.8, 4)
    out += text(x, y + 5, "N" if kind == "n" else "P", 12, col, "middle", "bold")
    if kind == "p":
        out += circle(x - w / 2 - 5, y, 4.5, "#fff", col, 1.6)
        out += line(x - w / 2 - 9.5, y, x - w / 2 - 24, y, col, 1.6)
    else:
        out += line(x - w / 2, y, x - w / 2 - 24, y, col, 1.6)
    return out


# ── Рис. 15.5.1 — МОН-транзистор як ключ (N і P — взаємодоповнення) ─────────
def fig155_switch():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "МОН-транзистор як ключ: N і P відкриваються протилежними рівнями", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "усе CMOS стоїть на цій взаємодоповняльності (з §12): один провідний — другий замкнений",
              12, GREY, "middle", style="italic")

    def panel(ox, kind, title):
        nonlocal s
        s += rect(ox, 86, 360, 250, "none", FAINT, 1.5, 10)
        s += text(ox + 180, 110, title, 14, INK, "middle", "bold")
        # затвор = 0
        s += fet(ox + 90, 200, kind, on=(kind == "p"))
        s += text(ox + 90, 150, "затвор = 0", 11.5, INK, "middle", "bold")
        s += text(ox + 90, 250, "відкритий" if kind == "p" else "замкнений",
                  11.5, (GREEN if kind == "p" else GREY), "middle", "bold")
        # затвор = 1
        s += fet(ox + 250, 200, kind, on=(kind == "n"))
        s += text(ox + 250, 150, "затвор = 1", 11.5, INK, "middle", "bold")
        s += text(ox + 250, 250, "відкритий" if kind == "n" else "замкнений",
                  11.5, (GREEN if kind == "n" else GREY), "middle", "bold")
        s += text(ox + 180, 300, "(зелений = проводить струм)", 10.5, GREY, "middle", style="italic")
        return

    panel(40, "n", "NMOS: відкривається ЛОГІЧНОЮ 1")
    panel(460, "p", "PMOS: відкривається ЛОГІЧНИМ 0")
    save("fig-15-5-1-switch.svg", s)


# ── Рис. 15.5.2 — принцип CMOS: підтяжка + стягування ───────────────────────
def fig155_principle():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Принцип CMOS: дві взаємодоповняльні мережі на один вихід", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "верхня (PMOS) тягне вихід до Vdd, нижня (NMOS) — до GND; за будь-якого входу провідна РІВНО одна",
              12, GREY, "middle", style="italic")
    cx = 410
    s += line(160, 100, 660, 100, RED, 2.5)
    s += text(140, 104, "Vdd", 12, RED, "end", "bold")
    s += line(160, 360, 660, 360, BLUE, 2.5)
    s += text(140, 364, "GND", 12, BLUE, "end", "bold")
    # PMOS-мережа
    s += rect(cx - 90, 130, 180, 70, "#fdf4f4", RED, 2, 8)
    s += text(cx, 162, "мережа PMOS", 13, RED, "middle", "bold")
    s += text(cx, 182, "(підтяжка до Vdd)", 11, GREY, "middle")
    s += line(cx, 100, cx, 130, INK, 2)
    # вихід
    s += line(cx, 200, cx, 290, INK, 2)
    s += circle(cx, 245, 4, INK, INK, 1)
    s += line(cx, 245, cx + 150, 245, INK, 2)
    s += text(cx + 156, 249, "вихід", 12.5, GREEN, "start", "bold")
    # NMOS-мережа
    s += rect(cx - 90, 290, 180, 70, "#f3f5fd", BLUE, 2, 8)
    s += text(cx, 322, "мережа NMOS", 13, BLUE, "middle", "bold")
    s += text(cx, 342, "(стягування до GND)", 11, GREY, "middle")
    # входи
    s += arrow(170, 245, cx - 90, 165, INK, 1.6, "4 3")
    s += arrow(170, 245, cx - 90, 325, INK, 1.6, "4 3")
    s += text(150, 249, "входи", 11.5, INK, "end", "bold")
    s += rect(660, 150, 150, 170, "#f4f7f4", GREEN, 1.6, 10)
    s += text(735, 176, "Завжди або-або:", 12, INK, "middle", "bold")
    for i, t in enumerate(["вихід=1: верхня", "  провідна, нижня ні", "вихід=0: навпаки",
                           "→ вихід завжди", "  твердий 0 чи 1", "→ крізь нема струму"]):
        s += text(675, 202 + i * 20, t, 11, INK, "start")
    save("fig-15-5-2-principle.svg", s)


# ── Рис. 15.5.3 — CMOS-інвертор (NOT) у двох станах ─────────────────────────
def fig155_inverter():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Найпростіший вентиль: CMOS-інвертор (NOT) — 2 транзистори", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "PMOS згори (до Vdd), NMOS знизу (до GND), затвори разом на вхід — і вихід завжди протилежний",
              12, GREY, "middle", style="italic")

    def inv(ox, a):
        nonlocal s
        vdd, gnd = 110, 330
        pon = (a == 0)
        non = (a == 1)
        s += line(ox - 70, vdd, ox + 70, vdd, RED, 2.2)
        s += text(ox - 76, vdd + 4, "Vdd", 10.5, RED, "end", "bold")
        s += line(ox - 70, gnd, ox + 70, gnd, BLUE, 2.2)
        s += text(ox - 76, gnd + 4, "GND", 10.5, BLUE, "end", "bold")
        # PMOS
        s += fet(ox, 165, "p", on=pon)
        s += line(ox, vdd, ox, 150, INK, 2)
        # NMOS
        s += fet(ox, 275, "n", on=non)
        s += line(ox, gnd, ox, 290, INK, 2)
        # вихід між ними
        s += line(ox, 180, ox, 260, INK, 2)
        s += circle(ox, 220, 3.5, INK, INK, 1)
        s += line(ox, 220, ox + 70, 220, INK, 2)
        outv = 1 - a
        s += text(ox + 76, 224, f"Y={outv}", 12.5, GREEN, "start", "bold")
        # вхід на затвори
        s += line(ox - 58, 165, ox - 58, 275, INK, 1.6)
        s += line(ox - 58, 165, ox - 41, 165, INK, 1.6)
        s += line(ox - 58, 275, ox - 41, 275, INK, 1.6)
        s += line(ox - 90, 220, ox - 58, 220, INK, 1.6)
        s += text(ox - 96, 224, f"A={a}", 12.5, (RED if a else BLUE), "end", "bold")
        s += text(ox, 90, f"вхід A = {a}", 12.5, INK, "middle", "bold")
        # підсвічений шлях
        if pon:
            s += text(ox, 360, "PMOS відкритий → Vdd → Y=1", 11, GREEN, "middle", "bold")
        else:
            s += text(ox, 360, "NMOS відкритий → GND → Y=0", 11, GREEN, "middle", "bold")
        return

    inv(250, 0)
    inv(630, 1)
    s += text(W / 2, 400, "Жоден стан не з'єднує Vdd із GND наскрізь — тому в спокої струм майже нульовий (§14.4).",
              12, INK, "middle", "bold")
    save("fig-15-5-3-inverter.svg", s)


# ── Рис. 15.5.4 — CMOS NAND і NOR: послідовно ↔ паралельно ──────────────────
def fig155_nand_nor():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "CMOS NAND і NOR: послідовно ↔ паралельно (двоїстість)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "по 4 транзистори; мережі завжди дзеркальні: де NMOS послідовно — там PMOS паралельно",
              12, GREY, "middle", style="italic")

    def schem(ox, title, pmos_par, sub):
        nonlocal s
        vdd, gnd = 110, 370
        s += text(ox, 90, title, 14, INK, "middle", "bold")
        s += line(ox - 80, vdd, ox + 80, vdd, RED, 2.2)
        s += text(ox - 86, vdd + 4, "Vdd", 10, RED, "end", "bold")
        s += line(ox - 80, gnd, ox + 80, gnd, BLUE, 2.2)
        s += text(ox - 86, gnd + 4, "GND", 10, BLUE, "end", "bold")
        outy = 240
        if pmos_par:  # NAND: PMOS паралельно, NMOS послідовно
            s += fet(ox - 30, 150, "p")
            s += fet(ox + 30, 150, "p")
            s += line(ox - 30, vdd, ox - 30, 135, INK, 1.8)
            s += line(ox + 30, vdd, ox + 30, 135, INK, 1.8)
            s += line(ox - 30, 165, ox - 30, outy, INK, 1.8)
            s += line(ox + 30, 165, ox + 30, outy, INK, 1.8)
            s += line(ox - 30, outy, ox + 30, outy, INK, 1.8)
            s += fet(ox, 290, "n")
            s += fet(ox, 340, "n")
            s += line(ox, outy, ox, 275, INK, 1.8)
            s += line(ox, 305, ox, 325, INK, 1.8)
            s += line(ox, 355, ox, gnd, INK, 1.8)
        else:  # NOR: PMOS послідовно, NMOS паралельно
            s += fet(ox, 150, "p")
            s += fet(ox, 200, "p")
            s += line(ox, vdd, ox, 135, INK, 1.8)
            s += line(ox, 165, ox, 185, INK, 1.8)
            s += line(ox, 215, ox, outy, INK, 1.8)
            s += fet(ox - 30, 300, "n")
            s += fet(ox + 30, 300, "n")
            s += line(ox - 30, outy, ox - 30, 285, INK, 1.8)
            s += line(ox + 30, outy, ox + 30, 285, INK, 1.8)
            s += line(ox - 30, outy, ox + 30, outy, INK, 1.8)
            s += line(ox - 30, 315, ox - 30, gnd, INK, 1.8)
            s += line(ox + 30, 315, ox + 30, gnd, INK, 1.8)
        s += circle(ox, outy, 3.5, INK, INK, 1)
        s += line(ox, outy, ox + 100, outy, INK, 2)
        s += text(ox + 106, outy + 4, "Y", 12, GREEN, "start", "bold")
        s += text(ox, 410, sub, 11.5, INK, "middle", "bold")
        s += text(ox, 430, "4 транзистори", 11, GREEN, "middle", "bold")
        return

    schem(240, "NAND", True, "PMOS ‖ паралельно, NMOS — послідовно")
    schem(640, "NOR", False, "PMOS — послідовно, NMOS ‖ паралельно")
    save("fig-15-5-4-nand-nor.svg", s)


# ── Рис. 15.5.5 — чому CMOS виграв + чому AND дорожчий за NAND ──────────────
def fig155_why():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому переміг CMOS — і чому «простий» AND дорожчий за NAND", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у спокої одна мережа завжди замкнена → наскрізного струму нема → майже нуль статичної потужності",
              12, GREY, "middle", style="italic")
    # ліворуч — енергія
    s += rect(60, 84, 360, 250, "none", GREEN, 1.6, 10)
    s += text(240, 110, "Сила CMOS", 14, GREEN, "middle", "bold")
    for i, t in enumerate([
        "• у спокої Vdd і GND НЕ з'єднані",
        "  наскрізь → струм ≈ 0",
        "• енергія тратиться лише при",
        "  ПЕРЕМИКАННІ (заряд ємностей)",
        "• звідси P ≈ C·V²·f (з §14.4):",
        "  менше V і f — менше тепла",
        "• вихід — «до шин» (≈0 / ≈Vdd):",
        "  чудові рівні й запас (§14.3/14.4)"]):
        s += text(76, 138 + i * 24, t, 11.5, INK, "start")
    # праворуч — рахунок транзисторів (замикаємо §15.3)
    s += rect(440, 84, 380, 250, "none", AMBER, 1.6, 10)
    s += text(630, 110, "Чому NAND/NOR — рідні", 14, "#9a7322", "middle", "bold")
    rows = [("інвертор (NOT)", "2"), ("NAND / NOR", "4"),
            ("AND = NAND + інвертор", "4+2 = 6"), ("OR = NOR + інвертор", "4+2 = 6")]
    for i, (name, n) in enumerate(rows):
        yy = 150 + i * 38
        s += text(460, yy, name, 12.5, INK, "start", "bold")
        s += text(800, yy, n + " тр.", 12.5, (GREEN if n in ("2", "4") else "#9a7322"), "end", "bold")
        s += line(460, yy + 10, 800, yy + 10, FAINT, 1)
    s += text(630, 320, "тому AND/OR будують ЧЕРЕЗ NAND/NOR — замикається §15.3", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 372, "Низька потужність + малі прості комірки — ось чому майже вся логіка сьогодні саме CMOS.",
              12.5, INK, "middle", "bold")
    save("fig-15-5-5-why.svg", s)


# ═══════════════════ §15.6 — Комбінаційні схеми ══════════════════════════════
def _box(x, y, w, h, label, sub=None, fill="#eef4ff"):
    out = rect(x, y, w, h, fill, INK, 2, 8)
    out += text(x + w / 2, y + h / 2 + 4, label, 13, INK, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + h / 2 + 20, sub, 10, GREY, "middle")
    return out


# ── Рис. 15.6.1 — що таке комбінаційна схема ────────────────────────────────
def fig156_combinational():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Комбінаційна схема: вихід залежить ЛИШЕ від входів зараз", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "немає пам'яті, немає зворотного зв'язку, немає такту — чиста функція входів (на відміну від Розділу 16)",
              12, GREY, "middle", style="italic")
    # комбінаційна
    s += rect(120, 110, 250, 150, "#eef4ff", INK, 2, 12)
    s += text(245, 175, "комбінаційна", 15, INK, "middle", "bold")
    s += text(245, 197, "(вентилі без петель)", 11, GREY, "middle")
    for i, lab in enumerate(["A", "B", "C"]):
        yy = 140 + i * 40
        s += _pin(70, yy, 120, yy)
        s += text(64, yy + 4, lab, 12, INK, "end", "bold")
    s += _pin(370, 185, 420, 185)
    s += text(426, 189, "Y = f(A,B,C)", 12.5, GREEN, "start", "bold")
    s += text(245, 282, "ті самі входи → завжди той самий вихід", 11.5, GREEN, "middle", "bold")
    # послідовнісна (тизер)
    s += rect(560, 110, 230, 150, "#f4f4f4", GREY, 1.6, 12)
    s += text(675, 170, "послідовнісна", 14, GREY, "middle", "bold")
    s += text(675, 190, "(з пам'яттю)", 11, GREY, "middle")
    s += f'<path d="M 600,235 q 75,40 150,0" fill="none" stroke="{GREY}" stroke-width="2" marker-end="url(#aInk)" stroke-dasharray="5 4"/>\n'
    s += text(675, 252, "зворотний зв'язок + такт", 10.5, GREY, "middle", style="italic")
    s += text(675, 282, "→ Розділ 16", 12, GREY, "middle", "bold")
    save("fig-15-6-1-combinational.svg", s)


# ── Рис. 15.6.2 — півсуматор ────────────────────────────────────────────────
def fig156_half_adder():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Півсуматор: додає два біти → сума й перенос", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "сума = A⊕B (XOR), перенос = A·B (AND) — рівно те, що ми передбачили в §15.4",
              12, GREY, "middle", style="italic")
    # входи
    s += text(110, 150, "A", 13, INK, "end", "bold")
    s += text(110, 250, "B", 13, INK, "end", "bold")
    s += circle(140, 150, 3, INK, INK, 1)
    s += circle(140, 250, 3, INK, INK, 1)
    s += line(120, 150, 250, 150, INK, 1.6)
    s += line(120, 250, 250, 250, INK, 1.6)
    s += line(140, 150, 140, 200, INK, 1.6)
    s += line(140, 250, 140, 220, INK, 1.6)
    # XOR → Sum
    s += line(250, 150, 250, 175, INK, 1.6)
    s += line(140, 200, 250, 200, INK, 1.6)
    s += _pin(250, 175, 264, 175)
    s += _pin(250, 200, 264, 200)
    s += gate_xor(264, 188, 50, 40)
    s += _pin(320, 188, 380, 188)
    s += text(386, 192, "Sum = A⊕B", 12.5, GREEN, "start", "bold")
    # AND → Carry
    s += line(140, 220, 250, 220, INK, 1.6)
    s += line(250, 250, 250, 245, INK, 1.6)
    s += _pin(250, 220, 264, 220)
    s += _pin(250, 245, 264, 245)
    s += gate_and(264, 232, 44, 36)
    s += _pin(314, 232, 380, 232)
    s += text(386, 236, "Carry = A·B", 12.5, GREEN, "start", "bold")
    # таблиця
    s += ttable(560, 110, ["A", "B", "Carry", "Sum"],
                [(0, 0, 0, 0), (0, 1, 0, 1), (1, 0, 0, 1), (1, 1, 1, 0)], cw=58, ch=28, out_cols=(2, 3))
    s += text(560 + 116, 110 + 28 * 5 + 20, "1+1 = 10 (двійкове 2)", 11.5, GREY, "middle", style="italic")
    save("fig-15-6-2-half-adder.svg", s)


# ── Рис. 15.6.3 — повний суматор ────────────────────────────────────────────
def fig156_full_adder():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 34, "Повний суматор: додає ТРИ біти (A, B і перенос-вхід)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "складають із двох півсуматорів + OR; Sum = A⊕B⊕Cin, Cout = більшість (A,B,Cin)",
              12, GREY, "middle", style="italic")
    # HA1
    s += text(95, 150, "A", 12, INK, "end", "bold")
    s += text(95, 180, "B", 12, INK, "end", "bold")
    s += _pin(100, 150, 140, 150)
    s += _pin(100, 180, 140, 180)
    s += _box(140, 135, 90, 60, "HA 1", None, "#eef4ff")
    s += _pin(230, 150, 290, 150)
    s += text(258, 142, "s1", 10, GREY, "middle")
    s += _pin(230, 180, 270, 180)
    s += line(270, 180, 270, 300, INK, 1.6)
    s += text(282, 184, "c1", 10, GREY, "middle")
    # HA2
    s += text(95, 240, "Cin", 12, INK, "end", "bold")
    s += _pin(100, 240, 290, 240)
    s += _box(290, 135, 90, 60, "HA 2", None, "#eef4ff")
    s += line(290, 240, 290, 195, INK, 1.6) if False else ""
    s += _pin(380, 150, 460, 150)
    s += text(470, 154, "Sum = A⊕B⊕Cin", 12.5, GREEN, "start", "bold")
    s += _pin(380, 180, 420, 180)
    s += line(420, 180, 420, 290, INK, 1.6)
    s += text(432, 184, "c2", 10, GREY, "middle")
    # вхід Cin до HA2 другим входом
    s += line(290, 240, 285, 240, INK, 1.6)
    s += text(248, 232, "Cin →", 9.5, GREY, "middle")
    # OR переносів
    s += _pin(270, 300, 320, 295)
    s += _pin(420, 290, 320, 305)
    s += gate_or(320, 300, 50, 40)
    s += _pin(376, 300, 460, 300)
    s += text(470, 304, "Cout = c1 + c2", 12.5, GREEN, "start", "bold")
    # таблиця
    s += ttable(560, 100, ["A", "B", "Ci", "Co", "S"],
                [(0, 0, 0, 0, 0), (0, 0, 1, 0, 1), (0, 1, 0, 0, 1), (0, 1, 1, 1, 0),
                 (1, 0, 0, 0, 1), (1, 0, 1, 1, 0), (1, 1, 0, 1, 0), (1, 1, 1, 1, 1)],
                cw=44, ch=26, out_cols=(3, 4))
    save("fig-15-6-3-full-adder.svg", s)


# ── Рис. 15.6.4 — ланцюговий суматор (ripple-carry) ─────────────────────────
def fig156_ripple():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Багатобітне додавання: ланцюг повних суматорів (перенос біжить)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перенос кожного розряду йде у наступний — як додавання стовпчиком; приклад 0110 + 1011 = 10001",
              12, GREY, "middle", style="italic")
    A = [0, 1, 1, 0]   # A0..A3  → число 0110 = 6
    B = [1, 1, 0, 1]   # B0..B3  → число 1011 = 11
    S = [1, 0, 0, 0]   # S0..S3  → 0001 (+ Cout=1) = 10001 = 17
    C = [0, 1, 1, 1]   # carry OUT of bit i (c1..c4)
    x0 = 130
    fy = 200
    for i in range(4):  # i=0 -> bit3 (leftmost)... draw bit3..bit0 left to right
        bit = 3 - i
        x = x0 + i * 170
        s += _box(x, fy - 35, 110, 70, f"FA біт {bit}", None, "#eef4ff")
        s += text(x + 55, fy - 50, f"A{bit}={A[bit]}  B{bit}={B[bit]}", 11, INK, "middle", "bold")
        s += _pin(x + 30, fy - 35, x + 30, fy - 48)
        s += _pin(x + 80, fy - 35, x + 80, fy - 48)
        # сума вниз
        s += _pin(x + 55, fy + 35, x + 55, fy + 60)
        s += text(x + 55, fy + 76, f"S{bit}={S[bit]}", 12, GREEN, "middle", "bold")
        # перенос між блоками (праворуч → ліворуч)
        if i < 3:
            cval = C[bit - 1] if bit - 1 >= 0 else 0
        # carry into this FA comes from the FA to its right (lower bit)
    # намалюємо переноси як стрілки справа наліво
    for i in range(3):
        x = x0 + i * 170
        xr = x0 + (i + 1) * 170
        cb = 3 - (i + 1)  # carry out of lower bit feeds this
        s += arrow(xr, fy, x + 110, fy, AMBER, 2)
        s += text((xr + x + 110) / 2, fy - 8, f"c={C[cb]}", 10.5, AMBER, "middle", "bold")
    # carry in (0) праворуч і carry out (ліворуч)
    s += _pin(x0 + 3 * 170 + 110, fy, x0 + 3 * 170 + 150, fy)
    s += text(x0 + 3 * 170 + 156, fy + 4, "Cin=0", 11, GREY, "start")
    s += _pin(x0, fy, x0 - 40, fy)
    s += text(x0 - 46, fy + 4, "Cout=1", 11, RED, "end", "bold")
    s += rect(70, 330, W - 140, 60, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 354, "0110 (6) + 1011 (11) = 1 0001 (17): перенос «біжить» з молодшого розряду в старший.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 376, "Що довше число, то довше біжить перенос — звідси затримка суматора (§14.5, далі §18).", 11.5, GREY, "middle", style="italic")
    save("fig-15-6-4-ripple.svg", s)


# ── Рис. 15.6.5 — мультиплексор ─────────────────────────────────────────────
def fig156_mux():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Мультиплексор (MUX): обирає, який вхід пропустити", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "лінія вибору S «перемикає»: S=0 → Y=A, S=1 → Y=B; це цифровий перемикач Y = S̄·A + S·B",
              12, GREY, "middle", style="italic")
    # gate-level 2:1
    s += text(110, 150, "A", 12, INK, "end", "bold")
    s += text(110, 250, "B", 12, INK, "end", "bold")
    s += _pin(116, 150, 230, 150)
    s += _pin(116, 250, 230, 250)
    # S і S̄
    s += text(110, 320, "S", 12, RED, "end", "bold")
    s += _pin(116, 320, 150, 320)
    s += gate_not(150, 320, 28, 24)
    s += line(184, 320, 200, 320, INK, 1.4)
    s += line(200, 320, 200, 170, INK, 1.4)  # S̄ до AND1
    s += line(134, 320, 134, 270, INK, 1.4)
    s += line(134, 270, 215, 270, INK, 1.4)  # S до AND2
    # AND1: S̄·A
    s += line(200, 170, 215, 170, INK, 1.4)
    s += _pin(215, 150, 230, 150)
    s += gate_and(230, 160, 44, 36)
    s += text(252, 138, "S̄·A", 9.5, GREY, "middle")
    s += _pin(280, 160, 320, 160)
    s += line(320, 160, 320, 192, INK, 1.6)
    # AND2: S·B
    s += _pin(215, 270, 230, 270)
    s += gate_and(230, 250, 44, 36)
    s += text(252, 292, "S·B", 9.5, GREY, "middle")
    s += _pin(280, 250, 320, 250)
    s += line(320, 250, 320, 218, INK, 1.6)
    # OR
    s += _pin(320, 192, 336, 192)
    s += _pin(320, 218, 336, 218)
    s += gate_or(336, 205, 50, 44)
    s += _pin(386, 205, 430, 205)
    s += text(436, 209, "Y", 13, GREEN, "start", "bold")
    # перемикач-інтуїція
    s += rect(540, 110, 290, 220, "none", FAINT, 1.5, 10)
    s += text(685, 136, "Інтуїція — перемикач", 13, INK, "middle", "bold")
    s += line(580, 180, 620, 180, INK, 2)
    s += text(572, 184, "A", 11, INK, "end", "bold")
    s += line(580, 240, 620, 240, INK, 2)
    s += text(572, 244, "B", 11, INK, "end", "bold")
    s += line(640, 210, 700, 210, INK, 2)
    s += line(640, 210, 622, 182, RED, 2.4)  # вказує на A
    s += circle(640, 210, 4, INK, INK, 1)
    s += text(706, 214, "Y", 12, GREEN, "start", "bold")
    s += text(685, 280, "S вирішує, до якого входу", 11, GREY, "middle")
    s += text(685, 296, "під'єднати вихід", 11, GREY, "middle")
    s += text(685, 318, "Більше входів → більше ліній S (4:1 → 2 лінії, 8:1 → 3)", 10.5, GREY, "middle", style="italic")
    save("fig-15-6-5-mux.svg", s)


# ── Рис. 15.6.6 — дешифратор ────────────────────────────────────────────────
def fig156_decoder():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 34, "Дешифратор: N входів → 2ᴺ виходів, активний рівно ОДИН", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вмикає той вихід, чий двійковий номер дорівнює входу — основа адресації (пам'ять, §19)",
              12, GREY, "middle", style="italic")
    # 2->4 decoder
    s += text(110, 200, "A1", 12, INK, "end", "bold")
    s += text(110, 250, "A0", 12, INK, "end", "bold")
    s += _pin(116, 200, 160, 200)
    s += _pin(116, 250, 160, 250)
    outs = [("Y0", "Ā1·Ā0", 0), ("Y1", "Ā1·A0", 0), ("Y2", "A1·Ā0", 1), ("Y3", "A1·A0", 0)]
    # приклад: A1=1, A0=0 → Y2 активний
    for i, (name, expr, active) in enumerate(outs):
        yy = 110 + i * 65
        s += gate_and(360, yy, 46, 38)
        s += _pin(316, yy - 10, 360, yy - 10)
        s += _pin(316, yy + 10, 360, yy + 10)
        s += _pin(406, yy, 460, yy)
        col = GREEN if active else GREY
        s += text(466, yy + 4, f"{name} = {active}", 12.5, col, "start", "bold")
        s += text(335, yy - 18, expr, 10, GREY, "middle")
    s += text(250, 330, "вхід A1A0 = 10  →  активний лише Y2", 12.5, GREEN, "middle", "bold")
    s += rect(560, 300, 290, 90, "#f4f7f4", GREEN, 1.6, 10)
    s += text(705, 324, "«один з багатьох» (one-hot):", 12, INK, "middle", "bold")
    s += text(705, 346, "так процесор обирає, ДО ЯКОЇ", 11, INK, "middle")
    s += text(705, 364, "комірки пам'яті звернутись (§19)", 11, INK, "middle")
    save("fig-15-6-6-decoder.svg", s)


# ═══════════════ §15.7 — Від вентилів до складних функцій ════════════════════
# ── Рис. 15.7.1 — драбина абстракції ────────────────────────────────────────
def fig157_ladder():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 34, "Драбина абстракції: як приборкують складність", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен рівень збудований з нижнього й ХОВАЄ його деталі — так із транзисторів виростає процесор",
              12, GREY, "middle", style="italic")
    levels = [
        ("транзистор", "ключ із §12 / §15.5", "#f3f5fd", BLUE),
        ("вентиль (AND, OR, NOT, …)", "кілька транзисторів (§15.2–15.5)", "#eef4ff", INK),
        ("блок: суматор · MUX · дешифратор", "десятки вентилів (§15.6)", "#eef7ee", GREEN),
        ("функціональний вузол: АЛП, регістр", "блоки + пам'ять (§15.7, Розділ 16)", "#fbf6ec", "#9a7322"),
        ("ПРОЦЕСОР", "вузли + керування (Розділ 18)", "#fdf4f4", RED),
    ]
    n = len(levels)
    bw, bh = 460, 56
    x0 = (W - bw) / 2
    for i, (name, made, bg, col) in enumerate(levels):
        y = 400 - i * 70
        wfac = 1.0 - i * 0.07
        ww = bw * wfac
        xx = (W - ww) / 2
        s += rect(xx, y, ww, bh, bg, col, 2, 10)
        s += text(W / 2, y + 25, name, 14, col, "middle", "bold")
        s += text(W / 2, y + 43, made, 10.5, GREY, "middle", style="italic")
        if i < n - 1:
            s += arrow(W / 2, y, W / 2, y - 14, INK, 2)
    s += text(W - 60, 120, "вище —", 11, GREY, "end", style="italic")
    s += text(W - 60, 136, "більше", 11, GREY, "end", style="italic")
    s += text(W - 60, 152, "абстракції", 11, GREY, "end", style="italic")
    s += text(70, 410, "нижче —", 11, GREY, "start", style="italic")
    s += text(70, 426, "більше деталей", 11, GREY, "start", style="italic")
    save("fig-15-7-1-ladder.svg", s)


# ── Рис. 15.7.2 — сила і стіна: будь-що, але таблиця вибухає ────────────────
def fig157_completeness():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 34, "Сила і межа комбінаційної логіки", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "будь-яку функцію можна збудувати (§15.1, §15.3) — та «однією таблицею» вона вибухає за розміром",
              12, GREY, "middle", style="italic")
    # ліворуч — сила
    s += rect(60, 90, 360, 240, "none", GREEN, 1.7, 10)
    s += text(240, 116, "СИЛА: будується будь-що", 13.5, GREEN, "middle", "bold")
    s += text(240, 150, "таблиця істинності", 12, INK, "middle", "bold")
    s += arrow(240, 158, 240, 178, INK, 1.8)
    s += text(240, 196, "сума добутків (§15.1)", 12, INK, "middle", "bold")
    s += arrow(240, 204, 240, 224, INK, 1.8)
    s += text(240, 242, "вентилі (досить навіть NAND)", 12, INK, "middle", "bold")
    s += text(240, 290, "{AND, OR, NOT} — функціонально", 11, GREY, "middle", style="italic")
    s += text(240, 306, "повний набір: на все вистачає", 11, GREY, "middle", style="italic")
    # праворуч — вибух
    s += rect(440, 90, 360, 240, "none", AMBER, 1.7, 10)
    s += text(620, 116, "СТІНА: 2ᴺ рядків", 13.5, "#9a7322", "middle", "bold")
    data = [(2, "4"), (4, "16"), (8, "256"), (16, "65 536"), (32, "≈ 4 млрд")]
    bx = 470
    base = 300
    for i, (nn, val) in enumerate(data):
        x = bx + i * 64
        h = min(10 + i * 36, 150)
        s += rect(x, base - h, 44, h, "#fbf3e0", AMBER, 1.5, 3)
        s += text(x + 22, base + 16, f"{nn}", 11, INK, "middle", "bold")
        s += text(x + 22, base - h - 6, val, 9.5, "#9a7322", "middle", "bold")
    s += text(620, base + 34, "входів  →  рядків (вибух!)", 11, GREY, "middle", style="italic")
    s += text(W / 2, 372, "Тому складне НЕ роблять однією величезною таблицею — його РОЗБИВАЮТЬ на блоки й кроки.",
              12.5, INK, "middle", "bold")
    save("fig-15-7-2-completeness.svg", s)


# ── Рис. 15.7.3 — стіна №2: немає пам'яті ──────────────────────────────────
def fig157_wall():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Друга межа: комбінаційна логіка нічого не ПАМ'ЯТАЄ", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вихід залежить лише від входів зараз — тож «порахувати натискання» чи «зробити крок за кроком» вона не вміє",
              12, GREY, "middle", style="italic")
    # приклад: лічильник натискань — неможливо без пам'яті
    s += rect(80, 110, 300, 150, "#eef4ff", INK, 2, 10)
    s += text(230, 150, "комбінаційна схема", 13, INK, "middle", "bold")
    s += text(230, 172, "знає лише ВХІД зараз", 11, GREY, "middle")
    s += text(230, 210, "«скільки разів", 12, RED, "middle", "bold")
    s += text(230, 228, "натиснули кнопку?»", 12, RED, "middle", "bold")
    s += text(230, 248, "— відповісти НЕ може", 11, RED, "middle", style="italic")
    s += arrow(390, 185, 470, 185, INK, 2.4)
    s += text(430, 175, "треба", 11, GREY, "middle")
    s += rect(480, 110, 300, 150, "#eef7ee", GREEN, 2, 10)
    s += text(630, 142, "ПАМ'ЯТЬ + ТАКТ", 14, GREEN, "middle", "bold")
    for i, t in enumerate(["• зберегти стан між подіями", "• рахувати, лічити кроки",
                           "• виконувати ПОСЛІДОВНІСТЬ", "  дій у часі"]):
        s += text(500, 174 + i * 22, t, 11.5, INK, "start")
    s += text(630, 250, "→ Розділ 16 (тригери)", 11.5, GREEN, "middle", "bold")
    s += text(W / 2, 350, "Дві межі — вибух таблиці й брак пам'яті — і штовхають від «однієї схеми» до МАШИНИ, що працює в часі.",
              12, INK, "middle", "bold")
    save("fig-15-7-3-wall.svg", s)


# ── Рис. 15.7.4 — АЛП: блок, що вміє кілька операцій ───────────────────────
def fig157_alu():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 34, "АЛП: усі §15.6-блоки сходяться в обчислювальне ядро", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кілька операцій рахуються паралельно, а MUX за кодом операції обирає потрібний результат",
              12, GREY, "middle", style="italic")
    # входи
    s += text(90, 130, "A", 14, INK, "end", "bold")
    s += text(90, 250, "B", 14, INK, "end", "bold")
    s += _pin(96, 130, 140, 130)
    s += _pin(96, 250, 140, 250)
    # операційні блоки
    ops = [("ADD  A+B", 120), ("AND  A·B", 175), ("OR   A+B", 230), ("CMP  A?B", 285)]
    for name, yy in ops:
        s += _box(140, yy - 18, 130, 36, name, None, "#eef4ff")
        s += _pin(270, yy, 470, yy)
    # спільні входи у блоки (схематично)
    s += line(120, 130, 120, 285, GREY, 1.4)
    s += line(120, 130, 140, 130, GREY, 1.4)
    for _, yy in ops:
        s += line(120, yy, 140, yy, GREY, 1.4)
    s += line(120, 250, 120, 285, GREY, 1.4)
    # MUX
    s += f'<path d="M 470,100 L 510,118 L 510,292 L 470,310 Z" fill="#fbf6ec" stroke="{INK}" stroke-width="2"/>\n'
    s += text(490, 208, "MUX", 12, INK, "middle", "bold")
    s += _pin(510, 205, 580, 205)
    s += text(586, 209, "результат", 12.5, GREEN, "start", "bold")
    # керування
    s += _pin(490, 340, 490, 312)
    s += text(490, 358, "код операції", 11.5, RED, "middle", "bold")
    s += text(490, 374, "(обирає, що видати)", 10.5, GREY, "middle", style="italic")
    s += rect(630, 110, 210, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(735, 136, "Це вже §15.6 разом:", 12, INK, "middle", "bold")
    s += text(735, 160, "суматор + логіка + MUX", 11.5, INK, "middle")
    s += text(735, 184, "= обчислювальне ядро", 11.5, INK, "middle", "bold")
    s += text(735, 208, "процесора.", 11.5, INK, "middle")
    s += text(735, 234, "Лишилось додати пам'ять", 11, GREY, "middle", style="italic")
    s += text(735, 250, "і керування (Розділи 16, 18).", 11, GREY, "middle", style="italic")
    save("fig-15-7-4-alu.svg", s)


# ── Рис. 15.7.5 — два способи обчислити функцію ────────────────────────────
def fig157_two_ways():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Два способи обчислити: простором (схема) чи в часі (процесор)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ту саму функцію можна «відлити» в залізо назавжди — або виконувати кроками на гнучкій машині",
              12, GREY, "middle", style="italic")
    # ліворуч — просторово
    s += rect(60, 90, 360, 250, "none", INK, 1.7, 10)
    s += text(240, 114, "ПРОСТОРОВО: окрема схема", 13, INK, "middle", "bold")
    # купка вентилів
    for (gx, gy) in [(140, 160), (210, 150), (180, 210), (260, 200), (150, 260), (240, 255)]:
        s += gate_and(gx, gy, 30, 24) if (gx + gy) % 2 == 0 else gate_or(gx, gy, 32, 24)
    s += _pin(300, 205, 360, 205)
    s += text(310, 196, "відповідь", 10.5, GREEN, "start", "bold")
    s += text(240, 300, "швидко, але ЖОРСТКО:", 11.5, INK, "middle", "bold")
    s += text(240, 318, "одна функція, площа росте зі складністю", 10.5, GREY, "middle", style="italic")
    # праворуч — у часі
    s += rect(440, 90, 360, 250, "none", GREEN, 1.7, 10)
    s += text(620, 114, "У ЧАСІ: процесор", 13, GREEN, "middle", "bold")
    s += _box(500, 150, 100, 44, "АЛП", None, "#eef4ff")
    s += _box(640, 150, 100, 44, "регістри", None, "#eef7ee")
    s += f'<path d="M 600,172 h 40" fill="none" stroke="{INK}" stroke-width="1.8" marker-end="url(#aInk)"/>\n'
    s += f'<path d="M 640,186 q -20,40 -70,0" fill="none" stroke="{GREY}" stroke-width="1.6" marker-end="url(#aInk)" stroke-dasharray="4 3"/>\n'
    s += text(620, 232, "крок 1 → крок 2 → крок 3 …", 11.5, INK, "middle", "bold")
    s += text(620, 254, "(такт за тактом, за програмою)", 10.5, GREY, "middle", style="italic")
    s += text(620, 300, "гнучко й компактно, але ПОВІЛЬНІШЕ:", 11.5, INK, "middle", "bold")
    s += text(620, 318, "один маленький АЛП виконує що завгодно", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 372, "«Залізо» vs «програма»: той самий результат — або схемою назавжди, або кроками на процесорі.",
              12, INK, "middle", "bold")
    save("fig-15-7-5-two-ways.svg", s)


if __name__ == "__main__":
    # історія розділу (§15.0)
    fig_timeline()
    fig_idea()
    fig_strange()
    fig_bridge()
    # §15.1
    fig151_truthtable()
    fig151_three_ops()
    fig151_venn()
    fig151_laws()
    fig151_simplify()
    fig151_sop()
    # §15.2
    fig152_symbols()
    fig152_bubble()
    fig152_iec()
    fig152_multi()
    fig152_wiring()
    # §15.3
    fig153_nand_nor()
    fig153_demorgan()
    fig153_universal()
    fig153_why()
    fig153_nor_apollo()
    # §15.4
    fig154_xor_xnor()
    fig154_from_gates()
    fig154_compare()
    fig154_parity()
    fig154_controlled()
    # §15.5
    fig155_switch()
    fig155_principle()
    fig155_inverter()
    fig155_nand_nor()
    fig155_why()
    # §15.6
    fig156_combinational()
    fig156_half_adder()
    fig156_full_adder()
    fig156_ripple()
    fig156_mux()
    fig156_decoder()
    # §15.7
    fig157_ladder()
    fig157_completeness()
    fig157_wall()
    fig157_alu()
    fig157_two_ways()
    print("ch15 figures done.")
