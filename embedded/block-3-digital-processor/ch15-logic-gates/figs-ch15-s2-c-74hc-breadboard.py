# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки «74HC00/08/32 на макетці» (до теми 3.2.2,
Розділ 15, Модуль 3). Чистий Python, без залежностей. Вивід → ./img/.
УНІКАЛЬНІ імена файлів (префікс fig-15-2-2c-), головний figs.py розділу не чіпаємо.
Стиль (AUTHORING §9): білий фон; '1'/high червоний, '0'/low синій; поле/дійсне
зелене; стрілки через marker; шрифт sans-serif. Нумерація — Рис. 3.2.2c.k.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (та сама, що в figs.py розділу) ──────────────────────────────────
RED   = "#c0271e"   # '1' / high / +5 В
BLUE  = "#1f47b5"   # '0' / low / GND
GREEN = "#1f8a3b"   # дійсне / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
SILVER = "#cfcfcf"
CHIPBG = "#2b2b2b"   # корпус мікросхеми (чорна пластмаса)
BOARD = "#f3efe2"    # поле макетки
COPPER = "#cf8b5e"
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


# ── маленькі гліфи вентилів (відмітні форми) ─────────────────────────────────
def gate_and(x, y, w=26, h=22, fill="#ffffff", stroke=INK, sw=1.6):
    r = h / 2
    bx = x + w - r
    return (f'<path d="M {x},{y-r} L {bx},{y-r} A {r},{r} 0 0 1 {bx},{y+r} '
            f'L {x},{y+r} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_or(x, y, w=30, h=22, fill="#ffffff", stroke=INK, sw=1.6):
    r = h / 2
    return (f'<path d="M {x},{y-r} Q {x+w*0.55},{y-r} {x+w},{y} '
            f'Q {x+w*0.55},{y+r} {x},{y+r} Q {x+w*0.28},{y} {x},{y-r} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_nand(x, y, w=26, h=22, fill="#ffffff", stroke=INK, sw=1.6):
    out = gate_and(x, y, w, h, fill, stroke, sw)
    out += circle(x + w + 3, y, 3, "#fff", stroke, sw)
    return out


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 3.2.2c.1 — родинна розпіновка DIP-14: 74HC00 / 74HC08 / 74HC32
# Три однокорпусні чипи: чотири вентилі, спільне розташування ніжок, VCC/GND.
# ═════════════════════════════════════════════════════════════════════════════
def fig_pinout():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 28, "Один корпус DIP-14, три мікросхеми: чотири вентилі, спільна розпіновка живлення",
              16, INK, "middle", "bold")

    # порядок входів/виходів у пакеті '00/'08/'32 (quad 2-input) однаковий:
    # піни:  1=1A 2=1B 3=1Y | 4=2A 5=2B 6=2Y | 7=GND |
    #        8=3Y 9=3A 10=3B | 11=4Y 12=4A 13=4B | 14=VCC
    chips = [
        ("74HC00", "4 × NAND", "Y = A·B (з кружком)", gate_nand, 70),
        ("74HC08", "4 × AND",  "Y = A·B",             gate_and, 360),
        ("74HC32", "4 × OR",   "Y = A+B",             gate_or,  650),
    ]
    cw, ch = 210, 300
    top = 70
    for name, sub, expr, glyph, x0 in chips:
        cx = x0 + cw / 2
        # підпис чипа
        s += text(cx, top - 22, name, 17, INK, "middle", "bold")
        s += text(cx, top - 5, sub + "  ·  " + expr, 12.5, GREY, "middle")
        # корпус
        bx, by = x0 + 38, top
        bw, bh = cw - 76, ch
        s += rect(bx, by, bw, bh, CHIPBG, INK, 2, rx=6)
        # ключ-виїмка зверху (показує орієнтацію / пін 1)
        s += (f'<path d="M {bx+bw/2-13},{by} A 13,13 0 0 0 {bx+bw/2+13},{by}" '
              f'fill="#1b1b1b" stroke="{GREY}" stroke-width="1.4"/>\n')
        s += text(bx + bw / 2, by + 16, "виїмка-ключ", 9.5, SILVER, "middle")

        # 14 ніжок: 7 ліворуч (1..7 зверху вниз), 7 праворуч (14..8 зверху вниз)
        npins = 7
        pin_dy = bh / npins
        leg = 22
        left_labels = ["1A", "1B", "1Y", "2A", "2B", "2Y", "GND"]
        right_labels = ["VCC", "4B", "4A", "4Y", "3B", "3A", "3Y"]
        left_nums = [1, 2, 3, 4, 5, 6, 7]
        right_nums = [14, 13, 12, 11, 10, 9, 8]
        for i in range(npins):
            py = by + pin_dy * (i + 0.5)
            # ліва ніжка
            s += line(bx - leg, py, bx, py, SILVER, 5)
            lab = left_labels[i]
            col = INK
            if lab == "GND":
                col = BLUE
            s += text(bx - leg - 5, py + 4, f"{left_nums[i]}", 10, GREY, "end")
            s += text(bx + 6, py + 4, lab, 11.5, col if col != INK else "#ffffff", "start",
                      "bold" if lab in ("GND",) else "normal")
            # права ніжка
            s += line(bx + bw, py, bx + bw + leg, py, SILVER, 5)
            rlab = right_labels[i]
            rcol = INK
            if rlab == "VCC":
                rcol = RED
            s += text(bx + bw + leg + 5, py + 4, f"{right_nums[i]}", 10, GREY, "start")
            s += text(bx + bw - 6, py + 4, rlab, 11.5,
                      rcol if rcol != INK else "#ffffff", "end",
                      "bold" if rlab in ("VCC",) else "normal")

        # маленький символ одного з чотирьох вентилів у центрі корпусу
        s += glyph(bx + bw / 2 - 15, by + bh / 2 - 4)
        # позначити пін1 крапкою
        s += circle(bx + 11, by + pin_dy * 0.5, 3.0, SILVER, INK, 1.2)

    # легенда живлення
    ly = top + ch + 36
    s += rect(70, ly, W - 140, 56, "#fbfbf6", FAINT, 1.4, rx=8)
    s += circle(96, ly + 19, 6, RED, INK, 1.2)
    s += text(110, ly + 23, "пін 14 = VCC → +5 В (живлення)", 13.5, INK)
    s += circle(96, ly + 41, 6, BLUE, INK, 1.2)
    s += text(110, ly + 45, "пін 7 = GND → земля (0 В)", 13.5, INK)
    s += text(470, ly + 23, "Усередині — ЧОТИРИ незалежні вентилі (1..4); входи A,B → вихід Y.", 13, INK)
    s += text(470, ly + 45, "Розташування ніжок у '00 / '08 / '32 ОДНАКОВЕ — різниться лише логіка.",
              13, GREEN, "start", "bold")
    save("fig-15-2-2c-1-pinout.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 3.2.2c.2 — підключення на макетці: живлення з шин, блокувальний кондер,
# один із чотирьох вентилів заведено (A,B з кнопок/перемичок) → світлодіод.
# ═════════════════════════════════════════════════════════════════════════════
def fig_wiring():
    W, H = 940, 520
    s = header(W, H)
    s += text(W / 2, 26, "74HC08 на макетці: живлення, блокувальний конденсатор, один вентиль у ділі",
              16, INK, "middle", "bold")

    # ── шини живлення (зверху + , знизу − ) ──────────────────────────────────
    bx0, bx1 = 60, W - 60
    yplus = 64
    yminus = H - 70
    # верхня шина +5
    s += line(bx0, yplus, bx1, yplus, RED, 4)
    s += line(bx0, yplus + 10, bx1, yplus + 10, RED, 1.5, dash="3,5")
    s += text(bx0 - 6, yplus + 4, "+", 22, RED, "end", "bold")
    s += text(bx1 + 8, yplus + 4, "+5 В", 13, RED, "start", "bold")
    # нижня шина GND
    s += line(bx0, yminus, bx1, yminus, BLUE, 4)
    s += line(bx0, yminus - 10, bx1, yminus - 10, BLUE, 1.5, dash="3,5")
    s += text(bx0 - 6, yminus + 6, "−", 22, BLUE, "end", "bold")
    s += text(bx1 + 8, yminus + 6, "GND", 13, BLUE, "start", "bold")

    # центральна канавка
    midy = (yplus + yminus) / 2
    s += line(bx0 + 20, midy, bx1 - 20, midy, FAINT, 10)
    s += text(bx1 - 24, midy - 6, "канавка", 10, GREY, "end")

    # ── корпус DIP верхи на канавці ──────────────────────────────────────────
    cw, chh = 150, 150
    cx0 = 300
    cy0 = midy - chh / 2
    s += rect(cx0, cy0, cw, chh, CHIPBG, INK, 2, rx=6)
    s += (f'<path d="M {cx0+cw/2-12},{cy0} A 12,12 0 0 0 {cx0+cw/2+12},{cy0}" '
          f'fill="#1b1b1b" stroke="{GREY}" stroke-width="1.4"/>\n')
    s += text(cx0 + cw / 2, cy0 + chh / 2 - 6, "74HC08", 15, "#ffffff", "middle", "bold")
    s += text(cx0 + cw / 2, cy0 + chh / 2 + 12, "(вентиль 1)", 11, SILVER, "middle")

    # ніжки: ліворуч 1..7 (зверху вниз), праворуч 14..8
    npins = 7
    pin_dy = chh / npins
    leg = 18
    lx = cx0
    rx = cx0 + cw
    left_pin_y = [cy0 + pin_dy * (i + 0.5) for i in range(npins)]
    right_pin_y = left_pin_y
    for i in range(npins):
        s += line(lx - leg, left_pin_y[i], lx, left_pin_y[i], SILVER, 4)
        s += line(rx, right_pin_y[i], rx + leg, right_pin_y[i], SILVER, 4)
    # індекси потрібних пінів
    P1A, P1B, P1Y = left_pin_y[0], left_pin_y[1], left_pin_y[2]   # піни 1,2,3
    PGND = left_pin_y[6]                                          # пін 7
    PVCC = right_pin_y[0]                                         # пін 14 (праворуч зверху)
    s += text(lx - leg - 2, P1A - 6, "1 (1A)", 9.5, GREY, "end")
    s += text(lx - leg - 2, P1B - 6, "2 (1B)", 9.5, GREY, "end")
    s += text(lx - leg - 2, P1Y - 6, "3 (1Y)", 9.5, GREY, "end")
    s += text(lx - leg - 2, PGND - 6, "7 (GND)", 9.5, BLUE, "end")
    s += text(rx + leg + 2, PVCC - 6, "14 (VCC)", 9.5, RED, "start")

    # ── живлення чипа: VCC↑ до +, GND↓ до − ──────────────────────────────────
    s += polyline([(rx + leg, PVCC), (rx + leg + 30, PVCC), (rx + leg + 30, yplus + 22), (rx + leg + 30, yplus)],
                  RED, 3)
    s += arrow(rx + leg + 30, yplus + 16, rx + leg + 30, yplus + 2, RED, 3)
    s += polyline([(lx - leg, PGND), (lx - leg - 28, PGND), (lx - leg - 28, yminus)], BLUE, 3)
    s += arrow(lx - leg - 28, yminus - 14, lx - leg - 28, yminus - 2, BLUE, 3)

    # ── блокувальний конденсатор 100 нФ між пінами 14 і 7, поряд із чипом ─────
    capx = rx + leg + 64
    capy_top = PVCC
    capy_bot = PGND
    s += line(rx + leg, PVCC, capx, PVCC, RED, 2)
    s += line(rx + leg, PGND, capx, PGND, BLUE, 2)
    # сам конденсатор (дві пластини)
    cmid = (capy_top + capy_bot) / 2
    s += line(capx, PVCC, capx, cmid - 7, RED, 2)
    s += line(capx, PGND, capx, cmid + 7, BLUE, 2)
    s += line(capx - 12, cmid - 7, capx + 12, cmid - 7, INK, 2.6)
    s += line(capx - 12, cmid + 7, capx + 12, cmid + 7, INK, 2.6)
    s += text(capx + 18, cmid - 2, "100 нФ", 11.5, INK, "start", "bold")
    s += text(capx + 18, cmid + 14, "блокувальний", 10, GREEN)
    s += text(capx + 18, cmid + 27, "(поряд із чипом!)", 10, GREEN)

    # ── входи A, B з кнопок/перемичок (тут: A=1, B=1 → AND=1) ─────────────────
    # вхід 1A ← перемичка з +5 (логічна 1)
    ax = lx - leg - 70
    s += polyline([(lx - leg, P1A), (ax, P1A), (ax, yplus)], RED, 2.6)
    s += arrow(ax, yplus + 14, ax, yplus + 2, RED, 2.6)
    s += circle(ax, P1A, 3.5, RED, INK, 1.2)
    s += text(ax - 6, P1A - 8, "A = 1", 12, RED, "end", "bold")
    # вхід 1B ← перемичка з +5 (логічна 1) — інша точка шини
    bxp = lx - leg - 110
    s += polyline([(lx - leg, P1B), (bxp, P1B), (bxp, yplus)], RED, 2.6)
    s += arrow(bxp, yplus + 14, bxp, yplus + 2, RED, 2.6)
    s += circle(bxp, P1B, 3.5, RED, INK, 1.2)
    s += text(bxp - 6, P1B + 16, "B = 1", 12, RED, "end", "bold")

    # ── вихід 1Y → струмообмежувальний резистор → світлодіод → GND ───────────
    oy = P1Y
    ox = rx  # but 1Y is on the LEFT (pin 3). Вивід ліворуч:
    # 1Y ліворуч (пін 3) — ведемо праворуч під чипом до світлодіода
    s += line(lx - leg, oy, lx - leg - 18, oy, GREEN, 2.6)
    s += polyline([(lx - leg - 18, oy), (lx - leg - 18, midy + 64), (cx0 + cw + 150, midy + 64)], GREEN, 2.6)
    # резистор
    rxs = cx0 + cw + 150
    ry = midy + 64
    s += rect(rxs, ry - 7, 34, 14, "#fff", INK, 1.6)
    s += text(rxs + 17, ry - 12, "330 Ω", 10.5, INK, "middle")
    s += line(rxs + 34, ry, rxs + 60, ry, GREEN, 2.6)
    # світлодіод (трикутник + риска)
    ledx = rxs + 60
    s += (f'<path d="M {ledx},{ry-9} L {ledx},{ry+9} L {ledx+16},{ry} Z" '
          f'fill="{AMBER}" stroke="{INK}" stroke-width="1.6"/>\n')
    s += line(ledx + 16, ry - 9, ledx + 16, ry + 9, INK, 2.4)
    s += text(ledx + 8, ry - 16, "LED", 11, INK, "middle", "bold")
    # далі до GND
    s += polyline([(ledx + 16, ry), (ledx + 40, ry), (ledx + 40, yminus)], BLUE, 2.6)
    s += arrow(ledx + 40, yminus - 14, ledx + 40, yminus - 2, BLUE, 2.6)
    s += text(rxs + 6, ry + 26, "вихід 1Y = A·B = 1 → світлодіод горить", 12, GREEN, "start", "bold")

    # підпис «перший байт»
    s += text(60, H - 18, "«Перший байт» цифрової схеми: подав +5 на обидва входи AND — і вихід засвітив LED.",
              12.5, GREY, "start", "italic")
    save("fig-15-2-2c-2-wiring.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 3.2.2c.3 — головні граблі CMOS: НЕ лишай вхід «у повітрі».
# Ліворуч: плаваючий вхід → невизначений рівень, шум, нагрів.
# Праворуч: невживаний вхід підтягнуто до шини → чисто.
# ═════════════════════════════════════════════════════════════════════════════
def fig_floating():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 26, "Невикористаний вхід CMOS не можна лишати «в повітрі»",
              16, INK, "middle", "bold")

    # дві панелі
    def panel(x0, ok):
        out = ""
        pw, ph = 400, 320
        py = 56
        bg = "#fbf3f3" if not ok else "#f1f8f2"
        edge = RED if not ok else GREEN
        out += rect(x0, py, pw, ph, bg, edge, 2, rx=10)
        title = "ПОГАНО: вхід плаває" if not ok else "ДОБРЕ: вхід підтягнуто"
        out += text(x0 + pw / 2, py + 26, title, 15, edge, "middle", "bold")

        # вентиль AND посередині панелі
        gx = x0 + 150
        gy = py + 150
        gw, gh = 70, 56
        r = gh / 2
        bxg = gx + gw - r
        out += (f'<path d="M {gx},{gy-r} L {bxg},{gy-r} A {r},{r} 0 0 1 {bxg},{gy+r} '
                f'L {gx},{gy+r} Z" fill="#ffffff" stroke="{INK}" stroke-width="2"/>\n')
        out += text(gx + 26, gy + 5, "&", 20, INK, "middle", "bold")
        # вхід A — використовується (сигнал)
        ya = gy - 14
        out += line(gx - 80, ya, gx, ya, INK, 2.4)
        out += text(gx - 84, ya + 4, "A", 13, INK, "end", "bold")
        out += text(gx - 80, ya - 8, "сигнал", 10, GREY, "start")
        # вихід
        out += line(gx + gw, gy, gx + gw + 70, gy, INK, 2.4)
        out += text(gx + gw + 74, gy + 4, "Y", 13, INK, "start", "bold")

        # вхід B — другий
        yb = gy + 14
        out += line(gx - 80, yb, gx, yb, INK, 2.4)
        out += text(gx - 84, yb + 4, "B", 13, INK, "end", "bold")

        if not ok:
            # плаваючий: обрив, знак питання, «?»
            out += line(gx - 80, yb, gx - 120, yb, INK, 2.4)
            out += circle(gx - 120, yb, 3.5, "#fff", RED, 2)
            out += text(gx - 126, yb + 4, "✂", 14, RED, "end")
            out += text(gx - 96, yb - 12, "не підключено", 10.5, RED, "middle")
            # хмарка шуму над входом
            out += polyline([(gx - 70, yb + 22), (gx - 62, yb + 14), (gx - 54, yb + 24),
                             (gx - 46, yb + 14), (gx - 38, yb + 24)], GREY, 1.8)
            out += text(gx - 54, yb + 40, "наводки, шум", 10, GREY, "middle")
            # вихід невизначений
            out += text(gx + gw + 74, gy + 22, "= ?", 13, RED, "start", "bold")
            out += text(gx + gw / 2, py + ph - 58, "рівень B «гуляє» 0↔1", 11.5, RED, "middle")
            out += text(gx + gw / 2, py + ph - 40, "вихід смикається, чип", 11.5, RED, "middle")
            out += text(gx + gw / 2, py + ph - 24, "гріється (наскрізний струм)", 11.5, RED, "middle")
        else:
            # підтягнуто до +5 (для AND невживаний вхід → у '1')
            out += polyline([(gx - 80, yb), (gx - 120, yb), (gx - 120, py + 60)], RED, 2.4)
            out += arrow(gx - 120, py + 74, gx - 120, py + 62, RED, 2.4)
            out += text(gx - 124, py + 56, "+5 В", 11.5, RED, "end", "bold")
            out += circle(gx - 120, yb, 3.5, RED, INK, 1.4)
            out += text(gx - 96, yb + 28, "B = 1 (тривко)", 11, GREEN, "middle", "bold")
            out += text(gx + gw + 74, gy + 22, "= A", 13, GREEN, "start", "bold")
            out += text(gx + gw / 2, py + ph - 58, "невживаний вхід AND →", 11.5, GREEN, "middle")
            out += text(gx + gw / 2, py + ph - 40, "до +5 (для OR → до GND);", 11.5, GREEN, "middle")
            out += text(gx + gw / 2, py + ph - 24, "вихід чистий і стабільний", 11.5, GREEN, "middle")
        return out

    s += panel(50, ok=False)
    s += panel(490, ok=True)

    # нижня примітка-правило
    s += text(W / 2, H - 14,
              "Правило CMOS: КОЖЕН вхід — на 0 або 1. Невживані входи й цілі вентилі — жорстко до VCC чи GND.",
              12.5, INK, "middle", "bold")
    save("fig-15-2-2c-3-floating.svg", s)


if __name__ == "__main__":
    fig_pinout()
    fig_wiring()
    fig_floating()
    print("done.")
