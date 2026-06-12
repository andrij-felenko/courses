# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для математичної вставки §3.4.3m
«Арифметика за модулем: доповняльний код — це залишки mod 2ⁿ».

Окремий скрипт (головний figs.py розділу не чіпаємо). Чистий Python без
залежностей. Вивід → ./img/. Імена файлів: fig-17-3m-<k>-*.svg, підписи у
тексті — «Рис. 3.4.3m.k».

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «поле/виділення»
зелене; стрілки через marker; шрифт sans-serif.
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
VIOLET = "#6a3da8"
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
        f'  <marker id="aViolet" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOLET}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", VIOLET: "aViolet"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def curve(x1, y1, cx, cy, x2, y2, color=INK, w=2, dash=None, arrow_end=True):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{_MARK.get(color, "aInk")})"' if arrow_end else ""
    return (f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d}{m}/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.4.3m.1 — класи лишків mod 8: пряма «складається» у 8 кошиків ──────
def fig_classes():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 36, "Класи лишків за модулем 8: числова пряма «складається» у 8 кошиків",
              20, INK, "middle", "bold")
    s += text(W / 2, 58, "усі цілі з однаковим залишком від ділення на 8 — це одне й те саме за модулем 8",
              12.5, GREY, "middle", style="italic")

    # верхня числова пряма 0..23 з мітками
    y0 = 110
    x_lo, x_hi = 70, W - 40
    n = 24
    step = (x_hi - x_lo) / (n - 1)
    s += line(x_lo - 12, y0, x_hi + 12, y0, INK, 2)
    s += arrow(x_hi + 12, y0, x_hi + 30, y0, INK, 2)
    pal = [BLUE, "#2f6fd0", GREEN, "#3a9b55", AMBER, "#d08a2a", RED, VIOLET]
    for k in range(n):
        x = x_lo + k * step
        r = k % 8
        c = pal[r]
        s += circle(x, y0, 4.2, c, c, 1)
        s += text(x, y0 - 12, str(k), 11.5, c, "middle", "bold" if r == 5 else "normal")
        # підкреслимо приклад r=5: 5,13,21
        if r == 5:
            s += circle(x, y0, 8.5, "none", RED, 2)

    s += text(x_lo - 16, y0 + 22, "…", 14, GREY, "middle")
    # пояснення прикладу 5
    s += text(W / 2, y0 + 40, "приклад: 5, 13, 21 — усі дають залишок 5  →  5 ≡ 13 ≡ 21 (mod 8)",
              13, RED, "middle", "bold")

    # «складання» — стрілки вниз у 8 кошиків
    by = 300
    cw = (x_hi - x_lo - 7 * 10) / 8
    bx0 = x_lo
    boxes = []
    for r in range(8):
        bx = bx0 + r * (cw + 10)
        boxes.append((bx, bx + cw))
        c = pal[r]
        s += rect(bx, by, cw, 150, "#fbfbff", c, 2, 8)
        s += text(bx + cw / 2, by - 10, f"клас {r}", 13, c, "middle", "bold")
        # члени класу
        members = [r + 8 * j for j in range(3)]
        for j, mv in enumerate(members):
            s += text(bx + cw / 2, by + 34 + j * 30, str(mv), 14.5, c, "middle",
                      "bold" if j == 0 else "normal")
        s += text(bx + cw / 2, by + 150 - 12, "+8 →", 10.5, GREY, "middle", style="italic")

    # стрілки від прямої до кошиків (кілька показових)
    for k in [0, 1, 5, 8, 13, 21]:
        x = x_lo + k * step
        r = k % 8
        bx = (boxes[r][0] + boxes[r][1]) / 2
        s += curve(x, y0 + 12, (x + bx) / 2, (y0 + by) / 2 + 20, bx, by - 26,
                   pal[r], 1.6, dash="4,4")

    # підсумок-рамка
    s += rect(W / 2 - 330, 480, 660, 56, "#f3f8f3", GREEN, 2, 10)
    s += text(W / 2, 503, "Z розпадається рівно на 8 непересічних класів: {0,1,2,3,4,5,6,7}.",
              13.5, INK, "middle", "bold")
    s += text(W / 2, 523, "Лишити число «за модулем 8» = знайти, у якому кошику воно лежить.",
              12.5, GREY, "middle")
    save("fig-17-3m-1-classes.svg", s)


