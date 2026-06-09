# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 14 — «Логічні рівні: від аналога до цифри» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' / HIGH ('1') червоний, '−' / LOW ('0') синій;
«чисте/дійсне» — зелене; стрілки через marker; шрифт sans-serif. Підписи нумеруються
посекційно (Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 14.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # HIGH / '1' / +
BLUE  = "#1f47b5"   # LOW / '0' / −
GREEN = "#1f8a3b"   # чисте / дійсне / «спрацювало»
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
AMBER = "#caa24a"   # шум / спотворення
COPPER = "#b5742e"  # реле / мідь
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


_SUPMAP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
           "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻"}


def _sup(n):
    return "".join(_SUPMAP[c] for c in str(n))


# ── допоміжні елементи схем ──────────────────────────────────────────────────
def battery(cx, cy, scale=1.0):
    """Символ джерела: довга риска (+) і коротка (−), горизонтально по центру (cx,cy)."""
    out = line(cx - 3, cy - 13 * scale, cx - 3, cy + 13 * scale, INK, 3)   # довга (+)
    out += line(cx + 3, cy - 7 * scale, cx + 3, cy + 7 * scale, INK, 5)    # коротка (−)
    out += text(cx - 12, cy - 16 * scale, "+", 13, RED, "middle", "bold")
    out += text(cx + 14, cy - 16 * scale, "−", 13, BLUE, "middle", "bold")
    return out


def lamp(cx, cy, r=16, on=False):
    """Лампа: коло з хрестиком; on=True — зелене світіння."""
    fill = "#eafaef" if on else "#ffffff"
    stroke = GREEN if on else GREY
    out = circle(cx, cy, r, fill, stroke, 2.4)
    d = r * 0.62
    out += line(cx - d, cy - d, cx + d, cy + d, stroke, 2)
    out += line(cx - d, cy + d, cx + d, cy - d, stroke, 2)
    if on:
        for a in range(0, 360, 45):
            ex = cx + (r + 5) * math.cos(math.radians(a))
            ey = cy + (r + 5) * math.sin(math.radians(a))
            fx = cx + (r + 11) * math.cos(math.radians(a))
            fy = cy + (r + 11) * math.sin(math.radians(a))
            out += line(ex, ey, fx, fy, GREEN, 1.8)
    return out


def switch(x, y, length, closed, label):
    """Перемикач (реле-контакт) уздовж горизонталі від (x,y); довжина length.
    closed=True — замкнений (провідник), False — розімкнений (підняте плече)."""
    out = circle(x, y, 4, INK, INK, 1)
    out += circle(x + length, y, 4, INK, INK, 1)
    col = GREEN if closed else GREY
    if closed:
        out += line(x, y, x + length, y, col, 3)
    else:
        # плече підняте під кутом — розрив
        ang = -32
        ex = x + length * math.cos(math.radians(ang))
        ey = y + length * math.sin(math.radians(ang))
        out += line(x, y, ex, ey, col, 3)
    state = "1 (замкн.)" if closed else "0 (розімкн.)"
    out += text(x + length / 2, y - 16, label, 14, INK, "middle", "bold")
    out += text(x + length / 2, y + 26, state, 11.5, col, "middle", "bold")
    return out


# ── Рис. 14.0.1 — таймлайн: ланцюг питань до цифрової епохи ───────────────────
def fig_timeline():
    W, H = 880, 760
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: як аналог поступився цифрі", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "кожен крок — нове питання; сірим — постаті, що мають власну детальну історію далі в Модулі 3",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 100, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("~1837", "Беббідж / Babbage", "Чи може машина рахувати за програмою? — зубчаста, десяткова (→ Розділ 18)", True),
        ("1847", "Буль / Boole", "Чи можна звести міркування до алгебри з 0 і 1? — алгебра логіки (→ Розділ 15)", True),
        ("1870-ті", "телеграф, реле / relay", "Сигнал або Є, або нема — перемикач як два чіткі стани", False),
        ("1931", "Буш / Bush", "Аналоговий «диференціальний аналізатор» — рахує валами й шестернями", False),
        ("1937", "Шеннон / Shannon", "А що, як реле — це і Є булева логіка? — магістерська теза, що злила їх воєдино", False),
        ("1948", "Шеннон / Shannon", "Скільки інформації витримає ШУМНИЙ канал? — теорія інформації, «біт»", False),
        ("1947 →", "транзистор / transistor", "дискретний стан у кремнії — і цифрова епоха стартує (Модуль 2 → решта Модуля 3)", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, faint) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if faint else INK
        if i == 4:  # Шеннон 1937 — акцент
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 13, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if i == 4 else col), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, col, "start", style="italic")
    save("fig-14-0-1-timeline.svg", s)


# ── Рис. 14.0.2 — теза Шеннона: перемикачі = булева алгебра ───────────────────
def fig_shannon_map():
    W, H = 880, 540
    s = header(W, H)
    s += text(W / 2, 36, "Теза Шеннона (1937): перемикач = булева змінна", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "послідовно з'єднані контакти — це AND (·), паралельно — це OR (+); «лампа світиться» = логічна 1",
              12.5, GREY, "middle", style="italic")

    def truth(x, y, header_lbl, rows):
        out = text(x + 56, y - 10, header_lbl, 13.5, INK, "middle", "bold")
        cw, ch = 38, 22
        cols = ["A", "B", "вих."]
        for c, name in enumerate(cols):
            out += rect(x + c * cw, y, cw, ch, "#f3f3f3", GREY, 1.2)
            out += text(x + c * cw + cw / 2, y + 15, name, 12.5, INK, "middle", "bold")
        for r, (a, b, q) in enumerate(rows):
            yy = y + ch * (r + 1)
            for c, v in enumerate((a, b, q)):
                col = RED if v == 1 else BLUE
                bg = "#fdf4f4" if v == 1 else "#f3f5fd"
                if c == 2:
                    bg = "#eafaef" if v == 1 else "#f3f5fd"
                out += rect(x + c * cw, yy, cw, ch, bg, GREY, 1.2)
                out += text(x + c * cw + cw / 2, yy + 15, str(v),
                            12.5, (GREEN if (c == 2 and v == 1) else col), "middle", "bold")
        return out

    def panel(cx, title, expr, closedA, closedB, series):
        out = rect(cx - 190, 86, 380, 250, "none", FAINT, 2, 14)
        out += text(cx, 112, title, 16, INK, "middle", "bold")
        # коло: джерело зліва, лампа справа
        top_y = 165
        bx = cx - 150          # клема джерела
        lx = cx + 150          # лампа
        out += battery(bx, top_y + 35, 1.0)
        if series:
            # два контакти послідовно вгорі
            out += line(bx, top_y, bx + 18, top_y, INK, 2.4)
            out += switch(bx + 18, top_y, 70, closedA, "A")
            out += switch(bx + 18 + 70 + 18, top_y, 70, closedB, "B")
            out += line(bx + 18 + 70 + 18 + 70, top_y, lx, top_y, INK, 2.4)
            lit = closedA and closedB
        else:
            # два контакти паралельно
            out += line(bx, top_y, bx + 40, top_y, INK, 2.4)
            # верхня гілка A
            out += line(bx + 40, top_y, bx + 40, top_y - 28, INK, 2.4)
            out += switch(bx + 40, top_y - 28, 120, closedA, "A")
            out += line(bx + 40 + 120, top_y - 28, bx + 40 + 120, top_y, INK, 2.4)
            # нижня гілка B
            out += line(bx + 40, top_y, bx + 40, top_y + 28, INK, 2.4)
            out += switch(bx + 40, top_y + 28, 120, closedB, "B")
            out += line(bx + 40 + 120, top_y + 28, bx + 40 + 120, top_y, INK, 2.4)
            out += line(bx + 40 + 120, top_y, lx, top_y, INK, 2.4)
            lit = closedA or closedB
        # лампа + назад до джерела
        out += lamp(lx, top_y, 15, lit)
        out += line(lx, top_y + 15, lx, top_y + 70, INK, 2.4)
        out += line(lx, top_y + 70, bx, top_y + 70, INK, 2.4)
        out += line(bx, top_y + 70, bx, top_y + 48, INK, 2.4)
        out += line(bx, top_y + 22, bx, top_y, INK, 2.4)
        out += text(cx, 304, expr, 17, INK, "middle", "bold")
        out += text(cx, 326, ("лампа = 1 лише коли A і B замкнені" if series
                              else "лампа = 1 коли A або B замкнені"),
                    12, GREY, "middle", style="italic")
        return out

    s += panel(252, "Послідовно  →  AND", "вих = A · B", True, True, True)
    s += panel(628, "Паралельно  →  OR", "вих = A + B", True, False, False)

    s += truth(150, 372, "AND (· , «і»)",
               [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)])
    s += truth(528, 372, "OR (+ , «або»)",
               [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)])

    s += rect(330, 372, 168, 118, "#f4f7f4", GREEN, 1.6, 10)
    s += text(414, 398, "Чому це бомба:", 13, INK, "middle", "bold")
    s += text(414, 420, "схему з реле тепер", 12, INK, "middle")
    s += text(414, 438, "можна СПРОСТИТИ", 12, INK, "middle", "bold")
    s += text(414, 456, "алгеброю Буля —", 12, INK, "middle")
    s += text(414, 474, "як шкільний приклад.", 12, INK, "middle")
    save("fig-14-0-2-shannon-map.svg", s)


# ── Рис. 14.0.3 — чому цифра виживає в шумі (регенерація) ─────────────────────
def fig_noise():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 36, "Чому переміг дискретний сигнал: шум накопичується — чи стирається", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58,
              "однаковий шум додається на кожній ланці; аналог його ТЯГНЕ далі, цифру щоразу «випрямляють» назад до 0/1",
              12.5, GREY, "middle", style="italic")

    # детермінований «шум» — сума кількох синусів (без random, відтворювано)
    def noise(t, k):
        return (math.sin(t * 5.3 + k * 1.7) + 0.6 * math.sin(t * 11.0 + k * 3.1)
                + 0.4 * math.sin(t * 23.0 + k)) * 1.0

    stages = 3
    seg_w = 230
    x0 = 70
    amp = 26

    # ── рядок АНАЛОГ ─────────────────────────────────────────────
    ay = 150
    s += text(x0, ay - 60, "АНАЛОГ", 16, AMBER, "start", "bold")
    s += text(x0 + 95, ay - 60, "— кожен підсилювач підсилює й корисне, і шум: похибка росте", 12.5, GREY, "start", style="italic")
    nlev = 0.0
    for st in range(stages):
        xa = x0 + st * seg_w
        # підсилювач-трикутник
        s += f'<path d="M {xa-8},{ay-22} L {xa+24},{ay} L {xa-8},{ay+22} Z" fill="#fbf3e0" stroke="{AMBER}" stroke-width="2"/>\n'
        s += text(xa + 8, ay + 5, "▷", 12, AMBER, "middle")
        # хвиля цієї ланки
        nlev += 1.0
        pts = []
        N = 90
        for i in range(N + 1):
            t = i / N
            xx = xa + 30 + t * (seg_w - 50)
            base = math.sin(t * 2 * math.pi * 1.5)
            yy = ay - amp * base - nlev * 3.0 * noise(t, st)
            pts.append((xx, yy))
        s += polyline(pts, AMBER, 2.2)
        s += text(xa + 30 + (seg_w - 50) / 2, ay + 50, f"ланка {st+1}", 11.5, GREY, "middle")
    s += text(x0 + stages * seg_w - 6, ay - 24, "спотворено", 12.5, RED, "start", "bold")
    s += text(x0 + stages * seg_w - 6, ay - 8, "вже не та форма", 11, GREY, "start", style="italic")

    # ── рядок ЦИФРА ──────────────────────────────────────────────
    dy = 380
    s += text(x0, dy - 78, "ЦИФРА", 16, GREEN, "start", "bold")
    s += text(x0 + 78, dy - 78, "— на кожній ланці пороговий вирішувач (буфер) «округлює» сигнал назад до чистих 0/1", 12.5, GREY, "start", style="italic")
    thr = dy
    hi = dy - amp
    lo = dy + amp
    # рівень-смуги
    s += rect(x0, hi - 12, stages * seg_w - 20, 12, "#fdf4f4", "none", 0)
    s += rect(x0, lo, stages * seg_w - 20, 12, "#f3f5fd", "none", 0)
    pattern = [1, 0, 1, 1, 0]
    for st in range(stages):
        xa = x0 + st * seg_w
        # регенератор-прямокутник (компаратор)
        s += rect(xa - 12, dy - 20, 30, 40, "#eafaef", GREEN, 2, 5)
        s += text(xa + 3, dy + 5, "⎍", 14, GREEN, "middle", "bold")
        # поріг
        s += line(xa + 26, thr, xa + seg_w - 24, thr, GREY, 1.4, "5 4")
        if st == 0:
            s += text(xa + seg_w - 24, thr - 4, "поріг", 11, GREY, "end", style="italic")
        # ідеальний меандр + шум, але «прибитий» до рівнів
        pts = []
        N = 120
        seglen = (seg_w - 50) / len(pattern)
        for i in range(N + 1):
            t = i / N
            idx = min(int(t * len(pattern)), len(pattern) - 1)
            level = hi if pattern[idx] == 1 else lo
            xx = xa + 30 + t * (seg_w - 50)
            # невеликий залишковий шум, але форма збережена
            yy = level - 2.2 * noise(t, st + 7)
            pts.append((xx, yy))
        s += polyline(pts, GREEN, 2.4)
        s += text(xa + 30 + (seg_w - 50) / 2, dy + 52, f"ланка {st+1}", 11.5, GREY, "middle")
    s += text(x0 - 8, hi - 18, "1", 13, RED, "end", "bold")
    s += text(x0 - 8, lo + 22, "0", 13, BLUE, "end", "bold")
    s += text(x0 + stages * seg_w - 6, dy - amp - 4, "як новий", 12.5, GREEN, "start", "bold")
    s += text(x0 + stages * seg_w - 6, dy - amp + 12, "0/1 відновлено точно", 11, GREY, "start", style="italic")

    s += rect(70, 500, W - 140, 46, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 524,
              "Поки шум менший за «яму» між 0 і 1, його можна стерти НАЦІЛО. Саме це 1948 року Шеннон зробив строгою теорією.",
              13, INK, "middle", "bold")
    save("fig-14-0-3-noise-regen.svg", s)


# ═════════════════════════ §14.1 — Навіщо цифра ═════════════════════════════

