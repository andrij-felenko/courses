# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для вставки 1.10.5c — «ESD-симулятор і рівні IEC 61000-4-2».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-10-5c-*).
НЕ чіпає головний figs.py розділу (тут його ще немає).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; sans-serif; стрілки через marker.
Нумерація підписів у тексті: Рис. 1.10.5c.k.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
PURPLE = "#7a3ea8"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange", GREY: "aGrey"}


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


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _cap(cx, cy, label="", vertical=True, gap=10, plate=22):
    """Конденсатор. vertical=True: дві горизонтальні пластини, вивід угору/вниз."""
    out = ""
    if vertical:
        out += line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, INK, 3)
        out += line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, INK, 3)
    else:
        out += line(cx - gap / 2, cy - plate / 2, cx - gap / 2, cy + plate / 2, INK, 3)
        out += line(cx + gap / 2, cy - plate / 2, cx + gap / 2, cy + plate / 2, INK, 3)
    if label:
        out += text(cx + plate / 2 + 8, cy + 5, label, 13, INK, "start", "bold", "italic")
    return out


def _resistor_h(x, y, w=64, h=22, label=""):
    out = rect(x, y - h / 2, w, h, "#fff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 7, label, 13, INK, "middle", "bold", "italic")
    return out


# ---------------------------------------------------------------------------
# Рис. 1.10.5c.1 — RC-мережа пістолета (150 пФ / 330 Ом) + форма струму контактного
#                  розряду 4 кВ із контрольними точками 15 А / 0.8 нс / 8 А / 4 А.
# ---------------------------------------------------------------------------
def fig1():
    W, H = 760, 410
    s = header(W, H)
    s += text(W / 2, 30, "ESD-пістолет: RC-мережа й форма удару (контактний розряд, IEC 61000-4-2)",
              17, INK, "middle", "bold")

    # --- ліворуч: схема RC-мережі ---
    s += text(40, 64, "Що всередині наконечника", 14, INK, "start", "bold")

    hv_x = 70          # шина високовольтного джерела
    top_y = 95
    bot_y = 300
    cap_y = (top_y + bot_y) / 2

    # Високовольтне джерело заряду (ліворуч): прямокутник
    s += rect(40, cap_y - 26, 50, 52, "#fff", PURPLE, 2, 5)
    s += text(65, cap_y - 4, "HV", 13, PURPLE, "middle", "bold")
    s += text(65, cap_y + 14, "0…8 кВ", 10.5, PURPLE, "middle")
    # від джерела до верхньої шини
    s += line(90, cap_y, hv_x, cap_y, INK, 2)
    s += line(hv_x, top_y, hv_x, bot_y, INK, 2)

    # Конденсатор 150 пФ (вертикальний у стовпі)
    s += _cap(hv_x, cap_y, "150 пФ", vertical=True, gap=12, plate=30)
    s += text(hv_x - 20, cap_y - 22, "= тіло", 10.5, GREY, "end")

    # Нижня шина = повернення (земля пістолета)
    s += line(hv_x, bot_y, 250, bot_y, INK, 2)
    # символ землі
    gx = 250
    s += line(gx, bot_y - 14, gx, bot_y, INK, 2)
    s += line(gx - 16, bot_y, gx + 16, bot_y, INK, 2.5)
    s += line(gx - 10, bot_y + 6, gx + 10, bot_y + 6, INK, 2.5)
    s += line(gx - 5, bot_y + 12, gx + 5, bot_y + 12, INK, 2.5)
    s += text(gx, bot_y + 30, "повернення (земля)", 11, INK, "middle")

    # Верхня шина → резистор 330 Ом → наконечник
    s += line(hv_x, top_y, 150, top_y, INK, 2)
    s += _resistor_h(150, top_y, 70, 22, "330 Ом")
    s += text(150 + 35, top_y + 28, "= рука/шкіра", 10.5, GREY, "middle")
    s += line(220, top_y, 270, top_y, INK, 2)

    # Наконечник (tip) — гострий конус
    s += polygon([(270, top_y - 9), (270, top_y + 9), (300, top_y)], INK)
    s += text(285, top_y - 18, "наконечник", 11, INK, "middle", "bold")

    # DUT — плата, у яку б'є розряд
    s += rect(312, top_y - 30, 78, 60, "#eef6ff", BLUE, 2, 5)
    s += text(351, top_y - 2, "DUT", 13, BLUE, "middle", "bold")
    s += text(351, top_y + 16, "(пристрій)", 9.5, BLUE, "middle")
    s += arrow(300, top_y, 312, top_y, RED, 2.4)
    # іскра
    s += polyline([(301, top_y - 4), (305, top_y + 3), (308, top_y - 3), (311, top_y + 2)], RED, 2)

    # --- праворуч: осцилограма струму ---
    ox, oy = 430, 95          # лівий-верх осей
    ow, oh = 300, 210
    bx, by = ox, oy + oh      # початок осей (зліва-внизу)
    s += text(ox + ow / 2, 64, "Струм у наконечнику при 4 кВ", 14, INK, "middle", "bold")

    # осі
    s += arrow(bx, by, bx + ow + 6, by, INK, 2)         # час →
    s += arrow(bx, by, bx, oy - 6, INK, 2)              # струм ↑
    s += text(bx + ow + 4, by + 18, "час, нс", 12, INK, "middle")
    s += text(bx - 8, oy - 8, "I, А", 12, INK, "end")

    # горизонтальні рівні (15, 8, 4 А) — масштаб: 15 А → 150 px
    def yI(amp):
        return by - amp * (oh - 30) / 16.0

    for amp, lab, col in [(15, "15 А", RED), (8, "8 А", ORANGE), (4, "4 А", GREEN)]:
        yy = yI(amp)
        s += line(bx, yy, bx + ow, yy, FAINT, 1, "4 4")
        s += text(bx - 6, yy + 4, lab, 11, col, "end", "bold")

    # вісь часу: 0, 30, 60 нс — масштаб 60 нс → ow-20
    def xT(t):
        return bx + t * (ow - 20) / 70.0

    for t in (0, 30, 60):
        xx = xT(t)
        s += line(xx, by, xx, by + 5, INK, 1.5)
        s += text(xx, by + 20, str(t), 11, INK, "middle")

    # форма: швидкий фронт ~0.8 нс до 15 А, потім спад, точки 30 нс=8 А, 60 нс=4 А
    pts = []
    # фронт
    pts.append((xT(0), by))
    pts.append((xT(0.8), yI(15)))
    # перший пік і подвійногорбий спад (схематично) до 8 А на 30 нс і 4 А на 60 нс
    pts.append((xT(2.5), yI(11.5)))
    pts.append((xT(6), yI(13.5)))   # другий менший горб (індуктивність наконечника)
    pts.append((xT(12), yI(10.0)))
    pts.append((xT(30), yI(8)))
    pts.append((xT(45), yI(5.6)))
    pts.append((xT(60), yI(4)))
    pts.append((xT(70), yI(3.1)))
    s += polyline(pts, RED, 2.6)

    # позначити фронт 0.8 нс
    s += line(xT(0.8), yI(15), xT(0.8), yI(15) - 16, GREY, 1.2, "3 3")
    s += text(xT(0.8) + 4, yI(15) - 18, "фронт 0.8 нс", 10.5, GREY, "start")

    # маркери контрольних точок
    for t, amp, col in [(30, 8, ORANGE), (60, 4, GREEN)]:
        s += circle(xT(t), yI(amp), 4, col, col, 1)
    s += circle(xT(0.8), yI(15), 4, RED, RED, 1)
    s += text(xT(0.8) + 6, yI(15) + 14, "пік 15 А", 10.5, RED, "start", "bold")

    s += text(ox + ow / 2, oy + oh + 44,
              "Заряд 150 пФ → крізь 330 Ом б'є в DUT: фронт <1 нс, пік ∝ напрузі",
              11.5, GREY, "middle")
    save("fig-10-5c-1-network-waveform.svg", s)


# ---------------------------------------------------------------------------
# Рис. 1.10.5c.2 — два методи (контактний vs повітряний) + драбина рівнів 1–4.
# ---------------------------------------------------------------------------
def fig2():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Два методи розряду й чотири рівні жорсткості",
              17, INK, "middle", "bold")

    # --- ліворуч-угорі: контактний розряд ---
    s += text(40, 66, "Контактний (contact): наконечник торкається металу",
              13.5, INK, "start", "bold")
    cy = 120
    # наконечник притиснутий до точки
    s += polygon([(60, cy - 9), (60, cy + 9), (96, cy)], INK)
    s += line(40, cy, 60, cy, INK, 2)
    s += text(50, cy - 16, "tip", 10.5, INK, "middle")
    # метал DUT
    s += rect(96, cy - 22, 120, 44, "#eef6ff", BLUE, 2, 4)
    s += text(156, cy + 5, "метал / роз'єм", 12, BLUE, "middle")
    s += circle(98, cy, 3.5, INK, INK, 1)  # точка контакту
    s += text(250, cy - 4, "розряд вмикає", 11.5, INK, "start")
    s += text(250, cy + 12, "реле в пістолеті", 11.5, INK, "start")
    s += text(250, cy + 30, "→ повторюваний фронт", 11, GREEN, "start", "bold")

    # --- ліворуч-нижче: повітряний розряд ---
    s += text(40, cy + 78, "Повітряний (air): наконечник підносять до пластику",
              13.5, INK, "start", "bold")
    ay = cy + 132
    s += circle(72, ay, 9, "#fff", INK, 2)  # круглий наконечник для air
    s += line(40, ay, 63, ay, INK, 2)
    s += text(52, ay - 16, "tip", 10.5, INK, "middle")
    # іскра через проміжок
    s += polyline([(81, ay), (90, ay - 6), (98, ay + 6), (107, ay - 5), (116, ay)], RED, 2.2)
    s += rect(120, ay - 22, 96, 44, "#f3f0f8", PURPLE, 2, 4)
    s += text(168, ay + 5, "корпус", 12, PURPLE, "middle")
    s += text(250, ay - 4, "іскра сама пробиває", 11.5, INK, "start")
    s += text(250, ay + 12, "повітря — фронт", 11.5, INK, "start")
    s += text(250, ay + 30, "«плаває», гірша повторність", 11, RED, "start")

    # --- праворуч: драбина рівнів ---
    lx = 470
    s += text(lx + 130, 66, "Рівні жорсткості", 14, INK, "middle", "bold")
    rows = [
        ("Рів.", "контакт", "повітря", "середовище", INK, False),
        ("1", "2 кВ", "2 кВ", "контрольоване, антистат.", GREEN, True),
        ("2", "4 кВ", "4 кВ", "офіс, житло", GREEN, True),
        ("3", "6 кВ", "8 кВ", "цех, помірна синтетика", ORANGE, True),
        ("4", "8 кВ", "15 кВ", "суворе: сухо, синтетика", RED, True),
    ]
    cols = [lx, lx + 56, lx + 132, lx + 196]
    cw = [56, 76, 64, 116]
    ry = 92
    rh = 56
    for i, (a, b, c, d, col, box) in enumerate(rows):
        yy = ry + i * rh
        if box:
            s += rect(lx - 6, yy - rh + 14, 270, rh, "#fff", FAINT, 1, 4)
            # кольорова смужка рівня
            s += rect(lx - 6, yy - rh + 14, 6, rh, col, col, 0, 0)
        wt = "bold" if i == 0 else "normal"
        sz = 13 if i == 0 else 14
        s += text(cols[0] + 22, yy, a, sz, col if i else INK, "middle", "bold")
        s += text(cols[1] + 30, yy, b, sz, INK, "middle", wt)
        s += text(cols[2] + 24, yy, c, sz, INK, "middle", wt)
        s += text(cols[3] + 4, yy, d, 11.5, INK, "start", wt)

    s += text(lx + 130, ry + len(rows) * rh + 6,
              "Вищий рівень = більший пік струму, не лише вольти",
              11, GREY, "middle")

    # стрілка «жорсткіше вниз»
    s += arrow(lx - 22, ry + 8, lx - 22, ry + 3.4 * rh, GREY, 2)
    s += text(lx - 30, ry + 1.8 * rh, "жорсткіше", 11, GREY, "middle", "bold")
    # повернути текст вертикально
    s = s.replace(
        f'<text x="{lx - 30:.1f}" y="{ry + 1.8 * rh:.1f}" font-family="{FONT}" font-size="11" '
        f'fill="{GREY}" text-anchor="middle" font-weight="bold" font-style="normal">жорсткіше</text>',
        f'<text x="{lx - 30:.1f}" y="{ry + 1.8 * rh:.1f}" font-family="{FONT}" font-size="11" '
        f'fill="{GREY}" text-anchor="middle" font-weight="bold" font-style="normal" '
        f'transform="rotate(-90 {lx - 30:.1f} {ry + 1.8 * rh:.1f})">жорсткіше</text>'
    )

    save("fig-10-5c-2-methods-levels.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done.")
