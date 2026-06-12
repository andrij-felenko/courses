# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки §3.1.6.c — «74HC14: шість інверторів Шмітта».
Чистий Python, без залежностей. Вивід → ./img/ (той самий каталог фігур розділу).

Стиль (AUTHORING §9) збігається з figs.py розділу: білий фон; HIGH/'1'/+ червоний,
LOW/'0'/− синій; «чисте/спрацювало» зелене; стрілки через marker; шрифт sans-serif.
Допоміжні функції скопійовано з figs.py розділу, щоб вигляд був єдиний, але головний
figs.py НЕ чіпається (вставка має власні унікальні фігури).

Нумерація підписів — як в історіях/вставках до теми: «Рис. 3.1.6c.k».
Імена SVG на диску — самодостатні (з префіксом s6-c), щоб не плутати з фігурами теми.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (як у figs.py розділу) ───────────────────────────────────────────
RED    = "#c0271e"   # HIGH / '1' / +
BLUE   = "#1f47b5"   # LOW / '0' / −
GREEN  = "#1f8a3b"   # чисте / спрацювало
INK    = "#1b1b1b"   # основний текст/лінії
GREY   = "#8a8a8a"   # допоміжне
FAINT  = "#e4e4e4"   # бліде тло
AMBER  = "#caa24a"   # шум / спотворення
COPPER = "#b5742e"   # мідь
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


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


def polygon(points, fill="none", stroke=INK, w=2):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── будівельні блоки схем ────────────────────────────────────────────────────
def inverter(x, y, scale=1.0, color=INK, hyst=True, label=None):
    """Інвертор-буфер трикутником вістрям праворуч, вхід ліворуч у (x,y).
    hyst=True — рисуємо всередині гліф петлі гістерезису (символ Шмітта)."""
    L = 46 * scale          # довжина трикутника
    H = 34 * scale          # висота біля основи
    tip_x = x + L
    out = polygon([(x, y - H / 2), (x, y + H / 2), (tip_x, y)], "#ffffff", color, 2.2)
    # бульбашка інверсії на вістрі
    br = 5.0 * scale
    out += circle(tip_x + br, y, br, "#ffffff", color, 2.2)
    if hyst:
        # гліф петлі гістерезису всередині трикутника
        g = 7.0 * scale
        cx = x + L * 0.40
        out += polyline([(cx - g, y + g * 0.55), (cx - g * 0.1, y + g * 0.55),
                         (cx - g * 0.1, y - g * 0.55)], color, 1.6)
        out += polyline([(cx + g, y - g * 0.55), (cx + g * 0.1, y - g * 0.55),
                         (cx + g * 0.1, y + g * 0.55)], color, 1.6)
    if label:
        out += text((x + tip_x) / 2, y - H / 2 - 6 * scale, label, 12 * scale,
                    color, "middle", "bold")
    return out, tip_x + 2 * br


