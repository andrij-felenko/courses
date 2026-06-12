# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.7.2c — «Клейова логіка сьогодні: GreenPAK-клас».
Окремий генератор (головний figs.py розділу не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-r07-s2c-1-glue.svg     — роль «клейової логіки»: дрібний CMIC у проміжку між великими чипами
  fig-r07-s2c-2-matrix.svg   — нутро CMIC: матриця з'єднань + LUT/тригери/лічильники/компаратор/ЦАП, NVM
  fig-r07-s2c-3-config.svg   — «перша конфігурація»: GUI → I²C-запис у NVM → знеструмлення → чип сам працює
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
VIOL  = "#7a3ea8"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey",
         VIOL: "aViol", AMBER: "aAmber"}


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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def chip(x, y, w, h, title, sub="", fill="#fbfbfb", stroke=INK, pins=0, pin_side="lr"):
    """Корпус-чип із ключем-виїмкою, підписом і (опційно) рядами ніжок."""
    out = rect(x, y, w, h, fill, stroke, 2, 8)
    out += circle(x + 12, y + 12, 5, "#fff", stroke, 1.4)          # ключ
    out += text(x + w/2, y + h/2 - 2, title, 14, stroke, "middle", "bold")
    if sub:
        out += text(x + w/2, y + h/2 + 16, sub, 10, GREY, "middle")
    if pins:
        pitch = h / (pins + 1)
        for i in range(pins):
            yy = y + pitch * (i + 1)
            if "l" in pin_side:
                out += line(x - 9, yy, x, yy, INK, 2)
            if "r" in pin_side:
                out += line(x + w, yy, x + w + 9, yy, INK, 2)
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Фігура 1: роль «клейової логіки» — дрібний CMIC у проміжку між великими чипами ──
def fig1_glue():
    W, H = 800, 470
    b = header(W, H)
    b += text(W/2, 30, "Клейова логіка: дрібний конфігурований чип у проміжку між великими",
              17, INK, "middle", "bold")

    # три великі «острови» на платі: МК, давач, драйвер мотора
    mcu = (60, 150, 150, 150)
    sens = (590, 90, 150, 95)
    drv = (590, 270, 150, 95)
    b += chip(*mcu, "МК", "(зайнятий, ніжок мало)", "#eef7ee", GREEN)
    b += chip(*sens, "Давач", "віддає імпульси", "#f3f3ff", BLUE)
    b += chip(*drv, "Драйвер", "хоче ENABLE+скид", "#fff3f3", RED)

    # дрібний CMIC посередині — «клей»
    gx, gy, gw, gh = 350, 175, 110, 110
    b += rect(gx, gy, gw, gh, "#fffdf2", AMBER, 2.4, 10)
    b += circle(gx + 11, gy + 11, 4.5, "#fff", AMBER, 1.4)
    b += text(gx + gw/2, gy + 40, "CMIC", 14, AMBER, "middle", "bold")
    b += text(gx + gw/2, gy + 58, "GreenPAK-", 10, INK, "middle")
    b += text(gx + gw/2, gy + 72, "клас", 10, INK, "middle")
    b += text(gx + gw/2, gy + 96, "дрібнота-«клей»", 9, GREY, "middle")
    b += text(gx + gw/2, gy - 10, "1 крихітний корпус замість жмені деталей", 11, AMBER, "middle", style="italic")

    # дроти: МК → CMIC (мало ліній), CMIC → давач/драйвер
    b += arrow(mcu[0] + mcu[2], 200, gx, 200, GREEN, 2)
    b += text((mcu[0] + mcu[2] + gx)/2, 190, "1 пін", 10, GREEN, "middle")
    b += arrow(gx + gw, 205, sens[0], 150, BLUE, 2)
    b += arrow(gx + gw, 250, drv[0], 305, RED, 2)
    b += text(gx + gw + 30, 168, "лічить/ділить", 9, BLUE, "start")
    b += text(gx + gw + 30, 292, "генерує ENABLE,", 9, RED, "start")
    b += text(gx + gw + 30, 306, "скид, затримку", 9, RED, "start")

    # що ховається ВСЕРЕДИНІ клею — підпис унизу
    b += text(W/2, 360, "Усередині — той самий матеріал розділу: кілька LUT (§3.7.3), тригерів (§3.3),",
              12, GREY, "middle")
    b += text(W/2, 378, "лічильник-затримка, компаратор. Дрібні «склейки» між чипами, яких бракувало.",
              12, GREY, "middle")

    b += text(W/2, 418, "Роль із §3.7.2 — та сама, що колись у PAL/GAL: підігнати один чип до іншого.",
              13, GREEN, "middle", "bold")
    b += text(W/2, 442, "Лише тепер «клей» крихітний, дешевий і вміє ще й аналог.",
              12, GREEN, "middle", style="italic")
    save("fig-r07-s2c-1-glue.svg", b)