# ── Рис. 3.4.3m.2 — годинник mod 12: 15 ≡ 3, −1 ≡ 11 ────────────────────────
def fig_clock():
    W, H = 900, 540
    s = header(W, H)
    s += text(W / 2, 34, "Годинник — це арифметика за модулем 12",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "«третя» і «п'ятнадцята» — той самий кут стрілки: 15 ≡ 3 (mod 12)",
              12.5, GREY, "middle", style="italic")

    cx, cy, R = 250, 300, 165
    s += circle(cx, cy, R, "#fcfcff", INK, 2.5)
    for h in range(12):
        ang = math.radians(-90 + h * 30)
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        xt = cx + (R - 26) * math.cos(ang)
        yt = cy + (R - 26) * math.sin(ang)
        s += line(x, y, cx + (R - 10) * math.cos(ang), cy + (R - 10) * math.sin(ang), GREY, 1.5)
        lbl = "12" if h == 0 else str(h)
        col = INK
        wt = "normal"
        if h == 3:
            col, wt = GREEN, "bold"
        if h == 11:
            col, wt = RED, "bold"
        s += text(xt, yt + 5, lbl, 16 if wt == "bold" else 14, col, "middle", wt)
    s += circle(cx, cy, 4, INK, INK, 1)

    # стрілка на 3 (зелена) і «крок назад» на 11 (червона)
    a3 = math.radians(-90 + 3 * 30)
    s += arrow(cx, cy, cx + (R - 40) * math.cos(a3), cy + (R - 40) * math.sin(a3), GREEN, 3)
    a11 = math.radians(-90 + 11 * 30)
    s += arrow(cx, cy, cx + (R - 40) * math.cos(a11), cy + (R - 40) * math.sin(a11), RED, 3)
    # дуга «+12»
    s += text(cx, cy + R + 34, "повний оберт = +12 → нічого не змінює",
              12.5, GREY, "middle", style="italic")

    # права колонка: рівняння
    bx = 540
    s += text(bx, 130, "Те саме мовою лишків:", 15, INK, "start", "bold")
    rows = [
        ("15 год = 3 год", "15 = 1·12 + 3", "15 ≡ 3 (mod 12)", GREEN),
        ("27 год = 3 год", "27 = 2·12 + 3", "27 ≡ 3 (mod 12)", GREEN),
        ("«за годину до 12»", "−1 = (−1)·12 + 11", "−1 ≡ 11 (mod 12)", RED),
        ("«дві години тому»", "−2 = (−1)·12 + 10", "−2 ≡ 10 (mod 12)", RED),
    ]
    yy = 168
    for human, calc, cong, c in rows:
        s += text(bx, yy, human, 13.5, INK, "start", "bold")
        s += text(bx + 8, yy + 22, calc, 13, GREY, "start")
        s += text(bx + 8, yy + 44, cong, 14.5, c, "start", "bold")
        yy += 78

    s += rect(bx - 10, 470, 350, 50, "#f3f5fb", BLUE, 2, 10)
    s += text(bx + 165, 491, "Від'ємне число має додатного «двійника»",
              12.5, INK, "middle", "bold")
    s += text(bx + 165, 509, "у тому самому колі: −1 ↔ 11.  Це — ключ до §3.4.3.",
              11.5, GREY, "middle")
    save("fig-17-3m-2-clock.svg", s)