# ── Рис. 3.1.6c.1 — анатомія: шість інверторів усередині + розпіновка DIP-14 ──
def fig_anatomy():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 34, "74HC14 зсередини: шість незалежних інверторів Шмітта в одному корпусі",
              19, INK, "middle", "bold")
    s += text(W / 2, 55, "ліворуч — логіка (що робить чип); праворуч — реальний корпус DIP-14 і призначення ніжок",
              12.5, GREY, "middle", style="italic")

    # ── ліва панель: 6 інверторів стовпчиком ─────────────────────────────────
    bx, by = 60, 92
    bw, bh = 360, 348
    s += rect(bx, by, bw, bh, "#fcfcfc", FAINT, 1.5, 8)
    s += text(bx + bw / 2, by + 22, "Логічна схема (6 × інвертор Шмітта)", 13.5, INK, "middle", "bold")
    rows = 6
    top = by + 48
    step = (bh - 70) / rows
    for i in range(rows):
        yy = top + step * i + step / 2
        ix = bx + 96
        # вхідна лінія + мітка nA
        s += line(bx + 30, yy, ix, yy, INK, 2)
        s += text(bx + 26, yy + 4, f"{i+1}A", 12.5, BLUE, "end", "bold")
        body, ox = inverter(ix, yy, 0.92, INK, True)
        s += body
        # вихідна лінія + мітка nY
        s += line(ox, yy, bx + bw - 30, yy, INK, 2)
        s += text(bx + bw - 26, yy + 4, f"{i+1}Y", 12.5, RED, "start", "bold")
    s += text(bx + bw / 2, by + bh - 8, "кожен канал самостійний: Y = NOT(A), з гістерезисом на вході",
              11, GREY, "middle", style="italic")

    # ── права панель: корпус DIP-14 з пінами ─────────────────────────────────
    px, py = 520, 96
    pw, ph = 150, 326
    s += rect(px, py, pw, ph, "#f2f2f2", INK, 2, 6)
    # півколо-ключ зверху (виїмка корпусу)
    s += f'<path d="M {px+pw/2-16:.1f},{py:.1f} a 16,16 0 0,0 32,0" fill="#ffffff" stroke="{INK}" stroke-width="2"/>\n'
    s += text(px + pw / 2, py + ph / 2 - 6, "74HC14", 16, INK, "middle", "bold")
    s += text(px + pw / 2, py + ph / 2 + 14, "DIP-14", 12, GREY, "middle")

    pins_left = ["1A", "1Y", "2A", "2Y", "3A", "3Y", "GND"]      # 1..7 згори вниз
    pins_right = ["VCC", "6A", "6Y", "5A", "5Y", "4A", "4Y"]      # 14..8 згори вниз
    n = 7
    pstep = (ph - 36) / (n - 1)
    pin_top = py + 18
    leg = 26

    def pin_color(name):
        if name == "VCC":
            return RED
        if name == "GND":
            return BLUE
        if name.endswith("A"):
            return BLUE
        return RED

    for i in range(n):
        yy = pin_top + pstep * i
        num = i + 1
        nm = pins_left[i]
        col = pin_color(nm)
        s += rect(px - leg, yy - 5, leg, 10, "#dcdcdc", GREY, 1.2)   # ніжка
        s += text(px - leg - 6, yy + 4, f"{num}", 11, GREY, "end")
        s += text(px - leg - 26, yy + 4, nm, 12.5, col, "end", "bold")
    for i in range(n):
        yy = pin_top + pstep * i
        num = 14 - i
        nm = pins_right[i]
        col = pin_color(nm)
        s += rect(px + pw, yy - 5, leg, 10, "#dcdcdc", GREY, 1.2)
        s += text(px + pw + leg + 6, yy + 4, f"{num}", 11, GREY, "start")
        s += text(px + pw + leg + 26, yy + 4, nm, 12.5, col, "start", "bold")

    # легенда живлення (під обома панелями, по центру)
    ly = by + bh + 22
    s += rect(bx + 24, ly, 12, 12, "none", RED, 2)
    s += text(bx + 42, ly + 11, "VCC — пін 14 (живлення, 2…6 В)", 12.5, INK, "start")
    s += rect(bx + 24, ly + 22, 12, 12, "none", BLUE, 2)
    s += text(bx + 42, ly + 33, "GND — пін 7 (спільна земля)", 12.5, INK, "start")
    s += text(px - 16, ly + 11, "Y = NOT(A) на кожному з шести каналів,", 12.5, GREY, "start", style="italic")
    s += text(px - 16, ly + 33, "вхід завжди з гістерезисом (петля в символі)", 12.5, GREY, "start", style="italic")
    return W, H, s