# ── Фігура 2: нутро CMIC — матриця з'єднань + блоки + NVM ─────────────────────
def fig2_matrix():
    W, H = 820, 540
    b = header(W, H)
    b += text(W/2, 30, "Нутро CMIC: блоки + матриця з'єднань, налаштована з NVM",
              17, INK, "middle", "bold")

    # корпус
    cx, cy, cw, ch = 60, 60, 700, 400
    b += rect(cx, cy, cw, ch, "#fcfcff", INK, 2, 12)
    b += circle(cx + 16, cy + 16, 6, "#fff", INK, 1.6)
    b += text(cx + cw - 12, cy + 22, "один корпус (SOIC/QFN/STQFN)", 11, GREY, "end", style="italic")

    # ── ліворуч: банк ресурсних блоків ──
    bx = cx + 28
    blocks = [
        ("LUT × кілька", "будь-яка булева\nфункція (§3.7.3)", VIOL),
        ("D-тригери", "пам'ять стану\n(§3.3)", BLUE),
        ("Лічильники/\nзатримки", "ділення такту,\nтаймери", GREEN),
        ("Компаратор", "аналог → поріг\n(§3.1.6)", RED),
        ("ЦАП / опорна", "вузли аналогу", AMBER),
        ("Осцилятор", "власний такт", INK),
    ]
    bw, bh = 150, 50
    by0 = cy + 50
    gap = 10
    yb = []
    for i, (nm, role, col) in enumerate(blocks):
        y = by0 + i * (bh + gap)
        yb.append(y + bh/2)
        b += rect(bx, y, bw, bh, "#fff", col, 2, 7)
        # назва (може бути у два рядки)
        lines = nm.split("\n")
        ty = y + 18 if len(lines) > 1 else y + 22
        for ln in lines:
            b += text(bx + bw/2, ty, ln, 11, col, "middle", "bold")
            ty += 13
        # роль дрібним під назвою
        rl = role.split("\n")
        ry = y + bh - 14 if len(rl) > 1 else y + bh - 8
        for ln in rl:
            b += text(bx + bw/2, ry, ln, 8.5, GREY, "middle")
            ry += 10

    # ── центр: матриця з'єднань (connection fabric) ──
    mx, my, mw, mh = bx + bw + 70, cy + 60, 180, 360
    b += rect(mx, my, mw, mh, "#f0fff2", GREEN, 2, 8)
    b += text(mx + mw/2, my - 24, "матриця з'єднань", 12, GREEN, "middle", "bold")
    b += text(mx + mw/2, my - 10, "(будь-що з будь-чим, за бажанням)", 9.5, GREEN, "middle", style="italic")
    # сітка точок-перемикачів
    cols = 5
    rows = 7
    for c in range(cols):
        xx = mx + 20 + c * (mw - 40) / (cols - 1)
        b += line(xx, my + 14, xx, my + mh - 14, FAINT, 1)
    for r in range(rows):
        yy = my + 22 + r * (mh - 44) / (rows - 1)
        b += line(mx + 14, yy, mx + mw - 14, yy, FAINT, 1)
    # кілька «замкнених» вузлів (запрограмовані з'єднання)
    nodes = [(1, 0), (3, 1), (0, 2), (4, 3), (2, 4), (1, 5), (3, 6)]
    for c, r in nodes:
        xx = mx + 20 + c * (mw - 40) / (cols - 1)
        yy = my + 22 + r * (mh - 44) / (rows - 1)
        b += circle(xx, yy, 4.2, GREEN, GREEN, 1)

    # стрілки від блоків у матрицю
    for y in yb:
        b += arrow(bx + bw, y, mx, my + 30 + (y - (cy + 50)) * 0.85, GREY, 1.4)

    # ── праворуч: GPIO-піни ──
    px = mx + mw + 70
    pins = ["GPIO0", "GPIO1", "GPIO2", "GPIO3", "GPIO4", "GPIO5"]
    pbh = 30
    py0 = cy + 70
    for i, nm in enumerate(pins):
        y = py0 + i * (pbh + 16)
        b += rect(px, y, 80, pbh, "#fbfbfb", INK, 1.6, 5)
        b += text(px + 40, y + 20, nm, 11, INK, "middle", "bold")
        b += line(px + 80, y + pbh/2, cx + cw, y + pbh/2, INK, 2)
        b += circle(cx + cw, y + pbh/2, 3, INK, INK, 1)
        # від матриці до піна
        b += arrow(mx + mw, my + 40 + i * 52, px, y + pbh/2, GREY, 1.3)
    b += text(px + 40, py0 - 14, "ніжки", 11, GREY, "middle")
    b += text(px + 40, cy + ch - 18, "кожен пін — вхід АБО вихід,", 9, GREY, "middle")
    b += text(px + 40, cy + ch - 6, "як налаштуєш", 9, GREY, "middle")

    # ── NVM знизу: вона тримає всю конфігурацію ──
    b += rect(bx, cy + ch + 24, cw - 56, 40, "#fff7ec", AMBER, 2.2, 8)
    b += text(cx + cw/2 - 28, cy + ch + 49, "NVM (енергонезалежна пам'ять): зберігає ВСЮ таблицю з'єднань і налаштування блоків",
              12, AMBER, "middle", "bold")
    b += arrow(mx + mw/2, my + mh, mx + mw/2, cy + ch + 22, AMBER, 2, "5,4")

    save("fig-r07-s2c-2-matrix.svg", b)