# ── Рис. 14.1.1 — дві мови для одного числа ──────────────────────────────────
def fig141_two_languages():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 36, "Дві мови, щоб нести число: неперервна й дискретна", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "аналог кладе значення у точну ВИСОТУ сигналу; цифра дозволяє лише кілька станів — логіка бере рівно два",
              12.5, GREY, "middle", style="italic")
    # ── АНАЛОГ ──
    ax, aw = 95, 300
    track_y = 185
    s += text(ax, 110, "АНАЛОГ — неперервний", 15, INK, "start", "bold")
    for i in range(61):
        xx = ax + aw * i / 60
        s += line(xx, track_y - 4, xx, track_y + 4, FAINT, 1)
    s += line(ax, track_y, ax + aw, track_y, INK, 2)
    pv = 0.62
    px = ax + aw * pv
    s += arrow(px, track_y - 48, px, track_y - 7, GREEN, 2.6)
    s += circle(px, track_y, 5, GREEN, GREEN, 1)
    s += text(px, track_y - 56, "значення — тут", 12.5, GREEN, "middle", "bold")
    s += text(px, track_y - 40, "(будь-де)", 11, GREEN, "middle", style="italic")
    s += text(ax, track_y + 26, "0", 12, GREY, "middle")
    s += text(ax + aw, track_y + 26, "макс", 12, GREY, "middle")
    s += text(ax + aw / 2, track_y + 52, "∞ можливих значень —", 12, GREY, "middle", style="italic")
    s += text(ax + aw / 2, track_y + 70, "і шум ховається між ними непомітно", 12, GREY, "middle", style="italic")
    # ── ЦИФРА ──
    bx = 540
    s += text(bx, 110, "ЦИФРА — дискретна (тут: 2 стани)", 15, INK, "start", "bold")
    y1, yf, y0 = 135, 178, 213
    s += rect(bx, y1, 80, 34, "#fdf4f4", RED, 2.4, 8)
    s += text(bx + 40, y1 + 23, "1", 17, RED, "middle", "bold")
    s += rect(bx, yf, 80, 30, "#f6f6f6", GREY, 1.2, 0)
    s += text(bx + 40, yf + 19, "заборонено", 10.5, GREY, "middle", style="italic")
    s += rect(bx, y0, 80, 34, "#f3f5fd", BLUE, 2.4, 8)
    s += text(bx + 40, y0 + 23, "0", 17, BLUE, "middle", "bold")
    s += text(bx + 92, y1 + 22, "← дозволений стан", 12.5, INK, "start")
    s += text(bx + 92, y0 + 22, "← дозволений стан", 12.5, INK, "start")
    s += text(bx + 92, yf + 19, "← «нічия земля» (запас)", 11.5, GREY, "start", style="italic")
    s += text(bx + 40, y0 + 56, "значення «округлюється» до 0 або 1", 11.5, GREY, "middle", style="italic")
    # ── нижня плашка ──
    s += rect(70, 350, W - 140, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 374, "Більше станів теж можна (як 10 десяткових цифр — Розділ 17), але кожен зайвий стан звужує «ями» між ними.",
              12.5, INK, "middle")
    s += text(W / 2, 394, "Заради найбільшої стійкості до шуму логіка спинилася на ДВОХ — 0 і 1.", 12.5, INK, "middle", "bold")
    save("fig-14-1-1-two-languages.svg", s)


# ── Рис. 14.1.2 — шум на порозі: аналог гадає, цифра вирішує ──────────────────
def fig141_decision():
    W, H = 880, 450
    s = header(W, H)
    s += text(W / 2, 36, "Той самий шумний сигнал: аналог лишається невизначеним, цифра вирішує", 20, INK, "middle", "bold")
    s += text(W / 2, 58,
              "цифровий вхід питає лише «вище порога чи нижче» — і поки шум не дістав порога, відповідь тверда",
              12.5, GREY, "middle", style="italic")

    vmax = 3.3
    top_y, bot_y = 100, 360

    def vy(v):
        return bot_y - (v / vmax) * (bot_y - top_y)

    nom, band = 2.05, 0.15

    def axis(cx, title):
        out = text(cx, 86, title, 15, INK, "middle", "bold")
        out += line(cx, top_y, cx, bot_y, INK, 2)
        for v in range(0, 4):
            out += line(cx - 5, vy(v), cx + 5, vy(v), GREY, 1.4)
            out += text(cx - 12, vy(v) + 4, f"{v}", 11, GREY, "end")
        out += text(cx - 12, top_y - 6, "В", 11, GREY, "end")
        return out

    # ЛІВО — аналог
    lx = 230
    s += axis(lx, "АНАЛОГ: читаємо саме значення")
    s += rect(lx - 26, vy(nom + band), 52, vy(nom - band) - vy(nom + band), "#fbf3e0", AMBER, 1.6, 3)
    s += line(lx - 30, vy(nom), lx + 30, vy(nom), AMBER, 2.4)
    s += circle(lx, vy(nom), 4, AMBER, AMBER, 1)
    s += text(lx + 40, vy(nom + band) - 2, "1.9 … 2.2 В ?", 13, INK, "start", "bold")
    s += text(lx + 40, vy(nom) + 16, "шум ±0.15 В", 11.5, AMBER, "start")
    s += text(lx, bot_y + 28, "а скільки НАСПРАВДІ?", 13, RED, "middle", "bold")
    s += text(lx, bot_y + 46, "шум невіддільний від значення", 11.5, GREY, "middle", style="italic")

    # ПРАВО — цифра
    rx = 640
    s += axis(rx, "ЦИФРА: вирішуємо 0 / 1")
    thr = 1.65
    s += line(rx - 90, vy(thr), rx + 60, vy(thr), BLUE, 2, "6 4")
    s += text(rx - 94, vy(thr) + 4, "поріг", 11.5, BLUE, "end", "bold")
    s += rect(rx - 26, vy(nom + band), 52, vy(nom - band) - vy(nom + band), "#eafaef", GREEN, 1.6, 3)
    s += line(rx - 30, vy(nom), rx + 30, vy(nom), GREEN, 2.4)
    # стрілка запасу
    s += arrow(rx + 44, vy(nom - band), rx + 44, vy(thr), GREEN, 1.8)
    s += arrow(rx + 44, vy(thr), rx + 44, vy(nom - band), GREEN, 1.8)
    s += text(rx + 50, (vy(nom - band) + vy(thr)) / 2 + 4, "запас 0.25 В", 11.5, GREEN, "start", "bold")
    s += text(rx, bot_y + 28, "однозначно  «1»", 15, GREEN, "middle", "bold")
    s += text(rx, bot_y + 46, "весь шумовий розкид — вище порога", 11.5, GREY, "middle", style="italic")

    s += rect(70, 408, W - 140, 34, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 430, "Огрубивши до «вище/нижче порога», цифра виграє визначеність там, де аналог приречений сумніватися.",
              12.5, INK, "middle", "bold")
    save("fig-14-1-2-decision.svg", s)


# ── Рис. 14.1.3 — накопичення похибки за копіями ─────────────────────────────
def fig141_generations():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 36, "Копія копії: аналог псується з кожним поколінням, цифра — ні", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58,
              "кожне копіювання додає трохи шуму; в аналозі він НАКОПИЧУЄТЬСЯ (~√N), у цифрі щоразу стирається до 0",
              12.5, GREY, "middle", style="italic")
    gx0, gx1 = 110, 700
    gy_bot, gy_top = 360, 100
    Nmax = 8
    s += arrow(gx0, gy_bot, gx1 + 8, gy_bot, INK, 2)
    s += arrow(gx0, gy_bot, gx0, gy_top - 8, INK, 2)
    s += text(gx1 + 14, gy_bot + 18, "копія №", 12.5, INK, "start", "bold")
    s += text(gx0 - 10, gy_top - 12, "накопичена", 12, INK, "middle", "bold")
    s += text(gx0 - 10, gy_top + 4, "похибка", 12, INK, "middle", "bold")
    for n in range(Nmax + 1):
        xx = gx0 + (gx1 - gx0) * n / Nmax
        s += line(xx, gy_bot, xx, gy_bot + 5, GREY, 1.4)
        s += text(xx, gy_bot + 20, str(n), 11, GREY, "middle")
    # аналог: sigma*sqrt(n)
    sigma = 1.0
    full = math.sqrt(Nmax)
    pts = []
    for i in range(0, 161):
        n = Nmax * i / 160.0
        e = sigma * math.sqrt(n)
        xx = gx0 + (gx1 - gx0) * n / Nmax
        yy = gy_bot - (e / full) * (gy_bot - gy_top)
        pts.append((xx, yy))
    s += polyline(pts, AMBER, 2.8)
    s += text(gx1 - 4, gy_top + 26, "АНАЛОГ ~ σ·√N", 13.5, AMBER, "end", "bold")
    s += text(gx1 - 4, gy_top + 44, "(шипіння касети, копія ксерокса)", 11.5, GREY, "end", style="italic")
    # цифра: 0
    s += line(gx0, gy_bot - 3, gx1, gy_bot - 3, GREEN, 3)
    s += text(gx0 + 90, gy_bot - 12, "ЦИФРА = 0 (регенерується щоразу)", 13, GREEN, "start", "bold")
    # маленькі ескізи якості
    for n, q in ((1, "чисто"), (4, "шум"), (8, "руїна")):
        xx = gx0 + (gx1 - gx0) * n / Nmax
        e = sigma * math.sqrt(n)
        yy = gy_bot - (e / full) * (gy_bot - gy_top)
        s += circle(xx, yy, 4, AMBER, AMBER, 1)
        s += text(xx + 6, yy - 8, q, 11, GREY, "start", style="italic")
    # підсумкова плашка справа
    s += rect(728, 110, 130, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(793, 134, "100 копій:", 12.5, INK, "middle", "bold")
    s += text(793, 158, "аналог", 12, AMBER, "middle", "bold")
    s += text(793, 176, "σ·√100 = 10σ", 12, INK, "middle")
    s += text(793, 194, "(зруйновано)", 11, GREY, "middle", style="italic")
    s += text(793, 222, "цифра", 12, GREEN, "middle", "bold")
    s += text(793, 240, "0 (як новий)", 12, INK, "middle")
    save("fig-14-1-3-generations.svg", s)


# ── Рис. 14.1.4 — чому два, а не десять ──────────────────────────────────────
def fig141_why_two():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Чому два стани, а не десять: ширина «ями» вирішує все", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "за того самого розмаху напруги (тут 3.3 В) менше станів = ширші ями = більший запас на шум",
              12.5, GREY, "middle", style="italic")
    top_y, bot_y = 110, 400
    Vdd = 3.3
    noise_px = 0.45 / Vdd * (bot_y - top_y)   # однаковий шум 0.45 В в обох

    def bar(cx, levels, title, sub):
        out = text(cx, 92, title, 15, INK, "middle", "bold")
        out += rect(cx - 50, top_y, 100, bot_y - top_y, "#fafafa", INK, 2, 0)
        for k in range(levels):
            ly = bot_y - (bot_y - top_y) * k / (levels - 1)
            col = RED if k == levels - 1 else (BLUE if k == 0 else GREY)
            out += line(cx - 50, ly, cx + 50, ly, col, 2.4)
            lab = "1" if k == levels - 1 else ("0" if k == 0 else "")
            if lab:
                out += text(cx - 60, ly + 5, lab, 13, col, "end", "bold")
        # позначка одного кроку (яма)
        step = (bot_y - top_y) / (levels - 1)
        out += line(cx + 64, bot_y, cx + 64, bot_y - step, INK, 1.6)
        out += line(cx + 60, bot_y, cx + 68, bot_y, INK, 1.6)
        out += line(cx + 60, bot_y - step, cx + 68, bot_y - step, INK, 1.6)
        out += text(cx + 72, bot_y - step / 2 + 4, "яма", 11, INK, "start", "bold")
        # однаковий шум
        ny = top_y + 36
        out += rect(cx - 14, ny, 28, noise_px, "#fbf3e0", AMBER, 1.6, 2)
        out += text(cx, ny - 6, "шум 0.45 В", 11, AMBER, "middle", "bold")
        out += text(cx, bot_y + 26, sub, 12.5, INK, "middle", "bold")
        return out

    s += bar(250, 2, "2 рівні", "крок 3.3 В → запас ~1.65 В")
    s += text(250, 446, "шум « ями  →  стерти начисто", 12, GREEN, "middle", "bold")
    s += bar(630, 10, "10 рівнів", "крок 0.37 В → запас ~0.18 В")
    s += text(630, 446, "шум > кроку  →  стрибок у сусідній рівень", 12, RED, "middle", "bold")
    # порівняння стрілкою
    s += text(W / 2, top_y + 150, "той самий", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, top_y + 166, "шум", 11.5, GREY, "middle", style="italic")
    save("fig-14-1-4-why-two.svg", s)


# ── Рис. 14.1.5 — цифрова прірва: плавна vs раптова відмова ───────────────────
def fig141_cliff():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 36, "Чесна ціна: цифра ідеальна — аж до обриву", 21, INK, "middle", "bold")
    s += text(W / 2, 58,
              "аналог деградує плавно з ростом шуму; цифра тримає 100 %, та за порогом запасу падає в прірву",
              12.5, GREY, "middle", style="italic")
    gx0, gx1 = 110, 770
    gy_bot, gy_top = 350, 95
    s += arrow(gx0, gy_bot, gx1 + 8, gy_bot, INK, 2)
    s += arrow(gx0, gy_bot, gx0, gy_top - 8, INK, 2)
    s += text(gx1 + 4, gy_bot + 20, "рівень шуму →", 12.5, INK, "end", "bold")
    s += text(gx0 - 8, gy_top - 10, "надійність", 12.5, INK, "middle", "bold")
    for q in (0, 50, 100):
        yy = gy_bot - q / 100 * (gy_bot - gy_top)
        s += line(gx0 - 5, yy, gx0, yy, GREY, 1.4)
        s += text(gx0 - 10, yy + 4, f"{q}%", 11, GREY, "end")
    # аналог: плавний спад (опукла крива)
    pts = []
    for i in range(0, 161):
        x = i / 160.0
        q = 100 * (1 - x) ** 1.4
        xx = gx0 + x * (gx1 - gx0)
        yy = gy_bot - q / 100 * (gy_bot - gy_top)
        pts.append((xx, yy))
    s += polyline(pts, AMBER, 2.6)
    s += text(gx0 + 250, gy_bot - 150, "АНАЛОГ —", 13.5, AMBER, "start", "bold")
    s += text(gx0 + 250, gy_bot - 132, "плавна деградація", 12, GREY, "start", style="italic")
    # цифра: 100 до margin, тоді обрив
    margin = 0.55
    pts2 = []
    for i in range(0, 161):
        x = i / 160.0
        if x < margin - 0.03:
            q = 100
        elif x < margin + 0.05:
            q = 100 * (1 - (x - (margin - 0.03)) / 0.08)
        else:
            q = 2
        xx = gx0 + x * (gx1 - gx0)
        yy = gy_bot - q / 100 * (gy_bot - gy_top)
        pts2.append((xx, yy))
    s += polyline(pts2, GREEN, 3)
    s += text(gx0 + 70, gy_top + 22, "ЦИФРА — ідеально…", 13.5, GREEN, "start", "bold")
    mx = gx0 + margin * (gx1 - gx0)
    s += line(mx, gy_bot, mx, gy_top, BLUE, 1.6, "5 4")
    s += text(mx, gy_bot + 20, "запас вичерпано", 11.5, BLUE, "middle", "bold")
    s += text(mx + 40, gy_top + 60, "…і раптом прірва", 12.5, RED, "start", "bold")
    s += rect(70, 388, W - 140, 34, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 410, "Тому цифрова система або працює ідеально, або «не бачить» сигнал зовсім — золотої середини майже немає.",
              12.5, INK, "middle", "bold")
    save("fig-14-1-5-cliff.svg", s)