# ── Рис. 3.1.6c.2 — «перший байт»: RC-генератор на одному інверторі ──────────
def fig_oscillator():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "«Перший байт»: один інвертор 74HC14 + R + C = генератор прямокутних імпульсів",
              18, INK, "middle", "bold")
    s += text(W / 2, 55, "конденсатор заряджається через R, поки не проб'є VT+ — вихід перекидається — і C розряджається до VT−",
              12.5, GREY, "middle", style="italic")

    # ── схема ліворуч ────────────────────────────────────────────────────────
    # інвертор
    invx, invy = 250, 200
    body, ox = inverter(invx, invy, 1.15, INK, True)
    s += body
    s += text((invx + ox) / 2, invy - 34, "1/6 × 74HC14", 12.5, INK, "middle", "bold")

    # вихід інвертора йде праворуч і вниз до R
    outx = ox + 10
    s += line(ox, invy, outx, invy, INK, 2.4)
    s += text(outx + 6, invy - 8, "вихід", 12, RED, "start", "bold")
    # петля зворотного зв'язку: вихід → R → вузол входу
    node_x = invx - 70          # вузол перед входом
    s += line(outx, invy, outx, invy + 70, INK, 2.4)       # вниз
    s += line(outx, invy + 70, node_x, invy + 70, INK, 2.4)  # ліворуч під схемою
    # резистор R на горизонталі (зиґзаґ)
    rx0 = node_x + 60
    rx1 = node_x + 150
    zig = [(rx0, invy + 70)]
    seg = (rx1 - rx0) / 6
    for k in range(1, 6):
        zig.append((rx0 + seg * k, invy + 70 + (10 if k % 2 else -10)))
    zig.append((rx1, invy + 70))
    s += polyline(zig, INK, 2.4)
    s += text((rx0 + rx1) / 2, invy + 70 + 30, "R", 14, INK, "middle", "bold")
    # від резистора вгору до вузла входу
    s += line(node_x, invy + 70, node_x, invy, INK, 2.4)
    s += line(node_x, invy, invx, invy, INK, 2.4)
    s += circle(node_x, invy, 3.2, INK, INK, 1)            # вузол
    s += text(node_x - 6, invy - 10, "Vc", 13, GREEN, "end", "bold")
    # конденсатор від вузла на землю
    s += line(node_x, invy, node_x, invy + 26, INK, 2.4)
    s += line(node_x - 14, invy + 26, node_x + 14, invy + 26, INK, 3)   # обкладка
    s += line(node_x - 14, invy + 33, node_x + 14, invy + 33, INK, 3)   # обкладка
    s += text(node_x + 20, invy + 33, "C", 14, INK, "start", "bold")
    # земля
    gy = invy + 50
    s += line(node_x, invy + 33, node_x, gy, INK, 2.4)
    for k, ww in enumerate((18, 12, 6)):
        s += line(node_x - ww, gy + k * 5, node_x + ww, gy + k * 5, INK, 2.4)

    # ── часова діаграма праворуч ─────────────────────────────────────────────
    gx, gy0 = 560, 110
    gw, gh = 300, 240
    s += rect(gx, gy0, gw, gh, "#fcfcfc", FAINT, 1.5, 6)
    s += text(gx + gw / 2, gy0 - 6, "що на конденсаторі (Vc) і на виході", 12.5, INK, "middle", "bold")
    midy = gy0 + gh * 0.46
    # рівні порогів
    vt_plus = gy0 + gh * 0.28
    vt_minus = gy0 + gh * 0.64
    s += line(gx, vt_plus, gx + gw, vt_plus, RED, 1.4, "5,4")
    s += text(gx + gw - 4, vt_plus - 4, "VT+", 11.5, RED, "end", "bold")
    s += line(gx, vt_minus, gx + gw, vt_minus, BLUE, 1.4, "5,4")
    s += text(gx + gw - 4, vt_minus + 13, "VT−", 11.5, BLUE, "end", "bold")
    # пилкоподібна Vc (заряд/розряд експонентами, спрощено ламаною)
    saw = []
    x = gx + 6
    rising = True
    yv = vt_minus
    saw.append((x, yv))
    seg_w = (gw - 12) / 6
    for _ in range(6):
        x += seg_w
        yv = vt_plus if rising else vt_minus
        saw.append((x, yv))
        rising = not rising
    s += polyline(saw, GREEN, 2.4)
    s += text(gx + 8, midy + 56, "Vc — пилка між порогами", 11, GREEN, "start", style="italic")
    # вихідний меандр унизу
    oy = gy0 + gh - 18
    amp = 22
    sq = []
    x = gx + 6
    hi = True   # інвертор: поки Vc росте до VT+, вихід ВИСОКИЙ; на піку перекидається в НИЗЬКИЙ
    sq.append((x, oy - (amp if hi else 0)))
    for _ in range(6):
        sq.append((x, oy - (amp if hi else 0)))
        hi = not hi
        sq.append((x, oy - (amp if hi else 0)))
        x += seg_w
    sq.append((x, oy - (amp if hi else 0)))
    s += polyline(sq, RED, 2.2)
    s += text(gx + 8, oy + 14, "вихід — чистий меандр", 11, RED, "start", style="italic")

    s += text(W / 2, H - 14,
              "період задає добуток R×C: більший — повільніше блимає. Жодного кварцу, жодного коду — лише два пасивні елементи.",
              12, INK, "middle", style="italic")
    return W, H, s