# ── Фігура 3: «перша конфігурація» — GUI → I²C у NVM → знеструмлення → чип сам працює ──
def fig3_config():
    W, H = 820, 430
    b = header(W, H)
    b += text(W/2, 30, "«Перша конфігурація»: не код для МК, а схема, що друкується в чип",
              16, INK, "middle", "bold")

    steps = [
        ("1. Малюємо схему",
         ["у редакторі (GUI)", "тягнемо дроти між", "блоками — без HDL"], VIOL),
        ("2. Записуємо в чип",
         ["I²C-запис конфігу", "в NVM (програматор", "або просто МК)"], BLUE),
        ("3. Знеструмлюємо",
         ["конфіг лишається", "в NVM — не зника", "після вимкнення"], AMBER),
        ("4. Чип сам працює",
         ["вмикається вже", "налаштованим, МК", "більше не потрібен"], GREEN),
    ]
    n = len(steps)
    bw, bh = 165, 150
    gap = (W - n * bw) / (n + 1)
    y = 80
    centers = []
    for i, (title, lines, col) in enumerate(steps):
        x = gap + i * (bw + gap)
        centers.append((x + bw, y + bh/2, x, col))
        b += rect(x, y, bw, bh, "#ffffff", col, 2.4, 10)
        b += rect(x, y, bw, 30, col, col, 0, 10)
        b += text(x + bw/2, y + 20, title, 12, "#ffffff", "middle", "bold")
        ty = y + 56
        for ln in lines:
            b += text(x + bw/2, ty, ln, 11, INK, "middle")
            ty += 19
        # маленька іконка-натяк усередині кожного кроку
        if i == 0:
            b += rect(x + 30, y + 108, 30, 22, "#fff", VIOL, 1.6, 3)
            b += rect(x + 105, y + 108, 30, 22, "#fff", VIOL, 1.6, 3)
            b += line(x + 60, y + 119, x + 105, y + 119, VIOL, 1.8)
        elif i == 1:
            b += text(x + bw/2, y + 126, "SDA · SCL →", 11, BLUE, "middle", "bold")
        elif i == 2:
            b += text(x + bw/2, y + 126, "⏻  →  NVM тримає", 11, AMBER, "middle", "bold")
        else:
            b += text(x + bw/2, y + 126, "✓ працює само", 11, GREEN, "middle", "bold")

    # стрілки між кроками
    for i in range(n - 1):
        x_end = centers[i][0]
        x_next = centers[i + 1][2]
        b += arrow(x_end + 4, y + bh/2, x_next - 4, y + bh/2, GREY, 2.2)

    # нижній контраст: МК vs CMIC
    cy = 270
    b += line(60, cy, W - 60, cy, FAINT, 1)
    b += text(W/2, cy + 24, "Чим це відрізняється від звички програмувати МК", 13, INK, "middle", "bold")

    b += rect(70, cy + 38, 330, 70, "#f4f7ff", BLUE, 1.8, 8)
    b += text(235, cy + 60, "МК: щоразу при старті", 12, BLUE, "middle", "bold")
    b += text(235, cy + 80, "ВИКОНУЄ програму інструкція за", 11, INK, "middle")
    b += text(235, cy + 96, "інструкцією — потрібні такт і живлення.", 11, INK, "middle")

    b += rect(W - 400, cy + 38, 330, 70, "#eef7ee", GREEN, 1.8, 8)
    b += text(W - 235, cy + 60, "CMIC: схема просто Є в залізі", 12, GREEN, "middle", "bold")
    b += text(W - 235, cy + 80, "одразу після подачі живлення —", 11, INK, "middle")
    b += text(W - 235, cy + 96, "ніякої програми не «біжить» (§3.7.5).", 11, INK, "middle")

    b += text(W/2, cy + 132, "Тому «перший байт» тут — це «перша конфігурація»: один раз залив схему — і забув.",
              12, GREEN, "middle", "bold")
    save("fig-r07-s2c-3-config.svg", b)


if __name__ == "__main__":
    fig1_glue()
    fig2_matrix()
    fig3_config()
    print("r07-s2-c-greenpak figures done.")