# ── Рис. 3.4.3m.3 — коректність: звести-потім-додати = додати-потім-звести ───
def fig_welldefined():
    W, H = 900, 540
    s = header(W, H)
    s += text(W / 2, 34, "Чому за модулем можна спокійно рахувати: операції «не плутають» класи",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "приклад mod 8: однакова відповідь, хоч зводь спершу, хоч наприкінці",
              12.5, GREY, "middle", style="italic")

    # дві стежки до одного результату (комутативна діаграма)
    # верхня: 13 + 14 -> 27 -> (mod 8) 3
    # нижня:  5  + 6  -> 11 -> (mod 8) 3
    x1, x2, x3 = 130, 430, 720
    yT, yB = 150, 360
    box_w, box_h = 150, 56

    def node(x, y, top, bot, c):
        out = rect(x - box_w / 2, y - box_h / 2, box_w, box_h, "#fcfcff", c, 2, 9)
        out += text(x, y - 4, top, 15, c, "middle", "bold")
        out += text(x, y + 17, bot, 11.5, GREY, "middle")
        return out

    # верхня стежка (сирі числа)
    s += node(x1, yT, "13 + 14", "сирі числа", INK)
    s += node(x2, yT, "= 27", "сума", INK)
    s += node(x3, yT, "27 mod 8 = 3", "лишок наприкінці", GREEN)
    s += arrow(x1 + box_w / 2, yT, x2 - box_w / 2, yT, INK, 2)
    s += arrow(x2 + box_w / 2, yT, x3 - box_w / 2, yT, GREEN, 2.4)
    s += text((x1 + x2) / 2, yT - 36, "+", 14, INK, "middle", "bold")

    # нижня стежка (спершу звели)
    s += node(x1, yB, "5 + 6", "13≡5, 14≡6", BLUE)
    s += node(x2, yB, "= 11", "сума малих", BLUE)
    s += node(x3, yB, "11 mod 8 = 3", "лишок наприкінці", GREEN)
    s += arrow(x1 + box_w / 2, yB, x2 - box_w / 2, yB, BLUE, 2)
    s += arrow(x2 + box_w / 2, yB, x3 - box_w / 2, yB, GREEN, 2.4)
    s += text((x1 + x2) / 2, yB - 36, "+", 14, BLUE, "middle", "bold")

    # вертикальні зв'язки «звести спершу»
    s += curve(x1, yT + box_h / 2, x1 - 70, (yT + yB) / 2, x1, yB - box_h / 2,
               VIOLET, 2, dash="5,4")
    s += text(x1 - 96, (yT + yB) / 2, "звели", 12.5, VIOLET, "middle", "bold")
    s += text(x1 - 96, (yT + yB) / 2 + 17, "спершу", 12.5, VIOLET, "middle")

    # результати збігаються
    s += curve(x3, yT + box_h / 2, x3 + 78, (yT + yB) / 2, x3, yB - box_h / 2,
               GREEN, 2, dash="5,4", arrow_end=False)
    s += text(x3 + 96, (yT + yB) / 2, "однаково!", 13, GREEN, "middle", "bold")
    s += text(x3 + 96, (yT + yB) / 2 + 17, "= 3", 13, GREEN, "middle", "bold")

    # підсумок
    s += rect(W / 2 - 360, 452, 720, 64, "#f3f8f3", GREEN, 2, 10)
    s += text(W / 2, 476, "(a + b) mod m = ((a mod m) + (b mod m)) mod m   — і так само для «−» та «×».",
              14, INK, "middle", "bold")
    s += text(W / 2, 499, "Тому залізо вільне рахувати лише n молодшими бітами: «зайве» можна викидати будь-коли.",
              12, GREY, "middle")
    save("fig-17-3m-3-welldefined.svg", s)