# ── Рис. 3.1.6c.3 — типове застосування: чистимо дребезг кнопки ──────────────
def fig_debounce():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Типове застосування: 74HC14 «вичищає» брудний фронт у логічно чистий",
              18, INK, "middle", "bold")
    s += text(W / 2, 55, "RC згладжує стрибки, а гістерезис інвертора відрізає рештки дребезгу — на виході один чіткий перепад",
              12.5, GREY, "middle", style="italic")

    # три блоки: кнопка+RC → 74HC14 → чистий сигнал
    # блок 1: брудний вхід
    b1x = 70
    s += text(b1x + 70, 95, "кнопка + RC", 13, INK, "middle", "bold")
    # брудний фронт
    dirty = [(b1x, 180), (b1x + 30, 180)]
    import random
    random.seed(7)
    xx = b1x + 30
    for _ in range(8):
        xx += 7
        dirty.append((xx, 180 - random.choice([0, 40, 8, 46, 4, 44])))
    dirty.append((b1x + 140, 132))
    s += polyline(dirty, AMBER, 2.4)
    s += text(b1x + 70, 215, "брудний, з дребезгом", 11, AMBER, "middle", style="italic")
    s += text(b1x + 70, 232, "і млявим фронтом", 11, AMBER, "middle", style="italic")

    # стрілка
    s += arrow(b1x + 150, 156, b1x + 215, 156, GREY, 2.2)

    # блок 2: інвертор Шмітта
    invx, invy = b1x + 230, 156
    body, ox = inverter(invx, invy, 1.25, INK, True)
    s += body
    s += text((invx + ox) / 2, invy - 36, "1/6 × 74HC14", 12.5, INK, "middle", "bold")
    s += text((invx + ox) / 2, invy + 46, "два пороги VT+/VT−", 11, GREEN, "middle", style="italic")

    # стрілка
    s += arrow(ox + 12, invy, ox + 80, invy, GREY, 2.2)

    # блок 3: чистий вихід (інвертований → один чіткий перепад)
    cx = ox + 95
    clean = [(cx, 134), (cx + 70, 134), (cx + 70, 188), (cx + 150, 188)]
    s += polyline(clean, GREEN, 2.6)
    s += text(cx + 75, 215, "один чистий перепад", 11.5, GREEN, "middle", "bold")
    s += text(cx + 75, 232, "(і логічно інвертований)", 11, GREY, "middle", style="italic")

    s += text(W / 2, H - 16,
              "Той самий прийом — для будь-якого млявого чи зашумленого джерела: давач із плавним виходом, довга лінія, оптичний переривач.",
              12, INK, "middle", style="italic")
    return W, H, s


if __name__ == "__main__":
    for name, fn in [
        ("fig-14-6c-1-anatomy.svg", fig_anatomy),
        ("fig-14-6c-2-oscillator.svg", fig_oscillator),
        ("fig-14-6c-3-debounce.svg", fig_debounce),
    ]:
        W, H, body = fn()
        save(name, body)
    print("done")