# ── Рис. 14.1.6 — баланс: що виграли / що віддали ────────────────────────────
def fig141_balance():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 36, "Угода «цифра»: що виграли і чим заплатили", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "огрубити неперервний світ до 0/1 — це обмін, і варто бачити обидві колонки",
              12.5, GREY, "middle", style="italic")
    # ліва колонка — виграли
    s += rect(70, 84, 370, 274, "#f4f7f4", GREEN, 1.8, 12)
    s += text(255, 112, "ЩО ВИГРАЛИ", 16, GREEN, "middle", "bold")
    wins = [
        "стійкість до шуму — його можна стерти",
        "точне копіювання й зберігання",
        "обчислення, програмованість,",
        "   доказова правильність (теза Шеннона)",
        "однакова обробка будь-яких даних",
        "   (звук, число, зображення — усе біти)",
    ]
    for i, t in enumerate(wins):
        yy = 142 + i * 32
        if not t.startswith("   "):
            s += text(92, yy, "✓", 15, GREEN, "start", "bold")
        s += text(112, yy, t.strip(), 13, INK, "start")
    # права колонка — віддали
    s += rect(470, 84, 340, 274, "#fbf6ec", AMBER, 1.8, 12)
    s += text(640, 112, "ЧИМ ЗАПЛАТИЛИ", 16, "#9a7322", "middle", "bold")
    costs = [
        "неперервність — значення квантується",
        "   (втрата дрібниць; Розділ 17)",
        "більше «дротів» / смуги на ту саму",
        "   точність (багато бітів)",
        "раптова відмова на обриві —",
        "   немає плавної деградації",
    ]
    for i, t in enumerate(costs):
        yy = 142 + i * 32
        if not t.startswith("   "):
            s += text(492, yy, "✗", 15, "#9a7322", "start", "bold")
        s += text(512, yy, t.strip(), 13, INK, "start")
    s += rect(70, 372, W - 140, 40, "#eef4ff", BLUE, 1.6, 10)
    s += text(W / 2, 397, "Для ОБЧИСЛЕНЬ ця угода — найвигідніша в техніці: трохи точності й смуги за майже абсолютну надійність.",
              12.5, INK, "middle", "bold")
    save("fig-14-1-6-balance.svg", s)


# ═══════════════════ §14.2 — «0» і «1» як діапазони напруг ═══════════════════
# Приклад-сімейство (узагальнений КМОН при Vdd = 3.3 В):
V_DD, V_OL, V_IL, V_IH, V_OH = 3.3, 0.3, 1.0, 2.3, 3.0


def _vaxis(s, cx, top_y, bot_y, vmax=V_DD, ticks=(0, 1, 2, 3)):
    s += line(cx, top_y, cx, bot_y, INK, 2)
    for v in ticks:
        yy = bot_y - (v / vmax) * (bot_y - top_y)
        s += line(cx - 5, yy, cx + 5, yy, GREY, 1.4)
        s += text(cx - 10, yy + 4, str(v), 11, GREY, "end")
    s += text(cx - 10, top_y - 10, "В", 11, GREY, "end")
    return s


# ── Рис. 14.2.1 — смугова діаграма рівнів (VOL/VIL/VIH/VOH) ──────────────────
def fig142_band_diagram():
    W, H = 880, 520
    s = header(W, H)
    s += text(W / 2, 34, "Логічний рівень — це СМУГА напруг (приклад: живлення 3.3 В, КМОН)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56,
              "вихід драйвера тиснеться до шин; вхід приймача приймає ширші смуги; між VIL і VIH — заборонена зона",
              12.5, GREY, "middle", style="italic")
    top_y, bot_y = 110, 470

    def vy(v):
        return bot_y - (v / V_DD) * (bot_y - top_y)

    s = _vaxis(s, 120, top_y, bot_y)
    s += text(120 - 10, vy(V_DD) + 4, "3.3", 11, GREY, "end")
    # ── вихід ──
    ox0, ow = 210, 150
    s += text(ox0 + ow / 2, 92, "ВИХІД — що гарантує драйвер", 14, INK, "middle", "bold")
    s += rect(ox0, vy(V_OL), ow, bot_y - vy(V_OL), "#f3f5fd", BLUE, 1.6)
    s += rect(ox0, top_y, ow, vy(V_OH) - top_y, "#fdf4f4", RED, 1.6)
    s += rect(ox0, vy(V_OH), ow, vy(V_OL) - vy(V_OH), "#fafafa", GREY, 1.2)
    s += text(ox0 + ow / 2, (bot_y + vy(V_OL)) / 2 + 4, "0  (≤ 0.3 В)", 12.5, BLUE, "middle", "bold")
    s += text(ox0 + ow / 2, (top_y + vy(V_OH)) / 2 + 4, "1  (≥ 3.0 В)", 12.5, RED, "middle", "bold")
    s += text(ox0 + ow / 2, (vy(V_OH) + vy(V_OL)) / 2 - 2, "драйвер сюди", 10.5, GREY, "middle", style="italic")
    s += text(ox0 + ow / 2, (vy(V_OH) + vy(V_OL)) / 2 + 13, "не виводить", 10.5, GREY, "middle", style="italic")
    s += line(ox0, vy(V_OL), ox0 + ow, vy(V_OL), BLUE, 1.4, "4 3")
    s += text(ox0 - 6, vy(V_OL) + 4, "VOL", 11, BLUE, "end", "bold")
    s += line(ox0, vy(V_OH), ox0 + ow, vy(V_OH), RED, 1.4, "4 3")
    s += text(ox0 - 6, vy(V_OH) + 4, "VOH", 11, RED, "end", "bold")
    # ── вхід ──
    ix0, iw = 560, 150
    s += text(ix0 + iw / 2, 92, "ВХІД — що вимагає приймач", 14, INK, "middle", "bold")
    s += rect(ix0, vy(V_IL), iw, bot_y - vy(V_IL), "#f3f5fd", BLUE, 1.6)
    s += rect(ix0, top_y, iw, vy(V_IH) - top_y, "#fdf4f4", RED, 1.6)
    s += rect(ix0, vy(V_IH), iw, vy(V_IL) - vy(V_IH), "#ededed", GREY, 1.2)
    for hx in range(int(ix0) + 10, int(ix0 + iw), 15):
        s += line(hx, vy(V_IH), hx - 14, vy(V_IL), "#cfcfcf", 0.8)
    s += text(ix0 + iw / 2, (bot_y + vy(V_IL)) / 2 + 4, "читається 0", 12.5, BLUE, "middle", "bold")
    s += text(ix0 + iw / 2, (top_y + vy(V_IH)) / 2 + 4, "читається 1", 12.5, RED, "middle", "bold")
    s += text(ix0 + iw / 2, (vy(V_IH) + vy(V_IL)) / 2, "ЗАБОРОНЕНО", 12, "#5a5a5a", "middle", "bold")
    s += text(ix0 + iw / 2, (vy(V_IH) + vy(V_IL)) / 2 + 17, "(невизначено)", 10.5, GREY, "middle", style="italic")
    s += line(ix0, vy(V_IL), ix0 + iw, vy(V_IL), BLUE, 1.4, "4 3")
    s += text(ix0 + iw + 6, vy(V_IL) + 4, "VIL 1.0", 11, BLUE, "start", "bold")
    s += line(ix0, vy(V_IH), ix0 + iw, vy(V_IH), RED, 1.4, "4 3")
    s += text(ix0 + iw + 6, vy(V_IH) + 4, "VIH 2.3", 11, RED, "start", "bold")
    # ── запас між колонками ──
    cx = 460
    for (va, vb, lab) in ((V_OH, V_IH, "запас «1»"), (V_IL, V_OL, "запас «0»")):
        ya, yb = vy(va), vy(vb)
        s += line(cx, ya, cx, yb, GREEN, 2)
        s += line(cx - 6, ya, cx + 6, ya, GREEN, 2)
        s += line(cx - 6, yb, cx + 6, yb, GREEN, 2)
        s += text(cx, (ya + yb) / 2 - 4, lab, 11, GREEN, "middle", "bold")
        s += text(cx, (ya + yb) / 2 + 11, "(§14.3)", 9.5, GREEN, "middle", style="italic")
    s += text(cx, bot_y + 28, "VOH > VIH і VOL < VIL → драйвер завжди «перестаровує», лишаючи зелений запас на шум",
              12, INK, "middle", "bold")
    save("fig-14-2-1-band-diagram.svg", s)


# ── Рис. 14.2.2 — будь-яке значення в смузі читається однаково ───────────────
def fig142_range_not_point():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Будь-яке значення в смузі читається однаково — точне число неважливе", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вісім різних виміряних напруг → три вердикти: «1», «невизначено», «0»",
              12.5, GREY, "middle", style="italic")
    top_y, bot_y = 90, 430
    strip_x, strip_w = 300, 150

    def vy(v):
        return bot_y - (v / V_DD) * (bot_y - top_y)

    s = _vaxis(s, 250, top_y, bot_y)
    s += text(250 - 10, vy(V_DD) + 4, "3.3", 11, GREY, "end")
    # смуги
    s += rect(strip_x, vy(V_IL), strip_w, bot_y - vy(V_IL), "#f3f5fd", BLUE, 1.4)
    s += rect(strip_x, top_y, strip_w, vy(V_IH) - top_y, "#fdf4f4", RED, 1.4)
    s += rect(strip_x, vy(V_IH), strip_w, vy(V_IL) - vy(V_IH), "#ededed", GREY, 1.2)
    s += line(strip_x - 4, vy(V_IH), strip_x + strip_w, vy(V_IH), RED, 1.3, "4 3")
    s += line(strip_x - 4, vy(V_IL), strip_x + strip_w, vy(V_IL), BLUE, 1.3, "4 3")
    s += text(strip_x + strip_w + 8, vy(V_IH) + 4, "VIH 2.3", 11, RED, "start", "bold")
    s += text(strip_x + strip_w + 8, vy(V_IL) + 4, "VIL 1.0", 11, BLUE, "start", "bold")
    samples = [(3.3, RED, "→ 1"), (2.8, RED, "→ 1"), (2.4, RED, "→ 1"),
               (1.9, GREY, "→ ?"), (1.4, GREY, "→ ?"),
               (0.8, BLUE, "→ 0"), (0.3, BLUE, "→ 0"), (0.0, BLUE, "→ 0")]
    for i, (v, col, verdict) in enumerate(samples):
        yy = vy(v)
        dx = strip_x + 30 + (i % 3) * 38
        s += circle(dx, yy, 5, col, col, 1)
        s += text(dx, yy - 9, f"{v:.1f}", 10.5, col, "middle", "bold")
        s += text(strip_x + strip_w + 70, yy + 4, f"{v:.1f} В  {verdict}", 11.5, col, "start", "bold")
    s += text(strip_x + strip_w / 2, top_y + 22, "зона «1»", 12, RED, "middle", "bold")
    s += text(strip_x + strip_w / 2, (vy(V_IH) + vy(V_IL)) / 2 + 4, "заборонено", 11, "#5a5a5a", "middle", "bold")
    s += text(strip_x + strip_w / 2, bot_y - 16, "зона «0»", 12, BLUE, "middle", "bold")
    s += rect(70, 444, W - 140, 0.1, "none", "none", 0)
    save("fig-14-2-2-range-not-point.svg", s)


# ── Рис. 14.2.3 — подорож логічної 1 дротом ─────────────────────────────────
def fig142_journey():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Подорож логічної «1»: вийшла при 3.0 В — дійшла при 2.4 В, та все ще «1»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "по дорозі сигнал втрачає напругу (опір дроту, наведення, шум), але лишається вище за VIH",
              12.5, GREY, "middle", style="italic")
    gx0, gx1 = 150, 720
    gy_bot, gy_top = 350, 90

    def vy(v):
        return gy_bot - (v / V_DD) * (gy_bot - gy_top)

    s = _vaxis(s, gx0, gy_top, gy_bot)
    s += text(gx0 - 10, vy(V_DD) + 4, "3.3", 11, GREY, "end")
    # драйвер і приймач
    s += rect(gx0 + 6, vy(V_OH) - 22, 70, 44, "#eef4ff", INK, 2, 6)
    s += text(gx0 + 41, vy(V_OH) - 2, "драйвер", 11, INK, "middle", "bold")
    s += rect(gx1 - 70, vy(2.4) - 22, 70, 44, "#eef4ff", INK, 2, 6)
    s += text(gx1 - 35, vy(2.4) - 2, "приймач", 11, INK, "middle", "bold")
    # рівні VOH, VIH
    s += line(gx0, vy(V_OH), gx1, vy(V_OH), RED, 1.2, "5 4")
    s += text(gx1 + 6, vy(V_OH) + 4, "VOH 3.0", 11, RED, "start", "bold")
    s += line(gx0, vy(V_IH), gx1, vy(V_IH), "#b06a1e", 1.6, "6 4")
    s += text(gx1 + 6, vy(V_IH) + 4, "VIH 2.3", 11, "#b06a1e", "start", "bold")
    # просідання сигналу з шумом
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        base = V_OH - 0.6 * t
        nz = 0.06 * math.sin(t * 26) + 0.04 * math.sin(t * 53 + 1)
        v = base + nz
        xx = gx0 + 80 + t * (gx1 - 80 - gx0)
        pts.append((xx, vy(v)))
    s += polyline(pts, GREEN, 2.4)
    s += text(gx0 + 90, vy(V_OH) - 14, "вийшло 3.0 В", 11.5, GREEN, "start", "bold")
    s += arrow((gx0 + gx1) / 2, vy(2.85), (gx0 + gx1) / 2, vy(2.55), AMBER, 2)
    s += text((gx0 + gx1) / 2 + 8, vy(2.7) + 4, "втрати + шум", 11.5, AMBER, "start", "bold")
    s += text(gx1 - 80, vy(2.4) - 30, "дійшло ≈ 2.4 В", 11.5, GREEN, "end", "bold")
    s += rect(70, 378, W - 140, 34, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 400, "Дійшло 2.4 В — усе ще вище за VIH 2.3 В, тож приймач упевнено читає «1». Скільки можна втратити — це запас (§14.3).",
              12, INK, "middle", "bold")
    save("fig-14-2-3-journey.svg", s)