# ── Рис. 3.4.3m.4 — міст: доповняльний код = представники класів mod 2ⁿ ──────
def fig_twoscomp():
    W, H = 900, 580
    s = header(W, H)
    s += text(W / 2, 34, "Доповняльний код — це вибір представника в кожному класі mod 2ⁿ",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "8 бітів → модуль 256; з кожної пари «двійників» беремо того, що ближчий до нуля",
              12.5, GREY, "middle", style="italic")

    # числова пряма −5 ... показ 251 і −5 як один клас mod 256
    yL = 150
    s += text(70, yL - 26, "Один клас за модулем 256:", 14, INK, "start", "bold")
    pts = [("−261", GREY), ("−5", RED), ("251", RED), ("507", GREY)]
    xs = [150, 360, 560, 770]
    s += line(90, yL, 840, yL, INK, 2)
    s += arrow(840, yL, 858, yL, INK, 2)
    s += arrow(90, yL, 72, yL, INK, 2)
    for (lbl, c), x in zip(pts, xs):
        s += circle(x, yL, 5, c, c, 1)
        s += text(x, yL - 14, lbl, 14, c, "middle", "bold" if c == RED else "normal")
    # дуги +256 між сусідами
    for i in range(3):
        xa, xb = xs[i], xs[i + 1]
        s += curve(xa, yL + 8, (xa + xb) / 2, yL + 52, xb, yL + 8, VIOLET, 1.8,
                   dash="5,4")
        s += text((xa + xb) / 2, yL + 50, "+256", 11, VIOLET, "middle", "bold")
    s += text(W / 2, yL + 78, "−5 ≡ 251 (mod 256):  той самий клас, той самий бітовий запис 11111011",
              13, RED, "middle", "bold")

    # коло 4-бітне: представники доповняльного коду
    cx, cy, R = 250, 410, 120
    s += circle(cx, cy, R, "#fcfcff", INK, 2)
    for v in range(16):
        ang = math.radians(-90 + v * 22.5)
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        s += circle(x, y, 3.2, INK, INK, 1)
        signed = v if v < 8 else v - 16
        c = BLUE if v < 8 else RED
        xt = cx + (R + 22) * math.cos(ang)
        yt = cy + (R + 22) * math.sin(ang)
        s += text(xt, yt + 4, f"{v}", 11, GREY, "middle")
        xs2 = cx + (R - 22) * math.cos(ang)
        ys2 = cy + (R - 22) * math.sin(ang)
        s += text(xs2, ys2 + 4, f"{signed:+d}".replace("+0", "0"), 11.5, c, "middle",
                  "bold")
    s += text(cx, cy - 4, "mod 16", 13, INK, "middle", "bold")
    s += text(cx, cy + 15, "(4 біти)", 11, GREY, "middle")
    s += text(cx, cy + R + 44, "сині = верхній представник (0…7),  червоні = «довертаємо» вниз (−8…−1)",
              11.5, GREY, "middle", style="italic")

    # права колонка: словник «клас → представник»
    bx = 540
    s += text(bx, 300, "Словник класів (8 біт, mod 256):", 14, INK, "start", "bold")
    rows = [
        ("клас 0", "0", "0", BLUE),
        ("клас 1", "1", "+1", BLUE),
        ("клас 127", "127", "+127", BLUE),
        ("клас 128", "128", "−128", RED),
        ("клас 251", "251", "−5", RED),
        ("клас 255", "255", "−1", RED),
    ]
    yy = 330
    s += text(bx, yy - 6, "клас", 11.5, GREY, "start")
    s += text(bx + 120, yy - 6, "беззнак.", 11.5, GREY, "start")
    s += text(bx + 230, yy - 6, "доповн. код", 11.5, GREY, "start")
    for name, u, sg, c in rows:
        s += text(bx, yy + 14, name, 12.5, INK, "start")
        s += text(bx + 120, yy + 14, u, 12.5, BLUE, "start", "bold")
        s += text(bx + 230, yy + 14, sg, 12.5, c, "start", "bold")
        yy += 26
    s += rect(bx - 6, yy + 4, 330, 46, "#f3f8f3", GREEN, 2, 9)
    s += text(bx + 159, yy + 23, "Біти ті самі — різниться лише, який", 11.5, INK, "middle", "bold")
    s += text(bx + 159, yy + 40, "представник класу ми «називаємо» (§3.4.1).", 11, GREY, "middle")
    save("fig-17-3m-4-twoscomp.svg", s)


if __name__ == "__main__":
    fig_classes()
    fig_clock()
    fig_welldefined()
    fig_twoscomp()
    print("§3.4.3m figures done.")