# ── Рис. 14.2.4 — заборонена зона небезпечна ────────────────────────────────
def fig142_forbidden_danger():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому в забороненій зоні не можна затримуватися", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "поки вхід повзе між VIL і VIH, вихід приймача невизначений — смикається, дзвенить, гріється",
              12.5, GREY, "middle", style="italic")
    gx0, gx1 = 120, 760
    # ВХІД (повільний пандус)
    iy_b, iy_t = 200, 90

    def ivy(v):
        return iy_b - (v / V_DD) * (iy_b - iy_t)

    s += text(gx0, iy_t - 14, "ВХІД (повільно повзе вгору)", 13, INK, "start", "bold")
    s += rect(gx0, ivy(V_IH), gx1 - gx0, ivy(V_IL) - ivy(V_IH), "#ededed", "none", 0)
    s += line(gx0, ivy(V_IL), gx1, ivy(V_IL), BLUE, 1, "4 3")
    s += line(gx0, ivy(V_IH), gx1, ivy(V_IH), RED, 1, "4 3")
    s += text(gx1 + 4, ivy(V_IL) + 4, "VIL", 10, BLUE, "start", "bold")
    s += text(gx1 + 4, ivy(V_IH) + 4, "VIH", 10, RED, "start", "bold")
    s += polyline([(gx0, ivy(0.1)), (gx1, ivy(3.2))], INK, 2.4)
    # зона входу в забороненому
    zx0 = gx0 + (gx1 - gx0) * (V_IL / 3.1)
    zx1 = gx0 + (gx1 - gx0) * (V_IH / 3.1)
    s += line(zx0, iy_b, zx0, 250, GREY, 1, "3 3")
    s += line(zx1, iy_b, zx1, 250, GREY, 1, "3 3")
    # ВИХІД
    oy_b, oy_t = 360, 250

    def ovy(v):
        return oy_b - (v / V_DD) * (oy_b - oy_t)

    s += text(gx0, oy_t - 8, "ВИХІД приймача", 13, INK, "start", "bold")
    s += line(gx0, ovy(0), gx1, ovy(0), GREY, 1)
    # до зони — чистий 0; у зоні — осциляція; після — чистий 1
    pts = []
    N = 200
    for i in range(N + 1):
        x = gx0 + (gx1 - gx0) * i / N
        if x < zx0:
            v = 0.1
        elif x < zx1:
            v = 1.65 + 1.4 * math.sin((x - zx0) / 9.0)
        else:
            v = 3.2
        pts.append((x, ovy(v)))
    s += polyline(pts, RED, 2.4)
    s += rect(zx0, oy_t, zx1 - zx0, oy_b - oy_t, "#fff6f6", "#e7b7b7", 1.2)
    s += text((zx0 + zx1) / 2, oy_t + 16, "смикається / дзвенить", 11.5, RED, "middle", "bold")
    s += text(gx0 + 40, ovy(0) - 6, "чистий 0", 11, BLUE, "start", "bold")
    s += text(gx1 - 40, ovy(3.0), "чистий 1", 11, RED, "end", "bold")
    s += rect(70, 388, W - 140, 34, "#fbf6ec", AMBER, 1.6, 10)
    s += text(W / 2, 410, "Тому цифрові фронти роблять КРУТИМИ (§14.5), а де сигнал млявий — ставлять тригер Шмітта (§14.6).",
              12, INK, "middle", "bold")
    save("fig-14-2-4-forbidden-danger.svg", s)


# ── Рис. 14.2.5 — чому це смуги: розкид заліза ──────────────────────────────
def fig142_spread():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чому рівні задають як СМУГИ: розкид між чіпами, температурою, навантаженням", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "даташит не обіцяє точне число — він гарантує МЕЖУ: «1» не нижче VOH(min), «0» не вище VOL(max)",
              12.5, GREY, "middle", style="italic")
    gx0, gx1 = 110, 760
    top_y, bot_y = 90, 360

    def vy(v):
        return bot_y - (v / V_DD) * (bot_y - top_y)

    s = _vaxis(s, gx0, top_y, bot_y)
    s += text(gx0 - 10, vy(V_DD) + 4, "3.3", 11, GREY, "end")
    # гарантовані межі
    s += rect(gx0, top_y, gx1 - gx0, vy(V_OH) - top_y, "#fdf4f4", "none", 0)
    s += rect(gx0, vy(V_OL), gx1 - gx0, bot_y - vy(V_OL), "#f3f5fd", "none", 0)
    s += line(gx0, vy(V_OH), gx1, vy(V_OH), RED, 2)
    s += text(gx1 + 6, vy(V_OH) + 4, "VOH(min) 3.0", 11, RED, "start", "bold")
    s += line(gx0, vy(V_OL), gx1, vy(V_OL), BLUE, 2)
    s += text(gx1 + 6, vy(V_OL) + 4, "VOL(max) 0.3", 11, BLUE, "start", "bold")
    # хмари виміряних значень (детерміновано)
    for i in range(22):
        t = i / 21.0
        jx = gx0 + 70 + t * (gx1 - gx0 - 120)
        hv = 3.02 + 0.26 * (0.5 + 0.5 * math.sin(i * 2.3)) + 0.02 * math.sin(i * 7.0)
        if hv > 3.3:
            hv = 3.3
        s += circle(jx, vy(hv), 3.5, RED, RED, 1)
        lv = 0.28 - 0.26 * (0.5 + 0.5 * math.sin(i * 1.9 + 1)) - 0.02 * math.sin(i * 5.0)
        if lv < 0:
            lv = 0.02
        s += circle(jx, vy(lv), 3.5, BLUE, BLUE, 1)
    s += text((gx0 + gx1) / 2, vy(3.18), "реальні «1» різних чіпів — усі ВИЩЕ за VOH(min)", 11.5, RED, "middle", "bold")
    s += text((gx0 + gx1) / 2, vy(0.12), "реальні «0» — усі НИЖЧЕ за VOL(max)", 11.5, BLUE, "middle", "bold")
    s += rect(70, 378, W - 140, 34, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 400, "Точне значення «гуляє», та воно завжди по «правильний» бік межі — тому в розрахунок беруть саме межу.",
              12, INK, "middle", "bold")
    save("fig-14-2-5-spread.svg", s)


# ═══════════════════ §14.3 — Запас завадостійкості (noise margin) ════════════
ORANGE = "#b06a1e"   # пороги входу


# ── Рис. 14.3.1 — означення запасу: NMH і NML ───────────────────────────────
def fig143_margin_defined():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 34, "Запас завадостійкості = різниця між тим, що ДАЮТЬ, і тим, що ВИМАГАЮТЬ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "драйвер видає сигнал «з перестаранням», і ця надлишкова відстань до порога — і є запас",
              12.5, GREY, "middle", style="italic")
    top_y, bot_y = 100, 440

    def vy(v):
        return bot_y - (v / V_DD) * (bot_y - top_y)

    s = _vaxis(s, 150, top_y, bot_y)
    s += text(150 - 10, vy(V_DD) + 4, "3.3", 11, GREY, "end")
    sx0, sw = 232, 250
    s += rect(sx0, top_y, sw, vy(V_OH) - top_y, "#fdf4f4", "none", 0)
    s += rect(sx0, vy(V_OH), sw, vy(V_IH) - vy(V_OH), "#eafaef", "none", 0)
    s += rect(sx0, vy(V_IH), sw, vy(V_IL) - vy(V_IH), "#ededed", "none", 0)
    s += rect(sx0, vy(V_IL), sw, vy(V_OL) - vy(V_IL), "#eafaef", "none", 0)
    s += rect(sx0, vy(V_OL), sw, bot_y - vy(V_OL), "#f3f5fd", "none", 0)
    s += rect(sx0, top_y, sw, bot_y - top_y, "none", INK, 1.5)
    for v, col, lab, dash in ((V_OH, RED, "VOH 3.0", None), (V_IH, ORANGE, "VIH 2.3", "5 4"),
                              (V_IL, ORANGE, "VIL 1.0", "5 4"), (V_OL, BLUE, "VOL 0.3", None)):
        s += line(sx0, vy(v), sx0 + sw, vy(v), col, 1.8, dash)
        s += text(sx0 - 6, vy(v) + 4, lab, 11, col, "end", "bold")
    s += text(sx0 + sw / 2, (top_y + vy(V_OH)) / 2 + 4, "драйвер дає «1»", 11, RED, "middle", "bold")
    s += text(sx0 + sw / 2, (vy(V_OH) + vy(V_IH)) / 2 + 4, "NMH — запас «1»", 12, GREEN, "middle", "bold")
    s += text(sx0 + sw / 2, (vy(V_IH) + vy(V_IL)) / 2 + 4, "заборонено", 11, "#5a5a5a", "middle", "bold")
    s += text(sx0 + sw / 2, (vy(V_IL) + vy(V_OL)) / 2 + 4, "NML — запас «0»", 12, GREEN, "middle", "bold")
    s += text(sx0 + sw / 2, (vy(V_OL) + bot_y) / 2 + 4, "драйвер дає «0»", 11, BLUE, "middle", "bold")
    bx = sx0 + sw + 16
    for (va, vb) in ((V_OH, V_IH), (V_IL, V_OL)):
        s += line(bx, vy(va), bx, vy(vb), GREEN, 2.2)
        s += line(bx - 5, vy(va), bx + 5, vy(va), GREEN, 2.2)
        s += line(bx - 5, vy(vb), bx + 5, vy(vb), GREEN, 2.2)
        s += text(bx + 8, (vy(va) + vy(vb)) / 2 + 4, "0.7 В", 11, GREEN, "start", "bold")
    # формула
    fx = 612
    s += rect(fx, 120, 250, 250, "#f4f7f4", GREEN, 1.7, 12)
    s += text(fx + 125, 150, "Запас (noise margin)", 14, INK, "middle", "bold")
    s += text(fx + 18, 186, "NMH = VOH − VIH", 14, INK, "start", "bold")
    s += text(fx + 36, 208, "= 3.0 − 2.3 = 0.7 В", 13.5, GREEN, "start", "bold")
    s += text(fx + 18, 244, "NML = VIL − VOL", 14, INK, "start", "bold")
    s += text(fx + 36, 266, "= 1.0 − 0.3 = 0.7 В", 13.5, GREEN, "start", "bold")
    s += line(fx + 18, 286, fx + 232, 286, GREY, 1.2)
    s += text(fx + 18, 312, "стійкість лінії =", 13.5, INK, "start", "bold")
    s += text(fx + 36, 334, "min(NMH, NML) = 0.7 В", 14, INK, "start", "bold")
    s += text(fx + 18, 356, "найслабший бік вирішує", 11.5, GREY, "start", style="italic")
    save("fig-14-3-1-margin-defined.svg", s)


# ── Рис. 14.3.2 — запас як бюджет на негаразди ──────────────────────────────
def fig143_budget():
    W, H = 840, 450
    s = header(W, H)
    s += text(W / 2, 34, "Запас — це бюджет: усі негаразди «з'їдають» його разом", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "поки сума всіх завад менша за запас (0.7 В), лінія працює; коли перевищить — зрив",
              12.5, GREY, "middle", style="italic")
    bx0, bw = 300, 90
    base_y = 400
    scale = 380.0  # px на 1 В
    limit = 0.70
    segs = [("зсув землі", 0.20, BLUE), ("падіння I·R на дроті", 0.20, AMBER),
            ("перехресна завада", 0.15, COPPER), ("дзвін / відбиття", 0.10, GREY)]
    y = base_y
    total = 0.0
    for name, val, col in segs:
        h = val * scale
        s += rect(bx0, y - h, bw, h, col, "#ffffff", 1)
        s += text(bx0 - 12, y - h / 2 + 4, f"{val:.2f}", 11.5, col, "end", "bold")
        s += text(bx0 + bw + 12, y - h / 2 + 4, name, 12.5, INK, "start")
        y -= h
        total += val
    # залишок-подушка
    limit_y = base_y - limit * scale
    s += rect(bx0, limit_y, bw, y - limit_y, "#eafaef", GREEN, 1.4)
    s += text(bx0 + bw + 12, (y + limit_y) / 2 + 4, f"лишилось {limit - total:.2f} В", 12, GREEN, "start", "bold")
    # лінія межі
    s += line(bx0 - 30, limit_y, bx0 + bw + 30, limit_y, GREEN, 2, "6 4")
    s += text(bx0 - 36, limit_y + 4, "запас", 12, GREEN, "end", "bold")
    s += text(bx0 - 36, limit_y + 19, "0.70 В", 11.5, GREEN, "end", "bold")
    # вісь
    s += line(bx0, base_y, bx0 + bw, base_y, INK, 2)
    s += text(bx0 + bw / 2, base_y + 20, "сума завад", 12, INK, "middle", "bold")
    s += rect(70, 414, W - 140, 30, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 434, f"0.20 + 0.20 + 0.15 + 0.10 = 0.65 В  <  0.70 В  →  працює, та лишилось тільки 0.05 В.",
              12.5, INK, "middle", "bold")
    save("fig-14-3-2-budget.svg", s)


# ── Рис. 14.3.3 — вороги, що з'їдають запас ─────────────────────────────────
def fig143_enemies():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Хто з'їдає запас: карта завад між драйвером і приймачем", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна реальна неприємність відбирає кілька десятків мілівольтів — і всі вони складаються",
              12.5, GREY, "middle", style="italic")
    dy = 180
    dx0, dx1 = 150, 720
    # бокси
    s += rect(70, dy - 30, 90, 60, "#eef4ff", INK, 2, 8)
    s += text(115, dy + 5, "драйвер", 12.5, INK, "middle", "bold")
    s += rect(W - 160, dy - 30, 90, 60, "#eef4ff", INK, 2, 8)
    s += text(W - 115, dy + 5, "приймач", 12.5, INK, "middle", "bold")
    # сигнальний дріт з резистором
    s += line(160, dy - 12, 300, dy - 12, INK, 2.4)
    s += f'<path d="M 300,{dy-12} l 8,-7 l 12,14 l 12,-14 l 12,14 l 8,-7" fill="none" stroke="{AMBER}" stroke-width="2.4"/>\n'
    s += line(352, dy - 12, W - 160, dy - 12, INK, 2.4)
    s += text(326, dy - 24, "опір дроту → I·R", 11.5, AMBER, "middle", "bold")
    # земля з offset
    s += line(160, dy + 18, 360, dy + 18, INK, 2.4)
    s += battery(380, dy + 18, 0.7)
    s += line(400, dy + 18, W - 160, dy + 18, INK, 2.4)
    s += text(380, dy + 44, "зсув землі ΔV", 11.5, BLUE, "middle", "bold")
    s += text(W / 2, dy + 6, "GND", 10.5, GREY, "middle")
    # перехресна завада зверху
    s += line(200, dy - 80, W - 200, dy - 80, COPPER, 2)
    s += text(W / 2, dy - 88, "сусідній дріт, що перемикається", 11, COPPER, "middle", style="italic")
    for cxp in (430, 470, 510):
        s += line(cxp, dy - 76, cxp, dy - 16, COPPER, 1, "3 3")
    s += text(560, dy - 52, "ємнісна перехресна завада", 11.5, COPPER, "start", "bold")
    # просадка живлення
    s += arrow(115, dy - 30, 115, dy - 64, RED, 1.8)
    s += text(115, dy - 70, "просадка Vdd", 10.5, RED, "middle", "bold")
    # дзвін на вході
    s += polyline([(W - 175, dy - 12), (W - 170, dy - 22), (W - 166, dy - 4),
                   (W - 162, dy - 17), (W - 160, dy - 12)], RED, 1.8)
    s += text(W - 150, dy + 40, "дзвін/відбиття", 10.5, RED, "start", "bold")
    s += rect(70, 350, W - 140, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 374, "Усі ці завади додаються до сигналу вже ПІСЛЯ драйвера. Якщо їхня сума більша за запас —", 12, INK, "middle")
    s += text(W / 2, 393, "приймач провалюється в заборонену зону, і «1» може прочитатися як «0».", 12, INK, "middle", "bold")
    save("fig-14-3-3-enemies.svg", s)


# ── Рис. 14.3.4 — запас як відстань до обриву ───────────────────────────────
def fig143_cliff_distance():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Запас — це відстань до обриву з §14.1", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "поки сумарний шум лівіше за межу запасу — лінія працює ідеально; правіше — зрив",
              12.5, GREY, "middle", style="italic")
    ax0, ax1 = 110, 720
    ay = 170
    nmax = 1.0
    margin = 0.70
    cur = 0.45

    def nx(n):
        return ax0 + (n / nmax) * (ax1 - ax0)

    s += rect(ax0, ay - 18, nx(margin) - ax0, 36, "#eafaef", GREEN, 1.6)
    s += rect(nx(margin), ay - 18, ax1 - nx(margin), 36, "#fdecec", RED, 1.6)
    s += text((ax0 + nx(margin)) / 2, ay + 6, "працює (запас цілий)", 12.5, GREEN, "middle", "bold")
    s += text((nx(margin) + ax1) / 2, ay + 6, "ОБРИВ", 13, RED, "middle", "bold")
    for n in range(0, 11):
        x = nx(n / 10)
        s += line(x, ay + 18, x, ay + 24, GREY, 1.2)
        s += text(x, ay + 38, f"{n/10:.1f}", 9.5, GREY, "middle")
    s += text(ax1 / 2 + 130, ay + 56, "сумарний шум, В", 11.5, INK, "middle", "bold")
    # межа
    s += line(nx(margin), ay - 40, nx(margin), ay + 24, RED, 2, "5 4")
    s += text(nx(margin), ay - 46, "межа запасу 0.70 В", 11.5, RED, "middle", "bold")
    # поточний шум
    s += arrow(nx(cur), ay - 56, nx(cur), ay - 20, INK, 2.4)
    s += text(nx(cur), ay - 62, "зараз 0.45 В", 11.5, INK, "middle", "bold")
    # запас, що лишився
    s += line(nx(cur), ay + 60, nx(margin), ay + 60, GREEN, 2)
    s += line(nx(cur), ay + 55, nx(cur), ay + 65, GREEN, 2)
    s += line(nx(margin), ay + 55, nx(margin), ay + 65, GREEN, 2)
    s += text((nx(cur) + nx(margin)) / 2, ay + 80, "ще 0.25 В до обриву", 12, GREEN, "middle", "bold")
    save("fig-14-3-4-cliff-distance.svg", s)


# ── Рис. 14.3.5 — запас масштабується з живленням ───────────────────────────
def fig143_scale_vdd():
    W, H = 840, 440
    s = header(W, H)
    s += text(W / 2, 34, "Запас масштабується з живленням: нижча напруга — менший абсолютний запас", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "у КМОН запас порядку (0.25…0.3)·Vdd з кожного боку; ті самі мілівольти шуму небезпечніші при низькому Vdd",
              12.5, GREY, "middle", style="italic")
    top_y, bot_y = 100, 380
    maxv = 5.0
    bars = [(5.0, 230), (3.3, 460), (1.8, 690)]

    def vy(v, top, bot):
        return bot - (v / maxv) * (bot - top)

    for vdd, cx in bars:
        vol, vil, vih, voh = 0.0, 0.3 * vdd, 0.7 * vdd, vdd
        bw = 120
        x0 = cx - bw / 2
        s += rect(x0, vy(vdd, top_y, bot_y), bw, bot_y - vy(vdd, top_y, bot_y), "none", INK, 1.6)
        s += rect(x0, vy(voh, top_y, bot_y), bw, vy(vih, top_y, bot_y) - vy(voh, top_y, bot_y), "#eafaef", GREEN, 1.2)
        s += rect(x0, vy(vih, top_y, bot_y), bw, vy(vil, top_y, bot_y) - vy(vih, top_y, bot_y), "#ededed", "none", 0)
        s += rect(x0, vy(vil, top_y, bot_y), bw, vy(vol, top_y, bot_y) - vy(vil, top_y, bot_y), "#eafaef", GREEN, 1.2)
        s += text(cx, vy(vdd, top_y, bot_y) - 10, f"Vdd = {vdd} В", 13.5, INK, "middle", "bold")
        nm = 0.3 * vdd
        s += text(cx, (vy(voh, top_y, bot_y) + vy(vih, top_y, bot_y)) / 2 + 4, f"{nm:.2f} В", 12, GREEN, "middle", "bold")
        s += text(cx, (vy(vih, top_y, bot_y) + vy(vil, top_y, bot_y)) / 2 + 4, "заборон.", 10, "#5a5a5a", "middle")
        s += text(cx, (vy(vil, top_y, bot_y) + vy(vol, top_y, bot_y)) / 2 + 4, f"{nm:.2f} В", 12, GREEN, "middle", "bold")
        s += text(cx, bot_y + 20, f"запас ≈ {nm:.2f} В", 12, GREEN, "middle", "bold")
    # однаковий шум 0.4 В горизонталлю
    nz = 0.4
    yy = bot_y + 50
    s += rect(140, yy, 560, 22, "#fbf3e0", AMBER, 1.4)
    s += text(420, yy + 15, "той самий шум 0.4 В: при 5 В — дрібниця, при 1.8 В — майже весь запас", 12, INK, "middle", "bold")
    save("fig-14-3-5-scale-vdd.svg", s)


# ═══════════════ §14.4 — Логічні сімейства й рівні (TTL/CMOS) ════════════════
FAM = {
    "TTL5":  dict(vdd=5.0, vil=0.8, vih=2.0, vol=0.4, voh=2.4, name="5 В TTL"),
    "CMOS5": dict(vdd=5.0, vil=1.5, vih=3.5, vol=0.1, voh=4.9, name="5 В CMOS"),
    "LV33":  dict(vdd=3.3, vil=0.8, vih=2.0, vol=0.4, voh=3.0, name="3.3 В LVCMOS"),
}


# ── Рис. 14.4.1 — дві лінії: TTL (BJT) vs CMOS ──────────────────────────────
def fig144_ttl_vs_cmos():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дві великі лінії логіки: TTL (на BJT) і CMOS (на MOSFET-парах)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "сімейство — це домовленість про рівні й поведінку, щоб чипи розуміли одне одного",
              12.5, GREY, "middle", style="italic")

    def panel(x0, title, sub, rows, icon):
        out = rect(x0, 80, 370, 300, "none", INK, 1.8, 12)
        out += text(x0 + 185, 108, title, 16, INK, "middle", "bold")
        out += text(x0 + 185, 128, sub, 11.5, GREY, "middle", style="italic")
        icon(x0 + 60, 200)
        for i, t in enumerate(rows):
            yy = 168 + i * 30
            out += text(x0 + 130, yy, "•", 13, GREEN, "start", "bold")
            out += text(x0 + 146, yy, t, 12.5, INK, "start")
        return out

    def bjt_icon(cx, cy):
        nonlocal s
        s += line(cx - 18, cy, cx, cy, INK, 2)          # база
        s += line(cx, cy - 24, cx, cy + 24, INK, 3)     # вертикаль
        s += line(cx, cy - 12, cx + 22, cy - 28, INK, 2)  # колектор
        s += line(cx, cy + 12, cx + 22, cy + 28, INK, 2)  # емітер
        s += f'<path d="M {cx+14},{cy+22} l 8,6 l -2,-9 z" fill="{INK}"/>\n'
        s += circle(cx, cy, 30, "none", GREY, 1.4)
        s += text(cx, cy + 50, "BJT (§11)", 11, INK, "middle", "bold")

    def cmos_icon(cx, cy):
        nonlocal s
        s += line(cx, cy - 34, cx + 40, cy - 34, RED, 2)   # Vdd
        s += text(cx + 46, cy - 31, "Vdd", 9.5, RED, "start")
        s += rect(cx + 6, cy - 28, 28, 18, "#fdf4f4", RED, 1.6, 3)
        s += text(cx + 20, cy - 15, "P", 11, RED, "middle", "bold")
        s += rect(cx + 6, cy + 10, 28, 18, "#f3f5fd", BLUE, 1.6, 3)
        s += text(cx + 20, cy + 23, "N", 11, BLUE, "middle", "bold")
        s += line(cx + 20, cy - 10, cx + 20, cy + 10, INK, 2)
        s += line(cx + 20, cy, cx + 44, cy, INK, 2)
        s += text(cx + 48, cy + 3, "вих", 9.5, INK, "start")
        s += line(cx, cy + 38, cx + 40, cy + 38, INK, 2)   # GND
        s += text(cx + 46, cy + 41, "GND", 9.5, GREY, "start")
        s += text(cx + 20, cy + 58, "CMOS (§12)", 11, INK, "middle", "bold")

    s += panel(60, "TTL", "transistor-transistor logic",
               ["5 В; пороги несиметричні", "(VIL 0.8 / VIH 2.0 В)",
                "вхід СПОЖИВАЄ струм", "помітна статична потужність",
                "вхід «висить» ≈ як 1", "історично швидша"], bjt_icon)
    s += panel(450, "CMOS", "complementary MOS",
               ["вихід «до шин» (≈0 / ≈Vdd)", "пороги ≈ 0.3 / 0.7 Vdd",
                "майже нуль статичного струму", "вхід — величезний опір",
                "вхід НЕ МОЖНА лишати висіти", "працює в широкому Vdd"], cmos_icon)
    s += rect(70, 398, W - 140, 48, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 420, "Сьогодні майже вся логіка — CMOS (мала потужність, з §12.9). Але «TTL-рівні» лишилися",
              12.5, INK, "middle")
    s += text(W / 2, 438, "як поширений стандарт порогів, із яким досі звіряються на сумісність.", 12.5, INK, "middle", "bold")
    save("fig-14-4-1-ttl-vs-cmos.svg", s)


# ── Рис. 14.4.2 — драбина напруг живлення ───────────────────────────────────
def fig144_voltage_ladder():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 34, "Драбина напруг: чому логіка століттями «спускається»", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "нижче живлення → менше енергії (E ∝ C·V²), але менший абсолютний запас (§14.3)",
              12.5, GREY, "middle", style="italic")
    steps = [(5.0, "класика TTL/CMOS"), (3.3, "сучасний стандарт, ESP32"),
             (2.5, "ядра ПЛІС"), (1.8, "флеш, периферія"), (1.2, "ядра процесорів")]
    x0, y0 = 150, 130
    sw_, sh_ = 120, 46
    dx, dy = 120, 52
    for i, (v, note) in enumerate(steps):
        x = x0 + i * dx
        y = y0 + i * dy
        col = RED if i == 1 else INK
        s += rect(x, y, sw_, sh_, "#eef4ff" if i == 1 else "#fafafa", col, 2 if i == 1 else 1.6, 8)
        s += text(x + sw_ / 2, y + 22, f"{v} В", 16, col, "middle", "bold")
        s += text(x + sw_ / 2, y + 39, note, 10, GREY, "middle")
        if i < len(steps) - 1:
            s += arrow(x + sw_, y + sh_ / 2, x + dx, y + dy + sh_ / 2 - 6, GREY, 1.8)
    # стрілки-пояснення
    s += arrow(720, 150, 720, 360, GREEN, 2)
    s += text(732, 250, "↓ менше енергії", 12, GREEN, "start", "bold")
    s += text(732, 268, "↓ вища швидкість", 12, GREEN, "start")
    s += arrow(120, 360, 120, 150, AMBER, 2)
    s += text(108, 250, "↑ більший запас", 12, AMBER, "end", "bold")
    s += text(108, 268, "↑ простіше живити", 12, AMBER, "end")
    save("fig-14-4-2-voltage-ladder.svg", s)


# ── Рис. 14.4.3 — карти порогів трьох сімейств на спільній осі ──────────────
def fig144_threshold_maps():
    W, H = 880, 480
    s = header(W, H)
    s += text(W / 2, 34, "Карти рівнів трьох сімейств на спільній шкалі напруг", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "сумісність читається оком: трикутник VOH драйвера має дотягтися до низу червоної смуги «1» приймача",
              12, GREY, "middle", style="italic")
    maxv = 5.5
    top_y, bot_y = 100, 430

    def vy(v):
        return bot_y - (v / maxv) * (bot_y - top_y)

    s = _vaxis(s, 110, top_y, bot_y, vmax=maxv, ticks=(0, 1, 2, 3, 4, 5))
    cols = [("TTL5", 250), ("CMOS5", 470), ("LV33", 690)]
    bw = 120
    for key, cx in cols:
        f = FAM[key]
        x0 = cx - bw / 2
        # вхідні смуги
        s += rect(x0, top_y, bw, vy(f["vih"]) - top_y, "#fdf4f4", "none", 0)  # read-1 (до верху осі)
        s += rect(x0, vy(f["vih"]), bw, vy(f["vil"]) - vy(f["vih"]), "#ededed", "none", 0)
        s += rect(x0, vy(f["vil"]), bw, bot_y - vy(f["vil"]), "#f3f5fd", "none", 0)
        s += rect(x0, top_y, bw, bot_y - top_y, "none", INK, 1.4)
        # пороги входу
        s += line(x0, vy(f["vih"]), x0 + bw, vy(f["vih"]), RED, 1.6, "4 3")
        s += text(x0 + 4, vy(f["vih"]) - 4, f"VIH {f['vih']}", 10, RED, "start", "bold")
        s += line(x0, vy(f["vil"]), x0 + bw, vy(f["vil"]), BLUE, 1.6, "4 3")
        s += text(x0 + 4, vy(f["vil"]) + 12, f"VIL {f['vil']}", 10, BLUE, "start", "bold")
        # виходи — трикутники
        s += f'<path d="M {x0+bw+4},{vy(f["voh"])-6} l 12,6 l -12,6 z" fill="{RED}"/>\n'
        s += text(x0 + bw + 20, vy(f["voh"]) + 4, f"VOH {f['voh']}", 10, RED, "start", "bold")
        s += f'<path d="M {x0+bw+4},{vy(f["vol"])-6} l 12,6 l -12,6 z" fill="{BLUE}"/>\n'
        s += text(x0 + bw + 20, vy(f["vol"]) + 4, f"VOL {f['vol']}", 10, BLUE, "start", "bold")
        # Vdd
        s += line(x0, vy(f["vdd"]), x0 + bw, vy(f["vdd"]), GREY, 1.2)
        s += text(cx, top_y - 14, f["name"], 13, INK, "middle", "bold")
        s += text(cx, bot_y + 20, f"Vdd {f['vdd']} В", 11, GREY, "middle")
    s += text(160, top_y + 16, "червона смуга", 9.5, RED, "middle")
    s += text(160, top_y + 28, "= читається 1", 9.5, RED, "middle")
    save("fig-14-4-3-threshold-maps.svg", s)


# ── Рис. 14.4.4 — три випадки сумісності ────────────────────────────────────
def fig144_compat_cases():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Три класичні випадки стику сімейств", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "перевіряємо двома питаннями: ЛОГІЧНО (чи дотягує рівень) і ЕЛЕКТРИЧНО (чи не спалить перенапруга)",
              12, GREY, "middle", style="italic")

    def case(y, drv, rcv, ok, check, note):
        s2 = rect(60, y, W - 120, 96, "#f7fbf7" if ok else "#fdf6f6", GREEN if ok else RED, 1.6, 10)
        s2 += rect(90, y + 28, 150, 40, "#eef4ff", INK, 1.6, 6)
        s2 += text(165, y + 53, drv, 12.5, INK, "middle", "bold")
        s2 += arrow(248, y + 48, 330, y + 48, INK, 2.4)
        s2 += rect(338, y + 28, 150, 40, "#eef4ff", INK, 1.6, 6)
        s2 += text(413, y + 53, rcv, 12.5, INK, "middle", "bold")
        mark = "✓" if ok else "✗"
        s2 += text(520, y + 40, mark, 22, GREEN if ok else RED, "start", "bold")
        s2 += text(548, y + 36, check, 12.5, INK, "start", "bold")
        s2 += text(548, y + 58, note, 11.5, GREY, "start")
        return s2

    s += case(84, "3.3 В CMOS", "5 В TTL", True,
              "VOH 3.0 ≥ VIH 2.0  →  працює напряму",
              "улюблений збіг: 3.3-вольтовий вихід дотягує до TTL-порога")
    s += case(192, "3.3 В CMOS", "5 В CMOS", False,
              "VOH 3.0 < VIH 3.5  →  «1» не впізнається",
              "потрібен зсувач рівня ВГОРУ (або вхід із нижчим порогом)")
    s += case(300, "5 В (будь-яке)", "3.3 В вхід", False,
              "5 В > абс. макс 3.3-чипа  →  б'є струмом у захисний діод",
              "логічно дотягує, та ЕЛЕКТРИЧНО небезпечно: треба захист / 5V-tolerant")
    save("fig-14-4-4-compat-cases.svg", s)


# ── Рис. 14.4.5 — способи зсунути рівень ────────────────────────────────────
def fig144_level_shift():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Як подружити різні напруги: три типові рішення", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "від простого дільника до спеціального чипа — вибір за швидкістю й напрямком сигналу",
              12, GREY, "middle", style="italic")

    def box(x0, title):
        nonlocal s
        s += rect(x0, 84, 250, 240, "none", INK, 1.6, 12)
        s += text(x0 + 125, 110, title, 14, INK, "middle", "bold")

    # (a) зсувач-чип
    box(40, "Зсувач рівня (чип)")
    s += rect(110, 150, 110, 90, "#eef4ff", INK, 1.8, 8)
    s += text(165, 185, "level", 12, INK, "middle", "bold")
    s += text(165, 203, "shifter", 12, INK, "middle", "bold")
    s += line(70, 175, 110, 175, RED, 2)
    s += text(70, 168, "5 В", 10, RED, "start", "bold")
    s += line(220, 175, 260, 175, "#b06a1e", 2)
    s += text(248, 168, "3.3 В", 10, "#b06a1e", "start", "bold")
    s += text(165, 270, "двонапрямлений,", 11, GREY, "middle")
    s += text(165, 286, "найнадійніший", 11, GREY, "middle", "bold")

    # (b) резистивний дільник
    box(315, "Резистивний дільник")
    s += line(370, 140, 370, 180, INK, 2)
    s += text(370, 134, "5 В вхід", 10, RED, "middle", "bold")
    s += rect(360, 180, 20, 40, "none", INK, 1.6)
    s += text(345, 204, "R1", 10, INK, "end")
    s += line(370, 220, 370, 240, INK, 2)
    s += circle(370, 240, 3, INK, INK, 1)
    s += line(370, 240, 440, 240, "#b06a1e", 2)
    s += text(448, 243, "3.3 В", 10, "#b06a1e", "start", "bold")
    s += rect(360, 240, 20, 40, "none", INK, 1.6)
    s += text(345, 264, "R2", 10, INK, "end")
    s += line(370, 280, 370, 300, INK, 2)
    s += line(355, 300, 385, 300, INK, 2)
    s += text(370, 314, "лише вниз, повільні сигнали", 10, GREY, "middle")

    # (c) open-drain + pull-up
    box(590, "Відкритий стік + підтяжка")
    s += line(700, 130, 700, 150, RED, 2)
    s += text(700, 124, "3.3 В", 10, "#b06a1e", "middle", "bold")
    s += rect(690, 150, 20, 36, "none", INK, 1.6)
    s += text(672, 172, "R", 10, INK, "end")
    s += line(700, 186, 700, 210, INK, 2)
    s += circle(700, 210, 3, INK, INK, 1)
    s += line(700, 210, 760, 210, INK, 2)
    s += text(768, 213, "шина", 10, INK, "start")
    # транзистор-ключ донизу
    s += line(700, 210, 700, 250, INK, 2)
    s += rect(688, 250, 24, 28, "#f3f5fd", BLUE, 1.6, 3)
    s += text(700, 268, "N", 10, BLUE, "middle", "bold")
    s += line(700, 278, 700, 300, INK, 2)
    s += line(685, 300, 715, 300, INK, 2)
    s += text(700, 316, "тягне до 0; «1» дає підтяжка (§22)", 9.5, GREY, "middle")
    save("fig-14-4-5-level-shift.svg", s)


# ═══════════════ §14.5 — Фронти й час наростання ═════════════════════════════
def _exp_rise(x0, x1, y0v, y1v, tau_px, vy, N=120, falling=False):
    pts = []
    for i in range(N + 1):
        dx = (x1 - x0) * i / N
        frac = 1 - math.exp(-dx / tau_px)
        v = y0v + (y1v - y0v) * frac
        pts.append((x0 + dx, vy(v)))
    return pts


# ── Рис. 14.5.1 — ідеальний фронт проти реального ───────────────────────────
def fig145_ideal_vs_real():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чому фронт не миттєвий: напруга наростає за експонентою (RC)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "час наростання tr домовилися міряти від 10% до 90% розмаху — між цими рівнями сигнал «їде»",
              12.5, GREY, "middle", style="italic")
    gx0, gx1 = 120, 770
    gy_bot, gy_top = 340, 100
    Vdd = 3.3

    def vy(v):
        return gy_bot - (v / Vdd) * (gy_bot - gy_top)

    s += arrow(gx0, gy_bot, gx1 + 8, gy_bot, INK, 2)
    s += arrow(gx0, gy_bot, gx0, gy_top - 8, INK, 2)
    s += text(gx1 + 12, gy_bot + 18, "час", 12, INK, "start", "bold")
    s += text(gx0 - 8, gy_top - 12, "напруга", 12, INK, "middle", "bold")
    for v in (0, Vdd):
        s += line(gx0 - 4, vy(v), gx0, vy(v), GREY, 1.2)
    s += text(gx0 - 8, vy(0) + 4, "0", 11, GREY, "end")
    s += text(gx0 - 8, vy(Vdd) + 4, "Vdd", 11, GREY, "end")
    t0 = 250
    tau = 70
    # ідеальний крок
    s += line(t0, vy(0), t0, vy(Vdd), GREY, 1.6, "5 4")
    s += line(t0, vy(Vdd), gx1, vy(Vdd), GREY, 1.6, "5 4")
    s += text(t0 + 6, vy(Vdd) - 8, "ідеал (миттєво)", 11.5, GREY, "start", style="italic")
    # реальна експонента
    s += polyline(_exp_rise(t0, gx1, 0, Vdd, tau, vy), GREEN, 2.8)
    # рівні 10% / 90%
    v10, v90 = 0.1 * Vdd, 0.9 * Vdd
    x10 = t0 + tau * math.log(1 / 0.9)
    x90 = t0 + tau * math.log(1 / 0.1)
    for v, x, lab in ((v90, x90, "90%"), (v10, x10, "10%")):
        s += line(gx0, vy(v), x, vy(v), GREY, 1, "3 3")
        s += line(x, vy(v), x, gy_bot, GREY, 1, "3 3")
        s += text(gx0 + 4, vy(v) - 4, lab, 10.5, GREY, "start")
        s += circle(x, vy(v), 3.5, GREEN, GREEN, 1)
    # брекет tr
    by = gy_bot + 26
    s += line(x10, by, x90, by, RED, 2)
    s += line(x10, by - 5, x10, by + 5, RED, 2)
    s += line(x90, by - 5, x90, by + 5, RED, 2)
    s += text((x10 + x90) / 2, by + 18, "tr — час наростання (rise time)", 12, RED, "middle", "bold")
    s += text(620, vy(2.4), "спад tf — дзеркально", 11, GREY, "start", style="italic")
    save("fig-14-5-1-ideal-vs-real.svg", s)


# ── Рис. 14.5.2 — причина: драйвер R заряджає ємність C ──────────────────────
def fig145_rc_cause():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Звідки експонента: вихідний опір драйвера заряджає ємність вузла", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама RC-стала часу, що й у Розділі 7 — лише тепер це «паразит», який сповільнює логіку",
              12.5, GREY, "middle", style="italic")
    # схема зліва
    s += line(120, 110, 120, 140, RED, 2)
    s += text(120, 104, "Vdd", 11, RED, "middle", "bold")
    s += rect(108, 140, 24, 40, "none", INK, 1.6)
    s += text(92, 164, "Rout", 11, INK, "end", "bold")
    s += text(150, 164, "(опір драйвера)", 10.5, GREY, "start")
    s += line(120, 180, 120, 215, INK, 2)
    s += circle(120, 215, 3, INK, INK, 1)
    s += text(120, 232, "вузол (вихід)", 10.5, INK, "middle", "bold")
    s += line(120, 215, 260, 215, INK, 2)
    # конденсатор навантаження
    s += line(260, 215, 260, 250, INK, 2)
    s += line(245, 250, 275, 250, INK, 3)
    s += line(245, 260, 275, 260, INK, 3)
    s += line(260, 260, 260, 285, INK, 2)
    s += line(245, 285, 275, 285, INK, 2)
    s += text(286, 248, "C = затвор (§12.7)", 10.5, INK, "start", "bold")
    s += text(286, 264, "+ дріт + входи", 10.5, GREY, "start")
    # приймач (high-Z)
    s += rect(180, 195, 70, 40, "#eef4ff", INK, 1.6, 6)
    s += text(215, 219, "приймач", 10.5, INK, "middle")
    # крива справа
    gx0, gx1 = 470, 840
    gy_bot, gy_top = 330, 110
    Vdd = 3.3

    def vy(v):
        return gy_bot - (v / Vdd) * (gy_bot - gy_top)

    s += arrow(gx0, gy_bot, gx1 + 6, gy_bot, INK, 2)
    s += arrow(gx0, gy_bot, gx0, gy_top - 6, INK, 2)
    s += polyline(_exp_rise(gx0, gx1, 0, Vdd, 60, vy), GREEN, 2.8)
    s += line(gx0, vy(0.63 * Vdd), gx0 + 60, vy(0.63 * Vdd), GREY, 1, "3 3")
    s += line(gx0 + 60, vy(0), gx0 + 60, vy(0.63 * Vdd), GREY, 1, "3 3")
    s += text(gx0 + 64, vy(0.63 * Vdd) + 4, "63% за час τ", 10.5, GREY, "start")
    # формула
    s += rect(560, 120, 250, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(685, 146, "τ = Rout · C", 14, INK, "middle", "bold")
    s += text(685, 170, "tr ≈ 2.2 · τ", 14, INK, "middle", "bold")
    s += text(685, 196, "крутість (slew) = ΔV / tr", 12.5, INK, "middle", "bold")
    s += rect(70, 360, W - 140, 44, "#fbf6ec", AMBER, 1.6, 10)
    s += text(W / 2, 382, "Більший опір драйвера або більша ємність (довгий дріт, багато входів) → довша τ → млявіший фронт.", 12, INK, "middle", "bold")
    s += text(W / 2, 398, "Швидкий фронт = сильний драйвер (малий Rout) + мала ємність (короткі дроти).", 11.5, GREY, "middle")
    save("fig-14-5-2-rc-cause.svg", s)


# ── Рис. 14.5.3 — фронт і час у забороненій зоні ────────────────────────────
def fig145_dwell():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чому крутий фронт безпечніший: час у забороненій зоні", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "поки сигнал між VIL і VIH — вихід приймача невизначений (§14.2); крутий фронт проскакує цю зону вмить",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 120, 800
    gy_bot, gy_top = 340, 100
    Vdd = 3.3
    vil, vih = 1.0, 2.3

    def vy(v):
        return gy_bot - (v / Vdd) * (gy_bot - gy_top)

    s += arrow(gx0, gy_bot, gx1 + 6, gy_bot, INK, 2)
    s += arrow(gx0, gy_bot, gx0, gy_top - 6, INK, 2)
    s += text(gx1 + 10, gy_bot + 16, "час", 11.5, INK, "start", "bold")
    # заборонена смуга
    s += rect(gx0, vy(vih), gx1 - gx0, vy(vil) - vy(vih), "#ededed", "none", 0)
    s += line(gx0, vy(vih), gx1, vy(vih), RED, 1, "4 3")
    s += line(gx0, vy(vil), gx1, vy(vil), BLUE, 1, "4 3")
    s += text(gx1 + 4, vy(vih) + 4, "VIH", 10, RED, "start", "bold")
    s += text(gx1 + 4, vy(vil) + 4, "VIL", 10, BLUE, "start", "bold")
    # повільний фронт
    sx0 = 180
    s += polyline(_exp_rise(sx0, sx0 + 360, 0, Vdd, 150, vy), AMBER, 2.6)
    # час у зоні (повільний)
    def t_at(x0, tau, v):
        return x0 + tau * math.log(Vdd / (Vdd - v))
    a1, a2 = t_at(sx0, 150, vil), t_at(sx0, 150, vih)
    s += line(a1, gy_bot + 12, a2, gy_bot + 12, AMBER, 3)
    s += text((a1 + a2) / 2, gy_bot + 30, "довго в зоні — небезпечно", 11, AMBER, "middle", "bold")
    s += text(sx0 + 80, vy(2.7), "повільний фронт", 11, AMBER, "start", "bold")
    # крутий фронт
    fx0 = 560
    s += polyline(_exp_rise(fx0, fx0 + 80, 0, Vdd, 14, vy), GREEN, 2.8)
    b1, b2 = t_at(fx0, 14, vil), t_at(fx0, 14, vih)
    s += line(b1, gy_bot + 12, b2, gy_bot + 12, GREEN, 4)
    s += text((b1 + b2) / 2 + 10, gy_bot + 30, "мить", 11, GREEN, "start", "bold")
    s += text(fx0 + 20, vy(2.7), "крутий фронт", 11, GREEN, "start", "bold")
    save("fig-14-5-3-dwell.svg", s)


# ── Рис. 14.5.4 — затримка поширення проти часу наростання ──────────────────
def fig145_propagation():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 34, "Дві різні величини: затримка поширення tpd і час наростання tr", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "tpd — на скільки вихід ВІДСТАЄ (міряють по 50%); tr — наскільки сам фронт крутий. Це не одне й те саме",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 130, 800
    Vdd = 3.3

    def mkvy(b, t):
        return lambda v: b - (v / Vdd) * (b - t)

    # вхід
    ivy = mkvy(190, 100)
    s += text(70, 150, "ВХІД", 12.5, INK, "start", "bold")
    s += line(gx0, ivy(0), 300, ivy(0), INK, 2.4)
    s += polyline(_exp_rise(300, 340, 0, Vdd, 8, ivy), INK, 2.4)
    s += line(340, ivy(Vdd), gx1, ivy(Vdd), INK, 2.4)
    s += line(gx0, ivy(0.5 * Vdd), gx1, ivy(0.5 * Vdd), GREY, 1, "3 3")
    s += text(gx1 + 4, ivy(0.5 * Vdd) + 4, "50%", 10, GREY, "start")
    xin = 320
    s += circle(xin, ivy(0.5 * Vdd), 3.5, INK, INK, 1)
    # вихід
    ovy = mkvy(370, 280)
    s += text(70, 330, "ВИХІД", 12.5, INK, "start", "bold")
    s += line(gx0, ovy(0), 430, ovy(0), GREEN, 2.4)
    s += polyline(_exp_rise(430, 520, 0, Vdd, 22, ovy), GREEN, 2.6)
    s += line(520, ovy(Vdd), gx1, ovy(Vdd), GREEN, 2.4)
    s += line(gx0, ovy(0.5 * Vdd), gx1, ovy(0.5 * Vdd), GREY, 1, "3 3")
    xout = 430 + 22 * math.log(2)
    s += circle(xout, ovy(0.5 * Vdd), 3.5, GREEN, GREEN, 1)
    # tpd
    s += line(xin, ivy(0.5 * Vdd), xin, ovy(0.5 * Vdd) + 10, RED, 1.2, "4 3")
    s += line(xout, ivy(0.5 * Vdd), xout, ovy(0.5 * Vdd), RED, 1.2, "4 3")
    s += arrow(xin, 235, xout, 235, RED, 2)
    s += arrow(xout, 235, xin, 235, RED, 2)
    s += text((xin + xout) / 2, 228, "tpd (затримка 50%→50%)", 11.5, RED, "middle", "bold")
    # tr на виході
    o10 = 430 + 22 * math.log(1 / 0.9)
    o90 = 430 + 22 * math.log(1 / 0.1)
    s += line(o10, ovy(0) + 6, o90, ovy(0) + 6, COPPER, 2)
    s += text(o90 + 6, ovy(0) + 10, "tr виходу", 10.5, COPPER, "start", "bold")
    save("fig-14-5-4-propagation.svg", s)


# ── Рис. 14.5.5 — час наростання обмежує швидкість ──────────────────────────
def fig145_bitrate():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Фронт обмежує швидкість: коли період стає як tr, рівні «не встигають»", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "повільні фронти не дають сигналу дійти до шин — «око» закривається, 0 і 1 розмиваються",
              12, GREY, "middle", style="italic")
    Vdd = 3.3
    vil, vih = 1.0, 2.3

    def panel(y0, title, period, tau, col, ok):
        nonlocal s
        gx0, gx1 = 150, 800
        gy_bot, gy_top = y0 + 90, y0
        def vy(v):
            return gy_bot - (v / Vdd) * (gy_bot - gy_top)
        s += text(70, y0 + 50, title, 12, INK, "start", "bold")
        s += rect(gx0, vy(vih), gx1 - gx0, vy(vil) - vy(vih), "#f3f3f3", "none", 0)
        bits = [0, 1, 0, 1, 1, 0, 1, 0]
        pts = []
        x = gx0
        cur = 0.0
        for b in bits:
            target = Vdd if b else 0.0
            for i in range(24):
                t = i / 24.0 * period
                frac = 1 - math.exp(-t / tau)
                v = cur + (target - cur) * frac
                pts.append((x + t, vy(v)))
            cur = cur + (target - cur) * (1 - math.exp(-period / tau))
            x += period
        s += polyline(pts, col, 2.4)
        s += text(810, vy(vih) - 4, "VIH", 9, RED, "start")
        s += text(810, vy(vil) + 8, "VIL", 9, BLUE, "start")
        verdict = "око відкрите ✓" if ok else "око закрите ✗"
        s += text(770, y0 + 16, verdict, 11.5, GREEN if ok else RED, "end", "bold")
    panel(96, "період » tr (повільні дані)", 70, 8, GREEN, True)
    panel(250, "період ≈ tr (надто швидко)", 26, 14, RED, False)
    save("fig-14-5-5-bitrate.svg", s)


# ── Рис. 14.5.6 — золота середина крутості ──────────────────────────────────
def fig145_sweet_spot():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Золота середина: не надто повільно, не надто швидко", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "повільний фронт зависає в зоні й не дає швидкості; надто крутий — дзвенить, відбивається, світить завадою",
              12, GREY, "middle", style="italic")
    Vdd = 3.3

    def panel(cx, title, kind, col):
        nonlocal s
        gy_bot, gy_top = 320, 130
        def vy(v):
            return gy_bot - (v / Vdd) * (gy_bot - gy_top)
        x0 = cx - 110
        x1 = cx + 110
        s += rect(x0, gy_top - 10, 220, gy_bot - gy_top + 20, "none", FAINT, 1.5, 8)
        s += line(x0 + 10, vy(0), x1 - 10, vy(0), GREY, 1)
        if kind == "slow":
            s += polyline(_exp_rise(cx - 60, cx + 90, 0, Vdd, 70, vy), col, 2.6)
        elif kind == "good":
            s += polyline(_exp_rise(cx - 40, cx + 10, 0, Vdd, 12, vy), col, 2.8)
            s += line(cx + 10, vy(Vdd), x1 - 10, vy(Vdd), col, 2.8)
        else:  # fast with ringing
            s += polyline(_exp_rise(cx - 50, cx - 20, 0, Vdd, 6, vy), col, 2.8)
            rp = []
            for i in range(60):
                t = i / 6.0
                v = Vdd + 0.7 * math.exp(-t * 0.5) * math.cos(t * 2.2)
                rp.append((cx - 20 + i * 2.2, vy(min(v, 3.3 + 0.7))))
            s += polyline(rp, col, 2.4)
        s += text(cx, gy_top - 22, title, 13, col, "middle", "bold")
        return

    panel(180, "занадто повільно", "slow", AMBER)
    s += text(180, 348, "зависає в зоні,", 11, GREY, "middle")
    s += text(180, 363, "не клокнеш швидко", 11, GREY, "middle")
    panel(450, "у міру — добре", "good", GREEN)
    s += text(450, 348, "проскакує зону,", 11, GREY, "middle")
    s += text(450, 363, "тримає швидкість", 11, GREY, "middle")
    panel(720, "занадто швидко", "fast", RED)
    s += text(720, 348, "дзвін, викид, завада (EMI),", 11, GREY, "middle")
    s += text(720, 363, "відбиття (→ §41)", 11, GREY, "middle")
    save("fig-14-5-6-sweet-spot.svg", s)


# ═══════════════ §14.6 — Аналог→цифра на порозі (компаратор/Шмітт) ═══════════
def _comp_symbol(cx, cy, plus_top=True):
    out = (f'<path d="M {cx-46},{cy-42} L {cx-46},{cy+42} L {cx+52},{cy} Z" '
           f'fill="#fafafa" stroke="{INK}" stroke-width="2"/>\n')
    yp = cy - 20 if plus_top else cy + 20
    ym = cy + 20 if plus_top else cy - 20
    out += text(cx - 38, yp + 5, "+", 15, RED, "start", "bold")
    out += text(cx - 38, ym + 5, "−", 15, BLUE, "start", "bold")
    return out


def _noisy(t, k=0.0):
    return (0.55 * math.sin(t * 7.0 + k) + 0.3 * math.sin(t * 17.0 + 1.3 * k)
            + 0.18 * math.sin(t * 37.0 + 2.1))


# ── Рис. 14.6.1 — компаратор як 1-бітний перетворювач ───────────────────────
def fig146_comparator():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Найпростіший аналого-цифровий перетворювач — це компаратор (§13.7)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одне питання «вхід вище опорної напруги чи ні?» дає рівно 1 біт: чисту цифру з аналога",
              12.5, GREY, "middle", style="italic")
    # компаратор
    cx, cy = 175, 210
    s += _comp_symbol(cx, cy)
    s += line(cx - 100, cy - 20, cx - 46, cy - 20, INK, 2)
    s += text(cx - 104, cy - 16, "Vвх", 12, INK, "end", "bold")
    s += line(cx - 100, cy + 20, cx - 46, cy + 20, INK, 2)
    s += text(cx - 104, cy + 24, "Vref", 12, "#b06a1e", "end", "bold")
    s += line(cx + 52, cy, cx + 100, cy, INK, 2)
    s += text(cx + 104, cy + 4, "цифра", 12, GREEN, "start", "bold")
    s += text(cx, cy + 78, "вище Vref → 1", 11.5, INK, "middle", "bold")
    s += text(cx, cy + 94, "нижче → 0", 11.5, INK, "middle")
    # графіки
    gx0, gx1 = 360, 840
    Vdd = 3.3
    vref = 1.65

    def vy(v, b, t):
        return b - (v / Vdd) * (b - t)

    # верх: Vвх + Vref
    ty_b, ty_t = 200, 100
    s += text(gx0, 92, "вхід (аналог) і опорна напруга", 11.5, INK, "start", "bold")
    s += line(gx0, vy(vref, ty_b, ty_t), gx1, vy(vref, ty_b, ty_t), "#b06a1e", 1.6, "5 4")
    s += text(gx1 + 4, vy(vref, ty_b, ty_t) + 4, "Vref", 10, "#b06a1e", "start", "bold")
    pts = []
    N = 200
    for i in range(N + 1):
        t = i / N * 6.0
        v = 1.65 + 1.25 * math.sin(t * 1.1) + 0.12 * _noisy(t)
        v = max(0.05, min(Vdd - 0.05, v))
        pts.append((gx0 + (gx1 - gx0) * i / N, vy(v, ty_b, ty_t)))
    s += polyline(pts, INK, 2.2)
    # низ: цифровий вихід
    oy_b, oy_t = 340, 250
    s += text(gx0, 242, "цифровий вихід", 11.5, GREEN, "start", "bold")
    opts = []
    for i in range(N + 1):
        t = i / N * 6.0
        v = 1.65 + 1.25 * math.sin(t * 1.1) + 0.12 * _noisy(t)
        hi = v > vref
        opts.append((gx0 + (gx1 - gx0) * i / N, vy(Vdd if hi else 0, oy_b, oy_t)))
    s += polyline(opts, GREEN, 2.4)
    s += text(gx0 - 4, vy(Vdd, oy_b, oy_t) + 4, "1", 11, GREEN, "end", "bold")
    s += text(gx0 - 4, vy(0, oy_b, oy_t) + 4, "0", 11, GREEN, "end", "bold")
    save("fig-14-6-1-comparator.svg", s)


# ── Рис. 14.6.2 — один поріг + шум = дребезг ────────────────────────────────
def fig146_chatter():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Біда одного порога: біля нього шумний сигнал «дзвенить»", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "коли повільний зашумлений сигнал перетинає поріг, шум кидає його туди-сюди — купа хибних перемикань",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 110, 800
    Vdd = 3.3
    vth = 1.65

    def vy(v, b, t):
        return b - (v / Vdd) * (b - t)

    ty_b, ty_t = 210, 100
    s += line(gx0, vy(vth, ty_b, ty_t), gx1, vy(vth, ty_b, ty_t), "#b06a1e", 1.6, "5 4")
    s += text(gx1 + 4, vy(vth, ty_b, ty_t) + 4, "поріг", 10, "#b06a1e", "start", "bold")
    s += text(gx0, 92, "вхід: повільний наростаючий + шум", 11.5, INK, "start", "bold")
    N = 260
    raw = []
    for i in range(N + 1):
        t = i / N
        v = 0.4 + 2.4 * t + 0.22 * _noisy(t * 6.0)
        raw.append(v)
        raw[i] = max(0.05, min(Vdd - 0.05, v))
    pts = [(gx0 + (gx1 - gx0) * i / N, vy(raw[i], ty_b, ty_t)) for i in range(N + 1)]
    s += polyline(pts, INK, 2.0)
    # вихід — дребезг
    oy_b, oy_t = 360, 250
    s += text(gx0, 242, "вихід: хибні перемикання біля порога", 11.5, RED, "start", "bold")
    opts = [(gx0 + (gx1 - gx0) * i / N, vy(Vdd if raw[i] > vth else 0, oy_b, oy_t)) for i in range(N + 1)]
    s += polyline(opts, RED, 2.2)
    # підсвітити зону дребезгу
    s += rect(330, oy_t - 6, 150, (oy_b - oy_t) + 16, "#fff6f6", "#e7b7b7", 1.2)
    s += text(405, oy_b + 26, "дребезг!", 12, RED, "middle", "bold")
    save("fig-14-6-2-chatter.svg", s)


# ── Рис. 14.6.3 — гістерезис: два пороги все лікують ────────────────────────
def fig146_hysteresis_fix():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Ліки — гістерезис: два пороги замість одного", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "вихід стає 1 лише вище VT+, а 0 — лише нижче VT−; шум усередині смуги нічого не перемикає",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 110, 800
    Vdd = 3.3
    vtp, vtm = 2.0, 1.3

    def vy(v, b, t):
        return b - (v / Vdd) * (b - t)

    ty_b, ty_t = 210, 100
    s += rect(gx0, vy(vtp, ty_b, ty_t), gx1 - gx0, vy(vtm, ty_b, ty_t) - vy(vtp, ty_b, ty_t), "#eef7ee", "none", 0)
    s += line(gx0, vy(vtp, ty_b, ty_t), gx1, vy(vtp, ty_b, ty_t), RED, 1.4, "5 4")
    s += line(gx0, vy(vtm, ty_b, ty_t), gx1, vy(vtm, ty_b, ty_t), BLUE, 1.4, "5 4")
    s += text(gx1 + 4, vy(vtp, ty_b, ty_t) + 4, "VT+", 10, RED, "start", "bold")
    s += text(gx1 + 4, vy(vtm, ty_b, ty_t) + 4, "VT−", 10, BLUE, "start", "bold")
    s += text(gx0, 92, "той самий шумний вхід", 11.5, INK, "start", "bold")
    N = 260
    raw = []
    for i in range(N + 1):
        t = i / N
        v = 0.4 + 2.4 * t + 0.22 * _noisy(t * 6.0)
        raw.append(max(0.05, min(Vdd - 0.05, v)))
    pts = [(gx0 + (gx1 - gx0) * i / N, vy(raw[i], ty_b, ty_t)) for i in range(N + 1)]
    s += polyline(pts, INK, 2.0)
    # вихід з гістерезисом
    oy_b, oy_t = 360, 250
    s += text(gx0, 242, "вихід: одне чисте перемикання", 11.5, GREEN, "start", "bold")
    state = 0
    opts = []
    for i in range(N + 1):
        v = raw[i]
        if state == 0 and v > vtp:
            state = 1
        elif state == 1 and v < vtm:
            state = 0
        opts.append((gx0 + (gx1 - gx0) * i / N, vy(Vdd if state else 0, oy_b, oy_t)))
    s += polyline(opts, GREEN, 2.4)
    s += text(gx0 - 4, vy(Vdd, oy_b, oy_t) + 4, "1", 11, GREEN, "end", "bold")
    s += text(gx0 - 4, vy(0, oy_b, oy_t) + 4, "0", 11, GREEN, "end", "bold")
    save("fig-14-6-3-hysteresis-fix.svg", s)


# ── Рис. 14.6.4 — передавальна характеристика (петля гістерезису) ───────────
def fig146_transfer():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Передавальна характеристика тригера Шмітта: петля гістерезису", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "вихід залежить не лише від входу, а й від того, ЗВІДКИ прийшли — це «пам'ять» одного біта",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 130, 540
    gy_bot, gy_top = 350, 130
    Vdd = 3.3
    vtm, vtp = 1.2, 2.1

    def x(v):
        return gx0 + (v / Vdd) * (gx1 - gx0)

    s += arrow(gx0, gy_bot, gx1 + 16, gy_bot, INK, 2)
    s += arrow(gx0, gy_bot, gx0, gy_top - 12, INK, 2)
    s += text(gx1 + 20, gy_bot + 18, "вхід", 11.5, INK, "start", "bold")
    s += text(gx0 - 8, gy_top - 18, "вихід", 11.5, INK, "middle", "bold")
    s += text(gx0 - 8, gy_top + 4, "1", 11, GREEN, "end", "bold")
    s += text(gx0 - 8, gy_bot + 4, "0", 11, GREEN, "end", "bold")
    # петля
    s += line(gx0, gy_bot, x(vtp), gy_bot, GREEN, 2.6)            # низ (зростання)
    s += arrow((gx0 + x(vtp)) / 2 - 10, gy_bot, (gx0 + x(vtp)) / 2 + 10, gy_bot, GREEN, 2.6)
    s += line(x(vtp), gy_bot, x(vtp), gy_top, GREEN, 2.6)         # стрибок вгору
    s += arrow(x(vtp), (gy_bot + gy_top) / 2 + 10, x(vtp), (gy_bot + gy_top) / 2 - 10, GREEN, 2.6)
    s += line(x(vtp), gy_top, gx1, gy_top, GREEN, 2.6)            # верх праворуч
    s += line(x(vtm), gy_top, x(vtp), gy_top, GREEN, 2.6)         # верх (спадання)
    s += arrow((x(vtm) + x(vtp)) / 2 + 10, gy_top, (x(vtm) + x(vtp)) / 2 - 10, gy_top, GREEN, 2.6)
    s += line(x(vtm), gy_top, x(vtm), gy_bot, GREEN, 2.6)         # стрибок вниз
    s += arrow(x(vtm), (gy_bot + gy_top) / 2 - 10, x(vtm), (gy_bot + gy_top) / 2 + 10, GREEN, 2.6)
    # пороги
    for v, col, lab in ((vtm, BLUE, "VT−"), (vtp, RED, "VT+")):
        s += line(x(v), gy_bot, x(v), gy_bot + 6, col, 1.4)
        s += text(x(v), gy_bot + 20, lab, 11, col, "middle", "bold")
    s += line(x(vtm), gy_bot + 30, x(vtp), gy_bot + 30, INK, 1.6)
    s += line(x(vtm), gy_bot + 26, x(vtm), gy_bot + 34, INK, 1.6)
    s += line(x(vtp), gy_bot + 26, x(vtp), gy_bot + 34, INK, 1.6)
    s += text((x(vtm) + x(vtp)) / 2, gy_bot + 46, "гістерезис VH = VT+ − VT−", 11, INK, "middle", "bold")
    # символ Шмітта
    sx, sy = 700, 230
    s += f'<path d="M {sx-50},{sy-38} L {sx-50},{sy+38} L {sx+48},{sy} Z" fill="#fafafa" stroke="{INK}" stroke-width="2"/>\n'
    # гліф гістерезису всередині
    s += line(sx - 28, sy + 8, sx - 8, sy + 8, INK, 2)
    s += line(sx - 8, sy + 8, sx - 8, sy - 8, INK, 2)
    s += line(sx - 18, sy - 8, sx + 6, sy - 8, INK, 2)
    s += line(sx + 6, sy - 8, sx + 6, sy + 8, INK, 2)
    s += line(sx - 50, sy, sx - 84, sy, INK, 2)
    s += line(sx + 48, sy, sx + 82, sy, INK, 2)
    s += text(sx, sy + 70, "символ тригера Шмітта", 12, INK, "middle", "bold")
    s += text(sx, sy + 88, "(гліф петлі всередині буфера)", 11, GREY, "middle", style="italic")
    save("fig-14-6-4-transfer.svg", s)


# ── Рис. 14.6.5 — як зроблено: додатний зворотний зв'язок ───────────────────
def fig146_feedback():
    W, H = 880, 410
    s = header(W, H)
    s += text(W / 2, 34, "Як зроблено гістерезис: додатний зворотний зв'язок зсуває поріг (§13.8)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "частинка виходу повертається на вхід і сама рухає опорну напругу — поріг «тікає» від сигналу",
              12, GREY, "middle", style="italic")

    def state(x0, out_hi, label, vt_lbl):
        nonlocal s
        cx, cy = x0 + 120, 210
        s += _comp_symbol(cx, cy)
        s += line(cx - 110, cy - 20, cx - 46, cy - 20, INK, 2)
        s += text(cx - 114, cy - 16, "Vвх", 11.5, INK, "end", "bold")
        # вихід
        ocol = GREEN if out_hi else GREY
        s += line(cx + 52, cy, cx + 96, cy, ocol, 2.4)
        s += text(cx + 100, cy + 4, "1" if out_hi else "0", 13, ocol, "start", "bold")
        # ЗЗ на + вхід
        s += line(cx + 74, cy, cx + 74, cy + 70, ocol, 2)
        s += line(cx + 74, cy + 70, cx - 70, cy + 70, ocol, 2)
        s += line(cx - 70, cy + 70, cx - 70, cy + 20, ocol, 2)
        s += line(cx - 70, cy + 20, cx - 46, cy + 20, ocol, 2)
        s += rect(cx - 6, cy + 62, 24, 16, "#fafafa", ocol, 1.4)
        s += text(cx + 6, cy + 100, "R зв'язку", 10.5, GREY, "middle")
        s += text(cx, cy - 70, label, 12.5, INK, "middle", "bold")
        s += text(cx, cy - 52, vt_lbl, 12, (RED if out_hi else BLUE), "middle", "bold")
        return

    state(40, False, "вихід = 0 (чекає на «1»)", "поріг піднятий до VT+ (2.0 В)")
    state(470, True, "вихід = 1 (чекає на «0»)", "поріг опущений до VT− (1.3 В)")
    s += rect(70, 348, W - 140, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 372, "Поріг сам «тікає» від сигналу: щойно перемкнулися — наступний поріг далі, тож шум уже не дістає. Це і є петля.",
              12, INK, "middle", "bold")
    save("fig-14-6-5-feedback.svg", s)


# ── Рис. 14.6.6 — застосування: «загострити» млявий сигнал ──────────────────
def fig146_squareup():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Застосування: перетворити млявий зашумлений сигнал на чисту цифру", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "тригер Шмітта «загострює» повільні фронти (§14.5) і вбиває дребезг — звідси й позначка на входах МК",
              12, GREY, "middle", style="italic")
    Vdd = 3.3
    vtp, vtm = 2.1, 1.2

    def vy(v, b, t):
        return b - (v / Vdd) * (b - t)

    gx0, gx1 = 110, 560
    # вхід — повільна зашумлена синусоїда
    ty_b, ty_t = 200, 100
    s += text(gx0, 92, "вхід: повільна, зашумлена", 11.5, INK, "start", "bold")
    s += rect(gx0, vy(vtp, ty_b, ty_t), gx1 - gx0, vy(vtm, ty_b, ty_t) - vy(vtp, ty_b, ty_t), "#eef7ee", "none", 0)
    s += line(gx0, vy(vtp, ty_b, ty_t), gx1, vy(vtp, ty_b, ty_t), RED, 1.2, "5 4")
    s += line(gx0, vy(vtm, ty_b, ty_t), gx1, vy(vtm, ty_b, ty_t), BLUE, 1.2, "5 4")
    N = 240
    raw = []
    for i in range(N + 1):
        t = i / N * 6.28
        v = 1.65 + 1.15 * math.sin(t) + 0.18 * _noisy(t * 2.0)
        raw.append(max(0.05, min(Vdd - 0.05, v)))
    s += polyline([(gx0 + (gx1 - gx0) * i / N, vy(raw[i], ty_b, ty_t)) for i in range(N + 1)], INK, 2.0)
    # Шмітт-блок
    sx = 610
    s += f'<path d="M {sx},150 L {sx},230 L {sx+70},190 Z" fill="#fafafa" stroke="{INK}" stroke-width="2"/>\n'
    s += line(sx + 14, 198, sx + 30, 198, INK, 1.8)
    s += line(sx + 30, 198, sx + 30, 182, INK, 1.8)
    s += line(sx + 22, 182, sx + 42, 182, INK, 1.8)
    s += line(sx + 42, 182, sx + 42, 198, INK, 1.8)
    s += arrow(sx - 40, 190, sx, 190, INK, 2)
    s += text(sx + 35, 250, "Шмітт", 11.5, INK, "middle", "bold")
    # вихід — чистий меандр
    ox0, ox1 = 700, 850
    s += text(ox0 - 10, 92, "чистий вихід", 11.5, GREEN, "start", "bold")
    state = 0
    opts = []
    for i in range(N + 1):
        v = raw[i]
        if state == 0 and v > vtp:
            state = 1
        elif state == 1 and v < vtm:
            state = 0
        opts.append((ox0 + (ox1 - ox0) * i / N, vy(Vdd if state else 0, ty_b + 0, ty_t + 0)))
    s += polyline(opts, GREEN, 2.6)
    s += text(ox0 - 6, vy(Vdd, ty_b, ty_t) + 4, "1", 10.5, GREEN, "end", "bold")
    s += text(ox0 - 6, vy(0, ty_b, ty_t) + 4, "0", 10.5, GREEN, "end", "bold")
    s += rect(70, 300, W - 140, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 326, "Один компаратор із гістерезисом перетворює будь-що аналогове на чисту, без-дребезгу цифру.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 348, "Саме так аналоговий світ Модулів 1–2 «заходить» у цифровий світ Модуля 3 — крізь поріг.", 12, INK, "middle")
    s += text(W / 2, 372, "Тому на схемах входи з позначкою-петлею (Шмітт) ставлять там, де сигнал млявий: кнопки, давачі, довгі лінії.", 11.5, GREY, "middle", style="italic")
    save("fig-14-6-6-squareup.svg", s)


if __name__ == "__main__":
    # історія розділу (§14.0)
    fig_timeline()
    fig_shannon_map()
    fig_noise()
    # §14.1
    fig141_two_languages()
    fig141_decision()
    fig141_generations()
    fig141_why_two()
    fig141_cliff()
    fig141_balance()
    # §14.2
    fig142_band_diagram()
    fig142_range_not_point()
    fig142_journey()
    fig142_forbidden_danger()
    fig142_spread()
    # §14.3
    fig143_margin_defined()
    fig143_budget()
    fig143_enemies()
    fig143_cliff_distance()
    fig143_scale_vdd()
    # §14.4
    fig144_ttl_vs_cmos()
    fig144_voltage_ladder()
    fig144_threshold_maps()
    fig144_compat_cases()
    fig144_level_shift()
    # §14.5
    fig145_ideal_vs_real()
    fig145_rc_cause()
    fig145_dwell()
    fig145_propagation()
    fig145_bitrate()
    fig145_sweet_spot()
    # §14.6
    fig146_comparator()
    fig146_chatter()
    fig146_hysteresis_fix()
    fig146_transfer()
    fig146_feedback()
    fig146_squareup()
    print("ch14 figures done.")
